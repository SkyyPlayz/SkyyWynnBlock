"""Derive SkyyArmory/build_skyyarmory_0.1.12.py (+ its harness SkyyArmory/test_skyyarmory_0.1.12.py) from the GENERATED 0.1.11
(SkyyArmory/build_skyyarmory_0.1.11.py = the tools/deploy_set.py SET pin, made by tools/armory_0_1_11_patch.py; test_skyyarmory_0.1.11.py =
its harness). Every anchor is asserted (rep = exactly one hit). Edit THIS file, never the generated scripts.
Run:  python tools/armory_0_1_12_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.12.py   then
      python SkyyArmory/test_skyyarmory_0.1.12.py --dir tools/dev/scratch/<task>/harness      (never --deploy)

0.1.12 = THE MONK MOVES, built INTO the real weapons (Skyy 2026-10-08: "start building the monk moves"; "you just tie the moves into the
weapon from the start, so i can test by playing, and all i have to do is run the probe command for the data to appear in chat"; "plunge is
sloww"; brief = docs/answered/classes.md 2026-10-08 REQUEST + the Monk LOCKED lines; numbers research/cloud/Monk-Kit-Spec.md section 3; the
engine paths = SkyyMonkProbe 0.1, probe results docs/log/2026-10.md 2026-10-08 MONK PROBE lines):
(1) POLE-VAULT = the charged attack of ALL 9 Bo staffs. The shared root SkyyArmory_Bo_Primary (0.1.11) now names SkyyArmory_Monk_Bo_Charge
    = the vanilla Staff_Primary Charging step copied at build time (same hold 1 s, pose, slow walk) whose tap key "0" is the 0.1.11 swing
    chain SkyyArmory_Bo_Swings and whose hold key launches the invisible marker SkyyArmory_Monk_Vault (code 12000). The server (Monk.vault):
    on the ground only; lunge (vault.lunge 3 blocks in vault.lungeTime 0.2 s, a Set every tick), then the vault Set (vy for vault.height 4.5,
    forward for vault.distance 7 x vault.pushBoost 2.1 - the probe: the engine eats about half the sideways push); every enemy whose BODY
    the swept path touches (horizontal distance <= vault.kickReach 1.5 + the mob's own width, vertical overlap with its height box, every
    tick from the lunge start to the landing, the segment between ticks sampled every 0.25 block) is kicked ONCE for vault.kickDamage 2 x
    the staff's normal hit (PHYSICAL from you = the melee path: SkyyGear levels it like a swing). FLOWING FALL from the top (flow.slower 15 %
    slower fall = a Set every tick, your own sideways speed kept so you steer; flow.fallDamage 15 % less fall damage). ONE free mid-air jump
    by CROUCH (vault.airJump; the server never sees the jump key in mid-air - probe M3).
(2) SKIPPING BOUNDS after a vault: a jump in the window bound.before 0.25 s before to bound.after 0.10 s after a landing (probe M2) bounds you
    forward bound.distance 5 + bound.perBlock 0.5 per block fallen (bound.cap +8) x the push boost, bound.height 1.4 x a jump, flowing fall
    again; the chain goes on while the timing holds and you pay bound.stamina 3 + bound.mana 1; a timed landing takes NO fall damage (the
    FALL damage is held ~0.15 s and forgiven by the bound, else re-dealt at 85 %).
(3) RISING STRIKE = the charged attack of the 12 fist weapons (wraps + gauntlets): each fist root now names SkyyArmory_Monk_Fist_<key>_Charge
    (the vanilla dagger Charging shape + AllowIndefiniteHold = fired on RELEASE like the Bo: tap key "0" = the 0.1.7 combo chain unchanged, hold 0.6 s = SkyyArmory_Monk_Rise_Launch, the PowerUp
    pose, marker SkyyArmory_Monk_Rise code 12001). Uppercut leap rise.height 6 up with rise.forward 1.0 b/s drift (0.4 x the probe push);
    enemies in the cone ahead (rise.coneLength 3 x rise.coneWidth 1.5, + half their width) take rise.damage 1.2 x the fist's jab and are
    knocked up rise.knockUp 5 (bosses / mini-bosses = stun.bossWords: hit, never lifted); HANG rise.hang 1.2 s at the top for you and them;
    your hits on a held enemy fling it rise.airKnockback 6 blocks; CROUCH near the top = PLUNGE PUNCH at plunge.speed 30 b/s (Skyy: 14 was
    'sloww') dragging the held enemies, landing slam plunge.damage 1.0 x a jab within plunge.radius 3, no fall damage; no plunge = the
    flowing fall (steerable, -15 % fall damage).
(4) COSTS (LOCKED cost rule, physical = more Stamina than Mana): vault 7 St + 3 Mana, rise 8 + 4, bound 3 + 1 - paid at the start; a move
    that does not move you (under 1 block) gives them back; too little = no move, nothing taken. Every number is a Server Setup row
    (Server Setup > Armory > Monk moves + weapons; tools/skyycfg.py, KEEP=10). No cooldowns.
(5) NO ACROBATICS XP: while a Monk move runs (and ~0.5 s after it) the plain java.lang bridge key armory:monkmove:<uuid> -> Long (epoch ms
    until) is set; SkyySkills 0.4.22 pays no Acrobatics XP (run / jump / fall / roll) and fires no Double Jump for that player meanwhile.
(6) ONE DEBUG TOGGLE: /armory debug monk on|off (admin: requirePermission skyyarmory.admin + no permission groups) - every move you make then
    prints its MEASURED numbers in your chat (+ the server log): forward / height / air time / lunge / kicks / hang / plunge speed / costs.
(7) CLIENT LOG FIX (docs/log 2026-10-08 LOG SCAN): every SkyyArmory_Fist animation entry without a ThirdPerson gets the vanilla Default
    (unarmed) third-person file of the same movement (Default/<name>.blockyanim, the FPS file name without _FPS; the Step / Jump / Fall
    entries the vanilla Sword set's mapping) - the 50 'Missing third person animation for item: SkyyArmory_Fist/...' warnings.
    'Missing primary chain for fork' = UNVERIFIED, NOT ruled out: the 07:06 log has 17 of them right after the server WARN '[ChargingInteraction]
    charge value 0.214 exceeds max allowed 0.200' (and 0.402 > 0.400) - ChargingInteraction.validateChargeValue caps the allowed value at the
    highest key only when AllowIndefiniteHold is false, so a client that overshoots the last key by a frame trips it; 0.200 = the VANILLA
    Weapon_Daggers_Primary (not ours), 0.400 = Weapon_Daggers_Primary_Pounce (ours since 0.1.8, the vanilla keys kept). The new fist holds
    therefore use AllowIndefiniteHold (cannot overshoot); the dagger holds are unchanged (a gameplay change Skyy did not ask for). Check the
    logs after play. 'Couldn't find attachment target: R-Attachment': not changed (12 lines in the 13 s before a vanilla wolf attack SEVERE;
    our models' root node = the vanilla Bo / dagger models' R-Attachment root).
NO saved data, no migration (new keys only - an existing config.properties simply lacks them = the defaults), no new system (the moves run
in the existing TravTick / GrappleFallSys / ArmoryHitSys / ArmoryTravSys), one new command, 4 new classes (MonkState, Monk, ArmoryCmd,
ArmoryDbgCmd).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.11.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.12.py")
TSRC = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.11.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.12.py")

CR, LF = chr(13), chr(10)
raw = open(SRC, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.11"\nMOD = "SkyyArmory"' in s and "0.1.11 = NO MAGIC SHOT ON THE BO STAFFS" in s, "build_skyyarmory_0.1.11.py is not the 0.1.11 pin"
assert "Monk" + "State" not in s and "MK_ON" not in s, "0.1.11 already has Monk moves"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:140])
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyArmory 0.1.11 - build script (javassist via jpype). GENERATED by tools/armory_0_1_11_patch.py from the GENERATED 0.1.10 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.11.py -> SkyyArmory/SkyyArmory-0.1.11.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.11.py --dir tools/dev/scratch/<task>/harness.
''', '''"""SkyyArmory 0.1.12 - build script (javassist via jpype). GENERATED by tools/armory_0_1_12_patch.py from the GENERATED 0.1.11 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.12.py -> SkyyArmory/SkyyArmory-0.1.12.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.12.py --dir tools/dev/scratch/<task>/harness.

0.1.12 = THE MONK MOVES built into the real weapons (Skyy 2026-10-08 "start building the monk moves"; full notes in tools/armory_0_1_12_patch.py):
Bo staffs hold = POLE-VAULT (lunge, vault 4.5 up x 7 forward, kicks along the swept path 2x a Bo hit, flowing fall, a free air jump by
crouch) + SKIPPING BOUNDS (a jump 0.25 s before to 0.10 s after a landing); fist weapons hold = RISING STRIKE (6 up, cone hit 1.2x, knock-up,
hang 1.2 s, air hits fling) + PLUNGE PUNCH (crouch near the top, 30 b/s, slam); costs vault 7+3 / rise 8+4 / bound 3+1 (refunded when you do
not move); bridge armory:monkmove:<uuid> (SkyySkills 0.4.22: no Acrobatics XP meanwhile); /armory debug monk on|off (admin) prints every
move's measured numbers; the SkyyArmory_Fist animation set gets third-person files. Server Setup > Armory > Monk moves + weapons.

0.1.11 (the base, everything below is still true unless 0.1.12 above says otherwise):
''')
rep('VERSION = "0.1.11"\nMOD = "SkyyArmory"', 'VERSION = "0.1.12"\nMOD = "SkyyArmory"')

# ---------------------------------------------------------------------------------------------------------------- the rows (Server Setup)
# (key, label, cat, type, default, min, max, opts, unit, flags, help, ArmoryCfg field, Java type, Java default, config.properties comment)
CFG_MK_PY = r'''
# ================================================================= 0.1.12 THE MONK MOVES (Skyy 2026-10-08 "start building the monk moves"; Monk-Kit-Spec 3)
MK_VAULT_MARK, MK_RISE_MARK = "SkyyArmory_Monk_Vault", "SkyyArmory_Monk_Rise"          # the invisible markers the holds launch
MK_VAULT_CODE, MK_RISE_CODE = 12000, 12001
MK_FIST_HOLD = 0.6               # the fist hold = the dagger Shadow Step hold (client-predicted; a read-only row)
MK_FLING_PER = 2.0               # air-hit fling speed per block of rise.airKnockback (the probe's 12 b/s for 6 blocks - UNVERIFIED distance)
MK_FLAG_MS = 500                 # the Acrobatics flag lasts this long after the last active tick (~0.5 s after a landing)
_MK = "monk"          # the existing Monk category (the kit allows 16): "Monk moves + weapons" - the move rows first, the fixed rows after
CFG_MK = [
    ('monk.moves', 'Monk moves', _MK, 'bool', 'true', '', '', '', '', 'live,part,danger', 'Off = holding a Bo staff or fist attack does nothing.', 'MK_ON', 'boolean', 'true', 'Monk moves: Bo staff hold = Pole-Vault + skipping bounds, fist hold = Rising Strike + Plunge Punch. Off = the holds do nothing.'),
    ('vault.lunge', 'Pole-Vault lunge (blocks)', _MK, 'dec', '3', '0', '8', '', 'blocks', 'live', 'The quick step on the ground before the vault (0 = vault at once).', 'MK_LUNGE', 'double', '3', 'Pole-Vault: the quick lunge on the ground before the vault, in blocks (0 = vault at once).'),
    ('vault.lungeTime', 'Lunge time (s)', _MK, 'dec', '0.2', '0.1', '0.6', '', 's', 'live,adv', 'How long the lunge pushes; its speed = lunge blocks / this.', 'MK_LUNGE_T', 'double', '0.2', 'Pole-Vault: how long the lunge pushes (seconds); speed = lunge / this.'),
    ('vault.height', 'Pole-Vault height (blocks)', _MK, 'dec', '4.5', '1', '12', '', 'blocks', 'live', 'How high the vault lifts you.', 'MK_VH', 'double', '4.5', 'Pole-Vault: how high you rise (blocks).'),
    ('vault.distance', 'Pole-Vault distance (blocks)', _MK, 'dec', '7', '1', '20', '', 'blocks', 'live', 'How far forward the vault carries you.', 'MK_VD', 'double', '7', 'Pole-Vault: how far forward the vault carries you (blocks).'),
    ('vault.pushBoost', 'Forward push boost (x)', _MK, 'dec', '2.1', '1', '4', '', 'x', 'live,adv', 'The game eats about half a sideways push in the air (probe): 2.1 reaches the distance.', 'MK_BOOST', 'double', '2.1', 'Pole-Vault + bounds: the forward push x this (the probe: the engine bleeds about half the sideways push, 2.1 reaches the set distance).'),
    ('vault.kickDamage', 'Vault kick (x a Bo hit)', _MK, 'dec', '2', '0', '5', '', 'x', 'live', 'Every enemy the vault path touches takes this x the staff hit, once.', 'MK_KICK', 'double', '2', "Pole-Vault: every enemy whose body your path touches takes this x the staff's normal hit, once per vault."),
    ('vault.kickReach', 'Vault kick reach (blocks)', _MK, 'dec', '1.5', '0.5', '4', '', 'blocks', 'live', 'Kicks an enemy within this + its own width of your path, at its height.', 'MK_KREACH', 'double', '1.5', "Pole-Vault: an enemy is kicked when your path passes within this + the enemy's own width of it, at its height."),
    ('vault.stamina', 'Pole-Vault Stamina', _MK, 'dec', '7', '0', '20', '', '', 'live', 'Paid at the start; back if you do not move.', 'MK_VST', 'double', '7', 'Pole-Vault Stamina (paid at the start, given back when you do not move).'),
    ('vault.mana', 'Pole-Vault Mana', _MK, 'dec', '3', '0', '50', '', '', 'live', 'Paid at the start (only with a Mana pool); back if you do not move.', 'MK_VMA', 'double', '3', 'Pole-Vault Mana (only with a Mana pool; given back when you do not move).'),
    ('vault.airJump', 'Free air jump (crouch)', _MK, 'bool', 'true', '', '', '', '', 'live', 'One free mid-air jump by crouching, before the vault lands.', 'MK_AIRJUMP', 'boolean', 'true', 'Pole-Vault: one free mid-air jump by crouching before you land (the server never sees the jump key in mid-air).'),
    ('flow.slower', 'Flowing fall: slower (%)', _MK, 'int', '15', '0', '60', 'step=5', '%', 'live', 'After a vault, bound or Rising Strike you fall this much slower.', 'MK_FLOW', 'int', '15', 'Flowing fall: after a Monk move you fall this % slower (you can still steer).'),
    ('flow.fallDamage', 'Flowing fall: less damage (%)', _MK, 'int', '15', '0', '100', 'step=5', '%', 'live', 'Fall damage of a flowing fall is this much lower.', 'MK_FLOWDMG', 'int', '15', 'Flowing fall: its fall damage is this % lower (a timed bound takes none).'),
    ('bound.before', 'Bound window before landing (s)', _MK, 'dec', '0.25', '0', '0.6', '', 's', 'live', 'A jump pressed this early still bounds.', 'MK_BBEFORE', 'double', '0.25', 'Skipping bounds: a jump pressed up to this long before you land still bounds (seconds).'),
    ('bound.after', 'Bound window after landing (s)', _MK, 'dec', '0.1', '0', '0.4', '', 's', 'live', 'A jump pressed this late still bounds.', 'MK_BAFTER', 'double', '0.1', 'Skipping bounds: a jump pressed up to this long after you land still bounds (seconds).'),
    ('bound.distance', 'Bound distance (blocks)', _MK, 'dec', '5', '1', '15', '', 'blocks', 'live', 'How far forward a bound carries you.', 'MK_BDIST', 'double', '5', 'Skipping bounds: how far forward one bound carries you (blocks).'),
    ('bound.perBlock', 'Bound: extra per block fallen', _MK, 'dec', '0.5', '0', '2', '', 'blocks', 'live', 'The further you fell, the further the bound.', 'MK_BPER', 'double', '0.5', 'Skipping bounds: extra forward distance per block you fell before it.'),
    ('bound.cap', 'Bound: most extra (blocks)', _MK, 'dec', '8', '0', '20', '', 'blocks', 'live', 'The extra from falling stops here.', 'MK_BCAP', 'double', '8', 'Skipping bounds: the extra from falling stops at this many blocks.'),
    ('bound.height', 'Bound height (x a jump)', _MK, 'dec', '1.4', '0.5', '3', '', 'x', 'live', 'How high a bound goes, compared to a normal jump.', 'MK_BH', 'double', '1.4', 'Skipping bounds: height compared to a normal jump.'),
    ('bound.stamina', 'Bound Stamina', _MK, 'dec', '3', '0', '20', '', '', 'live', 'Too little = the bounds end.', 'MK_BST', 'double', '3', 'Skipping bounds: Stamina per bound (too little = the chain ends).'),
    ('bound.mana', 'Bound Mana', _MK, 'dec', '1', '0', '50', '', '', 'live', 'Only with a Mana pool. Too little = the bounds end.', 'MK_BMA', 'double', '1', 'Skipping bounds: Mana per bound (only with a Mana pool).'),
    ('rise.height', 'Rising Strike height (blocks)', _MK, 'dec', '6', '1', '15', '', 'blocks', 'live', 'How high the uppercut leap goes.', 'MK_RH', 'double', '6', 'Rising Strike: how high the uppercut leap goes (blocks).'),
    ('rise.forward', 'Rising Strike drift (b/s)', _MK, 'dec', '1', '0', '8', '', '', 'live,adv', 'Forward drift while rising (0.4 x the probe push, it drifted too far).', 'MK_RFWD', 'double', '1', 'Rising Strike: forward drift speed while rising (blocks per second).'),
    ('rise.damage', 'Rising Strike hit (x a jab)', _MK, 'dec', '1.2', '0', '5', '', 'x', 'live', "Enemies in front take this x the fist weapon's jab.", 'MK_RDMG', 'double', '1.2', "Rising Strike: enemies in the cone take this x the fist weapon's jab."),
    ('rise.coneLength', 'Rising Strike reach (blocks)', _MK, 'dec', '3', '1', '8', '', 'blocks', 'live', 'How far in front the uppercut hits.', 'MK_RLEN', 'double', '3', 'Rising Strike: how far in front the uppercut hits (blocks).'),
    ('rise.coneWidth', 'Rising Strike width (blocks)', _MK, 'dec', '1.5', '0.5', '6', '', 'blocks', 'live', 'How wide the uppercut hits (+ half the enemy width).', 'MK_RWID', 'double', '1.5', 'Rising Strike: how wide the uppercut hits (blocks; + half the enemy width).'),
    ('rise.knockUp', 'Knock enemies up (blocks)', _MK, 'dec', '5', '0', '12', '', 'blocks', 'live', 'Bosses and mini-bosses (stun.bossWords) are hit, never lifted.', 'MK_RUP', 'double', '5', 'Rising Strike: enemies hit are knocked up this high (bosses / mini-bosses: hit, never lifted).'),
    ('rise.hang', 'Hang time at the top (s)', _MK, 'dec', '1.2', '0', '4', '', 's', 'live', 'You and the lifted enemies slow down at the top.', 'MK_RHANG', 'double', '1.2', 'Rising Strike: hang time at the top for you and the lifted enemies (seconds).'),
    ('rise.airKnockback', 'Air hit knockback (blocks)', _MK, 'dec', '6', '0', '20', '', 'blocks', 'live', 'Your hits on a lifted enemy send it flying.', 'MK_RFLING', 'double', '6', 'Rising Strike: your hits on a lifted enemy send it flying about this far.'),
    ('rise.stamina', 'Rising Strike Stamina', _MK, 'dec', '8', '0', '20', '', '', 'live', 'Paid at the start; back if you do not move.', 'MK_RST', 'double', '8', 'Rising Strike Stamina (given back when you do not move).'),
    ('rise.mana', 'Rising Strike Mana', _MK, 'dec', '4', '0', '50', '', '', 'live', 'Only with a Mana pool; back if you do not move.', 'MK_RMA', 'double', '4', 'Rising Strike Mana (only with a Mana pool; given back when you do not move).'),
    ('plunge.speed', 'Plunge Punch speed (b/s)', _MK, 'dec', '30', '10', '60', '', '', 'live', 'Skyy: 14 was slow (a normal fall tops out near 16).', 'MK_PSPD', 'double', '30', 'Plunge Punch: how fast you slam down (blocks per second; a normal fall tops out near 16).'),
    ('plunge.damage', 'Plunge slam (x a jab)', _MK, 'dec', '1', '0', '5', '', 'x', 'live', "The landing slam hits this x the fist weapon's jab.", 'MK_PDMG', 'double', '1', "Plunge Punch: the landing slam hits every enemy around for this x the fist weapon's jab."),
    ('plunge.radius', 'Plunge slam radius (blocks)', _MK, 'dec', '3', '1', '8', '', 'blocks', 'live', 'Enemies this close to where you land are hit.', 'MK_PRAD', 'double', '3', 'Plunge Punch: enemies this close to where you land are hit (blocks).'),
]
assert len(set(r[0] for r in CFG_MK)) == len(CFG_MK) == 34 and all(len(r) == 15 and r[2] == _MK for r in CFG_MK)
assert all(len(r[1]) <= 40 and len(r[10]) <= 100 for r in CFG_MK), [(r[0], len(r[1]), len(r[10])) for r in CFG_MK if len(r[1]) > 40 or len(r[10]) > 100]
'''
rep('''# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)''', CFG_MK_PY.lstrip("\n") + '''# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)''')
rep('''+ CFG_GRAPPLE + CFG_LEAP + CFG_BK + CFG_ST + CFG_SS      # 0.1.2 grapple''', '''+ CFG_GRAPPLE + CFG_LEAP + CFG_BK + CFG_ST + CFG_SS + CFG_MK      # 0.1.12: + the Monk moves; 0.1.2 grapple''')

# ---------------------------------------------------------------------------------------------------------------- the assets
ASSET_PY = r'''# ================================================================= 0.1.12 ASSETS: THE MONK MOVES (the charged keys + markers + the Fist set's third-person files)
P_MKINT = "Server/Item/Interactions/Weapons/Monk/SkyyArmory/%s.json"
ID_MK_BOCHARGE, ID_MK_VAULT_LAUNCH, ID_MK_RISE_LAUNCH = "SkyyArmory_Monk_Bo_Charge", "SkyyArmory_Monk_Vault_Launch", "SkyyArmory_Monk_Rise_Launch"
ID_MK_FCHARGE = "SkyyArmory_Monk_Fist_%s_Charge"
MK_INT_IDS = []


def add_mki(iid, obj):
    assert iid.startswith("SkyyArmory_Monk_") and not az_has("int", iid) and not az_has("root", iid), iid
    add_int(P_MKINT, iid, obj)
    MK_INT_IDS.append(iid)


# ---- (1) the Bo hold: the vanilla Staff_Primary Charging step (asserted unchanged in 0.1.11's block: VSP), tap "0" = the 0.1.11 swing chain,
# the hold key = the vault marker launch; the root SkyyArmory_Bo_Primary (all 9 Bo staffs name it) now names this step
assert VSP["Type"] == "Charging" and sorted(VSP["Next"]) == ["0", "1"] and VSP["Next"]["1"] == "Staff_Cast_Summon_Charged" \
    and VSP["Effects"] == {"ItemAnimationId": "CastSummonCharging"} and VSP.get("AllowIndefiniteHold") is True, VSP
MK_BO_HOLD = float(min(k_ for k_ in VSP["Next"] if k_ != "0"))
assert MK_BO_HOLD == 1.0, MK_BO_HOLD
_bch = json.loads(json.dumps(VSP))
_bch["Next"] = {"0": ID_BOSWING, "1": ID_MK_VAULT_LAUNCH}
assert "CastSummonCharging" in ANIMS[ANIM_STAFF]["Animations"] and "CastSummon" in ANIMS[ANIM_STAFF]["Animations"]
add_mki(ID_MK_BOCHARGE, _bch)
add_mki(ID_MK_VAULT_LAUNCH, launch(MK_VAULT_MARK, "CastSummon"))
assert ROOTS[ID_BOROOT] == {"Interactions": [ID_BOSWING]} and ASSETS[P_BOROOT % ID_BOROOT] == jdump(ROOTS[ID_BOROOT])
ROOTS[ID_BOROOT] = {"Interactions": [ID_MK_BOCHARGE]}
ASSETS[P_BOROOT % ID_BOROOT] = jdump(ROOTS[ID_BOROOT])
# ---- (3) the fist hold: the vanilla dagger Charging shape (Weapon_Daggers_Primary: DisplayProgress false, tap "0" = the combo), the hold
# key MK_FIST_HOLD = the rise marker launch with the PowerUp pose (our Fist set); every fist root keeps its own keys (RequireNewClick,
# ClickQueuingTimeout, Cooldown, Tags) - only its Interactions name the Charging step instead of the chain
_vdgp = az_get("int", "Weapon_Daggers_Primary")
assert _vdgp["Type"] == "Charging" and _vdgp.get("DisplayProgress") is False and sorted(_vdgp) == ["DisplayProgress", "Next", "Type"], _vdgp
assert "PowerUp" in ANIMS[ANIM_FIST]["Animations"]
add_mki(ID_MK_RISE_LAUNCH, launch(MK_RISE_MARK, "PowerUp"))
MK_FROOTS = []
for _iid in GAUNT_IDS + WRAP_IDS:
    _rid = FIST_ROOT[_iid]
    _key = _rid[len("SkyyArmory_Fist_"):-len("_Primary")]
    _ro = ROOTS[_rid]
    assert _ro["Interactions"] == [ID_FCHAIN % _key] and ASSETS[P_FROOT % _rid] == jdump(_ro), _rid
    # fix round: AllowIndefiniteHold true (the vanilla Knife_Attack / Staff_Primary way) - fires on RELEASE like the Bo, never at the 0.6 key while
    # still held, and the client's charge value can never overshoot the highest key (the vanilla dagger shape's 'charge value 0.214 exceeds max
    # allowed 0.200' WARN that came with 'Missing primary chain for fork' in the 07:06 log)
    add_mki(ID_MK_FCHARGE % _key, {"Type": "Charging", "DisplayProgress": False, "AllowIndefiniteHold": True,
                                   "Next": {"0": ID_FCHAIN % _key, str(MK_FIST_HOLD): ID_MK_RISE_LAUNCH}})
    _ro["Interactions"] = [ID_MK_FCHARGE % _key]
    ASSETS[P_FROOT % _rid] = jdump(_ro)
    MK_FROOTS.append(_rid)
assert len(MK_FROOTS) == 12 and len(MK_INT_IDS) == 15
add_prj(MK_VAULT_MARK, blink_marker())
add_prj(MK_RISE_MARK, blink_marker())
MK_PRJS = [MK_VAULT_MARK, MK_RISE_MARK]
# ---- (7) the client log fix: every SkyyArmory_Fist entry without a ThirdPerson gets the vanilla Default (unarmed) third-person file
MK_TP_FIXED = {"StepWalk": "Default/Step_Walk", "StepRun": "Default/Step_Run", "StepSprint": "Default/Step_Sprint",
               "StepCrouchWalk": "Default/Step_Crouch_Walk", "Jump": "Default/Jump", "JumpWalk": "Default/Jump_Far", "JumpRun": "Default/Jump_Far",
               "JumpCrouch": "Default/Jump_Crouch", "Fall": "Default/Fall", "FallFar": "Default/Fall_Far"}
_swd = anim_chain("Sword")
assert [_swd[k_]["ThirdPerson"].rsplit("/", 1)[1] for k_ in ("Jump", "JumpWalk", "JumpRun", "Fall", "FallFar")] == \
    ["Jump.blockyanim", "Jump_Far.blockyanim", "Jump_Far.blockyanim", "Fall.blockyanim", "Fall_Far.blockyanim"], "the vanilla Sword set's jump / fall mapping changed"
MK_TP = {}
_fa = ANIMS[ANIM_FIST]["Animations"]
for _k, _e in _fa.items():
    if "ThirdPerson" in _e:
        continue
    if _k in MK_TP_FIXED:
        _tp = "Characters/Animations/" + MK_TP_FIXED[_k] + ".blockyanim"
    else:
        assert str(_e.get("FirstPerson", "")).endswith("_FPS.blockyanim"), (_k, _e)
        _tp = _e["FirstPerson"][:-len("_FPS.blockyanim")] + ".blockyanim"
    assert ("Common/" + _tp) in AZ_SET, (_k, _tp)
    MK_TP[_k] = _tp
_fa0 = json.loads(json.dumps(_fa))
for _k, _tp in MK_TP.items():
    _fa[_k]["ThirdPerson"] = _tp
assert len(MK_TP) == 50 and not [k_ for k_, e_ in _fa.items() if "ThirdPerson" not in e_] \
    and all((dict((x_, y_) for x_, y_ in _fa[k_].items() if x_ != "ThirdPerson") if k_ in MK_TP else _fa[k_]) == _fa0[k_] for k_ in _fa), len(MK_TP)
assert ASSETS[P_ANIM % ANIM_FIST] != jdump(ANIMS[ANIM_FIST])
ASSETS[P_ANIM % ANIM_FIST] = jdump(ANIMS[ANIM_FIST])
# ---- the descriptions say the hold
_ll = ASSETS[P_LANG].split("\n")
MK_LANG = []
for _n, _l in enumerate(_ll):
    for _i in BO_IDS + GAUNT_IDS + WRAP_IDS:
        if _l.startswith("items.%s.description = " % _i):
            assert _l.endswith(" Right click: block.") and "Hold" not in _l, _l
            _ll[_n] = _l[:-len(" Right click: block.")] + (" Hold + release: Pole-Vault (kicks, bounds)." if _i in BO_IDS else
                                                           " Hold + release: Rising Strike (crouch at the top: Plunge Punch).") + " Right click: block."
            MK_LANG.append(_i)
assert sorted(MK_LANG) == sorted(BO_IDS + GAUNT_IDS + WRAP_IDS)
ASSETS[P_LANG] = "\n".join(_ll)
# ---- reference closure of the 0.1.12 files: every id they name is ours or vanilla, every pose is in the set the weapon uses
_mk12 = []
for _iid in MK_INT_IDS:
    for _r in refs_of(INTS[_iid], set()):
        if _r not in INTS and _r not in ROOTS and not az_has("int", _r) and not az_has("root", _r):
            _mk12.append("%s -> %s" % (_iid, _r))
for _r in [ID_BOROOT] + MK_FROOTS:
    for _x in ROOTS[_r]["Interactions"]:
        if _x not in INTS:
            _mk12.append("%s -> %s" % (_r, _x))
assert INTS[ID_MK_VAULT_LAUNCH]["ProjectileId"] in PRJS and INTS[ID_MK_RISE_LAUNCH]["ProjectileId"] in PRJS
assert not _mk12, "0.1.12 reference closure: %s" % _mk12[:6]
MK12_FILES = sorted([P_MKINT % i for i in MK_INT_IDS] + [P_PRJ % p for p in MK_PRJS])
MK12_CHANGED = sorted([P_BOROOT % ID_BOROOT] + [P_FROOT % r for r in MK_FROOTS] + [P_ANIM % ANIM_FIST])
assert all(p in ASSETS for p in MK12_FILES + MK12_CHANGED) and len(MK12_FILES) == 17 and len(MK12_CHANGED) == 14
# the Bo / fist hit tables the moves scale from (read from our own chains above, never typed in)
MK_BO_TAB = [("Weapon_Bo_" + m, float(BO[m]["hit"])) for m in BO_METALS] + [(i, float(VBO_HIT[0])) for i in VBO_IDS]
MK_FIST_TAB = [("Weapon_Fist_Gauntlets_" + m, float(GAUNT[m]["jab"])) for m in GAUNT_METALS] + [("Weapon_Fist_Wraps_" + c, float(WRAP[c]["jab"])) for c, _col, _k, _p in WRAPS]
assert len(MK_BO_TAB) == 9 and len(MK_FIST_TAB) == 12 and all(h_ > 0.0 for i_, h_ in MK_BO_TAB + MK_FIST_TAB)
print("0.1.12 monk moves: Bo hold %s s -> %s (marker %s), fist hold %s s -> %s (marker %s); %d new files, %d changed (the Bo root, 12 fist roots, "
      "the Fist animation set: %d third-person files)" % (num(MK_BO_HOLD) if "num" in dir() else MK_BO_HOLD, ID_MK_VAULT_LAUNCH, MK_VAULT_MARK, MK_FIST_HOLD,
                                                          ID_MK_RISE_LAUNCH, MK_RISE_MARK, len(MK12_FILES), len(MK12_CHANGED), len(MK_TP)))
'''
rep('''# ================================================================= the SET jars, SkyySkills (anchor + handover), the clash scan''',
    ASSET_PY + '''# ================================================================= the SET jars, SkyySkills (anchor + handover), the clash scan''')
rep('''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS)) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) + 1 + len(BK_PRJS) + len(SS_PRJS) == len(PRJS) \\
    and set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS) == set(PRJS)''',
    '''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS + MK_PRJS)) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) + 1 + len(BK_PRJS) + len(SS_PRJS) + len(MK_PRJS) == len(PRJS) \\
    and set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS + MK_PRJS) == set(PRJS)          # 0.1.12: + the 2 Monk markers''')

# ---------------------------------------------------------------------------------------------------------------- the config file + rows
rep('''] + [x for _r in CFG_SS for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + SS_TAB_LINES + [
''', '''] + [x for _r in CFG_SS for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + SS_TAB_LINES + [
    "",
    "# ---- Monk moves (SkyyArmory 0.1.12; Skyy 2026-10-08 'start building the monk moves'): Bo staff hold = Pole-Vault + skipping bounds, fist hold = Rising Strike",
] + [x for _r in CFG_MK for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
''')
rep('''("shadow", "Dagger Shadow Step"), ("stun", "Monk stunlock"),
            ("monk", "Monk weapons (fixed)"),''', '''("shadow", "Dagger Shadow Step"), ("stun", "Monk stunlock"),
            ("monk", "Monk moves + weapons"),''')
rep('''- no charged attack (0.1.11: the magic shot is gone; Pole-Vault comes later) - Lv %d-%d''', '''- hold = Pole-Vault (0.1.12, the rows above) - Lv %d-%d''')
rep('''"Hit before levels, level band, recipe. Pole-Vault comes later."''', '''"Hit before levels, level band, recipe. The hold = Pole-Vault (the rows above)."''')
rep('''FIXED_VAL = dict((f[0], f[3]) for f in FIXED)
''', '''FIXED.append(("fixed.monk.keys", "Monk move keys (fixed in the jar)", "monk",
              "Bo staffs: hold the attack %s s + release = Pole-Vault, jump as you land = bound; fists: hold %s s + release = Rising Strike; "
              "crouch in the air = the free air jump (vault) / Plunge Punch (near the top)" % (num(MK_BO_HOLD), num(MK_FIST_HOLD)),
              "Client-predicted holds (the Bo = the vanilla staff charge, fists = the dagger Shadow Step hold)."))
FIXED.append(("fixed.monk.debug", "Monk move numbers (admin)", "monk", "/armory debug monk on|off",
              "Each Monk move then prints its measured numbers (distance, height, air time, kicks, costs) in chat."))
FIXED_VAL = dict((f[0], f[3]) for f in FIXED)
''')

# ---------------------------------------------------------------------------------------------------------------- ArmoryDefs + ArmoryCfg
rep('''          "public static final double SS_MELEE = %r;" % SS_MELEE):          # fix round: the melee reach of a dagger hit
    F(dfs, f)
''', '''          "public static final double SS_MELEE = %r;" % SS_MELEE):          # fix round: the melee reach of a dagger hit
    F(dfs, f)
for f in ("public static final String MK_VAULT_MARK = %s;" % jstr(MK_VAULT_MARK), "public static final int MK_VAULT_CODE = %d;" % MK_VAULT_CODE,
          "public static final String MK_RISE_MARK = %s;" % jstr(MK_RISE_MARK), "public static final int MK_RISE_CODE = %d;" % MK_RISE_CODE):          # 0.1.12
    F(dfs, f)
''')
rep('''  m.put(SS_MARK, Integer.valueOf(SS_CODE));          // 0.1.8: the Shadow Step marker
''', '''  m.put(SS_MARK, Integer.valueOf(SS_CODE));          // 0.1.8: the Shadow Step marker
  m.put(MK_VAULT_MARK, Integer.valueOf(MK_VAULT_CODE));          // 0.1.12: the Monk Pole-Vault marker
  m.put(MK_RISE_MARK, Integer.valueOf(MK_RISE_CODE));            // 0.1.12: the Monk Rising Strike marker
''')
rep('''F(cfg, "public static volatile String SHADOW_TEXT = \\"\\";")          # 0.1.8
''', '''F(cfg, "public static volatile String SHADOW_TEXT = \\"\\";")          # 0.1.8
F(cfg, "public static volatile String MONK_TEXT = \\"\\";")          # 0.1.12
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
exec(CFG_MK_PY, _ns)          # the row table (plain Python) -> the loader lines of ArmoryCfg.apply
APPLY_MK = "\n".join(apply_line(r) for r in _ns["CFG_MK"])
rep('''  SHADOW_TEXT = shadowText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:shadow", SHADOW_TEXT); } catch (Throwable tss) { }
''', '''  SHADOW_TEXT = shadowText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:shadow", SHADOW_TEXT); } catch (Throwable tss) { }
''' + APPLY_MK + '''
  MONK_TEXT = monkText();          // 0.1.12
  try { @PKG@.ArmoryDefs.bridge().put("armory:monk", MONK_TEXT); } catch (Throwable tmk) { }
''')
rep('''M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''', '''# 0.1.12: the Monk moves' live numbers (bridge armory:monk, the start line)
M(cfg, r"""
public static String monkText() {
  return "monk moves " + (MK_ON ? "on" : "OFF") + " - Pole-Vault (Bo hold): lunge " + cfmt(MK_LUNGE) + " in " + cfmt(MK_LUNGE_T) + " s, " + cfmt(MK_VH) + " up x "
    + cfmt(MK_VD) + " forward (push x" + cfmt(MK_BOOST) + "), kick " + cfmt(MK_KICK) + "x a Bo hit within " + cfmt(MK_KREACH) + " + the enemy width, "
    + cfmt(MK_VST) + " Stamina + " + cfmt(MK_VMA) + " Mana, air jump " + (MK_AIRJUMP ? "on" : "off") + "; bounds " + cfmt(MK_BBEFORE) + " s before / "
    + cfmt(MK_BAFTER) + " s after a landing, " + cfmt(MK_BDIST) + " + " + cfmt(MK_BPER) + " per block fallen (cap +" + cfmt(MK_BCAP) + "), x" + cfmt(MK_BH)
    + " jump, " + cfmt(MK_BST) + " + " + cfmt(MK_BMA) + "; Rising Strike (fist hold): " + cfmt(MK_RH) + " up, drift " + cfmt(MK_RFWD) + " b/s, hit "
    + cfmt(MK_RDMG) + "x a jab in " + cfmt(MK_RLEN) + " x " + cfmt(MK_RWID) + ", knock-up " + cfmt(MK_RUP) + ", hang " + cfmt(MK_RHANG) + " s, air hits fling "
    + cfmt(MK_RFLING) + ", " + cfmt(MK_RST) + " + " + cfmt(MK_RMA) + "; plunge " + cfmt(MK_PSPD) + " b/s, slam " + cfmt(MK_PDMG) + "x in " + cfmt(MK_PRAD)
    + "; flowing fall " + MK_FLOW + "% slower, " + MK_FLOWDMG + "% less fall damage; no Acrobatics XP meanwhile (bridge armory:monkmove:<uuid>)";
}""")
M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''')

# ---------------------------------------------------------------------------------------------------------------- engine members (probed)
rep('''print("engine members probed: %d" % len(PROBED))
''', '''# ---- 0.1.12 the Monk moves (the SkyyMonkProbe 0.1 paths, VERIFIED in game 2026-10-08; every member probed): movement edges, the client
# velocity, a Set per tick, the jump force, gravity, the fall distance, PHYSICAL hits, the re-dealt held FALL damage, the admin command
T.update({"MMG": "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementManager",
          "MVS": "com.hypixel.hytale.protocol.MovementSettings",
          "PHC": "com.hypixel.hytale.server.core.modules.physics.util.PhysicsConstants",
          "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
          "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
          "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
          "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
          "ACMD": "com.hypixel.hytale.server.core.command.system.AbstractCommand",
          "CREG": "com.hypixel.hytale.server.core.command.system.CommandRegistry"})
for _c, _m, _r, _a in ((T["MMG"], "getComponentType", T["CTYPE"], []), (T["MMG"], "getSettings", T["MVS"], []),
                       (T["PLA"], "getCurrentFallDistance", "double", []), (T["PLA"], "getComponentType", T["CTYPE"], []),
                       (T["VEL"], "addInstruction", "void", [T["VEC"], T["VCF"], T["CVT"]]), (T["VEL"], "getClientVelocity", T["VEC"], []),
                       (T["DSYS"], "executeDamage", "void", [T["REF"], T["CB"], T["DMG"]]), (T["DMG"], "<init>", "void", [T["DSRC"], T["DCS"], "float"]),
                       (T["DMG"], "getCause", T["DCS"], []), (T["DMG"], "setCancelled", "void", ["boolean"]),
                       (T["PR"], "getUsername", S_, []), (T["PR"], "sendMessage", "void", ["com.hypixel.hytale.server.core.Message"]),
                       (T["NPC"], "getRoleName", S_, []), (T["BOX"], "width", "double", []), (T["BOX"], "depth", "double", []),
                       (T["ACMD"], "requirePermission", "void", [S_]), (T["ACMD"], "setPermissionGroups", "void", ["java.lang.String[]"]),
                       (T["ACMD"], "addUsageVariant", "void", [T["ACMD"]]),
                       (T["ACMD"], "withRequiredArg", T["RA"], [S_, S_, "com.hypixel.hytale.server.core.command.system.arguments.types.ArgumentType"]),
                       (T["CTX"], "get", O_, ["com.hypixel.hytale.server.core.command.system.arguments.system.Argument"]),
                       (PB, "getCommandRegistry", T["CREG"], []), (T["CREG"], "registerCommand", "com.hypixel.hytale.server.core.command.system.CommandRegistration", [T["ACMD"]]),
                       (T["APC"], "<init>", "void", [S_, S_]), (T["APC"], "<init>", "void", [S_])):
    probe_sig(_c, _m, _r, _a)
for _c, _f in ((T["MST"], "onGround"), (T["MST"], "jumping"), (T["MST"], "crouching"), (T["MST"], "flying"), (T["MST"], "inFluid"),
               (T["MST"], "swimming"), (T["MVS"], "jumpForce"), (T["PHC"], "GRAVITY_ACCELERATION"), (T["DCS"], "PHYSICAL"), (T["DCS"], "FALL"),
               (T["DMG"], "NULL_SOURCE"), (T["ATY"], "STRING")):
    _fld = pool.get(_c).getField(_f)
    assert JMod.isPublic(_fld.getModifiers()), "%s.%s is not public" % (_c, _f)
    PROBED.append("%s.%s" % (_c.rsplit(".", 1)[1], _f))
_ape = [m for m in pool.get(T["APC"]).getDeclaredMethods() if str(m.getName()) == "execute" and JMod.isAbstract(m.getModifiers())]
assert len(_ape) == 1 and str(_ape[0].getSignature()) == "(L%s;L%s;L%s;L%s;L%s;)V" % tuple(T[k].replace(".", "/") for k in ("CTX", "ST", "REF", "PR", "WLD")), \\
    "AbstractPlayerCommand.execute changed: %s" % [str(m.getSignature()) for m in _ape]
PROBED.append("0.1.12: AbstractPlayerCommand.execute(CommandContext, Store, Ref, PlayerRef, World) (the SkyyMonkProbe command shape)")
print("engine members probed: %d" % len(PROBED))
''')

# ---------------------------------------------------------------------------------------------------------------- the Java (MonkState, Monk, the command)
MONK_JAVA = r'''# ---------------------------------------------------------------- 0.1.12 THE MONK MOVES (the SkyyMonkProbe 0.1 paths, made real; tools/armory_0_1_12_patch.py)
msta = pool.makeClass(PKG + ".MonkState")
monk = pool.makeClass(PKG + ".Monk")
mcmd = pool.makeClass(PKG + ".ArmoryCmd", pool.get(T["APC"]))
mdbg = pool.makeClass(PKG + ".ArmoryDbgCmd", pool.get(T["APC"]))
ALL += [msta, monk, mdbg, mcmd]
for f in ("public java.util.UUID u;", "public @REF@ ref;", "public @ST@ st;",
          # move: 0 none, 1 lunge, 2 vault in the air, 3 rising, 4 hang, 5 plunge, 6 the fall after the hang (no plunge)
          "public int move;", "public String item;", "public double hit;", "public double hx;", "public double hz;", "public long t0;",
          "public long lungeUntil;", "public double x0;", "public double y0;", "public double z0;", "public double lungeD;",
          "public double px;", "public double py;", "public double pz;", "public boolean havePrev;",
          "public java.util.HashSet kicked;", "public int kicks;", "public double kickAmt;", "public double paidS;", "public double paidM;",
          "public boolean flow;", "public long flowTop;", "public long flowArm;", "public boolean flowRose;",
          "public long airUntil;", "public boolean airUsed;",
          "public boolean prevGround;", "public boolean prevJump;", "public boolean prevCrouch;",
          "public long leftAt;", "public long lastLand;", "public double airTopY;", "public double fallMax;", "public double landFell;",
          "public long airPress;", "public boolean wasFalling;",
          "public boolean chain;", "public boolean boundDone;", "public int bounds;", "public long lastBoundAt;",
          "public double pendFall;", "public long pendFallAt;", "public long noFallUntil;",
          "public java.util.ArrayList ups;", "public int upsHit;", "public boolean rsRose;", "public long rsApex;", "public long rsT;", "public int flings;",
          "public double minVy;", "public double plungeY0;", "public long plungeT0;", "public double mobMinY;", "public double mobMaxY;",
          # the flight record (debug numbers): 0 none, 1 vault, 2 bound, 4 rise
          "public int fk;", "public double fx0;", "public double fy0;", "public double fz0;", "public double fTop;", "public long fT0;",
          "public boolean fLeft;", "public double fWantD;", "public double fWantH;", "public String fCost;",
          "public @REF@ flung;", "public double flX;", "public double flZ;", "public long flAt;", "public long last;"):
    F(msta, f)
C(msta, r"""
public MonkState(java.util.UUID u, @REF@ r, @ST@ st) {
  this.u = u;
  this.ref = r;
  this.st = st;
  this.prevGround = true;
  this.kicked = new java.util.HashSet();
  this.ups = new java.util.ArrayList();
  this.item = "";
  this.fCost = "";
}""")
for f in ("public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap DEBUG = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap FLAGGED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final String KEY = \"armory:monkmove:\";",
          "public static final long FLAG_MS = %dL;" % MK_FLAG_MS, "public static final double FLING_PER = %r;" % MK_FLING_PER,
          "public static final String[] BO_IDS = %s;" % jarr([i_ for i_, h_ in MK_BO_TAB]), "public static final double[] BO_HIT = %s;" % jdbls([h_ for i_, h_ in MK_BO_TAB]),
          "public static final String[] FIST_IDS = %s;" % jarr([i_ for i_, h_ in MK_FIST_TAB]), "public static final double[] FIST_HIT = %s;" % jdbls([h_ for i_, h_ in MK_FIST_TAB]),
          "public static volatile long CLOCK = 0L;",          # HARNESS SEAM ONLY (0 in the game = the wall clock)
          "public static volatile java.util.List SINK = null;",          # HARNESS SEAM ONLY (null in the game): every debug line
          "public static volatile long MARKS = 0L;", "public static volatile long VAULTS = 0L;", "public static volatile long BOUNDS = 0L;",
          "public static volatile long RISES = 0L;", "public static volatile long PLUNGES = 0L;", "public static volatile long KICKS = 0L;",
          "public static volatile long FLINGS = 0L;", "public static volatile long REFUSED = 0L;", "public static volatile long REFUNDS = 0L;",
          "public static volatile long HELD = 0L;", "public static volatile long FORGIVEN = 0L;", "public static volatile long REDEALT = 0L;",
          "public static volatile long CUT = 0L;", "public static volatile long FLOWED = 0L;", "public static volatile long AIRJUMPS = 0L;",
          "public static volatile String LAST_WHY = \"\";", "public static volatile long SWEPT = 0L;", "public static volatile long STALE = 0L;"):
    F(monk, f)
M(monk, r"""public static long now() { long c = CLOCK; return c != 0L ? c : System.currentTimeMillis(); }""")
M(monk, r"""public static void warn(String key, String msg) { @PKG@.ArmoryLog.warnOnce("monk:" + key, msg); }""")
M(monk, r"""
public static String f1(double v) {
  if (v != v) return "?";
  long t = Math.round(v * 10.0);
  String sign = t < 0L ? "-" : "";
  if (t < 0L) t = 0L - t;
  return sign + (t / 10L) + "." + (t % 10L);
}""")
# ---- PURE maths (the probe's MpLogic; the harness runs them on plain numbers)
M(monk, r"""
public static double vyFor(double h, double g) {
  if (!(h > 0.0) || !(g > 0.0)) return 0.0;
  return Math.sqrt(2.0 * g * h);
}""")
M(monk, r"""
public static double hSpeed(double dist, double vy, double g) {
  if (!(vy > 0.0) || !(g > 0.0) || !(dist > 0.0)) return 0.0;
  return dist / (2.0 * vy / g);
}""")
M(monk, r"""
public static double boundDist(double base, double per, double cap, double fell) {
  double e = fell > 0.0 ? fell * per : 0.0;
  if (e > cap) e = cap;
  if (e < 0.0) e = 0.0;
  return base + e;
}""")
# a press at 'press' ms is timed for a landing at 'land' ms: from 'before' ms before to 'after' ms after (0 = no such event)
M(monk, r"""
public static boolean timed(long land, long press, long before, long after) {
  if (land <= 0L || press <= 0L) return false;
  long d = press - land;
  return d >= 0L - before && d <= after;
}""")
# the flowing fall: the speed t ms after the top under (1 - pct) x g (never upward)
M(monk, r"""
public static double slowVy(double pct, double g, long ms) {
  if (ms <= 0L) return 0.0;
  double f = 1.0 - pct;
  if (f < 0.0) f = 0.0;
  if (f > 1.0) f = 1.0;
  return 0.0 - f * g * ((double) ms / 1000.0);
}""")
M(monk, r"""
public static boolean inCone(double ox, double oz, double lx, double lz, double len, double half) {
  double f = ox * lx + oz * lz;
  if (f < 0.0 || f > len) return false;
  double s = ox * (0.0 - lz) + oz * lx;
  if (s < 0.0) s = 0.0 - s;
  return s <= half;
}""")
# THE VAULT KICK (probe M6 missed a Trork Mauler: its sphere tested the mob's FEET point): your body (feet moving a -> b, height ph) touches an
# enemy's body (feet m, width w, height h) when, somewhere on the segment (sampled every 0.25 block), the horizontal distance to its centre is
# <= reach + its own width AND the height ranges overlap
M(monk, r"""
public static boolean kickTest(double ax, double ay, double az, double bx, double by, double bz, double mx, double my, double mz, double mw, double mh,
                               double reach, double ph) {
  double dx = bx - ax;
  double dy = by - ay;
  double dz = bz - az;
  double len = Math.sqrt(dx * dx + dy * dy + dz * dz);
  int n = (int) Math.ceil(len / 0.25);
  if (n < 1) n = 1;
  if (n > 256) n = 256;
  double lim = reach + mw;
  for (int i = 0; i <= n; i++) {
    double t = (double) i / (double) n;
    double x = ax + dx * t;
    double y = ay + dy * t;
    double z = az + dz * t;
    double hx = x - mx;
    double hz = z - mz;
    if (hx * hx + hz * hz > lim * lim) continue;
    if (y < my + mh && y + ph > my) return true;
  }
  return false;
}""")
# the stunlock's boss words (Stun.bossRole's rule: a WHOLE part of the role name split at _) - a boss is hit but never lifted
M(monk, r"""
public static boolean bossWord(String role, String words) {
  if (role == null || words == null) return false;
  String r = "_" + role.trim().toLowerCase() + "_";
  String[] ws = words.split(",");
  for (int i = 0; i < ws.length; i++) {
    String w = ws[i].trim().toLowerCase();
    if (w.length() > 0 && r.indexOf("_" + w + "_") >= 0) return true;
  }
  return false;
}""")
M(monk, r"""
public static double hitOf(String[] ids, double[] hits, String item) {
  if (item == null) return 0.0;
  for (int i = 0; i < ids.length; i++) if (ids[i].equals(item)) return hits[i];
  return 0.0;
}""")
M(monk, "public static double boHit(String item) { return hitOf(BO_IDS, BO_HIT, item); }")
M(monk, "public static double fistHit(String item) { return hitOf(FIST_IDS, FIST_HIT, item); }")
# ---- engine glue (world thread; never throws)
M(monk, r"""
public static double grav() {
  try { double g = (double) @PHC@.GRAVITY_ACCELERATION; if (g > 0.0) return g; } catch (Throwable t) { }
  return 32.0;
}""")
M(monk, r"""
public static double jumpForce(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @MMG@.getComponentType());
    @MVS@ s = o instanceof @MMG@ ? ((@MMG@) o).getSettings() : null;
    if (s != null && s.jumpForce > 0.0f) return (double) s.jumpForce;
  } catch (Throwable t) { }
  return 11.8;
}""")
M(monk, r"""
public static @MST@ moves(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @MSC@.getComponentType());
    return o instanceof @MSC@ ? ((@MSC@) o).getMovementStates() : null;
  } catch (Throwable t) { return null; }
}""")
M(monk, r"""
public static double[] cvel(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @VEL@.getComponentType());
    @VEC@ c = o instanceof @VEL@ ? ((@VEL@) o).getClientVelocity() : null;
    if (c == null) return null;
    return new double[] { c.x, c.y, c.z };
  } catch (Throwable t) { return null; }
}""")
M(monk, r"""
public static double fallDist(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @PLA@.getComponentType());
    return o instanceof @PLA@ ? ((@PLA@) o).getCurrentFallDistance() : 0.0;
  } catch (Throwable t) { return 0.0; }
}""")
# the Acrobatics flag for SkyySkills 0.4.22 (plain java.lang: a Long = epoch ms until)
M(monk, r"""
public static void flag(java.util.UUID u, long until) {
  if (u == null) return;
  try {
    @PKG@.ArmoryDefs.bridge().put(KEY + u.toString(), Long.valueOf(until));
    FLAGGED.put(u, Boolean.TRUE);
  } catch (Throwable t) { }
}""")
M(monk, r"""
public static void unflagAll() {
  try {
    java.util.Map b = @PKG@.ArmoryDefs.bridge();
    java.util.Iterator it = FLAGGED.keySet().iterator();
    while (it.hasNext()) b.remove(KEY + String.valueOf(it.next()));
  } catch (Throwable t) { }
  FLAGGED.clear();
}""")
M(monk, r"""
public static void dbg(java.util.UUID u, @PR@ pr, String text) {
  if (u == null || text == null || !DEBUG.containsKey(u)) return;
  java.util.List sink = SINK;
  if (sink != null) sink.add(text);
  @PKG@.ArmoryLog.info("monk debug " + (pr == null ? u.toString() : pr.getUsername()) + ": " + text);
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[Monk] " + text).color("#9fd3ff")); } catch (Throwable t) { }
}""")
M(monk, r"""
public static String stat(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @ESM@.getComponentType());
    if (!(o instanceof @ESM@)) return "stats unreadable";
    @ESV@ s = ((@ESM@) o).get(@DST@.getStamina());
    @ESV@ m = ((@ESM@) o).get(@DST@.getMana());
    return "left: Stamina " + (s == null ? "-" : f1((double) s.get())) + ", Mana " + (m == null ? "-" : f1((double) m.get()));
  } catch (Throwable t) { return "stats unreadable"; }
}""")
# an enemy for a Monk move: 0 = a mob you may hit (ArmoryTrav.kind's enemy, not protected: traders / invulnerable), 1 = an enemy player (PvP
# on + trav.players, never party), -1 = no
M(monk, r"""
public static int foe(@CAC@ acc, @REF@ t, @REF@ me, java.util.UUID u, boolean pvp) {
  if (t == null || me == null || t.equals(me)) return -1;
  if (@PKG@.ArmoryTrav.kind(acc, t, me, u, pvp) != 0) return -1;
  if (@PKG@.Kunai.prOf(acc, t) != null) return 1;
  if (@PKG@.Shadow.protect(acc, t)) return -1;
  return 0;
}""")
M(monk, r"""
public static String roleOf(@CAC@ acc, @REF@ t) {
  try {
    Object o = acc.getComponent(t, @NPC@.getComponentType());
    return o instanceof @NPC@ ? ((@NPC@) o).getRoleName() : null;
  } catch (Throwable x) { return null; }
}""")
M(monk, r"""
public static boolean liftable(@CAC@ acc, @REF@ t) {
  String role = roleOf(acc, t);
  return role != null && !bossWord(role, @PKG@.ArmoryCfg.STUN_BOSS);
}""")
M(monk, r"""
public static double[] body(@CAC@ acc, @REF@ t) {
  try {
    Object o = acc.getComponent(t, @BBX@.getComponentType());
    if (o instanceof @BBX@ && ((@BBX@) o).getBoundingBox() != null) {
      @BOX@ b = ((@BBX@) o).getBoundingBox();
      double w = Math.max(b.width(), b.depth());
      double h = b.height();
      return new double[] { w > 0.0 && w < 16.0 ? w : 1.0, h > 0.0 && h < 32.0 ? h : 1.8 };
    }
  } catch (Throwable x) { }
  return new double[] { 1.0, 1.8 };
}""")
# one Monk hit through the WHOLE damage pipeline: Damage$EntitySource(you) + PHYSICAL = the melee shape (SkyyGear levels it from the weapon in
# your hand, armour applies); MINE-marked so the burst / backstab / Hard Knuckles hooks leave it alone
M(monk, r"""
public static boolean hit(@CB@ buf, @REF@ target, @REF@ me, double amount) {
  try {
    if (!(amount > 0.0) || me == null || !me.isValid() || target == null || !target.isValid()) return false;
    @DCS@ cause = @DCS@.PHYSICAL;
    if (cause == null) return false;
    @DMG@ d = new @DMG@((@DSRC@) new @DENT@(me), cause, (float) amount);
    if (@PKG@.ArmoryTrav.MINE.size() > 4096) @PKG@.ArmoryTrav.MINE.clear();
    @PKG@.ArmoryTrav.MINE.put(d, Boolean.TRUE);
    @DSYS@.executeDamage(target, buf, d);
    return true;
  } catch (Throwable t) { warn("hit", "a Monk move hit failed (" + t + ")"); return false; }
}""")
# a held FALL damage re-dealt the vanilla way (DamageSystems$FallDamagePlayers: Damage.NULL_SOURCE + FALL), MINE-marked (onFall skips it)
M(monk, r"""
public static boolean fallHit(@CB@ buf, @REF@ me, double amount) {
  try {
    if (!(amount > 0.0) || me == null || !me.isValid()) return false;
    @DCS@ cause = @DCS@.FALL;
    if (cause == null) return false;
    @DMG@ d = new @DMG@(@DMG@.NULL_SOURCE, cause, (float) amount);
    @PKG@.ArmoryTrav.MINE.put(d, Boolean.TRUE);
    @DSYS@.executeDamage(me, buf, d);
    return true;
  } catch (Throwable t) { warn("fall", "a held fall damage could not be dealt (" + t + ")"); return false; }
}""")
M(monk, r"""
public static @PKG@.MonkState state(java.util.UUID u, @REF@ r, @ST@ st) {
  @PKG@.MonkState s = (@PKG@.MonkState) STATES.get(u);
  if (s == null || s.st != st) {
    s = new @PKG@.MonkState(u, r, st);
    STATES.put(u, s);
  }
  s.ref = r;
  return s;
}""")
M(monk, r"""
public static void armFlow(@PKG@.MonkState s, long now) {
  s.flow = true;
  s.flowTop = 0L;
  s.flowArm = now;
  s.flowRose = false;
}""")
M(monk, r"""
public static void flight(@PKG@.MonkState s, int kind, @VEC@ p, double wantD, double wantH, long now, String cost) {
  s.fk = kind;
  s.fx0 = p.x; s.fy0 = p.y; s.fz0 = p.z; s.fTop = p.y;
  s.fT0 = now;
  s.fLeft = false;
  s.fWantD = wantD;
  s.fWantH = wantH;
  s.fCost = cost == null ? "" : cost;
}""")
M(monk, r"""
public static String pct(double got, double want) {
  if (!(want > 0.0)) return "";
  return " (target " + f1(want) + ", " + Math.round(got / want * 100.0) + "%)";
}""")
# your horizontal aim now (the head direction; the harness seam Leap.LOOK first), else the given fallback
M(monk, r"""
public static double[] aimH(@CAC@ acc, @REF@ r, java.util.UUID u, double fx, double fz) {
  double[] a = null;
  try { if (acc instanceof @CB@) a = @PKG@.Leap.aim((@CB@) acc, r, u, null); } catch (Throwable t) { a = null; }
  double x = a == null ? fx : a[3];
  double z = a == null ? fz : a[5];
  double l = Math.sqrt(x * x + z * z);
  if (!(l > 1.0E-4)) { x = fx; z = fz; l = Math.sqrt(x * x + z * z); }
  if (!(l > 1.0E-4)) return new double[] { 0.0, 1.0 };
  return new double[] { x / l, z / l };
}""")
# a move that did not move you (under 1 block) costs nothing (LOCKED 2026-10-05: "a traversal that does not move you costs nothing")
M(monk, r"""
public static boolean refund(@PKG@.MonkState s, @CAC@ acc, @REF@ r, @VEC@ p, @PR@ pr, String what) {
  if (p == null || (!(s.paidS > 0.0) && !(s.paidM > 0.0))) return false;
  double dx = p.x - s.x0;
  double dz = p.z - s.z0;
  double up = s.fTop - s.y0;
  if (Math.sqrt(dx * dx + dz * dz) >= 1.0 || up >= 1.0 || Math.abs(p.y - s.y0) >= 1.0) { s.paidS = 0.0; s.paidM = 0.0; return false; }
  @PKG@.ArmoryTrav.addStat(acc, r, @DST@.getStamina(), s.paidS);
  @PKG@.ArmoryTrav.addStat(acc, r, @DST@.getMana(), s.paidM);
  REFUNDS = REFUNDS + 1L;
  dbg(s.u, pr, what + " did not move you - " + f1(s.paidS) + " Stamina + " + f1(s.paidM) + " Mana given back.");
  s.paidS = 0.0;
  s.paidM = 0.0;
  return true;
}""")
M(monk, r"""
public static boolean ready(@PKG@.MonkState s, @PR@ pr, @CB@ buf, @REF@ r, java.util.UUID u, String item, String what, long now) {
  if (!@PKG@.ArmoryCfg.MK_ON) { LAST_WHY = "monk moves off"; return false; }
  if (!@PKG@.ArmoryTrav.allowed(u, item)) { REFUSED = REFUSED + 1L; LAST_WHY = what + ": class lock"; dbg(u, pr, what + ": your class may not use " + item + " - nothing spent."); return false; }
  if (@PKG@.ArmoryTrav.dead(buf, r) || @PKG@.Leap.mounted(buf, r)) { REFUSED = REFUSED + 1L; LAST_WHY = what + ": dead or mounted"; return false; }
  @MST@ ms = moves(buf, r);
  if (ms == null || !ms.onGround || ms.flying || ms.inFluid || ms.swimming) {
    REFUSED = REFUSED + 1L;
    LAST_WHY = what + ": not on the ground";
    @PKG@.ArmoryTrav.tell(pr, what + " needs solid ground under you - nothing spent.");
    dbg(u, pr, what + ": only from the ground (not in the air, flying or in water) - nothing spent.");
    return false;
  }
  return true;
}""")
M(monk, r"""
public static boolean pay(@PKG@.MonkState s, @PR@ pr, @CB@ buf, @REF@ r, double st, double ma, String what) {
  if (@PKG@.Leap.take(buf, r, st, ma) == 0) {
    REFUSED = REFUSED + 1L;
    LAST_WHY = what + ": too little Stamina or Mana";
    @PKG@.ArmoryTrav.tell(pr, "Not enough Stamina or Mana for " + what + " - " + f1(st) + " Stamina + " + f1(ma) + " Mana.");
    dbg(s.u, pr, what + " refused: " + f1(st) + " Stamina + " + f1(ma) + " Mana needed (" + stat(buf, r) + ").");
    return false;
  }
  s.paidS = st;
  s.paidM = ma;
  return true;
}""")
M(monk, r"""
public static void reset(@PKG@.MonkState s, String item, double hit, double hx, double hz, @VEC@ p, long now) {
  s.item = item;
  s.hit = hit;
  s.hx = hx;
  s.hz = hz;
  s.t0 = now;
  s.x0 = p.x; s.y0 = p.y; s.z0 = p.z;
  s.px = p.x; s.py = p.y; s.pz = p.z;
  s.havePrev = true;
  s.kicked.clear();
  s.kicks = 0;
  s.ups.clear();
  s.upsHit = 0;
  s.flings = 0;
  s.chain = false;
  s.bounds = 0;
  s.flow = false;
  s.airUntil = 0L;
  s.airUsed = false;
  s.lastLand = 0L;
  s.airPress = 0L;
  s.fk = 0;
  s.lungeD = 0.0;
  s.minVy = 0.0;
}""")
# ---- (1) THE POLE-VAULT: the lunge (a Set every tick), then the vault Set; the kicks are swept every tick (sweep)
M(monk, r"""
public static void launchVault(@PKG@.MonkState s, @PR@ pr, @CB@ buf, @REF@ r, @VEC@ p, long now) {
  double g = grav();
  double vy = vyFor(@PKG@.ArmoryCfg.MK_VH, g);
  double vh = hSpeed(@PKG@.ArmoryCfg.MK_VD, vy, g) * @PKG@.ArmoryCfg.MK_BOOST;
  @PKG@.Leap.vel(buf, r, s.hx * vh, vy, s.hz * vh, false);
  double dx = p.x - s.x0;
  double dz = p.z - s.z0;
  s.lungeD = Math.sqrt(dx * dx + dz * dz);
  s.move = 2;
  flight(s, 1, p, @PKG@.ArmoryCfg.MK_VD, @PKG@.ArmoryCfg.MK_VH, now, f1(s.paidS) + " Stamina + " + f1(s.paidM) + " Mana");
  armFlow(s, now);
  s.airUntil = @PKG@.ArmoryCfg.MK_AIRJUMP ? now + 4000L : 0L;
  s.airUsed = false;
  s.chain = true;          // the bounds: the first landing after the vault may bound
  s.lastLand = 0L;
  s.airPress = 0L;
  s.boundDone = false;
  s.bounds = 0;
}""")
M(monk, r"""
public static boolean vault(@PKG@.MonkState s, @PR@ pr, @CB@ buf, @REF@ r, java.util.UUID u, String item, double[] d, long now) {
  double hit = boHit(item);
  if (!(hit > 0.0)) { LAST_WHY = "vault: no Bo staff in hand"; dbg(u, pr, "Pole-Vault: no Bo staff in your hand (" + item + ") - nothing done."); return false; }
  if (!ready(s, pr, buf, r, u, item, "Pole-Vault", now)) return false;
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, r);
  if (p == null) return false;
  if (!pay(s, pr, buf, r, @PKG@.ArmoryCfg.MK_VST, @PKG@.ArmoryCfg.MK_VMA, "Pole-Vault")) return false;
  double[] h = aimH(buf, r, u, d == null ? 0.0 : d[0], d == null ? 1.0 : d[2]);
  reset(s, item, hit, h[0], h[1], p, now);
  s.kickAmt = hit * @PKG@.ArmoryCfg.MK_KICK;
  s.move = 1;
  s.lungeUntil = now + Math.round(@PKG@.ArmoryCfg.MK_LUNGE_T * 1000.0);
  VAULTS = VAULTS + 1L;
  LAST_WHY = "vault";
  dbg(u, pr, "Pole-Vault: paid " + f1(s.paidS) + " Stamina + " + f1(s.paidM) + " Mana (" + stat(buf, r) + "); lunge " + f1(@PKG@.ArmoryCfg.MK_LUNGE)
      + " in " + f1(@PKG@.ArmoryCfg.MK_LUNGE_T) + " s, kick " + f1(s.kickAmt) + " each.");
  if (!(@PKG@.ArmoryCfg.MK_LUNGE > 0.0)) launchVault(s, pr, buf, r, p, now);
  return true;
}""")
M(monk, r"""
public static void lungeTick(@PKG@.MonkState s, @PR@ pr, @CB@ buf, @REF@ r, @VEC@ p, double[] cv, long now) {
  if (now >= s.lungeUntil) { launchVault(s, pr, buf, r, p, now); return; }
  double t = @PKG@.ArmoryCfg.MK_LUNGE_T;
  double v = t > 0.0 ? @PKG@.ArmoryCfg.MK_LUNGE / t : 0.0;
  @PKG@.Leap.vel(buf, r, s.hx * v, cv == null ? 0.0 : cv[1], s.hz * v, false);
}""")
# every tick of the lunge + the vault: each enemy whose body the swept segment (last tick -> now) touches is kicked once
M(monk, r"""
public static void sweep(@PKG@.MonkState s, @PR@ pr, @CB@ buf, @REF@ r, java.util.UUID u, @VEC@ p) {
  if (!s.havePrev) { s.px = p.x; s.py = p.y; s.pz = p.z; s.havePrev = true; }
  double dx = p.x - s.px;
  double dy = p.y - s.py;
  double dz = p.z - s.pz;
  double len = Math.sqrt(dx * dx + dy * dy + dz * dz);
  double reach = @PKG@.ArmoryCfg.MK_KREACH;
  java.util.List l = @PKG@.ArmoryTrav.near(buf, (p.x + s.px) / 2.0, (p.y + s.py) / 2.0, (p.z + s.pz) / 2.0, len / 2.0 + reach + 8.0);
  boolean pvp = @PKG@.ArmoryTrav.pvp(@PKG@.ArmoryTrav.worldOf(buf));
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (s.kicked.contains(t) || foe(buf, t, r, u, pvp) < 0) continue;
    @VEC@ tp = @PKG@.ArmoryTrav.posOf(buf, t);
    if (tp == null) continue;
    double[] b = body(buf, t);
    if (!kickTest(s.px, s.py, s.pz, p.x, p.y, p.z, tp.x, tp.y, tp.z, b[0], b[1], reach, 1.8)) continue;
    s.kicked.add(t);
    if (hit(buf, t, r, s.kickAmt)) { s.kicks = s.kicks + 1; KICKS = KICKS + 1L; }
  }
  s.px = p.x; s.py = p.y; s.pz = p.z;
}""")
# ---- the flowing fall (probe M1: a Set every tick from the top, (1 - flow.slower) x gravity; your own sideways speed kept = you steer)
M(monk, r"""
public static void flowTick(@PKG@.MonkState s, @CB@ buf, @REF@ r, double[] cv, boolean ground, long now) {
  if (!s.flow || cv == null || ground) return;
  if (s.flowTop == 0L) {
    if (cv[1] > 1.0) s.flowRose = true;
    if (cv[1] <= 0.0 && (s.flowRose || now - s.flowArm > 1500L)) s.flowTop = now;
    return;
  }
  double vy = slowVy((double) @PKG@.ArmoryCfg.MK_FLOW / 100.0, grav(), now - s.flowTop);
  if (@PKG@.Leap.vel(buf, r, cv[0], vy, cv[2], false)) FLOWED = FLOWED + 1L;
}""")
# ---- (2) THE BOUND (probe M2): base + per block fallen (cap), 1.4 x a jump, x the push boost; costs or the chain ends
M(monk, r"""
public static void bound(@PKG@.MonkState s, @PR@ pr, @CB@ buf, @REF@ r, @VEC@ p, long now, String how) {
  if (s.boundDone) return;
  s.boundDone = true;
  if (@PKG@.Leap.take(buf, r, @PKG@.ArmoryCfg.MK_BST, @PKG@.ArmoryCfg.MK_BMA) == 0) {
    s.chain = false;
    @PKG@.ArmoryTrav.tell(pr, "Out of Stamina or Mana - the bounds end (" + f1(@PKG@.ArmoryCfg.MK_BST) + " Stamina + " + f1(@PKG@.ArmoryCfg.MK_BMA) + " Mana a bound).");
    dbg(s.u, pr, "Bound refused (" + how + "): too little Stamina / Mana - the chain ENDS after " + s.bounds + " bounds (" + stat(buf, r) + ").");
    return;
  }
  double g = grav();
  double[] h = aimH(buf, r, s.u, s.hx, s.hz);
  double vy = jumpForce(buf, r) * Math.sqrt(@PKG@.ArmoryCfg.MK_BH);
  double d = boundDist(@PKG@.ArmoryCfg.MK_BDIST, @PKG@.ArmoryCfg.MK_BPER, @PKG@.ArmoryCfg.MK_BCAP, s.landFell);
  double vh = hSpeed(d, vy, g) * @PKG@.ArmoryCfg.MK_BOOST;
  @PKG@.Leap.vel(buf, r, h[0] * vh, vy, h[1] * vh, false);
  s.hx = h[0];
  s.hz = h[1];
  s.bounds = s.bounds + 1;
  s.lastBoundAt = now;
  s.wasFalling = false;
  s.airUntil = 0L;          // the free air jump is only the FIRST jump after the vault (LOCKED 2026-10-04)
  armFlow(s, now);
  BOUNDS = BOUNDS + 1L;
  flight(s, 2, p, d, vy * vy / (2.0 * g), now, f1(@PKG@.ArmoryCfg.MK_BST) + " Stamina + " + f1(@PKG@.ArmoryCfg.MK_BMA) + " Mana");
  dbg(s.u, pr, "Bound " + s.bounds + " (" + how + "): fell " + f1(s.landFell) + " -> " + f1(d) + " blocks forward, " + f1(vy * vy / (2.0 * g)) + " high (" + stat(buf, r) + ").");
}""")
# a held FALL damage belongs to THAT landing's bound: from 150 ms before it (an early press bounds in the landing tick) to bound.after + 50 ms
M(monk, r"""
public static boolean boundFor(long bound, long fall, long after) {
  return bound > 0L && fall > 0L && bound >= fall - 150L && bound <= fall + after + 50L;
}""")
M(monk, r"""
public static void heldFall(@PKG@.MonkState s, @PR@ pr, @CB@ buf, @REF@ r, long now) {
  if (s.pendFallAt <= 0L) return;
  long after = Math.round(@PKG@.ArmoryCfg.MK_BAFTER * 1000.0);
  if (s.lastBoundAt >= s.leftAt && boundFor(s.lastBoundAt, s.pendFallAt, after)) {          // a bound of THIS landing (not the one that started the flight)
    FORGIVEN = FORGIVEN + 1L;
    dbg(s.u, pr, "Timed landing: the fall damage " + f1(s.pendFall) + " is forgiven.");
    s.pendFallAt = 0L;
    return;
  }
  if (now - s.pendFallAt <= after + 50L) return;
  double a = s.pendFall * (1.0 - (double) @PKG@.ArmoryCfg.MK_FLOWDMG / 100.0);
  s.pendFallAt = 0L;
  if (fallHit(buf, r, a)) REDEALT = REDEALT + 1L;
  dbg(s.u, pr, "Missed the bound timing: fall damage " + f1(s.pendFall) + " -> " + f1(a) + " (flowing fall -" + @PKG@.ArmoryCfg.MK_FLOWDMG + "%).");
}""")
# ---- the movement edges (probe M2 / M3 with its local fixes 3, 6, 7): bounds at a timed landing, the chain's end, the free air jump
M(monk, r"""
public static void edges(@PKG@.MonkState s, @PR@ pr, @CB@ buf, @REF@ r, @VEC@ p, double[] cv, boolean ground, boolean land, boolean leave,
                         boolean jEdge, boolean cEdge, long now) {
  long before = Math.round(@PKG@.ArmoryCfg.MK_BBEFORE * 1000.0);
  long after = Math.round(@PKG@.ArmoryCfg.MK_BAFTER * 1000.0);
  if (leave || land) s.wasFalling = false;
  if (!ground && !leave && cv != null && cv[1] < -2.0) s.wasFalling = true;
  if (land) {
    s.boundDone = false;
    s.lastLand = now;
    s.landFell = s.fallMax;
    if (s.chain && s.airPress > 0L && timed(now, s.airPress, before, after)) bound(s, pr, buf, r, p, now, "pressed " + (now - s.airPress) + " ms early");
  }
  if (jEdge) {
    if (ground || leave || now - s.leftAt <= 150L) {
      long d = s.lastLand > 0L ? now - s.lastLand : 99999L;
      if (s.chain && d <= after) bound(s, pr, buf, r, p, now, d + " ms after landing");
    } else {
      s.airPress = now;
      boolean fresh = cv != null && cv[1] > 0.5 * jumpForce(buf, r) && s.wasFalling;
      if (s.chain && fresh) { s.landFell = s.fallMax; s.boundDone = false; bound(s, pr, buf, r, p, now, "landing hidden"); }
    }
  }
  if (s.chain && s.move == 0 && s.lastLand > 0L && ground && !s.boundDone && now - s.lastLand > after) {
    s.chain = false;
    dbg(s.u, pr, "Bounds ended: no jump within " + f1((double) after / 1000.0) + " s of the landing (" + s.bounds + " bounds).");
  }
  if (s.airUntil > now && !s.airUsed && !ground && !leave && now - s.leftAt > 150L && cEdge && @PKG@.ArmoryCfg.MK_AIRJUMP) {
    s.airUsed = true;
    double vy = jumpForce(buf, r);
    @PKG@.Leap.vel(buf, r, cv == null ? 0.0 : cv[0], vy, cv == null ? 0.0 : cv[2], false);
    armFlow(s, now);
    AIRJUMPS = AIRJUMPS + 1L;
    dbg(s.u, pr, "Free air jump (crouch): up at " + f1(vy) + " b/s.");
  }
}""")
# ---- (3) RISING STRIKE (probe M7 / M8 / M10): the leap, the cone hit + knock-up, the hang, the plunge, the slam
M(monk, r"""
public static boolean rise(@PKG@.MonkState s, @PR@ pr, @CB@ buf, @REF@ r, java.util.UUID u, String item, double[] d, long now) {
  double jab = fistHit(item);
  if (!(jab > 0.0)) { LAST_WHY = "rise: no fist weapon in hand"; dbg(u, pr, "Rising Strike: no fist weapon in your hand (" + item + ") - nothing done."); return false; }
  if (!ready(s, pr, buf, r, u, item, "Rising Strike", now)) return false;
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, r);
  if (p == null) return false;
  if (!pay(s, pr, buf, r, @PKG@.ArmoryCfg.MK_RST, @PKG@.ArmoryCfg.MK_RMA, "Rising Strike")) return false;
  double[] h = aimH(buf, r, u, d == null ? 0.0 : d[0], d == null ? 1.0 : d[2]);
  reset(s, item, jab, h[0], h[1], p, now);
  double g = grav();
  double vy = vyFor(@PKG@.ArmoryCfg.MK_RH, g);
  double f = @PKG@.ArmoryCfg.MK_RFWD;
  @PKG@.Leap.vel(buf, r, s.hx * f, vy, s.hz * f, false);
  s.move = 3;
  s.rsT = now;
  s.rsRose = false;
  s.noFallUntil = 0L;
  s.mobMinY = 1.0E9;
  s.mobMaxY = -1.0E9;
  flight(s, 4, p, 0.0, @PKG@.ArmoryCfg.MK_RH, now, f1(s.paidS) + " Stamina + " + f1(s.paidM) + " Mana");
  RISES = RISES + 1L;
  double ku = vyFor(@PKG@.ArmoryCfg.MK_RUP, g);
  double len = @PKG@.ArmoryCfg.MK_RLEN;
  boolean pvp = @PKG@.ArmoryTrav.pvp(@PKG@.ArmoryTrav.worldOf(buf));
  java.util.List l = @PKG@.ArmoryTrav.near(buf, p.x + s.hx * len * 0.5, p.y + 1.0, p.z + s.hz * len * 0.5, len + 4.0);
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    int k = foe(buf, t, r, u, pvp);
    if (k < 0) continue;
    @VEC@ tp = @PKG@.ArmoryTrav.posOf(buf, t);
    if (tp == null || Math.abs(tp.y - p.y) > 2.5) continue;
    double[] b = body(buf, t);
    if (!inCone(tp.x - p.x, tp.z - p.z, s.hx, s.hz, len + b[0] * 0.5, @PKG@.ArmoryCfg.MK_RWID * 0.5 + b[0] * 0.5)) continue;
    if (hit(buf, t, r, jab * @PKG@.ArmoryCfg.MK_RDMG)) n++;
    if (k == 0 && ku > 0.0 && liftable(buf, t) && @PKG@.Leap.vel(buf, t, 0.0, ku, 0.0, true)) s.ups.add(t);
  }
  s.upsHit = n;
  LAST_WHY = "rise";
  dbg(u, pr, "Rising Strike: paid " + f1(s.paidS) + " Stamina + " + f1(s.paidM) + " Mana (" + stat(buf, r) + "); " + n + " enemies hit for "
      + f1(jab * @PKG@.ArmoryCfg.MK_RDMG) + ", " + s.ups.size() + " knocked up at " + f1(ku) + " b/s. Crouch near the top = Plunge Punch.");
  return true;
}""")
M(monk, r"""
public static void holdMobs(@PKG@.MonkState s, @CB@ buf, double vy) {
  for (int i = s.ups.size() - 1; i >= 0; i--) {
    @REF@ t = (@REF@) s.ups.get(i);
    if (t == null || !t.isValid() || @PKG@.ArmoryTrav.dead(buf, t)) { s.ups.remove(i); continue; }
    @PKG@.Leap.vel(buf, t, 0.0, vy, 0.0, true);
    @VEC@ tp = @PKG@.ArmoryTrav.posOf(buf, t);
    if (tp != null) {
      if (tp.y < s.mobMinY) s.mobMinY = tp.y;
      if (tp.y > s.mobMaxY) s.mobMaxY = tp.y;
    }
  }
}""")
M(monk, r"""
public static void plunge(@PKG@.MonkState s, @PR@ pr, @VEC@ p, long now, String why) {
  s.move = 5;
  s.plungeT0 = now;
  s.plungeY0 = p.y;
  s.minVy = 0.0;
  s.noFallUntil = now + 6500L;
  s.flow = false;
  dbg(s.u, pr, "Plunge Punch (" + why + ") at " + f1(@PKG@.ArmoryCfg.MK_PSPD) + " b/s with " + s.ups.size() + " enemies.");
}""")
M(monk, r"""
public static void riseTick(@PKG@.MonkState s, @PR@ pr, @CB@ buf, @REF@ r, java.util.UUID u, @VEC@ p, double[] cv, boolean ground, boolean cEdge, long now) {
  if (s.move == 3) {
    if (cv != null && cv[1] > 1.0) s.rsRose = true;
    boolean nearTop = s.rsRose && cv != null && cv[1] <= 3.0;
    if (cEdge && nearTop) { plunge(s, pr, p, now, "crouch near the top"); return; }
    if ((s.rsRose && cv != null && cv[1] <= 0.5) || now - s.rsT > 1500L) {
      s.move = 4;
      s.rsApex = now;
      double dx = p.x - s.x0;
      double dz = p.z - s.z0;
      if (refund(s, buf, r, p, pr, "Rising Strike")) { s.move = 0; s.ups.clear(); s.fk = 0; return; }
      dbg(u, pr, "Rising Strike top: rose " + f1(s.fTop - s.y0) + pct(s.fTop - s.y0, @PKG@.ArmoryCfg.MK_RH) + ", drifted " + f1(Math.sqrt(dx * dx + dz * dz))
          + " forward in " + (now - s.rsT) + " ms; HANG " + Math.round(@PKG@.ArmoryCfg.MK_RHANG * 1000.0) + " ms with " + s.ups.size() + " enemies.");
    }
    return;
  }
  if (s.move == 4) {
    if (cEdge) { plunge(s, pr, p, now, "crouch " + (now - s.rsApex) + " ms into the hang"); return; }
    if (now - s.rsApex < Math.round(@PKG@.ArmoryCfg.MK_RHANG * 1000.0)) {
      @PKG@.Leap.vel(buf, r, cv == null ? 0.0 : cv[0] * 0.5, -1.0, cv == null ? 0.0 : cv[2] * 0.5, false);
      holdMobs(s, buf, -1.0);
      return;
    }
    s.move = 6;
    armFlow(s, now);
    s.flowTop = now;
    s.ups.clear();
    dbg(u, pr, "Hang over (" + (now - s.rsApex) + " ms; enemies held between y " + f1(s.mobMinY) + " and " + f1(s.mobMaxY) + ", " + s.flings
        + " flung). No plunge: flowing fall, steer with your keys.");
    return;
  }
  if (s.move == 5) {
    if (cv != null && cv[1] < s.minVy) s.minVy = cv[1];
    if (!ground) {
      @PKG@.Leap.vel(buf, r, 0.0, 0.0 - @PKG@.ArmoryCfg.MK_PSPD, 0.0, false);
      holdMobs(s, buf, 0.0 - @PKG@.ArmoryCfg.MK_PSPD);
      if (now - s.plungeT0 > 6000L) { s.move = 0; s.fk = 0; s.ups.clear(); s.noFallUntil = 0L; dbg(u, pr, "Plunge: no landing within 6 s - stopped."); }
      return;
    }
    s.move = 0;
    s.fk = 0;
    s.noFallUntil = now + 500L;
    PLUNGES = PLUNGES + 1L;
    double rad = @PKG@.ArmoryCfg.MK_PRAD;
    boolean pvp = @PKG@.ArmoryTrav.pvp(@PKG@.ArmoryTrav.worldOf(buf));
    java.util.List l = @PKG@.ArmoryTrav.near(buf, p.x, p.y + 0.5, p.z, rad + 4.0);
    int n = 0;
    for (int i = 0; i < l.size(); i++) {
      Object o = l.get(i);
      if (!(o instanceof @REF@)) continue;
      @REF@ t = (@REF@) o;
      if (foe(buf, t, r, u, pvp) < 0) continue;
      @VEC@ tp = @PKG@.ArmoryTrav.posOf(buf, t);
      if (tp == null || Math.abs(tp.y - p.y) > 2.5) continue;
      double[] b = body(buf, t);
      double hx = tp.x - p.x;
      double hz = tp.z - p.z;
      if (Math.sqrt(hx * hx + hz * hz) > rad + b[0] * 0.5) continue;
      if (hit(buf, t, r, s.hit * @PKG@.ArmoryCfg.MK_PDMG)) n++;
    }
    int dragged = 0;
    for (int i = 0; i < s.ups.size(); i++) {
      @VEC@ tp = @PKG@.ArmoryTrav.posOf(buf, (@REF@) s.ups.get(i));
      if (tp != null && tp.y - p.y < 2.0) dragged++;
    }
    long ms = now - s.plungeT0;
    dbg(u, pr, "Plunge landed: fell " + f1(s.plungeY0 - p.y) + " blocks in " + ms + " ms (" + f1(ms > 0L ? (s.plungeY0 - p.y) * 1000.0 / (double) ms : 0.0)
        + " b/s average, fastest " + f1(0.0 - s.minVy) + ", setting " + f1(@PKG@.ArmoryCfg.MK_PSPD) + "); slam hit " + n + " for " + f1(s.hit * @PKG@.ArmoryCfg.MK_PDMG)
        + " within " + f1(rad) + "; " + dragged + "/" + s.ups.size() + " lifted enemies came down with you; no fall damage.");
    s.ups.clear();
    return;
  }
  if (s.move == 6 && ground) {
    s.move = 0;
    s.fk = 0;
    dbg(u, pr, "Rising Strike landed after the flowing fall: " + (now - s.rsT) + " ms in the air.");
  }
}""")
# ---- a flight's measured numbers at its landing (debug), the vault's end + the refund of a vault that did not move you
M(monk, r"""
public static void report(@PKG@.MonkState s, @PR@ pr, @CB@ buf, @REF@ r, @VEC@ p, long now, boolean landed) {
  double dx = p.x - s.fx0;
  double dz = p.z - s.fz0;
  double d = Math.sqrt(dx * dx + dz * dz);
  double h = s.fTop - s.fy0;
  long air = now - s.fT0;
  int k = s.fk;
  s.fk = 0;
  if (k == 1) {
    s.move = 0;
    if (!s.fLeft) { s.chain = false; s.flow = false; }          // it never left the ground (a wall, a ceiling): no bounds, no flowing fall
    boolean back = refund(s, buf, r, p, pr, "The Pole-Vault");
    dbg(s.u, pr, "Pole-Vault" + (landed ? "" : " (NO landing in 6 s)") + ": lunge " + f1(s.lungeD) + pct(s.lungeD, @PKG@.ArmoryCfg.MK_LUNGE) + ", vault forward " + f1(d)
        + pct(d, s.fWantD) + ", height " + f1(h) + pct(h, s.fWantH) + ", air " + air + " ms, kicked " + s.kicks + " x " + f1(s.kickAmt)
        + (s.airUsed ? ", air jump used" : "") + ", cost " + (back ? "given back" : s.fCost) + ".");
    return;
  }
  if (k == 2) dbg(s.u, pr, "Bound " + s.bounds + " landed: forward " + f1(d) + pct(d, s.fWantD) + ", height " + f1(h) + pct(h, s.fWantH) + ", air " + air + " ms, cost " + s.fCost + ".");
}""")
# ---- fix round: a player who left mid-move never ticks again - every 5 s any tick drops records idle for 30 s (+ their flag)
M(monk, r"""
public static int sweepStale(long now) {
  int n = 0;
  java.util.Iterator it = STATES.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    @PKG@.MonkState s = (@PKG@.MonkState) STATES.get(k);
    if (s != null && now - s.last <= 30000L) continue;
    if (s != null && !STATES.remove(k, s)) continue;
    try { @PKG@.ArmoryDefs.bridge().remove(KEY + String.valueOf(k)); } catch (Throwable t) { }
    FLAGGED.remove(k);
    n++;
  }
  STALE = STALE + (long) n;
  return n;
}""")
# ---- the per-player tick (TravTick -> Monk.tickPlayer, world thread, every tick)
M(monk, r"""
public static void tickPlayer(@REF@ r, @ST@ st, @CB@ buf) {
  if (r == null || STATES.isEmpty()) return;
  long now0 = now();
  if (now0 - SWEPT > 5000L) { SWEPT = now0; sweepStale(now0); }
  java.util.UUID u = @PKG@.Leap.uuidOf(buf, r);
  if (u == null) return;
  @PKG@.MonkState s = (@PKG@.MonkState) STATES.get(u);
  if (s == null) return;
  if (s.st != st) { STATES.remove(u, s); return; }          // another world: the move is over
  if (s.ref == null || !s.ref.equals(r)) { if (s.ref == null || !s.ref.isValid()) { STATES.remove(u, s); return; } s.ref = r; }
  if (@PKG@.ArmoryTrav.dead(buf, r) || @PKG@.Leap.mounted(buf, r)) { STATES.remove(u, s); return; }
  long now = now();
  @MST@ ms = moves(buf, r);
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, r);
  if (ms == null || p == null) return;
  @PR@ pr = @PKG@.Kunai.prOf(buf, r);
  if ((ms.flying || ms.inFluid || ms.swimming) && (s.move != 0 || s.chain || s.flow)) {
    s.move = 0; s.chain = false; s.flow = false; s.fk = 0; s.ups.clear();
    s.noFallUntil = 0L;          // fix round: a cancelled plunge keeps no fall immunity
    dbg(u, pr, "Monk move ended (water or flying).");
  }
  double[] cv = cvel(buf, r);
  boolean g = ms.onGround;
  boolean land = g && !s.prevGround;
  boolean leave = !g && s.prevGround;
  boolean jEdge = ms.jumping && !s.prevJump;
  boolean cEdge = ms.crouching && !s.prevCrouch;
  s.prevGround = g;
  s.prevJump = ms.jumping;
  s.prevCrouch = ms.crouching;
  if (leave) { s.leftAt = now; s.airTopY = p.y; s.fallMax = 0.0; }
  if (!g) {
    if (p.y > s.airTopY) s.airTopY = p.y;
    double fd = fallDist(buf, r);
    if (fd > s.fallMax) s.fallMax = fd;
    if (s.airTopY - p.y > s.fallMax) s.fallMax = s.airTopY - p.y;
    if (s.fk != 0) s.fLeft = true;
  }
  if (s.fk != 0 && p.y > s.fTop) s.fTop = p.y;
  if (s.move == 1) lungeTick(s, pr, buf, r, p, cv, now);
  if (s.move == 1 || s.move == 2) sweep(s, pr, buf, r, u, p);
  if (s.move >= 3) riseTick(s, pr, buf, r, u, p, cv, g, cEdge, now);
  if (s.move == 0 || s.move == 2 || s.move == 6) flowTick(s, buf, r, cv, g, now);
  if ((s.fk == 1 || s.fk == 2) && ((g && s.fLeft) || now - s.fT0 > 6000L || (s.fk == 1 && !s.fLeft && now - s.fT0 > 1200L))) report(s, pr, buf, r, p, now, g);
  edges(s, pr, buf, r, p, cv, g, land, leave, jEdge, cEdge, now);
  heldFall(s, pr, buf, r, now);
  if (s.flung != null && now - s.flAt > 1500L) {
    @VEC@ fp = @PKG@.ArmoryTrav.posOf(buf, s.flung);
    if (fp != null) dbg(u, pr, "The flung enemy flew " + f1(Math.sqrt((fp.x - s.flX) * (fp.x - s.flX) + (fp.z - s.flZ) * (fp.z - s.flZ))) + " blocks (setting " + f1(@PKG@.ArmoryCfg.MK_RFLING) + ").");
    s.flung = null;
  }
  if (g && s.flow && s.move == 0 && !s.chain && s.lastLand > 0L && now - s.lastLand > 300L) s.flow = false;
  if (g && s.flow && s.move == 0 && !s.chain && s.lastLand <= 0L) s.flow = false;
  boolean active = s.move != 0 || s.chain || s.flow || s.pendFallAt > 0L || s.fk != 0;
  if (active) { s.last = now; flag(u, now + FLAG_MS); }
  else if (now - s.last > 1500L) STATES.remove(u, s);
}""")
# ---- the markers' SPAWN (ArmoryTrav.added, code 12000 / 12001): the marker goes at once, the move starts now (the bow leap way)
M(monk, r"""
public static void marker(@REF@ mk, @LPC@ pc, int c, @ST@ st, @CB@ buf) {
  try { buf.removeEntity(mk, @REMR@.REMOVE); } catch (Throwable t0) { }
  java.util.UUID u = pc.getCreatorUuid();
  @REF@ r = @PKG@.Leap.refOf(buf, u);
  if (u == null || r == null) return;
  MARKS = MARKS + 1L;
  String item = @PKG@.Leap.hand(buf, r, u);
  double[] d = @PKG@.ArmoryTrav.unit(@PKG@.ArmorySpawn.launchVelocity(pc.getSimplePhysicsProvider()));
  if (d == null) d = @PKG@.ArmoryTrav.look(buf, u);
  @PR@ pr = @PKG@.Kunai.prOf(buf, r);
  long now = now();
  @PKG@.MonkState s = state(u, r, st);
  if (s.move != 0) { LAST_WHY = "a move is running"; dbg(u, pr, "A Monk move is already running - this hold did nothing."); return; }
  boolean ok = c == @PKG@.ArmoryDefs.MK_VAULT_CODE ? vault(s, pr, buf, r, u, item, d, now) : rise(s, pr, buf, r, u, item, d, now);
  if (ok) { s.last = now; flag(u, now + FLAG_MS); }
}""")
# ---- GrappleFallSys (Filter group): the plunge takes none, a chain's landing is HELD (the bound forgives it), a flowing fall -15 %
M(monk, r"""
public static void onFall(@DMG@ d, @PR@ pr, @CB@ buf) {
  if (STATES.isEmpty() || d == null || pr == null || d.isCancelled()) return;
  if (@PKG@.ArmoryTrav.MINE.containsKey(d)) return;          // our own re-dealt held fall
  @PKG@.MonkState s = (@PKG@.MonkState) STATES.get(pr.getUuid());
  if (s == null) return;
  long now = now();
  float a = d.getAmount();
  if (now < s.noFallUntil) { d.setCancelled(true); CUT = CUT + 1L; dbg(s.u, pr, "Plunge landing: fall damage " + f1((double) a) + " cancelled."); return; }
  if (!@PKG@.ArmoryCfg.MK_ON) return;
  if (s.chain) { d.setCancelled(true); s.pendFall = (double) a; s.pendFallAt = now; HELD = HELD + 1L; return; }
  if (s.flow || s.move == 6 || s.move == 2) {
    float b = (float) ((double) a * (1.0 - (double) @PKG@.ArmoryCfg.MK_FLOWDMG / 100.0));
    d.setAmount(b);
    dbg(s.u, pr, "Flowing fall: fall damage " + f1((double) a) + " -> " + f1((double) b) + ".");
  }
}""")
# ---- ArmoryHitSys (Inspect group, the hit really landed): your hit on an enemy you lifted, while you rise or hang, flings it
M(monk, r"""
public static void onHit(@CB@ buf, @REF@ target, @DMG@ d) {
  try {
    if (STATES.isEmpty() || d == null || target == null || d.isCancelled() || !(d.getAmount() > 0.0f)) return;
    if (@PKG@.ArmoryTrav.MINE.containsKey(d)) return;
    Object src = d.getSource();
    if (!(src instanceof @DENT@)) return;
    @REF@ a = ((@DENT@) src).getRef();
    @PR@ pr = @PKG@.Kunai.prOf(buf, a);
    if (pr == null) return;
    @PKG@.MonkState s = (@PKG@.MonkState) STATES.get(pr.getUuid());
    if (s == null || (s.move != 3 && s.move != 4) || !s.ups.contains(target)) return;
    double[] h = aimH(buf, a, s.u, s.hx, s.hz);
    double v = @PKG@.ArmoryCfg.MK_RFLING * FLING_PER;
    if (!(v > 0.0) || !@PKG@.Leap.vel(buf, target, h[0] * v, 2.0, h[1] * v, true)) return;
    s.ups.remove(target);
    s.flings = s.flings + 1;
    FLINGS = FLINGS + 1L;
    @VEC@ tp = @PKG@.ArmoryTrav.posOf(buf, target);
    if (tp != null) { s.flung = target; s.flX = tp.x; s.flZ = tp.z; s.flAt = now(); }
    dbg(s.u, pr, "Air hit: that enemy is flung at " + f1(v) + " b/s (setting " + f1(@PKG@.ArmoryCfg.MK_RFLING) + " blocks).");
  } catch (Throwable t) { warn("onhit", "the Rising Strike air hit failed (" + t + ")"); }
}""")
# ---- /armory debug monk on|off
M(monk, r"""
public static void say(@PR@ pr, String text) {
  try { if (pr != null) pr.sendMessage(@MSG@.raw(text)); } catch (Throwable t) { }
  java.util.List sink = SINK;
  if (sink != null) sink.add(text);
}""")
M(monk, r"""
public static void help(@PR@ pr) {
  boolean on = pr != null && DEBUG.containsKey(pr.getUuid());
  say(pr, "/armory debug monk on|off (admin) - while on, every Pole-Vault, bound and Rising Strike you make prints its measured numbers here "
      + "(forward, height, air time, kicks, hang, plunge speed, costs). Now: " + (on ? "ON" : "off") + ".");
}""")
M(monk, r"""
public static void debugCmd(@PR@ pr, String a, String b, String c) {
  if (pr == null) return;
  String x = a == null ? "" : a.trim().toLowerCase(java.util.Locale.ROOT);
  String y = b == null ? "" : b.trim().toLowerCase(java.util.Locale.ROOT);
  String z = c == null ? "" : c.trim().toLowerCase(java.util.Locale.ROOT);
  if (!x.equals("debug") || !y.equals("monk") || !(z.equals("on") || z.equals("off"))) { help(pr); return; }
  java.util.UUID u = pr.getUuid();
  if (z.equals("on")) DEBUG.put(u, Boolean.TRUE);
  else DEBUG.remove(u);
  @PKG@.ArmoryLog.info(pr.getUsername() + " turned the Monk move debug " + z);
  say(pr, z.equals("on") ? "Monk debug ON: hold a Bo staff or fist attack and release - each move prints its numbers here (and in the server log)."
                         : "Monk debug off.");
}""")
M(monk, r"""
public static void clear() {
  STATES.clear();
  unflagAll();
}""")
EXEC12 = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
F(mdbg, "public @RA@ aArg;")
F(mdbg, "public @RA@ bArg;")
F(mdbg, "public @RA@ cArg;")
C(mdbg, r"""
public ArmoryDbgCmd() {
  super("(admin) /armory debug monk on|off: every Monk move prints its measured numbers in your chat");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.aArg = withRequiredArg("what", "debug", @ATY@.STRING);
  this.bArg = withRequiredArg("which", "monk", @ATY@.STRING);
  this.cArg = withRequiredArg("state", "on or off", @ATY@.STRING);
}""")
M(mdbg, EXEC12 + r""" {
  String a = null, b = null, c = null;
  try { a = String.valueOf(ctx.get(this.aArg)); b = String.valueOf(ctx.get(this.bArg)); c = String.valueOf(ctx.get(this.cArg)); }
  catch (Throwable t) { @PKG@.Monk.help(pr); return; }
  @PKG@.Monk.debugCmd(pr, a, b, c);
}""")
C(mcmd, r"""
public ArmoryCmd() {
  super("armory", "(admin) SkyyArmory tools: /armory debug monk on|off");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addUsageVariant(new @PKG@.ArmoryDbgCmd());
}""")
M(mcmd, EXEC12 + r""" {
  @PKG@.Monk.help(pr);
}""")
'''
rep('''# ---- ArmoryTravSys.onEntityAdded (SPAWN of one of our projectiles): quick orbs -> range / pierce record; wand charged orb -> burst''',
    MONK_JAVA + '''# ---- ArmoryTravSys.onEntityAdded (SPAWN of one of our projectiles): quick orbs -> range / pierce record; wand charged orb -> burst''')
rep('''  if (c == @PKG@.ArmoryDefs.SS_CODE) { @PKG@.Shadow.marker(ref, pc, c, st, buf); return; }     // 0.1.8: the dagger Shadow Step
''', '''  if (c == @PKG@.ArmoryDefs.SS_CODE) { @PKG@.Shadow.marker(ref, pc, c, st, buf); return; }     // 0.1.8: the dagger Shadow Step
  if (c == @PKG@.ArmoryDefs.MK_VAULT_CODE || c == @PKG@.ArmoryDefs.MK_RISE_CODE) { @PKG@.Monk.marker(ref, pc, c, st, buf); return; }     // 0.1.12: the Monk holds
''')
rep('''      @PKG@.Levitate.SAVES = @PKG@.Levitate.SAVES + 1L;
    }
  } catch (Throwable t) { @PKG@.Grapple.warn("fall:"''', '''      @PKG@.Levitate.SAVES = @PKG@.Levitate.SAVES + 1L;
    } else @PKG@.Monk.onFall(d, (@PR@) po, buf);          // 0.1.12: the plunge / a held bound landing / the flowing fall
  } catch (Throwable t) { @PKG@.Grapple.warn("fall:"''')
rep('''    if (@PKG@.ArmoryTrav.mine(d)) return;          // our own burst / trail hit: never a burst of its own
''', '''    if (chunk != null) @PKG@.Monk.onHit(buf, chunk.getReferenceTo(idx), d);          // 0.1.12: a Rising Strike air hit flings (skips our own hits)
    if (@PKG@.ArmoryTrav.mine(d)) return;          // our own burst / trail hit: never a burst of its own
''')
rep('''    try { @PKG@.Kunai.tickPlayer(chunk.getReferenceTo(idx), store, cb); }         // 0.1.6: the kunai flight / landing / return knockback
    catch (Throwable tk) { @PKG@.Kunai.warn("tick:" + tk.getClass().getName(), "kunai tick failed (" + tk + ")"); }
''', '''    try { @PKG@.Kunai.tickPlayer(chunk.getReferenceTo(idx), store, cb); }         // 0.1.6: the kunai flight / landing / return knockback
    catch (Throwable tk) { @PKG@.Kunai.warn("tick:" + tk.getClass().getName(), "kunai tick failed (" + tk + ")"); }
    try { @PKG@.Monk.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.12: the Monk moves (vault, bounds, rise, plunge, flowing fall)
    catch (Throwable tm) { @PKG@.Monk.warn("tick:" + tm.getClass().getName(), "Monk move tick failed (" + tm + ")"); }
''')

# ---------------------------------------------------------------------------------------------------------------- the plugin
rep('''               "armory:grapple", "armory:leap", "armory:book", "armory:kunai", "armory:stun", "armory:shadow"]''',
    '''               "armory:grapple", "armory:leap", "armory:book", "armory:kunai", "armory:stun", "armory:shadow", "armory:monk"]''')
rep('''  b.put("armory:shadow", @PKG@.ArmoryCfg.SHADOW_TEXT);          // 0.1.8
''', '''  b.put("armory:shadow", @PKG@.ArmoryCfg.SHADOW_TEXT);          // 0.1.8
  b.put("armory:monk", @PKG@.ArmoryCfg.MONK_TEXT);          // 0.1.12
''')
rep('''  @PKG@.ArmoryTree.unpublish();          // 0.1.9
}""" % jarr(BRIDGE_KEYS))''', '''  @PKG@.ArmoryTree.unpublish();          // 0.1.9
  @PKG@.Monk.clear();          // 0.1.12: the armory:monkmove:<uuid> flags go too
}""" % jarr(BRIDGE_KEYS))''')
rep('''  @PKG@.Kunai.DGEN.clear();
  systems();
  publish();''', '''  @PKG@.Kunai.DGEN.clear();
  @PKG@.Monk.clear();          // 0.1.12
  @PKG@.Monk.DEBUG.clear();
  systems();
  publish();
  try { getCommandRegistry().registerCommand(new @PKG@.ArmoryCmd()); }          // 0.1.12: /armory debug monk on|off (admin)
  catch (Throwable tcm) { @PKG@.ArmoryLog.warn("/armory could not be registered: " + tcm + " - no Monk debug lines this start"); }''')
rep('''  @PKG@.ArmoryLog.info("@VERSION@ " + @PKG@.ArmoryCfg.SHADOW_TEXT);
''', '''  @PKG@.ArmoryLog.info("@VERSION@ " + @PKG@.ArmoryCfg.SHADOW_TEXT);
  @PKG@.ArmoryLog.info("@VERSION@ " + @PKG@.ArmoryCfg.MONK_TEXT + "; /armory debug monk on|off (admin)");
''')
rep('''  @PKG@.Kunai.DGEN.clear();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''', '''  @PKG@.Kunai.DGEN.clear();
  @PKG@.Monk.clear();          // 0.1.12
  @PKG@.Monk.DEBUG.clear();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''')
rep('''"Daggers: hold + release = Shadow Step (vanish, appear behind the enemy you aim at, backstab). "''',
    '''"Daggers: hold + release = Shadow Step (vanish, appear behind the enemy you aim at, backstab). "
                 "Monk moves: Bo staff hold = Pole-Vault (kicks) + skipping bounds; fist hold = Rising Strike + Plunge Punch (/armory debug monk on|off). "''')
rep('''    assert sorted(n for n in _names if n in set(BO_FILES)) == sorted(BO_FILES), "0.1.11: the 4 Bo files"
''', '''    assert sorted(n for n in _names if n in set(BO_FILES)) == sorted(BO_FILES), "0.1.11: the 4 Bo files"
    assert sorted(n for n in _names if n in set(MK12_FILES)) == MK12_FILES and len([n for n in _names if "/SkyyArmory_Monk_" in n]) == 17, "0.1.12: the 17 Monk move files"
''')
rep('''AZ.close()''', '''print("0.1.12 monk moves: %d rows (Server Setup > Armory > Monk moves + weapons) + 2 read-only rows; markers %s / %s (codes %d / %d); Bo hits %s; fist jabs %s; "
      "bridge armory:monk + armory:monkmove:<uuid>; command /armory (admin)" % (len(CFG_MK), MK_VAULT_MARK, MK_RISE_MARK, MK_VAULT_CODE, MK_RISE_CODE,
                                                                              ", ".join("%s %s" % (i_.split("_")[-1], bnum(h_)) for i_, h_ in MK_BO_TAB),
                                                                              ", ".join("%s %s" % ("_".join(i_.split("_")[2:]), bnum(h_)) for i_, h_ in MK_FIST_TAB)))
AZ.close()''')

with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(s.replace(LF, NL))
print("wrote %s" % os.path.relpath(DST, ROOT))

# ================================================================================================ harness
traw = open(TSRC, encoding="utf8", newline="").read()
TNL = CR + LF if (CR + LF) in traw else LF
ts = traw.replace(CR + LF, LF)


def hrep(old, new, count=1):
    global ts
    n = ts.count(old)
    assert n == count, "harness anchor count %d (want %d): %s" % (n, count, old[:140])
    ts = ts.replace(old, new)


hrep('"""SkyyArmory 0.1.11 - test harness. GENERATED by tools/armory_0_1_11_patch.py from test_skyyarmory_0.1.10.py - edit the patch, never this file.',
     '''"""SkyyArmory 0.1.12 - test harness. GENERATED by tools/armory_0_1_12_patch.py from test_skyyarmory_0.1.11.py - edit the patch, never this file.
Run: python SkyyArmory/test_skyyarmory_0.1.12.py --dir tools/dev/scratch/<task>/harness   (--no-set skips the one-JVM SET run, --keep keeps it)
Every 0.1.11 check still runs on the 0.1.11 shape: JZ is the jar AS THE OLDER CHECKS KNOW IT - the 17 new Monk files are hidden and the 14
changed files (the Bo root, the 12 fist roots, the SkyyArmory_Fist animation set) + the lang read as the 0.1.11 jar's bytes (P14 proves the real
files are exactly the planned change of those bytes); the classes are the real 0.1.12 ones (A / X / T / V / every Java path); R14e
(0.1.10 -> new) is history - R15e compares 0.1.11 -> 0.1.12 file by file AND method by method.
NEW P14 (Python) + R15 (JVM, after R14) EXECUTE every 0.1.12 path:
  P14  the 17 new files (every Parallel 2+ entries), the 14 changed files = the 0.1.11 bytes with only the planned change (the Bo root and
       the 12 fist roots name the new Charging steps; the Bo Charging step = the vanilla Staff_Primary with the 2 keys pointed at ours; the
       fist Charging = the vanilla dagger shape; the launches; the markers = the blink marker shape; the 50 third-person files = Default
       files that exist (NEGATIVE CONTROL: 0.1.11 had 50 entries without one); the lang = 19 descriptions + the hold sentence); a walk
       from every Bo / fist item's attack button reaches the swing / combo chain AND the marker launch, no Mana, no StatsCondition;
       SkyySkills 0.4.22 (when built) ships no vanilla Bo item.
  R15  a: THE ENGINE ASSET VALIDATORS on all 17 new + 14 changed assets (+ every inline step); b: into the stores, RootInteraction.build()
       of the Bo root + every fist root (Charging -> the chain + the launch, 0 missing); c: the Monk Java on the engine stand-ins - the pure
       maths (kickTest vs the probe's feet-point sphere = NEGATIVE CONTROL), the vault (marker -> costs, lunge Sets, vault Set, kicks once per
       enemy along the swept path incl. a mob the probe missed, flowing fall Sets, the free air jump by crouch, the landing report), the
       bounds (timed after / early press, held fall forgiven, missed = re-dealt 85 %, out of Stamina ends the chain), refunds, refusals
       (air, class lock, no Bo, Stamina), Rising Strike (cone hit, knock-up, boss never lifted, hang, air-hit fling, plunge 30 b/s + drag
       + slam + no fall damage, no-plunge flowing fall -15 %), the Acrobatics flag, the debug lines, the command (admin), the dispatch
       through ArmoryTravSys / TravTick / GrappleFallSys / ArmoryHitSys, world change; e: vs the 0.1.11 jar file by file + method by method.

0.1.11 harness: SkyyArmory 0.1.11 - test harness. GENERATED by tools/armory_0_1_11_patch.py from test_skyyarmory_0.1.10.py - edit the patch, never this file.''')
hrep('VERSION = "0.1.11"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.11 SkyyArmory"',
     'VERSION = "0.1.12"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.12 SkyyArmory"')
hrep('os.path.join(SCRATCH_ROOT, "armory0111", "harness")', 'os.path.join(SCRATCH_ROOT, "armory0112", "harness")')
hrep('raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.11.py', 'raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.12.py')
hrep('Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.11"))', 'Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.12"))')
hrep('"[SkyyArmory] 0.1.11 ready" in m_', '"[SkyyArmory] 0.1.12 ready" in m_')
hrep('"0.1.11 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_', '"0.1.12 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_')
hrep('"0.1.11 crossbow grapple: grapple on" in m_', '"0.1.12 crossbow grapple: grapple on" in m_')
hrep('"51 of 51 items, 341 of 341 interactions, 63 of 63 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.11 SkyyArmory" in str(r[1])',
     '"51 of 51 items, 356 of 356 interactions, 65 of 65 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.12 SkyyArmory" in str(r[1])')
hrep('''    check(len(names) == 47, "A: 47 classes (40 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap + 0.1.6's 6 book / kunai + 0.1.7's 2 stunlock + 0.1.8's Shadow + 0.1.9's ArmoryTree + 7 kit)")''',
     '''    check(len(names) == 51, "A: 51 classes (44 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap + 0.1.6's 6 book / kunai + 0.1.7's 2 stunlock + 0.1.8's Shadow + 0.1.9's ArmoryTree + 0.1.12's MonkState / Monk / ArmoryCmd / ArmoryDbgCmd + 7 kit)")''')

# ---- the jar as the older checks know it (0.1.11): new Monk files hidden, the 14 changed files + the lang read from the 0.1.11 jar
hrep('''JZ = zipfile.ZipFile(JAR)
JN = JZ.namelist()''', '''JZ = zipfile.ZipFile(JAR)
# 0.1.12: JREAL = the real jar (P14 / R15); JZ = the jar as the older checks know it - the 17 new Monk move files hidden, the 14 changed
# files (the Bo root, the 12 fist roots, the Fist animation set) and the lang read as the 0.1.11 jar's bytes (P14 checks the real ones are
# exactly the planned change of those bytes); classes, manifest and everything else = the real jar
JREAL = JZ
OLD111 = os.path.join(HERE, "SkyyArmory-0.1.11.jar")
if not os.path.isfile(OLD111):
    raise SystemExit("the 0.1.12 harness needs SkyyArmory-0.1.11.jar (the base, the SET pin) next to it: %s" % OLD111)
OZ111 = zipfile.ZipFile(OLD111)
MK12_NEW = sorted(n_ for n_ in JREAL.namelist() if "/SkyyArmory_Monk_" in n_)
MK12_FROOTS = sorted(n_ for n_ in JREAL.namelist() if n_.startswith("Server/Item/RootInteractions/Weapons/Fist/SkyyArmory/SkyyArmory_Fist_"))
MK12_BOROOT = "Server/Item/RootInteractions/Weapons/Bo/SkyyArmory/SkyyArmory_Bo_Primary.json"
MK12_ANIM = "Server/Item/Animations/SkyyArmory/SkyyArmory_Fist.json"
MK12_LANG = "Server/Languages/en-US/server.lang"
MK12_CHG = sorted([MK12_BOROOT, MK12_ANIM] + MK12_FROOTS)


class Z111(object):
    """the 0.1.12 jar as the 0.1.11 checks know it (read only)"""
    def __init__(self, real, old, hide, oldfiles):
        self.real, self.old, self.hide, self.oldfiles = real, old, set(hide), set(oldfiles)

    def namelist(self):
        return [n_ for n_ in self.real.namelist() if n_ not in self.hide]

    def read(self, n_):
        if n_ in self.hide:
            raise KeyError(n_)
        return self.old.read(n_) if n_ in self.oldfiles else self.real.read(n_)

    def close(self):
        self.real.close()
        self.old.close()


JZ = Z111(JREAL, OZ111, MK12_NEW, MK12_CHG + [MK12_LANG])
JN = JZ.namelist()''')

# ---- T: the plugin registers its command (a capturing CommandRegistry stand-in)
hrep('''    rp.writeFile(hcls)
''', '''    rp.writeFile(hcls)
    rc12 = CPj.makeClass("armoryharness.CaptureCmds", CPj.get("com.hypixel.hytale.server.core.command.system.CommandRegistry"))          # 0.1.12
    rc12.addField(JClass("javassist.CtField").make("public static java.util.List CAP = new java.util.ArrayList();", rc12))
    rc12.addConstructor(JClass("javassist.CtNewConstructor").make("public CaptureCmds() { super((java.util.List) null, (java.util.function.BooleanSupplier) null, "
                                                                   "(String) null, (com.hypixel.hytale.server.core.plugin.PluginBase) null); }", rc12))
    rc12.addMethod(CtNM.make("public com.hypixel.hytale.server.core.command.system.CommandRegistration registerCommand(com.hypixel.hytale.server.core.command.system.AbstractCommand c) "
                             "{ CAP.add(c); return null; }", rc12))
    rc12.writeFile(hcls)
''')
hrep('''        setf(p_, PBc, "entityStoreRegistry", U.allocateInstance(CPc.class_))
''', '''        setf(p_, PBc, "entityStoreRegistry", U.allocateInstance(CPc.class_))
        JClass("armoryharness.CaptureCmds").CAP.clear()          # 0.1.12: /armory
        setf(p_, PBc, "commandRegistry", U.allocateInstance(JClass("armoryharness.CaptureCmds").class_))
''')
hrep('''        caps.append([s_ for s_ in CPc.CAP])
''', '''        caps.append([s_ for s_ in CPc.CAP])
        cmds12.append([str(c_.getClass().getSimpleName()) for c_ in JClass("armoryharness.CaptureCmds").CAP])
''')
hrep('''    s0 = snap()
    caps = []
''', '''    s0 = snap()
    caps = []
    cmds12 = []
''')
hrep('''    print("T. real setup() twice on a copy of the live data''', '''    monk_line = [m_ for lv_, m_ in records()[n_log0:] if "0.1.12 monk moves on - Pole-Vault (Bo hold): lunge 3 in 0.2 s, 4.5 up x 7 forward (push x2.1)" in m_]
    check(cmds12 == [["ArmoryCmd"], ["ArmoryCmd"]] and len(monk_line) == 2 and "/armory debug monk on|off (admin)" in monk_line[0]
          and br.get("armory:monk") is None and not [k_ for k_ in br.keySet() if str(k_).startswith("armory:monkmove:")],
          "T (0.1.12): each setup() registers exactly ONE command (/armory) and prints the Monk moves line; after shutdown armory:monk and every "
          "armory:monkmove:<uuid> flag are gone: %s %s" % (cmds12, monk_line[:1]))
    print("T. real setup() twice on a copy of the live data''')

# ---- L: the 15 new interactions + 2 markers go into the stores before the pack check (it counts every id the jar ships)
hrep('''    CHK = JClass(PKG + "ArmoryCheck")
    r = CHK.packCheck()
''', '''    bad12 = []          # 0.1.12: the new Monk interactions + markers (the real files) into the stores - the pack check counts them
    for c_, pre_ in ((INTc, "Server/Item/Interactions/"), (PRJc, "Server/Projectiles/")):
        objs_ = []
        for n_ in MK12_NEW:
            if n_.startswith(pre_):
                o_, w_ = dec(c_, os.path.basename(n_)[:-5], JREAL.read(n_).decode("utf-8"))
                if o_ is None or w_:
                    bad12.append("%s: %s" % (n_, w_))
                else:
                    objs_.append(o_)
        load(c_, objs_, PACK)
    check(not bad12 and len(MK12_NEW) == 17, "L (0.1.12): the 15 Monk interactions + 2 markers decode (no unknown key) and go into the stores: %s" % bad12[:3])
    CHK = JClass(PKG + "ArmoryCheck")
    r = CHK.packCheck()
''')
# ---- R14e (0.1.10 -> new) is history: R15e compares 0.1.11 -> 0.1.12
hrep('''    OLD110 = os.path.join(HERE, "SkyyArmory-0.1.10.jar")
    if not os.path.isfile(OLD110):
        print("R14e. NOTE no SkyyArmory-0.1.10.jar here - the old-vs-new file compare is skipped")''',
     '''    OLD110 = None          # 0.1.12: the 0.1.10 -> new compare is history - R15e compares 0.1.11 -> 0.1.12
    if OLD110 is None:
        print("R14e. NOTE (0.1.12) the 0.1.10 -> new file compare is history - R15e compares 0.1.11 -> 0.1.12")''')

# ---- P14 (Python): every 0.1.12 file before the JVM part
P14 = r"""# ============================================================================================================ P14. 0.1.12 the Monk moves (pure files)
MKV, MKR = "SkyyArmory_Monk_Vault", "SkyyArmory_Monk_Rise"
MK_BOCH, MK_VL, MK_RL = "SkyyArmory_Monk_Bo_Charge", "SkyyArmory_Monk_Vault_Launch", "SkyyArmory_Monk_Rise_Launch"
JR = dict((n_, json.loads(JREAL.read(n_).decode("utf-8"))) for n_ in MK12_NEW + MK12_CHG)
JO = dict((n_, json.loads(OZ111.read(n_).decode("utf-8"))) for n_ in MK12_CHG)
mkid = lambda n_: os.path.basename(n_)[:-5]
NEWINT = dict((mkid(n_), JR[n_]) for n_ in MK12_NEW if n_.startswith("Server/Item/Interactions/"))
NEWPRJ = dict((mkid(n_), JR[n_]) for n_ in MK12_NEW if n_.startswith("Server/Projectiles/"))
FKEYS = [mkid(n_)[len("SkyyArmory_Fist_"):-len("_Primary")] for n_ in MK12_FROOTS]
check(len(MK12_NEW) == 17 and len(NEWINT) == 15 and sorted(NEWPRJ) == [MKR, MKV] and len(MK12_FROOTS) == 12
      and sorted(NEWINT) == sorted([MK_BOCH, MK_VL, MK_RL] + ["SkyyArmory_Monk_Fist_%s_Charge" % k_ for k_ in FKEYS])
      and all(n_.startswith("Server/Item/Interactions/Weapons/Monk/SkyyArmory/") for n_ in MK12_NEW if n_.startswith("Server/Item/Interactions/"))
      and not [i_ for i_ in list(NEWINT) + list(NEWPRJ) if ahas("int", i_) or ahas("prj", i_) or ahas("root", i_)],
      "P14: 17 new files = the Bo Charging step, the 2 launches, 12 fist Charging steps (Weapons/Monk/SkyyArmory/), 2 markers; no id in Assets.zip: %s" % MK12_NEW[:4])
_p14bad = []
for n_ in MK12_NEW + MK12_CHG:
    _p13walk(JR[n_], n_)
check(not [x_ for x_ in _p13bad if x_ in JR], "P14: every Parallel in the 31 new / changed files has 2+ entries: %s" % [x_ for x_ in _p13bad if x_ in JR][:3])
# the Bo: root -> Charging (the vanilla Staff_Primary now, its 2 keys pointed at ours) -> "0" the 0.1.11 swing chain, "1" the vault launch
_vsp14 = aj("int", "Staff_Primary")
_bch14 = copy.deepcopy(_vsp14)
_bch14["Next"] = {"0": "SkyyArmory_Bo_Swings", "1": MK_VL}
_ss14 = L18_J[L18_INTS[SS_LAUNCH]]
check(JO[MK12_BOROOT] == {"Interactions": ["SkyyArmory_Bo_Swings"]} and JR[MK12_BOROOT] == {"Interactions": [MK_BOCH]}
      and NEWINT[MK_BOCH] == _bch14 and sorted(_vsp14["Next"]) == ["0", "1"] and _vsp14["Next"]["1"] == "Staff_Cast_Summon_Charged"
      and NEWINT[MK_VL] == {"Type": "LaunchProjectile", "RunTime": _ss14["RunTime"], "Effects": {"ItemAnimationId": "CastSummon"}, "ProjectileId": MKV}
      and "SkyyArmory_Bo_Swings" in L111_INTS,
      "P14 (1): the Bo root (0.1.11: the swing chain) names SkyyArmory_Monk_Bo_Charge = the vanilla Staff_Primary Charging (Assets.zip now: hold 1, "
      "the CastSummonCharging pose, slow walk) with tap '0' = SkyyArmory_Bo_Swings and hold '1' = the vault launch (the Shadow Step launch's "
      "RunTime, the CastSummon pose, marker %s): %s" % (MKV, NEWINT[MK_BOCH]))
_vdg14 = aj("int", "Weapon_Daggers_Primary")
fb14 = []
for n_ in MK12_FROOTS:
    k_ = mkid(n_)[len("SkyyArmory_Fist_"):-len("_Primary")]
    o_, r_ = JO[n_], JR[n_]
    ch_ = NEWINT.get("SkyyArmory_Monk_Fist_%s_Charge" % k_)
    want_ = dict(o_, Interactions=["SkyyArmory_Monk_Fist_%s_Charge" % k_])
    if r_ != want_ or list(r_) != list(o_) or o_["Interactions"] != ["SkyyArmory_Fist_%s_Chain" % k_] or ch_ != {"Type": "Charging", "DisplayProgress": False, "AllowIndefiniteHold": True,
            "Next": {"0": "SkyyArmory_Fist_%s_Chain" % k_, "0.6": MK_RL}} or ("SkyyArmory_Fist_%s_Chain" % k_) not in L17_INTS:
        fb14.append(k_)
check(not fb14 and sorted(_vdg14) == ["DisplayProgress", "Next", "Type"] and _vdg14["DisplayProgress"] is False
      and NEWINT[MK_RL] == {"Type": "LaunchProjectile", "RunTime": _ss14["RunTime"], "Effects": {"ItemAnimationId": "PowerUp"}, "ProjectileId": MKR},
      "P14 (3): each of the 12 fist roots = its 0.1.11 file (RequireNewClick, queue, cooldown, tags kept) naming SkyyArmory_Monk_Fist_<key>_Charge = "
      "the vanilla dagger Charging shape (no progress bar) + AllowIndefiniteHold (fires on release, no overshoot WARN): tap '0' = the 0.1.7 combo chain, hold 0.6 = the rise launch (PowerUp pose, marker %s): %s" % (MKR, fb14))
_bm14 = J[J_PRJ["SkyyArmory_Blink_Iron"]]
check(NEWPRJ[MKV] == _bm14 and NEWPRJ[MKR] == _bm14, "P14: both markers = the staff blink marker shape (invisible, no damage, removed at its spawn)")
# the client log fix: the Fist animation set
_fa_o, _fa_n = JO[MK12_ANIM]["Animations"], JR[MK12_ANIM]["Animations"]
_vdef = aj("anim", "Default")["Animations"]
tp14 = dict((k_, e_["ThirdPerson"]) for k_, e_ in _fa_n.items() if "ThirdPerson" not in _fa_o[k_])
tpb14 = [k_ for k_ in tp14 if ("Common/" + tp14[k_]) not in AZS or not tp14[k_].startswith("Characters/Animations/")
         or (("FirstPerson" in _fa_o[k_]) and tp14[k_] != _fa_o[k_]["FirstPerson"].replace("_FPS.blockyanim", ".blockyanim"))]
check(sorted(_fa_n) == sorted(_fa_o) and len(tp14) == 50 and not tpb14 and not [k_ for k_, e_ in _fa_n.items() if "ThirdPerson" not in e_]
      and all(dict((x_, y_) for x_, y_ in _fa_n[k_].items() if x_ != "ThirdPerson") == _fa_o[k_] for k_ in tp14)
      and all(_fa_n[k_] == _fa_o[k_] for k_ in _fa_n if k_ not in tp14)
      and dict((x_, y_) for x_, y_ in JR[MK12_ANIM].items() if x_ != "Animations") == dict((x_, y_) for x_, y_ in JO[MK12_ANIM].items() if x_ != "Animations")
      and len([k_ for k_, e_ in _vdef.items() if "ThirdPerson" not in e_]) == 50
      and tp14.get("Walk") == "Characters/Animations/Default/Walk.blockyanim" and tp14.get("JumpRun") == "Characters/Animations/Default/Jump_Far.blockyanim",
      "P14 (7): the SkyyArmory_Fist set - the 50 entries without a ThirdPerson (NEGATIVE CONTROL: the vanilla Default set + 0.1.11 had 50) get the "
      "vanilla Default (unarmed) third-person file of the same movement (the FPS file without _FPS; Step / Jump / Fall = the Sword mapping), "
      "every file in Assets.zip, nothing else changed: %s" % tpb14[:4])
lo14 = OZ111.read(MK12_LANG).decode("utf-8").split("\n")
ln14 = JREAL.read(MK12_LANG).decode("utf-8").split("\n")
lch14 = [k_ for k_ in range(max(len(lo14), len(ln14))) if k_ >= len(lo14) or k_ >= len(ln14) or lo14[k_] != ln14[k_]]
lbad14 = [k_ for k_ in lch14 if k_ >= len(lo14) or k_ >= len(ln14) or not lo14[k_].endswith(" Right click: block.")
          or ln14[k_] not in (lo14[k_][:-len(" Right click: block.")] + " Hold + release: Pole-Vault (kicks, bounds). Right click: block.",
                              lo14[k_][:-len(" Right click: block.")] + " Hold + release: Rising Strike (crouch at the top: Plunge Punch). Right click: block.")]
check(len(ln14) == len(lo14) and len(lch14) == 19 and not lbad14,
      "P14: the lang = 0.1.11's with only the 19 Bo / fist descriptions telling the hold: %s" % [ln14[k_] for k_ in lbad14][:2])


def p14_reach(item):
    # every step the attack button can reach (item vars applied): the real 0.1.12 files first, then Assets.zip
    vars_ = item.get("InteractionVars") or {}
    seen_, todo_, types_, txt_ = set(), [("root", item["Interactions"]["Primary"])], set(), []
    allint = dict(NEWINT)
    allint.update(dict((k_, L17_J[p_]) for k_, p_ in L17_INTS.items()))
    allint.update(dict((k_, L111_J[p_]) for k_, p_ in L111_INTS.items()))
    roots = dict((mkid(n_), JR[n_]) for n_ in MK12_FROOTS + [MK12_BOROOT])
    while todo_:
        k_, x_ = todo_.pop()
        if (k_, x_) in seen_:
            continue
        seen_.add((k_, x_))
        d_ = vars_.get(x_) if x_ in vars_ else (roots.get(x_) if k_ == "root" else None)
        if d_ is None:
            d_ = allint.get(x_)
        if d_ is None and ahas("int", x_):
            d_ = aj("int", x_)
        if d_ is None and ahas("root", x_):
            d_ = aj("root", x_)
        if d_ is None:
            types_.add("MISSING " + x_)
            continue
        txt_.append(json.dumps(d_))

        def scan(o_, ref_):
            if isinstance(o_, str):
                if ref_:
                    todo_.append(("int", o_))
            elif isinstance(o_, list):
                for v_ in o_:
                    scan(v_, ref_)
            elif isinstance(o_, dict):
                if "Type" in o_:
                    types_.add(o_["Type"])
                nmap_ = ref_ and "Type" not in o_ and o_ and all(re.match(r"^[0-9.]+$", str(q_)) for q_ in o_)
                for q_, v_ in o_.items():
                    if q_ == "Var":
                        if isinstance(v_, str) and v_ in vars_:
                            todo_.append(("int", v_))
                        continue
                    scan(v_, nmap_ or q_ in ("Next", "Failed", "Interactions", "Parent"))
        scan(d_, isinstance(d_, str))
    return types_, "".join(txt_)


rb14 = []
for i_ in sorted(L111_REAL) + VBO111:
    it_ = L111_REAL[i_] if i_ in L111_REAL else L111_J[L111_ITEMS[i_]]
    ty_, tx_ = p14_reach(it_)
    if [t_ for t_ in ty_ if t_.startswith("MISSING") or t_ in ("StatsCondition",)] or '"Mana"' in tx_ or "Charging" not in ty_ or "Chaining" not in ty_ \
            or ('"ProjectileId": "%s"' % MKV) not in tx_ or "Spear_Swing_Left" not in tx_:
        rb14.append((i_, sorted(ty_)))
for i_ in sorted(L17_ITEMS):
    if not i_.startswith("Weapon_Fist_"):
        continue
    ty_, tx_ = p14_reach(L17_J[L17_ITEMS[i_]])
    if [t_ for t_ in ty_ if t_.startswith("MISSING") or t_ == "StatsCondition"] or '"Mana"' in tx_ or "Charging" not in ty_ or "Chaining" not in ty_ \\
            or ('"ProjectileId": "%s"' % MKR) not in tx_ or "Raycast" not in tx_:
        rb14.append((i_, sorted(ty_)))
check(not rb14, "P14: from the attack button of all 9 Bo staffs and all 12 fist weapons (item vars applied, our real files + Assets.zip) the walk "
                "reaches the Charging step, the tap chain (Bo: the Spear swings; fists: the Raycast combo) AND the move's marker launch - no "
                "missing id, no StatsCondition, no Mana: %s" % rb14[:2])
SK22 = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.22.jar")
if os.path.isfile(SK22):
    with zipfile.ZipFile(SK22) as z_:
        sk22bo = [n_ for n_ in z_.namelist() if n_.startswith("Server/Item/Items/") and os.path.basename(n_)[:-5] in VBO111]
    check(not sk22bo, "P14 (SkyySkills 0.4.22 handover): the built SkyySkills 0.4.22 ships no vanilla Bo item - ours (charged = Pole-Vault) are live: %s" % sk22bo)
    print("P14. SkyySkills 0.4.22 ships no vanilla Bo item: our Weapon_Staff_Bo_Wood / _Bamboo (Pole-Vault) are the live ones once it is pinned")
else:
    print("P14. NOTE SkyySkills-0.4.22.jar not built here - the Bo handover check is skipped")
print("P14. 0.1.12: 17 new files, 14 changed (the planned change of the 0.1.11 bytes), 50 third-person files, 19 descriptions, every Bo / fist "
      "button reaches its chain + the move marker")
"""
hrep('''PY_OKS, PY_FAILS = OKS[0], len(FAILS)
''', P14.replace("\\\\\n", "\\\n") + '''PY_OKS, PY_FAILS = OKS[0], len(FAILS)
''')

# ---- the older checks' counts that 0.1.12 grows (the Monk tick in TravTick; the 34 + 2 rows)
hrep('''    check(tt4.count("tickPlayer") == 4 and "onBowShot" in gb4,''', '''    check(tt4.count("tickPlayer") == 5 and "onBowShot" in gb4,''')          # 0.1.12: + Monk.tickPlayer
hrep('''tt10.count("tickPlayer") == 4 and "fallSafe" in gf10''', '''tt10.count("tickPlayer") == 5 and "fallSafe" in gf10 and "onFall" in gf10''')
hrep('''                                                      "backstabBonus", "staminaCost", "players", "neutral")]      # 0.1.8
''', '''                                                      "backstabBonus", "staminaCost", "players", "neutral")]      # 0.1.8
    NEW_ROWS += ["monk.moves", "vault.lunge", "vault.lungeTime", "vault.height", "vault.distance", "vault.pushBoost", "vault.kickDamage", "vault.kickReach",
                 "vault.stamina", "vault.mana", "vault.airJump", "flow.slower", "flow.fallDamage", "bound.before", "bound.after", "bound.distance",
                 "bound.perBlock", "bound.cap", "bound.height", "bound.stamina", "bound.mana", "rise.height", "rise.forward", "rise.damage",
                 "rise.coneLength", "rise.coneWidth", "rise.knockUp", "rise.hang", "rise.airKnockback", "rise.stamina", "rise.mana", "plunge.speed",
                 "plunge.damage", "plunge.radius"]      # 0.1.12 the Monk moves
''')
hrep('''          and len(keys) == 10 + NN + 14 + 8 + 8 + 5 + 2 + 2 + 17 + 20 + 3,''', '''          and len(keys) == 10 + NN + 14 + 8 + 8 + 5 + 2 + 2 + 17 + 20 + 3 + 2,          # 0.1.12: + fixed.monk.keys / fixed.monk.debug''')
# ---- R15 (JVM): before L2 (L2 changes the store)
R15 = r'''    # ============================================================================ R15. 0.1.12 THE MONK MOVES - every new path EXECUTED
    from jpype import JLong
    MK, MKS = JClass(PKG + "Monk"), JClass(PKG + "MonkState")
    # R15a THE ENGINE ASSET VALIDATORS on the 15 new interactions, the 2 markers, the 13 changed roots and the Fist animation set (the REAL files)
    val15, objs15 = [], {}
    for n_ in MK12_NEW + MK12_CHG:
        c_ = INTc if n_.startswith("Server/Item/Interactions/") else (PRJc if n_.startswith("Server/Projectiles/") else
                                                                       (ROOTc if n_.startswith("Server/Item/RootInteractions/") else IPAc))
        o_, w_ = validate14(c_, os.path.basename(n_)[:-5], JREAL.read(n_).decode("utf-8"))
        if o_ is None or w_:
            val15.append("%s: %s" % (n_, w_))
            continue
        objs15.setdefault(c_, []).append((os.path.basename(n_)[:-5], o_))
    check(not val15 and sum(len(v_) for v_ in objs15.values()) == 31,
          "R15a: the ENGINE ASSET VALIDATORS pass on all 31 new / changed assets (15 interactions, 2 markers, 13 roots, the Fist animation set) and "
          "every inline step in them (decode, the codec's full validate pass, logOrThrowValidatorExceptions, contained assets): %s" % val15[:4])
    # R15a2 (fix round): the decoded fist Charging steps (and the Bo one) have allowIndefiniteHold = true -> validateChargeValue never caps at the
    # highest key (no 'charge value .. exceeds max allowed' WARN), the hold fires on release; NEGATIVE CONTROL: the vanilla dagger step decodes false
    CHI15 = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.ChargingInteraction")
    fAIH15 = CHI15.class_.getDeclaredField("allowIndefiniteHold")
    fAIH15.setAccessible(True)
    aih15 = sorted((k_, bool(fAIH15.getBoolean(o_))) for k_, o_ in objs15.get(INTc, []) if k_.endswith("_Charge"))
    vdg15, wdg15 = validate14(INTc, "Weapon_Daggers_Primary", json.dumps(aj("int", "Weapon_Daggers_Primary")))
    check(len(aih15) == 13 and all(v_ for k_, v_ in aih15) and vdg15 is not None and not bool(fAIH15.getBoolean(vdg15)),
          "R15a2 (fix): the 12 fist Charging steps + the Bo one decode with allowIndefiniteHold = true (fire on release, the charge value is never "
          "capped at the 0.6 key -> no overshoot WARN); NEGATIVE CONTROL the vanilla Weapon_Daggers_Primary decodes false: %s %s" % (aih15[:3], wdg15))
    # R15b: the real roots into the store, then RootInteraction.build(): Charging -> the tap chain + the marker launch, nothing missing
    for c_ in (INTc, PRJc, ROOTc, IPAc):
        load(c_, [o_ for k_, o_ in objs15.get(c_, [])], PACK)
    nm0 = len([m_ for lv_, m_ in records() if "Missing interaction" in m_])
    cb15 = []
    for rid_ in ["SkyyArmory_Bo_Primary"] + [os.path.basename(n_)[:-5] for n_ in MK12_FROOTS]:
        res_ = compile_root(rid_)
        cls_ = [cn_ for cn_, iid_ in res_["ops"]]
        bad_ = [x_ for x_ in res_["bad"] if not any(x_.endswith(" " + v_) for v_ in van14)]
        if bad_ or "ChargingInteraction" not in cls_ or "LaunchProjectileInteraction" not in cls_ or "ChainingInteraction" not in cls_:
            cb15.append((rid_, bad_[:2], cls_[:8]))
    nm1 = len([m_ for lv_, m_ in records() if "Missing interaction" in m_])
    check(not cb15 and nm1 == nm0, "R15b: RootInteraction.build() on the real stores - the Bo root and the 12 fist roots compile to Charging -> the tap chain "
                                   "(Chaining) + the marker launch (LaunchProjectile), 0 missing interactions: %s" % cb15[:2])
    for c_ in (ROOTc, IPAc):          # the 0.1.11 shapes back for the checks after this one (L2 reads the store)
        pass
    # R15c THE MONK JAVA on the engine stand-ins
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    if DCSc.PHYSICAL is None:
        jfield(DCSc, "PHYSICAL").set(None, DCSc("Physical"))
    G15 = float(JClass("com.hypixel.hytale.server.core.modules.physics.util.PhysicsConstants").GRAVITY_ACCELERATION)
    rn = lambda v: round(float(v), 3)
    # -- R15c1 the pure maths
    vy45 = float(MK.vyFor(4.5, G15))
    vh7 = float(MK.hSpeed(7.0, vy45, G15))
    pure = [rn(vy45), rn(vh7), rn(MK.boundDist(5.0, 0.5, 8.0, 4.1)), rn(MK.boundDist(5.0, 0.5, 8.0, 30.0)), rn(MK.boundDist(5.0, 0.5, 8.0, -2.0)),
            bool(MK.timed(1000, 760, 250, 100)), bool(MK.timed(1000, 740, 250, 100)), bool(MK.timed(1000, 1100, 250, 100)), bool(MK.timed(1000, 1101, 250, 100)),
            bool(MK.timed(0, 1000, 250, 100)), rn(MK.slowVy(0.15, G15, 1000)), rn(MK.slowVy(0.15, G15, 0)), rn(MK.slowVy(2.0, G15, 500)),
            bool(MK.inCone(2.0, 0.5, 1.0, 0.0, 3.0, 0.75)), bool(MK.inCone(2.0, 1.0, 1.0, 0.0, 3.0, 0.75)), bool(MK.inCone(-1.0, 0.0, 1.0, 0.0, 3.0, 0.75)),
            bool(MK.bossWord("Trork_Chieftain", ACfg.STUN_BOSS)), bool(MK.bossWord("Snapdragon", ACfg.STUN_BOSS)), bool(MK.bossWord("Trork_Mauler", ACfg.STUN_BOSS)),
            rn(MK.boHit("Weapon_Bo_Iron")), rn(MK.boHit("Weapon_Staff_Bo_Wood")), rn(MK.fistHit("Weapon_Fist_Gauntlets_Iron")), rn(MK.fistHit("Weapon_Sword_Iron"))]
    check(abs(vy45 - math.sqrt(2.0 * G15 * 4.5)) < 1e-9 and abs(vh7 - 7.0 / (2.0 * vy45 / G15)) < 1e-9 and pure[2:] == [7.05, 13.0, 5.0, True, False, True, False, False,
          rn(-0.85 * G15), 0.0, 0.0, True, False, False, True, False, False, 12.2, 5.0, 9.2, 0.0],
          "R15c1: vy for 4.5 = sqrt(2 g h), forward speed = 7 / air time; bound 5 + 0.5 x 4.1 fallen = 7.05, cap +8 = 13, no negative; the timed "
          "window -250 .. +100 ms (edges in, 1 ms past out, no landing = no); the flowing fall 0.85 g t; the cone; boss words (whole parts); the "
          "Bo / fist hit tables (Iron Bo 12.2, vanilla Bo 5, Iron gauntlet jab 9.2, a sword 0): %s" % pure)
    # THE KICK TEST vs the probe's (M6: a sphere r 1.5 around your chest tested the mob's FEET point - it missed a Trork Mauler)
    def probe_sphere(px, py, pz, mx, my, mz):
        return math.sqrt((px - mx) ** 2 + (py + 1.0 - my) ** 2 + (pz - mz) ** 2) <= 1.5
    kt = [bool(MK.kickTest(0.0, 64.0, 0.0, 4.0, 64.0, 0.0, 2.0, 64.0, 1.5, 1.2, 2.4, 1.5, 1.8)),          # beside the path
          bool(MK.kickTest(4.0, 64.8, 0.5, 6.0, 64.8, 0.5, 5.0, 63.0, 0.5, 1.0, 2.4, 1.5, 1.8)),          # over a tall mob, its head in your path
          bool(MK.kickTest(0.0, 64.0, 0.0, 4.0, 64.0, 0.0, 2.0, 64.0, 4.0, 1.0, 2.0, 1.5, 1.8)),          # 4 aside: out of reach
          bool(MK.kickTest(0.0, 70.0, 0.0, 4.0, 70.0, 0.0, 2.0, 64.0, 0.0, 1.0, 2.0, 1.5, 1.8)),          # far above its head
          bool(MK.kickTest(0.0, 64.0, 0.0, 30.0, 64.0, 0.0, 15.0, 64.0, 0.0, 1.0, 2.0, 1.5, 1.8))]       # a fast tick (30 blocks): the segment is swept
    probe_miss = [any(probe_sphere(x_ / 4.0, 64.0, 0.0, 2.0, 64.0, 1.5) for x_ in range(0, 17)),
                  any(probe_sphere(4.0 + x_ / 4.0, 64.8, 0.5, 5.0, 63.0, 0.5) for x_ in range(0, 9))]
    check(kt == [True, True, False, False, True] and probe_miss == [False, False],
          "R15c1 (probe M6 fix): the kick = the BODY test along the swept path - a mob 1.5 beside your path and a tall mob whose head your feet pass "
          "are kicked, 4 aside / far above are not, a 30-block tick between 2 samples still hits; NEGATIVE CONTROL: the probe's feet-point sphere "
          "misses both of the first two: %s %s" % (kt, probe_miss))
    # -- the stand-ins: the caster (player 1), a clock, the area seam, the debug sink
    T15 = [1900000000000]

    def clk(ms_=33):
        T15[0] += ms_
        MK.CLOCK = JLong(T15[0])
    clk(0)
    NEAR15 = []

    @JImplements("java.util.function.Function")
    class Near15:
        @JOverride
        def apply(self, o):
            l_ = ArrayList()
            for r_ in NEAR15:
                l_.add(r_)
            return l_
    AT.NEAR = Near15()
    MST15 = JClass("com.hypixel.hytale.protocol.MovementStates")

    def mstate(r_, ground=True, jump=False, crouch=False):
        msc_ = MSCc()
        m_ = MST15()
        m_.onGround = ground
        m_.jumping = jump
        m_.crouching = crouch
        msc_.setMovementStates(m_)
        put(r_, MSCc.getComponentType(), msc_)

    def mpos(r_, x, y, z):
        comp(r_, TCc.getComponentType()).getPosition().set(x, y, z)

    def cvel(r_, x, y, z):
        comp(r_, VELc.getComponentType()).setClient(x, y, z)

    def tk(ms_=33, r_=None):
        clk(ms_)
        MK.tickPlayer(rc if r_ is None else r_, tst, tbuf)

    def ninst(r_):
        x_ = last_instr(r_)
        return 0 if x_ is None else x_[3]

    def mkevents():
        return [e_ for e_ in events() if e_[2] in ("EntitySource",)]

    def fall15(r_, amount):
        TCH.R = r_
        d_ = DMGc(ENTS(r_), DCSc.FALL, JFloat(amount))
        gfs.handle(0, tch, tst, tbuf, d_)
        return bool(d_.isCancelled()), rn(d_.getAmount())
    SINK15 = ArrayList()
    MK.SINK = SINK15
    MK.clear()
    MK.DEBUG.clear()
    hand15, look15 = LP.HAND, LP.LOOK
    LP.HAND, LP.LOOK = HashMap(), HashMap()          # the Leap seams (the item in hand + the look) for this section
    LP.HAND.put(cu, "Weapon_Bo_Iron")
    LP.LOOK.put(cu, JArray(JDouble)([0.5, 65.6, 0.5, 1.0, 0.0, 0.0]))
    put(rc, TPc.getComponentType(), None)
    put(rc, VELc.getComponentType(), VELc())
    mpos(rc, 0.5, 64.0, 0.5)
    mstate(rc, ground=True)
    mc.setStatValue(STAM, JFloat(10.0))
    mc.setStatValue(MANA, JFloat(200.0))
    TW.ALL.clear()
    reset_buf()
    MK.debugCmd(prc, "debug", "monk", "on")
    dbg_on = bool(MK.DEBUG.containsKey(cu)) and "Monk debug ON" in str(SINK15.get(SINK15.size() - 1))
    # -- R15c2 THE POLE-VAULT: the marker's SPAWN (ArmoryTravSys -> ArmoryTrav.added, code 12000)
    mA = mob(1510, 2.5, 64.0, 2.0, (1.2, 2.4, 1.2), role="Trork_Mauler")          # 1.5 beside the lunge path: the probe's sphere missed this
    mH = mob(1511, 7.0, 62.6, 0.5, (1.0, 2.4, 1.0), role="Trork_Mauler")          # under the vault: its head in the path
    mF = mob(1512, 3.0, 64.0, 5.0, (1.0, 2.0, 1.0), role="Trork_Mauler")          # 4.5 aside: never kicked
    NEAR15[:] = [mA, mH, mF, rc]
    vm, vpc = launched("SkyyArmory_Monk_Vault", 1520, 0.5, 65.6, 0.5)
    m0 = int(MK.MARKS)
    AT.added(vm, vpc, int(ADefs.pidCode("SkyyArmory_Monk_Vault")), tst, tbuf)
    s15 = MK.STATES.get(cu)
    fl_ = br.get("armory:monkmove:" + str(cu))
    v0 = (s15 is not None and int(s15.move) == 1, sv(mc, STAM), sv(mc, MANA), vm in list(TBf.REMOVED), int(MK.MARKS) - m0,
          fl_ is not None and int(fl_) == T15[0] + 500, rn(s15.kickAmt) if s15 is not None else None)
    check(dbg_on and int(ADefs.pidCode("SkyyArmory_Monk_Vault")) == 12000 and int(ADefs.pidCode("SkyyArmory_Monk_Rise")) == 12001
          and v0 == (True, 3.0, 197.0, True, 1, True, 24.4),
          "R15c2: the Bo hold's marker SPAWN (code 12000) -> the marker is removed, the vault starts (lunge), 7 Stamina + 3 Mana paid (10 -> 3, 200 -> 197), "
          "the Acrobatics flag armory:monkmove:<uuid> = now + 500 ms (a Long), kick = 2 x the Iron Bo hit 12.2 = 24.4; /armory debug monk on: %s" % (v0,))
    # the lunge: a Set every tick (3 blocks in 0.2 s = 15 b/s, your vertical speed kept), the kicks swept along the way
    n0 = ninst(rc)
    mpos(rc, 1.5, 64.0, 0.5)
    tk(33)
    l1 = last_instr(rc)
    mpos(rc, 3.0, 64.0, 0.5)
    tk(33)
    mpos(rc, 3.4, 64.0, 0.5)
    tk(33)
    ev1 = sorted((e_[0], e_[1]) for e_ in mkevents())
    check(l1 is not None and l1[0] == (15.0, 0.0, 0.0) and l1[1] == "Set" and l1[2] is None and ninst(rc) == n0 + 3
          and ev1 == [(1510, 24.4)] and int(s15.kicks) == 1,
          "R15c2: the lunge = a velocity Set every tick (15 b/s along your look, no dash config); the Trork Mauler 1.5 beside the path is kicked "
          "ONCE (PHYSICAL from you, 24.4) though three ticks pass it, the mob 4.5 aside never: %s %s" % (l1, ev1))
    mpos(rc, 3.5, 64.0, 0.5)
    tk(140)          # past vault.lungeTime 0.2 s: the vault Set
    l2 = last_instr(rc)
    want_v = (rn(vh7 * 2.1), rn(vy45), 0.0)
    check(l2 is not None and (rn(l2[0][0]), rn(l2[0][1]), rn(l2[0][2])) == want_v and int(s15.move) == 2 and bool(s15.chain) and bool(s15.flow)
          and int(s15.airUntil) == T15[0] + 4000 and rn(s15.lungeD) == 3.0,
          "R15c2: after vault.lungeTime the VAULT Set = (forward 7 / air time x the push boost 2.1, up sqrt(2 g 4.5), 0) = %s; the bounds chain, "
          "the flowing fall and the free air jump (4 s) are armed; lunge measured 3.0: %s" % (want_v, l2))
    # in the air: the tall mob under the path is kicked (the probe's sphere missed it), the flowing fall from the top, the free air jump
    mstate(rc, ground=False)
    cvel(rc, 10.0, 12.0, 0.0)
    mpos(rc, 5.5, 64.8, 0.5)
    tk(33)
    mpos(rc, 7.5, 64.8, 0.5)
    tk(33)
    ev2 = sorted((e_[0], e_[1]) for e_ in mkevents())
    cvel(rc, 9.0, -0.5, 0.0)
    mpos(rc, 8.0, 68.5, 0.5)
    tk(33)          # the top
    nf0 = ninst(rc)
    cvel(rc, 9.0, -3.0, 0.0)
    mpos(rc, 8.5, 68.0, 0.5)
    tk(100)
    fl1 = last_instr(rc)
    check(ev2 == [(1510, 24.4), (1511, 24.4)] and fl1 is not None and ninst(rc) == nf0 + 1
          and (rn(fl1[0][0]), rn(fl1[0][1]), rn(fl1[0][2])) == (9.0, rn(MK.slowVy(0.15, G15, 100)), 0.0),
          "R15c2: in the air the tall mob whose head the path crosses is kicked (once); 100 ms past the top the FLOWING FALL Set keeps your sideways "
          "speed (you steer) and falls 0.85 g t: %s %s" % (ev2, fl1))
    mstate(rc, ground=False, crouch=True)
    tk(33)
    aj1 = last_instr(rc)
    na1 = int(MK.AIRJUMPS)
    mstate(rc, ground=False, crouch=False)
    tk(33)
    mstate(rc, ground=False, crouch=True)
    tk(33)
    check(aj1 is not None and rn(aj1[0][0]) == 9.0 and aj1[0][1] > 5.0 and int(MK.AIRJUMPS) == na1 and bool(s15.airUsed),
          "R15c2: CROUCH in mid-air = the ONE free air jump (up at the jump force, your sideways speed kept); a second crouch does nothing: %s" % (aj1,))
    # the landing: the FALL damage is HELD (the chain), the report line; a jump 40 ms after the landing = a BOUND, the held fall forgiven
    cvel(rc, 8.0, -12.0, 0.0)
    mpos(rc, 9.0, 66.0, 0.5)
    tk(33)
    held = fall15(rc, 10.0)
    mstate(rc, ground=True)
    cvel(rc, 0.0, 0.0, 0.0)
    mpos(rc, 10.0, 64.0, 0.5)
    tk(33)
    rep1 = [str(x_) for x_ in SINK15 if str(x_).startswith("Pole-Vault: lunge")]
    mstate(rc, ground=True, jump=True)
    tk(40)
    b1 = last_instr(rc)
    reset_buf()
    tk(33)
    nb1 = (int(MK.BOUNDS), int(MK.FORGIVEN), sv(mc, STAM), sv(mc, MANA), int(s15.bounds), bool(s15.chain), int(s15.airUntil))
    fell1 = float(s15.landFell)
    vyb = 11.8 * math.sqrt(1.4)
    check(held == (True, 10.0) and int(s15.move) == 0 and len(rep1) == 1 and "kicked 2 x 24.4" in rep1[0] and "air jump used" in rep1[0]
          and b1 is not None and rn(b1[0][1]) == rn(vyb) and rn(b1[0][0]) == rn(MK.hSpeed(MK.boundDist(5.0, 0.5, 8.0, fell1), vyb, G15) * 2.1)
          and nb1[1] >= 1 and nb1[2:] == (0.0, 196.0, 1, True, 0) and not [e_ for e_ in events() if e_[0] == 1],
          "R15c3: at the landing the FALL damage is HELD (cancelled) - the report line says lunge / forward / height / air / kicks / air jump; a jump "
          "40 ms after the landing = a BOUND (1.4 x a jump, forward 5 + 0.5 per block fallen x 2.1 along your look), 3 Stamina + 1 Mana, the held "
          "fall FORGIVEN (no damage dealt), the free air jump gone: %s %s %s" % (held, rep1[:1], nb1))
    # the next landing with 0 Stamina: the bound is refused -> the chain ends; the held FALL damage is re-dealt at 85 %
    mstate(rc, ground=False)
    cvel(rc, 6.0, -10.0, 0.0)
    mpos(rc, 14.0, 66.0, 0.5)
    tk(33)
    mpos(rc, 16.0, 65.0, 0.5)
    tk(33)
    held2 = fall15(rc, 10.0)
    mstate(rc, ground=True)
    mpos(rc, 17.0, 64.0, 0.5)
    tk(33)
    rep2 = [str(x_) for x_ in SINK15 if str(x_).startswith("Bound 1 landed")]
    mstate(rc, ground=True, jump=True)
    reset_buf()
    tk(30)
    refused2 = (bool(s15.chain), int(MK.BOUNDS))
    tk(200)
    ev3 = [e_ for e_ in events() if e_[0] == 1]
    check(held2 == (True, 10.0) and len(rep2) == 1 and refused2 == (False, nb1[0]) and len(ev3) == 1 and ev3[0][1] == 8.5,
          "R15c3: with 0 Stamina the timed jump is refused and the bounds END; the landing's held FALL damage is then re-dealt at 85 %% (10 -> 8.5): "
          "%s %s %s" % (held2, refused2, ev3))
    # the flag outlives the move by ~0.5 s, then the record goes
    tk(900)
    tk(900)
    tk(900)
    gone15 = MK.STATES.get(cu) is None
    fl2 = br.get("armory:monkmove:" + str(cu))
    check(gone15 and fl2 is not None and int(fl2) < T15[0] and int(fl2) > T15[0] - 4000,
          "R15c3: after the chain ends and the flowing fall is over the record goes; the flag's last value is in the past (SkyySkills pays again): %s" % fl2)
    # an EARLY press (0.2 s before the landing) bounds at the landing too
    mc.setStatValue(STAM, JFloat(20.0))
    mpos(rc, 0.5, 64.0, 0.5)
    mstate(rc, ground=True)
    cvel(rc, 0.0, 0.0, 0.0)
    vm2, vpc2 = launched("SkyyArmory_Monk_Vault", 1521, 0.5, 65.6, 0.5)
    AT.added(vm2, vpc2, 12000, tst, tbuf)
    s15 = MK.STATES.get(cu)
    tk(250)
    mstate(rc, ground=False)
    cvel(rc, 10.0, 12.0, 0.0)
    mpos(rc, 2.0, 66.0, 0.5)
    tk(33)
    cvel(rc, 10.0, -8.0, 0.0)
    mpos(rc, 5.0, 66.0, 0.5)
    tk(300)
    mstate(rc, ground=False, jump=True)
    tk(33)
    nb2 = int(MK.BOUNDS)
    mstate(rc, ground=True, jump=True)
    mpos(rc, 7.0, 64.0, 0.5)
    tk(200)
    check(int(MK.BOUNDS) == nb2 + 1 and int(s15.bounds) == 1, "R15c3: a jump pressed 0.2 s BEFORE the landing (the server sees it in the air) bounds at the landing")
    # REFUND: a vault that does not move you (a wall, a ceiling) costs nothing
    MK.clear()
    mc.setStatValue(STAM, JFloat(10.0))
    mc.setStatValue(MANA, JFloat(200.0))
    mpos(rc, 0.5, 64.0, 0.5)
    mstate(rc, ground=True)
    vm3, vpc3 = launched("SkyyArmory_Monk_Vault", 1522, 0.5, 65.6, 0.5)
    AT.added(vm3, vpc3, 12000, tst, tbuf)
    paid3 = (sv(mc, STAM), sv(mc, MANA))
    for _i in range(14):
        tk(120)
    check(paid3 == (3.0, 197.0) and (sv(mc, STAM), sv(mc, MANA)) == (10.0, 200.0) and int(MK.REFUNDS) >= 1,
          "R15c4 (LOCKED: a traversal that does not move you costs nothing): a vault that never left the ground gives the 7 Stamina + 3 Mana back: %s -> %s" % (
              paid3, (sv(mc, STAM), sv(mc, MANA))))
    # REFUSALS cost nothing: in the air, the class lock, no Bo in hand, too little Stamina
    def vtry(ground=True, hand="Weapon_Bo_Iron", deny=None, stam=10.0, code=12000, pid="SkyyArmory_Monk_Vault"):
        MK.clear()
        mc.setStatValue(STAM, JFloat(stam))
        mc.setStatValue(MANA, JFloat(200.0))
        mstate(rc, ground=ground)
        LP.HAND.put(cu, hand)
        if deny:
            br.put("class:fn:allowed", DenyId(deny))
        o_, p_ = launched(pid, 1530 + int(MK.REFUSED) % 50, 0.5, 65.6, 0.5)
        AT.added(o_, p_, code, tst, tbuf)
        br.remove("class:fn:allowed")
        s_ = MK.STATES.get(cu)
        return (s_ is not None and int(s_.move) != 0, sv(mc, STAM), sv(mc, MANA), str(MK.LAST_WHY))
    rf = [vtry(ground=False), vtry(deny="Weapon_Bo_Iron"), vtry(hand="Weapon_Sword_Iron"), vtry(stam=5.0),
          vtry(ground=False, hand="Weapon_Fist_Gauntlets_Iron", code=12001, pid="SkyyArmory_Monk_Rise"), vtry(hand="Weapon_Bo_Iron", code=12001, pid="SkyyArmory_Monk_Rise")]
    LP.HAND.put(cu, "Weapon_Bo_Iron")
    check(rf == [(False, 10.0, 200.0, "Pole-Vault: not on the ground"), (False, 10.0, 200.0, "Pole-Vault: class lock"),
                 (False, 10.0, 200.0, "vault: no Bo staff in hand"), (False, 5.0, 200.0, "Pole-Vault: too little Stamina or Mana"),
                 (False, 10.0, 200.0, "Rising Strike: not on the ground"), (False, 10.0, 200.0, "rise: no fist weapon in hand")],
          "R15c4: refusals cost NOTHING - in the air, SkyyClasses' class lock, a non-Bo item, 5 < 7 Stamina; Rising Strike in the air / with a Bo: %s" % rf)
    # -- R15c5 RISING STRIKE (code 12001): the cone hit + knock-up (a boss is hit, never lifted), the hang, the air-hit fling, the plunge
    MK.clear()
    LP.HAND.put(cu, "Weapon_Fist_Gauntlets_Iron")
    mc.setStatValue(STAM, JFloat(10.0))
    mc.setStatValue(MANA, JFloat(200.0))
    mpos(rc, 0.5, 64.0, 0.5)
    mstate(rc, ground=True)
    cvel(rc, 0.0, 0.0, 0.0)
    mC = mob(1540, 2.0, 64.0, 0.5, (1.0, 2.0, 1.0), role="Trork_Mauler")
    mD = mob(1541, 2.5, 64.0, 1.0, (1.0, 2.0, 1.0), role="Goblin_Scrapper")
    mB = mob(1542, 2.0, 64.0, 0.0, (1.4, 2.6, 1.4), role="Trork_Chieftain")
    mK = mob(1543, -4.0, 64.0, 0.5, (1.0, 2.0, 1.0), role="Trork_Mauler")          # behind you, out of the slam
    NEAR15[:] = [mC, mD, mB, mK, rc]
    reset_buf()
    rm, rpc = launched("SkyyArmory_Monk_Rise", 1544, 0.5, 65.6, 0.5)
    AT.added(rm, rpc, 12001, tst, tbuf)
    s15 = MK.STATES.get(cu)
    r1 = last_instr(rc)
    hitsR = sorted((e_[0], e_[1]) for e_ in mkevents())
    upsR = sorted(int(x_.getIndex()) for x_ in s15.ups)
    kc = last_instr(mC)
    kb = last_instr(mB)
    ku = rn(MK.vyFor(5.0, G15))
    check(int(s15.move) == 3 and (sv(mc, STAM), sv(mc, MANA)) == (2.0, 196.0) and r1 is not None and (rn(r1[0][0]), rn(r1[0][1]), rn(r1[0][2])) == (1.0, rn(MK.vyFor(6.0, G15)), 0.0)
          and hitsR == [(1540, 11.04), (1541, 11.04), (1542, 11.04)] and upsR == [1540, 1541] and kc is not None and (rn(kc[0][0]), rn(kc[0][1]), rn(kc[0][2])) == (0.0, ku, 0.0)
          and kc[2] == (0.97, 0.94, 5.0, "Exp") and kb is None,
          "R15c5: the fist hold's marker (code 12001) -> RISING STRIKE: 8 Stamina + 4 Mana, the Set up for 6 blocks with 1 b/s drift; the 3 enemies in "
          "the cone ahead are hit for 1.2 x the Iron gauntlet jab 9.2 = 11.04, the one behind is not; the 2 plain mobs are knocked up (vy for 5, the "
          "dagger dash push), the Trork Chieftain (stun.bossWords) is hit but never lifted: %s %s %s" % (hitsR, upsR, kc))
    mstate(rc, ground=False)
    cvel(rc, 0.0, 15.0, 0.0)
    mpos(rc, 0.8, 66.0, 0.5)
    tk(33)
    cvel(rc, 0.4, 0.3, 0.0)
    mpos(rc, 1.0, 70.0, 0.5)
    tk(400)
    apex = (int(s15.move), [str(x_) for x_ in SINK15 if str(x_).startswith("Rising Strike top")][-1:])
    cvel(rc, 0.4, -0.5, 0.0)
    tk(33)
    h1 = last_instr(rc)
    hm = last_instr(mC)
    # an air hit on a lifted enemy (your own melee, the Inspect group) -> it is flung
    TCH.R = mC
    dh = DMGc(ENTS(rc), DCSc.PHYSICAL, JFloat(5.0))
    HS.handle(0, tch, tst, tbuf, dh)
    fg = last_instr(mC)
    upsA = sorted(int(x_.getIndex()) for x_ in s15.ups)
    check(apex[0] == 4 and len(apex[1]) == 1 and "rose 6.0" in apex[1][0] and h1 is not None and (rn(h1[0][0]), rn(h1[0][1])) == (0.2, -1.0)
          and hm is not None and (rn(hm[0][1]), hm[2]) == (-1.0, (0.97, 0.94, 5.0, "Exp"))
          and fg is not None and (rn(fg[0][0]), rn(fg[0][1]), rn(fg[0][2])) == (12.0, 2.0, 0.0) and upsA == [1541] and int(MK.FLINGS) >= 1,
          "R15c5: at the top the HANG - a Set every tick for you (half your sideways speed, -1 down) and the lifted enemies (-1); your hit on a "
          "lifted enemy flings it 6 blocks along your look (12 b/s + 2 up, the dash push) and it is no longer held: %s %s %s %s" % (apex, h1, hm, fg))
    # CROUCH during the hang = PLUNGE PUNCH: 30 b/s down for you + the held enemy, no fall damage, the slam at the landing
    mstate(rc, ground=False, crouch=True)
    tk(33)
    plunged = int(s15.move)
    cvel(rc, 0.0, -29.0, 0.0)
    mpos(rc, 1.0, 66.0, 0.5)
    tk(33)
    p1 = last_instr(rc)
    pd = last_instr(mD)
    pfall = fall15(rc, 12.0)
    mstate(rc, ground=True, crouch=True)
    mpos(rc, 1.0, 64.0, 0.5)
    comp(mD, TCc.getComponentType()).getPosition().set(2.0, 64.5, 1.0)
    reset_buf()
    tk(33)
    slam = sorted((e_[0], e_[1]) for e_ in mkevents())
    plg = [str(x_) for x_ in SINK15 if str(x_).startswith("Plunge landed")]
    pfall2 = fall15(rc, 12.0)
    check(plunged == 5 and p1 is not None and (rn(p1[0][0]), rn(p1[0][1]), rn(p1[0][2])) == (0.0, -30.0, 0.0) and pd is not None and rn(pd[0][1]) == -30.0
          and pfall == (True, 12.0) and pfall2[0] and int(s15.move) == 0 and int(MK.PLUNGES) >= 1
          and slam == [(1540, 9.2), (1541, 9.2), (1542, 9.2)] and len(plg) == 1 and "1/1 lifted enemies came down with you" in plg[0] and "fastest 29.0" in plg[0],
          "R15c5: CROUCH in the hang = PLUNGE PUNCH - you and the held enemy are Set to 30 b/s down every tick (Skyy: 14 was slow), the FALL damage is "
          "cancelled (in the air and at the landing), the slam hits every enemy within 3 blocks for 1.0 x the jab (9.2), the report says the speed and "
          "the dragged enemy: %s %s %s" % (slam, plg, pfall))
    # no plunge: the hang ends -> the flowing fall (steer), -15 % fall damage
    MK.clear()
    mc.setStatValue(STAM, JFloat(10.0))
    mpos(rc, 0.5, 64.0, 0.5)
    mstate(rc, ground=True)
    cvel(rc, 0.0, 0.0, 0.0)
    NEAR15[:] = [rc]
    rm2, rpc2 = launched("SkyyArmory_Monk_Rise", 1545, 0.5, 65.6, 0.5)
    AT.added(rm2, rpc2, 12001, tst, tbuf)
    s15 = MK.STATES.get(cu)
    mstate(rc, ground=False)
    cvel(rc, 0.0, 15.0, 0.0)
    mpos(rc, 0.5, 66.0, 0.5)
    tk(33)
    cvel(rc, 0.0, 0.2, 0.0)
    mpos(rc, 0.5, 70.0, 0.5)
    tk(400)
    tk(1250)
    nf = int(s15.move)
    cvel(rc, 3.0, -5.0, 0.0)
    tk(100)
    ff = last_instr(rc)
    ffall = fall15(rc, 20.0)
    mstate(rc, ground=True)
    mpos(rc, 1.0, 64.0, 0.5)
    tk(33)
    check(nf == 6 and ff is not None and rn(ff[0][0]) == 3.0 and rn(ff[0][1]) == rn(MK.slowVy(0.15, G15, 100)) and ffall == (False, 17.0) and int(s15.move) == 0,
          "R15c5: no crouch -> after rise.hang the flowing fall (a Set every tick, your sideways speed kept = you steer) and the fall damage -15 %% "
          "(20 -> 17): %s %s" % (ff, ffall))
    # -- R15c7 (fix round) a plunge cut short by WATER keeps NO fall immunity (before: noFallUntil stayed ~6.5 s)
    MK.clear()
    mc.setStatValue(STAM, JFloat(10.0))
    mpos(rc, 0.5, 64.0, 0.5)
    mstate(rc, ground=True)
    cvel(rc, 0.0, 0.0, 0.0)
    NEAR15[:] = [rc]
    rm3, rpc3 = launched("SkyyArmory_Monk_Rise", 1547, 0.5, 65.6, 0.5)
    AT.added(rm3, rpc3, 12001, tst, tbuf)
    s15 = MK.STATES.get(cu)
    mstate(rc, ground=False)
    cvel(rc, 0.0, 15.0, 0.0)
    mpos(rc, 0.5, 66.0, 0.5)
    tk(33)
    cvel(rc, 0.0, 0.2, 0.0)
    mpos(rc, 0.5, 70.0, 0.5)
    tk(33)
    mstate(rc, ground=False, crouch=True)
    tk(33)
    wp0 = (int(s15.move), int(s15.noFallUntil) > T15[0])
    msw_ = MSCc()
    mw_ = MST15()
    mw_.onGround = False
    mw_.inFluid = True
    msw_.setMovementStates(mw_)
    put(rc, MSCc.getComponentType(), msw_)
    tk(33)
    wp1 = (int(s15.move), int(s15.noFallUntil))
    mstate(rc, ground=False)
    tk(33)
    wfall = fall15(rc, 12.0)
    check(wp0 == (5, True) and wp1 == (0, 0) and wfall == (False, 12.0),
          "R15c7 (fix): a Plunge Punch (move 5, fall immunity on) that touches water ends with NO fall immunity left - the next fall deals its full "
          "12 (before the fix it was cancelled for ~6.5 s): %s %s %s" % (wp0, wp1, wfall))
    # -- R15c8 (fix round) a player who LEFT mid-move (never ticks again): any other player's tick drops records idle 30 s + their flag, every 5 s
    MK.clear()
    gu_ = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    fu_ = UUID.fromString("00000000-0000-0000-0000-0000000000a2")
    gs_ = MKS(gu_, rc, tst)
    gs_.last = T15[0] - 40000
    gs_.chain = True
    fs_ = MKS(fu_, rc, tst)
    fs_.last = T15[0] - 1000          # NEGATIVE CONTROL: idle only 1 s - kept
    MK.STATES.put(gu_, gs_)
    MK.STATES.put(fu_, fs_)
    MK.flag(gu_, T15[0] - 39500)
    MK.flag(fu_, T15[0] + 500)
    MK.SWEPT = JLong(T15[0] - 1000)          # swept 1 s ago: not yet
    st0 = int(MK.STALE)
    tk(33)
    sw0 = (MK.STATES.containsKey(gu_), MK.STATES.containsKey(fu_))
    MK.SWEPT = JLong(T15[0] - 6000)
    tk(33)
    sw1 = (MK.STATES.containsKey(gu_), MK.STATES.containsKey(fu_), br.get("armory:monkmove:" + str(gu_)) is None,
           br.get("armory:monkmove:" + str(fu_)) is not None, MK.FLAGGED.containsKey(gu_), int(MK.STALE) - st0, int(MK.SWEPT) == T15[0])
    MK.clear()
    check(sw0 == (True, True) and sw1 == (False, True, True, True, False, 1, True),
          "R15c8 (fix): a record whose player left mid-move (no tick for 40 s) is dropped by another player's tick once the 5 s sweep is due "
          "(its bridge flag + FLAGGED entry too, STATES can empty again); a record idle 1 s stays; no sweep before 5 s: %s %s" % (sw0, sw1))
    # -- R15c6 the dispatch through the real systems: TravTick runs the Monk tick, a world change ends the record, the command, the flag
    MK.clear()
    LP.HAND.put(cu, "Weapon_Bo_Iron")
    mc.setStatValue(STAM, JFloat(10.0))
    mpos(rc, 0.5, 64.0, 0.5)
    mstate(rc, ground=True)
    vm4, vpc4 = launched("SkyyArmory_Monk_Vault", 1546, 0.5, 65.6, 0.5)
    AT.added(vm4, vpc4, 12000, tst, tbuf)
    TTK = JClass(PKG + "TravTick")()
    TCH.R = rc
    ni0 = ninst(rc)
    clk(33)
    TTK.tick(JFloat(0.033), 0, tch, tst, tbuf)
    ni1 = ninst(rc)
    other = U.allocateInstance(TSt.class_)
    clk(33)
    MK.tickPlayer(rc, other, tbuf)
    gone_w = MK.STATES.get(cu) is None
    check(ni1 == ni0 + 1 and gone_w, "R15c6: TravTick.tick runs the Monk tick (one lunge Set); a tick in another world ends the record")
    AC12 = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fpg = AC12.class_.getDeclaredField("permissionGroups")
    fpg.setAccessible(True)
    cmd_ok = []
    for cn_ in ("ArmoryCmd", "ArmoryDbgCmd"):
        try:
            c_ = JClass(PKG + cn_)()
            perm_ = c_.getPermission()
            grp_ = fpg.get(c_)
            cmd_ok.append((cn_, "skyyarmory.admin" in (str(perm_.getId()) if hasattr(perm_, "getId") else str(perm_)), grp_ is not None and len(grp_) == 0))
            if cn_ == "ArmoryCmd":
                rec_ = c_.getPermissionGroupsRecursive()
                leak_ = [str(k_) for k_ in rec_.keySet() if rec_.get(k_) is not None and any("skyyarmory.admin" in str(x_) for x_ in rec_.get(k_))]
                cmd_ok.append(("leak", not leak_, str(c_.getName()) == "armory"))
        except Exception as e_:
            cmd_ok.append((cn_, "construct failed %s" % str(e_)[:200], False))
    SINK15.clear()
    MK.debugCmd(prc, "debug", "monk", "off")
    off_ = (not MK.DEBUG.containsKey(cu), "Monk debug off." in [str(x_) for x_ in SINK15])
    SINK15.clear()
    MK.debugCmd(prc, "debug", "monks", "on")
    MK.help(prc)
    help_ = [str(x_) for x_ in SINK15]
    br.put("armory:monkmove:00000000-0000-0000-0000-00000000abcd", JLong(5))
    MK.FLAGGED.put(UUID.fromString("00000000-0000-0000-0000-00000000abcd"), JClass("java.lang.Boolean").TRUE)
    MK.clear()
    check(cmd_ok == [("ArmoryCmd", True, True), ("leak", True, True), ("ArmoryDbgCmd", True, True)] and off_ == (True, True)
          and len(help_) == 2 and all(h_.startswith("/armory debug monk on|off (admin)") for h_ in help_) and not MK.DEBUG.containsKey(cu)
          and br.get("armory:monkmove:00000000-0000-0000-0000-00000000abcd") is None and MK.STATES.isEmpty(),
          "R15c6: /armory + its usage variant need skyyarmory.admin with EMPTY permission groups (no group is handed the node); debug off; a wrong "
          "word shows the usage, not a toggle; Monk.clear() removes every flag it set: %s %s %s" % (cmd_ok, off_, help_[:1]))
    MK.CLOCK = JLong(0)
    MK.SINK = None
    AT.NEAR = None
    LP.HAND, LP.LOOK = hand15, look15
    print("R15c. Monk moves executed: vault (lunge %s, vault %s, kicks %d), bounds %d (forgiven %d, re-dealt %d), refunds %d, refusals %d, rises %d, "
          "flings %d, plunges %d, air jumps %d, flowing-fall Sets %d" % (l1[0] if l1 else None, l2[0] if l2 else None, int(MK.KICKS), int(MK.BOUNDS),
                                                                       int(MK.FORGIVEN), int(MK.REDEALT), int(MK.REFUNDS), int(MK.REFUSED),
                                                                       int(MK.RISES), int(MK.FLINGS), int(MK.PLUNGES), int(MK.AIRJUMPS), int(MK.FLOWED)))
    # R15e: vs the 0.1.11 jar - file by file, then METHOD BY METHOD (javassist's instruction printer, offsets dropped, the version text = V)
    on_ = OZ111.namelist()
    nn_ = JREAL.namelist()
    new_ = sorted(set(nn_) - set(on_))
    gone_ = sorted(set(on_) - set(nn_))
    diff_ = sorted(n_ for n_ in on_ if n_ in set(nn_) and not n_.endswith(".class") and n_ != "manifest.json" and OZ111.read(n_) != JREAL.read(n_))
    check(sorted(n_ for n_ in new_ if not n_.endswith(".class")) == MK12_NEW and sorted(n_ for n_ in new_ if n_.endswith(".class")) == sorted(
              "com/skyy/armory/%s.class" % c_ for c_ in ("Monk", "MonkState", "ArmoryCmd", "ArmoryDbgCmd")) and not gone_ and diff_ == sorted(MK12_CHG + [MK12_LANG]),
          "R15e: vs SkyyArmory-0.1.11.jar - new = the 17 Monk files + 4 classes (Monk, MonkState, ArmoryCmd, ArmoryDbgCmd), none gone, changed "
          "non-class files = the Bo root, 12 fist roots, the Fist animation set, the lang: new %s gone %s diff %s" % (new_[:4], gone_[:3], sorted(set(diff_) ^ set(MK12_CHG + [MK12_LANG]))[:4]))
    IP15, PS15, BOS15 = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def methods_of(jarp):
        cp_ = JClass("javassist.ClassPool")(False)
        cp_.insertClassPath(jarp)          # first: the harness JVM's own class path holds the 0.1.12 jar
        cp_.appendClassPath(B.SERVER_JAR)
        cp_.appendSystemPath()
        out_ = {}
        for n_ in zipfile.ZipFile(jarp).namelist():
            if not n_.endswith(".class"):
                continue
            cc_ = cp_.get(n_[:-6].replace("/", "."))
            ms_ = {}
            for m_ in list(cc_.getDeclaredMethods()):
                if m_.getMethodInfo().getCodeAttribute() is None:
                    ms_["%s%s" % (m_.getName(), m_.getSignature())] = ""
                    continue
                bos_ = BOS15()
                IP15(PS15(bos_)).print_(m_)
                t_ = re.sub(r"#\d+ = ", "", str(bos_.toString()))
                t_ = re.sub(r"(?m)^\s*\d+: ", "", t_).replace("ldc_w ", "ldc ")
                t_ = re.sub(r"(?m)^((?:goto|goto_w|if\w*|jsr) )-?\d+", r"\1L", t_)
                ms_["%s%s" % (m_.getName(), m_.getSignature())] = t_.replace("0.1.12", "V").replace("0.1.11", "V")
            for c_ in list(cc_.getDeclaredConstructors()):
                ca_ = c_.getMethodInfo().getCodeAttribute()
                ms_["<init>" + str(c_.getSignature())] = str(ca_.getCodeLength()) if ca_ is not None else ""
            out_[n_.rsplit("/", 1)[1][:-6]] = (ms_, sorted("%s:%s" % (f_.getName(), f_.getSignature()) for f_ in cc_.getDeclaredFields()))
        return out_
    MN, MO = methods_of(JAR), methods_of(OLD111)
    cmp15 = {}
    for c_ in sorted(set(MN) | set(MO)):
        if c_ not in MN or c_ not in MO:
            cmp15[c_] = "only in " + ("0.1.12" if c_ in MN else "0.1.11")
            continue
        ch_ = sorted(k_ for k_ in set(MN[c_][0]) | set(MO[c_][0]) if MN[c_][0].get(k_) != MO[c_][0].get(k_))
        fd_ = sorted(set(MN[c_][1]) ^ set(MO[c_][1]))
        if ch_ or fd_:
            cmp15[c_] = {"methods": [k_.split("(")[0] for k_ in ch_], "fields": [f_.split(":")[0] for f_ in fd_]}
    # ArmoryCfg load / reloadAll / useDefaults inline DEF_CFG (the default config text, + the Monk lines)
    plan15 = {"ArmoryCfg": ({"apply", "monkText", "load", "reloadAll", "useDefaults"}, None), "ArmoryDefs": ({"pids"}, {"MK_VAULT_MARK", "MK_VAULT_CODE", "MK_RISE_MARK", "MK_RISE_CODE"}),
              "ArmoryTrav": ({"added"}, set()), "GrappleFallSys": ({"handle"}, set()), "ArmoryHitSys": ({"handle"}, set()), "TravTick": ({"tick"}, set()),
              "SkyyArmoryPlugin": ({"setup", "shutdown", "unpublish", "publish"}, set())}
    bad15 = {}
    for c_, v_ in cmp15.items():
        if c_ in ("Monk", "MonkState", "ArmoryCmd", "ArmoryDbgCmd") and v_ == "only in 0.1.12":
            continue
        if c_.startswith("Cfg") and isinstance(v_, dict):          # the config kit (tools/skyycfg.py): its row tables carry the 34 + 2 new rows
            continue
        if c_ == "ArmoryHooks" and isinstance(v_, dict) and not v_["fields"]:          # the read-only row texts (fixed.bo.*, fixed.monk.*)
            continue
        if c_ in plan15 and isinstance(v_, dict) and set(v_["methods"]) <= plan15[c_][0] and (plan15[c_][1] is None or set(v_["fields"]) <= plan15[c_][1]):
            if c_ == "ArmoryCfg" and not all(f_.startswith("MK_") or f_ in ("MONK_TEXT", "DEF_CFG") for f_ in v_["fields"]):
                bad15[c_] = v_
            continue
        bad15[c_] = v_
    check(not bad15, "R15e: 0.1.11 -> 0.1.12 METHOD BY METHOD - only the planned methods / fields differ (ArmoryCfg apply + monkText + the MK_* rows, "
                     "ArmoryDefs pids + the 4 marker constants, ArmoryTrav.added, GrappleFallSys / ArmoryHitSys handle, TravTick.tick, the plugin "
                     "setup / shutdown / publish / unpublish, the kit's row tables, ArmoryHooks' row texts) + the 4 new classes: %s" % json.dumps(bad15)[:1500])
    print("R15e. vs 0.1.11: +17 files + 4 classes, 15 files changed; methods changed: %s" % json.dumps(cmp15)[:1200])
    print("R15. 0.1.12 Monk moves: validators, store, build, Java (vault, bounds, rise, plunge, refunds, refusals, flag, command, dispatch), old-jar compare - every path executed")
'''
hrep('''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''',
     R15 + '''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''')

out_t = ts.replace(LF, TNL)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(out_t)
print("wrote %s" % os.path.relpath(TDST, ROOT))
