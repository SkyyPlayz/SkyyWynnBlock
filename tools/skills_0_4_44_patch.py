"""Derive SkyySkills/build_skyyskills_0.4.44.py from the GENERATED SkyySkills 0.4.43 (build_skyyskills_0.4.43.py = the tools/deploy_set.py SET
pin; 0.4.43 came from 0.4.42 by tools/skills_0_4_43_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.43 (nothing else changed); 0.4.43 stays untouched, its line endings are kept.
Run:  python tools/skills_0_4_44_patch.py   then   python SkyySkills/build_skyyskills_0.4.44.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.44.py

0.4.44 (2026-10-16) = THE ROLL GOES EVERY WAY + DODGE STYLES BY CLASS + PERFECT DODGE TUNING (lean round roll01).
  Skyy 2026-10-16: "okay. i was asking because rolling backwards still doesnt work. check how perfect dodges makes it work for them and
  copy it"; popups (question -> answer): "PERFECT DODGE: 50 ms window, x1.25 counter-hit for 0.75 s, +5 Acrobatics XP (max 50 XP / min,
  monster hits only)?" -> "100 ms now. 1,000 xp /min and doesn't have to hit a mob. (is the counter attack automatic?)"; "PERFECT DODGE:
  base roll for everyone (not an Acrobatics perk)?" -> "based on class steed/weight. heavy classes lunge, most classes roll, light fast
  classes like assassin and monk, and priest flip"; "PERFECT DODGE: how should a perfect dodge be shown?" -> "HUD flash + sound now";
  "PERFECT DODGE: when a hit is both a Perfect Parries counter and a dodge counter, only the parry multiplier applies (no stacking)?" ->
  "Stack them"; on XP caps: "raise cap. set caps absurdly high so we can find exploits. id like to remove the cap entirely later."
  (A) WHY BACK ROLLS NEVER WORKED: since 0.4.20 / 0.4.23 the roll is started BY THE SERVER on the rise of MovementStates.sprinting. The
  client only turns "sprinting" on while W is held (SkyyKeyProbe 0.2, 2026-10-10), so S / A / D + sprint sends the server nothing and no
  roll starts (side rolls only came from W+A / W+D). The 8-way chain itself (0.4.18's Dodge.json) was always right - it never ran.
  WHAT PERFECT DODGES DOES (narwhals, All Rights Reserved - read only, nothing copied): in its default mode it does not watch sprinting at
  all. It writes its own root interaction id into the player's Interactions COMPONENT under InteractionType.Dodge - the per-entity slot
  the engine asks FIRST when it resolves the root of an input (InteractionContext.getRootInteractionId: entity Interactions, then the held
  item, then the unarmed "Empty" set). With that slot filled, the CLIENT's own dodge input - which sits on the sprint key - fires
  InteractionType.Dodge itself in every direction, and the client answers the MovementCondition from the keys it holds (Back, BackLeft,
  ..., Failed = no key). Vanilla 0.7 leaves the slot empty (Unarmed/Interactions/Empty.json has no Dodge entry, no item has one), which
  is why the vanilla dodge looked "unbound". PD binds only when the slot is empty / the vanilla "Dodge" / the unarmed fallback, re-checks
  when the held item changes and takes its id out when the player leaves.
  OURS (own code, the same engine route): Acro.keyTick (AcroSys, world thread, once a second per player) puts this player's DODGE STYLE
  root into the Interactions slot InteractionType.Dodge (Acro.bindPlan: empty / one of OUR three roots -> set; already right -> nothing;
  another mod's root -> left alone + one WARN; off -> our root taken out). In that mode the 0.4.23 server sprint-press roll is OFF (tap()
  answers false) - the client's own dodge input does every roll, so a forward press never rolls twice. Row "Roll every direction"
  (acro.rollKey, default true); false = 0.4.43 exactly (server press, forward only, always the roll style). acro.dodgeTap=false turns
  sprint rolls off completely (slot out).
  (B) DODGE STYLES BY CLASS (class:<uuid> from SkyyClasses, read only, SkillClass.className): three roots, each Condition Flying false ->
  a named MovementCondition (8 directions, no key = back) -> per-direction named bodies (vanilla Dodge_Left body shape: Stamina 2,
  0.25 s i-frames Dodge_Invulnerability, Adventure Stamina spend + regen pause, VelocityConfig vanilla):
    roll  = root "Dodge" (0.4.18-0.4.43 unchanged): force 13, Roll / RollBackward / RollLeft / RollRight.
    lunge = root SkyySkills_Dodge_Lunge: force 10 (shorter), flat, the vanilla Dash animations (DashForward / DashBackward / DashLeft /
            DashRight, effects Dodge_Lunge_*).
    flip  = root SkyySkills_Dodge_Flip: force 13 with a small hop (Direction Y 0.5); back / back-diagonals = the vanilla Shortbow
            "Backflip", left / right = "SideflipLeft" / "SideflipRight" (an interaction step naming ItemPlayerAnimationsId Shortbow - the
            vanilla way abilities play another item's animation; the effect Dodge_Flip marks the flip for XP / perfect dodge); forward /
            forward-diagonals = the forward roll look (vanilla has no plain front flip outside the Battleaxe attack).
  Server Setup -> Acrobatics: "Dodge style: <class>" (choice roll / lunge / flip) for no class + the 8 classes. Defaults: Warrior,
  Berserker, Spellblade = lunge; Archer, Mage, no class = roll; Assassin, Monk, Priest = flip. A class switch rebinds within 1 s.
  Every style counts for roll XP, the level / tree push, the perfect dodge and the counter-hit (the new effects join the 4 roll effects in
  Acro.dodge, Acro.rollFx and PDodge.rollAge).
  (C) PERFECT DODGE: window 50 -> 100 ms; XP cap 50 -> 1,000,000 a minute (Skyy: absurdly high to find exploits); the XP is paid for ANY
  attacker entity (monsters AND players - 0.4.37 paid only for monsters); self-hits and environment damage (fall, fire, drowning,
  poison, no entity source, causes that bypass resistances) never count (unchanged). Ranching cap 200 -> 1,000,000 a minute. The
  counter-hit stays a damage bonus on your NEXT hit (not automatic). STACKS with Perfect Parries now: a hit that is also its counter
  (PP_Counterattack_Ready on the attacker) gets our x1.25 on top (0.4.37 skipped ours; PARRY_SKIP now counts the stacked hits).
  SHOWN: a HUD flash (SkyyHud bridge feed:fn:push, kind "dodge": "Perfect dodge! Next hit x1.25 +5 XP") + the 0.4.39 sound; the chat
  line is gone - it is only sent when the HUD answers no (no SkyyHud / Feed widget off), so a perfect dodge is never silent.
  MIGRATION Pd44Mig (PROJECT-RULES 4; RbCoinMig's reviewed machinery): ONCE on an EXISTING xp.properties (setup, after RbCoinMig, before
  SkillCfg.load): a one-line acro.perfectDodge.windowMs=50 -> 100, acro.perfectDodge.maxXpPerMinute=50 -> 1000000,
  ranching.maxXpPerMinute=200 -> 1000000; any other value kept (INFO); no line = nothing (the new code default applies - Skyy's live file
  has none of the three); config-history copy first, one config-changes.log line per change (Undo), marker comment at the end, file's
  own line ending, Properties check (only those keys).
  SAVED DATA: the Interactions component is saved with the player, so the style root stays in the player file. ROLLBACK to 0.4.43: first
  switch "Roll every direction" OFF in Server Setup and let every player log in once (it takes the slot out) - else a forward sprint
  press rolls twice on 0.4.43 (client + server press) and a lunge / flip slot names a root 0.4.43 does not ship (the dodge input does
  nothing). The migrated numbers stay (0.4.43 reads them). Removing SkyySkills entirely with "Dodge" left on the slot = the vanilla
  sideways dash on sprint + A / D (harmless).
  No new system or command.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.43.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.44.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.4.43"' in s and s.startswith('"""SkyySkills 0.4.43 - build script') and "ROLL_KEY" not in s, "not the generated 0.4.43 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.44 (2026-10-16)"):].rstrip() + "\n"
STYLE_CLASSES = ["none", "archer", "warrior", "assassin", "monk", "mage", "berserker", "priest", "spellblade"]
STYLE_DEFS = ["roll", "roll", "lunge", "flip", "flip", "roll", "lunge", "flip", "lunge"]
STYLE_LABEL = {"none": "no class"}

# ================================================================================================ docstring + version
rep('''"""SkyySkills 0.4.43 - build script (derived from the generated 0.4.42 by tools/skills_0_4_43_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.44 - build script (derived from the generated 0.4.43 by tools/skills_0_4_44_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.44.py.
0.4.43 was derived from the generated 0.4.42 by tools/skills_0_4_43_patch.py;
''')
rep('VERSION = "0.4.43"', 'VERSION = "0.4.44"')

# ================================================================================================ the engine type
rep('''ICH = "com.hypixel.hytale.server.core.entity.InteractionChain"
''', '''ICH = "com.hypixel.hytale.server.core.entity.InteractionChain"
ITS44 = "com.hypixel.hytale.server.core.modules.interaction.Interactions"   # 0.4.44: the per-entity root slots (InteractionType -> root id)
''')

# ================================================================================================ (C) perfect dodge / Ranching defaults
rep('''PD_ON_DEF, PD_WIN_DEF, PD_CTR_DEF, PD_MULT_DEF, PD_XP_DEF, PD_PM_DEF = "true", "50", "750", "1.25", "5", "50"
''', '''PD_ON_DEF, PD_WIN_DEF, PD_CTR_DEF, PD_MULT_DEF, PD_XP_DEF, PD_PM_DEF = "true", "100", "750", "1.25", "5", "1000000"   # 0.4.44: 50 -> 100 ms, 50 -> 1000000 a minute (Skyy)
''')
rep('''RANCH_PM_DEF = "200"
''', '''RANCH_PM_DEF = "1000000"   # 0.4.44: 200 -> 1000000 (Skyy: caps absurdly high to find exploits; Pd44Mig moves an untouched 200)
''')
rep('''         "# x acro.perfectDodge.counterMultiplier damage (1 = no counter-hit). The XP comes only from monsters' hits, at most",
         "# acro.perfectDodge.maxXpPerMinute a minute per player (0 = no cap); a hit the server would block anyway never counts.",''',
    '''         "# x acro.perfectDodge.counterMultiplier damage (1 = no counter-hit). The XP comes from any attacker's hit, at most",
         "# acro.perfectDodge.maxXpPerMinute a minute per player (0 = no cap); a hit the server would block anyway never counts.",''')
rep('''for _d37 in ("boolean ON = true", "long WINDOW_MS = 50L", "long COUNTER_MS = 750L", "double MULT = 1.25", "long XP = 5L", "long MAX_PM = 50L"):''',
    '''for _d37 in ("boolean ON = true", "long WINDOW_MS = 100L", "long COUNTER_MS = 750L", "double MULT = 1.25", "long XP = 5L", "long MAX_PM = 1000000L"):   # 0.4.44: 100 ms, 1000000 a minute''')
rep('''  WINDOW_MS = clampL(@PKG@.SkillCfg.lng(p, "acro.perfectDodge.windowMs", 50L), 0L, 250L);''',
    '''  WINDOW_MS = clampL(@PKG@.SkillCfg.lng(p, "acro.perfectDodge.windowMs", 100L), 0L, 250L);   // 0.4.44: 50 -> 100 (Skyy)''')
rep('''  MAX_PM = clampL(@PKG@.SkillCfg.lng(p, "acro.perfectDodge.maxXpPerMinute", 50L), 0L, 1000000000L);   // fix round: the XP cap''',
    '''  MAX_PM = clampL(@PKG@.SkillCfg.lng(p, "acro.perfectDodge.maxXpPerMinute", 1000000L), 0L, 1000000000L);   // fix round: the XP cap; 0.4.44: 50 -> 1000000''')
rep('''  long pm = @PKG@.SkillCfg.lng(p, "ranching.maxXpPerMinute", 200L);''',
    '''  long pm = @PKG@.SkillCfg.lng(p, "ranching.maxXpPerMinute", 1000000L);   // 0.4.44: 200 -> 1000000''')
rep('''     "Acrobatics XP for each perfect dodge of a monster's hit (once per roll).", "reload"),''',
    '''     "Acrobatics XP for each perfect dodge of any attacker's hit (once per roll).", "reload"),''')
rep(""" ms before a hit: no damage, +" + XP + " Acrobatics XP from monsters' hits" + (MAX_PM""",
    """ ms before a hit: no damage, +" + XP + " Acrobatics XP from any attacker's hit" + (MAX_PM""")
rep('''     "A roll right before a hit: no damage, Acrobatics XP (monsters' hits) and a stronger next hit.", "reload"),''',
    '''     "A dodge right before a hit: no damage, Acrobatics XP (any attacker) and a stronger next hit.", "reload"),''')
# any attacker entity pays the XP (self-hits / environment never reach perfect(): PDodgeSys needs an EntitySource that is not the player)
rep('''    @PKG@.PDodge.perfect(pr, st, r, System.currentTimeMillis(), !byPlayer);''',
    '''    @PKG@.PDodge.perfect(pr, st, r, System.currentTimeMillis(), true);   // 0.4.44 (Skyy "doesn't have to hit a mob"): any attacker pays the XP''')
# the counter-hit STACKS with Perfect Parries' counter (Skyy "Stack them")
rep('''    // fix round 2: no stacking with Perfect Parries (pack mod) - a hit that is its counterattack (PP_Counterattack_Ready on the attacker)
    // keeps only the parry's own multiplier; our counter-hit is used up by it
    try {
      if (@PKG@.PDodge.hasFx((@ECC@) buf.getComponent(att, @ECC@.getComponentType()), @PKG@.PDodge.PARRY_FX)) {
        @PKG@.PDodge.PARRY_SKIP.incrementAndGet();
        return;
      }
    } catch (Throwable pt) { }''', '''    // 0.4.44 (Skyy "Stack them"): a hit that is also Perfect Parries' counterattack (PP_Counterattack_Ready on the attacker) gets our
    // multiplier ON TOP of the parry's; PARRY_SKIP now counts those stacked hits
    try {
      if (@PKG@.PDodge.hasFx((@ECC@) buf.getComponent(att, @ECC@.getComponentType()), @PKG@.PDodge.PARRY_FX)) @PKG@.PDodge.PARRY_SKIP.incrementAndGet();
    } catch (Throwable pt) { }''')
# HUD flash instead of the chat line (the chat line only when the HUD says no)
rep('''# a perfect dodge of player pr (world thread, from PDodgeSys - the hit is already cancelled): one reward per roll - the counter-hit window,
''', '''# 0.4.44 (Skyy "HUD flash + sound now"): the HUD text of a perfect dodge (<= 48 characters, SkyyHud's feed limit)
pdg.addMethod(CtNewMethod.make(J14(r"""
public static String flashText(long xp) {
  String t = "Perfect dodge!";
  if (COUNTER_MS > 0L && MULT > 1.0) t = t + " Next hit x" + @PKG@.DivCfg.num(MULT);
  if (xp > 0L) t = t + " +" + xp + " XP";
  return t.length() > 48 ? t.substring(0, 48) : t;
}"""), pdg))
# the flash through SkyyHud's bridge feed:fn:push (kind "dodge"); TRUE = shown; FALSE (no SkyyHud / Feed widget off / no function) = not shown
pdg.addMethod(CtNewMethod.make(J14(r"""
public static boolean flash(java.util.UUID u, long xp) {
  try {
    Object f = @PKG@.SkillStore.bridge().get("feed:fn:push");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, "dodge", null, flashText(xp) });
    return Boolean.TRUE.equals(r);
  } catch (Throwable t) { return false; }
}"""), pdg))
# a perfect dodge of player pr (world thread, from PDodgeSys - the hit is already cancelled): one reward per roll - the counter-hit window,
''')
rep('''    s[2] = now;
    pr.sendMessage(@MSG@.raw(line(paid)).color("#9fd8ff"));''', '''    s[2] = now;
    if (!flash(u, paid)) pr.sendMessage(@MSG@.raw(line(paid)).color("#9fd8ff"));   // 0.4.44: the HUD flash; the chat line only when the HUD says no''')

# ================================================================================================ the default file: the 0.4.44 block
rep('''assert len(G43_KEYS) == len(set(G43_KEYS)) == 8
DEFAULTS = "\\n".join(L) + "\\n"
''', '''assert len(G43_KEYS) == len(set(G43_KEYS)) == 8
# 0.4.44 (tools/skills_0_4_44_patch.py): the roll goes every way (acro.rollKey) + the dodge style per class; a missing key reads the same
# code default. PD44_MARK = Pd44Mig's run-once marker (a fresh file is never migrated).
STYLE_CLASSES = ''' + repr(STYLE_CLASSES) + '''
STYLE_DEFS = ''' + repr(STYLE_DEFS) + '''
PD44_MARK_ID = "SkyySkills 0.4.44 perfect dodge 100 ms"
PD44_MARK = "# SkyySkills 0.4.44 perfect dodge 100 ms: window 100 ms, XP caps 1000000 a minute (old defaults 50 ms, 50, 200)."
assert "=" not in PD44_MARK and ":" in PD44_MARK and len(PD44_MARK) <= 140 and all(ord(_ch) < 128 for _ch in PD44_MARK)
G44_L = ["# ---------- Dodge roll input + dodge style (SkyySkills 0.4.44) ----------",
         "# Comments must stay on their own lines.",
         "# With acro.rollKey on, the sprint key dodges through the game's own dodge input: you dodge the way you move - forward, back,",
         "# sideways and diagonals (standing still = back). Off: the server watches for a sprint press instead (forward rolls only).",
         "# acro.dodgeTap false turns sprint dodges off either way.",
         "acro.rollKey=true",
         "# Dodge style per class (roll, lunge or flip); none = players without a class. Lunge = a shorter flat dash, flip = a hop with a",
         "# back or side flip. Every style keeps the perfect dodge."] + ["acro.dodgeStyle.%s=%s" % _sd for _sd in zip(STYLE_CLASSES, STYLE_DEFS)] + [PD44_MARK]
L.append("")
L.extend(G44_L)
G44_DEFAULTS = "\\n".join(G44_L) + "\\n"
assert all(ord(ch) < 128 for ch in G44_DEFAULTS) and '"' not in G44_DEFAULTS and "\\\\" not in G44_DEFAULTS and all(len(_ln) <= 140 for _ln in G44_L if _ln.startswith("#"))
assert not any(_cre.match(r"#\\s*[A-Za-z][A-Za-z0-9._-]*\\s*[=:]\\s*\\S+\\s*$", _ln) for _ln in G44_L), "a comment looks like a template line"
G44_KEYS = [_ln.split("=", 1)[0] for _ln in G44_L if not _ln.startswith("#")]
assert G44_KEYS == ["acro.rollKey"] + ["acro.dodgeStyle." + _c for _c in STYLE_CLASSES]
DEFAULTS = "\\n".join(L) + "\\n"
''')

# ================================================================================================ AcroCfg: ROLL_KEY + the styles
rep('''"double DODGE_MOVE = 2.0", "boolean TAP_ON = true", "long TAP_MS = 200L",''',
    '''"double DODGE_MOVE = 2.0", "boolean TAP_ON = true", "boolean ROLL_KEY = true", "long TAP_MS = 200L",''')
rep('''acfg.addField(CtField.make("public static final String DJ_DEFAULTS = " + DJ_LIT + ";", acfg))
''', '''acfg.addField(CtField.make("public static final String DJ_DEFAULTS = " + DJ_LIT + ";", acfg))
# 0.4.44: the dodge style per class (STYLE_CLASSES[0] = no class); STYLE = the live values (roll / lunge / flip)
acfg.addField(CtField.make("public static final String[] STYLE_CLASSES = new String[] { %s };" % ", ".join(json.dumps(_c) for _c in STYLE_CLASSES), acfg))
acfg.addField(CtField.make("public static final String[] STYLE_DEFS = new String[] { %s };" % ", ".join(json.dumps(_c) for _c in STYLE_DEFS), acfg))
acfg.addField(CtField.make("public static volatile String[] STYLE = new String[] { %s };" % ", ".join(json.dumps(_c) for _c in STYLE_DEFS), acfg))
acfg.addMethod(CtNewMethod.make("""
public static String[] readStyles(java.util.Properties p) {
  String[] n = new String[STYLE_CLASSES.length];
  for (int i = 0; i < n.length; i++) {
    String v = p.getProperty("acro.dodgeStyle." + STYLE_CLASSES[i]);
    v = v == null ? STYLE_DEFS[i] : v.trim().toLowerCase(java.util.Locale.ROOT);
    if (!"roll".equals(v) && !"lunge".equals(v) && !"flip".equals(v)) v = STYLE_DEFS[i];
    n[i] = v;
  }
  return n;
}""", acfg))
''')
rep('''  TAP_ON = {PKG}.SkillCfg.bool(p, "acro.dodgeTap", true);   // 0.4.23: a sprint PRESS rolls (0.4.20: a short tap; acro.dodgeTapMs is read but unused)
''', '''  TAP_ON = {PKG}.SkillCfg.bool(p, "acro.dodgeTap", true);   // 0.4.23: a sprint PRESS rolls (0.4.20: a short tap; acro.dodgeTapMs is read but unused)
  ROLL_KEY = {PKG}.SkillCfg.bool(p, "acro.rollKey", true);   // 0.4.44: the client's own dodge input dodges (every direction); false = 0.4.43's server press
  STYLE = readStyles(p);   // 0.4.44: acro.dodgeStyle.<class>
''')

# ================================================================================================ Acro: state 304 -> 308, the server press off in key mode
rep('''  double[] n = new double[304];   // 0.4.20: 296 -> 304 (the sprint-tap roll); 0.4.19: 292 -> 296 (the roll move gate)
''', '''  double[] n = new double[308];   // 0.4.44: 304 -> 308 (304 the last dodge-slot check ms, 305 its plan); 0.4.20: 296 -> 304 (the sprint-tap roll); 0.4.19: 292 -> 296 (the roll move gate)
''')
rep('''  if (!{PKG}.AcroCfg.TAP_ON || ms == null) {{
    s[296] = 0.0;
    return false;
  }}
  boolean ownRoll = rollOn || s[296] > 0.0;''', '''  if (!{PKG}.AcroCfg.TAP_ON || {PKG}.AcroCfg.ROLL_KEY || ms == null) {{   // 0.4.44: in key mode the client's dodge input rolls - no server press
    s[296] = 0.0;
    return false;
  }}
  boolean ownRoll = rollOn || s[296] > 0.0;''')

# ================================================================================================ Acro: the style effects count as a roll (XP, push, rollFx, PDodge.rollAge)
rep('''acro.addMethod(CtNewMethod.make(f"""
public static void dodge(double[] s, {ST} store, {CB} cb, {REF} ref, java.util.UUID u, long now, boolean creative, boolean excluded) {{
''', '''# 0.4.44: the lunge / flip effects (STYLE_FX_IDS) count like the 4 roll effects - roll XP + push (dodge), rollFx, PDodge.rollAge
acro.addField(CtField.make("public static final String[] STYLE_FX = new String[] { %s };" % ", ".join(json.dumps(_x) for _x in STYLE_FX_IDS), acro))
acro.addMethod(CtNewMethod.make(f"""
public static boolean isStyleFx(int x) {{
  if (x == Integer.MIN_VALUE || x < 0) return false;
  for (int k = 0; k < STYLE_FX.length; k++) {{
    if ({EFX}.getAssetMap().getIndex(STYLE_FX[k]) == x) return true;
  }}
  return false;
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static boolean styleFx({ECC} ecc) {{
  if (ecc == null) return false;
  for (int k = 0; k < STYLE_FX.length; k++) {{
    int i = {EFX}.getAssetMap().getIndex(STYLE_FX[k]);
    if (i != Integer.MIN_VALUE && ecc.hasEffect(i)) return true;
  }}
  return false;
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static void dodge(double[] s, {ST} store, {CB} cb, {REF} ref, java.util.UUID u, long now, boolean creative, boolean excluded) {{
''')
rep('''    if (bi != Integer.MIN_VALUE && ecc.hasEffect(bi)) on = true;
  }}
  if (on && s[6] < 0.5) {{''', '''    if (bi != Integer.MIN_VALUE && ecc.hasEffect(bi)) on = true;
    if (!on && styleFx(ecc)) on = true;   // 0.4.44: a lunge / flip
  }}
  if (on && s[6] < 0.5) {{''')
rep('''    String[] ids = new String[] {{ "Dodge_Left", "Dodge_Right", "Dodge_Forward", "Dodge_Back" }};''',
    '''    String[] ids = new String[] {{ "Dodge_Left", "Dodge_Right", "Dodge_Forward", "Dodge_Back" }};
    if (styleFx(ecc)) return true;   // 0.4.44: a lunge / flip''')
rep('''    if (x == Integer.MIN_VALUE || (x != li && x != ri && x != fi && x != bi)) continue;''',
    '''    if (x == Integer.MIN_VALUE || (x != li && x != ri && x != fi && x != bi && !@PKG@.Acro.isStyleFx(x))) continue;   // 0.4.44: + lunge / flip''')

# ================================================================================================ Acro: the dodge-input slot (style root, bindPlan / keyBind / keyTick)
rep('''# sliding XP cap (review fix): per-second ring, see the STATE layout above
''', '''# 0.4.44 (Skyy 2026-10-16 "check how perfect dodges makes it work for them and copy it" - learned, not copied): the player's Interactions
# component slot InteractionType.Dodge holds the root the engine (and the client) use for the dodge input FIRST
# (InteractionContext.getRootInteractionId). Filled with one of OUR dodge roots, the client's own dodge input on the sprint key fires in
# every direction and the client answers the MovementCondition from its keys. Vanilla leaves the slot empty.
# bindPlan (pure): want = the root this player should have (null = none): 0 nothing to do, 1 put want in (empty slot or another of OUR
# roots), 2 take our root out (want null), 3 another mod's root is there (left alone).
for c, m in ((ITS44, "getComponentType"), (ITS44, "getInteractionId"), (ITS44, "setInteractionId"), (ITS44, "removeInteractionId")):
    B.probe(pool, c, m)
acro.addField(CtField.make("public static boolean KEY_FOREIGN = false;", acro))   # 0.4.44: the other-mod WARN is logged once
acro.addField(CtField.make("public static boolean KEY_FAILED = false;", acro))    # 0.4.44: keyBind's WARN is logged once
acro.addField(CtField.make('public static final String KEY_ROOT = "Dodge";', acro))   # 0.4.44: the roll (the vanilla dodge root = our 8-way roll)
acro.addField(CtField.make("public static final String LUNGE_ROOT = %s;" % json.dumps(STYLE_ROOTS["lunge"]), acro))
acro.addField(CtField.make("public static final String FLIP_ROOT = %s;" % json.dumps(STYLE_ROOTS["flip"]), acro))
acro.addMethod(CtNewMethod.make("""
public static boolean ours(String id) {
  return id != null && (KEY_ROOT.equals(id) || LUNGE_ROOT.equals(id) || FLIP_ROOT.equals(id));
}""", acro))
acro.addMethod(CtNewMethod.make("""
public static int bindPlan(String cur, String want) {
  if (want != null) {
    if (cur == null) return 1;
    if (want.equals(cur)) return 0;
    if (ours(cur)) return 1;
    return 3;
  }
  if (ours(cur)) return 2;
  return 0;
}""", acro))
# the style of a class name (class:<uuid>; null / unknown = the "none" entry) and its root
acro.addMethod(CtNewMethod.make(f"""
public static String styleFor(String cls) {{
  String[] st = {PKG}.AcroCfg.STYLE;
  String[] cl = {PKG}.AcroCfg.STYLE_CLASSES;
  if (cls != null) {{
    String c = cls.trim();
    for (int i = 1; i < cl.length && i < st.length; i++) if (cl[i].equalsIgnoreCase(c)) return st[i];
  }}
  return st.length > 0 ? st[0] : "roll";
}}""", acro))
acro.addMethod(CtNewMethod.make("""
public static String styleRoot(String style) {
  if ("lunge".equals(style)) return LUNGE_ROOT;
  if ("flip".equals(style)) return FLIP_ROOT;
  return KEY_ROOT;
}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static int keyBind({ST} store, {CB} cb, {REF} ref, String want) {{
  try {{
    {ITS44} its = ({ITS44}) store.getComponent(ref, {ITS44}.getComponentType());
    String cur = its == null ? null : its.getInteractionId({ITY}.Dodge);
    int plan = bindPlan(cur, want);
    if (plan == 1) {{
      if (its == null) {{
        {ITS44} n = new {ITS44}();
        n.setInteractionId({ITY}.Dodge, want);
        cb.putComponent(ref, {ITS44}.getComponentType(), n);
      }} else its.setInteractionId({ITY}.Dodge, want);
    }} else if (plan == 2) {{
      its.removeInteractionId({ITY}.Dodge);
    }} else if (plan == 3 && !KEY_FOREIGN) {{
      KEY_FOREIGN = true;
      {PKG}.SkillCfg.warn("the dodge input already runs another mod's root '" + cur + "' - SkyySkills leaves it (logged once); its dodges replace ours");
    }}
    return plan;
  }} catch (Throwable t) {{
    if (!KEY_FAILED) {{ KEY_FAILED = true; {PKG}.SkillCfg.warn("the dodge input slot could not be set (logged once): " + t); }}
    return 9;
  }}
}}""", acro))
# once a second per player (s[304] the last check, s[305] its plan); wanted = acro.dodgeTap AND acro.rollKey; the root = the class's style
acro.addMethod(CtNewMethod.make(f"""
public static String wantRoot(java.util.UUID u) {{
  if (!{PKG}.AcroCfg.TAP_ON || !{PKG}.AcroCfg.ROLL_KEY) return null;
  return styleRoot(styleFor(u == null ? null : {PKG}.SkillClass.className(u)));
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static void keyTick(double[] s, {ST} store, {CB} cb, {REF} ref, java.util.UUID u, long now) {{
  if (s[304] > 0.0 && (double) now - s[304] < 1000.0) return;
  s[304] = (double) now;
  s[305] = (double) keyBind(store, cb, ref, wantRoot(u));
}}""", acro))
# sliding XP cap (review fix): per-second ring, see the STATE layout above
''')

# ================================================================================================ AcroSys: keyTick every tick (own 1 s clock)
rep('''    if ({PKG}.AcroCfg.TAP_ON) {{   // 0.4.23: a sprint PRESS starts the vanilla Dodge chain (the 8-way roll) at once - any game mode, acro.enabled or not
''', '''    {PKG}.Acro.keyTick(s, store, cb, ref, u, now);   // 0.4.44: the dodge input slot = this player's style root (own 1 s clock, own try)
    if ({PKG}.AcroCfg.TAP_ON) {{   // 0.4.23: a sprint PRESS starts the vanilla Dodge chain (the 8-way roll) at once - any game mode, acro.enabled or not
''')

# ================================================================================================ (B) the lunge / flip assets
rep('''assert "Stamina_Bar_Flash" in _dv_names and not [_i for _i in DODGE_FLAT if _i in _dv_names]
''', '''assert "Stamina_Bar_Flash" in _dv_names and not [_i for _i in DODGE_FLAT if _i in _dv_names]
# ================= 0.4.44 DODGE STYLES (Skyy 2026-10-16 "heavy classes lunge, most classes roll, light fast classes like assassin and monk,
# and priest flip"): two more roots beside the roll's "Dodge", each Condition Flying false -> a NAMED MovementCondition (8 directions, no
# key = back) -> named per-direction bodies = the roll body shape (the same condition, i-frames, Stamina spend) with their own look + push.
STYLE_ROOTS = {"roll": "Dodge", "lunge": "SkyySkills_Dodge_Lunge", "flip": "SkyySkills_Dodge_Flip"}
STYLE_LUNGE_FORCE, STYLE_FLIP_Y = 10, 0.5      # lunge: shorter + flat; flip: the roll's force with a small hop
STYLE_FX = [("Dodge_Lunge_Forward", "DashForward"), ("Dodge_Lunge_Back", "DashBackward"), ("Dodge_Lunge_Left", "DashLeft"), ("Dodge_Lunge_Right", "DashRight")]
STYLE_FX_IDS = [_f[0] for _f in STYLE_FX] + ["Dodge_Flip"]
STYLE_FLIP_ANIM = {"Back": "Backflip", "Left": "SideflipLeft", "Right": "SideflipRight"}   # vanilla Server/Item/Animations/Shortbow.json
_SD7 = 0.7071
STYLE_DIRS = [("Forward", 0, -1), ("ForwardLeft", -_SD7, -_SD7), ("ForwardRight", _SD7, -_SD7), ("Back", 0, 1), ("BackLeft", -_SD7, _SD7),
              ("BackRight", _SD7, _SD7), ("Left", -1, 0), ("Right", 1, 0)]
with zipfile.ZipFile(ASSETS) as _sz:
    _s_sb = json.loads(_sz.read("Server/Item/Animations/Shortbow.json").decode("utf-8-sig"))
_s_sba = _s_sb.get("Animations") or {}
if not all(isinstance(_s_sba.get(_a), dict) and _s_sba[_a].get("ThirdPerson") for _a in STYLE_FLIP_ANIM.values()):
    dodge_fail("the vanilla Shortbow animations %s are gone - the flip dodge needs a look" % sorted(STYLE_FLIP_ANIM.values()))
_dv_miss44 = [_a for _f, _a in STYLE_FX if not (_dv_sets.get(_a) or {}).get("Animations")]
if _dv_miss44:
    dodge_fail("Player.json has no animation set %s (the lunge)" % _dv_miss44)


def _style_group(k):
    return "Forward" if k.startswith("Forward") else ("Back" if k.startswith("Back") else k)
STYLE_FLAT = {}
for _g in ("Forward", "Back", "Left", "Right"):
    STYLE_FLAT["SkyySkills_Lunge_Look_" + _g] = dict(copy.deepcopy(DODGE_FLAT["SkyySkills_Roll_Look_Forward"]), EffectId="Dodge_Lunge_" + _g)
STYLE_FLAT["SkyySkills_Flip_Mark"] = dict(copy.deepcopy(DODGE_FLAT["SkyySkills_Roll_Look_Forward"]), EffectId="Dodge_Flip")
for _g, _a in sorted(STYLE_FLIP_ANIM.items()):
    STYLE_FLAT["SkyySkills_Flip_Anim_" + _g] = {"Type": "Simple", "Effects": {"ItemPlayerAnimationsId": "Shortbow", "ItemAnimationId": _a}}
for _sty in ("Lunge", "Flip"):
    _pick = {"Type": "MovementCondition"}
    for _k, _x, _z in STYLE_DIRS:
        _id = "SkyySkills_%s_%s" % (_sty, _k)
        _g = _style_group(_k)
        _push = copy.deepcopy(DODGE_FLAT["SkyySkills_Roll_Forward_Push"])
        if _sty == "Lunge":
            _look = ["SkyySkills_Lunge_Look_" + _g]
            _push["Direction"], _push["Force"] = {"X": _x, "Y": 0, "Z": _z}, STYLE_LUNGE_FORCE
        else:
            _look = ["SkyySkills_Roll_Look_Forward"] if _g == "Forward" else ["SkyySkills_Flip_Mark", "SkyySkills_Flip_Anim_" + _g]
            _push["Direction"] = {"X": _x, "Y": STYLE_FLIP_Y, "Z": _z}
        STYLE_FLAT[_id + "_Push"] = _push
        STYLE_FLAT[_id + "_Steps"] = dict(copy.deepcopy(DODGE_FLAT["SkyySkills_Roll_Forward_Steps"]), Interactions=[_DF_SAFE] + _look + [_id + "_Push", _DF_SPEND])
        STYLE_FLAT[_id] = dict(copy.deepcopy(DODGE_FLAT["SkyySkills_Roll_Forward"]), Next=_id + "_Steps")
        _pick[_k] = _id
    _pick["Failed"] = "SkyySkills_%s_Back" % _sty          # Skyy: standing still = back
    STYLE_FLAT["SkyySkills_Dodge_%s_Pick" % _sty] = _pick
    STYLE_FLAT["SkyySkills_Dodge_%s_Main" % _sty] = dict((_k2, _v2) for _k2, _v2 in _dv_main.items() if _k2 != "Next")
    STYLE_FLAT["SkyySkills_Dodge_%s_Main" % _sty]["Next"] = "SkyySkills_Dodge_%s_Pick" % _sty
assert STYLE_FLAT["SkyySkills_Dodge_Lunge_Main"] == {"Type": "Condition", "Flying": False, "Next": "SkyySkills_Dodge_Lunge_Pick"}
assert len(STYLE_FLAT) == 4 + 1 + 3 + 2 * (3 * 8 + 2) and not any(_dodge_has_inline(_v) for _v in STYLE_FLAT.values())
_s_clash = [_i for _i in list(STYLE_FLAT) + STYLE_FX_IDS + list(STYLE_ROOTS.values())[1:] if _i in _dv_names or _i in DODGE_FLAT]
if _s_clash:
    dodge_fail("the 0.4.44 style ids already exist: %s" % _s_clash)
for _fid in sorted(STYLE_FLAT):
    _dodge_put("Server/Item/Interactions/Dodge/%s.json" % _fid, STYLE_FLAT[_fid])
for _sty in ("lunge", "flip"):
    _dodge_put("Server/Item/RootInteractions/%s.json" % STYLE_ROOTS[_sty],
               dict(DODGE_ROOT, Interactions=["SkyySkills_Dodge_%s_Main" % _sty.capitalize()]))
for _fid, _anim in STYLE_FX:
    _e = copy.deepcopy(_dv_fx["Dodge_Left"])
    _e["ApplicationEffects"]["EntityAnimationId"] = _anim
    _dodge_put("Server/Entity/Effects/Movement/%s.json" % _fid, _e)
_dodge_put("Server/Entity/Effects/Movement/Dodge_Flip.json", {"Duration": _dv_fx["Dodge_Left"]["Duration"], "OverlapBehavior": "Extend"})
# every name a style file uses exists (ours or vanilla), every effect exists, every body keeps the roll's cost / i-frames / spend
_s_ints = set(os.path.basename(_p)[:-5] for _p in DODGE_FILES if _p.startswith("Server/Item/Interactions/")) | {"Stamina_Bar_Flash"}
for _fid, _fb in STYLE_FLAT.items():
    _names = [_v for _k2, _v in _fb.items() if _k2 in ("Next", "Failed", "Forward", "Back", "Left", "Right", "ForwardLeft", "ForwardRight", "BackLeft", "BackRight") and isinstance(_v, str)]
    _names += [_n for _n in (_fb.get("Interactions") or []) if isinstance(_n, str)]
    assert all(_n in _s_ints for _n in _names), (_fid, _names)
_s_fxs = set(os.path.basename(_p)[:-5] for _p in DODGE_FILES if _p.startswith("Server/Entity/Effects/")) | {"Dodge_Invulnerability"}
assert all(_e["EffectId"] in _s_fxs for _e in STYLE_FLAT.values() if _e["Type"] == "ApplyEffect")
assert all(STYLE_FLAT[_i]["Costs"] == {"Stamina": 2} for _i in STYLE_FLAT if STYLE_FLAT[_i]["Type"] == "StatsConditionWithModifier")
assert len(DODGE_FILES) == 31 + len(STYLE_FLAT) + 2 + len(STYLE_FX) + 1
DODGE_INT_IDS = DODGE_INT_IDS + sorted(STYLE_FLAT)
DODGE_FX_IDS = DODGE_FX_IDS + STYLE_FX_IDS
print("dodge styles (0.4.44): lunge (force %d, Dash animations) + flip (hop %.1f, Shortbow Backflip / Sideflip) = %d named files, 2 roots, %d effects"
      % (STYLE_LUNGE_FORCE, STYLE_FLIP_Y, len(STYLE_FLAT), len(STYLE_FX) + 1))
''')
rep('''"Server/Item/RootInteractions/Dodge.json")) for _p in DODGE_FILES)''',
    '''"Server/Item/RootInteractions/Dodge.json", "Server/Item/RootInteractions/SkyySkills_Dodge_")) for _p in DODGE_FILES)   # 0.4.44: + the style roots''')

# ================================================================================================ Server Setup rows (under the sprint-press rows)
_rows = ['''    # 0.4.44: the client's own dodge input dodges every way (off = 0.4.43's server press, forward only)
    ("acro.rollKey", "Roll every direction", "acrobatics", "bool", "true", "", "", "", "", "live",
     "On: sprint dodges the way you move - back, sideways too. Off: forward rolls only (old way).", "reload"),
''']
for _c, _d in zip(STYLE_CLASSES, STYLE_DEFS):
    _lab = STYLE_LABEL.get(_c, _c.capitalize())
    _rows.append('''    ("acro.dodgeStyle.%s", "Dodge style: %s", "acrobatics", "choice", "%s", "", "", "roll|Roll,lunge|Lunge,flip|Flip", "", "live",
     "How %s dodge: roll, lunge (short flat dash) or flip (hop + flip).", "reload"),
''' % (_c, _lab, _d, "players without a class" if _c == "none" else _c.capitalize() + "s"))
rep('''     "Not used since SkyySkills 0.4.23: the roll fires the moment you press sprint.", "reload"),
''', '''     "Not used since SkyySkills 0.4.23: the roll fires the moment you press sprint.", "reload"),
''' + "".join(_rows))
rep('''assert len(CFG_ROWS) == 261, ("0.4.43: + 9 rows''', '''assert len(CFG_ROWS) == 271, ("0.4.44: + acro.rollKey + 9 acro.dodgeStyle.*; 0.4.43: + 9 rows''')
rep('''"\\n" + G42_DEFAULTS + "\\n" + G43_DEFAULTS)   # 0.4.43: + G43;''', '''"\\n" + G42_DEFAULTS + "\\n" + G43_DEFAULTS + "\\n" + G44_DEFAULTS)   # 0.4.44: + G44; 0.4.43: + G43;''')
rep('''assert [_r[0] for _r in CFG_ROWS][-9:] == G43_KEYS + ["hp.regen.show"]
''', '''assert [_r[0] for _r in CFG_ROWS][-9:] == G43_KEYS + ["hp.regen.show"]
# 0.4.44: acro.rollKey + the 9 style rows once each, right after the two sprint-press rows, row default = the default file
_k44 = [_r[0] for _r in CFG_ROWS]
_i44 = _k44.index("acro.dodgeTapMs") + 1
assert _k44[_i44:_i44 + len(G44_KEYS)] == G44_KEYS and all(_k44.count(_k) == 1 for _k in G44_KEYS)
for _k in G44_KEYS:
    _r44 = [_r for _r in CFG_ROWS if _r[0] == _k][0]
    assert _r44[2] == "acrobatics" and ("\\n" + _k + "=" + _r44[4] + "\\n") in ("\\n" + G44_DEFAULTS) and _dp.get(_k) == _r44[4], _k
assert DEFAULTS.count(PD44_MARK_ID) == 1 and _dp.get("acro.perfectDodge.windowMs") == "100" and _dp.get("ranching.maxXpPerMinute") == "1000000"
''')

# ================================================================================================ Pd44Mig (the one-time defaults move)
rep('''rbcm = pool.makeClass(PKG + ".RbCoinMig")      # 0.4.38: the one-time rebirth.coinFactor 0.9 -> 0.8 update of an existing xp.properties
''', '''rbcm = pool.makeClass(PKG + ".RbCoinMig")      # 0.4.38: the one-time rebirth.coinFactor 0.9 -> 0.8 update of an existing xp.properties
pd44 = pool.makeClass(PKG + ".Pd44Mig")        # 0.4.44: the one-time perfect dodge 50 -> 100 ms + XP caps -> 1000000 update of an existing xp.properties
''')
rep('''# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs''', r'''# ---- Pd44Mig (0.4.44, PROJECT-RULES section 4; RbCoinMig's reviewed machinery, several keys): ONCE on an EXISTING xp.properties, setup()
# right after RbCoinMig.run, BEFORE SkillCfg.load. Nothing to do = no file or a comment line holding MARK_ID. Per key: when its LAST entry is
# a one-line entry holding exactly the old default, every such one-line entry -> the new default (value text only); any other value kept
# (INFO); NO line = nothing (the new code default applies). The marker goes at the end; config-history copy first; one config-changes.log
# line per change (Undo); Properties check (only those keys differ); atomicWrite. A failure = WARN, file untouched, retried next start.
pd44.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(PD44_MARK_ID), pd44))
pd44.addField(CtField.make("public static final String MARK = %s;" % json.dumps(PD44_MARK), pd44))
pd44.addField(CtField.make('public static final String[] KEYS = new String[] { "acro.perfectDodge.windowMs", "acro.perfectDodge.maxXpPerMinute", "ranching.maxXpPerMinute" };', pd44))
pd44.addField(CtField.make('public static final String[] OLDS = new String[] { "50", "50", "200" };', pd44))
pd44.addField(CtField.make('public static final String[] NEWS = new String[] { "100", "1000000", "1000000" };', pd44))
pd44.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.44";', pd44))
assert ("\n" + DEFAULTS).count("\nacro.perfectDodge.windowMs=100\n") == 1 and ("\n" + DEFAULTS).count("\nranching.maxXpPerMinute=1000000\n") == 1
pd44.addMethod(CtNewMethod.make(J14(r"""
public static int idx(String k) {
  if (k == null) return -1;
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(k)) return i;
  return -1;
}"""), pd44))
# pure text step. null = nothing to do; else { new text, String[] { key, old, new }* (the change-log rows), boolean[] migrated, String kept }
pd44.addMethod(CtNewMethod.make(J14(r"""
public static Object[] plan(String text) {
  if (text == null) return null;
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  String[] eff = new String[KEYS.length];
  boolean[] multi = new boolean[KEYS.length];
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    int x = idx(@PKG@.CfgFile.key(s));
    if (x >= 0) { eff[x] = @PKG@.CfgFile.value(l, k).trim(); multi[x] = e > k; }
    k = e + 1;
  }
  boolean[] mig = new boolean[KEYS.length];
  StringBuilder kept = new StringBuilder();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < KEYS.length; i++) {
    mig[i] = eff[i] != null && !multi[i] && eff[i].equals(OLDS[i]);
    if (mig[i]) { rows.add(KEYS[i]); rows.add(OLDS[i]); rows.add(NEWS[i]); }
    else if (eff[i] != null) kept.append(kept.length() > 0 ? "; " : "").append(KEYS[i] + "=" + @PKG@.CfgRows.oneLine(p.getProperty(KEYS[i])) + " kept (an admin's value) - the 0.4.44 default is " + NEWS[i]);
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    int x2 = idx(@PKG@.CfgFile.key(s2));
    if (x2 >= 0 && mig[x2] && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(OLDS[x2])) {
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + NEWS[x2] + (raw[k].endsWith("\r") ? "\r" : ""));
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + 256);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  String body = sb.toString();
  String nl = cr + "\n";
  String pre = (body.length() == 0 || body.endsWith("\n")) ? "" : nl;
  String last = body.endsWith("\n") ? body.substring(0, body.length() - 1) : body;
  if (last.endsWith("\r")) last = last.substring(0, last.length() - 1);
  int bs = 0;
  for (int i = last.length() - 1; i >= 0 && last.charAt(i) == '\\'; i--) bs++;
  if (bs % 2 == 1) pre = pre + nl;
  body = body + pre + MARK + nl;
  String[] ra = new String[rows.size()];
  for (int i = 0; i < ra.length; i++) ra[i] = (String) rows.get(i);
  return new Object[] { body, ra, mig, kept.toString() };
}"""), pd44))
# only the migrated keys may differ (exactly their new value); nothing added or removed
pd44.addMethod(CtNewMethod.make(J14(r"""
public static boolean sameAfter(byte[] old, byte[] nb, boolean[] mig) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties n = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    n.load(new java.io.ByteArrayInputStream(nb));
    if (n.size() != a.size()) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String want = a.getProperty(k);
      int x = idx(k);
      if (x >= 0 && mig[x]) want = NEWS[x];
      String got = n.getProperty(k);
      if (got == null || !got.equals(want)) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}"""), pd44))
pd44.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    boolean[] mig = (boolean[]) r[2];
    if (!sameAfter(old, data, mig)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.44 (perfect dodge 100 ms, XP caps): the update would change another setting (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = @PKG@.HealMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.HealMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.44 perfect dodge / XP cap update");
    if (!@PKG@.HealMig.mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.44 (perfect dodge 100 ms, XP caps): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[1];
    StringBuilder ch = new StringBuilder();
    for (int i = 0; i + 2 < rows.length; i += 3) {
      @PKG@.CfgLog.enqueue(@PKG@.RbCoinMig.logLine(rows[i], rows[i + 1], rows[i + 2]).replace(@PKG@.RbCoinMig.WHO, WHO));
      ch.append(ch.length() > 0 ? ", " : "").append(rows[i] + " " + rows[i + 1] + " -> " + rows[i + 2]);
    }
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String msg = "xp.properties updated for 0.4.44: " + (ch.length() > 0 ? ch.toString() + " (Server Setup -> Changes -> Undo)" : "no setting changed - 0.4.44 marker added") + " - the old file is in config-history";
    @PKG@.SkillCfg.info(msg);
    String kept = (String) r[3];
    if (kept.length() > 0) { @PKG@.SkillCfg.info(kept); return msg + "\n" + kept; }
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update xp.properties for 0.4.44 (perfect dodge 100 ms, XP caps; the file is used as it is): " + t);
    return "";
  }
}"""), pd44))

# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs''')
rep('''  {PKG}.RbCoinMig.run();      // 0.4.38: untouched rebirth.coinFactor 0.9 (or no line) -> 0.8 in an existing xp.properties, once; History first
''', '''  {PKG}.RbCoinMig.run();      // 0.4.38: untouched rebirth.coinFactor 0.9 (or no line) -> 0.8 in an existing xp.properties, once; History first
  {PKG}.Pd44Mig.run();        // 0.4.44: untouched perfect dodge 50 ms / caps 50 / 200 -> 100 ms / 1000000, once; History first
''')
rep('''          rbcm, snd39, rbs39,
''', '''          rbcm, snd39, rbs39, pd44,
''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "command / system registrations changed"
_i = s.index
assert _i("public static boolean isStyleFx(int x)") < _i("public static boolean styleFx(") < _i("public static void dodge(double[] s, {ST} store")
assert _i("public static boolean ours(String id)") < _i("public static int bindPlan(String cur, String want)") < _i("public static String styleFor(") \
    < _i("public static String styleRoot(") < _i("public static int keyBind(") < _i("public static String wantRoot(") < _i("public static void keyTick(") \
    < _i("{PKG}.Acro.keyTick(s, store, cb, ref, u, now);")
assert _i("public static boolean tap(double[] s, {MVT} ms") < _i("{PKG}.AcroCfg.ROLL_KEY || ms == null")
assert _i("STYLE_FX_IDS = [") < _i('acro.addField(CtField.make("public static final String[] STYLE_FX')
assert _i("public static String[] readStyles(") < _i("  STYLE = readStyles(p);")
assert _i("public static boolean flash(java.util.UUID u, long xp)") < _i("if (!flash(u, paid))")
assert _i("STYLE_ROOTS = {") < _i("json.dumps(STYLE_ROOTS[\"lunge\"])")
assert _i("public static Object[] plan(String text) {\n  if (text == null) return null;\n  java.util.Properties p = new java.util.Properties();\n  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }\n  String[] raw = text.split(\"\\n\", -1);\n  java.util.ArrayList l = new java.util.ArrayList();\n  for (int i = 0; i < raw.length; i++) {\n    String s0 = raw[i];\n    if (s0.endsWith(\"\\r\")) s0 = s0.substring(0, s0.length() - 1);\n    l.add(s0);\n  }\n  String[] eff") > 0
assert s.count("{PKG}.Acro.keyTick(") == 1 and s.count("its.setInteractionId(") == 1
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.4.43 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", dst, "(%d lines; 0.4.43 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
