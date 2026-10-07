"""Derive SkyySkills/build_skyyskills_0.4.20.py from the LIVE generated SkyySkills/build_skyyskills_0.4.19.py (= the tools/deploy_set.py SET
pin, deployed 2026-10-06 evening with the roll move gate; 0.4.19 came from 0.4.18 by tools/skills_0_4_19_patch.py, ... 0.4.6 from Skyy's
EDITED 0.4.5 - commit ab75b6c; never re-run skills_0_4_5 or older patches). Same style as skills_0_4_19_patch.py: rep(old, new) with
asserted single anchors, newline-agnostic; 0.4.19 stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_20_patch.py   then   python SkyySkills/build_skyyskills_0.4.20.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.20.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/skills0420/, deleted afterwards)

0.4.20 = THE SPRINT-TAP ROLL. Skyy LOCKED 2026-10-06 (docs/answered/skills.md, after finding no Dodge key in Settings -> Controls - one key
= crouch / slide while sprinting / roll when held while falling; the vanilla dodge input is unbound): roll trigger = "Tap the sprint key" ->
a short sprint-key tap rolls in the movement direction (standing still = back roll); holding the key still sprints.
(1) DETECTION (server, AcroSys tick, world thread): the client reports MovementStates.sprinting in its movement packets (the engine path
    Perfect Dodges 0.5.16 SprintWalkTriggerSystem uses - read for the idea, no code copied). Acro.tap: a sprinting rise starts a press
    (s[296] = now) unless the player is in a blocked state; the fall is a TAP when the press lasted at most acro.dodgeTapMs (NEW row,
    default 200 ms, 50-1000), the release tick is not blocked, no roll effect is on, and the last STARTED tap roll is at least
    Acro.TAP_CD_MS (400, fixed - NOT the acro.dodgeCooldownMs XP row) old. Longer presses only sprint. BLOCKED = Acro.excludedState
    (mounted, flying, gliding, sitting, sleeping, climbing, in fluid, swimming, mantling) + crouching / forced crouch / sliding / rolling
    (a crouch-slide out of a short sprint is not a roll) + NOT ON THE GROUND; a blocked tick while the key is held cancels the press,
    and no press starts within Acro.TAP_SETTLE_MS (300) of a blocked tick. acro.dodgeTap=false (NEW row) = no tap rolls.
    REVIEW FIXES (2 critics): (a) a press that began while moving is no tap when the fall comes with no movement key (horizontalIdle:
    letting go of W while holding sprint, toggle sprint + a short W tap); a press that began standing still keeps the back roll.
    (b) Stamina under 0.5 at the fall = no tap (sprint ran out of breath). (c) ground only (an air roll's ApplyForce Set Y 0 zeroes the
    fall speed = no fall damage; the vanilla dodge input is unchanged). (d) the tap's own 400 ms cooldown (an admin's XP cooldown no
    longer throttles or un-throttles the roll). (e) cooldown / counter only when startRoll returned 0 (Acro.tapDone). (f) the
    "roll is on" guard reads the roll effects itself while acro.enabled is off (s[6] is stale then). (g) the 300 ms settle after a
    blocked tick (sprint resuming after a slide / crouch roll / landing is no press). (h) a watchdog (Acro.tapWatch): a queued tap
    roll whose roll effect never shows within 1 s counts in s[303] and logs ONE warning naming the engine's "Client failed to send
    client data" line, so a client that does not answer a server-started Dodge chain is visible in the log.
(2) START (Acro.startRoll): the vanilla server path (EntityStatsSystems$Changes, InteractionRunCommand, DamageSystems all do this):
    InteractionModule.get().getInteractionManagerComponent() -> the player's InteractionManager; RootInteraction "Dodge" (vanilla root,
    untouched) -> canRun(InteractionType.Dodge, root) (the chain rules: a running chain that blocks Dodge blocks the tap too) ->
    InteractionContext.forInteraction(im, ref, Dodge, cb) -> initChain(Dodge, ctx, root, false) -> queueExecuteChain. The chain is 0.4.18's:
    Dodge.json (Flying false) -> MovementCondition (the CLIENT answers the direction: WaitForDataFrom.Client) -> the 8 rolls, no key = back
    roll; each roll = vanilla StatsConditionWithModifier Stamina 2 (no Stamina = vanilla Stamina_Bar_Flash, no roll), 0.25 s
    Dodge_Invulnerability, ApplyForce Set 13. A failure = 1 WARN line (logged once), no roll. Result code kept in s[299].
(3) Everything 0.4.18 / 0.4.19 do stays: Acro.dodge sees the roll effects exactly as before (Acro XP 3 per roll, the move gate, the 400 ms
    paid cooldown, the push), no XP cap, the assets are byte-identical. Acro state double[296] -> double[304]: 295 prev sprinting, 296 the
    press ms (0 = none), 297 the last tap roll ms, 298 tap rolls started, 299 the last startRoll result, 300 press began standing
    still, 301 last blocked tick ms, 302 watchdog ms, 303 queued tap rolls that never played.
(4) Server Setup (Skills > Acrobatics): acro.dodgeTap "Roll on sprint tap" (bool, true) and acro.dodgeTapMs "Sprint tap window" (int ms,
    200, 50-1000), right after the read-only acro.roll row. The default file gets both (with one comment line) after acro.dodgeMinMove; an
    EXISTING file is not touched (no migration: a missing key reads the same default; the kit appends the line on the first change).
LATENCY (honest): the roll starts on key UP. Release -> the client's next movement packet -> ping/2 -> the server's next tick (0-33 ms) ->
    the queued chain runs at the next InteractionManager tick (0-33 ms) -> ping/2 -> the client plays the roll. About ping + 15-65 ms after
    the release (single player / LAN: ~20-70 ms); the i-frames start on the server after the client's direction answer (+ ~ping/2). The
    vanilla dodge input (unbound) is client-predicted (no delay) and still works.
NOT in this build: no new assets, no migration, no new system / command / event (AcroSys calls the two new static methods).
"""
import difflib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.19.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.20.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.19"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.19"' in s and "derived from the generated 0.4.18 by tools/skills_0_4_19_patch.py" in s, "not the live generated 0.4.19"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "DODGE_FILES" in s and "acro.dodgeMinMove" in s and "AcroMig" in s and "ROLL_SETTLE_MS" in s, "the 0.4.18 roll / 0.4.19 gate is missing"
for _x in ("acro.dodgeTap", "TAP_ON", "startRoll", "InteractionManager\"", "new double[304]"):
    assert _x not in s, "0.4.19 already has " + _x
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


# blocks that must stay byte-identical (0.4.19 code this build does not touch)
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
        block("# ================= 0.4.18 DODGE ROLL", "# ---- 0.4.18 dodge roll conflict check"),
        block("# ---- AcroMig (0.4.19", "# ---- ManaGuard (point 3)"),
        block("# 0.4.18: a \"dodge\" = any of the 4 roll effects", "# sliding XP cap (review fix)")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.19 - build script (derived from the generated 0.4.18 by tools/skills_0_4_19_patch.py - edit the patch, not this file;
0.4.18 was derived''', '''"""SkyySkills 0.4.20 - build script (derived from the generated 0.4.19 by tools/skills_0_4_20_patch.py - edit the patch, not this file;
0.4.19 was derived from the generated 0.4.18 by tools/skills_0_4_19_patch.py; 0.4.18 was derived''')
HEAD_0420 = '''0.4.20: THE SPRINT-TAP ROLL (Skyy LOCKED 2026-10-06 roll trigger = "Tap the sprint key"; full notes in tools/skills_0_4_20_patch.py). Keeps
  all of 0.4.19 (same pairing; 0.4.19 is a safe rollback - the two new keys are simply ignored). A sprint-key press shorter than
  acro.dodgeTapMs (200 ms) starts the vanilla Dodge root chain for the player from the server (0.4.18's 8-way roll: the client picks the
  direction, no key = back roll; 2 Stamina, 0.25 s safe); holding the key still sprints. Not while mounted / flying / gliding / sitting /
  sleeping / climbing / in fluid / swimming / mantling / crouching / sliding / rolling / in the air, not while a roll is on, not when the
  movement keys came up with it, not out of Stamina, at most one tap roll per 0.4 s (own cooldown). Rows acro.dodgeTap (on/off) +
  acro.dodgeTapMs. No migration, no new assets.
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.20.py, -Xverify:all, scratch under tools/dev/scratch deleted afterwards).
'''
before('0.4.19: THE ROLL MOVE GATE + NO MOVE XP CAP (Skyy LOCKED 2026-10-06 "add the move gate like jumps but remove the xp cap on both"; full\n', HEAD_0420)
rep('VERSION = "0.4.19"\n', 'VERSION = "0.4.20"\n')

# ---------------------------------------------------------------------------------------------------------------- engine class names
after('ECC = "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent"\n',
      '''# 0.4.20: the sprint-tap roll starts the vanilla Dodge root chain from the server (InteractionManager.initChain + queueExecuteChain)
IMG = "com.hypixel.hytale.server.core.entity.InteractionManager"
IMM = "com.hypixel.hytale.server.core.modules.interaction.InteractionModule"
RTI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.RootInteraction"
ITY = "com.hypixel.hytale.protocol.InteractionType"
ICX = "com.hypixel.hytale.server.core.entity.InteractionContext"
ICH = "com.hypixel.hytale.server.core.entity.InteractionChain"
''')

# ---------------------------------------------------------------------------------------------------------------- (4) default file lines
TAP_DOC = ("# Sprint-tap roll (SkyySkills 0.4.20): a sprint-key press shorter than acro.dodgeTapMs rolls the way you move (standing still"
           " = back).")
assert len(TAP_DOC) <= 140 and all(ord(c) < 128 for c in TAP_DOC) and '"' not in TAP_DOC and "\\" not in TAP_DOC
rep('''ACRO_L.append("acro.dodgeMinMove=2.0")
''', '''ACRO_L.append("acro.dodgeMinMove=2.0")
ACRO_TAP_DOC = %s   # 0.4.20: the sprint-tap roll (no migration: a missing key reads the same default)
ACRO_L.append(ACRO_TAP_DOC)
ACRO_L.append("acro.dodgeTap=true")
ACRO_L.append("acro.dodgeTapMs=200")
''' % json.dumps(TAP_DOC))

# ---------------------------------------------------------------------------------------------------------------- (1) AcroCfg
rep('''              "double DODGE_MOVE = 2.0", "double MAX_PER_MIN = 0.0", ''',
    '''              "double DODGE_MOVE = 2.0", "boolean TAP_ON = true", "long TAP_MS = 200L", "double MAX_PER_MIN = 0.0", ''')
rep('''  DODGE_MOVE = nn({PKG}.SkillCfg.dbl(p, "acro.dodgeMinMove", 2.0));   // 0.4.19: blocks moved on your own between paid rolls
''', '''  DODGE_MOVE = nn({PKG}.SkillCfg.dbl(p, "acro.dodgeMinMove", 2.0));   // 0.4.19: blocks moved on your own between paid rolls
  TAP_ON = {PKG}.SkillCfg.bool(p, "acro.dodgeTap", true);   // 0.4.20: a short sprint-key tap rolls
  TAP_MS = Math.max(50L, Math.min(1000L, {PKG}.SkillCfg.lng(p, "acro.dodgeTapMs", 200L)));
''')

# ---------------------------------------------------------------------------------------------------------------- (1)+(2)+(3) Acro
rep('''#  The jump gate s[10] counts the same own movement (a roll slide feeds neither gate) and takes back the same 2 ticks at a new roll.
''', '''#  The jump gate s[10] counts the same own movement (a roll slide feeds neither gate) and takes back the same 2 ticks at a new roll.
# 0.4.20 (sprint-tap roll): double[304]: 295 prev sprinting, 296 the sprint press ms (0 = none / cancelled), 297 the last tap roll ms,
#  298 tap rolls started, 299 the last startRoll result (0 = queued), 300 the press began with no movement key (1/0), 301 the last
#  blocked tick ms, 302 the queued tap roll's ms (watchdog, 0 = none), 303 queued tap rolls that never played. Physical-player state:
#  no reset clears it.
''')
rep('''  double[] n = new double[296];   // 0.4.19: 292 -> 296 (the roll move gate)
''', '''  double[] n = new double[304];   // 0.4.20: 296 -> 304 (the sprint-tap roll); 0.4.19: 292 -> 296 (the roll move gate)
''')
after('''acro.addField(CtField.make("public static final long ROLL_SETTLE_MS = 700L;", acro))   # 0.4.19: the slide after a roll effect (not own movement)
''', '''acro.addField(CtField.make("public static boolean TAP_FAILED = false;", acro))   # 0.4.20: startRoll's WARN is logged once
acro.addField(CtField.make("public static boolean TAP_NOROLL = false;", acro))   # 0.4.20 fix: the watchdog's WARN is logged once
acro.addField(CtField.make("public static final long TAP_CD_MS = 400L;", acro))   # 0.4.20 fix: the tap's OWN cooldown (not the XP row)
acro.addField(CtField.make("public static final long TAP_SETTLE_MS = 300L;", acro))   # 0.4.20 fix: no press this soon after a blocked tick
''')
TAP_JAVA = '''# 0.4.20 (Skyy LOCKED 2026-10-06 "Tap the sprint key"): the sprint-tap detector, once per tick from AcroSys. ms = this tick's MovementStates
# (the client's sprint state); rollOn = a roll effect is on; sta = Stamina now (-1 = not read / unknown). true = start a roll now (the
# caller runs startRoll, then tapDone). A press = the sprinting rise on an unblocked tick at least TAP_SETTLE_MS (300) after the last
# blocked tick (cancelled when any held tick is blocked); a tap = the fall at most acro.dodgeTapMs after the press, on an unblocked tick,
# no roll on, at least TAP_CD_MS (400) after the last STARTED tap roll. Review fixes: BLOCKED includes "not on the ground" (an air roll's
# ApplyForce Set Y 0 would zero the fall speed = no fall damage); a press that began while moving whose fall comes with NO movement key
# is not a tap (letting go of W while holding sprint; toggle sprint + a short W tap); a fall with Stamina under 0.5 is not a tap (sprint
# ran out of breath, not a key release); a press right after a slide / crouch roll / landing (sprint resuming) is not a tap. Never throws.
acro.addMethod(CtNewMethod.make(f"""
public static boolean tapBlocked({MVT} ms) {{
  if (ms == null) return true;
  return excludedState(ms) || ms.crouching || ms.forcedCrouching || ms.sliding || ms.rolling || !ms.onGround;
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
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
}""", acro))
# the watchdog (review: a chain the client never answers ends silently): a queued tap roll whose roll effect never shows within 1 s
# counts in s[303] and logs ONE warning (too little Stamina = the vanilla bar flash is the normal reason)
acro.addMethod(CtNewMethod.make(f"""
public static void tapWatch(double[] s, long now, boolean rollOn) {{
  if (s[302] <= 0.0) return;
  if (rollOn) {{ s[302] = 0.0; return; }}
  if ((double) now - s[302] < 1000.0) return;
  s[302] = 0.0;
  s[303] = s[303] + 1.0;
  if (!TAP_NOROLL) {{ TAP_NOROLL = true; {PKG}.SkillCfg.warn("a sprint-tap roll was queued but no roll played within 1 s (logged once). Too little Stamina is normal; otherwise look in this log for: Client failed to send client data (the client did not answer the Dodge chain)"); }}
}}""", acro))
# a roll effect is on (the same 4 effects dodge() sees) - for the tap while acro.enabled is off (dodge() does not run then, s[6] is stale)
acro.addMethod(CtNewMethod.make(f"""
public static boolean rollFx({ST} store, {REF} ref) {{
  try {{
    {ECC} ecc = ({ECC}) store.getComponent(ref, {ECC}.getComponentType());
    if (ecc == null) return false;
    String[] ids = new String[] {{ "Dodge_Left", "Dodge_Right", "Dodge_Forward", "Dodge_Back" }};
    for (int k = 0; k < ids.length; k++) {{
      int i = {EFX}.getAssetMap().getIndex(ids[k]);
      if (i != Integer.MIN_VALUE && ecc.hasEffect(i)) return true;
    }}
  }} catch (Throwable t) {{ }}
  return false;
}}""", acro))
# Stamina now; -1 = unknown (no stat map / no value)
acro.addMethod(CtNewMethod.make(f"""
public static double stamina({ST} store, {REF} ref) {{
  try {{
    {ESM} m = ({ESM}) store.getComponent(ref, {ESM}.getComponentType());
    if (m == null) return -1.0;
    {ESV} sv = m.get({DST}.getStamina());
    if (sv == null) return -1.0;
    return (double) sv.get();
  }} catch (Throwable t) {{ return -1.0; }}
}}""", acro))
# the roll start: the vanilla server-started chain (EntityStatsSystems$Changes / InteractionRunCommand pattern) on the vanilla Dodge root
# (0.4.18's Dodge.json: Flying false -> MovementCondition answered by the client -> the 8 rolls, no key = back). 0 = queued; 1 no
# InteractionModule, 2 no InteractionManager, 3 no Dodge root, 4 a running chain's rules block Dodge, 5 no chain, 9 failed (WARN once).
acro.addMethod(CtNewMethod.make(f"""
public static int startRoll({ST} store, {CB} cb, {REF} ref) {{
  try {{
    {IMM} mod = {IMM}.get();
    if (mod == null) return 1;
    {IMG} im = ({IMG}) store.getComponent(ref, mod.getInteractionManagerComponent());
    if (im == null) return 2;
    {RTI} root = ({RTI}) {RTI}.getAssetMap().getAsset("Dodge");
    if (root == null) return 3;
    if (!im.canRun({ITY}.Dodge, root)) return 4;
    {ICX} ctx = {ICX}.forInteraction(im, ref, {ITY}.Dodge, cb);
    {ICH} ch = im.initChain({ITY}.Dodge, ctx, root, false);
    if (ch == null) return 5;
    im.queueExecuteChain(ch);
    return 0;
  }} catch (Throwable t) {{
    if (!TAP_FAILED) {{ TAP_FAILED = true; {PKG}.SkillCfg.warn("sprint-tap roll could not start (logged once): " + t); }}
    return 9;
  }}
}}""", acro))
'''
before("# sliding XP cap (review fix): per-second ring, see the STATE layout above\n", TAP_JAVA)

# ---------------------------------------------------------------------------------------------------------------- (1)+(2) AcroSys
rep('''      {PKG}.Acro.falls(s, store, ref, now, creative);
    }}
    {PKG}.Brew.tick(u, store, cb, ref, dt);
''', '''      {PKG}.Acro.falls(s, store, ref, now, creative);
    }}
    if ({PKG}.AcroCfg.TAP_ON) {{   // 0.4.20: a short sprint-key tap starts the vanilla Dodge chain (the 8-way roll) - any game mode, acro.enabled or not
      {MSC} tmc = ({MSC}) store.getComponent(ref, {MSC}.getComponentType());
      boolean tro = {PKG}.AcroCfg.ENABLED ? s[6] > 0.5 : {PKG}.Acro.rollFx(store, ref);   // s[6] is only fresh while dodge() runs
      {PKG}.Acro.tapWatch(s, now, tro);
      double tsta = s[295] > 0.5 ? {PKG}.Acro.stamina(store, ref) : -1.0;   // only a possible release tick reads Stamina
      if (tmc != null && {PKG}.Acro.tap(s, tmc.getMovementStates(), now, tro, tsta)) {PKG}.Acro.tapDone(s, now, {PKG}.Acro.startRoll(store, cb, ref));
    }}
    {PKG}.Brew.tick(u, store, cb, ref, dt);
''')

# ---------------------------------------------------------------------------------------------------------------- (4) Server Setup rows
rep('''     "Dodge rolls the way you move (standing still = back), in the air too. Vanilla numbers.", "custom:SkillKit"),
''', '''     "Dodge rolls the way you move (standing still = back), in the air too. Vanilla numbers.", "custom:SkillKit"),
    # 0.4.20 (Skyy LOCKED 2026-10-06 "Tap the sprint key"): the sprint-tap roll
    ("acro.dodgeTap", "Roll on sprint tap", "acrobatics", "bool", "true", "", "", "", "", "live",
     "Tap sprint: roll the way you move (still = back); hold: sprint. On ground only. Sprint must be hold.", "reload"),
    ("acro.dodgeTapMs", "Sprint tap window", "acrobatics", "int", "200", "50", "1000", "", "ms", "live,adv",
     "A sprint press shorter than this rolls; longer only sprints. At most one tap roll per 0.4 s.", "reload"),
''')
rep("""assert len(CFG_ROWS) == 203, (""", """assert len(CFG_ROWS) == 205, (""")
rep("""fromLevel; 0.4.18: + the read-only acro.roll; 0.4.19: + acro.dodgeMinMove, got %d" % len(CFG_ROWS))""",
    """fromLevel; 0.4.18: + the read-only acro.roll; 0.4.19: + acro.dodgeMinMove; 0.4.20: + acro.dodgeTap / acro.dodgeTapMs, got %d" % len(CFG_ROWS))""")
before('''assert sum(1 for _r in CFG_ROWS if _r[0] == "mana.classBase") == 1 and sum(1 for _r in CFG_ROWS if _r[0] == "spell.manaDivisor") == 1
''', '''# 0.4.20: the two tap rows right after acro.roll, row default = file default, once each; the comment line once, right before them
_k20 = [_r[0] for _r in CFG_ROWS]
assert _k20[_k20.index("acro.roll") + 1:_k20.index("acro.roll") + 3] == ["acro.dodgeTap", "acro.dodgeTapMs"]
assert _k20.count("acro.dodgeTap") == 1 and _k20.count("acro.dodgeTapMs") == 1
assert _dp.get("acro.dodgeTap") == "true" == [_r for _r in CFG_ROWS if _r[0] == "acro.dodgeTap"][0][4]
assert _dp.get("acro.dodgeTapMs") == "200" == [_r for _r in CFG_ROWS if _r[0] == "acro.dodgeTapMs"][0][4]
assert DEFAULTS.count(ACRO_GATE_MARK + "\\nacro.dodgeMinMove=2.0\\n" + ACRO_TAP_DOC + "\\nacro.dodgeTap=true\\nacro.dodgeTapMs=200\\n") == 1
''')

# ---------------------------------------------------------------------------------------------------------------- manifest text
rep(''' The dodge key rolls the way you move: 8 directions, standing still = a back roll (vanilla 2 Stamina, 0.25 s safe, works in the air).''',
    ''' A short tap of the sprint key (or the dodge key) rolls the way you move: 8 directions, standing still = a back roll (vanilla 2 Stamina, 0.25 s safe; the sprint tap on the ground only); holding sprint still sprints (Server Setup: Roll on sprint tap, Sprint tap window).''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands: 0.4.20 adds none"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
_ix = lambda t: s.index(t)
assert _ix('IMG = "com.hypixel') < _ix("public static boolean tap(double[] s,") < _ix("public static int startRoll(") < _ix("{PKG}.Acro.startRoll(store, cb, ref)")
assert (_ix("public static boolean tap(double[] s,") < _ix("public static void tapDone(") < _ix("public static void tapWatch(")
        < _ix("public static boolean rollFx(") < _ix("public static double stamina(") < _ix("public static int startRoll("))
assert _ix("public static boolean excludedState(") < _ix("public static boolean tapBlocked(") < _ix("public static boolean tap(double[] s,")
assert _ix("ACRO_TAP_DOC = ") < _ix("ACRO_DEFAULTS = ")
assert s.count("new double[304]") == 1 and "new double[296]" not in s and s.count("s[295]") >= 2
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.19 lines changed outside the planned places: %r" % _bad[:5]
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.19,", len(_gone), "0.4.19 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
