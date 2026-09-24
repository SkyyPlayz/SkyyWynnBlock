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
  4. Reset detection that works with several appliers: per player {lastWrittenSpeed, lastWrittenJump, strikes, targetSpeed,
     targetJump, warned}. Live value already equal to the target (whoever wrote it) -> strikes = 0, no write. Different -> write,
     strikes++. A NEW target (a source changed) resets strikes. 5 strikes in a row = something outside the protocol keeps resetting
     the settings -> pause until the target changes. The pause is logged ONCE PER PLAYER (warned flag in that player's state; it is
     forgotten with the state, i.e. when the player's total goes neutral or the player leaves), with the number of players paused
     right now and the known outside writers that are loaded (see OUTSIDE THE PROTOCOL). Two protocol appliers never strike each
     other because they compute the same target; a one-sync disagreement while a source is being replaced is healed on the next sync.
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
    ("LadyPaladra", "TheArmory", "JumpHeightModifierSystem: jumpForce"),
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
                 ("java.util.Map", "putIfAbsent"), ("java.util.Map", "remove")):
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
    # OUTSIDE THE PROTOCOL: loaded + enabled plugins that are known to write MovementSettings directly ("" = none)
    cls.addMethod(CtNewMethod.make(f"""
public static String findConflicts() {{
  StringBuilder b = new StringBuilder();
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
  if (c.length() > 0) {warn}(mod + ": these enabled plugins write MovementSettings.baseSpeed/jumpForce directly and do NOT speak the Skyy movement protocol: " + c + " - when one keeps resetting a player's movement, the Skyy speed/jump bonus pauses for that player (it wins). SkyWynn rule: do not enable them together with SkyySkills 0.2 / SkyyAccessories 0.3");
}}""", cls))
    cls.addMethod(CtNewMethod.make("""
public static int pausedCount(java.util.concurrent.ConcurrentHashMap state) {
  int n = 0;
  try {
    java.util.Iterator it = state.values().iterator();
    while (it.hasNext()) {
      float[] a = (float[]) it.next();
      if (a != null && a.length > 2 && a[2] >= 5.0f) n = n + 1;
    }
  } catch (Throwable t) { }
  return n;
}""", cls))
    # the applier. state: uuid -> float[]{lastWrittenSpeed, lastWrittenJump, strikes, targetSpeed, targetJump, warned}
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
  if (near(ws, d.baseSpeed) && near(wj, d.jumpForce)) {{
    if (st == null) return;
    boolean sOurs = near(s.baseSpeed, st[0]) && !near(s.baseSpeed, d.baseSpeed);
    boolean jOurs = near(s.jumpForce, st[1]) && !near(s.jumpForce, d.jumpForce);
    if (sOurs) s.baseSpeed = d.baseSpeed;
    if (jOurs) s.jumpForce = d.jumpForce;
    if (sOurs || jOurs) mm.update(pr.getPacketHandler());
    state.remove(u);
    return;
  }}
  if (st == null) {{ st = new float[] {{ -1.0f, -1.0f, 0.0f, 0.0f, 0.0f, 0.0f }}; state.put(u, st); }}
  if (!near(st[3], ws) || !near(st[4], wj)) {{ st[2] = 0.0f; st[3] = ws; st[4] = wj; }}
  if (near(s.baseSpeed, ws) && near(s.jumpForce, wj)) {{ st[0] = ws; st[1] = wj; st[2] = 0.0f; return; }}
  if (st[2] >= 5.0f) return;
  s.baseSpeed = ws;
  s.jumpForce = wj;
  mm.update(pr.getPacketHandler());
  st[0] = ws; st[1] = wj; st[2] = st[2] + 1.0f;
  if (st[2] >= 5.0f && st[5] < 0.5f) {{
    st[5] = 1.0f;
    String known = CONFLICTS;
    {warn}(mod + ": movement settings of " + u + " keep being reset by something outside the Skyy movement protocol - speed/jump bonus paused for this player until a bonus changes (logged once per player; " + pausedCount(state) + " player(s) paused now" + (known != null && known.length() > 0 ? "; enabled direct writers: " + known : "") + ")");
  }}
}}""", cls))
    return fqn
