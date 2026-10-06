"""Derive SkyyArmory/build_skyyarmory_0.1.1.py (+ its harness SkyyArmory/test_skyyarmory_0.1.1.py) from the LIVE 0.1
(SkyyArmory/build_skyyarmory_0.1.py = the tools/deploy_set.py SET pin; test_skyyarmory_0.1.py = its harness). SkyyArmory 0.1 had no patch
history, so this is its FIRST patch: every anchor is asserted (rep = exactly one hit). Edit THIS file, never the generated scripts.
Run:  python tools/armory_0_1_1_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.1.py   then   python SkyyArmory/test_skyyarmory_0.1.1.py
      (never --deploy: deploy order SkyyClasses 0.1.12 -> SkyyArmory 0.1.1 -> SkyyGear 0.2.4, spec 3.4)

0.1.1 = MAGIC TRAVERSALS (research/Magic-Traversal-Spec.md; section 8 = Skyy's answers 2026-10-05, LOCKED, beats sections 0-7):
  STAFF HOLD = BLINK: the charged chain launches an invisible marker projectile SkyyArmory_Blink_<M> (Damage 0, Gravity 0, model
    SkyyArmory_Marker = the orb model without attachment / particles / trails); ArmoryTravSys (RefSystem on projectiles, SPAWN) zeroes its
    launch velocity, and a world-thread job (TravJob) scans the look direction (TravMath.scan: 0.5-block steps, the body box 0.6 wide x 3
    heights must be passable = engine BlockType material not Solid, ground within blink.floorCheck below, a blocked step is refined back in
    0.05 steps, nothing free beyond 1 block = no blink) and puts Teleport.createForPlayer(world, dest, rotation) (+ head rotation,
    .withoutVelocityReset() while blink.keepFall is on) on the caster. A BLINK THAT DOES NOT MOVE YOU COSTS NOTHING (Skyy): the chain's
    client-predicted Mana is given back (EntityStatMap.addStatValue) and no Stamina is taken - also for the class lock, the cooldown and
    too little Stamina. A real blink costs the chain's Mana AND Stamina = Mana x trav.staminaPercent % (50 = Skyy's 2 Mana : 1 Stamina),
    at most trav.staminaCap. The marker stays for blink.trailSeconds as the trail's damage source (Damage$ProjectileSource(caster,
    marker) = the shape of a vanilla orb hit, so ArmoryTuneSys' staff tune and SkyyGear's spell level scale the trail like orb hits);
    TravTick (EntityTickingSystem on Player, once per world tick) hits every enemy inside the capsule every blink.tick seconds for
    blink.trailPercent % of the staff's charged damage per second, then removes the marker. staff.mode orb / part.trav off = the 0.1
    charged orb (SkyyArmory_StaffOrb_<M> spawned with the marker's velocity through ProjectileComponent.assembleDefaultProjectile, the
    LaunchProjectileInteraction#firstRun steps). The staff casts no longer spend the vanilla 5 Stamina / 1.5 s regen pause (both elements
    and both interaction files are gone): only the blink itself pays Stamina.
  WAND HOLD = HOP BACK + BURST + HEAL ORB: at the charged orb's SPAWN the caster gets Velocity.addInstruction(-look x hop.force, the
    dagger dash's VelocityConfig, Set) - look down = straight up; no ground within hop.groundCheck under the spot 3 blocks behind = half
    the force; the hop costs Stamina (as above; too little = the orb flies without a hop). ArmoryHitSys (Inspect damage group): the
    orb's direct hit keeps its vanilla damage; every OTHER enemy within burst.radius takes burst.percent % of the hit's initial amount
    (through the full damage pipeline, so tune / Gear / armour apply once); a heal orb (orb.radius, orb.seconds) heals every orb.tick
    every NON-HOSTILE player inside for orb.healPercent % of the landed burst damage per second x orb.partyPercent % (Skyy: "heals
    everyone, but party more"): through SkyyClasses 0.1.12's class:fn:heal (Object[]{healer, target, Double hp, "armory:orb", the wand
    id}) - IT splits party / others (its priestHeal.othersPercent, default 50) and applies the wand's charged cap, the per-second budget,
    Divinity XP and the chat lines; without SkyyClasses Armory splits itself (orb.othersPercent, default 50) straight into Health (no XP).
    A miss (the orb ends on a block) bursts where it ended (asset damage x tune, Damage$EntitySource(caster)).
  QUICK SHOTS: wand taps PIERCE with no cap (Skyy; pierce.max 0 = none): each enemy hit spawns a continuation orb past it (same id, same
    shooter, the original start), an enemy the chain already hit is never hit again (ArmoryTuneSys cancels it); quick orbs vanish past
    quick.range.wand (16) / quick.range.staff (24) blocks (TravTick); staff quick hits x (1 + quick.staffBonus %) (15).
  ENEMIES: NPCs with stats; players only where the world's PvP is on AND trav.players is on AND they are not the caster's party
    (class:fn:ally, else party:fn:members). No traversal locks on to anything (Skyy: lock-on = party only - none here).
  Bridge: armory:fn:info answers 11 elements ([8] traversal words, [9] quick words, [10] Double staff quick bonus %), armory:trav (live
    numbers), reads class:fn:heal / class:fn:ally / class:fn:allowed / party:fn:members. Rows: Server Setup > Armory (categories trav /
    blink / hop / burst; quick.life is now Advanced). Pure maths in TravMath (bare-JVM tested on a fake grid).
  FIX ROUND (trav-fix 2026-10-06, critic findings): the pierce continuation spawns only when the line from the hit to its spawn point is
    passable (TravMath.clear - no shot through a wall); the hop keeps a damaging fall (vy = min(hop vy, client vy) when falling faster
    than the world's MinFallSpeedToEngageRoll, Double-Jump rule 7); blink / hop / burst check SkyyClasses' class lock on the CAST weapon
    (not only the hand); Damage.HIT_LOCATION is read as the engine's Vector4d; an idle world's TravWorld is dropped (no Store kept after an
    island unloads); SkyyClasses present without class:fn:heal (older than 0.1.12) = the heal orb heals nobody (one WARN) and the build
    asserts the SkyyClasses 0.1.12 pin; orb.othersPercent is Advanced and labelled "(no SkyyClasses)".
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.1.py")
TSRC = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.1.py")

raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1"\nMOD = "SkyyArmory"' in s and "FIX ROUND (2026-10-03, review findings" in s, "build_skyyarmory_0.1.py is not the live 0.1"
SYS0 = s.count("registerSystem(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:140])
    s = s.replace(old, new)


# ================================================================================================ header + version
rep('"""SkyyArmory 0.1 - build script (javassist via jpype). NEW MOD:',
    '"""SkyyArmory 0.1.1 - build script (javassist via jpype). GENERATED by tools/armory_0_1_1_patch.py from the LIVE 0.1 - edit the patch,\n'
    'never this file. Run: python SkyyArmory/build_skyyarmory_0.1.1.py -> SkyyArmory/SkyyArmory-0.1.1.jar (never --deploy). Harness:\n'
    'python SkyyArmory/test_skyyarmory_0.1.1.py (scratch tools/dev/scratch/armory011/).\n\n'
    + open(__file__, encoding="utf8").read().split('"""')[1].split("\n", 3)[3].strip() + "\n\n"
    '0.1 (the base, everything below is still true unless 0.1.1 above says otherwise):\nSkyyArmory 0.1 - build script (javassist via jpype). NEW MOD:')
rep('VERSION = "0.1"\nMOD = "SkyyArmory"', 'VERSION = "0.1.1"\nMOD = "SkyyArmory"')
# trav-fix 2026-10-06 (critic): 0.1.1's heal orb needs SkyyClasses 0.1.12's class:fn:heal (the Priest check, the wand cap, the budget, XP) -
# pinning Armory 0.1.1 next to Classes 0.1.11 stops this build (at runtime an older Classes = the orb heals nobody, one WARN)
rep('CLASSES_PARTNER = "0.1.11"\n', 'CLASSES_PARTNER = "0.1.12"     # 0.1.1 (trav-fix): class:fn:heal; 0.1: 0.1.11 (the wand heal caps)\n')
# tools/deploy_set.py's PACK_THIRD_PARTY list spans several lines since 2026-10-05 (the pack round): read it with DOTALL
rep('''PACKS = re.findall(r'"([^"]+:[^"]+)"', re.search(r"PACK_THIRD_PARTY = \\[(.*?)\\]", _dst).group(1))''',
    '''PACKS = re.findall(r'"([^"]+:[^"]+)"', re.search(r"PACK_THIRD_PARTY = \\[(.*?)\\]", _dst, re.S).group(1))''')
rep('assert PACK_KEY == "Skyy:0.1 SkyyArmory", PACK_KEY', 'assert PACK_KEY == "Skyy:%s SkyyArmory" % VERSION, PACK_KEY')

# ================================================================================================ 0.1.1 constants (spec 3.1.1)
rep("# ================================================================= the ONE cost table", r'''# ================================================================= 0.1.1 MAGIC TRAVERSALS (research/Magic-Traversal-Spec.md 3.1.1)
STAFF_STAMINA = 0                # quick / normal staff casts cost no Stamina (Skyy 2026-10-04 + 2026-10-05); only the blink pays (server)
HOP_MODE = "server"              # "server" = the Java push (live force + void check) | "asset" = the client dash (ApplyForce in the chain)
SCAN_MODE = "step"               # the blink scan: 0.5-block steps (the only mode built)
ORB_LOOK = "particles"           # the heal orb look: particles (the only look built; "totem" = a vanilla deployable - left out)
TRAIL_COLOR = "#ffe9a0"          # the blink trail's light (gold recolour of the orb particles)
assert STAFF_STAMINA == 0 and HOP_MODE in ("server", "asset") and SCAN_MODE == "step" and ORB_LOOK == "particles"
ID_SBLINK = "SkyyArmory_Blink_%s"
MARKER = "SkyyArmory_Marker"
PS_TRAIL = "SkyyArmory_Trail_Light"
ID_WHOP = "SkyyArmory_Wand_Hop"
FX_PORTAL, SND_BLINK = "Portal_Teleport", "SFX_Portal_Neutral_Teleport_Local"
PS_BURST, SND_BURST = "Explosion_Small", "SFX_Staff_Flame_Fireball_Impact"
PS_HEAL, SND_HEAL = "Totem_Heal_Simple_Test", "SFX_Deployable_Totem_Heal_Spawn"
MARKER_TTL = 10.0                # the marker outlives the longest trail (blink.trailSeconds max 8 s); removed by TravTick at the end
TRAV = dict(                     # the row defaults (spec 1.4 + section 8)
    part=True, mode="blink", dist=10, floor=12, keepFall=True, trailOn=True, trailWidth=1.5, trailSeconds=3.0, trailPct=30, tick=0.5,
    cd=0.0, hopForce=13.0, hopGround=6, burstR=6.0, burstPct=60, orbR=9.0, orbSec=3.5, orbPct=20, orbTick=1.0, partyPct=100,
    othersPct=50, players=True, maxLive=64, fx=True, stamPct=50, stamCap=10, pierce=0, rangeW=16, rangeS=24, staffBonus=15)

# ================================================================= the ONE cost table''')
rep('SWITCHES = ("WAND_STYLE", "QUICK_LOOK",', 'SWITCHES = ("HOP_MODE", "WAND_STYLE", "QUICK_LOOK",')

# ================================================================================================ vanilla shapes 0.1.1 relies on
rep('''for _st in ("Mana", "Stamina", "StaminaRegenDelay"):
    assert az_has("stat", _st), "no entity stat %s" % _st
''', '''for _st in ("Mana", "Stamina", "StaminaRegenDelay"):
    assert az_has("stat", _st), "no entity stat %s" % _st
# ---- 0.1.1: every vanilla id the traversals name (FX + the dagger dash's push feel) - the build stops if Hytale renames one
for _s in (SND_BLINK, SND_BURST, SND_HEAL):
    assert az_has("sound", _s), "no sound event %s" % _s
for _p in (PS_BURST, PS_HEAL, "GreenOrbTrail"):
    assert _p in _IDX["psys"], "no particle system %s" % _p
assert [n for n in AZ_NAMES if n.startswith("Server/Entity/Effects/") and n.endswith("/" + FX_PORTAL + ".json")], "no entity effect " + FX_PORTAL
DASH = az_get("int", "Daggers_Dash_Backward")["Interactions"][0]
assert DASH["Type"] == "ApplyForce" and DASH["Force"] == 13 and DASH["ChangeVelocityType"] == "Set" and DASH["Direction"] == {"X": 0, "Y": 0, "Z": 5}, DASH
DASH_CFG = DASH["VelocityConfig"]
assert DASH_CFG == {"AirResistance": 0.97, "AirResistanceMax": 0.96, "GroundResistance": 0.94, "GroundResistanceMax": 0.82, "Threshold": 5.0,
                    "Style": "Exp"}, DASH_CFG
assert VORB["TimeToLive"] < MARKER_TTL and "Damage" in VORB and "Gravity" in VORB
''')

# ================================================================================================ staff chain: no Stamina, the hold launches the marker
rep('''add_int(P_SINT, ID_SSTAM, {"Type": "ChangeStat", "StatModifiers": {"Stamina": -5}})
add_int(P_SINT, ID_SSTAMD, {"Type": "ChangeStat", "Behaviour": "Set", "StatModifiers": {"StaminaRegenDelay": -1.5}})
''', '''# 0.1.1 (STAFF_STAMINA 0): no SkyyArmory_Staff_Stamina / _Stamina_Delay any more - the staff casts spend Mana only; the blink pays its
# Stamina on the server (only when it really moves you)
''')
rep('''    add_int(P_SINT, ID_SLAUNCH % _m, launch(ID_SORB % _m, "CastSummonCharged"))
    add_int(P_SINT, ID_SCAST % _m, stats_check(_c, VSC["RunTime"], [ID_SSTAM, ID_SSTAMD, ID_SCOST % _m, ID_SLAUNCH % _m, ID_SCEFF], ID_SFAIL))''',
    '''    add_int(P_SINT, ID_SLAUNCH % _m, launch(ID_SBLINK % _m, "CastSummonCharged"))     # 0.1.1: the blink marker (orb mode: Java spawns the orb)
    add_int(P_SINT, ID_SCAST % _m, stats_check(_c, VSC["RunTime"], [ID_SCOST % _m, ID_SLAUNCH % _m, ID_SCEFF], ID_SFAIL))''')
# HOP_MODE "asset" (verification builds only): the client dash as a 4th Parallel element of every metal wand's charged cast
rep('''    add_int(P_WINT, ID_WCAST % _m, stats_check(_c, VWC["RunTime"], [ID_WCOST % _m, ID_WLAUNCH % _m, ID_WCEFF], ID_WFAIL))''',
    '''    if HOP_MODE == "asset" and ID_WHOP not in INTS:
        add_int(P_WINT, ID_WHOP, {"Type": "ApplyForce", "Force": DASH["Force"], "Direction": {"X": 0, "Y": 0, "Z": 5}, "AdjustVertical": True,
                                  "ChangeVelocityType": "Set", "VelocityConfig": dict(DASH_CFG)})
    add_int(P_WINT, ID_WCAST % _m, stats_check(_c, VWC["RunTime"], [ID_WCOST % _m, ID_WLAUNCH % _m, ID_WCEFF] + ([ID_WHOP] if HOP_MODE == "asset" else []),
                                               ID_WFAIL))''')

# ================================================================================================ the blink marker projectiles + model + trail light
rep('''for _m, _c, _q, _k, _cd, _qd in ST:
    add_prj(ID_SORB % _m, orb(_cd))
    if STAFF_TAP == "quick":
        add_prj(ID_SQORB % _m, quick_orb(_qd))
''', '''for _m, _c, _q, _k, _cd, _qd in ST:
    add_prj(ID_SORB % _m, orb(_cd))
    if STAFF_TAP == "quick":
        add_prj(ID_SQORB % _m, quick_orb(_qd))


def blink_marker():
    """0.1.1 (spec 2.2): the invisible, harmless marker the staff hold launches - the orb's flight fields, Damage 0, Gravity 0, no hit /
    death particles, the marker model, a life longer than any trail (TravTick removes it)"""
    d = orb(0)
    d["Appearance"] = MARKER
    d["Gravity"] = 0
    d["TimeToLive"] = MARKER_TTL
    d["DeathEffectsOnHit"] = False
    d.pop("HitParticles", None)
    d.pop("DeathParticles", None)
    return d


for _m in METALS:
    add_prj(ID_SBLINK % _m, blink_marker())
''')
rep('''put(P_MODEL % QMODEL, _qm)
QMODEL_JSON = _qm
''', '''put(P_MODEL % QMODEL, _qm)
QMODEL_JSON = _qm
# 0.1.1: the marker model = the orb model without its attachment, particles and trails (base texture Projectile_default.png is fully
# transparent, S:2.3) -> an invisible projectile; the same hitbox
_mk = json.loads(json.dumps(VORBM))
_mk["DefaultAttachments"] = []
_mk["Particles"] = []
_mk["Trails"] = []
put(P_MODEL % MARKER, _mk)
MARKER_JSON = _mk


def gold_color(x):
    """a vanilla particle colour moved onto the trail's light hue (TRAIL_COLOR), saturation / value / alpha kept"""
    m = re.match(r"^(rgba\\()?#([0-9a-fA-F]{6})([0-9a-fA-F]{2})?(.*)$", x)
    if not m:
        return x
    h6 = m.group(2)
    r, g, b = (int(h6[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
    th, ts, tv = colorsys.rgb_to_hsv(*(int(TRAIL_COLOR[i:i + 2], 16) / 255.0 for i in (1, 3, 5)))
    if ss > 0.15:
        r, g, b = colorsys.hsv_to_rgb(th, min(ss, max(ts, 0.35)), max(vv, tv * 0.8))
    out = "#%02x%02x%02x" % tuple(int(round(c * 255)) for c in (r, g, b))
    return (m.group(1) or "") + out + (m.group(3) or "") + m.group(4)


def gold_tree(x):
    if isinstance(x, dict):
        return dict((k, (gold_color(v) if (k == "Color" and isinstance(v, str)) else gold_tree(v))) for k, v in x.items())
    if isinstance(x, list):
        return [gold_tree(v) for v in x]
    return x


assert hue(gold_color("#5bff57")) != hue("#5bff57") and abs(hue(gold_color("#5bff57")) - hue(TRAIL_COLOR)) < 2.0
TRAIL_FILES = []
_gt = json.loads(AZ.read(_IDX["psys"]["GreenOrbTrail"][0]).decode("utf-8-sig"))
for _sp in _gt["Spawners"]:
    _src = _sp["SpawnerId"]
    _dst = "SkyyArmory_Trail_" + _src.replace("GreenOrb", "")
    assert _src in _IDX["pspawn"] and _dst not in PSP.values(), _src
    if (P_PSPAWN % _dst) not in ASSETS:
        put(P_PSPAWN % _dst, gold_tree(json.loads(AZ.read(_IDX["pspawn"][_src][0]).decode("utf-8-sig"))))
        TRAIL_FILES.append(P_PSPAWN % _dst)
    _sp["SpawnerId"] = _dst
put(P_PSYS % PS_TRAIL, _gt)
TRAIL_FILES.append(P_PSYS % PS_TRAIL)
PS_RING = PS_GLOW if QUICK_LOOK == "recolor" else "GreenOrbTrail"      # the heal orb's ring points
''')
# reference closure: the marker model is ours; the marker carries no hit / death particles
rep('''    if _d["Appearance"] != QMODEL and not az_has("model", _d["Appearance"]):''',
    '''    if _d["Appearance"] not in (QMODEL, MARKER) and not az_has("model", _d["Appearance"]):''')
rep('''    for _k in ("HitParticles", "DeathParticles"):
        _sid = _d[_k]["SystemId"]''', '''    for _k in ("HitParticles", "DeathParticles"):
        if _k not in _d and _d["Appearance"] == MARKER:
            continue
        _sid = _d[_k]["SystemId"]''')
rep('''for _p in QMODEL_JSON["Particles"]:''', '''for _p in [MARKER_JSON["Model"], MARKER_JSON["Texture"]]:
    if ("Common/" + _p) not in AZ_SET:
        _bad_ref.append("marker model: missing " + _p)
if MARKER_JSON["DefaultAttachments"] or MARKER_JSON["Particles"] or MARKER_JSON["Trails"]:
    _bad_ref.append("marker model: must carry no attachment / particles / trails (invisible)")
for _f in TRAIL_FILES:
    if _f.endswith(".particlesystem"):
        for _sp in json.loads(ASSETS[_f])["Spawners"]:
            if (P_PSPAWN % _sp["SpawnerId"]) not in ASSETS:
                _bad_ref.append("trail light: unknown spawner " + _sp["SpawnerId"])
    else:
        _tx = json.loads(ASSETS[_f]).get("Particle", {}).get("Texture")
        if _tx and ("Common/" + _tx) not in AZ_SET:
            _bad_ref.append("%s: texture %s" % (_f, _tx))
for _p in QMODEL_JSON["Particles"]:''')
# gate(): the staff hold spends exactly its Mana and nothing else (no Stamina)
rep('''        fail = INTS[sc["Failed"]]
        assert fail["Type"] == "Simple" and "StatModifiers" not in fail and "Next" not in fail''',
    '''        fail = INTS[sc["Failed"]]
        assert fail["Type"] == "Simple" and "StatModifiers" not in fail and "Next" not in fail
        for r in sc["Next"]["Interactions"]:          # 0.1.1: no chain spends Stamina any more (STAFF_STAMINA 0)
            for iid in r["Interactions"]:
                assert "Stamina" not in (INTS[iid].get("StatModifiers") or {}) and "StaminaRegenDelay" not in (INTS[iid].get("StatModifiers") or {}), iid''')
rep('''_scc = VSC["RunTime"] + max(0.0, 0.0, 0.0, RT_LAUNCH, 0.5)''', '''_scc = VSC["RunTime"] + max(0.0, RT_LAUNCH, 0.5)''')

# ================================================================================================ JVM: tokens + probes
rep('''ADRS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction"''', '''T.update({   # 0.1.1 traversals (VERIFIED by reflection / bytecode 2026-10-06; every member is probed below)
    "RSYS": "com.hypixel.hytale.component.system.RefSystem",
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "CAC": "com.hypixel.hytale.component.ComponentAccessor",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "HR": "com.hypixel.hytale.server.core.modules.entity.component.HeadRotation",
    "ES": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "NPC": "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DTH": "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "TP": "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport",
    "VEL": "com.hypixel.hytale.server.core.modules.physics.component.Velocity",
    "VCF": "com.hypixel.hytale.server.core.modules.splitvelocity.VelocityConfig",
    "CVT": "com.hypixel.hytale.protocol.ChangeVelocityType",
    "VTS": "com.hypixel.hytale.protocol.VelocityThresholdStyle",
    "TU": "com.hypixel.hytale.server.core.util.TargetUtil",
    "XFM": "com.hypixel.hytale.math.vector.Transform",
    "R3F": "com.hypixel.hytale.math.vector.Rotation3f",
    "PTU": "com.hypixel.hytale.server.core.universe.world.ParticleUtil",
    "SNU": "com.hypixel.hytale.server.core.universe.world.SoundUtil",
    "SEV": "com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent",
    "SCAT": "com.hypixel.hytale.protocol.SoundCategory",
    "ECC": "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent",
    "EFX": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect",
    "DENT": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource",
    "DCS": "com.hypixel.hytale.server.core.modules.entity.damage.DamageCause",
    "DSYS": "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems",
    "CHS": "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore",
    "BSC": "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection",
    "BTY": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
    "BMAT": "com.hypixel.hytale.protocol.BlockMaterial",
    "PHM": "com.hypixel.hytale.server.core.modules.physics.util.PhysicsMath",
    "INTG": "com.hypixel.hytale.server.core.modules.entity.component.Intangible",
    "BBX": "com.hypixel.hytale.server.core.modules.entity.component.BoundingBox",
    "BOX": "com.hypixel.hytale.math.shape.Box",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "UUIDC": "com.hypixel.hytale.server.core.entity.UUIDComponent",
    "V4": "org.joml.Vector4d",                                                                     # trav-fix: Damage.HIT_LOCATION's type
    "MCF": "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementConfig",        # trav-fix: the hop keeps a damaging fall
    "GPC": "com.hypixel.hytale.server.core.asset.type.gameplay.GameplayConfig",
    "PCF": "com.hypixel.hytale.server.core.asset.type.gameplay.PlayerConfig",
})
ADRS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction"''')
rep('''print("engine members probed: %d" % len(PROBED))''', '''# ---- 0.1.1: every engine member the traversals call (a game update that renames one stops the build; spec 5 T2)
_W = "java.util.List"
SIGS2 = [
    (T["RSYS"], "onEntityAdded", "void", [T["REF"], T["ADDR"], T["ST"], T["CB"]]), (T["RSYS"], "onEntityRemove", "void", [T["REF"], T["REMR"], T["ST"], T["CB"]]),
    (T["ETS"], "tick", "void", ["float", "int", T["ACH"], T["ST"], T["CB"]]), (T["ETS"], "isParallel", "boolean", ["int", "int"]),
    (T["QRY"], "and", "com.hypixel.hytale.component.query.AndQuery", ["com.hypixel.hytale.component.query.Query[]"]),
    (T["TC"], "getComponentType", T["CTYPE"], []), (T["TC"], "getPosition", T["VEC"], []), (T["TC"], "getRotation", T["R3F"], []),
    (T["HR"], "getComponentType", T["CTYPE"], []), (T["HR"], "getRotation", T["R3F"], []),
    (T["LPC"], "getCreatorUuid", "java.util.UUID", []), (T["LPC"], "getProjectile", T["PRJ"], []), (T["LPC"], "initialize", "boolean", []),
    (T["LPC"], "shoot", "void", [T["HOLD"], "java.util.UUID", "double", "double", "double", "float", "float"]),
    (T["LPC"], "assembleDefaultProjectile", T["HOLD"], [T["TRS"], S_, T["VEC"], T["R3F"]]),
    (T["HOLD"], "ensureComponent", "void", [T["CTYPE"]]), (T["INTG"], "getComponentType", T["CTYPE"], []),
    (T["CB"], "addEntity", T["REF"], [T["HOLD"], T["ADDR"]]), (T["CB"], "removeEntity", "void", [T["REF"], T["REMR"]]),
    (T["CB"], "getExternalData", O_, []), (T["CB"], "getResource", T["RSC"], [T["RTY"]]), (T["CB"], "invoke", "void", [T["REF"], T["EV"]]),
    (T["ST"], "getExternalData", O_, []), (T["ST"], "putComponent", "void", [T["REF"], T["CTYPE"], T["COMP"]]),
    (T["CAC"], "getComponent", T["COMP"], [T["REF"], T["CTYPE"]]), (T["REF"], "getStore", T["ST"], []),
    (T["ES"], "getWorld", T["WLD"], []), (T["ES"], "getRefFromUUID", T["REF"], ["java.util.UUID"]),
    (T["WLD"], "execute", "void", ["java.lang.Runnable"]), (T["WLD"], "getName", S_, []), (T["WLD"], "getChunkStore", T["CHS"], []),
    (T["WLD"], "getWorldConfig", "com.hypixel.hytale.server.core.universe.world.WorldConfig", []),
    ("com.hypixel.hytale.server.core.universe.world.WorldConfig", "isPvpEnabled", "boolean", []),
    (T["UNI"], "get", T["UNI"], []), (T["UNI"], "getPlayer", T["PR"], ["java.util.UUID"]),
    (T["PR"], "getComponentType", T["CTYPE"], []), (T["PR"], "getUuid", "java.util.UUID", []), (T["PR"], "getReference", T["REF"], []),
    (T["PR"], "isValid", "boolean", []), (T["PR"], "sendMessage", "void", [T["MSG"]]),
    (T["MSG"], "raw", T["MSG"], [S_]), (T["MSG"], "color", T["MSG"], [S_]),
    (T["NPC"], "getComponentType", T["CTYPE"], []), (T["DTH"], "getComponentType", T["CTYPE"], []),
    (T["ESM"], "getComponentType", T["CTYPE"], []), (T["ESM"], "get", T["ESV"], ["int"]), (T["ESM"], "addStatValue", "float", ["int", "float"]),
    (T["ESM"], "subtractStatValue", "float", ["int", "float"]), (T["ESV"], "get", "float", []), (T["ESV"], "getMax", "float", []),
    (T["DST"], "getStamina", "int", []), (T["DST"], "getHealth", "int", []),
    (T["TP"], "getComponentType", T["CTYPE"], []), (T["TP"], "createForPlayer", T["TP"], [T["WLD"], "org.joml.Vector3dc", "com.hypixel.hytale.math.vector.Rotation3fc"]),
    (T["TP"], "withoutVelocityReset", T["TP"], []), (T["TP"], "setHeadRotation", T["TP"], ["com.hypixel.hytale.math.vector.Rotation3fc"]),
    (T["VEL"], "getComponentType", T["CTYPE"], []), (T["VEL"], "addInstruction", "void", [T["VEC"], T["VCF"], T["CVT"]]),
    (T["VCF"], "<init>", "void", []), (T["VCF"], "setAirResistance", "void", ["float"]), (T["VCF"], "setAirResistanceMax", "void", ["float"]),
    (T["VCF"], "setGroundResistance", "void", ["float"]), (T["VCF"], "setGroundResistanceMax", "void", ["float"]),
    (T["VCF"], "setThreshold", "void", ["float"]), (T["VCF"], "setStyle", "void", [T["VTS"]]),
    (T["TU"], "getAllEntitiesInSphere", _W, [T["VEC"], "double", T["CAC"]]), (T["TU"], "getLook", T["XFM"], [T["REF"], T["CAC"]]),
    (T["XFM"], "getDirection", T["VEC"], []), (T["R3F"], "<init>", "void", ["float", "float", "float"]),
    (T["PHM"], "headingFromDirection", "float", ["double", "double"]), (T["PHM"], "pitchFromDirection", "float", ["double", "double", "double"]),
    (T["PHM"], "vectorFromAngles", T["VEC"], ["float", "float", T["VEC"]]),
    (T["PTU"], "spawnParticleEffect", "void", [S_, "org.joml.Vector3dc", T["CAC"]]),
    (T["SNU"], "playSoundEvent3d", "void", ["int", T["SCAT"], "double", "double", "double", T["CAC"]]),
    (T["SEV"], "getAssetMap", "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", []),
    (T["EFX"], "getAssetMap", "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", []),
    (T["ECC"], "getComponentType", T["CTYPE"], []), (T["ECC"], "addEffect", "boolean", [T["REF"], T["EFX"], T["CAC"]]),
    (T["DMG"], "<init>", "void", [T["DSRC"], T["DCS"], "float"]), (T["DMG"], "getInitialAmount", "float", []),
    (T["DMG"], "setCancelled", "void", ["boolean"]), (T["DMG"], "getIfPresentMetaObject", O_, ["com.hypixel.hytale.server.core.meta.MetaKey"]),
    (T["DPRJ"], "<init>", "void", [T["REF"], T["REF"]]), (T["DENT"], "<init>", "void", [T["REF"]]),
    (T["DSYS"], "executeDamage", "void", [T["REF"], T["CB"], T["DMG"]]), (T["DMOD"], "getInspectDamageGroup", T["SG"], []),
    (T["CHS"], "getChunkSectionReferenceAtBlock", T["REF"], ["int", "int", "int"]), (T["CHS"], "getStore", T["ST"], []),
    (T["BSC"], "getComponentType", T["CTYPE"], []), (T["BSC"], "get", "int", ["int", "int", "int"]),
    (T["BTY"], "getAssetMap", "com.hypixel.hytale.assetstore.map.BlockTypeAssetMap", []), (T["BTY"], "getMaterial", T["BMAT"], []),
    ("com.hypixel.hytale.assetstore.map.BlockTypeAssetMap", "getAsset", "com.hypixel.hytale.assetstore.map.JsonAssetWithMap", ["int"]),
    (T["BBX"], "getComponentType", T["CTYPE"], []), (T["BBX"], "getBoundingBox", T["BOX"], []), (T["BOX"], "width", "double", []),
    (T["BOX"], "depth", "double", []), (T["INVC"], "getItemInHand", T["IS"], [T["CAC"], T["REF"]]), (T["IS"], "getItemId", S_, []),
    (T["IS"], "isEmpty", "boolean", []), (T["SPP"], "getVelocity", T["VEC"], []),
    # trav-fix 2026-10-06: the hop reads the player's client velocity (what DamageSystems$FallDamagePlayers reads) and the world's MovementConfig
    (T["VEL"], "getClientVelocity", T["VEC"], []), (T["WLD"], "getGameplayConfig", T["GPC"], []), (T["GPC"], "getPlayerConfig", T["PCF"], []),
    (T["PCF"], "getMovementConfigIndex", "int", []), (T["MCF"], "getMinFallSpeedToEngageRoll", "float", []),
]
for _c, _m, _r, _a in SIGS2:
    probe_sig(_c, _m, _r, _a)
for _c, _f in ((T["DCS"], "PROJECTILE"), (T["DMG"], "HIT_LOCATION"), (T["CVT"], "Set"), (T["VTS"], "Exp"), (T["SCAT"], "SFX"),
               (T["BMAT"], "Solid"), (T["BTY"], "EMPTY_ID"), (T["REMR"], "REMOVE")):
    _fld = pool.get(_c).getField(_f)
    assert JMod.isPublic(_fld.getModifiers()) and JMod.isStatic(_fld.getModifiers()), "%s.%s is not public static" % (_c, _f)
    PROBED.append("%s.%s" % (_c.rsplit(".", 1)[1], _f))
assert int(pool.get(T["BTY"]).getField("EMPTY_ID").getConstantValue()) == 0, "BlockType.EMPTY_ID is not 0"
# trav-fix 2026-10-06 (critic): Damage.HIT_LOCATION is a MetaKey<org.joml.Vector4d> (read off HytaleServer.jar) - hitAt tests Vector4d first.
# Only DamageEntityInteraction (melee) puts it; a projectile hit carries none, so the burst / pierce use the target's position (spec fallback).
_hl_sig = str(pool.get(T["DMG"]).getField("HIT_LOCATION").getGenericSignature())
assert "Lorg/joml/Vector4d;" in _hl_sig, "Damage.HIT_LOCATION is not a MetaKey<Vector4d> any more: %s" % _hl_sig
for _f in ("x", "y", "z"):
    assert JMod.isPublic(pool.get(T["V4"]).getField(_f).getModifiers()), "org.joml.Vector4d.%s is not public" % _f
assert pool.get(T["MCF"]).getMethod("getAssetMap", "()Lcom/hypixel/hytale/assetstore/map/IndexedLookupTableAssetMap;") is not None
PROBED.append("Damage.HIT_LOCATION<Vector4d>")
print("engine members probed: %d" % len(PROBED))''')

# ================================================================================================ Java tables: the blink markers
rep('''W_IDS = WAND_IDS
W_ORB = [VAN_ORB] + [ID_ORB % m for m in NEW_METALS]''', '''W_IDS = WAND_IDS
S_BLINK = [ID_SBLINK % m for m in METALS]           # 0.1.1: the staff hold's marker (code 5000 + i)
W_ORB = [VAN_ORB] + [ID_ORB % m for m in NEW_METALS]''')
rep('''assert len(set(QUICK_IDS + ORB_IDS)) == len(QUICK_IDS) + len(ORB_IDS) == len(PRJS) and set(QUICK_IDS + ORB_IDS) == set(PRJS)''',
    '''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK)) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) == len(PRJS) and set(QUICK_IDS + ORB_IDS + S_BLINK) == set(PRJS)''')
rep('''          "public static final String[] S_QORB = %s;" % jarr(S_QORB),''', '''          "public static final String[] S_QORB = %s;" % jarr(S_QORB),
          "public static final String[] S_BLINK = %s;" % jarr(S_BLINK),''')
rep('''  for (int i = 0; i < S_ORB.length; i++) m.put(S_ORB[i], Integer.valueOf(4000 + i));
  PID = m;''', '''  for (int i = 0; i < S_ORB.length; i++) m.put(S_ORB[i], Integer.valueOf(4000 + i));
  for (int i = 0; i < S_BLINK.length; i++) m.put(S_BLINK[i], Integer.valueOf(5000 + i));
  PID = m;''')
# tune: the blink trail ticks follow the staff's tune; staff quick shots x (1 + quick.staffBonus %) (spec 1.1 Tap, LOCKED 2026-10-04)
rep('''M(dfs, r"""
public static float tuneFactor(String pid, boolean on, double[] wandPct, double[] staffPct, int quickPct) {''', '''M(dfs, r"""
public static float tuneFactor2(String pid, boolean on, double[] wandPct, double[] staffPct, int quickPct, int staffBonusPct) {
  if (!on) return 1.0f;
  int c = pidCode(pid);
  if (c < 0) return 1.0f;
  int i = c % 1000;
  double q = quickPct / (double) QUICK_SHARE_PCT;
  double f = 1.0;
  if (c >= 1000 && c < 2000) f = pctOf(wandPct, i) * q;
  else if (c >= 2000 && c < 3000) f = pctOf(wandPct, i);
  else if (c >= 3000 && c < 4000) f = pctOf(staffPct, i) * q * (1.0 + (staffBonusPct > 0 ? staffBonusPct : 0) / 100.0);
  else if (c >= 4000 && c < 5000) f = pctOf(staffPct, i);
  else if (c >= 5000 && c < 6000) f = pctOf(staffPct, i);
  return (float) f;
}""")
M(dfs, r"""
public static float tuneFactor(String pid, boolean on, double[] wandPct, double[] staffPct, int quickPct) {''')

# ================================================================================================ settings: fields, file text, rows (spec 1.4 + 8)
TD = None   # filled below from the generated script's TRAV dict (one source of truth)
exec_ns = {}
exec(re.search(r"(TRAV = dict\(.*?staffBonus=\d+\)\n)", s, re.S).group(1), exec_ns)
TD = exec_ns["TRAV"]


def bt(v):
    return "true" if v else "false"


def dn(v):
    v = float(v)
    return str(int(v)) if v == int(v) else repr(v)


CFG_NEW = [   # (key, label, cat, type, default text, min, max, opts, unit, flags, help, field, java type, java default, file comment)
    ("part.trav", "Magic traversals", "trav", "bool", bt(TD["part"]), "", "", "", "", "live,part,danger",
     "Off = staff holds fire the old orb, wands only shoot; no blink / hop / burst / heal orb / pierce.", "PART_TRAV", "boolean", bt(TD["part"]),
     "Off = staff holds fire the 0.1 charged orb, wands only shoot (no blink, hop, burst, heal orb or pierce)."),
    ("trav.staminaPercent", "Traversal Stamina (% of its Mana)", "trav", "int", str(TD["stamPct"]), "0", "200", "step=5", "%", "live",
     "Every traversal costs its Mana AND this % as Stamina. 50 = Skyy's 2 Mana : 1 Stamina.", "STAMINA_PCT", "int", str(TD["stamPct"]),
     "Every traversal costs Mana AND Stamina: Stamina = this % of its Mana (50 = 2 Mana : 1 Stamina). Too little Stamina = no traversal."),
    ("trav.staminaCap", "Most Stamina per traversal", "trav", "int", str(TD["stamCap"]), "0", "100", "", "", "live",
     "0 = no cap. Vanilla max Stamina is 10, so a higher cost could never be paid.", "STAMINA_CAP", "int", str(TD["stamCap"]),
     "At most this much Stamina per traversal (0 = no cap; vanilla max Stamina is 10)."),
    ("trav.players", "Hit players (world PvP on)", "trav", "bool", bt(TD["players"]), "", "", "", "", "live",
     "Trail and burst hit other players only where PvP is on; never party members.", "TRAV_PLAYERS", "boolean", bt(TD["players"]),
     "Trail and burst hit other players only where the world's PvP is on - never party members."),
    ("trav.maxLive", "Most live trails + orbs per world", "trav", "int", str(TD["maxLive"]), "8", "256", "", "", "live",
     "Oldest dropped first.", "TRAV_MAXLIVE", "int", str(TD["maxLive"]), "Most live trails + heal orbs per world (the oldest is dropped)."),
    ("trav.fx", "Traversal particles and sounds", "trav", "bool", bt(TD["fx"]), "", "", "", "", "live",
     "Off = no light, burst or heal orb particles and no traversal sounds.", "TRAV_FX", "boolean", bt(TD["fx"]), "Traversal particles and sounds."),
    ("staff.mode", "Staff hold", "blink", "choice", TD["mode"], "", "", "blink|Blink,orb|Charged orb", "", "live",
     "blink = teleport + light trail; orb = the 0.1 charged orb.", "STAFF_MODE", "String", TD["mode"],
     "Staff hold: blink (teleport + light trail) or orb (the 0.1 charged orb)."),
    ("blink.distance", "Blink distance (blocks)", "blink", "int", str(TD["dist"]), "3", "20", "", "blocks", "live",
     "Server-wide until the class trees add upgrades and the own setting.", "BLINK_DIST", "int", str(TD["dist"]), "Blink distance (blocks)."),
    ("blink.floorCheck", "Blink needs ground within (blocks)", "blink", "int", str(TD["floor"]), "0", "64", "", "blocks", "live",
     "0 = off. Shortens a blink over open void to the last spot with ground below.", "BLINK_FLOOR", "int", str(TD["floor"]),
     "A blink lands only where ground lies within this many blocks below (0 = off)."),
    ("blink.keepFall", "Blink keeps falling speed", "blink", "bool", bt(TD["keepFall"]), "", "", "", "", "live",
     "On = no fall-damage escape. Off = the teleport stops your fall.", "BLINK_KEEPFALL", "boolean", bt(TD["keepFall"]),
     "On = the blink keeps your falling speed (no fall-damage escape)."),
    ("blink.trailOn", "Light trail", "blink", "bool", bt(TD["trailOn"]), "", "", "", "", "live", "Off = blink only.", "TRAIL_ON", "boolean",
     bt(TD["trailOn"]), "The light trail along the blink."),
    ("blink.trailWidth", "Trail width (blocks)", "blink", "dec", dn(TD["trailWidth"]), "0.5", "4", "", "blocks", "live",
     "Enemies inside this width of the line take the trail damage.", "TRAIL_WIDTH", "double", dn(TD["trailWidth"]), "Trail width (blocks)."),
    ("blink.trailSeconds", "Trail lasts (s)", "blink", "dec", dn(TD["trailSeconds"]), "0.5", "8", "", "s", "live",
     "How long the light line hangs.", "TRAIL_SECONDS", "double", dn(TD["trailSeconds"]), "Trail lasts (seconds)."),
    ("blink.trailPercent", "Trail damage (% of charged per second)", "blink", "int", str(TD["trailPct"]), "0", "200", "step=5", "%", "live",
     "Per enemy standing in it.", "TRAIL_PCT", "int", str(TD["trailPct"]), "Trail damage per second, % of the staff's charged damage."),
    ("blink.tick", "Trail tick (s)", "blink", "dec", dn(TD["tick"]), "0.25", "1", "", "s", "live",
     "Damage every this often.", "BLINK_TICK", "double", dn(TD["tick"]), "Trail damage every this many seconds."),
    ("blink.cooldown", "Blink cooldown (s)", "blink", "dec", dn(TD["cd"]), "0", "10", "", "s", "live",
     "0 = none. A blink inside the cooldown does nothing and costs nothing.", "BLINK_CD", "double", dn(TD["cd"]),
     "Blink cooldown in seconds (0 = none); a blink inside it does nothing and costs nothing."),
    ("hop.force", "Wand hop force", "hop", "dec", dn(TD["hopForce"]), "0", "25", "", "", "live",
     "0 = no hop. 13 = the vanilla dagger dash.", "HOP_FORCE", "double", dn(TD["hopForce"]), "Wand hop force (13 = the vanilla dagger dash, 0 = no hop)."),
    ("hop.groundCheck", "Hop needs ground within (blocks)", "hop", "int", str(TD["hopGround"]), "0", "32", "", "blocks", "live",
     "0 = off. No ground behind you = half the hop.", "HOP_GROUND", "int", str(TD["hopGround"]),
     "No ground within this many blocks under the spot 3 blocks behind you = half the hop (0 = off)."),
    ("burst.radius", "Burst radius (blocks)", "hop", "dec", dn(TD["burstR"]), "1", "12", "", "blocks", "live",
     "Enemies around the orb's end take the burst.", "BURST_RADIUS", "double", dn(TD["burstR"]), "Burst radius (blocks)."),
    ("burst.percent", "Burst damage to others (%)", "hop", "int", str(TD["burstPct"]), "0", "100", "step=5", "%", "live",
     "% of the orb's damage; the enemy hit directly takes the full shot.", "BURST_PCT", "int", str(TD["burstPct"]),
     "Burst damage to the OTHER enemies, % of the orb's damage (the enemy hit directly takes the full shot)."),
    ("orb.radius", "Heal orb radius (blocks)", "hop", "dec", dn(TD["orbR"]), "1", "16", "", "blocks", "live",
     "Players inside heal every tick.", "ORB_RADIUS", "double", dn(TD["orbR"]), "Heal orb radius (blocks)."),
    ("orb.seconds", "Heal orb lasts (s)", "hop", "dec", dn(TD["orbSec"]), "0.5", "8", "", "s", "live",
     "How long the glow stays.", "ORB_SECONDS", "double", dn(TD["orbSec"]), "Heal orb lasts (seconds)."),
    ("orb.healPercent", "Heal orb (% of burst damage per second)", "hop", "int", str(TD["orbPct"]), "0", "100", "step=5", "%", "live",
     "Each ally inside, every second.", "ORB_HEAL_PCT", "int", str(TD["orbPct"]), "Heal orb: % of the burst's damage per second."),
    ("orb.tick", "Heal orb tick (s)", "hop", "dec", dn(TD["orbTick"]), "0.25", "2", "", "s", "live",
     "Heals every this often.", "ORB_TICK", "double", dn(TD["orbTick"]), "Heal orb heals every this many seconds."),
    ("orb.partyPercent", "Heal orb share - you + party (%)", "hop", "int", str(TD["partyPct"]), "0", "200", "step=5", "%", "live",
     "The Priest and party members get this % of the orb's heal (the base SkyyClasses splits).", "ORB_PARTY_PCT", "int", str(TD["partyPct"]),
     "The Priest + party members get this % of the heal orb's heal."),
    ("orb.othersPercent", "Heal orb others % (no SkyyClasses)", "hop", "int", str(TD["othersPct"]), "0", "200", "step=5", "%", "live,adv",
     "Without SkyyClasses only (with it: Classes priestHeal.othersPercent). 0 = party only.", "ORB_OTHERS_PCT", "int", str(TD["othersPct"]),
     "Every other non-hostile player gets this % (0 = party only) - only without SkyyClasses; with it its priestHeal.othersPercent decides."),
    ("pierce.max", "Wand quick shot pierces (0 = no cap)", "quick", "int", str(TD["pierce"]), "0", "50", "", "", "live",
     "0 = no cap (Skyy): only the range limits it.", "PIERCE_MAX", "int", str(TD["pierce"]),
     "Wand quick shots pierce this many enemies (0 = no cap: only the range limits it)."),
    ("quick.range.wand", "Wand quick shot range (blocks)", "quick", "int", str(TD["rangeW"]), "4", "64", "", "blocks", "live",
     "The quick orb vanishes this far from where it was cast.", "RANGE_WAND", "int", str(TD["rangeW"]), "Wand quick shot range (blocks)."),
    ("quick.range.staff", "Staff quick shot range (blocks)", "quick", "int", str(TD["rangeS"]), "4", "64", "", "blocks", "live",
     "The quick orb vanishes this far from where it was cast.", "RANGE_STAFF", "int", str(TD["rangeS"]), "Staff quick shot range (blocks)."),
    ("quick.staffBonus", "Staff quick shot bonus (%)", "quick", "int", str(TD["staffBonus"]), "0", "100", "step=5", "%", "live",
     "Staff taps hit this much harder per Mana than wand taps.", "STAFF_BONUS", "int", str(TD["staffBonus"]),
     "Staff quick shots hit this % harder (per Mana) than wand quick shots."),
]
for _r in CFG_NEW:
    assert len(_r[1]) <= 40 and len(_r[10]) <= 100, (_r[0], len(_r[1]), len(_r[10]))
    assert "%" not in _r[13]
import pprint
_cfgnew_txt = ("# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV): (key, label, cat, type, default, min, max, opts,"
               " unit, flags, help, ArmoryCfg field, Java type, Java default, config.properties comment)" + LF + "CFG_NEW = "
               + pprint.pformat(CFG_NEW, width=150) + LF + LF + "# ================================================================= the ONE cost table")
rep("# ================================================================= the ONE cost table", _cfgnew_txt)
rep('''          "public static volatile String LOADED = \\"\\";",''', '''          "public static volatile String LOADED = \\"\\";",
          "public static volatile String TRAV_TEXT = \\"\\";",''')
rep('''    F(cfg, f)

# ================================================================= the config kit''', '''    F(cfg, f)
for _r in CFG_NEW:            # 0.1.1 traversal settings (field: rows of the kit; ArmoryCfg.apply reads them the same way)
    F(cfg, "public static volatile %s %s = %s;" % (_r[12], _r[11], ('"%s"' % _r[13]) if _r[12] == "String" else (repr(float(_r[13])) if _r[12] == "double" else _r[13])))

# ================================================================= the config kit''')
_lines = ['    "",', '    "# ---- magic traversals (the staff / wand HOLD; research/Magic-Traversal-Spec.md + Skyy\'s answers 2026-10-05)",']
for _r in CFG_NEW:
    _lines.append('    "# %s",' % _r[14].replace('"', "'"))
    _lines.append('    "%s=%s",' % (_r[0], _r[4]))
rep('''    "",
    "# ---- Mana check (server log)",''', "\n".join(_lines) + '''
    "",
    "# ---- Mana check (server log)",''')
rep('''CFG_CATS = [("damage", "Damage"), ("quick", "Quick shot"), ("check", "Mana check"), ("wands", "Wands (fixed)"), ("staffs", "Staffs (fixed)")]''',
    '''CFG_CATS = [("trav", "Traversal"), ("blink", "Staff blink"), ("hop", "Wand hop + burst"), ("damage", "Damage"), ("quick", "Quick shot"),
            ("check", "Mana check"), ("wands", "Wands (fixed)"), ("staffs", "Staffs (fixed)")]''')
rep('''FIXED_VAL = dict((f[0], f[3]) for f in FIXED)''', '''FIXED.append(("staff.stamina", "Staff cast Stamina (fixed in the jar)", "trav",
              "%d - quick casts and orb mode spend Mana only; the blink pays Stamina (row above)" % STAFF_STAMINA,
              "Was 5 + a 1.5 s regen pause in 0.1. Build constant STAFF_STAMINA."))
FIXED.append(("hop.mode", "Hop mode (fixed in the jar)", "hop", HOP_MODE,
              "server = the Java push (live force, ground check); asset = the client dash."))
FIXED_VAL = dict((f[0], f[3]) for f in FIXED)''')
rep('''    ("quick.life", "Quick shot reach (seconds)", "quick", "int", str(QUICK_LIFE_DEF), "1", str(VANILLA_LIFE_MS // 1000), "", "s", "new",''',
    '''    ("quick.life", "Quick shot reach (seconds)", "quick", "int", str(QUICK_LIFE_DEF), "1", str(VANILLA_LIFE_MS // 1000), "", "s", "new,adv",''')
rep('''] + [(k, lab, cat, "text", val, "", "", "", "", "ro", hlp, "custom:ArmoryHooks") for k, lab, cat, val, hlp in FIXED]''',
    '''] + [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], "field:ArmoryCfg." + r[11]) for r in CFG_NEW] + [
    (k, lab, cat, "text", val, "", "", "", "", "ro", hlp, "custom:ArmoryHooks") for k, lab, cat, val, hlp in FIXED]''')
rep('''    if _r[3] in ("bool", "int", "dec") and "ro" not in _r[9]:''', '''    if _r[3] in ("bool", "int", "dec", "choice") and "ro" not in _r[9]:''')
# ArmoryCfg.apply reads the new keys (clamped like the kit validates) + the live summary for armory:trav
_apply = []
for _r in CFG_NEW:
    k, typ, fld, jd = _r[0], _r[3], _r[11], _r[13]
    if typ == "bool":
        _apply.append('  %s = bool(c.getProperty("%s"), %s);' % (fld, k, jd))
    elif typ == "int":
        _apply.append('  %s = intOf(c.getProperty("%s"), %s, %s, %s);' % (fld, k, jd, _r[5], _r[6]))
    elif typ == "dec":
        _apply.append('  %s = dec(c.getProperty("%s"), %s, %s, %s);' % (fld, k, dn(jd) if "." in jd else jd + ".0", _r[5] if "." in _r[5] else _r[5] + ".0",
                                                                    _r[6] if "." in _r[6] else _r[6] + ".0"))
    elif typ == "choice":
        _apply.append('  %s = "orb".equalsIgnoreCase(String.valueOf(c.getProperty("%s")).trim()) ? "orb" : "blink";' % (fld, k))
_apply.append("  TRAV_TEXT = travText();")
_apply.append('  try { @PKG@.ArmoryDefs.bridge().put("armory:trav", TRAV_TEXT); } catch (Throwable tb) { }')
_ap = "\n".join(_apply) + "\n"
assert "%" not in _ap
rep('''  CHECK_SHARE = intOf(c.getProperty("check.share"), %d, 10, 100);
  StringBuilder sb = new StringBuilder();''', '''  CHECK_SHARE = intOf(c.getProperty("check.share"), %d, 10, 100);
''' + _ap + '''  StringBuilder sb = new StringBuilder();''')
rep('''+ ", Mana check " + (CHECK_ON ? "on (" + CHECK_SHARE + "%%)" : "off");''',
    '''+ ", Mana check " + (CHECK_ON ? "on (" + CHECK_SHARE + "%%)" : "off") + "; " + TRAV_TEXT;''')
rep('''M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''', '''M(cfg, r"""
public static String travText() {
  return "traversals " + (PART_TRAV ? "on" : "OFF") + " (Stamina " + STAMINA_PCT + "% of the Mana, cap " + STAMINA_CAP + ") - staff hold "
    + STAFF_MODE + (STAFF_MODE.equals("orb") ? "" : " " + BLINK_DIST + " blocks (ground " + BLINK_FLOOR + ", keep fall " + (BLINK_KEEPFALL ? "on" : "off")
    + ", trail " + (TRAIL_ON ? TRAIL_WIDTH + " wide " + TRAIL_SECONDS + " s " + TRAIL_PCT + "%/s every " + BLINK_TICK + " s" : "off")
    + (BLINK_CD > 0.0 ? ", cooldown " + BLINK_CD + " s" : "") + ")") + " - wand hold hop " + HOP_FORCE + " (ground " + HOP_GROUND
    + "), burst " + BURST_RADIUS + " blocks " + BURST_PCT + "%, heal orb " + ORB_RADIUS + " blocks " + ORB_SECONDS + " s " + ORB_HEAL_PCT
    + "%/s every " + ORB_TICK + " s (party " + ORB_PARTY_PCT + "%, others " + ORB_OTHERS_PCT + "%) - quick shots: wand " + RANGE_WAND
    + " blocks, pierce " + (PIERCE_MAX > 0 ? String.valueOf(PIERCE_MAX) : "no cap") + "; staff " + RANGE_STAFF + " blocks +" + STAFF_BONUS
    + "% - players " + (TRAV_PLAYERS ? "where PvP is on" : "never") + ", at most " + TRAV_MAXLIVE + " live effects per world";
}""")
M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''')

# ================================================================================================ new classes (created with the others)
rep('''pl = pool.makeClass(PKG + ".SkyyArmoryPlugin", pool.get(T["JP"]))
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info]''', '''pl = pool.makeClass(PKG + ".SkyyArmoryPlugin", pool.get(T["JP"]))
# 0.1.1 traversals (spec 3.1.3): pure maths + the grid seam (bare-JVM tested), the per-world state, the engine glue, three systems
tgrid = pool.makeInterface(PKG + ".TravGrid")
tmath = pool.makeClass(PKG + ".TravMath")
wgrid = pool.makeClass(PKG + ".WorldGrid")
tshot = pool.makeClass(PKG + ".TravShot")
tfx = pool.makeClass(PKG + ".TravFx")
tworld = pool.makeClass(PKG + ".TravWorld")
tjob = pool.makeClass(PKG + ".TravJob")
theal = pool.makeClass(PKG + ".TravHeal")
trav = pool.makeClass(PKG + ".ArmoryTrav")
travsys = pool.makeClass(PKG + ".ArmoryTravSys", pool.get(T["RSYS"]))
hitsys = pool.makeClass(PKG + ".ArmoryHitSys", pool.get(T["DES"]))
ttick = pool.makeClass(PKG + ".TravTick", pool.get(T["ETS"]))
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick]''')

JAVA_BLOCK = r'''# ---------------------------------------------------------------- 0.1.1 TRAVERSALS (research/Magic-Traversal-Spec.md 2 + 3.1.3; section 8 wins)
# TravGrid: the block seam of the blink / hop scans - 0 = passable, 1 = solid, -1 = unknown (unloaded section, outside the world: a wall)
M(tgrid, "public abstract int at(int x, int y, int z);")

# ---- TravMath: PURE maths (no engine type; the bare-JVM harness runs it on a fake grid)
F(tmath, "public static final double HALF = 0.299;")          # half the player's body width (0.6) - a landing never overlaps a block
F(tmath, "public static final double STEP = 0.5;")            # the scan step (a 1-block wall can never be skipped)
F(tmath, "public static final double FINE = 0.05;")           # the refine step back from a blocked step
# -1 = the body box (0.6 x 0.6 at feet, waist and head height) touches a non-passable / unknown block, 0 = free
M(tmath, r"""
public static int body(@PKG@.TravGrid g, double x, double y, double z) {
  int ya = (int) Math.floor(y + 0.05);
  int yb = (int) Math.floor(y + 0.95);
  int yc = (int) Math.floor(y + 1.75);
  int x0 = (int) Math.floor(x - HALF);
  int x1 = (int) Math.floor(x + HALF);
  int z0 = (int) Math.floor(z - HALF);
  int z1 = (int) Math.floor(z + HALF);
  for (int bx = x0; bx <= x1; bx++) {
    for (int bz = z0; bz <= z1; bz++) {
      if (g.at(bx, ya, bz) != 0) return -1;
      if (yb != ya && g.at(bx, yb, bz) != 0) return -1;
      if (yc != yb && g.at(bx, yc, bz) != 0) return -1;
    }
  }
  return 0;
}""")
# true = a solid block within depth blocks under the feet column (depth 0 = no check); an unknown block below ends the look (no ground)
M(tmath, r"""
public static boolean ground(@PKG@.TravGrid g, double x, double y, double z, int depth) {
  if (depth <= 0) return true;
  int bx = (int) Math.floor(x);
  int bz = (int) Math.floor(z);
  int by = (int) Math.floor(y + 0.05);
  for (int i = 1; i <= depth; i++) {
    int c = g.at(bx, by - i, bz);
    if (c == 1) return true;
    if (c < 0) return false;
  }
  return false;
}""")
# 1 = a landing spot (body free + ground below), 0 = body free but no ground (void: the scan goes on, never lands there), -1 = blocked
M(tmath, r"""
public static int spot(@PKG@.TravGrid g, double x, double y, double z, int floor) {
  if (body(g, x, y, z) < 0) return -1;
  return ground(g, x, y, z, floor) ? 1 : 0;
}""")
# THE blink scan (spec 1.1 + 4): from the feet along the unit look direction, 0.5-block steps up to maxD; the farthest landing spot;
# the first blocked / unknown step ends it - refined back in 0.05 steps to the farthest landing spot before that block; nothing beyond
# 1 block = 0 (no blink, costs nothing)
M(tmath, r"""
public static double scan(@PKG@.TravGrid g, double sx, double sy, double sz, double dx0, double dy0, double dz0, double maxD, int floor) {
  if (g == null || !(maxD > 0.0)) return 0.0;
  double len = Math.sqrt(dx0 * dx0 + dy0 * dy0 + dz0 * dz0);
  if (!(len > 1.0E-6) || Double.isNaN(len) || Double.isInfinite(len)) return 0.0;
  double dx = dx0 / len;
  double dy = dy0 / len;
  double dz = dz0 / len;
  double best = 0.0;
  int n = (int) Math.floor(maxD / STEP + 1.0E-9);
  boolean blocked = false;
  for (int k = 1; k <= n && !blocked; k++) {
    double t = k * STEP;
    int c = spot(g, sx + dx * t, sy + dy * t, sz + dz * t, floor);
    if (c < 0) {
      blocked = true;
      for (int j = 1; j < 10; j++) {
        double u = t - j * FINE;
        if (u <= best + 1.0E-9) break;
        if (spot(g, sx + dx * u, sy + dy * u, sz + dz * u, floor) == 1) { best = u; break; }
      }
    } else if (c == 1) {
      best = t;
    }
  }
  if (!blocked && maxD > n * STEP + 1.0E-9 && spot(g, sx + dx * maxD, sy + dy * maxD, sz + dz * maxD, floor) == 1) best = maxD;
  return best >= 1.0 ? best : 0.0;
}""")
# distance of point p to the segment a-b (the trail capsule)
M(tmath, r"""
public static double segDist(double px, double py, double pz, double ax, double ay, double az, double bx, double by, double bz) {
  double vx = bx - ax;
  double vy = by - ay;
  double vz = bz - az;
  double vv = vx * vx + vy * vy + vz * vz;
  double t = 0.0;
  if (vv > 1.0E-9) t = ((px - ax) * vx + (py - ay) * vy + (pz - az) * vz) / vv;
  if (t < 0.0) t = 0.0;
  if (t > 1.0) t = 1.0;
  double cx = ax + vx * t - px;
  double cy = ay + vy * t - py;
  double cz = az + vz * t - pz;
  return Math.sqrt(cx * cx + cy * cy + cz * cz);
}""")
# the hop push: OPPOSITE to the look (look down = straight up), force (halved when there is no ground behind)
M(tmath, r"""
public static double[] hopVector(double dx0, double dy0, double dz0, double force, boolean half) {
  double len = Math.sqrt(dx0 * dx0 + dy0 * dy0 + dz0 * dz0);
  if (!(len > 1.0E-6) || !(force > 0.0)) return new double[] { 0.0, 0.0, 0.0 };
  double f = half ? force * 0.5 : force;
  return new double[] { -dx0 / len * f, -dy0 / len * f, -dz0 / len * f };
}""")
# where the hop's ground check looks: 3 blocks behind (horizontal, opposite to the look); straight up / down = under the feet
M(tmath, r"""
public static double[] hopProbe(double dx, double dz) {
  double hx = -dx;
  double hz = -dz;
  double l = Math.sqrt(hx * hx + hz * hz);
  if (!(l > 0.2)) return new double[] { 0.0, 0.0 };
  return new double[] { hx / l * 3.0, hz / l * 3.0 };
}""")
# FIX ROUND (trav-fix 2026-10-06, critic: pierce through thin walls): true = every 0.25-block point of the segment a-b (b included) sits
# in a passable block (0); a solid / unknown block anywhere on it = false. No grid = false (never spawn blind).
M(tmath, r"""
public static boolean clear(@PKG@.TravGrid g, double ax, double ay, double az, double bx, double by, double bz) {
  if (g == null) return false;
  double dx = bx - ax;
  double dy = by - ay;
  double dz = bz - az;
  double l = Math.sqrt(dx * dx + dy * dy + dz * dz);
  if (Double.isNaN(l) || Double.isInfinite(l)) return false;
  int n = (int) Math.ceil(l / 0.25);
  if (n < 1) n = 1;
  for (int k = 0; k <= n; k++) {
    double u = (double) k / (double) n;
    if (g.at((int) Math.floor(ax + dx * u), (int) Math.floor(ay + dy * u), (int) Math.floor(az + dz * u)) != 0) return false;
  }
  return true;
}""")
# FIX ROUND (trav-fix, critic: the hop erased a damaging fall; Double-Jump-Spec rule 7): the hop's vertical speed. Falling faster than
# limit (the world's MinFallSpeedToEngageRoll, vanilla 21 = a landing that hurts) keeps the fall: min(hop vy, current vy).
M(tmath, r"""
public static double hopVy(double hopVy, double curVy, double limit) {
  if (Double.isNaN(curVy) || !(limit > 0.0)) return hopVy;
  if (curVy < -limit && curVy < hopVy) return curVy;
  return hopVy;
}""")
# damage / heal of ONE tick: base x pct % per second x the tick length
M(tmath, r"""
public static double perTick(double base, double pct, long stepMs) {
  if (!(base > 0.0) || !(pct > 0.0) || stepMs <= 0L) return 0.0;
  return base * pct / 100.0 * (double) stepMs / 1000.0;
}""")
# Skyy 2026-10-05: every traversal costs Mana AND Stamina; magical = 2 Mana : 1 Stamina (pct 50), at most cap (0 = no cap)
M(tmath, r"""
public static double staminaCost(double mana, int pct, int cap) {
  if (!(mana > 0.0) || pct <= 0) return 0.0;
  double c = mana * (double) pct / 100.0;
  if (cap > 0 && c > (double) cap) c = (double) cap;
  return c;
}""")
# who a player is to the caster: 2 = the caster or an ally (party), 1 = a player who is not an enemy, 0 = an enemy (PvP on + trav.players)
M(tmath, r"""
public static int who(boolean self, boolean ally, boolean pvp, boolean players) {
  if (self || ally) return 2;
  if (pvp && players) return 0;
  return 1;
}""")
# the heal orb's share (Skyy: "heals everyone, but party more"): allies partyPct %, other non-hostile players othersPct %, enemies 0
M(tmath, r"""
public static double share(double hp, int who, int partyPct, int othersPct) {
  if (!(hp > 0.0)) return 0.0;
  if (who == 2) return partyPct > 0 ? hp * (double) partyPct / 100.0 : 0.0;
  if (who == 1) return othersPct > 0 ? hp * (double) othersPct / 100.0 : 0.0;
  return 0.0;
}""")
M(tmath, r"""
public static String fmt(double v) {
  if (Double.isNaN(v) || Double.isInfinite(v)) return "0";
  double r = Math.floor(v * 10.0 + 0.5) / 10.0;
  if (Math.abs(r - Math.floor(r)) < 1.0E-9) return String.valueOf((long) Math.floor(r));
  return String.valueOf(r);
}""")
# the tooltip words (armory:fn:info [8]; SkyyGear 0.2.4 adds the line under the charged shot) - no , : ; { } " ' _ (UI text rule)
M(tmath, r"""
public static String travWords(boolean staff, boolean ours, boolean on, String mode, int dist, double burstR, double orbR, double stamina) {
  if (!on || !ours) return "";
  String st = stamina > 0.0 ? " - " + fmt(stamina) + " Stamina" : "";
  if (staff) {
    if ("orb".equals(mode)) return "";
    return "Hold - blink " + dist + " blocks + light trail" + st;
  }
  return "Hold - hop back + burst " + fmt(burstR) + " blocks + heal orb " + fmt(orbR) + " blocks" + st;
}""")
# [9] appended to the quick shot line: wand "pierces - 16 blocks", staff "24 blocks" ("" = no quick shot)
M(tmath, r"""
public static String quickWords(boolean staff, boolean has, boolean on, int pierceMax, int range) {
  if (!has) return "";
  if (staff || !on) return range + " blocks";
  return (pierceMax > 0 ? "pierces " + pierceMax : "pierces") + " - " + range + " blocks";
}""")

# ---- WorldGrid: the engine's blocks (world thread; never loads a chunk - the SkyySkills blockIdAt read path, spec 2.2)
wgrid.addInterface(tgrid)
F(wgrid, "public @CHS@ cs;")
F(wgrid, "public @ST@ cst;")
F(wgrid, "public static volatile String FAIL = null;")
C(wgrid, r"""
public WorldGrid(@WLD@ w) {
  this.cs = null;
  this.cst = null;
  try {
    if (w != null) this.cs = w.getChunkStore();
    if (this.cs != null) this.cst = this.cs.getStore();
  } catch (Throwable t) { this.cs = null; }
}""")
# passable = the empty block or a block whose material is not Solid (plants, fluids, air-like); unknown block type = solid (safe)
M(wgrid, r"""
public int at(int x, int y, int z) {
  try {
    if (this.cs == null || this.cst == null) return -1;
    @REF@ sr = this.cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (sr == null || !sr.isValid()) return -1;
    @BSC@ sec = (@BSC@) this.cst.getComponent(sr, @BSC@.getComponentType());
    if (sec == null) return -1;
    int id = sec.get(x, y, z);
    if (id == @BTY@.EMPTY_ID) return 0;
    Object o = @BTY@.getAssetMap().getAsset(id);
    if (!(o instanceof @BTY@)) return 1;
    return ((@BTY@) o).getMaterial() == @BMAT@.Solid ? 1 : 0;
  } catch (Throwable t) {
    if (FAIL == null) { FAIL = String.valueOf(t); @PKG@.ArmoryLog.warnOnce("grid", "block read failed (" + t + ") - blinks treat it as a wall"); }
    return -1;
  }
}""")

# ---- TravShot: one tracked orb (quick: range + pierce chain; wand charged: burst once)
for f in ("public double sx;", "public double sy;", "public double sz;", "public double range;", "public java.util.HashSet hits;",
          "public int count;", "public int code;", "public java.util.UUID caster;", "public String pid;"):
    F(tshot, f)
C(tshot, r"""
public TravShot(double sx, double sy, double sz, double range, int code, java.util.UUID caster, String pid) {
  this.sx = sx;
  this.sy = sy;
  this.sz = sz;
  this.range = range;
  this.code = code;
  this.caster = caster;
  this.pid = pid;
  this.hits = new java.util.HashSet();
  this.count = 0;
}""")
# the pierce continuation: the same start (the range counts from the first launch), the same hit set, the hits so far
M(tshot, r"""
public @PKG@.TravShot next() {
  @PKG@.TravShot n = new @PKG@.TravShot(this.sx, this.sy, this.sz, this.range, this.code, this.caster, this.pid);
  n.hits = this.hits;
  n.count = this.count;
  return n;
}""")

# ---- TravFx: one live effect (kind 1 = blink trail, 2 = heal orb, 0 = a marker to remove)
for f in ("public int kind;", "public double ax;", "public double ay;", "public double az;", "public double bx;", "public double by;",
          "public double bz;", "public double r;", "public long until;", "public long next;", "public long step;", "public long fxNext;",
          "public double amount;", "public java.util.UUID caster;", "public @REF@ marker;", "public int code;", "public int ticks;"):
    F(tfx, f)
C(tfx, r"""
public TravFx(int kind, double ax, double ay, double az, double bx, double by, double bz, double r, long until, long next, long step,
              double amount, java.util.UUID caster, @REF@ marker, int code) {
  this.kind = kind;
  this.ax = ax;
  this.ay = ay;
  this.az = az;
  this.bx = bx;
  this.by = by;
  this.bz = bz;
  this.r = r;
  this.until = until;
  this.next = next;
  this.step = step;
  this.amount = amount;
  this.caster = caster;
  this.marker = marker;
  this.code = code;
  this.fxNext = 0L;
  this.ticks = 0;
}""")

# ---- TravWorld: the per-world state (key = the world's entity Store; every list is touched on that world's thread only)
F(tworld, "public static final java.util.concurrent.ConcurrentHashMap ALL = new java.util.concurrent.ConcurrentHashMap();")
for f in ("public java.util.ArrayList fx;", "public java.util.HashMap quick;", "public java.util.HashMap orbs;", "public java.util.HashMap pend;",
          "public long lastNs;"):
    F(tworld, f)
C(tworld, r"""
public TravWorld() {
  this.fx = new java.util.ArrayList();
  this.quick = new java.util.HashMap();
  this.orbs = new java.util.HashMap();
  this.pend = new java.util.HashMap();
  this.lastNs = 0L;
}""")
M(tworld, "public static @PKG@.TravWorld of(Object st) { return st == null ? null : (@PKG@.TravWorld) ALL.get(st); }")
M(tworld, r"""
public static @PKG@.TravWorld get(Object st) {
  if (st == null) return null;
  @PKG@.TravWorld w = (@PKG@.TravWorld) ALL.get(st);
  if (w != null) return w;
  w = new @PKG@.TravWorld();
  Object o = ALL.putIfAbsent(st, w);
  return o != null ? (@PKG@.TravWorld) o : w;
}""")
M(tworld, "public boolean idle() { return this.fx.isEmpty() && this.quick.isEmpty() && this.orbs.isEmpty() && this.pend.isEmpty(); }")
M(tworld, r"""
public int live(long now) {
  int n = 0;
  for (int k = 0; k < this.fx.size(); k++) {
    @PKG@.TravFx f = (@PKG@.TravFx) this.fx.get(k);
    if (f.kind != 0 && f.until > now) n++;
  }
  return n;
}""")
F(tworld, "public static volatile long DROPPED = 0L;")
# a new trail / orb; over trav.maxLive the OLDEST live ones end now (removed on the next tick, markers included)
M(tworld, r"""
public void add(@PKG@.TravFx f, int max, long now) {
  if (f == null) return;
  if (f.kind != 0) {
    int live = live(now);
    for (int k = 0; k < this.fx.size() && live >= max; k++) {
      @PKG@.TravFx o = (@PKG@.TravFx) this.fx.get(k);
      if (o.kind != 0 && o.until > now) { o.until = now; live--; DROPPED = DROPPED + 1L; }
    }
  }
  this.fx.add(f);
}""")

# ---- TravJob (blink / hop, run on the caster's world thread OUTSIDE the systems) + TravHeal (the heal orb's heals) - fields first
tjob.addInterface(pool.get("java.lang.Runnable"))
for f in ("public int kind;", "public java.util.UUID u;", "public String world;", "public @ST@ mst;", "public @REF@ marker;", "public double[] dir;",
          "public int idx;"):
    F(tjob, f)
C(tjob, r"""
public TravJob(int kind, java.util.UUID u, String world, @ST@ mst, @REF@ marker, double[] dir, int idx) {
  this.kind = kind;
  this.u = u;
  this.world = world;
  this.mst = mst;
  this.marker = marker;
  this.dir = dir;
  this.idx = idx;
}""")
theal.addInterface(pool.get("java.lang.Runnable"))
for f in ("public java.util.UUID healer;", "public java.util.UUID[] who;", "public double[] hp;", "public @ST@ st;", "public String wand;"):
    F(theal, f)
C(theal, r"""
public TravHeal(java.util.UUID healer, java.util.UUID[] who, double[] hp, @ST@ st, String wand) {
  this.healer = healer;
  this.who = who;
  this.hp = hp;
  this.st = st;
  this.wand = wand;
}""")

# ---- ArmoryTrav: the engine glue (no method throws to the engine)
for f in ("public static volatile boolean SYS_TRAV = false;", "public static volatile boolean SYS_HIT = false;", "public static volatile boolean SYS_TICK = false;",
          "public static volatile long BLINKS = 0L;", "public static volatile long REFUNDS = 0L;", "public static volatile long HOPS = 0L;",
          "public static volatile long BURSTS = 0L;", "public static volatile long BURST_HITS = 0L;", "public static volatile long TRAIL_HITS = 0L;",
          "public static volatile long PIERCES = 0L;", "public static volatile long RANGED = 0L;",
          "public static volatile double HEALED = 0.0;", "public static volatile String LAST_WHY = \"\";",
          "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap TOLD = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.Map MINE = java.util.Collections.synchronizedMap(new java.util.IdentityHashMap());",
          "public static volatile @VCF@ DASH = null;",
          "public static volatile @PKG@.TravGrid GRID = null;",                 # HARNESS SEAM ONLY (null in the game = the world's blocks)
          "public static volatile java.util.function.Function NEAR = null;",    # HARNESS SEAM ONLY (null in the game = TargetUtil's sphere query)
          "public static final String FX_PORTAL = %s;" % jstr(FX_PORTAL), "public static final String SND_BLINK = %s;" % jstr(SND_BLINK),
          "public static final String PS_BURST = %s;" % jstr(PS_BURST), "public static final String SND_BURST = %s;" % jstr(SND_BURST),
          "public static final String PS_HEAL = %s;" % jstr(PS_HEAL), "public static final String SND_HEAL = %s;" % jstr(SND_HEAL),
          "public static final String PS_TRAIL = %s;" % jstr(PS_TRAIL), "public static final String PS_RING = %s;" % jstr(PS_RING),
          "public static final boolean HOP_SERVER = %s;" % ("true" if HOP_MODE == "server" else "false")):
    F(trav, f)
M(trav, r"""
public static void warn(String key, String msg) { @PKG@.ArmoryLog.warnOnce("trav:" + key, msg); }""")
M(trav, r"""
public static java.util.function.Function fn(String key) {
  try {
    Object o = @PKG@.ArmoryDefs.bridge().get(key);
    return o instanceof java.util.function.Function ? (java.util.function.Function) o : null;
  } catch (Throwable t) { return null; }
}""")
M(trav, r"""
public static @WLD@ worldOf(Object st) {
  try {
    Object e = null;
    if (st instanceof @ST@) e = ((@ST@) st).getExternalData();
    else if (st instanceof @CB@) e = ((@CB@) st).getExternalData();
    if (e instanceof @ES@) return ((@ES@) e).getWorld();
  } catch (Throwable t) { }
  return null;
}""")
M(trav, r"""
public static boolean pvp(@WLD@ w) {
  try { return w != null && w.getWorldConfig() != null && w.getWorldConfig().isPvpEnabled(); } catch (Throwable t) { return false; }
}""")
# party:fn:members as Strings (null = SkyyParty absent / no answer) - the SkyyClasses HealTask.members pattern
M(trav, r"""
public static String[] members(java.util.UUID u) {
  java.util.function.Function f = fn("party:fn:members");
  if (f == null || u == null) return null;
  try {
    Object r = f.apply(u);
    if (!(r instanceof Object[])) return null;
    Object[] a = (Object[]) r;
    String[] out = new String[a.length];
    for (int i = 0; i < a.length; i++) out[i] = a[i] == null ? null : String.valueOf(a[i]).trim();
    return out;
  } catch (Throwable t) { return null; }
}""")
# allies (spec 1.3 + section 8): the same player, SkyyClasses' class:fn:ally (Object[]{UUID a, UUID b} -> Boolean), else SkyyParty's members
M(trav, r"""
public static boolean ally(java.util.UUID a, java.util.UUID b) {
  if (a == null || b == null) return false;
  if (a.equals(b)) return true;
  java.util.function.Function f = fn("class:fn:ally");
  if (f != null) {
    try {
      Object r = f.apply(new Object[] { a, b });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    } catch (Throwable t) { }
  }
  String[] ms = members(a);
  if (ms == null) return false;
  String s = b.toString();
  for (int i = 0; i < ms.length; i++) if (ms[i] != null && ms[i].equalsIgnoreCase(s)) return true;
  return false;
}""")
# SkyyClasses' weapon lock (class:fn:allowed, Object[]{UUID, itemId} -> Boolean): a class that may not use the weapon gets no traversal
M(trav, r"""
public static boolean allowed(java.util.UUID u, String item) {
  java.util.function.Function f = fn("class:fn:allowed");
  if (f == null || u == null || item == null) return true;
  try {
    Object r = f.apply(new Object[] { u, item });
    return !(r instanceof Boolean) || ((Boolean) r).booleanValue();
  } catch (Throwable t) { return true; }
}""")
M(trav, r"""
public static String handItem(@CAC@ acc, @REF@ r) {
  try {
    @IS@ it = @INVC@.getItemInHand(acc, r);
    return (it == null || it.isEmpty()) ? null : it.getItemId();
  } catch (Throwable t) { return null; }
}""")
M(trav, r"""
public static boolean dead(@CAC@ acc, @REF@ r) {
  try { return acc.getComponent(r, @DTH@.getComponentType()) != null; } catch (Throwable t) { return false; }
}""")
M(trav, r"""
public static void addStat(@CAC@ acc, @REF@ r, int idx, double v) {
  if (idx < 0 || !(v > 0.0)) return;
  try {
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m != null) m.addStatValue(idx, (float) v);
  } catch (Throwable t) { warn("stat", "could not give Mana back (" + t + ")"); }
}""")
# the traversal's Stamina (taken only when the traversal happens): 1 = paid (or nothing to pay), 0 = too little (nothing taken), -1 = no
# Stamina stat readable (nothing taken, the traversal goes on - never blocks a player whose stats cannot be read)
M(trav, r"""
public static int takeStamina(@CAC@ acc, @REF@ r, double cost) {
  if (!(cost > 0.0)) return 1;
  try {
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m == null) return -1;
    int si = @DST@.getStamina();
    if (si < 0) return -1;
    @ESV@ sv = m.get(si);
    if (sv == null) return -1;
    if ((double) sv.get() + 1.0E-4 < cost) return 0;
    m.subtractStatValue(si, (float) cost);
    return 1;
  } catch (Throwable t) { warn("stamina", "Stamina could not be read (" + t + ") - traversals take none"); return -1; }
}""")
M(trav, r"""
public static void tell(@PR@ pr, String text) {
  if (pr == null || text == null) return;
  try {
    java.util.UUID u = pr.getUuid();
    long now = System.currentTimeMillis();
    Object o = TOLD.get(u);
    if (o instanceof Long && now - ((Long) o).longValue() < 2500L) return;
    TOLD.put(u, Long.valueOf(now));
    pr.sendMessage(@MSG@.raw(text).color("#ffbf66"));
  } catch (Throwable t) { }
}""")
# ---- FX (trav.fx; never throws)
M(trav, r"""
public static void particle(String id, double x, double y, double z, @CAC@ acc) {
  if (!@PKG@.ArmoryCfg.TRAV_FX || id == null) return;
  try { @PTU@.spawnParticleEffect(id, new @VEC@(x, y, z), acc); } catch (Throwable t) { warn("particle", "particle " + id + " failed (" + t + ")"); }
}""")
M(trav, r"""
public static void sound(String id, double x, double y, double z, @CAC@ acc) {
  if (!@PKG@.ArmoryCfg.TRAV_FX || id == null) return;
  try {
    int i = @SEV@.getAssetMap().getIndex(id);
    if (i >= 0) @SNU@.playSoundEvent3d(i, @SCAT@.SFX, x, y, z, acc);
  } catch (Throwable t) { warn("sound", "sound " + id + " failed (" + t + ")"); }
}""")
M(trav, r"""
public static void effect(@REF@ r, String id, @CAC@ acc) {
  if (!@PKG@.ArmoryCfg.TRAV_FX || r == null) return;
  try {
    @ECC@ c = (@ECC@) acc.getComponent(r, @ECC@.getComponentType());
    Object fx = @EFX@.getAssetMap().getAsset(id);
    if (c != null && fx instanceof @EFX@) c.addEffect(r, (@EFX@) fx, acc);
  } catch (Throwable t) { warn("effect", "entity effect " + id + " failed (" + t + ")"); }
}""")
# the dagger dash's push feel (Daggers_Dash_Backward.json, asserted at build time)
M(trav, (r"""
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
  } catch (Throwable t) { warn("dash", "the dash velocity config failed (" + t + ") - the hop uses the engine default"); return null; }
}""").replace("AIRMAXf", repr(float(DASH_CFG["AirResistanceMax"])) + "f").replace("AIRf", repr(float(DASH_CFG["AirResistance"])) + "f")
      .replace("GROUNDMAXf", repr(float(DASH_CFG["GroundResistanceMax"])) + "f").replace("GROUNDf", repr(float(DASH_CFG["GroundResistance"])) + "f")
      .replace("THRESf", repr(float(DASH_CFG["Threshold"])) + "f").replace("STYLE", DASH_CFG["Style"]))
M(trav, r"""
public static double[] unit(@VEC@ v) {
  if (v == null) return null;
  double l = Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
  if (!(l > 1.0E-6) || Double.isNaN(l) || Double.isInfinite(l)) return null;
  return new double[] { v.x / l, v.y / l, v.z / l };
}""")
# the caster's look (TargetUtil.getLook - what LaunchProjectileInteraction aims with): the fallback when the launch velocity is unreadable
M(trav, r"""
public static double[] look(@CB@ buf, java.util.UUID u) {
  try {
    @REF@ r = ((@ES@) buf.getExternalData()).getRefFromUUID(u);
    if (r == null || !r.isValid()) return null;
    @XFM@ lk = @TU@.getLook(r, buf);
    if (lk == null) return null;
    return unit(lk.getDirection());
  } catch (Throwable t) { return null; }
}""")
M(trav, r"""
public static String pidOf(@CB@ buf, @REF@ pr) {
  try {
    if (buf == null || pr == null || !pr.isValid()) return null;
    @LPC@ pc = (@LPC@) buf.getComponent(pr, @LPC@.getComponentType());
    return pc == null ? null : pc.getProjectileAssetName();
  } catch (Throwable t) { return null; }
}""")
# a projectile like LaunchProjectileInteraction#firstRun builds it (bytecode 163-293): assembleDefaultProjectile, Intangible, initialize,
# shoot (creator = the caster, so ShotTrack / GearShotTrack record it from the weapon in hand), addEntity SPAWN
M(trav, r"""
public static @REF@ spawn(@CB@ buf, String pid, double x, double y, double z, double dx, double dy, double dz, java.util.UUID creator) {
  try {
    @TRS@ tr = (@TRS@) buf.getResource(@TRS@.getResourceType());
    if (tr == null || pid == null || creator == null) return null;
    float yaw = @PHM@.headingFromDirection(dx, dz);
    float pitch = @PHM@.pitchFromDirection(dx, dy, dz);
    @HOLD@ h = @LPC@.assembleDefaultProjectile(tr, pid, new @VEC@(x, y, z), new @R3F@(pitch, yaw, 0.0f));
    if (h == null) return null;
    @LPC@ pc = (@LPC@) h.getComponent(@LPC@.getComponentType());
    if (pc == null) return null;
    h.ensureComponent(@INTG@.getComponentType());
    if (pc.getProjectile() == null) {          // firstRun 229-251: initialize resolves the asset; still none = nothing launched
      pc.initialize();
      if (pc.getProjectile() == null) return null;
    }
    pc.shoot(h, creator, x, y, z, yaw, pitch);
    return buf.addEntity(h, @ADDR@.SPAWN);
  } catch (Throwable t) { warn("spawn", "could not launch " + pid + " (" + t + ")"); return null; }
}""")
# the target class (spec 1.3): 2 = the caster / an ally player, 1 = a player who is not an enemy, 0 = an enemy, -1 = skip (dead, no stats)
M(trav, r"""
public static int kind(@CAC@ acc, @REF@ r, @REF@ caster, java.util.UUID cu, boolean pvp) {
  try {
    if (r == null || !r.isValid()) return -1;
    if (caster != null && r.equals(caster)) return 2;
    if (dead(acc, r)) return -1;
    @PR@ pr = (@PR@) acc.getComponent(r, @PR@.getComponentType());
    if (pr != null) {
      java.util.UUID u = pr.getUuid();
      if (u == null) return -1;
      return @PKG@.TravMath.who(u.equals(cu), ally(cu, u), pvp, @PKG@.ArmoryCfg.TRAV_PLAYERS);
    }
    if (acc.getComponent(r, @NPC@.getComponentType()) != null && acc.getComponent(r, @ESM@.getComponentType()) != null) return 0;
    return -1;
  } catch (Throwable t) { return -1; }
}""")
M(trav, "public static boolean mine(Object d) { return d != null && MINE.remove(d) != null; }")
# one traversal hit through the WHOLE damage pipeline (Filter: tune / Gear / class lock / armour; PvP filter; Inspect: heal share):
# the shape of a vanilla orb hit (Damage$ProjectileSource(caster, projectile), PROJECTILE) - or Damage$EntitySource(caster) without a
# live projectile. Marked MINE so ArmoryHitSys never bursts on its own burst.
M(trav, r"""
public static boolean hit(@CB@ buf, @REF@ target, @REF@ caster, @REF@ proj, double amount) {
  try {
    if (!(amount > 0.0) || caster == null || !caster.isValid() || target == null || !target.isValid()) return false;
    @DCS@ cause = @DCS@.PROJECTILE;
    if (cause == null) return false;
    @DSRC@ src = null;
    if (proj != null && proj.isValid()) src = new @DPRJ@(caster, proj);
    else src = new @DENT@(caster);
    @DMG@ d = new @DMG@(src, cause, (float) amount);
    if (MINE.size() > 4096) MINE.clear();
    MINE.put(d, Boolean.TRUE);
    @DSYS@.executeDamage(target, buf, d);
    return true;
  } catch (Throwable t) { warn("hit", "a traversal hit failed (" + t + ")"); return false; }
}""")
M(trav, r"""
public static java.util.List near(@CB@ buf, double x, double y, double z, double r) {
  try {
    if (NEAR != null) {
      Object o = NEAR.apply(new double[] { x, y, z, r });
      return o instanceof java.util.List ? new java.util.ArrayList((java.util.List) o) : new java.util.ArrayList();
    }
    java.util.List l = @TU@.getAllEntitiesInSphere(new @VEC@(x, y, z), r, buf);
    return l == null ? new java.util.ArrayList() : new java.util.ArrayList(l);
  } catch (Throwable t) { warn("near", "the area query failed (" + t + ")"); return new java.util.ArrayList(); }
}""")
M(trav, r"""
public static @VEC@ posOf(@CAC@ acc, @REF@ r) {
  try {
    if (r == null) return null;
    @TC@ tc = (@TC@) acc.getComponent(r, @TC@.getComponentType());
    return tc == null ? null : tc.getPosition();
  } catch (Throwable t) { return null; }
}""")
# a marker that is not needed any more (no blink / no trail): TravTick removes it on its next run
M(trav, r"""
public static void dropMarker(@PKG@.TravWorld tw, @REF@ marker, long now) {
  if (tw == null || marker == null) return;
  tw.add(new @PKG@.TravFx(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, now, now, 1000L, 0.0, null, marker, 0), 0, now);
}""")
# ---- THE BLINK (spec 1.1 + section 8): world thread, outside the systems (the SkyyEssentials teleport path)
M(trav, r"""
public static @PKG@.TravGrid grid(@WLD@ w) {
  if (GRID != null) return GRID;
  return new @PKG@.WorldGrid(w);
}""")
M(trav, r"""
public static void blink(@PKG@.TravJob j) {
  long now = System.currentTimeMillis();
  @PKG@.TravWorld tw = @PKG@.TravWorld.get(j.mst);
  int i = j.idx;
  double mana = (double) @PKG@.ArmoryDefs.S_C[i];
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(j.u); } catch (Throwable t0) { pr = null; }
  @REF@ ref = (pr == null || !pr.isValid()) ? null : pr.getReference();
  @ST@ st = (ref == null || !ref.isValid()) ? null : ref.getStore();
  if (st == null || st != j.mst) { LAST_WHY = "the caster left this world"; dropMarker(tw, j.marker, now); return; }
  String why = null;
  @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
  @VEC@ pos = tc == null ? null : tc.getPosition();
  double[] d = j.dir;
  @WLD@ w = worldOf(st);
  Object last = LAST.get(j.u);
  if (pos == null || d == null || w == null) why = "no position or direction";
  else if (dead(st, ref)) why = "dead";
  else if (!allowed(j.u, @PKG@.ArmoryDefs.S_IDS[i]) || !allowed(j.u, handItem(st, ref))) why = "class lock";     // trav-fix: the CAST staff too
  else if (@PKG@.ArmoryCfg.BLINK_CD > 0.0 && last instanceof Long && now - ((Long) last).longValue() < Math.round(@PKG@.ArmoryCfg.BLINK_CD * 1000.0)) why = "cooldown";
  double t = 0.0;
  if (why == null) {
    t = @PKG@.TravMath.scan(grid(w), pos.x, pos.y, pos.z, d[0], d[1], d[2], (double) @PKG@.ArmoryCfg.BLINK_DIST, @PKG@.ArmoryCfg.BLINK_FLOOR);
    if (!(t > 0.0)) why = "no free spot ahead";
  }
  double cost = @PKG@.TravMath.staminaCost(mana, @PKG@.ArmoryCfg.STAMINA_PCT, @PKG@.ArmoryCfg.STAMINA_CAP);
  if (why == null && takeStamina(st, ref, cost) == 0) {
    why = "too little Stamina";
    tell(pr, "Not enough Stamina to blink - " + @PKG@.TravMath.fmt(cost) + " needed.");
  }
  if (why != null) {
    addStat(st, ref, @DST@.getMana(), mana);     // a blink that does not move you costs NOTHING (Skyy 2026-10-05): the chain's Mana back
    REFUNDS = REFUNDS + 1L;
    LAST_WHY = why;
    dropMarker(tw, j.marker, now);
    return;
  }
  double sx = pos.x;
  double sy = pos.y;
  double sz = pos.z;
  double ex = sx + d[0] * t;
  double ey = sy + d[1] * t;
  double ez = sz + d[2] * t;
  @TP@ tp = @TP@.createForPlayer(w, new @VEC@(ex, ey, ez), tc.getRotation());
  try {
    @HR@ hr = (@HR@) st.getComponent(ref, @HR@.getComponentType());
    if (hr != null && hr.getRotation() != null) tp.setHeadRotation(hr.getRotation());
  } catch (Throwable t2) { }
  if (@PKG@.ArmoryCfg.BLINK_KEEPFALL) tp = tp.withoutVelocityReset();
  st.putComponent(ref, @TP@.getComponentType(), tp);
  LAST.put(j.u, Long.valueOf(now));
  BLINKS = BLINKS + 1L;
  LAST_WHY = "blink " + @PKG@.TravMath.fmt(t) + " blocks";
  effect(ref, FX_PORTAL, st);
  sound(SND_BLINK, sx, sy, sz, st);
  sound(SND_BLINK, ex, ey, ez, st);
  if (!@PKG@.ArmoryCfg.TRAIL_ON || !(@PKG@.ArmoryCfg.TRAIL_SECONDS > 0.0)) { dropMarker(tw, j.marker, now); return; }
  long step = Math.round(@PKG@.ArmoryCfg.BLINK_TICK * 1000.0);
  if (step < 50L) step = 50L;
  double per = @PKG@.TravMath.perTick((double) @PKG@.ArmoryDefs.S_CD[i], (double) @PKG@.ArmoryCfg.TRAIL_PCT, step);
  tw.add(new @PKG@.TravFx(1, sx, sy + 0.9, sz, ex, ey + 0.9, ez, @PKG@.ArmoryCfg.TRAIL_WIDTH / 2.0, now + Math.round(@PKG@.ArmoryCfg.TRAIL_SECONDS * 1000.0),
    now, step, per, j.u, j.marker, 5000 + i), @PKG@.ArmoryCfg.TRAV_MAXLIVE, now);
}""")
# trav-fix: the world's MovementConfig MinFallSpeedToEngageRoll (what DamageSystems$FallDamagePlayers compares; vanilla 21) - SkyySkills'
# djMaxFall read; unreadable = 21
M(trav, r"""
public static double maxFall(@WLD@ w) {
  try {
    int mi = w.getGameplayConfig().getPlayerConfig().getMovementConfigIndex();
    Object o = @MCF@.getAssetMap().getAsset(mi);
    if (o instanceof @MCF@ && ((@MCF@) o).getMinFallSpeedToEngageRoll() > 0.0f) return (double) ((@MCF@) o).getMinFallSpeedToEngageRoll();
  } catch (Throwable t) { }
  return 21.0;
}""")
# ---- THE HOP (spec 1.2 + 2.3): Set velocity opposite to the look, the dagger dash's config; half without ground behind
M(trav, r"""
public static void hop(@PKG@.TravJob j) {
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(j.u); } catch (Throwable t0) { pr = null; }
  @REF@ ref = (pr == null || !pr.isValid()) ? null : pr.getReference();
  @ST@ st = (ref == null || !ref.isValid()) ? null : ref.getStore();
  if (st == null || st != j.mst || j.dir == null || !(@PKG@.ArmoryCfg.HOP_FORCE > 0.0)) return;
  if (dead(st, ref)) return;
  if (!allowed(j.u, @PKG@.ArmoryDefs.W_IDS[j.idx]) || !allowed(j.u, handItem(st, ref))) { LAST_WHY = "hop: class lock"; return; }   // trav-fix: the CAST wand
  @VEC@ pos = posOf(st, ref);
  @VEL@ v = (@VEL@) st.getComponent(ref, @VEL@.getComponentType());
  @WLD@ w = worldOf(st);
  if (pos == null || v == null || w == null) return;
  double cost = @PKG@.TravMath.staminaCost((double) @PKG@.ArmoryDefs.W_C[j.idx], @PKG@.ArmoryCfg.STAMINA_PCT, @PKG@.ArmoryCfg.STAMINA_CAP);
  if (takeStamina(st, ref, cost) == 0) { LAST_WHY = "hop: too little Stamina"; tell(pr, "Not enough Stamina to hop - " + @PKG@.TravMath.fmt(cost) + " needed."); return; }
  double[] pb = @PKG@.TravMath.hopProbe(j.dir[0], j.dir[2]);
  boolean ground = @PKG@.TravMath.ground(grid(w), pos.x + pb[0], pos.y, pos.z + pb[1], @PKG@.ArmoryCfg.HOP_GROUND);
  double[] hv = @PKG@.TravMath.hopVector(j.dir[0], j.dir[1], j.dir[2], @PKG@.ArmoryCfg.HOP_FORCE, !ground);
  double cvy = Double.NaN;
  try { @VEC@ cv = v.getClientVelocity(); if (cv != null) cvy = cv.y; } catch (Throwable t1) { cvy = Double.NaN; }
  double vy = @PKG@.TravMath.hopVy(hv[1], cvy, maxFall(w));         // trav-fix: a hop never cancels a damaging fall (Double-Jump rule 7)
  boolean kept = vy != hv[1];
  v.addInstruction(new @VEC@(hv[0], vy, hv[2]), dash(), @CVT@.Set);
  HOPS = HOPS + 1L;
  LAST_WHY = "hop " + (ground ? "full" : "half (no ground behind)") + (kept ? " - fall kept" : "");
}""")
# ---- ArmoryTravSys.onEntityAdded (SPAWN of one of our projectiles): quick orbs -> range / pierce record; wand charged orb -> burst
# record + the hop job; staff blink marker -> stop it + the blink job (or, staff.mode orb / part.trav off, the 0.1 charged orb)
M(trav, r"""
public static void added(@REF@ ref, @LPC@ pc, int c, @ST@ st, @CB@ buf) {
  int i = c % 1000;
  @PKG@.TravWorld tw = @PKG@.TravWorld.get(st);
  @VEC@ p = posOf(buf, ref);
  java.util.UUID cu = pc.getCreatorUuid();
  String pid = pc.getProjectileAssetName();
  if ((c >= 1000 && c < 2000) || (c >= 3000 && c < 4000)) {
    @PKG@.TravShot s = (@PKG@.TravShot) tw.pend.remove(ref);
    if (s == null) {
      if (p == null) return;
      s = new @PKG@.TravShot(p.x, p.y, p.z, (double) (c < 2000 ? @PKG@.ArmoryCfg.RANGE_WAND : @PKG@.ArmoryCfg.RANGE_STAFF), c, cu, pid);
    }
    tw.quick.put(ref, s);
    return;
  }
  if (c >= 2000 && c < 3000) {
    tw.orbs.put(ref, new @PKG@.TravShot(p == null ? 0.0 : p.x, p == null ? 0.0 : p.y, p == null ? 0.0 : p.z, 0.0, c, cu, pid));
    if (!@PKG@.ArmoryCfg.PART_TRAV || cu == null || !HOP_SERVER) return;
    double[] d = unit(@PKG@.ArmorySpawn.launchVelocity(pc.getSimplePhysicsProvider()));
    if (d == null) d = look(buf, cu);
    @WLD@ w = worldOf(st);
    if (w != null && d != null) w.execute(new @PKG@.TravJob(2, cu, w.getName(), st, null, d, i));
    return;
  }
  if (c >= 5000 && c < 6000) {
    @VEC@ v = @PKG@.ArmorySpawn.launchVelocity(pc.getSimplePhysicsProvider());
    double[] d = unit(v);
    if (!@PKG@.ArmoryCfg.PART_TRAV || "orb".equals(@PKG@.ArmoryCfg.STAFF_MODE)) {
      if (d == null && cu != null) d = look(buf, cu);
      if (p != null && d != null && cu != null) spawn(buf, @PKG@.ArmoryDefs.S_ORB[i], p.x, p.y, p.z, d[0], d[1], d[2], cu);
      buf.removeEntity(ref, @REMR@.REMOVE);
      return;
    }
    if (v != null) v.set(0.0, 0.0, 0.0);     // the marker stays where it was cast (no movement = no sweep = no hit events)
    if (d == null && cu != null) d = look(buf, cu);
    @WLD@ w = worldOf(st);
    if (w == null || cu == null) { buf.removeEntity(ref, @REMR@.REMOVE); return; }
    w.execute(new @PKG@.TravJob(1, cu, w.getName(), st, ref, d, i));
  }
}""")
# the burst (spec 1.2 + 2.4): every OTHER enemy within burst.radius takes burst.percent % of dmgBase; then the heal orb (healBase)
M(trav, r"""
public static void burst(@ST@ st, @CB@ buf, @REF@ proj, @PKG@.TravShot s, double cx, double cy, double cz, @REF@ direct, double dmgBase, double healBase) {
  if (!@PKG@.ArmoryCfg.PART_TRAV || s == null) return;
  int wi = s.code % 1000;
  if (wi >= 0 && wi < @PKG@.ArmoryDefs.W_IDS.length && !allowed(s.caster, @PKG@.ArmoryDefs.W_IDS[wi])) { LAST_WHY = "burst: class lock"; return; }   // trav-fix
  long now = System.currentTimeMillis();
  @PKG@.TravWorld tw = @PKG@.TravWorld.get(st);
  @REF@ caster = null;
  try { caster = s.caster == null ? null : ((@ES@) buf.getExternalData()).getRefFromUUID(s.caster); } catch (Throwable t0) { caster = null; }
  boolean pvp = pvp(worldOf(buf));
  BURSTS = BURSTS + 1L;
  if (@PKG@.ArmoryCfg.BURST_PCT > 0 && dmgBase > 0.0 && caster != null && caster.isValid() && @PKG@.ArmoryCfg.BURST_RADIUS > 0.0) {
    double amt = dmgBase * (double) @PKG@.ArmoryCfg.BURST_PCT / 100.0;
    java.util.List l = near(buf, cx, cy, cz, @PKG@.ArmoryCfg.BURST_RADIUS);
    for (int k = 0; k < l.size(); k++) {
      @REF@ r = (@REF@) l.get(k);
      if (r == null || (direct != null && r.equals(direct))) continue;
      if (kind(buf, r, caster, s.caster, pvp) != 0) continue;
      if (hit(buf, r, caster, proj, amt)) BURST_HITS = BURST_HITS + 1L;
    }
  }
  particle(PS_BURST, cx, cy, cz, buf);
  sound(SND_BURST, cx, cy, cz, buf);
  if (@PKG@.ArmoryCfg.ORB_HEAL_PCT > 0 && @PKG@.ArmoryCfg.ORB_SECONDS > 0.0 && healBase > 0.0 && @PKG@.ArmoryCfg.ORB_RADIUS > 0.0) {
    long step = Math.round(@PKG@.ArmoryCfg.ORB_TICK * 1000.0);
    if (step < 50L) step = 50L;
    double per = @PKG@.TravMath.perTick(healBase, (double) @PKG@.ArmoryCfg.ORB_HEAL_PCT, step);
    tw.add(new @PKG@.TravFx(2, cx, cy, cz, cx, cy, cz, @PKG@.ArmoryCfg.ORB_RADIUS, now + Math.round(@PKG@.ArmoryCfg.ORB_SECONDS * 1000.0), now + step, step,
      per, s.caster, null, s.code), @PKG@.ArmoryCfg.TRAV_MAXLIVE, now);
    sound(SND_HEAL, cx, cy, cz, buf);
  }
}""")
M(trav, r"""
public static double[] hitAt(@DMG@ d, @CB@ buf, @REF@ tg) {
  try {
    Object o = d.getIfPresentMetaObject(@DMG@.HIT_LOCATION);
    if (o instanceof @V4@) { @V4@ v4 = (@V4@) o; return new double[] { v4.x, v4.y, v4.z }; }      // trav-fix: the engine's type (MetaKey<Vector4d>)
    if (o instanceof @VEC@) { @VEC@ v = (@VEC@) o; return new double[] { v.x, v.y, v.z }; }
  } catch (Throwable t) { }
  @VEC@ p = posOf(buf, tg);
  if (p != null) return new double[] { p.x, p.y + 0.9, p.z };
  return null;
}""")
M(trav, r"""
public static double thickness(@CAC@ acc, @REF@ r) {
  try {
    @BBX@ b = (@BBX@) acc.getComponent(r, @BBX@.getComponentType());
    if (b == null || b.getBoundingBox() == null) return 1.0;
    double w = Math.max(b.getBoundingBox().width(), b.getBoundingBox().depth());
    return w > 0.0 && w < 16.0 ? w : 1.0;
  } catch (Throwable t) { return 1.0; }
}""")
# ---- ArmoryHitSys (Inspect group: the damage really landed): a wand charged orb's direct hit -> burst + heal orb; a wand quick orb's hit
# -> the pierce continuation (no cap by default - Skyy: only the range limits it)
M(trav, r"""
public static void landed(@ST@ st, @CB@ buf, @DMG@ d, @REF@ pj, int c, @REF@ tg) {
  @PKG@.TravWorld tw = @PKG@.TravWorld.of(st);
  if (tw == null || tg == null) return;
  if (c >= 2000 && c < 3000) {
    @PKG@.TravShot s = (@PKG@.TravShot) tw.orbs.get(pj);
    if (s == null || s.count > 0) return;
    s.count = 1;
    double[] h = hitAt(d, buf, tg);
    if (h == null) return;
    burst(st, buf, pj, s, h[0], h[1], h[2], tg, (double) d.getInitialAmount(), (double) d.getAmount());
    return;
  }
  if (c < 1000 || c >= 2000) return;
  @PKG@.TravShot s = (@PKG@.TravShot) tw.quick.get(pj);
  if (s == null || s.caster == null) return;
  s.hits.add(tg);
  s.count = s.count + 1;
  if (@PKG@.ArmoryCfg.PIERCE_MAX > 0 && s.count >= @PKG@.ArmoryCfg.PIERCE_MAX + 1) return;
  double[] h = hitAt(d, buf, tg);
  if (h == null) return;
  double dx = h[0] - s.sx;
  double dy = h[1] - s.sy;
  double dz = h[2] - s.sz;
  double l = Math.sqrt(dx * dx + dy * dy + dz * dz);
  if (!(l > 0.1)) return;
  dx = dx / l;
  dy = dy / l;
  dz = dz / l;
  double ext = thickness(buf, tg) * 0.75 + 0.3;
  double x = h[0] + dx * ext;
  double y = h[1] + dy * ext;
  double z = h[2] + dz * ext;
  double gone = Math.sqrt((x - s.sx) * (x - s.sx) + (y - s.sy) * (y - s.sy) + (z - s.sz) * (z - s.sz));
  if (gone >= s.range) return;
  // trav-fix (critic HIGH): the continuation never starts past a block - the line from the hit to the spawn point (spawn cell included)
  // must be passable, else the chain ends there (a mob against a wall never lets the shot through the wall)
  if (!@PKG@.TravMath.clear(grid(worldOf(buf)), h[0], h[1], h[2], x, y, z)) { LAST_WHY = "pierce: a block past the enemy"; return; }
  @REF@ nr = spawn(buf, s.pid, x, y, z, dx, dy, dz, s.caster);
  if (nr != null) { tw.pend.put(nr, s.next()); PIERCES = PIERCES + 1L; }
}""")
# ArmoryTuneSys (Filter group): true = this pierce chain already hit that enemy (the hit is cancelled - "hitting each" once)
M(trav, r"""
public static boolean repeatHit(@ST@ st, @REF@ pj, @REF@ tg, String pid) {
  try {
    if (pj == null || tg == null || !@PKG@.ArmoryDefs.isQuick(pid)) return false;
    @PKG@.TravWorld tw = @PKG@.TravWorld.of(st);
    if (tw == null) return false;
    @PKG@.TravShot s = (@PKG@.TravShot) tw.quick.get(pj);
    return s != null && s.hits.contains(tg);
  } catch (Throwable t) { return false; }
}""")
# trav-fix (critic: TravWorld.ALL kept every world Store until restart - SkyyIslands unloads island worlds): an idle world's state goes
M(trav, r"""
public static void forget(@ST@ st, @PKG@.TravWorld tw) {
  try { if (st != null && tw != null && tw.idle()) @PKG@.TravWorld.ALL.remove(st, tw); } catch (Throwable t) { }
}""")
# ArmoryTravSys.onEntityRemove: a wand charged orb that hit nobody bursts where it ended (spec 2.4 miss: asset damage x tune,
# Damage$EntitySource(caster) - the orb is being removed); the records end
M(trav, r"""
public static void removed(@REF@ ref, boolean removeReason, @ST@ st, @CB@ buf) {
  @PKG@.TravWorld tw = @PKG@.TravWorld.of(st);
  if (tw == null) return;
  tw.quick.remove(ref);
  tw.pend.remove(ref);
  @PKG@.TravShot s = (@PKG@.TravShot) tw.orbs.remove(ref);
  if (s == null || s.count > 0 || !removeReason || !@PKG@.ArmoryCfg.PART_TRAV) { forget(st, tw); return; }
  @VEC@ p = posOf(buf, ref);
  if (p == null) p = posOf(st, ref);
  if (p == null) return;
  int i = s.code % 1000;
  double base = (double) @PKG@.ArmoryDefs.W_CD[i];
  if (@PKG@.ArmoryCfg.PART_TUNE) base = base * @PKG@.ArmoryCfg.tunePct(false, i) / 100.0;
  s.count = 1;
  burst(st, buf, null, s, p.x, p.y, p.z, null, base, base);
  forget(st, tw);
}""")
# ---- one effect tick (TravTick): trail damage to every enemy inside the capsule / heal orb heals (SkyyClasses' class:fn:heal on this world)
M(trav, r"""
public static void tickFx(@PKG@.TravFx f, @ST@ st, @CB@ buf, long now) {
  if (f.kind == 1) {
    @REF@ caster = null;
    try { caster = ((@ES@) buf.getExternalData()).getRefFromUUID(f.caster); } catch (Throwable t0) { caster = null; }
    if (caster == null || !caster.isValid()) return;        // no credit without the shooter (spec 1.3)
    boolean pvp = pvp(worldOf(buf));
    double mx = (f.ax + f.bx) / 2.0;
    double my = (f.ay + f.by) / 2.0;
    double mz = (f.az + f.bz) / 2.0;
    double half = @PKG@.TravMath.segDist(f.ax, f.ay, f.az, mx, my, mz, mx, my, mz);
    java.util.List l = near(buf, mx, my, mz, half + f.r + 1.5);
    for (int k = 0; k < l.size(); k++) {
      @REF@ r = (@REF@) l.get(k);
      if (kind(buf, r, caster, f.caster, pvp) != 0) continue;
      @VEC@ p = posOf(buf, r);
      if (p == null) continue;
      if (@PKG@.TravMath.segDist(p.x, p.y + 0.9, p.z, f.ax, f.ay, f.az, f.bx, f.by, f.bz) > f.r + 0.4) continue;
      if (hit(buf, r, caster, f.marker, f.amount)) TRAIL_HITS = TRAIL_HITS + 1L;
    }
    f.ticks = f.ticks + 1;
    return;
  }
  if (f.kind == 2) {
    boolean pvp = pvp(worldOf(buf));
    java.util.List l = near(buf, f.ax, f.ay, f.az, f.r);
    java.util.ArrayList us = new java.util.ArrayList();
    java.util.ArrayList hs = new java.util.ArrayList();
    boolean classes = fn("class:fn:heal") != null;      // SkyyClasses 0.1.12 splits party / others itself (priestHeal.othersPercent)
    for (int k = 0; k < l.size(); k++) {
      @REF@ r = (@REF@) l.get(k);
      try {
        if (r == null || !r.isValid() || dead(buf, r)) continue;
        @PR@ pr = (@PR@) buf.getComponent(r, @PR@.getComponentType());
        if (pr == null || pr.getUuid() == null) continue;
        java.util.UUID u = pr.getUuid();
        int k2 = @PKG@.TravMath.who(u.equals(f.caster), ally(f.caster, u), pvp, @PKG@.ArmoryCfg.TRAV_PLAYERS);
        double hp = @PKG@.TravMath.share(f.amount, classes && k2 == 1 ? 2 : k2, @PKG@.ArmoryCfg.ORB_PARTY_PCT, @PKG@.ArmoryCfg.ORB_OTHERS_PCT);
        if (hp > 0.0) { us.add(u); hs.add(Double.valueOf(hp)); }
      } catch (Throwable t1) { }
    }
    f.ticks = f.ticks + 1;
    particle(PS_HEAL, f.ax, f.ay, f.az, buf);
    if (us.isEmpty()) return;
    java.util.UUID[] who = new java.util.UUID[us.size()];
    double[] hp = new double[us.size()];
    for (int k = 0; k < who.length; k++) { who[k] = (java.util.UUID) us.get(k); hp[k] = ((Double) hs.get(k)).doubleValue(); }
    @WLD@ w = worldOf(buf);
    String wand = (f.code >= 2000 && f.code < 3000) ? @PKG@.ArmoryDefs.W_IDS[f.code % 1000] : null;
    if (w != null) w.execute(new @PKG@.TravHeal(f.caster, who, hp, st, wand));
  }
}""")
# the light (trail: points every block along the line; heal orb: 8 points on its ring) - every 0.25 s / 0.5 s
M(trav, r"""
public static void drawFx(@PKG@.TravFx f, @CB@ buf) {
  if (f.kind == 1) {
    double dx = f.bx - f.ax;
    double dy = f.by - f.ay;
    double dz = f.bz - f.az;
    double l = Math.sqrt(dx * dx + dy * dy + dz * dz);
    int n = (int) Math.floor(l);
    if (n > 24) n = 24;
    for (int k = 0; k <= n; k++) {
      double u = n == 0 ? 0.0 : (double) k / (double) n;
      particle(PS_TRAIL, f.ax + dx * u, f.ay + dy * u, f.az + dz * u, buf);
    }
    return;
  }
  if (f.kind == 2) {
    for (int k = 0; k < 8; k++) {
      double a = Math.PI * 2.0 * (double) k / 8.0;
      particle(PS_RING, f.ax + Math.cos(a) * f.r, f.ay + 0.2, f.az + Math.sin(a) * f.r, buf);
    }
  }
}""")
# the end of an effect: its marker goes (REMOVE)
M(trav, r"""
public static void endFx(@PKG@.TravFx f, @CB@ buf) {
  try { if (f.marker != null && f.marker.isValid()) buf.removeEntity(f.marker, @REMR@.REMOVE); } catch (Throwable t) { }
}""")
# heal one player directly (SkyyClasses absent): room-clamped, never a dead player, no XP (spec 2.5)
M(trav, r"""
public static double healDirect(@ST@ st, java.util.UUID u, double hp) {
  try {
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null || !pr.isValid()) return 0.0;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid() || r.getStore() != st || dead(st, r)) return 0.0;
    @ESM@ m = (@ESM@) st.getComponent(r, @ESM@.getComponentType());
    if (m == null) return 0.0;
    int hi = @DST@.getHealth();
    @ESV@ v = m.get(hi);
    if (v == null || v.get() <= 0.0f) return 0.0;
    double room = (double) (v.getMax() - v.get());
    double got = hp < room ? hp : room;
    if (!(got > 0.01)) return 0.0;
    m.addStatValue(hi, (float) got);
    return got;
  } catch (Throwable t) { warn("heal", "the heal orb could not heal (" + t + ")"); return 0.0; }
}""")
M(tjob, r"""
public void run() {
  try {
    if (this.kind == 1) @PKG@.ArmoryTrav.blink(this);
    else @PKG@.ArmoryTrav.hop(this);
  } catch (Throwable t) { @PKG@.ArmoryTrav.warn("job" + this.kind, (this.kind == 1 ? "blink" : "hop") + " failed (" + t + ")"); }
}""")
# class:fn:heal (SkyyClasses 0.1.12): Object[]{UUID healer, UUID target, Double hp, String why, String wandItemId} -> Double healed (the
# party / others split by its priestHeal.othersPercent, the wand's charged cap, the per-second budget, Divinity XP, chat; 0.0 = refused).
# Called on the target's world thread (World.execute of the orb's world) for players Armory would not hurt. No SkyyClasses: straight into
# Health with Armory's own split (orb.othersPercent), no XP.
M(theal, r"""
public void run() {
  try {
    java.util.function.Function f = @PKG@.ArmoryTrav.fn("class:fn:heal");
    // trav-fix (critic: an older SkyyClasses = uncapped direct heals): SkyyClasses present (class:fn:allowed) but no class:fn:heal = older than
    // 0.1.12 -> the heal orb heals nobody (never the direct path that skips the Priest check, the wand cap, the budget and the switch)
    if (f == null && @PKG@.ArmoryTrav.fn("class:fn:allowed") != null) {
      @PKG@.ArmoryTrav.warn("oldclasses", "SkyyClasses is older than 0.1.12 (no class:fn:heal) - the heal orb heals nobody; deploy SkyyClasses 0.1.12");
      @PKG@.ArmoryTrav.LAST_WHY = "heal orb: SkyyClasses too old";
      return;
    }
    for (int k = 0; k < this.who.length; k++) {
      if (this.who[k] == null || !(this.hp[k] > 0.0)) continue;
      double got = 0.0;
      if (f != null) {
        try {
          Object r = f.apply(this.wand != null ? new Object[] { this.healer, this.who[k], Double.valueOf(this.hp[k]), "armory:orb", this.wand }
                                               : new Object[] { this.healer, this.who[k], Double.valueOf(this.hp[k]), "armory:orb" });
          if (r instanceof Number) got = ((Number) r).doubleValue();
        } catch (Throwable t1) { got = 0.0; }
      } else {
        got = @PKG@.ArmoryTrav.healDirect(this.st, this.who[k], this.hp[k]);
      }
      if (got > 0.0) @PKG@.ArmoryTrav.HEALED = @PKG@.ArmoryTrav.HEALED + got;
    }
  } catch (Throwable t) { @PKG@.ArmoryTrav.warn("healtask", "heal orb tick failed (" + t + ")"); }
}""")
# ---- TravWorld.run: once per world tick (TravTick) - effects, quick orb ranges, record hygiene
M(tworld, r"""
public void run(@ST@ st, @CB@ buf, long now) {
  for (int k = this.fx.size() - 1; k >= 0; k--) {
    @PKG@.TravFx f = (@PKG@.TravFx) this.fx.get(k);
    if (now >= f.until) {
      this.fx.remove(k);
      @PKG@.ArmoryTrav.endFx(f, buf);
      continue;
    }
    if (f.kind != 0 && now >= f.next) {
      f.next = f.next + f.step;
      if (f.next <= now) f.next = now + f.step;
      try { @PKG@.ArmoryTrav.tickFx(f, st, buf, now); } catch (Throwable t1) { @PKG@.ArmoryTrav.warn("tickfx", "a traversal tick failed (" + t1 + ")"); }
    }
    if (f.kind != 0 && now >= f.fxNext) {
      f.fxNext = now + (f.kind == 1 ? 250L : 500L);
      @PKG@.ArmoryTrav.drawFx(f, buf);
    }
  }
  java.util.Iterator it = this.quick.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    @REF@ r = (@REF@) e.getKey();
    @PKG@.TravShot s = (@PKG@.TravShot) e.getValue();
    if (r == null || !r.isValid()) { it.remove(); continue; }
    @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, r);
    if (p == null) continue;
    double dx = p.x - s.sx;
    double dy = p.y - s.sy;
    double dz = p.z - s.sz;
    if (dx * dx + dy * dy + dz * dz > s.range * s.range) {
      it.remove();
      try { buf.removeEntity(r, @REMR@.REMOVE); @PKG@.ArmoryTrav.RANGED = @PKG@.ArmoryTrav.RANGED + 1L; } catch (Throwable t2) { }
    }
  }
  java.util.Iterator io = this.orbs.keySet().iterator();
  while (io.hasNext()) { @REF@ r = (@REF@) io.next(); if (r == null || !r.isValid()) io.remove(); }
  if (this.pend.size() > 256) this.pend.clear();
}""")

# ---- the three systems (one registerSystem per class)
F(travsys, "public @QRY@ query;")
C(travsys, "public ArmoryTravSys() { super(); this.query = null; }")
M(travsys, r"""
public @QRY@ getQuery() {
  if (this.query == null) this.query = @QRY@.and(new @QRY@[] { (@QRY@) @TC@.getComponentType(), (@QRY@) @LPC@.getComponentType() });
  return this.query;
}""")
M(travsys, r"""
public void onEntityAdded(@REF@ ref, @ADDR@ reason, @ST@ st, @CB@ buf) {
  try {
    if (reason != @ADDR@.SPAWN) return;
    @LPC@ pc = (@LPC@) buf.getComponent(ref, @LPC@.getComponentType());
    if (pc == null) return;
    int c = @PKG@.ArmoryDefs.pidCode(pc.getProjectileAssetName());
    if (c < 1000) return;
    @PKG@.ArmoryTrav.added(ref, pc, c, st, buf);
  } catch (Throwable t) { @PKG@.ArmoryTrav.warn("added:" + t.getClass().getName(), "traversal hook failed (" + t + ")"); }
}""")
M(travsys, r"""
public void onEntityRemove(@REF@ ref, @REMR@ reason, @ST@ st, @CB@ buf) {
  try { @PKG@.ArmoryTrav.removed(ref, reason == @REMR@.REMOVE, st, buf); }
  catch (Throwable t) { @PKG@.ArmoryTrav.warn("removed:" + t.getClass().getName(), "traversal remove hook failed (" + t + ")"); }
}""")
C(hitsys, "public ArmoryHitSys() { super(); }")
M(hitsys, "public @QRY@ getQuery() { return @QRY@.any(); }")
M(hitsys, "public @SG@ getGroup() { return @DMOD@.get().getInspectDamageGroup(); }")
M(hitsys, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (@PKG@.ArmoryTrav.mine(d)) return;          // our own burst / trail hit: never a burst of its own
    if (d.isCancelled() || !@PKG@.ArmoryCfg.PART_TRAV) return;
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DPRJ@)) return;
    @REF@ pj = ((@DPRJ@) src).getProjectile();
    int c = @PKG@.ArmoryDefs.pidCode(@PKG@.ArmoryTrav.pidOf(buf, pj));
    if (c < 1000 || c >= 3000) return;
    @PKG@.ArmoryTrav.landed(st, buf, d, pj, c, chunk.getReferenceTo(idx));
  } catch (Throwable t) { @PKG@.ArmoryTrav.warn("hit:" + t.getClass().getName(), "burst / pierce failed (" + t + ")"); }
}""")
C(ttick, "public TravTick() { super(); }")
M(ttick, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(ttick, "public boolean isParallel(int a, int b) { return false; }")
M(ttick, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @PKG@.TravWorld tw = @PKG@.TravWorld.of(store);
    if (tw == null) return;
    if (tw.idle()) { @PKG@.ArmoryTrav.forget(store, tw); return; }     // trav-fix: no Store is kept once its world has nothing live
    long ns = System.nanoTime();
    if (ns - tw.lastNs < 20000000L) return;     // once per world tick (the first player of the tick runs it)
    tw.lastNs = ns;
    tw.run(store, cb, System.currentTimeMillis());
  } catch (Throwable t) { @PKG@.ArmoryTrav.warn("tick:" + t.getClass().getName(), "traversal tick failed (" + t + ")"); }
}""")
'''
NEW_JAVA = JAVA_BLOCK      # defined below the header (the classes' Java, inserted before ArmoryTuneSys: tune + info call into it)
assert NEW_JAVA.startswith("# ---------------------------------------------------------------- 0.1.1 TRAVERSALS")
rep('''# ---------------------------------------------------------------- ArmoryTuneSys (Filter group, BEFORE ArmorDamageReduction)''',
    NEW_JAVA.rstrip("\n") + '''

# ---------------------------------------------------------------- ArmoryTuneSys (Filter group, BEFORE ArmorDamageReduction)''')
# tune: + the pierce chain's "never the same enemy twice" + the staff quick bonus
rep('''    String pid = pidOf(buf, ((@DPRJ@) src).getProjectile());
    if (pid == null) return;
    float f = @PKG@.ArmoryDefs.tuneFactor(pid, true, @PKG@.ArmoryCfg.TUNE_W, @PKG@.ArmoryCfg.TUNE_S, @PKG@.ArmoryCfg.QUICK_DAMAGE);''',
    '''    String pid = pidOf(buf, ((@DPRJ@) src).getProjectile());
    if (pid == null) return;
    if (chunk != null && @PKG@.ArmoryDefs.isQuick(pid) && @PKG@.ArmoryTrav.repeatHit(st, ((@DPRJ@) src).getProjectile(), chunk.getReferenceTo(idx), pid)) { d.setCancelled(true); return; }   // 0.1.1 pierce
    float f = @PKG@.ArmoryDefs.tuneFactor2(pid, true, @PKG@.ArmoryCfg.TUNE_W, @PKG@.ArmoryCfg.TUNE_S, @PKG@.ArmoryCfg.QUICK_DAMAGE, @PKG@.ArmoryCfg.STAFF_BONUS);''')
rep('''public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!@PKG@.ArmoryCfg.PART_TUNE || !(ev instanceof @DMG@)) return;''', '''public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@)) return;
    if (!@PKG@.ArmoryCfg.PART_TUNE) {   // 0.1.1: the pierce rule holds with the tune off too
      @DMG@ d0 = (@DMG@) ev;
      @DSRC@ s0 = d0.getSource();
      if (chunk != null && !d0.isCancelled() && s0 instanceof @DPRJ@ && @PKG@.ArmoryTrav.repeatHit(st, ((@DPRJ@) s0).getProjectile(), chunk.getReferenceTo(idx), pidOf(buf, ((@DPRJ@) s0).getProjectile()))) d0.setCancelled(true);
      return;
    }''')
# pack check: the staff hold launches the marker (Damage 0)
rep('''    wantLaunch(bad, am, pm, "SkyyArmory_Staff_Cast_Launch_" + m, @PKG@.ArmoryDefs.S_ORB[i], @PKG@.ArmoryDefs.S_CD[i], 30.0);''',
    '''    wantLaunch(bad, am, pm, "SkyyArmory_Staff_Cast_Launch_" + m, @PKG@.ArmoryDefs.S_BLINK[i], 0, 30.0);   // 0.1.1: the blink marker''')
rep('''public static String[] packCheck() {''', '''public static String[] packCheck() {
  // 0.1.1: the 8 StaffOrb projectiles stay loaded (orb mode + part.trav off spawn them from Java) - checked below with the other projectiles''')
# armory:fn:info: + [8] traversal words, [9] quick words, [10] staff quick bonus % (spec 3.1.5 + 3.3)
rep('''        Integer.valueOf(@PKG@.ArmoryDefs.W_CD[i]), Integer.valueOf(@PKG@.ArmoryDefs.W_QD[i]), Double.valueOf(@PKG@.ArmoryCfg.tunePct(false, i)),
        @PKG@.ArmoryDefs.W_ORB[i], @PKG@.ArmoryDefs.W_QORB[i] };''', '''        Integer.valueOf(@PKG@.ArmoryDefs.W_CD[i]), Integer.valueOf(@PKG@.ArmoryDefs.W_QD[i]), Double.valueOf(@PKG@.ArmoryCfg.tunePct(false, i)),
        @PKG@.ArmoryDefs.W_ORB[i], @PKG@.ArmoryDefs.W_QORB[i], @PKG@.TravMath.travWords(false, i > 0, @PKG@.ArmoryCfg.PART_TRAV, @PKG@.ArmoryCfg.STAFF_MODE,
        @PKG@.ArmoryCfg.BLINK_DIST, @PKG@.ArmoryCfg.BURST_RADIUS, @PKG@.ArmoryCfg.ORB_RADIUS, @PKG@.TravMath.staminaCost((double) @PKG@.ArmoryDefs.W_C[i], @PKG@.ArmoryCfg.STAMINA_PCT, @PKG@.ArmoryCfg.STAMINA_CAP)),
        @PKG@.TravMath.quickWords(false, @PKG@.ArmoryDefs.W_QORB[i].length() > 0, @PKG@.ArmoryCfg.PART_TRAV, @PKG@.ArmoryCfg.PIERCE_MAX, @PKG@.ArmoryCfg.RANGE_WAND),
        Double.valueOf(0.0) };''')
rep('''        Integer.valueOf(@PKG@.ArmoryDefs.S_CD[i]), Integer.valueOf(@PKG@.ArmoryDefs.S_QD[i]), Double.valueOf(@PKG@.ArmoryCfg.tunePct(true, i)),
        @PKG@.ArmoryDefs.S_ORB[i], @PKG@.ArmoryDefs.S_QORB[i] };''', '''        Integer.valueOf(@PKG@.ArmoryDefs.S_CD[i]), Integer.valueOf(@PKG@.ArmoryDefs.S_QD[i]), Double.valueOf(@PKG@.ArmoryCfg.tunePct(true, i)),
        @PKG@.ArmoryDefs.S_ORB[i], @PKG@.ArmoryDefs.S_QORB[i], @PKG@.TravMath.travWords(true, true, @PKG@.ArmoryCfg.PART_TRAV, @PKG@.ArmoryCfg.STAFF_MODE,
        @PKG@.ArmoryCfg.BLINK_DIST, @PKG@.ArmoryCfg.BURST_RADIUS, @PKG@.ArmoryCfg.ORB_RADIUS, @PKG@.TravMath.staminaCost((double) @PKG@.ArmoryDefs.S_C[i], @PKG@.ArmoryCfg.STAMINA_PCT, @PKG@.ArmoryCfg.STAMINA_CAP)),
        @PKG@.TravMath.quickWords(true, @PKG@.ArmoryDefs.S_QORB[i].length() > 0, @PKG@.ArmoryCfg.PART_TRAV, 0, @PKG@.ArmoryCfg.RANGE_STAFF),
        Double.valueOf(@PKG@.ArmoryCfg.PART_TUNE ? (double) @PKG@.ArmoryCfg.STAFF_BONUS : 0.0) };''')

# ================================================================================================ plugin: systems, bridge, log, shutdown
rep('''BRIDGE_KEYS = ["armory:wands", "armory:staffs", "armory:quick", "armory:fn:info", "armory:check", "gear:loot:add:SkyyArmory"]''',
    '''BRIDGE_KEYS = ["armory:wands", "armory:staffs", "armory:quick", "armory:fn:info", "armory:check", "gear:loot:add:SkyyArmory", "armory:trav"]''')
rep('''    try { getEntityStoreRegistry().registerSystem(new @PKG@.ArmorySpawnSys(false)); } catch (Throwable t4) { @PKG@.ArmoryLog.warn("the quick shot hook could not be registered: " + t4 + " - quick shots keep the built-in size and speed"); }
  }''', '''    try { getEntityStoreRegistry().registerSystem(new @PKG@.ArmorySpawnSys(false)); } catch (Throwable t4) { @PKG@.ArmoryLog.warn("the quick shot hook could not be registered: " + t4 + " - quick shots keep the built-in size and speed"); }
  }
  // 0.1.1 traversals: one registerSystem per class (brief rule); a failing one is WARNed once and the rest still run
  try { getEntityStoreRegistry().registerSystem(new @PKG@.ArmoryTravSys()); @PKG@.ArmoryTrav.SYS_TRAV = true; }
  catch (Throwable t5) { @PKG@.ArmoryLog.warn("ArmoryTravSys could not be registered: " + t5 + " - no blink / hop / burst on a miss / quick shot range; staff holds then do nothing"); }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.ArmoryHitSys()); @PKG@.ArmoryTrav.SYS_HIT = true; }
  catch (Throwable t6) { @PKG@.ArmoryLog.warn("ArmoryHitSys could not be registered: " + t6 + " - no burst on a direct hit, no pierce"); }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.TravTick()); @PKG@.ArmoryTrav.SYS_TICK = true; }
  catch (Throwable t7) { @PKG@.ArmoryLog.warn("TravTick could not be registered: " + t7 + " - no trail damage, no heal orb, no quick shot range"); }''')
rep('''  b.put("gear:loot:add:SkyyArmory", @PKG@.ArmoryDefs.LOOT_TEXT);
}""")''', '''  b.put("gear:loot:add:SkyyArmory", @PKG@.ArmoryDefs.LOOT_TEXT);
  b.put("armory:trav", @PKG@.ArmoryCfg.TRAV_TEXT);
}""")''')
rep('''  @PKG@.ArmorySpawn.SHOTS = 0L;
  systems();''', '''  @PKG@.ArmorySpawn.SHOTS = 0L;
  @PKG@.TravWorld.ALL.clear();
  systems();''')
rep('''  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""" % (WAND_STYLE,''', '''  @PKG@.ArmoryLog.info("@VERSION@ magic traversals: " + @PKG@.ArmoryCfg.TRAV_TEXT + " (systems: hook " + @PKG@.ArmoryTrav.SYS_TRAV + ", hits " + @PKG@.ArmoryTrav.SYS_HIT + ", tick " + @PKG@.ArmoryTrav.SYS_TICK + ")");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""" % (WAND_STYLE,''')
rep('''  @PKG@.ArmoryCheck.STOP = true;
  unpublish();''', '''  @PKG@.ArmoryCheck.STOP = true;
  unpublish();
  @PKG@.TravWorld.ALL.clear();''')
rep('''man = B.manifest(MOD, VERSION, "SkyWynn armory: 7 metal Priest wands (Copper to Onyxium, tap = blue quick shot at 1/5 Mana, hold = charged "
                 "shot; Mana and damage per metal) + the Wood wand tap, and the Mage staff ladder (2x the wand's Mana). Recipes at the Weapon "
                 "Bench (Bow tab). Settings in game (Server Setup > Armory). Zero dependencies.", PKG + ".SkyyArmoryPlugin")''',
    '''man = B.manifest(MOD, VERSION, "SkyWynn armory: 7 metal Priest wands (Copper to Onyxium, tap = blue quick shot that pierces, hold = hop "
                 "back + burst + heal orb) + the Wood wand tap, and the Mage staff ladder (tap = quick shot, hold = blink + light trail). "
                 "Recipes at the Weapon Bench (Bow tab). Settings in game (Server Setup > Armory). Zero dependencies.", PKG + ".SkyyArmoryPlugin")''')
rep('''print("switches: style %s, look %s, size %s, tap anim %s / %s, Wood quick %s, staff base %d (S1), staff tap %s (S2), Onyxium staff recipe %s (S3)" % (
    WAND_STYLE, QUICK_LOOK, QUICK_SIZE_MODE, QUICK_ANIM, STAFF_QUICK_ANIM, WOOD_QUICK, STAFF_BASE, STAFF_TAP, ONYX_STAFF_RECIPE))''',
    '''print("switches: style %s, look %s, size %s, tap anim %s / %s, Wood quick %s, staff base %d (S1), staff tap %s (S2), Onyxium staff recipe %s (S3)" % (
    WAND_STYLE, QUICK_LOOK, QUICK_SIZE_MODE, QUICK_ANIM, STAFF_QUICK_ANIM, WOOD_QUICK, STAFF_BASE, STAFF_TAP, ONYX_STAFF_RECIPE))
print("0.1.1 traversals: hop %s, scan %s, orb look %s, staff Stamina %d, %d blink markers (model %s), trail light %s (%d files), rows %d new" % (
    HOP_MODE, SCAN_MODE, ORB_LOOK, STAFF_STAMINA, len(S_BLINK), MARKER, PS_TRAIL, len(TRAIL_FILES), len(CFG_NEW)))''')

assert s.count("registerSystem(") == SYS0 + 3, "0.1.1 registers exactly 3 more systems"
for _bad in ("ID_SSTAM, ID_SSTAMD,", 'launch(ID_SORB % _m, "CastSummonCharged")'):
    assert _bad not in s, _bad
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))

# ================================================================================================ the harness: 0.1's checks (patched for 0.1.1) + the new sections
HARNESS_P8 = r'''# ============================================================================================================ P8. 0.1.1 traversal assets (spec 5 T1)
VMODEL = aj("model", VAN_ORB)
stam_files = [n for n in JN if "SkyyArmory_Staff_Stamina" in n]
stam_keys = sorted(i for i, d in JINT.items() if set((d.get("StatModifiers") or {}).keys()) & {"Stamina", "StaminaRegenDelay"}
                   or set((d.get("Costs") or {}).keys()) & {"Stamina", "StaminaRegenDelay"})
check(not stam_files and not stam_keys, "P8 (T1): no SkyyArmory_Staff_Stamina* file and no Stamina / regen delay in any chain: %s %s" % (stam_files, stam_keys))
for m in METALS:
    par = JINT["SkyyArmory_Staff_Cast_" + m]["Next"]["Interactions"]
    kids = [r_["Interactions"][0] for r_ in par]
    lid = JINT["SkyyArmory_Staff_Cast_Launch_" + m]
    b_ = JPRJ[BLINK[m]]
    check(kids == ["SkyyArmory_Staff_Cast_Cost_" + m, "SkyyArmory_Staff_Cast_Launch_" + m, "SkyyArmory_Staff_Cast_Effect"]
          and lid["ProjectileId"] == BLINK[m] and lid["Effects"] == {"ItemAnimationId": "CastSummonCharged"} and lid["RunTime"] == 0.25,
          "P8 (T1): the %s staff hold = cost + launch %s + effect (no Stamina step)" % (m, BLINK[m]))
    check(b_["Damage"] == 0 and b_["Gravity"] == 0 and b_["TimeToLive"] >= 8.0 and b_["Appearance"] == "SkyyArmory_Marker"
          and "HitParticles" not in b_ and "DeathParticles" not in b_ and b_["DeathEffectsOnHit"] is False and "Parent" not in b_
          and b_["MuzzleVelocity"] == 30, "P8 (T1): %s - Damage 0, Gravity 0, TTL %s (> the 8 s longest trail), the marker model, no hit / death particles" % (
              BLINK[m], b_["TimeToLive"]))
    check(JPRJ[SORB[m]]["Damage"] == S[m][3], "P8: the %s StaffOrb stays (staff.mode orb / part.trav off spawn it from Java): %d" % (m, JPRJ[SORB[m]]["Damage"]))
MK = J[J_MODELS["SkyyArmory_Marker"]]
check(MK["DefaultAttachments"] == [] and MK["Particles"] == [] and MK["Trails"] == [] and MK["HitBox"] == VMODEL["HitBox"]
      and MK["Model"] == VMODEL["Model"] and MK["Texture"] == VMODEL["Texture"] == "Items/Projectiles/Projectile_default.png",
      "P8 (T1): SkyyArmory_Marker = the orb model asset without attachment / particles / trails (the transparent base texture), the orb's hitbox")
tl = J[J_PSYS["SkyyArmory_Trail_Light"]]
gold = []
for sp_ in tl["Spawners"]:
    sid = sp_["SpawnerId"]
    gold.append(sid in J_PSP)
    for c_ in re.findall(r'"Color": "(?:rgba\()?#([0-9a-fA-F]{6})', json.dumps(J[J_PSP[sid]])):
        import colorsys as _cs
        h_, s_, v_ = _cs.rgb_to_hsv(*(int(c_[i:i + 2], 16) / 255.0 for i in (0, 2, 4)))
        if s_ > 0.15:
            gold.append(30.0 <= h_ * 360.0 <= 60.0)
check(len(tl["Spawners"]) == 2 and all(gold), "P8: the trail light = GreenOrbTrail's 2 spawners recoloured gold (hue 30-60 degrees): %s" % [sp_["SpawnerId"] for sp_ in tl["Spawners"]])
check("SkyyArmory_Wand_Hop" not in JINT and all("ApplyForce" not in json.dumps(d) for d in JINT.values()),
      "P8: HOP_MODE server - no client dash in any wand chain (the hop is the Java push)")
print("P8. 0.1.1 assets: no Stamina steps, 8 staff holds launch the blink marker (Damage 0, invisible model), gold trail light, no asset hop")
'''
HARNESS_N = r'''    # ---------------- N. 0.1.1 MAGIC TRAVERSALS - every new path EXECUTED (spec 5 T2-T4 + Skyy's section 8)
    ACfg.useDefaults()
    AT, TW, TM, TJ, TH = (JClass(PKG + n_) for n_ in ("ArmoryTrav", "TravWorld", "TravMath", "TravJob", "TravHeal"))
    V3 = JClass("org.joml.Vector3d")
    V4 = JClass("org.joml.Vector4d")          # trav-fix: Damage.HIT_LOCATION's real type (MetaKey<Vector4d>)
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    SYS_ = JClass("java.lang.System")
    nowms = lambda: int(SYS_.currentTimeMillis())
    # --- N1. TravMath (pure) on a fake grid: 0 passable, 1 solid, -1 unknown
    @JImplements(PKG + "TravGrid")
    class Grid:
        def __init__(self, fn): self.fn = fn
        @JOverride
        def at(self, x, y, z): return int(self.fn(int(x), int(y), int(z)))
    def world_fn(walls=(), floor_ok=lambda x, z: True, ceiling=None, unknown=lambda x, y, z: False):
        def fn(x, y, z):
            if unknown(x, y, z):
                return -1
            if y == 63 and floor_ok(x, z):
                return 1
            if ceiling is not None and y == ceiling:
                return 1
            for w_ in walls:
                if w_(x, y, z):
                    return 1
            return 0
        return fn
    wall6 = lambda x, y, z: x == 6 and 64 <= y <= 66
    g_wall = Grid(world_fn([wall6]))
    sc = lambda g, s, d, D=10.0, f=12: round(float(TM.scan(g, s[0], s[1], s[2], d[0], d[1], d[2], D, f)), 6)
    check(sc(g_wall, (0.0, 64.0, 0.5), (1, 0, 0)) == 5.7, "N1 (T3): a wall at x 6 -> the blink lands 5.7 (0.3 short, body box free): %s" % sc(g_wall, (0.0, 64.0, 0.5), (1, 0, 0)))
    check(sc(g_wall, (0.5, 64.0, 0.5), (1, 0, 0)) == 5.2, "N1: from x 0.5 the same wall -> 5.2 blocks (lands at x 5.7)")
    g_void = Grid(world_fn(floor_ok=lambda x, z: x <= 3))
    check(sc(g_void, (0.5, 64.0, 0.5), (1, 0, 0)) == 3.0 and sc(g_void, (0.5, 64.0, 0.5), (1, 0, 0), f=0) == 10.0,
          "N1 (T3): open void beyond x 4 -> the last floored step (3.0); floorCheck 0 -> the full 10: %s / %s" % (
              sc(g_void, (0.5, 64.0, 0.5), (1, 0, 0)), sc(g_void, (0.5, 64.0, 0.5), (1, 0, 0), f=0)))
    g_ceil = Grid(world_fn(ceiling=70))
    check(sc(g_ceil, (0.5, 64.0, 0.5), (0, 1, 0)) == 4.2, "N1 (T3): straight up under a ceiling at y 70 -> 4.2 (the head stays below it): %s" % sc(g_ceil, (0.5, 64.0, 0.5), (0, 1, 0)))
    g_open = Grid(world_fn())
    check(sc(g_open, (0.5, 64.0, 0.5), (0, 1, 0)) == 10.0 and sc(g_open, (0.5, 64.0, 0.5), (0, 1, 0), f=5) == 4.5,
          "N1 (T3): straight up in the open: 10 with the 12-block floor check, 4.5 with floorCheck 5")
    wall1 = lambda x, y, z: x == 1 and 64 <= y <= 66
    check(sc(Grid(world_fn([wall1])), (0.5, 64.0, 0.5), (1, 0, 0)) == 0.0, "N1: a wall in your face -> 0 = no blink (costs nothing)")
    check(sc(Grid(world_fn(unknown=lambda x, y, z: x >= 4)), (0.5, 64.0, 0.5), (1, 0, 0)) == 3.2, "N1: an unloaded section (unknown block) stops it like a wall: 3.2")
    diag = Grid(world_fn([lambda x, y, z: x == 4 and 64 <= y <= 66]))
    dg = sc(diag, (0.5, 64.0, 0.5), (1, 0, 1))
    check(dg == 4.5 and 0.5 + dg / math.sqrt(2.0) + 0.299 < 4.0, "N1: a 1-block wall is never skipped on a diagonal (the body box stops 4.5 blocks along, before x 4): %s" % dg)
    check(sc(g_open, (0.5, 64.0, 0.5), (0, 0, 0)) == 0.0 and sc(None, (0.5, 64.0, 0.5), (1, 0, 0)) == 0.0, "N1: no direction / no grid -> 0")
    sd = round(float(TM.segDist(0.0, 1.0, 0.0, -2.0, 0.0, 0.0, 2.0, 0.0, 0.0)), 6)
    check(sd == 1.0 and round(float(TM.segDist(5.0, 0.0, 0.0, -2.0, 0.0, 0.0, 2.0, 0.0, 0.0)), 6) == 3.0, "N1 (T3): segment distances (beside 1.0, past the end 3.0)")
    hv = lambda d, f, h: [round(float(x), 6) for x in TM.hopVector(d[0], d[1], d[2], f, h)]
    check(hv((0, 0, 1), 13.0, False) == [0.0, 0.0, -13.0] and hv((0, -1, 0), 13.0, False) == [0.0, 13.0, 0.0] and hv((0, 1, 0), 13.0, True) == [0.0, -6.5, 0.0]
          and hv((1, 0, 0), 0.0, False) == [0.0, 0.0, 0.0], "N1 (T3): hop = opposite to the look (level back, look down = straight up), half without ground, force 0 = none")
    check([round(float(x), 6) for x in TM.hopProbe(0.0, 1.0)] == [0.0, -3.0] and [round(float(x), 6) for x in TM.hopProbe(0.0, 0.0)] == [0.0, 0.0],
          "N1: the hop's ground check looks 3 blocks behind (under the feet when looking straight up / down)")
    check(round(float(TM.perTick(175.0, 30.0, 500)), 6) == 26.25 and round(float(TM.perTick(88.0, 20.0, 1000)), 6) == 17.6, "N1 (T3): Iron staff trail 26.25 per 0.5 s tick; Iron wand heal orb 17.6 per 1 s")
    stc = [round(float(TM.staminaCost(float(c_), 50, 10)), 3) for c_ in (10, 20, 30, 5, 15, 85)]
    check(stc == [5.0, 10.0, 10.0, 2.5, 7.5, 10.0] and float(TM.staminaCost(30.0, 50, 0)) == 15.0 and float(TM.staminaCost(30.0, 0, 10)) == 0.0,
          "N1 (section 8): 2 Mana : 1 Stamina - Skyy's 10 + 5 and 20 + 10, capped at 10; cap 0 = 15; 0%% = free: %s" % stc)
    check([int(TM.who(*a_)) for a_ in ((True, False, True, True), (False, True, True, True), (False, False, False, True), (False, False, True, True), (False, False, True, False))]
          == [2, 2, 1, 0, 1], "N1 (1.3): self / party = ally; a stranger is an enemy only with PvP on AND trav.players")
    check([round(float(TM.share(10.0, k_, 100, 50)), 3) for k_ in (2, 1, 0)] == [10.0, 5.0, 0.0], "N1 (section 8): heal orb share - party 100%, others 50%, enemies 0")
    check(str(TM.travWords(True, True, True, "blink", 10, 6.0, 9.0, 10.0)) == "Hold - blink 10 blocks + light trail - 10 Stamina"
          and str(TM.travWords(False, True, True, "blink", 10, 6.0, 9.0, 7.5)) == "Hold - hop back + burst 6 blocks + heal orb 9 blocks - 7.5 Stamina"
          and str(TM.travWords(True, True, True, "orb", 10, 6.0, 9.0, 10.0)) == "" and str(TM.travWords(False, True, False, "blink", 10, 6.0, 9.0, 1.0)) == ""
          and str(TM.quickWords(False, True, True, 0, 16)) == "pierces - 16 blocks" and str(TM.quickWords(True, True, True, 0, 24)) == "24 blocks"
          and str(TM.quickWords(False, True, False, 0, 16)) == "16 blocks" and str(TM.quickWords(False, False, True, 0, 16)) == "",
          "N1: the tooltip words ([8] / [9]) - no , : ; { } quote or underscore")
    check(not bool(TM.clear(g_wall, 5.5, 64.5, 0.5, 6.55, 64.5, 0.5)) and bool(TM.clear(g_wall, 2.0, 64.5, 0.5, 5.9, 64.5, 0.5))
          and not bool(TM.clear(None, 0.0, 64.5, 0.0, 1.0, 64.5, 0.0)) and not bool(TM.clear(g_wall, 2.0, 64.5, 0.5, 2.0, 63.5, 0.5)),
          "N1 (trav-fix, pierce): TravMath.clear - a segment into the wall at x 6 is blocked, one short of it is clear, no grid / a floor block = blocked")
    hvy = [round(float(TM.hopVy(a_, b_, 21.0)), 3) for a_, b_ in ((0.0, -30.0), (13.0, -30.0), (13.0, -10.0), (-13.0, -30.0), (-13.0, -10.0), (13.0, -21.0))]
    check(hvy == [-30.0, -30.0, 13.0, -30.0, -13.0, 13.0] and float(TM.hopVy(5.0, float("nan"), 21.0)) == 5.0 and float(TM.hopVy(13.0, -50.0, 0.0)) == 13.0,
          "N1 (trav-fix, Double-Jump rule 7): the hop keeps a fall faster than 21 b/s (vy = min(hop, fall)); a slow fall / no velocity read = the hop's vy: %s" % hvy)
    print("N1. TravMath on a fake grid: wall 5.7, void 3.0, ceiling 4.2, up 10 / 4.5, face-wall 0, hop vectors, 2:1 costs, ally / share rules, clear, hopVy")

    # --- N0. the engine stand-ins (component types registered like the modules do; a map-backed Store / CommandBuffer / World)
    CTF = JClass("javassist.CtField")
    CNC = JClass("javassist.CtNewConstructor")

    def stub(name, sup, fields, methods, ctor=None):
        """a stand-in subclass; it is only ever created by Unsafe.allocateInstance, so its constructor (needed by javassist when the
        superclass has no inheritable one) never runs"""
        c_ = CPj.makeClass("armoryharness." + name, CPj.get(sup))
        if ctor is not None:
            c_.addConstructor(CNC.make(ctor, c_))
        for f_ in fields:
            c_.addField(CTF.make(f_, c_))
        for m_ in methods:
            c_.addMethod(CtNM.make(m_, c_))
        try:
            c_.writeFile(hcls)
        except Exception as e_:
            raise SystemExit("stub %s: %s" % (name, e_.stacktrace() if hasattr(e_, "stacktrace") else e_))
        return JClass("armoryharness." + name)
    CP_ = "com.hypixel.hytale.component."
    GETC = ("public " + CP_ + "Component getComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t) { java.util.Map m = (java.util.Map) armoryharness.TStore.COMP.get(r); "
            "if (m == null) return null; return (" + CP_ + "Component) m.get(t); }")
    PUTC = ("public void putComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t, " + CP_ + "Component c) { java.util.Map m = (java.util.Map) armoryharness.TStore.COMP.get(r); "
            "if (m == null) { m = new java.util.HashMap(); armoryharness.TStore.COMP.put(r, m); } m.put(t, c); }")
    TSt = stub("TStore", CP_ + "Store", ["public static java.util.HashMap COMP = new java.util.HashMap();", "public static Object EXT = null;",
                                         "public static java.util.HashMap RES = new java.util.HashMap();"],
               [GETC, PUTC, "public void addComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t, " + CP_ + "Component c) { putComponent(r, t, c); }",
                "public Object getExternalData() { return EXT; }",
                "public " + CP_ + "Resource getResource(" + CP_ + "ResourceType t) { return (" + CP_ + "Resource) RES.get(t); }"],
               ctor="public TStore() { super((" + CP_ + "ComponentRegistry) null, 0, (Object) null, (" + CP_ + "IResourceStorage) null); }")
    TBf = stub("TBuf", CP_ + "CommandBuffer", ["public static java.util.ArrayList EVENTS = new java.util.ArrayList();",
                                               "public static java.util.ArrayList ADDED = new java.util.ArrayList();",
                                               "public static java.util.ArrayList REMOVED = new java.util.ArrayList();", "public static int NEXT = 5000;",
                                               "public static " + CP_ + "Store STORE = null;"],
               [GETC, PUTC, "public Object getExternalData() { return armoryharness.TStore.EXT; }",
                "public " + CP_ + "Resource getResource(" + CP_ + "ResourceType t) { return (" + CP_ + "Resource) armoryharness.TStore.RES.get(t); }",
                "public " + CP_ + "Ref addEntity(" + CP_ + "Holder h, " + CP_ + "AddReason why) { NEXT = NEXT + 1; " + CP_ + "Ref r = new " + CP_ + "Ref(STORE, NEXT); "
                "ADDED.add(new Object[] { h, r }); return r; }",
                "public void removeEntity(" + CP_ + "Ref r, " + CP_ + "RemoveReason why) { REMOVED.add(r); }",
                "public void invoke(" + CP_ + "Ref r, " + CP_ + "system.EcsEvent e) { EVENTS.add(new Object[] { r, e }); }",
                "public " + CP_ + "Store getStore() { return STORE; }"])
    WLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    TWd = stub("TWorld", "com.hypixel.hytale.server.core.universe.world.World", ["public static java.util.ArrayList JOBS = new java.util.ArrayList();"],
               ["public void execute(java.lang.Runnable r) { JOBS.add(r); }"],
               ctor="public TWorld() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }")

    def gfield(clsname, meth):
        """the field a getter reads (its first getfield) - the stand-ins set exactly that field"""
        cc_ = CPj.get(clsname)
        m_ = [x for x in cc_.getDeclaredMethods() if str(x.getName()) == meth][0]
        it_ = m_.getMethodInfo().getCodeAttribute().iterator()
        cp_ = m_.getMethodInfo().getConstPool()
        while it_.hasNext():
            p_ = it_.next()
            if it_.byteAt(p_) == 0xb4:
                return str(cp_.getFieldrefName(it_.u16bitAt(p_ + 1)))
        return None

    @JImplements("java.util.function.Supplier")
    class Sup:
        def __init__(self, f): self.f = f
        @JOverride
        def get(self): return self.f()

    def regtype(cls_, name_, make=None):
        try:
            cd_ = jfield(cls_, "CODEC").get(None)
            if make is None and cd_ is not None:
                return reg_.registerComponent(cls_.class_, name_, cd_)
        except Exception:
            pass
        return reg_.registerComponent(cls_.class_, Sup(make if make is not None else (lambda: cls_())))
    EMN = "com.hypixel.hytale.server.core.modules.entity.EntityModule"
    HRc = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    VELc = JClass("com.hypixel.hytale.server.core.modules.physics.component.Velocity")
    TPc = JClass("com.hypixel.hytale.server.core.modules.entity.teleport.Teleport")
    BBXc = JClass("com.hypixel.hytale.server.core.modules.entity.component.BoundingBox")
    ECCc = JClass("com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent")
    UUIDCc = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    MSCc = JClass("com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent")
    VISc = JClass("com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$Visible")
    INTGc = JClass("com.hypixel.hytale.server.core.modules.entity.component.Intangible")
    PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    ESMc = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DTHc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    reg_errs = []
    for getter_, cls_, mk_ in (("getHeadRotationComponentType", HRc, None), ("getVelocityComponentType", VELc, None), ("getTeleportComponentType", TPc, lambda: None),
                               ("getBoundingBoxComponentType", BBXc, None), ("getEffectControllerComponentType", ECCc, None),
                               ("getPlayerComponentType", PLAc, lambda: None), ("getUuidComponentType", UUIDCc, lambda: UUIDCc(UUID.randomUUID())),
                               ("getMovementStatesComponentType", MSCc, None), ("getVisibleComponentType", VISc, None),
                               ("getIntangibleComponentType", INTGc, lambda: INTGc.INSTANCE)):
        try:
            setf(em, EMc, gfield(EMN, getter_), regtype(cls_, cls_.class_.getSimpleName(), mk_))
        except Exception as e_:
            reg_errs.append("%s: %s" % (getter_, str(e_)[:120]))
    npc_t = reg_.registerComponent(NPCc.class_, Sup(lambda: None))
    c2t = HashMap()
    c2t.put(NPCc.class_, npc_t)
    setf(em, EMc, "classToComponentType", c2t)
    setf(em, JClass("com.hypixel.hytale.server.core.plugin.PluginBase"), "state", JClass("com.hypixel.hytale.server.core.plugin.PluginState").ENABLED)
    pr_t = reg_.registerComponent(PRc.class_, Sup(lambda: None))
    setf(uni, UNI, gfield("com.hypixel.hytale.server.core.universe.Universe", "getPlayerRefComponentType"), pr_t)
    ESMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    esmod = U.allocateInstance(ESMOD.class_)
    setf(esmod, ESMOD, "entityStatMapComponentType", reg_.registerComponent(ESMc.class_, Sup(lambda: ESMc())))
    jfield(ESMOD, "instance").set(None, esmod)
    DMOD_ = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule")
    dmod = U.allocateInstance(DMOD_.class_)
    setf(dmod, DMOD_, "deathComponentType", reg_.registerComponent(DTHc.class_, Sup(lambda: None)))
    jfield(DMOD_, "instance").set(None, dmod)
    DCSc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
    if DCSc.PROJECTILE is None:
        jfield(DCSc, "PROJECTILE").set(None, DCSc("Projectile"))
    check(not reg_errs and NPCc.getComponentType() is not None and PRc.getComponentType() is not None and ESMc.getComponentType() is not None
          and TPc.getComponentType() is not None and VELc.getComponentType() is not None,
          "N0: the engine component types the traversals read are registered like the modules do: %s" % reg_errs)
    tst = U.allocateInstance(TSt.class_)
    TBf.STORE = tst
    tbuf = U.allocateInstance(TBf.class_)
    world = U.allocateInstance(TWd.class_)
    setf(world, WLDc, "name", "trav-test")
    WCc = JClass("com.hypixel.hytale.server.core.universe.world.WorldConfig")
    wcfg = U.allocateInstance(WCc.class_)     # (its constructor needs the codec registry; the PvP flag is a plain field)
    setf(world, WLDc, "worldConfig", wcfg)
    es = U.allocateInstance(ESr.class_)
    setf(es, ESr, gfield("com.hypixel.hytale.server.core.universe.world.storage.EntityStore", "getWorld"), world)
    ebu = HashMap()
    setf(es, ESr, "entitiesByUuid", ebu)
    TSt.EXT = es
    TSt.RES.put(TRSc.getResourceType(), clock)
    MANA, STAM, HP = int(DST.getMana()), int(DST.getStamina()), int(DST.getHealth())

    def put(r_, t_, c_):
        tst.putComponent(r_, t_, c_)

    def comp(r_, t_):
        return tst.getComponent(r_, t_)

    def stats(mana=200.0, stam=10.0, hp=100.0):
        m_ = ESMc()
        m_.update()
        SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
        MT = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
        CT_ = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
        for i_, want_ in ((MANA, 500.0), (STAM, 20.0)):
            try:
                m_.putModifier(i_, "armorytest", SMO(MT.MAX, CT_.ADDITIVE, JFloat(want_)))
            except Exception:
                pass
        m_.setStatValue(MANA, JFloat(mana))
        m_.setStatValue(STAM, JFloat(stam))
        m_.setStatValue(HP, JFloat(hp))
        return m_

    def sv(m_, i_):
        return round(float(m_.get(i_).get()), 3)

    def player(i_, x, y, z, **kw):
        u_ = UUID.fromString("00000000-0000-0000-0011-%012d" % i_)
        r_ = REFc(tst, i_)
        pr_ = U.allocateInstance(PRc.class_)
        setf(pr_, PRc, "uuid", u_)
        setf(pr_, PRc, "entity", r_)
        setf(pr_, PRc, "username", "p%d" % i_)
        pbu.put(u_, pr_)
        ebu.put(u_, r_)
        put(r_, PRc.getComponentType(), pr_)
        put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, 0.0, 0.0)))
        put(r_, HRc.getComponentType(), HRc(R3(0.1, 0.2, 0.0)))
        m_ = stats(**kw)
        put(r_, ESMc.getComponentType(), m_)
        put(r_, VELc.getComponentType(), VELc())
        return u_, r_, pr_, m_

    def npc(i_, x, y, z):
        r_ = REFc(tst, i_)
        put(r_, NPCc.getComponentType(), TCc())
        put(r_, ESMc.getComponentType(), stats())
        put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, 0.0, 0.0)))
        return r_
    cu, rc, prc, mc = player(1, 0.5, 64.0, 0.5)
    check(sv(mc, MANA) == 200.0 and sv(mc, STAM) == 10.0, "N0: the caster's real EntityStatMap (vanilla stat types) holds 200 Mana / 10 Stamina: %s / %s (max %s / %s)" % (
        sv(mc, MANA), sv(mc, STAM), mc.get(MANA).getMax(), mc.get(STAM).getMax()))
    pu, rp, prp, mp = player(2, 2.5, 64.0, 0.5, hp=50.0)
    su, rs, prs, ms = player(3, 3.5, 64.0, 0.5, hp=50.0)
    n_on, n_off = npc(20, 3.0, 64.0, 0.5), npc(21, 3.0, 64.0, 6.0)

    @JImplements("java.util.function.Function")
    class Members:
        @JOverride
        def apply(self, o): return JArray(JObject)([str(pu)]) if str(o) == str(cu) else JArray(JObject)([])
    br.put("party:fn:members", Members())
    NEARL = []

    @JImplements("java.util.function.Function")
    class Near:
        @JOverride
        def apply(self, o):
            l_ = ArrayList()
            for r_ in NEARL:
                l_.add(r_)
            return l_
    AT.NEAR = Near()
    ACfg.TRAV_FX = False
    TW.ALL.clear()

    def events():
        out = []
        for e_ in list(TBf.EVENTS):
            d_ = e_[1]
            src_ = d_.getSource()
            out.append((int(e_[0].getIndex()), round(float(d_.getAmount()), 4), str(src_.getClass().getSimpleName()),
                        int(src_.getProjectile().getIndex()) if DPS.class_.isInstance(src_) and src_.getProjectile() is not None else None))
        return out

    def reset_buf():
        TBf.EVENTS.clear()
        TBf.ADDED.clear()
        TBf.REMOVED.clear()
        TWd.JOBS.clear()

    # --- N2. THE BLINK (TravJob kind 1 -> ArmoryTrav.blink): moves you, costs Mana + Stamina 2:1; a blink that does not move you is FREE
    AT.GRID = Grid(world_fn([wall6, lambda x, y, z: x == -1 and 64 <= y <= 66]))
    I_IRON = 2
    m1 = REFc(tst, 901)
    TJ(1, cu, "trav-test", tst, m1, JArray(JDouble)([1.0, 0.0, 0.0]), I_IRON).run()
    tp = comp(rc, TPc.getComponentType())
    tpos = None if tp is None else (round(float(tp.getPosition().x()), 4), round(float(tp.getPosition().y()), 4), round(float(tp.getPosition().z()), 4))
    tw = TW.of(tst)
    fx0 = None if tw is None or tw.fx.size() == 0 else tw.fx.get(tw.fx.size() - 1)
    check(tpos == (5.7, 64.0, 0.5) and tp is not None and not bool(tp.isResetVelocity()) and sv(mc, MANA) == 200.0 and sv(mc, STAM) == 0.0 and int(AT.BLINKS) == 1,
          "N2 (1.1 + 8): an Iron staff blink toward a wall at x 6 -> Teleport to (5.7, 64, 0.5) WITHOUT a velocity reset (keepFall), the chain's 30 Mana stays spent, "
          "Stamina 10 -> 0 (30 x 50%% = 15, cap 10): %s, Mana %s, Stamina %s, why %s" % (tpos, sv(mc, MANA), sv(mc, STAM), AT.LAST_WHY))
    check(fx0 is not None and int(fx0.kind) == 1 and fx0.marker == m1 and abs(float(fx0.amount) - 26.25) < 1e-9 and abs(float(fx0.r) - 0.75) < 1e-9
          and 2900 <= int(fx0.until) - nowms() <= 3100 and abs(float(fx0.ax) - 0.5) < 1e-9 and abs(float(fx0.bx) - 5.7) < 1e-6 and abs(float(fx0.ay) - 64.9) < 1e-9,
          "N2 (1.1): the light trail - the marker kept as its source, 26.25 per 0.5 s tick (175 x 30%/s), 1.5 wide, 3 s, from where you were to where you landed")
    # no move: facing the wall at x -1 -> NOTHING spent (Skyy 2026-10-05)
    put(rc, TPc.getComponentType(), None)
    mc.setStatValue(MANA, JFloat(100.0))
    mc.setStatValue(STAM, JFloat(10.0))
    r0 = int(AT.REFUNDS)
    m2 = REFc(tst, 902)
    TJ(1, cu, "trav-test", tst, m2, JArray(JDouble)([-1.0, 0.0, 0.0]), I_IRON).run()
    check(comp(rc, TPc.getComponentType()) is None and sv(mc, MANA) == 130.0 and sv(mc, STAM) == 10.0 and int(AT.REFUNDS) == r0 + 1
          and str(AT.LAST_WHY) == "no free spot ahead", "N2 (section 8): a blink that does not move you costs NOTHING - the 30 Mana come back (100 -> 130), "
                                                        "no Stamina taken, no teleport: Mana %s, Stamina %s, %s" % (sv(mc, MANA), sv(mc, STAM), AT.LAST_WHY))
    tw.run(tst, tbuf, nowms())
    check(m2 in list(TBf.REMOVED) and m1 not in list(TBf.REMOVED), "N2: the unused marker is removed on the next tick; the trail's marker stays")
    # too little Stamina -> no blink, Mana back
    mc.setStatValue(STAM, JFloat(4.0))
    TJ(1, cu, "trav-test", tst, REFc(tst, 903), JArray(JDouble)([1.0, 0.0, 0.0]), I_IRON).run()
    check(comp(rc, TPc.getComponentType()) is None and sv(mc, MANA) == 160.0 and sv(mc, STAM) == 4.0 and str(AT.LAST_WHY) == "too little Stamina",
          "N2 (section 8): 4 Stamina < 10 needed -> no blink, nothing spent (Mana back): %s / %s" % (sv(mc, MANA), sv(mc, STAM)))
    # Wood staff: 10 Mana + 5 Stamina (Skyy's example), the cap untouched
    mc.setStatValue(STAM, JFloat(10.0))
    TJ(1, cu, "trav-test", tst, REFc(tst, 904), JArray(JDouble)([0.0, 0.0, 1.0]), 0).run()
    check(comp(rc, TPc.getComponentType()) is not None and sv(mc, STAM) == 5.0, "N2 (section 8): a Wood staff blink costs 10 Mana + 5 Stamina (Skyy's 2:1 example): Stamina %s" % sv(mc, STAM))
    # cooldown row: inside it -> free; keepFall off -> the teleport resets the velocity; the void -> the last floored step
    ACfg.BLINK_CD = 5.0
    put(rc, TPc.getComponentType(), None)
    mc.setStatValue(STAM, JFloat(10.0))
    mana_b = sv(mc, MANA)
    TJ(1, cu, "trav-test", tst, REFc(tst, 905), JArray(JDouble)([0.0, 0.0, 1.0]), I_IRON).run()
    check(comp(rc, TPc.getComponentType()) is None and str(AT.LAST_WHY) == "cooldown" and sv(mc, MANA) == mana_b + 30.0 and sv(mc, STAM) == 10.0,
          "N2: blink.cooldown 5 s -> a blink inside it does nothing and costs nothing")
    ACfg.BLINK_CD = 0.0
    ACfg.BLINK_KEEPFALL = False
    AT.GRID = Grid(world_fn(floor_ok=lambda x, z: x <= 3))
    TJ(1, cu, "trav-test", tst, REFc(tst, 906), JArray(JDouble)([1.0, 0.0, 0.0]), 0).run()
    tp = comp(rc, TPc.getComponentType())
    check(tp is not None and bool(tp.isResetVelocity()) and round(float(tp.getPosition().x()), 4) == 3.5,
          "N2 (4): over the void the blink stops at the last spot with ground (x 3.5); blink.keepFall off -> the teleport resets the velocity: %s" % (
              None if tp is None else tp.getPosition()))
    ACfg.BLINK_KEEPFALL = True
    # SkyyClasses' weapon lock: a class that may not use the staff gets no blink (and pays nothing)
    @JImplements("java.util.function.Function")
    class Deny:
        @JOverride
        def apply(self, o): return JClass("java.lang.Boolean").FALSE
    put(rc, TPc.getComponentType(), None)
    br.put("class:fn:allowed", Deny())
    AT.GRID = Grid(world_fn())
    mc.setStatValue(STAM, JFloat(10.0))
    mana_l = sv(mc, MANA)
    TJ(1, cu, "trav-test", tst, REFc(tst, 907), JArray(JDouble)([1.0, 0.0, 0.0]), 0).run()
    lock_why = str(AT.LAST_WHY)
    lock_tp = comp(rc, TPc.getComponentType())
    lock_cost = (sv(mc, MANA) - mana_l, sv(mc, STAM))
    br.remove("class:fn:allowed")
    # the hand item is read through InventoryComponent.getItemInHand (null here = no item = allowed): the lock answers only for an item
    br.put("class:fn:allowed", Deny())
    deny_ = (bool(AT.allowed(cu, "Weapon_Staff_Iron")), bool(AT.allowed(cu, None)))
    br.remove("class:fn:allowed")
    check(lock_tp is None and lock_why == "class lock" and lock_cost == (10.0, 10.0) and deny_ == (False, True) and bool(AT.allowed(cu, "Weapon_Staff_Iron")),
          "N2 (trav-fix): SkyyClasses' class:fn:allowed (Object[]{UUID, itemId} -> Boolean) is asked for the CAST staff (Weapon_Staff_Wood), not only the hand "
          "(empty here) - a locked class gets no blink and pays nothing (the 10 Mana back, Stamina kept): %s / %s / %s" % (deny_, lock_why, lock_cost))
    print("N2. blink: wall 5.7 (keep fall), 2:1 Stamina with the cap, no-move / short Stamina / cooldown = FREE, void -> last floored step, keepFall off")

    # --- N3. the trail ticks (TravTick -> TravWorld.run): enemies on the line only; party never; strangers only with PvP on + trav.players
    reset_buf()
    for k_ in range(tw.fx.size() - 1, -1, -1):
        if tw.fx.get(k_).marker != m1:
            tw.fx.subList(k_, k_ + 1).clear()
    fx1 = tw.fx.get(0)
    NEARL[:] = [n_on, n_off, rp, rs, rc]
    fx1.next = 0
    tw.run(tst, tbuf, nowms())
    ev = events()
    check(ev == [(20, 26.25, "ProjectileSource", 901)], "N3 (1.1 + 1.3): PvP off - one tick hits only the NPC standing in the line, 26.25 through "
                                                         "Damage$ProjectileSource(caster, marker); the NPC 6 blocks aside, the party member, the stranger and the caster nothing: %s" % ev)
    reset_buf()
    tw.run(tst, tbuf, nowms())
    check(events() == [], "N3: the next tick waits blink.tick (0.5 s) - no double hit inside a tick")
    wcfg.setPvpEnabled(True)
    fx1.next = 0
    tw.run(tst, tbuf, nowms())
    ev_pvp = sorted(events())
    ACfg.TRAV_PLAYERS = False
    reset_buf()
    fx1.next = 0
    tw.run(tst, tbuf, nowms())
    ev_np = sorted(events())
    ACfg.TRAV_PLAYERS = True
    check(ev_pvp == [(3, 26.25, "ProjectileSource", 901), (20, 26.25, "ProjectileSource", 901)] and ev_np == [(20, 26.25, "ProjectileSource", 901)],
          "N3 (2.7 + 1.3): PvP on - the stranger in the line is hit too, the party member never; trav.players off - players never: %s / %s" % (ev_pvp, ev_np))
    wcfg.setPvpEnabled(False)
    reset_buf()
    fx1.until = nowms() - 1
    tw.run(tst, tbuf, nowms())
    check(m1 in list(TBf.REMOVED) and tw.fx.size() == 0, "N3: after blink.trailSeconds the trail ends and its marker is removed (REMOVE)")
    print("N3. trail: line-only hits, 0.5 s ticks, PvP / party / trav.players rules, marker removed at the end")

    # --- N4. THE HOP (TravJob kind 2 -> ArmoryTrav.hop): Set velocity opposite to the look, the dagger dash's config, Stamina 2:1
    def last_instr(r_):
        v_ = comp(r_, VELc.getComponentType())
        ins = list(v_.getInstructions())
        if not ins:
            return None
        o_ = ins[-1]
        vec, typ, cfg_ = None, None, None
        for f_ in o_.getClass().getDeclaredFields():
            f_.setAccessible(True)
            x_ = f_.get(o_)
            if V3.class_.isInstance(x_):
                vec = (round(float(x_.x()), 4), round(float(x_.y()), 4), round(float(x_.z()), 4))
            elif x_ is not None and str(x_.getClass().getSimpleName()) == "ChangeVelocityType":
                typ = str(x_)
            elif x_ is not None and str(x_.getClass().getSimpleName()) == "VelocityConfig":
                cfg_ = (round(float(x_.getAirResistance()), 3), round(float(x_.getGroundResistance()), 3), round(float(x_.getThreshold()), 3), str(x_.getStyle()))
        return vec, typ, cfg_, len(ins)
    AT.GRID = Grid(world_fn())
    mc.setStatValue(STAM, JFloat(10.0))
    TJ(2, cu, "trav-test", tst, None, JArray(JDouble)([0.0, 0.0, 1.0]), I_IRON).run()
    h1 = last_instr(rc)
    check(h1 is not None and h1[0] == (0.0, 0.0, -13.0) and h1[1] == "Set" and h1[2] == (0.97, 0.94, 5.0, "Exp") and sv(mc, STAM) == 2.5,
          "N4 (1.2 + 2.3): an Iron wand hop looking level -> Velocity instruction (0, 0, -13) Set with the dagger dash's config; Stamina 10 -> 2.5 (15 x 50%%): %s, %s" % (
              h1, sv(mc, STAM)))
    TJ(2, cu, "trav-test", tst, None, JArray(JDouble)([0.0, -1.0, 0.0]), 0).run()
    h2 = last_instr(rc)
    check(h2 is not None and h2[0] == (0.0, 13.0, 0.0) and sv(mc, STAM) == 0.0, "N4 (LOCKED 2026-10-04): look down = straight up (0, 13, 0); Wood wand 5 Mana + 2.5 Stamina: %s / %s" % (h2, sv(mc, STAM)))
    TJ(2, cu, "trav-test", tst, None, JArray(JDouble)([0.0, 0.0, 1.0]), I_IRON).run()
    h3 = last_instr(rc)
    check(h3 is not None and h3[3] == h2[3], "N4 (section 8): too little Stamina -> no hop (the orb flew anyway): %s instructions" % (None if h3 is None else h3[3]))
    mc.setStatValue(STAM, JFloat(10.0))
    AT.GRID = Grid(lambda x, y, z: 0)
    TJ(2, cu, "trav-test", tst, None, JArray(JDouble)([0.0, 0.0, 1.0]), I_IRON).run()
    h4 = last_instr(rc)
    check(h4 is not None and h4[0] == (0.0, 0.0, -6.5) and str(AT.LAST_WHY).startswith("hop half"), "N4 (4): no ground 3 blocks behind -> half the hop: %s" % (h4,))
    ACfg.HOP_FORCE = 0.0
    mc.setStatValue(STAM, JFloat(10.0))
    TJ(2, cu, "trav-test", tst, None, JArray(JDouble)([0.0, 0.0, 1.0]), I_IRON).run()
    check(last_instr(rc)[3] == h4[3] and sv(mc, STAM) == 10.0, "N4: hop.force 0 = no hop and no Stamina")
    ACfg.HOP_FORCE = 13.0
    AT.GRID = Grid(world_fn())
    # trav-fix (critic): falling faster than MinFallSpeedToEngageRoll (21; the stand-in world has no MovementConfig -> the vanilla 21) the
    # hop keeps the fall - the Set velocity's y is the client fall speed, never 0 / up
    vel_ = comp(rc, VELc.getComponentType())
    vel_.setClient(0.0, -30.0, 0.0)
    mc.setStatValue(STAM, JFloat(10.0))
    TJ(2, cu, "trav-test", tst, None, JArray(JDouble)([0.0, 0.0, 1.0]), I_IRON).run()
    hf1, why_f1 = last_instr(rc), str(AT.LAST_WHY)
    mc.setStatValue(STAM, JFloat(10.0))
    TJ(2, cu, "trav-test", tst, None, JArray(JDouble)([0.0, -1.0, 0.0]), I_IRON).run()
    hf2 = last_instr(rc)
    vel_.setClient(0.0, -10.0, 0.0)
    mc.setStatValue(STAM, JFloat(10.0))
    TJ(2, cu, "trav-test", tst, None, JArray(JDouble)([0.0, -1.0, 0.0]), I_IRON).run()
    hf3 = last_instr(rc)
    vel_.setClient(0.0, 0.0, 0.0)
    check(hf1[0] == (0.0, -30.0, -13.0) and why_f1.endswith("fall kept") and hf2[0] == (0.0, -30.0, 0.0) and hf3[0] == (0.0, 13.0, 0.0)
          and abs(float(AT.maxFall(world)) - 21.0) < 1e-9,
          "N4 (trav-fix, Double-Jump rule 7): falling at 30 b/s the hop keeps the fall (level: (0, -30, -13); look down: (0, -30, 0) - no fall-damage "
          "escape); a 10 b/s fall hops normally (0, 13, 0): %s / %s / %s" % (hf1, hf2, hf3))

    @JImplements("java.util.function.Function")
    class DenyId:
        def __init__(self, item): self.item = item
        @JOverride
        def apply(self, o):
            a_ = list(o)
            return JClass("java.lang.Boolean").FALSE if str(a_[1]) == self.item else JClass("java.lang.Boolean").TRUE
    br.put("class:fn:allowed", DenyId(WID["Iron"]))
    mc.setStatValue(STAM, JFloat(10.0))
    n_ins = last_instr(rc)[3]
    TJ(2, cu, "trav-test", tst, None, JArray(JDouble)([0.0, 0.0, 1.0]), I_IRON).run()
    hop_lock = (last_instr(rc)[3], str(AT.LAST_WHY), sv(mc, STAM))
    br.remove("class:fn:allowed")
    check(hop_lock == (n_ins, "hop: class lock", 10.0), "N4 (trav-fix): a class locked out of the CAST wand (Weapon_Wand_Iron; the hand is empty) gets no hop "
                                                        "and pays no Stamina: %s" % (hop_lock,))
    print("N4. hop: level back, down = up, half without ground, Stamina 2:1, short Stamina / force 0 = no hop, a damaging fall kept, cast-wand lock")

    # --- N5. SPAWN hook (ArmoryTravSys -> ArmoryTrav.added) on REAL ProjectileComponents after initialize + shoot
    def launched(pid, ref_i, x, y, z, yaw=-1.5707964, pitch=0.0):
        h_ = reg_.newHolder()
        pc_ = LPCc(pid)
        h_.putComponent(LPCc.getComponentType(), pc_)
        pc_.initialize()
        pc_.shoot(h_, cu, x, y, z, JFloat(yaw), JFloat(pitch))
        r_ = REFc(tst, ref_i)
        put(r_, LPCc.getComponentType(), pc_)
        put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, 0.0, 0.0)))
        return r_, pc_
    reset_buf()
    TW.ALL.clear()
    ob1, opc1 = launched(ORB["Iron"], 950, 0.5, 65.5, 0.5)
    AT.added(ob1, opc1, int(ADefs.pidCode(ORB["Iron"])), tst, tbuf)
    tw = TW.of(tst)
    jobs = list(TWd.JOBS)
    check(tw is not None and tw.orbs.containsKey(ob1) and len(jobs) == 1 and int(jobs[0].kind) == 2 and abs(float(jobs[0].dir[0]) - 1.0) < 1e-4
          and int(jobs[0].idx) == 2, "N5 (2.3): a wand charged orb's SPAWN -> a burst record + ONE hop job on the world thread, direction = the launch velocity (+x): %s" % (
              [(int(j.kind), [round(float(x), 3) for x in j.dir]) for j in jobs]))
    bm, bpc = launched(BLINK["Iron"], 951, 0.5, 65.5, 0.5)
    v_before = ASp.launchVelocity(bpc.getSimplePhysicsProvider())
    vb = None if v_before is None else (round(float(v_before.x()), 3), round(float(v_before.y()), 3), round(float(v_before.z()), 3))
    reset_buf()
    AT.added(bm, bpc, int(ADefs.pidCode(BLINK["Iron"])), tst, tbuf)
    v_after = ASp.launchVelocity(bpc.getSimplePhysicsProvider())
    jobs = list(TWd.JOBS)
    check(vb == (30.0, 0.0, 0.0) and v_after is not None and float(v_after.x()) == 0.0 and len(jobs) == 1 and int(jobs[0].kind) == 1 and jobs[0].marker == bm
          and abs(float(jobs[0].dir[0]) - 1.0) < 1e-4 and not list(TBf.REMOVED), "N5 (2.2): the blink marker's SPAWN -> its launch velocity %s is zeroed (it stays where it was cast) "
                                                                                  "and ONE blink job carries it + the direction" % (vb,))
    ACfg.STAFF_MODE = "orb"
    bm2, bpc2 = launched(BLINK["Iron"], 952, 0.5, 65.5, 0.5)
    reset_buf()
    AT.added(bm2, bpc2, int(ADefs.pidCode(BLINK["Iron"])), tst, tbuf)
    added_ = list(TBf.ADDED)
    sp_pid = None if not added_ else str(added_[0][0].getComponent(LPCc.getComponentType()).getProjectileAssetName())
    sp_cr = None if not added_ else str(added_[0][0].getComponent(LPCc.getComponentType()).getCreatorUuid())
    check(sp_pid == SORB["Iron"] and sp_cr == str(cu) and bm2 in list(TBf.REMOVED) and not list(TWd.JOBS),
          "N5 (2.2): staff.mode orb -> the 0.1 charged orb %s is launched from the marker (assembleDefaultProjectile + shoot, creator = the caster) and the marker removed: %s %s" % (
              SORB["Iron"], sp_pid, sp_cr))
    ACfg.STAFF_MODE = "blink"
    ACfg.PART_TRAV = False
    bm3, bpc3 = launched(BLINK["Wood"], 953, 0.5, 65.5, 0.5)
    reset_buf()
    AT.added(bm3, bpc3, int(ADefs.pidCode(BLINK["Wood"])), tst, tbuf)
    added_ = list(TBf.ADDED)
    check(len(added_) == 1 and str(added_[0][0].getComponent(LPCc.getComponentType()).getProjectileAssetName()) == SORB["Wood"] and bm3 in list(TBf.REMOVED),
          "N5: part.trav off -> the staff hold is the 0.1 charged orb again")
    reset_buf()
    ob_off, opc_off = launched(ORB["Copper"], 954, 0.5, 65.5, 0.5)
    AT.added(ob_off, opc_off, int(ADefs.pidCode(ORB["Copper"])), tst, tbuf)
    check(not list(TWd.JOBS), "N5: part.trav off -> no hop")
    ACfg.PART_TRAV = True
    T2_ = JClass("com.hypixel.hytale.math.vector.Transform")
    # spawn() mirrors LaunchProjectileInteraction#firstRun (spec 2.6 / T2): the same engine steps in the same order
    def calls_of(cls, meth):
        cc_ = CPj.get(cls)
        m_ = [x for x in cc_.getDeclaredMethods() if str(x.getName()) == meth][0]
        it_ = m_.getMethodInfo().getCodeAttribute().iterator()
        cp_ = m_.getMethodInfo().getConstPool()
        out = []
        while it_.hasNext():
            p_ = it_.next()
            if it_.byteAt(p_) in (0xb6, 0xb7, 0xb8, 0xb9):
                t_ = cp_.getTag(it_.u16bitAt(p_ + 1))
                nm_ = str(cp_.getInterfaceMethodrefName(it_.u16bitAt(p_ + 1))) if t_ == CPool.CONST_InterfaceMethodref else str(cp_.getMethodrefName(it_.u16bitAt(p_ + 1)))
                out.append(nm_)
        return out
    STEPS = ["assembleDefaultProjectile", "ensureComponent", "initialize", "shoot", "addEntity"]
    fr = [x for x in calls_of("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.LaunchProjectileInteraction", "firstRun") if x in STEPS]
    sp_ = [x for x in calls_of(PKG + "ArmoryTrav", "spawn") if x in STEPS]
    adp = calls_of("com.hypixel.hytale.server.core.entity.entities.ProjectileComponent", "assembleDefaultProjectile")
    check(fr == STEPS and sp_ == STEPS, "N5 (T2): ArmoryTrav.spawn makes the engine calls of LaunchProjectileInteraction#firstRun in its order %s (firstRun: %s)" % (sp_, fr))
    print("N5. T2: assembleDefaultProjectile puts / ensures: %s" % [x for x in adp if x in ("putComponent", "ensureComponent", "ensureAndGetComponent")])
    print("N5. SPAWN hook: hop job, marker stopped + blink job, orb mode / part off -> the 0.1 orb from the marker, spawn() = firstRun's steps")

    # --- N6. THE BURST + HEAL ORB (ArmoryHitSys -> ArmoryTrav.landed) + the miss burst (ArmoryTravSys.onEntityRemove -> removed)
    reset_buf()
    n_dir, n_near = npc(30, 6.0, 64.0, 0.5), npc(31, 8.0, 64.0, 0.5)
    NEARL[:] = [n_dir, n_near, rp, rs, rc]
    d_hit = DMGc(DPS(rc, ob1), DCSc.PROJECTILE, JFloat(88.0))
    d_hit.setAmount(JFloat(70.0))         # after armour / tune: the heal orb uses the LANDED damage, the burst the initial one
    AT.landed(tst, tbuf, d_hit, ob1, int(ADefs.pidCode(ORB["Iron"])), n_dir)
    ev = events()
    hfx = [tw.fx.get(k_) for k_ in range(tw.fx.size()) if int(tw.fx.get(k_).kind) == 2]
    check(ev == [(31, 52.8, "ProjectileSource", 950)] and len(hfx) == 1 and abs(float(hfx[0].amount) - 14.0) < 1e-9 and abs(float(hfx[0].r) - 9.0) < 1e-9
          and 3400 <= int(hfx[0].until) - nowms() <= 3600, "N6 (1.2 + 2.4): the orb's direct hit (88 initial, 70 landed) -> every OTHER enemy within 6 takes 60%% of 88 = 52.8 "
                                                            "through Damage$ProjectileSource(caster, orb) - not the direct target, not the party member / stranger / caster; a 9-block "
                                                            "heal orb for 3.5 s healing 20%% of 70 = 14 per 1 s tick: %s / %s" % (ev, [float(f.amount) for f in hfx]))
    reset_buf()
    AT.landed(tst, tbuf, d_hit, ob1, int(ADefs.pidCode(ORB["Iron"])), n_near)
    check(events() == [] and len([1 for k_ in range(tw.fx.size()) if int(tw.fx.get(k_).kind) == 2]) == 1, "N6: one burst per orb (a second hit of the same orb bursts nothing)")
    # the burst hits are ours (MINE): ArmoryHitSys never bursts on them
    HS = JClass(PKG + "ArmoryHitSys")()
    reset_buf()
    AT.landed(tst, tbuf, DMGc(DPS(rc, ob1), DCSc.PROJECTILE, JFloat(88.0)), ob1, 2002, n_dir)
    # PvP on: the stranger becomes an enemy (burst) - a fresh orb
    ob2, opc2 = launched(ORB["Iron"], 960, 0.5, 65.5, 0.5)
    AT.added(ob2, opc2, 2002, tst, tbuf)
    wcfg.setPvpEnabled(True)
    reset_buf()
    AT.landed(tst, tbuf, DMGc(DPS(rc, ob2), DCSc.PROJECTILE, JFloat(88.0)), ob2, 2002, n_dir)
    ev_p = sorted(events())
    wcfg.setPvpEnabled(False)
    check(ev_p == [(3, 52.8, "ProjectileSource", 960), (31, 52.8, "ProjectileSource", 960)], "N6 (2.7): PvP on -> the stranger is an enemy (burst), the party member never: %s" % ev_p)
    # the heal orb ticks: caster + party 100%, other non-hostile players 50%, enemies (PvP) none - through class:fn:heal
    for k_ in range(tw.fx.size() - 1, -1, -1):
        if int(tw.fx.get(k_).kind) != 2:
            tw.fx.subList(k_, k_ + 1).clear()
    while tw.fx.size() > 1:
        tw.fx.subList(tw.fx.size() - 1, tw.fx.size()).clear()
    hf = tw.fx.get(0)
    reset_buf()
    hf.next = 0
    tw.run(tst, tbuf, nowms())
    hj = [j for j in list(TWd.JOBS) if str(j.getClass().getSimpleName()) == "TravHeal"]
    split = None if len(hj) != 1 else sorted((str(u_)[-2:], round(float(h_), 3)) for u_, h_ in zip(list(hj[0].who), list(hj[0].hp)))
    check(split == [("01", 14.0), ("02", 14.0), ("03", 7.0)] and str(hj[0].healer) == str(cu),
          "N6 (section 8): a heal orb tick heals EVERYONE non-hostile inside - the Priest + the party member 100%% (14), the stranger 50%% (7), the NPCs nothing: %s" % split)
    hp_before = sv(mp, HP)
    hj[0].run()
    check(sv(mp, HP) == round(hp_before + 14.0, 3) and sv(ms, HP) == round(50.0 + 7.0, 3), "N6 (2.5): without SkyyClasses Armory splits itself and heals straight "
                                                                                          "into Health (no XP): party %s -> %s, stranger 50 -> %s" % (hp_before, sv(mp, HP), sv(ms, HP)))
    CALLS = []

    @JImplements("java.util.function.Function")
    class Heal:
        @JOverride
        def apply(self, o):
            a_ = list(o)
            CALLS.append((str(a_[0]), str(a_[1]), str(a_[2].getClass().getName()), round(float(a_[2]), 3), str(a_[3]), len(a_), str(a_[4]) if len(a_) > 4 else None))
            return JClass("java.lang.Double")(float(a_[2]))
    br.put("class:fn:heal", Heal())
    reset_buf()
    hf.next = 0
    tw.run(tst, tbuf, nowms())
    hjc = [j for j in list(TWd.JOBS) if str(j.getClass().getSimpleName()) == "TravHeal"]
    h0 = float(AT.HEALED)
    if hjc:
        hjc[0].run()
    br.remove("class:fn:heal")
    W_I = WID["Iron"]
    check(sorted(CALLS) == sorted([(str(cu), str(cu), "java.lang.Double", 14.0, "armory:orb", 5, W_I), (str(cu), str(pu), "java.lang.Double", 14.0, "armory:orb", 5, W_I),
                                   (str(cu), str(su), "java.lang.Double", 14.0, "armory:orb", 5, W_I)]) and abs(float(AT.HEALED) - h0 - 42.0) < 1e-6,
          "N6 (bridge contract, SkyyClasses 0.1.12): with class:fn:heal present Armory passes EVERY non-hostile player the party amount (14) and lets SkyyClasses "
          "split party / others (its priestHeal.othersPercent - never twice): Object[]{UUID healer, UUID target, Double hp, \"armory:orb\", the casting wand id}; "
          "its Double answer counts: %s" % CALLS)
    wcfg.setPvpEnabled(True)
    reset_buf()
    hf.next = 0
    tw.run(tst, tbuf, nowms())
    hj2 = [j for j in list(TWd.JOBS) if str(j.getClass().getSimpleName()) == "TravHeal"]
    split2 = None if len(hj2) != 1 else sorted(str(u_)[-2:] for u_ in list(hj2[0].who))
    wcfg.setPvpEnabled(False)
    ACfg.ORB_OTHERS_PCT = 0
    reset_buf()
    hf.next = 0
    tw.run(tst, tbuf, nowms())
    hj3 = [j for j in list(TWd.JOBS) if str(j.getClass().getSimpleName()) == "TravHeal"]
    split3 = None if len(hj3) != 1 else sorted(str(u_)[-2:] for u_ in list(hj3[0].who))
    ACfg.ORB_OTHERS_PCT = 50

    @JImplements("java.util.function.Function")
    class AllyAll:
        @JOverride
        def apply(self, o): return JClass("java.lang.Boolean").TRUE
    br.put("class:fn:ally", AllyAll())
    reset_buf()
    hf.next = 0
    tw.run(tst, tbuf, nowms())
    hj4 = [j for j in list(TWd.JOBS) if str(j.getClass().getSimpleName()) == "TravHeal"]
    split4 = None if len(hj4) != 1 else sorted((str(u_)[-2:], round(float(h_), 3)) for u_, h_ in zip(list(hj4[0].who), list(hj4[0].hp)))
    br.remove("class:fn:ally")
    check(split2 == ["01", "02"] and split3 == ["01", "02"] and split4 == [("01", 14.0), ("02", 14.0), ("03", 14.0)],
          "N6: PvP on -> the stranger is an enemy and is not healed; orb.othersPercent 0 -> party only; class:fn:ally (Object[]{UUID a, UUID b} -> Boolean) "
          "decides who is party: %s / %s / %s" % (split2, split3, split4))
    # the miss: an orb removed (REMOVE) without a direct hit bursts where it ended - asset damage x tune, Damage$EntitySource(caster)
    ob3, opc3 = launched(ORB["Iron"], 970, 0.5, 65.5, 0.5)
    AT.added(ob3, opc3, 2002, tst, tbuf)
    put(ob3, TCc.getComponentType(), TCc(V3(9.0, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    reset_buf()
    n_fx = tw.fx.size()
    AT.removed(ob3, True, tst, tbuf)
    ev_m = sorted(events())
    check(ev_m == [(30, 52.8, "EntitySource", None), (31, 52.8, "EntitySource", None)]
          and tw.fx.size() == n_fx + 1 and abs(float(tw.fx.get(tw.fx.size() - 1).amount) - 17.6) < 1e-9 and not tw.orbs.containsKey(ob3),
          "N6 (2.4 miss): an Iron orb ending on a block bursts there - 60%% of its 88 asset damage x tune 100%% through Damage$EntitySource(caster) on every enemy around, "
          "a heal orb of 20%% of 88 = 17.6 per tick: %s" % ev_m)
    ob4, opc4 = launched(ORB["Iron"], 971, 0.5, 65.5, 0.5)
    AT.added(ob4, opc4, 2002, tst, tbuf)
    reset_buf()
    AT.removed(ob4, False, tst, tbuf)
    AT.removed(ob1, True, tst, tbuf)
    check(events() == [], "N6: an orb that already burst (direct hit) or that unloads (not REMOVE) never bursts on removal")
    # trav-fix (critic): the miss burst (Damage$EntitySource - SkyyClasses' DamageLock would judge the hand) checks the CAST wand's class lock
    ob5, opc5 = launched(ORB["Iron"], 972, 0.5, 65.5, 0.5)
    AT.added(ob5, opc5, 2002, tst, tbuf)
    put(ob5, TCc.getComponentType(), TCc(V3(9.0, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    br.put("class:fn:allowed", DenyId(WID["Iron"]))
    reset_buf()
    n_fx5 = tw.fx.size()
    AT.removed(ob5, True, tst, tbuf)
    burst_lock = (events(), tw.fx.size() - n_fx5, str(AT.LAST_WHY))
    br.remove("class:fn:allowed")
    check(burst_lock == ([], 0, "burst: class lock"), "N6 (trav-fix): a class locked out of the cast wand gets no miss burst and no heal orb: %s" % (burst_lock,))

    # trav-fix (critic): SkyyClasses present (class:fn:allowed) but older than 0.1.12 (no class:fn:heal) -> the heal orb heals nobody (never the
    # uncapped direct heal); no SkyyClasses at all -> the direct heal above
    @JImplements("java.util.function.Function")
    class AllowAll:
        @JOverride
        def apply(self, o): return JClass("java.lang.Boolean").TRUE
    br.put("class:fn:allowed", AllowAll())
    hp_o = sv(mp, HP)
    h_old = TH(cu, JArray(UUID)([pu]), JArray(JDouble)([5.0]), tst, WID["Iron"])
    h_old.run()
    old_cls = (sv(mp, HP) - hp_o, str(AT.LAST_WHY))
    br.remove("class:fn:allowed")
    h_none = TH(cu, JArray(UUID)([pu]), JArray(JDouble)([5.0]), tst, WID["Iron"])
    h_none.run()
    check(old_cls == (0.0, "heal orb: SkyyClasses too old") and sv(mp, HP) == round(hp_o + 5.0, 3),
          "N6 (trav-fix): SkyyClasses 0.1.11 (class:fn:allowed, no class:fn:heal) -> the heal orb heals nobody (+%s); no SkyyClasses -> Health +5 (%s -> %s)" % (
              old_cls, hp_o, sv(mp, HP)))
    print("N6. burst: others 60%, not the direct target / allies, once per orb, PvP stranger; heal orb split 100/50 via class:fn:heal (contract) or Health; miss burst")

    # --- N7. PIERCE (ArmoryHitSys -> landed, quick wand orb) + the "never twice" rule (ArmoryTuneSys.repeatHit) + the ranges (TravTick)
    reset_buf()
    TW.ALL.clear()
    q1, qpc1 = launched(QORB["Iron"], 980, 0.5, 65.0, 0.5)
    AT.added(q1, qpc1, int(ADefs.pidCode(QORB["Iron"])), tst, tbuf)
    tw = TW.of(tst)
    s1 = tw.quick.get(q1)
    nA, nB = npc(40, 5.5, 64.0, 0.5), npc(41, 9.5, 64.0, 0.5)
    dq = DMGc(DPS(rc, q1), DCSc.PROJECTILE, JFloat(18.0))
    dq.putMetaObject(DMGc.HIT_LOCATION, V4(5.5, 65.0, 0.5, 1.0))
    AT.landed(tst, tbuf, dq, q1, int(ADefs.pidCode(QORB["Iron"])), nA)
    added_ = list(TBf.ADDED)
    cont = None
    if added_:
        h_ = added_[0][0]
        pcn = h_.getComponent(LPCc.getComponentType())
        tcn = h_.getComponent(TCc.getComponentType())
        cont = (str(pcn.getProjectileAssetName()), str(pcn.getCreatorUuid()), None if tcn is None else round(float(tcn.getPosition().x()), 2))
    check(s1 is not None and abs(float(s1.range) - 16.0) < 1e-9 and cont is not None and cont[0] == QORB["Iron"] and cont[1] == str(cu) and cont[2] > 6.0
          and tw.pend.size() == 1 and int(AT.PIERCES) >= 1,
          "N7 (1.2 + 2.6): a wand quick orb hitting an enemy -> a continuation of the same orb past it (assembleDefaultProjectile + shoot, creator = the caster, "
          "past x 6): %s" % (cont,))
    nref = added_[0][1] if added_ else None
    if nref is not None:
        put(nref, TCc.getComponentType(), TCc(V3(7.0, 65.0, 0.5), R3(0.0, 0.0, 0.0)))
        AT.added(nref, pcn, int(ADefs.pidCode(QORB["Iron"])), tst, tbuf)
    s2 = None if nref is None else tw.quick.get(nref)
    check(s2 is not None and abs(float(s2.sx) - 0.5) < 1e-9 and s2.hits.contains(nA) and bool(AT.repeatHit(tst, nref, nA, QORB["Iron"]))
          and not bool(AT.repeatHit(tst, nref, nB, QORB["Iron"])) and tw.pend.size() == 0,
          "N7 (section 8): the continuation keeps the first launch's start (the range counts from there) and the chain's hit set - the enemy it already hit is "
          "cancelled (ArmoryTuneSys), the next one is not")
    # the two damage systems on a real dispatch shape (a chunk whose getReferenceTo answers the target): ArmoryTuneSys (Filter) cancels
    # the chain's repeat hit, ArmoryHitSys (Inspect) turns a landed quick-orb hit into the next continuation
    TCh = stub("TChunk", CP_ + "ArchetypeChunk", ["public static " + CP_ + "Ref TARGET = null;"],
               ["public " + CP_ + "Ref getReferenceTo(int i) { return TARGET; }"])
    chunk = U.allocateInstance(TCh.class_)
    if nref is not None:
        put(nref, LPCc.getComponentType(), pcn)
    TCh.TARGET = nA
    d_rep = DMGc(DPS(rc, nref), DCSc.PROJECTILE, JFloat(18.0))
    tsys.handle(0, chunk, tst, tbuf, d_rep)
    TCh.TARGET = nB
    d_new = DMGc(DPS(rc, nref), DCSc.PROJECTILE, JFloat(18.0))
    tsys.handle(0, chunk, tst, tbuf, d_new)
    reset_buf()
    HS.handle(0, chunk, tst, tbuf, d_new)
    hs_added = len(list(TBf.ADDED))
    check(bool(d_rep.isCancelled()) and not bool(d_new.isCancelled()) and float(d_new.getAmount()) == 18.0 and hs_added == 1,
          "N7 (dispatch): ArmoryTuneSys.handle CANCELS the chain's hit on the enemy it already hit and leaves a new enemy's hit alone (18); ArmoryHitSys.handle "
          "on that landed hit launches the next continuation: %s / %s / %s" % (bool(d_rep.isCancelled()), float(d_new.getAmount()), hs_added))
    # no cap by default: the continuation's hit pierces again; pierce.max 1 stops after the first enemy
    reset_buf()
    dq2 = DMGc(DPS(rc, nref), DCSc.PROJECTILE, JFloat(18.0))
    dq2.putMetaObject(DMGc.HIT_LOCATION, V4(9.5, 65.0, 0.5, 1.0))
    AT.landed(tst, tbuf, dq2, nref, 1002, nB)
    again = len(list(TBf.ADDED))
    ACfg.PIERCE_MAX = 1
    reset_buf()
    q2, qpc2 = launched(QORB["Iron"], 981, 0.5, 65.0, 0.5)
    AT.added(q2, qpc2, 1002, tst, tbuf)
    dq3 = DMGc(DPS(rc, q2), DCSc.PROJECTILE, JFloat(18.0))
    dq3.putMetaObject(DMGc.HIT_LOCATION, V4(5.5, 65.0, 0.5, 1.0))
    AT.landed(tst, tbuf, dq3, q2, 1002, nA)
    first_c = list(TBf.ADDED)
    capped = [len(first_c), None]
    if first_c:
        c_ref, c_pc = first_c[0][1], first_c[0][0].getComponent(LPCc.getComponentType())
        put(c_ref, TCc.getComponentType(), TCc(V3(7.0, 65.0, 0.5), R3(0.0, 0.0, 0.0)))
        AT.added(c_ref, c_pc, 1002, tst, tbuf)
        reset_buf()
        dq5 = DMGc(DPS(rc, c_ref), DCSc.PROJECTILE, JFloat(18.0))
        dq5.putMetaObject(DMGc.HIT_LOCATION, V4(9.5, 65.0, 0.5, 1.0))
        AT.landed(tst, tbuf, dq5, c_ref, 1002, nB)
        capped[1] = len(list(TBf.ADDED))
    ACfg.PIERCE_MAX = 0
    reset_buf()
    dq4 = DMGc(DPS(rc, q2), DCSc.PROJECTILE, JFloat(18.0))
    dq4.putMetaObject(DMGc.HIT_LOCATION, V4(15.9, 65.0, 0.5, 1.0))
    tw.quick.get(q2).count = 0
    AT.landed(tst, tbuf, dq4, q2, 1002, nB)
    past_range = len(list(TBf.ADDED))
    check(again == 1 and capped == [1, 0] and past_range == 0, "N7: pierce.max 0 = no cap (the 2nd enemy pierces too), pierce.max 1 = through ONE enemy (the 2nd hit ends it); never past "
                                                          "the 16-block range: %s / %s / %s" % (again, capped, past_range))
    # the ranges: TravTick removes quick orbs past quick.range.* (wand 16, staff 24) - measured from the first launch
    sq, spc = launched(SQORB["Iron"], 982, 0.5, 65.0, 0.5)
    AT.added(sq, spc, int(ADefs.pidCode(SQORB["Iron"])), tst, tbuf)
    reset_buf()
    put(q2, TCc.getComponentType(), TCc(V3(15.0, 65.0, 0.5), R3(0.0, 0.0, 0.0)))
    put(sq, TCc.getComponentType(), TCc(V3(20.0, 65.0, 0.5), R3(0.0, 0.0, 0.0)))
    put(nref, TCc.getComponentType(), TCc(V3(17.0, 65.0, 0.5), R3(0.0, 0.0, 0.0)))
    tw.run(tst, tbuf, nowms())
    rm1 = sorted(int(r_.getIndex()) for r_ in list(TBf.REMOVED))
    put(sq, TCc.getComponentType(), TCc(V3(25.0, 65.0, 0.5), R3(0.0, 0.0, 0.0)))
    reset_buf()
    tw.run(tst, tbuf, nowms())
    rm2 = sorted(int(r_.getIndex()) for r_ in list(TBf.REMOVED))
    check(rm1 == [int(nref.getIndex())] and rm2 == [982] and abs(float(tw.quick.get(q2).range) - 16.0) < 1e-9,
          "N7 (2.6): TravTick removes the continuation 16.5 blocks from the first launch (wand 16), keeps the wand orb at 14.5 and the staff orb at 19.5, "
          "then removes the staff orb past 24: %s / %s" % (rm1, rm2))
    ACfg.PART_TRAV = False
    reset_buf()
    q3, qpc3 = launched(QORB["Iron"], 983, 0.5, 65.0, 0.5)
    AT.added(q3, qpc3, 1002, tst, tbuf)
    d_off = DMGc(DPS(rc, q3), DCSc.PROJECTILE, JFloat(18.0))
    HS.handle(0, None, tst, tbuf, d_off)
    check(not list(TBf.ADDED), "N7: part.trav off -> ArmoryHitSys does nothing (no pierce, no burst)")
    ACfg.PART_TRAV = True
    # trav-fix (critic): Damage.HIT_LOCATION is a Vector4d in the engine (x, y, z used); none (every projectile hit - only melee puts it) =
    # the target's position + 0.9
    dv_ = DMGc(DPS(rc, q1), DCSc.PROJECTILE, JFloat(1.0))
    dv_.putMetaObject(DMGc.HIT_LOCATION, V4(1.25, 66.0, 2.5, 1.0))
    ha1 = [round(float(x), 3) for x in AT.hitAt(dv_, tbuf, nA)]
    ha2 = [round(float(x), 3) for x in AT.hitAt(DMGc(DPS(rc, q1), DCSc.PROJECTILE, JFloat(1.0)), tbuf, nA)]
    check(ha1 == [1.25, 66.0, 2.5] and ha2 == [5.5, 64.9, 0.5], "N7 (trav-fix): hitAt reads the engine's Vector4d hit location; none = the target + 0.9: %s / %s" % (ha1, ha2))
    # trav-fix (critic HIGH): an enemy flush against a wall - the continuation would start inside the wall -> no continuation (the chain ends);
    # the same hit with the wall 2 blocks further -> the continuation flies
    AT.GRID = Grid(world_fn([lambda x, y, z: x == 6 and 64 <= y <= 66]))
    reset_buf()
    q5, qpc5 = launched(QORB["Iron"], 984, 0.5, 65.0, 0.5)
    AT.added(q5, qpc5, 1002, tst, tbuf)
    d5 = DMGc(DPS(rc, q5), DCSc.PROJECTILE, JFloat(18.0))
    d5.putMetaObject(DMGc.HIT_LOCATION, V4(5.5, 65.0, 0.5, 1.0))
    AT.landed(tst, tbuf, d5, q5, 1002, nA)
    walled = (len(list(TBf.ADDED)), str(AT.LAST_WHY))
    AT.GRID = Grid(world_fn([lambda x, y, z: x == 8 and 64 <= y <= 66]))
    reset_buf()
    q6, qpc6 = launched(QORB["Iron"], 985, 0.5, 65.0, 0.5)
    AT.added(q6, qpc6, 1002, tst, tbuf)
    d6 = DMGc(DPS(rc, q6), DCSc.PROJECTILE, JFloat(18.0))
    d6.putMetaObject(DMGc.HIT_LOCATION, V4(5.5, 65.0, 0.5, 1.0))
    AT.landed(tst, tbuf, d6, q6, 1002, nA)
    open_ = len(list(TBf.ADDED))
    AT.GRID = Grid(world_fn())
    check(walled == (0, "pierce: a block past the enemy") and open_ == 1,
          "N7 (trav-fix): a wall right behind the enemy ends the pierce chain (no continuation inside / past the wall); 2 blocks further it flies: %s / %s" % (walled, open_))
    print("N7. pierce: continuation past the enemy, original start + hit set kept, never the same enemy twice, no cap / cap 1, ranges 16 / 24")

    # --- N8. maxLive, the rows (T4), the bridge words + armory:trav, KEEP 10
    TW.ALL.clear()
    tw = TW.get(tst)
    t_ = nowms()
    for k_ in range(70):
        tw.add(JClass(PKG + "TravFx")(1, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.5, t_ + 5000, t_, 500, 1.0, cu, None, 5000), int(ACfg.TRAV_MAXLIVE), t_)
    check(int(tw.live(t_)) == 64 and tw.fx.size() == 70, "N8 (1.3): trav.maxLive 64 - the 6 oldest live effects end at once (removed on the next tick)")
    Rows2 = JClass(PKG + "CfgRows")
    ks = [str(k) for k in Rows2.KEYS]
    tys = dict(zip(ks, [str(t) for t in Rows2.TYPES]))
    dfs2 = dict(zip(ks, [str(d) for d in Rows2.DEFS]))
    want_def = {"part.trav": "true", "staff.mode": "blink", "blink.distance": "10", "blink.floorCheck": "12", "blink.trailWidth": "1.5", "blink.trailSeconds": "3",
                "blink.trailPercent": "30", "blink.tick": "0.5", "blink.cooldown": "0", "hop.force": "13", "hop.groundCheck": "6", "burst.radius": "6",
                "burst.percent": "60", "orb.radius": "9", "orb.seconds": "3.5", "orb.healPercent": "20", "orb.tick": "1", "orb.partyPercent": "100",
                "orb.othersPercent": "50", "trav.players": "true", "trav.maxLive": "64", "trav.fx": "true", "pierce.max": "0", "quick.range.wand": "16",
                "quick.range.staff": "24", "quick.staffBonus": "15", "trav.staminaPercent": "50", "trav.staminaCap": "10"}
    bad_def = dict((k, (dfs2.get(k), v)) for k, v in want_def.items() if dfs2.get(k) != v)
    check(not bad_def and tys["staff.mode"] == "choice" and int(Rows2.KEEP) == 10 and "staff.stamina" in ks and "hop.mode" in ks,
          "N8 (T4): every traversal row emits with spec 1.4 / section 8's default, staff.mode a choice, KEEP 10, the 2 read-only rows: %s" % bad_def)
    pr_ = Props()
    for k_, v_ in (("blink.distance", "99"), ("staff.mode", "ORB"), ("orb.tick", "0.01"), ("trav.staminaCap", "-5"), ("part.trav", "off")):
        pr_.setProperty(k_, v_)
    ACfg.apply(pr_)
    clamp = (int(ACfg.BLINK_DIST), str(ACfg.STAFF_MODE), float(ACfg.ORB_TICK), int(ACfg.STAMINA_CAP), bool(ACfg.PART_TRAV))
    pr_.setProperty("staff.mode", "teleport")
    ACfg.apply(pr_)
    check(clamp == (20, "orb", 0.25, 0, False) and str(ACfg.STAFF_MODE) == "blink" and str(br.get("armory:trav")).startswith("traversals OFF"),
          "N8: the loader clamps like the kit validates (99 -> 20, ORB -> orb, 0.01 -> 0.25, -5 -> 0, off) and an unknown mode reads blink; armory:trav follows: %s" % (clamp,))
    ACfg.useDefaults()
    PL.publish()
    info2 = br.get("armory:fn:info")
    a_s = list(info2.apply(JArray(JObject)(["staff", "Weapon_Staff_Iron"])))
    a_w = list(info2.apply(JArray(JObject)(["wand", "Weapon_Wand_Iron"])))
    a_0 = list(info2.apply(JArray(JObject)(["wand", "Weapon_Wand_Wood"])))
    check(len(a_s) == 11 and str(a_s[8]) == "Hold - blink 10 blocks + light trail - 10 Stamina" and str(a_s[9]) == "24 blocks" and float(a_s[10]) == 15.0
          and str(a_w[8]) == "Hold - hop back + burst 6 blocks + heal orb 9 blocks - 7.5 Stamina" and str(a_w[9]) == "pierces - 16 blocks" and float(a_w[10]) == 0.0
          and str(a_0[8]) == "" and str(a_0[9]) == "pierces - 16 blocks" and str(a_s[6]) == SORB["Iron"],
          "N8 (3.1.5): armory:fn:info [8] traversal words, [9] quick words, [10] staff quick bonus %%; [6] stays the StaffOrb (the charged damage SkyyGear shows); "
          "the Wood wand's hold is SkyySkills' orb (no words): %s / %s / %s" % (a_s[8:], a_w[8:], a_0[8:]))
    trav_txt = str(br.get("armory:trav"))
    check(trav_txt.startswith("traversals on (Stamina 50% of the Mana, cap 10) - staff hold blink 10 blocks") and "pierce no cap" in trav_txt and "party 100%, others 50%" in trav_txt,
          "N8: armory:trav carries the live numbers for SkyyMenu's help: %s" % trav_txt[:200])
    # --- G2. SkyyGear 0.2.4 (loaded instead of the pin when it is built - the deploy partner, spec 3.3 / 3.4): its tooltip lines on these
    # REAL armory:fn:info answers (GearView.statLines = the shot block of the tooltip), and an older 8-element answer = 0.2.3's lines
    if os.path.basename(GEAR_JAR) == "SkyyGear-0.2.4.jar":
        GV, GBs = JClass("com.skyy.gear.GearView"), JClass("com.skyy.gear.GearBase")

        def tip(iid, lv):
            t_, c_ = ArrayList(), ArrayList()
            GV.statLines(iid, doc(lv), t_, c_)
            return [str(x) for x in t_]
        ms_ = float(GBs.mult("Weapon_Staff_Iron", doc(15), True))
        mw_ = float(GBs.mult("Weapon_Wand_Iron", doc(15), True))
        fl = lambda x: int(math.floor(x + 1e-6))
        ws_ = ["Charged shot - 30 Mana - %d damage at Lv 15" % fl(175 * ms_), "Hold - blink 10 blocks + light trail - 10 Stamina",
               "Quick shot - 6 Mana - %d damage at Lv 15 - 24 blocks" % fl(35 * 1.15 * ms_)]
        ww_ = ["Charged shot - 15 Mana - %d damage at Lv 15" % fl(88 * mw_), "Hold - hop back + burst 6 blocks + heal orb 9 blocks - 7.5 Stamina",
               "Quick shot - 3 Mana - %d damage at Lv 15 - pierces - 16 blocks" % fl(18 * mw_)]
        ts_, tw_ = tip("Weapon_Staff_Iron", 15), tip("Weapon_Wand_Iron", 15)
        check(ts_[:3] == ws_ and tw_[:3] == ww_, "G2 (3.3): SkyyGear 0.2.4's tooltip - the hold line right under the charged shot, the quick words on the quick "
                                                 "line, the staff quick shot x1.15 (quick.staffBonus): %s / %s" % (ts_[:3], tw_[:3]))
        real_info = br.get("armory:fn:info")

        @JImplements("java.util.function.Function")
        class Old8:
            @JOverride
            def apply(self, o):
                r_ = real_info.apply(o)
                return None if r_ is None else JArray(JObject)(list(r_)[:8])
        br.put("armory:fn:info", Old8())
        to_ = tip("Weapon_Staff_Iron", 15)
        br.put("armory:fn:info", real_info)
        check(to_[:2] == ["Charged shot - 30 Mana - %d damage at Lv 15" % fl(175 * ms_), "Quick shot - 6 Mana - %d damage at Lv 15" % fl(35 * ms_)],
              "G2: an older SkyyArmory (8 elements) -> exactly 0.2.3's two lines: %s" % to_[:3])
        ACfg.PART_TRAV = False
        tf_ = tip("Weapon_Staff_Iron", 15)
        ACfg.PART_TRAV = True
        check(tf_[:2] == ["Charged shot - 30 Mana - %d damage at Lv 15" % fl(175 * ms_), "Quick shot - 6 Mana - %d damage at Lv 15 - 24 blocks" % fl(35 * 1.15 * ms_)],
              "G2: part.trav off -> no hold line (the quick range words stay - the ranges are not part of the traversal switch): %s" % tf_[:3])
        print("G2. SkyyGear 0.2.4 tooltip on SkyyArmory 0.1.1's answers: %s | %s" % (ts_[:3], tw_[:3]))
    else:
        print("G2. NOTE SkyyGear 0.2.4 is not built here - its tooltip lines are not checked")
    # trav-fix (critic): an idle world's TravWorld is dropped (TravTick on an idle world; an orb record removed) - no Store kept after an island unloads
    TW.ALL.clear()
    TW.get(tst)
    TT_ = JClass(PKG + "TravTick")()
    TT_.tick(JFloat(0.05), 0, None, tst, tbuf)
    gone1 = TW.of(tst) is None
    reset_buf()
    ob7, opc7 = launched(ORB["Iron"], 990, 0.5, 65.5, 0.5)
    AT.added(ob7, opc7, 2002, tst, tbuf)
    TT_.tick(JFloat(0.05), 0, None, tst, tbuf)
    kept1 = TW.of(tst) is not None
    AT.removed(ob7, False, tst, tbuf)
    gone2 = TW.of(tst) is None
    check(gone1 and kept1 and gone2, "N8 (trav-fix): TravWorld.ALL forgets a world with nothing live (TravTick / the last record removed) and keeps one "
                                     "with a live orb: %s / %s / %s" % (gone1, kept1, gone2))
    PL.unpublish()
    br.remove("party:fn:members")
    AT.NEAR = None
    AT.GRID = None
    TW.ALL.clear()
    ACfg.useDefaults()
    print("N8. maxLive 64, %d rows with the spec defaults, loader clamps, armory:fn:info [8]-[10], armory:trav" % len(want_def))
'''
traw = open(TSRC, encoding="utf8", newline="").read()
TNL = CR + LF if (CR + LF) in traw else LF
ts = traw.replace(CR + LF, LF)


def hrep(old, new, count=1):
    global ts
    n = ts.count(old)
    assert n == count, "harness anchor count %d (want %d): %s" % (n, count, old[:140])
    ts = ts.replace(old, new)


hrep('"""SkyyArmory 0.1 - test harness (', '''"""SkyyArmory 0.1.1 - test harness. GENERATED by tools/armory_0_1_1_patch.py from test_skyyarmory_0.1.py - edit the patch, never this file.
Every 0.1 check below still runs (patched where 0.1.1 changed the asset set on purpose: no staff Stamina elements, the staff hold
launches the blink marker, 11-element armory:fn:info, 5 systems, the new rows); two NEW sections EXECUTE the traversals:
  P8  (Python, spec 5 T1) no SkyyArmory_Staff_Stamina* file and no Stamina in any chain; every staff charged Launch names
      SkyyArmory_Blink_<M>; every Blink projectile Damage 0 / Gravity 0 / TTL > the longest trail / the marker model / no hit or death
      particles; the marker model carries no attachment / particles / trails (the orb's hitbox); the gold trail light files; no asset hop.
  N   (JVM, spec 5 T2-T4 + section 8) TravMath on a fake grid (wall at 6 -> 5.7, void -> last floored step, ceiling, straight up with
      the floor check, a wall in your face = 0 = free); the engine glue on real engine objects (TransformComponent, HeadRotation,
      EntityStatMap with the real stat types, Velocity, Teleport, Damage / ProjectileSource / EntitySource, ProjectileComponent after
      initialize + shoot, assembleDefaultProjectile) inside a map-backed Store / CommandBuffer / World: the blink moves you (Teleport,
      keep-fall, Mana kept, Stamina 2:1 with the cap) and a blink that does not move you costs NOTHING (Mana back, no Stamina: wall,
      too little Stamina, cooldown, class lock); the trail hits enemies on the line only (party never, strangers only with PvP on +
      trav.players), the marker goes at the end; the hop pushes opposite to the look (down = straight up, half without ground, Stamina
      2:1, too little = no hop); the burst hits the OTHER enemies for 60% (not the direct target, not allies), once per orb, a miss
      bursts where the orb ended; the heal orb heals the Priest + party 100% / other non-hostile players 50% through class:fn:heal
      (the exact Object[] contract) or straight into Health without SkyyClasses; the pierce continuation (LaunchProjectileInteraction's
      steps), the chain never hits an enemy twice, the quick ranges 16 / 24 remove the orb; staff.mode orb / part.trav off fire the 0.1
      orb; trav.maxLive; the rows, armory:trav, armory:fn:info [8]-[10], KEEP 10.
Harness seams (null in the game): ArmoryTrav.GRID (the block grid) and ArmoryTrav.NEAR (the sphere query) - everything else is the engine.

0.1 harness: SkyyArmory 0.1 - test harness (''')
hrep('VERSION = "0.1"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1 SkyyArmory"',
     'VERSION = "0.1.1"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.1 SkyyArmory"')
hrep('os.path.join(SCRATCH_ROOT, "armory01", "harness")', 'os.path.join(SCRATCH_ROOT, "armory011", "harness")')
hrep('''PACKS = re.findall(r'"([^"]+:[^"]+)"', re.search(r"PACK_THIRD_PARTY = \\[(.*?)\\]", _dst).group(1))''',
     '''PACKS = re.findall(r'"([^"]+:[^"]+)"', re.search(r"PACK_THIRD_PARTY = \\[(.*?)\\]", _dst, re.S).group(1))''')
hrep('raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.py', 'raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.1.py')
hrep('''SQORB = dict((m, "SkyyArmory_StaffQuickOrb_" + m) for m in METALS)''', '''SQORB = dict((m, "SkyyArmory_StaffQuickOrb_" + m) for m in METALS)
BLINK = dict((m, "SkyyArmory_Blink_" + m) for m in METALS)          # 0.1.1: the staff hold's invisible blink marker''')
hrep('''check(len(J_INTS) == 117 and len(J_ROOTS) == 15 and len(J_PRJ) == 31, "P0: 117 interactions, 15 roots, 31 projectiles (%d / %d / %d)" % (''',
     '''check(len(J_INTS) == 115 and len(J_ROOTS) == 15 and len(J_PRJ) == 39, "P0: 115 interactions (0.1.1: no staff Stamina pair), 15 roots, 39 projectiles (+ 8 blink markers) (%d / %d / %d)" % (''')
hrep('''check(sorted(J_PRJ) == sorted(list(ORB.values()) + list(QORB.values()) + list(SORB.values()) + list(SQORB.values())), "P0: projectile ids")''',
     '''check(sorted(J_PRJ) == sorted(list(ORB.values()) + list(QORB.values()) + list(SORB.values()) + list(SQORB.values()) + list(BLINK.values())), "P0: projectile ids")''')
hrep('''check(list(J_MODELS) == ["SkyyArmory_QuickOrb"] and list(J_TRAILS) == ["SkyyArmory_Orb_Trail_Blue"] and len(J_PSYS) == 3 and len(J_PSP) == 5,
      "P0: quick look = 1 model asset, 1 trail, 3 particle systems, 5 spawners")''',
     '''check(sorted(J_MODELS) == ["SkyyArmory_Marker", "SkyyArmory_QuickOrb"] and list(J_TRAILS) == ["SkyyArmory_Orb_Trail_Blue"] and len(J_PSYS) == 4 and len(J_PSP) == 7,
      "P0: quick look (1 model asset, 1 trail, 3 particle systems, 5 spawners) + 0.1.1's marker model and the gold trail light (1 system, 2 spawners)")''')
hrep('''        for k in ("HitParticles", "DeathParticles"):
            s = d[k]["SystemId"]''', '''        for k in ("HitParticles", "DeathParticles"):
            if k not in d and d["Appearance"] == "SkyyArmory_Marker":
                continue                 # 0.1.1: the blink marker carries none (it never hits; it is removed, never killed)
            s = d[k]["SystemId"]''')
hrep('''    check(PIN.get(MOD) == VERSION, "P5 (pair): SkyySkills %s is pinned, so SkyyArmory %s must be pinned in the same SET: %s" % (SKILLS_PIN, VERSION, PIN.get(MOD)))''',
     '''    check(PIN.get(MOD) is not None, "P5 (pair): SkyySkills %s is pinned, so a SkyyArmory must be pinned in the same SET (0.1.1 takes 0.1's slot): %s" % (SKILLS_PIN, PIN.get(MOD)))''')
hrep('''check(sorted(pk_found) == sorted(PACKS), "P5: both pack mods found and checked: %s" % pk_found)''',
     '''check(set(pk_found) <= set(PACKS) and pk_found, "P5: the installed pack mods were found and checked: %s (listed but not installed here: %s)" % (
    pk_found, sorted(set(PACKS) - set(pk_found))))''')
hrep('''    check(len(names) == 17, "A: 17 classes (10 SkyyArmory + 7 kit)")''', '''    check(len(names) == 29, "A: 29 classes (22 SkyyArmory incl. 0.1.1's 12 traversal classes + 7 kit)")''')
hrep('''        check(str(DEC[("interaction", "SkyyArmory_Staff_Cast_Launch_" + m)].getProjectileId()) == SORB[m]''',
     '''        check(str(DEC[("interaction", "SkyyArmory_Staff_Cast_Launch_" + m)].getProjectileId()) == BLINK[m]''')
hrep('''    sta = DEC[("interaction", "SkyyArmory_Staff_Stamina")]
    std = DEC[("interaction", "SkyyArmory_Staff_Stamina_Delay")]
    check(dict((str(k), float(v)) for k, v in dict(f_esa.get(sta)).items()) == {"Stamina": -5.0}
          and dict((str(k), float(v)) for k, v in dict(f_esa.get(std)).items()) == {"StaminaRegenDelay": -1.5}
          and str(jfield(CSB, "changeStatBehaviour").get(std)) == "Set", "R (ST3): the staff hold spends 5 Stamina and Sets the regen delay -1.5 (vanilla)")''',
     '''    stam_spend = []
    for k_, o_ in DEC.items():
        if k_[0] == "interaction" and CSB.class_.isInstance(o_):
            a_ = f_esa.get(o_)
            if a_ is not None and (a_.containsKey("Stamina") or a_.containsKey("StaminaRegenDelay")):
                stam_spend.append(k_[1])
    check(("interaction", "SkyyArmory_Staff_Stamina") not in DEC and ("interaction", "SkyyArmory_Staff_Stamina_Delay") not in DEC and not stam_spend,
          "R (0.1.1, Skyy 2026-10-05): no decoded interaction spends Stamina or sets its regen delay - the staff casts cost Mana only (the blink pays its Stamina on the server): %s" % stam_spend)''')
hrep('''    for pid in sorted(JPRJ):''', '''    for pid in sorted(p_ for p_ in JPRJ if p_ not in BLINK.values()):       # the 8 blink markers: section N1''')
hrep('''            load(MDLc, [qm], PACK)]''', '''            load(MDLc, [qm, DEC[("model", "SkyyArmory_Marker")]], PACK)]''')
hrep('''"15 of 15 items, 117 of 117 interactions, 31 of 31 projectiles come from Skyy:0.1 SkyyArmory"''',
     '''"15 of 15 items, 115 of 115 interactions, 39 of 39 projectiles come from Skyy:0.1.1 SkyyArmory"''')
hrep('''        cast_kids = ([["SkyyArmory_Staff_Stamina"], ["SkyyArmory_Staff_Stamina_Delay"]] if kind_ == "Staff" else []) + [''', '''        cast_kids = [''')
hrep('''              "Stamina, regen delay, cost, launch, effect for staffs", comp_bad[:3]))''', '''              "cost, launch (the blink marker for staffs), effect - 0.1.1: no Stamina elements", comp_bad[:3]))''')
hrep('''        for iid, sp, q_, o_ in ((WID[m], "wand", QORB[m], ORB.get(m, VAN_ORB)), (SID[m], "staff", SQORB[m], SORB[m])):''',
     '''        for iid, sp, q_, o_ in ((WID[m], "wand", QORB[m], ORB.get(m, VAN_ORB)), (SID[m], "staff", SQORB[m], BLINK[m])):     # 0.1.1: the staff hold launches the marker''')
hrep('''            lo_hi = ((W[m][4], W[m][3]) if sp == "wand" else (S[m][4], S[m][3]))''',
     '''            # 0.1.1: the blink marker deals nothing itself (Damage 0), so SkyyGear's chain-walk range of a staff is its quick shot only (its
            # tooltip lines come from armory:fn:info, not from this walk - SkyyGear 0.2.2+)
            lo_hi = ((W[m][4], W[m][3]) if sp == "wand" else (S[m][4], S[m][4]))''')
hrep('''    check(hit(QORB["Mithril"]) == 200.0 and hit(SQORB["Mithril"]) == 200.0 and hit(ORB["Mithril"]) == 100.0 and hit(SORB["Mithril"]) == 100.0,
          "U (T12): quick.damage 40 doubles quick hits only (wand + staff)")''',
     '''    check(hit(QORB["Mithril"]) == 200.0 and hit(SQORB["Mithril"]) == 230.0 and hit(ORB["Mithril"]) == 100.0 and hit(SORB["Mithril"]) == 100.0,
          "U (T12): quick.damage 40 doubles quick hits only (wand + staff; 0.1.1: staff quick shots + quick.staffBonus 15%)")''')
hrep('''    check(hit(SORB["Mithril"]) == 300.0 and hit(SQORB["Mithril"]) == 600.0 and hit(SORB["Onyxium"]) == 100.0, "U (T12): Mithril staff 300% (+ quick 40)")''',
     '''    check(hit(SORB["Mithril"]) == 300.0 and hit(SQORB["Mithril"]) == 690.0 and hit(SORB["Onyxium"]) == 100.0 and hit(BLINK["Mithril"]) == 300.0,
          "U (T12): Mithril staff 300% (+ quick 40 + the 15% staff bonus); 0.1.1: its blink trail ticks follow the staff's tune too")''')
hrep('''    want_rows = ["part.tune", "tune.wand", "tune.staff", "quick.damage", "part.spawn", "quick.size", "quick.speed", "quick.life", "check.on", "check.share"]
    check(keys[:10] == want_rows and all(k.startswith("fixed.") for k in keys[10:]) and len(keys) == 10 + 8 + 8 + 5,
          "K: 10 live rows (fix round: + quick.life) + 21 read-only rows (8 wands, 8 staffs, quick shot, art, Wood tap, staff tap, staff base): %s" % keys[:10])
    check(types["tune.wand"] == "table" and types["tune.staff"] == "table" and "part" in flags["part.tune"].split(",") and "danger" in flags["part.spawn"].split(",")
          and all(flags[k] == "ro" for k in keys[10:]) and all(len(h) <= 100 for h in helps.values()) and types["quick.life"] == "int"
          and defs["quick.life"] == "5" and flags["quick.life"] == "new", "K: row types / flags / help lengths; quick.life int 5 s, new shots only")''',
     '''    want_rows = ["part.tune", "tune.wand", "tune.staff", "quick.damage", "part.spawn", "quick.size", "quick.speed", "quick.life", "check.on", "check.share"]
    NEW_ROWS = ["part.trav", "trav.staminaPercent", "trav.staminaCap", "trav.players", "trav.maxLive", "trav.fx", "staff.mode", "blink.distance",
                "blink.floorCheck", "blink.keepFall", "blink.trailOn", "blink.trailWidth", "blink.trailSeconds", "blink.trailPercent", "blink.tick",
                "blink.cooldown", "hop.force", "hop.groundCheck", "burst.radius", "burst.percent", "orb.radius", "orb.seconds", "orb.healPercent",
                "orb.tick", "orb.partyPercent", "orb.othersPercent", "pierce.max", "quick.range.wand", "quick.range.staff", "quick.staffBonus"]
    NN = len(NEW_ROWS)
    check(keys[:10] == want_rows and keys[10:10 + NN] == NEW_ROWS and all(k.startswith("fixed.") or k in ("staff.stamina", "hop.mode") for k in keys[10 + NN:])
          and len(keys) == 10 + NN + 8 + 8 + 5 + 2,
          "K: 10 live rows (fix round: + quick.life) + 0.1.1's %d traversal rows + 23 read-only rows (8 wands, 8 staffs, quick shot, art, Wood tap, "
          "staff tap, staff base, staff Stamina, hop mode): %s" % (NN, keys[10:10 + NN] if keys[10:10 + NN] != NEW_ROWS else len(keys)))
    check(types["tune.wand"] == "table" and types["tune.staff"] == "table" and "part" in flags["part.tune"].split(",") and "danger" in flags["part.spawn"].split(",")
          and all(flags[k] == "ro" for k in keys[10 + NN:]) and all(len(h) <= 100 for h in helps.values()) and types["quick.life"] == "int"
          and defs["quick.life"] == "5" and flags["quick.life"] == "new,adv", "K: row types / flags / help lengths; quick.life int 5 s, new shots only, Advanced (0.1.1, spec 3.1.4)")''')
hrep('''    check(all(g_ == (8, c_, q_, "java.lang.String") for (i_, k_, c_, q_), (_i, g_) in zip(want_ids, got_ids))''',
     '''    check(all(g_ == (11, c_, q_, "java.lang.String") for (i_, k_, c_, q_), (_i, g_) in zip(want_ids, got_ids))''')
hrep('''          "orb + SkyyArmory_QuickOrb_Wood), each a shipped projectile: %s" % [g for g in got_ids if g[1] is None or g[1][0] != 8][:3])''',
     '''          "orb + SkyyArmory_QuickOrb_Wood), each a shipped projectile; 0.1.1: 11 elements: %s" % [g for g in got_ids if g[1] is None or g[1][0] != 11][:3])''')
hrep('''        setf(p_, PBc, "dataDirectory", Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1")))''',
     '''        setf(p_, PBc, "dataDirectory", Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.1")))''')
hrep('''    ready = [m_ for lv_, m_ in records()[n_log0:] if "[SkyyArmory] 0.1 ready" in m_]''', '''    ready = [m_ for lv_, m_ in records()[n_log0:] if "[SkyyArmory] 0.1.1 ready" in m_]''')
hrep('''    check(len(caps) == 2 and all(len(c) == 2 for c in caps) and str(caps[0][0].getClass().getSimpleName()) == "ArmoryTuneSys"
          and str(caps[0][1].getClass().getSimpleName()) == "ArmorySpawnSys" and bool(caps[0][0].ordered) and bool(caps[0][1].ordered),
          "T: setup() hands the registry exactly 2 systems (one registerSystem each), both ordered (before armour / after the vanilla projectile setup)")''',
     '''    check(len(caps) == 2 and all(len(c) == 5 for c in caps) and [str(x.getClass().getSimpleName()) for x in caps[0]] == [
              "ArmoryTuneSys", "ArmorySpawnSys", "ArmoryTravSys", "ArmoryHitSys", "TravTick"] and bool(caps[0][0].ordered) and bool(caps[0][1].ordered),
          "T: setup() hands the registry exactly 5 systems (one registerSystem each; 0.1.1: + ArmoryTravSys, ArmoryHitSys, TravTick), tune + spawn ordered: %s" % (
              [str(x.getClass().getSimpleName()) for x in caps[0]] if caps else None))
    trav_line = [m_ for lv_, m_ in records()[n_log0:] if "0.1.1 magic traversals: traversals on" in m_]
    check(len(trav_line) == 2 and "hook true, hits true, tick true" in trav_line[0], "T (0.1.1): the start line names the traversal numbers and the 3 systems: %s" % trav_line[:1])''')
hrep('GEAR_JAR = os.path.join(ROOT, "SkyyGear", "SkyyGear-%s.jar" % PIN["SkyyGear"])',
     'GEAR_JAR = os.path.join(ROOT, "SkyyGear", "SkyyGear-%s.jar" % PIN["SkyyGear"])' + LF +
     'if os.path.isfile(os.path.join(ROOT, "SkyyGear", "SkyyGear-0.2.4.jar")):     # 0.1.1: the deploy partner (its tooltip words, G2)' + LF +
     '    GEAR_JAR = os.path.join(ROOT, "SkyyGear", "SkyyGear-0.2.4.jar")')
hrep('''    print("G. SkyyGear %s: bands, spell, K = 1, the walk on the real chains (quick 0 / charged 1 for 16 weapons + 3 wood wands), spellRange" % PIN["SkyyGear"])''',
     '''    print("G. %s: bands, spell, K = 1, the walk on the real chains (quick 0 / charged 1 for 16 weapons + 3 wood wands), spellRange" % os.path.basename(GEAR_JAR))''')
hrep('''PY_OKS, PY_FAILS = OKS[0], len(FAILS)''', HARNESS_P8.rstrip("\n") + "\n" + '''PY_OKS, PY_FAILS = OKS[0], len(FAILS)''')
hrep('''    # ---------------- L2. (last: it changes the store)''', HARNESS_N.rstrip("\n") + "\n" + '''    # ---------------- L2. (last: it changes the store)''')
tout = ts.replace(LF, TNL)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(tout)
print("wrote %s (%d lines)" % (os.path.relpath(TDST, ROOT), tout.count(TNL) + 1))
