"""Derive SkyyArmory/build_skyyarmory_0.1.21.py (+ its harness SkyyArmory/test_skyyarmory_0.1.21.py) from the GENERATED 0.1.20
(SkyyArmory/build_skyyarmory_0.1.20.py = the tools/deploy_set.py SET pin, made by tools/armory_0_1_20_patch.py; test_skyyarmory_0.1.20.py =
its harness). Every anchor is asserted (rep = exactly one hit). Edit THIS file, never the generated scripts.
Run:  python tools/armory_0_1_21_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.21.py   then
      python SkyyArmory/test_skyyarmory_0.1.21.py --dir tools/dev/scratch/<task>/harness      (never --deploy)

0.1.21 = THE SOUL ORB ROUND (every Soul Orb change in one build). Skyy's words (docs/answered/classes.md LOCKED 2026-10-11):
  "id scale up the damage on T1 cause it des verry little damage and swap from crystals to essence for the crafting, and follow the vanillas
   essence progression, starting with life essence"  (+ popups "Vanilla ladder (Recommended)", "x2.5 (Recommended)")
  "and the traversal doesnt work yet"
  "make the lines more whispy when not tethered, and more obviouis when it is."
  "and make it teather a little faster,"
  "yeah, a thorium one was only doing 2 damage a tick. it needs a lot more damage"
  1 ESSENCES (the VANILLA ladder): the Soul Orb = 25 Life Essence + 4 Sticks + 1 Plant Fibre (the Blue Crystal is gone: 5 more Life Essence
    instead); the cages: Copper Life (15), Iron Fire (15), Thorium Ice (15), Cobalt Water (12), Adamantite Lightning (12), Mithril Void (10),
    Onyxium Concentrated Life (1 = 100 Life Essence at the Farming bench; FIX (review): was 5 = 500, ~33x the other steps). Recipe SHAPE unchanged (the tier before x1 + the metal's bars +
    the essence) - SkyyGear 0.2.22's /upgrade reader (GearUp.fromRecipe) still finds every step. The zone drops follow the ladder:
    Life Zone 1 (8 %), Fire the volcanic caves (10 %), Water Zone 2 (8 %), Ice Zone 3 (8 %), Lightning Zone 4 (8 %), Void Zone 4 (5 %);
    Concentrated Life is craft-only (vanilla: 100 Life Essence at the Farming bench). The essence table entries are named after the vanilla
    items (essence.chance.Ice / .Water / .Lightning; Earth / Frost / Storm / Light are gone - the live file has none of them).
    SkyyArmory_Essence_Earth / _Light: never dropped again and in no recipe; the two items stay defined (ids kept) so existing stacks stay
    valid (their description says so). The soul / gem / Binding colour of the moved tiers follows the essence (Priest.md: "The soul, gems and
    Bindings take the essence colour"): Thorium ice cyan, Cobalt water blue, Onyxium concentrated-life lime (art generated at build time).
  2 DAMAGE: a Binding deals soul.damagePerSecond.<tier> a second, before SkyyGear levels (NEW table; soul.damagePerMana + soul.damageMult are
    gone - nothing in the live file): Soul Orb 5, Copper 7, Iron 10, Thorium 15, Cobalt 20, Adamantite 30, Mithril 40, Onyxium 55 (Thorium
    3.45 -> 15 = x4.3; the Orb 2 -> 5 = x2.5, Skyy's popup). Mana per Binding per second unchanged (1.00 .. 1.35).
  3 TETHER ~30 % FASTER: soul.stabilize 2.5 / 2.3 / 2.1 / 1.9 / 1.7 / 1.6 / 1.5 / 1.5 -> 1.75 / 1.6 / 1.45 / 1.35 / 1.2 / 1.1 / 1.05 / 1.0 s.
  4 LINES: a WISPY Binding = sparse (1.8 blocks apart), faint, flickering dots (every third dot skipped, the gap moves each draw) of a NEW
    faint system SkyyArmory_SoulWisp_<tier>; a SOLID Binding = dense (0.45 apart), brighter, thicker dots (the existing SkyyArmory_Soul_<tier>
    systems made tighter + 1.6x bigger). The per-player budget soul.lineDots 48 -> 64 (max 96 -> 128): every line asks for its dots, an
    over-budget draw is shared out in proportion (every line keeps at least one dot), never above the budget.
  5 WINGS OF FATE (research/classes/Priest.md 'Charged = WINGS OF FATE', research/cloud/Soul-Orb-Spec.md 4.2): HOLD LEFT CLICK with a Soul
    Orb / Cage (a Charging Primary: the wand's charge pose, 0.35 s key; a tap does nothing - right click stays the Bindings) and let go ->
    an invisible marker (code 14000) the Java turns into the move: Priest only (class:fn:allowed), costs wings.mana 20 + wings.stamina 10
    (2 Mana : 1 Stamina), given back when the move did not move you a block. An ALLY (a party member when you are in a party; any player when
    you are not - wings.anyPlayer) nearest your crosshair within wings.lockRange 30 inside wings.lockCone 30 degrees, line of sight = LOCKED:
    up to wings.allyBounds 8 bounds at wings.allySpeed 24 b/s re-aimed at them each bound (a bound = ONE plain velocity Set, the Monk
    vault's; ballistic so it lands on the aim point after one bound), until you are within wings.arrive 3 blocks = ARRIVED: the ally heals base (wings.baseHeal
    10 % + wings.tierHeal 1 % per tier of THEIR max Health) + ALL your stored soul healing (armory:fn:soul pool, Soul.takeAll - it empties),
    at most wings.healCap 60 % of their max Health; Divinity XP through skill:fn:healxp ("armory:wings"). No ally = wings.bounds 3 glide
    bounds where you look at wings.speed 18 b/s + wings.lift 4 up (ONE Set each, the wand launch's dash config). Every bound keeps a DAMAGING FALL (TravMath.hopVy + ArmoryTrav.maxFall,
    the wand / bow rule); no void protection (Skyy). Looks: two glowing blue wings (SkyyArmory_Wings_Blue dots) + a blue trail every 150 ms.
    Ends: arrived, glide over, the ally gone / too far / not reached 1 s after the last bound, death, world change. New classes WingsState +
    Wings (TravTick), new rows wings.* (Server Setup > Armory > Soul Orb + essences).
  6 LOW (0.1.20 review): the hop.maxUp row help no longer says "Full in the air" next to the kept damaging fall.
No saved data. FIX (review) migrate021 (PROJECT-RULES 4): a config.properties first written by 0.1.19 / 0.1.20 spells out every Soul row, so a
soul.stabilize.<tier> / soul.lineDots line still on its 0.1.20 default becomes the 0.1.21 one ONCE (History copy, change-log + Undo, marker,
bytes + line endings kept; hand-set values kept + logged); the 0.1.20 lines 0.1.21 no longer reads (soul.damagePerMana, soul.damageMult.*, the
Earth / Frost / Storm / Light essence lines) stay in the file without a WARN (a hand-set one is named once). Skyy's live file has no soul.*
line: the marker only. FIX (review) too: Wings of Fate keeps the cast's profile (a profile switch ends the flight; healxp gets the profile
key), 5 failed bounds in a row end a flight (refund if it did not move you); over the line budget the wispy lines are held first so a solid
line keeps >= 2x a wispy line's dots at every tier. New ids: 4 interactions +
1 root (Wings), 1 marker projectile, 8 wisp + 1 wings particle systems; no item id added or removed.
ROLLBACK: 0.1.20 (the old recipes / damage / colours; Wings of Fate gone); no data involved. Items crafted with the new recipes stay valid.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.20.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.21.py")
TSRC = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.20.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.21.py")

CR, LF = chr(13), chr(10)
raw = open(SRC, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.20"\nMOD = "SkyyArmory"' in s and "0.1.20 = THE WAND KEEPS A DAMAGING FALL" in s, "build_skyyarmory_0.1.20.py is not the 0.1.20 pin"
assert "0.1.21" not in s and "Wings.tickPlayer" not in s and "soul.damagePerSecond" not in s, "0.1.20 already has the 0.1.21 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:140])
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyArmory 0.1.20 - build script (javassist via jpype). GENERATED by tools/armory_0_1_20_patch.py from the GENERATED 0.1.19 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.20.py -> SkyyArmory/SkyyArmory-0.1.20.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.20.py --dir tools/dev/scratch/<task>/harness.
''', '''"""SkyyArmory 0.1.21 - build script (javassist via jpype). GENERATED by tools/armory_0_1_21_patch.py from the GENERATED 0.1.20 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.21.py -> SkyyArmory/SkyyArmory-0.1.21.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.21.py --dir tools/dev/scratch/<task>/harness.

0.1.21 = THE SOUL ORB ROUND (Skyy 2026-10-11, docs/answered/classes.md; full notes in tools/armory_0_1_21_patch.py): the VANILLA essence
ladder (Soul Orb 25 Life Essence, no Blue Crystal; cages Life / Fire / Ice / Water / Lightning / Void / Concentrated Life; zone drops Life Z1,
Fire volcanic, Water Z2, Ice Z3, Lightning + Void Z4; our Earth / Light essences no longer dropped or used, ids kept); Binding damage a
second by tier 5 / 7 / 10 / 15 / 20 / 30 / 40 / 55 (NEW table soul.damagePerSecond); tether ~30 % faster (1.75 .. 1.0 s); wispy lines =
sparse faint flickering dots, solid = dense bright thick (soul.lineDots 64); WINGS OF FATE = hold LEFT click + let go: glide bounds where
you look, or locked onto an ally (party / any player) and carried to them - arriving heals them (base + all stored soul healing); one
velocity write per bound, a damaging fall kept, Priest only, 20 Mana + 10 Stamina (rows wings.*).

0.1.20 (the base, everything below is still true unless 0.1.21 above says otherwise):
''')
rep('VERSION = "0.1.20"\nMOD = "SkyyArmory"', 'VERSION = "0.1.21"\nMOD = "SkyyArmory"')

# ---------------------------------------------------------------------------------------------------------------- 6 LOW: hop.maxUp help
H21_OLD_HELP = "Caps the launch's up part (look down = up). Full in the air; a damaging fall is kept. 0 = no cap."
H21_HELP = "Caps the launch's up part (look down = up), in the air too; a damaging fall is kept. 0 = no cap."
assert len(H21_HELP) <= 100
rep('"' + H21_OLD_HELP + '", ', '"' + H21_HELP + '", ')

# ---------------------------------------------------------------------------------------------------------------- 1-4 the numbers + rows
rep('''SOUL_MULT = [1.0, 1.1, 1.1, 1.5, 1.5, 2.0, 2.0, 2.5]     # damage per Mana x (LOCKED / proposed)''',
    '''SOUL_DPS = [5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 40.0, 55.0]  # 0.1.21 damage a second per Binding before levels (Skyy 2026-10-11: "it needs a lot more damage"; Orb x2.5)''')
rep('''SOUL_STAB = [2.5, 2.3, 2.1, 1.9, 1.7, 1.6, 1.5, 1.5]     # stabilize seconds (Skyy: 1.5-2.5 s, higher tiers faster; spec 2)''',
    '''SOUL_STAB = [1.75, 1.6, 1.45, 1.35, 1.2, 1.1, 1.05, 1.0]  # stabilize seconds - 0.1.21 ~30 % faster (Skyy 2026-10-11: "make it teather a little faster"; 0.1.20: 2.5 .. 1.5)''')
rep('''ESS_NAMES = ["Life", "Fire", "Earth", "Frost", "Storm", "Void", "Light"]          # Skyy 2026-10-10 Element ladder (+ Life / Fire, 2026-10-04)
ESS_PCT = [8.0, 10.0, 8.0, 8.0, 8.0, 5.0, 3.0]           # % per kill of a monster of that essence's zone
ESS_ZONE = [1, 0, 2, 3, 4, 4, 4]                         # 0 = the vanilla volcanic caves (deep-cave mobs, any zone); Void + Light: no zone 5+ yet''',
    '''ESS_NAMES = ["Life", "Fire", "Ice", "Water", "Lightning", "Void"]          # 0.1.21 the VANILLA essence ladder (Skyy 2026-10-11; Concentrated Life = craft-only)
ESS_PCT = [8.0, 10.0, 8.0, 8.0, 8.0, 5.0]           # % per kill of a monster of that essence's zone
ESS_ZONE = [1, 0, 3, 2, 4, 4]                         # 0 = the vanilla volcanic caves (deep-cave mobs, any zone); Ice = the frost zone, Water = Zone 2 (its first drop source)''')
rep('''    ('soul.damagePerMana', 'Binding damage per Mana', _SO, 'dec', '2', '0', '50', '', '', 'live', 'Damage per Mana a Binding drains, x the tier multiple (before levels). Tooltips show defaults.', 'SOUL_DPM', 'double', '2', 'Soul Bindings: damage per Mana drained (x the tier multiple below; before SkyyGear levels). 2 = 0.08 x the Wood wand charged shot (25 damage) per Mana (Soul-Orb-Spec 2.1).'),
''', '')
rep('''    ('soul.lineDots', 'Binding line dots (per player)', _SO, 'int', '48', '0', '96', '', '', 'live', 'At most this many dots for all Binding lines of one Priest at once. 0 = no lines.', 'SOUL_DOTS', 'int', '48', 'Soul Bindings: at most this many particle dots for all Binding lines of one player per draw (4 draws a second; 0 = no lines).'),''',
    '''    ('soul.lineDots', 'Binding line dots (per player)', _SO, 'int', '64', '0', '128', '', '', 'live', 'At most this many dots for all Binding lines of one Priest at once. 0 = no lines.', 'SOUL_DOTS', 'int', '64', 'Soul Bindings: at most this many particle dots for all Binding lines of one player per draw (4 draws a second; 0 = no lines). 0.1.21: 64 (0.1.20: 48) - solid lines are denser (0.45 blocks), wispy ones sparse (1.8) and flickering.'),''')
rep('''assert len(set(r[0] for r in CFG_SOUL)) == len(CFG_SOUL) == 13 and all(len(r) == 15 and r[2] == _SO for r in CFG_SOUL)''',
    '''assert len(set(r[0] for r in CFG_SOUL)) == len(CFG_SOUL) == 12 and all(len(r) == 15 and r[2] == _SO for r in CFG_SOUL)          # 0.1.21: soul.damagePerMana gone''')
CFG_WINGS_PY = r'''# ================================================================= 0.1.21 WINGS OF FATE (Skyy 2026-10-11 "and the traversal doesnt work yet"; Priest.md, Soul-Orb-Spec 4.2)
CFG_WINGS = [
    ('wings.enabled', 'Wings of Fate (hold left click)', _SO, 'bool', 'true', '', '', '', '', 'live,part,danger', 'Off = holding left click with a Soul Orb / Cage does nothing.', 'WINGS_ON', 'boolean', 'true', 'Wings of Fate (the Soul Orb / Cage charged move: hold left click, let go). Off = nothing happens.'),
    ('wings.mana', 'Wings of Fate Mana cost', _SO, 'dec', '20', '0', '200', '', '', 'live', 'Mana a cast costs (2 Mana : 1 Stamina, the magic traversal rule).', 'WINGS_MA', 'double', '20', 'Wings of Fate: Mana a cast costs (the magic traversal ratio 2 Mana : 1 Stamina; a cast that does not move you a block is given back).'),
    ('wings.stamina', 'Wings of Fate Stamina cost', _SO, 'dec', '10', '0', '100', '', '', 'live', 'Stamina a cast costs. Too little Mana or Stamina = no cast.', 'WINGS_ST', 'double', '10', 'Wings of Fate: Stamina a cast costs (too little Mana or Stamina = nothing happens, nothing is taken).'),
    ('wings.speed', 'Wings glide speed (b/s)', _SO, 'dec', '18', '4', '40', '', '', 'live', 'How fast each glide bound throws you where you look (no ally).', 'WINGS_SPEED', 'double', '18', 'Wings of Fate: the speed of each glide bound where you look when no ally is locked (blocks per second).'),
    ('wings.boundSeconds', 'Wings time per bound (s)', _SO, 'dec', '0.35', '0.15', '1', '', 's', 'live', 'A new bound every this many seconds (one push each).', 'WINGS_BOUND', 'double', '0.35', 'Wings of Fate: seconds between two bounds (each bound is ONE push; nothing in between).'),
    ('wings.bounds', 'Wings bounds without an ally', _SO, 'int', '3', '1', '8', '', '', 'live', 'Glide bounds when no ally is that way.', 'WINGS_BOUNDS', 'int', '3', 'Wings of Fate: how many glide bounds when no ally is locked.'),
    ('wings.allyBounds', 'Wings bounds to an ally (most)', _SO, 'int', '8', '1', '16', '', '', 'live', 'Most bounds to reach a locked ally (farther than a plain glide).', 'WINGS_ABOUNDS', 'int', '8', 'Wings of Fate: the most bounds that carry you to a locked ally (each re-aimed at them).'),
    ('wings.allySpeed', 'Wings speed to an ally (b/s)', _SO, 'dec', '24', '4', '48', '', '', 'live', 'How fast the bounds carry you to a locked ally.', 'WINGS_ASPEED', 'double', '24', 'Wings of Fate: the speed of the bounds to a locked ally (blocks per second).'),
    ('wings.lift', 'Wings lift per bound (b/s)', _SO, 'dec', '4', '0', '15', '', '', 'live', 'Extra upward push on each plain glide bound (keeps you gliding).', 'WINGS_LIFT', 'double', '4', 'Wings of Fate: extra upward speed on each glide bound without an ally (the up part is at most 15).'),
    ('wings.lockRange', 'Wings ally lock reach (blocks)', _SO, 'int', '30', '5', '64', '', 'blocks', 'live', 'An ally this close in the look direction is locked on.', 'WINGS_RANGE', 'int', '30', 'Wings of Fate: an ally at most this far (line of sight) in the look direction is locked on.'),
    ('wings.lockCone', 'Wings ally lock cone (degrees, full)', _SO, 'int', '30', '4', '90', '', '', 'live', 'The ally nearest your crosshair inside this cone is locked on.', 'WINGS_CONE', 'int', '30', 'Wings of Fate: the ally nearest your crosshair inside a cone this wide is locked on.'),
    ('wings.arrive', 'Wings arrival distance (blocks)', _SO, 'dec', '3', '1', '8', '', 'blocks', 'live', 'Reaching this close to the ally = arrived (the heal).', 'WINGS_ARRIVE', 'double', '3', 'Wings of Fate: within this many blocks of the locked ally you have arrived (the heal).'),
    ('wings.baseHeal', 'Wings base heal (% of max Health)', _SO, 'dec', '10', '0', '60', '', '%', 'live', 'The arrival heal before stored healing: this % + the tier step below.', 'WINGS_BASE', 'double', '10', 'Wings of Fate: the arrival heal = this % of the ally max Health + the tier step, even with nothing stored (Skyy 2026-10-04).'),
    ('wings.tierHeal', 'Wings heal per tier (%)', _SO, 'dec', '1', '0', '10', '', '%', 'live', '+ this % of max Health per tier above the Soul Orb (Onyxium = +7).', 'WINGS_PER', 'double', '1', 'Wings of Fate: + this % of the ally max Health per tier above the Soul Orb (Orb 10, Onyxium 17 by default).'),
    ('wings.healCap', 'Wings heal cap (% of max Health)', _SO, 'int', '60', '0', '100', 'step=5', '%', 'live', 'The arrival heal (base + stored) is at most this. The stored pool empties.', 'WINGS_CAP', 'int', '60', 'Wings of Fate: the arrival heal (base + ALL stored soul healing) is at most this % of the ally max Health; the stored pool empties.'),
    ('wings.anyPlayer', 'Wings: any player when not in a party', _SO, 'bool', 'true', '', '', '', '', 'live', 'On = with no party any player counts as an ally; in a party only members.', 'WINGS_ANY', 'boolean', 'true', 'Wings of Fate: on = when you are in no party any player counts as an ally; in a party only its members do.'),
]
assert len(set(r[0] for r in CFG_WINGS)) == len(CFG_WINGS) == 16 and all(len(r) == 15 and r[2] == _SO for r in CFG_WINGS)
assert all(len(r[1]) <= 40 and len(r[10]) <= 100 for r in CFG_WINGS), [(r[0], len(r[1]), len(r[10])) for r in CFG_WINGS if len(r[1]) > 40 or len(r[10]) > 100]
assert "%" not in "".join(r[13] for r in CFG_WINGS)
CFG_SOUL = CFG_SOUL + CFG_WINGS          # one category (Soul Orb + essences): the rows, the fields, the default file
'''
rep('''assert "%" not in "".join(r[13] for r in CFG_SOUL)
''', '''assert "%" not in "".join(r[13] for r in CFG_SOUL)
''' + CFG_WINGS_PY)

# ---------------------------------------------------------------------------------------------------------------- 1 the essences + recipes + colours
rep('''ESS_IDS = ["Ingredient_Life_Essence", "Ingredient_Fire_Essence", "SkyyArmory_Essence_Earth", "Ingredient_Ice_Essence",
           "Ingredient_Lightning_Essence", "Ingredient_Void_Essence", "SkyyArmory_Essence_Light"]''',
    '''ESS_IDS = ["Ingredient_Life_Essence", "Ingredient_Fire_Essence", "Ingredient_Ice_Essence", "Ingredient_Water_Essence",
           "Ingredient_Lightning_Essence", "Ingredient_Void_Essence"]          # 0.1.21: the vanilla ladder (the drop table, index = ESS_NAMES)
ESS_CONC = "Ingredient_Life_Essence_Concentrated"          # 0.1.21: Onyxium's essence - craft-only (vanilla: 100 Life Essence, Farming bench)''')
rep('''"Dropped by Zone 2 monsters. Used to craft the Thorium Soul Cage."),''',
    '''"No longer dropped or used in any recipe (Soul Cages use the vanilla essences now). Kept so old stacks stay valid."),''')
rep('''"Dropped rarely by the deepest zone's monsters. Used to craft the Onyxium Soul Cage.")}''',
    '''"No longer dropped or used in any recipe (Soul Cages use the vanilla essences now). Kept so old stacks stay valid.")}''')
rep('''SOUL_ESS = [None, "Life", "Fire", "Earth", "Frost", "Storm", "Void", "Light"]          # the essence each cage is crafted with (the Orb: Life, below)
SOUL_ESS_QTY = [20, 15, 15, 15, 12, 12, 10, 10]         # Soul-Orb-Spec 1 (Onyxium: 10 Light, the Element ladder)''',
    '''# 0.1.21 (Skyy 2026-10-11 "follow the vanillas essence progression, starting with life essence"): the essence each tier is crafted with
SOUL_ESS_IDS = ["Ingredient_Life_Essence", "Ingredient_Life_Essence", "Ingredient_Fire_Essence", "Ingredient_Ice_Essence", "Ingredient_Water_Essence",
                "Ingredient_Lightning_Essence", "Ingredient_Void_Essence", ESS_CONC]
SOUL_ESS_QTY = [25, 15, 15, 15, 12, 12, 10, 1]         # the Orb: 20 + 5 for the Blue Crystal it no longer takes; Onyxium 1 Concentrated = 100 Life (FIX (review): 5 = 500 was ~33x the other steps)''')
rep('''SOUL_COLORS = ["#3f8cff", "#5bd65b", "#ff4a3a", "#ffa830", "#4fe3ff", "#ffe14a", "#a050ff", "#fff0b0"]''',
    '''SOUL_COLORS = ["#3f8cff", "#5bd65b", "#ff4a3a", "#4fe3ff", "#2f6bff", "#ffe14a", "#a050ff", "#8cff3a"]          # 0.1.21: Thorium ice, Cobalt water, Onyxium concentrated life''')
rep('''              ("Resources/Ingredients/Essence_Textures/Fire_Essence_Texture.png", (0.0, 1.0), ((0xff, 0xa8, 0x30), 0.85)),
              ("Resources/Ingredients/Essence_Textures/Ice_Essence_Texture.png", (0.0, 1.0), None),
              ("Resources/Ingredients/Essence_Textures/Lightning_Essence_Texture.png", (0.0, 1.0), None),
              ("Resources/Ingredients/Essence_Textures/Void_Essence_Texture.png", (0.10, 1.0), None),
              ("Resources/Crystals/Crystal_Fragment_Textures/White.png", (0.0, 1.0), ((0xff, 0xe9, 0xa0), 0.6))]''',
    '''              ("Resources/Ingredients/Essence_Textures/Ice_Essence_Texture.png", (0.0, 1.0), None),          # 0.1.21 Thorium = Ice
              ("Resources/Ingredients/Essence_Textures/Water_Essence_Texture.png", (0.0, 1.0), None),        # 0.1.21 Cobalt = Water
              ("Resources/Ingredients/Essence_Textures/Lightning_Essence_Texture.png", (0.0, 1.0), None),
              ("Resources/Ingredients/Essence_Textures/Void_Essence_Texture.png", (0.10, 1.0), None),
              ("Resources/Ingredients/Essence_Textures/Life_Essence_Texture.png", (0.0, 1.0), ((0x8c, 0xff, 0x3a), 0.55))]          # 0.1.21 Onyxium = Concentrated Life''')
rep('''assert len(SOUL_IDS) == len(SOUL_NAMES) == len(SOUL_N) == len(SOUL_MULT) == len(SOUL_MPS) == len(SOUL_STAB) == len(SOUL_CAP) == len(SOUL_COLORS) == len(SOUL_PAINT) == 8
assert len(ESS_IDS) == len(ESS_NAMES) == len(ESS_PCT) == len(ESS_ZONE) == 7''',
    '''assert len(SOUL_IDS) == len(SOUL_NAMES) == len(SOUL_N) == len(SOUL_DPS) == len(SOUL_MPS) == len(SOUL_STAB) == len(SOUL_CAP) == len(SOUL_COLORS) == len(SOUL_PAINT) == len(SOUL_ESS_IDS) == 8
assert len(ESS_IDS) == len(ESS_NAMES) == len(ESS_PCT) == len(ESS_ZONE) == 6''')
rep('''for _i in ("Ingredient_Crystal_Blue", "Ingredient_Stick", "Ingredient_Fibre"):
    assert az_has("item", _i), "a Soul Orb recipe input left Assets.zip: %s" % _i''',
    '''for _i in ("Ingredient_Stick", "Ingredient_Fibre", ESS_CONC, "Ingredient_Water_Essence"):          # 0.1.21: no Blue Crystal any more
    assert az_has("item", _i), "a Soul Orb recipe input left Assets.zip: %s" % _i
assert all(az_has("item", _i) for _i in SOUL_ESS_IDS) and not [_i for _i in SOUL_ESS_IDS if _i.startswith("SkyyArmory_")], "0.1.21: only vanilla essences"
_conc = az_get("item", ESS_CONC)
assert [(x_["ItemId"], x_["Quantity"]) for x_ in _conc["Recipe"]["Input"]] == [("Ingredient_Life_Essence", 100)], "the vanilla Concentrated Life recipe changed"''')
# the review copy: a moved tier may now equal the reviewed sheet (Thorium = Ice again) - equal = "= reviewed copy", else "recoloured"
rep('''            else:
                assert open(_rt, "rb").read() != _tex, "%s: the Element ladder recolour did not change the texture" % _tier
                SOUL_REVIEW[_tier] = "model + spin = reviewed copy; soul + gems in the 2026-10-10 Element colour"''',
    '''            elif open(_rt, "rb").read() == _tex and open(_ri, "rb").read() == _icon:          # 0.1.21: the vanilla ladder (Thorium = Ice = the reviewed sheet)
                SOUL_REVIEW[_tier] = "= reviewed copy"
            else:
                SOUL_REVIEW[_tier] = "model + spin = reviewed copy; soul + gems in the 0.1.21 vanilla-essence colour"''')
rep('''                     "Input": [{"ItemId": "Ingredient_Life_Essence", "Quantity": SOUL_ESS_QTY[0]}, {"ItemId": "Ingredient_Crystal_Blue", "Quantity": 1},
                               {"ItemId": "Ingredient_Stick", "Quantity": 4}, {"ItemId": "Ingredient_Fibre", "Quantity": 1}],''',
    '''                     "Input": [{"ItemId": SOUL_ESS_IDS[0], "Quantity": SOUL_ESS_QTY[0]},          # 0.1.21: no Blue Crystal (Skyy: "swap from crystals to essence")
                               {"ItemId": "Ingredient_Stick", "Quantity": 4}, {"ItemId": "Ingredient_Fibre", "Quantity": 1}],''')
rep('''                                   {"ItemId": ESS_IDS[ESS_NAMES.index(SOUL_ESS[_t])], "Quantity": SOUL_ESS_QTY[_t]}],''',
    '''                                   {"ItemId": SOUL_ESS_IDS[_t], "Quantity": SOUL_ESS_QTY[_t]}],          # 0.1.21: the vanilla ladder''')
rep('''for _r in SOUL_RECIPES:
    for _x in _r["Input"]:
        assert az_has("item", _x["ItemId"]) or _x["ItemId"] in SOUL_IDS or _x["ItemId"].startswith("SkyyArmory_Essence_"), _x''',
    '''for _r in SOUL_RECIPES:
    for _x in _r["Input"]:
        assert az_has("item", _x["ItemId"]) or _x["ItemId"] in SOUL_IDS, _x          # 0.1.21: never our Earth / Light essence
    assert not [x_ for x_ in _r["Input"] if "Crystal" in x_["ItemId"] or x_["ItemId"].startswith("SkyyArmory_Essence_")], _r
# SkyyGear 0.2.22's /upgrade reader (GearUp.fromRecipe): a cage recipe = ONE output of the next tier x1 whose inputs hold the tier before x1;
# the other inputs (bars + essence) are the cost - the shape is unchanged, only the essence id moved
for _t in range(1, 8):
    _ins = SOUL_RECIPES[_t]["Input"]
    assert [x_["ItemId"] for x_ in _ins][0] == SOUL_IDS[_t - 1] and _ins[0]["Quantity"] == 1 and len(_ins) == 3 and _ins[2]["ItemId"] == SOUL_ESS_IDS[_t], _ins''')
rep('''    SOUL_LANG.append("items.%s.description = Priest. Hold right click: bind up to %d %s near where you look. Each Binding drains %s Mana a second "
                     "for %s damage a second - no Mana regen while bound. Look %s s to make a Binding solid. Damage is stored as healing."
                     % (_sid, _cap, "enemy" if _cap == 1 else "enemies", bnum(SOUL_MPS[_t]), bnum(round(2.0 * SOUL_MPS[_t] * SOUL_MULT[_t], 2)),
                        bnum(SOUL_STAB[_t])))''',
    '''    SOUL_LANG.append("items.%s.description = Priest. Hold right click: bind up to %d %s near where you look. Each Binding drains %s Mana a second "
                     "for %s damage a second - no Mana regen while bound. Look %s s to make a Binding solid. Damage is stored as healing. "
                     "Hold left click and let go: Wings of Fate - glide where you look, or fly to an ally and heal them with your stored healing."
                     % (_sid, _cap, "enemy" if _cap == 1 else "enemies", bnum(SOUL_MPS[_t]), bnum(SOUL_DPS[_t]), bnum(SOUL_STAB[_t])))''')
rep('''           "IconProperties": json.loads(json.dumps(SOUL_ART[_t][3])), "Interactions": {"Secondary": ID_SOUL_ROOT}, "Weapon": {},''',
    '''           "IconProperties": json.loads(json.dumps(SOUL_ART[_t][3])), "Interactions": {"Primary": ID_WINGS_ROOT, "Secondary": ID_SOUL_ROOT}, "Weapon": {},''')
# ---- the Wings root (before the items): a Charging Primary - the wand's own charge pose + key (VWP, 0.35 s), tap = a short Simple (nothing),
# the key = an invisible marker (code 14000) the Java turns into Wings of Fate (the Monk / Shadow Step marker way)
rep('''add_root(P_WROOT, ID_SOUL_ROOT, [ID_SOUL_ROOT])
''', '''add_root(P_WROOT, ID_SOUL_ROOT, [ID_SOUL_ROOT])
# ---- 0.1.21 WINGS OF FATE (Skyy 2026-10-11 "and the traversal doesnt work yet"): HOLD LEFT CLICK (the wand's charge: VWP pose + its 0.35 s
# key, AllowIndefiniteHold = fires on release) -> the marker; a tap = nothing. Right click stays the Bindings (no clash).
ID_WINGS_ROOT, ID_WINGS_CHG = "SkyyArmory_Soul_Wings", "SkyyArmory_Soul_Wings_Charge"
ID_WINGS_TAP, ID_WINGS_LAUNCH = "SkyyArmory_Soul_Wings_Tap", "SkyyArmory_Soul_Wings_Launch"
WINGS_KEY = min(k_ for k_ in VWP["Next"] if k_ != "0")
assert WINGS_KEY == "0.35" and VWP["AllowIndefiniteHold"] is True, VWP
add_int(P_WINT, ID_WINGS_TAP, {"Type": "Simple", "RunTime": 0.05})
add_int(P_WINT, ID_WINGS_LAUNCH, launch(WINGS_MARK, VWL["Effects"]["ItemAnimationId"]))
add_int(P_WINT, ID_WINGS_CHG, {"Type": "Charging", "Effects": dict(VWP["Effects"]), "AllowIndefiniteHold": True,
                               "HorizontalSpeedMultiplier": VWP["HorizontalSpeedMultiplier"], "Next": {"0": ID_WINGS_TAP, WINGS_KEY: ID_WINGS_LAUNCH}})
add_root(P_WROOT, ID_WINGS_ROOT, [ID_WINGS_CHG])
add_prj(WINGS_MARK, blink_marker())
WINGS_PRJS = [WINGS_MARK]
''')
rep('''RICO_MARK, RICO_CODE = "SkyyArmory_Wand_Ricochet", 13000          # the invisible marker Ability 1 launches (removed at its SPAWN)''',
    '''RICO_MARK, RICO_CODE = "SkyyArmory_Wand_Ricochet", 13000          # the invisible marker Ability 1 launches (removed at its SPAWN)
WINGS_MARK, WINGS_CODE = "SkyyArmory_Soul_Wings_Mark", 14000          # 0.1.21: the invisible marker the Soul Orb / Cage left-click hold launches''')
rep('''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS + MK_PRJS + RICO_PRJS)) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) + 1 + len(BK_PRJS) + len(SS_PRJS) + len(MK_PRJS) + len(RICO_PRJS) == len(PRJS) \\
    and set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS + MK_PRJS + RICO_PRJS) == set(PRJS)''',
    '''assert len(set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS + MK_PRJS + RICO_PRJS + WINGS_PRJS)) == len(QUICK_IDS) + len(ORB_IDS) + len(S_BLINK) + 1 + len(BK_PRJS) + len(SS_PRJS) + len(MK_PRJS) + len(RICO_PRJS) + len(WINGS_PRJS) == len(PRJS) \\
    and set(QUICK_IDS + ORB_IDS + S_BLINK + [BOW_BLAST] + BK_PRJS + SS_PRJS + MK_PRJS + RICO_PRJS + WINGS_PRJS) == set(PRJS)          # 0.1.21: + the Wings marker''')

# ---------------------------------------------------------------------------------------------------------------- 4 the line looks + the wings
rep('''        put(P_PSPAWN % _new, soul_tree(finite_spawner(ours(P_PSPAWN % _old), SOUL_EMIT, FX_LIFE["ring"][1]), SOUL_COLORS[_t]))''',
    '''        put(P_PSPAWN % _new, soul_solid(soul_tree(finite_spawner(ours(P_PSPAWN % _old), SOUL_EMIT, FX_LIFE["ring"][1]), SOUL_COLORS[_t])))          # 0.1.21: tighter + bigger''')
rep('''PS_SOUL = ["SkyyArmory_Soul_%s" % _m for _m in SOUL_TIERS]
''', '''PS_SOUL = ["SkyyArmory_Soul_%s" % _m for _m in SOUL_TIERS]
PS_WISP = ["SkyyArmory_SoulWisp_%s" % _m for _m in SOUL_TIERS]          # 0.1.21: the faint wispy-line dot per tier
PS_WINGS = "SkyyArmory_Wings_Blue"          # 0.1.21: the glowing blue wing dot


def _scale(d, k):
    return dict((a_, ({"Min": round(float(v_["Min"]) * k, 4), "Max": round(float(v_["Max"]) * k, 4)} if isinstance(v_, dict) else v_)) for a_, v_ in d.items())


def soul_solid(sp):
    """0.1.21 SOLID = a brighter, thicker line (Skyy: "more obviouis when it is"): the dust packed tight round the line + every dot 1.6x"""
    sp = json.loads(json.dumps(sp))
    iaf = sp["Particle"]["InitialAnimationFrame"]
    iaf["Scale"] = _scale(iaf["Scale"], 1.6)
    if sp["Particle"]["Texture"].endswith("Spark2.png"):
        sp["EmitOffset"] = dict((a_, {"Min": 0.02, "Max": 0.08}) for a_ in ("X", "Y", "Z"))
        sp["InitialVelocity"]["Speed"] = {"Min": 0.1, "Max": 0.35}
    return sp


def soul_wisp(sp):
    """0.1.21 WISPY = a faint, thin, loose puff (Skyy: "make the lines more whispy when not tethered"): a third of the dust, 35 % opacity, 0.7x"""
    sp = json.loads(json.dumps(sp))
    assert sp["Particle"]["Texture"].endswith("Spark2.png"), sp["Particle"]["Texture"]
    sp["EmitOffset"] = dict((a_, {"Min": 0.12, "Max": 0.4}) for a_ in ("X", "Y", "Z"))
    sp["SpawnRate"] = {"Min": 20, "Max": 20}
    sp["MaxConcurrentParticles"] = 12
    sp["InitialVelocity"]["Speed"] = {"Min": 0.2, "Max": 0.7}
    iaf = sp["Particle"]["InitialAnimationFrame"]
    iaf["Scale"] = _scale(iaf["Scale"], 0.7)
    iaf["Opacity"] = 0.35
    an = sp["Particle"]["Animation"]
    an["0"]["Opacity"] = 0.35
    an["70"]["Opacity"] = 0.25
    an["100"]["Opacity"] = 0
    return sp


''')
rep('''SOUL_FILES += [P_WINT % ID_SOUL_ROOT, P_WINT % ID_SOUL_REL, P_WROOT % ID_SOUL_ROOT] + [P_WITEM % i_[len("Weapon_Wand_"):] for i_ in SOUL_IDS] + ESS_FILES''',
    '''# ---- 0.1.21 the WISPY dot per tier: the ring's dust only, faint + loose (soul_wisp), in the tier colour; the WING dot: the ring's glow, blue, 2.2x
W21_FILES = []
for _t, _psid in enumerate(PS_WISP):
    assert not az_has("psys", _psid) and (P_PSYS % _psid) not in ASSETS, _psid
    _spid = "SkyyArmory_SoulWisp_%s_Dust" % SOUL_TIERS[_t]
    put(P_PSPAWN % _spid, soul_wisp(soul_tree(finite_spawner(ours(P_PSPAWN % "SkyyArmory_Ring_Dust_Blue"), SOUL_EMIT, FX_LIFE["ring"][1]), SOUL_COLORS[_t])))
    _wd = {"Spawners": [{"SpawnerId": _spid, "PositionOffset": {"X": 0, "Y": 0, "Z": 0}}], "LifeSpan": SOUL_EMIT}
    put(P_PSYS % _psid, _wd)
    assert not endless(_wd, {_spid: ours(P_PSPAWN % _spid)})
    W21_FILES += [P_PSPAWN % _spid, P_PSYS % _psid]
_wg = soul_tree(finite_spawner(ours(P_PSPAWN % "SkyyArmory_Ring_Sparks_Blue"), 0.2, FX_LIFE["ring"][1]), "#7ab8ff")
_wg["Particle"]["InitialAnimationFrame"]["Scale"] = _scale(_wg["Particle"]["InitialAnimationFrame"]["Scale"], 2.2)
_wg["EmitOffset"] = dict((a_, {"Min": 0, "Max": 0.05}) for a_ in ("X", "Y", "Z"))
put(P_PSPAWN % "SkyyArmory_Wings_Glow", _wg)
_wgd = {"Spawners": [{"SpawnerId": "SkyyArmory_Wings_Glow", "FixedRotation": True, "PositionOffset": {"X": 0, "Y": 0, "Z": 0}}], "LifeSpan": 0.2}
assert not az_has("psys", PS_WINGS) and (P_PSYS % PS_WINGS) not in ASSETS
put(P_PSYS % PS_WINGS, _wgd)
assert not endless(_wgd, {"SkyyArmory_Wings_Glow": _wg})
W21_FILES += [P_PSPAWN % "SkyyArmory_Wings_Glow", P_PSYS % PS_WINGS]
W21_FILES += [P_WINT % ID_WINGS_TAP, P_WINT % ID_WINGS_LAUNCH, P_WINT % ID_WINGS_CHG, P_WROOT % ID_WINGS_ROOT, P_PRJ % WINGS_MARK]
W21_FILES = sorted(W21_FILES)
assert all(p_ in ASSETS for p_ in W21_FILES) and len(W21_FILES) == 8 * 2 + 2 + 5
for _r in refs_of(INTS[ID_WINGS_CHG], set()):
    assert _r in INTS or az_has("int", _r) or _r in PRJS, (ID_WINGS_CHG, _r)
assert ROOTS[ID_WINGS_ROOT] == {"Interactions": [ID_WINGS_CHG]}
print("0.1.21 soul lines + wings: %d wispy dot systems (%s ..), the solid ones tighter + 1.6x, wing dot %s; Wings root %s (Charging %s: tap %s, "
      "hold %s s -> %s -> marker %s code %d); %d new files" % (len(PS_WISP), PS_WISP[0], PS_WINGS, ID_WINGS_ROOT, ID_WINGS_CHG, ID_WINGS_TAP,
                                                                WINGS_KEY, ID_WINGS_LAUNCH, WINGS_MARK, WINGS_CODE, len(W21_FILES)))
SOUL_FILES += [P_WINT % ID_SOUL_ROOT, P_WINT % ID_SOUL_REL, P_WROOT % ID_SOUL_ROOT] + [P_WITEM % i_[len("Weapon_Wand_"):] for i_ in SOUL_IDS] + ESS_FILES''')

# ---------------------------------------------------------------------------------------------------------------- ArmoryDefs
rep('''          "public static final String[] ESS_NAMES = %s;" % jarr(ESS_NAMES), "public static final String[] ESS_IDS = %s;" % jarr(ESS_IDS)):          # 0.1.19''',
    '''          "public static final String[] ESS_NAMES = %s;" % jarr(ESS_NAMES), "public static final String[] ESS_IDS = %s;" % jarr(ESS_IDS),          # 0.1.19
          "public static final String[] SOUL_WPS = %s;" % jarr(PS_WISP), "public static final String PS_WINGS = %s;" % jstr(PS_WINGS),          # 0.1.21
          "public static final String WINGS_MARK = %s;" % jstr(WINGS_MARK), "public static final int WINGS_CODE = %d;" % WINGS_CODE):''')
rep('''  m.put(RICO_MARK, Integer.valueOf(RICO_CODE));                  // 0.1.14: the wand signature's ricochet marker''',
    '''  m.put(RICO_MARK, Integer.valueOf(RICO_CODE));                  // 0.1.14: the wand signature's ricochet marker
  m.put(WINGS_MARK, Integer.valueOf(WINGS_CODE));                // 0.1.21: the Soul Orb / Cage Wings of Fate marker''')

# ---------------------------------------------------------------------------------------------------------------- the tables + the fixed row
rep('''    ("soul.damageMult", "Damage per Mana by tier (x)", "soul", "dec", "0", "10", "x", "x soul.damagePerMana. Skyy: 1.0 / 1.1 / 1.1 / 1.5 / 1.5 / 2.0 / 2.0 / 2.5. Tooltips show defaults.", "SOUL_MULT", SOUL_MULT, SOUL_TIERS),
    ("soul.stabilize", "Seconds to make a Binding solid", "soul", "dec", "0", "10", "s", "Look at a new Binding this long; then you may look away (Skyy: 1.5-2.5 s). Tooltips show defaults.", "SOUL_STAB", SOUL_STAB, SOUL_TIERS),''',
    '''    ("soul.damagePerSecond", "Damage a second per Binding by tier", "soul", "dec", "0", "500", "", "Before SkyyGear levels. Skyy: 5 / 7 / 10 / 15 / 20 / 30 / 40 / 55. Tooltips show defaults.", "SOUL_DPS", SOUL_DPS, SOUL_TIERS),
    ("soul.stabilize", "Seconds to make a Binding solid", "soul", "dec", "0", "10", "s", "Look at a new Binding this long, then you may look away (1.75-1.0 s). Tooltips show defaults.", "SOUL_STAB", SOUL_STAB, SOUL_TIERS),''')
rep('''    ("essence.chance", "Essence drop chance (%)", "soul", "dec", "0", "100", "%", "Chance per kill of a monster of that essence's zone (Frost = Ice, Storm = Lightning).", "ESS_PCT", ESS_PCT, ESS_NAMES),
    ("essence.zone", "Essence zone (0 = volcanic caves)", "soul", "int", "0", "9", "", "Zone N mobs drop it (Void, Light: Zone 4 for now). Outside zones: Lv 1-20/21-30/31-45/46+ (fixed).", "ESS_ZONE", ESS_ZONE, ESS_NAMES),''',
    '''    ("essence.chance", "Essence drop chance (%)", "soul", "dec", "0", "100", "%", "Chance per kill of a monster of that essence's zone (the vanilla essences).", "ESS_PCT", ESS_PCT, ESS_NAMES),
    ("essence.zone", "Essence zone (0 = volcanic caves)", "soul", "int", "0", "9", "", "Zone N mobs drop it (Void: Zone 4 for now). Outside zones: Lv 1-20/21-30/31-45/46+ (fixed).", "ESS_ZONE", ESS_ZONE, ESS_NAMES),''')
rep('''              "8 items Weapon_Wand_SoulOrb / _SoulCage_<metal> (Priest), hold right click = Bindings; recipes: the tier before + bars + "
              "essence; new essences Earth + Light",''',
    '''              "8 items Weapon_Wand_SoulOrb / _SoulCage_<metal> (Priest), hold right click = Bindings, hold left click = Wings of Fate; recipes: "
              "the tier before + bars + a vanilla essence (Life, Life, Fire, Ice, Water, Lightning, Void, Concentrated Life)",''')
rep('''M(hooks, "public static String checkEssence(String key, String value) { return checkIn(key, value, @PKG@.ArmoryDefs.ESS_NAMES, \\"Life, Fire, Earth, Frost, Storm, Void or Light\\"); }")''',
    '''M(hooks, "public static String checkEssence(String key, String value) { return checkIn(key, value, @PKG@.ArmoryDefs.ESS_NAMES, \\"Life, Fire, Ice, Water, Lightning or Void\\"); }")          # 0.1.21''')

# ---------------------------------------------------------------------------------------------------------------- ArmoryCfg: soulText + load
rep('''  sb.append(" s; each drains");
  for (int i = 0; i < SOUL_MPS.length; i++) sb.append(i == 0 ? " " : " / ").append(cfmt(SOUL_MPS[i]));
  sb.append(" Mana/s for ").append(cfmt(SOUL_DPM)).append(" x");
  for (int i = 0; i < SOUL_MULT.length; i++) sb.append(i == 0 ? " " : " / ").append(cfmt(SOUL_MULT[i]));
  sb.append(" damage per Mana every ").append(cfmt(SOUL_TICK)).append(" s; ").append(SOUL_STORE).append("% stored as healing, Mana regen ")''',
    '''  sb.append(" s; each drains");
  for (int i = 0; i < SOUL_MPS.length; i++) sb.append(i == 0 ? " " : " / ").append(cfmt(SOUL_MPS[i]));
  sb.append(" Mana/s for");
  for (int i = 0; i < SOUL_DPS.length; i++) sb.append(i == 0 ? " " : " / ").append(cfmt(SOUL_DPS[i]));
  sb.append(" damage/s (before levels) every ").append(cfmt(SOUL_TICK)).append(" s; ").append(SOUL_STORE).append("% stored as healing, Mana regen ")''')
rep('''      .append(ESS_ZONE[i] < 0.5 ? "volcanic caves" : "Z" + (int) ESS_ZONE[i]);
  }
  return sb.append(")").toString();
}""")''', '''      .append(ESS_ZONE[i] < 0.5 ? "volcanic caves" : "Z" + (int) ESS_ZONE[i]);
  }
  sb.append("); line dots ").append(SOUL_DOTS).append(" a draw");
  sb.append("; Wings of Fate ").append(WINGS_ON ? "on" : "OFF").append(" (hold left click: ").append(cfmt(WINGS_MA)).append(" Mana + ").append(cfmt(WINGS_ST))
    .append(" Stamina; ").append(WINGS_BOUNDS).append(" glide bounds at ").append(cfmt(WINGS_SPEED)).append(" b/s, or up to ").append(WINGS_ABOUNDS)
    .append(" to an ally within ").append(WINGS_RANGE).append(" blocks at ").append(cfmt(WINGS_ASPEED)).append(" b/s, a bound every ").append(cfmt(WINGS_BOUND))
    .append(" s; arriving heals ").append(cfmt(WINGS_BASE)).append("% + ").append(cfmt(WINGS_PER)).append("% a tier + the stored healing, at most ")
    .append(WINGS_CAP).append("%)");
  return sb.toString();
}""")''')
rep('''  SOUL_DPM = dec(c.getProperty("soul.damagePerMana"), 2.0, 0.0, 50.0);
''', '')
rep('''  SOUL_DOTS = intOf(c.getProperty("soul.lineDots"), 48, 0, 96);
  ESS_ON = bool(c.getProperty("essence.drops"), true);''', '''  SOUL_DOTS = intOf(c.getProperty("soul.lineDots"), 64, 0, 128);          // 0.1.21: 48 -> 64 (denser solid lines)
  ESS_ON = bool(c.getProperty("essence.drops"), true);
  WINGS_ON = bool(c.getProperty("wings.enabled"), true);          // 0.1.21 Wings of Fate
  WINGS_MA = dec(c.getProperty("wings.mana"), 20.0, 0.0, 200.0);
  WINGS_ST = dec(c.getProperty("wings.stamina"), 10.0, 0.0, 100.0);
  WINGS_SPEED = dec(c.getProperty("wings.speed"), 18.0, 4.0, 40.0);
  WINGS_BOUND = dec(c.getProperty("wings.boundSeconds"), 0.35, 0.15, 1.0);
  WINGS_BOUNDS = intOf(c.getProperty("wings.bounds"), 3, 1, 8);
  WINGS_ABOUNDS = intOf(c.getProperty("wings.allyBounds"), 8, 1, 16);
  WINGS_ASPEED = dec(c.getProperty("wings.allySpeed"), 24.0, 4.0, 48.0);
  WINGS_LIFT = dec(c.getProperty("wings.lift"), 4.0, 0.0, 15.0);
  WINGS_RANGE = intOf(c.getProperty("wings.lockRange"), 30, 5, 64);
  WINGS_CONE = intOf(c.getProperty("wings.lockCone"), 30, 4, 90);
  WINGS_ARRIVE = dec(c.getProperty("wings.arrive"), 3.0, 1.0, 8.0);
  WINGS_BASE = dec(c.getProperty("wings.baseHeal"), 10.0, 0.0, 60.0);
  WINGS_PER = dec(c.getProperty("wings.tierHeal"), 1.0, 0.0, 10.0);
  WINGS_CAP = intOf(c.getProperty("wings.healCap"), 60, 0, 100);
  WINGS_ANY = bool(c.getProperty("wings.anyPlayer"), true);''')
rep('''  SOUL_MULT = tab(c, "soul.damageMult.", @PKG@.ArmoryDefs.SOUL_TIERS, SOUL_MULT_DEF, 0.0, 10.0);''',
    '''  SOUL_DPS = tab(c, "soul.damagePerSecond.", @PKG@.ArmoryDefs.SOUL_TIERS, SOUL_DPS_DEF, 0.0, 500.0);          // 0.1.21''')

# ---------------------------------------------------------------------------------------------------------------- Soul: damage, lines, takeAll
rep('''M(soul, r"""public static double dps(double dpm, double mps, double mult) { return (dpm > 0.0 && mps > 0.0 && mult > 0.0) ? dpm * mps * mult : 0.0; }""")''',
    '''# 0.1.21 (Skyy 2026-10-11 "it needs a lot more damage"): a Binding's damage a second = soul.damagePerSecond.<tier> (before levels); <= 0 = none
M(soul, r"""
public static double dps(int tier) {
  if (tier < 0 || tier >= @PKG@.ArmoryCfg.SOUL_DPS.length) return 0.0;
  double v = @PKG@.ArmoryCfg.SOUL_DPS[tier];
  return v > 0.0 ? v : 0.0;
}""")''')
rep('''    double per = dps(@PKG@.ArmoryCfg.SOUL_DPM, mps, @PKG@.ArmoryCfg.SOUL_MULT[tier]) * secs;''',
    '''    double per = dps(tier) * secs;          // 0.1.21: the tier's damage a second (no longer Mana x damage per Mana x multiple)''')
rep('''# the look of a Binding: a dotted line from the cage (in front of your hand) to the mob - wispy = sparse, solid = dense - in the tier colour;
# at most soul.lineDots (48) dots a line-draw for ALL of a player's Bindings together (20 Onyxium Bindings = 2 dots each: the packet budget)
M(soul, r"""
public static int line(@CAC@ acc, int tier, double[] f, double[] c, boolean solid, int most) {
  if (f == null || c == null || tier < 0 || tier >= @PKG@.ArmoryDefs.SOUL_PS.length) return 0;
  double dx = c[0] - f[0];
  double dy = c[1] - f[1];
  double dz = c[2] - f[2];
  double l = Math.sqrt(dx * dx + dy * dy + dz * dz);
  int n = (int) Math.floor(l / (solid ? 0.6 : 1.5));
  int cap = most < 2 ? 1 : most - 1;
  if (n > cap) n = cap;
  int out = 0;
  for (int k = 0; k <= n; k++) {
    double fr = n == 0 ? 1.0 : (double) k / (double) n;
    @PKG@.ArmoryTrav.particle(@PKG@.ArmoryDefs.SOUL_PS[tier], f[0] + dx * fr, f[1] + dy * fr, f[2] + dz * fr, acc);
    out = out + 1;
  }
  return out;
}""")''', '''# the look of a Binding (0.1.21, Skyy 2026-10-11: "make the lines more whispy when not tethered, and more obviouis when it is."): a dotted
# line from the cage (in front of your hand) to the mob in the tier colour. WISPY = sparse (WISP_GAP 1.8 blocks), the faint SoulWisp system,
# FLICKERING (dot k is skipped when (k + draw) % 3 == 0: a third of the dots gone, the gap moving every draw); SOLID = dense (SOLID_GAP 0.45),
# the bright thick Soul system. soul.lineDots (64) = the budget of ALL of a player's lines per draw, shared out by alloc
F(soul, "public static final double SOLID_GAP = 0.45;")
F(soul, "public static final double WISP_GAP = 1.8;")
F(soul, "public static volatile long DOTS = 0L;")
M(soul, r"""
public static int want(double len, boolean solid) {
  if (!(len > 0.0)) return 1;
  return (int) Math.floor(len / (solid ? SOLID_GAP : WISP_GAP)) + 1;
}""")
# the budget: every line asks for want dots; when the sum is over the budget each gets its share (floor, at least 1), trimmed from the
# largest until the sum fits; budget <= 0 = nothing
M(soul, r"""
public static int[] alloc(int[] want, int budget) {
  int n = want == null ? 0 : want.length;
  int[] out = new int[n];
  if (n == 0 || budget <= 0) return out;
  int tot = 0;
  for (int k = 0; k < n; k++) if (want[k] > 0) tot = tot + want[k];
  if (tot <= budget) {
    for (int k = 0; k < n; k++) out[k] = want[k] > 0 ? want[k] : 0;
    return out;
  }
  int used = 0;
  for (int k = 0; k < n; k++) {
    int w = want[k] > 0 ? want[k] : 0;
    int c = (int) Math.floor((double) w * (double) budget / (double) tot);
    if (c < 1 && w > 0) c = 1;
    out[k] = c;
    used = used + c;
  }
  while (used > budget) {
    int bi = -1;
    for (int k = 0; k < n; k++) if (out[k] > 0 && (bi < 0 || out[k] > out[bi])) bi = k;
    if (bi < 0) break;
    out[bi] = out[bi] - 1;
    used = used - 1;
  }
  return out;
}""")
# FIX (review: "at Cobalt and above a solid line is no denser than a lone wispy one"): a WISPY line gets at most half a fair share (budget /
# lines / 2, at least 1) FIRST, the SOLID lines share the rest (alloc: as asked when it fits) - so a solid line always keeps at least twice a
# wispy line's dots at every tier (64 dots, 10-block lines: Thorium 5 vs 10, Cobalt 3 vs 6, Onyxium 1 vs 3); never above the budget
M(soul, r"""
public static int[] share(int[] want, boolean[] solid, int budget) {
  int n = want == null ? 0 : want.length;
  int[] out = new int[n];
  if (n == 0 || budget <= 0) return out;
  int fair = budget / n;
  if (fair < 1) fair = 1;
  int wcap = fair / 2;
  if (wcap < 1) wcap = 1;
  int[] sw = new int[n];
  int usedW = 0;
  int ns = 0;
  for (int k = 0; k < n; k++) {
    int w = want[k] > 0 ? want[k] : 0;
    boolean so = solid != null && k < solid.length && solid[k];
    if (so) { sw[k] = w; if (w > 0) ns = ns + 1; }
    else { sw[k] = 0; out[k] = w < wcap ? w : wcap; usedW = usedW + out[k]; }
  }
  int rest = budget - usedW;
  if (ns > 0 && rest > 0) {
    int[] g = alloc(sw, rest);          // fits = as asked, else shared in proportion (at least 1 each)
    for (int k = 0; k < n; k++) if (solid != null && k < solid.length && solid[k]) out[k] = g[k];
  }
  int used = 0;
  for (int k = 0; k < n; k++) used = used + out[k];
  while (used > budget) {
    int bi = -1;
    for (int k = 0; k < n; k++) if (out[k] > 0 && (bi < 0 || out[k] > out[bi])) bi = k;
    if (bi < 0) break;
    out[bi] = out[bi] - 1;
    used = used - 1;
  }
  return out;
}""")
M(soul, r"""public static boolean flick(int k, int draw) { return ((k + draw) % 3) == 0; }""")
M(soul, r"""
public static int line(@CAC@ acc, int tier, double[] f, double[] c, boolean solid, int count, int draw) {
  if (f == null || c == null || count <= 0 || tier < 0 || tier >= @PKG@.ArmoryDefs.SOUL_PS.length || tier >= @PKG@.ArmoryDefs.SOUL_WPS.length) return 0;
  double dx = c[0] - f[0];
  double dy = c[1] - f[1];
  double dz = c[2] - f[2];
  String id = solid ? @PKG@.ArmoryDefs.SOUL_PS[tier] : @PKG@.ArmoryDefs.SOUL_WPS[tier];
  int out = 0;
  for (int k = 0; k < count; k++) {
    if (!solid && count > 1 && flick(k, draw)) continue;
    double fr = count == 1 ? 1.0 : (double) k / (double) (count - 1);
    @PKG@.ArmoryTrav.particle(id, f[0] + dx * fr, f[1] + dy * fr, f[2] + dz * fr, acc);
    out = out + 1;
  }
  DOTS = DOTS + (long) out;
  return out;
}""")''')
rep('''  if (now >= s.fx && a != null && @PKG@.ArmoryCfg.SOUL_DOTS > 0) {
    s.fx = now + FX_MS;
    double[] from = handPos(a);
    int most = @PKG@.ArmoryCfg.SOUL_DOTS / (s.binds.size() > 0 ? s.binds.size() : 1);
    for (int k = 0; k < s.binds.size(); k++) {
      @PKG@.SoulBind b = (@PKG@.SoulBind) s.binds.get(k);
      line(cb, tier, from, centre(cb, b.t), b.stable, most);
    }
  }''', '''  if (now >= s.fx && a != null && @PKG@.ArmoryCfg.SOUL_DOTS > 0) {          // 0.1.21: wispy / solid looks, the budget shared out (alloc)
    s.fx = now + FX_MS;
    s.draws = s.draws + 1;
    double[] from = handPos(a);
    int nb = s.binds.size();
    int[] w = new int[nb];
    double[] cx = new double[nb];
    double[] cy = new double[nb];
    double[] cz = new double[nb];
    boolean[] ok = new boolean[nb];
    boolean[] so = new boolean[nb];
    for (int k = 0; k < nb; k++) {
      @PKG@.SoulBind b = (@PKG@.SoulBind) s.binds.get(k);
      so[k] = b.stable;
      double[] c = centre(cb, b.t);
      ok[k] = c != null && from != null;
      if (!ok[k]) { w[k] = 0; continue; }
      cx[k] = c[0];
      cy[k] = c[1];
      cz[k] = c[2];
      w[k] = want(dist(from[0], from[1], from[2], c[0], c[1], c[2]), b.stable);
    }
    int[] got = share(w, so, @PKG@.ArmoryCfg.SOUL_DOTS);          // FIX (review): wispy held first, solid share the rest
    for (int k = 0; k < nb; k++) {
      if (!ok[k] || got[k] <= 0) continue;
      @PKG@.SoulBind b = (@PKG@.SoulBind) s.binds.get(k);
      line(cb, tier, from, new double[] { cx[k], cy[k], cz[k] }, b.stable, got[k], s.draws);
    }
  }''')
rep('''          "public boolean blocked;", "public double drained;", "public double dealt;", "public double[] p;", "public long lookAt;"):
    F(sstate, f)''', '''          "public boolean blocked;", "public double drained;", "public double dealt;", "public double[] p;", "public long lookAt;",
          "public int draws;"):          # 0.1.21: the line draws (the wispy flicker moves with it)
    F(sstate, f)''')
rep('''  this.p = null;
  this.lookAt = 0L;
}""")''', '''  this.p = null;
  this.lookAt = 0L;
  this.draws = 0;
}""")''')
rep('''# who may be bound: an enemy MOB''', '''# 0.1.21 WINGS OF FATE: ALL the stored healing at once (the pool empties - Skyy: "plus all the stored soul healing on top"); the arrival heal
# caps the total, the rest is gone
M(soul, r"""
public static double takeAll(java.util.UUID u, long now) {
  if (u == null) return 0.0;
  double hp = poolNow(u, now);
  if (POOL.remove(u) != null) publish(u, 0.0);
  return hp > 0.0 ? hp : 0.0;
}""")
# who may be bound: an enemy MOB''')

# ---------------------------------------------------------------------------------------------------------------- 5 Wings of Fate (Java)
WINGS_JAVA = r'''# ---------------------------------------------------------------- 0.1.21 WINGS OF FATE (tools/armory_0_1_21_patch.py; Skyy 2026-10-11 "and the traversal doesnt work yet")
wst = pool.makeClass(PKG + ".WingsState")
wings = pool.makeClass(PKG + ".Wings")
ALL += [wst, wings]
for f in ("public java.util.UUID u;", "public @REF@ ref;", "public @ST@ st;", "public int tier;", "public String item;", "public @REF@ ally;",
          "public java.util.UUID au;", "public String aname;", "public int bounds;", "public int most;", "public long next;", "public long t0;",
          "public long last;", "public double x0;", "public double y0;", "public double z0;", "public double paidS;", "public double paidM;",
          "public long fx;", "public double hx;", "public double hz;",
          "public long gen;", "public String pk;", "public int fails;"):          # FIX (review): the profile at cast + failed bounds in a row
    F(wst, f)
C(wst, r"""
public WingsState(java.util.UUID u, @REF@ ref, @ST@ st, int tier, String item, long now) {
  this.u = u;
  this.ref = ref;
  this.st = st;
  this.tier = tier;
  this.item = item;
  this.ally = null;
  this.au = null;
  this.aname = null;
  this.bounds = 0;
  this.most = 0;
  this.next = now;
  this.t0 = now;
  this.last = now;
  this.paidS = 0.0;
  this.paidM = 0.0;
  this.fx = 0L;
  this.hx = 1.0;
  this.hz = 0.0;
  this.gen = 0L;
  this.pk = null;
  this.fails = 0;
}""")
for f in ("public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile long CLOCK = 0L;",          # HARNESS SEAM ONLY (0 in the game = the wall clock)
          "public static final long FX_MS = 150L;", "public static final int WING_DOTS = 5;", "public static final double MAX_UP = 15.0;",
          "public static volatile long MARKS = 0L;", "public static volatile long CASTS = 0L;", "public static volatile long REFUSED = 0L;",
          "public static volatile long LOCKS = 0L;", "public static volatile long BOUNDS = 0L;", "public static volatile long WRITES = 0L;",
          "public static volatile long KEPT = 0L;", "public static volatile long ARRIVALS = 0L;", "public static volatile long ENDS = 0L;",
          "public static volatile long REFUNDS = 0L;", "public static volatile long XP = 0L;", "public static volatile long FXDOTS = 0L;",
          "public static volatile double HEALED = 0.0;", "public static volatile double LAST_HEAL = 0.0;", "public static volatile double LAST_STORED = 0.0;",
          "public static volatile double LAST_BASE = 0.0;", "public static volatile String LAST_WHY = \"\";", "public static volatile String LAST_END = \"\";",
          "public static volatile long SWEEP_AT = 0L;", "public static volatile long STALE = 0L;", "public static final long STALE_MS = 15000L;",
          "public static final int FAIL_MAX = 5;", "public static volatile long FAILS = 0L;"):          # FIX (review): 5 failed bounds in a row = the end
    F(wings, f)
M(wings, r"""public static long now() { long c = CLOCK; return c != 0L ? c : System.currentTimeMillis(); }""")
M(wings, r"""public static void warn(String key, String msg) { @PKG@.ArmoryLog.warnOnce("wings:" + key, msg); }""")
M(wings, r"""public static long boundMs() { long m = Math.round(@PKG@.ArmoryCfg.WINGS_BOUND * 1000.0); return m < 50L ? 50L : m; }""")
# ---- PURE maths (the harness runs them on plain numbers)
# a bound toward a point (dx, dy, dz away) that lands there after t seconds under gravity g (ballistic); sideways at most maxH, up at most maxUp
M(wings, r"""
public static double[] toward(double dx, double dy, double dz, double t, double g, double maxH, double maxUp) {
  if (!(t > 0.0)) return null;
  double vx = dx / t;
  double vz = dz / t;
  double vy = dy / t + 0.5 * (g > 0.0 ? g : 0.0) * t;
  double h = Math.sqrt(vx * vx + vz * vz);
  if (maxH > 0.0 && h > maxH) { vx = vx * maxH / h; vz = vz * maxH / h; }
  if (maxUp > 0.0 && vy > maxUp) vy = maxUp;
  return new double[] { vx, vy, vz };
}""")
# a plain glide bound: the look x speed, + lift up, the up part at most maxUp
M(wings, r"""
public static double[] glide(double lx, double ly, double lz, double speed, double lift, double maxUp) {
  double vy = ly * speed + lift;
  if (maxUp > 0.0 && vy > maxUp) vy = maxUp;
  return new double[] { lx * speed, vy, lz * speed };
}""")
# the arrival heal: (base % + per-tier % x tier) of the ally's max Health + ALL the stored healing, at most cap % of that max Health
M(wings, r"""
public static double healAmt(double maxHp, int tier, double basePct, double perTier, double stored, double capPct) {
  if (!(maxHp > 0.0)) return 0.0;
  double b = maxHp * (basePct + perTier * (double) (tier < 0 ? 0 : tier)) / 100.0;
  if (!(b > 0.0)) b = 0.0;
  double t = b + (stored > 0.0 ? stored : 0.0);
  double c = maxHp * (capPct > 0.0 ? capPct : 0.0) / 100.0;
  if (t > c) t = c;
  return t > 0.0 ? t : 0.0;
}""")
M(wings, r"""
public static double baseOf(double maxHp, int tier, double basePct, double perTier) {
  if (!(maxHp > 0.0)) return 0.0;
  double b = maxHp * (basePct + perTier * (double) (tier < 0 ? 0 : tier)) / 100.0;
  return b > 0.0 ? b : 0.0;
}""")
# ---- engine glue (world thread; never throws)
M(wings, r"""
public static double heal(@CAC@ acc, @REF@ t, double want) {
  if (!(want > 0.0) || t == null) return 0.0;
  try {
    @ESM@ m = (@ESM@) acc.getComponent(t, @ESM@.getComponentType());
    if (m == null) return 0.0;
    int hi = @DST@.getHealth();
    if (hi < 0) return 0.0;
    @ESV@ v = m.get(hi);
    if (v == null || v.get() <= 0.0f) return 0.0;
    double room = (double) (v.getMax() - v.get());
    double got = want < room ? want : room;
    if (!(got > 0.01)) return 0.0;
    m.addStatValue(hi, (float) got);
    return got;
  } catch (Throwable e) { warn("heal", "the Wings of Fate heal failed (" + e + ")"); return 0.0; }
}""")
# FIX (review): the profile key (tools/PROFILES-CONTRACT.md pkey) - SkyySkills refuses the XP when the profile moved on (healxp's expectKey)
M(wings, r"""
public static String pkey(java.util.UUID u) {
  if (u == null) return null;
  try {
    Object f = @PKG@.ArmoryTree.bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(wings, r"""
public static void xp(java.util.UUID u, double hp, String pk) {
  if (u == null || !(hp > 0.0)) return;
  java.util.function.Function f = @PKG@.ArmoryTrav.fn("skill:fn:healxp");
  if (f == null) return;
  Object[] a = pk == null ? new Object[] { u, Double.valueOf(hp), "armory:wings" } : new Object[] { u, Double.valueOf(hp), "armory:wings", pk };
  try { f.apply(a); XP = XP + 1L; }
  catch (Throwable t) { warn("xp", "skill:fn:healxp failed (" + t + ") - no Divinity XP for Wings of Fate heals"); }
}""")
# the ally: another living PLAYER - in a party only its members (class:fn:ally / party:fn:members), in none any player (wings.anyPlayer) -
# nearest your crosshair inside wings.lockCone within wings.lockRange with line of sight (eye -> their middle)
M(wings, r"""
public static @REF@ pickAlly(@CB@ buf, @REF@ me, java.util.UUID u, double[] a, @PKG@.TravGrid g) {
  if (a == null || a.length < 6 || u == null) return null;
  String[] party = @PKG@.ArmoryTrav.members(u);          // null = no SkyyParty; a party = any member besides you (SkyyParty lists you too)
  boolean inParty = false;
  if (party != null) for (int i = 0; i < party.length; i++) if (party[i] != null && !party[i].equalsIgnoreCase(u.toString())) { inParty = true; break; }
  if (!inParty && !@PKG@.ArmoryCfg.WINGS_ANY) return null;
  double rng = (double) @PKG@.ArmoryCfg.WINGS_RANGE;
  double half = (double) @PKG@.ArmoryCfg.WINGS_CONE * 0.5;
  java.util.List l = @PKG@.ArmoryTrav.near(buf, a[0], a[1], a[2], rng + 2.0);
  @REF@ best = null;
  double bo = 0.0;
  double bd = 0.0;
  for (int k = 0; k < l.size(); k++) {
    Object o = l.get(k);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!t.isValid() || (me != null && t.equals(me))) continue;
    @PR@ pr = @PKG@.Kunai.prOf(buf, t);
    if (pr == null) continue;
    java.util.UUID tu = pr.getUuid();
    if (tu == null || tu.equals(u) || @PKG@.ArmoryTrav.dead(buf, t)) continue;
    if (inParty && !@PKG@.ArmoryTrav.ally(u, tu)) continue;
    @VEC@ q = @PKG@.ArmoryTrav.posOf(buf, t);
    if (q == null) continue;
    double vx = q.x - a[0];
    double vy = q.y + 0.9 - a[1];
    double vz = q.z - a[2];
    double d = Math.sqrt(vx * vx + vy * vy + vz * vz);
    if (d > rng + 1.0E-9 || d < 0.5) continue;
    double off = @PKG@.TravMath.offDeg(a[3], a[4], a[5], vx, vy, vz);
    if (off > half + 1.0E-9) continue;
    if (g != null && !@PKG@.TravMath.clear(g, a[0], a[1], a[2], q.x, q.y + 0.9, q.z)) continue;
    if (best == null || off < bo - 1.0E-6 || (Math.abs(off - bo) <= 1.0E-6 && d < bd)) { best = t; bo = off; bd = d; }
  }
  return best;
}""")
# ONE BOUND = ONE velocity Set (a glide: the wand launch's dash config; a carry: a plain Set like the Monk vault, whose ballistic maths were
# measured in game): to the ally (re-aimed every bound, ballistic: lands on the aim point after one
# bound's time, at most wings.allySpeed x bound seconds of the way) or a glide where you look; a fall faster than MinFallSpeedToEngageRoll
# is KEPT (TravMath.hopVy - the wand / bow rule; no fall-damage escape). No void protection (Skyy 2026-10-07).
M(wings, r"""
public static boolean bound(@PKG@.WingsState s, @CB@ buf, @REF@ r, double[] a, long now) {
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, r);
  if (p == null) return false;
  double t = (double) boundMs() / 1000.0;
  double[] v = null;
  if (s.ally != null) {
    @VEC@ q = @PKG@.ArmoryTrav.posOf(buf, s.ally);
    if (q == null) return false;
    double dx = q.x - p.x;
    double dy = q.y - p.y;
    double dz = q.z - p.z;
    double d = Math.sqrt(dx * dx + dy * dy + dz * dz);
    double step = @PKG@.ArmoryCfg.WINGS_ASPEED * t;
    double f = d > step && d > 1.0E-9 ? step / d : 1.0;
    v = toward(dx * f, dy * f, dz * f, t, @PKG@.Monk.grav(), @PKG@.ArmoryCfg.WINGS_ASPEED * 1.5, 25.0);
  } else {
    if (a == null || a.length < 6) return false;
    v = glide(a[3], a[4], a[5], @PKG@.ArmoryCfg.WINGS_SPEED, @PKG@.ArmoryCfg.WINGS_LIFT, MAX_UP);
  }
  if (v == null) return false;
  double cvy = @PKG@.Leap.clientVy(buf, r);
  double vy = @PKG@.TravMath.hopVy(v[1], cvy, @PKG@.ArmoryTrav.maxFall(@PKG@.ArmoryTrav.worldOf(buf)));
  if (vy != v[1]) KEPT = KEPT + 1L;
  if (!@PKG@.Leap.vel(buf, r, v[0], vy, v[2], s.ally == null)) return false;          // glide = the wand launch's dash config; carry = a plain Set (the Monk vault's ballistic)
  WRITES = WRITES + 1L;
  s.bounds = s.bounds + 1;
  s.next = now + boundMs();
  s.last = now;
  double h = Math.sqrt(v[0] * v[0] + v[2] * v[2]);
  if (h > 1.0E-6) { s.hx = v[0] / h; s.hz = v[2] / h; }
  BOUNDS = BOUNDS + 1L;
  return true;
}""")
# the wings: WING_DOTS glowing blue dots per wing in an arc out from the back (the last bound's heading) + one blue trail dot at the body
M(wings, r"""
public static int draw(@CAC@ acc, @VEC@ p, @PKG@.WingsState s) {
  if (p == null || s == null) return 0;
  double rx = 0.0 - s.hz;
  double rz = s.hx;
  int n = 0;
  for (int side = -1; side <= 1; side = side + 2) {
    for (int k = 1; k <= WING_DOTS; k++) {
      double out = 0.28 * (double) k;
      double up = 0.55 * Math.sin(Math.PI * (double) k / (double) (WING_DOTS + 1)) + 0.06 * (double) k;
      double back = 0.3 + 0.06 * (double) k;
      @PKG@.ArmoryTrav.particle(@PKG@.ArmoryDefs.PS_WINGS, p.x - s.hx * back + rx * out * (double) side, p.y + 1.15 + up, p.z - s.hz * back + rz * out * (double) side, acc);
      n = n + 1;
    }
  }
  @PKG@.ArmoryTrav.particle(@PKG@.ArmoryDefs.SOUL_PS[0], p.x - s.hx * 0.4, p.y + 0.7, p.z - s.hz * 0.4, acc);
  n = n + 1;
  FXDOTS = FXDOTS + (long) n;
  return n;
}""")
# a player who left mid-flight never ticks again: every 5 s any tick drops flights idle for STALE_MS (15 s; a flight is at most ~9 s)
M(wings, r"""
public static int sweep(long now) {
  int n = 0;
  java.util.Iterator it = STATES.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object v = e.getValue();
    if (v instanceof @PKG@.WingsState && now - ((@PKG@.WingsState) v).last <= STALE_MS) continue;
    it.remove();
    n = n + 1;
  }
  STALE = STALE + (long) n;
  return n;
}""")
M(wings, r"""
public static void say(@PR@ pr, String text, String color) {
  try { if (pr != null) pr.sendMessage(@MSG@.raw(text).color(color)); } catch (Throwable t) { }
}""")
# the end: a move that did not move you a block (a wall in the way) costs nothing (LOCKED 2026-10-05) - the Mana + Stamina given back
M(wings, r"""
public static void end(@PKG@.WingsState s, @CAC@ acc, @REF@ r, String why, long now) {
  if (s == null) return;
  STATES.remove(s.u, s);
  ENDS = ENDS + 1L;
  LAST_END = why;
  LAST_WHY = "ended (" + why + ")";
  @VEC@ p = r == null ? null : @PKG@.ArmoryTrav.posOf(acc, r);
  if (p == null || (!(s.paidS > 0.0) && !(s.paidM > 0.0))) return;
  double dx = p.x - s.x0;
  double dy = p.y - s.y0;
  double dz = p.z - s.z0;
  if (Math.sqrt(dx * dx + dz * dz) >= 1.0 || Math.abs(dy) >= 1.0) return;
  @PKG@.ArmoryTrav.addStat(acc, r, @DST@.getStamina(), s.paidS);
  @PKG@.ArmoryTrav.addStat(acc, r, @DST@.getMana(), s.paidM);
  s.paidS = 0.0;
  s.paidM = 0.0;
  REFUNDS = REFUNDS + 1L;
  LAST_WHY = "ended (" + why + ") - it did not move you: Mana + Stamina given back";
}""")
# ARRIVED: the ally heals base + ALL the stored soul healing (Soul.takeAll - the pool empties), capped; Divinity XP; both told
M(wings, r"""
public static double arrive(@PKG@.WingsState s, @CB@ buf, @REF@ r, @PR@ pr, long now) {
  STATES.remove(s.u, s);
  ARRIVALS = ARRIVALS + 1L;
  float mx = @PKG@.Soul.statOf(buf, s.ally, @PKG@.Soul.hpIdx(), true);
  double max = mx > 0.0f ? (double) mx : 0.0;
  double stored = @PKG@.Soul.takeAll(s.u, now);
  double base = baseOf(max, s.tier, @PKG@.ArmoryCfg.WINGS_BASE, @PKG@.ArmoryCfg.WINGS_PER);
  double want = healAmt(max, s.tier, @PKG@.ArmoryCfg.WINGS_BASE, @PKG@.ArmoryCfg.WINGS_PER, stored, (double) @PKG@.ArmoryCfg.WINGS_CAP);
  double got = heal(buf, s.ally, want);
  LAST_BASE = base;
  LAST_STORED = stored;
  LAST_HEAL = got;
  HEALED = HEALED + got;
  LAST_END = "arrived";
  LAST_WHY = "arrived - healed " + @PKG@.TravMath.fmt(got) + " (base " + @PKG@.TravMath.fmt(base) + " + stored " + @PKG@.TravMath.fmt(stored) + ", cap "
    + @PKG@.ArmoryCfg.WINGS_CAP + "%)";
  xp(s.u, got, s.pk);          // FIX (review): the cast's profile key
  @VEC@ q = @PKG@.ArmoryTrav.posOf(buf, s.ally);
  if (q != null) {
    for (int k = 0; k < 6; k++) {
      double an = Math.PI * 2.0 * (double) k / 6.0;
      @PKG@.ArmoryTrav.particle(@PKG@.ArmoryDefs.PS_WINGS, q.x + Math.cos(an) * 0.7, q.y + 1.0, q.z + Math.sin(an) * 0.7, buf);
    }
  }
  say(pr, "Wings of Fate: you healed " + (s.aname == null ? "your ally" : s.aname) + " for " + @PKG@.TravMath.fmt(got)
    + (stored > 0.0 ? " (" + @PKG@.TravMath.fmt(stored) + " from your Bindings)." : "."), "#8fd1ff");
  try {
    @PR@ apr = @PKG@.Kunai.prOf(buf, s.ally);
    if (apr != null && pr != null && got > 0.0) say(apr, pr.getUsername() + " flew to you on Wings of Fate: +" + @PKG@.TravMath.fmt(got) + " Health.", "#8fd1ff");
  } catch (Throwable t) { }
  return got;
}""")
# THE CAST (the marker's SPAWN): class lock, a soul weapon in hand, alive / not mounted, not already flying, the cost (2 Mana : 1 Stamina),
# the ally lock, the first bound now
M(wings, r"""
public static boolean cast(java.util.UUID u, @REF@ r, @ST@ st, @CB@ buf) {
  long now = now();
  @PR@ pr = @PKG@.Kunai.prOf(buf, r);
  if (!@PKG@.ArmoryCfg.WINGS_ON) { REFUSED = REFUSED + 1L; LAST_WHY = "Wings of Fate off"; return false; }
  String item = @PKG@.Leap.hand(buf, r, u);
  int tier = @PKG@.Soul.tierOf(item);
  if (tier < 0) { REFUSED = REFUSED + 1L; LAST_WHY = "no soul weapon in hand"; return false; }
  if (!@PKG@.ArmoryTrav.allowed(u, item)) { REFUSED = REFUSED + 1L; LAST_WHY = "class lock"; @PKG@.ArmoryTrav.tell(pr, "Only Priests can use Wings of Fate."); return false; }
  if (@PKG@.ArmoryTrav.dead(buf, r) || @PKG@.Leap.mounted(buf, r)) { REFUSED = REFUSED + 1L; LAST_WHY = "dead or mounted"; return false; }
  @PKG@.WingsState old = (@PKG@.WingsState) STATES.get(u);
  if (old != null && old.st == st) { REFUSED = REFUSED + 1L; LAST_WHY = "already flying"; return false; }
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, r);
  double[] a = @PKG@.Leap.aim(buf, r, u, null);
  if (p == null || a == null) { REFUSED = REFUSED + 1L; LAST_WHY = "no position / look"; return false; }
  if (@PKG@.Leap.take(buf, r, @PKG@.ArmoryCfg.WINGS_ST, @PKG@.ArmoryCfg.WINGS_MA) == 0) {
    REFUSED = REFUSED + 1L;
    LAST_WHY = "too little Stamina or Mana";
    @PKG@.ArmoryTrav.tell(pr, "Not enough Mana or Stamina for Wings of Fate - " + @PKG@.TravMath.fmt(@PKG@.ArmoryCfg.WINGS_MA) + " Mana + "
      + @PKG@.TravMath.fmt(@PKG@.ArmoryCfg.WINGS_ST) + " Stamina.");
    return false;
  }
  @PKG@.WingsState s = new @PKG@.WingsState(u, r, st, tier, item, now);
  s.x0 = p.x;
  s.y0 = p.y;
  s.z0 = p.z;
  s.paidS = @PKG@.ArmoryCfg.WINGS_ST;
  s.paidM = @PKG@.ArmoryCfg.WINGS_MA;
  s.gen = @PKG@.ArmoryTree.gen(u);          // FIX (review): a profile switch mid-flight ends it
  s.pk = pkey(u);
  double hl = Math.sqrt(a[3] * a[3] + a[5] * a[5]);
  if (hl > 1.0E-6) { s.hx = a[3] / hl; s.hz = a[5] / hl; }
  @REF@ al = pickAlly(buf, r, u, a, @PKG@.ArmoryTrav.grid(@PKG@.ArmoryTrav.worldOf(buf)));
  if (al != null) {
    @PR@ apr = @PKG@.Kunai.prOf(buf, al);
    s.ally = al;
    s.au = apr == null ? null : apr.getUuid();
    s.aname = apr == null ? null : apr.getUsername();
    s.most = @PKG@.ArmoryCfg.WINGS_ABOUNDS;
    LOCKS = LOCKS + 1L;
  } else s.most = @PKG@.ArmoryCfg.WINGS_BOUNDS;
  STATES.put(u, s);
  CASTS = CASTS + 1L;
  if (!bound(s, buf, r, a, now)) { s.fails = 1; FAILS = FAILS + 1L; }
  LAST_WHY = al != null ? "locked on " + (s.aname == null ? "an ally" : s.aname) : "glide";
  if (al != null) @PKG@.ArmoryTrav.tell(pr, "Wings of Fate: carrying you to " + (s.aname == null ? "your ally" : s.aname) + ".");
  return true;
}""")
M(wings, r"""
public static void marker(@REF@ mk, @LPC@ pc, int c, @ST@ st, @CB@ buf) {
  try { buf.removeEntity(mk, @REMR@.REMOVE); } catch (Throwable t0) { }
  MARKS = MARKS + 1L;
  java.util.UUID u = pc.getCreatorUuid();
  @REF@ r = @PKG@.Leap.refOf(buf, u);
  if (u == null || r == null) return;
  cast(u, r, st, buf);
}""")
# TravTick, every tick of every player (world thread): the ends first (world change, death, the ally gone), the arrival, the next bound, the looks
M(wings, r"""
public static void tickPlayer(@REF@ ref, @ST@ st, @CB@ cb) {
  if (STATES.isEmpty() || ref == null || !ref.isValid()) return;
  @PR@ pr = @PKG@.Kunai.prOf(cb, ref);
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  if (u == null) return;
  long now = now();
  if (now - SWEEP_AT > 5000L) { SWEEP_AT = now; sweep(now); }
  @PKG@.WingsState s = (@PKG@.WingsState) STATES.get(u);
  if (s == null) return;
  s.last = now;
  if (s.st != st) { STATES.remove(u, s); ENDS = ENDS + 1L; LAST_END = "world change"; LAST_WHY = "ended (world change)"; return; }
  if (@PKG@.ArmoryTrav.dead(cb, ref)) { STATES.remove(u, s); ENDS = ENDS + 1L; LAST_END = "death"; LAST_WHY = "ended (death)"; return; }
  if (@PKG@.ArmoryTree.gen(u) != s.gen) { STATES.remove(u, s); ENDS = ENDS + 1L; LAST_END = "profile switch"; LAST_WHY = "ended (profile switch)"; return; }          // FIX (review)
  if (!ref.equals(s.ref)) s.ref = ref;
  @VEC@ p = @PKG@.ArmoryTrav.posOf(cb, ref);
  if (p == null) return;
  if (s.ally != null) {
    @VEC@ q = (!s.ally.isValid() || @PKG@.ArmoryTrav.dead(cb, s.ally)) ? null : @PKG@.ArmoryTrav.posOf(cb, s.ally);
    if (q == null) { end(s, cb, ref, "the ally is gone", now); return; }
    double dx = q.x - p.x;
    double dy = q.y - p.y;
    double dz = q.z - p.z;
    double d = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (d <= @PKG@.ArmoryCfg.WINGS_ARRIVE + 1.0E-9) { arrive(s, cb, ref, pr, now); return; }
    if (d > (double) @PKG@.ArmoryCfg.WINGS_RANGE * 2.0 + 8.0) { end(s, cb, ref, "the ally is too far", now); return; }
  }
  if (now >= s.next) {
    if (s.bounds < s.most) {
      double[] la = null;
      if (s.ally == null) la = @PKG@.Leap.aim(cb, ref, u, null);
      if (bound(s, cb, ref, la, now)) s.fails = 0;
      else {          // FIX (review): a bound that cannot be made (no velocity / look) never strands the flight: 5 in a row = the end (+ the refund)
        s.fails = s.fails + 1;
        FAILS = FAILS + 1L;
        if (s.fails >= FAIL_MAX) { end(s, cb, ref, "no bound", now); return; }
      }
    }
    else if (now >= s.next + (s.ally != null ? 1000L : 0L)) { end(s, cb, ref, s.ally != null ? "the ally was not reached" : "glide over", now); return; }
  }
  if (now >= s.fx) { s.fx = now + FX_MS; draw(cb, p, s); }
}""")
M(wings, r"""public static void clear() { STATES.clear(); }""")
'''
rep('''# ---- ArmoryTravSys.onEntityAdded (SPAWN of one of our projectiles)''', WINGS_JAVA + '''# ---- ArmoryTravSys.onEntityAdded (SPAWN of one of our projectiles)''')
rep('''  if (c == @PKG@.ArmoryDefs.RICO_CODE) { @PKG@.Rico.marker(ref, pc, c, st, buf); return; }     // 0.1.14: the wand signature''',
    '''  if (c == @PKG@.ArmoryDefs.RICO_CODE) { @PKG@.Rico.marker(ref, pc, c, st, buf); return; }     // 0.1.14: the wand signature
  if (c == @PKG@.ArmoryDefs.WINGS_CODE) { @PKG@.Wings.marker(ref, pc, c, st, buf); return; }     // 0.1.21: Wings of Fate (Soul Orb / Cage hold)''')
rep('''    try { @PKG@.Soul.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.19: the Soul Orb / Cage Bindings (hold right click)
    catch (Throwable ts) { @PKG@.Soul.warn("tick:" + ts.getClass().getName(), "Soul Binding tick failed (" + ts + ")"); }''',
    '''    try { @PKG@.Soul.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.19: the Soul Orb / Cage Bindings (hold right click)
    catch (Throwable ts) { @PKG@.Soul.warn("tick:" + ts.getClass().getName(), "Soul Binding tick failed (" + ts + ")"); }
    try { @PKG@.Wings.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.21: Wings of Fate (bounds, arrival, the wings)
    catch (Throwable tw) { @PKG@.Wings.warn("tick:" + tw.getClass().getName(), "Wings of Fate tick failed (" + tw + ")"); }''')
rep('''  @PKG@.Soul.clear();          // 0.1.19: every regen block cleared, the armory:soul:<uuid> values go too''',
    '''  @PKG@.Soul.clear();          // 0.1.19: every regen block cleared, the armory:soul:<uuid> values go too
  @PKG@.Wings.clear();          // 0.1.21''')
rep('''  @PKG@.Soul.clear();          // 0.1.19
  @PKG@.SoulDrop.ROLLED.clear();''', '''  @PKG@.Soul.clear();          // 0.1.19
  @PKG@.SoulDrop.ROLLED.clear();
  @PKG@.Wings.clear();          // 0.1.21''')

# ---------------------------------------------------------------------------------------------------------------- FIX (review): migrate021
# A server whose config.properties was first written by 0.1.19 / 0.1.20 has every Soul row spelled out (seed(FILE, DEF_CFG) writes the whole
# default file), so the old tether times + 48 dots would beat the new defaults. ONE-TIME UPDATE (PROJECT-RULES 4, the migrate018 steps): a
# soul.stabilize.<tier> / soul.lineDots line still on its 0.1.20 default becomes the 0.1.21 one; a hand-set value is KEPT + logged; History
# copy first, an Undo-able change-log line per key, a run-once marker, the file's bytes + line endings kept. The 0.1.20 lines 0.1.21 no longer
# reads (soul.damagePerMana, soul.damageMult.*, the Earth / Frost / Storm / Light essence lines) stay untouched in the file: never a WARN for
# them (ArmoryCfg.retired), a hand-set one is named once in the log (its new home). Skyy's live file has no soul.* line: the marker only.
rep("""M18_MARK_ID = 'SkyyArmory 0.1.18 wand launch'
""", """M18_MARK_ID = 'SkyyArmory 0.1.18 wand launch'
M21_MARK_ID = 'SkyyArmory 0.1.21 soul tether'          # 0.1.21 FIX (review): migrate021
M21_MARK = '# SkyyArmory 0.1.21 soul tether (Skyy 2026-10-11: "make it teather a little faster"): Bindings turn solid in 1.75 .. 1.0 s (0.1.20: 2.5 .. 1.5), 64 line dots a draw (0.1.20: 48) - lines still on the old defaults were updated once'
""")
rep('''] + [x for _r in CFG_SOUL for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + SOUL_TAB_LINES + [''',
    '''] + [x for _r in CFG_SOUL for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [M21_MARK] + SOUL_TAB_LINES + [          # 0.1.21: a new file = migrate021 done''')
M21_PY = r'''# 0.1.21 FIX (review): migrate021's keys (the 0.1.20 default -> the 0.1.21 one) + the 0.1.20 lines 0.1.21 no longer reads (their 0.1.20 default)
M21_KEYS = ["soul.stabilize.%s" % _m for _m in SOUL_TIERS] + ["soul.lineDots"]
M21_OLD = ["2.5", "2.3", "2.1", "1.9", "1.7", "1.6", "1.5", "1.5", "48"]
M21_NEW = [bnum(_x) for _x in SOUL_STAB] + [[r_[4] for r_ in CFG_SOUL if r_[0] == "soul.lineDots"][0]]
assert M21_NEW == ["1.75", "1.6", "1.45", "1.35", "1.2", "1.1", "1.05", "1", "64"], M21_NEW
M21_RET = ([("soul.damagePerMana", "2")] + [("soul.damageMult.%s" % _m, _v) for _m, _v in zip(SOUL_TIERS, ["1", "1.1", "1.1", "1.5", "1.5", "2", "2", "2.5"])]
           + [("essence.chance.%s" % _n, _v) for _n, _v in (("Earth", "8"), ("Frost", "8"), ("Storm", "8"), ("Light", "3"))]
           + [("essence.zone.%s" % _n, _v) for _n, _v in (("Earth", "2"), ("Frost", "3"), ("Storm", "4"), ("Light", "4"))])
assert not [k_ for k_, v_ in M21_RET if ("\n%s=" % k_) in CFG_TEXT] and all(("\n%s=" % k_) in CFG_TEXT for k_ in M21_KEYS)
for f in ("public static final String[] M21_KEYS = %s;" % jarr(M21_KEYS), "public static final String[] M21_OLD = %s;" % jarr(M21_OLD),
          "public static final String[] M21_NEW = %s;" % jarr(M21_NEW), "public static final String[] M21_RET_KEYS = %s;" % jarr([k_ for k_, v_ in M21_RET]),
          "public static final String[] M21_RET_OLD = %s;" % jarr([v_ for k_, v_ in M21_RET]),
          "public static final String M21_MARK = %s;" % jstr(M21_MARK), "public static final String M21_MARK_ID = %s;" % jstr(M21_MARK_ID),
          "public static final String M21_WHO = \"SkyyArmory 0.1.21\";", "public static volatile String M21_LAST = \"\";"):
    F(cfg, f)
# a 0.1.20 line 0.1.21 no longer reads: tab() never WARNs about it (a 0.1.19 / 0.1.20 default file has all of them)
M(cfg, r"""
public static boolean retired(String k) {
  if (k == null) return false;
  for (int i = 0; i < M21_RET_KEYS.length; i++) if (M21_RET_KEYS[i].equals(k)) return true;
  return false;
}""")
M(cfg, r"""
public static double[] tab(java.util.Properties p, String prefix, String[] ms, double[] defs, double lo, double hi) {'''
rep('''M(cfg, r"""
public static double[] tab(java.util.Properties p, String prefix, String[] ms, double[] defs, double lo, double hi) {''', M21_PY)
rep('''    if (!known) @PKG@.ArmoryLog.warnOnce("tab:" + k, "config.properties: " + k + " is not a metal of this table - ignored");''',
    '''    if (!known && !retired(k)) @PKG@.ArmoryLog.warnOnce("tab:" + k, "config.properties: " + k + " is not a metal of this table - ignored");          // 0.1.21: never a retired 0.1.20 line''')
M21_JAVA = r'''
# one key's text step = m18Key with the 0.1.21 marker (null = the marker is already there; else { text, change, kept notes, { key, old, new } })
M(cfg, r"""
public static Object[] m21Key(String text, String key, String oldV, String newV, boolean mark) {
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
      if (mark && s.indexOf(M21_MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    if (key.equals(@PKG@.CfgFile.key(s))) {
      if (first < 0) first = k;
      eff = @PKG@.CfgFile.value(l, k).trim();
      multi = e > k;
    }
    k = e + 1;
  }
  boolean mig = eff != null && !multi && m13Is(eff, oldV);
  String chg = "";
  String[] rows = new String[0];
  java.util.ArrayList kept = new java.util.ArrayList();
  if (mig) {
    chg = key + " " + @PKG@.CfgRows.oneLine(eff) + " -> " + newV;
    rows = new String[] { key, eff, newV };
  } else if (eff != null && (multi || !m13Is(eff, newV))) {
    kept.add(key + "=" + @PKG@.CfgRows.oneLine(eff) + " kept (custom) - the 0.1.21 default is " + newV);
  }
  String nl = text.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
  if (first < 0) {
    String out0 = text;
    if (mark) out0 = (text.length() == 0 || text.endsWith("\n")) ? text + M21_MARK + nl : text + nl + M21_MARK;
    return new Object[] { out0, chg, (String[]) kept.toArray(new String[0]), rows };
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (mark && k == first) {
      boolean crm = raw[k].endsWith("\r") || (k == raw.length - 1 && text.indexOf("\r\n") >= 0);
      out.add(M21_MARK + (crm ? "\r" : ""));
    }
    if (mig && e2 == k && key.equals(@PKG@.CfgFile.key(s2)) && m13Is(@PKG@.CfgFile.value(l, k).trim(), oldV)) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + newV + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + M21_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg, (String[]) kept.toArray(new String[0]), rows };
}""")
# the effective value of one key (null = no line)
M(cfg, r"""
public static String m21Val(String text, String key) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  String eff = null;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    if (key.equals(@PKG@.CfgFile.key(s))) eff = @PKG@.CfgFile.value(l, k).trim();
    k = e + 1;
  }
  return eff;
}""")
# all 9 keys in one pass (the marker with the first): { text, "a -> b, c -> d", kept notes, { key, old, new, ... } } or null (ran before); a
# hand-set retired line is named (where its setting lives now) - the line itself stays
M(cfg, r"""
public static Object[] m21Update(String text) {
  String cur = text;
  String chg = "";
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < M21_KEYS.length; i++) {
    Object[] a = m21Key(cur, M21_KEYS[i], M21_OLD[i], M21_NEW[i], i == 0);
    if (a == null) return null;
    cur = (String) a[0];
    String c = (String) a[1];
    if (c.length() > 0) chg = chg.length() > 0 ? chg + ", " + c : c;
    String[] kk = (String[]) a[2];
    for (int j = 0; j < kk.length; j++) kept.add(kk[j]);
    String[] rr = (String[]) a[3];
    for (int j = 0; j < rr.length; j++) rows.add(rr[j]);
  }
  for (int i = 0; i < M21_RET_KEYS.length; i++) {
    String v = m21Val(cur, M21_RET_KEYS[i]);
    if (v == null || m13Is(v, M21_RET_OLD[i])) continue;
    kept.add(M21_RET_KEYS[i] + "=" + @PKG@.CfgRows.oneLine(v) + " is no longer read (custom, left in the file) - 0.1.21: "
      + (M21_RET_KEYS[i].startsWith("soul.") ? "Binding damage is soul.damagePerSecond.<tier>" : "the essences are Life / Fire / Ice / Water / Lightning / Void (Frost = Ice, Storm = Lightning)")
      + "; set it again in Server Setup > Armory > Soul Orb + essences");
  }
  return new Object[] { cur, chg, (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
}""")
M(cfg, r"""
public static String m21Log(String key, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + M21_WHO + "\t-\tupdate\t" + key + "\t" + @PKG@.CfgRows.oneLine(o) + "\t" + n + "\tok";
}""")
M(cfg, r"""
public static synchronized String migrate021() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = m21Update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    m12Kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), M21_WHO, "before the 0.1.21 soul tether update");
    if (!m12Saved(old)) {
      @PKG@.ArmoryLog.warn("config.properties NOT updated to the 0.1.21 soul tether: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    int q = 0;
    while (q + 2 < rows.length) {
      @PKG@.CfgLog.enqueue(m21Log(rows[q], rows[q + 1], rows[q + 2]));
      q = q + 3;
    }
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.1.21 soul tether: " + chg + " (Skyy 2026-10-11: make it teather a little faster; the old file is in config-history; Server Setup -> Changes can undo it)";
    else msg = "config.properties: no soul.stabilize / soul.lineDots line held the 0.1.20 default - nothing changed, the new defaults apply (0.1.21 marker added)";
    @PKG@.ArmoryLog.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { @PKG@.ArmoryLog.info(kept[i]); all.append("; ").append(kept[i]); }
    M21_LAST = all.toString();
    return M21_LAST;
  } catch (Throwable t) {
    @PKG@.ArmoryLog.warn("could not update config.properties to the 0.1.21 soul tether (the file is used as it is): " + t);
    return "";
  }
}""")'''
rep('''    M18_LAST = all.toString();
    return M18_LAST;
  } catch (Throwable t) {
    @PKG@.ArmoryLog.warn("could not update config.properties to the 0.1.18 wand launch (the file is used as it is): " + t);
    return "";
  }
}""")''', '''    M18_LAST = all.toString();
    return M18_LAST;
  } catch (Throwable t) {
    @PKG@.ArmoryLog.warn("could not update config.properties to the 0.1.18 wand launch (the file is used as it is): " + t);
    return "";
  }
}""")''' + M21_JAVA)
rep('''  String m18 = @PKG@.ArmoryCfg.migrate018();          // 0.1.18: hop.hangSeconds 0.35 -> 0 ONCE (same rules) - no slow, just the launch''',
    '''  String m18 = @PKG@.ArmoryCfg.migrate018();          // 0.1.18: hop.hangSeconds 0.35 -> 0 ONCE (same rules) - no slow, just the launch
  String m21 = @PKG@.ArmoryCfg.migrate021();          // 0.1.21 FIX (review): soul.stabilize.<tier> 2.5 .. 1.5 -> 1.75 .. 1.0 + soul.lineDots 48 -> 64 ONCE (same rules)''')
rep('''    + (@PKG@.ArmoryTrav.fn(@PKG@.Soul.REGEN_FN) != null ? "found" : "not loaded yet - read at use time; without SkyySkills 0.4.30 Mana regenerates while bound") + ")");''',
    '''    + (@PKG@.ArmoryTrav.fn(@PKG@.Soul.REGEN_FN) != null ? "found" : "not loaded yet - read at use time; without SkyySkills 0.4.30 Mana regenerates while bound") + ")"
    + (m21.length() > 0 ? "; " + m21 : ""));          // 0.1.21: migrate021''')

# ---------------------------------------------------------------------------------------------------------------- the jar checks + manifest + prints
rep('''        "0.1.19: the %d Soul files (10 items: 8 soul weapons + 2 essences; no vanilla essence overridden)" % len(SOUL_FILES)''',
    '''        "0.1.19: the %d Soul files (10 items: 8 soul weapons + 2 essences; no vanilla essence overridden)" % len(SOUL_FILES)
    assert sorted(n for n in _names if n in set(W21_FILES)) == W21_FILES and len([n for n in _names if "/SkyyArmory_SoulWisp_" in n]) == 16 \\
        and len([n for n in _names if "/SkyyArmory_Soul_Wings" in n]) == 5, "0.1.21: the %d wisp / wings files" % len(W21_FILES)''')
rep('''"Priest Soul Orb + 7 Soul Cages: hold right click to bind nearby enemies (steady damage for steady Mana, stored as healing); "''',
    '''"Priest Soul Orb + 7 Soul Cages: hold right click to bind nearby enemies (steady damage for steady Mana, stored as healing), "
                 "hold left click for Wings of Fate (glide, or fly to an ally and heal them); "''')
rep('''print("0.1.20 wand fall: a wand launch made while falling''', '''print("0.1.21 soul orb round: damage a second %s, solid after %s s, recipes %s; essence drops %s; lines: solid %s / wispy %s blocks apart, "
      "budget %s dots; Wings of Fate %d rows, marker %s (code %d), classes WingsState + Wings" % (
          "/".join(bnum(x_) for x_ in SOUL_DPS), "/".join(bnum(x_) for x_ in SOUL_STAB),
          "; ".join("%s <- %s" % (SOUL_IDS[t_], " + ".join("%d %s" % (x_["Quantity"], x_["ItemId"]) for x_ in r_["Input"])) for t_, r_ in enumerate(SOUL_RECIPES)),
          ", ".join("%s %s%% %s" % (n_, bnum(p_), "volcanic" if z_ == 0 else "Z%d" % z_) for n_, p_, z_ in zip(ESS_NAMES, ESS_PCT, ESS_ZONE)), 0.45, 1.8,
          [r_[4] for r_ in CFG_SOUL if r_[0] == "soul.lineDots"][0], len(CFG_WINGS), WINGS_MARK, WINGS_CODE))
print("0.1.20 wand fall: a wand launch made while falling''')

assert "SOUL_MULT" not in s.replace("SOUL_MULT_PLACEHOLDER", ""), [l_ for l_ in s.split(LF) if "SOUL_MULT" in l_][:6]
assert "SOUL_DPM" not in s, [l_ for l_ in s.split(LF) if "SOUL_DPM" in l_][:6]
assert "SOUL_ESS[" not in s and "Ingredient_Crystal_Blue\", \"Quantity\"" not in s

with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(s.replace(LF, NL))
print("wrote %s" % os.path.relpath(DST, ROOT))

if os.environ.get("ARMORY0121_BUILD_ONLY"):
    raise SystemExit(0)
# ================================================================================================================ the harness
traw = open(TSRC, encoding="utf8", newline="").read()
TNL = CR + LF if (CR + LF) in traw else LF
ts = traw.replace(CR + LF, LF)


def hrep(old, new, count=1):
    global ts
    n = ts.count(old)
    assert n == count, "harness anchor count %d (want %d): %s" % (n, count, old[:140])
    ts = ts.replace(old, new)


hrep('"""SkyyArmory 0.1.20 - test harness. GENERATED by tools/armory_0_1_20_patch.py from test_skyyarmory_0.1.19.py - edit the patch, never this file.',
     '''"""SkyyArmory 0.1.21 - test harness. GENERATED by tools/armory_0_1_21_patch.py from test_skyyarmory_0.1.20.py - edit the patch, never this file.
Run: python SkyyArmory/test_skyyarmory_0.1.21.py --dir tools/dev/scratch/<task>/harness   (--no-set skips the one-JVM SET run, --keep keeps it)
Every 0.1.20 check still runs on the 0.1.20 shape: JZ21 = the real 0.1.21 jar; JZ = the jar AS THE 0.1.20 CHECKS KNOW IT - the 23 new files
(8 wispy + 1 wing particle systems with their spawners, the Wings root / Charging / tap / launch, the marker) hidden, the changed files (the 8
Soul items, the 2 old essences, the 8 solid-line spawners, the lang) read as the 0.1.20 jar's bytes, the manifest description the 0.1.20 one
(P23 proves the real files are exactly the planned change). The classes are the real 0.1.21 ones: the old Soul checks run with the 0.1.20
NUMBERS pinned (Soul pin20: damage a second 2 / 2.31 / 2.42 / 3.45 / 3.6 / 5 / 5.2 / 6.75 = the old 2 x Mana/s x multiple, solid after
2.5 .. 1.5 s, 48 line dots) - the new defaults are R24's; the checks of things that changed ON PURPOSE (the line look, the rows / tables /
essence drops, the class count, the method compares) now expect the 0.1.21 shape.
NEW P23 (Python) + R24 (JVM, after R23) EXECUTE every 0.1.21 path:
  P23  vs the 0.1.20 jar: exactly the planned new + changed files; the recipes (Soul Orb 25 Life, no crystal; the vanilla essence ladder;
       SkyyGear 0.2.22's GearUp.fromRecipe rule finds all 7 cage steps); the Wings root / Charging / marker; the wisp / solid / wing looks
  R24  a: the rows + tables + defaults + clamps; b: damage a second per tier through the REAL pulse (every tier, 1 Binding, 2 s); c: the
       tether timing per tier (wispy just before, solid at the new time); d: the line look per state (wispy sparse + faint system +
       flicker moving, solid dense + bright system, the budget shared out, never above it); e: the essence drops (new zones, Earth / Light
       never); f: WINGS OF FATE through the real marker chain - no ally (3 bounds, ONE velocity write each, none in between), ally lock
       (party member / any player / a stranger refused in a party / out of the cone / behind a wall), carried + arrival heal amounts
       (base + ALL stored, the pool emptied, the cap), a damaging fall KEPT, the class lock / no Mana / dead ally / no move refund; g: vs
       the 0.1.20 jar method by method.

0.1.20 harness: SkyyArmory 0.1.20 - test harness. GENERATED by tools/armory_0_1_20_patch.py from test_skyyarmory_0.1.19.py - edit the patch, never this file.''')
hrep('VERSION = "0.1.20"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.20 SkyyArmory"',
     'VERSION = "0.1.21"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.21 SkyyArmory"')
hrep('os.path.join(SCRATCH_ROOT, "armory0120", "harness")', 'os.path.join(SCRATCH_ROOT, "armory0121", "harness")')
hrep('raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.20.py', 'raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.21.py')
hrep('Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.20"))', 'Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.21"))')
for _v in ('"[SkyyArmory] 0.1.20 ready" in m_', '"0.1.20 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_',
           '"0.1.20 crossbow grapple: grapple on" in m_',
           '"0.1.20 monk moves on - Pole-Vault (Bo hold): lunge 3 in 0.2 s, 4.5 up x 7 forward (push x2.1)" in m_',
           '"0.1.20 wand signature on - the signature key when the meter is full (20; quick-shot hit +1, charged hit +2)" in m_',
           '"0.1.20 soul Bindings on - hold right click: bind every enemy within 3 blocks of where you look" in m_',
           'come from Skyy:0.1.20 SkyyArmory" in str(r[1])'):
    hrep(_v, _v.replace("0.1.20", "0.1.21"))
hrep('t_.replace("0.1.20", "V").replace("0.1.19", "V")', 't_.replace("0.1.21", "V").replace("0.1.20", "V").replace("0.1.19", "V")')
# ---- the 0.1.20 view of the jar (the Z118 pattern)
hrep('''JZ = zipfile.ZipFile(JAR)
# 0.1.19: JZ19 = the real 0.1.19 jar''', '''JZ = zipfile.ZipFile(JAR)
# 0.1.21: JZ21 = the real 0.1.21 jar (P23 / R24); from here on JZ is the jar AS THE 0.1.20 CHECKS KNOW IT: the new files hidden, the changed
# ones read as the 0.1.20 jar's bytes, the manifest = the real one with the 0.1.20 description; the classes stay real (A / X verify them)
# except the 2 new Wings classes, hidden from the old class lists (R24 loads them under -Xverify:all and runs the access audit on them)
JZ21 = JZ
OLD120 = os.path.join(HERE, "SkyyArmory-0.1.20.jar")
if not os.path.isfile(OLD120):
    raise SystemExit("the 0.1.21 harness needs SkyyArmory-0.1.20.jar (the base, the SET pin) next to it: %s" % OLD120)
OZ120 = zipfile.ZipFile(OLD120)
W21_NEW = sorted(n_ for n_ in JZ21.namelist() if n_ not in set(OZ120.namelist()) and not n_.endswith(".class"))
W21_CHANGED = sorted(n_ for n_ in JZ21.namelist() if n_ in set(OZ120.namelist()) and not n_.endswith(".class") and n_ != "manifest.json"
                     and JZ21.read(n_) != OZ120.read(n_))
W21_CLS = ["com/skyy/armory/Wings.class", "com/skyy/armory/WingsState.class"]


class Z120(object):
    """the 0.1.21 jar as the 0.1.20 checks know it (read only)"""
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


JZ = Z120(JZ21, OZ120, W21_NEW + W21_CLS, W21_CHANGED)          # the 2 Wings classes too: R24 loads / verifies / audits them itself
# 0.1.19: JZ19 = the real 0.1.19 jar''')
# ---- the old R22 checks run with the 0.1.20 NUMBERS pinned (pin20): the classes are 0.1.21's, the defaults R24's
hrep('''    def setup22(item=IRON22, mana=200.0, walls=()):''', '''    PIN20_DPS = [2.0 * m_ * x_ for m_, x_ in zip([1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35], [1.0, 1.1, 1.1, 1.5, 1.5, 2.0, 2.0, 2.5])]
    PIN20_STAB = [2.5, 2.3, 2.1, 1.9, 1.7, 1.6, 1.5, 1.5]

    def pin20():          # 0.1.21: the 0.1.20 numbers (2 x Mana/s x multiple; 2.5 .. 1.5 s; 48 dots) for the old checks
        ACfg.SOUL_DPS = JArray(JDouble)(PIN20_DPS)
        ACfg.SOUL_STAB = JArray(JDouble)(PIN20_STAB)
        ACfg.SOUL_DOTS = 48

    def setup22(item=IRON22, mana=200.0, walls=()):''')
hrep('''        SO.HELD = HELD22
        ACfg.useDefaults()
        ACfg.TRAV_FX = True''', '''        SO.HELD = HELD22
        ACfg.useDefaults()
        pin20()
        ACfg.TRAV_FX = True''')

# ---- L: the 0.1.21 Wings interactions / root / marker (the real files) go into the stores too - the pack check counts them
hrep('''    check(not bad19l and n19l == 13, "L (0.1.19): the 2 Soul interactions, the root and the 10 items (8 Soul weapons + 2 essences) decode (no unknown key, "
                                     "no failed validation) and go into the stores: %d %s" % (n19l, bad19l[:3]))''',
     '''    check(not bad19l and n19l == 13, "L (0.1.19): the 2 Soul interactions, the root and the 10 items (8 Soul weapons + 2 essences) decode (no unknown key, "
                                     "no failed validation) and go into the stores: %d %s" % (n19l, bad19l[:3]))
    bad21l, n21l = [], 0          # 0.1.21: the Wings Charging / tap / launch, its root and the marker (the REAL files) into the stores
    for c_, pre_ in ((INTc, "Server/Item/Interactions/"), (ROOTc, "Server/Item/RootInteractions/"), (PRJc, "Server/Projectiles/")):
        objs_ = []
        for n_ in W21_NEW:
            if n_.startswith(pre_) and n_.endswith(".json"):
                o_, w_, ei_ = dec17(c_, os.path.basename(n_)[:-5], JZ21.read(n_).decode("utf-8"))
                if o_ is None or w_:
                    bad21l.append("%s: %s" % (n_, w_))
                else:
                    objs_.append(o_)
                    n21l += 1
        load(c_, objs_, PACK)
    check(not bad21l and n21l == 5, "L (0.1.21): the Wings Charging + tap + launch, the Wings root and the marker decode (no unknown key, no failed "
                                    "validation) and go into the stores: %d %s" % (n21l, bad21l[:3]))''')
hrep('''"64 of 64 items, 360 of 360 interactions, 66 of 66 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.21 SkyyArmory"''',
     '''"64 of 64 items, 363 of 363 interactions, 67 of 67 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.21 SkyyArmory"''')
# ---- K: the rows (soul.damagePerMana gone, the 16 wings.* rows, the damagePerSecond table)
hrep('''    NEW_ROWS += ["soul.enabled", "soul.damagePerMana", "soul.tick", "soul.lockRadius", "soul.lockRange", "soul.snapRange", "soul.aimCone",
                 "soul.wispyGrace", "soul.storePercent", "soul.decayPercent", "soul.noRegen", "soul.lineDots", "essence.drops"]      # 0.1.19 the Soul Orb''',
     '''    NEW_ROWS += ["soul.enabled", "soul.tick", "soul.lockRadius", "soul.lockRange", "soul.snapRange", "soul.aimCone",
                 "soul.wispyGrace", "soul.storePercent", "soul.decayPercent", "soul.noRegen", "soul.lineDots", "essence.drops"]      # 0.1.19 the Soul Orb (0.1.21: - soul.damagePerMana)
    NEW_ROWS += ["wings." + k_ for k_ in ("enabled", "mana", "stamina", "speed", "boundSeconds", "bounds", "allyBounds", "allySpeed", "lift",
                                          "lockRange", "lockCone", "arrive", "baseHeal", "tierHeal", "healCap", "anyPlayer")]      # 0.1.21 Wings of Fate''')
hrep('''    TAB16 += ["soul.bindings", "soul.manaPerSecond", "soul.damageMult", "soul.stabilize", "soul.storeCap", "essence.chance", "essence.zone"]      # 0.1.19''',
     '''    TAB16 += ["soul.bindings", "soul.manaPerSecond", "soul.damagePerSecond", "soul.stabilize", "soul.storeCap", "essence.chance", "essence.zone"]      # 0.1.19 (0.1.21: damageMult -> damagePerSecond)''')
# ---- T: the start line carries the 0.1.21 defaults
hrep('''"solid after 2.5 / 2.3 / 2.1 / 1.9 / 1.7 / 1.6 / 1.5 / 1.5 s" in soul_line[0]
          and "50% stored as healing, Mana regen blocked while bound" in soul_line[0] and "Life 8% Z1, Fire 10% volcanic caves, Earth 8% Z2" in soul_line[0]''',
     '''"solid after 1.75 / 1.6 / 1.45 / 1.35 / 1.2 / 1.1 / 1.05 / 1 s" in soul_line[0]
          and "50% stored as healing, Mana regen blocked while bound" in soul_line[0] and "Life 8% Z1, Fire 10% volcanic caves, Ice 8% Z3, Water 8% Z2" in soul_line[0]
          and "for 5 / 7 / 10 / 15 / 20 / 30 / 40 / 55 damage/s (before levels)" in soul_line[0] and "Wings of Fate on (hold left click: 20 Mana + 10 Stamina" in soul_line[0]''')
# ---- R4 / R10d: TravTick now ticks 7 (0.1.21: + Wings.tickPlayer)
hrep('''    check(tt4.count("tickPlayer") == 6 and "onBowShot" in gb4,''', '''    check(tt4.count("tickPlayer") == 7 and "onBowShot" in gb4,''')          # 0.1.21: + Wings
hrep('''tt10.count("tickPlayer") == 6 and "fallSafe" in gf10''', '''tt10.count("tickPlayer") == 7 and "fallSafe" in gf10''')
# ---- R22a: the 0.1.21 rows / tables / defaults (soul.damagePerMana gone, damagePerSecond, the faster tether, 64 dots, the vanilla essences)
hrep('''    want22 = {"soul.enabled": "true", "soul.damagePerMana": "2", "soul.tick": "0.5",''', '''    want22 = {"soul.enabled": "true", "soul.tick": "0.5",''')
hrep('''              "soul.noRegen": "true", "soul.lineDots": "48", "essence.drops": "true"}''', '''              "soul.noRegen": "true", "soul.lineDots": "64", "essence.drops": "true"}          # 0.1.21: 64 dots, no damagePerMana''')
hrep('''             "soul.damageMult": [1, 1.1, 1.1, 1.5, 1.5, 2, 2, 2.5], "soul.stabilize": [2.5, 2.3, 2.1, 1.9, 1.7, 1.6, 1.5, 1.5],''',
     '''             "soul.damagePerSecond": [5, 7, 10, 15, 20, 30, 40, 55], "soul.stabilize": [1.75, 1.6, 1.45, 1.35, 1.2, 1.1, 1.05, 1],''')
hrep('''    ETAB22 = {"essence.chance": [8, 10, 8, 8, 8, 5, 3], "essence.zone": [1, 0, 2, 3, 4, 4, 4]}
    ENAMES22 = ["Life", "Fire", "Earth", "Frost", "Storm", "Void", "Light"]''',
     '''    ETAB22 = {"essence.chance": [8, 10, 8, 8, 8, 5], "essence.zone": [1, 0, 3, 2, 4, 4]}          # 0.1.21: the vanilla ladder
    ENAMES22 = ["Life", "Fire", "Ice", "Water", "Lightning", "Void"]''')
hrep('''    ld22 = ([float(x_) for x_ in ACfg.SOUL_NT], [float(x_) for x_ in ACfg.SOUL_MPS], [float(x_) for x_ in ACfg.SOUL_MULT], [float(x_) for x_ in ACfg.SOUL_STAB],''',
     '''    ld22 = ([float(x_) for x_ in ACfg.SOUL_NT], [float(x_) for x_ in ACfg.SOUL_MPS], [float(x_) for x_ in ACfg.SOUL_DPS], [float(x_) for x_ in ACfg.SOUL_STAB],''')
hrep('''    for k_, v_ in (("soul.lockRadius", "99"), ("soul.tick", "0"), ("soul.bindings.Onyxium", "99"), ("soul.storePercent", "-5"), ("essence.chance.Light", "500"),''',
     '''    for k_, v_ in (("soul.lockRadius", "99"), ("soul.tick", "0"), ("soul.bindings.Onyxium", "99"), ("soul.storePercent", "-5"), ("essence.chance.Void", "500"),''')
hrep('''    cl22 = (float(ACfg.SOUL_RADIUS), float(ACfg.SOUL_TICK), float(ACfg.SOUL_NT[7]), int(ACfg.SOUL_STORE), float(ACfg.ESS_PCT[6]), float(ACfg.ESS_ZONE[5]))''',
     '''    cl22 = (float(ACfg.SOUL_RADIUS), float(ACfg.SOUL_TICK), float(ACfg.SOUL_NT[7]), int(ACfg.SOUL_STORE), float(ACfg.ESS_PCT[5]), float(ACfg.ESS_ZONE[5]))''')
hrep('''            hk22.checkEssence("essence.chance[Light]", "3") is None, hk22.checkEssence("essence.chance[Wind]", "3") is not None)''',
     '''            hk22.checkEssence("essence.chance[Water]", "3") is None, hk22.checkEssence("essence.chance[Light]", "3") is not None)          # 0.1.21: Light gone''')
hrep('''    check(not fl22 and ld22 == ([1.0, 2.0, 4.0, 6.0, 10.0, 14.0, 16.0, 20.0], [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35], [1.0, 1.1, 1.1, 1.5, 1.5, 2.0, 2.0, 2.5],
                                  [2.5, 2.3, 2.1, 1.9, 1.7, 1.6, 1.5, 1.5], [10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 55.0, 60.0], [8.0, 10.0, 8.0, 8.0, 8.0, 5.0, 3.0],
                                  [1.0, 0.0, 2.0, 3.0, 4.0, 4.0, 4.0])''',
     '''    check(not fl22 and ld22 == ([1.0, 2.0, 4.0, 6.0, 10.0, 14.0, 16.0, 20.0], [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35], [5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 40.0, 55.0],
                                  [1.75, 1.6, 1.45, 1.35, 1.2, 1.1, 1.05, 1.0], [10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 55.0, 60.0], [8.0, 10.0, 8.0, 8.0, 8.0, 5.0],
                                  [1.0, 0.0, 3.0, 2.0, 4.0, 4.0])          # 0.1.21''')
hrep('''          "R22a: the 13 Soul rows + 7 tables''', '''          "R22a (0.1.21 shape): the 12 Soul rows (+ 16 wings.*, R24) + 7 tables''')
# ---- R22b: damage a second = the tier's soul.damagePerSecond (0.1.21 defaults here: R22a ended on useDefaults)
hrep('''            [round(float(SO.dps(2.0, m_, x_)), 4) for m_, x_ in zip(TAB22["soul.manaPerSecond"], TAB22["soul.damageMult"])],''',
     '''            [round(float(SO.dps(t_)), 4) for t_ in range(-1, 9)],          # 0.1.21: soul.damagePerSecond.<tier>''')
hrep('''    check(pm22 == ([0, 1, 2, 3, 4, 5, 6, 7, -1, -1], [0, 1, 2, 4, 6, 10, 14, 16, 20, 0], [2.0, 2.31, 2.42, 3.45, 3.6, 5.0, 5.2, 6.75], 2.2,''',
     '''    check(pm22 == ([0, 1, 2, 3, 4, 5, 6, 7, -1, -1], [0, 1, 2, 4, 6, 10, 14, 16, 20, 0], [0.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 40.0, 55.0, 0.0], 2.2,''')
hrep('''cap (1 / 2 / 4 / 6 / 10 / 14 / 16 / 20), damage a second per Binding = 2 x "
          "Mana/s x tier multiple (Orb 2.0 .. Onyxium 6.75)''', '''cap (1 / 2 / 4 / 6 / 10 / 14 / 16 / 20), damage a second per Binding = "
          "soul.damagePerSecond (0.1.21: Orb 5 .. Onyxium 55; no tier = 0)''')
# ---- R22l: the vanilla essence ladder (Water Z2, Ice Z3, Lightning + Void Z4; Earth / Light never)
hrep('''    ACfg.ESS_ZONE = JArray(JDouble)([1.0, 0.0, 2.0, 3.0, 4.0, 6.0, 6.0])          # an admin moves Void + Light to a later zone
    es22["Void + Light moved to Zone 6"] = (dead22(4614, "Env_Zone4_Wastes")[:2], dead22(4615, "Env_Zone6_Future")[:2])''',
     '''    ACfg.ESS_ZONE = JArray(JDouble)([1.0, 0.0, 3.0, 2.0, 4.0, 6.0])          # an admin moves Void to a later zone (0.1.21: Light is gone)
    es22["Void moved to Zone 6"] = (dead22(4614, "Env_Zone4_Wastes")[:2], dead22(4615, "Env_Zone6_Future")[:2])''')
hrep('''    check(es22["Zone 1"] == (1, [["Ingredient_Life_Essence"]]) and es22["Zone 2"] == (1, [["SkyyArmory_Essence_Earth"]])
          and es22["Zone 3"] == (1, [["Ingredient_Ice_Essence"]])
          and es22["Zone 4"] == (3, [["Ingredient_Lightning_Essence", "Ingredient_Void_Essence", "SkyyArmory_Essence_Light"]])
          and es22["volcanic Zone 2 cave"] == (2, [["Ingredient_Fire_Essence", "SkyyArmory_Essence_Earth"]])
          and es22["no env, SkyyMobs Lv 25"] == (1, [["SkyyArmory_Essence_Earth"]]) and es22["no env, no level"][:2] == (0, [])''',
     '''    check(es22["Zone 1"] == (1, [["Ingredient_Life_Essence"]]) and es22["Zone 2"] == (1, [["Ingredient_Water_Essence"]])
          and es22["Zone 3"] == (1, [["Ingredient_Ice_Essence"]])
          and es22["Zone 4"] == (2, [["Ingredient_Lightning_Essence", "Ingredient_Void_Essence"]])
          and es22["volcanic Zone 2 cave"] == (2, [["Ingredient_Fire_Essence", "Ingredient_Water_Essence"]])
          and es22["no env, SkyyMobs Lv 25"] == (1, [["Ingredient_Water_Essence"]]) and es22["no env, no level"][:2] == (0, [])''')
hrep('''          and es22["Void + Light moved to Zone 6"] == ((1, [["Ingredient_Lightning_Essence"]]), (2, [["Ingredient_Void_Essence", "SkyyArmory_Essence_Light"]])),
          "R22l (Skyy: 'each drops from mobs of the matching zone'): a player's kill rolls its zone's essence - Zone 1 Life, Zone 2 Earth (new), Zone 3 "
          "Frost (the vanilla Ice Essence), Zone 4 Storm (Lightning) + Void + Light (no later zone yet: the nearest one), a volcanic cave adds Fire; "''',
     '''          and es22["Void moved to Zone 6"] == ((1, [["Ingredient_Lightning_Essence"]]), (1, [["Ingredient_Void_Essence"]])),
          "R22l (0.1.21, Skyy 'follow the vanillas essence progression'): a player's kill rolls its zone's essence - Zone 1 Life, Zone 2 Water, Zone 3 "
          "Ice, Zone 4 Lightning + Void (no later zone yet), a volcanic cave adds Fire; our Earth / Light never; "''')
hrep('''mob's kill, a Creative killer, essence.drops off = nothing; essence.zone moves Void + Light to a later zone''',
     '''mob's kill, a Creative killer, essence.drops off = nothing; essence.zone moves Void to a later zone''')
# ---- R22p FIX 5: the tooltip rows (0.1.21: damagePerSecond instead of damagePerMana / damageMult)
hrep('''    check(all("Tooltips show defaults." in hl22.get(k_, "") for k_ in ("soul.damagePerMana", "soul.bindings", "soul.manaPerSecond", "soul.damageMult", "soul.stabilize")),
          "R22p FIX 5 (critic: tooltips bake the numbers): the 5 rows the tooltip numbers come from say so: %s" % [hl22.get(k_, "")[-40:] for k_ in ("soul.damagePerMana", "soul.bindings")])''',
     '''    check(all("Tooltips show defaults." in hl22.get(k_, "") for k_ in ("soul.damagePerSecond", "soul.bindings", "soul.manaPerSecond", "soul.stabilize")),
          "R22p FIX 5 (critic: tooltips bake the numbers): the 4 rows the tooltip numbers come from say so (0.1.21: damagePerSecond): %s" % [hl22.get(k_, "")[-40:] for k_ in ("soul.damagePerSecond", "soul.bindings")])''')
# ---- R23e / R23f: history (0.1.19 -> 0.1.20 = the 0.1.20 jar); the help text is 0.1.21's
hrep('''    MN23, MO23 = methods_of(JAR), methods_of(OLD119)''', '''    MN23, MO23 = methods_of(OLD120), methods_of(OLD119)          # 0.1.21: R23e = the 0.1.20 round's compare (history); R24g = 0.1.20 -> 0.1.21''')
hrep('''          and "Caps the launch's up part (look down = up). Full in the air; a damaging fall is kept. 0 = no cap.".encode("utf-8") in cls23''',
     '''          and H21_HELP_LIT.encode("utf-8") in cls23 and b"Full in the air; a damaging fall" not in cls23          # 0.1.21: the LOW reword''')
ts = ts.replace("H21_HELP_LIT", repr(H21_HELP))
# ---- R22c / R22e: the 0.1.21 line look (wispy = the SoulWisp system, sparse 1.8 + flicker; solid = dense 0.45); the budget pinned at 48
hrep('''        caps22[i_] = (nb22(), len(set(e_[0] for e_ in hits22())), len([p_ for p_ in list(AT.PSEEN) if str(p_).startswith("SkyyArmory_Soul_")]))''',
     '''        caps22[i_] = (nb22(), len(set(e_[0] for e_ in hits22())), len([p_ for p_ in list(AT.PSEEN) if str(p_).startswith("SkyyArmory_Soul")]))          # 0.1.21: + SoulWisp''')
hrep('''    fx_w = len([p_ for p_ in list(AT.PSEEN) if str(p_) == "SkyyArmory_Soul_Iron"])''',
     '''    fx_w = len([p_ for p_ in list(AT.PSEEN) if str(p_) == "SkyyArmory_SoulWisp_Iron"])          # 0.1.21: the faint wispy system''')
hrep('''    check(fx_w == 6 and fx_s == 3 * 15 and not oth_,
          "R22e: the Binding line - the first (wispy) line = 6 sparse dots of SkyyArmory_Soul_Iron, a solid Binding = 15 dense dots, a line every 250 ms "''',
     '''    check(fx_w == 4 and fx_s == 3 * 20 and not oth_,
          "R22e (0.1.21 look): the Binding line - the first (wispy) line = 5 sparse dots (1.8 apart) of SkyyArmory_SoulWisp_Iron, one flickered out "
          "= 4, a solid Binding = 20 dense dots (0.45 apart) of SkyyArmory_Soul_Iron, a line every 250 ms "''')
hrep('''        dps_ = 2.0 * mps_ * TAB22["soul.damageMult"][t_]''', '''        dps_ = TAB22["soul.damagePerSecond"][t_]          # 0.1.21: the table itself''')

# ---- FIX (review): R22c's first-draw budget (48 pinned) - the 20 forming Onyxium lines are WISPY = held to 1 dot each (Soul.share) = 20
hrep('''    check(all(0 < v_[2] <= 48 for v_ in caps22.values()) and caps22[SOUL19_IDS[7]][2] == 40,
          "R22c: the line-draw budget - all of a player's Binding lines together at most 48 dots a draw (20 Onyxium lines = 2 dots each = 40): %s"''',
     '''    check(all(0 < v_[2] <= 48 for v_ in caps22.values()) and caps22[SOUL19_IDS[7]][2] == 20,
          "R22c (0.1.21 FIX share): the line-draw budget - all of a player's Binding lines together at most 48 dots a draw (20 forming Onyxium lines = wispy, held to 1 dot each = 20): %s"''')
# ---- FIX (review): T - the live copy also gets migrate021 (Skyy's file has no soul.* line = the marker only)
hrep('''        r18_ = ACfg.m18Update(t17_)          # 0.1.18: + hop.hangSeconds 0.35 -> 0
        want_ = (str(r18_[0]) if r18_ is not None else t17_).encode("latin-1")''',
     '''        r18_ = ACfg.m18Update(t17_)          # 0.1.18: + hop.hangSeconds 0.35 -> 0
        t18_ = str(r18_[0]) if r18_ is not None else t17_
        r21_ = ACfg.m21Update(t18_)          # 0.1.21 FIX (review): + soul.stabilize / soul.lineDots (the live file: the marker only)
        want_ = (str(r21_[0]) if r21_ is not None else t18_).encode("latin-1")''')
hrep('''and str(ACfg.M17_MARK_ID) in txt1_ and str(ACfg.M18_MARK_ID) in txt1_,''',
     '''and str(ACfg.M17_MARK_ID) in txt1_ and str(ACfg.M18_MARK_ID) in txt1_ and str(ACfg.M21_MARK_ID) in txt1_,''')

# ---- P23 (Python): the real 0.1.21 files vs the 0.1.20 jar = exactly the planned change
P23 = r'''
# ================================================================================================================ P23. 0.1.21 the Soul Orb round (pure files)
_SID23 = ["Weapon_Wand_SoulOrb"] + ["Weapon_Wand_SoulCage_%s" % m_ for m_ in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")]
_T23 = ["Orb", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
_P23 = "Server/Particles/SkyyArmory/"
_WANT_NEW23 = sorted(["%sSkyyArmory_SoulWisp_%s.particlesystem" % (_P23, t_) for t_ in _T23]
                     + ["%sSpawners/SkyyArmory_SoulWisp_%s_Dust.particlespawner" % (_P23, t_) for t_ in _T23]
                     + [_P23 + "SkyyArmory_Wings_Blue.particlesystem", _P23 + "Spawners/SkyyArmory_Wings_Glow.particlespawner"]
                     + ["Server/Item/Interactions/Weapons/Wand/SkyyArmory/SkyyArmory_Soul_Wings_%s.json" % k_ for k_ in ("Charge", "Tap", "Launch")]
                     + ["Server/Item/RootInteractions/Weapons/Wand/SkyyArmory/SkyyArmory_Soul_Wings.json",
                        "Server/Projectiles/Player/SkyyArmory/SkyyArmory_Soul_Wings_Mark.json"])
_ITEM23 = dict((i_, "Server/Item/Items/Weapon/Wand/%s.json" % i_) for i_ in _SID23)
_ART23 = sorted(["Common/Items/Weapons/SoulCage/SkyyArmory_%s_Texture.png" % m_ for m_ in ("Thorium", "Cobalt", "Onyxium")]
                + ["Common/Icons/ItemsGenerated/SkyyArmory_SoulCage_%s.png" % m_ for m_ in ("Thorium", "Cobalt", "Onyxium")])
_SOLID23 = sorted("%sSpawners/SkyyArmory_Soul_%s_%s_Blue.particlespawner" % (_P23, t_, k_) for t_ in _T23 for k_ in ("Dust", "Sparks"))
_WANT_CH23 = sorted(list(_ITEM23.values()) + _ART23 + _SOLID23 + ["Server/Languages/en-US/server.lang"])
_c23n = sorted(n_ for n_ in JZ21.namelist() if n_.endswith(".class"))
_c23o = sorted(n_ for n_ in OZ120.namelist() if n_.endswith(".class"))
_gone23 = sorted(set(OZ120.namelist()) - set(JZ21.namelist()))
check(W21_NEW == _WANT_NEW23 and W21_CHANGED == _WANT_CH23 and not _gone23 and sorted(set(_c23n) - set(_c23o)) == sorted(W21_CLS) and set(_c23o) <= set(_c23n),
      "P23: vs SkyyArmory-0.1.20.jar - new = exactly the 23 planned files (8 wispy dot systems + spawners, the wing dot + spawner, the Wings "
      "Charging / tap / launch + root + marker) + Wings / WingsState, none gone; changed = the 8 Soul items, the 3 recoloured cages' texture + "
      "icon, the 16 solid-line spawners, the lang: new %s | changed %s | gone %s" % (sorted(set(W21_NEW) ^ set(_WANT_NEW23)), sorted(set(W21_CHANGED) ^ set(_WANT_CH23)), _gone23))
_it23 = dict((i_, json.loads(JZ21.read(p_).decode("utf-8"))) for i_, p_ in _ITEM23.items())
_io23 = dict((i_, json.loads(OZ120.read(p_).decode("utf-8"))) for i_, p_ in _ITEM23.items())
_rc23 = dict((i_, [(x_["ItemId"], x_["Quantity"]) for x_ in d_["Recipe"]["Input"]]) for i_, d_ in _it23.items())
_ESS23 = ["Ingredient_Life_Essence", "Ingredient_Life_Essence", "Ingredient_Fire_Essence", "Ingredient_Ice_Essence", "Ingredient_Water_Essence",
          "Ingredient_Lightning_Essence", "Ingredient_Void_Essence", "Ingredient_Life_Essence_Concentrated"]
_QTY23 = [25, 15, 15, 15, 12, 12, 10, 1]          # FIX (review): Onyxium 1 Concentrated Life (= 100 Life)
_bad23 = []
if _rc23[_SID23[0]] != [("Ingredient_Life_Essence", 25), ("Ingredient_Stick", 4), ("Ingredient_Fibre", 1)]:
    _bad23.append(("Soul Orb", _rc23[_SID23[0]]))
for t_ in range(1, 8):
    o_ = _io23[_SID23[t_]]["Recipe"]["Input"]
    want_ = [(_SID23[t_ - 1], 1), (o_[1]["ItemId"], o_[1]["Quantity"]), (_ESS23[t_], _QTY23[t_])]          # the bars unchanged from 0.1.20
    if _rc23[_SID23[t_]] != want_:
        _bad23.append((_SID23[t_], _rc23[_SID23[t_]], want_))
for i_ in _SID23:          # nothing else in an item moved: only Interactions.Primary (+ the recipe; the 3 recoloured tiers' Light colour)
    a_, b_ = dict(_it23[i_]), dict(_io23[i_])
    for k_ in ("Recipe", "Interactions", "Light"):
        a_.pop(k_, None)
        b_.pop(k_, None)
    if a_ != b_ or _it23[i_]["Interactions"] != {"Primary": "SkyyArmory_Soul_Wings", "Secondary": "SkyyArmory_Soul_Bind"} \
            or _it23[i_]["Recipe"].get("BenchRequirement") != _io23[i_]["Recipe"].get("BenchRequirement"):
        _bad23.append((i_, "other fields moved"))
_flat23 = json.dumps([_rc23[i_] for i_ in _SID23])
check(not _bad23 and "Crystal" not in _flat23 and "SkyyArmory_Essence_" not in _flat23
      and all(ahas("item", e_) for e_ in set(_ESS23)) and aj("item", "Ingredient_Life_Essence_Concentrated")["Recipe"]["Input"] == [{"ItemId": "Ingredient_Life_Essence", "Quantity": 100}],
      "P23 (Skyy 2026-10-11 'swap from crystals to essence ... follow the vanillas essence progression, starting with life essence'): the Soul Orb = "
      "25 Life Essence + 4 Sticks + 1 Plant Fibre (no Blue Crystal); the cages Life 15 / Fire 15 / Ice 15 / Water 12 / Lightning 12 / Void 10 / "
      "Concentrated Life 1 (= 100 Life, vanilla 100 : 1) on the 0.1.20 bars + bench; only the recipe + Primary (+ the moved tiers' light) changed; "
      "every essence a vanilla item: %s" % _bad23[:3])


def _gear_from_recipe(out_id, inputs, frm, to):          # SkyyGear 0.2.22 GearUp.fromRecipe, line for line (the item's own recipe: output = it x1)
    if out_id != to:
        return None
    has, ids, qs = False, [], []
    for iid, q in inputs:
        if iid is None:
            return None
        if iid == frm and not has and q == 1:
            has = True
            continue
        if iid in (frm, to):
            return None
        if q < 1:
            continue
        if iid in ids:
            qs[ids.index(iid)] += q
        else:
            ids.append(iid)
            qs.append(q)
    return (ids, qs) if has else None


_gu23 = [_gear_from_recipe(_SID23[t_], _rc23[_SID23[t_]], _SID23[t_ - 1], _SID23[t_]) for t_ in range(1, 8)]
check(all(g_ is not None and len(g_[0]) == 2 and g_[0][1] == _ESS23[t_ + 1] for t_, g_ in enumerate(_gu23)),
      "P23: SkyyGear 0.2.22's /upgrade reader (GearUp.fromRecipe, re-run here line for line on the real recipes) finds all 7 cage steps; the "
      "cost = the bars + the vanilla essence: %s" % ["%s: %s" % (_T23[t_ + 1], g_) for t_, g_ in enumerate(_gu23)])
_wc23 = json.loads(JZ21.read("Server/Item/Interactions/Weapons/Wand/SkyyArmory/SkyyArmory_Soul_Wings_Charge.json").decode("utf-8"))
_wl23 = json.loads(JZ21.read("Server/Item/Interactions/Weapons/Wand/SkyyArmory/SkyyArmory_Soul_Wings_Launch.json").decode("utf-8"))
_wr23 = json.loads(JZ21.read("Server/Item/RootInteractions/Weapons/Wand/SkyyArmory/SkyyArmory_Soul_Wings.json").decode("utf-8"))
_wm23 = json.loads(JZ21.read("Server/Projectiles/Player/SkyyArmory/SkyyArmory_Soul_Wings_Mark.json").decode("utf-8"))
_vwp23 = aj("int", "Wand_Primary")
check(_wc23["Type"] == "Charging" and _wc23["AllowIndefiniteHold"] is True and _wc23["Effects"] == _vwp23["Effects"]
      and _wc23["Next"] == {"0": "SkyyArmory_Soul_Wings_Tap", "0.35": "SkyyArmory_Soul_Wings_Launch"} and sorted(_vwp23["Next"]) == ["0", "0.35"]
      and _wl23["Type"] == "LaunchProjectile" and _wl23["ProjectileId"] == "SkyyArmory_Soul_Wings_Mark" and _wr23 == {"Interactions": ["SkyyArmory_Soul_Wings_Charge"]}
      and _wm23.get("Damage", 0) == 0 and _wm23.get("Gravity") == 0,
      "P23 (Wings of Fate input): the Soul items' PRIMARY = a Charging with the wand's own pose + 0.35 s key (AllowIndefiniteHold: fires on "
      "release), tap '0' = a no-op Simple, the key = the harmless invisible marker SkyyArmory_Soul_Wings_Mark (Damage 0, Gravity 0); right click "
      "stays the Bindings: %s / %s" % (_wc23.get("Next"), _wl23.get("ProjectileId")))
_lang23 = JZ21.read("Server/Languages/en-US/server.lang").decode("utf-8")
_dl23 = dict((l_.split(" = ", 1)[0], l_.split(" = ", 1)[1]) for l_ in _lang23.splitlines() if " = " in l_)
_DPS23 = ["5", "7", "10", "15", "20", "30", "40", "55"]
_STAB23 = ["1.75", "1.6", "1.45", "1.35", "1.2", "1.1", "1.05", "1"]
check(all(("for %s damage a second" % d_) in _dl23["items.%s.description" % i_] and ("Look %s s to make" % s_) in _dl23["items.%s.description" % i_]
          and "Wings of Fate" in _dl23["items.%s.description" % i_] for i_, d_, s_ in zip(_SID23, _DPS23, _STAB23))
      and "No longer dropped or used" in _dl23["items.SkyyArmory_Essence_Earth.description"] and "No longer dropped or used" in _dl23["items.SkyyArmory_Essence_Light.description"],
      "P23: the tooltips say the new damage a second (5 .. 55), the faster solid time (1.75 .. 1 s) and Wings of Fate; Earth / Light Essence say "
      "they are no longer dropped or used (ids kept): %s" % _dl23["items.Weapon_Wand_SoulCage_Thorium.description"][:200])
_sp23 = lambda p_: json.loads(JZ21.read(p_).decode("utf-8"))
_wisp23 = _sp23(_P23 + "Spawners/SkyyArmory_SoulWisp_Iron_Dust.particlespawner")
_sold23 = _sp23(_P23 + "Spawners/SkyyArmory_Soul_Iron_Dust_Blue.particlespawner")
_solo23 = json.loads(OZ120.read(_P23 + "Spawners/SkyyArmory_Soul_Iron_Dust_Blue.particlespawner").decode("utf-8"))
_ws23 = _sp23(_P23 + "SkyyArmory_SoulWisp_Iron.particlesystem")
_wg23 = _sp23(_P23 + "SkyyArmory_Wings_Blue.particlesystem")
check(_wisp23["Particle"]["InitialAnimationFrame"]["Opacity"] == 0.35 and _wisp23["SpawnRate"]["Max"] < _sold23["SpawnRate"]["Max"]
      and _wisp23["Particle"]["InitialAnimationFrame"]["Scale"]["X"]["Max"] < _sold23["Particle"]["InitialAnimationFrame"]["Scale"]["X"]["Max"]
      and _sold23["Particle"]["InitialAnimationFrame"]["Scale"]["X"]["Max"] > _solo23["Particle"]["InitialAnimationFrame"]["Scale"]["X"]["Max"]
      and _sold23["EmitOffset"]["X"]["Max"] < _solo23["EmitOffset"]["X"]["Max"] and _ws23["LifeSpan"] == 0.25 and _wg23["LifeSpan"] == 0.2
      and _sold23["Particle"]["InitialAnimationFrame"]["Color"] == _solo23["Particle"]["InitialAnimationFrame"]["Color"],
      "P23 (Skyy: 'make the lines more whispy when not tethered, and more obviouis when it is'): the wispy dot = 35 %% opacity, a third of the dust, "
      "smaller; the solid dot = 1.6x bigger and packed tighter than 0.1.20 (same colour); both finite (0.25 s), the wing dot 0.2 s")
print("P23. 0.1.21: 23 new files + Wings / WingsState, %d changed (8 items, 6 art, 16 solid spawners, lang); recipes %s; SkyyGear's reader finds 7 steps"
      % (len(W21_CHANGED), "; ".join("%s %s" % (_T23[t_], _rc23[i_]) for t_, i_ in enumerate(_SID23))))
'''
hrep('''print("P22. 0.1.20: %d non-class files identical to 0.1.19, manifest version only, the same %d classes" % (len(_files22), len(_c22n)))
''', '''print("P22. 0.1.20: %d non-class files identical to 0.1.19, manifest version only, the same %d classes" % (len(_files22), len(_c22n)))
''' + P23)

# ---- R24 (JVM): after R23, before L2 (L2 changes the store)
R24 = r'''    # ============================================================================ R24. 0.1.21 THE SOUL ORB ROUND - every new path EXECUTED
    WG, WGS = JClass(PKG + "Wings"), JClass(PKG + "WingsState")
    # R24 classes: Wings + WingsState (hidden from A / X's lists) load + verify under -Xverify:all and pass the MethodHandles access audit
    cl24 = [str(Cls.forName(PKG + c_, True, sysl).getName()) for c_ in ("Wings", "WingsState")]
    au24 = [lookup_audit(PKG + c_) for c_ in ("Wings", "WingsState")]
    check(len(cl24) == 2 and all(not r_ for r_, n_ in au24) and sum(n_ for r_, n_ in au24) > 100,
          "R24 classes: Wings + WingsState load and verify (-Xverify:all) and every reference passes MethodHandles.Lookup: %s" % [(len(r_), n_, r_[:2]) for r_, n_ in au24])

    # R24a THE ROWS + TABLES + DEFAULTS + CLAMPS (the real 0.1.21 defaults)
    ACfg.useDefaults()
    Rows24 = JClass(PKG + "CfgRows")
    k24 = [str(k_) for k_ in Rows24.KEYS]
    d24 = dict(zip(k24, [str(x_) for x_ in Rows24.DEFS]))
    c24 = dict(zip(k24, [str(x_) for x_ in Rows24.CATS]))
    h24 = dict(zip(k24, [str(x_) for x_ in Rows24.HELPS]))
    dc24 = str(ACfg.DEF_CFG)
    WROWS24 = {"wings.enabled": "true", "wings.mana": "20", "wings.stamina": "10", "wings.speed": "18", "wings.boundSeconds": "0.35", "wings.bounds": "3",
               "wings.allyBounds": "8", "wings.allySpeed": "24", "wings.lift": "4", "wings.lockRange": "30", "wings.lockCone": "30", "wings.arrive": "3",
               "wings.baseHeal": "10", "wings.tierHeal": "1", "wings.healCap": "60", "wings.anyPlayer": "true"}
    fl24 = [k_ for k_, v_ in WROWS24.items() if d24.get(k_) != v_ or c24.get(k_) != "soul" or ("\n%s=%s\n" % (k_, v_)) not in dc24]
    fl24 += [k_ for k_ in ("soul.damagePerMana", "soul.damageMult", "essence.chance.Earth", "essence.chance.Light", "essence.chance.Frost") if k_ in k24 or ("\n" + k_ + "=") in dc24]
    fl24 += [k_ for k_ in ("soul.damagePerSecond.Orb=5", "soul.damagePerSecond.Thorium=15", "soul.damagePerSecond.Onyxium=55", "soul.stabilize.Orb=1.75",
                           "soul.stabilize.Onyxium=1", "soul.lineDots=64", "essence.zone.Water=2", "essence.zone.Ice=3", "essence.chance.Lightning=8") if ("\n" + k_ + "\n") not in dc24]
    ld24 = (bool(ACfg.WINGS_ON), float(ACfg.WINGS_MA), float(ACfg.WINGS_ST), float(ACfg.WINGS_SPEED), float(ACfg.WINGS_BOUND), int(ACfg.WINGS_BOUNDS),
            int(ACfg.WINGS_ABOUNDS), float(ACfg.WINGS_ASPEED), float(ACfg.WINGS_LIFT), int(ACfg.WINGS_RANGE), int(ACfg.WINGS_CONE), float(ACfg.WINGS_ARRIVE),
            float(ACfg.WINGS_BASE), float(ACfg.WINGS_PER), int(ACfg.WINGS_CAP), bool(ACfg.WINGS_ANY), int(ACfg.SOUL_DOTS))
    pr24 = Props()
    for k_, v_ in (("wings.mana", "999"), ("wings.bounds", "0"), ("wings.boundSeconds", "0.01"), ("wings.healCap", "150"), ("soul.damagePerSecond.Thorium", "900"),
                   ("soul.lineDots", "999"), ("wings.anyPlayer", "false"), ("soul.stabilize.Orb", "-3")):
        pr24.setProperty(k_, v_)
    ACfg.apply(pr24)
    cl24b = (float(ACfg.WINGS_MA), int(ACfg.WINGS_BOUNDS), float(ACfg.WINGS_BOUND), int(ACfg.WINGS_CAP), float(ACfg.SOUL_DPS[3]), int(ACfg.SOUL_DOTS),
             bool(ACfg.WINGS_ANY), float(ACfg.SOUL_STAB[0]))
    ACfg.useDefaults()
    tx24 = str(ACfg.soulText())
    check(not fl24 and ld24 == (True, 20.0, 10.0, 18.0, 0.35, 3, 8, 24.0, 4.0, 30, 30, 3.0, 10.0, 1.0, 60, True, 64)
          and cl24b == (200.0, 1, 0.15, 100, 500.0, 128, False, 0.0) and all(len(h24[k_]) <= 100 for k_ in WROWS24)
          and "for 5 / 7 / 10 / 15 / 20 / 30 / 40 / 55 damage/s (before levels)" in tx24 and "Wings of Fate on (hold left click: 20 Mana + 10 Stamina; 3 glide bounds at 18 b/s, or up to 8 to an ally within 30 blocks" in tx24
          and "arriving heals 10% + 1% a tier + the stored healing, at most 60%" in tx24 and "line dots 64 a draw" in tx24,
          "R24a: the 16 wings.* rows (Server Setup > Armory > Soul Orb + essences) with their defaults in the rows + the default file, the new tables "
          "(damagePerSecond 5 .. 55, stabilize 1.75 .. 1, the vanilla essences), no damagePerMana / damageMult / Earth / Light / Frost line; the loader "
          "clamps (Mana 999 -> 200, bounds 0 -> 1, 0.01 s -> 0.15, cap 150 -> 100, Thorium 900 -> 500 dmg/s, 999 dots -> 128, stabilize -3 -> 0); "
          "armory:soul words: %s | %s | %s" % (fl24[:6], cl24b, tx24[-420:]))

    # R24b DAMAGE A SECOND PER TIER through the REAL pulse (Skyy: "a thorium one was only doing 2 damage a tick. it needs a lot more damage")
    dmg24 = {}
    for t_, i_ in enumerate(SOUL19_IDS):
        setup22(item=i_, mana=200.0)
        ACfg.useDefaults()
        ACfg.TRAV_FX = True
        NEAR22[:] = [mob(4900 + t_, 10.0, 64.0, 0.5, BOX22), rc]
        tick22(1, 0)
        tick22(20, 100)                    # 2 s: pulses at 0 / 0.5 / 1 / 1.5 / 2
        hs_ = [h_[1] for h_ in hits22() if h_[0] == 4900 + t_]
        dmg24[SOUL19_TIERS[t_]] = (len(hs_), sorted(set(hs_)), round(200.0 - sv(mc, MANA), 4))
    want24 = dict((m_, (5, [round(d_ * 0.5, 4)], round(5 * 0.5 * p_, 4))) for m_, d_, p_ in zip(SOUL19_TIERS, [5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 40.0, 55.0],
                                                                                              [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35]))
    check(dmg24 == want24,
          "R24b: ONE Binding for 2 s at the defaults - every 0.5 s pulse hits for half the tier's damage a second (Orb 2.5 .. Thorium 7.5 (0.1.20: "
          "1.73) .. Onyxium 27.5) through Damage$EntitySource(you), 5 pulses; Mana per Binding unchanged (1.00 .. 1.35/s): %s" % json.dumps(dmg24))

    # R24c THE TETHER TIMING (~30 % faster): wispy one tick before the tier's new time, solid at it (100 ms ticks: the first whole tick at / past it)
    st24 = {}
    for t_, i_ in enumerate(SOUL19_IDS):
        setup22(item=i_)
        ACfg.useDefaults()
        NEAR22[:] = [mob(4920 + t_, 10.0, 64.0, 0.5, BOX22), rc]
        tick22(1, 0)
        k_ = int(math.ceil(round([1.75, 1.6, 1.45, 1.35, 1.2, 1.1, 1.05, 1.0][t_] * 1000.0) / 100.0 - 1e-9))
        tick22(k_ - 1, 100)
        a_ = solid22()
        tick22(1, 100)
        st24[SOUL19_TIERS[t_]] = (k_, a_, solid22())
    check(all(v_[1] == [False] and v_[2] == [True] for v_ in st24.values()) and [v_[0] for v_ in st24.values()] == [18, 16, 15, 14, 12, 11, 11, 10],
          "R24c (Skyy: 'make it teather a little faster'): each tier is still wispy one 100 ms tick before its new time and solid at it - Orb 1.75 s "
          "(0.1.20: 2.5), Copper 1.6, Iron 1.45, Thorium 1.35, Cobalt 1.2, Adamantite 1.1, Mithril 1.05, Onyxium 1.0 (0.1.20: 1.5): %s" % json.dumps(st24))

    # R24d THE LINE LOOK PER STATE (defaults: 64 dots) - wispy = sparse, faint, flickering; solid = dense, bright
    setup22()
    ACfg.useDefaults()
    ACfg.TRAV_FX = True
    NEAR22[:] = [mob(4940, 10.0, 64.0, 0.5, BOX22), rc]
    draws24 = []
    AT.PSEEN.clear()
    tick22(1, 0)
    for k_ in range(9):
        s_ = st22()
        d0_ = int(s_.draws)
        ps_ = list(AT.PSEEN)
        draws24.append((int(s_.draws), len([p_ for p_ in ps_ if str(p_) == "SkyyArmory_SoulWisp_Iron"]), len([p_ for p_ in ps_ if str(p_) == "SkyyArmory_Soul_Iron"])))
        AT.PSEEN.clear()
        tick22(1, 100)
    wd24 = [x_ for x_ in draws24 if x_[1] > 0]
    tick22(20, 100)                    # solid (Iron 1.45 s)
    AT.PSEEN.clear()
    dr0_ = int(st22().draws)
    tick22(9, 100)
    sd24 = (int(st22().draws) - dr0_, len([p_ for p_ in list(AT.PSEEN) if str(p_) == "SkyyArmory_Soul_Iron"]), len([p_ for p_ in list(AT.PSEEN) if str(p_) == "SkyyArmory_SoulWisp_Iron"]))
    fl24d = [[k_ for k_ in range(5) if bool(SO.flick(k_, d_))] for d_ in (1, 2, 3)]
    al24 = [list(SO.alloc(JArray(JInt)(w_), b_)) for w_, b_ in (([5, 20], 64), ([20] * 20, 64), ([30, 30, 30], 64), ([1] * 70, 64), ([20, 5], 0), ([], 64), ([40, 2], 20))]
    check(len(wd24) >= 3 and [x_[1] for x_ in wd24[:3]] == [4, 3, 3] and all(x_[2] == 0 for x_ in wd24) and sd24 == (3, 60, 0)
          and fl24d == [[2], [1, 4], [0, 3]] and int(SO.want(8.9, False)) == 5 and int(SO.want(8.9, True)) == 20 and int(SO.want(0.0, True)) == 1
          and al24[0] == [5, 20] and sum(al24[1]) <= 64 and min(al24[1]) >= 1 and al24[1] == [3] * 20 and al24[2] == [21, 21, 21]
          and sum(al24[3]) == 64 and min(al24[3]) >= 0 and al24[4] == [0, 0] and al24[5] == [] and sum(al24[6]) == 20 and al24[6][1] >= 1,
          "R24d (Skyy: 'make the lines more whispy when not tethered, and more obviouis when it is'): a WISPY Iron Binding 8.9 blocks away = 5 "
          "sparse dots (1.8 apart) of the faint SkyyArmory_SoulWisp_Iron, one in three flickered out and the gap MOVES every draw (4 / 3 / 3 dots; "
          "skipped %s), never the solid system; SOLID = 20 dense dots (0.45 apart) of the bright SkyyArmory_Soul_Iron a draw (3 draws = 60), never "
          "the wisp; the budget (alloc): fits = as asked, over = shared (20 x 20 -> 3 each = 60 <= 64; 3 x 30 -> 21 each), every line >= 1 dot, "
          "0 = nothing: wispy %s solid %s alloc %s" % (fl24d, wd24[:4], sd24, al24))
    setup22(item=SOUL19_IDS[7])
    ACfg.useDefaults()
    ACfg.TRAV_FX = True
    NEAR22[:] = pack22(4950, 24) + [rc]
    tick22(1, 0)
    tick22(12, 100)                    # all 20 solid (Onyxium 1.0 s)
    AT.PSEEN.clear()
    dr0_ = int(st22().draws)
    tick22(9, 100)
    on24 = (nb22(), all(solid22()), int(st22().draws) - dr0_, len([p_ for p_ in list(AT.PSEEN) if str(p_).startswith("SkyyArmory_Soul")]))
    check(on24[0] == 20 and on24[1] and on24[2] > 0 and on24[3] <= 64 * on24[2] and on24[3] >= 40 * on24[2],
          "R24d: 20 SOLID Onyxium Bindings ask for about 20 dots each - every draw stays within soul.lineDots 64 (shared out, at least 2 each): %s" % (on24,))

    # R24d2 FIX (review MEDIUM 'at Cobalt and above a solid line is no denser than a lone wispy one'): Soul.share - over the budget the wispy
    # lines are held to half a fair share FIRST, the solid ones share the rest: a solid line keeps >= 2x a wispy line's dots at EVERY tier
    def sh24(n_, solid_, l_=10.0, budget=64):
        w_ = [int(SO.want(l_, s_)) for s_ in solid_]
        return [int(x_) for x_ in SO.share(JArray(JInt)(w_), JArray(JBoolean)(solid_), budget)]
    tiers24 = {}
    for m_, n_ in zip(SOUL19_TIERS, [1, 2, 4, 6, 10, 14, 16, 20]):
        aw_ = sh24(n_, [False] * n_)
        as_ = sh24(n_, [True] * n_)
        mx_ = sh24(n_, [k_ % 2 == 0 for k_ in range(n_)])
        tiers24[m_] = (min(aw_), max(aw_), min(as_), max(as_), sum(as_), mx_[:2], sum(mx_))
    bad24d = [m_ for m_, v_ in tiers24.items() if v_[2] < 2 * v_[1] or v_[4] > 64 or v_[6] > 64 or (len(v_[5]) == 2 and v_[5][0] < 2 * v_[5][1])]
    setup22(item=SOUL19_IDS[7])
    ACfg.useDefaults()
    ACfg.TRAV_FX = True
    NEAR22[:] = pack22(4970, 24) + [rc]
    tick22(1, 0)
    tick22(2, 100)
    AT.PSEEN.clear()
    dr0_ = int(st22().draws)
    tick22(3, 100)                     # all 20 still wispy (Onyxium 1.0 s)
    nw_ = len([p_ for p_ in list(AT.PSEEN) if str(p_) == "SkyyArmory_SoulWisp_Onyxium"])
    ow24 = (nb22(), not any(solid22()), int(st22().draws) - dr0_, nw_)
    tick22(12, 100)                    # all 20 solid
    AT.PSEEN.clear()
    dr1_ = int(st22().draws)
    tick22(9, 100)
    os24 = (all(solid22()), int(st22().draws) - dr1_, len([p_ for p_ in list(AT.PSEEN) if str(p_) == "SkyyArmory_Soul_Onyxium"]))
    check(not bad24d and tiers24["Onyxium"][:4] == (1, 1, 3, 3) and tiers24["Cobalt"][:4] == (3, 3, 6, 6) and tiers24["Thorium"][:4] == (5, 5, 10, 10) and tiers24["Iron"][:2] == (6, 6)
          and ow24[0] == 20 and ow24[1] and ow24[2] > 0 and ow24[3] == 20 * ow24[2] and os24[0] and os24[1] > 0 and 2 * 20 * os24[1] <= os24[2] <= 64 * os24[1],
          "R24d2 (FIX, review: 'a solid line is no denser than a lone wispy one' at Cobalt+): 10-block lines at every tier within 64 dots - all wispy "
          "/ all solid / mixed: solid >= 2x wispy everywhere (Iron 4 lines: wispy as asked 6, solid 16; Thorium 6: 5 vs 10; Cobalt 10: 3 vs 6; Onyxium 20: 1 vs 3); the "
          "REAL Onyxium draw: 20 forming Bindings = 1 faint SoulWisp dot each a draw, 20 solid = 2-3 bright Soul dots each (40 .. 64 a draw): "
          "%s | wispy %s solid %s | bad %s" % (json.dumps(tiers24), ow24, os24, bad24d))

    # R24h FIX (review MEDIUM 'the no migration claim is wrong for fresh 0.1.19 and 0.1.20 installs'): migrate021 (PROJECT-RULES 4)
    MK21 = str(ACfg.M21_MARK)

    def upd21(t_):
        r_ = ACfg.m21Update(t_)
        return None if r_ is None else (str(r_[0]), str(r_[1]), [str(x) for x in r_[2]], [str(x) for x in r_[3]])
    OLDS21 = [("Orb", "2.5", "1.75"), ("Copper", "2.3", "1.6"), ("Iron", "2.1", "1.45"), ("Thorium", "1.9", "1.35"), ("Cobalt", "1.7", "1.2"),
              ("Adamantite", "1.6", "1.1"), ("Mithril", "1.5", "1.05"), ("Onyxium", "1.5", "1")]
    f20 = ("a=1\nsoul.damagePerMana=2\nsoul.lineDots=48\nsoul.damageMult.Orb=1\n"
           + "".join("soul.stabilize.%s=%s\n" % (m_, o_) for m_, o_, n_ in OLDS21) + "essence.chance.Frost=8\nessence.zone.Light=4\nb=2\n")
    w20 = ("a=1\nsoul.damagePerMana=2\nsoul.lineDots=64\nsoul.damageMult.Orb=1\n" + MK21 + "\n"
           + "".join("soul.stabilize.%s=%s\n" % (m_, n_) for m_, o_, n_ in OLDS21) + "essence.chance.Frost=8\nessence.zone.Light=4\nb=2\n")
    u1 = upd21(f20)
    u2 = upd21("soul.stabilize.Orb=3\r\nsoul.lineDots = 48.0\r\nessence.chance.Frost=12\r\nsoul.damagePerMana=4\r\n")
    u3 = upd21("quick.life=20\n")
    u4 = upd21(u1[0])
    u5 = upd21(str(ACfg.DEF_CFG))
    check(u1 is not None and u1[0] == w20 and u1[1] == ", ".join("soul.stabilize.%s %s -> %s" % x_ for x_ in OLDS21) + ", soul.lineDots 48 -> 64"
          and u1[2] == [] and len(u1[3]) == 27
          and u2 is not None and u2[0] == MK21 + "\r\nsoul.stabilize.Orb=3\r\nsoul.lineDots = 64\r\nessence.chance.Frost=12\r\nsoul.damagePerMana=4\r\n"
          and u2[1] == "soul.lineDots 48.0 -> 64" and len(u2[2]) == 3 and "soul.stabilize.Orb=3 kept (custom) - the 0.1.21 default is 1.75" in u2[2][0]
          and "essence.chance.Frost=12 is no longer read" in " ".join(u2[2]) and "Frost = Ice" in " ".join(u2[2]) and "soul.damagePerMana=4 is no longer read" in " ".join(u2[2])
          and u3 == ("quick.life=20\n" + MK21 + "\n", "", [], []) and u4 is None and u5 is None,
          "R24h (PROJECT-RULES 4): a 0.1.20 default file - the 8 soul.stabilize lines + soul.lineDots on the old defaults -> 1.75 .. 1 / 64 "
          "(value text only, the marker before the first, the retired 0.1.20 lines left as they are, silently); CRLF kept, hand-set values KEPT + "
          "noted, a hand-set Frost / damagePerMana named (its new home); no line = the marker only (Skyy's live file); runs once; a 0.1.21 default "
          "file = already done: %s / %s / %s" % (u1, u2, u3))
    mdir21 = os.path.join(SCRATCH, "m21", "mods", "Skyy_SkyyArmory")
    shutil.rmtree(os.path.dirname(os.path.dirname(mdir21)), ignore_errors=True)
    os.makedirs(mdir21)
    mtxt21 = f20.replace("\n", "\r\n").replace("essence.zone.Light=4", "essence.zone.Light=4\r\nessence.chance.Wind=3").encode("latin-1")
    open(os.path.join(mdir21, "config.properties"), "wb").write(mtxt21)
    ACfg.DIR = Paths.get(mdir21)
    ACfg.FILE = ACfg.DIR.resolve("config.properties")
    ALOG24 = JClass(PKG + "ArmoryLog")
    for k_ in ("tab:essence.chance.Frost", "tab:essence.zone.Light", "tab:essence.chance.Wind"):
        ALOG24.ONCE.remove(k_)
    mr21 = [str(ACfg.migrate012()), str(ACfg.migrate013()), str(ACfg.migrate014()), str(ACfg.migrate016()), str(ACfg.migrate017()), str(ACfg.migrate018())]
    bf21 = open(os.path.join(mdir21, "config.properties"), "rb").read()
    mr21a = str(ACfg.migrate021())
    af21 = open(os.path.join(mdir21, "config.properties"), "rb").read()
    hist21 = os.path.join(mdir21, "config-history")
    baks21 = sorted(f_ for f_ in os.listdir(hist21) if f_.endswith(".bak")) if os.path.isdir(hist21) else []
    bak21 = open(os.path.join(hist21, baks21[-1]), "rb").read() if baks21 else b""
    log21 = open(os.path.join(mdir21, "config-changes.log"), "rb").read().decode("latin-1") if os.path.isfile(os.path.join(mdir21, "config-changes.log")) else ""
    mr21b = str(ACfg.migrate021())
    af21b = open(os.path.join(mdir21, "config.properties"), "rb").read()
    ACfg.load()
    ld21 = ([float(x_) for x_ in ACfg.SOUL_STAB], int(ACfg.SOUL_DOTS), bool(ALOG24.ONCE.containsKey("tab:essence.chance.Frost")),
            bool(ALOG24.ONCE.containsKey("tab:essence.zone.Light")), bool(ALOG24.ONCE.containsKey("tab:essence.chance.Wind")))
    ACfg.DIR = None
    ACfg.FILE = None
    ACfg.useDefaults()
    check(af21 == upd21(bf21.decode("latin-1"))[0].encode("latin-1") and b"soul.stabilize.Orb=1.75\r\n" in af21 and b"soul.lineDots=64\r\n" in af21
          and b"soul.damagePerMana=2\r\n" in af21 and baks21 and bak21 == bf21 and "\tSkyyArmory 0.1.21\t-\tupdate\tsoul.stabilize.Orb\t2.5\t1.75\tok" in log21
          and "\tSkyyArmory 0.1.21\t-\tupdate\tsoul.lineDots\t48\t64\tok" in log21 and "soul.stabilize.Orb 2.5 -> 1.75" in mr21a and mr21b == "" and af21b == af21
          and ld21 == ([1.75, 1.6, 1.45, 1.35, 1.2, 1.1, 1.05, 1.0], 64, False, False, True),
          "R24h (the real ArmoryCfg.migrate021 on a scratch 0.1.20-style file, after migrate012 .. 018 like setup()): History copy = the old bytes, "
          "an Undo-able change-log line per key, CRLF kept, the second run idle; the loader then reads 1.75 .. 1 s + 64 dots; the retired Frost / "
          "Light lines never WARN, an unknown one (Wind) still does: %s | %s | %s | %s" % (mr21, mr21a[:200], log21.strip()[-80:], ld21))

    # R24e THE ESSENCE DROP TABLE is the vanilla ladder (R22l rolls it): no SkyyArmory essence in it, Water has a zone
    check([str(x_) for x_ in ADefs.ESS_IDS] == ["Ingredient_Life_Essence", "Ingredient_Fire_Essence", "Ingredient_Ice_Essence", "Ingredient_Water_Essence",
                                               "Ingredient_Lightning_Essence", "Ingredient_Void_Essence"]
          and [str(x_) for x_ in ADefs.ESS_NAMES] == ["Life", "Fire", "Ice", "Water", "Lightning", "Void"],
          "R24e: the drop table = Life / Fire / Ice / Water / Lightning / Void (vanilla items; Water now drops in Zone 2, Lightning in Zone 4); "
          "Concentrated Life craft-only; our Earth / Light essences never drop")

    # R24f WINGS OF FATE through the REAL marker chain (ArmoryTrav.added -> Wings.marker -> cast -> bound; Wings.tickPlayer every tick)
    WMARK24 = "SkyyArmory_Soul_Wings_Mark"
    keep_party24 = br.get("party:fn:members")          # put back after R24
    keep_pk24 = br.get("profile:fn:key")
    G24 = float(JClass(PKG + "Monk").grav())
    XP24 = []

    @JImplements("java.util.function.Function")
    class Xp24:
        @JOverride
        def apply(self, o):
            XP24.append((str(o[0]), round(float(o[1]), 4), str(o[2]), str(o[3]) if len(o) > 3 else None))          # FIX (review): + the profile key
            return BOOL22.TRUE

    @JImplements("java.util.function.Function")
    class Party24:
        @JOverride
        def apply(self, o):
            return JArray(JObject)([str(cu), str(pu)]) if str(o) in (str(cu), str(pu)) else JArray(JObject)([])

    def setup24(item=IRON22, mana=200.0, stam=20.0, cvy=0.0, walls=()):
        setup22(item=item, mana=mana, walls=walls)
        ACfg.useDefaults()
        ACfg.TRAV_FX = True
        WG.STATES.clear()
        WG.CLOCK = JLong(T22[0])
        put(rc, VELc.getComponentType(), VELc())
        comp(rc, VELc.getComponentType()).setClient(0.0, cvy, 0.0)
        mc.setStatValue(STAM, JFloat(stam))
        for r_, u_, x_, z_ in ((rp, pu, 20.5, 0.5), (rs, su, 20.5, 4.0)):
            put(r_, DTHc.getComponentType(), None)
            at20(r_, x_, 64.0, z_)
        mp.setStatValue(HP, JFloat(50.0))
        ms.setStatValue(HP, JFloat(50.0))
        br.put("skill:fn:healxp", Xp24())
        br.put("party:fn:members", Party24())          # SkyyParty's shape: you + your party (p1 + p2); p3 = a stranger
        br.remove("profile:fn:key")          # FIX (review): no SkyyProfiles = the profile key is the UUID
        XP24[:] = []
        NEAR22[:] = [rc, rp, rs]

    def cast24(i_):
        WG.CLOCK = JLong(T22[0])
        mk_, pc_ = launched(WMARK24, i_, 0.5, 65.5, 0.5)
        n0_, r0_ = len(instrs19(rc)), len(list(TBf.REMOVED))
        AT.added(mk_, pc_, int(ADefs.pidCode(WMARK24)), tst, tbuf)
        return (mk_ in list(TBf.REMOVED)[r0_:]), [w_[0] for w_ in instrs19(rc)[n0_:]]

    def tick24(n_=1, ms_=100, move=None, store=None):
        w_ = []
        for k_ in range(n_):
            clk22(ms_)
            WG.CLOCK = JLong(T22[0])
            if move is not None:
                move(k_)
            n0_ = len(instrs19(rc))
            WG.tickPlayer(rc, store if store is not None else tst, tbuf)
            w_.append([x_[0] for x_ in instrs19(rc)[n0_:]])
        return w_

    def ws24():
        return WG.STATES.get(cu)

    def near24(a_, b_, eps=0.01):
        return a_ is not None and b_ is not None and all(abs(float(x_) - float(y_)) <= eps for x_, y_ in zip(a_, b_))
    # (1) NO ALLY: 3 glide bounds where you look (steer between them), ONE write each and none in between, the wings + trail, 20 Mana + 10 Stamina
    setup24()
    NEAR22[:] = [rc]
    m0_, s0_ = sv(mc, MANA), sv(mc, STAM)
    rm1_, w1_ = cast24(5000)
    g_st = ws24()
    gl24 = {"marker removed": rm1_, "first": w1_, "ally": None if g_st is None else g_st.ally, "most": None if g_st is None else int(g_st.most),
            "paid": (round(m0_ - sv(mc, MANA), 3), round(s0_ - sv(mc, STAM), 3)), "why": str(WG.LAST_WHY)}
    AT.PSEEN.clear()
    pos_ = [0.5]

    def fly24(k_):
        pos_[0] += 1.5
        at20(rc, pos_[0], 64.0, 0.5)
    t1_ = tick24(3, 100, fly24)
    look22(0.0, 0.0, 1.0)              # look +z: the next bound goes that way
    t2_ = tick24(9, 100, fly24)
    gl24["ticks"] = [len(x_) for x_ in t1_ + t2_]
    gl24["bounds"] = [x_ for x_ in t1_ + t2_ if x_]
    gl24["end"] = (ws24() is None, str(WG.LAST_END))
    gl24["fx"] = (len([p_ for p_ in list(AT.PSEEN) if str(p_) == "SkyyArmory_Wings_Blue"]), len([p_ for p_ in list(AT.PSEEN) if str(p_) == "SkyyArmory_Soul_Orb"]))
    gl24["kept"] = (round(m0_ - sv(mc, MANA), 3), round(s0_ - sv(mc, STAM), 3))
    gl24["dash"] = [bool(w_[1]) for w_ in instrs19(rc)]
    check(gl24["marker removed"] and len(gl24["first"]) == 1 and near24(gl24["first"][0], (18.0, 4.0, 0.0)) and gl24["ally"] is None and gl24["most"] == 3
          and gl24["paid"] == (20.0, 10.0) and gl24["why"] == "glide" and gl24["ticks"] == [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]
          and near24(gl24["bounds"][0][0], (0.0, 4.0, 18.0)) and near24(gl24["bounds"][1][0], (0.0, 4.0, 18.0)) and gl24["end"] == (True, "glide over")
          and gl24["fx"][0] > 0 and gl24["fx"][0] == 10 * gl24["fx"][1] and gl24["kept"] == (20.0, 10.0) and gl24["dash"] == [True, True, True],
          "R24f (Priest.md: 'long, fast gliding bounds the way you look'): hold left click + let go with NO ally that way = the marker is removed, "
          "20 Mana + 10 Stamina paid (2 : 1), 3 bounds at 18 b/s + 4 up where you look (the 2nd + 3rd follow a new look: +z), each ONE velocity Set "
          "(the wand launch's dash config) 350 ms apart and NOTHING in between, then 'glide over'; the glowing blue wings (10 dots) + a blue trail dot every "
          "150 ms; you moved = no refund: %s" % json.dumps(gl24, default=str))
    # (2) THE ALLY LOCK: a party member dead ahead (a stranger in the cone too) -> locked, carried in re-aimed ballistic bounds, arrival heal
    setup24()
    t0_ = T22[0]
    SO.store(cu, JDouble(30.0), JDouble(1000.0), 2, JLong(0), JLong(T22[0]))          # 30 HP stored by Bindings
    hpmax24 = float(mp.get(HP).getMax())
    rm2_, w2_ = cast24(5010)
    a_st = ws24()
    al24f = {"locked": None if a_st is None or a_st.ally is None else int(a_st.ally.getIndex()), "most": None if a_st is None else int(a_st.most),
             "first": w2_, "why": str(WG.LAST_WHY)}
    step24 = 24.0 * 0.35
    at20(rc, 0.5 + step24, 64.0, 0.5)
    b2_ = tick24(4, 100)
    at20(rc, 0.5 + 2 * step24, 64.0, 0.5)          # 3.2 from the ally: not yet arrived
    b3_ = tick24(4, 100)
    at20(rc, 18.0, 64.0, 0.5)                       # 2.5 from the ally: arrived
    b4_ = tick24(1, 100)
    al24f["bounds"] = [x_ for x_ in b2_ + b3_ + b4_ if x_]
    al24f["ticks"] = [len(x_) for x_ in b2_ + b3_ + b4_]
    al24f["end"] = (ws24() is None, str(WG.LAST_END), round(float(WG.LAST_BASE), 4), round(float(WG.LAST_STORED), 4), round(float(WG.LAST_HEAL), 4))
    al24f["ally hp"] = sv(mp, HP)
    al24f["pool"] = (round(float(SO.poolNow(cu, T22[0])), 4), br.get("armory:soul:" + str(cu)) is None)
    al24f["xp"] = list(XP24)
    al24f["dash"] = [bool(w_[1]) for w_ in instrs19(rc)]
    vy24 = round(0.5 * G24 * 0.35, 4)
    base24 = round(hpmax24 * 0.12, 4)
    check(al24f["locked"] == int(rp.getIndex()) and al24f["most"] == 8 and al24f["why"] == "locked on p2" and len(al24f["first"]) == 1
          and near24(al24f["first"][0], (24.0, vy24, 0.0)) and al24f["ticks"] == [0, 0, 0, 1, 0, 0, 0, 1, 0]
          and near24(al24f["bounds"][0][0], (24.0, vy24, 0.0)) and near24(al24f["bounds"][1][0], (3.2 / 0.35, vy24, 0.0))
          and al24f["end"] == (True, "arrived", base24, 30.0, round(base24 + 30.0, 4)) and al24f["ally hp"] == round(50.0 + base24 + 30.0, 3)
          and al24f["pool"] == (0.0, True) and al24f["xp"] == [(str(cu), round(base24 + 30.0, 4), "armory:wings", str(cu))] and al24f["dash"] == [False, False, False],
          "R24f (Priest.md: 'if an ally is that way, it locks on and carries you to them'; 'arriving heals the ally: a base heal + all the stored "
          "soul healing'): the PARTY MEMBER dead ahead is locked (the stranger in the cone is not: you are in a party), 8 bounds at most; each bound "
          "is ONE plain Set (the Monk vault's) re-aimed at them, ballistic (lands on the aim point after 0.35 s: 24 b/s + %s up; the last one short: 9.14), none in between; "
          "within 3 blocks = ARRIVED: the ally heals base 12 %% (Iron: 10 + 2 tiers) = %s + ALL 30 stored = %s, the pool EMPTIED (armory:soul gone), "
          "Divinity XP through skill:fn:healxp ('armory:wings'): %s" % (vy24, base24, base24 + 30.0, json.dumps(al24f, default=str)))
    # (3) the heal cap + nothing stored + the tier step
    hc24 = {}
    for nm_, item_, stored_, hp0_ in (("Iron, 80 stored (cap 60 %)", IRON22, 80.0, 10.0), ("Onyxium, nothing stored (17 %)", SOUL19_IDS[7], 0.0, 10.0),
                                     ("Soul Orb, nothing stored (10 %)", SOUL19_IDS[0], 0.0, 10.0), ("Iron, ally nearly full", IRON22, 30.0, 95.0)):
        setup24(item=item_)
        mp.setStatValue(HP, JFloat(hp0_))
        if stored_ > 0:
            SO.store(cu, JDouble(stored_), JDouble(1000.0), 2, JLong(0), JLong(T22[0]))
        cast24(5020 + len(hc24))
        at20(rc, 18.0, 64.0, 0.5)
        tick24(1, 100)
        hc24[nm_] = (str(WG.LAST_END), round(float(WG.LAST_BASE), 3), round(float(WG.LAST_STORED), 3), round(float(WG.LAST_HEAL), 3), sv(mp, HP),
                     round(float(SO.poolNow(cu, T22[0])), 3))
    check(hc24["Iron, 80 stored (cap 60 %)"] == ("arrived", round(hpmax24 * 0.12, 3), 80.0, round(hpmax24 * 0.6, 3), round(10.0 + hpmax24 * 0.6, 3), 0.0)
          and hc24["Onyxium, nothing stored (17 %)"][1:4] == (round(hpmax24 * 0.17, 3), 0.0, round(hpmax24 * 0.17, 3))
          and hc24["Soul Orb, nothing stored (10 %)"][1:4] == (round(hpmax24 * 0.10, 3), 0.0, round(hpmax24 * 0.10, 3))
          and hc24["Iron, ally nearly full"][3:6] == (round(hpmax24 - 95.0, 3), round(hpmax24, 3), 0.0),
          "R24f: the arrival heal - base 10 %% + 1 %% a tier of the ALLY's max Health (%s) even with nothing stored (Orb 10 %%, Onyxium 17 %%), plus ALL "
          "the stored healing, at most wings.healCap 60 %% (80 stored on Iron -> 60 %%, the pool still EMPTIES); never above the room: %s" % (hpmax24, json.dumps(hc24)))
    # (4) WHO IS AN ALLY: no party = any player; in a party = members only; the cone, the reach, a wall, a dead player, wings.anyPlayer off
    lk24 = {}

    def lock_case(nm_, pre_, near_=None, walls=()):
        setup24(walls=walls)
        if near_ is not None:
            NEAR22[:] = near_
        pre_()
        cast24(5040 + len(lk24))
        s_ = ws24()
        lk24[nm_] = None if s_ is None or s_.ally is None else int(s_.ally.getIndex())
        if s_ is not None:
            WG.STATES.clear()
    lock_case("party member ahead", lambda: None)
    lock_case("stranger ahead, you in a party", lambda: at20(rp, -20.0, 64.0, 0.5))
    lock_case("no party: any player", lambda: (br.remove("party:fn:members"), at20(rp, -20.0, 64.0, 0.5)))
    lock_case("no party, wings.anyPlayer off", lambda: (br.remove("party:fn:members"), at20(rp, -20.0, 64.0, 0.5), setattr(ACfg, "WINGS_ANY", False)))
    lock_case("member 45 degrees off (cone 30)", lambda: at20(rp, 10.5, 64.0, 10.5), near_=[rc, rp])
    lock_case("member 35 blocks away (reach 30)", lambda: at20(rp, 35.5, 64.0, 0.5), near_=[rc, rp])
    lock_case("member behind a wall", lambda: None, near_=[rc, rp], walls=[WALL22])
    lock_case("member dead", lambda: put(rp, DTHc.getComponentType(), U.allocateInstance(DTHc.class_)), near_=[rc, rp])
    lock_case("mob ahead (never a mob)", lambda: None, near_=[rc, mob(4960, 10.0, 64.0, 0.5, BOX22)])
    check(lk24 == {"party member ahead": int(rp.getIndex()), "stranger ahead, you in a party": None, "no party: any player": int(rs.getIndex()),
                   "no party, wings.anyPlayer off": None, "member 45 degrees off (cone 30)": None, "member 35 blocks away (reach 30)": None,
                   "member behind a wall": None, "member dead": None, "mob ahead (never a mob)": None},
          "R24f WHO (Skyy 'ally' = party member / player): in a party only its members are locked; with no party any player is (wings.anyPlayer; "
          "off = none); never outside the 30-degree cone, past 30 blocks, behind a wall, a dead player or a mob - each of those = a plain glide: %s" % json.dumps(lk24))
    # (5) A DAMAGING FALL IS KEPT on every bound (the wand / bow rule; no void protection either)
    fk24 = {}
    for nm_, cvy_, ally_ in (("glide, falling 30", -30.0, False), ("glide, falling 10", -10.0, False), ("to the ally, falling 30", -30.0, True)):
        setup24(cvy=cvy_)
        if not ally_:
            NEAR22[:] = [rc]
        k0_ = int(WG.KEPT)
        fk24[nm_] = (cast24(5060 + len(fk24))[1], int(WG.KEPT) - k0_)
    check(near24(fk24["glide, falling 30"][0][0], (18.0, -30.0, 0.0)) and fk24["glide, falling 30"][1] == 1
          and near24(fk24["glide, falling 10"][0][0], (18.0, 4.0, 0.0)) and fk24["glide, falling 10"][1] == 0
          and near24(fk24["to the ally, falling 30"][0][0], (24.0, -30.0, 0.0)) and fk24["to the ally, falling 30"][1] == 1,
          "R24f (the wand rule): a bound made while falling faster than MinFallSpeedToEngageRoll (21) KEEPS the fall (vertical -30, sideways the bound) "
          "- no fall-damage escape; a slow fall (10) gets the full bound: %s" % json.dumps(fk24))
    # (6) REFUSED = nothing paid, nothing pushed: class lock, no soul weapon, too little Mana / Stamina, already flying, wings.enabled off, dead
    rf24 = {}

    def refuse_case(nm_, pre_, mana=200.0, stam=20.0, post=None):
        setup24(mana=mana, stam=stam)
        NEAR22[:] = [rc]
        pre_()
        m0_, s0_ = sv(mc, MANA), sv(mc, STAM)
        rm_, w_ = cast24(5080 + len(rf24))
        rf24[nm_] = (rm_, len(w_), round(m0_ - sv(mc, MANA), 3), round(s0_ - sv(mc, STAM), 3), str(WG.LAST_WHY))
        if post is not None:
            post()
    refuse_case("class lock", lambda: br.put("class:fn:allowed", Deny22()), post=lambda: br.remove("class:fn:allowed"))
    refuse_case("a wand in hand", lambda: HAND22.put(cu, "Weapon_Wand_Iron"))
    refuse_case("5 Mana", lambda: None, mana=5.0)
    refuse_case("2 Stamina", lambda: None, stam=2.0)
    refuse_case("wings.enabled off", lambda: setattr(ACfg, "WINGS_ON", False))
    refuse_case("dead", lambda: put(rc, DTHc.getComponentType(), U.allocateInstance(DTHc.class_)), post=lambda: put(rc, DTHc.getComponentType(), None))
    setup24()
    NEAR22[:] = [rc]
    cast24(5095)
    m0_ = sv(mc, MANA)
    rm_, w_ = cast24(5096)
    rf24["already flying"] = (rm_, len(w_), round(m0_ - sv(mc, MANA), 3), 0.0, str(WG.LAST_WHY))
    check(rf24 == {"class lock": (True, 0, 0.0, 0.0, "class lock"), "a wand in hand": (True, 0, 0.0, 0.0, "no soul weapon in hand"),
                   "5 Mana": (True, 0, 0.0, 0.0, "too little Stamina or Mana"), "2 Stamina": (True, 0, 0.0, 0.0, "too little Stamina or Mana"),
                   "wings.enabled off": (True, 0, 0.0, 0.0, "Wings of Fate off"), "dead": (True, 0, 0.0, 0.0, "dead or mounted"),
                   "already flying": (True, 0, 0.0, 0.0, "already flying")},
          "R24f REFUSALS (Priest only, the class lock): SkyyClasses says no / no soul weapon in hand / 5 Mana (20 needed) / 2 Stamina (10 needed) / "
          "wings.enabled off / dead / a second cast while flying = the marker still goes, NOTHING pushed, NOTHING paid: %s" % json.dumps(rf24))
    # (7) THE ENDS: the ally not reached (all 8 bounds, you never got closer = a REFUND: it did not move you), the ally gone / too far, death,
    # world change
    en24 = {}
    setup24()
    m0_, s0_ = sv(mc, MANA), sv(mc, STAM)
    cast24(5100)
    tk_ = tick24(50, 100)          # 8 bounds (the last at 2.8 s) + 1 s
    en24["not reached"] = (sum(len(x_) for x_ in tk_) + 1, str(WG.LAST_END), ws24() is None, round(m0_ - sv(mc, MANA), 3), round(s0_ - sv(mc, STAM), 3))
    for nm_, act_, store_ in (("the ally is gone", lambda: put(rp, DTHc.getComponentType(), U.allocateInstance(DTHc.class_)), None),
                              ("the ally is too far", lambda: at20(rp, 120.5, 64.0, 0.5), None),
                              ("death", lambda: put(rc, DTHc.getComponentType(), U.allocateInstance(DTHc.class_)), None),
                              ("world change", lambda: None, tst2)):
        setup24()
        cast24(5110 + len(en24))
        at20(rc, 3.0, 64.0, 0.5)          # moved: no refund
        act_()
        tick24(1, 100, store=store_)
        en24[nm_] = (str(WG.LAST_END), ws24() is None)
        put(rc, DTHc.getComponentType(), None)
    check(en24["not reached"] == (8, "the ally was not reached", True, 0.0, 0.0) and en24["the ally is gone"] == ("the ally is gone", True)
          and en24["the ally is too far"] == ("the ally is too far", True) and en24["death"] == ("death", True) and en24["world change"] == ("world change", True),
          "R24f ENDS: all 8 bounds without reaching the ally = 'not reached' 1 s after the last - and since it never moved you (a wall in the "
          "way) the 20 Mana + 10 Stamina come BACK (LOCKED 2026-10-05); the ally dead / 120 blocks away, your death, a world change end it at once: %s" % json.dumps(en24))
    # (7b) a player who left mid-flight never ticks: the sweep (any tick, every 5 s) drops a flight idle for 15 s, keeps a live one
    setup24()
    NEAR22[:] = [rc]
    cast24(5130)
    old_ = ws24()
    clk22(16000)
    sw_a = int(WG.sweep(JLong(T22[0])))
    sw_b = ws24() is None
    cast24(5131)
    sw_c = (int(WG.sweep(JLong(T22[0] + 1000))), ws24() is not None)
    WG.STATES.clear()
    check(old_ is not None and sw_a == 1 and sw_b and sw_c == (0, True),
          "R24f SWEEP: a flight whose player stopped ticking 16 s ago is dropped (no state left behind); a 1-second-old one is kept: %s %s %s" % (sw_a, sw_b, sw_c))
    # (8) THE INPUT CHAIN: RootInteraction.build() of SkyyArmory_Soul_Wings = the Charging -> tap Simple / the marker launch (the real store)
    rres24 = compile_root("SkyyArmory_Soul_Wings")
    ops24 = [c_ for c_, i_ in rres24["ops"]]
    check(not rres24["bad"] and ops24[:1] == ["ChargingInteraction"] and "LaunchProjectileInteraction" in ops24,
          "R24f INPUT: RootInteraction.build() of the Wings root on the real stores = Charging -> (tap) Simple / (0.35 s hold) LaunchProjectile of "
          "the marker - no missing interaction: %s %s" % (ops24, rres24["bad"][:2]))
    # (9) FIX (review, LOW): THE PROFILE - the cast keeps its profile: a switch mid-flight ENDS it; the XP carries the cast's profile key
    @JImplements("java.util.function.Function")
    class Pk24:
        @JOverride
        def apply(self, o):
            return str(o) + "-p2"
    pf24 = {}
    setup24()
    NEAR22[:] = [rc]
    br.put("profile:epoch:" + str(cu), "e1-24")
    br.put("profile:fn:key", Pk24())
    cast24(5140)
    s_ = ws24()
    pf24["cast"] = (s_ is not None, None if s_ is None else str(s_.pk))
    tick24(1, 100)
    pf24["same profile"] = ws24() is not None
    br.put("profile:epoch:" + str(cu), "e2-24")
    tick24(1, 100)
    pf24["switched"] = (ws24() is None, str(WG.LAST_END))
    setup24()
    br.put("profile:fn:key", Pk24())
    cast24(5141)
    at20(rc, 18.0, 64.0, 0.5)
    tick24(1, 100)
    pf24["arrival xp"] = (str(WG.LAST_END), [x_[3] for x_ in XP24])
    br.remove("profile:epoch:" + str(cu))
    br.remove("profile:fn:key")
    check(pf24 == {"cast": (True, str(cu) + "-p2"), "same profile": True, "switched": (True, "profile switch"),
                   "arrival xp": ("arrived", [str(cu) + "-p2"])},
          "R24f PROFILE (FIX, review LOW 'Wings of Fate is not tied to a profile'): the cast keeps its profile (ArmoryTree.gen + the pkey); the "
          "same profile flies on, a profile switch (profile:epoch moves) ENDS the flight at once (no heal for profile B); an arrival's Divinity "
          "XP goes through skill:fn:healxp WITH the cast's profile key (SkyySkills refuses it after a switch): %s" % json.dumps(pf24))
    # (10) FIX (review, LOW): A STUCK FLIGHT - no velocity component (a bound can never be made): 5 failed bounds in a row END it and, since it
    # did not move you, the 20 Mana + 10 Stamina come back; never "already flying" forever
    setup24()
    NEAR22[:] = [rc]
    put(rc, VELc.getComponentType(), None)
    m0_, s0_ = sv(mc, MANA), sv(mc, STAM)
    WG.CLOCK = JLong(T22[0])
    mk_, pc_ = launched(WMARK24, 5150, 0.5, 65.5, 0.5)
    AT.added(mk_, pc_, int(ADefs.pidCode(WMARK24)), tst, tbuf)
    s_ = ws24()
    sk24 = {"cast": (s_ is not None, None if s_ is None else int(s_.fails)), "paid": (round(m0_ - sv(mc, MANA), 3), round(s0_ - sv(mc, STAM), 3))}
    live_ = []
    for k_ in range(6):
        clk22(100)
        WG.CLOCK = JLong(T22[0])
        WG.tickPlayer(rc, tst, tbuf)
        live_.append(ws24() is not None)
    sk24["alive per tick"] = live_
    sk24["end"] = (str(WG.LAST_END), "given back" in str(WG.LAST_WHY))
    sk24["back"] = (round(m0_ - sv(mc, MANA), 3), round(s0_ - sv(mc, STAM), 3))
    put(rc, VELc.getComponentType(), VELc())
    rm_, w_ = cast24(5151)
    sk24["cast again"] = (ws24() is not None, len(w_))
    WG.STATES.clear()
    check(sk24 == {"cast": (True, 1), "paid": (20.0, 10.0), "alive per tick": [True, True, True, False, False, False], "end": ("no bound", True),
                   "back": (0.0, 0.0), "cast again": (True, 1)},
          "R24f STUCK (FIX, review LOW 'a stuck flight state costs Mana and Stamina with no refund'): a flight whose bounds cannot be made (the "
          "cast's bound + 4 more failed in a row = 5) ENDS ('no bound') and - it never moved you - the 20 Mana + 10 Stamina come BACK; the next "
          "cast works: %s" % json.dumps(sk24))
    br.remove("skill:fn:healxp")
    if keep_party24 is not None:
        br.put("party:fn:members", keep_party24)
    else:
        br.remove("party:fn:members")
    if keep_pk24 is not None:
        br.put("profile:fn:key", keep_pk24)
    WG.STATES.clear()
    WG.CLOCK = JLong(0)

    # R24g vs the 0.1.20 jar METHOD BY METHOD: only the planned methods / fields
    MN24, MO24 = methods_of(JAR), methods_of(OLD120)
    cmp24 = {}
    for c_ in sorted(set(MN24) | set(MO24)):
        if c_ not in MN24 or c_ not in MO24:
            cmp24[c_] = "only in " + ("0.1.21" if c_ in MN24 else "0.1.20")
            continue
        ch_ = sorted(k_ for k_ in set(MN24[c_][0]) | set(MO24[c_][0]) if MN24[c_][0].get(k_) != MO24[c_][0].get(k_))
        fd_ = sorted(set(MN24[c_][1]) ^ set(MO24[c_][1]))
        if ch_ or fd_:
            cmp24[c_] = {"methods": sorted(set(k_.split("(")[0] for k_ in ch_)), "fields": sorted(set(f_.split(":")[0] for f_ in fd_))}
    plan24 = {"Soul": ({"dps", "line", "step", "want", "alloc", "share", "flick", "takeAll"}, {"SOLID_GAP", "WISP_GAP", "DOTS"}),
              "SoulState": ({"<init>"}, {"draws"}),
              "ArmoryCfg": ({"apply", "load", "reloadAll", "useDefaults", "soulText", "<clinit>", "retired", "tab", "m21Key", "m21Val", "m21Update", "m21Log", "migrate021"},
                            {"SOUL_DPM", "SOUL_MULT", "SOUL_MULT_DEF", "SOUL_DPS", "SOUL_DPS_DEF", "WINGS_ON", "WINGS_MA", "WINGS_ST", "WINGS_SPEED",
                             "WINGS_BOUND", "WINGS_BOUNDS", "WINGS_ABOUNDS", "WINGS_ASPEED", "WINGS_LIFT", "WINGS_RANGE", "WINGS_CONE", "WINGS_ARRIVE",
                             "WINGS_BASE", "WINGS_PER", "WINGS_CAP", "WINGS_ANY", "M21_KEYS", "M21_OLD", "M21_NEW", "M21_RET_KEYS", "M21_RET_OLD",
                             "M21_MARK", "M21_MARK_ID", "M21_WHO", "M21_LAST"}),
              "ArmoryDefs": ({"pids", "<clinit>"}, {"SOUL_WPS", "PS_WINGS", "WINGS_MARK", "WINGS_CODE"}),
              "ArmoryHooks": ({"checkEssence", "<clinit>"}, set()), "ArmoryTrav": ({"added"}, set()), "TravTick": ({"tick"}, set()),
              "SkyyArmoryPlugin": ({"setup", "unpublish", "<clinit>"}, set()), "CfgRows": ({"<clinit>"}, set()), "ArmoryCheck": ({"<clinit>"}, set())}
    bad24g = {}
    for c_, v_ in cmp24.items():
        if c_ in ("Wings", "WingsState") and v_ == "only in 0.1.21":
            continue
        if c_ in plan24 and isinstance(v_, dict) and set(v_["methods"]) <= plan24[c_][0] and set(v_["fields"]) <= plan24[c_][1]:
            continue
        bad24g[c_] = v_
    check(not bad24g and cmp24.get("Wings") == "only in 0.1.21" and cmp24.get("WingsState") == "only in 0.1.21"
          and "added" in cmp24.get("ArmoryTrav", {}).get("methods", []) and "tick" in cmp24.get("TravTick", {}).get("methods", []),
          "R24g: 0.1.20 -> 0.1.21 METHOD BY METHOD - only the planned methods / fields differ (Wings + WingsState new; Soul's damage / line / "
          "budget / takeAll; the rows + soulText; Defs + pids; checkEssence; ArmoryTrav.added's marker; TravTick's tick; the plugin's setup / "
          "unpublish): %s" % json.dumps(bad24g)[:1500])
    print("R24g. vs 0.1.20 method by method: %s" % json.dumps(cmp24)[:2000])
    # the balance numbers (the Class Balance chart) + the in-game numbers
    print("R24. balance (0.1.21 defaults, before SkyyGear levels): " + " | ".join(
        "%s: %d Bindings x %s dmg/s = %s dmg/s, %s Mana/s (%s dmg per Mana), solid %s s, Wings heal %d%% + stored (cap 60%%)" % (
            m_, n_, d_, n_ * d_, round(n_ * p_, 2), round(d_ / p_, 2), s_, 10 + t_) for t_, (m_, n_, d_, p_, s_) in enumerate(zip(
                SOUL19_TIERS, [1, 2, 4, 6, 10, 14, 16, 20], [5, 7, 10, 15, 20, 30, 40, 55], [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35],
                [1.75, 1.6, 1.45, 1.35, 1.2, 1.1, 1.05, 1.0]))))
    SO.HELD = None
    SO.CLOCK = JLong(0)
    SO.STATES.clear()
    SO.POOL.clear()
    AT.NEAR, AT.GRID, LP.HAND, LP.LOOK = keep22
    AT.PSEEN = None
    br.remove("skill:fn:regenblock")
    ACfg.useDefaults()
    TW.ALL.clear()
    reset_buf()
    put(rc, DTHc.getComponentType(), None)
    put(rc, VELc.getComponentType(), VELc())
    at20(rc, 0.5, 64.0, 0.5)
    at20(rp, 2.5, 64.0, 0.5)
    at20(rs, 3.5, 64.0, 0.5)
    put(rp, DTHc.getComponentType(), None)
    mc.setStatValue(MANA, JFloat(200.0))
    mc.setStatValue(STAM, JFloat(10.0))
    mp.setStatValue(HP, JFloat(50.0))
    ms.setStatValue(HP, JFloat(50.0))
    print("R24. 0.1.21 soul orb round: rows + tables, damage a second per tier (real pulse), the faster tether per tier, wispy vs solid lines + "
          "the budget, the vanilla essence table, Wings of Fate (glide, ally lock + carry + heal, the cap, who is an ally, the kept fall, every "
          "refusal, every end + the refund, the real input chain), the 0.1.20 compare")
'''
hrep('''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''',
     R24 + '''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''')

out_t = ts.replace(LF, TNL)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(out_t)
print("wrote %s" % os.path.relpath(TDST, ROOT))
