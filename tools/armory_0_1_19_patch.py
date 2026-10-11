"""Derive SkyyArmory/build_skyyarmory_0.1.19.py (+ its harness SkyyArmory/test_skyyarmory_0.1.19.py) from the GENERATED 0.1.18
(SkyyArmory/build_skyyarmory_0.1.18.py = the tools/deploy_set.py SET pin, made by tools/armory_0_1_18_patch.py; test_skyyarmory_0.1.18.py =
its harness). Every anchor is asserted (rep = exactly one hit). Edit THIS file, never the generated scripts.
Run:  python tools/armory_0_1_19_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.19.py   then
      python SkyyArmory/test_skyyarmory_0.1.19.py --dir tools/dev/scratch/<task>/harness      (never --deploy)
Partner: SkyySkills 0.4.30 (tools/skills_0_4_30_patch.py) adds the regen-block bridge skill:fn:regenblock this build calls (without it the
Bindings still work, but SkyySkills keeps refilling Mana while you bind - the build says so in its start line).

0.1.19 = THE SOUL ORB / SOUL CAGES (the Priest's second weapon; Skyy asked "when will the soul cage weapon be ready?" 2026-10-10).
Design (Skyy's lines win): research/classes/Priest.md "Soul Orb ladder" + "How soul Bindings work" (LOCKED 2026-10-04 / 2026-10-07),
docs/answered/classes.md (soul tether + Mana Steal 2026-10-04, Bindings through walls 2026-10-07, the Element ladder 2026-10-10),
research/cloud/Soul-Orb-Spec.md (the paper numbers). Art: models-local/art/soulcage (approved 2026-10-06 v2) - its generator
tools/art/make_soulcage.py is CALLED AT BUILD TIME (the vanilla-derived bytes only in the jar, like every SkyyArmory art).
  THE ITEMS (8, Priest only): Weapon_Wand_SoulOrb (Soul Orb, blue, 1 Binding, 1.0x) -> Weapon_Wand_SoulCage_<Metal>: Copper (Life Essence,
    green, 2, 1.1x) -> Iron (Fire, red, 4, 1.1x) -> Thorium (Earth, amber, 6, 1.5x) -> Cobalt (Frost = the vanilla Ice Essence, cyan, 10,
    1.5x) -> Adamantite (Storm = the vanilla Lightning Essence, yellow, 14, 2.0x) -> Mithril (Void, purple, 16, 2.0x) -> Onyxium (Light,
    white-gold, 20, 2.5x). THE CLASS LOCK: the ids start with Weapon_Wand_ = SkyyClasses' Priest prefix (the same lock as the wands; SkyyClasses
    unchanged) and the Java asks class:fn:allowed before a hold binds anything. Recipes at the Weapon Bench (the wand's tab + tier): the Soul
    Orb = 20 Life Essence + 1 Blue Crystal + 4 Sticks + 1 Plant Fibre (Soul-Orb-Spec 1); every cage = the tier before + that metal's bars (the
    metal wand's bar count) + its essence (15 / 15 / 15 / 12 / 12 / 10 / 10).
  THE ESSENCES: Life, Fire, Ice (Frost), Lightning (Storm) and Void are the VANILLA essences (same names / colours, SkyyCollections already
    counts them); Earth (amber) and Light (white-gold) are NEW items SkyyArmory_Essence_Earth / SkyyArmory_Essence_Light (recoloured vanilla
    essence art, made at build time). EXTRA DROPS (SoulDropSys): a monster a player kills drops its zone's essence by chance (Server Setup
    table): Life Zone 1, Fire the vanilla volcanic caves (any zone), Earth Zone 2, Frost Zone 3, Storm Zone 4; Void + Light have no zone yet
    (Zones 5+ do not exist) = Zone 4 at a lower chance (the nearest equivalent; a row moves them). Zone = the mob's spawn environment
    (Env_Zone<N>_...; volcanic = *Caves_Volcanic*), else SkyyMobs' level (mob:fn:level) in the zone bands 1-20 / 21-30 / 31-45 / 46+.
    Hostile / neutral mobs only, once per death, never for Creative players.
  THE BINDINGS (hold right click; a Charging Secondary root the server watches through the player's InteractionManager chains - the same
    test the vanilla ChargingCondition runs): every enemy MOB (never a player, never a friendly / protected mob) within soul.lockRadius (3)
    of the look point (the mob nearest your crosshair within soul.aimCone, else the block you look at; soul.lockRange 25) gets a Binding at
    once, up to the tier's cap; LINE OF SIGHT is needed to START one, never to keep it. Damage starts at once. A Binding is WISPY until you
    have looked at it for the tier's stabilize time (2.5 s Soul Orb .. 1.5 s Mithril / Onyxium); looking away longer than soul.wispyGrace
    (0.4 s) before that snaps it; once SOLID you may look away and bind the next group (up to the cap). Held while you hold right click and
    your Mana lasts. Every soul.tick (0.5 s): each Binding drains soul.manaPerSecond (1.00 .. 1.35 Mana a second, ~flat) and deals
    soul.damagePerMana (2) x that x the tier multiple per second through the WHOLE damage pipeline (Damage$EntitySource(you): SkyyGear's
    level scaling, crits and MANA STEAL apply like any wand-in-hand hit); soul.storePercent (50) of it is STORED as bonus healing on the
    Priest (capped at the tier's % of the Priest's max Health; decays soul.decayPercent 2 %/s after you let go; reset on death and profile
    switch) - published as armory:soul:<uuid> (Double HP) + armory:fn:soul (get / take) for Sacred Heal / Wings of Fate (nothing reads it yet).
    NO NATURAL MANA REGEN while any Binding is active: skill:fn:regenblock (SkyySkills 0.4.30) is renewed every pulse and cleared at the end.
    RELEASE: let go of right click, Mana runs out (not enough for the next pulse = all Bindings end, nothing dealt), death, world change,
    profile switch, the soul weapon leaves your hand, soul.enabled off; a Binding alone ends when its mob dies or is farther than
    soul.snapRange (30). Nothing is dealt after a release. Looks: a particle line per Binding in the tier colour (8 finite systems, the
    heal-orb ring recoloured; no vanilla point-to-point beam exists - the vanilla Beam_* systems are fixed-size spell effects): wispy =
    sparse dots, solid = a dense line; at most 48 dots a draw for all of one player's lines (20 Onyxium lines = 2 dots each). The root is a
    Charging with AllowIndefiniteHold and DisplayProgress off (the vanilla Watering Can's hold-to-keep-going shape, no charge bar); the
    look point is re-read every 0.1 s. Wings of Fate (the charged traversal) is NOT in this build.
  SETTINGS (Server Setup > Armory > "Soul Orb + essences"; the "Staffs (fixed)" rows moved into "Wand + staff (fixed)" - the kit has 16
    categories): soul.enabled, soul.damagePerMana, soul.tick, soul.lockRadius, soul.lockRange, soul.snapRange, soul.aimCone,
    soul.wispyGrace, soul.storePercent, soul.decayPercent, soul.noRegen, soul.lineDots, essence.drops + the tables soul.bindings / soul.manaPerSecond /
    soul.damageMult / soul.stabilize / soul.storeCap (per tier) and essence.chance / essence.zone (per essence) + 1 read-only row.
FIX ROUND (critics 2026-10-10): an out-of-Mana release LATCHES the hold (no new Bindings until right click is let go - no bind / fail loop);
  an unreadable Mana stat ends the Bindings (never free hits); a sweep every 5 s drops the Bindings, stored healing, armory:soul:<uuid> and
  latch of a player not ticked for 30 s (left the game); the dot budget is the row soul.lineDots (48; 0 = no lines) and every soul dot
  system emits 0.25 s = one re-draw (the ring copy emitted 0.5 s = two overlapping systems); the 5 rows the tooltip numbers come from say
  "Tooltips show defaults." (the item descriptions are baked at build time). Harness R22p runs each fix.
FIX ROUND 2 (critics 2026-10-10): the look point tests the aim cone BEFORE any ray-cast (only cone mobs are ray-cast, nearest the crosshair
  first - the same pick); no look scan while the cap is full and every Binding is solid; ArmoryTree.gen only for a player with soul state (a
  new hold reads it at its start); a let-go made with another item in hand clears the out-of-Mana latch; the soul.damagePerMana help says
  2 = 0.08 x the Wood wand charged shot (25) = Soul-Orb-Spec 2.1; the essence.zone help names the fixed level bands. Harness R22q.
No saved data beyond config.properties (new keys only - a missing key reads its default), no migration, no new command.
ROLLBACK: 0.1.18 does not know the 10 new item ids (Soul Orb / Cages / Earth / Light Essence become unknown items) - roll back only before
anyone crafted one (FLOOR once they exist).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.18.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.19.py")
TSRC = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.18.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.19.py")

CR, LF = chr(13), chr(10)
raw = open(SRC, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.18"\nMOD = "SkyyArmory"' in s and "0.1.18 = THE WAND LAUNCH" in s, "build_skyyarmory_0.1.18.py is not the 0.1.18 pin"
assert "SoulCage" not in s and "Soul.tickPlayer" not in s and "soul.enabled" not in s, "0.1.18 already has the 0.1.19 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:140])
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyArmory 0.1.18 - build script (javassist via jpype). GENERATED by tools/armory_0_1_18_patch.py from the GENERATED 0.1.17 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.18.py -> SkyyArmory/SkyyArmory-0.1.18.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.18.py --dir tools/dev/scratch/<task>/harness.
''', '''"""SkyyArmory 0.1.19 - build script (javassist via jpype). GENERATED by tools/armory_0_1_19_patch.py from the GENERATED 0.1.18 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.19.py -> SkyyArmory/SkyyArmory-0.1.19.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.19.py --dir tools/dev/scratch/<task>/harness.

0.1.19 = THE SOUL ORB / SOUL CAGES (the Priest's second weapon; Skyy 2026-10-10 "when will the soul cage weapon be ready?"; full notes in
tools/armory_0_1_19_patch.py): 8 Priest items Weapon_Wand_SoulOrb + Weapon_Wand_SoulCage_<Copper..Onyxium> (art: tools/art/make_soulcage.py
at build time, the soul / gems in the 2026-10-10 element colours), each crafted from the one before + bars + its essence; 2 new essences
(SkyyArmory_Essence_Earth / _Light) + extra zone essence drops (SoulDropSys); HOLD RIGHT CLICK = soul Bindings (Soul + SoulState + SoulBind,
TravTick): every enemy mob near the look point up to the tier cap (1 / 2 / 4 / 6 / 10 / 14 / 16 / 20), line of sight to start, wispy ->
solid after 2.5 .. 1.5 s of looking, then look away; steady damage for a steady Mana drain per Binding, 50 % stored as healing
(armory:soul:<uuid>, armory:fn:soul), no Mana regen while bound (skill:fn:regenblock, SkyySkills 0.4.30), released on let go / no Mana /
death / world change / profile switch. Server Setup > Armory > Soul Orb + essences.

0.1.18 (the base, everything below is still true unless 0.1.19 above says otherwise):
''')
rep('VERSION = "0.1.18"\nMOD = "SkyyArmory"', 'VERSION = "0.1.19"\nMOD = "SkyyArmory"')

# ---------------------------------------------------------------------------------------------------------------- rows (Server Setup)
CFG_SOUL_PY = r'''# ================================================================= 0.1.19 THE SOUL ORB / SOUL CAGES (Skyy 2026-10-10 "when will the soul cage weapon be ready?")
SOUL_TIERS = ["Orb", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]          # the ladder (Priest.md "Soul Orb ladder")
SOUL_N = [1, 2, 4, 6, 10, 14, 16, 20]                    # Bindings (LOCKED; Adamantite+ proposed and kept)
SOUL_MULT = [1.0, 1.1, 1.1, 1.5, 1.5, 2.0, 2.0, 2.5]     # damage per Mana x (LOCKED / proposed)
SOUL_MPS = [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35]  # Mana per Binding per second (Skyy: "about the same, a few small steps"; spec 2)
SOUL_STAB = [2.5, 2.3, 2.1, 1.9, 1.7, 1.6, 1.5, 1.5]     # stabilize seconds (Skyy: 1.5-2.5 s, higher tiers faster; spec 2)
SOUL_CAP = [10, 15, 20, 30, 40, 50, 55, 60]              # stored-heal cap, % of max Health (spec 2: never above the 60 % single-heal cap)
ESS_NAMES = ["Life", "Fire", "Earth", "Frost", "Storm", "Void", "Light"]          # Skyy 2026-10-10 Element ladder (+ Life / Fire, 2026-10-04)
ESS_PCT = [8.0, 10.0, 8.0, 8.0, 8.0, 5.0, 3.0]           # % per kill of a monster of that essence's zone
ESS_ZONE = [1, 0, 2, 3, 4, 4, 4]                         # 0 = the vanilla volcanic caves (deep-cave mobs, any zone); Void + Light: no zone 5+ yet
_SO = "soul"          # NEW category "Soul Orb + essences" (the 16th: the fixed staff rows moved into "Wand + staff (fixed)")
CFG_SOUL = [
    ('soul.enabled', 'Soul Bindings (hold right click)', _SO, 'bool', 'true', '', '', '', '', 'live,part,danger', 'Off = holding right click with a Soul Orb / Cage does nothing.', 'SOUL_ON', 'boolean', 'true', 'Soul Orb / Soul Cage Bindings (hold right click). Off = nothing happens.'),
    ('soul.damagePerMana', 'Binding damage per Mana', _SO, 'dec', '2', '0', '50', '', '', 'live', 'Damage per Mana a Binding drains, x the tier multiple (before levels). Tooltips show defaults.', 'SOUL_DPM', 'double', '2', 'Soul Bindings: damage per Mana drained (x the tier multiple below; before SkyyGear levels). 2 = 0.08 x the Wood wand charged shot (25 damage) per Mana (Soul-Orb-Spec 2.1).'),
    ('soul.tick', 'Binding pulse (s)', _SO, 'dec', '0.5', '0.1', '2', '', 's', 'live', 'How often Bindings drain Mana and hit (the per-second numbers stay the same).', 'SOUL_TICK', 'double', '0.5', 'Soul Bindings: seconds between two drains / hits (the per-second numbers do not change).'),
    ('soul.lockRadius', 'Binding radius (blocks)', _SO, 'dec', '3', '0.5', '8', '', 'blocks', 'live', 'Every enemy this close to where you look gets a Binding (up to the cap).', 'SOUL_RADIUS', 'double', '3', 'Soul Bindings: every enemy within this many blocks of the look point gets a Binding at once (up to the tier cap).'),
    ('soul.lockRange', 'Binding reach (blocks)', _SO, 'int', '25', '4', '64', '', 'blocks', 'live', 'How far you can look to start Bindings.', 'SOUL_RANGE', 'int', '25', 'Soul Bindings: the look point is at most this far (blocks).'),
    ('soul.snapRange', 'Binding breaks past (blocks)', _SO, 'int', '30', '4', '96', '', 'blocks', 'live', 'A Binding whose mob gets farther than this ends.', 'SOUL_SNAP', 'int', '30', 'Soul Bindings: a Binding ends when its mob is farther than this (blocks).'),
    ('soul.aimCone', 'Binding aim cone (degrees, full)', _SO, 'int', '12', '2', '60', '', '', 'live', 'The mob nearest your crosshair inside this cone sets the look point.', 'SOUL_CONE', 'int', '12', 'Soul Bindings: the enemy nearest your crosshair inside a cone this wide is the look point (none = the block you look at).'),
    ('soul.wispyGrace', 'Wispy Binding look-away grace (s)', _SO, 'dec', '0.4', '0', '3', '', 's', 'live', 'A wispy Binding snaps when you look away longer than this.', 'SOUL_GRACE', 'double', '0.4', 'Soul Bindings: a wispy (not yet solid) Binding snaps when you look away from it longer than this (seconds).'),
    ('soul.storePercent', 'Damage stored as healing (%)', _SO, 'int', '50', '0', '100', 'step=5', '%', 'live', 'This share of Binding damage is stored as bonus healing.', 'SOUL_STORE', 'int', '50', 'Soul Bindings: this % of the damage is stored as bonus healing on the Priest (armory:soul:<uuid>).'),
    ('soul.decayPercent', 'Stored healing fades (% a second)', _SO, 'dec', '2', '0', '20', '', '%', 'live', 'After you let go the stored healing shrinks this % a second.', 'SOUL_DECAY', 'double', '2', 'Soul Bindings: after you let go the stored healing shrinks by this % a second (0 = never).'),
    ('soul.noRegen', 'No Mana regen while binding', _SO, 'bool', 'true', '', '', '', '', 'live', 'Skyy: no natural Mana regen while any Binding holds (Mana Steal still works).', 'SOUL_NOREGEN', 'boolean', 'true', 'Soul Bindings: no natural Mana regen while any Binding holds (needs SkyySkills 0.4.30; Mana Steal still works).'),
    ('soul.lineDots', 'Binding line dots (per player)', _SO, 'int', '48', '0', '96', '', '', 'live', 'At most this many dots for all Binding lines of one Priest at once. 0 = no lines.', 'SOUL_DOTS', 'int', '48', 'Soul Bindings: at most this many particle dots for all Binding lines of one player per draw (4 draws a second; 0 = no lines).'),
    ('essence.drops', 'Zone essence drops', _SO, 'bool', 'true', '', '', '', '', 'live,part,danger', 'Off = monsters drop no extra essences (vanilla drops stay).', 'ESS_ON', 'boolean', 'true', 'Essence drops: a monster a player kills may drop its zone essence (the tables below). Off = none.'),
]
assert len(set(r[0] for r in CFG_SOUL)) == len(CFG_SOUL) == 13 and all(len(r) == 15 and r[2] == _SO for r in CFG_SOUL)
assert all(len(r[1]) <= 40 and len(r[10]) <= 100 for r in CFG_SOUL), [(r[0], len(r[1]), len(r[10])) for r in CFG_SOUL if len(r[1]) > 40 or len(r[10]) > 100]
assert "%" not in "".join(r[13] for r in CFG_SOUL)
'''
rep('''# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)''', CFG_SOUL_PY + '''# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)''')
rep('''+ CFG_GRAPPLE + CFG_LEAP + CFG_BK + CFG_ST + CFG_SS + CFG_MK + CFG_SIG      # 0.1.14: + the wand signature;''',
    '''+ CFG_GRAPPLE + CFG_LEAP + CFG_BK + CFG_ST + CFG_SS + CFG_MK + CFG_SIG + CFG_SOUL      # 0.1.19: + the Soul Orb; 0.1.14: + the wand signature;''')

# the categories: the kit takes 16 and all 16 are used - the 8 fixed staff rows join the fixed wand rows ("Wand + staff (fixed)", 20 chars),
# "staffs" becomes the Soul Orb category (ids are layout only: no saved value names a category)
rep('''            ("check", "Mana check"), ("wands", "Wands (fixed)"), ("staffs", "Staffs (fixed)")]''',
    '''            ("check", "Mana check"), ("wands", "Wand + staff (fixed)"), ("soul", "Soul Orb + essences")]          # 0.1.19: staffs -> wands, + soul''')
rep('''    FIXED.append(("fixed.staff.%s" % _m, "%s (fixed in the jar)" % (STAFF_NAMES.get(_m) or (_m + " Staff")), "staffs", fixed_staff(_i),''',
    '''    FIXED.append(("fixed.staff.%s" % _m, "%s (fixed in the jar)" % (STAFF_NAMES.get(_m) or (_m + " Staff")), "wands", fixed_staff(_i),          # 0.1.19: was "staffs"''')
rep('''FIXED.append(("fixed.staffTap", "Staff tap", "staffs",''', '''FIXED.append(("fixed.staffTap", "Staff tap", "wands",''')
rep('''FIXED.append(("fixed.staffBase", "Staff damage base", "staffs",''', '''FIXED.append(("fixed.staffBase", "Staff damage base", "wands",''')

# ---------------------------------------------------------------------------------------------------------------- the assets
SOUL_ASSET_PY = r'''# ================================================================= 0.1.19 ASSETS: THE SOUL ORB / SOUL CAGES + ESSENCES (tools/armory_0_1_19_patch.py)
ID_SOUL_ROOT = "SkyyArmory_Soul_Bind"          # the Secondary root (and its Charging interaction - the kunai return's shape)
ID_SOUL_REL = "SkyyArmory_Soul_Release"        # what a release runs (a short Simple; the Java ends the Bindings when the chain leaves the Charging)
SOUL_IDS = ["Weapon_Wand_SoulOrb"] + ["Weapon_Wand_SoulCage_%s" % _m for _m in SOUL_TIERS[1:]]
SOUL_NAMES = ["Soul Orb"] + ["%s Soul Cage" % _m for _m in SOUL_TIERS[1:]]
ESS_IDS = ["Ingredient_Life_Essence", "Ingredient_Fire_Essence", "SkyyArmory_Essence_Earth", "Ingredient_Ice_Essence",
           "Ingredient_Lightning_Essence", "Ingredient_Void_Essence", "SkyyArmory_Essence_Light"]
ESS_NEW = {"Earth": ("Resources/Ingredients/Essence_Textures/Fire_Essence_Texture.png", (0xff, 0xa8, 0x30), 0.85, "#320", "Earth Essence",
                     "Dropped by Zone 2 monsters. Used to craft the Thorium Soul Cage."),
           "Light": ("Resources/Ingredients/Essence_Textures/Life_Essence_Texture.png", (0xff, 0xe9, 0xa0), 0.7, "#332", "Light Essence",
                     "Dropped rarely by the deepest zone's monsters. Used to craft the Onyxium Soul Cage.")}
SOUL_ESS = [None, "Life", "Fire", "Earth", "Frost", "Storm", "Void", "Light"]          # the essence each cage is crafted with (the Orb: Life, below)
SOUL_ESS_QTY = [20, 15, 15, 15, 12, 12, 10, 10]         # Soul-Orb-Spec 1 (Onyxium: 10 Light, the Element ladder)
# the soul / gem / Binding colour of each tier (Skyy 2026-10-04 + the 2026-10-10 Element ladder) = the particle line colour
SOUL_COLORS = ["#3f8cff", "#5bd65b", "#ff4a3a", "#ffa830", "#4fe3ff", "#ffe14a", "#a050ff", "#fff0b0"]
# the soul / gem paint per tier: (vanilla essence texture, span, tint (rgb, strength) or None). Copper (Life) + Iron (Fire) = exactly the
# reviewed art (make_soulcage's own colours); Thorium .. Onyxium follow Skyy's 2026-10-10 Element ladder (the reviewed sheet predates it:
# Ice / Lightning / Void / White crystal / Voidheart) - same geometry, metal and gem count, only the soul + gem colour moves
SOUL_PAINT = [("Resources/Ingredients/Essence_Textures/Ice_Essence_Texture.png", (0.0, 1.0), ((0x3f, 0x8c, 0xff), 0.8)),
              ("Resources/Ingredients/Essence_Textures/Life_Essence_Texture.png", (0.0, 1.0), None),
              ("Resources/Ingredients/Essence_Textures/Fire_Essence_Texture.png", (0.0, 1.0), None),
              ("Resources/Ingredients/Essence_Textures/Fire_Essence_Texture.png", (0.0, 1.0), ((0xff, 0xa8, 0x30), 0.85)),
              ("Resources/Ingredients/Essence_Textures/Ice_Essence_Texture.png", (0.0, 1.0), None),
              ("Resources/Ingredients/Essence_Textures/Lightning_Essence_Texture.png", (0.0, 1.0), None),
              ("Resources/Ingredients/Essence_Textures/Void_Essence_Texture.png", (0.10, 1.0), None),
              ("Resources/Crystals/Crystal_Fragment_Textures/White.png", (0.0, 1.0), ((0xff, 0xe9, 0xa0), 0.6))]
assert len(SOUL_IDS) == len(SOUL_NAMES) == len(SOUL_N) == len(SOUL_MULT) == len(SOUL_MPS) == len(SOUL_STAB) == len(SOUL_CAP) == len(SOUL_COLORS) == len(SOUL_PAINT) == 8
assert len(ESS_IDS) == len(ESS_NAMES) == len(ESS_PCT) == len(ESS_ZONE) == 7
for _i in SOUL_IDS + ["SkyyArmory_Essence_Earth", "SkyyArmory_Essence_Light"]:
    assert not az_has("item", _i) and _i not in ITEMS, _i
assert not [_i for _i in SOUL_IDS if "skyy" in _i.lower()], "never 'skyy' in a gear id (SkyyGear GearData.skyyItem)"
for _i in ESS_IDS:
    assert az_has("item", _i) or _i.startswith("SkyyArmory_Essence_"), "a vanilla essence moved: %s" % _i
for _i in ("Ingredient_Crystal_Blue", "Ingredient_Stick", "Ingredient_Fibre"):
    assert az_has("item", _i), "a Soul Orb recipe input left Assets.zip: %s" % _i
assert all(_i.startswith("Weapon_Wand_") for _i in SOUL_IDS), "the Soul items carry the Priest prefix (SkyyClasses' class lock)"
# ---- the art (tools/art/make_soulcage.py functions, AT BUILD TIME - its main() writes the review copy and is never called here)
import make_soulcage as MSC
assert tuple(MSC.METALS) == tuple(SOUL_TIERS[1:]) and tuple(MSC.TETHERS) == tuple(SOUL_N[1:]), (MSC.METALS, MSC.TETHERS)
SOUL_DIR = MSC.ITEM_DIR[len("Common/"):]          # Items/Weapons/SoulCage
SOUL_ANIM = MSC.ANIM_PATH[len("Common/"):]
MODEL_SOUL = [SOUL_DIR + "/SkyyArmory_SoulOrb.blockymodel"] + ["%s/SkyyArmory_%s.blockymodel" % (SOUL_DIR, _m) for _m in SOUL_TIERS[1:]]
TEX_SOUL = [SOUL_DIR + "/SkyyArmory_SoulOrb_Texture.png"] + ["%s/SkyyArmory_%s_Texture.png" % (SOUL_DIR, _m) for _m in SOUL_TIERS[1:]]
ICON_SOUL = ["Icons/ItemsGenerated/SkyyArmory_SoulOrb.png"] + ["Icons/ItemsGenerated/SkyyArmory_SoulCage_%s.png" % _m for _m in SOUL_TIERS[1:]]
ORB_STRETCH = 1.8          # the bare Soul Orb: the soul alone, 1.8x bigger (no cage around it)
ORB_ICON = dict(MSC.ICON_PROPS, Scale=1.2)
SOUL_FILES, SOUL_REVIEW = [], {}
_anim = MSC.jbytes(MSC.build_anim())
ASSETS["Common/" + SOUL_ANIM] = _anim
SOUL_FILES.append("Common/" + SOUL_ANIM)
SOUL_ART = []
for _t, _tier in enumerate(SOUL_TIERS):
    _metal = "Copper" if _tier == "Orb" else _tier
    _hd, _bd = SA._tuned(_metal, "head"), SA._tuned(_metal, "bands")
    _et, (_elo, _ehi), _tint = SOUL_PAINT[_t]
    _M = MSC.ramp_fn(SA.metal_gradient(AZ, _metal), _hd["lo"], _hd["hi"])
    _T = MSC.ramp_fn(SA.band_gradient(AZ, _metal), _bd["lo"], _bd["hi"])
    _E = MSC.ramp_fn(SA.palette_from([SA._read(AZ, _et)]), _elo, _ehi, _tint)
    _model = MSC.build_model(max(0, _t - 1))
    _props = MSC.ICON_PROPS
    if _tier == "Orb":
        _flt = _model["nodes"][0]["children"][0]
        assert _flt["name"] == "Float" and [c_["name"] for c_ in _flt["children"]] == ["Soul", "SoulB", "Cage"]
        _flt["children"] = [c_ for c_ in _flt["children"] if c_["name"] != "Cage"]
        for c_ in _flt["children"]:
            c_["shape"]["stretch"] = {"x": ORB_STRETCH, "y": ORB_STRETCH, "z": ORB_STRETCH}
        _props = ORB_ICON
    _tex = SA.png_encode(MSC.paint(_M, _T, _E))
    _icon = SA.render_icon(_model, _tex, _props, 64)
    _mj = MSC.jbytes(_model)
    assert SA.png_size(_tex) == (MSC.TEX_W, MSC.TEX_H) and SA.png_size(_icon) == (64, 64)
    for _p, _b in ((MODEL_SOUL[_t], _mj), (TEX_SOUL[_t], _tex), (ICON_SOUL[_t], _icon)):
        assert ("Common/" + _p) not in AZ_SET and ("Common/" + _p) not in ASSETS, _p
        ASSETS["Common/" + _p] = _b
        SOUL_FILES.append("Common/" + _p)
    SOUL_ART.append((_mj, _tex, _icon, _props))
    # the review copy (git-ignored models-local/art/soulcage, Skyy's approved v2): geometry + spin always equal; Copper / Iron (Life / Fire,
    # unchanged essences) byte-equal; Thorium+ = the Element ladder recolour (texture + icon differ on purpose)
    if _tier != "Orb":
        _rv = os.path.join(ROOT, "models-local", "art", "soulcage")
        _rm, _rt, _ri = [os.path.join(_rv, *("Common/" + p_).split("/")) for p_ in (MODEL_SOUL[_t], TEX_SOUL[_t], ICON_SOUL[_t])]
        _ra = os.path.join(_rv, *MSC.ANIM_PATH.split("/"))
        if all(os.path.isfile(p_) for p_ in (_rm, _rt, _ri, _ra)):
            assert open(_rm, "rb").read() == _mj and open(_ra, "rb").read() == _anim, \
                "%s: the soul cage model / spin differs from the reviewed copy (re-run python tools/art/make_soulcage.py)" % _tier
            if _tier in ("Copper", "Iron"):
                assert open(_rt, "rb").read() == _tex and open(_ri, "rb").read() == _icon, "%s: the soul cage art differs from the reviewed copy" % _tier
                SOUL_REVIEW[_tier] = "= reviewed copy"
            else:
                assert open(_rt, "rb").read() != _tex, "%s: the Element ladder recolour did not change the texture" % _tier
                SOUL_REVIEW[_tier] = "model + spin = reviewed copy; soul + gems in the 2026-10-10 Element colour"
        else:
            SOUL_REVIEW[_tier] = "no review copy here"
assert len(set(a_[1] for a_ in SOUL_ART)) == 8 and len(set(a_[2] for a_ in SOUL_ART)) == 8


def soul_tint_png(png, rgb, k):
    """a vanilla texture moved onto a target hue at its own luminance (make_soulcage's ramp tint, per pixel; alpha kept)"""
    im = SA.png_decode(png)
    tr, tg, tb = rgb
    tl = 0.299 * tr + 0.587 * tg + 0.114 * tb
    for y_ in range(im.h):
        for x_ in range(im.w):
            c_ = im.get(x_, y_)
            if c_[3] == 0:
                continue
            l_ = 0.299 * c_[0] + 0.587 * c_[1] + 0.114 * c_[2]
            h_ = (tr * l_ / tl, tg * l_ / tl, tb * l_ / tl)
            im.put(x_, y_, (c_[0] + (h_[0] - c_[0]) * k, c_[1] + (h_[1] - c_[1]) * k, c_[2] + (h_[2] - c_[2]) * k, c_[3]))
    return SA.png_encode(im)


# ---- the 2 new essences: the vanilla essence item shape (model, icon view, sound set, stack) + a recoloured texture + our icon
_vess = az_get("item", "Ingredient_Life_Essence")
assert _vess["Model"] == "Resources/Ingredients/Essence.blockymodel" and _vess["PlayerAnimationsId"] == "Item" and _vess.get("MaxStack") == 100 \
    and _vess["Categories"] == ["Items.Ingredients"] and _vess["Tags"] == {"Type": ["Ingredient"]}, "the vanilla Life Essence changed shape"
_vem = json.loads(SA._read(AZ, _vess["Model"]).decode("utf-8-sig"))
P_EITEM = "Server/Item/Items/Ingredient/%s.json"
ESS_FILES = []
for _n, (_src, _rgb, _k, _light, _nm, _ds) in sorted(ESS_NEW.items()):
    _eid = "SkyyArmory_Essence_" + _n
    _etex = soul_tint_png(SA._read(AZ, _src), _rgb, _k)
    _eicon = SA.render_icon(_vem, _etex, _vess["IconProperties"], 64)
    _tp, _ip = "Items/SkyyArmory/Essence/%s_Texture.png" % _eid, "Icons/ItemsGenerated/%s.png" % _eid
    assert ("Common/" + _tp) not in AZ_SET and ("Common/" + _ip) not in AZ_SET
    ASSETS["Common/" + _tp] = _etex
    ASSETS["Common/" + _ip] = _eicon
    _ei = {"TranslationProperties": {"Name": "server.items.%s.name" % _eid, "Description": "server.items.%s.description" % _eid},
           "Icon": _ip, "Quality": "Uncommon", "Categories": list(_vess["Categories"]), "Model": _vess["Model"], "Texture": _tp,
           "PlayerAnimationsId": _vess["PlayerAnimationsId"], "IconProperties": json.loads(json.dumps(_vess["IconProperties"])),
           "Tags": json.loads(json.dumps(_vess["Tags"])), "ItemEntity": {"ParticleSystemId": None}, "Scale": _vess["Scale"],
           "Light": {"Color": _light, "Radius": 1}, "ItemSoundSetId": _vess["ItemSoundSetId"], "MaxStack": 100, "DropOnDeath": True}
    ITEMS[_eid] = _ei
    put(P_EITEM % _eid, _ei)
    ESS_FILES += [P_EITEM % _eid, "Common/" + _tp, "Common/" + _ip]
# ---- the Bindings root: a Charging Secondary (the kunai return's shape: AllowIndefiniteHold, Next "0" = a short Simple) with the wand's
# hold pose (the vanilla Watering Can's hold-to-keep-going shape: Charging + AllowIndefiniteHold); the SERVER watches the chain (Soul.heldChain) -
# no projectile, no marker, nothing client-side to spend
assert "CastLeftCharging" in json.loads(AZ.read("Server/Item/Animations/Wand.json").decode("utf-8-sig"))["Animations"]
add_int(P_WINT, ID_SOUL_REL, {"Type": "Simple", "RunTime": 0.05})
add_int(P_WINT, ID_SOUL_ROOT, {"Type": "Charging", "Effects": {"ItemAnimationId": "CastLeftCharging"}, "AllowIndefiniteHold": True,
                               "DisplayProgress": False, "Next": {"0": ID_SOUL_REL}})          # no charge bar: a hold with no stages (the vanilla Battleaxe way)
add_root(P_WROOT, ID_SOUL_ROOT, [ID_SOUL_ROOT])
# ---- the recipes: the Soul Orb (Soul-Orb-Spec 1), then each cage = the tier before + its metal wand's bars + its essence, at that metal wand's
# bench (the Weapon Bench, its tab + tier) and time
SOUL_RECIPES = []
_r0 = json.loads(json.dumps(WAND_RECIPES["Copper"]))
SOUL_RECIPES.append({"TimeSeconds": _r0.get("TimeSeconds", 3), "KnowledgeRequired": False,
                     "Input": [{"ItemId": "Ingredient_Life_Essence", "Quantity": SOUL_ESS_QTY[0]}, {"ItemId": "Ingredient_Crystal_Blue", "Quantity": 1},
                               {"ItemId": "Ingredient_Stick", "Quantity": 4}, {"ItemId": "Ingredient_Fibre", "Quantity": 1}],
                     "BenchRequirement": json.loads(json.dumps(_r0["BenchRequirement"]))})
for _t in range(1, 8):
    _m = SOUL_TIERS[_t]
    _wr = json.loads(json.dumps(WAND_RECIPES[_m]))
    _bars = [x_ for x_ in _wr["Input"] if x_.get("ItemId") == "Ingredient_Bar_%s" % _m]
    assert len(_bars) == 1 and int(_bars[0]["Quantity"]) > 0, (_m, _wr["Input"])
    SOUL_RECIPES.append({"TimeSeconds": _wr.get("TimeSeconds", 3), "KnowledgeRequired": False,
                         "Input": [{"ItemId": SOUL_IDS[_t - 1], "Quantity": 1}, {"ItemId": _bars[0]["ItemId"], "Quantity": int(_bars[0]["Quantity"])},
                                   {"ItemId": ESS_IDS[ESS_NAMES.index(SOUL_ESS[_t])], "Quantity": SOUL_ESS_QTY[_t]}],
                         "BenchRequirement": json.loads(json.dumps(_wr["BenchRequirement"]))})
for _r in SOUL_RECIPES:
    for _x in _r["Input"]:
        assert az_has("item", _x["ItemId"]) or _x["ItemId"] in SOUL_IDS or _x["ItemId"].startswith("SkyyArmory_Essence_"), _x
    assert any(b_.get("Type") == "Crafting" and b_.get("Id") == "Weapon_Bench" for b_ in _r["BenchRequirement"]), _r


def soul_light(hx):
    """a dim 3-digit item light in the soul colour (the vanilla essences carry #310 / #130)"""
    return "#" + "".join("%x" % (int(hx[1 + 2 * k_:3 + 2 * k_], 16) // 64) for k_ in range(3))


# ---- the 8 items (Priest only by the Weapon_Wand_ prefix); quality / level from the same-metal sword (the spellbook rule; the Orb = Crude)
SOUL_LANG = []
for _t, _sid in enumerate(SOUL_IDS):
    _sw = resolve("item", "Weapon_Sword_" + ("Crude" if _t == 0 else SOUL_TIERS[_t]))
    _it = {"TranslationProperties": {"Name": "server.items.%s.name" % _sid, "Description": "server.items.%s.description" % _sid},
           "Categories": ["Items.Weapons"], "Icon": ICON_SOUL[_t], "Quality": _sw["Quality"], "ItemLevel": _sw["ItemLevel"],
           "Model": MODEL_SOUL[_t], "Texture": TEX_SOUL[_t], "PlayerAnimationsId": "Wand",
           "IconProperties": json.loads(json.dumps(SOUL_ART[_t][3])), "Interactions": {"Secondary": ID_SOUL_ROOT}, "Weapon": {},
           "Light": {"Color": soul_light(SOUL_COLORS[_t]), "Radius": 1}, "Recipe": SOUL_RECIPES[_t]}
    if _t > 0:
        _it["Animation"] = SOUL_ANIM          # the cage spins (the vanilla Weapon_Staff_Crystal_Flame item-animation pattern)
    ITEMS[_sid] = _it
    put(P_WITEM % _sid[len("Weapon_Wand_"):], _it)
    _cap = SOUL_N[_t]
    SOUL_LANG.append("items.%s.name = %s" % (_sid, SOUL_NAMES[_t]))
    SOUL_LANG.append("items.%s.description = Priest. Hold right click: bind up to %d %s near where you look. Each Binding drains %s Mana a second "
                     "for %s damage a second - no Mana regen while bound. Look %s s to make a Binding solid. Damage is stored as healing."
                     % (_sid, _cap, "enemy" if _cap == 1 else "enemies", bnum(SOUL_MPS[_t]), bnum(round(2.0 * SOUL_MPS[_t] * SOUL_MULT[_t], 2)),
                        bnum(SOUL_STAB[_t])))
for _n, (_src, _rgb, _k, _light, _nm, _ds) in sorted(ESS_NEW.items()):
    SOUL_LANG += ["items.SkyyArmory_Essence_%s.name = %s" % (_n, _nm), "items.SkyyArmory_Essence_%s.description = %s" % (_n, _ds)]
for _l in SOUL_LANG:
    assert ("\n" + _l.split(" = ")[0] + " ") not in _vlang, _l
# (the lines join the lang AFTER the 0.1.15 Untiered lines - the end of the file - see the rep below)
# ---- the Binding lines: 8 finite point systems = the heal orb's ring (SkyyArmory_Ring_Blue, finite) moved onto each tier's colour


def soul_color(x, target):
    m_ = re.match(r"^(rgba\()?#([0-9a-fA-F]{6})([0-9a-fA-F]{2})?(.*)$", x)
    if not m_:
        return x
    h6_ = m_.group(2)
    r_, g_, b_ = (int(h6_[i_:i_ + 2], 16) / 255.0 for i_ in (0, 2, 4))
    hh_, ss_, vv_ = colorsys.rgb_to_hsv(r_, g_, b_)
    th_, ts_, tv_ = colorsys.rgb_to_hsv(*(int(target[i_:i_ + 2], 16) / 255.0 for i_ in (1, 3, 5)))
    if ss_ > 0.15:
        r_, g_, b_ = colorsys.hsv_to_rgb(th_, min(max(ss_, 0.25), max(ts_, 0.3)), max(vv_, tv_ * 0.8))
    return (m_.group(1) or "") + "#%02x%02x%02x" % tuple(int(round(c_ * 255)) for c_ in (r_, g_, b_)) + (m_.group(3) or "") + m_.group(4)


def soul_tree(x, target):
    if isinstance(x, dict):
        return dict((k_, (soul_color(v_, target) if (k_ == "Color" and isinstance(v_, str)) else soul_tree(v_, target))) for k_, v_ in x.items())
    if isinstance(x, list):
        return [soul_tree(v_, target) for v_ in x]
    return x


PS_SOUL = ["SkyyArmory_Soul_%s" % _m for _m in SOUL_TIERS]
_ring = ours(P_PSYS % PS_RING)
assert PS_RING == "SkyyArmory_Ring_Blue" and isinstance(_ring.get("LifeSpan"), (int, float)) and _ring["LifeSpan"] > 0, "the finite heal-orb ring changed"
SOUL_EMIT = 0.25          # FIX ROUND (critic: particle cost): a dot emits for ONE re-draw (Soul.FX_MS 250 ms), never two overlapping systems
for _t, _psid in enumerate(PS_SOUL):
    assert not az_has("psys", _psid) and (P_PSYS % _psid) not in ASSETS, _psid
    _d = json.loads(json.dumps(_ring))
    _d["LifeSpan"] = min(float(_d["LifeSpan"]), SOUL_EMIT)
    for _e in _d["Spawners"]:
        _old = _e["SpawnerId"]
        _new = _old.replace("SkyyArmory_Ring_", "SkyyArmory_Soul_%s_" % SOUL_TIERS[_t])
        assert _new != _old and (P_PSPAWN % _new) not in ASSETS, _old
        if "StartDelay" in _e:
            _e["StartDelay"] = round(min(float(_e["StartDelay"]), SOUL_EMIT * 0.6), 4)
        put(P_PSPAWN % _new, soul_tree(finite_spawner(ours(P_PSPAWN % _old), SOUL_EMIT, FX_LIFE["ring"][1]), SOUL_COLORS[_t]))
        SOUL_FILES.append(P_PSPAWN % _new)
        _e["SpawnerId"] = _new
    put(P_PSYS % _psid, _d)
    SOUL_FILES.append(P_PSYS % _psid)
    assert not endless(_d, dict((e_["SpawnerId"], ours(P_PSPAWN % e_["SpawnerId"])) for e_ in _d["Spawners"])) and _d["LifeSpan"] == SOUL_EMIT, _psid
SOUL_FILES += [P_WINT % ID_SOUL_ROOT, P_WINT % ID_SOUL_REL, P_WROOT % ID_SOUL_ROOT] + [P_WITEM % i_[len("Weapon_Wand_"):] for i_ in SOUL_IDS] + ESS_FILES
SOUL_FILES = sorted(SOUL_FILES)
assert all(p_ in ASSETS for p_ in SOUL_FILES) and len(SOUL_FILES) == len(set(SOUL_FILES))
# reference closure of the new files
_sbad = []
for _sid in SOUL_IDS + ["SkyyArmory_Essence_Earth", "SkyyArmory_Essence_Light"]:
    _it = ITEMS[_sid]
    for _slot, _rid in (_it.get("Interactions") or {}).items():
        if _rid not in ROOTS:
            _sbad.append("%s %s -> %s" % (_sid, _slot, _rid))
    for _f in ("Icon", "Texture", "Model", "Animation"):
        _p = _it.get(_f)
        if _p and ("Common/" + _p) not in AZ_SET and ("Common/" + _p) not in ASSETS:
            _sbad.append("%s: missing %s %s" % (_sid, _f, _p))
    if not az_has("quality", _it["Quality"]):
        _sbad.append("%s: unknown quality %s" % (_sid, _it["Quality"]))
for _r in refs_of(INTS[ID_SOUL_ROOT], set()):
    if _r not in INTS and not az_has("int", _r):
        _sbad.append("%s -> %s" % (ID_SOUL_ROOT, _r))
assert not _sbad and ROOTS[ID_SOUL_ROOT] == {"Interactions": [ID_SOUL_ROOT]}, _sbad
print("0.1.19 soul orb: %d items (%s) + 2 essences (%s), root %s (Charging, hold = Bindings), %d particle lines, %d files; art %s; recipes %s" % (
    len(SOUL_IDS), ", ".join(SOUL_IDS), ", ".join(sorted("SkyyArmory_Essence_" + n_ for n_ in ESS_NEW)), ID_SOUL_ROOT, len(PS_SOUL), len(SOUL_FILES),
    sorted(set(SOUL_REVIEW.values())), "; ".join("%s <- %s" % (SOUL_IDS[t_], " + ".join("%d %s" % (x_["Quantity"], x_["ItemId"]) for x_ in r_["Input"]))
                                                for t_, r_ in enumerate(SOUL_RECIPES))))
'''
rep('''# ================================================================= the SET jars, SkyySkills (anchor + handover), the clash scan''',
    SOUL_ASSET_PY + '''# ================================================================= the SET jars, SkyySkills (anchor + handover), the clash scan''')
rep('''ASSETS[P_LANG] = ASSETS[P_LANG] + "\\n".join(UT_LANG) + "\\n"
''', '''ASSETS[P_LANG] = ASSETS[P_LANG] + "\\n".join(UT_LANG) + "\\n"
ASSETS[P_LANG] = ASSETS[P_LANG] + "\\n".join(SOUL_LANG) + "\\n"          # 0.1.19: the Soul Orb names + descriptions (appended last)
''')

# ---------------------------------------------------------------------------------------------------------------- the tables + the default file
SOUL_TAB_PY = r'''# ---- 0.1.19: the Soul Orb tables (an entry per tier) + the essence drop tables (an entry per essence)
SOUL_TAB = [  # (key, label, cat, value type, min, max, unit, help, ArmoryCfg field, defaults, names)
    ("soul.bindings", "Bindings by tier (most at once)", "soul", "int", "1", "32", "", "Skyy: 1 / 2 / 4 / 6 / 10 / 14 / 16 / 20 (Orb = the bare Soul Orb). Tooltips show defaults.", "SOUL_NT", SOUL_N, SOUL_TIERS),
    ("soul.manaPerSecond", "Mana a second per Binding by tier", "soul", "dec", "0", "20", "", "Each Binding drains this much Mana a second (about the same every tier). Tooltips show defaults.", "SOUL_MPS", SOUL_MPS, SOUL_TIERS),
    ("soul.damageMult", "Damage per Mana by tier (x)", "soul", "dec", "0", "10", "x", "x soul.damagePerMana. Skyy: 1.0 / 1.1 / 1.1 / 1.5 / 1.5 / 2.0 / 2.0 / 2.5. Tooltips show defaults.", "SOUL_MULT", SOUL_MULT, SOUL_TIERS),
    ("soul.stabilize", "Seconds to make a Binding solid", "soul", "dec", "0", "10", "s", "Look at a new Binding this long; then you may look away (Skyy: 1.5-2.5 s). Tooltips show defaults.", "SOUL_STAB", SOUL_STAB, SOUL_TIERS),
    ("soul.storeCap", "Stored healing cap by tier (%)", "soul", "int", "0", "100", "%", "Stored healing stops at this % of the Priest's max Health.", "SOUL_CAP", SOUL_CAP, SOUL_TIERS),
    ("essence.chance", "Essence drop chance (%)", "soul", "dec", "0", "100", "%", "Chance per kill of a monster of that essence's zone (Frost = Ice, Storm = Lightning).", "ESS_PCT", ESS_PCT, ESS_NAMES),
    ("essence.zone", "Essence zone (0 = volcanic caves)", "soul", "int", "0", "9", "", "Zone N mobs drop it (Void, Light: Zone 4 for now). Outside zones: Lv 1-20/21-30/31-45/46+ (fixed).", "ESS_ZONE", ESS_ZONE, ESS_NAMES),
]
assert all(len(t[1]) <= 40 and len(t[7]) <= 100 and len(t[9]) == len(t[10]) for t in SOUL_TAB), [t[0] for t in SOUL_TAB]
SOUL_TAB_ROWS = []
for _k, _lab, _cat, _vt, _mn, _mx, _u, _hlp, _fld, _defs, _ms in SOUL_TAB:
    _chk = "ArmoryHooks.checkSoul" if _ms is SOUL_TIERS else "ArmoryHooks.checkEssence"
    SOUL_TAB_ROWS.append((_k, _lab, _cat, "table", "", _mn, _mx, "%s;none;%s" % (_vt, "Value"), _u, "live", _hlp,
                          "reload@%s:%s.;check=%s" % (CFG_FILE, _k, _chk)))
SOUL_TAB_LINES = []
for _k, _lab, _cat, _vt, _mn, _mx, _u, _hlp, _fld, _defs, _ms in SOUL_TAB:
    SOUL_TAB_LINES.append("# " + _lab + ": " + _hlp)
    SOUL_TAB_LINES += ["%s.%s=%s" % (_k, _m, bnum(_d)) for _m, _d in zip(_ms, _defs)]
'''
rep('''CFG_LINES = [
    "# SkyyArmory %s - settings''', SOUL_TAB_PY + '''CFG_LINES = [
    "# SkyyArmory %s - settings''')
rep('''] + [x for _r in CFG_SIG for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
''', '''] + [x for _r in CFG_SIG for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
    "",
    "# ---- Soul Orb / Soul Cages + essence drops (SkyyArmory 0.1.19; Skyy 2026-10-04 / 2026-10-07 / 2026-10-10): hold right click = soul Bindings",
] + [x for _r in CFG_SOUL for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + SOUL_TAB_LINES + [
''')
rep('''FIXED_VAL = dict((f[0], f[3]) for f in FIXED)
''', '''FIXED.append(("fixed.soul", "Soul Orb + Cages (fixed in the jar)", "soul",
              "8 items Weapon_Wand_SoulOrb / _SoulCage_<metal> (Priest), hold right click = Bindings; recipes: the tier before + bars + "
              "essence; new essences Earth + Light",
              "Client-predicted: the hold, the art, the recipes. The rows above set the rest."))
FIXED_VAL = dict((f[0], f[3]) for f in FIXED)
''')
rep('''] + [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], "field:ArmoryCfg." + r[11]) for r in CFG_NEW] + BK_TAB_ROWS + SS_TAB_ROWS + [''',
    '''] + [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], "field:ArmoryCfg." + r[11]) for r in CFG_NEW] + BK_TAB_ROWS + SS_TAB_ROWS + SOUL_TAB_ROWS + [''')
rep('''assert all(_l in CFG_TEXT for _l in SS_TAB_LINES), "0.1.8 table lines in the default file"
''', '''assert all(_l in CFG_TEXT for _l in SS_TAB_LINES), "0.1.8 table lines in the default file"
for _k, _lab, _cat, _vt, _mn, _mx, _u, _hlp, _fld, _defs, _ms in SOUL_TAB:        # 0.1.19: every soul / essence table entry's default is in the file
    assert [_dp.get("%s.%s" % (_k, _m)) for _m in _ms] == [bnum(_d) for _d in _defs], (_k, [_dp.get("%s.%s" % (_k, _m)) for _m in _ms])
assert all(_l in CFG_TEXT for _l in SOUL_TAB_LINES), "0.1.19 table lines in the default file"
''')

# ---------------------------------------------------------------------------------------------------------------- ArmoryDefs + ArmoryCfg + hooks
rep('''for f in ("public static final String RICO_MARK = %s;" % jstr(RICO_MARK), "public static final int RICO_CODE = %d;" % RICO_CODE,
          "public static final int SIG_MAX = %d;" % SIG_MAX):          # 0.1.14 the wand signature
    F(dfs, f)
''', '''for f in ("public static final String RICO_MARK = %s;" % jstr(RICO_MARK), "public static final int RICO_CODE = %d;" % RICO_CODE,
          "public static final int SIG_MAX = %d;" % SIG_MAX):          # 0.1.14 the wand signature
    F(dfs, f)
for f in ("public static final String[] SOUL_IDS = %s;" % jarr(SOUL_IDS), "public static final String[] SOUL_TIERS = %s;" % jarr(SOUL_TIERS),
          "public static final String[] SOUL_NAMES = %s;" % jarr(SOUL_NAMES), "public static final String[] SOUL_PS = %s;" % jarr(PS_SOUL),
          "public static final String SOUL_ROOT = %s;" % jstr(ID_SOUL_ROOT),
          "public static final String[] ESS_NAMES = %s;" % jarr(ESS_NAMES), "public static final String[] ESS_IDS = %s;" % jarr(ESS_IDS)):          # 0.1.19
    F(dfs, f)
''')
rep('''F(cfg, "public static volatile String SIG_TEXT = \\"\\";")          # 0.1.14
''', '''F(cfg, "public static volatile String SIG_TEXT = \\"\\";")          # 0.1.14
for _k, _lab, _cat, _vt, _mn, _mx, _u, _hlp, _fld, _defs, _ms in SOUL_TAB:        # 0.1.19 the soul tier tables (index = SOUL_TIERS) + essence tables (ESS_NAMES)
    F(cfg, "public static volatile double[] %s = %s;" % (_fld, jdbls(_defs)))
    F(cfg, "public static final double[] %s_DEF = %s;" % (_fld, jdbls(_defs)))
F(cfg, "public static volatile String SOUL_TEXT = \\"\\";")          # 0.1.19
''')


def apply_line(r):
    k, typ, d, lo, hi, fld = r[0], r[3], r[4], r[5], r[6], r[11]
    if typ == "bool":
        return '  %s = bool(c.getProperty("%s"), %s);' % (fld, k, d)
    if typ == "int":
        return '  %s = intOf(c.getProperty("%s"), %d, %d, %d);' % (fld, k, int(d), int(lo), int(hi))
    assert typ == "dec", r
    return '  %s = dec(c.getProperty("%s"), %r, %r, %r);' % (fld, k, float(d), float(lo), float(hi))


_ns = {"bnum": lambda v: str(v), "CFG_FILE": "Skyy_SkyyArmory/config.properties"}
exec(CFG_SOUL_PY, _ns)          # the row tables (plain Python) -> the loader lines of ArmoryCfg.apply
exec(SOUL_TAB_PY, _ns)
APPLY_SOUL = "\n".join(apply_line(r) for r in _ns["CFG_SOUL"])
for _t in _ns["SOUL_TAB"]:
    _names = "@PKG@.ArmoryDefs.SOUL_TIERS" if _t[10] is _ns["SOUL_TIERS"] else "@PKG@.ArmoryDefs.ESS_NAMES"
    APPLY_SOUL += '\n  %s = tab(c, "%s.", %s, %s_DEF, %r, %r);' % (_t[8], _t[0], _names, _t[8], float(_t[4]), float(_t[5]))
assert "%" not in APPLY_SOUL          # apply() is a %-formatted block
rep('''  SIG_TEXT = sigText();          // 0.1.14
''', '''  SIG_TEXT = sigText();          // 0.1.14
''' + APPLY_SOUL + '''
  SOUL_TEXT = soulText();          // 0.1.19
  try { @PKG@.ArmoryDefs.bridge().put("armory:soul", SOUL_TEXT); } catch (Throwable tsl) { }
''')
rep('''M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''', '''# 0.1.19: the Soul Orb's live numbers (the start line + armory:soul)
M(cfg, r"""
public static String soulText() {
  StringBuilder sb = new StringBuilder();
  sb.append("soul Bindings ").append(SOUL_ON ? "on" : "OFF").append(" - hold right click: bind every enemy within ").append(cfmt(SOUL_RADIUS))
    .append(" blocks of where you look (reach ").append(SOUL_RANGE).append(", line of sight to start), up to");
  for (int i = 0; i < @PKG@.ArmoryDefs.SOUL_TIERS.length && i < SOUL_NT.length; i++) sb.append(i == 0 ? " " : " / ").append((int) SOUL_NT[i]);
  sb.append(" (Orb .. Onyxium); solid after");
  for (int i = 0; i < SOUL_STAB.length; i++) sb.append(i == 0 ? " " : " / ").append(cfmt(SOUL_STAB[i]));
  sb.append(" s; each drains");
  for (int i = 0; i < SOUL_MPS.length; i++) sb.append(i == 0 ? " " : " / ").append(cfmt(SOUL_MPS[i]));
  sb.append(" Mana/s for ").append(cfmt(SOUL_DPM)).append(" x");
  for (int i = 0; i < SOUL_MULT.length; i++) sb.append(i == 0 ? " " : " / ").append(cfmt(SOUL_MULT[i]));
  sb.append(" damage per Mana every ").append(cfmt(SOUL_TICK)).append(" s; ").append(SOUL_STORE).append("% stored as healing, Mana regen ")
    .append(SOUL_NOREGEN ? "blocked while bound" : "not blocked").append("; essence drops ").append(ESS_ON ? "on" : "OFF").append(" (");
  for (int i = 0; i < @PKG@.ArmoryDefs.ESS_NAMES.length && i < ESS_PCT.length; i++) {
    sb.append(i == 0 ? "" : ", ").append(@PKG@.ArmoryDefs.ESS_NAMES[i]).append(' ').append(cfmt(ESS_PCT[i])).append("% ")
      .append(ESS_ZONE[i] < 0.5 ? "volcanic caves" : "Z" + (int) ESS_ZONE[i]);
  }
  return sb.append(")").toString();
}""")
M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''')
rep('''M(hooks, "public static String checkShadow(String key, String value) {''',
    '''M(hooks, "public static String checkSoul(String key, String value) { return checkIn(key, value, @PKG@.ArmoryDefs.SOUL_TIERS, \\"Orb, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril or Onyxium\\"); }")          # 0.1.19
M(hooks, "public static String checkEssence(String key, String value) { return checkIn(key, value, @PKG@.ArmoryDefs.ESS_NAMES, \\"Life, Fire, Earth, Frost, Storm, Void or Light\\"); }")
M(hooks, "public static String checkShadow(String key, String value) {''')

# ---------------------------------------------------------------------------------------------------------------- engine members (probed)
rep('''print("engine members probed: %d" % len(PROBED))
''', '''# ---- 0.1.19 the Soul Orb: the held chain (the vanilla ChargingCondition's own walk: InteractionManager chains -> the root's operation at the
# chain's counter -> its inner Interaction), the Mana / Health stats, the essence drop (the SkyyGear 0.2.11 death-drop recipe), the zone
T.update({"OPR": "com.hypixel.hytale.server.core.modules.interaction.interaction.operation.Operation",
          "ENVA": "com.hypixel.hytale.server.core.asset.type.environment.config.Environment",
          "BCH": "com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk",
          "CHU": "com.hypixel.hytale.math.util.ChunkUtil",
          "ITC": "com.hypixel.hytale.server.core.modules.entity.item.ItemComponent",
          "GM": "com.hypixel.hytale.protocol.GameMode",
          "SOULROT": "com.hypixel.hytale.math.vector.Rotation3fc"})
for _c, _m, _r, _a in ((T["ICHN"], "getRootInteraction", T["RTI"], []), (T["ICHN"], "getOperationCounter", "int", []),
                       (T["RTI"], "getOperation", T["OPR"], ["int"]), (T["RTI"], "getId", S_, []), (T["OPR"], "getInnerOperation", T["OPR"], []),
                       (T["DST"], "getMana", "int", []), (T["DST"], "getHealth", "int", []), (T["ESM"], "subtractStatValue", "float", ["int", "float"]),
                       (T["ESV"], "get", "float", []), (T["ESV"], "getMax", "float", []),
                       (T["NPC"], "getEnvironment", "int", []), (T["NPC"], "getRoleName", S_, []), (T["ENVA"], "getAssetMap", "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", []),
                       (T["ENVA"], "getId", S_, []), (T["WLD"], "getChunkStore", T["CHS"], []), (T["WLD"], "getName", S_, []),
                       (T["CHS"], "getChunkComponent", T["COMP"], ["long", T["CTYPE"]]), (T["CHU"], "indexChunkFromBlock", "long", ["int", "int"]),
                       (T["BCH"], "getComponentType", T["CTYPE"], []), (T["BCH"], "getEnvironment", "int", ["int", "int", "int"]),
                       (T["DTH"], "getDeathInfo", T["DMG"], []), (T["HR"], "getRotation", T["R3F"], []), (T["R3F"], "<init>", "void", [T["SOULROT"]]),
                       (T["ITC"], "generateItemDrops", T["HOLD"] + "[]", [T["CAC"], "java.util.List", T["VEC"], T["SOULROT"]]),
                       (T["CB"], "addEntities", T["REF"] + "[]", [T["HOLD"] + "[]", T["ADDR"]]), (T["IS"], "<init>", "void", [S_, "int"]),
                       (T["PLA"], "getGameMode", T["GM"], []), (T["UUIDC"], "getUuid", "java.util.UUID", [])):
    probe_sig(_c, _m, _r, _a)
for _cl, _f in ((T["ITYP"], "Secondary"), (T["GM"], "Creative")):
    _fld = pool.get(_cl).getField(_f)
    assert JMod.isPublic(_fld.getModifiers()) and JMod.isStatic(_fld.getModifiers()), "%s.%s is not public static" % (_cl, _f)
    PROBED.append("%s.%s" % (_cl.rsplit(".", 1)[1], _f))
assert pool.get(T["CHI"]).subclassOf(pool.get(T["INT"])), "ChargingInteraction is no Interaction any more"
_cc19 = _calls("com.hypixel.hytale.server.core.modules.entity.condition.ChargingCondition", "eval0")
_fe19 = _calls("com.hypixel.hytale.server.core.entity.InteractionManager", "forEachInteraction",
               "(Ljava/util/Map;Lcom/hypixel/hytale/function/function/TriFunction;Ljava/lang/Object;)Ljava/lang/Object;")
assert "forEachInteraction" in _cc19 and "getRootInteraction" in _fe19 and "getOperationCounter" in _fe19 and "getOperation" in _fe19 \\
    and "getInnerOperation" in _fe19, "the vanilla ChargingCondition no longer walks the chains the way Soul.heldChain does: %s / %s" % (_cc19, _fe19)
PROBED.append("0.1.19: ChargingCondition.eval0 -> InteractionManager.forEachInteraction (chains -> root.getOperation(counter).getInnerOperation()) = Soul.heldChain")
print("engine members probed: %d" % len(PROBED))
''')

# ---------------------------------------------------------------------------------------------------------------- the Java (SoulBind + SoulState + Soul + SoulFn + SoulDrop + SoulDropSys)
SOUL_JAVA = r'''# ---------------------------------------------------------------- 0.1.19 THE SOUL ORB / SOUL CAGES (tools/armory_0_1_19_patch.py; Skyy 2026-10-04 / 10-07 / 10-10)
sbind = pool.makeClass(PKG + ".SoulBind")
sstate = pool.makeClass(PKG + ".SoulState")
soul = pool.makeClass(PKG + ".Soul")
sfn = pool.makeClass(PKG + ".SoulFn")
sdrop = pool.makeClass(PKG + ".SoulDrop")
sdsys = pool.makeClass(PKG + ".SoulDropSys", pool.get(T["ETS"]))
ALL += [sbind, sstate, soul, sfn, sdrop, sdsys]
for f in ("public @REF@ t;", "public long born;", "public long seen;", "public double held;", "public boolean stable;", "public double dealt;"):
    F(sbind, f)
C(sbind, r"""
public SoulBind(@REF@ t, long now) {
  this.t = t;
  this.born = now;
  this.seen = now;
  this.held = 0.0;
  this.stable = false;
  this.dealt = 0.0;
}""")
for f in ("public java.util.UUID u;", "public @ST@ st;", "public int tier;", "public String item;", "public java.util.ArrayList binds;",
          "public long last;", "public long tickAt;", "public long scan;", "public long fx;", "public long gen;", "public long born;",
          "public boolean blocked;", "public double drained;", "public double dealt;", "public double[] p;", "public long lookAt;"):
    F(sstate, f)
C(sstate, r"""
public SoulState(java.util.UUID u, @ST@ st, int tier, String item, long gen, long now) {
  this.u = u;
  this.st = st;
  this.tier = tier;
  this.item = item;
  this.binds = new java.util.ArrayList();
  this.last = now;
  this.tickAt = now;
  this.scan = 0L;
  this.fx = 0L;
  this.gen = gen;
  this.born = now;
  this.blocked = false;
  this.drained = 0.0;
  this.dealt = 0.0;
  this.p = null;
  this.lookAt = 0L;
}""")
for f in ("public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap POOL = new java.util.concurrent.ConcurrentHashMap();",          # u -> double[]{hp, ms, gen, binding, tier, published}
          "public static volatile java.util.Map HELD = null;",          # HARNESS SEAM ONLY (null in the game = the InteractionManager chains): uuid -> Boolean
          "public static volatile long CLOCK = 0L;",          # HARNESS SEAM ONLY (0 in the game = the wall clock)
          "public static volatile long HOLDS = 0L;", "public static volatile long BINDS = 0L;", "public static volatile long STABLES = 0L;",
          "public static volatile long SNAPS = 0L;", "public static volatile long ENDS = 0L;", "public static volatile long PULSES = 0L;",
          "public static volatile long HITS = 0L;", "public static volatile long RELEASES = 0L;", "public static volatile long OUT_OF_MANA = 0L;",
          "public static volatile long LOS_REFUSED = 0L;", "public static volatile long LOCKED = 0L;", "public static volatile long REGEN_SET = 0L;",
          "public static volatile long REGEN_CLEAR = 0L;", "public static volatile long REGEN_MISSING = 0L;", "public static volatile long RESETS = 0L;",
          "public static volatile double DRAINED = 0.0;", "public static volatile double STORED = 0.0;",
          # FIX ROUND: LATCH = uuid -> TRUE after an out-of-Mana release (no new hold until the button is let go); SEEN = uuid -> Long last
          # tick of a player with soul state (the sweep drops the state / stored healing / latch of a player gone longer than GONE_MS)
          "public static final java.util.concurrent.ConcurrentHashMap LATCH = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile long LATCHED = 0L;", "public static volatile long SWEPT = 0L;", "public static volatile long NO_MANA_STAT = 0L;",
          "public static volatile long SWEEP_AT = 0L;", "public static final long SWEEP_MS = 5000L;", "public static final long GONE_MS = 30000L;",
          # FIX ROUND 2: LOOK_RAYS = look-point ray-casts (only mobs inside the aim cone); SCAN_SKIPS = look scans skipped (cap full, all solid)
          "public static volatile long LOOK_RAYS = 0L;", "public static volatile long SCAN_SKIPS = 0L;",
          "public static volatile String LAST_WHY = \"\";", "public static volatile String LAST_RELEASE = \"\";",
          "public static final double EYE = %r;" % SS_EYE, "public static final long SCAN_MS = 100L;", "public static final long FX_MS = 250L;",
          "public static final long PUB_MS = 500L;", "public static final int MAX_BINDS = 32;", "public static final String KEY = \"armory:soul:\";",
          "public static final String REGEN_FN = \"skill:fn:regenblock\";"):
    F(soul, f)
M(soul, r"""public static void warn(String key, String msg) { @PKG@.ArmoryLog.warnOnce("soul:" + key, msg); }""")
M(soul, r"""public static long now() { long c = CLOCK; return c > 0L ? c : System.currentTimeMillis(); }""")
M(soul, r"""
public static int tierOf(String item) {
  if (item == null) return -1;
  for (int i = 0; i < @PKG@.ArmoryDefs.SOUL_IDS.length; i++) if (@PKG@.ArmoryDefs.SOUL_IDS[i].equals(item)) return i;
  return -1;
}""")
# ---- PURE maths (plain numbers; the harness runs them)
M(soul, r"""
public static int cap(int tier) {
  if (tier < 0 || tier >= @PKG@.ArmoryCfg.SOUL_NT.length) return 0;
  int n = (int) Math.round(@PKG@.ArmoryCfg.SOUL_NT[tier]);
  return n < 0 ? 0 : (n > MAX_BINDS ? MAX_BINDS : n);
}""")
M(soul, r"""public static double dps(double dpm, double mps, double mult) { return (dpm > 0.0 && mps > 0.0 && mult > 0.0) ? dpm * mps * mult : 0.0; }""")
M(soul, r"""public static double drain(int n, double mps, double secs) { return (n > 0 && mps > 0.0 && secs > 0.0) ? (double) n * mps * secs : 0.0; }""")
M(soul, r"""public static long stabMs(double s) { return s > 0.0 ? Math.round(s * 1000.0) : 0L; }""")
M(soul, r"""public static long pulseMs() { long p = Math.round(@PKG@.ArmoryCfg.SOUL_TICK * 1000.0); return p < 50L ? 50L : p; }""")
# the stored healing: + add, at most cap (a pool already above a lowered cap is kept, never cut); decay = pct of the pool a second, compounding
# (x (1 - pct / 100) ^ seconds: the same result however often it is read)
M(soul, r"""
public static double addStore(double pool, double add, double cap) {
  double p = pool > 0.0 ? pool : 0.0;
  if (!(add > 0.0)) return p;
  double c = cap > 0.0 ? cap : 0.0;
  double r = p + add;
  if (r > c) r = c > p ? c : p;
  return r;
}""")
M(soul, r"""
public static double decay(double pool, double pct, double secs) {
  if (!(pool > 0.0)) return 0.0;
  if (!(pct > 0.0) || !(secs > 0.0)) return pool;
  if (pct >= 100.0) return 0.0;
  return pool * Math.pow(1.0 - pct / 100.0, secs);
}""")
M(soul, r"""
public static double dist(double ax, double ay, double az, double bx, double by, double bz) {
  double dx = bx - ax;
  double dy = by - ay;
  double dz = bz - az;
  return Math.sqrt(dx * dx + dy * dy + dz * dz);
}""")
# ---- engine glue (world thread; never throws)
M(soul, r"""public static int manaIdx() { try { return @DST@.getMana(); } catch (Throwable t) { return -1; } }""")
M(soul, r"""public static int hpIdx() { try { return @DST@.getHealth(); } catch (Throwable t) { return -1; } }""")
M(soul, r"""
public static float statOf(@CAC@ acc, @REF@ r, int idx, boolean max) {
  if (idx < 0 || r == null) return -1.0f;
  try {
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m == null) return -1.0f;
    @ESV@ v = m.get(idx);
    if (v == null) return -1.0f;
    return max ? v.getMax() : v.get();
  } catch (Throwable t) { return -1.0f; }
}""")
M(soul, r"""
public static boolean spend(@CAC@ acc, @REF@ r, int idx, double amt) {
  if (idx < 0 || r == null || !(amt > 0.0)) return false;
  try {
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m == null) return false;
    m.subtractStatValue(idx, (float) amt);
    return true;
  } catch (Throwable t) { warn("spend", "the Binding drain could not take Mana (" + t + ")"); return false; }
}""")
# THE HOLD: the player's InteractionManager has a Secondary chain of our root whose CURRENT operation is the Charging (the vanilla
# ChargingCondition walks the same way); a release moves the chain to its "0" Simple (then it ends) = not held
M(soul, r"""
public static boolean heldChain(@CAC@ acc, @REF@ r) {
  try {
    Object im = acc.getComponent(r, @IMOD@.get().getInteractionManagerComponent());
    if (!(im instanceof @IMGR@)) return false;
    java.util.Map m = (java.util.Map) ((@IMGR@) im).getChains();
    if (m == null || m.isEmpty()) return false;
    java.util.Iterator it = m.values().iterator();
    while (it.hasNext()) {
      Object c = it.next();
      if (!(c instanceof @ICHN@)) continue;
      @ICHN@ ch = (@ICHN@) c;
      if (ch.getType() != @ITYP@.Secondary) continue;
      @RTI@ root = ch.getRootInteraction();
      if (root == null || !@PKG@.ArmoryDefs.SOUL_ROOT.equals(root.getId())) continue;
      @OPR@ op = root.getOperation(ch.getOperationCounter());
      if (op == null) continue;
      @OPR@ in = op.getInnerOperation();
      if (in instanceof @CHI@) return true;
    }
  } catch (Throwable t) { warn("held", "the right-click hold could not be read (" + t + ") - no Bindings"); }
  return false;
}""")
M(soul, r"""
public static boolean held(@CAC@ acc, @REF@ r, java.util.UUID u) {
  java.util.Map h = HELD;
  if (h != null) return Boolean.TRUE.equals(h.get(u));
  return heldChain(acc, r);
}""")
# SkyySkills 0.4.30's skill:fn:regenblock (Object[]{UUID, Long untilMs} -> Boolean; 0 = clear): no natural Mana regen while bound
M(soul, r"""
public static boolean regen(java.util.UUID u, long until) {
  if (u == null) return false;
  java.util.function.Function f = @PKG@.ArmoryTrav.fn(REGEN_FN);
  if (f == null) { if (until > 0L) REGEN_MISSING = REGEN_MISSING + 1L; return false; }
  try {
    Object r = f.apply(new Object[] { u, Long.valueOf(until) });
    if (until > 0L) REGEN_SET = REGEN_SET + 1L; else REGEN_CLEAR = REGEN_CLEAR + 1L;
    return Boolean.TRUE.equals(r);
  } catch (Throwable t) { warn("regen", REGEN_FN + " failed (" + t + ") - Mana may regenerate while bound"); return false; }
}""")
# ---- the stored healing (one pool per player: double[]{hp, last ms, profile gen, binding 1/0, tier, last published ms})
M(soul, r"""
public static void publish(java.util.UUID u, double hp) {
  try {
    java.util.Map b = @PKG@.ArmoryDefs.bridge();
    if (hp > 0.005) b.put(KEY + u.toString(), Double.valueOf(Math.floor(hp * 100.0 + 0.5) / 100.0));
    else b.remove(KEY + u.toString());
  } catch (Throwable t) { }
}""")
M(soul, r"""
public static void resetPool(java.util.UUID u, String why) {
  if (u == null) return;
  if (POOL.remove(u) != null) { RESETS = RESETS + 1L; LAST_WHY = "stored healing cleared (" + why + ")"; }
  publish(u, 0.0);
}""")
M(soul, r"""
public static double poolNow(java.util.UUID u, long now) {
  if (u == null) return 0.0;
  Object o = POOL.get(u);
  if (!(o instanceof double[])) return 0.0;
  double[] p = (double[]) o;
  if (p[3] < 0.5) {
    double secs = (double) (now - (long) p[1]) / 1000.0;
    if (secs > 0.0) { p[0] = decay(p[0], @PKG@.ArmoryCfg.SOUL_DECAY, secs); p[1] = (double) now; }
  }
  if (!(p[0] > 0.005)) { POOL.remove(u, o); publish(u, 0.0); return 0.0; }
  return p[0];
}""")
M(soul, r"""
public static void store(java.util.UUID u, double add, double capHp, int tier, long gen, long now) {
  if (u == null || !(add > 0.0)) return;
  Object o = POOL.get(u);
  double[] p = null;
  if (o instanceof double[]) p = (double[]) o;
  if (p == null) { p = new double[] { 0.0, (double) now, (double) gen, 1.0, (double) tier, 0.0 }; POOL.put(u, p); }
  double before = p[0];
  p[0] = addStore(p[0], add, capHp);
  p[1] = (double) now;
  p[2] = (double) gen;
  p[3] = 1.0;
  p[4] = (double) tier;
  STORED = STORED + (p[0] - before);
  publish(u, p[0]);
  p[5] = (double) now;
}""")
M(soul, r"""
public static void unbinding(java.util.UUID u, long now) {
  Object o = POOL.get(u);
  if (o instanceof double[]) { double[] p = (double[]) o; p[3] = 0.0; p[1] = (double) now; }
}""")
# every tick of the player: the pool resets on death / a profile switch (Soul-Orb-Spec 4.1), decays when not binding, published twice a second
M(soul, r"""
public static void poolTick(java.util.UUID u, boolean dead, long gen, long now) {
  Object o = POOL.get(u);
  if (!(o instanceof double[])) return;
  double[] p = (double[]) o;
  if (dead) { resetPool(u, "death"); return; }
  if ((long) p[2] != gen) { resetPool(u, "profile switch"); return; }
  if (now - (long) p[5] < PUB_MS) return;
  double hp = poolNow(u, now);
  if (hp > 0.0) { publish(u, hp); p[5] = (double) now; }
}""")
# armory:fn:soul "take": the stored healing a heal spends - at most the tier's cap % of the HEALED one's max Health (Soul-Orb-Spec 4.1)
M(soul, r"""
public static double take(java.util.UUID u, double maxHp, long now) {
  double hp = poolNow(u, now);
  if (!(hp > 0.0)) return 0.0;
  double[] p = (double[]) POOL.get(u);
  if (p == null) return 0.0;
  int tier = (int) p[4];
  double capPct = (tier >= 0 && tier < @PKG@.ArmoryCfg.SOUL_CAP.length) ? @PKG@.ArmoryCfg.SOUL_CAP[tier] : 0.0;
  double lim = maxHp > 0.0 ? maxHp * capPct / 100.0 : hp;
  double t = hp < lim ? hp : lim;
  if (!(t > 0.0)) return 0.0;
  p[0] = hp - t;
  if (!(p[0] > 0.005)) { POOL.remove(u); publish(u, 0.0); } else publish(u, p[0]);
  return t;
}""")
# who may be bound: an enemy MOB (ArmoryTrav.kind 0 with PvP off = never a player), never a player at all (Bindings are PvE), never a
# protected mob (Invulnerable / grapple.noYankWords), never a Friendly / Revered / Ignore one (livestock, pets, summons - Shadow.attitude)
M(soul, r"""
public static boolean ok(@CAC@ acc, @REF@ t, @REF@ me, java.util.UUID u) {
  if (t == null || (me != null && t.equals(me))) return false;
  if (@PKG@.ArmoryTrav.kind(acc, t, me, u, false) != 0) return false;
  if (@PKG@.Kunai.prOf(acc, t) != null) return false;
  if (@PKG@.Shadow.protect(acc, t)) return false;
  return @PKG@.Shadow.attitude(acc, t, me) <= 1;
}""")
M(soul, r"""
public static double[] centre(@CAC@ acc, @REF@ t) {
  @VEC@ p = @PKG@.ArmoryTrav.posOf(acc, t);
  if (p == null) return null;
  return new double[] { p.x, p.y + @PKG@.Shadow.height(acc, t) * 0.5, p.z };
}""")
M(soul, r"""
public static boolean bound(@PKG@.SoulState s, @REF@ t) {
  for (int k = 0; k < s.binds.size(); k++) if (t.equals(((@PKG@.SoulBind) s.binds.get(k)).t)) return true;
  return false;
}""")
# THE LOOK POINT: the enemy nearest your crosshair inside soul.aimCone within soul.lockRange (line of sight), else the first block your look
# hits within the reach (0.25 steps, 0.3 short of it), else none (looking at the sky). FIX ROUND 2 (critic: a ray-cast for every mob in the
# 27-block sphere): the cone + range test (Rico.aimed's own rule) runs FIRST and only mobs inside the cone are ray-cast, nearest the
# crosshair first, stopping at the first clear one (the same pick as Rico.aimed over the ray-cast set)
M(soul, r"""
public static double[] lookPoint(@CAC@ acc, @REF@ me, java.util.UUID u, double[] a, @PKG@.TravGrid g) {
  if (a == null || a.length < 6) return null;
  double rng = (double) @PKG@.ArmoryCfg.SOUL_RANGE;
  double half = (double) @PKG@.ArmoryCfg.SOUL_CONE * 0.5;
  java.util.List l = @PKG@.Shadow.near(acc, a[0], a[1], a[2], rng + 2.0);
  int n = l.size();
  double[] xs = new double[n];
  double[] ys = new double[n];
  double[] zs = new double[n];
  double[] offs = new double[n];
  double[] ds = new double[n];
  boolean[] cand = new boolean[n];
  for (int k = 0; k < n; k++) {
    cand[k] = false;
    Object o = l.get(k);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!ok(acc, t, me, u)) continue;
    double[] c = centre(acc, t);
    if (c == null) continue;
    double vx = c[0] - a[0];
    double vy = c[1] - a[1];
    double vz = c[2] - a[2];
    double d = Math.sqrt(vx * vx + vy * vy + vz * vz);
    if (d > rng || d < 0.3) continue;
    double off = @PKG@.TravMath.offDeg(a[3], a[4], a[5], vx, vy, vz);
    if (off > half) continue;
    xs[k] = c[0];
    ys[k] = c[1];
    zs[k] = c[2];
    offs[k] = off;
    ds[k] = d;
    cand[k] = true;
  }
  if (g != null) {
    while (true) {
      int i = -1;
      for (int k = 0; k < n; k++) {
        if (!cand[k]) continue;
        if (i < 0 || offs[k] < offs[i] - 1.0E-6 || (Math.abs(offs[k] - offs[i]) <= 1.0E-6 && ds[k] < ds[i])) i = k;
      }
      if (i < 0) break;
      cand[i] = false;
      LOOK_RAYS = LOOK_RAYS + 1L;
      if (@PKG@.TravMath.clear(g, a[0], a[1], a[2], xs[i], ys[i], zs[i])) return new double[] { xs[i], ys[i], zs[i] };
    }
  }
  if (g == null) return null;
  for (double d = 0.5; d <= rng + 1.0E-9; d = d + 0.25) {
    double x = a[0] + a[3] * d;
    double y = a[1] + a[4] * d;
    double z = a[2] + a[5] * d;
    int b = g.at((int) Math.floor(x), (int) Math.floor(y), (int) Math.floor(z));
    if (b != 0) {
      if (d <= 0.75) return null;
      return new double[] { x - a[3] * 0.3, y - a[4] * 0.3, z - a[5] * 0.3 };
    }
  }
  return null;
}""")
# NEW BINDINGS: every enemy within soul.lockRadius of the look point and soul.lockRange of your eye, LINE OF SIGHT from your eye to START,
# nearest to the point first, up to the tier's cap
M(soul, r"""
public static int bindNew(@PKG@.SoulState s, @CAC@ acc, @REF@ me, double[] p, double[] a, @PKG@.TravGrid g, long now) {
  int cap = cap(s.tier);
  if (p == null || a == null || s.binds.size() >= cap) return 0;
  double r = @PKG@.ArmoryCfg.SOUL_RADIUS;
  java.util.List l = @PKG@.Shadow.near(acc, p[0], p[1], p[2], r + 2.0);
  int n = l.size();
  @REF@[] rs = new @REF@[n];
  double[] ds = new double[n];
  for (int k = 0; k < n; k++) {
    rs[k] = null;
    Object o = l.get(k);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (bound(s, t) || !ok(acc, t, me, s.u)) continue;
    double[] c = centre(acc, t);
    if (c == null) continue;
    double d = dist(p[0], p[1], p[2], c[0], c[1], c[2]);
    if (d > r + 1.0E-9) continue;
    if (dist(a[0], a[1], a[2], c[0], c[1], c[2]) > (double) @PKG@.ArmoryCfg.SOUL_RANGE + 1.0E-9) continue;
    if (g == null || !@PKG@.TravMath.clear(g, a[0], a[1], a[2], c[0], c[1], c[2])) { LOS_REFUSED = LOS_REFUSED + 1L; continue; }
    rs[k] = t;
    ds[k] = d;
  }
  int added = 0;
  while (s.binds.size() < cap) {
    int best = -1;
    for (int k = 0; k < n; k++) if (rs[k] != null && (best < 0 || ds[k] < ds[best] - 1.0E-9)) best = k;
    if (best < 0) break;
    s.binds.add(new @PKG@.SoulBind(rs[best], now));
    rs[best] = null;
    added = added + 1;
    BINDS = BINDS + 1L;
  }
  if (added > 0) LAST_WHY = added + " new Binding" + (added == 1 ? "" : "s") + " (" + s.binds.size() + " of " + cap + ")";
  return added;
}""")
# the look of a Binding: a dotted line from the cage (in front of your hand) to the mob - wispy = sparse, solid = dense - in the tier colour;
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
}""")
M(soul, r"""
public static double[] handPos(double[] a) {
  if (a == null || a.length < 6) return null;
  return new double[] { a[0] + a[3] * 0.6, a[1] - 0.45 + a[4] * 0.6, a[2] + a[5] * 0.6 };
}""")
M(soul, r"""
public static double capHp(@CAC@ acc, @REF@ me, int tier) {
  if (tier < 0 || tier >= @PKG@.ArmoryCfg.SOUL_CAP.length) return 0.0;
  float mx = statOf(acc, me, hpIdx(), true);
  double base = mx > 0.0f ? (double) mx : 100.0;
  return base * @PKG@.ArmoryCfg.SOUL_CAP[tier] / 100.0;
}""")
# THE RELEASE: every Binding ends at once (nothing is dealt after it), the regen block is cleared, the stored healing starts to fade
M(soul, r"""
public static void release(@PKG@.SoulState s, String why, long now) {
  if (s == null) return;
  STATES.remove(s.u, s);
  int n = s.binds.size();
  s.binds.clear();
  if (s.blocked) { regen(s.u, 0L); s.blocked = false; }
  unbinding(s.u, now);
  RELEASES = RELEASES + 1L;
  LAST_RELEASE = why;
  LAST_WHY = "released (" + why + ")" + (n > 0 ? " - " + n + " Binding" + (n == 1 ? "" : "s") + " ended" : "");
}""")
# ONE TICK of a held soul weapon: (1) Bindings whose mob died / left / is past soul.snapRange end; (2) wispy ones grow solid while looked at
# (within the radius + 1 of the look point), snap after the grace; (3) new ones near the look point up to the cap; (4) every soul.tick the
# pulse: Mana for every Binding first (too little = all end, nothing dealt), then the damage through the whole pipeline, the stored healing,
# the regen block renewed; (5) the lines
M(soul, r"""
public static void step(@PKG@.SoulState s, @CB@ cb, @REF@ me, @PR@ pr, long now) {
  double dt = (double) (now - s.tickAt);
  if (dt < 0.0) dt = 0.0;
  if (dt > 1000.0) dt = 1000.0;
  s.tickAt = now;
  int tier = s.tier;
  double[] a = @PKG@.Leap.aim(cb, me, s.u, null);
  @WLD@ w = @PKG@.ArmoryTrav.worldOf(cb);
  @PKG@.TravGrid g = @PKG@.ArmoryTrav.grid(w);
  for (int k = s.binds.size() - 1; k >= 0; k--) {
    @PKG@.SoulBind b = (@PKG@.SoulBind) s.binds.get(k);
    String gone = null;
    if (b.t == null || !b.t.isValid() || @PKG@.ArmoryTrav.dead(cb, b.t)) gone = "its mob died";
    else {
      double[] c = centre(cb, b.t);
      if (c == null) gone = "its mob is gone";
      else if (a != null && dist(a[0], a[1], a[2], c[0], c[1], c[2]) > (double) @PKG@.ArmoryCfg.SOUL_SNAP + 1.0E-9) gone = "too far";
    }
    if (gone != null) { s.binds.remove(k); ENDS = ENDS + 1L; LAST_WHY = "a Binding ended (" + gone + ")"; }
  }
  boolean wispy = false;          // FIX ROUND 2 (critic: the scan ran with the cap full and every Binding solid = nothing could use it)
  for (int k = 0; k < s.binds.size(); k++) if (!((@PKG@.SoulBind) s.binds.get(k)).stable) { wispy = true; break; }
  boolean needLook = wispy || s.binds.size() < cap(tier);
  if (a == null) s.p = null;          // the look point: at most every SCAN_MS (an area query), kept in between
  else if (!needLook) { s.p = null; SCAN_SKIPS = SCAN_SKIPS + 1L; }          // lookAt kept: a freed slot re-scans on the next tick
  else if (now - s.lookAt >= SCAN_MS) { s.p = lookPoint(cb, me, s.u, a, g); s.lookAt = now; }
  double[] p = s.p;
  double r = @PKG@.ArmoryCfg.SOUL_RADIUS;
  long grace = Math.round(@PKG@.ArmoryCfg.SOUL_GRACE * 1000.0);
  long need = stabMs(@PKG@.ArmoryCfg.SOUL_STAB[tier]);
  for (int k = s.binds.size() - 1; k >= 0; k--) {
    @PKG@.SoulBind b = (@PKG@.SoulBind) s.binds.get(k);
    if (b.stable) continue;
    double[] c = centre(cb, b.t);
    boolean look = p != null && c != null && dist(p[0], p[1], p[2], c[0], c[1], c[2]) <= r + 1.0 + 1.0E-9;
    if (look) {
      b.seen = now;
      b.held = b.held + dt;
      if (b.held + 1.0E-6 >= (double) need) { b.stable = true; STABLES = STABLES + 1L; LAST_WHY = "a Binding is solid"; }
    } else if (now - b.seen > grace) {
      s.binds.remove(k);
      SNAPS = SNAPS + 1L;
      LAST_WHY = "a wispy Binding snapped (you looked away before it was solid)";
    }
  }
  int had = s.binds.size();
  if (p != null && had < cap(tier) && now >= s.scan) {
    s.scan = now + SCAN_MS;
    bindNew(s, cb, me, p, a, g, now);
  }
  int n = s.binds.size();
  long pm = pulseMs();
  if (n == 0) {
    s.last = now;
    if (s.blocked) { regen(s.u, 0L); s.blocked = false; unbinding(s.u, now); }
    return;
  }
  if (had == 0) s.last = now - pm;          // damage starts at once
  if (now - s.last >= pm) {
    double secs = (double) (now - s.last) / 1000.0;
    if (secs > 1.0) secs = 1.0;
    s.last = now;
    double mps = @PKG@.ArmoryCfg.SOUL_MPS[tier];
    double cost = drain(n, mps, secs);
    int mi = manaIdx();
    float cur = statOf(cb, me, mi, false);
    if (cur < 0.0f) {          // FIX ROUND (critic): an unreadable Mana stat never means free Bindings
      NO_MANA_STAT = NO_MANA_STAT + 1L;
      warn("nomana", "a binder's Mana could not be read - the Bindings end (no free hits)");
      release(s, "Mana could not be read", now);
      LATCH.put(s.u, Boolean.TRUE);
      LATCHED = LATCHED + 1L;
      return;
    }
    if ((double) cur + 1.0E-4 < cost) {
      OUT_OF_MANA = OUT_OF_MANA + 1L;
      release(s, "out of Mana", now);
      LATCH.put(s.u, Boolean.TRUE);          // FIX ROUND (critic): no new hold until right click is let go (no bind / fail loop every tick)
      LATCHED = LATCHED + 1L;
      @PKG@.ArmoryTrav.tell(pr, "Your Bindings broke - out of Mana.");
      return;
    }
    if (cost > 0.0) spend(cb, me, mi, cost);
    DRAINED = DRAINED + cost;
    s.drained = s.drained + cost;
    double per = dps(@PKG@.ArmoryCfg.SOUL_DPM, mps, @PKG@.ArmoryCfg.SOUL_MULT[tier]) * secs;
    double sum = 0.0;
    for (int k = 0; k < s.binds.size(); k++) {
      @PKG@.SoulBind b = (@PKG@.SoulBind) s.binds.get(k);
      if (@PKG@.ArmoryTrav.hit(cb, b.t, me, null, per)) { HITS = HITS + 1L; b.dealt = b.dealt + per; sum = sum + per; }
    }
    PULSES = PULSES + 1L;
    s.dealt = s.dealt + sum;
    if (sum > 0.0) store(s.u, sum * (double) @PKG@.ArmoryCfg.SOUL_STORE / 100.0, capHp(cb, me, tier), tier, s.gen, now);
    if (@PKG@.ArmoryCfg.SOUL_NOREGEN) { regen(s.u, now + pm * 3L + 500L); s.blocked = true; }
    else if (s.blocked) { regen(s.u, 0L); s.blocked = false; }
  }
  if (now >= s.fx && a != null && @PKG@.ArmoryCfg.SOUL_DOTS > 0) {
    s.fx = now + FX_MS;
    double[] from = handPos(a);
    int most = @PKG@.ArmoryCfg.SOUL_DOTS / (s.binds.size() > 0 ? s.binds.size() : 1);
    for (int k = 0; k < s.binds.size(); k++) {
      @PKG@.SoulBind b = (@PKG@.SoulBind) s.binds.get(k);
      line(cb, tier, from, centre(cb, b.t), b.stable, most);
    }
  }
}""")
# FIX ROUND (critics: a disconnect strands the state, the stored healing and armory:soul:<uuid>): every SWEEP_MS, a player not ticked for
# GONE_MS (left the game) loses the Bindings (released: the regen block cleared), the stored healing (armory:soul:<uuid> removed) and the latch
M(soul, r"""
public static int sweep(long now) {
  int n = 0;
  java.util.Iterator it = SEEN.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object k = e.getKey();
    Object v = e.getValue();
    if (!(k instanceof java.util.UUID)) { it.remove(); continue; }
    if (v instanceof Long && now - ((Long) v).longValue() <= GONE_MS) continue;
    java.util.UUID u = (java.util.UUID) k;
    it.remove();
    Object o = STATES.get(u);
    if (o instanceof @PKG@.SoulState) release((@PKG@.SoulState) o, "left the game", now);
    resetPool(u, "left the game");
    LATCH.remove(u);
    n = n + 1;
  }
  java.util.Iterator is = STATES.keySet().iterator();
  while (is.hasNext()) { Object k2 = is.next(); if (!SEEN.containsKey(k2)) { Object o2 = STATES.get(k2); if (o2 instanceof @PKG@.SoulState) release((@PKG@.SoulState) o2, "left the game", now); n = n + 1; } }
  java.util.Iterator ip = POOL.keySet().iterator();
  while (ip.hasNext()) { Object k3 = ip.next(); if (k3 instanceof java.util.UUID && !SEEN.containsKey(k3)) { resetPool((java.util.UUID) k3, "left the game"); n = n + 1; } }
  java.util.Iterator il = LATCH.keySet().iterator();
  while (il.hasNext()) { Object k4 = il.next(); if (!SEEN.containsKey(k4)) il.remove(); }
  SWEPT = SWEPT + (long) n;
  return n;
}""")
# TravTick, every tick of every player (world thread): the release reasons first (off, world change, death, profile switch, the weapon left
# the hand, let go), then the hold (class lock at its start)
M(soul, r"""
public static void tickPlayer(@REF@ ref, @ST@ st, @CB@ cb) {
  if (ref == null || !ref.isValid()) return;
  @PR@ pr = @PKG@.Kunai.prOf(cb, ref);
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  if (u == null) return;
  long now = now();
  @PKG@.SoulState s = (@PKG@.SoulState) STATES.get(u);
  if (s != null || POOL.containsKey(u) || LATCH.containsKey(u)) SEEN.put(u, Long.valueOf(now));          // FIX ROUND: the sweep's "still here"
  if (now - SWEEP_AT >= SWEEP_MS) { SWEEP_AT = now; try { sweep(now); } catch (Throwable ts) { warn("sweep", "the soul sweep failed (" + ts + ")"); } }
  if (s == null && POOL.isEmpty() && !@PKG@.ArmoryCfg.SOUL_ON) return;
  boolean dead = @PKG@.ArmoryTrav.dead(cb, ref);
  boolean mine = s != null || POOL.containsKey(u);          // FIX ROUND 2 (critic): the profile epoch only for a player with soul state
  long gen = mine ? @PKG@.ArmoryTree.gen(u) : 0L;
  if (s != null) {
    String why = null;
    if (!@PKG@.ArmoryCfg.SOUL_ON) why = "Soul Bindings off";
    else if (s.st != st) why = "world change";
    else if (dead) why = "death";
    else if (s.gen != gen) why = "profile switch";
    if (why != null) { release(s, why, now); s = null; }
  }
  if (mine) poolTick(u, dead, gen, now);
  if (!@PKG@.ArmoryCfg.SOUL_ON || dead) return;
  String item = @PKG@.Leap.hand(cb, ref, u);
  int tier = tierOf(item);
  if (s != null && (tier < 0 || !item.equals(s.item))) { release(s, "the soul weapon left your hand", now); s = null; }
  if (tier < 0) {          // FIX ROUND 2 (critic: a stale latch survived a let-go made with another item in hand)
    if (LATCH.containsKey(u) && !held(cb, ref, u)) LATCH.remove(u);
    return;
  }
  if (!held(cb, ref, u)) {
    if (s != null) release(s, "let go", now);
    LATCH.remove(u);
    return;
  }
  if (s == null && LATCH.containsKey(u)) return;          // FIX ROUND: out of Mana - let go of right click to bind again
  if (s == null) {
    if (!@PKG@.ArmoryTrav.allowed(u, item)) {
      LOCKED = LOCKED + 1L;
      LAST_WHY = "class lock";
      @PKG@.ArmoryTrav.tell(pr, "Only Priests can bind souls.");
      return;
    }
    if (!mine) gen = @PKG@.ArmoryTree.gen(u);
    s = new @PKG@.SoulState(u, st, tier, item, gen, now);
    SEEN.put(u, Long.valueOf(now));          // before STATES: another world's sweep never sees a state without its SEEN
    STATES.put(u, s);
    HOLDS = HOLDS + 1L;
  }
  step(s, cb, ref, pr, now);
}""")
M(soul, r"""
public static void clear() {
  java.util.Iterator it = STATES.values().iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (o instanceof @PKG@.SoulState && ((@PKG@.SoulState) o).blocked) regen(((@PKG@.SoulState) o).u, 0L);
  }
  STATES.clear();
  java.util.Iterator pk = POOL.keySet().iterator();
  while (pk.hasNext()) { Object k = pk.next(); if (k instanceof java.util.UUID) publish((java.util.UUID) k, 0.0); }
  POOL.clear();
  LATCH.clear();
  SEEN.clear();
}""")
# ---- armory:fn:soul (java.lang types only; never throws): UUID or {"get", UUID} -> Double stored HP (after the fade);
# {"take", UUID, Number maxHp} -> Double taken (at most the tier's cap % of that max Health); {"text"} -> String the live numbers
sfn.addInterface(pool.get("java.util.function.Function"))
C(sfn, "public SoulFn() { }")
M(sfn, r"""
public Object apply(Object arg) {
  try {
    long now = @PKG@.Soul.now();
    if (arg instanceof java.util.UUID) return Double.valueOf(@PKG@.Soul.poolNow((java.util.UUID) arg, now));
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 1 || !(a[0] instanceof String)) return null;
    String op = ((String) a[0]).trim().toLowerCase();
    if (op.equals("text")) return @PKG@.ArmoryCfg.SOUL_TEXT;
    if (a.length < 2 || !(a[1] instanceof java.util.UUID)) return null;
    java.util.UUID u = (java.util.UUID) a[1];
    if (op.equals("get")) return Double.valueOf(@PKG@.Soul.poolNow(u, now));
    if (op.equals("take")) {
      double mx = a.length > 2 && a[2] instanceof Number ? ((Number) a[2]).doubleValue() : 0.0;
      return Double.valueOf(@PKG@.Soul.take(u, mx, now));
    }
    return null;
  } catch (Throwable t) { return null; }
}""")
# ---- THE ESSENCE DROPS (SoulDropSys: NPCEntity + DeathComponent, once per death): a player's kill of a hostile / neutral monster rolls the
# essences of its zone (essence.zone; 0 = the vanilla volcanic caves) at essence.chance %; spawned with the engine's own item drop recipe
for f in ("public static final java.util.concurrent.ConcurrentHashMap ROLLED = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile java.util.function.BiFunction SPAWN = null;",          # HARNESS SEAM ONLY: (ItemStack list, Vector3d) instead of the world
          "public static volatile java.util.Map ENV = null;",          # HARNESS SEAM ONLY: Ref -> environment id
          "public static volatile double ROLL = -1.0;",          # HARNESS SEAM ONLY (< 0 in the game = random): the 0..100 roll
          "public static volatile long DEATHS = 0L;", "public static volatile long ROLLS = 0L;", "public static volatile long DROPS = 0L;",
          "public static volatile long NOZONE = 0L;", "public static volatile long SKIPPED = 0L;", "public static volatile String LAST_WHY = \"\";"):
    F(sdrop, f)
M(sdrop, r"""public static void warn(String key, String msg) { @PKG@.ArmoryLog.warnOnce("essence:" + key, msg); }""")
# pure: the zone of an environment id (Env_Zone2_... -> 2; -1 = none) / a volcanic cave env / a SkyyMobs level (the zone bands)
M(sdrop, r"""
public static int zoneOfEnv(String env) {
  if (env == null) return -1;
  int i = env.indexOf("Zone");
  if (i < 0 || i + 4 >= env.length()) return -1;
  char c = env.charAt(i + 4);
  return (c >= '0' && c <= '9') ? (int) (c - '0') : -1;
}""")
M(sdrop, r"""public static boolean volcanic(String env) { return env != null && env.indexOf("Caves_Volcanic") >= 0; }""")
M(sdrop, r"""
public static int zoneOfLevel(int lvl) {
  if (lvl <= 0) return -1;
  if (lvl <= 20) return 1;
  if (lvl <= 30) return 2;
  if (lvl <= 45) return 3;
  return 4;
}""")
# which essences may drop: zone z (or a volcanic cave) -> the indexes of ESS_NAMES whose essence.zone matches
M(sdrop, r"""
public static boolean matches(int i, int zone, boolean volc) {
  if (i < 0 || i >= @PKG@.ArmoryCfg.ESS_ZONE.length) return false;
  int z = (int) Math.round(@PKG@.ArmoryCfg.ESS_ZONE[i]);
  if (z == 0) return volc;
  return zone > 0 && z == zone;
}""")
M(sdrop, r"""
public static String envOf(@CAC@ acc, @REF@ r, Object npc, @VEC@ p, @WLD@ w) {
  java.util.Map seam = ENV;
  if (seam != null) { Object o = seam.get(r); return o == null ? null : String.valueOf(o); }
  int ei = Integer.MIN_VALUE;
  try { if (npc instanceof @NPC@) ei = ((@NPC@) npc).getEnvironment(); } catch (Throwable t0) { ei = Integer.MIN_VALUE; }
  if ((ei == Integer.MIN_VALUE || ei < 0) && w != null && p != null) {
    try {
      int x = (int) Math.floor(p.x);
      int y = (int) Math.floor(p.y);
      int z = (int) Math.floor(p.z);
      Object c = w.getChunkStore().getChunkComponent(@CHU@.indexChunkFromBlock(x, z), @BCH@.getComponentType());
      if (c instanceof @BCH@) ei = ((@BCH@) c).getEnvironment(x, y, z);
    } catch (Throwable t1) { ei = Integer.MIN_VALUE; }
  }
  if (ei == Integer.MIN_VALUE || ei < 0) return null;
  try {
    Object a = @ENVA@.getAssetMap().getAsset(ei);
    if (a instanceof @ENVA@) return ((@ENVA@) a).getId();
  } catch (Throwable t2) { }
  return null;
}""")
M(sdrop, r"""
public static int mobLevel(@WLD@ w, java.util.UUID nu) {
  java.util.function.Function f = @PKG@.ArmoryTrav.fn("mob:fn:level");
  if (f == null || nu == null) return -1;
  try {
    Object r = f.apply(new Object[] { w == null ? null : w.getName(), nu });
    return r instanceof Number ? ((Number) r).intValue() : -1;
  } catch (Throwable t) { return -1; }
}""")
M(sdrop, r"""
public static void prune(long now) {
  if (ROLLED.size() < 256) return;
  java.util.Iterator it = ROLLED.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object v = e.getValue();
    if (!(v instanceof Long) || now - ((Long) v).longValue() > 60000L) it.remove();
  }
}""")
# one dying NPC (world thread): 0 = nothing, n = essences dropped
M(sdrop, r"""
public static int roll(@REF@ r, @ST@ st, @CB@ cb) {
  if (!@PKG@.ArmoryCfg.ESS_ON || r == null || !r.isValid()) return 0;
  @DTH@ dc = (@DTH@) cb.getComponent(r, @DTH@.getComponentType());
  if (dc == null) return 0;
  if (cb.getComponent(r, @PLA@.getComponentType()) != null || @PKG@.Kunai.prOf(cb, r) != null) return 0;
  @UUIDC@ uc = (@UUIDC@) cb.getComponent(r, @UUIDC@.getComponentType());
  java.util.UUID nu = uc == null ? null : uc.getUuid();
  if (nu == null) return 0;
  long now = System.currentTimeMillis();
  prune(now);
  if (ROLLED.putIfAbsent(nu, Long.valueOf(now)) != null) return 0;
  DEATHS = DEATHS + 1L;
  @REF@ kr = null;
  try {
    @DMG@ d = dc.getDeathInfo();
    Object src = d == null ? null : d.getSource();
    if (src instanceof @DENT@) kr = ((@DENT@) src).getRef();
  } catch (Throwable tk) { kr = null; }
  if (kr == null || !kr.isValid()) { SKIPPED = SKIPPED + 1L; LAST_WHY = "not a player's kill"; return 0; }
  @PR@ kp = @PKG@.Kunai.prOf(cb, kr);
  if (kp == null) { SKIPPED = SKIPPED + 1L; LAST_WHY = "not a player's kill"; return 0; }
  try {
    Object pl = cb.getComponent(kr, @PLA@.getComponentType());
    if (pl instanceof @PLA@ && ((@PLA@) pl).getGameMode() == @GM@.Creative) { SKIPPED = SKIPPED + 1L; LAST_WHY = "creative"; return 0; }
  } catch (Throwable tg) { }
  if (@PKG@.Shadow.attitude(cb, r, kr) > 1) { SKIPPED = SKIPPED + 1L; LAST_WHY = "a friendly mob"; return 0; }
  @VEC@ p = @PKG@.ArmoryTrav.posOf(cb, r);
  if (p == null) return 0;
  @WLD@ w = @PKG@.ArmoryTrav.worldOf(st);
  String env = envOf(cb, r, cb.getComponent(r, @NPC@.getComponentType()), p, w);
  int zone = zoneOfEnv(env);
  boolean volc = volcanic(env);
  if (zone < 0 && !volc) zone = zoneOfLevel(mobLevel(w, nu));
  if (zone < 0 && !volc) { NOZONE = NOZONE + 1L; LAST_WHY = "no zone (env " + env + ")"; return 0; }
  java.util.ArrayList l = new java.util.ArrayList();
  java.util.ArrayList names = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.ArmoryDefs.ESS_IDS.length; i++) {
    if (!matches(i, zone, volc)) continue;
    ROLLS = ROLLS + 1L;
    double x = ROLL >= 0.0 ? ROLL : java.util.concurrent.ThreadLocalRandom.current().nextDouble() * 100.0;
    if (x < @PKG@.ArmoryCfg.ESS_PCT[i]) { l.add(new @IS@(@PKG@.ArmoryDefs.ESS_IDS[i], 1)); names.add(@PKG@.ArmoryDefs.ESS_NAMES[i]); }
  }
  LAST_WHY = "zone " + zone + (volc ? " (volcanic)" : "") + ": " + names;
  if (l.isEmpty()) return 0;
  @VEC@ at = new @VEC@(p.x, p.y + 1.0, p.z);
  java.util.function.BiFunction seam = SPAWN;
  if (seam != null) { seam.apply(l, at); DROPS = DROPS + (long) l.size(); return l.size(); }
  try {
    @HR@ hr = (@HR@) cb.getComponent(r, @HR@.getComponentType());
    @R3F@ rot = hr == null || hr.getRotation() == null ? new @R3F@(0.0f, 0.0f, 0.0f) : new @R3F@(hr.getRotation());
    @HOLD@[] hs = @ITC@.generateItemDrops(st, l, at, rot);
    if (hs == null || hs.length == 0) return 0;
    cb.addEntities(hs, @ADDR@.SPAWN);
    DROPS = DROPS + (long) l.size();
    return l.size();
  } catch (Throwable t) { warn("spawn:" + t.getClass().getName(), "an essence drop failed (" + t + ")"); return 0; }
}""")
C(sdsys, "public SoulDropSys() { super(); }")
M(sdsys, "public @QRY@ getQuery() { return @QRY@.and(new @QRY@[] { (@QRY@) @NPC@.getComponentType(), (@QRY@) @DTH@.getComponentType() }); }")
M(sdsys, "public boolean isParallel(int a, int b) { return false; }")
M(sdsys, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try { if (chunk != null) @PKG@.SoulDrop.roll(chunk.getReferenceTo(idx), store, cb); }
  catch (Throwable t) { @PKG@.SoulDrop.warn("tick:" + t.getClass().getName(), "the essence drop tick failed (" + t + ")"); }
}""")
'''
rep('''# ---- ArmoryTravSys.onEntityAdded (SPAWN of one of our projectiles): quick orbs -> range / pierce record; wand charged orb -> burst''',
    SOUL_JAVA + '''# ---- ArmoryTravSys.onEntityAdded (SPAWN of one of our projectiles): quick orbs -> range / pierce record; wand charged orb -> burst''')
# TravTick: the soul hold, per player (world thread), its own try
rep('''    try { @PKG@.Monk.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.12: the Monk moves (vault, bounds, rise, plunge, flowing fall)
    catch (Throwable tm) { @PKG@.Monk.warn("tick:" + tm.getClass().getName(), "Monk move tick failed (" + tm + ")"); }
''', '''    try { @PKG@.Monk.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.12: the Monk moves (vault, bounds, rise, plunge, flowing fall)
    catch (Throwable tm) { @PKG@.Monk.warn("tick:" + tm.getClass().getName(), "Monk move tick failed (" + tm + ")"); }
    try { @PKG@.Soul.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.19: the Soul Orb / Cage Bindings (hold right click)
    catch (Throwable ts) { @PKG@.Soul.warn("tick:" + ts.getClass().getName(), "Soul Binding tick failed (" + ts + ")"); }
''')

# ---------------------------------------------------------------------------------------------------------------- the plugin
rep('''               "armory:grapple", "armory:leap", "armory:book", "armory:kunai", "armory:stun", "armory:shadow", "armory:monk"]''',
    '''               "armory:grapple", "armory:leap", "armory:book", "armory:kunai", "armory:stun", "armory:shadow", "armory:monk",
               "armory:soul", "armory:fn:soul"]          # 0.1.19 (+ armory:soul:<uuid>, removed by Soul.clear)''')
rep('''  try { getEntityStoreRegistry().registerSystem(new @PKG@.GrappleFallSys()); @PKG@.Grapple.SYS_FALL = true; }
  catch (Throwable t9) { @PKG@.ArmoryLog.warn("GrappleFallSys could not be registered: " + t9 + " - grapple landings take normal fall damage"); }
}""" % (ADRS, ONADD))''', '''  try { getEntityStoreRegistry().registerSystem(new @PKG@.GrappleFallSys()); @PKG@.Grapple.SYS_FALL = true; }
  catch (Throwable t9) { @PKG@.ArmoryLog.warn("GrappleFallSys could not be registered: " + t9 + " - grapple landings take normal fall damage"); }
  // 0.1.19: the zone essence drops (the Bindings ride TravTick)
  try { getEntityStoreRegistry().registerSystem(new @PKG@.SoulDropSys()); SYS_DROP = true; }
  catch (Throwable t10) { SYS_DROP = false; @PKG@.ArmoryLog.warn("SoulDropSys could not be registered: " + t10 + " - no zone essence drops this start"); }
}""" % (ADRS, ONADD))''')
rep('''C(pl, "public SkyyArmoryPlugin(@JPI@ init) { super(init); }")''',
    '''F(pl, "public static volatile boolean SYS_DROP = false;")          # 0.1.19
C(pl, "public SkyyArmoryPlugin(@JPI@ init) { super(init); }")''')
rep('''  b.put("armory:monk", @PKG@.ArmoryCfg.MONK_TEXT);          // 0.1.12
''', '''  b.put("armory:monk", @PKG@.ArmoryCfg.MONK_TEXT);          // 0.1.12
  b.put("armory:soul", @PKG@.ArmoryCfg.SOUL_TEXT);          // 0.1.19
  b.put("armory:fn:soul", new @PKG@.SoulFn());
''')
rep('''  @PKG@.Monk.clear();          // 0.1.12: the armory:monkmove:<uuid> flags go too
}""" % jarr(BRIDGE_KEYS))''', '''  @PKG@.Monk.clear();          // 0.1.12: the armory:monkmove:<uuid> flags go too
  @PKG@.Soul.clear();          // 0.1.19: every regen block cleared, the armory:soul:<uuid> values go too
}""" % jarr(BRIDGE_KEYS))''')
rep('''  @PKG@.Monk.clear();          // 0.1.12
  @PKG@.Monk.DEBUG.clear();
  systems();
  publish();''', '''  @PKG@.Monk.clear();          // 0.1.12
  @PKG@.Monk.DEBUG.clear();
  @PKG@.Soul.clear();          // 0.1.19
  @PKG@.SoulDrop.ROLLED.clear();
  systems();
  publish();''')
rep('''  @PKG@.ArmoryLog.info("@VERSION@ " + @PKG@.ArmoryCfg.SIG_TEXT);
''', '''  @PKG@.ArmoryLog.info("@VERSION@ " + @PKG@.ArmoryCfg.SIG_TEXT);
  @PKG@.ArmoryLog.info("@VERSION@ " + @PKG@.ArmoryCfg.SOUL_TEXT + " (essence drop system " + SYS_DROP + "; SkyySkills regen block "
    + (@PKG@.ArmoryTrav.fn(@PKG@.Soul.REGEN_FN) != null ? "found" : "not loaded yet - read at use time; without SkyySkills 0.4.30 Mana regenerates while bound") + ")");
''')
rep('''  @PKG@.Monk.clear();          // 0.1.12
  @PKG@.Monk.DEBUG.clear();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''', '''  @PKG@.Monk.clear();          // 0.1.12
  @PKG@.Monk.DEBUG.clear();
  @PKG@.Soul.clear();          // 0.1.19 (unpublish did it too; a second call is a no-op)
  @PKG@.SoulDrop.ROLLED.clear();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''')

# ---------------------------------------------------------------------------------------------------------------- the jar checks + prints
rep('''"Wand signature (fills as your shots hit): a bolt that ricochets through up to 8 enemies. "''',
    '''"Wand signature (fills as your shots hit): a bolt that ricochets through up to 8 enemies. "
                 "Priest Soul Orb + 7 Soul Cages: hold right click to bind nearby enemies (steady damage for steady Mana, stored as healing); "
                 "monsters drop zone essences. "''')
rep('''    assert sorted(n for n in _names if os.path.basename(n)[:-5] in VBO_IDS) == sorted(VBO_OVR[i][0] for i in VBO_IDS), "0.1.11: exactly 2 vanilla Bo files"
''', '''    assert sorted(n for n in _names if os.path.basename(n)[:-5] in VBO_IDS) == sorted(VBO_OVR[i][0] for i in VBO_IDS), "0.1.11: exactly 2 vanilla Bo files"
    assert sorted(n for n in _names if n in set(SOUL_FILES)) == SOUL_FILES and len([n for n in SOUL_FILES if n.startswith("Server/Item/Items/")]) == 10 \\
        and len([n for n in _names if "/SoulCage/" in n]) == 8 * 2 + 1 and not [n for n in _names if os.path.basename(n)[:-5] in ESS_IDS and "SkyyArmory" not in n], \\
        "0.1.19: the %d Soul files (10 items: 8 soul weapons + 2 essences; no vanilla essence overridden)" % len(SOUL_FILES)
''')
rep('''AZ.close()''', '''print("0.1.19 soul orb: %d rows + %d tables + 1 read-only row (Server Setup > Armory > Soul Orb + essences); %d items, %d files; SoulBind / SoulState / "
      "Soul (TravTick) + SoulFn (armory:fn:soul) + SoulDrop / SoulDropSys (essence drops); partner SkyySkills 0.4.30 (skill:fn:regenblock)"
      % (len(CFG_SOUL), len(SOUL_TAB), len(SOUL_IDS) + 2, len(SOUL_FILES)))
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


hrep('"""SkyyArmory 0.1.18 - test harness. GENERATED by tools/armory_0_1_18_patch.py from test_skyyarmory_0.1.17.py - edit the patch, never this file.',
     '''"""SkyyArmory 0.1.19 - test harness. GENERATED by tools/armory_0_1_19_patch.py from test_skyyarmory_0.1.18.py - edit the patch, never this file.
Run: python SkyyArmory/test_skyyarmory_0.1.19.py --dir tools/dev/scratch/<task>/harness   (--no-set skips the one-JVM SET run, --keep keeps it)
Every 0.1.18 check still runs on the 0.1.18 shape: JZ19 = the real 0.1.19 jar; JZ = the jar AS THE 0.1.18 CHECKS KNOW IT - the new Soul Orb
files hidden (8 items, 2 essences + their art, the root + 2 interactions, 16 particle files, the cage art), the lang read as the 0.1.18 jar's
bytes, the manifest = the real one with the 0.1.18 description (P21 proves the real files are exactly the planned change of those bytes); the
classes are the real 0.1.19 ones (A / X / T / V / every Java path; the 6 new classes SoulBind, SoulState, Soul, SoulFn, SoulDrop, SoulDropSys
are left out of the older class-list compares); the old row checks see the new rows / category; R21f now compares 0.1.17 -> 0.1.18 (history),
R22h 0.1.18 -> 0.1.19.
NEW P21 (Python) + R22 (JVM, after R21) EXECUTE every 0.1.19 path:
  P21  vs the 0.1.18 jar: new = exactly the Soul files + 6 classes, changed = the lang (only appended lines) + the manifest (version + one
       sentence); the 8 items (Priest prefix, Secondary = the Charging root, art paths, recipes chained tier by tier with bars + essence),
       the 2 essences (vanilla essence shape), the root (Charging, AllowIndefiniteHold, Next "0" -> release), 8 finite particle systems,
       no vanilla essence overridden; the cage art = the reviewed copy's geometry + spin
  R22  a: the rows + tables + defaults + clamps + the default file + armory:soul; b: the pure maths (tierOf, cap, dps, drain, stabilize,
       store cap + fade); c: THE BIND CAP PER TIER (24 mobs packed at the look point: 1 / 2 / 4 / 6 / 10 / 14 / 16 / 20); d: LINE OF SIGHT to
       START (a wall = no Binding), NOT to keep (a wall added later = still drained + hit); e: STABILIZE TIMING (wispy until the tier's time,
       looking away before it = snap after the grace, after it = kept; a solid Binding never snaps) + binding the NEXT group up to the cap;
       f: DRAIN + DAMAGE PER PULSE (Mana per Binding per second x n, damage per Binding through the damage pipeline, stored 50 % up to the
       cap, the fade after the release); g: THE REGEN BLOCK on (renewed every pulse) / off (cleared at the release; none without Bindings);
       h: RELEASES - let go, Mana 0 (nothing dealt, all end), death (+ the pool reset), world change, profile switch (+ the pool reset),
       weapon swap, soul.enabled off; NO DAMAGE AFTER A RELEASE; a dead / too-far mob ends its own Binding; i: CLASS LOCK (class:fn:allowed
       FALSE = nothing bound, nothing drained); j: THE REAL HOLD on a real InteractionManager chain (our root at its Charging = held; past it /
       another root / Primary = not); k: armory:fn:soul get / take / text; l: ESSENCE DROPS (zone by env / volcanic / SkyyMobs level, chances,
       once per death, never a player kill-less / Creative / friendly death, the seam spawn); m: vs the 0.1.18 jar method by method.

0.1.18 harness: SkyyArmory 0.1.18 - test harness. GENERATED by tools/armory_0_1_18_patch.py from test_skyyarmory_0.1.17.py - edit the patch, never this file.''')
hrep('VERSION = "0.1.18"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.18 SkyyArmory"',
     'VERSION = "0.1.19"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.19 SkyyArmory"')
hrep('os.path.join(SCRATCH_ROOT, "armory0118", "harness")', 'os.path.join(SCRATCH_ROOT, "armory0119", "harness")')
hrep('raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.18.py', 'raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.19.py')
hrep('Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.18"))', 'Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.19"))')
for _v in ('"[SkyyArmory] 0.1.18 ready" in m_', '"0.1.18 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_',
           '"0.1.18 crossbow grapple: grapple on" in m_',
           '"0.1.18 monk moves on - Pole-Vault (Bo hold): lunge 3 in 0.2 s, 4.5 up x 7 forward (push x2.1)" in m_',
           '"0.1.18 wand signature on - the signature key when the meter is full (20; quick-shot hit +1, charged hit +2)" in m_',
           'come from Skyy:0.1.18 SkyyArmory" in str(r[1])'):
    hrep(_v, _v.replace("0.1.18", "0.1.19"))
hrep('t_.replace("0.1.18", "V").replace("0.1.17", "V")', 't_.replace("0.1.19", "V").replace("0.1.18", "V").replace("0.1.17", "V")')
hrep("    MN21, MO21 = methods_of(JAR), methods_of(OLD117)",
     "    MN21, MO21 = methods_of(OLD118), methods_of(OLD117)          # 0.1.19: R21f = the 0.1.18 round's compare (history); R22m = 0.1.18 -> 0.1.19")
hrep('''            cmp21[c_] = "only in " + ("0.1.18" if c_ in MN21 else "0.1.17")''',
     '''            cmp21[c_] = "only in " + ("0.1.18" if c_ in MN21 else "0.1.17")          # (0.1.19: MN21 = the 0.1.18 jar)''')
# ---- the jar as the 0.1.18 checks know it (a new outermost view; every older view builds on it)
hrep('''JZ = zipfile.ZipFile(JAR)
# 0.1.15: JZ15 = the real 0.1.15 jar (P17 / R18);''', '''JZ = zipfile.ZipFile(JAR)
# 0.1.19: JZ19 = the real 0.1.19 jar (P21 / R22); from here on JZ is the jar AS THE 0.1.18 CHECKS KNOW IT: the new Soul files hidden (not the
# classes - A / X verify every class), the lang read as the 0.1.18 jar's bytes, the manifest = the real one with the 0.1.18 description
JZ19 = JZ
OLD118 = os.path.join(HERE, "SkyyArmory-0.1.18.jar")
if not os.path.isfile(OLD118):
    raise SystemExit("the 0.1.19 harness needs SkyyArmory-0.1.18.jar (the base, the SET pin) next to it: %s" % OLD118)
OZ118 = zipfile.ZipFile(OLD118)
SOUL19_IDS = ["Weapon_Wand_SoulOrb"] + ["Weapon_Wand_SoulCage_%s" % m_ for m_ in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")]
SOUL19_TIERS = ["Orb", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
SOUL19_CLS = ["com/skyy/armory/%s.class" % c_ for c_ in ("Soul", "SoulBind", "SoulDrop", "SoulDropSys", "SoulFn", "SoulState")]
SOUL19_LANG = "Server/Languages/en-US/server.lang"
SOUL19_NEW = sorted(n_ for n_ in JZ19.namelist() if n_ not in set(OZ118.namelist()) and not n_.endswith(".class"))


class Z118(object):
    """the 0.1.19 jar as the 0.1.18 checks know it (read only)"""
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


JZ = Z118(JZ19, OZ118, SOUL19_NEW, [SOUL19_LANG])
# 0.1.15: JZ15 = the real 0.1.15 jar (P17 / R18);''')
# the class-list compares of the older rounds: the 6 new 0.1.19 classes are P21's
hrep('''_p15nn, _p15on = set(JZ13.namelist()) - set(SIG14_CLS), set(OZ112.namelist())''',
     '''_p15nn, _p15on = set(JZ13.namelist()) - set(SIG14_CLS) - set(SOUL19_CLS), set(OZ112.namelist())''')
hrep('''_n16, _o16 = set(JZ14.namelist()), set(OZ113.namelist())''', '''_n16, _o16 = set(JZ14.namelist()) - set(SOUL19_CLS), set(OZ113.namelist())          # 0.1.19: the Soul classes are P21's''')
for _p in ("18", "19", "20"):
    hrep('''_c%sn, _c%so = sorted(n_ for n_ in _n%s if n_.endswith(".class")),''' % (_p, _p, _p),
         '''_c%sn, _c%so = sorted(n_ for n_ in _n%s if n_.endswith(".class") and n_ not in SOUL19_CLS),''' % (_p, _p, _p))
hrep('''    nn_ = [n_ for n_ in JREAL.namelist() if n_ not in SIG14_CLS]          # 0.1.14: Rico / RicoChain are R17's''',
     '''    nn_ = [n_ for n_ in JREAL.namelist() if n_ not in SIG14_CLS and n_ not in SOUL19_CLS]          # 0.1.14: Rico / RicoChain are R17's; 0.1.19: the Soul classes R22's''')
hrep('''    check(len(names) == 53, "A: 53 classes (46 SkyyArmory incl.''', '''    check(len(names) == 59, "A: 59 classes (52 SkyyArmory incl. 0.1.19's 6 Soul classes +''')
hrep('''"54 of 54 items, 358 of 358 interactions, 66 of 66 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.19 SkyyArmory" in str(r[1])''',
     '''"64 of 64 items, 360 of 360 interactions, 66 of 66 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.19 SkyyArmory" in str(r[1])''')
# ---- L: the 0.1.19 interactions + root + items (the real files) go into the stores before the pack check (it counts every id the jar ships)
hrep('''    check(not bad15l and len(objs15l) == 3, "L (0.1.15): the 3 Untiered items decode (no unknown key, no failed validation) and go into the store: %s" % bad15l[:3])
''', '''    check(not bad15l and len(objs15l) == 3, "L (0.1.15): the 3 Untiered items decode (no unknown key, no failed validation) and go into the store: %s" % bad15l[:3])
    bad19l, n19l = [], 0          # 0.1.19: the Soul interactions, the root, the 10 items (the real files) into the stores - the pack check counts them
    for c_, pre_ in ((INTc, "Server/Item/Interactions/"), (ROOTc, "Server/Item/RootInteractions/"), (ITMc, "Server/Item/Items/")):
        objs_ = []
        for n_ in SOUL19_NEW:
            if n_.startswith(pre_) and n_.endswith(".json"):
                o_, w_, ei_ = dec17(c_, os.path.basename(n_)[:-5], JZ19.read(n_).decode("utf-8"))
                if o_ is None or w_:
                    bad19l.append("%s: %s" % (n_, w_))
                else:
                    objs_.append(o_)
                    n19l += 1
        load(c_, objs_, PACK)
    check(not bad19l and n19l == 13, "L (0.1.19): the 2 Soul interactions, the root and the 10 items (8 Soul weapons + 2 essences) decode (no unknown key, "
                                     "no failed validation) and go into the stores: %d %s" % (n19l, bad19l[:3]))
''')


# ---- the older checks that list classes / rows / systems / TravTick calls: + the 0.1.19 parts
hrep('''_n17, _o17 = set(JZ15.namelist()), set(OZ114.namelist())''',
     '''_n17, _o17 = set(JZ15.namelist()) - set(SOUL19_CLS), set(OZ114.namelist())          # 0.1.19: the Soul classes are P21's''')
hrep('''                                             "chargeQuick", "chargeCharged", "players", "refundMiss")]      # 0.1.14 the wand signature
''', '''                                             "chargeQuick", "chargeCharged", "players", "refundMiss")]      # 0.1.14 the wand signature
    NEW_ROWS += ["soul.enabled", "soul.damagePerMana", "soul.tick", "soul.lockRadius", "soul.lockRange", "soul.snapRange", "soul.aimCone",
                 "soul.wispyGrace", "soul.storePercent", "soul.decayPercent", "soul.noRegen", "soul.lineDots", "essence.drops"]      # 0.1.19 the Soul Orb
''')
hrep('''             "kunai.stamina", "kunai.mana", "ret.window", "ret.radius", "dagger.shadowStep.cooldown"]      # 0.1.6 per-metal tables + 0.1.8's
''', '''             "kunai.stamina", "kunai.mana", "ret.window", "ret.radius", "dagger.shadowStep.cooldown"]      # 0.1.6 per-metal tables + 0.1.8's
    TAB16 += ["soul.bindings", "soul.manaPerSecond", "soul.damageMult", "soul.stabilize", "soul.storeCap", "essence.chance", "essence.zone"]      # 0.1.19
''')
assert ts.count("10 + NN + 14") == 4
ts = ts.replace("10 + NN + 14", "10 + NN + len(TAB16)")          # 0.1.19: the 7 Soul tables follow the 14 older ones
hrep('''          and len(keys) == 10 + NN + len(TAB16) + 8 + 8 + 5 + 2 + 2 + 17 + 20 + 3 + 2 + 1,''',
     '''          and len(keys) == 10 + NN + len(TAB16) + 8 + 8 + 5 + 2 + 2 + 17 + 20 + 3 + 2 + 1 + 1,          # 0.1.19: + fixed.soul''')
hrep('''    check(len(caps) == 2 and all(len(c) == 7 for c in caps) and [str(x.getClass().getSimpleName()) for x in caps[0]] == [
              "ArmoryTuneSys", "ArmorySpawnSys", "ArmoryTravSys", "ArmoryHitSys", "TravTick", "GrappleBoltSys", "GrappleFallSys"]''',
     '''    check(len(caps) == 2 and all(len(c) == 8 for c in caps) and [str(x.getClass().getSimpleName()) for x in caps[0]] == [
              "ArmoryTuneSys", "ArmorySpawnSys", "ArmoryTravSys", "ArmoryHitSys", "TravTick", "GrappleBoltSys", "GrappleFallSys", "SoulDropSys"]''')
hrep('''"T: setup() hands the registry exactly 7 systems (one registerSystem each; 0.1.2: + GrappleBoltSys, GrappleFallSys)''',
     '''"T: setup() hands the registry exactly 8 systems (one registerSystem each; 0.1.2: + GrappleBoltSys, GrappleFallSys; 0.1.19: + SoulDropSys)''')
hrep('''    check(tt4.count("tickPlayer") == 5 and "onBowShot" in gb4,''', '''    check(tt4.count("tickPlayer") == 6 and "onBowShot" in gb4,''')
hrep('''"kunaiModel" in gb10 and tt10.count("tickPlayer") == 5 and''', '''"kunaiModel" in gb10 and tt10.count("tickPlayer") == 6 and''')

# ---- P21 (Python): the 0.1.19 files before the JVM part
P21 = r'''
# ================================================================================================================ P21. 0.1.19 the Soul Orb (pure files)
S21_ITEMS = dict((i_, "Server/Item/Items/Weapon/Wand/%s.json" % i_) for i_ in SOUL19_IDS)
S21_ESS = dict((i_, "Server/Item/Items/Ingredient/%s.json" % i_) for i_ in ("SkyyArmory_Essence_Earth", "SkyyArmory_Essence_Light"))
S21_ROOT = "Server/Item/RootInteractions/Weapons/Wand/SkyyArmory/SkyyArmory_Soul_Bind.json"
S21_INTS = {"SkyyArmory_Soul_Bind": "Server/Item/Interactions/Weapons/Wand/SkyyArmory/SkyyArmory_Soul_Bind.json",
            "SkyyArmory_Soul_Release": "Server/Item/Interactions/Weapons/Wand/SkyyArmory/SkyyArmory_Soul_Release.json"}
S21_ART = sorted(["Common/Items/Weapons/SoulCage/SkyyArmory_SoulOrb.blockymodel", "Common/Items/Weapons/SoulCage/SkyyArmory_SoulOrb_Texture.png",
                  "Common/Icons/ItemsGenerated/SkyyArmory_SoulOrb.png", "Common/Items/Weapons/SoulCage/SkyyArmory_SoulCage_Spin.blockyanim"]
                 + ["Common/Items/Weapons/SoulCage/SkyyArmory_%s%s" % (m_, x_) for m_ in SOUL19_TIERS[1:] for x_ in (".blockymodel", "_Texture.png")]
                 + ["Common/Icons/ItemsGenerated/SkyyArmory_SoulCage_%s.png" % m_ for m_ in SOUL19_TIERS[1:]]
                 + ["Common/Items/SkyyArmory/Essence/%s_Texture.png" % i_ for i_ in S21_ESS] + ["Common/Icons/ItemsGenerated/%s.png" % i_ for i_ in S21_ESS])
S21_PSYS = dict((m_, "Server/Particles/SkyyArmory/SkyyArmory_Soul_%s.particlesystem" % m_) for m_ in SOUL19_TIERS)
_ps21 = dict((m_, json.loads(JZ19.read(p_).decode("utf-8"))) for m_, p_ in S21_PSYS.items())
S21_PSP = sorted("Server/Particles/SkyyArmory/Spawners/%s.particlespawner" % e_["SpawnerId"] for d_ in _ps21.values() for e_ in d_["Spawners"])
S21_ALL = sorted(list(S21_ITEMS.values()) + list(S21_ESS.values()) + [S21_ROOT] + list(S21_INTS.values()) + S21_ART + list(S21_PSYS.values()) + S21_PSP)
_n21, _o21 = set(JZ19.namelist()), set(OZ118.namelist())
check(sorted(_n21 - _o21) == sorted(S21_ALL + SOUL19_CLS) and not (_o21 - _n21) and SOUL19_NEW == S21_ALL,
      "P21: vs SkyyArmory-0.1.18.jar - new = exactly the %d Soul files (8 items, 2 essences, the root + 2 interactions, %d art files, 8 particle "
      "systems + %d spawners) + the 6 Soul classes, none gone: %s / %s" % (len(S21_ALL), len(S21_ART), len(S21_PSP), sorted(_n21 ^ set(list(_o21) + S21_ALL + SOUL19_CLS))[:6],
                                                                           sorted(set(SOUL19_NEW) ^ set(S21_ALL))[:6]))
_d21 = sorted(n_ for n_ in _n21 & _o21 if not n_.endswith(".class") and n_ != "manifest.json" and JZ19.read(n_) != OZ118.read(n_))
_lo21, _ln21 = OZ118.read(SOUL19_LANG).decode("utf-8"), JZ19.read(SOUL19_LANG).decode("utf-8")
_add21 = _ln21[len(_lo21):].strip("\n").split("\n") if _ln21.startswith(_lo21) else None
_m21n, _m21o = json.loads(JZ19.read("manifest.json").decode("utf-8")), json.loads(OZ118.read("manifest.json").decode("utf-8"))
_SENT21 = ("Priest Soul Orb + 7 Soul Cages: hold right click to bind nearby enemies (steady damage for steady Mana, stored as healing); "
           "monsters drop zone essences. ")
check(_d21 == [SOUL19_LANG] and _add21 is not None and len(_add21) == 20
      and sorted(l_.split(" = ")[0] for l_ in _add21) == sorted(["items.%s.%s" % (i_, k_) for i_ in SOUL19_IDS + sorted(S21_ESS) for k_ in ("name", "description")])
      and dict(_m21n, Version=None, Name=None, Description=None) == dict(_m21o, Version=None, Name=None, Description=None)
      and _m21n["Version"] == VERSION and _m21n["Description"].replace(_SENT21, "") == _m21o["Description"] and _SENT21 in _m21n["Description"],
      "P21: the only changed non-class files = the lang (0.1.18's text + exactly the 20 new name / description lines) and the manifest (version + "
      "one sentence): %s %s" % (_d21, (_add21 or [])[:3]))
_it21 = dict((i_, json.loads(JZ19.read(p_).decode("utf-8"))) for i_, p_ in S21_ITEMS.items())
_ess21 = dict((i_, json.loads(JZ19.read(p_).decode("utf-8"))) for i_, p_ in S21_ESS.items())
_root21 = json.loads(JZ19.read(S21_ROOT).decode("utf-8"))
_int21 = dict((i_, json.loads(JZ19.read(p_).decode("utf-8"))) for i_, p_ in S21_INTS.items())
check(_root21 == {"Interactions": ["SkyyArmory_Soul_Bind"]}
      and _int21["SkyyArmory_Soul_Bind"] == {"Type": "Charging", "Effects": {"ItemAnimationId": "CastLeftCharging"}, "AllowIndefiniteHold": True,
                                            "DisplayProgress": False, "Next": {"0": "SkyyArmory_Soul_Release"}}
      and _int21["SkyyArmory_Soul_Release"] == {"Type": "Simple", "RunTime": 0.05}
      and "CastLeftCharging" in aj("anim", "Wand")["Animations"] and not ahas("root", "SkyyArmory_Soul_Bind") and not ahas("int", "SkyyArmory_Soul_Bind"),
      "P21: the root = one Charging (the wand's hold pose, AllowIndefiniteHold, any release -> the short Release Simple) - the kunai return's "
      "shape; nothing spends Mana client-side (the server drains while the chain sits in the Charging): %s" % _int21)
_ESS21 = {"Life": "Ingredient_Life_Essence", "Fire": "Ingredient_Fire_Essence", "Earth": "SkyyArmory_Essence_Earth", "Frost": "Ingredient_Ice_Essence",
          "Storm": "Ingredient_Lightning_Essence", "Void": "Ingredient_Void_Essence", "Light": "SkyyArmory_Essence_Light"}
_LADDER21 = [None, ("Life", 15), ("Fire", 15), ("Earth", 15), ("Frost", 12), ("Storm", 12), ("Void", 10), ("Light", 10)]
_bad21 = []
for t_, i_ in enumerate(SOUL19_IDS):
    d_ = _it21[i_]
    if d_.get("Interactions") != {"Secondary": "SkyyArmory_Soul_Bind"} or d_.get("PlayerAnimationsId") != "Wand" or not i_.startswith("Weapon_Wand_"):
        _bad21.append("%s: interactions / pose %s" % (i_, d_.get("Interactions")))
    for f_ in ("Model", "Texture", "Icon"):
        if ("Common/" + d_[f_]) not in _n21:
            _bad21.append("%s: %s %s not in the jar" % (i_, f_, d_[f_]))
    if (t_ == 0) != ("Animation" not in d_) or (t_ > 0 and d_["Animation"] != "Items/Weapons/SoulCage/SkyyArmory_SoulCage_Spin.blockyanim"):
        _bad21.append("%s: Animation %s" % (i_, d_.get("Animation")))
    r_ = d_.get("Recipe") or {}
    inp_ = [(x_.get("ItemId"), x_.get("Quantity")) for x_ in r_.get("Input", [])]
    if t_ == 0:
        want_ = [("Ingredient_Life_Essence", 20), ("Ingredient_Crystal_Blue", 1), ("Ingredient_Stick", 4), ("Ingredient_Fibre", 1)]
    else:
        m_ = SOUL19_TIERS[t_]
        bars_ = [x_ for x_ in aj("item", "Weapon_Shortbow_" + (m_ if m_ != "Onyxium" else "Mithril"))["Recipe"]["Input"] if str(x_.get("ItemId", "")).startswith("Ingredient_Bar_")]
        want_ = [(SOUL19_IDS[t_ - 1], 1), ("Ingredient_Bar_" + m_, int(bars_[0]["Quantity"])), (_ESS21[_LADDER21[t_][0]], _LADDER21[t_][1])]
    if inp_ != want_ or not any(b_.get("Id") == "Weapon_Bench" and b_.get("Type") == "Crafting" for b_ in r_.get("BenchRequirement", [])):
        _bad21.append("%s: recipe %s (want %s)" % (i_, inp_, want_))
for i_, d_ in _ess21.items():
    v_ = aj("item", "Ingredient_Life_Essence")
    if d_["Model"] != v_["Model"] or d_["IconProperties"] != v_["IconProperties"] or d_["Categories"] != v_["Categories"] or d_.get("MaxStack") != 100 \
            or ("Common/" + d_["Texture"]) not in _n21 or ("Common/" + d_["Icon"]) not in _n21:
        _bad21.append("%s: not the vanilla essence shape" % i_)
_vov21 = [n_ for n_ in _n21 if os.path.basename(n_)[:-5] in ("Ingredient_Life_Essence", "Ingredient_Fire_Essence", "Ingredient_Ice_Essence",
                                                              "Ingredient_Lightning_Essence", "Ingredient_Void_Essence")]
_cls_src21 = open(os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_%s.py" % PIN["SkyyClasses"]), encoding="utf-8").read()
_pri21 = re.search(r'"name": "Priest".*?"weapons": \[(.*?)\]', _cls_src21, re.S)
check(not _bad21 and not _vov21 and _pri21 is not None and '("Weapon_Wand_", "wands")' in _pri21.group(1)
      and all(ahas("item", x_) for x_ in ("Ingredient_Life_Essence", "Ingredient_Fire_Essence", "Ingredient_Ice_Essence", "Ingredient_Lightning_Essence",
                                          "Ingredient_Void_Essence", "Ingredient_Crystal_Blue", "Ingredient_Stick", "Ingredient_Fibre")),
      "P21: the 8 Soul items - Weapon_Wand_ ids (= the pinned SkyyClasses %s Priest prefix: the class lock), Secondary = our root, the wand pose, "
      "their own art in the jar, the cages spin; RECIPES CHAINED tier by tier: the Soul Orb = 20 Life + 1 Blue Crystal + 4 Sticks + 1 Fibre, every "
      "cage = the tier before + that metal wand's bars + its essence (Life 15, Fire 15, Earth 15, Frost (Ice) 12, Storm (Lightning) 12, Void 10, "
      "Light 10) at the Weapon Bench; the 2 new essences = the vanilla essence shape + our art; no vanilla essence file overridden: %s %s" % (
          PIN["SkyyClasses"], _bad21[:4], _vov21))
_fin21, _col21 = [], {}
for m_, d_ in _ps21.items():
    sp_ = [json.loads(JZ19.read("Server/Particles/SkyyArmory/Spawners/%s.particlespawner" % e_["SpawnerId"]).decode("utf-8")) for e_ in d_["Spawners"]]
    if not (isinstance(d_.get("LifeSpan"), (int, float)) and d_["LifeSpan"] > 0) or not all(isinstance(s_.get("ParticleLifeSpan"), dict) for s_ in sp_):
        _fin21.append(m_)
    _col21[m_] = sorted(set(re.findall(r'"Color": "([^"]+)"', json.dumps(sp_))))
check(not _fin21 and len(set(json.dumps(v_) for v_ in _col21.values())) == 8,
      "P21: the 8 Binding line systems are FINITE (a system LifeSpan, every particle a life) and each tier has its own colours: %s %s" % (_fin21, _col21.get("Iron")))
_rv21 = os.path.join(ROOT, "models-local", "art", "soulcage", "Common")
if os.path.isdir(_rv21):
    _rb21 = []
    for m_ in SOUL19_TIERS[1:]:
        for x_ in ([".blockymodel"] + (["_Texture.png"] if m_ in ("Copper", "Iron") else [])):
            p_ = "Items/Weapons/SoulCage/SkyyArmory_%s%s" % (m_, x_)
            if open(os.path.join(_rv21, *p_.split("/")), "rb").read() != JZ19.read("Common/" + p_):
                _rb21.append(p_)
    if open(os.path.join(_rv21, "Items", "Weapons", "SoulCage", "SkyyArmory_SoulCage_Spin.blockyanim"), "rb").read() != JZ19.read("Common/Items/Weapons/SoulCage/SkyyArmory_SoulCage_Spin.blockyanim"):
        _rb21.append("spin")
    check(not _rb21, "P21: the 7 cage models + the spin = Skyy's reviewed copy (models-local/art/soulcage) byte for byte; Copper / Iron textures too "
                     "(Thorium+ souls recoloured to the 2026-10-10 Element ladder on purpose): %s" % _rb21)
else:
    print("P21. NOTE no review copy (models-local/art/soulcage) here - the cage art is checked by the build")
print("P21. 0.1.19: %d new files (8 Soul items, 2 essences, root + 2 interactions, art, 8 finite Binding lines), 20 lang lines, recipes chained" % len(S21_ALL))
'''
hrep('''PY_OKS, PY_FAILS = OKS[0], len(FAILS)
''', P21 + '''PY_OKS, PY_FAILS = OKS[0], len(FAILS)
''')

# ---- T: the 0.1.19 start line
hrep('''          "T (0.1.14): each setup() prints the wand signature line with the defaults: %s" % sig_line[:1])
''', '''          "T (0.1.14): each setup() prints the wand signature line with the defaults: %s" % sig_line[:1])
    soul_line = [m_ for lv_, m_ in records()[n_log0:] if "0.1.19 soul Bindings on - hold right click: bind every enemy within 3 blocks of where you look" in m_]
    check(len(soul_line) == 2 and "up to 1 / 2 / 4 / 6 / 10 / 14 / 16 / 20 (Orb .. Onyxium)" in soul_line[0] and "solid after 2.5 / 2.3 / 2.1 / 1.9 / 1.7 / 1.6 / 1.5 / 1.5 s" in soul_line[0]
          and "50% stored as healing, Mana regen blocked while bound" in soul_line[0] and "Life 8% Z1, Fire 10% volcanic caves, Earth 8% Z2" in soul_line[0]
          and "essence drop system true" in soul_line[0],
          "T (0.1.19): each setup() prints the Soul Orb line with the defaults (+ SoulDropSys registered, the regen-block bridge state): %s" % soul_line[:1])
''')

# ---- R22 (JVM): after R21, before L2 (L2 changes the store)
R22 = r'''    # ============================================================================ R22. 0.1.19 THE SOUL ORB - every new path EXECUTED
    from jpype import JLong
    SO, SDR, SFN = JClass(PKG + "Soul"), JClass(PKG + "SoulDrop"), JClass(PKG + "SoulFn")
    HM22, BOOL22 = JClass("java.util.HashMap"), JClass("java.lang.Boolean")
    T22 = [2100000000000]

    def clk22(ms_=0):
        T22[0] += ms_
        SO.CLOCK = JLong(T22[0])
        return T22[0]
    NEAR22 = []

    @JImplements("java.util.function.Function")
    class Near22:
        @JOverride
        def apply(self, o):
            l_ = ArrayList()
            for r_ in NEAR22:
                l_.add(r_)
            return l_
    REGEN22 = []

    @JImplements("java.util.function.Function")
    class Regen22:
        @JOverride
        def apply(self, o):
            REGEN22.append((str(o[0]), int(o[1])))
            return BOOL22.TRUE

    @JImplements("java.util.function.Function")
    class Deny22:
        @JOverride
        def apply(self, o):
            return BOOL22.FALSE
    keep22 = (AT.NEAR, AT.GRID, LP.HAND, LP.LOOK)
    HAND22, LOOK22, HELD22 = HM22(), HM22(), HM22()
    EYE22 = (0.5, 65.6, 0.5)
    BOX22 = (0.8, 1.8, 0.8)
    IRON22 = "Weapon_Wand_SoulCage_Iron"
    WALL22 = lambda x, y, z: x == 5 and 64 <= y <= 67

    def look22(dx=1.0, dy=0.0, dz=0.0):
        l_ = math.sqrt(dx * dx + dy * dy + dz * dz)
        LOOK22.put(cu, JArray(JDouble)([EYE22[0], EYE22[1], EYE22[2], dx / l_, dy / l_, dz / l_]))

    def setup22(item=IRON22, mana=200.0, walls=()):
        reset_buf()
        TW.ALL.clear()
        SO.STATES.clear()
        SO.POOL.clear()
        SO.LATCH.clear()          # FIX ROUND: every case starts with no latch / no SEEN record
        SO.SEEN.clear()
        SO.HELD = HELD22
        ACfg.useDefaults()
        ACfg.TRAV_FX = True
        AT.PSEEN = ArrayList()
        AT.NEAR = Near22()
        AT.GRID = Grid(world_fn(list(walls)))
        LP.HAND, LP.LOOK = HAND22, LOOK22
        HAND22.put(cu, item)
        HELD22.put(cu, BOOL22.TRUE)
        look22()
        for k_ in ("class:fn:allowed", "class:fn:ally", "profile:epoch:" + str(cu), "armory:soul:" + str(cu), "mob:fn:level"):
            br.remove(k_)
        br.put("skill:fn:regenblock", Regen22())
        REGEN22[:] = []
        put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
        put(rc, DTHc.getComponentType(), None)
        mc.setStatValue(MANA, JFloat(mana))
        clk22(1000)

    def tick22(n_=1, ms_=100, store=None):
        for k_ in range(n_):
            clk22(ms_)
            SO.tickPlayer(rc, store if store is not None else tst, tbuf)

    def st22():
        return SO.STATES.get(cu)

    def nb22():
        s_ = st22()
        return 0 if s_ is None else int(s_.binds.size())

    def solid22():
        s_ = st22()
        return [] if s_ is None else [bool(s_.binds.get(k_).stable) for k_ in range(int(s_.binds.size()))]

    def hits22():
        return [(e_[0], round(e_[1], 4)) for e_ in events() if e_[2] == "EntitySource"]
    OFF22 = [(0.0, 0.0)] + [(dx_, dz_) for dx_ in (0.0, -1.0, 1.0) for dz_ in (-2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0)] + [(-1.0, 0.0), (1.0, 0.0)]

    def pack22(i0_, n_, cx=10.0, cz=0.5):          # n mobs packed within 2.3 blocks of one spot dead ahead (the "6 mobs in a 3-block space")
        return [mob(i0_ + k_, cx + dx_, 64.0, cz + dz_, BOX22) for k_, (dx_, dz_) in enumerate(OFF22[:n_])]

    # R22o THE ENGINE ASSET VALIDATORS on the 13 new JSON assets (the REAL files: 2 interactions, the root, 8 Soul items, 2 essences) + every
    # inline step (decode, the codec's full validate pass, logOrThrowValidatorExceptions, contained assets) - a vanilla id the bare JVM does not
    # load is a test-bed line when Assets.zip has it (R14's rule)
    KNOWN14.update(os.path.basename(n_).rsplit(".", 1)[0] for n_ in SOUL19_NEW)
    KNOWN14.update(n_[len("Common/"):] for n_ in SOUL19_NEW if n_.startswith("Common/"))
    val22, env22 = [], len(ENV14)
    for c_, pre_ in ((INTc, "Server/Item/Interactions/"), (ROOTc, "Server/Item/RootInteractions/"), (ITMc, "Server/Item/Items/")):
        for n_ in SOUL19_NEW:
            if n_.startswith(pre_) and n_.endswith(".json"):
                o_, w_ = validate14(c_, os.path.basename(n_)[:-5], JZ19.read(n_).decode("utf-8"))
                if o_ is None or w_:
                    val22.append("%s: %s" % (n_, w_))
    check(not val22 and len([n_ for n_ in SOUL19_NEW if n_.endswith(".json") and n_.startswith("Server/Item/")]) == 13,
          "R22o: the ENGINE ASSET VALIDATORS pass on the 13 new Soul assets (the Charging root + its Release, the 8 Soul items with their recipes, "
          "the 2 essences) and every inline step: %s (test-bed lines %d)" % (val22[:4], len(ENV14) - env22))

    # R22a THE ROWS + TABLES + DEFAULTS + CLAMPS + THE DEFAULT FILE + armory:soul
    ACfg.useDefaults()
    Rows22 = JClass(PKG + "CfgRows")
    k22 = [str(k_) for k_ in Rows22.KEYS]
    d22 = dict(zip(k22, [str(d_) for d_ in Rows22.DEFS]))
    c22 = dict(zip(k22, [str(c_) for c_ in Rows22.CATS]))
    t22 = dict(zip(k22, [str(t_) for t_ in Rows22.TYPES]))
    dc22 = str(ACfg.DEF_CFG)
    want22 = {"soul.enabled": "true", "soul.damagePerMana": "2", "soul.tick": "0.5", "soul.lockRadius": "3", "soul.lockRange": "25",
              "soul.snapRange": "30", "soul.aimCone": "12", "soul.wispyGrace": "0.4", "soul.storePercent": "50", "soul.decayPercent": "2",
              "soul.noRegen": "true", "soul.lineDots": "48", "essence.drops": "true"}
    TAB22 = {"soul.bindings": [1, 2, 4, 6, 10, 14, 16, 20], "soul.manaPerSecond": [1, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35],
             "soul.damageMult": [1, 1.1, 1.1, 1.5, 1.5, 2, 2, 2.5], "soul.stabilize": [2.5, 2.3, 2.1, 1.9, 1.7, 1.6, 1.5, 1.5],
             "soul.storeCap": [10, 15, 20, 30, 40, 50, 55, 60]}
    ETAB22 = {"essence.chance": [8, 10, 8, 8, 8, 5, 3], "essence.zone": [1, 0, 2, 3, 4, 4, 4]}
    ENAMES22 = ["Life", "Fire", "Earth", "Frost", "Storm", "Void", "Light"]
    fl22 = [k_ for k_, v_ in want22.items() if d22.get(k_) != v_ or c22.get(k_) != "soul"]
    fl22 += [k_ for k_ in list(TAB22) + list(ETAB22) if t22.get(k_) != "table" or c22.get(k_) != "soul"]
    fl22 += ["%s.%s" % (k_, m_) for k_, vs_ in TAB22.items() for m_, v_ in zip(SOUL19_TIERS, vs_) if ("\n%s.%s=%s\n" % (k_, m_, ("%g" % v_))) not in dc22]
    fl22 += ["%s.%s" % (k_, m_) for k_, vs_ in ETAB22.items() for m_, v_ in zip(ENAMES22, vs_) if ("\n%s.%s=%s\n" % (k_, m_, ("%g" % v_))) not in dc22]
    fl22 += [k_ for k_, v_ in want22.items() if ("\n%s=%s\n" % (k_, v_)) not in dc22]
    ld22 = ([float(x_) for x_ in ACfg.SOUL_NT], [float(x_) for x_ in ACfg.SOUL_MPS], [float(x_) for x_ in ACfg.SOUL_MULT], [float(x_) for x_ in ACfg.SOUL_STAB],
            [float(x_) for x_ in ACfg.SOUL_CAP], [float(x_) for x_ in ACfg.ESS_PCT], [float(x_) for x_ in ACfg.ESS_ZONE])
    pr22 = Props()
    for k_, v_ in (("soul.lockRadius", "99"), ("soul.tick", "0"), ("soul.bindings.Onyxium", "99"), ("soul.storePercent", "-5"), ("essence.chance.Light", "500"),
                   ("soul.bindings.Nope", "4"), ("essence.zone.Void", "6")):
        pr22.setProperty(k_, v_)
    ACfg.apply(pr22)
    cl22 = (float(ACfg.SOUL_RADIUS), float(ACfg.SOUL_TICK), float(ACfg.SOUL_NT[7]), int(ACfg.SOUL_STORE), float(ACfg.ESS_PCT[6]), float(ACfg.ESS_ZONE[5]))
    ACfg.useDefaults()
    hk22 = JClass(PKG + "ArmoryHooks")
    hc22 = (hk22.checkSoul("soul.bindings[Copper]", "2") is None, hk22.checkSoul("soul.bindings[Bronze]", "2") is not None,
            hk22.checkEssence("essence.chance[Light]", "3") is None, hk22.checkEssence("essence.chance[Wind]", "3") is not None)
    tx22 = str(ACfg.soulText())
    check(not fl22 and ld22 == ([1.0, 2.0, 4.0, 6.0, 10.0, 14.0, 16.0, 20.0], [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35], [1.0, 1.1, 1.1, 1.5, 1.5, 2.0, 2.0, 2.5],
                                  [2.5, 2.3, 2.1, 1.9, 1.7, 1.6, 1.5, 1.5], [10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 55.0, 60.0], [8.0, 10.0, 8.0, 8.0, 8.0, 5.0, 3.0],
                                  [1.0, 0.0, 2.0, 3.0, 4.0, 4.0, 4.0])
          and cl22 == (8.0, 0.1, 32.0, 0, 100.0, 6.0) and hc22 == (True, True, True, True) and c22.get("fixed.soul") == "soul"
          and c22.get("fixed.staff.Iron") == "wands" and "soul" in [str(x_) for x_ in Rows22.CAT_IDS] and "staffs" not in [str(x_) for x_ in Rows22.CAT_IDS]
          and tx22.startswith("soul Bindings on - hold right click: bind every enemy within 3 blocks"),
          "R22a: the 13 Soul rows + 7 tables (Server Setup > Armory > Soul Orb + essences; the fixed staff rows now under 'Wand + staff (fixed)') with "
          "Skyy's numbers in the rows and the default file; the loader clamps (radius 99 -> 8, pulse 0 -> 0.1, Onyxium 99 -> 32 Bindings, store -5 -> 0, "
          "chance 500 -> 100, zone 6 kept) and ignores unknown table entries; the table checks take only the 8 tiers / 7 essences; armory:soul words: "
          "%s | %s | %s" % (fl22[:6], cl22, tx22[:160]))

    # R22b THE PURE MATHS
    pm22 = ([int(SO.tierOf(i_)) for i_ in SOUL19_IDS + ["Weapon_Wand_Iron", None]], [int(SO.cap(t_)) for t_ in range(-1, 9)],
            [round(float(SO.dps(2.0, m_, x_)), 4) for m_, x_ in zip(TAB22["soul.manaPerSecond"], TAB22["soul.damageMult"])],
            round(float(SO.drain(4, 1.1, 0.5)), 4), float(SO.drain(0, 1.1, 0.5)), int(SO.stabMs(2.1)), int(SO.pulseMs()),
            round(float(SO.addStore(5.0, 3.0, 20.0)), 4), round(float(SO.addStore(19.0, 3.0, 20.0)), 4), round(float(SO.addStore(25.0, 3.0, 20.0)), 4),
            round(float(SO.addStore(5.0, -3.0, 20.0)), 4), round(float(SO.decay(20.0, 2.0, 10.0)), 4), round(float(SO.decay(20.0, 2.0, 60.0)), 4),
            round(float(SO.decay(20.0, 0.0, 10.0)), 4), round(float(SO.decay(SO.decay(20.0, 2.0, 4.0), 2.0, 6.0)), 4), float(SO.decay(20.0, 100.0, 1.0)), [int(SDR.zoneOfEnv(e_)) for e_ in ("Env_Zone2_Desert", "Env_Zone1_Caves_Volcanic_T1", "Zone4_Tier5", "Env_Hub", None)],
            [bool(SDR.volcanic(e_)) for e_ in ("Env_Zone1_Caves_Volcanic_T1", "Env_Zone4_Caves_Volcanic", "Env_Zone1_Caves")],
            [int(SDR.zoneOfLevel(l_)) for l_ in (0, 1, 20, 21, 30, 31, 45, 46, 60)])
    check(pm22 == ([0, 1, 2, 3, 4, 5, 6, 7, -1, -1], [0, 1, 2, 4, 6, 10, 14, 16, 20, 0], [2.0, 2.31, 2.42, 3.45, 3.6, 5.0, 5.2, 6.75], 2.2, 0.0, 2100, 500,
                  8.0, 20.0, 25.0, 5.0, round(20 * 0.98 ** 10, 4), round(20 * 0.98 ** 60, 4), 20.0, round(20 * 0.98 ** 10, 4), 0.0, [2, 1, 4, -1, -1], [True, True, False], [-1, 1, 1, 2, 2, 3, 3, 4, 4]),
          "R22b: the pure maths - tierOf (8 ids; a wand / nothing = -1), cap (1 / 2 / 4 / 6 / 10 / 14 / 16 / 20), damage a second per Binding = 2 x "
          "Mana/s x tier multiple (Orb 2.0 .. Onyxium 6.75), drain = n x Mana/s x s (4 Iron Bindings for 0.5 s = 2.2), Iron solid at 2100 ms, pulse "
          "500 ms, the store cap (a pool above a lowered cap is kept, never cut), the fade (2 %%/s compounding: 10 s 20 -> 16.34 in one read or in 4 + 6 s, 60 s -> 5.95, 0 %% = none, 100 %% = gone), the zone "
          "of an env / a volcanic cave / a SkyyMobs level (1-20 / 21-30 / 31-45 / 46+): %s" % (pm22,))

    # R22c THE BIND CAP PER TIER: 24 mobs packed at the look point - every one in the small radius at once, up to the cap
    caps22 = {}
    for t_, i_ in enumerate(SOUL19_IDS):
        setup22(item=i_)
        NEAR22[:] = pack22(4000 + 30 * t_, 24) + [rc]
        tick22(1, 0)
        caps22[i_] = (nb22(), len(set(e_[0] for e_ in hits22())), len([p_ for p_ in list(AT.PSEEN) if str(p_).startswith("SkyyArmory_Soul_")]))
    check([v_[0] for v_ in caps22.values()] == [1, 2, 4, 6, 10, 14, 16, 20] and [v_[1] for v_ in caps22.values()] == [1, 2, 4, 6, 10, 14, 16, 20],
          "R22c (Skyy: '6 mobs packed in a 3-block space = 6 Bindings in one go', up to the orb's cap): 24 mobs within 2.3 blocks of the look point - "
          "ONE tick binds exactly 1 / 2 / 4 / 6 / 10 / 14 / 16 / 20 (Orb .. Onyxium) and each Bound mob is hit at once: %s" % caps22)
    check(all(0 < v_[2] <= 48 for v_ in caps22.values()) and caps22[SOUL19_IDS[7]][2] == 40,
          "R22c: the line-draw budget - all of a player's Binding lines together at most 48 dots a draw (20 Onyxium lines = 2 dots each = 40): %s"
          % [v_[2] for v_ in caps22.values()])
    # the radius: a mob 3.5 blocks from the look point is never bound (Onyxium, room for 20)
    setup22(item=SOUL19_IDS[7])
    far22 = [mob(4300, 10.0, 64.0, 0.5, BOX22), mob(4301, 10.0, 64.0, 4.0, BOX22), mob(4302, 10.0, 64.0, 3.4, BOX22)]
    NEAR22[:] = far22 + [rc]
    tick22(1, 0)
    rad22 = sorted(e_[0] for e_ in hits22())
    check(rad22 == [4300, 4302], "R22c: soul.lockRadius 3 - a mob 2.9 blocks from the look point is bound, one 3.5 blocks away is not: %s" % rad22)

    # R22d LINE OF SIGHT to START, never to keep (Skyy 2026-10-07)
    setup22(walls=[WALL22])
    m22 = mob(4310, 10.0, 64.0, 0.5, BOX22)
    NEAR22[:] = [m22, rc]
    l0_ = int(SO.LOS_REFUSED)
    tick22(5, 100)
    los_a = (nb22(), hits22())
    AT.GRID = Grid(world_fn())
    tick22(1, 100)
    los_b = nb22()
    tick22(25, 100)          # Iron: solid after 2.1 s
    los_c = solid22()
    AT.GRID = Grid(world_fn([WALL22]))
    look22(0.0, 0.0, 1.0)
    n0_ = len(hits22())
    tick22(10, 100)          # 1 s through the wall, looking away
    los_d = (nb22(), len([h_ for h_ in hits22()[n0_:] if h_[0] == 4310]))
    check(los_a == (0, []) and los_b == 1 and los_c == [True] and los_d == (1, 2),
          "R22d (Skyy: 'cannot lock on through block, but once locked, still drains hp even if the line goes through a block'): a wall between "
          "you and the mob = NO Binding, nothing hit (the look stops at the wall); the wall gone = bound; solid after 2.1 s; the wall back AND "
          "looking away = still bound and hit twice a second: %s %s %s %s" % (los_a, los_b, los_c, los_d))

    # R22e STABILIZE TIMING: wispy until the tier's time while looked at; looking away before it snaps after the grace; solid = kept
    stab22 = {}
    for i_, need_ in ((SOUL19_IDS[0], 25), (SOUL19_IDS[7], 15)):
        setup22(item=i_)
        NEAR22[:] = [mob(4320, 10.0, 64.0, 0.5, BOX22), rc]
        tick22(1, 0)                   # bound (wispy)
        tick22(need_ - 2, 100)
        a_ = solid22()
        tick22(2, 100)
        b_ = solid22()
        stab22[i_] = (a_, b_)
    setup22(item=SOUL19_IDS[0])
    NEAR22[:] = [mob(4330, 10.0, 64.0, 0.5, BOX22), rc]
    tick22(1, 0)
    tick22(10, 100)                    # 1.0 s of 2.5
    s0_ = int(SO.SNAPS)
    look22(0.0, 0.0, 1.0)              # away (the sky: no look point)
    tick22(3, 100)                     # 0.3 s < the 0.4 s grace
    snap_a = (nb22(), int(SO.SNAPS) - s0_)
    tick22(3, 100)                     # 0.6 s > the grace
    snap_b = (nb22(), int(SO.SNAPS) - s0_)
    look22()
    tick22(1, 100)                     # bound again
    tick22(26, 100)                    # solid
    look22(0.0, 0.0, 1.0)
    tick22(30, 100)                    # 3 s away
    snap_c = (nb22(), solid22(), int(SO.SNAPS) - s0_)
    # binding the NEXT group once solid, up to the cap (Copper 2: one more)
    setup22(item=SOUL19_IDS[1])
    ga_, gb1_, gb2_ = mob(4340, 10.0, 64.0, 0.5, BOX22), mob(4341, 0.5, 64.0, 10.0, BOX22), mob(4342, 1.5, 64.0, 10.0, BOX22)
    NEAR22[:] = [ga_, gb1_, gb2_, rc]
    tick22(1, 0)
    grp_a = nb22()
    tick22(24, 100)                    # Copper: solid after 2.3 s
    look22(0.0, 0.0, 1.0)              # the next group (+z)
    tick22(2, 100)
    s_ = st22()
    grp_b = sorted(int(s_.binds.get(k_).t.getIndex()) for k_ in range(int(s_.binds.size()))) if s_ is not None else None
    check(stab22[SOUL19_IDS[0]] == ([False], [True]) and stab22[SOUL19_IDS[7]] == ([False], [True]) and snap_a == (1, 0) and snap_b == (0, 1)
          and snap_c == (1, [True], 1) and grp_a == 1 and grp_b == [4340, 4341],
          "R22e (Skyy: 'keep looking 1.5-2.5 s until it stabilizes (wispy -> solid); only then can you look away'): the Soul Orb is still wispy at 2.3 s "
          "and solid at 2.5 s, Onyxium wispy at 1.3 s and solid at 1.5 s; looking away 0.3 s keeps a wispy Binding (grace 0.4), 0.6 s snaps it; a "
          "SOLID one survives 3 s of looking away; once solid you bind the NEXT group (Copper cap 2: one more of the two there, the first kept): "
          "%s %s %s %s %s %s" % (stab22, snap_a, snap_b, snap_c, grp_a, grp_b))

    # R22e THE LOOK: one line per Binding in the tier colour - wispy = sparse dots (1.5 blocks apart), solid = dense (0.6), 4 times a second
    setup22()
    NEAR22[:] = [mob(4350, 10.0, 64.0, 0.5, BOX22), rc]
    tick22(1, 0)
    fx_w = len([p_ for p_ in list(AT.PSEEN) if str(p_) == "SkyyArmory_Soul_Iron"])
    tick22(22, 100)                    # Iron solid at 2.1 s
    AT.PSEEN.clear()
    tick22(10, 100)                    # 1 s solid
    fx_s = len([p_ for p_ in list(AT.PSEEN) if str(p_) == "SkyyArmory_Soul_Iron"])
    oth_ = [str(p_) for p_ in list(AT.PSEEN) if str(p_) != "SkyyArmory_Soul_Iron"]
    # from the hand (eye + 0.6 along the look, 0.45 down) to the mob's middle: 8.9 blocks -> 6 wispy dots, 15 solid ones; 4 lines a second
    check(fx_w == 6 and fx_s == 3 * 15 and not oth_,
          "R22e: the Binding line - the first (wispy) line = 6 sparse dots of SkyyArmory_Soul_Iron, a solid Binding = 15 dense dots, a line every 250 ms "
          "at the latest (100 ms ticks here: every 3rd tick = 3 lines = 45 dots in 1 s; the game's 33 ms ticks: about 4 a second), no other particle: %s %s %s" % (fx_w, fx_s, oth_[:3]))

    # R22f DRAIN + DAMAGE PER PULSE: 4 Iron Bindings - 4 x 1.1 Mana/s, 2 x 1.1 x 1.1 damage/s each, every 0.5 s, the first at once; 50 % stored
    setup22(mana=200.0)
    pk22 = pack22(4400, 4)
    NEAR22[:] = pk22 + [rc]
    tick22(1, 0)
    f_a = (round(sv(mc, MANA), 3), sorted(hits22()))
    tick22(4, 100)                     # +0.4 s: no pulse yet
    f_b = (round(sv(mc, MANA), 3), len(hits22()))
    tick22(1, 100)                     # +0.5 s: the second pulse
    f_c = (round(sv(mc, MANA), 3), len(hits22()), round(float(SO.poolNow(cu, T22[0])), 4), str(br.get("armory:soul:" + str(cu))))
    hpmax22 = float(mc.get(HP).getMax())
    tick22(200, 100)                   # 20 s more: the pool reaches the Iron cap (20 % of max Health) and stays there
    f_d = (round(float(SO.poolNow(cu, T22[0])), 4), round(sv(mc, MANA), 3), len(hits22()))
    check(f_a == (197.8, [(4400 + k_, 1.21) for k_ in range(4)]) and f_b == (197.8, 4) and f_c == (195.6, 8, 4.84, "4.84")
          and abs(f_d[0] - round(hpmax22 * 0.2, 4)) < 1e-6 and f_d[1] == round(195.6 - 40 * 2.2, 3) and f_d[2] == 8 + 4 * 40,
          "R22f (Skyy: 'steady damage for a steady Mana drain per Binding'; 'damage is stored as bonus healing'): 4 Iron Bindings - the first pulse AT "
          "ONCE: 2.2 Mana (4 x 1.1 x 0.5) and 4 hits of 1.21 (2 x 1.1 x 1.1 x 0.5, Damage$EntitySource(you) through the damage pipeline); nothing "
          "more for 0.4 s; at 0.5 s the next (195.6 Mana, 8 hits); 50 %% stored (4.84 HP, armory:soul:<uuid>); after 20 s the pool sits at the Iron "
          "cap (20 %% of max Health %s) while the drain + hits go on: %s %s %s %s" % (hpmax22, f_a, f_b, f_c, f_d))
    # the regen block: renewed every pulse while bound, cleared at the release; the fade after the release
    rg_a = list(REGEN22)
    HELD22.put(cu, BOOL22.FALSE)
    n0_ = len(hits22())
    tick22(1, 100)
    rel_a = (st22() is None, str(SO.LAST_RELEASE), list(REGEN22[len(rg_a):]))
    tick22(100, 100)                   # 10 s after the release
    rel_b = (len(hits22()) - n0_, round(float(SO.poolNow(cu, T22[0])), 4))
    check(len(rg_a) == 42 and all(u_ == str(cu) and u2_ > 0 for u_, u2_ in rg_a) and rg_a[-1][1] - rg_a[-2][1] == 500
          and rel_a == (True, "let go", [(str(cu), 0)]) and rel_b[0] == 0 and abs(rel_b[1] - round(hpmax22 * 0.2 * 0.98 ** 10, 4)) < 1e-3,
          "R22g (Skyy: 'no natural Mana regen while any Binding is active'): skill:fn:regenblock gets { you, until } on EVERY pulse (42 calls in 20.5 s, each "
          "until = the pulse + 2 s) and { you, 0 } at the release; letting go of right click ends every Binding at once - NO damage in the next 10 s, "
          "and the stored healing fades 2 %%/s (10 s: x0.98^10): %s ... %s | %s %s" % (rg_a[:2], rg_a[-1:], rel_a, rel_b))
    # no Binding, button held: no regen block at all
    setup22()
    NEAR22[:] = [rc]
    tick22(10, 100)
    check(nb22() == 0 and REGEN22 == [] and st22() is not None and round(sv(mc, MANA), 3) == 200.0,
          "R22g: holding right click with NO enemy in reach binds nothing, drains nothing and never blocks the regen: %s" % (REGEN22,))

    # R22g CROSS-MOD: the REAL SkyySkills 0.4.30 RegenBlockFn (its own class loader) as skill:fn:regenblock - blocked while bound, free after
    SK30 = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.30.jar")
    if os.path.isfile(SK30):
        URL22, URLCL22, File22 = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
        urls22 = JArray(URL22)(1)
        urls22[0] = File22(SK30).toURI().toURL()
        ld22 = URLCL22(urls22, sysl)
        RBF22 = JClass("com.skyy.skills.RegenBlockFn", loader=ld22)
        MR22 = JClass("com.skyy.skills.ManaRegen", loader=ld22)
        setup22()
        br.put("skill:fn:regenblock", RBF22())
        NEAR22[:] = pack22(4560, 2) + [rc]
        wall22 = lambda: int(JClass("java.lang.System").currentTimeMillis())
        x0_ = int(MR22.blockLeft(cu, JLong(wall22())))
        tick22(1, 0)
        x1_ = int(MR22.blockLeft(cu, JLong(wall22())))
        HELD22.put(cu, BOOL22.FALSE)
        tick22(1, 100)
        x2_ = int(MR22.blockLeft(cu, JLong(wall22())))
        check(x0_ == 0 and 9000 <= x1_ <= 10000 and x2_ == 0 and st22() is None,
              "R22g CROSS-MOD (the real SkyySkills 0.4.30 jar's RegenBlockFn + ManaRegen in their own loader): no block before, BLOCKED the moment "
              "the first Binding pulses (the until is SkyySkills-capped at 10 s ahead), cleared at the release: %s %s %s" % (x0_, x1_, x2_))
        br.remove("skill:fn:regenblock")
        print("R22g. cross-mod: the real SkyySkills 0.4.30 regen block %d ms before, %d ms while bound, %d ms after the release" % (x0_, x1_, x2_))
    else:
        print("R22g. NOTE SkyySkills-0.4.30.jar is not built here - the cross-mod regen block check is skipped (build it: tools/skills_0_4_30_patch.py)")

    # R22h THE RELEASES - each one ends every Binding, nothing is dealt after it
    rel22 = {}

    def rel_case(name_, act_, mana_=200.0, ticks_=3, epoch_=None, store2_=None):
        setup22(mana=mana_)
        if epoch_ is not None:
            br.put("profile:epoch:" + str(cu), JLong(epoch_))
        NEAR22[:] = pack22(4500, 4) + [rc]
        tick22(1, 0)
        h0_ = len(hits22())
        p0_ = round(float(SO.poolNow(cu, T22[0])), 4)
        act_()
        NEAR22[:] = [rc]          # from here on only the OLD Bindings could hit anything
        tick22(1, 100, store2_)
        why_ = str(SO.LAST_RELEASE)
        tick22(ticks_ * 5, 100)
        rel22[name_] = (nb22() == 0, why_, len(hits22()) - h0_, p0_, round(float(SO.poolNow(cu, T22[0])), 4), str(br.get("armory:soul:" + str(cu))))
    tst2 = U.allocateInstance(TSt.class_)
    rel_case("death", lambda: put(rc, DTHc.getComponentType(), U.allocateInstance(DTHc.class_)))
    rel_case("world change", lambda: None, store2_=tst2)
    rel_case("profile switch", lambda: br.put("profile:epoch:" + str(cu), JLong(8)), epoch_=7)
    rel_case("weapon swap", lambda: HAND22.put(cu, "Weapon_Wand_Iron"))
    rel_case("soul.enabled off", lambda: setattr(ACfg, "SOUL_ON", False))
    ACfg.SOUL_ON = True
    # Mana runs out: 3 Mana pays the first pulse (2.2) but not the second -> all end, the second pulse deals nothing
    setup22(mana=3.0)
    NEAR22[:] = pack22(4520, 4) + [rc]
    tick22(1, 0)
    om_a = (nb22(), len(hits22()), round(sv(mc, MANA), 3))
    tick22(5, 100)
    om_b = (st22() is None, str(SO.LAST_RELEASE), len(hits22()), round(sv(mc, MANA), 3))
    tick22(10, 100)
    om_c = len(hits22())
    setup22(mana=1.0)
    NEAR22[:] = pack22(4530, 4) + [rc]
    tick22(1, 0)
    om_d = (st22() is None, str(SO.LAST_RELEASE), len(hits22()), round(sv(mc, MANA), 3))
    check(rel22["death"][:3] == (True, "death", 0) and rel22["death"][4] == 0.0 and rel22["death"][5] == "None"
          and rel22["world change"][:3] == (True, "world change", 0) and rel22["world change"][4] > 0.0
          and rel22["profile switch"][:3] == (True, "profile switch", 0) and rel22["profile switch"][4] == 0.0
          and rel22["weapon swap"][:3] == (True, "the soul weapon left your hand", 0) and rel22["soul.enabled off"][:3] == (True, "Soul Bindings off", 0)
          and om_a == (4, 4, 0.8) and om_b == (True, "out of Mana", 4, 0.8) and om_c == 4 and om_d == (True, "out of Mana", 0, 1.0),
          "R22h (Skyy: 'held while right-click is held or until Mana runs out'; the spec's death / profile resets): DEATH, WORLD CHANGE, PROFILE "
          "SWITCH, the WEAPON SWAP and soul.enabled OFF each end every OLD Binding at once and nothing is dealt after (15 more ticks; a hold still "
          "going on in the new world / profile starts from nothing); death and the "
          "profile switch also clear the stored healing (armory:soul:<uuid> removed), a world change keeps it; MANA: 3 Mana pays the first pulse "
          "(0.8 left) - the second finds too little = all end, nothing dealt, the 0.8 kept; 1 Mana = the very first pulse refused, nothing dealt: "
          "%s | %s %s %s %s" % (rel22, om_a, om_b, om_c, om_d))
    # one Binding ends on its own: its mob dies / walks past soul.snapRange - the others go on
    setup22(item=SOUL19_IDS[3])
    own22 = pack22(4540, 3)
    NEAR22[:] = own22 + [rc]
    tick22(1, 0)
    tick22(20, 100)                    # Thorium: all 3 solid after 1.9 s (a wispy one would snap: nothing stays in the look)
    put(own22[0], DTHc.getComponentType(), U.allocateInstance(DTHc.class_))
    put(own22[1], TCc.getComponentType(), TCc(V3(40.0, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    e0_ = int(SO.ENDS)
    n0_ = len(hits22())
    tick22(10, 100)
    own_h = sorted(set(h_[0] for h_ in hits22()[n0_:]))
    check(nb22() == 1 and int(SO.ENDS) - e0_ == 2 and own_h == [4542],
          "R22h: a Binding whose mob DIED or is 39.5 blocks away (past soul.snapRange 30) ends alone - the third goes on and only it is hit: %s" % own_h)

    # R22i THE CLASS LOCK: SkyyClasses' class:fn:allowed says no -> nothing bound, nothing drained, nothing hit
    setup22()
    br.put("class:fn:allowed", Deny22())
    NEAR22[:] = pack22(4550, 4) + [rc]
    lk0_ = int(SO.LOCKED)
    tick22(10, 100)
    lock22 = (st22() is None, int(SO.LOCKED) - lk0_, len(hits22()), round(sv(mc, MANA), 3), str(SO.LAST_WHY))
    br.remove("class:fn:allowed")
    check(lock22 == (True, 10, 0, 200.0, "class lock"),
          "R22i (Priest only, like the wands): a class SkyyClasses' class:fn:allowed refuses for the Soul Cage binds NOTHING, drains NOTHING, hits "
          "NOTHING (asked every tick of the hold): %s" % (lock22,))

    # R22j THE REAL HOLD: our root on a real InteractionManager chain (the vanilla ChargingCondition's walk)
    IMODc = JClass("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    IMGRc = JClass("com.hypixel.hytale.server.core.entity.InteractionManager")
    ICHNc = JClass("com.hypixel.hytale.server.core.entity.InteractionChain")
    ITYPc = JClass("com.hypixel.hytale.protocol.InteractionType")
    rres22 = compile_root("SkyyArmory_Soul_Bind")
    root22 = RMAP.getAsset("SkyyArmory_Soul_Bind")
    kroot22 = RMAP.getAsset("SkyyArmory_Kunai_Return_Iron")
    if kroot22 is not None:
        compile_root("SkyyArmory_Kunai_Return_Iron")
    imod_old22 = jfield(IMODc, "instance").get(None)
    imod22 = U.allocateInstance(IMODc.class_)
    imct22 = reg_.registerComponent(IMGRc.class_, Sup(lambda: None))
    setf(imod22, IMODc, gfield("com.hypixel.hytale.server.core.modules.interaction.InteractionModule", "getInteractionManagerComponent"), imct22)
    jfield(IMODc, "instance").set(None, imod22)
    held22 = {}
    try:
        im22 = U.allocateInstance(IMGRc.class_)
        chains22 = JClass("it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap")()
        setf(im22, IMGRc, "chains", chains22)
        setf(im22, IMGRc, "unmodifiableChains", chains22)          # getChains() answers this view (bytecode)
        ch22 = U.allocateInstance(ICHNc.class_)
        CH22 = "com.hypixel.hytale.server.core.entity.InteractionChain"

        def chain22(ty_, root_, op_):
            setf(ch22, ICHNc, gfield(CH22, "getType"), ty_)
            setf(ch22, ICHNc, gfield(CH22, "getRootInteraction"), root_)
            setf(ch22, ICHNc, gfield(CH22, "getOperationCounter"), JInt(op_))
            return bool(SO.heldChain(tst, rc))
        held22["no manager"] = bool(SO.heldChain(tst, rc))
        put(rc, imct22, im22)
        held22["no chain"] = bool(SO.heldChain(tst, rc))
        chains22.put(JInt(1), ch22)
        held22["our root, at the Charging"] = chain22(ITYPc.Secondary, root22, 0)
        held22["our root, released (op 1)"] = chain22(ITYPc.Secondary, root22, 1)
        held22["our root as Primary"] = chain22(ITYPc.Primary, root22, 0)
        held22["another root (kunai return)"] = chain22(ITYPc.Secondary, kroot22, 0) if kroot22 is not None else False
        # through tickPlayer (HELD seam off = the game path): the held chain binds, the release on the chain ends it
        setup22()
        SO.HELD = None
        NEAR22[:] = pack22(4560, 2) + [rc]
        chain22(ITYPc.Secondary, root22, 0)
        tick22(1, 0)
        held22["tick: held"] = (nb22(), len(hits22()))
        chain22(ITYPc.Secondary, root22, 1)
        tick22(1, 100)
        held22["tick: released"] = (st22() is None, str(SO.LAST_RELEASE))
        chains22.clear()
    finally:
        put(rc, imct22, None)
        jfield(IMODc, "instance").set(None, imod_old22)
        SO.HELD = HELD22
    ops22 = [c_ for c_, i_ in rres22["ops"]]
    check(not rres22["bad"] and ops22[:1] == ["ChargingInteraction"] and "SimpleInteraction" in ops22
          and held22 == {"no manager": False, "no chain": False, "our root, at the Charging": True, "our root, released (op 1)": False,
                         "our root as Primary": False, "another root (kunai return)": False, "tick: held": (2, 2), "tick: released": (True, "let go")},
          "R22j THE REAL HOLD: RootInteraction.build() of SkyyArmory_Soul_Bind = Charging -> the Release Simple; Soul.heldChain on a REAL "
          "InteractionManager / InteractionChain (the vanilla ChargingCondition's walk: chains -> root.getOperation(counter).getInnerOperation()): held "
          "ONLY while our root's Secondary chain sits at its Charging - released (op 1), a Primary chain, another root, no chain / no manager = not "
          "held; through tickPlayer the held chain binds 2 mobs and the chain moving past the Charging releases them: %s %s" % (ops22, held22))

    # R22k armory:fn:soul (get / take / text) - the stored healing for Sacred Heal / Wings of Fate
    setup22()
    NEAR22[:] = pack22(4570, 4) + [rc]
    tick22(1, 0)
    tick22(10, 100)                    # 3 pulses: 3 x 4 x 1.21 x 50 % = 7.26
    fn22 = SFN()
    g22 = round(float(fn22.apply(cu)), 4)
    g22b = round(float(fn22.apply(JArray(JObject)(["get", cu]))), 4)
    tk22 = round(float(fn22.apply(JArray(JObject)(["take", cu, JDouble(20.0)]))), 4)          # Iron cap 20 % of 20 HP = 4
    left22 = round(float(fn22.apply(JArray(JObject)(["get", cu]))), 4)
    tk22b = round(float(fn22.apply(JArray(JObject)(["take", cu, JDouble(1000.0)]))), 4)
    txt22 = str(fn22.apply(JArray(JObject)(["text"])))
    bad22 = (fn22.apply("x"), fn22.apply(JArray(JObject)(["take"])), fn22.apply(JArray(JObject)(["nope", cu])))
    check(g22 == 7.26 and g22b == 7.26 and tk22 == 4.0 and left22 == 3.26 and tk22b == 3.26 and txt22 == str(ACfg.SOUL_TEXT) and bad22 == (None, None, None),
          "R22k: armory:fn:soul - get = 7.26 stored HP (3 pulses x 4 x 1.21 x 50 %%), take for a 20-HP ally = 4 (the Iron cap 20 %% of the HEALED "
          "one's max Health), 3.26 left, a big ally takes the rest; text = armory:soul; anything else = null: %s %s %s %s %s %s" % (g22, g22b, tk22, left22, tk22b, bad22))
    HELD22.put(cu, BOOL22.FALSE)
    tick22(1, 100)

    # R22l THE ESSENCE DROPS (SoulDrop.roll on the stand-ins: the env seam, the roll seam, the spawn seam)
    DROPS22 = []

    @JImplements("java.util.function.BiFunction")
    class Spawn22:
        @JOverride
        def apply(self, l_, at_):
            DROPS22.append(sorted(str(x_.getItemId()) for x_ in l_))
            return None

    @JImplements("java.util.function.Function")
    class Lvl22:
        @JOverride
        def apply(self, o):
            return JInt(25)
    ENV22 = HM22()
    SDR.SPAWN, SDR.ENV = Spawn22(), ENV22
    UC22 = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    PLA22 = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    GM22 = JClass("com.hypixel.hytale.protocol.GameMode")
    DIDX = [0]

    def dead22(i_, env_, killer=None, roll=0.0):
        r_ = mob(i_, 10.0, 64.0, 0.5, BOX22)
        put(r_, UC22.getComponentType(), UC22(UUID.fromString("00000000-0000-0000-0022-%012d" % i_)))
        d_ = U.allocateInstance(DTHc.class_)
        setf(d_, DTHc, gfield("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent", "getDeathInfo"),
             DMGc(DENTc(killer if killer is not None else rc), C_["Physical"], JFloat(10.0)))
        put(r_, DTHc.getComponentType(), d_)
        if env_ is not None:
            ENV22.put(r_, env_)
        SDR.ROLL = roll
        DROPS22[:] = []
        n_ = int(SDR.roll(r_, tst, tbuf))
        return n_, list(DROPS22), str(SDR.LAST_WHY), r_
    ACfg.useDefaults()
    es22 = {}
    for nm_, i_, env_ in (("Zone 1", 4600, "Env_Zone1_Plains"), ("Zone 2", 4601, "Env_Zone2_Desert"), ("Zone 3", 4602, "Env_Zone3_Tundra"),
                          ("Zone 4", 4603, "Env_Zone4_Wastes"), ("volcanic Zone 2 cave", 4604, "Env_Zone2_Caves_Volcanic_T1")):
        es22[nm_] = dead22(i_, env_)[:2]
    br.put("mob:fn:level", Lvl22())
    es22["no env, SkyyMobs Lv 25"] = dead22(4605, None)[:2]
    br.remove("mob:fn:level")
    es22["no env, no level"] = dead22(4606, None)[:3]
    es22["roll 99"] = dead22(4607, "Env_Zone4_Wastes", roll=99.0)[:2]
    es22["roll 7 (Life 8 %)"] = dead22(4608, "Env_Zone1_Plains", roll=7.99)[:2]
    once_ = dead22(4609, "Env_Zone1_Plains")
    SDR.ROLL = 0.0
    DROPS22[:] = []
    es22["the same death again"] = (int(SDR.roll(once_[3], tst, tbuf)), list(DROPS22))
    es22["killed by a mob"] = dead22(4610, "Env_Zone1_Plains", killer=mob(4611, 9.0, 64.0, 0.5, BOX22))[:3]
    plc22 = U.allocateInstance(PLA22.class_)
    setf(plc22, PLA22, gfield("com.hypixel.hytale.server.core.entity.entities.Player", "getGameMode"), GM22.Creative)
    put(rc, PLA22.getComponentType(), plc22)
    es22["Creative killer"] = dead22(4612, "Env_Zone1_Plains")[:3]
    put(rc, PLA22.getComponentType(), None)
    ACfg.ESS_ON = False
    es22["essence.drops off"] = dead22(4613, "Env_Zone1_Plains")[:2]
    ACfg.ESS_ON = True
    ACfg.ESS_ZONE = JArray(JDouble)([1.0, 0.0, 2.0, 3.0, 4.0, 6.0, 6.0])          # an admin moves Void + Light to a later zone
    es22["Void + Light moved to Zone 6"] = (dead22(4614, "Env_Zone4_Wastes")[:2], dead22(4615, "Env_Zone6_Future")[:2])
    ACfg.useDefaults()
    SDR.SPAWN, SDR.ENV, SDR.ROLL = None, None, -1.0
    check(es22["Zone 1"] == (1, [["Ingredient_Life_Essence"]]) and es22["Zone 2"] == (1, [["SkyyArmory_Essence_Earth"]])
          and es22["Zone 3"] == (1, [["Ingredient_Ice_Essence"]])
          and es22["Zone 4"] == (3, [["Ingredient_Lightning_Essence", "Ingredient_Void_Essence", "SkyyArmory_Essence_Light"]])
          and es22["volcanic Zone 2 cave"] == (2, [["Ingredient_Fire_Essence", "SkyyArmory_Essence_Earth"]])
          and es22["no env, SkyyMobs Lv 25"] == (1, [["SkyyArmory_Essence_Earth"]]) and es22["no env, no level"][:2] == (0, [])
          and es22["no env, no level"][2].startswith("no zone") and es22["roll 99"] == (0, []) and es22["roll 7 (Life 8 %)"] == (1, [["Ingredient_Life_Essence"]])
          and es22["the same death again"] == (0, []) and es22["killed by a mob"] == (0, [], "not a player's kill")
          and es22["Creative killer"] == (0, [], "creative") and es22["essence.drops off"] == (0, [])
          and es22["Void + Light moved to Zone 6"] == ((1, [["Ingredient_Lightning_Essence"]]), (2, [["Ingredient_Void_Essence", "SkyyArmory_Essence_Light"]])),
          "R22l (Skyy: 'each drops from mobs of the matching zone'): a player's kill rolls its zone's essence - Zone 1 Life, Zone 2 Earth (new), Zone 3 "
          "Frost (the vanilla Ice Essence), Zone 4 Storm (Lightning) + Void + Light (no later zone yet: the nearest one), a volcanic cave adds Fire; "
          "no env = the SkyyMobs level band (Lv 25 = Zone 2), neither = nothing; the chance (99 > 8 %% nothing, 7.99 < 8 Life); ONCE per death; a "
          "mob's kill, a Creative killer, essence.drops off = nothing; essence.zone moves Void + Light to a later zone: %s" % json.dumps(es22, default=str))

    # R22p FIX ROUND (the critics) - each fix EXECUTED
    # (1) THE LATCH: holding right click through an out-of-Mana release never restarts the Bindings (no bind / fail loop every tick), even when
    # Mana comes back; letting go clears it and the next hold binds again
    setup22(mana=3.0)
    NEAR22[:] = pack22(4700, 4) + [rc]
    tick22(1, 0)
    la_a = (nb22(), len(hits22()))
    tick22(5, 100)                     # the second pulse finds 0.8 Mana < 4.4 -> released, latched
    h0_, b0_, q0_, l0_ = int(SO.HOLDS), int(SO.BINDS), len(hits22()), int(SO.LATCHED) - 1
    tick22(40, 100)                    # 4 s more holding
    mc.setStatValue(MANA, JFloat(200.0))
    tick22(10, 100)                    # Mana back, still holding: still nothing
    la_b = (st22() is None, str(SO.LAST_RELEASE), int(SO.HOLDS) - h0_, int(SO.BINDS) - b0_, len(hits22()) - q0_, round(sv(mc, MANA), 3), bool(SO.LATCH.containsKey(cu)), int(SO.LATCHED) - l0_)
    HELD22.put(cu, BOOL22.FALSE)
    tick22(1, 100)
    la_c = bool(SO.LATCH.containsKey(cu))
    HELD22.put(cu, BOOL22.TRUE)
    tick22(1, 100)
    la_d = (nb22(), int(SO.HOLDS) - h0_, len(hits22()) - q0_)
    check(la_a == (4, 4) and la_b == (True, "out of Mana", 0, 0, 0, 200.0, True, 1) and la_c is False and la_d == (4, 1, 4),
          "R22p FIX 1 (critic: no latch after out of Mana): 4 Bindings, out of Mana at the 2nd pulse -> 50 more ticks HOLDING (Mana refilled to 200 "
          "half way) = no new hold, no Binding, no hit, no Mana spent (latched); letting go clears the latch; the next hold binds 4 at once: "
          "%s %s %s %s" % (la_a, la_b, la_c, la_d))
    # (2) AN UNREADABLE MANA STAT = the Bindings end (never free hits)
    setup22()
    NEAR22[:] = pack22(4710, 4) + [rc]
    put(rc, ESMc.getComponentType(), None)
    nm0_, q0_ = int(SO.NO_MANA_STAT), len(hits22())
    tick22(12, 100)
    nm_ = (st22() is None, str(SO.LAST_RELEASE), int(SO.NO_MANA_STAT) - nm0_, len(hits22()) - q0_, float(SO.STORED) >= 0.0, bool(SO.LATCH.containsKey(cu)))
    put(rc, ESMc.getComponentType(), mc)
    check(nm_[:4] == (True, "Mana could not be read", 1, 0) and nm_[5] is True,
          "R22p FIX 2 (critic: statOf -1 skipped both Mana guards = free hits): with no Mana stat the very first pulse releases every Binding, "
          "nothing is dealt (1.2 s held), the hold is latched: %s" % (nm_,))
    # (3) THE SWEEP: a player gone (no tick) for soul GONE_MS (30 s) loses the Bindings (regen block cleared), the stored healing + its bridge
    # key and the latch; a player who IS ticked after a long gap is never swept; a stored pool of nobody online is dropped
    setup22()
    NEAR22[:] = pack22(4720, 4) + [rc]
    tick22(6, 100)
    sw_a = (nb22(), float(SO.poolNow(cu, T22[0])) > 0.0, br.get("armory:soul:" + str(cu)) is not None, bool(SO.SEEN.containsKey(cu)))
    clk22(40000)
    tick22(1, 0)                       # ticked after a 40 s gap: SEEN is renewed BEFORE the sweep
    sw_b = (st22() is not None, str(SO.LAST_RELEASE) != "left the game")
    REGEN22[:] = []
    u2_ = JClass("java.util.UUID").randomUUID()
    SO.store(u2_, JDouble(5.0), JDouble(50.0), 2, JLong(0), JLong(T22[0]))
    sp0_ = int(SO.SWEPT)
    clk22(31000)                       # nobody ticks for 31 s (cu left the game)
    swn_ = int(SO.sweep(JLong(T22[0])))
    sw_c = (st22() is None, str(SO.LAST_RELEASE), SO.POOL.isEmpty(), br.get("armory:soul:" + str(cu)) is None, br.get("armory:soul:" + str(u2_)) is None,
            (str(cu), 0) in REGEN22, bool(SO.SEEN.containsKey(cu)), int(SO.SWEPT) - sp0_ >= 2)
    check(sw_a == (4, True, True, True) and sw_b == (True, True) and sw_c == (True, "left the game", True, True, True, True, False, True),
          "R22p FIX 3 (critics: nothing cleans up when a player disconnects): a binder not ticked for 31 s is swept - Bindings released, the regen "
          "block cleared (skill:fn:regenblock 0), stored healing + armory:soul:<uuid> gone, a pool of nobody online gone; ticked after a 40 s gap "
          "= kept: %s %s %s (swept %s)" % (sw_a, sw_b, sw_c, swn_))
    # (4) THE DOT BUDGET (soul.lineDots) + the dots emit for ONE re-draw (250 ms LifeSpan, no two overlapping systems)
    setup22()
    ACfg.SOUL_DOTS = 0
    NEAR22[:] = [mob(4730, 10.0, 64.0, 0.5, BOX22), rc]
    tick22(10, 100)
    dt_0 = len([p_ for p_ in list(AT.PSEEN) if str(p_).startswith("SkyyArmory_Soul_")])
    ACfg.SOUL_DOTS = 10
    tick22(30, 100)                    # Iron solid at 2.1 s: a solid 8.9-block line would be 15 dots; the budget cuts it to 10
    AT.PSEEN.clear()
    tick22(3, 100)
    dt_1 = len([p_ for p_ in list(AT.PSEEN) if str(p_) == "SkyyArmory_Soul_Iron"])
    ACfg.useDefaults()
    ls_ = sorted(set(round(float(json.loads(zipfile.ZipFile(JAR).read(n_).decode("utf-8-sig")).get("LifeSpan", -1)), 3) for n_ in zipfile.ZipFile(JAR).namelist()
                     if n_.startswith("Server/Particles/") and "/SkyyArmory_Soul_" in n_ and n_.endswith(".particlesystem")))
    check(dt_0 == 0 and dt_1 == 10 and ls_ == [0.25] and int(SO.FX_MS) == 250,
          "R22p FIX 4 (critic: particle cost): soul.lineDots 0 = no line at all, 10 = a solid line cut to 10 dots; every SkyyArmory_Soul_* system "
          "emits 0.25 s = Soul.FX_MS (one re-draw, no overlap): %s %s %s" % (dt_0, dt_1, ls_))
    # (5) THE HELP ROWS say the tooltips show the defaults (the tooltip words are baked at build time)
    hl22 = dict(zip([str(k_) for k_ in Rows22.KEYS], [str(h_) for h_ in Rows22.HELPS]))
    check(all("Tooltips show defaults." in hl22.get(k_, "") for k_ in ("soul.damagePerMana", "soul.bindings", "soul.manaPerSecond", "soul.damageMult", "soul.stabilize")),
          "R22p FIX 5 (critic: tooltips bake the numbers): the 5 rows the tooltip numbers come from say so: %s" % [hl22.get(k_, "")[-40:] for k_ in ("soul.damagePerMana", "soul.bindings")])

    # R22q FIX ROUND 2 (the second critics) - each fix EXECUTED
    # (1) THE LOOK POINT ray-casts only mobs inside the aim cone (20 mobs beside you = 0 ray-casts), nearest the crosshair first; a cone mob
    # behind a wall is skipped for the next clear one in the cone (the same pick as before)
    setup22(item=SOUL19_IDS[0])
    side22 = [mob(4800 + k_, 0.5 + (k_ % 5), 64.0, 6.0 + (k_ // 5) * 3.0, BOX22) for k_ in range(20)]
    NEAR22[:] = [mob(4790, 10.0, 64.0, 0.5, BOX22)] + side22 + [rc]
    r0_ = int(SO.LOOK_RAYS)
    tick22(1, 0)
    lr_a = (nb22(), [e_[0] for e_ in hits22()], int(SO.LOOK_RAYS) - r0_)
    setup22(item=SOUL19_IDS[0], walls=[lambda x, y, z: x == 5 and 64 <= y <= 67 and z <= 1])
    ACfg.SOUL_CONE = 60                # a 30-degree half cone: 4792 (23 degrees off, its line passes the wall's end) is inside it
    NEAR22[:] = [mob(4791, 10.0, 64.0, 0.5, BOX22), mob(4792, 10.0, 64.0, 4.5, BOX22)] + side22 + [rc]
    r0_ = int(SO.LOOK_RAYS)
    tick22(1, 0)
    lr_b = (nb22(), [e_[0] for e_ in hits22()], int(SO.LOOK_RAYS) - r0_)
    ACfg.useDefaults()
    check(lr_a == (1, [4790], 1) and lr_b == (1, [4792], 2),
          "R22q FIX 1 (critic: a ray-cast for every mob in the 27-block sphere): 1 mob ahead + 20 beside you = ONE look ray-cast and the mob ahead "
          "bound; the cone mob behind a wall is skipped (2 ray-casts) and the next clear one in the cone is the look point: %s %s" % (lr_a, lr_b))
    # (2) NO LOOK SCAN with the cap full and every Binding solid (the Orb: 1 of 1, solid after 2.5 s): no ray-casts, still hit; a free cap
    # slot (Copper 1 of 2) keeps scanning
    setup22(item=SOUL19_IDS[0])
    NEAR22[:] = [mob(4793, 10.0, 64.0, 0.5, BOX22)] + side22[:3] + [rc]
    tick22(1, 0)
    tick22(26, 100)                    # solid
    r0_, k0_, q0_ = int(SO.LOOK_RAYS), int(SO.SCAN_SKIPS), len(hits22())
    tick22(20, 100)
    sk_a = (solid22(), int(SO.LOOK_RAYS) - r0_, int(SO.SCAN_SKIPS) - k0_, len(hits22()) - q0_)
    setup22(item=SOUL19_IDS[1])
    NEAR22[:] = [mob(4794, 10.0, 64.0, 0.5, BOX22), rc]
    tick22(1, 0)
    tick22(24, 100)                    # Copper solid, 1 of 2
    r0_, k0_ = int(SO.LOOK_RAYS), int(SO.SCAN_SKIPS)
    tick22(10, 100)
    sk_b = (solid22(), int(SO.LOOK_RAYS) - r0_ >= 10, int(SO.SCAN_SKIPS) - k0_)
    check(sk_a == ([True], 0, 20, 4) and sk_b == ([True], True, 0),
          "R22q FIX 2 (critic: the look scan ran with nothing to use it): Orb 1 of 1 solid = 20 ticks, 0 ray-casts, 20 skipped scans, still hit "
          "4 times (2 s); Copper 1 of 2 solid = still scanning every tick: %s %s" % (sk_a, sk_b))
    # (3) THE LATCH is cleared by a let-go made with ANOTHER item in hand: re-equip the cage + hold = binds at once
    setup22(mana=3.0)
    NEAR22[:] = pack22(4830, 4) + [rc]
    tick22(6, 100)                     # out of Mana at the 2nd pulse -> latched
    lt_a = (st22() is None, bool(SO.LATCH.containsKey(cu)))
    mc.setStatValue(MANA, JFloat(200.0))
    HAND22.put(cu, "Weapon_Wand_Iron")
    HELD22.put(cu, BOOL22.FALSE)
    tick22(1, 100)                     # let go with the metal wand in hand
    lt_b = bool(SO.LATCH.containsKey(cu))
    HAND22.put(cu, IRON22)
    HELD22.put(cu, BOOL22.TRUE)
    tick22(1, 100)
    lt_c = nb22()
    check(lt_a == (True, True) and lt_b is False and lt_c == 4,
          "R22q FIX 3 (critic: a stale latch after a let-go with another item): latched out of Mana, let go holding a metal wand = latch cleared, "
          "the cage again + hold = 4 Bindings at once: %s %s %s" % (lt_a, lt_b, lt_c))
    # (4) THE PROFILE EPOCH is read only for a player with soul state: a new hold still takes the CURRENT epoch, and a stored pool still
    # resets on a profile switch made while nothing is held
    setup22()
    br.put("profile:epoch:" + str(cu), JLong(21))
    NEAR22[:] = pack22(4840, 2) + [rc]
    HAND22.put(cu, "Weapon_Wand_Iron")
    tick22(5, 100)                     # no soul weapon: no state, no pool
    ep_a = (st22() is None, SO.POOL.isEmpty())
    HAND22.put(cu, IRON22)
    tick22(3, 100)
    g1_ = int(st22().gen) if st22() is not None else None
    HELD22.put(cu, BOOL22.FALSE)
    tick22(1, 100)                     # let go: a stored pool remains
    pa_ = float(SO.poolNow(cu, T22[0])) > 0.0
    br.put("profile:epoch:" + str(cu), JLong(22))
    tick22(1, 100)
    ep_b = (g1_ is not None, pa_, SO.POOL.isEmpty(), str(br.get("armory:soul:" + str(cu))))
    HELD22.put(cu, BOOL22.TRUE)
    tick22(1, 100)
    g2_ = int(st22().gen) if st22() is not None else None
    br.remove("profile:epoch:" + str(cu))
    check(ep_a == (True, True) and ep_b[:3] == (True, True, True) and g2_ is not None and g2_ != g1_,
          "R22q FIX 4 (critic: ArmoryTree.gen for every player every tick): no soul weapon = no state; a hold takes the current epoch; a profile "
          "switch while a pool is stored (nothing held) still resets it; the next hold has the new generation: %s %s %s %s" % (ep_a, g1_, ep_b, g2_))
    SO.LATCH.clear()
    SO.SEEN.clear()

    # R22m vs the 0.1.18 jar METHOD BY METHOD
    MN22, MO22 = methods_of(JAR), methods_of(OLD118)
    cmp22 = {}
    for c_ in sorted(set(MN22) | set(MO22)):
        if c_ not in MN22 or c_ not in MO22:
            cmp22[c_] = "only in " + ("0.1.19" if c_ in MN22 else "0.1.18")
            continue
        ch_ = sorted(k_ for k_ in set(MN22[c_][0]) | set(MO22[c_][0]) if MN22[c_][0].get(k_) != MO22[c_][0].get(k_))
        fd_ = sorted(set(MN22[c_][1]) ^ set(MO22[c_][1]))
        if ch_ or fd_:
            cmp22[c_] = {"methods": [k_.split("(")[0] for k_ in ch_], "fields": [f_.split(":")[0] for f_ in fd_]}
    new22 = {"Soul", "SoulBind", "SoulDrop", "SoulDropSys", "SoulFn", "SoulState"}
    # ArmoryCfg load / reloadAll / useDefaults differ only by the DEF_CFG text constant they read (the new default lines)
    plan22 = {"ArmoryCfg": ({"apply", "soulText", "load", "reloadAll", "useDefaults", "<clinit>"}, {"SOUL_ON", "SOUL_DPM", "SOUL_TICK", "SOUL_RADIUS", "SOUL_RANGE", "SOUL_SNAP", "SOUL_CONE",
                                                                "SOUL_GRACE", "SOUL_STORE", "SOUL_DECAY", "SOUL_NOREGEN", "SOUL_DOTS", "ESS_ON", "SOUL_NT", "SOUL_NT_DEF",
                                                                "SOUL_MPS", "SOUL_MPS_DEF", "SOUL_MULT", "SOUL_MULT_DEF", "SOUL_STAB", "SOUL_STAB_DEF",
                                                                "SOUL_CAP", "SOUL_CAP_DEF", "ESS_PCT", "ESS_PCT_DEF", "ESS_ZONE", "ESS_ZONE_DEF", "SOUL_TEXT"}),
              "ArmoryDefs": ({"<clinit>"}, {"SOUL_IDS", "SOUL_TIERS", "SOUL_NAMES", "SOUL_PS", "SOUL_ROOT", "ESS_NAMES", "ESS_IDS"}),
              "ArmoryHooks": ({"checkSoul", "checkEssence", "<clinit>"}, set()),
              "TravTick": ({"tick"}, set()),
              "SkyyArmoryPlugin": ({"systems", "publish", "unpublish", "setup", "shutdown", "<clinit>"}, {"SYS_DROP"}),
              "CfgRows": ({"<clinit>"}, set()), "ArmoryCheck": ({"<clinit>"}, set())}
    bad22m = {}
    for c_, v_ in cmp22.items():
        if c_ in new22 and v_ == "only in 0.1.19":
            continue
        if c_ in plan22 and isinstance(v_, dict) and set(v_["methods"]) <= plan22[c_][0] and set(v_["fields"]) <= plan22[c_][1]:
            continue
        bad22m[c_] = v_
    check(not bad22m and set(c_ for c_, v_ in cmp22.items() if v_ == "only in 0.1.19") == new22 and "tick" in cmp22.get("TravTick", {}).get("methods", [])
          and "systems" in cmp22.get("SkyyArmoryPlugin", {}).get("methods", []),
          "R22m: 0.1.18 -> 0.1.19 METHOD BY METHOD - only the planned methods / fields differ (the 6 new Soul classes, the rows + tables + soulText, "
          "the Defs tables, the 2 table checks, TravTick's tick (+ Soul.tickPlayer), the plugin's systems / bridge / start lines): %s" % json.dumps(bad22m)[:1500])
    print("R22m. vs 0.1.18 method by method: %s" % json.dumps(cmp22)[:1800])
    # the balance numbers (the Class Balance chart): per tier at the defaults
    bal22 = []
    for t_, i_ in enumerate(SOUL19_TIERS):
        n_ = TAB22["soul.bindings"][t_]
        mps_ = TAB22["soul.manaPerSecond"][t_]
        dps_ = 2.0 * mps_ * TAB22["soul.damageMult"][t_]
        bal22.append("%s: %d Bindings, %s Mana/s each (full %s/s), %s dmg/s each (full %s/s), %s dmg per Mana, solid %s s, store cap %d%%" % (
            i_, n_, mps_, round(n_ * mps_, 2), round(dps_, 3), round(n_ * dps_, 2), round(dps_ / mps_, 3), TAB22["soul.stabilize"][t_], TAB22["soul.storeCap"][t_]))
    print("R22. balance (defaults, before SkyyGear levels): " + " | ".join(bal22))
    SO.HELD = None
    SO.CLOCK = JLong(0)
    SO.STATES.clear()
    SO.POOL.clear()
    AT.NEAR, AT.GRID, LP.HAND, LP.LOOK = keep22
    AT.PSEEN = None
    br.remove("skill:fn:regenblock")
    br.remove("profile:epoch:" + str(cu))
    ACfg.useDefaults()
    TW.ALL.clear()
    reset_buf()
    put(rc, DTHc.getComponentType(), None)
    at20(rc, 0.5, 64.0, 0.5)
    mc.setStatValue(MANA, JFloat(200.0))
    print("R22. 0.1.19 soul orb: rows + tables, maths, the cap per tier, line of sight to start only, wispy -> solid + snaps + the next group, "
          "drain / damage / store per pulse, the regen block, every release (no damage after), the class lock, the REAL hold chain, armory:fn:soul, "
          "the essence drops, the 0.1.18 compare")
'''
hrep('''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''',
     R22 + '''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''')

out_t = ts.replace(LF, TNL)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(out_t)
print("wrote %s" % os.path.relpath(TDST, ROOT))
