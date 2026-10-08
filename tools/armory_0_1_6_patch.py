"""Derive SkyyArmory/build_skyyarmory_0.1.6.py (+ its harness SkyyArmory/test_skyyarmory_0.1.6.py) from the GENERATED 0.1.5
(SkyyArmory/build_skyyarmory_0.1.5.py = the tools/deploy_set.py SET pin, made by tools/armory_0_1_5_patch.py; test_skyyarmory_0.1.5.py =
its harness). Every anchor is asserted (rep = exactly one hit). Edit THIS file, never the generated scripts.
Run:  python tools/armory_0_1_6_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.6.py   then   python SkyyArmory/test_skyyarmory_0.1.6.py
      (never --deploy; deploy partners: SkyyClasses 0.1.13 (spellbooks = Mage) + SkyyGear 0.2.8 (the kunai bands) - both asserted once pinned)

0.1.6 = THE SPELLBOOKS + KUNAI ITEMS (Skyy 2026-10-07: "start building the spellbooks and kunai items next", "defaults are fine, go ahead",
"Match the wands.  New like the concept."; docs/answered/gear.md LOCKED 2026-10-07 SPELLBOOKS + KUNAI = every default of
research/cloud/Spellbook-Ladder.md Q1-9 and research/cloud/Kunai-Ladder.md Q1-8; the two specs are the contract):
  SPELLBOOKS Weapon_Spellbook_Copper ... _Onyxium (Mage weapons - SkyyClasses 0.1.13). Item = the vanilla Grimoire_Brown item shape (no
    MaxStack, no InteractionVars), that metal's sword Quality / ItemLevel, the metal's SHORTBOW recipe (Onyxium = the Mithril one with Onyxium
    bars - the wand rule), art from tools/art/make_spellbooks.py AT BUILD TIME (vanilla-derived bytes only in the jar; the review copy in
    models-local/art/spellbooks must match when present). Primary + Secondary = SkyyArmory_Spellbook_Primary_<M> (Charging, the vanilla
    Spellbook_Primary values): key 0 = PAGE BURST (StatsCondition B Mana -> Parallel [ChangeStat -B, LaunchProjectile the lobbed carrier orb
    SkyyArmory_Spellbook_Burst_<M> (the vanilla orb + gravity), sound]; too little Mana = the no-ammo click) - 0.5 s between casts (Medium);
    key 1 (the 1 s hold) = LEVITATE (an invisible marker SkyyArmory_Spellbook_Levitate_<M>, no Mana in the chain - the server charges it).
    B = 30 % of the Mage fighter pool at the band start (rounded to 5), per-target damage = 0.40 x the same-metal staff's damage per Mana x B
    (the spec 2 table, asserted): Copper 40 / 90, Iron 55 / 128, Thorium 70 / 168, Cobalt 85 / 207, Adamantite 115 / 283, Mithril + Onyxium
    130 / 321; burst radius 3 / 3.25 / 3.5 / 4 / 4.25 / 4.5 / 4.5, targets 4 / 4 / 5 / 5 / 6 / 6 / 6.
    JAVA: the burst orb's SPAWN (ArmoryTravSys) -> a record + the range watch (book.range, default 20: past it the orb is removed and BURSTS
    there); its direct hit (ArmoryHitSys) or its end (a miss / the range) -> ArmoryTrav.bookBurst: every enemy inside the radius, NEAREST FIRST,
    up to the targets cap (the direct target counts as one), takes the per-target damage through the whole damage pipeline (tune / SkyyGear /
    armour; players only where PvP is on + trav.players, never party - the staff rules); book.edgeFalloff % less at the edge (default 0).
    book.k scales every burst hit (ArmoryTuneSys: x book.k / 0.40). A spellbook hit never heals (SkyyClasses 0.1.13: not a Priest weapon).
    LEVITATE (Levitate + LevState, TravTick per player): the marker is removed at its SPAWN; class lock (the book + the hand), a damaging fall
    (faster than the world's roll speed) is never erased, a ceiling within 2 blocks = no cast and NOTHING spent; else lev.mana.<M> +
    lev.stamina.<M> (the traversal Stamina cap applies) -> RISE (a Velocity Set up at lev.riseSpeed every tick, up to lev.height.<M> or the
    first ceiling) -> HOVER lev.hover.<M> s (a Set every tick: the look's horizontal direction x lev.drift.<M> x the world's walk speed
    (MovementConfig BaseSpeed x ForwardRunSpeedMultiplier, VERIFIED 5.5 x 1.0), holding the height) -> crouch (lev.crouchLands) or the time
    ends it -> FLOAT: no fall damage until the hover's end + lev.safeAfter s (GrappleFallSys), falls capped at lev.floatFall b/s until then.
  KUNAI Weapon_Kunai_Crude / _Copper ... _Onyxium (Assassin weapons - SkyyClasses' "Weapon_Kunai" rule; SkyyGear 0.2.8 bands them by the metal
    word). ONE reusable kunai (stack 1, nothing ever leaves the inventory - the throw spawns a projectile only). Item = the vanilla Kunai model
    + a build-time texture / icon (tools/art/make_kunai.py; Crude = its new crude_gradients: the Crude dagger's stone + wood), the sword's
    Quality / ItemLevel, PlayerAnimationsId Throwing_Knife, the metal's DAGGERS recipe (Onyxium = Mithril's with Onyxium bars). Primary =
    Charging: tap = THROW (a ProjectileConfig = the vanilla Kunai config with our model id, gravity 6 = nearly straight, the hit = 1.12 x that
    metal's average dagger hit (Swing / Stab entries, read at build time) = 80 % of the dagger's DPS at the Fast cadence, gone past
    kunai.throwRange 20); hold 0.6 s = THROW + TELEPORT (the same kunai under its teleport model id; costs kunai.stamina.<M> + kunai.mana.<M> at
    the throw - too little = no throw; cooldown / spam net / combat row = a normal throw). Where it lands (its impact point, wrapped like the
    grapple bolt; out of kunai.range.<M> = where it left the range; kunai.flightTtl) you are teleported on the world thread - the SAFETY
    SCAN = the blink's TravMath.scan from your feet (0.5-block steps, the body box passable, walls / unloaded blocks stop it, ground within
    kunai.floorCheck, default 0 = NO void protection - Skyy LOCKED 2026-10-07 "dont put any void protection on any traversal"),
    1 block short of a mob you hit (kunai.behindMob off), never next to a non-party player
    unless the world's PvP is on (kunai.pvp), never across a locked arena (kunai.noArena: asks the bridge arena:fn:blocks when a mod answers
    it), same world only; a teleport that does not move you costs NOTHING (both refunded). The kunai leaving your hand mid-flight / death /
    another world = cancelled (refunded). Secondary hold 0.4 s = RETURN (a marker) within ret.window.<M> s: back to the spot you left (or the
    nearest safe spot within 3 blocks, else no return), then a knockback ring ret.radius.<M> x ret.force on enemies (no damage by default,
    ret.damage %). The vanilla Weapon_Kunai stays plain loot (no teleport).
  SETTINGS (Server Setup > Armory > Spellbook burst / Spellbook Levitate / Kunai; times in seconds): 20 rows + 13 per-metal tables +
    17 read-only rows (the costs and keys the client predicts are fixed in the jar, like the wands / staffs). No migration: every new key
    is absent from today's file and reads its default.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.5.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.6.py")
TSRC = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.5.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.6.py")

raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.5"\nMOD = "SkyyArmory"' in s and "0.1.5 = THE NEW METAL STAFF LOOKS" in s, "build_skyyarmory_0.1.5.py is not the 0.1.5 pin"
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
rep('''"""SkyyArmory 0.1.5 - build script (javassist via jpype). GENERATED by tools/armory_0_1_5_patch.py from the GENERATED 0.1.4 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.5.py -> SkyyArmory/SkyyArmory-0.1.5.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.5.py (scratch tools/dev/scratch/armory015/).
''', '"""SkyyArmory 0.1.6 - build script (javassist via jpype). GENERATED by tools/armory_0_1_6_patch.py from the GENERATED 0.1.5 - edit the\n'
    'patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.6.py -> SkyyArmory/SkyyArmory-0.1.6.jar (never --deploy). Harness:\n'
    'python SkyyArmory/test_skyyarmory_0.1.6.py (scratch tools/dev/scratch/armory016/).\n\n'
    + open(__file__, encoding="utf8").read().split('"""')[1].split("\n", 3)[3].strip() + "\n\n"
    '0.1.5 (the base, everything below is still true unless 0.1.6 above says otherwise):\n')
rep('VERSION = "0.1.5"\nMOD = "SkyyArmory"', 'VERSION = "0.1.6"\nMOD = "SkyyArmory"')

# ================================================================================================ the 0.1.6 constants + scalar rows
BK_CONST = r'''
# ================================================================= 0.1.6 SPELLBOOKS + KUNAI (research/cloud/Spellbook-Ladder.md + Kunai-Ladder.md; Skyy LOCKED 2026-10-07)
BOOK_SHARE = 0.30                # book cost = 30 % of the Mage fighter pool at the band start (spec 2), rounded to 5
BOOK_KDEF = 0.40                 # per-target damage = k x the staff's damage per Mana x B (row book.k; 0.34-0.49 keeps "wins from 3 targets")
BOOK_GRAVITY = 8                 # the carrier orb is lobbed (vanilla orb 0): a short arc
BOOK_TAP_RT = 0.25               # StatsCondition RunTime: + launch 0.25 = 0.5 s between casts (Medium, spec 2 cadence)
BOOK_HOLD_KEY = "1"              # the 1 s hold (the vanilla Spellbook_Primary charge key)
LEV_MIN_ROOM = 2.0               # spec 3: a ceiling within 2 blocks = no cast, nothing spent
LEV_WALK_DEF = 5.5               # VERIFIED Server/Entity/MovementConfig/Default.json BaseSpeed 5.5 x ForwardRunSpeedMultiplier 1.0 (read live)
KUNAI_HIT_X = 0.7 / 0.5          # Kunai-Ladder 5: kunai hit = dagger hit x (0.7 / 0.5) x kunai.dpsShare (Fast w 0.7 vs Super Fast w 0.5)
KUNAI_SHARE_DEF = 0.80
KUNAI_GRAVITY = 6                # nearly straight (vanilla Kunai 20); the grapple bolt's 6
KUNAI_CHARGE = "0.6"             # the hold key (spec 4 kunai.charge 0.6 s - client-predicted, fixed in the jar)
KUNAI_RET_KEY = "0.4"            # hold right click this long = the return
KUNAI_STICK = 0.5                # a kunai that hits a block stays 0.5 s (a picture only), then removes itself
KNOCK_BASE, KNOCK_UP = 10.0, 4.0 # the return knockback: 10 b/s outward + 4 up at ret.force 1 (the dagger dash config on mobs)
FIGHT_MS = 5000                  # kunai.noCombat: a hit dealt or taken within 5 s = in combat
CFG_BK = [
    ('part.book', 'Spellbooks (burst + Levitate)', 'book', 'bool', 'true', '', '', '', '', 'live,part,danger', 'Off = a book tap fires a plain orb (no burst) and the hold does nothing.', 'PART_BOOK', 'boolean', 'true', 'Spellbooks: tap = Page Burst, hold = Levitate. Off = a tap fires a plain orb (no burst) and the hold does nothing.'),
    ('book.k', 'Burst damage factor (k)', 'book', 'dec', '0.4', '0.1', '1', '', '', 'live', 'Per-target damage vs the staff per Mana. 0.34-0.49 keeps the book winning only from 3 targets.', 'BOOK_K', 'double', '0.4', 'Page Burst per-target damage = k x the same-metal staff damage per Mana x the book cost (0.4 = the spec table; every burst hit x k / 0.4).'),
    ('book.range', 'Burst orb range (blocks)', 'book', 'int', '20', '4', '64', '', 'blocks', 'live', 'The page orb bursts where it hits, or here at the latest.', 'BOOK_RANGE', 'int', '20', 'The page orb bursts where it hits something, or this many blocks from where it was cast at the latest.'),
    ('book.edgeFalloff', 'Less damage at the edge (%)', 'book', 'int', '0', '0', '90', 'step=5', '%', 'live', '0 = every target in the burst takes the full damage.', 'BOOK_FALL', 'int', '0', 'Burst damage this % lower at the edge of the burst (0 = full damage everywhere inside it).'),
    ('lev.safeAfter', 'No fall damage after the hover (s)', 'lev', 'dec', '3', '0', '10', '', 's', 'live', 'Seconds after the hover ends with no fall damage.', 'LEV_SAFE', 'double', '3', 'Levitate: no fall damage until the hover ends plus this many seconds.'),
    ('lev.crouchLands', 'Crouch ends the hover', 'lev', 'bool', 'true', '', '', '', '', 'live', 'Crouch while hovering = start floating down at once.', 'LEV_CROUCH', 'boolean', 'true', 'Levitate: crouching while you hover ends the hover early (you float down).'),
    ('lev.riseSpeed', 'Rise speed (blocks per second)', 'lev', 'dec', '10', '3', '30', '', '', 'live', 'How fast Levitate lifts you to its height.', 'LEV_RISE', 'double', '10', 'Levitate: how fast you rise to the height (blocks per second).'),
    ('lev.floatFall', 'Float down speed (b/s)', 'lev', 'dec', '6', '0', '20', '', '', 'live', 'Fastest fall after the hover until the safe time ends (0 = a normal fall).', 'LEV_FLOAT', 'double', '6', 'Levitate: after the hover you fall at most this fast until the safe time ends (0 = a normal fall).'),
    ('part.kunai', 'Kunai teleport + return', 'kunai', 'bool', 'true', '', '', '', '', 'live,part,danger', 'Off = the hold throws a normal kunai (no teleport, no return).', 'PART_KUNAI', 'boolean', 'true', 'Kunai: hold = throw + teleport, hold right click = return. Off = the hold throws a normal kunai.'),
    ('kunai.dpsShare', 'Kunai damage share of the dagger', 'kunai', 'dec', '0.8', '0.3', '1.5', '', 'x', 'live', 'Kunai DPS vs the same-metal dagger (hit = dagger hit x 1.4 x this).', 'K_SHARE', 'double', '0.8', 'Kunai DPS as a share of the same-metal dagger (a kunai hit = the dagger hit x 0.7 / 0.5 x this).'),
    ('kunai.throwRange', 'Throw range (blocks)', 'kunai', 'int', '20', '5', '40', '', 'blocks', 'live', 'A thrown kunai is gone past this.', 'K_THROW_RANGE', 'int', '20', 'A thrown kunai (tap) is gone past this many blocks.'),
    ('kunai.flightTtl', 'Teleport kunai flight time (s)', 'kunai', 'dec', '1.5', '0.3', '5', '', 's', 'live', 'Still flying after this = you appear where it is.', 'K_TTL', 'double', '1.5', 'A teleport kunai still flying after this many seconds lands you where it is.'),
    ('kunai.floorCheck', 'Ground under the landing (blocks)', 'kunai', 'int', '0', '0', '64', '', 'blocks', 'live', '0 = off (no void protection, Skyy).', 'K_FLOOR', 'int', '0', 'A kunai teleport needs ground within this many blocks below the landing spot (0 = off: no void protection, Skyy 2026-10-07).'),
    ('kunai.behindMob', 'Land behind a mob', 'kunai', 'bool', 'false', '', '', '', '', 'live', 'Off = you land 1 block in front of the mob you hit.', 'K_BEHIND', 'boolean', 'false', 'On = a kunai that hits a mob puts you behind it (off = 1 block in front of it).'),
    ('kunai.noArena', 'No teleport across locked arenas', 'kunai', 'bool', 'true', '', '', '', '', 'live', 'Asks the bridge arena:fn:blocks (no mod answers it yet).', 'K_NOARENA', 'boolean', 'true', 'No kunai teleport into, out of or past a locked arena (a mod answering arena:fn:blocks decides).'),
    ('kunai.noCombat', 'No teleport in combat', 'kunai', 'bool', 'false', '', '', '', '', 'live', 'On = no teleport within 5 s of a hit you dealt or took.', 'K_NOCOMBAT', 'boolean', 'false', 'On = no kunai teleport within 5 seconds of a hit you dealt or took (a normal throw instead).'),
    ('kunai.pvp', 'Land next to players', 'kunai', 'choice', 'world', '', '', 'world|Where PvP is on,never|Never', '', 'live', 'Party members always; other players only where the world PvP is on.', 'K_PVP', 'String', 'world', 'A kunai that hits a player lands you next to them: world = only where PvP is on (party always), never.'),
    ('kunai.maxPerMinute', 'Most teleports per minute', 'kunai', 'int', '12', '0', '120', '', '', 'live', 'A spam net (0 = no cap).', 'K_MAXMIN', 'int', '12', 'At most this many kunai teleports per player per minute (0 = no cap).'),
    ('ret.force', 'Return knockback strength', 'kunai', 'dec', '1', '0', '3', '', 'x', 'live', '1 = 10 blocks per second outward.', 'K_FORCE', 'double', '1', 'Kunai return: how hard the knockback ring pushes enemies (1 = 10 blocks per second outward).'),
    ('ret.damage', 'Return knockback damage (%)', 'kunai', 'int', '0', '0', '200', 'step=5', '%', 'live', '% of a kunai hit (0 = a push only).', 'K_RDMG', 'int', '0', 'Kunai return: the knockback deals this % of a kunai hit (0 = a push only).'),
]
'''
before('''# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)''', BK_CONST)
rep("""'Staff quick shots hit this % harder (per Mana) than wand quick shots.')] + CFG_GRAPPLE + CFG_LEAP      # 0.1.2 grapple + 0.1.3 leap rows""",
    """'Staff quick shots hit this % harder (per Mana) than wand quick shots.')] + CFG_GRAPPLE + CFG_LEAP + CFG_BK      # 0.1.2 grapple + 0.1.3 leap + 0.1.6 book / kunai rows""")

# ================================================================================================ the assets (vanilla shapes first)
BK_ASSETS = r'''
# ================================================================= 0.1.6 ASSETS: SPELLBOOKS + KUNAI (research/cloud/Spellbook-Ladder.md + Kunai-Ladder.md; vanilla shapes first)
BOOK_METALS = list(NEW_METALS)
KUNAI_METALS = ["Crude"] + list(NEW_METALS)
P_BITEM = "Server/Item/Items/Weapon/Spellbook/Weapon_Spellbook_%s.json"
P_BINT = "Server/Item/Interactions/Weapons/Spellbook/SkyyArmory/%s.json"
P_BROOT = "Server/Item/RootInteractions/Weapons/Spellbook/SkyyArmory/%s.json"
P_KITEM = "Server/Item/Items/Weapon/Kunai/Weapon_Kunai_%s.json"
P_KINT = "Server/Item/Interactions/Weapons/Kunai/SkyyArmory/%s.json"
P_KROOT = "Server/Item/RootInteractions/Weapons/Kunai/SkyyArmory/%s.json"
MODEL_BOOK = "Items/Weapons/Spellbook/SkyyArmory_%s.blockymodel"
TEX_BOOK = "Items/Weapons/Spellbook/SkyyArmory_%s_Texture.png"
ICON_BOOK = "Icons/ItemsGenerated/SkyyArmory_Spellbook_%s.png"
TEX_KUNAI = "Items/Weapons/Kunai/SkyyArmory_%s_Texture.png"
ICON_KUNAI = "Icons/ItemsGenerated/SkyyArmory_Kunai_%s.png"
ID_BROOT, ID_BCAST = "SkyyArmory_Spellbook_Primary_%s", "SkyyArmory_Spellbook_Cast_%s"
ID_BCOST, ID_BLAUNCH = "SkyyArmory_Spellbook_Cast_Cost_%s", "SkyyArmory_Spellbook_Cast_Launch_%s"
ID_BEFF, ID_BFAIL = "SkyyArmory_Spellbook_Cast_Effect", "SkyyArmory_Spellbook_Fail"
ID_BLEV, ID_BLEVL = "SkyyArmory_Spellbook_Lev_%s", "SkyyArmory_Spellbook_Lev_Launch_%s"
ID_BBURST, ID_BLEVM = "SkyyArmory_Spellbook_Burst_%s", "SkyyArmory_Spellbook_Levitate_%s"          # projectiles (spec 4 asset ids)
ID_KROOT, ID_KTHROW, ID_KPORT = "SkyyArmory_Kunai_Primary_%s", "SkyyArmory_Kunai_Throw_Step_%s", "SkyyArmory_Kunai_Port_Step_%s"
ID_KRROOT, ID_KRLAUNCH, ID_KIDLE = "SkyyArmory_Kunai_Return_%s", "SkyyArmory_Kunai_Return_Launch_%s", "SkyyArmory_Kunai_Idle"
ID_KCFG_T, ID_KCFG_P = "SkyyArmory_Kunai_Throw_%s", "SkyyArmory_Kunai_Teleport_%s"   # ProjectileConfig ids AND their model ids (spec 2 asset ids)
ID_KRMARK = "SkyyArmory_Kunai_ReturnMark_%s"                                        # the return's invisible marker (legacy projectile)
SND_BOOK_HIT, SND_BOOK_CHARGE = "SFX_Skeleton_Mage_Spellbook_Impact", "SFX_Skeleton_Mage_Spellbook_Charge"
SND_KUNAI = "SFX_Daggers_T2_Stab_Impact"


def bnum(v):
    v = round(float(v), 4)
    return str(int(v)) if v == int(v) else ("%.4f" % v).rstrip("0").rstrip(".")

# ---- the vanilla shapes this block copies (the build stops if Hytale changes them)
VBOOK = az_get("item", "Weapon_Spellbook_Grimoire_Brown")
assert VBOOK["PlayerAnimationsId"] == "Spellbook" and VBOOK["Interactions"] == {"Primary": "Spellbook_Primary", "Secondary": "Spellbook_Primary"} \
    and VBOOK["Tags"] == {"Type": ["Weapon"], "Family": ["Spellbook"]} and VBOOK["Weapon"] == {} and VBOOK["Model"] == "Items/Weapons/Spellbook/Grimoire.blockymodel" \
    and VBOOK["IconProperties"] == {"Scale": 0.745, "Translation": [-7.8, -7.8], "Rotation": [45, 90, 0]}, "the vanilla Grimoire_Brown item changed"
VBP = az_get("int", "Spellbook_Primary")
assert VBP["Type"] == "Charging" and sorted(VBP["Next"]) == ["0", BOOK_HOLD_KEY] and VBP["AllowIndefiniteHold"] is True \
    and VBP["HorizontalSpeedMultiplier"] == 0.8 and VBP["Effects"] == {"ItemAnimationId": "CastHurlCharging", "WorldSoundEventId": SND_BOOK_CHARGE}, VBP
VBFAIL = az_get("int", "Spellbook_Cast_Fail")
assert VBFAIL == {"Type": "Simple", "RunTime": 0.2, "Effects": {"ItemAnimationId": "Interact", "WorldSoundEventId": "SFX_Bow_No_Ammo"}}, VBFAIL
assert "ModifyInventory" in json.dumps(az_get("int", "Spellbook_Cast_Cost")), "vanilla books use themselves up - ours never name that step"
_banim = resolve("anim", "Spellbook")["Animations"]
assert all(a in _banim for a in ("CastHurlCharging", "CastHurlCharged", "CastPushCharged")), sorted(_banim)
VKUNAI = az_get("item", "Weapon_Kunai")
assert VKUNAI["PlayerAnimationsId"] == "Throwing_Knife" and VKUNAI["Model"] == "Items/Weapons/Throwing_Knife/Kunai.blockymodel" \
    and VKUNAI["Interactions"]["Secondary"]["Interactions"] == ["Kunai_Throw"] and "MaxStack" not in VKUNAI, "the vanilla Kunai changed"
assert "ModifyInventory" not in json.dumps(az_get("int", "Kunai_Throw")), "VERIFIED (Kunai-Ladder 9 item 4): the vanilla kunai throw consumes no item"
_kanim = az_get("anim", "Throwing_Knife")["Animations"]
assert "Throw" in _kanim and "Interact" in _kanim, sorted(_kanim)
VKCFG = az_json(az_path("pcfg", "Projectile_Config_Kunai"))
assert "Parent" not in VKCFG and VKCFG["Model"] == "Kunai" and VKCFG["Physics"]["Type"] == "Standard" and VKCFG["Physics"]["Gravity"] == 20 \
    and VKCFG["LaunchForce"] == 45, VKCFG
_vkh = VKCFG["Interactions"]["ProjectileHit"]["Interactions"]
_vkm = VKCFG["Interactions"]["ProjectileMiss"]["Interactions"]
assert _vkh[0]["Parent"] == "DamageEntityParent" and _vkh[0]["DamageCalculator"] == {"BaseDamage": {"Physical": 6}} and _vkh[1]["Type"] == "RemoveEntity" \
    and _vkm[0]["Type"] == "Simple" and _vkm[0]["RunTime"] == 5 and _vkm[1] == {"Type": "RemoveEntity", "Entity": "User"}, VKCFG["Interactions"]
VKMODEL = az_get("model", "Kunai")
assert VKMODEL["DefaultAttachments"] == [{"Model": "Items/Weapons/Throwing_Knife/Kunai.blockymodel", "Texture": "Items/Weapons/Throwing_Knife/Kunai_Texture.png"}]
for _s in (SND_BOOK_HIT, SND_BOOK_CHARGE, SND_KUNAI, "SFX_Bow_No_Ammo"):
    assert az_has("sound", _s), "no sound event %s" % _s
assert az_has("int", "DamageEntityParent")
# spec 4 / Kunai-Ladder 2 build stop: a vanilla metal spellbook / kunai would be overridden - Skyy decides first
for _m in BOOK_METALS:
    assert not az_has("item", "Weapon_Spellbook_" + _m), "Hytale now has Weapon_Spellbook_%s - SkyyArmory would override it" % _m
for _m in KUNAI_METALS:
    assert not az_has("item", "Weapon_Kunai_" + _m), "Hytale now has Weapon_Kunai_%s - SkyyArmory would override it" % _m
    assert "skyy" not in ("Weapon_Kunai_" + _m).lower()

# ---- THE BOOK LADDER (spec 2, python-checked there; asserted here): pool = 30 + 10 L + 0.2 x floor(L / 9) at the band start (the 15.4 Mage
# fighter rule), B = 30 % of it rounded to 5, the staff's damage per Mana = STAFF_BASE x mult / C (charged), per-target = 0.40 x that x B


def mage_pool(l):
    return 30 + 10 * l + 0.2 * (l // 9)


def round5(x):
    return int(5 * math.floor(x / 5.0 + 0.5 + 1e-9))


BOOK = {}
for _m in BOOK_METALS:
    _st = [x for x in ST if x[0] == _m][0]
    _pool = mage_pool(BANDS[_m][0])
    _b = round5(BOOK_SHARE * _pool)
    _dpm = STAFF_BASE * _st[3] / float(_st[1])
    BOOK[_m] = dict(pool=_pool, cost=_b, dpm=_dpm, dmg=rhu(BOOK_KDEF * _dpm * _b))
    assert _b <= 0.40 * _pool and abs(BOOK[_m]["dmg"] / (_dpm * _b) - BOOK_KDEF) < 0.01, (_m, BOOK[_m])
if STAFF_BASE == 50:
    assert [(BOOK[m]["cost"], BOOK[m]["dmg"]) for m in BOOK_METALS] == [(40, 90), (55, 128), (70, 168), (85, 207), (115, 283), (130, 321), (130, 321)], BOOK
    assert [round(BOOK[m]["pool"], 1) for m in BOOK_METALS] == [130.2, 180.2, 230.4, 280.4, 380.6, 430.8, 430.8]
BOOK_R = [3.0, 3.25, 3.5, 4.0, 4.25, 4.5, 4.5]             # spec 2 radius
BOOK_T = [4, 4, 5, 5, 6, 6, 6]                            # spec 2 targets cap
LEV_H = [8.0, 8.0, 9.0, 10.0, 11.0, 12.0, 12.0]           # spec 3 (Skyy Q6: scales by metal; Copper = the locked 8 / 3)
LEV_S = [3.0, 3.0, 3.5, 4.0, 4.5, 5.0, 5.0]
LEV_D = [0.8, 0.8, 0.9, 1.0, 1.0, 1.1, 1.1]
LEV_M = [10.0, 10.0, 12.0, 14.0, 16.0, 18.0, 18.0]
LEV_ST = [5.0, 5.0, 6.0, 7.0, 8.0, 9.0, 9.0]
assert all(LEV_M[i] == 2 * LEV_ST[i] for i in range(7)) and LEV_H[0] == 8.0 and LEV_S[0] == 3.0, "spec 3: Mana = 2 x Stamina; Copper = the lock"
# the rule that sets every number (spec 2): per Mana the book loses at 1 and 2 targets and wins from 3 (k 0.40)
for _i, _m in enumerate(BOOK_METALS):
    _rel = [n_ * BOOK[_m]["dmg"] / (BOOK[_m]["dpm"] * BOOK[_m]["cost"]) for n_ in (1, 2, 3)]
    assert _rel[0] < 1.0 and _rel[1] < 1.0 and _rel[2] > 1.0, (_m, _rel)
# ---- THE KUNAI LADDER (Kunai-Ladder 4 + 5): range 20 every metal (Skyy Q5), costs Stamina 2 : Mana 1, the hit = 1.12 x the dagger's average hit
K_RANGE = [20] * 8
K_CD = [7.0, 6.0, 5.5, 5.0, 4.5, 4.0, 3.5, 3.5]
K_STAM = [6.0, 6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0]
K_MANA = [3.0, 3.0, 3.0, 3.0, 2.0, 2.0, 2.0, 2.0]
K_WIN = [8.0, 8.0, 8.0, 9.0, 9.0, 10.0, 10.0, 10.0]
K_RAD = [3.0, 3.0, 3.25, 3.5, 3.75, 4.0, 4.25, 4.25]
assert all(K_STAM[i] == 2 * K_MANA[i] or (K_STAM[i] == 5.0 and K_MANA[i] == 2.0) for i in range(8)), "physical: Stamina 2 : Mana 1 (whole numbers)"
DAGGER = {}
for _m in KUNAI_METALS:
    _dd = item_resolved("Weapon_Daggers_" + _m)
    _iv = _dd.get("InteractionVars") or {}
    _hits = [float(_iv[_k]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Physical"])
             for _k in ("Swing_Left_Damage", "Swing_Right_Damage", "Stab_Left_Damage", "Stab_Right_Damage")]
    _all = []
    for _v in _iv.values():
        for _e in _v.get("Interactions") or []:
            if isinstance(_e, dict) and isinstance(_e.get("DamageCalculator"), dict):
                _all += [float(x) for x in _e["DamageCalculator"].get("BaseDamage", {}).values()]
                for _a in _e.get("AngledDamage") or []:
                    _all += [float(x) for x in (_a.get("DamageCalculator") or {}).get("BaseDamage", {}).values()]
    DAGGER[_m] = dict(hits=_hits, mean=sum(_hits) / 4.0, max=max(_all), quality=_dd.get("Quality"), level=_dd.get("ItemLevel"))
KUNAI_DMG = dict((m, rhu(DAGGER[m]["mean"] * KUNAI_HIT_X * KUNAI_SHARE_DEF)) for m in KUNAI_METALS)
assert KUNAI_DMG == {"Crude": 5, "Copper": 7, "Iron": 9, "Thorium": 12, "Cobalt": 12, "Adamantite": 14, "Mithril": 18, "Onyxium": 18}, KUNAI_DMG
DROP_BENCH2 = ("Armory",)


def dagger_recipe(m):
    r = item_resolved("Weapon_Daggers_" + m).get("Recipe")
    assert isinstance(r, dict), "Weapon_Daggers_%s has no recipe any more" % m
    assert set(r) <= set(RECIPE_KEYS), (m, sorted(r))
    out = json.loads(json.dumps(r))
    if "BenchRequirement" in out:
        out["BenchRequirement"] = [b for b in out["BenchRequirement"] if b.get("Id") not in DROP_BENCH2]
    assert any(b.get("Type") == "Crafting" for b in out.get("BenchRequirement") or []), m
    return out


assert item_resolved("Weapon_Daggers_Onyxium").get("Recipe") is None, "vanilla gave the Onyxium daggers a recipe - re-check Skyy's Onyxium answer"
KUNAI_RECIPES = dict((m, dagger_recipe(m)) for m in KUNAI_METALS if m != "Onyxium")
_kor = dagger_recipe("Mithril")
_kon = [x for x in _kor["Input"] if x.get("ItemId") == "Ingredient_Bar_Mithril"]
assert len(_kon) == 1, _kor
_kon[0]["ItemId"] = "Ingredient_Bar_Onyxium"
KUNAI_RECIPES["Onyxium"] = _kor
for _m, _r in list(KUNAI_RECIPES.items()) + [("book", r_) for r_ in WAND_RECIPES.values()]:
    for _x in _r["Input"]:
        assert (_x.get("ItemId") is None or az_has("item", _x["ItemId"])) and (_x.get("ResourceTypeId") is None or az_has("rtype", _x["ResourceTypeId"])), (_m, _x)
for _i in ["Weapon_Spellbook_" + m for m in BOOK_METALS] + ["Weapon_Kunai_" + m for m in KUNAI_METALS]:
    assert _i + "_Recipe_Generated_0" not in _vrecipe_ids and _i not in _salvage_in, _i

# ---- SPELLBOOK chains (spec 2 + 3): tap = Page Burst (Mana in the chain, client-predicted), hold 1 s = the Levitate marker (no Mana: the server)
BK_INTS, BK_PRJS = [], []


def add_bk(path_fmt, iid, obj):
    add_int(path_fmt, iid, obj)
    BK_INTS.append(iid)


add_bk(P_BINT, ID_BEFF, {"Type": "Simple", "RunTime": BOOK_TAP_RT, "Effects": {"WorldSoundEventId": SND_BOOK_HIT}})
add_bk(P_BINT, ID_BFAIL, json.loads(json.dumps(VBFAIL)))


def book_orb(dmg):
    d = orb(dmg)
    d["Gravity"] = BOOK_GRAVITY
    return d


for _i, _m in enumerate(BOOK_METALS):
    _b = BOOK[_m]["cost"]
    add_bk(P_BINT, ID_BCOST % _m, change_mana(_b))
    add_bk(P_BINT, ID_BLAUNCH % _m, launch(ID_BBURST % _m, "CastHurlCharged"))
    add_bk(P_BINT, ID_BCAST % _m, stats_check(_b, BOOK_TAP_RT, [ID_BCOST % _m, ID_BLAUNCH % _m, ID_BEFF], ID_BFAIL))
    add_bk(P_BINT, ID_BLEVL % _m, launch(ID_BLEVM % _m, "CastPushCharged"))
    add_bk(P_BINT, ID_BLEV % _m, {"Type": "Simple", "RunTime": 0.167, "Next": {"Type": "Parallel", "Interactions": [inline_root(ID_BLEVL % _m)]}})
    add_bk(P_BINT, ID_BROOT % _m, {"Type": "Charging", "Effects": dict(VBP["Effects"]), "AllowIndefiniteHold": VBP["AllowIndefiniteHold"],
                                   "HorizontalSpeedMultiplier": VBP["HorizontalSpeedMultiplier"], "Next": {"0": ID_BCAST % _m, BOOK_HOLD_KEY: ID_BLEV % _m}})
    add_root(P_BROOT, ID_BROOT % _m, [ID_BROOT % _m])
    add_prj(ID_BBURST % _m, book_orb(BOOK[_m]["dmg"]))
    add_prj(ID_BLEVM % _m, blink_marker())
    BK_PRJS += [ID_BBURST % _m, ID_BLEVM % _m]

# ---- KUNAI chains (Kunai-Ladder 4): tap = throw, hold 0.6 s = throw + teleport (the same kunai under its teleport model id), right-click hold
# 0.4 s = the return marker. ProjectileConfig = the vanilla Kunai config with our model, gravity 6, our hit, a 0.5 s stick on a block.
add_bk(P_KINT, ID_KIDLE, {"Type": "Simple", "RunTime": 0.05})
KCFGS, KMODELS = {}, {}


def kunai_cfg(m, model_id):
    d = json.loads(json.dumps(VKCFG))
    d["Model"] = model_id
    d["Physics"]["Gravity"] = KUNAI_GRAVITY
    d["Interactions"]["ProjectileHit"]["Interactions"][0]["DamageCalculator"] = {"BaseDamage": {"Physical": KUNAI_DMG[m]}}
    d["Interactions"]["ProjectileMiss"]["Interactions"][0]["RunTime"] = KUNAI_STICK
    return d


for _i, _m in enumerate(KUNAI_METALS):
    for _cid, _sid in ((ID_KCFG_T % _m, ID_KTHROW % _m), (ID_KCFG_P % _m, ID_KPORT % _m)):
        assert not az_has("pcfg", _cid) and not az_has("model", _cid), _cid
        KCFGS[_cid] = kunai_cfg(_m, _cid)
        put(P_PCFG % _cid, KCFGS[_cid])
        _km = json.loads(json.dumps(VKMODEL))
        _km["DefaultAttachments"][0]["Texture"] = TEX_KUNAI % _m
        KMODELS[_cid] = _km
        put(P_MODEL % _cid, _km)
        add_bk(P_KINT, _sid, {"Type": "Serial", "Interactions": [{"Type": "Simple", "RunTime": 0.1, "Effects": {"ItemAnimationId": "Throw"}},
                                                                {"Type": "Projectile", "RunTime": 0.25, "Config": _cid}]})
    add_bk(P_KINT, ID_KROOT % _m, {"Type": "Charging", "AllowIndefiniteHold": True, "Next": {"0": ID_KTHROW % _m, KUNAI_CHARGE: ID_KPORT % _m}})
    add_root(P_KROOT, ID_KROOT % _m, [ID_KROOT % _m])
    add_bk(P_KINT, ID_KRLAUNCH % _m, {"Type": "LaunchProjectile", "RunTime": 0.2, "Effects": {"ItemAnimationId": "Interact"}, "ProjectileId": ID_KRMARK % _m})
    add_bk(P_KINT, ID_KRROOT % _m, {"Type": "Charging", "AllowIndefiniteHold": True, "Next": {"0": ID_KIDLE, KUNAI_RET_KEY: ID_KRLAUNCH % _m}})
    add_root(P_KROOT, ID_KRROOT % _m, [ID_KRROOT % _m])
    add_prj(ID_KRMARK % _m, blink_marker())
    BK_PRJS.append(ID_KRMARK % _m)

# ---- THE ART, generated at build time (Skyy 2026-10-07 "Match the wands"): tools/art/make_spellbooks.py + make_kunai.py functions in the order
# of their main(); the vanilla-derived bytes exist only in the jar. When the git-ignored review copy exists it must equal the jar bytes.
import make_spellbooks as MSB
import make_kunai as MKU
assert tuple(MSB.METALS) == tuple(BOOK_METALS) and tuple(MKU.METALS) == tuple(BOOK_METALS), (MSB.METALS, MKU.METALS)
_bvd, _bvm, _bvt, _bvi = SA.item_parts(AZ, MSB.BASE_ITEM)
assert _bvd["IconProperties"] == VBOOK["IconProperties"] and MSB.BASE_ITEM.endswith("/Weapon_Spellbook_Grimoire_Brown.json")
_bvanilla = json.loads(_bvm.decode("utf-8-sig"))
BOOK_ART, BOOK_REVIEW = {}, {}
for _m in BOOK_METALS:
    _bb = MSB.Builder()
    _bmodel = MSB.build_model(_bvanilla, _m, _bb)
    _bplace = MSB.pack(_bb, 64)
    _btex, _bG = MSB.make_texture(AZ, _bvt, _bvanilla, _m, _bb, _bplace)
    _bicon = SA.png_encode(MSB.render(_bmodel, _btex, VBOOK["IconProperties"]))
    _bmj = (json.dumps(_bmodel, indent=2) + "\n").encode("utf-8")
    _tw, _th = SA.png_size(_btex)
    assert _tw % 32 == 0 and _th % 32 == 0 and SA.png_size(_bicon) == (64, 64), (_m, _tw, _th)
    for _rn in ("Handle", "Book-Top", "Book-Bot"):
        assert MSB.find(_bmodel["nodes"], _rn) is not None, (_m, _rn)
    BOOK_ART[_m] = (_bmj, _btex, _bicon)
    ASSETS["Common/" + MODEL_BOOK % _m] = _bmj
    ASSETS["Common/" + TEX_BOOK % _m] = _btex
    ASSETS["Common/" + ICON_BOOK % _m] = _bicon
    _rv = os.path.join(ROOT, "models-local", "art", "spellbooks", "Common")
    _rf = [os.path.join(_rv, *(p % _m).split("/")) for p in (MODEL_BOOK, TEX_BOOK, ICON_BOOK)]
    if all(os.path.isfile(p) for p in _rf):
        assert [open(p, "rb").read() for p in _rf] == [_bmj, _btex, _bicon], \
            "%s: the built spellbook art differs from the reviewed copy in models-local/art/spellbooks (re-run python tools/art/make_spellbooks.py)" % _m
        BOOK_REVIEW[_m] = "= reviewed copy"
    else:
        BOOK_REVIEW[_m] = "no review copy here"
assert len(set(a[1] for a in BOOK_ART.values())) == 7 and len(set(a[2] for a in BOOK_ART.values())) == 7
_kvd, _kvm, _kvt, _kvi = SA.item_parts(AZ, MKU.BASE_ITEM)
_kmodel = json.loads(_kvm.decode("utf-8-sig"))
KUNAI_ART, KUNAI_REVIEW = {}, {}
for _m in KUNAI_METALS:
    _kt = MKU.kunai_texture(AZ, _m, _kmodel, _kvt, MKU.crude_gradients(AZ) if _m == "Crude" else None)
    _ki = SA.render_icon(_kmodel, _kt, _kvd["IconProperties"], 64)
    assert SA.png_size(_kt) == SA.png_size(_kvt) and SA.png_size(_ki) == (64, 64), _m
    KUNAI_ART[_m] = (_kt, _ki)
    ASSETS["Common/" + TEX_KUNAI % _m] = _kt
    ASSETS["Common/" + ICON_KUNAI % _m] = _ki
    _rk = os.path.join(ROOT, "models-local", "art", "kunai", "Common")
    _rkf = [os.path.join(_rk, *(TEX_KUNAI % _m).split("/")), os.path.join(_rk, *(ICON_KUNAI % _m).split("/"))]
    if _m != "Crude" and all(os.path.isfile(p) for p in _rkf):
        assert [open(p, "rb").read() for p in _rkf] == [_kt, _ki], \
            "%s: the built kunai art differs from the reviewed copy in models-local/art/kunai (re-run python tools/art/make_kunai.py)" % _m
        KUNAI_REVIEW[_m] = "= reviewed copy"
    else:
        KUNAI_REVIEW[_m] = "built here (Crude: new)" if _m == "Crude" else "no review copy here"
assert len(set(a[0] for a in KUNAI_ART.values())) == 8 and KUNAI_ART["Crude"][0] != _kvt

# ---- the items
BK_ITEMS = []
for _i, _m in enumerate(BOOK_METALS):
    _sw = resolve("item", "Weapon_Sword_" + _m)
    _it = {"TranslationProperties": {"Name": "server.items.Weapon_Spellbook_%s.name" % _m}, "Categories": list(VBOOK["Categories"]),
           "Icon": ICON_BOOK % _m, "Quality": _sw["Quality"], "ItemLevel": _sw["ItemLevel"], "Model": MODEL_BOOK % _m, "Texture": TEX_BOOK % _m,
           "PlayerAnimationsId": VBOOK["PlayerAnimationsId"], "IconProperties": json.loads(json.dumps(VBOOK["IconProperties"])),
           "Interactions": {"Primary": ID_BROOT % _m, "Secondary": ID_BROOT % _m}, "DroppedItemAnimation": VBOOK["DroppedItemAnimation"],
           "Scale": VBOOK["Scale"], "Tags": json.loads(json.dumps(VBOOK["Tags"])), "Weapon": {}, "ItemSoundSetId": VBOOK["ItemSoundSetId"],
           "Recipe": json.loads(json.dumps(WAND_RECIPES[_m]))}
    assert "MaxStack" not in _it and "InteractionVars" not in _it and "skyy" not in ("Weapon_Spellbook_" + _m).lower()
    ITEMS["Weapon_Spellbook_" + _m] = _it
    put(P_BITEM % _m, _it)
    BK_ITEMS.append("Weapon_Spellbook_" + _m)
for _i, _m in enumerate(KUNAI_METALS):
    _sw = resolve("item", "Weapon_Sword_" + _m)
    _it = {"TranslationProperties": {"Name": "server.items.Weapon_Kunai_%s.name" % _m}, "Categories": list(VKUNAI["Categories"]),
           "Icon": ICON_KUNAI % _m, "IconProperties": json.loads(json.dumps(VKUNAI["IconProperties"])), "Quality": _sw["Quality"],
           "ItemLevel": _sw["ItemLevel"], "Model": VKUNAI["Model"], "Texture": TEX_KUNAI % _m, "PlayerAnimationsId": VKUNAI["PlayerAnimationsId"],
           "Weapon": {}, "Interactions": {"Primary": ID_KROOT % _m, "Secondary": ID_KRROOT % _m}, "Tags": {"Type": ["Weapon"], "Family": ["Kunai"]},
           "Recipe": KUNAI_RECIPES[_m]}
    assert "MaxStack" not in _it and "Utility" not in _it
    ITEMS["Weapon_Kunai_" + _m] = _it
    put(P_KITEM % _m, _it)
    BK_ITEMS.append("Weapon_Kunai_" + _m)
assert [(ITEMS[i]["Quality"], ITEMS[i]["ItemLevel"]) for i in BK_ITEMS] == [
    ("Common", 10), ("Uncommon", 20), ("Rare", 30), ("Rare", 35), ("Rare", 40), ("Epic", 50), ("Epic", 50),
    ("Common", 3), ("Common", 10), ("Uncommon", 20), ("Rare", 30), ("Rare", 35), ("Rare", 40), ("Epic", 50), ("Epic", 50)], \
    "the vanilla sword qualities / levels changed (spec 4 table): %s" % [(ITEMS[i]["Quality"], ITEMS[i]["ItemLevel"]) for i in BK_ITEMS]
# ---- language (names + descriptions through the default key; the numbers are the defaults)
BKLANG = []
# the tooltip shows what the player PAYS: the traversal Stamina cap (trav.staminaCap, default 5) applies to Levitate + the kunai teleport
_CAPROW = [r_ for r_ in CFG_NEW if r_[0] == 'trav.staminaCap']
assert len(_CAPROW) == 1 and _CAPROW[0][4] == '5', "trav.staminaCap default moved: %s" % _CAPROW
TRAV_CAP_DEF = float(_CAPROW[0][4])
def capst(v):
    return min(float(v), TRAV_CAP_DEF) if TRAV_CAP_DEF > 0 else float(v)
def levmana(i):          # fix2: what Levitate really charges = min(lev.mana, 2 x the Stamina paid)
    return min(float(LEV_M[i]), 2.0 * capst(LEV_ST[i]))
for _i, _m in enumerate(BOOK_METALS):
    BKLANG.append("items.Weapon_Spellbook_%s.name = %s Spellbook" % (_m, _m))
    BKLANG.append("items.Weapon_Spellbook_%s.description = Tap: Page Burst, %d Mana, hits up to %d within %s blocks. Hold: Levitate, %s Mana + %s Stamina."
                  % (_m, BOOK[_m]["cost"], BOOK_T[_i], bnum(BOOK_R[_i]), bnum(levmana(_i)), bnum(capst(LEV_ST[_i]))))
for _i, _m in enumerate(KUNAI_METALS):
    BKLANG.append("items.Weapon_Kunai_%s.name = %s Kunai" % (_m, _m))
    BKLANG.append("items.Weapon_Kunai_%s.description = Tap: throw, %d blocks. Hold: throw and teleport where it lands, %s Stamina + %s Mana. "
                  "Hold right click: go back." % (_m, K_RANGE[_i], bnum(capst(K_STAM[_i])), bnum(K_MANA[_i])))
for _l in BKLANG:
    assert ("\n" + _l.split(" = ")[0] + " ") not in _vlang, "vanilla already has " + _l.split(" = ")[0]
ASSETS[P_LANG] = ASSETS[P_LANG] + "\n".join(BKLANG) + "\n"
# ---- reference closure of the 0.1.6 files (every id / file they name exists: ours or Assets.zip)
_kbad = []
for _iid in BK_INTS:
    _d = INTS[_iid]
    for _r in refs_of(_d, set()):
        if _r not in INTS and _r not in ROOTS and not az_has("int", _r) and not az_has("root", _r):
            _kbad.append("%s -> %s" % (_iid, _r))
    if _d.get("Type") == "LaunchProjectile" and _d["ProjectileId"] not in PRJS:
        _kbad.append("%s launches %s" % (_iid, _d["ProjectileId"]))
    for _e in [_d] + [x for x in _d.get("Interactions") or [] if isinstance(x, dict)]:
        if _e.get("Type") == "Projectile" and (P_PCFG % _e["Config"]) not in ASSETS:
            _kbad.append("%s: config %s" % (_iid, _e["Config"]))
        _sn = (_e.get("Effects") or {}).get("WorldSoundEventId")
        if _sn and not az_has("sound", _sn):
            _kbad.append("%s: sound %s" % (_iid, _sn))
for _i in BK_ITEMS:
    for _slot, _rid in ITEMS[_i]["Interactions"].items():
        if _rid not in ROOTS:
            _kbad.append("%s %s -> %s" % (_i, _slot, _rid))
    for _f in ("Icon", "Texture", "Model"):
        if ("Common/" + ITEMS[_i][_f]) not in AZ_SET and ("Common/" + ITEMS[_i][_f]) not in ASSETS:
            _kbad.append("%s: %s %s" % (_i, _f, ITEMS[_i][_f]))
    if not az_has("quality", ITEMS[_i]["Quality"]) or ("Server/Audio/ItemSounds/%s.json" % ITEMS[_i].get("ItemSoundSetId", "ISS_Weapons_Books")) not in AZ_SET:
        _kbad.append("%s: quality / sound set" % _i)
for _cid, _c in KCFGS.items():
    if (P_MODEL % _c["Model"]) not in ASSETS:
        _kbad.append("%s: model %s" % (_cid, _c["Model"]))
    for _x in [x for k in ("ProjectileHit", "ProjectileMiss") for x in _c["Interactions"][k]["Interactions"]]:
        if _x.get("Parent") and not az_has("int", _x["Parent"]):
            _kbad.append("%s: parent %s" % (_cid, _x["Parent"]))
for _cid, _mm in KMODELS.items():
    _kbad += [p for p in [_mm["Model"], _mm["Texture"]] + [a["Model"] for a in _mm["DefaultAttachments"]] if ("Common/" + p) not in AZ_SET]
    _kbad += [a["Texture"] for a in _mm["DefaultAttachments"] if ("Common/" + a["Texture"]) not in ASSETS]
    _kbad += [t["TrailId"] for t in _mm.get("Trails") or [] if not az_has("trail", t["TrailId"])]
for _p in BK_PRJS:
    if PRJS[_p]["Appearance"] not in (MARKER,) and not az_has("model", PRJS[_p]["Appearance"]):
        _kbad.append("%s: appearance %s" % (_p, PRJS[_p]["Appearance"]))
assert not _kbad, "0.1.6 reference closure: %s" % _kbad
# the book chains' Mana: the check = the spend, a Failed branch spends nothing; the hold spends nothing (the server charges Levitate)
for _i, _m in enumerate(BOOK_METALS):
    _ch = INTS[ID_BROOT % _m]
    _sc = INTS[_ch["Next"]["0"]]
    _sp = sum(INTS[x]["StatModifiers"].get("Mana", 0) for r_ in _sc["Next"]["Interactions"] for x in r_["Interactions"] if INTS[x].get("Type") == "ChangeStat")
    assert _sc["Type"] == "StatsCondition" and _sc["Costs"] == {"Mana": BOOK[_m]["cost"]} and -_sp == BOOK[_m]["cost"] and _sc["Failed"] == ID_BFAIL, _m
    assert "Mana" not in json.dumps(INTS[_ch["Next"][BOOK_HOLD_KEY]]) and "Stamina" not in json.dumps([INTS[x] for x in BK_INTS]), _m
    assert abs(BOOK_TAP_RT + max(RT_LAUNCH, INTS[ID_BEFF]["RunTime"]) - 0.5) < 1e-9, "the tap cadence is 0.5 s (Medium)"
_ktxt = json.dumps(KCFGS) + json.dumps([INTS[x] for x in BK_INTS if x.startswith("SkyyArmory_Kunai")])
assert "ModifyInventory" not in _ktxt and '"Ammo"' not in _ktxt and "StatModifiers" not in _ktxt and "Costs" not in _ktxt, \
    "a kunai file names the inventory / ammo / a stat: the kunai must never be used up and its costs are the server's"
BK_FILES = sorted(set([P_BINT % i for i in BK_INTS if i.startswith("SkyyArmory_Spellbook")] + [P_KINT % i for i in BK_INTS if i.startswith("SkyyArmory_Kunai")]
                      + [P_BROOT % (ID_BROOT % m) for m in BOOK_METALS] + [P_KROOT % (r_ % m) for m in KUNAI_METALS for r_ in (ID_KROOT, ID_KRROOT)]
                      + [P_PRJ % p for p in BK_PRJS] + [P_PCFG % c for c in KCFGS] + [P_MODEL % c for c in KMODELS]
                      + [P_BITEM % m for m in BOOK_METALS] + [P_KITEM % m for m in KUNAI_METALS]
                      + ["Common/" + p % m for m in BOOK_METALS for p in (MODEL_BOOK, TEX_BOOK, ICON_BOOK)]
                      + ["Common/" + p % m for m in KUNAI_METALS for p in (TEX_KUNAI, ICON_KUNAI)]))
assert all(p in ASSETS for p in BK_FILES), [p for p in BK_FILES if p not in ASSETS][:5]
print("0.1.6 spellbooks: %s" % "; ".join("%s %d Mana / %d per target, r %s, %d targets, lev %s b %s s (art %s)" % (
    m, BOOK[m]["cost"], BOOK[m]["dmg"], bnum(BOOK_R[i]), BOOK_T[i], bnum(LEV_H[i]), bnum(LEV_S[i]), BOOK_REVIEW[m]) for i, m in enumerate(BOOK_METALS)))
print("0.1.6 kunai: %s" % "; ".join("%s hit %d (dagger avg %s, max %s) cd %s s %s St + %s Mana (art %s)" % (
    m, KUNAI_DMG[m], bnum(DAGGER[m]["mean"]), bnum(DAGGER[m]["max"]), bnum(K_CD[i]), bnum(K_STAM[i]), bnum(K_MANA[i]), KUNAI_REVIEW[m]) for i, m in enumerate(KUNAI_METALS)))
print("0.1.6 SkyyGear 0.2.8 note (the KUNAI TWIN: Weapon_Kunai_<Metal> takes Weapon_Daggers_<Metal>'s K): kunai hit / dagger average at the "
      "same level = %s (target 1.12 = 80 %% of the dagger DPS; only the whole-number rounding differs)" % ", ".join(
          "%s %.2f" % (m, KUNAI_DMG[m] / DAGGER[m]["mean"]) for m in KUNAI_METALS))
print("0.1.6 files: %d (%d interactions, %d projectiles, %d configs + models, 15 items, %d art files)" % (
    len(BK_FILES), len(BK_INTS), len(BK_PRJS), len(KCFGS), 3 * 7 + 2 * 8))

'''
before('''# ================================================================= the SET jars, SkyySkills (anchor + handover), the clash scan''', BK_ASSETS)
# the projectile id table assert (0.1.3) + the new projectiles
rep('''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST])) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) + 1 == len(PRJS) and set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST]) == set(PRJS)''',
    '''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS)) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) + 1 + len(BK_PRJS) == len(PRJS) \\
    and set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS) == set(PRJS)          # 0.1.6: + the book orbs / Levitate + return markers''')
# the partners: SkyyClasses 0.1.13 (spellbooks = Mage) and SkyyGear 0.2.8 (the kunai bands) once SkyyArmory 0.1.6 is pinned
rep('''CLASSES_PARTNER = "0.1.12"     # 0.1.1 (trav-fix): class:fn:heal; 0.1: 0.1.11 (the wand heal caps)''',
    '''CLASSES_PARTNER = "0.1.13"     # 0.1.6: spellbooks = Mage; 0.1.1 (trav-fix): class:fn:heal; 0.1: 0.1.11 (the wand heal caps)
GEAR_PARTNER = "0.2.8"         # 0.1.6: Weapon_Kunai_<Metal> bands by the metal word (0.2.7 puts them in the Kunai row 20-27)''')
rep('''        "SkyyArmory %s is pinned with SkyyClasses %s: pin SkyyClasses %s+ (the wand heal caps) in the same deploy" % (VERSION, _cpin, CLASSES_PARTNER))''',
    '''        "SkyyArmory %s is pinned with SkyyClasses %s: pin SkyyClasses %s+ (spellbooks = Mage) in the same deploy" % (VERSION, _cpin, CLASSES_PARTNER))
    _gpin = dict(PINS).get("SkyyGear")
    assert _gpin is not None and vtuple(_gpin) >= vtuple(GEAR_PARTNER), (
        "SkyyArmory %s is pinned with SkyyGear %s: pin SkyyGear %s+ (the kunai level bands) in the same deploy" % (VERSION, _gpin, GEAR_PARTNER))''')

# ================================================================================================ the per-metal tables + read-only rows + the file
BK_TABLES = r'''
# ---- 0.1.6: the per-metal tables (one row each, an entry per metal; Server Setup > Armory) and the read-only rows (costs + keys the client
# predicts are fixed in the jar, spec 7 rule of SkyyArmory)
BK_TAB = [  # (key, label, cat, value type, min, max, unit, help, ArmoryCfg field, defaults, metals)
    ("book.radius", "Burst radius by metal (blocks)", "book", "dec", "1", "12", "blocks", "Every enemy inside takes the per-target damage (nearest first).", "BOOK_R", BOOK_R, BOOK_METALS),
    ("book.targets", "Most burst targets by metal", "book", "int", "1", "20", "", "The direct target counts as one.", "BOOK_T", BOOK_T, BOOK_METALS),
    ("lev.height", "Levitate height by metal (blocks)", "lev", "dec", "2", "30", "blocks", "How high you rise (Copper 8 = Skyy's lock).", "LEV_H", LEV_H, BOOK_METALS),
    ("lev.hover", "Levitate hover by metal (s)", "lev", "dec", "0.5", "15", "s", "How long you hover, drifting the way you look.", "LEV_S", LEV_S, BOOK_METALS),
    ("lev.drift", "Levitate drift by metal (x walk)", "lev", "dec", "0", "3", "x", "Hover drift speed as a share of the walk speed (5.5 b/s).", "LEV_D", LEV_D, BOOK_METALS),
    ("lev.mana", "Levitate Mana by metal", "lev", "dec", "0", "200", "", "Paid once when you rise; at most 2 x the Stamina paid (10 at cap 5). Tooltips show the defaults.", "LEV_M", LEV_M, BOOK_METALS),
    ("lev.stamina", "Levitate Stamina by metal", "lev", "dec", "0", "10", "", "Paid once when you rise (trav.staminaCap applies). Tooltips show the default cap 5.", "LEV_ST", LEV_ST, BOOK_METALS),
    ("kunai.range", "Teleport range by metal (blocks)", "kunai", "int", "5", "40", "blocks", "Past it you appear where the kunai left your range (Skyy: 20).", "K_RANGE", K_RANGE, KUNAI_METALS),
    ("kunai.cooldown", "Teleport cooldown by metal (s)", "kunai", "dec", "0", "30", "s", "A hold inside it throws a normal kunai.", "K_CD", K_CD, KUNAI_METALS),
    ("kunai.stamina", "Teleport Stamina by metal", "kunai", "dec", "0", "10", "", "Paid at the throw; refunded if you do not move. trav.staminaCap applies; tooltips show cap 5.", "K_STAM", K_STAM, KUNAI_METALS),
    ("kunai.mana", "Teleport Mana by metal", "kunai", "dec", "0", "50", "", "Paid at the throw; refunded when you do not move.", "K_MANA", K_MANA, KUNAI_METALS),
    ("ret.window", "Return window by metal (s)", "kunai", "dec", "1", "30", "s", "Hold right click within this to go back to where you were.", "K_WIN", K_WIN, KUNAI_METALS),
    ("ret.radius", "Return knockback by metal (blocks)", "kunai", "dec", "0", "10", "blocks", "Enemies this close to your return spot are pushed away.", "K_RAD", K_RAD, KUNAI_METALS),
]
BK_TAB_ROWS = []
for _k, _lab, _cat, _vt, _mn, _mx, _u, _hlp, _fld, _defs, _ms in BK_TAB:
    _chk = "ArmoryHooks.checkBook" if _ms is BOOK_METALS else "ArmoryHooks.checkKunai"
    BK_TAB_ROWS.append((_k, _lab, _cat, "table", "", _mn, _mx, "%s;none;%s" % (_vt, "Value"), _u, "live", _hlp,
                        "reload@%s:%s.;check=%s" % (CFG_FILE, _k, _chk)))
BK_TAB_LINES = []
for _k, _lab, _cat, _vt, _mn, _mx, _u, _hlp, _fld, _defs, _ms in BK_TAB:
    BK_TAB_LINES.append("# " + _lab + ": " + _hlp)
    BK_TAB_LINES += ["%s.%s=%s" % (_k, _m, num(_d)) for _m, _d in zip(_ms, _defs)]
'''
before('''CFG_LINES = [''', BK_TABLES)
BK_FIXED = r'''
FIXED.append(("fixed.book.costShare", "Book Mana rule (fixed in the jar)", "book", "%d %% of the Mage pool at the band start (spec 2), rounded to 5" % int(BOOK_SHARE * 100),
              "The Page Burst Mana is client-predicted (in the chain) - it changes only with a new build."))
for _i, _m in enumerate(BOOK_METALS):
    FIXED.append(("fixed.book.%s" % _m, "%s Spellbook (fixed in the jar)" % _m, "book",
                  "%d Mana - %d damage per target before levels - Lv %d-%d - the %s shortbow recipe" % (
                      BOOK[_m]["cost"], BOOK[_m]["dmg"], BANDS[_m][0], BANDS[_m][1], "Mithril (Onyxium bars)" if _m == "Onyxium" else _m),
                  "Page Burst Mana (30 % of the pool), damage x book.k / 0.4, level band, recipe."))
FIXED.append(("fixed.kunai.keys", "Kunai keys (fixed in the jar)", "kunai", "tap = throw, hold %s s = teleport, right click hold %s s = return" % (KUNAI_CHARGE, KUNAI_RET_KEY),
              "Client-predicted charge keys (Kunai-Ladder 9 kunai.charge 0.6)."))
for _i, _m in enumerate(KUNAI_METALS):
    FIXED.append(("fixed.kunai.%s" % _m, "%s Kunai (fixed in the jar)" % _m, "kunai",
                  "hit %d (1.12 x the %s daggers' %s) - Lv %d-%d - the %s daggers recipe" % (
                      KUNAI_DMG[_m], _m, num(DAGGER[_m]["mean"]), 1 if _m == "Crude" else BANDS[_m][0], 13 if _m == "Crude" else BANDS[_m][1],
                      "Mithril (Onyxium bars)" if _m == "Onyxium" else _m),
                  "Hit before levels (x kunai.dpsShare / 0.8), level band, recipe."))
'''
before('''FIXED_VAL = dict((f[0], f[3]) for f in FIXED)''', BK_FIXED)
rep('''] + [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], "field:ArmoryCfg." + r[11]) for r in CFG_NEW] + [''',
    '''] + [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], "field:ArmoryCfg." + r[11]) for r in CFG_NEW] + BK_TAB_ROWS + [''')
rep('''CFG_CATS = [("trav", "Traversal"), ("blink", "Staff blink"), ("hop", "Wand hop + burst"), ("grapple", "Crossbow grapple"), ("bow", "Bow leap + blast"),''',
    '''CFG_CATS = [("trav", "Traversal"), ("blink", "Staff blink"), ("hop", "Wand hop + burst"), ("grapple", "Crossbow grapple"), ("bow", "Bow leap + blast"),
            ("book", "Spellbook burst"), ("lev", "Spellbook Levitate"), ("kunai", "Kunai"),''')
rep('''    "",
    "# ---- Mana check (server log)",''', '''    "",
    "# ---- spellbooks (SkyyArmory 0.1.6; research/cloud/Spellbook-Ladder.md, Skyy 2026-10-07): tap = Page Burst, hold 1 s = Levitate",
] + [x for _r in CFG_BK if _r[2] in ("book", "lev") for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [x for x in BK_TAB_LINES if x.startswith(("# Burst", "# Most", "# Levitate", "book.", "lev."))] + [
    "",
    "# ---- kunai (SkyyArmory 0.1.6; research/cloud/Kunai-Ladder.md, Skyy 2026-10-07): tap = throw, hold 0.6 s = throw + teleport, right click hold = return",
] + [x for _r in CFG_BK if _r[2] == "kunai" for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [x for x in BK_TAB_LINES if x.startswith(("# Teleport", "# Return", "kunai.", "ret."))] + [
    "",
    "# ---- Mana check (server log)",''')
# the table defaults are in the default file (a key-family table's default entries)
after('''assert all(_dp.get(k) == "100" for k in TUNE_KEYS_W + TUNE_KEYS_S)
''', '''for _k, _lab, _cat, _vt, _mn, _mx, _u, _hlp, _fld, _defs, _ms in BK_TAB:        # 0.1.6: every table entry's default is in the file
    assert [_dp.get("%s.%s" % (_k, _m)) for _m in _ms] == [num(_d) for _d in _defs], (_k, [_dp.get("%s.%s" % (_k, _m)) for _m in _ms])
assert len(BK_TAB_LINES) == sum(1 + len(t[10]) for t in BK_TAB) and all(_l in CFG_TEXT for _l in BK_TAB_LINES), "0.1.6 table lines in the default file"
''')
rep('''               FILES=[CFG_FILE], NOTE="Tap = quick shot, hold = charged shot. Costs + art are fixed in the jar.",''',
    '''               FILES=[CFG_FILE], NOTE="Tap = the quick move, hold = the charged move or traversal. Costs + art are fixed in the jar.",''')

# ================================================================================================ ArmoryCfg: the table fields, the loader, the texts
after('''for _r in CFG_NEW:            # 0.1.1 traversal settings (field: rows of the kit; ArmoryCfg.apply reads them the same way)
    F(cfg, "public static volatile %s %s = %s;" % (_r[12], _r[11], ('"%s"' % _r[13]) if _r[12] == "String" else (repr(float(_r[13])) if _r[12] == "double" else _r[13])))
''', '''for _k, _lab, _cat, _vt, _mn, _mx, _u, _hlp, _fld, _defs, _ms in BK_TAB:        # 0.1.6 per-metal tables (index = BOOK_METALS / KUNAI_METALS)
    F(cfg, "public static volatile double[] %s = %s;" % (_fld, jdbls(_defs)))
    F(cfg, "public static final double[] %s_DEF = %s;" % (_fld, jdbls(_defs)))
for f in ("public static volatile String BOOK_TEXT = \\"\\";", "public static volatile String KUNAI_TEXT = \\"\\";"):
    F(cfg, f)
''')
BK_CFG_M = r'''# 0.1.6: a per-metal table (key family prefix + metal), clamped like the kit validates
M(cfg, r"""
public static double[] tab(java.util.Properties p, String prefix, String[] ms, double[] defs, double lo, double hi) {
  double[] out = new double[ms.length];
  for (int i = 0; i < ms.length; i++) out[i] = dec(p.getProperty(prefix + ms[i]), defs[i], lo, hi);
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith(prefix)) continue;
    String e = k.substring(prefix.length());
    boolean known = false;
    for (int i = 0; i < ms.length; i++) if (ms[i].equals(e)) known = true;
    if (!known) @PKG@.ArmoryLog.warnOnce("tab:" + k, "config.properties: " + k + " is not a metal of this table - ignored");
  }
  return out;
}""")
M(cfg, r"""
public static String cfmt(double v) {
  if (Double.isNaN(v) || Double.isInfinite(v)) return "0";
  double r = Math.floor(v * 100.0 + 0.5) / 100.0;
  if (Math.abs(r - Math.floor(r)) < 1.0E-9) return String.valueOf((long) Math.floor(r));
  return String.valueOf(r);
}""")
M(cfg, r"""
public static String bookText() {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < @PKG@.ArmoryDefs.B_METALS.length; i++) {
    if (i > 0) sb.append(", ");
    sb.append(@PKG@.ArmoryDefs.B_METALS[i]).append(' ').append(cfmt(BOOK_R[i])).append("b/").append((int) Math.round(BOOK_T[i]))
      .append(" lev ").append(cfmt(LEV_H[i])).append("b ").append(cfmt(LEV_S[i])).append("s ")
      .append(cfmt(LEV_M[i])).append("M+").append(cfmt(LEV_ST[i])).append("St");
  }
  return "spellbooks " + (PART_BOOK ? "on" : "OFF") + " - Page Burst k " + BOOK_K + ", orb range " + BOOK_RANGE + ", edge -" + BOOK_FALL
    + " pct - Levitate rise " + LEV_RISE + " b/s, safe " + LEV_SAFE + " s after the hover, float " + LEV_FLOAT + " b/s, crouch ends "
    + (LEV_CROUCH ? "on" : "off") + " - " + sb.toString();
}""")
M(cfg, r"""
public static String kunaiText() {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < @PKG@.ArmoryDefs.K_METALS.length; i++) {
    if (i > 0) sb.append(", ");
    sb.append(@PKG@.ArmoryDefs.K_METALS[i]).append(' ').append((int) Math.round(K_RANGE[i])).append("b cd ").append(cfmt(K_CD[i]))
      .append("s ").append(cfmt(K_STAM[i])).append("St+").append(cfmt(K_MANA[i])).append("M ret ")
      .append(cfmt(K_WIN[i])).append("s/").append(cfmt(K_RAD[i])).append("b");
  }
  return "kunai teleport " + (PART_KUNAI ? "on" : "OFF") + " - dps share " + K_SHARE + ", throw " + K_THROW_RANGE + " blocks, flight " + K_TTL
    + " s, ground " + K_FLOOR + ", behind mob " + (K_BEHIND ? "on" : "off") + ", arenas " + (K_NOARENA ? "blocked" : "free") + ", combat "
    + (K_NOCOMBAT ? "blocked" : "free") + ", players " + K_PVP + ", " + K_MAXMIN + " per minute, return push x" + K_FORCE + " dmg " + K_RDMG + " pct - " + sb.toString();
}""")
'''
before('''M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''', BK_CFG_M)
after('''  LEAP_TEXT = leapText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:leap", LEAP_TEXT); } catch (Throwable tl) { }
''', '''  PART_BOOK = bool(c.getProperty("part.book"), true);
  BOOK_K = dec(c.getProperty("book.k"), 0.4, 0.1, 1.0);
  BOOK_RANGE = intOf(c.getProperty("book.range"), 20, 4, 64);
  BOOK_FALL = intOf(c.getProperty("book.edgeFalloff"), 0, 0, 90);
  BOOK_R = tab(c, "book.radius.", @PKG@.ArmoryDefs.B_METALS, BOOK_R_DEF, 1.0, 12.0);
  BOOK_T = tab(c, "book.targets.", @PKG@.ArmoryDefs.B_METALS, BOOK_T_DEF, 1.0, 20.0);
  LEV_H = tab(c, "lev.height.", @PKG@.ArmoryDefs.B_METALS, LEV_H_DEF, 2.0, 30.0);
  LEV_S = tab(c, "lev.hover.", @PKG@.ArmoryDefs.B_METALS, LEV_S_DEF, 0.5, 15.0);
  LEV_D = tab(c, "lev.drift.", @PKG@.ArmoryDefs.B_METALS, LEV_D_DEF, 0.0, 3.0);
  LEV_M = tab(c, "lev.mana.", @PKG@.ArmoryDefs.B_METALS, LEV_M_DEF, 0.0, 200.0);
  LEV_ST = tab(c, "lev.stamina.", @PKG@.ArmoryDefs.B_METALS, LEV_ST_DEF, 0.0, 10.0);
  LEV_SAFE = dec(c.getProperty("lev.safeAfter"), 3.0, 0.0, 10.0);
  LEV_CROUCH = bool(c.getProperty("lev.crouchLands"), true);
  LEV_RISE = dec(c.getProperty("lev.riseSpeed"), 10.0, 3.0, 30.0);
  LEV_FLOAT = dec(c.getProperty("lev.floatFall"), 6.0, 0.0, 20.0);
  BOOK_TEXT = bookText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:book", BOOK_TEXT); } catch (Throwable tbk) { }
  PART_KUNAI = bool(c.getProperty("part.kunai"), true);
  K_SHARE = dec(c.getProperty("kunai.dpsShare"), 0.8, 0.3, 1.5);
  K_THROW_RANGE = intOf(c.getProperty("kunai.throwRange"), 20, 5, 40);
  K_TTL = dec(c.getProperty("kunai.flightTtl"), 1.5, 0.3, 5.0);
  K_FLOOR = intOf(c.getProperty("kunai.floorCheck"), 0, 0, 64);
  K_BEHIND = bool(c.getProperty("kunai.behindMob"), false);
  K_NOARENA = bool(c.getProperty("kunai.noArena"), true);
  K_NOCOMBAT = bool(c.getProperty("kunai.noCombat"), false);
  K_PVP = "never".equalsIgnoreCase(String.valueOf(c.getProperty("kunai.pvp")).trim()) ? "never" : "world";
  K_MAXMIN = intOf(c.getProperty("kunai.maxPerMinute"), 12, 0, 120);
  K_FORCE = dec(c.getProperty("ret.force"), 1.0, 0.0, 3.0);
  K_RDMG = intOf(c.getProperty("ret.damage"), 0, 0, 200);
  K_RANGE = tab(c, "kunai.range.", @PKG@.ArmoryDefs.K_METALS, K_RANGE_DEF, 5.0, 40.0);
  K_CD = tab(c, "kunai.cooldown.", @PKG@.ArmoryDefs.K_METALS, K_CD_DEF, 0.0, 30.0);
  K_STAM = tab(c, "kunai.stamina.", @PKG@.ArmoryDefs.K_METALS, K_STAM_DEF, 0.0, 10.0);
  K_MANA = tab(c, "kunai.mana.", @PKG@.ArmoryDefs.K_METALS, K_MANA_DEF, 0.0, 50.0);
  K_WIN = tab(c, "ret.window.", @PKG@.ArmoryDefs.K_METALS, K_WIN_DEF, 1.0, 30.0);
  K_RAD = tab(c, "ret.radius.", @PKG@.ArmoryDefs.K_METALS, K_RAD_DEF, 0.0, 10.0);
  KUNAI_TEXT = kunaiText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:kunai", KUNAI_TEXT); } catch (Throwable tku) { }
''')

# ================================================================================================ ArmoryHooks: the two table checks
before('''M(hooks, r"""
public static String customGet(String key) {''', '''# 0.1.6: the book / kunai tables take only their metals
M(hooks, r"""
public static String checkIn(String key, String value, String[] ms, String words) {
  if (key == null) return null;
  int a = key.indexOf('[');
  int b = key.lastIndexOf(']');
  if (a < 0 || b < a) return null;
  String e = key.substring(a + 1, b);
  for (int i = 0; i < ms.length; i++) if (ms[i].equals(e)) return null;
  if (value == null) return null;
  return "Not a metal of this table - use " + words + ".";
}""")
M(hooks, "public static String checkBook(String key, String value) { return checkIn(key, value, @PKG@.ArmoryDefs.B_METALS, \\"Copper, Iron, Thorium, Cobalt, Adamantite, Mithril or Onyxium\\"); }")
M(hooks, "public static String checkKunai(String key, String value) { return checkIn(key, value, @PKG@.ArmoryDefs.K_METALS, \\"Crude, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril or Onyxium\\"); }")
''')

# ================================================================================================ ArmoryDefs: the 0.1.6 tables, codes, item indexes
after('''          "public static volatile java.util.HashMap ITEM = null;"):
    F(dfs, f)
''', '''for f in ("public static final String[] B_METALS = %s;" % jarr(BOOK_METALS),           # 0.1.6 spellbooks
          "public static final String[] B_IDS = %s;" % jarr(["Weapon_Spellbook_" + m for m in BOOK_METALS]),
          "public static final String[] B_BURST = %s;" % jarr([ID_BBURST % m for m in BOOK_METALS]),
          "public static final String[] B_LEVM = %s;" % jarr([ID_BLEVM % m for m in BOOK_METALS]),
          "public static final int[] B_COST = %s;" % jints([BOOK[m]["cost"] for m in BOOK_METALS]),
          "public static final int[] B_DMG = %s;" % jints([BOOK[m]["dmg"] for m in BOOK_METALS]),
          "public static final String[] K_METALS = %s;" % jarr(KUNAI_METALS),           # 0.1.6 kunai
          "public static final String[] K_IDS = %s;" % jarr(["Weapon_Kunai_" + m for m in KUNAI_METALS]),
          "public static final String[] K_THROW = %s;" % jarr([ID_KCFG_T % m for m in KUNAI_METALS]),
          "public static final String[] K_PORT = %s;" % jarr([ID_KCFG_P % m for m in KUNAI_METALS]),
          "public static final String[] K_RMARK = %s;" % jarr([ID_KRMARK % m for m in KUNAI_METALS]),
          "public static final int[] K_DMG = %s;" % jints([KUNAI_DMG[m] for m in KUNAI_METALS]),
          "public static final double BOOK_KDEF = %r;" % BOOK_KDEF, "public static final double K_SHARE_DEF = %r;" % KUNAI_SHARE_DEF):
    F(dfs, f)
''')
after('''  m.put(BLAST, Integer.valueOf(BLAST_CODE));          // 0.1.3: the bow leap's blast arrow
''', '''  for (int i = 0; i < B_BURST.length; i++) m.put(B_BURST[i], Integer.valueOf(7000 + i));     // 0.1.6: the Page Burst orbs
  for (int i = 0; i < B_LEVM.length; i++) m.put(B_LEVM[i], Integer.valueOf(8000 + i));       // 0.1.6: the Levitate markers
  for (int i = 0; i < K_RMARK.length; i++) m.put(K_RMARK[i], Integer.valueOf(9000 + i));     // 0.1.6: the kunai return markers
''')
after('''  for (int i = 0; i < S_IDS.length; i++) m.put(S_IDS[i], Integer.valueOf(200 + i));
''', '''  for (int i = 0; i < B_IDS.length; i++) m.put(B_IDS[i], Integer.valueOf(300 + i));          // 0.1.6
  for (int i = 0; i < K_IDS.length; i++) m.put(K_IDS[i], Integer.valueOf(400 + i));
''')
before('''# THE damage rule of ArmoryTuneSys (spec 3.1 + 15.2), plain values only: 1 = untouched''', '''# 0.1.6: book / kunai item index, the kunai's model id -> throw i / teleport 100 + i (-1 = not ours)
M(dfs, r"""
public static int bookIndex(String id) {
  if (id == null) return -1;
  Object o = items().get(id);
  int c = o instanceof Integer ? ((Integer) o).intValue() : -1;
  return c >= 300 && c < 400 ? c - 300 : -1;
}""")
M(dfs, r"""
public static int kunaiIndex(String id) {
  if (id == null) return -1;
  Object o = items().get(id);
  int c = o instanceof Integer ? ((Integer) o).intValue() : -1;
  return c >= 400 && c < 500 ? c - 400 : -1;
}""")
M(dfs, r"""
public static int kunaiModel(String mid) {
  if (mid == null || !mid.startsWith("SkyyArmory_Kunai_")) return -1;
  for (int i = 0; i < K_THROW.length; i++) {
    if (K_THROW[i].equals(mid)) return i;
    if (K_PORT[i].equals(mid)) return 100 + i;
  }
  return -1;
}""")
''')

# ================================================================================================ engine members the 0.1.6 code calls (probed)
after('''    "INVU": "com.hypixel.hytale.server.core.modules.entity.component.Invulnerable",     # FIX ROUND: never yank an Invulnerable mob (traders)
})''', '''
T.update({   # 0.1.6 Levitate (crouch, walk speed) + kunai (the hit's source) - VERIFIED by reflection 2026-10-07; every member is probed below
    "MSC": "com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent",
    "MST": "com.hypixel.hytale.protocol.MovementStates",
})''')
before('''print("engine members probed: %d" % len(PROBED))''', '''# ---- 0.1.6: Levitate reads the crouch state + the walk speed, the kunai's combat row the hit's attacker
SIGS6 = [(T["MSC"], "getComponentType", T["CTYPE"], []), (T["MSC"], "getMovementStates", T["MST"], []),
         (T["MCF"], "getBaseSpeed", "float", []), (T["MCF"], "getForwardRunSpeedMultiplier", "float", []),
         (T["DENT"], "getRef", T["REF"], []), (T["VEL"], "getClientVelocity", T["VEC"], []),
         (T["SPPV"], "setImpactConsumer", "void", [T["IMPC"]]), (T["SPPV"], "getImpactConsumer", T["IMPC"], [])]
for _c, _m, _r, _a in SIGS6:
    probe_sig(_c, _m, _r, _a)
for _f in ("crouching",):
    assert JMod.isPublic(pool.get(T["MST"]).getField(_f).getModifiers()), "MovementStates.%s is not public" % _f
    PROBED.append("MovementStates.%s" % _f)
_mcfd = json.loads(AZ.read("Server/Entity/MovementConfig/Default.json").decode("utf-8-sig"))
assert _mcfd["BaseSpeed"] * _mcfd.get("ForwardRunSpeedMultiplier", 1.0) == LEV_WALK_DEF, "the walk speed changed: %s" % _mcfd["BaseSpeed"]
PROBED.append("MovementConfig Default BaseSpeed %s x ForwardRun %s (Assets.zip)" % (_mcfd["BaseSpeed"], _mcfd.get("ForwardRunSpeedMultiplier")))
''')

# ================================================================================================ the classes (declared up front: javassist needs them)
rep('''leap = pool.makeClass(PKG + ".Leap")
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick,
       gmath, gstate, grap, gimp, gbolt, gfall, lstate, leap]''', '''leap = pool.makeClass(PKG + ".Leap")
# 0.1.6 spellbook Levitate + the kunai: per-player records, the glue, the impact wrapper, the world-thread job
lvst = pool.makeClass(PKG + ".LevState")
levc = pool.makeClass(PKG + ".Levitate")
kst = pool.makeClass(PKG + ".KunaiState")
kimp = pool.makeClass(PKG + ".KunaiImpact")
kjob = pool.makeClass(PKG + ".KunaiJob")
kun = pool.makeClass(PKG + ".Kunai")
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick,
       gmath, gstate, grap, gimp, gbolt, gfall, lstate, leap, lvst, levc, kst, kimp, kjob, kun]''')

# ================================================================================================ TravMath: the pure 0.1.6 maths (bare-JVM tested)
after('''M(tmath, "public static boolean emitOk(long now, long emitMs, long until) { return now + emitMs <= until; }")
''', '''# 0.1.6 Levitate: the hover holds its height - a Set of (target - y) x 4, at most 3 b/s either way
M(tmath, r"""
public static double holdVy(double target, double y) {
  if (Double.isNaN(target) || Double.isNaN(y)) return 0.0;
  double v = (target - y) * 4.0;
  if (v > 3.0) v = 3.0;
  if (v < -3.0) v = -3.0;
  return v;
}""")
# 0.1.6 Page Burst: base x (1 - pct % x d / r) - 0 % = the full damage everywhere
M(tmath, r"""
public static double falloff(double base, double d, double r, int pct) {
  if (!(base > 0.0)) return 0.0;
  if (pct <= 0 || !(r > 0.0)) return base;
  double t = d / r;
  if (t < 0.0) t = 0.0;
  if (t > 1.0) t = 1.0;
  return base * (1.0 - (double) pct / 100.0 * t);
}""")
# 0.1.6 kunai return: the spot itself when the body fits there, else the nearest landing spot (body free + ground within floor) within maxR -
# rings every 0.5 block, 16 directions, the same height then 1 up then 1 down; null = none (no return)
M(tmath, r"""
public static double[] safeNear(@PKG@.TravGrid g, double x, double y, double z, double maxR, int floor) {
  if (g == null) return null;
  if (body(g, x, y, z) == 0) return new double[] { x, y, z };
  double[] dy = new double[] { 0.0, 1.0, -1.0 };
  for (double r = 0.5; r <= maxR + 1.0E-9; r = r + 0.5) {
    for (int h = 0; h < dy.length; h++) {
      for (int k = 0; k < 16; k++) {
        double a = Math.PI * 2.0 * (double) k / 16.0;
        double px = x + Math.cos(a) * r;
        double pz = z + Math.sin(a) * r;
        if (spot(g, px, y + dy[h], pz, floor) == 1) return new double[] { px, y + dy[h], pz };
      }
    }
  }
  return null;
}""")
# 0.1.6 kunai landing: from the feet, toward the point - a hit on the ground (a solid block right under the point, free above) goes feet -> point; a wall
# or a mob goes the way the kunai flew (eye -> point, so a level throw at a wall lands you on the ground in front of it). A mob: 1 block short
# of it (half its width more), or behind it with behind on. -> { dx, dy, dz, maxD }
M(tmath, r"""
public static double[] kunaiAim(@PKG@.TravGrid g, double fx, double fy, double fz, double tx, double ty, double tz, boolean mob, double thick, boolean behind) {
  double ex = fx;
  double ey = fy + 1.6;
  double ez = fz;
  boolean ground = !mob && g != null && g.at((int) Math.floor(tx), (int) Math.floor(ty - 0.3), (int) Math.floor(tz)) == 1
    && g.at((int) Math.floor(tx), (int) Math.floor(ty + 0.3), (int) Math.floor(tz)) == 0;          // a top face: solid under, free above
  double dx = ground ? tx - fx : tx - ex;
  double dy = ground ? ty - fy : ty - ey;
  double dz = ground ? tz - fz : tz - ez;
  double d = Math.sqrt(dx * dx + dy * dy + dz * dz);
  double maxD = d + 0.3;
  if (mob) maxD = behind ? d + thick + 0.6 : d - 1.0 - thick * 0.5;
  return new double[] { dx, dy, dz, maxD };
}""")
''')

# ================================================================================================ TravWorld: the book orbs' range watch
rep('''for f in ("public java.util.ArrayList fx;", "public java.util.HashMap quick;", "public java.util.HashMap orbs;", "public java.util.HashMap pend;",
          "public long lastNs;"):''', '''for f in ("public java.util.ArrayList fx;", "public java.util.HashMap quick;", "public java.util.HashMap orbs;", "public java.util.HashMap pend;",
          "public long lastNs;", "public java.util.HashMap books;"):          # 0.1.6: the Page Burst orbs in flight (range watch)''')
rep('''  this.pend = new java.util.HashMap();
  this.lastNs = 0L;''', '''  this.pend = new java.util.HashMap();
  this.lastNs = 0L;
  this.books = new java.util.HashMap();''')
rep('''M(tworld, "public boolean idle() { return this.fx.isEmpty() && this.quick.isEmpty() && this.orbs.isEmpty() && this.pend.isEmpty(); }")''',
    '''M(tworld, "public boolean idle() { return this.fx.isEmpty() && this.quick.isEmpty() && this.orbs.isEmpty() && this.pend.isEmpty() && this.books.isEmpty(); }")''')
before('''  java.util.Iterator io = this.orbs.keySet().iterator();''', '''  java.util.Iterator ib = this.books.entrySet().iterator();          // 0.1.6: a Page Burst orb past book.range bursts there
  while (ib.hasNext()) {
    java.util.Map.Entry eb = (java.util.Map.Entry) ib.next();
    @REF@ rb = (@REF@) eb.getKey();
    @PKG@.TravShot sb = (@PKG@.TravShot) eb.getValue();
    if (rb == null || !rb.isValid()) { ib.remove(); continue; }
    @VEC@ pb = @PKG@.ArmoryTrav.posOf(buf, rb);
    if (pb == null) continue;
    double bx = pb.x - sb.sx;
    double by = pb.y - sb.sy;
    double bz = pb.z - sb.sz;
    if (bx * bx + by * by + bz * bz > sb.range * sb.range) {
      ib.remove();
      try { buf.removeEntity(rb, @REMR@.REMOVE); @PKG@.ArmoryTrav.BOOK_RANGED = @PKG@.ArmoryTrav.BOOK_RANGED + 1L; } catch (Throwable tb) { }
    }
  }
''')

# ================================================================================================ ArmoryTrav: counters + the Page Burst
before('''M(trav, r"""
public static void warn(String key, String msg) { @PKG@.ArmoryLog.warnOnce("trav:" + key, msg); }""")''',
       '''for f in ("public static volatile long BOOK_BURSTS = 0L;", "public static volatile long BOOK_HITS = 0L;", "public static volatile long BOOK_RANGED = 0L;",
          "public static final String SND_BOOK = %s;" % jstr(SND_BOOK_HIT)):         # 0.1.6
    F(trav, f)
''')
BK_BURST = r'''# ---- 0.1.6 THE PAGE BURST (Spellbook-Ladder 2): every enemy inside the tier's radius, NEAREST FIRST, up to the targets cap (the direct
# target counts as one), takes `base` through the whole damage pipeline (ArmoryTuneSys x book.k / 0.4, SkyyGear, armour) - players only where
# PvP is on (+ trav.players), never allies; book.edgeFalloff % less at the edge. A miss / the range: base = the asset damage x the tune
M(trav, r"""
public static double bookBase(int bi) {
  if (bi < 0 || bi >= @PKG@.ArmoryDefs.B_DMG.length) return 0.0;
  double b = (double) @PKG@.ArmoryDefs.B_DMG[bi];
  if (@PKG@.ArmoryCfg.PART_TUNE) b = b * @PKG@.ArmoryCfg.BOOK_K / @PKG@.ArmoryDefs.BOOK_KDEF;
  return b;
}""")
M(trav, r"""
public static int bookBurst(@ST@ st, @CB@ buf, @REF@ proj, @PKG@.TravShot s, double cx, double cy, double cz, @REF@ direct, double base) {
  if (s == null || !@PKG@.ArmoryCfg.PART_BOOK) return 0;
  int bi = s.code % 1000;
  if (bi < 0 || bi >= @PKG@.ArmoryDefs.B_IDS.length) return 0;
  if (!allowed(s.caster, @PKG@.ArmoryDefs.B_IDS[bi])) { LAST_WHY = "book: class lock"; return 0; }
  @REF@ caster = null;
  try { caster = s.caster == null ? null : ((@ES@) buf.getExternalData()).getRefFromUUID(s.caster); } catch (Throwable t0) { caster = null; }
  boolean pvp = pvp(worldOf(buf));
  BOOK_BURSTS = BOOK_BURSTS + 1L;
  double r = @PKG@.ArmoryCfg.BOOK_R[bi];
  int cap = (int) Math.round(@PKG@.ArmoryCfg.BOOK_T[bi]);
  int got = direct != null ? 1 : 0;
  int hits = 0;
  if (base > 0.0 && caster != null && caster.isValid() && r > 0.0 && got < cap) {
    java.util.List l = near(buf, cx, cy, cz, r);
    int n = l.size();
    @REF@[] rs = new @REF@[n];
    double[] ds = new double[n];
    int m = 0;
    for (int k = 0; k < n; k++) {
      @REF@ t = (@REF@) l.get(k);
      if (t == null || (direct != null && t.equals(direct))) continue;
      if (kind(buf, t, caster, s.caster, pvp) != 0) continue;
      @VEC@ tp = posOf(buf, t);
      if (tp == null) continue;
      double dx = tp.x - cx;
      double dy = tp.y + 0.9 - cy;
      double dz = tp.z - cz;
      rs[m] = t;
      ds[m] = Math.sqrt(dx * dx + dy * dy + dz * dz);
      m++;
    }
    for (int a = 0; a < m && got < cap; a++) {
      int best = a;
      for (int b = a + 1; b < m; b++) if (ds[b] < ds[best]) best = b;
      @REF@ tr = rs[best];
      double td = ds[best];
      rs[best] = rs[a];
      ds[best] = ds[a];
      rs[a] = tr;
      ds[a] = td;
      if (hit(buf, tr, caster, proj, @PKG@.TravMath.falloff(base, td, r, @PKG@.ArmoryCfg.BOOK_FALL))) { got++; hits++; BOOK_HITS = BOOK_HITS + 1L; }
    }
  }
  particle(PS_BURST, cx, cy, cz, buf);
  if (r > 0.0) {          // fix2 (spec 2: the burst reads as a ring): the finite blue ring points at the tier's radius (they vanish on their own)
    for (int q = 0; q < 12; q++) {
      double qa = Math.PI * 2.0 * (double) q / 12.0;
      particle(PS_RING, cx + Math.cos(qa) * r, cy, cz + Math.sin(qa) * r, buf);
    }
  }
  sound(SND_BOOK, cx, cy, cz, buf);
  LAST_WHY = "book burst: " + got + " of " + cap + " targets";
  return hits;
}""")
'''
before('''M(trav, r"""
public static double[] hitAt(@DMG@ d, @CB@ buf, @REF@ tg) {''', BK_BURST)

# ================================================================================================ ArmoryTravSys / ArmoryHitSys wiring (added, landed, removed)
rep('''  java.util.UUID cu = pc.getCreatorUuid();
  String pid = pc.getProjectileAssetName();
  if ((c >= 1000 && c < 2000) || (c >= 3000 && c < 4000)) {''', '''  java.util.UUID cu = pc.getCreatorUuid();
  String pid = pc.getProjectileAssetName();
  if (c >= 7000 && c < 8000) {          // 0.1.6: a Page Burst orb -> the burst record + the range watch (book off = a plain orb)
    if (!@PKG@.ArmoryCfg.PART_BOOK || p == null) return;
    @PKG@.TravShot sbk = new @PKG@.TravShot(p.x, p.y, p.z, (double) @PKG@.ArmoryCfg.BOOK_RANGE, c, cu, pid);
    tw.orbs.put(ref, sbk);
    tw.books.put(ref, sbk);
    return;
  }
  if (c >= 8000 && c < 9000) { @PKG@.Levitate.begin(ref, pc, c, st, buf); return; }          // 0.1.6: the spellbook hold
  if (c >= 9000 && c < 10000) { @PKG@.Kunai.recallMarker(ref, pc, c, st, buf); return; }     // 0.1.6: the kunai return
  if ((c >= 1000 && c < 2000) || (c >= 3000 && c < 4000)) {''')
rep('''  if (c >= 6000 && c < 7000) {          // 0.1.3: the blast arrow's direct hit -> the blast around it (once)''',
    '''  if (c >= 7000 && c < 8000) {          // 0.1.6: a Page Burst orb's direct hit -> the burst around it (once; the direct target counts)
    @PKG@.TravShot sk = (@PKG@.TravShot) tw.orbs.get(pj);
    if (sk == null || sk.count > 0) return;
    sk.count = 1;
    double[] hk = hitAt(d, buf, tg);
    if (hk != null) bookBurst(st, buf, pj, sk, hk[0], hk[1], hk[2], tg, (double) d.getInitialAmount());
    return;
  }
  if (c >= 6000 && c < 7000) {          // 0.1.3: the blast arrow's direct hit -> the blast around it (once)''')
rep('''  @PKG@.TravShot s = (@PKG@.TravShot) tw.orbs.remove(ref);
  if (s != null && s.code >= 6000 && s.code < 7000) {''', '''  @PKG@.TravShot s = (@PKG@.TravShot) tw.orbs.remove(ref);
  tw.books.remove(ref);
  if (s != null && s.code >= 7000 && s.code < 8000) {          // 0.1.6: a Page Burst orb that hit no one (a block, the range) bursts where it ended
    if (s.count == 0 && removeReason) {
      @VEC@ pk = posOf(buf, ref);
      if (pk == null) pk = posOf(st, ref);
      if (pk != null) { s.count = 1; bookBurst(st, buf, null, s, pk.x, pk.y, pk.z, null, bookBase(s.code % 1000)); }
    }
    forget(st, tw);
    return;
  }
  if (s != null && s.code >= 6000 && s.code < 7000) {''')
rep('''    if (c < 1000 || (c >= 3000 && c < 6000) || c >= 7000) return;          // 0.1.3: + the blast arrow (6000)''',
    '''    if (c < 1000 || (c >= 3000 && c < 6000) || c >= 8000) return;          // 0.1.3: + the blast arrow (6000); 0.1.6: + the Page Burst orbs (7000)
    if (c < 3000 && !@PKG@.ArmoryCfg.PART_TRAV) return;          // fix2: part.trav gates only the wand codes; the blast / Page Burst have their own switch''')
# fix2 (critic: part.trav off + part.book on = the direct target took the hit AND the miss burst): the Page Burst hit path is gated by
# part.book (inside bookBurst), not part.trav - the early part.trav return moves below the code test, wand codes only
rep('''    if (d.isCancelled() || !@PKG@.ArmoryCfg.PART_TRAV) return;''', '''    if (d.isCancelled()) return;''')
rep('''    if (!(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (@PKG@.ArmoryTrav.mine(d)) return;          // our own burst / trail hit: never a burst of its own''', '''    if (!(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (@PKG@.ArmoryCfg.K_NOCOMBAT && chunk != null) @PKG@.Kunai.fight(buf, chunk.getReferenceTo(idx), d);          // 0.1.6: kunai.noCombat
    if (@PKG@.ArmoryTrav.mine(d)) return;          // our own burst / trail hit: never a burst of its own''')

# ================================================================================================ ArmoryTuneSys: book.k + kunai.dpsShare
rep('''    String pid = pidOf(buf, ((@DPRJ@) src).getProjectile());
    if (pid == null) return;''', '''    String pid = pidOf(buf, ((@DPRJ@) src).getProjectile());
    if (pid == null) {          // 0.1.6: a kunai (a ProjectileConfig shot: no ProjectileComponent) - x kunai.dpsShare / 0.8
      float kf = @PKG@.Kunai.tuneOf(buf, ((@DPRJ@) src).getProjectile());
      if (kf != 1.0f) d.setAmount(d.getAmount() * kf);
      return;
    }''')
rep('''    float f = @PKG@.ArmoryDefs.tuneFactor2(pid, true, @PKG@.ArmoryCfg.TUNE_W, @PKG@.ArmoryCfg.TUNE_S, @PKG@.ArmoryCfg.QUICK_DAMAGE, @PKG@.ArmoryCfg.STAFF_BONUS);''',
    '''    float f = @PKG@.ArmoryDefs.tuneFactor2(pid, true, @PKG@.ArmoryCfg.TUNE_W, @PKG@.ArmoryCfg.TUNE_S, @PKG@.ArmoryCfg.QUICK_DAMAGE, @PKG@.ArmoryCfg.STAFF_BONUS);
    int bk0 = @PKG@.ArmoryDefs.pidCode(pid);
    if (bk0 >= 7000 && bk0 < 8000) f = (float) (@PKG@.ArmoryCfg.BOOK_K / @PKG@.ArmoryDefs.BOOK_KDEF);          // 0.1.6: every Page Burst hit x book.k / 0.4''')

# ================================================================================================ TravTick / GrappleBoltSys / GrappleFallSys wiring
rep('''    try { @PKG@.Leap.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.3: the leap's rise / hang / shot
    catch (Throwable tl) { @PKG@.Leap.warn("tick:" + tl.getClass().getName(), "leap tick failed (" + tl + ")"); }''',
    '''    try { @PKG@.Leap.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.3: the leap's rise / hang / shot
    catch (Throwable tl) { @PKG@.Leap.warn("tick:" + tl.getClass().getName(), "leap tick failed (" + tl + ")"); }
    try { @PKG@.Levitate.tickPlayer(chunk.getReferenceTo(idx), store, cb); }      // 0.1.6: the spellbook Levitate (rise / hover / float)
    catch (Throwable tv) { @PKG@.Levitate.warn("tick:" + tv.getClass().getName(), "Levitate tick failed (" + tv + ")"); }
    try { @PKG@.Kunai.tickPlayer(chunk.getReferenceTo(idx), store, cb); }         // 0.1.6: the kunai flight / landing / return knockback
    catch (Throwable tk) { @PKG@.Kunai.warn("tick:" + tk.getClass().getName(), "kunai tick failed (" + tk + ")"); }''')
rep('''    if (m == null) return;
    if (@PKG@.Leap.ARROW.equals(m.getModelAssetId())) {''', '''    if (m == null) return;
    int kc = @PKG@.ArmoryDefs.kunaiModel(m.getModelAssetId());          // 0.1.6: one of our kunai (throw i / teleport 100 + i)
    if (kc >= 0) {
      Object ks = buf.getComponent(ref, @SPPV@.getComponentType());
      if (ks instanceof @SPPV@) @PKG@.Kunai.onShot(ref, (@SPPV@) ks, st, buf, kc);
      return;
    }
    if (@PKG@.Leap.ARROW.equals(m.getModelAssetId())) {''')
rep('''  try { @PKG@.Grapple.boltGone(ref, st, buf); }
  catch (Throwable t) { @PKG@.Grapple.warn("removed:" + t.getClass().getName(), "grapple bolt remove hook failed (" + t + ")"); }''',
    '''  try { @PKG@.Grapple.boltGone(ref, st, buf); }
  catch (Throwable t) { @PKG@.Grapple.warn("removed:" + t.getClass().getName(), "grapple bolt remove hook failed (" + t + ")"); }
  try { @PKG@.Kunai.gone(ref); }          // 0.1.6: a kunai that is gone (hit / stuck time over / removed)
  catch (Throwable tk) { @PKG@.Kunai.warn("gone:" + tk.getClass().getName(), "kunai remove hook failed (" + tk + ")"); }''')
rep('''    if (@PKG@.Grapple.fallSafe(((@PR@) po).getUuid(), System.currentTimeMillis())) {
      d.setCancelled(true);
      @PKG@.Grapple.FALLS = @PKG@.Grapple.FALLS + 1L;
    }''', '''    if (@PKG@.Grapple.fallSafe(((@PR@) po).getUuid(), System.currentTimeMillis())) {
      d.setCancelled(true);
      @PKG@.Grapple.FALLS = @PKG@.Grapple.FALLS + 1L;
    } else if (@PKG@.Levitate.fallSafe(((@PR@) po).getUuid(), System.currentTimeMillis())) {          // 0.1.6: Levitate + lev.safeAfter
      d.setCancelled(true);
      @PKG@.Levitate.SAVES = @PKG@.Levitate.SAVES + 1L;
    }''')

# ================================================================================================ LEVITATE + KUNAI (Java; before ArmoryTrav.added)
BK_JAVA = r'''# ---------------------------------------------------------------- 0.1.6 LEVITATE (Spellbook-Ladder 3; the hold of a spellbook)
for f in ("public java.util.UUID u;", "public @REF@ ref;", "public @ST@ st;", "public int idx;", "public long t0;", "public int phase;",
          "public double y0;", "public double top;", "public double holdY;", "public long hoverMs;", "public long hoverUntil;", "public long riseUntil;",
          "public long safeUntil;", "public double drift;", "public int ticks;", "public int riseTicks;", "public int hoverTicks;", "public int floatTicks;",
          "public int stall;", "public double lastY;", "public String endWhy;"):
    F(lvst, f)
C(lvst, r"""
public LevState(java.util.UUID u, @REF@ ref, @ST@ st, int idx, long t0) {
  this.u = u;
  this.ref = ref;
  this.st = st;
  this.idx = idx;
  this.t0 = t0;
  this.phase = 1;
  this.ticks = 0;
  this.riseTicks = 0;
  this.hoverTicks = 0;
  this.floatTicks = 0;
  this.stall = 0;
  this.safeUntil = 0L;
  this.endWhy = "";
}""")
for f in ("public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap SAFE = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile long LEVS = 0L;", "public static volatile long REFUSED = 0L;", "public static volatile long HOVERS = 0L;",
          "public static volatile long ENDS = 0L;", "public static volatile long SAVES = 0L;", "public static volatile long CROUCHES = 0L;",
          "public static volatile String LAST_WHY = \"\";", "public static volatile int SWEEP_N = 0;",
          "public static final double MIN_ROOM = %r;" % LEV_MIN_ROOM, "public static final double WALK_DEF = %r;" % LEV_WALK_DEF,
          "public static final String SND_LEV = %s;" % jstr(SND_BOOK_CHARGE)):
    F(levc, f)
M(levc, r"""public static void warn(String key, String msg) { @PKG@.ArmoryLog.warnOnce("lev:" + key, msg); }""")
# the world's walk speed (MovementConfig BaseSpeed x ForwardRunSpeedMultiplier - VERIFIED 5.5 x 1.0 in Default.json); unreadable = 5.5
M(levc, r"""
public static double walk(@WLD@ w) {
  try {
    int mi = w.getGameplayConfig().getPlayerConfig().getMovementConfigIndex();
    Object o = @MCF@.getAssetMap().getAsset(mi);
    if (o instanceof @MCF@) {
      double b = (double) ((@MCF@) o).getBaseSpeed();
      double f = (double) ((@MCF@) o).getForwardRunSpeedMultiplier();
      if (b > 0.0 && f > 0.0) return b * f;
    }
  } catch (Throwable t) { }
  return WALK_DEF;
}""")
M(levc, r"""
public static boolean crouching(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @MSC@.getComponentType());
    if (!(o instanceof @MSC@)) return false;
    @MST@ m = ((@MSC@) o).getMovementStates();
    return m != null && m.crouching;
  } catch (Throwable t) { return false; }
}""")
M(levc, r"""
public static double[] clientVel(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @VEL@.getComponentType());
    if (o instanceof @VEL@) {
      @VEC@ cv = ((@VEL@) o).getClientVelocity();
      if (cv != null) return new double[] { cv.x, cv.y, cv.z };
    }
  } catch (Throwable t) { }
  return null;
}""")
M(levc, r"""
public static boolean refuse(@CAC@ acc, @REF@ r, String why, String tell) {
  REFUSED = REFUSED + 1L;
  LAST_WHY = why;
  if (tell != null) {
    try {
      Object po = acc.getComponent(r, @PR@.getComponentType());
      if (po instanceof @PR@) @PKG@.ArmoryTrav.tell((@PR@) po, tell);
    } catch (Throwable t) { }
  }
  return false;
}""")
# the hold's marker SPAWN (ArmoryTrav.added): the marker goes; the checks; the cost; the rise starts (a Set up this tick)
M(levc, r"""
public static boolean begin(@REF@ marker, @LPC@ pc, int c, @ST@ st, @CB@ buf) {
  try { buf.removeEntity(marker, @REMR@.REMOVE); } catch (Throwable t0) { }
  java.util.UUID u = pc.getCreatorUuid();
  @REF@ r = @PKG@.Leap.refOf(buf, u);
  int i = c % 1000;
  if (r == null || i < 0 || i >= @PKG@.ArmoryDefs.B_IDS.length) return false;
  if (!@PKG@.ArmoryCfg.PART_BOOK) return refuse(buf, r, "spellbooks off", null);
  if (@PKG@.ArmoryTrav.dead(buf, r) || @PKG@.Leap.mounted(buf, r)) return refuse(buf, r, "dead or mounted", null);
  String item = @PKG@.Leap.hand(buf, r, u);
  if (!@PKG@.ArmoryTrav.allowed(u, @PKG@.ArmoryDefs.B_IDS[i]) || !@PKG@.ArmoryTrav.allowed(u, item)) return refuse(buf, r, "class lock", null);
  @WLD@ w = @PKG@.ArmoryTrav.worldOf(buf);
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, r);
  if (w == null || p == null) return refuse(buf, r, "no world / position", null);
  double cvy = @PKG@.Leap.clientVy(buf, r);
  if (!Double.isNaN(cvy) && cvy < 0.0 - @PKG@.ArmoryTrav.maxFall(w)) return refuse(buf, r, "falling - a damaging fall is never erased", "You are falling too fast to levitate.");
  double room = @PKG@.TravMath.scan(@PKG@.ArmoryTrav.grid(w), p.x, p.y, p.z, 0.0, 1.0, 0.0, @PKG@.ArmoryCfg.LEV_H[i], 0);
  if (room < MIN_ROOM) return refuse(buf, r, "a ceiling within 2 blocks - nothing spent", "No room to levitate here - nothing spent.");
  double mana = @PKG@.ArmoryCfg.LEV_M[i];
  double stam = @PKG@.ArmoryCfg.LEV_ST[i];
  if (@PKG@.ArmoryCfg.STAMINA_CAP > 0 && stam > (double) @PKG@.ArmoryCfg.STAMINA_CAP) stam = (double) @PKG@.ArmoryCfg.STAMINA_CAP;
  if (mana > 2.0 * stam) mana = 2.0 * stam;          // fix2: Mana = 2 x the Stamina PAID (Skyy's 2:1 magical rule; spec 3 "Mana = 2 x Stamina")
  if (@PKG@.Leap.take(buf, r, stam, mana) == 0)
    return refuse(buf, r, "too little Mana or Stamina", "Not enough Mana or Stamina to levitate - " + @PKG@.TravMath.fmt(mana) + " Mana + " + @PKG@.TravMath.fmt(stam) + " Stamina needed.");
  long now = System.currentTimeMillis();
  @PKG@.LevState s = new @PKG@.LevState(u, r, st, i, now);
  s.y0 = p.y;
  s.top = p.y + room;
  s.holdY = s.top;
  s.lastY = p.y;
  s.hoverMs = Math.round(@PKG@.ArmoryCfg.LEV_S[i] * 1000.0);
  s.drift = @PKG@.ArmoryCfg.LEV_D[i];
  double rs = @PKG@.ArmoryCfg.LEV_RISE > 1.0 ? @PKG@.ArmoryCfg.LEV_RISE : 1.0;
  s.riseUntil = now + Math.round(room / rs * 1000.0) + 750L;
  STATES.put(u, s);
  SAFE.remove(u);
  @PKG@.Leap.vel(buf, r, 0.0, @PKG@.ArmoryCfg.LEV_RISE, 0.0, false);
  @PKG@.ArmoryTrav.sound(SND_LEV, p.x, p.y, p.z, buf);
  LEVS = LEVS + 1L;
  LAST_WHY = "levitate " + @PKG@.TravMath.fmt(room) + " blocks";
  return true;
}""")
M(levc, r"""
public static void endHover(@PKG@.LevState s, long now, String why) {
  s.phase = 3;
  s.endWhy = why;
  s.safeUntil = now + Math.round(@PKG@.ArmoryCfg.LEV_SAFE * 1000.0);
  SAFE.put(s.u, Long.valueOf(s.safeUntil));
}""")
# records of players who are gone (disconnect) are dropped; the safe-time map is pruned
M(levc, r"""
public static void sweep(long now) {
  java.util.Iterator it = STATES.values().iterator();
  while (it.hasNext()) {
    @PKG@.LevState s = (@PKG@.LevState) it.next();
    boolean gone = false;
    try { gone = s.ref == null || !s.ref.isValid() || now - s.t0 > 120000L; } catch (Throwable t) { gone = true; }
    if (gone) it.remove();
  }
  java.util.Iterator is = SAFE.values().iterator();
  while (is.hasNext()) { Object o = is.next(); if (!(o instanceof Long) || now > ((Long) o).longValue()) is.remove(); }
}""")
# TravTick -> once per player per world tick: RISE (a Set up every tick to the height / a ceiling / the time) -> HOVER (a Set every tick: the
# look's horizontal direction x drift x walk, holding the height) -> crouch / the time -> FLOAT (no fall damage until the safe time ends,
# falls capped at lev.floatFall) -> the end
M(levc, r"""
public static void tickPlayer(@REF@ r, @ST@ st, @CB@ buf) {
  if (r == null || STATES.isEmpty()) return;
  SWEEP_N = SWEEP_N + 1;
  if (SWEEP_N >= 300) { SWEEP_N = 0; try { sweep(System.currentTimeMillis()); } catch (Throwable ts) { } }
  java.util.UUID u = @PKG@.Leap.uuidOf(buf, r);
  if (u == null) return;
  @PKG@.LevState s = (@PKG@.LevState) STATES.get(u);
  if (s == null) return;
  long now = System.currentTimeMillis();
  if (s.st != st || s.ref == null || !s.ref.equals(r)) { STATES.remove(u, s); LAST_WHY = "left the world / a new body"; return; }
  if (@PKG@.ArmoryTrav.dead(buf, r)) { STATES.remove(u, s); SAFE.remove(u); LAST_WHY = "died"; return; }
  s.ticks = s.ticks + 1;
  if (@PKG@.Leap.mounted(buf, r)) { if (s.phase < 3) endHover(s, now, "mounted"); STATES.remove(u, s); LAST_WHY = "mounted"; return; }
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, r);
  if (s.phase == 1) {
    boolean top = false;
    if (p != null) {
      if (p.y >= s.top - 0.25) top = true;
      if (p.y <= s.lastY + 0.01) s.stall = s.stall + 1;
      else s.stall = 0;
      s.lastY = p.y;
    }
    if (now >= s.riseUntil || s.stall >= 6) top = true;
    if (!top) {
      if (@PKG@.Leap.vel(buf, r, 0.0, @PKG@.ArmoryCfg.LEV_RISE, 0.0, false)) s.riseTicks = s.riseTicks + 1;
      return;
    }
    s.phase = 2;
    s.holdY = p == null ? s.top : p.y;
    s.hoverUntil = now + s.hoverMs;
    HOVERS = HOVERS + 1L;
  }
  if (s.phase == 2) {
    if (@PKG@.ArmoryCfg.LEV_CROUCH && crouching(buf, r)) { endHover(s, now, "crouch"); CROUCHES = CROUCHES + 1L; }
    else if (now >= s.hoverUntil) endHover(s, now, "the hover ended");
    else {
      double[] a = @PKG@.Leap.aim(buf, r, u, null);
      double dx = 0.0;
      double dz = 0.0;
      if (a != null) {
        double l = Math.sqrt(a[3] * a[3] + a[5] * a[5]);
        if (l > 1.0E-3) { dx = a[3] / l; dz = a[5] / l; }
      }
      double spd = s.drift * walk(@PKG@.ArmoryTrav.worldOf(buf));
      double vy = p == null ? 0.0 : @PKG@.TravMath.holdVy(s.holdY, p.y);
      if (@PKG@.Leap.vel(buf, r, dx * spd, vy, dz * spd, false)) s.hoverTicks = s.hoverTicks + 1;
      return;
    }
  }
  if (s.phase == 3) {
    if (now >= s.safeUntil) { STATES.remove(u, s); ENDS = ENDS + 1L; LAST_WHY = "landed (" + s.endWhy + ")"; return; }
    double[] cv = clientVel(buf, r);
    if (@PKG@.ArmoryCfg.LEV_FLOAT > 0.0 && cv != null && cv[1] < 0.0 - @PKG@.ArmoryCfg.LEV_FLOAT) {
      if (@PKG@.Leap.vel(buf, r, cv[0], 0.0 - @PKG@.ArmoryCfg.LEV_FLOAT, cv[2], false)) s.floatTicks = s.floatTicks + 1;
    }
  }
}""")
# GrappleFallSys: no FALL damage while rising / hovering, and until the hover's end + lev.safeAfter
M(levc, r"""
public static boolean fallSafe(java.util.UUID u, long now) {
  if (u == null) return false;
  @PKG@.LevState s = (@PKG@.LevState) STATES.get(u);
  if (s != null && s.phase < 3 && s.ref != null && s.ref.isValid()) return true;
  Object g = SAFE.get(u);
  return g instanceof Long && now <= ((Long) g).longValue();
}""")

# ---------------------------------------------------------------- 0.1.6 KUNAI (Kunai-Ladder 3-6: throw, teleport with the safety scan, return)
for f in ("public java.util.UUID u;", "public @REF@ ref;", "public @ST@ st;", "public int idx;", "public @REF@ proj;", "public String item;", "public long t0;",
          "public double sx;", "public double sy;", "public double sz;", "public double ex;", "public double ey;", "public double ez;",
          "public double lx;", "public double ly;", "public double lz;", "public boolean hit;", "public double hx;", "public double hy;", "public double hz;",
          "public @REF@ hitEnt;", "public boolean gone;", "public double stam;", "public double mana;"):
    F(kst, f)
C(kst, r"""
public KunaiState(java.util.UUID u, @REF@ ref, @ST@ st, int idx, @REF@ proj, String item, long t0) {
  this.u = u;
  this.ref = ref;
  this.st = st;
  this.idx = idx;
  this.proj = proj;
  this.item = item;
  this.t0 = t0;
  this.hit = false;
  this.gone = false;
  this.hitEnt = null;
}""")
kimp.addInterface(pool.get(T["IMPC"]))
F(kimp, "public @IMPC@ inner;")
F(kimp, "public java.util.UUID u;")
C(kimp, "public KunaiImpact(@IMPC@ inner, java.util.UUID u) { this.inner = inner; this.u = u; }")
kjob.addInterface(pool.get("java.lang.Runnable"))
for f in ("public int kind;", "public java.util.UUID u;", "public @ST@ st;", "public double[] pt;", "public int idx;", "public double stam;", "public double mana;"):
    F(kjob, f)
C(kjob, r"""
public KunaiJob(int kind, java.util.UUID u, @ST@ st, double[] pt, int idx, double stam, double mana) {
  this.kind = kind;
  this.u = u;
  this.st = st;
  this.pt = pt;
  this.idx = idx;
  this.stam = stam;
  this.mana = mana;
}""")
for f in ("public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();",   # u -> KunaiState
          "public static final java.util.concurrent.ConcurrentHashMap RET = new java.util.concurrent.ConcurrentHashMap();",      # u -> {x, y, z, until, idx}
          "public static final java.util.concurrent.ConcurrentHashMap RETST = new java.util.concurrent.ConcurrentHashMap();",    # u -> the Store
          "public static final java.util.concurrent.ConcurrentHashMap FLY = new java.util.concurrent.ConcurrentHashMap();",      # tap kunai -> {sx, sy, sz, range, until}
          "public static final java.util.concurrent.ConcurrentHashMap FLYU = new java.util.concurrent.ConcurrentHashMap();",     # tap kunai -> thrower
          "public static final java.util.concurrent.ConcurrentHashMap LASTPORT = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap PERMIN = new java.util.concurrent.ConcurrentHashMap();",   # u -> ArrayList of Long
          "public static final java.util.concurrent.ConcurrentHashMap FIGHT = new java.util.concurrent.ConcurrentHashMap();",    # u -> Long (noCombat)
          "public static final java.util.concurrent.ConcurrentHashMap KNOCK = new java.util.concurrent.ConcurrentHashMap();",    # u -> {x, y, z, r, f, dmg}
          "public static volatile long THROWS = 0L;", "public static volatile long PORTS = 0L;", "public static volatile long REFUNDS = 0L;",
          "public static volatile long RETURNS = 0L;", "public static volatile long KNOCKS = 0L;", "public static volatile long RANGED = 0L;",
          "public static volatile long CANCELS = 0L;", "public static volatile long REFUSED = 0L;", "public static volatile long NORMALS = 0L;",
          "public static volatile String LAST_WHY = \"\";", "public static volatile int SWEEP_N = 0;",
          "public static final long FIGHT_MS = %dL;" % FIGHT_MS, "public static final double KNOCK_BASE = %r;" % KNOCK_BASE,
          "public static final double KNOCK_UP = %r;" % KNOCK_UP, "public static final double RET_SEARCH = 3.0;",
          "public static final String FX_PORTAL = %s;" % jstr(FX_PORTAL), "public static final String SND_PORT = %s;" % jstr(SND_BLINK),
          "public static final String SND_NO = %s;" % jstr(SND_GNO)):
    F(kun, f)
M(kun, r"""public static void warn(String key, String msg) { @PKG@.ArmoryLog.warnOnce("kunai:" + key, msg); }""")
M(kun, r"""
public static @PR@ prOf(@CAC@ acc, @REF@ r) {
  try { Object o = acc.getComponent(r, @PR@.getComponentType()); return o instanceof @PR@ ? (@PR@) o : null; } catch (Throwable t) { return null; }
}""")
M(kun, r"""
public static void tellRef(@CAC@ acc, @REF@ r, String text) {
  @PR@ p = prOf(acc, r);
  if (p != null) @PKG@.ArmoryTrav.tell(p, text);
}""")
M(kun, r"""
public static double thick(@CAC@ acc, @REF@ r) {
  try {
    @BBX@ b = (@BBX@) acc.getComponent(r, @BBX@.getComponentType());
    if (b == null || b.getBoundingBox() == null) return 1.0;
    double w = Math.max(b.getBoundingBox().width(), b.getBoundingBox().depth());
    return w > 0.0 && w < 16.0 ? w : 1.0;
  } catch (Throwable t) { return 1.0; }
}""")
M(kun, r"""
public static void refund(@CAC@ acc, @REF@ r, double stam, double mana) {
  if (r == null || !r.isValid()) return;
  @PKG@.ArmoryTrav.addStat(acc, r, @DST@.getStamina(), stam);
  @PKG@.ArmoryTrav.addStat(acc, r, @DST@.getMana(), mana);
  REFUNDS = REFUNDS + 1L;
}""")
# the kunai hit's tune (ArmoryTuneSys): one of our kunai models -> x kunai.dpsShare / 0.8
M(kun, r"""
public static float tuneOf(@CB@ buf, @REF@ proj) {
  try {
    if (proj == null || !proj.isValid()) return 1.0f;
    Object mc = buf.getComponent(proj, @MODC@.getComponentType());
    if (!(mc instanceof @MODC@) || ((@MODC@) mc).getModel() == null) return 1.0f;
    if (@PKG@.ArmoryDefs.kunaiModel(((@MODC@) mc).getModel().getModelAssetId()) < 0) return 1.0f;
    return (float) (@PKG@.ArmoryCfg.K_SHARE / @PKG@.ArmoryDefs.K_SHARE_DEF);
  } catch (Throwable t) { return 1.0f; }
}""")
# kunai.noCombat (ArmoryHitSys, Inspect group): the time of a hit a player dealt or took
M(kun, r"""
public static void fight(@CB@ buf, @REF@ target, @DMG@ d) {
  try {
    if (d == null || d.isCancelled()) return;
    long now = System.currentTimeMillis();
    @PR@ tp = target == null ? null : prOf(buf, target);
    if (tp != null && tp.getUuid() != null) FIGHT.put(tp.getUuid(), Long.valueOf(now));
    Object src = d.getSource();
    if (src instanceof @DENT@) {
      @REF@ a = ((@DENT@) src).getRef();
      @PR@ ap = a == null ? null : prOf(buf, a);
      if (ap != null && ap.getUuid() != null) FIGHT.put(ap.getUuid(), Long.valueOf(now));
    }
  } catch (Throwable t) { }
}""")
M(kun, r"""
public static boolean fighting(java.util.UUID u, long now) {
  Object o = FIGHT.get(u);
  return o instanceof Long && now - ((Long) o).longValue() < FIGHT_MS;
}""")
# the spam net: true = one more teleport this minute is fine (recorded by mark)
M(kun, r"""
public static boolean underCap(java.util.UUID u, long now) {
  if (@PKG@.ArmoryCfg.K_MAXMIN <= 0) return true;
  Object o = PERMIN.get(u);
  if (!(o instanceof java.util.ArrayList)) return true;
  java.util.ArrayList l = (java.util.ArrayList) o;
  for (int i = l.size() - 1; i >= 0; i--) if (now - ((Long) l.get(i)).longValue() >= 60000L) l.remove(i);
  return l.size() < @PKG@.ArmoryCfg.K_MAXMIN;
}""")
M(kun, r"""
public static void mark(java.util.UUID u, long now) {
  Object o = PERMIN.get(u);
  java.util.ArrayList l = o instanceof java.util.ArrayList ? (java.util.ArrayList) o : new java.util.ArrayList();
  l.add(Long.valueOf(now));
  while (l.size() > 240) l.remove(0);
  PERMIN.put(u, l);
  LASTPORT.put(u, Long.valueOf(now));
}""")
# a tap kunai (or a hold that may not teleport now): it flies kunai.throwRange at most
M(kun, r"""
public static void fly(@REF@ proj, @CB@ buf, java.util.UUID u, long now) {
  @VEC@ pp = @PKG@.ArmoryTrav.posOf(buf, proj);
  if (pp == null) return;
  FLY.put(proj, new double[] { pp.x, pp.y, pp.z, (double) @PKG@.ArmoryCfg.K_THROW_RANGE, (double) (now + Math.round(@PKG@.ArmoryCfg.K_TTL * 1000.0) + 500L) });
  FLYU.put(proj, u);
}""")
M(kun, r"""
public static void cancel(@PKG@.KunaiState s, @CB@ buf, @ST@ st, String why) {
  if (s == null) return;
  STATES.remove(s.u, s);
  if (s.st == st) {
    refund(buf, s.ref, s.stam, s.mana);
    try { if (s.proj != null && s.proj.isValid()) buf.removeEntity(s.proj, @REMR@.REMOVE); } catch (Throwable t) { }
  }
  CANCELS = CANCELS + 1L;
  LAST_WHY = "cancelled - " + why;
}""")
# GrappleBoltSys.onEntityAdded (SPAWN of one of our kunai): a tap = a throw (range watch); a hold = the teleport kunai - class lock (no throw),
# cooldown / spam net / combat row (a normal throw + a line), the cost (too little = no throw, spec 4), the impact watch, the record
M(kun, r"""
public static void onShot(@REF@ proj, @SPPV@ sp, @ST@ st, @CB@ buf, int code) {
  if (proj == null || sp == null) return;
  int i = code % 100;
  boolean port = code >= 100;
  java.util.UUID u = sp.getCreatorUuid();
  @REF@ r = @PKG@.Leap.refOf(buf, u);
  if (r == null || i < 0 || i >= @PKG@.ArmoryDefs.K_IDS.length) return;
  long now = System.currentTimeMillis();
  THROWS = THROWS + 1L;
  if (!port || !@PKG@.ArmoryCfg.PART_KUNAI) { fly(proj, buf, u, now); LAST_WHY = port ? "kunai teleport off - a normal throw" : "throw"; return; }
  String item = @PKG@.Leap.hand(buf, r, u);
  if (!@PKG@.ArmoryTrav.allowed(u, @PKG@.ArmoryDefs.K_IDS[i]) || !@PKG@.ArmoryTrav.allowed(u, item)) {
    try { buf.removeEntity(proj, @REMR@.REMOVE); } catch (Throwable t0) { }
    REFUSED = REFUSED + 1L;
    LAST_WHY = "class lock";
    return;
  }
  if (@PKG@.ArmoryTrav.dead(buf, r) || @PKG@.Leap.mounted(buf, r)) { fly(proj, buf, u, now); LAST_WHY = "dead or mounted - a normal throw"; return; }
  Object lp = LASTPORT.get(u);
  String why = null;
  if (lp instanceof Long && now - ((Long) lp).longValue() < Math.round(@PKG@.ArmoryCfg.K_CD[i] * 1000.0)) why = "cooldown";
  else if (!underCap(u, now)) why = "the per-minute cap";
  else if (@PKG@.ArmoryCfg.K_NOCOMBAT && fighting(u, now)) why = "in combat";
  if (why != null) {
    fly(proj, buf, u, now);
    NORMALS = NORMALS + 1L;
    LAST_WHY = why + " - a normal throw";
    tellRef(buf, r, "No teleport now (" + why + ") - a normal throw.");
    return;
  }
  double stam = @PKG@.ArmoryCfg.K_STAM[i];
  double mana = @PKG@.ArmoryCfg.K_MANA[i];
  if (@PKG@.ArmoryCfg.STAMINA_CAP > 0 && stam > (double) @PKG@.ArmoryCfg.STAMINA_CAP) stam = (double) @PKG@.ArmoryCfg.STAMINA_CAP;
  if (@PKG@.Leap.take(buf, r, stam, mana) == 0) {
    try { buf.removeEntity(proj, @REMR@.REMOVE); } catch (Throwable t1) { }
    REFUSED = REFUSED + 1L;
    LAST_WHY = "too little Stamina or Mana - no throw";
    tellRef(buf, r, "Not enough Stamina or Mana to teleport - " + @PKG@.TravMath.fmt(stam) + " Stamina + " + @PKG@.TravMath.fmt(mana) + " Mana needed.");
    return;
  }
  @PKG@.KunaiState old = (@PKG@.KunaiState) STATES.get(u);
  if (old != null) cancel(old, buf, st, "a newer teleport kunai");
  try { sp.setImpactConsumer(new @PKG@.KunaiImpact(sp.getImpactConsumer(), u)); }
  catch (Throwable t2) { warn("wrap", "a kunai's impact could not be watched (" + t2 + ") - it lands you where it was last seen"); }
  @PKG@.KunaiState s = new @PKG@.KunaiState(u, r, st, i, proj, item, now);
  @VEC@ fp = @PKG@.ArmoryTrav.posOf(buf, r);
  @VEC@ pp = @PKG@.ArmoryTrav.posOf(buf, proj);
  if (fp != null) { s.sx = fp.x; s.sy = fp.y; s.sz = fp.z; }
  if (pp != null) { s.ex = pp.x; s.ey = pp.y; s.ez = pp.z; s.lx = pp.x; s.ly = pp.y; s.lz = pp.z; }
  else if (fp != null) { s.ex = fp.x; s.ey = fp.y + 1.6; s.ez = fp.z; s.lx = s.ex; s.ly = s.ey; s.lz = s.ez; }
  s.stam = stam;
  s.mana = mana;
  STATES.put(u, s);
  LAST_WHY = "teleport kunai thrown";
}""")
# KunaiImpact (inside StandardPhysicsTickSystem): the impact point + the entity hit (null = a block); the engine's own consumer runs after
M(kun, r"""
public static void impact(java.util.UUID u, @REF@ proj, @VEC@ pos, @REF@ hit, @CB@ buf) {
  if (u == null || proj == null) return;
  @PKG@.KunaiState s = (@PKG@.KunaiState) STATES.get(u);
  if (s == null || s.hit || s.proj == null || !s.proj.equals(proj)) return;
  if (hit != null && hit.equals(s.ref)) return;
  s.hit = true;
  if (pos != null) { s.hx = pos.x; s.hy = pos.y; s.hz = pos.z; }
  else { s.hx = s.lx; s.hy = s.ly; s.hz = s.lz; }
  s.hitEnt = hit;
}""")
M(kun, r"""
public static void gone(@REF@ proj) {
  if (proj == null) return;
  FLY.remove(proj);
  FLYU.remove(proj);
  if (STATES.isEmpty()) return;
  java.util.Iterator it = STATES.values().iterator();
  while (it.hasNext()) {
    @PKG@.KunaiState s = (@PKG@.KunaiState) it.next();
    if (s.proj != null && s.proj.equals(proj)) s.gone = true;
  }
}""")
# the return knockback (the tick after the return): enemies within the radius are pushed outward (mobs with the dagger dash config; players only
# where PvP is on + trav.players, never party), ret.damage % of a kunai hit
M(kun, r"""
public static int knock(@REF@ r, @ST@ st, @CB@ buf, java.util.UUID u, double[] kn) {
  if (kn == null || !(kn[3] > 0.0) || !(kn[4] > 0.0)) return 0;
  boolean pvp = @PKG@.ArmoryTrav.pvp(@PKG@.ArmoryTrav.worldOf(buf));
  java.util.List l = @PKG@.ArmoryTrav.near(buf, kn[0], kn[1], kn[2], kn[3]);
  int n = 0;
  for (int k = 0; k < l.size(); k++) {
    @REF@ t = (@REF@) l.get(k);
    if (t == null || t.equals(r)) continue;
    if (@PKG@.ArmoryTrav.kind(buf, t, r, u, pvp) != 0) continue;
    @VEC@ tp = @PKG@.ArmoryTrav.posOf(buf, t);
    if (tp == null) continue;
    double dx = tp.x - kn[0];
    double dz = tp.z - kn[2];
    double l2 = Math.sqrt(dx * dx + dz * dz);
    if (l2 < 0.1) { dx = 1.0; dz = 0.0; l2 = 1.0; }
    boolean mob = prOf(buf, t) == null;
    double f = KNOCK_BASE * kn[4];
    if (@PKG@.Leap.vel(buf, t, dx / l2 * f, KNOCK_UP * kn[4], dz / l2 * f, mob)) { n++; KNOCKS = KNOCKS + 1L; }
    if (kn[5] > 0.0) @PKG@.ArmoryTrav.hit(buf, t, r, null, kn[5]);
  }
  return n;
}""")
# a tap kunai past kunai.throwRange (or its time) is removed; a stale record goes
M(kun, r"""
public static void flyTick(java.util.UUID u, @ST@ st, @CB@ buf, long now) {
  java.util.Iterator it = FLY.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    @REF@ pr = (@REF@) e.getKey();
    if (!u.equals(FLYU.get(pr))) continue;
    if (pr == null || !pr.isValid()) { it.remove(); FLYU.remove(pr); continue; }
    if (pr.getStore() != st) continue;
    double[] d = (double[]) e.getValue();
    @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, pr);
    boolean out = (double) now > d[4];
    if (p != null) {
      double dx = p.x - d[0];
      double dy = p.y - d[1];
      double dz = p.z - d[2];
      if (dx * dx + dy * dy + dz * dz > d[3] * d[3]) out = true;
    }
    if (out) {
      it.remove();
      FLYU.remove(pr);
      try { buf.removeEntity(pr, @REMR@.REMOVE); RANGED = RANGED + 1L; } catch (Throwable t) { }
    }
  }
}""")
M(kun, r"""
public static void sweep(long now) {
  java.util.Iterator it = STATES.values().iterator();
  while (it.hasNext()) {
    @PKG@.KunaiState s = (@PKG@.KunaiState) it.next();
    boolean g = false;
    try { g = s.ref == null || !s.ref.isValid() || now - s.t0 > 60000L; } catch (Throwable t) { g = true; }
    if (g) it.remove();
  }
  java.util.Iterator ir = RET.entrySet().iterator();
  while (ir.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) ir.next();
    double[] d = (double[]) e.getValue();
    if (d == null || (double) now > d[3]) { ir.remove(); RETST.remove(e.getKey()); }
  }
  java.util.Iterator ifl = FLY.keySet().iterator();
  while (ifl.hasNext()) { Object k = ifl.next(); try { if (!((@REF@) k).isValid()) { ifl.remove(); FLYU.remove(k); } } catch (Throwable t2) { ifl.remove(); } }
  java.util.Iterator ifg = FIGHT.values().iterator();
  while (ifg.hasNext()) { Object o = ifg.next(); if (!(o instanceof Long) || now - ((Long) o).longValue() > FIGHT_MS) ifg.remove(); }
}""")
# TravTick -> once per player per world tick: the return knockback, the tap kunai ranges, the teleport kunai: hand / death / world checks, where it
# is, then LAND (hit / gone / out of range = the range point on the line / its time): the PvP rule on a player hit, then the teleport job
M(kun, r"""
public static void tickPlayer(@REF@ r, @ST@ st, @CB@ buf) {
  if (r == null) return;
  if (STATES.isEmpty() && FLY.isEmpty() && KNOCK.isEmpty()) return;
  long now = System.currentTimeMillis();
  SWEEP_N = SWEEP_N + 1;
  if (SWEEP_N >= 300) { SWEEP_N = 0; try { sweep(now); } catch (Throwable ts) { } }
  java.util.UUID u = @PKG@.Leap.uuidOf(buf, r);
  if (u == null) return;
  Object kn = KNOCK.remove(u);
  if (kn instanceof double[]) knock(r, st, buf, u, (double[]) kn);
  if (!FLY.isEmpty()) flyTick(u, st, buf, now);
  @PKG@.KunaiState s = (@PKG@.KunaiState) STATES.get(u);
  if (s == null) return;
  if (s.st != st || s.ref == null || !s.ref.equals(r)) { STATES.remove(u, s); CANCELS = CANCELS + 1L; LAST_WHY = "cancelled - left the world"; return; }
  if (@PKG@.ArmoryTrav.dead(buf, r)) { STATES.remove(u, s); CANCELS = CANCELS + 1L; LAST_WHY = "cancelled - died"; return; }
  String hand = @PKG@.Leap.hand(buf, r, u);
  if (hand == null ? s.item != null : !hand.equals(s.item)) { cancel(s, buf, st, "the kunai left your hand"); return; }
  @VEC@ pp = (s.proj != null && s.proj.isValid()) ? @PKG@.ArmoryTrav.posOf(buf, s.proj) : null;
  if (pp != null) { s.lx = pp.x; s.ly = pp.y; s.lz = pp.z; }
  int i = s.idx;
  double tx = s.lx;
  double ty = s.ly;
  double tz = s.lz;
  @REF@ ent = null;
  String why = null;
  double rg = @PKG@.ArmoryCfg.K_RANGE[i];
  double ox = s.lx - s.ex;
  double oy = s.ly - s.ey;
  double oz = s.lz - s.ez;
  double od = Math.sqrt(ox * ox + oy * oy + oz * oz);
  if (s.hit) { tx = s.hx; ty = s.hy; tz = s.hz; ent = s.hitEnt; why = ent == null ? "hit a block" : "hit"; }
  else if (s.gone || s.proj == null || !s.proj.isValid()) why = "the kunai stopped";
  else if (od > rg) {
    tx = s.ex + ox / od * rg;
    ty = s.ey + oy / od * rg;
    tz = s.ez + oz / od * rg;
    why = "out of range";
  } else if (now - s.t0 > Math.round(@PKG@.ArmoryCfg.K_TTL * 1000.0)) why = "flight time";
  if (why == null) return;
  STATES.remove(u, s);
  try { if (!s.hit && s.proj != null && s.proj.isValid()) buf.removeEntity(s.proj, @REMR@.REMOVE); } catch (Throwable tr) { }
  if (ent != null) {
    @PR@ hp = prOf(buf, ent);
    if (hp != null) {
      boolean ok = @PKG@.ArmoryTrav.ally(u, hp.getUuid()) || ("world".equals(@PKG@.ArmoryCfg.K_PVP) && @PKG@.ArmoryTrav.pvp(@PKG@.ArmoryTrav.worldOf(buf)));
      if (!ok) {
        refund(buf, r, s.stam, s.mana);
        LAST_WHY = "no teleport next to that player (PvP off) - refunded";
        tellRef(buf, r, "You cannot teleport next to that player here - nothing spent.");
        return;
      }
    }
  }
  @WLD@ w = @PKG@.ArmoryTrav.worldOf(buf);
  if (w == null) { refund(buf, r, s.stam, s.mana); LAST_WHY = "no world"; return; }
  double th = ent == null ? 0.0 : thick(buf, ent);
  w.execute(new @PKG@.KunaiJob(1, u, st, new double[] { tx, ty, tz, ent == null ? 0.0 : 1.0, th }, i, s.stam, s.mana));
  LAST_WHY = "landing - " + why;
}""")
# the bridge arena:fn:blocks (Object[]{UUID, double[] from, double[] to} -> Boolean TRUE = a locked arena is in the way); no answer = free
M(kun, r"""
public static boolean arena(java.util.UUID u, double[] from, double[] to) {
  if (!@PKG@.ArmoryCfg.K_NOARENA) return false;
  java.util.function.Function f = @PKG@.ArmoryTrav.fn("arena:fn:blocks");
  if (f == null) return false;
  try { return Boolean.TRUE.equals(f.apply(new Object[] { u, from, to })); } catch (Throwable t) { return false; }
}""")
M(kun, r"""
public static boolean port(@ST@ st, @REF@ ref, @WLD@ w, double ex, double ey, double ez) {
  try {
    @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
    if (tc == null) return false;
    @TP@ tp = @TP@.createForPlayer(w, new @VEC@(ex, ey, ez), tc.getRotation());
    try {
      @HR@ hr = (@HR@) st.getComponent(ref, @HR@.getComponentType());
      if (hr != null && hr.getRotation() != null) tp.setHeadRotation(hr.getRotation());
    } catch (Throwable t2) { }
    tp = tp.withoutVelocityReset();          // a damaging fall is never erased (the blink's keepFall rule)
    st.putComponent(ref, @TP@.getComponentType(), tp);
    return true;
  } catch (Throwable t) { warn("port", "a kunai teleport failed (" + t + ")"); return false; }
}""")
# THE TELEPORT (world thread, outside the systems - the blink's path): the safety scan from your feet, the arena bridge; no move = refunded
M(kun, r"""
public static void teleport(@PKG@.KunaiJob j) {
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(j.u); } catch (Throwable t0) { pr = null; }
  @REF@ ref = (pr == null || !pr.isValid()) ? null : pr.getReference();
  @ST@ st = (ref == null || !ref.isValid()) ? null : ref.getStore();
  if (st == null || st != j.st) { LAST_WHY = "the thrower left this world"; return; }
  if (@PKG@.ArmoryTrav.dead(st, ref)) { LAST_WHY = "died"; return; }
  @VEC@ pos = @PKG@.ArmoryTrav.posOf(st, ref);
  @WLD@ w = @PKG@.ArmoryTrav.worldOf(st);
  if (pos == null || w == null) { refund(st, ref, j.stam, j.mana); LAST_WHY = "no position"; return; }
  @PKG@.TravGrid g = @PKG@.ArmoryTrav.grid(w);
  double[] aim = @PKG@.TravMath.kunaiAim(g, pos.x, pos.y, pos.z, j.pt[0], j.pt[1], j.pt[2], j.pt[3] > 0.5, j.pt[4], @PKG@.ArmoryCfg.K_BEHIND);
  if (arena(j.u, new double[] { pos.x, pos.y, pos.z }, new double[] { j.pt[0], j.pt[1], j.pt[2] })) {
    refund(st, ref, j.stam, j.mana);
    LAST_WHY = "a locked arena - refunded";
    @PKG@.ArmoryTrav.tell(pr, "A locked arena blocks your kunai - nothing spent.");
    return;
  }
  double t = aim[3] >= 1.0 ? @PKG@.TravMath.scan(g, pos.x, pos.y, pos.z, aim[0], aim[1], aim[2], aim[3], @PKG@.ArmoryCfg.K_FLOOR) : 0.0;
  if (!(t > 0.0)) {
    refund(st, ref, j.stam, j.mana);
    LAST_WHY = "no safe spot - refunded";
    @PKG@.ArmoryTrav.tell(pr, "No safe spot to teleport to - nothing spent.");
    return;
  }
  double l = Math.sqrt(aim[0] * aim[0] + aim[1] * aim[1] + aim[2] * aim[2]);
  double ex = pos.x + aim[0] / l * t;
  double ey = pos.y + aim[1] / l * t;
  double ez = pos.z + aim[2] / l * t;
  double sx = pos.x;
  double sy = pos.y;
  double sz = pos.z;
  if (!port(st, ref, w, ex, ey, ez)) { refund(st, ref, j.stam, j.mana); return; }
  long now = System.currentTimeMillis();
  RET.put(j.u, new double[] { sx, sy, sz, (double) (now + Math.round(@PKG@.ArmoryCfg.K_WIN[j.idx] * 1000.0)), (double) j.idx });
  RETST.put(j.u, st);
  mark(j.u, now);
  PORTS = PORTS + 1L;
  LAST_WHY = "teleport " + @PKG@.TravMath.fmt(t) + " blocks";
  @PKG@.ArmoryTrav.effect(ref, FX_PORTAL, st);
  @PKG@.ArmoryTrav.sound(SND_PORT, sx, sy, sz, st);
  @PKG@.ArmoryTrav.sound(SND_PORT, ex, ey, ez, st);
}""")
# THE RETURN (world thread): within the window, back to the spot you left - or the nearest safe spot within 3 blocks, else no return (the window
# is gone: "no refund of the window"); then the knockback ring on the next tick
M(kun, r"""
public static void recall(@PKG@.KunaiJob j) {
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(j.u); } catch (Throwable t0) { pr = null; }
  @REF@ ref = (pr == null || !pr.isValid()) ? null : pr.getReference();
  @ST@ st = (ref == null || !ref.isValid()) ? null : ref.getStore();
  if (st == null || st != j.st) { LAST_WHY = "return: left this world"; return; }
  if (@PKG@.ArmoryTrav.dead(st, ref)) return;
  if (!@PKG@.ArmoryCfg.PART_KUNAI) { LAST_WHY = "return: kunai teleport off"; return; }
  double[] rt = (double[]) RET.get(j.u);
  if (rt == null || RETST.get(j.u) != st) { LAST_WHY = "return: nothing to return to"; @PKG@.ArmoryTrav.tell(pr, "Nothing to return to - teleport with a kunai first."); return; }
  long now = System.currentTimeMillis();
  if ((double) now > rt[3]) { RET.remove(j.u); RETST.remove(j.u); LAST_WHY = "return: too late"; @PKG@.ArmoryTrav.tell(pr, "Too late to return."); return; }
  int ki = (int) rt[4];
  if (!@PKG@.ArmoryTrav.allowed(j.u, @PKG@.ArmoryDefs.K_IDS[ki]) || !@PKG@.ArmoryTrav.allowed(j.u, @PKG@.ArmoryTrav.handItem(st, ref))) { LAST_WHY = "return: class lock"; return; }
  @WLD@ w = @PKG@.ArmoryTrav.worldOf(st);
  double[] sp = @PKG@.TravMath.safeNear(@PKG@.ArmoryTrav.grid(w), rt[0], rt[1], rt[2], RET_SEARCH, @PKG@.ArmoryCfg.K_FLOOR);
  RET.remove(j.u);
  RETST.remove(j.u);
  if (sp == null) { LAST_WHY = "return: the spot is blocked - no return"; @PKG@.ArmoryTrav.tell(pr, "Your return spot is blocked - no return."); return; }
  @VEC@ from = @PKG@.ArmoryTrav.posOf(st, ref);
  if (!port(st, ref, w, sp[0], sp[1], sp[2])) return;
  RETURNS = RETURNS + 1L;
  LAST_WHY = "returned";
  double hit = (double) @PKG@.ArmoryDefs.K_DMG[ki] * @PKG@.ArmoryCfg.K_SHARE / @PKG@.ArmoryDefs.K_SHARE_DEF * (double) @PKG@.ArmoryCfg.K_RDMG / 100.0;
  KNOCK.put(j.u, new double[] { sp[0], sp[1], sp[2], @PKG@.ArmoryCfg.K_RAD[ki], @PKG@.ArmoryCfg.K_FORCE, hit });
  @PKG@.ArmoryTrav.effect(ref, FX_PORTAL, st);
  if (from != null) @PKG@.ArmoryTrav.sound(SND_PORT, from.x, from.y, from.z, st);
  @PKG@.ArmoryTrav.sound(SND_PORT, sp[0], sp[1], sp[2], st);
}""")
# the return marker's SPAWN (ArmoryTrav.added): the marker goes, the return job runs on the world thread
M(kun, r"""
public static void recallMarker(@REF@ marker, @LPC@ pc, int c, @ST@ st, @CB@ buf) {
  try { buf.removeEntity(marker, @REMR@.REMOVE); } catch (Throwable t0) { }
  java.util.UUID u = pc.getCreatorUuid();
  @WLD@ w = @PKG@.ArmoryTrav.worldOf(st);
  if (u == null || w == null) return;
  w.execute(new @PKG@.KunaiJob(2, u, st, null, c % 1000, 0.0, 0.0));
}""")
M(kimp, r"""
public void onImpact(@REF@ p, @VEC@ pos, @V3I@ blk, @REF@ hit, String name, @CB@ buf) {
  try { @PKG@.Kunai.impact(this.u, p, pos, hit, buf); }
  catch (Throwable t) { @PKG@.Kunai.warn("impact", "the kunai impact record failed (" + t + ")"); }
  if (this.inner != null) this.inner.onImpact(p, pos, blk, hit, name, buf);
}""")
M(kjob, r"""
public void run() {
  try {
    if (this.kind == 1) @PKG@.Kunai.teleport(this);
    else @PKG@.Kunai.recall(this);
  } catch (Throwable t) { @PKG@.Kunai.warn("job" + this.kind, (this.kind == 1 ? "teleport" : "return") + " failed (" + t + ")"); }
}""")

'''
before('''# ---- ArmoryTravSys.onEntityAdded (SPAWN of one of our projectiles): quick orbs -> range / pierce record; wand charged orb -> burst''', BK_JAVA)

# ================================================================================================ the plugin: bridge keys, setup / shutdown, the start line
rep('''BRIDGE_KEYS = ["armory:wands", "armory:staffs", "armory:quick", "armory:fn:info", "armory:check", "gear:loot:add:SkyyArmory", "armory:trav",
               "armory:grapple", "armory:leap"]''', '''BRIDGE_KEYS = ["armory:wands", "armory:staffs", "armory:quick", "armory:fn:info", "armory:check", "gear:loot:add:SkyyArmory", "armory:trav",
               "armory:grapple", "armory:leap", "armory:book", "armory:kunai"]''')
after('''  b.put("armory:leap", @PKG@.ArmoryCfg.LEAP_TEXT);
''', '''  b.put("armory:book", @PKG@.ArmoryCfg.BOOK_TEXT);          // 0.1.6
  b.put("armory:kunai", @PKG@.ArmoryCfg.KUNAI_TEXT);
''')
rep('''  @PKG@.Leap.STATES.clear();
  systems();''', '''  @PKG@.Leap.STATES.clear();
  @PKG@.Levitate.STATES.clear();          // 0.1.6
  @PKG@.Levitate.SAFE.clear();
  @PKG@.Kunai.STATES.clear();
  @PKG@.Kunai.RET.clear();
  @PKG@.Kunai.RETST.clear();
  @PKG@.Kunai.FLY.clear();
  @PKG@.Kunai.FLYU.clear();
  @PKG@.Kunai.KNOCK.clear();
  systems();''')
after('''  @PKG@.ArmoryLog.info("@VERSION@ leap: " + @PKG@.ArmoryCfg.LEAP_TEXT + (m13.length() > 0 ? "; " + m13 : "") + (m14.length() > 0 ? "; " + m14 : ""));
''', '''  @PKG@.ArmoryLog.info("@VERSION@ spellbooks + kunai: " + @PKG@.ArmoryCfg.BOOK_TEXT + " | " + @PKG@.ArmoryCfg.KUNAI_TEXT);
''')
rep('''  @PKG@.Leap.STATES.clear();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''', '''  @PKG@.Leap.STATES.clear();
  @PKG@.Levitate.STATES.clear();          // 0.1.6
  @PKG@.Levitate.SAFE.clear();
  @PKG@.Kunai.STATES.clear();
  @PKG@.Kunai.RET.clear();
  @PKG@.Kunai.RETST.clear();
  @PKG@.Kunai.FLY.clear();
  @PKG@.Kunai.FLYU.clear();
  @PKG@.Kunai.KNOCK.clear();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''')
rep('''                 "the wand hold hangs too. Copper + Onyxium crossbows. "''', '''                 "the wand hold hangs too. Copper + Onyxium crossbows. Mage spellbooks Copper to Onyxium (tap = Page Burst, hold = Levitate) and "
                 "Assassin kunai Crude to Onyxium (tap = throw, hold = throw + teleport, hold right click = return). "''')

# ================================================================================================ jar check + build lines
rep('''    _sitems = sorted(n for n in _names if n.startswith("Server/Item/Items/Weapon/Staff/"))''', '''    _bkn = sorted(n for n in _names if n in set(BK_FILES))
    assert _bkn == BK_FILES and len([n for n in BK_FILES if n.startswith("Server/Item/Items/")]) == 15, "0.1.6: the %d book + kunai files" % len(BK_FILES)
    assert not [n for n in _names if os.path.basename(n) in ("Weapon_Kunai.json", "Spellbook_Primary.json", "Projectile_Config_Kunai.json")], \\
        "0.1.6 overrides no vanilla kunai / spellbook file (the vanilla Kunai stays plain loot)"
    _sitems = sorted(n for n in _names if n.startswith("Server/Item/Items/Weapon/Staff/"))''')
rep('''print("0.1.5 staff looks (tools/art/make_staffs.py at build time): " + "; ".join("%s %d boxes, texture %dx%d, %s" % (
    _m, STAFF_ART[_m][3], STAFF_ART[_m][4][0], STAFF_ART[_m][4][1], STAFF_REVIEW[_m]) for _m in NEW_METALS))''',
    '''print("0.1.5 staff looks (tools/art/make_staffs.py at build time): " + "; ".join("%s %d boxes, texture %dx%d, %s" % (
    _m, STAFF_ART[_m][3], STAFF_ART[_m][4][0], STAFF_ART[_m][4][1], STAFF_REVIEW[_m]) for _m in NEW_METALS))
print("0.1.6 spellbooks + kunai: %d files (15 items, %d interactions, %d projectiles, %d kunai configs + models, art %s / %s), %d scalar rows + %d "
      "tables + %d read-only rows, codes 7000 (burst orbs) 8000 (Levitate) 9000 (return), partners SkyyClasses %s / SkyyGear %s" % (
          len(BK_FILES), len(BK_INTS), len(BK_PRJS), len(KCFGS), sorted(set(BOOK_REVIEW.values())), sorted(set(KUNAI_REVIEW.values())), len(CFG_BK),
          len(BK_TAB), len([f for f in FIXED if f[0].startswith(("fixed.book", "fixed.kunai"))]), CLASSES_PARTNER, GEAR_PARTNER))''')

assert s.count("registerSystem(") == SYS0, "0.1.6 registers no new system (TravTick / ArmoryTravSys / ArmoryHitSys / GrappleBoltSys / GrappleFallSys carry it)"
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))

# ================================================================================================ the harness: 0.1.5's checks (+ the set changes) + R10
traw = open(TSRC, encoding="utf8", newline="").read()
TNL = CR + LF if (CR + LF) in traw else LF
ts = traw.replace(CR + LF, LF)


def hrep(old, new, count=1):
    global ts
    n = ts.count(old)
    assert n == count, "harness anchor count %d (want %d): %s" % (n, count, old[:140])
    ts = ts.replace(old, new)


hrep('"""SkyyArmory 0.1.5 - test harness. GENERATED by tools/armory_0_1_5_patch.py from test_skyyarmory_0.1.4.py - edit the patch, never this file.',
     '''"""SkyyArmory 0.1.6 - test harness. GENERATED by tools/armory_0_1_6_patch.py from test_skyyarmory_0.1.5.py - edit the patch, never this file.
Every 0.1.5 check below still runs, patched only where 0.1.6 changed the set on purpose (+ 15 items, the book / kunai interactions, roots,
projectiles, configs, models, PNGs, rows and classes in the counts; R9's 0.1.4 -> 0.1.5 jar compare moved to R10's 0.1.5 -> 0.1.6 compare).
NEW section R10 (JVM, after R8) EXECUTES every 0.1.6 path on real engine objects (the 0.1.1 / 0.1.2 stand-ins):
  R10a the assets: the 15 items / chains / projectiles / kunai configs decode through the engine codecs; the art = tools/art/make_spellbooks.py +
       make_kunai.py run again (byte for byte); the book Mana check = its spend; the kunai files name no inventory / ammo / stat;
  R10b the Page Burst: the orb's SPAWN -> the record + the range watch; its direct hit -> every enemy in the radius NEAREST FIRST up to the cap
       (the direct target counts), never allies / strangers with PvP off; a miss bursts where it ended; past book.range -> removed -> bursts;
       ArmoryTuneSys x book.k / 0.4; book.edgeFalloff; part.book off = a plain orb;
  R10c Levitate: the marker removed at its SPAWN, the cost (Mana + capped Stamina), the rise Sets, the hover Sets (look x drift x walk 5.5,
       holding the height), crouch ends it, the safe time (GrappleFallSys cancels FALL damage until the hover end + 3 s, not after), the float
       cap; refusals cost nothing (ceiling within 2 blocks, class lock, a damaging fall, too little Mana);
  R10d the kunai: a tap = range watch (removed past kunai.throwRange); a hold = cost + impact wrap + the record; landing on a block / a mob /
       out of range / the flight time -> the teleport job -> TravMath.scan safety (walls, 1 block short of a mob; NO void check by default) -> Teleport (velocity
       kept); no move / a non-party player with PvP off / a locked arena = refunded; the hand change / a newer kunai = cancelled + refunded;
       cooldown / spam net / combat = a normal throw; too little Stamina = no throw; the return (window, safe spot within 3 blocks, the
       knockback ring next tick, enemies only); ArmoryTuneSys x kunai.dpsShare / 0.8 on the kunai's model;
  R10e the rows (20 scalars + 13 tables + 17 read-only), the loader clamps, armory:book / armory:kunai, the default file's lines;
  R10f vs the 0.1.5 jar: the new files = exactly the 0.1.6 set, every other non-class file byte-identical (the lang file only grows), the
       changed classes listed.

0.1.5 harness: SkyyArmory 0.1.5 - test harness. GENERATED by tools/armory_0_1_5_patch.py from test_skyyarmory_0.1.4.py - edit the patch, never this file.''')
hrep('VERSION = "0.1.5"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.5 SkyyArmory"',
     'VERSION = "0.1.6"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.6 SkyyArmory"')
hrep('os.path.join(SCRATCH_ROOT, "armory015", "harness")', 'os.path.join(SCRATCH_ROOT, "armory016", "harness")')
hrep('raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.5.py', 'raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.6.py')
hrep('Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.5"))', 'Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.6"))')
hrep('"[SkyyArmory] 0.1.5 ready" in m_', '"[SkyyArmory] 0.1.6 ready" in m_')
hrep('"0.1.5 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_', '"0.1.6 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_')
hrep('"0.1.5 crossbow grapple: grapple on" in m_', '"0.1.6 crossbow grapple: grapple on" in m_')
hrep('come from Skyy:0.1.5 SkyyArmory" in str(r[1])', 'come from Skyy:0.1.6 SkyyArmory" in str(r[1])')
# R9: the 0.1.4 -> 0.1.5 jar compare is history (R10f compares 0.1.5 -> 0.1.6); its art checks still run on this jar
hrep('''OLD_JAR = os.path.join(HERE, "SkyyArmory-0.1.4.jar")
if not os.path.isfile(OLD_JAR):
    _inst = os.path.join(B.MODS_DIR, "SkyyArmory.jar")
    try:
        with zipfile.ZipFile(_inst) as _iz:
            OLD_JAR = _inst if json.loads(_iz.read("manifest.json").decode("utf-8-sig")).get("Version") == "0.1.4" else None
    except Exception:
        OLD_JAR = None''', '''OLD_JAR = None          # 0.1.6: the 0.1.4 -> 0.1.5 compare is history - R10f compares 0.1.5 -> 0.1.6''')
hrep('''    print("R9. NOTE no 0.1.4 jar here (SkyyArmory/SkyyArmory-0.1.4.jar or an installed 0.1.4 Mods/SkyyArmory.jar) - the old-vs-new file compare is skipped")''',
     '''    print("R9. NOTE (0.1.6) the 0.1.4 -> 0.1.5 file compare is history - R10f compares 0.1.5 -> 0.1.6")''')

# P0: the 0.1.6 spellbook + kunai files are checked in R10 - every 0.1.5 check below sees the 0.1.5 set (the 0.1.3 crossbow pattern)
hrep('''J_PNG = sorted(n for n in JN if n.endswith(".png"))
''', '''J_PNG = sorted(n for n in JN if n.endswith(".png"))
# 0.1.6: the spellbook + kunai files are checked in R10; the 0.1.5 checks below see the 0.1.5 set
L16_PRE = ("Weapon_Spellbook_", "Weapon_Kunai_", "SkyyArmory_Spellbook_", "SkyyArmory_Kunai_")


def l16_pop(d):
    return dict((k_, d.pop(k_)) for k_ in sorted(d) if k_.startswith(L16_PRE))


L16_ITEMS, L16_INTS, L16_ROOTS, L16_PRJ, L16_MODELS = l16_pop(J_ITEMS), l16_pop(J_INTS), l16_pop(J_ROOTS), l16_pop(J_PRJ), l16_pop(J_MODELS)
L16_PNG = [n for n in J_PNG if n.startswith(("Common/Items/Weapons/Spellbook/", "Common/Items/Weapons/Kunai/"))
           or "/SkyyArmory_Spellbook_" in n or "/SkyyArmory_Kunai_" in n]
J_PNG = [n for n in J_PNG if n not in L16_PNG]
''')
hrep('''J_PCFG = by_dir("Server/ProjectileConfigs/")
''', '''J_PCFG = by_dir("Server/ProjectileConfigs/")
L16_PCFG = l16_pop(J_PCFG)          # 0.1.6: the kunai configs (R10)
''')

hrep('''    check(len(names) == 37, "A: 37 classes (30 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap classes + 7 kit)")''',
     '''    check(len(names) == 43, "A: 43 classes (36 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap + 0.1.6's 6 book / kunai classes + 7 kit)")''')

# ---- K: the config kit rows (+ 0.1.6's 20 scalars after the 0.1.3 rows, 13 tables, 17 read-only rows)
hrep('''                 "bow.stamina", "bow.mana"]      # 0.1.3
    NN = len(NEW_ROWS)''', '''                 "bow.stamina", "bow.mana"]      # 0.1.3
    NEW_ROWS += ["part.book", "book.k", "book.range", "book.edgeFalloff", "lev.safeAfter", "lev.crouchLands", "lev.riseSpeed", "lev.floatFall",
                 "part.kunai", "kunai.dpsShare", "kunai.throwRange", "kunai.flightTtl", "kunai.floorCheck", "kunai.behindMob", "kunai.noArena",
                 "kunai.noCombat", "kunai.pvp", "kunai.maxPerMinute", "ret.force", "ret.damage"]      # 0.1.6
    TAB16 = ["book.radius", "book.targets", "lev.height", "lev.hover", "lev.drift", "lev.mana", "lev.stamina", "kunai.range", "kunai.cooldown",
             "kunai.stamina", "kunai.mana", "ret.window", "ret.radius"]      # 0.1.6 per-metal tables
    NN = len(NEW_ROWS)''')
hrep('''    check(keys[:10] == want_rows and keys[10:10 + NN] == NEW_ROWS and all(k.startswith("fixed.") or k in ("staff.stamina", "hop.mode", "grapple.flight", "grapple.rightClick") for k in keys[10 + NN:])
          and len(keys) == 10 + NN + 8 + 8 + 5 + 2 + 2,''', '''    check(keys[:10] == want_rows and keys[10:10 + NN] == NEW_ROWS and keys[10 + NN:10 + NN + 13] == TAB16
          and all(k.startswith("fixed.") or k in ("staff.stamina", "hop.mode", "grapple.flight", "grapple.rightClick") for k in keys[10 + NN + 13:])
          and len(keys) == 10 + NN + 13 + 8 + 8 + 5 + 2 + 2 + 17,''')
hrep('''          and all(flags[k] == "ro" for k in keys[10 + NN:]) and all(len(h) <= 100 for h in helps.values()) and types["quick.life"] == "int"''',
     '''          and all(flags[k] == "ro" for k in keys[10 + NN + 13:]) and all(types[k] == "table" for k in TAB16) and all(len(h) <= 100 for h in helps.values()) and types["quick.life"] == "int"''')
# ---- R4: TravTick now also runs Levitate + Kunai (4 tickPlayer calls)
hrep('''    check(tt4.count("tickPlayer") == 2 and "onBowShot" in gb4, "R4: TravTick runs Grapple.tickPlayer AND Leap.tickPlayer; GrappleBoltSys hands our arrow model to Leap.onBowShot")''',
     '''    check(tt4.count("tickPlayer") == 4 and "onBowShot" in gb4, "R4: TravTick runs Grapple.tickPlayer AND Leap.tickPlayer (0.1.6: + Levitate + Kunai); GrappleBoltSys hands our arrow model to Leap.onBowShot")''')
# ---- L: the 0.1.6 assets decode through the engine codecs and load from our pack (R10a), then the pack check counts them
L16_LOAD = r'''    # ---- 0.1.6 (R10a): the spellbook + kunai assets through the engine codecs (no unknown key, no failed validation) into the real stores
    bad16, van16 = [], []
    for i_ in ("DamageEntityParent",):          # the kunai hit's inline vanilla parent
        if INTc.getAssetMap().getAsset(i_) is None:
            o_, w_ = decp(INTc, i_, INTS_ALL[i_] if i_ in INTS_ALL else aj("int", i_))
            if o_ is None or load(INTc, [o_], "Hytale:Hytale") is not True:
                van16.append(i_)
    for c_, tab_, kind_ in ((INTc, L16_INTS, "interaction"), (ROOTc, L16_ROOTS, "root"), (PRJc, L16_PRJ, "projectile"), (MDLc, L16_MODELS, "model"),
                            (PCFGc, L16_PCFG, "pcfg"), (ITMc, L16_ITEMS, "item")):
        objs_ = []
        for k_ in sorted(tab_):
            o_, w_ = dec(c_, k_, JZ.read(tab_[k_]).decode("utf-8"))
            if o_ is None or w_:
                bad16.append("%s %s: %s" % (kind_, k_, w_))
                continue
            DEC[(kind_, k_)] = o_
            objs_.append(o_)
        load(c_, objs_, PACK)
        for k_ in sorted(tab_):
            if kind_ != "pcfg" and (c_.getAssetMap().getAsset(k_) is None or str(c_.getAssetMap().getAssetPack(k_)) != PACK):
                bad16.append("%s %s is not in the store from our pack" % (kind_, k_))
    check(not bad16 and len(L16_ITEMS) == 15 and len(L16_INTS) == 85 and len(L16_ROOTS) == 23 and len(L16_PRJ) == 22 and len(L16_MODELS) == 16
          and len(L16_PCFG) == 16, "L (0.1.6 / R10a): the 15 items, 85 interactions, 23 roots, 22 projectiles, 16 kunai models + 16 kunai configs decode "
                                   "through the engine codecs (no unknown key) and sit in the real stores from our pack: %s %s" % (bad16[:4], van16))
    dbad16 = [k_ for k_ in L16_ITEMS if ("item", k_) not in DEC or int(DEC[("item", k_)].getMaxStack()) != 1 or DEC[("item", k_)].getWeapon() is None]
    check(not dbad16, "R10a: every spellbook + kunai decodes as a weapon with MaxStack 1 (one reusable item, never a stack of thrown ammo): %s" % dbad16)
'''
hrep('''    CHK = JClass(PKG + "ArmoryCheck")
    r = CHK.packCheck()
    check(str(r[0]) == "info" and "17 of 17 items, 122 of 122 interactions, 40 of 40 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.6 SkyyArmory" in str(r[1])''',
     L16_LOAD + '''    CHK = JClass(PKG + "ArmoryCheck")
    r = CHK.packCheck()
    check(str(r[0]) == "info" and "32 of 32 items, 207 of 207 interactions, 62 of 62 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.6 SkyyArmory" in str(r[1])''')

# ---- R10: every 0.1.6 path EXECUTED (inserted after R8, before the L2 WARN case that changes the store)
R10 = r'''    # ============================================================================ R10. 0.1.6 SPELLBOOKS + KUNAI - every new path EXECUTED
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    LV, KU, KJ = JClass(PKG + "Levitate"), JClass(PKG + "Kunai"), JClass(PKG + "KunaiJob")
    KImp = JClass(PKG + "KunaiImpact")
    ADf = JClass(PKG + "ArmoryDefs")
    BM = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
    KM = ["Crude"] + BM
    BURST = dict((m_, "SkyyArmory_Spellbook_Burst_" + m_) for m_ in BM)
    LEVM = dict((m_, "SkyyArmory_Spellbook_Levitate_" + m_) for m_ in BM)
    KT = dict((m_, "SkyyArmory_Kunai_Throw_" + m_) for m_ in KM)
    KP = dict((m_, "SkyyArmory_Kunai_Teleport_" + m_) for m_ in KM)
    KRM = dict((m_, "SkyyArmory_Kunai_ReturnMark_" + m_) for m_ in KM)
    br.put("party:fn:members", Members())
    TW.ALL.clear()
    LP.STATES.clear()
    LP.HAND = HashMap()
    LP.LOOK = HashMap()
    LV.STATES.clear()
    LV.SAFE.clear()
    KU.STATES.clear()
    KU.RET.clear()
    KU.RETST.clear()
    KU.FLY.clear()
    KU.FLYU.clear()
    KU.LASTPORT.clear()
    KU.PERMIN.clear()
    KU.FIGHT.clear()
    KU.KNOCK.clear()
    AT.GRID = Grid(world_fn())
    TWd.JOBS.clear()
    reset_buf()
    put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    put(rc, TPc.getComponentType(), None)
    vel_r = comp(rc, VELc.getComponentType())
    vel_r.setClient(0.0, 0.0, 0.0)
    mc.setStatValue(MANA, JFloat(200.0))
    mc.setStatValue(STAM, JFloat(10.0))
    NEARL[:] = []

    @JImplements("java.util.function.Function")
    class NearR:          # the sphere query with its radius (the 0.1.1 seam answers everything): entities whose body centre is within r
        @JOverride
        def apply(self, o):
            q_ = list(o)
            l_ = ArrayList()
            for r_ in NEARL:
                tc_ = comp(r_, TCc.getComponentType())
                if tc_ is None:
                    continue
                p_ = tc_.getPosition()
                if math.sqrt((p_.x() - q_[0]) ** 2 + (p_.y() + 0.9 - q_[1]) ** 2 + (p_.z() - q_[2]) ** 2) <= q_[3] + 1e-9:
                    l_.add(r_)
            return l_
    AT.NEAR = NearR()

    # --- R10a (Python side): the art = the generators run again, the tables, the chains
    sys.path.insert(0, os.path.join(TOOLS, "art"))
    import make_spellbooks as MSB10
    import make_kunai as MKU10
    z10 = SA.assets()
    _bvd, _bvm, _bvt, _bvi = SA.item_parts(z10, MSB10.BASE_ITEM)
    _bva = json.loads(_bvm.decode("utf-8-sig"))
    art_ok = []
    for m_ in BM:
        b_ = MSB10.Builder()
        md_ = MSB10.build_model(_bva, m_, b_)
        pl_ = MSB10.pack(b_, 64)
        tx_, _g = MSB10.make_texture(z10, _bvt, _bva, m_, b_, pl_)
        ic_ = SA.png_encode(MSB10.render(md_, tx_, _bvd["IconProperties"]))
        art_ok.append(((json.dumps(md_, indent=2) + "\n").encode("utf-8"), tx_, ic_) == tuple(
            JZ.read("Common/Items/Weapons/Spellbook/SkyyArmory_%s%s" % (m_, s_)) if not s_.startswith("Icon") else JZ.read("Common/Icons/ItemsGenerated/SkyyArmory_Spellbook_%s.png" % m_)
            for s_ in (".blockymodel", "_Texture.png", "Icon")))
    _kvd, _kvm, _kvt, _kvi = SA.item_parts(z10, MKU10.BASE_ITEM)
    _kmd = json.loads(_kvm.decode("utf-8-sig"))
    for m_ in KM:
        kt_ = MKU10.kunai_texture(z10, m_, _kmd, _kvt, MKU10.crude_gradients(z10) if m_ == "Crude" else None)
        ki_ = SA.render_icon(_kmd, kt_, _kvd["IconProperties"], 64)
        art_ok.append((kt_, ki_) == (JZ.read("Common/Items/Weapons/Kunai/SkyyArmory_%s_Texture.png" % m_), JZ.read("Common/Icons/ItemsGenerated/SkyyArmory_Kunai_%s.png" % m_)))
    crude_t = JZ.read("Common/Items/Weapons/Kunai/SkyyArmory_Crude_Texture.png")
    z10.close()
    check(all(art_ok) and len(art_ok) == 15 and crude_t != _kvt and crude_t != JZ.read("Common/Items/Weapons/Kunai/SkyyArmory_Copper_Texture.png"),
          "R10a (Skyy: match the wands): tools/art/make_spellbooks.py + make_kunai.py run again here = the jar's 7 book models / textures / icons and 8 "
          "kunai textures / icons byte for byte (Crude = the new stone + wood look, not the vanilla texture): %s" % art_ok)
    jb = dict((k_, json.loads(JZ.read(p_).decode("utf-8"))) for k_, p_ in L16_INTS.items())
    jitm = dict((k_, json.loads(JZ.read(p_).decode("utf-8"))) for k_, p_ in L16_ITEMS.items())
    jcfg = dict((k_, json.loads(JZ.read(p_).decode("utf-8"))) for k_, p_ in L16_PCFG.items())
    want_b = [(40, 90), (55, 128), (70, 168), (85, 207), (115, 283), (130, 321), (130, 321)]
    gb = []
    for i_, m_ in enumerate(BM):
        ch_ = jb["SkyyArmory_Spellbook_Primary_" + m_]
        sc_ = jb[ch_["Next"]["0"]]
        cost_ = jb["SkyyArmory_Spellbook_Cast_Cost_" + m_]["StatModifiers"]["Mana"]
        prj_ = json.loads(JZ.read(L16_PRJ[BURST[m_]]).decode("utf-8"))
        gb.append((sc_["Costs"]["Mana"], -cost_, prj_["Damage"], ch_["Next"]["1"] == "SkyyArmory_Spellbook_Lev_" + m_,
                   jitm["Weapon_Spellbook_" + m_]["Interactions"] == {"Primary": ch_ and "SkyyArmory_Spellbook_Primary_" + m_, "Secondary": "SkyyArmory_Spellbook_Primary_" + m_}))
    check([(g_[0], g_[2]) for g_ in gb] == want_b and all(g_[0] == g_[1] and g_[3] and g_[4] for g_ in gb)
          and [int(x) for x in ADf.B_COST] == [w_[0] for w_ in want_b] and [int(x) for x in ADf.B_DMG] == [w_[1] for w_ in want_b],
          "R10a (spec 2 table): the tap checks = spends 40 / 55 / 70 / 85 / 115 / 130 / 130 Mana, the burst orb deals 90 / 128 / 168 / 207 / 283 / 321 / 321 "
          "per target, the 1 s hold = Levitate, Primary + Secondary = the book chain: %s" % gb)
    kd_ = [jcfg[KT[m_]]["Interactions"]["ProjectileHit"]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Physical"] for m_ in KM]
    ktxt = json.dumps(jcfg) + json.dumps([v_ for k_, v_ in jb.items() if k_.startswith("SkyyArmory_Kunai")]) + json.dumps([jitm[k_] for k_ in jitm if "Kunai" in k_])
    check(kd_ == [5, 7, 9, 12, 12, 14, 18, 18] and [int(x) for x in ADf.K_DMG] == kd_ and all(jcfg[KP[m_]] == dict(jcfg[KT[m_]], Model=KP[m_]) for m_ in KM)
          and all(jcfg[KT[m_]]["Physics"]["Gravity"] == 6 for m_ in KM) and "ModifyInventory" not in ktxt and '"Ammo"' not in ktxt
          and "StatModifiers" not in ktxt and "MaxStack" not in ktxt and "Utility" not in ktxt,
          "R10a (Kunai-Ladder 3 + 5): the kunai hit = 1.12 x the same-metal dagger's average (5 / 7 / 9 / 12 / 12 / 14 / 18 / 18), the teleport kunai = "
          "the same shot under its own model id, nearly straight (gravity 6); no file names the inventory, ammo, a stat, a stack size or the off-hand: %s" % kd_)

    # --- R10b. THE PAGE BURST (ArmoryTravSys SPAWN -> ArmoryHitSys landed -> bookBurst; a miss / the range -> removed -> bookBurst)
    tw = TW.get(tst)
    n_dir = npc(1601, 5.0, 64.0, 0.5)
    n_a, n_b, n_c, n_d = npc(1602, 6.0, 64.0, 0.5), npc(1603, 5.0, 64.0, 2.0), npc(1604, 3.0, 64.0, 0.5), npc(1605, 5.0, 64.0, -2.0)
    n_far = npc(1606, 9.5, 64.0, 0.5)
    put(rp, TCc.getComponentType(), TCc(V3(5.5, 64.0, 1.0), R3(0.0, 0.0, 0.0)))
    put(rs, TCc.getComponentType(), TCc(V3(4.5, 64.0, 1.0), R3(0.0, 0.0, 0.0)))
    NEARL[:] = [n_dir, n_a, n_b, n_c, n_d, n_far, rp, rs, rc]
    ob1, opb1 = launched(BURST["Copper"], 1610, 0.5, 65.5, 0.5)
    AT.added(ob1, opb1, int(ADf.pidCode(BURST["Copper"])), tst, tbuf)
    rec1 = (int(ADf.pidCode(BURST["Copper"])), tw.orbs.containsKey(ob1), tw.books.containsKey(ob1), float(tw.books.get(ob1).range) if tw.books.containsKey(ob1) else None)
    reset_buf()
    d1 = DMGc(DPS(rc, ob1), DCSc.PROJECTILE, JFloat(90.0))
    AT.landed(tst, tbuf, d1, ob1, 7000, n_dir)
    ev1 = events()
    check(rec1 == (7000, True, True, 20.0) and ev1 == [(1602, 90.0, "ProjectileSource", 1610), (1603, 90.0, "ProjectileSource", 1610), (1604, 90.0, "ProjectileSource", 1610)],
          "R10b (spec 2): a Copper Page Burst orb's SPAWN -> the burst record + the 20-block range watch; its direct hit on one mob -> the 3 NEAREST other "
          "enemies inside 3 blocks take the full 90 each (cap 4 = the direct target + 3: the 4th at 2.5 blocks and the one at 4.5 do not; the party "
          "member, the stranger (PvP off) and you never): %s %s" % (rec1, ev1))
    AT.landed(tst, tbuf, DMGc(DPS(rc, ob1), DCSc.PROJECTILE, JFloat(90.0)), ob1, 7000, n_dir)
    once1 = len(events()) == len(ev1)
    wcfg.setPvpEnabled(True)
    ACfg.BOOK_T = JArray(JDouble)([9, 4, 5, 5, 6, 6, 6])
    ACfg.BOOK_FALL = 50
    reset_buf()
    ob2, opb2 = launched(BURST["Copper"], 1611, 0.5, 65.5, 0.5)
    AT.added(ob2, opb2, 7000, tst, tbuf)
    AT.landed(tst, tbuf, DMGc(DPS(rc, ob2), DCSc.PROJECTILE, JFloat(90.0)), ob2, 7000, n_dir)
    ev2 = dict((e_[0], e_[1]) for e_ in events())
    wcfg.setPvpEnabled(False)
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    check(once1 and sorted(ev2) == [3, 1602, 1603, 1604, 1605] and abs(ev2[1602] - 90.0 * (1 - 0.5 * 1.0 / 3.0)) < 1e-3
          and abs(ev2[1605] - 90.0 * (1 - 0.5 * 2.5 / 3.0)) < 1e-3 and 2 not in ev2 and 1 not in ev2,
          "R10b: a burst happens once per orb; with PvP on the stranger is an enemy too (the party member and you never), cap 9 takes all 5 inside, "
          "book.edgeFalloff 50 = 90 x (1 - 0.5 x d / 3) (75 at 1 block, 52.5 at 2.5): %s" % ev2)
    # a miss (removed without a hit) bursts where it ended with the asset damage x the tune; past book.range the watch removes it -> the same
    reset_buf()
    ob3, opb3 = launched(BURST["Copper"], 1612, 0.5, 65.5, 0.5)
    AT.added(ob3, opb3, 7000, tst, tbuf)
    comp(ob3, TCc.getComponentType()).getPosition().set(5.0, 64.9, 0.5)
    AT.removed(ob3, True, tst, tbuf)
    ev3 = sorted(events())
    ob4, opb4 = launched(BURST["Copper"], 1613, 0.5, 65.5, 0.5)
    AT.added(ob4, opb4, 7000, tst, tbuf)
    reset_buf()
    tw.lastNs = 0
    comp(ob4, TCc.getComponentType()).getPosition().set(15.0, 64.9, 0.5)
    tw.run(tst, tbuf, nowms())
    near4 = (ob4 in list(TBf.REMOVED), tw.books.containsKey(ob4))
    comp(ob4, TCc.getComponentType()).getPosition().set(21.5, 64.9, 0.5)
    tw.run(tst, tbuf, nowms())
    rng4 = (ob4 in list(TBf.REMOVED), tw.books.containsKey(ob4), int(AT.BOOK_RANGED) >= 1)
    check([e_[0] for e_ in ev3] == [1601, 1602, 1603, 1604] and all(e_[1] == 90.0 and e_[2] == "EntitySource" for e_ in ev3)
          and near4 == (False, True) and rng4 == (True, False, True),
          "R10b (spec 2: bursts where it hits the ground or at its max range): a miss bursts where the orb ended - 4 targets nearest first, 90 each "
          "(EntitySource - the orb is gone); the range watch leaves an orb 14.5 blocks out alone and removes it past 20 (the removal = the miss burst): %s %s %s" % (ev3, near4, rng4))
    TS10 = JClass(PKG + "ArmoryTuneSys")(False)
    ACfg.BOOK_K = 0.6
    dk = DMGc(DPS(rc, ob1), DCSc.PROJECTILE, JFloat(90.0))
    TS10.handle(0, None, tst, tbuf, dk)
    ACfg.PART_TUNE = False
    dk2 = DMGc(DPS(rc, ob1), DCSc.PROJECTILE, JFloat(90.0))
    TS10.handle(0, None, tst, tbuf, dk2)
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    ACfg.PART_BOOK = False
    ob5, opb5 = launched(BURST["Copper"], 1614, 0.5, 65.5, 0.5)
    AT.added(ob5, opb5, 7000, tst, tbuf)
    off5 = (tw.orbs.containsKey(ob5), tw.books.containsKey(ob5))
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    check(abs(float(dk.getAmount()) - 135.0) < 1e-3 and float(dk2.getAmount()) == 90.0 and off5 == (False, False),
          "R10b: book.k 0.6 -> every burst hit x 0.6 / 0.4 (90 -> 135, ArmoryTuneSys on the orb's own pid); part.tune off = untouched; part.book off = "
          "a plain orb (no record, no burst): %s %s %s" % (float(dk.getAmount()), float(dk2.getAmount()), off5))
    # FIX2 (critic 2): part.trav OFF + part.book on -> ArmoryHitSys still routes a Page Burst direct hit to the burst, so the removal that
    # follows is no second "miss" burst on the same mob (was: the direct mob took the hit + a full miss burst); the burst draws the ring
    ACfg.PART_TRAV = False
    ACfg.TRAV_FX = True
    AT.PSEEN = ArrayList()
    reset_buf()
    ob6, opb6 = launched(BURST["Copper"], 1615, 0.5, 65.5, 0.5)
    AT.added(ob6, opb6, 7000, tst, tbuf)
    TCh.TARGET = n_dir
    HS.handle(0, chunk, tst, tbuf, DMGc(DPS(rc, ob6), DCSc.PROJECTILE, JFloat(90.0)))
    ev6a = sorted(events())
    comp(ob6, TCc.getComponentType()).getPosition().set(5.0, 64.9, 0.5)
    AT.removed(ob6, True, tst, tbuf)
    ev6b = sorted(events())
    rings6 = len([x_ for x_ in list(AT.PSEEN) if str(x_) == "SkyyArmory_Ring_Blue"])
    AT.PSEEN = None
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    check([e_[0] for e_ in ev6a] == [1602, 1603, 1604] and ev6b == ev6a and 1601 not in [e_[0] for e_ in ev6b] and rings6 == 12,
          "R10b FIX2: part.trav off, part.book on - a Page Burst direct hit still bursts through ArmoryHitSys (3 others, cap 4) and the orb's removal "
          "after that hit adds NOTHING (the direct mob is never hit twice); the burst draws 12 blue ring points at the radius: %s %s rings %d" % (ev6a, ev6b, rings6))
    print("R10b. Page Burst: nearest-first cap, PvP / party rules, falloff, once per orb, miss + range bursts, book.k tune, part.book off")

    # --- R10c. LEVITATE (the hold's marker SPAWN -> Levitate.begin; TravTick -> Levitate.tickPlayer; GrappleFallSys -> Levitate.fallSafe)
    NEARL[:] = []
    LP.HAND.put(cu, "Weapon_Spellbook_Copper")
    LP.LOOK.put(cu, JArray(JDouble)([0.5, 65.6, 0.5, 1.0, 0.0, 0.0]))
    reset_buf()
    om1, opm1 = launched(LEVM["Copper"], 1620, 0.5, 65.5, 0.5)
    AT.added(om1, opm1, int(ADf.pidCode(LEVM["Copper"])), tst, tbuf)
    s1 = LV.STATES.get(cu)
    i1 = last_instr(rc)
    begin1 = (int(ADf.pidCode(LEVM["Copper"])), om1 in list(TBf.REMOVED), s1 is not None and int(s1.phase), sv(mc, MANA), sv(mc, STAM), i1[0] if i1 else None,
              i1[1] if i1 else None, i1[2] if i1 else "x", round(float(s1.top), 3) if s1 is not None else None)
    check(begin1 == (8000, True, 1, 190.0, 5.0, (0.0, 10.0, 0.0), "Set", None, 72.0),
          "R10c (spec 3): a Copper spellbook hold -> the invisible marker is removed at its SPAWN, 10 Mana + 5 Stamina paid once, the RISE starts "
          "(a Velocity Set straight up at lev.riseSpeed 10, no config = the hang path), up to 8 blocks (top y 72): %s" % (begin1,))
    n1 = i1[3]
    LV.tickPlayer(rc, tst, tbuf)
    rise_n = last_instr(rc)[3] - n1
    fall_rise = fall(rc)
    comp(rc, TCc.getComponentType()).getPosition().set(0.5, 72.0, 0.5)
    LV.tickPlayer(rc, tst, tbuf)
    h1 = last_instr(rc)
    hov1 = (int(s1.phase), h1[0], 2900 <= int(s1.hoverUntil) - nowms() <= 3100)
    comp(rc, TCc.getComponentType()).getPosition().set(0.5, 71.0, 0.5)
    LP.LOOK.put(cu, JArray(JDouble)([0.5, 72.6, 0.5, 0.0, 0.8, 0.6]))
    LV.tickPlayer(rc, tst, tbuf)
    h2 = last_instr(rc)
    fall_hover = fall(rc)
    check(rise_n == 1 and fall_rise and hov1 == (2, (4.4, 0.0, 0.0), True) and h2[0] == (0.0, 3.0, 4.4) and fall_hover,
          "R10c (spec 3): a Set up every tick while rising; at the top -> the HOVER for lev.hover 3 s: a Set every tick = the look's HORIZONTAL direction "
          "x drift 0.8 x the walk speed 5.5 (= 4.4 b/s, looking up still drifts flat) and the height held ((72 - 71) x 4 = 3 b/s up); no FALL damage while "
          "rising or hovering (GrappleFallSys): %s %s %s" % (rise_n, hov1, h2))
    msc_ = MSCc()
    mst_ = JClass("com.hypixel.hytale.protocol.MovementStates")()
    mst_.crouching = True
    msc_.setMovementStates(mst_)
    put(rc, MSCc.getComponentType(), msc_)
    LV.tickPlayer(rc, tst, tbuf)
    cr = (int(s1.phase), str(s1.endWhy), 2900 <= int(s1.safeUntil) - nowms() <= 3100, LV.SAFE.containsKey(cu))
    put(rc, MSCc.getComponentType(), None)
    vel_r.setClient(0.0, -20.0, 0.0)
    nf = last_instr(rc)[3]
    LV.tickPlayer(rc, tst, tbuf)
    fl1 = last_instr(rc)
    vel_r.setClient(0.0, -4.0, 0.0)
    LV.tickPlayer(rc, tst, tbuf)
    fl2 = last_instr(rc)[3] == fl1[3]
    fall_safe = fall(rc)
    s1.safeUntil = nowms() - 1
    LV.SAFE.put(cu, JClass("java.lang.Long")(nowms() - 1))
    fall_after = fall(rc)
    LV.tickPlayer(rc, tst, tbuf)
    gone1 = LV.STATES.get(cu) is None
    vel_r.setClient(0.0, 0.0, 0.0)
    check(cr == (3, "crouch", True, True) and fl1[3] == nf + 1 and fl1[0] == (0.0, -6.0, 0.0) and fl2 and fall_safe and not fall_after and gone1,
          "R10c (spec 3 + lev.crouchLands): crouching ends the hover -> FLOAT: no fall damage until the hover's end + lev.safeAfter 3 s, a fall faster "
          "than lev.floatFall 6 b/s is capped to 6 (a slower one untouched); after the safe time FALL damage counts again and the record ends: %s %s" % (cr, fl1))
    # refusals cost NOTHING: a ceiling within 2 blocks, the class lock, a damaging fall, too little Mana; a roomy enough ceiling lifts you to it
    def lev_try(metal="Copper", grid=None, deny=None, vy=0.0, mana=200.0, stam=10.0):
        LV.STATES.clear()
        AT.GRID = grid if grid is not None else Grid(world_fn())
        if deny:
            br.put("class:fn:allowed", DenyId(deny))
        vel_r.setClient(0.0, vy, 0.0)
        mc.setStatValue(MANA, JFloat(mana))
        mc.setStatValue(STAM, JFloat(stam))
        put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
        reset_buf()
        o_, p_ = launched(LEVM[metal], 1630 + len(LV.STATES) + int(nowms() % 50), 0.5, 65.5, 0.5)
        AT.added(o_, p_, int(ADf.pidCode(LEVM[metal])), tst, tbuf)
        br.remove("class:fn:allowed")
        vel_r.setClient(0.0, 0.0, 0.0)
        s_ = LV.STATES.get(cu)
        return (s_ is not None, sv(mc, MANA), sv(mc, STAM), str(LV.LAST_WHY), None if s_ is None else round(float(s_.top), 2), o_ in list(TBf.REMOVED))
    rf1 = lev_try(grid=Grid(world_fn(ceiling=67)))
    rf2 = lev_try(grid=Grid(world_fn(ceiling=68)))
    rf3 = lev_try(deny="Weapon_Spellbook_Copper")
    rf4 = lev_try(vy=-30.0)
    rf5 = lev_try(mana=5.0)
    rf6 = lev_try(metal="Thorium")
    LV.STATES.clear()
    LV.SAFE.clear()
    AT.GRID = Grid(world_fn())
    check(rf1[:3] == (False, 200.0, 10.0) and rf1[3].startswith("a ceiling") and rf1[5] and rf2[:3] == (True, 190.0, 5.0) and rf2[4] == 66.2
          and rf3[:4] == (False, 200.0, 10.0, "class lock") and rf4[:3] == (False, 200.0, 10.0) and rf4[3].startswith("falling")
          and rf5[:3] == (False, 5.0, 10.0) and rf5[3] == "too little Mana or Stamina" and rf6[:3] == (True, 190.0, 5.0),
          "R10c: a ceiling within 2 blocks = no cast and NOTHING spent (the marker still goes); a ceiling at 4 blocks lifts you 2.2 (to it); the class lock, "
          "a damaging fall (falling 30 b/s) and too little Mana cost nothing; Thorium pays 10 Mana + 5 Stamina (6 capped by trav.staminaCap 5, Mana = 2 x the Stamina paid - fix2): %s" % (
              [rf1, rf2, rf3, rf4, rf5, rf6],))
    print("R10c. Levitate: marker removed, cost once, rise / hover / crouch / float Sets, fall-safe window, refusals free, Stamina cap")

    # --- R10d. THE KUNAI (GrappleBoltSys SPAWN -> Kunai.onShot; KunaiImpact; TravTick -> Kunai.tickPlayer; KunaiJob teleport / return)
    GBS10 = GBS()
    for r_ in (n_dir, n_a, n_b, n_c, n_d, n_far):
        put(r_, VELc.getComponentType(), VELc())
    LP.HAND.put(cu, "Weapon_Kunai_Copper")
    LP.LOOK.put(cu, JArray(JDouble)([0.5, 65.6, 0.5, 1.0, 0.0, 0.0]))

    def kreset(stam=10.0, mana=200.0):
        KU.STATES.clear()
        KU.LASTPORT.clear()
        KU.PERMIN.clear()
        KU.FIGHT.clear()
        KU.RET.clear()
        KU.RETST.clear()
        KU.KNOCK.clear()
        TWd.JOBS.clear()
        reset_buf()
        mc.setStatValue(STAM, JFloat(stam))
        mc.setStatValue(MANA, JFloat(mana))
        put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
        put(rc, TPc.getComponentType(), None)

    def kthrow(model, x=1.0, y=65.6, z=0.5):
        fk_ = FakeImpact()
        b_, sp_ = bolt(x, y, z, creator=cu, model=model, fake=fk_)
        GBS10.onEntityAdded(b_, ADDR.SPAWN, tst, tbuf)
        return b_, sp_, fk_

    def kland(b_, sp_, pos, hit=None):
        sp_.getImpactConsumer().onImpact(b_, V3(pos[0], pos[1], pos[2]), V3Ic(0, 0, 0), hit, "x", tbuf)
        KU.tickPlayer(rc, tst, tbuf)
        jobs_ = list(TWd.JOBS)
        TWd.JOBS.clear()
        for j_ in jobs_:
            j_.run()
        tp_ = comp(rc, TPc.getComponentType())
        return None if tp_ is None else (round(float(tp_.getPosition().x()), 2), round(float(tp_.getPosition().y()), 2), round(float(tp_.getPosition().z()), 2),
                                         bool(tp_.isResetVelocity())), len(jobs_)
    # a TAP = a plain throw: no cost, no record, gone past kunai.throwRange
    kreset()
    bt, spt, fkt = kthrow(KT["Copper"])
    tap1 = (KU.FLY.containsKey(bt), KU.STATES.get(cu) is None, sv(mc, STAM), sv(mc, MANA))
    comp(bt, TCc.getComponentType()).getPosition().set(15.0, 65.6, 0.5)
    KU.tickPlayer(rc, tst, tbuf)
    tap2 = bt in list(TBf.REMOVED)
    comp(bt, TCc.getComponentType()).getPosition().set(21.5, 65.6, 0.5)
    KU.tickPlayer(rc, tst, tbuf)
    tap3 = (bt in list(TBf.REMOVED), KU.FLY.containsKey(bt))
    check(tap1 == (True, True, 10.0, 200.0) and not tap2 and tap3 == (True, False),
          "R10d (Kunai-Ladder 4): a tap throws a kunai that costs nothing and is removed once it is past kunai.throwRange 20 (not at 14.5): %s %s %s" % (tap1, tap2, tap3))
    # a HOLD on the ground 10 blocks out: the cost, the impact wrapper, the landing job, the teleport (velocity kept), the return record
    kreset()
    bp, spp, fkp = kthrow(KP["Copper"])
    sp1 = KU.STATES.get(cu)
    wrap1 = (sp1 is not None, KImp.class_.isInstance(spp.getImpactConsumer()), spp.getImpactConsumer().inner == fkp, sv(mc, STAM), sv(mc, MANA))
    tpl1, nj1 = kland(bp, spp, (10.5, 64.0, 0.5))
    rt1 = KU.RET.get(cu)
    check(wrap1 == (True, True, True, 5.0, 197.0) and nj1 == 1 and tpl1 is not None and tpl1[0] == 10.8 and tpl1[1:] == (64.0, 0.5, False)
          and rt1 is not None and [round(float(x), 2) for x in list(rt1)[:3]] == [0.5, 64.0, 0.5] and 7900 <= float(rt1[3]) - nowms() <= 8100
          and len(fkp.calls) == 1 and int(KU.PORTS) >= 1,
          "R10d (Kunai-Ladder 4 + 6): a held Copper kunai costs 5 Stamina (6 capped at 5) + 3 Mana at the throw, its impact is watched (the engine's own "
          "consumer still runs); landing on the ground 10 blocks out -> ONE teleport job -> you land there (the scan: body free, ground below), the "
          "velocity KEPT (no fall-damage escape), a return to (0.5, 64, 0.5) open for ret.window 8 s: %s %s %s" % (wrap1, tpl1, None if rt1 is None else list(rt1)))
    # a wall at eye level 5.5 out: land in front of it (the scan stops at the wall) ; a mob at 8: land 1 block + half its width short of it
    kreset()
    AT.GRID = Grid(world_fn([wall6]))
    bw, spw, _f = kthrow(KP["Copper"])
    tpl2, _n = kland(bw, spw, (6.0, 65.6, 0.5))
    AT.GRID = Grid(world_fn())
    kreset()
    bm, spm, _f = kthrow(KP["Copper"])
    n_mob = npc(1640, 8.0, 64.0, 0.5)
    tpl3, _n = kland(bm, spm, (7.6, 65.6, 0.5), hit=n_mob)
    ACfg.K_BEHIND = True
    kreset()
    bm2, spm2, _f = kthrow(KP["Copper"])
    tpl3b, _n = kland(bm2, spm2, (7.6, 65.6, 0.5), hit=n_mob)
    ACfg.K_BEHIND = False
    check(tpl2 is not None and tpl2[0] == 5.7 and tpl3 is not None and 6.0 <= tpl3[0] <= 7.0 and tpl3b is not None and tpl3b[0] > 8.5,
          "R10d (Kunai-Ladder 6): a kunai in a wall at eye level -> you land on the ground in front of the wall (x 5.7, the blink scan); a kunai in a mob "
          "at x 8 -> 1 block (+ half its width) in front of it, never inside; kunai.behindMob on -> behind it: %s %s %s" % (tpl2, tpl3, tpl3b))
    # the void (ground only up to x 3): NO void protection by default (Skyy LOCKED 2026-10-07) -> you land over the void where the kunai was;
    # an admin who sets kunai.floorCheck 12 gets the old last-spot-with-ground (x 3.5); no free spot (a wall in your face): NOTHING spent; out of range: where it left 20
    def kvoid():
        kreset()
        AT.GRID = Grid(world_fn(floor_ok=lambda x, z: x <= 3))
        bv, spv, _f = kthrow(KP["Copper"])
        comp(bv, TCc.getComponentType()).getPosition().set(10.5, 65.6, 0.5)          # still flying over the void when its time runs out
        KU.STATES.get(cu).t0 = nowms() - 2000
        KU.tickPlayer(rc, tst, tbuf)
        for j_ in list(TWd.JOBS):
            j_.run()
        TWd.JOBS.clear()
        _tv = comp(rc, TPc.getComponentType())
        return None if _tv is None else (round(float(_tv.getPosition().x()), 2),)
    floor_def = int(ACfg.K_FLOOR)
    tpl4v = kvoid()
    ACfg.K_FLOOR = 12
    tpl4 = kvoid()
    ACfg.K_FLOOR = floor_def
    check(floor_def == 0 and tpl4v is not None and tpl4v[0] >= 9.5,
          "R10d FIX (Skyy LOCKED 2026-10-07 'dont put any void protection on any traversal'): kunai.floorCheck defaults to 0 and a teleport kunai over "
          "open void lands you over the void where it was (x >= 9.5, not shortened): floorCheck %s, landed %s" % (floor_def, tpl4v))
    kreset()
    AT.GRID = Grid(world_fn([wall1]))
    bn, spn_, _f = kthrow(KP["Copper"])
    tpl5, _n = kland(bn, spn_, (1.05, 65.6, 0.5))
    nom5 = (sv(mc, STAM), sv(mc, MANA), str(KU.LAST_WHY))
    AT.GRID = Grid(world_fn())
    kreset()
    bo, spo, _f = kthrow(KP["Copper"])
    comp(bo, TCc.getComponentType()).getPosition().set(25.0, 65.6, 0.5)
    KU.tickPlayer(rc, tst, tbuf)
    jo = list(TWd.JOBS)
    TWd.JOBS.clear()
    for j_ in jo:
        j_.run()
    tpo = comp(rc, TPc.getComponentType())
    out6 = (len(jo), bo in list(TBf.REMOVED), None if tpo is None else round(float(tpo.getPosition().x()), 2))
    check(tpl4 is not None and tpl4[0] == 3.5 and tpl5 is None and nom5 == (10.0, 200.0, "no safe spot - refunded") and out6[0] == 1 and out6[1]
          and out6[2] is not None and 20.0 <= out6[2] <= 21.5,
          "R10d (Kunai-Ladder 6): with an admin kunai.floorCheck 12 (default 0) over open void you land at the last spot with ground (x 3.5); a teleport that cannot move you is refunded in full "
          "(Stamina + Mana back); a kunai past kunai.range 20 lands you where it left the range (the kunai is removed): %s %s %s %s" % (tpl4, tpl5, nom5, out6))
    # players: a stranger with PvP off = no teleport, refunded; a party member = fine; PvP on = fine; kunai.pvp never = never
    def kplayer(target, pvp=False, rule="world"):
        kreset()
        wcfg.setPvpEnabled(pvp)
        ACfg.K_PVP = rule
        b_, s_, _f2 = kthrow(KP["Copper"])
        t_, n_ = kland(b_, s_, (4.2, 65.6, 1.0), hit=target)
        wcfg.setPvpEnabled(False)
        ACfg.K_PVP = "world"
        return t_ is not None, sv(mc, STAM), sv(mc, MANA)
    pv = [kplayer(rs), kplayer(rp), kplayer(rs, pvp=True), kplayer(rs, pvp=True, rule="never")]
    check(pv == [(False, 10.0, 200.0), (True, 5.0, 197.0), (True, 5.0, 197.0), (False, 10.0, 200.0)],
          "R10d (Skyy Q8: next to players only where PvP is on): a kunai in a stranger with PvP off = no teleport, refunded; a party member always; a "
          "stranger with PvP on = yes; kunai.pvp never = never: %s" % pv)
    # a locked arena (arena:fn:blocks TRUE) = refunded; the hand changes mid-flight / a newer kunai = cancelled + refunded; flight time = lands
    @JImplements("java.util.function.Function")
    class ArenaYes:
        @JOverride
        def apply(self, o): return JClass("java.lang.Boolean").TRUE
    kreset()
    br.put("arena:fn:blocks", ArenaYes())
    ba, spa, _f = kthrow(KP["Copper"])
    tpa, _n = kland(ba, spa, (10.5, 64.0, 0.5))
    ar1 = (tpa is None, sv(mc, STAM), sv(mc, MANA))
    br.remove("arena:fn:blocks")
    kreset()
    bh, sph, _f = kthrow(KP["Copper"])
    LP.HAND.put(cu, "Weapon_Sword_Iron")
    KU.tickPlayer(rc, tst, tbuf)
    hc1 = (KU.STATES.get(cu) is None, bh in list(TBf.REMOVED), sv(mc, STAM), sv(mc, MANA), len(list(TWd.JOBS)))
    LP.HAND.put(cu, "Weapon_Kunai_Copper")
    kreset()
    bx1, spx1, _f = kthrow(KP["Copper"])
    bx2, spx2, _f = kthrow(KP["Copper"])
    nw1 = (bx1 in list(TBf.REMOVED), KU.STATES.get(cu) is not None and KU.STATES.get(cu).proj == bx2, sv(mc, STAM), sv(mc, MANA))
    kreset()
    bf, spf, _f = kthrow(KP["Copper"])
    comp(bf, TCc.getComponentType()).getPosition().set(7.0, 65.6, 0.5)
    KU.STATES.get(cu).t0 = nowms() - 2000
    KU.tickPlayer(rc, tst, tbuf)
    ft1 = (len(list(TWd.JOBS)), bf in list(TBf.REMOVED))
    check(ar1 == (True, 10.0, 200.0) and hc1 == (True, True, 10.0, 200.0, 0) and nw1 == (True, True, 5.0, 197.0) and ft1 == (1, True),
          "R10d (Kunai-Ladder 3 + 6): a locked arena (arena:fn:blocks) = no teleport, refunded; the kunai leaving your hand mid-flight = cancelled, the "
          "kunai removed, refunded; a newer teleport kunai cancels the older (refunded, one cost); past kunai.flightTtl 1.5 s you land where it is: %s %s %s %s" % (
              ar1, hc1, nw1, ft1))
    # cooldown / the spam net / combat = a NORMAL throw (no cost); too little Stamina = NO throw; the class lock = no throw
    kreset()
    KU.LASTPORT.put(cu, JClass("java.lang.Long")(nowms()))
    bc1, _s, _f = kthrow(KP["Copper"])
    cd1 = (KU.FLY.containsKey(bc1), KU.STATES.get(cu) is None, sv(mc, STAM), "cooldown" in str(KU.LAST_WHY))
    kreset()
    ACfg.K_MAXMIN = 1
    KU.mark(cu, nowms())
    KU.LASTPORT.clear()
    bc2, _s, _f = kthrow(KP["Copper"])
    cd2 = (KU.FLY.containsKey(bc2), KU.STATES.get(cu) is None, "per-minute" in str(KU.LAST_WHY))
    ACfg.K_MAXMIN = 12
    kreset()
    ACfg.K_NOCOMBAT = True
    KU.fight(tbuf, rc, DMGc(ENTS(n_a), DCSc.PROJECTILE, JFloat(5.0)))
    bc3, _s, _f = kthrow(KP["Copper"])
    cd3 = (KU.FLY.containsKey(bc3), KU.STATES.get(cu) is None, "combat" in str(KU.LAST_WHY))
    ACfg.K_NOCOMBAT = False
    kreset(stam=1.0)
    bc4, _s, _f = kthrow(KP["Copper"])
    cd4 = (bc4 in list(TBf.REMOVED), KU.STATES.get(cu) is None, sv(mc, STAM), sv(mc, MANA))
    kreset()
    br.put("class:fn:allowed", DenyId("Weapon_Kunai_Copper"))
    bc5, _s, _f = kthrow(KP["Copper"])
    cd5 = (bc5 in list(TBf.REMOVED), KU.STATES.get(cu) is None, sv(mc, STAM), str(KU.LAST_WHY))
    br.remove("class:fn:allowed")
    check(cd1 == (True, True, 10.0, True) and cd2 == (True, True, True) and cd3 == (True, True, True) and cd4 == (True, True, 1.0, 200.0)
          and cd5 == (True, True, 10.0, "class lock"),
          "R10d: inside the 6 s cooldown, over kunai.maxPerMinute or (kunai.noCombat on) within 5 s of a hit = a NORMAL throw at no cost; too little "
          "Stamina = no throw at all (spec 4: like a dodge); the class lock = no throw: %s %s %s %s %s" % (cd1, cd2, cd3, cd4, cd5))
    # THE RETURN: within the window back to where you were; the knockback ring on the next tick (enemies only, the dash config); late / blocked
    kreset()
    bq, spq, _f = kthrow(KP["Copper"])
    kland(bq, spq, (10.5, 64.0, 0.5))
    put(rc, TPc.getComponentType(), None)
    put(rc, TCc.getComponentType(), TCc(V3(10.8, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    n_k = npc(1650, 1.5, 64.0, 0.5)
    put(n_k, VELc.getComponentType(), VELc())
    put(rp, TCc.getComponentType(), TCc(V3(0.5, 64.0, 1.5), R3(0.0, 0.0, 0.0)))
    NEARL[:] = [n_k, rp, rc]
    ACfg.K_RDMG = 50
    reset_buf()
    om_, opm_ = launched(KRM["Copper"], 1651, 10.8, 65.5, 0.5)
    AT.added(om_, opm_, int(ADf.pidCode(KRM["Copper"])), tst, tbuf)
    jr = list(TWd.JOBS)
    TWd.JOBS.clear()
    for j_ in jr:
        j_.run()
    tpr = comp(rc, TPc.getComponentType())
    put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    KU.tickPlayer(rc, tst, tbuf)
    kk = last_instr(n_k)
    evk = events()
    kp_ = last_instr(rp)
    ret1 = (int(ADf.pidCode(KRM["Copper"])), om_ in list(TBf.REMOVED), len(jr), None if tpr is None else (round(float(tpr.getPosition().x()), 2), round(float(tpr.getPosition().y()), 2)),
            KU.RET.get(cu) is None, kk[0] if kk else None, kk[2] if kk else None, [(e_[0], e_[1]) for e_ in evk])
    ACfg.K_RDMG = 0
    check(ret1[:6] == (9001, True, 1, (0.5, 64.0), True, (10.0, 4.0, 0.0))          # 9000 + 1 = Copper (index 1 after Crude) and ret1[6] == (0.97, 0.94, 5.0, "Exp") and ret1[7] == [(1650, 3.5)]
          and (kp_ is None or kp_[0] != (0.0, 4.0, 10.0)),
          "R10d (Kunai-Ladder 4): a right-click hold launches the return marker (removed at its SPAWN) -> ONE return job -> back to the exact spot you left; "
          "the window is used up; on the next tick the knockback ring pushes the mob 1 block from the spot outward (10 b/s + 4 up, the dagger dash "
          "config), never the party member; ret.damage 50 %% = 3.5 (half a Copper kunai hit 7): %s" % (ret1,))
    # late / nothing to return to / the spot blocked (the nearest free spot within 3 blocks instead)
    kreset()
    KU.RET.put(cu, JArray(JDouble)([0.5, 64.0, 0.5, float(nowms() - 10), 1.0]))
    KU.RETST.put(cu, tst)
    om2, opm2 = launched(KRM["Copper"], 1652, 10.8, 65.5, 0.5)
    AT.added(om2, opm2, 9001, tst, tbuf)
    for j_ in list(TWd.JOBS):
        j_.run()
    late = (comp(rc, TPc.getComponentType()) is None, str(KU.LAST_WHY))
    kreset()
    om3, opm3 = launched(KRM["Copper"], 1653, 10.8, 65.5, 0.5)
    AT.added(om3, opm3, 9001, tst, tbuf)
    for j_ in list(TWd.JOBS):
        j_.run()
    none_ = (comp(rc, TPc.getComponentType()) is None, str(KU.LAST_WHY))
    kreset()
    AT.GRID = Grid(world_fn([lambda x, y, z: x == 0 and z == 0 and 64 <= y <= 66]))
    KU.RET.put(cu, JArray(JDouble)([0.5, 64.0, 0.5, float(nowms() + 5000), 1.0]))
    KU.RETST.put(cu, tst)
    om4, opm4 = launched(KRM["Copper"], 1654, 10.8, 65.5, 0.5)
    AT.added(om4, opm4, 9001, tst, tbuf)
    for j_ in list(TWd.JOBS):
        j_.run()
    tpb = comp(rc, TPc.getComponentType())
    blk = None if tpb is None else (round(float(tpb.getPosition().x()), 2), round(float(tpb.getPosition().z()), 2))
    AT.GRID = Grid(world_fn())
    check(late == (True, "return: too late") and none_ == (True, "return: nothing to return to") and blk is not None
          and (blk[0] >= 1.0 or blk[1] >= 1.0) and math.hypot(blk[0] - 0.5, blk[1] - 0.5) <= 3.0 + 1e-6,
          "R10d: a return after the window = too late (no move); none open = nothing to return to; a return spot inside a block -> the nearest free "
          "spot within 3 blocks: %s %s %s" % (late, none_, blk))
    # the kunai's hit tune (ArmoryTuneSys: a ProjectileConfig shot, no ProjectileComponent - the model id) x kunai.dpsShare / 0.8
    kreset()
    bk_, spk_, _f = kthrow(KP["Copper"])
    ACfg.K_SHARE = 1.2
    dku = DMGc(DPS(rc, bk_), DCSc.PROJECTILE, JFloat(7.0))
    TS10.handle(0, None, tst, tbuf, dku)
    btu, _s = bolt(1.0, 65.6, 0.5, creator=cu, model=G_BOLT)
    dgr = DMGc(DPS(rc, btu), DCSc.PROJECTILE, JFloat(7.0))
    TS10.handle(0, None, tst, tbuf, dgr)
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    check(abs(float(dku.getAmount()) - 10.5) < 1e-3 and float(dgr.getAmount()) == 7.0,
          "R10d (Kunai-Ladder 9 kunai.dpsShare): a kunai hit x 1.2 / 0.8 (7 -> 10.5) through ArmoryTuneSys (by the kunai's model id); the grapple bolt "
          "untouched: %s %s" % (float(dku.getAmount()), float(dgr.getAmount())))
    tt10 = calls_of(PKG + "TravTick", "tick")
    gb10 = calls_of(PKG + "GrappleBoltSys", "onEntityAdded")
    gf10 = calls_of(PKG + "GrappleFallSys", "handle")
    check("onShot" in gb10 and "kunaiModel" in gb10 and tt10.count("tickPlayer") == 4 and "fallSafe" in gf10 and gf10.count("fallSafe") == 2,
          "R10d (wiring, bytecode): GrappleBoltSys hands our kunai models to Kunai.onShot; TravTick ticks Levitate + Kunai; GrappleFallSys asks Levitate too")
    print("R10d. kunai: tap range, hold cost + impact + teleport (ground, wall, mob, void, range, flight time), refunds, PvP / arena / hand / newer, "
          "normal throws, return + knockback + damage, late / none / blocked, tune")

    # --- R10e. THE ROWS: defaults, the loader clamps, the bridge texts, the default file lines, SkyyClasses 0.1.13's class rules
    Rows10 = JClass(PKG + "CfgRows")
    k10 = [str(k) for k in Rows10.KEYS]
    d10 = dict(zip(k10, [str(d) for d in Rows10.DEFS]))
    want10 = {"part.book": "true", "book.k": "0.4", "book.range": "20", "book.edgeFalloff": "0", "lev.safeAfter": "3", "lev.crouchLands": "true",
              "lev.riseSpeed": "10", "lev.floatFall": "6", "part.kunai": "true", "kunai.dpsShare": "0.8", "kunai.throwRange": "20", "kunai.flightTtl": "1.5",
              "kunai.floorCheck": "0", "kunai.behindMob": "false", "kunai.noArena": "true", "kunai.noCombat": "false", "kunai.pvp": "world",
              "kunai.maxPerMinute": "12", "ret.force": "1", "ret.damage": "0"}
    bad10 = dict((k_, (d10.get(k_), v_)) for k_, v_ in want10.items() if d10.get(k_) != v_)
    dtxt = str(ACfg.DEF_CFG)
    lines10 = ["book.radius.Copper=3", "book.radius.Iron=3.25", "book.targets.Adamantite=6", "lev.height.Copper=8", "lev.height.Onyxium=12",
               "lev.hover.Mithril=5", "lev.drift.Thorium=0.9", "lev.mana.Cobalt=14", "lev.stamina.Adamantite=8", "kunai.range.Crude=20",
               "kunai.cooldown.Crude=7", "kunai.cooldown.Onyxium=3.5", "kunai.stamina.Cobalt=5", "kunai.mana.Iron=3", "ret.window.Thorium=9", "ret.radius.Mithril=4.25"]
    check(not bad10 and all(("\n" + l_ + "\n") in dtxt for l_ in lines10) and "fixed.book.Copper" in k10 and "fixed.kunai.Crude" in k10,
          "R10e: the 20 new rows emit with the spec defaults, the 13 per-metal tables' default entries are in the default file (spec 2 / 3 / 4 tables), "
          "the read-only cost rows exist: %s" % bad10)
    pr10 = Props()
    for k_, v_ in (("book.k", "5"), ("lev.height.Copper", "99"), ("kunai.range.Crude", "0"), ("kunai.pvp", "junk"), ("lev.hover.Iron", "2.5"),
                   ("kunai.cooldown.Nope", "3")):
        pr10.setProperty(k_, v_)
    ACfg.apply(pr10)
    cl10 = (float(ACfg.BOOK_K), float(ACfg.LEV_H[0]), float(ACfg.K_RANGE[0]), str(ACfg.K_PVP), float(ACfg.LEV_S[1]), float(ACfg.K_CD[0]))
    bk10, ku10 = str(br.get("armory:book")), str(br.get("armory:kunai"))
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    check(cl10 == (1.0, 30.0, 5.0, "world", 2.5, 7.0) and bk10.startswith("spellbooks on - Page Burst k 1.0") and "Copper 3b/4 lev 30b" in bk10
          and ku10.startswith("kunai teleport on") and "Crude 5b cd 7s" in ku10,
          "R10e: the loader clamps like the kit (book.k 5 -> 1, lev.height 99 -> 30, kunai.range 0 -> 5, a bad choice -> world, an unknown metal "
          "ignored); armory:book / armory:kunai name the live numbers: %s | %s" % (bk10[:120], ku10[:120]))
    CLJ13 = os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.13.jar")
    own10 = None
    if os.path.isfile(CLJ13):
        ucl13 = JClass("java.net.URLClassLoader")(JArray(JClass("java.net.URL"))([JClass("java.io.File")(CLJ13).toURI().toURL()]), sysl)
        CD13 = JClass("java.lang.Class").forName("com.skyy.classes.ClassDefs", True, ucl13)
        mo13 = CD13.getMethod("ownerOf", JClass("java.lang.String").class_)
        nm13 = [str(x) for x in CD13.getField("NAMES").get(None)]
        own10 = sorted(set(nm13[int(mo13.invoke(None, i_))] for i_ in L16_ITEMS if "Spellbook" in i_)), \
            sorted(set(nm13[int(mo13.invoke(None, i_))] for i_ in L16_ITEMS if "Kunai" in i_))
    check(own10 == (["Mage"], ["Assassin"]),
          "R10e (deploy partner): SkyyClasses 0.1.13's own ClassDefs.ownerOf (loaded from its jar) = every new spellbook a Mage weapon, every kunai an "
          "Assassin weapon: %s" % (own10,))
    print("R10e. rows + clamps + bridge texts + SkyyClasses 0.1.13 owners %s" % (own10,))

    # --- R10f. vs the 0.1.5 jar: new files = exactly the 0.1.6 set, every other non-class file byte-identical (the lang only grows), the classes
    OLD15 = os.path.join(HERE, "SkyyArmory-0.1.5.jar")
    if not os.path.isfile(OLD15):
        print("R10f. NOTE no SkyyArmory-0.1.5.jar here - the old-vs-new file compare is skipped")
    else:
        with zipfile.ZipFile(OLD15) as oz_:
            on_ = oz_.namelist()
            new_ = sorted(set(JN) - set(on_))
            gone_ = sorted(set(on_) - set(JN))
            l16f = sorted(set(list(L16_ITEMS.values()) + list(L16_INTS.values()) + list(L16_ROOTS.values()) + list(L16_PRJ.values())
                              + list(L16_MODELS.values()) + list(L16_PCFG.values()) + L16_PNG
                              + [n_ for n_ in JN if n_.startswith("Common/Items/Weapons/Spellbook/") and n_.endswith(".blockymodel")]))
            newcls = sorted(n_ for n_ in new_ if n_.endswith(".class"))
            diff_ = [n_ for n_ in on_ if n_ in JSET and not n_.endswith(".class") and n_ not in ("manifest.json", "Server/Languages/en-US/server.lang")
                     and oz_.read(n_) != JZ.read(n_)]
            lang_ok = JZ.read("Server/Languages/en-US/server.lang").startswith(oz_.read("Server/Languages/en-US/server.lang"))
            ccl = sorted(n_ for n_ in on_ if n_.endswith(".class") and n_ in JSET and oz_.read(n_) != JZ.read(n_))
        check(sorted(n_ for n_ in new_ if not n_.endswith(".class")) == l16f and newcls == sorted("com/skyy/armory/%s.class" % c_ for c_ in
              ("LevState", "Levitate", "KunaiState", "KunaiImpact", "KunaiJob", "Kunai")) and not gone_ and not diff_ and lang_ok,
              "R10f: vs SkyyArmory-0.1.5.jar - the new files are exactly the %d spellbook / kunai files + the 6 new classes, none gone, every other "
              "non-class file byte-identical, the lang file only grows: %s %s %s" % (len(l16f), [n_ for n_ in new_ if n_ not in l16f][:4], gone_[:3], diff_[:3]))
        print("R10f. vs 0.1.5: +%d files (+6 classes), %d classes changed: %s" % (len(l16f), len(ccl), ", ".join(c_.split("/")[-1][:-6] for c_ in ccl)))
    # FIX (critic 3): the tooltips show the Stamina the player PAYS (trav.staminaCap 5 applied), never the uncapped 6-9
    lang16 = JZ.read("Server/Languages/en-US/server.lang").decode("utf8")
    ltip = dict((l_.split(" = ", 1)[0].strip(), l_.split(" = ", 1)[1]) for l_ in lang16.splitlines() if " = " in l_ and (".Weapon_Spellbook_" in l_ or ".Weapon_Kunai_" in l_))
    tipbad = [k_ for k_, v_ in ltip.items() if k_.endswith(".description") and any((" %d Stamina" % n_) in v_ for n_ in (6, 7, 8, 9))]
    check(not tipbad and "Hold: Levitate, 10 Mana + 5 Stamina." in ltip.get("items.Weapon_Spellbook_Mithril.description", "")
          and all(("Hold: Levitate, 10 Mana + 5 Stamina." in ltip.get("items.Weapon_Spellbook_%s.description" % m_, "")) for m_ in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"))
          and "Hold: Levitate, 10 Mana + 5 Stamina." in ltip.get("items.Weapon_Spellbook_Copper.description", "")
          and "5 Stamina + 3 Mana" in ltip.get("items.Weapon_Kunai_Crude.description", "")
          and "5 Stamina + 2 Mana" in ltip.get("items.Weapon_Kunai_Onyxium.description", ""),
          "R10f FIX: spellbook + kunai tooltips name the capped Stamina (trav.staminaCap 5): every book 10 Mana + 5 Stamina (fix2: Mana = 2 x the Stamina paid), Crude kunai "
          "5 Stamina + 3 Mana, no description says 6-9 Stamina: %s" % tipbad)
    NEARL[:] = []
    LV.STATES.clear()
    LV.SAFE.clear()
    KU.STATES.clear()
    KU.RET.clear()
    KU.RETST.clear()
    KU.FLY.clear()
    KU.FLYU.clear()
    KU.KNOCK.clear()
    print("R10. 0.1.6 spellbooks + kunai: every path executed")
'''
hrep('''    LP.HAND = None
    LP.LOOK = None
    LP.STATES.clear()
    TW.ALL.clear()
    AT.NEAR = None
    AT.GRID = None
    br.remove("party:fn:members")
    # ---------------- L2.''', R10 + '''    LP.HAND = None
    LP.LOOK = None
    LP.STATES.clear()
    TW.ALL.clear()
    AT.NEAR = None
    AT.GRID = None
    br.remove("party:fn:members")
    # ---------------- L2.''')

tout = ts.replace(LF, TNL)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(tout)
print("wrote %s (%d lines)" % (os.path.relpath(TDST, ROOT), tout.count(TNL) + 1))
