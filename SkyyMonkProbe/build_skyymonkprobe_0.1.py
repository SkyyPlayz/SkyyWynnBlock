"""SkyyMonkProbe 0.1 - build script (javassist via jpype). Cloud draft (PR #11, research/cloud/Monk-Probe-Plan.md) turned into a working
local probe 2026-10-08: built against the installed HytaleServer.jar, harness SkyyMonkProbe/test_skyymonkprobe_0.1.py (executes every
code path on engine stand-ins). Not pinned in tools/deploy_set.py by this round (the local session pins it for ONE test session).
LOCAL FIXES vs the cloud draft (each checked against HytaleServer.jar bytecode / Assets.zip):
  1. probe hits use DamageCause.PHYSICAL (the melee cause; the draft's PROJECTILE + a plain EntitySource makes SkyyGear 0.2.9 look for a
     shot record and log "no launch record"); the re-dealt held FALL damage uses Damage.NULL_SOURCE + FALL = exactly what vanilla
     DamageSystems$FallDamagePlayers builds (no self-sourced damage, no PvP filter in the way).
  2. MINE (our own Damage objects) is an identity map (SkyyArmory ArmoryTrav.MINE's shape), not an equals/hashCode map.
  3. a ground jump whose 'jumping' flag reaches the server one tick AFTER onGround went false (<= 150 ms after take-off) counts as a
     ground jump (the draft took it for an air press, so that bound was missed).
  4. Skyy's open defaults kept: CROUCH also gives the free air jump (m3 and the vault's air jump; "m3 jump" = jump key only); slowfx
     defaults to the vanilla 'Slow' effect (Server/Entity/Effects/Status/Slow.json, HorizontalSpeedMultiplier 0.5, checked at build
     time) = the short slow if mobs cannot hang; the flowing fall keeps -15% fall damage whatever the slow fall does.
  5. enemy() = SkyyArmory ArmoryTrav.kind's enemy branch (kind 0: a live NPCEntity with an EntityStatMap, no DeathComponent; players,
     dead mobs and stat-less entities never) - the Monk build shares that one filter.
  6. a held FALL damage is forgiven only by a bound for THAT landing (boundFor: -150 .. +150 ms around its FALL event); the draft's
     'forgive' flag survived from the previous bound through the whole flight and forgave the next landing without a timed jump.
  7. one bound per LANDING (boundDone resets at the landing, not at take-off: the draft's chain never ended after a missed landing and
     a hidden landing never bounded); a hidden landing needs a fall first (wasFalling), so jump taps while rising are no extra bounds;
     the free air jump only counts edges more than 150 ms after take-off (the late ground-jump flag of fix 3 is no air jump).
REVIEW FIXES (2026-10-08, after the critics):
  R1. a probe hit (m5 / m6 / m7 PHYSICAL) never kills: capped at the target's Health - 1, skipped at <= 1 / unreadable Health (a lethal
      probe hit would be a real player kill = kill rewards to the op's profile that outlive the probe).
  R3. /mprobe stop with a held FALL damage pending ends every probe but settles that damage first (forgiven / re-dealt at 85 %), then
      clears the state. A world switch / disconnect inside the ~150 ms hold still drops it (the old world's entity is gone) - harmless.
  R4. a relog (the state's player ref no longer valid) drops the old state in the first tick instead of re-arming it.
  R5. the m4 window prints when its 30 s are over (m2 / m3 already did).
A THROWAWAY dev / test pack like SkyyGatherProbe / SkyyReelProbe: op-only commands, then (once accepted) pinned for ONE test
session and removed again. Nothing here is a feature; it only answers the Monk engine questions (research/cloud/Monk-Kit-Spec.md section 5,
the plan + test script: research/cloud/Monk-Probe-Plan.md) before the Monk class round depends on them.
Run:   python SkyyMonkProbe/build_skyymonkprobe_0.1.py   -> SkyyMonkProbe/SkyyMonkProbe-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
Check: python SkyyMonkProbe/test_skyymonkprobe_0.1.py    (-Xverify:all, every code path executed on engine stand-ins, permissions,
       start twice on a scratch copy of live data, engine-access audit)

SKYY'S LOCKS THE PROBES TEST (docs/answered/classes.md lines 34, 35, 39, 96, 128): the Bo staff Pole-Vault (lunge, vault up + forward, kick
2x a normal hit once per enemy, ~15% slower fall + 15% less fall damage), skipping bounds (jump right at landing, further the further you
fell, no fall damage on a timed landing, more Stamina than a jump), ONE free mid-air jump after the vault, the fist Rising Strike (uppercut
leap, knocked-up enemies, hang time, air hits fling them, CROUCH near the top = Plunge Punch dragging them down, no fall damage + NO
Acrobatics XP on the slam), physical traversals cost more Stamina than Mana, Flowing Form combo stacks (each 5 s, max 20).

NO ASSET OVERRIDDEN: the jar ships no item, block or language file at all (the kit hands out the two vanilla Bo staffs by id).
Every probe number below is a PROBE number (research/cloud/Monk-Kit-Spec.md section 3), not a balance decision.

THE PROBES (/mprobe, alias /monkprobe; op only: requirePermission skyymonkprobe.admin + no permission groups; every chat line is also
written to the server log as "[SkyyMonkProbe] ..."; state is memory only, per player, gone at a restart or a world change):
  kit          the vanilla Weapon_Staff_Bo_Wood + Weapon_Staff_Bo_Bamboo (storage first, nothing dropped)
  m1 <pct>     SLOW FALL: launches you 4.5 blocks straight up; from the top it sets your fall speed every tick to (1 - pct/100) x g x t
               (pct 0 = a vanilla fall, the baseline). Landing prints fall time vs the vanilla formula, the ratio, Sets sent, server us/tick.
  m1cap <bps>  SLOW FALL, cap way (SkyyArmory Levitate float): falling faster than <bps> is set back to <bps>.
  m2 [log]     JUMP AT LANDING (60 s): every landing / jump / crouch edge with ms timings, the fall height (our top-y and the engine's
               Player.getCurrentFallDistance), when the FALL damage event came. Without "log": SKIPPING BOUNDS run - a jump 0.25 s
               before to 0.10 s after a landing bounds you (5 + 0.5 per block fallen, cap +8, 1.4x jump height); every FALL damage in
               the chain is HELD 100 ms and forgiven on a timed bound, else re-dealt at 85 %.
  m3 [jump]    MID-AIR JUMP (30 s): logs every airborne jump / crouch / extraJumpsUsed edge; the first airborne JUMP or CROUCH edge
               ("jump": the JUMP key only) gives one free air jump (a normal jump's speed); the line says which key did it.
  m4 [pct]     FALL DAMAGE CANCEL (30 s): your FALL damage x pct/100 (default 0 = cancelled) in the Filter damage group; logs both amounts.
  m5 <kind>    PUSH: vault (4.5 up, 7 forward) | lunge (3 forward on the ground) | rise (6 up, 1.5 forward). Landing prints the
               measured distance / height / air time vs the target. The vault also arms the free air jump and the flowing fall.
  m6 [hit]     PATH SWEEP: a vault that kicks every enemy within 1.5 blocks of you on the way for 2 x hit (default 6), once per enemy.
  m7 [hit]     RISING STRIKE (covers m8 / m10 / m11): rise 6 + 1.5 forward; enemies in the 3 x 1.5 cone ahead take 1.2 x hit and are
               knocked up 5 blocks; at the top a 1.2 s hang (you and them ~held); your hits on them fling them 6 blocks; CROUCH near the
               top = PLUNGE (you + them down at 14 b/s, slam 1.0 x hit in 3 blocks, no fall damage, Acrobatics XP read before / after).
  m9 on|off    COSTS: vault 7 Stamina + 3 Mana, rise 8 + 4, bound 3 + 1 (Mana only with a Mana pool); too little = refused / chain ends.
  m12 [secs]   FLOWING FORM AURA (default 30 s): a 5-block scan every 1 s (enemies inside, scan cost) + your landed hits as combo stacks
               (each lasts 5 s, max 20).
  m13          the item in your hand (weapon or not) + the build-time desk read of the vanilla Bo staffs' interactions.
  slowfx [id]  applies the vanilla entity effect <id> (default Slow: 10 s, half walking speed) to every enemy within 5 blocks.
  xp           your Acrobatics XP now (SkyySkills skill:fn:xp).        stats   your probe counters.        stop   clears your probe state.

ENGINE PATHS (all from existing Skyy scripts - the plan cites file + line; nothing here is a new engine API except where marked):
  pushes / per-tick holds   Velocity.addInstruction(Vector3d, VelocityConfig, ChangeVelocityType.Set) - SkyySkills airJump, SkyyArmory
                            Leap / Levitate / Grapple (NPCs get the vanilla dagger dash VelocityConfig, read from Assets.zip like SkyyArmory)
  movement edges            MovementStatesComponent.getMovementStates(): onGround / jumping / crouching / extraJumpsUsed / rolling
  fall damage               DamageEventSystem in DamageModule.getFilterDamageGroup(), cause FALL (SkyyArmory GrappleFallSys, SkyySkills
                            AcroFallSys); hits seen in getInspectDamageGroup() (SkyySkills AcroFallSeenSys, SkyyArmory ArmoryHitSys)
  probe hits                DamageSystems.executeDamage(target, CommandBuffer, new Damage(new Damage$EntitySource(you), cause, amount))
                            (SkyyArmory ArmoryTrav.hit's shape; cause PHYSICAL = the melee cause; a held fall: NULL_SOURCE + FALL)
  area / look               TargetUtil.getAllEntitiesInSphere / TargetUtil.getLook (SkyyArmory)
  costs                     EntityStatMap.subtractStatValue on DefaultEntityStatTypes.getStamina() / getMana() (SkyyArmory Leap.take)
  NEW (no Skyy script does it yet): holding a MOB in mid-air with a per-tick Set (the grapple yank only drags mobs along the ground), a
  vanilla slow effect on a mob (slowfx 'Slow' on an NPC: UNVERIFIED in game), re-dealing a held FALL damage (vanilla's own shape).
"""
import sys, os, json, zipfile, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

if "--deploy" in sys.argv:
    raise SystemExit("SkyyMonkProbe: --deploy is not supported here - deploys go through tools/deploy_set.py")

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
NODE = "skyymonkprobe.admin"
BO_IDS = ["Weapon_Staff_Bo_Wood", "Weapon_Staff_Bo_Bamboo"]     # vanilla (docs/answered/classes.md; research/cloud/Monk-Kit-Spec.md)

# ================= the probe numbers (research/cloud/Monk-Kit-Spec.md section 3; probe values, not balance) =================
N = {
    "VAULT_UP": 4.5, "VAULT_FWD": 7.0, "LUNGE_FWD": 3.0, "RISE_UP": 6.0, "RISE_FWD": 1.5,
    "FLOW": 0.15,                         # flowing fall: 15 % slower, 15 % less fall damage
    "B_BEFORE": 250, "B_AFTER": 100,      # the timed-landing window, ms
    "B_BASE": 5.0, "B_PER": 0.5, "B_CAP": 8.0, "B_HEIGHT": 1.4,
    "KNOCK_UP": 5.0, "HANG_MS": 1200, "HANG_VY": -1.0, "FLING": 12.0, "PLUNGE": 14.0, "SLAM_R": 3.0,
    "CONE_LEN": 3.0, "CONE_HALF": 0.75, "SWEEP_R": 1.5, "AURA_R": 5.0, "COMBO_MS": 5000, "COMBO_MAX": 20,
    "C_VAULT_S": 7.0, "C_VAULT_M": 3.0, "C_RISE_S": 8.0, "C_RISE_M": 4.0, "C_BOUND_S": 3.0, "C_BOUND_M": 1.0,
    "HIT": 6.0,                            # the probe's "normal Bo hit" (the Bo combo average is about 6.3)
}

az = zipfile.ZipFile(ASSETS)
AZ_NAMES = set(az.namelist())
ITEM_PATH = dict((n.rsplit("/", 1)[1][:-5], n) for n in AZ_NAMES if n.startswith("Server/Item/Items/") and n.endswith(".json"))


def vanilla_json(path):
    return json.loads(az.read(path).decode("utf-8-sig"))


for _i in BO_IDS:
    if _i not in ITEM_PATH:
        raise SystemExit("vanilla item %s not in Assets.zip - research/cloud/Monk-Kit-Spec.md names it" % _i)

# ---- probe 13 (desk read at build time): what the vanilla Bo staffs carry (interactions, charging), printed + shipped as one text line
def charg_strings(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if "harg" in str(k):
                out.add(str(k))
            charg_strings(v, out)
    elif isinstance(o, list):
        for v in o:
            charg_strings(v, out)
    elif isinstance(o, str) and "harg" in o:
        out.add(o)


BO_DESK = []
for _i in BO_IDS:
    _d = vanilla_json(ITEM_PATH[_i])
    _inter = _d.get("Interactions") or {}
    _vars = _d.get("InteractionVars") or {}
    _ch = set()
    charg_strings(_d, _ch)
    _line = "%s: Parent %s, PlayerAnimationsId %s, Weapon %s, Interactions %s, InteractionVars %s, 'charg' strings %s" % (
        _i, _d.get("Parent", "-"), _d.get("PlayerAnimationsId", "-"), "yes" if "Weapon" in _d else "no",
        sorted(_inter) if isinstance(_inter, dict) else _inter, sorted(_vars) if isinstance(_vars, dict) else "-",
        sorted(_ch) if _ch else "none")
    print("M13 desk read:", _line)
    BO_DESK.append(re.sub(r"[^\x20-\x7e]", "?", _line)[:600])

# ---- the vanilla dagger dash's VelocityConfig (what SkyyArmory gives NPC Velocity Sets; values read here, never copied into the repo)
_dash = sorted(n for n in AZ_NAMES if n.startswith("Server/") and n.endswith("/Daggers_Dash_Backward.json"))
if len(_dash) != 1:
    raise SystemExit("Daggers_Dash_Backward.json not found once in Assets.zip: %r" % _dash)
_dash_i = vanilla_json(_dash[0])["Interactions"][0]
DASH = _dash_i.get("VelocityConfig")
if _dash_i.get("Type") != "ApplyForce" or not isinstance(DASH, dict) or \
        sorted(DASH) != sorted(["AirResistance", "AirResistanceMax", "GroundResistance", "GroundResistanceMax", "Threshold", "Style"]):
    raise SystemExit("Daggers_Dash_Backward changed shape: %r - re-check the NPC push config (SkyyArmory ArmoryTrav.dash)" % _dash_i)
SLOW_ID = "Slow"      # Server/Entity/Effects/Status/Slow.json (asset id = file name): the "short slow if mobs cannot hang" default
_slow = sorted(n for n in AZ_NAMES if n.startswith("Server/Entity/Effects/") and n.endswith("/" + SLOW_ID + ".json"))
if len(_slow) != 1 or "HorizontalSpeedMultiplier" not in (vanilla_json(_slow[0]).get("ApplicationEffects") or {}):
    raise SystemExit("vanilla entity effect %s (a slow) not found once in Assets.zip: %r" % (SLOW_ID, _slow))
print("assets: none shipped; kit %s; NPC push config from %s; slowfx default %s" % (BO_IDS, _dash[0], _slow[0]))

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.monkprobe"
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "AC": "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IST": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "ITM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "CAC": "com.hypixel.hytale.component.ComponentAccessor",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "SG": "com.hypixel.hytale.component.SystemGroup",
    "DES": "com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem",
    "DMOD": "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
    "DMG": "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
    "DSRC": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$Source",
    "DENT": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource",
    "DCS": "com.hypixel.hytale.server.core.modules.entity.damage.DamageCause",
    "DSYS": "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems",
    "MSC": "com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent",
    "MVT": "com.hypixel.hytale.protocol.MovementStates",
    "MMG": "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementManager",
    "MVS": "com.hypixel.hytale.protocol.MovementSettings",
    "PHC": "com.hypixel.hytale.server.core.modules.physics.util.PhysicsConstants",
    "VEL": "com.hypixel.hytale.server.core.modules.physics.component.Velocity",
    "VCF": "com.hypixel.hytale.server.core.modules.splitvelocity.VelocityConfig",
    "CVT": "com.hypixel.hytale.protocol.ChangeVelocityType",
    "VTS": "com.hypixel.hytale.protocol.VelocityThresholdStyle",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "V3D": "org.joml.Vector3d",
    "TU": "com.hypixel.hytale.server.core.util.TargetUtil",
    "XFM": "com.hypixel.hytale.math.vector.Transform",
    "NPC": "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "DTH": "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "ECC": "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent",
    "EFX": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect",
    "ILT": "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap",
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
for c, m in ((T["AC"], "requirePermission"), (T["AC"], "setPermissionGroups"), (T["AC"], "addAliases"), (T["AC"], "addUsageVariant"),
             (T["AC"], "withRequiredArg"), (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["PR"], "getUuid"), (T["PR"], "getComponentType"), (T["MSG"], "raw"), (T["PLA"], "getComponentType"),
             (T["PLA"], "getCurrentFallDistance"), (T["INVC"], "getCombined"), (T["INVC"], "STORAGE_HOTBAR_BACKPACK"),
             (T["INVC"], "getItemInHand"), (T["IC"], "addItemStack"), (T["IS"], "getItemId"), (T["IS"], "isEmpty"), (T["IS"], "getQuantity"),
             (T["IS"], "getItem"), (T["IST"], "succeeded"), (T["IST"], "getRemainder"), (T["ITM"], "getWeapon"),
             (T["ESM"], "getComponentType"), (T["ESM"], "get"), (T["ESM"], "subtractStatValue"), (T["ESV"], "get"), (T["ESV"], "getMax"),
             (T["DST"], "getStamina"), (T["DST"], "getMana"), (T["DST"], "getHealth"), (T["ETS"], "tick"), (T["ETS"], "isParallel"), (T["ACH"], "getReferenceTo"),
             (T["DMOD"], "get"), (T["DMOD"], "getFilterDamageGroup"), (T["DMOD"], "getInspectDamageGroup"), (T["DMG"], "getCause"),
             (T["DMG"], "getAmount"), (T["DMG"], "setAmount"), (T["DMG"], "isCancelled"), (T["DMG"], "setCancelled"), (T["DMG"], "getSource"),
             (T["DCS"], "FALL"), (T["DCS"], "PHYSICAL"), (T["DMG"], "NULL_SOURCE"), (T["DCS"], "getId"), (T["DSYS"], "executeDamage"),
             ("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource", "getRef"),
             (T["MSC"], "getComponentType"), (T["MSC"], "getMovementStates"), (T["MVT"], "onGround"), (T["MVT"], "jumping"),
             (T["MVT"], "crouching"), (T["MVT"], "extraJumpsUsed"), (T["MVT"], "rolling"), (T["MVT"], "mounting"),
             (T["MMG"], "getComponentType"), (T["MMG"], "getSettings"), (T["MVS"], "jumpForce"), (T["PHC"], "GRAVITY_ACCELERATION"),
             (T["VEL"], "getComponentType"), (T["VEL"], "addInstruction"), (T["VEL"], "getClientVelocity"), (T["CVT"], "Set"),
             (T["VCF"], "setAirResistance"), (T["VCF"], "setAirResistanceMax"), (T["VCF"], "setGroundResistance"),
             (T["VCF"], "setGroundResistanceMax"), (T["VCF"], "setThreshold"), (T["VCF"], "setStyle"),
             (T["TC"], "getComponentType"), (T["TC"], "getPosition"), (T["TU"], "getAllEntitiesInSphere"), (T["TU"], "getLook"),
             (T["XFM"], "getDirection"), (T["XFM"], "getPosition"), (T["NPC"], "getComponentType"), (T["DTH"], "getComponentType"),
             (T["ECC"], "getComponentType"), (T["ECC"], "addEffect"), (T["EFX"], "getAssetMap"), (T["ILT"], "getIndex"), (T["ILT"], "getAsset"),
             ("com.hypixel.hytale.component.Ref", "isValid"), (PB, "getCommandRegistry"), (PB, "getEntityStoreRegistry"), (PB, "getLogger"),
             (PB, "shutdown")):
    B.probe(pool, c, m)
# exact signatures of the calls whose shape matters most (a re-typed parameter stops the build, not the test session)
_V = "L" + T["V3D"].replace(".", "/") + ";"
for c, m, d in ((T["VEL"], "addInstruction", "(" + _V + "L" + T["VCF"].replace(".", "/") + ";L" + T["CVT"].replace(".", "/") + ";)V"),
                (T["TU"], "getAllEntitiesInSphere", "(" + _V + "DL" + T["CAC"].replace(".", "/") + ";)Ljava/util/List;"),
                (T["DSYS"], "executeDamage", "(L" + T["REF"].replace(".", "/") + ";L" + T["CB"].replace(".", "/") + ";L" + T["DMG"].replace(".", "/") + ";)V"),
                (T["ESM"], "subtractStatValue", "(IF)F"), (T["PLA"], "getCurrentFallDistance", "()D")):
    try:
        pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))

TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def mk(name, sup=None):
    return pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)


def jl(s):
    return json.dumps(s)          # a Java string literal (ASCII text only here)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(jl(x) for x in xs)


def jd(v):
    return repr(float(v))         # a Java double literal


# ---- MpLog: server log + chat. SINK (harness hook, null in game) also receives every chat line.
log = mk("MpLog")
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.List SINK;")
M(log, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyMonkProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyMonkProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void tell(@PR@ pr, String s) {
  info((pr == null ? "" : "to " + pr.getUsername() + ": ") + s);
  try { if (SINK != null) SINK.add(s); } catch (Throwable t) { }
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[MonkProbe] " + s)); } catch (Throwable t) { }
}""")

# ---- MpLogic: pure functions (no engine objects) - the harness calls them directly
lg = mk("MpLogic")
# launch speed for a height h under gravity g (no drag): sqrt(2 g h)
M(lg, r"""
public static double vyFor(double h, double g) {
  if (!(h > 0.0) || !(g > 0.0)) return 0.0;
  return Math.sqrt(2.0 * g * h);
}""")
# ground-to-ground air time of a launch vy (no drag)
M(lg, r"""
public static double airTime(double vy, double g) {
  if (!(vy > 0.0) || !(g > 0.0)) return 0.0;
  return 2.0 * vy / g;
}""")
# the horizontal speed that covers dist during that air time
M(lg, r"""
public static double hSpeed(double dist, double vy, double g) {
  double t = airTime(vy, g);
  if (!(t > 0.0) || !(dist > 0.0)) return 0.0;
  return dist / t;
}""")
# skipping bound distance: base + perBlock x blocks fallen, the extra capped
M(lg, r"""
public static double boundDist(double base, double per, double cap, double fell) {
  double e = fell > 0.0 ? fell * per : 0.0;
  if (e > cap) e = cap;
  return base + e;
}""")
# a press at 'press' ms is timed for a landing at 'land' ms: from 'before' ms before to 'after' ms after (0 = no such event)
M(lg, r"""
public static boolean timed(long land, long press, long before, long after) {
  if (land <= 0L || press <= 0L) return false;
  long d = press - land;
  return d >= 0L - before && d <= after;
}""")
# analytic slow fall: the speed t ms after the top under (1 - pct) x g (never upward)
M(lg, r"""
public static double slowVy(double pct, double g, long ms) {
  if (ms <= 0L) return 0.0;
  double f = 1.0 - pct;
  if (f < 0.0) f = 0.0;
  if (f > 1.0) f = 1.0;
  return 0.0 - f * g * ((double) ms / 1000.0);
}""")
# the cap way: falling faster than cap -> cap; anything else unchanged (NaN = no reading = unchanged)
M(lg, r"""
public static double capVy(double cvy, double cap) {
  if (cvy != cvy || !(cap > 0.0)) return cvy;
  if (cvy < 0.0 - cap) return 0.0 - cap;
  return cvy;
}""")
# expected fall-time ratio slow / vanilla for a gravity scaled by (1 - pct): 1 / sqrt(1 - pct)
M(lg, r"""
public static double expectRatio(double pct) {
  if (!(pct > 0.0) || pct >= 1.0) return 1.0;
  return 1.0 / Math.sqrt(1.0 - pct);
}""")
# the vanilla (no drag) fall time in ms for a drop of h blocks
M(lg, r"""
public static double fallMs(double h, double g) {
  if (!(h > 0.0) || !(g > 0.0)) return 0.0;
  return Math.sqrt(2.0 * h / g) * 1000.0;
}""")
# target offset (ox, oz) from the caster, look (lx, lz) a horizontal unit vector: in front 0..len and at most half to the side
M(lg, r"""
public static boolean inCone(double ox, double oz, double lx, double lz, double len, double half) {
  double f = ox * lx + oz * lz;
  if (f < 0.0 || f > len) return false;
  double s = ox * (0.0 - lz) + oz * lx;
  if (s < 0.0) s = 0.0 - s;
  return s <= half;
}""")
# combo stacks: drop every stamp (Long ms) at least 'life' ms old; the stacks left, at most max
M(lg, r"""
public static int prune(java.util.ArrayList l, long now, long life, int max) {
  if (l == null) return 0;
  for (int i = l.size() - 1; i >= 0; i--) {
    Long t = (Long) l.get(i);
    if (t == null || now - t.longValue() >= life) l.remove(i);
  }
  while (l.size() > max) l.remove(0);
  return l.size();
}""")
M(lg, r"""
public static String f1(double v) {
  if (v != v) return "?";
  long t = Math.round(v * 10.0);
  String sign = t < 0L ? "-" : "";
  if (t < 0L) t = 0L - t;
  return sign + (t / 10L) + "." + (t % 10L);
}""")
# "PASS" when got is within tol (a fraction) of want, else "OFF"; with the numbers
M(lg, r"""
public static String verdict(double got, double want, double tol) {
  if (!(want > 0.0)) return "n/a (" + f1(got) + ")";
  double r = got / want;
  double d = r - 1.0;
  if (d < 0.0) d = 0.0 - d;
  return (d <= tol ? "PASS" : "OFF") + " (" + f1(got) + " vs " + f1(want) + ", " + Math.round(r * 100.0) + "%)";
}""")
M(lg, r"""
public static int number(String s, int dflt, int lo, int hi) {
  int n = dflt;
  try { n = Integer.parseInt(s == null ? "" : s.trim()); } catch (Throwable t) { n = dflt; }
  if (n < lo) n = lo;
  if (n > hi) n = hi;
  return n;
}""")
M(lg, r"""
public static double dnum(String s, double dflt, double lo, double hi) {
  double n = dflt;
  try { n = Double.parseDouble(s == null ? "" : s.trim()); } catch (Throwable t) { n = dflt; }
  if (n != n) n = dflt;
  if (n < lo) n = lo;
  if (n > hi) n = hi;
  return n;
}""")

# ---- MpState: one player's probe state (world thread only; one per player in MpCmds.STATES)
sta = mk("MpState")
for f in ("public java.util.UUID u;", "public @REF@ ref;", "public @ST@ st;",
          # movement edges (every tick)
          "public boolean prevGround;", "public boolean prevJump;", "public boolean prevCrouch;", "public int prevXj;",
          "public double airTopY;", "public double fallMax;", "public long leftAt;", "public long lastLand;", "public double landFell;",
          "public long airPress;", "public long lastFallAt;", "public double lastFallAmt;", "public int fallEvents;",
          # pending push: 0 none, 1 vault, 2 lunge, 3 rise, 4 m1 launch
          "public int pend;",
          # m1 slow fall: mode 0 off, 1 analytic, 2 cap
          "public int m1Mode;", "public double m1Val;", "public int m1Phase;", "public long m1Top;", "public double m1TopY;", "public long m1Sets;",
          "public double m1MinVy;",
          # m2 / m3
          "public long logUntil;", "public boolean chain;", "public boolean boundDone;", "public int bounds;", "public long lastBoundAt;", "public boolean wasFalling;",
          "public double pendFall;", "public long pendFallAt;", "public long airUntil;", "public boolean airCrouch;", "public boolean airUsed;",
          # m4 / flowing fall
          "public long fallUntil;", "public double fallPct;", "public long noFallUntil;", "public boolean flowFall;", "public long flowTop;",
          # a push makes the client's reported speed stale for a few ticks: a top only counts once the client has been seen RISING
          "public long flowArm;", "public boolean flowRose;", "public boolean m1Rose;", "public boolean rsRose;",
          # flight tracking (m5 / m6 / m7)
          "public int fl;", "public String flKind;", "public double fx0;", "public double fy0;", "public double fz0;", "public double fTop;",
          "public long fT0;", "public boolean fLeft;", "public double fWantD;", "public double fWantH;",
          # m6 sweep
          "public boolean sweep;", "public double hitAmt;", "public java.util.HashSet kicked;",
          # m7 rising strike: 0 none, 1 rising, 2 hang, 3 plunge, 4 falling
          "public int rs;", "public long rsT;", "public long rsApex;", "public java.util.ArrayList ups;", "public double rsMinY;", "public double rsMaxY;",
          "public long xpBefore;", "public long xpAt;", "public int flings;",
          # m9 costs
          "public boolean costs;",
          # /mprobe stop with a held FALL damage pending: the tick settles it, then drops the state (REVIEW FIX 3)
          "public boolean quit;",
          # m12 aura
          "public long auraUntil;", "public long auraNext;", "public java.util.ArrayList stamps;", "public int combo;", "public int hitsSeen;",
          "public long auraNs;", "public long auraNsMax;", "public int auraScans;",
          # timing of this probe's own tick work
          "public long ns;", "public long nsMax;", "public long ticks;", "public long sets;"):
    F(sta, f)
C(sta, r"""
public MpState(java.util.UUID u, @REF@ r, @ST@ st) {
  this.u = u;
  this.ref = r;
  this.st = st;
  this.prevGround = true;
  this.kicked = new java.util.HashSet();
  this.ups = new java.util.ArrayList();
  this.stamps = new java.util.ArrayList();
  this.flKind = "";
  this.m1MinVy = 0.0;
}""")

# ---- MpCmds: engine glue + every probe (world thread: AbstractPlayerCommand.execute, the tick and the damage systems)
cmds = mk("MpCmds")
F(cmds, "public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();")
F(cmds, "public static final java.util.Map MINE = java.util.Collections.synchronizedMap(new java.util.IdentityHashMap());")
F(cmds, "public static final String SLOW_ID = %s;" % jl(SLOW_ID))
F(cmds, "public static final String[] KIT = %s;" % jarr(BO_IDS))
F(cmds, "public static final String[] BO_DESK = %s;" % jarr(BO_DESK))
F(cmds, "public static volatile @VCF@ DASH = null;")
for k, v in sorted(N.items()):
    F(cmds, "public static final double %s = %s;" % (k, jd(v)))
M(cmds, r"""
public static void tell(@PR@ pr, String s) { @PKG@.MpLog.tell(pr, s); }""")
M(cmds, r"""
public static String f1(double v) { return @PKG@.MpLogic.f1(v); }""")
# the probe clock: wall time in game; CLOCK is a harness seam only (0 = never set outside the harness)
F(cmds, "public static volatile long CLOCK = 0L;")
M(cmds, r"""
public static long now() { long c = CLOCK; return c != 0L ? c : System.currentTimeMillis(); }""")
M(cmds, r"""
public static java.util.Map bridge() {
  Object b = System.getProperties().get("skyy.bridge");
  if (b instanceof java.util.Map) return (java.util.Map) b;
  return java.util.Collections.EMPTY_MAP;
}""")
M(cmds, r"""
public static @PR@ prOf(@CAC@ acc, @REF@ r) {
  try { if (r == null || !r.isValid()) return null; return (@PR@) acc.getComponent(r, @PR@.getComponentType()); } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static @V3D@ pos(@CAC@ acc, @REF@ r) {
  try {
    @TC@ tc = (@TC@) acc.getComponent(r, @TC@.getComponentType());
    return tc == null ? null : tc.getPosition();
  } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static @MVT@ moves(@CAC@ acc, @REF@ r) {
  try {
    @MSC@ c = (@MSC@) acc.getComponent(r, @MSC@.getComponentType());
    return c == null ? null : c.getMovementStates();
  } catch (Throwable t) { return null; }
}""")
# the client's own velocity (what FallDamagePlayers reads); null = unreadable
M(cmds, r"""
public static double[] cvel(@CAC@ acc, @REF@ r) {
  try {
    @VEL@ v = (@VEL@) acc.getComponent(r, @VEL@.getComponentType());
    @V3D@ c = v == null ? null : v.getClientVelocity();
    if (c == null) return null;
    return new double[] { c.x, c.y, c.z };
  } catch (Throwable t) { return null; }
}""")
# the vanilla dagger dash's push feel - SkyyArmory gives it to every NPC Velocity Set ("like a knockback")
M(cmds, (r"""
public static @VCF@ dash() {
  @VCF@ c = DASH;
  if (c != null) return c;
  try {
    c = new @VCF@();
    c.setAirResistance(AIRf);
    c.setAirResistanceMax(AIRMAXf);
    c.setGroundResistance(GROUNDf);
    c.setGroundResistanceMax(GROUNDMAXf);
    c.setThreshold(THRESf);
    c.setStyle(@VTS@.STYLE);
    DASH = c;
    return c;
  } catch (Throwable t) { @PKG@.MpLog.warn("dash config failed: " + t); return null; }
}""").replace("AIRMAXf", repr(float(DASH["AirResistanceMax"])) + "f").replace("AIRf", repr(float(DASH["AirResistance"])) + "f")
      .replace("GROUNDMAXf", repr(float(DASH["GroundResistanceMax"])) + "f").replace("GROUNDf", repr(float(DASH["GroundResistance"])) + "f")
      .replace("THRESf", repr(float(DASH["Threshold"])) + "f").replace("STYLE", str(DASH["Style"])))
# one Velocity Set (players: no config, like SkyySkills' air jump and SkyyArmory's hang; NPCs: the dash config, like the grapple yank)
M(cmds, r"""
public static boolean setVel(@CAC@ acc, @REF@ r, double x, double y, double z, boolean npc) {
  try {
    if (r == null || !r.isValid()) return false;
    @VEL@ v = (@VEL@) acc.getComponent(r, @VEL@.getComponentType());
    if (v == null) return false;
    @VCF@ cf = null;
    if (npc) cf = dash();
    v.addInstruction(new @V3D@(x, y, z), cf, @CVT@.Set);
    return true;
  } catch (Throwable t) { @PKG@.MpLog.warn("a velocity Set failed: " + t); return false; }
}""")
M(cmds, r"""
public static double grav() {
  try { double g = (double) @PHC@.GRAVITY_ACCELERATION; if (g > 0.0) return g; } catch (Throwable t) { }
  return 32.0;
}""")
M(cmds, r"""
public static double jumpForce(@CAC@ acc, @REF@ r) {
  try {
    @MMG@ mm = (@MMG@) acc.getComponent(r, @MMG@.getComponentType());
    @MVS@ s = mm == null ? null : mm.getSettings();
    if (s != null && s.jumpForce > 0.0f) return (double) s.jumpForce;
  } catch (Throwable t) { }
  return 11.8;
}""")
M(cmds, r"""
public static double fallDist(@CAC@ acc, @REF@ r) {
  try {
    @PLA@ p = (@PLA@) acc.getComponent(r, @PLA@.getComponentType());
    return p == null ? 0.0 : p.getCurrentFallDistance();
  } catch (Throwable t) { return 0.0; }
}""")
# where you look: {eye x, y, z, dir x, y, z, horizontal unit x, z} (TargetUtil.getLook, what SkyyArmory aims with); null = unreadable
M(cmds, r"""
public static double[] look(@CAC@ acc, @REF@ r) {
  try {
    @XFM@ lk = @TU@.getLook(r, acc);
    if (lk == null || lk.getPosition() == null || lk.getDirection() == null) return null;
    @V3D@ e = lk.getPosition();
    @V3D@ d = lk.getDirection();
    double hl = Math.sqrt(d.x * d.x + d.z * d.z);
    double hx = hl > 1.0E-4 ? d.x / hl : 0.0;
    double hz = hl > 1.0E-4 ? d.z / hl : 1.0;
    return new double[] { e.x, e.y, e.z, d.x, d.y, d.z, hx, hz };
  } catch (Throwable t) { return null; }
}""")
# THE SHARED ENEMY FILTER (note for the Monk build): the same rule as SkyyArmory ArmoryTrav.kind == 0 (an enemy) - a live NPCEntity
# with an EntityStatMap and no DeathComponent; players (any), dead mobs and stat-less entities are never hit / held / counted.
M(cmds, r"""
public static boolean enemy(@CAC@ acc, @REF@ t, @REF@ self) {
  try {
    if (t == null || !t.isValid() || t.equals(self)) return false;
    if (acc.getComponent(t, @DTH@.getComponentType()) != null) return false;
    return acc.getComponent(t, @NPC@.getComponentType()) != null && acc.getComponent(t, @ESM@.getComponentType()) != null;
  } catch (Throwable t2) { return false; }
}""")
M(cmds, r"""
public static java.util.List near(@CAC@ acc, double x, double y, double z, double r) {
  try {
    java.util.List l = @TU@.getAllEntitiesInSphere(new @V3D@(x, y, z), r, acc);
    return l == null ? new java.util.ArrayList() : new java.util.ArrayList(l);
  } catch (Throwable t) { @PKG@.MpLog.warn("area query failed: " + t); return new java.util.ArrayList(); }
}""")
# a target's Health now; -1 = unreadable (no stat map / no Health stat)
M(cmds, r"""
public static double hpOf(@CAC@ acc, @REF@ t) {
  try {
    @ESM@ m = (@ESM@) acc.getComponent(t, @ESM@.getComponentType());
    int hi = @DST@.getHealth();
    @ESV@ hv = m == null || hi < 0 ? null : m.get(hi);
    return hv == null ? -1.0 : (double) hv.get();
  } catch (Throwable x) { return -1.0; }
}""")
# one probe hit through the whole damage pipeline, MINE-marked: a melee probe hit = Damage$EntitySource(you) + PHYSICAL (SkyyArmory
# ArmoryTrav.hit's shape, the melee cause); a re-dealt held fall = Damage.NULL_SOURCE + FALL (vanilla DamageSystems$FallDamagePlayers)
M(cmds, r"""
public static boolean hit(@CB@ buf, @REF@ target, @REF@ src, double amount, boolean fall) {
  try {
    if (!(amount > 0.0) || target == null || !target.isValid() || src == null || !src.isValid()) return false;
    // REVIEW FIX 1: a probe hit NEVER kills (a kill would pay real kill rewards - SkyyCollections / SkyyMobs / SkyyEssentials kill
    // hooks - to the op's profile): capped at the target's Health - 1, none at all at <= 1 Health or an unreadable Health. Only the
    // re-dealt held FALL (vanilla's own fall shape, already 85 % of a fall the game was dealing anyway) is left uncapped.
    if (!fall) {
      double hp = hpOf(buf, target);
      if (!(hp > 1.0)) { @PKG@.MpLog.info("probe hit skipped: target Health " + f1(hp) + " (probe hits never kill)"); return false; }
      if (amount > hp - 1.0) { @PKG@.MpLog.info("probe hit capped " + f1(amount) + " -> " + f1(hp - 1.0) + " (Health " + f1(hp) + ": probe hits never kill)"); amount = hp - 1.0; }
    }
    @DCS@ cause = fall ? @DCS@.FALL : @DCS@.PHYSICAL;
    if (cause == null) return false;
    @DSRC@ from = fall ? @DMG@.NULL_SOURCE : (@DSRC@) new @DENT@(src);
    @DMG@ d = new @DMG@(from, cause, (float) amount);
    if (MINE.size() > 4096) MINE.clear();
    MINE.put(d, Boolean.TRUE);
    @DSYS@.executeDamage(target, buf, d);
    return true;
  } catch (Throwable t) { @PKG@.MpLog.warn("a probe hit failed: " + t); return false; }
}""")
M(cmds, r"""
public static String statText(@CAC@ acc, @REF@ r) {
  try {
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m == null) return "no stats";
    @ESV@ s = m.get(@DST@.getStamina());
    @ESV@ n = m.get(@DST@.getMana());
    return "Stamina " + (s == null ? "-" : f1((double) s.get()) + "/" + f1((double) s.getMax())) + ", Mana " + (n == null ? "-" : f1((double) n.get()) + "/" + f1((double) n.getMax()));
  } catch (Throwable t) { return "stats unreadable"; }
}""")
# the cost (SkyyArmory Leap.take's rules): 1 = paid (or unreadable: never blocks), 0 = too little (nothing taken); Mana only with a Mana pool
M(cmds, r"""
public static int take(@CAC@ acc, @REF@ r, double stam, double mana) {
  try {
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m == null) return 1;
    int si = @DST@.getStamina();
    int mi = @DST@.getMana();
    @ESV@ sv = null;
    @ESV@ mv = null;
    if (si >= 0) sv = m.get(si);
    if (mi >= 0) mv = m.get(mi);
    boolean useMana = mana > 0.0 && mv != null && mv.getMax() > 0.0f;
    if (stam > 0.0 && sv != null && (double) sv.get() + 1.0E-4 < stam) return 0;
    if (useMana && (double) mv.get() + 1.0E-4 < mana) return 0;
    if (stam > 0.0 && sv != null) m.subtractStatValue(si, (float) stam);
    if (useMana) m.subtractStatValue(mi, (float) mana);
    return 1;
  } catch (Throwable t) { @PKG@.MpLog.warn("cost unreadable: " + t); return 1; }
}""")
# SkyySkills skill:fn:xp {UUID, "Acrobatics"} -> Long (the active profile's total); -1 = no SkyySkills / no answer
M(cmds, r"""
public static long acroXp(java.util.UUID u) {
  try {
    Object f = bridge().get("skill:fn:xp");
    if (!(f instanceof java.util.function.Function)) return -1L;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, "Acrobatics" });
    if (r instanceof Number) return ((Number) r).longValue();
  } catch (Throwable t) { }
  return -1L;
}""")
M(cmds, r"""
public static @PKG@.MpState state(@PR@ pr, @REF@ r, @ST@ st) {
  java.util.UUID u = pr.getUuid();
  @PKG@.MpState s = (@PKG@.MpState) STATES.get(u);
  if (s == null || s.st != st) {
    s = new @PKG@.MpState(u, r, st);
    STATES.put(u, s);
  }
  s.ref = r;
  s.quit = false;
  return s;
}""")
# start a flight record (m5 / m6 / m7): where it started, what it should reach
M(cmds, r"""
public static void flight(@PKG@.MpState s, @V3D@ p, String kind, double wantD, double wantH, long now) {
  s.fl = 1;
  s.flKind = kind;
  s.fx0 = p.x; s.fy0 = p.y; s.fz0 = p.z; s.fTop = p.y;
  s.fT0 = now;
  s.fLeft = false;
  s.fWantD = wantD;
  s.fWantH = wantH;
}""")
M(cmds, r"""
public static void armFlow(@PKG@.MpState s, long now) {
  s.flowFall = true;
  s.flowTop = 0L;
  s.flowArm = now;
  s.flowRose = false;
}""")
# ---- the pushes (run in the tick right after the command armed them)
M(cmds, r"""
public static void push(@PKG@.MpState s, @PR@ pr, @CB@ cb, @REF@ r, @V3D@ p, long now) {
  int k = s.pend;
  s.pend = 0;
  double g = grav();
  double[] lk = look(cb, r);
  if (lk == null) { s.rs = 0; tell(pr, "Push: your look direction is unreadable - nothing done."); return; }
  if (k == 4) {
    double vy = @PKG@.MpLogic.vyFor(VAULT_UP, g);
    if (setVel(cb, r, 0.0, vy, 0.0, false)) s.sets = s.sets + 1L;
    s.m1Phase = 1;
    s.m1Rose = false;
    s.m1Sets = 0L;
    s.m1MinVy = 0.0;
    flight(s, p, "m1 launch", 0.0, VAULT_UP, now);
    tell(pr, "M1: launched up at " + f1(vy) + " b/s (" + f1(VAULT_UP) + " blocks). Do not touch the keys until you land.");
    return;
  }
  if (k == 1) {
    if (s.costs && take(cb, r, C_VAULT_S, C_VAULT_M) == 0) { tell(pr, "M9: not enough for the vault (" + f1(C_VAULT_S) + " Stamina + " + f1(C_VAULT_M) + " Mana) - refused. " + statText(cb, r)); return; }
    double vy = @PKG@.MpLogic.vyFor(VAULT_UP, g);
    double vh = @PKG@.MpLogic.hSpeed(VAULT_FWD, vy, g);
    if (setVel(cb, r, lk[6] * vh, vy, lk[7] * vh, false)) s.sets = s.sets + 1L;
    flight(s, p, s.sweep ? "m6 vault + sweep" : "m5 vault", VAULT_FWD, VAULT_UP, now);
    armFlow(s, now);
    s.airUntil = now + 4000L;
    s.airUsed = false;
    s.airCrouch = true;          // Skyy's open default: CROUCH is the free air jump too (the Acrobatics double-jump key)
    tell(pr, "Vault: vy " + f1(vy) + ", forward " + f1(vh) + " b/s (target " + f1(VAULT_FWD) + " forward, " + f1(VAULT_UP) + " up). Flowing fall + one free air jump armed." + (s.costs ? " " + statText(cb, r) : ""));
    return;
  }
  if (k == 2) {
    double vh = LUNGE_FWD / 0.25;
    if (setVel(cb, r, lk[6] * vh, 0.0, lk[7] * vh, false)) s.sets = s.sets + 1L;
    flight(s, p, "m5 lunge", LUNGE_FWD, 0.0, now);
    tell(pr, "Lunge: " + f1(vh) + " b/s along the ground (target " + f1(LUNGE_FWD) + " blocks; measured after 0.6 s).");
    return;
  }
  if (k == 3) {
    if (s.costs && take(cb, r, C_RISE_S, C_RISE_M) == 0) { tell(pr, "M9: not enough for the rise (" + f1(C_RISE_S) + " Stamina + " + f1(C_RISE_M) + " Mana) - refused. " + statText(cb, r)); s.rs = 0; return; }
    double vy = @PKG@.MpLogic.vyFor(RISE_UP, g);
    // m7 (rs 1) hangs at the top, so it should cover RISE_FWD by the apex; a plain rise lands without a hang, so spread it over the whole air time
    double vh = s.rs == 1 ? RISE_FWD / (vy / g) : RISE_FWD / (2.0 * vy / g);
    if (setVel(cb, r, lk[6] * vh, vy, lk[7] * vh, false)) s.sets = s.sets + 1L;
    flight(s, p, "m7 rise", RISE_FWD, RISE_UP, now);
    if (s.rs != 1) { tell(pr, "Rise: vy " + f1(vy) + " (target " + f1(RISE_UP) + " up, " + f1(RISE_FWD) + " forward)."); return; }
    // m7: the cone in front: hit + knock up with you
    s.ups.clear();
    s.rsT = now;
    s.rsApex = 0L;
    s.rsRose = false;
    s.noFallUntil = 0L;
    s.rsMinY = 1.0E9;
    s.rsMaxY = -1.0E9;
    s.flings = 0;
    double ku = @PKG@.MpLogic.vyFor(KNOCK_UP, g);
    java.util.List l = near(cb, p.x + lk[6] * 1.5, p.y + 1.0, p.z + lk[7] * 1.5, CONE_LEN);
    int n = 0;
    for (int i = 0; i < l.size(); i++) {
      @REF@ t = (@REF@) l.get(i);
      if (!enemy(cb, t, r)) continue;
      @V3D@ tp = pos(cb, t);
      if (tp == null || !@PKG@.MpLogic.inCone(tp.x - p.x, tp.z - p.z, lk[6], lk[7], CONE_LEN, CONE_HALF)) continue;
      hit(cb, t, r, 1.2 * s.hitAmt, false);
      if (setVel(cb, t, 0.0, ku, 0.0, true)) n++;
      s.ups.add(t);
    }
    tell(pr, "M7 Rising Strike: vy " + f1(vy) + ", " + n + " enemies in the cone hit for " + f1(1.2 * s.hitAmt) + " and knocked up at " + f1(ku) + " b/s. Crouch near the top = plunge.");
  }
}""")
# ---- m1: the slow fall (analytic or cap), measured from the top to the landing
M(cmds, r"""
public static void m1Tick(@PKG@.MpState s, @PR@ pr, @CB@ cb, @REF@ r, @V3D@ p, double[] cv, boolean ground, boolean land, long now) {
  if (s.m1Phase == 0) return;
  double g = grav();
  if (s.m1Phase == 1) {
    if (cv != null && cv[1] > 1.0) s.m1Rose = true;
    if (cv != null && cv[1] <= 0.0 && (s.m1Rose || now - s.fT0 > 1500L)) { s.m1Phase = 2; s.m1Top = now; s.m1TopY = p.y; }
    else if (now - s.fT0 > 3000L) { s.m1Phase = 0; tell(pr, "M1: never reached a top (client speed unreadable?) - stopped."); }
    return;
  }
  if (s.m1Phase == 2 && !land && !ground) {
    if (cv != null && cv[1] < s.m1MinVy) s.m1MinVy = cv[1];
    if (s.m1Mode == 1 && s.m1Val > 0.0) {
      double vy = @PKG@.MpLogic.slowVy(s.m1Val / 100.0, g, now - s.m1Top);
      if (setVel(cb, r, cv == null ? 0.0 : cv[0], vy, cv == null ? 0.0 : cv[2], false)) { s.m1Sets = s.m1Sets + 1L; s.sets = s.sets + 1L; }
    } else if (s.m1Mode == 2 && cv != null) {
      double vy = @PKG@.MpLogic.capVy(cv[1], s.m1Val);
      if (vy != cv[1] && setVel(cb, r, cv[0], vy, cv[2], false)) { s.m1Sets = s.m1Sets + 1L; s.sets = s.sets + 1L; }
    }
    if (now - s.m1Top > 6000L) { s.m1Phase = 0; tell(pr, "M1: no landing within 6 s - stopped."); }
    return;
  }
  if (s.m1Phase == 2 && (land || ground)) {
    s.m1Phase = 0;
    double h = s.m1TopY - p.y;
    double ms = (double) (now - s.m1Top);
    double van = @PKG@.MpLogic.fallMs(h, g);
    String what = s.m1Mode == 2 ? "cap " + f1(s.m1Val) + " b/s" : (s.m1Val > 0.0 ? f1(s.m1Val) + "% slower" : "BASELINE (vanilla)");
    double want = s.m1Mode == 1 ? van * @PKG@.MpLogic.expectRatio(s.m1Val / 100.0) : 0.0;
    tell(pr, "M1 " + what + ": fell " + f1(h) + " blocks in " + Math.round(ms) + " ms (vanilla formula " + Math.round(van) + " ms, ratio " + f1(van > 0.0 ? ms / van : 0.0) + "), fastest fall seen " + f1(0.0 - s.m1MinVy) + " b/s, " + s.m1Sets + " Sets."
        + (s.m1Mode == 1 && s.m1Val > 0.0 ? " Expected " + Math.round(want) + " ms: " + @PKG@.MpLogic.verdict(ms, want, 0.10) + ". Did it look smooth (no stutter)?" : " Run it again with 15 to compare."));
  }
}""")
# ---- the flowing fall after a vault / a hang (analytic 15 % slower from the top); stops at the landing
M(cmds, r"""
public static void flowTick(@PKG@.MpState s, @CB@ cb, @REF@ r, double[] cv, boolean ground, long now) {
  if (!s.flowFall || cv == null) return;
  // on the ground: forget the old apex, so the next takeoff (a bound, a late FALL window) starts a fresh slow fall from its own top
  if (ground) { if (s.flowTop != 0L) armFlow(s, now); return; }
  if (s.flowTop == 0L) {
    if (cv[1] > 1.0) s.flowRose = true;
    if (cv[1] <= 0.0 && (s.flowRose || now - s.flowArm > 1500L)) s.flowTop = now;
    return;
  }
  double vy = @PKG@.MpLogic.slowVy(FLOW, grav(), now - s.flowTop);
  if (setVel(cb, r, cv[0], vy, cv[2], false)) s.sets = s.sets + 1L;
}""")
# ---- m2 / m3 / bounds: the movement edges
M(cmds, r"""
public static void bound(@PKG@.MpState s, @PR@ pr, @CB@ cb, @REF@ r, long now, String how) {
  if (s.boundDone) return;
  s.boundDone = true;
  if (s.costs && take(cb, r, C_BOUND_S, C_BOUND_M) == 0) {
    s.chain = false;
    tell(pr, "Bound refused: not enough Stamina / Mana (" + f1(C_BOUND_S) + " + " + f1(C_BOUND_M) + ") - the chain ENDS here after " + s.bounds + " bounds. " + statText(cb, r));
    return;
  }
  double g = grav();
  double[] lk = look(cb, r);
  double hx = lk == null ? 0.0 : lk[6];
  double hz = lk == null ? 1.0 : lk[7];
  double vy = jumpForce(cb, r) * Math.sqrt(B_HEIGHT);
  double d = @PKG@.MpLogic.boundDist(B_BASE, B_PER, B_CAP, s.landFell);
  double vh = @PKG@.MpLogic.hSpeed(d, vy, g);
  if (setVel(cb, r, hx * vh, vy, hz * vh, false)) s.sets = s.sets + 1L;
  s.bounds = s.bounds + 1;
  s.lastBoundAt = now;
  s.wasFalling = false;
  armFlow(s, now);
  tell(pr, "BOUND " + s.bounds + " (" + how + "): fell " + f1(s.landFell) + " -> " + f1(d) + " blocks forward, vy " + f1(vy) + "." + (s.costs ? " " + statText(cb, r) : ""));
}""")
M(cmds, r"""
public static void edges(@PKG@.MpState s, @PR@ pr, @CB@ cb, @REF@ r, @MVT@ ms, double[] cv, boolean ground, boolean land, boolean leave,
                         boolean jEdge, boolean cEdge, boolean xEdge, long now) {
  if (s.logUntil > 0L && now >= s.logUntil) {
    s.logUntil = 0L;
    tell(pr, "M2 / M3: the time is over (" + s.bounds + " bounds)." + (s.chain ? " Chain stopped." : ""));
    s.chain = false;
  }
  boolean logOn = s.logUntil > now;
  // one bound per landing: boundDone resets at a landing (LOCAL FIX: the draft reset it at take-off, so after a missed landing the chain
  // never ended and a hidden landing could never bound); wasFalling = seen falling since the last take-off / bound (a hidden landing
  // needs a fall before the fresh rise - jump taps while rising from a bound are no new bound)
  if (leave || land) s.wasFalling = false;
  if (!ground && !leave && cv != null && cv[1] < -2.0) s.wasFalling = true;
  if (land) {
    s.boundDone = false;
    s.lastLand = now;
    s.landFell = s.fallMax;
    if (logOn) {
      String fallNote = s.lastFallAt > 0L && now - s.lastFallAt < 500L ? "the FALL damage (" + f1(s.lastFallAmt) + ") came " + (now - s.lastFallAt) + " ms BEFORE this tick" : "no FALL damage seen yet";
      tell(pr, "M2 landed: fell " + f1(s.landFell) + " blocks, rolling " + (ms.rolling ? "YES" : "no") + ", " + fallNote + ".");
    }
    if (s.chain && s.airPress > 0L && @PKG@.MpLogic.timed(now, s.airPress, (long) B_BEFORE, (long) B_AFTER)) bound(s, pr, cb, r, now, "pressed " + (now - s.airPress) + " ms early");
  }
  if (jEdge) {
    if (ground || leave || now - s.leftAt <= 150L) {
      // a jump from the ground (the server sees 'jumping' as you leave it, or a tick or so after onGround went false): how long after the landing?
      long d = s.lastLand > 0L ? now - s.lastLand : 99999L;
      if (logOn) tell(pr, "M2: jump " + (d < 99999L ? d + " ms after the landing" : "(no landing seen)") + " - window " + (long) B_AFTER + " ms after: " + (d <= (long) B_AFTER ? "TIMED" : "not timed"));
      if (s.chain && d <= (long) B_AFTER) bound(s, pr, cb, r, now, d + " ms after landing");
    } else {
      // airborne for a while: a press in the air (early press / mid-air jump), or a fresh jump whose landing tick the server never saw
      s.airPress = now;
      boolean fresh = cv != null && cv[1] > 0.5 * jumpForce(cb, r) && s.wasFalling;
      if (logOn) tell(pr, "M2 / M3: jump edge IN THE AIR (client vy " + (cv == null ? "?" : f1(cv[1])) + ")" + (fresh ? " - rising fast: a jump from the ground whose landing tick the server never saw" : ""));
      if (s.chain && fresh) { s.landFell = s.fallMax; s.boundDone = false; bound(s, pr, cb, r, now, "landing hidden"); }
    }
  }
  if (cEdge && !ground && logOn) tell(pr, "M3 / M10: crouch edge IN THE AIR (client vy " + (cv == null ? "?" : f1(cv[1])) + ")");
  if (xEdge && logOn) tell(pr, "M3: extraJumpsUsed is now " + (int) ms.extraJumpsUsed + " (the client's own extra jump)");
  if (s.chain && s.bounds > 0 && s.lastLand > 0L && ground && !s.boundDone && now - s.lastLand > (long) B_AFTER) {
    s.chain = false;
    tell(pr, "Chain ENDED: no timed jump within " + (long) B_AFTER + " ms of the landing (" + s.bounds + " bounds).");
  }
  // m3 / the vault's free air jump: the first airborne jump edge (or crouch edge unless "m3 jump")
  if (s.airUntil > now && !s.airUsed && !ground && !leave && now - s.leftAt > 150L && (jEdge || (s.airCrouch && cEdge))) {
    s.airUsed = true;
    double vy = jumpForce(cb, r);
    if (setVel(cb, r, cv == null ? 0.0 : cv[0], vy, cv == null ? 0.0 : cv[2], false)) s.sets = s.sets + 1L;
    if (s.flowFall) armFlow(s, now);
    tell(pr, "AIR JUMP by " + (jEdge ? "the JUMP key" : "CROUCH") + ": vy " + f1(vy) + ".");
  }
}""")
# a FALL damage held during a chain: forgiven by a bound for THAT landing (its FALL event comes in the landing tick; the bound from 150 ms
# before - an early press bounds in the landing tick, one tick of jitter - to B_AFTER + 50 ms after), else re-dealt at (1 - FLOW) once
# the window is over. LOCAL FIX: the draft kept a 'forgive' flag from the PREVIOUS bound through the whole flight, so the next landing's
# fall was forgiven without any timed jump.
M(cmds, r"""
public static boolean boundFor(long bound, long fall) {
  return bound > 0L && fall > 0L && bound >= fall - 150L && bound <= fall + (long) B_AFTER + 50L;
}""")
M(cmds, r"""
public static void heldFall(@PKG@.MpState s, @PR@ pr, @CB@ cb, @REF@ r, long now) {
  if (s.pendFallAt <= 0L) return;
  if (boundFor(s.lastBoundAt, s.pendFallAt)) {
    tell(pr, "Timed landing: the held FALL damage " + f1(s.pendFall) + " is FORGIVEN.");
    s.pendFallAt = 0L;
    return;
  }
  if (now - s.pendFallAt <= (long) B_AFTER + 50L) return;
  double a = s.pendFall * (1.0 - FLOW);
  s.pendFallAt = 0L;
  boolean ok = hit(cb, r, r, a, true);
  tell(pr, "Missed landing: the held FALL damage re-dealt at 85% = " + f1(a) + (ok ? "" : " - FAILED (see the log)") + ". Did your Health drop by that?");
}""")
# ---- flight report (m5 / m6 / m7): measured distance, height and air time vs the target; the m6 sweep while flying
M(cmds, r"""
public static void flightTick(@PKG@.MpState s, @PR@ pr, @CB@ cb, @REF@ r, @V3D@ p, boolean ground, boolean land, long now) {
  if (s.fl == 0) return;
  if (!ground) s.fLeft = true;
  if (p.y > s.fTop) s.fTop = p.y;
  if (s.sweep && !ground) {
    java.util.List l = near(cb, p.x, p.y + 1.0, p.z, SWEEP_R);
    for (int i = 0; i < l.size(); i++) {
      @REF@ t = (@REF@) l.get(i);
      if (!enemy(cb, t, r) || s.kicked.contains(t)) continue;
      s.kicked.add(t);
      hit(cb, t, r, 2.0 * s.hitAmt, false);
    }
  }
  boolean lunge = "m5 lunge".equals(s.flKind);
  boolean done = (s.fLeft && (land || ground)) || (lunge && now - s.fT0 >= 600L);
  if (!done && now - s.fT0 < 6000L) return;
  double dx = p.x - s.fx0;
  double dz = p.z - s.fz0;
  double d = Math.sqrt(dx * dx + dz * dz);
  double h = s.fTop - s.fy0;
  String head = s.flKind + ": " + (done ? "" : "NO LANDING in 6 s - ");
  tell(pr, head + "forward " + @PKG@.MpLogic.verdict(d, s.fWantD, 0.25) + ", height " + (s.fWantH > 0.0 ? @PKG@.MpLogic.verdict(h, s.fWantH, 0.25) : f1(h)) + ", air " + (now - s.fT0) + " ms.");
  if (s.sweep) tell(pr, "M6: kicked " + s.kicked.size() + " enemies for " + f1(2.0 * s.hitAmt) + " each (once each - did any take two kicks?).");
  s.fl = 0;
  s.sweep = false;
  s.kicked.clear();
}""")
# ---- m7: hang / plunge / slam / the Acrobatics XP check (m8, m10, m11)
M(cmds, r"""
public static void holdMobs(@PKG@.MpState s, @CB@ cb, double vy) {
  for (int i = s.ups.size() - 1; i >= 0; i--) {
    @REF@ t = (@REF@) s.ups.get(i);
    if (t == null || !t.isValid()) { s.ups.remove(i); continue; }
    if (setVel(cb, t, 0.0, vy, 0.0, true)) s.sets = s.sets + 1L;
    @V3D@ tp = pos(cb, t);
    if (tp != null) {
      if (tp.y < s.rsMinY) s.rsMinY = tp.y;
      if (tp.y > s.rsMaxY) s.rsMaxY = tp.y;
    }
  }
}""")
# the plunge starts: no fall damage from now on (the FALL event may come before this tick sees the landing), the XP before
M(cmds, r"""
public static void plunge(@PKG@.MpState s, @PR@ pr, long now, String why) {
  s.rs = 3;
  s.rsT = now;
  s.noFallUntil = now + 6500L;
  s.xpBefore = acroXp(s.u);
  tell(pr, why + " - PLUNGE at " + f1(PLUNGE) + " b/s.");
}""")
M(cmds, r"""
public static void risingTick(@PKG@.MpState s, @PR@ pr, @CB@ cb, @REF@ r, @MVT@ ms, @V3D@ p, double[] cv, boolean ground, boolean land, boolean cEdge, long now) {
  if (s.rs == 0) return;
  if (s.rs == 1) {
    if (cv != null && cv[1] > 1.0) s.rsRose = true;
    boolean nearTop = s.rsRose && cv != null && cv[1] <= 3.0;
    if (cEdge && nearTop) { plunge(s, pr, now, "M10: crouch near the top seen (still rising, client vy " + f1(cv[1]) + ")"); return; }
    if ((s.rsRose && cv != null && cv[1] <= 0.5) || now - s.rsT > 1500L) {
      s.rs = 2;
      s.rsApex = now;
      tell(pr, "M7: the top - HANG " + (long) HANG_MS + " ms (you and " + s.ups.size() + " enemies held). Crouch now to plunge.");
    }
    return;
  }
  if (s.rs == 2) {
    if (cEdge) { plunge(s, pr, now, "M10: crouch near the top seen (" + (now - s.rsApex) + " ms into the hang)"); return; }
    if (now - s.rsApex < (long) HANG_MS) {
      if (setVel(cb, r, cv == null ? 0.0 : cv[0] * 0.5, HANG_VY, cv == null ? 0.0 : cv[2] * 0.5, false)) s.sets = s.sets + 1L;
      holdMobs(s, cb, HANG_VY);
      return;
    }
    s.rs = 4;
    armFlow(s, now);
    s.flowTop = now;
    tell(pr, "M7: hang over - mobs stayed between y " + f1(s.rsMinY) + " and " + f1(s.rsMaxY) + " (" + s.flings + " flings). No plunge: flowing fall (15% slower, 15% less fall damage).");
    return;
  }
  if (s.rs == 3) {
    if (!(land || ground)) {
      if (setVel(cb, r, 0.0, 0.0 - PLUNGE, 0.0, false)) s.sets = s.sets + 1L;
      holdMobs(s, cb, 0.0 - PLUNGE);
      if (now - s.rsT > 6000L) { s.rs = 0; tell(pr, "M8: no landing within 6 s - stopped."); }
      return;
    }
    s.rs = 0;
    s.noFallUntil = now + 500L;
    int n = 0;
    java.util.List l = near(cb, p.x, p.y + 0.5, p.z, SLAM_R);
    for (int i = 0; i < l.size(); i++) {
      @REF@ t = (@REF@) l.get(i);
      if (!enemy(cb, t, r)) continue;
      if (hit(cb, t, r, s.hitAmt, false)) n++;
    }
    int dragged = 0;
    for (int i = 0; i < s.ups.size(); i++) {
      @V3D@ tp = pos(cb, (@REF@) s.ups.get(i));
      if (tp != null && tp.y - p.y < 2.0) dragged++;
    }
    s.xpAt = now + 2500L;
    tell(pr, "M8 PLUNGE landed: slam hit " + n + " enemies in " + f1(SLAM_R) + " blocks; " + dragged + "/" + s.ups.size() + " knocked-up enemies came down with you; rolling at landing " + (ms.rolling ? "YES (SkyySkills may pay roll XP!)" : "no") + ". Acrobatics XP check in 2.5 s.");
    return;
  }
  if (s.rs == 4 && (land || ground)) {
    s.rs = 0;
    tell(pr, "M7: landed after the flowing fall (FALL damage x 0.85 if any - see the m4 line).");
  }
}""")
M(cmds, r"""
public static void xpTick(@PKG@.MpState s, @PR@ pr, long now) {
  if (s.xpAt <= 0L || now < s.xpAt) return;
  s.xpAt = 0L;
  long after = acroXp(s.u);
  if (s.xpBefore < 0L || after < 0L) { tell(pr, "M11: SkyySkills skill:fn:xp not found - read your Acrobatics XP with /skills instead."); return; }
  long d = after - s.xpBefore;
  tell(pr, "M11: Acrobatics XP " + s.xpBefore + " -> " + after + " (" + (d == 0L ? "PASS: no XP for the plunge" : "FAIL: +" + d + " XP was paid") + ").");
}""")
# ---- m12: the aura scan + combo stacks
M(cmds, r"""
public static void auraTick(@PKG@.MpState s, @PR@ pr, @CB@ cb, @REF@ r, @V3D@ p, long now) {
  if (s.auraUntil <= 0L) return;
  if (now >= s.auraUntil) {
    s.auraUntil = 0L;
    tell(pr, "M12 over: " + s.auraScans + " scans, avg " + (s.auraScans == 0 ? 0L : s.auraNs / s.auraScans / 1000L) + " us, max " + s.auraNsMax / 1000L + " us; " + s.hitsSeen + " hits counted, last combo " + s.combo + ".");
    return;
  }
  int c = @PKG@.MpLogic.prune(s.stamps, now, (long) COMBO_MS, (int) COMBO_MAX);
  if (c != s.combo) { s.combo = c; tell(pr, "M12 combo " + c); }
  if (now < s.auraNext) return;
  s.auraNext = now + 1000L;
  long t0 = System.nanoTime();
  java.util.List l = near(cb, p.x, p.y + 1.0, p.z, AURA_R);
  int n = 0;
  for (int i = 0; i < l.size(); i++) if (enemy(cb, (@REF@) l.get(i), r)) n++;
  long ns = System.nanoTime() - t0;
  s.auraNs = s.auraNs + ns;
  if (ns > s.auraNsMax) s.auraNsMax = ns;
  s.auraScans = s.auraScans + 1;
  if (s.auraScans % 5 == 1) tell(pr, "M12 aura: " + n + " enemies within " + f1(AURA_R) + " blocks (scan " + ns / 1000L + " us), combo " + s.combo + ".");
}""")
# ---- the per-player tick (MpTick, world thread, every tick)
M(cmds, r"""
public static void tickPlayer(@REF@ r, @ST@ store, @CB@ cb, float dt) {
  if (r == null || STATES.isEmpty()) return;
  @PR@ pr = prOf(cb, r);
  if (pr == null) return;
  @PKG@.MpState s = (@PKG@.MpState) STATES.get(pr.getUuid());
  if (s == null) return;
  if (s.st != store) { STATES.remove(pr.getUuid(), s); return; }      // another world: the probe state is dropped
  // REVIEW FIX 4: a relog makes a new player entity; the old state (its ref no longer valid) must not come back armed
  if (s.ref != r && (s.ref == null || !s.ref.isValid())) { STATES.remove(pr.getUuid(), s); @PKG@.MpLog.info(pr.getUsername() + ": stale probe state (relog) dropped"); return; }
  long t0 = System.nanoTime();
  long now = now();
  @MVT@ ms = moves(cb, r);
  @V3D@ p = pos(cb, r);
  if (ms == null || p == null) return;
  double[] cv = cvel(cb, r);
  boolean g = ms.onGround;
  boolean land = g && !s.prevGround;
  boolean leave = !g && s.prevGround;
  boolean jEdge = ms.jumping && !s.prevJump;
  boolean cEdge = ms.crouching && !s.prevCrouch;
  int xj = (int) ms.extraJumpsUsed;
  boolean xEdge = xj != s.prevXj;
  s.prevGround = g;
  s.prevJump = ms.jumping;
  s.prevCrouch = ms.crouching;
  s.prevXj = xj;
  if (leave) { s.leftAt = now; s.airTopY = p.y; s.fallMax = 0.0; }
  if (!g) {
    if (p.y > s.airTopY) s.airTopY = p.y;
    double fd = fallDist(cb, r);
    if (fd > s.fallMax) s.fallMax = fd;
    if (s.airTopY - p.y > s.fallMax) s.fallMax = s.airTopY - p.y;
  }
  if (s.pend != 0) push(s, pr, cb, r, p, now);
  m1Tick(s, pr, cb, r, p, cv, g, land, now);
  if (s.m1Phase == 0 && (s.rs == 0 || s.rs == 4)) flowTick(s, cb, r, cv, g, now);
  edges(s, pr, cb, r, ms, cv, g, land, leave, jEdge, cEdge, xEdge, now);
  heldFall(s, pr, cb, r, now);
  flightTick(s, pr, cb, r, p, g, land, now);
  risingTick(s, pr, cb, r, ms, p, cv, g, land, cEdge, now);
  if (g && s.flowFall && s.rs == 0 && s.m1Phase == 0 && s.fl == 0 && !s.chain && now - s.lastLand > 500L) s.flowFall = false;   // kept 0.5 s: the FALL event may come late
  xpTick(s, pr, now);
  auraTick(s, pr, cb, r, p, now);
  if (s.fallUntil > 0L && now >= s.fallUntil) { s.fallUntil = 0L; tell(pr, "M4: the 30 s are over - retype /mprobe m4 to test again."); }
  if (s.quit && s.pendFallAt <= 0L) { STATES.remove(pr.getUuid(), s); tell(pr, "Probe state cleared (the held FALL damage is settled)."); return; }
  long ns = System.nanoTime() - t0;
  s.ns = s.ns + ns;
  if (ns > s.nsMax) s.nsMax = ns;
  s.ticks = s.ticks + 1L;
}""")
# ---- the damage hooks (MpFallSys: Filter group; MpHitSys: Inspect group)
M(cmds, r"""
public static boolean isFall(@DCS@ c) {
  if (c == null) return false;
  if (c == @DCS@.FALL) return true;
  return "Fall".equalsIgnoreCase(String.valueOf(c.getId()));
}""")
M(cmds, r"""
public static void onFall(@DMG@ d, @PR@ pr) {
  @PKG@.MpState s = (@PKG@.MpState) STATES.get(pr.getUuid());
  if (s == null) return;
  long now = now();
  float a = d.getAmount();
  s.lastFallAt = now;
  s.lastFallAmt = (double) a;
  s.fallEvents = s.fallEvents + 1;
  if (now < s.noFallUntil) { d.setCancelled(true); tell(pr, "M8: plunge slam FALL damage " + f1((double) a) + " CANCELLED."); return; }
  if (s.chain) { d.setCancelled(true); s.pendFall = (double) a; s.pendFallAt = now; tell(pr, "Chain: FALL damage " + f1((double) a) + " HELD for " + (long) B_AFTER + " ms (a timed jump forgives it)."); return; }
  if (now < s.fallUntil) {
    if (!(s.fallPct > 0.0)) { d.setCancelled(true); tell(pr, "M4: FALL damage " + f1((double) a) + " CANCELLED - did your Health stay the same?"); }
    else { d.setAmount((float) ((double) a * s.fallPct / 100.0)); tell(pr, "M4: FALL damage " + f1((double) a) + " -> " + f1((double) a * s.fallPct / 100.0)); }
    return;
  }
  if (s.flowFall) { d.setAmount((float) ((double) a * (1.0 - FLOW))); tell(pr, "Flowing fall: FALL damage " + f1((double) a) + " -> " + f1((double) a * (1.0 - FLOW)) + " (-15%)."); }
}""")
M(cmds, r"""
public static void onHit(@DMG@ d, @REF@ target, @CB@ buf) {
  if (MINE.remove(d) != null) return;
  Object src = d.getSource();
  if (!(src instanceof @DENT@)) return;
  @REF@ att = ((@DENT@) src).getRef();
  @PR@ apr = prOf(buf, att);
  if (apr == null) return;
  @PKG@.MpState s = (@PKG@.MpState) STATES.get(apr.getUuid());
  if (s == null) return;
  long now = now();
  if (s.auraUntil > now) { s.stamps.add(Long.valueOf(now)); s.hitsSeen = s.hitsSeen + 1; }
  if ((s.rs == 1 || s.rs == 2) && s.ups.contains(target)) {
    double[] lk = look(buf, att);
    if (lk != null && setVel(buf, target, lk[6] * FLING, 2.0, lk[7] * FLING, true)) {
      s.flings = s.flings + 1;
      s.ups.remove(target);
      tell(apr, "M7: air hit - that enemy is FLUNG " + f1(FLING) + " b/s along your look (did it fly about 6 blocks?).");
    }
  }
}""")
# ---- the commands' work (world thread)
M(cmds, r"""
public static void help(@PR@ pr) {
  tell(pr, "Monk probes (op only). The plan's test script says the order; send the server log afterwards.");
  tell(pr, "/mprobe kit | m1 <pct> | m1cap <bps> | m2 [log] | m3 [jump] | m4 [pct] | m5 vault|lunge|rise | m6 [hit] | m7 [hit]");
  tell(pr, "/mprobe m9 on|off | m12 [secs] | m13 | slowfx [EffectId] | xp | stats | stop");
}""")
M(cmds, r"""
public static void kit(@PR@ pr, @ST@ st, @REF@ ref) {
  @IC@ dst = null;
  try { dst = @INVC@.getCombined(st, ref, @INVC@.STORAGE_HOTBAR_BACKPACK); } catch (Throwable t) { dst = null; }
  if (dst == null) { tell(pr, "Could not open your inventory."); return; }
  StringBuilder lost = new StringBuilder();
  int got = 0;
  for (int i = 0; i < KIT.length; i++) {
    boolean ok = false;
    try {
      @IST@ tx = dst.addItemStack(new @IS@(KIT[i], 1));
      @IS@ rem = tx == null ? null : tx.getRemainder();
      ok = tx != null && tx.succeeded() && (rem == null || rem.isEmpty());
    } catch (Throwable t) { @PKG@.MpLog.warn("kit " + KIT[i] + " failed: " + t); ok = false; }
    if (ok) got++;
    else lost.append(lost.length() == 0 ? "" : ", ").append(KIT[i]);
  }
  tell(pr, "Kit: " + got + " Bo staffs given." + (lost.length() > 0 ? " No room for " + lost.toString() + " - nothing was dropped." : ""));
}""")
M(cmds, r"""
public static void m13(@PR@ pr, @ST@ st, @REF@ ref) {
  String id = "nothing";
  String weapon = "-";
  try {
    @IS@ it = @INVC@.getItemInHand(st, ref);
    if (it != null && !it.isEmpty()) {
      id = it.getItemId();
      weapon = it.getItem() != null && it.getItem().getWeapon() != null ? "a WEAPON" : "not a weapon";
    }
  } catch (Throwable t) { id = "unreadable (" + t + ")"; }
  tell(pr, "M13: in your hand: " + id + " (" + weapon + "). Hold it, tap + hold the attack: does the hold do a charged attack of its own?");
  for (int i = 0; i < BO_DESK.length; i++) tell(pr, "M13 build-time read: " + BO_DESK[i]);
}""")
M(cmds, r"""
public static void slowfx(@PR@ pr, @ST@ st, @REF@ ref, String id) {
  if (id == null || id.trim().length() == 0) id = SLOW_ID;
  Object fx = null;
  try {
    int i = @EFX@.getAssetMap().getIndex(id.trim());
    if (i >= 0) fx = @EFX@.getAssetMap().getAsset(i);
  } catch (Throwable t) { fx = null; }
  if (!(fx instanceof @EFX@)) { tell(pr, "No entity effect '" + id.trim() + "' is loaded."); return; }
  @V3D@ p = pos(st, ref);
  if (p == null) { tell(pr, "No position."); return; }
  java.util.List l = near(st, p.x, p.y + 1.0, p.z, AURA_R);
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    @REF@ t = (@REF@) l.get(i);
    if (!enemy(st, t, ref)) continue;
    try {
      @ECC@ c = (@ECC@) st.getComponent(t, @ECC@.getComponentType());
      if (c != null && c.addEffect(t, (@EFX@) fx, st)) n++;
    } catch (Throwable t2) { @PKG@.MpLog.warn("slowfx failed: " + t2); }
  }
  tell(pr, "slowfx: '" + id.trim() + "' applied to " + n + " enemies within " + f1(AURA_R) + " blocks. Do they move slower? Does it show an icon?");
}""")
M(cmds, r"""
public static void stats(@PR@ pr, @PKG@.MpState s) {
  if (s == null) { tell(pr, "No probe state - run a probe first."); return; }
  tell(pr, "Stats: " + s.ticks + " ticks, avg " + (s.ticks == 0L ? 0L : s.ns / s.ticks / 1000L) + " us, max " + s.nsMax / 1000L + " us per tick; " + s.sets + " velocity Sets; " + s.fallEvents + " FALL events; " + s.bounds + " bounds; costs " + (s.costs ? "on" : "off") + ".");
}""")
# one entry point for both usage variants: what = probe word, arg = second word or null
M(cmds, r"""
public static void run(@REF@ ref, @ST@ st, @PR@ pr, String what, String arg) {
  String t = what == null ? "" : what.trim().toLowerCase(java.util.Locale.ROOT);
  String a = arg == null ? null : arg.trim().toLowerCase(java.util.Locale.ROOT);
  @PKG@.MpLog.info(pr.getUsername() + " ran /mprobe " + t + (arg == null ? "" : " " + arg));
  if (t.equals("kit")) { kit(pr, st, ref); return; }
  if (t.equals("m13")) { m13(pr, st, ref); return; }
  if (t.equals("slowfx")) { slowfx(pr, st, ref, arg); return; }
  if (t.equals("xp") || t.equals("m11")) { tell(pr, "Acrobatics XP now: " + acroXp(pr.getUuid()) + " (-1 = SkyySkills not found). M11 itself runs inside m7: crouch at the top."); return; }
  if (t.equals("stop")) {
    @PKG@.MpState o = (@PKG@.MpState) STATES.get(pr.getUuid());
    if (o != null && o.pendFallAt > 0L) {
      // REVIEW FIX 3: a held FALL damage is never dropped by a stop: every probe ends now, the tick forgives / re-deals it, then clears
      @PKG@.MpState q = new @PKG@.MpState(o.u, o.ref, o.st);
      q.pendFall = o.pendFall;
      q.pendFallAt = o.pendFallAt;
      q.lastBoundAt = o.lastBoundAt;
      q.quit = true;
      STATES.put(pr.getUuid(), q);
      tell(pr, "Probes stopped; the held FALL damage " + f1(o.pendFall) + " is settled first (state cleared in a moment).");
      return;
    }
    STATES.remove(pr.getUuid());
    tell(pr, "Probe state cleared.");
    return;
  }
  if (t.equals("stats")) { stats(pr, (@PKG@.MpState) STATES.get(pr.getUuid())); return; }
  @PKG@.MpState s = state(pr, ref, st);
  long now = now();
  if (t.equals("m1") || t.equals("m1cap")) {
    s.m1Mode = t.equals("m1cap") ? 2 : 1;
    s.m1Val = s.m1Mode == 2 ? @PKG@.MpLogic.dnum(a, 6.0, 0.5, 40.0) : @PKG@.MpLogic.dnum(a, 0.0, 0.0, 90.0);
    s.pend = 4;
    tell(pr, "M1 armed (" + (s.m1Mode == 2 ? "cap " + f1(s.m1Val) + " b/s" : f1(s.m1Val) + "% slower") + "): stand still on flat open ground.");
    return;
  }
  if (t.equals("m2")) {
    s.logUntil = now + 60000L;
    s.chain = !"log".equals(a);
    s.bounds = 0;
    s.airPress = 0L;
    tell(pr, "M2 armed for 60 s: " + (s.chain ? "SKIPPING BOUNDS - jump off something, then press jump right as you land (" + (long) B_BEFORE + " ms before to " + (long) B_AFTER + " ms after)." : "logging only - jump around, fall from heights."));
    return;
  }
  if (t.equals("m3") || t.equals("m10")) {
    s.logUntil = now + 30000L;
    s.airUntil = now + 30000L;
    s.airUsed = false;
    s.airCrouch = !"jump".equals(a);
    tell(pr, "M3 armed for 30 s: jump, then press JUMP" + (s.airCrouch ? " or CROUCH" : " (jump key only)") + " in mid-air (one free air jump). Every air edge is printed.");
    return;
  }
  if (t.equals("m4")) {
    s.fallUntil = now + 30000L;
    s.fallPct = @PKG@.MpLogic.dnum(a, 0.0, 0.0, 100.0);
    tell(pr, "M4 armed for 30 s: your FALL damage x " + f1(s.fallPct) + "% - jump off a 6+ block drop.");
    return;
  }
  if (t.equals("m5")) {
    int k = "lunge".equals(a) ? 2 : ("rise".equals(a) ? 3 : 1);
    s.rs = 0;
    s.sweep = false;
    s.pend = k;
    tell(pr, "M5 " + (k == 1 ? "vault" : (k == 2 ? "lunge" : "rise")) + " armed: it fires on the next tick - look where you want to go.");
    return;
  }
  if (t.equals("m6")) {
    s.hitAmt = @PKG@.MpLogic.dnum(a, HIT, 1.0, 100.0);
    s.sweep = true;
    s.kicked.clear();
    s.rs = 0;
    s.pend = 1;
    tell(pr, "M6 armed: a vault that kicks enemies on the way for " + f1(2.0 * s.hitAmt) + " each - aim it through a group of mobs.");
    return;
  }
  if (t.equals("m7") || t.equals("m8")) {
    s.hitAmt = @PKG@.MpLogic.dnum(a, HIT, 1.0, 100.0);
    s.rs = 1;
    s.sweep = false;
    s.pend = 3;
    s.airUntil = 0L;      // no m3 / vault free air jump during the rise: its crouch is the plunge, not an air jump
    s.airCrouch = false;
    tell(pr, "M7 armed: face 1-3 mobs within 3 blocks. Crouch near the top = plunge (M8 / M10 / M11).");
    return;
  }
  if (t.equals("m9")) {
    s.costs = !"off".equals(a);
    tell(pr, "M9 costs " + (s.costs ? "ON" : "OFF") + ": vault " + f1(C_VAULT_S) + "+" + f1(C_VAULT_M) + ", rise " + f1(C_RISE_S) + "+" + f1(C_RISE_M) + ", bound " + f1(C_BOUND_S) + "+" + f1(C_BOUND_M) + " (Stamina + Mana). " + statText(st, ref));
    return;
  }
  if (t.equals("m12")) {
    int secs = @PKG@.MpLogic.number(arg, 30, 5, 300);
    s.auraUntil = now + (long) secs * 1000L;
    s.auraNext = 0L;
    s.stamps.clear();
    s.combo = 0;
    s.hitsSeen = 0;
    s.auraNs = 0L; s.auraNsMax = 0L; s.auraScans = 0;
    tell(pr, "M12 armed for " + secs + " s: fight mobs with the Bo staff - every landed hit = 1 combo (5 s each, max " + (int) COMBO_MAX + ").");
    return;
  }
  help(pr);
}""")

# ---- MpTick: EntityTickingSystem on Player (one registerSystem per class), world thread, every tick
tick = mk("MpTick", T["ETS"])
F(tick, "public static boolean FAILED_ONCE = false;")
C(tick, "public MpTick() { super(); }")
M(tick, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(tick, "public boolean isParallel(int a, int b) { return false; }")
M(tick, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (chunk == null || @PKG@.MpCmds.STATES.isEmpty()) return;
    @PKG@.MpCmds.tickPlayer(chunk.getReferenceTo(idx), store, cb, dt);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.MpLog.warn("tick failed (logged once): " + t); }
  }
}""")

# ---- MpFallSys: DamageEventSystem in the FILTER group (SkyyArmory GrappleFallSys / SkyySkills AcroFallSys pattern), players only
fall = mk("MpFallSys", T["DES"])
F(fall, "public static boolean FAILED_ONCE = false;")
C(fall, "public MpFallSys() { super(); }")
M(fall, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(fall, "public @SG@ getGroup() { return @DMOD@.get().getFilterDamageGroup(); }")
M(fall, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@) || chunk == null || @PKG@.MpCmds.STATES.isEmpty()) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled() || !@PKG@.MpCmds.isFall(d.getCause())) return;
    if (@PKG@.MpCmds.MINE.containsKey(d)) return;          // our own re-dealt fall
    @PR@ pr = (@PR@) st.getComponent(chunk.getReferenceTo(idx), @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.MpCmds.onFall(d, pr);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.MpLog.warn("fall filter failed (logged once): " + t); }
  }
}""")

# ---- MpHitSys: DamageEventSystem in the INSPECT group (after ApplyDamage), any target: the combo count + the air-hit fling
hits = mk("MpHitSys", T["DES"])
F(hits, "public static boolean FAILED_ONCE = false;")
C(hits, "public MpHitSys() { super(); }")
M(hits, "public @QRY@ getQuery() { return @QRY@.any(); }")
M(hits, "public @SG@ getGroup() { return @DMOD@.get().getInspectDamageGroup(); }")
M(hits, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@) || chunk == null || @PKG@.MpCmds.STATES.isEmpty()) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled() || !(d.getAmount() > 0.0f)) { @PKG@.MpCmds.MINE.remove(d); return; }
    @PKG@.MpCmds.onHit(d, chunk.getReferenceTo(idx), buf);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.MpLog.warn("hit hook failed (logged once): " + t); }
  }
}""")

EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
# ---- /mprobe <what> <value>  (admin: requirePermission + no permission groups)
cmd2 = mk("MProbeArg2Cmd", T["APC"])
F(cmd2, "public @RA@ whatArg;")
F(cmd2, "public @RA@ valArg;")
C(cmd2, r"""
public MProbeArg2Cmd() {
  super("(admin) /mprobe <probe> <value>: m1 15, m1cap 6, m2 log, m3 jump, m4 0, m5 vault, m6 6, m7 6, m9 on, m12 30, slowfx <id>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.whatArg = withRequiredArg("probe", "m1, m1cap, m2, m3, m4, m5, m6, m7, m9, m12 or slowfx", @ATY@.STRING);
  this.valArg = withRequiredArg("value", "a number, a word (log, jump, vault, lunge, rise, on, off) or an effect id", @ATY@.STRING);
}""")
M(cmd2, EXEC + r""" {
  String a = null, v = null;
  try { a = String.valueOf(ctx.get(this.whatArg)); v = String.valueOf(ctx.get(this.valArg)); }
  catch (Throwable t) { @PKG@.MpLog.tell(pr, "Usage: /mprobe <probe> <value>"); return; }
  @PKG@.MpCmds.run(ref, store, pr, a, v);
}""")
# ---- /mprobe <what>
cmd1 = mk("MProbeArgCmd", T["APC"])
F(cmd1, "public @RA@ whatArg;")
C(cmd1, r"""
public MProbeArgCmd() {
  super("(admin) /mprobe <kit, m1 .. m13, xp, stats, stop>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.whatArg = withRequiredArg("probe", "kit, m1, m1cap, m2, m3, m4, m5, m6, m7, m9, m12, m13, xp, stats or stop", @ATY@.STRING);
}""")
M(cmd1, EXEC + r""" {
  String a = null;
  try { a = String.valueOf(ctx.get(this.whatArg)); }
  catch (Throwable t) { @PKG@.MpLog.tell(pr, "Usage: /mprobe <kit, m1 .. m13, xp, stats, stop>"); return; }
  @PKG@.MpCmds.run(ref, store, pr, a, null);
}""")
# ---- /mprobe (alias /monkprobe): the help list
cmd = mk("MProbeCmd", T["APC"])
C(cmd, r"""
public MProbeCmd() {
  super("mprobe", "(admin) Monk engine probes M1-M13 (throwaway dev pack): /mprobe lists them");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "monkprobe" });
  addUsageVariant(new @PKG@.MProbeArgCmd());
  addUsageVariant(new @PKG@.MProbeArg2Cmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.MpCmds.help(pr);
}""")

# ---- the plugin
pl = mk("SkyyMonkProbePlugin", T["JP"])
C(pl, "public SkyyMonkProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.MpLog.LOG = getLogger();
  getCommandRegistry().registerCommand(new @PKG@.MProbeCmd());
  getEntityStoreRegistry().registerSystem(new @PKG@.MpTick());
  getEntityStoreRegistry().registerSystem(new @PKG@.MpFallSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.MpHitSys());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyMonkProbe] @VERSION@ ready - /mprobe (admin): Monk probes M1-M13 (throwaway dev pack, remove after the test session)");
}""")
M(pl, r"""
protected void shutdown() {
  @PKG@.MpCmds.STATES.clear();
  @PKG@.MpCmds.MINE.clear();
  super.shutdown();
}""")

ALL = [log, lg, sta, cmds, tick, fall, hits, cmd2, cmd1, cmd, pl]
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d" % len(ALL))

jar = os.path.join(HERE, "SkyyMonkProbe-%s.jar" % VERSION)
man = B.manifest("SkyyMonkProbe", VERSION, "SkyWynn THROWAWAY dev pack: Monk engine probes M1-M13 (/mprobe, admin only) - slow fall, timed landings, air jump, fall damage, pushes, mob knock-up / hang / drag, costs, aura. Pinned for one test session, then removed.", PKG + ".SkyyMonkProbePlugin")
man["IncludesAssetPack"] = False   # class-only jar, like SkyyUiProbe 0.4 / SkyyClasses 0.1.13
B.assemble(jar, man, OUT, {})
