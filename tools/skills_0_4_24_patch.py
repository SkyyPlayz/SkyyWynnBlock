"""Derive SkyySkills/build_skyyskills_0.4.24.py from the LIVE generated SkyySkills/build_skyyskills_0.4.23.py (= the tools/deploy_set.py SET
pin; 0.4.23 came from 0.4.22 by tools/skills_0_4_23_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_23_patch.py: rep(old, new) with asserted single anchors, newline-agnostic; 0.4.23
stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_24_patch.py   then   python SkyySkills/build_skyyskills_0.4.24.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.24.py --dir tools/dev/scratch/<task>/skills0424   (bare JVM, -Xverify:all; the folder is deleted)

0.4.24 = THE WOOD WAND SIGNATURE (Skyy 2026-10-08, docs/answered/gear.md: "Wand can shoot a shot that ricochets through eight enemies";
follow-up of SkyyArmory 0.1.14 - docs/log/2026-10.md 09:55 line: "WOOD wand NOT yet: SkyySkills ships Weapon_Wand_Wood (+ Rotten / Tribal)
and wins - needs a SkyySkills handover"). SkyySkills loads after SkyyArmory and its item override of Weapon_Wand_Wood wins the id (SkyyArmory
0.1.13+ is forbidden to ship it), so the signature has to be named HERE.
  THE CHANGE: SkyySkills' generated item overrides of Weapon_Wand_Wood, Weapon_Wand_Wood_Rotten and Weapon_Wand_Tribal (the three users of
    the vanilla Wand_Primary - SkyyArmory's Java already serves all three as wand index 0: its quick shots charge the meter, base 25 x 1.5)
    get EXACTLY the three fields SkyyArmory 0.1.14 gave its 7 metal wands, and nothing else:
      Interactions.Ability1 = "SkyyArmory_Wand_Signature" (SkyyArmory's root: StatsCondition SignatureEnergy 100 % -> ChangeStat -100 % ->
                              the ricochet marker launch)
      Weapon               = the vanilla sword's signature block (EntityStatsToClear ["SignatureEnergy"], StatModifiers SignatureEnergy
                              +20 Additive) - the meter
      ItemAppearanceConditions = the vanilla sword's "signature ready" look (particles on the Handle node at 100 %)
    Generated at build time from the vanilla Template_Weapon_Sword (the SkyyArmory 0.1.14 way, every assert of its block repeated) and
    CHECKED equal to the pinned SkyyArmory jar's 7 metal wands field by field (a SkyyArmory change of the meter stops this build).
    Primary / Secondary (Wand_Primary), InteractionVars (the Mana / 5 cost overrides), every other field: unchanged (asserted: the item
    file differs from 0.4.23's in exactly those 3 keys). Rotten / Tribal: the same vanilla shape (Weapon {}, no Ability1, no look, the
    Particles on a model with a Handle node - checked in Assets.zip), so the same change (trivially the same - reported).
  STOP RULE (deploy_set, for the main session): SkyySkills 0.4.24+ needs SkyyArmory 0.1.14+ (the root it names). This build stops when the
    pinned SkyyArmory is older or its jar lacks the root / the 7 metal wands' fields.
  No Java change (only the version strings), no migration, no new row / key / system / command, no saved-data change. The Wood wand's
  description line is SkyyArmory's lang (items.Weapon_Wand_Wood.description) - not touched here (a SkyyArmory follow-up).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.23.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.24.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.23"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
assert 'VERSION = "0.4.23"' in s and "derived from the generated 0.4.22 by tools/skills_0_4_23_patch.py" in s, "not the live generated 0.4.23"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "SkyyArmory_Wand_Signature" not in s and "WOOD_SIG" not in s, "0.4.23 already has the 0.4.24 parts"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyySkills 0.4.23 - build script (derived from the generated 0.4.22 by tools/skills_0_4_23_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.24 - build script (derived from the generated 0.4.23 by tools/skills_0_4_24_patch.py - edit the patch, not this file;
0.4.23 was derived from the generated 0.4.22 by tools/skills_0_4_23_patch.py; ''')
rep('''0.4.23: THE ROLL REWORK + LOG FIXES (Skyy LOCKED 2026-10-08 sprint-tap roll test; full notes in tools/skills_0_4_23_patch.py). Deploy WITH''',
    '''0.4.24: THE WOOD WAND SIGNATURE (Skyy 2026-10-08 "Wand can shoot a shot that ricochets through eight enemies"; full notes in
  tools/skills_0_4_24_patch.py). Deploy WITH SkyyArmory 0.1.14+ (STOP: SkyySkills 0.4.24+ needs SkyyArmory 0.1.14+ - the root it names).
  SkyySkills' item overrides of Weapon_Wand_Wood / _Wood_Rotten / _Tribal get exactly the 3 fields SkyyArmory 0.1.14 gave its 7 metal
  wands: Interactions.Ability1 = SkyyArmory_Wand_Signature (the ricochet bolt), the vanilla sword's Weapon block (the SignatureEnergy
  meter, 20) and its ItemAppearanceConditions (the ready glow). Generated from the vanilla Template_Weapon_Sword and checked equal to the
  pinned SkyyArmory jar's metal wands. Nothing else changes (Mana costs, Primary / Secondary, Java). No migration, no new row / key / system.
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.24.py, -Xverify:all).
0.4.23: THE ROLL REWORK + LOG FIXES (Skyy LOCKED 2026-10-08 sprint-tap roll test; full notes in tools/skills_0_4_23_patch.py). Deploy WITH''')
rep('VERSION = "0.4.23"', 'VERSION = "0.4.24"')

# ---------------------------------------------------------------------------------------------------------------- the wood wand signature
# after the live-set jar loop (it knows the pinned SkyyArmory version: _armory_pin) and before the pack-mod scan; SPELL_FILES is final here
# except for these 3 item texts (the jar is assembled from SPELL_FILES at the end; nothing between compares their bytes)
WOOD_SIG_PY = r'''# ================= 0.4.24 THE WOOD WAND SIGNATURE (Skyy 2026-10-08 "Wand can shoot a shot that ricochets through eight enemies";
# tools/skills_0_4_24_patch.py). SkyySkills' item overrides of the 3 users of the vanilla Wand_Primary get exactly the 3 fields SkyyArmory
# 0.1.14 gave its 7 metal wands (Ability1 root, the sword's signature Weapon block, its ready look) - generated from the vanilla
# Template_Weapon_Sword like SkyyArmory does, then checked equal to the pinned SkyyArmory jar's wands. Nothing else in the files changes.
WOOD_SIG = ["Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal"]
WOOD_SIG_ROOT = "SkyyArmory_Wand_Signature"          # SkyyArmory 0.1.14's Ability1 root (Server/Item/RootInteractions/Weapons/Wand/SkyyArmory/)
WOOD_SIG_MAX = 20                                    # SkyyArmory's SIG_MAX (the vanilla sword's meter)
WOOD_SIG_ARMORY = (0, 1, 14)                         # STOP: SkyySkills 0.4.24+ needs SkyyArmory 0.1.14+
WOOD_SIG_METALS = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]


def wood_sig_fail(msg):
    raise SystemExit("wood wand signature (0.4.24): " + msg)


with zipfile.ZipFile(ASSETS) as _wz:
    _wzn = _wz.namelist()

    def _wread(base, pre="Server/Item/Items/"):
        _h = [_n for _n in _wzn if _n.startswith(pre) and _n.endswith("/%s.json" % base)]
        if len(_h) != 1:
            wood_sig_fail("%d x %s.json under %s in Assets.zip (want exactly one)" % (len(_h), base, pre))
        return _h[0], json.loads(_wz.read(_h[0]).decode("utf-8-sig"))
    # (1) the vanilla shapes SkyyArmory 0.1.14 copies (a game update that changes them stops the build - its asserts repeated)
    _wsp, _vsw = _wread("Template_Weapon_Sword")
    if _vsw.get("Parent") is not None or (_vsw.get("Interactions") or {}).get("Ability1") != "Root_Weapon_Sword_Signature_Vortexstrike" \
            or sorted(_vsw.get("Weapon") or {}) != ["EntityStatsToClear", "StatModifiers"] or _vsw["Weapon"]["EntityStatsToClear"] != ["SignatureEnergy"] \
            or _vsw["Weapon"]["StatModifiers"] != {"SignatureEnergy": [{"Amount": 20, "CalculationType": "Additive"}]}:
        wood_sig_fail("the vanilla sword's signature meter changed: %s" % _vsw.get("Weapon"))
    WOOD_SIG_WEAPON = json.loads(json.dumps(_vsw["Weapon"]))
    WOOD_SIG_WEAPON["StatModifiers"]["SignatureEnergy"][0]["Amount"] = WOOD_SIG_MAX
    WOOD_SIG_LOOK = json.loads(json.dumps(_vsw["ItemAppearanceConditions"]))
    if list(WOOD_SIG_LOOK) != ["SignatureEnergy"] or len(WOOD_SIG_LOOK["SignatureEnergy"]) != 1 or WOOD_SIG_LOOK["SignatureEnergy"][0]["Condition"] != [100, 100]:
        wood_sig_fail("the vanilla sword's ready look changed: %s" % WOOD_SIG_LOOK)
    _wlp = [_p for _k in ("Particles", "FirstPersonParticles") for _p in WOOD_SIG_LOOK["SignatureEnergy"][0].get(_k, [])]
    if not _wlp or not all(_p.get("TargetNodeName") == "Handle" and _p.get("TargetEntityPart") == "PrimaryItem" for _p in _wlp):
        wood_sig_fail("the vanilla sword's ready look no longer sits on the Handle node: %s" % _wlp)
    _wst = [_n for _n in _wzn if _n.startswith("Server/Entity/Stats/") and _n.endswith("/SignatureEnergy.json")]
    if len(_wst) != 1 or json.loads(_wz.read(_wst[0]).decode("utf-8-sig")).get("Max") != 0:
        wood_sig_fail("the vanilla SignatureEnergy stat changed (%s)" % _wst)
    # (2) each wand: still the vanilla shape this change was made for (Primary = Secondary = Wand_Primary, Weapon {}, no Ability1, no look),
    # its model has the Handle node the ready look sits on, and no other vanilla item inherits it by Parent
    for _wi in WOOD_SIG:
        _wp, _wv = _wread(_wi)
        if _wv.get("Parent") is not None or _wv.get("Interactions") != {"Primary": "Wand_Primary", "Secondary": "Wand_Primary"} \
                or _wv.get("Weapon") != {} or "ItemAppearanceConditions" in _wv:
            wood_sig_fail("the vanilla %s changed shape (Interactions %s, Weapon %s) - the signature handover needs a look" % (
                _wi, _wv.get("Interactions"), _wv.get("Weapon")))
        _wm = [_n for _n in _wzn if _n.startswith("Common/") and _n.endswith("/" + _wv["Model"])]
        if len(_wm) != 1 or b'"Handle"' not in _wz.read(_wm[0]):
            wood_sig_fail("%s's model %s has no Handle node (the ready look's anchor)" % (_wi, _wv.get("Model")))
    _wheirs = []
    for _n in _wzn:
        if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
            _b = _wz.read(_n)
            if b'"Parent"' in _b and any(('"%s"' % _wi).encode() in _b for _wi in WOOD_SIG):
                try:
                    _pj = json.loads(_b.decode("utf-8-sig"))
                except ValueError:
                    continue
                if isinstance(_pj, dict) and _pj.get("Parent") in WOOD_SIG:
                    _wheirs.append(_n)
    if _wheirs:
        wood_sig_fail("vanilla items inherit a wood wand by Parent (they would get the signature too): %s" % _wheirs[:4])
# (3) the pinned SkyyArmory (the root's owner): 0.1.14+, ships the root, its 7 metal wands carry exactly these 3 fields
if _armory_pin is None or tuple(int(_x) for _x in _armory_pin.split(".")) < WOOD_SIG_ARMORY:
    wood_sig_fail("STOP: SkyySkills 0.4.24+ needs SkyyArmory 0.1.14+ (the root %s it names) - tools/deploy_set.py SET pins SkyyArmory %s" % (
        WOOD_SIG_ROOT, _armory_pin))
_wjp = os.path.join(os.path.dirname(HERE), "SkyyArmory", "SkyyArmory-%s.jar" % _armory_pin)
WOOD_SIG_CHECKED = None
if os.path.isfile(_wjp):
    with zipfile.ZipFile(_wjp) as _wj:
        _wjn = _wj.namelist()
        _wr = [_n for _n in _wjn if _n.startswith("Server/Item/RootInteractions/") and _n.endswith("/%s.json" % WOOD_SIG_ROOT)]
        if len(_wr) != 1:
            wood_sig_fail("SkyyArmory %s ships %d x %s.json (want exactly one) - SkyySkills 0.4.24+ needs SkyyArmory 0.1.14+" % (_armory_pin, len(_wr), WOOD_SIG_ROOT))
        if [_n for _n in _wjn if _n.startswith("Server/Item/Items/") and os.path.basename(_n)[:-5] in WOOD_SIG]:
            wood_sig_fail("SkyyArmory %s ships a wood wand item file - two overrides of one id" % _armory_pin)
        for _m in WOOD_SIG_METALS:
            _h = [_n for _n in _wjn if _n.startswith("Server/Item/Items/") and _n.endswith("/Weapon_Wand_%s.json" % _m)]
            _aj = json.loads(_wj.read(_h[0]).decode("utf-8-sig")) if len(_h) == 1 else {}
            if (_aj.get("Interactions") or {}).get("Ability1") != WOOD_SIG_ROOT or _aj.get("Weapon") != WOOD_SIG_WEAPON \
                    or _aj.get("ItemAppearanceConditions") != WOOD_SIG_LOOK:
                wood_sig_fail("SkyyArmory %s's Weapon_Wand_%s does not carry the same signature fields (Ability1 %s, Weapon %s) - the wood "
                              "wands must match the metal ones" % (_armory_pin, _m, (_aj.get("Interactions") or {}).get("Ability1"), _aj.get("Weapon")))
    WOOD_SIG_CHECKED = _armory_pin
else:
    print("wood wand signature: NOTE SkyyArmory %s is not built here - the metal wands' fields were not compared" % _armory_pin)
# (4) the 3 item overrides: + exactly the 3 fields (Ability1 appended to Interactions, Weapon in place, the look appended - SkyyArmory's order)
WOOD_SIG_FILES = []
for _wi in WOOD_SIG:
    _wp = [_p for _p in SPELL_FILES if _p.startswith("Server/Item/Items/") and _p.endswith("/%s.json" % _wi)]
    if len(_wp) != 1:
        wood_sig_fail("%s is not one of this jar's item overrides (%s)" % (_wi, _wp))
    _wold = json.loads(SPELL_FILES[_wp[0]])
    if _wold.get("Interactions") != {"Primary": "Wand_Primary", "Secondary": "Wand_Primary"} or _wold.get("Weapon") != {} \
            or "ItemAppearanceConditions" in _wold or not _wold.get("InteractionVars"):
        wood_sig_fail("this jar's %s override is not the expected shape: %s" % (_wi, sorted(_wold)))
    _wnew = json.loads(SPELL_FILES[_wp[0]])
    _wnew["Interactions"]["Ability1"] = WOOD_SIG_ROOT
    _wnew["Weapon"] = json.loads(json.dumps(WOOD_SIG_WEAPON))
    _wnew["ItemAppearanceConditions"] = json.loads(json.dumps(WOOD_SIG_LOOK))
    assert sorted(_k for _k in set(_wnew) | set(_wold) if _wnew.get(_k) != _wold.get(_k)) == ["Interactions", "ItemAppearanceConditions", "Weapon"], _wi
    assert [_k for _k in _wnew if _k != "ItemAppearanceConditions"] == list(_wold) and list(_wnew)[-1] == "ItemAppearanceConditions"
    assert _wnew["Interactions"] == {"Primary": "Wand_Primary", "Secondary": "Wand_Primary", "Ability1": WOOD_SIG_ROOT}
    assert _wnew["InteractionVars"] == _wold["InteractionVars"]
    _txt = json.dumps(_wnew, indent=2, ensure_ascii=True) + "\n"
    assert json.loads(_txt) == _wnew and all(ord(ch) < 128 for ch in _txt)
    SPELL_FILES[_wp[0]] = _txt
    WOOD_SIG_FILES.append(_wp[0])
assert len(WOOD_SIG_FILES) == 3 and len(set(WOOD_SIG_FILES)) == 3
print("wood wand signature (0.4.24): %s get Ability1 %s + the sword's meter (%d) + its ready look; checked equal to SkyyArmory %s's 7 metal "
      "wands%s" % (", ".join(WOOD_SIG), WOOD_SIG_ROOT, WOOD_SIG_MAX, _armory_pin, "" if WOOD_SIG_CHECKED else " (NOT compared: jar missing)"))
'''
rep('''_pk_found, _other, _pk_mana = [], [], []
''', WOOD_SIG_PY + '''_pk_found, _other, _pk_mana = [], [], []
''')

assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "0.4.24 adds no system / command"
with open(dst, "w", encoding="utf8", newline="") as f:
    f.write(s.replace(LF, NL))
print("wrote %s" % os.path.relpath(dst, ROOT))
