"""Derive SkyySkills/build_skyyskills_0.4.19.py from the LIVE generated SkyySkills/build_skyyskills_0.4.18.py (= the tools/deploy_set.py SET
pin, deployed 2026-10-06 with the 8-way dodge roll; 0.4.18 came from 0.4.17 by tools/skills_0_4_18_patch.py, ... 0.4.6 from Skyy's EDITED
0.4.5 - commit ab75b6c; never re-run skills_0_4_5 or older patches). Same style as skills_0_4_18_patch.py: rep(old, new) with asserted single
anchors, newline-agnostic; 0.4.18 stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_19_patch.py   then   python SkyySkills/build_skyyskills_0.4.19.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.19.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/skills0419/, deleted afterwards)

0.4.19 = THE ROLL MOVE GATE + NO MOVE XP CAP. Skyy LOCKED 2026-10-06 (docs/answered/skills.md, after the Dodge Roll deploy): "add the move
gate like jumps but remove the xp cap on both."
(1) ROLL MOVE GATE: a roll pays acro.dodgeXp only after the player moved acro.dodgeMinMove blocks (NEW row, default 2.0 = acro.jumpMinMove's
    default) since the last PAID roll - the JUMP_MOVE shape (an own counter, reset when a roll pays). One difference, on purpose: the roll's
    OWN slide does not count. A roll is ApplyForce 13 "Set" (VelocityConfig ground resistance 0.94 -> 0.82 below 5 b/s), about 4-5 blocks,
    more than the 2.0 gate - counted, rolling in place would pay every roll. So movement while a roll effect is on and Acro.ROLL_SETTLE_MS
    (700 ms) after it is not counted, and at every new roll the last 2 ticks are taken back (the client starts the slide a tick before the
    server sees the effect). The 400 ms cooldown stays (a roll inside it is not counted at all); the Acrobatics push still comes on every
    counted roll, paid or not (the gate is about XP only); Creative pays nothing as before.
(2) NO MOVE XP CAP: acro.maxXpPerMinute keeps its row, 0 = no cap (was: 0 = no movement XP at all) and 0 is the new default; Acro.take pays
    everything while it is 0 (the ring still records, so a cap set later counts the last minute). Running, jumps, rolls and the Double Jump
    XP all went through this one cap, so all of them are uncapped now (Skyy named jumps and dodges; running pays at most ~84 a minute at
    full sprint, under the old 240, so it changes nothing for running). The FALL caps (acro.fallXpMax / acro.fallMaxXpPerMinute) stay.
(3) ONE-TIME MIGRATION AcroMig (PROJECT-RULES section 4) of an existing xp.properties, setup() after KillXpMig, before SkillCfg.load:
    acro.maxXpPerMinute=240 (still the old default, a one-line entry) -> 0 (change-log line, Undo = 240); a hand-set value is kept (INFO
    line; a hand-set 0 gets a WARN that 0 now means no cap); acro.dodgeMinMove=2.0 inserted under acro.dodgeCooldownMs (change-log line
    0 -> 2.0, Undo = 0 = no gate, the 0.4.18 behaviour) unless the file has it; the exact default comment lines of the dodge and the cap
    rewritten; marker = the new comment line holding "SkyySkills 0.4.19 roll move gate" (run once). Properties check (nothing else
    changes), config-history copy first (HealMig.mgKit + CfgHist.snapshot + mgSaved), the kit's atomicWrite (ISO-8859-1 bytes, line endings
    kept). A file with no acro.* key is left to AcroCfg.ensureDefaults (it appends the whole 0.4.19 section).
(4) JUMP GATE FIX (review): the jump gate (s[10], acro.jumpMinMove) now counts the same own movement as the roll gate - a roll's slide
    no longer fills it, and the same 2 ticks are taken back at a new roll. In 0.4.18 roll-in-place + jump paid ~2 XP a cycle, bounded only
    by the 240 cap; with no cap it would farm without limit. Jumps differ from 0.4.18 only where a roll slide fed the jump gate.
NOT in this build: the jump cooldown / jumpMinMove values, the fall caps, the dodge cooldown, the roll assets - all unchanged.
"""
import difflib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.18.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.19.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.18"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.18"' in s and "derived from the generated 0.4.17 by tools/skills_0_4_18_patch.py" in s, "not the live generated 0.4.18"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "DODGE_FILES" in s and '"acro.roll"' in s, "the dodge roll (0.4.18) is missing"
for _x in ("acro.dodgeMinMove", "DODGE_MOVE", "AcroMig", "ROLL_SETTLE_MS"):
    assert _x not in s, "0.4.18 already has " + _x
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
OLDS = []


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    i = s.index(old)
    j = s.find(LF, i + len(old))
    OLDS.append(s[s.rfind(LF, 0, i) + 1:(j if j >= 0 else len(s))])
    s = s.replace(old, new)


def after(anchor, add):
    rep(anchor, anchor + add)


def before(anchor, add):
    rep(anchor, add + anchor)


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1 and s.index(a) < s.index(b), (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# blocks that must stay byte-identical (0.4.18 code this build does not touch)
KEEP = [block("# >>> SPELL GEN", "# <<< SPELL GEN"),
        block("# ================= Xbow part 1 (0.4.5)", "# ================= ClassCurve (0.4.12)"),
        block("# ================= 0.4.2 FELLED TREES", "# FellCredit (spec 2.6)"),
        block("# ================= skill:fn:addxp (0.4)", "# ================= leaderboard ================="),
        block("# ================= OverallPage (0.4.6)", "# ================= 0.4.3 ADMIN CONFIG"),
        block("# ---- 0.4.5 Xbow part 2", "# ================= ManaRegen (0.4.12)"),
        block("# ================= CombatDmgSys (0.3)", "# ================= PlacedStore"),
        block("# ================= RollSys (0.4.14)", "# ================= CombatDmgSys (0.3)"),
        block("# ================= SkillStore: per-player XP", "# ================= SkillClass (0.3)"),
        block("# ---- HealMig (0.4.11 point 5)", "# ---- DocMig (0.4.14, fix (5))"),
        block("# ================= ClassMana part 1 (0.4.15", "# ================= SkillLv (0.4.16)"),
        block("# ================= OwnCurve (0.4.16)", "# ================= GatherPace.apply (0.4.14)"),
        block("# ---- SkillLvMig (0.4.16)", "# ---- ManaGuard (point 3)"),
        block("# ================= 0.4.18 DODGE ROLL", "# ---- 0.4.18 dodge roll conflict check")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.18 - build script (derived from the generated 0.4.17 by tools/skills_0_4_18_patch.py - edit the patch, not this file;
0.4.17 was derived''', '''"""SkyySkills 0.4.19 - build script (derived from the generated 0.4.18 by tools/skills_0_4_19_patch.py - edit the patch, not this file;
0.4.18 was derived from the generated 0.4.17 by tools/skills_0_4_18_patch.py; 0.4.17 was derived''')
HEAD_0419 = '''0.4.19: THE ROLL MOVE GATE + NO MOVE XP CAP (Skyy LOCKED 2026-10-06 "add the move gate like jumps but remove the xp cap on both"; full
  notes in tools/skills_0_4_19_patch.py). Keeps all of 0.4.18 (same pairing; 0.4.18 is a safe rollback - it reads acro.maxXpPerMinute=0 as
  "no movement XP", so set it back to 240 first). A roll pays only after moving acro.dodgeMinMove (2.0) blocks on your own since the last
  paid roll (the roll's own slide does not count); acro.maxXpPerMinute 0 = no cap, the new default (running, jumps, rolls). AcroMig: an
  untouched 240 -> 0, acro.dodgeMinMove added, once, History first, Undo lines.
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.19.py, -Xverify:all, scratch under tools/dev/scratch deleted afterwards).
'''
before('0.4.18: THE DODGE ROLL (research/Grapple-Bolt-Spec.md 1.2 / 2.5 / 3.2; Skyy LOCKED 2026-10-06 "Yes, 8-way roll"; full notes in\n', HEAD_0419)
rep('VERSION = "0.4.18"\n', 'VERSION = "0.4.19"\n')

# ---------------------------------------------------------------------------------------------------------------- (3) default file lines
DODGE_DOC_OLD = "# Dodge (the vanilla strafe left/right dodge): XP per dodge, at most one per acro.dodgeCooldownMs."
DODGE_DOC_NEW = "# Dodge rolls (the dodge key, 8 directions): XP per roll, at most one counted roll per acro.dodgeCooldownMs."
GATE_MARK_ID = "SkyySkills 0.4.19 roll move gate"
GATE_MARK = "# A roll pays only after acro.dodgeMinMove blocks of your own movement since the last paid roll (" + GATE_MARK_ID + ")."
CAP_DOC_0419 = ("# Running, jumping and dodging XP together pays at most this much in ANY 60 seconds (0 = no cap, the default since"
                " SkyySkills 0.4.19).")
assert all(len(x) <= 140 and all(ord(c) < 128 for c in x) and '"' not in x and "\\" not in x for x in (DODGE_DOC_NEW, GATE_MARK, CAP_DOC_0419))
rep('''ACRO_L.append("# Dodge (the vanilla strafe left/right dodge): XP per dodge, at most one per acro.dodgeCooldownMs.")
ACRO_L.append("acro.dodgeXp=3")
ACRO_L.append("acro.dodgeCooldownMs=400")
ACRO_L.append(ACRO_CAP_NEW)
ACRO_L.append("acro.maxXpPerMinute=240")
''', '''# 0.4.19 (Skyy LOCKED 2026-10-06): the roll move gate (acro.dodgeMinMove, GATE_MARK = AcroMig's run-once marker) and no move XP cap by default
# (0 = no cap); AcroMig brings an existing file here once (ACRO_DODGE_DOC_OLD / ACRO_CAP_NEW / ACRO_CAP_OLD -> the new comment lines)
ACRO_DODGE_DOC_OLD = %s
ACRO_DODGE_DOC_NEW = %s
ACRO_GATE_MARK_ID = %s
ACRO_GATE_MARK = %s
ACRO_CAP_0419 = %s
ACRO_L.append(ACRO_DODGE_DOC_NEW)
ACRO_L.append("acro.dodgeXp=3")
ACRO_L.append("acro.dodgeCooldownMs=400")
ACRO_L.append(ACRO_GATE_MARK)
ACRO_L.append("acro.dodgeMinMove=2.0")
ACRO_L.append(ACRO_CAP_0419)
ACRO_L.append("acro.maxXpPerMinute=0")
''' % (json.dumps(DODGE_DOC_OLD), json.dumps(DODGE_DOC_NEW), json.dumps(GATE_MARK_ID), json.dumps(GATE_MARK), json.dumps(CAP_DOC_0419)))

# ---------------------------------------------------------------------------------------------------------------- (1)+(2) AcroCfg
rep('''"double FALL_DMG_XP = 10.0", "double FALL_MAX = 2000.0", "double FALL_PER_MIN = 3000.0", "double DODGE_XP = 3.0", "long DODGE_CD = 400L",
              "double MAX_PER_MIN = 240.0", ''', '''"double FALL_DMG_XP = 10.0", "double FALL_MAX = 2000.0", "double FALL_PER_MIN = 3000.0", "double DODGE_XP = 3.0", "long DODGE_CD = 400L",
              "double DODGE_MOVE = 2.0", "double MAX_PER_MIN = 0.0", ''')
rep('''  MAX_PER_MIN = nn({PKG}.SkillCfg.dbl(p, "acro.maxXpPerMinute", 240.0));
''', '''  DODGE_MOVE = nn({PKG}.SkillCfg.dbl(p, "acro.dodgeMinMove", 2.0));   // 0.4.19: blocks moved on your own between paid rolls
  MAX_PER_MIN = nn({PKG}.SkillCfg.dbl(p, "acro.maxXpPerMinute", 0.0));   // 0.4.19: 0 = no cap (the default)
''')

# ---------------------------------------------------------------------------------------------------------------- (1)+(2) Acro
rep('''#  287 prev extraJumpsUsed, 288-291 spare. reset (world change) and profileReset also zero 281, 282, 284 and 285.
''', '''#  287 prev extraJumpsUsed, 288-291 spare. reset (world change) and profileReset also zero 281, 282, 284 and 285.
# 0.4.19 (roll move gate): double[296]: 291 blocks moved on your own since the last PAID roll (not while a roll slides), 292 the roll slide
#  window end ms (a roll effect on + ROLL_SETTLE_MS), 293 / 294 what the last two move() ticks added to 291 (taken back at a new roll: the
#  client starts the slide before the server sees the effect), 295 spare. Physical-player state like the jump edge: no reset clears it.
#  The jump gate s[10] counts the same own movement (a roll slide feeds neither gate) and takes back the same 2 ticks at a new roll.
''')
rep('''  double[] n = new double[292];
''', '''  double[] n = new double[296];   // 0.4.19: 292 -> 296 (the roll move gate)
''')
before('''acro.addField(CtField.make('public static final String SOURCE = "skills.acrobatics";', acro))
''', '''acro.addField(CtField.make("public static final long ROLL_SETTLE_MS = 700L;", acro))   # 0.4.19: the slide after a roll effect (not own movement)
''')
rep('''  if (!excluded) s[10] = s[10] + hd;
''', '''  double own = (!excluded && (double) now >= s[292]) ? hd : 0.0;   // 0.4.19: both move gates count your own movement only (no roll slide)
  s[10] = s[10] + own;
  s[291] = s[291] + own;
  s[294] = s[293];
  s[293] = own;
''')
rep('''  if (on && s[6] < 0.5 && !excluded && (double) now - s[20] >= (double) {PKG}.AcroCfg.DODGE_CD) {{
    s[20] = (double) now;
    if (!creative) s[11] = s[11] + {PKG}.AcroCfg.DODGE_XP;
    if ({PKG}.AcroCfg.DODGE_BOOST) s[23] = (double) (now + 100L);
  }}
''', '''  if (on && s[6] < 0.5) {{   // 0.4.19: a new roll - the last 2 ticks were already its slide
    s[291] = Math.max(0.0, s[291] - s[293] - s[294]);
    s[10] = Math.max(0.0, s[10] - s[293] - s[294]);   // the jump gate too (roll + jump in place cannot farm the uncapped jump XP)
    s[293] = 0.0;
    s[294] = 0.0;
  }}
  if (on) s[292] = (double) (now + ROLL_SETTLE_MS);
  if (on && s[6] < 0.5 && !excluded && (double) now - s[20] >= (double) {PKG}.AcroCfg.DODGE_CD) {{
    s[20] = (double) now;
    if (!creative && s[291] >= {PKG}.AcroCfg.DODGE_MOVE) {{   // 0.4.19: the move gate (acro.dodgeMinMove since the last PAID roll)
      s[11] = s[11] + {PKG}.AcroCfg.DODGE_XP;
      s[291] = 0.0;
    }}
    if ({PKG}.AcroCfg.DODGE_BOOST) s[23] = (double) (now + 100L);
  }}
''')
rep('''# whole XP that may be paid now under acro.maxXpPerMinute (0 = none); records what it allows
acro.addMethod(CtNewMethod.make(f"""
public static double take(double[] s, long now, double whole) {{
  long sec = now / 1000L;
  double room''', '''# whole XP that may be paid now under acro.maxXpPerMinute (0.4.19: 0 = no cap - was 0 = none); records what it allows
acro.addMethod(CtNewMethod.make(f"""
public static double take(double[] s, long now, double whole) {{
  long sec = now / 1000L;
  if ({PKG}.AcroCfg.MAX_PER_MIN <= 0.0) {{
    if (whole < 1.0) return 0.0;
    addPaid(s, sec, whole);
    return whole;
  }}
  double room''')

# ---------------------------------------------------------------------------------------------------------------- Server Setup rows
rep('''    ("acro.dodgeXp", "XP per dodge", "acrobatics", "dec", "3", "0", "100000", "", "", "live",
     "Dodge rolls the way you move (8 ways, standing still = back): every roll pays this.", "reload"),
    ("acro.dodgeCooldownMs", "Paid dodge cooldown", "acrobatics", "int", "400", "100", "600000", "", "ms", "live,adv", "", "reload"),
''', '''    ("acro.dodgeXp", "XP per dodge", "acrobatics", "dec", "3", "0", "100000", "", "", "live",
     "Dodge rolls the way you move (8 ways, standing still = back): a roll pays this after moving.", "reload"),
    ("acro.dodgeCooldownMs", "Paid dodge cooldown", "acrobatics", "int", "400", "100", "600000", "", "ms", "live,adv", "", "reload"),
    # 0.4.19 (Skyy LOCKED 2026-10-06): the roll move gate, like acro.jumpMinMove
    ("acro.dodgeMinMove", "Move between paid rolls", "acrobatics", "dec", "2.0", "0", "1000", "", "blocks", "live,adv",
     "Rolling in place pays nothing: move this far on your own between paid rolls. 0 = no gate.", "reload"),
''')
rep('''    ("acro.maxXpPerMinute", "Move XP per minute cap", "acrobatics", "dec", "240", "0", "1000000000", "", "", "live",
     "Running, jumping and dodging XP together in any 60 seconds.", "reload"),
''', '''    ("acro.maxXpPerMinute", "Move XP per minute cap", "acrobatics", "dec", "0", "0", "1000000000", "", "", "live",
     "Running, jumping and dodging XP together in any 60 seconds. 0 = no cap (the default).", "reload"),
''')
rep("""assert len(CFG_ROWS) == 202, (""", """assert len(CFG_ROWS) == 203, (""")
rep("""fromLevel; 0.4.18: + the read-only acro.roll, got %d" % len(CFG_ROWS))""",
    """fromLevel; 0.4.18: + the read-only acro.roll; 0.4.19: + acro.dodgeMinMove, got %d" % len(CFG_ROWS))""")
before('''assert sum(1 for _r in CFG_ROWS if _r[0] == "mana.classBase") == 1 and sum(1 for _r in CFG_ROWS if _r[0] == "spell.manaDivisor") == 1
''', '''# 0.4.19: the gate row right after the dodge cooldown, row default = file default; the cap row 0 = file default; the marker once in the file
_k19 = [_r[0] for _r in CFG_ROWS]
assert _k19[_k19.index("acro.dodgeCooldownMs") + 1] == "acro.dodgeMinMove" and _k19.count("acro.dodgeMinMove") == 1
assert _dp.get("acro.dodgeMinMove") == "2.0" == [_r for _r in CFG_ROWS if _r[0] == "acro.dodgeMinMove"][0][4]
assert _dp.get("acro.maxXpPerMinute") == "0" == [_r for _r in CFG_ROWS if _r[0] == "acro.maxXpPerMinute"][0][4]
assert DEFAULTS.count(ACRO_GATE_MARK_ID) == 1 and DEFAULTS.count(ACRO_GATE_MARK + "\\nacro.dodgeMinMove=2.0\\n") == 1
assert ACRO_DODGE_DOC_OLD not in DEFAULTS and ACRO_CAP_NEW not in DEFAULTS and ACRO_CAP_OLD not in DEFAULTS
''')

# ---------------------------------------------------------------------------------------------------------------- (3) AcroMig
rep('''kxm  = pool.makeClass(PKG + ".KillXpMig")
''', '''kxm  = pool.makeClass(PKG + ".KillXpMig")
# 0.4.19: the one-time config update for the roll move gate + no move XP cap (AcroMig)
amg  = pool.makeClass(PKG + ".AcroMig")
''')
AMIG = r'''
# ---- AcroMig (0.4.19, Skyy LOCKED 2026-10-06 "add the move gate like jumps but remove the xp cap on both"): ONCE on an EXISTING xp.properties,
# setup() after KillXpMig.run, BEFORE SkillCfg.load and CfgPub.start. Nothing to do = no file (load() writes the 0.4.19 default), no acro.* key
# (AcroCfg.ensureDefaults appends the whole 0.4.19 section), or a comment line holding MARK_ID (done before). Else, per logical line (the kit's
# own parser): acro.maxXpPerMinute whose LAST entry is a one-line entry holding exactly 240 (the old default) -> every such one-line entry 0
# (value text only; key, separator, CR kept) + a config-changes.log line (Undo = 240); any other value is kept (an INFO line; a hand-set 0
# gets a WARN: 0 now means no cap). The marker line + acro.dodgeMinMove=2.0 (only when the file lacks the key; a change-log line 0 -> 2.0,
# Undo = 0 = no gate) go right under the last acro.dodgeCooldownMs entry, or at the end in the file's own line ending. The exact default
# dodge / cap comment lines become the 0.4.19 ones. Properties check (only those two keys differ), config-history copy first, atomicWrite.
# A failure = WARN, file untouched, retried at the next start.
amg.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(ACRO_GATE_MARK_ID), amg))
amg.addField(CtField.make("public static final String MARK = %s;" % json.dumps(ACRO_GATE_MARK), amg))
amg.addField(CtField.make("public static final String[] DOC_OLD = %s;" % jarr([ACRO_DODGE_DOC_OLD, ACRO_CAP_NEW, ACRO_CAP_OLD]), amg))
amg.addField(CtField.make("public static final String[] DOC_NEW = %s;" % jarr([ACRO_DODGE_DOC_NEW, ACRO_CAP_0419, ACRO_CAP_0419]), amg))
amg.addField(CtField.make('public static final String CAP_KEY = "acro.maxXpPerMinute";', amg))
amg.addField(CtField.make('public static final String CAP_OLD = "240";', amg))
amg.addField(CtField.make('public static final String CAP_NEW = "0";', amg))
amg.addField(CtField.make('public static final String GATE_KEY = "acro.dodgeMinMove";', amg))
amg.addField(CtField.make('public static final String GATE_DEF = "2.0";', amg))
amg.addField(CtField.make('public static final String GATE_UNDO = "0";', amg))
amg.addField(CtField.make('public static final String AFTER_KEY = "acro.dodgeCooldownMs";', amg))
amg.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.19";', amg))
assert all('"' not in _x and "\\" not in _x for _x in (ACRO_DODGE_DOC_OLD, ACRO_CAP_NEW, ACRO_CAP_OLD, ACRO_DODGE_DOC_NEW, ACRO_CAP_0419))
assert ("\n" + ACRO_DEFAULTS).count("\nacro.maxXpPerMinute=0\n") == 1 and ACRO_GATE_MARK in ACRO_L
amg.addMethod(CtNewMethod.make(J14(r"""
public static int docIdx(String body) {
  for (int i = 0; i < DOC_OLD.length; i++) if (DOC_OLD[i].equals(body)) return i;
  return -1;
}"""), amg))
# pure text step (ISO-8859-1 chars in and out). null = nothing to do (the marker is in a comment line, no acro.* key, or the text cannot be read
# as Properties); else { new text, String[] { key, old, new }* (the change-log rows), Boolean cap updated, Boolean gate added, Integer comment
# lines updated, String kept note ("" = none), Boolean kept note is a WARN }. Never throws for any text.
amg.addMethod(CtNewMethod.make(J14(r"""
public static Object[] plan(String text) {
  if (text == null) return null;
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }
  boolean anyAcro = false;
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) if (((String) it.next()).startsWith("acro.")) anyAcro = true;
  if (!anyAcro) return null;
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  String capEff = null;
  boolean capMulti = false;
  int afterEnd = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    String key = @PKG@.CfgFile.key(s);
    if (CAP_KEY.equals(key)) { capEff = @PKG@.CfgFile.value(l, k).trim(); capMulti = e > k; }
    if (AFTER_KEY.equals(key)) afterEnd = e;
    k = e + 1;
  }
  boolean capMig = capEff != null && !capMulti && capEff.equals(CAP_OLD);
  boolean addGate = p.getProperty(GATE_KEY) == null;
  String kept = "";
  boolean warn = false;
  if (capEff != null && !capMig) {
    String v = p.getProperty(CAP_KEY);
    double dv = @PKG@.SkillCfg.dbl(p, CAP_KEY, 240.0);
    if (!(dv > 0.0)) {
      kept = CAP_KEY + "=" + @PKG@.CfgRows.oneLine(v) + " kept - NOTE: since SkyySkills 0.4.19 a cap of 0 means NO cap (before, it paid no running / jump / roll XP at all); set acro.enabled=false or the XP rows to 0 to stop movement XP";
      warn = true;
    } else {
      kept = CAP_KEY + "=" + @PKG@.CfgRows.oneLine(v) + " kept (an admin's value) - the 0.4.19 default is 0 = no cap";
    }
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  int docs = 0;
  boolean placed = false;
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) {
      int d = docIdx(s2);
      if (d >= 0) { out.add(DOC_NEW[d] + (raw[k].endsWith("\r") ? "\r" : "")); docs++; }
      else out.add(raw[k]);
      k++;
      continue;
    }
    int e2 = @PKG@.CfgFile.end(l, k);
    String key2 = @PKG@.CfgFile.key(s2);
    if (capMig && CAP_KEY.equals(key2) && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(CAP_OLD)) {
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + CAP_NEW + (raw[k].endsWith("\r") ? "\r" : ""));
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    if (e2 == afterEnd && e2 + 1 < raw.length) {
      String c1 = raw[e2].endsWith("\r") ? "\r" : cr;
      out.add(MARK + c1);
      if (addGate) out.add(GATE_KEY + "=" + GATE_DEF + c1);
      placed = true;
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + 512);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  String body = sb.toString();
  if (!placed) {
    String nl = cr + "\n";
    String b = MARK + nl + (addGate ? GATE_KEY + "=" + GATE_DEF + nl : "");
    String pre = (body.length() == 0 || body.endsWith("\n")) ? "" : nl;
    String last = body.endsWith("\n") ? body.substring(0, body.length() - 1) : body;
    if (last.endsWith("\r")) last = last.substring(0, last.length() - 1);
    int bs = 0;
    for (int i = last.length() - 1; i >= 0 && last.charAt(i) == '\\'; i--) bs++;
    if (bs % 2 == 1) pre = pre + nl;
    body = body + pre + b;
  }
  java.util.ArrayList rows = new java.util.ArrayList();
  if (capMig) { rows.add(CAP_KEY); rows.add(CAP_OLD); rows.add(CAP_NEW); }
  if (addGate) { rows.add(GATE_KEY); rows.add(GATE_UNDO); rows.add(GATE_DEF); }
  return new Object[] { body, (String[]) rows.toArray(new String[0]), Boolean.valueOf(capMig), Boolean.valueOf(addGate), Integer.valueOf(docs),
                        kept, Boolean.valueOf(warn) };
}"""), amg))
# only the planned keys differ: every old key keeps its value except acro.maxXpPerMinute (exactly 0 when updated), acro.dodgeMinMove is the one
# new key (exactly 2.0) when added
amg.addMethod(CtNewMethod.make(J14(r"""
public static boolean sameAfter(byte[] old, byte[] nb, boolean capMig, boolean addGate) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties n = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    n.load(new java.io.ByteArrayInputStream(nb));
    if (n.size() != a.size() + (addGate ? 1 : 0)) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String want = a.getProperty(k);
      if (capMig && CAP_KEY.equals(k)) want = CAP_NEW;
      String got = n.getProperty(k);
      if (got == null || !got.equals(want)) return false;
    }
    if (addGate && (a.getProperty(GATE_KEY) != null || !GATE_DEF.equals(n.getProperty(GATE_KEY)))) return false;
    return true;
  } catch (Throwable t) { return false; }
}"""), amg))
amg.addMethod(CtNewMethod.make(J14(r"""
public static String logLine(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}"""), amg))
amg.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    boolean capMig = ((Boolean) r[2]).booleanValue();
    boolean addGate = ((Boolean) r[3]).booleanValue();
    if (!sameAfter(old, data, capMig, addGate)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.19 (roll move gate / no move XP cap): the update would change another setting (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = @PKG@.HealMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.HealMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.19 roll move gate / move XP cap update");
    if (!@PKG@.HealMig.mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.19 (roll move gate / no move XP cap): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[1];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    StringBuilder what = new StringBuilder();
    if (capMig) what.append(CAP_KEY + " 240 -> 0 (no cap on running / jump / roll XP; Server Setup -> Changes -> Undo = 240)");
    if (addGate) { if (what.length() > 0) what.append("; "); what.append(GATE_KEY + "=" + GATE_DEF + " added (rolls pay only after moving; Undo = 0 = no gate)"); }
    if (what.length() == 0) what.append("no setting changed - 0.4.19 marker added");
    int docs = ((Integer) r[4]).intValue();
    String msg = "xp.properties updated for 0.4.19: " + what.toString() + (docs > 0 ? "; " + docs + " default comment line(s) updated" : "") + " - the old file is in config-history";
    @PKG@.SkillCfg.info(msg);
    String kept = (String) r[5];
    if (kept.length() > 0) {
      if (((Boolean) r[6]).booleanValue()) @PKG@.SkillCfg.warn(kept); else @PKG@.SkillCfg.info(kept);
      return msg + "\n" + kept;
    }
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update xp.properties for 0.4.19 (roll move gate / no move XP cap; the file is used as it is): " + t);
    return "";
  }
}"""), amg))

'''
before('''# ---- ManaGuard (point 3): WARN once per class whose base Mana is below the Mana cost of a weapon in its class kit.''', AMIG.lstrip("\n"))
rep('''  {PKG}.KillXpMig.run();      // 0.4.17: kill XP by level + Mana regen per class level lines into an existing xp.properties, once; History first
''', '''  {PKG}.KillXpMig.run();      // 0.4.17: kill XP by level + Mana regen per class level lines into an existing xp.properties, once; History first
  {PKG}.AcroMig.run();        // 0.4.19: untouched acro.maxXpPerMinute 240 -> 0 + acro.dodgeMinMove into an existing xp.properties, once; History first
''')
rep('''          kxm):   # 0.4.17: + KillXpMig;''', '''          kxm, amg):   # 0.4.19: + AcroMig; 0.4.17: + KillXpMig;''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands: 0.4.19 adds none"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
_ix = lambda t: s.index(t)
assert _ix('amg  = pool.makeClass(PKG + ".AcroMig")') < _ix("# ---- AcroMig (0.4.19") < _ix("{PKG}.AcroMig.run();") < _ix("kxm, amg):")
assert _ix("def J14(src_):") < _ix("# ---- AcroMig (0.4.19") and _ix("ACRO_GATE_MARK_ID = ") < _ix("ACRO_DEFAULTS = ")
assert _ix("{PKG}.KillXpMig.run();") < _ix("{PKG}.AcroMig.run();") < _ix("String rules = {PKG}.SkillCfg.load();")
assert s.count("s[291]") >= 6 and s.count("new double[296]") == 1 and "new double[292]" not in s
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.18 lines changed outside the planned places: %r" % _bad[:5]
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.18,", len(_gone), "0.4.18 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
