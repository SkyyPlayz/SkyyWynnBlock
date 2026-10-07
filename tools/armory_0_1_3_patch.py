"""Derive SkyyArmory/build_skyyarmory_0.1.3.py (+ its harness SkyyArmory/test_skyyarmory_0.1.3.py) from the GENERATED 0.1.2
(SkyyArmory/build_skyyarmory_0.1.2.py = the tools/deploy_set.py SET pin, made by tools/armory_0_1_2_patch.py; test_skyyarmory_0.1.2.py =
its harness). Every anchor is asserted (rep = exactly one hit). Edit THIS file, never the generated scripts.
Run:  python tools/armory_0_1_3_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.3.py   then   python SkyyArmory/test_skyyarmory_0.1.3.py
      (never --deploy; SkyyArmory 0.1.3 needs the same deploy partners as 0.1.2 - SkyyClasses 0.1.12+ - and nothing new)

0.1.3 = THE BOW LEAP + THE APEX HANG (Skyy 2026-10-06, LOCKED docs/answered/classes.md: "add the wynncraft like bow traversal ... pushes you
exactly opposite the direction you are looking. then shoots an explosive arrow ... a slight pause ... on both the bow and wand, so you are at
the Hight of your jump, it slows slightly so you can aim ... then you fall") + the COPPER / ONYXIUM CROSSBOWS (Skyy: "Copper + Onyxium
(Recommended)", docs/answered/gear.md 2026-10-06) + the lingering-particle fix (Skyy: "it leaves partials behind", "the blue balls stay") +
hop.force 13 -> 30 (Skyy: "30"):
  BOW LEAP: the vanilla full-draw release Weapon_Shortbow_Primary_Shoot_Strength_4 (the ONE interaction the Template_Weapon_Shortbow var
    Primary_Shoot_Strength_4 parents; every vanilla shortbow reaches it - build-checked) is overridden by id at its vanilla path with ONE change:
    Config = SkyyArmory_Bow_Leap (= the vanilla Projectile_Config_Arrow_Shortbow_Strength_4 fully resolved, only its Model id is ours, the
    same Arrow_Crude look). GrappleBoltSys (already a RefSystem on Projectile + StandardPhysicsProvider) sees that model at SPAWN -> Leap.onBowShot:
    part.bowtrav, a bow in hand, class lock (Archer), bow.stamina + bow.mana (bows are physical: 3 Stamina : 1 Mana) - anything refused = the
    arrow is LEFT ALONE (the vanilla full-draw shot, its own damage). Else the arrow is removed at once, you are pushed exactly opposite your look
    (the wand hop maths: bow.hopForce 30, the dagger dash config, half without ground behind, a damaging fall kept), and the rhythm runs.
  THE RHYTHM (bow AND wand): RISE (until the top: the client's own vertical speed <= 0.5 after it rose, or you start to come down, at most
    LEAP_RISE_MAX s) -> HANG (hop.hangSeconds / bow.hangSeconds, 0.35: a Velocity Set every tick = your hop's sideways speed x LEAP_KEEP + a
    slow drift down hop.hangFall / bow.hangFall 1.5 b/s - the grapple pull's per-tick Set path, Skyy tested it in game) -> FIRE where you NOW
    look (TargetUtil.getLook: the eye + the head direction) -> normal falling (no more Sets; fall damage untouched: a damaging fall is kept by
    the hop and ends the hang at once - never erased). No slow-fall effect exists in the engine (build-probed: EntityEffect ApplicationEffects /
    MovementEffects carry no gravity; MovementSettings only inverted gravity), so the per-tick Set is the only path.
  BOW SHOT = SkyyArmory_Bow_Blast (a legacy projectile, the vanilla Arrow_FullCharge resolved; ArmoryTrav.spawn = LaunchProjectileInteraction's
    own steps, creator = you). Its direct hit deals the bow's full-draw damage (Leap.BOW_IDS / BOW_DMG, read from every vanilla shortbow's
    Primary_Shoot_Damage_Strength_4 at build time; unknown bows = the template's 15) - ArmoryTuneSys scales the hit to it; the BLAST (direct
    hit or where it lands) hits every OTHER enemy within bow.blastRadius 4 for bow.blastPercent 60 % of it (the wand burst's rules: PvP + party,
    the whole damage pipeline, never a block). WAND: the charged orb the chain launches is removed at its SPAWN (after the class lock + the
    traversal Stamina), the hop runs, and at the end of the hang ArmoryTrav.spawn launches the same orb where you look - burst + heal orb as
    before. hop.hangSeconds 0 = the 0.1.2 way (orb at the cast, hop at once).
  CROSSBOWS: Weapon_Crossbow_Copper_Wynn + Weapon_Crossbow_Onyxium_Wynn = the vanilla Weapon_Crossbow_Iron item (Parent Template_Weapon_Crossbow:
    same model, interactions, Ammo / reload, the grapple) with the tier's numbers (the Iron -> More Crossbow Tiers x1.25 step) and a texture +
    icon RECOLOURED AT BUILD TIME (the metal parts only, skyyart.metal_gradient = the metal wands' palettes). Ids: start Weapon_Crossbow_ (SkyyClasses
    Archer rule, SkyySkills' keepLoaded prefix), hold 'crossbow' (the grapple), a metal token (SkyyGear bands), and the _Wynn tail no vanilla /
    More Crossbow Tiers / Frah's Crossbow Tiers id uses (Frah already ships Weapon_Crossbow_Onyxium). Recipes at the Weapon_Bench (Weapon_Bow).
  PARTICLES THAT STAY (why: every point particle SkyyArmory spawned was an endless emitter - GreenOrbTrail's spawners emit 60/s with no
    LifeSpan / TotalParticles (they are built to ride a projectile and die with it), and Totem_Heal_Simple_Test lives 9 s; spawned at a point
    through ParticleUtil nothing ever ends them, so the rope dots, the blink light and the heal orb's blue ring stayed in the sky): every
    point system now has its own SYSTEM LifeSpan (the vanilla Block_Break / Totem field, ParticleSystem.getLifeSpan) = its re-draw interval and
    every particle lives at most FX_FADE - and the Java never starts one whose emission would outlive its effect. Last particle gone <= 0.3 s
    after the grapple ends (rope 0.15 + 0.15), the trail / ring / heal pulse ends (fade 0.25 / 0.25 / 0.3), the burst <= 1 s total.
  hop.force 13 -> 30 (max 25 -> 50): ArmoryCfg.migrate013 = the migrate012 rules (an untouched one-line 13 becomes 30, any other value kept +
    logged, History copy first, one Undo-able change-log line, a marker so it runs once).
"""
import os
import re
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.2.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.3.py")
TSRC = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.2.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.3.py")

raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.2"\nMOD = "SkyyArmory"' in s and "FIX ROUND (grapple-fix 2026-10-06, critic findings)" in s, "build_skyyarmory_0.1.2.py is not the 0.1.2 pin"
SYS0 = s.count("registerSystem(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:140])
    s = s.replace(old, new)


# ================================================================================================ the new rows (Skyy's numbers where given)
# (key, label, cat, type, default, min, max, opts, unit, flags, help, ArmoryCfg field, Java type, Java default, config.properties comment)
L_ROWS = [
    ("hop.hangSeconds", "Wand hang at the top (s)", "hop", "dec", "0.35", "0", "1.5", "", "s", "live",
     "Hop, a slow fall at the top to aim, THEN the orb fires. 0 = the orb at the cast (0.1.2).", "HOP_HANG", "double", "0.35",
     "Wand hold: the hop, then this many seconds of slow fall at the top (to aim), then the orb fires where you look (0 = the orb at the cast)."),
    ("hop.hangFall", "Wand hang drift down (b/s)", "hop", "dec", "1.5", "0", "10", "", "", "live",
     "Downward speed while hanging (0 = hold still).", "HOP_FALL", "double", "1.5",
     "Downward speed (blocks per second) while the wand hop hangs at the top (0 = hold still)."),
    ("part.bowtrav", "Bow leap (full-draw traversal)", "bow", "bool", "true", "", "", "", "", "live,part,danger",
     "Off = a full-draw shot is the vanilla arrow again.", "PART_BOWTRAV", "boolean", "true",
     "Bow full draw = leap back + hang + blast arrow (Skyy 2026-10-06). Off = the vanilla full-draw arrow."),
    ("bow.hopForce", "Bow leap force", "bow", "dec", "30", "0", "50", "", "", "live",
     "Pushes you opposite your look (look down = up). 0 = no leap, the vanilla arrow.", "BOW_FORCE", "double", "30",
     "Bow leap force: pushes you exactly opposite your look (look down = straight up; 0 = no leap, the vanilla arrow)."),
    ("bow.hangSeconds", "Bow hang at the top (s)", "bow", "dec", "0.35", "0", "1.5", "", "s", "live",
     "A slow fall at the top to aim; then the blast arrow fires. 0 = it fires at the top.", "BOW_HANG", "double", "0.35",
     "Bow leap: this many seconds of slow fall at the top (to aim), then the blast arrow fires where you look (0 = at the top)."),
    ("bow.hangFall", "Bow hang drift down (b/s)", "bow", "dec", "1.5", "0", "10", "", "", "live",
     "Downward speed while hanging (0 = hold still).", "BOW_FALL", "double", "1.5",
     "Downward speed (blocks per second) while the bow leap hangs at the top (0 = hold still)."),
    ("bow.blastRadius", "Blast radius (blocks)", "bow", "dec", "4", "1", "12", "", "blocks", "live",
     "Enemies around the blast arrow's hit take the blast. Never breaks blocks.", "BOW_RADIUS", "double", "4",
     "Blast radius (blocks) around where the blast arrow hits (it never breaks blocks)."),
    ("bow.blastPercent", "Blast damage to others (%)", "bow", "int", "60", "0", "100", "step=5", "%", "live",
     "% of the bow's full-draw damage; the enemy hit directly takes all of it.", "BOW_PCT", "int", "60",
     "Blast damage to the OTHER enemies, % of the bow's full-draw damage (the enemy hit directly takes all of it)."),
    ("bow.stamina", "Bow leap Stamina", "bow", "dec", "3", "0", "10", "", "", "live",
     "Physical traversal: more Stamina than Mana. Too little = a normal shot.", "BOW_STAM", "double", "3",
     "A bow leap costs this much Stamina (physical: more Stamina than Mana)..."),
    ("bow.mana", "Bow leap Mana", "bow", "dec", "1", "0", "50", "", "", "live",
     "Only where the player has Mana. Too little = a normal shot.", "BOW_MANA", "double", "1",
     "... and this much Mana where the player has Mana. Too little of either = the normal full-draw arrow."),
]
for _r in L_ROWS:
    assert len(_r) == 15 and len(_r[1]) <= 40 and len(_r[10]) <= 100 and all(32 <= ord(c) < 127 for c in "".join(_r)), _r
L_DEF = dict((r[0], r[4]) for r in L_ROWS)
assert L_DEF["bow.hopForce"] == "30" and L_DEF["bow.hangSeconds"] == "0.35" and L_DEF["hop.hangSeconds"] == "0.35"
assert float(L_DEF["bow.stamina"]) > float(L_DEF["bow.mana"]), "bows are physical: more Stamina than Mana"

M13_MARK_ID = "SkyyArmory 0.1.3 wand hop force"
M13_MARK = ("# %s (Skyy 2026-10-06: \"30\"): the wand hop pushes 30 (0.1.2: 13) - a line still on the old 13 was updated once" % M13_MARK_ID)
assert "=" not in M13_MARK and all(32 <= ord(c) < 127 for c in M13_MARK)

# ================================================================================================ header + version
rep('''"""SkyyArmory 0.1.2 - build script (javassist via jpype). GENERATED by tools/armory_0_1_2_patch.py from the GENERATED 0.1.1 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.2.py -> SkyyArmory/SkyyArmory-0.1.2.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.2.py (scratch tools/dev/scratch/armory012/).
''', '"""SkyyArmory 0.1.3 - build script (javassist via jpype). GENERATED by tools/armory_0_1_3_patch.py from the GENERATED 0.1.2 - edit the\n'
    'patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.3.py -> SkyyArmory/SkyyArmory-0.1.3.jar (never --deploy). Harness:\n'
    'python SkyyArmory/test_skyyarmory_0.1.3.py (scratch tools/dev/scratch/armory013/).\n\n'
    + open(__file__, encoding="utf8").read().split('"""')[1].split("\n", 3)[3].strip() + "\n\n"
    '0.1.2 (the base, everything below is still true unless 0.1.3 above says otherwise):\n')
rep('VERSION = "0.1.2"\nMOD = "SkyyArmory"', 'VERSION = "0.1.3"\nMOD = "SkyyArmory"')

# ================================================================================================ 0.1.3 constants
rep('''# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)''', '''# ================================================================= 0.1.3 BOW LEAP + APEX HANG + CROSSBOWS + PARTICLE LIFE
LEAP_RISE_MIN, LEAP_RISE_MAX = 0.1, 1.0   # the rise: the top is looked for after 0.1 s; at most 1 s (a hop that never comes down)
LEAP_APEX_VY = 0.5               # the top = the client's vertical speed (PlayerInput$SetClientVelocity) at most this, after it rose
LEAP_KEEP = 0.2                  # the hang keeps this share of the hop's sideways speed (a slight drift, not a stop)
BOW_INT = "Weapon_Shortbow_Primary_Shoot_Strength_4"      # the vanilla full-draw release (the template var's parent; overridden by id)
BOW_LEAP = "SkyyArmory_Bow_Leap"                          # its ProjectileConfig id AND the model id the Java knows the shot by
BOW_BLAST = "SkyyArmory_Bow_Blast"                        # the explosive arrow fired at the top (legacy projectile, code 6000)
BLAST_CODE = 6000
BLAST_TTL = 4.0                  # s: a blast arrow that hits nothing bursts after this (vanilla Arrow_FullCharge: 20)
BLAST_SPEED = 60                 # b/s muzzle speed (Arrow_FullCharge: 50)
XBOWS = [("Copper", "Weapon_Crossbow_Copper_Wynn"), ("Onyxium", "Weapon_Crossbow_Onyxium_Wynn")]
# the tier numbers (the Iron -> More Crossbow Tiers step: Adamantite -> Mithril x1.25 on every damage, durability +30 / +30 / +40):
# Copper = Iron / 1.25, Onyxium = Mithril x 1.25; reload = the seconds per bolt (vanilla Common_StatAmmoReload_Effects 0.3)
XSTAT = {"Copper": {"std": 8, "combo": 22, "sig": 62, "dur": 90, "reload": 0.375},
         "Onyxium": {"std": 31, "combo": 85, "sig": 244, "dur": 260, "reload": 0.3}}
# FX life (seconds): emit = the system LifeSpan (= its re-draw interval), fade = the longest particle life; gone <= emit + fade after the
# last draw, and the Java never draws one whose emission would outlive its effect
FX_LIFE = {"trail": (0.25, 0.25), "ring": (0.5, 0.25), "heal": (0.5, 0.3), "rope": (0.15, 0.15), "burst": (0.3, 0.7)}
PS_RING2, PS_HEAL2, PS_BURST2 = "SkyyArmory_Ring_Blue", "SkyyArmory_Heal_Pulse", "SkyyArmory_Burst"
M13_MARK_ID = %r
M13_MARK = %r
CFG_LEAP = ''' % (M13_MARK_ID, M13_MARK) + "[\n" + "".join("    %r,\n" % (r,) for r in L_ROWS) + ''']

# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)''')
rep("cd=0.0, hopForce=13.0, hopGround=6,", "cd=0.0, hopForce=30.0, hopGround=6,")
rep(''' ('hop.force',
  'Wand hop force',
  'hop',
  'dec',
  '13',
  '0',
  '25',
  '',
  '',
  'live',
  '0 = no hop. 13 = the vanilla dagger dash.',
  'HOP_FORCE',
  'double',
  '13',
  'Wand hop force (13 = the vanilla dagger dash, 0 = no hop).'),''', ''' ('hop.force',
  'Wand hop force',
  'hop',
  'dec',
  '30',
  '0',
  '50',
  '',
  '',
  'live',
  'Skyy 2026-10-06: 30 (0.1.2: 13 = the dagger dash, too weak). 0 = no hop.',
  'HOP_FORCE',
  'double',
  '30',
  'Wand hop force (Skyy 2026-10-06: 30; 13 = the vanilla dagger dash, 0 = no hop).'),''')
rep("""  'Staff quick shots hit this % harder (per Mana) than wand quick shots.')] + CFG_GRAPPLE      # 0.1.2: the grapple rows (same machinery)
""", """  'Staff quick shots hit this % harder (per Mana) than wand quick shots.')] + CFG_GRAPPLE + CFG_LEAP      # 0.1.2 grapple + 0.1.3 leap rows
""")

# ================================================================================================ the 0.1.3 assets (after the reference closure)
L_ASSETS = r'''
# ================================================================= 0.1.3 ASSETS (bow leap, blast arrow, crossbows, particle life) - vanilla shapes first
# ---- (1) THE BOW LEAP: the full-draw release override (one change: Config), the leap config (vanilla Strength_4 resolved, our model id)
P_BOW_INT = "Server/Item/Interactions/Weapons/Shortbow/Primary/Shoot/%s.json"
VBOW4 = az_get("int", BOW_INT)
assert VBOW4 == {"Parent": "Weapon_Shortbow_Primary_Shoot_Projectile", "Config": "Projectile_Config_Arrow_Shortbow_Strength_4",
                 "Effects": {"ItemAnimationId": "ShootCharged"}}, VBOW4
assert _IDX["int"][BOW_INT] == [P_BOW_INT % BOW_INT], _IDX["int"][BOW_INT]
_bow_users = sorted(n for n in AZ_NAMES if n.startswith("Server/") and n.endswith(".json") and ('"%s"' % BOW_INT).encode() in AZ.read(n))
# the users: the template var + the two Charging steps' Replace defaults (vanilla charge, the developer Test_Zoom bow) - all one release
assert _bow_users == ["Server/Item/Interactions/Weapons/Shortbow/Primary/Shoot/Test_Zoom_Bow_Primary_Shoot_Charge.json",
                      "Server/Item/Interactions/Weapons/Shortbow/Primary/Shoot/Weapon_Shortbow_Primary_Shoot_Charge.json",
                      "Server/Item/Items/Weapon/Shortbow/Template_Weapon_Shortbow.json"], _bow_users
assert az_get("int", "Weapon_Shortbow_Primary_Shoot_Projectile")["Type"] == "Projectile"
_vbt = az_get("item", "Template_Weapon_Shortbow")
assert _vbt["Interactions"]["Primary"] == "Root_Weapon_Shortbow_Primary_Shoot" and _vbt["InteractionVars"]["Primary_Shoot_Strength_4"] == {
    "Interactions": [{"$Comment": "Launching a shot with full charge (1.2s+)", "Parent": BOW_INT}]}, _vbt["InteractionVars"]["Primary_Shoot_Strength_4"]


def item_resolved(iid, seen=None):
    """an Assets.zip item with its Parent chain merged (top-level keys; InteractionVars per var key - the engine's own inheritance shape)"""
    seen = seen or set()
    assert iid not in seen, iid
    seen.add(iid)
    d = az_get("item", iid)
    if not d.get("Parent"):
        return json.loads(json.dumps(d))
    b = item_resolved(d["Parent"], seen)
    for k, v in d.items():
        if k == "Parent":
            continue
        if k == "InteractionVars" and isinstance(b.get(k), dict):
            b[k] = dict(b[k])
            b[k].update(v)
        else:
            b[k] = v
    return b


BOW_REACH, BOW_TABLE = [], []          # the bows our override reaches + (id, full-draw damage) for the blast arrow
for _bi in sorted(_IDX["item"]):
    if not _bi.startswith("Weapon_Shortbow_"):
        continue
    _bd = item_resolved(_bi)
    _bv = (_bd.get("InteractionVars") or {})
    _s4 = (_bv.get("Primary_Shoot_Strength_4") or {}).get("Interactions") or [{}]
    if (_bd.get("Interactions") or {}).get("Primary") == "Root_Weapon_Shortbow_Primary_Shoot" and _s4[0].get("Parent") == BOW_INT:
        BOW_REACH.append(_bi)
        _dmg = _bv["Primary_Shoot_Damage_Strength_4"]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Projectile"]
        assert isinstance(_dmg, (int, float)) and _dmg > 0, (_bi, _dmg)
        BOW_TABLE.append((_bi, int(round(_dmg))))
BOW_DEF = int(_vbt["InteractionVars"]["Primary_Shoot_Damage_Strength_4"]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Projectile"])
assert BOW_DEF == 15 and len(BOW_REACH) >= 12 and "Weapon_Shortbow_Iron" in BOW_REACH and "Weapon_Shortbow_Crude" in BOW_REACH, (BOW_DEF, BOW_REACH)
assert dict(BOW_TABLE)["Weapon_Shortbow_Iron"] == 19 and dict(BOW_TABLE)["Weapon_Shortbow_Mithril"] == 37, BOW_TABLE
BOW_OTHER = sorted(i for i in _IDX["item"] if i.startswith("Weapon_Shortbow_") and i not in BOW_REACH)
INTS[BOW_INT] = {"Parent": VBOW4["Parent"], "Config": BOW_LEAP, "Effects": json.loads(json.dumps(VBOW4["Effects"]))}    # by id, like Wand_Primary
put(P_BOW_INT % BOW_INT, INTS[BOW_INT])


def pcfg_resolved(pid):
    d = az_json(az_path("pcfg", pid))
    if not d.get("Parent"):
        return json.loads(json.dumps(d))
    b = pcfg_resolved(d["Parent"])
    b.update(dict((k, json.loads(json.dumps(v))) for k, v in d.items() if k != "Parent"))
    return b


_s4c = az_json(az_path("pcfg", "Projectile_Config_Arrow_Shortbow_Strength_4"))
assert _s4c["Parent"] == "Projectile_Config_Arrow_Shortbow" and all(k in _s4c for k in ("Physics", "Interactions", "LaunchForce", "Model")), sorted(_s4c)
BOW_PCFG = pcfg_resolved("Projectile_Config_Arrow_Shortbow_Strength_4")
assert BOW_PCFG["Model"] == "Arrow_Crude" and "Parent" not in BOW_PCFG and BOW_PCFG["LaunchForce"] == 85, BOW_PCFG
_bow_vanilla_cfg = json.loads(json.dumps(BOW_PCFG))
BOW_PCFG["Model"] = BOW_LEAP
put(P_PCFG % BOW_LEAP, BOW_PCFG)
BOW_MODEL = json.loads(json.dumps(_vam))           # Arrow_Crude, its own vanilla trails (the shot looks exactly vanilla)
put(P_MODEL % BOW_LEAP, BOW_MODEL)
# ---- (2) THE BLAST ARROW: the vanilla legacy Arrow_FullCharge resolved, our flight + damage (ArmoryTuneSys scales the hit to the bow)
VARROW = resolve("prj", "Arrow_FullCharge")
assert VARROW["Appearance"] == "Arrow_Crude" and VARROW["Damage"] == 20 and VARROW["TimeToLive"] == 20 and "HitParticles" in VARROW, VARROW
BLAST_DMG = VARROW["Damage"]
_bl = json.loads(json.dumps(VARROW))
_bl.pop("Parent", None)
_bl["MuzzleVelocity"] = BLAST_SPEED
_bl["TerminalVelocity"] = max(BLAST_SPEED, VARROW["TerminalVelocity"])
_bl["TimeToLive"] = BLAST_TTL
_bl["DeathParticles"] = json.loads(json.dumps(VARROW["HitParticles"]))      # (the blast itself is drawn by the Java)
assert not az_has("prj", BOW_BLAST)
PRJS[BOW_BLAST] = _bl
put(P_PRJ % BOW_BLAST, _bl)
for _i in (BOW_LEAP, BOW_BLAST, PS_RING2, PS_HEAL2, PS_BURST2):
    assert not az_has("pcfg", _i) and not az_has("model", _i) and not az_has("prj", _i) and _i not in _IDX["psys"], _i

# ---- (3) PARTICLE LIFE (Skyy: "it leaves partials behind", "the blue balls stay"): every point system gets a system LifeSpan and short particles


def _plmax(sp):
    pl = sp.get("ParticleLifeSpan")
    assert isinstance(pl, dict), sp
    return max(float(pl.get("Min", 0.0)), float(pl.get("Max", 0.0)))


def finite_spawner(sp, emit, fade):
    sp = json.loads(json.dumps(sp))
    pl = sp["ParticleLifeSpan"]
    sp["ParticleLifeSpan"] = dict((k, (round(min(float(v), fade), 4) if k in ("Min", "Max") else v)) for k, v in pl.items())
    if isinstance(sp.get("LifeSpan"), (int, float)):
        sp["LifeSpan"] = min(float(sp["LifeSpan"]), emit)
    return sp


def endless(sysd, spawners):
    """True = this system never stops by itself (no system LifeSpan and a spawner that emits for ever: no TotalParticles / LifeSpan)"""
    if isinstance(sysd.get("LifeSpan"), (int, float)) and sysd["LifeSpan"] > 0:
        return False
    return any(spawners[e["SpawnerId"]].get("TotalParticles") is None and spawners[e["SpawnerId"]].get("LifeSpan") is None for e in sysd["Spawners"])


FX_BUDGET = {}      # system id -> (emit, fade, vanish = LifeSpan + the longest particle)
FX_FILES = []


def finite_system(sid, sysd, spawners, kind, rename, start_scale=1.0, in_place=False):
    emit, fade = FX_LIFE[kind]
    d = json.loads(json.dumps(sysd))
    d["LifeSpan"] = emit
    worst = 0.0
    for e in d["Spawners"]:
        old = e["SpawnerId"]
        new = rename(old)
        if "StartDelay" in e:
            e["StartDelay"] = round(min(float(e["StartDelay"]) * start_scale, emit * 0.6), 4)
        sp = finite_spawner(spawners[old], emit, fade)
        worst = max(worst, _plmax(sp))
        if in_place:
            assert new == old and (P_PSPAWN % new) in ASSETS, new
            ASSETS[P_PSPAWN % new] = jdump(sp)
        elif (P_PSPAWN % new) not in ASSETS:
            put(P_PSPAWN % new, sp)
            FX_FILES.append(P_PSPAWN % new)
        e["SpawnerId"] = new
    if in_place:
        ASSETS[P_PSYS % sid] = jdump(d)
    else:
        put(P_PSYS % sid, d)
        FX_FILES.append(P_PSYS % sid)
    FX_BUDGET[sid] = (emit, fade, emit + worst)
    assert emit + worst <= emit + fade + 1e-9, (sid, emit, worst)
    return d


def ours(path):
    return json.loads(ASSETS[path])


def vanilla_sp(sid):
    return json.loads(AZ.read(_IDX["pspawn"][sid][0]).decode("utf-8-sig"))


def vanilla_sys(sid):
    return json.loads(AZ.read(_IDX["psys"][sid][0]).decode("utf-8-sig"))


# the WHY, kept as a build fact: the sources were endless at a point
_got = vanilla_sys("GreenOrbTrail")
assert endless(_got, dict((e["SpawnerId"], vanilla_sp(e["SpawnerId"])) for e in _got["Spawners"])), "GreenOrbTrail stops by itself now - re-check"
assert vanilla_sys("Totem_Heal_Simple_Test").get("LifeSpan") == 9
_old_trail = ours(P_PSYS % PS_TRAIL)
_old_rope = ours(P_PSYS % GDOT)
assert endless(_old_trail, dict((e["SpawnerId"], ours(P_PSPAWN % e["SpawnerId"])) for e in _old_trail["Spawners"]))
assert endless(_old_rope, dict((e["SpawnerId"], ours(P_PSPAWN % e["SpawnerId"])) for e in _old_rope["Spawners"]))
# the blink light + the rope dots: our own files, fixed in place
finite_system(PS_TRAIL, _old_trail, dict((e["SpawnerId"], ours(P_PSPAWN % e["SpawnerId"])) for e in _old_trail["Spawners"]), "trail", lambda x: x, in_place=True)
finite_system(GDOT, _old_rope, dict((e["SpawnerId"], ours(P_PSPAWN % e["SpawnerId"])) for e in _old_rope["Spawners"]), "rope", lambda x: x, in_place=True)
# the heal orb's ring: a copy of the blue glow (the quick orb keeps riding the endless original - it dies with the orb)
_glow = ours(P_PSYS % PS_GLOW)
finite_system(PS_RING2, _glow, dict((e["SpawnerId"], ours(P_PSPAWN % e["SpawnerId"])) for e in _glow["Spawners"]), "ring",
              lambda x: x.replace("SkyyArmory_Orb_", "SkyyArmory_Ring_"))
# the heal pulse (was Totem_Heal_Simple_Test: 9 s per pulse, one pulse a second) and the burst (Explosion_Small): copies
_tot = vanilla_sys(PS_HEAL)
finite_system(PS_HEAL2, _tot, dict((e["SpawnerId"], vanilla_sp(e["SpawnerId"])) for e in _tot["Spawners"]), "heal",
              lambda x: "SkyyArmory_Heal_" + x.replace("Totem_Heal_", ""), start_scale=0.2)
_exs = vanilla_sys(PS_BURST)
finite_system(PS_BURST2, _exs, dict((e["SpawnerId"], vanilla_sp(e["SpawnerId"])) for e in _exs["Spawners"]), "burst",
              lambda x: "SkyyArmory_Burst_" + x.replace("Explosion_Small_", ""))
PS_RING, PS_HEAL, PS_BURST = PS_RING2, PS_HEAL2, PS_BURST2          # the Java spawns the finite copies from here on
FX_POINT = [PS_TRAIL, PS_RING, PS_HEAL, PS_BURST, GDOT]
_attached = set()
for _p, _t in ASSETS.items():
    if _p.startswith("Server/Models/") and isinstance(_t, str):
        for _pp in json.loads(_t).get("Particles") or []:
            _attached.add(_pp.get("SystemId"))
for _p, _d in PRJS.items():
    for _k in ("HitParticles", "DeathParticles"):
        if _k in _d:
            _attached.add(_d[_k]["SystemId"] + "@hit")
assert not (_attached & set(FX_POINT)), "a finite point system rides a model (its LifeSpan would cut that look): %s" % (_attached & set(FX_POINT))
for _sid in FX_POINT:
    _d = ours(P_PSYS % _sid)
    _sps = [ours(P_PSPAWN % e["SpawnerId"]) for e in _d["Spawners"]]
    assert _d["LifeSpan"] == FX_BUDGET[_sid][0] and not endless(_d, dict((e["SpawnerId"], ours(P_PSPAWN % e["SpawnerId"])) for e in _d["Spawners"]))
    assert max(_plmax(x) for x in _sps) <= FX_BUDGET[_sid][1] + 1e-9, _sid
    for _x in _sps:
        _tx = (_x.get("Particle") or {}).get("Texture")
        assert not _tx or ("Common/" + _tx) in AZ_SET, (_sid, _tx)
assert FX_BUDGET[GDOT][2] <= 0.3 + 1e-9 and FX_BUDGET[PS_TRAIL][2] <= 0.5 + 1e-9 and FX_BUDGET[PS_BURST][2] <= 1.0 + 1e-9, FX_BUDGET
assert az_has("sound", SND_BURST)
# the grapple bolt's flight trail: the vanilla Arrow trail's length again (0.1.2 doubled it to 40)
_gtj = json.loads(ASSETS[P_TRAIL % GTRAIL])
_gtj["LifeSpan"] = _vtr["LifeSpan"]
ASSETS[P_TRAIL % GTRAIL] = jdump(_gtj)

# ---- (4) THE CROSSBOWS (Skyy: "Copper + Onyxium (Recommended)"): the vanilla Iron crossbow + the tier numbers + build-time recoloured art
P_XITEM = "Server/Item/Items/Weapon/Crossbow/%s.json"
TEX_XBOW = "Items/Weapons/Crossbow/SkyyArmory_%s_Texture.png"
ICON_XBOW = "Icons/ItemsGenerated/SkyyArmory_Crossbow_%s.png"
VXI = az_get("item", "Weapon_Crossbow_Iron")
_vxiv = VXI["InteractionVars"]


def _xd(iv, k):
    return iv[k]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Projectile"]


assert VXI["Parent"] == "Template_Weapon_Crossbow" and (_xd(_vxiv, "Standard_Projectile_Damage"), _xd(_vxiv, "Combo_Projectile_Damage"),
       _xd(_vxiv, "Signature_BigArrow_Damage"), VXI["MaxDurability"]) == (10, 27, 78, 120), "the vanilla Iron crossbow changed"
assert "Interactions" not in VXI and "Weapon" not in VXI, "the Iron crossbow names its own interactions / Weapon now - re-check the copy"
_vxt = az_get("item", "Template_Weapon_Crossbow")
_vreload = _vxt["InteractionVars"]["Reload_Effects"]
assert az_get("int", "Common_StatAmmoReload_Effects")["RunTime"] == 0.3 and _vreload["Interactions"][0]["Parent"] == "Common_StatAmmoReload_Effects"
assert abs(XSTAT["Copper"]["std"] - 10 / 1.25) <= 0.5 and abs(XSTAT["Copper"]["combo"] - 27 / 1.25) <= 0.5 and abs(XSTAT["Copper"]["sig"] - 78 / 1.25) <= 0.5
assert XSTAT["Copper"]["dur"] < 120 and XSTAT["Copper"]["reload"] > 0.3, "Copper sits below Iron"
# the step pattern from More Crossbow Tiers (pack mod, read only): Mithril x 1.25 = Onyxium
MCT_NOTE = "More Crossbow Tiers not found - the Onyxium numbers are the baked Mithril 25 / 68 / 195 / 220 x 1.25"
for _f in (sorted(os.listdir(B.MODS_DIR)) if os.path.isdir(B.MODS_DIR) else []):
    if not (_f.startswith("More_Crossbow_Tiers") and _f.endswith(".zip")):
        continue
    with zipfile.ZipFile(os.path.join(B.MODS_DIR, _f)) as _mz:
        _mm = json.loads(_mz.read("manifest.json").decode("utf-8-sig"))
        if (_mm.get("Group"), _mm.get("Name")) != ("Serj", "More Crossbow Tiers"):
            continue
        _mi = json.loads(_mz.read("Server/Item/Items/Weapon_Crossbow_Mithril.json").decode("utf-8-sig"))
        _ma = json.loads(_mz.read("Server/Item/Items/Weapon_Crossbow_Adamantite.json").decode("utf-8-sig"))
        _mt = (_xd(_mi["InteractionVars"], "Standard_Projectile_Damage"), _xd(_mi["InteractionVars"], "Combo_Projectile_Damage"),
               _xd(_mi["InteractionVars"], "Signature_BigArrow_Damage"), _mi["MaxDurability"])
        _at = (_xd(_ma["InteractionVars"], "Standard_Projectile_Damage"), _xd(_ma["InteractionVars"], "Combo_Projectile_Damage"),
               _xd(_ma["InteractionVars"], "Signature_BigArrow_Damage"), _ma["MaxDurability"])
        assert _mt == (25, 68, 195, 220) and _at == (20, 54, 156, 180), (_mt, _at)
        MCT_NOTE = "More Crossbow Tiers %s: Adamantite %s -> Mithril %s (x1.25)" % (_f, _at, _mt)
        break
assert (XSTAT["Onyxium"]["std"], XSTAT["Onyxium"]["combo"], XSTAT["Onyxium"]["sig"]) == (int(25 * 1.25), int(round(68 * 1.25)), int(round(195 * 1.25 + 0.01)))
assert XSTAT["Onyxium"]["dur"] == 220 + 40
_XWOOD = ("Handle", "Handle2", "Main", "Main2", "L-Wood-Side", "R-Wood-Side", "L-String", "R-String")
_XMETAL = ("Stud-Back", "Stud-Mid", "Stud-Front", "Metal-Top", "Trigger", "Trigger2", "Bow-Mid", "Bow-L", "Bow-L2", "Bow-R", "Bow-R2")
_xd0, _xmodel, _xtex, _xicon = SA.item_parts(AZ, "Server/Item/Items/Weapon/Crossbow/Weapon_Crossbow_Iron.json")
assert sorted(SA.node_names(_xmodel)) == sorted(_XWOOD + _XMETAL), SA.node_names(_xmodel)


def _grey(c, lim=0.2):
    mx = max(c[:3])
    return mx > 1e-6 and (mx - min(c[:3])) / mx < lim


def icon_mask(img):
    """the metal pixels: every grey pixel bright enough not to be a dark rim (the Iron crossbow's metal - limbs, plates, the studs painted
    on the stock - is neutral grey; its wood, strings and fletching are coloured). The same rule for the texture and the icon."""
    return sorted((x, y) for y in range(img.h) for x in range(img.w)
                  if img.get(x, y)[3] >= 1 and _grey(img.get(x, y)) and SA.luma(img.get(x, y)) >= 24.0)


XART = {}
_ximg, _iimg = SA._img(_xtex), SA._img(_xicon)
_xall = icon_mask(_ximg)
_xin = set((x, y) for x, y, _ri in SA._region_points(_ximg, SA.node_rects(_xmodel, _XMETAL), 1))
assert len([p for p in _xall if p in _xin]) > 0.8 * len(_xall), "most grey texels must sit on the metal nodes"
# 0.1.3 fixer (art critic): the texture also holds the bolt sprite (grey arrow head + fletching strip) outside the metal nodes - keep it vanilla:
# only grey texels INSIDE the metal nodes' UV boxes are recoloured (the icon is a flat render: its mask stays the grey rule)
_xmask = [p for p in _xall if p in _xin]
XOUT = len(_xall) - len(_xmask)
assert XOUT > 0, "the bolt-sprite grey texels the critic saw are gone - re-check the mask"
_imask = icon_mask(_iimg)
assert len(_xmask) > 400 and len(_imask) > 150, (len(_xmask), len(_imask))
for _m, _xid in XBOWS:
    _g = SA.metal_gradient(AZ, _m)
    _tu = SA._tuned(_m, "head")
    _kw = dict(lo=_tu["lo"], hi=_tu["hi"], rank=_tu["rank"])
    _tx = SA.recolor(_xtex, _g, [(x, y, x + 1, y + 1) for x, y in _xmask], **_kw)
    _ic = SA.recolor(_xicon, _g, [(x, y, x + 1, y + 1) for x, y in _imask], **_kw)
    assert _tx == SA.recolor(_xtex, _g, [(x, y, x + 1, y + 1) for x, y in _xmask], **_kw), "the crossbow art must be deterministic"
    for _src, _new, _mk in ((_ximg, SA._img(_tx), set(_xmask)), (_iimg, SA._img(_ic), set(_imask))):
        assert (_src.w, _src.h) == (_new.w, _new.h)
        _chg = [(x, y) for y in range(_src.h) for x in range(_src.w) if _src.get(x, y) != _new.get(x, y)]
        assert len(_chg) > 0.6 * len(_mk) and all(p in _mk for p in _chg), (_m, len(_chg), len(_mk))
        assert all(_src.get(x, y)[3] == _new.get(x, y)[3] for y in range(_src.h) for x in range(_src.w)), "alpha kept"
    XART[_m] = (_tx, _ic)
    ASSETS["Common/" + TEX_XBOW % _m] = _tx
    ASSETS["Common/" + ICON_XBOW % _m] = _ic
assert XART["Copper"][0] != XART["Onyxium"][0] and XART["Copper"][0] != _xtex


def xbow_recipe(m):
    if m == "Copper":       # the Copper shortbow's materials at the Iron crossbow's bench (no tier) - 6 bars like every crossbow
        return {"TimeSeconds": 3, "KnowledgeRequired": False,
                "Input": [{"ItemId": "Ingredient_Bar_Copper", "Quantity": 6}, {"ResourceTypeId": "Wood_Trunk", "Quantity": 4},
                          {"ItemId": "Ingredient_Fibre", "Quantity": 6}],
                "BenchRequirement": [{"Type": "Crafting", "Categories": ["Weapon_Bow"], "Id": "Weapon_Bench"}]}
    # Onyxium: Onyxium bars have no world source in 0.6 (QUESTION for Skyy) - the top Mithril recipe, more of it, at the tier-3 bench
    return {"TimeSeconds": 5, "KnowledgeRequired": False,
            "Input": [{"ItemId": "Ingredient_Bar_Mithril", "Quantity": 10}, {"ItemId": "Ingredient_Voidheart", "Quantity": 2},
                      {"ItemId": "Ingredient_Leather_Storm", "Quantity": 3}],
            "BenchRequirement": [{"Type": "Crafting", "Categories": ["Weapon_Bow"], "Id": "Weapon_Bench", "RequiredTierLevel": 3}]}


_vx_bench = [b for b in VXI["Recipe"]["BenchRequirement"] if b.get("Id") not in DROP_BENCH]
assert _vx_bench == [{"Type": "Crafting", "Categories": ["Weapon_Bow"], "Id": "Weapon_Bench"}], _vx_bench
assert az_get("item", "Weapon_Shortbow_Mithril")["Recipe"]["BenchRequirement"][0].get("RequiredTierLevel") == 3
XLANG = []
XBOW_IDS = [x for _m, x in XBOWS]
for _m, _xid in XBOWS:
    assert _xid.startswith("Weapon_Crossbow_") and "crossbow" in _xid.lower() and "skyy" not in _xid.lower() and _m in _xid.split("_"), _xid
    assert not az_has("item", _xid) and (_xid + "_Recipe_Generated_0") not in _vrecipe_ids and _xid not in _salvage_in, _xid
    _sw = resolve("item", "Weapon_Sword_" + _m)
    _st = XSTAT[_m]
    _it = json.loads(json.dumps(VXI))
    _it["TranslationProperties"] = {"Name": "server.items.%s.name" % _xid}
    _it["Texture"] = TEX_XBOW % _m
    _it["Icon"] = ICON_XBOW % _m
    _it["Quality"], _it["ItemLevel"] = _sw["Quality"], _sw["ItemLevel"]
    _it["MaxDurability"] = _st["dur"]
    _iv = _it["InteractionVars"]
    for _k, _v in (("Standard_Projectile_Damage", "std"), ("Combo_Projectile_Damage", "combo"), ("Signature_BigArrow_Damage", "sig")):
        _iv[_k]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Projectile"] = _st[_v]
    if _st["reload"] != 0.3:
        _rl = json.loads(json.dumps(_vreload))
        _rl["Interactions"][0]["RunTime"] = _st["reload"]
        _iv["Reload_Effects"] = _rl
    _it["Recipe"] = xbow_recipe(_m)
    for _x in _it["Recipe"]["Input"]:
        assert (_x.get("ItemId") is None or az_has("item", _x["ItemId"])) and (_x.get("ResourceTypeId") is None or az_has("rtype", _x["ResourceTypeId"])), _x
    ITEMS[_xid] = _it
    put(P_XITEM % _xid, _it)
    XLANG.append("items.%s.name = %s Crossbow" % (_xid, _m))
assert [(m, ITEMS[x]["Quality"], ITEMS[x]["ItemLevel"]) for m, x in XBOWS] == [("Copper", "Common", 10), ("Onyxium", "Epic", 50)]
for _l in XLANG:
    assert ("\n" + _l.split(" = ")[0] + " ") not in _vlang, "vanilla already has " + _l.split(" = ")[0]
ASSETS[P_LANG] = ASSETS[P_LANG] + "\n".join(XLANG) + "\n"
L_FILES = [P_BOW_INT % BOW_INT, P_PCFG % BOW_LEAP, P_MODEL % BOW_LEAP, P_PRJ % BOW_BLAST] + FX_FILES + [P_XITEM % x for x in XBOW_IDS] \
    + ["Common/" + TEX_XBOW % m for m, _x in XBOWS] + ["Common/" + ICON_XBOW % m for m, _x in XBOWS]
assert all(p in ASSETS for p in L_FILES)
# reference closure of the 0.1.3 files
_lbad = []
_lbad += [] if az_has("int", INTS[BOW_INT]["Parent"]) else ["bow parent"]
_lbad += [x for x in (BOW_PCFG["LaunchWorldSoundEventId"], BOW_PCFG["LaunchLocalSoundEventId"]) if not az_has("sound", x)]
_lbad += [t["TrailId"] for t in BOW_MODEL["Trails"] if not az_has("trail", t["TrailId"])]
_lbad += [] if az_has("model", _bl["Appearance"]) else ["blast model"]
_lbad += [x["SystemId"] for x in (_bl["HitParticles"], _bl["DeathParticles"]) if x["SystemId"] not in _IDX["psys"] and (P_PSYS % x["SystemId"]) not in ASSETS]
_lbad += [x for x in (_bl.get("HitSoundEventId"), _bl.get("MissSoundEventId")) if x and not az_has("sound", x)]
for _xid in XBOW_IDS:
    for _f in ("Icon", "Texture", "Model"):
        if ("Common/" + ITEMS[_xid][_f]) not in AZ_SET and ("Common/" + ITEMS[_xid][_f]) not in ASSETS:
            _lbad.append("%s %s" % (_xid, _f))
    for _k, _v in ITEMS[_xid]["InteractionVars"].items():
        for _e in _v["Interactions"]:
            if isinstance(_e, dict) and _e.get("Parent") and not az_has("int", _e["Parent"]):
                _lbad.append("%s %s parent %s" % (_xid, _k, _e["Parent"]))
    _lbad += [] if az_has("quality", ITEMS[_xid]["Quality"]) else ["%s quality" % _xid]
assert not _lbad, "0.1.3 reference closure: %s" % _lbad
print("0.1.3 bow leap: %s -> config %s (vanilla Strength_4, our model id), reaches %d shortbows (%s); not reached (own chains): %s" % (
    BOW_INT, BOW_LEAP, len(BOW_REACH), ", ".join(BOW_REACH), ", ".join(BOW_OTHER)))
print("0.1.3 blast arrow %s: %d b/s, %s s, full-draw damage table %s (unknown bow %d)" % (BOW_BLAST, BLAST_SPEED, BLAST_TTL, BOW_TABLE, BOW_DEF))
print("0.1.3 particle life (emit / fade / vanish s): %s" % ", ".join("%s %s/%s/%s" % (k, v[0], v[1], round(v[2], 3)) for k, v in sorted(FX_BUDGET.items())))
print("0.1.3 crossbows: bolt-sprite grey texels kept vanilla %d; %s; %s; metal texels %d (texture) / %d (icon)" % (XOUT,
    "; ".join("%s = %s %d %s/%s/%s dur %s reload %s s" % (x, ITEMS[x]["Quality"], ITEMS[x]["ItemLevel"], XSTAT[m]["std"], XSTAT[m]["combo"], XSTAT[m]["sig"],
              XSTAT[m]["dur"], XSTAT[m]["reload"]) for m, x in XBOWS), MCT_NOTE, len(_xmask), len(_imask)))
'''
rep('''assert not _gbad, "grapple reference closure: %s" % _gbad
''', '''assert not _gbad, "grapple reference closure: %s" % _gbad
''' + L_ASSETS)

rep('print("assets: %d files - %d items (7 wands + 8 staffs), %d interactions,', 'print("assets: %d files - %d items (7 wands + 8 staffs + 2 crossbows), %d interactions,')
# ================================================================================================ JVM: probes (every new engine member)
rep('''PROBED.append("StandardPhysicsTickSystem#tick / ProjectileModule.spawnProjectile / StandardPhysicsProvider.<init> shapes (bytecode)")''',
    '''PROBED.append("StandardPhysicsTickSystem#tick / ProjectileModule.spawnProjectile / StandardPhysicsProvider.<init> shapes (bytecode)")
# ---- 0.1.3: the leap's engine members + the evidence behind the hang path (no slow-fall effect exists; the client's own vertical speed is
# what the server holds; a Set reaches the client as one ChangeVelocity packet) + the particle LifeSpan field the finite systems use
SIGS4 = [(T["XFM"], "getPosition", T["VEC"], []), (T["XFM"], "getDirection", T["VEC"], []), (T["VEL"], "getClientVelocity", T["VEC"], []),
         ("com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSystem", "getLifeSpan", "float", [])]
for _c, _m, _r, _a in SIGS4:
    probe_sig(_c, _m, _r, _a)
assert "setClient" in _ops("com.hypixel.hytale.server.core.modules.entity.player.PlayerInput$SetClientVelocity", "apply"), "the client velocity is no longer the client's"
_pvx = _ops("com.hypixel.hytale.server.core.universe.system.PlayerVelocityInstructionSystem", "tick")
assert "writeNoCache" in _pvx and "clear" in _pvx, "PlayerVelocityInstructionSystem no longer sends each Set at once"
_afx = [str(f.getName()) for f in pool.get("com.hypixel.hytale.protocol.ApplicationEffects").getDeclaredFields()]
_mfx = [str(f.getName()) for f in pool.get("com.hypixel.hytale.protocol.MovementEffects").getDeclaredFields()]
_msx = [str(f.getName()) for f in pool.get("com.hypixel.hytale.protocol.MovementSettings").getDeclaredFields()]
assert not [f for f in _afx + _mfx if "ravity" in f or "fall" in f.lower()], (_afx, _mfx)
assert sorted(f for f in _msx if "ravity" in f) == sorted(["invertedGravity", "wishDirectionGravityX", "wishDirectionGravityY"]), [f for f in _msx if "ravity" in f]
PROBED.append("0.1.3 hang path: no gravity / slow-fall field in ApplicationEffects / MovementEffects (MovementSettings: %s) -> the per-tick Velocity Set; "
              "PlayerInput$SetClientVelocity -> Velocity.setClient (the top check reads the client's own speed)" % ", ".join(f for f in _msx if "ravity" in f))''')

# ================================================================================================ Java tables + classes
rep('''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK)) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) == len(PRJS) and set(QUICK_IDS + ORB_IDS + S_BLINK) == set(PRJS)''',
    '''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST])) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) + 1 == len(PRJS) and set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST]) == set(PRJS)''')
rep('''ROOT_CHECK_IDS = [XROOT] if XROOT_JSON else []      # 0.1.2: the crossbow right click must come from our pack''',
    '''ROOT_CHECK_IDS = [XROOT] if XROOT_JSON else []      # 0.1.2: the crossbow right click must come from our pack
ITEM_CHECK_IDS = sorted(ITEMS)                      # 0.1.3: + the 2 crossbows (ITEMS grew after the closure)
PRJ_CHECK_IDS = sorted(PRJS)                        # 0.1.3: + the blast arrow
INT_CHECK_IDS = sorted(INTS)                        # 0.1.3: + the full-draw override''')
rep('''          "public static final String[] S_BLINK = %s;" % jarr(S_BLINK),''', '''          "public static final String[] S_BLINK = %s;" % jarr(S_BLINK),
          "public static final String BLAST = %s;" % jstr(BOW_BLAST), "public static final int BLAST_CODE = %d;" % BLAST_CODE,''')
rep('''  for (int i = 0; i < S_BLINK.length; i++) m.put(S_BLINK[i], Integer.valueOf(5000 + i));
  PID = m;''', '''  for (int i = 0; i < S_BLINK.length; i++) m.put(S_BLINK[i], Integer.valueOf(5000 + i));
  m.put(BLAST, Integer.valueOf(BLAST_CODE));          // 0.1.3: the bow leap's blast arrow
  PID = m;''')
rep('''gfall = pool.makeClass(PKG + ".GrappleFallSys", pool.get(T["DES"]))
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick,
       gmath, gstate, grap, gimp, gbolt, gfall]''', '''gfall = pool.makeClass(PKG + ".GrappleFallSys", pool.get(T["DES"]))
# 0.1.3 leap (bow full draw + the wand's hang): the per-player record + the glue
lstate = pool.makeClass(PKG + ".LeapState")
leap = pool.makeClass(PKG + ".Leap")
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick,
       gmath, gstate, grap, gimp, gbolt, gfall, lstate, leap]''')

# ================================================================================================ settings: file text, cats, loader
rep('''    "# Wand hop force (13 = the vanilla dagger dash, 0 = no hop).",
    "hop.force=13",''', '''    "# Wand hop force (Skyy 2026-10-06: 30; 13 = the vanilla dagger dash, 0 = no hop).",
    M13_MARK,
    "hop.force=30",''')
rep('''    "# No ground within this many blocks under the spot 3 blocks behind you = half the hop (0 = off).",
    "hop.groundCheck=6",''', '''    "# No ground within this many blocks under the spot 3 blocks behind you = half the hop (0 = off).",
    "hop.groundCheck=6",
] + [x for _r in CFG_LEAP if _r[2] == "hop" for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [''')
rep('''] + [x for _r in CFG_GRAPPLE for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
    "",
    "# ---- Mana check (server log)",''', '''] + [x for _r in CFG_GRAPPLE for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
    "",
    "# ---- bow leap (a shortbow's full draw; Skyy 2026-10-06: Wynncraft-like - back, hang at the top, blast arrow)",
] + [x for _r in CFG_LEAP if _r[2] == "bow" for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
    "",
    "# ---- Mana check (server log)",''')
rep('''CFG_CATS = [("trav", "Traversal"), ("blink", "Staff blink"), ("hop", "Wand hop + burst"), ("grapple", "Crossbow grapple"), ("damage", "Damage"),''',
    '''CFG_CATS = [("trav", "Traversal"), ("blink", "Staff blink"), ("hop", "Wand hop + burst"), ("grapple", "Crossbow grapple"), ("bow", "Bow leap + blast"),
            ("damage", "Damage"),''')
rep('''          "public static volatile String GRAPPLE_TEXT = \\"\\";",''', '''          "public static volatile String GRAPPLE_TEXT = \\"\\";",
          "public static volatile String LEAP_TEXT = \\"\\";",''')
_ll = []
for _r in L_ROWS:
    k, t, d, lo, hi, fld = _r[0], _r[3], _r[4], _r[5], _r[6], _r[11]
    if t == "bool":
        _ll.append('  %s = bool(c.getProperty("%s"), %s);' % (fld, k, d))
    elif t == "int":
        _ll.append('  %s = intOf(c.getProperty("%s"), %s, %s, %s);' % (fld, k, d, lo, hi))
    elif t == "dec":
        _ll.append('  %s = dec(c.getProperty("%s"), %r, %r, %r);' % (fld, k, float(d), float(lo), float(hi)))
    else:
        raise SystemExit("leap row type %s" % t)
L_LOADER = "\n".join(_ll)
assert "%" not in L_LOADER
rep('''  HOP_FORCE = dec(c.getProperty("hop.force"), 13.0, 0.0, 25.0);''', '''  HOP_FORCE = dec(c.getProperty("hop.force"), 30.0, 0.0, 50.0);      // 0.1.3: Skyy "30" (max 25 -> 50)''')
rep('''  GRAPPLE_TEXT = grappleText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:grapple", GRAPPLE_TEXT); } catch (Throwable tg) { }''', '''  GRAPPLE_TEXT = grappleText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:grapple", GRAPPLE_TEXT); } catch (Throwable tg) { }
''' + L_LOADER + '''
  LEAP_TEXT = leapText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:leap", LEAP_TEXT); } catch (Throwable tl) { }''')
rep('''M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''', '''# 0.1.3: the leap's live numbers (bridge armory:leap, the start line)
M(cfg, r"""
public static String leapText() {
  return "wand hold: hop " + HOP_FORCE + (HOP_HANG > 0.0 ? ", hang " + HOP_HANG + " s (drift " + HOP_FALL + " b/s down), then the orb" : ", the orb at the cast (no hang)")
    + " - bow full draw: " + (PART_BOWTRAV && BOW_FORCE > 0.0 ? "leap " + BOW_FORCE + ", hang " + BOW_HANG + " s (drift " + BOW_FALL + " b/s down), then the blast arrow: "
    + BOW_RADIUS + " blocks, " + BOW_PCT + "% to the others - cost " + BOW_STAM + " Stamina + " + BOW_MANA + " Mana" : "OFF (the vanilla arrow)");
}""")
M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''')

# ---- the one-time hop.force update (ArmoryCfg.migrate013 = the migrate012 rules, a decimal value; a hand-set number is kept)
M13_JAVA = r'''
for f in ("public static final String M13_KEY = \"hop.force\";", "public static final String M13_OLD = \"13\";",
          "public static final String M13_NEW = \"30\";", "public static final String M13_MARK = %s;" % jstr(M13_MARK),
          "public static final String M13_MARK_ID = %s;" % jstr(M13_MARK_ID), "public static final String M13_WHO = \"SkyyArmory 0.1.3\";",
          "public static volatile String M13_LAST = \"\";"):
    F(cfg, f)
M(cfg, r"""
public static boolean m13Is(String v, String want) {
  if (v == null) return false;
  try { return Math.abs(Double.parseDouble(v.trim()) - Double.parseDouble(want)) < 1.0E-9; } catch (Throwable t) { return false; }
}""")
# the same text step as m12Update (null = the marker is already there; else { text, change, kept notes, { key, old, new } }); a decimal value
M(cfg, r"""
public static Object[] m13Update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  String eff = null;
  boolean multi = false;
  int first = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(M13_MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    if (M13_KEY.equals(@PKG@.CfgFile.key(s))) {
      if (first < 0) first = k;
      eff = @PKG@.CfgFile.value(l, k).trim();
      multi = e > k;
    }
    k = e + 1;
  }
  boolean mig = eff != null && !multi && m13Is(eff, M13_OLD);
  String chg = "";
  String[] rows = new String[0];
  java.util.ArrayList kept = new java.util.ArrayList();
  if (mig) {
    chg = M13_KEY + " " + @PKG@.CfgRows.oneLine(eff) + " -> " + M13_NEW;
    rows = new String[] { M13_KEY, eff, M13_NEW };
  } else if (eff != null && (multi || !m13Is(eff, M13_NEW))) {
    kept.add(M13_KEY + "=" + @PKG@.CfgRows.oneLine(eff) + " kept (custom) - the 0.1.3 default is " + M13_NEW);
  }
  String nl = text.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
  if (first < 0) {
    String out0 = (text.length() == 0 || text.endsWith("\n")) ? text + M13_MARK + nl : text + nl + M13_MARK;
    return new Object[] { out0, chg, (String[]) kept.toArray(new String[0]), rows };
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (k == first) {
      boolean crm = raw[k].endsWith("\r") || (k == raw.length - 1 && text.indexOf("\r\n") >= 0);
      out.add(M13_MARK + (crm ? "\r" : ""));
    }
    if (mig && e2 == k && M13_KEY.equals(@PKG@.CfgFile.key(s2)) && m13Is(@PKG@.CfgFile.value(l, k).trim(), M13_OLD)) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + M13_NEW + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + M13_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg, (String[]) kept.toArray(new String[0]), rows };
}""")
M(cfg, r"""
public static String m13Log(String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + M13_WHO + "\t-\tupdate\t" + M13_KEY + "\t" + @PKG@.CfgRows.oneLine(o) + "\t" + n + "\tok";
}""")
M(cfg, r"""
public static synchronized String migrate013() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = m13Update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    m12Kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), M13_WHO, "before the 0.1.3 wand hop force update");
    if (!m12Saved(old)) {
      @PKG@.ArmoryLog.warn("config.properties NOT updated to the 0.1.3 wand hop force: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    if (rows.length == 3) {
      @PKG@.CfgLog.enqueue(m13Log(rows[1], rows[2]));
      @PKG@.CfgLog.flush();
    }
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.1.3 wand hop force: " + chg + " (Skyy 2026-10-06; the old file is in config-history; Server Setup -> Changes can undo it)";
    else msg = "config.properties: no hop.force line held the old 13 - nothing changed (0.1.3 hop force marker added)";
    @PKG@.ArmoryLog.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { @PKG@.ArmoryLog.info(kept[i]); all.append("; ").append(kept[i]); }
    M13_LAST = all.toString();
    return M13_LAST;
  } catch (Throwable t) {
    @PKG@.ArmoryLog.warn("could not update config.properties to the 0.1.3 wand hop force (the file is used as it is): " + t);
    return "";
  }
}""")
'''
rep('''M(cfg, r"""
public static double tunePct(boolean staff, int i) {''', M13_JAVA + '''M(cfg, r"""
public static double tunePct(boolean staff, int i) {''')

# ================================================================================================ the Java: TravShot base, TravMath, the Leap
rep('''          "public int count;", "public int code;", "public java.util.UUID caster;", "public String pid;"):''',
    '''          "public int count;", "public int code;", "public java.util.UUID caster;", "public String pid;",
          "public double base;"):          # 0.1.3: the bow's full-draw damage a blast arrow deals (0 = none)''')
rep('''# damage / heal of ONE tick: base x pct % per second x the tick length
M(tmath, r"""''', '''# 0.1.3 THE RHYTHM (pure): the top of a leap - a kept damaging fall = at once (no hang); at most tMax; never before tMin; a hop with no rise
# (looking up / level) = at tMin; else only after the rise was SEEN (the client's speed went up / you rose 0.3) and then the client's
# vertical speed is at most apexVy or you start to come down (0.05 under the best height)
M(tmath, r"""
public static boolean apex(long t, long tMin, long tMax, double vy, double apexVy, boolean rose, double y, double bestY, double hopVy, boolean kept) {
  if (kept) return true;
  if (t >= tMax) return true;
  if (t < tMin) return false;
  if (!(hopVy > 1.0)) return true;
  if (!rose) return false;
  if (!Double.isNaN(vy) && vy <= apexVy) return true;
  if (!Double.isNaN(y) && y < bestY - 0.05) return true;
  return false;
}""")
# the hang's Set: keep x the hop's sideways speed, a slow drift down
M(tmath, r"""
public static double[] hangVec(double hx, double hz, double keep, double fall) {
  double k = keep > 0.0 ? keep : 0.0;
  double f = fall > 0.0 ? fall : 0.0;
  return new double[] { hx * k, 0.0 - f, hz * k };
}""")
# a point particle is started only when its emission (its system LifeSpan) ends inside the effect's life
M(tmath, "public static boolean emitOk(long now, long emitMs, long until) { return now + emitMs <= until; }")
# damage / heal of ONE tick: base x pct % per second x the tick length
M(tmath, r"""''')

# FX timing constants (ArmoryTrav) from the build's FX_LIFE table + the harness seam
rep('''          "public static final boolean HOP_SERVER = %s;" % ("true" if HOP_MODE == "server" else "false")):
    F(trav, f)''', '''          "public static final boolean HOP_SERVER = %s;" % ("true" if HOP_MODE == "server" else "false"),
          "public static final long EMIT_TRAIL_MS = %dL;" % int(round(FX_LIFE["trail"][0] * 1000)),
          "public static final long EMIT_RING_MS = %dL;" % int(round(FX_LIFE["ring"][0] * 1000)),
          "public static final long EMIT_HEAL_MS = %dL;" % int(round(FX_LIFE["heal"][0] * 1000)),
          "public static volatile long BLASTS = 0L;", "public static volatile long BLAST_HITS = 0L;",
          "public static volatile java.util.List PSEEN = null;"):      # HARNESS SEAM ONLY (null in the game): every point particle id + time
    F(trav, f)''')
rep('''public static void particle(String id, double x, double y, double z, @CAC@ acc) {
  if (!@PKG@.ArmoryCfg.TRAV_FX || id == null) return;''', '''public static void particle(String id, double x, double y, double z, @CAC@ acc) {
  if (!@PKG@.ArmoryCfg.TRAV_FX || id == null) return;
  java.util.List seen = PSEEN;
  if (seen != null) seen.add(id);''')

LEAP_JAVA = r'''
# ---------------------------------------------------------------- 0.1.3 THE LEAP (bow full draw + the wand hold's hang; Skyy 2026-10-06)
for f in ("public java.util.UUID u;", "public @REF@ ref;", "public @ST@ st;", "public int kind;", "public String pid;", "public int code;",
          "public String item;", "public double base;", "public long t0;", "public int phase;", "public long hangUntil;", "public long hangMs;",
          "public double fall;", "public double hx;", "public double hz;", "public double hopVy;", "public boolean kept;", "public boolean rose;",
          "public double y0;", "public double bestY;", "public double dx;", "public double dy;", "public double dz;", "public int ticks;",
          "public int hangTicks;"):
    F(lstate, f)
C(lstate, r"""
public LeapState(java.util.UUID u, @REF@ ref, @ST@ st, int kind, String pid, int code, String item, double base, long t0) {
  this.u = u;
  this.ref = ref;
  this.st = st;
  this.kind = kind;
  this.pid = pid;
  this.code = code;
  this.item = item;
  this.base = base;
  this.t0 = t0;
  this.phase = 1;
  this.hangUntil = 0L;
  this.hangMs = 0L;
  this.kept = false;
  this.rose = false;
  this.y0 = 0.0;
  this.bestY = -1.0E9;
  this.ticks = 0;
  this.hangTicks = 0;
}""")
for f in ("public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile long LEAPS = 0L;", "public static volatile long FIRES = 0L;", "public static volatile long HANG_TICKS = 0L;",
          "public static volatile long REFUSED = 0L;", "public static volatile long NOSHOT = 0L;", "public static volatile long SWEPT = 0L;",
          "public static volatile String LAST_WHY = \"\";", "public static volatile int SWEEP_N = 0;", "public static final int SWEEP_EVERY = 300;",
          "public static volatile java.util.Map HAND = null;",      # HARNESS SEAM ONLY (null in the game = InventoryComponent.getItemInHand)
          "public static volatile java.util.Map LOOK = null;",      # HARNESS SEAM ONLY (null in the game = TargetUtil.getLook): uuid -> double[6]
          "public static final String ARROW = %s;" % jstr(BOW_LEAP), "public static final String BLAST = %s;" % jstr(BOW_BLAST),
          "public static final int BLAST_CODE = %d;" % BLAST_CODE, "public static final double BLAST_DMG = %r;" % float(BLAST_DMG),
          "public static final long RISE_MIN = %dL;" % int(round(LEAP_RISE_MIN * 1000)), "public static final long RISE_MAX = %dL;" % int(round(LEAP_RISE_MAX * 1000)),
          "public static final double APEX_VY = %r;" % float(LEAP_APEX_VY), "public static final double KEEP = %r;" % float(LEAP_KEEP),
          "public static final long MAX_AGE = %dL;" % int(round((LEAP_RISE_MAX + 1.5 + 2.0) * 1000)),
          "public static final String[] BOW_IDS = %s;" % jarr([b for b, d in BOW_TABLE]), "public static final int[] BOW_DMG = %s;" % jints([d for b, d in BOW_TABLE]),
          "public static final int BOW_DEF = %d;" % BOW_DEF, "public static final String SND_SHOT = %s;" % jstr(SND_GLAUNCH)):
    F(leap, f)
M(leap, r"""public static void warn(String key, String msg) { @PKG@.ArmoryLog.warnOnce("leap:" + key, msg); }""")
M(leap, r"""
public static java.util.UUID uuidOf(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @PR@.getComponentType());
    return o instanceof @PR@ ? ((@PR@) o).getUuid() : null;
  } catch (Throwable t) { return null; }
}""")
M(leap, r"""
public static boolean mounted(@CAC@ acc, @REF@ r) {
  try { return acc.getComponent(r, @MNT@.getComponentType()) != null; } catch (Throwable t) { return false; }
}""")
M(leap, r"""
public static @REF@ refOf(@CB@ buf, java.util.UUID u) {
  try {
    if (u == null) return null;
    @REF@ r = ((@ES@) buf.getExternalData()).getRefFromUUID(u);
    return (r != null && r.isValid()) ? r : null;
  } catch (Throwable t) { return null; }
}""")
M(leap, r"""
public static String hand(@CAC@ acc, @REF@ r, java.util.UUID u) {
  java.util.Map h = HAND;
  if (h != null) {
    Object o = h.get(u);
    return o == null ? null : String.valueOf(o);
  }
  return @PKG@.ArmoryTrav.handItem(acc, r);
}""")
# one Velocity Set: the hop with the dagger dash's config (the 0.1.1 hop feel), the hang without one (the grapple pull's per-tick Set)
M(leap, r"""
public static boolean vel(@CAC@ acc, @REF@ r, double x, double y, double z, boolean dash) {
  try {
    if (r == null || !r.isValid()) return false;
    Object o = acc.getComponent(r, @VEL@.getComponentType());
    if (!(o instanceof @VEL@)) return false;
    @VCF@ cf = null;
    if (dash) cf = @PKG@.ArmoryTrav.dash();
    ((@VEL@) o).addInstruction(new @VEC@(x, y, z), cf, @CVT@.Set);
    return true;
  } catch (Throwable t) { warn("vel", "a leap velocity failed (" + t + ")"); return false; }
}""")
M(leap, r"""
public static double clientVy(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @VEL@.getComponentType());
    if (o instanceof @VEL@) {
      @VEC@ cv = ((@VEL@) o).getClientVelocity();
      if (cv != null) return cv.y;
    }
  } catch (Throwable t) { }
  return Double.NaN;
}""")
# the bow's cost (server, live rows): 1 = paid (or not readable - never blocks), 0 = too little (nothing taken); Mana only with a Mana pool
M(leap, r"""
public static int take(@CAC@ acc, @REF@ r, double stam, double mana) {
  try {
    Object o = acc.getComponent(r, @ESM@.getComponentType());
    if (!(o instanceof @ESM@)) return 1;
    @ESM@ m = (@ESM@) o;
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
  } catch (Throwable t) { warn("cost", "the bow leap cost could not be read (" + t + ") - the leap goes on free"); return 1; }
}""")
M(leap, r"""
public static int bowDamage(String item) {
  if (item == null) return BOW_DEF;
  for (int i = 0; i < BOW_IDS.length; i++) if (BOW_IDS[i].equals(item)) return BOW_DMG[i];
  return BOW_DEF;
}""")
M(leap, r"""
public static boolean isBow(String item) {
  if (item == null) return false;
  String l = item.toLowerCase();
  return l.indexOf("bow") >= 0 && l.indexOf("crossbow") < 0;
}""")
# where the shot leaves and goes: the eye + the head direction NOW (TargetUtil.getLook - what LaunchProjectileInteraction aims with), else
# the feet + 1.6 and the given direction
M(leap, r"""
public static double[] aim(@CB@ buf, @REF@ r, java.util.UUID u, double[] dflt) {
  java.util.Map lm = LOOK;
  if (lm != null) {
    Object o = lm.get(u);
    if (o instanceof double[]) return (double[]) o;
  }
  try {
    @XFM@ lk = @TU@.getLook(r, buf);
    if (lk != null && lk.getPosition() != null) {
      double[] d = @PKG@.ArmoryTrav.unit(lk.getDirection());
      @VEC@ e = lk.getPosition();
      if (d != null) return new double[] { e.x, e.y, e.z, d[0], d[1], d[2] };
    }
  } catch (Throwable t) { }
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, r);
  if (p == null || dflt == null) return null;
  return new double[] { p.x, p.y + 1.6, p.z, dflt[0], dflt[1], dflt[2] };
}""")
# THE SHOT at the end of the hang: the wand's own orb / the bow's blast arrow, launched like LaunchProjectileInteraction (ArmoryTrav.spawn,
# creator = the player) where they look now; marked in TravWorld.pend so its SPAWN is recognised (no second leap) and carries the damage
M(leap, r"""
public static void fire(@PKG@.LeapState s, @ST@ st, @CB@ buf, String why) {
  if (s == null) return;
  STATES.remove(s.u, s);
  if (s.st != st || s.ref == null || !s.ref.isValid()) { NOSHOT = NOSHOT + 1L; LAST_WHY = "no shot (" + why + ")"; return; }
  double[] a = aim(buf, s.ref, s.u, new double[] { s.dx, s.dy, s.dz });
  if (a == null) { NOSHOT = NOSHOT + 1L; LAST_WHY = "no shot - no aim (" + why + ")"; return; }
  double x = a[0] + a[3] * 0.5;
  double y = a[1] + a[4] * 0.5;
  double z = a[2] + a[5] * 0.5;
  @REF@ nr = @PKG@.ArmoryTrav.spawn(buf, s.pid, x, y, z, a[3], a[4], a[5], s.u);
  if (nr == null) { NOSHOT = NOSHOT + 1L; LAST_WHY = "the shot could not be launched (" + why + ")"; return; }
  @PKG@.TravWorld tw = @PKG@.TravWorld.get(st);
  @PKG@.TravShot ts = new @PKG@.TravShot(x, y, z, 0.0, s.code, s.u, s.pid);
  ts.base = s.base;
  tw.pend.put(nr, ts);
  if (s.kind == 2) @PKG@.ArmoryTrav.sound(SND_SHOT, x, y, z, buf);
  FIRES = FIRES + 1L;
  LAST_WHY = "fired - " + why;
}""")
# the hop at the cast (the wand hop's maths: opposite to the look, the dagger dash, half without ground behind, a damaging fall KEPT)
M(leap, r"""
public static double[] hopNow(@CB@ buf, @REF@ r, double[] dir, double force) {
  @VEC@ pos = @PKG@.ArmoryTrav.posOf(buf, r);
  @WLD@ w = @PKG@.ArmoryTrav.worldOf(buf);
  if (pos == null || dir == null || !(force > 0.0)) return null;
  double[] pb = @PKG@.TravMath.hopProbe(dir[0], dir[2]);
  boolean ground = @PKG@.TravMath.ground(@PKG@.ArmoryTrav.grid(w), pos.x + pb[0], pos.y, pos.z + pb[1], @PKG@.ArmoryCfg.HOP_GROUND);
  double[] hv = @PKG@.TravMath.hopVector(dir[0], dir[1], dir[2], force, !ground);
  double cvy = clientVy(buf, r);
  double vy = @PKG@.TravMath.hopVy(hv[1], cvy, @PKG@.ArmoryTrav.maxFall(w));
  if (!vel(buf, r, hv[0], vy, hv[2], true)) return null;
  return new double[] { hv[0], vy, hv[2], vy != hv[1] ? 1.0 : 0.0, ground ? 1.0 : 0.0 };
}""")
M(leap, r"""
public static @PKG@.LeapState begin(int kind, java.util.UUID u, @REF@ r, @ST@ st, @CB@ buf, String pid, int code, String item, double base,
                                     double[] dir, double force, double hangS, double fall) {
  @PKG@.LeapState old = (@PKG@.LeapState) STATES.get(u);
  if (old != null) fire(old, st, buf, "a new leap");          // the older leap's shot goes at once (never lost)
  long now = System.currentTimeMillis();
  @PKG@.LeapState s = new @PKG@.LeapState(u, r, st, kind, pid, code, item, base, now);
  s.dx = dir[0];
  s.dy = dir[1];
  s.dz = dir[2];
  s.hangMs = Math.round(hangS * 1000.0);
  if (s.hangMs < 0L) s.hangMs = 0L;
  s.fall = fall;
  double[] h = hopNow(buf, r, dir, force);
  if (h != null) { s.hx = h[0]; s.hz = h[2]; s.hopVy = h[1]; s.kept = h[3] > 0.5; }
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, r);
  if (p != null) { s.y0 = p.y; s.bestY = p.y; }
  STATES.put(u, s);
  LEAPS = LEAPS + 1L;
  LAST_WHY = (kind == 2 ? "bow leap" : "wand leap") + (h == null ? " (no hop)" : (s.kept ? " (falling - kept)" : ""));
  return s;
}""")
# WAND (ArmoryTrav.added, a wand charged orb's SPAWN, hop.hangSeconds > 0): the class lock + the traversal Stamina first - refused = false (the
# 0.1.2 way: the orb flies, the hop job refuses the same way); else the orb is removed now and fired again at the end of the hang
M(leap, r"""
public static boolean onWandOrb(@REF@ orb, @LPC@ pc, int c, @ST@ st, @CB@ buf) {
  java.util.UUID u = pc.getCreatorUuid();
  @REF@ r = refOf(buf, u);
  int i = c % 1000;
  if (r == null || i < 0 || i >= @PKG@.ArmoryDefs.W_IDS.length) return false;
  if (@PKG@.ArmoryTrav.dead(buf, r) || mounted(buf, r)) return false;
  String item = hand(buf, r, u);
  if (!@PKG@.ArmoryTrav.allowed(u, @PKG@.ArmoryDefs.W_IDS[i]) || !@PKG@.ArmoryTrav.allowed(u, item)) { REFUSED = REFUSED + 1L; LAST_WHY = "wand: class lock"; return false; }
  double[] d = @PKG@.ArmoryTrav.unit(@PKG@.ArmorySpawn.launchVelocity(pc.getSimplePhysicsProvider()));
  if (d == null) d = @PKG@.ArmoryTrav.look(buf, u);
  if (d == null) return false;
  double cost = @PKG@.TravMath.staminaCost((double) @PKG@.ArmoryDefs.W_C[i], @PKG@.ArmoryCfg.STAMINA_PCT, @PKG@.ArmoryCfg.STAMINA_CAP);
  if (@PKG@.ArmoryTrav.takeStamina(buf, r, cost) == 0) { REFUSED = REFUSED + 1L; LAST_WHY = "wand: too little Stamina"; return false; }
  buf.removeEntity(orb, @REMR@.REMOVE);
  begin(1, u, r, st, buf, pc.getProjectileAssetName(), c, item, 0.0, d, @PKG@.ArmoryCfg.HOP_FORCE, @PKG@.ArmoryCfg.HOP_HANG, @PKG@.ArmoryCfg.HOP_FALL);
  @PKG@.ArmoryTrav.HOPS = @PKG@.ArmoryTrav.HOPS + 1L;
  return true;
}""")
# BOW (GrappleBoltSys, the full-draw arrow's SPAWN - our model id): part.bowtrav, a bow in hand, the class lock (Archer), the bow costs -
# anything refused = the arrow is LEFT ALONE (the vanilla full-draw shot); else it is removed now and the leap runs
M(leap, r"""
public static void onBowShot(@REF@ arrow, @SPPV@ sp, @ST@ st, @CB@ buf) {
  if (arrow == null || sp == null) return;
  if (!@PKG@.ArmoryCfg.PART_BOWTRAV || !(@PKG@.ArmoryCfg.BOW_FORCE > 0.0)) { LAST_WHY = "bow leap off (vanilla arrow)"; return; }
  java.util.UUID u = sp.getCreatorUuid();
  @REF@ r = refOf(buf, u);
  if (r == null) return;
  String item = hand(buf, r, u);
  if (!isBow(item)) { LAST_WHY = "not a bow (vanilla arrow)"; return; }
  if (!@PKG@.ArmoryTrav.allowed(u, item)) { REFUSED = REFUSED + 1L; LAST_WHY = "bow: class lock (vanilla arrow)"; return; }
  if (@PKG@.ArmoryTrav.dead(buf, r) || mounted(buf, r)) { LAST_WHY = "bow: dead or mounted (vanilla arrow)"; return; }
  double[] a = aim(buf, r, u, null);
  double[] d = a == null ? @PKG@.ArmoryTrav.look(buf, u) : new double[] { a[3], a[4], a[5] };
  if (d == null) { LAST_WHY = "bow: no look (vanilla arrow)"; return; }
  if (take(buf, r, @PKG@.ArmoryCfg.BOW_STAM, @PKG@.ArmoryCfg.BOW_MANA) == 0) {
    REFUSED = REFUSED + 1L;
    LAST_WHY = "bow: too little Stamina or Mana (vanilla arrow)";
    try {
      Object po = buf.getComponent(r, @PR@.getComponentType());
      if (po instanceof @PR@) @PKG@.ArmoryTrav.tell((@PR@) po, "Not enough Stamina or Mana to leap - " + @PKG@.TravMath.fmt(@PKG@.ArmoryCfg.BOW_STAM) + " Stamina + " + @PKG@.TravMath.fmt(@PKG@.ArmoryCfg.BOW_MANA) + " Mana needed. A normal shot.");
    } catch (Throwable t) { }
    return;
  }
  buf.removeEntity(arrow, @REMR@.REMOVE);
  begin(2, u, r, st, buf, BLAST, BLAST_CODE, item, (double) bowDamage(item), d, @PKG@.ArmoryCfg.BOW_FORCE, @PKG@.ArmoryCfg.BOW_HANG, @PKG@.ArmoryCfg.BOW_FALL);
}""")
# records whose player is gone (disconnect) or that are far too old are dropped (no shot)
M(leap, r"""
public static void sweep(long now) {
  java.util.Iterator it = STATES.values().iterator();
  while (it.hasNext()) {
    @PKG@.LeapState s = (@PKG@.LeapState) it.next();
    boolean gone = false;
    try { gone = s.ref == null || !s.ref.isValid() || now - s.t0 > MAX_AGE; } catch (Throwable t) { gone = true; }
    if (gone) { it.remove(); SWEPT = SWEPT + 1L; }
  }
}""")
# TravTick -> once per player per world tick: the world / body / death / mount checks, RISE -> HANG (a Set every tick) -> FIRE
M(leap, r"""
public static void tickPlayer(@REF@ r, @ST@ st, @CB@ buf) {
  if (r == null || STATES.isEmpty()) return;
  SWEEP_N = SWEEP_N + 1;
  if (SWEEP_N >= SWEEP_EVERY) {
    SWEEP_N = 0;
    try { sweep(System.currentTimeMillis()); } catch (Throwable ts) { warn("sweep", "the leap sweep failed (" + ts + ")"); }
  }
  java.util.UUID u = uuidOf(buf, r);
  if (u == null) return;
  @PKG@.LeapState s = (@PKG@.LeapState) STATES.get(u);
  if (s == null) return;
  long now = System.currentTimeMillis();
  if (s.st != st) { STATES.remove(u, s); NOSHOT = NOSHOT + 1L; LAST_WHY = "left the world (no shot)"; return; }
  if (s.ref == null || !s.ref.equals(r)) { STATES.remove(u, s); NOSHOT = NOSHOT + 1L; LAST_WHY = "a new body (no shot)"; return; }
  if (@PKG@.ArmoryTrav.dead(buf, r)) { STATES.remove(u, s); NOSHOT = NOSHOT + 1L; LAST_WHY = "died (no shot)"; return; }
  if (mounted(buf, r)) { fire(s, st, buf, "mounted"); return; }
  s.ticks = s.ticks + 1;
  double cvy = clientVy(buf, r);
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, r);
  if (s.phase == 1) {
    double y = Double.NaN;
    if (p != null) {
      y = p.y;
      if (p.y > s.bestY) s.bestY = p.y;
      if (p.y > s.y0 + 0.3) s.rose = true;
    }
    if (!Double.isNaN(cvy) && cvy > 1.0) s.rose = true;
    if (!@PKG@.TravMath.apex(now - s.t0, RISE_MIN, RISE_MAX, cvy, APEX_VY, s.rose, y, s.bestY, s.hopVy, s.kept)) return;
    if (s.kept) { fire(s, st, buf, "falling - no hang (fall kept)"); return; }
    if (s.hangMs <= 0L) { fire(s, st, buf, "the top"); return; }
    s.phase = 2;
    s.hangUntil = now + s.hangMs;
  }
  if (s.phase == 2) {
    if (!Double.isNaN(cvy) && cvy < 0.0 - @PKG@.ArmoryTrav.maxFall(@PKG@.ArmoryTrav.worldOf(buf))) { fire(s, st, buf, "falling - hang ended"); return; }
    if (now >= s.hangUntil) { fire(s, st, buf, "after the hang"); return; }
    double[] hv = @PKG@.TravMath.hangVec(s.hx, s.hz, KEEP, s.fall);
    if (vel(buf, r, hv[0], hv[1], hv[2], false)) { s.hangTicks = s.hangTicks + 1; HANG_TICKS = HANG_TICKS + 1L; }
  }
}""")
M(leap, r"""
public static double blastBase(@ST@ st, @REF@ proj) {
  try {
    @PKG@.TravWorld tw = @PKG@.TravWorld.of(st);
    if (tw == null || proj == null) return 0.0;
    @PKG@.TravShot s = (@PKG@.TravShot) tw.orbs.get(proj);
    return s == null ? 0.0 : s.base;
  } catch (Throwable t) { return 0.0; }
}""")
'''
rep('''# ---- ArmoryTravSys.onEntityAdded (SPAWN of one of our projectiles): quick orbs -> range / pierce record; wand charged orb -> burst''',
    LEAP_JAVA + '''# ---- ArmoryTravSys.onEntityAdded (SPAWN of one of our projectiles): quick orbs -> range / pierce record; wand charged orb -> burst''')

# ---- ArmoryTrav.added: the leap's own re-fired orb, the wand leap, the blast arrow
rep('''  if (c >= 2000 && c < 3000) {
    tw.orbs.put(ref, new @PKG@.TravShot(p == null ? 0.0 : p.x, p == null ? 0.0 : p.y, p == null ? 0.0 : p.z, 0.0, c, cu, pid));
    if (!@PKG@.ArmoryCfg.PART_TRAV || cu == null || !HOP_SERVER) return;''', '''  if (c >= 2000 && c < 3000) {
    @PKG@.TravShot lp = (@PKG@.TravShot) tw.pend.remove(ref);          // 0.1.3: the orb a leap fired at the end of its hang (no new leap)
    if (lp == null && @PKG@.ArmoryCfg.PART_TRAV && cu != null && HOP_SERVER && @PKG@.ArmoryCfg.HOP_HANG > 0.0 && @PKG@.ArmoryCfg.HOP_FORCE > 0.0
        && @PKG@.Leap.onWandOrb(ref, pc, c, st, buf)) return;           // 0.1.3: hop -> hang -> THEN the orb (Skyy 2026-10-06)
    tw.orbs.put(ref, new @PKG@.TravShot(p == null ? 0.0 : p.x, p == null ? 0.0 : p.y, p == null ? 0.0 : p.z, 0.0, c, cu, pid));
    if (lp != null) return;
    if (!@PKG@.ArmoryCfg.PART_TRAV || cu == null || !HOP_SERVER) return;''')
rep('''  if (c >= 5000 && c < 6000) {
    @VEC@ v = @PKG@.ArmorySpawn.launchVelocity(pc.getSimplePhysicsProvider());''', '''  if (c >= 6000 && c < 7000) {          // 0.1.3: the bow leap's blast arrow (its damage = the bow's full draw, from the leap)
    @PKG@.TravShot lb = (@PKG@.TravShot) tw.pend.remove(ref);
    @PKG@.TravShot sb = new @PKG@.TravShot(p == null ? 0.0 : p.x, p == null ? 0.0 : p.y, p == null ? 0.0 : p.z, 0.0, c, cu, pid);
    sb.base = lb != null && lb.base > 0.0 ? lb.base : (double) @PKG@.Leap.BOW_DEF;
    tw.orbs.put(ref, sb);
    return;
  }
  if (c >= 5000 && c < 6000) {
    @VEC@ v = @PKG@.ArmorySpawn.launchVelocity(pc.getSimplePhysicsProvider());''')
# ---- the blast (before landed): every OTHER enemy within bow.blastRadius takes bow.blastPercent % of the bow's full-draw damage
rep('''M(trav, r"""
public static double[] hitAt(@DMG@ d, @CB@ buf, @REF@ tg) {''', '''M(trav, r"""
public static void blast(@ST@ st, @CB@ buf, @REF@ proj, @PKG@.TravShot s, double cx, double cy, double cz, @REF@ direct) {
  if (s == null || !@PKG@.ArmoryCfg.PART_BOWTRAV) return;
  @REF@ caster = null;
  try { caster = s.caster == null ? null : ((@ES@) buf.getExternalData()).getRefFromUUID(s.caster); } catch (Throwable t0) { caster = null; }
  boolean pvp = pvp(worldOf(buf));
  BLASTS = BLASTS + 1L;
  if (@PKG@.ArmoryCfg.BOW_PCT > 0 && s.base > 0.0 && caster != null && caster.isValid() && @PKG@.ArmoryCfg.BOW_RADIUS > 0.0) {
    double amt = s.base * (double) @PKG@.ArmoryCfg.BOW_PCT / 100.0;
    java.util.List l = near(buf, cx, cy, cz, @PKG@.ArmoryCfg.BOW_RADIUS);
    for (int k = 0; k < l.size(); k++) {
      @REF@ r = (@REF@) l.get(k);
      if (r == null || (direct != null && r.equals(direct))) continue;
      if (kind(buf, r, caster, s.caster, pvp) != 0) continue;
      if (hit(buf, r, caster, proj, amt)) BLAST_HITS = BLAST_HITS + 1L;
    }
  }
  particle(PS_BURST, cx, cy, cz, buf);
  sound(SND_BURST, cx, cy, cz, buf);
}""")
M(trav, r"""
public static double[] hitAt(@DMG@ d, @CB@ buf, @REF@ tg) {''')
rep('''  @PKG@.TravWorld tw = @PKG@.TravWorld.of(st);
  if (tw == null || tg == null) return;
  if (c >= 2000 && c < 3000) {''', '''  @PKG@.TravWorld tw = @PKG@.TravWorld.of(st);
  if (tw == null || tg == null) return;
  if (c >= 6000 && c < 7000) {          // 0.1.3: the blast arrow's direct hit -> the blast around it (once)
    @PKG@.TravShot sb = (@PKG@.TravShot) tw.orbs.get(pj);
    if (sb == null || sb.count > 0) return;
    sb.count = 1;
    double[] hb = hitAt(d, buf, tg);
    if (hb != null) blast(st, buf, pj, sb, hb[0], hb[1], hb[2], tg);
    return;
  }
  if (c >= 2000 && c < 3000) {''')
rep('''  @PKG@.TravShot s = (@PKG@.TravShot) tw.orbs.remove(ref);
  if (s == null || s.count > 0 || !removeReason || !@PKG@.ArmoryCfg.PART_TRAV) { forget(st, tw); return; }''', '''  @PKG@.TravShot s = (@PKG@.TravShot) tw.orbs.remove(ref);
  if (s != null && s.code >= 6000 && s.code < 7000) {          // 0.1.3: a blast arrow that hit no one blasts where it ended
    if (s.count == 0 && removeReason) {
      @VEC@ pb = posOf(buf, ref);
      if (pb == null) pb = posOf(st, ref);
      if (pb != null) { s.count = 1; blast(st, buf, null, s, pb.x, pb.y, pb.z, null); }
    }
    forget(st, tw);
    return;
  }
  if (s == null || s.count > 0 || !removeReason || !@PKG@.ArmoryCfg.PART_TRAV) { forget(st, tw); return; }''')
# ---- the particle emission rule (never start a point particle whose emission outlives its effect)
rep('''    f.ticks = f.ticks + 1;
    particle(PS_HEAL, f.ax, f.ay, f.az, buf);''', '''    f.ticks = f.ticks + 1;
    if (@PKG@.TravMath.emitOk(now, EMIT_HEAL_MS, f.until)) particle(PS_HEAL, f.ax, f.ay, f.az, buf);     // 0.1.3: never past the orb's end''')
rep('''    if (f.kind != 0 && now >= f.fxNext) {
      f.fxNext = now + (f.kind == 1 ? 250L : 500L);''', '''    if (f.kind != 0 && now >= f.fxNext && @PKG@.TravMath.emitOk(now, f.kind == 1 ? @PKG@.ArmoryTrav.EMIT_TRAIL_MS : @PKG@.ArmoryTrav.EMIT_RING_MS, f.until)) {
      f.fxNext = now + (f.kind == 1 ? @PKG@.ArmoryTrav.EMIT_TRAIL_MS : @PKG@.ArmoryTrav.EMIT_RING_MS);      // 0.1.3: = the systems' LifeSpan''')

# ---- the systems: the bow shot in GrappleBoltSys, the leap tick in TravTick, the blast arrow's damage in ArmoryTuneSys, its hit in ArmoryHitSys
rep('''    @MDL@ m = ((@MODC@) mc).getModel();
    if (m == null || !@PKG@.Grapple.BOLT.equals(m.getModelAssetId())) return;''', '''    @MDL@ m = ((@MODC@) mc).getModel();
    if (m == null) return;
    if (@PKG@.Leap.ARROW.equals(m.getModelAssetId())) {          // 0.1.3: a shortbow's full-draw arrow -> the bow leap (or left alone)
      Object bs = buf.getComponent(ref, @SPPV@.getComponentType());
      if (bs instanceof @SPPV@) @PKG@.Leap.onBowShot(ref, (@SPPV@) bs, st, buf);
      return;
    }
    if (!@PKG@.Grapple.BOLT.equals(m.getModelAssetId())) return;''')
rep('''  if (chunk != null) {          // 0.1.2: the crossbow grapple, per player (world thread)
    try { @PKG@.Grapple.tickPlayer(chunk.getReferenceTo(idx), store, cb); }
    catch (Throwable tg) { @PKG@.Grapple.warn("tick:" + tg.getClass().getName(), "grapple tick failed (" + tg + ")"); }
  }''', '''  if (chunk != null) {          // 0.1.2: the crossbow grapple, per player (world thread)
    try { @PKG@.Grapple.tickPlayer(chunk.getReferenceTo(idx), store, cb); }
    catch (Throwable tg) { @PKG@.Grapple.warn("tick:" + tg.getClass().getName(), "grapple tick failed (" + tg + ")"); }
    try { @PKG@.Leap.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.3: the leap's rise / hang / shot
    catch (Throwable tl) { @PKG@.Leap.warn("tick:" + tl.getClass().getName(), "leap tick failed (" + tl + ")"); }
  }''')
rep('''    int c = @PKG@.ArmoryDefs.pidCode(@PKG@.ArmoryTrav.pidOf(buf, pj));
    if (c < 1000 || c >= 3000) return;''', '''    int c = @PKG@.ArmoryDefs.pidCode(@PKG@.ArmoryTrav.pidOf(buf, pj));
    if (c < 1000 || (c >= 3000 && c < 6000) || c >= 7000) return;          // 0.1.3: + the blast arrow (6000)''')
rep('''public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@)) return;
    if (!@PKG@.ArmoryCfg.PART_TUNE) {   // 0.1.1: the pierce rule holds with the tune off too''', '''public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@)) return;
    @DMG@ db = (@DMG@) ev;            // 0.1.3: a blast arrow's own hit deals the bow's full-draw damage (any earlier factor kept; our blast hits untouched)
    if (!db.isCancelled() && db.getSource() instanceof @DPRJ@ && !@PKG@.ArmoryTrav.MINE.containsKey(db)) {
      @REF@ bp = ((@DPRJ@) db.getSource()).getProjectile();
      String bpid = pidOf(buf, bp);
      if (bpid != null && @PKG@.ArmoryDefs.pidCode(bpid) == @PKG@.ArmoryDefs.BLAST_CODE) {
        double bb = @PKG@.Leap.blastBase(st, bp);
        if (bb > 0.0) db.setAmount((float) ((double) db.getAmount() * bb / @PKG@.Leap.BLAST_DMG));
        return;
      }
    }
    if (!@PKG@.ArmoryCfg.PART_TUNE) {   // 0.1.1: the pierce rule holds with the tune off too''')

# ================================================================================================ plugin: bridge, migration, log, shutdown
rep('''BRIDGE_KEYS = ["armory:wands", "armory:staffs", "armory:quick", "armory:fn:info", "armory:check", "gear:loot:add:SkyyArmory", "armory:trav",
               "armory:grapple"]''', '''BRIDGE_KEYS = ["armory:wands", "armory:staffs", "armory:quick", "armory:fn:info", "armory:check", "gear:loot:add:SkyyArmory", "armory:trav",
               "armory:grapple", "armory:leap"]''')
rep('''  b.put("armory:grapple", @PKG@.ArmoryCfg.GRAPPLE_TEXT);
}""")''', '''  b.put("armory:grapple", @PKG@.ArmoryCfg.GRAPPLE_TEXT);
  b.put("armory:leap", @PKG@.ArmoryCfg.LEAP_TEXT);
}""")''')
rep('''  String m12 = @PKG@.ArmoryCfg.migrate012();          // 0.1.2: a trav.staminaCap line still at 10 becomes 5 ONCE (History copy first), before the loader
  @PKG@.ArmoryCfg.load();''', '''  String m12 = @PKG@.ArmoryCfg.migrate012();          // 0.1.2: a trav.staminaCap line still at 10 becomes 5 ONCE (History copy first), before the loader
  String m13 = @PKG@.ArmoryCfg.migrate013();          // 0.1.3: a hop.force line still at 13 becomes 30 ONCE (same rules)
  @PKG@.ArmoryCfg.load();''')
rep('''  @PKG@.Grapple.LASTEND.clear();
  systems();''', '''  @PKG@.Grapple.LASTEND.clear();
  @PKG@.Leap.STATES.clear();
  systems();''')
rep('''(m12.length() > 0 ? "; " + m12 : ""));''', '''(m12.length() > 0 ? "; " + m12 : ""));
  @PKG@.ArmoryLog.info("@VERSION@ leap: " + @PKG@.ArmoryCfg.LEAP_TEXT + (m13.length() > 0 ? "; " + m13 : ""));''')
rep('''  @PKG@.Grapple.STATES.clear();
  @PKG@.Grapple.GRACE.clear();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''', '''  @PKG@.Grapple.STATES.clear();
  @PKG@.Grapple.GRACE.clear();
  @PKG@.Leap.STATES.clear();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''')
rep('''                 "Crossbow right click = the grapple bolt (shoot, pull, let go; hooks mobs). "''',
    '''                 "Crossbow right click = the grapple bolt (shoot, pull, let go; hooks mobs). Shortbow full draw = leap back, hang, blast arrow; "
                 "the wand hold hangs too. Copper + Onyxium crossbows. "''')
rep('''      len(GINTS), ("the root override " + XROOT) if XROOT_JSON else "no root override", len(G_FILES), len(CFG_GRAPPLE), M12_MARK_ID))''',
    '''      len(GINTS), ("the root override " + XROOT) if XROOT_JSON else "no root override", len(G_FILES), len(CFG_GRAPPLE), M12_MARK_ID))
print("0.1.3 leap: rise %s-%s s (top: client vy <= %s after the rise), hang keep %s, %d rows, hop.force default 30 (one-time update marker %r); "
      "%d files; crossbows %s" % (LEAP_RISE_MIN, LEAP_RISE_MAX, LEAP_APEX_VY, LEAP_KEEP, len(CFG_LEAP), M13_MARK_ID, len(L_FILES), ", ".join(XBOW_IDS)))''')

assert s.count("registerSystem(") == SYS0, "0.1.3 registers no new system (the bow shot rides GrappleBoltSys, the leap TravTick)"
for _bad in ("\"hop.force=13\"", 'dec(c.getProperty("hop.force"), 13.0'):
    assert _bad not in s, _bad
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))

# ================================================================================================ the harness: 0.1.2's checks (patched for 0.1.3) + the new sections
HARNESS_P10 = r'''# ============================================================================================================ P10. 0.1.3 assets (bow leap, blast, particle life, crossbows)
BOW_INT, BOW_LEAP, BOW_BLAST = "Weapon_Shortbow_Primary_Shoot_Strength_4", "SkyyArmory_Bow_Leap", "SkyyArmory_Bow_Blast"
_vb4 = aj("int", BOW_INT)
check(XINT[BOW_INT] == dict(_vb4, Config=BOW_LEAP) and X_PATHS[BOW_INT] == AIDX["int"][BOW_INT] == "Server/Item/Interactions/Weapons/Shortbow/Primary/Shoot/%s.json" % BOW_INT,
      "P10 (bow leap): the full-draw release = the vanilla %s at its own path with ONE change: Config -> %s: %s" % (BOW_INT, BOW_LEAP, XINT[BOW_INT]))
_tsb = aj("item", "Template_Weapon_Shortbow")
check(_tsb["InteractionVars"]["Primary_Shoot_Strength_4"]["Interactions"][0]["Parent"] == BOW_INT
      and aj("int", "Weapon_Shortbow_Primary_Shoot_Charge")["Next"]["1.2"]["Next"]["DefaultValue"]["Interactions"] == [BOW_INT],
      "P10: every template shortbow's 1.2 s full charge reaches that one interaction (the template var + the Charging default)")


def _pcres(base):
    d_ = az_json_by_base("Server/ProjectileConfigs/", base)
    if not d_.get("Parent"):
        return copy.deepcopy(d_)
    b_ = _pcres(d_["Parent"])
    b_.update(copy.deepcopy(dict((k, v) for k, v in d_.items() if k != "Parent")))
    return b_


_lc = J[J_PCFG[BOW_LEAP]]
_vlc = _pcres("Projectile_Config_Arrow_Shortbow_Strength_4")
check(_lc == dict(_vlc, Model=BOW_LEAP) and _vlc["Model"] == "Arrow_Crude" and "Primary_Shoot_Damage_Strength_4" in json.dumps(_lc["Interactions"]),
      "P10: the leap config = the vanilla Strength_4 config fully resolved, only Model = our id (a refused leap = the vanilla full-draw arrow with its own damage var)")
check(J[J_MODELS[BOW_LEAP]] == aj("model", "Arrow_Crude"), "P10: the leap arrow's model = Arrow_Crude (the shot looks vanilla)")
_vbl = aresolve("prj", "Arrow_FullCharge")
_bl = XPRJ[BOW_BLAST]
check(dict((k, v) for k, v in _bl.items() if k not in ("MuzzleVelocity", "TerminalVelocity", "TimeToLive", "DeathParticles"))
      == dict((k, v) for k, v in _vbl.items() if k not in ("MuzzleVelocity", "TerminalVelocity", "TimeToLive", "Parent"))
      and _bl["Damage"] == 20 and _bl["MuzzleVelocity"] == 60 and _bl["TimeToLive"] == 4.0 and _bl["DeathParticles"] == _vbl["HitParticles"]
      and not [w for w in ("Block", "Explosion") if w in json.dumps(_bl)],
      "P10: the blast arrow = the vanilla legacy Arrow_FullCharge (Damage 20, scaled to the bow at the hit) with 60 b/s, 4 s, no block damage: %s" % _bl)
FXP = {"SkyyArmory_Trail_Light": (0.25, 0.25), "SkyyArmory_Ring_Blue": (0.5, 0.25), "SkyyArmory_Heal_Pulse": (0.5, 0.3), "SkyyArmory_Burst": (0.3, 0.7),
       "SkyyArmory_Rope_Dot": (0.15, 0.15)}
_fxbad, _fxv = [], {}
for _sid, (_em, _fd) in FXP.items():
    _d = J[J_PSYS[_sid]]
    _pl = []
    for _e in _d["Spawners"]:
        _sp = J.get(J_PSP.get(_e["SpawnerId"], "?"))
        if _sp is None:
            _fxbad.append("%s: spawner %s not in the jar" % (_sid, _e["SpawnerId"]))
            continue
        _pl.append(max(float(_sp["ParticleLifeSpan"].get("Min", 0)), float(_sp["ParticleLifeSpan"].get("Max", 0))))
    _fxv[_sid] = round(_d.get("LifeSpan", 99) + max(_pl or [99]), 3)
    if _d.get("LifeSpan") != _em or max(_pl or [99]) > _fd + 1e-9:
        _fxbad.append("%s: LifeSpan %s, longest particle %s" % (_sid, _d.get("LifeSpan"), max(_pl or [99])))
_models_ps = set(p_.get("SystemId") for m_ in J_MODELS.values() for p_ in (J[m_].get("Particles") or []))
check(not _fxbad and not (_models_ps & set(FXP)) and _fxv["SkyyArmory_Rope_Dot"] <= 0.3 and _fxv["SkyyArmory_Trail_Light"] <= 0.5 and _fxv["SkyyArmory_Burst"] <= 1.0,
      "P10 (Skyy: 'it leaves partials behind', 'the blue balls stay'): every point particle system has a system LifeSpan = its re-draw interval and "
      "short particles - gone this long after its last draw (s): %s; none rides a model: %s" % (_fxv, _fxbad))
_vgot = aj("psys", "GreenOrbTrail")
check(not _vgot.get("LifeSpan") and all(aj("pspawn", e_["SpawnerId"]).get("TotalParticles") is None for e_ in _vgot["Spawners"])
      and aj("psys", "Totem_Heal_Simple_Test").get("LifeSpan") == 9 and "SkyyArmory_Orb_Glow_Blue" in _models_ps,
      "P10 (the cause, kept as a fact): the vanilla GreenOrbTrail (the base of the rope dots, the blink light and the blue ring) emits for ever (no LifeSpan, "
      "no TotalParticles - it is built to ride a projectile); the totem heal lives 9 s; the quick orb still rides the endless blue glow (it dies with the orb)")
VXI = aj("item", "Weapon_Crossbow_Iron")
_XMETALT = ("Stud-Back", "Stud-Mid", "Stud-Front", "Metal-Top", "Trigger", "Trigger2", "Bow-Mid", "Bow-L", "Bow-L2", "Bow-R", "Bow-R2")
XST = {"Weapon_Crossbow_Copper_Wynn": ("Copper", 8, 22, 62, 90, 0.375, "Common", 10), "Weapon_Crossbow_Onyxium_Wynn": ("Onyxium", 31, 85, 244, 260, None, "Epic", 50)}


def _xdmg(it, k):
    return it["InteractionVars"][k]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Projectile"]


for _xid, (_m, _sd, _cb, _sg, _du, _rl, _q, _lv) in XST.items():
    _it = XITEM[_xid]
    _diff = sorted(k for k in set(_it) | set(VXI) if _it.get(k) != VXI.get(k))
    _ivd = sorted(k for k in set(_it["InteractionVars"]) | set(VXI["InteractionVars"]) if _it["InteractionVars"].get(k) != VXI["InteractionVars"].get(k))
    check(_diff == sorted(["TranslationProperties", "Texture", "Icon", "Quality", "ItemLevel", "MaxDurability", "Recipe", "InteractionVars"])
          and _ivd == sorted(["Standard_Projectile_Damage", "Combo_Projectile_Damage", "Signature_BigArrow_Damage"] + (["Reload_Effects"] if _rl else []))
          and (_xdmg(_it, "Standard_Projectile_Damage"), _xdmg(_it, "Combo_Projectile_Damage"), _xdmg(_it, "Signature_BigArrow_Damage"), _it["MaxDurability"]) == (_sd, _cb, _sg, _du)
          and (_it["Quality"], _it["ItemLevel"]) == (_q, _lv) and _it["Parent"] == "Template_Weapon_Crossbow" and _it["Model"] == VXI["Model"]
          and (not _rl or _it["InteractionVars"]["Reload_Effects"]["Interactions"][0]["RunTime"] == _rl),
          "P10 (crossbows): %s = the vanilla Iron crossbow (Parent template: same model, interactions, Ammo / reload, the grapple) + %d / %d / %d damage, "
          "durability %d, %s Lv %d%s: %s / %s" % (_xid, _sd, _cb, _sg, _du, _q, _lv, (", reload %s s a bolt" % _rl) if _rl else "", _diff, _ivd))
    _tp, _ip = "Common/" + _it["Texture"], "Common/" + _it["Icon"]
    _vt, _vi = SA._img(AZ.read("Common/" + VXI["Texture"])), SA._img(AZ.read("Common/" + VXI["Icon"]))
    _nt, _ni = SA._img(JZ.read(_tp)), SA._img(JZ.read(_ip))
    _art = []
    for _a, _b in ((_vt, _nt), (_vi, _ni)):
        _ch = [(x, y) for y in range(_a.h) for x in range(_a.w) if _a.get(x, y) != _b.get(x, y)]
        _grey = all((max(_a.get(x, y)[:3]) - min(_a.get(x, y)[:3])) < 0.2 * max(_a.get(x, y)[:3]) for x, y in _ch)
        _art.append(((_a.w, _a.h) == (_b.w, _b.h), len(_ch) > 150, _grey, all(_a.get(x, y)[3] == _b.get(x, y)[3] for x, y in _ch)))
    _xmr = SA.node_rects(SA.item_parts(AZ, "Server/Item/Items/Weapon/Crossbow/Weapon_Crossbow_Iron.json")[1], _XMETALT)
    _xinT = set((x, y) for x, y, _ri in SA._region_points(_vt, _xmr, 1))
    _chT = [(x, y) for y in range(_vt.h) for x in range(_vt.w) if _vt.get(x, y) != _nt.get(x, y)]
    check(len(_chT) > 400 and all(p_ in _xinT for p_ in _chT),
          "P10 (crossbows, fixer): %s - every recoloured TEXTURE texel sits inside a metal node's UV box (the bolt sprite's arrow head / fletching stay vanilla): %d changed, %d outside"
          % (_xid, len(_chT), len([p_ for p_ in _chT if p_ not in _xinT])))
    check(_tp in JSET and _ip in JSET and all(all(t_) for t_ in _art) and "SkyyArmory_" in _tp and "SkyyArmory_" in _ip
          and not [n for n in AZN if n in (_tp, _ip)],
          "P10 (crossbows): %s - the texture + icon are generated into the jar (own paths), only the vanilla GREY (metal) texels recoloured, alpha kept: %s" % (_xid, _art))
    _r = _it["Recipe"]
    _ins = sorted((x_.get("ItemId") or x_.get("ResourceTypeId"), x_["Quantity"]) for x_ in _r["Input"])
    _want = sorted([("Ingredient_Bar_Copper", 6), ("Wood_Trunk", 4), ("Ingredient_Fibre", 6)]) if _m == "Copper" else \
        sorted([("Ingredient_Bar_Mithril", 10), ("Ingredient_Voidheart", 2), ("Ingredient_Leather_Storm", 3)])
    check(_ins == _want and _r["BenchRequirement"][0]["Id"] == "Weapon_Bench" and _r["BenchRequirement"][0]["Categories"] == ["Weapon_Bow"]
          and _r["BenchRequirement"][0].get("RequiredTierLevel") == (3 if _m == "Onyxium" else None) and len(_r["BenchRequirement"]) == 1
          and all(ahas("item", x_["ItemId"]) for x_ in _r["Input"] if "ItemId" in x_) and all(ahas("rtype", x_["ResourceTypeId"]) for x_ in _r["Input"] if "ResourceTypeId" in x_),
          "P10 (crossbows): %s recipe at the Weapon_Bench (Weapon_Bow%s): %s" % (_xid, ", tier 3" if _m == "Onyxium" else "", _ins))
    check(_xid.startswith("Weapon_Crossbow_") and "crossbow" in _xid.lower() and "skyy" not in _xid.lower() and _m in _xid.split("_")
          and not ahas("item", _xid) and ("items.%s.name = %s Crossbow" % (_xid, _m)) in JZ.read("Server/Languages/en-US/server.lang").decode("utf-8"),
          "P10 (crossbows): the id %s - Weapon_Crossbow_ (SkyyClasses Archer, SkyySkills keepLoaded), 'crossbow' (the grapple), the metal word (SkyyGear), "
          "no 'skyy', not a vanilla id; named '%s Crossbow'" % (_xid, _m))
_inst = []
for _f in (sorted(os.listdir(B.MODS_DIR)) if os.path.isdir(B.MODS_DIR) else []):
    if _f.lower().endswith((".zip", ".jar")):
        try:
            with zipfile.ZipFile(os.path.join(B.MODS_DIR, _f)) as _mz:
                _inst += [(_f, n_) for n_ in _mz.namelist() if os.path.basename(n_)[:-5] in XST]
        except Exception:
            pass
check(not _inst, "P10 (crossbows): no installed mod (More Crossbow Tiers, Frah's Crossbow Tiers - it ships Weapon_Crossbow_Onyxium - ...) uses our ids: %s" % _inst[:3])
print("P10. 0.1.3 assets: the full-draw override + leap config + blast arrow, finite point particles %s, crossbows %s" % (_fxv, sorted(XST)))
'''
HARNESS_R = r'''    # ---------------- R13. 0.1.3 THE LEAP (bow + wand), THE BLAST, THE PARTICLE LIFE, THE CROSSBOWS - every new path EXECUTED
    ACfg.useDefaults()
    LP = JClass(PKG + "Leap")
    TM = JClass(PKG + "TravMath")
    ASp_ = JClass(PKG + "ArmorySpawn")
    br.put("party:fn:members", Members())
    TW.ALL.clear()
    LP.STATES.clear()
    LP.HAND = HashMap()
    LP.LOOK = HashMap()
    NOW = lambda: int(SYS_.currentTimeMillis())
    # --- R1. the rhythm maths (pure)
    ap = lambda *a: bool(TM.apex(*a))
    check(not ap(50, 100, 1000, 5.0, 0.5, True, 66.0, 66.0, 10.0, False) and ap(50, 100, 1000, 5.0, 0.5, True, 66.0, 66.0, 10.0, True)
          and ap(1000, 100, 1000, 5.0, 0.5, False, 66.0, 66.0, 10.0, False) and ap(150, 100, 1000, 0.0, 0.5, False, 64.0, 64.0, 0.0, False)
          and not ap(150, 100, 1000, 0.0, 0.5, False, 64.0, 64.0, 10.0, False) and ap(150, 100, 1000, 0.3, 0.5, True, 66.0, 66.0, 10.0, False)
          and ap(150, 100, 1000, 3.0, 0.5, True, 65.9, 66.0, 10.0, False) and not ap(150, 100, 1000, 3.0, 0.5, True, 66.0, 66.0, 10.0, False),
          "R1: the top - never before 0.1 s, a kept fall at once, 1 s at most, no rise expected = at 0.1 s, a rise must be SEEN first (a stale "
          "client speed of 0 never counts), then client vy <= 0.5 or coming down")
    check([round(float(x), 4) for x in TM.hangVec(-30.0, 10.0, 0.2, 1.5)] == [-6.0, -1.5, 2.0] and [round(float(x), 4) for x in TM.hangVec(-30.0, 0.0, -1.0, -2.0)] == [0.0, 0.0, 0.0]
          and bool(TM.emitOk(1000, 250, 1250)) and not bool(TM.emitOk(1001, 250, 1250)),
          "R1: the hang Set = 0.2 x the hop's sideways speed + 1.5 b/s down; a point particle starts only if its emission ends inside its effect")
    # --- R2. rows + defaults (Skyy: hop.force 30) + clamps + armory:leap
    Rows4 = JClass(PKG + "CfgRows")
    ks4 = [str(k) for k in Rows4.KEYS]
    df4 = dict(zip(ks4, [str(d) for d in Rows4.DEFS]))
    want_l = {"hop.force": "30", "hop.hangSeconds": "0.35", "hop.hangFall": "1.5", "part.bowtrav": "true", "bow.hopForce": "30", "bow.hangSeconds": "0.35",
              "bow.hangFall": "1.5", "bow.blastRadius": "4", "bow.blastPercent": "60", "bow.stamina": "3", "bow.mana": "1"}
    bad_l = dict((k, (df4.get(k), v)) for k, v in want_l.items() if df4.get(k) != v)
    check(not bad_l,
          "R2: the leap rows emit with Skyy's / the task's defaults (hop.force 30, hang 0.35 s, bow 30, blast 4 blocks 60 %%, 3 Stamina + 1 Mana): %s" % bad_l)
    check(abs(float(ACfg.HOP_FORCE) - 30.0) < 1e-9 and abs(float(ACfg.HOP_HANG) - 0.35) < 1e-9 and bool(ACfg.PART_BOWTRAV) and abs(float(ACfg.BOW_FORCE) - 30.0) < 1e-9
          and float(ACfg.BOW_STAM) > float(ACfg.BOW_MANA), "R2: the loaded defaults (bows physical: more Stamina than Mana)")
    pr4 = Props()
    for k_, v_ in (("hop.force", "99"), ("bow.hangSeconds", "9"), ("bow.blastPercent", "-5"), ("hop.hangFall", "-1")):
        pr4.setProperty(k_, v_)
    ACfg.apply(pr4)
    cl4 = (float(ACfg.HOP_FORCE), float(ACfg.BOW_HANG), int(ACfg.BOW_PCT), float(ACfg.HOP_FALL))
    ACfg.useDefaults()
    ltxt = str(br.get("armory:leap"))
    check(cl4 == (50.0, 1.5, 0, 0.0) and ltxt.startswith("wand hold: hop 30.0, hang 0.35 s") and "bow full draw: leap 30.0, hang 0.35 s" in ltxt and "4.0 blocks, 60% to the others" in ltxt,
          "R2: the loader clamps like the kit (hop.force 99 -> 50 = the new max, hang 9 -> 1.5, -5 %% -> 0, drift -1 -> 0); armory:leap: %s" % ltxt[:160])
    # --- R3. THE WAND LEAP: orb removed at its SPAWN -> hop 30 with the dash config -> rise -> hang Sets -> the same orb where you look now
    reset_buf()
    TW.ALL.clear()
    AT.GRID = Grid(world_fn())
    AT.NEAR = Near()
    TWd.JOBS.clear()
    put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    vel_r = comp(rc, VELc.getComponentType())
    vel_r.setClient(0.0, 0.0, 0.0)
    mc.setStatValue(STAM, JFloat(10.0))
    mc.setStatValue(MANA, JFloat(200.0))
    n_w0 = last_instr(rc)[3] if last_instr(rc) else 0
    ow1, opw1 = launched(ORB["Iron"], 1301, 0.5, 65.5, 0.5)           # cast looking +x (level)
    AT.added(ow1, opw1, 2002, tst, tbuf)
    sw1 = LP.STATES.get(cu)
    hw1 = last_instr(rc)
    tw = TW.of(tst)
    check(sw1 is not None and int(sw1.kind) == 1 and str(sw1.pid) == ORB["Iron"] and ow1 in list(TBf.REMOVED) and not tw.orbs.containsKey(ow1)
          and not list(TWd.JOBS) and hw1 is not None and hw1[0] == (-30.0, 0.0, 0.0) and hw1[1] == "Set" and hw1[2] == (0.97, 0.94, 5.0, "Exp")
          and sv(mc, STAM) == 5.0 and sv(mc, MANA) == 200.0,
          "R3 (Skyy: hop -> pause at the top -> THEN the orb): an Iron wand's charged orb is removed at its SPAWN (no burst record, no 0.1.2 hop job), the hop "
          "(-30, 0, 0) Set with the dagger dash config (hop.force 30), Stamina 10 -> 5 (15 x 50%% capped 5), the chain's Mana stays spent: %s %s" % (hw1, str(LP.LAST_WHY)))
    n1 = hw1[3]
    LP.tickPlayer(rc, tst, tbuf)
    still = (int(sw1.phase), last_instr(rc)[3] == n1)
    sw1.t0 = NOW() - 150
    LP.tickPlayer(rc, tst, tbuf)
    hh1 = last_instr(rc)
    LP.tickPlayer(rc, tst, tbuf)
    hh2 = last_instr(rc)
    check(still == (1, True) and int(sw1.phase) == 2 and hh1[0] == (-6.0, -1.5, 0.0) and hh1[1] == "Set" and hh1[2] is None and hh2[3] == hh1[3] + 1
          and 300 <= int(sw1.hangUntil) - NOW() <= 400 and int(sw1.hangTicks) == 2,
          "R3: no Set before 0.1 s; a level hop has no rise -> the top at 0.1 s -> the HANG: a Velocity Set EVERY tick (no VelocityConfig = the grapple pull's "
          "path) of 0.2 x the sideways speed + 1.5 b/s down, for hop.hangSeconds 0.35: %s %s" % (hh1, hh2))
    LP.LOOK.put(cu, JArray(JDouble)([0.5, 65.6, 0.5, 0.0, 0.0, 1.0]))         # the player now looks +z
    sw1.hangUntil = NOW() - 1
    reset_buf()
    n_h = last_instr(rc)[3]
    LP.tickPlayer(rc, tst, tbuf)
    add_w = list(TBf.ADDED)
    pcw = None if not add_w else add_w[0][0].getComponent(LPCc.getComponentType())
    lvw = None if pcw is None else ASp_.launchVelocity(pcw.getSimplePhysicsProvider())
    nrw = None if not add_w else add_w[0][1]
    check(LP.STATES.get(cu) is None and len(add_w) == 1 and str(pcw.getProjectileAssetName()) == ORB["Iron"] and str(pcw.getCreatorUuid()) == str(cu)
          and lvw is not None and abs(float(lvw.x())) < 1e-6 and float(lvw.z()) > 1.0 and tw.pend.containsKey(nrw) and last_instr(rc)[3] == n_h
          and str(LP.LAST_WHY) == "fired - after the hang",
          "R3: after the hang the SAME orb (%s) is launched like LaunchProjectileInteraction (creator = you) where you look NOW (+z, the cast was +x), "
          "marked for its SPAWN; no more Sets (normal falling): %s" % (ORB["Iron"], None if lvw is None else (float(lvw.x()), float(lvw.z()))))
    put(nrw, LPCc.getComponentType(), pcw)
    put(nrw, TCc.getComponentType(), TCc(V3(0.5, 65.6, 1.0), R3(0.0, 0.0, 0.0)))
    n_b = last_instr(rc)[3]
    AT.added(nrw, pcw, 2002, tst, tbuf)
    check(tw.orbs.containsKey(nrw) and not tw.pend.containsKey(nrw) and LP.STATES.get(cu) is None and nrw not in list(TBf.REMOVED) and last_instr(rc)[3] == n_b,
          "R3: that orb's SPAWN -> the burst record (no second leap, no second hop)")
    n_dir3, n_near3 = npc(1330, 6.0, 64.0, 5.5), npc(1331, 8.0, 64.0, 5.5)
    NEARL[:] = [n_dir3, n_near3, rp, rs, rc]
    reset_buf()
    d3 = DMGc(DPS(rc, nrw), DCSc.PROJECTILE, JFloat(88.0))
    AT.landed(tst, tbuf, d3, nrw, 2002, n_dir3)
    ev3 = events()
    hfx3 = [tw.fx.get(k_) for k_ in range(tw.fx.size()) if int(tw.fx.get(k_).kind) == 2]
    check(ev3 == [(1331, 52.8, "ProjectileSource", int(nrw.getIndex()))] and len(hfx3) == 1,
          "R3: its hit -> the burst (60%% of 88 to the other enemy) + the heal orb, exactly as 0.1.2: %s (%s, bursts %d, fx %d)" % (ev3, str(AT.LAST_WHY), int(AT.BURSTS), len(hfx3)))
    # looking down: the hop goes UP; the top waits for the rise to be SEEN, then the client's vy <= 0.5
    reset_buf()
    tw.fx.clear()
    mc.setStatValue(STAM, JFloat(10.0))
    ow2, opw2 = launched(ORB["Iron"], 1302, 0.5, 65.5, 0.5, yaw=0.0, pitch=-1.5707964)
    AT.added(ow2, opw2, 2002, tst, tbuf)
    sw2 = LP.STATES.get(cu)
    hw2 = last_instr(rc)
    sw2.t0 = NOW() - 150
    vel_r.setClient(0.0, 0.0, 0.0)
    LP.tickPlayer(rc, tst, tbuf)
    p_a = int(sw2.phase)
    vel_r.setClient(0.0, 8.0, 0.0)
    LP.tickPlayer(rc, tst, tbuf)
    p_b = (int(sw2.phase), bool(sw2.rose))
    vel_r.setClient(0.0, 0.3, 0.0)
    LP.tickPlayer(rc, tst, tbuf)
    p_c = int(sw2.phase)
    vel_r.setClient(0.0, 0.0, 0.0)
    LP.STATES.clear()
    check(hw2 is not None and abs(hw2[0][1] - 30.0) < 1e-3 and p_a == 1 and p_b == (1, True) and p_c == 2,
          "R3 (look down = straight up): hop (0, 30, 0); the top is NOT the stale client speed 0 before the rise, the rise (vy 8) is seen, then vy 0.3 "
          "<= 0.5 = the top -> hang: %s %s %s %s" % (hw2, p_a, p_b, p_c))
    # refused: a class lock / too little Stamina = the 0.1.2 way (the orb flies, the hop job decides); hop.hangSeconds 0 = 0.1.2
    br.put("class:fn:allowed", DenyId(WID["Iron"]))
    reset_buf()
    TWd.JOBS.clear()
    ow3, opw3 = launched(ORB["Iron"], 1303, 0.5, 65.5, 0.5)
    AT.added(ow3, opw3, 2002, tst, tbuf)
    r_lock = (ow3 in list(TBf.REMOVED), tw.orbs.containsKey(ow3), len(list(TWd.JOBS)), LP.STATES.get(cu) is None, str(LP.LAST_WHY))
    br.remove("class:fn:allowed")
    mc.setStatValue(STAM, JFloat(1.0))
    reset_buf()
    TWd.JOBS.clear()
    ow4, opw4 = launched(ORB["Iron"], 1304, 0.5, 65.5, 0.5)
    AT.added(ow4, opw4, 2002, tst, tbuf)
    r_st = (ow4 in list(TBf.REMOVED), tw.orbs.containsKey(ow4), sv(mc, STAM), LP.STATES.get(cu) is None, str(LP.LAST_WHY))
    mc.setStatValue(STAM, JFloat(10.0))
    ACfg.HOP_HANG = 0.0
    reset_buf()
    TWd.JOBS.clear()
    ow5, opw5 = launched(ORB["Iron"], 1305, 0.5, 65.5, 0.5)
    AT.added(ow5, opw5, 2002, tst, tbuf)
    r_old = (ow5 in list(TBf.REMOVED), tw.orbs.containsKey(ow5), len(list(TWd.JOBS)), LP.STATES.get(cu) is None)
    ACfg.HOP_HANG = 0.35
    check(r_lock == (False, True, 1, True, "wand: class lock") and r_st == (False, True, 1.0, True, "wand: too little Stamina") and r_old == (False, True, 1, True),
          "R3: a class lock / too little Stamina -> the orb is NOT removed (it flies at once, the 0.1.2 hop job refuses the same way); hop.hangSeconds 0 = "
          "exactly 0.1.2 (orb + hop job): %s %s %s" % (r_lock, r_st, r_old))
    # a damaging fall is never erased: falling at 30 b/s the hop keeps it and there is NO hang (the orb fires at the first tick)
    reset_buf()
    vel_r.setClient(0.0, -30.0, 0.0)
    ow6, opw6 = launched(ORB["Iron"], 1306, 0.5, 65.5, 0.5)
    AT.added(ow6, opw6, 2002, tst, tbuf)
    sw6 = LP.STATES.get(cu)
    hk6 = last_instr(rc)
    n6 = hk6[3]
    LP.tickPlayer(rc, tst, tbuf)
    kf = (sw6 is not None and bool(sw6.kept), hk6[0][1], LP.STATES.get(cu) is None, last_instr(rc)[3] == n6, len(list(TBf.ADDED)), str(LP.LAST_WHY))
    vel_r.setClient(0.0, 0.0, 0.0)
    check(kf == (True, -30.0, True, True, 1, "fired - falling - no hang (fall kept)"),
          "R3 (fall damage rules as the wand hop): falling at 30 b/s the hop keeps the fall (vy -30) and there is no hang - the orb fires at the first tick, "
          "no Set: %s" % (kf,))
    # death / another world mid-leap = no shot; a new cast fires the older leap's shot at once (never lost)
    reset_buf()
    mc.setStatValue(STAM, JFloat(10.0))
    ow7, opw7 = launched(ORB["Iron"], 1307, 0.5, 65.5, 0.5)
    AT.added(ow7, opw7, 2002, tst, tbuf)
    put(rc, DTHc.getComponentType(), TCc())
    LP.tickPlayer(rc, tst, tbuf)
    dd7 = (LP.STATES.get(cu) is None, len(list(TBf.ADDED)), str(LP.LAST_WHY))
    put(rc, DTHc.getComponentType(), None)
    mc.setStatValue(STAM, JFloat(10.0))
    ow8, opw8 = launched(ORB["Iron"], 1308, 0.5, 65.5, 0.5)
    AT.added(ow8, opw8, 2002, tst, tbuf)
    LP.tickPlayer(rc, U.allocateInstance(TSt.class_), tbuf)
    wc8 = (LP.STATES.get(cu) is None, len(list(TBf.ADDED)), str(LP.LAST_WHY))
    mc.setStatValue(STAM, JFloat(10.0))
    ow9, opw9 = launched(ORB["Iron"], 1309, 0.5, 65.5, 0.5)
    AT.added(ow9, opw9, 2002, tst, tbuf)
    mc.setStatValue(STAM, JFloat(10.0))
    ow10, opw10 = launched(ORB["Iron"], 1310, 0.5, 65.5, 0.5)
    AT.added(ow10, opw10, 2002, tst, tbuf)
    nl10 = (len(list(TBf.ADDED)), LP.STATES.get(cu) is not None)
    LP.STATES.clear()
    check(dd7 == (True, 0, "died (no shot)") and wc8 == (True, 0, "left the world (no shot)") and nl10 == (1, True),
          "R3: dying / leaving the world mid-leap = no shot; a second cast mid-leap fires the first leap's orb at once and starts its own: %s %s %s" % (dd7, wc8, nl10))
    print("R3. wand leap: orb removed at spawn, hop 30 (dash), rise seen, hang Sets each tick, the orb where you look now, burst + heal as before; "
          "refused / hang 0 = 0.1.2; damaging fall kept (no hang); death / world = no shot")

    # --- R4. THE BOW LEAP on a REAL StandardPhysicsProvider (the full-draw arrow's SPAWN through GrappleBoltSys)
    BOW_M = "SkyyArmory_Bow_Leap"
    reset_buf()
    TW.ALL.clear()
    LP.STATES.clear()
    mc.setStatValue(STAM, JFloat(10.0))
    mc.setStatValue(MANA, JFloat(200.0))
    LP.HAND.put(cu, "Weapon_Shortbow_Iron")
    LP.LOOK.put(cu, JArray(JDouble)([0.5, 65.6, 0.5, 1.0, 0.0, 0.0]))
    ba1, spa1 = shoot(creator=cu, model=BOW_M)
    sb1 = LP.STATES.get(cu)
    hb1 = last_instr(rc)
    check(sb1 is not None and int(sb1.kind) == 2 and str(sb1.pid) == "SkyyArmory_Bow_Blast" and abs(float(sb1.base) - 19.0) < 1e-9 and ba1 in list(TBf.REMOVED)
          and hb1[0] == (-30.0, 0.0, 0.0) and hb1[2] == (0.97, 0.94, 5.0, "Exp") and sv(mc, STAM) == 7.0 and sv(mc, MANA) == 199.0,
          "R4 (Skyy: the Wynncraft bow traversal): an Iron shortbow's full-draw arrow (our model id) -> removed at its SPAWN, pushed exactly opposite the look "
          "(-30, 0, 0; bow.hopForce 30, the dash config), 3 Stamina + 1 Mana (physical), the blast arrow will deal the Iron bow's full draw 19: %s %s" % (hb1, str(LP.LAST_WHY)))
    sb1.t0 = NOW() - 150
    LP.tickPlayer(rc, tst, tbuf)
    hbh = last_instr(rc)
    LP.LOOK.put(cu, JArray(JDouble)([0.5, 65.6, 0.5, 0.0, -0.6, 0.8]))         # aiming down at something during the hang
    sb1.hangUntil = NOW() - 1
    reset_buf()
    LP.tickPlayer(rc, tst, tbuf)
    add_b = list(TBf.ADDED)
    pcb = None if not add_b else add_b[0][0].getComponent(LPCc.getComponentType())
    lvb = None if pcb is None else ASp_.launchVelocity(pcb.getSimplePhysicsProvider())
    nrb = None if not add_b else add_b[0][1]
    tw = TW.of(tst)
    check(hbh[0] == (-6.0, -1.5, 0.0) and hbh[2] is None and len(add_b) == 1 and str(pcb.getProjectileAssetName()) == "SkyyArmory_Bow_Blast"
          and str(pcb.getCreatorUuid()) == str(cu) and lvb is not None and float(lvb.y()) < 0.0 and float(lvb.z()) > 0.0 and abs(float(lvb.x())) < 1e-6
          and tw is not None and tw.pend.containsKey(nrb) and abs(float(tw.pend.get(nrb).base) - 19.0) < 1e-9,
          "R4: the hang (Sets of (-6, -1.5, 0)) then the BLAST ARROW launched where you aim now (down + forward), creator = you, carrying 19: %s" % (
              repr(None if lvb is None else (float(lvb.x()), float(lvb.y()), float(lvb.z()))),))
    put(nrb, LPCc.getComponentType(), pcb)
    put(nrb, TCc.getComponentType(), TCc(V3(0.5, 65.3, 0.9), R3(0.0, 0.0, 0.0)))
    AT.added(nrb, pcb, 6000, tst, tbuf)
    check(tw.orbs.containsKey(nrb) and abs(float(tw.orbs.get(nrb).base) - 19.0) < 1e-9 and int(tw.orbs.get(nrb).code) == 6000 and int(ADefs.pidCode("SkyyArmory_Bow_Blast")) == 6000,
          "R4: the blast arrow's SPAWN -> its record (code 6000, base 19)")
    TS4 = JClass(PKG + "ArmoryTuneSys")(False)
    TCH.R = n_dir3
    d4 = DMGc(DPS(rc, nrb), DCSc.PROJECTILE, JFloat(20.0))
    TS4.handle(0, tch, tst, tbuf, d4)
    d4b = DMGc(DPS(rc, nrb), DCSc.PROJECTILE, JFloat(10.0))
    TS4.handle(0, tch, tst, tbuf, d4b)
    check(abs(float(d4.getAmount()) - 19.0) < 1e-4 and abs(float(d4b.getAmount()) - 9.5) < 1e-4,
          "R4 (ArmoryTuneSys): the blast arrow's own hit = the bow's full draw (20 -> 19; an earlier factor kept: 10 -> 9.5): %s %s" % (float(d4.getAmount()), float(d4b.getAmount())))
    NEARL[:] = [n_dir3, n_near3, rp, rs, rc]
    reset_buf()
    AT.landed(tst, tbuf, d4, nrb, 6000, n_dir3)
    ev4 = events()
    my4 = [e_[1] for e_ in list(TBf.EVENTS)]
    d_mine = my4[0] if my4 else None
    if d_mine is not None:
        a_before = float(d_mine.getAmount())
        TS4.handle(0, tch, tst, tbuf, d_mine)
    check(ev4 == [(1331, 11.4, "ProjectileSource", int(nrb.getIndex()))] and d_mine is not None and float(d_mine.getAmount()) == a_before
          and not [1 for k_ in range(tw.fx.size()) if int(tw.fx.get(k_).kind) == 2],
          "R4 (the explosive arrow): its direct hit -> the BLAST: every OTHER enemy within 4 takes 60%% of 19 = 11.4 through the whole damage pipeline "
          "(Damage$ProjectileSource) - not the direct target, the party member, the stranger (PvP off) or you; ArmoryTuneSys leaves our own blast "
          "hits alone; no heal orb: %s" % ev4)
    reset_buf()
    AT.landed(tst, tbuf, d4, nrb, 6000, n_near3)
    once = events() == []
    wcfg.setPvpEnabled(True)
    nrb2 = REFc(tst, 1340)
    s_b2 = JClass(PKG + "TravShot")(0.5, 65.0, 0.5, 0.0, 6000, cu, "SkyyArmory_Bow_Blast")
    s_b2.base = 37.0
    tw.orbs.put(nrb2, s_b2)
    put(nrb2, TCc.getComponentType(), TCc(V3(7.0, 64.0, 5.5), R3(0.0, 0.0, 0.0)))
    reset_buf()
    AT.removed(nrb2, True, tst, tbuf)
    ev4m = sorted(events())
    wcfg.setPvpEnabled(False)
    check(once and ev4m == [(3, 22.2, "EntitySource", None), (1330, 22.2, "EntitySource", None), (1331, 22.2, "EntitySource", None)] and not tw.orbs.containsKey(nrb2),
          "R4: one blast per arrow; a blast arrow that hits no one blasts where it ENDS (a Mithril bow: 60%% of 37 = 22.2 to every enemy around - with PvP on "
          "the stranger too, the party member never): %s" % ev4m)
    # refused = the arrow is LEFT ALONE (the vanilla full-draw shot): class lock, too little Stamina, part off, no bow in hand, a vanilla arrow model
    def bow_try(hand=None, stam=10.0, part=True, model=BOW_M, deny=False):
        reset_buf()
        LP.STATES.clear()
        mc.setStatValue(STAM, JFloat(stam))
        if hand is None:
            LP.HAND.remove(cu)
        else:
            LP.HAND.put(cu, hand)
        ACfg.PART_BOWTRAV = part
        if deny:
            br.put("class:fn:allowed", NoXbow2())
        b_, sp_ = shoot(creator=cu, model=model)
        if deny:
            br.remove("class:fn:allowed")
        ACfg.PART_BOWTRAV = True
        return (b_ in list(TBf.REMOVED), LP.STATES.get(cu) is not None, sv(mc, STAM))

    @JImplements("java.util.function.Function")
    class NoXbow2:
        @JOverride
        def apply(self, o):
            a_ = list(o)
            return JClass("java.lang.Boolean").FALSE if "Shortbow" in str(a_[1]) else JClass("java.lang.Boolean").TRUE
    rf = [bow_try("Weapon_Shortbow_Iron", deny=True), bow_try("Weapon_Shortbow_Iron", stam=2.0), bow_try("Weapon_Shortbow_Iron", part=False),
          bow_try("Weapon_Crossbow_Iron"), bow_try(None), bow_try("Weapon_Shortbow_Iron", model="Arrow_Crude")]
    ok_bow = bow_try("Weapon_Shortbow_Crude")
    cr_base = float(LP.STATES.get(cu).base) if LP.STATES.get(cu) is not None else None
    LP.STATES.clear()
    check(rf == [(False, False, 10.0), (False, False, 2.0), (False, False, 10.0), (False, False, 10.0), (False, False, 10.0), (False, False, 10.0)]
          and ok_bow == (True, True, 7.0) and cr_base == 12.0,
          "R4: the vanilla full-draw arrow is LEFT ALONE (not removed, no leap, nothing paid) for a class that may not use bows, too little Stamina (2 < 3), "
          "part.bowtrav off, a crossbow / nothing in hand, a vanilla arrow model; a Crude bow leaps with its own 12: %s %s %s" % (rf, ok_bow, cr_base))
    tt4 = calls_of(PKG + "TravTick", "tick")
    gb4 = calls_of(PKG + "GrappleBoltSys", "onEntityAdded")
    check(tt4.count("tickPlayer") == 2 and "onBowShot" in gb4, "R4: TravTick runs Grapple.tickPlayer AND Leap.tickPlayer; GrappleBoltSys hands our arrow model to Leap.onBowShot")
    print("R4. bow leap: arrow removed, hop 30, 3 + 1, hang, the blast arrow where you aim (19 for Iron), blast 60% / 4 blocks, misses blast too; refusals = vanilla arrow")

    # --- R5. THE PARTICLE LIFE: no point particle is started whose emission outlives its effect (heal pulse + ring, trail, rope after the grapple)
    ACfg.TRAV_FX = True
    AT.PSEEN = ArrayList()
    TW.ALL.clear()
    tw5 = TW.get(tst)
    t0_ = NOW()
    FXc = JClass(PKG + "TravFx")
    f_h = FXc(2, 0.5, 64.0, 0.5, 0.5, 64.0, 0.5, 9.0, t0_ + 3300, t0_, 1000, 5.0, cu, None, 2002)       # lives that are NOT a multiple of the
    f_t = FXc(1, 0.5, 64.9, 0.5, 6.5, 64.9, 0.5, 0.75, t0_ + 2900, t0_, 500, 5.0, cu, None, 5002)     # re-draw interval (orb.seconds 3.3, trail 2.9)
    tw5.add(f_h, 64, t0_)
    tw5.add(f_t, 64, t0_)
    last_ = {}
    first_ = {}
    t_ = t0_
    while t_ <= t0_ + 4200:
        n0_ = AT.PSEEN.size()
        tw5.run(tst, tbuf, t_)
        for x_ in list(AT.PSEEN)[n0_:]:
            last_[str(x_)] = t_
            first_.setdefault(str(x_), t_)
        t_ += 50
    em = {"SkyyArmory_Heal_Pulse": 500, "SkyyArmory_Ring_Blue": 500, "SkyyArmory_Trail_Light": 250}
    until_ = {"SkyyArmory_Heal_Pulse": t0_ + 3300, "SkyyArmory_Ring_Blue": t0_ + 3300, "SkyyArmory_Trail_Light": t0_ + 2900}
    pl5 = dict((k, (first_.get(k, -1) - t0_, last_.get(k, -1) - t0_, last_.get(k, 10 ** 9) + em[k] <= until_[k])) for k in em)
    check(all(v_[2] and v_[0] == 0 for v_ in pl5.values()) and pl5["SkyyArmory_Ring_Blue"][1] == 2500 and pl5["SkyyArmory_Trail_Light"][1] == 2500
          and pl5["SkyyArmory_Heal_Pulse"][1] == 2000,
          "R5 (Skyy: 'the blue balls stay'): over a heal orb's 3.3 s and a trail's 2.9 s life (TravWorld.run every 50 ms) the heal pulse, the blue ring and the "
          "gold trail are spawned only while their emission ends inside the effect - last start + emission <= the end (ms from the start: first, last, ok): %s" % pl5)
    # the rope: only while the grapple runs - nothing after it ends (release / arrival / snap)
    GR.HAND = HashMap()
    GR.HAND.put(gu, "Weapon_Crossbow_Iron")
    GR.STATES.clear()
    reset_buf()
    setpos(gr_, 0.5, 64.0, 0.5)
    full()
    GR.DOT_WIN = 0
    b5, sp5 = shoot(x=20.5, y=66.0, z=0.5)
    sp5.setState(SPST.RESTING)
    click()
    AT.PSEEN.clear()
    for _k in range(8):
        gtick()
    during = len([x_ for x_ in list(AT.PSEEN) if str(x_) == "SkyyArmory_Rope_Dot"])
    click()
    AT.PSEEN.clear()
    for _k in range(12):
        gtick()
    after = len(list(AT.PSEEN))
    ACfg.TRAV_FX = False
    AT.PSEEN = None
    psd = DEC.get(("particle system", "SkyyArmory_Rope_Dot"))
    check(during > 0 and after == 0 and gstate() is None and psd is not None and abs(float(psd.getLifeSpan()) - 0.15) < 1e-6,
          "R5 (Skyy: 'it leaves partials behind'): rope dots only while pulled (%d dots in 8 ticks), NONE after the let-go (%d); each dot system ends by its "
          "engine-decoded LifeSpan %s s + particles <= 0.15 s = gone <= 0.3 s after the grapple ends" % (during, after, None if psd is None else float(psd.getLifeSpan())))
    lsp = dict((k_, round(float(DEC[("particle system", k_)].getLifeSpan()), 3)) for k_ in ("SkyyArmory_Trail_Light", "SkyyArmory_Ring_Blue", "SkyyArmory_Heal_Pulse",
                                                                                                  "SkyyArmory_Burst", "SkyyArmory_Rope_Dot") if ("particle system", k_) in DEC)
    check(lsp == {"SkyyArmory_Trail_Light": 0.25, "SkyyArmory_Ring_Blue": 0.5, "SkyyArmory_Heal_Pulse": 0.5, "SkyyArmory_Burst": 0.3, "SkyyArmory_Rope_Dot": 0.15}
          and str(AT.PS_RING) == "SkyyArmory_Ring_Blue" and str(AT.PS_HEAL) == "SkyyArmory_Heal_Pulse" and str(AT.PS_BURST) == "SkyyArmory_Burst",
          "R5: the engine's own ParticleSystem codec reads every point system's LifeSpan (the field Block_Break / the totem use) and the Java spawns the "
          "finite copies: %s" % lsp)
    print("R5. particle life: heal pulse / ring / trail stop inside their effect, rope dots stop with the grapple, LifeSpans decoded: %s" % lsp)

    # --- R6. THE CROSSBOWS: decoded items + recipes, the grapple from them, SkyyClasses' own Archer rule, SkyyGear's bands
    bad6 = []
    for k_ in L13_ITEMS:
        o_, why_ = dec(ITMc, k_, json.dumps(XITEM[k_]))
        if o_ is None or why_:
            bad6.append("%s: %s" % (k_, why_))
            continue
        if not (int(o_.getMaxDurability()) == XITEM[k_]["MaxDurability"] and int(o_.getItemLevel()) == XITEM[k_]["ItemLevel"]):
            bad6.append("%s: read-back %s / %s" % (k_, o_.getMaxDurability(), o_.getItemLevel()))
        ro_, rwhy_ = dec_recipe(json.dumps(XITEM[k_]["Recipe"]), k_ + "_Recipe_Generated_0")
        if ro_ is None or rwhy_:
            bad6.append("%s recipe: %s" % (k_, rwhy_))
    check(not bad6, "R6: both crossbows decode through Item's engine codec (Parent Template_Weapon_Crossbow in the store) + their recipes through "
                    "CraftingRecipe.CODEC, durability / level read back: %s" % bad6)
    g6 = []
    for k_ in L13_ITEMS:
        reset_buf()
        GR.STATES.clear()
        GR.LASTEND.clear()
        GR.HAND.put(gu, k_)
        b6, sp6 = shoot()
        g6.append((gstate() is not None and str(gstate().item) == k_, b6 in list(TBf.REMOVED)))
    GR.STATES.clear()
    GR.HAND = None
    check(g6 == [(True, False), (True, False)], "R6: the Grapple Bolt works from both new crossbows (the id holds 'crossbow'): %s" % g6)
    CLJ = os.path.join(ROOT, "SkyyClasses", "SkyyClasses-%s.jar" % PIN["SkyyClasses"])
    own6 = None
    if os.path.isfile(CLJ):
        UCL = JClass("java.net.URLClassLoader")
        ucl = UCL(JArray(JClass("java.net.URL"))([JClass("java.io.File")(CLJ).toURI().toURL()]), sysl)
        CDF = JClass("java.lang.Class").forName("com.skyy.classes.ClassDefs", True, ucl)
        m_own = CDF.getMethod("ownerOf", JClass("java.lang.String").class_)
        f_arc = CDF.getField("ARCHER")
        own6 = [int(m_own.invoke(None, x_)) for x_ in L13_ITEMS + ["Weapon_Crossbow_Iron"]] + [int(f_arc.get(None))]
    check(own6 is not None and own6[0] == own6[1] == own6[2] == own6[3],
          "R6 (class lock): SkyyClasses %s's own ClassDefs.ownerOf (loaded from its jar) gives both new crossbows the Archer class like the Iron crossbow: %s" % (
              PIN["SkyyClasses"], own6))
    bd6 = [[int(x) for x in GLvl.band(k_)] for k_ in L13_ITEMS]
    gg6 = [(bool(GData.isGear(k_)), bool(GData.skyyItem(k_))) for k_ in L13_ITEMS]
    check(bd6[0][:2] == [10, 18] and bd6[1][:2] == [40, 49] and gg6 == [(True, False), (True, False)],
          "R6 (SkyyGear %s's real code): the Copper crossbow is gear in the Copper band 10-18, the Onyxium one in the Onyxium band 40-49 (the metal word "
          "in the id), neither a Skyy item: %s %s" % (os.path.basename(GEAR_JAR), bd6, gg6))
    print("R6. crossbows: decoded + recipes, grapple from both, SkyyClasses Archer, SkyyGear bands %s" % bd6)

    # --- R7. THE ONE-TIME hop.force UPDATE (Skyy: "30"; PROJECT-RULES 4): the text step, then the real migrate013 on a scratch file
    MK3 = str(ACfg.M13_MARK)

    def upd3(t_):
        r_ = ACfg.m13Update(t_)
        return None if r_ is None else (str(r_[0]), str(r_[1]), [str(x) for x in r_[2]], [str(x) for x in r_[3]])
    v1 = upd3("a=1\nhop.force=13\nb=2\n")
    v2 = upd3("a=1\r\nhop.force = 13.0\r\n")
    v3 = upd3("hop.force=20\n")
    v4 = upd3("quick.life=20\n")
    v5 = upd3(v1[0])
    v6 = upd3("hop.force=30\n")
    check(v1 == ("a=1\n" + MK3 + "\nhop.force=30\nb=2\n", "hop.force 13 -> 30", [], ["hop.force", "13", "30"])
          and v2 == ("a=1\r\n" + MK3 + "\r\nhop.force = 30\r\n", "hop.force 13.0 -> 30", [], ["hop.force", "13.0", "30"])
          and v3[0] == MK3 + "\nhop.force=20\n" and v3[1] == "" and len(v3[2]) == 1 and "kept (custom)" in v3[2][0]
          and v4 == ("quick.life=20\n" + MK3 + "\n", "", [], []) and v5 is None and v6 == (MK3 + "\nhop.force=30\n", "", [], []),
          "R7 (PROJECT-RULES 4): an untouched 13 (or 13.0) -> 30 (value text only, CRLF kept), a hand-set 20 KEPT + noted, no line = marker only, runs once: "
          "%s / %s / %s" % (v1, v2, v3))
    mdir3 = os.path.join(SCRATCH, "m13", "mods", "Skyy_SkyyArmory")
    shutil.rmtree(os.path.dirname(os.path.dirname(mdir3)), ignore_errors=True)
    os.makedirs(mdir3)
    mtxt3 = ("# SkyyArmory 0.1.2 test file\r\npart.trav=true\r\nhop.force=13\r\nquick.life=20\r\n").encode("latin-1")
    open(os.path.join(mdir3, "config.properties"), "wb").write(mtxt3)
    ACfg.DIR = Paths.get(mdir3)
    ACfg.FILE = ACfg.DIR.resolve("config.properties")
    mr3 = str(ACfg.migrate013())
    af3 = open(os.path.join(mdir3, "config.properties"), "rb").read()
    hist3 = os.path.join(mdir3, "config-history")
    baks3 = sorted(f_ for f_ in os.listdir(hist3) if f_.endswith(".bak")) if os.path.isdir(hist3) else []
    log3 = open(os.path.join(mdir3, "config-changes.log"), "rb").read().decode("latin-1") if os.path.isfile(os.path.join(mdir3, "config-changes.log")) else ""
    mr3b = str(ACfg.migrate013())
    ACfg.load()
    hf3 = float(ACfg.HOP_FORCE)
    ACfg.DIR = None
    ACfg.FILE = None
    ACfg.useDefaults()
    check(af3 == upd3(mtxt3.decode("latin-1"))[0].encode("latin-1") and b"hop.force=30\r\n" in af3 and baks3 and open(os.path.join(hist3, baks3[-1]), "rb").read() == mtxt3
          and "\tSkyyArmory 0.1.3\t-\tupdate\thop.force\t13\t30\tok" in log3 and "13 -> 30" in mr3 and mr3b == "" and hf3 == 30.0,
          "R7 (the real ArmoryCfg.migrate013 on a scratch file): History copy = the old bytes, the Undo-able change-log line, CRLF kept, the second run idle, "
          "the loader reads 30: %s | %s" % (mr3[:120], log3.strip()[-70:]))
    print("R7. hop.force one-time update: 13 -> 30, custom kept, marker once, real migrate013 with History + Undo log")
    LP.HAND = None
    LP.LOOK = None
    LP.STATES.clear()
    TW.ALL.clear()
    AT.NEAR = None
    AT.GRID = None
    br.remove("party:fn:members")
'''
# (old, new) swaps of 0.1.2 checks that 0.1.3 changes on purpose
HARNESS_SWAPS = [
    ('''check(sorted(J_ITEMS) == sorted([WID[m] for m in NEW] + [SID[m] for m in METALS]), "P0: 15 items = 7 new wands + the 8 ladder staffs: %s" % sorted(J_ITEMS))''',
     '''check(sorted(J_ITEMS) == sorted([WID[m] for m in NEW] + [SID[m] for m in METALS] + L13_ITEMS),
      "P0: 17 items = 7 new wands + the 8 ladder staffs + 0.1.3's 2 crossbows: %s" % sorted(J_ITEMS))'''),
    ('''check(len(J_INTS) == 121 and len(J_ROOTS) == 16 and len(J_PRJ) == 39, "P0: 121 interactions (0.1.2: + 6 grapple), 16 roots (+ the crossbow root override), 39 projectiles (%d / %d / %d)" % (''',
     '''check(len(J_INTS) == 122 and len(J_ROOTS) == 16 and len(J_PRJ) == 40, "P0: 122 interactions (0.1.3: + the full-draw override), 16 roots, 40 projectiles (+ the blast arrow) (%d / %d / %d)" % ('''),
    ('''check(sorted(J_PRJ) == sorted(list(ORB.values()) + list(QORB.values()) + list(SORB.values()) + list(SQORB.values()) + list(BLINK.values())), "P0: projectile ids")''',
     '''check(sorted(J_PRJ) == sorted(list(ORB.values()) + list(QORB.values()) + list(SORB.values()) + list(SQORB.values()) + list(BLINK.values()) + L13_PRJ), "P0: projectile ids")'''),
    ('''check(sorted(J_MODELS) == ["SkyyArmory_Grapple_Bolt", "SkyyArmory_Marker", "SkyyArmory_QuickOrb"] and sorted(J_TRAILS) == ["SkyyArmory_Orb_Trail_Blue", "SkyyArmory_Rope_Trail"]
      and len(J_PSYS) == 5 and len(J_PSP) == 9,''',
     '''check(sorted(J_MODELS) == ["SkyyArmory_Bow_Leap", "SkyyArmory_Grapple_Bolt", "SkyyArmory_Marker", "SkyyArmory_QuickOrb"]
      and sorted(J_TRAILS) == ["SkyyArmory_Orb_Trail_Blue", "SkyyArmory_Rope_Trail"] and len(J_PSYS) == 8 and len(J_PSP) == 9 + 2 + 6 + 8,'''),
    ('''check(len(J_PNG) == 15 and "Server/Languages/en-US/server.lang" in JSET and "manifest.json" in JSET, "P0: 15 PNGs (7 textures, 7 icons, 1 orb texture), lang, manifest")''',
     '''check(len(J_PNG) == 19 and "Server/Languages/en-US/server.lang" in JSET and "manifest.json" in JSET, "P0: 19 PNGs (7 + 2 crossbow textures, 7 + 2 icons, 1 orb texture), lang, manifest")'''),
    ('''check(all(k.startswith("SkyyArmory_") or k in ("Wand_Primary", "Root_Weapon_Crossbow_Secondary_Guard") for k in list(J_INTS) + list(J_ROOTS)) and "Wand_Primary" in J_INTS''',
     '''check(all(k.startswith("SkyyArmory_") or k in ("Wand_Primary", "Root_Weapon_Crossbow_Secondary_Guard") + tuple(L13_INT) for k in list(J_INTS) + list(J_ROOTS)) and "Wand_Primary" in J_INTS'''),
    # the 0.1.3 additions leave the 0.1.2 tables (their own checks are P10 / R): every older check keeps running on the 0.1.2 set
    ('''JPRJ = dict((i, J[p]) for i, p in J_PRJ.items())
''', '''JPRJ = dict((i, J[p]) for i, p in J_PRJ.items())
XITEM = dict((k, JITEM.pop(k)) for k in L13_ITEMS)          # 0.1.3: the crossbows, the full-draw override, the blast arrow - checked in P10 / R
XINT = dict((k, JINT.pop(k)) for k in L13_INT)
XPRJ = dict((k, JPRJ.pop(k)) for k in L13_PRJ)
X_PATHS = dict([(k, J_ITEMS.pop(k)) for k in L13_ITEMS] + [(k, J_INTS.pop(k)) for k in L13_INT] + [(k, J_PRJ.pop(k)) for k in L13_PRJ])
'''),
    ('''VAN_ORB = "Skeleton_Mage_Corruption_Orb"
''', '''VAN_ORB = "Skeleton_Mage_Corruption_Orb"
L13_ITEMS = ["Weapon_Crossbow_Copper_Wynn", "Weapon_Crossbow_Onyxium_Wynn"]       # 0.1.3
L13_INT = ["Weapon_Shortbow_Primary_Shoot_Strength_4"]
L13_PRJ = ["SkyyArmory_Bow_Blast"]
'''),
    # SkyySkills 0.4.19+ (pinned) also ships the Dodge Roll interactions (another round): the 8 spell overrides are still all there
    ('''check(sorted(SK_INTS) == sorted(["Wand_Cast_Left_Charged", "Wand_Cast_Cost", "Staff_Cast_Summon_Charged", "Staff_Cast_Cost", "Spellbook_Cast_Hurl_Charged",
                                 "Spellbook_Cast_Cost", "Gun_Shoot_Flintlock_Charged", "Gun_Shoot_Cost"]), "pinned SkyySkills %s: its 8 interaction overrides" % SKILLS_PIN)''',
     '''_SK8 = ["Wand_Cast_Left_Charged", "Wand_Cast_Cost", "Staff_Cast_Summon_Charged", "Staff_Cast_Cost", "Spellbook_Cast_Hurl_Charged", "Spellbook_Cast_Cost",
        "Gun_Shoot_Flintlock_Charged", "Gun_Shoot_Cost"]
check(set(_SK8) <= set(SK_INTS) and all(k == "Dodge" or k.startswith("SkyySkills_") for k in set(SK_INTS) - set(_SK8)),
      "pinned SkyySkills %s: its 8 interaction overrides (+ only its own Dodge Roll files, 0.4.19+): %s" % (SKILLS_PIN, sorted(set(SK_INTS) - set(_SK8))))'''),
    ('''check(sorted(J_PCFG) == [G_BOLT] and sorted(J_EFX) == sorted([G_OUT, G_CLICK]) and all(i in JINT for i in G_INTS) and XROOT in JROOT,
      "P9 (T1): the grapple files - 6 interactions, the root override, 1 projectile config, 2 effects: %s %s" % (sorted(J_PCFG), sorted(J_EFX)))''',
     '''check(sorted(J_PCFG) == sorted([G_BOLT, "SkyyArmory_Bow_Leap"]) and sorted(J_EFX) == sorted([G_OUT, G_CLICK]) and all(i in JINT for i in G_INTS) and XROOT in JROOT,
      "P9 (T1): the grapple files - 6 interactions, the root override, 1 projectile config (+ 0.1.3's bow leap config), 2 effects: %s %s" % (sorted(J_PCFG), sorted(J_EFX)))'''),
    ('''      and not [n for n in JN if "Crossbow" in n and n.startswith("Server/Item/Items/")],
      "P9 (2.1): every crossbow reaches the root through the vanilla template (no item override shipped); left click / reload / swap stay vanilla")''',
     '''      and sorted(os.path.basename(n)[:-5] for n in JN if "Crossbow" in n and n.startswith("Server/Item/Items/")) == L13_ITEMS
      and all("Interactions" not in XITEM[k] and XITEM[k]["Parent"] == "Template_Weapon_Crossbow" for k in L13_ITEMS),
      "P9 (2.1): every crossbow reaches the root through the vanilla template (no vanilla item override shipped; 0.1.3's 2 new crossbows parent "
      "the template and name no interaction); left click / reload / swap stay vanilla")'''),
    ('''check(_rt["LifeSpan"] == 40 and _rt["RenderMode"] == "BlendLinear" and _rt["Start"]["Color"] == "#8a6a45e0" and _rt["End"]["Color"] == "#8a6a4500"
      and _rt["TexturePath"] == _vt["TexturePath"], "P9 (2.4): the rope trail = the vanilla Arrow trail, rope brown, twice as long")''',
     '''check(_rt["LifeSpan"] == _vt["LifeSpan"] == 20 and _rt["RenderMode"] == "BlendLinear" and _rt["Start"]["Color"] == "#8a6a45e0" and _rt["End"]["Color"] == "#8a6a4500"
      and _rt["TexturePath"] == _vt["TexturePath"], "P9 (2.4, 0.1.3): the rope trail = the vanilla Arrow trail, rope brown, the vanilla length again (0.1.2: 40)")'''),
    ('''    check(len(names) == 35, "A: 35 classes (28 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple classes + 7 kit)")''',
     '''    check(len(names) == 37, "A: 37 classes (30 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap classes + 7 kit)")'''),
    # L: the 0.1.3 assets into the real stores too (the vanilla parents they name first), then the plugin's own pack check
    ('''    CHK = JClass(PKG + "ArmoryCheck")
    r = CHK.packCheck()
    check(str(r[0]) == "info" and "15 of 15 items, 121 of 121 interactions, 39 of 39 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.2 SkyyArmory" in str(r[1])''',
     '''    # 0.1.3: the vanilla parents the new assets name (the crossbow template, its var parents + roots, the shortbow projectile step) - parents first -
    # then the 2 crossbows, the full-draw override and the blast arrow, with our pack
    need13, seen13, roots13 = [], set(), []

    def need_of(x):
        if isinstance(x, str):
            if x in INTS_ALL and x not in seen13 and x not in vint and x not in JINT:
                seen13.add(x)
                need_of(INTS_ALL[x])
                need13.append(x)
            elif x in ROOTS_ALL and x not in seen13 and x not in vroot and x not in JROOT:
                seen13.add(x)
                need_of(ROOTS_ALL[x])
                roots13.append(x)
        elif isinstance(x, list):
            for e in x:
                need_of(e)
        elif isinstance(x, dict):
            for k, v in x.items():
                if k not in ("Type", "$Comment"):
                    need_of(v)
    vtpl13 = aj("item", "Template_Weapon_Crossbow")
    for d_ in [vtpl13] + list(XITEM.values()) + list(XINT.values()):
        need_of(d_)

    def decp(c, key, d):
        """dec() with the asset's Parent key handed to the codec (AssetExtraInfo.Data's parent key - the store resolves the inheritance)"""
        st = AR.getAssetStore(c.class_)
        ei = AEI(Paths.get(key + ".json"), ADT(c.class_, key, d.get("Parent")))
        par = st.getAssetMap().getAsset(d["Parent"]) if d.get("Parent") else None
        if d.get("Parent") and par is None:
            return None, "parent %s not in the store" % d["Parent"]
        try:
            if par is not None:      # the store's own inheritance path (AssetCodec.decodeAndInheritJsonAsset with the loaded parent)
                o = st.getCodec().decodeAndInheritJsonAsset(RJR.fromJsonString(json.dumps(d)), par, ei)
            else:
                o = st.getCodec().decodeJsonAsset(RJR.fromJsonString(json.dumps(d)), ei)
        except Exception as e:
            return None, "exception " + str(e)[:300]
        uk = [str(x) for x in ei.getUnknownKeys()]
        return o, ("unknown keys %s" % uk) if uk else ""
    van13, bad13 = [], []          # the vanilla neighbours: best effort (some need modules the bare JVM has no codecs for) - a NOTE, never a FAIL
    for i_ in need13:
        o_, w_ = decp(INTc, i_, INTS_ALL[i_])
        if o_ is None or load(INTc, [o_], "Hytale:Hytale") is not True:
            van13.append(i_)
    for i_ in roots13:
        o_, w_ = decp(ROOTc, i_, ROOTS_ALL[i_])
        if o_ is None or load(ROOTc, [o_], "Hytale:Hytale") is not True:
            van13.append(i_)
    o_, w_ = decp(ITMc, "Template_Weapon_Crossbow", vtpl13)
    if o_ is None:
        bad13.append("the crossbow template: %s" % w_)
    else:
        load(ITMc, [o_], "Hytale:Hytale")
    for c_, tab_, kind_ in ((INTc, XINT, "interaction"), (PRJc, XPRJ, "projectile"), (ITMc, XITEM, "item")):
        for k_, d_ in tab_.items():
            o_, w_ = decp(c_, k_, d_)
            if o_ is None or w_:
                bad13.append("%s %s: %s" % (kind_, k_, w_))
                continue
            DEC[(kind_, k_)] = o_
            load(c_, [o_], PACK)          # (an item's load validates sounds / interactions the bare JVM lacks - the store holding it is the check)
            if c_.getAssetMap().getAsset(k_) is None or str(c_.getAssetMap().getAssetPack(k_)) != PACK:
                bad13.append("%s %s is not in the store from our pack" % (kind_, k_))
    check(not bad13, "L (0.1.3): the 2 crossbows (on the vanilla template, decoded with the store's own inheritance), the full-draw override (on its vanilla "
                     "parent) and the blast arrow decode through the engine codecs - no unknown key - and sit in the real stores from our pack: %s" % bad13)
    print("L. NOTE %d of %d vanilla neighbours of the crossbow template could not load in the bare JVM (codecs of other modules): %s" % (
        len(van13), len(need13) + len(roots13), van13[:8]))
    CHK = JClass(PKG + "ArmoryCheck")
    r = CHK.packCheck()
    check(str(r[0]) == "info" and "17 of 17 items, 122 of 122 interactions, 40 of 40 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.3 SkyyArmory" in str(r[1])'''),
    # K: + the 10 leap rows (after the grapple rows)
    ('''                 "grapple.ropeSpacing", "grapple.cooldown", "grapple.yankSize", "grapple.bossWords", "grapple.noYankWords", "grapple.yankPlayers"]      # 0.1.2
    NN = len(NEW_ROWS)''', '''                 "grapple.ropeSpacing", "grapple.cooldown", "grapple.yankSize", "grapple.bossWords", "grapple.noYankWords", "grapple.yankPlayers"]      # 0.1.2
    NEW_ROWS += ["hop.hangSeconds", "hop.hangFall", "part.bowtrav", "bow.hopForce", "bow.hangSeconds", "bow.hangFall", "bow.blastRadius", "bow.blastPercent",
                 "bow.stamina", "bow.mana"]      # 0.1.3
    NN = len(NEW_ROWS)'''),
    # N8: hop.force's default is Skyy's 30 now
    ('''                "blink.trailPercent": "30", "blink.tick": "0.5", "blink.cooldown": "0", "hop.force": "13", "hop.groundCheck": "6", "burst.radius": "6",''',
     '''                "blink.trailPercent": "30", "blink.tick": "0.5", "blink.cooldown": "0", "hop.force": "30", "hop.groundCheck": "6", "burst.radius": "6",'''),
    # N8 forget: an orb record keeps the world (the 0.1.2 way: hang 0 - with the 0.1.3 hang the orb is re-fired at the top instead)
    ('''    reset_buf()
    ob7, opc7 = launched(ORB["Iron"], 990, 0.5, 65.5, 0.5)
    AT.added(ob7, opc7, 2002, tst, tbuf)''', '''    reset_buf()
    ob7, opc7 = launched(ORB["Iron"], 990, 0.5, 65.5, 0.5)
    ACfg.HOP_HANG = 0.0
    AT.added(ob7, opc7, 2002, tst, tbuf)
    ACfg.HOP_HANG = 0.35'''),
    # T: the live copy gets BOTH one-time updates (each its own History version); the second start nothing
    ('''        want_ = str(ACfg.m12Update(old_.decode("latin-1"))[0]).encode("latin-1") if ACfg.m12Update(old_.decode("latin-1")) is not None else old_
        hb_ = sorted(k for k in s1 if k.startswith(os.path.join("Skyy_SkyyArmory", "config-history")) and k.endswith(".bak") and k not in s0)
        check(s1[kc_][0] == want_ and (want_ == old_ or (len(hb_) == 1 and s1[hb_[0]][0] == old_)) and str(ACfg.M12_MARK_ID) in s1[kc_][0].decode("latin-1"),
              "T (0.1.2): the live copy's config.properties got the one-time Stamina cap update on the first start (= the text step's result, the old bytes kept "
              "as a History version): %d -> %d bytes, %s" % (len(old_), len(s1[kc_][0]), hb_))''',
     '''        t_ = old_.decode("latin-1")
        r12_ = ACfg.m12Update(t_)
        t12_ = str(r12_[0]) if r12_ is not None else t_
        r13_ = ACfg.m13Update(t12_)
        want_ = (str(r13_[0]) if r13_ is not None else t12_).encode("latin-1")
        hb_ = sorted(k for k in s1 if k.startswith(os.path.join("Skyy_SkyyArmory", "config-history")) and k.endswith(".bak") and k not in s0)
        txt1_ = s1[kc_][0].decode("latin-1")
        check(s1[kc_][0] == want_ and (want_ == old_ or (1 <= len(hb_) <= 2 and s1[hb_[0]][0] == old_)) and str(ACfg.M12_MARK_ID) in txt1_ and str(ACfg.M13_MARK_ID) in txt1_,
              "T (0.1.2 + 0.1.3): the live copy's config.properties got the one-time updates on the first start (= the text steps' result - Skyy's live file: "
              "no hop.force line = the marker only, the new default 30 applies; the old bytes kept as a History version): %d -> %d bytes, %s" % (len(old_), len(s1[kc_][0]), hb_))'''),
]

traw = open(TSRC, encoding="utf8", newline="").read()
TNL = CR + LF if (CR + LF) in traw else LF
ts = traw.replace(CR + LF, LF)


def hrep(old, new, count=1):
    global ts
    n = ts.count(old)
    assert n == count, "harness anchor count %d (want %d): %s" % (n, count, old[:140])
    ts = ts.replace(old, new)


hrep('"""SkyyArmory 0.1.2 - test harness. GENERATED by tools/armory_0_1_2_patch.py from test_skyyarmory_0.1.1.py - edit the patch, never this file.',
     '''"""SkyyArmory 0.1.3 - test harness. GENERATED by tools/armory_0_1_3_patch.py from test_skyyarmory_0.1.2.py - edit the patch, never this file.
Every 0.1.2 check below still runs (patched where 0.1.3 changed the set on purpose: + the leap / crossbow / particle files in the counts, 37
classes, the leap rows, hop.force 30 - the 0.1.1 traversal checks N2-N7 pin hop.force 13 and hop.hangSeconds 0 to keep their numbers (the
0.1.2 way), the live-copy start runs both one-time updates). NEW sections EXECUTE the 0.1.3 paths:
  P10 (Python) the full-draw override = vanilla with Config swapped, the leap config = the vanilla Strength_4 config resolved with our model id,
      the blast arrow = Arrow_FullCharge with our flight, every point particle system finite (LifeSpan + short particles; the endless sources
      named), the 2 crossbows = the Iron crossbow + the tier table + recipes + recoloured art (only grey texels changed), ids.
  R   (JVM) the rhythm maths; the WAND leap (orb removed at spawn -> hop with the dash config -> rise -> hang Sets each tick -> the same orb
      fired where you look -> burst + heal orb as before; refused = the 0.1.2 way); the BOW leap on a REAL StandardPhysicsProvider (arrow
      removed -> hop 30 -> hang -> the blast arrow; class lock / short Stamina / part off / no bow = the vanilla arrow left alone); the blast
      (direct hit = the bow's full draw through ArmoryTuneSys; others 60 %; PvP + party rules; a miss blasts where it lands); a damaging fall
      kept (no hang); death / world change = no shot; particles: no emission past an effect's end (trail, ring, heal pulse, rope after the
      grapple ends); the crossbows grapple + SkyyClasses' own ClassDefs.ownerOf = Archer + SkyyGear bands; hop.force 13 -> 30 one-time update
      (text step + the real migrate013); the rows.
Harness seams (null in the game): + Leap.HAND, Leap.LOOK (the item in hand, the eye + look), ArmoryTrav.PSEEN (point particles spawned).

0.1.2 harness: SkyyArmory 0.1.2 - test harness. GENERATED by tools/armory_0_1_2_patch.py from test_skyyarmory_0.1.1.py - edit the patch, never this file.''')
hrep('VERSION = "0.1.2"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.2 SkyyArmory"',
     'VERSION = "0.1.3"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.3 SkyyArmory"')
hrep('os.path.join(SCRATCH_ROOT, "armory012", "harness")', 'os.path.join(SCRATCH_ROOT, "armory013", "harness")')
hrep('raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.2.py', 'raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.3.py')
hrep('''        setf(p_, PBc, "dataDirectory", Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.2")))''',
     '''        setf(p_, PBc, "dataDirectory", Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.3")))''')
hrep('''    ready = [m_ for lv_, m_ in records()[n_log0:] if "[SkyyArmory] 0.1.2 ready" in m_]''', '''    ready = [m_ for lv_, m_ in records()[n_log0:] if "[SkyyArmory] 0.1.3 ready" in m_]''')
hrep('''    trav_line = [m_ for lv_, m_ in records()[n_log0:] if "0.1.2 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_]''',
     '''    trav_line = [m_ for lv_, m_ in records()[n_log0:] if "0.1.3 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_]''')
hrep('''    gr_line = [m_ for lv_, m_ in records()[n_log0:] if "0.1.2 crossbow grapple: grapple on" in m_]''',
     '''    gr_line = [m_ for lv_, m_ in records()[n_log0:] if "0.1.3 crossbow grapple: grapple on" in m_]''')
hrep('''    ACfg.STAMINA_CAP = 10          # 0.1.2: N2-N7 keep 0.1.1's numbers at the old cap 10 (the 0.1.2 default 5 is checked in N8, G2 and Q12)''',
     '''    ACfg.STAMINA_CAP = 10          # 0.1.2: N2-N7 keep 0.1.1's numbers at the old cap 10 (the 0.1.2 default 5 is checked in N8, G2 and Q12)
    ACfg.HOP_FORCE = 13.0          # 0.1.3: N2-N7 keep 0.1.1's hop numbers (13) and the 0.1.2 way (no hang); the 0.1.3 defaults are checked in R
    ACfg.HOP_HANG = 0.0''')
for _old, _new in HARNESS_SWAPS if "HARNESS_SWAPS" in globals() else []:
    hrep(_old, _new)
if HARNESS_P10:
    hrep('''PY_OKS, PY_FAILS = OKS[0], len(FAILS)''', HARNESS_P10.rstrip("\n") + "\n" + '''PY_OKS, PY_FAILS = OKS[0], len(FAILS)''')
if HARNESS_R:
    hrep('''    # ---------------- L2. (last: it changes the store)''', HARNESS_R.rstrip("\n") + "\n" + '''    # ---------------- L2. (last: it changes the store)''')
tout = ts.replace(LF, TNL)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(tout)
print("wrote %s (%d lines)" % (os.path.relpath(TDST, ROOT), tout.count(TNL) + 1))
