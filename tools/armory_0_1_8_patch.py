"""Derive SkyyArmory/build_skyyarmory_0.1.8.py (+ its harness SkyyArmory/test_skyyarmory_0.1.8.py) from the GENERATED 0.1.7
(SkyyArmory/build_skyyarmory_0.1.7.py = the tools/deploy_set.py SET pin, made by tools/armory_0_1_7_patch.py; test_skyyarmory_0.1.7.py =
its harness). Every anchor is asserted (rep = exactly one hit). Edit THIS file, never the generated scripts.
Run:  python tools/armory_0_1_8_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.8.py   then   python SkyyArmory/test_skyyarmory_0.1.8.py
      (never --deploy; no deploy partner: SkyyGear's dagger speed chains route through the vanilla Pounce_StaminaCondition - asserted)

0.1.8 = THE DAGGER SHADOW STEP (Skyy 2026-10-07, research/Shadow-Step-Spec.md = the contract; docs/answered/classes.md LOCKED lines "ASSASSIN
dagger charged = SHADOW STEP", "VOID" and "NO VOID PROTECTION anywhere"; spec section 6 defaults: +10 % bonus, PvP yes where PvP is on, ALL daggers):
  THE INPUT: the daggers' charged move. Every Weapon_Daggers_* (vanilla, pack daggers and SkyyGear's speed copies) reaches the vanilla Pounce
    through Root_Weapon_Daggers_Primary -> Weapon_Daggers_Primary "0.2" -> Var Pounce_StaminaCondition (vanilla: Stamina > 0, regen pause) ->
    Var Pounce (default Weapon_Daggers_Primary_Pounce). SkyyArmory overrides THAT ONE interaction by id (the Wand_Primary / bow-leap way): the
    vanilla charging (0.4 s, its particles + PounceStabCharging pose, release before it = the vanilla tap chain) is kept, only its "0.4" step
    changes - LaunchProjectile of the invisible marker SkyyArmory_Shadow_Step (the blink-marker shape) instead of the leap. Tap combo, the
    right-click guard and the Razorstrike signature stay vanilla. The chain spends no Stamina (the server does - a step that cannot move you is free).
  THE STEP (Java, Shadow + KunaiJob kind 3; world thread outside the systems - the kunai teleport path): the marker's SPAWN -> removed -> the
    job: class lock, cooldown by metal, the TARGET = an enemy (a mob you can hurt: NPC with stats, not Invulnerable, no grapple.noYankWords role;
    a player only where PvP is on + trav.players + dagger.shadowStep.players, never party) whose centre is closest to your aim, within
    targetRange 24 and inside the targetCone (30 = the cone's FULL width, so at most 15 degrees off your aim - fix round), with line of sight.
    FIX ROUND (critic): the engine attitude decides who is an enemy - the mob's WorldSupport component (Role.createAndAttach puts it on every
    NPC; VERIFIED bytecode): its attitude override toward YOU, else its default player attitude. HOSTILE mobs (and PvP players) always win
    over NEUTRAL ones (wildlife, Scarak, Feran - only when no hostile one is in the cone, row dagger.shadowStep.neutral); FRIENDLY / REVERED
    / IGNORE mobs (livestock, pets, villagers, summoned allies) are never a target -> ARRIVE `behind` 1.5 blocks (more for a wide mob) behind its body
    facing its back: the nearest free spot of its back half (0, +-30, +-60, +-90 degrees, the same height, 1 up, 1 down; the line from its centre
    to the spot clear), else beside it (+-120); none = nothing spent. Your body + head turn to face its back (Teleport body + head rotation).
    NO TARGET: straight along your aim (pitch included) up to noTargetDistance 18 - the blink scan (the farthest free 2-block body spot, 0.3
    short of walls; air and void allowed - NO void protection, Skyy). A step that cannot move you >= 1 block costs nothing. Safety = the kunai
    teleport's: never inside a block, never through a wall, never into another world, the locked-arena bridge (arena:fn:blocks, kunai.noArena).
  THE BACKSTAB: a targeted step arms your next dagger MELEE hit within backstabWindow 3 s (any enemy; a 0-damage guard shove does not count;
    fix round: the hit's damage cause must be Physical (or inherit it) and you within dagger reach of the target - the longest vanilla dagger
    selector EndDistance read at build time + 1 block + half its width - so a kunai / arrow / spell hit with a dagger in hand never spends it): x the
    vanilla dagger backstab (the AngledDamage factor of the vanilla daggers' Pounce / Razorstrike, read at build time = 1.5; the vanilla taps
    carry none) x (1 + backstabBonus 0.10). A signature (Ability) chain hit already gets the vanilla backstab from behind: it gets only the
    bonus (no double backstab). ArmoryTuneSys (Filter group, before armour) applies it.
  COST + COOLDOWN: staminaCost 4 (the traversal Stamina cap trav.staminaCap applies), paid only when you move; cooldown by metal Crude / Copper
    6 s ... Onyxium 4 s, every other dagger (Bone, Bronze, pack daggers) the "Other" entry 6 s.
  THE SHADOW: a short, dark, see-through smoke silhouette (SkyyArmory_Shadow_Fade, built from the vanilla Smoke_Black spawner at build time)
    at the spot you left, gone in about 1 s; trav.fx off = none.
  SETTINGS: 10 rows + a cooldown table (Server Setup > Armory > Dagger Shadow Step) + 3 read-only rows. No migration (new keys only).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.7.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.8.py")
TSRC = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.7.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.8.py")

raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.7"\nMOD = "SkyyArmory"' in s and "0.1.7 = THE MONK WEAPONS AS ITEMS" in s, "build_skyyarmory_0.1.7.py is not the 0.1.7 pin"
SYS0 = s.count("registerSystem(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:140])
    s = s.replace(old, new)


def after(anchor, add):
    rep(anchor, anchor + add)


def before(anchor, add):
    rep(anchor, add + anchor)


# ================================================================================================ header + version
rep('''"""SkyyArmory 0.1.7 - build script (javassist via jpype). GENERATED by tools/armory_0_1_7_patch.py from the GENERATED 0.1.6 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.7.py -> SkyyArmory/SkyyArmory-0.1.7.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.7.py (scratch tools/dev/scratch/armory017/).
''', '"""SkyyArmory 0.1.8 - build script (javassist via jpype). GENERATED by tools/armory_0_1_8_patch.py from the GENERATED 0.1.7 - edit the\n'
    'patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.8.py -> SkyyArmory/SkyyArmory-0.1.8.jar (never --deploy). Harness:\n'
    'python SkyyArmory/test_skyyarmory_0.1.8.py (scratch tools/dev/scratch/armory018/).\n\n'
    + open(__file__, encoding="utf8").read().split('"""')[1].split("\n", 3)[3].strip() + "\n\n"
    '0.1.7 (the base, everything below is still true unless 0.1.8 above says otherwise):\n')
rep('VERSION = "0.1.7"\nMOD = "SkyyArmory"', 'VERSION = "0.1.8"\nMOD = "SkyyArmory"')

# ================================================================================================ the 0.1.8 constants + the Shadow Step rows
SS_CONST = r'''
# ================================================================= 0.1.8 DAGGER SHADOW STEP (Skyy LOCKED 2026-10-07; research/Shadow-Step-Spec.md 2 + 4 + 6 defaults)
SS_MARK = "SkyyArmory_Shadow_Step"          # the invisible marker the charged release launches (code 11000; removed at its SPAWN)
SS_CODE = 11000
SS_POUNCE = "Weapon_Daggers_Primary_Pounce"  # the ONE vanilla dagger interaction we override (its "0.4" step only)
SS_ANIM = "DashForward"                      # the release pose (vanilla Daggers animation set)
SS_SND = "SFX_Daggers_T1_Pounce"             # the vanilla dagger pounce whoosh, at the spot you leave and where you appear
PS_SHADOW = "SkyyArmory_Shadow_Fade"         # the fading see-through shadow (built from the vanilla Smoke_Black spawner)
SS_SHADOW_S = 1.0                            # spec 2: ~1 s fade (the particle asset - fixed in the jar, a read-only row)
SS_EYE = 1.6                                 # the eye height every SkyyArmory traversal aims from
SS_METALS_DEF = ["Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium", "Other"]
SS_CD = [6.0, 6.0, 5.5, 5.0, 5.0, 4.5, 4.0, 4.0, 6.0]          # spec 2: 6 s Crude / Copper -> 4 s Onyxium; Other = every non-metal dagger
CFG_SS = [
    ('dagger.shadowStep.enabled', 'Dagger Shadow Step', 'shadow', 'bool', 'true', '', '', '', '', 'live,part,danger', 'Off = holding the dagger attack does nothing (the vanilla Pounce is replaced).', 'SS_ON', 'boolean', 'true', 'Daggers: hold the attack + release = Shadow Step (vanish, appear behind the enemy you aim at, backstab). Off = the hold does nothing.'),
    ('dagger.shadowStep.targetRange', 'Target range (blocks)', 'shadow', 'int', '24', '4', '48', '', 'blocks', 'live', 'Enemies this close (line of sight) can be stepped behind.', 'SS_RANGE', 'int', '24', 'Shadow Step targets an enemy at most this many blocks away (line of sight needed).'),
    ('dagger.shadowStep.targetCone', 'Target cone (degrees, full width)', 'shadow', 'int', '30', '10', '180', 'step=5', '', 'live', 'Full cone width around your crosshair (30 = up to 15 degrees off it); closest to the crosshair wins.', 'SS_CONE', 'int', '30', 'Shadow Step looks for an enemy inside a cone this many degrees wide around your aim (30 = at most 15 degrees off it); the one closest to your crosshair wins.'),
    ('dagger.shadowStep.behind', 'Arrive behind it (blocks)', 'shadow', 'dec', '1.5', '0.5', '4', '', 'blocks', 'live', 'From its centre (wide mobs: half their width + 0.5 at least).', 'SS_BEHIND', 'double', '1.5', 'You appear this many blocks behind the target (wide mobs: at least half their width + 0.5), facing its back.'),
    ('dagger.shadowStep.noTargetDistance', 'No target: step forward (blocks)', 'shadow', 'int', '18', '2', '40', '', 'blocks', 'live', 'Straight where you look; air and void allowed (Skyy: no void protection).', 'SS_FAR', 'int', '18', 'No enemy in your aim: you step straight where you look, up to this many blocks (into the air or over the void is allowed).'),
    ('dagger.shadowStep.backstabWindow', 'Backstab window (s)', 'shadow', 'dec', '3', '0.5', '10', '', 's', 'live', 'Your next dagger hit within this many seconds is a backstab.', 'SS_WINDOW', 'double', '3', 'After a step behind an enemy, your next dagger hit within this many seconds is a guaranteed backstab.'),
    ('dagger.shadowStep.backstabBonus', 'Backstab bonus (x)', 'shadow', 'dec', '0.1', '0', '1', '', 'x', 'live', 'On top of the vanilla backstab (x1.5): 0.1 = +10 %.', 'SS_BONUS', 'double', '0.1', 'The guaranteed backstab = the vanilla dagger backstab (x1.5) x (1 + this); 0.1 = +10 %.'),
    ('dagger.shadowStep.staminaCost', 'Stamina cost', 'shadow', 'dec', '4', '0', '10', '', '', 'live', 'Paid only when you move (trav.staminaCap applies).', 'SS_STAM', 'double', '4', 'Stamina a Shadow Step costs, paid only when it moves you (trav.staminaCap caps it).'),
    ('dagger.shadowStep.players', 'Step behind players (PvP on)', 'shadow', 'bool', 'true', '', '', '', '', 'live', 'Only where the world PvP is on and trav.players is on; never party.', 'SS_PLAYERS', 'boolean', 'true', 'Shadow Step may target players where the world PvP is on (trav.players on too); never party members.'),
    ('dagger.shadowStep.neutral', 'Step behind neutral mobs', 'shadow', 'bool', 'true', '', '', '', '', 'live', 'Hostile mobs win; neutral ones (wildlife, Scarak) only if no hostile is in aim. Livestock: never.', 'SS_NEUTRAL', 'boolean', 'true', 'Shadow Step targets hostile mobs first; on = a neutral mob (wildlife, Scarak, Feran) counts when no hostile one is in your aim. Friendly mobs (livestock, pets, villagers) never count.'),
]
'''
before('''# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)''', SS_CONST)
rep("""+ CFG_GRAPPLE + CFG_LEAP + CFG_BK + CFG_ST      # 0.1.2 grapple + 0.1.3 leap + 0.1.6 book / kunai + 0.1.7 stunlock rows""",
    """+ CFG_GRAPPLE + CFG_LEAP + CFG_BK + CFG_ST + CFG_SS      # 0.1.2 grapple + 0.1.3 leap + 0.1.6 book / kunai + 0.1.7 stunlock + 0.1.8 Shadow Step rows""")

# ================================================================================================ the 0.1.8 assets (vanilla shapes first)
SS_ASSETS = r'''
# ================================================================= 0.1.8 ASSETS: THE DAGGER SHADOW STEP (research/Shadow-Step-Spec.md; Skyy LOCKED 2026-10-07) - vanilla shapes first
P_SSINT = "Server/Item/Interactions/Weapons/Daggers/SkyyArmory/%s.json"
P_POUNCE = "Server/Item/Interactions/Weapons/Daggers/Primary/Pounce/%s.json"          # the vanilla path of the one override
ID_SS_LAUNCH = "SkyyArmory_Shadow_Step_Launch"
# ---- (1) the route every dagger takes to the charged move (read at build time; a game update that changes it stops the build)
assert _IDX["int"][SS_POUNCE] == [P_POUNCE % SS_POUNCE], _IDX["int"][SS_POUNCE]
VPOUNCE = az_get("int", SS_POUNCE)
assert VPOUNCE["Type"] == "Charging" and sorted(VPOUNCE["Next"]) == ["0", "0.4"] and VPOUNCE["Next"]["0"] == "Weapon_Daggers_Primary_Chain" \
    and VPOUNCE.get("AllowIndefiniteHold") is False and VPOUNCE["Effects"]["ItemAnimationId"] == "PounceStabCharging", VPOUNCE
_vp04 = VPOUNCE["Next"]["0.4"]
assert _vp04["Type"] == "Serial" and _vp04["Interactions"][0]["Var"] == "Pounce_Stamina_Cost" and \
    _vp04["Interactions"][0]["DefaultValue"]["Interactions"][1] == {"Type": "ChangeStat", "StatModifiers": {"Stamina": -4}}, _vp04
SS_VANILLA_STAMINA = -_vp04["Interactions"][0]["DefaultValue"]["Interactions"][1]["StatModifiers"]["Stamina"]          # 4 = the spec's cost
_pounce_users = sorted(n for n in AZ_NAMES if n.startswith("Server/") and n.endswith(".json") and ('"%s"' % SS_POUNCE).encode() in AZ.read(n))
assert _pounce_users == ["Server/Item/Interactions/Weapons/Daggers/Primary/Pounce/Weapon_Daggers_Primary_Pounce_StaminaCondition.json"], _pounce_users
_vsc = az_get("int", "Weapon_Daggers_Primary_Pounce_StaminaCondition")
assert _vsc["Type"] == "StatsCondition" and _vsc["Costs"] == {"Stamina": 0.1} and _vsc["Next"]["Next"]["Var"] == "Pounce" \
    and _vsc["Next"]["Next"]["DefaultValue"] == {"Interactions": [SS_POUNCE]} and _vsc["Failed"] == "Weapon_Daggers_Primary_Chain", _vsc
_vdp = az_get("int", "Weapon_Daggers_Primary")
assert _vdp["Next"]["0.2"]["Var"] == "Pounce_StaminaCondition" and _vdp["Next"]["0.2"]["DefaultValue"] == {"Interactions": ["Weapon_Daggers_Primary_Pounce_StaminaCondition"]}, _vdp
assert az_get("root", "Root_Weapon_Daggers_Primary")["Interactions"] == ["Weapon_Daggers_Primary"]
SS_KEY_S = round(float(min(k for k in _vdp["Next"] if k != "0")) + 0.4, 3)          # 0.2 + 0.4 = the hold the client needs
assert SS_KEY_S == 0.6, SS_KEY_S
SS_REACH, SS_OTHER = [], []
for _di in sorted(_IDX["item"]):
    if not _di.startswith("Weapon_Daggers_"):
        continue
    _dd = item_resolved(_di)
    _dv = _dd.get("InteractionVars") or {}
    if (_dd.get("Interactions") or {}).get("Primary") == "Root_Weapon_Daggers_Primary" and "Pounce" not in _dv and "Pounce_StaminaCondition" not in _dv:
        SS_REACH.append(_di)
    else:
        SS_OTHER.append(_di)
assert len(SS_REACH) >= 14 and not SS_OTHER and "Weapon_Daggers_Crude" in SS_REACH and "Weapon_Daggers_Onyxium" in SS_REACH, (SS_REACH, SS_OTHER)
assert all(az_get("item", i).get("Parent") == "Template_Weapon_Daggers" for i in SS_REACH)
_vtd = az_get("item", "Template_Weapon_Daggers")
assert _vtd["Interactions"] == {"Primary": "Root_Weapon_Daggers_Primary", "Secondary": "Root_Weapon_Daggers_Secondary_Guard",
                                "Ability1": "Root_Weapon_Daggers_Signature_Razorstrike"}, _vtd["Interactions"]
# ---- (2) the vanilla backstab (DamageEntityInteraction AngledDamage: Angle 180 = the attacker in the target's rear, within AngleDistance 80
# degrees of straight behind - the bytecode rule, asserted below): only the Pounce + Razorstrike hits carry a DAMAGE backstab (their angled
# entry has its own calculator, x1.5); the taps' angled entry (inherited from the vanilla tap parents, or "[]" on the metal daggers) has no
# calculator = the same damage with a crit look - so a tap never gets a damage backstab in vanilla and the guaranteed backstab is ours
def _angled(entry, parent_id):
    """the AngledDamage list a var entry really runs: its own, else its Parent's"""
    if "AngledDamage" in entry:
        return entry["AngledDamage"] or []
    return az_get("int", parent_id).get("AngledDamage") or []


_bx, SS_SIG_PLAIN = [], []
for _di in SS_REACH:
    _dv = item_resolved(_di).get("InteractionVars") or {}
    _sig_calc = 0
    for _k in ("Pounce_Stab_Damage", "Pounce_Sweep_Damage", "Razorstrike_Slash_Damage", "Razorstrike_Sweep_Damage", "Razorstrike_Lunge_Damage"):
        _e = _dv[_k]["Interactions"][0]
        for _a in _angled(_e, _e["Parent"]):
            assert _a["Angle"] == 180 and _a["AngleDistance"] == 80, (_di, _k, _a)
            if "DamageCalculator" in _a:
                _bx.append(float(_a["DamageCalculator"]["BaseDamage"]["Physical"]) / float(_e["DamageCalculator"]["BaseDamage"]["Physical"]))
                _sig_calc += 1 if _k.startswith("Razorstrike") else 0
    if _sig_calc == 0:
        SS_SIG_PLAIN.append(_di)          # its signature has no damage backstab: a Razorstrike after a step gets the full guaranteed one
    for _k in ("Swing_Left_Damage", "Swing_Right_Damage", "Stab_Left_Damage", "Stab_Right_Damage"):
        _e = _dv[_k]["Interactions"][0]
        assert all("DamageCalculator" not in _a for _a in _angled(_e, _e["Parent"])), (_di, _k)
assert len(_bx) >= 50 and all(1.45 <= x <= 1.56 for x in _bx), (len(_bx), min(_bx), max(_bx))
SS_BX = round(sorted(_bx)[len(_bx) // 2], 1)          # 1.5 (the vanilla numbers are whole-number roundings of x1.5)
# fix round (critic: the backstab could be spent by a kunai / arrow / spell hit with a dagger in hand): a melee dagger hit lands within the
# longest vanilla dagger selector reach (EndDistance, every file under Weapons/Daggers) + 1 block of slack (lag, the lunge) + half the target
def _ends(x, out):
    if isinstance(x, dict):
        for _k, _v in x.items():
            if _k == "EndDistance" and isinstance(_v, (int, float)):
                out.append(float(_v))
            else:
                _ends(_v, out)
    elif isinstance(x, list):
        for _v in x:
            _ends(_v, out)
    return out


_dend = []
for _n in AZ_NAMES:
    if _n.startswith("Server/Item/Interactions/Weapons/Daggers/") and _n.endswith(".json"):
        _ends(json.loads(AZ.read(_n).decode("utf-8-sig")), _dend)
assert len(_dend) >= 20 and 2.0 <= max(_dend) <= 5.0, (len(_dend), max(_dend) if _dend else None)
SS_MELEE = round(max(_dend) + 1.0, 2)          # 3.75 (the backflip stab) + 1 = 4.75
SS_BACK_DEG = 80
assert SS_BX == 1.5 and SS_SIG_PLAIN == ["Weapon_Daggers_Bronze", "Weapon_Daggers_Bronze_Ancient", "Weapon_Daggers_Claw_Bone", "Weapon_Daggers_Onyxium"], (SS_BX, SS_SIG_PLAIN)
# ---- (3) the override: the vanilla charging kept, "0.4" = the marker launch (no Stamina in the chain - the server pays)
assert SS_ANIM in az_get("anim", "Daggers")["Animations"] and az_has("sound", SS_SND)
SS_POUNCE_JSON = json.loads(json.dumps(VPOUNCE))
SS_POUNCE_JSON["Next"]["0.4"] = ID_SS_LAUNCH
INTS[SS_POUNCE] = SS_POUNCE_JSON          # by id, like Wand_Primary and the bow leap
put(P_POUNCE % SS_POUNCE, SS_POUNCE_JSON)
add_int(P_SSINT, ID_SS_LAUNCH, {"Type": "LaunchProjectile", "RunTime": RT_LAUNCH, "Effects": {"ItemAnimationId": SS_ANIM}, "ProjectileId": SS_MARK})
add_prj(SS_MARK, blink_marker())
SS_PRJS = [SS_MARK]
# ---- (4) the fading shadow: the vanilla Smoke_Black spawner made a short, dark, see-through body-sized burst (no rising column)
_vsm = vanilla_sp("Smoke_Black")
assert _vsm["Particle"]["Texture"] == "Particles/Textures/Smoke/Smoke.png" and ("Common/" + _vsm["Particle"]["Texture"]) in AZ_SET
_ssp = json.loads(json.dumps(_vsm))
_ssp["Shape"] = "Cube"
_ssp["EmitOffset"] = {"X": {"Min": 0.22, "Max": 0.22}, "Y": {"Min": 0.85, "Max": 0.85}, "Z": {"Min": 0.22, "Max": 0.22}}
_ssp["MaxConcurrentParticles"] = 40
_ssp["ParticleLifeSpan"] = {"Min": round(SS_SHADOW_S * 0.8, 3), "Max": SS_SHADOW_S}
_ssp["SpawnRate"] = {"Min": 120, "Max": 120}
_ssp["TotalParticles"] = {"Min": 26, "Max": 26}
_ssp["InitialVelocity"] = {"Speed": {"Min": 0.05, "Max": 0.15}, "Yaw": {"Min": -180, "Max": 180}, "Pitch": {"Min": 60, "Max": 120}}
_ssp.pop("Attractors", None)
_anim = _ssp["Particle"]["Animation"]
_anim["0"]["Color"] = "#1b1526"
_anim["0"]["Opacity"] = 0.42
_anim["50"] = {"Opacity": 0.3}
_anim["100"]["Opacity"] = 0
_anim["100"]["Scale"] = {"X": {"Min": 1.25, "Max": 1.4}, "Y": {"Min": 1.25, "Max": 1.4}}
_ssp["Particle"]["InitialAnimationFrame"]["Color"] = "#1b1526"
_ssp["Particle"]["InitialAnimationFrame"]["Opacity"] = 0.42
_ssp["Particle"]["InitialAnimationFrame"]["Scale"] = {"X": {"Min": 0.55, "Max": 0.8}, "Y": {"Min": 0.55, "Max": 0.8}}
put(P_PSPAWN % PS_SHADOW, _ssp)
_ssy = {"LifeSpan": 0.3, "Spawners": [{"SpawnerId": PS_SHADOW, "PositionOffset": {"X": 0, "Y": 0.9, "Z": 0}}]}
put(P_PSYS % PS_SHADOW, _ssy)
assert PS_SHADOW not in _IDX["psys"] and PS_SHADOW not in _IDX["pspawn"]
FX_BUDGET[PS_SHADOW] = (0.3, SS_SHADOW_S, 0.3 + SS_SHADOW_S)
assert not endless(_ssy, {PS_SHADOW: _ssp}) and _plmax(_ssp) <= SS_SHADOW_S + 1e-9 and max(_anim[k].get("Opacity", 0) for k in _anim) < 0.5
SS_FILES = sorted([P_POUNCE % SS_POUNCE, P_SSINT % ID_SS_LAUNCH, P_PRJ % SS_MARK, P_PSPAWN % PS_SHADOW, P_PSYS % PS_SHADOW])
assert all(p in ASSETS for p in SS_FILES)
# ---- (5) SkyyGear's dagger speed chains (the pinned jar) still reach our override: their Charging "0.2" names the vanilla StaminaCondition
_sset = open(SET_FILE, encoding="utf-8").read()
_sset = _sset[_sset.index("SET = ["):_sset.index("\n]\n", _sset.index("SET = ["))]
_gear_pin = dict(re.findall(r'\("(Skyy\w+)", "([0-9][0-9.]*)"\)', _sset)).get("SkyyGear")
_gear_jar = os.path.join(ROOT, "SkyyGear", "SkyyGear-%s.jar" % _gear_pin)
SS_GEAR = "SkyyGear %s not built here - not checked" % _gear_pin
if os.path.isfile(_gear_jar):
    with zipfile.ZipFile(_gear_jar) as _gz:
        _gn = _gz.namelist()
        assert not [n for n in _gn if os.path.basename(n) in (SS_POUNCE + ".json", "Weapon_Daggers_Primary_Pounce_StaminaCondition.json")], \
            "SkyyGear %s ships the dagger Pounce - SkyyArmory owns it now" % _gear_pin
        _gsp = [n for n in _gn if n.endswith("_Daggers_Weapon_Daggers_Primary.json")]
        for _n in _gsp:
            _gd = json.loads(_gz.read(_n).decode("utf-8-sig"))
            assert _gd["Next"]["0.2"]["DefaultValue"] == {"Interactions": ["Weapon_Daggers_Primary_Pounce_StaminaCondition"]}, (_n, _gd["Next"])
    SS_GEAR = "SkyyGear %s: %d dagger speed chains route the hold to the vanilla Pounce_StaminaCondition (-> our override)" % (_gear_pin, len(_gsp))
print("0.1.8 Shadow Step: %s overridden (its 0.4 s step -> %s -> marker %s); reaches %d daggers (%s); backstab x%s (%d vanilla angled hits); %s" % (
    SS_POUNCE, ID_SS_LAUNCH, SS_MARK, len(SS_REACH), ", ".join(x[len("Weapon_Daggers_"):] for x in SS_REACH), SS_BX, len(_bx), SS_GEAR))
'''
before('''# ================================================================= the SET jars, SkyySkills (anchor + handover), the clash scan''', SS_ASSETS)
rep('''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS)) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) + 1 + len(BK_PRJS) == len(PRJS) \\
    and set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS) == set(PRJS)          # 0.1.6: + the book orbs / Levitate + return markers''',
    '''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS)) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) + 1 + len(BK_PRJS) + len(SS_PRJS) == len(PRJS) \\
    and set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS) == set(PRJS)          # 0.1.6: + the book orbs / Levitate + return markers; 0.1.8: + the Shadow Step marker''')

# ================================================================================================ the per-metal cooldown table, read-only rows, the file
SS_TABLES = r'''
# ---- 0.1.8: the Shadow Step cooldown by metal (one row, an entry per metal + Other)
SS_TAB = [("dagger.shadowStep.cooldown", "Shadow Step cooldown by metal (s)", "shadow", "dec", "0", "30", "s",
           "Other = every non-metal dagger (Bone, Bronze, pack daggers).", "SS_CD", SS_CD, SS_METALS_DEF)]
SS_TAB_ROWS = []
for _k, _lab, _cat, _vt, _mn, _mx, _u, _hlp, _fld, _defs, _ms in SS_TAB:
    SS_TAB_ROWS.append((_k, _lab, _cat, "table", "", _mn, _mx, "%s;none;%s" % (_vt, "Value"), _u, "live", _hlp,
                        "reload@%s:%s.;check=ArmoryHooks.checkShadow" % (CFG_FILE, _k)))
SS_TAB_LINES = []
for _k, _lab, _cat, _vt, _mn, _mx, _u, _hlp, _fld, _defs, _ms in SS_TAB:
    SS_TAB_LINES.append("# " + _lab + ": " + _hlp)
    SS_TAB_LINES += ["%s.%s=%s" % (_k, _m, num(_d)) for _m, _d in zip(_ms, _defs)]
'''
before('''CFG_LINES = [''', SS_TABLES)
rep('''] + [x for _r in CFG_ST for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
    "",
    "# ---- Mana check (server log)",''', '''] + [x for _r in CFG_ST for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
    "",
    "# ---- dagger Shadow Step (SkyyArmory 0.1.8; research/Shadow-Step-Spec.md, Skyy 2026-10-07): hold the dagger attack + release = vanish, appear behind the enemy you aim at",
] + [x for _r in CFG_SS for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + SS_TAB_LINES + [
    "",
    "# ---- Mana check (server log)",''')
rep('''            ("book", "Spellbook burst"), ("lev", "Spellbook Levitate"), ("kunai", "Kunai"), ("stun", "Monk stunlock"), ("monk", "Monk weapons (fixed)"),''',
    '''            ("book", "Spellbook burst"), ("lev", "Spellbook Levitate"), ("kunai", "Kunai"), ("shadow", "Dagger Shadow Step"), ("stun", "Monk stunlock"),
            ("monk", "Monk weapons (fixed)"),''')
SS_FIXED = r'''
FIXED.append(("fixed.shadow.keys", "Shadow Step keys (fixed in the jar)", "shadow",
              "hold the dagger attack %s s and release (the vanilla Pounce hold) - tap combo, right-click guard + signature stay vanilla" % num(SS_KEY_S),
              "The client-predicted charge of every dagger; the vanilla Pounce leap is replaced."))
FIXED.append(("fixed.shadow.look", "Shadow look (fixed in the jar)", "shadow",
              "a dark see-through shadow where you stood, gone in about %s s (trav.fx off = none)" % num(SS_SHADOW_S), "The particle asset (client side)."))
FIXED.append(("fixed.shadow.backstab", "Backstab factor (fixed in the jar)", "shadow",
              "x%s = the vanilla dagger backstab (Pounce / Razorstrike from behind), then x (1 + backstabBonus)" % num(SS_BX),
              "Read from the vanilla daggers at build time."))
'''
before('''FIXED_VAL = dict((f[0], f[3]) for f in FIXED)''', SS_FIXED)
rep('''] + [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], "field:ArmoryCfg." + r[11]) for r in CFG_NEW] + BK_TAB_ROWS + [''',
    '''] + [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], "field:ArmoryCfg." + r[11]) for r in CFG_NEW] + BK_TAB_ROWS + SS_TAB_ROWS + [''')
after('''assert len(BK_TAB_LINES) == sum(1 + len(t[10]) for t in BK_TAB) and all(_l in CFG_TEXT for _l in BK_TAB_LINES), "0.1.6 table lines in the default file"
''', '''for _k, _lab, _cat, _vt, _mn, _mx, _u, _hlp, _fld, _defs, _ms in SS_TAB:        # 0.1.8: every cooldown entry's default is in the file
    assert [_dp.get("%s.%s" % (_k, _m)) for _m in _ms] == [num(_d) for _d in _defs], (_k, [_dp.get("%s.%s" % (_k, _m)) for _m in _ms])
assert all(_l in CFG_TEXT for _l in SS_TAB_LINES), "0.1.8 table lines in the default file"
''')

# ================================================================================================ ArmoryCfg: the table field, the loader, the text
after('''F(cfg, "public static volatile String STUN_TEXT = \\"\\";")          # 0.1.7
''', '''for _k, _lab, _cat, _vt, _mn, _mx, _u, _hlp, _fld, _defs, _ms in SS_TAB:        # 0.1.8 the Shadow Step cooldown table (index = SS_METALS)
    F(cfg, "public static volatile double[] %s = %s;" % (_fld, jdbls(_defs)))
    F(cfg, "public static final double[] %s_DEF = %s;" % (_fld, jdbls(_defs)))
F(cfg, "public static volatile String SHADOW_TEXT = \\"\\";")          # 0.1.8
''')
before('''M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''', '''# 0.1.8: the Shadow Step's live numbers (bridge armory:shadow, the start line)
M(cfg, r"""
public static String shadowText() {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < @PKG@.ArmoryDefs.SS_METALS.length; i++) {
    if (i > 0) sb.append(", ");
    sb.append(@PKG@.ArmoryDefs.SS_METALS[i]).append(' ').append(cfmt(SS_CD[i])).append('s');
  }
  return "dagger Shadow Step " + (SS_ON ? "on" : "OFF") + " - target " + SS_RANGE + " blocks in a " + SS_CONE + " deg cone around your aim (hostile first, neutral "
    + (SS_NEUTRAL ? "too" : "never") + ", players " + (SS_PLAYERS ? "where PvP is on" : "never") + "), arrive " + SS_BEHIND + " behind facing its back, no target = " + SS_FAR
    + " blocks straight (no void check), backstab window " + SS_WINDOW + " s x@BX@ x (1 + " + SS_BONUS + "), " + SS_STAM + " Stamina - cooldown " + sb.toString();
}""".replace("@BX@", num(SS_BX)))
''')
after('''  STUN_TEXT = stunText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:stun", STUN_TEXT); } catch (Throwable tst) { }
''', '''  SS_ON = bool(c.getProperty("dagger.shadowStep.enabled"), true);          // 0.1.8
  SS_RANGE = intOf(c.getProperty("dagger.shadowStep.targetRange"), 24, 4, 48);
  SS_CONE = intOf(c.getProperty("dagger.shadowStep.targetCone"), 30, 10, 180);
  SS_BEHIND = dec(c.getProperty("dagger.shadowStep.behind"), 1.5, 0.5, 4.0);
  SS_FAR = intOf(c.getProperty("dagger.shadowStep.noTargetDistance"), 18, 2, 40);
  SS_WINDOW = dec(c.getProperty("dagger.shadowStep.backstabWindow"), 3.0, 0.5, 10.0);
  SS_BONUS = dec(c.getProperty("dagger.shadowStep.backstabBonus"), 0.1, 0.0, 1.0);
  SS_STAM = dec(c.getProperty("dagger.shadowStep.staminaCost"), 4.0, 0.0, 10.0);
  SS_PLAYERS = bool(c.getProperty("dagger.shadowStep.players"), true);
  SS_NEUTRAL = bool(c.getProperty("dagger.shadowStep.neutral"), true);          // fix round
  SS_CD = tab(c, "dagger.shadowStep.cooldown.", @PKG@.ArmoryDefs.SS_METALS, SS_CD_DEF, 0.0, 30.0);
  SHADOW_TEXT = shadowText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:shadow", SHADOW_TEXT); } catch (Throwable tss) { }
''')

# ================================================================================================ ArmoryDefs: the marker code, the metal of a dagger
after('''F(dfs, "public static final String[] STUN_PRE = %s;" % jarr(STUN_PRE))          # 0.1.7: the Monk combo weapons (stunlock count)
''', '''for f in ("public static final String SS_MARK = %s;" % jstr(SS_MARK), "public static final int SS_CODE = %d;" % SS_CODE,          # 0.1.8
          "public static final String[] SS_METALS = %s;" % jarr(SS_METALS_DEF), "public static final double SS_BX = %r;" % SS_BX,
          "public static final String[] SS_SIG_PLAIN = %s;" % jarr(SS_SIG_PLAIN), "public static final double SS_BACK_DEG = %r;" % float(SS_BACK_DEG),
          "public static final double SS_MELEE = %r;" % SS_MELEE):          # fix round: the melee reach of a dagger hit
    F(dfs, f)
''')
rep('''  for (int i = 0; i < K_RMARK.length; i++) m.put(K_RMARK[i], Integer.valueOf(9000 + i));     // 0.1.6: the kunai return markers
''', '''  for (int i = 0; i < K_RMARK.length; i++) m.put(K_RMARK[i], Integer.valueOf(9000 + i));     // 0.1.6: the kunai return markers
  m.put(SS_MARK, Integer.valueOf(SS_CODE));          // 0.1.8: the Shadow Step marker
''')
before('''# THE damage rule of ArmoryTuneSys (spec 3.1 + 15.2), plain values only: 1 = untouched''', '''# 0.1.8: the Shadow Step cooldown entry of a dagger - a metal named as a WHOLE part of the id (split at _), else the last entry (Other)
M(dfs, r"""
public static int ssMetal(String id) {
  int other = SS_METALS.length - 1;
  if (id == null) return other;
  String r = "_" + id.trim().toLowerCase() + "_";
  for (int i = 0; i < other; i++) if (r.indexOf("_" + SS_METALS[i].toLowerCase() + "_") >= 0) return i;
  return other;
}""")
M(dfs, r"""
public static boolean sigPlain(String id) {
  if (id == null) return false;
  for (int i = 0; i < SS_SIG_PLAIN.length; i++) if (SS_SIG_PLAIN[i].equals(id)) return true;
  return false;
}""")
''')

# ================================================================================================ ArmoryHooks: the table check
after('''M(hooks, "public static String checkKunai(String key, String value) { return checkIn(key, value, @PKG@.ArmoryDefs.K_METALS, \\"Crude, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril or Onyxium\\"); }")
''', '''M(hooks, "public static String checkShadow(String key, String value) { return checkIn(key, value, @PKG@.ArmoryDefs.SS_METALS, \\"Crude, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium or Other\\"); }")
''')

# ================================================================================================ engine members the 0.1.8 code calls (probed + bytecode)
SS_PROBE = r'''# ---- 0.1.8 Shadow Step: the facing teleport, the target's body yaw, the signature-chain check (VERIFIED 2026-10-07; every member probed)
T.update({"IMOD": "com.hypixel.hytale.server.core.modules.interaction.InteractionModule",
          "IMGR": "com.hypixel.hytale.server.core.entity.InteractionManager",
          "ICHN": "com.hypixel.hytale.server.core.entity.InteractionChain",
          "ITYP": "com.hypixel.hytale.protocol.InteractionType"})
for _c, _m, _r, _a in ((T["IMOD"], "get", T["IMOD"], []), (T["IMOD"], "getInteractionManagerComponent", T["CTYPE"], []),
                       (T["IMGR"], "getChains", "it.unimi.dsi.fastutil.ints.Int2ObjectMap", []), (T["ICHN"], "getType", T["ITYP"], []),
                       (T["TC"], "getRotation", T["R3F"], []), (T["R3F"], "yaw", "float", []), (T["HR"], "getRotation", T["R3F"], []),
                       (T["TP"], "setHeadRotation", T["TP"], ["com.hypixel.hytale.math.vector.Rotation3fc"]), (T["BOX"], "height", "double", [])):
    probe_sig(_c, _m, _r, _a)
for _f in ("Ability1", "Ability2", "Ability3"):
    _fld = pool.get(T["ITYP"]).getField(_f)
    assert JMod.isPublic(_fld.getModifiers()) and JMod.isStatic(_fld.getModifiers()), "InteractionType.%s is not public static" % _f
    PROBED.append("InteractionType.%s" % _f)
assert "java.util.Map" in [str(i.getName()) for i in pool.get("it.unimi.dsi.fastutil.ints.Int2ObjectMap").getInterfaces()], "Int2ObjectMap is no java.util.Map"
# the server sends a player Teleport's body AND head rotation to the client (TeleportSystems$PlayerMoveSystem.teleportToPosition):
_tps = _calls("com.hypixel.hytale.server.core.modules.entity.teleport.TeleportSystems$PlayerMoveSystem", "teleportToPosition")
assert "getRotation" in _tps and "teleportRotation" in _tps and "getHeadRotation" in _tps and "queueAndSendClientTeleport" in _tps, \
    "a player Teleport no longer carries its rotation to the client - re-check Shadow Step facing"
# the vanilla backstab = DamageEntityInteraction's angled entry against the target's body yaw (the snapshot's getBodyRotation) - our arrival
# spot is behind THAT yaw (TransformComponent rotation)
_dea = _calls("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.DamageEntityInteraction", "attemptEntityDamage0")
assert "getBodyRotation" in _dea and "yaw" in _dea and "atan2" in _dea and "wrapAngle" in _dea and "compareAngle" in _dea and ".angleRad" in _dea \
    and ".angleDistanceRad" in _dea, \
    "DamageEntityInteraction's angled (backstab) rule no longer compares the attacker angle with the target's body yaw: %s" % _dea
_hfd = _ops("com.hypixel.hytale.server.core.modules.physics.util.PhysicsMath", "headingFromDirection")
assert _hfd == ["atan2"], _hfd
PROBED.append("0.1.8: Teleport body + head rotation sent to the client; DamageEntityInteraction angled vs body yaw; PhysicsMath heading = atan2(-dx, -dz) (bytecode)")
# fix round (critic): who is an ENEMY = the engine attitude on the mob's WorldSupport component; a melee hit = a Physical-family cause
T.update({"WSUP": "com.hypixel.hytale.server.npc.role.support.WorldSupport", "ATT": "com.hypixel.hytale.server.core.asset.type.attitude.Attitude"})
for _c, _m, _r, _a in ((T["WSUP"], "getComponentType", T["CTYPE"], []), (T["WSUP"], "getOverriddenAttitude", T["ATT"], [T["REF"]]),
                       (T["WSUP"], "getDefaultPlayerAttitude", T["ATT"], []), (T["DCS"], "getInherits", S_, []), (T["DCS"], "getId", S_, []),
                       (T["DCS"], "getAssetMap", "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", [])):
    probe_sig(_c, _m, _r, _a)
for _f in ("HOSTILE", "NEUTRAL", "FRIENDLY", "REVERED", "IGNORE"):
    _fld = pool.get(T["ATT"]).getField(_f)
    assert JMod.isPublic(_fld.getModifiers()) and JMod.isStatic(_fld.getModifiers()), "Attitude.%s is not public static" % _f
    PROBED.append("Attitude.%s" % _f)
# every role NPC carries WorldSupport (Role.createAndAttach puts it on the holder); getOverriddenAttitude is a pure map read (no side effect)
_rca = []
for _mm in pool.get("com.hypixel.hytale.server.npc.role.Role").getDeclaredMethods():
    if str(_mm.getName()) != "createAndAttach":
        continue
    _cp, _it = _mm.getMethodInfo().getConstPool(), _mm.getMethodInfo().getCodeAttribute().iterator()
    while _it.hasNext():
        _p = _it.next()
        if _it.byteAt(_p) in (0xb6, 0xb8, 0xb9):
            _ix = _it.u16bitAt(_p + 1)
            if _cp.getTag(_ix) == _JCP.CONST_InterfaceMethodref:
                _rca.append(str(_cp.getInterfaceMethodrefClassName(_ix)) + "." + str(_cp.getInterfaceMethodrefName(_ix)))
            else:
                _rca.append(str(_cp.getMethodrefClassName(_ix)) + "." + str(_cp.getMethodrefName(_ix)))
_wsi = [i for i, x in enumerate(_rca) if x == T["WSUP"] + ".getComponentType"]
assert len(_wsi) == 1 and _rca[_wsi[0] + 1].endswith("Holder.putComponent"), "Role.createAndAttach no longer puts WorldSupport on the NPC: %s" % _rca
_goa = _calls(T["WSUP"], "getOverriddenAttitude")
assert _goa == ["getIndex", "get", "getAttitudeOverride"] or (set(_goa) <= {"getIndex", "get", "getAttitudeOverride", ".attitudeOverrideMemory"} and "getAttitudeOverride" in _goa), _goa
PROBED.append("fix round: WorldSupport on every role NPC (Role.createAndAttach), its attitude override + default player attitude (bytecode)")
'''
before('''print("engine members probed: %d" % len(PROBED))''', SS_PROBE)

# ================================================================================================ the classes (declared up front: javassist needs them)
rep('''srec = pool.makeClass(PKG + ".StunRec")
stun = pool.makeClass(PKG + ".Stun")
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick,
       gmath, gstate, grap, gimp, gbolt, gfall, lstate, leap, lvst, levc, kst, kimp, kjob, kun, srec, stun]''', '''srec = pool.makeClass(PKG + ".StunRec")
stun = pool.makeClass(PKG + ".Stun")
# 0.1.8 the dagger Shadow Step (the job reuses KunaiJob kind 3)
shd = pool.makeClass(PKG + ".Shadow")
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick,
       gmath, gstate, grap, gimp, gbolt, gfall, lstate, leap, lvst, levc, kst, kimp, kjob, kun, srec, stun, shd]''')

# ================================================================================================ TravMath: the pure 0.1.8 maths (bare-JVM tested)
after('''M(tmath, "public static boolean emitOk(long now, long emitMs, long until) { return now + emitMs <= until; }")
''', r'''# 0.1.8 Shadow Step: the angle (degrees) between your aim d and the way to a target v (no direction = 180)
M(tmath, r"""
public static double offDeg(double dx, double dy, double dz, double vx, double vy, double vz) {
  double a = Math.sqrt(dx * dx + dy * dy + dz * dz);
  double b = Math.sqrt(vx * vx + vy * vy + vz * vz);
  if (!(a > 1.0E-9) || !(b > 1.0E-9)) return 180.0;
  double c = (dx * vx + dy * vy + dz * vz) / (a * b);
  if (c > 1.0) c = 1.0;
  if (c < -1.0) c = -1.0;
  return Math.toDegrees(Math.acos(c));
}""")
# 0.1.8: where you arrive behind a target at (tx, ty, tz) whose body yaw is yaw (forward = (-sin yaw, -cos yaw), PhysicsMath's heading rule,
# so behind = (+sin, +cos)), r blocks from its centre: the nearest free spot of its back half (0, +-30, +-60, +-90 degrees; the same height,
# 1 up, 1 down; the body box free and the line from its centre (height cy) to your chest clear), else beside it (+-120); null = none.
# -> { x, y, z, 0 = back half / 1 = beside }
M(tmath, r"""
public static double[] arrive(@PKG@.TravGrid g, double tx, double ty, double tz, double yaw, double r, double cy) {
  if (g == null || !(r > 0.0) || Double.isNaN(yaw)) return null;
  double bx = Math.sin(yaw);
  double bz = Math.cos(yaw);
  double ix = tx + bx * r;
  double iz = tz + bz * r;
  double[] angs = new double[] { 0.0, 30.0, -30.0, 60.0, -60.0, 90.0, -90.0, 120.0, -120.0 };
  double[] hs = new double[] { 0.0, 1.0, -1.0 };
  for (int pass = 0; pass < 2; pass++) {
    double best = 1.0E18;
    double[] out = null;
    int a0 = pass == 0 ? 0 : 7;
    int a1 = pass == 0 ? 7 : 9;
    for (int k = a0; k < a1; k++) {
      double rad = Math.toRadians(angs[k]);
      double cx = bx * Math.cos(rad) - bz * Math.sin(rad);
      double cz = bx * Math.sin(rad) + bz * Math.cos(rad);
      for (int h = 0; h < hs.length; h++) {
        double x = tx + cx * r;
        double y = ty + hs[h];
        double z = tz + cz * r;
        if (body(g, x, y, z) != 0) continue;
        if (!clear(g, tx, cy, tz, x, y + 1.0, z)) continue;
        double d2 = (x - ix) * (x - ix) + (y - ty) * (y - ty) + (z - iz) * (z - iz);
        if (d2 < best - 1.0E-9) { best = d2; out = new double[] { x, y, z, (double) pass }; }
      }
    }
    if (out != null) return out;
  }
  return null;
}""")
# 0.1.8 the vanilla backstab rule (DamageEntityInteraction.attemptEntityDamage0): the attacker at (ax, az) is in the rear of a target at
# (tx, tz) with body yaw yaw when the way target -> attacker is within maxDeg of the target's back (sin yaw, cos yaw)
M(tmath, r"""
public static boolean behind(double tx, double tz, double yaw, double ax, double az, double maxDeg) {
  double dx = ax - tx;
  double dz = az - tz;
  if (!(dx * dx + dz * dz > 1.0E-9) || Double.isNaN(yaw)) return false;
  return offDeg(dx, 0.0, dz, Math.sin(yaw), 0.0, Math.cos(yaw)) < maxDeg;
}""")
# 0.1.8 the guaranteed backstab: the vanilla backstab factor x (1 + bonus); a hit that already got the vanilla damage backstab (a signature
# hit from behind) the bonus only - never a double backstab
M(tmath, r"""
public static double backstab(boolean already, double bx, double bonus) {
  double b = bonus > 0.0 ? bonus : 0.0;
  double x = bx > 1.0 ? bx : 1.0;
  return already ? 1.0 + b : x * (1.0 + b);
}""")
''')

# ================================================================================================ Shadow (Java; before KunaiJob.run, ArmoryTrav.added and ArmoryTuneSys)
SS_JAVA = r'''
# ---------------------------------------------------------------- 0.1.8 THE DAGGER SHADOW STEP (research/Shadow-Step-Spec.md; Skyy LOCKED 2026-10-07)
for f in ("public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",    # u -> Long (cooldown start)
          "public static final java.util.concurrent.ConcurrentHashMap ARMED = new java.util.concurrent.ConcurrentHashMap();",   # u -> Long (backstab until)
          "public static volatile java.util.function.Function SIG = null;",          # HARNESS SEAM ONLY (null in the game = the attacker's chains)
          "public static volatile long MARKS = 0L;", "public static volatile long STEPS = 0L;", "public static volatile long TARGETED = 0L;",
          "public static volatile long STRAIGHT = 0L;", "public static volatile long REFUSED = 0L;", "public static volatile long BACKSTABS = 0L;",
          "public static volatile String LAST_WHY = \"\";", "public static volatile String LAST_TARGET = \"\";",
          "public static final double EYE = %r;" % SS_EYE, "public static final String FX = %s;" % jstr(PS_SHADOW),
          "public static final String SND = %s;" % jstr(SS_SND)):
    F(shd, f)
M(shd, r"""public static void warn(String key, String msg) { @PKG@.ArmoryLog.warnOnce("shadow:" + key, msg); }""")
M(shd, r"""
public static boolean dagger(String item) { return item != null && item.toLowerCase().indexOf("dagger") >= 0; }""")
# the grapple's "never yanked" words (traders, pets, mounts, hub NPCs): a substring of the role name, any case
M(shd, r"""
public static boolean word(String role, String words) {
  if (role == null || words == null) return false;
  String r = role.toLowerCase();
  String[] ws = words.split(",");
  for (int i = 0; i < ws.length; i++) {
    String w = ws[i].trim().toLowerCase();
    if (w.length() > 0 && r.indexOf(w) >= 0) return true;
  }
  return false;
}""")
M(shd, r"""
public static boolean protect(@CAC@ acc, @REF@ t) {
  try {
    if (acc.getComponent(t, @INVU@.getComponentType()) != null) return true;
    Object no = acc.getComponent(t, @NPC@.getComponentType());
    if (no instanceof @NPC@ && word(((@NPC@) no).getRoleName(), @PKG@.ArmoryCfg.G_NOYANK)) return true;
  } catch (Throwable t2) { }
  return false;
}""")
M(shd, r"""
public static double height(@CAC@ acc, @REF@ r) {
  try {
    @BBX@ b = (@BBX@) acc.getComponent(r, @BBX@.getComponentType());
    if (b == null || b.getBoundingBox() == null) return 1.8;
    double h = b.getBoundingBox().height();
    return h > 0.0 && h < 32.0 ? h : 1.8;
  } catch (Throwable t) { return 1.8; }
}""")
M(shd, r"""
public static float bodyYaw(@CAC@ acc, @REF@ r) {
  try {
    @TC@ tc = (@TC@) acc.getComponent(r, @TC@.getComponentType());
    if (tc == null || tc.getRotation() == null) return Float.NaN;
    return tc.getRotation().yaw();
  } catch (Throwable t) { return Float.NaN; }
}""")
# the area query on a ComponentAccessor (the job runs on the world thread outside the systems: a Store); the harness seam first
M(shd, r"""
public static java.util.List near(@CAC@ acc, double x, double y, double z, double r) {
  try {
    if (@PKG@.ArmoryTrav.NEAR != null) {
      Object o = @PKG@.ArmoryTrav.NEAR.apply(new double[] { x, y, z, r });
      return o instanceof java.util.List ? new java.util.ArrayList((java.util.List) o) : new java.util.ArrayList();
    }
    java.util.List l = @TU@.getAllEntitiesInSphere(new @VEC@(x, y, z), r, acc);
    return l == null ? new java.util.ArrayList() : new java.util.ArrayList(l);
  } catch (Throwable t) { warn("near", "the Shadow Step area query failed (" + t + ")"); return new java.util.ArrayList(); }
}""")
# fix round (critic): the mob's attitude toward YOU, from the engine (WorldSupport, on every role NPC): 0 = HOSTILE, 1 = NEUTRAL (or no
# attitude to read), 2 = FRIENDLY / REVERED / IGNORE (livestock, pets, villagers, summoned allies). The override toward you first (a pure map
# read), else the role's default player attitude - never WorldSupport.getAttitude (it builds the blackboard view and needs a cache)
M(shd, r"""
public static int attitude(@CAC@ acc, @REF@ t, @REF@ me) {
  try {
    Object o = acc.getComponent(t, @WSUP@.getComponentType());
    if (!(o instanceof @WSUP@)) return 1;
    @WSUP@ ws = (@WSUP@) o;
    @ATT@ a = me == null ? null : ws.getOverriddenAttitude(me);
    if (a == null) a = ws.getDefaultPlayerAttitude();
    if (a == null) return 1;
    if (a == @ATT@.HOSTILE) return 0;
    if (a == @ATT@.NEUTRAL) return 1;
    return 2;
  } catch (Throwable x) { return 1; }
}""")
# THE TARGET (spec 2): an enemy (kind 0: a mob you can hurt, or a player where PvP is on + trav.players), not protected, players only with
# dagger.shadowStep.players; its centre within targetRange of your eye, inside the targetCone (its FULL width - at most half of it off your
# aim), line of sight. Fix round: hostile mobs + players (tier 0) always beat neutral mobs (tier 1, only with dagger.shadowStep.neutral);
# friendly mobs never. Inside a tier the smallest angle wins (ties: the nearer)
M(shd, r"""
public static @REF@ pick(@CAC@ acc, @REF@ me, java.util.UUID u, double ex, double ey, double ez, double[] d, @PKG@.TravGrid g, boolean pvp) {
  if (g == null || d == null) return null;
  java.util.List l = near(acc, ex, ey, ez, (double) @PKG@.ArmoryCfg.SS_RANGE + 2.0);
  @REF@ best = null;
  int bt = 9;
  double bo = 1.0E9;
  double bd = 1.0E9;
  for (int k = 0; k < l.size(); k++) {
    Object o = l.get(k);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (t.equals(me)) continue;
    if (@PKG@.ArmoryTrav.kind(acc, t, me, u, pvp) != 0) continue;
    boolean player = @PKG@.Kunai.prOf(acc, t) != null;
    if (player && !@PKG@.ArmoryCfg.SS_PLAYERS) continue;
    if (!player && protect(acc, t)) continue;
    int tr = player ? 0 : attitude(acc, t, me);
    if (tr > 1 || (tr == 1 && !@PKG@.ArmoryCfg.SS_NEUTRAL) || tr > bt) continue;
    @VEC@ p = @PKG@.ArmoryTrav.posOf(acc, t);
    if (p == null) continue;
    double cy = p.y + height(acc, t) * 0.5;
    double vx = p.x - ex;
    double vy = cy - ey;
    double vz = p.z - ez;
    double dist = Math.sqrt(vx * vx + vy * vy + vz * vz);
    if (dist > (double) @PKG@.ArmoryCfg.SS_RANGE || dist < 0.3) continue;
    double off = @PKG@.TravMath.offDeg(d[0], d[1], d[2], vx, vy, vz);
    if (off > (double) @PKG@.ArmoryCfg.SS_CONE * 0.5) continue;
    if (!@PKG@.TravMath.clear(g, ex, ey, ez, p.x, cy, p.z)) continue;
    if (tr < bt || off < bo - 1.0E-6 || (Math.abs(off - bo) <= 1.0E-6 && dist < bd)) { best = t; bt = tr; bo = off; bd = dist; }
  }
  return best;
}""")
# the teleport (the kunai port + a facing): face = body yaw + head pitch / yaw toward the target's back; else your rotation kept. The
# velocity is kept (a damaging fall is never erased - the blink's keepFall rule)
M(shd, r"""
public static boolean port(@ST@ st, @REF@ ref, @WLD@ w, double x, double y, double z, boolean face, float pitch, float yaw) {
  try {
    @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
    if (tc == null) return false;
    @TP@ tp = @TP@.createForPlayer(w, new @VEC@(x, y, z), face ? new @R3F@(0.0f, yaw, 0.0f) : tc.getRotation());
    if (face) tp.setHeadRotation(new @R3F@(pitch, yaw, 0.0f));
    else {
      try {
        @HR@ hr = (@HR@) st.getComponent(ref, @HR@.getComponentType());
        if (hr != null && hr.getRotation() != null) tp.setHeadRotation(hr.getRotation());
      } catch (Throwable t2) { }
    }
    tp = tp.withoutVelocityReset();
    st.putComponent(ref, @TP@.getComponentType(), tp);
    return true;
  } catch (Throwable t) { warn("port", "a Shadow Step teleport failed (" + t + ")"); return false; }
}""")
M(shd, r"""
public static void sweep(long now) {
  if (LAST.size() > 512) {
    java.util.Iterator it = LAST.values().iterator();
    while (it.hasNext()) { Object o = it.next(); if (!(o instanceof Long) || now - ((Long) o).longValue() > 60000L) it.remove(); }
  }
  if (ARMED.size() > 512) {
    java.util.Iterator ia = ARMED.values().iterator();
    while (ia.hasNext()) { Object o = ia.next(); if (!(o instanceof Long) || now > ((Long) o).longValue()) ia.remove(); }
  }
}""")
# THE STEP (world thread, outside the systems - the kunai teleport path; KunaiJob kind 3, pt = the aim)
M(shd, r"""
public static void step(@PKG@.KunaiJob j) {
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(j.u); } catch (Throwable t0) { pr = null; }
  @REF@ ref = (pr == null || !pr.isValid()) ? null : pr.getReference();
  @ST@ st = (ref == null || !ref.isValid()) ? null : ref.getStore();
  if (st == null || st != j.st) { LAST_WHY = "the stepper left this world"; return; }
  if (!@PKG@.ArmoryCfg.SS_ON) { LAST_WHY = "Shadow Step off"; return; }
  if (@PKG@.ArmoryTrav.dead(st, ref)) { LAST_WHY = "dead"; return; }
  if (@PKG@.Leap.mounted(st, ref)) { REFUSED = REFUSED + 1L; LAST_WHY = "mounted"; return; }
  String item = @PKG@.Leap.hand(st, ref, j.u);
  if (!@PKG@.ArmoryTrav.allowed(j.u, item)) { REFUSED = REFUSED + 1L; LAST_WHY = "class lock"; return; }
  long now = System.currentTimeMillis();
  sweep(now);
  int mi = @PKG@.ArmoryDefs.ssMetal(item);
  long cd = Math.round(@PKG@.ArmoryCfg.SS_CD[mi] * 1000.0);
  Object lp = LAST.get(j.u);
  if (lp instanceof Long && now - ((Long) lp).longValue() < cd) {
    REFUSED = REFUSED + 1L;
    LAST_WHY = "cooldown";
    @PKG@.ArmoryTrav.tell(pr, "Shadow Step is ready in " + @PKG@.TravMath.fmt((double) (cd - (now - ((Long) lp).longValue())) / 1000.0) + " s.");
    return;
  }
  @VEC@ pos = @PKG@.ArmoryTrav.posOf(st, ref);
  @WLD@ w = @PKG@.ArmoryTrav.worldOf(st);
  double[] d = j.pt;
  if (pos == null || w == null || d == null || d.length < 3) { LAST_WHY = "no position"; return; }
  double dl = Math.sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]);
  if (!(dl > 1.0E-6)) { LAST_WHY = "no aim"; return; }
  double dx = d[0] / dl;
  double dy = d[1] / dl;
  double dz = d[2] / dl;
  @PKG@.TravGrid g = @PKG@.ArmoryTrav.grid(w);
  double sx = pos.x;
  double sy = pos.y;
  double sz = pos.z;
  double ex = sx;
  double ey = sy + EYE;
  double ez = sz;
  @REF@ tgt = pick(st, ref, j.u, ex, ey, ez, new double[] { dx, dy, dz }, g, @PKG@.ArmoryTrav.pvp(w));
  double tx = 0.0;
  double ty = 0.0;
  double tz = 0.0;
  boolean face = false;
  float pitch = 0.0f;
  float yaw = 0.0f;
  if (tgt != null) {
    @VEC@ tp = @PKG@.ArmoryTrav.posOf(st, tgt);
    float tyaw = bodyYaw(st, tgt);
    if (tp == null || Float.isNaN(tyaw)) { LAST_WHY = "the target has no position"; return; }
    double h = height(st, tgt);
    double r = Math.max(@PKG@.ArmoryCfg.SS_BEHIND, @PKG@.Kunai.thick(st, tgt) * 0.5 + 0.5);
    double cy = tp.y + h * 0.5;
    double[] a = @PKG@.TravMath.arrive(g, tp.x, tp.y, tp.z, (double) tyaw, r, cy);
    if (a == null) {
      REFUSED = REFUSED + 1L;
      LAST_WHY = "no room behind the target - nothing spent";
      @PKG@.ArmoryTrav.tell(pr, "No room behind that enemy - nothing spent.");
      return;
    }
    tx = a[0];
    ty = a[1];
    tz = a[2];
    double fx = tp.x - tx;
    double fy = cy - (ty + EYE);
    double fz = tp.z - tz;
    yaw = @PHM@.headingFromDirection(fx, fz);
    pitch = @PHM@.pitchFromDirection(fx, fy, fz);
    face = true;
    LAST_TARGET = (a[3] > 0.5 ? "beside " : "behind ") + @PKG@.TravMath.fmt(r) + " at yaw " + @PKG@.TravMath.fmt((double) tyaw);
  } else {
    double t = @PKG@.TravMath.scan(g, sx, sy, sz, dx, dy, dz, (double) @PKG@.ArmoryCfg.SS_FAR, 0);          // no void check (Skyy)
    if (!(t > 0.0)) {
      REFUSED = REFUSED + 1L;
      LAST_WHY = "no free spot ahead - nothing spent";
      @PKG@.ArmoryTrav.tell(pr, "No room to Shadow Step there - nothing spent.");
      return;
    }
    tx = sx + dx * t;
    ty = sy + dy * t;
    tz = sz + dz * t;
    LAST_TARGET = "";
  }
  double mv = Math.sqrt((tx - sx) * (tx - sx) + (ty - sy) * (ty - sy) + (tz - sz) * (tz - sz));
  if (mv < 1.0) { REFUSED = REFUSED + 1L; LAST_WHY = "would not move you 1 block - nothing spent"; return; }
  if (@PKG@.Kunai.arena(j.u, new double[] { sx, sy, sz }, new double[] { tx, ty, tz })) {
    REFUSED = REFUSED + 1L;
    LAST_WHY = "a locked arena - nothing spent";
    @PKG@.ArmoryTrav.tell(pr, "A locked arena blocks your Shadow Step - nothing spent.");
    return;
  }
  double stam = @PKG@.ArmoryCfg.SS_STAM;
  if (@PKG@.ArmoryCfg.STAMINA_CAP > 0 && stam > (double) @PKG@.ArmoryCfg.STAMINA_CAP) stam = (double) @PKG@.ArmoryCfg.STAMINA_CAP;
  if (@PKG@.Leap.take(st, ref, stam, 0.0) == 0) {
    REFUSED = REFUSED + 1L;
    LAST_WHY = "too little Stamina";
    @PKG@.ArmoryTrav.tell(pr, "Not enough Stamina for Shadow Step - " + @PKG@.TravMath.fmt(stam) + " needed.");
    return;
  }
  if (!port(st, ref, w, tx, ty, tz, face, pitch, yaw)) {
    @PKG@.ArmoryTrav.addStat(st, ref, @DST@.getStamina(), stam);
    LAST_WHY = "teleport failed - refunded";
    return;
  }
  LAST.put(j.u, Long.valueOf(now));
  STEPS = STEPS + 1L;
  if (tgt != null) {
    ARMED.put(j.u, Long.valueOf(now + Math.round(@PKG@.ArmoryCfg.SS_WINDOW * 1000.0)));
    TARGETED = TARGETED + 1L;
  } else {
    ARMED.remove(j.u);
    STRAIGHT = STRAIGHT + 1L;
  }
  LAST_WHY = (tgt != null ? "behind the target " : "straight ") + @PKG@.TravMath.fmt(mv) + " blocks";
  @PKG@.ArmoryTrav.particle(FX, sx, sy, sz, st);
  @PKG@.ArmoryTrav.sound(SND, sx, sy, sz, st);
  @PKG@.ArmoryTrav.sound(SND, tx, ty, tz, st);
}""")
# the marker's SPAWN (ArmoryTrav.added, code 11000): the marker goes at once, the step runs on the world thread (the aim = the launch
# direction - the caster's look, as the blink reads it)
M(shd, r"""
public static void marker(@REF@ mk, @LPC@ pc, int c, @ST@ st, @CB@ buf) {
  try { buf.removeEntity(mk, @REMR@.REMOVE); } catch (Throwable t0) { }
  java.util.UUID u = pc.getCreatorUuid();
  @WLD@ w = @PKG@.ArmoryTrav.worldOf(st);
  if (u == null || w == null) return;
  MARKS = MARKS + 1L;
  if (!@PKG@.ArmoryCfg.SS_ON) { LAST_WHY = "Shadow Step off"; return; }
  double[] d = @PKG@.ArmoryTrav.unit(@PKG@.ArmorySpawn.launchVelocity(pc.getSimplePhysicsProvider()));
  if (d == null) d = @PKG@.ArmoryTrav.look(buf, u);
  if (d == null) { LAST_WHY = "no aim"; return; }
  w.execute(new @PKG@.KunaiJob(3, u, st, d, 0, 0.0, 0.0));
}""")
# a signature (Ability1-3) chain running on the attacker: its hit has the vanilla backstab from behind of its own
M(shd, r"""
public static boolean sigHit(@CAC@ acc, @REF@ a) {
  java.util.function.Function f = SIG;
  if (f != null) {
    try { return Boolean.TRUE.equals(f.apply(a)); } catch (Throwable t0) { return false; }
  }
  try {
    Object im = acc.getComponent(a, @IMOD@.get().getInteractionManagerComponent());
    if (!(im instanceof @IMGR@)) return false;
    java.util.Map m = (java.util.Map) ((@IMGR@) im).getChains();
    if (m == null) return false;
    java.util.Iterator it = m.values().iterator();
    while (it.hasNext()) {
      Object c = it.next();
      if (!(c instanceof @ICHN@)) continue;
      @ITYP@ ty = ((@ICHN@) c).getType();
      if (ty == @ITYP@.Ability1 || ty == @ITYP@.Ability2 || ty == @ITYP@.Ability3) return true;
    }
  } catch (Throwable t) { warn("sig", "the signature check failed (" + t + ") - counted as a normal hit"); }
  return false;
}""")
# fix round (critic): a MELEE dagger hit = a Physical-family damage cause (the vanilla dagger hits are "Physical"; Slashing / Bludgeoning
# inherit it) dealt from within dagger reach (ArmoryDefs.SS_MELEE, read from the vanilla dagger selectors + 1, + half the target's width;
# height: within the target's height + that reach). A kunai / arrow (plain EntitySource, Physical) from farther, a spell, fire or poison: no
M(shd, r"""
public static boolean physical(@DCS@ c) {
  @DCS@ x = c;
  for (int i = 0; i < 6 && x != null; i++) {
    String id = x.getId();
    if ("Physical".equals(id)) return true;
    String inh = x.getInherits();
    if (inh == null || inh.length() == 0) return false;
    Object n = null;
    try { n = @DCS@.getAssetMap().getAsset(inh); } catch (Throwable t) { n = null; }
    x = n instanceof @DCS@ ? (@DCS@) n : null;
  }
  return false;
}""")
M(shd, r"""
public static boolean melee(@CAC@ acc, @REF@ a, @REF@ target) {
  @VEC@ ap = @PKG@.ArmoryTrav.posOf(acc, a);
  @VEC@ tp = @PKG@.ArmoryTrav.posOf(acc, target);
  if (ap == null || tp == null) return false;
  double lim = @PKG@.ArmoryDefs.SS_MELEE + @PKG@.Kunai.thick(acc, target) * 0.5;
  double dx = ap.x - tp.x;
  double dz = ap.z - tp.z;
  return dx * dx + dz * dz <= lim * lim && Math.abs(ap.y - tp.y) <= height(acc, target) + @PKG@.ArmoryDefs.SS_MELEE;
}""")
# THE BACKSTAB (ArmoryTuneSys, the Filter group, before armour): a player's MELEE dagger hit inside the window -> once
M(shd, r"""
public static void filter(@CB@ buf, @REF@ target, @DMG@ d) {
  try {
    if (ARMED.isEmpty() || d == null || target == null || d.isCancelled() || !@PKG@.ArmoryCfg.SS_ON) return;
    Object src = d.getSource();
    if (!(src instanceof @DENT@) || src instanceof @DPRJ@) return;
    if (@PKG@.ArmoryTrav.MINE.containsKey(d)) return;
    @REF@ a = ((@DENT@) src).getRef();
    if (a == null || a.equals(target)) return;
    @PR@ ap = @PKG@.Kunai.prOf(buf, a);
    if (ap == null) return;
    java.util.UUID u = ap.getUuid();
    Object o = ARMED.get(u);
    if (!(o instanceof Long)) return;
    if (System.currentTimeMillis() > ((Long) o).longValue()) { ARMED.remove(u); return; }
    if (d.getAmount() <= 0.0f) return;          // the 0-damage guard shove
    String item = @PKG@.Leap.hand(buf, a, u);
    if (!dagger(item)) return;
    if (!physical(d.getCause()) || !melee(buf, a, target)) return;          // fix round: a kunai / arrow / spell hit keeps the window
    ARMED.remove(u);
    boolean already = false;          // a signature hit from behind already carries the vanilla damage backstab (its daggers that have one)
    if (sigHit(buf, a) && !@PKG@.ArmoryDefs.sigPlain(item)) {
      @VEC@ tp = @PKG@.ArmoryTrav.posOf(buf, target);
      @VEC@ ap2 = @PKG@.ArmoryTrav.posOf(buf, a);
      if (tp != null && ap2 != null) already = @PKG@.TravMath.behind(tp.x, tp.z, (double) bodyYaw(buf, target), ap2.x, ap2.z, @PKG@.ArmoryDefs.SS_BACK_DEG);
    }
    double f = @PKG@.TravMath.backstab(already, @PKG@.ArmoryDefs.SS_BX, @PKG@.ArmoryCfg.SS_BONUS);
    d.setAmount((float) ((double) d.getAmount() * f));
    BACKSTABS = BACKSTABS + 1L;
    LAST_WHY = "backstab x" + @PKG@.TravMath.fmt(f);
  } catch (Throwable t) { warn("filter:" + t.getClass().getName(), "the Shadow Step backstab failed (" + t + ") - that hit was left alone"); }
}""")
'''
before('''M(kjob, r"""
public void run() {''', SS_JAVA)
rep('''    if (this.kind == 1) @PKG@.Kunai.teleport(this);
    else @PKG@.Kunai.recall(this);''', '''    if (this.kind == 1) @PKG@.Kunai.teleport(this);
    else if (this.kind == 3) @PKG@.Shadow.step(this);          // 0.1.8: the dagger Shadow Step
    else @PKG@.Kunai.recall(this);''')
rep('''  if (c >= 9000 && c < 10000) { @PKG@.Kunai.recallMarker(ref, pc, c, st, buf); return; }     // 0.1.6: the kunai return''',
    '''  if (c >= 9000 && c < 10000) { @PKG@.Kunai.recallMarker(ref, pc, c, st, buf); return; }     // 0.1.6: the kunai return
  if (c == @PKG@.ArmoryDefs.SS_CODE) { @PKG@.Shadow.marker(ref, pc, c, st, buf); return; }     // 0.1.8: the dagger Shadow Step''')
rep('''    if (chunk != null) @PKG@.Stun.filter(buf, chunk.getReferenceTo(idx), (@DMG@) ev);          // 0.1.7: the boss stunlock breakout''',
    '''    if (chunk != null) @PKG@.Stun.filter(buf, chunk.getReferenceTo(idx), (@DMG@) ev);          // 0.1.7: the boss stunlock breakout
    if (chunk != null) @PKG@.Shadow.filter(buf, chunk.getReferenceTo(idx), (@DMG@) ev);        // 0.1.8: the Shadow Step backstab''')

# ================================================================================================ the plugin: bridge key, setup / shutdown, the start line
rep('''               "armory:grapple", "armory:leap", "armory:book", "armory:kunai", "armory:stun"]''',
    '''               "armory:grapple", "armory:leap", "armory:book", "armory:kunai", "armory:stun", "armory:shadow"]''')
after('''  b.put("armory:stun", @PKG@.ArmoryCfg.STUN_TEXT);          // 0.1.7
''', '''  b.put("armory:shadow", @PKG@.ArmoryCfg.SHADOW_TEXT);          // 0.1.8
''')
rep('''  @PKG@.Stun.BY.clear();          // 0.1.7
''', '''  @PKG@.Stun.BY.clear();          // 0.1.7
  @PKG@.Shadow.LAST.clear();          // 0.1.8
  @PKG@.Shadow.ARMED.clear();
''', count=2)
after('''  @PKG@.ArmoryLog.info("@VERSION@ monk weapons (bo staffs, hand wraps, gauntlets; right click = block): " + @PKG@.ArmoryCfg.STUN_TEXT);
''', '''  @PKG@.ArmoryLog.info("@VERSION@ " + @PKG@.ArmoryCfg.SHADOW_TEXT);
''')
rep('''                 "Monk bo staffs, hand wraps and gauntlets (one-target combos; bosses break out of a stunlock); right click = block. "''',
    '''                 "Monk bo staffs, hand wraps and gauntlets (one-target combos; bosses break out of a stunlock); right click = block. "
                 "Daggers: hold + release = Shadow Step (vanish, appear behind the enemy you aim at, backstab). "''')

# ================================================================================================ jar check + build lines
rep('''    _sitems = sorted(n for n in _names if n.startswith("Server/Item/Items/Weapon/Staff/"))''', '''    assert sorted(n for n in _names if n in set(SS_FILES)) == SS_FILES, "0.1.8: the %d Shadow Step files" % len(SS_FILES)
    assert [n for n in _names if os.path.basename(n).startswith("Weapon_Daggers_")] == [P_POUNCE % SS_POUNCE], \\
        "0.1.8 overrides exactly one vanilla dagger file (the Pounce) and no dagger item"
    _sitems = sorted(n for n in _names if n.startswith("Server/Item/Items/Weapon/Staff/"))''')
after('''          len(ALL_GUARDED), GEAR_PARTNER))''', '''
print("0.1.8 Shadow Step: %d files (the %s override, %s, marker %s, the shadow %s), %d rows + the cooldown table (%d entries) + %d read-only rows, "
      "backstab x%s, hold %s s; no partner (SkyyGear's speed chains reach the override)" % (
          len(SS_FILES), SS_POUNCE, ID_SS_LAUNCH, SS_MARK, PS_SHADOW, len(CFG_SS), len(SS_METALS_DEF),
          len([f for f in FIXED if f[0].startswith("fixed.shadow")]), num(SS_BX), num(SS_KEY_S)))''')

assert s.count("registerSystem(") == SYS0, "0.1.8 registers no new system (ArmoryTuneSys + ArmoryTravSys carry the Shadow Step)"
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))


# ================================================================================================ the harness: 0.1.7's checks (+ the set changes) + P12 / R12
traw = open(TSRC, encoding="utf8", newline="").read()
TNL = CR + LF if (CR + LF) in traw else LF
ts = traw.replace(CR + LF, LF)


def hrep(old, new, count=1):
    global ts
    n = ts.count(old)
    assert n == count, "harness anchor count %d (want %d): %s" % (n, count, old[:140])
    ts = ts.replace(old, new)


hrep('"""SkyyArmory 0.1.7 - test harness. GENERATED by tools/armory_0_1_7_patch.py from test_skyyarmory_0.1.6.py - edit the patch, never this file.',
     '''"""SkyyArmory 0.1.8 - test harness. GENERATED by tools/armory_0_1_8_patch.py from test_skyyarmory_0.1.7.py - edit the patch, never this file.
Every 0.1.7 check below still runs, patched only where 0.1.8 changed the set on purpose: the 5 Shadow Step files (the vanilla Pounce override,
the launch step, the marker, the shadow spawner + system) are checked in P12 + R12 (the older checks see the 0.1.7 set); + the Shadow class,
+ 10 rows, a cooldown table and 3 read-only rows in the counts; R11e's 0.1.6 -> 0.1.7 compare is history (R12f compares 0.1.7 -> 0.1.8).
NEW P12 (Python) + R12 (JVM, after R11) EXECUTE every 0.1.8 path:
  P12  the override = the vanilla Pounce (read from Assets.zip) except its "0.4" step; the launch step; the marker = the blink marker shape;
       every vanilla dagger reaches it; the shadow spawner is finite, dark, see-through (< 50 % opacity), gone within about 1.3 s;
  R12a the 5 files decode through the engine codecs into the real stores; RootInteraction.build() of the vanilla dagger root with our override
       loaded compiles the hold to our launch step (0 missing interactions);
  R12b TravMath on a fake grid: the aim angle, the arrival spot (behind / nearest free back-half spot / beside / none, the same height / 1 up /
       1 down, never through a wall), the vanilla backstab rule = the engine's own maths (TrigMathUtil.atan2, MathUtil.wrapAngle / compareAngle),
       PhysicsMath's heading rule, the backstab factor;
  R12c THE STEP (the marker's SPAWN -> KunaiJob 3 -> Shadow.step on the map-backed world): the target nearest your aim within range / cone /
       line of sight, behind it facing its back (the Teleport's body + head rotation point at its back), the cost (4 Stamina, the cap), the
       cooldown by metal, no target = straight 18 (walls 0.3 short, the void ALLOWED), refusals free (no room, a wall in your face, a locked
       arena, the class lock, too little Stamina, off), protected mobs / party / PvP-off players never targeted, the shadow particle;
       FIX ROUND: the engine attitude (real WorldSupport components): hostile beats neutral, friendly never, the override toward you, the
       neutral row; the cone is its FULL width (30 = 15 degrees off your aim);
  R12d THE BACKSTAB on REAL Damage objects through ArmoryTuneSys: x1.5 x 1.1 once within the window, a signature hit from behind x1.1 only,
       projectiles / other weapons / the guard shove / expired windows left alone; FIX ROUND: on the REAL vanilla damage causes (Physical,
       Slashing -> Physical, Projectile, Fire -> Elemental) only a Physical-family hit within dagger reach spends it;
  R12e the rows (10 + the cooldown table + 3 read-only), the loader clamps, armory:shadow, the default file;
  R12f vs the 0.1.7 jar: the new files = exactly the 5 Shadow Step files + Shadow.class, every other non-class file byte-identical.

0.1.7 harness: SkyyArmory 0.1.7 - test harness. GENERATED by tools/armory_0_1_7_patch.py from test_skyyarmory_0.1.6.py - edit the patch, never this file.''')
hrep('VERSION = "0.1.7"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.7 SkyyArmory"',
     'VERSION = "0.1.8"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.8 SkyyArmory"')
hrep('os.path.join(SCRATCH_ROOT, "armory017", "harness")', 'os.path.join(SCRATCH_ROOT, "armory018", "harness")')
hrep('raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.7.py', 'raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.8.py')
hrep('Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.7"))', 'Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.8"))')
hrep('"[SkyyArmory] 0.1.7 ready" in m_', '"[SkyyArmory] 0.1.8 ready" in m_')
hrep('"0.1.7 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_', '"0.1.8 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_')
hrep('"0.1.7 crossbow grapple: grapple on" in m_', '"0.1.8 crossbow grapple: grapple on" in m_')
hrep('"51 of 51 items, 338 of 338 interactions, 62 of 62 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.7 SkyyArmory" in str(r[1])',
     '"51 of 51 items, 340 of 340 interactions, 63 of 63 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.8 SkyyArmory" in str(r[1])')
# P0: the Shadow Step files are checked in P12 / R12; the older checks see the 0.1.7 set
hrep('''        _d17["PlayerAnimationsId"] = {"SkyyArmory_Staff": "Staff", "SkyyArmory_Spellbook": "Spellbook", "SkyyArmory_Wand": "Wand"}.get(_d17.get("PlayerAnimationsId"), _d17.get("PlayerAnimationsId"))
''', '''        _d17["PlayerAnimationsId"] = {"SkyyArmory_Staff": "Staff", "SkyyArmory_Spellbook": "Spellbook", "SkyyArmory_Wand": "Wand"}.get(_d17.get("PlayerAnimationsId"), _d17.get("PlayerAnimationsId"))
# 0.1.8: the Shadow Step files are checked in P12 / R12; the older checks below see the 0.1.7 set
SS_POUNCE, SS_LAUNCH, SS_MARK, SS_FX = "Weapon_Daggers_Primary_Pounce", "SkyyArmory_Shadow_Step_Launch", "SkyyArmory_Shadow_Step", "SkyyArmory_Shadow_Fade"
L18_INTS = dict((k_, J_INTS.pop(k_)) for k_ in (SS_POUNCE, SS_LAUNCH))
L18_PRJ = {SS_MARK: J_PRJ.pop(SS_MARK)}
L18_PSYS = {SS_FX: J_PSYS.pop(SS_FX)}
L18_PSP = {SS_FX: J_PSP.pop(SS_FX)}
_l18p = set(list(L18_INTS.values()) + list(L18_PRJ.values()) + list(L18_PSYS.values()) + list(L18_PSP.values()))
L18_J = dict((p_, J.pop(p_)) for p_ in list(J) if p_ in _l18p)
''')
hrep('''    check(len(names) == 45, "A: 45 classes (38 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap + 0.1.6's 6 book / kunai + 0.1.7's 2 stunlock classes + 7 kit)")''',
     '''    check(len(names) == 46, "A: 46 classes (39 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap + 0.1.6's 6 book / kunai + 0.1.7's 2 stunlock + 0.1.8's Shadow + 7 kit)")''')
# ---- K: + 0.1.8's 10 Shadow Step rows (after the stunlock rows), its cooldown table (after the 0.1.6 tables), 3 read-only rows
hrep('''    NEW_ROWS += ["part.stun", "stun.perPlayer", "stun.maxPlayers", "stun.gap", "stun.window", "stun.bossWords"]      # 0.1.7
    TAB16 = ["book.radius", "book.targets", "lev.height", "lev.hover", "lev.drift", "lev.mana", "lev.stamina", "kunai.range", "kunai.cooldown",
             "kunai.stamina", "kunai.mana", "ret.window", "ret.radius"]      # 0.1.6 per-metal tables''',
     '''    NEW_ROWS += ["part.stun", "stun.perPlayer", "stun.maxPlayers", "stun.gap", "stun.window", "stun.bossWords"]      # 0.1.7
    NEW_ROWS += ["dagger.shadowStep." + k_ for k_ in ("enabled", "targetRange", "targetCone", "behind", "noTargetDistance", "backstabWindow",
                                                      "backstabBonus", "staminaCost", "players", "neutral")]      # 0.1.8
    TAB16 = ["book.radius", "book.targets", "lev.height", "lev.hover", "lev.drift", "lev.mana", "lev.stamina", "kunai.range", "kunai.cooldown",
             "kunai.stamina", "kunai.mana", "ret.window", "ret.radius", "dagger.shadowStep.cooldown"]      # 0.1.6 per-metal tables + 0.1.8's''')
hrep('''    check(keys[:10] == want_rows and keys[10:10 + NN] == NEW_ROWS and keys[10 + NN:10 + NN + 13] == TAB16
          and all(k.startswith("fixed.") or k in ("staff.stamina", "hop.mode", "grapple.flight", "grapple.rightClick") for k in keys[10 + NN + 13:])
          and len(keys) == 10 + NN + 13 + 8 + 8 + 5 + 2 + 2 + 17 + 20,''',
     '''    check(keys[:10] == want_rows and keys[10:10 + NN] == NEW_ROWS and keys[10 + NN:10 + NN + 14] == TAB16
          and all(k.startswith("fixed.") or k in ("staff.stamina", "hop.mode", "grapple.flight", "grapple.rightClick") for k in keys[10 + NN + 14:])
          and len(keys) == 10 + NN + 14 + 8 + 8 + 5 + 2 + 2 + 17 + 20 + 3,''')
hrep('''          and all(flags[k] == "ro" for k in keys[10 + NN + 13:]) and all(types[k] == "table" for k in TAB16)''',
     '''          and all(flags[k] == "ro" for k in keys[10 + NN + 14:]) and all(types[k] == "table" for k in TAB16)''')
# ---- R11e: the 0.1.6 -> 0.1.7 compare is history (R12f compares 0.1.7 -> 0.1.8)
hrep('''    OLD16 = os.path.join(HERE, "SkyyArmory-0.1.6.jar")
    if not os.path.isfile(OLD16):
        print("R11e. NOTE no SkyyArmory-0.1.6.jar here - the old-vs-new file compare is skipped")''',
     '''    OLD16 = None          # 0.1.8: the 0.1.6 -> 0.1.7 compare is history - R12f compares 0.1.7 -> 0.1.8
    if OLD16 is None:
        print("R11e. NOTE (0.1.8) the 0.1.6 -> 0.1.7 file compare is history - R12f compares 0.1.7 -> 0.1.8")''')

# ---- L: the 0.1.8 Shadow Step files decode + load from our pack before the pack check counts them (R12a)
L18_LOAD = r"""    # ---- 0.1.8 (R12a): the Shadow Step files through the engine codecs (no unknown key, no failed validation) into the real stores
    bad18 = []
    for c_, tab_, kind_ in ((PSPc, L18_PSP, "spawner"), (PSYc, L18_PSYS, "particle system"), (PRJc, L18_PRJ, "projectile"), (INTc, L18_INTS, "interaction")):
        objs_, eis_ = [], []
        for k_ in sorted(tab_):
            o_, w_, ei_ = dec17(c_, k_, JZ.read(tab_[k_]).decode("utf-8"))
            if o_ is None or w_:
                bad18.append("%s %s: %s" % (kind_, k_, w_))
                continue
            DEC[(kind_, k_)] = o_
            objs_.append(o_)
            eis_.append(ei_)
        load(c_, objs_, PACK)
        for ei_ in eis_:
            try:
                ei_.getData().loadContainedAssets(False)
            except Exception as e_:
                bad18.append("%s contained assets: %s" % (kind_, str(e_)[:160]))
        for k_ in sorted(tab_):
            if c_.getAssetMap().getAsset(k_) is None or str(c_.getAssetMap().getAssetPack(k_)) != PACK:
                bad18.append("%s %s is not in the store from our pack" % (kind_, k_))
    check(not bad18 and len(L18_INTS) == 2 and len(L18_PRJ) == 1 and len(L18_PSYS) == 1 and len(L18_PSP) == 1,
          "L (0.1.8 / R12a): the Pounce override + the launch step, the marker, the shadow spawner + system decode through the engine codecs (no "
          "unknown key, no failed validation) and sit in the real stores from our pack: %s" % bad18[:4])
"""
hrep('''    check(not dbad17, "R11a: every Monk weapon decodes as a weapon with MaxStack 1: %s" % dbad17)
''', '''    check(not dbad17, "R11a: every Monk weapon decodes as a weapon with MaxStack 1: %s" % dbad17)
''' + L18_LOAD)

# ---- P12 (Python, before the JVM part): every 0.1.8 file checked on its own (independent of the build's numbers)
P12 = r'''
# ============================================================================================================ P12. 0.1.8 the dagger Shadow Step (pure files)
SSJ = dict((k_, L18_J[p_]) for k_, p_ in L18_INTS.items())
SSM = L18_J[L18_PRJ[SS_MARK]]
SSP = L18_J[L18_PSP[SS_FX]]
SSY = L18_J[L18_PSYS[SS_FX]]
VPO = aj("int", SS_POUNCE)
check(L18_INTS[SS_POUNCE] == AIDX["int"][SS_POUNCE] and dict((k, v) for k, v in SSJ[SS_POUNCE].items() if k != "Next") == dict((k, v) for k, v in VPO.items() if k != "Next")
      and SSJ[SS_POUNCE]["Next"] == {"0": VPO["Next"]["0"], "0.4": SS_LAUNCH} and VPO["Next"]["0"] == "Weapon_Daggers_Primary_Chain",
      "P12: the ONE vanilla override = Weapon_Daggers_Primary_Pounce at its vanilla path, every field the vanilla one (the charging pose + particles, "
      "0.5 move speed, no endless hold, release before 0.4 s = the vanilla tap chain) except its 0.4 s step -> %s" % SS_LAUNCH)
check(SSJ[SS_LAUNCH] == {"Type": "LaunchProjectile", "RunTime": 0.25, "Effects": {"ItemAnimationId": "DashForward"}, "ProjectileId": SS_MARK}
      and "DashForward" in aj("anim", "Daggers")["Animations"] and L18_INTS[SS_LAUNCH].startswith("Server/Item/Interactions/Weapons/Daggers/SkyyArmory/"),
      "P12: the 0.4 s step only launches the invisible marker (the vanilla DashForward pose) - no Stamina, no force, no damage in the chain")
check(SSM == JPRJ[BLINK["Iron"]] and SSM["Damage"] == 0 and SSM["Gravity"] == 0 and SSM["Appearance"] == "SkyyArmory_Marker" and SSM["DeathEffectsOnHit"] is False,
      "P12: the marker = the staff blink marker shape (no damage, no gravity, the invisible marker model, no hit / death effects)")
_vtpl = aj("item", "Template_Weapon_Daggers")
_vdp = aj("int", "Weapon_Daggers_Primary")
_vsc = aj("int", "Weapon_Daggers_Primary_Pounce_StaminaCondition")
ss_reach = sorted(i for i in AIDX["item"] if i.startswith("Weapon_Daggers_") and aresolve("item", i)["Interactions"]["Primary"] == "Root_Weapon_Daggers_Primary"
                  and not set(aj("item", i).get("InteractionVars") or {}) & {"Pounce", "Pounce_StaminaCondition"})
check(_vtpl["Interactions"]["Primary"] == "Root_Weapon_Daggers_Primary" and aj("root", "Root_Weapon_Daggers_Primary")["Interactions"] == ["Weapon_Daggers_Primary"]
      and _vdp["Next"]["0.2"]["DefaultValue"] == {"Interactions": ["Weapon_Daggers_Primary_Pounce_StaminaCondition"]}
      and _vsc["Next"]["Next"]["DefaultValue"] == {"Interactions": [SS_POUNCE]} and _vsc["Costs"] == {"Stamina": 0.1}
      and len(ss_reach) == len([i for i in AIDX["item"] if i.startswith("Weapon_Daggers_")]) >= 16,
      "P12 (Assets.zip): every vanilla dagger (%d) reaches the override: the template's primary root -> Weapon_Daggers_Primary 0.2 s -> the vanilla "
      "StaminaCondition (Stamina > 0, regen pause) -> Var Pounce -> Weapon_Daggers_Primary_Pounce; no dagger names its own Pounce" % len(ss_reach))
_ssop = []
for _k in ("0", "50", "100"):
    _ssop.append(SSP["Particle"]["Animation"][_k].get("Opacity", 0))
_ssop.append(SSP["Particle"]["InitialAnimationFrame"]["Opacity"])
_rgb = SSP["Particle"]["InitialAnimationFrame"]["Color"]
_lum = (0.2126 * int(_rgb[1:3], 16) + 0.7152 * int(_rgb[3:5], 16) + 0.0722 * int(_rgb[5:7], 16)) / 255.0
check(SSY == {"LifeSpan": 0.3, "Spawners": [{"SpawnerId": SS_FX, "PositionOffset": {"X": 0, "Y": 0.9, "Z": 0}}]} and max(_ssop) < 0.5 and _ssop[2] == 0
      and _lum < 0.15 and SSP["TotalParticles"]["Max"] <= 40 and SSP["ParticleLifeSpan"]["Max"] <= 1.0 and "Attractors" not in SSP
      and ("Common/" + SSP["Particle"]["Texture"]) in AZS and SSP["EmitOffset"]["Y"]["Max"] < 1.0 and SSP["Shape"] == "Cube"
      and not ahas("psys", SS_FX) and not ahas("pspawn", SS_FX),
      "P12 (Skyy: 'see-through, not distracting'): the shadow = a %d-particle, body-sized (0.44 x 1.7) dark (%s) smoke burst, at most %s opaque, "
      "fading to 0, every particle gone by %s s after a 0.3 s emit; no vanilla id" % (SSP["TotalParticles"]["Max"], _rgb, max(_ssop), SSP["ParticleLifeSpan"]["Max"]))
print("P12. 0.1.8 Shadow Step: the Pounce override (0.4 s step only), the launch, the marker, %d daggers reach it, the shadow (opacity <= %s)" % (len(ss_reach), max(_ssop)))
'''
hrep('''PY_OKS, PY_FAILS = OKS[0], len(FAILS)
print("PYTHON PART: %d ok, %d FAIL" % (PY_OKS, PY_FAILS))''', P12 + '''PY_OKS, PY_FAILS = OKS[0], len(FAILS)
print("PYTHON PART: %d ok, %d FAIL" % (PY_OKS, PY_FAILS))''')

R12 = r'''    # ============================================================================ R12. 0.1.8 THE DAGGER SHADOW STEP - every new path EXECUTED
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    SH = JClass(PKG + "Shadow")
    KJ = JClass(PKG + "KunaiJob")
    LP.HAND = HashMap()          # the Leap / Shadow hand seam (R11 left it off)
    AT.NEAR = NearR()            # the sphere query seam with its radius (R10's; R11 left it off)
    ADf = JClass(PKG + "ArmoryDefs")
    PHMc = JClass("com.hypixel.hytale.server.core.modules.physics.util.PhysicsMath")
    TMU = JClass("com.hypixel.hytale.math.util.TrigMathUtil")
    MU = JClass("com.hypixel.hytale.math.util.MathUtil")
    XFMc = JClass("com.hypixel.hytale.math.vector.Transform")
    PI_ = math.pi
    # --- R12a. the engine compile: the vanilla dagger chain with our override loaded (0 missing interactions) + our override compiled alone
    need18 = set()

    def clo18(x):
        if isinstance(x, str):
            if x in INTS_ALL and x not in need18 and x not in (SS_POUNCE, SS_LAUNCH) and INTc.getAssetMap().getAsset(x) is None:
                need18.add(x)
                clo18(INTS_ALL[x])
        elif isinstance(x, list):
            for e_ in x:
                clo18(e_)
        elif isinstance(x, dict):
            for k_, v_ in x.items():
                if k_ not in ("Type", "$Comment"):
                    clo18(v_)
    clo18(aj("root", "Root_Weapon_Daggers_Primary"))
    clo18(L18_J[L18_INTS[SS_POUNCE]])
    pend18, got18, vb18 = sorted(need18), {}, []
    for _round in range(12):
        nxt_, now_ = [], []
        for i_ in pend18:
            d_ = INTS_ALL[i_]
            if d_.get("Parent") and d_["Parent"] in need18 and d_["Parent"] not in got18:
                nxt_.append(i_)
                continue
            o_, w_, ei_ = dec17(INTc, i_, json.dumps(d_))
            if o_ is None:
                vb18.append((i_, w_))
                continue
            got18[i_] = (o_, ei_)
            now_.append(i_)
        load(INTc, [got18[i_][0] for i_ in now_], "Hytale:Hytale")
        for i_ in now_:
            try:
                got18[i_][1].getData().loadContainedAssets(False)
            except Exception as e_:
                vb18.append((i_, "contained: " + str(e_)[:120]))
        pend18 = nxt_
        if not pend18:
            break
    if ROOTc.getAssetMap().getAsset("Root_Weapon_Daggers_Primary") is None:
        o_, w_ = dec(ROOTc, "Root_Weapon_Daggers_Primary", json.dumps(aj("root", "Root_Weapon_Daggers_Primary")))
        load(ROOTc, [o_], "Hytale:Hytale")
    o_, w_ = dec(ROOTc, "SkyyArmoryTest_ShadowRoot", json.dumps({"Interactions": [SS_POUNCE]}))
    load(ROOTc, [o_], "Test:Pack")
    n_m0 = len([m_ for lv_, m_ in records() if "Missing interaction" in m_])
    res_d = compile_root("Root_Weapon_Daggers_Primary")
    res_s = compile_root("SkyyArmoryTest_ShadowRoot")
    n_m1 = len([m_ for lv_, m_ in records() if "Missing interaction" in m_])
    ops_s = [(c_, i_) for c_, i_ in res_s["ops"] if i_ is not None]
    path18 = ["Weapon_Daggers_Primary", "Weapon_Daggers_Primary_Chain", "Weapon_Daggers_Primary_Pounce_StaminaCondition", SS_POUNCE, SS_LAUNCH]
    vb18x = [(i_, w_) for i_, w_ in vb18 if not i_.endswith("_Damage")]          # the tap hits' damage leaves are not on the hold path
    if len(vb18x) < len(vb18):
        print("R12a. NOTE %d tap damage leaves did not decode alone in the bare JVM (not on the hold path): %s" % (len(vb18) - len(vb18x), [i_ for i_, w_ in vb18][:4]))
    check(not vb18x and all(INTc.getAssetMap().getAsset(i_) is not None for i_ in path18) and not res_d["bad"] and not res_s["bad"] and n_m1 == n_m0 and str(INTc.getAssetMap().getAssetPack(SS_POUNCE)) == PACK
          and ("ChargingInteraction", SS_POUNCE) in ops_s and ("LaunchProjectileInteraction", SS_LAUNCH) in ops_s
          and not [c_ for c_, i_ in ops_s if c_ in ("ApplyForceInteraction", "ChangeStatInteraction")],
          "R12a (engine compile): RootInteraction.build() of the vanilla dagger root (its %d vanilla interactions loaded, our override from our pack) and "
          "of our override alone - 0 missing interactions, no placeholder; the override compiles to Charging -> [the vanilla tap chain | %s "
          "(LaunchProjectile)], no ApplyForce (the leap) and no ChangeStat (Stamina) left: %s %s %s" % (len(got18), SS_LAUNCH, vb18x[:2], res_s["bad"][:2], ops_s[:8]))
    print("R12a. Shadow Step files decoded + loaded from our pack; the vanilla dagger root + the override compiled (%d / %d operations)" % (
        len(res_d["ops"]), len(res_s["ops"])))

    # --- R12b. TravMath (pure) + the engine's own angle maths
    od_ = [round(float(TM.offDeg(*a_)), 4) for a_ in ((1, 0, 0, 1, 0, 0), (1, 0, 0, 0, 0, 1), (1, 0, 0, 1, 0, 1), (1, 0, 0, -1, 0, 0), (0, 0, 0, 1, 0, 0))]
    hd_ = [(y_, float(PHMc.headingFromDirection(-math.sin(y_), -math.cos(y_)))) for y_ in (-3.0, -1.5, -0.4, 0.0, 0.7, 2.0, 3.0)]
    r3t = R3(0.0, 1.25, 0.0)
    check(od_ == [0.0, 90.0, 45.0, 180.0, 180.0] and all(abs(a_ - b_) < 0.01 for a_, b_ in hd_) and abs(float(r3t.yaw()) - 1.25) < 1e-6 and float(r3t.pitch()) == 0.0,
          "R12b: the aim angle (0 / 90 / 45 / 180, no direction = 180); PhysicsMath.headingFromDirection(-sin y, -cos y) = y (forward = (-sin, -cos), so "
          "a body's back = (+sin, +cos)); Rotation3f(pitch, yaw, roll): %s %s" % (od_, [(a_, round(b_, 3)) for a_, b_ in hd_]))
    # the vanilla backstab rule (DamageEntityInteraction.attemptEntityDamage0 bytecode): hit = wrapAngle(atan2(ax - tx, az - tz) + PI - bodyYaw),
    # a backstab when |compareAngle(hit, PI)| < 80 deg - TravMath.behind must agree away from the exact edge
    mism, edge, nb = [], 0, 0
    for yd_ in range(-180, 180, 23):
        ty_ = math.radians(yd_)
        for ad_ in range(0, 360, 5):
            ax_, az_ = 8.5 + 2.0 * math.sin(math.radians(ad_)), 0.5 + 2.0 * math.cos(math.radians(ad_))
            hit_ = float(MU.wrapAngle(JFloat(float(TMU.atan2(ax_ - 8.5, az_ - 0.5)) + PI_ - ty_)))
            eng_ = abs(float(MU.compareAngle(hit_, PI_))) < math.radians(80.0)
            ours_ = bool(TM.behind(8.5, 0.5, ty_, ax_, az_, 80.0))
            off_ = math.degrees(abs(math.atan2(math.sin(math.radians(ad_) - ty_), math.cos(math.radians(ad_) - ty_))))
            if abs(off_ - 80.0) < 1.5:
                edge += 1
                continue
            nb += 1 if eng_ else 0
            if eng_ != ours_:
                mism.append((yd_, ad_, eng_, ours_))
    check(not mism and nb > 100 and not bool(TM.behind(8.5, 0.5, 0.0, 8.5, 0.5, 80.0)) and not bool(TM.behind(8.5, 0.5, float("nan"), 9.0, 0.5, 80.0)),
          "R12b: TravMath.behind = the engine's own backstab maths (real TrigMathUtil.atan2 / MathUtil.wrapAngle / compareAngle) on %d target yaws x 72 "
          "attacker spots (%d backstabs; %d within 1.5 deg of the 80 deg edge skipped); same spot / no yaw = no: %s" % (16, nb, edge, mism[:3]))
    check([round(float(TM.backstab(*a_)), 4) for a_ in ((False, 1.5, 0.1), (True, 1.5, 0.1), (False, 1.5, 0.0), (False, 0.5, 0.1), (False, 1.5, -1.0))]
          == [1.65, 1.1, 1.5, 1.1, 1.5], "R12b: the guaranteed backstab = x1.5 x 1.1 (Skyy's +10 %); already a vanilla backstab = x1.1 only; bonus 0 = x1.5")
    # the arrival spot: a faithful Python copy of TravMath.arrive (body box, the 0.25-step clear line, the pass order) - Java must equal it

    def py_body(cells_, x, y, z):
        ys_ = sorted(set([math.floor(y + 0.05), math.floor(y + 0.95), math.floor(y + 1.75)]))
        for bx_ in range(math.floor(x - 0.299), math.floor(x + 0.299) + 1):
            for bz_ in range(math.floor(z - 0.299), math.floor(z + 0.299) + 1):
                for by_ in ys_:
                    if (bx_, by_, bz_) in cells_ or by_ == 63:
                        return False
        return True

    def py_clear(cells_, ax, ay, az, bx, by, bz):
        dx, dy, dz = bx - ax, by - ay, bz - az
        n_ = max(1, int(math.ceil(math.sqrt(dx * dx + dy * dy + dz * dz) / 0.25)))
        for k_ in range(n_ + 1):
            u_ = k_ / n_
            c_ = (math.floor(ax + dx * u_), math.floor(ay + dy * u_), math.floor(az + dz * u_))
            if c_ in cells_ or c_[1] == 63:
                return False
        return True

    def py_arrive(cells_, tx, ty, tz, yaw, r, cy):
        bx, bz = math.sin(yaw), math.cos(yaw)
        ix, iz = tx + bx * r, tz + bz * r
        angs = [0.0, 30.0, -30.0, 60.0, -60.0, 90.0, -90.0, 120.0, -120.0]
        for pss, (a0, a1) in enumerate(((0, 7), (7, 9))):
            best, out = 1e18, None
            for k_ in range(a0, a1):
                rad = math.radians(angs[k_])
                cx, cz = bx * math.cos(rad) - bz * math.sin(rad), bx * math.sin(rad) + bz * math.cos(rad)
                for h_ in (0.0, 1.0, -1.0):
                    x, y, z = tx + cx * r, ty + h_, tz + cz * r
                    if not py_body(cells_, x, y, z) or not py_clear(cells_, tx, cy, tz, x, y + 1.0, z):
                        continue
                    d2 = (x - ix) ** 2 + (y - ty) ** 2 + (z - iz) ** 2
                    if d2 < best - 1e-9:
                        best, out = d2, (x, y, z, float(pss))
            if out is not None:
                return out
        return None

    def jarrive(cells_, tx, ty, tz, yaw, r, cy):
        g_ = Grid(lambda x, y, z: 1 if ((x, y, z) in cells_ or y == 63) else 0)
        a_ = TM.arrive(g_, tx, ty, tz, yaw, r, cy)
        return None if a_ is None else tuple(round(float(v_), 6) for v_ in a_)

    def rnd(t_):
        return None if t_ is None else tuple(round(v_, 6) for v_ in t_)
    import random as _rnd
    _rnd.seed(18)
    amis, apass, anone = [], [0, 0], 0
    for n_ in range(250):
        yaw_ = _rnd.uniform(-PI_, PI_)
        r_ = _rnd.choice([1.5, 1.5, 2.0, 2.5])
        cells_ = set()
        for _c in range(_rnd.randint(0, 40)):
            cells_.add((_rnd.randint(5, 12), _rnd.randint(64, 67), _rnd.randint(-3, 4)))
        cells_.discard((8, 64, 0))
        cells_.discard((8, 65, 0))
        want_ = rnd(py_arrive(cells_, 8.5, 64.0, 0.5, yaw_, r_, 64.9))
        got_ = jarrive(cells_, 8.5, 64.0, 0.5, yaw_, r_, 64.9)
        if want_ != got_:
            amis.append((n_, want_, got_))
        if want_ is None:
            anone += 1
        else:
            apass[int(want_[3])] += 1
    open_ = jarrive(set(), 8.5, 64.0, 0.5, PI_ / 2.0, 1.5, 64.9)
    # behind blocked at foot height, free one block up (a step): the spot 1 up
    step_c = set((x_, 64, z_) for x_ in range(9, 12) for z_ in range(-3, 4))
    up_ = jarrive(step_c, 8.5, 64.0, 0.5, PI_ / 2.0, 1.5, 64.9)
    # the whole back half blocked, the sides (beside) free - a mob facing yaw 75 deg (a layout found offline that keeps your line of sight free)
    y30 = math.radians(75.0)

    def body_cells(x, y, z):
        ys_ = sorted(set([math.floor(y + 0.05), math.floor(y + 0.95), math.floor(y + 1.75)]))
        return set((bx_, by_, bz_) for bx_ in range(math.floor(x - 0.299), math.floor(x + 0.299) + 1)
                   for bz_ in range(math.floor(z - 0.299), math.floor(z + 0.299) + 1) for by_ in ys_)
    back_c, bes_c = set(), set()
    for k_, a_ in enumerate([0, 30, -30, 60, -60, 90, -90, 120, -120]):
        rad = math.radians(a_)
        cx, cz = math.sin(y30) * math.cos(rad) - math.cos(y30) * math.sin(rad), math.sin(y30) * math.sin(rad) + math.cos(y30) * math.cos(rad)
        for h_ in (0.0, 1.0, -1.0):
            bc_ = body_cells(8.5 + cx * 1.5, 64.0 + h_, 0.5 + cz * 1.5)
            if k_ < 7:
                back_c |= bc_
            elif h_ == 0.0:
                bes_c |= bc_
    side_c = set(c_ for c_ in back_c - bes_c if c_[1] >= 64) - {(8, 64, 0), (8, 65, 0)}
    bes_ = jarrive(side_c, 8.5, 64.0, 0.5, y30, 1.5, 64.9)
    shut_ = jarrive(side_c | bes_c - {(8, 64, 0), (8, 65, 0)}, 8.5, 64.0, 0.5, y30, 1.5, 64.9)
    check(not amis and apass[0] > 100 and apass[1] >= 1 and open_ == (10.0, 64.0, 0.5, 0.0) and up_ is not None and up_[1] == 65.0
          and up_[3] == 0.0 and bes_ is not None and bes_[3] == 1.0 and bes_ == rnd(py_arrive(side_c, 8.5, 64.0, 0.5, y30, 1.5, 64.9)) and shut_ is None,
          "R12b (spec 2 'Arrive'): TravMath.arrive = an independent Python copy on 250 random block layouts (%d back half / %d beside / %d none); open "
          "ground = 1.5 straight behind a mob facing -x (x 10.0); a block behind at foot height = the spot 1 up; the whole back half blocked = beside it "
          "(%s); boxed in = none: %s" % (apass[0], apass[1], anone, bes_, amis[:2]))
    print("R12b. TravMath: aim angle, heading rule, the vanilla backstab rule (engine maths), backstab factor, arrive = Python copy on 250 layouts")

    # --- R12c. THE STEP (marker SPAWN -> KunaiJob 3 -> Shadow.step), on the map-backed world
    def ss_reset(stam=10.0, hand="Weapon_Daggers_Copper", grid=None, near=()):
        SH.LAST.clear()
        SH.ARMED.clear()
        TWd.JOBS.clear()
        reset_buf()
        put(rc, TPc.getComponentType(), None)
        put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
        put(rc, HRc.getComponentType(), HRc(R3(0.1, 0.2, 0.0)))
        mc.setStatValue(STAM, JFloat(stam))
        LP.HAND.put(cu, hand)
        AT.GRID = grid if grid is not None else Grid(world_fn())
        NEARL[:] = list(near)

    def ss_run(d=(1.0, 0.0, 0.0)):
        KJ(3, cu, tst, JArray(JDouble)([float(x_) for x_ in d]), 0, 0.0, 0.0).run()
        tp_ = comp(rc, TPc.getComponentType())
        if tp_ is None:
            return None
        p_, b_, h_ = tp_.getPosition(), tp_.getRotation(), tp_.getHeadRotation()
        return (round(float(p_.x()), 3), round(float(p_.y()), 3), round(float(p_.z()), 3), round(float(b_.yaw()), 4),
                None if h_ is None else round(float(h_.pitch()), 4), None if h_ is None else round(float(h_.yaw()), 4), bool(tp_.isResetVelocity()))

    def ss_mob(i_, x, y, z, yaw, box=(0.6, 1.8, 0.6), role=None):
        r_ = mob(i_, x, y, z, box, role=role)
        put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, yaw, 0.0)))
        return r_
    m_f = ss_mob(1801, 8.5, 64.0, 0.5, PI_ / 2.0)          # 8 blocks ahead, facing you (-x)
    ss_reset(near=[m_f, rc])
    t0_ = nowms()
    s1 = ss_run()
    arm1 = SH.ARMED.get(cu)
    look1 = None
    if s1 is not None:
        dv_ = XFMc(s1[0], s1[1] + 1.6, s1[2], JFloat(s1[4]), JFloat(s1[5]), JFloat(0.0)).getDirection()
        tv_ = (8.5 - s1[0], 64.9 - (s1[1] + 1.6), 0.5 - s1[2])
        tl_ = math.sqrt(sum(v_ * v_ for v_ in tv_))
        look1 = round((float(dv_.x()) * tv_[0] + float(dv_.y()) * tv_[1] + float(dv_.z()) * tv_[2]) / tl_, 4)
    check(s1 is not None and s1[:3] == (10.0, 64.0, 0.5) and abs(s1[3] - PI_ / 2.0) < 0.01 and abs(s1[5] - PI_ / 2.0) < 0.01 and s1[4] < 0.0 and not s1[6]
          and look1 is not None and look1 > 0.999 and bool(TM.behind(8.5, 0.5, PI_ / 2.0, s1[0], s1[2], 80.0)) and sv(mc, STAM) == 6.0
          and arm1 is not None and 2900 <= int(arm1) - t0_ <= 3200 and SH.LAST.get(cu) is not None and str(SH.LAST_WHY).startswith("behind the target"),
          "R12c (Skyy: 'appear behind your enemy facing their back'): a mob 8 blocks ahead facing you -> you appear 1.5 behind it (x 10.0), the Teleport "
          "turns your body + head to its back (the engine's Transform look points at its centre: %s), the velocity kept (no fall-damage escape), 4 Stamina "
          "paid (10 -> 6), the backstab window open 3 s, the 6 s cooldown started: %s, Stamina %s, %s" % (look1, s1, sv(mc, STAM), SH.LAST_WHY))
    # the enemy nearest your AIM wins (not the nearest one); off the cone / out of range / behind a wall = no target
    m_a = ss_mob(1802, 6.5, 64.0, 2.5, PI_ / 2.0)           # 18 deg off your aim, close
    m_b = ss_mob(1803, 14.5, 64.0, 0.5, PI_ / 2.0)          # dead ahead, farther
    ss_reset(near=[m_a, m_b])
    s2 = ss_run()
    m_c = ss_mob(1804, 5.5, 64.0, 4.5, PI_ / 2.0)           # 38 deg off (> 30)
    ss_reset(near=[m_c])
    s3 = ss_run()
    m_d = ss_mob(1805, 26.5, 64.0, 0.5, PI_ / 2.0)          # 26 blocks (> 24)
    ss_reset(near=[m_d])
    s4 = ss_run()
    ss_reset(near=[m_f], grid=Grid(world_fn([lambda x, y, z: x == 5 and 64 <= y <= 66])))          # a wall between you
    s5 = ss_run()
    arm5 = SH.ARMED.get(cu)
    ACfg.SS_CONE = 80
    ss_reset(near=[m_c])
    s3b = ss_run()
    ACfg.SS_CONE = 30
    ss_reset(near=[m_a])          # fix round: 18 deg off is outside the default 30 deg cone (15 each side) ...
    s3c = ss_run()
    m_e = ss_mob(1820, 8.5, 64.0, 2.2, PI_ / 2.0)          # ... 12 deg off is inside it
    ss_reset(near=[m_e])
    s3d = ss_run()
    check(s2 is not None and s2[:3] == (16.0, 64.0, 0.5) and s3 is not None and s3[:3] == (18.5, 64.0, 0.5) and s4 is not None and s4[:3] == (18.5, 64.0, 0.5)
          and s5 is not None and s5[:3] == (4.7, 64.0, 0.5) and arm5 is None and s3b is not None and s3b[:3] == (7.0, 64.0, 4.5)
          and s3c is not None and s3c[:3] == (18.5, 64.0, 0.5) and s3d is not None and s3d[0] == 10.0 and abs(s3d[2] - 2.2) < 1e-6,
          "R12c (spec 2 'Target', 'inside a 30 deg cone' = its FULL width - fix round): the mob dead ahead at 14 wins over a closer one 18 deg off "
          "your aim (behind it: x 16); a mob 18 deg off alone (> 15) or 38 deg off or 26 blocks away (range 24) or behind a wall is no target - you "
          "step straight (18 blocks, or 0.3 short of the wall at x 5) and no backstab is armed; 12 deg off = a target; targetCone 80 (40 each side) "
          "takes the 38 deg mob: %s %s %s %s %s %s %s" % (s2, s3, s4, s5, s3b, s3c, s3d))
    # fix round (critic): WHO IS AN ENEMY = the engine attitude on REAL WorldSupport components (NPCPlugin's component type registered like
    # the plugin does; Role.createAndAttach puts one on every role NPC - bytecode-checked by the build)
    NPCP = JClass("com.hypixel.hytale.server.npc.NPCPlugin")
    WSc = JClass("com.hypixel.hytale.server.npc.role.support.WorldSupport")
    ATTc = JClass("com.hypixel.hytale.server.core.asset.type.attitude.Attitude")
    AMEc = JClass("com.hypixel.hytale.server.npc.util.AttitudeMemoryEntry")
    npl_old = NPCP.get()
    npl = npl_old if npl_old is not None else U.allocateInstance(NPCP.class_)
    jfield(NPCP, "instance").set(None, npl)
    setf(npl, NPCP, "worldSupportComponentType", reg_.registerComponent(WSc.class_, Sup(lambda: None)))

    def ss_att(i_, x, z, att, over=None):
        r_ = ss_mob(i_, x, 64.0, z, PI_ / 2.0)
        ws_ = U.allocateInstance(WSc.class_)
        setf(ws_, WSc, "defaultPlayerAttitude", att)
        if over is not None:
            mem_ = JClass("it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap")()
            mem_.put(JInt(int(over[0].getIndex())), AMEc(over[1], 60.0))
            setf(ws_, WSc, "attitudeOverrideMemory", mem_)
        put(r_, WSc.getComponentType(), ws_)
        return r_
    a_cow = ss_att(1821, 8.5, 0.5, ATTc.REVERED)            # livestock, dead ahead
    a_deer = ss_att(1822, 9.5, 0.5, ATTc.NEUTRAL)           # wildlife, dead ahead
    a_zom = ss_att(1823, 12.5, 1.5, ATTc.HOSTILE)           # 7 deg off, farther
    a_ally = ss_att(1824, 8.5, 0.5, ATTc.IGNORE)            # a summoned ally
    a_pet = ss_att(1825, 8.5, 0.5, ATTc.FRIENDLY)
    a_mad = ss_att(1826, 8.5, 0.5, ATTc.REVERED, over=(rc, ATTc.HOSTILE))          # a cow that turned on YOU
    a_madx = ss_att(1827, 8.5, 0.5, ATTc.REVERED, over=(rs, ATTc.HOSTILE))         # ... on someone else
    att_ = []
    for near_, neu_ in (([a_cow, a_zom], True), ([a_deer, a_zom], True), ([a_deer], True), ([a_deer], False), ([a_cow], True), ([a_ally], True),
                        ([a_pet], True), ([a_mad], True), ([a_madx], True)):
        ss_reset(near=near_)
        ACfg.SS_NEUTRAL = neu_
        r_ = ss_run()
        att_.append(None if r_ is None else (round(r_[0], 2), round(r_[2], 2)))
    ACfg.SS_NEUTRAL = True
    att_lvl = [int(SH.attitude(tst, r_, rc)) for r_ in (a_zom, a_deer, a_cow, a_ally, a_pet, a_mad, a_madx, m_f)]
    jfield(NPCP, "instance").set(None, npl_old)
    att_gone = int(SH.attitude(tst, a_zom, rc))          # no NPC plugin = the attitude cannot be read = neutral (never a crash)
    check([a_[0] for a_ in att_] == [14.0, 14.0, 11.0, 18.5, 18.5, 18.5, 18.5, 10.0, 18.5] and att_[0][1] == 1.5 and att_[1][1] == 1.5
          and att_lvl == [0, 1, 2, 2, 2, 0, 2, 1] and att_gone == 1,
          "R12c (spec 2 'the HOSTILE mob' - fix round, critic): a cow (Revered) or a deer (Neutral) dead ahead loses to a hostile zombie 7 deg off "
          "(behind the zombie: x 14); a neutral mob alone = a target (x 11) unless dagger.shadowStep.neutral is off; livestock, a summoned ally "
          "(Ignore), a pet (Friendly) = never (straight 18); a cow whose attitude override toward YOU is Hostile = a target (x 10), toward someone "
          "else = not; no attitude to read = neutral: %s %s %s" % (att_, att_lvl, att_gone))
    # protected mobs (Invulnerable, a trader role), party members, players with PvP off / the players row off: never targeted
    m_m = ss_mob(1806, 8.5, 64.0, 0.5, PI_ / 2.0, role="Kweebec_Merchant")
    m_i = ss_mob(1807, 8.5, 64.0, 0.5, PI_ / 2.0)
    put(m_i, INVc.getComponentType(), INVc.INSTANCE)
    ss_reset(near=[m_m, m_i])
    s6 = ss_run()
    put(rs, TCc.getComponentType(), TCc(V3(8.5, 64.0, 0.5), R3(0.0, PI_ / 2.0, 0.0)))
    put(rp, TCc.getComponentType(), TCc(V3(8.5, 64.0, 0.5), R3(0.0, PI_ / 2.0, 0.0)))
    pl_ = []
    br.put("party:fn:members", Members())          # rp = your party (N0's answer)
    for who_, pvp_, row_ in ((rs, False, True), (rs, True, True), (rp, True, True), (rs, True, False)):
        ss_reset(near=[who_])
        wcfg.setPvpEnabled(pvp_)
        ACfg.SS_PLAYERS = row_
        r_ = ss_run()
        pl_.append(None if r_ is None else r_[0])
    wcfg.setPvpEnabled(False)
    ACfg.SS_PLAYERS = True
    br.remove("party:fn:members")
    check(s6 is not None and s6[0] == 18.5 and pl_ == [18.5, 10.0, 18.5, 18.5],
          "R12c (spec 2 + section 6: 'PvP yes where PvP is on'): a trader role / an Invulnerable mob is never a target; a stranger only where the world "
          "PvP is on (behind them: x 10), a party member never, dagger.shadowStep.players off = never: %s %s" % (s6, pl_))
    # NO TARGET: straight where you look (18 blocks, pitch included); air + void ALLOWED (Skyy: no void protection); a wall in your face = free
    ss_reset(grid=Grid(world_fn(floor_ok=lambda x, z: x <= 3)))
    s7 = ss_run()
    ss_reset()
    s8 = ss_run((0.0, 1.0, 0.0))
    ss_reset(grid=Grid(world_fn([lambda x, y, z: x == 1 and 64 <= y <= 66])))
    s9 = ss_run()
    w9 = (sv(mc, STAM), str(SH.LAST_WHY), SH.LAST.get(cu))
    ss_reset()
    s10 = ss_run((1.0, 0.0, 0.0))
    check(s7 is not None and s7[:3] == (18.5, 64.0, 0.5) and s8 is not None and s8[:3] == (0.5, 82.0, 0.5) and s9 is None
          and w9 == (10.0, "no free spot ahead - nothing spent", None) and s10 is not None and s10[3] == 0.0 and s10[5] == 0.2 and not s10[6],
          "R12c (spec 2 'No target' + 'Air / void'): open void beyond x 3 -> you still step the full 18 blocks out over the void (no void check); "
          "looking straight up -> 18 blocks into the air; a wall in your face -> no step, nothing spent, no cooldown; a straight step keeps your "
          "rotation + head (yaw 0 / 0.2) and your velocity: %s %s %s %s %s" % (s7, s8, s9, w9, s10))
    # COST + COOLDOWN by metal: 4 Stamina (the traversal cap applies), too little = nothing; Copper 6 s, Onyxium 4 s, Other (Bone) 6 s
    ss_reset()
    ss_run()
    put(rc, TPc.getComponentType(), None)
    put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    c1 = ss_run()
    c1w = str(SH.LAST_WHY)
    cds = []
    for hand_, age_ in (("Weapon_Daggers_Copper", 5900), ("Weapon_Daggers_Copper", 6100), ("Weapon_Daggers_Onyxium", 3900), ("Weapon_Daggers_Onyxium", 4100),
                        ("Weapon_Daggers_Bone", 5900), ("Dagger_Iron_Black", 5400), ("Dagger_Iron_Black", 5600)):
        ss_reset(hand=hand_)
        SH.LAST.put(cu, JClass("java.lang.Long").valueOf(nowms() - age_))
        cds.append(ss_run() is not None)
    ss_reset(stam=3.0)
    c2 = (ss_run(), sv(mc, STAM), str(SH.LAST_WHY))
    ACfg.STAMINA_CAP = 2
    ss_reset()
    c3 = (ss_run() is not None, sv(mc, STAM))
    ACfg.STAMINA_CAP = 5
    mets = [int(ADf.ssMetal(i_)) for i_ in ("Weapon_Daggers_Crude", "Weapon_Daggers_Copper", "Weapon_Daggers_Adamantite_Saurian", "Weapon_Daggers_Mithril",
                                            "Weapon_Daggers_Onyxium", "Dagger_Iron_Black", "Weapon_Daggers_Bone", "Endgame_Daggers_Prisma", None)]
    check(c1 is None and c1w == "cooldown" and cds == [False, True, False, True, False, False, True] and c2 == (None, 3.0, "too little Stamina")
          and c3 == (True, 8.0) and mets == [0, 1, 5, 6, 7, 2, 8, 8, 8],
          "R12c (spec 2 'Cost' + 'Cooldown'): a second step inside the cooldown does nothing; Copper 6 s, Onyxium 4 s, Bone (Other) 6 s, a pack "
          "'Dagger_Iron_Black' = Iron 5.5 s; 3 Stamina < 4 = no step, nothing taken; trav.staminaCap 2 caps the cost (10 -> 8); the metal is a whole "
          "part of the id (Adamantite_Saurian = Adamantite, Prisma / none = Other): %s %s %s %s %s" % (c1w, cds, c2, c3, mets))
    # refusals that cost nothing: no room behind the target, a locked arena, the class lock, Shadow Step off
    box_c = set(c_ for c_ in back_c | bes_c if c_[1] >= 64) - {(8, 64, 0), (8, 65, 0)}
    m_y = ss_mob(1808, 8.5, 64.0, 0.5, y30)
    ss_reset(near=[m_y], grid=Grid(lambda x, y, z: 1 if ((x, y, z) in box_c or y == 63) else 0))
    r1 = (ss_run(), sv(mc, STAM), str(SH.LAST_WHY), SH.LAST.get(cu))
    ss_reset(near=[m_y], grid=Grid(lambda x, y, z: 1 if ((x, y, z) in side_c or y == 63) else 0))
    r1b = ss_run()
    r1bw = (str(SH.LAST_WHY), SH.ARMED.get(cu) is not None, str(SH.LAST_TARGET))
    ss_reset(near=[m_f])
    br.put("arena:fn:blocks", ArenaYes())
    r2 = (ss_run(), sv(mc, STAM), str(SH.LAST_WHY))
    br.remove("arena:fn:blocks")
    ss_reset(near=[m_f])
    br.put("class:fn:allowed", Deny())
    r3 = (ss_run(), sv(mc, STAM), str(SH.LAST_WHY))
    br.remove("class:fn:allowed")
    ss_reset(near=[m_f])
    ACfg.SS_ON = False
    r4 = (ss_run(), sv(mc, STAM), str(SH.LAST_WHY))
    ACfg.SS_ON = True
    check(r1 == (None, 10.0, "no room behind the target - nothing spent", None) and r1b is not None and not bool(TM.behind(8.5, 0.5, y30, r1b[0], r1b[2], 80.0))
          and r1bw[0].startswith("behind the target") and r1bw[1] and r1bw[2].startswith("beside")
          and r2 == (None, 10.0, "a locked arena - nothing spent") and r3 == (None, 10.0, "class lock") and r4 == (None, 10.0, "Shadow Step off"),
          "R12c (spec 2 'Arrive' + 'Safety'): a target boxed in on every side = no step, nothing spent, no cooldown; back half blocked = beside it "
          "(%s %s); a locked arena (arena:fn:blocks) / SkyyClasses' class lock / dagger.shadowStep.enabled off = nothing: %s %s %s %s" % (r1b, r1bw, r1, r2, r3, r4))
    # the marker's SPAWN (ArmoryTravSys -> ArmoryTrav.added, code 11000): removed at once, ONE KunaiJob 3 with the launch direction; the shadow
    ss_reset(near=[m_f])
    om_, opm_ = launched(SS_MARK, 1809, 0.5, 65.6, 0.5)
    AT.added(om_, opm_, int(ADf.pidCode(SS_MARK)), tst, tbuf)
    jm_ = list(TWd.JOBS)
    mk1 = (int(ADf.pidCode(SS_MARK)), om_ in list(TBf.REMOVED), len(jm_), int(jm_[0].kind) if jm_ else None,
           [round(float(x_), 3) for x_ in jm_[0].pt] if jm_ else None)
    TWd.JOBS.clear()
    ACfg.TRAV_FX = True
    seen_ = ArrayList()
    AT.PSEEN = seen_
    for j_ in jm_:
        j_.run()
    AT.PSEEN = None
    ACfg.TRAV_FX = False
    mk2 = comp(rc, TPc.getComponentType())
    ss_reset(near=[m_f])
    ACfg.SS_ON = False
    om2_, opm2_ = launched(SS_MARK, 1810, 0.5, 65.6, 0.5)
    AT.added(om2_, opm2_, int(ADf.pidCode(SS_MARK)), tst, tbuf)
    mk3 = (om2_ in list(TBf.REMOVED), len(list(TWd.JOBS)))
    ACfg.SS_ON = True
    check(mk1 == (11000, True, 1, 3, [1.0, 0.0, 0.0]) and mk2 is not None and round(float(mk2.getPosition().x()), 2) == 10.0 and SS_FX in [str(x_) for x_ in seen_]
          and mk3 == (True, 0),
          "R12c (the wiring): the hold's marker SPAWN (code 11000) -> removed at once + ONE world-thread job (kind 3) aimed along the launch "
          "direction -> the step behind the mob; the fading shadow particle %s is spawned where you stood (trav.fx on); dagger.shadowStep.enabled "
          "off = the marker removed, no job: %s %s" % (SS_FX, mk1, mk3))
    print("R12c. Shadow Step: target by aim (range / cone / line of sight), behind + facing, PvP / party / protected rules, straight 18 (void + air "
          "allowed), costs + cap, cooldowns by metal, free refusals, marker wiring, shadow")

    # --- R12d. THE BACKSTAB (Shadow.filter from ArmoryTuneSys, the Filter group) on REAL Damage objects
    # fix round: the REAL vanilla damage causes (the Fall way, Q0): a Damage resolves its cause through the store
    bad_c = []
    for nm_ in ("Physical", "Slashing", "Projectile", "Elemental", "Fire"):
        if DCSc.getAssetMap().getAsset(nm_) is None:
            o_, w_ = dec(DCSc, nm_, AZ.read("Server/Entity/Damage/%s.json" % nm_).decode("utf-8-sig"))
            keep_c = HashMap(pbu)
            pbu.clear()
            l_ = load(DCSc, [o_], "Hytale:Hytale") if o_ is not None else None
            pbu.putAll(keep_c)
            if o_ is None or l_ is False:
                bad_c.append((nm_, w_, l_))
    C_ = dict((nm_, DCSc.getAssetMap().getAsset(nm_)) for nm_ in ("Physical", "Slashing", "Projectile", "Elemental", "Fire"))
    phy_ = [bool(SH.physical(C_[nm_])) for nm_ in ("Physical", "Slashing", "Projectile", "Fire")] + [bool(SH.physical(None))]
    check(not bad_c and all(C_.values()) and str(C_["Slashing"].getInherits()) == "Physical" and phy_ == [True, True, False, False, False]
          and float(ADf.SS_MELEE) == 4.75,
          "R12d (fix round): the vanilla Physical / Slashing / Projectile / Elemental / Fire causes decoded + loaded; Shadow.physical: Physical yes, "
          "Slashing (inherits Physical) yes, Projectile / Fire / none no; dagger reach = the longest vanilla dagger selector 3.75 + 1 = %s: %s %s" % (
              ADf.SS_MELEE, bad_c, phy_))
    m_t = ss_mob(1811, 8.5, 64.0, 0.5, PI_ / 2.0)
    put(rc, TCc.getComponentType(), TCc(V3(10.0, 64.0, 0.5), R3(0.0, PI_ / 2.0, 0.0)))

    def bs(amount=10.0, hand="Weapon_Daggers_Copper", src=None, arm=3000, sig=None, at=10.0, cause="Physical"):
        SH.ARMED.clear()
        if arm is not None:
            SH.ARMED.put(cu, JClass("java.lang.Long").valueOf(nowms() + arm))
        LP.HAND.put(cu, hand)
        put(rc, TCc.getComponentType(), TCc(V3(at, 64.0, 0.5), R3(0.0, PI_ / 2.0, 0.0)))
        if sig is not None:
            @JImplements("java.util.function.Function")
            class Sig:
                @JOverride
                def apply(self, o): return JClass("java.lang.Boolean").valueOf(sig)
            SH.SIG = Sig()
        d_ = DMGc(src if src is not None else DENTc(rc), C_[cause], JFloat(amount))
        SH.filter(tbuf, m_t, d_)
        SH.SIG = None
        return round(float(d_.getAmount()), 3), SH.ARMED.get(cu) is not None
    b1 = bs()
    SH.ARMED.put(cu, JClass("java.lang.Long").valueOf(nowms() + 3000))
    d2_ = DMGc(DENTc(rc), C_["Physical"], JFloat(10.0))
    SH.filter(tbuf, m_t, d2_)
    d3_ = DMGc(DENTc(rc), C_["Physical"], JFloat(10.0))
    SH.filter(tbuf, m_t, d3_)
    b2 = (round(float(d2_.getAmount()), 3), round(float(d3_.getAmount()), 3))
    bres = [bs(arm=-50), bs(src=DPS(rc, REFc(tst, 7899))), bs(hand="Weapon_Sword_Iron"), bs(amount=0.0), bs(sig=True), bs(sig=True, at=7.0),
            bs(sig=True, hand="Weapon_Daggers_Onyxium"), bs(hand="Dagger_Iron_Black"), bs(arm=None)]
    ACfg.SS_ON = False
    boff = bs()
    ACfg.SS_ON = True
    ACfg.SS_BONUS = 0.25
    bb = bs()
    ACfg.SS_BONUS = 0.1
    sig_eng = bool(SH.sigHit(tst, rc))
    # fix round (critic): a kunai / arrow thrown with a dagger in hand (plain EntitySource, Physical) from beyond dagger reach, a Projectile /
    # Fire cause, keep the window; a Slashing hit (inherits Physical) and a hit at the edge of reach spend it
    mel_ = [bs(at=16.0), bs(cause="Projectile"), bs(cause="Fire"), bs(cause="Slashing"), bs(at=8.5 + 4.75 + 0.3 - 0.05), bs(at=8.5 + 4.75 + 0.3 + 0.1)]
    put(rc, TCc.getComponentType(), TCc(V3(10.0, 64.0, 0.5), R3(0.0, PI_ / 2.0, 0.0)))          # back behind the mob (the wiring check below)
    check(b1 == (16.5, False) and b2 == (16.5, 10.0)
          and bres == [(10.0, False), (10.0, True), (10.0, True), (0.0, True), (11.0, False), (16.5, False), (16.5, False), (16.5, False), (10.0, False)]
          and boff == (10.0, True) and bb == (18.75, False) and sig_eng is False
          and mel_ == [(10.0, True), (10.0, True), (10.0, True), (16.5, False), (16.5, False), (10.0, True)],
          "R12d (Skyy: 'your next hit is a guaranteed back stab. and do a small bonus'): the next dagger melee hit within 3 s = x1.5 (the vanilla "
          "backstab) x 1.1 (10 -> 16.5) ONCE (the next hit 10); after the window / a projectile / a sword / the 0-damage guard shove: untouched (the "
          "last three keep the window); a signature hit from behind (it has the vanilla x1.5 already) x1.1 only, from the front x1.65, an Onyxium "
          "signature (no vanilla backstab) x1.65; a pack dagger counts; off = untouched; backstabBonus 0.25 -> x1.875; no InteractionManager = not a "
          "signature; FIX ROUND: a hit from 7.5 blocks (a thrown kunai / arrow), a Projectile or Fire cause = untouched + the window kept, a Slashing "
          "hit and one inside reach (4.75 + half the mob) = the backstab: %s %s %s %s %s %s" % (b1, b2, bres, boff, bb, mel_))
    tune12 = calls_of(PKG + "ArmoryTuneSys", "handle")
    chk12 = None
    try:
        TCh12 = stub("TChunk12", "com.hypixel.hytale.component.ArchetypeChunk", ["public static com.hypixel.hytale.component.Ref R = null;"],
                     ["public com.hypixel.hytale.component.Ref getReferenceTo(int i) { return R; }"])
        ch12 = U.allocateInstance(TCh12.class_)
        TCh12.R = m_t
        SH.ARMED.put(cu, JClass("java.lang.Long").valueOf(nowms() + 3000))
        LP.HAND.put(cu, "Weapon_Daggers_Copper")
        d12_ = DMGc(DENTc(rc), C_["Physical"], JFloat(10.0))
        JClass(PKG + "ArmoryTuneSys")(True).handle(0, ch12, tst, tbuf, d12_)
        chk12 = round(float(d12_.getAmount()), 3)
    except Exception as e_:
        chk12 = "stub: " + str(e_)[:120]
    check(tune12.count("filter") >= 2 and chk12 == 16.5,
          "R12d (wiring): ArmoryTuneSys.handle (the Filter group, before armour) runs Shadow.filter: a Copper dagger hit 10 inside the window on the chunk's "
          "entity -> %s" % chk12)
    put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    SH.ARMED.clear()
    print("R12d. backstab: x1.65 once within 3 s, signature x1.1 from behind, others untouched, bonus row, ArmoryTuneSys wiring")

    # --- R12e. THE ROWS: 9 + the cooldown table + 3 read-only rows, the loader clamps, armory:shadow, the default file
    Rows12 = JClass(PKG + "CfgRows")
    k12 = [str(k_) for k_ in Rows12.KEYS]
    d12 = dict(zip(k12, [str(d_) for d_ in Rows12.DEFS]))
    t12 = dict(zip(k12, [str(d_) for d_ in Rows12.TYPES]))
    f12 = dict(zip(k12, [str(d_) for d_ in Rows12.FLAGS]))
    want12 = {"dagger.shadowStep.enabled": "true", "dagger.shadowStep.targetRange": "24", "dagger.shadowStep.targetCone": "30",
              "dagger.shadowStep.behind": "1.5", "dagger.shadowStep.noTargetDistance": "18", "dagger.shadowStep.backstabWindow": "3",
              "dagger.shadowStep.backstabBonus": "0.1", "dagger.shadowStep.staminaCost": "4", "dagger.shadowStep.players": "true",
              "dagger.shadowStep.neutral": "true"}
    dcfg12 = str(ACfg.DEF_CFG)
    cdw = {"Crude": "6", "Copper": "6", "Iron": "5.5", "Thorium": "5", "Cobalt": "5", "Adamantite": "4.5", "Mithril": "4", "Onyxium": "4", "Other": "6"}
    bad12 = dict((k_, (d12.get(k_), v_)) for k_, v_ in want12.items() if d12.get(k_) != v_)
    fx12 = [k_ for k_ in k12 if k_.startswith("fixed.shadow.")]
    check(not bad12 and t12["dagger.shadowStep.cooldown"] == "table" and "danger" in f12["dagger.shadowStep.enabled"].split(",")
          and sorted(fx12) == ["fixed.shadow.backstab", "fixed.shadow.keys", "fixed.shadow.look"] and all(f12[k_] == "ro" for k_ in fx12)
          and all(("\n%s=%s\n" % (k_, v_)) in dcfg12 for k_, v_ in want12.items())
          and all(("\ndagger.shadowStep.cooldown.%s=%s\n" % (k_, v_)) in dcfg12 for k_, v_ in cdw.items()),
          "R12e (spec 4): the 10 rows + the cooldown table (Crude / Copper 6 s ... Onyxium 4 s, Other 6 s) emit with the spec defaults, enabled is a "
          "danger switch, 3 read-only rows (keys, shadow look, backstab x1.5), every default in the default file: %s %s" % (bad12, fx12))
    pr12 = Props()
    for k_, v_ in (("dagger.shadowStep.targetRange", "99"), ("dagger.shadowStep.targetCone", "1"), ("dagger.shadowStep.behind", "9"),
                   ("dagger.shadowStep.noTargetDistance", "0"), ("dagger.shadowStep.backstabWindow", "0"), ("dagger.shadowStep.backstabBonus", "5"),
                   ("dagger.shadowStep.staminaCost", "-3"), ("dagger.shadowStep.players", "off"), ("dagger.shadowStep.enabled", "off"),
                   ("dagger.shadowStep.neutral", "off"),
                   ("dagger.shadowStep.cooldown.Onyxium", "99"), ("dagger.shadowStep.cooldown.Copper", "2.5")):
        pr12.setProperty(k_, v_)
    ACfg.apply(pr12)
    cl12 = (int(ACfg.SS_RANGE), int(ACfg.SS_CONE), float(ACfg.SS_BEHIND), int(ACfg.SS_FAR), float(ACfg.SS_WINDOW), float(ACfg.SS_BONUS), float(ACfg.SS_STAM),
            bool(ACfg.SS_PLAYERS), bool(ACfg.SS_ON), [float(x_) for x_ in ACfg.SS_CD], bool(ACfg.SS_NEUTRAL))
    st12 = str(br.get("armory:shadow"))
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    st12d = str(br.get("armory:shadow"))
    chk_ok = JClass(PKG + "ArmoryHooks").checkShadow("dagger.shadowStep.cooldown[Other]", "3")
    chk_bad = JClass(PKG + "ArmoryHooks").checkShadow("dagger.shadowStep.cooldown[Bronze]", "3")
    check(cl12 == (48, 10, 4.0, 2, 0.5, 1.0, 0.0, False, False, [6.0, 2.5, 5.5, 5.0, 5.0, 4.5, 4.0, 30.0, 6.0], False) and st12.startswith("dagger Shadow Step OFF")
          and "neutral never" in st12 and bool(ACfg.SS_NEUTRAL) and int(ACfg.SS_CONE) == 30
          and st12d.startswith("dagger Shadow Step on - target 24 blocks in a 30 deg cone around your aim (hostile first, neutral too") and "Onyxium 4s" in st12d and "x1.5 x (1 + 0.1)" in st12d
          and chk_ok is None and chk_bad is not None,
          "R12e: the loader clamps like the kit (99 -> 48, cone 1 -> 10, 9 -> 4, 0 -> 2, 0 -> 0.5, 5 -> 1, -3 -> 0, Onyxium 99 -> 30); armory:shadow names the "
          "live numbers; the table check takes the 8 metals + Other only: %s | %s | %r %r" % (cl12, st12d, chk_ok, chk_bad))
    print("R12e. rows + clamps + armory:shadow + table check")

    # --- R12f. vs the 0.1.7 jar: the new files = exactly the 5 Shadow Step files + Shadow.class, every other non-class file byte-identical
    OLD17 = os.path.join(HERE, "SkyyArmory-0.1.7.jar")
    if not os.path.isfile(OLD17):
        print("R12f. NOTE no SkyyArmory-0.1.7.jar here - the old-vs-new file compare is skipped")
    else:
        with zipfile.ZipFile(OLD17) as oz_:
            on_ = oz_.namelist()
            new_ = sorted(set(JN) - set(on_))
            gone_ = sorted(set(on_) - set(JN))
            diff_ = [n_ for n_ in on_ if n_ in JSET and not n_.endswith(".class") and n_ != "manifest.json" and oz_.read(n_) != JZ.read(n_)]
            ccl = sorted(n_ for n_ in on_ if n_.endswith(".class") and n_ in JSET and oz_.read(n_) != JZ.read(n_))
        check(sorted(n_ for n_ in new_ if not n_.endswith(".class")) == sorted(_l18p) and [n_ for n_ in new_ if n_.endswith(".class")] == ["com/skyy/armory/Shadow.class"]
              and not gone_ and not diff_,
              "R12f: vs SkyyArmory-0.1.7.jar - the new files are exactly the 5 Shadow Step files + Shadow.class, none gone, every other non-class file "
              "byte-identical: %s %s %s" % ([n_ for n_ in new_ if n_ not in _l18p][:4], gone_[:3], diff_[:3]))
        print("R12f. vs 0.1.7: +5 files (+ Shadow.class), %d classes changed: %s" % (len(ccl), ", ".join(c_.split("/")[-1][:-6] for c_ in ccl)))
    AT.NEAR = None
    print("R12. 0.1.8 dagger Shadow Step: every path executed")
'''
hrep('''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''',
     R12 + '''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''')


out_t = ts.replace(LF, TNL)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(out_t)
print("wrote %s (%d lines)" % (os.path.relpath(TDST, ROOT), out_t.count(TNL) + 1))
