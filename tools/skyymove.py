"""SKYY SHARED MOVEMENT PROTOCOL v1 - one source of truth for every Skyy mod that changes a player's movement stats.
Used at BUILD time by SkyySkills 0.2+ and SkyyAccessories 0.3+ (each jar gets its own copy of the MoveSync class in its own package,
so there is no runtime dependency between the mods; both copies are generated from THIS file, so they behave identically).

WHY: speed talismans (SkyyAccessories) and Acrobatics (SkyySkills) both change MovementManager.getSettings(). Two mods that each write
"default * my bonus" overwrite each other every second (flicker, then both back off). With this protocol every mod only PUBLISHES its
own bonus, and every applier computes the SAME total from ALL published bonuses, so any number of appliers agree (idempotent).

BRIDGE DATA (JVM-global map System.getProperties().get("skyy.bridge"), JDK types only - never a class from a mod jar):
  "move:proto"     -> Integer 1 (first mod to start sets it; a mod that sees another number logs a warning)
  "move:<uuid>"    -> java.util.concurrent.ConcurrentHashMap  source name -> entry     (created with putIfAbsent by whoever posts first)
  entry            =  java.util.Map (never mutated after it is put; replace the whole entry to change it):
                        "layer"      -> String "flat" | "pct"
                        "speed"      -> Number   flat: fraction of the DEFAULT base speed added (0.25 = +25 % of vanilla speed)
                                                  pct : percent on top, as a fraction (0.10 = +10 %)
                        "jump"       -> Number   flat: extra jump HEIGHT in blocks           pct : jump height x (1 + value)
                        "fallDamage" -> Number   flat: added to the fall-damage multiplier   pct : multiplier x (1 + value)
                                                  (negative = less damage: -0.25 = 25 % less)
                      Unknown keys are ignored (the stat list is extensible); non-numbers / NaN count as 0.
  "stat:owner:fallDamage" -> String mod name. Damage stats must be applied ONCE: the mod that wins putIfAbsent applies the summed
                      fallDamage of ALL sources in its Damage filter system; every other mod only posts. Released on shutdown with
                      remove(key, ownName). (SkyySkills 0.2 is the only fall-damage applier today.)
Source names in use: "skills.acrobatics" (SkyySkills, layer flat), "accessories.talismans" (SkyyAccessories, layer pct).

LAYERED FORMULA (Skyy 2026-09-23: skills + armor = FLAT on the default, accessories = PERCENT on top):
  speed factor  = clamp((1 + sum flat speed) * (1 + sum pct speed), 0.3, 5.0);  baseSpeed = default.baseSpeed * factor
  jump height   = clamp((h0 + sum flat jump) * (1 + sum pct jump), 0, h0 + 20),  h0 = default.jumpForce^2 / (2 g)
                  jumpForce = sqrt(2 g height)   (g = PhysicsConstants.GRAVITY_ACCELERATION = 32; the engine's own jump sets
                  velocity.y = jumpForce, verified in KnockbackPredictionSystems$SimulateKnockback; default JumpForce 11.8 -> h0 2.18)
  fall damage   = damage * clamp((1 + sum flat fallDamage) * (1 + sum pct fallDamage), 0, 2)   (never heals)
  Only MovementSettings.baseSpeed and .jumpForce are written (the direction multipliers are factors ON baseSpeed - scaling them too
  compounds, see SkyyAccessories 0.2 notes).

RULES FOR A MOD:
  1. post(u, mySource, layer, speed, jump, fall) whenever your bonus may have changed (Skyy mods do it every 1 s per online player,
     on the world thread). All zeros REMOVES your entry. Never touch another source's entry.
  2. sync(u, playerRef, commandBuffer, ref, myStateMap, myName) right after posting (world thread). It computes the target from ALL
     sources and writes baseSpeed/jumpForce only when the live value differs, then MovementManager.update(packetHandler).
  3. Nothing is written while MovementStates.mounting is true (mount settings belong to the mount); the engine re-applies defaults
     on dismount/world change/game mode/model change and the next sync (<= 1 s) puts the bonus back.
  4. Reset detection that works with several appliers, PER FIELD (Movement 2, 2026-10-18): per player {lastWrittenSpeed,
     lastWrittenJump, speedStrikes, targetSpeed, targetJump, speedWarned, jumpStrikes, jumpWarned, rideFails, rideState, rideAmount,
     -}. For each field (baseSpeed, jumpForce) on its own: live value already equal to the target (whoever wrote it) -> that field's
     strikes = 0, no write. Different -> write, strikes++. A NEW target for a field (a source changed) resets that field's strikes.
     5 strikes in a row = something outside the protocol keeps resetting THAT field -> that field pauses until its target changes;
     the other field keeps working (a jump fight never costs the speed bonus). Each field's pause is logged ONCE PER PLAYER (flag in
     that player's state; forgotten with the state, i.e. when the player's total goes neutral or the player leaves), with the number
     of players paused right now and the known outside writers that are loaded (see OUTSIDE THE PROTOCOL). Two protocol appliers never
     strike each other because they compute the same target; a one-sync disagreement while a source is being replaced is healed on
     the next sync.
  4b. THE ARMORY JUMP RIDE (Movement 2; research/Armory-Movement-Conflict.md; Skyy 2026-10-09 "lock the armory jump system ... edit
     theirs to work with our mods instead of clashing" = absorbed at runtime, nothing of theirs edited). The Armory 1.23.0's
     JumpHeightModifierSystem writes, EVERY tick for EVERY player, jumpForce = default.jumpForce x StatMultiplier.forStat(Jump_Height)
     and swimJumpForce likewise (VERIFIED bytecode 2026-10-18: fromMaxima(assetMax, valueMax) = 1 when assetMax <= 0 or
     |valueMax - assetMax| <= 1e-4, else max(0, 1 + valueMax / assetMax), not finite -> 1). The engine's EntityStatValue.computeModifiers
     (VERIFIED) builds max = (assetMax + sum of ADDITIVE MAX amounts) x (sum of MULTIPLICATIVE MAX amounts, only when one exists) - so
     the Engineering Rig's Multiplicative 0.2 gives max 2 of 10 = x1.2 jump force. When the stat asset "Jump_Height" exists (a pack
     with it is loaded) and move:cfg:armoryJump is not "yield", the jump half of our target is NOT written to jumpForce: one ADDITIVE
     MAX modifier "skyy_move_jump" on the player's Jump_Height stat is solved (rideAmount) so their multiplier becomes
     W x M (W = their multiplier from every OTHER modifier = the Rig, M = our jumpForce / default) and their own system produces our
     jump; nothing fights, their armor effect and ours stack. M = 1 removes the key. Every applier solves the same amount (idempotent).
     CALIBRATION (closed loop): one sync after the amount last changed, the live jumpForce must equal default x W x M (0.1 %); 3 failed
     checks in a row -> that player falls back to rule 4 (the modifier is removed, jumpForce written directly - against The Armory it
     strikes and the JUMP pauses, speed unaffected; one warning per player). The modifier is saved with the player by the engine: it is
     removed when the total goes neutral, on yield / fallback, and re-solved on the next sync after a join (rollback note: a build
     without this code leaves it on - with The Armory it keeps a jump bonus; set move:cfg:armoryJump = yield before rolling back).
     While riding, The Armory's swimJumpForce gets the same factor (their rule). Mounted players are skipped as before.
     move:cfg:armoryJump (bridge String, "ride" default / "yield") is published by SkyyGear's Server Setup row move.armoryJump.
  5. When the total is neutral (no bonus left) an applier restores the default ONLY for a field that still holds the exact value it
     last wrote (so another movement mod is never stomped), then forgets the player. A player nobody touched is never written.

OUTSIDE THE PROTOCOL (review 2026-09-23 - decision for SkyWynn):
  The protocol only coordinates mods that implement it (today: SkyySkills 0.2+, SkyyAccessories 0.3+). Any other mod that writes
  MovementSettings.baseSpeed / jumpForce directly cannot be told apart from "the engine reset the settings": if it re-applies its own
  value every tick, rule 4 backs off after 5 strikes and THAT MOD WINS for that player (no flicker war, but no Skyy speed/jump bonus
  for that player until a Skyy bonus changes). fallDamage is not affected (it is a Damage filter, not a MovementSettings write).
  SkyWynn decision: do NOT enable a direct MovementSettings writer in a SkyWynn world together with SkyySkills 0.2 / SkyyAccessories
  0.3. To make a violation visible, every applier checks the loaded + enabled plugins once, on its first sync (all plugins are loaded
  by then), against KNOWN_WRITERS below and logs one warning naming each one found; the per-player pause lines repeat the names.
  KNOWN_WRITERS = bytecode scan (PUTFIELD MovementSettings.baseSpeed / jumpForce) of every jar in UserData/Mods on 2026-09-23,
  matched by manifest Group + Name (Skyy mods carry the version in Name, so the pre-protocol SkyyAccessories 0.2 is listed too).
  Re-run the scan (scratchpad mvwrite_scan.py pattern) when new movement mods are installed and extend the list.
"""

PROTOCOL = 1

MSC = "com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent"
MVT = "com.hypixel.hytale.protocol.MovementStates"
MMG = "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementManager"
MVS = "com.hypixel.hytale.protocol.MovementSettings"
PHC = "com.hypixel.hytale.server.core.modules.physics.util.PhysicsConstants"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
CB  = "com.hypixel.hytale.component.CommandBuffer"
PLM = "com.hypixel.hytale.server.core.plugin.PluginManager"
PLB = "com.hypixel.hytale.server.core.plugin.PluginBase"
PID = "com.hypixel.hytale.common.plugin.PluginIdentifier"
# Movement 2 (rule 4b): the Jump_Height stat ride
ESM = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"
ESV = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue"
ESTT = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType"
SMO = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier"
CAL = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType"
MTG = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget"
MODF = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier"
ALM = "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap"
JUMP_STAT = "Jump_Height"          # The Armory's stat (Server/Entity/Stats/Jump_Height.json: Min 1, Max 10, Initial 1)
RIDE_KEY = "skyy_move_jump"        # our ONE modifier key on it (saved with the player by the engine)
CFG_RIDE = "move:cfg:armoryJump"   # bridge String "ride" (default) | "yield"
RIDE_WRITER = ("LadyPaladra", "TheArmory")   # the KNOWN_WRITERS row the ride absorbs (not named in the conflict warning while riding)
RIDE_FAILS = 3                     # failed calibration checks in a row before a player falls back to rule 4

# (manifest Group, manifest Name, what it writes) - see OUTSIDE THE PROTOCOL. Scan of UserData/Mods, 2026-09-23.
KNOWN_WRITERS = (
    ("Skyy", "0.2 SkyyAccessories", "pre-protocol Speed talisman, AccEffects: baseSpeed - deploy SkyyAccessories 0.3"),
    ("Alechilles", "Alec's Tamework!", "AvatarFlightGroundMovementService: baseSpeed"),
    ("Config", "Endgame&QoL", "AccessoryPassiveSystem: baseSpeed"),
    ("HylamityTeam", "Hylamity", "GroundMoveSpeedModifierSystem: baseSpeed"),
    ("Siren", "Mermaids", "Mermaid / Vampire / Werewolf systems: baseSpeed, jumpForce"),
    ("Wyyne", "More Boots", "BootsListener: jumpForce"),
    ("nep", "NotEnoughPotions", "speed / jump / water speed potions: baseSpeed, jumpForce"),
    ("Zuxaw", "RPGLeveling", "MovementSpeedHelper, DeathDetectionSystem: baseSpeed"),
    ("OrbisOrigins", "Rogue", "PlayerController: baseSpeed, jumpForce"),
    ("fevzi", "TerrariaAddons", "SpeedBoostSystem, BalloonSystem: baseSpeed, jumpForce"),
    ("LadyPaladra", "TheArmory", "JumpHeightModifierSystem: jumpForce, swimJumpForce (handled by the Jump_Height stat ride); "
                                 "GroundMoveSpeedModifierSystem: forwardSprintSpeedMultiplier (no conflict)"),
    ("ninesliced", "Unstable Rifts", "ArmorAbilityBuffSystem, PlayerStateService: baseSpeed, jumpForce"),
)


def _java_strings(vals):
    import json
    for v in vals:
        assert all(ord(ch) < 128 for ch in v) and "\\" not in v, v
    return "new String[] { " + ", ".join(json.dumps(v) for v in vals) + " }"


def probe(B, pool):
    """API drift check for everything MoveSync touches."""
    for c, m in ((MSC, "getComponentType"), (MSC, "getMovementStates"), (MVT, "mounting"), (MMG, "getComponentType"),
                 (MMG, "getSettings"), (MMG, "getDefaultSettings"), (MMG, "update"), (MVS, "baseSpeed"), (MVS, "jumpForce"),
                 (PHC, "GRAVITY_ACCELERATION"), (PR, "getPacketHandler"), (CB, "getComponent"),
                 (PLM, "get"), (PLM, "getPlugins"), (PLB, "getIdentifier"), (PLB, "isEnabled"), (PID, "getGroup"), (PID, "getName"),
                 ("java.util.Map", "putIfAbsent"), ("java.util.Map", "remove"),
                 (ESM, "getComponentType"), (ESM, "get"), (ESM, "update"), (ESM, "getModifier"), (ESM, "putModifier"), (ESM, "removeModifier"),
                 (ESV, "getModifiers"), (ESV, "getMax"), (ESTT, "getAssetMap"), (ESTT, "getMax"), (ALM, "getIndex"),
                 (ALM, "getAsset"), (SMO, "getAmount"), (SMO, "getCalculationType"), (MODF, "getTarget"), (CAL, "ADDITIVE"),
                 (CAL, "MULTIPLICATIVE"), (MTG, "MAX"), (MVS, "swimJumpForce")):
        B.probe(pool, c, m)


def add_move_sync(cls, CtField, CtNewMethod, warn):
    """Fill the (already created, empty) CtClass `cls` with the protocol implementation.
    warn = fully qualified static void method taking a String, e.g. "com.skyy.skills.SkillCfg.warn" (must already be compiled)."""
    fqn = cls.getName()
    cls.addField(CtField.make("public static final int PROTOCOL = %d;" % PROTOCOL, cls))
    cls.addField(CtField.make('public static final String OWNER_FALL = "stat:owner:fallDamage";', cls))
    # review fix: the pause warning is per player now (state[5]); the old single static WARNED flag is gone
    cls.addField(CtField.make("public static final String[] KNOWN_GROUP = %s;" % _java_strings([w[0] for w in KNOWN_WRITERS]), cls))
    cls.addField(CtField.make("public static final String[] KNOWN_NAME = %s;" % _java_strings([w[1] for w in KNOWN_WRITERS]), cls))
    cls.addField(CtField.make("public static final String[] KNOWN_WHAT = %s;" % _java_strings([w[2] for w in KNOWN_WRITERS]), cls))
    cls.addField(CtField.make("public static volatile boolean CONFLICTS_CHECKED = false;", cls))
    cls.addField(CtField.make('public static volatile String CONFLICTS = "";', cls))
    # Movement 2 (rule 4b)
    cls.addField(CtField.make('public static final String JUMP_STAT = "%s";' % JUMP_STAT, cls))
    cls.addField(CtField.make('public static final String RIDE_KEY = "%s";' % RIDE_KEY, cls))
    cls.addField(CtField.make('public static final String CFG_RIDE = "%s";' % CFG_RIDE, cls))
    cls.addField(CtField.make('public static final String RIDE_GROUP = "%s";' % RIDE_WRITER[0], cls))
    cls.addField(CtField.make('public static final String RIDE_NAME = "%s";' % RIDE_WRITER[1], cls))
    cls.addField(CtField.make("public static final float RIDE_FAILS = %d.0f;" % RIDE_FAILS, cls))
    cls.addField(CtField.make("public static volatile int RIDES = 0;", cls))          # sanity counters for a harness / debug line
    cls.addField(CtField.make("public static volatile int FALLBACKS = 0;", cls))
    assert RIDE_WRITER in [(w[0], w[1]) for w in KNOWN_WRITERS]
    cls.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", cls))
    cls.addMethod(CtNewMethod.make(f"""
public static void checkProto(String mod) {{
  try {{
    Object o = bridge().putIfAbsent("move:proto", Integer.valueOf(PROTOCOL));
    if (o instanceof Number && ((Number) o).intValue() != PROTOCOL) {warn}(mod + ": another mod speaks movement protocol " + o + ", this one speaks " + PROTOCOL + " - movement bonuses may fight");
  }} catch (Throwable t) {{ }}
}}""", cls))
    cls.addMethod(CtNewMethod.make("""
public static java.util.Map sources(java.util.UUID u, boolean create) {
  java.util.Map b = bridge();
  String k = "move:" + u.toString();
  Object o = b.get(k);
  if (o instanceof java.util.Map) return (java.util.Map) o;
  if (!create) return null;
  java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
  Object prev = b.putIfAbsent(k, n);
  if (prev instanceof java.util.Map) return (java.util.Map) prev;
  return n;
}""", cls))
    cls.addMethod(CtNewMethod.make("""
public static void post(java.util.UUID u, String source, String layer, float speed, float jump, float fall) {
  if (speed == 0.0f && jump == 0.0f && fall == 0.0f) {
    java.util.Map m = sources(u, false);
    if (m != null) m.remove(source);
    return;
  }
  java.util.HashMap e = new java.util.HashMap();
  e.put("layer", layer);
  e.put("speed", Float.valueOf(speed));
  e.put("jump", Float.valueOf(jump));
  e.put("fallDamage", Float.valueOf(fall));
  java.util.Map m = sources(u, true);
  if (e.equals(m.get(source))) return;
  m.put(source, e);
}""", cls))
    cls.addMethod(CtNewMethod.make("""
public static float num(Object o) {
  if (!(o instanceof Number)) return 0.0f;
  float f = ((Number) o).floatValue();
  if (Float.isNaN(f) || Float.isInfinite(f)) return 0.0f;
  return f;
}""", cls))
    # {flatSpeed, pctSpeed, flatJump, pctJump, flatFall, pctFall}
    cls.addMethod(CtNewMethod.make("""
public static float[] sums(java.util.UUID u) {
  float[] r = new float[6];
  java.util.Map m = sources(u, false);
  if (m == null) return r;
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof java.util.Map)) continue;
    java.util.Map e = (java.util.Map) o;
    int off = "pct".equals(e.get("layer")) ? 1 : 0;
    r[off] = r[off] + num(e.get("speed"));
    r[2 + off] = r[2 + off] + num(e.get("jump"));
    r[4 + off] = r[4 + off] + num(e.get("fallDamage"));
  }
  return r;
}""", cls))
    cls.addMethod(CtNewMethod.make("""
public static float clamp(float v, float lo, float hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}""", cls))
    cls.addMethod(CtNewMethod.make("""
public static float speedFactor(float[] r) {
  return clamp((1.0f + r[0]) * (1.0f + r[1]), 0.3f, 5.0f);
}""", cls))
    cls.addMethod(CtNewMethod.make(f"""
public static float jumpForce(float[] r, float def) {{
  if (def <= 0.0f) return def;
  double g = {PHC}.GRAVITY_ACCELERATION;
  if (g <= 0.0) g = 32.0;
  double h0 = (double) def * (double) def / (2.0 * g);
  double h = (h0 + (double) r[2]) * (1.0 + (double) r[3]);
  if (h < 0.0) h = 0.0;
  if (h > h0 + 20.0) h = h0 + 20.0;
  return (float) Math.sqrt(2.0 * g * h);
}}""", cls))
    cls.addMethod(CtNewMethod.make("""
public static float fallMultiplier(float[] r) {
  return clamp((1.0f + r[4]) * (1.0f + r[5]), 0.0f, 2.0f);
}""", cls))
    cls.addMethod(CtNewMethod.make("""
public static boolean near(float a, float b) {
  float m = Math.abs(b);
  if (m < 1.0f) m = 1.0f;
  return Math.abs(a - b) <= 0.001f * m;
}""", cls))
    cls.addMethod(CtNewMethod.make("""
public static boolean ownsFall(String mod) {
  try {
    Object o = bridge().putIfAbsent(OWNER_FALL, mod);
    return o == null || mod.equals(o);
  } catch (Throwable t) { return false; }
}""", cls))
    cls.addMethod(CtNewMethod.make("""
public static void releaseFall(String mod) {
  try { bridge().remove(OWNER_FALL, mod); } catch (Throwable t) { }
}""", cls))
    # ---- Movement 2 (rule 4b): the Jump_Height stat ride. Pure helpers first (a harness calls them without an engine) ----
    # The Armory's StatMultiplier.fromMaxima(assetMax, valueMax), copied from its 1.23.0 bytecode (read only, 2026-10-18)
    cls.addMethod(CtNewMethod.make("""
public static float theirMult(float assetMax, float valueMax) {
  if (!(assetMax > 0.0f)) return 1.0f;
  if (Math.abs(valueMax - assetMax) <= 1.0E-4f) return 1.0f;
  float m = 1.0f + valueMax / assetMax;
  if (Float.isNaN(m) || Float.isInfinite(m)) return 1.0f;
  return Math.max(0.0f, m);
}""", cls))
    # the engine's EntityStatValue.computeModifiers for one stat's max (VERIFIED bytecode): (asset + sum add) x (sum mul, if any)
    cls.addMethod(CtNewMethod.make("""
public static float statMax(float assetMax, float add, float mul, boolean hasMul) {
  float m = assetMax + add;
  if (hasMul) m = m * mul;
  return m;
}""", cls))
    # the ADDITIVE MAX amount that makes their multiplier = target, given every OTHER modifier (add / mul sums); NaN = cannot
    cls.addMethod(CtNewMethod.make("""
public static float rideAmount(float assetMax, float add, float mul, boolean hasMul, float target) {
  if (!(assetMax > 0.0f) || Float.isNaN(target) || Float.isInfinite(target) || target < 0.0f) return Float.NaN;
  float x = assetMax * (target - 1.0f);
  if (Math.abs(x - assetMax) <= 0.002f) x = assetMax + 0.004f;
  float a;
  if (hasMul) {
    if (Math.abs(mul) < 1.0E-6f) return Float.NaN;
    a = x / mul - assetMax - add;
  } else a = x - assetMax - add;
  if (Float.isNaN(a) || Float.isInfinite(a)) return Float.NaN;
  return a;
}""", cls))
    # (rideAmount: a target of exactly 2.0 would land on their "max equals the asset max = x1.0" gap - nudged by 0.04 %)
    # calibration step (state st, see sync): changed = this sync put a new amount; returns false once the player falls back
    cls.addMethod(CtNewMethod.make("""
public static boolean rideCheck(float[] st, boolean changed, float a, float live, float expect) {
  if (changed || Float.isNaN(st[10]) || !near(st[10], a)) { st[10] = a; st[9] = 1.0f; st[8] = 0.0f; return true; }
  if (near(live, expect)) { st[8] = 0.0f; st[1] = expect; st[9] = 1.0f; return true; }
  st[8] = st[8] + 1.0f;
  if (st[8] >= RIDE_FAILS) { st[9] = 2.0f; return false; }
  return true;
}""", cls))
    # rule 4 for one field: live == target -> 0 (strikes reset); paused -> 0; else 1 = write (strike counted), 2 = write + paused now
    cls.addMethod(CtNewMethod.make("""
public static int fieldStep(float[] st, int strikes, boolean atTarget) {
  if (atTarget) { st[strikes] = 0.0f; return 0; }
  if (st[strikes] >= 5.0f) return 0;
  st[strikes] = st[strikes] + 1.0f;
  return st[strikes] >= 5.0f ? 2 : 1;
}""", cls))
    cls.addMethod(CtNewMethod.make("""
public static boolean rideOn() {
  try { return !"yield".equals(bridge().get(CFG_RIDE)); } catch (Throwable t) { return true; }
}""", cls))
    # the Jump_Height stat index, -1 = no such stat asset (The Armory not loaded)
    cls.addMethod(CtNewMethod.make(f"""
public static int jumpStat() {{
  try {{
    {ALM} m = {ESTT}.getAssetMap();
    if (m == null) return -1;
    int i = m.getIndex(JUMP_STAT);
    return i < 0 ? -1 : i;
  }} catch (Throwable t) {{ return -1; }}
}}""", cls))
    cls.addMethod(CtNewMethod.make(f"""
public static void unride({ESM} esm, int ji) {{
  if (esm == null || ji < 0) return;
  try {{ if (esm.getModifier(ji, RIDE_KEY) != null) esm.removeModifier(ji, RIDE_KEY); }} catch (Throwable t) {{ }}
}}""", cls))
    # one sync of the ride: m = our jumpForce / default. Returns true = the jump is handled through the stat this sync
    cls.addMethod(CtNewMethod.make(f"""
public static boolean ride({ESM} esm, int ji, float m, float live, float def, float[] st) {{
  try {{
    {ESV} v = esm.get(ji);
    if (v == null) {{ esm.update(); v = esm.get(ji); }}          // the engine adds a new stat asset to the map on update() (The Armory does the same)
    {ESTT} t = ({ESTT}) {ESTT}.getAssetMap().getAsset(ji);
    if (t == null || !(t.getMax() > 0.0f)) {{ st[9] = 2.0f; return false; }}
    if (v == null) {{ st[8] = st[8] + 1.0f; if (st[8] >= RIDE_FAILS) {{ st[9] = 2.0f; return false; }} return true; }}          // not on this player yet: counts as a miss
    float am = t.getMax();
    float add = 0.0f;
    float mul = 0.0f;
    boolean hasMul = false;
    java.util.Map mods = v.getModifiers();
    if (mods != null) {{
      java.util.Iterator it = mods.keySet().iterator();
      while (it.hasNext()) {{
        Object k = it.next();
        if (RIDE_KEY.equals(k)) continue;
        Object o = mods.get(k);
        if (!(o instanceof {SMO})) continue;
        {SMO} sm = ({SMO}) o;
        if (sm.getTarget() != {MTG}.MAX) continue;
        if (sm.getCalculationType() == {CAL}.ADDITIVE) add = add + sm.getAmount();
        else if (sm.getCalculationType() == {CAL}.MULTIPLICATIVE) {{ hasMul = true; mul = mul + sm.getAmount(); }}
      }}
    }}
    float w = theirMult(am, statMax(am, add, mul, hasMul));
    if (near(m, 1.0f)) {{ unride(esm, ji); st[10] = Float.NaN; st[8] = 0.0f; st[9] = 1.0f; st[1] = def * w; return true; }}
    float a = rideAmount(am, add, mul, hasMul, w * m);
    if (Float.isNaN(a)) {{ st[9] = 2.0f; return false; }}
    {MODF} cur = esm.getModifier(ji, RIDE_KEY);
    boolean same = false;
    if (cur instanceof {SMO}) {{
      {SMO} cs = ({SMO}) cur;
      same = cs.getTarget() == {MTG}.MAX && cs.getCalculationType() == {CAL}.ADDITIVE && near(cs.getAmount(), a);
    }}
    if (!same) {{
      esm.putModifier(ji, RIDE_KEY, new {SMO}({MTG}.MAX, {CAL}.ADDITIVE, a));
      RIDES = RIDES + 1;
    }}
    float expect = def * theirMult(am, statMax(am, add + a, mul, hasMul));
    return rideCheck(st, !same, a, live, expect);
  }} catch (Throwable e) {{ st[9] = 2.0f; return false; }}
}}""", cls))
    # OUTSIDE THE PROTOCOL: loaded + enabled plugins that are known to write MovementSettings directly ("" = none); The Armory is
    # left out while the ride is on and its stat exists (rule 4b absorbs it)
    cls.addMethod(CtNewMethod.make(f"""
public static String findConflicts() {{
  StringBuilder b = new StringBuilder();
  boolean rides = rideOn() && jumpStat() >= 0;
  try {{
    java.util.List l = {PLM}.get().getPlugins();
    for (int i = 0; i < l.size(); i++) {{
      Object o = l.get(i);
      if (!(o instanceof {PLB})) continue;
      {PLB} p = ({PLB}) o;
      if (!p.isEnabled()) continue;
      {PID} id = p.getIdentifier();
      if (id == null) continue;
      String g = id.getGroup();
      String n = id.getName();
      for (int k = 0; k < KNOWN_NAME.length; k++) {{
        if (KNOWN_NAME[k].equals(n) && KNOWN_GROUP[k].equals(g)) {{
          if (rides && RIDE_NAME.equals(n) && RIDE_GROUP.equals(g)) continue;
          if (b.length() > 0) b.append("; ");
          b.append(g).append(":").append(n).append(" (").append(KNOWN_WHAT[k]).append(")");
        }}
      }}
    }}
  }} catch (Throwable t) {{ }}
  return b.toString();
}}""", cls))
    cls.addMethod(CtNewMethod.make(f"""
public static synchronized void checkConflicts(String mod) {{
  if (CONFLICTS_CHECKED) return;
  CONFLICTS_CHECKED = true;
  String c = findConflicts();
  CONFLICTS = c;
  if (c.length() > 0) {warn}(mod + ": these enabled plugins write MovementSettings.baseSpeed/jumpForce directly and do NOT speak the Skyy movement protocol: " + c + " - when one keeps resetting a player's speed or jump, that Skyy bonus pauses for that player (it wins; the other bonus keeps working). SkyWynn rule: do not enable them together with the Skyy movement mods");
}}""", cls))
    cls.addMethod(CtNewMethod.make("""
public static int pausedCount(java.util.concurrent.ConcurrentHashMap state) {
  int n = 0;
  try {
    java.util.Iterator it = state.values().iterator();
    while (it.hasNext()) {
      float[] a = (float[]) it.next();
      if (a != null && a.length > 6 && (a[2] >= 5.0f || a[6] >= 5.0f)) n = n + 1;
    }
  } catch (Throwable t) { }
  return n;
}""", cls))
    # the applier. state: uuid -> float[12]{lastWrittenSpeed, lastWrittenJump, speedStrikes, targetSpeed, targetJump, speedWarned,
    # jumpStrikes, jumpWarned, rideFails, rideState (0 not riding, 1 riding, 2 fell back), rideAmount (NaN none), rideWarned}
    cls.addMethod(CtNewMethod.make(f"""
public static void sync(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref, java.util.concurrent.ConcurrentHashMap state, String mod) {{
  if (!CONFLICTS_CHECKED) checkConflicts(mod);
  {MMG} mm = ({MMG}) cb.getComponent(ref, {MMG}.getComponentType());
  if (mm == null) return;
  {MSC} msc = ({MSC}) cb.getComponent(ref, {MSC}.getComponentType());
  if (msc != null) {{
    {MVT} ms = msc.getMovementStates();
    if (ms != null && ms.mounting) return;
  }}
  {MVS} s = mm.getSettings();
  {MVS} d = mm.getDefaultSettings();
  if (s == null || d == null || d.baseSpeed <= 0.0f) return;
  float[] r = sums(u);
  float ws = d.baseSpeed * speedFactor(r);
  float wj = jumpForce(r, d.jumpForce);
  float[] st = (float[]) state.get(u);
  if (st != null && st.length < 12) {{ state.remove(u); st = null; }}
  int ji = jumpStat();
  {ESM} esm = null;
  if (ji >= 0) esm = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());
  if (near(ws, d.baseSpeed) && near(wj, d.jumpForce)) {{
    unride(esm, ji);
    if (st == null) return;
    boolean sOurs = near(s.baseSpeed, st[0]) && !near(s.baseSpeed, d.baseSpeed);
    boolean jOurs = (st[9] < 0.5f || st[9] > 1.5f) && near(s.jumpForce, st[1]) && !near(s.jumpForce, d.jumpForce);
    if (sOurs) s.baseSpeed = d.baseSpeed;
    if (jOurs) s.jumpForce = d.jumpForce;
    if (sOurs || jOurs) mm.update(pr.getPacketHandler());
    state.remove(u);
    return;
  }}
  if (st == null) {{ st = new float[] {{ -1.0f, -1.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, Float.NaN, 0.0f }}; state.put(u, st); }}
  if (!near(st[3], ws)) {{ st[2] = 0.0f; st[3] = ws; }}
  if (!near(st[4], wj)) {{ st[6] = 0.0f; st[4] = wj; }}
  boolean write = false;
  boolean sAt = near(s.baseSpeed, ws);
  int sp = fieldStep(st, 2, sAt);
  if (sAt) st[0] = ws;
  if (sp > 0) {{ s.baseSpeed = ws; st[0] = ws; write = true; }}
  boolean jHandled = false;
  if (esm != null && st[9] < 1.5f && rideOn()) {{
    if (d.jumpForce > 0.0f && ride(esm, ji, wj / d.jumpForce, s.jumpForce, d.jumpForce, st)) jHandled = true;
    else {{
      unride(esm, ji);
      st[9] = 2.0f; st[10] = Float.NaN;
      FALLBACKS = FALLBACKS + 1;
      if (st[11] < 0.5f) {{
        st[11] = 1.0f;
        {warn}(mod + ": the " + JUMP_STAT + " stat ride did not give " + u + " the Skyy jump bonus " + (int) RIDE_FAILS + " checks in a row - this player's jump bonus falls back to direct writes (logged once per player; the speed bonus is not affected)");
      }}
    }}
  }} else if (esm != null) {{
    unride(esm, ji);
    if (st[9] > 0.5f && st[9] < 1.5f) {{ st[9] = 0.0f; st[10] = Float.NaN; st[8] = 0.0f; }}
  }}
  int jp = 0;
  if (!jHandled) {{
    boolean jAt = near(s.jumpForce, wj);
    jp = fieldStep(st, 6, jAt);
    if (jAt) st[1] = wj;
    if (jp > 0) {{ s.jumpForce = wj; st[1] = wj; write = true; }}
  }}
  if (write) mm.update(pr.getPacketHandler());
  boolean sNew = sp == 2 && st[5] < 0.5f;
  boolean jNew = jp == 2 && st[7] < 0.5f;
  if (sNew || jNew) {{
    String what = sNew ? (jNew ? "speed and jump bonus" : "speed bonus") : "jump bonus";
    if (sNew) st[5] = 1.0f;
    if (jNew) st[7] = 1.0f;
    String known = CONFLICTS;
    {warn}(mod + ": movement settings of " + u + " keep being reset by something outside the Skyy movement protocol - " + what + " paused for this player until that bonus changes (the other one keeps working; logged once per player and field; " + pausedCount(state) + " player(s) paused now" + (known != null && known.length() > 0 ? "; enabled direct writers: " + known : "") + ")");
  }}
}}""", cls))
    return fqn
