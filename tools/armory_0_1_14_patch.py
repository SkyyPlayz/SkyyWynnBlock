"""Derive SkyyArmory/build_skyyarmory_0.1.14.py (+ its harness SkyyArmory/test_skyyarmory_0.1.14.py) from the GENERATED 0.1.13
(SkyyArmory/build_skyyarmory_0.1.13.py = the tools/deploy_set.py SET pin, made by tools/armory_0_1_13_patch.py; test_skyyarmory_0.1.13.py =
its harness). Every anchor is asserted (rep = exactly one hit). Edit THIS file, never the generated scripts.
Run:  python tools/armory_0_1_14_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.14.py   then
      python SkyyArmory/test_skyyarmory_0.1.14.py --dir tools/dev/scratch/<task>/harness      (never --deploy)

0.1.14 = THE WAND SIGNATURE (Skyy 2026-10-08, docs/answered/gear.md: "Wand can shoot a shot that ricochets through eight enemies"; "Id like to
keep the vanilla Q special attacks on the weapons. That charge from use"; "Whichever ability is tied to the weapon, players can worry about
what its bound to."). No saved data, no migration (new keys only - a missing key reads its default).
  THE METER (the vanilla signature way, Template_Weapon_Sword read at build time): each of the 7 metal wands (Weapon_Wand_Copper ... _Onyxium)
    gets Weapon.EntityStatsToClear ["SignatureEnergy"] + StatModifiers SignatureEnergy +SIG_MAX (20, the sword's size) and the sword's
    "signature ready" look (ItemAppearanceConditions on the Handle node) - the client shows the meter and the ready glow exactly like a
    vanilla weapon. The vanilla meters fill through the damage interactions' EntityStatsOnHit (+1 a hit); our wand shots are legacy
    Projectile assets (no EntityStatsOnHit field), so the server adds the charge (Rico.gain, ArmoryHitSys = the Inspect group, the hit
    really landed): a quick-orb hit +sig.wand.chargeQuick (1), a charged-orb direct hit +sig.wand.chargeCharged (2), only while a wand is
    in the shooter's hand, clamped at the meter's max; our own bounce / burst hits never charge (vanilla signature hits do not either).
    SkyyGear 0.2.10 keeps the charge across weapon swaps through the player's SignatureEnergy (not touched here).
  THE KEY: Interactions.Ability1 = the root SkyyArmory_Wand_Signature (RequireNewClick, Tags Attack Ranged - the crossbow BigArrow root's
    shape) -> SkyyArmory_Wand_Signature_Cast = StatsCondition SignatureEnergy 100 % (the vanilla gate, client-predicted) -> ChangeStat
    SignatureEnergy -100 % -> SkyyArmory_Wand_Signature_Launch (the CastLeftCharged pose + the vanilla SFX_Staff_Ice_Shoot) = LaunchProjectile
    of the invisible marker SkyyArmory_Wand_Ricochet (the blink-marker shape, code 13000). Every existing wand move (tap quick shot, hold
    hop / burst / heal orb, right-click block) is untouched (Primary / Secondary roots unchanged).
  THE RICOCHET (Java: Rico + RicoChain, world thread - the marker's SPAWN queues a chain on the world's TravWorld, TravTick advances it):
    the first target = an enemy within sig.wand.aimRange 24 of your eye, inside sig.wand.aimCone 30 (full width) around your aim, line of
    sight, the smallest angle wins (ties: the nearer); then every sig.wand.bounceDelay 0.15 s the bolt jumps to the NEAREST enemy it has
    not hit yet within sig.wand.bounceRange 10 of the last one (line of sight), up to sig.wand.maxHits 8 hits; no enemy in range = it stops
    early. Never the same enemy twice. Enemy = ArmoryTrav.kind (a mob with stats, alive; a player only where the world PvP is on +
    trav.players + sig.wand.players, never yourself or a party member / ally), never a protected mob (Invulnerable / grapple.noYankWords)
    and never a Friendly / Revered / Ignore mob (livestock, pets, summoned allies - the Shadow Step attitude rule). A target that died mid-
    chain is skipped (the next jump starts where it stood). Damage: hit 1 = sig.wand.firstHit 1.5 x the wand's charged shot (the jar's
    number before levels x tune.wand), every bounce sig.wand.falloff 10 % less than the one before (8 hits = 1.5, 1.35, ... 0.72 x), each
    through the whole damage pipeline (ArmoryTrav.hit: Damage$EntitySource(you), PROJECTILE, marked ours). The look: a line of the blue
    finite ring points (SkyyArmory_Ring_Blue, the Page Burst ring) along every jump, the vanilla Impact_Sword_Signature burst (finite,
    asserted) + the vanilla SFX_Skeleton_Mage_Spellbook_Impact on each hit (trav.fx off = none). No enemy in your aim: nothing happens and
    the charge comes back (sig.wand.refundMiss); signature off / class lock: the charge comes back too.
  THE WOOD WAND: Weapon_Wand_Wood (+ Rotten / Tribal) is SkyySkills' item file (SkyySkills loads after us and wins the id - this build
    asserts it ships no Weapon_Wand_Wood): it cannot get the Ability1 key or the meter from this jar. The Java already serves it (wand
    index 0: base 25 x 1.5, its quick shots charge) - the Wood signature goes live when SkyySkills' Weapon_Wand_Wood names
    "Ability1": "SkyyArmory_Wand_Signature" + the same Weapon / ItemAppearanceConditions (or hands the id over). UNVERIFIED until then.
  SETTINGS: 12 rows (Server Setup > Armory > Wand + signature, keys sig.wand.*; the category was "Wand hop + burst") + 1 read-only row (the meter size + the key).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.13.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.14.py")
TSRC = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.13.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.14.py")

CR, LF = chr(13), chr(10)
raw = open(SRC, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.13"\nMOD = "SkyyArmory"' in s and "0.1.13 = THE LOG FIXES" in s, "build_skyyarmory_0.1.13.py is not the 0.1.13 pin"
assert "Rico" not in s and "sig.wand" not in s, "0.1.13 already has the 0.1.14 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:140])
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyArmory 0.1.13 - build script (javassist via jpype). GENERATED by tools/armory_0_1_13_patch.py from the GENERATED 0.1.12 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.13.py -> SkyyArmory/SkyyArmory-0.1.13.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.13.py --dir tools/dev/scratch/<task>/harness.
''', '''"""SkyyArmory 0.1.14 - build script (javassist via jpype). GENERATED by tools/armory_0_1_14_patch.py from the GENERATED 0.1.13 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.14.py -> SkyyArmory/SkyyArmory-0.1.14.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.14.py --dir tools/dev/scratch/<task>/harness.

0.1.14 = THE WAND SIGNATURE (Skyy 2026-10-08 "Wand can shoot a shot that ricochets through eight enemies"; full notes in
tools/armory_0_1_14_patch.py): the 7 metal wands get the vanilla signature meter (SignatureEnergy max 20, the sword's ready glow) charged by
their shot hits (quick +1, charged +2; server side - legacy projectiles have no EntityStatsOnHit) and Ability 1 = StatsCondition 100 % ->
ChangeStat -100 % -> the marker SkyyArmory_Wand_Ricochet (code 13000): Rico picks the enemy in your aim (24 blocks, 30 degree cone, line of
sight), then jumps every 0.15 s to the nearest enemy it has not hit within 10 blocks, up to 8 hits; hit 1 = 1.5 x the wand's charged shot,
-10 % a bounce; PvP / party / attitude rules of the traversals; no target = the charge back. 12 rows sig.wand.* + 1 read-only row.

0.1.13 (the base, everything below is still true unless 0.1.14 above says otherwise):

0.1.13 = THE LOG FIXES''')
rep('''
0.1.13 = THE LOG FIXES (Skyy 2026-10-08 "check the logs to fix things"; full notes in tools/armory_0_1_13_patch.py)''',
    ''' (Skyy 2026-10-08 "check the logs to fix things"; full notes in tools/armory_0_1_13_patch.py)''')
rep('VERSION = "0.1.13"\nMOD = "SkyyArmory"', 'VERSION = "0.1.14"\nMOD = "SkyyArmory"')

# ---------------------------------------------------------------------------------------------------------------- the rows (Server Setup)
CFG_SIG_PY = r'''# ================================================================= 0.1.14 THE WAND SIGNATURE (Skyy 2026-10-08 "Wand can shoot a shot that ricochets through eight enemies")
SIG_MAX = 20                     # the meter (SignatureEnergy max on the wand item, client-predicted = a read-only row): the vanilla sword's size
RICO_MARK, RICO_CODE = "SkyyArmory_Wand_Ricochet", 13000          # the invisible marker Ability 1 launches (removed at its SPAWN)
_SG = "hop"          # the existing wand category (the kit allows 16 and all 16 are used), relabelled "Wand hop + burst" -> "Wand + signature" (20-char label cap)
CFG_SIG = [
    ('sig.wand.enabled', 'Wand signature (ricochet)', _SG, 'bool', 'true', '', '', '', '', 'live,part,danger', 'Off = the wand signature does nothing (its charge is given back).', 'SIG_ON', 'boolean', 'true', 'Wand signature (Ability 1 when the meter is full): a magic bolt that ricochets from enemy to enemy. Off = nothing happens, the charge comes back.'),
    ('sig.wand.firstHit', 'Signature first hit (x charged shot)', _SG, 'dec', '1.5', '0.1', '5', '', 'x', 'live', "The first enemy takes this x the wand's charged shot (before levels).", 'SIG_FIRST', 'double', '1.5', "Wand signature: the first enemy takes this x the wand's charged shot (its damage before levels, x tune.wand)."),
    ('sig.wand.falloff', 'Each bounce hits less (%)', _SG, 'int', '10', '0', '50', 'step=5', '%', 'live', 'Every bounce hits this % less than the hit before it.', 'SIG_FALL', 'int', '10', 'Wand signature: every bounce hits this % less than the hit before it.'),
    ('sig.wand.maxHits', 'Signature: most enemies hit', _SG, 'int', '8', '1', '16', '', '', 'live', 'The bolt stops after this many hits (never the same enemy twice).', 'SIG_HITS', 'int', '8', 'Wand signature: the bolt stops after this many hits (never the same enemy twice).'),
    ('sig.wand.bounceRange', 'Bounce range (blocks)', _SG, 'dec', '10', '2', '24', '', 'blocks', 'live', 'It jumps to the nearest enemy it has not hit within this range (line of sight).', 'SIG_BOUNCE', 'double', '10', 'Wand signature: the bolt jumps to the nearest enemy it has not hit within this many blocks (line of sight); none = it stops.'),
    ('sig.wand.aimRange', 'Signature first target range (blocks)', _SG, 'int', '24', '4', '48', '', 'blocks', 'live', 'The first enemy must be this close to you (line of sight).', 'SIG_RANGE', 'int', '24', 'Wand signature: the first enemy must be at most this many blocks from you (line of sight).'),
    ('sig.wand.aimCone', 'Signature aim cone (degrees, full)', _SG, 'int', '30', '10', '180', 'step=5', '', 'live', 'Full cone width around your crosshair; closest to the crosshair wins.', 'SIG_CONE', 'int', '30', 'Wand signature: the first enemy must be inside a cone this many degrees wide around your aim; the one closest to your crosshair wins.'),
    ('sig.wand.bounceDelay', 'Time between bounces (s)', _SG, 'dec', '0.15', '0', '1', '', 's', 'live', '0 = every bounce in the same moment.', 'SIG_DELAY', 'double', '0.15', 'Wand signature: seconds between two hits of the bolt (0 = all at once).'),
    ('sig.wand.chargeQuick', 'Signature charge per quick-shot hit', _SG, 'dec', '1', '0', '10', '', '', 'live', 'The meter holds %d; a quick shot that hits an enemy adds this.' % SIG_MAX, 'SIG_GAINQ', 'double', '1', 'Wand signature: a quick shot that hits adds this much to the meter (it holds %d).' % SIG_MAX),
    ('sig.wand.chargeCharged', 'Signature charge per charged hit', _SG, 'dec', '2', '0', '10', '', '', 'live', 'A charged shot that hits an enemy adds this.', 'SIG_GAINC', 'double', '2', 'Wand signature: a charged shot that hits adds this much to the meter (its burst adds nothing).'),
    ('sig.wand.players', 'Signature bounces to players (PvP on)', _SG, 'bool', 'true', '', '', '', '', 'live', 'Only where the world PvP is on and trav.players is on; never party.', 'SIG_PLAYERS', 'boolean', 'true', 'Wand signature: the bolt may hit players where the world PvP is on (trav.players on too); never party members.'),
    ('sig.wand.refundMiss', 'No enemy in aim: charge back', _SG, 'bool', 'true', '', '', '', '', 'live', 'On = a signature with no enemy in your aim keeps its charge.', 'SIG_REFUND', 'boolean', 'true', 'Wand signature: no enemy in your aim = nothing happens and the meter is full again (off = the charge is spent).'),
]
assert len(set(r[0] for r in CFG_SIG)) == len(CFG_SIG) == 12 and all(len(r) == 15 and r[2] == _SG for r in CFG_SIG)
assert all(len(r[1]) <= 40 and len(r[10]) <= 100 for r in CFG_SIG), [(r[0], len(r[1]), len(r[10])) for r in CFG_SIG if len(r[1]) > 40 or len(r[10]) > 100]
'''
rep('''# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)''', CFG_SIG_PY + '''# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)''')
rep('''+ CFG_GRAPPLE + CFG_LEAP + CFG_BK + CFG_ST + CFG_SS + CFG_MK      # 0.1.12: + the Monk moves;''',
    '''+ CFG_GRAPPLE + CFG_LEAP + CFG_BK + CFG_ST + CFG_SS + CFG_MK + CFG_SIG      # 0.1.14: + the wand signature; 0.1.12: + the Monk moves;''')

# the category label (critic fix: the signature rows were hidden under "Wand hop + burst"; id "hop" unchanged, the kit caps labels at 20)
rep('''("hop", "Wand hop + burst")''', '''("hop", "Wand + signature")''')

# ---------------------------------------------------------------------------------------------------------------- the assets
ASSET_PY = r'''# ================================================================= 0.1.14 ASSETS: THE WAND SIGNATURE (the vanilla signature shape; tools/armory_0_1_14_patch.py)
ID_SIG_ROOT = "SkyyArmory_Wand_Signature"                   # the Ability1 root (RootInteractions/Weapons/Wand/SkyyArmory/)
ID_SIG_CAST, ID_SIG_LAUNCH = "SkyyArmory_Wand_Signature_Cast", "SkyyArmory_Wand_Signature_Launch"
SND_SIG_CAST = "SFX_Staff_Ice_Shoot"          # the vanilla charged-cast sound (Wand_Cast_Effect / Staff_Cast_Effect)
PS_SIG_HIT = "Impact_Sword_Signature"         # the vanilla signature impact (finite: every spawner has TotalParticles - asserted)
SND_SIG_HIT = SND_BOOK_HIT                    # the vanilla magic impact (SFX_Skeleton_Mage_Spellbook_Impact)
PS_SIG_BOLT = PS_RING                         # the finite blue ring point (the Page Burst ring; built from vanilla at build time)
# ---- (1) the vanilla signature shapes this block copies (a game update that changes them stops the build)
_vsw = resolve("item", "Template_Weapon_Sword")
assert _vsw["Interactions"].get("Ability1") == "Root_Weapon_Sword_Signature_Vortexstrike" and sorted(_vsw["Weapon"]) == ["EntityStatsToClear", "StatModifiers"] \
    and _vsw["Weapon"]["EntityStatsToClear"] == ["SignatureEnergy"] and _vsw["Weapon"]["StatModifiers"] == {"SignatureEnergy": [{"Amount": 20, "CalculationType": "Additive"}]}, \
    "the vanilla sword's signature meter changed: %s" % _vsw.get("Weapon")
SIG_WEAPON = json.loads(json.dumps(_vsw["Weapon"]))
SIG_WEAPON["StatModifiers"]["SignatureEnergy"][0]["Amount"] = SIG_MAX
SIG_LOOK = json.loads(json.dumps(_vsw["ItemAppearanceConditions"]))
assert list(SIG_LOOK) == ["SignatureEnergy"] and len(SIG_LOOK["SignatureEnergy"]) == 1 and SIG_LOOK["SignatureEnergy"][0]["Condition"] == [100, 100], SIG_LOOK
_slp = [p_ for k_ in ("Particles", "FirstPersonParticles") for p_ in SIG_LOOK["SignatureEnergy"][0].get(k_, [])]
assert _slp and all(p_.get("TargetNodeName") == "Handle" and p_.get("TargetEntityPart") == "PrimaryItem" and az_has("psys", p_["SystemId"]) for p_ in _slp), _slp
assert VW["Particles"][0]["TargetNodeName"] == "Handle", "the wand model's Handle node (the ready glow's anchor) changed"
_vxr = az_get("root", "Root_Weapon_Crossbow_Signature_BigArrow")
assert _vxr == {"RequireNewClick": True, "Interactions": ["Weapon_Crossbow_Signature_BigArrow"], "Tags": {"Attack": ["Ranged"]}}, _vxr
_vxs = az_get("int", "Weapon_Crossbow_Signature_BigArrow")["Next"]
assert _vxs["Type"] == "StatsCondition" and _vxs["Costs"] == {"SignatureEnergy": 100} and _vxs["ValueType"] == "Percent" \
    and _vxs["Next"]["Type"] == "ChangeStat" and _vxs["Next"]["ValueType"] == "Percent" and _vxs["Next"]["StatModifiers"]["SignatureEnergy"] == -100, _vxs
assert az_has("stat", "SignatureEnergy") and az_get("stat", "SignatureEnergy")["Max"] == 0, "the vanilla SignatureEnergy stat changed"
assert az_has("sound", SND_SIG_CAST) and az_has("sound", SND_SIG_HIT) and "CastLeftCharged" in ANIMS[ANIM_WAND]["Animations"]
_shs = json.loads(AZ.read(_IDX["psys"][PS_SIG_HIT][0]).decode("utf-8-sig"))
_shsp = [json.loads(AZ.read(_IDX["pspawn"][x_["SpawnerId"]][0]).decode("utf-8-sig")) for x_ in _shs["Spawners"]]
assert _shsp and all(isinstance(x_.get("TotalParticles"), dict) and x_["TotalParticles"].get("Max", 0) > 0 for x_ in _shsp), \
    "the vanilla %s is no longer finite - it would leave particles behind" % PS_SIG_HIT
# ---- (2) the root, the gate + spend, the launch, the marker
assert not az_has("root", ID_SIG_ROOT) and ID_SIG_ROOT not in ROOTS
ROOTS[ID_SIG_ROOT] = {"RequireNewClick": True, "Interactions": [ID_SIG_CAST], "Tags": {"Attack": ["Ranged"]}}
put(P_WROOT % ID_SIG_ROOT, ROOTS[ID_SIG_ROOT])
add_int(P_WINT, ID_SIG_CAST, {"Type": "StatsCondition", "Costs": {"SignatureEnergy": 100}, "ValueType": "Percent",
                              "Next": {"Type": "ChangeStat", "StatModifiers": {"SignatureEnergy": -100}, "ValueType": "Percent", "Next": ID_SIG_LAUNCH}})
add_int(P_WINT, ID_SIG_LAUNCH, {"Type": "LaunchProjectile", "RunTime": RT_LAUNCH,
                                "Effects": {"ItemAnimationId": "CastLeftCharged", "WorldSoundEventId": SND_SIG_CAST}, "ProjectileId": RICO_MARK})
add_prj(RICO_MARK, blink_marker())
RICO_PRJS = [RICO_MARK]
# ---- (3) the 7 metal wands: Ability1 + the meter + the ready look (every other field, the Primary / Secondary roots untouched)
SIG_WANDS = []
for _m in NEW_METALS:
    _i, _p = "Weapon_Wand_" + _m, P_WITEM % _m
    _it = ITEMS[_i]
    assert ASSETS[_p] == jdump(_it) and _it["Weapon"] == {} and "Ability1" not in _it["Interactions"] and "ItemAppearanceConditions" not in _it \
        and _it["Interactions"] == {"Primary": ID_WROOT % _m, "Secondary": GUARD_ROOT}, (_i, _it["Interactions"])
    _old = json.loads(json.dumps(_it))
    _it["Interactions"]["Ability1"] = ID_SIG_ROOT
    _it["Weapon"] = json.loads(json.dumps(SIG_WEAPON))
    _it["ItemAppearanceConditions"] = json.loads(json.dumps(SIG_LOOK))
    assert sorted(k_ for k_ in set(_it) | set(_old) if _it.get(k_) != _old.get(k_)) == ["Interactions", "ItemAppearanceConditions", "Weapon"], _i
    ASSETS[_p] = jdump(_it)
    SIG_WANDS.append(_i)
assert len(SIG_WANDS) == 7 and "Weapon_Wand_Wood" not in ITEMS          # the Wood wand is SkyySkills' file (see the patch notes)
# ---- (4) the descriptions say the signature
_ll = ASSETS[P_LANG].split("\n")
SIG_LANG = []
for _n, _l in enumerate(_ll):
    for _i in SIG_WANDS:
        if _l.startswith("items.%s.description = " % _i):
            assert _l.endswith(" Right click: block.") and "Signature" not in _l, _l
            _ll[_n] = _l[:-len(" Right click: block.")] + " Signature (fills as your shots hit): a bolt that ricochets through up to 8 enemies. Right click: block."
            SIG_LANG.append(_i)
assert sorted(SIG_LANG) == sorted(SIG_WANDS)
ASSETS[P_LANG] = "\n".join(_ll)
# ---- (5) reference closure + no one-entry Parallel anywhere in the jar (0.1.10: the engine refuses the pack)
_sig14 = []
for _iid in (ID_SIG_CAST, ID_SIG_LAUNCH):
    for _r in refs_of(INTS[_iid], set()):
        if _r not in INTS and _r not in ROOTS and not az_has("int", _r) and not az_has("root", _r):
            _sig14.append("%s -> %s" % (_iid, _r))
assert all(_x in INTS for _x in ROOTS[ID_SIG_ROOT]["Interactions"]) and INTS[ID_SIG_LAUNCH]["ProjectileId"] in PRJS and not _sig14, _sig14


def _one_par(o_, out_, n_):
    if isinstance(o_, dict):
        if o_.get("Type") == "Parallel" and (not isinstance(o_.get("Interactions"), list) or len(o_["Interactions"]) < 2):
            out_.append(n_)
        for v_ in o_.values():
            _one_par(v_, out_, n_)
    elif isinstance(o_, list):
        for v_ in o_:
            _one_par(v_, out_, n_)


_op14 = []
for _p, _t in ASSETS.items():
    if _p.startswith("Server/") and _p.endswith(".json") and not isinstance(_t, bytes):
        _one_par(json.loads(_t), _op14, _p)
assert not _op14, "0.1.14: a one-entry Parallel (the engine refuses the whole pack): %s" % _op14[:4]
SIG_FILES = sorted([P_WROOT % ID_SIG_ROOT, P_WINT % ID_SIG_CAST, P_WINT % ID_SIG_LAUNCH, P_PRJ % RICO_MARK])
SIG_CHANGED = sorted(P_WITEM % m for m in NEW_METALS)
assert all(p in ASSETS for p in SIG_FILES + SIG_CHANGED) and len(SIG_FILES) == 4 and len(SIG_CHANGED) == 7
print("0.1.14 wand signature: meter %d (the sword's), Ability1 %s -> %s -> %s (marker %s, code %d); %d new files, %d wands changed + their "
      "descriptions; hit look %s / %s, bolt %s" % (SIG_MAX, ID_SIG_ROOT, ID_SIG_CAST, ID_SIG_LAUNCH, RICO_MARK, RICO_CODE, len(SIG_FILES), len(SIG_CHANGED),
                                                   PS_SIG_HIT, SND_SIG_HIT, PS_SIG_BOLT))
'''
rep('''# ================================================================= the SET jars, SkyySkills (anchor + handover), the clash scan''',
    ASSET_PY + '''# ================================================================= the SET jars, SkyySkills (anchor + handover), the clash scan''')
rep('''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS + MK_PRJS)) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) + 1 + len(BK_PRJS) + len(SS_PRJS) + len(MK_PRJS) == len(PRJS) \\
    and set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS + MK_PRJS) == set(PRJS)''',
    '''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS + MK_PRJS + RICO_PRJS)) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) + 1 + len(BK_PRJS) + len(SS_PRJS) + len(MK_PRJS) + len(RICO_PRJS) == len(PRJS) \\
    and set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS + MK_PRJS + RICO_PRJS) == set(PRJS)          # 0.1.14: + the ricochet marker''')

# ---------------------------------------------------------------------------------------------------------------- the config file + rows
rep('''] + [x for _r in CFG_MK for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
''', '''] + [x for _r in CFG_MK for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
    "",
    "# ---- wand signature (SkyyArmory 0.1.14; Skyy 2026-10-08 'Wand can shoot a shot that ricochets through eight enemies'): the signature key when the meter is full",
] + [x for _r in CFG_SIG for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
''')
rep('''FIXED_VAL = dict((f[0], f[3]) for f in FIXED)
''', '''FIXED.append(("fixed.sig.wand", "Wand signature meter (fixed in the jar)", "hop",
              "the signature key (Ability 1) when the meter is full: %d (quick-shot hit +1, charged hit +2 by default); the 7 metal wands "
              "(the Wood wand follows when SkyySkills hands its item over)" % SIG_MAX,
              "Client-predicted: meter size, key, ready glow (the sword's). The rows above set the rest."))
FIXED_VAL = dict((f[0], f[3]) for f in FIXED)
''')

# ---------------------------------------------------------------------------------------------------------------- ArmoryDefs + ArmoryCfg
rep('''for f in ("public static final String MK_VAULT_MARK = %s;" % jstr(MK_VAULT_MARK), "public static final int MK_VAULT_CODE = %d;" % MK_VAULT_CODE,
          "public static final String MK_RISE_MARK = %s;" % jstr(MK_RISE_MARK), "public static final int MK_RISE_CODE = %d;" % MK_RISE_CODE):          # 0.1.12
    F(dfs, f)
''', '''for f in ("public static final String MK_VAULT_MARK = %s;" % jstr(MK_VAULT_MARK), "public static final int MK_VAULT_CODE = %d;" % MK_VAULT_CODE,
          "public static final String MK_RISE_MARK = %s;" % jstr(MK_RISE_MARK), "public static final int MK_RISE_CODE = %d;" % MK_RISE_CODE):          # 0.1.12
    F(dfs, f)
for f in ("public static final String RICO_MARK = %s;" % jstr(RICO_MARK), "public static final int RICO_CODE = %d;" % RICO_CODE,
          "public static final int SIG_MAX = %d;" % SIG_MAX):          # 0.1.14 the wand signature
    F(dfs, f)
''')
rep('''  m.put(MK_RISE_MARK, Integer.valueOf(MK_RISE_CODE));            // 0.1.12: the Monk Rising Strike marker
''', '''  m.put(MK_RISE_MARK, Integer.valueOf(MK_RISE_CODE));            // 0.1.12: the Monk Rising Strike marker
  m.put(RICO_MARK, Integer.valueOf(RICO_CODE));                  // 0.1.14: the wand signature's ricochet marker
''')
rep('''F(cfg, "public static volatile String MONK_TEXT = \\"\\";")          # 0.1.12
''', '''F(cfg, "public static volatile String MONK_TEXT = \\"\\";")          # 0.1.12
F(cfg, "public static volatile String SIG_TEXT = \\"\\";")          # 0.1.14
''')


def apply_line(r):
    k, typ, d, lo, hi, fld = r[0], r[3], r[4], r[5], r[6], r[11]
    if typ == "bool":
        return '  %s = bool(c.getProperty("%s"), %s);' % (fld, k, d)
    if typ == "int":
        return '  %s = intOf(c.getProperty("%s"), %d, %d, %d);' % (fld, k, int(d), int(lo), int(hi))
    assert typ == "dec", r
    return '  %s = dec(c.getProperty("%s"), %r, %r, %r);' % (fld, k, float(d), float(lo), float(hi))


_ns = {}
exec(CFG_SIG_PY, _ns)          # the row table (plain Python) -> the loader lines of ArmoryCfg.apply
APPLY_SIG = "\n".join(apply_line(r) for r in _ns["CFG_SIG"])
assert "%" not in APPLY_SIG          # apply() is a %-formatted block
rep('''  MONK_TEXT = monkText();          // 0.1.12
  try { @PKG@.ArmoryDefs.bridge().put("armory:monk", MONK_TEXT); } catch (Throwable tmk) { }
''', '''  MONK_TEXT = monkText();          // 0.1.12
  try { @PKG@.ArmoryDefs.bridge().put("armory:monk", MONK_TEXT); } catch (Throwable tmk) { }
''' + APPLY_SIG + '''
  SIG_TEXT = sigText();          // 0.1.14
''')
rep('''M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''', '''# 0.1.14: the wand signature's live numbers (the start line)
M(cfg, r"""
public static String sigText() {
  return "wand signature " + (SIG_ON ? "on" : "OFF") + " - the signature key when the meter is full (" + @PKG@.ArmoryDefs.SIG_MAX + "; quick-shot hit +"
    + cfmt(SIG_GAINQ) + ", charged hit +" + cfmt(SIG_GAINC) + "): a bolt that ricochets through up to " + SIG_HITS + " enemies (the first within " + SIG_RANGE
    + " blocks in a " + SIG_CONE + " degree cone, then the nearest new one within " + cfmt(SIG_BOUNCE) + " every " + cfmt(SIG_DELAY) + " s), first hit "
    + cfmt(SIG_FIRST) + "x the charged shot, -" + SIG_FALL + "% a bounce, players " + (SIG_PLAYERS ? "where PvP is on" : "never") + ", no target: the charge "
    + (SIG_REFUND ? "comes back" : "is spent");
}""")
M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''')

# ---------------------------------------------------------------------------------------------------------------- engine members (probed)
rep('''print("engine members probed: %d" % len(PROBED))
''', '''# ---- 0.1.14 the wand signature: the meter's stat index (the charge + the refund write it with the probed setStatValue / get / getMax)
probe_sig(T["DST"], "getSignatureEnergy", "int", [])
probe_sig(T["ESM"], "setStatValue", "float", ["int", "float"])
probe_sig(T["DENT"], "getRef", T["REF"], [])
print("engine members probed: %d" % len(PROBED))
''')

# ---------------------------------------------------------------------------------------------------------------- the Java (TravWorld + RicoChain + Rico)
rep('''C(tworld, r"""
public TravWorld() {''', '''F(tworld, "public java.util.ArrayList rico;")          # 0.1.14: the wand signature's ricochet chains (RicoChain, this world's thread only)
C(tworld, r"""
public TravWorld() {''')
rep('''  this.books = new java.util.HashMap();
}""")''', '''  this.books = new java.util.HashMap();
  this.rico = new java.util.ArrayList();
}""")''')
rep('''M(tworld, "public boolean idle() { return this.fx.isEmpty() && this.quick.isEmpty() && this.orbs.isEmpty() && this.pend.isEmpty() && this.books.isEmpty(); }")''',
    '''M(tworld, "public boolean idle() { return this.fx.isEmpty() && this.quick.isEmpty() && this.orbs.isEmpty() && this.pend.isEmpty() && this.books.isEmpty() && this.rico.isEmpty(); }")''')
rep('''  if (this.pend.size() > 256) this.pend.clear();
}""")''', '''  if (this.pend.size() > 256) this.pend.clear();
  @PKG@.Rico.run(this, st, buf, now);          // 0.1.14: the wand signature's ricochet chains
}""")''')

RICO_JAVA = r'''# ---------------------------------------------------------------- 0.1.14 THE WAND SIGNATURE RICOCHET (tools/armory_0_1_14_patch.py; Skyy 2026-10-08)
rch = pool.makeClass(PKG + ".RicoChain")
rico = pool.makeClass(PKG + ".Rico")
ALL += [rch, rico]
for f in ("public java.util.UUID u;", "public String item;", "public int wi;", "public double base;", "public int hits;", "public java.util.HashSet hit;",
          "public double x;", "public double y;", "public double z;", "public double[] dir;", "public long next;", "public long born;"):
    F(rch, f)
C(rch, r"""
public RicoChain(java.util.UUID u, String item, int wi, double base, double x, double y, double z, double[] dir, long now) {
  this.u = u;
  this.item = item;
  this.wi = wi;
  this.base = base;
  this.hits = 0;
  this.hit = new java.util.HashSet();
  this.x = x;
  this.y = y;
  this.z = z;
  this.dir = dir;
  this.next = now;
  this.born = now;
}""")
for f in ("public static volatile long MARKS = 0L;", "public static volatile long CASTS = 0L;", "public static volatile long HITS = 0L;",
          "public static volatile long MISSES = 0L;", "public static volatile long ENDS_RANGE = 0L;", "public static volatile long ENDS_MAX = 0L;",
          "public static volatile long REFUSED = 0L;", "public static volatile long REFUNDS = 0L;", "public static volatile long GAINS = 0L;",
          "public static volatile String LAST_WHY = \"\";",
          "public static volatile long CLOCK = 0L;",          # HARNESS SEAM ONLY (0 in the game = the wall clock)
          "public static final double EYE = %r;" % SS_EYE, "public static final int MAX_CHAINS = 256;", "public static final long MAX_MS = 15000L;",
          "public static final String PS_BOLT = %s;" % jstr(PS_SIG_BOLT), "public static final String PS_HIT = %s;" % jstr(PS_SIG_HIT),
          "public static final String SND_HIT = %s;" % jstr(SND_SIG_HIT)):
    F(rico, f)
M(rico, r"""public static void warn(String key, String msg) { @PKG@.ArmoryLog.warnOnce("rico:" + key, msg); }""")
M(rico, r"""public static long now() { long c = CLOCK; return c > 0L ? c : System.currentTimeMillis(); }""")
# ---- PURE maths (plain numbers; the harness runs them)
# hit n (0 = the first) = base x (1 - fall %)^n
M(rico, r"""
public static double amount(double base, int fallPct, int n) {
  if (!(base > 0.0) || n < 0) return 0.0;
  double f = 1.0 - (double) fallPct / 100.0;
  if (f < 0.0) f = 0.0;
  double a = base;
  for (int i = 0; i < n; i++) a = a * f;
  return a;
}""")
# the first hit's base: the wand's charged shot (the jar's number before levels; x tune.wand for the metal wands - the Wood hold is the
# shared vanilla orb, tune.wand scales only its quick shot) x sig.wand.firstHit
M(rico, r"""
public static double base(int wi, boolean tune, double[] pct, double first) {
  if (wi < 0 || wi >= @PKG@.ArmoryDefs.W_CD.length || !(first > 0.0)) return 0.0;
  double b = (double) @PKG@.ArmoryDefs.W_CD[wi];
  if (tune && wi > 0) b = b * @PKG@.ArmoryDefs.pctOf(pct, wi);
  return b * first;
}""")
# the nearest candidate (ok[i]) within range of (x, y, z); ties: the lower index; -1 = none
M(rico, r"""
public static int nearest(double[] xs, double[] ys, double[] zs, boolean[] ok, double x, double y, double z, double range) {
  int best = -1;
  double bd = 1.0E18;
  if (xs == null || ys == null || zs == null || ok == null) return -1;
  for (int i = 0; i < xs.length && i < ys.length && i < zs.length && i < ok.length; i++) {
    if (!ok[i]) continue;
    double dx = xs[i] - x;
    double dy = ys[i] - y;
    double dz = zs[i] - z;
    double d = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (d > range) continue;
    if (d < bd - 1.0E-9) { best = i; bd = d; }
  }
  return best;
}""")
# the aimed candidate: within range of the eye, at most cone / 2 degrees off the aim, the smallest angle wins (ties: the nearer); -1 = none
M(rico, r"""
public static int aimed(double[] xs, double[] ys, double[] zs, boolean[] ok, double ex, double ey, double ez, double[] d, double range, double cone) {
  int best = -1;
  double bo = 1.0E9;
  double bd = 1.0E18;
  if (xs == null || ys == null || zs == null || ok == null || d == null || d.length < 3) return -1;
  for (int i = 0; i < xs.length && i < ys.length && i < zs.length && i < ok.length; i++) {
    if (!ok[i]) continue;
    double vx = xs[i] - ex;
    double vy = ys[i] - ey;
    double vz = zs[i] - ez;
    double dist = Math.sqrt(vx * vx + vy * vy + vz * vz);
    if (dist > range || dist < 0.3) continue;
    double off = @PKG@.TravMath.offDeg(d[0], d[1], d[2], vx, vy, vz);
    if (off > cone * 0.5) continue;
    if (off < bo - 1.0E-6 || (Math.abs(off - bo) <= 1.0E-6 && dist < bd)) { best = i; bo = off; bd = dist; }
  }
  return best;
}""")
# ---- engine glue (world thread; never throws)
M(rico, r"""public static int sigIdx() { try { return @DST@.getSignatureEnergy(); } catch (Throwable t) { return -1; } }""")
# the meter: + amt, clamped at its max; a max of 0 (no signature weapon in hand) = nothing
M(rico, r"""
public static boolean add(@CAC@ acc, @REF@ r, double amt) {
  int i = sigIdx();
  if (i < 0 || r == null || !(amt > 0.0)) return false;
  try {
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m == null) return false;
    @ESV@ v = m.get(i);
    if (v == null) return false;
    float mx = v.getMax();
    float cur = v.get();
    if (!(mx > 0.0f) || cur >= mx) return false;
    float nv = cur + (float) amt;
    if (nv > mx) nv = mx;
    m.setStatValue(i, nv);
    return true;
  } catch (Throwable t) { warn("add", "the wand signature meter could not be filled (" + t + ")"); return false; }
}""")
# the charge back (no target / off / class lock): the meter full again
M(rico, r"""
public static boolean refund(@CAC@ acc, @REF@ r) {
  int i = sigIdx();
  if (i < 0 || r == null) return false;
  try {
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m == null) return false;
    @ESV@ v = m.get(i);
    if (v == null || !(v.getMax() > 0.0f)) return false;
    m.setStatValue(i, v.getMax());
    REFUNDS = REFUNDS + 1L;
    return true;
  } catch (Throwable t) { warn("refund", "the wand signature charge could not be given back (" + t + ")"); return false; }
}""")
# ArmoryHitSys (Inspect, the hit landed): a wand shot's hit charges the meter (quick +chargeQuick, charged +chargeCharged) while a wand is
# in the shooter's hand; our own hits (bounce / burst / trail - MINE) never reach here (ArmoryHitSys returns on them first)
M(rico, r"""
public static void gain(@CB@ buf, @REF@ target, @DMG@ d, int c) {
  try {
    if (!@PKG@.ArmoryCfg.SIG_ON || d == null || d.isCancelled() || !(d.getAmount() > 0.0f) || c < 1000 || c >= 3000) return;
    Object src = d.getSource();
    if (!(src instanceof @DENT@)) return;
    @REF@ a = ((@DENT@) src).getRef();
    if (a == null || !a.isValid() || (target != null && a.equals(target))) return;
    @PR@ ap = @PKG@.Kunai.prOf(buf, a);
    if (ap == null) return;
    if (@PKG@.ArmoryDefs.wandIndex(@PKG@.Leap.hand(buf, a, ap.getUuid())) < 0) return;
    double amt = c < 2000 ? @PKG@.ArmoryCfg.SIG_GAINQ : @PKG@.ArmoryCfg.SIG_GAINC;
    if (add(buf, a, amt)) GAINS = GAINS + 1L;
  } catch (Throwable t) { warn("gain", "the wand signature charge failed (" + t + ") - that hit charged nothing"); }
}""")
# who the bolt may hit: an enemy (ArmoryTrav.kind 0: alive, a mob with stats, a player only where PvP is on + trav.players, never you /
# party / ally), players only with sig.wand.players, never a protected mob, never a Friendly / Revered / Ignore one (Shadow.attitude)
M(rico, r"""
public static boolean ok(@CAC@ acc, @REF@ t, @REF@ me, java.util.UUID u, boolean pvp) {
  if (t == null || (me != null && t.equals(me))) return false;
  if (@PKG@.ArmoryTrav.kind(acc, t, me, u, pvp) != 0) return false;
  if (@PKG@.Kunai.prOf(acc, t) != null) return @PKG@.ArmoryCfg.SIG_PLAYERS;
  if (@PKG@.Shadow.protect(acc, t)) return false;
  return @PKG@.Shadow.attitude(acc, t, me) <= 1;
}""")
# the candidates around a point: refs + body centres (the hit set left out); the area seam first (Shadow.near)
M(rico, r"""
public static @REF@ pick(@CAC@ acc, @REF@ me, java.util.UUID u, double x, double y, double z, double[] aim, java.util.HashSet done, @PKG@.TravGrid g, boolean pvp) {
  double rng = aim != null ? (double) @PKG@.ArmoryCfg.SIG_RANGE : @PKG@.ArmoryCfg.SIG_BOUNCE;
  java.util.List l = @PKG@.Shadow.near(acc, x, y, z, rng + 2.0);
  int n = l.size();
  @REF@[] rs = new @REF@[n];
  double[] xs = new double[n];
  double[] ys = new double[n];
  double[] zs = new double[n];
  boolean[] okk = new boolean[n];
  for (int k = 0; k < n; k++) {
    Object o = l.get(k);
    okk[k] = false;
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (done != null && done.contains(t)) continue;
    if (!ok(acc, t, me, u, pvp)) continue;
    @VEC@ p = @PKG@.ArmoryTrav.posOf(acc, t);
    if (p == null) continue;
    rs[k] = t;
    xs[k] = p.x;
    ys[k] = p.y + @PKG@.Shadow.height(acc, t) * 0.5;
    zs[k] = p.z;
    okk[k] = g == null || @PKG@.TravMath.clear(g, x, y, z, xs[k], ys[k], zs[k]);
  }
  int i = aim != null ? aimed(xs, ys, zs, okk, x, y, z, aim, rng, (double) @PKG@.ArmoryCfg.SIG_CONE) : nearest(xs, ys, zs, okk, x, y, z, rng);
  return i < 0 ? null : rs[i];
}""")
# the bolt's look: finite blue points every ~0.75 block along the jump (at most 24)
M(rico, r"""
public static void bolt(@CAC@ acc, double ax, double ay, double az, double bx, double by, double bz) {
  double dx = bx - ax;
  double dy = by - ay;
  double dz = bz - az;
  double l = Math.sqrt(dx * dx + dy * dy + dz * dz);
  int n = (int) Math.floor(l / 0.75);
  if (n > 24) n = 24;
  for (int k = 0; k <= n; k++) {
    double f = n == 0 ? 1.0 : (double) k / (double) n;
    @PKG@.ArmoryTrav.particle(PS_BOLT, ax + dx * f, ay + dy * f, az + dz * f, acc);
  }
}""")
# the marker's SPAWN (ArmoryTrav.added, code 13000): the marker goes at once; checks; the chain is queued on this world (TravTick runs it)
M(rico, r"""
public static void marker(@REF@ mk, @LPC@ pc, int c, @ST@ st, @CB@ buf) {
  try { buf.removeEntity(mk, @REMR@.REMOVE); } catch (Throwable t0) { }
  MARKS = MARKS + 1L;
  java.util.UUID u = pc.getCreatorUuid();
  if (u == null) { LAST_WHY = "no caster"; return; }
  @REF@ me = null;
  try { me = ((@ES@) buf.getExternalData()).getRefFromUUID(u); } catch (Throwable t1) { me = null; }
  if (me == null || !me.isValid()) { LAST_WHY = "no caster"; return; }
  if (!@PKG@.ArmoryCfg.SIG_ON) { REFUSED = REFUSED + 1L; LAST_WHY = "signature off"; refund(buf, me); return; }
  String item = @PKG@.Leap.hand(buf, me, u);
  int wi = @PKG@.ArmoryDefs.wandIndex(item);
  if (wi < 0) { REFUSED = REFUSED + 1L; LAST_WHY = "no wand in hand"; return; }
  if (!@PKG@.ArmoryTrav.allowed(u, item)) { REFUSED = REFUSED + 1L; LAST_WHY = "class lock"; refund(buf, me); return; }
  if (@PKG@.ArmoryTrav.dead(buf, me)) { REFUSED = REFUSED + 1L; LAST_WHY = "dead"; return; }
  double[] d = @PKG@.ArmoryTrav.unit(@PKG@.ArmorySpawn.launchVelocity(pc.getSimplePhysicsProvider()));
  if (d == null) d = @PKG@.ArmoryTrav.look(buf, u);
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, me);
  if (d == null || p == null) { REFUSED = REFUSED + 1L; LAST_WHY = "no aim"; refund(buf, me); return; }
  @PKG@.TravWorld tw = @PKG@.TravWorld.get(st);
  if (tw == null || tw.rico.size() >= MAX_CHAINS) { REFUSED = REFUSED + 1L; LAST_WHY = "too many chains"; refund(buf, me); return; }
  double b = base(wi, @PKG@.ArmoryCfg.PART_TUNE, @PKG@.ArmoryCfg.TUNE_W, @PKG@.ArmoryCfg.SIG_FIRST);
  tw.rico.add(new @PKG@.RicoChain(u, item, wi, b, p.x, p.y + EYE, p.z, d, now()));
  CASTS = CASTS + 1L;
  LAST_WHY = "cast";
}""")
# one chain on its world's tick: false = it ended (the caller drops it). The first jump goes to the aimed enemy, every later one to the
# nearest new enemy within the bounce range of the last hit; a dead / gone target is never picked (ArmoryTrav.kind); delay 0 = all at once
M(rico, r"""
public static boolean step(@PKG@.RicoChain ch, @ST@ st, @CB@ buf, long now) {
  if (ch == null) return false;
  if (now - ch.born > MAX_MS) { LAST_WHY = "timed out"; return false; }
  for (int guard = 0; guard < 64; guard++) {
    if (now < ch.next) return true;
    @REF@ me = null;
    try { me = ((@ES@) buf.getExternalData()).getRefFromUUID(ch.u); } catch (Throwable t0) { me = null; }
    if (me == null || !me.isValid()) { LAST_WHY = "the caster left this world"; return false; }
    @WLD@ w = @PKG@.ArmoryTrav.worldOf(buf);
    boolean pvp = @PKG@.ArmoryTrav.pvp(w);
    @PKG@.TravGrid g = @PKG@.ArmoryTrav.grid(w);
    double[] aim = null;
    if (ch.hits == 0) aim = ch.dir;
    @REF@ t = pick(buf, me, ch.u, ch.x, ch.y, ch.z, aim, ch.hit, g, pvp);
    if (t == null) {
      if (ch.hits == 0) {
        MISSES = MISSES + 1L;
        String held = @PKG@.Leap.hand(buf, me, ch.u);
        boolean same = ch.item != null && ch.item.equals(held);          // fix: never refill a meter the player swapped to after the cast
        boolean back = @PKG@.ArmoryCfg.SIG_REFUND && same && refund(buf, me);
        LAST_WHY = "no enemy in your aim" + (back ? " - the charge is back" : (@PKG@.ArmoryCfg.SIG_REFUND && !same ? " - the wand left your hand, the charge is spent" : ""));
        if (back) @PKG@.Kunai.tellRef(buf, me, "No enemy in your aim - your signature charge is kept.");
      } else {
        ENDS_RANGE = ENDS_RANGE + 1L;
        LAST_WHY = "no new enemy within " + @PKG@.TravMath.fmt(@PKG@.ArmoryCfg.SIG_BOUNCE) + " blocks after " + ch.hits + " hits";
      }
      return false;
    }
    @VEC@ tp = @PKG@.ArmoryTrav.posOf(buf, t);
    if (tp == null) return false;
    double tx = tp.x;
    double ty = tp.y + @PKG@.Shadow.height(buf, t) * 0.5;
    double tz = tp.z;
    double amt = amount(ch.base, @PKG@.ArmoryCfg.SIG_FALL, ch.hits);
    bolt(buf, ch.x, ch.y, ch.z, tx, ty, tz);
    ch.hit.add(t);
    ch.hits = ch.hits + 1;
    ch.x = tx;
    ch.y = ty;
    ch.z = tz;
    if (@PKG@.ArmoryTrav.hit(buf, t, me, null, amt)) HITS = HITS + 1L;
    @PKG@.ArmoryTrav.particle(PS_HIT, tx, ty, tz, buf);
    @PKG@.ArmoryTrav.sound(SND_HIT, tx, ty, tz, buf);
    if (ch.hits >= @PKG@.ArmoryCfg.SIG_HITS) { ENDS_MAX = ENDS_MAX + 1L; LAST_WHY = ch.hits + " hits (the most)"; return false; }
    long dl = Math.round(@PKG@.ArmoryCfg.SIG_DELAY * 1000.0);
    if (dl < 0L) dl = 0L;
    ch.next = now + dl;
    LAST_WHY = ch.hits + " hits";
  }
  return true;
}""")
# TravWorld.run (TravTick, once per world tick): every chain of this world
M(rico, r"""
public static void run(@PKG@.TravWorld tw, @ST@ st, @CB@ buf, long now) {
  if (tw == null || tw.rico == null || tw.rico.isEmpty()) return;
  for (int k = tw.rico.size() - 1; k >= 0; k--) {
    @PKG@.RicoChain ch = (@PKG@.RicoChain) tw.rico.get(k);
    boolean keep = false;
    try { keep = step(ch, st, buf, now); }
    catch (Throwable t) { warn("step:" + t.getClass().getName(), "a wand signature ricochet failed (" + t + ") - that bolt ended"); keep = false; }
    if (!keep) tw.rico.remove(k);
  }
}""")
'''
rep('''# ---- ArmoryTravSys.onEntityAdded (SPAWN of one of our projectiles): quick orbs -> range / pierce record; wand charged orb -> burst''',
    RICO_JAVA + '''# ---- ArmoryTravSys.onEntityAdded (SPAWN of one of our projectiles): quick orbs -> range / pierce record; wand charged orb -> burst''')
rep('''  if (c == @PKG@.ArmoryDefs.MK_VAULT_CODE || c == @PKG@.ArmoryDefs.MK_RISE_CODE) { @PKG@.Monk.marker(ref, pc, c, st, buf); return; }     // 0.1.12: the Monk holds
''', '''  if (c == @PKG@.ArmoryDefs.MK_VAULT_CODE || c == @PKG@.ArmoryDefs.MK_RISE_CODE) { @PKG@.Monk.marker(ref, pc, c, st, buf); return; }     // 0.1.12: the Monk holds
  if (c == @PKG@.ArmoryDefs.RICO_CODE) { @PKG@.Rico.marker(ref, pc, c, st, buf); return; }     // 0.1.14: the wand signature
''')
rep('''    int c = @PKG@.ArmoryDefs.pidCode(@PKG@.ArmoryTrav.pidOf(buf, pj));
''', '''    int c = @PKG@.ArmoryDefs.pidCode(@PKG@.ArmoryTrav.pidOf(buf, pj));
    if (c >= 1000 && c < 3000 && chunk != null) @PKG@.Rico.gain(buf, chunk.getReferenceTo(idx), d, c);          // 0.1.14: a wand shot's hit charges the signature
''')

# ---------------------------------------------------------------------------------------------------------------- the plugin + the jar
rep('''  @PKG@.ArmoryLog.info("@VERSION@ " + @PKG@.ArmoryCfg.MONK_TEXT + "; /armory debug monk on|off (admin)");
''', '''  @PKG@.ArmoryLog.info("@VERSION@ " + @PKG@.ArmoryCfg.MONK_TEXT + "; /armory debug monk on|off (admin)");
  @PKG@.ArmoryLog.info("@VERSION@ " + @PKG@.ArmoryCfg.SIG_TEXT);
''')
rep('''"Monk moves: Bo staff hold = Pole-Vault (kicks) + skipping bounds; fist hold = Rising Strike + Plunge Punch (/armory debug monk on|off). "''',
    '''"Monk moves: Bo staff hold = Pole-Vault (kicks) + skipping bounds; fist hold = Rising Strike + Plunge Punch (/armory debug monk on|off). "
                 "Wand signature (fills as your shots hit): a bolt that ricochets through up to 8 enemies. "''')
rep('''    assert sorted(n for n in _names if n in set(MK12_FILES)) == MK12_FILES and len([n for n in _names if "/SkyyArmory_Monk_" in n]) == 17, "0.1.12: the 17 Monk move files"
''', '''    assert sorted(n for n in _names if n in set(MK12_FILES)) == MK12_FILES and len([n for n in _names if "/SkyyArmory_Monk_" in n]) == 17, "0.1.12: the 17 Monk move files"
    assert sorted(n for n in _names if n in set(SIG_FILES + SIG_CHANGED)) == sorted(SIG_FILES + SIG_CHANGED) \\
        and len([n for n in _names if "/SkyyArmory_Wand_Signature" in n or "/SkyyArmory_Wand_Ricochet" in n]) == 4, "0.1.14: the 4 signature files + 7 wands"
''')
rep('''AZ.close()''', '''print("0.1.14 wand signature: %d rows (Server Setup > Armory > Wand + signature, sig.wand.*) + 1 read-only row; meter %d on %d wands; marker %s "
      "(code %d); Rico + RicoChain (the TravTick chain), the charge in ArmoryHitSys" % (len(CFG_SIG), SIG_MAX, len(SIG_WANDS), RICO_MARK, RICO_CODE))
AZ.close()''')

with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(s.replace(LF, NL))
print("wrote %s" % os.path.relpath(DST, ROOT))

# ================================================================================================================ the harness
traw = open(TSRC, encoding="utf8", newline="").read()
TNL = CR + LF if (CR + LF) in traw else LF
ts = traw.replace(CR + LF, LF)


def hrep(old, new, count=1):
    global ts
    n = ts.count(old)
    assert n == count, "harness anchor count %d (want %d): %s" % (n, count, old[:140])
    ts = ts.replace(old, new)


hrep('"""SkyyArmory 0.1.13 - test harness. GENERATED by tools/armory_0_1_13_patch.py from test_skyyarmory_0.1.12.py - edit the patch, never this file.',
     '''"""SkyyArmory 0.1.14 - test harness. GENERATED by tools/armory_0_1_14_patch.py from test_skyyarmory_0.1.13.py - edit the patch, never this file.
Run: python SkyyArmory/test_skyyarmory_0.1.14.py --dir tools/dev/scratch/<task>/harness   (--no-set skips the one-JVM SET run, --keep keeps it)
Every 0.1.13 check still runs on the 0.1.13 shape: JZ14 = the real 0.1.14 jar; JZ = the jar AS THE 0.1.13 CHECKS KNOW IT - the 4 new
signature files hidden, the 7 changed wand items + the lang read as the 0.1.13 jar's bytes, the manifest = the real one with the 0.1.13
description (P16 proves the real files are exactly the planned change of those bytes); the classes are the real 0.1.14 ones (A / X / T / V /
every Java path, the 2 new classes Rico + RicoChain included); R16e now compares 0.1.12 -> 0.1.13 (history), R17g 0.1.13 -> 0.1.14.
NEW P16 (Python) + R17 (JVM, after R16) EXECUTE every 0.1.14 path:
  P16  the 4 new files (the root = the vanilla crossbow BigArrow root shape, the gate + spend = the BigArrow StatsCondition / ChangeStat
       shape, the launch, the marker = the blink marker shape), the 7 wands = the 0.1.13 bytes + Ability1 + the sword's meter (20) + the
       sword's ready look only, the lang = 7 descriptions + the signature sentence, nothing else changed; no one-entry Parallel in the whole
       real jar (+ a negative control); the Ability1 walk of every wand reaches the gate, the spend and the marker launch; SkyySkills'
       Weapon_Wand_Wood (NOTE).
  R17  a: THE ENGINE ASSET VALIDATORS on the 4 new + 7 changed assets (+ every inline step); b: into the stores, RootInteraction.build() of
       the Ability1 root = StatsCondition -> ChangeStat -> LaunchProjectile, 0 missing; c: THE ENERGY GATE EXECUTED - the engine's own
       StatsConditionInteraction.canAfford (the decoded real file) on the caster's real EntityStatMap with the wand's meter (max 20): full =
       yes, 19 / 0 = no; d: the Rico maths (the 8-hit damage series, the base from the wand's charged shot + tune, nearest / aimed with
       ties, range and cone edges); e: the ricochet on the engine stand-ins through ArmoryTrav.added -> Rico.marker and TravWorld.run ->
       Rico.run: 8 TARGETS (10 mobs in a row: exactly 8 hits, never twice, 132 -> 63.14, one hit per 0.15 s), OUT OF RANGE (10.5 blocks:
       stops after 1; 10.0: hit), PARTY / PVP (PvP off: the stranger never; on: the stranger yes, the party member never; the players row
       off: no player), DEAD TARGET MID-CHAIN (skipped, the next jump from where the dead one stood), a wall (no line of sight), a friendly
       / an invulnerable mob never, no enemy in aim = the charge back (the row off: spent), off / class lock / no wand = refused (+ refund),
       the Wood wand's base, the caster leaving ends the chain, TravWorld idle only after the chain; f: THE CHARGE through ArmoryHitSys -
       quick hit +1, charged hit +2, clamped at 20, no wand in hand / our own MINE hit / a cancelled hit = nothing; g: vs the 0.1.13 jar
       method by method.

0.1.13 harness: SkyyArmory 0.1.13 - test harness. GENERATED by tools/armory_0_1_13_patch.py from test_skyyarmory_0.1.12.py - edit the patch, never this file.''')
hrep('VERSION = "0.1.13"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.13 SkyyArmory"',
     'VERSION = "0.1.14"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.14 SkyyArmory"')
hrep('os.path.join(SCRATCH_ROOT, "armory0113", "harness")', 'os.path.join(SCRATCH_ROOT, "armory0114", "harness")')
hrep('raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.13.py', 'raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.14.py')
hrep('Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.13"))', 'Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.14"))')
hrep('"[SkyyArmory] 0.1.13 ready" in m_', '"[SkyyArmory] 0.1.14 ready" in m_')
hrep('"0.1.13 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_', '"0.1.14 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_')
hrep('"0.1.13 crossbow grapple: grapple on" in m_', '"0.1.14 crossbow grapple: grapple on" in m_')
hrep('"0.1.13 monk moves on - Pole-Vault (Bo hold): lunge 3 in 0.2 s, 4.5 up x 7 forward (push x2.1)" in m_',
     '"0.1.14 monk moves on - Pole-Vault (Bo hold): lunge 3 in 0.2 s, 4.5 up x 7 forward (push x2.1)" in m_')
hrep('"51 of 51 items, 356 of 356 interactions, 65 of 65 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.13 SkyyArmory" in str(r[1])',
     '"51 of 51 items, 358 of 358 interactions, 66 of 66 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.14 SkyyArmory" in str(r[1])')
hrep('''    check(len(names) == 51, "A: 51 classes (44 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap + 0.1.6's 6 book / kunai + 0.1.7's 2 stunlock + 0.1.8's Shadow + 0.1.9's ArmoryTree + 0.1.12's MonkState / Monk / ArmoryCmd / ArmoryDbgCmd + 7 kit)")''',
     '''    check(len(names) == 53, "A: 53 classes (46 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap + 0.1.6's 6 book / kunai + 0.1.7's 2 stunlock + 0.1.8's Shadow + 0.1.9's ArmoryTree + 0.1.12's MonkState / Monk / ArmoryCmd / ArmoryDbgCmd + 0.1.14's Rico / RicoChain + 7 kit)")''')
# the T start lines: + the signature line, twice
hrep('''    print("T. real setup() twice on a copy of the live data''', '''    sig_line = [m_ for lv_, m_ in records()[n_log0:] if "0.1.14 wand signature on - the signature key when the meter is full (20; quick-shot hit +1, charged hit +2)" in m_]
    check(len(sig_line) == 2 and "up to 8 enemies" in sig_line[0] and "first hit 1.5x the charged shot, -10% a bounce" in sig_line[0],
          "T (0.1.14): each setup() prints the wand signature line with the defaults: %s" % sig_line[:1])
    print("T. real setup() twice on a copy of the live data''')

# ---- the jar as the 0.1.13 checks know it
hrep('''JZ = zipfile.ZipFile(JAR)
# 0.1.13: JZ13 = the real 0.1.13 jar (P15 / R16);''', '''JZ = zipfile.ZipFile(JAR)
# 0.1.14: JZ14 = the real 0.1.14 jar (P16 / R17); from here on JZ is the jar AS THE 0.1.13 CHECKS KNOW IT: the 4 new signature files hidden,
# the 7 changed wand items + the lang read as the 0.1.13 jar's bytes, the manifest = the real one with the 0.1.13 description - P16 proves
# the real files are exactly the planned change of those bytes; every class = the real jar (Rico / RicoChain included)
JZ14 = JZ
OLD113 = os.path.join(HERE, "SkyyArmory-0.1.13.jar")
if not os.path.isfile(OLD113):
    raise SystemExit("the 0.1.14 harness needs SkyyArmory-0.1.13.jar (the base, the SET pin) next to it: %s" % OLD113)
OZ113 = zipfile.ZipFile(OLD113)
SIG14_NEW = sorted(n_ for n_ in JZ14.namelist() if "/SkyyArmory_Wand_Signature" in n_ or "/SkyyArmory_Wand_Ricochet" in n_)
SIG14_CHG = sorted("Server/Item/Items/Weapon/Wand/Weapon_Wand_%s.json" % m_ for m_ in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"))
SIG14_LANG = "Server/Languages/en-US/server.lang"
SIG14_CLS = ["com/skyy/armory/Rico.class", "com/skyy/armory/RicoChain.class"]


class Z113(object):
    """the 0.1.14 jar as the 0.1.13 checks know it (read only)"""
    def __init__(self, real, old, hide, oldfiles):
        self.real, self.old, self.hide, self.oldfiles = real, old, set(hide), set(oldfiles)

    def namelist(self):
        return [n_ for n_ in self.real.namelist() if n_ not in self.hide]

    def read(self, n_):
        if n_ in self.hide:
            raise KeyError(n_)
        if n_ == "manifest.json":
            m_ = json.loads(self.real.read(n_).decode("utf-8"))
            m_["Description"] = json.loads(self.old.read(n_).decode("utf-8"))["Description"]
            return json.dumps(m_, indent=2).encode("utf-8")
        return self.old.read(n_) if n_ in self.oldfiles else self.real.read(n_)

    def close(self):
        self.real.close()
        self.old.close()


JZ = Z113(JZ14, OZ113, SIG14_NEW, SIG14_CHG + [SIG14_LANG])
# 0.1.13: JZ13 = the real 0.1.13 jar (P15 / R16);''')
# the history checks that list new classes / names: the 2 new 0.1.14 classes are not theirs
hrep('''_p15nn, _p15on = set(JZ13.namelist()), set(OZ112.namelist())''', '''_p15nn, _p15on = set(JZ13.namelist()) - set(SIG14_CLS), set(OZ112.namelist())          # 0.1.14: Rico / RicoChain are P16's''')
hrep('''    nn_ = JREAL.namelist()
''', '''    nn_ = [n_ for n_ in JREAL.namelist() if n_ not in SIG14_CLS]          # 0.1.14: Rico / RicoChain are R17's
''')
hrep('''    MN16, MO16 = methods_of(JAR), methods_of(OLD112)''', '''    MN16, MO16 = methods_of(OLD113), methods_of(OLD112)          # 0.1.14: R16e = the 0.1.13 round's compare (history); R17g = 0.1.13 -> 0.1.14''')
hrep('''                ms_["%s%s" % (m_.getName(), m_.getSignature())] = t_.replace("0.1.13", "V").replace("0.1.12", "V").replace("0.1.11", "V")''',
     '''                ms_["%s%s" % (m_.getName(), m_.getSignature())] = t_.replace("0.1.14", "V").replace("0.1.13", "V").replace("0.1.12", "V").replace("0.1.11", "V")''')
# ---- L: the 2 new interactions + the marker go into the stores before the pack check (it counts every id the jar ships)
hrep('''    CHK = JClass(PKG + "ArmoryCheck")
    r = CHK.packCheck()
''', '''    bad14l = []          # 0.1.14: the signature interactions + the marker (the real files) into the stores - the pack check counts them
    for c_, pre_ in ((INTc, "Server/Item/Interactions/"), (PRJc, "Server/Projectiles/")):
        objs_ = []
        for n_ in SIG14_NEW:
            if n_.startswith(pre_):
                o_, w_ = dec(c_, os.path.basename(n_)[:-5], JZ14.read(n_).decode("utf-8"))
                if o_ is None or w_:
                    bad14l.append("%s: %s" % (n_, w_))
                else:
                    objs_.append(o_)
        load(c_, objs_, PACK)
    check(not bad14l and len(SIG14_NEW) == 4, "L (0.1.14): the 2 signature interactions + the marker decode (no unknown key) and go into the stores: %s" % bad14l[:3])
    CHK = JClass(PKG + "ArmoryCheck")
    r = CHK.packCheck()
''')
# ---- K: the 12 new rows + 1 read-only row
hrep('''                 "plunge.damage", "plunge.radius"]      # 0.1.12 the Monk moves
''', '''                 "plunge.damage", "plunge.radius"]      # 0.1.12 the Monk moves
    NEW_ROWS += ["sig.wand." + k_ for k_ in ("enabled", "firstHit", "falloff", "maxHits", "bounceRange", "aimRange", "aimCone", "bounceDelay",
                                             "chargeQuick", "chargeCharged", "players", "refundMiss")]      # 0.1.14 the wand signature
''')
hrep('''          and len(keys) == 10 + NN + 14 + 8 + 8 + 5 + 2 + 2 + 17 + 20 + 3 + 2,          # 0.1.12: + fixed.monk.keys / fixed.monk.debug''',
     '''          and len(keys) == 10 + NN + 14 + 8 + 8 + 5 + 2 + 2 + 17 + 20 + 3 + 2 + 1,          # 0.1.12: + fixed.monk.keys / fixed.monk.debug; 0.1.14: + fixed.sig.wand''')

# ---- P16 (Python): the 0.1.14 files before the JVM part
P16 = r"""# ============================================================================================================ P16. 0.1.14 the wand signature (pure files)
S14_ROOT, S14_CAST, S14_LAUNCH, S14_MARK = "SkyyArmory_Wand_Signature", "SkyyArmory_Wand_Signature_Cast", "SkyyArmory_Wand_Signature_Launch", "SkyyArmory_Wand_Ricochet"
S14_PATHS = {"root": "Server/Item/RootInteractions/Weapons/Wand/SkyyArmory/%s.json" % S14_ROOT,
             "cast": "Server/Item/Interactions/Weapons/Wand/SkyyArmory/%s.json" % S14_CAST,
             "launch": "Server/Item/Interactions/Weapons/Wand/SkyyArmory/%s.json" % S14_LAUNCH,
             "mark": "Server/Projectiles/Player/SkyyArmory/%s.json" % S14_MARK}
S14 = dict((k_, json.loads(JZ14.read(p_).decode("utf-8"))) for k_, p_ in S14_PATHS.items())
check(SIG14_NEW == sorted(S14_PATHS.values()) and not [i_ for i_ in (S14_ROOT, S14_CAST, S14_LAUNCH, S14_MARK) if ahas("int", i_) or ahas("root", i_) or ahas("prj", i_)],
      "P16: 4 new files (the Ability1 root, the gate + spend, the launch, the marker); no id in Assets.zip: %s" % SIG14_NEW)
_vxr16 = aj("root", "Root_Weapon_Crossbow_Signature_BigArrow")
_vxs16 = aj("int", "Weapon_Crossbow_Signature_BigArrow")["Next"]
check(S14["root"] == dict(_vxr16, Interactions=[S14_CAST]) and sorted(_vxr16) == ["Interactions", "RequireNewClick", "Tags"]
      and S14["cast"] == {"Type": "StatsCondition", "Costs": {"SignatureEnergy": 100}, "ValueType": "Percent",
                          "Next": {"Type": "ChangeStat", "StatModifiers": {"SignatureEnergy": -100}, "ValueType": "Percent", "Next": S14_LAUNCH}}
      and _vxs16["Type"] == "StatsCondition" and _vxs16["Costs"] == S14["cast"]["Costs"] and _vxs16["ValueType"] == "Percent"
      and _vxs16["Next"]["Type"] == "ChangeStat" and _vxs16["Next"]["StatModifiers"]["SignatureEnergy"] == -100 and _vxs16["Next"]["ValueType"] == "Percent",
      "P16: the root = the vanilla crossbow BigArrow root (RequireNewClick, Tags Attack Ranged) naming our gate; the gate = the vanilla signature "
      "gate (StatsCondition SignatureEnergy 100 %%) -> the spend (ChangeStat -100 %%) -> our launch: %s" % S14["cast"])
check(S14["launch"] == {"Type": "LaunchProjectile", "RunTime": 0.25, "Effects": {"ItemAnimationId": "CastLeftCharged", "WorldSoundEventId": "SFX_Staff_Ice_Shoot"},
                        "ProjectileId": S14_MARK} and ahas("sound", "SFX_Staff_Ice_Shoot")
      and S14["mark"] == J[J_PRJ["SkyyArmory_Blink_Iron"]] and float(S14["mark"]["Damage"]) == 0.0,
      "P16: the launch = the charged cast pose + the vanilla SFX_Staff_Ice_Shoot + the marker; the marker = the blink marker shape (invisible, Damage 0)")
_sw16 = aresolve("item", "Template_Weapon_Sword")
_wch16 = []
for n_ in SIG14_CHG:
    o_, r_ = json.loads(OZ113.read(n_).decode("utf-8")), json.loads(JZ14.read(n_).decode("utf-8"))
    w_ = copy.deepcopy(o_)
    w_["Interactions"]["Ability1"] = S14_ROOT
    w_["Weapon"] = {"EntityStatsToClear": ["SignatureEnergy"], "StatModifiers": {"SignatureEnergy": [{"Amount": 20, "CalculationType": "Additive"}]}}
    w_["ItemAppearanceConditions"] = _sw16["ItemAppearanceConditions"]
    if r_ != w_ or o_["Weapon"] != {} or "Ability1" in o_["Interactions"] or sorted(r_["Interactions"]) != ["Ability1", "Primary", "Secondary"]:
        _wch16.append(n_)
check(not _wch16 and _sw16["Weapon"]["StatModifiers"]["SignatureEnergy"][0]["Amount"] == 20 and len(SIG14_CHG) == 7,
      "P16: each of the 7 metal wands = its 0.1.13 file + Ability1 (our root) + the vanilla sword's meter (SignatureEnergy +20, cleared on swap) "
      "+ the sword's ready look - the Primary / Secondary roots and every other field unchanged: %s" % _wch16)
lo16 = OZ113.read(SIG14_LANG).decode("utf-8").split("\n")
ln16 = JZ14.read(SIG14_LANG).decode("utf-8").split("\n")
lch16 = [k_ for k_ in range(max(len(lo16), len(ln16))) if k_ >= len(lo16) or k_ >= len(ln16) or lo16[k_] != ln16[k_]]
lbad16 = [k_ for k_ in lch16 if k_ >= len(lo16) or k_ >= len(ln16) or not lo16[k_].endswith(" Right click: block.") or ln16[k_] !=
          lo16[k_][:-len(" Right click: block.")] + " Signature (fills as your shots hit): a bolt that ricochets through up to 8 enemies. Right click: block."]
check(len(ln16) == len(lo16) and len(lch16) == 7 and not lbad16 and all(".Weapon_Wand_" in ln16[k_] for k_ in lch16),
      "P16: the lang = 0.1.13's with only the 7 metal wand descriptions telling the signature: %s" % [ln16[k_] for k_ in lbad16][:2])
_n16, _o16 = set(JZ14.namelist()), set(OZ113.namelist())
_d16 = sorted(n_ for n_ in _n16 & _o16 if not n_.endswith(".class") and n_ != "manifest.json" and JZ14.read(n_) != OZ113.read(n_))
_m16 = json.loads(JZ14.read("manifest.json").decode("utf-8")), json.loads(OZ113.read("manifest.json").decode("utf-8"))
check(sorted(_n16 - _o16) == sorted(SIG14_NEW + SIG14_CLS) and not (_o16 - _n16) and _d16 == sorted(SIG14_CHG + [SIG14_LANG])
      and dict(_m16[0], Version=None, Name=None, Description=None) == dict(_m16[1], Version=None, Name=None, Description=None)
      and _m16[0]["Version"] == VERSION and _m16[0]["Description"].replace("Wand signature (fills as your shots hit): a bolt that ricochets through up to 8 enemies. ", "") == _m16[1]["Description"],
      "P16: vs SkyyArmory-0.1.13.jar - new = the 4 signature files + Rico.class + RicoChain.class, none gone, changed non-class files = the 7 "
      "wands + the lang, the manifest = its version + one description sentence: %s %s" % (sorted(_n16 ^ _o16)[:6], _d16[:4]))
_op16 = []


def _p16walk(o_, n_):
    if isinstance(o_, dict):
        if o_.get("Type") == "Parallel" and (not isinstance(o_.get("Interactions"), list) or len(o_["Interactions"]) < 2):
            _op16.append(n_)
        for v_ in o_.values():
            _p16walk(v_, n_)
    elif isinstance(o_, list):
        for v_ in o_:
            _p16walk(v_, n_)


_jn16 = [n_ for n_ in JZ14.namelist() if n_.startswith("Server/") and n_.endswith(".json")]
for n_ in _jn16:
    _p16walk(json.loads(JZ14.read(n_).decode("utf-8")), n_)
_p16walk({"Type": "Simple", "Next": {"Type": "Parallel", "Interactions": [{"Interactions": ["X"]}]}}, "NEG")
_negp16, _op16 = [x_ for x_ in _op16 if x_ == "NEG"], [x_ for x_ in _op16 if x_ != "NEG"]
check(not _op16 and _negp16 == ["NEG"] and len(_jn16) > 500,
      "P16 (0.1.10's rule on the WHOLE real 0.1.14 jar): every Parallel in all %d JSON files has 2+ entries (NEGATIVE CONTROL: a one-entry "
      "Parallel is caught): %s" % (len(_jn16), _op16[:4]))
_wk16 = []
for n_ in SIG14_CHG:
    it_ = json.loads(JZ14.read(n_).decode("utf-8"))
    r_ = S14["root"] if it_["Interactions"].get("Ability1") == S14_ROOT else None
    c_ = S14["cast"] if r_ is not None and r_["Interactions"] == [S14_CAST] else None
    l_ = S14["launch"] if c_ is not None and c_["Next"]["Next"] == S14_LAUNCH else None
    if l_ is None or l_["ProjectileId"] != S14_MARK or "Mana" in json.dumps([r_, c_, l_]):
        _wk16.append(n_)
check(not _wk16, "P16: from the Ability1 key of all 7 wands the walk reaches the gate (SignatureEnergy 100 %%), the spend and the marker launch - "
                 "no Mana anywhere in it: %s" % _wk16)
SK14W = SK_ITEMS.get("Weapon_Wand_Wood")
if SK14W is not None:
    print("P16. NOTE the pinned SkyySkills %s ships Weapon_Wand_Wood (Interactions %s) and loads after SkyyArmory: the Wood wand gets the "
          "signature when SkyySkills names Ability1 %s + the meter (or hands the id over) - SkyyArmory's Java already serves it (wand index 0)" % (
              SKILLS_PIN, sorted(SK14W.get("Interactions", {})), S14_ROOT))
print("P16. 0.1.14: 4 new files (the vanilla signature shapes), 7 wands + 7 descriptions changed, nothing else; no one-entry Parallel; every "
      "wand's Ability1 reaches the gate, the spend and the marker")
"""
hrep('''PY_OKS, PY_FAILS = OKS[0], len(FAILS)
''', P16 + '''PY_OKS, PY_FAILS = OKS[0], len(FAILS)
''')

# ---- R17 (JVM): after R16, before L2 (L2 changes the store)
R17 = r'''    # ============================================================================ R17. 0.1.14 THE WAND SIGNATURE - every new path EXECUTED
    from jpype import JLong
    RC, RCH = JClass(PKG + "Rico"), JClass(PKG + "RicoChain")
    # R17a THE ENGINE ASSET VALIDATORS on the 4 new + 7 changed assets (the REAL files) + every inline step
    # (the wands name the new root: the 4 new assets are validated and go into the stores FIRST; a vanilla asset the bare JVM does not load -
    # e.g. the sword's ModelVFX Sword_Signature_Status, a kind R14's list lacks - is a test-bed line when Assets.zip has it)
    KNOWN14.update(os.path.basename(n_).rsplit(".", 1)[0] for n_ in AZN if n_.startswith("Server/"))
    val17, objs17 = [], {}
    for n_ in SIG14_NEW + ["LOAD"] + SIG14_CHG:
        if n_ == "LOAD":
            for c_ in (INTc, PRJc, ROOTc):
                load(c_, [o_ for k_, o_ in objs17.get(c_, [])], PACK)
            continue
        c_ = INTc if n_.startswith("Server/Item/Interactions/") else (PRJc if n_.startswith("Server/Projectiles/") else
                                                                       (ROOTc if n_.startswith("Server/Item/RootInteractions/") else ITMc))
        o_, w_ = validate14(c_, os.path.basename(n_)[:-5], JZ14.read(n_).decode("utf-8"))
        if o_ is None or w_:
            val17.append("%s: %s" % (n_, w_))
            continue
        objs17.setdefault(c_, []).append((os.path.basename(n_)[:-5], o_))
    check(not val17 and sum(len(v_) for v_ in objs17.values()) == 11,
          "R17a: the ENGINE ASSET VALIDATORS pass on all 11 new / changed assets (the root, the gate + spend, the launch, the marker, the 7 wands) "
          "and every inline step in them (decode, the codec's full validate pass, logOrThrowValidatorExceptions, contained assets): %s" % val17[:4])
    # R17b the real files into the stores, then RootInteraction.build() of the Ability1 root
    keep17 = HashMap(pbu)          # the stand-in players have no packet handler: no broadcast while the items load (the R16d way)
    pbu.clear()
    ld17 = [load(c_, [o_ for k_, o_ in objs17.get(c_, [])], PACK) for c_ in (INTc, PRJc, ROOTc, ITMc)]
    pbu.putAll(keep17)
    wi17 = ITMc.getAssetMap().getAsset("Weapon_Wand_Iron")
    wint17 = dict((str(k_), str(v_)) for k_, v_ in dict(wi17.getInteractions()).items()) if wi17 is not None else {}
    nm17a = len([m_ for lv_, m_ in records() if "Missing interaction" in m_])
    res17 = compile_root(S14_ROOT)
    nm17b = len([m_ for lv_, m_ in records() if "Missing interaction" in m_])
    cls17 = [cn_ for cn_, iid_ in res17["ops"] if iid_ is not None]
    check(not res17["bad"] and nm17b == nm17a and ("StatsConditionInteraction", S14_CAST) in res17["ops"] and "ChangeStatInteraction" in cls17
          and ("LaunchProjectileInteraction", S14_LAUNCH) in res17["ops"] and cls17.index("StatsConditionInteraction") < cls17.index("ChangeStatInteraction")
          < cls17.index("LaunchProjectileInteraction") and str(ITMc.getAssetMap().getAssetPack("Weapon_Wand_Iron")) == PACK and ld17 == [True] * 4
          and wint17.get("Ability1") == S14_ROOT and wint17.get("Primary") == "SkyyArmory_Wand_Primary_Iron" and wi17.getWeapon() is not None,
          "R17b: RootInteraction.build() of %s on the real stores = StatsCondition (the gate) -> ChangeStat (the spend) -> LaunchProjectile (the "
          "marker), 0 missing interactions; the 7 real wands load into the store from our pack (Iron: Ability1 = our root, Primary kept, a "
          "Weapon block): %s %s %s %s" % (S14_ROOT, ld17, wint17, res17["bad"][:2], res17["ops"][:8]))
    # R17c THE ENERGY GATE EXECUTED: the engine's StatsConditionInteraction.canAfford on the decoded real file + the caster's real EntityStatMap
    # with the wand's meter (the item's Weapon StatModifiers = a MAX ADDITIVE 20 modifier, the vanilla way)
    SIGI = int(DST.getSignatureEnergy())
    SMO17 = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MT17 = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CT17 = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    max17a = float(mc.get(SIGI).getMax())
    mc.putModifier(SIGI, "armorytest-sig", SMO17(MT17.MAX, CT17.ADDITIVE, JFloat(20.0)))
    cast17o = dict(objs17.get(INTc, [])).get(S14_CAST)
    SCIc = JClass(PI + "none.StatsConditionInteraction")
    ca17 = SCIc.class_.getDeclaredMethod("canAfford", REFc.class_, JClass("com.hypixel.hytale.component.ComponentAccessor").class_)
    ca17.setAccessible(True)

    def afford17(v_):
        mc.setStatValue(SIGI, JFloat(v_))
        return bool(ca17.invoke(cast17o, JArray(JClass("java.lang.Object"))([rc, tst])))
    gate17 = [afford17(20.0), afford17(19.0), afford17(0.0)]
    _vg17 = aj("int", "Weapon_Crossbow_Signature_BigArrow")["Next"]          # the vanilla gate itself (its Next = the vanilla Replace chain, left out)
    vsig17, wsig17 = validate14(INTc, "SkyyArmoryHarness_VanillaGate", json.dumps({"Type": _vg17["Type"], "Costs": _vg17["Costs"], "ValueType": _vg17["ValueType"]}))
    gate17v = None
    if vsig17 is not None:
        mc.setStatValue(SIGI, JFloat(20.0))
        gate17v = bool(ca17.invoke(vsig17, JArray(JClass("java.lang.Object"))([rc, tst])))
    check(cast17o is not None and SCIc.class_.isInstance(cast17o) and max17a == 0.0 and float(mc.get(SIGI).getMax()) == 20.0
          and gate17 == [True, False, False] and gate17v is True,
          "R17c: THE ENERGY GATE - the engine's own StatsConditionInteraction.canAfford on our decoded gate and the caster's real stat map: no wand "
          "= a 0 meter; with the wand's meter (max 20) a FULL meter passes, 19 / 0 do not (the vanilla crossbow BigArrow gate, decoded the same "
          "way, passes the full meter too): %s / vanilla %s" % (gate17, gate17v))
    # R17d the pure maths
    ACfg.useDefaults()
    tw50 = JArray(JDouble)([100.0, 100.0, 50.0, 100.0, 100.0, 100.0, 100.0, 100.0])
    ser17 = [round(float(RC.amount(132.0, 10, n_)), 4) for n_ in range(8)]
    base17 = [float(RC.base(2, True, ACfg.TUNE_W, 1.5)), float(RC.base(0, True, ACfg.TUNE_W, 1.5)), float(RC.base(2, True, tw50, 1.5)),
              float(RC.base(2, False, tw50, 1.5)), float(RC.base(0, True, JArray(JDouble)([50.0] * 8), 1.5)), float(RC.base(6, True, ACfg.TUNE_W, 1.5)),
              float(RC.base(-1, True, ACfg.TUNE_W, 1.5)), float(RC.base(2, True, ACfg.TUNE_W, 0.0)), round(float(RC.amount(132.0, 0, 7)), 4),
              round(float(RC.amount(132.0, 100, 1)), 4), float(RC.amount(-5.0, 10, 0))]
    D_ = lambda xs: JArray(JDouble)([float(x_) for x_ in xs])
    B_ = lambda xs: JArray(JBoolean)([bool(x_) for x_ in xs])
    near17 = [int(RC.nearest(D_([5, 3, 3, 12]), D_([0, 0, 0, 0]), D_([0, 0, 0, 0]), B_([1, 1, 1, 1]), 0.0, 0.0, 0.0, 10.0)),
              int(RC.nearest(D_([5, 3, 3, 12]), D_([0, 0, 0, 0]), D_([0, 0, 0, 0]), B_([1, 0, 1, 1]), 0.0, 0.0, 0.0, 10.0)),
              int(RC.nearest(D_([5, 3, 3, 12]), D_([0, 0, 0, 0]), D_([0, 0, 0, 0]), B_([1, 1, 1, 1]), 0.0, 0.0, 0.0, 2.5)),
              int(RC.nearest(D_([10, 10.01]), D_([0, 0]), D_([0, 0]), B_([1, 1]), 0.0, 0.0, 0.0, 10.0)),
              int(RC.nearest(D_([10.01]), D_([0]), D_([0]), B_([1]), 0.0, 0.0, 0.0, 10.0))]
    ax_ = JArray(JDouble)([1.0, 0.0, 0.0])
    aim17 = [int(RC.aimed(D_([10, 5, 8, 30, 0.1]), D_([0, 1.2, 0, 0, 0]), D_([0, 0, 0, 0, 0]), B_([1, 1, 1, 1, 1]), 0.0, 0.0, 0.0, ax_, 24.0, 30.0)),
             int(RC.aimed(D_([5]), D_([1.2]), D_([0]), B_([1]), 0.0, 0.0, 0.0, ax_, 24.0, 30.0)),          # 13.5 deg off: inside 15
             int(RC.aimed(D_([5]), D_([1.4]), D_([0]), B_([1]), 0.0, 0.0, 0.0, ax_, 24.0, 30.0)),          # 15.6 deg off: outside
             int(RC.aimed(D_([5]), D_([1.4]), D_([0]), B_([1]), 0.0, 0.0, 0.0, ax_, 24.0, 40.0)),          # a 40 deg cone takes it
             int(RC.aimed(D_([-5]), D_([0]), D_([0]), B_([1]), 0.0, 0.0, 0.0, ax_, 24.0, 180.0)),          # behind you: never (180 = 90 a side)
             int(RC.aimed(D_([30]), D_([0]), D_([0]), B_([1]), 0.0, 0.0, 0.0, ax_, 24.0, 30.0))]           # past the range
    want_ser = [round(132.0 * 0.9 ** n_, 4) for n_ in range(8)]
    check(ser17 == want_ser and base17 == [132.0, 37.5, 66.0, 132.0, 37.5, 787.5, 0.0, 0.0, 132.0, 0.0, 0.0] and near17 == [1, 2, -1, 0, -1]
          and aim17 == [2, 0, -1, 0, -1, -1],
          "R17d: the Rico maths - hit n = base x 0.9^n (Iron: 132, 118.8 ... 63.14); base = the wand's charged shot x tune.wand x firstHit "
          "(Iron 88 x 1.5 = 132, Wood 25 x 1.5 = 37.5 with tune.wand ignored for the Wood hold, Iron at 50 %% = 66, tune off = 132, Mithril 787.5, "
          "unknown wand / firstHit 0 = 0); falloff 0 = flat, 100 = nothing after the first; nearest (ties = the first listed, the range edge "
          "inclusive), aimed (angle first, ties = the nearer; the cone edge; behind; out of range): %s %s %s %s" % (ser17, base17, near17, aim17))
    # R17e THE RICOCHET on the engine stand-ins (ArmoryTrav.added -> Rico.marker, TravWorld.run -> Rico.run)
    ACfg.useDefaults()
    ACfg.TRAV_FX = True
    PS17 = ArrayList()
    AT.PSEEN = PS17
    grid17_old, near17_old = AT.GRID, AT.NEAR
    AT.GRID = Grid(world_fn())
    hand17, look17 = LP.HAND, LP.LOOK
    LP.HAND, LP.LOOK = HashMap(), None
    LP.HAND.put(cu, "Weapon_Wand_Iron")
    NEAR17 = []

    @JImplements("java.util.function.Function")
    class Near17:
        @JOverride
        def apply(self, o):
            l_ = ArrayList()
            for r_ in NEAR17:
                l_.add(r_)
            return l_
    AT.NEAR = Near17()
    for k_ in ("class:fn:allowed", "class:fn:ally"):
        br.remove(k_)
    br.put("party:fn:members", Members())          # rp (player 2) = your party
    wcfg.setPvpEnabled(False)
    tc17_old = dict((int(r_.getIndex()), comp(r_, TCc.getComponentType())) for r_ in (rc, rp, rs))
    put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    T17 = [1950000000000]

    def clk17(ms_=0):
        T17[0] += ms_
        RC.CLOCK = JLong(T17[0])
        return T17[0]

    def cast17(i_):
        mk_, pc_ = launched(S14_MARK, i_, 0.5, 65.6, 0.5)          # aimed along +x (the launch velocity), from the eye height
        AT.added(mk_, pc_, int(ADefs.pidCode(S14_MARK)), tst, tbuf)
        return mk_

    def tick17(ms_):
        tw_ = TW.of(tst)
        if tw_ is not None:
            tw_.run(tst, tbuf, clk17(ms_))
        else:
            clk17(ms_)

    def hits17():
        return [(e_[0], round(e_[1], 3)) for e_ in events() if e_[2] == "EntitySource"]

    def fresh17():
        reset_buf()
        TW.ALL.clear()
        clk17(1000)

    def row17(i0_, xs_, y_=64.7):          # mobs whose body centre sits at your eye height (65.6): every one dead ahead
        return [mob(i0_ + k_, x_, y_, 0.5, (0.8, 1.8, 0.8)) for k_, x_ in enumerate(xs_)]
    w17 = lambda n_: round(132.0 * 0.9 ** n_, 3)
    # -- (1) 8 TARGETS: 10 mobs in a row 3 blocks apart
    fresh17()
    r8 = row17(1700, [6.0 + 3.0 * k_ for k_ in range(10)])
    NEAR17[:] = r8 + [rc]
    c0_, e0_ = int(RC.CASTS), int(RC.ENDS_MAX)
    mk17 = cast17(1790)
    tw17 = TW.of(tst)
    q17 = (mk17 in list(TBf.REMOVED), tw17 is not None and int(tw17.rico.size()) == 1, tw17 is not None and not bool(tw17.idle()), int(RC.CASTS) - c0_)
    per17 = []
    for k_ in range(18):
        n0_ = len(hits17())
        tick17(0 if k_ == 0 else 75)
        per17.append(len(hits17()) - n0_)
    h8 = hits17()
    idle8 = bool(TW.of(tst).idle()) if TW.of(tst) is not None else True
    bolts8 = len([p_ for p_ in list(PS17) if str(p_) == str(RC.PS_BOLT)])
    imp8 = len([p_ for p_ in list(PS17) if str(p_) == str(RC.PS_HIT)])
    check(q17 == (True, True, True, 1) and h8 == [(1700 + k_, w17(k_)) for k_ in range(8)] and per17[:16] == [1, 0] * 8 and sum(per17) == 8
          and int(RC.ENDS_MAX) == e0_ + 1 and idle8 and imp8 == 8 and bolts8 >= 8,
          "R17e (1) 8 TARGETS: Ability 1's marker SPAWN (code 13000) -> the marker removed, ONE chain queued (the world is busy); 10 mobs in a row: "
          "the aimed one first, then the nearest new one each 0.15 s (ticks every 75 ms: a hit every other tick) - exactly 8 hits, never the same "
          "mob twice, 132 -> 63.135 (Damage$EntitySource(you), PROJECTILE), the 9th + 10th mob untouched, then the world is idle again; 8 "
          "Impact_Sword_Signature bursts + the blue bolt points: %s %s %s (%d bolt points)" % (q17, h8, per17, bolts8))
    # -- (2) OUT OF RANGE: the next mob 10.5 blocks away = the bolt stops after 1 hit; at exactly 10.0 it jumps
    fresh17()
    NEAR17[:] = row17(1710, [6.0, 16.5]) + [rc]
    r0_ = int(RC.ENDS_RANGE)
    cast17(1791)
    for k_ in range(6):
        tick17(0 if k_ == 0 else 150)
    hr1 = hits17()
    why_r = str(RC.LAST_WHY)
    fresh17()
    NEAR17[:] = row17(1712, [6.0, 16.0]) + [rc]
    cast17(1792)
    for k_ in range(6):
        tick17(0 if k_ == 0 else 150)
    hr2 = hits17()
    check(hr1 == [(1710, 132.0)] and int(RC.ENDS_RANGE) == r0_ + 2 and why_r.startswith("no new enemy within 10 blocks after 1 hits")
          and hr2 == [(1712, 132.0), (1713, 118.8)],
          "R17e (2) OUT OF RANGE: the second mob 10.5 blocks from the first = no jump (the bolt stops after 1 hit: %s); at 10.0 blocks = it jumps: %s / %s" % (
              why_r, hr1, hr2))
    # -- (3) PARTY / PVP: a mob, your party member (nearer) and a stranger behind it
    pp17 = []
    for pvp_, row_ in ((False, True), (True, True), (True, False)):
        fresh17()
        m3 = row17(1720 + (10 if pvp_ else 0) + (5 if not row_ else 0), [6.0])[0]
        put(rp, TCc.getComponentType(), TCc(V3(9.0, 64.7, 0.5), R3(0.0, 0.0, 0.0)))
        put(rs, TCc.getComponentType(), TCc(V3(12.0, 64.7, 0.5), R3(0.0, 0.0, 0.0)))
        NEAR17[:] = [m3, rp, rs, rc]
        wcfg.setPvpEnabled(pvp_)
        ACfg.SIG_PLAYERS = row_
        cast17(1793)
        for k_ in range(6):
            tick17(0 if k_ == 0 else 150)
        pp17.append(hits17())
    wcfg.setPvpEnabled(False)
    ACfg.SIG_PLAYERS = True
    iP, iS = int(rp.getIndex()), int(rs.getIndex())
    check(pp17[0] == [(1720, 132.0)] and pp17[1] == [(1730, 132.0), (iS, 118.8)] and pp17[2] == [(1735, 132.0)],
          "R17e (3) PARTY / PVP: PvP off - after the mob the bolt never jumps to the stranger or your party member (it stops); PvP on - it skips "
          "your party member (nearer) and hits the stranger; sig.wand.players off - no player at all: %s (party %d, stranger %d)" % (pp17, iP, iS))
    # -- (4) DEAD TARGET MID-CHAIN: after the first hit the first and the second mob die; the bolt skips the dead one and jumps from where
    # the first one stood to the third (6 blocks)
    fresh17()
    d3 = row17(1740, [6.0, 9.0, 12.0])
    NEAR17[:] = d3 + [rc]
    cast17(1794)
    tick17(0)
    hd1 = hits17()
    for r_ in d3[:2]:
        put(r_, DTHc.getComponentType(), U.allocateInstance(DTHc.class_))
    for k_ in range(5):
        tick17(150)
    hd = hits17()
    check(hd1 == [(1740, 132.0)] and hd == [(1740, 132.0), (1742, 118.8)] and bool(AT.dead(tst, d3[1])),
          "R17e (4) DEAD TARGET MID-CHAIN: the second mob died before the next jump -> skipped (ArmoryTrav.kind: dead); the first one died too and "
          "the jump starts where it stood (the third mob 6 blocks on): %s" % (hd,))
    # -- (5) a wall: no line of sight to the only mob = no target -> the charge comes back (sig.wand.refundMiss), the row off = spent
    rf17 = []
    for refund_ in (True, False):
        fresh17()
        AT.GRID = Grid(world_fn([lambda x, y, z: x == 4 and 64 <= y <= 67]))
        ACfg.SIG_REFUND = refund_
        NEAR17[:] = row17(1750 + (0 if refund_ else 1), [8.0]) + [rc]
        mc.setStatValue(SIGI, JFloat(0.0))          # the chain's ChangeStat already spent it
        m0_, f0_ = int(RC.MISSES), int(RC.REFUNDS)
        cast17(1795)
        tick17(0)
        rf17.append((hits17(), sv(mc, SIGI), int(RC.MISSES) - m0_, int(RC.REFUNDS) - f0_, str(RC.LAST_WHY), TW.of(tst) is None or int(TW.of(tst).rico.size()) == 0))
    AT.GRID = Grid(world_fn())
    ACfg.SIG_REFUND = True
    check(rf17[0] == ([], 20.0, 1, 1, "no enemy in your aim - the charge is back", True) and rf17[1] == ([], 0.0, 1, 0, "no enemy in your aim", True),
          "R17e (5) LINE OF SIGHT + NO TARGET: a wall between you and the only mob = no target: nothing hits, the meter is full again (20) and the "
          "chain ends; sig.wand.refundMiss off = the charge stays spent: %s" % (rf17,))
    # -- (5b) FIX (critic 1): the wand swapped away between the cast and the chain's step = no refund into the new item's meter
    fresh17()
    AT.GRID = Grid(world_fn([lambda x, y, z: x == 4 and 64 <= y <= 67]))
    NEAR17[:] = row17(1752, [8.0]) + [rc]
    mc.setStatValue(SIGI, JFloat(0.0))
    m0_, f0_ = int(RC.MISSES), int(RC.REFUNDS)
    cast17(1794)
    LP.HAND.put(cu, "Weapon_Sword_Iron")          # swapped inside the 1-2 tick window
    tick17(0)
    sw17 = (hits17(), sv(mc, SIGI), int(RC.MISSES) - m0_, int(RC.REFUNDS) - f0_, str(RC.LAST_WHY))
    LP.HAND.put(cu, "Weapon_Wand_Iron")
    AT.GRID = Grid(world_fn())
    check(sw17 == ([], 0.0, 1, 0, "no enemy in your aim - the wand left your hand, the charge is spent"),
          "R17e (5b) SWAP BEFORE THE MISS REFUND: fire at a wall, swap to a sword before the chain's first step -> no refund (the sword's "
          "meter is not filled), the miss is counted: %s" % (sw17,))
    # -- (6) who is never a target: a friendly (Revered) cow and an invulnerable mob before a hostile zombie (the engine attitude, the
    # Shadow Step rule; NPCPlugin's WorldSupport type as R12c registered it)
    fresh17()
    jfield(NPCP, "instance").set(None, npl)
    a17cow = ss_att(1760, 5.0, 0.5, ATTc.REVERED)
    a17zom = ss_att(1761, 9.0, 0.5, ATTc.HOSTILE)
    a17inv = mob(1762, 7.0, 64.0, 0.5, (0.8, 1.8, 0.8))
    put(a17inv, INVc.getComponentType(), INVc.INSTANCE)
    NEAR17[:] = [a17cow, a17inv, a17zom, rc]
    cast17(1796)
    for k_ in range(6):
        tick17(0 if k_ == 0 else 150)
    ha17 = hits17()
    jfield(NPCP, "instance").set(None, npl_old)
    check(ha17 == [(1761, 132.0)], "R17e (6) a Revered cow (livestock) and an Invulnerable mob are never hit - the hostile zombie behind them is the "
                                   "first target and there is no one left to jump to: %s" % (ha17,))
    # -- (7) refused casts: the signature off / a class lock (the charge back), no wand in hand (nothing), the Wood wand's base
    rq17 = []
    for case_ in ("off", "lock", "nowand"):
        fresh17()
        NEAR17[:] = row17(1770 + len(rq17), [6.0]) + [rc]
        mc.setStatValue(SIGI, JFloat(0.0))
        ACfg.SIG_ON = case_ != "off"
        if case_ == "lock":
            br.put("class:fn:allowed", Deny())
        LP.HAND.put(cu, "Weapon_Sword_Iron" if case_ == "nowand" else "Weapon_Wand_Iron")
        q0_ = int(RC.REFUSED)
        cast17(1797)
        tick17(0)
        rq17.append((case_, int(RC.REFUSED) - q0_, sv(mc, SIGI), hits17(), TW.of(tst) is None or int(TW.of(tst).rico.size()) == 0, str(RC.LAST_WHY)))
        br.remove("class:fn:allowed")
        ACfg.SIG_ON = True
    LP.HAND.put(cu, "Weapon_Wand_Wood")
    fresh17()
    NEAR17[:] = row17(1780, [6.0, 9.0]) + [rc]
    cast17(1798)
    for k_ in range(4):
        tick17(0 if k_ == 0 else 150)
    hw17 = hits17()
    LP.HAND.put(cu, "Weapon_Wand_Iron")
    check(rq17 == [("off", 1, 20.0, [], True, "signature off"), ("lock", 1, 20.0, [], True, "class lock"), ("nowand", 1, 0.0, [], True, "no wand in hand")]
          and hw17 == [(1780, 37.5), (1781, 33.75)],
          "R17e (7) REFUSED: sig.wand.enabled off / a class locked out of the wand (SkyyClasses class:fn:allowed) = no bolt, the meter full again; "
          "no wand in hand = no bolt, nothing given; the Wood wand (index 0) = 25 x 1.5 = 37.5 then 33.75: %s %s" % (rq17, hw17))
    # -- (8) the caster leaves the world mid-chain: the chain ends at the next tick
    fresh17()
    NEAR17[:] = row17(1785, [6.0, 9.0, 12.0]) + [rc]
    cast17(1799)
    tick17(0)
    ebu.remove(cu)
    tick17(150)
    hl17, why_l = hits17(), str(RC.LAST_WHY)
    ebu.put(cu, rc)
    idle_l = TW.of(tst) is None or bool(TW.of(tst).idle())
    check(hl17 == [(1785, 132.0)] and why_l == "the caster left this world" and idle_l,
          "R17e (8) the caster left this world after the first hit -> the chain ends (no more hits), the world goes idle: %s %s" % (hl17, why_l))
    # R17f THE CHARGE through ArmoryHitSys (Inspect): quick +1, charged +2, clamped at 20; no wand / our own MINE hit / cancelled / 0 damage = nothing
    fresh17()
    mt17 = row17(1800, [6.0])[0]
    TCh.TARGET = mt17
    mc.setStatValue(SIGI, JFloat(0.0))
    g0_ = int(RC.GAINS)
    gq17, gqpc = launched(QORB["Iron"], 1801, 0.5, 65.0, 0.5)
    go17, gopc = launched(ORB["Iron"], 1802, 0.5, 65.0, 0.5)

    def hs17(pj_, amt_, cancel=False, mine=False):
        d_ = DMGc(DPS(rc, pj_), DCSc.PROJECTILE, JFloat(amt_))
        if cancel:
            d_.setCancelled(True)
        if mine:
            AT.MINE.put(d_, JClass("java.lang.Boolean").TRUE)
        HS.handle(0, chunk, tst, tbuf, d_)
        return sv(mc, SIGI)
    gn17 = [hs17(gq17, 18.0), hs17(go17, 88.0)]
    LP.HAND.put(cu, "Weapon_Sword_Iron")
    gn17.append(hs17(gq17, 18.0))
    LP.HAND.put(cu, "Weapon_Wand_Iron")
    gn17 += [hs17(gq17, 18.0, mine=True), hs17(gq17, 18.0, cancel=True), hs17(gq17, 0.0)]
    mc.setStatValue(SIGI, JFloat(19.5))
    gn17.append(hs17(go17, 88.0))
    g1_ = int(RC.GAINS)
    gn17.append(hs17(go17, 88.0))
    g2_ = int(RC.GAINS)
    ACfg.SIG_ON = False
    mc.setStatValue(SIGI, JFloat(0.0))
    gn17.append(hs17(gq17, 18.0))
    ACfg.SIG_ON = True
    check(gn17 == [1.0, 3.0, 3.0, 3.0, 3.0, 3.0, 20.0, 20.0, 0.0] and g1_ - g0_ == 3 and g2_ == g1_,
          "R17f THE CHARGE (ArmoryHitSys.handle on a real dispatch shape): a quick-orb hit +1, a charged-orb hit +2; a sword in hand, our own "
          "(MINE) hit, a cancelled hit, a 0-damage hit = nothing; 19.5 + 2 = 20 (the max), a full meter takes nothing more; the signature off "
          "= no charge: %s" % (gn17,))
    AT.PSEEN = None
    AT.GRID, AT.NEAR = grid17_old, near17_old
    LP.HAND, LP.LOOK = hand17, look17
    RC.CLOCK = JLong(0)
    mc.setStatValue(SIGI, JFloat(0.0))
    for r_ in (rc, rp, rs):
        put(r_, TCc.getComponentType(), tc17_old[int(r_.getIndex())])
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    TW.ALL.clear()
    reset_buf()
    # R17g: vs the 0.1.13 jar METHOD BY METHOD (the file by file compare = P16)
    MN17, MO17 = methods_of(JAR), methods_of(OLD113)
    cmp17 = {}
    for c_ in sorted(set(MN17) | set(MO17)):
        if c_ not in MN17 or c_ not in MO17:
            cmp17[c_] = "only in " + ("0.1.14" if c_ in MN17 else "0.1.13")
            continue
        ch_ = sorted(k_ for k_ in set(MN17[c_][0]) | set(MO17[c_][0]) if MN17[c_][0].get(k_) != MO17[c_][0].get(k_))
        fd_ = sorted(set(MN17[c_][1]) ^ set(MO17[c_][1]))
        if ch_ or fd_:
            cmp17[c_] = {"methods": [k_.split("(")[0] for k_ in ch_], "fields": [f_.split(":")[0] for f_ in fd_]}
    plan17 = {"ArmoryCfg": ({"apply", "sigText", "load", "reloadAll", "useDefaults"}, None), "ArmoryDefs": ({"pids"}, {"RICO_MARK", "RICO_CODE", "SIG_MAX"}),
              "ArmoryTrav": ({"added"}, set()), "ArmoryHitSys": ({"handle"}, set()), "TravWorld": ({"idle", "run", "<init>"}, {"rico"}),
              "SkyyArmoryPlugin": ({"setup"}, set())}
    bad17 = {}
    for c_, v_ in cmp17.items():
        if c_ in ("Rico", "RicoChain") and v_ == "only in 0.1.14":
            continue
        if c_.startswith("Cfg") and isinstance(v_, dict):          # the config kit (tools/skyycfg.py): its row tables carry the 12 + 1 new rows
            continue
        if c_ == "ArmoryHooks" and isinstance(v_, dict) and not v_["fields"]:          # the read-only row texts (fixed.sig.wand)
            continue
        if c_ in plan17 and isinstance(v_, dict) and set(v_["methods"]) <= plan17[c_][0] and (plan17[c_][1] is None or set(v_["fields"]) <= plan17[c_][1]):
            if c_ == "ArmoryCfg" and not all(f_.startswith("SIG_") or f_ == "DEF_CFG" for f_ in v_["fields"]):
                bad17[c_] = v_
            continue
        bad17[c_] = v_
    check(not bad17 and cmp17.get("Rico") == "only in 0.1.14" and cmp17.get("RicoChain") == "only in 0.1.14"
          and "added" in cmp17.get("ArmoryTrav", {}).get("methods", []) and "handle" in cmp17.get("ArmoryHitSys", {}).get("methods", []),
          "R17g: 0.1.13 -> 0.1.14 METHOD BY METHOD - only the planned methods / fields differ (ArmoryCfg apply + sigText + the SIG_* rows, ArmoryDefs "
          "pids + 3 constants, ArmoryTrav.added, ArmoryHitSys.handle, TravWorld rico / idle / run, the plugin's setup line, the kit's row tables, "
          "ArmoryHooks' row texts) + the 2 new classes: %s" % json.dumps(bad17)[:1500])
    print("R17g. vs 0.1.13 method by method: %s" % json.dumps(cmp17)[:1500])
    # R17h FIX (critic 3): the wand category's label names the signature (id "hop" kept, 16 categories, the sig rows in it)
    Rows17 = JClass(PKG + "CfgRows")
    cl17 = [str(x_) for x_ in Rows17.CAT_LABELS]
    check(len(cl17) == 16 and cl17[2] == "Wand + signature" and "Wand hop + burst" not in cl17 and len(cl17[2]) <= 20,
          "R17h: Server Setup > Armory: the wand category is now 'Wand + signature' (the 12 sig.wand rows + hop + burst; id hop): %s" % cl17)
    print("R17. 0.1.14 wand signature: validators (11), the Ability1 root compile, the engine's energy gate, the Rico maths, the ricochet (8 targets, "
          "range, party / PvP, dead mid-chain, wall + refund, attitude, refusals, Wood, caster gone), the charge, the 0.1.13 compare - every path executed")
'''
hrep('''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''',
     R17 + '''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''')

out_t = ts.replace(LF, TNL)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(out_t)
print("wrote %s" % os.path.relpath(TDST, ROOT))
