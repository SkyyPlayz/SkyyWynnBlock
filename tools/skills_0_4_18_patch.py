"""Derive SkyySkills/build_skyyskills_0.4.18.py from the LIVE generated SkyySkills/build_skyyskills_0.4.17.py (= the tools/deploy_set.py SET
pin, deployed 2026-10-06 with the mob curve; 0.4.17 came from 0.4.16 by tools/skills_0_4_17_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 -
commit ab75b6c; never re-run skills_0_4_5 or older patches). Same style as skills_0_4_17_patch.py: rep(old, new) with asserted single
anchors, newline-agnostic; 0.4.17 stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_18_patch.py   then   python SkyySkills/build_skyyskills_0.4.18.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.18.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/skills0418/, deleted afterwards)

0.4.18 = THE DODGE ROLL (research/Grapple-Bolt-Spec.md 1.2 / 2.5 / 3.2 - the spec calls it "SkyySkills 0.4.17"; 0.4.17 became the mob
curve, so this is 0.4.18 and keeps ALL of 0.4.17, the mob-curve pairing included). Skyy LOCKED 2026-10-06 (docs/answered/classes.md):
"Dodge Roll = the vanilla dodge key turned into a real roll in all 8 directions, standing still = roll back" ("Yes, 8-way roll"); the
other dodge questions = the spec defaults (vanilla numbers, rolls give the same Acrobatics dodge XP + push, real Roll animations).

(1) ASSETS (generated at build time from Assets.zip, read in memory; the build stops if a vanilla body it copies changed):
    - override Server/Item/Interactions/Dodge.json: the vanilla Condition (Flying false - air rolls stay allowed) -> MovementCondition
      Forward / ForwardLeft / ForwardRight -> SkyySkills_Roll_Forward*, Back / BackLeft / BackRight / Failed (no movement key) ->
      SkyySkills_Roll_Back*, Left -> vanilla Dodge_Left, Right -> vanilla Dodge_Right.
    - 6 new interactions Server/Item/Interactions/Dodge/SkyySkills_Roll_<dir>.json = the vanilla Dodge_Left.json body (Stamina 2 through
      StatsConditionWithModifier "Dodge", Dodge_Invulnerability 0.25 s, ApplyForce Set 13 with the vanilla VelocityConfig, Adventure:
      Stamina -2 + StaminaRegenDelay -0.7, Failed Stamina_Bar_Flash) with only the direction effect and the Direction vector changed
      (forward = Z -1 like vanilla's left = X -1; diagonals 0.7071).
    - 2 new effects Server/Entity/Effects/Movement/Dodge_Forward.json / Dodge_Back.json (the vanilla Dodge_Left effect with animation
      Roll / RollBackward; diagonals: forward ones Roll, back ones RollBackward) + overrides of the vanilla Dodge_Left / Dodge_Right
      effects with RollLeft / RollRight (were DashLeft / DashRight). Nothing else in Assets.zip names those two effects (build check).
    - conflict check: no jar of the live set and no PACK_THIRD_PARTY pack mod ships one of these files / ids (stop); other installed mods
      that do are listed with their "HUD mod" Enabled state (a NOTE; Skyy's own 1.5.0 modpack ships a Dodge.json - disabled).
(2) Acro.dodge: the dodge effects it watches become Dodge_Left, Dodge_Right, Dodge_Forward, Dodge_Back (same edge / cooldown / XP / push).
(3) Server Setup: read-only info row acro.roll (custom:SkillKit) "8-way roll, 13 force, 2 Stamina, 0.25 s safe - fixed in the jar";
    help text on acro.dodgeXp "Dodge rolls the way you move ...". The manifest text names the roll.
(4) FIX: the built-in kit table (ManaGuard fallback, KIT_FALLBACK) = SkyyClasses 0.1.12's default kits (Warrior got a Wood Shield in
    SkyyClasses 0.1.10: the build printed "mana guard: ... DIFFERS ... (Warrior)").
NOT in this build: no config migration (no new file keys - the info row is read-only); the default xp.properties comment lines stay
0.4.17's (a fresh file's "the vanilla strafe left/right dodge" comment is left as is - changing default text would touch the migrations).
"""
import copy
import difflib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.17.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.18.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.17"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.17"' in s and "derived from the generated 0.4.16 by tools/skills_0_4_17_patch.py" in s, "not the live generated 0.4.17"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert '".KillXpMig"' in s and "combat.xpFrom" in s and "mob:fn:info" in s, "the mob curve (0.4.17) is missing"
for _x in ("DODGE_FILES", "SkyySkills_Roll_", "Dodge_Forward", "acro.roll\""):
    assert _x not in s, "0.4.17 already has " + _x
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
OLDS = []


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    i = s.index(old)
    j = s.find(LF, i + len(old))
    OLDS.append(s[s.rfind(LF, 0, i) + 1:(j if j >= 0 else len(s))])
    s = s.replace(old, new)


def after(anchor, add):
    rep(anchor, anchor + add)


def before(anchor, add):
    rep(anchor, add + anchor)


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1 and s.index(a) < s.index(b), (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# blocks that must stay byte-identical (0.4.17 code this build does not touch - the mob curve's part included)
KEEP = [block("# >>> SPELL GEN", "# <<< SPELL GEN"),
        block("# ================= Xbow part 1 (0.4.5)", "# ================= ClassCurve (0.4.12)"),
        block("# ================= 0.4.2 FELLED TREES", "# FellCredit (spec 2.6)"),
        block("# ================= skill:fn:addxp (0.4)", "# ================= leaderboard ================="),
        block("# ================= OverallPage (0.4.6)", "# ================= 0.4.3 ADMIN CONFIG"),
        block("# ---- 0.4.5 Xbow part 2", "# ================= ManaRegen (0.4.12)"),
        block("# ================= CombatDmgSys (0.3)", "# ================= PlacedStore"),
        block("# ================= RollSys (0.4.14)", "# ================= CombatDmgSys (0.3)"),
        block("# ================= SkillStore: per-player XP", "# ================= SkillClass (0.3)"),
        block("# ---- HealMig (0.4.11 point 5)", "# ---- DocMig (0.4.14, fix (5))"),
        block("# ================= ClassMana part 1 (0.4.15", "# ================= SkillLv (0.4.16)"),
        block("# ================= OwnCurve (0.4.16)", "# ================= GatherPace.apply (0.4.14)"),
        block("# ---- SkillLvMig (0.4.16)", "# ---- ManaGuard (point 3)")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.17 - build script (derived from the generated 0.4.16 by tools/skills_0_4_17_patch.py - edit the patch, not this file;
0.4.16 was derived''', '''"""SkyySkills 0.4.18 - build script (derived from the generated 0.4.17 by tools/skills_0_4_18_patch.py - edit the patch, not this file;
0.4.17 was derived from the generated 0.4.16 by tools/skills_0_4_17_patch.py; 0.4.16 was derived''')
HEAD_0418 = '''0.4.18: THE DODGE ROLL (research/Grapple-Bolt-Spec.md 1.2 / 2.5 / 3.2; Skyy LOCKED 2026-10-06 "Yes, 8-way roll"; full notes in
  tools/skills_0_4_18_patch.py). Keeps all of 0.4.17 (same mob-curve pairing: SkyyMobs 0.1.4 + SkyyGear 0.2.5; 0.4.17 is a safe rollback).
  The vanilla dodge key rolls the way you move: 8 directions (Dodge.json override, 6 new SkyySkills_Roll_* interactions = the vanilla
     Dodge_Left body turned), standing still = roll back; vanilla 2 Stamina, force 13, 0.25 s Dodge_Invulnerability, air rolls as vanilla;
     effects Dodge_Forward / Dodge_Back (new) + Dodge_Left / Dodge_Right (overridden) play Roll / RollBackward / RollLeft / RollRight.
  Acrobatics dodge XP + push count all 4 roll effects. Read-only Server Setup row acro.roll. Built-in kit table = SkyyClasses 0.1.12.
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.18.py, -Xverify:all, scratch under tools/dev/scratch deleted afterwards).
'''
before("0.4.17: THE MOB CURVE'S SKYYSKILLS PART (research/Mob-Curve-Spec.md 2.4 / 4.2 / 6.3 / 6.4; Skyy 2026-10-05 \"accept all defaults\"; full\n",
       HEAD_0418)
rep('VERSION = "0.4.17"\n', 'VERSION = "0.4.18"\n')

# ---------------------------------------------------------------------------------------------------------------- (4) kit table fix
rep("""('Warrior', 'Weapon_Sword_Crude:1'),""", """('Warrior', 'Weapon_Sword_Crude:1,Weapon_Shield_Wood:1'),""")

# ---------------------------------------------------------------------------------------------------------------- (1) the dodge roll assets
# the roll table: (MovementCondition key, interaction id, Direction X, Z, direction effect id). Forward = Z -1 (vanilla's left = X -1 and
# ApplyForce turns the vector by the head yaw: right-handed, facing -Z at yaw 0, so right = +X; Skyy's own 1.5.0 modpack used the same).
D = 0.7071
ROLLS = [("Forward", "SkyySkills_Roll_Forward", 0, -1, "Dodge_Forward"),
         ("ForwardLeft", "SkyySkills_Roll_ForwardLeft", -D, -D, "Dodge_Forward"),
         ("ForwardRight", "SkyySkills_Roll_ForwardRight", D, -D, "Dodge_Forward"),
         ("Back", "SkyySkills_Roll_Back", 0, 1, "Dodge_Back"),
         ("BackLeft", "SkyySkills_Roll_BackLeft", -D, D, "Dodge_Back"),
         ("BackRight", "SkyySkills_Roll_BackRight", D, D, "Dodge_Back")]
FX = [("Dodge_Left", "RollLeft"), ("Dodge_Right", "RollRight"), ("Dodge_Forward", "Roll"), ("Dodge_Back", "RollBackward")]
DODGE_PY = r'''# ================= 0.4.18 DODGE ROLL (research/Grapple-Bolt-Spec.md 1.2 / 2.5 / 3.2; Skyy LOCKED 2026-10-06 "Yes, 8-way roll") =================
# The vanilla dodge key (InteractionType.Dodge, root Server/Item/RootInteractions/Dodge.json - untouched) runs Server/Item/Interactions/
# Dodge.json: Condition Flying false -> MovementCondition. Vanilla fills only Left / Right (Dodge_Left / Dodge_Right). This jar overrides
# Dodge.json so every direction rolls and no movement key (Failed) rolls back; the 6 new interactions are the vanilla Dodge_Left body with
# only the direction effect and the Direction vector changed (cost, i-frames, force, VelocityConfig, Adventure-only Stamina spend and regen
# pause all vanilla). Generated from Assets.zip read in memory at every build; the build stops when a body it copies changed.
DODGE_ROLLS = @ROLLS@
DODGE_FX = @FX@
import copy   # 0.4.18: deep copies of the vanilla dodge bodies
DODGE_INT_IDS = ["Dodge"] + [_r[1] for _r in DODGE_ROLLS]
DODGE_FX_IDS = [_f[0] for _f in DODGE_FX]
_dodge_dups = []


def _dodge_hook(pairs):
    _ks = [k for k, v in pairs]
    _dodge_dups.extend(sorted(set(k for k in _ks if _ks.count(k) > 1)))
    return dict(pairs)


def dodge_fail(msg):
    raise SystemExit("dodge roll (0.4.18): " + msg)


with zipfile.ZipFile(ASSETS) as _dz:
    _dzn = _dz.namelist()

    def _dread(path):
        if path not in _dzn:
            dodge_fail("%s is not in Assets.zip any more - the dodge roll needs a look" % path)
        del _dodge_dups[:]
        _j = json.loads(_dz.read(path).decode("utf-8-sig"), object_pairs_hook=_dodge_hook)
        if _dodge_dups:
            dodge_fail("%s has a duplicate JSON key %s" % (path, _dodge_dups))
        return _j
    _dv_root = _dread("Server/Item/RootInteractions/Dodge.json")
    _dv_main = _dread("Server/Item/Interactions/Dodge.json")
    _dv_left = _dread("Server/Item/Interactions/Dodge/Dodge_Left.json")
    _dv_right = _dread("Server/Item/Interactions/Dodge/Dodge_Right.json")
    _dv_fx = dict((_i, _dread("Server/Entity/Effects/Movement/%s.json" % _i)) for _i in ("Dodge_Left", "Dodge_Right", "Dodge_Invulnerability"))
    _dv_player = _dread("Server/Models/Human/Player.json")
    _dv_names = set(os.path.basename(_n)[:-5] for _n in _dzn if _n.startswith("Server/") and _n.endswith(".json"))
    # who names the two side effects / the dodge interaction ids (their look changes for everything that applies them)
    _dv_refs = {}
    for _n in _dzn:
        if _n.startswith("Server/") and _n.endswith(".json"):
            _b = _dz.read(_n)
            for _i in ("Dodge_Left", "Dodge_Right", "Dodge_Invulnerability"):
                if ('"%s"' % _i).encode("utf-8") in _b:
                    _dv_refs.setdefault(_i, []).append(_n)
# the vanilla shapes this build copies (spec 2.5 VERIFIED 2026-10-06); any game change stops the build
if _dv_root != {"Interactions": ["Dodge"], "RequireNewClick": True}:
    dodge_fail("the vanilla dodge root changed: %r" % (_dv_root,))
_DV_MAIN = {"Type": "Condition", "Flying": False, "Next": {"Type": "MovementCondition", "ForwardLeft": {"Type": "Simple"},
            "ForwardRight": {"Type": "Simple"}, "Left": "Dodge_Left", "Right": "Dodge_Right", "BackLeft": {"Type": "Simple"},
            "BackRight": {"Type": "Simple"}}}
if _dv_main != _DV_MAIN:
    dodge_fail("the vanilla Dodge.json changed: %r" % (_dv_main,))
_DV_VC = {"AirResistance": 0.97, "AirResistanceMax": 0.96, "GroundResistance": 0.94, "GroundResistanceMax": 0.82, "Threshold": 5.0, "Style": "Exp"}


def _dodge_body(fx, x, z):
    """the vanilla Dodge_Left.json shape with the direction effect fx and Direction (x, 0, z)"""
    return {"Type": "StatsConditionWithModifier", "Costs": {"Stamina": 2}, "InteractionModifierId": "Dodge",
            "Next": {"Type": "Serial", "Interactions": [
                {"Type": "ApplyEffect", "EffectId": "Dodge_Invulnerability"},
                {"Type": "ApplyEffect", "EffectId": fx},
                {"Type": "ApplyForce", "Direction": {"X": x, "Y": 0, "Z": z}, "AdjustVertical": False, "WaitForGround": False, "Force": 13,
                 "ChangeVelocityType": "Set", "VelocityConfig": dict(_DV_VC)},
                {"Type": "Condition", "RequiredGameMode": "Adventure", "Next": {"Type": "Serial", "Interactions": [
                    {"Type": "ChangeStatWithModifier", "StatModifiers": {"Stamina": -2}, "ValueType": "Absolute", "InteractionModifierId": "Dodge"},
                    {"Type": "ChangeStat", "StatModifiers": {"StaminaRegenDelay": -0.7}, "Behaviour": "Set", "ValueType": "Absolute"}]}}]},
            "Failed": "Stamina_Bar_Flash"}
if _dv_left != _dodge_body("Dodge_Left", -1, 0) or _dv_right != _dodge_body("Dodge_Right", 1, 0):
    dodge_fail("the vanilla Dodge_Left / Dodge_Right interaction body changed (cost 2, force 13, VelocityConfig, Stamina -2, regen -0.7): %r"
               % (_dv_left,))
for _i, _a in (("Dodge_Left", "DashLeft"), ("Dodge_Right", "DashRight")):
    if _dv_fx[_i] != {"Duration": 0.25, "ApplicationEffects": {"EntityAnimationId": _a}, "OverlapBehavior": "Extend"}:
        dodge_fail("the vanilla %s effect changed: %r" % (_i, _dv_fx[_i]))
if _dv_fx["Dodge_Invulnerability"] != {"Duration": 0.25, "Invulnerable": True}:
    dodge_fail("the vanilla Dodge_Invulnerability effect changed (the 0.25 s i-frames): %r" % (_dv_fx["Dodge_Invulnerability"],))
_dv_sets = (_dv_player.get("AnimationSets") or {})
_dv_miss = [_a for _f, _a in DODGE_FX if not (_dv_sets.get(_a) or {}).get("Animations")]
if _dv_miss:
    dodge_fail("Player.json has no animation set %s" % _dv_miss)
# the side effects are only named by the dodge chain (their new look changes nothing else); the i-frames effect likewise
for _i in ("Dodge_Left", "Dodge_Right", "Dodge_Invulnerability"):
    _extra = [_n for _n in _dv_refs.get(_i, []) if _n not in ("Server/Item/Interactions/Dodge.json", "Server/Item/Interactions/Dodge/Dodge_Left.json",
                                                             "Server/Item/Interactions/Dodge/Dodge_Right.json")]
    if _extra:
        dodge_fail("assets outside the dodge chain name %s (its new look would change them too): %s" % (_i, _extra[:5]))
# our new ids are new (never a vanilla id of any asset type)
_dv_clash = [_i for _i in DODGE_INT_IDS[1:] + ["Dodge_Forward", "Dodge_Back"] if _i in _dv_names]
if _dv_clash:
    dodge_fail("Assets.zip already has %s" % _dv_clash)
assert [_r[0] for _r in DODGE_ROLLS] == ["Forward", "ForwardLeft", "ForwardRight", "Back", "BackLeft", "BackRight"]
assert all(abs(_r[2] * _r[2] + _r[3] * _r[3] - 1.0) < 1e-3 for _r in DODGE_ROLLS), "roll directions must be unit vectors"
assert all(_r[4] == ("Dodge_Forward" if _r[0].startswith("Forward") else "Dodge_Back") for _r in DODGE_ROLLS)
# the generated files
_d_main = copy.deepcopy(_dv_main)
_d_next = {"Type": "MovementCondition"}
for _k in ("Forward", "Back"):
    _d_next[_k] = [_r[1] for _r in DODGE_ROLLS if _r[0] == _k][0]
_d_next["Left"], _d_next["Right"] = "Dodge_Left", "Dodge_Right"
for _k in ("ForwardLeft", "ForwardRight", "BackLeft", "BackRight"):
    _d_next[_k] = [_r[1] for _r in DODGE_ROLLS if _r[0] == _k][0]
_d_next["Failed"] = "SkyySkills_Roll_Back"          # Skyy: standing still = roll back
_d_main["Next"] = _d_next
assert dict((k, v) for k, v in _d_main.items() if k != "Next") == dict((k, v) for k, v in _dv_main.items() if k != "Next")
DODGE_FILES = {}


def _dodge_put(path, obj):
    _t = json.dumps(obj, indent=2, ensure_ascii=True) + "\n"
    assert path not in DODGE_FILES and json.loads(_t) == obj and all(ord(ch) < 128 for ch in _t)
    DODGE_FILES[path] = _t
_dodge_put("Server/Item/Interactions/Dodge.json", _d_main)
for _k, _id, _x, _z, _fx in DODGE_ROLLS:
    _b = copy.deepcopy(_dv_left)
    _b["Next"]["Interactions"][1]["EffectId"] = _fx
    _b["Next"]["Interactions"][2]["Direction"] = {"X": _x, "Y": 0, "Z": _z}
    assert _b == _dodge_body(_fx, _x, _z)
    _dodge_put("Server/Item/Interactions/Dodge/%s.json" % _id, _b)
for _fid, _anim in DODGE_FX:
    _e = copy.deepcopy(_dv_fx["Dodge_Left"])
    _e["ApplicationEffects"]["EntityAnimationId"] = _anim
    _dodge_put("Server/Entity/Effects/Movement/%s.json" % _fid, _e)
assert len(DODGE_FILES) == 1 + len(DODGE_ROLLS) + len(DODGE_FX) == 11
assert not set(DODGE_FILES) & set(SPELL_FILES)
# every id Dodge.json names exists (ours or vanilla), every effect a roll applies exists
_d_ints = set(os.path.basename(_p)[:-5] for _p in DODGE_FILES if _p.startswith("Server/Item/Interactions/")) | {"Dodge_Left", "Dodge_Right"}
assert all(_v in _d_ints for _k, _v in _d_next.items() if _k != "Type"), _d_next
_d_fxs = set(os.path.basename(_p)[:-5] for _p in DODGE_FILES if _p.startswith("Server/Entity/Effects/")) | {"Dodge_Invulnerability"}
assert all(_e["EffectId"] in _d_fxs for _p, _t in DODGE_FILES.items() if "/Dodge/" in _p
           for _e in json.loads(_t)["Next"]["Interactions"] if _e["Type"] == "ApplyEffect")
'''
DODGE_PY = DODGE_PY.replace("@ROLLS@", repr(ROLLS)).replace("@FX@", repr(FX))
before("# no other Skyy mod of the live set (tools/deploy_set.py SET, its pinned jars) and no pack mod (PACK_THIRD_PARTY, found in the Mods folder by\n",
       DODGE_PY)
# the conflict check (after the spell section: it has the SET pins and PACK_THIRD_PARTY read already)
DODGE_CHECK = r'''# ---- 0.4.18 dodge roll conflict check: no other jar of the live set and no pack mod (PACK_THIRD_PARTY) ships one of the 11 files or ids -
# two overrides of Dodge.json would fight (the one loaded last wins). Other installed mods that ship one are listed with their "HUD mod"
# Enabled state (read only; Skyy's own 1.5.0 modpack, Perfect Dodges, MMOSkillTree ... are disabled there).


def _dodge_clash(names):
    return sorted(n for n in names if n in DODGE_FILES
                  or (n.startswith("Server/Item/Interactions/") and n.endswith(".json") and os.path.basename(n)[:-5] in DODGE_INT_IDS)
                  or (n.startswith("Server/Entity/Effects/") and n.endswith(".json") and os.path.basename(n)[:-5] in DODGE_FX_IDS))
_d_checked = []
for _mod, _ver in _pins:
    if _mod == "SkyySkills":
        continue
    _jp = os.path.join(os.path.dirname(HERE), _mod, "%s-%s.jar" % (_mod, _ver))
    if not os.path.isfile(_jp):
        print("dodge roll: NOTE %s %s is not built here - not checked" % (_mod, _ver))
        continue
    with zipfile.ZipFile(_jp) as _jz:
        _cl = _dodge_clash(_jz.namelist())
    if _cl:
        dodge_fail("%s %s (live set) also ships %s" % (_mod, _ver, _cl[:5]))
    _d_checked.append(_mod)
try:
    with open(os.path.join(B.USERDATA, "Saves", "HUD mod", "config.json"), "rb") as _wf:
        _d_world = (json.loads(_wf.read().decode("utf-8-sig")) or {}).get("Mods") or {}
except Exception:
    _d_world = None
_d_found, _d_other = [], []
for _f in (sorted(os.listdir(B.MODS_DIR)) if os.path.isdir(B.MODS_DIR) else []):
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
    _cl = _dodge_clash(_nm)
    if _key in _packs:
        _d_found.append(_key)
        if _cl:
            dodge_fail("pack mod %s (%s) also ships %s" % (_key, _f, _cl[:5]))
    elif _cl and not str(_man.get("Name", "")).endswith("SkyySkills"):
        _en = None
        if isinstance(_d_world, dict):
            _w = _d_world.get(_key)
            _en = _w.get("Enabled") if isinstance(_w, dict) else _w
        _d_other.append("%s [%s] %s (%d file(s), e.g. %s)" % (_f, _key, "ENABLED in HUD mod - it fights this override" if _en else
                                                             ("disabled in HUD mod" if _en is not None else "not listed in HUD mod"), len(_cl), _cl[0]))
print("dodge roll (0.4.18): %d files generated from Assets.zip (Dodge.json -> 8 directions + standing = back; %d roll interactions = the vanilla "
      "Dodge_Left body turned: 2 Stamina, force 13, 0.25 s i-frames, air as vanilla; effects %s); no clash with %d live-set jars or the pack "
      "mods %s" % (len(DODGE_FILES), len(DODGE_ROLLS), ", ".join("%s=%s" % _f for _f in DODGE_FX), len(_d_checked),
                   ", ".join(sorted(_d_found)) or "(none installed)"))
for _d_o in _d_other:
    print("dodge roll: NOTE another installed mod ships dodge assets: %s" % _d_o)
'''
before("# the modifier keys (spec 4.12): our own prefix, distinct, never SkyyAccessories' skyyacc_* or the coming SkyyGear's skyygear*\n", DODGE_CHECK)

# ---------------------------------------------------------------------------------------------------------------- (2) Acro.dodge
rep('''    int li = {EFX}.getAssetMap().getIndex("Dodge_Left");
    int ri = {EFX}.getAssetMap().getIndex("Dodge_Right");
    if (li != Integer.MIN_VALUE && ecc.hasEffect(li)) on = true;
    if (ri != Integer.MIN_VALUE && ecc.hasEffect(ri)) on = true;
''', '''    int li = {EFX}.getAssetMap().getIndex("Dodge_Left");
    int ri = {EFX}.getAssetMap().getIndex("Dodge_Right");
    int fi = {EFX}.getAssetMap().getIndex("Dodge_Forward");   // 0.4.18: the 8-way roll's forward / back effects (SkyySkills assets)
    int bi = {EFX}.getAssetMap().getIndex("Dodge_Back");
    if (li != Integer.MIN_VALUE && ecc.hasEffect(li)) on = true;
    if (ri != Integer.MIN_VALUE && ecc.hasEffect(ri)) on = true;
    if (fi != Integer.MIN_VALUE && ecc.hasEffect(fi)) on = true;
    if (bi != Integer.MIN_VALUE && ecc.hasEffect(bi)) on = true;
''')
rep('''# excluded = excludedState(MovementStates) of this tick (true when the component is missing): review fix - a dodge in an excluded
''', '''# 0.4.18: a "dodge" = any of the 4 roll effects (Dodge_Left / Dodge_Right / Dodge_Forward / Dodge_Back - DODGE_FX); an air roll is no
# excluded state (falling / jumping are not), so it pays like a ground roll.
# excluded = excludedState(MovementStates) of this tick (true when the component is missing): review fix - a dodge in an excluded
''')

# ---------------------------------------------------------------------------------------------------------------- (3) Server Setup rows
ROLL_TEXT = "8-way roll, 13 force, 2 Stamina, 0.25 s safe - fixed in the jar"
rep('''    ("acro.dodgeXp", "XP per dodge", "acrobatics", "dec", "3", "0", "100000", "", "", "live", "", "reload"),
    ("acro.dodgeCooldownMs", "Paid dodge cooldown", "acrobatics", "int", "400", "100", "600000", "", "ms", "live,adv", "", "reload"),
''', '''    ("acro.dodgeXp", "XP per dodge", "acrobatics", "dec", "3", "0", "100000", "", "", "live",
     "Dodge rolls the way you move (8 ways, standing still = back): every roll pays this.", "reload"),
    ("acro.dodgeCooldownMs", "Paid dodge cooldown", "acrobatics", "int", "400", "100", "600000", "", "ms", "live,adv", "", "reload"),
    # 0.4.18 (research/Grapple-Bolt-Spec.md 1.3): the dodge roll's numbers are vanilla's, fixed in the jar's assets - shown, never edited
    ("acro.roll", "Dodge roll", "acrobatics", "text", ROLL_TEXT, "", "", "", "", "ro",
     "Dodge rolls the way you move (standing still = back), in the air too. Vanilla numbers.", "custom:SkillKit"),
''')
before('''assert sum(1 for _r in CFG_ROWS if _r[0] == "mana.classBase") == 1 and sum(1 for _r in CFG_ROWS if _r[0] == "spell.manaDivisor") == 1
''', '''# 0.4.18: the read-only acro.roll row (SkillKit.customGet answers ROLL_TEXT); its numbers are the generated dodge files'
assert ROLL_TEXT == %r and sum(1 for _r in CFG_ROWS if _r[0] == "acro.roll") == 1 and "acro.roll" not in CFG.parse_props(DEFAULTS)
assert all(json.loads(DODGE_FILES["Server/Item/Interactions/Dodge/%%s.json" %% _r[1]])["Costs"] == {"Stamina": 2} for _r in DODGE_ROLLS)
assert all(json.loads(DODGE_FILES["Server/Item/Interactions/Dodge/%%s.json" %% _r[1]])["Next"]["Interactions"][2]["Force"] == 13 for _r in DODGE_ROLLS)
assert _dv_fx["Dodge_Invulnerability"]["Duration"] == 0.25 and len(DODGE_ROLLS) + 2 == 8
''' % ROLL_TEXT)
# the row list is defined before ROLL_TEXT's assert block - define the constant ahead of CFG_ROWS too (the row tuple reads it)
before('''CFG_ROWS = [''', '''ROLL_TEXT = %r   # 0.4.18: the acro.roll info row's text (read-only)
''' % ROLL_TEXT)
rep('''public static String customGet(String key) {
  if ("spell.manaDivisor".equals(key)) return String.valueOf(""" + PKG + """.ManaCost.DIVISOR);
''', '''public static String customGet(String key) {
  if ("spell.manaDivisor".equals(key)) return String.valueOf(""" + PKG + """.ManaCost.DIVISOR);
  if ("acro.roll".equals(key)) return """ + json.dumps(ROLL_TEXT) + """;   // 0.4.18: read-only (the dodge roll's vanilla numbers)
''')

rep("""assert len(CFG_ROWS) == 201, (""", """assert len(CFG_ROWS) == 202, (""")
rep("""fromLevel, got %d" % len(CFG_ROWS))""", """fromLevel; 0.4.18: + the read-only acro.roll, got %d" % len(CFG_ROWS))""")

# ---------------------------------------------------------------------------------------------------------------- jar: assets + manifest text
rep('''Priest heals on party members (Divinity, from SkyyClasses) and running / jumping / big survived falls / dodging (+ the Acrobatics tree Double Jump: jump again in mid-air).''',
    '''Priest heals on party members (Divinity, from SkyyClasses) and running / jumping / big survived falls / dodge rolls (+ the Acrobatics tree Double Jump: jump again in mid-air). The dodge key rolls the way you move: 8 directions, standing still = a back roll (vanilla 2 Stamina, 0.25 s safe, works in the air).''')
rep('''B.assemble(jar, m, OUT, SPELL_FILES)
''', '''ASSET_FILES = dict(SPELL_FILES)   # 0.4.18: + the dodge roll files (DODGE_FILES: Server/Item/Interactions + Server/Entity/Effects/Movement)
assert not set(ASSET_FILES) & set(DODGE_FILES) and all(_p.startswith(("Server/Item/Interactions/", "Server/Entity/Effects/Movement/")) for _p in DODGE_FILES)
ASSET_FILES.update(DODGE_FILES)
B.assemble(jar, m, OUT, ASSET_FILES)
''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands: 0.4.18 adds none"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
_ix = lambda t: s.index(t)
assert _ix("ROLL_TEXT = %r   # 0.4.18: the acro.roll info row" % ROLL_TEXT) < _ix("CFG_ROWS = [") < _ix('    ("acro.roll", "Dodge roll"')
assert _ix("DODGE_FILES = {}") < _ix("def _dodge_clash(names):") < _ix("ASSET_FILES.update(DODGE_FILES)")
assert _ix("_sre.findall(") < _ix("def _dodge_clash(names):") and _ix("_packs = None") < _ix("def _dodge_clash(names):")
for _f, _a in FX:
    assert s.count('getIndex("%s")' % _f) == 1, _f
assert s.count("'Warrior', 'Weapon_Sword_Crude:1,Weapon_Shield_Wood:1'") == 1
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.17 lines changed outside the planned places: %r" % _bad[:5]
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.17,", len(_gone), "0.4.17 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
