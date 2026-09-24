"""Derive SkyySkills/build_skyyskills_0.2.py from 0.1 (same style as acc_0_2_patch.py: rep(old, new) with asserted anchors;
the CRLF/LF line endings of the 0.1 script are preserved).
0.2: ACROBATICS (mcMMO style), the 5th skill. Skyy: "you gain xp for it by running, jumping, and falling. as you level it up you slowly
gain more movement speed, jump height, and reduced fall damage. (if we add a dodge, that would also boost acrobatics, and your dodge
distance and speed would increase as it is leveled.)"
 - XP (AcroSys = EntityTickingSystem on Player entities, world thread; pattern: SkyyAccessories AccEffects + MMOSkillTree
   MovementXpTickingSystem, whose velocity-based distance was NOT copied - Velocity.getX() is the server-side velocity, the client's
   motion lives in clientVelocity - we measure TransformComponent.getPosition() deltas instead, with a teleport guard):
     running  = blocks moved on the ground x acro.sprint/walk/runXpPerBlock (MovementStates sprinting / walking|crouching / any other
                input-driven move; horizontalIdle or idle = pushed by something else = 0)
     jumping  = MovementStates.jumping false->true edge, acro.jumpCooldownMs between paid jumps and acro.jumpMinMove blocks travelled
                since the last paid jump (no XP for jumping in place)
     falling  = own peak-Y tracking while airborne (the engine's currentFallDistance also grows on teleports - LivingEntity.moveTo,
                called by TeleportSystems.completeTeleport); a drop >= acro.fallMinBlocks pays per block, a fall that produced a FALL
                Damage event pays per point of the UNREDUCED damage instead (Damage.getInitialAmount), only if the player is still
                alive 0.4 s later. Landing in water / while gliding / climbing / mantling pays nothing.
     dodge    = the VANILLA dodge exists (Server/Item/RootInteractions/Dodge.json, InteractionType.Dodge: strafe left/right +
                dodge input -> StatsConditionWithModifier -> ApplyEffect Dodge_Invulnerability + Dodge_Left|Right (0.25 s) ->
                ApplyForce 13 Set). ApplyEffectInteraction.firstRun runs on the SERVER, so a rising edge of
                EffectControllerComponent.hasEffect(Dodge_Left|Dodge_Right) = one dodge -> acro.dodgeXp.
     anti-exploit: no XP (run, jump, fall AND dodge - one shared Acro.excludedState) while mounted / flying / gliding /
                climbing / swimming / in fluid / sitting / sleeping / mantling, none in creative (creativeXp); no dodge push in
                those states either; a tick move > acro.teleportBlocks or faster than acro.maxSpeed pays nothing and cancels the
                fall in progress; world change resets the tracker; ALL Acrobatics XP together is capped at acro.maxXpPerMinute in
                ANY 60 s (sliding per-second ring); the chat line is throttled to acro.feedbackMs (running would otherwise print
                every 2 s).
 - Review fixes (2026-09-23): dodge()/boost() now honour the excluded movement states; paid fall-damage notes are cleared so an old
   timestamp cannot swallow the next safe landing; sliding XP cap instead of a fixed minute; acro.speedPerLevel /
   acro.jumpBlocksPerLevel reject negative / NaN like every other rate; MoveSync (tools/skyymove.py) logs the pause once PER PLAYER
   and names the known non-Skyy mods that write MovementSettings directly (see its OUTSIDE THE PROTOCOL section).
 - Bonuses (per level, linear, every acro.* key in xp.properties; Skyy's targets from HANDOFF: +1 % vanilla speed, +0.015 blocks
   jump height, -0.5 % fall damage per level) go through the SHARED SKYY MOVEMENT PROTOCOL (tools/skyymove.py, also used by
   SkyyAccessories 0.3): source "skills.acrobatics", layer "flat". Speed/jump are applied by MoveSync.sync (MovementSettings
   baseSpeed/jumpForce from the defaults, idempotent, several appliers agree). Fall damage: AcroFallSys = DamageEventSystem in
   DamageModule.getFilterDamageGroup() (vanilla DamageSystems$ArmorDamageReduction pattern; ApplyDamage runs AFTER Filter) scales
   Damage.setAmount by the summed fallDamage multiplier of ALL sources - SkyySkills claims the single fall-damage applier role
   (bridge putIfAbsent "stat:owner:fallDamage"). Dodge boost: on each detected dodge an extra push of acro.dodgeForce x
   min(acro.dodgeBoostMax, level x acro.dodgeBoostPerLevel) along the client's horizontal velocity, 100 ms after the Dodge effect
   appears (so it follows the dodge's own ApplyForce Set instruction instead of being overwritten by it; only while the effect lasts), via
   Velocity.addInstruction(vec, null, ChangeVelocityType.Add) - the vanilla LaunchPadInteraction / knockback path that
   PlayerVelocityInstructionSystem sends to the client as a ChangeVelocity packet (longer AND faster dodge).
 - Data: the player data array is now long[2*N] (xp[0..N-1], paid[N..2N-1]); old files simply lack Acrobatics / Acrobatics.paid
   (-> 0 XP, paid = level 0). Every hard-coded 4/8 of 0.1 (paid offset, leaderboard caches) now uses SkillDefs.N. Existing
   xp.properties files get the acro.* section appended once (defaults are used either way). Bridge skill:<uuid> includes
   Acrobatics; level-up coins as for every skill. /skills page: Acrobatics row shows the current bonuses (set via #SkyySkBonus.Text).
Run:  python tools/skills_0_2_patch.py   then   python SkyySkills/build_skyyskills_0.2.py   (never --deploy from an agent)
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.1.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.2.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.1"
s = raw.decode("utf8").replace("\r\n", "\n")

def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    if count == 1:
        assert s.count(old) == 1, "anchor not unique: " + old[:80]
    else:
        assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)

# ---------------------------------------------------------------- header / version
rep('"""SkyySkills 0.1 - build script (javassist via jpype). Hypixel-SkyBlock-style skills: Mining, Foraging, Farming, Combat.\n'
    'Run:   python build_skyyskills_0.1.py            -> SkyySkills/SkyySkills-0.1.jar\n'
    '       python build_skyyskills_0.1.py --deploy   -> also copies to Mods/SkyySkills.jar and enables it in the HUD mod world\n',
'''"""SkyySkills 0.2 - build script (derived from 0.1 by tools/skills_0_2_patch.py - edit the patch, not this file)
Run:   python build_skyyskills_0.2.py            -> SkyySkills/SkyySkills-0.2.jar
       python build_skyyskills_0.2.py --deploy   -> also copies to Mods/SkyySkills.jar and enables it in the HUD mod world
       DEPLOY TOGETHER WITH SkyyAccessories 0.3 (0.2's speed talisman does not speak the movement protocol and would fight Acrobatics)
0.2: ACROBATICS (mcMMO style) as the 5th skill: XP for running (per block, sprint > run > walk), jumping (edge + cooldown + must have
     moved), falling (drop height, or unreduced fall damage survived) and the vanilla dodge (Dodge_Left/Right effect edge); bonuses
     per level: movement speed, jump height, less fall damage, a longer/faster dodge. All rates and bonuses are acro.* keys in
     xp.properties. Anti-exploit: teleport/launch guard, world-change reset, no XP (dodges included) and no dodge push while
     mounted/flying/gliding/climbing/swimming/in fluid/sitting/sleeping/mantling, no XP in creative, no XP for jumping in place,
     cap on all Acrobatics XP in any 60 s (sliding).
     SHARED SKYY MOVEMENT PROTOCOL v1 (tools/skyymove.py has the full spec; SkyyAccessories 0.3 implements the same code):
       bridge "move:<uuid>" -> ConcurrentHashMap source -> Map{layer "flat"|"pct", speed, jump, fallDamage}; each mod posts ONLY its
       own source ("skills.acrobatics" = flat) and every applier sets baseSpeed = default x clamp((1+sum flat)(1+sum pct), 0.3, 5),
       jump height = (h0 + sum flat blocks)(1 + sum pct) -> jumpForce = sqrt(2 g h); fall damage x clamp((1+flat)(1+pct), 0, 2)
       applied ONLY by the owner of "stat:owner:fallDamage" (putIfAbsent; SkyySkills). Idempotent, so several appliers agree;
       5-strike pause only against writers outside the protocol (logged once per player); nothing written while mounted.
       Non-Skyy mods that write MovementSettings directly are NOT coordinated (they win for the player they reset): do not enable
       them in a SkyWynn world; the known ones are named in the server log on the first sync (skyymove.KNOWN_WRITERS).
     Fall reduction = DamageEventSystem in the Filter damage group (runs before ApplyDamage). Dodge boost = Velocity.addInstruction Add.
     Player data array long[2*N]; old player files load with Acrobatics 0. Page: Acrobatics row shows the current bonuses.
0.1 notes:
SkyySkills 0.1 - build script (javassist via jpype). Hypixel-SkyBlock-style skills: Mining, Foraging, Farming, Combat.
''')
rep('VERSION = "0.1"', 'VERSION = "0.2"')
rep('import skyybuild as B\n', 'import skyybuild as B\nimport skyymove as MV   # shared Skyy movement protocol (MoveSync class source; also used by SkyyAccessories 0.3)\n')

# ---------------------------------------------------------------- engine classes + probes
rep('BTM = "com.hypixel.hytale.assetstore.map.BlockTypeAssetMap"\n',
'''BTM = "com.hypixel.hytale.assetstore.map.BlockTypeAssetMap"
# 0.2 Acrobatics API (verified with reflect.py / bcfull.py against HytaleServer.jar, see tools/skills_0_2_patch.py)
ETS = "com.hypixel.hytale.component.system.tick.EntityTickingSystem"
MSC = "com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent"
MVT = "com.hypixel.hytale.protocol.MovementStates"
TRC = "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent"
V3D = "org.joml.Vector3d"
VEL = "com.hypixel.hytale.server.core.modules.physics.component.Velocity"
VCF = "com.hypixel.hytale.server.core.modules.splitvelocity.VelocityConfig"
CVT = "com.hypixel.hytale.protocol.ChangeVelocityType"
ECC = "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent"
EFX = "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect"
DCS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageCause"
DEVS= "com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem"
DMM = "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule"
SYG = "com.hypixel.hytale.component.SystemGroup"
''')
rep('''             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)
''', '''             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)
for c, m in ((ETS, "tick"), (MSC, "getComponentType"), (MSC, "getMovementStates"), (MVT, "jumping"), (MVT, "onGround"), (MVT, "sprinting"),
             (MVT, "running"), (MVT, "walking"), (MVT, "horizontalIdle"), (MVT, "idle"), (MVT, "crouching"), (MVT, "sliding"), (MVT, "mounting"), (MVT, "flying"), (MVT, "gliding"),
             (MVT, "climbing"), (MVT, "inFluid"), (MVT, "swimming"), (MVT, "sitting"), (MVT, "sleeping"), (MVT, "mantling"),
             (TRC, "getComponentType"), (TRC, "getPosition"), (V3D, "x"), (V3D, "y"), (V3D, "z"),
             (VEL, "getComponentType"), (VEL, "getClientVelocity"), (VEL, "addInstruction"), (CVT, "Add"),
             (ECC, "getComponentType"), (ECC, "hasEffect"), (EFX, "getAssetMap"), ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getIndex"),
             (DMG, "getCause"), (DMG, "getAmount"), (DMG, "setAmount"), (DMG, "getInitialAmount"), (DCS, "FALL"), (DCS, "getId"),
             (DMM, "get"), (DMM, "getFilterDamageGroup"), (ESV, "get"), (PLA, "isWaitingForClientReady"), (CB, "getComponent"),
             ("com.hypixel.hytale.component.system.ISystem", "getGroup")):
    B.probe(pool, c, m)
MV.probe(B, pool)
''')

# ---------------------------------------------------------------- icons + defaults
rep('ICONS = ["Tool_Pickaxe_Iron", "Tool_Hatchet_Iron", "Tool_Hoe_Iron", "Weapon_Sword_Iron"]',
    'ICONS = ["Tool_Pickaxe_Iron", "Tool_Hatchet_Iron", "Tool_Hoe_Iron", "Weapon_Sword_Iron", "Armor_Leather_Light_Legs"]')
rep('''L.append("prefix.%s=Farming:2" % must_prefix("Plant_Cactus"))
DEFAULTS = "\\n".join(L) + "\\n"
''', '''L.append("prefix.%s=Farming:2" % must_prefix("Plant_Cactus"))
# 0.2: Acrobatics - also appended once to an existing xp.properties that has no acro.* key (AcroCfg.ensureDefaults)
ACRO_L = []
ACRO_L.append("# ---------- Acrobatics (run, jump, fall, dodge) - SkyySkills 0.2 ----------")
ACRO_L.append("# Comments must stay on their own lines (a # after a value becomes part of the value).")
ACRO_L.append("# acro.enabled=false turns off Acrobatics XP AND its movement bonuses.")
ACRO_L.append("acro.enabled=true")
ACRO_L.append("# XP per block moved on the ground (sprint / run / walk or sneak), measured from the server position. A move of more than")
ACRO_L.append("# acro.teleportBlocks in one tick or faster than acro.maxSpeed blocks per second (teleport, launch, lag burst) pays nothing.")
ACRO_L.append("# No Acrobatics XP (running, jumping, falling or dodging) and no dodge push while mounted, flying, gliding, climbing,")
ACRO_L.append("# swimming, in fluid, sitting, sleeping or mantling; no Acrobatics XP in creative (see creativeXp).")
ACRO_L.append("acro.sprintXpPerBlock=0.25")
ACRO_L.append("acro.runXpPerBlock=0.15")
ACRO_L.append("acro.walkXpPerBlock=0.05")
ACRO_L.append("acro.maxSpeed=30")
ACRO_L.append("acro.teleportBlocks=8")
ACRO_L.append("# Jumps: acro.jumpXp per jump, at most one paid jump per acro.jumpCooldownMs, and only after moving acro.jumpMinMove blocks")
ACRO_L.append("# since the last paid jump (jumping in place pays nothing).")
ACRO_L.append("acro.jumpXp=2")
ACRO_L.append("acro.jumpCooldownMs=800")
ACRO_L.append("acro.jumpMinMove=2.0")
ACRO_L.append("# Falls: landing after a drop of at least acro.fallMinBlocks pays acro.fallXpPerBlock per block from there on; a fall that hurt")
ACRO_L.append("# pays acro.fallDamageXp per point of fall damage (before the Acrobatics reduction) instead, only if you survived it.")
ACRO_L.append("# One landing pays at most acro.fallXpMax. Landing in water pays nothing.")
ACRO_L.append("acro.fallMinBlocks=4")
ACRO_L.append("acro.fallXpPerBlock=2")
ACRO_L.append("acro.fallDamageXp=2")
ACRO_L.append("acro.fallXpMax=50")
ACRO_L.append("# Dodge (the vanilla strafe left/right dodge): XP per dodge, at most one per acro.dodgeCooldownMs.")
ACRO_L.append("acro.dodgeXp=3")
ACRO_L.append("acro.dodgeCooldownMs=400")
ACRO_L.append("# All Acrobatics XP together pays at most this much in ANY 60 seconds (sliding window; movement is easy to macro).")
ACRO_L.append("acro.maxXpPerMinute=240")
ACRO_L.append("# The +Acrobatics XP chat line shows at most once per this many ms (level ups always show; /skills quiet hides it).")
ACRO_L.append("acro.feedbackMs=30000")
ACRO_L.append("# Bonuses per Acrobatics level (linear). speedPerLevel = fraction of vanilla speed (0.01 = +1% per level);")
ACRO_L.append("# jumpBlocksPerLevel = extra jump height in blocks; fallReductionPerLevel = less fall damage per level, capped at fallReductionMax.")
ACRO_L.append("acro.speedPerLevel=0.01")
ACRO_L.append("acro.jumpBlocksPerLevel=0.015")
ACRO_L.append("acro.fallReductionPerLevel=0.005")
ACRO_L.append("acro.fallReductionMax=0.8")
ACRO_L.append("# Dodge boost: every dodge gets an extra push of dodgeForce x (level x dodgeBoostPerLevel, at most dodgeBoostMax) in the")
ACRO_L.append("# direction you are moving (the vanilla dodge force is 13). acro.dodgeBoost=false turns the push off (dodge XP stays).")
ACRO_L.append("acro.dodgeBoost=true")
ACRO_L.append("acro.dodgeForce=13")
ACRO_L.append("acro.dodgeBoostPerLevel=0.004")
ACRO_L.append("acro.dodgeBoostMax=0.5")
L.append("")
L.extend(ACRO_L)
ACRO_DEFAULTS = "\\n".join(ACRO_L) + "\\n"
assert all(ord(ch) < 128 for ch in ACRO_DEFAULTS)
ACRO_LIT = json.dumps(ACRO_DEFAULTS)
DEFAULTS = "\\n".join(L) + "\\n"
''')

# ---------------------------------------------------------------- new classes
rep('pl   = pool.makeClass(PKG + ".SkyySkillsPlugin", pool.get(JP))\n',
'''pl   = pool.makeClass(PKG + ".SkyySkillsPlugin", pool.get(JP))
acfg = pool.makeClass(PKG + ".AcroCfg")
mvs_ = pool.makeClass(PKG + ".MoveSync")
acro = pool.makeClass(PKG + ".Acro")
asy  = pool.makeClass(PKG + ".AcroSys", pool.get(ETS))
afs  = pool.makeClass(PKG + ".AcroFallSys", pool.get(DEVS))
''')

# ---------------------------------------------------------------- SkillDefs: 5th skill
rep('''defs.addField(CtField.make('public static final String[] NAMES = new String[] { "Mining", "Foraging", "Farming", "Combat" };', defs))''',
    '''defs.addField(CtField.make('public static final String[] NAMES = new String[] { "Mining", "Foraging", "Farming", "Combat", "Acrobatics" };', defs))''')
rep('''defs.addField(CtField.make('public static final String[] COLORS = new String[] { "#8fc8ff", "#8fe08a", "#f0d060", "#ff8a7a" };', defs))''',
    '''defs.addField(CtField.make('public static final String[] COLORS = new String[] { "#8fc8ff", "#8fe08a", "#f0d060", "#ff8a7a", "#c8a0ff" };', defs))''')
rep('defs.addField(CtField.make("public static final int N = 4;", defs))', 'defs.addField(CtField.make("public static final int N = 5;", defs))')
rep('defs.addField(CtField.make("public static final int COMBAT = 3;", defs))\n',
    'defs.addField(CtField.make("public static final int COMBAT = 3;", defs))\ndefs.addField(CtField.make("public static final int ACROBATICS = 4;", defs))\n')
# block rules can never pay Combat or Acrobatics
rep('  if (sk < 0 || sk == {PKG}.SkillDefs.COMBAT) return null;',
    '  if (sk < 0 || sk == {PKG}.SkillDefs.COMBAT || sk == {PKG}.SkillDefs.ACROBATICS) return null;')

# ---------------------------------------------------------------- AcroCfg (before SkillCfg.load, which calls it)
rep('cfg.addMethod(CtNewMethod.make(f"""\npublic static synchronized String load() {{',
'''# ================= AcroCfg: acro.* keys of xp.properties (0.2) =================
acfg.addField(CtField.make("public static final String DEFAULTS = " + ACRO_LIT + ";", acfg))
for _decl in ("boolean ENABLED = true", "double SPRINT = 0.25", "double RUN = 0.15", "double WALK = 0.05", "double MAX_SPEED = 30.0",
              "double TELEPORT = 8.0", "double JUMP_XP = 2.0", "long JUMP_CD = 800L", "double JUMP_MOVE = 2.0", "double FALL_MIN = 4.0",
              "double FALL_XP = 2.0", "double FALL_DMG_XP = 2.0", "double FALL_MAX = 50.0", "double DODGE_XP = 3.0", "long DODGE_CD = 400L",
              "double MAX_PER_MIN = 240.0", "long FEEDBACK_MS = 30000L", "double SPEED_PER_LVL = 0.01", "double JUMP_PER_LVL = 0.015",
              "double FALL_PER_LVL = 0.005", "double FALL_RED_MAX = 0.8", "boolean DODGE_BOOST = true", "double DODGE_FORCE = 13.0",
              "double DODGE_PER_LVL = 0.004", "double DODGE_MAX = 0.5"):
    acfg.addField(CtField.make("public static volatile %s;" % _decl, acfg))
acfg.addMethod(CtNewMethod.make("""
public static double nn(double v) {
  if (Double.isNaN(v) || v < 0.0) return 0.0;
  return v;
}""", acfg))
acfg.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ENABLED = {PKG}.SkillCfg.bool(p, "acro.enabled", true);
  SPRINT = nn({PKG}.SkillCfg.dbl(p, "acro.sprintXpPerBlock", 0.25));
  RUN = nn({PKG}.SkillCfg.dbl(p, "acro.runXpPerBlock", 0.15));
  WALK = nn({PKG}.SkillCfg.dbl(p, "acro.walkXpPerBlock", 0.05));
  MAX_SPEED = Math.max(5.0, {PKG}.SkillCfg.dbl(p, "acro.maxSpeed", 30.0));
  TELEPORT = Math.max(2.0, {PKG}.SkillCfg.dbl(p, "acro.teleportBlocks", 8.0));
  JUMP_XP = nn({PKG}.SkillCfg.dbl(p, "acro.jumpXp", 2.0));
  JUMP_CD = Math.max(200L, {PKG}.SkillCfg.lng(p, "acro.jumpCooldownMs", 800L));
  JUMP_MOVE = nn({PKG}.SkillCfg.dbl(p, "acro.jumpMinMove", 2.0));
  FALL_MIN = Math.max(1.0, {PKG}.SkillCfg.dbl(p, "acro.fallMinBlocks", 4.0));
  FALL_XP = nn({PKG}.SkillCfg.dbl(p, "acro.fallXpPerBlock", 2.0));
  FALL_DMG_XP = nn({PKG}.SkillCfg.dbl(p, "acro.fallDamageXp", 2.0));
  FALL_MAX = nn({PKG}.SkillCfg.dbl(p, "acro.fallXpMax", 50.0));
  DODGE_XP = nn({PKG}.SkillCfg.dbl(p, "acro.dodgeXp", 3.0));
  DODGE_CD = Math.max(100L, {PKG}.SkillCfg.lng(p, "acro.dodgeCooldownMs", 400L));
  MAX_PER_MIN = nn({PKG}.SkillCfg.dbl(p, "acro.maxXpPerMinute", 240.0));
  FEEDBACK_MS = Math.max(2000L, {PKG}.SkillCfg.lng(p, "acro.feedbackMs", 30000L));
  SPEED_PER_LVL = nn({PKG}.SkillCfg.dbl(p, "acro.speedPerLevel", 0.01));
  JUMP_PER_LVL = nn({PKG}.SkillCfg.dbl(p, "acro.jumpBlocksPerLevel", 0.015));
  FALL_PER_LVL = nn({PKG}.SkillCfg.dbl(p, "acro.fallReductionPerLevel", 0.005));
  FALL_RED_MAX = Math.min(1.0, nn({PKG}.SkillCfg.dbl(p, "acro.fallReductionMax", 0.8)));
  DODGE_BOOST = {PKG}.SkillCfg.bool(p, "acro.dodgeBoost", true);
  DODGE_FORCE = nn({PKG}.SkillCfg.dbl(p, "acro.dodgeForce", 13.0));
  DODGE_PER_LVL = nn({PKG}.SkillCfg.dbl(p, "acro.dodgeBoostPerLevel", 0.004));
  DODGE_MAX = Math.min(2.0, nn({PKG}.SkillCfg.dbl(p, "acro.dodgeBoostMax", 0.5)));
}}""", acfg))
# an xp.properties written by 0.1 has no acro.* key: append the documented section once (the code defaults apply either way)
acfg.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    if (String.valueOf(en.nextElement()).startsWith("acro.")) return;
  }}
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Acrobatics section (acro.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the acro.* section to xp.properties: " + t); }}
}}""", acfg))
cfg.addMethod(CtNewMethod.make(f"""
public static synchronized String load() {{''')
rep('''    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try {{ p.load(in); }} finally {{ in.close(); }}
    {PKG}.SkillDefs.setTable({PKG}.SkillDefs.DEFAULT_PER);
''', '''    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try {{ p.load(in); }} finally {{ in.close(); }}
    {PKG}.AcroCfg.ensureDefaults(p);
    {PKG}.SkillDefs.setTable({PKG}.SkillDefs.DEFAULT_PER);
''')
rep('''    C_DEFAULT = lng(p, "combat.default", 5L);
''', '''    C_DEFAULT = lng(p, "combat.default", 5L);
    {PKG}.AcroCfg.read(p);
''')
rep('''role rule(s), max level " + {PKG}.SkillDefs.MAX + (bad''', '''role rule(s), acrobatics " + ({PKG}.AcroCfg.ENABLED ? "on" : "off") + ", max level " + {PKG}.SkillDefs.MAX + (bad''')

# ---------------------------------------------------------------- SkillStore: data layout long[2N] (0.1 hard-coded 8 / offset 4)
rep('# data layout: long[8] = xp[0..3], paid level[4..7]', '# data layout: long[2*N] = xp[0..N-1], paid level[N..2N-1]   (0.2: N = 5; 0.1 hard-coded long[8] / offset 4)')
rep('# player file -> {long[8] data,', '# player file -> {long[2*N] data,')
rep('  long[] d = new long[8];\n', '  long[] d = new long[2 * {PKG}.SkillDefs.N];\n')
rep('d[4 + i]', 'd[{PKG}.SkillDefs.N + i]', count=6)
rep('4 + skill', '{PKG}.SkillDefs.N + skill', count=5)
rep('top.addField(CtField.make("public static final long[] AT = new long[4];", top))',
    'top.addField(CtField.make("public static final long[] AT = new long[%d];" % 5, top))   # = SkillDefs.N')
rep('top.addField(CtField.make("public static final Object[] CACHE = new Object[4];", top))',
    'top.addField(CtField.make("public static final Object[] CACHE = new Object[%d];" % 5, top))')

# ---------------------------------------------------------------- SkillXp: gain2 (Acrobatics throttles its own chat line)
rep('public static void gain({PR} pr, int skill, long amount) {{\n',
    'public static void gain2({PR} pr, int skill, long amount, boolean note) {{\n')
rep('''  {PKG}.SkillMsg.note(pr, skill, amount);
  long[] paid = null;''', '''  if (note) {PKG}.SkillMsg.note(pr, skill, amount);
  long[] paid = null;''')

ACRO_BLOCK = r'''xp.addMethod(CtNewMethod.make(f"""
public static void gain({PR} pr, int skill, long amount) {{
  gain2(pr, skill, amount, true);
}}""", xp))

# ================= 0.2 ACROBATICS =================
# MoveSync = the shared Skyy movement protocol (tools/skyymove.py; identical code in SkyyAccessories 0.3)
MV.add_move_sync(mvs_, CtField, CtNewMethod, PKG + ".SkillCfg.warn")

# Acro: per-player tracker (in memory only). STATE uuid -> double[152]:
#  0-2 last position, 3 has position, 4 prev onGround, 5 prev jumping, 6 prev dodging, 7 peak Y while airborne, 8 has peak,
#  9 last paid jump ms, 10 blocks moved since the last paid jump, 11 pending (fractional) XP, 12-13 unused (were the fixed per-minute
#  window, replaced by the sliding ring 24-151 in the review fix), 14 seconds since the last 1 s sync, 15 unresolved fall damage ms
#  (0 once it has been paid - review fix, a stale timestamp swallowed the next safe landing), 16 its unreduced amount, 17 fall damage
#  resolved, 18 pending landing ms, 19 its drop in blocks, 20 last dodge ms, 21 XP not shown in chat yet, 22 last chat line ms,
#  23 pending dodge boost ms (the push is sent 100 ms after the Dodge effect appears so it lands AFTER the dodge's own ApplyForce "Set"
#  instruction, which would erase it), 24-87 Acrobatics XP paid per wall-clock second (ring slot = second % 64), 88-151 the second
#  each ring slot holds. acro.maxXpPerMinute caps the XP of ANY 61 consecutive whole seconds, which covers every real 60 s interval
#  (review fix: the 0.2 draft reset a fixed 60 s window, so a burst across the reset paid ~2x the cap).
acro.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap STATE = new java.util.concurrent.ConcurrentHashMap();", acro))
acro.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap WORLD = new java.util.concurrent.ConcurrentHashMap();", acro))
acro.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap MOVE = new java.util.concurrent.ConcurrentHashMap();", acro))
acro.addField(CtField.make('public static final String SOURCE = "skills.acrobatics";', acro))
acro.addField(CtField.make('public static final String MOD = "SkyySkills";', acro))
acro.addMethod(CtNewMethod.make("""
public static double[] state(java.util.UUID u) {
  double[] s = (double[]) STATE.get(u);
  if (s != null) return s;
  double[] n = new double[152];
  Object o = STATE.putIfAbsent(u, n);
  return o == null ? n : (double[]) o;
}""", acro))
acro.addMethod(CtNewMethod.make("""
public static void reset(double[] s) {
  s[3] = 0.0; s[5] = 0.0; s[6] = 0.0; s[8] = 0.0; s[18] = 0.0; s[23] = 0.0;
}""", acro))
acro.addMethod(CtNewMethod.make("""
public static boolean worldChanged(java.util.UUID u, String wn) {
  if (wn == null) return false;
  Object o = WORLD.put(u, wn);
  return o != null && !o.equals(wn);
}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static void retainOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr != null) online.add(pr.getUuid());
    }}
    STATE.keySet().retainAll(online);
    WORLD.keySet().retainAll(online);
    MOVE.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", acro))
acro.addMethod(CtNewMethod.make("""
public static boolean isFall(com.hypixel.hytale.server.core.modules.entity.damage.DamageCause c) {
  if (c == null) return false;
  com.hypixel.hytale.server.core.modules.entity.damage.DamageCause f = com.hypixel.hytale.server.core.modules.entity.damage.DamageCause.FALL;
  if (c == f) return true;
  String a = c.getId();
  if (a == null) return false;
  if (f == null) return a.equals("Fall");
  return a.equals(f.getId());
}""", acro))
# bonuses of one Acrobatics level (fractions / blocks)
acro.addMethod(CtNewMethod.make(f"""
public static double speedBonus(int lvl) {{
  return lvl <= 0 ? 0.0 : lvl * {PKG}.AcroCfg.SPEED_PER_LVL;
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static double jumpBonus(int lvl) {{
  return lvl <= 0 ? 0.0 : lvl * {PKG}.AcroCfg.JUMP_PER_LVL;
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static double fallBonus(int lvl) {{
  if (lvl <= 0) return 0.0;
  double f = lvl * {PKG}.AcroCfg.FALL_PER_LVL;
  return f > {PKG}.AcroCfg.FALL_RED_MAX ? {PKG}.AcroCfg.FALL_RED_MAX : f;
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static double dodgeBonus(int lvl) {{
  if (lvl <= 0 || !{PKG}.AcroCfg.DODGE_BOOST) return 0.0;
  double f = lvl * {PKG}.AcroCfg.DODGE_PER_LVL;
  return f > {PKG}.AcroCfg.DODGE_MAX ? {PKG}.AcroCfg.DODGE_MAX : f;
}}""", acro))
# 0.123 -> "+12.3" (percent, signed), 0.5 -> "+50"
acro.addMethod(CtNewMethod.make("""
public static String pct(double v) {
  long t = Math.round(v * 1000.0);
  String sign = t < 0L ? "-" : "+";
  if (t < 0L) t = -t;
  if (t % 10L == 0L) return sign + (t / 10L);
  return sign + (t / 10L) + "." + (t % 10L);
}""", acro))
# 0.75 -> "+0.75" (blocks, signed)
acro.addMethod(CtNewMethod.make("""
public static String blocks(double v) {
  long t = Math.round(v * 100.0);
  String sign = t < 0L ? "-" : "+";
  if (t < 0L) t = -t;
  return sign + (t / 100L) + "." + ((t % 100L) < 10L ? "0" : "") + (t % 100L);
}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static String bonusText(int lvl) {{
  if (!{PKG}.AcroCfg.ENABLED) return "Acrobatics bonuses are turned off on this server";
  if (lvl <= 0) return "Level up to run faster - jump higher - take less fall damage - dodge further";
  String t = "Speed " + pct(speedBonus(lvl)) + "%   Jump " + blocks(jumpBonus(lvl)) + " blocks   Fall damage " + pct(0.0 - fallBonus(lvl)) + "%";
  double db = dodgeBonus(lvl);
  if (db > 0.0) t = t + "   Dodge " + pct(db) + "%";
  return t;
}}""", acro))
# fall Damage seen by AcroFallSys (world thread): remembered, paid by falls() once the player is still alive 0.4 s later
acro.addMethod(CtNewMethod.make("""
public static void noteFall(java.util.UUID u, float amount) {
  double[] s = state(u);
  s[15] = (double) System.currentTimeMillis();
  s[16] = (double) amount;
  s[17] = 0.0;
}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static boolean alive({ST} store, {REF} ref) {{
  try {{
    if (!ref.isValid()) return false;
    {ESM} m = ({ESM}) store.getComponent(ref, {ESM}.getComponentType());
    if (m == null) return true;
    int hi = {DST}.getHealth();
    if (hi < 0) return true;
    {ESV} hv = m.get(hi);
    return hv == null || hv.get() > 0.0f;
  }} catch (Throwable t) {{ return false; }}
}}""", acro))
# the ONE anti-exploit movement-state set (review fix: move() AND dodge() use it - the 0.2 draft only checked it in move())
acro.addMethod(CtNewMethod.make(f"""
public static boolean excludedState({MVT} ms) {{
  if (ms == null) return true;
  return ms.mounting || ms.flying || ms.gliding || ms.sitting || ms.sleeping || ms.climbing || ms.inFluid || ms.swimming || ms.mantling;
}}""", acro))
# running / jumping / landing detection for one tick
acro.addMethod(CtNewMethod.make(f"""
public static void move(double[] s, {MVT} ms, {V3D} pos, float dt, long now, boolean creative) {{
  double x = pos.x();
  double y = pos.y();
  double z = pos.z();
  boolean excluded = excludedState(ms);
  boolean tele = false;
  double hd = 0.0;
  if (s[3] > 0.5) {{
    double dx = x - s[0];
    double dy = y - s[1];
    double dz = z - s[2];
    hd = Math.sqrt(dx * dx + dz * dz);
    if (Math.sqrt(dx * dx + dy * dy + dz * dz) > {PKG}.AcroCfg.TELEPORT) tele = true;
    else if (dt > 0.0f && hd / (double) dt > {PKG}.AcroCfg.MAX_SPEED) tele = true;
  }}
  s[0] = x; s[1] = y; s[2] = z; s[3] = 1.0;
  if (tele) {{ hd = 0.0; s[8] = 0.0; s[18] = 0.0; }}
  boolean ground = ms.onGround;
  if (!tele && !excluded && !creative && ground && hd > 0.0) {{
    double rate = {PKG}.AcroCfg.RUN;
    if (ms.horizontalIdle || ms.idle) rate = 0.0;
    else if (ms.sprinting) rate = {PKG}.AcroCfg.SPRINT;
    else if (ms.walking || ms.crouching) rate = {PKG}.AcroCfg.WALK;
    s[11] = s[11] + hd * rate;
  }}
  if (!excluded) s[10] = s[10] + hd;
  boolean jmp = ms.jumping;
  if (jmp && s[5] < 0.5 && !excluded && !creative && !tele) {{
    if ((double) now - s[9] >= (double) {PKG}.AcroCfg.JUMP_CD && s[10] >= {PKG}.AcroCfg.JUMP_MOVE) {{
      s[11] = s[11] + {PKG}.AcroCfg.JUMP_XP;
      s[9] = (double) now;
      s[10] = 0.0;
    }}
  }}
  s[5] = jmp ? 1.0 : 0.0;
  if (excluded || tele) {{
    s[8] = 0.0;
  }} else if (!ground) {{
    if (s[8] < 0.5 || y > s[7]) s[7] = y;
    s[8] = 1.0;
  }} else {{
    if (s[4] < 0.5 && s[8] > 0.5) {{
      double drop = s[7] - y;
      if (drop >= {PKG}.AcroCfg.FALL_MIN && !creative) {{ s[18] = (double) now; s[19] = drop; }}
    }}
    s[8] = 0.0;
  }}
  s[4] = ground ? 1.0 : 0.0;
}}""", acro))
# pay landings: a FALL damage event near the landing pays by damage (if alive), otherwise the drop pays per block.
# Timing (verified in HytaleServer.jar): DamageSystems$FallDamagePlayers creates the FALL Damage from the SAME queued client
# SetMovementStates update (onGround) that PlayerSystems$ProcessPlayerInput applies to MovementStatesComponent, in the same world
# tick, so the damage note and the landing AcroSys sees are at most a tick apart; the note is paid at +400 ms, the landing at +700 ms.
# Review fix: a paid note is cleared (s[15] = 0) and the landing check only counts an UNRESOLVED note, so the timestamp of an
# earlier, already paid fall can no longer swallow the XP of the next safe landing within 1.5 s.
acro.addMethod(CtNewMethod.make(f"""
public static void falls(double[] s, {ST} store, {REF} ref, long now, boolean creative) {{
  double t = (double) now;
  if (s[15] > 0.0 && s[17] < 0.5 && t - s[15] >= 400.0) {{
    s[17] = 1.0;
    if (!creative && alive(store, ref)) {{
      double x = s[16] * {PKG}.AcroCfg.FALL_DMG_XP;
      if (x > {PKG}.AcroCfg.FALL_MAX) x = {PKG}.AcroCfg.FALL_MAX;
      if (x > 0.0) s[11] = s[11] + x;
    }}
    if (s[18] > 0.0 && Math.abs(s[18] - s[15]) < 1500.0) s[18] = 0.0;
    s[15] = 0.0;
  }}
  if (s[18] > 0.0 && t - s[18] >= 700.0) {{
    boolean hurt = s[15] > 0.0 && s[17] < 0.5 && Math.abs(s[15] - s[18]) < 1500.0;
    if (!hurt && !creative) {{
      double x = (s[19] - {PKG}.AcroCfg.FALL_MIN + 1.0) * {PKG}.AcroCfg.FALL_XP;
      if (x > {PKG}.AcroCfg.FALL_MAX) x = {PKG}.AcroCfg.FALL_MAX;
      if (x > 0.0) s[11] = s[11] + x;
    }}
    s[18] = 0.0;
  }}
}}""", acro))
# dodge boost: extra push along the client's horizontal velocity (vanilla LaunchPadInteraction / knockback path: Velocity instruction ->
# PlayerVelocityInstructionSystem -> ChangeVelocity packet, VelocityConfig null like the launch pad)
acro.addMethod(CtNewMethod.make(f"""
public static void boost({CB} cb, {REF} ref, java.util.UUID u) {{
  double f = dodgeBonus({PKG}.SkillStore.level(u, {PKG}.SkillDefs.ACROBATICS));
  if (f <= 0.0) return;
  {VEL} v = ({VEL}) cb.getComponent(ref, {VEL}.getComponentType());
  if (v == null) return;
  {V3D} cv = v.getClientVelocity();
  if (cv == null) return;
  double hx = cv.x();
  double hz = cv.z();
  double hl = Math.sqrt(hx * hx + hz * hz);
  if (hl < 1.0) return;
  double add = {PKG}.AcroCfg.DODGE_FORCE * f;
  v.addInstruction(new {V3D}(hx / hl * add, 0.0, hz / hl * add), ({VCF}) null, {CVT}.Add);
}}""", acro))
# excluded = excludedState(MovementStates) of this tick (true when the component is missing): review fix - a dodge in an excluded
# state (mounted, flying, gliding, sitting, sleeping, climbing, in fluid, swimming, mantling) pays no XP and gets no push, exactly
# like running / jumping / falling in move(); a push still pending when the player enters such a state is dropped. The edge (s[6])
# is tracked in every state, so a Dodge effect that began while excluded is not counted when the state ends mid-effect.
acro.addMethod(CtNewMethod.make(f"""
public static void dodge(double[] s, {ST} store, {CB} cb, {REF} ref, java.util.UUID u, long now, boolean creative, boolean excluded) {{
  {ECC} ecc = ({ECC}) store.getComponent(ref, {ECC}.getComponentType());
  boolean on = false;
  if (ecc != null) {{
    int li = {EFX}.getAssetMap().getIndex("Dodge_Left");
    int ri = {EFX}.getAssetMap().getIndex("Dodge_Right");
    if (li != Integer.MIN_VALUE && ecc.hasEffect(li)) on = true;
    if (ri != Integer.MIN_VALUE && ecc.hasEffect(ri)) on = true;
  }}
  if (on && s[6] < 0.5 && !excluded && (double) now - s[20] >= (double) {PKG}.AcroCfg.DODGE_CD) {{
    s[20] = (double) now;
    if (!creative) s[11] = s[11] + {PKG}.AcroCfg.DODGE_XP;
    if ({PKG}.AcroCfg.DODGE_BOOST) s[23] = (double) (now + 100L);
  }}
  s[6] = on ? 1.0 : 0.0;
  if (s[23] > 0.0 && (double) now >= s[23]) {{
    s[23] = 0.0;
    if (on && !excluded) boost(cb, ref, u);
  }}
}}""", acro))
# sliding XP cap (review fix): per-second ring, see the STATE layout above
acro.addMethod(CtNewMethod.make("""
public static double paidRecently(double[] s, long sec) {
  double sum = 0.0;
  double lo = (double) (sec - 60L);
  double hi = (double) sec;
  for (int k = 0; k < 64; k++) {
    double at = s[88 + k];
    if (at >= lo && at <= hi) sum = sum + s[24 + k];
  }
  return sum;
}""", acro))
acro.addMethod(CtNewMethod.make("""
public static void addPaid(double[] s, long sec, double amt) {
  int k = (int) (sec % 64L);
  if (s[88 + k] != (double) sec) { s[88 + k] = (double) sec; s[24 + k] = 0.0; }
  s[24 + k] = s[24 + k] + amt;
}""", acro))
# whole XP that may be paid now under acro.maxXpPerMinute (0 = none); records what it allows
acro.addMethod(CtNewMethod.make(f"""
public static double take(double[] s, long now, double whole) {{
  long sec = now / 1000L;
  double room = {PKG}.AcroCfg.MAX_PER_MIN - paidRecently(s, sec);
  if (whole > room) whole = Math.floor(room);
  if (whole < 1.0) return 0.0;
  addPaid(s, sec, whole);
  return whole;
}}""", acro))
# once per second: pay whole XP (sliding per-minute cap, global multiplier), throttled chat line
acro.addMethod(CtNewMethod.make(f"""
public static void flush({PR} pr, double[] s, long now) {{
  if (pr == null) return;
  double t = (double) now;
  double whole = Math.floor(s[11]);
  if (whole >= 1.0) {{
    s[11] = s[11] - whole;
    whole = take(s, now, whole);
    if (whole >= 1.0) {{
      long amt = {PKG}.SkillCfg.scaled((long) whole);
      if (amt > 0L) {{
        {PKG}.SkillXp.gain2(pr, {PKG}.SkillDefs.ACROBATICS, amt, false);
        s[21] = s[21] + (double) amt;
      }}
    }}
  }}
  if (s[21] >= 1.0 && t - s[22] >= (double) {PKG}.AcroCfg.FEEDBACK_MS) {{
    long shown = (long) s[21];
    s[21] = 0.0;
    s[22] = t;
    {PKG}.SkillMsg.note(pr, {PKG}.SkillDefs.ACROBATICS, shown);
  }}
}}""", acro))
# once per second: publish this player's Acrobatics bonus (flat layer) and apply the protocol total
acro.addMethod(CtNewMethod.make(f"""
public static void bonuses(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref) {{
  int lvl = {PKG}.AcroCfg.ENABLED ? {PKG}.SkillStore.level(u, {PKG}.SkillDefs.ACROBATICS) : 0;
  {PKG}.MoveSync.post(u, SOURCE, "flat", (float) speedBonus(lvl), (float) jumpBonus(lvl), (float) (0.0 - fallBonus(lvl)));
  {PKG}.MoveSync.sync(u, pr, cb, ref, MOVE, MOD);
}}""", acro))

# AcroSys: EntityTickingSystem on Player entities (AccEffects pattern; runs on the world thread, not parallel)
asy.addConstructor(CtNewConstructor.make("public AcroSys() { super(); }", asy))
asy.addField(CtField.make("public static boolean FAILED_ONCE = false;", asy))
asy.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", asy))
asy.addMethod(CtNewMethod.make(f"""
public void tick(float dt, int idx, {ACH} chunk, {ST} store, {CB} cb) {{
  try {{
    {REF} ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    {PLA} p = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    {PR} pr = ({PR}) store.getComponent(ref, {PR}.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    double[] s = {PKG}.Acro.state(u);
    long now = System.currentTimeMillis();
    String wn = null;
    Object ext = store.getExternalData();
    if (ext instanceof {EST}) {{
      {WLD} w = (({EST}) ext).getWorld();
      if (w != null) wn = w.getName();
    }}
    if ({PKG}.Acro.worldChanged(u, wn)) {PKG}.Acro.reset(s);
    if ({PKG}.AcroCfg.ENABLED) {{
      boolean creative = {PKG}.SkillXp.creative(store, ref);
      {MSC} msc = ({MSC}) store.getComponent(ref, {MSC}.getComponentType());
      {TRC} tc = ({TRC}) store.getComponent(ref, {TRC}.getComponentType());
      {MVT} ms = null;
      if (msc != null) ms = msc.getMovementStates();
      {V3D} pos = null;
      if (tc != null) pos = tc.getPosition();
      if (ms != null && pos != null) {PKG}.Acro.move(s, ms, pos, dt, now, creative);
      {PKG}.Acro.dodge(s, store, cb, ref, u, now, creative, {PKG}.Acro.excludedState(ms));
      {PKG}.Acro.falls(s, store, ref, now, creative);
    }}
    s[14] = s[14] + (double) dt;
    if (s[14] < 1.0) return;
    s[14] = 0.0;
    {PKG}.Acro.flush(pr, s, now);
    {PKG}.Acro.bonuses(u, pr, cb, ref);
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("acrobatics tick failed (logged once): " + t); }}
  }}
}}""", asy))

# AcroFallSys: DamageEventSystem in the FILTER group (vanilla DamageSystems$ArmorDamageReduction pattern; ApplyDamage declares
# AFTER Gather, AFTER Filter, BEFORE Inspect). Remembers every player fall for XP; as the elected fall-damage applier it scales the
# damage by the summed fallDamage multiplier of all protocol sources (never below 0, never cancels).
afs.addConstructor(CtNewConstructor.make("public AcroFallSys() { super(); }", afs))
afs.addField(CtField.make("public static boolean FAILED_ONCE = false;", afs))
afs.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", afs))
afs.addMethod(CtNewMethod.make(f"""
public {SYG} getGroup() {{
  return {DMM}.get().getFilterDamageGroup();
}}""", afs))
afs.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
    {DMG} d = ({DMG}) ev;
    if (d.isCancelled()) return;
    if (!{PKG}.Acro.isFall(d.getCause())) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    {PKG}.Acro.noteFall(u, d.getInitialAmount());
    if (!{PKG}.MoveSync.ownsFall({PKG}.Acro.MOD)) return;
    float m = {PKG}.MoveSync.fallMultiplier({PKG}.MoveSync.sums(u));
    if ({PKG}.MoveSync.near(m, 1.0f)) return;
    float a = d.getAmount() * m;
    if (a < 0.0f) a = 0.0f;
    d.setAmount(a);
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("acrobatics fall damage handler failed (logged once): " + t); }}
  }}
}}""", afs))
'''
rep('}}""", xp))\n\n# ================= PlacedStore: positions of player-placed blocks, per world =================',
    '}}""", xp))\n' + ACRO_BLOCK + '\n# ================= PlacedStore: positions of player-placed blocks, per world =================')

# ---------------------------------------------------------------- /skills page: 5 rows, Acrobatics row with its bonuses
rep('"Group #SkyySkills {{ Anchor: (Width: 640, Height: 480);', '"Group #SkyySkills {{ Anchor: (Width: 640, Height: 530);')
rep('''      b.appendInline("#SkyySkills", "Group #SkyySkRow" + i + " {{ Anchor: (Height: 72); LayoutMode: Left; Padding: (Top: 6); Background: #142030(0.9); }}");''',
'''      int rh = i == {PKG}.SkillDefs.ACROBATICS ? 88 : 72;
      b.appendInline("#SkyySkills", "Group #SkyySkRow" + i + " {{ Anchor: (Height: " + rh + "); LayoutMode: Left; Padding: (Top: 6); Background: #142030(0.9); }}");''')
rep('''"Group #SkyySkTxt" + i + " {{ Anchor: (Width: 420, Height: 60); LayoutMode: Top; }}");''',
    '''"Group #SkyySkTxt" + i + " {{ Anchor: (Width: 420, Height: " + (rh - 12) + "); LayoutMode: Top; }}");''')
rep('''      b.appendInline("#SkyySkTxt" + i, "Label {{ Anchor: (Height: 20); Text: \\\\"" + safe(prog) + "\\\\"; Style: (FontSize: 11, TextColor: #b8c8d8, VerticalAlignment: Center); }}");
''', '''      b.appendInline("#SkyySkTxt" + i, "Label {{ Anchor: (Height: 20); Text: \\\\"" + safe(prog) + "\\\\"; Style: (FontSize: 11, TextColor: #b8c8d8, VerticalAlignment: Center); }}");
      if (i == {PKG}.SkillDefs.ACROBATICS) {{
        b.appendInline("#SkyySkTxt" + i, "Label #SkyySkBonus {{ Anchor: (Height: 16); Text: \\\\"\\\\"; Style: (FontSize: 10, RenderBold: true, TextColor: #d8c0ff, VerticalAlignment: Center); }}");
        b.set("#SkyySkBonus.Text", {PKG}.Acro.bonusText(lv));
      }}
''')
rep('Text: \\\\"Mine ores and stone - chop trees - harvest ripe crops - defeat monsters.  /skills quiet hides XP messages\\\\";',
    'Text: \\\\"Mine - chop trees - harvest ripe crops - defeat monsters - run jump fall and dodge.  /skills quiet hides XP messages\\\\";')

# ---------------------------------------------------------------- commands
rep('withRequiredArg("skill", "mining | foraging | farming | combat", {ATY}.STRING);',
    'withRequiredArg("skill", "mining | foraging | farming | combat | acrobatics", {ATY}.STRING);')
rep('"[Skills] Unknown skill. Use mining, foraging, farming or combat."', '"[Skills] Unknown skill. Use mining, foraging, farming, combat or acrobatics."')

# ---------------------------------------------------------------- ticker prune, plugin setup / shutdown
rep('''  if (this.n % 60L == 0L) {{ try {{ {PKG}.PlacedStore.flush(); }} catch (Throwable t) {{ }} }}
''', '''  if (this.n % 60L == 0L) {{ try {{ {PKG}.PlacedStore.flush(); }} catch (Throwable t) {{ }} }}
  if (this.n % 30L == 0L) {{ try {{ {PKG}.Acro.retainOnline(); }} catch (Throwable t) {{ }} }}
''')
rep('''  getEntityStoreRegistry().registerSystem(new {PKG}.KillSys());
''', '''  getEntityStoreRegistry().registerSystem(new {PKG}.KillSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.AcroSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.AcroFallSys());
  {PKG}.MoveSync.checkProto({PKG}.Acro.MOD);
  boolean fallOwner = {PKG}.MoveSync.ownsFall({PKG}.Acro.MOD);
''')
rep('''log("[SkyySkills] {VERSION} ready - /skills; xp rules: " + rules);''',
    '''log("[SkyySkills] {VERSION} ready - /skills; xp rules: " + rules + (fallOwner ? "" : "; fall damage bonuses are applied by " + {PKG}.MoveSync.bridge().get({PKG}.MoveSync.OWNER_FALL)));''')
rep('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:level"); }} catch (Throwable t) {{ }}
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:level"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.MoveSync.releaseFall({PKG}.Acro.MOD); }} catch (Throwable t) {{ }}
''')
rep('for c in (defs, cfg, sto, pub, fn, msg, fl, xp, plc, hg, btk, ptk, htk, bsy, psy, usy, ksy, tcm, top, page, tcmd, qcmd, rcmd, cmd, tick, pl):',
    'for c in (defs, cfg, sto, pub, fn, msg, fl, xp, plc, hg, btk, ptk, htk, bsy, psy, usy, ksy, tcm, top, page, tcmd, qcmd, rcmd, cmd, tick, pl, acfg, mvs_, acro, asy, afs):')
rep('"SkyWynn skills (Hypixel SkyBlock style): Mining, Foraging, Farming, Combat to level 50. XP from breaking blocks, ripe crops and NPC kills; level ups pay SkyyCoins. /skills. Zero dependencies."',
    '"SkyWynn skills (Hypixel SkyBlock style): Mining, Foraging, Farming, Combat, Acrobatics to level 50. XP from breaking blocks, ripe crops, NPC kills and running / jumping / falling / dodging; Acrobatics raises speed, jump height and dodge push and lowers fall damage (shared Skyy movement protocol). Level ups pay SkyyCoins. /skills. Zero dependencies."')

assert "SkillDefs.N + i]" in s and "new long[8]" not in s and "4 + skill" not in s
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.1
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
