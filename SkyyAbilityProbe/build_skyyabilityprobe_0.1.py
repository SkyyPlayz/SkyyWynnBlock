"""SkyyAbilityProbe 0.1 - build script (javassist via jpype).
UNTESTED draft from a cloud session - cannot compile here (no HytaleServer.jar); never pin or deploy before the local session builds + reviews it.
A THROWAWAY dev / test pack like SkyyGatherProbe / SkyyReelProbe / SkyyMonkProbe: one op-only command, pinned for ONE test session after
review, then removed again. Nothing here is a feature; it only answers the class-ability ENGINE questions P1-P15 of
research/cloud/Class-Ability-Engine-Spec.md section 16 (step E0 of its build plan, section 15) before the engine (E1+) depends on them.
The plan, pass / fail rules and Skyy's test script: research/cloud/Ability-Probe-Plan.md.
Run:   python SkyyAbilityProbe/build_skyyabilityprobe_0.1.py   -> SkyyAbilityProbe/SkyyAbilityProbe-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
Check: python SkyyAbilityProbe/test_skyyabilityprobe_0.1.py    (bare JVM, -Xverify:all, pure logic, the state-reset rule, permissions)

SKYY'S LOCKS THE PROBES SERVE (docs/answered/classes.md): line 31 (2 class abilities on the two rune lines, built on runes), 104-105
(every weapon's hold is taken -> abilities need their own input), 112-114 (Mana Barrier: 12 s, Mana drain instead of Health, faint
see-through dome), 120-121 (boss stunlock breakout), 129 (Blood Frenzy costs per attack, hit or miss), 132-135 (Warlord's Banner),
145-147 (Shield Bubble 6 blocks / 12 s, Guardian Spirit passive save at 30% Health).

RUNS ON 0.6.8 AND 0.7: every Hytale 0.7 class (the rune / ability system) is reached by REFLECTION at run time, never named in Java, so
the jar compiles and loads on today's 0.6.8 server too. On 0.6.8 the rune probes (P1 P2 P3 P4 P14) answer "needs Hytale 0.7"; P5-P13 and
P15 work on both.

NO ASSETS: the jar ships no item, block, effect, particle or language file (manifest IncludesAssetPack false, asserted by the harness).
P1's "our own rune with a 1-step cast root" half needs a rune ITEM - that is an asset, so it is NOT here (E2 or a probe 0.2 with assets).

THE PROBES (/aprobe, alias /abilityprobe - never /abilities: vanilla 0.7 owns it; op only: requirePermission skyyabilityprobe.admin + no
permission groups on the root and every usage variant; every chat line also goes to the server log as "[SkyyAbilityProbe] ..."; state is
memory only, per player; ONE timed probe at a time per player - arming a probe ends the running one first and resets every probe field):
  p1 [cancel]        (0.7) 60 s: every InteractionChainStartEvent of yours (type, root id, held item); "cancel" cancels Ability2 / 3
                     chains and checks your Mana 1 s later (no stuck animation / cooldown / Mana spent?)
  p2 [secs]          (0.7) Primary chain starts vs your landed hits (default 20 s): do swings that MISS raise the event?
  p3 [dump]          (0.7) find the player's CooldownHandler (InteractionManager / Player getters), list its public methods to the log
  p3 read <rootId>   isOnCooldown / getCooldown for a rune's Cast root id (after a vanilla rune cast)
  p3 <method> <rootId> <secs>   call one handler method by name (String = rootId, numbers = secs) - the HUD-fill test
  p4 read | watch | put <slot> <itemId> | take <slot> | bad <slot>    (0.7) the AbilitySlots section (-11): read, 60 s
                     InventoryChangeEvent watch, write a rune by code, remove it, and try a NON-rune (the held item) into a slot
  p5 [secs] | p5 save  damage order: each hit to / from you printed at our FILTER system BEFORE ArmorDamageReduction, our FILTER system
                     AFTER it, and the INSPECT group (landed); "save" = the next lethal hit on you is cancelled in the late filter and
                     Health set to 30% (the Guardian Spirit shape)
  p6 [effectId|none] [secs]  swing / hit gaps with an extra status effect kept on you (re-put every 0.5 s; counts how often another
                     system took it off - SkyyGear's speed tiers do that)
  p7 [secs]          every 0.25 s subtract 0.5 Mana + 0.25 Stamina while SkyySkills regen runs: exact? does regen keep going?
  p8 [hits/s] [secs] | p8 stun   probe hits (no knockback) on the nearest enemy: does it still attack you? / the vanilla Stun 1.5 s
  p9 <particleId> [radius]       a faint dome look for 12 s: 16 particles on a ground ring + 8 on an upper ring every 0.5 s
  p10 [secs]         a 6-block "bubble" where you stand: every 0.25 s every projectile inside that is not yours is removed
  p11 <blockId> [secs]           a temporary "banner" block 2 blocks in front of you (empty spot only), removed after secs (default 10)
  p12 | p12 stun     the nearest NPC's targeting methods dumped to the log / the vanilla Stun 1 s on it and its hits on you after
  p13 [zones] [secs] getAllEntitiesInSphere cost: zones x 4 Hz scans (radius 8) around you + the world tick rate (default 48, 10 s)
  p14                (0.7) your rune sections -11 / -12 + your SkyyProfiles profile key (run, switch profile, run again)
  p15                Mana: your value / max, the Mana stat type's own max (0.6.8: 0, 0.7: 100) - compare with /skills mana
  info | stats | stop

ENGINE PATHS (from live Skyy scripts - research/cloud/Ability-Probe-Plan.md cites file + line for each):
  damage filters + order    DamageEventSystem in DamageModule.getFilterDamageGroup() with getDependencies() = SystemDependency(Order
                            .BEFORE / AFTER, DamageSystems$ArmorDamageReduction) (SkyyArmory ArmoryTuneSys, SkyyGear GearHitSys /
                            GearArmorSys); landed amounts in getInspectDamageGroup() (SkyyClasses PriestHealSys, SkyyArmory ArmoryHitSys)
  probe hits                DamageSystems.executeDamage(target, CommandBuffer, new Damage(new Damage$EntitySource(you), PROJECTILE, n))
                            (SkyyArmory ArmoryTrav.hit; SkyyMonkProbe)
  status effects            EffectControllerComponent.addEffect(ref, effect, secs, OverlapBehavior.OVERWRITE, acc), getActiveEffects()
                            (SkyyArmory ArmoryTree.stun = the vanilla "Stun", SkyyGear GearSpeed.put)
  particles                 ParticleUtil.spawnParticleEffect(String, Vector3dc, ComponentAccessor) (SkyyArmory ArmoryTrav.particle)
  projectiles               ProjectileComponent / StandardPhysicsProvider getCreatorUuid (SkyyClasses ShotTrack), CommandBuffer
                            .removeEntity(ref, RemoveReason.REMOVE) (SkyyArmory Leap.onBowShot)
  blocks                    World.getChunkIfLoaded + WorldChunk.getBlock / setBlock (SkyyIslands FillTask); ChunkUtil.indexChunkFromBlock
                            is NEW (build-time probe; P11 is left out of the jar when it is missing)
  stats                     EntityStatMap.subtractStatValue / setStatValue, EntityStatType.getAssetMap().getAsset(i).getMax()
                            (SkyyArmory Leap.take, SkyySkills Overall.typeMax)
  NEW (no Skyy script does it): InteractionChainStartEvent, the CooldownHandler, the AbilitySlots / RuneBag components (0.7, reflection),
  NPC targeting (P12 only dumps candidate method names), setting a block outside chunk (0,0).
REVIEW FIXES (2026-10-11, Copilot on PR 13):
  R1. P8 probe hits never kill (a kill = real kill rewards, and the probe would end early): hit() skips at Health <= 2 / unreadable and
      caps at Health - 1 (SkyyMonkProbe R1's shape); our late filter clamps a MINE hit again to the target's Health - 1 after armour
      (cancels it at <= 1 / unreadable); p8Tick ends the probe once the mob is at <= 2 Health. Residual: a filter of another mod ordered
      AFTER ours could still raise the amount - P8 says so if the mob dies.
  R3. AbRefl.fill gives int / long parameters the requested secs too (truncated; units unknown - the P3 line prints the signature).
  R5. P7 pays both costs or neither: both balances are checked first; a step either balance cannot pay counts as short, nothing spent.
  R6. P5 catches a cancel AFTER our late filter: every hit our late filter passed is counted (p5Late), every one that lands uncancelled
      in Inspect too (p5Landed); the tick reports a missing one at once, the summary says FAIL. MINE / EARLY / LATE are identity maps
      (SkyyArmory ArmoryTrav.MINE's shape): a filter changing the amount can never break the lookup.
  Rejected: removeItemStackFromSlot(short) (one argument) exists - pinned SkyySacks 0.7.17 (lines 4766, 6951) and SkyyGear 0.2.23
      (lines 22107, 23048) compile and run it on an ItemContainer.
"""
import sys, os, json, zipfile, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

if "--deploy" in sys.argv:
    raise SystemExit("SkyyAbilityProbe: --deploy is not supported here - deploys go through tools/deploy_set.py")

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
NODE = "skyyabilityprobe.admin"
PKG = "com.skyy.abilprobe"
# Hytale 0.7 classes (research/Hytale-Runes-Research.md 1.2 + 6, VERIFIED in 0.7.0-pre.4) - reached by reflection only
CHAIN_EVT = "com.hypixel.hytale.server.core.modules.interaction.event.InteractionChainStartEvent"
ABSLOTS = "com.hypixel.hytale.server.core.inventory.InventoryComponent$AbilitySlots"
RUNEBAG = "com.hypixel.hytale.server.core.inventory.InventoryComponent$RuneBag"
ADRS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction"
STUN_FX = "Stun"         # the vanilla Stun effect (SkyyArmory 0.1.9 asserts it: Status/Stun.json, movement disabled)
NPC_KW = "target,mark,lock,aggro,attitude,combat,hostile,forget,clear,attack"

# ================= the probe numbers (research/cloud/Class-Ability-Engine-Spec.md sections 10 / 13 / 14; probe values, not balance) =================
N = {
    "SAVE_PCT": 30.0,      # Guardian Spirit saved Health % (docs/answered/classes.md line 145; row gs.health)
    "P7_MANA": 0.5, "P7_STAM": 0.25, "P7_STEP": 250.0,      # 2 Mana + 1 Stamina per second (a toggle drain's shape)
    "P8_AMT": 1.0, "P8_STUN": 1.5, "P8_RANGE": 6.0,          # probe hit size, stun.immune 1.5 s, the target search radius
    "P9_STEP": 500.0,      # particles at most every 0.5 s per effect (spec section 14)
    "P10_R": 6.0, "P10_STEP": 250.0,                          # Shield Bubble 6 blocks (line 145), the 0.25 s zone tick
    "P12_RANGE": 8.0, "P12_STUN": 1.0,
    "P13_R": 8.0, "P13_HZ": 4.0, "P13_RING": 10.0, "P13_LIMIT_US": 1000.0,   # Sanctuary 8 blocks, abil.tick 0.25 s, the 1 ms budget
    "GAP_MAX": 1500.0,     # swing / hit gaps longer than this are pauses, not counted
}

az = zipfile.ZipFile(ASSETS)
NAMES = az.namelist()
NAMESET = set(NAMES)


def vanilla_json(path):
    return json.loads(az.read(path).decode("utf-8-sig"))


def ascii_line(s, n=600):
    return re.sub(r"[^\x20-\x7e]", "?", str(s))[:n]


_stun = "Server/Entity/Effects/Status/Stun.json"
if _stun not in NAMESET or vanilla_json(_stun)["ApplicationEffects"]["MovementEffects"].get("DisableAll") is not True:
    raise SystemExit("the vanilla Stun effect changed - SkyyArmory 0.1.9 asserts the same (P8 / P12 use it)")

# ---- desk reads at build time (printed + shipped as text lines for /aprobe info; ids and numbers only, nothing vanilla is committed)
DESK = []
_mana = "Server/Entity/Stats/Mana.json"
MANA_MAX = vanilla_json(_mana).get("Max") if _mana in NAMESET else None
DESK.append("P15 desk: Server/Entity/Stats/Mana.json Max = %s (0.6.8: 0, 0.7.0-pre.4: 100 - research/Hytale-Runes-Research.md 1.1)" % MANA_MAX)
_PKW = re.compile(r"(?i)ring|shield|barrier|bubble|dome|aura|circle|ward")
PARTICLES = sorted(set(n.rsplit("/", 1)[1].rsplit(".", 1)[0] for n in NAMES
                       if "Particles/" in n and n.lower().endswith((".particlesystem", ".json")) and _PKW.search(n.rsplit("/", 1)[1])))
DESK.append("P9 desk: %d particle ids with ring / shield / barrier / bubble / dome / aura / circle / ward: %s" % (len(PARTICLES), ", ".join(PARTICLES[:20]) or "none found - pass an id by hand"))
BANNERS = sorted(set(n.rsplit("/", 1)[1][:-5] for n in NAMES
                     if n.startswith("Server/Item/Items/") and n.endswith(".json") and "banner" in n.rsplit("/", 1)[1].lower()))
DESK.append("P11 desk: %d item / block ids with 'banner': %s" % (len(BANNERS), ", ".join(BANNERS[:12]) or "none found"))
RUNES = []
for _n in sorted(NAMES):
    if _n.startswith("Server/Item/Items/Rune/") and _n.endswith(".json"):
        try:
            _d = vanilla_json(_n)
        except Exception:
            continue
        _ab = _d.get("Ability") if isinstance(_d, dict) else None
        if isinstance(_ab, dict):
            RUNES.append("%s (Slot %s, Cast %s, Cooldown %s, Cost %s %s)" % (_n.rsplit("/", 1)[1][:-5], _ab.get("Slot"), ascii_line(_ab.get("Cast"), 80),
                                                                         _ab.get("Cooldown"), _ab.get("Cost"), _ab.get("CostType")))
DESK.append("P1/P3 desk: %d rune items (Hytale 0.7): %s" % (len(RUNES), "; ".join(RUNES[:8]) or "none (0.6.8 assets)"))
for _l in DESK:
    print(_l)
DESK = [ascii_line(x) for x in DESK]

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
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
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "ESTT": "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType",
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "EES": "com.hypixel.hytale.component.system.EntityEventSystem",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "CAC": "com.hypixel.hytale.component.ComponentAccessor",
    "CTYPE": "com.hypixel.hytale.component.ComponentType",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "SG": "com.hypixel.hytale.component.SystemGroup",
    "SDEP": "com.hypixel.hytale.component.dependency.SystemDependency",
    "ORD": "com.hypixel.hytale.component.dependency.Order",
    "REMR": "com.hypixel.hytale.component.RemoveReason",
    "DES": "com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem",
    "DMOD": "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
    "DMG": "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
    "DENT": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource",
    "DCS": "com.hypixel.hytale.server.core.modules.entity.damage.DamageCause",
    "DSYS": "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems",
    "DTH": "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "V3D": "org.joml.Vector3d",
    "TU": "com.hypixel.hytale.server.core.util.TargetUtil",
    "XFM": "com.hypixel.hytale.math.vector.Transform",
    "NPC": "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "ECC": "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent",
    "EFX": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect",
    "OVB": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.OverlapBehavior",
    "I2O": "it.unimi.dsi.fastutil.ints.Int2ObjectMap",
    "PTU": "com.hypixel.hytale.server.core.universe.world.ParticleUtil",
    "LPC": "com.hypixel.hytale.server.core.entity.entities.ProjectileComponent",
    "SPP": "com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsProvider",
    "ICE": "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent",
    "IMOD": "com.hypixel.hytale.server.core.modules.interaction.InteractionModule",
    "WCH": "com.hypixel.hytale.server.core.universe.world.chunk.WorldChunk",
    "CHU": "com.hypixel.hytale.math.util.ChunkUtil",
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
# every member below is already used by a live Skyy build script (research/cloud/Ability-Probe-Plan.md section 1 names file + line)
for c, m in ((T["AC"], "requirePermission"), (T["AC"], "setPermissionGroups"), (T["AC"], "addAliases"), (T["AC"], "addUsageVariant"),
             (T["AC"], "withRequiredArg"), (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["PR"], "getUuid"), (T["PR"], "getComponentType"), (T["MSG"], "raw"), (T["HSV"], "SCHEDULED_EXECUTOR"),
             (T["PLA"], "getComponentType"), (T["INVC"], "getItemInHand"), (T["IC"], "getCapacity"), (T["IC"], "getItemStack"),
             (T["IC"], "addItemStackToSlot"), (T["IC"], "removeItemStackFromSlot"), (T["IS"], "getItemId"), (T["IS"], "isEmpty"),
             (T["IS"], "getQuantity"), (T["ESM"], "getComponentType"), (T["ESM"], "get"), (T["ESM"], "subtractStatValue"),
             (T["ESM"], "setStatValue"), (T["ESV"], "get"), (T["ESV"], "getMax"), (T["DST"], "getStamina"), (T["DST"], "getMana"),
             (T["DST"], "getHealth"), (T["ESTT"], "getAssetMap"), (T["ESTT"], "getMax"), (T["ETS"], "tick"), (T["ETS"], "isParallel"),
             (T["ACH"], "getReferenceTo"), (T["DMOD"], "get"), (T["DMOD"], "getFilterDamageGroup"), (T["DMOD"], "getInspectDamageGroup"),
             (T["DMG"], "getCause"), (T["DMG"], "getAmount"), (T["DMG"], "isCancelled"), (T["DMG"], "setCancelled"), (T["DMG"], "setAmount"), (T["DMG"], "getSource"),
             (T["DCS"], "PROJECTILE"), (T["DCS"], "getId"), (T["DSYS"], "executeDamage"), (T["DENT"], "getRef"),
             (T["ORD"], "BEFORE"), (T["ORD"], "AFTER"), (T["REMR"], "REMOVE"), (T["TC"], "getComponentType"), (T["TC"], "getPosition"),
             (T["TU"], "getAllEntitiesInSphere"), (T["TU"], "getLook"), (T["XFM"], "getDirection"), (T["XFM"], "getPosition"),
             (T["NPC"], "getComponentType"), (T["DTH"], "getComponentType"), (T["ECC"], "getComponentType"), (T["ECC"], "addEffect"),
             (T["ECC"], "getActiveEffects"), (T["EFX"], "getAssetMap"), (T["OVB"], "OVERWRITE"), (T["I2O"], "get"),
             (T["PTU"], "spawnParticleEffect"), (T["LPC"], "getComponentType"), (T["LPC"], "getCreatorUuid"), (T["SPP"], "getComponentType"),
             (T["SPP"], "getCreatorUuid"), (T["ICE"], "getItemContainer"), (T["IMOD"], "get"), (T["IMOD"], "getInteractionManagerComponent"),
             (T["CB"], "removeEntity"), (T["CB"], "getComponent"), ("com.hypixel.hytale.component.Ref", "isValid"),
             (T["WLD"], "execute"), (PB, "getCommandRegistry"), (PB, "getEntityStoreRegistry"), (PB, "getLogger"), (PB, "shutdown")):
    B.probe(pool, c, m)
# exact signatures of the calls whose shape matters most (a re-typed parameter stops the build, not the test session)
def _d(cn):
    return "L" + cn.replace(".", "/") + ";"
_V = _d(T["V3D"])
for c, m, d in ((T["TU"], "getAllEntitiesInSphere", "(" + _V + "D" + _d(T["CAC"]) + ")Ljava/util/List;"),
                (T["DSYS"], "executeDamage", "(" + _d(T["REF"]) + _d(T["CB"]) + _d(T["DMG"]) + ")V"),
                (T["ESM"], "subtractStatValue", "(IF)F"),
                (T["ECC"], "addEffect", "(" + _d(T["REF"]) + _d(T["EFX"]) + "F" + _d(T["OVB"]) + _d(T["CAC"]) + ")Z"),
                (T["PTU"], "spawnParticleEffect", "(Ljava/lang/String;Lorg/joml/Vector3dc;" + _d(T["CAC"]) + ")V"),
                (T["CB"], "removeEntity", "(" + _d(T["REF"]) + _d(T["REMR"]) + ")V"),
                (T["SDEP"], "<init>", "(" + _d(T["ORD"]) + "Ljava/lang/Class;)V")):
    try:
        if m == "<init>":
            pool.get(c).getConstructor(d)
        else:
            pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
try:
    pool.get(T["EES"]).getConstructor("(Ljava/lang/Class;)V")
except Exception as _e:
    raise SystemExit("EntityEventSystem(Class) constructor missing (SkyyGear event_system relies on it): %s" % _e)
if pool.getOrNull(ADRS) is None:
    raise SystemExit("DamageSystems$ArmorDamageReduction is gone - SkyyArmory / SkyyGear order their filters against it")

# ---- Hytale 0.7 presence (printed only: the jar runs on both)
V07 = dict((k, pool.getOrNull(c) is not None) for k, c in (("InteractionChainStartEvent", CHAIN_EVT), ("AbilitySlots", ABSLOTS),
                                                            ("RuneBag", RUNEBAG)))
_sj = zipfile.ZipFile(J["server_jar"])
COOLDOWN_CLASSES = sorted(n[:-6].replace("/", ".") for n in _sj.namelist() if n.endswith(".class") and "CooldownHandler" in n)
DESK.append("0.7 desk: this server jar has %s; CooldownHandler classes: %s" % (
    ", ".join("%s %s" % (k, "YES" if v else "no") for k, v in sorted(V07.items())), ", ".join(COOLDOWN_CLASSES[:4]) or "none"))
print(DESK[-1])

# ---- P11 needs ChunkUtil.indexChunkFromBlock (NEW: no Skyy script uses it; SkyyIslands only writes chunk (0, 0)). Missing -> P11 not built.
P11_BUILT = True
try:
    B.probe(pool, T["CHU"], "indexChunkFromBlock")
    pool.get(T["CHU"]).getMethod("indexChunkFromBlock", "(II)J")
    pool.get(T["WLD"]).getMethod("getChunkIfLoaded", "(J)" + _d(T["WCH"]))
    pool.get(T["WCH"]).getMethod("getBlock", "(III)I")
    pool.get(T["WCH"]).getMethod("setBlock", "(IIILjava/lang/String;)Z")
except BaseException as _e:            # B.probe raises SystemExit
    P11_BUILT = False
    print("P11 NOT BUILT (block API differs: %s) - /aprobe p11 will say so; the other probes are unaffected" % _e)

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


# ---- AbLog: server log + chat. SINK (harness hook, null in game) also receives every chat line.
log = mk("AbLog")
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.List SINK;")
M(log, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyAbilityProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyAbilityProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void tell(@PR@ pr, String s) {
  info((pr == null ? "" : "to " + pr.getUsername() + ": ") + s);
  try { if (SINK != null) SINK.add(s); } catch (Throwable t) { }
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[AbilityProbe] " + s)); } catch (Throwable t) { }
}""")

# ---- AbLogic: pure functions (no engine objects) - the harness calls them directly
lg = mk("AbLogic")
M(lg, r"""
public static String f1(double v) {
  if (v != v) return "?";
  long t = Math.round(v * 10.0);
  String sign = t < 0L ? "-" : "";
  if (t < 0L) t = 0L - t;
  return sign + (t / 10L) + "." + (t % 10L);
}""")
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
# word i of the command (null = missing / blank); kept in its own case (ids are case-sensitive)
M(lg, r"""
public static String word(String[] w, int i) {
  if (w == null || i < 0 || i >= w.length || w[i] == null) return null;
  String t = w[i].trim();
  return t.length() == 0 ? null : t;
}""")
M(lg, r"""
public static String low(String s) {
  return s == null ? null : s.toLowerCase(java.util.Locale.ROOT);
}""")
M(lg, r"""
public static double avg(long sum, int n) {
  return n <= 0 ? 0.0 : (double) sum / (double) n;
}""")
M(lg, r"""
public static double perSec(long count, long ms) {
  if (ms <= 0L) return 0.0;
  return (double) count * 1000.0 / (double) ms;
}""")
# point i of n on a circle of radius r around (cx, cz)
M(lg, r"""
public static double[] ring(double cx, double cz, double r, int i, int n) {
  if (n < 1) n = 1;
  double a = 2.0 * Math.PI * (double) i / (double) n;
  return new double[] { cx + r * Math.cos(a), cz + r * Math.sin(a) };
}""")
# a hit of 'amount' on 'health' kills (the Guardian Spirit trigger)
M(lg, r"""
public static boolean lethal(double health, double amount) {
  return amount > 0.0 && health > 0.0 && health - amount <= 0.0;
}""")
# the saved Health: pct % of max, at least 1, never above max
M(lg, r"""
public static float saveHealth(double max, double pct) {
  double v = max * pct / 100.0;
  if (v < 1.0) v = 1.0;
  if (max > 0.0 && v > max) v = max;
  return (float) v;
}""")
# a subtract that did not land exactly (before - cost != after): a write fight with another system
M(lg, r"""
public static boolean fight(double before, double cost, double after, double eps) {
  double d = after - (before - cost);
  if (d < 0.0) d = 0.0 - d;
  return d > eps;
}""")
M(lg, r"""
public static boolean slotOk(int s) {
  return s >= 0 && s <= 5;
}""")
M(lg, r"""
public static int floorI(double v) {
  return (int) Math.floor(v);
}""")
# a gap between two swings / hits that counts (a longer gap is a pause)
M(lg, r"""
public static boolean gapOk(long gap, long max) {
  return gap > 0L && gap <= max;
}""")
# chain type text -> 1 ability (Ability2 / Ability3), 2 primary, 0 other
M(lg, r"""
public static int kind(String type) {
  if ("Ability2".equals(type) || "Ability3".equals(type)) return 1;
  if ("Primary".equals(type)) return 2;
  return 0;
}""")
M(lg, r"""
public static String swingVerdict(int swings, int hits) {
  if (swings <= 0) return "NO SWINGS SEEN (FAIL: Primary chains do not raise the event, or you did not swing)";
  if (swings > hits) return "PASS (" + swings + " swings, " + hits + " landed hits: the misses were seen)";
  return "UNCLEAR (" + swings + " swings, " + hits + " landed hits: swing at the air too)";
}""")
M(lg, r"""
public static String budget(double usPerTick, double limitUs) {
  return (usPerTick < limitUs ? "PASS" : "OVER") + " (" + f1(usPerTick) + " us per tick, budget " + f1(limitUs) + ")";
}""")

# ---- AbRefl: reflection helpers for the Hytale 0.7 classes (never throw)
rf = mk("AbRefl")
M(rf, r"""
public static Class cls(String n) {
  try { return Class.forName(n); } catch (Throwable t) { return null; }
}""")
M(rf, r"""
public static String cut(String s, int n) {
  if (s == null) return "null";
  return s.length() <= n ? s : s.substring(0, n) + "...";
}""")
M(rf, r"""
public static java.lang.reflect.Method m0(Object o, String name) {
  if (o == null || name == null) return null;
  try {
    java.lang.reflect.Method[] ms = o.getClass().getMethods();
    for (int i = 0; i < ms.length; i++) if (ms[i].getName().equals(name) && ms[i].getParameterTypes().length == 0) return ms[i];
  } catch (Throwable t) { }
  return null;
}""")
M(rf, r"""
public static Object call0(Object o, String name) {
  java.lang.reflect.Method m = m0(o, name);
  if (m == null) return null;
  try { return m.invoke(o, new Object[0]); } catch (Throwable t) { return null; }
}""")
M(rf, r"""
public static Object static0(String cn, String name) {
  try {
    Class c = Class.forName(cn);
    java.lang.reflect.Method m = c.getMethod(name, new Class[0]);
    return m.invoke(null, new Object[0]);
  } catch (Throwable t) { return null; }
}""")
# cancel a cancellable event (setCancelled(true)); true = it reads back as cancelled
M(rf, r"""
public static boolean cancel(Object ev) {
  if (ev == null) return false;
  try {
    java.lang.reflect.Method m = ev.getClass().getMethod("setCancelled", new Class[] { Boolean.TYPE });
    m.invoke(ev, new Object[] { Boolean.TRUE });
    return Boolean.TRUE.equals(call0(ev, "isCancelled"));
  } catch (Throwable t) { return false; }
}""")
M(rf, r"""
public static String simple(Class c) {
  return c == null ? "null" : c.getSimpleName();
}""")
M(rf, r"""
public static String sig(java.lang.reflect.Method m) {
  StringBuilder b = new StringBuilder();
  b.append(m.getName()).append("(");
  Class[] ps = m.getParameterTypes();
  for (int i = 0; i < ps.length; i++) {
    if (i > 0) b.append(", ");
    b.append(simple(ps[i]));
  }
  b.append(") -> ").append(simple(m.getReturnType()));
  return b.toString();
}""")
M(rf, r"""
public static boolean hit(String lname, String kws) {
  if (kws == null || kws.length() == 0) return true;
  String[] k = kws.split(",");
  for (int i = 0; i < k.length; i++) if (k[i].length() > 0 && lname.indexOf(k[i]) >= 0) return true;
  return false;
}""")
# every public method of o (not java.lang.Object's) whose lower-case name holds a keyword (kws "" = all): one line each into out
M(rf, r"""
public static int dump(Object o, String kws, java.util.List out, String prefix) {
  if (o == null || out == null) return 0;
  int n = 0;
  try {
    java.lang.reflect.Method[] ms = o.getClass().getMethods();
    for (int i = 0; i < ms.length; i++) {
      if (ms[i].getDeclaringClass() == Object.class) continue;
      if (!hit(ms[i].getName().toLowerCase(java.util.Locale.ROOT), kws)) continue;
      out.add(prefix + o.getClass().getName() + "." + sig(ms[i]));
      n++;
    }
  } catch (Throwable t) { out.add(prefix + "dump failed: " + t); }
  return n;
}""")
# the first public zero-argument method of o whose return type's class name holds kw, its value (null = none); where gets its name
M(rf, r"""
public static Object findBy(Object o, String kw, StringBuilder where) {
  if (o == null || kw == null) return null;
  try {
    java.lang.reflect.Method[] ms = o.getClass().getMethods();
    for (int i = 0; i < ms.length; i++) {
      if (ms[i].getParameterTypes().length != 0) continue;
      if (ms[i].getReturnType().getName().indexOf(kw) < 0) continue;
      Object v = ms[i].invoke(o, new Object[0]);
      if (v != null) {
        if (where != null) where.append(o.getClass().getSimpleName()).append(".").append(ms[i].getName()).append("()");
        return v;
      }
    }
  } catch (Throwable t) { }
  return null;
}""")
# parameters from what a command gives: String = id, float / double / int / long = secs (int / long truncated; units unknown - P3 prints
# the signature it called; float[] = { secs }), boolean = false; null = cannot
M(rf, r"""
public static Object[] fill(Class[] ps, String id, double secs) {
  Object[] a = new Object[ps.length];
  for (int i = 0; i < ps.length; i++) {
    String n = ps[i].getName();
    if (n.equals("java.lang.String")) a[i] = id;
    else if (n.equals("float") || n.equals("java.lang.Float")) a[i] = Float.valueOf((float) secs);
    else if (n.equals("double") || n.equals("java.lang.Double")) a[i] = Double.valueOf(secs);
    else if (n.equals("int")) a[i] = Integer.valueOf((int) secs);
    else if (n.equals("long")) a[i] = Long.valueOf((long) secs);
    else if (n.equals("boolean")) a[i] = Boolean.FALSE;
    else if (n.equals("[F")) a[i] = new float[] { (float) secs };
    else return null;
  }
  return a;
}""")
# a value as text: class + toString, and for a non-JDK object its public zero-argument get / is / has values (at most 12)
M(rf, r"""
public static String describe(Object r) {
  if (r == null) return "null";
  StringBuilder b = new StringBuilder();
  b.append(r.getClass().getSimpleName()).append(" ").append(cut(String.valueOf(r), 160));
  if (r.getClass().getName().startsWith("java.")) return b.toString();
  try {
    java.lang.reflect.Method[] ms = r.getClass().getMethods();
    int n = 0;
    for (int i = 0; i < ms.length && n < 12; i++) {
      java.lang.reflect.Method m = ms[i];
      if (m.getDeclaringClass() == Object.class || m.getParameterTypes().length != 0) continue;
      String nm = m.getName();
      if (!(nm.startsWith("get") || nm.startsWith("is") || nm.startsWith("has"))) continue;
      Object v = null;
      try { v = m.invoke(r, new Object[0]); } catch (Throwable t2) { v = "threw " + t2.getClass().getSimpleName(); }
      b.append("; ").append(nm).append("=").append(cut(String.valueOf(v), 60));
      n++;
    }
  } catch (Throwable t) { }
  return b.toString();
}""")
# the public method 'name' with the fewest parameters fill() can fill: called, its result as text (never throws)
M(rf, r"""
public static String invoke(Object o, String name, String id, double secs) {
  if (o == null) return "no object";
  try {
    java.lang.reflect.Method[] ms = o.getClass().getMethods();
    java.lang.reflect.Method best = null;
    Object[] args = null;
    for (int i = 0; i < ms.length; i++) {
      if (!ms[i].getName().equals(name)) continue;
      Object[] a = fill(ms[i].getParameterTypes(), id, secs);
      if (a == null) continue;
      if (best == null || a.length < args.length) { best = ms[i]; args = a; }
    }
    if (best == null) return "no public " + name + "(...) with only String / number / boolean parameters on " + o.getClass().getName();
    Object r = best.invoke(o, args);
    return sig(best) + " returned " + describe(r);
  } catch (Throwable t) { return name + " threw " + t; }
}""")

# ---- AbState: one player's probe state (world thread; one per player in AbCmds.STATES). EVERY probe field is reset by AbCmds.clear
#      (the harness sets each field and checks clear() resets it - the SkyyMonkProbe review found stale timers / armed flags).
STATE_FIELDS = [
    # the running timed probe: mode 0 none, else the probe number; every hook also checks now < modeUntil (a disconnected player's
    # state can never act after its window, tick or no tick)
    ("int", "mode"), ("long", "modeUntil"), ("long", "armedAt"), ("int", "lines"),
    # P1 / P2 / P6 chain starts (0.7)
    ("boolean", "cancel"), ("int", "chains"), ("int", "chainAb"), ("int", "chainPrim"), ("int", "chainOther"), ("int", "cancelled"),
    ("int", "cancelFail"), ("long", "p1CheckAt"), ("double", "p1Mana"),
    # landed hits + gaps (P2 / P6)
    ("int", "hits"), ("long", "lastHit"), ("long", "hitGapSum"), ("int", "hitGapN"), ("long", "lastSwing"), ("long", "swGapSum"),
    ("int", "swGapN"),
    # P4 watch
    ("int", "invSlots"), ("int", "invBag"), ("int", "invOther"),
    # P5
    ("boolean", "save"), ("int", "saves"), ("int", "p5Seen"), ("int", "p5Changed"),
    # hits our late filter passed / of those, landed uncancelled in Inspect / missing ones already told (REVIEW FIX R6)
    ("int", "p5Late"), ("int", "p5Landed"), ("int", "p5Lost"),
    # P6
    ("String", "fxId"), ("int", "fxIdx"), ("int", "fxPuts"), ("int", "fxGone"), ("long", "fxNext"), ("boolean", "fxPut"),
    # P7
    ("long", "p7Next"), ("int", "p7Steps"), ("int", "p7Short"), ("int", "p7Fights"), ("double", "p7SpentM"), ("double", "p7SpentS"),
    ("double", "p7RegenM"), ("double", "p7RegenS"), ("double", "p7LastM"), ("double", "p7LastS"),
    # P8 / P12 (target = the mob's Ref, typed Object so the harness can set it)
    ("Object", "target"), ("long", "p8Next"), ("long", "p8Gap"), ("int", "p8Sent"), ("int", "mobHits"), ("boolean", "p8Stun"),
    # P9 / P10 / P13 anchor
    ("double", "ax"), ("double", "ay"), ("double", "az"), ("double", "radius"), ("String", "fxName"), ("long", "p9Next"), ("int", "p9Calls"),
    ("int", "p9Fail"),
    # P10
    ("long", "p10Next"), ("int", "p10Seen"), ("int", "p10Removed"), ("int", "p10Own"), ("int", "p10Scans"), ("long", "p10Ns"),
    ("long", "p10Max"), ("HashSet", "removed"),
    # P13
    ("int", "zones"), ("double", "p13Acc"), ("int", "p13Idx"), ("long", "p13Ticks"), ("long", "p13Scans"), ("long", "p13Ents"),
    ("long", "p13Ns"), ("long", "p13Max"),
]
KEEP_FIELDS = [("java.util.UUID", "u"), ("@REF@", "ref"), ("@ST@", "st"), ("long", "ns"), ("long", "nsMax"), ("long", "ticks")]
_JT = {"HashSet": "java.util.HashSet"}
sta = mk("AbState")
for t, n in KEEP_FIELDS + STATE_FIELDS:
    F(sta, "public %s %s;" % (_JT.get(t, t), n))
C(sta, r"""
public AbState(java.util.UUID u, @REF@ r, @ST@ st) {
  this.u = u;
  this.ref = r;
  this.st = st;
  this.removed = new java.util.HashSet();
  this.fxId = "";
  this.fxName = "";
  this.fxIdx = -1;
  this.p7LastM = -1.0;
  this.p7LastS = -1.0;
}""")


def _reset(t, n):
    if t == "HashSet":
        return "  s.%s.clear();" % n
    if t == "String":
        return '  s.%s = "";' % n
    if t == "Object":
        return "  s.%s = null;" % n
    if t == "boolean":
        return "  s.%s = false;" % n
    if t == "double":
        return "  s.%s = %s;" % (n, "-1.0" if n in ("p7LastM", "p7LastS") else "0.0")
    if t == "long":
        return "  s.%s = 0L;" % n
    return "  s.%s = %s;" % (n, "-1" if n == "fxIdx" else "0")


# ---- AbUnplace: P11's timed block removal. Scheduler thread (stage 0) -> the block's own world thread (stage 1); it removes the block
#      only while it is still the one we placed, so it never touches a block someone put there later. PLACED = what is still out there.
unp = mk("AbUnplace")
unp.addInterface(pool.get("java.lang.Runnable"))
for f in ("public static final java.util.concurrent.ConcurrentHashMap PLACED = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile String LAST = \"no P11 block yet\";",
          "public @WLD@ world;", "public int x;", "public int y;", "public int z;", "public int want;", "public int stage;", "public String key;"):
    F(unp, f)
C(unp, r"""
public AbUnplace(@WLD@ w, int x, int y, int z, int want) {
  this.world = w;
  this.x = x;
  this.y = y;
  this.z = z;
  this.want = want;
  this.stage = 0;
  this.key = x + " " + y + " " + z;
}""")
if P11_BUILT:
    M(unp, r"""
public void run() {
  try {
    if (this.stage == 0) { this.stage = 1; this.world.execute(this); return; }
    @WCH@ c = this.world.getChunkIfLoaded(@CHU@.indexChunkFromBlock(this.x, this.z));
    if (c == null) { LAST = "P11: the chunk at " + this.key + " is not loaded - the probe block STAYS there: remove it by hand"; @PKG@.AbLog.warn(LAST); return; }
    int now = c.getBlock(this.x, this.y, this.z);
    if (now != this.want) { PLACED.remove(this.key); LAST = "P11: the block at " + this.key + " changed (" + now + ") - left alone"; @PKG@.AbLog.info(LAST); return; }
    boolean ok = c.setBlock(this.x, this.y, this.z, "Empty");
    int after = c.getBlock(this.x, this.y, this.z);
    if (ok && after == 0) { PLACED.remove(this.key); LAST = "P11: the block at " + this.key + " was removed cleanly (PASS)"; @PKG@.AbLog.info(LAST); }
    else { LAST = "P11: removing the block at " + this.key + " FAILED (setBlock " + ok + ", block now " + after + ") - remove it by hand"; @PKG@.AbLog.warn(LAST); }
  } catch (Throwable t) { LAST = "P11: removal at " + this.key + " failed (" + t + ") - remove it by hand"; @PKG@.AbLog.warn(LAST); }
}""")
else:
    M(unp, "public void run() { }")

# ---- AbCmds: engine glue + every probe (world thread: AbstractPlayerCommand.execute, the tick, the damage / event systems)
cmds = mk("AbCmds")
for f in ("public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.Map MINE = java.util.Collections.synchronizedMap(new java.util.IdentityHashMap());",
          "public static final java.util.Map EARLY = java.util.Collections.synchronizedMap(new java.util.IdentityHashMap());",
          "public static final java.util.Map LATE = java.util.Collections.synchronizedMap(new java.util.IdentityHashMap());",
          "public static volatile boolean CHAIN_ON = false;",
          "public static volatile String ORDER_EARLY = \"not registered\";",
          "public static volatile String ORDER_LATE = \"not registered\";",
          "public static volatile String CHAIN_WHY = \"not registered\";",
          "public static final boolean P11_BUILT = %s;" % ("true" if P11_BUILT else "false"),
          "public static final String[] DESK = %s;" % jarr(DESK),
          "public static final String ABSLOTS = %s;" % jl(ABSLOTS),
          "public static final String RUNEBAG = %s;" % jl(RUNEBAG),
          "public static final String STUN_FX = %s;" % jl(STUN_FX),
          "public static final String NPC_KW = %s;" % jl(NPC_KW)):
    F(cmds, f)
for k, v in sorted(N.items()):
    F(cmds, "public static final double %s = %s;" % (k, jd(v)))
M(cmds, r"""
public static void tell(@PR@ pr, String s) { @PKG@.AbLog.tell(pr, s); }""")
M(cmds, r"""
public static String f1(double v) { return @PKG@.AbLogic.f1(v); }""")
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
  } catch (Throwable t) { @PKG@.AbLog.warn("area query failed: " + t); return new java.util.ArrayList(); }
}""")
M(cmds, r"""
public static @REF@ nearestEnemy(@CAC@ acc, @REF@ self, @V3D@ p, double rad) {
  if (p == null) return null;
  java.util.List l = near(acc, p.x, p.y + 1.0, p.z, rad);
  @REF@ best = null;
  double bd = 1.0E18;
  for (int i = 0; i < l.size(); i++) {
    @REF@ t = (@REF@) l.get(i);
    if (!enemy(acc, t, self)) continue;
    @V3D@ q = pos(acc, t);
    if (q == null) continue;
    double d = (q.x - p.x) * (q.x - p.x) + (q.y - p.y) * (q.y - p.y) + (q.z - p.z) * (q.z - p.z);
    if (d < bd) { bd = d; best = t; }
  }
  return best;
}""")
# {value, max} of one stat (null = unreadable)
M(cmds, r"""
public static double[] stat(@CAC@ acc, @REF@ r, int idx) {
  try {
    if (idx < 0 || r == null) return null;
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m == null) return null;
    @ESV@ v = m.get(idx);
    if (v == null) return null;
    return new double[] { (double) v.get(), (double) v.getMax() };
  } catch (Throwable t) { return null; }
}""")
# one probe hit through the whole damage pipeline (SkyyArmory ArmoryTrav.hit's shape: an EntitySource, cause PROJECTILE), MINE-marked
M(cmds, r"""
public static boolean hit(@CB@ buf, @REF@ target, @REF@ src, double amount) {
  try {
    if (!(amount > 0.0) || target == null || !target.isValid() || src == null || !src.isValid()) return false;
    // REVIEW FIX R1: a probe hit never kills - none at <= 2 / unreadable Health, else capped at Health - 1 (onLate clamps it again)
    double[] hv = stat(buf, target, @DST@.getHealth());
    if (hv == null || !(hv[0] > 2.0)) return false;
    if (amount > hv[0] - 1.0) amount = hv[0] - 1.0;
    @DCS@ cause = @DCS@.PROJECTILE;
    if (cause == null) return false;
    @DMG@ d = new @DMG@(new @DENT@(src), cause, (float) amount);
    if (MINE.size() > 4096) MINE.clear();
    MINE.put(d, Boolean.TRUE);
    @DSYS@.executeDamage(target, buf, d);
    return true;
  } catch (Throwable t) { @PKG@.AbLog.warn("a probe hit failed: " + t); return false; }
}""")
M(cmds, r"""
public static boolean spend(@CAC@ acc, @REF@ r, int idx, double cost) {
  try {
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m == null || idx < 0 || m.get(idx) == null) return false;
    m.subtractStatValue(idx, (float) cost);
    return true;
  } catch (Throwable t) { return false; }
}""")
# a vanilla status effect for secs (SkyyArmory ArmoryTree.stun's call: addEffect with a duration + OVERWRITE)
M(cmds, r"""
public static boolean addFx(@CAC@ acc, @REF@ t, String id, double secs) {
  try {
    if (t == null || !t.isValid() || id == null) return false;
    @ECC@ c = (@ECC@) acc.getComponent(t, @ECC@.getComponentType());
    Object fx = @EFX@.getAssetMap().getAsset(id);
    if (c == null || !(fx instanceof @EFX@)) return false;
    return c.addEffect(t, (@EFX@) fx, (float) secs, @OVB@.OVERWRITE, acc);
  } catch (Throwable x) { @PKG@.AbLog.warn("effect " + id + " failed: " + x); return false; }
}""")
M(cmds, r"""
public static Object compOf(@CAC@ acc, @REF@ r, String clsName) {
  try {
    Object ct = @PKG@.AbRefl.static0(clsName, "getComponentType");
    if (!(ct instanceof @CTYPE@) || r == null) return null;
    return acc.getComponent(r, (@CTYPE@) ct);
  } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static @IC@ containerOf(Object comp) {
  Object o = @PKG@.AbRefl.call0(comp, "getInventory");
  return o instanceof @IC@ ? (@IC@) o : null;
}""")
M(cmds, r"""
public static String slotText(@IC@ c, int i) {
  try {
    @IS@ s = c.getItemStack((short) i);
    return s == null || s.isEmpty() ? "-" : s.getItemId() + (s.getQuantity() > 1 ? " x" + s.getQuantity() : "");
  } catch (Throwable t) { return "?"; }
}""")
M(cmds, r"""
public static String slots(@IC@ c, boolean onlyFilled, int max) {
  if (c == null) return "none";
  StringBuilder b = new StringBuilder();
  int cap = 0;
  try { cap = (int) c.getCapacity(); } catch (Throwable t) { return "unreadable"; }
  int n = 0;
  for (int i = 0; i < cap && n < max; i++) {
    String one = slotText(c, i);
    if (onlyFilled && "-".equals(one)) continue;
    if (b.length() > 0) b.append(", ");
    b.append(i).append(" ").append(one);
    n++;
  }
  return "(" + cap + " slots) " + (b.length() == 0 ? "all empty" : b.toString());
}""")
M(cmds, r"""
public static String txText(Object tx) {
  if (tx == null) return "no transaction";
  Object ok = @PKG@.AbRefl.call0(tx, "succeeded");
  return tx.getClass().getSimpleName() + (ok == null ? "" : " succeeded=" + ok);
}""")
M(cmds, r"""
public static Object imgr(@CAC@ acc, @REF@ r) {
  try { return acc.getComponent(r, @IMOD@.get().getInteractionManagerComponent()); } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static @PKG@.AbState state(@PR@ pr, @REF@ r, @ST@ st) {
  java.util.UUID u = pr.getUuid();
  @PKG@.AbState s = (@PKG@.AbState) STATES.get(u);
  if (s == null || s.st != st) {
    s = new @PKG@.AbState(u, r, st);
    STATES.put(u, s);
  }
  s.ref = r;
  return s;
}""")
# the running probe of that player, or null (mode < 0 = any mode). EVERY hook goes through this: no window, no action.
M(cmds, r"""
public static @PKG@.AbState active(@PR@ pr, int mode, long now) {
  if (pr == null) return null;
  @PKG@.AbState s = (@PKG@.AbState) STATES.get(pr.getUuid());
  if (s == null || s.mode == 0 || now >= s.modeUntil) return null;
  if (mode >= 0 && s.mode != mode) return null;
  return s;
}""")
M(cmds, r"""
public static @REF@ attacker(@DMG@ d) {
  try {
    Object src = d.getSource();
    if (src instanceof @DENT@) return ((@DENT@) src).getRef();
  } catch (Throwable t) { }
  return null;
}""")
M(cmds, r"""
public static String causeOf(@DMG@ d) {
  try { @DCS@ c = d.getCause(); return c == null ? "?" : String.valueOf(c.getId()); } catch (Throwable t) { return "?"; }
}""")
# ---- THE RESET RULE: every probe field back to its resting value (generated from the AbState field list - nothing can be forgotten)
M(cmds, "public static void clear(@PKG@.AbState s) {\n  if (s == null) return;\n" + "\n".join(_reset(t, n) for t, n in STATE_FIELDS) + "\n}")
# ---- arming a timed probe (pure: no engine objects - the harness runs it): clear() FIRST, then the probe's own fields. null = armed.
M(cmds, r"""
public static String plan(@PKG@.AbState s, String[] w, long now) {
  clear(s);
  String t = @PKG@.AbLogic.low(@PKG@.AbLogic.word(w, 0));
  String a1 = @PKG@.AbLogic.word(w, 1);
  String a2 = @PKG@.AbLogic.word(w, 2);
  String l1 = @PKG@.AbLogic.low(a1);
  s.armedAt = now;
  int secs = 0;
  if ("p1".equals(t)) { s.mode = 1; secs = 60; s.cancel = "cancel".equals(l1); }
  else if ("p2".equals(t)) { s.mode = 2; secs = @PKG@.AbLogic.number(a1, 20, 5, 120); }
  else if ("p4".equals(t) && "watch".equals(l1)) { s.mode = 4; secs = 60; }
  else if ("p5".equals(t)) { s.mode = 5; s.save = "save".equals(l1); secs = s.save ? 60 : @PKG@.AbLogic.number(a1, 60, 10, 300); }
  else if ("p6".equals(t)) { s.mode = 6; s.fxId = (a1 == null || "none".equals(l1)) ? "" : a1; secs = @PKG@.AbLogic.number(a2, 20, 5, 120); }
  else if ("p7".equals(t)) { s.mode = 7; secs = @PKG@.AbLogic.number(a1, 10, 3, 60); }
  else if ("p8".equals(t)) {
    s.mode = 8;
    if ("stun".equals(l1)) { s.p8Stun = true; secs = 5; }
    else { int hps = @PKG@.AbLogic.number(a1, 3, 1, 10); s.p8Gap = 1000L / (long) hps; secs = @PKG@.AbLogic.number(a2, 6, 2, 20); }
  }
  else if ("p9".equals(t)) {
    if (a1 == null) { clear(s); return "Usage: /aprobe p9 <particleId> [radius] (/aprobe info lists candidate ids)"; }
    s.mode = 9; secs = 12; s.fxName = a1; s.radius = @PKG@.AbLogic.dnum(a2, 4.0, 1.0, 12.0);
  }
  else if ("p10".equals(t)) { s.mode = 10; secs = @PKG@.AbLogic.number(a1, 12, 3, 60); s.radius = P10_R; }
  else if ("p12".equals(t) && "stun".equals(l1)) { s.mode = 12; secs = 5; s.p8Stun = true; }
  else if ("p13".equals(t)) { s.mode = 13; s.zones = @PKG@.AbLogic.number(a1, 48, 1, 256); secs = @PKG@.AbLogic.number(a2, 10, 3, 60); }
  else { clear(s); return "unknown probe - /aprobe lists them"; }
  s.modeUntil = now + (long) secs * 1000L;
  return null;
}""")
# ---- the summary of the running probe (pure: numbers only, so it is safe from any world / after a world change)
M(cmds, r"""
public static void summary(@PKG@.AbState s, @PR@ pr, String why) {
  if (s == null || s.mode == 0) return;
  long ms = System.currentTimeMillis() - s.armedAt;
  if (ms < 1L) ms = 1L;
  String h = "P" + s.mode + " " + (why == null ? "done" : why) + ": ";
  int m = s.mode;
  if (m == 1) tell(pr, h + s.chains + " chains (" + s.chainAb + " Ability2/3, " + s.chainPrim + " Primary, " + s.chainOther + " other)" + (s.cancel ? ", " + s.cancelled + " cancelled, " + s.cancelFail + " cancel failures" : "") + ". PASS = your rune keys printed Ability2 / Ability3 lines" + (s.cancel ? " and a cancelled cast showed no animation, no cooldown fill, no Mana spent." : "."));
  else if (m == 2) tell(pr, h + @PKG@.AbLogic.swingVerdict(s.chainPrim, s.hits) + (CHAIN_ON ? "" : " - this server has no InteractionChainStartEvent (Hytale 0.6.8): needs 0.7."));
  else if (m == 4) tell(pr, h + s.invSlots + " InventoryChangeEvents on AbilitySlots, " + s.invBag + " on the RuneBag, " + s.invOther + " on other containers. PASS = your drag in the rune bench printed an AbilitySlots line.");
  else if (m == 5) tell(pr, h + s.p5Seen + " hits followed; " + s.p5Changed + " changed AFTER our late filter (= another mod's filter runs after it); " + (s.p5Late - s.p5Landed) + " of " + s.p5Late + " passed our late filter but never landed (" + (s.p5Late > s.p5Landed ? "FAIL: cancelled after it" : "PASS") + ")" + ", lethal saves " + s.saves + ". Filters: early " + ORDER_EARLY + ", late " + ORDER_LATE + ".");
  else if (m == 6) tell(pr, h + "swing gap " + f1(@PKG@.AbLogic.avg(s.swGapSum, s.swGapN)) + " ms (" + s.swGapN + " gaps, 0.7 only), hit gap " + f1(@PKG@.AbLogic.avg(s.hitGapSum, s.hitGapN)) + " ms (" + s.hitGapN + " gaps)" + (s.fxId.length() > 0 ? "; effect " + s.fxId + " put " + s.fxPuts + " times, taken off by another system " + s.fxGone + " times" : "; no effect (baseline)") + ".");
  else if (m == 7) tell(pr, h + s.p7Steps + " steps: spent " + f1(s.p7SpentM) + " Mana + " + f1(s.p7SpentS) + " Stamina, regen seen meanwhile +" + f1(s.p7RegenM) + " Mana / +" + f1(s.p7RegenS) + " Stamina, " + s.p7Fights + " inexact subtracts, " + s.p7Short + " steps too poor to pay. " + (s.p7Fights == 0 ? "PASS (exact)" : "FAIL (a write fight)") + (s.p7RegenM > 0.0 ? ", regen kept running." : ", NO Mana regen seen while spending."));
  else if (m == 8) tell(pr, h + (s.p8Stun ? "Stun " + f1(P8_STUN) + " s" : s.p8Sent + " probe hits (no knockback)") + " - the mob hit you " + s.mobHits + " times in " + (ms / 1000L) + " s. 0 = those hits keep it from attacking; > 0 = it attacks through them.");
  else if (m == 9) tell(pr, h + s.p9Calls + " particle calls (" + s.p9Fail + " failed) for '" + s.fxName + "', radius " + f1(s.radius) + ". Was the dome visible but easy to see through (docs/answered/classes.md line 114)?");
  else if (m == 10) tell(pr, h + s.p10Scans + " scans, " + s.p10Seen + " projectiles seen, " + s.p10Removed + " removed, " + s.p10Own + " of yours kept; scan avg " + (s.p10Scans == 0 ? 0L : s.p10Ns / (long) s.p10Scans / 1000L) + " us, max " + s.p10Max / 1000L + " us. Did the arrows vanish cleanly (no ghost arrow, no hit)?");
  else if (m == 12) tell(pr, h + "Stun " + f1(P12_STUN) + " s on the mob, then it hit you " + s.mobHits + " times. Did it turn back to you right after the stun?");
  else if (m == 13) {
    double tps = @PKG@.AbLogic.perSec(s.p13Ticks, ms);
    double us = s.p13Ticks == 0L ? 0.0 : (double) s.p13Ns / (double) s.p13Ticks / 1000.0;
    tell(pr, h + s.zones + " zones x " + f1(P13_HZ) + " Hz: " + s.p13Scans + " scans (" + f1(@PKG@.AbLogic.perSec(s.p13Scans, ms)) + " per s), " + f1(s.p13Scans == 0L ? 0.0 : (double) s.p13Ents / (double) s.p13Scans) + " entities per scan, max " + s.p13Max / 1000L + " us in one tick; world ticks per second " + f1(tps) + " (spec assumes 30). " + @PKG@.AbLogic.budget(us, P13_LIMIT_US));
  }
}""")
M(cmds, r"""
public static void finish(@PKG@.AbState s, @PR@ pr, String why) {
  summary(s, pr, why);
  if (s != null && s.mode == 5) { EARLY.clear(); LATE.clear(); }
  clear(s);
}""")
M(cmds, r"""
public static void help(@PR@ pr) {
  tell(pr, "Ability engine probes (op only, research/cloud/Ability-Probe-Plan.md). One timed probe at a time; send the server log afterwards.");
  tell(pr, "0.7: /aprobe p1 [cancel] | p2 [secs] | p3 [dump|read <rootId>|<method> <rootId> <secs>] | p4 read|watch|put <slot> <id>|take <slot>|bad <slot> | p14");
  tell(pr, "both: /aprobe p5 [secs|save] | p6 [effectId|none] [secs] | p7 [secs] | p8 [hits/s] [secs] | p8 stun | p9 <particleId> [radius] | p10 [secs]");
  tell(pr, "both: /aprobe p11 <blockId> [secs] | p12 | p12 stun | p13 [zones] [secs] | p15 | info | stats | stop");
}""")
M(cmds, r"""
public static void info(@PR@ pr) {
  tell(pr, "Info: InteractionChainStartEvent " + (CHAIN_ON ? "LISTENING (Hytale 0.7)" : "not available (" + CHAIN_WHY + ")") + "; AbilitySlots class " + (@PKG@.AbRefl.cls(ABSLOTS) != null ? "present" : "missing") + "; damage filters: early " + ORDER_EARLY + ", late " + ORDER_LATE + "; P11 " + (P11_BUILT ? "built" : "NOT built") + ".");
  for (int i = 0; i < DESK.length; i++) tell(pr, DESK[i]);
}""")
M(cmds, r"""
public static void stats(@PR@ pr) {
  @PKG@.AbState s = (@PKG@.AbState) STATES.get(pr.getUuid());
  if (s == null) tell(pr, "No probe state.");
  else tell(pr, "Stats: running P" + s.mode + ", " + s.ticks + " ticks, avg " + (s.ticks == 0L ? 0L : s.ns / s.ticks / 1000L) + " us, max " + s.nsMax / 1000L + " us per tick.");
  tell(pr, @PKG@.AbUnplace.LAST + " (" + @PKG@.AbUnplace.PLACED.size() + " probe blocks still placed)");
}""")

# ---- P3: the CooldownHandler (0.7; reflection)
M(cmds, r"""
public static void p3(@PR@ pr, @ST@ st, @REF@ ref, String[] w) {
  String a1 = @PKG@.AbLogic.word(w, 1);
  String l1 = @PKG@.AbLogic.low(a1);
  StringBuilder where = new StringBuilder();
  Object im = imgr(st, ref);
  Object h = @PKG@.AbRefl.findBy(im, "Cooldown", where);
  if (h == null) {
    Object pl = null;
    try { pl = st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { pl = null; }
    h = @PKG@.AbRefl.findBy(pl, "Cooldown", where);
  }
  if (h == null) {
    java.util.ArrayList out = new java.util.ArrayList();
    @PKG@.AbRefl.dump(im, "cooldown", out, "P3 InteractionManager: ");
    for (int i = 0; i < out.size(); i++) @PKG@.AbLog.info(String.valueOf(out.get(i)));
    tell(pr, "P3: no CooldownHandler reachable from the InteractionManager or the Player component (" + (im == null ? "no InteractionManager" : im.getClass().getName()) + "). FAIL for the plugin path - HUD H1 is out, use the SkyyHud Abilities widget (spec 12 H2).");
    return;
  }
  if (a1 == null || "dump".equals(l1)) {
    java.util.ArrayList out = new java.util.ArrayList();
    int n = @PKG@.AbRefl.dump(h, "", out, "P3: ");
    for (int i = 0; i < out.size(); i++) @PKG@.AbLog.info(String.valueOf(out.get(i)));
    tell(pr, "P3: CooldownHandler = " + where + " (" + h.getClass().getName() + "), " + n + " public methods - all in the server log. Next: cast a vanilla rune, then /aprobe p3 read <its Cast root id>.");
    for (int i = 0; i < out.size() && i < 8; i++) tell(pr, String.valueOf(out.get(i)));
    return;
  }
  String id = @PKG@.AbLogic.word(w, 2);
  if (id == null) { tell(pr, "Usage: /aprobe p3 read <rootId>  |  /aprobe p3 <method> <rootId> <secs>"); return; }
  if ("read".equals(l1)) {
    tell(pr, "P3 isOnCooldown: " + @PKG@.AbRefl.invoke(h, "isOnCooldown", id, 0.0));
    tell(pr, "P3 getCooldown: " + @PKG@.AbRefl.invoke(h, "getCooldown", id, 0.0));
    return;
  }
  double secs = @PKG@.AbLogic.dnum(@PKG@.AbLogic.word(w, 3), 8.0, 0.0, 120.0);
  tell(pr, "P3 call " + a1 + "(" + id + ", " + f1(secs) + " s): " + @PKG@.AbRefl.invoke(h, a1, id, secs) + " - does the rune's HUD slot show a cooldown fill now?");
}""")
# ---- P4: the AbilitySlots section -11 (0.7; reflection for the component, ItemContainer calls as SkyyClasses / SkyyProfiles)
M(cmds, r"""
public static void p4(@PR@ pr, @ST@ st, @REF@ ref, String[] w) {
  Object comp = compOf(st, ref, ABSLOTS);
  @IC@ c = containerOf(comp);
  if (c == null) { tell(pr, "P4 needs Hytale 0.7: no AbilitySlots " + (comp == null ? "component" : "container (" + comp.getClass().getName() + ")") + " on you."); return; }
  String l1 = @PKG@.AbLogic.low(@PKG@.AbLogic.word(w, 1));
  if (l1 == null || "read".equals(l1)) { tell(pr, "P4 AbilitySlots " + slots(c, false, 6) + ". Slot 0 = line 1 (Use Ability 2), 3 = line 2 (Use Ability 3)."); return; }
  int slot = @PKG@.AbLogic.number(@PKG@.AbLogic.word(w, 2), -1, -1, 99);
  if (!@PKG@.AbLogic.slotOk(slot)) { tell(pr, "Usage: /aprobe p4 put <slot 0-5> <itemId> | take <slot> | bad <slot>"); return; }
  try {
    if ("put".equals(l1)) {
      String id = @PKG@.AbLogic.word(w, 3);
      if (id == null) { tell(pr, "Usage: /aprobe p4 put <slot 0-5> <itemId>"); return; }
      if (!"-".equals(slotText(c, slot))) { tell(pr, "P4 put: slot " + slot + " is not empty (" + slotText(c, slot) + ") - /aprobe p4 take " + slot + " first."); return; }
      Object tx = c.addItemStackToSlot((short) slot, new @IS@(id, 1));
      tell(pr, "P4 put " + id + " -> slot " + slot + ": " + txText(tx) + "; slot now " + slotText(c, slot) + ". Then: die, change world, relog - and /aprobe p4 read after each.");
      return;
    }
    if ("take".equals(l1)) {
      String before = slotText(c, slot);
      Object tx = c.removeItemStackFromSlot((short) slot);
      tell(pr, "P4 take slot " + slot + " (" + before + "): " + txText(tx) + "; slot now " + slotText(c, slot) + ".");
      return;
    }
    if ("bad".equals(l1)) {
      @IS@ hand = @INVC@.getItemInHand(st, ref);
      if (hand == null || hand.isEmpty()) { tell(pr, "P4 bad: hold any NON-rune item (a sword) first."); return; }
      if (!"-".equals(slotText(c, slot))) { tell(pr, "P4 bad: slot " + slot + " is not empty - /aprobe p4 take " + slot + " first."); return; }
      String id = hand.getItemId();
      Object tx = c.addItemStackToSlot((short) slot, new @IS@(id, 1));
      if (!"-".equals(slotText(c, slot))) {
        c.removeItemStackFromSlot((short) slot);
        String again = slotText(c, slot);
        tell(pr, "P4 bad: FAIL - a non-rune (" + id + ") went into slot " + slot + " from code (the slot filter does not guard code writes; the engine's mirror must check items itself). Removed again: " + ("-".equals(again) ? "yes" : "NO - take it out by hand") + ".");
      } else tell(pr, "P4 bad: PASS - slot " + slot + " refused " + id + " (" + txText(tx) + ").");
      return;
    }
  } catch (Throwable t) { tell(pr, "P4 " + l1 + " failed: " + t); return; }
  tell(pr, "Usage: /aprobe p4 read | watch | put <slot> <itemId> | take <slot> | bad <slot>");
}""")
# ---- P14: the rune sections across SkyyProfiles profiles (0.7)
M(cmds, r"""
public static void p14(@PR@ pr, @ST@ st, @REF@ ref) {
  @IC@ a = containerOf(compOf(st, ref, ABSLOTS));
  @IC@ b = containerOf(compOf(st, ref, RUNEBAG));
  if (a == null && b == null) { tell(pr, "P14 needs Hytale 0.7: no AbilitySlots / RuneBag on you."); return; }
  Object key = bridge().get("profile:key:" + pr.getUuid().toString());
  tell(pr, "P14 profile " + (key == null ? "(no SkyyProfiles key)" : String.valueOf(key)) + ": ability slots -11 " + slots(a, true, 6) + "; rune bag -12 " + slots(b, true, 20) + ".");
  tell(pr, "Now /profiles switch to another profile and run /aprobe p14 again: the SAME runes there = the leak (SkyyProfiles 0.1.6 saves 6 sections only).");
}""")
# ---- P15: Mana numbers (both versions)
M(cmds, r"""
public static void p15(@PR@ pr, @ST@ st, @REF@ ref) {
  int mi = @DST@.getMana();
  double[] mv = stat(st, ref, mi);
  float tmax = 0.0f;
  try {
    @ESTT@ t = (@ESTT@) @ESTT@.getAssetMap().getAsset(mi);
    if (t != null) tmax = t.getMax();
  } catch (Throwable x) { tmax = -1.0f; }
  if (mv == null) { tell(pr, "P15: your Mana is unreadable."); return; }
  tell(pr, "P15: your Mana " + f1(mv[0]) + " / " + f1(mv[1]) + "; the Mana stat type's own max " + f1((double) tmax) + " (0.6.8: 0, 0.7: 100). Your max minus it = " + f1(mv[1] - (double) tmax) + ".");
  tell(pr, "PASS = your max is the SkyySkills number /skills mana shows (base 10 / 20 + class levels), i.e. the vanilla " + f1((double) tmax) + " is NOT added on top" + (tmax > 0.0f && mv[1] >= (double) tmax ? " - CHECK: your max is at least the vanilla max." : "."));
}""")
# ---- P11: a temporary banner block (both versions; left out when the block API differs)
if P11_BUILT:
    M(cmds, r"""
public static void p11(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ world, String[] w) {
  String id = @PKG@.AbLogic.word(w, 1);
  if (id == null) { tell(pr, "Usage: /aprobe p11 <blockId> [secs] (/aprobe info lists 'banner' ids)"); return; }
  int secs = @PKG@.AbLogic.number(@PKG@.AbLogic.word(w, 2), 10, 3, 60);
  @V3D@ p = pos(st, ref);
  double[] lk = look(st, ref);
  if (p == null || lk == null || world == null) { tell(pr, "P11: no position / look."); return; }
  int bx = @PKG@.AbLogic.floorI(p.x + lk[6] * 2.0);
  int by = @PKG@.AbLogic.floorI(p.y);
  int bz = @PKG@.AbLogic.floorI(p.z + lk[7] * 2.0);
  try {
    @WCH@ c = world.getChunkIfLoaded(@CHU@.indexChunkFromBlock(bx, bz));
    if (c == null) { tell(pr, "P11: that chunk is not loaded."); return; }
    int before = c.getBlock(bx, by, bz);
    if (before != 0) { tell(pr, "P11: the spot 2 blocks in front of your feet is not empty (block " + before + ") - face open air on flat ground."); return; }
    boolean ok = c.setBlock(bx, by, bz, id);
    int after = c.getBlock(bx, by, bz);
    if (!ok || after == 0) { tell(pr, "P11: setBlock(" + bx + " " + by + " " + bz + ", " + id + ") = " + ok + ", read back " + after + " - not placed (unknown block id, or the chunk wants local coordinates)."); return; }
    @PKG@.AbUnplace u = new @PKG@.AbUnplace(world, bx, by, bz, after);
    @PKG@.AbUnplace.PLACED.put(u.key, id);
    @HSV@.SCHEDULED_EXECUTOR.schedule(u, (long) secs, java.util.concurrent.TimeUnit.SECONDS);
    tell(pr, "P11: placed " + id + " at " + bx + " " + by + " " + bz + " (block " + after + "); it is removed in " + secs + " s (/aprobe stats shows how it went). Did it appear 2 blocks in front of you, and vanish cleanly?");
  } catch (Throwable t) { tell(pr, "P11 failed: " + t); }
}""")
else:
    M(cmds, r"""
public static void p11(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ world, String[] w) {
  tell(pr, "P11 is not in this jar: the block API (ChunkUtil.indexChunkFromBlock / WorldChunk.setBlock) differs on this server - see the build log.");
}""")
# ---- P12: the nearest NPC's targeting API (dump to the log)
M(cmds, r"""
public static void p12(@PR@ pr, @ST@ st, @REF@ ref) {
  @REF@ t = nearestEnemy(st, ref, pos(st, ref), P12_RANGE);
  if (t == null) { tell(pr, "P12: no enemy NPC within " + f1(P12_RANGE) + " blocks."); return; }
  Object npc = null;
  try { npc = st.getComponent(t, @NPC@.getComponentType()); } catch (Throwable x) { npc = null; }
  java.util.ArrayList out = new java.util.ArrayList();
  int n = @PKG@.AbRefl.dump(npc, NPC_KW, out, "P12 NPC: ");
  Object role = @PKG@.AbRefl.call0(npc, "getRole");
  n = n + @PKG@.AbRefl.dump(role, NPC_KW, out, "P12 Role: ");
  if (role != null) {
    try {
      java.lang.reflect.Method[] ms = role.getClass().getMethods();
      for (int i = 0; i < ms.length && out.size() < 200; i++) {
        if (ms[i].getParameterTypes().length != 0) continue;
        String rt = ms[i].getReturnType().getName();
        if (rt.indexOf("Support") < 0 && rt.indexOf("Target") < 0 && rt.indexOf("Combat") < 0 && rt.indexOf("Marked") < 0 && rt.indexOf("Sensor") < 0) continue;
        Object v = ms[i].invoke(role, new Object[0]);
        n = n + @PKG@.AbRefl.dump(v, NPC_KW, out, "P12 Role." + ms[i].getName() + "(): ");
      }
    } catch (Throwable x) { out.add("P12 role walk failed: " + x); }
  }
  for (int i = 0; i < out.size(); i++) @PKG@.AbLog.info(String.valueOf(out.get(i)));
  tell(pr, "P12: " + n + " candidate targeting methods written to the server log (NPC " + (npc == null ? "none" : npc.getClass().getName()) + ", role " + (role == null ? "none" : role.getClass().getName()) + "). Next: /aprobe p12 stun.");
}""")
# ---- engine setup of an armed probe (after plan); a text = refused (the caller clears the state)
M(cmds, r"""
public static String start(@PKG@.AbState s, @PR@ pr, @ST@ st, @REF@ ref, long now) {
  int m = s.mode;
  if ((m == 1 || m == 2) && !CHAIN_ON) return "P" + m + " needs Hytale 0.7 (no InteractionChainStartEvent on this server: " + CHAIN_WHY + ").";
  if (m == 4 && containerOf(compOf(st, ref, ABSLOTS)) == null) return "P4 watch needs Hytale 0.7 (no AbilitySlots on you).";
  if (m == 6 && s.fxId.length() > 0) {
    int i = -1;
    try { i = @EFX@.getAssetMap().getIndex(s.fxId); } catch (Throwable x) { i = -1; }
    if (i < 0) return "P6: no entity effect '" + s.fxId + "' is loaded (try SkyyGear_Speed_Fast with SkyyGear on).";
    s.fxIdx = i;
  }
  if (m == 8 || m == 12) {
    @REF@ t = nearestEnemy(st, ref, pos(st, ref), m == 8 ? P8_RANGE : P12_RANGE);
    if (t == null) return "P" + m + ": no enemy NPC near you.";
    s.target = t;
    if (s.p8Stun && !addFx(st, t, STUN_FX, m == 8 ? P8_STUN : P12_STUN)) return "P" + m + ": the vanilla Stun effect could not be put on it.";
  }
  if (m == 9 || m == 10) {
    @V3D@ p = pos(st, ref);
    if (p == null) return "P" + m + ": no position.";
    s.ax = p.x; s.ay = p.y; s.az = p.z;
  }
  return null;
}""")
M(cmds, r"""
public static String armedText(@PKG@.AbState s) {
  long secs = (s.modeUntil - s.armedAt) / 1000L;
  int m = s.mode;
  String h = "P" + m + " armed for " + secs + " s: ";
  if (m == 1) return h + "press Use Ability 2 / 3 (rune keys) and swing" + (s.cancel ? " - Ability2/3 chains are CANCELLED, watch for a stuck animation or a cooldown fill" : "") + ".";
  if (m == 2) return h + "swing 5 times at the AIR, then 5 times at a mob.";
  if (m == 4) return h + "open the rune bench and drag a rune in and out.";
  if (m == 5) return h + (s.save ? "the next hit that would KILL you is cancelled and your Health set to " + f1(SAVE_PCT) + "% - take a big hit." : "hit a mob and let it hit you; every hit prints before armour / after armour / landed.");
  if (m == 6) return h + "swing nonstop at a mob" + (s.fxId.length() > 0 ? " - effect " + s.fxId + " is kept on you." : " (baseline, no effect).");
  if (m == 7) return h + "stand still; 0.5 Mana + 0.25 Stamina are taken every 0.25 s.";
  if (m == 8) return h + (s.p8Stun ? "the nearest mob is Stunned " + f1(P8_STUN) + " s - does it hit you?" : "probe hits every " + s.p8Gap + " ms on the nearest mob - let it try to hit you.");
  if (m == 9) return h + "a dome of '" + s.fxName + "' (radius " + f1(s.radius) + ") where you stand - step in and out, look through it.";
  if (m == 10) return h + "a " + f1(s.radius) + "-block bubble where you stand - let a skeleton shoot at you from outside.";
  if (m == 12) return h + "the nearest mob is Stunned " + f1(P12_STUN) + " s; then count how fast it comes back for you.";
  if (m == 13) return h + s.zones + " zones scanning at " + f1(P13_HZ) + " Hz each - stand among some mobs.";
  return h;
}""")

# ---- the tick parts (world thread)
M(cmds, r"""
public static void p6Tick(@PKG@.AbState s, @CB@ cb, @REF@ r, long now) {
  if (s.fxIdx < 0 || now < s.fxNext) return;
  s.fxNext = now + 500L;
  @ECC@ c = (@ECC@) cb.getComponent(r, @ECC@.getComponentType());
  if (c == null) return;
  if (s.fxPut) {
    @I2O@ m = c.getActiveEffects();
    if (m == null || m.get(s.fxIdx) == null) s.fxGone = s.fxGone + 1;      // a 1 s effect re-put every 0.5 s cannot run out: someone took it off
  }
  if (addFx(cb, r, s.fxId, 1.0)) { s.fxPut = true; s.fxPuts = s.fxPuts + 1; }
}""")
M(cmds, r"""
public static void p7Tick(@PKG@.AbState s, @CB@ cb, @REF@ r, long now) {
  if (now < s.p7Next) return;
  s.p7Next = now + (long) P7_STEP;
  s.p7Steps = s.p7Steps + 1;
  int mi = @DST@.getMana();
  int si = @DST@.getStamina();
  double[] mv = stat(cb, r, mi);
  double[] sv = stat(cb, r, si);
  if (mv != null && s.p7LastM >= 0.0 && mv[0] > s.p7LastM) s.p7RegenM = s.p7RegenM + (mv[0] - s.p7LastM);
  if (sv != null && s.p7LastS >= 0.0 && sv[0] > s.p7LastS) s.p7RegenS = s.p7RegenS + (sv[0] - s.p7LastS);
  // REVIEW FIX R5: both costs or neither (a step either balance cannot pay = short, nothing spent)
  if (mv == null || sv == null || mv[0] < P7_MANA || sv[0] < P7_STAM) {
    s.p7Short = s.p7Short + 1;
    s.p7LastM = mv == null ? -1.0 : mv[0];
    s.p7LastS = sv == null ? -1.0 : sv[0];
    return;
  }
  if (spend(cb, r, mi, P7_MANA)) {
    double[] a = stat(cb, r, mi);
    s.p7SpentM = s.p7SpentM + P7_MANA;
    if (a == null || @PKG@.AbLogic.fight(mv[0], P7_MANA, a[0], 0.01)) s.p7Fights = s.p7Fights + 1;
    s.p7LastM = a == null ? -1.0 : a[0];
  } else s.p7LastM = mv[0];
  if (spend(cb, r, si, P7_STAM)) {
    double[] b = stat(cb, r, si);
    s.p7SpentS = s.p7SpentS + P7_STAM;
    if (b == null || @PKG@.AbLogic.fight(sv[0], P7_STAM, b[0], 0.01)) s.p7Fights = s.p7Fights + 1;
    s.p7LastS = b == null ? -1.0 : b[0];
  } else s.p7LastS = sv[0];
}""")
# REVIEW FIX R6: hits our late filter passed that never landed (filter + Inspect run in one damage dispatch, so by the next tick a missing
# one was cancelled after our filter) - told as they happen; the summary gives the FAIL
M(cmds, r"""
public static void p5Tick(@PKG@.AbState s, @PR@ pr) {
  int lost = s.p5Late - s.p5Landed;
  if (lost <= s.p5Lost) return;
  tell(pr, "P5: " + (lost - s.p5Lost) + " hit(s) passed our late filter but never landed - CANCELLED after it (FAIL: a later filter cancels).");
  s.p5Lost = lost;
}""")
M(cmds, r"""
public static void p8Tick(@PKG@.AbState s, @PR@ pr, @CB@ cb, @REF@ r, long now) {
  @REF@ t = (@REF@) s.target;
  boolean gone = t == null || !t.isValid();
  try { if (!gone && cb.getComponent(t, @DTH@.getComponentType()) != null) gone = true; } catch (Throwable x) { gone = true; }
  if (gone) { tell(pr, "P" + s.mode + ": the mob is gone or dead - ending now." + (s.mode == 8 && !s.p8Stun ? " If the probe hits killed it, another mod's damage filter runs after ours and raised them (REVIEW FIX R1)." : "")); s.modeUntil = now; return; }
  if (s.p8Stun || s.mode != 8 || now < s.p8Next) return;
  s.p8Next = now + s.p8Gap;
  double[] hv = stat(cb, t, @DST@.getHealth());
  if (hv == null || !(hv[0] > 2.0)) { tell(pr, "P8: the mob's Health is " + (hv == null ? "unreadable" : f1(hv[0])) + " - probe hits never kill, ending now."); s.modeUntil = now; return; }
  if (hit(cb, t, r, P8_AMT)) s.p8Sent = s.p8Sent + 1;
}""")
M(cmds, r"""
public static void p9Tick(@PKG@.AbState s, @CB@ cb, long now) {
  if (now < s.p9Next) return;
  s.p9Next = now + (long) P9_STEP;
  for (int i = 0; i < 24; i++) {
    boolean low = i < 16;
    double rr = low ? s.radius : s.radius * 0.7;
    double[] xz = @PKG@.AbLogic.ring(s.ax, s.az, rr, low ? i : i - 16, low ? 16 : 8);
    double y = low ? s.ay + 0.15 : s.ay + s.radius * 0.7;
    try { @PTU@.spawnParticleEffect(s.fxName, new @V3D@(xz[0], y, xz[1]), cb); s.p9Calls = s.p9Calls + 1; }
    catch (Throwable t) { s.p9Fail = s.p9Fail + 1; }
  }
}""")
M(cmds, r"""
public static void p10Tick(@PKG@.AbState s, @CB@ cb, long now) {
  if (now < s.p10Next) return;
  s.p10Next = now + (long) P10_STEP;
  long t0 = System.nanoTime();
  java.util.List l = near(cb, s.ax, s.ay + 1.0, s.az, s.radius);
  for (int i = 0; i < l.size(); i++) {
    @REF@ t = (@REF@) l.get(i);
    if (t == null || !t.isValid() || s.removed.contains(t)) continue;
    java.util.UUID creator = null;
    boolean proj = false;
    try {
      Object sp = cb.getComponent(t, @SPP@.getComponentType());
      if (sp instanceof @SPP@) { proj = true; creator = ((@SPP@) sp).getCreatorUuid(); }
      Object lp = cb.getComponent(t, @LPC@.getComponentType());
      if (lp instanceof @LPC@) { proj = true; if (creator == null) creator = ((@LPC@) lp).getCreatorUuid(); }
    } catch (Throwable x) { proj = false; }
    if (!proj) continue;
    s.p10Seen = s.p10Seen + 1;
    if (creator != null && creator.equals(s.u)) { s.p10Own = s.p10Own + 1; s.removed.add(t); continue; }
    try { cb.removeEntity(t, @REMR@.REMOVE); s.removed.add(t); s.p10Removed = s.p10Removed + 1; }
    catch (Throwable x) { @PKG@.AbLog.warn("P10 remove failed: " + x); }
  }
  long ns = System.nanoTime() - t0;
  s.p10Scans = s.p10Scans + 1;
  s.p10Ns = s.p10Ns + ns;
  if (ns > s.p10Max) s.p10Max = ns;
}""")
M(cmds, r"""
public static void p13Tick(@PKG@.AbState s, @CB@ cb, @V3D@ p, float dt) {
  s.p13Ticks = s.p13Ticks + 1L;
  double d = (double) dt;
  if (!(d > 0.0)) d = 0.0;
  if (d > 0.2) d = 0.2;
  s.p13Acc = s.p13Acc + (double) s.zones * P13_HZ * d;
  long t0 = System.nanoTime();
  int n = 0;
  while (s.p13Acc >= 1.0 && n < 400) {
    s.p13Acc = s.p13Acc - 1.0;
    int i = s.p13Idx % (s.zones < 1 ? 1 : s.zones);
    s.p13Idx = s.p13Idx + 1;
    double[] xz = @PKG@.AbLogic.ring(p.x, p.z, P13_RING, i, s.zones);
    java.util.List l = near(cb, xz[0], p.y + 1.0, xz[1], P13_R);
    s.p13Ents = s.p13Ents + (long) l.size();
    n++;
  }
  long ns = System.nanoTime() - t0;
  s.p13Scans = s.p13Scans + (long) n;
  s.p13Ns = s.p13Ns + ns;
  if (ns > s.p13Max) s.p13Max = ns;
}""")
# ---- the per-player tick (AbTick, world thread, every tick)
M(cmds, r"""
public static void tickPlayer(@REF@ r, @ST@ store, @CB@ cb, float dt) {
  if (r == null || STATES.isEmpty()) return;
  @PR@ pr = prOf(cb, r);
  if (pr == null) return;
  @PKG@.AbState s = (@PKG@.AbState) STATES.get(pr.getUuid());
  if (s == null) return;
  if (s.st != store) { finish(s, pr, "ended: you changed world"); STATES.remove(pr.getUuid(), s); return; }
  long now = System.currentTimeMillis();
  if (s.p1CheckAt > 0L && now >= s.p1CheckAt) {
    s.p1CheckAt = 0L;
    double[] mv = stat(cb, r, @DST@.getMana());
    if (mv != null) tell(pr, "P1 cancel check: Mana " + f1(s.p1Mana) + " -> " + f1(mv[0]) + " 1 s later (" + (mv[0] + 0.01 >= s.p1Mana ? "PASS: nothing spent" : "FAIL: Mana went DOWN - the cancelled cast was paid") + ").");
  }
  if (s.mode == 0) return;
  if (now >= s.modeUntil) { finish(s, pr, null); return; }
  long t0 = System.nanoTime();
  int m = s.mode;
  if (m == 5) p5Tick(s, pr);
  else if (m == 6) p6Tick(s, cb, r, now);
  else if (m == 7) p7Tick(s, cb, r, now);
  else if (m == 8 || m == 12) p8Tick(s, pr, cb, r, now);
  else if (m == 9) p9Tick(s, cb, now);
  else if (m == 10) p10Tick(s, cb, now);
  else if (m == 13) { @V3D@ p = pos(cb, r); if (p != null) p13Tick(s, cb, p, dt); }
  long ns = System.nanoTime() - t0;
  s.ns = s.ns + ns;
  if (ns > s.nsMax) s.nsMax = ns;
  s.ticks = s.ticks + 1L;
}""")
# ---- the hooks
# P1 / P2 / P6: InteractionChainStartEvent (0.7, reached by reflection); the event's entity = the player
M(cmds, r"""
public static void onChain(Object ev, @REF@ r, @CB@ buf) {
  @PR@ pr = prOf(buf, r);
  long now = System.currentTimeMillis();
  @PKG@.AbState s = active(pr, -1, now);
  if (s == null || (s.mode != 1 && s.mode != 2 && s.mode != 6)) return;
  String type = String.valueOf(@PKG@.AbRefl.call0(ev, "getType"));
  int k = @PKG@.AbLogic.kind(type);
  s.chains = s.chains + 1;
  if (k == 1) s.chainAb = s.chainAb + 1;
  else if (k == 2) s.chainPrim = s.chainPrim + 1;
  else s.chainOther = s.chainOther + 1;
  if (k == 2 && s.mode == 6) {
    if (s.lastSwing > 0L && @PKG@.AbLogic.gapOk(now - s.lastSwing, (long) GAP_MAX)) { s.swGapSum = s.swGapSum + (now - s.lastSwing); s.swGapN = s.swGapN + 1; }
    s.lastSwing = now;
  }
  if (s.mode != 1) return;
  Object ctx = @PKG@.AbRefl.call0(ev, "getContext");
  Object root = @PKG@.AbRefl.call0(ev, "getRootInteractionId");
  if (root == null) root = @PKG@.AbRefl.call0(ctx, "getRootInteractionId");
  Object held = @PKG@.AbRefl.call0(ctx, "getHeldItem");
  String hid = held instanceof @IS@ ? ((@IS@) held).getItemId() : String.valueOf(held);
  String line = "P1 chain " + type + ", root " + root + ", held " + hid + " (+" + (now - s.armedAt) + " ms)";
  if (s.cancel && k == 1) {
    boolean ok = @PKG@.AbRefl.cancel(ev);
    if (ok) s.cancelled = s.cancelled + 1; else s.cancelFail = s.cancelFail + 1;
    line = line + (ok ? " -> CANCELLED" : " -> cancel FAILED");
    double[] mv = stat(buf, r, @DST@.getMana());
    if (ok && mv != null && s.p1CheckAt == 0L) { s.p1Mana = mv[0]; s.p1CheckAt = now + 1000L; }
  }
  if (s.lines < 30) { s.lines = s.lines + 1; tell(pr, line); } else @PKG@.AbLog.info(line);
}""")
M(cmds, r"""
public static boolean p5Watch(@DMG@ d, @REF@ target, @CB@ buf, long now) {
  if (active(prOf(buf, target), 5, now) != null) return true;
  return active(prOf(buf, attacker(d)), 5, now) != null;
}""")
# FILTER group, BEFORE ArmorDamageReduction: the amount before armour
M(cmds, r"""
public static void onEarly(@DMG@ d, @REF@ target, @CB@ buf) {
  if (d.isCancelled() || MINE.containsKey(d)) return;
  if (!p5Watch(d, target, buf, System.currentTimeMillis())) return;
  if (EARLY.size() > 4096) EARLY.clear();
  EARLY.put(d, Float.valueOf(d.getAmount()));
}""")
# REVIEW FIX R1: a probe (MINE) hit after armour is clamped again to the target's Health - 1; cancelled at <= 1 / unreadable Health
M(cmds, r"""
public static void clampMine(@DMG@ d, @REF@ target, @CB@ buf) {
  double[] hv = stat(buf, target, @DST@.getHealth());
  if (hv == null || !(hv[0] > 1.0)) { d.setCancelled(true); MINE.remove(d); return; }
  if ((double) d.getAmount() > hv[0] - 1.0) d.setAmount((float) (hv[0] - 1.0));
}""")
# p5 save: a lethal hit on s's player is cancelled and their Health set to SAVE_PCT % (true = cancelled here)
M(cmds, r"""
public static boolean saveIfLethal(@DMG@ d, @REF@ target, @CB@ buf, @PR@ tpr, @PKG@.AbState s) {
  if (s == null || !s.save) return false;
  int hi = @DST@.getHealth();
  double[] hv = stat(buf, target, hi);
  if (hv == null || !@PKG@.AbLogic.lethal(hv[0], (double) d.getAmount())) return false;
  try {
    @ESM@ m = (@ESM@) buf.getComponent(target, @ESM@.getComponentType());
    if (m == null) return false;
    float to = @PKG@.AbLogic.saveHealth(hv[1], SAVE_PCT);
    d.setCancelled(true);
    m.setStatValue(hi, to);
    s.save = false;
    s.saves = s.saves + 1;
    tell(tpr, "P5 SAVE: a lethal " + causeOf(d) + " hit of " + f1((double) d.getAmount()) + " (Health " + f1(hv[0]) + ") was cancelled in our late filter, Health set to " + f1((double) to) + ". Did you survive, with no death screen and no armour / durability oddity?");
    return true;
  } catch (Throwable t) { tell(tpr, "P5 save failed: " + t); return d.isCancelled(); }
}""")
# FILTER group, AFTER ArmorDamageReduction: the amount after armour + the Guardian Spirit shape (p5 save)
M(cmds, r"""
public static void onLate(@DMG@ d, @REF@ target, @CB@ buf) {
  if (d.isCancelled()) return;
  if (MINE.containsKey(d)) { clampMine(d, target, buf); return; }
  long now = System.currentTimeMillis();
  if (!p5Watch(d, target, buf, now)) return;
  if (LATE.size() > 4096) LATE.clear();
  LATE.put(d, Float.valueOf(d.getAmount()));
  @PR@ tpr = prOf(buf, target);
  @PKG@.AbState s = active(tpr, 5, now);
  @PKG@.AbState sa = active(prOf(buf, attacker(d)), 5, now);
  if (!saveIfLethal(d, target, buf, tpr, s)) {
    if (s != null) s.p5Late = s.p5Late + 1;
    if (sa != null) sa.p5Late = sa.p5Late + 1;
  }
}""")
M(cmds, r"""
public static void p5Line(@PKG@.AbState s, @PR@ pr, String who, @DMG@ d, Float e, Float l) {
  if (s == null) return;
  s.p5Seen = s.p5Seen + 1;
  if (l != null && !d.isCancelled()) s.p5Landed = s.p5Landed + 1;
  float got = d.getAmount();
  boolean changed = l != null && Math.abs(l.floatValue() - got) > 0.01f;
  if (changed) s.p5Changed = s.p5Changed + 1;
  String line = "P5 " + who + " " + causeOf(d) + ": before armour " + (e == null ? "-" : f1((double) e.floatValue())) + ", after armour " + (l == null ? "-" : f1((double) l.floatValue())) + (d.isCancelled() ? ", CANCELLED after our late filter" : ", landed " + f1((double) got)) + (changed ? "  <- changed AFTER our late filter" : "");
  if (s.lines < 30) { s.lines = s.lines + 1; tell(pr, line); } else @PKG@.AbLog.info(line);
}""")
# INSPECT group: landed amounts (P5), your landed hits (P2 / P6), the probe mob hitting you (P8 / P12)
M(cmds, r"""
public static void onSeen(@DMG@ d, @REF@ target, @CB@ buf) {
  if (MINE.remove(d) != null) { EARLY.remove(d); LATE.remove(d); return; }
  Float e = (Float) EARLY.remove(d);
  Float l = (Float) LATE.remove(d);
  long now = System.currentTimeMillis();
  @REF@ a = attacker(d);
  @PR@ apr = prOf(buf, a);
  @PR@ tpr = prOf(buf, target);
  if (e != null || l != null) {
    p5Line(active(tpr, 5, now), tpr, "you took", d, e, l);
    p5Line(active(apr, 5, now), apr, "you dealt", d, e, l);
  }
  @PKG@.AbState sa = active(apr, -1, now);
  if (sa != null && (sa.mode == 2 || sa.mode == 6)) {
    sa.hits = sa.hits + 1;
    if (sa.lastHit > 0L && @PKG@.AbLogic.gapOk(now - sa.lastHit, (long) GAP_MAX)) { sa.hitGapSum = sa.hitGapSum + (now - sa.lastHit); sa.hitGapN = sa.hitGapN + 1; }
    sa.lastHit = now;
  }
  @PKG@.AbState sm = active(tpr, -1, now);
  if (sm != null && (sm.mode == 8 || sm.mode == 12) && a != null && a.equals(sm.target)) {
    sm.mobHits = sm.mobHits + 1;
    if (sm.lines < 20) { sm.lines = sm.lines + 1; tell(tpr, "P" + sm.mode + ": the mob HIT you (" + f1((double) d.getAmount()) + ") at +" + (now - sm.armedAt) + " ms."); }
  }
}""")
# P4 watch: InventoryChangeEvent on you - which container (AbilitySlots / RuneBag re-read each time: the component can be replaced)
M(cmds, r"""
public static void onInv(Object ev, @REF@ r, @ST@ st) {
  @PR@ pr = prOf(st, r);
  @PKG@.AbState s = active(pr, 4, System.currentTimeMillis());
  if (s == null) return;
  Object ic = null;
  try { ic = ((@ICE@) ev).getItemContainer(); } catch (Throwable t) { ic = null; }
  Object ab = containerOf(compOf(st, r, ABSLOTS));
  Object bag = containerOf(compOf(st, r, RUNEBAG));
  String where = "another container";
  if (ic != null && ic == ab) { s.invSlots = s.invSlots + 1; where = "the AbilitySlots (-11)"; }
  else if (ic != null && ic == bag) { s.invBag = s.invBag + 1; where = "the RuneBag (-12)"; }
  else s.invOther = s.invOther + 1;
  if (s.lines < 20 && ic != null && (ic == ab || ic == bag)) { s.lines = s.lines + 1; tell(pr, "P4 watch: InventoryChangeEvent on " + where + "; slots now " + slots((@IC@) ic, true, 6)); }
}""")
# ---- one entry point for every usage variant: w = the words after /aprobe
M(cmds, r"""
public static void run(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ world, String[] w) {
  String t = @PKG@.AbLogic.low(@PKG@.AbLogic.word(w, 0));
  String l1 = @PKG@.AbLogic.low(@PKG@.AbLogic.word(w, 1));
  StringBuilder all = new StringBuilder();
  for (int i = 0; w != null && i < w.length; i++) { if (w[i] != null) all.append(" ").append(w[i]); }
  @PKG@.AbLog.info(pr.getUsername() + " ran /aprobe" + all.toString());
  if (t == null || "help".equals(t)) { help(pr); return; }
  if ("info".equals(t)) { info(pr); return; }
  if ("stats".equals(t)) { stats(pr); return; }
  if ("stop".equals(t)) {
    @PKG@.AbState s0 = (@PKG@.AbState) STATES.remove(pr.getUuid());
    if (s0 != null) finish(s0, pr, "stopped");
    tell(pr, "Probe state cleared.");
    return;
  }
  if ("p3".equals(t)) { p3(pr, st, ref, w); return; }
  if ("p4".equals(t) && !"watch".equals(l1)) { p4(pr, st, ref, w); return; }
  if ("p11".equals(t)) { p11(pr, st, ref, world, w); return; }
  if ("p12".equals(t) && !"stun".equals(l1)) { p12(pr, st, ref); return; }
  if ("p14".equals(t)) { p14(pr, st, ref); return; }
  if ("p15".equals(t)) { p15(pr, st, ref); return; }
  @PKG@.AbState s = state(pr, ref, st);
  if (s.mode != 0) finish(s, pr, "ended early (a new probe was armed)");
  long now = System.currentTimeMillis();
  String err = plan(s, w, now);
  if (err != null) { tell(pr, err); return; }
  String err2 = start(s, pr, st, ref, now);
  if (err2 != null) { clear(s); tell(pr, err2); return; }
  tell(pr, armedText(s));
}""")

# ---- AbTick: EntityTickingSystem on Player (one registerSystem per class), world thread, every tick
tick = mk("AbTick", T["ETS"])
F(tick, "public static boolean FAILED_ONCE = false;")
C(tick, "public AbTick() { super(); }")
M(tick, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(tick, "public boolean isParallel(int a, int b) { return false; }")
M(tick, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (chunk == null || @PKG@.AbCmds.STATES.isEmpty()) return;
    @PKG@.AbCmds.tickPlayer(chunk.getReferenceTo(idx), store, cb, dt);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.AbLog.warn("tick failed (logged once): " + t); }
  }
}""")


# ---- the two FILTER systems, ordered around ArmorDamageReduction (SkyyArmory ArmoryTuneSys / SkyyGear dmg_system shape); ordered=false
#      = the unordered fallback (SkyyArmory registers the same class again unordered when the ordered registration throws)
def filter_sys(name, order, hook):
    c = mk(name, T["DES"])
    for f in ("public static Class ADR;", "public static boolean FAILED_ONCE = false;", "public java.util.Set deps;", "public boolean ordered;"):
        F(c, f)
    C(c, r"""
public %s(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  this.ordered = ordered && ADR != null;
  if (this.ordered) this.deps.add(new @SDEP@(@ORD@.%s, ADR));
}""" % (name, order))
    M(c, "public @QRY@ getQuery() { return @QRY@.any(); }")
    M(c, "public @SG@ getGroup() { return @DMOD@.get().getFilterDamageGroup(); }")
    M(c, "public java.util.Set getDependencies() { return this.deps; }")
    M(c, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@) || chunk == null || @PKG@.AbCmds.STATES.isEmpty()) return;
    @PKG@.AbCmds.%s((@DMG@) ev, chunk.getReferenceTo(idx), buf);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.AbLog.warn("%s failed (logged once): " + t); }
  }
}""" % (hook, name))
    return c


early = filter_sys("AbEarlySys", "BEFORE", "onEarly")
late = filter_sys("AbLateSys", "AFTER", "onLate")

# ---- AbSeenSys: DamageEventSystem in the INSPECT group (after the damage landed; cancelled events never arrive)
seen = mk("AbSeenSys", T["DES"])
F(seen, "public static boolean FAILED_ONCE = false;")
C(seen, "public AbSeenSys() { super(); }")
M(seen, "public @QRY@ getQuery() { return @QRY@.any(); }")
M(seen, "public @SG@ getGroup() { return @DMOD@.get().getInspectDamageGroup(); }")
M(seen, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@) || chunk == null) return;
    @DMG@ d = (@DMG@) ev;
    if (@PKG@.AbCmds.STATES.isEmpty()) { @PKG@.AbCmds.MINE.remove(d); return; }
    @PKG@.AbCmds.onSeen(d, chunk.getReferenceTo(idx), buf);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.AbLog.warn("inspect hook failed (logged once): " + t); }
  }
}""")

# ---- AbInvSys: InventoryChangeEvent on the player (SkyySkills SmeltSys / SkyyGear GearInvSys pattern) - P4 watch
inv = mk("AbInvSys", T["EES"])
F(inv, "public static boolean FAILED_ONCE = false;")
C(inv, "public AbInvSys() { super(@ICE@.class); }")
M(inv, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(inv, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (chunk == null || @PKG@.AbCmds.STATES.isEmpty()) return;
    @PKG@.AbCmds.onInv(ev, chunk.getReferenceTo(idx), st);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.AbLog.warn("inventory hook failed (logged once): " + t); }
  }
}""")

# ---- AbChainSys: EntityEventSystem on the 0.7 InteractionChainStartEvent. The event class is handed in at run time (Class.forName), so
#      this class names no 0.7 type and loads on 0.6.8; the plugin only builds it when the class exists.
chain = mk("AbChainSys", T["EES"])
F(chain, "public static boolean FAILED_ONCE = false;")
C(chain, "public AbChainSys(Class evt) { super(evt); }")
M(chain, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(chain, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (chunk == null || @PKG@.AbCmds.STATES.isEmpty()) return;
    @PKG@.AbCmds.onChain(ev, chunk.getReferenceTo(idx), buf);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.AbLog.warn("chain hook failed (logged once): " + t); }
  }
}""")

# ---- /aprobe and its usage variants (admin: requirePermission + no permission groups on each)
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
ARG_DESCS = ["probe", "first value", "second value", "third value"]


def variant(n):
    """/aprobe with n words: one usage variant class (admin: requirePermission + no permission groups, like the root)"""
    cname = "AProbeArg%dCmd" % n
    vc = mk(cname, T["APC"])
    for i in range(n):
        F(vc, "public @RA@ a%d;" % i)
    usage = "(admin) /aprobe " + " ".join("<%s>" % d for d in ARG_DESCS[:n])
    args = "\n".join('  this.a%d = withRequiredArg("%s", "%s", @ATY@.STRING);' % (i, ARG_DESCS[i].replace(" ", ""),
                     "p1 .. p15, info, stats, stop" if i == 0 else "a word or a number") for i in range(n))
    C(vc, r"""
public %s() {
  super("%s");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
%s
}""" % (cname, usage, args))
    reads = "\n".join("    w[%d] = String.valueOf(ctx.get(this.a%d));" % (i, i) for i in range(n))
    M(vc, EXEC + r""" {
  String[] w = new String[%d];
  try {
%s
  } catch (Throwable t) { @PKG@.AbLog.tell(pr, "Usage: /aprobe <probe> [values]"); return; }
  @PKG@.AbCmds.run(ref, store, pr, world, w);
}""" % (n, reads))
    return vc


VARIANTS = [variant(1), variant(2), variant(3), variant(4)]
cmd = mk("AProbeCmd", T["APC"])
C(cmd, r"""
public AProbeCmd() {
  super("aprobe", "(admin) Class-ability engine probes P1-P15 (throwaway dev pack): /aprobe lists them");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "abilityprobe" });
  addUsageVariant(new @PKG@.AProbeArg1Cmd());
  addUsageVariant(new @PKG@.AProbeArg2Cmd());
  addUsageVariant(new @PKG@.AProbeArg3Cmd());
  addUsageVariant(new @PKG@.AProbeArg4Cmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.AbCmds.help(pr);
}""")

# ---- the plugin
pl = mk("SkyyAbilityProbePlugin", T["JP"])
C(pl, "public SkyyAbilityProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.AbLog.LOG = getLogger();
  getCommandRegistry().registerCommand(new @PKG@.AProbeCmd());
  getEntityStoreRegistry().registerSystem(new @PKG@.AbTick());
  Class adr = @PKG@.AbRefl.cls("%s");
  @PKG@.AbEarlySys.ADR = adr;
  @PKG@.AbLateSys.ADR = adr;
  try { getEntityStoreRegistry().registerSystem(new @PKG@.AbEarlySys(true)); @PKG@.AbCmds.ORDER_EARLY = adr == null ? "UNORDERED (no ArmorDamageReduction)" : "BEFORE ArmorDamageReduction"; }
  catch (Throwable t1) {
    @PKG@.AbLog.warn("could not order the early filter (" + t1 + ") - unordered");
    try { getEntityStoreRegistry().registerSystem(new @PKG@.AbEarlySys(false)); @PKG@.AbCmds.ORDER_EARLY = "UNORDERED (" + t1.getClass().getSimpleName() + ")"; } catch (Throwable t2) { @PKG@.AbCmds.ORDER_EARLY = "FAILED " + t2; }
  }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.AbLateSys(true)); @PKG@.AbCmds.ORDER_LATE = adr == null ? "UNORDERED (no ArmorDamageReduction)" : "AFTER ArmorDamageReduction"; }
  catch (Throwable t1) {
    @PKG@.AbLog.warn("could not order the late filter (" + t1 + ") - unordered");
    try { getEntityStoreRegistry().registerSystem(new @PKG@.AbLateSys(false)); @PKG@.AbCmds.ORDER_LATE = "UNORDERED (" + t1.getClass().getSimpleName() + ")"; } catch (Throwable t2) { @PKG@.AbCmds.ORDER_LATE = "FAILED " + t2; }
  }
  getEntityStoreRegistry().registerSystem(new @PKG@.AbSeenSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.AbInvSys());
  Class ce = @PKG@.AbRefl.cls("%s");
  if (ce == null) @PKG@.AbCmds.CHAIN_WHY = "Hytale 0.6.8 has no such class";
  else {
    try { getEntityStoreRegistry().registerSystem(new @PKG@.AbChainSys(ce)); @PKG@.AbCmds.CHAIN_ON = true; @PKG@.AbCmds.CHAIN_WHY = "listening"; }
    catch (Throwable t3) { @PKG@.AbCmds.CHAIN_WHY = "registration failed: " + t3; @PKG@.AbLog.warn("InteractionChainStartEvent hook failed: " + t3); }
  }
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyAbilityProbe] @VERSION@ ready - /aprobe (admin): ability engine probes P1-P15 (throwaway dev pack, remove after the test session); chain event " + @PKG@.AbCmds.CHAIN_WHY + "; filters " + @PKG@.AbCmds.ORDER_EARLY + " / " + @PKG@.AbCmds.ORDER_LATE);
}""" % (ADRS, CHAIN_EVT))
M(pl, r"""
protected void shutdown() {
  try {
    java.util.Iterator it = @PKG@.AbUnplace.PLACED.keySet().iterator();
    while (it.hasNext()) @PKG@.AbLog.warn("P11 block still placed at " + it.next() + " - remove it by hand");
  } catch (Throwable t) { }
  @PKG@.AbCmds.STATES.clear();
  @PKG@.AbCmds.MINE.clear();
  @PKG@.AbCmds.EARLY.clear();
  @PKG@.AbCmds.LATE.clear();
  super.shutdown();
}""")

ALL = [log, lg, rf, sta, unp, cmds, tick, early, late, seen, inv, chain] + VARIANTS + [cmd, pl]
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d (P11 %s; 0.7 classes on this jar: %s)" % (len(ALL), "built" if P11_BUILT else "NOT built", V07))

jar = os.path.join(HERE, "SkyyAbilityProbe-%s.jar" % VERSION)
man = B.manifest("SkyyAbilityProbe", VERSION, "SkyWynn THROWAWAY dev pack: class-ability engine probes P1-P15 (/aprobe, admin only) - rune keys and chain events, cooldown handler, ability slots, damage filter order, swing speed, Mana costs, stunlock, dome particles, projectile removal, banner block, NPC targeting, scan cost, profile leak, Mana scale. Pinned for one test session, then removed.", PKG + ".SkyyAbilityProbePlugin")
man["IncludesAssetPack"] = False   # class-only jar, like SkyyMonkProbe / SkyyClasses 0.1.14 (the harness asserts it)
B.assemble(jar, man, OUT, {})
