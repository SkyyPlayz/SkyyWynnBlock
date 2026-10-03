"""SkyyArmory 0.1 - build script (javassist via jpype). NEW MOD: research/SkyyArmory-Spec.md (critic + editor checked) + its section 15
"Staffs, Mana pools and heal caps (2026-10-03)" (wins over older sections), with Skyy's LOCKED answers (OPEN-QUESTIONS.md Q&A 2026-10-02 /
2026-10-03): wand art style B for every metal, tap = blue smaller 3x-speed quick shot at 1/5 Mana and 1/5 damage, hold = charged shot,
costs Wood 5/1, Copper 10/2, Iron 15/3, Thorium 25/5, Cobalt 40/8, Adamantite 60/12, Mithril + Onyxium 85/17 (damage = 1.25 x cost
multiple - 0.25), a Wood Wand tap with too little Mana = the no-Mana click, Onyxium wand recipe = the MITHRIL shortbow recipe with ONYXIUM
bars, Mage staffs get their Mana / damage ladder WITH the wands (this round).
Run:   python SkyyArmory/build_skyyarmory_0.1.py      -> SkyyArmory/SkyyArmory-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the whole set once it is pinned)
Test:  python SkyyArmory/test_skyyarmory_0.1.py       (bare JVM, -Xverify:all; scratch under tools/dev/scratch/armory01/)

OPEN QUESTIONS FOR SKYY (spec 15.7) - this build ships the recommended defaults; each answer is ONE constant below:
  S1 STAFF_BASE = 50       staffs cost 2x the wand's Mana and hit 2x (same damage per Mana as wands)   [25 = keep the vanilla 25 orb]
  S2 STAFF_TAP = "quick"   a staff tap is the quick shot like the wands                                [ "spear" = keep the free swing]
  S3 ONYX_STAFF_RECIPE = True  the Onyxium staff gets the Onyxium wand's recipe                       [False = no recipe]
  S4 (Mage +10 max Mana per Sorcery level) and S5 (heal caps) are SkyySkills 0.4.15 / SkyyClasses 0.1.11 rows; SkyyArmory only reads
     / publishes what they need (the Mana check reads mana.classPerLevel; armory:fn:info + armory:quick feed the heal caps).
  S6 / S7 (the other staffs and wands, regen by max Mana): later - nothing here.

WHAT IT SHIPS (all generated from Assets.zip at build time - no vanilla file is in git; PROJECT-RULES 2)
  WANDS (Priest, spec 1-5): 7 NEW items Weapon_Wand_<Copper .. Onyxium> = the Wooden Earth Wand model with a style-B texture + a real
    rendered icon (tools/skyyart.py), Quality / ItemLevel of that metal's vanilla sword, the metal's shortbow recipe embedded (Weapon
    Bench > Bow tab; Onyxium = Mithril's with Onyxium bars), interactions Primary + Secondary = SkyyArmory_Wand_Primary_<M>:
      Charging (vanilla Wand_Primary values) -> key 0 (tap)  = SkyyArmory_Wand_Quick_<M>: StatsCondition Mana Q (RunTime 0.1) ->
                                                               Parallel [ChangeStat -Q, LaunchProjectile SkyyArmory_QuickOrb_<M>, sound]
                                                key 0.35 (hold) = SkyyArmory_Wand_Cast_<M>: StatsCondition Mana C (0.167) ->
                                                               Parallel [ChangeStat -C, LaunchProjectile SkyyArmory_Orb_<M>, sound]
      too little Mana = SkyyArmory_Wand_Fail (the vanilla no-ammo click, nothing spent). Never a Replace / InteractionVars: the check that
      runs is the one the Charging step names (the SkyySkills 0.4.9 lesson).
  WOOD WAND TAP (spec 2.4, WOOD_QUICK): the vanilla INTERACTION Wand_Primary is overridden with ONE change - Next "0" (the free sword
    swing) -> SkyyArmory_Wand_Quick_Wood (1 Mana, SkyyArmory_QuickOrb_Wood 5 damage); "0.35" stays Wand_Cast_Left_Charged, so the hold
    keeps SkyySkills' 5 / 5. Reaches all three users of Wand_Primary: Weapon_Wand_Wood, _Wood_Rotten, _Tribal (SkyySkills' item overrides
    keep "Primary": "Wand_Primary"; checked against the pinned SkyySkills jar).
  STAFFS (Mage, spec 15.2 - 15.3): the 8 ladder staffs Weapon_Staff_<Wood .. Onyxium> move from SkyySkills to SkyyArmory (the HANDOVER:
    SkyySkills 0.4.15 stops shipping them; deploy + roll back TOGETHER). Each override = the vanilla file with Primary / Secondary =
    SkyyArmory_Staff_Primary_<M> and no InteractionVars (Onyxium also gets the Onyxium wand's recipe); nothing else changes. Chain =
    the wand's with the vanilla staff numbers: Charging (vanilla Staff_Primary values) key 0 -> quick (StatsCondition Q, RunTime 0.31),
    key 1 (the 1.0 s hold) -> charged (StatsCondition C, 0.167 -> Parallel [Stamina -5, StaminaRegenDelay Set -1.5, Mana -C, launch,
    sound]). Mana = 2 x the wand's; damage = STAFF_BASE x the same multiple (staff orbs SkyyArmory_StaffOrb_<M>, quick
    SkyyArmory_StaffQuickOrb_<M>). Staff_Primary (24 users) is never touched. SkyyGear's 7 staff recipes stay SkyyGear's.
  PROJECTILES: fully resolved (no Parent, so they decode and check alone): charged = the vanilla Skeleton_Mage_Corruption_Orb fields with
    Damage = round(25 x mult) (wands) / round(STAFF_BASE x mult) (staffs); quick = 3x MuzzleVelocity (90, TerminalVelocity 150), the blue
    look, Damage = round(5 x mult) / round(STAFF_BASE / 5 x mult). The Wood wand's charged shot stays the shared vanilla orb.
  QUICK LOOK (QUICK_LOOK "recolor"): model asset SkyyArmory_QuickOrb (a copy of the orb's model asset: the same hitbox +-0.1) with a blue
    Fireball texture (skyyart recolor of SkeletonMage.png onto the vanilla Iceball colours), blue copies of the GreenOrb particle systems
    + spawners and of the SkeletonMage trail. "ice" = all-vanilla Iceball look (one constant). SMALLER: ArmorySpawnSys puts an
    EntityScaleComponent (quick.size %, default 60) on every spawned quick orb (QUICK_SIZE_MODE "scale"); "model" = a build-time smaller
    Fireball copy instead (no Java, size fixed).
  JAVA (no commands, no pages, no saved data beyond the config file - no migrations):
    ArmoryTuneSys  DamageEventSystem, Filter group BEFORE ArmorDamageReduction (GearHitSys' slot): hits whose Damage$ProjectileSource
                   projectile has one of our asset names x tune % (and quick hits x quick.damage / 20). 100% / 20 = untouched.
    ArmorySpawnSys HolderSystem on ProjectileComponent (AddReason.SPAWN only, our quick ids only): the size + the speed row.
                   FINDING (bytecode, corrects spec 2.3): ProjectileComponent.shoot -> SimplePhysicsProvider.setVelocity writes the launch
                   velocity into forceProviderStandardState.nextTickVelocity (MAX sentinel = unset; updateVelocity copies it into the
                   velocity on the first physics tick), NOT into getVelocity()'s vector (still 0 when the entity is added). So the speed row
                   scales nextTickVelocity (read by reflection; a protected engine field, the SkyySkills liveCheck pattern). At the
                   default 3x it does nothing - the asset's 90 holds.
                   FIX ROUND (review: spec risk R17 is live and worse than vanilla - a Wood-wand tap costs 1 Mana per 0.35 s, so a Priest
                   can keep ~170 quick orbs alive at 90 blocks/s for their full 60 s): the REACH row quick.life (default 5 s = 450 blocks)
                   moves a quick orb's DespawnComponent to the world clock's now (TimeResource of the store) + quick.life, never later
                   than the vanilla 60 s that ProjectileComponent.assembleDefaultProjectile sets (asserted from its bytecode). The engine's
                   own DespawnSystem removes it then - the same removal as vanilla's 60 s. Charged orbs keep the vanilla 60 s.
    ArmoryCheck    ~20 s after start: the PACK CHECK (every SkyyArmory item / interaction / projectile + Wand_Primary comes from our pack)
                   + the LIVE READ-BACK (Charging keys, StatsCondition / ChangeStat Mana, launch ids, projectile damage / speed = the
                   tables) -> one INFO or one WARN; the MANA CHECK (each charged shot vs a Priest's / Mage's max Mana at the weapon's
                   first level, read from SkyySkills' rows through config:fn:SkyySkills, incl. 0.4.15's mana.classPerLevel) at start and
                   whenever SkyySkills' or our settings change -> armory:check.
    Bridge keys    armory:wands, armory:staffs (id:charged:quick:mult:chargedDmg:quickDmg,...), armory:fn:info (Object[]{"wand"|"staff",
                   itemId} -> Object[]{Integer charged, Integer quick, Double mult, Integer chargedDmg, Integer quickDmg, Double tunePct,
                   String chargedProjectileId, String quickProjectileId ("" = none)} or null; the Rotten / Tribal wands answer as the Wood
                   wand - charged id = the shared vanilla orb; elements 6 + 7 are the FIX ROUND's: SkyyClasses raises the heal cap only for
                   the wand's OWN shots, not for any projectile launched with a wand in hand), armory:quick (the 16 quick projectile ids),
                   armory:check, gear:loot:add:SkyyArmory (the 7 wand ids; research/Loot-Unid-Spec.md 8), config:def / fn / epoch:SkyyArmory.
  SETTINGS  Server Setup > Armory (tools/skyycfg.py kit 1.1, node skyyarmory.admin), Skyy_SkyyArmory/config.properties: part.tune,
    tune.wand + tune.staff (% per weapon), quick.damage, part.spawn, quick.size, quick.speed, quick.life (fix round: the reach), check.on,
    check.share; READ-ONLY rows show every weapon's fixed numbers (Mana costs, keys and art are client-predicted asset data - fixed in the
    jar, spec 7).

CROSS-MOD CONTRACTS (checked here, re-checked by the harness)
  SkyyGear 0.2.1: "Weapon_" + material word = band, no "skyy" in a gear id, Weapon_Wand_ / Weapon_Staff_ = spells (K = 1, Magical
    Power), GearShotTrack + the charged walk on our projectile ids (charged = launched only from the largest Charging key).
  SkyyClasses: Weapon_Wand_ = Priest, Weapon_Staff_ = Mage.  SkyySkills: SPELL GEN touches only Assets.zip ids (our numbers are final),
    the Wood anchor (Wand_Cast_Left_Charged 5 / Wand_Cast_Cost -5 in the pinned jar), the staff HANDOVER (0.4.15 ships none of the 8).
  SkyyArmory OWNS Wand_Primary, the 7 metal wand ids, the 8 ladder staff item files and every SkyyArmory_* id: a SET jar or pack mod
    shipping one stops this build (other installed mods: NOTE); SkyySkills 0.4.14's 8 staff files are the handover exception.

UNVERIFIED (needs the game): the client drawing the generated textures / icons / blue particle copies (R1 / R2), the client honouring
  EntityScaleComponent on a projectile (R2b; fallback QUICK_SIZE_MODE "model"), the speed + reach hook in a live world (R2c / R17), how
  the tap animation fits (QUICK_ANIM), the lang descriptions in the vanilla tooltip.
DEPLOY: only TOGETHER with SkyySkills 0.4.15 (the staff handover; roll back as a pair - with 0.4.14 both packs ship the 8 staffs, and
  0.4.15 without SkyyArmory leaves the staffs on vanilla files: 50 Mana behind a 10-Mana check) and SkyyClasses 0.1.11 (heal caps; it
  reads armory:fn:info / armory:quick). This build STOPS when tools/deploy_set.py pins SkyyArmory with SkyySkills below 0.4.15 or with
  SkyyClasses below 0.1.11 (fix round); tools/deploy_set.py itself needs the same pair assert (the main session's file). Removing
  SkyyArmory later: metal wands already owned become unknown placeholder items that keep their id, count and metadata (spec R13).

CHECKED 2026-10-03 (re-run before a deploy - the harness is the source of truth, not this text):
  build: 56 engine members probed by exact signature (+ 7 protected fields read only by reflection), 17 classes (7 kit), access audit
    5468 references 0 refused (non-public used: DamageEventSystem.<init> and PluginBase.shutdown from their subclasses), "assembled
    ...SkyyArmory-0.1.jar" (208,675 bytes, 204 assets: 15 items, 117 interactions, 15 roots, 31 projectiles, 11 quick-look files, 15 PNGs,
    lang); clash scan clean on the 25 SET jars + both pack mods (NOTE HyboardsPack3.4, installed but off, ships the 8 staffs).
  python tools/ci/lint.py 0 fails (the 26 warnings are SkyySacks 0.7.12's); lint --perm 0 fails; skyycfg_test PASS; skyyui_test 10060 ok
    + the known stale "base-gated WrapMaxLines"; skyyart.verify in every build.
  SkyyArmory/test_skyyarmory_0.1.py: 398 ok, 0 FAIL - T1-T14, T-live, ST1-ST9, ST-live executed (engine codecs + real asset stores,
    SkyySkills' own spell_casts, SkyyGear 0.2.1's real walk, a real Holder / ProjectileComponent / Damage, the kit, the real setup() twice
    on a live-data copy, the whole SET in one JVM: 26 jars, 1118 classes, -Xverify:all).
  verification builds (--out + --switch): STAFF_BASE=25, STAFF_TAP=spear (92 interactions, 23 projectiles), ONYX_STAFF_RECIPE=False,
    QUICK_LOOK=ice, QUICK_SIZE_MODE=model, WOOD_QUICK=False, WAND_STYLE=A - all assemble.
  mutations: the spec's getVelocity() speed hook -> harness S fails; quick share ignored -> U + K fail (3); a Copper tap spending 3 behind a
    2-Mana check -> the build refuses it, and the same edit made in the jar -> P0 / P2 / R / L fail; the Wood hold redirected -> the build
    refuses it, in the jar -> P2 / P3 / R / L / G fail (10).
FIX ROUND (2026-10-03, review findings; scratch tools/dev/scratch/armoryfix, deleted afterwards):
  build: 64 engine members probed (+ DespawnComponent / TimeResource / Store.getResource and the 60000 ms despawn constant read from
    ProjectileComponent.assembleDefaultProjectile's bytecode), access audit 5523 references 0 refused, "assembled ...SkyyArmory-0.1.jar"
    209,895 bytes (204 assets, 17 classes); every alternative switch (the 7 above) still assembles; --set-file builds: the planned pin bump
    (SkyySkills 0.4.15 + SkyyClasses 0.1.11 + SkyyArmory 0.1) assembles the identical jar (222 entries), SkyyArmory pinned with SkyyClasses
    0.1.10 or with SkyySkills 0.4.14 STOPS.
  harness: + P1 negative controls (18 broken-reference classes), + C (RootInteraction.build of the 15 roots + Wand_Primary + every Parallel
    child root: 12 operations per root, 0 missing; a missing Charging target is caught), + S reach row on a real DespawnComponent + TimeResource,
    + K quick.life, + B the info answer's own projectile ids; P5 / P7 version-aware (pre-pin 0.4.14 / post-pin 0.4.15) + the pair checks.
    Mutants: a Charging key -> a missing interaction = 10 FAIL (P1, P2, P3, R, L, C, G); -> another wand's quick chain = 8 FAIL (C among them).
"""
import sys, os, re, json, zipfile, math, copy, colorsys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.isfile(os.path.join(ROOT, "tools", "skyybuild.py")):      # the project root (also from a scratch copy of this script)
    if os.path.dirname(ROOT) == ROOT:
        raise SystemExit("cannot find the project root (tools/skyybuild.py) above " + HERE)
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import skyycfg as CFG
import skyyart as SA

VERSION = "0.1"
MOD = "SkyyArmory"
NODE = "skyyarmory.admin"
PKG = "com.skyy.armory"

# ================================================================= build switches (spec 1.3, 2.2, 2.3, 2.4, 15.2, 15.7)
WAND_STYLE = "B"                 # LOCKED 2026-10-02 (Skyy: "actually do B"): every metal wand = wood handle + metal head. "A" still builds.
QUICK_LOOK = "recolor"           # "recolor" (blue copies of the vanilla orb look) | "ice" (all-vanilla Iceball look)
QUICK_SIZE_MODE = "scale"        # "scale" (ArmorySpawnSys EntityScaleComponent, live row) | "model" (smaller Fireball copy, fixed)
QUICK_ANIM = "CastLeftCharged"   # wand tap animation: the 20-frame cast vanilla plays on its 0.25 s launch | "CastLeft" (50 frames)
STAFF_QUICK_ANIM = "CastSummonCharged"   # staff tap animation: the 30-frame cast | "CastSummon" (90 frames, too long)
WOOD_QUICK = True                # the Wood / Rotten / Tribal wand tap = the 1-Mana quick shot (Wand_Primary override); False = vanilla
STAFF_BASE = 50                  # S1 (open, recommended 50): the Wood staff's charged damage; 25 = the vanilla orb (half damage per Mana)
STAFF_TAP = "quick"              # S2 (open, recommended "quick"): staff tap = quick shot | "spear" = keep the vanilla free spear swing
ONYX_STAFF_RECIPE = True         # S3 (open, recommended True): Onyxium staff = the Onyxium wand's recipe (Mithril shortbow, Onyxium bars)

# ================================================================= the ONE cost table (spec 4.3 + 15.2; Skyy's numbers + the locked rule)
WANDS = [("Wood", 5), ("Copper", 10), ("Iron", 15), ("Thorium", 25), ("Cobalt", 40), ("Adamantite", 60), ("Mithril", 85), ("Onyxium", 85)]
STAFF_FACTOR = 2                 # a staff shot costs 2x the wand shot of the same metal (vanilla: staff 10 / wand 5)
BASE_ORB = 25                    # the vanilla Skeleton_Mage_Corruption_Orb damage (asserted from Assets.zip below)
QUICK_SHARE = 5                  # quick = 1/5 of the Mana and 1/5 of the damage (Skyy)
SPEED_X = 3                      # quick orb speed = 3 x the charged orb (Skyy)
QUICK_SIZE_DEF = 60              # quick.size default, % of the charged orb (spec 2.3)
QUICK_LIFE_DEF = 5               # quick.life default, seconds (fix round, spec R17): a quick orb that hits nothing vanishes after 5 s
VANILLA_LIFE_MS = 60000          # the vanilla projectile despawn (ProjectileComponent.assembleDefaultProjectile, asserted from its bytecode)
CHECK_SHARE_DEF = 40             # check.share default (spec 7)
BANDS = {"Wood": (1, 13), "Copper": (10, 18), "Iron": (15, 23), "Thorium": (20, 28), "Cobalt": (25, 38), "Adamantite": (35, 43),
         "Mithril": (40, 49), "Onyxium": (40, 49)}       # SkyyGear 0.2 bands (G BANDS); the Mana check reads the live table first
WAND_NAMES = {"Wood": "Wooden Earth Wand"}
STAFF_NAMES = {"Wood": "Wooden Earth Staff"}
WOOD_ALIASES = ["Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal"]   # the other two users of Wand_Primary (same 5 / 1 ladder rung)
ARMORY_OWNED = ["Weapon_Staff_%s" % m for m, _c in WANDS]          # the 8 staff item files handed over from SkyySkills
SKILLS_HANDOVER = "0.4.15"       # the SkyySkills version that stops shipping ARMORY_OWNED (spec 15.3)

# VERIFICATION BUILDS ONLY: --out <folder inside tools/dev/scratch> writes build_classes + the jar there, and only then may --switch NAME=VALUE
# (repeatable) override a switch above - e.g. "--switch STAFF_BASE=25 --switch STAFF_TAP=spear" proves Skyy's other answers build before
# the constant is changed. The real jar (no --out) is always built from the constants.
OUT_DIR = HERE
if "--out" in sys.argv:
    OUT_DIR = os.path.realpath(sys.argv[sys.argv.index("--out") + 1])
    if not (OUT_DIR + os.sep).startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep):
        raise SystemExit("--out must be a folder inside tools/dev/scratch")
    os.makedirs(OUT_DIR, exist_ok=True)
# --set-file <a copy of tools/deploy_set.py inside tools/dev/scratch> (VERIFICATION BUILDS ONLY, with --out): the SET pins are read from it -
# e.g. the planned pin bump (SkyySkills 0.4.15 + SkyyClasses 0.1.11 + SkyyArmory 0.1) or a partial pin that must stop the build
SET_FILE = os.path.join(ROOT, "tools", "deploy_set.py")
if "--set-file" in sys.argv:
    if OUT_DIR == HERE:
        raise SystemExit("--set-file needs --out <scratch folder> (the real jar is checked against tools/deploy_set.py only)")
    SET_FILE = os.path.realpath(sys.argv[sys.argv.index("--set-file") + 1])
    if not (SET_FILE + os.sep).startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep):
        raise SystemExit("--set-file must be a file inside tools/dev/scratch")
    print("VERIFICATION BUILD: SET pins read from %s" % SET_FILE)
SWITCHES = ("WAND_STYLE", "QUICK_LOOK", "QUICK_SIZE_MODE", "QUICK_ANIM", "STAFF_QUICK_ANIM", "WOOD_QUICK", "STAFF_BASE", "STAFF_TAP", "ONYX_STAFF_RECIPE")
for _i, _a in enumerate(sys.argv):
    if _a == "--switch":
        if OUT_DIR == HERE:
            raise SystemExit("--switch needs --out <scratch folder> (the real jar is built from the constants only)")
        _k, _v = sys.argv[_i + 1].split("=", 1)
        if _k not in SWITCHES:
            raise SystemExit("--switch: unknown switch %s (one of %s)" % (_k, ", ".join(SWITCHES)))
        globals()[_k] = (_v == "True") if _v in ("True", "False") else (int(_v) if _v.isdigit() else _v)
        print("VERIFICATION BUILD: %s = %r" % (_k, globals()[_k]))
assert WAND_STYLE in SA.WAND_STYLES and QUICK_LOOK in ("recolor", "ice") and QUICK_SIZE_MODE in ("scale", "model")
assert QUICK_ANIM in ("CastLeftCharged", "CastLeft") and STAFF_QUICK_ANIM in ("CastSummonCharged", "CastSummon")
assert STAFF_BASE in (25, 50) and STAFF_TAP in ("quick", "spear") and isinstance(WOOD_QUICK, bool) and isinstance(ONYX_STAFF_RECIPE, bool)


def rhu(x):
    """round half up from the exact value (Python's round() is banker's rounding)"""
    return int(math.floor(x + 0.5 + 1e-9))


def mult_of(c, c0):
    """Skyy's rule: damage multiple = 1.25 x cost multiple - 0.25"""
    return 1.25 * (c / float(c0)) - 0.25


W0 = WANDS[0][1]
WT = []      # (metal, charged C, quick Q, mult, charged damage, quick damage)
for _m, _c in WANDS:
    assert _c % QUICK_SHARE == 0, "%s: the charged cost must divide by %d" % (_m, QUICK_SHARE)
    _k = mult_of(_c, W0)
    WT.append((_m, _c, _c // QUICK_SHARE, _k, rhu(BASE_ORB * _k), rhu(BASE_ORB / float(QUICK_SHARE) * _k)))
S0 = W0 * STAFF_FACTOR
ST = []
for _m, _c in WANDS:
    _sc = _c * STAFF_FACTOR
    _k = mult_of(_sc, S0)
    ST.append((_m, _sc, _sc // QUICK_SHARE, _k, rhu(STAFF_BASE * _k), rhu(STAFF_BASE / float(QUICK_SHARE) * _k)))
METALS = [w[0] for w in WT]
NEW_METALS = METALS[1:]
# Skyy's locked rungs + the rule (OPEN-QUESTIONS LOCKED 2026-10-02): Wood 5 / 1, Copper 10 / 2 (~2.25x), Iron 15 / 3 (3.5x)
assert [(w[0], w[1], w[2]) for w in WT[:3]] == [("Wood", 5, 1), ("Copper", 10, 2), ("Iron", 15, 3)] and WT[1][3] == 2.25 and WT[2][3] == 3.5
assert [w[1] for w in WT] == [5, 10, 15, 25, 40, 60, 85, 85], "the cost ladder changed - Skyy's answer is the table above"
_steps = [WT[i + 1][1] - WT[i][1] for i in range(len(WT) - 2)]
assert _steps == sorted(_steps) and _steps[:2] == [5, 5], "the cost steps never shrink before Mithril: %s" % _steps
assert [(w[4], w[5]) for w in WT] == [(25, 5), (56, 11), (88, 18), (150, 30), (244, 49), (369, 74), (525, 105), (525, 105)], WT
assert all(abs(w[5] - w[4] / 5.0) <= 1.0 for w in WT), "quick damage within one point of 1/5"
assert [(s[1], s[2]) for s in ST] == [(10, 2), (20, 4), (30, 6), (50, 10), (80, 16), (120, 24), (170, 34), (170, 34)]
assert [s[3] for s in ST] == [w[3] for w in WT], "staffs use the wand's multiples"
if STAFF_BASE == 50:
    assert [(s[4], s[5]) for s in ST] == [(50, 10), (113, 23), (175, 35), (300, 60), (488, 98), (738, 148), (1050, 210), (1050, 210)], ST
else:
    assert [(s[4], s[5]) for s in ST] == [(w[4], w[5]) for w in WT], ST
print("ladder (metal: wand C/Q x mult = dmg charged/quick | staff C/Q = dmg): " + "; ".join(
    "%s %d/%d x%s = %d/%d | %d/%d = %d/%d" % (w[0], w[1], w[2], ("%.2f" % w[3]).rstrip("0").rstrip("."), w[4], w[5], s[1], s[2], s[4], s[5])
    for w, s in zip(WT, ST)))

# ================================================================= asset ids (spec 2.2, 2.3, 15.2) - every new id starts with SkyyArmory_
WAND_IDS = ["Weapon_Wand_%s" % m for m in METALS]            # [0] = the vanilla Wood wand (we own only its tap)
STAFF_IDS = ["Weapon_Staff_%s" % m for m in METALS]
ID_WROOT = "SkyyArmory_Wand_Primary_%s"
ID_WCAST, ID_WCOST, ID_WLAUNCH = "SkyyArmory_Wand_Cast_%s", "SkyyArmory_Wand_Cast_Cost_%s", "SkyyArmory_Wand_Cast_Launch_%s"
ID_WQUICK, ID_WQCOST, ID_WQLAUNCH = "SkyyArmory_Wand_Quick_%s", "SkyyArmory_Wand_Quick_Cost_%s", "SkyyArmory_Wand_Quick_Launch_%s"
ID_WCEFF, ID_WQEFF, ID_WFAIL = "SkyyArmory_Wand_Cast_Effect", "SkyyArmory_Wand_Quick_Effect", "SkyyArmory_Wand_Fail"
ID_SROOT = "SkyyArmory_Staff_Primary_%s"
ID_SCAST, ID_SCOST, ID_SLAUNCH = "SkyyArmory_Staff_Cast_%s", "SkyyArmory_Staff_Cast_Cost_%s", "SkyyArmory_Staff_Cast_Launch_%s"
ID_SQUICK, ID_SQCOST, ID_SQLAUNCH = "SkyyArmory_Staff_Quick_%s", "SkyyArmory_Staff_Quick_Cost_%s", "SkyyArmory_Staff_Quick_Launch_%s"
ID_SSTAM, ID_SSTAMD = "SkyyArmory_Staff_Stamina", "SkyyArmory_Staff_Stamina_Delay"
ID_SCEFF, ID_SQEFF, ID_SFAIL = "SkyyArmory_Staff_Cast_Effect", "SkyyArmory_Staff_Quick_Effect", "SkyyArmory_Staff_Fail"
ID_ORB, ID_QORB = "SkyyArmory_Orb_%s", "SkyyArmory_QuickOrb_%s"
ID_SORB, ID_SQORB = "SkyyArmory_StaffOrb_%s", "SkyyArmory_StaffQuickOrb_%s"
VAN_ORB = "Skeleton_Mage_Corruption_Orb"
QMODEL = "SkyyArmory_QuickOrb"
TRAIL_BLUE = "SkyyArmory_Orb_Trail_Blue"
PS_GLOW, PS_IMPACT, PS_HEAD = "SkyyArmory_Orb_Glow_Blue", "SkyyArmory_Orb_Impact_Blue", "SkyyArmory_Orb_Head_Blue"
PSP = {"GreenOrbDust": "SkyyArmory_Orb_Dust_Blue", "GreenOrbSparks": "SkyyArmory_Orb_Sparks_Blue", "GreenOrbSplash": "SkyyArmory_Orb_Splash_Blue",
       "GreenOrbSmoke": "SkyyArmory_Orb_Smoke_Blue", "Void_Sparks_Eyes": "SkyyArmory_Orb_Eyes_Blue"}
PSYS = {"GreenOrbTrail": PS_GLOW, "GreenOrbImpact": PS_IMPACT, "Spectre_Void_Head": PS_HEAD}
BLUE = "#3f8cff"                 # the quick orb's particle tint (spec 2.3)
TEX_QORB = "Items/Projectiles/Fireball_Textures/SkyyArmory_QuickOrb_Blue.png"
MODEL_QORB = "Items/Projectiles/SkyyArmory_QuickOrb.blockymodel"   # QUICK_SIZE_MODE "model" only
TEX_WAND = "Items/Weapons/Wand/SkyyArmory_%s_Texture.png"
ICON_WAND = "Icons/ItemsGenerated/SkyyArmory_Wand_%s.png"
P_WITEM = "Server/Item/Items/Weapon/Wand/Weapon_Wand_%s.json"
P_SITEM = "Server/Item/Items/Weapon/Staff/Weapon_Staff_%s.json"
P_WINT = "Server/Item/Interactions/Weapons/Wand/SkyyArmory/%s.json"
P_SINT = "Server/Item/Interactions/Weapons/Staff/SkyyArmory/%s.json"
P_WROOT = "Server/Item/RootInteractions/Weapons/Wand/SkyyArmory/%s.json"
P_SROOT = "Server/Item/RootInteractions/Weapons/Staff/SkyyArmory/%s.json"
P_WAND_PRIMARY = "Server/Item/Interactions/Weapons/Wand/Wand_Primary.json"   # the ONE vanilla interaction we override
P_PRJ = "Server/Projectiles/Player/SkyyArmory/%s.json"
P_MODEL = "Server/Models/Projectiles/SkyyArmory/%s.json"
P_TRAIL = "Server/Entity/Trails/%s.json"
P_PSYS = "Server/Particles/SkyyArmory/%s.particlesystem"
P_PSPAWN = "Server/Particles/SkyyArmory/Spawners/%s.particlespawner"
P_LANG = "Server/Languages/en-US/server.lang"

# ================================================================= Assets.zip (read-only) + the vanilla shapes this build relies on
SA.verify()                                  # PNG codec + icon renderer vs vanilla icons + every wand recipe source (fails loudly)
AZ = SA.assets()
AZ_NAMES = AZ.namelist()
AZ_SET = set(AZ_NAMES)
_IDX = {}
for _n in AZ_NAMES:
    if not _n.endswith(".json") or not _n.startswith("Server/"):
        continue
    _b = os.path.basename(_n)[:-5]
    for _pre, _kind in (("Server/Item/Items/", "item"), ("Server/Item/Interactions/", "int"), ("Server/Item/RootInteractions/", "root"),
                        ("Server/Projectiles/", "prj"), ("Server/Models/", "model"), ("Server/Entity/Trails/", "trail"),
                        ("Server/Audio/SoundEvents/", "sound"), ("Server/Item/Animations/", "anim"), ("Server/Item/Qualities/", "quality"),
                        ("Server/Item/ResourceTypes/", "rtype"), ("Server/Item/Recipes/", "recipe"), ("Server/Entity/Stats/", "stat"),
                        ("Server/Item/ItemSoundSets/", "iss"), ("Server/Item/Category/", "cat")):
        if _n.startswith(_pre):
            _IDX.setdefault(_kind, {}).setdefault(_b, []).append(_n)
for _n in AZ_NAMES:
    if _n.startswith("Server/Particles/") and _n.endswith((".particlesystem", ".particlespawner")):
        _IDX.setdefault("psys" if _n.endswith(".particlesystem") else "pspawn", {}).setdefault(os.path.basename(_n).rsplit(".", 1)[0], []).append(_n)
for _k in ("item", "int", "root", "prj", "model"):
    _dup = sorted(i for i, ps in _IDX[_k].items() if len(ps) > 1)
    assert not _dup, "Assets.zip has %s ids more than once: %s" % (_k, _dup[:5])


def az_path(kind, aid):
    ps = _IDX.get(kind, {}).get(aid)
    if not ps:
        raise SystemExit("Assets.zip: no %s %r" % (kind, aid))
    return ps[0]


def az_json(path):
    return json.loads(AZ.read(path).decode("utf-8-sig"))


def az_get(kind, aid):
    return az_json(az_path(kind, aid))


def az_has(kind, aid):
    return aid in _IDX.get(kind, {})


def resolve(kind, aid, seen=None):
    """a Parent chain resolved the asset way (child fields win; nested objects of the child replace the parent's)"""
    d = az_get(kind, aid)
    p = d.get("Parent")
    if not p:
        return d
    seen = seen or set()
    assert p not in seen, "Parent loop at %s" % p
    seen.add(p)
    base = dict(resolve(kind, p, seen))
    for k, v in d.items():
        if k != "Parent":
            base[k] = v
    return base


# ---- the vanilla Wood wand (model, icon view, parts copied into every metal wand)
VW = az_get("item", "Weapon_Wand_Wood")
assert VW.get("Interactions") == {"Primary": "Wand_Primary", "Secondary": "Wand_Primary"}, VW.get("Interactions")
assert VW["Model"] == "Items/Weapons/Wand/Wood.blockymodel" and VW["Texture"] == "Items/Weapons/Wand/Wood_Texture.png"
assert VW["PlayerAnimationsId"] == "Wand" and VW["Tags"] == {"Type": ["Weapon"], "Family": ["Wand"]} and VW["Weapon"] == {}
assert VW["Particles"] == [{"SystemId": "Wood_Wand", "TargetNodeName": "Handle"}] and VW["ItemSoundSetId"] == "ISS_Weapons_Wand"
assert "MaxStack" not in VW and "MaxDurability" not in VW, "the Wood wand gained a stack size / durability - check the wand copy"
# ---- the vanilla wand chain (spec 2.1) - the build stops if Hytale changes it
VWP = az_get("int", "Wand_Primary")
assert VWP.get("Type") == "Charging" and sorted(VWP["Next"]) == ["0", "0.35"], VWP
assert VWP["Next"]["0"] == {"Type": "Chaining", "ChainingAllowance": 1.25, "Next": ["Sword_Swing_Left_Fast", "Sword_Swing_Right_Fast"]}, VWP
assert VWP["Next"]["0.35"] == "Wand_Cast_Left_Charged" and VWP["Effects"] == {"ItemAnimationId": "CastLeftCharging"}
assert VWP["AllowIndefiniteHold"] is True and VWP["HorizontalSpeedMultiplier"] == 0.75 and set(VWP) == {
    "Type", "Effects", "AllowIndefiniteHold", "HorizontalSpeedMultiplier", "Next"}, sorted(VWP)
assert az_get("root", "Wand_Primary") == {"Interactions": ["Wand_Primary"]}
VWC = az_get("int", "Wand_Cast_Left_Charged")
assert VWC["Type"] == "StatsCondition" and VWC["RunTime"] == 0.167 and VWC["Next"]["Type"] == "Parallel" and len(VWC["Next"]["Interactions"]) == 3
VWL = az_get("int", "Wand_Cast_Launch")
assert VWL == {"Type": "LaunchProjectile", "RunTime": 0.25, "Effects": {"ItemAnimationId": "CastLeftCharged"}, "ProjectileId": VAN_ORB}, VWL
VWE = az_get("int", "Wand_Cast_Effect")
assert VWE["Type"] == "Simple" and VWE["RunTime"] == 0.5 and VWE["Effects"] == {"WorldSoundEventId": "SFX_Staff_Ice_Shoot"}, VWE
VWF = az_get("int", "Wand_Cast_Fail")
assert VWF == {"Type": "Simple", "RunTime": 0.2, "Effects": {"ItemAnimationId": "Interact", "WorldSoundEventId": "SFX_Bow_No_Ammo"}}, VWF
# who uses Wand_Primary (spec 2.4): exactly the 3 wood-tier wands; nothing outside Server/Item names it (no NPC)
_wp_users, _wp_out = [], []
for _n in AZ_NAMES:
    if _n.startswith("Server/") and _n.endswith(".json"):
        _raw = AZ.read(_n)
        if b'"Wand_Primary"' in _raw:
            if _n.startswith("Server/Item/Items/"):
                _wp_users.append(os.path.basename(_n)[:-5])
            elif _n not in (az_path("int", "Wand_Primary"), az_path("root", "Wand_Primary")):
                _wp_out.append(_n)
assert sorted(_wp_users) == sorted(["Weapon_Wand_Wood"] + WOOD_ALIASES) and not _wp_out, (_wp_users, _wp_out)
# ---- the vanilla staff chain (spec 15.1)
VSP = az_get("int", "Staff_Primary")
assert VSP.get("Type") == "Charging" and sorted(VSP["Next"]) == ["0", "1"], VSP
assert VSP["Next"]["0"] == {"Type": "Chaining", "ChainingAllowance": 1.25, "Next": ["Spear_Swing_Left", "Spear_Swing_Right"]}, VSP
assert VSP["Next"]["1"] == "Staff_Cast_Summon_Charged" and VSP["Effects"] == {"ItemAnimationId": "CastSummonCharging"}
assert VSP["AllowIndefiniteHold"] is True and VSP["HorizontalSpeedMultiplier"] == 0.5
VSC = az_get("int", "Staff_Cast_Summon_Charged")
assert VSC["Type"] == "Simple" and VSC["RunTime"] == 0.167 and len(VSC["Next"]["Interactions"]) == 5, "the vanilla staff cast changed"
_stam = VSC["Next"]["Interactions"][0]["Interactions"][0]
_stamd = VSC["Next"]["Interactions"][1]["Interactions"][0]
assert _stam["Var"] == "Staff_Cast_Summon_StaminaCost" and _stam["DefaultValue"]["Interactions"] == [{"Type": "ChangeStat", "StatModifiers": {"Stamina": -5}}]
assert _stamd["Var"] == "Staff_Cast_Summon_StaminaRegenDelay" and _stamd["DefaultValue"]["Interactions"] == [
    {"Type": "ChangeStat", "Behaviour": "Set", "StatModifiers": {"StaminaRegenDelay": -1.5}}]
assert az_get("int", "Staff_Cast_Launch") == {"Type": "LaunchProjectile", "RunTime": 0.25, "Effects": {"ItemAnimationId": "CastSummonCharged"}, "ProjectileId": VAN_ORB}
assert az_get("int", "Staff_Cast_Effect")["Effects"] == {"WorldSoundEventId": "SFX_Staff_Ice_Shoot"} and az_get("int", "Staff_Cast_Effect")["RunTime"] == 0.5
assert az_get("int", "Staff_Cast_Fail") == {"Type": "Simple", "RunTime": 0.2, "Effects": {"ItemAnimationId": "Interact", "WorldSoundEventId": "SFX_Bow_No_Ammo"}}
STAFF_VARS = ["Staff_Cast_Summon_Charged", "Staff_Cast_Summon_Cost", "Staff_Cast_Summon_Launch", "Staff_Cast_Summon_Effect", "Staff_Cast_Summon_Fail",
              "Spear_Swing_Left_Damage", "Spear_Swing_Right_Damage", "Spear_Swing_Left_Effect", "Spear_Swing_Right_Effect"]
VSTAFF = {}
for _m in METALS:
    _d = az_get("item", "Weapon_Staff_" + _m)
    assert "Parent" not in _d and _d.get("Interactions") == {"Primary": "Staff_Primary", "Secondary": "Staff_Primary"}, (_m, _d.get("Interactions"))
    assert sorted(_d.get("InteractionVars", {})) == sorted(STAFF_VARS), (_m, sorted(_d.get("InteractionVars", {})))
    assert "Recipe" not in _d, "vanilla gave the %s staff a recipe - SkyyGear's recipe would be a duplicate" % _m
    VSTAFF[_m] = _d
# ---- the 7 new wand ids and every SkyyArmory_ id are free in Assets.zip (spec 1.1: a vanilla metal wand would be overridden)
for _i in WAND_IDS[1:]:
    assert not az_has("item", _i), "Hytale now has %s - SkyyArmory would override it; Skyy decides first" % _i
assert not [n for n in AZ_NAMES if "SkyyArmory" in n], "Assets.zip holds a SkyyArmory file"
# ---- the vanilla charged orb, resolved (spec 2.3: no Parent in our copies)
VORB = resolve("prj", VAN_ORB)
assert VORB["Damage"] == BASE_ORB and VORB["MuzzleVelocity"] == 30 and VORB["TerminalVelocity"] == 50 and VORB["Gravity"] == 0, VORB
assert VORB["Appearance"] == VAN_ORB and VORB["TimeToLive"] == 3.1 and VORB["HitParticles"] == {"SystemId": "GreenOrbImpact"}, VORB
assert az_get("prj", VAN_ORB).get("Parent") == "Staff_Wood_Rotten_Corruption_Orb"
VORBM = az_get("model", VAN_ORB)
assert VORBM["HitBox"] == {"Max": {"X": 0.1, "Y": 0.1, "Z": 0.1}, "Min": {"X": -0.1, "Y": -0.1, "Z": -0.1}}, VORBM.get("HitBox")
assert VORBM["DefaultAttachments"] == [{"Model": "Items/Projectiles/Fireball.blockymodel", "Texture": "Items/Projectiles/Fireball_Textures/SkeletonMage.png"}]
assert [p["SystemId"] for p in VORBM["Particles"]] == ["GreenOrbTrail", "Spectre_Void_Head"] and [t["TrailId"] for t in VORBM["Trails"]] == ["SkeletonMage", "SkeletonMage"]
# ---- animations, sounds, everything a generated file names
_wanim = az_get("anim", "Wand")["Animations"]
_sanim = az_get("anim", "Staff")["Animations"]
assert all(a in _wanim for a in ("CastLeft", "CastLeftCharging", "CastLeftCharged")), sorted(_wanim)
assert all(a in _sanim for a in ("CastSummon", "CastSummonCharging", "CastSummonCharged")), sorted(_sanim)
for _s in ("SFX_Staff_Ice_Shoot", "SFX_Wand_Ice_Shoot", "SFX_Bow_No_Ammo", "SFX_Skeleton_Mage_Spellbook_Impact"):
    assert az_has("sound", _s), "no sound event %s" % _s
for _st in ("Mana", "Stamina", "StaminaRegenDelay"):
    assert az_has("stat", _st), "no entity stat %s" % _st


# ---- cadence (spec 2.2 / 15.2): the vanilla taps, computed from the JSON (RunTime + Next; Parallel = the longest child; a Selector's
# hit forks do not add; Replace = the item var's value, else its default)
def dur(x, vars_, depth=0):
    assert depth < 60, "cadence: too deep"
    if isinstance(x, str):
        if az_has("int", x):
            return dur(resolve("int", x), vars_, depth + 1)
        if az_has("root", x):
            return dur(az_get("root", x), vars_, depth + 1)
        raise SystemExit("cadence: unknown id %s" % x)
    if isinstance(x, list):
        return sum(dur(e, vars_, depth + 1) for e in x)
    if not isinstance(x, dict):
        return 0.0
    if "Parent" in x and "Type" not in x:
        base = dict(resolve("int", x["Parent"]))
        base.update(dict((k, v) for k, v in x.items() if k != "Parent"))
        x = base
    t = x.get("Type")
    if t is None and "Interactions" in x:
        return dur(x["Interactions"], vars_, depth + 1)
    if t == "Replace":
        v = vars_.get(x["Var"], x.get("DefaultValue"))
        return dur(v, vars_, depth + 1)
    if t == "Parallel":
        return max(dur(e, vars_, depth + 1) for e in x["Interactions"])
    own = float(x.get("RunTime", 0.0))
    nxt = x.get("Next")
    return own + (dur(nxt, vars_, depth + 1) if nxt is not None else 0.0)


VAN_TAP_W = max(dur("Sword_Swing_Left_Fast", VW["InteractionVars"]), dur("Sword_Swing_Right_Fast", VW["InteractionVars"]))
VAN_TAP_S = max(dur("Spear_Swing_Left", VSTAFF["Wood"]["InteractionVars"]), dur("Spear_Swing_Right", VSTAFF["Wood"]["InteractionVars"]))
VAN_CAST_W = dur("Wand_Cast_Left_Charged", VW["InteractionVars"])
VAN_CAST_S = dur("Staff_Cast_Summon_Charged", VSTAFF["Wood"]["InteractionVars"])
assert abs(VAN_TAP_W - 0.346) < 1e-9 and abs(VAN_TAP_S - 0.557) < 1e-9, (VAN_TAP_W, VAN_TAP_S)
assert abs(VAN_CAST_W - 0.667) < 1e-9 and abs(VAN_CAST_S - 0.667) < 1e-9, (VAN_CAST_W, VAN_CAST_S)
RT_WQUICK, RT_SQUICK, RT_LAUNCH, RT_QEFF = 0.1, 0.31, 0.25, 0.25
print("cadence: vanilla wand tap %.3f s, staff tap %.3f s, charged chains %.3f / %.3f s" % (VAN_TAP_W, VAN_TAP_S, VAN_CAST_W, VAN_CAST_S))

# ================================================================= recipes (spec 5.1 + Skyy's Onyxium answer + 15.3)
RECIPE_KEYS = ("Input", "BenchRequirement", "TimeSeconds", "KnowledgeRequired", "OutputQuantity", "RequiredMemoriesLevel")
DROP_BENCH = ("Armory",)     # the developer-only DiagramCrafting bench (SkyyGear 0.2 review finding 5)


def shortbow_recipe(metal):
    r = az_get("item", "Weapon_Shortbow_" + metal).get("Recipe")
    assert isinstance(r, dict), "Weapon_Shortbow_%s has no recipe any more" % metal
    assert set(r) <= set(RECIPE_KEYS), "the %s shortbow recipe has keys this build does not copy: %s" % (metal, sorted(set(r) - set(RECIPE_KEYS)))
    out = json.loads(json.dumps(r))
    if "BenchRequirement" in out:
        out["BenchRequirement"] = [b for b in out["BenchRequirement"] if b.get("Id") not in DROP_BENCH]
    assert any(b.get("Type") == "Crafting" for b in out.get("BenchRequirement") or []), "%s: no Crafting bench left" % metal
    return out


def onyx_recipe():
    r = shortbow_recipe("Mithril")
    n = 0
    for x in r["Input"]:
        if x.get("ItemId") == "Ingredient_Bar_Mithril":
            x["ItemId"] = "Ingredient_Bar_Onyxium"
            n += 1
    assert n == 1, "the Mithril shortbow recipe has %d Mithril bar inputs" % n
    return r


WAND_RECIPES = dict((m, shortbow_recipe(m)) for m in NEW_METALS if m != "Onyxium")
WAND_RECIPES["Onyxium"] = onyx_recipe()
assert az_get("item", "Weapon_Shortbow_Onyxium").get("Recipe") is None, "vanilla gave the Onyxium shortbow a recipe - re-check Skyy's answer"
assert WAND_RECIPES["Onyxium"]["Input"][0] == {"ItemId": "Ingredient_Bar_Onyxium", "Quantity": 6}, WAND_RECIPES["Onyxium"]["Input"]
_vrecipe_ids = set()
for _i, _ps in _IDX["item"].items():
    if isinstance(az_json(_ps[0]).get("Recipe"), dict):
        _vrecipe_ids.add(_i + "_Recipe_Generated_0")
_vrecipe_ids |= set(_IDX.get("recipe", {}))
_salvage_in = set()
for _rn, _ps in _IDX.get("recipe", {}).items():
    for _x in az_json(_ps[0]).get("Input") or []:
        if isinstance(_x, dict) and _x.get("ItemId"):
            _salvage_in.add(_x["ItemId"])
for _m, _r in WAND_RECIPES.items():
    for _x in _r["Input"]:
        assert ("ItemId" in _x) != ("ResourceTypeId" in _x) and int(_x["Quantity"]) > 0, _x
        assert _x.get("ItemId") is None or az_has("item", _x["ItemId"]), "unknown input item %s" % _x
        assert _x.get("ResourceTypeId") is None or az_has("rtype", _x["ResourceTypeId"]), "unknown resource type %s" % _x
for _i in WAND_IDS[1:] + (["Weapon_Staff_Onyxium"] if ONYX_STAFF_RECIPE else []):
    assert _i + "_Recipe_Generated_0" not in _vrecipe_ids and _i not in _salvage_in, _i

# ================================================================= generators
ASSETS = {}          # jar path -> text / bytes
INTS, ROOTS, PRJS, ITEMS = {}, {}, {}, {}   # id -> dict (also the harness's tables)


def jdump(o):
    t = json.dumps(o, indent=2, ensure_ascii=True) + "\n"
    assert json.loads(t) == o
    return t


def put(path, obj):
    assert path not in ASSETS, "two files at " + path
    ASSETS[path] = jdump(obj)


def add_int(path_fmt, iid, obj):
    assert iid not in INTS and not az_has("int", iid) or iid == "Wand_Primary", iid
    INTS[iid] = obj
    put(path_fmt % iid, obj)


def add_root(path_fmt, rid, ints):
    assert rid not in ROOTS and not az_has("root", rid), rid
    obj = {"Interactions": list(ints)}
    ROOTS[rid] = obj
    put(path_fmt % rid, obj)


def inline_root(iid):
    return {"Interactions": [iid]}


def stats_check(mana, runtime, nxt, failed):
    return {"Type": "StatsCondition", "Costs": {"Mana": mana}, "RunTime": runtime,
            "Next": {"Type": "Parallel", "Interactions": [inline_root(i) for i in nxt]}, "Failed": failed}


def change_mana(mana):
    return {"Type": "ChangeStat", "StatModifiers": {"Mana": -mana}}


def launch(pid, anim):
    return {"Type": "LaunchProjectile", "RunTime": RT_LAUNCH, "Effects": {"ItemAnimationId": anim}, "ProjectileId": pid}


# ---- shared wand steps (= vanilla Wand_Cast_Effect / Wand_Cast_Fail, under our own ids so no other mod's override reaches them)
add_int(P_WINT, ID_WCEFF, {"Type": "Simple", "RunTime": VWE["RunTime"], "Effects": dict(VWE["Effects"])})
add_int(P_WINT, ID_WQEFF, {"Type": "Simple", "RunTime": RT_QEFF, "Effects": {"WorldSoundEventId": "SFX_Wand_Ice_Shoot"}})
add_int(P_WINT, ID_WFAIL, {"Type": "Simple", "RunTime": VWF["RunTime"], "Effects": dict(VWF["Effects"])})


def wand_quick(m, q):
    add_int(P_WINT, ID_WQCOST % m, change_mana(q))
    add_int(P_WINT, ID_WQLAUNCH % m, launch(ID_QORB % m, QUICK_ANIM))
    add_int(P_WINT, ID_WQUICK % m, stats_check(q, RT_WQUICK, [ID_WQCOST % m, ID_WQLAUNCH % m, ID_WQEFF], ID_WFAIL))


for _m, _c, _q, _k, _cd, _qd in WT[1:]:
    wand_quick(_m, _q)
    add_int(P_WINT, ID_WCOST % _m, change_mana(_c))
    add_int(P_WINT, ID_WLAUNCH % _m, launch(ID_ORB % _m, VWL["Effects"]["ItemAnimationId"]))
    add_int(P_WINT, ID_WCAST % _m, stats_check(_c, VWC["RunTime"], [ID_WCOST % _m, ID_WLAUNCH % _m, ID_WCEFF], ID_WFAIL))
    _ch = {"Type": "Charging", "Effects": dict(VWP["Effects"]), "AllowIndefiniteHold": VWP["AllowIndefiniteHold"],
           "HorizontalSpeedMultiplier": VWP["HorizontalSpeedMultiplier"], "Next": {"0": ID_WQUICK % _m, "0.35": ID_WCAST % _m}}
    add_int(P_WINT, ID_WROOT % _m, _ch)
    add_root(P_WROOT, ID_WROOT % _m, [ID_WROOT % _m])
if WOOD_QUICK:
    wand_quick("Wood", WT[0][2])
    WP_NEW = json.loads(json.dumps(VWP))
    WP_NEW["Next"]["0"] = ID_WQUICK % "Wood"
    INTS["Wand_Primary"] = WP_NEW
    put(P_WAND_PRIMARY, WP_NEW)
    # the override differs from vanilla in Next["0"] only (the SkyySkills _spell_diff pattern)
    _a, _b = json.loads(json.dumps(VWP)), json.loads(json.dumps(WP_NEW))
    _a["Next"].pop("0"), _b["Next"].pop("0")
    assert _a == _b and list(VWP) == list(WP_NEW), "the Wand_Primary override may change Next['0'] only"

# ---- staffs (spec 15.2)
add_int(P_SINT, ID_SSTAM, {"Type": "ChangeStat", "StatModifiers": {"Stamina": -5}})
add_int(P_SINT, ID_SSTAMD, {"Type": "ChangeStat", "Behaviour": "Set", "StatModifiers": {"StaminaRegenDelay": -1.5}})
add_int(P_SINT, ID_SCEFF, {"Type": "Simple", "RunTime": 0.5, "Effects": {"WorldSoundEventId": "SFX_Staff_Ice_Shoot"}})
add_int(P_SINT, ID_SFAIL, {"Type": "Simple", "RunTime": 0.2, "Effects": {"ItemAnimationId": "Interact", "WorldSoundEventId": "SFX_Bow_No_Ammo"}})
if STAFF_TAP == "quick":
    add_int(P_SINT, ID_SQEFF, {"Type": "Simple", "RunTime": RT_QEFF, "Effects": {"WorldSoundEventId": "SFX_Wand_Ice_Shoot"}})
for _m, _c, _q, _k, _cd, _qd in ST:
    if STAFF_TAP == "quick":
        add_int(P_SINT, ID_SQCOST % _m, change_mana(_q))
        add_int(P_SINT, ID_SQLAUNCH % _m, launch(ID_SQORB % _m, STAFF_QUICK_ANIM))
        add_int(P_SINT, ID_SQUICK % _m, stats_check(_q, RT_SQUICK, [ID_SQCOST % _m, ID_SQLAUNCH % _m, ID_SQEFF], ID_SFAIL))
        _tap = ID_SQUICK % _m
    else:
        _tap = json.loads(json.dumps(VSP["Next"]["0"]))       # the vanilla spear Chaining (its vars stay on the item)
    add_int(P_SINT, ID_SCOST % _m, change_mana(_c))
    add_int(P_SINT, ID_SLAUNCH % _m, launch(ID_SORB % _m, "CastSummonCharged"))
    add_int(P_SINT, ID_SCAST % _m, stats_check(_c, VSC["RunTime"], [ID_SSTAM, ID_SSTAMD, ID_SCOST % _m, ID_SLAUNCH % _m, ID_SCEFF], ID_SFAIL))
    _ch = {"Type": "Charging", "Effects": dict(VSP["Effects"]), "AllowIndefiniteHold": VSP["AllowIndefiniteHold"],
           "HorizontalSpeedMultiplier": VSP["HorizontalSpeedMultiplier"], "Next": {"0": _tap, "1": ID_SCAST % _m}}
    add_int(P_SINT, ID_SROOT % _m, _ch)
    add_root(P_SROOT, ID_SROOT % _m, [ID_SROOT % _m])


# ---- projectiles (spec 2.3, 15.2): fully resolved, no Parent
def orb(dmg):
    d = json.loads(json.dumps(VORB))
    d.pop("Parent", None)
    d["Damage"] = dmg
    return d


def quick_orb(dmg):
    d = orb(dmg)
    d["Appearance"] = QMODEL
    d["MuzzleVelocity"] = VORB["MuzzleVelocity"] * SPEED_X
    d["TerminalVelocity"] = VORB["TerminalVelocity"] * SPEED_X
    imp = PS_IMPACT if QUICK_LOOK == "recolor" else "Impact_Ice"
    d["HitParticles"] = {"SystemId": imp}
    d["DeathParticles"] = {"SystemId": imp}
    return d


def add_prj(pid, obj):
    assert pid not in PRJS and not az_has("prj", pid), pid
    PRJS[pid] = obj
    put(P_PRJ % pid, obj)


for _m, _c, _q, _k, _cd, _qd in WT:
    if _m != "Wood":
        add_prj(ID_ORB % _m, orb(_cd))
    if _m != "Wood" or WOOD_QUICK:
        add_prj(ID_QORB % _m, quick_orb(_qd))
for _m, _c, _q, _k, _cd, _qd in ST:
    add_prj(ID_SORB % _m, orb(_cd))
    if STAFF_TAP == "quick":
        add_prj(ID_SQORB % _m, quick_orb(_qd))


# ---- the quick-orb look (spec 2.3)
def blue_color(s):
    """a vanilla particle / trail colour turned blue: hues from yellow to cyan (40-180 deg) move into the blue range, the rest stay"""
    m = re.match(r"^(rgba\()?#([0-9a-fA-F]{6})([0-9a-fA-F]{2})?(.*)$", s)
    if not m:
        return s
    h6 = m.group(2)
    r, g, b = (int(h6[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
    deg = hh * 360.0
    if 40.0 <= deg <= 180.0 and ss > 0.15:
        deg = min(250.0, max(185.0, 215.0 + (deg - 120.0) * 0.5))
        r, g, b = colorsys.hsv_to_rgb(deg / 360.0, ss, vv)
    out = "#%02x%02x%02x" % tuple(int(round(c * 255)) for c in (r, g, b))
    return (m.group(1) or "") + out + (m.group(3) or "") + m.group(4)


def blue_tree(x):
    if isinstance(x, dict):
        return dict((k, (blue_color(v) if (k == "Color" and isinstance(v, str)) else blue_tree(v))) for k, v in x.items())
    if isinstance(x, list):
        return [blue_tree(v) for v in x]
    return x


assert blue_color("#5bff57").startswith("#") and blue_color("#5bff57") != "#5bff57" and blue_color("#3232ff") == "#3232ff"
assert blue_color("rgba(#6cb839, 1)").startswith("rgba(#") and blue_color("rgba(#6cb839, 1)").endswith(", 1)")


def hue(hexs):
    r, g, b = (int(hexs[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    return colorsys.rgb_to_hsv(r, g, b)[0] * 360.0


QLOOK_FILES = []
if QUICK_LOOK == "recolor":
    for _src, _dst in PSP.items():
        _d = blue_tree(json.loads(AZ.read(_IDX["pspawn"][_src][0]).decode("utf-8-sig")))
        put(P_PSPAWN % _dst, _d)
        QLOOK_FILES.append(P_PSPAWN % _dst)
    for _src, _dst in PSYS.items():
        _d = json.loads(AZ.read(_IDX["psys"][_src][0]).decode("utf-8-sig"))
        for _sp in _d["Spawners"]:
            assert _sp["SpawnerId"] in PSP, "%s names an unknown spawner %s" % (_src, _sp["SpawnerId"])
            _sp["SpawnerId"] = PSP[_sp["SpawnerId"]]
        put(P_PSYS % _dst, _d)
        QLOOK_FILES.append(P_PSYS % _dst)
    _tr = az_get("trail", "SkeletonMage")
    assert _tr["Start"]["Color"] == "rgba(#6cb839, 1)", _tr["Start"]
    _tr = json.loads(json.dumps(_tr))
    _tr["Start"]["Color"] = "rgba(%s, 1)" % BLUE
    put(P_TRAIL % TRAIL_BLUE, _tr)
    QLOOK_FILES.append(P_TRAIL % TRAIL_BLUE)
    # the blue Fireball texture: a gradient map of the green SkeletonMage texture onto the vanilla Iceball colours, alpha kept
    _skel = AZ.read("Common/Items/Projectiles/Fireball_Textures/SkeletonMage.png")
    QTEX = SA.recolor(_skel, SA.palette_from([AZ.read("Common/Items/Projectiles/Iceball_Texture.png")]))
    ASSETS["Common/" + TEX_QORB] = QTEX
    _qm = json.loads(json.dumps(VORBM))
    _qm["DefaultAttachments"][0]["Texture"] = TEX_QORB
    _qm["Particles"] = [{"Color": BLUE, "SystemId": PS_GLOW, "TargetNodeName": "Fireball"}, {"Color": BLUE, "Scale": 5, "SystemId": PS_HEAD}]
    for _t in _qm["Trails"]:
        _t["TrailId"] = TRAIL_BLUE
else:
    _qm = json.loads(json.dumps(VORBM))
    _qm["DefaultAttachments"] = [{"Model": "Items/Projectiles/Iceball.blockymodel", "Texture": "Items/Projectiles/Iceball_Texture.png"}]
    _qm["Particles"] = [{"SystemId": "IceBall", "TargetNodeName": "Fireball"}]
    _qm["Trails"] = [{"TrailId": "Orb_Trail_White", "TargetNodeName": "Origin_Item"}]
    QTEX = None
if QUICK_SIZE_MODE == "model":
    _fm = json.loads(AZ.read("Common/" + _qm["DefaultAttachments"][0]["Model"]).decode("utf-8-sig"))
    _f = QUICK_SIZE_DEF / 100.0

    def _scale_node(n):
        for k in ("position",):
            if isinstance(n.get(k), dict):
                n[k] = dict((a, v * _f) for a, v in n[k].items())
        sh = n.get("shape") or {}
        for k in ("offset", "stretch"):
            if isinstance(sh.get(k), dict):
                sh[k] = dict((a, v * _f) for a, v in sh[k].items())
        for ch in n.get("children") or []:
            _scale_node(ch)
    for _nd in _fm.get("nodes") or []:
        _scale_node(_nd)
    ASSETS["Common/" + MODEL_QORB] = json.dumps(_fm, indent=2) + "\n"
    _qm["DefaultAttachments"][0]["Model"] = MODEL_QORB
    for _p in _qm["Particles"]:
        _p["Scale"] = _p.get("Scale", 1) * _f
assert _qm["HitBox"] == VORBM["HitBox"], "the quick orb keeps the charged orb's hitbox"
put(P_MODEL % QMODEL, _qm)
QMODEL_JSON = _qm

# ---- the wand items (spec 1.1) + art (spec 1.2 / 1.3)
ART = {}
for _m, _c, _q, _k, _cd, _qd in WT[1:]:
    _swr = resolve("item", "Weapon_Sword_" + _m)
    _tex, _icon = SA.wand_art(AZ, _m, WAND_STYLE)
    ART[_m] = (_tex, _icon)
    ASSETS["Common/" + TEX_WAND % _m] = _tex
    ASSETS["Common/" + ICON_WAND % _m] = _icon
    _it = {"TranslationProperties": {"Name": "server.items.Weapon_Wand_%s.name" % _m}, "Categories": list(VW["Categories"]),
           "Icon": ICON_WAND % _m, "Quality": _swr["Quality"], "ItemLevel": _swr["ItemLevel"], "Model": VW["Model"],
           "Texture": TEX_WAND % _m, "PlayerAnimationsId": VW["PlayerAnimationsId"], "Particles": json.loads(json.dumps(VW["Particles"])),
           "Utility": dict(VW["Utility"]), "Interactions": {"Primary": ID_WROOT % _m, "Secondary": ID_WROOT % _m},
           "IconProperties": json.loads(json.dumps(VW["IconProperties"])), "DroppedItemAnimation": VW["DroppedItemAnimation"],
           "Tags": json.loads(json.dumps(VW["Tags"])), "Weapon": {}, "ItemSoundSetId": VW["ItemSoundSetId"],
           "Recipe": WAND_RECIPES[_m]}
    assert "skyy" not in ("Weapon_Wand_" + _m).lower(), "never 'skyy' in a gear id (SkyyGear GearData.skyyItem)"
    ITEMS["Weapon_Wand_" + _m] = _it
    put(P_WITEM % _m, _it)
assert [(m, ITEMS["Weapon_Wand_" + m]["Quality"], ITEMS["Weapon_Wand_" + m]["ItemLevel"]) for m in NEW_METALS] == [
    ("Copper", "Common", 10), ("Iron", "Uncommon", 20), ("Thorium", "Rare", 30), ("Cobalt", "Rare", 35), ("Adamantite", "Rare", 40),
    ("Mithril", "Epic", 50), ("Onyxium", "Epic", 50)], "the vanilla sword qualities / levels changed (spec 1.1 table)"
# the same art in the other style still builds (spec 1.3: style A is one letter away) - checked, never shipped
_other = "A" if WAND_STYLE == "B" else "B"
for _m in NEW_METALS:
    _t2, _i2 = SA.wand_art(AZ, _m, _other)
    assert SA.png_size(_t2) == (64, 32) and SA.png_size(_i2) == (64, 64) and _t2 != ART[_m][0], _m

# ---- the 8 staff item overrides (spec 15.2 / 15.3)
STAFF_DIFF = {}
for _m, _c, _q, _k, _cd, _qd in ST:
    _v = VSTAFF[_m]
    _o = json.loads(json.dumps(_v))
    _o["Interactions"] = {"Primary": ID_SROOT % _m, "Secondary": ID_SROOT % _m}
    if STAFF_TAP == "quick":
        _o.pop("InteractionVars")
    else:
        _o["InteractionVars"] = dict((k, v) for k, v in _v["InteractionVars"].items() if k.startswith("Spear_"))
    if _m == "Onyxium" and ONYX_STAFF_RECIPE:
        _o["Recipe"] = onyx_recipe()
    # everything else equals vanilla (the S14 _spell_diff check)
    _a = dict((k, v) for k, v in _v.items() if k not in ("Interactions", "InteractionVars", "Recipe"))
    _b = dict((k, v) for k, v in _o.items() if k not in ("Interactions", "InteractionVars", "Recipe"))
    assert _a == _b and [k for k in _v if k in _o] == [k for k in _o if k in _v], _m
    ITEMS["Weapon_Staff_" + _m] = _o
    put(P_SITEM % _m, _o)
    STAFF_DIFF[_m] = sorted(set(k for k in set(_v) | set(_o) if _v.get(k) != _o.get(k)))

# ---- language (spec 1.1, 2.4, 15.3): names of the new wands + descriptions through the default key server.items.<id>.description
LANG = []
for _m, _c, _q, _k, _cd, _qd in WT[1:]:
    LANG.append("items.Weapon_Wand_%s.name = %s Wand" % (_m, _m))
    LANG.append("items.Weapon_Wand_%s.description = Tap: quick shot, %d Mana. Hold: charged shot, %d Mana." % (_m, _q, _c))
if WOOD_QUICK:
    for _i in ["Weapon_Wand_Wood"] + WOOD_ALIASES:
        LANG.append("items.%s.description = Tap: quick shot, %d Mana. Hold: charged shot, %d Mana." % (_i, WT[0][2], WT[0][1]))
for _m, _c, _q, _k, _cd, _qd in ST:
    if STAFF_TAP == "quick":
        LANG.append("items.Weapon_Staff_%s.description = Tap: quick shot, %d Mana. Hold 1 s: charged shot, %d Mana." % (_m, _q, _c))
    else:
        LANG.append("items.Weapon_Staff_%s.description = Hold 1 s: charged shot, %d Mana." % (_m, _c))
_vlang = AZ.read(P_LANG).decode("utf-8-sig")
for _l in LANG:
    assert ("\n" + _l.split(" = ")[0] + " ") not in _vlang, "vanilla already has " + _l.split(" = ")[0]
ASSETS[P_LANG] = "\n".join(LANG) + "\n"

# ================================================================= reference closure + gate simulation (pure Python, self-check)
OUR_INTS = set(INTS)
OUR_ROOTS = set(ROOTS)


def refs_of(x, out):
    """interaction / root ids a generated interaction names (strings in Next / Failed / Interactions)"""
    if isinstance(x, str):
        out.add(x)
    elif isinstance(x, list):
        for e in x:
            refs_of(e, out)
    elif isinstance(x, dict):
        for k, v in x.items():
            if k in ("Next", "Failed", "Interactions"):
                if isinstance(v, dict) and "Type" not in v and "Interactions" not in v:      # a Charging key map
                    for vv in v.values():
                        refs_of(vv, out)
                else:
                    refs_of(v, out)
    return out


_bad_ref = []
SKILLS_INTS = ("Wand_Cast_Left_Charged", "Wand_Cast_Cost", "Staff_Cast_Summon_Charged", "Staff_Cast_Cost", "Spellbook_Cast_Hurl_Charged",
               "Spellbook_Cast_Cost", "Gun_Shoot_Flintlock_Charged", "Gun_Shoot_Cost")
for _iid, _d in INTS.items():
    for _r in refs_of(_d, set()):
        if _r in SKILLS_INTS and not (_iid == "Wand_Primary" and _r == "Wand_Cast_Left_Charged"):
            _bad_ref.append("%s names SkyySkills' %s" % (_iid, _r))
        if _r not in OUR_INTS and _r not in OUR_ROOTS and not az_has("int", _r) and not az_has("root", _r):
            _bad_ref.append("%s -> unknown %s" % (_iid, _r))
        if _r in ("Staff_Primary",):
            _bad_ref.append("%s names Staff_Primary" % _iid)
    if _d.get("Type") == "LaunchProjectile":
        if _d["ProjectileId"] not in PRJS and not az_has("prj", _d["ProjectileId"]):
            _bad_ref.append("%s launches unknown %s" % (_iid, _d["ProjectileId"]))
    _snd = (_d.get("Effects") or {}).get("WorldSoundEventId")
    if _snd and not az_has("sound", _snd):
        _bad_ref.append("%s: unknown sound %s" % (_iid, _snd))
for _rid, _d in ROOTS.items():
    for _r in _d["Interactions"]:
        if _r not in OUR_INTS:
            _bad_ref.append("root %s -> %s" % (_rid, _r))
for _pid, _d in PRJS.items():
    if _d["Appearance"] != QMODEL and not az_has("model", _d["Appearance"]):
        _bad_ref.append("%s: unknown model %s" % (_pid, _d["Appearance"]))
    for _k in ("HitParticles", "DeathParticles"):
        _sid = _d[_k]["SystemId"]
        if _sid not in PSYS.values() and _sid not in _IDX["psys"]:
            _bad_ref.append("%s: unknown particle system %s" % (_pid, _sid))
for _iid, _it in ITEMS.items():
    for _slot, _rid in _it["Interactions"].items():
        if _rid not in OUR_ROOTS:
            _bad_ref.append("%s %s -> %s" % (_iid, _slot, _rid))
    for _f in ("Icon", "Texture", "Model"):
        _p = _it.get(_f)
        if _p and ("Common/" + _p) not in AZ_SET and ("Common/" + _p) not in ASSETS:
            _bad_ref.append("%s: missing %s %s" % (_iid, _f, _p))
    if not az_has("quality", _it["Quality"]):
        _bad_ref.append("%s: unknown quality %s" % (_iid, _it["Quality"]))
for _p in ([QMODEL_JSON["Model"], QMODEL_JSON["Texture"]] + [a["Model"] for a in QMODEL_JSON["DefaultAttachments"]]
           + [a["Texture"] for a in QMODEL_JSON["DefaultAttachments"]]):
    if ("Common/" + _p) not in AZ_SET and ("Common/" + _p) not in ASSETS:
        _bad_ref.append("quick model: missing " + _p)
for _p in QMODEL_JSON["Particles"]:
    if _p["SystemId"] not in PSYS.values() and _p["SystemId"] not in _IDX["psys"]:
        _bad_ref.append("quick model: particle system " + _p["SystemId"])
for _t in QMODEL_JSON["Trails"]:
    if _t["TrailId"] != TRAIL_BLUE and not az_has("trail", _t["TrailId"]):
        _bad_ref.append("quick model: trail " + _t["TrailId"])
if QUICK_LOOK == "recolor":
    for _src, _dst in PSP.items():
        _d = json.loads(ASSETS[P_PSPAWN % _dst])
        _tx = _d.get("Particle", {}).get("Texture")
        if _tx and ("Common/" + _tx) not in AZ_SET:
            _bad_ref.append("%s: texture %s" % (_dst, _tx))
assert not _bad_ref, "reference closure:\n  " + "\n  ".join(_bad_ref)


# a small gate walk of OUR chains (the harness runs SkyySkills' own spell_casts on the full asset set): per Charging key the Mana the
# check needs and the Mana the step spends - they must match the table, and a Failed branch spends nothing
def gate(charging_id):
    ch = INTS[charging_id]
    out = {}
    for key, tgt in ch["Next"].items():
        if not isinstance(tgt, str) or tgt not in INTS:
            out[key] = None
            continue
        sc = INTS[tgt]
        assert sc["Type"] == "StatsCondition" and sc["Failed"] in (ID_WFAIL, ID_SFAIL), tgt
        spend = 0
        for r in sc["Next"]["Interactions"]:
            for iid in r["Interactions"]:
                d = INTS[iid]
                if d.get("Type") == "ChangeStat":
                    spend += d["StatModifiers"].get("Mana", 0)
        fail = INTS[sc["Failed"]]
        assert fail["Type"] == "Simple" and "StatModifiers" not in fail and "Next" not in fail
        out[key] = (sc["Costs"]["Mana"], -spend)
    return out


for _m, _c, _q, _k, _cd, _qd in WT[1:]:
    assert gate(ID_WROOT % _m) == {"0": (_q, _q), "0.35": (_c, _c)}, (_m, gate(ID_WROOT % _m))
for _m, _c, _q, _k, _cd, _qd in ST:
    assert gate(ID_SROOT % _m) == ({"0": (_q, _q), "1": (_c, _c)} if STAFF_TAP == "quick" else {"0": None, "1": (_c, _c)}), (_m, gate(ID_SROOT % _m))
if WOOD_QUICK:
    _qw = INTS[ID_WQUICK % "Wood"]
    assert _qw["Costs"]["Mana"] == 1 and INTS[ID_WQCOST % "Wood"]["StatModifiers"]["Mana"] == -1
# cadence of our chains (spec 2.2 / 15.2): taps never faster than today's, charged chains = vanilla
_wq = RT_WQUICK + max(RT_LAUNCH, RT_QEFF, 0.0)
_sq = RT_SQUICK + max(RT_LAUNCH, RT_QEFF, 0.0)
_wc = VWC["RunTime"] + max(0.0, RT_LAUNCH, VWE["RunTime"])
_scc = VSC["RunTime"] + max(0.0, 0.0, 0.0, RT_LAUNCH, 0.5)
assert _wq >= VAN_TAP_W - 1e-9 and _sq >= VAN_TAP_S - 1e-9 and abs(_wc - VAN_CAST_W) < 1e-9 and abs(_scc - VAN_CAST_S) < 1e-9, (_wq, _sq, _wc, _scc)
print("assets: %d files - %d items (7 wands + 8 staffs), %d interactions, %d roots, %d projectiles, %d quick-look files, %d art PNGs, lang %d lines"
      % (len(ASSETS), len(ITEMS), len(INTS), len(ROOTS), len(PRJS), len(QLOOK_FILES) + 1 + (1 if QTEX else 0),
         len([p for p in ASSETS if p.endswith(".png")]), len(LANG)))

# ================================================================= the SET jars, SkyySkills (anchor + handover), the clash scan
_dst = open(SET_FILE, encoding="utf-8").read()      # read only, never run (tools/deploy_set.py; a scratch copy only with --set-file)
_s0 = _dst.index("SET = [")
PINS = re.findall(r'\("(Skyy\w+)", "([0-9][0-9.]*)"\)', _dst[_s0:_dst.index("\n]\n", _s0)])
PACKS = re.findall(r'"([^"]+:[^"]+)"', re.search(r"PACK_THIRD_PARTY = \[(.*?)\]", _dst).group(1))
assert len(PINS) >= 20 and PACKS and any(m == "SkyySkills" for m, v in PINS), (PINS, PACKS)


def vtuple(s):
    return tuple(int(x) for x in s.split("."))


SKILLS_PIN = dict(PINS)["SkyySkills"]
ARMORY_PINNED = dict(PINS).get("SkyyArmory")
SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-%s.jar" % SKILLS_PIN)
assert os.path.isfile(SKILLS_JAR), "the pinned SkyySkills jar %s is not built here" % SKILLS_JAR
# FIX ROUND (review: a partial pin passed every check): SkyyArmory pinned = SkyyClasses 0.1.11+ in the same deploy (the wand heal caps read
# armory:fn:info / armory:quick; 0.1.10 would heal a tap as much as a charged shot from Iron up). The SkyySkills 0.4.15 pair is checked below.
CLASSES_PARTNER = "0.1.11"
if ARMORY_PINNED == VERSION:
    _cpin = dict(PINS).get("SkyyClasses")
    assert _cpin is not None and vtuple(_cpin) >= vtuple(CLASSES_PARTNER), (
        "SkyyArmory %s is pinned with SkyyClasses %s: pin SkyyClasses %s+ (the wand heal caps) in the same deploy" % (VERSION, _cpin, CLASSES_PARTNER))


def jar_json(jz, name):
    return json.loads(jz.read(name).decode("utf-8-sig"))


def skills_anchor(path):
    """spec 2.5: the pinned SkyySkills' Wood rung = 5 / -5, and its three wood-tier wand items still point at Wand_Primary with a 5-Mana
    spend (so our Wand_Primary override reaches them and the hold stays the ladder's Wood rung). Returns the jar's staff item paths."""
    with zipfile.ZipFile(path) as jz:
        names = jz.namelist()
        byb = dict((os.path.basename(n)[:-5], n) for n in names if n.startswith("Server/Item/") and n.endswith(".json"))
        wc = jar_json(jz, byb["Wand_Cast_Left_Charged"])
        cost = jar_json(jz, byb["Wand_Cast_Cost"])
        assert wc["Costs"]["Mana"] == WT[0][1] and cost["StatModifiers"]["Mana"] == -WT[0][1], (
            "%s: the Wood rung is %s / %s, not %d / -%d - re-anchor the ladder on purpose" % (os.path.basename(path), wc["Costs"], cost["StatModifiers"], WT[0][1], WT[0][1]))
        for iid in ["Weapon_Wand_Wood"] + WOOD_ALIASES:
            d = jar_json(jz, byb[iid])
            assert d["Interactions"] == {"Primary": "Wand_Primary", "Secondary": "Wand_Primary"}, (iid, d["Interactions"])
            sp = d["InteractionVars"]["Wand_Cast_Left_Cost"]["Interactions"][0]
            assert sp == {"Parent": "Wand_Cast_Cost", "StatModifiers": {"Mana": -WT[0][1]}}, (iid, sp)
        assert "Wand_Primary" not in byb, "%s ships Wand_Primary - SkyyArmory owns it" % os.path.basename(path)
        return sorted(n for n in names if n in [P_SITEM % m for m in METALS])


_staff_pinned = skills_anchor(SKILLS_JAR)
HANDOVER = []
PARTNER_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-%s.jar" % SKILLS_HANDOVER)
if vtuple(SKILLS_PIN) >= vtuple(SKILLS_HANDOVER):
    assert not _staff_pinned, "pinned SkyySkills %s still ships %s - the staff handover needs %s" % (SKILLS_PIN, _staff_pinned, SKILLS_HANDOVER)
    HANDOVER.append("pinned SkyySkills %s ships none of the 8 staff files (handover done)" % SKILLS_PIN)
else:
    assert ARMORY_PINNED != VERSION, ("SkyyArmory %s is pinned with SkyySkills %s, which still ships the 8 staff files: pin SkyySkills %s "
                                      "(staff handover) in the same deploy" % (VERSION, SKILLS_PIN, SKILLS_HANDOVER))
    HANDOVER.append("NOTE pinned SkyySkills %s still ships the 8 staff files (%d) - SkyyArmory %s must deploy TOGETHER with SkyySkills %s "
                    "(and roll back together)" % (SKILLS_PIN, len(_staff_pinned), VERSION, SKILLS_HANDOVER))
    if os.path.isfile(PARTNER_JAR):
        _staff_partner = skills_anchor(PARTNER_JAR)
        assert not _staff_partner, "SkyySkills %s still ships %s - the handover build must drop them" % (SKILLS_HANDOVER, _staff_partner)
        HANDOVER.append("partner SkyySkills %s (built, not pinned) ships none of the 8 staff files and keeps the Wood rung 5 / 5" % SKILLS_HANDOVER)
    else:
        HANDOVER.append("NOTE partner SkyySkills %s is not built yet - its harness must prove it ships none of the 8 staff files" % SKILLS_HANDOVER)


def asset_key(n):
    """(asset class, id) of a jar entry - two packs collide on the same id within one asset class (Common files: the exact path)"""
    if n.startswith("Common/"):
        return ("common", n)
    for pre, k in (("Server/Item/Items/", "item"), ("Server/Item/Interactions/", "int"), ("Server/Item/RootInteractions/", "root"),
                   ("Server/Projectiles/", "prj"), ("Server/Models/", "model"), ("Server/Entity/Trails/", "trail"),
                   ("Server/Item/Recipes/", "recipe")):
        if n.startswith(pre) and n.endswith(".json"):
            return (k, os.path.basename(n)[:-5])
    if n.startswith("Server/Particles/") and n.endswith((".particlesystem", ".particlespawner")):
        return ("psys" if n.endswith(".particlesystem") else "pspawn", os.path.basename(n).rsplit(".", 1)[0])
    return None


OUR_KEYS = set(k for k in (asset_key(p) for p in ASSETS) if k is not None)
OUR_KEYS |= set(("recipe", i + "_Recipe_Generated_0") for i in ITEMS if "Recipe" in ITEMS[i])
STAFF_KEYS = set(("item", i) for i in ARMORY_OWNED)
OUR_EXCL = OUR_KEYS - STAFF_KEYS


def clash(names):
    keys = set(k for k in (asset_key(n) for n in names) if k is not None)
    for n in names:                            # standalone recipes collide with our generated item recipe ids too
        if n.startswith("Server/Item/Recipes/") and n.endswith(".json"):
            keys.add(("recipe", os.path.basename(n)[:-5]))
    return sorted(OUR_EXCL & keys), sorted(STAFF_KEYS & keys)


CHECKED, NOTES = [], []
for _mod, _ver in PINS:
    if _mod == MOD:
        continue
    _jp = os.path.join(ROOT, _mod, "%s-%s.jar" % (_mod, _ver))
    if not os.path.isfile(_jp):
        NOTES.append("%s %s is not built here - not checked" % (_mod, _ver))
        continue
    with zipfile.ZipFile(_jp) as _jz:
        _ex, _st = clash(_jz.namelist())
    assert not _ex, "%s %s (live set) also ships SkyyArmory-owned assets: %s" % (_mod, _ver, _ex[:6])
    assert not _st or _mod == "SkyySkills", "%s %s ships the ladder staff items %s - only SkyySkills may (the handover)" % (_mod, _ver, _st)
    CHECKED.append(_mod)
_pk_found, _other = [], []
for _f in (sorted(os.listdir(B.MODS_DIR)) if os.path.isdir(B.MODS_DIR) else []):       # installed mods, read only
    _p = os.path.join(B.MODS_DIR, _f)
    try:
        if os.path.isdir(_p):
            with open(os.path.join(_p, "manifest.json"), "rb") as _mf:
                _man = json.loads(_mf.read().decode("utf-8-sig"))
            _nm = [os.path.relpath(os.path.join(_r, _x), _p).replace(os.sep, "/") for _r, _ds, _fl in os.walk(_p) for _x in _fl]
        elif _f.lower().endswith((".zip", ".jar")):
            with zipfile.ZipFile(_p) as _mz:
                _man = json.loads(_mz.read("manifest.json").decode("utf-8-sig"))
                _nm = _mz.namelist()
        else:
            continue
    except Exception:
        continue
    if not isinstance(_man, dict):
        continue
    _key = "%s:%s" % (_man.get("Group"), _man.get("Name"))
    if str(_man.get("Group")) == "Skyy":
        continue                               # our own deployed jars: the SET pins above are the ones that count
    _ex, _st = clash(_nm)
    _wp = sorted(n for n in _nm if os.path.basename(n) == "Wand_Primary.json")
    if _key in PACKS:
        _pk_found.append(_key)
        assert not _ex and not _st and not _wp, "pack mod %s (%s) ships SkyyArmory assets %s" % (_key, _f, (_ex + _st + _wp)[:6])
    elif _ex or _st or _wp:
        _other.append("%s (%d)" % (_f, len(_ex) + len(_st) + len(_wp)))
if _other:
    NOTES.append("installed mods that are not pack mods and ship SkyyArmory ids (not enabled in the test world; they clash with SkyySkills the "
                 "same way today): " + ", ".join(_other))
print("clash scan: %d SET jars + pack mods %s checked - no clash; %s" % (len(CHECKED), sorted(_pk_found), "; ".join(HANDOVER)))
for _nt in NOTES:
    print("clash scan: NOTE " + _nt)

# ================================================================= JVM + engine members (every one probed: a missing one fails the build)
import jpype
_tmp = os.environ.get("TEMP") or os.environ.get("TMP") or HERE
jpype.startJVM(B._jvm(), "-XX:-UsePerfData", "-Djava.io.tmpdir=" + _tmp, "--add-opens=java.base/java.lang=ALL-UNNAMED",
               "--enable-native-access=ALL-UNNAMED", classpath=[B.JAVASSIST], convertStrings=True)
_JC = jpype.JClass
pool = _JC("javassist.ClassPool")(False)
pool.appendSystemPath()
pool.appendClassPath(B.SERVER_JAR)
CtField, CtNewMethod, CtNewConstructor = _JC("javassist.CtField"), _JC("javassist.CtNewMethod"), _JC("javassist.CtNewConstructor")
JMod = _JC("javassist.Modifier")
OUT = B.class_out(OUT_DIR)
_pk = B.manifest(MOD, VERSION, "", "")
PACK_KEY = "%s:%s" % (_pk["Group"], _pk["Name"])     # the asset pack key the engine gives this jar (PluginIdentifier = Group:Name)
assert PACK_KEY == "Skyy:0.1 SkyyArmory", PACK_KEY
PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE, "PACK": PACK_KEY,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "HOLD": "com.hypixel.hytale.component.Holder",
    "ADDR": "com.hypixel.hytale.component.AddReason",
    "REMR": "com.hypixel.hytale.component.RemoveReason",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "SG": "com.hypixel.hytale.component.SystemGroup",
    "SDEP": "com.hypixel.hytale.component.dependency.SystemDependency",
    "ORD": "com.hypixel.hytale.component.dependency.Order",
    "CTYPE": "com.hypixel.hytale.component.ComponentType",
    "COMP": "com.hypixel.hytale.component.Component",
    "DES": "com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem",
    "DMOD": "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
    "DMG": "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
    "DSRC": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$Source",
    "DPRJ": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource",
    "HSYS": "com.hypixel.hytale.component.system.HolderSystem",
    "LPC": "com.hypixel.hytale.server.core.entity.entities.ProjectileComponent",
    "ESC": "com.hypixel.hytale.server.core.modules.entity.component.EntityScaleComponent",
    "SPP": "com.hypixel.hytale.server.core.modules.physics.SimplePhysicsProvider",
    "FPSS": "com.hypixel.hytale.server.core.modules.physics.util.ForceProviderStandardState",
    "DSP": "com.hypixel.hytale.server.core.modules.entity.DespawnComponent",          # fix round: the quick orb's reach
    "TRS": "com.hypixel.hytale.server.core.modules.time.TimeResource",
    "RTY": "com.hypixel.hytale.component.ResourceType",
    "RSC": "com.hypixel.hytale.component.Resource",
    "VEC": "org.joml.Vector3d",
    "ITM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "INT": PI + "Interaction",
    "PRJ": "com.hypixel.hytale.server.core.asset.type.projectile.config.Projectile",
    "LPI": PI + "server.LaunchProjectileInteraction",
    "SCB": PI + "none.StatsConditionBaseInteraction",
    "CSB": PI + "server.ChangeStatBaseInteraction",
    "CHI": PI + "client.ChargingInteraction",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "DAM": "com.hypixel.hytale.assetstore.map.DefaultAssetMap",
    "CRP": "com.hypixel.hytale.component.ComponentRegistryProxy",
    "FN": "java.util.function.Function",
    "I2F": "it.unimi.dsi.fastutil.ints.Int2FloatMap",
    "F2O": "it.unimi.dsi.fastutil.floats.Float2ObjectMap",
}
ADRS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction"
ONADD = "com.hypixel.hytale.server.core.modules.entity.LegacyProjectileSystems$OnAddHolderSystem"
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"


def jdesc(t):
    if t.endswith("[]"):
        return "[" + jdesc(t[:-2])
    prim = {"int": "I", "long": "J", "float": "F", "double": "D", "boolean": "Z", "void": "V", "char": "C", "byte": "B", "short": "S"}
    return prim[t] if t in prim else "L" + t.replace(".", "/") + ";"


PROBED = []


def probe_sig(cls, name, ret, args):
    desc = "(" + "".join(jdesc(a) for a in args) + ")" + jdesc(ret)
    c = pool.get(cls)
    try:
        if name == "<init>":
            c.getConstructor(desc)
        else:
            c.getMethod(name, desc)
    except Exception:
        raise SystemExit("API probe failed: %s.%s%s not found" % (cls, name, desc))
    PROBED.append("%s.%s%s" % (cls.rsplit(".", 1)[1], name, desc))


S_ = "java.lang.String"
O_ = "java.lang.Object"
SIGS = [
    # damage tune (ArmoryTuneSys): Filter group before armor, the projectile's own asset name
    (T["DMOD"], "get", T["DMOD"], []), (T["DMOD"], "getFilterDamageGroup", T["SG"], []),
    (T["DMG"], "getSource", T["DSRC"], []), (T["DMG"], "getAmount", "float", []), (T["DMG"], "setAmount", "void", ["float"]),
    (T["DMG"], "isCancelled", "boolean", []), (T["DPRJ"], "getProjectile", T["REF"], []),
    (T["CB"], "getComponent", T["COMP"], [T["REF"], T["CTYPE"]]), (T["REF"], "isValid", "boolean", []),
    (T["LPC"], "getComponentType", T["CTYPE"], []), (T["LPC"], "getProjectileAssetName", S_, []),
    (T["SDEP"], "<init>", "void", [T["ORD"], "java.lang.Class"]), (T["QRY"], "any", "com.hypixel.hytale.component.query.AnyQuery", []),
    (T["DES"], "handle", "void", ["int", T["ACH"], T["ST"], T["CB"], T["EV"]]),
    # quick-orb spawn hook (ArmorySpawnSys)
    (T["HSYS"], "onEntityAdd", "void", [T["HOLD"], T["ADDR"], T["ST"]]), (T["HSYS"], "onEntityRemoved", "void", [T["HOLD"], T["REMR"], T["ST"]]),
    (T["HOLD"], "getComponent", T["COMP"], [T["CTYPE"]]), (T["HOLD"], "putComponent", "void", [T["CTYPE"], T["COMP"]]),
    (T["ESC"], "<init>", "void", ["float"]), (T["ESC"], "getComponentType", T["CTYPE"], []), (T["ESC"], "getScale", "float", []),
    (T["LPC"], "getSimplePhysicsProvider", T["SPP"], []), (T["VEC"], "set", T["VEC"], ["double", "double", "double"]),
    # fix round: the quick orb's reach (DespawnComponent at the world clock's now + quick.life)
    (T["DSP"], "getComponentType", T["CTYPE"], []), (T["DSP"], "getDespawn", "java.time.Instant", []),
    (T["DSP"], "setDespawn", "void", ["java.time.Instant"]), (T["DSP"], "<init>", "void", ["java.time.Instant"]),
    (T["TRS"], "getResourceType", T["RTY"], []), (T["TRS"], "getNow", "java.time.Instant", []),
    (T["ST"], "getResource", T["RSC"], [T["RTY"]]),
    # pack check + live read-back (ArmoryCheck)
    (T["ITM"], "getAssetMap", T["DAM"], []), (T["INT"], "getAssetMap", "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", []),
    (T["PRJ"], "getAssetMap", T["DAM"], []), (T["DAM"], "getAssetPack", S_, [O_]), (T["DAM"], "getAsset", "com.hypixel.hytale.assetstore.JsonAsset", [O_]),
    (T["PRJ"], "getDamage", "int", []), (T["PRJ"], "getMuzzleVelocity", "double", []), (T["LPI"], "getProjectileId", S_, []),
    (T["DST"], "getMana", "int", []), (T["I2F"], "get", "float", ["int"]), (T["I2F"], "containsKey", "boolean", ["int"]),
    (T["F2O"], "get", O_, ["float"]),
    # plugin
    (PB, "getDataDirectory", "java.nio.file.Path", []), (PB, "getLogger", T["LOG"], []), (PB, "shutdown", "void", []),
    (PB, "getEntityStoreRegistry", T["CRP"], []), (T["CRP"], "registerSystem", "void", ["com.hypixel.hytale.component.system.ISystem"]),
    (T["LOG"], "at", "com.hypixel.hytale.logger.HytaleLogger$Api", ["java.util.logging.Level"]),
]
for _c, _m, _r, _a in SIGS:
    probe_sig(_c, _m, _r, _a)
for _c, _f in ((T["FPSS"], "nextTickVelocity"), (T["VEC"], "x"), (T["VEC"], "y"), (T["VEC"], "z"), (T["ADDR"], "SPAWN"),
               (T["HSV"], "SCHEDULED_EXECUTOR"), (T["ORD"], "BEFORE"), (T["ORD"], "AFTER")):
    _fld = pool.get(_c).getField(_f)
    assert JMod.isPublic(_fld.getModifiers()), "%s.%s is not public" % (_c, _f)
    PROBED.append("%s.%s" % (_c.rsplit(".", 1)[1], _f))
# the protected engine fields read by reflection (never by bytecode: the access audit below proves it)
for _c, _f, _t in ((T["SPP"], "forceProviderStandardState", T["FPSS"]), (T["SCB"], "rawCosts", "it.unimi.dsi.fastutil.objects.Object2FloatMap"),
                   (T["SCB"], "costs", T["I2F"]), (T["CSB"], "entityStatAssets", "it.unimi.dsi.fastutil.objects.Object2FloatMap"),
                   (T["CSB"], "entityStats", T["I2F"]), (T["CHI"], "sortedKeys", "float[]"), (T["CHI"], "next", T["F2O"])):
    _fld = pool.get(_c).getDeclaredField(_f)
    assert str(_fld.getType().getName()) == _t, (_c, _f, str(_fld.getType().getName()))
    PROBED.append("%s.%s (reflection)" % (_c.rsplit(".", 1)[1], _f))
for _c in (ADRS, ONADD):
    pool.get(_c)
# fix round (spec R17): the vanilla life the reach row shortens = ProjectileComponent.assembleDefaultProjectile's
# DespawnComponent.despawnInMilliseconds(time, 60000) - the long constant loaded right before that call (a Hytale change stops the build)
_JCP = _JC("javassist.bytecode.ConstPool")
_adp = [m for m in pool.get(T["LPC"]).getDeclaredMethods() if str(m.getName()) == "assembleDefaultProjectile"]
assert len(_adp) == 1, "ProjectileComponent.assembleDefaultProjectile: %d methods" % len(_adp)
_ami = _adp[0].getMethodInfo()
_acp, _ait = _ami.getConstPool(), _ami.getCodeAttribute().iterator()
_alast, _alife = None, []
while _ait.hasNext():
    _ap = _ait.next()
    _aop = _ait.byteAt(_ap)
    if _aop == 0x14 and _acp.getTag(_ait.u16bitAt(_ap + 1)) == _JCP.CONST_Long:          # ldc2_w <long>
        _alast = int(_acp.getLongInfo(_ait.u16bitAt(_ap + 1)))
    elif _aop == 0xb8 and str(_acp.getMethodrefClassName(_ait.u16bitAt(_ap + 1))) == T["DSP"] \
            and str(_acp.getMethodrefName(_ait.u16bitAt(_ap + 1))) == "despawnInMilliseconds":
        _alife.append(_alast)
assert _alife == [VANILLA_LIFE_MS], "assembleDefaultProjectile's projectile despawn is %s ms, not %d - re-check the quick.life row" % (_alife, VANILLA_LIFE_MS)
PROBED.append("ProjectileComponent.assembleDefaultProjectile despawn %d ms (bytecode)" % VANILLA_LIFE_MS)
print("engine members probed: %d" % len(PROBED))

TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")


def jv(src):
    def rep(m):
        k = m.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def F(cls, src):
    cls.addField(CtField.make(jv(src), cls))


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:3000]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:3000]))


def jstr(s):
    assert all(32 <= ord(c) < 127 for c in s), repr(s)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def jtext(s):
    assert all(32 <= ord(c) < 127 or c == "\n" for c in s), repr(s)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def jarr(xs):
    return "new String[] { " + ", ".join(jstr(x) for x in xs) + " }"


def jints(xs):
    return "new int[] { " + ", ".join(str(int(x)) for x in xs) + " }"


def jdbls(xs):
    return "new double[] { " + ", ".join(repr(float(x)) for x in xs) + " }"


def num(v):
    v = round(float(v), 4)
    return str(int(v)) if v == int(v) else ("%.4f" % v).rstrip("0").rstrip(".")


# ---- the Java tables (one place: the Python tables above)
W_IDS = WAND_IDS
W_ORB = [VAN_ORB] + [ID_ORB % m for m in NEW_METALS]
W_QORB = [(ID_QORB % m) if (m != "Wood" or WOOD_QUICK) else "" for m in METALS]
W_Q = [w[2] if (w[0] != "Wood" or WOOD_QUICK) else 0 for w in WT]
W_QD = [w[5] if (w[0] != "Wood" or WOOD_QUICK) else 0 for w in WT]
S_ORB = [ID_SORB % m for m in METALS]
S_QORB = [(ID_SQORB % m) if STAFF_TAP == "quick" else "" for m in METALS]
S_Q = [s[2] if STAFF_TAP == "quick" else 0 for s in ST]
S_QD = [s[5] if STAFF_TAP == "quick" else 0 for s in ST]
QUICK_IDS = [p for p in W_QORB + S_QORB if p]
ORB_IDS = W_ORB[1:] + S_ORB
assert len(set(QUICK_IDS + ORB_IDS)) == len(QUICK_IDS) + len(ORB_IDS) == len(PRJS) and set(QUICK_IDS + ORB_IDS) == set(PRJS)
WANDS_TEXT = ",".join("%s:%d:%d:%s:%d:%d" % (W_IDS[i], WT[i][1], W_Q[i], num(WT[i][3]), WT[i][4], W_QD[i]) for i in range(len(WT)))
STAFFS_TEXT = ",".join("%s:%d:%d:%s:%d:%d" % (STAFF_IDS[i], ST[i][1], S_Q[i], num(ST[i][3]), ST[i][4], S_QD[i]) for i in range(len(ST)))
QUICK_TEXT = ",".join(QUICK_IDS)
LOOT_TEXT = ",".join(WAND_IDS[1:])
INT_CHECK_IDS = sorted(INTS)                        # every interaction we ship (incl. Wand_Primary): the pack check
ITEM_CHECK_IDS = sorted(ITEMS)
PRJ_CHECK_IDS = sorted(PRJS)
BAND_A = [BANDS[m][0] for m in METALS]
BAND_B = [BANDS[m][1] for m in METALS]
T.update({"NW": str(len(WT)), "SPX": "%d.0" % SPEED_X, "QSH": str(100 // QUICK_SHARE), "SZMODE": QUICK_SIZE_MODE,
          "WQK": "true" if WOOD_QUICK else "false", "STQ": "true" if STAFF_TAP == "quick" else "false"})

# ================================================================= classes (all top-level; methods before callers)
lg = pool.makeClass(PKG + ".ArmoryLog")
dfs = pool.makeClass(PKG + ".ArmoryDefs")
cfg = pool.makeClass(PKG + ".ArmoryCfg")
hooks = pool.makeClass(PKG + ".ArmoryHooks")
spn = pool.makeClass(PKG + ".ArmorySpawn")
tune = pool.makeClass(PKG + ".ArmoryTuneSys", pool.get(T["DES"]))
spsys = pool.makeClass(PKG + ".ArmorySpawnSys", pool.get(T["HSYS"]))
chk = pool.makeClass(PKG + ".ArmoryCheck")
info = pool.makeClass(PKG + ".ArmoryInfoFn")
pl = pool.makeClass(PKG + ".SkyyArmoryPlugin", pool.get(T["JP"]))
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info]

# ---------------------------------------------------------------- ArmoryLog
F(lg, "public static @LOG@ LOG;")
F(lg, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
M(lg, r"""
public static void info(String msg) {
  try {
    if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyArmory] " + msg);
    else System.out.println("[SkyyArmory] " + msg);
  } catch (Throwable t) { }
}""")
M(lg, r"""
public static void warn(String msg) {
  try {
    if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyArmory] " + msg);
    else System.out.println("[SkyyArmory] WARN " + msg);
  } catch (Throwable t) { }
}""")
M(lg, r"""
public static void warnOnce(String key, String msg) {
  if (key == null || ONCE.putIfAbsent(key, Boolean.TRUE) != null) return;
  warn(msg);
}""")

# ---------------------------------------------------------------- ArmoryDefs: the tables + pure decisions (testable on plain values)
for f in ("public static final String VERSION = \"@VERSION@\";", "public static final String PACK = \"@PACK@\";",
          "public static final String[] METALS = %s;" % jarr(METALS),
          "public static final String[] W_IDS = %s;" % jarr(W_IDS),
          "public static final String[] WOOD_ALIASES = %s;" % jarr(WOOD_ALIASES),
          "public static final int[] W_C = %s;" % jints([w[1] for w in WT]),
          "public static final int[] W_Q = %s;" % jints(W_Q),
          "public static final double[] W_MULT = %s;" % jdbls([w[3] for w in WT]),
          "public static final int[] W_CD = %s;" % jints([w[4] for w in WT]),
          "public static final int[] W_QD = %s;" % jints(W_QD),
          "public static final String[] W_ORB = %s;" % jarr(W_ORB),
          "public static final String[] W_QORB = %s;" % jarr(W_QORB),
          "public static final String[] S_IDS = %s;" % jarr(STAFF_IDS),
          "public static final int[] S_C = %s;" % jints([s[1] for s in ST]),
          "public static final int[] S_Q = %s;" % jints(S_Q),
          "public static final double[] S_MULT = %s;" % jdbls([s[3] for s in ST]),
          "public static final int[] S_CD = %s;" % jints([s[4] for s in ST]),
          "public static final int[] S_QD = %s;" % jints(S_QD),
          "public static final String[] S_ORB = %s;" % jarr(S_ORB),
          "public static final String[] S_QORB = %s;" % jarr(S_QORB),
          "public static final int[] BAND_A = %s;" % jints(BAND_A),
          "public static final int[] BAND_B = %s;" % jints(BAND_B),
          "public static final String WANDS_TEXT = %s;" % jstr(WANDS_TEXT),
          "public static final String STAFFS_TEXT = %s;" % jstr(STAFFS_TEXT),
          "public static final String QUICK_TEXT = %s;" % jstr(QUICK_TEXT),
          "public static final String LOOT_TEXT = %s;" % jstr(LOOT_TEXT),
          "public static final String[] ITEM_CHECK = %s;" % jarr(ITEM_CHECK_IDS),
          "public static final String[] INT_CHECK = %s;" % jarr(INT_CHECK_IDS),
          "public static final String[] PRJ_CHECK = %s;" % jarr(PRJ_CHECK_IDS),
          "public static final double SPEED_X = @SPX@;",
          "public static final long VANILLA_LIFE_MS = %dL;" % VANILLA_LIFE_MS,
          "public static final int QUICK_SHARE_PCT = @QSH@;",
          "public static final String SIZE_MODE = \"@SZMODE@\";",
          "public static final boolean WOOD_QUICK = @WQK@;",
          "public static final boolean STAFF_QUICK = @STQ@;",
          "public static volatile java.util.HashMap PID = null;",
          "public static volatile java.util.HashMap ITEM = null;"):
    F(dfs, f)
M(dfs, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# pid -> code: 1000 + i = wand quick i, 2000 + i = wand charged orb i (metals only), 3000 + i = staff quick i, 4000 + i = staff orb i
M(dfs, r"""
public static java.util.HashMap pids() {
  java.util.HashMap m = PID;
  if (m != null) return m;
  m = new java.util.HashMap();
  for (int i = 0; i < W_QORB.length; i++) if (W_QORB[i].length() > 0) m.put(W_QORB[i], Integer.valueOf(1000 + i));
  for (int i = 1; i < W_ORB.length; i++) m.put(W_ORB[i], Integer.valueOf(2000 + i));
  for (int i = 0; i < S_QORB.length; i++) if (S_QORB[i].length() > 0) m.put(S_QORB[i], Integer.valueOf(3000 + i));
  for (int i = 0; i < S_ORB.length; i++) m.put(S_ORB[i], Integer.valueOf(4000 + i));
  PID = m;
  return m;
}""")
M(dfs, r"""
public static int pidCode(String pid) {
  if (pid == null) return -1;
  Object o = pids().get(pid);
  return o instanceof Integer ? ((Integer) o).intValue() : -1;
}""")
M(dfs, "public static boolean isQuick(String pid) { int c = pidCode(pid); return (c >= 1000 && c < 2000) || (c >= 3000 && c < 4000); }")
M(dfs, "public static boolean isOurs(String pid) { return pidCode(pid) >= 0; }")
# item id -> code: 100 + i = wand i (the Rotten / Tribal wands answer as the Wood wand), 200 + i = staff i
M(dfs, r"""
public static java.util.HashMap items() {
  java.util.HashMap m = ITEM;
  if (m != null) return m;
  m = new java.util.HashMap();
  for (int i = 0; i < W_IDS.length; i++) m.put(W_IDS[i], Integer.valueOf(100 + i));
  for (int i = 0; i < WOOD_ALIASES.length; i++) m.put(WOOD_ALIASES[i], Integer.valueOf(100));
  for (int i = 0; i < S_IDS.length; i++) m.put(S_IDS[i], Integer.valueOf(200 + i));
  ITEM = m;
  return m;
}""")
M(dfs, r"""
public static int wandIndex(String id) {
  if (id == null) return -1;
  Object o = items().get(id);
  int c = o instanceof Integer ? ((Integer) o).intValue() : -1;
  return c >= 100 && c < 200 ? c - 100 : -1;
}""")
M(dfs, r"""
public static int staffIndex(String id) {
  if (id == null) return -1;
  Object o = items().get(id);
  int c = o instanceof Integer ? ((Integer) o).intValue() : -1;
  return c >= 200 && c < 300 ? c - 200 : -1;
}""")
# THE damage rule of ArmoryTuneSys (spec 3.1 + 15.2), plain values only: 1 = untouched
M(dfs, r"""
public static double pctOf(double[] a, int i) {
  if (a == null || i < 0 || i >= a.length) return 1.0;
  return a[i] / 100.0;
}""")
M(dfs, r"""
public static float tuneFactor(String pid, boolean on, double[] wandPct, double[] staffPct, int quickPct) {
  if (!on) return 1.0f;
  int c = pidCode(pid);
  if (c < 0) return 1.0f;
  int i = c % 1000;
  double q = quickPct / (double) QUICK_SHARE_PCT;
  double f = 1.0;
  if (c >= 1000 && c < 2000) f = pctOf(wandPct, i) * q;
  else if (c >= 2000 && c < 3000) f = pctOf(wandPct, i);
  else if (c >= 3000 && c < 4000) f = pctOf(staffPct, i) * q;
  else if (c >= 4000 && c < 5000) f = pctOf(staffPct, i);
  return (float) f;
}""")
# THE spawn rule of ArmorySpawnSys (spec 2.3): null = leave the projectile alone, else { scale (0 = no scale component), speed factor,
# life in ms (0 = keep the vanilla despawn; fix round, spec R17: quick.life seconds, only when shorter than the vanilla 60 s) }
M(dfs, r"""
public static double[] spawnPlan(String pid, boolean spawn, boolean on, int sizePct, double speedX, String mode, int lifeS) {
  if (!spawn || !on || !isQuick(pid)) return null;
  double scale = 0.0;
  if ("scale".equals(mode) && sizePct > 0 && sizePct < 100) scale = sizePct / 100.0;
  double k = speedX / SPEED_X;
  if (!(k > 0.0) || Math.abs(k - 1.0) < 1e-9) k = 1.0;
  double life = 0.0;
  if (lifeS > 0 && (long) lifeS * 1000L < VANILLA_LIFE_MS) life = (double) lifeS * 1000.0;
  if (scale == 0.0 && k == 1.0 && life == 0.0) return null;
  return new double[] { scale, k, life };
}""")

# ---------------------------------------------------------------- ArmoryCfg: the settings (the config kit binds the fields)
TUNE_KEYS_W = ["tune.wand.%s" % m for m in METALS]
TUNE_KEYS_S = ["tune.staff.%s" % m for m in METALS]
CFG_FILE = "Skyy_SkyyArmory/config.properties"
CFG_LINES = [
    "# SkyyArmory %s - settings (SkyWynn Menu > Server Setup > Armory). Changes made in game are written here; after a hand edit use" % VERSION,
    "# Reload on that page. Mana costs, tap / hold keys and the art are fixed in the jar (the game client predicts them) - shown read-only there.",
    "",
    "# ---- damage",
    "# Damage tune: off = every wand and staff hits for its built-in numbers (the two % tables and quick shot damage are ignored).",
    "part.tune=true",
    "# Damage by wand (%): both shots of that wand x this % (100 = the built-in table). Wood = its quick shot only: its hold fires the shared",
    "# vanilla orb, which spellbooks, the staffs outside the ladder and Skeleton Mages use too.",
] + ["%s=100" % k for k in TUNE_KEYS_W] + [
    "# Damage by staff (%): both shots of that staff x this %.",
] + ["%s=100" % k for k in TUNE_KEYS_S] + [
    "",
    "# ---- quick shot (the tap)",
    "# Quick shot damage (% of the charged shot): 20 = 1/5 (built in). Scales quick-shot hits of wands and staffs only.",
    "quick.damage=20",
    "# Quick shot size / speed / reach: off = quick shots keep the built-in speed, full size and the vanilla %d s life." % (VANILLA_LIFE_MS // 1000),
    "part.spawn=true",
    "# Quick shot size (%% of the charged orb, 20-100). New shots only.",
    "quick.size=%d" % QUICK_SIZE_DEF,
    "# Quick shot speed (x the charged orb, 1-5; %d = built into the orb). New shots only." % SPEED_X,
    "quick.speed=%d" % SPEED_X,
    "# Quick shot reach (seconds, 1-%d): a quick orb that hits nothing vanishes after this long (%d = vanilla). New shots only." % (
        VANILLA_LIFE_MS // 1000, VANILLA_LIFE_MS // 1000),
    "quick.life=%d" % QUICK_LIFE_DEF,
    "",
    "# ---- Mana check (server log)",
    "# One INFO table at start and whenever SkyySkills' Mana rows change; a WARN for each weapon whose charged shot needs more than",
    "# check.share % of a Priest's (wands) / Mage's (staffs) max Mana at the weapon's first level (only the class skill levelled).",
    "check.on=true",
    "check.share=%d" % CHECK_SHARE_DEF,
]
CFG_TEXT = "\n".join(CFG_LINES) + "\n"
CFG_TEXT = CFG_TEXT.replace("(%% of", "(% of")
for f in ("public static java.nio.file.Path DIR;", "public static java.nio.file.Path FILE;",
          "public static volatile boolean PART_TUNE = true;", "public static volatile int QUICK_DAMAGE = 20;",
          "public static volatile boolean PART_SPAWN = true;", "public static volatile int QUICK_SIZE = %d;" % QUICK_SIZE_DEF,
          "public static volatile double QUICK_SPEED = %d.0;" % SPEED_X, "public static volatile int QUICK_LIFE = %d;" % QUICK_LIFE_DEF,
          "public static volatile boolean CHECK_ON = true;",
          "public static volatile int CHECK_SHARE = %d;" % CHECK_SHARE_DEF,
          "public static volatile double[] TUNE_W = %s;" % jdbls([100] * len(METALS)),
          "public static volatile double[] TUNE_S = %s;" % jdbls([100] * len(METALS)),
          "public static volatile String LOADED = \"\";",
          "public static final String DEF_CFG = %s;" % jtext(CFG_TEXT)):
    F(cfg, f)

# ================================================================= the config kit (Server Setup > Armory)
CFG_CATS = [("damage", "Damage"), ("quick", "Quick shot"), ("check", "Mana check"), ("wands", "Wands (fixed)"), ("staffs", "Staffs (fixed)")]


def fixed_wand(i):
    w = WT[i]
    if w[0] == "Wood":
        q = ("tap %d Mana, quick %d dmg" % (W_Q[0], W_QD[0])) if WOOD_QUICK else "tap = vanilla swing"
        return "%s | hold %d Mana (SkyySkills), vanilla orb %d dmg | Lv %d-%d" % (q, w[1], w[4], BANDS["Wood"][0], BANDS["Wood"][1])
    return "%d / %d Mana - x%s - %d / %d damage - Lv %d-%d" % (w[1], w[2], num(w[3]), w[4], w[5], BANDS[w[0]][0], BANDS[w[0]][1])


def fixed_staff(i):
    s = ST[i]
    if STAFF_TAP == "quick":
        return "%d / %d Mana - x%s - %d / %d damage - Lv %d-%d" % (s[1], s[2], num(s[3]), s[4], s[5], BANDS[s[0]][0], BANDS[s[0]][1])
    return "%d Mana (tap = spear swing) - x%s - %d damage - Lv %d-%d" % (s[1], num(s[3]), s[4], BANDS[s[0]][0], BANDS[s[0]][1])


FIXED = []     # (key, label, cat, value, help)
for _i, _m in enumerate(METALS):
    FIXED.append(("fixed.wand.%s" % _m, "%s (fixed in the jar)" % (WAND_NAMES.get(_m) or (_m + " Wand")), "wands", fixed_wand(_i),
                  "Charged / quick Mana, damage multiple, damage before levels, SkyyGear level band." if _m != "Wood" else
                  "The vanilla wand: SkyyArmory adds only its tap. Rotten and Tribal wands are the same."))
for _i, _m in enumerate(METALS):
    FIXED.append(("fixed.staff.%s" % _m, "%s (fixed in the jar)" % (STAFF_NAMES.get(_m) or (_m + " Staff")), "staffs", fixed_staff(_i),
                  "Charged / quick Mana (2x the wand), damage multiple, damage before levels, level band."))
FIXED.append(("fixed.quick", "Quick shot (fixed)", "quick",
              "%d blocks/s (%dx), wand tap %s s, staff tap %s s, look %s, size by %s, anim %s" % (
                  VORB["MuzzleVelocity"] * SPEED_X, SPEED_X, num(_wq), num(_sq), "blue" if QUICK_LOOK == "recolor" else "ice", QUICK_SIZE_MODE,
                  QUICK_ANIM), "Built into the jar: speed in the orb asset, the tap chain lengths, the look and the size path."))
FIXED.append(("fixed.art", "Wand art style", "wands", "%s - %s (LOCKED)" % (WAND_STYLE, SA.WAND_STYLES[WAND_STYLE]),
              "Skyy's pick (2026-10-02): every metal wand has a wood handle and a metal head."))
FIXED.append(("fixed.woodQuick", "Wood wand quick shot", "wands", "on - 1 Mana tap on the Wood, Rotten and Tribal wands" if WOOD_QUICK else "off",
              "The vanilla wand interaction Wand_Primary: tap = the 1-Mana quick shot instead of the free swing."))
FIXED.append(("fixed.staffTap", "Staff tap", "staffs", "quick shot (1/5 Mana, 1/5 damage)" if STAFF_TAP == "quick" else "vanilla spear swing",
              "What a short click on a ladder staff does (Skyy's question S2)."))
FIXED.append(("fixed.staffBase", "Staff damage base", "staffs", "%d (Wood staff charged shot)" % STAFF_BASE,
              "Skyy's question S1: 50 = staffs hit 2x like their 2x Mana; 25 = the vanilla orb."))
FIXED_VAL = dict((f[0], f[3]) for f in FIXED)
CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    ("part.tune", "Damage tune", "damage", "bool", "true", "", "", "", "", "live,part,danger",
     "Off = every wand and staff hits for its built-in numbers (the % tables + quick damage ignored).", "field:ArmoryCfg.PART_TUNE"),
    ("tune.wand", "Damage by wand (%)", "damage", "table", "", "10", "500", "int;none;Damage", "%", "live",
     "Both shots of that wand x this %. Wood: quick shot only (its hold is the shared vanilla orb).",
     "reload@%s:tune.wand.;check=ArmoryHooks.checkTune" % CFG_FILE),
    ("tune.staff", "Damage by staff (%)", "damage", "table", "", "10", "500", "int;none;Damage", "%", "live",
     "Both shots of that staff x this %.", "reload@%s:tune.staff.;check=ArmoryHooks.checkTune" % CFG_FILE),
    ("quick.damage", "Quick shot damage (% of charged)", "quick", "int", "20", "5", "100", "step=5", "%", "live",
     "20 = 1/5 of the charged shot (built in). Scales quick-shot hits only, wands and staffs.", "field:ArmoryCfg.QUICK_DAMAGE"),
    ("part.spawn", "Quick shot size / speed / reach", "quick", "bool", "true", "", "", "", "", "live,part,danger",
     "Off = quick shots keep the built-in speed, full size and the vanilla %d s life." % (VANILLA_LIFE_MS // 1000), "field:ArmoryCfg.PART_SPAWN"),
    ("quick.size", "Quick shot size (%)", "quick", "int", str(QUICK_SIZE_DEF), "20", "100", "step=5", "%",
     "new" if QUICK_SIZE_MODE == "scale" else "ro",
     "Size of the blue orb, % of the charged orb. New shots only. 100 = same size."
     if QUICK_SIZE_MODE == "scale" else "Fixed in the jar (a smaller orb model) in this build.",
     "field:ArmoryCfg.QUICK_SIZE" if QUICK_SIZE_MODE == "scale" else "custom:ArmoryHooks"),
    ("quick.speed", "Quick shot speed (x charged)", "quick", "dec", str(SPEED_X), "1", "5", "", "x", "new",
     "%d = Skyy's %dx (built into the orb). New shots only." % (SPEED_X, SPEED_X), "field:ArmoryCfg.QUICK_SPEED"),
    # fix round (spec R17): the reach - fewer orbs flying unseen for a minute (5 s = 450 blocks at the built-in speed)
    ("quick.life", "Quick shot reach (seconds)", "quick", "int", str(QUICK_LIFE_DEF), "1", str(VANILLA_LIFE_MS // 1000), "", "s", "new",
     "A quick orb that hits nothing vanishes after this long (%d = vanilla). New shots only." % (VANILLA_LIFE_MS // 1000),
     "field:ArmoryCfg.QUICK_LIFE"),
    ("check.on", "Mana check in the log", "check", "bool", "true", "", "", "", "", "live",
     "One INFO table at start and when SkyySkills' Mana rows change; a WARN per weapon over the share.", "field:ArmoryCfg.CHECK_ON"),
    ("check.share", "Mana check share (%)", "check", "int", str(CHECK_SHARE_DEF), "10", "100", "step=5", "%", "live",
     "Warn when a charged shot needs more than this share of a Priest's / Mage's Mana at its first level.", "field:ArmoryCfg.CHECK_SHARE"),
] + [(k, lab, cat, "text", val, "", "", "", "", "ro", hlp, "custom:ArmoryHooks") for k, lab, cat, val, hlp in FIXED]
_bad = ["%s help %d" % (r[0], len(r[10])) for r in CFG_ROWS if len(r[10]) > 100] + \
       ["%s label %d" % (r[0], len(r[1])) for r in CFG_ROWS if len(r[1]) > 40]
assert not _bad, "config row text too long: %s" % _bad
_dp = CFG.parse_props(CFG_TEXT)
for _r in CFG_ROWS:
    if _r[3] in ("bool", "int", "dec") and "ro" not in _r[9]:
        assert _dp.get(_r[0]) == _r[4], "default file and row default differ: %s (%r vs %r)" % (_r[0], _dp.get(_r[0]), _r[4])
assert all(_dp.get(k) == "100" for k in TUNE_KEYS_W + TUNE_KEYS_S)
kit = CFG.emit(pool, PKG, MOD=MOD, TITLE="Armory", VERSION=VERSION, NODE=NODE, CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=[CFG_FILE], NOTE="Tap = quick shot, hold = charged shot. Costs + art are fixed in the jar.",
               RELOAD="ArmoryCfg.reloadAll", KEEP=10, DEFAULTS={"config.properties": CFG_TEXT})

# ---------------------------------------------------------------- ArmoryCfg methods (the loader clamps like the kit validates)
M(cfg, r"""
public static boolean bool(String v, boolean def) {
  if (v == null) return def;
  String t = v.trim().toLowerCase();
  if (t.equals("true") || t.equals("on") || t.equals("yes") || t.equals("1")) return true;
  if (t.equals("false") || t.equals("off") || t.equals("no") || t.equals("0")) return false;
  return def;
}""")
M(cfg, r"""
public static int intOf(String v, int def, int lo, int hi) {
  if (v == null) return def;
  try {
    long x = Long.parseLong(v.trim());
    if (x < lo) return lo;
    if (x > hi) return hi;
    return (int) x;
  } catch (Throwable t) { return def; }
}""")
M(cfg, r"""
public static double dec(String v, double def, double lo, double hi) {
  if (v == null) return def;
  try {
    double x = Double.parseDouble(v.trim());
    if (Double.isNaN(x) || Double.isInfinite(x)) return def;
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
  } catch (Throwable t) { return def; }
}""")
M(cfg, r"""
public static java.util.Properties props(String text) {
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { }
  return p;
}""")
M(cfg, r"""
public static java.util.Properties read(java.nio.file.Path f) {
  if (f == null) return null;
  java.io.InputStream in = null;
  try {
    if (!java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) return null;
    in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    java.util.Properties p = new java.util.Properties();
    p.load(in);
    return p;
  } catch (Throwable t) {
    @PKG@.ArmoryLog.warn("could not read " + f + ": " + t + " - using the built-in defaults");
    return null;
  } finally {
    try { if (in != null) in.close(); } catch (Throwable t2) { }
  }
}""")
M(cfg, r"""
public static void seed(java.nio.file.Path f, String text) {
  if (f == null) return;
  try {
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
    java.nio.file.Path dir = f.getParent();
    if (dir != null) java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, text.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    @PKG@.ArmoryLog.info("wrote the default " + f.getFileName());
  } catch (Throwable t) { @PKG@.ArmoryLog.warn("could not write the default " + f + ": " + t); }
}""")
M(cfg, r"""
public static double[] table(java.util.Properties p, String prefix) {
  String[] ms = @PKG@.ArmoryDefs.METALS;
  double[] out = new double[ms.length];
  for (int i = 0; i < ms.length; i++) out[i] = (double) intOf(p.getProperty(prefix + ms[i]), 100, 10, 500);
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith(prefix)) continue;
    String e = k.substring(prefix.length());
    boolean known = false;
    for (int i = 0; i < ms.length; i++) if (ms[i].equals(e)) known = true;
    if (!known) @PKG@.ArmoryLog.warnOnce("tune:" + k, "config.properties: " + k + " is not a weapon of this table (" + prefix + "Wood ... Onyxium) - ignored");
  }
  return out;
}""")
M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {
  PART_TUNE = bool(c.getProperty("part.tune"), true);
  TUNE_W = table(c, "tune.wand.");
  TUNE_S = table(c, "tune.staff.");
  QUICK_DAMAGE = intOf(c.getProperty("quick.damage"), 20, 5, 100);
  PART_SPAWN = bool(c.getProperty("part.spawn"), true);
  QUICK_SIZE = intOf(c.getProperty("quick.size"), %d, 20, 100);
  QUICK_SPEED = dec(c.getProperty("quick.speed"), %d.0, 1.0, 5.0);
  QUICK_LIFE = intOf(c.getProperty("quick.life"), %d, 1, %d);
  CHECK_ON = bool(c.getProperty("check.on"), true);
  CHECK_SHARE = intOf(c.getProperty("check.share"), %d, 10, 100);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < TUNE_W.length; i++) if (TUNE_W[i] != 100.0) sb.append(sb.length() > 0 ? ", " : "").append(@PKG@.ArmoryDefs.METALS[i]).append(" wand ").append((int) TUNE_W[i]).append("%%");
  for (int i = 0; i < TUNE_S.length; i++) if (TUNE_S[i] != 100.0) sb.append(sb.length() > 0 ? ", " : "").append(@PKG@.ArmoryDefs.METALS[i]).append(" staff ").append((int) TUNE_S[i]).append("%%");
  LOADED = "damage tune " + (PART_TUNE ? "on" : "OFF") + (sb.length() > 0 ? " (" + sb.toString() + ")" : "") + ", quick shot " + QUICK_DAMAGE + "%% damage, "
    + (PART_SPAWN ? QUICK_SIZE + "%% size / " + QUICK_SPEED + "x speed / " + QUICK_LIFE + " s reach" : "size / speed / reach hook OFF") + ", Mana check " + (CHECK_ON ? "on (" + CHECK_SHARE + "%%)" : "off");
}""" % (QUICK_SIZE_DEF, SPEED_X, QUICK_LIFE_DEF, VANILLA_LIFE_MS // 1000, CHECK_SHARE_DEF))
M(cfg, r"""
public static void reloadAll() {
  java.util.Properties c = read(FILE);
  if (c == null) c = props(DEF_CFG);
  apply(c);
}""")
M(cfg, r"""
public static void load() {
  seed(FILE, DEF_CFG);
  reloadAll();
}""")
M(cfg, "public static void useDefaults() { apply(props(DEF_CFG)); }")
M(cfg, r"""
public static double tunePct(boolean staff, int i) {
  double[] a = staff ? TUNE_S : TUNE_W;
  if (a == null || i < 0 || i >= a.length) return 100.0;
  return a[i];
}""")

# ---------------------------------------------------------------- ArmoryHooks: the kit's check= hook and the read-only rows
F(hooks, "public static final String[] FIXED_KEYS = %s;" % jarr([f[0] for f in FIXED] + (["quick.size"] if QUICK_SIZE_MODE == "model" else [])))
F(hooks, "public static final String[] FIXED_VALS = %s;" % jarr([f[3] for f in FIXED] + (["%d (fixed)" % QUICK_SIZE_DEF] if QUICK_SIZE_MODE == "model" else [])))
M(hooks, r"""
public static String checkTune(String key, String value) {
  if (key == null) return null;
  int a = key.indexOf('[');
  int b = key.lastIndexOf(']');
  if (a < 0 || b < a) return null;
  String e = key.substring(a + 1, b);
  String[] ms = @PKG@.ArmoryDefs.METALS;
  for (int i = 0; i < ms.length; i++) if (ms[i].equals(e)) return null;
  if (value == null) return null;
  return "Not a weapon of this table - use Wood, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril or Onyxium.";
}""")
M(hooks, r"""
public static String customGet(String key) {
  for (int i = 0; i < FIXED_KEYS.length; i++) if (FIXED_KEYS[i].equals(key)) return FIXED_VALS[i];
  return null;
}""")
M(hooks, r"""
public static Object[] customSet(String key, String value) {
  return new Object[] { "bad", null, "Fixed in the jar - it changes only with a new SkyyArmory build." };
}""")

# ---------------------------------------------------------------- ArmorySpawn: the quick-orb hook's work (world thread, never throws)
for f in ("public static volatile java.lang.reflect.Field FPS = null;", "public static volatile boolean LOGGED = false;",
          "public static volatile String FIRST = \"\";", "public static volatile long SHOTS = 0L;"):
    F(spn, f)
M(spn, r"""
public static @VEC@ launchVelocity(@SPP@ sp) {
  if (sp == null) return null;
  try {
    java.lang.reflect.Field f = FPS;
    if (f == null) {
      f = Class.forName("@SPP@").getDeclaredField("forceProviderStandardState");
      f.setAccessible(true);
      FPS = f;
    }
    Object o = f.get(sp);
    if (!(o instanceof @FPSS@)) return null;
    @VEC@ v = ((@FPSS@) o).nextTickVelocity;
    if (v == null || !(v.x < Double.MAX_VALUE)) return null;
    return v;
  } catch (Throwable t) {
    @PKG@.ArmoryLog.warnOnce("spawnvel", "the quick shot speed row could not reach the launch velocity (" + t + ") - quick shots keep the built-in speed");
    return null;
  }
}""")
M(spn, r"""
public static double len(@VEC@ v) {
  return v == null ? -1.0 : Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}""")
# fix round (spec R17): the quick orb's reach - its DespawnComponent (vanilla: assembleDefaultProjectile's now + 60 s) moves to the world
# clock's now (the store's TimeResource) + lifeMs, never later than it was. Returns the remaining life in ms after the change (-1 = not
# changed: no store / clock / component, or the hook failed - the orb keeps the vanilla despawn). World thread, never throws.
M(spn, r"""
public static long shorten(@HOLD@ h, @ST@ st, double lifeMs) {
  if (h == null || st == null || !(lifeMs > 0.0)) return -1L;
  try {
    @TRS@ tr = (@TRS@) st.getResource(@TRS@.getResourceType());
    if (tr == null || tr.getNow() == null) return -1L;
    java.time.Instant cap = tr.getNow().plusMillis((long) lifeMs);
    @DSP@ dc = (@DSP@) h.getComponent(@DSP@.getComponentType());
    if (dc == null) {
      h.putComponent(@DSP@.getComponentType(), new @DSP@(cap));
    } else {
      java.time.Instant cur = dc.getDespawn();
      if (cur == null || cap.isBefore(cur)) dc.setDespawn(cap);
      else cap = cur;
    }
    return java.time.Duration.between(tr.getNow(), cap).toMillis();
  } catch (Throwable t) {
    @PKG@.ArmoryLog.warnOnce("spawnlife", "the quick shot reach row could not set the orb's despawn (" + t + ") - quick shots keep the vanilla life");
    return -1L;
  }
}""")
M(spn, r"""
public static void apply(@HOLD@ h, boolean spawn, @ST@ st) {
  if (h == null || !spawn) return;
  @LPC@ pc = null;
  try { pc = (@LPC@) h.getComponent(@LPC@.getComponentType()); } catch (Throwable t) { pc = null; }
  if (pc == null) return;
  String pid = pc.getProjectileAssetName();
  double[] plan = @PKG@.ArmoryDefs.spawnPlan(pid, spawn, @PKG@.ArmoryCfg.PART_SPAWN, @PKG@.ArmoryCfg.QUICK_SIZE, @PKG@.ArmoryCfg.QUICK_SPEED, @PKG@.ArmoryDefs.SIZE_MODE, @PKG@.ArmoryCfg.QUICK_LIFE);
  boolean quick = @PKG@.ArmoryDefs.isQuick(pid);
  if (quick) SHOTS = SHOTS + 1L;
  long left = -1L;
  if (plan != null) {
    if (plan[0] > 0.0) h.putComponent(@ESC@.getComponentType(), new @ESC@((float) plan[0]));
    if (plan[1] != 1.0) {
      @VEC@ v = launchVelocity(pc.getSimplePhysicsProvider());
      if (v != null) v.set(v.x * plan[1], v.y * plan[1], v.z * plan[1]);
    }
    if (plan[2] > 0.0) left = shorten(h, st, plan[2]);
  }
  if (quick && !LOGGED) {
    LOGGED = true;
    @VEC@ v2 = launchVelocity(pc.getSimplePhysicsProvider());
    String sc = "1 (full size)";
    try {
      @ESC@ e = (@ESC@) h.getComponent(@ESC@.getComponentType());
      if (e != null) sc = String.valueOf(e.getScale());
    } catch (Throwable t3) { }
    FIRST = "first quick orb after start: " + pid + " - scale " + sc + ", launch speed " + (v2 == null ? "unknown" : String.valueOf(Math.round(len(v2) * 100.0) / 100.0)) + " blocks/s (built in " + (30.0 * @PKG@.ArmoryDefs.SPEED_X) + ", row " + @PKG@.ArmoryCfg.QUICK_SPEED + "x), despawns in " + (left >= 0L ? String.valueOf(left / 1000.0) + " s (reach row " + @PKG@.ArmoryCfg.QUICK_LIFE + " s)" : "the vanilla " + (@PKG@.ArmoryDefs.VANILLA_LIFE_MS / 1000L) + " s");
    @PKG@.ArmoryLog.info(FIRST);
  }
}""")

# ---------------------------------------------------------------- ArmoryTuneSys (Filter group, BEFORE ArmorDamageReduction)
for f in ("public static Class ADR;", "public java.util.Set deps;", "public boolean ordered;"):
    F(tune, f)
C(tune, r"""
public ArmoryTuneSys(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  this.ordered = ordered && ADR != null;
  if (this.ordered) this.deps.add(new @SDEP@(@ORD@.BEFORE, ADR));
}""")
M(tune, "public @QRY@ getQuery() { return @QRY@.any(); }")
M(tune, "public @SG@ getGroup() { return @DMOD@.get().getFilterDamageGroup(); }")
M(tune, "public java.util.Set getDependencies() { return this.deps; }")
M(tune, r"""
public static String pidOf(@CB@ buf, @REF@ pr) {
  if (buf == null || pr == null || !pr.isValid()) return null;
  @LPC@ pc = (@LPC@) buf.getComponent(pr, @LPC@.getComponentType());
  return pc == null ? null : pc.getProjectileAssetName();
}""")
M(tune, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!@PKG@.ArmoryCfg.PART_TUNE || !(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled()) return;
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DPRJ@)) return;
    String pid = pidOf(buf, ((@DPRJ@) src).getProjectile());
    if (pid == null) return;
    float f = @PKG@.ArmoryDefs.tuneFactor(pid, true, @PKG@.ArmoryCfg.TUNE_W, @PKG@.ArmoryCfg.TUNE_S, @PKG@.ArmoryCfg.QUICK_DAMAGE);
    if (f != 1.0f) d.setAmount(d.getAmount() * f);
  } catch (Throwable t) { @PKG@.ArmoryLog.warnOnce("tune:" + t.getClass().getName(), "damage tune failed (" + t + ") - that hit kept its built-in damage"); }
}""")

# ---------------------------------------------------------------- ArmorySpawnSys (HolderSystem on projectiles, after the vanilla one)
for f in ("public static Class ONADD;", "public java.util.Set deps;", "public boolean ordered;"):
    F(spsys, f)
C(spsys, r"""
public ArmorySpawnSys(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  this.ordered = ordered && ONADD != null;
  if (this.ordered) this.deps.add(new @SDEP@(@ORD@.AFTER, ONADD));
}""")
M(spsys, "public @QRY@ getQuery() { return (@QRY@) @LPC@.getComponentType(); }")
M(spsys, "public java.util.Set getDependencies() { return this.deps; }")
M(spsys, r"""
public void onEntityAdd(@HOLD@ h, @ADDR@ why, @ST@ st) {
  try { @PKG@.ArmorySpawn.apply(h, why == @ADDR@.SPAWN, st); }
  catch (Throwable t) { @PKG@.ArmoryLog.warnOnce("spawn:" + t.getClass().getName(), "quick shot size / speed hook failed (" + t + ") - that orb keeps the built-in look"); }
}""")
M(spsys, "public void onEntityRemoved(@HOLD@ h, @REMR@ why, @ST@ st) { }")

# ---------------------------------------------------------------- ArmoryCheck: pack check + live read-back + Mana check (scheduler thread)
chk.addInterface(pool.get("java.lang.Runnable"))
for f in ("public static volatile int GEN = 0;", "public static volatile boolean STOP = false;", "public static volatile int TRIES = 0;",
          "public static volatile boolean PACK_DONE = false;", "public static volatile String PACK_LAST = \"\";",
          "public static volatile String MANA_LAST = \"\";", "public static volatile String MANA_SIG = \"\";",
          "public static volatile java.lang.reflect.Field RAW = null;", "public static volatile java.lang.reflect.Field RES = null;",
          "public static volatile java.lang.reflect.Field CRAW = null;", "public static volatile java.lang.reflect.Field CRES = null;",
          "public static volatile java.lang.reflect.Field KEYS = null;", "public static volatile java.lang.reflect.Field NEXT = null;",
          "public static final int START_S = 20;", "public static final int RETRY_S = 10;", "public static final int WATCH_S = 30;",
          "public static final int PACK_MAX = 6;", "public int gen;"):
    F(chk, f)
C(chk, "public ArmoryCheck(int gen) { this.gen = gen; }")
M(chk, r"""
public static java.lang.reflect.Field field(String cls, String name) throws Exception {
  java.lang.reflect.Field f = Class.forName(cls).getDeclaredField(name);
  f.setAccessible(true);
  return f;
}""")
# the live Mana check of a StatsCondition / the live spend of a ChangeStat (Mana index of the engine's resolved int map, the SkyySkills
# 0.4.9 liveCheck pattern): -1 not there / unreadable, -2 another type
M(chk, r"""
public static float liveCheck(Object a) {
  try {
    if (a == null) return -1.0f;
    if (!(a instanceof @SCB@)) return -2.0f;
    if (RES == null) RES = field("@SCB@", "costs");
    Object c = RES.get(a);
    if (!(c instanceof @I2F@)) return -4.0f;
    @I2F@ cm = (@I2F@) c;
    int mi = @DST@.getMana();
    if (!cm.containsKey(mi)) return -3.0f;
    return cm.get(mi);
  } catch (Throwable t) { return -1.0f; }
}""")
M(chk, r"""
public static float liveSpend(Object a) {
  try {
    if (a == null) return -1.0f;
    if (!(a instanceof @CSB@)) return -2.0f;
    if (CRES == null) CRES = field("@CSB@", "entityStats");
    Object c = CRES.get(a);
    if (!(c instanceof @I2F@)) return -4.0f;
    @I2F@ cm = (@I2F@) c;
    int mi = @DST@.getMana();
    if (!cm.containsKey(mi)) return -3.0f;
    return -cm.get(mi);
  } catch (Throwable t) { return -1.0f; }
}""")
M(chk, r"""
public static String keysOf(Object a) {
  try {
    if (!(a instanceof @CHI@)) return null;
    if (KEYS == null) KEYS = field("@CHI@", "sortedKeys");
    if (NEXT == null) NEXT = field("@CHI@", "next");
    float[] k = (float[]) KEYS.get(a);
    @F2O@ n = (@F2O@) NEXT.get(a);
    if (k == null || n == null) return null;
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < k.length; i++) {
      if (sb.length() > 0) sb.append(" ");
      sb.append(k[i]).append("=").append(String.valueOf(n.get(k[i])));
    }
    return sb.toString();
  } catch (Throwable t) { return null; }
}""")
M(chk, r"""
public static String launchOf(Object a) {
  if (!(a instanceof @LPI@)) return null;
  return ((@LPI@) a).getProjectileId();
}""")
M(chk, r"""
public static void wantInt(java.util.List bad, @DAM@ m, String id, int kind, float want) {
  Object a = null;
  try { a = m.getAsset(id); } catch (Throwable t) { a = null; }
  float got = kind == 0 ? liveCheck(a) : liveSpend(a);
  if (Math.abs(got - want) > 0.001f) bad.add(id + (kind == 0 ? " checks " : " spends ") + (got < 0.0f && got > -5.0f && got != -want ? "?(" + got + ")" : String.valueOf(got)) + " Mana, not " + want);
}""")
M(chk, r"""
public static void wantKeys(java.util.List bad, @DAM@ m, String id, String want, String tail) {
  Object a = null;
  try { a = m.getAsset(id); } catch (Throwable t) { a = null; }
  String got = keysOf(a);
  boolean ok = got != null && (want != null ? got.equals(want) : (got.startsWith("0.0=") && got.endsWith(tail)));
  if (!ok) bad.add(id + " keys " + got + ", not " + (want != null ? want : "0.0=<spear swing>" + tail));
}""")
M(chk, r"""
public static void wantLaunch(java.util.List bad, @DAM@ m, @DAM@ pm, String id, String pid, int dmg, double speed) {
  Object a = null;
  try { a = m.getAsset(id); } catch (Throwable t) { a = null; }
  String got = launchOf(a);
  if (got == null || !got.equals(pid)) { bad.add(id + " launches " + got + ", not " + pid); return; }
  Object p = null;
  try { p = pm.getAsset(pid); } catch (Throwable t) { p = null; }
  if (!(p instanceof @PRJ@)) { bad.add(pid + " is not a loaded projectile"); return; }
  @PRJ@ pr = (@PRJ@) p;
  if (pr.getDamage() != dmg || Math.abs(pr.getMuzzleVelocity() - speed) > 0.001) bad.add(pid + " damage " + pr.getDamage() + " / speed " + pr.getMuzzleVelocity() + ", not " + dmg + " / " + speed);
}""")
M(chk, r"""
public static int packOf(@DAM@ m, String[] ids, java.util.List other, java.util.List miss) {
  int mine = 0;
  for (int i = 0; i < ids.length; i++) {
    String p = null;
    try { p = m.getAssetPack(ids[i]); } catch (Throwable t) { p = null; }
    if (p == null) { miss.add(ids[i]); continue; }
    if (p.equals(@PKG@.ArmoryDefs.PACK)) { mine++; continue; }
    other.add(ids[i] + " (" + p + ")");
  }
  return mine;
}""")
M(chk, r"""
public static String head(java.util.List l, int n) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < l.size() && i < n; i++) { if (sb.length() > 0) sb.append(", "); sb.append(String.valueOf(l.get(i))); }
  if (l.size() > n) sb.append(", ...");
  return sb.toString();
}""")
# {level "info" / "warn" / "" (nothing readable yet - try again), message}
M(chk, r"""
public static String[] packCheck() {
  @DAM@ im = null;
  @DAM@ am = null;
  @DAM@ pm = null;
  try { im = @ITM@.getAssetMap(); } catch (Throwable t) { im = null; }
  try { am = @INT@.getAssetMap(); } catch (Throwable t) { am = null; }
  try { pm = @PRJ@.getAssetMap(); } catch (Throwable t) { pm = null; }
  if (im == null || am == null || pm == null) return new String[] { "", "the game's asset maps are not readable yet" };
  java.util.ArrayList other = new java.util.ArrayList();
  java.util.ArrayList miss = new java.util.ArrayList();
  int mi = packOf(im, @PKG@.ArmoryDefs.ITEM_CHECK, other, miss);
  int ma = packOf(am, @PKG@.ArmoryDefs.INT_CHECK, other, miss);
  int mp = packOf(pm, @PKG@.ArmoryDefs.PRJ_CHECK, other, miss);
  if (mi + ma + mp + other.size() == 0) return new String[] { "", "the game's assets could not be read" };
  java.util.ArrayList bad = new java.util.ArrayList();
  String[] ms = @PKG@.ArmoryDefs.METALS;
  for (int i = 0; i < ms.length; i++) {
    String m = ms[i];
    if (i > 0) {
      wantKeys(bad, am, "SkyyArmory_Wand_Primary_" + m, "0.0=SkyyArmory_Wand_Quick_" + m + " 0.35=SkyyArmory_Wand_Cast_" + m, null);
      wantInt(bad, am, "SkyyArmory_Wand_Cast_" + m, 0, (float) @PKG@.ArmoryDefs.W_C[i]);
      wantInt(bad, am, "SkyyArmory_Wand_Cast_Cost_" + m, 1, (float) @PKG@.ArmoryDefs.W_C[i]);
      wantLaunch(bad, am, pm, "SkyyArmory_Wand_Cast_Launch_" + m, @PKG@.ArmoryDefs.W_ORB[i], @PKG@.ArmoryDefs.W_CD[i], 30.0);
    }
    if (i > 0 || @PKG@.ArmoryDefs.WOOD_QUICK) {
      wantInt(bad, am, "SkyyArmory_Wand_Quick_" + m, 0, (float) @PKG@.ArmoryDefs.W_Q[i]);
      wantInt(bad, am, "SkyyArmory_Wand_Quick_Cost_" + m, 1, (float) @PKG@.ArmoryDefs.W_Q[i]);
      wantLaunch(bad, am, pm, "SkyyArmory_Wand_Quick_Launch_" + m, @PKG@.ArmoryDefs.W_QORB[i], @PKG@.ArmoryDefs.W_QD[i], 30.0 * @PKG@.ArmoryDefs.SPEED_X);
    }
    if (@PKG@.ArmoryDefs.STAFF_QUICK) wantKeys(bad, am, "SkyyArmory_Staff_Primary_" + m, "0.0=SkyyArmory_Staff_Quick_" + m + " 1.0=SkyyArmory_Staff_Cast_" + m, null);
    else wantKeys(bad, am, "SkyyArmory_Staff_Primary_" + m, null, " 1.0=SkyyArmory_Staff_Cast_" + m);
    wantInt(bad, am, "SkyyArmory_Staff_Cast_" + m, 0, (float) @PKG@.ArmoryDefs.S_C[i]);
    wantInt(bad, am, "SkyyArmory_Staff_Cast_Cost_" + m, 1, (float) @PKG@.ArmoryDefs.S_C[i]);
    wantLaunch(bad, am, pm, "SkyyArmory_Staff_Cast_Launch_" + m, @PKG@.ArmoryDefs.S_ORB[i], @PKG@.ArmoryDefs.S_CD[i], 30.0);
    if (@PKG@.ArmoryDefs.STAFF_QUICK) {
      wantInt(bad, am, "SkyyArmory_Staff_Quick_" + m, 0, (float) @PKG@.ArmoryDefs.S_Q[i]);
      wantInt(bad, am, "SkyyArmory_Staff_Quick_Cost_" + m, 1, (float) @PKG@.ArmoryDefs.S_Q[i]);
      wantLaunch(bad, am, pm, "SkyyArmory_Staff_Quick_Launch_" + m, @PKG@.ArmoryDefs.S_QORB[i], @PKG@.ArmoryDefs.S_QD[i], 30.0 * @PKG@.ArmoryDefs.SPEED_X);
    }
  }
  if (@PKG@.ArmoryDefs.WOOD_QUICK) wantKeys(bad, am, "Wand_Primary", "0.0=SkyyArmory_Wand_Quick_Wood 0.35=Wand_Cast_Left_Charged", null);
  String pre = "pack check: " + mi + " of " + @PKG@.ArmoryDefs.ITEM_CHECK.length + " items, " + ma + " of " + @PKG@.ArmoryDefs.INT_CHECK.length
    + " interactions, " + mp + " of " + @PKG@.ArmoryDefs.PRJ_CHECK.length + " projectiles come from " + @PKG@.ArmoryDefs.PACK;
  if (other.isEmpty() && miss.isEmpty() && bad.isEmpty())
    return new String[] { "info", pre + "; live read-back OK (tap / hold keys, Mana checks = spends, launches, projectile damage + speed match the tables)" };
  String w = pre;
  if (!other.isEmpty()) w = w + "; ANOTHER PACK WINS for " + other.size() + ": " + head(other, 8) + " (of two packs with the same asset the one loaded last wins - for the staffs: deploy SkyySkills 0.4.15 with SkyyArmory)";
  if (!miss.isEmpty()) w = w + "; NOT LOADED: " + head(miss, 8);
  if (!bad.isEmpty()) w = w + "; LIVE VALUES DIFFER: " + head(bad, 8);
  return new String[] { "warn", w };
}""")
# ---- the Mana check: SkyySkills' rows through its config bridge (read-only ops), SkyyGear's bands for the first levels
M(chk, r"""
public static Object cfgOp(String mod, Object[] op) {
  try {
    Object f = @PKG@.ArmoryDefs.bridge().get("config:fn:" + mod);
    if (!(f instanceof @FN@)) return null;
    return ((@FN@) f).apply(op);
  } catch (Throwable t) { return null; }
}""")
M(chk, r"""
public static String cfgGet(String mod, String key) {
  Object o = cfgOp(mod, new Object[] { "get", key });
  return o instanceof String ? (String) o : null;
}""")
M(chk, r"""
public static String tableVal(String mod, String table, String entry) {
  Object o = cfgOp(mod, new Object[] { "keys", table, "" });
  if (!(o instanceof Object[])) return null;
  Object[] r = (Object[]) o;
  if (r.length < 3 || !(r[0] instanceof String[]) || !(r[2] instanceof String[])) return null;
  String[] es = (String[]) r[0];
  String[] vs = (String[]) r[2];
  for (int i = 0; i < es.length && i < vs.length; i++) if (es[i] != null && es[i].equalsIgnoreCase(entry)) return vs[i];
  return null;
}""")
M(chk, r"""
public static double num(String v, double def) {
  if (v == null) return def;
  try {
    String t = v.trim();
    int b = t.indexOf('|');
    if (b >= 0) t = t.substring(0, b);
    return Double.parseDouble(t.trim());
  } catch (Throwable x) { return def; }
}""")
M(chk, r"""
public static int bandStart(int i) {
  String m = @PKG@.ArmoryDefs.METALS[i];
  String v = tableVal("SkyyGear", "level.material", m);
  if (m.equals("Wood") && v == null) v = tableVal("SkyyGear", "level.material", "Crude");
  int s = (int) num(v, (double) @PKG@.ArmoryDefs.BAND_A[i]);
  return s < 1 ? 1 : s;
}""")
M(chk, r"""
public static long epochOf(String mod) {
  Object o = @PKG@.ArmoryDefs.bridge().get("config:epoch:" + mod);
  return o instanceof Number ? ((Number) o).longValue() : -1L;
}""")
# {level "info" / "warn" / "skip", message}: the fighter's pool = base + per-level x L + Overall x floor(L / 9) + combat perk x L
M(chk, r"""
public static String[] manaCheck() {
  if (cfgOp("SkyySkills", new Object[] { "get", "mana.base" }) == null)
    return new String[] { "skip", "Mana check skipped: SkyySkills (its settings bridge) is not loaded" };
  boolean baseOn = !"false".equals(cfgGet("SkyySkills", "mana.base.enabled"));
  double baseAll = num(cfgGet("SkyySkills", "mana.base"), 10.0);
  double overall = num(cfgGet("SkyySkills", "overall.manaPerLevel"), 0.2);
  double combat = num(cfgGet("SkyySkills", "perk.combat.manaPerLevel"), 0.0);
  String[] cls = new String[] { "Priest", "Mage" };
  double[] base = new double[2];
  double[] per = new double[2];
  boolean[] hasRow = new boolean[2];
  for (int c = 0; c < 2; c++) {
    String b = tableVal("SkyySkills", "mana.classBase", cls[c]);
    base[c] = baseOn ? num(b, baseAll) : 0.0;
    String p = tableVal("SkyySkills", "mana.classPerLevel", cls[c]);
    hasRow[c] = p != null;
    per[c] = baseOn ? num(p, 0.0) : 0.0;
  }
  int share = @PKG@.ArmoryCfg.CHECK_SHARE;
  StringBuilder sb = new StringBuilder();
  java.util.ArrayList warn = new java.util.ArrayList();
  String[] ms = @PKG@.ArmoryDefs.METALS;
  int[] start = new int[ms.length];
  for (int i = 0; i < ms.length; i++) start[i] = bandStart(i);
  for (int c = 0; c < 2; c++) {
    sb.append(c == 0 ? "wands (Priest " : "; staffs (Mage ").append(Math.round(base[c] * 10.0) / 10.0).append(" + ").append(per[c]).append(c == 0 ? "/Divinity): " : "/Sorcery): ");
    for (int i = 0; i < ms.length; i++) {
      int L = start[i];
      double pool = base[c] + per[c] * L + overall * Math.floor(L / 9.0) + combat * L;
      int cost = c == 0 ? @PKG@.ArmoryDefs.W_C[i] : @PKG@.ArmoryDefs.S_C[i];
      double pct = pool > 0.0 ? cost * 100.0 / pool : 1000.0;
      if (i > 0) sb.append(", ");
      sb.append(ms[i]).append(" ").append(cost).append("/").append(Math.round(pool * 10.0) / 10.0).append(" ").append(Math.round(pct)).append("%");
      String w = (c == 0 ? ms[i] + " Wand" : ms[i] + " Staff") + " at " + (c == 0 ? "Divinity " : "Sorcery ") + L + ": " + cost + " of " + (Math.round(pool * 10.0) / 10.0) + " max Mana";
      if (cost > pool) warn.add(w + " - CANNOT be cast");
      else if (pct > share) warn.add(w + " (" + Math.round(pct) + "% > " + share + "%)");
    }
  }
  String lead = "Mana check (fighter = only the class skill levelled, at each weapon's first level; Overall " + overall + "/level" + (combat > 0.0 ? ", combat perk " + combat + "/level" : "") + (baseOn ? "" : ", Base Mana OFF") + "): ";
  if (warn.isEmpty()) return new String[] { "info", lead + sb.toString() + " - every charged shot within " + share + "%" };
  String need = (!hasRow[0] || !hasRow[1]) ? " SkyySkills has no 'Max Mana per class level' row (mana.classPerLevel) - it comes with SkyySkills 0.4.15." : "";
  return new String[] { "warn", lead + sb.toString() + " - OVER " + share + "%: " + head(warn, 10) + "." + need };
}""")
M(chk, r"""
public static void manaTick(boolean force) {
  if (!@PKG@.ArmoryCfg.CHECK_ON) { MANA_SIG = ""; return; }
  String sig = epochOf("SkyySkills") + "|" + epochOf("SkyyGear") + "|" + epochOf("SkyyArmory");
  if (!force && sig.equals(MANA_SIG)) return;
  MANA_SIG = sig;
  String[] r = manaCheck();
  MANA_LAST = r[1];
  try { @PKG@.ArmoryDefs.bridge().put("armory:check", r[1]); } catch (Throwable t) { }
  if ("warn".equals(r[0])) @PKG@.ArmoryLog.warn(r[1]);
  else @PKG@.ArmoryLog.info(r[1]);
}""")
M(chk, r"""
public static void schedule(Runnable r, int seconds) {
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(r, (long) seconds, java.util.concurrent.TimeUnit.SECONDS); }
  catch (Throwable t) { @PKG@.ArmoryLog.warnOnce("sched", "could not schedule the start checks (" + t + ") - no pack / Mana check this start"); }
}""")
M(chk, r"""
public void run() {
  if (STOP || this.gen != GEN) return;
  try {
    if (!PACK_DONE) {
      TRIES = TRIES + 1;
      String[] r = packCheck();
      if (r[0].length() > 0) {
        PACK_DONE = true;
        PACK_LAST = r[1];
        if ("warn".equals(r[0])) @PKG@.ArmoryLog.warn(r[1]);
        else @PKG@.ArmoryLog.info(r[1]);
      } else if (TRIES >= PACK_MAX) {
        PACK_DONE = true;
        PACK_LAST = "pack check gave up after " + TRIES + " tries: " + r[1];
        @PKG@.ArmoryLog.warn(PACK_LAST);
      }
    }
    manaTick(false);
  } catch (Throwable t) { @PKG@.ArmoryLog.warnOnce("check:" + t.getClass().getName(), "start checks failed: " + t); }
  if (!STOP && this.gen == GEN) schedule(this, PACK_DONE ? WATCH_S : RETRY_S);
}""")
M(chk, r"""
public static void start() {
  GEN = GEN + 1;
  STOP = false;
  TRIES = 0;
  PACK_DONE = false;
  MANA_SIG = "";
  schedule(new @PKG@.ArmoryCheck(GEN), START_S);
}""")

# ---------------------------------------------------------------- ArmoryInfoFn (armory:fn:info; any thread, never throws)
info.addInterface(pool.get(T["FN"]))
C(info, "public ArmoryInfoFn() { }")
M(info, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 2 || a[0] == null || a[1] == null) return null;
    String kind = String.valueOf(a[0]);
    String id = String.valueOf(a[1]);
    if (kind.equals("wand")) {
      int i = @PKG@.ArmoryDefs.wandIndex(id);
      if (i < 0) return null;
      return new Object[] { Integer.valueOf(@PKG@.ArmoryDefs.W_C[i]), Integer.valueOf(@PKG@.ArmoryDefs.W_Q[i]), Double.valueOf(@PKG@.ArmoryDefs.W_MULT[i]),
        Integer.valueOf(@PKG@.ArmoryDefs.W_CD[i]), Integer.valueOf(@PKG@.ArmoryDefs.W_QD[i]), Double.valueOf(@PKG@.ArmoryCfg.tunePct(false, i)),
        @PKG@.ArmoryDefs.W_ORB[i], @PKG@.ArmoryDefs.W_QORB[i] };
    }
    if (kind.equals("staff")) {
      int i = @PKG@.ArmoryDefs.staffIndex(id);
      if (i < 0) return null;
      return new Object[] { Integer.valueOf(@PKG@.ArmoryDefs.S_C[i]), Integer.valueOf(@PKG@.ArmoryDefs.S_Q[i]), Double.valueOf(@PKG@.ArmoryDefs.S_MULT[i]),
        Integer.valueOf(@PKG@.ArmoryDefs.S_CD[i]), Integer.valueOf(@PKG@.ArmoryDefs.S_QD[i]), Double.valueOf(@PKG@.ArmoryCfg.tunePct(true, i)),
        @PKG@.ArmoryDefs.S_ORB[i], @PKG@.ArmoryDefs.S_QORB[i] };
    }
    return null;
  } catch (Throwable t) { return null; }
}""")

# ---------------------------------------------------------------- the plugin
BRIDGE_KEYS = ["armory:wands", "armory:staffs", "armory:quick", "armory:fn:info", "armory:check", "gear:loot:add:SkyyArmory"]
C(pl, "public SkyyArmoryPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public static Class cls(String n) {
  try { return Class.forName(n); } catch (Throwable t) { return null; }
}""")
M(pl, r"""
public void systems() {
  @PKG@.ArmoryTuneSys.ADR = cls("%s");
  @PKG@.ArmorySpawnSys.ONADD = cls("%s");
  try { getEntityStoreRegistry().registerSystem(new @PKG@.ArmoryTuneSys(true)); }
  catch (Throwable t1) {
    @PKG@.ArmoryLog.warn("could not order the damage tune before armour (" + t1 + ") - unordered this start");
    try { getEntityStoreRegistry().registerSystem(new @PKG@.ArmoryTuneSys(false)); } catch (Throwable t2) { @PKG@.ArmoryLog.warn("the damage tune could not be registered: " + t2 + " - weapons hit for their built-in numbers"); }
  }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.ArmorySpawnSys(true)); }
  catch (Throwable t3) {
    @PKG@.ArmoryLog.warn("could not order the quick shot hook after the vanilla projectile setup (" + t3 + ") - unordered this start");
    try { getEntityStoreRegistry().registerSystem(new @PKG@.ArmorySpawnSys(false)); } catch (Throwable t4) { @PKG@.ArmoryLog.warn("the quick shot hook could not be registered: " + t4 + " - quick shots keep the built-in size and speed"); }
  }
}""" % (ADRS, ONADD))
M(pl, r"""
public static void publish() {
  java.util.Map b = @PKG@.ArmoryDefs.bridge();
  b.put("armory:wands", @PKG@.ArmoryDefs.WANDS_TEXT);
  b.put("armory:staffs", @PKG@.ArmoryDefs.STAFFS_TEXT);
  b.put("armory:quick", @PKG@.ArmoryDefs.QUICK_TEXT);
  b.put("armory:fn:info", new @PKG@.ArmoryInfoFn());
  b.put("armory:check", "");
  b.put("gear:loot:add:SkyyArmory", @PKG@.ArmoryDefs.LOOT_TEXT);
}""")
M(pl, r"""
public static void unpublish() {
  try {
    java.util.Map b = @PKG@.ArmoryDefs.bridge();
    String[] k = %s;
    for (int i = 0; i < k.length; i++) b.remove(k[i]);
  } catch (Throwable t) { }
}""" % jarr(BRIDGE_KEYS))
M(pl, r"""
public void setup() {
  @PKG@.ArmoryLog.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyArmory");
  @PKG@.ArmoryCfg.DIR = dir;
  @PKG@.ArmoryCfg.FILE = dir.resolve("config.properties");
  @PKG@.ArmoryCfg.load();
  @PKG@.ArmorySpawn.LOGGED = false;
  @PKG@.ArmorySpawn.FIRST = "";
  @PKG@.ArmorySpawn.SHOTS = 0L;
  systems();
  publish();
  @PKG@.ArmoryCheck.start();
  @PKG@.ArmoryLog.info("@VERSION@ ready - 7 metal wands (style %s) + the Wood wand tap (%s), 8 ladder staffs (%s; base %d); "
    + @PKG@.ArmoryCfg.LOADED + "; pack / live / Mana checks in " + @PKG@.ArmoryCheck.START_S + " s; settings in Server Setup > Armory (data in " + dir + ")");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""" % (WAND_STYLE, "1 Mana" if WOOD_QUICK else "off", "tap = quick shot, 2x wand Mana" if STAFF_TAP == "quick" else "tap = spear swing, 2x wand Mana",
        STAFF_BASE))
M(pl, r"""
protected void shutdown() {
  @PKG@.ArmoryCheck.STOP = true;
  unpublish();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  super.shutdown();
}""")

for c in ALL + [pl]:
    c.writeFile(OUT)
kit.write(OUT)
CLASSES = ALL + [pl]
print("classes written:", len(CLASSES) + len(kit.classes), "(%d kit)" % len(kit.classes))

# ================================================================= ACCESS AUDIT (SkyyUiProbe 0.3.1 lesson): what the JVM would refuse at RUN
# time with IllegalAccessError - javassist compiles a call to a protected / package-private member from any class and -Xverify:all does
# not catch it. Every class / member reference in the final class bytes is resolved here with the JVM's rules (the SkyyWorldGen 0.1 audit);
# the harness checks the same references again with MethodHandles.Lookup.
JConstPool = jpype.JClass("javassist.bytecode.ConstPool")
JClassFile, JDataIn, JByteIn = (jpype.JClass("javassist.bytecode.ClassFile"), jpype.JClass("java.io.DataInputStream"),
                                jpype.JClass("java.io.ByteArrayInputStream"))
AUDIT_OPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
             0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
             0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}


def class_file(data):
    return JClassFile(JDataIn(JByteIn(data)))


def audit_pkg(name):
    return name.rsplit(".", 1)[0] if "." in name else ""


def audit_elem(name):
    n = name.replace("/", ".").lstrip("[")
    if n.startswith("L") and n.endswith(";"):
        return n[1:-1]
    return None if len(n) == 1 and name.startswith("[") else n


def access_audit(items):
    refused, used, seen = [], set(), 0
    for D, cf in items:
        dn = str(D.getName())
        for mi in cf.getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it = mi.getConstPool(), ca.iterator()
            while it.hasNext():
                pos = it.next()
                op = it.byteAt(pos)
                if op not in AUDIT_OPS:
                    continue
                where = "%s.%s @%d %s" % (dn.rsplit(".", 1)[-1], mi.getName(), pos, AUDIT_OPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic (javassist never writes one)")
                    continue
                idx = it.byteAt(pos + 1) if op == 0x12 else it.u16bitAt(pos + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != JConstPool.CONST_Class:
                    continue
                if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                    cname, member = str(cp.getClassInfo(idx)), None
                elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                    cname, member = str(cp.getFieldrefClassName(idx)), ("field", str(cp.getFieldrefName(idx)), str(cp.getFieldrefType(idx)))
                elif tag == JConstPool.CONST_InterfaceMethodref:
                    cname, member = str(cp.getInterfaceMethodrefClassName(idx)), ("method", str(cp.getInterfaceMethodrefName(idx)),
                                                                                  str(cp.getInterfaceMethodrefType(idx)))
                else:
                    cname, member = str(cp.getMethodrefClassName(idx)), ("method", str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                seen += 1
                try:
                    en = audit_elem(cname)
                    if en is not None and audit_pkg(en) != audit_pkg(dn) and not JMod.isPublic(pool.get(en).getModifiers()):
                        refused.append("%s: class %s is not public - the JVM refuses it from %s (IllegalAccessError)" % (where, en, dn))
                    if member is None:
                        continue
                    kind, name, desc = member
                    Cc = pool.get("java.lang.Object" if cname.startswith("[") else cname)
                    if kind == "field":
                        x = Cc.getField(name, desc)
                    elif name == "<init>":
                        x = Cc.getConstructor(desc)
                    else:
                        x = Cc.getMethod(name, desc)
                    md, decl = x.getModifiers(), x.getDeclaringClass()
                    dcn = str(decl.getName())
                    if JMod.isPublic(md) or (audit_pkg(dcn) == audit_pkg(dn) and not JMod.isPrivate(md)):
                        continue
                    if JMod.isPrivate(md):
                        ok = dcn == dn
                    elif JMod.isProtected(md):
                        ok = bool(D.subclassOf(decl))
                    else:
                        ok = False
                    use = "%s %s.%s%s" % (JMod.toString(md), dcn, name, "" if kind == "field" else desc)
                    if ok:
                        used.add("%s.%s (from %s)" % (dcn.rsplit(".", 1)[-1], name, dn.rsplit(".", 1)[-1]))
                    else:
                        refused.append("%s: %s - the JVM refuses it from %s (IllegalAccessError)" % (where, use, dn))
                except Exception as e:
                    refused.append("%s: %s %s does not resolve: %s" % (where, cname, member, e))
    return refused, sorted(used), seen


_st = pool.makeClass(PKG + ".AccessAuditSelfTest")
M(_st, "public static void bad(@JP@ p) { p.setup(); }")
_st_refused, _st_used, _st_n = access_audit([(_st, class_file(_st.toBytecode()))])
_st.detach()
assert len(_st_refused) == 1 and "setup" in _st_refused[0] and "IllegalAccessError" in _st_refused[0], \
    "access audit self-test: a protected JavaPlugin.setup() call from a non-subclass must be refused: %s" % _st_refused
_items = []
for _cn in [str(c.getName()) for c in CLASSES] + [str(c.getName()) for c in kit.classes]:
    with open(os.path.join(OUT, *_cn.split(".")) + ".class", "rb") as _f:
        _items.append((pool.get(_cn), class_file(_f.read())))
AUDIT_REFUSED, AUDIT_USED, AUDIT_N = access_audit(_items)
if AUDIT_REFUSED:
    raise SystemExit("ACCESS AUDIT: %d reference(s) the JVM would refuse at run time (IllegalAccessError):\n  %s"
                     % (len(AUDIT_REFUSED), "\n  ".join(AUDIT_REFUSED)))
print("access audit: %d class / member references in %d classes, 0 the JVM would refuse; non-public engine members used: %s"
      % (AUDIT_N, len(_items), ", ".join(AUDIT_USED) or "none"))

# ================================================================= the jar
jar = os.path.join(OUT_DIR, "%s-%s.jar" % (MOD, VERSION))
man = B.manifest(MOD, VERSION, "SkyWynn armory: 7 metal Priest wands (Copper to Onyxium, tap = blue quick shot at 1/5 Mana, hold = charged "
                 "shot; Mana and damage per metal) + the Wood wand tap, and the Mage staff ladder (2x the wand's Mana). Recipes at the Weapon "
                 "Bench (Bow tab). Settings in game (Server Setup > Armory). Zero dependencies.", PKG + ".SkyyArmoryPlugin")
man["IncludesAssetPack"] = True
assert "%s:%s" % (man["Group"], man["Name"]) == PACK_KEY
B.assemble(jar, man, OUT, extra_files=ASSETS)
with zipfile.ZipFile(jar) as _jz:
    _names = _jz.namelist()
    _bad = [n for n in _names if n.lower().endswith(".ui")]
    if _bad:
        raise SystemExit("SkyyArmory jar must not ship .ui files: %s" % _bad)
    for _p, _t in ASSETS.items():
        _b = _jz.read(_p)
        assert _b == (_t if isinstance(_t, bytes) else _t.encode("utf-8")), "asset in the jar differs: " + _p
    _cls = [n for n in _names if n.endswith(".class")]
    assert len(_cls) == len(CLASSES) + len(kit.classes), (len(_cls), len(CLASSES), len(kit.classes))
    _sitems = sorted(n for n in _names if n.startswith("Server/Item/Items/Weapon/Staff/"))
    assert _sitems == sorted(P_SITEM % m for m in METALS), "SkyyArmory must ship all 8 ladder staff files (the handover): %s" % _sitems
    assert not [n for n in _names if os.path.basename(n)[:-5] in ("Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal")]
    assert not [n for n in _names if n.startswith("Server/Item/Interactions/") and os.path.basename(n)[:-5] in SKILLS_INTS]
print("ids: %d interactions (%s), %d roots, %d projectiles (%d quick), items %s" % (
    len(INTS), "incl. the Wand_Primary override" if WOOD_QUICK else "no Wand_Primary", len(ROOTS), len(PRJS), len(QUICK_IDS), ", ".join(sorted(ITEMS))))
print("bridge: armory:wands=%s" % WANDS_TEXT)
print("bridge: armory:staffs=%s" % STAFFS_TEXT)
print("bridge: armory:quick=%s" % QUICK_TEXT)
print("bridge: gear:loot:add:SkyyArmory=%s" % LOOT_TEXT)
print("switches: style %s, look %s, size %s, tap anim %s / %s, Wood quick %s, staff base %d (S1), staff tap %s (S2), Onyxium staff recipe %s (S3)" % (
    WAND_STYLE, QUICK_LOOK, QUICK_SIZE_MODE, QUICK_ANIM, STAFF_QUICK_ANIM, WOOD_QUICK, STAFF_BASE, STAFF_TAP, ONYX_STAFF_RECIPE))
AZ.close()
