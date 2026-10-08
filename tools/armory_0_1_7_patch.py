"""Derive SkyyArmory/build_skyyarmory_0.1.7.py (+ its harness SkyyArmory/test_skyyarmory_0.1.7.py) from the GENERATED 0.1.6
(SkyyArmory/build_skyyarmory_0.1.6.py = the tools/deploy_set.py SET pin, made by tools/armory_0_1_6_patch.py; test_skyyarmory_0.1.6.py =
its harness). Every anchor is asserted (rep = exactly one hit). Edit THIS file, never the generated scripts.
Run:  python tools/armory_0_1_7_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.7.py   then   python SkyyArmory/test_skyyarmory_0.1.7.py
      (never --deploy; deploy partner: SkyyGear 0.2.9 (the Monk weapons scale like the same-metal sword) - asserted once pinned)

0.1.7 = THE MONK WEAPONS AS ITEMS + RIGHT-CLICK BLOCK + NO VOID PROTECTION (Skyy 2026-10-07, docs/answered/gear.md + classes.md LOCKED lines:
"start building the bo staff and fist weapon items next" -> "Items now, moves later" + "Wraps + gauntlets only"; the FIST ATTACKS, STUNLOCK,
GAUNTLET speed, RIGHT-CLICK BLOCK default and NO VOID PROTECTION locks; research/cloud/Monk-Kit-Spec.md 1-2 is the contract):
  BO STAFFS Weapon_Bo_Copper ... _Onyxium (the vanilla Bamboo / Wood Bo staffs stay vanilla; no 'skyy' and NOT Weapon_Staff_: that prefix is
    the Mage's in SkyyClasses and a spell in SkyyGear). Item = the vanilla Weapon_Staff_Bo_Wood shape: Primary = the vanilla Staff_Primary root
    (tap = the vanilla Bo swing chain Spear_Swing_Left / _Right, hold = the vanilla staff cast - no charged move yet, Pole-Vault comes after the
    engine probes), its InteractionVars with the two swing damages set to BO_SHARE 0.82 x the same-metal vanilla sword's tap DPS x the 0.557 s
    swing (Monk-Kit-Spec 1.1), the metal's sword Quality / ItemLevel, the metal's SWORD recipe (VERIFIED: no vanilla spear has a recipe -
    Monk-Kit-Spec 8.2; Onyxium = the Mithril one with Onyxium bars), art = tools/art/make_staffs.py Bo models AT BUILD TIME.
  HAND WRAPS Weapon_Fist_Wraps_Linen / _Cotton / _Silk / _Cindercloth / _Shadoweave + GAUNTLETS Weapon_Fist_Gauntlets_Copper ... _Onyxium.
    Both hit ONE enemy (the vanilla Raycast selector - the Root / Stoneskin wands' player selector - returns the single best match: VERIFIED
    RaycastSelector$RuntimeSelector.selectTargetEntities). WRAPS (Skyy): each click throws several 0.1 s jabs, a power hit lands on jab N, no gap
    after it - Linen + Cotton 2 per click / power on 6, Silk 2 / 4, Cindercloth 3 / 6, Shadoweave 5 / 5; DPS = WRAP_SHARE 0.95 x the cloth
    column's sword. GAUNTLETS (Skyy): 1 jab per click, a chain of 4 with a 2x finisher, a jab every (sword 0.334 + dagger 0.207) / 2 = 0.27 s
    (both read from Assets.zip), a 0.7 s gap after the finisher (most mobs hit back), DPS = GAUNT_SHARE 0.9 x the sword. Animations = the
    vanilla unarmed punches (own set SkyyArmory_Fist: a copy of Default + faster jab copies), Weapon.RenderDualWielded, recipes: gauntlets = the
    metal's hands armor (Onyxium = Mithril's with Onyxium bars: the vanilla Onyxium hands recipe asks for Iron bars), wraps = the vanilla cloth
    hands' bolts + wood (its bench "TODO" exists nowhere) at the cloth column metal's hands bench (Shadoweave = Cindercloth's with Shadoweave
    bolts); art = tools/art/make_fists.py AT BUILD TIME (held R-Attachment models). No charged move yet (Rising Strike later).
  STUNLOCK BREAKOUT (Skyy: "the boss can hit you to break out of stunlock. if 2 people are spamming the boss the time doubles to 6 seconds"):
    Stun (ArmoryTuneSys, the Filter group): a Monk weapon's melee hit (Weapon_Fist_ / Weapon_Bo_ in hand) on a boss / mini-boss (stun.bossWords
    in the role name) starts or continues its count; a pause over stun.gap starts it again; after stun.perPlayer x (players hitting it, at
    most stun.maxPlayers) seconds the BREAKOUT WINDOW opens: combo hits on it do nothing for stun.window s, or until the boss hits a player.
  RIGHT-CLICK = BLOCK (Skyy): Secondary = the vanilla Root_Common_Guard_Entry_StaminaCondition (the vanilla guard: Common_Guard_Wield, a
    0-damage shove on left click) on every SkyyArmory wand, staff, spellbook, bo staff, wraps and gauntlets (not the crossbows: grapple; not
    the kunai: return). The vanilla Staff / Spellbook animation sets have no Guard pose: SkyyArmory_Staff / SkyyArmory_Spellbook = a copy of
    the vanilla Staff / Spellbook set + the Guard / GuardBash entries of Sword.json, generated at build time; SkyyArmory_Wand = the
    vanilla Wand set (Parent Sword, which already gives it Sword's Guard) naming the two entries itself, so no merge rule is relied on. The charged moves stay on the primary hold.
  NO VOID PROTECTION (Skyy: "dont put any void protection on any traversal"): the wand hop's / wand leap's / bow leap's half-hop without ground
    behind is gone (row hop.groundCheck removed), the kunai teleport + return no longer take a ground row (kunai.floorCheck removed: walls,
    inside-block, unloaded chunks, other worlds and locked arenas still stop it); blink.floorCheck keeps its row, default 0 since 0.1.4 (Skyy's
    file has no such line - no migration).
  SETTINGS: 6 new rows (Server Setup > Armory > Monk stunlock), 2 removed rows, 21 read-only rows (the Monk weapon numbers + the guard rule,
    client-predicted, fixed in the jar). No migration (no line to rewrite: removed keys are simply ignored if a file still holds them).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.6.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.7.py")
TSRC = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.6.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.7.py")

raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.6"\nMOD = "SkyyArmory"' in s and "0.1.6 = THE SPELLBOOKS + KUNAI ITEMS" in s, "build_skyyarmory_0.1.6.py is not the 0.1.6 pin"
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
rep('''"""SkyyArmory 0.1.6 - build script (javassist via jpype). GENERATED by tools/armory_0_1_6_patch.py from the GENERATED 0.1.5 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.6.py -> SkyyArmory/SkyyArmory-0.1.6.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.6.py (scratch tools/dev/scratch/armory016/).
''', '"""SkyyArmory 0.1.7 - build script (javassist via jpype). GENERATED by tools/armory_0_1_7_patch.py from the GENERATED 0.1.6 - edit the\n'
    'patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.7.py -> SkyyArmory/SkyyArmory-0.1.7.jar (never --deploy). Harness:\n'
    'python SkyyArmory/test_skyyarmory_0.1.7.py (scratch tools/dev/scratch/armory017/).\n\n'
    + open(__file__, encoding="utf8").read().split('"""')[1].split("\n", 3)[3].strip() + "\n\n"
    '0.1.6 (the base, everything below is still true unless 0.1.7 above says otherwise):\n')
rep('VERSION = "0.1.6"\nMOD = "SkyyArmory"', 'VERSION = "0.1.7"\nMOD = "SkyyArmory"')

# ================================================================================================ the 0.1.7 constants + the stunlock rows
ST_CONST = r'''
# ================================================================= 0.1.7 MONK WEAPONS + BLOCK + NO VOID (Skyy LOCKED 2026-10-07; research/cloud/Monk-Kit-Spec.md 1-2)
BO_SHARE = 0.82                  # Monk-Kit-Spec 1.1: Bo DPS = 0.82 x the same-metal sword (tap chains, vanilla timings)
GAUNT_SHARE = 0.90               # Monk-Kit-Spec 2.1: gauntlets 0.9 x the sword
WRAP_SHARE = 0.95                # Monk-Kit-Spec 2.1: wraps 0.95 x the sword of the cloth's metal column
GAUNT_FIN = 2.0                  # the 4th gauntlet jab = 2 x a jab (spec 3 / 3 / 3 / 6)
WRAP_POW = 5.0 / 3.0             # the wrap power hit = 5/3 x a jab (spec 3 / 3 / 3 / 5)
JAB_T = 0.1                      # one wrap jab (wind 0.04 + hit 0.02 + recover 0.04): 2 jabs = a dagger click (0.207 s), 5 = half a second
GAUNT_GAP = 0.7                  # s after the gauntlet finisher (Skyy: "slow enough most mobs can get a hit off")
FIST_REACH = 3                   # the Raycast selector's Distance (an int field, VERIFIED RaycastSelector.distance I); eye offset 1.6
GUARD_POSE = "Sword"             # the Guard / GuardBash entries our Staff / Spellbook sets take (task: Sword.json; "Battleaxe" = a 2-handed pose)
STUN_DEF_WORDS = "Boss,Guardian,Duke,Dragon,Chieftain,Elite,Hedera,Rex,Ogre,Golem,Yeti"     # grapple.bossWords' default + the mini-bosses it lacks
STUN_DEF_GAP = "0.8"             # fixer 2 (critic): 1 s left the gauntlet finisher pause (~1.01 s hit to hit) 8 ms over it - one server tick (33 ms)
                                 # could keep a gauntlet stunlock running; 0.8 sits > 2 ticks clear of both sides (asserted against the real timings)


def stun_boss_role(role, words):
    """fixer 2 (critic): the words match WHOLE parts of the role name split at '_' (Dragon_Fire yes, Snapdragon no) - Java Stun.bossRole"""
    r_ = "_" + role.strip().lower() + "_"
    return any(w_.strip() and ("_" + w_.strip().lower() + "_") in r_ for w_ in words.split(","))


# (fixer 2026-10-07, Skyy: "bosses and mini bosses" break out): Goblin_Ogre (124 HP = the Trork Chieftain's), the 6 Golem_Crystal_* / Golem_Firesteel
# (160-283 HP) and the Yeti (226 HP = Hedera's) match none of the grapple words - asserted below against Assets.zip; Skyy reviews the list
CFG_ST = [
    ('part.stun', 'Boss stunlock breakout', 'stun', 'bool', 'true', '', '', '', '', 'live,part,danger', 'Off = nonstop combo hits can stunlock a boss forever.', 'PART_STUN', 'boolean', 'true', 'Bosses + mini-bosses break out of a Monk combo stunlock and get a hit on you (Skyy 2026-10-07). Off = no breakout.'),
    ('stun.perPlayer', 'Breakout after (s per player)', 'stun', 'dec', '3', '0.5', '20', '', 's', 'live', 'Skyy: 3 s with 1 player, 6 s with 2 (x the players hitting it).', 'STUN_PER', 'double', '3', 'A boss under nonstop Monk combo hits breaks out after this many seconds x the players hitting it (Skyy: 1 player 3 s, 2 players 6 s).'),
    ('stun.maxPlayers', 'Most players counted', 'stun', 'int', '4', '1', '10', '', '', 'live', 'The cap (Skyy default): 4 players = 12 s at 3 s each.', 'STUN_MAX', 'int', '4', 'At most this many players count toward the breakout time (4 = 12 s at 3 s each).'),
    ('stun.gap', 'Pause that ends a stunlock (s)', 'stun', 'dec', STUN_DEF_GAP, '0.2', '5', '', 's', 'live', 'No Monk combo hit on it this long = the count starts over (the gauntlet finisher pause does).', 'STUN_GAP', 'double', STUN_DEF_GAP, 'No Monk combo hit on the boss for this many seconds = the stunlock count starts over (0.8: the gauntlet finisher pause resets it, nonstop wraps / bo taps do not).'),
    ('stun.window', 'Breakout window (s)', 'stun', 'dec', '1.5', '0.2', '5', '', 's', 'live', 'Combo hits on it do nothing this long, or until it hits a player.', 'STUN_WINDOW', 'double', '1.5', 'The breakout: Monk combo hits on that boss do nothing for this many seconds, or until it hits a player.'),
    ('stun.bossWords', 'Bosses + mini-bosses (role words)', 'stun', 'text', STUN_DEF_WORDS, '', '200', '', '', 'live', 'Whole parts of the role name: Dragon matches Dragon_Fire, not Snapdragon.', 'STUN_BOSS', 'String', STUN_DEF_WORDS, 'A mob whose role name has one of these comma-separated words as a whole part (split at _: Dragon matches Dragon_Fire, not Snapdragon) is a boss / mini-boss that breaks out of a stunlock.'),
]
'''
before('''# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)''', ST_CONST)
# the two void rows go (Skyy LOCKED 2026-10-07: no void protection on any traversal)
rep("""    ('kunai.floorCheck', 'Ground under the landing (blocks)', 'kunai', 'int', '0', '0', '64', '', 'blocks', 'live', '0 = off (no void protection, Skyy).', 'K_FLOOR', 'int', '0', 'A kunai teleport needs ground within this many blocks below the landing spot (0 = off: no void protection, Skyy 2026-10-07).'),
""", "")
rep(""" ('hop.groundCheck',
  'Hop needs ground within (blocks)',
  'hop',
  'int',
  '6',
  '0',
  '32',
  '',
  'blocks',
  'live',
  '0 = off. No ground behind you = half the hop.',
  'HOP_GROUND',
  'int',
  '6',
  'No ground within this many blocks under the spot 3 blocks behind you = half the hop (0 = off).'),
""", "")
rep("""+ CFG_GRAPPLE + CFG_LEAP + CFG_BK      # 0.1.2 grapple + 0.1.3 leap + 0.1.6 book / kunai rows""",
    """+ CFG_GRAPPLE + CFG_LEAP + CFG_BK + CFG_ST      # 0.1.2 grapple + 0.1.3 leap + 0.1.6 book / kunai + 0.1.7 stunlock rows""")

# ================================================================================================ the 0.1.7 assets (vanilla shapes first)
ST_ASSETS = r'''
# ================================================================= 0.1.7 ASSETS: MONK WEAPONS + RIGHT-CLICK BLOCK (Monk-Kit-Spec 1-2; Skyy LOCKED 2026-10-07) - vanilla shapes first
BO_METALS = list(NEW_METALS)
GAUNT_METALS = list(NEW_METALS)
WRAPS = [("Linen", "Copper", 2, 6), ("Cotton", "Iron", 2, 6), ("Silk", "Thorium", 2, 4), ("Cindercloth", "Cobalt", 3, 6),
         ("Shadoweave", "Adamantite", 5, 5)]           # (cloth, its metal column, jabs per click, the power hit on jab N) - Skyy's table
P_BOITEM = "Server/Item/Items/Weapon/Bo/Weapon_Bo_%s.json"
P_FITEM = "Server/Item/Items/Weapon/Fist/%s.json"
P_FINT = "Server/Item/Interactions/Weapons/Fist/SkyyArmory/%s.json"
P_FROOT = "Server/Item/RootInteractions/Weapons/Fist/SkyyArmory/%s.json"
P_ANIM = "Server/Item/Animations/SkyyArmory/%s.json"
MODEL_BO = "Items/Weapons/Staff/SkyyArmory_Bo_%s.blockymodel"
TEX_BO = "Items/Weapons/Staff/SkyyArmory_Bo_%s_Texture.png"
ICON_BO = "Icons/ItemsGenerated/SkyyArmory_Bo_%s.png"
MODEL_FIST = "Items/Weapons/Fist/SkyyArmory_%s_%s.blockymodel"           # (family, tier) - the make_fists.py paths
TEX_FIST = "Items/Weapons/Fist/SkyyArmory_%s_%s_Texture.png"
ICON_FIST = "Icons/ItemsGenerated/SkyyArmory_Fist_%s_%s.png"
GUARD_ROOT = "Root_Common_Guard_Entry_StaminaCondition"                  # the vanilla guard (Common_Guard_Wield) - no vanilla item uses it
ANIM_STAFF, ANIM_BOOK, ANIM_FIST, ANIM_WAND = "SkyyArmory_Staff", "SkyyArmory_Spellbook", "SkyyArmory_Fist", "SkyyArmory_Wand"
ID_FROOT, ID_FCHAIN, ID_FSTEP = "SkyyArmory_Fist_%s_Primary", "SkyyArmory_Fist_%s_Chain", "SkyyArmory_Fist_%s_Step%d"
BO_IDS = ["Weapon_Bo_" + m for m in BO_METALS]
GAUNT_IDS = ["Weapon_Fist_Gauntlets_" + m for m in GAUNT_METALS]
WRAP_IDS = ["Weapon_Fist_Wraps_" + c for c, _col, _k, _p in WRAPS]
MONK_IDS = BO_IDS + GAUNT_IDS + WRAP_IDS
STUN_PRE = ["Weapon_Fist_", "Weapon_Bo_"]           # the Monk combo weapons the stunlock count reads (Java ArmoryDefs.STUN_PRE)
# fixer: the mini-bosses the grapple words miss are real vanilla roles the stunlock words now catch (and no plain mob of ours by accident)
_stroles = set(os.path.basename(n)[:-5] for n in AZ_NAMES if n.startswith("Server/NPC/Roles/") and n.endswith(".json"))
for _r in ("Goblin_Ogre", "Golem_Firesteel", "Golem_Crystal_Earth", "Golem_Crystal_Flame", "Golem_Crystal_Frost", "Golem_Crystal_Sand",
           "Golem_Crystal_Thunder", "Yeti", "Trork_Chieftain", "Hedera", "Rex_Cave", "Dragon_Fire", "Golem_Guardian_Void"):
    assert _r in _stroles and any(_w.lower() in _r.lower() for _w in STUN_DEF_WORDS.split(",")), "stun.bossWords: role %s" % _r
for _r in ("Skeleton_Fighter", "Trork_Warrior", "Goblin_Scrapper", "Trork_Shaman", "Snapdragon"):
    assert _r in _stroles and not stun_boss_role(_r, STUN_DEF_WORDS), "stun.bossWords catches the plain mob %s" % _r
# fixer 2: the whole-part match (Java Stun.bossRole) still catches all 13 bosses / mini-bosses above
for _r in ("Goblin_Ogre", "Golem_Firesteel", "Golem_Crystal_Earth", "Golem_Crystal_Flame", "Golem_Crystal_Frost", "Golem_Crystal_Sand",
           "Golem_Crystal_Thunder", "Yeti", "Trork_Chieftain", "Hedera", "Rex_Cave", "Dragon_Fire", "Golem_Guardian_Void"):
    assert stun_boss_role(_r, STUN_DEF_WORDS), "stun.bossWords (whole parts) misses %s" % _r
for _i in MONK_IDS:
    assert "skyy" not in _i.lower() and not _i.startswith(("Weapon_Staff_", "Weapon_Claws_")), _i      # SkyyGear skyyItem / spell / exclude rules
    assert not az_has("item", _i), "Hytale now has %s - SkyyArmory would override it; Skyy decides first" % _i
    assert _i.startswith(tuple(STUN_PRE)), _i


def r1(x):
    """round half up to 0.1 (damage can be a float: DamageCalculator.baseDamageRaw is an Object2FloatMap - VERIFIED)"""
    return math.floor(x * 10.0 + 0.5 + 1e-9) / 10.0


def anim_chain(aid):
    """an animation set with its Parent chain merged the engine way (the Wand set = Parent Sword + 3 own entries proves the merge)"""
    d = az_get("anim", aid)
    out = dict(d.get("Animations") or {})
    p, seen = d.get("Parent"), set([aid])
    while p:
        assert p not in seen, p
        seen.add(p)
        pd = az_get("anim", p)
        for k_, v_ in (pd.get("Animations") or {}).items():
            out.setdefault(k_, v_)
        p = pd.get("Parent")
    return out


# ---- the vanilla shapes this block copies (the build stops if Hytale changes them)
VBO = az_get("item", "Weapon_Staff_Bo_Wood")
assert VBO["Interactions"] == {"Primary": "Staff_Primary", "Secondary": "Staff_Primary"} and VBO["PlayerAnimationsId"] == "Staff" and VBO["Weapon"] == {} \
    and sorted(VBO["InteractionVars"]) == sorted(STAFF_VARS) and VBO["Model"] == "Items/Weapons/Staff/Bo_Wood.blockymodel", "the vanilla Wood Bo staff changed"
assert VBO["InteractionVars"]["Spear_Swing_Left_Damage"] == "Spear_Swing_Left_Damage" and VBO["InteractionVars"]["Spear_Swing_Right_Damage"] == "Spear_Swing_Right_Damage"
assert az_get("root", "Staff_Primary") == {"Interactions": ["Staff_Primary"]}, "the vanilla Staff_Primary root changed"
VBO_HIT = [float(resolve("int", v)["DamageCalculator"]["BaseDamage"]["Physical"]) for v in ("Spear_Swing_Left_Damage", "Spear_Swing_Right_Damage")]
assert VBO_HIT == [5.0, 5.0] and set(resolve("int", "Spear_Swing_Left_Damage")["DamageCalculator"]) == {"BaseDamage"}, VBO_HIT
VBO_TAP = [dur("Spear_Swing_Left", VBO["InteractionVars"]), dur("Spear_Swing_Right", VBO["InteractionVars"])]
assert VBO_TAP == [VAN_TAP_S, VAN_TAP_S], VBO_TAP
# Monk-Kit-Spec 8.3 (VERIFIED): the vanilla Bo staffs' hold = the vanilla staff cast (Staff_Cast_Summon_Charged, 50 Mana in their vars) - no traversal
assert VBO["InteractionVars"]["Staff_Cast_Summon_Charged"]["Interactions"][0]["Costs"] == {"Mana": 50}
assert az_get("item", "Weapon_Staff_Bo_Bamboo")["Interactions"] == VBO["Interactions"]
VGUARD = az_get("root", GUARD_ROOT)
assert VGUARD["RequireNewClick"] is True and VGUARD["Rules"] == {"Interrupting": ["Primary"]} \
    and VGUARD["Interactions"][0]["DefaultValue"] == {"Interactions": ["Common_Guard_Entry_StaminaCondition"]}, VGUARD
_gw = az_get("int", "Common_Guard_Wield")
assert _gw["Type"] == "Wielding" and _gw["Effects"]["ItemAnimationId"] == "Guard" and az_get("int", "Common_Guard_Shove_Animation")["Effects"] == {"ItemAnimationId": "GuardBash"}
assert json.dumps(az_get("int", "Common_Guard_Entry_StaminaCondition")).count("Common_Guard_Wield") == 1
_users = [n for n in AZ_NAMES if n.startswith("Server/Item/Items/") and n.endswith(".json") and GUARD_ROOT.encode() in AZ.read(n)]
assert not _users, "a vanilla item uses %s now: %s" % (GUARD_ROOT, _users)
# the animation sets: Staff / Spellbook (+ Item) have NO Guard pose, the Wand set inherits Sword's (Parent), Default (unarmed) has punches + Guard
_pose = anim_chain(GUARD_POSE)
assert "Guard" in _pose and "GuardBash" in _pose and not az_get("anim", GUARD_POSE).get("Parent"), sorted(_pose)
assert "Guard" not in anim_chain("Staff") and "Guard" not in anim_chain("Spellbook"), "vanilla gave the Staff / Spellbook set a Guard pose - drop ours"
assert az_get("anim", "Wand").get("Parent") == "Sword" and "Guard" in anim_chain("Wand") and "Guard" not in (az_get("anim", "Wand").get("Animations") or {})
_unarmed = anim_chain("Default")
assert all(a in _unarmed for a in ("SwingLeft", "SwingRight", "SwingUpLeft", "Guard")) and not az_get("anim", "Default").get("Parent"), sorted(_unarmed)
for _a in (ANIM_STAFF, ANIM_BOOK, ANIM_FIST, ANIM_WAND):
    assert not az_has("anim", _a), _a
VUL = az_get("int", "Unarmed_Swing_Left")
VUU = az_get("int", "Unarmed_Swing_Up_Left")
_vul_hit = VUL["Next"]["Interactions"][0]["Interactions"][0]["HitEntity"]["Interactions"][0]
_vuu_hit = VUU["Next"]["Interactions"][0]["Interactions"][0]["HitEntity"]["Interactions"][0]
assert _vul_hit["Type"] == "DamageEntity" and _vul_hit["DamageCalculator"] == {"BaseDamage": {"Physical": 1}} and _vuu_hit["Type"] == "DamageEntity" \
    and "Knockback" in _vuu_hit["DamageEffects"] and "Knockback" not in _vul_hit["DamageEffects"], (_vul_hit, _vuu_hit)
assert VUL["Effects"]["WorldSoundEventId"] == "SFX_Unarmed_Swing" and az_has("sound", "SFX_Player_Unarmed_Swing_Left") and az_has("sound", "SFX_Player_Unarmed_Swing_Right")
for _sel in ("Root_Cast", "Stoneskin_Cast"):          # the vanilla player items that already pick with the Raycast selector (one target)
    assert '"Raycast"' in json.dumps(az_get("int", _sel)), _sel
VDG = item_resolved("Weapon_Daggers_Iron")
assert VDG["Weapon"].get("RenderDualWielded") is True and VDG["Reticle"] == "DefaultMelee", "the dagger template changed"

# ---- the cadence + DPS references (read here, never typed in): the vanilla sword's tap chain and the daggers' (VERIFIED 0.334 / 0.75 / 0.207)
_swc = resolve("int", "Weapon_Sword_Primary_Chain")
_dgc = resolve("int", "Weapon_Daggers_Primary_Chain")
SWORD = {}
for _m in ["Crude"] + list(NEW_METALS):
    _iv = item_resolved("Weapon_Sword_" + _m).get("InteractionVars") or {}
    _d = [float(_iv[k_]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Physical"]) for k_ in ("Swing_Left_Damage", "Swing_Right_Damage", "Swing_Down_Damage")]
    _t = [dur(x_, _iv) for x_ in _swc["Next"]]
    SWORD[_m] = dict(hits=_d, t=_t, dps=sum(_d) / sum(_t))
SWORD_T = (SWORD["Iron"]["t"][0] + SWORD["Iron"]["t"][1]) / 2.0
DAGGER_T = sum(dur(x_, item_resolved("Weapon_Daggers_Iron").get("InteractionVars") or {}) for x_ in _dgc["Next"]) / float(len(_dgc["Next"]))
GAUNT_T = round((SWORD_T + DAGGER_T) / 2.0, 2)
assert abs(SWORD_T - 0.334) < 1e-9 and abs(DAGGER_T - 0.207) < 1e-9 and DAGGER_T < GAUNT_T < SWORD_T, (SWORD_T, DAGGER_T, GAUNT_T)
assert [SWORD[m]["hits"] for m in ("Copper", "Adamantite")] == [[8.0, 8.0, 14.0], [14.0, 14.0, 28.0]], "the vanilla sword numbers changed"
GAUNT_FIN_T = 0.4 + GAUNT_GAP                    # finisher: wind 0.17 + hit 0.03 + recover 0.2, then the gap
GAUNT_CYCLE = 3.0 * GAUNT_T + GAUNT_FIN_T
# fixer 2 (critic): stun.gap must sit > 2 server ticks (30 TPS) clear of both sides: the slowest nonstop combo hit-to-hit (a bo tap, a gauntlet
# jab, a wrap step) keeps the count running, the gauntlet finisher pause (its recover + the next jab's wind-up) resets it
_TICK2 = 2.0 / 30.0
_FIN_GAP = round(0.2 + GAUNT_GAP, 3) + round(GAUNT_T * 0.4, 3)
assert max(VAN_TAP_S, GAUNT_T, 5 * JAB_T) + _TICK2 < float(STUN_DEF_GAP) < _FIN_GAP - _TICK2, ("stun.gap", STUN_DEF_GAP, VAN_TAP_S, GAUNT_T, _FIN_GAP)
BO = {}
for _m in BO_METALS:
    _h = r1(BO_SHARE * SWORD[_m]["dps"] * VAN_TAP_S)
    BO[_m] = dict(hit=_h, share=_h / VAN_TAP_S / SWORD[_m]["dps"])
GAUNT = {}
for _m in GAUNT_METALS:
    _u = GAUNT_SHARE * SWORD[_m]["dps"] * GAUNT_CYCLE / (3.0 + GAUNT_FIN)
    _j, _f = r1(_u), r1(_u * GAUNT_FIN)
    GAUNT[_m] = dict(jab=_j, fin=_f, share=(3.0 * _j + _f) / GAUNT_CYCLE / SWORD[_m]["dps"])
WRAP = {}
for _c, _col, _k, _p in WRAPS:
    _cyc = _p * JAB_T
    _u = WRAP_SHARE * SWORD[_col]["dps"] * _cyc / (_p - 1 + WRAP_POW)
    _j, _w = r1(_u), r1(_u * WRAP_POW)
    WRAP[_c] = dict(col=_col, k=_k, p=_p, jab=_j, pow=_w, cycle=_cyc, share=((_p - 1) * _j + _w) / _cyc / SWORD[_col]["dps"])
for _n, _t in (("bo", BO), ("gauntlets", GAUNT), ("wraps", WRAP)):
    for _x, _v in _t.items():
        assert abs(_v["share"] - {"bo": BO_SHARE, "gauntlets": GAUNT_SHARE, "wraps": WRAP_SHARE}[_n]) < 0.03, (_n, _x, _v)   # the 0.1 rounding only
assert all(GAUNT[m]["jab"] > WRAP[c]["jab"] for c, m, _k, _p in WRAPS), "Skyy: gauntlets hit harder per hit than the wraps of the same band"

# ---- recipes (Monk-Kit-Spec 8.2 VERIFIED: no vanilla spear recipe; hands armor recipes exist; vanilla cloth hands sit on bench "TODO")


def rec_copy(iid):
    r = item_resolved(iid).get("Recipe")
    assert isinstance(r, dict) and set(r) <= set(RECIPE_KEYS), (iid, r)
    out = json.loads(json.dumps(r))
    if "BenchRequirement" in out:
        out["BenchRequirement"] = [b for b in out["BenchRequirement"] if b.get("Id") not in DROP_BENCH2]
    return out


def bars_to(r, src, dst):
    n = 0
    for x in r["Input"]:
        if x.get("ItemId") == "Ingredient_Bar_" + src:
            x["ItemId"] = "Ingredient_Bar_" + dst
            n += 1
    assert n == 1, (src, r)
    return r


for _m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"):
    assert item_resolved("Weapon_Spear_" + _m).get("Recipe") is None, "vanilla gave the %s spear a recipe - Monk-Kit-Spec 1 prefers it" % _m
assert item_resolved("Weapon_Sword_Onyxium").get("Recipe") is None and "Ingredient_Bar_Iron" in json.dumps(item_resolved("Armor_Onyxium_Hands")["Recipe"])
BO_RECIPES = dict((m, rec_copy("Weapon_Sword_" + m)) for m in BO_METALS if m != "Onyxium")
BO_RECIPES["Onyxium"] = bars_to(rec_copy("Weapon_Sword_Mithril"), "Mithril", "Onyxium")
GAUNT_RECIPES = dict((m, rec_copy("Armor_%s_Hands" % m)) for m in GAUNT_METALS if m != "Onyxium")
GAUNT_RECIPES["Onyxium"] = bars_to(rec_copy("Armor_Mithril_Hands"), "Mithril", "Onyxium")
WRAP_RECIPES = {}
for _c, _col, _k, _p in WRAPS:
    _src = rec_copy("Armor_Cloth_%s_Hands" % (_c if _c != "Shadoweave" else "Cindercloth"))
    assert [b.get("Id") for b in _src["BenchRequirement"]] == ["TODO"], "a vanilla cloth hands bench exists now - use it: %s" % _src["BenchRequirement"]
    _in = [x for x in _src["Input"] if not str(x.get("ItemId", "")).startswith("Ingredient_Bar_")]
    if _c == "Shadoweave":
        _sw = [x for x in _in if x.get("ItemId") == "Ingredient_Bolt_Cindercloth"]
        assert len(_sw) == 1, _in
        _sw[0]["ItemId"] = "Ingredient_Bolt_Shadoweave"
    assert [x for x in _in if x.get("ItemId") == "Ingredient_Bolt_" + _c], (_c, _in)
    _bench = rec_copy("Armor_%s_Hands" % _col)["BenchRequirement"]
    WRAP_RECIPES[_c] = {"TimeSeconds": _src["TimeSeconds"], "KnowledgeRequired": False, "Input": _in, "BenchRequirement": _bench}
for _r in list(BO_RECIPES.values()) + list(GAUNT_RECIPES.values()) + list(WRAP_RECIPES.values()):
    assert any(b.get("Type") == "Crafting" and b.get("Id") in ("Weapon_Bench", "Armor_Bench") for b in _r["BenchRequirement"]), _r
    for _x in _r["Input"]:
        assert ("ItemId" in _x) != ("ResourceTypeId" in _x) and int(_x["Quantity"]) > 0, _x
        assert (_x.get("ItemId") is None or az_has("item", _x["ItemId"])) and (_x.get("ResourceTypeId") is None or az_has("rtype", _x["ResourceTypeId"])), _x
for _i in MONK_IDS:
    assert _i + "_Recipe_Generated_0" not in _vrecipe_ids and _i not in _salvage_in, _i

# ---- the animation sets (generated here from Assets.zip, never committed): a COPY of the vanilla set (its own Parent kept, the SkyyGear 0.2.6
# speed-set pattern) + the entries it lacks: Staff / Spellbook + Sword's Guard + GuardBash; Default (unarmed) + faster punch copies for the jabs
ANIMS = {}
for _a, _src in ((ANIM_STAFF, "Staff"), (ANIM_BOOK, "Spellbook"), (ANIM_FIST, "Default"), (ANIM_WAND, "Wand")):
    _c = json.loads(json.dumps(az_get("anim", _src)))
    _c.setdefault("Animations", {})
    ANIMS[_a] = _c
for _a in (ANIM_STAFF, ANIM_BOOK, ANIM_WAND):          # the Wand set inherits Sword's through its Parent - ours names them itself
    for _k in ("Guard", "GuardBash"):
        assert _k not in ANIMS[_a]["Animations"], (_a, _k)
        ANIMS[_a]["Animations"][_k] = json.loads(json.dumps(_pose[_k]))
for _new, _src, _x in (("JabLeft", "SwingLeft", 3.0), ("JabRight", "SwingRight", 3.0), ("PowerUp", "SwingUpLeft", 2.0)):
    assert _new not in _unarmed, _new
    _e = json.loads(json.dumps(_unarmed[_src]))
    _e["Speed"] = round(float(_e.get("Speed", 1.0)) * _x, 4)          # the vanilla punch played faster (the 0.1 s wrap jab)
    ANIMS[ANIM_FIST]["Animations"][_new] = _e
assert ANIMS[ANIM_BOOK].get("Parent") == "Item" and ANIMS[ANIM_WAND].get("Parent") == "Sword" and not ANIMS[ANIM_STAFF].get("Parent") \
    and not ANIMS[ANIM_FIST].get("Parent")
for _a, _d in ANIMS.items():
    put(P_ANIM % _a, _d)
ANIM_FILES = [P_ANIM % a for a in sorted(ANIMS)]

# ---- the fist chains: one Raycast pick per jab (ONE enemy), the vanilla unarmed hit shapes, our numbers. Every part is its own interaction
# asset named by id (no inline children): wind (the punch animation) -> the pick -> the recover pad; the hit = a DamageEntity asset
MK_INTS, MK_ROOTS = [], []
ID_FPART = "SkyyArmory_Fist_%s_%s"          # (item key, part)


def add_mk(iid, obj):
    add_int(P_FINT, iid, obj)
    MK_INTS.append(iid)


def hit_obj(dmg, power):
    h = json.loads(json.dumps(_vuu_hit if power else _vul_hit))
    h["DamageCalculator"] = {"BaseDamage": {"Physical": dmg}}
    return h


def fist_parts(key, wind, hit_t, rec_t, fin, anims, dmg, pdmg):
    """the shared parts of one fist weapon: JabL / JabR / Pow (wind + animation) -> SelJ / SelP (the Raycast pick) -> Pad / PadP; Hit / PowHit"""
    P = lambda part: ID_FPART % (key, part)
    add_mk(P("Hit"), hit_obj(dmg, False))
    add_mk(P("PowHit"), hit_obj(pdmg, True))
    add_mk(P("Pad"), {"Type": "Simple", "RunTime": rec_t})
    add_mk(P("PadP"), {"Type": "Simple", "RunTime": fin[2]})
    for sel, h, pad in (("SelJ", "Hit", "Pad"), ("SelP", "PowHit", "PadP")):
        add_mk(P(sel), {"Type": "Selector", "RunTime": hit_t if sel == "SelJ" else fin[1], "Selector": {"Id": "Raycast", "Offset": {"Y": 1.6}, "Distance": FIST_REACH},
                        "HitEntity": {"Interactions": [P(h)]}, "Next": P(pad)})
    for part, anim, sound, w_, sel in (("JabL", anims[0], "SFX_Player_Unarmed_Swing_Left", wind, "SelJ"), ("JabR", anims[1], "SFX_Player_Unarmed_Swing_Right", wind, "SelJ"),
                                       ("Pow", anims[2], "SFX_Player_Unarmed_Swing_Left", fin[0], "SelP")):
        add_mk(P(part), {"Type": "Simple", "RunTime": w_, "Effects": {"ItemAnimationId": anim, "WorldSoundEventId": "SFX_Unarmed_Swing", "LocalSoundEventId": sound},
                         "Next": P(sel)})
    return P


def fist_root(key, steps, cooldown):
    add_mk(ID_FCHAIN % key, {"Type": "Chaining", "ChainingAllowance": 1.0, "Next": steps})
    rid = ID_FROOT % key
    obj = {"RequireNewClick": True, "ClickQueuingTimeout": 0.2, "Cooldown": {"Cooldown": cooldown}, "Interactions": [ID_FCHAIN % key],
           "Tags": {"Attack": ["Melee"]}}
    assert rid not in ROOTS and not az_has("root", rid), rid
    ROOTS[rid] = obj
    put(P_FROOT % rid, obj)
    MK_ROOTS.append(rid)
    return rid


FIST_ROOT = {}
for _m in GAUNT_METALS:
    _g = GAUNT[_m]
    _jw, _jh = round(GAUNT_T * 0.4, 3), 0.03
    _P = fist_parts("Gauntlets_" + _m, _jw, _jh, round(GAUNT_T - _jw - _jh, 3), (0.17, 0.03, round(0.2 + GAUNT_GAP, 3)),
                    ("SwingLeft", "SwingRight", "SwingUpLeft"), _g["jab"], _g["fin"])
    FIST_ROOT["Weapon_Fist_Gauntlets_" + _m] = fist_root("Gauntlets_" + _m, [_P("JabL"), _P("JabR"), _P("JabL"), _P("Pow")], round(GAUNT_T * 0.75, 3))
for _c, _col, _k, _p in WRAPS:
    _w = WRAP[_c]
    _P = fist_parts("Wraps_" + _c, 0.04, 0.02, 0.04, (0.04, 0.02, 0.04), ("JabLeft", "JabRight", "PowerUp"), _w["jab"], _w["pow"])
    _steps, _cur, _n, _si = [], [], 0, 0
    while _n < _p:
        _n += 1
        _cur.append(_P("Pow") if _n == _p else _P("JabL" if _n % 2 else "JabR"))
        if len(_cur) == _k or _n == _p:
            _si += 1
            add_mk(ID_FSTEP % ("Wraps_" + _c, _si), {"Type": "Serial", "Interactions": _cur})
            _steps.append(ID_FSTEP % ("Wraps_" + _c, _si))
            _cur = []
    FIST_ROOT["Weapon_Fist_Wraps_" + _c] = fist_root("Wraps_" + _c, _steps, round(_k * JAB_T * 0.75, 3))

# ---- THE ART, generated at build time (Skyy 2026-10-07 "Match the wands"): tools/art/make_staffs.py (Bo) + make_fists.py functions in the
# order of their main(); the vanilla-derived bytes exist only in the jar. When the git-ignored review copy exists it must equal the jar bytes.
import make_fists as MF
assert tuple(MF.METALS) == tuple(GAUNT_METALS) and tuple((c, col) for c, col in MF.CLOTHS) == tuple((c, col) for c, col, _k, _p in WRAPS), (MF.METALS, MF.CLOTHS)
_bod, _bom, _bot, _boi = SA.item_parts(AZ, MS.BO_ITEM)
assert _bod["IconProperties"] == VBO["IconProperties"] and MS.BO_ITEM.endswith("/Weapon_Staff_Bo_Wood.json")
_bovan = json.loads(_bom.decode("utf-8-sig"))
BO_ART, MK_REVIEW = {}, {}


def review(sub, rels, data, key):
    _rv = os.path.join(ROOT, "models-local", "art", sub)
    _rf = [os.path.join(_rv, *r_.split("/")) for r_ in rels]
    if all(os.path.isfile(p) for p in _rf):
        assert [open(p, "rb").read() for p in _rf] == data, \
            "%s: the built art differs from the reviewed copy in models-local/art/%s (re-run the tools/art script and let Skyy look again)" % (key, sub)
        MK_REVIEW[key] = "= reviewed copy"
    else:
        MK_REVIEW[key] = "no review copy here"


for _m in BO_METALS:
    _bmd = MS.bo_model(_bovan, _m)
    _bpl, _bht = MS.pack(_bmd)
    _btx = MS.bo_texture(AZ, _m, _bmd, _bpl, _bht, MS.tier_colours(AZ, _m))
    _bic = SA.render_icon(_bmd, _btx, VBO["IconProperties"], 64)
    _bmj = (json.dumps(_bmd, indent=2) + "\n").encode("utf-8")
    _tw, _th = SA.png_size(_btx)
    assert _tw % 32 == 0 and _th % 32 == 0 and SA.png_size(_bic) == (64, 64), (_m, _tw, _th)
    for _rn in RIG_NODES:
        _a, _b = MS.find(_bmd["nodes"], _rn), MS.find(_bovan["nodes"], _rn)
        assert _a is not None and _b is not None and _a.get("position") == _b.get("position") and _a.get("orientation") == _b.get("orientation"), (_m, _rn)
    BO_ART[_m] = (_bmj, _btx, _bic)
    ASSETS["Common/" + MODEL_BO % _m] = _bmj
    ASSETS["Common/" + TEX_BO % _m] = _btx
    ASSETS["Common/" + ICON_BO % _m] = _bic
    review("staffs", ["Common/" + MODEL_BO % _m, "Common/" + TEX_BO % _m, "Common/" + ICON_BO % _m], [_bmj, _btx, _bic], "Bo " + _m)
FIST_ART, FIST_PROPS = {}, {}
_fams = []
_gl = []
for _m in GAUNT_METALS:
    _metal, _gold = MF.wand_metal(AZ, _m)
    _pal = {"metal": _metal, "gold": _gold, "gem": SA.gem_gradient(AZ, _m), "gold_trim": _m in MF.GOLD_TIERS,
            "rivets": _m not in ("Copper",), "vplate": _m == "Cobalt"}
    _gl.append(("Gauntlets", _m, MF.build_gauntlets(_m), _pal))
_wl = []
for _c, _col, _k, _p in WRAPS:
    _wl.append(("Wraps", _c, MF.build_wraps(_c), {"cloth": MF.cloth_gradient(AZ, _c), "stitched": _c in MF.STITCHED}))
for _fam in (_gl, _wl):
    _models = [it_[2].model() for it_ in _fam]
    _hts = [MF.pack(md_) for md_ in _models]
    _rot = MF.FAMILY_ROT.get(_fam[0][0], MF.ICON_ROT)
    _props = MF.fit_props(_models, _rot)
    for (_family, _tier, _b, _pal), _md, _ht in zip(_fam, _models, _hts):
        _seed = sum(ord(ch_) for ch_ in "SkyyArmory_Fist_%s_%s" % (_family, _tier))
        _tx = SA.png_encode(MF.Tex(_md, _ht, _b.kind, _pal, _seed, _rot).img)
        _ic = SA.render_icon(_md, _tx, _props, 64)
        _mj = (json.dumps(_md, indent=2) + "\n").encode("utf-8")
        assert _md["nodes"][0]["name"] == "R-Attachment" and _md["nodes"][0]["shape"]["settings"].get("isPiece") is True, (_family, _tier)
        assert SA.png_size(_tx)[0] % 32 == 0 and SA.png_size(_tx)[1] % 32 == 0 and SA.png_size(_ic) == (64, 64), (_family, _tier)
        _iid = "Weapon_Fist_%s_%s" % (_family, _tier)
        FIST_ART[_iid] = (_mj, _tx, _ic)
        FIST_PROPS[_iid] = _props
        _rels = ["Common/" + p_ % (_family, _tier) for p_ in (MODEL_FIST, TEX_FIST, ICON_FIST)]
        for _rl, _dt in zip(_rels, (_mj, _tx, _ic)):
            ASSETS[_rl] = _dt
        review("fists", _rels, [_mj, _tx, _ic], _iid)

# ---- the items
MK_ITEMS = []
for _m in BO_METALS:
    _sw = resolve("item", "Weapon_Sword_" + _m)
    _iv = json.loads(json.dumps(VBO["InteractionVars"]))
    for _side in ("Left", "Right"):
        _iv["Spear_Swing_%s_Damage" % _side] = {"Interactions": [{"Parent": "Spear_Swing_%s_Damage" % _side,
                                                                    "DamageCalculator": {"BaseDamage": {"Physical": BO[_m]["hit"]}}}]}
    _it = {"TranslationProperties": {"Name": "server.items.Weapon_Bo_%s.name" % _m}, "Categories": list(VBO["Categories"]),
           "Quality": _sw["Quality"], "ItemLevel": _sw["ItemLevel"], "Model": MODEL_BO % _m, "Texture": TEX_BO % _m, "PlayerAnimationsId": ANIM_STAFF,
           "Interactions": {"Primary": "Staff_Primary", "Secondary": GUARD_ROOT}, "InteractionVars": _iv,
           "IconProperties": json.loads(json.dumps(VBO["IconProperties"])), "Icon": ICON_BO % _m, "DroppedItemAnimation": VBO["DroppedItemAnimation"],
           "Tags": json.loads(json.dumps(VBO["Tags"])), "Weapon": {}, "ItemSoundSetId": VBO["ItemSoundSetId"], "Recipe": BO_RECIPES[_m]}
    ITEMS["Weapon_Bo_" + _m] = _it
    put(P_BOITEM % _m, _it)
    MK_ITEMS.append("Weapon_Bo_" + _m)
for _iid in GAUNT_IDS + WRAP_IDS:
    _fam, _tier = _iid.split("_")[2], _iid.split("_")[3]
    _col = _tier if _fam == "Gauntlets" else WRAP[_tier]["col"]
    _sw = resolve("item", "Weapon_Sword_" + _col)
    _it = {"TranslationProperties": {"Name": "server.items.%s.name" % _iid}, "Categories": ["Items.Weapons"], "Quality": _sw["Quality"],
           # wraps: the band start of the cloth's metal column (SkyyGear reads the cloth word; Shadoweave has no row - this level is its fallback)
           "ItemLevel": _sw["ItemLevel"] if _fam == "Gauntlets" else BANDS[_col][0],
           "Model": MODEL_FIST % (_fam, _tier), "Texture": TEX_FIST % (_fam, _tier), "Icon": ICON_FIST % (_fam, _tier),
           "IconProperties": json.loads(json.dumps(FIST_PROPS[_iid])), "PlayerAnimationsId": ANIM_FIST, "Reticle": VDG["Reticle"],
           "Interactions": {"Primary": FIST_ROOT[_iid], "Secondary": GUARD_ROOT}, "DroppedItemAnimation": VDG["DroppedItemAnimation"],
           "Tags": {"Type": ["Weapon"], "Family": ["Fist"]}, "Weapon": {"RenderDualWielded": True},
           "ItemSoundSetId": "ISS_Weapons_Blunt_Small" if _fam == "Gauntlets" else "ISS_Armor_Cloth",
           "Recipe": GAUNT_RECIPES[_tier] if _fam == "Gauntlets" else WRAP_RECIPES[_tier]}
    assert "MaxStack" not in _it and "InteractionVars" not in _it
    ITEMS[_iid] = _it
    put(P_FITEM % _iid, _it)
    MK_ITEMS.append(_iid)
assert MK_ITEMS == MONK_IDS and len(MK_ITEMS) == 19

# ---- RIGHT-CLICK = BLOCK on every SkyyArmory wand / staff / spellbook (Skyy LOCKED 2026-10-07); crossbows keep the grapple, kunai the return
GUARDED = []
for _i, _p in ([("Weapon_Wand_" + m, P_WITEM % m) for m in NEW_METALS] + [("Weapon_Staff_" + m, P_SITEM % m) for m in METALS]
               + [("Weapon_Spellbook_" + m, P_BITEM % m) for m in BOOK_METALS]):
    _it = ITEMS[_i]
    assert _it["Interactions"]["Secondary"] == _it["Interactions"]["Primary"] and ASSETS[_p] == jdump(_it), (_i, _it["Interactions"])
    _it["Interactions"]["Secondary"] = GUARD_ROOT
    if _i.startswith("Weapon_Staff_"):
        assert _it["PlayerAnimationsId"] == "Staff", _i
        _it["PlayerAnimationsId"] = ANIM_STAFF
    elif _i.startswith("Weapon_Spellbook_"):
        assert _it["PlayerAnimationsId"] == "Spellbook", _i
        _it["PlayerAnimationsId"] = ANIM_BOOK
    else:
        assert _it["PlayerAnimationsId"] == "Wand", _i
        _it["PlayerAnimationsId"] = ANIM_WAND          # the Wand set inherits Sword's Guard (Parent Sword); ours names it itself
    ASSETS[_p] = jdump(_it)
    GUARDED.append(_i)
assert len(GUARDED) == 22
for _x in XBOW_IDS:
    assert ITEMS[_x].get("Interactions", {}).get("Secondary") != GUARD_ROOT, _x
for _m in KUNAI_METALS:
    assert ITEMS["Weapon_Kunai_" + _m]["Interactions"]["Secondary"] == ID_KRROOT % _m, _m
ALL_GUARDED = GUARDED + MONK_IDS
for _i in ALL_GUARDED:
    _pa = ITEMS[_i]["PlayerAnimationsId"]
    _ch = anim_chain(_pa) if az_has("anim", _pa) else dict(list(ANIMS[_pa]["Animations"].items()) + (
        list(anim_chain(ANIMS[_pa]["Parent"]).items()) if ANIMS[_pa].get("Parent") else []))
    assert "Guard" in _ch, "%s: its animation set %s has no Guard pose" % (_i, _pa)

# ---- language (names + descriptions through the default key; the numbers are the build's)
MKLANG = []
for _m in BO_METALS:
    MKLANG.append("items.Weapon_Bo_%s.name = %s Bo Staff" % (_m, _m))
    MKLANG.append("items.Weapon_Bo_%s.description = Tap: staff swings, %s damage each. Hold: the staff cast. Right click: block." % (_m, bnum(BO[_m]["hit"])))
for _m in GAUNT_METALS:
    MKLANG.append("items.Weapon_Fist_Gauntlets_%s.name = %s Gauntlets" % (_m, _m))
    MKLANG.append("items.Weapon_Fist_Gauntlets_%s.description = Click: a heavy jab, %s damage; every 4th is a %s finisher. Hits one enemy. Right click: block."
                  % (_m, bnum(GAUNT[_m]["jab"]), bnum(GAUNT[_m]["fin"])))
for _c, _col, _k, _p in WRAPS:
    MKLANG.append("items.Weapon_Fist_Wraps_%s.name = %s Hand Wraps" % (_c, _c))
    MKLANG.append("items.Weapon_Fist_Wraps_%s.description = Click: %d quick jabs, %s damage each; jab %d is a %s power hit. Hits one enemy. Right click: block."
                  % (_c, _k, bnum(WRAP[_c]["jab"]), _p, bnum(WRAP[_c]["pow"])))
for _l in MKLANG:
    assert ("\n" + _l.split(" = ")[0] + " ") not in _vlang, "vanilla already has " + _l.split(" = ")[0]
ASSETS[P_LANG] = ASSETS[P_LANG] + "\n".join(MKLANG) + "\n"
# fixer (critic: the 22 caster items' own descriptions never said so): their description line ends with " Right click: block." too
_ll = ASSETS[P_LANG].split("\n")
_gl = {}
for _n, _l in enumerate(_ll):
    for _i in GUARDED:
        if _l.startswith("items.%s.description = " % _i):
            assert _i not in _gl and "Right click" not in _l, (_i, _l)
            _gl[_i] = _n
assert sorted(_gl) == sorted(GUARDED), sorted(set(GUARDED) - set(_gl))
for _i, _n in _gl.items():
    _ll[_n] = _ll[_n].rstrip() + " Right click: block."
ASSETS[P_LANG] = "\n".join(_ll)

# ---- reference closure of the 0.1.7 files (every id / file they name exists: ours or Assets.zip)
_mbad = []
for _iid in MK_INTS:
    for _r in refs_of(INTS[_iid], set()):
        if _r not in INTS and _r not in ROOTS and not az_has("int", _r) and not az_has("root", _r):
            _mbad.append("%s -> %s" % (_iid, _r))
    _txt = json.dumps(INTS[_iid])
    for _sn in re.findall(r'"(?:World|Local)SoundEventId": "([^"]+)"', _txt):
        if not az_has("sound", _sn):
            _mbad.append("%s: sound %s" % (_iid, _sn))
    for _ps in re.findall(r'"SystemId": "([^"]+)"', _txt):
        if _ps not in _IDX["psys"]:
            _mbad.append("%s: particles %s" % (_iid, _ps))
    for _an in re.findall(r'"ItemAnimationId": "([^"]+)"', _txt):
        if _an not in ANIMS[ANIM_FIST]["Animations"] and _an not in _unarmed:
            _mbad.append("%s: animation %s" % (_iid, _an))
for _i in MONK_IDS + GUARDED:
    for _slot, _rid in ITEMS[_i]["Interactions"].items():
        if _rid not in ROOTS and not az_has("root", _rid):
            _mbad.append("%s %s -> %s" % (_i, _slot, _rid))
    for _f in ("Icon", "Texture", "Model"):
        if ("Common/" + ITEMS[_i][_f]) not in AZ_SET and ("Common/" + ITEMS[_i][_f]) not in ASSETS:
            _mbad.append("%s: %s %s" % (_i, _f, ITEMS[_i][_f]))
    if not az_has("quality", ITEMS[_i]["Quality"]) or ("Server/Audio/ItemSounds/%s.json" % ITEMS[_i].get("ItemSoundSetId")) not in AZ_SET:
        _mbad.append("%s: quality / sound set" % _i)
    if ITEMS[_i]["PlayerAnimationsId"] not in ANIMS and not az_has("anim", ITEMS[_i]["PlayerAnimationsId"]):
        _mbad.append("%s: animation set %s" % (_i, ITEMS[_i]["PlayerAnimationsId"]))
for _i in MONK_IDS:
    for _v in (ITEMS[_i].get("InteractionVars") or {}).values():
        for _r in refs_of(_v, set()):
            if not az_has("int", _r) and not az_has("root", _r):
                _mbad.append("%s var -> %s" % (_i, _r))
for _a, _d in ANIMS.items():
    if _d.get("Parent") and not az_has("anim", _d["Parent"]):
        _mbad.append("%s: parent %s" % (_a, _d["Parent"]))
    for _e in _d["Animations"].values():
        _mbad += ["%s: %s" % (_a, v_) for k_, v_ in _e.items() if k_ in ("ThirdPerson", "ThirdPersonMoving", "FirstPerson", "ThirdPersonFace")
                  and ("Common/" + v_) not in AZ_SET]
assert not _mbad, "0.1.7 reference closure: %s" % _mbad[:8]
_mtxt = json.dumps([INTS[x] for x in MK_INTS])
assert "ModifyInventory" not in _mtxt and "StatModifiers" not in _mtxt and "Costs" not in _mtxt and _mtxt.count('"Raycast"') == 2 * 12 \
    and '"Horizontal"' not in _mtxt and not [x for x in MK_INTS if json.dumps(INTS[x]).count('"Type"') != 1], \
    "the fist chains: the Raycast pick only (2 per weapon: jab + power), every part its own asset (no inline child)"
MK_FILES = sorted(set([P_FINT % i for i in MK_INTS] + [P_FROOT % r for r in MK_ROOTS] + ANIM_FILES + [P_BOITEM % m for m in BO_METALS]
                      + [P_FITEM % i for i in GAUNT_IDS + WRAP_IDS] + ["Common/" + p % m for m in BO_METALS for p in (MODEL_BO, TEX_BO, ICON_BO)]
                      + ["Common/" + p % (i.split("_")[2], i.split("_")[3]) for i in GAUNT_IDS + WRAP_IDS for p in (MODEL_FIST, TEX_FIST, ICON_FIST)]))
assert all(p in ASSETS for p in MK_FILES) and len(MK_FILES) == len(MK_INTS) + len(MK_ROOTS) + len(ANIMS) + 19 + 3 * 19, len(MK_FILES)
print("0.1.7 bo staffs (2 swings / %s s, %d %% of the sword): %s" % (bnum(VAN_TAP_S), int(BO_SHARE * 100), ", ".join(
    "%s %s" % (m, bnum(BO[m]["hit"])) for m in BO_METALS)))
print("0.1.7 gauntlets (jab every %s s - sword %s / dagger %s - finisher + %s s gap, %d %% of the sword): %s" % (
    bnum(GAUNT_T), bnum(SWORD_T), bnum(DAGGER_T), bnum(GAUNT_GAP), int(GAUNT_SHARE * 100), ", ".join(
        "%s %s/%s" % (m, bnum(GAUNT[m]["jab"]), bnum(GAUNT[m]["fin"])) for m in GAUNT_METALS)))
print("0.1.7 hand wraps (%s s jabs, no gap, %d %% of the column sword): %s" % (bnum(JAB_T), int(WRAP_SHARE * 100), ", ".join(
    "%s %d/click power on %d %s/%s" % (c, WRAP[c]["k"], WRAP[c]["p"], bnum(WRAP[c]["jab"]), bnum(WRAP[c]["pow"])) for c, _col, _k, _p in WRAPS)))
print("0.1.7 right click = block (%s) on %d items; animation sets %s; art %s" % (GUARD_ROOT, len(ALL_GUARDED), ", ".join(sorted(ANIMS)),
                                                                                sorted(set(MK_REVIEW.values()))))
'''
before('''# ================================================================= the SET jars, SkyySkills (anchor + handover), the clash scan''', ST_ASSETS)
rep('''                   ("Server/Item/Recipes/", "recipe"), ("Server/ProjectileConfigs/", "pcfg"), ("Server/Entity/Effects/", "efx")):''',
    '''                   ("Server/Item/Recipes/", "recipe"), ("Server/ProjectileConfigs/", "pcfg"), ("Server/Entity/Effects/", "efx"),
                   ("Server/Item/Animations/", "anim")):          # 0.1.7: our animation sets''')
rep('''GEAR_PARTNER = "0.2.8"         # 0.1.6: Weapon_Kunai_<Metal> bands by the metal word (0.2.7 puts them in the Kunai row 20-27)''',
    '''GEAR_PARTNER = "0.2.9"         # 0.1.7: the Monk weapons scale like the same-metal sword (0.2.8: they are their own base -> far weaker per level)''')
rep('''        "SkyyArmory %s is pinned with SkyyGear %s: pin SkyyGear %s+ (the kunai level bands) in the same deploy" % (VERSION, _gpin, GEAR_PARTNER))''',
    '''        "SkyyArmory %s is pinned with SkyyGear %s: pin SkyyGear %s+ (the Monk weapon twin) in the same deploy" % (VERSION, _gpin, GEAR_PARTNER))''')

# ================================================================================================ the default file, the kit categories, read-only rows
rep('''    "# No ground within this many blocks under the spot 3 blocks behind you = half the hop (0 = off).",
    "hop.groundCheck=6",
''', '')
rep('''] + [x for x in BK_TAB_LINES if x.startswith(("# Teleport", "# Return", "kunai.", "ret."))] + [
    "",
    "# ---- Mana check (server log)",''', '''] + [x for x in BK_TAB_LINES if x.startswith(("# Teleport", "# Return", "kunai.", "ret."))] + [
    "",
    "# ---- Monk stunlock (SkyyArmory 0.1.7, Skyy 2026-10-07): a boss / mini-boss under nonstop Monk combo hits breaks out and hits you",
] + [x for _r in CFG_ST for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
    "",
    "# ---- Mana check (server log)",''')
rep('''            ("book", "Spellbook burst"), ("lev", "Spellbook Levitate"), ("kunai", "Kunai"),''',
    '''            ("book", "Spellbook burst"), ("lev", "Spellbook Levitate"), ("kunai", "Kunai"), ("stun", "Monk stunlock"), ("monk", "Monk weapons (fixed)"),''')
rep('''FIXED.append(("hop.mode", "Hop mode (fixed in the jar)", "hop", HOP_MODE,
              "server = the Java push (live force, ground check); asset = the client dash."))''',
    '''FIXED.append(("hop.mode", "Hop mode (fixed in the jar)", "hop", HOP_MODE,
              "server = the Java push (live force, no void check - Skyy); asset = the client dash."))''')
ST_FIXED = r'''
FIXED.append(("fixed.guard", "Right click = block (fixed in the jar)", "monk",
              "hold right click to block (the vanilla guard %s) on every SkyyArmory wand, staff, spellbook, bo staff, wraps + gauntlets; "
              "crossbows grapple, kunai return" % GUARD_ROOT, "Skyy 2026-10-07: block is the default unless the traversal needs right click."))
for _m in BO_METALS:
    FIXED.append(("fixed.bo.%s" % _m, "%s Bo Staff (fixed in the jar)" % _m, "monk",
                  "2 swings x %s dmg (%s s each, %d %% of the %s sword) - hold = the vanilla staff cast - Lv %d-%d - the %s sword recipe" % (
                      bnum(BO[_m]["hit"]), bnum(VAN_TAP_S), int(round(BO[_m]["share"] * 100)), _m, BANDS[_m][0], BANDS[_m][1],
                      "Mithril (Onyxium bars)" if _m == "Onyxium" else _m), "Hit before levels, level band, recipe. Pole-Vault comes later."))
for _m in GAUNT_METALS:
    FIXED.append(("fixed.fist.Gauntlets_%s" % _m, "%s Gauntlets (fixed in the jar)" % _m, "monk",
                  "3 jabs x %s + finisher %s, a jab every %s s, %s s gap after the finisher (%d %% of the sword) - one target - Lv %d-%d - the %s hands recipe" % (
                      bnum(GAUNT[_m]["jab"]), bnum(GAUNT[_m]["fin"]), bnum(GAUNT_T), bnum(GAUNT_GAP), int(round(GAUNT[_m]["share"] * 100)),
                      BANDS[_m][0], BANDS[_m][1], "Mithril (Onyxium bars)" if _m == "Onyxium" else _m),
                  "Client-predicted chain: per-hit damage, timing, level band, recipe."))
for _c, _col, _k, _p in WRAPS:
    FIXED.append(("fixed.fist.Wraps_%s" % _c, "%s Wraps (fixed in the jar)" % _c, "monk",
                  "%d jabs per click x %s, power hit %s on jab %d, %s s a jab, no gap (%d %% of the %s sword) - one target - the %s bolt" % (
                      _k, bnum(WRAP[_c]["jab"]), bnum(WRAP[_c]["pow"]), _p, bnum(JAB_T), int(round(WRAP[_c]["share"] * 100)), _col, _c),
                  "Client-predicted chain (Skyy's jab table): per-hit damage, timing, recipe."))
'''
before('''FIXED_VAL = dict((f[0], f[3]) for f in FIXED)''', ST_FIXED)

# ================================================================================================ ArmoryCfg: the loader, the texts (void rows out, stunlock in)
rep('''  HOP_GROUND = intOf(c.getProperty("hop.groundCheck"), 6, 0, 32);
''', '')
rep('''  K_FLOOR = intOf(c.getProperty("kunai.floorCheck"), 0, 0, 64);
''', '')
rep('''+ ")") + " - wand hold hop " + HOP_FORCE + " (ground " + HOP_GROUND
    + "), burst "''', '''+ ")") + " - wand hold hop " + HOP_FORCE + " (no void check)"
    + ", burst "''')
rep('''    + " s, ground " + K_FLOOR + ", behind mob "''', '''    + " s, no void check, behind mob "''')
after('''for f in ("public static volatile String BOOK_TEXT = \\"\\";", "public static volatile String KUNAI_TEXT = \\"\\";"):
    F(cfg, f)
''', '''F(cfg, "public static volatile String STUN_TEXT = \\"\\";")          # 0.1.7
''')
before('''M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''', '''# 0.1.7: the stunlock breakout's live numbers (bridge armory:stun, the start line)
M(cfg, r"""
public static String stunText() {
  return "boss stunlock breakout " + (PART_STUN ? "on" : "OFF") + " - after " + STUN_PER + " s x the players hitting it (at most " + STUN_MAX
    + "), a pause of " + STUN_GAP + " s starts the count again, then combo hits do nothing for " + STUN_WINDOW + " s (or until it hits a player) - bosses: " + STUN_BOSS;
}""")
''')
after('''  KUNAI_TEXT = kunaiText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:kunai", KUNAI_TEXT); } catch (Throwable tku) { }
''', '''  PART_STUN = bool(c.getProperty("part.stun"), true);          // 0.1.7
  STUN_PER = dec(c.getProperty("stun.perPlayer"), 3.0, 0.5, 20.0);
  STUN_MAX = intOf(c.getProperty("stun.maxPlayers"), 4, 1, 10);
  STUN_GAP = dec(c.getProperty("stun.gap"), 0.8, 0.2, 5.0);          // fixer 2: 0.8 (the gauntlet finisher pause resets it)
  STUN_WINDOW = dec(c.getProperty("stun.window"), 1.5, 0.2, 5.0);
  { String sw = c.getProperty("stun.bossWords"); STUN_BOSS = sw == null ? "@SWORDS@" : (sw.trim().length() > 200 ? sw.trim().substring(0, 200) : sw.trim()); }
  STUN_TEXT = stunText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:stun", STUN_TEXT); } catch (Throwable tst) { }
'''.replace("@SWORDS@", "Boss,Guardian,Duke,Dragon,Chieftain,Elite,Hedera,Rex"))

# ================================================================================================ ArmoryDefs: the Monk combo weapons
after('''          "public static final double BOOK_KDEF = %r;" % BOOK_KDEF, "public static final double K_SHARE_DEF = %r;" % KUNAI_SHARE_DEF):
    F(dfs, f)
''', '''F(dfs, "public static final String[] STUN_PRE = %s;" % jarr(STUN_PRE))          # 0.1.7: the Monk combo weapons (stunlock count)
''')

# ================================================================================================ the classes (declared up front: javassist needs them)
rep('''kun = pool.makeClass(PKG + ".Kunai")
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick,
       gmath, gstate, grap, gimp, gbolt, gfall, lstate, leap, lvst, levc, kst, kimp, kjob, kun]''', '''kun = pool.makeClass(PKG + ".Kunai")
# 0.1.7 the Monk stunlock breakout: the per-boss record + the rule (ArmoryTuneSys calls Stun.filter)
srec = pool.makeClass(PKG + ".StunRec")
stun = pool.makeClass(PKG + ".Stun")
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick,
       gmath, gstate, grap, gimp, gbolt, gfall, lstate, leap, lvst, levc, kst, kimp, kjob, kun, srec, stun]''')

# ================================================================================================ NO VOID PROTECTION: the hop / leap never halves, the kunai takes no ground row
rep('''  double[] pb = @PKG@.TravMath.hopProbe(j.dir[0], j.dir[2]);
  boolean ground = @PKG@.TravMath.ground(grid(w), pos.x + pb[0], pos.y, pos.z + pb[1], @PKG@.ArmoryCfg.HOP_GROUND);
  double[] hv = @PKG@.TravMath.hopVector(j.dir[0], j.dir[1], j.dir[2], @PKG@.ArmoryCfg.HOP_FORCE, !ground);''',
    '''  double[] hv = @PKG@.TravMath.hopVector(j.dir[0], j.dir[1], j.dir[2], @PKG@.ArmoryCfg.HOP_FORCE, false);          // 0.1.7: never halved over the void (Skyy)''')
rep('''  LAST_WHY = "hop " + (ground ? "full" : "half (no ground behind)") + (kept ? " - fall kept" : "");''',
    '''  LAST_WHY = "hop full" + (kept ? " - fall kept" : "");''')
rep('''  double[] pb = @PKG@.TravMath.hopProbe(dir[0], dir[2]);
  boolean ground = @PKG@.TravMath.ground(@PKG@.ArmoryTrav.grid(w), pos.x + pb[0], pos.y, pos.z + pb[1], @PKG@.ArmoryCfg.HOP_GROUND);
  double[] hv = @PKG@.TravMath.hopVector(dir[0], dir[1], dir[2], force, !ground);''',
    '''  double[] hv = @PKG@.TravMath.hopVector(dir[0], dir[1], dir[2], force, false);          // 0.1.7: never halved over the void (Skyy)''')
rep('''  return new double[] { hv[0], vy, hv[2], vy != hv[1] ? 1.0 : 0.0, ground ? 1.0 : 0.0 };''',
    '''  return new double[] { hv[0], vy, hv[2], vy != hv[1] ? 1.0 : 0.0, 1.0 };''')
rep('''@PKG@.TravMath.scan(g, pos.x, pos.y, pos.z, aim[0], aim[1], aim[2], aim[3], @PKG@.ArmoryCfg.K_FLOOR)''',
    '''@PKG@.TravMath.scan(g, pos.x, pos.y, pos.z, aim[0], aim[1], aim[2], aim[3], 0)''')
rep('''@PKG@.TravMath.safeNear(@PKG@.ArmoryTrav.grid(w), rt[0], rt[1], rt[2], RET_SEARCH, @PKG@.ArmoryCfg.K_FLOOR)''',
    '''@PKG@.TravMath.safeNear(@PKG@.ArmoryTrav.grid(w), rt[0], rt[1], rt[2], RET_SEARCH, 0)''')

# ================================================================================================ Stun (before ArmoryTuneSys, which calls it)
STUN_JAVA = r'''
# ---------------------------------------------------------------- 0.1.7 StunRec + Stun: the boss stunlock breakout (Skyy LOCKED 2026-10-07)
for f in ("public long start;", "public long last;", "public long openUntil;", "public java.util.HashMap who;"):
    F(srec, f)
C(srec, "public StunRec(long now) { this.start = now; this.last = now; this.openUntil = 0L; this.who = new java.util.HashMap(); }")
for f in ("public static final java.util.concurrent.ConcurrentHashMap BY = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile java.util.Map HAND = null;",          # HARNESS SEAM ONLY (null in the game = InventoryComponent.getItemInHand)
          "public static volatile long BREAKS = 0L;", "public static volatile long IGNORED = 0L;", "public static volatile long BACKS = 0L;",
          "public static volatile String LAST_WHY = \"\";", "public static volatile long UNKNOCKED = 0L;"):
    F(stun, f)
M(stun, "public static void warn(String k, String m) { @PKG@.ArmoryLog.warnOnce(\"stun:\" + k, m); }")
M(stun, r"""
public static boolean weapon(String id) {
  if (id == null) return false;
  for (int i = 0; i < @PKG@.ArmoryDefs.STUN_PRE.length; i++) if (id.startsWith(@PKG@.ArmoryDefs.STUN_PRE[i])) return true;
  return false;
}""")
# fixer 2 (critic: 'Snapdragon' held 'Dragon'): a boss word matches a WHOLE part of the role name split at '_' (multi-part words work too:
# 'Trork_Chieftain'); GrappleMath.bossName (the grapple's substring rule) is not changed
M(stun, r"""
public static boolean bossRole(String role, String words) {
  if (role == null || words == null) return false;
  String r = "_" + role.trim().toLowerCase() + "_";
  String[] ws = words.split(",");
  for (int i = 0; i < ws.length; i++) {
    String w = ws[i].trim().toLowerCase();
    if (w.length() > 0 && r.indexOf("_" + w + "_") >= 0) return true;
  }
  return false;
}""")
# fixer 2 (critic: a cancelled hit still shoves the boss): DamageEntityInteraction.attemptEntityDamage0 queues the KnockbackComponent on the
# target BEFORE it invokes the Damage event (bytecode, asserted at build time), and cancelling the event does not take it back. The event
# handlers run on a fork of that command buffer that is merged AFTER it (Store.internal_invoke: fork -> handleInternal -> mergeParallel), so a
# tryRemoveComponent queued here lands after the put: a breakout-window hit does not push the boss. (The hurt animation and the NPC damage
# systems already skip a cancelled event: EventSystem.shouldProcessEvent.)
M(stun, r"""
public static void noKnock(@CB@ buf, @REF@ target) {
  try {
    buf.tryRemoveComponent(target, @KNBC@.getComponentType());
    UNKNOCKED = UNKNOCKED + 1L;
  } catch (Throwable t) { warn("noknock:" + t.getClass().getName(), "a breakout-window hit could not drop its knockback (" + t + ")"); }
}""")
# the breakout time: stun.perPlayer x the players stunlocking it, at most stun.maxPlayers (Skyy: 1 player 3 s, 2 players 6 s, cap 4 = 12 s)
M(stun, r"""
public static long needMs(int n) {
  int c = @PKG@.ArmoryCfg.STUN_MAX;
  if (c < 1) c = 1;
  int k = n < 1 ? 1 : (n > c ? c : n);
  return Math.round(@PKG@.ArmoryCfg.STUN_PER * (double) k * 1000.0);
}""")
# the players still hitting it: a hit within the gap
M(stun, r"""
public static int players(@PKG@.StunRec r, long now, long gapMs) {
  java.util.Iterator it = r.who.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    Object v = r.who.get(k);
    if (!(v instanceof Long) || now - ((Long) v).longValue() > gapMs) it.remove();
  }
  return r.who.size();
}""")
M(stun, r"""
public static void tidy(long now) {
  if (BY.size() < 32) return;
  java.util.Iterator it = BY.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    Object v = BY.get(k);
    if (!(v instanceof @PKG@.StunRec) || (now - ((@PKG@.StunRec) v).last > 60000L && ((@PKG@.StunRec) v).openUntil < now)) it.remove();
  }
}""")
# THE RULE (plain values: bare-JVM tested). A Monk weapon's melee hit on a boss / mini-boss: true = cancel it (its breakout window is open)
M(stun, r"""
public static boolean onHit(Object target, java.util.UUID who, String item, String role, long now) {
  if (!@PKG@.ArmoryCfg.PART_STUN || target == null || who == null) return false;
  if (!weapon(item) || !bossRole(role, @PKG@.ArmoryCfg.STUN_BOSS)) return false;          // fixer 2: whole parts of the role name
  long gap = Math.round(@PKG@.ArmoryCfg.STUN_GAP * 1000.0);
  @PKG@.StunRec r = (@PKG@.StunRec) BY.get(target);
  if (r != null && r.openUntil > now) {
    r.last = now;
    IGNORED = IGNORED + 1L;
    LAST_WHY = "breakout window - the hit does nothing";
    return true;
  }
  if (r != null && r.openUntil > 0L) r = null;          // the window is over: a new count
  if (r == null || now - r.last > gap) {
    r = new @PKG@.StunRec(now);
    BY.put(target, r);
    tidy(now);
  }
  r.who.put(who, Long.valueOf(now));
  r.last = now;
  int n = players(r, now, gap);
  if (now - r.start >= needMs(n)) {
    r.openUntil = now + Math.round(@PKG@.ArmoryCfg.STUN_WINDOW * 1000.0);
    BREAKS = BREAKS + 1L;
    LAST_WHY = "breakout after " + (now - r.start) + " ms (" + n + " player" + (n == 1 ? "" : "s") + ")";
    return true;
  }
  LAST_WHY = "stunlock " + (now - r.start) + " of " + needMs(n) + " ms (" + n + " player" + (n == 1 ? "" : "s") + ")";
  return false;
}""")
# the boss hit a player: that is the breakout (Skyy: "the boss can hit you to break out") - the next combo hit starts a new count
M(stun, r"""
public static boolean bossHit(Object boss, long now) {
  if (boss == null || BY.remove(boss) == null) return false;
  BACKS = BACKS + 1L;
  LAST_WHY = "the boss hit back - the count starts over";
  return true;
}""")
M(stun, r"""
public static String roleOf(@CAC@ acc, @REF@ r) {
  try {
    Object no = acc.getComponent(r, @NPC@.getComponentType());
    return no instanceof @NPC@ ? ((@NPC@) no).getRoleName() : null;
  } catch (Throwable t) { return null; }
}""")
M(stun, r"""
public static String hand(@CAC@ acc, @REF@ r, java.util.UUID u) {
  java.util.Map h = HAND;
  if (h != null) {
    Object o = h.get(u);
    return o == null ? null : String.valueOf(o);
  }
  return @PKG@.ArmoryTrav.handItem(acc, r);
}""")
# the engine glue (ArmoryTuneSys, the Filter group): a player's MELEE hit (EntitySource, not a projectile) on an NPC -> onHit (true = cancelled);
# an NPC with a live record hitting a player -> bossHit
M(stun, r"""
public static void filter(@CB@ buf, @REF@ target, @DMG@ d) {
  try {
    if (!@PKG@.ArmoryCfg.PART_STUN || d == null || target == null || d.isCancelled()) return;
    Object src = d.getSource();
    if (!(src instanceof @DENT@) || src instanceof @DPRJ@) return;
    @REF@ a = ((@DENT@) src).getRef();
    if (a == null) return;
    long now = System.currentTimeMillis();
    @PR@ ap = @PKG@.Kunai.prOf(buf, a);
    if (ap != null) {
      if (d.getAmount() <= 0.0f) return;          // fixer: the 0-damage guard shove (left click while blocking) never counts toward a stunlock
      String role = roleOf(buf, target);
      if (role == null) return;
      java.util.UUID u = ap.getUuid();
      if (onHit(target, u, hand(buf, a, u), role, now)) {
        d.setCancelled(true);
        noKnock(buf, target);          // fixer 2: the cancelled hit's knockback goes too (it was queued before the event)
      }
      return;
    }
    if (!BY.isEmpty() && BY.containsKey(a) && @PKG@.Kunai.prOf(buf, target) != null) bossHit(a, now);
  } catch (Throwable t) { warn("filter:" + t.getClass().getName(), "the stunlock breakout check failed (" + t + ") - that hit was left alone"); }
}""")
'''
before('''# ---------------------------------------------------------------- ArmoryTuneSys (Filter group, BEFORE ArmorDamageReduction)''', STUN_JAVA)
# fixer 2 (the stunlock window): the knockback a cancelled hit already queued - the members + the engine order Stun.noKnock relies on
KNOCK_PROBE = r'''# fixer 2 (0.1.7 stunlock window): the knockback a cancelled hit already queued (VERIFIED by bytecode 2026-10-07)
T["KNBC"] = "com.hypixel.hytale.server.core.entity.knockback.KnockbackComponent"
for _c, _m, _r, _a in ((T["KNBC"], "getComponentType", T["CTYPE"], []), (T["CB"], "tryRemoveComponent", "void", [T["REF"], T["CTYPE"]])):
    probe_sig(_c, _m, _r, _a)
_dei = _calls("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.DamageEntityInteraction", "attemptEntityDamage0")
assert "putComponent" in _dei and "invoke" in _dei and _dei.index("putComponent") < len(_dei) - 1 - _dei[::-1].index("invoke"),     "DamageEntityInteraction no longer queues the knockback before the Damage event - re-check Stun.noKnock"
_sii = _calls("com.hypixel.hytale.component.Store", "internal_invoke",
              "(Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/event/EntityEventType;Lcom/hypixel/hytale/component/Ref;")
assert "fork" in _sii and "handleInternal" in _sii and "mergeParallel" in _sii and _sii.index("fork") < _sii.index("handleInternal") < _sii.index("mergeParallel"),     "Store.internal_invoke no longer runs event handlers on a fork merged after - re-check Stun.noKnock"
_spe = _calls("com.hypixel.hytale.component.system.EventSystem", "shouldProcessEvent")
assert "isCancelled" in _spe, "EventSystem.shouldProcessEvent no longer skips cancelled events"
PROBED.append("DamageEntityInteraction knockback put before the Damage event; event handlers on a fork merged after; cancelled events skipped")
'''
before('''print("engine members probed: %d" % len(PROBED))''', KNOCK_PROBE)
rep('''    @DMG@ db = (@DMG@) ev;            // 0.1.3: a blast arrow's own hit''',
    '''    if (chunk != null) @PKG@.Stun.filter(buf, chunk.getReferenceTo(idx), (@DMG@) ev);          // 0.1.7: the boss stunlock breakout
    @DMG@ db = (@DMG@) ev;            // 0.1.3: a blast arrow's own hit''')

# ================================================================================================ the plugin: bridge key, setup / shutdown, the start line
rep('''               "armory:grapple", "armory:leap", "armory:book", "armory:kunai"]''',
    '''               "armory:grapple", "armory:leap", "armory:book", "armory:kunai", "armory:stun"]''')
after('''  b.put("armory:kunai", @PKG@.ArmoryCfg.KUNAI_TEXT);
''', '''  b.put("armory:stun", @PKG@.ArmoryCfg.STUN_TEXT);          // 0.1.7
''')
rep('''  @PKG@.Kunai.KNOCK.clear();
''', '''  @PKG@.Kunai.KNOCK.clear();
  @PKG@.Stun.BY.clear();          // 0.1.7
''', count=2)
after('''  @PKG@.ArmoryLog.info("@VERSION@ spellbooks + kunai: " + @PKG@.ArmoryCfg.BOOK_TEXT + " | " + @PKG@.ArmoryCfg.KUNAI_TEXT);
''', '''  @PKG@.ArmoryLog.info("@VERSION@ monk weapons (bo staffs, hand wraps, gauntlets; right click = block): " + @PKG@.ArmoryCfg.STUN_TEXT);
''')
rep('''                 "Assassin kunai Crude to Onyxium (tap = throw, hold = throw + teleport, hold right click = return). "''',
    '''                 "Assassin kunai Crude to Onyxium (tap = throw, hold = throw + teleport, hold right click = return). "
                 "Monk bo staffs, hand wraps and gauntlets (one-target combos; bosses break out of a stunlock); right click = block. "''')

# ================================================================================================ jar check + build lines
rep('''    _sart = sorted(n for n in _names if n.startswith("Common/") and (n.startswith("Common/Items/Weapons/Staff/") or "/SkyyArmory_Staff_" in n))''',
    '''    _sart = sorted(n for n in _names if n.startswith("Common/") and (n.startswith("Common/Items/Weapons/Staff/") or "/SkyyArmory_Staff_" in n)
                   and "/SkyyArmory_Bo_" not in n)          # 0.1.7: the Bo staff art is checked with the Monk files''')
rep('''    _sitems = sorted(n for n in _names if n.startswith("Server/Item/Items/Weapon/Staff/"))''', '''    _mkn = sorted(n for n in _names if n in set(MK_FILES))
    assert _mkn == MK_FILES and len([n for n in MK_FILES if n.startswith("Server/Item/Items/")]) == 19, "0.1.7: the %d Monk weapon files" % len(MK_FILES)
    assert not [n for n in _names if os.path.basename(n)[:-5] in ("Staff_Primary", "Weapon_Staff_Bo_Wood", "Weapon_Staff_Bo_Bamboo", GUARD_ROOT, "Staff", "Spellbook", "Default", "Sword", "Wand")], \\
        "0.1.7 overrides no vanilla bo / guard / animation file"
    _sitems = sorted(n for n in _names if n.startswith("Server/Item/Items/Weapon/Staff/"))''')
rep('''          len(BK_TAB), len([f for f in FIXED if f[0].startswith(("fixed.book", "fixed.kunai"))]), CLASSES_PARTNER, GEAR_PARTNER))''',
    '''          len(BK_TAB), len([f for f in FIXED if f[0].startswith(("fixed.book", "fixed.kunai"))]), CLASSES_PARTNER, GEAR_PARTNER))
print("0.1.7 monk weapons: %d files (19 items, %d interactions, %d roots, %d animation sets), %d stunlock rows, %d read-only rows, block on %d items; "
      "void rows removed: hop.groundCheck, kunai.floorCheck; partner SkyyGear %s (the Monk weapon twin)" % (
          len(MK_FILES), len(MK_INTS), len(MK_ROOTS), len(ANIMS), len(CFG_ST), len([f for f in FIXED if f[0].startswith(("fixed.guard", "fixed.bo.", "fixed.fist"))]),
          len(ALL_GUARDED), GEAR_PARTNER))''')

assert s.count("registerSystem(") == SYS0, "0.1.7 registers no new system (ArmoryTuneSys carries the stunlock check)"
assert "HOP_GROUND" not in s and "ArmoryCfg.K_FLOOR" not in s and "  K_FLOOR = " not in s and '"hop.groundCheck=' not in s, "a void row survived"
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))


# ================================================================================================ the harness: 0.1.6's checks (+ the set changes) + P11 / R11
traw = open(TSRC, encoding="utf8", newline="").read()
TNL = CR + LF if (CR + LF) in traw else LF
ts = traw.replace(CR + LF, LF)


def hrep(old, new, count=1):
    global ts
    n = ts.count(old)
    assert n == count, "harness anchor count %d (want %d): %s" % (n, count, old[:140])
    ts = ts.replace(old, new)


hrep('"""SkyyArmory 0.1.6 - test harness. GENERATED by tools/armory_0_1_6_patch.py from test_skyyarmory_0.1.5.py - edit the patch, never this file.',
     '''"""SkyyArmory 0.1.7 - test harness. GENERATED by tools/armory_0_1_7_patch.py from test_skyyarmory_0.1.6.py - edit the patch, never this file.
Every 0.1.6 check below still runs, patched only where 0.1.7 changed the set on purpose: the 19 Monk items + their chains / roots / animation
sets / art are checked in P11 + R11 (the older checks see the 0.1.6 set); the 22 caster items' right click (= block) and staff / book animation
set are put back to their 0.1.6 shape for the older checks (P11 checks the real files); the two void rows are gone (N4 + R10d now expect no
void protection); R10f's 0.1.5 -> 0.1.6 compare is history (R11e compares 0.1.6 -> 0.1.7).
NEW P11 (Python) + R11 (JVM, after R10) EXECUTE every 0.1.7 path:
  P11  the 19 items (ids, Quality / ItemLevel, guard right click, animation set, dual-wield, recipes = sword / hands armor / bolt + bench),
       the right-click guard on all 41 SkyyArmory weapons (crossbows grapple, kunai return), the 3 animation sets (copies of the vanilla set +
       Sword's Guard / GuardBash, the unarmed punches sped up), the timings from the jar's own chains vs Assets.zip (gauntlet jab between the
       vanilla sword and dagger, a gap after the finisher; wraps: Skyy's jab table, no gap), one Raycast pick per jab (ONE enemy), DPS shares;
  R11a the 19 items + 131 interactions + 12 roots + 3 animation sets decode through the engine codecs into the real stores; RootInteraction
       .build() of every fist root (0 missing); SkyyGear / SkyyClasses read our ids (bands; the class rule = the "Weapon_" catch-all);
  R11b the stunlock breakout (Stun.onHit on plain values: 1 player 3 s, 2 players 6 s, cap 4 = 12 s, a pause restarts, the window, the boss hit,
       bosses only, Monk weapons only, part off) + Stun.filter / ArmoryTuneSys on REAL Damage objects (player melee -> cancelled at the
       breakout; the boss hitting a player ends it; projectiles, other mobs, other weapons left alone);
  R11c no void protection: the wand hop + the leap hop full over the void, the kunai over the void, the rows gone, blink.floorCheck 0 kept;
  R11d the 6 stunlock rows + 20 read-only rows, the loader clamps, armory:stun, the default file;
  R11e vs the 0.1.6 jar: the new files = exactly the 0.1.7 set + 2 classes, the 22 caster items differ in Secondary / PlayerAnimationsId only,
       the lang file only grows, the changed classes listed.

0.1.6 harness: SkyyArmory 0.1.6 - test harness. GENERATED by tools/armory_0_1_6_patch.py from test_skyyarmory_0.1.5.py - edit the patch, never this file.''')
hrep('VERSION = "0.1.6"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.6 SkyyArmory"',
     'VERSION = "0.1.7"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.7 SkyyArmory"')
hrep('os.path.join(SCRATCH_ROOT, "armory016", "harness")', 'os.path.join(SCRATCH_ROOT, "armory017", "harness")')
hrep('raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.6.py', 'raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.7.py')
hrep('Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.6"))', 'Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.7"))')
hrep('"[SkyyArmory] 0.1.6 ready" in m_', '"[SkyyArmory] 0.1.7 ready" in m_')
hrep('"0.1.6 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_', '"0.1.7 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_')
hrep('"0.1.6 crossbow grapple: grapple on" in m_', '"0.1.7 crossbow grapple: grapple on" in m_')
hrep('"32 of 32 items, 207 of 207 interactions, 62 of 62 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.6 SkyyArmory" in str(r[1])',
     '"51 of 51 items, 338 of 338 interactions, 62 of 62 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.7 SkyyArmory" in str(r[1])')

# P0: the Monk files are checked in P11 / R11; the 22 guarded caster items are put back to their 0.1.6 shape for every older check
hrep('''J_PNG = [n for n in J_PNG if n not in L16_PNG]
''', '''J_PNG = [n for n in J_PNG if n not in L16_PNG]
# 0.1.7: the Monk weapon files + the animation sets are checked in P11 / R11; the older checks below see the 0.1.6 set
L17_PRE = ("Weapon_Bo_", "Weapon_Fist_", "SkyyArmory_Fist_")


def l17_pop(d):
    return dict((k_, d.pop(k_)) for k_ in sorted(d) if k_.startswith(L17_PRE))


L17_ITEMS, L17_INTS, L17_ROOTS = l17_pop(J_ITEMS), l17_pop(J_INTS), l17_pop(J_ROOTS)
L17_PNG = [n for n in J_PNG if n.startswith("Common/Items/Weapons/Fist/") or "/SkyyArmory_Bo_" in n or "/SkyyArmory_Fist_" in n]
J_PNG = [n for n in J_PNG if n not in L17_PNG]
L17_ANIM = by_dir("Server/Item/Animations/")
_l17p = set(list(L17_ITEMS.values()) + list(L17_INTS.values()) + list(L17_ROOTS.values()) + list(L17_ANIM.values()))
L17_J = dict((p_, J.pop(p_)) for p_ in list(J) if p_ in _l17p)
GUARD17 = "Root_Common_Guard_Entry_StaminaCondition"
L17_REAL = {}          # the 22 caster items as shipped (right click = the guard; staffs / books on our animation sets)
for _p17, _d17 in sorted(J.items()):
    if _p17.startswith("Server/Item/Items/") and isinstance(_d17.get("Interactions"), dict) and _d17["Interactions"].get("Secondary") == GUARD17:
        L17_REAL[_p17] = copy.deepcopy(_d17)
        _d17["Interactions"]["Secondary"] = _d17["Interactions"]["Primary"]
        _d17["PlayerAnimationsId"] = {"SkyyArmory_Staff": "Staff", "SkyyArmory_Spellbook": "Spellbook"}.get(_d17.get("PlayerAnimationsId"), _d17.get("PlayerAnimationsId"))
''')
hrep('''    jitm = dict((k_, json.loads(JZ.read(p_).decode("utf-8"))) for k_, p_ in L16_ITEMS.items())''',
     '''    jitm = dict((k_, copy.deepcopy(J[p_])) for k_, p_ in L16_ITEMS.items())          # 0.1.7: the 0.1.6 shape (P11 checks the guard)''')

hrep('''    check(len(names) == 43, "A: 43 classes (36 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap + 0.1.6's 6 book / kunai classes + 7 kit)")''',
     '''    check(len(names) == 45, "A: 45 classes (38 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap + 0.1.6's 6 book / kunai + 0.1.7's 2 stunlock classes + 7 kit)")''')

# ---- K: the config kit rows (- the two void rows, + 0.1.7's 6 stunlock rows after the 0.1.6 rows, + 20 read-only rows)
hrep('''                "blink.cooldown", "hop.force", "hop.groundCheck", "burst.radius", "burst.percent", "orb.radius", "orb.seconds", "orb.healPercent",''',
     '''                "blink.cooldown", "hop.force", "burst.radius", "burst.percent", "orb.radius", "orb.seconds", "orb.healPercent",          # 0.1.7: - hop.groundCheck''')
hrep('''                 "part.kunai", "kunai.dpsShare", "kunai.throwRange", "kunai.flightTtl", "kunai.floorCheck", "kunai.behindMob", "kunai.noArena",
                 "kunai.noCombat", "kunai.pvp", "kunai.maxPerMinute", "ret.force", "ret.damage"]      # 0.1.6
    TAB16''', '''                 "part.kunai", "kunai.dpsShare", "kunai.throwRange", "kunai.flightTtl", "kunai.behindMob", "kunai.noArena",
                 "kunai.noCombat", "kunai.pvp", "kunai.maxPerMinute", "ret.force", "ret.damage"]      # 0.1.6 (0.1.7: - kunai.floorCheck)
    NEW_ROWS += ["part.stun", "stun.perPlayer", "stun.maxPlayers", "stun.gap", "stun.window", "stun.bossWords"]      # 0.1.7
    TAB16''')
hrep('''          and len(keys) == 10 + NN + 13 + 8 + 8 + 5 + 2 + 2 + 17,''', '''          and len(keys) == 10 + NN + 13 + 8 + 8 + 5 + 2 + 2 + 17 + 20,''')
hrep('''                "blink.trailPercent": "30", "blink.tick": "0.5", "blink.cooldown": "0", "hop.force": "30", "hop.groundCheck": "6", "burst.radius": "6",''',
     '''                "blink.trailPercent": "30", "blink.tick": "0.5", "blink.cooldown": "0", "hop.force": "30", "burst.radius": "6",''')
hrep('''              "kunai.floorCheck": "0", "kunai.behindMob": "false", "kunai.noArena": "true", "kunai.noCombat": "false", "kunai.pvp": "world",''',
     '''              "kunai.behindMob": "false", "kunai.noArena": "true", "kunai.noCombat": "false", "kunai.pvp": "world",''')
hrep('''          "R10e: the 20 new rows emit with the spec defaults,''', '''          "R10e: the 19 0.1.6 rows still there (0.1.7: - kunai.floorCheck) emit with the spec defaults,''')
# ---- N4: NO void protection (Skyy LOCKED 2026-10-07) - the hop is never halved over the void
hrep('''    check(h4 is not None and h4[0] == (0.0, 0.0, -6.5) and str(AT.LAST_WHY).startswith("hop half"), "N4 (4): no ground 3 blocks behind -> half the hop: %s" % (h4,))''',
     '''    check(h4 is not None and h4[0] == (0.0, 0.0, -13.0) and str(AT.LAST_WHY).startswith("hop full"),
          "N4 (0.1.7, Skyy 'dont put any void protection on any traversal'): no ground 3 blocks behind -> the FULL hop (0.1.6: half): %s" % (h4,))''')
# ---- R10d: the kunai has no ground row any more (0.1.6's admin floorCheck 12 case is gone with the row)
hrep('''    floor_def = int(ACfg.K_FLOOR)
    tpl4v = kvoid()
    ACfg.K_FLOOR = 12
    tpl4 = kvoid()
    ACfg.K_FLOOR = floor_def
    check(floor_def == 0 and tpl4v is not None and tpl4v[0] >= 9.5,''', '''    tpl4v = kvoid()
    k_floor_row = [f_ for f_ in ACfg.class_.getFields() if str(f_.getName()) == "K_FLOOR"]
    floor_def = 0 if not k_floor_row else -1
    check(floor_def == 0 and tpl4v is not None and tpl4v[0] >= 9.5,''')
hrep('''          "open void lands you over the void where it was (x >= 9.5, not shortened): floorCheck %s, landed %s" % (floor_def, tpl4v))''',
     '''          "open void lands you over the void where it was (x >= 9.5, not shortened; 0.1.7: no kunai.floorCheck row at all): %s, landed %s" % (floor_def, tpl4v))''')
hrep('''    check(tpl4 is not None and tpl4[0] == 3.5 and tpl5 is None and nom5 == (10.0, 200.0, "no safe spot - refunded") and out6[0] == 1 and out6[1]''',
     '''    check(tpl5 is None and nom5 == (10.0, 200.0, "no safe spot - refunded") and out6[0] == 1 and out6[1]''')
hrep('''          "R10d (Kunai-Ladder 6): with an admin kunai.floorCheck 12 (default 0) over open void you land at the last spot with ground (x 3.5); a teleport that cannot move you is refunded in full "
          "(Stamina + Mana back); a kunai past kunai.range 20 lands you where it left the range (the kunai is removed): %s %s %s %s" % (tpl4, tpl5, nom5, out6))''',
     '''          "R10d (Kunai-Ladder 6): a teleport that cannot move you is refunded in full (Stamina + Mana back); a kunai past kunai.range 20 lands you "
          "where it left the range (the kunai is removed): %s %s %s" % (tpl5, nom5, out6))''')
# ---- R10f: the 0.1.5 -> 0.1.6 compare is history (R11e compares 0.1.6 -> 0.1.7)
hrep('''    OLD15 = os.path.join(HERE, "SkyyArmory-0.1.5.jar")
    if not os.path.isfile(OLD15):
        print("R10f. NOTE no SkyyArmory-0.1.5.jar here - the old-vs-new file compare is skipped")''',
     '''    OLD15 = None          # 0.1.7: the 0.1.5 -> 0.1.6 compare is history - R11e compares 0.1.6 -> 0.1.7
    if OLD15 is None:
        print("R10f. NOTE (0.1.7) the 0.1.5 -> 0.1.6 file compare is history - R11e compares 0.1.6 -> 0.1.7")''')

# ---- L: the 0.1.7 assets decode + load from our pack before the pack check counts them
L17_LOAD = r"""    # ---- 0.1.7 (R11a): the Monk items / chains / roots through the engine codecs (no unknown key, no failed validation) into the real stores.
    # The selector types (Raycast ...) and knockback types are CodecMapCodec registrations of InteractionModule.setup (read from its bytecode,
    # the E pattern) - the bare JVM had only its AssetCodecMapCodec ones
    imc17 = CPj.get("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    ms17 = [x_ for x_ in imc17.getDeclaredMethods() if str(x_.getName()) == "setup"][0]
    cp17, it17 = ms17.getMethodInfo().getConstPool(), ms17.getMethodInfo().getCodeAttribute().iterator()
    gs17, s17, c17, maps17 = [], None, None, []
    while it17.hasNext():
        p_ = it17.next()
        op_ = it17.byteAt(p_)
        if op_ == 0xb2:
            idx_ = it17.u16bitAt(p_ + 1)
            gs17.append((str(cp17.getFieldrefClassName(idx_)), str(cp17.getFieldrefName(idx_))))
        elif op_ in (0x12, 0x13):
            idx_ = it17.byteAt(p_ + 1) if op_ == 0x12 else it17.u16bitAt(p_ + 1)
            tg_ = cp17.getTag(idx_)
            if tg_ == CPool.CONST_String:
                s17 = str(cp17.getStringInfo(idx_))
            elif tg_ == CPool.CONST_Class:
                c17 = str(cp17.getClassInfo(idx_))
        elif op_ == 0xb6:
            idx_ = it17.u16bitAt(p_ + 1)
            if str(cp17.getMethodrefClassName(idx_)) == "com.hypixel.hytale.codec.lookup.CodecMapCodec" and str(cp17.getMethodrefName(idx_)) == "register" \
                    and len(gs17) >= 2:
                maps17.append((gs17[-2], s17, c17))
    reg17 = []
    for (rc_, rf_), nm_, cl_ in maps17:
        try:
            jfield(JClass(rc_), rf_).get(None).register(nm_, JClass(cl_).class_, jfield(JClass(cl_), "CODEC").get(None))
            reg17.append("%s.%s" % (rc_.split(".")[-1], nm_))
        except Exception as e_:
            reg17.append("%s.%s (%s)" % (rc_.split(".")[-1], nm_, str(e_)[:60]))
    check("SelectorType.Raycast" in reg17 and "Knockback.Force" in reg17 and len(maps17) >= 10,
          "R11a (bare-JVM setup): InteractionModule.setup's CodecMapCodec registrations replayed (selector + knockback + break shapes): %s" % reg17)
    bad17 = []

    def dec17(c, key, text):
        # dec() that keeps the AssetExtraInfo: our inline steps (Next / Serial children) are CONTAINED assets the engine loads with the parent
        st = AR.getAssetStore(c.class_)
        ei = AEI(Paths.get(key + ".json"), ADT(c.class_, key, None))
        try:
            o = st.getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception as e:
            return None, "exception " + str(e)[:300], None
        prob = []
        vr = ei.getValidationResults()
        if vr is not None and vr.hasFailed():
            prob.append("validation failed %s" % [str(x) for x in (vr.getResults() or [])][:3])
        uk = [str(x) for x in ei.getUnknownKeys()]
        if uk:
            prob.append("unknown keys %s" % uk)
        return o, "; ".join(prob), ei
    for c_, tab_, kind_ in ((INTc, L17_INTS, "interaction"), (ROOTc, L17_ROOTS, "root"), (ITMc, L17_ITEMS, "item")):
        objs_, eis_ = [], []
        for k_ in sorted(tab_):
            o_, w_, ei_ = dec17(c_, k_, JZ.read(tab_[k_]).decode("utf-8"))
            if o_ is None or w_:
                bad17.append("%s %s: %s" % (kind_, k_, w_))
                continue
            DEC[(kind_, k_)] = o_
            objs_.append(o_)
            eis_.append(ei_)
        load(c_, objs_, PACK)
        for ei_ in eis_:
            try:
                ei_.getData().loadContainedAssets(False)
            except Exception as e_:
                bad17.append("%s contained assets: %s" % (kind_, str(e_)[:160]))
        for k_ in sorted(tab_):
            if c_.getAssetMap().getAsset(k_) is None or str(c_.getAssetMap().getAssetPack(k_)) != PACK:
                bad17.append("%s %s is not in the store from our pack" % (kind_, k_))
    check(not bad17 and len(L17_ITEMS) == 19 and len(L17_INTS) == 131 and len(L17_ROOTS) == 12,
          "L (0.1.7 / R11a): the 19 Monk items, 131 fist interactions, 12 fist roots decode through the engine codecs (no unknown key) and sit "
          "in the real stores from our pack: %s" % bad17[:4])
    dbad17 = [k_ for k_ in L17_ITEMS if ("item", k_) not in DEC or int(DEC[("item", k_)].getMaxStack()) != 1 or DEC[("item", k_)].getWeapon() is None]
    check(not dbad17, "R11a: every Monk weapon decodes as a weapon with MaxStack 1: %s" % dbad17)
"""
hrep('''    CHK = JClass(PKG + "ArmoryCheck")
    r = CHK.packCheck()''', L17_LOAD + '''    CHK = JClass(PKG + "ArmoryCheck")
    r = CHK.packCheck()''')

# ---- P11 (Python, before the JVM part): every 0.1.7 file checked on its own (independent of the build's numbers)
P11 = r'''
# ============================================================================================================ P11. 0.1.7 the Monk weapons + the guard (pure files)
GUARD = "Root_Common_Guard_Entry_StaminaCondition"
MKM = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
MKW = [("Linen", "Copper", 2, 6), ("Cotton", "Iron", 2, 6), ("Silk", "Thorium", 2, 4), ("Cindercloth", "Cobalt", 3, 6), ("Shadoweave", "Adamantite", 5, 5)]   # Skyy's table
BOI = ["Weapon_Bo_" + m for m in MKM]
GAI = ["Weapon_Fist_Gauntlets_" + m for m in MKM]
WRI = ["Weapon_Fist_Wraps_" + c for c, _x, _k, _p in MKW]
MI = dict((i, L17_J[L17_ITEMS[i]]) for i in L17_ITEMS)
MINT = dict((i, L17_J[L17_INTS[i]]) for i in L17_INTS)
MROOT = dict((i, L17_J[L17_ROOTS[i]]) for i in L17_ROOTS)
MANIM = dict((i, L17_J[L17_ANIM[i]]) for i in L17_ANIM)
check(sorted(MI) == sorted(BOI + GAI + WRI) and all("skyy" not in i.lower() for i in MI) and not [i for i in MI if ahas("item", i)]
      and not [i for i in MI if i.startswith(("Weapon_Staff_", "Weapon_Claws_"))],
      "P11: 19 Monk items = 7 bo staffs + 7 gauntlets + 5 hand wraps, no 'skyy' in an id, none overrides a vanilla id, none on the Mage's "
      "Weapon_Staff_ / SkyyGear's excluded Weapon_Claws_ prefix: %s" % sorted(MI))
check(sorted(MANIM) == ["SkyyArmory_Fist", "SkyyArmory_Spellbook", "SkyyArmory_Staff", "SkyyArmory_Wand"] and not [a for a in MANIM if ahas("anim", a)]
      and sorted(L17_ANIM.values()) == sorted("Server/Item/Animations/SkyyArmory/%s.json" % a for a in MANIM),
      "P11: 4 own animation sets under Server/Item/Animations/SkyyArmory/ (no vanilla id)")
# --- quality / level / shape
qbad = []
for m in MKM:
    sw = aresolve("item", "Weapon_Sword_" + m)
    for i in ("Weapon_Bo_" + m, "Weapon_Fist_Gauntlets_" + m):
        if (MI[i]["Quality"], MI[i]["ItemLevel"]) != (sw["Quality"], sw["ItemLevel"]):
            qbad.append(i)
WBAND = {"Copper": 10, "Iron": 15, "Thorium": 20, "Cobalt": 25, "Adamantite": 35}
for c, col, k, p in MKW:
    i = "Weapon_Fist_Wraps_" + c
    if (MI[i]["Quality"], MI[i]["ItemLevel"]) != (aresolve("item", "Weapon_Sword_" + col)["Quality"], WBAND[col]):
        qbad.append(i)
check(not qbad, "P11: bo staffs + gauntlets take the metal's sword Quality / ItemLevel, wraps the column's Quality + band start (Shadoweave 35 = "
                "its SkyyGear fallback level): %s" % qbad)
vbo = aj("item", "Weapon_Staff_Bo_Wood")
sbad = []
for i in BOI:
    d = MI[i]
    if d["Interactions"] != {"Primary": "Staff_Primary", "Secondary": GUARD} or d["PlayerAnimationsId"] != "SkyyArmory_Staff" or d["Weapon"] != {}:
        sbad.append(i + " chain")
    if sorted(d["InteractionVars"]) != sorted(vbo["InteractionVars"]) or any(d["InteractionVars"][k] != vbo["InteractionVars"][k] for k in vbo["InteractionVars"]
                                                                             if not k.endswith("_Damage")):
        sbad.append(i + " vars")
    if d["IconProperties"] != vbo["IconProperties"] or d["Tags"] != vbo["Tags"] or d["ItemSoundSetId"] != vbo["ItemSoundSetId"] or "MaxStack" in d:
        sbad.append(i + " shape")
for i in GAI + WRI:
    d = MI[i]
    key = i[len("Weapon_Fist_"):]
    if d["Interactions"] != {"Primary": "SkyyArmory_Fist_%s_Primary" % key, "Secondary": GUARD} or d["PlayerAnimationsId"] != "SkyyArmory_Fist" \
            or d["Weapon"] != {"RenderDualWielded": True} or "MaxStack" in d or d["Tags"] != {"Type": ["Weapon"], "Family": ["Fist"]}:
        sbad.append(i)
check(not sbad, "P11: bo staffs = the vanilla Wood Bo item (Staff_Primary: tap = its swing chain, hold = the vanilla staff cast - only the two swing "
      "damages differ) with right click = the guard on our staff set; wraps / gauntlets = our fist root + the guard, the fist set, dual-wielded: %s" % sbad)


def rcp(i):
    r = copy.deepcopy(aresolve("item", i).get("Recipe"))
    if r and "BenchRequirement" in r:
        r["BenchRequirement"] = [b for b in r["BenchRequirement"] if b.get("Id") != "Armory"]
    return r


def onyx(r, src):
    r = copy.deepcopy(r)
    for x in r["Input"]:
        if x.get("ItemId") == "Ingredient_Bar_" + src:
            x["ItemId"] = "Ingredient_Bar_Onyxium"
    return r


rbad = []
for m in MKM:
    if aresolve("item", "Weapon_Spear_" + m).get("Recipe") is not None:
        rbad.append("spear " + m)
    want_b = rcp("Weapon_Sword_" + m) if m != "Onyxium" else onyx(rcp("Weapon_Sword_Mithril"), "Mithril")
    want_gr = rcp("Armor_%s_Hands" % m) if m != "Onyxium" else onyx(rcp("Armor_Mithril_Hands"), "Mithril")
    if MI["Weapon_Bo_" + m]["Recipe"] != want_b:
        rbad.append("bo " + m)
    if MI["Weapon_Fist_Gauntlets_" + m]["Recipe"] != want_gr:
        rbad.append("gauntlets " + m)
for c, col, k, p in MKW:
    r = MI["Weapon_Fist_Wraps_" + c]["Recipe"]
    src = rcp("Armor_Cloth_%s_Hands" % (c if c != "Shadoweave" else "Cindercloth"))
    if [b.get("Id") for b in src["BenchRequirement"]] != ["TODO"]:
        rbad.append("cloth bench " + c)
    ins = [x for x in src["Input"] if not str(x.get("ItemId", "")).startswith("Ingredient_Bar_")]
    for x in ins:
        if x.get("ItemId") == "Ingredient_Bolt_Cindercloth" and c == "Shadoweave":
            x["ItemId"] = "Ingredient_Bolt_Shadoweave"
    if r["Input"] != ins or r["BenchRequirement"] != rcp("Armor_%s_Hands" % col)["BenchRequirement"] or not [x for x in ins if x.get("ItemId") == "Ingredient_Bolt_" + c]:
        rbad.append("wraps " + c)
check(not rbad, "P11 (Monk-Kit-Spec 8.2 VERIFIED): no vanilla spear has a recipe -> bo staff = the metal's sword recipe; gauntlets = the metal's hands armor "
      "(Onyxium = Mithril's with Onyxium bars: the vanilla Onyxium hands asks for Iron bars); wraps = the vanilla cloth hands' bolts + wood (its bench "
      "'TODO' exists nowhere) at the column metal's hands bench, Shadoweave = Cindercloth's with Shadoweave bolts: %s" % rbad)
# --- the RIGHT-CLICK guard on every SkyyArmory weapon (Skyy LOCKED 2026-10-07) except the crossbows (grapple) + kunai (return)
gw = dict((os.path.basename(p)[:-5], d) for p, d in L17_REAL.items())
want_gw = sorted(["Weapon_Wand_" + m for m in MKM] + ["Weapon_Staff_" + m for m in ["Wood"] + MKM] + ["Weapon_Spellbook_" + m for m in MKM])
gbad = [i for i, d in gw.items() if d["Interactions"]["Primary"] == GUARD or d["PlayerAnimationsId"] != {
    "Weapon_Wand": "SkyyArmory_Wand", "Weapon_Staff": "SkyyArmory_Staff", "Weapon_Spellbook": "SkyyArmory_Spellbook"}["_".join(i.split("_")[:2])]]
other_g = [os.path.basename(p)[:-5] for p, d in J.items() if p.startswith("Server/Item/Items/") and (d.get("Interactions") or {}).get("Secondary") == GUARD]
kun = [d["Interactions"]["Secondary"] for p, d in J.items() if os.path.basename(p).startswith("Weapon_Kunai_")]
xbw = [d.get("Interactions") for p, d in J.items() if os.path.basename(p).startswith("Weapon_Crossbow_")]
check(sorted(gw) == want_gw and not gbad and not other_g and all(k.startswith("SkyyArmory_Kunai_Return_") for k in kun) and len(kun) == 8
      and all(GUARD not in json.dumps(x) for x in xbw) and all(MI[i]["Interactions"]["Secondary"] == GUARD for i in MI)
      and aj("root", GUARD)["Interactions"][0]["DefaultValue"] == {"Interactions": ["Common_Guard_Entry_StaminaCondition"]}
      and aj("int", "Common_Guard_Wield")["Effects"]["ItemAnimationId"] == "Guard",
      "P11 (Skyy: 'make sure they can hold right click to block'): right click = the vanilla guard root on the 7 wands, 8 staffs, 7 spellbooks + the "
      "19 Monk items (41); the charged moves stay on the primary hold; the crossbows keep the grapple, the 8 kunai the return: %s %s %s" % (gbad, other_g, kun[:2]))


def chain_anims(a):
    d = aj("anim", a)
    out = dict(d.get("Animations") or {})
    while d.get("Parent"):
        d = aj("anim", d["Parent"])
        for k, v in (d.get("Animations") or {}).items():
            out.setdefault(k, v)
    return out


swa = aj("anim", "Sword")["Animations"]
abad = []
for a, src in (("SkyyArmory_Staff", "Staff"), ("SkyyArmory_Spellbook", "Spellbook"), ("SkyyArmory_Wand", "Wand")):
    v = aj("anim", src)
    d = MANIM[a]
    if dict((k, x) for k, x in d.items() if k != "Animations") != dict((k, x) for k, x in v.items() if k != "Animations") \
            or set(d["Animations"]) != set(v.get("Animations") or {}) | {"Guard", "GuardBash"} \
            or any(d["Animations"][k] != v["Animations"][k] for k in v.get("Animations") or {}) or d["Animations"]["Guard"] != swa["Guard"] \
            or d["Animations"]["GuardBash"] != swa["GuardBash"]:
        abad.append(a)
for src in ("Staff", "Spellbook"):
    if "Guard" in chain_anims(src):
        abad.append(src + " has a Guard now")
vd = aj("anim", "Default")
fd = MANIM["SkyyArmory_Fist"]
fwant = {"JabLeft": ("SwingLeft", 3.0), "JabRight": ("SwingRight", 3.0), "PowerUp": ("SwingUpLeft", 2.0)}
for k, (src, x) in fwant.items():
    e = dict(vd["Animations"][src])
    e["Speed"] = round(float(e.get("Speed", 1.0)) * x, 4)
    if fd["Animations"].get(k) != e:
        abad.append("fist " + k)
if dict((k, x) for k, x in fd["Animations"].items() if k not in fwant) != vd["Animations"] or "Guard" not in fd["Animations"]:
    abad.append("fist copy")
check(not abad and aj("anim", "Wand").get("Parent") == "Sword" and "Guard" in chain_anims("Wand"),
      "P11: SkyyArmory_Staff / _Spellbook / _Wand = the vanilla Staff / Spellbook / Wand set (Staff + Spellbook have no Guard pose) + Sword.json's Guard "
      "+ GuardBash; SkyyArmory_Fist = the vanilla unarmed set (punches + Guard) + JabLeft / JabRight (x3) / PowerUp (x2) copies: %s" % abad)


def mdur(x):
    if isinstance(x, str):
        return mdur(MINT[x])
    if isinstance(x, list):
        return sum(mdur(e) for e in x)
    if not isinstance(x, dict):
        return 0.0
    if x.get("Type") == "Serial":
        return sum(mdur(e) for e in x["Interactions"])
    return float(x.get("RunTime", 0.0)) + (mdur(x["Next"]) if x.get("Next") is not None else 0.0)


def mhits(x, out):
    if isinstance(x, str):
        return mhits(MINT[x], out)
    if isinstance(x, list):
        for e in x:
            mhits(e, out)
    elif isinstance(x, dict):
        if x.get("Type") == "Selector":
            h_ = [MINT[e_] if isinstance(e_, str) else e_ for e_ in x["HitEntity"]["Interactions"]]
            out.append((x["Selector"]["Id"], x["Selector"].get("Distance"), float(h_[0]["DamageCalculator"]["BaseDamage"]["Physical"]),
                        "Knockback" in h_[0].get("DamageEffects", {}), len(h_)))
        for k in ("Next", "Interactions"):
            if x.get(k) is not None:
                mhits(x[k], out)
    return out


sw_iron = aj("item", "Weapon_Sword_Iron")["InteractionVars"]
SWT = [dur(s_, sw_iron, VANI) for s_ in aj("int", "Weapon_Sword_Primary_Chain")["Next"]]
DGT = [dur(s_, aresolve("item", "Weapon_Daggers_Iron").get("InteractionVars") or {}, VANI) for s_ in aj("int", "Weapon_Daggers_Primary_Chain")["Next"]]
sword_click, dagger_click = (SWT[0] + SWT[1]) / 2.0, sum(DGT) / len(DGT)
tbad, hit_ids = [], []
for m in MKM:
    ch = MINT[MROOT["SkyyArmory_Fist_Gauntlets_%s_Primary" % m]["Interactions"][0]]
    st = [mdur(x) for x in ch["Next"]]
    hs = mhits(ch["Next"], [])
    if not (ch["Type"] == "Chaining" and len(st) == 4 and all(dagger_click < x < sword_click for x in st[:3]) and abs(st[0] - (sword_click + dagger_click) / 2.0) < 0.01
            and st[3] - 0.4 >= 0.5 and len(hs) == 4 and [h[2] for h in hs[:3]] == [hs[0][2]] * 3 and abs(hs[3][2] - 2.0 * hs[0][2]) <= 0.11 and hs[3][3]):
        tbad.append(("Gauntlets", m, st, hs))
    hit_ids += [(h[0], h[1], h[4]) for h in hs]
for c, col, k, p in MKW:
    ch = MINT[MROOT["SkyyArmory_Fist_Wraps_%s_Primary" % c]["Interactions"][0]]
    per = [len(MINT[x]["Interactions"]) for x in ch["Next"]]
    st = [mdur(x) for x in ch["Next"]]
    hs = mhits(ch["Next"], [])
    if not (sum(per) == p and all(n == k for n in per[:-1]) and 1 <= per[-1] <= k and all(abs(st[i] - per[i] * 0.1) < 1e-9 for i in range(len(st)))
            and len(hs) == p and all(not h[3] for h in hs[:-1]) and hs[-1][3] and hs[-1][2] > hs[0][2] and len(set(h[2] for h in hs[:-1])) == 1):
        tbad.append(("Wraps", c, per, st, hs))
    hit_ids += [(h[0], h[1], h[4]) for h in hs]
check(not tbad and set(hit_ids) == {("Raycast", 3, 1)} and len(hit_ids) == 28 + sum(p for c, col, k, p in MKW),
      "P11 (Skyy's fist locks): gauntlets = 1 jab per click, a chain of 4, every jab between the vanilla sword (%.3f s) and dagger (%.3f s) click (the "
      "midway %.3f s), a 2x finisher with a knock-up and a gap >= 0.5 s after it; wraps = Linen / Cotton 2 jabs per click power on 6, Silk 2 / 4, "
      "Cindercloth 3 / 6, Shadoweave 5 / 5, 0.1 s a jab, no gap after the power hit; every jab = ONE Raycast pick (a single target, 3 blocks): %s" % (
          sword_click, dagger_click, (sword_click + dagger_click) / 2.0, tbad[:2]))
# fixer 2 (critic: the gauntlet pause cleared stun.gap by 8 ms): the hit-to-hit times of nonstop gauntlet clicking, read off the jar's chain
# (a hit lands after its step's wind-up); R11b replays them with 2 server ticks of jitter against the real stun.gap
gch_ = MINT[MROOT["SkyyArmory_Fist_Gauntlets_Iron_Primary"]["Interactions"][0]]["Next"]
gst_ = [mdur(x) for x in gch_]
gw_ = [float((MINT[x] if isinstance(x, str) else x).get("RunTime", 0.0)) for x in gch_]
gt_, ghit_ = 0.0, []
for c_ in range(2):
    for i_ in range(len(gch_)):
        ghit_.append(gt_ + gw_[i_])
        gt_ += gst_[i_]
GSPAM_IV = [round(ghit_[i_ + 1] - ghit_[i_], 4) for i_ in range(len(gch_))]
check(len(GSPAM_IV) == 4 and max(GSPAM_IV[:3]) < 0.4 and GSPAM_IV[3] > 0.95,
      "P11 (fixer 2): nonstop gauntlet clicking lands its hits %s s apart - three quick jabs, then the finisher pause before the next jab" % GSPAM_IV)


def sword_dps(m):
    iv = aj("item", "Weapon_Sword_" + m)["InteractionVars"]
    d = sum(float(iv[k]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Physical"]) for k in ("Swing_Left_Damage", "Swing_Right_Damage", "Swing_Down_Damage"))
    return d / sum(SWT)


shares = {}
for m in MKM:
    bo = MI["Weapon_Bo_" + m]["InteractionVars"]
    bh = [float(bo["Spear_Swing_%s_Damage" % s]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Physical"]) for s in ("Left", "Right")]
    shares["bo " + m] = (bh[0] / tap_s) / sword_dps(m) if bh[0] == bh[1] else -1
    ch = MINT[MROOT["SkyyArmory_Fist_Gauntlets_%s_Primary" % m]["Interactions"][0]]
    shares["gauntlets " + m] = sum(h[2] for h in mhits(ch["Next"], [])) / sum(mdur(x) for x in ch["Next"]) / sword_dps(m)
for c, col, k, p in MKW:
    ch = MINT[MROOT["SkyyArmory_Fist_Wraps_%s_Primary" % c]["Interactions"][0]]
    shares["wraps " + c] = sum(h[2] for h in mhits(ch["Next"], [])) / sum(mdur(x) for x in ch["Next"]) / sword_dps(col)
sbad2 = dict((k, round(v, 3)) for k, v in shares.items() if abs(v - {"bo": 0.82, "gauntlets": 0.9, "wraps": 0.95}[k.split()[0]]) > 0.03)
gj = dict((m, mhits(MINT[MROOT["SkyyArmory_Fist_Gauntlets_%s_Primary" % m]["Interactions"][0]]["Next"], [])[0][2]) for m in MKM)
wj = dict((c, mhits(MINT[MROOT["SkyyArmory_Fist_Wraps_%s_Primary" % c]["Interactions"][0]]["Next"], [])[0][2]) for c, col, k, p in MKW)
check(not sbad2 and all(gj[col] > wj[c] for c, col, k, p in MKW),
      "P11: DPS vs the same-metal vanilla sword's tap chain within 0.03 of bo 0.82 / gauntlets 0.9 / wraps 0.95 (Monk-Kit-Spec; the 0.1 rounding), "
      "gauntlets hit harder per hit than the wraps of their band: %s" % (sbad2 or dict((k, round(v, 3)) for k, v in sorted(shares.items()))))
lang11 = JZ.read("Server/Languages/en-US/server.lang").decode("utf-8")
lbad = [i for i in MI if ("items.%s.name = " % i) not in lang11 or ("items.%s.description = " % i) not in lang11
        or "Right click: block." not in lang11.split("items.%s.description = " % i)[1].split("\n")[0]]
gl11 = [os.path.basename(p_)[:-5] for p_ in L17_REAL]
gl11b = [i for i in gl11 if lang11.count("items.%s.description = " % i) != 1
         or not lang11.split("items.%s.description = " % i)[1].split("\n")[0].endswith(" Right click: block.")]
check(not gl11b and len(gl11) == 22, "P11 (fixer, critic: the old descriptions never mentioned blocking): the 22 wands / staffs / spellbooks' "
      "one description line ends with 'Right click: block.': %s" % gl11b)
check(not lbad and "items.Weapon_Bo_Copper.name = Copper Bo Staff" in lang11 and "items.Weapon_Fist_Wraps_Linen.name = Linen Hand Wraps" in lang11
      and "items.Weapon_Fist_Gauntlets_Onyxium.name = Onyxium Gauntlets" in lang11, "P11: names + descriptions (right click: block) for the 19 items: %s" % lbad)
# --- the art the jar ships: tools/art/make_staffs.py (Bo) + make_fists.py run again here = the jar bytes; held R-Attachment pieces
sys.path.insert(0, os.path.join(TOOLS, "art"))
import make_staffs as MS11
import make_fists as MF11
z11 = SA.assets()
bod, bom, _bt11, _bi11 = SA.item_parts(z11, MS11.BO_ITEM)
bov = json.loads(bom.decode("utf-8-sig"))
art_bad = []
for m in MKM:
    md = MS11.bo_model(bov, m)
    pl, ht = MS11.pack(md)
    tx = MS11.bo_texture(z11, m, md, pl, ht, MS11.tier_colours(z11, m))
    ic = SA.render_icon(md, tx, bod["IconProperties"], 64)
    if [JZ.read("Common/Items/Weapons/Staff/SkyyArmory_Bo_%s%s" % (m, s)) for s in (".blockymodel", "_Texture.png")] + \
            [JZ.read("Common/Icons/ItemsGenerated/SkyyArmory_Bo_%s.png" % m)] != [(json.dumps(md, indent=2) + "\n").encode("utf-8"), tx, ic]:
        art_bad.append("Bo " + m)
for fam, tiers in (("Gauntlets", MKM), ("Wraps", [c for c, col, k, p in MKW])):
    bs = [MF11.build_gauntlets(t) if fam == "Gauntlets" else MF11.build_wraps(t) for t in tiers]
    mds = [b.model() for b in bs]
    hts = [MF11.pack(md) for md in mds]
    props = MF11.fit_props(mds, MF11.ICON_ROT)
    for t, b, md, ht in zip(tiers, bs, mds, hts):
        if fam == "Gauntlets":
            met, gold = MF11.wand_metal(z11, t)
            pal = {"metal": met, "gold": gold, "gem": SA.gem_gradient(z11, t), "gold_trim": t in MF11.GOLD_TIERS, "rivets": t != "Copper", "vplate": t == "Cobalt"}
        else:
            pal = {"cloth": MF11.cloth_gradient(z11, t), "stitched": t in MF11.STITCHED}
        tx = SA.png_encode(MF11.Tex(md, ht, b.kind, pal, sum(ord(ch_) for ch_ in "SkyyArmory_Fist_%s_%s" % (fam, t)), MF11.ICON_ROT).img)
        ic = SA.render_icon(md, tx, props, 64)
        got = [JZ.read("Common/Items/Weapons/Fist/SkyyArmory_%s_%s%s" % (fam, t, s)) for s in (".blockymodel", "_Texture.png")] + \
              [JZ.read("Common/Icons/ItemsGenerated/SkyyArmory_Fist_%s_%s.png" % (fam, t))]
        if got != [(json.dumps(md, indent=2) + "\n").encode("utf-8"), tx, ic] or MI["Weapon_Fist_%s_%s" % (fam, t)]["IconProperties"] != props \
                or md["nodes"][0]["name"] != "R-Attachment" or not md["nodes"][0]["shape"]["settings"].get("isPiece"):
            art_bad.append("%s %s" % (fam, t))
z11.close()
check(not art_bad and len(L17_PNG) == 2 * 19, "P11 (art at build time, vanilla-derived bytes only in the jar): make_staffs.py Bo + make_fists.py gauntlets / "
      "wraps run again here = the jar's 19 models / textures / icons, the item IconProperties = the generator's family fit, held R-Attachment pieces: %s" % art_bad)
print("P11. 0.1.7 Monk weapons: 19 items, recipes, guard on 41 items, 4 animation sets, timings (sword %.3f / dagger %.3f -> gauntlet %.3f), one target, "
      "shares %s, art" % (sword_click, dagger_click, (sword_click + dagger_click) / 2.0, dict((k, round(v, 2)) for k, v in sorted(shares.items()))))
'''
hrep('''PY_OKS, PY_FAILS = OKS[0], len(FAILS)
print("PYTHON PART: %d ok, %d FAIL" % (PY_OKS, PY_FAILS))''', P11 + '''PY_OKS, PY_FAILS = OKS[0], len(FAILS)
print("PYTHON PART: %d ok, %d FAIL" % (PY_OKS, PY_FAILS))''')
hrep('''        _d17["PlayerAnimationsId"] = {"SkyyArmory_Staff": "Staff", "SkyyArmory_Spellbook": "Spellbook"}.get(''',
     '''        _d17["PlayerAnimationsId"] = {"SkyyArmory_Staff": "Staff", "SkyyArmory_Spellbook": "Spellbook", "SkyyArmory_Wand": "Wand"}.get(''')

# ---- R11 (JVM, after R10): every 0.1.7 path EXECUTED
R11 = r'''    # ============================================================================ R11. 0.1.7 MONK WEAPONS + BLOCK + STUNLOCK + NO VOID - every new path EXECUTED
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    ST_ = JClass(PKG + "Stun")
    DENTc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    GUARD = "Root_Common_Guard_Entry_StaminaCondition"
    # --- R11a: the animation sets through the engine codec (the vanilla sets first: a Parent is read from the store), the fist roots compiled
    IPAc = JClass("com.hypixel.hytale.server.core.asset.type.itemanimation.config.ItemPlayerAnimations")
    abad11, akeys = [], {}

    def anim_keys(o_):
        m_ = o_.getAnimations()
        return set() if m_ is None else set(str(k_) for k_ in m_.keySet())
    if AR.getAssetStore(IPAc.class_) is None:
        abad11.append("no ItemPlayerAnimations store")
    else:
        for grp_ in (("Item", "Staff", "Default", "Sword"), ("Spellbook", "Wand")):
            objs_ = []
            for a_ in grp_:
                o_, w_ = dec(IPAc, a_, json.dumps(aj("anim", a_)))
                if o_ is None or w_:
                    abad11.append("vanilla %s: %s" % (a_, w_))
                else:
                    objs_.append(o_)
                    akeys[a_] = anim_keys(o_)
            load(IPAc, objs_, "Hytale:Hytale")
        objs_ = []
        for a_ in sorted(MANIM):
            o_, w_ = dec(IPAc, a_, json.dumps(MANIM[a_]))
            if o_ is None or w_:
                abad11.append("%s: %s" % (a_, w_))
            else:
                objs_.append(o_)
                akeys[a_] = anim_keys(o_)
        load(IPAc, objs_, PACK)
        for a_ in sorted(MANIM):
            if IPAc.getAssetMap().getAsset(a_) is None or str(IPAc.getAssetMap().getAssetPack(a_)) != PACK:
                abad11.append("%s is not in the store from our pack" % a_)
    check(not abad11 and all({"Guard", "GuardBash"} <= akeys.get(a_, set()) for a_ in ("SkyyArmory_Staff", "SkyyArmory_Spellbook", "SkyyArmory_Wand"))
          and {"Guard", "JabLeft", "JabRight", "PowerUp", "SwingLeft", "SwingUpLeft"} <= akeys.get("SkyyArmory_Fist", set()) and "CastSummonCharged" in akeys.get("SkyyArmory_Staff", set())
          and "Guard" not in akeys.get("Staff", {"Guard"}),
          "R11a: the 4 animation sets decode through ItemPlayerAnimations' engine codec (no unknown key) into the store from our pack - every one has "
          "Guard + GuardBash (the fist set: the unarmed Guard + the jabs), the staff set keeps the vanilla casts; vanilla Staff has no Guard: %s %s" % (
              abad11[:3], dict((k_, len(v_)) for k_, v_ in akeys.items())))
    print("R11a. NOTE (evidence, engine decode): the vanilla Wand set decoded alone holds %d entries, Guard %s - its Sword parent is merged %s"
          % (len(akeys.get("Wand", ())), "Guard" in akeys.get("Wand", ()), "at decode" if "Guard" in akeys.get("Wand", ()) else "later (client / lookup): ours names it itself"))
    # the vanilla guard root our right click names: its whole vanilla closure loaded, then compiled (0 missing)
    need11 = set()

    def clos11(x):
        if isinstance(x, str):
            if x in INTS_ALL and x not in need11 and INTc.getAssetMap().getAsset(x) is None:
                need11.add(x)
                clos11(INTS_ALL[x])
                p_ = INTS_ALL[x].get("Parent") if isinstance(INTS_ALL[x], dict) else None
                if p_:
                    clos11(p_)
        elif isinstance(x, list):
            for e_ in x:
                clos11(e_)
        elif isinstance(x, dict):
            for k_, v_ in x.items():
                if k_ not in ("Type", "$Comment"):
                    clos11(v_)
    clos11(ROOTS_ALL[GUARD])
    vi11, vb11, pend11 = {}, [], sorted(need11)
    for _r in range(12):
        nxt_, got_ = [], []
        for i_ in pend11:
            d_ = aj("int", i_)
            if d_.get("Parent") and d_["Parent"] in need11 and d_["Parent"] not in vi11:
                nxt_.append(i_)
                continue
            o_, w_ = dec(INTc, i_, json.dumps(d_))
            if o_ is None:
                vb11.append((i_, w_))
            else:
                vi11[i_] = o_
                got_.append(i_)
        load(INTc, [vi11[i_] for i_ in got_], "Hytale:Hytale")
        pend11 = nxt_
        if not pend11:
            break
    if ROOTc.getAssetMap().getAsset(GUARD) is None:
        o_, w_ = dec(ROOTc, GUARD, json.dumps(ROOTS_ALL[GUARD]))
        load(ROOTc, [o_], "Hytale:Hytale")
    n_m0 = len([m_ for lv_, m_ in records() if "Missing interaction" in m_])
    res_g = compile_root(GUARD)
    cls_g = [cn_ for cn_, iid_ in res_g["ops"] if iid_ is not None]
    cbad11 = []
    for rid_ in sorted(L17_ROOTS):
        res_ = compile_root(rid_)
        cls_ = [cn_ for cn_, iid_ in res_["ops"] if iid_ is not None]
        if res_["bad"] or "ChainingInteraction" not in cls_ or "SelectInteraction" not in cls_:
            cbad11.append((rid_, res_["bad"][:2], cls_[:8]))
    n_m1 = len([m_ for lv_, m_ in records() if "Missing interaction" in m_])
    gw11 = [i_ for i_ in ("Common_Guard_Entry_StaminaCondition", "Common_Guard_Wield") if INTc.getAssetMap().getAsset(i_) is None]
    check(not [x_ for x_ in vb11 if x_[0] not in ("Common_Guard_Shove_Hit", "Common_Guard_Shove_Selector")] and not gw11 and not res_g["bad"]
          and not cbad11 and n_m1 == n_m0 and len(L17_ROOTS) == 12,
          "R11a: RootInteraction.build() on the real stores - the vanilla guard root compiles (its StatsCondition entry + the Wielding guard decode + "
          "load; the 0-damage shove pair needs other modules' codecs in a bare JVM - NOTE %s); every fist root compiles to Chaining -> Simple -> Select "
          "(the Raycast pick) with its inline steps as contained assets and 0 missing interactions: %s %s %s %s" % (
              [x_[0] for x_ in vb11], gw11, res_g["bad"][:2], cls_g[:4], cbad11[:2]))
    # SkyyGear (the pinned jar on this classpath) and SkyyClasses 0.1.13 read our ids - the proof of what they need
    gband = dict((i_, [int(x_) for x_ in GLvl.band(i_)]) for i_ in ("Weapon_Bo_Copper", "Weapon_Bo_Onyxium", "Weapon_Fist_Gauntlets_Copper",
                                                                    "Weapon_Fist_Gauntlets_Mithril", "Weapon_Fist_Wraps_Linen", "Weapon_Fist_Wraps_Cindercloth",
                                                                    "Weapon_Fist_Wraps_Shadoweave"))
    gslot = [int(GData.slotOf(i_)) for i_ in sorted(L17_ITEMS)]
    check(gband["Weapon_Bo_Copper"][:2] == [10, 18] and gband["Weapon_Bo_Onyxium"][:2] == [40, 49] and gband["Weapon_Fist_Gauntlets_Copper"][:2] == [10, 18]
          and gband["Weapon_Fist_Gauntlets_Mithril"][:2] == [40, 49] and gband["Weapon_Fist_Wraps_Linen"][:2] == [10, 17]
          and gband["Weapon_Fist_Wraps_Cindercloth"][:2] == [30, 37] and gband["Weapon_Fist_Wraps_Shadoweave"] == [35, 35, 2]
          and set(gslot) == {0} and not any(bool(GData.isSpell(i_)) for i_ in L17_ITEMS),
          "R11a (SkyyGear's own code on our ids): the bands come from the metal word (bo / gauntlets) or SkyyGear's cloth rows (Linen 10-17 ... "
          "Cindercloth 30-37); Shadoweave has no SkyyGear row -> the item level 35 (exact; add 'level.material.Shadoweave' in Server Setup for a "
          "band); every Monk item is a gear WEAPON (slot 0, never a spell): %s %s" % (gband, sorted(set(gslot))))
    CLJ13b = os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.13.jar")
    own11 = None
    if os.path.isfile(CLJ13b):
        ucl_ = JClass("java.net.URLClassLoader")(JArray(JClass("java.net.URL"))([JClass("java.io.File")(CLJ13b).toURI().toURL()]), sysl)
        CDc_ = JClass("java.lang.Class").forName("com.skyy.classes.ClassDefs", True, ucl_)
        mo_ = CDc_.getMethod("ownerOf", JClass("java.lang.String").class_)
        own11 = sorted(set(int(mo_.invoke(None, i_)) for i_ in L17_ITEMS))
    check(own11 == [-2],
          "R11a (SkyyClasses 0.1.13's own ClassDefs.ownerOf): every Monk weapon falls under the 'Weapon_' catch-all (owner -2 = no class yet): blocked "
          "for players WITH a class while classes.unassignedBlocked is on - the Assassin kunai pattern until the Monk class exists: %s" % own11)
    print("R11a. animation sets + guard root + fist roots compiled; SkyyGear bands %s; SkyyClasses owner %s" % (gband, own11))

    # --- R11b. THE STUNLOCK BREAKOUT (Skyy LOCKED 2026-10-07): plain values first
    WR, ROLE = "Weapon_Fist_Wraps_Linen", "Trork_Chieftain"
    U1, U2 = UUID.fromString("00000000-0000-0000-0099-000000000001"), UUID.fromString("00000000-0000-0000-0099-000000000002")
    UX = [UUID.fromString("00000000-0000-0000-0099-00000000001%d" % n_) for n_ in range(6)]

    def first_break(who, step=200, until=30000, item=WR, role=ROLE, key="b"):
        ST_.BY.clear()
        t_ = 0
        while t_ <= until:
            for w_ in who:
                if bool(ST_.onHit(key, w_, item, role, t_)):
                    return t_
            t_ += step
        return None
    fb1 = first_break([U1])
    fb2 = first_break([U1, U2])
    fb6 = first_break(UX)
    fbg = first_break([U1], step=1200)
    fbn = first_break([U1], role="Skeleton_Fighter")
    fbs = first_break([U1], item="Weapon_Sword_Iron")
    fbo = first_break([U1], item="Weapon_Bo_Copper")
    fbG = first_break([U1], item="Weapon_Fist_Gauntlets_Iron")
    need_ = [int(ST_.needMs(n_)) for n_ in (0, 1, 2, 3, 4, 9)]
    check(fb1 == 3000 and fb2 == 6000 and fb6 == 12000 and fbg is None and fbn is None and fbs is None and fbo == 3000 and fbG == 3000
          and need_ == [3000, 3000, 6000, 9000, 12000, 12000],
          "R11b (Skyy: 'if 2 people are spamming the boss the time doubles to 6 seconds'): nonstop Monk combo hits on a boss break out after 3 s with 1 "
          "player, 6 s with 2, 12 s with 6 (cap 4); hits 1.2 s apart (> stun.gap 0.8) never; a Skeleton_Fighter never; a sword never; a bo staff / "
          "gauntlets count: %s %s" % ((fb1, fb2, fb6, fbg, fbn, fbs, fbo, fbG), need_))
    # the window: after the break combo hits do nothing for stun.window 1.5 s, then a new count; the boss hitting back ends it at once
    ST_.BY.clear()
    seq_ = [(t_, bool(ST_.onHit("w", U1, WR, ROLE, t_))) for t_ in range(0, 9001, 200)]
    cans_ = [t_ for t_, c_ in seq_ if c_]
    ign0 = int(ST_.IGNORED)
    ST_.BY.clear()
    for t_ in range(0, 3001, 200):
        ST_.onHit("h", U1, WR, ROLE, t_)
    back_ = bool(ST_.bossHit("h", 3100))
    after_ = [bool(ST_.onHit("h", U1, WR, ROLE, t_)) for t_ in range(3200, 6201, 200)]
    check(cans_[:9] == [3000, 3200, 3400, 3600, 3800, 4000, 4200, 4400, 7600] and back_ and not any(after_[:-1]) and after_[-1]
          and not bool(ST_.bossHit("nobody", 1)),
          "R11b: from the break at 3 s the combo hits do nothing until 4.5 s (stun.window 1.5), the next hit starts a new count (break again at 7.6 s); "
          "the boss hitting a player (bossHit) ends it at once - a new 3 s count from the next hit: %s / %s" % (cans_[:10], after_))
    ACfg.STUN_PER = 2.5
    ACfg.STUN_MAX = 2
    fb_c = (first_break([U1]), first_break(UX))
    ACfg.STUN_BOSS = "Skeleton"
    fb_w = first_break([U1], role="Skeleton_Fighter")
    ACfg.PART_STUN = False
    fb_off = first_break([U1])
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    check(fb_c == (2600, 5000) and fb_w == 2600 and fb_off is None,
          "R11b: the rows drive it - stun.perPlayer 2.5 + stun.maxPlayers 2 -> 2.6 s (the first 200 ms hit past 2.5 s) / 5 s for 6 players; "
          "stun.bossWords 'Skeleton' -> a Skeleton_Fighter breaks out; part.stun off -> never: %s %s %s" % (fb_c, fb_w, fb_off))
    # the engine glue on REAL Damage objects (Damage$EntitySource = melee; the harness stores): player -> boss melee, boss -> player
    boss11 = mob(7701, 3.0, 64.0, 0.5, (1.0, 2.0, 1.0), role=ROLE)
    grunt11 = mob(7702, 3.0, 64.0, 2.5, (0.6, 1.8, 0.6), role="Skeleton_Fighter")
    ST_.HAND = HashMap()
    ST_.HAND.put(cu, WR)
    ST_.BY.clear()
    t0_ = nowms()
    for k_ in range(15):
        ST_.onHit(boss11, cu, WR, ROLE, t0_ - 3400 + 200 * k_)          # a stunlock running for 3.4 s (the last hit 0.6 s ago)
    d1_ = DMGc(DENTc(rc), 0, JFloat(10.0))
    ST_.filter(tbuf, boss11, d1_)
    d1b_ = DMGc(DENTc(rc), 0, JFloat(10.0))
    ST_.filter(tbuf, boss11, d1b_)
    d2_ = DMGc(DENTc(boss11), 0, JFloat(5.0))
    ST_.filter(tbuf, rc, d2_)
    gone_ = not bool(ST_.BY.containsKey(boss11))
    d3_ = DMGc(DENTc(rc), 0, JFloat(10.0))
    ST_.filter(tbuf, boss11, d3_)
    for k_ in range(15):
        ST_.onHit(grunt11, cu, WR, "Skeleton_Fighter", t0_ - 3400 + 200 * k_)
    d4_ = DMGc(DENTc(rc), 0, JFloat(10.0))
    ST_.filter(tbuf, grunt11, d4_)
    ST_.BY.clear()
    for k_ in range(15):
        ST_.onHit(boss11, cu, WR, ROLE, t0_ - 3400 + 200 * k_)
    d5_ = DMGc(DPS(rc, REFc(tst, 7799)), 0, JFloat(10.0))
    ST_.filter(tbuf, boss11, d5_)
    ST_.HAND.put(cu, "Weapon_Sword_Iron")
    d6_ = DMGc(DENTc(rc), 0, JFloat(10.0))
    ST_.filter(tbuf, boss11, d6_)
    ST_.HAND.put(cu, WR)
    ST_.BY.clear()
    d0_ = DMGc(DENTc(rc), 0, JFloat(0.0))          # fixer: the guard shove (0 damage) with wraps in hand
    ST_.filter(tbuf, boss11, d0_)
    shove11 = (int(ST_.BY.size()), bool(d0_.isCancelled()))
    ST_.onHit(boss11, cu, WR, ROLE, t0_)
    d0b_ = DMGc(DENTc(rc), 0, JFloat(10.0))
    ST_.filter(tbuf, boss11, d0b_)
    check(shove11 == (0, False) and int(ST_.BY.size()) == 1,
          "R11b (fixer, critic note): a 0-damage guard shove from a player holding wraps starts no stunlock record and is left alone; a real "
          "10-damage jab does count: %s size %s" % (shove11, ST_.BY.size()))
    ST_.BY.clear()
    eng11 = (bool(d1_.isCancelled()), bool(d1b_.isCancelled()), bool(d2_.isCancelled()), gone_, bool(d3_.isCancelled()), bool(d4_.isCancelled()),
             bool(d5_.isCancelled()), bool(d6_.isCancelled()))
    check(eng11 == (True, True, False, True, False, False, False, False),
          "R11b (engine glue, real Damage objects): a player's melee hit (Damage$EntitySource) on the boss after a 3.4 s stunlock is CANCELLED (the "
          "breakout) and the next one too (the window); the boss's own hit on that player goes through and ends the record; the next combo hit counts "
          "again (not cancelled); a Skeleton_Fighter / a projectile hit / a sword in hand are left alone: %s" % (eng11,))
    # ArmoryTuneSys (the Filter group) is the caller: its handle runs Stun.filter on the hit entity of the chunk
    tune11 = calls_of(PKG + "ArmoryTuneSys", "handle")
    chk_run = None
    try:
        TCh11 = stub("TChunk11", "com.hypixel.hytale.component.ArchetypeChunk", ["public static com.hypixel.hytale.component.Ref R = null;"],
                     ["public com.hypixel.hytale.component.Ref getReferenceTo(int i) { return R; }"])
        ch11 = U.allocateInstance(TCh11.class_)
        TCh11.R = boss11
        ST_.BY.clear()
        t0_ = nowms()          # fixer 2: a fresh clock (the stub compile above can take longer than the 0.2 s left of the 0.8 s gap)
        for k_ in range(15):
            ST_.onHit(boss11, cu, WR, ROLE, t0_ - 3400 + 200 * k_)
        d7_ = DMGc(DENTc(rc), 0, JFloat(10.0))
        JClass(PKG + "ArmoryTuneSys")(True).handle(0, ch11, tst, tbuf, d7_)
        chk_run = bool(d7_.isCancelled())
    except Exception as e_:
        chk_run = "stub: " + str(e_)[:120]
    check("filter" in tune11 and chk_run is True,
          "R11b (wiring): ArmoryTuneSys.handle calls Stun.filter (bytecode) and, run on a chunk whose entity is the stunlocked boss, cancels the "
          "player's melee hit: %s / %s" % ("filter" in tune11, chk_run))
    ST_.BY.clear()
    ST_.HAND = None
    # --- fixer 2 (critics): the boss words match whole parts of the role name (Snapdragon is a plain mob)
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    tok11 = [bool(ST_.bossRole(r_, ACfg.STUN_BOSS)) for r_ in ("Snapdragon", "Dragon_Fire", "Test_Boss_Basic", "Golem_Crystal_Earth", "Yeti",
                                                                "Trork_Chieftain", "Goblin_Ogre", "Rex_Cave", "Skeleton_Fighter", "Trork_Warrior")]
    tokm = (bool(ST_.bossRole("Trork_Chieftain", "trork_chieftain")), bool(ST_.bossRole("Trork_Chieftain", "Chief")), bool(ST_.bossRole(None, "Boss")),
            bool(ST_.bossRole("Yeti", " , ")))
    fbsd = first_break([U1], role="Snapdragon")
    fbdf = first_break([U1], role="Dragon_Fire")
    check(tok11 == [True if i_ in range(1, 8) else False for i_ in range(10)] and tokm == (True, False, False, False) and fbsd is None and fbdf == 3000,
          "R11b (fixer 2, critic): a boss word matches a WHOLE part of the role name - Snapdragon (a plain Assets.zip mob) never breaks out, "
          "Dragon_Fire / Test_Boss_Basic / the Golems / Yeti / Trork_Chieftain / Goblin_Ogre / Rex_Cave do; multi-part words work, 'Chief' does not "
          "match Chieftain: %s %s %s %s" % (tok11, tokm, fbsd, fbdf))

    # --- fixer 2 (critic): stun.gap 0.8 vs the jar's own timings with 2 server ticks (30 TPS) of jitter against us
    def replay(ivs, item, until=20000):
        ST_.BY.clear()
        t_, i_ = 0.0, 0
        while t_ <= until:
            if bool(ST_.onHit("rp", U1, item, ROLE, int(round(t_)))):
                return int(round(t_))
            t_ += ivs[i_ % len(ivs)] * 1000.0
            i_ += 1
        return None
    TK2 = 2.0 / 30.0
    gpause = max(GSPAM_IV)
    g_worst = [x_ - TK2 if x_ == gpause else x_ + TK2 for x_ in GSPAM_IV]       # the jabs 2 ticks late, the finisher pause 2 ticks short
    rp11 = (replay(g_worst, "Weapon_Fist_Gauntlets_Iron"), replay([tap_s + TK2], "Weapon_Bo_Copper"), replay([0.1 + TK2], WR),
            replay([x_ + TK2 for x_ in GSPAM_IV[:3]], "Weapon_Fist_Gauntlets_Iron"))
    check(abs(float(ACfg.STUN_GAP) - 0.8) < 1e-9 and rp11[0] is None and rp11[1] is not None and 3000 <= rp11[1] <= 3700
          and rp11[2] is not None and rp11[2] <= 3200 and rp11[3] is not None and rp11[3] <= 3500,
          "R11b (fixer 2, critic: 8 ms margin): with stun.gap 0.8, nonstop gauntlets (hits %s s apart, the jabs 2 ticks late and the finisher pause "
          "2 ticks short) never stunlock a boss - the pause starts the count over; nonstop bo taps (%.3f s + 2 ticks), wrap jabs and gauntlet jabs "
          "that never reach the finisher still break out at about 3 s: %s" % (GSPAM_IV, tap_s, rp11))

    # --- fixer 2 (critic: a cancelled hit still shoves the boss): the breakout-window hit drops the knockback DamageEntityInteraction queued
    KBCc = JClass("com.hypixel.hytale.server.core.entity.knockback.KnockbackComponent")
    kbt = KBCc.getComponentType()
    ST_.HAND = HashMap()
    ST_.HAND.put(cu, WR)
    ST_.BY.clear()
    t1_ = nowms()
    for k_ in range(15):
        ST_.onHit(boss11, cu, WR, ROLE, t1_ - 3400 + 200 * k_)
    put(boss11, kbt, KBCc())
    u0_ = int(ST_.UNKNOCKED)
    dk1_ = DMGc(DENTc(rc), 0, JFloat(10.0))
    ST_.filter(tbuf, boss11, dk1_)
    kb1 = (bool(dk1_.isCancelled()), comp(boss11, kbt) is None, int(ST_.UNKNOCKED) - u0_)
    ST_.BY.clear()
    put(boss11, kbt, KBCc())
    dk2_ = DMGc(DENTc(rc), 0, JFloat(10.0))
    ST_.filter(tbuf, boss11, dk2_)
    kb2 = (bool(dk2_.isCancelled()), comp(boss11, kbt) is not None)
    tbuf.tryRemoveComponent(boss11, kbt)
    ST_.BY.clear()
    ST_.HAND = None
    check(kbt is not None and kb1 == (True, True, 1) and kb2 == (False, True) and "noKnock" in calls_of(PKG + "Stun", "filter")
          and "tryRemoveComponent" in calls_of(PKG + "Stun", "noKnock"),
          "R11b (fixer 2, critic): a breakout-window hit is cancelled AND drops the KnockbackComponent the hit queued (Stun.noKnock -> "
          "CommandBuffer.tryRemoveComponent), so the boss is not shoved; a normal combo hit keeps its knockback: %s %s" % (kb1, kb2))
    print("R11b. stunlock: 3 / 6 / 12 s, gap, window, boss hit, bosses + Monk weapons only, rows, part off; real Damage objects + ArmoryTuneSys")

    # --- R11c. NO VOID PROTECTION (Skyy LOCKED 2026-10-07): the hop / leap hop full over the void, the kunai over the void, the rows gone
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    AT.GRID = Grid(lambda x, y, z: 0)          # no ground anywhere
    put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    mc.setStatValue(STAM, JFloat(10.0))
    mc.setStatValue(MANA, JFloat(200.0))
    TJ(2, cu, "trav-test", tst, None, JArray(JDouble)([0.0, 0.0, 1.0]), I_IRON).run()
    hv11 = last_instr(rc)
    why11 = str(AT.LAST_WHY)
    pr11 = Props()
    pr11.setProperty("hop.groundCheck", "6")
    ACfg.apply(pr11)
    mc.setStatValue(STAM, JFloat(10.0))
    TJ(2, cu, "trav-test", tst, None, JArray(JDouble)([0.0, 0.0, 1.0]), I_IRON).run()
    hv11b = last_instr(rc)
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    lh11 = LP.hopNow(tbuf, rc, JArray(JDouble)([0.0, 0.0, 1.0]), 30.0)
    lh11 = None if lh11 is None else [round(float(x_), 3) for x_ in lh11]
    kv11 = kvoid()
    rows11 = [str(k_) for k_ in JClass(PKG + "CfgRows").KEYS]
    fld11 = [str(f_.getName()) for f_ in ACfg.class_.getFields()]
    dcfg11 = str(ACfg.DEF_CFG)
    check(hv11 is not None and hv11[0] == (0.0, 0.0, -30.0) and why11.startswith("hop full") and hv11b is not None and hv11b[0] == (0.0, 0.0, -30.0)
          and lh11 is not None and lh11[:3] == [0.0, 0.0, -30.0] and lh11[4] == 1.0 and kv11 is not None and kv11[0] >= 9.5
          and "hop.groundCheck" not in rows11 and "kunai.floorCheck" not in rows11 and "HOP_GROUND" not in fld11 and "K_FLOOR" not in fld11
          and "hop.groundCheck" not in dcfg11 and "kunai.floorCheck" not in dcfg11 and "\nblink.floorCheck=0\n" in dcfg11 and "blink.floorCheck" in rows11
          and int(ACfg.BLINK_FLOOR) == 0,
          "R11c (Skyy: 'dont put any void protection on any traversal'): over open void the wand hop pushes the FULL 30 (a leftover hop.groundCheck=6 "
          "line changes nothing), the leap hop is full too, a teleport kunai lands where it was over the void; the rows hop.groundCheck + "
          "kunai.floorCheck are gone (kit, loader, default file); blink.floorCheck keeps its row at 0: %s %s %s %s %s" % (hv11, why11, hv11b, lh11, kv11))
    AT.GRID = Grid(world_fn())
    print("R11c. no void protection: hop / leap / kunai full over the void, the two rows gone, blink.floorCheck 0 kept")

    # --- R11d. THE ROWS: the 6 stunlock rows + 20 read-only rows, the loader clamps, armory:stun, the default file
    Rows11 = JClass(PKG + "CfgRows")
    k11 = [str(k_) for k_ in Rows11.KEYS]
    d11 = dict(zip(k11, [str(d_) for d_ in Rows11.DEFS]))
    t11 = dict(zip(k11, [str(d_) for d_ in Rows11.TYPES]))
    f11 = dict(zip(k11, [str(d_) for d_ in Rows11.FLAGS]))
    want11 = {"part.stun": "true", "stun.perPlayer": "3", "stun.maxPlayers": "4", "stun.gap": "0.8", "stun.window": "1.5",
              "stun.bossWords": "Boss,Guardian,Duke,Dragon,Chieftain,Elite,Hedera,Rex,Ogre,Golem,Yeti"}
    bad11 = dict((k_, (d11.get(k_), v_)) for k_, v_ in want11.items() if d11.get(k_) != v_)
    fx11 = [k_ for k_ in k11 if k_ == "fixed.guard" or k_.startswith(("fixed.bo.", "fixed.fist."))]
    check(not bad11 and t11["part.stun"] == "bool" and t11["stun.bossWords"] == "text" and "danger" in f11["part.stun"].split(",")
          and len(fx11) == 20 and all(f11[k_] == "ro" for k_ in fx11) and all(("\n%s=%s\n" % (k_, v_)) in dcfg11 for k_, v_ in want11.items()),
          "R11d: the 6 stunlock rows emit with Skyy's numbers (3 s per player, cap 4, the boss words), part.stun a danger switch, the 20 read-only "
          "Monk rows (guard + 7 bo + 7 gauntlets + 5 wraps), every default in the default file: %s %s" % (bad11, len(fx11)))
    pr11 = Props()
    for k_, v_ in (("stun.perPlayer", "99"), ("stun.maxPlayers", "0"), ("stun.gap", "0.01"), ("stun.window", "9"), ("stun.bossWords", "x" * 300), ("part.stun", "off")):
        pr11.setProperty(k_, v_)
    ACfg.apply(pr11)
    cl11 = (float(ACfg.STUN_PER), int(ACfg.STUN_MAX), float(ACfg.STUN_GAP), float(ACfg.STUN_WINDOW), len(str(ACfg.STUN_BOSS)), bool(ACfg.PART_STUN))
    st11 = str(br.get("armory:stun"))
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    st11d = str(br.get("armory:stun"))
    check(cl11 == (20.0, 1, 0.2, 5.0, 200, False) and st11.startswith("boss stunlock breakout OFF") and st11d.startswith("boss stunlock breakout on - after 3.0 s")
          and "Chieftain" in st11d,
          "R11d: the loader clamps like the kit (99 -> 20, 0 -> 1, 0.01 -> 0.2, 9 -> 5, 300 chars -> 200, off); armory:stun names the live numbers: %s | %s" % (cl11, st11d[:140]))
    print("R11d. rows + clamps + armory:stun")

    # --- R11e. vs the 0.1.6 jar: the new files = exactly the 0.1.7 set (+ 2 classes), the 22 caster items differ in Secondary / PlayerAnimationsId only
    OLD16 = os.path.join(HERE, "SkyyArmory-0.1.6.jar")
    if not os.path.isfile(OLD16):
        print("R11e. NOTE no SkyyArmory-0.1.6.jar here - the old-vs-new file compare is skipped")
    else:
        with zipfile.ZipFile(OLD16) as oz_:
            on_ = oz_.namelist()
            new_ = sorted(set(JN) - set(on_))
            gone_ = sorted(set(on_) - set(JN))
            l17f = sorted(set(list(L17_ITEMS.values()) + list(L17_INTS.values()) + list(L17_ROOTS.values()) + list(L17_ANIM.values()) + L17_PNG
                              + [n_ for n_ in JN if n_.endswith(".blockymodel") and ("/SkyyArmory_Bo_" in n_ or n_.startswith("Common/Items/Weapons/Fist/"))]))
            newcls = sorted(n_ for n_ in new_ if n_.endswith(".class"))
            diff_ = [n_ for n_ in on_ if n_ in JSET and not n_.endswith(".class") and n_ not in ("manifest.json", "Server/Languages/en-US/server.lang")
                     and oz_.read(n_) != JZ.read(n_)]
            ddiff = []
            for n_ in diff_:
                a_, b_ = json.loads(oz_.read(n_).decode("utf-8")), json.loads(JZ.read(n_).decode("utf-8"))
                ch_ = sorted(set(k_ for k_ in set(a_) | set(b_) if a_.get(k_) != b_.get(k_)))
                if ch_ not in (["Interactions"], ["Interactions", "PlayerAnimationsId"]) or a_["Interactions"]["Primary"] != b_["Interactions"]["Primary"] \
                        or b_["Interactions"]["Secondary"] != GUARD:
                    ddiff.append((n_, ch_))
            ol_ = oz_.read("Server/Languages/en-US/server.lang").decode("utf-8").rstrip("\n").split("\n")
            nl_ = JZ.read("Server/Languages/en-US/server.lang").decode("utf-8").split("\n")
            # fixer: the old lines stay, only the 22 caster descriptions grow " Right click: block." (the Monk lines follow them)
            lchg_ = [k_ for k_ in range(len(ol_)) if k_ >= len(nl_) or nl_[k_] != ol_[k_]]
            lang_ok = len(nl_) >= len(ol_) and len(lchg_) == 22 and all(
                k_ < len(nl_) and nl_[k_] == ol_[k_].rstrip() + " Right click: block." and ".description = " in ol_[k_] for k_ in lchg_)
            ccl = sorted(n_ for n_ in on_ if n_.endswith(".class") and n_ in JSET and oz_.read(n_) != JZ.read(n_))
        check(sorted(n_ for n_ in new_ if not n_.endswith(".class")) == l17f and newcls == ["com/skyy/armory/Stun.class", "com/skyy/armory/StunRec.class"]
              and not gone_ and sorted(diff_) == sorted(L17_REAL) and not ddiff and lang_ok,
              "R11e: vs SkyyArmory-0.1.6.jar - the new files are exactly the %d Monk files + Stun / StunRec, none gone, the only changed non-class files are "
              "the 22 caster items (right click -> the guard, staff / book / wand animation set) + the lang file (grows; 22 descriptions + 'Right click: block.'): %s %s %s %s" % (
                  len(l17f), [n_ for n_ in new_ if n_ not in l17f and not n_.endswith(".class")][:4], gone_[:3], sorted(set(diff_) ^ set(L17_REAL))[:3], ddiff[:2]))
        print("R11e. vs 0.1.6: +%d files (+2 classes), 22 items rewired, %d classes changed: %s" % (len(l17f), len(ccl), ", ".join(c_.split("/")[-1][:-6] for c_ in ccl)))
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    print("R11. 0.1.7 monk weapons + block + stunlock + no void: every path executed")
'''
hrep('''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''',
     R11 + '''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''')
# fixer 2: the map-backed buffer also removes a component (Stun.noKnock), and the knockback type is registered like EntityModule does
hrep('''                "public " + CP_ + "Store getStore() { return STORE; }"])''',
     '''                "public " + CP_ + "Store getStore() { return STORE; }",
                "public void tryRemoveComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t) { java.util.Map m = (java.util.Map) armoryharness.TStore.COMP.get(r); "
                "if (m != null) m.remove(t); }"])''')
hrep('''                               ("getIntangibleComponentType", INTGc, lambda: INTGc.INSTANCE)):''',
     '''                               ("getIntangibleComponentType", INTGc, lambda: INTGc.INSTANCE),
                               ("getKnockbackComponentType", JClass("com.hypixel.hytale.server.core.entity.knockback.KnockbackComponent"), None)):''')

out_t = ts.replace(LF, TNL)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(out_t)
print("wrote %s (%d lines)" % (os.path.relpath(TDST, ROOT), out_t.count(TNL) + 1))
