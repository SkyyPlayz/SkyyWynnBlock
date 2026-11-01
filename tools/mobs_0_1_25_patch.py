"""Derive SkyyMobs/build_skyymobs_0.1.25.py from the GENERATED 0.1.24 (build_skyymobs_0.1.24.py = the tools/deploy_set.py SET pin, made by
tools/mobs_0_1_24_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.1.24
(tools/soundpass_gen.Patch); line endings kept.
Run:  python tools/mobs_0_1_25_patch.py   then   python SkyyMobs/build_skyymobs_0.1.25.py   then   python SkyyMobs/test_skyymobs_0.1.25.py
Edit THIS file, never the generated script (never --deploy).

0.1.25 (2026-11-01) = AUGMENTS ROUND A3 'sources + element mobs' (aug3), the SkyyMobs part (with SkyyMerchants 0.1.9 - T1 augments at the
  Traveling Merchant). research/Augments-Spec.md 6.1 row A3, 2.4 "Drops", 1d mob survey; Skyy (docs/answered/gear.md 2026-10-25, spec D13):
  "they drop the tier of the zone your in, so zone 3 drops T3 ... i want some mobs of every element in every zone. but i want a primary element
  per zone ... so zone 1 would be earth ... the earth augment drop chance would be higher there. even when fighting non elemental monsters";
  2026-10-30 "Allow x4.18" (the augment power is signed off). P0 X10 (tools/dev/scratch/aug0/P0-findings.md): spawn weights are build-time
  only; the element is per role (elem.mobs); the zone of a death = the environment's zone first, then the level (Armored / Veteran +1 / +2).
  1. AUGMENT DROPS (new class MobAug; SpoilsSys rolls it ONCE per death, after MobTheme, into the same list the Spoils spawn at the mob for
     the drop's owner). Only a levelled mob (a fighter: hostile / neutral fighters, pack mobs in rank.pack.mobs) or a boss rolls. The tier =
     the ZONE of the death (Env_Zone<N> environment first, else the level by bosses.zoneTops 20/40/60/80/100; above 5 = 5): stat kinds T1-T5,
     elements T1-T5 (T6-T10 only by fusing at SkyyGear's bench). Ids Skyy_Aug_<Kind>_<tier> (tools/tier_tags.py AUG_IDS; SkyyGear owns the
     items - Mobs only names them; an id the server lacks = counted, one WARN, nothing dropped).
     ELEMENT AUGMENT: one weighted roll a kill - each of the 5 elements weighs aug.drop.base (0.4 %) x aug.drop.elemMob (x3) when it is the
     mob's OWN element (Mob elements) x aug.drop.primary (x2) when it is the ZONE's element (aug.zoneElement.<zone>, even for non-elemental
     mobs); the sum is the chance of one element augment (capped at 100 %), the element picked by weight. Elites and mini bosses x
     aug.drop.eliteX (3). STAT AUGMENT (13 stat kinds, even odds; Poison stays craft-only, spec D16): elites aug.drop.statElite 2 %, mini bosses
     aug.drop.statMini 10 %. FULL BOSSES (Boss roles, pack bosses, rank boss): always aug.drop.bossStat (1) stat + aug.drop.bossElem (1)
     element augment (element by the same weights) + aug.drop.bossBonus (50 %) for one more element augment (spec: "bosses 1-2").
     Rates at the defaults: an ordinary Zone 1 mob 2.4 % (Earth 0.8, each other 0.4); a Zone 1 Earth mob 4.0 % (Earth 2.4); its elite 12 %.
  2. ZONE ELEMENT (spec N3 defaults: Z1 Earth, Z2 Thunder, Z3 Water, Z4 Fire, Z5 Air; rows aug.zoneElement.1..5, editable, "none" = no
     primary) + "most commons are the zone element": NEW row elem.zoneVariants (on) - an Armored / Veteran tougher version
     (<Role>_SkyyArmored<zone> / _SkyyVeteran<zone>, 0.1.22: 40 + 20 % of their families' spawns) whose vanilla role has NO Mob elements row
     takes its zone's element (MobElem.zoneOwn: plates, weak / resist, its hits' element share + states, mob:fn:elem / elemOf for SkyyGear /
     SkyyClasses - all role-based, so every reader agrees). A role WITH a row (Skeleton_Sand* = Earth ...) keeps it; "X=none" stays none.
     Spawn weights stay build-time and untouched (no spawn file changes; the jar's role / model / spawn files are byte-identical).
     aug3fix (critic: "some mobs of every element in every zone"): NEW row elem.zoneMix (60 %) - the zone element goes to the tougher versions
     making up ~60 % of the element-less ones' world spawns; the rest take the 4 other elements in turn (a build-time table MobElem.ZM_IDS /
     ZM_U / ZM_O, mirrored by aug_elem_of + the report). 100 = all take the zone element, 0 = none. aug3fix2 (critic: every element in EVERY
     zone, the zone element most of the commons): the zone element takes the MOST-spawned versions, the 4 lightest always another element.
     At 60 (roles / % of their spawns): Zone 1 Earth 5 / 61 + 4-5 roles of each other; Zone 3 Water 3 / 63 + Earth 3, Thunder / Fire / Air 2;
     Zone 4 Fire 2 / 71 + 1 of each other; Zone 2 has none (all its tougher versions are Sand = Earth rows -> Fire / Air missing there, asked).
     On land (fish files left out - Piranha live in the water) the zone element leads the elemental fighters (asserted): Zone 1 Earth 38 %,
     Zone 3 Water 97 %, Zone 4 Fire 97 %. Element-less vanilla commons (plain skeletons ...) stay element-less. Zone 5 has no vanilla spawns yet.
  3. MORE ELEMENT BODIES (the Mob elements default grows; spec 1d table): vanilla Crocodile = Water (the hostile lake / river predator with
     Piranha*, already Water), Lizard_Sand = Earth, Slug_Magma / Snail_Magma / Shellfish_Lava = Fire, Snail_Frost = Water, Tang_Lemon_Peel =
     Water, Bat = Air; and the PACK mod Slime Mobs! (lizard / bigfknlizard, MIT; by role id at runtime only, nothing of theirs copied):
     Green_Slime = Earth (Zone 1 plains / forests / swamps), Yellow_Slime = Thunder (Zone 2 deserts / savanna), Water_Slime = Water (shores of
     Zones 1-3), Ice_Slime = Water (Zone 3; Chill is a Water state, like Spirit_Frost), Fire_Slime / Bomb_Slime = Fire (Zone 4 / Zone 2 caves),
     Ghost_Slime = Air (caves of Zones 1, 3, 4). Their roles get band levels (rank.pack.mobs default + the 8 exact slime ids incl. King_Slime -
     aug3fix: not "*_Slime", which also matched Better Mob Expansion's BME_Slime; asserted against vanilla + every other installed mod) so
     they roll augments like any fighter. A config.properties that already HOLDS an elem.mobs / rank.pack.mobs line keeps it (no migration;
     Skyy's NewBetaTest has neither line, so the new defaults apply there).
  4. SERVER SETUP > Mobs > Augments (new tab, 15 rows, live) + Elements > "Tougher versions take the zone element" + "Tougher versions in
     the zone element" (%). New keys only: a
     file without the line = the default (NO one-time update). Ready line: + "augment drops ...".
  ZONE 2 NOTE (build report): Zone 2's world-spawn fighters are Sand skeletons (Mob elements row Earth), so its tougher versions keep Earth
  and Thunder (the N3 default) comes only from Yellow slimes (pack), Spirit_Thunder (elemental circles) and the x2 drop - Skyy's call (N3).
  GAPS (not built - new bodies, spec 1d (3)): a hostile Air flyer (vanilla Pterodactyl / Bat / Vulture are passive bird templates; Bat has no
  attack animation) and a hostile Water mob in Zone 4 lakes (vanilla Piranha / Crocodile / Water slimes cover Zones 1-3). Thunder flyer =
  vanilla Spirit_Thunder (hostile, Zone 2 elemental circles, already Thunder).
  SAVED DATA: none. One new class MobAug; no new system / command / bridge key. aug3fix: SpoilsSys wraps the augment roll in its own catch
  (one WARN "the augment drops failed") so a failure there never skips the dragon egg, the spawn or the secret finds.
  COMBAT NOTE: element-less tougher versions now HAVE an element (weak / resist +-25 %, part of their hits elemental) - elem.zoneVariants off
  is the one switch back (plates and fights revert at once).
  ROLLBACK to 0.1.24: alone is safe (no saved data; the 17 new rows are ignored; augments already dropped stay SkyyGear items; tougher versions
  lose their zone element; slimes lose their level and element).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import tier_tags as TT

P = G.Patch(os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.24.py"), os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.25.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.1.24"') and P.s.startswith('"""SkyyMobs 0.1.24 - build script') and P.has("MobTheme") and not P.has("MobAug"), "not the SET pin 0.1.24"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")
HEAD = open(os.path.abspath(__file__), encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.25 (2026-11-01)"):].rstrip() + "\n\n"

# the augment ids (tools/tier_tags.py = SkyyGear's own list): 13 stat kinds T1-T5, 5 elements T1-T10, Poison T1-T5
AUG_STAT = [k for k in TT.AUG_KINDS if TT.AUG_TIERS[k] == 5 and k != "Poison"]
AUG_ELEM = [k for k in TT.AUG_KINDS if TT.AUG_TIERS[k] == 10]
assert len(AUG_STAT) == 13 and AUG_ELEM == ["Earth", "Thunder", "Water", "Fire", "Air"] and len(TT.AUG_IDS) == 120
assert all("Skyy_Aug_%s_%d" % (k, n) in TT.AUG_IDS for k in AUG_STAT + AUG_ELEM for n in range(1, 6)), "every zone tier id exists"
ZONE_ELEM_DEF = ["Earth", "Thunder", "Water", "Fire", "Air"]          # spec 2.4 / N3 (Zone 1 = Earth is Skyy's words)

P.rep('''"""SkyyMobs 0.1.24 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_24_patch.py from the SET pin 0.1.23 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.24.py -> SkyyMobs/SkyyMobs-0.1.24.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.24.py
''', '''"""SkyyMobs 0.1.25 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_25_patch.py from the SET pin 0.1.24 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.25.py -> SkyyMobs/SkyyMobs-0.1.25.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.25.py
''' + NOTE)
P.rep('VERSION = "0.1.24"', 'VERSION = "0.1.25"')

# ---------- 3. more element bodies (vanilla + the Slime Mobs! pack roles) - after the 0.1.17 checks, before any use of the default
ELEM_A3 = '''# 0.1.25 (aug3, Augments-Spec 1d): more element bodies - vanilla (asserted in Assets.zip) + the PACK mod Slime Mobs! (lizard / bigfknlizard,
# MIT; by role id at runtime only - their files are never copied; checked against the installed zip when it is there, read-only)
ELEM_A3_VAN = [("Crocodile", "Water"), ("Lizard_Sand", "Earth"), ("Slug_Magma", "Fire"), ("Snail_Magma", "Fire"), ("Shellfish_Lava", "Fire"),
               ("Snail_Frost", "Water"), ("Tang_Lemon_Peel", "Water"), ("Bat", "Air")]
ELEM_A3_PACK = [("Green_Slime", "Earth"), ("Yellow_Slime", "Thunder"), ("Water_Slime", "Water"), ("Ice_Slime", "Water"), ("Fire_Slime", "Fire"),
                ("Bomb_Slime", "Fire"), ("Ghost_Slime", "Air")]
for _r in ELEM_A3_VAN:
    assert _r[0] in VANILLA, "0.1.25: %s is not a vanilla role" % _r[0]
    assert elem_row(_EROWS, _r[0]) is None, "0.1.25: %s already has an element row" % _r[0]
for _r in ELEM_A3_PACK:
    assert not any(glob(_r[0], _n) for _n in VANILLA) and elem_row(_EROWS, _r[0]) is None, "0.1.25: pack role %s clashes" % _r[0]
SLIME_ROLES = None          # the installed Slime Mobs! zip (read-only check; absent on a machine without it)
for _sz in sorted(os.listdir(B.MODS_DIR)) if os.path.isdir(B.MODS_DIR) else []:
    if _sz.lower().startswith("slimemobs") and _sz.lower().endswith((".zip", ".jar")):
        with zipfile.ZipFile(os.path.join(B.MODS_DIR, _sz)) as _zf:
            SLIME_ROLES = (_sz, sorted(os.path.basename(_n)[:-5] for _n in _zf.namelist() if _n.startswith("Server/NPC/Roles/") and _n.endswith(".json")
                                       and "/_Core/" not in _n and "/Templates/" not in _n),
                           dict((_n, _zf.read(_n).decode("utf-8-sig", "replace")) for _n in _zf.namelist() if _n.startswith("Server/NPC/Spawn/World/") and _n.endswith(".json")))
if SLIME_ROLES is not None:
    assert all(_r[0] in SLIME_ROLES[1] for _r in ELEM_A3_PACK), "0.1.25: a tagged slime role is not in %s: %s" % (SLIME_ROLES[0], SLIME_ROLES[1])
    print("0.1.25 Slime Mobs! (%s, read-only): roles %s" % (SLIME_ROLES[0], ", ".join(SLIME_ROLES[1])))
else:
    print("0.1.25 Slime Mobs! not installed here - its role ids are tagged by name only (UNVERIFIED against the zip)")
ELEM_ROWS = ELEM_ROWS + ELEM_A3_VAN + ELEM_A3_PACK
ELEM_MOBS_DEF = ", ".join("%s=%s" % _r for _r in ELEM_ROWS)
_EROWS = elem_parse(ELEM_MOBS_DEF)
assert len(_EROWS) == len(ELEM_ROWS) and len(ELEM_MOBS_DEF) <= 2000 and all(ord(_c) < 127 for _c in ELEM_MOBS_DEF)
for _r in _EROWS:          # elem1fix: still the pure wheel except the four "ice melts" rows (no new exception for SkyyMenu's chart)
    if _r[2]:
        assert _r[3] == _r[2] and (_r[4] == EL.beats(_r[2])) != (_r[0] in [_x.lower() for _x in _ICE]), "0.1.25: %s off the wheel" % _r[0]
print("0.1.25 elements: %d elem.mobs rows (%d chars; + %d vanilla, + %d Slime Mobs! roles)" % (len(ELEM_ROWS), len(ELEM_MOBS_DEF), len(ELEM_A3_VAN), len(ELEM_A3_PACK)))
'''
P.rep('''print("0.1.17 elements: %d elem.mobs rows (%d chars), %d vanilla roles with an own element" % (len(ELEM_ROWS), len(ELEM_MOBS_DEF), len(_elem_cover)))
''', '''print("0.1.17 elements: %d elem.mobs rows (%d chars), %d vanilla roles with an own element" % (len(ELEM_ROWS), len(ELEM_MOBS_DEF), len(_elem_cover)))
''' + ELEM_A3)
# the slimes get band levels (Pack mobs that get levels)
P.rep('''PACK_MOBS_DEF = "Sv2_Bandit_Minion*, Sv2_Ship_*"
''', '''# 0.1.25 (aug3): + the Slime Mobs! roles BY NAME (band levels -> augment drops). aug3fix: exact ids, not "*_Slime" - that also matched Better
# Mob Expansion's BME_Slime / BME_Slime_Red (the critic); asserted against vanilla and every OTHER mod in the Mods folder (read-only)
SLIME_LEVEL = ["Green_Slime", "Yellow_Slime", "Water_Slime", "Ice_Slime", "Fire_Slime", "Bomb_Slime", "Ghost_Slime", "King_Slime"]
PACK_MOBS_DEF = "Sv2_Bandit_Minion*, Sv2_Ship_*, " + ", ".join(SLIME_LEVEL)
assert not [_n for _n in VANILLA if _n in SLIME_LEVEL], "0.1.25: a Slime Mobs! role id is also a vanilla role"
_slime_other = []
for _sz in sorted(os.listdir(B.MODS_DIR)) if os.path.isdir(B.MODS_DIR) else []:
    if _sz.lower().endswith((".zip", ".jar")) and not _sz.lower().startswith("slimemobs"):
        try:
            with zipfile.ZipFile(os.path.join(B.MODS_DIR, _sz)) as _zf:
                _slime_other += ["%s: %s" % (_sz, _n) for _n in _zf.namelist() if _n.startswith("Server/NPC/Roles/") and _n.endswith(".json")
                                 and os.path.basename(_n)[:-5] in SLIME_LEVEL]
        except zipfile.BadZipFile:
            pass
assert not _slime_other, "0.1.25: another mod ships a role with a Slime Mobs! id: %s" % _slime_other
''')

# ---------- 1 + 2 + 4: the rows (build time), the per-zone element report
AUGR = [("aug.drop.on", "Augment drops", "bool", "true", "", "", "", "", "Mobs drop augments (SkyyGear items) of the zone's tier: Zone 3 = T3.", "AUG_ON"),
        ("aug.drop.base", "Element augment base chance", "dec", "0.4", "0", "100", "", "%",
         "Per kill, per element (5). One roll a kill: at most one element augment.", "AUG_BASE"),
        ("aug.drop.elemMob", "Own element x", "dec", "3", "1", "20", "", "x",
         "An element mob (Mob elements) drops its OWN element this many times more often.", "AUG_EMOB"),
        ("aug.drop.primary", "Zone element x", "dec", "2", "1", "20", "", "x",
         "The zone's element (below) drops this many times more often - from any mob there.", "AUG_PRIM"),
        ("aug.drop.eliteX", "Elite / mini boss element x", "dec", "3", "1", "20", "", "x",
         "Elites and mini bosses roll the element chances x this (capped at 100 %).", "AUG_ELITE"),
        ("aug.drop.statElite", "Elite: stat augment chance", "dec", "2", "0", "100", "", "%",
         "An elite's chance of one stat augment (Brute, Bulwark ...) of the zone's tier.", "AUG_SELITE"),
        ("aug.drop.statMini", "Mini boss: stat augment chance", "dec", "10", "0", "100", "", "%",
         "A mini boss's chance of one stat augment of the zone's tier.", "AUG_SMINI"),
        ("aug.drop.bossStat", "Boss: stat augments", "int", "1", "0", "5", "", "",
         "A full boss always drops this many stat augments (zone tier).", "AUG_BSTAT"),
        ("aug.drop.bossElem", "Boss: element augments", "int", "1", "0", "5", "", "",
         "A full boss always drops this many element augments (picked by the weights above).", "AUG_BELEM"),
        ("aug.drop.bossBonus", "Boss: one more element chance", "dec", "50", "0", "100", "", "%",
         "Chance a full boss drops one more element augment (bosses drop 1-2).", "AUG_BBONUS")]
AUGR += [("aug.zoneElement.%d" % _z, "Zone %d element" % _z, "text", ZONE_ELEM_DEF[_z - 1], "", "10", "", "",
          "Zone %d's main element: drops x Zone element x; tougher versions take it. Or none." % _z, "AUG_Z%d" % _z) for _z in range(1, 6)]
ZVAR_ROW = ("elem.zoneVariants", "Tougher versions take the zone element", "elem", "bool", "true", "", "", "", "", "live",
            "Armored / Veteran mobs with no Mob elements row get their zone's element (Augments tab).",
            "field:MobCfg.ELEM_ZVAR;after=MobCfg.elemEdit")
# aug3fix (critic: "some mobs of every element in every zone"): the zone element goes to elem.zoneMix % of a zone's element-less tougher
# versions, the rest take the 4 other elements in turn (a build-time table, so MobElem.zoneOwn, aug_elem_of and the report all agree)
ZMIX_ROW = ("elem.zoneMix", "Tougher versions in the zone element", "elem", "int", "60", "0", "100", "", "%", "live",
            "Share of element-less tougher versions that take the zone element; the rest get the other 4 in turn.",
            "field:MobCfg.ELEM_ZMIX;after=MobCfg.elemEdit")
ZMIX_DEF = int(ZMIX_ROW[4])
DEF = '''# 0.1.25 (aug3): the augment drop rows (Server Setup > Mobs > Augments; MobAug, rolled by SpoilsSys) + the per-zone element report
AUG_ROW = %r
ZVAR_ROW = %r
ZMIX_ROW = %r
AUG_STAT_KINDS = %r
AUG_ELEM_KINDS = %r
assert AUG_ELEM_KINDS == list(EL.NAMES), "0.1.25: the augment elements are MobElem.NAMES (Wynn order)"
assert all(len(_r[1]) <= 40 and len(_r[8]) <= 100 for _r in AUG_ROW), [(len(_r[1]), len(_r[8])) for _r in AUG_ROW]
_AUG_ZE = dict((int(_r[0].rsplit(".", 1)[1]), _r[3]) for _r in AUG_ROW if _r[0].startswith("aug.zoneElement."))
ZMIX_DEF = int(ZMIX_ROW[4])


def _jhash(s):          # = java.lang.String.hashCode (a stable shuffle of each zone's tougher versions)
    _h = 0
    for _c in s:
        _h = (31 * _h + ord(_c)) & 0xFFFFFFFF
    return _h


# the zone-mix table (aug3fix): per zone, its tougher versions WITHOUT a Mob elements row at the defaults, in a stable shuffled order; the
# i-th gets u = the middle of its share of their world-spawn WEIGHT (zone element when u * 100 < elem.zoneMix: so the %% is of the spawns,
# not of the role count) and o = (n - 1 - i) %% 4 = the o-th of the 4 OTHER elements (wheel order without the zone's) - counted from the
# end, so any 4 in a row that miss the zone element cover all 4 others
# aug3fix2 (critic: every element in EVERY zone + the zone element = most commons): HEAVIEST first, so the zone element takes the most-spawned
# versions and the other elements the light ones; and the min(4, n - 1) lightest always sit at / above the default mix (u >= ZMIX_DEF + a
# hair), so at the default every zone with 5+ element-less tougher versions has a role of each of the 4 other elements
_ZMW = {}
for _k, _d in sorted(_SP_ALL.items()):
    if _k.startswith("Void/"):
        continue
    for _e in _d.get("NPCs", []):
        if _e["Id"] in VAR_IDS:
            _ZMW[_e["Id"]] = _ZMW.get(_e["Id"], 0.0) + float(_e.get("Weight", 1))
ZMIX = {}
for _z in sorted(set(_v[2] for _v in VAR_IDS.values())):
    _vl = sorted([_v for _v in VAR_IDS if VAR_IDS[_v][2] == _z and elem_row(_EROWS, VAR_IDS[_v][0]) is None], key=lambda _x: (-_ZMW.get(_x, 0.0), _jhash(_x), _x))
    _wt = [max(_ZMW.get(_v, 0.0), 1e-6) for _v in _vl]
    _kt = min(4, len(_vl) - 1) if len(_vl) > 1 else 0
    _c = 0.0
    for _i, _v in enumerate(_vl):
        _u = (_c + _wt[_i] / 2.0) / sum(_wt)
        if _i >= len(_vl) - _kt:          # aug3fix2: the coverage tail (the lightest) stays off the zone element at the default
            _u = max(_u, ZMIX_DEF / 100.0 + 0.001 * (_i - len(_vl) + _kt + 1))
        ZMIX[_v] = (round(_u, 6), (len(_vl) - 1 - _i) %% 4)
        _c += _wt[_i]
    assert all(0.0 < ZMIX[_v][0] < 1.0 for _v in _vl)
ZMIX_IDS = sorted(ZMIX)
assert all(ord(_c) < 127 for _x in ZMIX_IDS for _c in _x), "0.1.25: ASCII ids (Java String order = Python's)"


def zmix_elem(role, pr, mix):
    """MobElem.zoneOwn mirror: the element (name) a tougher version without a row takes with zone element pr at elem.zoneMix = mix"""
    if not pr or pr == "none":
        return None
    _u, _o = ZMIX.get(role, (0.0, 0))
    if _u * 100.0 < mix:
        return pr
    return [_e for _e in AUG_ELEM_KINDS if _e != pr][_o]


def aug_elem_of(role, mix=None):
    """the element a role fights with at the defaults (MobElem.ownOf mirror): its row, else a tougher version's zone-mix element, else None"""
    _r = elem_row(_EROWS, VAR_IDS[role][0] if role in VAR_IDS else role)
    if _r is not None:
        return _r[2] or None
    return zmix_elem(role, _AUG_ZE.get(VAR_IDS[role][2]), ZMIX_DEF if mix is None else mix) if role in VAR_IDS else None


_aug_cov = {}
_aug_land = {}          # aug3fix2: the same without the fish / shore-water files (Piranha ... live in the lakes and rivers, Skyy's own wish)
for _k, _d in sorted(_SP_ALL.items()):
    for _env in _d.get("Environments", []):
        _zs = _env[4:9] if _env.startswith("Env_Zone") else ""
        if len(_zs) != 5 or not _zs[4].isdigit() or _k.startswith("Void/"):          # the night void invasions (*Void* = Thunder) are counted apart
            continue
        for _e in _d.get("NPCs", []):
            if _e["Id"] not in VAR_IDS and _e["Id"] not in FIGHTERS:
                continue
            _b = _aug_cov.setdefault(int(_zs[4]), {})
            _el = aug_elem_of(_e["Id"]) or "none"
            _b[_el] = _b.get(_el, 0.0) + float(_e.get("Weight", 1))
            if "_Fish" not in _k:
                _bl = _aug_land.setdefault(int(_zs[4]), {})
                _bl[_el] = _bl.get(_el, 0.0) + float(_e.get("Weight", 1))
if SLIME_ROLES is not None:          # the pack's world spawns (read-only, the installed zip), weights as written there
    for _n, _t in sorted(SLIME_ROLES[2].items()):
        _d = lenient(_t)
        for _env in _d.get("Environments", []):
            if _env.startswith("Env_Zone") and _env[8:9].isdigit():
                for _e in _d.get("NPCs", []):
                    _el = aug_elem_of(_e["Id"]) or "none"
                    _b = _aug_cov.setdefault(int(_env[8]), {})
                    _b["pack " + _el] = _b.get("pack " + _el, 0.0) + float(_e.get("Weight", 1))
AUG_COVER = {}
for _z in sorted(_aug_cov):
    _b = _aug_cov[_z]
    _tot = sum(_v for _k2, _v in _b.items() if not _k2.startswith("pack "))
    _per = {}
    for _k2, _v in _b.items():
        _per[_k2.replace("pack ", "")] = _per.get(_k2.replace("pack ", ""), 0.0) + _v
    _elems = dict((_e2, _per.get(_e2, 0.0)) for _e2 in AUG_ELEM_KINDS)
    AUG_COVER[_z] = (_tot, _b, _elems)
    print("0.1.25 Zone %%d spawn weight by element (vanilla fighters + tougher versions%%s): %%s" %% (_z, " + Slime Mobs!" if SLIME_ROLES else "",
          ", ".join("%%s %%.0f %%%%" %% (_k2, 100.0 * _v / _tot) for _k2, _v in sorted(_b.items(), key=lambda _x: -_x[1]) if not _k2.startswith("pack ")) +
          ("; pack: " + ", ".join("%%s %%g" %% (_k2[5:], _v) for _k2, _v in sorted(_b.items()) if _k2.startswith("pack ")) if any(_k2.startswith("pack ") for _k2 in _b) else "")))
if 5 not in AUG_COVER:          # aug3fix2 (critic): say so instead of skipping Zone 5 silently
    print("   NOTE Zone 5: no vanilla environment Env_Zone5_* spawns anything yet (Assets.zip has Zone 5 trees only) - its element %%s needs bodies when Zone 5 opens" %% _AUG_ZE[5])
for _z in sorted(AUG_COVER):          # every zone's fighters carry its element (the tougher versions), and every element-less tougher version takes it
    _b = AUG_COVER[_z][1]
    _pr = _AUG_ZE[_z]
    if not _b.get(_pr, 0.0) > 0.0:          # a report, not a failure (the drop x primary works anyway; beacon / circle / pack bodies are not counted here)
        print("   NOTE Zone %%d: no vanilla world-spawn fighter carries its element %%s (pack: %%g) - its commons are %%s" %% (_z, _pr, _b.get("pack " + _pr, 0.0),
              max([_e2 for _e2 in AUG_ELEM_KINDS], key=lambda _x: _b.get(_x, 0.0))))
    _vz = [_v for _v in VAR_IDS if VAR_IDS[_v][2] == _z]
    assert _vz and all(aug_elem_of(_v, 100) == (elem_row(_EROWS, VAR_IDS[_v][0])[2] if elem_row(_EROWS, VAR_IDS[_v][0]) else _pr) for _v in _vz), "0.1.25: Zone %%d tougher versions" %% _z
    _vw = sum(_b2 for _k2, _b2 in _b.items() if _k2 == _pr)
    _nw = sum(_v2 for _k2, _v2 in _b.items() if _k2 in AUG_ELEM_KINDS and _k2 != _pr)
    _vt = [_v for _v in _vz if elem_row(_EROWS, VAR_IDS[_v][0]) is None]
    _vm, _vmw = {}, {}
    for _v in _vt:
        _vm[aug_elem_of(_v)] = _vm.get(aug_elem_of(_v), 0) + 1
        _vmw[aug_elem_of(_v)] = _vmw.get(aug_elem_of(_v), 0.0) + _ZMW.get(_v, 0.0)
    _tw = sum(_vmw.values())
    assert not _tw or 0.45 <= _vmw.get(_pr, 0.0) / _tw <= 0.85, "0.1.25: Zone %%d's element = about elem.zoneMix of its element-less tougher versions' spawns: %%s" %% (_z, _vmw)
    assert len(_vt) < 5 or len(_vm) == 5, "aug3fix2: Zone %%d: 5+ element-less tougher versions = a role of every element at the default: %%s" %% (_z, _vm)
    _bl = _aug_land.get(_z, {})
    _le = dict((_e2, _bl.get(_e2, 0.0)) for _e2 in AUG_ELEM_KINDS)
    _ltot = sum(_le.values())
    if _vt:          # aug3fix2 (critic: "the primary just makes up most of the common mobs"): on land the zone element leads the elemental fighters
        assert _le[_pr] >= max(_le.values()), "aug3fix2: Zone %%d: on land %%s must lead the elemental fighters: %%s" %% (_z, _pr, _le)
    print("   Zone %%d on land (no fish files): elemental fighters %%s; %%s = %%.0f %%%% of them (of all land fighters %%.0f %%%%)" %% (_z,
          ", ".join("%%s %%.0f %%%%" %% (_e2, 100.0 * _le[_e2] / max(1e-9, _ltot)) for _e2 in AUG_ELEM_KINDS), _pr, 100.0 * _le[_pr] / max(1e-9, _ltot),
          100.0 * _le[_pr] / max(1e-9, sum(_bl.values()))))
    print("   Zone %%d: %%d of %%d tougher versions have no element row -> zone mix %%d %%%% (roles / %%%% of their spawns): %%s; element share of the zone's elemental fighters %%.0f %%%% %%s" %% (
          _z, len(_vt), len(_vz), ZMIX_DEF, ", ".join("%%s %%d / %%.0f" %% (_e2, _vm.get(_e2, 0), 100.0 * _vmw.get(_e2, 0.0) / max(1e-9, _tw)) for _e2 in AUG_ELEM_KINDS),
          100.0 * _vw / max(1.0, _vw + _nw), _pr))
AUG_GAPS = dict((_z, [_e2 for _e2 in AUG_ELEM_KINDS if AUG_COVER[_z][2][_e2] <= 0.0]) for _z in sorted(AUG_COVER))
print("0.1.25 elements with NO world-spawn body per zone (beacons / caves / circles not counted): %%s" %% AUG_GAPS)
''' % (AUGR, ZVAR_ROW, ZMIX_ROW, AUG_STAT, AUG_ELEM)
P.rep('''# 0.1.24 (gl2): the Trork / Kweebec set drop rows (Server Setup > Mobs > Set drops; MobTheme, rolled by SpoilsSys)
TH_TROW = ''', DEF + '''# 0.1.24 (gl2): the Trork / Kweebec set drop rows (Server Setup > Mobs > Set drops; MobTheme, rolled by SpoilsSys)
TH_TROW = ''')
# fields
P.rep('''for _r in TH_TROW:          # 0.1.24 (gl2): the set drop rows
    F(cfg, ("public static volatile String %s = %s;" % (_r[9], jstr(_r[3]))) if _r[2] == "text" else ("public static volatile double %s = %s;" % (_r[9], repr(float(_r[3])))))
''', '''for _r in TH_TROW:          # 0.1.24 (gl2): the set drop rows
    F(cfg, ("public static volatile String %s = %s;" % (_r[9], jstr(_r[3]))) if _r[2] == "text" else ("public static volatile double %s = %s;" % (_r[9], repr(float(_r[3])))))
for _r in AUG_ROW:          # 0.1.25 (aug3): the augment drop rows
    if _r[2] == "text":
        F(cfg, "public static volatile String %s = %s;" % (_r[9], jstr(_r[3])))
    elif _r[2] == "bool":
        F(cfg, "public static volatile boolean %s = %s;" % (_r[9], _r[3]))
    elif _r[2] == "int":
        F(cfg, "public static volatile int %s = %s;" % (_r[9], _r[3]))
    else:
        F(cfg, "public static volatile double %s = %s;" % (_r[9], repr(float(_r[3]))))
F(cfg, "public static volatile boolean ELEM_ZVAR = true;")          # 0.1.25: tougher versions take the zone element
F(cfg, "public static volatile int ELEM_ZMIX = %d;" % ZMIX_DEF)          # aug3fix: ... this % of them (the rest: the 4 other elements)
''')
# the tab + rows
P.rep('''CFG_CATS.insert(CFG_CATS.index(("variant", "Tougher mobs")) + 1, ("theme", "Set drops"))          # 0.1.24 (gl2)
''', '''CFG_CATS.insert(CFG_CATS.index(("variant", "Tougher mobs")) + 1, ("theme", "Set drops"))          # 0.1.24 (gl2)
CFG_CATS.insert(CFG_CATS.index(("theme", "Set drops")) + 1, ("aug", "Augments"))          # 0.1.25 (aug3)
''')
P.rep('''              "field:MobCfg.%s%s" % (_r[9], ";check=MobHooks.checkSetMobs" if _r[2] == "text" else "")) for _r in TH_TROW]          # 0.1.24 (gl2): the set drops (live)
''', '''              "field:MobCfg.%s%s" % (_r[9], ";check=MobHooks.checkSetMobs" if _r[2] == "text" else "")) for _r in TH_TROW]          # 0.1.24 (gl2): the set drops (live)
CFG_ROWS += [(_r[0], _r[1], "aug", _r[2], _r[3], _r[4], _r[5], _r[6], _r[7], "live", _r[8],
              "field:MobCfg.%s%s" % (_r[9], ";after=MobCfg.elemEdit;check=MobHooks.checkZoneElem" if _r[2] == "text" else "")) for _r in AUG_ROW]          # 0.1.25 (aug3): augment drops (live)
CFG_ROWS += [ZVAR_ROW, ZMIX_ROW]          # 0.1.25 (aug3): Elements > tougher versions take the zone element + its share (live)
''')
P.rep('''              ] + ["%s=%s" % (_r[0], _r[3]) for _r in TH_TROW]          # 0.1.24 (absent in an older file = the default)
''', '''              ] + ["%s=%s" % (_r[0], _r[3]) for _r in TH_TROW]          # 0.1.24 (absent in an older file = the default)
CFG_LINES += ["# Augment drops (SkyyMobs 0.1.25): levelled mobs drop SkyyGear augments of the zone's tier; own element x elemMob, zone element x primary.",
              ] + ["%s=%s" % (_r[0], _r[3]) for _r in AUG_ROW] + [
              "# Tougher versions (Armored / Veteran) with no Mob elements row take their zone's element (aug.zoneElement.<zone>).",
              "%s=%s" % (ZVAR_ROW[0], ZVAR_ROW[4]),
              "# ... elem.zoneMix % of them take it, the rest the 4 other elements in turn (some mobs of every element in every zone).",
              "%s=%s" % (ZMIX_ROW[0], ZMIX_ROW[4])]          # 0.1.25 (absent in an older file = the default)
''')
# load (before MobElem.derive: the zone elements feed it)
_LD = {"text": '''  %s = c.getProperty("%s", "%s").trim();          // 0.1.25 (aug3): a file without the line = the default
''', "bool": '''  %s = bool(c.getProperty("%s"), %s);
''', "int": '''  %s = intOf(c.getProperty("%s"), %s, %s, %s);
''', "dec": '''  %s = dec(c.getProperty("%s"), %s, %s, %s);
'''}
LOAD = ""
for _r in AUGR:
    if _r[2] == "text":
        LOAD += _LD["text"] % (_r[9], _r[0], _r[3])
    elif _r[2] == "bool":
        LOAD += _LD["bool"] % (_r[9], _r[0], _r[3])
    elif _r[2] == "int":
        LOAD += _LD["int"] % (_r[9], _r[0], _r[3], _r[4], _r[5])
    else:
        LOAD += _LD["dec"] % (_r[9], _r[0], repr(float(_r[3])), repr(float(_r[4])), repr(float(_r[5])))
LOAD += '''  ELEM_ZVAR = bool(c.getProperty("elem.zoneVariants"), true);          // 0.1.25 (aug3)
  ELEM_ZMIX = intOf(c.getProperty("elem.zoneMix"), %d, 0, 100);          // aug3fix
''' % ZMIX_DEF
P.rep('''  TH_ELITE = dec(c.getProperty("drops.eliteX"), 3.0, 1.0, 10.0);
''', '''  TH_ELITE = dec(c.getProperty("drops.eliteX"), 3.0, 1.0, 10.0);
''' + LOAD)
# the plate / health signature: a zone element edit re-applies the loaded mobs' plates
P.rep('''    + "|elem|" + ELEM_MOBS + "|" + ELEM_PLATE          // 0.1.17: the element plates
''', '''    + "|elem|" + ELEM_MOBS + "|" + ELEM_PLATE          // 0.1.17: the element plates
    + "|zvar|" + ELEM_ZVAR + "|" + ELEM_ZMIX + "|" + AUG_Z1 + "|" + AUG_Z2 + "|" + AUG_Z3 + "|" + AUG_Z4 + "|" + AUG_Z5          // 0.1.25: the zone elements of the tougher versions
''')

# ---------- 2. MobElem: the zone element of a tougher version without a row
P.rep('''           "public static volatile int ROWS = 0;"):
    F(mel, _f)''', '''           "public static volatile int ROWS = 0;",
           "public static volatile int[] ZOWN = new int[] { -1, -1, -1, -1, -1, -1 };",          # 0.1.25: zone -> its element for tougher versions (-1 none / off)
           "public static final String[] ZM_IDS = new String[] { %s };" % ", ".join(jstr(_v) for _v in ZMIX_IDS),          # aug3fix: the zone-mix table (sorted)
           "public static final double[] ZM_U = new double[] { %s };" % ", ".join(repr(ZMIX[_v][0]) for _v in ZMIX_IDS),
           "public static final int[] ZM_O = new int[] { %s };" % ", ".join(str(ZMIX[_v][1]) for _v in ZMIX_IDS)):
    F(mel, _f)''')
P.rep('''  TAB = t;
  ROWS = own.length;
  ANY = any && @PKG@.MobCfg.ELEM_SHARE > 0;''', '''  String[] zs = new String[] { null, @PKG@.MobCfg.AUG_Z1, @PKG@.MobCfg.AUG_Z2, @PKG@.MobCfg.AUG_Z3, @PKG@.MobCfg.AUG_Z4, @PKG@.MobCfg.AUG_Z5 };
  int[] zo = new int[] { -1, -1, -1, -1, -1, -1 };
  boolean zany = false;
  for (int z = 1; z < zs.length; z++) {
    int ze = @PKG@.MobCfg.ELEM_ZVAR ? idx(zs[z]) : -1;          // 0.1.25 (aug3): a tougher version without a row takes its zone's element
    zo[z] = ze >= 0 && ze <= 4 ? ze : -1;
    if (zo[z] >= 0) zany = true;
  }
  ZOWN = zo;
  TAB = t;
  ROWS = own.length;
  ANY = (any || zany) && @PKG@.MobCfg.ELEM_SHARE > 0;''')
P.rep('''M(mel, r"""
public static int ownOf(String role) {
  int r = row(role);
  if (r < 0) return -1;
  return ((int[]) TAB[2])[r];
}""")''', '''# 0.1.25 (aug3): a tougher version (<role>_SkyyArmored<z> / _SkyyVeteran<z>) whose vanilla role has NO row = its zone's element (elem.zoneVariants)
M(mel, r"""
public static int zoneOwn(String role) {
  int[] zo = ZOWN;
  if (zo == null || role == null) return -1;
  int z = @PKG@.MobCfg.variantZone(role);
  if (z < 1 || z >= zo.length) return -1;
  int p = zo[z];
  if (p < 0) return -1;
  int i = java.util.Arrays.binarySearch(ZM_IDS, role);          // aug3fix: the zone mix (a version not in the table = the zone element)
  if (i < 0 || ZM_U[i] * 100.0 < (double) @PKG@.MobCfg.ELEM_ZMIX) return p;
  int k = ZM_O[i];
  return k >= p ? k + 1 : k;          // the k-th of the 4 other elements (wheel order without the zone's)
}""")
M(mel, r"""
public static int ownOf(String role) {
  int r = row(role);
  if (r < 0) return zoneOwn(role);          // 0.1.25
  return ((int[]) TAB[2])[r];
}""")''')
P.rep('''  int r = row(role);
  if (r < 0 || t == null) return 0;
  int own = ((int[]) t[2])[r];
  int res = ((int[]) t[3])[r];
  int wk = ((int[]) t[4])[r];''', '''  int r = row(role);
  int own = -1;
  int res = -1;
  int wk = -1;
  if (r >= 0 && t != null) {
    own = ((int[]) t[2])[r];
    res = ((int[]) t[3])[r];
    wk = ((int[]) t[4])[r];
  } else {
    own = r < 0 ? zoneOwn(role) : -1;          // 0.1.25: a tougher version's zone element = a pure-wheel row
    if (own < 0) return 0;
    res = own;
    wk = beatsIn(WORD, own);
  }''')

# ---------- 1. MobAug (before MobTheme's block: MobEgg.text names it)
P.rep('''mthm = pool.makeClass(PKG + ".MobTheme")''', '''maug = pool.makeClass(PKG + ".MobAug")       # 0.1.25 (aug3): the augment drops by zone / element / rank (SpoilsSys rolls it)
mthm = pool.makeClass(PKG + ".MobTheme")''')
P.rep('''mlds, mvat, mspw, mspk, mvar, mvsy, mthm]''', '''mlds, mvat, mspw, mspk, mvar, mvsy, mthm, maug]''')
MA = r'''# 0.1.25 (aug3): MobAug - the augment drops (Augments-Spec 2.4). ONE roll set per dead mob (SpoilsSys, the world thread): the items go into
# the list the Spoils spawn at the mob for the drop's owner. ITEM_API = harness seam (null in the game). Element index = MobElem.NAMES.
for _f in ("public static final String[] STAT = %s;" % ("new String[] { " + ", ".join(jstr(_k) for _k in AUG_STAT_KINDS) + " }"),
           "public static volatile java.util.function.Predicate ITEM_API = null;",
           "public static volatile long ROLLS = 0L;", "public static volatile long DROPS = 0L;", "public static volatile long MISSING = 0L;",
           "public static volatile long BOSSES = 0L;", "public static final long[] BYZ = new long[6];"):
    F(maug, _f)
M(maug, r"""
public static boolean on() {
  if (!@PKG@.MobCfg.AUG_ON) return false;
  return @PKG@.MobCfg.AUG_BASE > 0.0 || @PKG@.MobCfg.AUG_SELITE > 0.0 || @PKG@.MobCfg.AUG_SMINI > 0.0 || @PKG@.MobCfg.AUG_BSTAT > 0
      || @PKG@.MobCfg.AUG_BELEM > 0 || @PKG@.MobCfg.AUG_BBONUS > 0.0;
}""")
# the zone of a level (bosses.zoneTops, = MobBossFn.zoneOf / TT.zone_of_level); 0 = no level
M(maug, r"""
public static int zoneOfLevel(int lv) {
  int[] tops = @PKG@.MobCfg.BOSS_TOP;
  if (tops == null || tops.length == 0 || lv < 1) return 0;
  for (int i = 0; i < tops.length; i++) if (tops[i] >= lv) return i + 1;
  return tops.length;
}""")
# P0 X10: the ENVIRONMENT's zone first (Env_Zone<N>...; a tougher version's +1 / +2 levels can pass the band), else the level; 1..5, 0 = none
M(maug, r"""
public static int zoneOf(String env, int lv) {
  String z = @PKG@.MobLevel.zoneOfEnv(env);
  int n = 0;
  if (z != null) {
    try { n = Integer.parseInt(z.substring(4)); } catch (Throwable t) { n = 0; }
  }
  if (n < 1) n = zoneOfLevel(lv);
  if (n < 1) return 0;
  return n > 5 ? 5 : n;
}""")
M(maug, r"""
public static int zoneElem(int z) {
  String s = null;
  if (z == 1) s = @PKG@.MobCfg.AUG_Z1;
  else if (z == 2) s = @PKG@.MobCfg.AUG_Z2;
  else if (z == 3) s = @PKG@.MobCfg.AUG_Z3;
  else if (z == 4) s = @PKG@.MobCfg.AUG_Z4;
  else if (z == 5) s = @PKG@.MobCfg.AUG_Z5;
  int e = @PKG@.MobElem.idx(s);
  return e >= 0 && e <= 4 ? e : -1;
}""")
# the 5 element weights (%) of one kill: b x m, x elemMob for the mob's own element, x primary for the zone's element
M(maug, r"""
public static double[] weights(String role, int z, double m, double b) {
  double[] w = new double[5];
  if (!(b > 0.0) || !(m > 0.0)) return w;
  int own = @PKG@.MobElem.ownOf(role);
  int pr = zoneElem(z);
  for (int e = 0; e < 5; e++) {
    double x = b * m;
    if (e == own) x = x * @PKG@.MobCfg.AUG_EMOB;
    if (e == pr) x = x * @PKG@.MobCfg.AUG_PRIM;
    w[e] = x;
  }
  return w;
}""")
# one weighted roll: sure = always an element (a boss); else the sum is the chance (%, capped at 100); -1 = none
M(maug, r"""
public static int pick(double[] w, java.util.Random rng, boolean sure) {
  if (w == null || rng == null) return -1;
  double t = 0.0;
  int last = -1;
  for (int e = 0; e < w.length; e++) {
    if (w[e] > 0.0) { t = t + w[e]; last = e; }
  }
  if (last < 0) return -1;
  double r = 0.0;
  if (sure || t >= 100.0) r = rng.nextDouble() * t;
  else {
    r = rng.nextDouble() * 100.0;
    if (r >= t) return -1;
  }
  for (int e = 0; e < w.length; e++) {
    if (!(w[e] > 0.0)) continue;
    if (r < w[e]) return e;
    r = r - w[e];
  }
  return last;
}""")
M(maug, r"""
public static boolean hit(double pct, java.util.Random rng) {
  double c = pct > 100.0 ? 100.0 : pct;
  return c > 0.0 && rng.nextDouble() * 100.0 < c;
}""")
M(maug, r"""
public static boolean itemOk(String id) {
  java.util.function.Predicate p = ITEM_API;
  if (p != null) return p.test(id);
  try { return @ITMA@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { return false; }
}""")
M(maug, r"""
public static int put(java.util.ArrayList l, String id) {
  if (!itemOk(id)) { MISSING = MISSING + 1L; @PKG@.MobLog.warnOnce("aug:missing", "an augment drop rolled " + id + " but the item is not loaded (SkyyGear 0.3.52+ missing?) - nothing dropped (one WARN for all ids; MobAug.MISSING counts them)"); return 0; }
  l.add(new Object[] { id, Integer.valueOf(1) });
  DROPS = DROPS + 1L;
  return 1;
}""")
M(maug, r"""
public static String elemId(int e, int z) { return "Skyy_Aug_" + @PKG@.MobElem.NAMES[e] + "_" + z; }""")
M(maug, r"""
public static String statId(java.util.Random rng, int z) { return "Skyy_Aug_" + STAT[rng.nextInt(STAT.length)] + "_" + z; }""")
# the rolls of one dead mob (rw = its rank word from MobInfo; env = its environment id; lvl = its level, 0 = unlevelled); returns the items added
M(maug, r"""
public static int addTo(java.util.ArrayList l, String role, String rw, String env, int lvl, java.util.Random rng) {
  if (l == null || role == null || rng == null || !on()) return 0;
  boolean boss = @PKG@.MobCfg.isBoss(role) || "boss".equals(rw);
  if (lvl < 1 && !boss) return 0;
  int z = zoneOf(env, lvl);
  if (z < 1) return 0;
  ROLLS = ROLLS + 1L;
  int n = 0;
  if (boss) {
    BOSSES = BOSSES + 1L;
    double[] w = weights(role, z, 1.0, 1.0);
    for (int i = 0; i < @PKG@.MobCfg.AUG_BELEM; i++) {
      int e = pick(w, rng, true);
      if (e >= 0) n = n + put(l, elemId(e, z));
    }
    if (hit(@PKG@.MobCfg.AUG_BBONUS, rng)) {
      int e2 = pick(w, rng, true);
      if (e2 >= 0) n = n + put(l, elemId(e2, z));
    }
    for (int i = 0; i < @PKG@.MobCfg.AUG_BSTAT; i++) n = n + put(l, statId(rng, z));
  } else {
    boolean mini = "mini".equals(rw);
    boolean elite = "elite".equals(rw);
    double m = (mini || elite) && @PKG@.MobCfg.AUG_ELITE > 1.0 ? @PKG@.MobCfg.AUG_ELITE : 1.0;
    int e = pick(weights(role, z, m, @PKG@.MobCfg.AUG_BASE), rng, false);
    if (e >= 0) n = n + put(l, elemId(e, z));
    double sc = mini ? @PKG@.MobCfg.AUG_SMINI : (elite ? @PKG@.MobCfg.AUG_SELITE : 0.0);
    if (hit(sc, rng)) n = n + put(l, statId(rng, z));
  }
  if (n > 0) BYZ[z] = BYZ[z] + (long) n;
  return n;
}""")
M(maug, r"""
public static String text() {
  StringBuilder zs = new StringBuilder();
  for (int z = 1; z <= 5; z++) { if (z > 1) zs.append('/'); int e = zoneElem(z); zs.append(e >= 0 ? @PKG@.MobElem.NAMES[e] : "none"); }
  return "augment drops " + (on() ? "on" : "OFF") + " (element " + @PKG@.MobCfg.AUG_BASE + " % each, own x" + @PKG@.MobCfg.AUG_EMOB + ", zone x" + @PKG@.MobCfg.AUG_PRIM
      + ", elites x" + @PKG@.MobCfg.AUG_ELITE + "; stat elite " + @PKG@.MobCfg.AUG_SELITE + " % / mini " + @PKG@.MobCfg.AUG_SMINI + " %; boss " + @PKG@.MobCfg.AUG_BSTAT + " stat + "
      + @PKG@.MobCfg.AUG_BELEM + " element (+" + @PKG@.MobCfg.AUG_BBONUS + " %); zones " + zs + (@PKG@.MobCfg.ELEM_ZVAR ? ", tougher versions take it" : "")
      + "; rolled " + ROLLS + ", dropped " + DROPS + (MISSING > 0L ? ", item missing " + MISSING : "") + ")";
}""")
# Server Setup check of a zone element (value null = back to the default)
M(mh, r"""
public static String checkZoneElem(String key, String value) {
  if (value == null) return null;
  if (@PKG@.MobElem.idx(value) < -1) return "'" + value.trim() + "' is no element - write Earth, Thunder, Water, Fire, Air or none.";
  return null;
}""")
'''
P.rep('''# 0.1.24 (gl2): MobTheme - the Trork / Kweebec set drops. ONE roll set per dead mob (SpoilsSys, the world thread): the items go into the list the''',
      MA + '''# 0.1.24 (gl2): MobTheme - the Trork / Kweebec set drops. ONE roll set per dead mob (SpoilsSys, the world thread): the items go into the list the''')
P.rep('''+ "); " + @PKG@.MobTheme.text();          // 0.1.24: + the set drops''',
      '''+ "); " + @PKG@.MobTheme.text() + "; " + @PKG@.MobAug.text();          // 0.1.24: + the set drops; 0.1.25: + the augment drops''')
# ---------- SpoilsSys: the gate + the roll (after the set drops, before the spawn)
P.rep('''&& !@PKG@.MobTheme.on()) return;          // 0.1.24: + the set drops''', '''&& !@PKG@.MobTheme.on() && !@PKG@.MobAug.on()) return;          // 0.1.24: + the set drops; 0.1.25: + the augment drops''')
P.rep('''    @PKG@.MobTheme.addTo(l, npc.getRoleName(), rw, @PKG@.MobSpoils.RNG);          // 0.1.24 (gl2): the Trork / Kweebec set drops (once per death)
''', '''    @PKG@.MobTheme.addTo(l, npc.getRoleName(), rw, @PKG@.MobSpoils.RNG);          // 0.1.24 (gl2): the Trork / Kweebec set drops (once per death)
    try {          // 0.1.25 (aug3): the augment drops (once per death); aug3fix: their own failure never stops the egg / spawn / secret finds
      String aenv = null;
      try { aenv = @PKG@.MobLevel.envId(npc.getEnvironment()); } catch (Throwable tae) { aenv = null; }
      @PKG@.MobAug.addTo(l, npc.getRoleName(), rw, aenv, lvl, @PKG@.MobSpoils.RNG);
    } catch (Throwable taug) { @PKG@.MobLog.warnOnce("aug", "the augment drops failed (logged once): " + taug); }
''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0 + 1, "0.1.25: one new class (MobAug), no system / command"
_i = P.s.index
assert _i("public static int variantZone(String role)") < _i("public static int zoneOwn(String role)") < _i("public static int ownOf(String role)") < _i("public static int mod(String role, int e)")
assert _i("public static int ownOf(String role)") < _i("public static double[] weights(String role, int z") < _i("@PKG@.MobAug.text()") < _i("@PKG@.MobAug.addTo(l, npc.getRoleName()")
assert _i("public static String zoneOfEnv(String env)") < _i("public static int zoneOf(String env, int lv)")
assert _i("ELEM_A3_VAN = [") < _i('"elem.mobs=" + ELEM_MOBS_DEF') and _i("ELEM_A3_VAN = [") < _i('public static volatile String ELEM_MOBS = %s;')
P.finish()
print("wrote", P.dst)
