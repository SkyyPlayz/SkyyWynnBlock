"""Derive SkyySkills/build_skyyskills_0.4.23.py from the LIVE generated SkyySkills/build_skyyskills_0.4.22.py (= the tools/deploy_set.py SET
pin; 0.4.22 came from 0.4.21 by tools/skills_0_4_22_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_22_patch.py: rep(old, new) with asserted single anchors, newline-agnostic; 0.4.22
stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_23_patch.py   then   python SkyySkills/build_skyyskills_0.4.23.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.23.py --dir tools/dev/scratch/<task>/skills0423   (bare JVM, -Xverify:all; the folder is deleted)

0.4.23 = THE ROLL REWORK + LOG FIXES (Skyy LOCKED 2026-10-08, docs/answered/skills.md: "the tap sprint to dodge worked, but on and off (make
sure there is no delay timer. it should be spam able. and it only worked forward and side to side, not back. forward diagonals worked. (dont
worry about interfering with sprint, just make it roll the moment you hit sprint, and if you hold, you come out of the roll sprinting.)";
"dont rebind sprint, leave it"; the 07:12 LOG SCAN line of docs/log/2026-10.md). Deploy WITH SkyyArmory 0.1.13 (alone it is safe too: the
staff handover check only reads more).
(1) THE ROLL FIRES ON THE SPRINT PRESS: the rising edge of the sprinting state the server sees (MovementStates.sprinting, from the client's
    ClientMovement packets) starts the vanilla Dodge root chain at once - no tap window, no release. Holding the key: the server never
    touches sprint, so you leave the roll sprinting. NO OWN COOLDOWN: 0.4.20's fixed 0.4 s tap cooldown (TAP_CD_MS, no row) is gone, and
    the engine's own one is gone too - the vanilla Dodge ROOT has no Cooldown, so InteractionTypeUtils.getDefaultCooldown(Dodge) = 0.35 s
    applied (InteractionManager.isOnCooldown; a server-started chain on cooldown fails SILENTLY - one reason for the "on and off"). This
    jar now ships Server/Item/RootInteractions/Dodge.json = the vanilla root + "Cooldown": {"Cooldown": 0} (CooldownHandler.isOnCooldown
    returns false for 0). Stamina is the only limit (2 per roll, the vanilla StatsCondition; out of Stamina = the vanilla bar flash). A
    press while a roll is still on waits for it (at most PRESS_BUFFER_MS 350) so spamming gives back-to-back rolls, none lost.
    Guards kept from 0.4.20 (each one a real false-roll case): ground only, not crouching / sliding / rolling / in an excluded state; not
    within TAP_SETTLE_MS (now 150, was 300) after such a tick (sprint resuming on landing); the tick before the press must be MOVING (a
    sprint that resumes because you pressed W again while holding the sprint key is not a press); not with under 0.5 Stamina.
    acro.dodgeCooldownMs is NOT the roll's limit (verified: Acro.dodge only uses it to count XP + the tree push) - unchanged, no migration.
    acro.dodgeTapMs is no longer read for anything (row kept, help says so; no migration). Binds are never touched.
(2) BACK ROLLS (investigated, NOT added): the server's only movement input is ClientMovement (MovementStates booleans, wishMovement,
    velocity, positions) - there is no key bitfield, and no InteractionType for sprint. The vanilla MovementConfig has a
    ForwardSprintSpeedMultiplier only (no backward / strafe sprint) and the client reports sprinting=false while moving back, so pressing
    sprint while walking back changes NOTHING the server receives (same flags, same speed). No fake trigger is added; back rolls stay on
    the vanilla dodge key (unbound for Skyy) and standing-still = back via that key. SkyyKeyProbe 0.1 '/keyprobe moves on' can confirm in game.
(3) THE 24 'Missing interaction **SkyySkills_Roll_<dir>_Next_Interactions_N' WARNINGS: the engine builds a batch's client packet
    (HytaleAssetStore.handleRemoveOrUpdate -> InteractionPacketGenerator -> SerialInteraction.configurePacket ->
    Interaction.getInteractionIdOrUnknown) BEFORE it loads that batch's inline children (AssetStore.loadAssets0: handleRemoveOrUpdate at
    533 / 555, loadContainedAssets at 572), so every inline Serial step is "missing" for a moment (the engine then loads the real one over
    the placeholder - verified in a bare JVM: the store keeps our real steps, the rolls were never broken by it; vanilla has ~100 such lines
    too). Fix: no inline steps any more - each roll is named files only (the roll check, its Serial, its push; shared: the i-frames, the 2
    roll looks, the Adventure Stamina spend + its 2 steps) = 25 files, all in one batch, so every name resolves before the packet is built.
    The bodies are still generated from vanilla Dodge_Left at build time and re-inlined they equal 0.4.22's exactly (asserted).
(4) THE STAFF HANDOVER CREDIT ('8 of 8 ladder staffs do NOT come from SkyyArmory'): this jar's overrides of the vanilla Staff_Cast_Summon_Charged
    and Staff_Cast_Cost make the engine re-read every item whose inline InteractionVars inherit them (AssetStore.reloadChildrenContainerAssets
    -> collectChildrenInDifferentFile -> loadAssetsFromPaths(<the loading pack>, ...)); the vanilla staff files' inline children stay linked
    to those parents after SkyyArmory's items replace them, so the 8 ladder staffs + the 2 Bo staffs are re-read FROM SKYYARMORY'S OWN FILES
    under this pack's name (verified in a bare JVM: the item's path stays SkyyArmory's file). Players got SkyyArmory's staffs (look, ladder
    Mana, Bo Pole-Vault) all along - only the pack label was SkyySkills. ManaGuard.armCheck now also reads the item's FILE and its real pack
    (AssetMap.getPath + AssetModule.findAssetPackForPath): from SkyyArmory's file = INFO "re-read under ... - same file"; a real other file =
    WARN as before. SkyySkills' spell-cost overrides are unchanged.
REVIEW FIXES: (a) MovementStates.rolling is the landing roll's flag: while OUR roll is on or a press waits, a 'rolling' tick no longer
    drops the press or restarts the 150 ms settle (tapHard = the old blocks minus 'rolling'); the press fires once the roll and 'rolling'
    are gone (within PRESS_BUFFER_MS). Without our roll, 'rolling' (landing) still blocks. (b) every new roll gets the level / tree push;
    acro.dodgeCooldownMs gates only the XP (Acro.dodgeNew; the row help says so). Rejected: a guard against held-sprint re-rolls (a client
    re-raise of held sprint looks the same on the server as a real re-press during the roll - any window would drop real presses).
NOT in this build: no migration, no new row / key / system / command, no saved-data change.
"""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.22.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.23.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.22"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
assert 'VERSION = "0.4.22"' in s and "derived from the generated 0.4.21 by tools/skills_0_4_22_patch.py" in s, "not the live generated 0.4.22"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "PRESS_BUFFER_MS" not in s and "armReport2" not in s and "DODGE_FLAT" not in s, "0.4.22 already has the 0.4.23 parts"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyySkills 0.4.22 - build script (derived from the generated 0.4.21 by tools/skills_0_4_22_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.23 - build script (derived from the generated 0.4.22 by tools/skills_0_4_23_patch.py - edit the patch, not this file;
0.4.22 was derived from the generated 0.4.21 by tools/skills_0_4_22_patch.py; ''')
rep('''0.4.22: THE MONK MOVES' SKYYSKILLS PART (Skyy 2026-10-08 "start building the monk moves"; full notes in tools/skills_0_4_22_patch.py). Deploy''',
    '''0.4.23: THE ROLL REWORK + LOG FIXES (Skyy LOCKED 2026-10-08 sprint-tap roll test; full notes in tools/skills_0_4_23_patch.py). Deploy WITH
  SkyyArmory 0.1.13. (1) The roll fires the moment sprint is PRESSED (the sprinting rise the server sees); no own cooldown and the Dodge
  root's engine default (0.35 s) set to 0 (Server/Item/RootInteractions/Dodge.json override); a press during a roll waits for it (350 ms);
  holding sprint = you leave the roll sprinting; Stamina is the only limit. (2) Back rolls: the client sends nothing when sprint is pressed
  while walking back (no sprinting flag, no speed change, no key field) - not added. (3) The roll steps are named files (25) - no inline
  steps, so no 'Missing interaction **SkyySkills_Roll_..' load warnings. (4) The staff handover check reads each staff's FILE: the 8 ladder
  staffs are re-read from SkyyArmory's own files under this pack's name (the engine's reload for Staff_Cast_* overrides) = INFO, not WARN.
  No migration, no new row / key / system. CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.23.py, -Xverify:all).
0.4.22: THE MONK MOVES' SKYYSKILLS PART (Skyy 2026-10-08 "start building the monk moves"; full notes in tools/skills_0_4_22_patch.py). Deploy''')
rep('VERSION = "0.4.22"', 'VERSION = "0.4.23"')

# ---------------------------------------------------------------------------------------------------------------- (1) the config texts
rep('''ACRO_TAP_DOC = "# Sprint-tap roll (SkyySkills 0.4.20): a sprint-key press shorter than acro.dodgeTapMs rolls the way you move (standing still = back)."''',
    '''ACRO_TAP_DOC = "# Sprint roll (SkyySkills 0.4.23): pressing sprint rolls the way you move at once; hold it and you come out sprinting (acro.dodgeTapMs: unused)."''')
rep('''ROLL_TEXT = '8-way roll, 13 force, 2 Stamina, 0.25 s safe - fixed in the jar\'''',
    '''ROLL_TEXT = '8-way roll, 13 force, 2 Stamina, 0.25 s safe, no cooldown - fixed in the jar\'''')
rep('''assert ROLL_TEXT == '8-way roll, 13 force, 2 Stamina, 0.25 s safe - fixed in the jar' and''',
    '''assert ROLL_TEXT == '8-way roll, 13 force, 2 Stamina, 0.25 s safe, no cooldown - fixed in the jar' and''')
rep('''    ("acro.dodgeTap", "Roll on sprint tap", "acrobatics", "bool", "true", "", "", "", "", "live",
     "Tap sprint: roll the way you move (still = back); hold: sprint. On ground only. Sprint must be hold.", "reload"),
    ("acro.dodgeTapMs", "Sprint tap window", "acrobatics", "int", "200", "50", "1000", "", "ms", "live,adv",
     "A sprint press shorter than this rolls; longer only sprints. At most one tap roll per 0.4 s.", "reload"),''',
    '''    ("acro.dodgeTap", "Roll on sprint press", "acrobatics", "bool", "true", "", "", "", "", "live",
     "Press sprint: roll the way you move at once; hold: you come out sprinting. On ground. No cooldown.", "reload"),
    ("acro.dodgeTapMs", "Sprint tap window (unused)", "acrobatics", "int", "200", "50", "1000", "", "ms", "live,adv",
     "Not used since SkyySkills 0.4.23: the roll fires the moment you press sprint.", "reload"),''')
rep('''A short tap of the sprint key (or the dodge key) rolls the way you move: 8 directions, standing still = a back roll (vanilla 2 Stamina, 0.25 s safe; the sprint tap on the ground only); holding sprint still sprints (Server Setup: Roll on sprint tap, Sprint tap window).''',
    '''Pressing the sprint key rolls the way you move at once (or the dodge key: 8 directions, standing still = a back roll; vanilla 2 Stamina, 0.25 s safe; no cooldown - Stamina is the limit; the sprint press on the ground only, and the game sends no sprint while walking back, so sprint rolls go forward / sideways); hold sprint and you come out of the roll sprinting (Server Setup: Roll on sprint press).''')

# ---------------------------------------------------------------------------------------------------------------- (1) the press detector
rep('''#  298 tap rolls started, 299 the last startRoll result (0 = queued), 300 the press began with no movement key (1/0), 301 the last
#  blocked tick ms, 302 the queued tap roll's ms (watchdog, 0 = none), 303 queued tap rolls that never played. Physical-player state:
#  no reset clears it.''', '''#  298 tap rolls started, 299 the last startRoll result (0 = queued), 300 the press began with no movement key (1/0), 301 the last
#  blocked tick ms, 302 the queued tap roll's ms (watchdog, 0 = none), 303 queued tap rolls that never played. Physical-player state:
#  no reset clears it.
# 0.4.23 (roll on the sprint PRESS): 296 = the pending press ms (0 = none; a press waits PRESS_BUFFER_MS for a roll on to end), 297 the last
#  STARTED roll ms (no cooldown reads it any more), 300 = the PREVIOUS tick had no horizontal movement (1/0); the rest as 0.4.20.''')
rep('''acro.addField(CtField.make("public static final long TAP_CD_MS = 400L;", acro))   # 0.4.20 fix: the tap's OWN cooldown (not the XP row)
acro.addField(CtField.make("public static final long TAP_SETTLE_MS = 300L;", acro))   # 0.4.20 fix: no press this soon after a blocked tick''',
    '''acro.addField(CtField.make("public static final long TAP_CD_MS = 0L;", acro))   # 0.4.23: NO own cooldown (Skyy: "no delay timer"; 0.4.20: 400)
acro.addField(CtField.make("public static final long TAP_SETTLE_MS = 150L;", acro))   # 0.4.23: 150 (0.4.20: 300) - no press this soon after a blocked tick
acro.addField(CtField.make("public static final long PRESS_BUFFER_MS = 350L;", acro))   # 0.4.23: a press during a roll waits this long for it to end''')
OLD_TAP = '''acro.addMethod(CtNewMethod.make(f"""
public static boolean tap(double[] s, {MVT} ms, long now, boolean rollOn, double sta) {{
  boolean sp = ms != null && ms.sprinting;
  boolean was = s[295] > 0.5;
  s[295] = sp ? 1.0 : 0.0;
  if (!{PKG}.AcroCfg.TAP_ON || ms == null) {{
    s[296] = 0.0;
    return false;
  }}
  boolean bad = tapBlocked(ms);
  if (bad) s[301] = (double) now;
  if (sp) {{
    if (!was) {{
      if (bad || (double) now - s[301] < (double) TAP_SETTLE_MS) s[296] = 0.0;
      else {{ s[296] = (double) now; s[300] = ms.horizontalIdle ? 1.0 : 0.0; }}
    }} else if (bad) s[296] = 0.0;
    return false;
  }}
  if (!was) return false;
  double t0 = s[296];
  s[296] = 0.0;
  if (t0 <= 0.0 || bad || rollOn) return false;
  if ((double) now - t0 > (double) {PKG}.AcroCfg.TAP_MS) return false;
  if (s[300] < 0.5 && ms.horizontalIdle) return false;
  if (sta >= 0.0 && sta < 0.5) return false;
  if ((double) now - s[297] < (double) TAP_CD_MS) return false;
  return true;
}}""", acro))
# after startRoll: the cooldown / counter / watchdog only for a roll that was really queued (code 0) - a refused start costs nothing
acro.addMethod(CtNewMethod.make("""
public static void tapDone(double[] s, long now, int code) {
  s[299] = (double) code;
  if (code != 0) return;
  s[297] = (double) now;
  s[298] = s[298] + 1.0;
  s[302] = (double) now;
}""", acro))'''
NEW_TAP = '''# 0.4.23 (Skyy LOCKED 2026-10-08 "just make it roll the moment you hit sprint, and if you hold, you come out of the roll sprinting"; "no delay
# timer. it should be spam able"): the PRESS detector replaces 0.4.20's tap (same name / signature, AcroSys calls it once per tick). A press =
# the sprinting RISE on an unblocked tick whose PREVIOUS tick was moving (s[300]: a sprint that resumes because W came back while the sprint
# key is held is no press), at least TAP_SETTLE_MS after the last blocked tick, not with under 0.5 Stamina (sta >= 0 = read on the rise
# tick). The press is remembered (s[296]) and fires on the first tick no roll is on - at most PRESS_BUFFER_MS later, dropped on a blocked
# tick. NO cooldown of its own (TAP_CD_MS = 0, never read). The release does nothing; holding = sprinting on (the server never touches it).
# Review fix: MovementStates.rolling is the LANDING roll's flag (the fall mitigation, 0.4.14). While OUR roll is on (rollOn) or a press
# waits, a 'rolling' tick (if the client flags the dodge too) is NOT a blocked tick: a press made then is kept and fires when the roll
# ends (and 'rolling' is gone), and it does not restart the 150 ms settle. Without our roll, 'rolling' = the landing roll = blocked as before.
acro.addMethod(CtNewMethod.make(f"""
public static boolean tapHard({MVT} ms) {{
  if (ms == null) return true;
  return excludedState(ms) || ms.crouching || ms.forcedCrouching || ms.sliding || !ms.onGround;
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static boolean tap(double[] s, {MVT} ms, long now, boolean rollOn, double sta) {{
  boolean sp = ms != null && ms.sprinting;
  boolean was = s[295] > 0.5;
  boolean movedBefore = s[300] < 0.5;
  s[295] = sp ? 1.0 : 0.0;
  s[300] = (ms == null || ms.horizontalIdle) ? 1.0 : 0.0;
  if (!{PKG}.AcroCfg.TAP_ON || ms == null) {{
    s[296] = 0.0;
    return false;
  }}
  boolean ownRoll = rollOn || s[296] > 0.0;
  boolean bad = tapHard(ms) || (ms.rolling && !ownRoll);
  if (bad) s[301] = (double) now;
  if (sp && !was && !bad && movedBefore && (double) now - s[301] >= (double) TAP_SETTLE_MS && !(sta >= 0.0 && sta < 0.5)) s[296] = (double) now;
  if (s[296] <= 0.0) return false;
  if (bad || (double) now - s[296] > (double) PRESS_BUFFER_MS) {{
    s[296] = 0.0;
    return false;
  }}
  if (rollOn || ms.rolling) return false;
  return true;
}}""", acro))
# after startRoll: 0 = queued (the press is used: counter + watchdog); 4 = a running chain's rules block Dodge right now (the press keeps
# waiting, PRESS_BUFFER_MS); any other refusal drops the press. Nothing here delays the next press.
acro.addMethod(CtNewMethod.make("""
public static void tapDone(double[] s, long now, int code) {
  s[299] = (double) code;
  if (code == 4) return;
  s[296] = 0.0;
  if (code != 0) return;
  s[297] = (double) now;
  s[298] = s[298] + 1.0;
  s[302] = (double) now;
}""", acro))'''
rep(OLD_TAP, NEW_TAP)
# review fix (Skyy "no delay timer"): every NEW roll gets the level / tree push (s[23]); acro.dodgeCooldownMs (DODGE_CD) now gates ONLY the
# roll XP (0.4.18-0.4.22: a roll within 400 ms of the last counted one got no push either - spam rolls pushed every other time). The
# ApplyForce of each roll SETS the velocity, so pushes never stack. dodgeNew = the edge's bookkeeping, a plain method the harness runs.
rep('''acro.addMethod(CtNewMethod.make(f"""
public static void dodge(double[] s, {ST} store, {CB} cb, {REF} ref, java.util.UUID u, long now, boolean creative, boolean excluded) {{''',
    '''acro.addMethod(CtNewMethod.make(f"""
public static void dodgeNew(double[] s, long now, boolean creative) {{
  if ({PKG}.AcroCfg.DODGE_BOOST) s[23] = (double) (now + 100L);
  if ((double) now - s[20] < (double) {PKG}.AcroCfg.DODGE_CD) return;
  s[20] = (double) now;
  if (!creative && s[291] >= {PKG}.AcroCfg.DODGE_MOVE) {{   // 0.4.19: the move gate (acro.dodgeMinMove since the last PAID roll)
    s[11] = s[11] + {PKG}.AcroCfg.DODGE_XP;
    s[291] = 0.0;
  }}
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static void dodge(double[] s, {ST} store, {CB} cb, {REF} ref, java.util.UUID u, long now, boolean creative, boolean excluded) {{''')
rep('''  if (on && s[6] < 0.5 && !excluded && (double) now - s[20] >= (double) {PKG}.AcroCfg.DODGE_CD) {{
    s[20] = (double) now;
    if (!creative && s[291] >= {PKG}.AcroCfg.DODGE_MOVE) {{   // 0.4.19: the move gate (acro.dodgeMinMove since the last PAID roll)
      s[11] = s[11] + {PKG}.AcroCfg.DODGE_XP;
      s[291] = 0.0;
    }}
    if ({PKG}.AcroCfg.DODGE_BOOST) s[23] = (double) (now + 100L);
  }}''', '''  if (on && s[6] < 0.5 && !excluded) dodgeNew(s, now, creative);   // 0.4.23: the push on every roll, the XP gap only for XP''')
rep('''    ("acro.dodgeCooldownMs", "Paid dodge cooldown", "acrobatics", "int", "400", "100", "600000", "", "ms", "live,adv", "", "reload"),''',
    '''    ("acro.dodgeCooldownMs", "Paid dodge cooldown", "acrobatics", "int", "400", "100", "600000", "", "ms", "live,adv",
     "Only how often a roll pays XP. Never delays the roll or its push (0.4.23).", "reload"),''')
rep('''      double tsta = s[295] > 0.5 ? {PKG}.Acro.stamina(store, ref) : -1.0;   // only a possible release tick reads Stamina
      if (tmc != null && {PKG}.Acro.tap(s, tmc.getMovementStates(), now, tro, tsta)) {PKG}.Acro.tapDone(s, now, {PKG}.Acro.startRoll(store, cb, ref));''',
    '''      {MVT} tms = tmc == null ? null : tmc.getMovementStates();
      double tsta = (tms != null && tms.sprinting && s[295] < 0.5) ? {PKG}.Acro.stamina(store, ref) : -1.0;   // 0.4.23: only a press (rise) tick reads Stamina
      if (tms != null && {PKG}.Acro.tap(s, tms, now, tro, tsta)) {PKG}.Acro.tapDone(s, now, {PKG}.Acro.startRoll(store, cb, ref));''')
rep('''    if ({PKG}.AcroCfg.TAP_ON) {{   // 0.4.20: a short sprint-key tap starts the vanilla Dodge chain (the 8-way roll) - any game mode, acro.enabled or not''',
    '''    if ({PKG}.AcroCfg.TAP_ON) {{   // 0.4.23: a sprint PRESS starts the vanilla Dodge chain (the 8-way roll) at once - any game mode, acro.enabled or not''')
rep('''  TAP_ON = {PKG}.SkillCfg.bool(p, "acro.dodgeTap", true);   // 0.4.20: a short sprint-key tap rolls''',
    '''  TAP_ON = {PKG}.SkillCfg.bool(p, "acro.dodgeTap", true);   // 0.4.23: a sprint PRESS rolls (0.4.20: a short tap; acro.dodgeTapMs is read but unused)''')

# ---------------------------------------------------------------------------------------------------------------- (1) + (3) the dodge files
OLD_FILES = '''_dodge_put("Server/Item/Interactions/Dodge.json", _d_main)
for _k, _id, _x, _z, _fx in DODGE_ROLLS:
    _b = copy.deepcopy(_dv_left)
    _b["Next"]["Interactions"][1]["EffectId"] = _fx
    _b["Next"]["Interactions"][2]["Direction"] = {"X": _x, "Y": 0, "Z": _z}
    assert _b == _dodge_body(_fx, _x, _z)
    _dodge_put("Server/Item/Interactions/Dodge/%s.json" % _id, _b)
for _fid, _anim in DODGE_FX:
    _e = copy.deepcopy(_dv_fx["Dodge_Left"])
    _e["ApplicationEffects"]["EntityAnimationId"] = _anim
    _dodge_put("Server/Entity/Effects/Movement/%s.json" % _fid, _e)
assert len(DODGE_FILES) == 1 + len(DODGE_ROLLS) + len(DODGE_FX) == 11
assert not set(DODGE_FILES) & set(SPELL_FILES)
# every id Dodge.json names exists (ours or vanilla), every effect a roll applies exists
_d_ints = set(os.path.basename(_p)[:-5] for _p in DODGE_FILES if _p.startswith("Server/Item/Interactions/")) | {"Dodge_Left", "Dodge_Right"}
assert all(_v in _d_ints for _k, _v in _d_next.items() if _k != "Type"), _d_next
_d_fxs = set(os.path.basename(_p)[:-5] for _p in DODGE_FILES if _p.startswith("Server/Entity/Effects/")) | {"Dodge_Invulnerability"}
assert all(_e["EffectId"] in _d_fxs for _p, _t in DODGE_FILES.items() if "/Dodge/" in _p
           for _e in json.loads(_t)["Next"]["Interactions"] if _e["Type"] == "ApplyEffect")'''
NEW_FILES = '''_dodge_put("Server/Item/Interactions/Dodge.json", _d_main)
# 0.4.23 (3): NO INLINE STEPS. The engine builds a batch's client packet before it loads the batch's inline children (AssetStore.loadAssets0:
# handleRemoveOrUpdate, then loadContainedAssets), so an inline Serial step logs 'Missing interaction **<id>_Next_Interactions_N' at load
# (24 lines in 0.4.22). Each roll is now NAMED files only, all in this jar's one Interactions batch: SkyySkills_Roll_<dir> (the vanilla
# StatsConditionWithModifier, Next = its Serial), SkyySkills_Roll_<dir>_Steps (the vanilla Serial, by name), SkyySkills_Roll_<dir>_Push (its
# ApplyForce); shared by all 6: SkyySkills_Roll_Safe (the i-frames), SkyySkills_Roll_Look_Forward / _Back (the roll look),
# SkyySkills_Roll_Spend (the Adventure-only Condition) -> SkyySkills_Roll_Spend_Steps -> SkyySkills_Roll_Spend_Stamina / _Regen.
# Re-inlined, every roll is exactly _dodge_body(fx, x, z) = 0.4.22's file (asserted below) - the vanilla Dodge_Left body.
DODGE_FLAT = {}          # id -> the named body (each goes to Server/Item/Interactions/Dodge/<id>.json)
_DF_SAFE, _DF_SPEND, _DF_SPEND_S = "SkyySkills_Roll_Safe", "SkyySkills_Roll_Spend", "SkyySkills_Roll_Spend_Steps"
_DF_STAM, _DF_REGEN = "SkyySkills_Roll_Spend_Stamina", "SkyySkills_Roll_Spend_Regen"
_DF_LOOK = {"Dodge_Forward": "SkyySkills_Roll_Look_Forward", "Dodge_Back": "SkyySkills_Roll_Look_Back"}
_dl_steps = _dv_left["Next"]["Interactions"]
assert [_x["Type"] for _x in _dl_steps] == ["ApplyEffect", "ApplyEffect", "ApplyForce", "Condition"] and _dl_steps[3]["Next"]["Type"] == "Serial"
DODGE_FLAT[_DF_SAFE] = copy.deepcopy(_dl_steps[0])
for _fx0, _lid in sorted(_DF_LOOK.items()):
    DODGE_FLAT[_lid] = dict(copy.deepcopy(_dl_steps[1]), EffectId=_fx0)
_sp = copy.deepcopy(_dl_steps[3])
DODGE_FLAT[_DF_STAM], DODGE_FLAT[_DF_REGEN] = _sp["Next"]["Interactions"]
DODGE_FLAT[_DF_SPEND_S] = dict(_sp["Next"], Interactions=[_DF_STAM, _DF_REGEN])
DODGE_FLAT[_DF_SPEND] = dict(_sp, Next=_DF_SPEND_S)
for _k, _id, _x, _z, _fx in DODGE_ROLLS:
    _b = copy.deepcopy(_dv_left)
    _b["Next"]["Interactions"][1]["EffectId"] = _fx
    _b["Next"]["Interactions"][2]["Direction"] = {"X": _x, "Y": 0, "Z": _z}
    assert _b == _dodge_body(_fx, _x, _z)
    DODGE_FLAT[_id + "_Push"] = copy.deepcopy(_b["Next"]["Interactions"][2])
    DODGE_FLAT[_id + "_Steps"] = dict(copy.deepcopy(_b["Next"]), Interactions=[_DF_SAFE, _DF_LOOK[_fx], _id + "_Push", _DF_SPEND])
    DODGE_FLAT[_id] = dict(copy.deepcopy(_b), Next=_id + "_Steps")


def _dodge_inline(x):
    """a named roll body with every name of DODGE_FLAT put back inline (the 0.4.22 shape)"""
    if isinstance(x, str) and x in DODGE_FLAT:
        return _dodge_inline(DODGE_FLAT[x])
    if isinstance(x, list):
        return [_dodge_inline(_v) for _v in x]
    if isinstance(x, dict):
        return dict((_k2, _v if _k2 in ("Type", "EffectId", "Failed", "InteractionModifierId") else _dodge_inline(_v)) for _k2, _v in x.items())
    return x


def _dodge_has_inline(x, top=True):
    """True when a step below the top is an inline interaction object (a dict with a Type)"""
    if isinstance(x, dict):
        if not top and isinstance(x.get("Type"), str):
            return True
        return any(_dodge_has_inline(_v, False) for _k2, _v in x.items() if _k2 not in ("VelocityConfig", "Direction", "Costs", "StatModifiers"))
    if isinstance(x, list):
        return any(_dodge_has_inline(_v, False) for _v in x)
    return False
for _k, _id, _x, _z, _fx in DODGE_ROLLS:
    assert _dodge_inline(_id) == _dodge_body(_fx, _x, _z), "0.4.23: the named roll %s re-inlined is not the 0.4.22 body" % _id
assert len(DODGE_FLAT) == 3 * len(DODGE_ROLLS) + 7 == 25 and not any(_dodge_has_inline(_v) for _v in DODGE_FLAT.values())
assert all(_i.startswith("SkyySkills_Roll_") for _i in DODGE_FLAT) and DODGE_FLAT[_DF_STAM]["Type"] == "ChangeStatWithModifier"
for _fid in sorted(DODGE_FLAT):
    _dodge_put("Server/Item/Interactions/Dodge/%s.json" % _fid, DODGE_FLAT[_fid])
DODGE_INT_IDS = ["Dodge"] + sorted(DODGE_FLAT)          # 0.4.23: every interaction id this jar ships for the roll (the clash checks)
# 0.4.23 (1): the vanilla Dodge ROOT + "Cooldown": {"Cooldown": 0}. Without a Cooldown the engine applies
# InteractionTypeUtils.getDefaultCooldown(Dodge) = 0.35 s (InteractionManager.isOnCooldown) and a server-started chain on cooldown fails
# silently (executeChain0); CooldownHandler.isOnCooldown answers false for a cooldown <= 0. Stamina stays the only limit.
DODGE_ROOT = dict(copy.deepcopy(_dv_root), Cooldown={"Cooldown": 0})
assert DODGE_ROOT == {"Interactions": ["Dodge"], "RequireNewClick": True, "Cooldown": {"Cooldown": 0}}
_dodge_put("Server/Item/RootInteractions/Dodge.json", DODGE_ROOT)
for _fid, _anim in DODGE_FX:
    _e = copy.deepcopy(_dv_fx["Dodge_Left"])
    _e["ApplicationEffects"]["EntityAnimationId"] = _anim
    _dodge_put("Server/Entity/Effects/Movement/%s.json" % _fid, _e)
assert len(DODGE_FILES) == 1 + len(DODGE_FLAT) + 1 + len(DODGE_FX) == 31
assert not set(DODGE_FILES) & set(SPELL_FILES)
# every id Dodge.json names exists (ours or vanilla), every name a roll file uses exists, every effect a roll applies exists
_d_ints = set(os.path.basename(_p)[:-5] for _p in DODGE_FILES if _p.startswith("Server/Item/Interactions/")) | {"Dodge_Left", "Dodge_Right"}
assert all(_v in _d_ints for _k, _v in _d_next.items() if _k != "Type"), _d_next
for _fid, _fb in DODGE_FLAT.items():
    _names = ([_fb["Next"]] if isinstance(_fb.get("Next"), str) else []) + [_n for _n in (_fb.get("Interactions") or []) if isinstance(_n, str)]
    assert all(_n in _d_ints for _n in _names), (_fid, _names)
    assert _fb.get("Failed") in (None, "Stamina_Bar_Flash"), _fid
_d_fxs = set(os.path.basename(_p)[:-5] for _p in DODGE_FILES if _p.startswith("Server/Entity/Effects/")) | {"Dodge_Invulnerability"}
assert all(_e["EffectId"] in _d_fxs for _e in DODGE_FLAT.values() if _e["Type"] == "ApplyEffect")
assert "Stamina_Bar_Flash" in _dv_names and not [_i for _i in DODGE_FLAT if _i in _dv_names]'''
rep(OLD_FILES, NEW_FILES)
rep('''# our new ids are new (never a vanilla id of any asset type)
_dv_clash = [_i for _i in DODGE_INT_IDS[1:] + ["Dodge_Forward", "Dodge_Back"] if _i in _dv_names]''',
    '''# our new ids are new (never a vanilla id of any asset type; 0.4.23: the 25 named roll files are checked again where they are made)
_dv_clash = [_i for _i in DODGE_INT_IDS[1:] + ["Dodge_Forward", "Dodge_Back"] if _i in _dv_names]''')
rep('''def _dodge_clash(names):
    return sorted(n for n in names if n in DODGE_FILES''', '''def _dodge_clash(names):          # 0.4.23: DODGE_FILES has the root override + the 25 named roll files
    return sorted(n for n in names if n in DODGE_FILES''')
rep('''print("dodge roll (0.4.18): %d files generated from Assets.zip (Dodge.json -> 8 directions + standing = back; %d roll interactions = the vanilla "
      "Dodge_Left body turned: 2 Stamina, force 13, 0.25 s i-frames, air as vanilla; effects %s); no clash with %d live-set jars or the pack "
      "mods %s" % (len(DODGE_FILES), len(DODGE_ROLLS), ", ".join("%s=%s" % _f for _f in DODGE_FX), len(_d_checked),
                   ", ".join(sorted(_d_found)) or "(none installed)"))''',
    '''print("dodge roll (0.4.18 / 0.4.23): %d files generated from Assets.zip (Dodge.json -> 8 directions + standing = back; %d rolls = the vanilla "
      "Dodge_Left body turned, as %d NAMED files (no inline step); the Dodge root with Cooldown 0 (vanilla: none = the 0.35 s default); 2 Stamina, "
      "force 13, 0.25 s i-frames, air as vanilla; effects %s); no clash with %d live-set jars or the pack mods %s" % (
          len(DODGE_FILES), len(DODGE_ROLLS), len(DODGE_FLAT), ", ".join("%s=%s" % _f for _f in DODGE_FX), len(_d_checked),
          ", ".join(sorted(_d_found)) or "(none installed)"))''')
rep('''assert all(json.loads(DODGE_FILES["Server/Item/Interactions/Dodge/%s.json" % _r[1]])["Next"]["Interactions"][2]["Force"] == 13 for _r in DODGE_ROLLS)''',
    '''assert all(json.loads(DODGE_FILES["Server/Item/Interactions/Dodge/%s_Push.json" % _r[1]])["Force"] == 13 for _r in DODGE_ROLLS)   # 0.4.23: named push''')
rep('''assert not set(ASSET_FILES) & set(DODGE_FILES) and all(_p.startswith(("Server/Item/Interactions/", "Server/Entity/Effects/Movement/")) for _p in DODGE_FILES)''',
    '''assert not set(ASSET_FILES) & set(DODGE_FILES) and all(_p.startswith(("Server/Item/Interactions/", "Server/Entity/Effects/Movement/", "Server/Item/RootInteractions/Dodge.json")) for _p in DODGE_FILES)''')

# ---------------------------------------------------------------------------------------------------------------- (4) the staff handover check
_a0 = s.index('mgd.addMethod(CtNewMethod.make(J14(r"""\npublic static String[] armReport(String[] packs) {')
_a1 = s.index('}"""), mgd))', _a0) + len('}"""), mgd))')
OLD_ARM = s[_a0:_a1]          # 0.4.15's armReport, whole (its texts live on in armReport2 word for word)
assert "Staff handover: " in OLD_ARM and OLD_ARM.count("public static") == 1
rep(OLD_ARM, '''# 0.4.23 (4): the pack an item's FILE belongs to (AssetMap.getPath + AssetModule.findAssetPackForPath); null = unknown. SkyySkills' own
# Staff_Cast_Summon_Charged / Staff_Cast_Cost overrides make the engine re-read (AssetStore.reloadChildrenContainerAssets) every item whose
# inline vars inherit them - the ladder staffs from SkyyArmory's own files - under THIS pack's name: the label is ours, the file theirs.
mgd.addMethod(CtNewMethod.make(J14(r"""
public static String filePack(com.hypixel.hytale.assetstore.AssetMap m, String id) {
  try {
    if (m == null || id == null) return null;
    java.nio.file.Path p = m.getPath(id);
    if (p == null) return null;
    com.hypixel.hytale.server.core.asset.AssetModule am = com.hypixel.hytale.server.core.asset.AssetModule.get();
    if (am == null) return null;
    com.hypixel.hytale.assetstore.AssetPack ap = am.findAssetPackForPath(p);
    return ap == null ? null : ap.getName();
  } catch (Throwable t) { return null; }
}"""), mgd))
# 0.4.23: packs[i] = the pack the engine names, files[i] = the pack of the file it loaded (null = not known): a SkyyArmory file counts as
# SkyyArmory's even when another pack re-read it; without such a re-read the texts are 0.4.15's word for word
mgd.addMethod(CtNewMethod.make(J14(r"""
public static String[] armReport2(String[] packs, String[] files) {
  String[] ids = @PKG@.ManaCost.ARM_IDS;
  if (ids.length == 0) return new String[] { "skip", "" };
  int mine = 0;
  int other = 0;
  int miss = 0;
  int reread = 0;
  String pk = null;
  String by = null;
  StringBuilder ot = new StringBuilder();
  for (int i = 0; i < ids.length; i++) {
    String p = (packs != null && i < packs.length) ? packs[i] : null;
    String f = (files != null && i < files.length) ? files[i] : null;
    if (p == null) { miss++; continue; }
    if (armoryPack(p)) { mine++; pk = p; continue; }
    if (armoryPack(f)) { mine++; reread++; pk = f; by = p; continue; }
    other++;
    if (ot.length() > 0) ot.append(", ");
    ot.append(ids[i]).append(" (").append(p).append(")");
  }
  if (mine + other == 0) return new String[] { "", "the game's item assets could not be read" };
  String pre = "Staff handover: ";
  String mt = miss > 0 ? "; " + miss + " not in the game's item assets" : "";
  String rr = reread > 0 ? " (" + reread + " of them re-read from " + pk + "'s own files under the name " + by + ": the engine re-reads every item whose vanilla vars inherit Staff_Cast_Summon_Charged / Staff_Cast_Cost when SkyySkills' overrides of those load - same file, only the label)" : "";
  if (other == 0) return new String[] { "info", pre + (miss == 0 ? "all " + mine : mine + " of " + ids.length) + " ladder staffs (Wood to Onyxium) come from " + pk + " - their Mana and orbs are SkyyArmory's staff ladder" + rr + mt };
  return new String[] { "warn", pre + other + " of " + ids.length + " ladder staffs do NOT come from SkyyArmory: " + ot.toString() + ". SkyySkills @VERSION@ no longer ships them, so they run on that pack's file - the vanilla one spends 50 Mana behind SkyySkills' 10-Mana check. Install SkyyArmory 0.1+ together with this SkyySkills (they deploy and roll back as a pair)" + rr + mt + "." };
}"""), mgd))
mgd.addMethod(CtNewMethod.make(J14(r"""
public static String[] armReport(String[] packs) {
  return armReport2(packs, null);
}"""), mgd))''')
rep('''public static String[] armCheck() {
  String[] ids = @PKG@.ManaCost.ARM_IDS;
  String[] ps = new String[ids.length];
  try {
    com.hypixel.hytale.assetstore.map.DefaultAssetMap m = @ITM@.getAssetMap();
    if (m != null) {
      for (int i = 0; i < ids.length; i++) {
        try { ps[i] = m.getAssetPack(ids[i]); } catch (Throwable t) { ps[i] = null; }
      }
    }
  } catch (Throwable t) { }
  return armReport(ps);
}"""), mgd))''', '''public static String[] armCheck() {
  String[] ids = @PKG@.ManaCost.ARM_IDS;
  String[] ps = new String[ids.length];
  String[] fs = new String[ids.length];
  try {
    com.hypixel.hytale.assetstore.map.DefaultAssetMap m = @ITM@.getAssetMap();
    if (m != null) {
      for (int i = 0; i < ids.length; i++) {
        try { ps[i] = m.getAssetPack(ids[i]); } catch (Throwable t) { ps[i] = null; }
        fs[i] = filePack(m, ids[i]);   // 0.4.23: the pack of the FILE the engine loaded
      }
    }
  } catch (Throwable t) { }
  return armReport2(ps, fs);
}"""), mgd))''')

assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "0.4.23 adds no system / command"
with open(dst, "w", encoding="utf8", newline="") as f:
    f.write(s.replace(LF, NL))
print("wrote %s" % os.path.relpath(dst, ROOT))
