"""Derive SkyyClasses/build_skyyclasses_0.1.50.py from the GENERATED SkyyClasses 0.1.49 (build_skyyclasses_0.1.49.py = the tools/deploy_set.py
SET pin; the EDITED lineage: Skyy's hand-edited 0.1.6 (commit ab75b6c) -> classes_0_1_7_patch.py -> ... -> classes_0_1_49_patch.py -> 0.1.49).
Never re-run an older patch. Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.1.49
(tools/soundpass_gen.Patch). Line endings kept.
Run:  python tools/classes_0_1_50_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.50.py   (never --deploy)
      then  python SkyyClasses/test_skyyclasses_0.1.50.py
Pairs with SkyyTrees 0.6.4 (tools/trees_0_6_4_patch.py + tools/trees_v3_data.py r064_apply). Art: art/r064-icons (tools/art/make_r064_icons.py).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.1.50 (2026-10-24) = PER-PATH CAPSTONES + THE ASSASSIN'S SECOND A1-ALT, the SkyyClasses part (with SkyyTrees 0.6.4). Skyy
  (docs/answered/classes.md 2026-10-24 PER-PATH CAPSTONES + 2ND ASSASSIN ALT; the 0.6.3 rule: "the A1 alts are supposed to be late game.
  both options are supposed to be significantly better than the A1 sacred heal. and its supposed to be an either or. the tree splits, you
  pick a path, and get locked out of the other.") - "Start the next queued rounds from RESUME (... per-path capstones + 2nd Assassin alt ...)".
  1. SHADOW MARK (id ShadowMark, the Assassin's A1-alt B, tier 4 - the end of the Shadow Mark path of the Assassin tree; SkyyTrees 0.6.4):
     marks the enemy you look at (up to ab.ShadowMark range 24 blocks - Shadow Step's reach) for 8 s: it is EXPOSED - every hit on it from
     anyone deals +20 % (x the ability's main effect: level, Power, the class tree, the A1-alt bonus x1.5 = +30 % at Lv 1; at most cap 60 %)
     through the shared Marked map (Abil.outMult, the same as Hunter's Mark; a stronger mark already on it is kept) - and your next hit is a
     First Strike (+CL_STRIKE % x main, the Cloak's window). A Shadow-Marked enemy that dies takes killCd 8 s off Shadow Mark's cooldown
     (whoever killed it; fix round: ONCE a cast - a mark passed on by Death Sentence or a 2nd landing kill gives no more). Shapes: walk Shadow Mark; sprint Marked Run (+ haste 20 % for 3 s); air Mark from Above (on landing: every enemy
     within 5 blocks at 60 %); crouch (the alt key) PATIENT MARK = the mark lasts 150 % and you are cloaked 2 s. Cost 7 Mana + 2 Stamina /
     24 s (crouch 26 s) - in line with Vanishing Act (7 + 2 / 28 s). Modifiers Duration, Power, Radius (fix round: + reach, so Patient
     Mark - the shape an alt always casts - uses it; Mark from Above's landing circle too), Efficiency. Numbers:
     Server Setup -> Classes -> Assassin abilities "Shadow Mark numbers" (ab.ShadowMark.numbers; a missing key = its default). Rune
     SkyyAbility_Assassin_ShadowMark (art/r064-icons ShadowMark.png). Engine use: only the parts the other abilities already use (lookMob,
     the Marked map, strikeArm, cloakAt, haste, landJob, near / enemy / losOk, the Inspect damage hook); world-thread only.
  2. THE 8 NEW PATH CAPSTONES (UpFx codes; SkyyTrees 0.6.4 sells them only while tree:reads:SkyyClasses lists Class.fx.<code>), numbers in
     Server Setup -> Classes "Path capstone numbers" (ab.Capstones2.numbers):
       xLegion    Oath of Legions (Warrior, Guardian's Oath): the oath binds every party member within its reach at once (each shares as the
                  main one), and the Warrior takes legionCut 15 % less while it holds (on top of the cut, 60 % at most)
       xShatterpt Shatterpoint (Spellblade, Shattering Arc): every enemy the arc hits gives 2 Momentum back (10 a cast), +30 % to Breached
       xRaincall  Raincaller (Archer, Arrow Rain): the rain drifts 1 block a pulse toward the enemy nearest its centre; +30 % to rooted enemies
       xFistStorm Storm of Fists (Monk, Hundred Fists): a shockwave every 5th combo hit (50 % of the count), through every enemy in the aura
       xSupernova Supernova (Mage, Starfall): when Starfall ends, a blast at its centre - 20 % of a star per star that hit (200 % at most)
       xCovenant  Saint's Covenant (Priest, Martyr's Grace): no drop between jumps; healing it cannot give becomes a ward (10 % max Health)
       xShroud    Shroud of Night (Assassin, Vanishing Act): enemies in the smoke are Exposed +20 %; the cloak holds 3 s longer inside it
                  (fix round: every shape - the cloak's own length + 3 s at most, and it lasts 3 s past your last moment in the smoke)
       xSentence  Death Sentence (Assassin, Shadow Mark): a Shadow-Marked kill passes the mark to the nearest enemy within 8 blocks (a fresh
                  timer) and readies your First Strike (once every 4 s)
     Three Shadow Mark path passives use the ability parameter codes every ability has (a.ShadowMark.dur / cost / pow).
  FIX ROUND (critics): the Exposed / Marked map never loses time to a weaker or shorter write (exposeOn keeps the later end; Hunter's Mark
  / Arrow Rain's mark keep a stronger Shadow Mark); a Shadow Mark kill hook that throws is caught on its own (the class tree's on-hit
  effects still run); the second capstone row is called "Path capstone numbers". FIX ROUND 2: the kill refund only while that cast's
  mark runs and only for the profile that cast it (smarkPrune drops spent tokens, a quit drops it); Hunter's Mark keeps only a RUNNING
  stronger Shadow Mark; the Radius line says "+X blocks reach" (the alt key always casts Patient Mark).
  SAVED DATA: none (two new Server Setup rows, read as their defaults while missing; the Assassin's alt pick "B" = Shadow Mark). ROLLBACK
  to 0.1.49: together with SkyyTrees 0.6.3 (0.1.49 knows no Shadow Mark - a loadout naming it falls back to the defaults; the new capstone
  codes are ignored).

'''

P = G.Patch(os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.49.py"), os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.50.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.1.49"') and P.s.startswith('"""SkyyClasses 0.1.49 - build script') and P.has("ALT_POW") and not P.has("ShadowMark"), "not the SET pin 0.1.49"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")

P.rep('''"""SkyyClasses 0.1.49 - build script (javassist via jpype). GENERATED by tools/classes_0_1_49_patch.py from the generated 0.1.48 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> ... -> classes_0_1_49_patch.py) - edit the patch, not this file.
Run: python SkyyClasses/build_skyyclasses_0.1.49.py -> SkyyClasses/SkyyClasses-0.1.49.jar (never --deploy). Test: python SkyyClasses/test_skyyclasses_0.1.49.py
''', '''"""SkyyClasses 0.1.50 - build script (javassist via jpype). GENERATED by tools/classes_0_1_50_patch.py from the generated 0.1.49 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> ... -> classes_0_1_50_patch.py) - edit the patch, not this file.
Run: python SkyyClasses/build_skyyclasses_0.1.50.py -> SkyyClasses/SkyyClasses-0.1.50.jar (never --deploy). Test: python SkyyClasses/test_skyyclasses_0.1.50.py
''' + NOTE + '''=== 0.1.49 (history) ===
''')
P.rep('VERSION = "0.1.49"', 'VERSION = "0.1.50"')

# ================================================================================================ 1. SHADOW MARK - the tables
P.rep('''    ('ShatteringArc', 'Shattering Arc', 'Spellblade', 4, True, False),
]
assert sorted((c, t) for _i, _n, c, t, _b, _p in ABILS) == sorted([(c, t) for c in ("Mage", "Priest", "Monk", "Warrior", "Berserker", "Archer", "Spellblade") for t in range(5)] + [("Assassin", t) for t in range(4)])
''', '''    ('ShatteringArc', 'Shattering Arc', 'Spellblade', 4, True, False),
    # 0.1.50: the Assassin's second A1-alt (docs/answered/classes.md 2026-10-24 2ND ASSASSIN ALT) - LAST, so every older index stays
    ('ShadowMark', 'Shadow Mark', 'Assassin', 4, True, False),
]
assert sorted((c, t) for _i, _n, c, t, _b, _p in ABILS) == sorted([(c, t) for c in ("Mage", "Priest", "Monk", "Warrior", "Berserker", "Archer", "Spellblade", "Assassin") for t in range(5)])   # 0.1.50: the Assassin has 5
''')
P.rep('''    ('ShatteringArc', 'SA', 'abilsb', [(16, 20), (16, 20), (16, 22), (14, 20)]),
]
''', '''    ('ShatteringArc', 'SA', 'abilsb', [(16, 20), (16, 20), (16, 22), (14, 20)]),
    # 0.1.50: Shadow Mark - power 16 like Vanishing Act (the Assassin split 43 / 57 -> 7 Mana + 2 Stamina), 24 s (crouch / air 26 s)
    ('ShadowMark', 'SM', 'abilas', [(16, 24), (16, 24), (16, 26), (16, 26)]),
]
''')
P.rep('''    'ShatteringArc': ['Shattering Arc', 'Shattering Rush', 'Shattering Fall', 'Measured Strike'],
}
''', '''    'ShatteringArc': ['Shattering Arc', 'Shattering Rush', 'Shattering Fall', 'Measured Strike'],
    'ShadowMark': ['Shadow Mark', 'Marked Run', 'Mark from Above', 'Patient Mark'],   # 0.1.50
}
''')
P.rep('''    'ShatteringArc': [(9, 2, 20), (9, 2, 20), (9, 2, 22), (8, 1, 20)],
}
''', '''    'ShatteringArc': [(9, 2, 20), (9, 2, 20), (9, 2, 22), (8, 1, 20)],
    'ShadowMark': [(7, 2, 24), (7, 2, 24), (7, 2, 26), (7, 2, 26)],   # 0.1.50
}
''')
P.rep('''NEW3_IDS = ['ArcaneBreach', 'ElementalImbue', 'Sunder', 'RiftCleave', 'ShatteringArc']   # 0.1.25: the Spellblade - costs + cooldown in their numbers row (AbilNum)
''', '''NEW3_IDS = ['ArcaneBreach', 'ElementalImbue', 'Sunder', 'RiftCleave', 'ShatteringArc']   # 0.1.25: the Spellblade - costs + cooldown in their numbers row (AbilNum)
NEW3_IDS = NEW3_IDS + ['ShadowMark']   # 0.1.50: Shadow Mark keeps its walking cost + cooldown in its numbers row too (AbilNum.SM_*)
''')
# the numbers rows: Shadow Mark + the new capstones (two new text rows; a missing key / row = its default)
P.rep('''                             ("holyOverlap", "CP_HOLYO", 150.0, "100", "300")):
    _n("ab.Capstones." + _k, _f, "dec", _d, _lo, _hi, "", "abilx", _k, _k)
''', '''                             ("holyOverlap", "CP_HOLYO", 150.0, "100", "300")):
    _n("ab.Capstones." + _k, _f, "dec", _d, _lo, _hi, "", "abilx", _k, _k)
# 0.1.50 SHADOW MARK (the Assassin's A1-alt B): the walking cost + cooldown and its numbers (s / blocks / %)
for _k, _f, _d, _lo, _hi in (("mana", "SM_MANA", 7.0, "0", "1000"), ("stamina", "SM_STAM", 2.0, "0", "100"), ("cooldown", "SM_CD", 24.0, "0", "600"),
                             ("range", "SM_RANGE", 24.0, "2", "64"), ("mark", "SM_MARK", 20.0, "0", "100"), ("cap", "SM_CAP", 60.0, "0", "200"),
                             ("time", "SM_TIME", 8.0, "0.5", "60"), ("crouchTime", "SM_CROUCHTIME", 150.0, "50", "400"),
                             ("crouchCloak", "SM_CROUCHCLOAK", 2.0, "0", "30"), ("sprintSpeed", "SM_SPRINTSPEED", 20.0, "0", "80"),
                             ("sprintTime", "SM_SPRINTTIME", 3.0, "0", "30"), ("airRadius", "SM_AIRRADIUS", 5.0, "1", "16"),
                             ("airPower", "SM_AIRPOWER", 60.0, "0", "200"), ("killCd", "SM_KILLCD", 8.0, "0", "600")):
    _n("ab.ShadowMark." + _k, _f, "dec", _d, _lo, _hi, "", "abilas", _k, _k)
# 0.1.50 THE PER-PATH CAPSTONES (UpFx; % / s / blocks) - their own text row "ab.Capstones2.numbers" (the first one is full)
for _k, _f, _d, _lo, _hi in (("legionCut", "CP2_LEGIONCUT", 15.0, "0", "50"), ("shatterMom", "CP2_SHATTERMOM", 2.0, "0", "10"),
                             ("shatterMax", "CP2_SHATTERMAX", 10.0, "0", "20"), ("shatterBreach", "CP2_SHATTERB", 30.0, "0", "200"),
                             ("rainStep", "CP2_RAINSTEP", 1.0, "0", "4"), ("rainRoot", "CP2_RAINROOT", 30.0, "0", "200"),
                             ("fistPct", "CP2_FISTPCT", 50.0, "10", "100"), ("novaPer", "CP2_NOVAPER", 20.0, "0", "100"),
                             ("novaMax", "CP2_NOVAMAX", 200.0, "0", "1000"), ("covWard", "CP2_COVWARD", 10.0, "0", "50"),
                             ("shroudExpose", "CP2_SHROUDX", 20.0, "0", "60"), ("shroudHold", "CP2_SHROUDT", 3.0, "0", "30"),
                             ("sentRange", "CP2_SENTRANGE", 8.0, "1", "32"), ("sentGap", "CP2_SENTGAP", 4.0, "0", "60")):
    _n("ab.Capstones2." + _k, _f, "dec", _d, _lo, _hi, "", "abilx", _k, _k)
''')
P.rep('''                                  + ['ClassTree', 'Capstones'])   # 0.1.43 fix round: the class-tree effect numbers; fix round 2: + the capstones
''', '''                                  + ['ClassTree', 'Capstones']   # 0.1.43 fix round: the class-tree effect numbers; fix round 2: + the capstones
                                  + ['ShadowMark', 'Capstones2'])   # 0.1.50: Shadow Mark + the per-path capstones
''')
P.rep('''{'Momentum': 'Momentum', 'Elements': 'Element statuses', 'ClassTree': 'Class tree', 'Capstones': 'Capstone'}[_aid]''',
      '''{'Momentum': 'Momentum', 'Elements': 'Element statuses', 'ClassTree': 'Class tree', 'Capstones': 'Capstone', 'Capstones2': 'Path capstone'}[_aid]''')
P.rep('''if _aid not in NEW2_IDS + NEW3_IDS + ["Momentum", "Elements", "ClassTree", "Capstones"] else''',
      '''if _aid not in NEW2_IDS + NEW3_IDS + ["Momentum", "Elements", "ClassTree", "Capstones", "Capstones2"] else''')
P.rep('''         "key=value: hits / cuts / slows %, times s, Mana + Stamina a second; no key = its default" if _aid == "Capstones" else   # 0.1.43 fix 2
''', '''         "key=value: hits / cuts / slows %, times s, Mana + Stamina a second; no key = its default" if _aid == "Capstones" else   # 0.1.43 fix 2
         "key=value: cuts / bonuses / blasts %, Momentum, blocks, s; no key = its default" if _aid == "Capstones2" else   # 0.1.50
''')
P.rep('''assert _aff == 37 + 20 + 16 + 60 + 20, _aff     # the plan's "all 37 shape rows PASS" + 0.1.23: Monk 5 x 4, Assassin 4 x 4 + 0.1.24: 15 x 4 + 0.1.25: 5 x 4
''', '''assert _aff == 37 + 20 + 16 + 60 + 20 + 4, _aff     # the plan's "all 37 shape rows PASS" + 0.1.23: Monk 5 x 4, Assassin 4 x 4 + 0.1.24: 15 x 4 + 0.1.25: 5 x 4 + 0.1.50: Shadow Mark 4
''')
P.rep('''    "VanishingAct": "A short cloak + smoke: enemies inside lose you, slowed. Sprint - behind you. Air - where you land. Crouch - Ambush Smoke.",
''', '''    "VanishingAct": "A short cloak + smoke: enemies inside lose you, slowed. Sprint - behind you. Air - where you land. Crouch - Ambush Smoke.",
    "ShadowMark": "Exposes the enemy you look at (more damage from everyone) + a First Strike. Crouch (your alt key) - Patient Mark: longer, cloaked.",   # 0.1.50
''')
P.rep('''    'ShatteringArc': ['Power', 'Radius', 'Knockback', 'Leech', 'Echo'],
}
''', '''    'ShatteringArc': ['Power', 'Radius', 'Knockback', 'Leech', 'Echo'],
    # 0.1.50: Shadow Mark (no class-file list yet - proposed here: the generic four; Radius = + reach, and Mark from Above's landing circle)
    'ShadowMark': ['Duration', 'Power', 'Radius', 'Efficiency'],
}
''')
P.rep('''           'ShatteringArc': 'damage per stack',
''', '''           'ShatteringArc': 'damage per stack',
           'ShadowMark': 'Exposed bonus',   # 0.1.50
''')
P.rep('''+ ['ArcaneBreach', 'ElementalImbue', 'Sunder', 'RiftCleave', 'ShatteringArc']   # 0.1.24 + 0.1.25
''', '''+ ['ArcaneBreach', 'ElementalImbue', 'Sunder', 'RiftCleave', 'ShatteringArc'] + ['ShadowMark']   # 0.1.24 + 0.1.25 + 0.1.50
''')
P.rep('''(+{SA_BREACHPERSTACK} % per Momentum, at most {SA_BREACHCAP} %) for {SA_TIME} s (+{SA_TIMEPERSTACK} s per Momentum).",
}
''', '''(+{SA_BREACHPERSTACK} % per Momentum, at most {SA_BREACHCAP} %) for {SA_TIME} s (+{SA_TIMEPERSTACK} s per Momentum).",
    "ShadowMark": "Marks the enemy you look at (up to {SM_RANGE} blocks) for {SM_TIME} s: it is Exposed - every hit on it from anyone deals +{SM_MARK} % (at most {SM_CAP} %) - and your next hit is a First Strike (+{CL_STRIKE} %). A marked kill takes {SM_KILLCD} s off the cooldown (once a cast).",   # 0.1.50
}
''')
# the class-tree codes this build applies: + the 8 new capstones and the 3 Shadow Mark parameters (tools/trees_v3_data.py R064_*; only
# SkyyTrees 0.6.4 lays their nodes out - this build reads the base tables, so it adds them here) + the Assassin's A4b in the shared tables
P.rep('''import trees_v3_data as V3D
V3D.check()
assert dict((_a, list(_m)) for _a, _m in V3D.CLASS_MODS.items())''', '''import trees_v3_data as V3D
V3D.check()
V3D.r064_lines()   # 0.1.50: Shadow Mark = the Assassin's A4b (CLASS_LINES / CLASS_MODS; the layout stays SkyyTrees 0.6.4's)
assert dict((_a, list(_m)) for _a, _m in V3D.CLASS_MODS.items())''')
P.rep('''UPFX_CODES = sorted(_upc)
UPFX_PER = _uper
''', '''for _c in V3D.R064_CODES:   # 0.1.50: the 8 new path capstones (1 rank)
    _upc.add(_c)
    _uper.setdefault(_c, 1.0)
for _p in V3D.R064_PASSIVES:   # 0.1.50: the Shadow Mark path passives (a.ShadowMark.dur / cost / pow)
    for _c, _v in _p["hook"][1]:
        _upc.add(_c)
        _uper.setdefault(_c, float(_v))
UPFX_CODES = sorted(_upc)
UPFX_PER = _uper
assert all(_c in UPFX_CODES for _c in V3D.R064_CODES + V3D.R064_APCODES) and len(V3D.R064_CODES) == 8
''')
P.rep('''assert "Class.Mage.A1" in TREE_READS and "Class.Mage.A4b" in TREE_READS and "Class.Assassin.A4b" not in TREE_READS and "M1A" not in TREE_READS
''', '''assert "Class.Mage.A1" in TREE_READS and "Class.Mage.A4b" in TREE_READS and "Class.Assassin.A4b" in TREE_READS and "M1A" not in TREE_READS   # 0.1.50: + Shadow Mark
assert all("Class.fx." + _c in TREE_READS for _c in V3D.R064_CODES), "0.1.50: SkyyTrees 0.6.4 sells the new capstones only while they are listed"
''')
P.rep('''UPFX_STATE = [''', '''UPFX_STATE_050 = ['SENT']   # 0.1.50: UUID -> Long the last Death Sentence
UPFX_STATE = [''')
P.rep('''for _f in UPFX_STATE + ["VC"]:
    F(upfx, ''', '''for _f in UPFX_STATE + UPFX_STATE_050 + ["VC"]:   # 0.1.50: + SENT
    F(upfx, ''')
P.rep('''      FSHIT, GKHIT, BUFF, VANT, CLOAKEND, RUMBLE, UNTOUCH, CLONES, CASC, TICKAT, BLOCKT, IMBT, BOWT, PRISM, NOVA, FURYN, CHG };   // fix 2: + NOVA, FURYN, CHG
''', '''      FSHIT, GKHIT, BUFF, VANT, CLOAKEND, RUMBLE, UNTOUCH, CLONES, CASC, TICKAT, BLOCKT, IMBT, BOWT, PRISM, NOVA, FURYN, CHG, SENT };   // fix 2: + NOVA, FURYN, CHG; 0.1.50: + SENT
''')
# the rune's picture: art/r064-icons (its own manifest; art/ability-icons is counted by the pinned builds)
P.rep('''    _png = _art_icon(_a[2], ICON_STANDIN.get(_a[0], _a[0]))   # 0.1.36: the class's own approved art (0.1.24 stand-ins: Challenge, Guardian's Oath)
''', '''    _png = _r064_icon() if _a[0] == "ShadowMark" else _art_icon(_a[2], ICON_STANDIN.get(_a[0], _a[0]))   # 0.1.36: the class's own approved art (0.1.24 stand-ins: Challenge, Guardian's Oath); 0.1.50: Shadow Mark = art/r064-icons
''')
P.rep('''ICON_STANDIN = {"Challenge": "Unbreakable", "GuardiansOath": "BulwarkStance"}''', '''_R064_DIR = os.path.join(os.path.dirname(HERE), "art", "r064-icons")
_R064_MAN = json.load(open(os.path.join(_R064_DIR, "manifest.json"), encoding="utf8"))


def _r064_icon():
    """0.1.50: the Shadow Mark picture (tools/art/make_r064_icons.py: the approved Assassin frame + a new symbol), the manifest's bytes"""
    _p = _R064_MAN["ability"]["file"]
    _f = [_x for _x in _R064_MAN["files"] if _x["path"] == _p]
    _d = open(os.path.join(_R064_DIR, *_p.split("/")), "rb").read()
    assert _p == "Common/Icons/Abilities/Assassin/ShadowMark.png" and len(_f) == 1 and _hl36.sha256(_d).hexdigest() == _f[0]["sha256"] and len(_d) == _f[0]["bytes"], "0.1.50: %s is not the r064 manifest's file" % _p
    assert SA.png_size(_d) == (64, 64) and _d[24:26] == b"\\x08\\x06", "0.1.50: the Shadow Mark icon is not a 64 x 64 RGBA8 PNG"
    return _d


ICON_STANDIN = {"Challenge": "Unbreakable", "GuardiansOath": "BulwarkStance"}''')
# the ability index constant + the mob map
P.rep('''("RIFT", "RiftCleave"), ("SHATTER", "ShatteringArc")):
    F(abdefs, ''', '''("RIFT", "RiftCleave"), ("SHATTER", "ShatteringArc"),
                  # 0.1.50: the Assassin's Shadow Mark (the LAST index - the Spellblade range checks are bounded by SHATTER below)
                  ("SMARK", "ShadowMark")):
    F(abdefs, ''')
P.rep('''           "MOMS", "MOMX", "IMBUE", "BREACH", "SUNDER", "SHOCKD", "STAGD", "CHILLS", "DOTS", "IMBN", "SBP"):
''', '''           "MOMS", "MOMX", "IMBUE", "BREACH", "SUNDER", "SHOCKD", "STAGD", "CHILLS", "DOTS", "IMBN", "SBP",
           # 0.1.50: mob Ref -> Object[] Shadow Mark {UUID caster, double[] {until, Exposed %, secs, First Strike bonus %}}
           # fix round: UUID -> Object[] {Long until, String profile key} the cast whose kill refund is still unused (one refund a cast)
           "SMARKS", "SMCUT"):
''')

# ================================================================================================ 2. SHADOW MARK - the Java
# the Spellblade-only range checks: the new last index must not count as a Spellblade ability
P.rep('''  if (ai >= @PKG@.AbilDefs.BREACH) return landSb(j, st, cb, cr, at, now);   // 0.1.25: the Spellblade's mid-air shapes
''', '''  if (ai == @PKG@.AbilDefs.SMARK) return "mark:" + smarkLand(j, cb, cr, at, now);   // 0.1.50: Mark from Above
  if (ai >= @PKG@.AbilDefs.BREACH && ai <= @PKG@.AbilDefs.SHATTER) return landSb(j, st, cb, cr, at, now);   // 0.1.25: the Spellblade's mid-air shapes (0.1.50: bounded)
''')
P.rep('''  if (j.ai >= @PKG@.AbilDefs.BREACH) return echoRun3(j, st, cb, cr, now);   // 0.1.25: Sunder, Rift Cleave, Shattering Arc
''', '''  if (j.ai >= @PKG@.AbilDefs.BREACH && j.ai <= @PKG@.AbilDefs.SHATTER) return echoRun3(j, st, cb, cr, now);   // 0.1.25: Sunder, Rift Cleave, Shattering Arc (0.1.50: bounded)
''')
P.rep('''  if (ai >= @PKG@.AbilDefs.BREACH) { String t25 = modText3(ai, mi, lvl, e, l1); if (t25 != null) return t25; }   // 0.1.25: the Spellblade
''', '''  if (ai >= @PKG@.AbilDefs.BREACH && ai <= @PKG@.AbilDefs.SHATTER) { String t25 = modText3(ai, mi, lvl, e, l1); if (t25 != null) return t25; }   // 0.1.25: the Spellblade (0.1.50: bounded)
  if (ai == @PKG@.AbilDefs.SMARK && mi == @PKG@.AbilModDefs.RADIUS) return "+" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.MOD_RADIUS * (double) e) + " blocks reach";   // 0.1.50 (fix round: + reach; fix 2: the text names only what the alt key reaches)
''')
# the target before anything is paid + the dispatch
P.rep('''    if (sbT == null) { refuse(pr, "No enemy in front of you within " + @PKG@.AbilMath.fmt(sr) + " blocks to Sunder - nothing was spent."); return "notarget"; }
  }
''', '''    if (sbT == null) { refuse(pr, "No enemy in front of you within " + @PKG@.AbilMath.fmt(sr) + " blocks to Sunder - nothing was spent."); return "notarget"; }
  }
  @REF@ smT = null;   // 0.1.50: Shadow Mark marks the enemy you look at - found before anything is paid (Mark from Above: on landing)
  if (ai == @PKG@.AbilDefs.SMARK && sh != 2) {
    double smr = @PKG@.AbilNum.SM_RANGE + cxr();   // fix round: the Radius modifier = + reach (Patient Mark is what an alt casts)
    smT = lookMob(st, ref, smr);
    if (smT == null) { refuse(pr, "No enemy in your look within " + @PKG@.AbilMath.fmt(smr) + " blocks to mark - nothing was spent."); return "notarget"; }
  }
''')
P.rep('''    else if (ai == @PKG@.AbilDefs.SHATTER) extra = shatterCast(pr, st, ref, u, k, aw, sh, h, now);
''', '''    else if (ai == @PKG@.AbilDefs.SHATTER) extra = shatterCast(pr, st, ref, u, k, aw, sh, h, now);
    else if (ai == @PKG@.AbilDefs.SMARK) extra = smarkCast(pr, st, ref, u, k, aw, sh, smT, now);   // 0.1.50
''')
P.rep('''    @PKG@.AbilStore.MOMX.remove(u);
''', '''    @PKG@.AbilStore.MOMX.remove(u);
    @PKG@.AbilStore.SMCUT.remove(u);   // 0.1.50 fix round 2: Shadow Mark's unused kill refund ends with the session
''')
P.rep('''  pruneD(@PKG@.AbilStore.MARKD, now, 0, 0);
''', '''  pruneD(@PKG@.AbilStore.MARKD, now, 0, 0);
  if (!@PKG@.AbilStore.SMARKS.isEmpty() || !@PKG@.AbilStore.SMCUT.isEmpty()) smarkPrune(now);   // 0.1.50 (fix 2: + SMCUT)
''')
SMARK_JAVA = r'''
# 0.1.50 SHADOW MARK (late bodies: they call UpFx, made after Abil) + the two capstone wrappers the direct starTick / graceRun call
F(abil, "public static volatile long SMARKED = 0L;")
F(abil, "public static volatile long SMKILLS = 0L;")
F(abil, "public static volatile boolean SMFAIL = false;")   # fix round: the kill hook's own catch logs once
ABIL_LATE += [
r"""
public static double exposeOn(@CAC@ acc, @REF@ t, double pct, double secs, long now) {
  if (t == null || !(pct > 0.0) || !(secs > 0.0)) return 0.0;
  double p = pct > @PKG@.AbilNum.SM_CAP ? @PKG@.AbilNum.SM_CAP : pct;
  if (!(p > 0.0)) return 0.0;
  double until = (double) (now + ms(secs));
  double stk = 1.0;
  Object o = @PKG@.AbilStore.MARKD.get(t);
  if (o instanceof double[] && ((double[]) o).length >= 3 && ((double[]) o)[0] > (double) now) {
    double[] m = (double[]) o;
    if (m[1] > p) return m[1];
    if (m[0] > until) until = m[0];   // fix round: a weaker / shorter write never cuts the running mark's time
    stk = m[2];
  }
  @PKG@.AbilStore.MARKD.put(t, new double[] { until, p, stk });
  MARKED = MARKED + 1L;
  return p;
}
""",
r"""
public static double smarkOn(@CAC@ acc, @REF@ t, java.util.UUID u, double pct, double secs, double bonus, long now) {
  if (t == null || u == null) return 0.0;
  double p = exposeOn(acc, t, pct, secs, now);
  if (!(p > 0.0)) return 0.0;
  if (@PKG@.AbilStore.SMARKS.size() > 2048) smarkPrune(now);
  double mine = pct > @PKG@.AbilNum.SM_CAP ? @PKG@.AbilNum.SM_CAP : pct;
  @PKG@.AbilStore.SMARKS.put(t, new Object[] { u, new double[] { (double) (now + ms(secs)), mine, secs, bonus } });
  @VEC@ q = pos(acc, t);
  if (q != null) particle(FX_GOD, q.x, q.y + 2.0, q.z, acc);
  return p;
}
""",
r"""
public static void smarkPrune(long now) {
  java.util.Iterator it = @PKG@.AbilStore.SMARKS.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    Object v = @PKG@.AbilStore.SMARKS.get(k);
    boolean dead = false;
    try { dead = (k instanceof @REF@) && !((@REF@) k).isValid(); } catch (Throwable t) { dead = false; }
    if (dead || !(v instanceof Object[]) || ((Object[]) v).length < 2 || !(((Object[]) v)[1] instanceof double[]) || ((double[]) ((Object[]) v)[1])[0] <= (double) now) it.remove();
  }
  java.util.Iterator ic = @PKG@.AbilStore.SMCUT.keySet().iterator();   // fix round 2: + the refund tokens whose cast's mark ran out
  while (ic.hasNext()) {
    Object v = @PKG@.AbilStore.SMCUT.get(ic.next());
    if (!(v instanceof Object[]) || ((Object[]) v).length < 1 || !(((Object[]) v)[0] instanceof Long) || ((Long) ((Object[]) v)[0]).longValue() <= now) ic.remove();
  }
}
""",
r"""
public static String smarkCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, @REF@ t, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double main = c == null ? 1.0 : c.main;
  double bonus = (double) @PKG@.AbilNum.CL_STRIKE * main;
  if (sh == 2) {
    aw.add(landJob(u, k, @PKG@.AbilDefs.SMARK, 0.0, now));
    if (pr != null) say(pr, "Mark from Above: every enemy near your landing will be marked.");
    LAST_ASN = "smark land";
    return " land";
  }
  if (t == null) return " notarget";
  double secs = cxds(@PKG@.AbilNum.SM_TIME) * (sh == 3 ? @PKG@.AbilNum.SM_CROUCHTIME / 100.0 : 1.0);
  double p = smarkOn(st, t, u, @PKG@.AbilNum.SM_MARK * main, secs, bonus, now);
  strikeArm(u, c, bonus, now);
  if (p > 0.0) @PKG@.AbilStore.SMCUT.put(u, new Object[] { Long.valueOf(now + ms(secs)), k });   // fix round: this cast's one kill refund (fix 2: until + the casting profile)
  if (sh == 1 && @PKG@.AbilNum.SM_SPRINTSPEED > 0.0) haste(st, ref, u, (int) Math.round(@PKG@.AbilNum.SM_SPRINTSPEED), @PKG@.AbilNum.SM_SPRINTTIME);
  if (sh == 3 && @PKG@.AbilNum.SM_CROUCHCLOAK > 0.0) cloakAt(pr, st, ref, u, k, aw, @PKG@.AbilNum.SM_CROUCHCLOAK, 3, now, @PKG@.AbilDefs.SMARK);
  SMARKED = SMARKED + 1L;
  used(u, k, @PKG@.AbilDefs.SMARK, c);
  String nm = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.SMARK, sh);
  if (pr != null) say(pr, nm + ": marked for " + @PKG@.AbilMath.fmt(secs) + " s - it takes +" + @PKG@.AbilMath.fmt(p) + " % damage from everyone; your next hit is a First Strike" + (sh == 3 ? " (you are cloaked)." : "."));
  LAST_ASN = "smark " + nm + " p=" + @PKG@.AbilMath.fmt(p);
  return " mark=" + @PKG@.AbilMath.fmt(p) + " secs=" + @PKG@.AbilMath.fmt(secs) + " strike=" + @PKG@.AbilMath.fmt(bonus);
}
""",
r"""
public static String smarkLand(@PKG@.AbilJob j, @CB@ cb, @REF@ cr, double[] at, long now) {
  if (j == null || at == null) return "nopos";
  @PKG@.AbilCtx c = j.cx;
  double main = c == null ? 1.0 : c.main;
  double bonus = (double) @PKG@.AbilNum.CL_STRIKE * main;
  double r = @PKG@.AbilNum.SM_AIRRADIUS + cxr();
  double secs = cxds(@PKG@.AbilNum.SM_TIME);
  double pct = @PKG@.AbilNum.SM_MARK * main * @PKG@.AbilNum.SM_AIRPOWER / 100.0;
  java.util.List l = near(cb, at[0], at[1], at[2], r);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  double shown = 0.0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    if (!losOk(cb, at[0], at[1] + 1.0, at[2], t)) continue;
    double p = smarkOn(cb, t, j.caster, pct, secs, bonus, now);
    if (p > 0.0) { n++; shown = p; }
  }
  if (n > 0) { strikeArm(j.caster, c, bonus, now); used(j.caster, j.pkey, @PKG@.AbilDefs.SMARK, c); SMARKED = SMARKED + (long) n; @PKG@.AbilStore.SMCUT.put(j.caster, new Object[] { Long.valueOf(now + ms(secs)), j.pkey }); }   // fix round: + one kill refund (fix 2: until + profile)
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, "Mark from Above: " + n + (n == 1 ? " enemy" : " enemies") + " marked" + (n > 0 ? " +" + @PKG@.AbilMath.fmt(shown) + " % for " + @PKG@.AbilMath.fmt(secs) + " s." : "."));
  LAST_ASN = "smark landing " + n;
  return String.valueOf(n);
}
""",
r"""
public static void smarkHit0(@CB@ buf, @REF@ t, @DMG@ d, long now) {
  if (t == null || d == null) return;
  Object o = @PKG@.AbilStore.SMARKS.get(t);
  if (!(o instanceof Object[]) || alive(buf, t)) return;
  @PKG@.AbilStore.SMARKS.remove(t);
  Object[] rec = (Object[]) o;
  if (rec.length < 2 || !(rec[0] instanceof java.util.UUID) || !(rec[1] instanceof double[])) return;
  java.util.UUID u = (java.util.UUID) rec[0];
  double[] nums = (double[]) rec[1];
  if (nums.length < 4 || nums[0] <= (double) now) return;
  String k = @PKG@.ClassCfg.pkey(u);
  Object cv = @PKG@.AbilStore.SMCUT.remove(u);   // fix round: once a cast (a passed-on mark gives none); fix 2: only while that cast's mark
  boolean cutOk = cv instanceof Object[] && ((Object[]) cv).length >= 2 && ((Object[]) cv)[0] instanceof Long   // runs, and only for the profile that cast it
    && ((Long) ((Object[]) cv)[0]).longValue() > now && k != null && k.equals(((Object[]) cv)[1]);
  long cut = cutOk ? ms(@PKG@.AbilNum.SM_KILLCD) : 0L;
  if (k != null && cut > 0L) @PKG@.UpFx.cdCut(k, "ShadowMark", cut, now);
  SMKILLS = SMKILLS + 1L;
  @PR@ pr = prOf(u);
  if (pr != null && cut > 0L) say(pr, "Shadow Mark: your marked enemy fell - Shadow Mark comes back " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.SM_KILLCD) + " s sooner.");
  @PKG@.UpFx.sentence(buf, t, u, nums, now);
  LAST_ASN = "smark kill" + (cut > 0L ? "" : " norefund");
}
""",
r"""
public static void smarkHit(@CB@ buf, @REF@ t, @DMG@ d, long now) {
  try { smarkHit0(buf, t, d, now); }
  catch (Throwable e) {   // fix round (critic): caught on its own, so the class tree's on-hit + kill effects (UpFx.landed) still run
    if (!SMFAIL) { SMFAIL = true; @PKG@.ClassCfg.warn("Shadow Mark kill hook failed (logged once; that kill gave no refund / jump): " + e); }
  }
}
""",
r"""
public static int capNova(@CB@ cb, @REF@ cr, java.util.UUID u, @PKG@.AbilCtx c, int hits, double x, double y, double z, double r, double amt) {
  return @PKG@.UpFx.supernova(cb, cr, u, c, hits, x, y, z, r, amt);
}
""",
r"""
public static boolean capCov(@PKG@.AbilCtx c) {
  return @PKG@.UpFx.covenant(c);
}
""",
]
'''
P.rep('''  return "+Your Ability 1 alt is now " + @PKG@.AbilDefs.NAMES[na] + " (Crouch + Ability 2)" + (cdOn ? " - it starts on its cooldown." : ".");
}
""",
]
for _src in ABIL_LATE:
    M(abil, _late_stub(_src))
''', '''  return "+Your Ability 1 alt is now " + @PKG@.AbilDefs.NAMES[na] + " (Crouch + Ability 2)" + (cdOn ? " - it starts on its cooldown." : ".");
}
""",
]''' + SMARK_JAVA + '''for _src in ABIL_LATE:
    M(abil, _late_stub(_src))
''')
# the kill: every damage event while a Shadow Mark runs (the Inspect group, after the damage - the same place UpFx.landed reads kills)
P.rep('''    @PKG@.Abil.siphonHit(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);
''', '''    @PKG@.Abil.siphonHit(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);
    if (!@PKG@.AbilStore.SMARKS.isEmpty()) @PKG@.Abil.smarkHit(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);   // 0.1.50: a Shadow-Marked kill
''')

# ================================================================================================ 3. THE PER-PATH CAPSTONES - the hooks in Abil
# Shatterpoint: Momentum back per enemy hit
P.rep('''  if (n > 0 && !echo) used(j.caster, j.pkey, @PKG@.AbilDefs.SHATTER, c);
''', '''  if (n > 0 && !echo) used(j.caster, j.pkey, @PKG@.AbilDefs.SHATTER, c);
  if (n > 0 && !echo) @PKG@.UpFx.shatterBack(c, j.caster, n, now);   // 0.1.50: Shatterpoint
''')
# Raincaller: the rain drifts toward the nearest enemy (once a pulse)
P.rep('''  if (now < z.nextHeal) return true;
  z.nextHeal = now + 500L;
  java.util.List l = near(cb, z.x, z.y, z.z, z.r);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  boolean lasting = nd(c, "Archer", "PA1");
''', '''  if (now < z.nextHeal) return true;
  z.nextHeal = now + 500L;
  if (ok && z.shape != 1 && z.n2 == 0) @PKG@.UpFx.rainDrift(z, cb, cr, now);   // 0.1.50: Raincaller
  java.util.List l = near(cb, z.x, z.y, z.z, z.r);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  boolean lasting = nd(c, "Archer", "PA1");
''')
# Storm of Fists: the wave count halved, every enemy in the aura
P.rep('''  z.d1 = hf && sh == 1 ? (double) @PKG@.AbilNum.HF_SP_EVERY : 0.0;
''', '''  if (hf) z.n1 = @PKG@.UpFx.fistEvery(c, z.n1);   // 0.1.50: Storm of Fists
  z.d1 = hf && sh == 1 ? (double) @PKG@.AbilNum.HF_SP_EVERY : 0.0;
''')
P.rep('''    Object ao = @PKG@.AbilStore.AWED.get(t);
    if (!(ao instanceof long[])) continue;
    long[] a = (long[]) ao;
    if (a[0] <= now || a[5] != ms || a[6] != ls) continue;
''', '''    if (!all) {   // 0.1.50: Storm of Fists strikes every enemy in the aura
      Object ao = @PKG@.AbilStore.AWED.get(t);
      if (!(ao instanceof long[])) continue;
      long[] a = (long[]) ao;
      if (a[0] <= now || a[5] != ms || a[6] != ls) continue;
    }
''')
P.rep('''  long ms = u.getMostSignificantBits();
  long ls = u.getLeastSignificantBits();
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    if (!all) {''', '''  long ms = u.getMostSignificantBits();
  long ls = u.getLeastSignificantBits();
  boolean all = @PKG@.UpFx.fistAll(u);
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    if (!all) {''')
# Supernova: the blast when Starfall ends
P.rep('''  if (echo || c == null) return false;
  if (j.brkAmt > 0.0) {
    int nb = burst(cb, cr, j.caster, cx, cy, cz, j.r, j.brkAmt, "Starfall");
''', '''  if (echo || c == null) return false;
  capNova(cb, cr, j.caster, c, j.hits, cx, cy, cz, j.r, amt);   // 0.1.50: Supernova
  if (j.brkAmt > 0.0) {
    int nb = burst(cb, cr, j.caster, cx, cy, cz, j.r, j.brkAmt, "Starfall");
''')
# Saint's Covenant: no drop, overheal -> a ward
P.rep('''  if (dp < 0.0) dp = 0.0;
  if (echo && cx != null && cx.base * cx.treeMain > 0.0) dp = dp * cx.main / (cx.base * cx.treeMain);
  int wardL = cx == null ? 0 : cx.lv(@PKG@.AbilModDefs.WARD);
''', '''  if (dp < 0.0) dp = 0.0;
  if (echo && cx != null && cx.base * cx.treeMain > 0.0) dp = dp * cx.main / (cx.base * cx.treeMain);
  boolean cov = capCov(cx);   // 0.1.50: Saint's Covenant
  if (cov) dp = 0.0;
  int wardL = cx == null ? 0 : cx.lv(@PKG@.AbilModDefs.WARD);
''')
P.rep('''    if (wardL > 0 && want > got + 0.01) {
      double wd = want - got;
      double wm = mx * 3.0 * (double) wardL / 100.0;
''', '''    if ((wardL > 0 || cov) && want > got + 0.01) {
      double wd = want - got;
      double wm = mx * 3.0 * (double) wardL / 100.0;
      double wc = cov ? mx * @PKG@.AbilNum.CP2_COVWARD / 100.0 : 0.0;   // 0.1.50: Saint's Covenant's ward
      if (wc > wm) wm = wc;
''')
# Shroud of Night: the smoke Exposes; the cloak holds longer inside it
P.rep('''  long lose = Math.round(@PKG@.AbilNum.VA_LOSE * 1000.0);
''', '''  long lose = Math.round(@PKG@.AbilNum.VA_LOSE * 1000.0);
  boolean shroud = @PKG@.UpFx.shroud(z);   // 0.1.50: Shroud of Night
''')
P.rep('''    if (now >= fv[1]) { effect(cb, t, z.pct >= 50.0 ? EF_SLOW : spdId(-(int) z.pct), 1.0); fv[1] = now + 500L; }
  }
  if (z.hits > 0 && !z.echoed) { z.echoed = true; used(z.caster, z.pkey, @PKG@.AbilDefs.VANISH, z.cx); }
  if (z.shape == 3) {
''', '''    if (now >= fv[1]) { effect(cb, t, z.pct >= 50.0 ? EF_SLOW : spdId(-(int) z.pct), 1.0); fv[1] = now + 500L; }
    if (shroud) exposeOn(cb, t, @PKG@.AbilNum.CP2_SHROUDX, 1.0, now);   // 0.1.50: Exposed while inside
  }
  if (z.hits > 0 && !z.echoed) { z.echoed = true; used(z.caster, z.pkey, @PKG@.AbilDefs.VANISH, z.cx); }
  if (z.shape == 3 || shroud) {   // 0.1.50: + Shroud of Night
''')
P.rep('''      long cap = ck.start + Math.round(@PKG@.AbilNum.VA_CR_CLOAK * 1000.0);
      long want = now + 600L;
''', '''      double capS = @PKG@.AbilNum.VA_CR_CLOAK;   // 0.1.50 Shroud of Night (fix round, critic): every shape - the cloak's own length (or Ambush's
      if (shroud) {                             // cap, the longer) + 3 s, and it lasts 3 s past your last moment inside the smoke
        double nat = @PKG@.AbilNum.VA_CLOAK;
        if (z.cx != null) { nat = nat * z.cx.durMult + z.cx.durAdd; if (nat < 0.5) nat = 0.5; }
        capS = (z.shape == 3 && capS > nat ? capS : nat) + @PKG@.AbilNum.CP2_SHROUDT;
      }
      long cap = ck.start + Math.round(capS * 1000.0);
      long want = now + 600L + (shroud ? Math.round(@PKG@.AbilNum.CP2_SHROUDT * 1000.0) : 0L);
''')
# fix round (critic): Hunter's Mark / Arrow Rain's mark (markMob) never weaken a running Shadow Mark - the stronger one stays, the later end
P.rep('''  double p = pct + 5.0 * (st - 1.0);
  @PKG@.AbilStore.MARKD.put(t, new double[] { (double) (now + ms(secs)), p, st });
  MARKED = MARKED + 1L;
''', '''  double p = pct + 5.0 * (st - 1.0);
  double mu = (double) (now + ms(secs));
  Object so = @PKG@.AbilStore.SMARKS.get(t);   // fix round 2: only a Shadow Mark still running (not an expired record the sweep has not dropped yet)
  boolean smLive = so instanceof Object[] && ((Object[]) so).length >= 2 && ((Object[]) so)[1] instanceof double[] && ((double[]) ((Object[]) so)[1]).length >= 1 && ((double[]) ((Object[]) so)[1])[0] > (double) now;
  if (o instanceof double[] && ((double[]) o).length >= 3 && ((double[]) o)[0] > (double) now && ((double[]) o)[1] > p && smLive) {
    if (((double[]) o)[0] > mu) mu = ((double[]) o)[0];   // 0.1.50 fix round: a stronger Shadow Mark is kept (its strength, the later end)
    p = ((double[]) o)[1];
  }
  @PKG@.AbilStore.MARKD.put(t, new double[] { mu, p, st });
  MARKED = MARKED + 1L;
''')

# ================================================================================================ 4. THE PER-PATH CAPSTONES - UpFx
UPFX_050 = r'''
# 0.1.50 THE PER-PATH CAPSTONES (Skill Trees 0.6.4): small hooks the Abil code paths call (tools/trees_v3_data.py R064_CAPS)
MU(r"""
public static boolean covenant(@PKG@.AbilCtx c) {
  return c != null && !c.echo && has(vec(c.tree), @C_xCovenant@);
}""")
MU(r"""
public static int fistEvery(@PKG@.AbilCtx c, int n) {
  if (c == null || n <= 0 || !has(vec(c.tree), @C_xFistStorm@)) return n;
  int m = (int) Math.round((double) n * @PKG@.AbilNum.CP2_FISTPCT / 100.0);
  CAPS = CAPS + 1L;
  return m < 2 ? 2 : m;
}""")
MU(r"""
public static boolean fistAll(java.util.UUID u) {
  return u != null && has(of(u), @C_xFistStorm@);
}""")
MU(r"""
public static boolean shroud(@PKG@.AbilZone z) {
  return z != null && z.cx != null && !z.cx.echo && has(vec(z.cx.tree), @C_xShroud@);
}""")
MU(r"""
public static void shatterBack(@PKG@.AbilCtx c, java.util.UUID u, int n, long now) {
  if (c == null || c.echo || u == null || n <= 0 || !has(vec(c.tree), @C_xShatterpt@)) return;
  int back = (int) Math.round(@PKG@.AbilNum.CP2_SHATTERMOM) * n;
  int mx = (int) Math.round(@PKG@.AbilNum.CP2_SHATTERMAX);
  if (back > mx) back = mx;
  if (back <= 0) return;
  @PKG@.Abil.momAdd(u, back, now);
  CAPS = CAPS + 1L;
  LAST = "shatterpoint " + back;
}""")
MU(r"""
public static void rainDrift(@PKG@.AbilZone z, @CB@ cb, @REF@ cr, long now) {
  if (z == null || z.cx == null || z.cx.echo || cr == null || !has(vec(z.cx.tree), @C_xRaincall@)) return;
  @REF@ t = @PKG@.Abil.nearest(cb, cr, z.x, z.y, z.z, z.r + 4.0, null);
  if (t == null) return;
  @VEC@ q = @PKG@.Abil.pos(cb, t);
  if (q == null) return;
  double dx = q.x - z.x;
  double dz = q.z - z.z;
  double d = Math.sqrt(dx * dx + dz * dz);
  if (d < 0.25) return;
  double s = @PKG@.AbilNum.CP2_RAINSTEP;
  if (s > d) s = d;
  z.x = z.x + dx / d * s;
  z.z = z.z + dz / d * s;
  CAPS = CAPS + 1L;
  LAST = "raincaller";
}""")
MU(r"""
public static int supernova(@CB@ cb, @REF@ cr, java.util.UUID u, @PKG@.AbilCtx c, int hits, double x, double y, double z, double r, double amt) {
  if (c == null || c.echo || u == null || hits <= 0 || !(amt > 0.0) || !has(vec(c.tree), @C_xSupernova@)) return 0;
  double pct = @PKG@.AbilNum.CP2_NOVAPER * (double) hits;
  if (pct > @PKG@.AbilNum.CP2_NOVAMAX) pct = @PKG@.AbilNum.CP2_NOVAMAX;
  if (!(pct > 0.0)) return 0;
  int n = @PKG@.Abil.burst(cb, cr, u, x, y, z, r, amt * pct / 100.0, "UpNova");
  CAPS = CAPS + 1L;
  @PR@ pr = @PKG@.Abil.prOf(u);
  if (pr != null) @PKG@.Abil.say(pr, "Supernova: the stars collapse - " + n + (n == 1 ? " enemy" : " enemies") + " hit for " + @PKG@.AbilMath.fmt(pct) + " % of a star.");
  LAST = "supernova " + n;
  return n;
}""")
MU(r"""
public static int legion(@ST@ st, @REF@ ref, java.util.UUID u, int sh, long now) {
  Object wo = @PKG@.AbilStore.OATHW.get(u);
  if (!(wo instanceof double[]) || ((double[]) wo).length < 2 || ((double[]) wo)[0] <= (double) now) return 0;
  double[] w = (double[]) wo;
  double cut = w[1] + @PKG@.AbilNum.CP2_LEGIONCUT;
  @PKG@.AbilStore.OATHW.put(u, new double[] { w[0], cut > 60.0 ? 60.0 : cut });
  double share = sh == 3 ? @PKG@.AbilNum.GO_BURDENSHARE : @PKG@.AbilNum.GO_SHARE;
  if (share > 90.0) share = 90.0;
  double[] me = @PKG@.Abil.here(st, ref);
  int n = 0;
  if (me != null) {
    java.util.ArrayList cu = new java.util.ArrayList();
    java.util.ArrayList cr = new java.util.ArrayList();
    @PKG@.Abil.gatherAt(st, st, me, @PKG@.AbilNum.GO_RANGE, cu, cr);
    for (int i = 0; i < cu.size(); i++) {
      java.util.UUID t = (java.util.UUID) cu.get(i);
      @REF@ r = (@REF@) cr.get(i);
      if (t.equals(u) || !@PKG@.HealTask.inParty(u, t) || !@PKG@.Abil.alive(st, r)) continue;
      Object oo = @PKG@.AbilStore.OATHS.get(t);
      if (oo instanceof double[] && ((double[]) oo)[0] > (double) now) continue;   // the main ally (or another Warrior's oath) - kept
      @PKG@.AbilStore.OATHS.put(t, new double[] { w[0], share, (double) u.getMostSignificantBits(), (double) u.getLeastSignificantBits(), 0.0 });
      n++;
    }
  }
  CAPS = CAPS + 1L;
  @PR@ pr = @PKG@.Abil.prOf(u);
  if (pr != null) @PKG@.Abil.say(pr, "Oath of Legions: " + n + " more party member" + (n == 1 ? "" : "s") + " bound; you take " + @PKG@.AbilMath.fmt(cut > 60.0 ? 60.0 : cut) + " % less while it holds.");
  LAST = "legion " + n;
  return n;
}""")
MU(r"""
public static void sentence(@CB@ buf, @REF@ t, java.util.UUID u, double[] nums, long now) {
  if (u == null || nums == null || nums.length < 4) return;
  double[] v = of(u);
  if (!has(v, @C_xSentence@)) return;
  if (!gap(SENT, u, Math.round(@PKG@.AbilNum.CP2_SENTGAP * 1000.0), now)) return;
  @PR@ pr = @PKG@.Abil.prOf(u);
  @REF@ cr = pr == null ? null : pr.getReference();
  @VEC@ q = @PKG@.Abil.pos(buf, t);
  @REF@ nx = null;
  if (q != null && cr != null && cr.isValid()) nx = @PKG@.Abil.nearest(buf, cr, q.x, q.y, q.z, @PKG@.AbilNum.CP2_SENTRANGE, t);
  if (nx != null) @PKG@.Abil.smarkOn(buf, nx, u, nums[1], nums[2], nums[3], now);
  @PKG@.Abil.strikeArm(u, null, nums[3], now);
  CAPS = CAPS + 1L;
  if (pr != null) @PKG@.Abil.say(pr, "Death Sentence: " + (nx != null ? "the mark jumps to the next enemy" : "no enemy near to take the mark") + " - your First Strike is ready.");
  LAST = "sentence " + (nx != null ? "jump" : "none");
}""")
'''
P.rep('''MU(r"""
public static void cast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, int ai, int sh, @PKG@.AbilCtx cx, double[] at, double mana, double stam, long now) {''',
      UPFX_050.strip("\n") + '''
MU(r"""
public static void cast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, int ai, int sh, @PKG@.AbilCtx cx, double[] at, double mana, double stam, long now) {''')
P.rep('''  if (ai == @PKG@.AbilDefs.IRONC && has(v, @C_xWarden@)) warden(st, ref, u, now);
''', '''  if (ai == @PKG@.AbilDefs.IRONC && has(v, @C_xWarden@)) warden(st, ref, u, now);
  if (ai == @PKG@.AbilDefs.OATH && has(v, @C_xLegion@)) legion(st, ref, u, sh, now);   // 0.1.50: Oath of Legions
''')
P.rep('''      if (has(v, @C_xGlacial@) && @PKG@.AbilStore.FROZEN.get(t) instanceof long[]) b = b + @PKG@.AbilNum.CP_GLACIALP;
''', '''      if (has(v, @C_xGlacial@) && @PKG@.AbilStore.FROZEN.get(t) instanceof long[]) b = b + @PKG@.AbilNum.CP_GLACIALP;
      if (ai == @PKG@.AbilDefs.SHATTER && has(v, @C_xShatterpt@) && @PKG@.Abil.breachPct(t, now) > 0.0) b = b + @PKG@.AbilNum.CP2_SHATTERB;   // 0.1.50: Shatterpoint
      if (ai == @PKG@.AbilDefs.RAIN && has(v, @C_xRaincall@) && timed(RT, t, now) > 0.0) b = b + @PKG@.AbilNum.CP2_RAINROOT;   // 0.1.50: Raincaller
''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0, "0.1.50: no class / command / system"
P.finish()
print("wrote", P.dst)
