"""Derive SkyyClasses/build_skyyclasses_0.1.25.py from the generated 0.1.24 (the SET pin; the EDITED lineage: Skyy's edited 0.1.6 ->
classes_0_1_7_patch.py -> ... -> classes_0_1_24_patch.py -> 0.1.24; classes_0_1_6_patch.py is never re-run). 0.1.24 stays untouched; its
line endings are kept.
Run:  python tools/classes_0_1_25_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.25.py   (never --deploy)
Test: python SkyyClasses/test_skyyclasses_0.1.25.py [--dir <scratch>] [--keep]

0.1.25 (2026-10-14) = THE SETTINGS SPLIT + THE SPELLBLADE + THE REBIRTH MODIFIER SLOTS (Skyy 2026-10-14 ~18:30 "do 1. 3. 6. 7. 8. and 9.":
'1. Split the SkyyClasses settings ... then Spellblade', '7. Rebirth wrap-up: the extra modifier slot every 5th rebirth ...'; "Basically we
are making our own runes and modifiers, then controlling them in the skill tree, instead of the vanilla controller, to lock then per class.
(If 2 of your abilities have echo modifier, the modifiers are unlocked and level separately per ability"; docs/answered/classes.md
2026-10-08 popup batch 1 Spellblade "Yes to all (Recommended)").
  (1) SETTINGS SPLIT: the config kit's row arrays leave CfgRows' static initialiser (63.5 of 64 KB in 0.1.24) for two holder classes
    CfgRows1 + CfgRows2 (tools/skyycfg.py emit(..., HOLDERS=2), opt-in; every other mod keeps HOLDERS=1 = byte for byte as before). CfgRows
    keeps every public field (KEYS, DEFS, ... DL0) - the SAME arrays, joined in its initialiser: keys, defaults, files, History, the Server
    Setup bridge and every saved config.properties line are unchanged (the harness compares every array of 0.1.24 and 0.1.25 and starts
    twice on a copy of the live data).
  (2) THE SPELLBLADE (research/classes/Spellblade.md, every page default "Yes to all"): the 8th class - skill Battlemagic, colour #6fd0d8
    (SkyyProfiles 0.1.9's card), role Melee mage; weapons = vanilla longswords (Weapon_Longsword_), The Armory's longsword recolours
    (Longsword_) + Zweihander + the 4 Elemental swords (Weapon_Elemental_ - a class lock only: they stay SHELVED, no drops), kit
    Weapon_Longsword_Crude. THE WARRIOR GIVES UP LONGSWORDS (Skyy: "Warrior gives up longswords + Zweihander"): swords, spears, shields.
    The class card is APPENDED after the CLASSES literal on purpose: SkyySkills' build reads that literal (its roster check) and a parallel
    SkyySkills round must not stop on it - SkyySkills has no Battlemagic slot yet (the build prints the gap; the companion list below).
    MOMENTUM (the class resource, ab.Momentum.numbers): +1 per enemy a Spellblade weapon hit lands on (at most +2 per swing; a swing = the
    hits within 0.15 s), +1 rhythm bonus when the swing STARTED within 0.4 s of the last hit landing (the Primary InteractionChainStartEvent -
    the Blood Frenzy hook), each stack decays 4 s after it was gained, max 20; Breach +3, Sunder +2, Rift Cleave +3, Shattering Arc keeps
    5. Lost: a hit for 15 % of your max Health (-3), stunned / rooted / frozen (all - checked every 0.25 s), a non-Spellblade item in hand
    (all). Rolling (7+): allies within 8 blocks +5 % move speed (an aura, refreshed every 0.25 s); Unstoppable (14+): +10 %, knockback on
    you is stripped (the Shield Wall door), statuses last 50 % longer. Element strength +1 % a stack. Attack speed / arc size per stack =
    SHOWN ONLY (no attack-speed door yet, like Blood Frenzy's). The HUD widget gets "Momentum 14 (Unstoppable)" (class:fn:abil out[47]) -
    SkyyHud draws it in a later round.
    THE FIVE ABILITIES (costs = power x 58 / 42, research/Class-Power-Split.md; the page's shape tables):
      A1 Arcane Breach (8 + 1; 16 s): a 180 degree arc, 5 blocks, 1.2 H, BREACHED 8 s: +15 % damage taken from everyone (+1 a Momentum
        stack, max 10; +0.5 a level; cap 30); +3 Momentum. Breaching Charge (sprint: a 2-block step, 7 s), Breach from Above (air: a 4-block
        circle on landing, 1.0 H, knock-up), Marked Ground (crouch: 360 degrees, 3.5 blocks, no damage, Breach 20 %). Mods Radius+ Duration+
        Power+ Chain (Breach jumps to the nearest enemy NOT hit). Breach + the Archer's Mark on one target = the higher + 5 (Skyy Q5).
      A2 Elemental Imbue (7 + 1; 18 s): 12 s of +30 % element damage on every Spellblade weapon hit + that element's status (abilities that
        hit while it runs carry the status too). Element = the Elemental sword's own (Flame Fire, Ice Water, Gravity Earth, Poison Poison),
        else your attunement (default Fire; picked in the ability panel, out of combat). Charging Imbue (sprint: + a crescent 8 blocks
        ahead, 0.8 H), Falling Imbue (air: + a 4-block burst on landing), Deep Imbue (crouch: 15 s, statuses +25 %, you stand 0.5 s). Mods
        Duration+ Power+ Efficiency Chain (the status jumps to one more enemy within 6). The element part is OUR multiplier until SkyyGear
        reads classes:fn:imbue (published; SkyyGear 'gear:imbue' = true switches ours off - no double count).
        STATUSES (ab.Elements.numbers, research/cloud/Element-System-Spec.md 5): Fire Burn (10 % of the hit a second, 4 s, 3 stacks), Water
        Chill (-15 % speed 3 s; 3 within 3 s = Freeze 1.5 s through Frost Nova's freeze + boss clock), Earth Stagger (every 3rd Earth hit: a
        0.4 s stun + -10 % defence 4 s), Lightning Shock (40 % jumps to 1 enemy within 3; shocked take +5 % 3 s), Wind Gust (+1 block
        knockback, an ability hit knocks up; bosses immune), Poison (8 % a second, 6 s). Bosses: stuns / slows halved.
      A2-alt Sunder (9 + 2; 30 s): the enemy you look at within 4: 2.0 H, SUNDERED 12 s - it deals 15 % less to players (Weakened);
        Exposed (+20 % crit damage on it) is SHOWN ONLY (no crit door yet). +2 Momentum. Lunging Sunder (sprint: a 3-block step, 1.8 H),
        Sunder from Above (air: the enemy nearest your landing within 3, 2.4 H, +0.5 s stagger), Armour Break (crouch: 1 s wind-up, 15 s,
        -10 % defence too). Mods Duration+ Power+ Chain (a second enemy within 6 at 75 %) Echo (a weaker strike 1 s later).
      A1-alt A Rift Cleave (10 + 2; 20 s): a 160 degree arc (5 blocks, 1.2 H) + a 2 x 8 rift ahead for 3 s: inside Breached 15 % + slowed
        20 % (+ the Imbue status each second); +3 Momentum. Running Rift (sprint: 2 x 10 behind you), Rift Drop (air: a 5-block circle on
        landing), Rift Ring (crouch: 4 blocks around you, 4 s, 18 %). Mods Duration+ Radius+ Slow Power+ Echo (a weaker rift 1 s after).
      A1-alt B Shattering Arc (9 + 2; 20 s): SPENDS your Momentum: a 200 degree arc, 6 blocks, 1.2 H + 0.1 H a stack, Breach 15 % + 1 a stack
        (cap 30) for 8 s + 0.25 s a stack; you keep 5. Shattering Rush (sprint: a 3-block step), Shattering Fall (air: a 5-block circle,
        knock-up), Measured Strike (crouch: spends half, 160 degrees). Mods Power+ Radius+ Knockback+ Leech Echo (spends nothing).
    RUNES: 5 hidden rune items SkyyAbility_Spellblade_* (STAND-IN icons: our Mage / Warrior / Berserker ability art recoloured teal until
    the art round). THE CLASS TREE (SkyyTrees 0.3.10 lists the Spellblade nodes): T4 Second Wind, T5 Keen Edge (+5 % on weapon hits), T6
    Tempo; Tempest PA1 Twin Attunement, PA2 Burning Rift, PA5 Tempest; Breaker PB1 Deep Breach, PB2 Armour Split, PB4 Marked for Death;
    Vanguard PC3 Momentum Push (12 blocks), PC5 Vanguard (Unstoppable -15 % damage taken, max Momentum 18). WAITING (other mods): T1-T3,
    PA3 (element reactions), PA4, PB3, PB5, PC1, PC2, PC4 (the great shield + traversals = SkyyArmory, reactions = later).
  (3) REBIRTH MODIFIER SLOTS (research/cloud/Rebirth-Spec.md 3.x + R6 "Modifier slots +1 every 5th rebirth (2 -> 3 at rebirth 5 -> 4 at
    rebirth 10)"): every ability gets one more modifier slot per rb.modSlotEvery (5) rebirths of the profile, at most rb.modSlotMax (2)
    more - on top of the slots the class tree opened. Saved in a NEW key e2.<Ability>=<slot 3>,<slot 4> (e.<Ability> keeps slots 1 + 2,
    so an older jar ignores slots 3 + 4). The doubling rule holds over all four slots (a stackable modifier in at most two slots, from
    its Lv 2; never Floor + Duration+ or Seeker + Ricochet). The panel bridge gets o[78 ..] (slots 3 + 4 per card) and modRows head
    fields 11-14 (SkyyTrees 0.3.10 shows them).
  Saved data: abilities/<pkey>.properties gains u./e./m. lines of the five abilities, e2.<Ability> (rebirth slots) and att1 / att2 (the
  Imbue attunement) - an older jar ignores them. No migration. config.properties: 9 NEW rows (the 5 numbers rows, ab.Momentum.numbers,
  ab.Elements.numbers, kit.Spellblade, rb.modSlotEvery, rb.modSlotMax) read their defaults while missing - the file is not rewritten.
  COMPANION ROUNDS (other mods - NOT edited here): SkyySkills: a Battlemagic class row (slot, CLASS_ROWS, _ROSTER, SKILL_ALIASES - its build
    then reads the Spellblade from this script once the card moves into the CLASSES literal), Spellblade Mana per class level 4 + Stamina
    0.09 (Class-Power-Split.md), class:fn:abilhit kill XP already generic. SkyyMenu: CLASS_PLAYABLE + the Spellblade. SkyyProfiles: the
    card's enabled flag (class:list already makes it pickable). SkyyGear: ("Spellblade", "Battlemagic") in its class-skill pairs, the
    Light armour type for the class, classes:fn:imbue (the element split, Element-System-Spec 4) then publish gear:imbue = true. SkyyHud:
    draw class:fn:abil out[47] (Momentum). SkyyArmory: the Spellblade swords + great shield (+ Crescent Rush / Bulwark Charge, the arc move
    set) - the tree's T1-T3 / PC1 / PC2 / PC4 wait for it.
  ROLLBACK to 0.1.24: abil.runeHud off + one login of every Spellblade first (their runes leave the ability slots); Spellblade profiles
    become classless-weapon profiles (no items lost, longswords go back to the Warrior); rebirth slots 3 + 4 go quiet (e2.* kept).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.24.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.25.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.24"' in s and "GENERATED by tools/classes_0_1_24_patch.py from the generated 0.1.23" in s, \
    "build_skyyclasses_0.1.24.py is not the generated 0.1.24"
assert "ArcaneBreach" not in s and "HOLDERS=" not in s
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:200])
    s = s.replace(old, new)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.25 (2026-10-14)"):].rstrip()

# ================================================================================================ docstring, version
rep('''"""SkyyClasses 0.1.24 - build script (javassist via jpype). GENERATED by tools/classes_0_1_24_patch.py from the generated 0.1.23 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_23_patch.py -> 0.1.23) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.25 - build script (javassist via jpype). GENERATED by tools/classes_0_1_25_patch.py from the generated 0.1.24 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_24_patch.py -> 0.1.24) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''' + NOTE.replace(LF, LF + "  ").replace("  " + LF, LF) + '''
  Notes in tools/classes_0_1_25_patch.py. CHECKED with SkyyClasses/test_skyyclasses_0.1.25.py.
=== 0.1.24 (history; still true unless 0.1.25 above says otherwise) ===
''')
rep('VERSION = "0.1.24"', 'VERSION = "0.1.25"')

# ================================================================================================ (1) THE SETTINGS SPLIT (the kit's row holders)
rep('''               RELOAD="ClassCfg.load", KEEP=CFG_KEEP, DEFAULTS={"config.properties": "".join(l + "\\n" for l in CFG_LINES)})''',
    '''               RELOAD="ClassCfg.load", KEEP=CFG_KEEP, DEFAULTS={"config.properties": "".join(l + "\\n" for l in CFG_LINES)},
               HOLDERS=2)   # 0.1.25: the row arrays live in CfgRows1 + CfgRows2 (CfgRows.<clinit> was 63.5 of 64 KB) - same fields, same contents
assert kit.info.get("holders") == 2 and len(kit.info["classes"]) == 9, "0.1.25: tools/skyycfg.py must support HOLDERS (the settings split)"''')

# ================================================================================================ (2) THE SPELLBLADE CLASS (+ the Warrior gives up longswords)
rep('''    {"name": "Warrior", "skill": "Swordsmanship", "color": "#e0b060", "enabled": True, "role": "Melee fighter",
     "desc": "Front line blade fighter. Swords and longswords up close and spears for reach.",
     "icons": ["Weapon_Sword_Iron", "Weapon_Longsword_Iron", "Weapon_Spear_Iron"],
     # 0.1.24 (LOCKED Skyy 2026-10-08 "shields warrior only"): shields are a Warrior weapon (they left FREE_WEAPONS)
     "weapons": [("Weapon_Sword_", "swords"), ("Weapon_Longsword_", "longswords"), ("Weapon_Spear_", "spears"), ("Weapon_Shield_", "shields")],
     # 0.1.10 (LOCKED Skyy 2026-10-01): + a Wood Shield - it goes into the off-hand when that is empty (Kit.offhand)
     "weapon_text": "Swords / Longswords / Spears / Shields", "kit": "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1"},''',
    '''    {"name": "Warrior", "skill": "Swordsmanship", "color": "#e0b060", "enabled": True, "role": "Melee fighter",
     "desc": "Front line blade fighter. A sword and shield up close and spears for reach.",   # 0.1.25: longswords went to the Spellblade
     "icons": ["Weapon_Sword_Iron", "Weapon_Shield_Iron", "Weapon_Spear_Iron"],
     # 0.1.24 (LOCKED Skyy 2026-10-08 "shields warrior only"): shields are a Warrior weapon (they left FREE_WEAPONS)
     # 0.1.25 (LOCKED Skyy 2026-10-08 popup batch 1 "Warrior gives up longswords + Zweihander"): longswords are the Spellblade's
     "weapons": [("Weapon_Sword_", "swords"), ("Weapon_Spear_", "spears"), ("Weapon_Shield_", "shields")],
     # 0.1.10 (LOCKED Skyy 2026-10-01): + a Wood Shield - it goes into the off-hand when that is empty (Kit.offhand)
     "weapon_text": "Swords / Spears / Shields", "kit": "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1"},''')
rep('''     "weapon_text": "Bo Staves / Wraps / Gauntlets", "kit": "Weapon_Staff_Bo_Wood:1"},
]''', '''     "weapon_text": "Bo Staves / Wraps / Gauntlets", "kit": "Weapon_Staff_Bo_Wood:1"},
]
# 0.1.25 (LOCKED Skyy 2026-10-08 "call it Spellblade" + popup batch 1 "Yes to all"; research/classes/Spellblade.md): THE 8TH CLASS. Appended
# after the literal ON PURPOSE: SkyySkills' build reads the CLASSES literal as its roster check and has no Battlemagic slot yet - the
# SkyySkills Battlemagic round moves this card into the literal (the build prints the gap below). Card text = SkyyProfiles 0.1.9's card.
# Weapons: vanilla longswords, The Armory's longsword recolours (Longsword_*), its Zweihander and the 4 Elemental swords (still SHELVED:
# a class lock, no drops) - pack mod ids are read at runtime only (PACK.md: never copied, never overridden).
CLASSES += [
    {"name": "Spellblade", "skill": "Battlemagic", "color": "#6fd0d8", "enabled": True, "role": "Melee mage",
     "desc": "Melee mage. Wide sweeping arcs with longswords - keep attacking to build Momentum and pour elements into every hit.",
     "icons": ["Weapon_Longsword_Iron", "Weapon_Longsword_Spectral", "Weapon_Longsword_Flame"],
     "weapons": [("Weapon_Longsword_", "longswords"), ("Longsword_", "longswords"), ("Zweihander", "two-handed swords"),
                 ("Weapon_Elemental_", "elemental swords")],
     "weapon_text": "Longswords / Zweihander", "kit": "Weapon_Longsword_Crude:1"},
]
PACK_PREFIXES = ["Longsword_", "Zweihander", "Weapon_Elemental_"]   # 0.1.25: The Armory (pack mod) ids - no vanilla item may match them''')
rep('''UI_DATA_COLORS = ["#8fd67a", "#e0b060", "#7fb0e0", "#d9443f", "#f2e6a0", "#b58cff", "#f08a30"] + ["#8fe39a", "#ffc800", "#ff9d6b"]''',
    '''UI_DATA_COLORS = ["#8fd67a", "#e0b060", "#7fb0e0", "#d9443f", "#f2e6a0", "#b58cff", "#f08a30", "#6fd0d8"] + ["#8fe39a", "#ffc800", "#ff9d6b"]   # 0.1.25: + Spellblade''')
rep('''for _p, _o, _n in RULES:
    if _p in ARMORY_PREFIXES:   # 0.1.14: SkyyArmory-only prefixes must NOT catch a vanilla item (they would move it)
        assert not any(_i.startswith(_p) for _i in _real), "SkyyArmory prefix %s matches a vanilla item" % _p
        continue''', '''for _p, _o, _n in RULES:
    if _p in ARMORY_PREFIXES or _p in PACK_PREFIXES:   # 0.1.14: SkyyArmory-only prefixes must NOT catch a vanilla item (0.1.25: + The Armory's)
        assert not any(_i.startswith(_p) for _i in _real), "SkyyArmory / pack prefix %s matches a vanilla item" % _p
        continue''')
rep('''assert [c["name"] for c in CLASSES] == ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk"] and all(c["enabled"] for c in CLASSES)''',
    '''assert [c["name"] for c in CLASSES] == ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"] and all(c["enabled"] for c in CLASSES)
# 0.1.25: THE SPELLBLADE OWNS EVERY LONGSWORD (vanilla + The Armory's recolours / Zweihander / Elemental swords); the Warrior keeps swords,
# spears and shields; no other class's weapon moved
SPELLBLADE_I = [i for i, c in enumerate(CLASSES) if c["name"] == "Spellblade"][0]
WARRIOR_I25 = [i for i, c in enumerate(CLASSES) if c["name"] == "Warrior"][0]
_ls25 = [i for i in _real if i.startswith("Weapon_Longsword_")]
assert len(_ls25) >= 18 and all(classify(i) == (SPELLBLADE_I, "longswords") for i in _ls25), [(i, classify(i)) for i in _ls25]
assert all(classify(i)[0] == WARRIOR_I25 for i in _real if i.startswith(("Weapon_Sword_", "Weapon_Spear_", "Weapon_Shield_"))), "Warrior weapons"
assert classify("Zweihander") == (SPELLBLADE_I, "two-handed swords") and classify("Longsword_Iron_Red")[0] == SPELLBLADE_I \\
    and classify("Weapon_Elemental_Flame") == (SPELLBLADE_I, "elemental swords"), "The Armory ids -> Spellblade"
_ARMORY_PACK = [os.path.join(B.USERDATA, "Mods", _f) for _f in (os.listdir(os.path.join(B.USERDATA, "Mods")) if os.path.isdir(os.path.join(B.USERDATA, "Mods")) else [])
                if _f.startswith("TheArmoryMod") and _f.endswith(".jar")]
if _ARMORY_PACK:   # read only: the ids it ships under our pack prefixes all belong to the Spellblade (nothing else of it moves)
    _pids = sorted(os.path.basename(n)[:-5] for n in zipfile.ZipFile(_ARMORY_PACK[0]).namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    _pk = [i for i in _pids if i.startswith(tuple(PACK_PREFIXES))]
    assert _pk and all(classify(i)[0] == SPELLBLADE_I for i in _pk), _pk
    print("0.1.25: The Armory (%s, read only): %d ids -> Spellblade (longsword recolours, Zweihander, Elemental swords)" % (os.path.basename(_ARMORY_PACK[0]), len(_pk)))
else:
    print("0.1.25: NOTE - The Armory pack jar is not in the Mods folder; its ids are checked from the prefixes only")
print("0.1.25: SPELLBLADE playable (%d vanilla longswords + The Armory's); the Warrior keeps swords, spears, shields" % len(_ls25))
# 0.1.25: SkyySkills' class rows (read only) - the Battlemagic slot is a companion round; say so loudly when it is missing
_SK = sorted([f for f in os.listdir(os.path.join(HERE, "..", "SkyySkills")) if re.match(r"build_skyyskills_\\d+\\.\\d+\\.\\d+\\.py$", f)],
             key=lambda f: tuple(int(x) for x in re.findall(r"\\d+", f)))
if _SK and "Battlemagic" not in open(os.path.join(HERE, "..", "SkyySkills", _SK[-1]), encoding="utf8").read():
    print("0.1.25: NOTE - %s has no Battlemagic class row: Spellblades earn no class XP (class level 0) until the SkyySkills Battlemagic "
          "round; /classadmin abil <player> grant opens their abilities for testing" % _SK[-1])''')
# the class page: one more card (8 x 96 px) - the window grows by one card (950 high, inside 1080)
rep('''CLS_W, CLS_H = 1100, 854           # 0.1.8's window, kept (Skyy: "keep the page size")''',
    '''CLS_W, CLS_H = 1100, 854 + 96      # 0.1.8's window (Skyy: "keep the page size") + one card for the Spellblade (0.1.25; 950 <= 1080)''')
rep('''Shields and tools work for every class. Hatchets are tools.''', '''Tools work for every class (hatchets too). Shields are Warrior weapons.''', 3)   # 0.1.24 made shields Warrior-only

# ================================================================================================ the ability table (the five)
NEW3 = [("ArcaneBreach", "Arcane Breach", "Spellblade", 0), ("ElementalImbue", "Elemental Imbue", "Spellblade", 1),
        ("Sunder", "Sunder", "Spellblade", 2), ("RiftCleave", "Rift Cleave", "Spellblade", 3), ("ShatteringArc", "Shattering Arc", "Spellblade", 4)]
NEW3_IDS = [a[0] for a in NEW3]
rep('''    ('HuntersNet', "Hunter's Net", 'Archer', 4, True, False),
]
assert sorted((c, t) for _i, _n, c, t, _b, _p in ABILS) == sorted([(c, t) for c in ("Mage", "Priest", "Monk", "Warrior", "Berserker", "Archer") for t in range(5)] + [("Assassin", t) for t in range(4)])''',
    '''    ('HuntersNet', "Hunter's Net", 'Archer', 4, True, False),
    # 0.1.25: THE SPELLBLADE (research/classes/Spellblade.md: A1 Arcane Breach, A2 Elemental Imbue, A2-alt Sunder, A1-alts Rift Cleave / Shattering Arc)
''' + "".join('    (%r, %r, %r, %d, True, False),\n' % a for a in NEW3) + ''']
assert sorted((c, t) for _i, _n, c, t, _b, _p in ABILS) == sorted([(c, t) for c in ("Mage", "Priest", "Monk", "Warrior", "Berserker", "Archer", "Spellblade") for t in range(5)] + [("Assassin", t) for t in range(4)])''')
# costs per shape: the page's power numbers (the old Mana in brackets) x the Spellblade split 58 / 42 (research/Class-Power-Split.md)
POW3 = [("ArcaneBreach", "AB", "abilsb", [(14, 16), (14, 16), (14, 18), (12, 16)]),
        ("ElementalImbue", "EI", "abilsb", [(12, 18), (14, 18), (14, 20), (14, 20)]),
        ("Sunder", "SU", "abilsb", [(16, 30), (16, 30), (16, 32), (18, 34)]),
        ("RiftCleave", "RC", "abilsb", [(18, 20), (18, 20), (18, 22), (18, 22)]),
        ("ShatteringArc", "SA", "abilsb", [(16, 20), (16, 20), (16, 22), (14, 20)])]
PLAN3 = {"ArcaneBreach": [(8, 1, 16), (8, 1, 16), (8, 1, 18), (7, 1, 16)], "ElementalImbue": [(7, 1, 18), (8, 1, 18), (8, 1, 20), (8, 1, 20)],
         "Sunder": [(9, 2, 30), (9, 2, 30), (9, 2, 32), (10, 2, 34)], "RiftCleave": [(10, 2, 20), (10, 2, 20), (10, 2, 22), (10, 2, 22)],
         "ShatteringArc": [(9, 2, 20), (9, 2, 20), (9, 2, 22), (8, 1, 20)]}
SNAMES3 = {"ArcaneBreach": ["Arcane Breach", "Breaching Charge", "Breach from Above", "Marked Ground"],
           "ElementalImbue": ["Elemental Imbue", "Charging Imbue", "Falling Imbue", "Deep Imbue"],
           "Sunder": ["Sunder", "Lunging Sunder", "Sunder from Above", "Armour Break"],
           "RiftCleave": ["Rift Cleave", "Running Rift", "Rift Drop", "Rift Ring"],
           "ShatteringArc": ["Shattering Arc", "Shattering Rush", "Shattering Fall", "Measured Strike"]}
rep('''    ('HuntersNet', 'HN', 'abilwba', [(14, 18), (14, 18), (14, 20), (12, 18)]),
]''', '''    ('HuntersNet', 'HN', 'abilwba', [(14, 18), (14, 18), (14, 20), (12, 18)]),
    # 0.1.25: the Spellblade (research/classes/Spellblade.md shape tables: the old Mana-only power x the 2026-10-08 split 58 / 42)
''' + "".join("    (%r, %r, %r, %r),\n" % p for p in POW3) + ''']''')
rep('''    'HuntersNet': ["Hunter's Net", 'Snare Line', 'Drop Net', 'Set Trap'],
}''', '''    'HuntersNet': ["Hunter's Net", 'Snare Line', 'Drop Net', 'Set Trap'],
''' + "".join("    %r: %r,\n" % (k, SNAMES3[k]) for k in NEW3_IDS) + '''}''')
rep('''    'HuntersNet': [(6, 2, 18), (6, 2, 18), (6, 2, 20), (5, 2, 18)],
}''', '''    'HuntersNet': [(6, 2, 18), (6, 2, 18), (6, 2, 20), (5, 2, 18)],
    # 0.1.25: research/classes/Spellblade.md (Spellblade 58 / 42)
''' + "".join("    %r: %r,\n" % (k, PLAN3[k]) for k in NEW3_IDS) + '''}''')
rep('''          "Warrior": (0.38, 0.62), "Berserker": (0.23, 0.77), "Archer": (0.43, 0.57)}                     # 0.1.24''',
    '''          "Warrior": (0.38, 0.62), "Berserker": (0.23, 0.77), "Archer": (0.43, 0.57),                     # 0.1.24
          "Spellblade": (0.58, 0.42)}                                                                       # 0.1.25''')
rep('''        if _id in NEW2_IDS:
            continue          # 0.1.24: no rows at all (the 64 KB cap) - the walking numbers are keys of ab.<Ability>.numbers''',
    '''        if _id in NEW2_IDS or _id in NEW3_IDS:
            continue          # 0.1.24: no rows at all (the 64 KB cap) - the walking numbers are keys of ab.<Ability>.numbers (0.1.25: + the Spellblade)''')
rep('''NEW2_IDS = ['RallyingGuard', ''', '''NEW3_IDS = %r   # 0.1.25: the Spellblade - costs + cooldown in their numbers row (AbilNum)
NEW2_IDS = ['RallyingGuard', ''' % NEW3_IDS)
rep('''        if _id in NEW_ABIL_IDS or _id in NEW2_IDS:   # 0.1.23: the walking row + the plan's shape numbers (scaled / shifted with it)
            _pk = PLAN_43[_id]
            _ix = {"MANA": 0, "STAM": 1, "CD": 2}[kind]
            _cl = "AbilNum" if _id in NEW2_IDS else "AbilCfg"   # 0.1.24: the walking numbers of the 15 live in AbilNum''',
    '''        if _id in NEW_ABIL_IDS or _id in NEW2_IDS or _id in NEW3_IDS:   # 0.1.23: the walking row + the plan's shape numbers (scaled / shifted with it)
            _pk = PLAN_43[_id]
            _ix = {"MANA": 0, "STAM": 1, "CD": 2}[kind]
            _cl = "AbilNum" if _id in NEW2_IDS or _id in NEW3_IDS else "AbilCfg"   # 0.1.24: the walking numbers of the 15 live in AbilNum (0.1.25: + 5)''')

# ================================================================================================ the numbers rows (AbilNum): the five + Momentum + Elements
NUM3 = {
    "ArcaneBreach": ("AB", [("mana", 8.0), ("stamina", 1.0), ("cooldown", 16.0), ("range", 5.0), ("angle", 90.0), ("power", 1.2), ("breach", 15.0),
                     ("time", 8.0), ("perStack", 1.0), ("stackCap", 10.0), ("perLevel", 0.5), ("cap", 30.0), ("step", 2.0), ("sprintTime", 7.0),
                     ("airRadius", 4.0), ("airPower", 1.0), ("airUp", 1.5), ("markRadius", 3.5), ("markBreach", 20.0), ("gain", 3.0),
                     ("chainRange", 6.0), ("durMax", 2.0)]),
    "ElementalImbue": ("EI", [("mana", 7.0), ("stamina", 1.0), ("cooldown", 18.0), ("time", 12.0), ("pct", 30.0), ("crescent", 8.0),
                       ("crescentPower", 0.8), ("crescentWidth", 1.5), ("burstRadius", 4.0), ("burstPower", 0.8), ("deepTime", 15.0),
                       ("deepStatus", 25.0), ("deepStill", 0.5), ("chainRange", 6.0), ("twinCut", 2.0)]),
    "Sunder": ("SU", [("mana", 9.0), ("stamina", 2.0), ("cooldown", 30.0), ("range", 4.0), ("power", 2.0), ("time", 12.0), ("weaken", 15.0),
               ("expose", 20.0), ("gain", 2.0), ("step", 3.0), ("lungePower", 1.8), ("airRadius", 3.0), ("airPower", 2.4), ("airStagger", 0.5),
               ("wind", 1.0), ("breakTime", 15.0), ("breakDef", 10.0), ("chainRange", 6.0), ("chainPct", 75.0), ("durMax", 2.0),
               ("splitDef", 10.0), ("splitCd", 4.0)]),
    "RiftCleave": ("RC", [("mana", 10.0), ("stamina", 2.0), ("cooldown", 20.0), ("range", 5.0), ("angle", 80.0), ("power", 1.2), ("length", 8.0),
                   ("width", 2.0), ("time", 3.0), ("breach", 15.0), ("slow", 20.0), ("runLength", 10.0), ("dropRadius", 5.0), ("ringRadius", 4.0),
                   ("ringTime", 4.0), ("ringBreach", 18.0), ("gain", 3.0), ("patch", 1.5), ("patchTime", 2.0)]),
    "ShatteringArc": ("SA", [("mana", 9.0), ("stamina", 2.0), ("cooldown", 20.0), ("range", 6.0), ("angle", 100.0), ("power", 1.2), ("perStack", 0.1),
                      ("breach", 15.0), ("breachPerStack", 1.0), ("breachCap", 30.0), ("time", 8.0), ("timePerStack", 0.25), ("keep", 5.0),
                      ("step", 3.0), ("airRadius", 5.0), ("airPower", 1.0), ("airUp", 3.0), ("halfAngle", 80.0)]),
    # the class resource + the element statuses (not abilities: their own numbers rows, the same AbilNum door)
    "Momentum": ("MO", [("max", 20.0), ("decay", 4.0), ("perHit", 1.0), ("maxPerSwing", 2.0), ("rhythm", 1.0), ("flow", 0.4), ("swing", 0.15),
                 ("rolling", 7.0), ("unstoppable", 14.0), ("pushRolling", 5.0), ("pushUnstoppable", 10.0), ("pushRange", 8.0), ("heavyHit", 15.0),
                 ("heavyDrop", 3.0), ("elemPerStack", 1.0), ("statusUnstop", 50.0), ("windKeep", 5.0), ("windEvery", 60.0), ("tempestEvery", 5.0),
                 ("tempestRadius", 4.0), ("tempestPower", 1.0), ("tempestDecay", 3.5), ("vanguardCut", 15.0), ("vanguardMax", 18.0),
                 ("pushRange3", 12.0), ("keen", 5.0)]),
    "Elements": ("EL", [("burnPct", 10.0), ("burnTime", 4.0), ("burnStacks", 3.0), ("chillSlow", 15.0), ("chillTime", 3.0), ("freezeAt", 3.0),
                 ("freezeWindow", 3.0), ("freezeTime", 1.5), ("staggerEvery", 3.0), ("staggerTime", 0.4), ("staggerDef", 10.0),
                 ("staggerDefTime", 4.0), ("shockPct", 40.0), ("shockRange", 3.0), ("shockVuln", 5.0), ("shockTime", 3.0), ("gustUp", 3.0),
                 ("gustKb", 1.0), ("poisonPct", 8.0), ("poisonTime", 6.0), ("bossCc", 50.0), ("breachMark", 5.0), ("bothBonus", 10.0)]),
}
NUM3_NAMES = {"Momentum": "Momentum", "Elements": "Element statuses"}   # the two non-ability rows (labels)
for _aid in NEW3_IDS:
    _kv = dict(NUM3[_aid][1])
    assert (_kv["mana"], _kv["stamina"], _kv["cooldown"]) == tuple(float(x) for x in PLAN3[_aid][0]), "%s: the walking numbers = the plan" % _aid


def _fld3(pre, key):
    return pre + "_" + {"mana": "MANA", "stamina": "STAM", "cooldown": "CD"}.get(key, key.upper())


_NL3 = []
for _aid in NEW3_IDS + ["Momentum", "Elements"]:
    _pre, _kvs = NUM3[_aid]
    for _k, _v in _kvs:
        _hi = "1000" if _k == "mana" else ("100" if _k == "stamina" else ("600" if _k == "cooldown" else "10000"))
        _NL3.append('_n("ab.%s.%s", "%s", "dec", %r, "0", "%s", "", "abilsb", "%s", "%s")' % (_aid, _k, _fld3(_pre, _k), float(_v), _hi, _k, _k))
rep('''# the text rows (one per ability, in ABILS order) + the AbilNum fields they fill''',
    '''# 0.1.25: THE SPELLBLADE (research/classes/Spellblade.md; mana / stamina / cooldown = the WALKING shape) + its Momentum and the element
# statuses (research/cloud/Element-System-Spec.md 5 + 10) - every number a key of ab.<Name>.numbers
''' + "\n".join(_NL3) + '''
# the text rows (one per ability, in ABILS order) + the AbilNum fields they fill''')
rep('''                                  + ['RallyingGuard', 'ShieldShockwave', 'IronChain', 'Challenge', 'GuardiansOath', 'Enrage', 'Whirlwind', 'Earthsplitter', 'BloodFrenzy', 'WarlordsBanner', 'PinningShot', 'RapidFire', 'ExplosiveArrow', 'ArrowRain', 'HuntersNet'])   # 0.1.24''',
    '''                                  + ['RallyingGuard', 'ShieldShockwave', 'IronChain', 'Challenge', 'GuardiansOath', 'Enrage', 'Whirlwind', 'Earthsplitter', 'BloodFrenzy', 'WarlordsBanner', 'PinningShot', 'RapidFire', 'ExplosiveArrow', 'ArrowRain', 'HuntersNet']   # 0.1.24
                                  + %r)   # 0.1.25''' % (NEW3_IDS + ["Momentum", "Elements"]))
rep('''    _nm = dict((a[0], a[1]) for a in ABILS)[_aid]''', '''    _nm = dict((a[0], a[1]) for a in ABILS).get(_aid) or %r[_aid]   # 0.1.25: + Momentum / Element statuses''' % NUM3_NAMES)
rep('''       ("key=value: time s, radius/range blocks, speed/slow/weaken %, power x one hit; no key = its default" if _aid not in NEW2_IDS else
        "key=value: mana stamina cooldown = walking cost; s, blocks, %, power x one hit; no key = default"))''',
    '''       ("key=value: time s, radius/range blocks, speed/slow/weaken %, power x one hit; no key = its default" if _aid not in NEW2_IDS + NEW3_IDS + ["Momentum", "Elements"] else
        ("key=value: stacks, s, blocks, %, power x one hit; no key = its default" if _aid in ("Momentum", "Elements") else
         "key=value: mana stamina cooldown = walking cost; s, blocks, %, power x one hit; no key = default")))''')
rep('''            ("abilwba", "Warrior Bers. Archer")]   # 0.1.24 (one category: the config kit allows 16)''',
    '''            ("abilwba", "Warrior Bers. Archer"),   # 0.1.24 (one category: the config kit allows 16)
            ("abilsb", "Spellblade abilities")]    # 0.1.25: the 16th (the kit's last) - the five + Momentum + the element statuses''')
# 0.1.25 REBIRTH SLOTS (Rebirth-Spec R6): the two rows (the abill category)
rep('''_r("rb.classCap0", "RB_CAP0", "int", 100, "1", "1000", "", "abill", "First-run class level cap", "Rebirth: the floor F(L) = min(15, 1 + 14 L / this).", "live,adv")''',
    '''_r("rb.classCap0", "RB_CAP0", "int", 100, "1", "1000", "", "abill", "First-run class level cap", "Rebirth: the floor F(L) = min(15, 1 + 14 L / this).", "live,adv")
# 0.1.25 (research/cloud/Rebirth-Spec.md R6, Skyy 2026-10-13 "and like every 5th rebirth you get another modifier slot")
_r("rb.modSlotEvery", "RB_SLOT_EVERY", "int", 5, "0", "100", "", "abill", "Rebirths per extra modifier slot", "Every ability gets one more modifier slot per this many rebirths. 0 = off.")
_r("rb.modSlotMax", "RB_SLOT_MAX", "int", 2, "0", "2", "", "abill", "Most extra modifier slots", "On top of the tree's 2 (slots 3 and 4: rebirth 5 and 10).")''')
# affordable when unlocked (research/Class-Power-Split.md: Spellblade base Mana 33 + 4 a level, Stamina 10 + 7 + 0.09 a level)
rep('''         ("Berserker", 1): (14, 22.16), ("Berserker", 10): (32, 23.6), ("Berserker", 20): (52, 25.2), ("Berserker", 30): (72, 26.8)}''',
    '''         ("Berserker", 1): (14, 22.16), ("Berserker", 10): (32, 23.6), ("Berserker", 20): (52, 25.2), ("Berserker", 30): (72, 26.8),
         ("Spellblade", 1): (37, 17.09), ("Spellblade", 10): (73, 17.9), ("Spellblade", 20): (113, 18.8), ("Spellblade", 30): (153, 19.7)}   # 0.1.25''')
rep('''assert _aff == 37 + 20 + 16 + 60, _aff     # the plan's "all 37 shape rows PASS" + 0.1.23: Monk 5 x 4, Assassin 4 x 4 + 0.1.24: 15 x 4''',
    '''assert _aff == 37 + 20 + 16 + 60 + 20, _aff     # the plan's "all 37 shape rows PASS" + 0.1.23: Monk 5 x 4, Assassin 4 x 4 + 0.1.24: 15 x 4 + 0.1.25: 5 x 4''')
DESC3 = {
    "ArcaneBreach": "Walk - a wide arc: enemies take more from everyone (Breach). Sprint - step in. Air - on landing. Crouch - Marked Ground.",
    "ElementalImbue": "Your hits deal element damage + its status for 12 s. Sprint - a crescent ahead. Air - a burst on landing. Crouch - Deep Imbue.",
    "Sunder": "A heavy strike on the enemy you look at - it deals 15 % less. Sprint - lunge in. Air - from above. Crouch - Armour Break.",
    "RiftCleave": "An arc that tears a rift: inside Breached + slowed. Sprint - behind you. Air - a circle on landing. Crouch - Rift Ring.",
    "ShatteringArc": "Spend your Momentum on one huge arc + Breach (keep 5). Sprint - step in. Air - a circle on landing. Crouch - spend half.",
}
assert all(len(v) <= 130 for v in DESC3.values())
rep('''ABIL_DESCS_.update({   # 0.1.23''', '''ABIL_DESCS_.update(%r)   # 0.1.25
ABIL_DESCS_.update({   # 0.1.23''' % DESC3)

# ================================================================================================ modifiers, nouns, runes, the class tree list
MODS3 = {"ArcaneBreach": ["Radius", "Duration", "Power", "Chain"], "ElementalImbue": ["Duration", "Power", "Efficiency", "Chain"],
         "Sunder": ["Duration", "Power", "Chain", "Echo"], "RiftCleave": ["Duration", "Radius", "Slow", "Power", "Echo"],
         "ShatteringArc": ["Power", "Radius", "Knockback", "Leech", "Echo"]}
rep('''    'HuntersNet': ['Radius', 'Duration', 'Pull', 'Split'],
}''', '''    'HuntersNet': ['Radius', 'Duration', 'Pull', 'Split'],
    # 0.1.25 (research/classes/Spellblade.md; Skyy Q8 "Echo on Sunder + the A1-alts, not on Breach / Imbue")
''' + "".join("    %r: %r,\n" % (k, MODS3[k]) for k in NEW3_IDS) + '''}''')
rep('''assert all(a in MOD_IDS and b in MOD_IDS for a, b in MOD_EXCL)''',
    '''assert all(a in MOD_IDS and b in MOD_IDS for a, b in MOD_EXCL)
assert all("Echo" in AB_MODS[_a] for _a in ("Sunder", "RiftCleave", "ShatteringArc")) and not [_a for _a in ("ArcaneBreach", "ElementalImbue") if "Echo" in AB_MODS[_a]], \\
    "Skyy Q8 (2026-10-08 popup batch 1): Echo on Sunder + the A1-alts, not on Breach / Imbue"''')
NOUN3 = {"ArcaneBreach": "damage + Breach", "ElementalImbue": "element damage", "Sunder": "damage + Weaken", "RiftCleave": "rift Breach",
         "ShatteringArc": "damage per stack"}
rep("""           'HuntersNet': 'damage',
           }""", """           'HuntersNet': 'damage',
""" + "".join("           %r: %r,\n" % (k, NOUN3[k]) for k in NEW3_IDS) + """           }""")
rep('''                                      "CloakFirstStrike", "Toxin", "GodKiller", "VanishingAct"] + ['RallyingGuard', 'ShieldShockwave', 'IronChain', 'Challenge', 'GuardiansOath', 'Enrage', 'Whirlwind', 'Earthsplitter', 'BloodFrenzy', 'WarlordsBanner', 'PinningShot', 'RapidFire', 'ExplosiveArrow', 'ArrowRain', 'HuntersNet']   # 0.1.24''',
    '''                                      "CloakFirstStrike", "Toxin", "GodKiller", "VanishingAct"] + ['RallyingGuard', 'ShieldShockwave', 'IronChain', 'Challenge', 'GuardiansOath', 'Enrage', 'Whirlwind', 'Earthsplitter', 'BloodFrenzy', 'WarlordsBanner', 'PinningShot', 'RapidFire', 'ExplosiveArrow', 'ArrowRain', 'HuntersNet'] + %r   # 0.1.24 + 0.1.25''' % NEW3_IDS)
rep('''          "Archer": ["PA1", "PA2", "PA3", "PA4", "PA5", "PB1", "PB2", "PB3", "PB4", "PC1", "PC2", "PC3", "PC4", "PC5"]}''',
    '''          "Archer": ["PA1", "PA2", "PA3", "PA4", "PA5", "PB1", "PB2", "PB3", "PB4", "PC1", "PC2", "PC3", "PC4", "PC5"],
          # 0.1.25 (research/classes/Spellblade.md class tree): Second Wind, Keen Edge, Tempo; Tempest PA1 / PA2 / PA5; Breaker PB1 / PB2 /
          # PB4; Vanguard PC3 / PC5 - the rest wait (the great shield + traversals = SkyyArmory, reactions + boss affixes = later)
          "Spellblade": ["T4", "T5", "T6", "PA1", "PA2", "PA5", "PB1", "PB2", "PB4", "PC3", "PC5"]}''')
rep('''TREE_READS = ",".join("Class.%s.%s" % (_c, _n) for _c in ("Mage", "Priest", "Monk", "Assassin", "Warrior", "Berserker", "Archer") for _n in TREE_SLOTS + TREE_K[_c])''',
    '''TREE_READS = ",".join("Class.%s.%s" % (_c, _n) for _c in ("Mage", "Priest", "Monk", "Assassin", "Warrior", "Berserker", "Archer", "Spellblade") for _n in TREE_SLOTS + TREE_K[_c])''')
rep('''    "# 0.1.24: ab.RallyingGuard.numbers ... ab.HuntersNet.numbers = the Warrior / Berserker / Archer abilities (walking cost inside).",
''', '''    "# 0.1.24: ab.RallyingGuard.numbers ... ab.HuntersNet.numbers = the Warrior / Berserker / Archer abilities (walking cost inside).",
    "# 0.1.25: ab.ArcaneBreach.numbers ... ab.ShatteringArc.numbers = the Spellblade; ab.Momentum / ab.Elements.numbers; rb.modSlot* = rebirth slots.",
''')
# the rune icons: no Spellblade art yet - our own Mage / Warrior / Berserker ability art recoloured teal (#6fd0d8) until the art round
rep('''    _png = open(os.path.join(_ICON_SRC, _a[2], ICON_STANDIN.get(_a[0], _a[0]) + ".png"), "rb").read()   # 0.1.24: stand-in icons''',
    '''    if _a[2] == "Spellblade":   # 0.1.25: STAND-INS (our art of another class, recoloured to the Spellblade teal) until the art round
        _png = SA.recolor(open(os.path.join(_ICON_SRC, ICON_SB[_a[0]][0], ICON_SB[_a[0]][1] + ".png"), "rb").read(), SB_TEAL)
    else:
        _png = open(os.path.join(_ICON_SRC, _a[2], ICON_STANDIN.get(_a[0], _a[0]) + ".png"), "rb").read()   # 0.1.24: stand-in icons''')
rep('''ICON_STANDIN = {"Challenge": "Unbreakable", "GuardiansOath": "BulwarkStance"}''',
    '''ICON_SB = {"ArcaneBreach": ("Mage", "ArcaneBeam"), "ElementalImbue": ("Mage", "Starfall"), "Sunder": ("Warrior", "ShieldShockwave"),
           "RiftCleave": ("Berserker", "Earthsplitter"), "ShatteringArc": ("Berserker", "Whirlwind")}   # 0.1.25: the Spellblade stand-ins (no art yet)
SB_TEAL = ((8, 30, 36), (24, 78, 88), (60, 150, 160), (111, 208, 216), (214, 248, 250))   # dark -> light, the class colour #6fd0d8 in the middle
assert not os.path.isdir(os.path.join(_ICON_SRC, "Spellblade")), "real Spellblade art arrived - drop the stand-ins"
ICON_STANDIN = {"Challenge": "Unbreakable", "GuardiansOath": "BulwarkStance"}''')

# ================================================================================================ AbilDefs: the new indices
rep('''                  ("PIN", "PinningShot"), ("RAPID", "RapidFire"), ("EXPLO", "ExplosiveArrow"), ("RAIN", "ArrowRain"), ("NET", "HuntersNet")):''',
    '''                  ("PIN", "PinningShot"), ("RAPID", "RapidFire"), ("EXPLO", "ExplosiveArrow"), ("RAIN", "ArrowRain"), ("NET", "HuntersNet"),
                  # 0.1.25: the Spellblade
                  ("BREACH", "ArcaneBreach"), ("IMBUE", "ElementalImbue"), ("SUNDER", "Sunder"), ("RIFT", "RiftCleave"), ("SHATTER", "ShatteringArc")):''')
# ================================================================================================ AbilStore maps, AbilCtx (slots 3 + 4), counters
rep('''           "BANNERS", "SPINS", "CHAINED", "RETRI", "DEADEYE", "BANKED", "SWINGS", "BLEEDS", "PAID"):''',
    '''           "BANNERS", "SPINS", "CHAINED", "RETRI", "DEADEYE", "BANKED", "SWINGS", "BLEEDS", "PAID",
           # 0.1.25: UUID -> long[] the Momentum ring (gain times); UUID -> long[] Momentum state {last hit, rhythm armed at, swing at, swing
           # hits, Second Wind at, hit counter, tree flags 1 T4 2 PA5 4 PC3 8 PC5 16 T5, next tick, flags read at, unstoppable since};
           # UUID -> double[] Imbue {until, element, %, status mult, chain, counted, pkey hash}; mob Ref -> double[] Breach {until, %, msb,
           # lsb, flags 1 PB4}; mob Ref -> double[] Sunder {until, weaken %, defence %, msb, lsb, flags 1 PB4}; mob Ref -> double[] Shocked
           # {until, %}; mob Ref -> double[] Stagger {until, defence %, Earth hits}; mob Ref -> long[] the last Chills; mob Ref ->
           # ArrayList the Burn / Poison jobs; pkey -> Long the Imbue casts (Twin Attunement alternates)
           # FIX 2: UUID -> long[] {next Spellblade probe} (momTick asks "is this a Spellblade?" at most once a second per player until one is seen)
           "MOMS", "MOMX", "IMBUE", "BREACH", "SUNDER", "SHOCKD", "STAGD", "CHILLS", "DOTS", "IMBN", "SBP"):''')
rep('''           "public int m0;", "public int m1;", "public int l0;", "public int l1;", "public boolean echo;", "public double echoPct;",''',
    '''           "public int m0;", "public int m1;", "public int l0;", "public int l1;", "public boolean echo;", "public double echoPct;",
           "public int m2;", "public int m3;", "public int l2;", "public int l3;",   # 0.1.25: modifier slots 3 + 4 (rebirth 5 / 10)''')
rep('''  this.ai = -1;
  this.m0 = -1;
  this.m1 = -1;''', '''  this.ai = -1;
  this.m0 = -1;
  this.m1 = -1;
  this.m2 = -1;
  this.m3 = -1;''')
rep('''  if (mi >= 0 && this.m0 == mi) n++;
  if (mi >= 0 && this.m1 == mi) n++;''', '''  if (mi >= 0 && this.m0 == mi) n++;
  if (mi >= 0 && this.m1 == mi) n++;
  if (mi >= 0 && this.m2 == mi) n++;   // 0.1.25: rebirth slots
  if (mi >= 0 && this.m3 == mi) n++;''')
rep('''  if (this.m0 == mi) return this.l0;
  if (this.m1 == mi) return this.l1;''', '''  if (this.m0 == mi) return this.l0;
  if (this.m1 == mi) return this.l1;
  if (this.m2 == mi) return this.l2;   // 0.1.25
  if (this.m3 == mi) return this.l3;''')
rep('''  c.pctAdd = this.pctAdd; c.hotAdd = this.hotAdd; c.m0 = this.m0; c.m1 = this.m1; c.l0 = this.l0; c.l1 = this.l1; c.echo = this.echo;''',
    '''  c.pctAdd = this.pctAdd; c.hotAdd = this.hotAdd; c.m0 = this.m0; c.m1 = this.m1; c.l0 = this.l0; c.l1 = this.l1; c.echo = this.echo;
  c.m2 = this.m2; c.m3 = this.m3; c.l2 = this.l2; c.l3 = this.l3;''')
rep('''  c.m0 = -1;
  c.m1 = -1;
  c.l0 = 0;
  c.l1 = 0;''', '''  c.m0 = -1;
  c.m1 = -1;
  c.l0 = 0;
  c.l1 = 0;
  c.m2 = -1;
  c.m3 = -1;
  c.l2 = 0;
  c.l3 = 0;''')
rep('''           "public static volatile String LAST_WAR = \\"\\";", "public static volatile String LAST_BER = \\"\\";", "public static volatile String LAST_ARC = \\"\\";"):
    F(abil, _f)''', '''           "public static volatile String LAST_WAR = \\"\\";", "public static volatile String LAST_BER = \\"\\";", "public static volatile String LAST_ARC = \\"\\";"):
    F(abil, _f)
# 0.1.25: the Spellblade counters (the harness + /classadmin abil info); SB_LIVE = a Spellblade was seen since the start (the hooks' fast exit)
for _f in ("public static volatile long BREACHED = 0L;", "public static volatile long SUNDERED = 0L;", "public static volatile long IMBUED = 0L;",
           "public static volatile long STATUSES = 0L;", "public static volatile long MOMGAIN = 0L;", "public static volatile long MOMLOST = 0L;",
           "public static volatile long RIFTS = 0L;", "public static volatile long SHATTERS = 0L;", "public static volatile long ATTUNES = 0L;",
           "public static volatile boolean SB_LIVE = false;", "public static volatile String LAST_SB = \\"\\";",
           "public static final String[] ELN = new String[] { \\"Fire\\", \\"Water\\", \\"Earth\\", \\"Lightning\\", \\"Wind\\", \\"Poison\\" };",
           "public static final String[] ELS = new String[] { \\"Burn\\", \\"Chill\\", \\"Stagger\\", \\"Shock\\", \\"Gust\\", \\"Poison\\" };"):
    F(abil, _f)''')

# ================================================================================================ (3) REBIRTH MODIFIER SLOTS: equipped / ctxFor / used / panel / modRows / equipMod
rep('''public static int[] equipped(java.util.Properties p, int ai, int lvl, int slots) {
  int[] r = new int[] { -1, -1 };
  if (ai < 0) return r;
  String id = @PKG@.AbilDefs.IDS[ai];
  String[] e = eqOf(p, id);
  for (int j = 0; j < 2 && j < slots; j++) {
    int mi = @PKG@.AbilModDefs.find(e[j]);
    int k = @PKG@.AbilModDefs.pos(ai, mi);
    if (mi < 0 || k < 0 || lvl < @PKG@.AbilModDefs.unlockAt(k)) continue;
    if (j == 1 && r[0] == mi) {
      if (!@PKG@.AbilModDefs.MSTACK[mi]) continue;
      if (mlvl(p, id, mi) < 2) continue;
    }
    if (j == 1 && r[0] >= 0 && @PKG@.AbilModDefs.excl(r[0], mi)) continue;   // 0.1.24: Floor / Duration+, Seeker / Ricochet
    r[j] = mi;
  }
  return r;
}''', '''public static int[] equipped(java.util.Properties p, int ai, int lvl, int slots) {
  int[] r = new int[] { -1, -1, -1, -1 };   // 0.1.25: slots 3 + 4 (rebirth) - e2.<Ability>
  if (ai < 0) return r;
  String id = @PKG@.AbilDefs.IDS[ai];
  String[] e = eqOf4(p, id);
  for (int j = 0; j < 4 && j < slots; j++) {
    int mi = @PKG@.AbilModDefs.find(e[j]);
    int k = @PKG@.AbilModDefs.pos(ai, mi);
    if (mi < 0 || k < 0 || lvl < @PKG@.AbilModDefs.unlockAt(k)) continue;
    int same = 0;
    boolean ex = false;
    for (int q = 0; q < j; q++) {
      if (r[q] == mi) same++;
      else if (r[q] >= 0 && @PKG@.AbilModDefs.excl(r[q], mi)) ex = true;   // 0.1.24: Floor / Duration+, Seeker / Ricochet
    }
    if (ex || same >= 2) continue;   // 0.1.25: a modifier fills at most two slots (the double), never three
    if (same == 1) {
      if (!@PKG@.AbilModDefs.MSTACK[mi]) continue;
      if (mlvl(p, id, mi) < 2) continue;
    }
    r[j] = mi;
  }
  return r;
}''')
rep('''    int[] eq = equipped(p, ai, stored, modSlots(csv, ai));     // unlocked modifiers stay unlocked (Skyy 5b)
    c.m0 = eq[0];
    c.m1 = eq[1];
    c.l0 = c.m0 < 0 ? 0 : modEff(p, id, stored, c.lvl, mlvl(p, id, c.m0));
    c.l1 = c.m1 < 0 ? 0 : modEff(p, id, stored, c.lvl, mlvl(p, id, c.m1));''',
    '''    int[] eq = equipped(p, ai, stored, slotsOf(csv, ai, k));   // unlocked modifiers stay unlocked (Skyy 5b); 0.1.25: + rebirth slots
    c.m0 = eq[0];
    c.m1 = eq[1];
    c.m2 = eq[2];
    c.m3 = eq[3];
    c.l0 = c.m0 < 0 ? 0 : modEff(p, id, stored, c.lvl, mlvl(p, id, c.m0));
    c.l1 = c.m1 < 0 ? 0 : modEff(p, id, stored, c.lvl, mlvl(p, id, c.m1));
    c.l2 = c.m2 < 0 ? 0 : modEff(p, id, stored, c.lvl, mlvl(p, id, c.m2));
    c.l3 = c.m3 < 0 ? 0 : modEff(p, id, stored, c.lvl, mlvl(p, id, c.m3));''')
rep('''    int[] eq = @PKG@.AbilCfg.MODS_ON ? equipped(p, ai, l0, modSlots(treeCsv(u), ai)) : new int[] { -1, -1 };
    String[] ks = new String[3];
    String[] vs = new String[3];''', '''    int[] eq = @PKG@.AbilCfg.MODS_ON ? equipped(p, ai, l0, slotsOf(treeCsv(u), ai, k)) : new int[] { -1, -1, -1, -1 };
    String[] ks = new String[5];
    String[] vs = new String[5];''')
rep('''    for (int j = 0; j < 2; j++) {
      int mi = eq[j];
      if (mi < 0) continue;
      if (j == 1 && eq[0] == mi) continue;
      int add = (eq[0] == mi && eq[1] == mi) ? 2 : 1;''', '''    for (int j = 0; j < eq.length; j++) {
      int mi = eq[j];
      if (mi < 0) continue;
      boolean dup = false;
      int add = 1;
      for (int q = 0; q < eq.length; q++) { if (q < j && eq[q] == mi) dup = true; if (q != j && eq[q] == mi) add++; }   // 0.1.25: 4 slots
      if (dup) continue;
      if (add > 2) add = 2;''')
rep('''  Object[] o = new Object[78];
  o[0] = "noclass";''', '''  Object[] o = new Object[94];   // 0.1.25: + [78 + i * 4 ..] = slot 3 + 4 of card i (name, level, name, level) - SkyyTrees 0.3.10
  o[0] = "noclass";''')
rep('''    int slots = modSlots(csv, ai);
    int[] eq = ai < 0 ? new int[] { -1, -1 } : equipped(p, ai, l, slots);''', '''    int slots = ai < 0 ? 0 : slotsOf(csv, ai, k);   // 0.1.25: + the rebirth slots
    int[] eq = ai < 0 ? new int[] { -1, -1, -1, -1 } : equipped(p, ai, l, slots);''')
rep('''    o[b + 14] = Integer.valueOf(slots);''', '''    o[b + 14] = Integer.valueOf(slots);
    o[78 + i * 4] = eq[2] < 0 ? "" : @PKG@.AbilModDefs.MNAME[eq[2]];   // 0.1.25: rebirth slots 3 + 4
    o[79 + i * 4] = Integer.valueOf(eq[2] < 0 ? 0 : mlvl(p, id, eq[2]));
    o[80 + i * 4] = eq[3] < 0 ? "" : @PKG@.AbilModDefs.MNAME[eq[3]];
    o[81 + i * 4] = Integer.valueOf(eq[3] < 0 ? 0 : mlvl(p, id, eq[3]));''')
rep('''  int slots = modSlots(csv, ai);
  int[] eq = equipped(p, ai, l, slots);
  String[] st = eqOf(p, aid);
  long picks = numOf(p, "rb.pick." + aid);   // 0.1.23: rebirth upgrades still to place''',
    '''  int slots = slotsOf(csv, ai, k);   // 0.1.25: + the rebirth slots
  int[] eq = equipped(p, ai, l, slots);
  String[] st = eqOf4(p, aid);
  long picks = numOf(p, "rb.pick." + aid);   // 0.1.23: rebirth upgrades still to place''')
rep('''    + "|" + (eq[0] < 0 ? "" : @PKG@.AbilModDefs.MID[eq[0]]) + "|" + (eq[1] < 0 ? "" : @PKG@.AbilModDefs.MID[eq[1]]) + "|" + gainText(ai, l) + "|" + picks;''',
    '''    + "|" + (eq[0] < 0 ? "" : @PKG@.AbilModDefs.MID[eq[0]]) + "|" + (eq[1] < 0 ? "" : @PKG@.AbilModDefs.MID[eq[1]]) + "|" + gainText(ai, l) + "|" + picks
    // 0.1.25: 11 slot 3, 12 slot 4, 13 rebirth slots, 14 tree slots, 15 the Imbue attunement ("Fire" or "Fire+Water"; "" = not Imbue),
    // 16 rb.modSlotEvery, 17 rb.modSlotMax (fix round: SkyyTrees' closed-slot text follows the live Server Setup numbers)
    + "|" + (eq[2] < 0 ? "" : @PKG@.AbilModDefs.MID[eq[2]]) + "|" + (eq[3] < 0 ? "" : @PKG@.AbilModDefs.MID[eq[3]]) + "|" + rbSlots(k) + "|" + modSlots(csv, ai)
    + "|" + (ai == @PKG@.AbilDefs.IMBUE ? attText(k, csv) : "") + "|" + @PKG@.AbilCfg.RB_SLOT_EVERY + "|" + @PKG@.AbilCfg.RB_SLOT_MAX;''')
rep('''    int cnt = (eq[0] == mi ? 1 : 0) + (eq[1] == mi ? 1 : 0);''',
    '''    int cnt = (eq[0] == mi ? 1 : 0) + (eq[1] == mi ? 1 : 0) + (eq[2] == mi ? 1 : 0) + (eq[3] == mi ? 1 : 0);   // 0.1.25: 4 slots''')
rep('''  int slots = modSlots(csv, ai);
  if (slot < 0 || slot > 1) return "-Pick modifier slot 1 or 2.";
  if (slot >= slots) return "-Modifier slot " + (slot + 1) + " of " + nm + " is not open - unlock M" + lineOf(ai) + (slot == 0 ? "A" : "B") + " in your class tree.";
  String[] e = eqOf(p, aid);''', '''  int slots = slotsOf(csv, ai, k);   // 0.1.25: + the rebirth slots
  if (slot < 0 || slot > 3) return "-Pick modifier slot 1 - 4.";
  if (slot >= slots) return "-Modifier slot " + (slot + 1) + " of " + nm + " is not open - " + slotHint(csv, ai, k, slot) + ".";
  String[] e = eqOf4(p, aid);''')
rep('''    int other = @PKG@.AbilModDefs.find(e[slot == 0 ? 1 : 0]);
    if (other == mi) {
      if (!@PKG@.AbilModDefs.MSTACK[mi]) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " cannot be equipped twice.";
      if (mlvl(p, aid, mi) < 2) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " can go in both slots from modifier Lv 2.";
    }
    if (other >= 0 && other != mi && @PKG@.AbilModDefs.excl(mi, other)) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " never goes together with " + @PKG@.AbilModDefs.MNAME[other] + " - take " + @PKG@.AbilModDefs.MNAME[other] + " out first.";   // 0.1.24''',
    '''    int same = 0;   // 0.1.25: the doubling + exclusion rules over every OTHER slot (4 slots)
    for (int q = 0; q < 4; q++) {
      if (q == slot) continue;
      int other = @PKG@.AbilModDefs.find(e[q]);
      if (other == mi) same++;
      else if (other >= 0 && @PKG@.AbilModDefs.excl(mi, other)) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " never goes together with " + @PKG@.AbilModDefs.MNAME[other] + " - take " + @PKG@.AbilModDefs.MNAME[other] + " out first.";   // 0.1.24
    }
    if (same >= 2) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " already fills two slots - a modifier doubles at most once.";
    if (same == 1) {
      if (!@PKG@.AbilModDefs.MSTACK[mi]) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " cannot be equipped twice.";
      if (mlvl(p, aid, mi) < 2) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " can go in two slots from modifier Lv 2.";
    }''')
rep('''  String v = e[0] + "," + e[1];
  if (",".equals(v)) v = null;
  if (!@PKG@.AbilStore.set(k, new String[] { "e." + aid }, new String[] { v })) return "-Your ability file could not be read - nothing changed (see the server log).";
  @PKG@.AbilStore.saveSoon(k);
  mirrorSoon(u);
  return "+" + nm + ": slot 1 " + (e[0].length() == 0 ? "empty" : @PKG@.AbilModDefs.MNAME[@PKG@.AbilModDefs.find(e[0])]) + ", slot 2 " + (e[1].length() == 0 ? "empty" : @PKG@.AbilModDefs.MNAME[@PKG@.AbilModDefs.find(e[1])]) + ".";''',
    '''  String v = e[0] + "," + e[1];
  if (",".equals(v)) v = null;
  String v2 = e[2] + "," + e[3];   // 0.1.25: slots 3 + 4 in their own key (an older jar never reads them)
  if (",".equals(v2)) v2 = null;
  if (!@PKG@.AbilStore.set(k, new String[] { "e." + aid, "e2." + aid }, new String[] { v, v2 })) return "-Your ability file could not be read - nothing changed (see the server log).";
  @PKG@.AbilStore.saveSoon(k);
  mirrorSoon(u);
  return "+" + nm + ": slot 1 " + (e[0].length() == 0 ? "empty" : @PKG@.AbilModDefs.MNAME[@PKG@.AbilModDefs.find(e[0])]) + ", slot 2 " + (e[1].length() == 0 ? "empty" : @PKG@.AbilModDefs.MNAME[@PKG@.AbilModDefs.find(e[1])])
    + (slots > 2 ? ", slot 3 " + (e[2].length() == 0 ? "empty" : @PKG@.AbilModDefs.MNAME[@PKG@.AbilModDefs.find(e[2])]) : "")
    + (slots > 3 ? ", slot 4 " + (e[3].length() == 0 ? "empty" : @PKG@.AbilModDefs.MNAME[@PKG@.AbilModDefs.find(e[3])]) : "") + ".";''')
rep('''  String mds = (cx.m0 >= 0 ? " m0=" + @PKG@.AbilModDefs.MID[cx.m0] + cx.l0 : "") + (cx.m1 >= 0 ? " m1=" + @PKG@.AbilModDefs.MID[cx.m1] + cx.l1 : "");''',
    '''  String mds = (cx.m0 >= 0 ? " m0=" + @PKG@.AbilModDefs.MID[cx.m0] + cx.l0 : "") + (cx.m1 >= 0 ? " m1=" + @PKG@.AbilModDefs.MID[cx.m1] + cx.l1 : "")
    + (cx.m2 >= 0 ? " m2=" + @PKG@.AbilModDefs.MID[cx.m2] + cx.l2 : "") + (cx.m3 >= 0 ? " m3=" + @PKG@.AbilModDefs.MID[cx.m3] + cx.l3 : "");   // 0.1.25''')
# doAction: the Imbue attunement (the panel's Element row)
rep('''  } else if (x.equals("rbpick")) {
    r = rbPick(u, a, b);   // 0.1.23: one rebirth upgrade -> that modifier may reach one more level
  }''', '''  } else if (x.equals("rbpick")) {
    r = rbPick(u, a, b);   // 0.1.23: one rebirth upgrade -> that modifier may reach one more level
  } else if (x.equals("attune")) {
    r = attune(u, a, b, csv);   // 0.1.25: the Spellblade's Imbue element (out of combat)
  }''')

L25 = []


def late25(src):
    L25.append(src.strip("\n"))


# ---------------------------------------------------------------- rebirth slots
late25(r'''
public static int rbSlots(String k) {
  long ev = @PKG@.AbilCfg.RB_SLOT_EVERY;
  long mx = @PKG@.AbilCfg.RB_SLOT_MAX;
  if (k == null || ev <= 0L || mx <= 0L) return 0;
  long n = (long) rbN(k) / ev;
  if (n > mx) n = mx;
  if (n > 2L) n = 2L;
  return n < 0L ? 0 : (int) n;
}''')
late25(r'''
public static int slotsOf(String csv, int ai, String k) {
  if (ai < 0) return 0;
  int n = modSlots(csv, ai) + rbSlots(k);
  return n > 4 ? 4 : n;
}''')
late25(r'''
public static String slotHint(String csv, int ai, String k, int slot) {
  int t = modSlots(csv, ai);
  int rb = rbSlots(k);
  long ev = @PKG@.AbilCfg.RB_SLOT_EVERY;
  if (t < 2 && @PKG@.AbilCfg.TREE_GATE) return "unlock M" + lineOf(ai) + (t == 0 ? "A" : "B") + " in your class tree" + (ev > 0L && rb < (int) @PKG@.AbilCfg.RB_SLOT_MAX ? " (or reach rebirth " + ((long) (rb + 1) * ev) + ")" : "");
  if (ev > 0L && rb < (int) @PKG@.AbilCfg.RB_SLOT_MAX) return "it opens at rebirth " + ((long) (rb + 1) * ev);
  return "this ability has no more slots";
}''')
late25(r'''
public static String[] eqOf4(java.util.Properties p, String id) {
  String[] a = eqOf(p, id);
  String v = p == null ? "" : p.getProperty("e2." + id, "");
  String[] r = new String[] { a[0], a[1], "", "" };
  int c = v.indexOf(',');
  if (c < 0) r[2] = v.trim();
  else { r[2] = v.substring(0, c).trim(); r[3] = v.substring(c + 1).trim(); }
  return r;
}''')

# ---------------------------------------------------------------- the Spellblade: class, weapon, tree flags
late25(r'''
public static int sbCi() {
  return @PKG@.AbilDefs.CLS[@PKG@.AbilDefs.BREACH];
}''')
late25(r'''
public static boolean sbWeapon(java.util.UUID u, String item) {
  if (u == null || item == null) return false;
  int ci = sbCi();
  return @PKG@.ClassDefs.ownerOf(item) == ci && @PKG@.ClassRules.allowed(u, item);
}''')
late25(r'''
public static double powMul(@PKG@.AbilCtx c) {
  return c == null ? 1.0 : 1.0 + @PKG@.AbilCfg.MOD_POWER * (double) c.eff(@PKG@.AbilModDefs.POWER) / 100.0;
}''')
# Duration+ on a debuff with a cap ("Breach lasts longer - max +2 s"): base x the Duration+ multiplier, never more than base + extraMax
late25(r'''
public static double durCap(double base, double extraMax) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  if (c == null) return base;
  double v = base * c.durMult;
  if (v > base + extraMax) v = base + extraMax;
  v = v + c.durAdd;
  return v < 0.5 ? 0.5 : v;
}''')
late25(r'''
public static long sbFlags(java.util.UUID u, long now) {
  long[] x = momX(u);
  if (x == null) return 0L;
  if (now - x[8] < 2000L && now >= x[8]) return x[6];
  String csv = treeCsv(u);
  long f = 0L;
  if (@PKG@.AbilModDefs.csvHas(csv, "T4")) f = f + 1L;
  if (@PKG@.AbilModDefs.csvHas(csv, "PA5")) f = f + 2L;
  if (@PKG@.AbilModDefs.csvHas(csv, "PC3")) f = f + 4L;
  if (@PKG@.AbilModDefs.csvHas(csv, "PC5")) f = f + 8L;
  if (@PKG@.AbilModDefs.csvHas(csv, "T5")) f = f + 16L;
  x[6] = f;
  x[8] = now;
  return f;
}''')

# ---------------------------------------------------------------- MOMENTUM (the class resource)
late25(r'''
public static long[] momX(java.util.UUID u) {
  if (u == null) return null;
  Object o = @PKG@.AbilStore.MOMX.get(u);
  if (o instanceof long[]) return (long[]) o;
  long[] x = new long[10];
  @PKG@.AbilStore.MOMX.put(u, x);
  return x;
}''')
late25(r'''
public static long[] momRing(java.util.UUID u) {
  Object o = @PKG@.AbilStore.MOMS.get(u);
  if (o instanceof long[]) return (long[]) o;
  long[] r = new long[30];
  @PKG@.AbilStore.MOMS.put(u, r);
  return r;
}''')
late25(r'''
public static int momMax(long flags) {
  double m = (flags & 8L) != 0L ? @PKG@.AbilNum.MO_VANGUARDMAX : @PKG@.AbilNum.MO_MAX;
  int n = (int) Math.round(m);
  return n < 1 ? 1 : (n > 30 ? 30 : n);
}''')
late25(r'''
public static long momDecay(long flags) {
  double d = (flags & 2L) != 0L ? @PKG@.AbilNum.MO_TEMPESTDECAY : @PKG@.AbilNum.MO_DECAY;
  return ms(d < 0.5 ? 0.5 : d);
}''')
late25(r'''
public static int momN(java.util.UUID u, long now) {
  if (u == null || @PKG@.AbilStore.MOMS.isEmpty()) return 0;
  Object o = @PKG@.AbilStore.MOMS.get(u);
  if (!(o instanceof long[])) return 0;
  long[] x = momX(u);
  long fl = x == null ? 0L : x[6];
  int n = @PKG@.AbilMath.live((long[]) o, now, momDecay(fl));
  int mx = momMax(fl);
  return n > mx ? mx : n;
}''')
late25(r'''
public static int momTier(int n) {
  if ((double) n >= @PKG@.AbilNum.MO_UNSTOPPABLE) return 2;
  if ((double) n >= @PKG@.AbilNum.MO_ROLLING) return 1;
  return 0;
}''')
# add n stacks now (the oldest / expired entries are reused); never past the max; returns the live count
late25(r'''
public static int momAdd(java.util.UUID u, int n, long now) {
  if (u == null || n <= 0) return momN(u, now);
  long[] r = momRing(u);
  long[] x = momX(u);
  int mx = momMax(x[6]);
  long dec = momDecay(x[6]);
  synchronized (r) { momAdd0(r, n, now, dec, mx); }
  MOMGAIN = MOMGAIN + (long) n;
  return momN(u, now);
}''')
late25(r'''
public static void momAdd0(long[] r, int n, long now, long dec, int mx) {
  for (int k = 0; k < n; k++) {
    int live = @PKG@.AbilMath.live(r, now, dec);
    int o = 0;
    if (live >= mx) {   // full: refresh the oldest live stack
      long best = Long.MAX_VALUE;
      for (int i = 0; i < r.length; i++) if (r[i] > 0L && now - r[i] < dec && r[i] < best) { best = r[i]; o = i; }
    } else {
      for (int i = 0; i < r.length; i++) if (r[i] <= 0L || now - r[i] >= dec) { o = i; break; }
    }
    r[o] = now;
  }
}''')
# lose n stacks (n < 0 = all): the oldest live ones go first; Second Wind (T4) keeps windKeep once per windEvery s when all would go
late25(r'''
public static int momLose(java.util.UUID u, int n, long now, String why) {
  if (u == null || @PKG@.AbilStore.MOMS.isEmpty()) return 0;
  Object o = @PKG@.AbilStore.MOMS.get(u);
  if (!(o instanceof long[])) return 0;
  long[] r = (long[]) o;
  long[] x = momX(u);
  long dec = momDecay(x[6]);
  int live = momN(u, now);
  if (live <= 0) return 0;
  int drop = n < 0 || n > live ? live : n;
  int keep = live - drop;
  if (keep == 0 && (x[6] & 1L) != 0L && now - x[4] >= ms(@PKG@.AbilNum.MO_WINDEVERY)) {
    keep = (int) Math.min((double) live, @PKG@.AbilNum.MO_WINDKEEP);
    x[4] = now;
    @PR@ pr = prOf(u);
    if (pr != null && keep > 0) say(pr, "Second Wind: you keep " + keep + " Momentum.");
  }
  synchronized (r) {
    for (int i = 0; i < r.length; i++) r[i] = 0L;
    for (int i = 0; i < keep && i < r.length; i++) r[i] = now;
  }
  MOMLOST = MOMLOST + (long) (live - keep);
  LAST_SB = "momentum lost " + (live - keep) + " (" + why + ")";
  return live - keep;
}''')
# Shattering Arc: spend `spend` stacks, never below the floor `keep` (when you had at least that many); returns the stacks spent
late25(r'''
public static int momSpend(java.util.UUID u, int spend, int keep, long now) {
  int live = momN(u, now);
  if (live <= 0 || spend <= 0) return 0;
  int sp = spend > live ? live : spend;
  int left = live - sp;
  int floor = keep < live ? keep : live;
  if (left < floor) left = floor;
  long[] r = momRing(u);
  synchronized (r) {
    for (int i = 0; i < r.length; i++) r[i] = 0L;
    for (int i = 0; i < left && i < r.length; i++) r[i] = now;
  }
  return sp;
}''')
late25(r'''
public static String momText(java.util.UUID u) {
  if (u == null || @PKG@.AbilStore.MOMS.isEmpty() || !@PKG@.AbilStore.MOMS.containsKey(u)) return "";
  int n = momN(u, System.currentTimeMillis());
  int t = momTier(n);
  return "Momentum " + n + (t == 2 ? " (Unstoppable)" : (t == 1 ? " (Rolling)" : ""));
}''')
# the swing START (AbilRuneSys, the Primary InteractionChainStartEvent): started within the flow window after the last landed hit =
# the rhythm bonus for this swing ("timing matters")
late25(r'''
public static String momSwing(@ICSE@ e, @REF@ r, @CB@ buf, long now) {
  try {
    if (e == null || e.isCancelled() || r == null || !r.isValid()) return null;
    Object po = buf.getComponent(r, @PR@.getComponentType());
    if (!(po instanceof @PR@)) return null;
    java.util.UUID u = ((@PR@) po).getUuid();
    Object xo = u == null ? null : @PKG@.AbilStore.MOMX.get(u);
    if (!(xo instanceof long[])) return null;
    long[] x = (long[]) xo;
    if (x[0] > 0L && now >= x[0] && now - x[0] <= ms(@PKG@.AbilNum.MO_FLOW)) { x[1] = now; return "rhythm"; }
    x[1] = 0L;
    return "late";
  } catch (Throwable t) { return null; }
}''')
# every 0.25 s per Spellblade (AbilTick.track): the weapon in hand, stunned / rooted / frozen, the momentum push aura, Unstoppable
late25(r'''
public static String momTick(@REF@ r, @CAC@ acc, java.util.UUID u, long now) {
  if (u == null || r == null) return null;
  if (!SB_LIVE) {   // FIX 2 (critic): the probe is throttled to once a second per player (it ran every tick for everyone on a server without a Spellblade)
    Object po = @PKG@.AbilStore.SBP.get(u);
    long[] pn = null;
    if (po instanceof long[]) pn = (long[]) po;
    if (pn != null && now < pn[0]) return null;
    if (pn == null) { pn = new long[1]; @PKG@.AbilStore.SBP.put(u, pn); }
    pn[0] = now + 1000L;
    if (@PKG@.ClassStore.classIndex(u) != sbCi()) return null;
    SB_LIVE = true;
  }
  Object xo = @PKG@.AbilStore.MOMX.get(u);
  if (!(xo instanceof long[])) return null;
  long[] x = (long[]) xo;
  if (now < x[7]) return null;
  x[7] = now + 250L;
  int n = momN(u, now);
  if (n <= 0) return "none";
  long fl = sbFlags(u, now);   // first: Second Wind (T4) must be known when everything would be lost
  if (@PKG@.ClassStore.classIndex(u) != sbCi()) { momLose(u, -1, now, "class"); return "class"; }
  String item = hand(acc, r);
  if (item != null && !sbWeapon(u, item)) { momLose(u, -1, now, "weapon"); return "weapon"; }
  if (hasFx(acc, r, EF_STUN) || hasFx(acc, r, "Root") || hasFx(acc, r, EF_FREEZE)) { momLose(u, -1, now, "stunned"); return "stunned"; }
  int t = momTier(n);
  if (t >= 1) {   // the momentum push: allies near you move a little faster (an aura - only while inside)
    double rng = (fl & 4L) != 0L ? @PKG@.AbilNum.MO_PUSHRANGE3 : @PKG@.AbilNum.MO_PUSHRANGE;
    int pct = (int) Math.round(t == 2 ? @PKG@.AbilNum.MO_PUSHUNSTOPPABLE : @PKG@.AbilNum.MO_PUSHROLLING);
    double[] me = here(acc, r);
    if (me != null && pct > 0) {
      java.util.ArrayList us = new java.util.ArrayList();
      java.util.ArrayList rs = new java.util.ArrayList();
      pickAllies(r.getStore(), acc, u, me, rng, rng, us, rs);
      for (int i = 0; i < us.size(); i++) {
        java.util.UUID au = (java.util.UUID) us.get(i);
        if (au.equals(u)) continue;
        // FIX 2 (critic): keep an ally's running HIGHER speed (a Monk's flow, a haste) or a slow (a tree drawback) - the aura never flips it
        Object so = @PKG@.AbilStore.SPD.get(au);
        if (so instanceof long[] && ((long[]) so).length > 3 && ((long[]) so)[3] > now && (((long[]) so)[0] > (long) pct || ((long[]) so)[0] < 0L)) continue;
        speedKeep(acc, (@REF@) rs.get(i), au, pct, 1.5);
      }
    }
  }
  if (t == 2) { if (x[9] == 0L) x[9] = now; } else x[9] = 0L;
  return "n=" + n + " tier=" + t;
}''')

# ---------------------------------------------------------------- ELEMENTS: the sword's element, the attunement, Imbue, the statuses
late25(r'''
public static int elemOfItem(String item) {
  if (item == null || !item.startsWith("Weapon_Elemental_")) return -1;
  String s = item.substring(17);
  if (s.startsWith("Flame")) return 0;
  if (s.startsWith("Ice")) return 1;
  if (s.startsWith("Gravity")) return 2;
  if (s.startsWith("Poison")) return 5;
  return -1;
}''')
late25(r'''
public static int elemIdx(String s) {
  if (s == null) return -1;
  String t = s.trim();
  for (int i = 0; i < ELN.length; i++) if (ELN[i].equalsIgnoreCase(t)) return i;
  if ("Thunder".equalsIgnoreCase(t)) return 3;
  if ("Air".equalsIgnoreCase(t)) return 4;
  return -1;
}''')
late25(r'''
public static int attOf(String k, int which) {
  if (k == null) return which == 1 ? 0 : -1;
  java.util.Properties p = @PKG@.AbilStore.load(k);
  int e = elemIdx(p == null ? null : p.getProperty(which == 1 ? "att1" : "att2"));
  if (e < 0 || e > 4) return which == 1 ? 0 : -1;   // the five elements (Poison comes only with the Poison sword); default Fire
  return e;
}''')
late25(r'''
public static String attText(String k, String csv) {
  int a = attOf(k, 1);
  boolean twin = @PKG@.AbilModDefs.csvHas(csv, "PA1");
  int b = twin ? attOf(k, 2) : -1;
  return ELN[a] + (twin ? "+" + (b < 0 ? "-" : ELN[b]) : "");
}''')
# doAction "attune": a = "next" (cycle) or an element name, b = "1" / "2" (2 = Twin Attunement's second element)
late25(r'''
public static String attune(java.util.UUID u, String a, String b, String csv) {
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci != sbCi()) return "-Only a Spellblade attunes an element.";
  if (combatMs(u) > 0L) return "-Leave combat first - attunement changes only out of combat.";
  String k = @PKG@.ClassCfg.pkey(u);
  int which = "2".equals(b == null ? "" : b.trim()) ? 2 : 1;
  if (which == 2 && !@PKG@.AbilModDefs.csvHas(csv == null ? treeCsv(u) : csv, "PA1")) return "-A second element needs Twin Attunement (Tempest path, PA1).";
  int cur = attOf(k, which);
  int e = elemIdx(a);
  if (a == null || a.trim().length() == 0 || "next".equalsIgnoreCase(a.trim())) e = cur < 0 ? 0 : (cur + 1) % 5;
  if (e < 0 || e > 4) return "-Elements: Fire, Water, Earth, Lightning, Wind.";
  if (!@PKG@.AbilStore.set(k, new String[] { which == 1 ? "att1" : "att2" }, new String[] { ELN[e] })) return "-Your ability file could not be read - nothing changed (see the server log).";
  @PKG@.AbilStore.saveSoon(k);
  ATTUNES = ATTUNES + 1L;
  return "+Elemental Imbue: " + (which == 2 ? "second element " : "") + ELN[e] + " (" + ELS[e] + "). An Elemental sword in your hand uses its own element.";
}''')
late25(r'''
public static double[] imbueOf(java.util.UUID u, long now) {
  if (u == null || @PKG@.AbilStore.IMBUE.isEmpty()) return null;
  Object o = @PKG@.AbilStore.IMBUE.get(u);
  if (!(o instanceof double[]) || ((double[]) o)[0] <= (double) now) return null;
  return (double[]) o;
}''')
late25(r'''
public static String imbueCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, String item, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  int e = elemOfItem(item);
  boolean twin = nd(c, "Spellblade", "PA1");
  if (e < 0) {
    e = attOf(k, 1);
    int e2 = twin ? attOf(k, 2) : -1;
    if (twin && e2 >= 0 && e2 != e) {   // Twin Attunement: the two elements take turns, one per cast
      Object no = @PKG@.AbilStore.IMBN.get(k);
      long cnt = no instanceof Long ? ((Long) no).longValue() : 0L;
      @PKG@.AbilStore.IMBN.put(k, Long.valueOf(cnt + 1L));
      if (cnt % 2L == 1L) e = e2;
    }
  }
  double secs = cxds(sh == 3 ? @PKG@.AbilNum.EI_DEEPTIME : @PKG@.AbilNum.EI_TIME);
  double pct = @PKG@.AbilNum.EI_PCT * (c == null ? 1.0 : c.main);
  double stat = 1.0 + (sh == 3 ? @PKG@.AbilNum.EI_DEEPSTATUS / 100.0 : 0.0);
  int chain = c == null ? 0 : c.eff(@PKG@.AbilModDefs.CHAIN);
  @PKG@.AbilStore.IMBUE.put(u, new double[] { (double) (now + ms(secs)), (double) e, pct, stat, (double) chain, 0.0 });
  IMBUED = IMBUED + 1L;
  if (sh == 3) effect(st, ref, "Root", @PKG@.AbilNum.EI_DEEPSTILL);
  String ex = "";
  if (sh == 1) {   // Charging Imbue: a crescent of the element ahead
    double[] me = here(st, ref);
    double[] f = flat(st, ref);
    if (me != null) {
      @PKG@.AbilJob j = sbJob(u, k, @PKG@.AbilDefs.IMBUE, 1, me, f, @PKG@.AbilNum.EI_CRESCENT + cxr(), 0.0, h * @PKG@.AbilNum.EI_CRESCENTPOWER * cxm(), now);
      j.what = "ImbueCrescent";
      aw.add(j);
      ex = " crescent";
    }
  }
  if (sh == 2) { aw.add(landJob(u, k, @PKG@.AbilDefs.IMBUE, h, now)); ex = " land"; }
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.IMBUE, sh) + ": " + ELN[e] + " for " + @PKG@.AbilMath.fmt(secs) + " s - your hits deal +" + @PKG@.AbilMath.fmt(pct) + " % " + ELN[e] + " damage and " + ELS[e] + ".");
  LAST_SB = "imbue " + ELN[e] + " pct=" + @PKG@.AbilMath.fmt(pct) + " secs=" + @PKG@.AbilMath.fmt(secs);
  return " elem=" + ELN[e] + " pct=" + @PKG@.AbilMath.fmt(pct) + " secs=" + @PKG@.AbilMath.fmt(secs) + (chain > 0 ? " chain=" + chain : "") + ex;
}''')
# the status strength: Momentum (+1 % a stack), the stand-still Deep Imbue, statuses last 50 % longer while Unstoppable
late25(r'''
public static double[] statMul(java.util.UUID u, double[] imb, long now) {
  int n = momN(u, now);
  double str = 1.0 + (double) n * @PKG@.AbilNum.MO_ELEMPERSTACK / 100.0;
  double dur = (imb == null ? 1.0 : imb[3]) * (momTier(n) == 2 ? 1.0 + @PKG@.AbilNum.MO_STATUSUNSTOP / 100.0 : 1.0);
  return new double[] { str, dur };
}''')
# a damage-over-time stack (Burn / Poison): job kind 26 on the mob; up to `stacks` live jobs per mob and kind (a new one refreshes the oldest)
late25(r'''
public static int dotOn(@CB@ cb, @REF@ t, java.util.UUID u, String what, double perSec, double secs, int stacks, long now) {
  if (t == null || u == null || !(perSec > 0.0) || !(secs > 0.0)) return 0;
  Object o = @PKG@.AbilStore.DOTS.get(t);
  java.util.ArrayList l = o instanceof java.util.ArrayList ? (java.util.ArrayList) o : new java.util.ArrayList();
  @PKG@.AbilStore.DOTS.put(t, l);
  int ticks = (int) Math.round(secs);
  if (ticks < 1) ticks = 1;
  int live = 0;
  @PKG@.AbilJob old = null;
  synchronized (l) {
    java.util.Iterator it = l.iterator();
    while (it.hasNext()) {
      @PKG@.AbilJob j = (@PKG@.AbilJob) it.next();
      if (j.left <= 0) { it.remove(); continue; }
      if (!what.equals(j.what)) continue;
      live++;
      if (old == null || j.left < old.left) old = j;
    }
    if (live >= (stacks < 1 ? 1 : stacks) && old != null) {
      old.left = ticks;
      if (perSec > old.amount) old.amount = perSec;
      return 0;
    }
    @PKG@.AbilJob j = new @PKG@.AbilJob(26, now + 1000L, u, what, 0.0, 0.0, 0.0, 0.0, perSec);
    j.pkey = @PKG@.ClassCfg.pkey(u);
    j.ai = @PKG@.AbilDefs.IMBUE;
    j.tref = t;
    j.left = ticks;
    j.every = 1000L;
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(cb.getExternalData()));
    aw.add(j);
    l.add(j);
  }
  return 1;
}''')
late25(r'''
public static boolean dotTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (cr == null || !cr.isValid() || !(j.tref instanceof @REF@)) { j.left = 0; return false; }
  @REF@ t = (@REF@) j.tref;
  if (!enemy(cb, t, cr)) { j.left = 0; return false; }
  hit(cb, t, cr, j.caster, j.amount, j.what);
  @VEC@ q = pos(cb, t);
  if (q != null) particle("ElemPoison".equals(j.what) ? FX_TOXIN : FX_FIRE, q.x, q.y + 1.0, q.z, cb);
  j.left = j.left - 1;
  j.at = now + 1000L;
  return j.left > 0;
}''')
# ONE STATUS on one mob (research/cloud/Element-System-Spec.md 5): hit = the damage of the hit that applied it; str / dur = statMul;
# heavy = an ability hit (Gust knocks up). Bosses: stuns / slows halved, Gust immune.
late25(r'''
public static String statusOn(@CB@ cb, @REF@ t, @REF@ cr, java.util.UUID u, int e, double hv, double str, double dur, long now, boolean heavy) {
  if (t == null || cr == null || e < 0 || e > 5 || !enemy(cb, t, cr)) return null;
  boolean boss = bossT(cb, t);
  double cc = boss ? @PKG@.AbilNum.EL_BOSSCC / 100.0 : 1.0;
  @VEC@ q = pos(cb, t);
  String out = ELS[e];
  if (e == 0) {
    dotOn(cb, t, u, "ElemBurn", hv * @PKG@.AbilNum.EL_BURNPCT / 100.0 * str, @PKG@.AbilNum.EL_BURNTIME * dur, (int) Math.round(@PKG@.AbilNum.EL_BURNSTACKS), now);
    if (q != null) particle(FX_FIRE, q.x, q.y + 1.0, q.z, cb);
  } else if (e == 1) {
    int sl = (int) Math.round(@PKG@.AbilNum.EL_CHILLSLOW * cc);
    if (sl > 0) effect(cb, t, spdId(-sl), @PKG@.AbilNum.EL_CHILLTIME * dur);
    Object co = @PKG@.AbilStore.CHILLS.get(t);
    long[] ch = co instanceof long[] ? (long[]) co : new long[12];
    int need = (int) Math.round(@PKG@.AbilNum.EL_FREEZEAT);
    if (need < 1) need = 1;
    if (need > ch.length) need = ch.length;
    int o = 0;
    for (int i = 1; i < ch.length; i++) if (ch[i] < ch[o]) o = i;
    ch[o] = now;
    @PKG@.AbilStore.CHILLS.put(t, ch);
    int recent = 0;
    for (int i = 0; i < ch.length; i++) if (ch[i] > 0L && now - ch[i] <= ms(@PKG@.AbilNum.EL_FREEZEWINDOW)) recent++;
    if (recent >= need) {
      for (int i = 0; i < ch.length; i++) ch[i] = 0L;
      int fz = freezeOne(cb, t, u, @PKG@.AbilNum.EL_FREEZETIME * dur, 1.0, 0.0, now);
      out = fz > 0 ? "Freeze" : "Chill";
    }
    if (q != null) particle(FX_FROST_HIT, q.x, q.y + 1.0, q.z, cb);
  } else if (e == 2) {
    Object so = @PKG@.AbilStore.STAGD.get(t);
    double[] sg = so instanceof double[] ? (double[]) so : new double[3];
    sg[2] = sg[2] + 1.0;
    int every = (int) Math.round(@PKG@.AbilNum.EL_STAGGEREVERY);
    if (every < 1) every = 1;
    if (((int) sg[2]) % every == 0) {
      stunMob(cb, t, u, @PKG@.AbilNum.EL_STAGGERTIME * cc * dur, now);
      sg[0] = (double) (now + ms(@PKG@.AbilNum.EL_STAGGERDEFTIME * dur));
      sg[1] = @PKG@.AbilNum.EL_STAGGERDEF * str;
      out = "Stagger!";
    }
    @PKG@.AbilStore.STAGD.put(t, sg);
    if (q != null) particle(FX_SPLIT, q.x, q.y + 0.1, q.z, cb);
  } else if (e == 3) {
    double until = (double) (now + ms(@PKG@.AbilNum.EL_SHOCKTIME * dur));
    @PKG@.AbilStore.SHOCKD.put(t, new double[] { until, @PKG@.AbilNum.EL_SHOCKVULN * str });
    if (q != null) {
      @REF@ x = nearest(cb, cr, q.x, q.y, q.z, @PKG@.AbilNum.EL_SHOCKRANGE, t);
      if (x != null) {
        hit(cb, x, cr, u, hv * @PKG@.AbilNum.EL_SHOCKPCT / 100.0 * str, "ElemShock");
        @PKG@.AbilStore.SHOCKD.put(x, new double[] { until, @PKG@.AbilNum.EL_SHOCKVULN * str });
        @VEC@ w = pos(cb, x);
        if (w != null) particle(FX_STAR, w.x, w.y + 1.0, w.z, cb);
        out = "Shock+jump";
      }
      particle(FX_STAR, q.x, q.y + 1.0, q.z, cb);
    }
  } else if (e == 4) {
    if (boss) out = "Gust (boss immune)";
    else {
      @VEC@ p = pos(cb, cr);
      if (p != null && q != null) {
        double dx = q.x - p.x;
        double dz = q.z - p.z;
        double d = Math.sqrt(dx * dx + dz * dz);
        double f = @PKG@.AbilNum.EL_GUSTKB * @PKG@.AbilCfg.PUSH_PER_BLOCK;
        double up = heavy ? @PKG@.AbilNum.EL_GUSTUP * @PKG@.AbilCfg.PUSH_PER_BLOCK * 0.5 : 0.3;
        if (d > 0.05) push(cb, t, dx / d * f, up, dz / d * f);
        else push(cb, t, 0.0, up, 0.0);
      }
      if (q != null) particle(FX_SMOKE, q.x, q.y + 1.0, q.z, cb);
    }
  } else {
    dotOn(cb, t, u, "ElemPoison", hv * @PKG@.AbilNum.EL_POISONPCT / 100.0 * str, @PKG@.AbilNum.EL_POISONTIME * dur, 1, now);
    if (q != null) particle(FX_TOXIN, q.x, q.y + 1.0, q.z, cb);
  }
  STATUSES = STATUSES + 1L;
  return out;
}''')
# the Imbue status of one hit (+ its Chain: the status jumps to `chain` more enemies within chainRange - no damage)
late25(r'''
public static String imbueStatus(@CB@ cb, @REF@ t, @REF@ cr, java.util.UUID u, double hv, boolean heavy, long now) {
  double[] imb = imbueOf(u, now);
  if (imb == null) return null;
  double[] sm = statMul(u, imb, now);
  int e = (int) imb[1];
  String r = statusOn(cb, t, cr, u, e, hv, sm[0], sm[1], now, heavy);
  int ch = (int) imb[4];
  if (ch > 0) {
    @VEC@ q = pos(cb, t);
    java.util.HashSet done = new java.util.HashSet();
    done.add(t);
    for (int i = 0; i < ch && q != null; i++) {
      @REF@ best = null;
      double bd = 1.0E18;
      java.util.List l = near(cb, q.x, q.y, q.z, @PKG@.AbilNum.EI_CHAINRANGE);
      for (int m = 0; m < l.size(); m++) {
        Object o = l.get(m);
        if (!(o instanceof @REF@) || done.contains(o) || !enemy(cb, (@REF@) o, cr)) continue;
        @VEC@ w = pos(cb, (@REF@) o);
        if (w == null) continue;
        double dd = (w.x - q.x) * (w.x - q.x) + (w.y - q.y) * (w.y - q.y) + (w.z - q.z) * (w.z - q.z);
        if (dd > @PKG@.AbilNum.EI_CHAINRANGE * @PKG@.AbilNum.EI_CHAINRANGE) continue;
        if (dd < bd) { bd = dd; best = (@REF@) o; }
      }
      if (best == null) break;
      done.add(best);
      statusOn(cb, best, cr, u, e, hv, sm[0], sm[1], now, heavy);
    }
    if (done.size() > 1) r = r + " chain+" + (done.size() - 1);
  }
  return r;
}''')

# ---------------------------------------------------------------- BREACH, SUNDER and the other debuffs on a mob (the outgoing multiplier)
late25(r'''
public static double breachOn(@CAC@ acc, @REF@ t, java.util.UUID u, double pct, double secs, long now, @PKG@.AbilCtx c) {
  if (t == null || u == null || !(pct > 0.0) || !(secs > 0.0)) return 0.0;
  double p = pct;
  if (nd(c, "Spellblade", "PB1")) p = p + (bossT(acc, t) ? 5.0 : -3.0);   // Deep Breach: bosses +5, others -3
  if (p < 0.0) p = 0.0;
  if (p > 60.0) p = 60.0;
  double until = (double) (now + ms(secs));
  double fl = nd(c, "Spellblade", "PB4") ? 1.0 : 0.0;
  Object o = @PKG@.AbilStore.BREACH.get(t);
  if (o instanceof double[] && ((double[]) o)[0] > (double) now) {   // the stronger Breach stays, the later end wins
    double[] b = (double[]) o;
    if (b[1] > p) p = b[1];
    if (b[0] > until) until = b[0];
    if (b.length > 4 && b[4] > fl) fl = b[4];
  }
  @PKG@.AbilStore.BREACH.put(t, new double[] { until, p, (double) u.getMostSignificantBits(), (double) u.getLeastSignificantBits(), fl });
  BREACHED = BREACHED + 1L;
  @VEC@ q = pos(acc, t);
  if (q != null) particle(FX_GOD, q.x, q.y + 2.2, q.z, acc);
  return p;
}''')
late25(r'''
public static double breachPct(@REF@ t, long now) {
  if (t == null || @PKG@.AbilStore.BREACH.isEmpty()) return 0.0;
  Object o = @PKG@.AbilStore.BREACH.get(t);
  if (!(o instanceof double[]) || ((double[]) o)[0] <= (double) now) return 0.0;
  return ((double[]) o)[1];
}''')
late25(r'''
public static double sunderOn(@CAC@ acc, @REF@ t, java.util.UUID u, double weaken, double def, double secs, long now, @PKG@.AbilCtx c) {
  if (t == null || u == null || !(secs > 0.0)) return 0.0;
  double w = weaken > 40.0 ? 40.0 : weaken;
  double fl = nd(c, "Spellblade", "PB4") ? 1.0 : 0.0;
  @PKG@.AbilStore.SUNDER.put(t, new double[] { (double) (now + ms(secs)), w, def, (double) u.getMostSignificantBits(), (double) u.getLeastSignificantBits(), fl });
  SUNDERED = SUNDERED + 1L;
  @VEC@ q = pos(acc, t);
  if (q != null) particle(FX_GOD, q.x, q.y + 1.5, q.z, acc);
  return w;
}''')
# the TARGET side of the outgoing multiplier (Abil.outMult): Sunder's defence cut (Armour Break / Armour Split), Stagger's defence cut,
# Shock, Marked for Death (Breach + Sunder from a Spellblade with PB4)
late25(r'''
public static double outMult3(@CAC@ acc, @REF@ t, java.util.UUID cu, long now) {
  double m = 1.0;
  double tn = (double) now;
  boolean sund = false;
  boolean both = false;
  Object so = @PKG@.AbilStore.SUNDER.get(t);
  if (so instanceof double[] && ((double[]) so)[0] > tn) {
    double[] s = (double[]) so;
    sund = true;
    if (s[2] > 0.0) m = m * (1.0 + s[2] / 100.0);
    if (s.length > 5 && s[5] > 0.5) both = true;
  }
  Object go = @PKG@.AbilStore.STAGD.get(t);
  if (go instanceof double[] && ((double[]) go)[0] > tn && ((double[]) go)[1] > 0.0) m = m * (1.0 + ((double[]) go)[1] / 100.0);
  Object ho = @PKG@.AbilStore.SHOCKD.get(t);
  if (ho instanceof double[] && ((double[]) ho)[0] > tn) m = m * (1.0 + ((double[]) ho)[1] / 100.0);
  if (sund) {
    Object bo = @PKG@.AbilStore.BREACH.get(t);
    if (bo instanceof double[] && ((double[]) bo)[0] > tn && (both || (((double[]) bo).length > 4 && ((double[]) bo)[4] > 0.5))) m = m * (1.0 + @PKG@.AbilNum.EL_BOTHBONUS / 100.0);
  }
  return m;
}''')

# ---------------------------------------------------------------- THE ARCS (job kind 25): every Spellblade swing-shaped ability runs on the next tick
late25(r'''
public static @PKG@.AbilJob sbJob(java.util.UUID u, String k, int ai, int sh, double[] at, double[] f, double r, double half, double amt, long when) {
  @PKG@.AbilJob j = new @PKG@.AbilJob(25, when, u, @PKG@.AbilDefs.IDS[ai], at[0], at[1], at[2], r, amt);
  j.pkey = k;
  j.ai = ai;
  j.sh = sh;
  j.width = half;
  j.dx = f == null ? 0.0 : f[0];
  j.dz = f == null ? 1.0 : f[1];
  return j;
}''')
# the enemies in a flat cone (half = the half-angle in degrees; 180 or more = a full circle) within r of (x, y, z)
late25(r'''
public static java.util.ArrayList sbCone(@CAC@ acc, @REF@ cr, double x, double y, double z, double dx, double dz, double r, double half) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.List l = near(acc, x, y, z, r + 0.5);
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(acc, t, cr)) continue;
    @VEC@ q = pos(acc, t);
    if (q == null) continue;
    double vx = q.x - x;
    double vz = q.z - z;
    double dd = Math.sqrt(vx * vx + vz * vz);
    if (dd > r + 0.5 || Math.abs(q.y - y) > 3.5) continue;
    if (half < 180.0 && dd > 0.6) {
      double cs = (vx * dx + vz * dz) / dd;
      if (cs > 1.0) cs = 1.0;
      if (cs < -1.0) cs = -1.0;
      if (Math.toDegrees(Math.acos(cs)) > half) continue;
    }
    out.add(t);
  }
  return out;
}''')
# the enemies on a straight line (the Charging Imbue crescent): from (x, z) along (dx, dz) for len blocks, w blocks wide
late25(r'''
public static java.util.ArrayList sbLine(@CAC@ acc, @REF@ cr, double x, double y, double z, double dx, double dz, double len, double w) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.List l = near(acc, x + dx * len * 0.5, y, z + dz * len * 0.5, len * 0.5 + w + 1.0);
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(acc, t, cr)) continue;
    @VEC@ q = pos(acc, t);
    if (q == null) continue;
    double vx = q.x - x;
    double vz = q.z - z;
    double along = vx * dx + vz * dz;
    double side = Math.abs(vx * dz - vz * dx);
    if (along < -0.5 || along > len + 0.5 || side > w / 2.0 + 0.5 || Math.abs(q.y - y) > 3.5) continue;
    out.add(t);
  }
  return out;
}''')
late25(r'''
public static double breachPctOf(@PKG@.AbilCtx c, double base, int stacks, double perStack, double stackCap, double cap) {
  double add = (double) stacks * perStack;
  if (add > stackCap) add = stackCap;
  double p = (base + add) * powMul(c) + @PKG@.AbilNum.AB_PERLEVEL * (double) (c == null || c.lvl < 1 ? 0 : c.lvl - 1);
  return p > cap ? cap : p;
}''')
# ARCANE BREACH (A1): the arc + Breach; Marked Ground = no damage; the landing circle = Breach from Above
late25(r'''
public static String breachCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, long now) {
  if (sh == 2) { aw.add(landJob(u, k, @PKG@.AbilDefs.BREACH, h, now)); return " land"; }
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double[] me = here(st, ref);
  double[] f = flat(st, ref);
  if (me == null) return " nopos";
  if (sh == 1 && f != null) push(st, ref, f[0] * @PKG@.AbilNum.AB_STEP * @PKG@.AbilCfg.PUSH_PER_BLOCK, 0.0, f[1] * @PKG@.AbilNum.AB_STEP * @PKG@.AbilCfg.PUSH_PER_BLOCK);
  int stk = momN(u, now);
  double r = (sh == 3 ? @PKG@.AbilNum.AB_MARKRADIUS : @PKG@.AbilNum.AB_RANGE) + cxr();
  double half = sh == 3 ? 180.0 : @PKG@.AbilNum.AB_ANGLE;
  double amt = sh == 3 ? 0.0 : h * @PKG@.AbilNum.AB_POWER * cxm();
  @PKG@.AbilJob j = sbJob(u, k, @PKG@.AbilDefs.BREACH, sh, me, f, r, half, amt, now);
  j.freeze = breachPctOf(c, sh == 3 ? @PKG@.AbilNum.AB_MARKBREACH : @PKG@.AbilNum.AB_BREACH, stk, @PKG@.AbilNum.AB_PERSTACK, @PKG@.AbilNum.AB_STACKCAP, @PKG@.AbilNum.AB_CAP);
  j.secs = durCap(sh == 1 ? @PKG@.AbilNum.AB_SPRINTTIME : @PKG@.AbilNum.AB_TIME, @PKG@.AbilNum.AB_DURMAX);
  j.len = (double) stk;
  aw.add(j);
  return " r=" + @PKG@.AbilMath.fmt(r) + " arc=" + @PKG@.AbilMath.fmt(half * 2.0) + " hit=" + @PKG@.AbilMath.fmt(amt) + " breach=" + @PKG@.AbilMath.fmt(j.freeze) + " secs=" + @PKG@.AbilMath.fmt(j.secs) + " stacks=" + stk;
}''')
late25(r'''
public static int breachRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_SB = "breach gone"; return -1; }
  @PKG@.AbilCtx c = j.cx;
  double x0 = j.x;
  double y0 = j.y;
  double z0 = j.z;
  if (j.sh != 2) { @VEC@ p = pos(cb, cr); if (p != null) { x0 = p.x; y0 = p.y; z0 = p.z; } }
  java.util.ArrayList hs = sbCone(cb, cr, x0, y0, z0, j.dx, j.dz, j.r, j.width);
  int n = 0;
  boolean imb = imbueOf(j.caster, now) != null;
  for (int i = 0; i < hs.size(); i++) {
    @REF@ t = (@REF@) hs.get(i);
    if (j.amount > 0.0 && hit(cb, t, cr, j.caster, j.amount, "ArcaneBreach")) n++;
    breachOn(cb, t, j.caster, j.freeze, j.secs, now, c);
    if (j.sh == 2) push(cb, t, 0.0, @PKG@.AbilNum.AB_AIRUP * @PKG@.AbilCfg.PUSH_PER_BLOCK * 0.5, 0.0);
    if (imb && j.amount > 0.0) imbueStatus(cb, t, cr, j.caster, j.amount, true, now);
  }
  int extra = 0;
  int ch = c == null ? 0 : c.eff(@PKG@.AbilModDefs.CHAIN);
  if (ch > 0) {   // Chain: the Breach jumps to the nearest enemies the arc missed
    java.util.HashSet skip = new java.util.HashSet(hs);
    for (int i = 0; i < ch; i++) {
      @REF@ best = null;
      double bd = 1.0E18;
      java.util.List l = near(cb, x0, y0, z0, j.r + @PKG@.AbilNum.AB_CHAINRANGE);
      for (int m = 0; m < l.size(); m++) {
        Object o = l.get(m);
        if (!(o instanceof @REF@) || skip.contains(o) || !enemy(cb, (@REF@) o, cr)) continue;
        @VEC@ w = pos(cb, (@REF@) o);
        if (w == null) continue;
        double dd = (w.x - x0) * (w.x - x0) + (w.z - z0) * (w.z - z0);
        if (dd < bd) { bd = dd; best = (@REF@) o; }
      }
      if (best == null) break;
      skip.add(best);
      breachOn(cb, best, j.caster, j.freeze, j.secs, now, c);
      extra++;
    }
  }
  if (imb && nd(c, "Spellblade", "PA2")) burnPatches(cb, cr, j, hs, now);   // Burning Rift: the imbued arc leaves element patches
  boolean any = hs.size() > 0 || extra > 0;
  if (any && (c == null || !c.echo)) { momAdd(j.caster, (int) Math.round(@PKG@.AbilNum.AB_GAIN), now); used(j.caster, j.pkey, @PKG@.AbilDefs.BREACH, c); }
  particle(j.sh == 2 || j.sh == 3 ? FX_SHOCK : FX_KICK, x0 + j.dx * 1.5, y0 + 0.2, z0 + j.dz * 1.5, cb);
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.BREACH, j.sh) + ": " + (hs.size() + extra) + ((hs.size() + extra) == 1 ? " enemy" : " enemies") + " Breached - +" + @PKG@.AbilMath.fmt(j.freeze) + " % damage taken for " + @PKG@.AbilMath.fmt(j.secs) + " s" + (extra > 0 ? " (" + extra + " by Chain)." : "."));
  LAST_SB = "breach " + j.sh + " hit=" + n + " breached=" + (hs.size() + extra) + " pct=" + @PKG@.AbilMath.fmt(j.freeze);
  return hs.size() + extra;
}''')
# Burning Rift (Tempest PA2): a 2 s element patch under up to 3 enemies the imbued arc hit
late25(r'''
public static int burnPatches(@CB@ cb, @REF@ cr, @PKG@.AbilJob j, java.util.ArrayList hs, long now) {
  double[] imb = imbueOf(j.caster, now);
  if (imb == null) return 0;
  double[] sm = statMul(j.caster, imb, now);
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(cb.getExternalData()));
  int n = 0;
  for (int i = 0; i < hs.size() && n < 3; i++) {
    @VEC@ q = pos(cb, (@REF@) hs.get(i));
    if (q == null) continue;
    @PKG@.AbilZone z = riftZone(j.caster, j.pkey, aw, new double[] { q.x, q.y, q.z }, null, 1, @PKG@.AbilNum.RC_PATCH, 0.0, 0.0, @PKG@.AbilNum.RC_PATCHTIME, sm[0], sm[1], (int) imb[1], j.amount, now);   // fix round: the status strength + duration (riftPlace's)
    if (z != null) { z.echoed = true; z.name = "Burning Rift"; n++; }
  }
  return n;
}''')
# SUNDER (A2-alt): one target, a heavy strike; Armour Break winds up 1 s (you stand rooted)
late25(r'''
public static String sunderCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, @REF@ t, long now) {
  if (sh == 2) { aw.add(landJob(u, k, @PKG@.AbilDefs.SUNDER, h, now)); return " land"; }
  if (t == null) return " notarget";
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double[] me = here(st, ref);
  if (me == null) return " nopos";
  if (sh == 1) {   // Lunging Sunder: a step in towards the target
    @VEC@ p = pos(st, ref);
    @VEC@ q = pos(st, t);
    if (p != null && q != null) {
      double dx = q.x - p.x;
      double dz = q.z - p.z;
      double dd = Math.sqrt(dx * dx + dz * dz);
      double sp = @PKG@.AbilNum.SU_STEP * @PKG@.AbilCfg.PUSH_PER_BLOCK;
      if (dd > 1.5) push(st, ref, dx / dd * sp, 0.0, dz / dd * sp);
    }
  }
  double pw = sh == 1 ? @PKG@.AbilNum.SU_LUNGEPOWER : @PKG@.AbilNum.SU_POWER;
  @PKG@.AbilJob j = sbJob(u, k, @PKG@.AbilDefs.SUNDER, sh, me, null, 0.0, 0.0, h * pw * cxm(), now + (sh == 3 ? ms(@PKG@.AbilNum.SU_WIND) : 0L));
  j.tref = t;
  sunderNums(j, c, sh);
  aw.add(j);
  if (sh == 3) {
    effect(st, ref, "Root", @PKG@.AbilNum.SU_WIND);
    if (pr != null) say(pr, "Armour Break: winding up...");
  }
  return " hit=" + @PKG@.AbilMath.fmt(j.amount) + " weaken=" + @PKG@.AbilMath.fmt(j.freeze) + " def=" + @PKG@.AbilMath.fmt(j.chill) + " secs=" + @PKG@.AbilMath.fmt(j.secs) + (sh == 3 ? " wind" : "");
}''')
late25(r'''
public static void sunderNums(@PKG@.AbilJob j, @PKG@.AbilCtx c, int sh) {
  j.secs = durCap(sh == 3 ? @PKG@.AbilNum.SU_BREAKTIME : @PKG@.AbilNum.SU_TIME, @PKG@.AbilNum.SU_DURMAX);
  j.freeze = @PKG@.AbilNum.SU_WEAKEN * powMul(c);
  j.chill = (sh == 3 ? @PKG@.AbilNum.SU_BREAKDEF : 0.0) + (nd(c, "Spellblade", "PB2") ? @PKG@.AbilNum.SU_SPLITDEF : 0.0);
  j.stun = sh == 2 ? @PKG@.AbilNum.SU_AIRSTAGGER : 0.0;
}''')
late25(r'''
public static int sunderRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_SB = "sunder gone"; return -1; }
  if (!(j.tref instanceof @REF@)) return -1;
  @REF@ t = (@REF@) j.tref;
  @PR@ pr = prOf(j.caster);
  if (!enemy(cb, t, cr)) { if (pr != null) send(pr, "Sunder: the target is gone.", "#ffc800"); LAST_SB = "sunder target gone"; return 0; }
  @PKG@.AbilCtx c = j.cx;
  boolean echo = c != null && c.echo;
  int n = 0;
  if (hit(cb, t, cr, j.caster, j.amount, "Sunder")) n++;
  if (!echo) sunderOn(cb, t, j.caster, j.freeze, j.chill, j.secs, now, c);
  if (j.stun > 0.0 && !bossT(cb, t)) stunMob(cb, t, j.caster, j.stun, now);
  if (imbueOf(j.caster, now) != null) imbueStatus(cb, t, cr, j.caster, j.amount, true, now);
  @VEC@ q = pos(cb, t);
  if (q != null) particle(FX_GOD, q.x, q.y + 1.0, q.z, cb);
  int ch = c == null || echo ? 0 : c.eff(@PKG@.AbilModDefs.CHAIN);
  if (ch > 0 && q != null) {   // Chain: a second enemy within chainRange at chainPct %
    @REF@ x = nearest(cb, cr, q.x, q.y, q.z, @PKG@.AbilNum.SU_CHAINRANGE, t);
    if (x != null) {
      if (hit(cb, x, cr, j.caster, j.amount * @PKG@.AbilNum.SU_CHAINPCT / 100.0, "Sunder")) n++;
      sunderOn(cb, x, j.caster, j.freeze, j.chill, j.secs, now, c);
    }
  }
  if (!echo && c != null && c.echoPct > 0.0) {   // Echo: a weaker strike 1 s later (refreshes nothing)
    @PKG@.AbilJob ej = new @PKG@.AbilJob(10, now + ms(@PKG@.AbilCfg.ECHO_DELAY), j.caster, "Sunder", j.x, j.y, j.z, 0.0, j.amount * c.echoPct);
    ej.pkey = j.pkey;
    ej.ai = @PKG@.AbilDefs.SUNDER;
    ej.sh = j.sh;
    ej.tref = t;
    ej.cx = c.echoOf(c.echoPct);
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
    if (aw != null) aw.add(ej);
  }
  if (n > 0 && !echo) { momAdd(j.caster, (int) Math.round(@PKG@.AbilNum.SU_GAIN), now); used(j.caster, j.pkey, @PKG@.AbilDefs.SUNDER, c); }
  if (pr != null) say(pr, (echo ? "Echo: " : "") + @PKG@.AbilDefs.sname(@PKG@.AbilDefs.SUNDER, j.sh) + (echo ? " strikes again." : ": Sundered for " + @PKG@.AbilMath.fmt(j.secs) + " s - it deals " + @PKG@.AbilMath.fmt(j.freeze) + " % less" + (j.chill > 0.0 ? ", -" + @PKG@.AbilMath.fmt(j.chill) + " % defence" : "") + "."));
  LAST_SB = "sunder" + (echo ? " echo" : "") + " hit=" + n + " weaken=" + @PKG@.AbilMath.fmt(j.freeze) + " def=" + @PKG@.AbilMath.fmt(j.chill);
  return n;
}''')
# RIFT CLEAVE (A1-alt A): the arc + the rift zone (kind 21: n1 0 a line x z -> x2 z2 (r = half its width), 1 a circle of radius r)
late25(r'''
public static @PKG@.AbilZone riftZone(java.util.UUID u, String k, @PKG@.AbilWorld aw, double[] at, double[] to, int mode, double r, double pct, double slow, double secs, double str, double dur, int elem, double h, long now) {
  if (at == null || aw == null) return null;
  @PKG@.AbilZone z = new @PKG@.AbilZone(21, u, at[0], at[1], at[2], r < 0.5 ? 0.5 : r, now, now + ms(secs));
  z.pkey = k;
  z.ai = @PKG@.AbilDefs.RIFT;
  z.n1 = mode;
  z.x2 = to == null ? at[0] : to[0];
  z.z2 = to == null ? at[2] : to[1];
  z.pct = pct;
  z.d1 = slow;
  z.n2 = elem;
  z.d2 = str;
  z.d3 = dur;
  z.h = h;
  z.nextHeal = now;
  z.hit = new java.util.HashSet();
  z.name = "Rift";
  aw.addZone(z);
  RIFTS = RIFTS + 1L;
  return z;
}''')
late25(r'''
public static boolean riftIn(@PKG@.AbilZone z, double qx, double qz) {
  if (z.n1 != 0) return (qx - z.x) * (qx - z.x) + (qz - z.z) * (qz - z.z) <= z.r * z.r;
  double sx = z.x2 - z.x;
  double sz = z.z2 - z.z;
  double l2 = sx * sx + sz * sz;
  double t = l2 > 1.0E-6 ? ((qx - z.x) * sx + (qz - z.z) * sz) / l2 : 0.0;
  if (t < 0.0) t = 0.0;
  if (t > 1.0) t = 1.0;
  double px = z.x + sx * t - qx;
  double pz = z.z + sz * t - qz;
  return px * px + pz * pz <= z.r * z.r;
}''')
late25(r'''
public static String riftCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, long now) {
  if (sh == 2) { aw.add(landJob(u, k, @PKG@.AbilDefs.RIFT, h, now)); return " land"; }
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double[] me = here(st, ref);
  double[] f = flat(st, ref);
  if (me == null) return " nopos";
  if (f == null) f = new double[] { 0.0, 1.0 };
  double pct = breachPctOf(c, sh == 3 ? @PKG@.AbilNum.RC_RINGBREACH : @PKG@.AbilNum.RC_BREACH, 0, 0.0, 0.0, @PKG@.AbilNum.AB_CAP);
  double slow = @PKG@.AbilNum.RC_SLOW + 5.0 * (double) (c == null ? 0 : c.eff(@PKG@.AbilModDefs.SLOW));
  double secs = cxds(sh == 3 ? @PKG@.AbilNum.RC_RINGTIME : @PKG@.AbilNum.RC_TIME);
  @PKG@.AbilJob j = sbJob(u, k, @PKG@.AbilDefs.RIFT, sh, me, f, @PKG@.AbilNum.RC_RANGE + cxr(), sh == 3 ? 180.0 : @PKG@.AbilNum.RC_ANGLE, sh == 3 ? 0.0 : h * @PKG@.AbilNum.RC_POWER * cxm(), now);
  j.freeze = pct;
  j.chill = slow;
  j.secs = secs;
  aw.add(j);
  return " breach=" + @PKG@.AbilMath.fmt(pct) + " slow=" + @PKG@.AbilMath.fmt(slow) + " secs=" + @PKG@.AbilMath.fmt(secs);
}''')
late25(r'''
public static @PKG@.AbilZone riftPlace(@PKG@.AbilJob j, @CB@ cb, @REF@ cr, double[] at, long now) {
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(cb.getExternalData()));
  @PKG@.AbilCtx c = j.cx;
  double rad = c == null ? 0.0 : c.radAdd + c.radTree;
  double[] imb = imbueOf(j.caster, now);
  double[] sm = statMul(j.caster, imb, now);
  int el = imb == null ? -1 : (int) imb[1];
  @PKG@.AbilZone z;
  if (j.sh == 2) z = riftZone(j.caster, j.pkey, aw, at, null, 1, @PKG@.AbilNum.RC_DROPRADIUS + rad, j.freeze, j.chill, j.secs, sm[0], sm[1], el, j.amount, now);
  else if (j.sh == 3) z = riftZone(j.caster, j.pkey, aw, at, null, 1, @PKG@.AbilNum.RC_RINGRADIUS + rad, j.freeze, j.chill, j.secs, sm[0], sm[1], el, j.amount, now);
  else {
    double len = (j.sh == 1 ? @PKG@.AbilNum.RC_RUNLENGTH : @PKG@.AbilNum.RC_LENGTH) + rad;
    double sg = j.sh == 1 ? -1.0 : 1.0;   // Running Rift: behind you
    z = riftZone(j.caster, j.pkey, aw, at, new double[] { at[0] + j.dx * len * sg, at[2] + j.dz * len * sg }, 0, @PKG@.AbilNum.RC_WIDTH / 2.0 + rad * 0.5, j.freeze, j.chill, j.secs, sm[0], sm[1], el, j.amount, now);
  }
  if (z != null) { z.shape = j.sh; z.name = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.RIFT, j.sh); if (c != null && c.echo) z.echoed = true; }
  return z;
}''')
late25(r'''
public static int riftRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_SB = "rift gone"; return -1; }
  @PKG@.AbilCtx c = j.cx;
  double x0 = j.x;
  double y0 = j.y;
  double z0 = j.z;
  if (j.sh != 2) { @VEC@ p = pos(cb, cr); if (p != null) { x0 = p.x; y0 = p.y; z0 = p.z; } }
  int n = 0;
  java.util.ArrayList hs = new java.util.ArrayList();
  boolean imb = imbueOf(j.caster, now) != null;
  if (j.amount > 0.0) {
    hs = sbCone(cb, cr, x0, y0, z0, j.dx, j.dz, j.r, j.width);
    for (int i = 0; i < hs.size(); i++) {
      @REF@ t = (@REF@) hs.get(i);
      if (hit(cb, t, cr, j.caster, j.amount, "RiftCleave")) n++;
      if (imb) imbueStatus(cb, t, cr, j.caster, j.amount, true, now);
    }
    if (imb && nd(c, "Spellblade", "PA2")) burnPatches(cb, cr, j, hs, now);
  }
  @PKG@.AbilZone z = riftPlace(j, cb, cr, new double[] { x0, y0, z0 }, now);
  if (z != null && n > 0 && (c == null || !c.echo)) { z.echoed = true; momAdd(j.caster, (int) Math.round(@PKG@.AbilNum.RC_GAIN), now); used(j.caster, j.pkey, @PKG@.AbilDefs.RIFT, c); }
  particle(FX_SPLIT0, x0 + j.dx * 1.5, y0 + 0.1, z0 + j.dz * 1.5, cb);
  @PR@ pr = prOf(j.caster);
  if (pr != null && z != null) say(pr, z.name + ": a rift for " + @PKG@.AbilMath.fmt(j.secs) + " s - Breach +" + @PKG@.AbilMath.fmt(j.freeze) + " % and " + @PKG@.AbilMath.fmt(j.chill) + " % slow inside" + (n > 0 ? " (" + n + (n == 1 ? " enemy" : " enemies") + " cleaved)." : "."));
  LAST_SB = "rift " + j.sh + " hit=" + n + " mode=" + (z == null ? -1 : z.n1);
  return n;
}''')
late25(r'''
public static boolean riftTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  boolean ok = live(cb, cr, z.caster, z.pkey);
  @PKG@.AbilCtx c = z.cx;
  if (!ok || z.ended || now >= z.until) {
    if (ok && c != null && !c.echo && c.echoPct > 0.0 && z.pct > 0.0 && !"Burning Rift".equals(z.name)) {   // Echo: a weaker rift 1 s after it ends
      @PKG@.AbilJob ej = new @PKG@.AbilJob(10, now + ms(@PKG@.AbilCfg.ECHO_DELAY), z.caster, "RiftCleave", z.x, z.y, z.z, z.r, z.h);
      ej.pkey = z.pkey;
      ej.ai = @PKG@.AbilDefs.RIFT;
      ej.sh = z.shape;
      ej.dx = z.x2;
      ej.dz = z.z2;
      ej.freeze = z.pct * c.echoPct;
      ej.chill = z.d1 * c.echoPct;
      ej.secs = (double) (z.until - z.start) / 1000.0;
      ej.left = z.n1;
      ej.width = z.d2;
      ej.len = z.d3;
      ej.total = z.n2;
      ej.cx = c.echoOf(c.echoPct);
      @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
      if (aw != null) aw.add(ej);
    }
    LAST_SB = "rift end " + z.hits;
    return false;
  }
  if (now < z.nextHeal) return true;
  z.nextHeal = now + 1000L;
  double reach = z.n1 == 0 ? Math.sqrt((z.x2 - z.x) * (z.x2 - z.x) + (z.z2 - z.z) * (z.z2 - z.z)) / 2.0 + z.r + 1.0 : z.r + 0.5;
  double cx0 = z.n1 == 0 ? (z.x + z.x2) / 2.0 : z.x;
  double cz0 = z.n1 == 0 ? (z.z + z.z2) / 2.0 : z.z;
  java.util.List l = near(cb, cx0, z.y, cz0, reach);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    @VEC@ q = pos(cb, t);
    if (q == null || !riftIn(z, q.x, q.z) || Math.abs(q.y - z.y) > 4.0) continue;
    n++;
    if (z.pct > 0.0) breachOn(cb, t, z.caster, z.pct, 1.5, now, c);
    if (z.d1 > 0.0) { int sl = (int) Math.round(z.d1 * (bossT(cb, t) ? @PKG@.AbilNum.EL_BOSSCC / 100.0 : 1.0)); if (sl > 0) effect(cb, t, sl >= 30 ? EF_SLOW : spdId(-sl), 1.5); }
    if (z.n2 >= 0) statusOn(cb, t, cr, z.caster, z.n2, z.h * 0.5, z.d2, z.d3, now, false);
  }
  z.hits = z.hits + n;
  if (n > 0 && !z.echoed && (c == null || !c.echo)) { z.echoed = true; momAdd(z.caster, (int) Math.round(@PKG@.AbilNum.RC_GAIN), now); used(z.caster, z.pkey, @PKG@.AbilDefs.RIFT, c); }
  if (now >= z.nextFx) {
    z.nextFx = now + 1000L;
    if (z.n1 == 0) for (int s2 = 0; s2 <= 3; s2++) particle(FX_SPLIT, z.x + (z.x2 - z.x) * (double) s2 / 3.0, z.y + 0.1, z.z + (z.z2 - z.z) * (double) s2 / 3.0, cb);
    else ring(FX_SPLIT, z, cb);
  }
  return true;
}''')
# SHATTERING ARC (A1-alt B): spends Momentum at the cast (you keep 5); the arc does the rest
late25(r'''
public static String shatterCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  int live = momN(u, now);
  int want = sh == 3 ? (live + 1) / 2 : live;
  int sp = momSpend(u, want, (int) Math.round(@PKG@.AbilNum.SA_KEEP), now);
  SHATTERS = SHATTERS + 1L;
  if (sh == 2) {
    @PKG@.AbilJob lj = landJob(u, k, @PKG@.AbilDefs.SHATTER, h, now);
    lj.len = (double) sp;
    aw.add(lj);
    return " land spent=" + sp;
  }
  double[] me = here(st, ref);
  double[] f = flat(st, ref);
  if (me == null) return " nopos";
  if (sh == 1 && f != null) push(st, ref, f[0] * @PKG@.AbilNum.SA_STEP * @PKG@.AbilCfg.PUSH_PER_BLOCK, 0.0, f[1] * @PKG@.AbilNum.SA_STEP * @PKG@.AbilCfg.PUSH_PER_BLOCK);
  @PKG@.AbilJob j = sbJob(u, k, @PKG@.AbilDefs.SHATTER, sh, me, f, @PKG@.AbilNum.SA_RANGE + cxr(), sh == 3 ? @PKG@.AbilNum.SA_HALFANGLE : @PKG@.AbilNum.SA_ANGLE, 0.0, now);
  shatterNums(j, c, h, sp);
  aw.add(j);
  return " spent=" + sp + " hit=" + @PKG@.AbilMath.fmt(j.amount) + " breach=" + @PKG@.AbilMath.fmt(j.freeze) + " secs=" + @PKG@.AbilMath.fmt(j.secs);
}''')
late25(r'''
public static void shatterNums(@PKG@.AbilJob j, @PKG@.AbilCtx c, double h, int sp) {
  double pw = (j.sh == 2 ? @PKG@.AbilNum.SA_AIRPOWER : @PKG@.AbilNum.SA_POWER) + @PKG@.AbilNum.SA_PERSTACK * (double) sp;
  j.amount = h * pw * (c == null ? 1.0 : c.main);
  j.freeze = breachPctOf(c, @PKG@.AbilNum.SA_BREACH, sp, @PKG@.AbilNum.SA_BREACHPERSTACK, 1000.0, @PKG@.AbilNum.SA_BREACHCAP);
  j.secs = cxds(@PKG@.AbilNum.SA_TIME + @PKG@.AbilNum.SA_TIMEPERSTACK * (double) sp);
  j.len = (double) sp;
}''')
late25(r'''
public static int shatterRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_SB = "shatter gone"; return -1; }
  @PKG@.AbilCtx c = j.cx;
  boolean echo = c != null && c.echo;
  double x0 = j.x;
  double y0 = j.y;
  double z0 = j.z;
  if (j.sh != 2) { @VEC@ p = pos(cb, cr); if (p != null) { x0 = p.x; y0 = p.y; z0 = p.z; } }
  java.util.ArrayList hs = sbCone(cb, cr, x0, y0, z0, j.dx, j.dz, j.r, j.width);
  int kb = c == null ? 0 : c.eff(@PKG@.AbilModDefs.KNOCK);
  int lc = c == null ? 0 : c.eff(@PKG@.AbilModDefs.LEECH);
  boolean imb = imbueOf(j.caster, now) != null;
  int n = 0;
  double dealt = 0.0;
  for (int i = 0; i < hs.size(); i++) {
    @REF@ t = (@REF@) hs.get(i);
    if (hit(cb, t, cr, j.caster, j.amount, "ShatteringArc")) { n++; dealt = dealt + j.amount; }
    if (!echo) breachOn(cb, t, j.caster, j.freeze, j.secs, now, c);
    if (imb) imbueStatus(cb, t, cr, j.caster, j.amount, true, now);
    @VEC@ q = pos(cb, t);
    double up = j.sh == 2 ? @PKG@.AbilNum.SA_AIRUP * @PKG@.AbilCfg.PUSH_PER_BLOCK * 0.5 : 0.0;
    if ((kb > 0 || up > 0.0) && q != null) {
      double dx = q.x - x0;
      double dz = q.z - z0;
      double d = Math.sqrt(dx * dx + dz * dz);
      double f = 2.0 * (double) kb * @PKG@.AbilCfg.PUSH_PER_BLOCK;
      if (d > 0.05) push(cb, t, dx / d * f, up > 0.0 ? up : f * 0.25, dz / d * f);
      else push(cb, t, 0.0, up, 0.0);
    }
  }
  if (lc > 0 && dealt > 0.0) apply(cb, cr, dealt * 3.0 * (double) lc / 100.0, dealt * 3.0 * (double) lc / 100.0);   // Leech: 3 % a level
  if (!echo && c != null && c.echoPct > 0.0) {   // Echo: a weaker arc 1 s later, spending nothing
    @PKG@.AbilJob ej = new @PKG@.AbilJob(10, now + ms(@PKG@.AbilCfg.ECHO_DELAY), j.caster, "ShatteringArc", x0, y0, z0, j.r, j.amount * c.echoPct);
    ej.pkey = j.pkey;
    ej.ai = @PKG@.AbilDefs.SHATTER;
    ej.sh = j.sh;
    ej.dx = j.dx;
    ej.dz = j.dz;
    ej.width = j.width;
    ej.cx = c.echoOf(c.echoPct);
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
    if (aw != null) aw.add(ej);
  }
  if (n > 0 && !echo) used(j.caster, j.pkey, @PKG@.AbilDefs.SHATTER, c);
  particle(j.sh == 2 ? FX_CRATER : FX_KICK, x0 + j.dx * 2.0, y0 + 0.3, z0 + j.dz * 2.0, cb);
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, (echo ? "Echo: " : "") + @PKG@.AbilDefs.sname(@PKG@.AbilDefs.SHATTER, j.sh) + ": " + n + (n == 1 ? " enemy" : " enemies") + (echo ? " hit." : " hit, " + (int) j.len + " Momentum spent - Breach +" + @PKG@.AbilMath.fmt(j.freeze) + " % for " + @PKG@.AbilMath.fmt(j.secs) + " s."));
  LAST_SB = "shatter" + (echo ? " echo" : "") + " hit=" + n + " spent=" + (int) j.len + " pct=" + @PKG@.AbilMath.fmt(j.freeze);
  return n;
}''')
# the Charging Imbue crescent / the Falling Imbue burst (element damage + the status)
late25(r'''
public static int imbueRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_SB = "imbue gone"; return -1; }
  java.util.ArrayList hs = j.sh == 2 ? sbCone(cb, cr, j.x, j.y, j.z, 0.0, 1.0, j.r, 180.0) : sbLine(cb, cr, j.x, j.y, j.z, j.dx, j.dz, j.r, @PKG@.AbilNum.EI_CRESCENTWIDTH);
  int n = 0;
  for (int i = 0; i < hs.size(); i++) {
    @REF@ t = (@REF@) hs.get(i);
    if (hit(cb, t, cr, j.caster, j.amount, j.sh == 2 ? "ImbueBurst" : "ImbueCrescent")) n++;
    imbueStatus(cb, t, cr, j.caster, j.amount, true, now);
  }
  if (j.sh == 2) particle(FX_CRATER, j.x, j.y + 0.1, j.z, cb);
  else for (int s2 = 1; s2 <= 4; s2++) particle(FX_KICK, j.x + j.dx * j.r * (double) s2 / 4.0, j.y + 1.0, j.z + j.dz * j.r * (double) s2 / 4.0, cb);
  LAST_SB = "imbue " + (j.sh == 2 ? "burst" : "crescent") + " hit=" + n;
  return n;
}''')
late25(r'''
public static boolean runJob5(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  if (j.kind == 26) return dotTick(j, st, cb, now);
  if (j.kind != 25) return false;
  if (j.ai == @PKG@.AbilDefs.BREACH) breachRun(j, st, cb, now);
  else if (j.ai == @PKG@.AbilDefs.SUNDER) sunderRun(j, st, cb, now);
  else if (j.ai == @PKG@.AbilDefs.RIFT) riftRun(j, st, cb, now);
  else if (j.ai == @PKG@.AbilDefs.SHATTER) shatterRun(j, st, cb, now);
  else if (j.ai == @PKG@.AbilDefs.IMBUE) imbueRun(j, st, cb, now);
  return false;
}''')
late25(r'''
public static boolean zoneTick5(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind == 21) return riftTick(z, st, cb, now);
  return false;
}''')
# the mid-air shapes, where the caster lands (Abil.land)
late25(r'''
public static String landSb(@PKG@.AbilJob j, @ST@ st, @CB@ cb, @REF@ cr, double[] at, long now) {
  int ai = j.ai;
  @PKG@.AbilCtx c = j.cx;
  @PR@ pr = prOf(j.caster);
  if (ai == @PKG@.AbilDefs.BREACH) {
    @PKG@.AbilJob b = sbJob(j.caster, j.pkey, ai, 2, at, null, @PKG@.AbilNum.AB_AIRRADIUS + cxr(), 180.0, j.amount * @PKG@.AbilNum.AB_AIRPOWER * cxm(), now);
    b.freeze = breachPctOf(c, @PKG@.AbilNum.AB_BREACH, momN(j.caster, now), @PKG@.AbilNum.AB_PERSTACK, @PKG@.AbilNum.AB_STACKCAP, @PKG@.AbilNum.AB_CAP);
    b.secs = durCap(@PKG@.AbilNum.AB_TIME, @PKG@.AbilNum.AB_DURMAX);
    return "breach:" + breachRun(b, st, cb, now);
  }
  if (ai == @PKG@.AbilDefs.IMBUE) {
    @PKG@.AbilJob b = sbJob(j.caster, j.pkey, ai, 2, at, null, @PKG@.AbilNum.EI_BURSTRADIUS + cxr(), 180.0, j.amount * @PKG@.AbilNum.EI_BURSTPOWER * cxm(), now);
    return "burst:" + imbueRun(b, st, cb, now);
  }
  if (ai == @PKG@.AbilDefs.SUNDER) {
    @REF@ t = nearest(cb, cr, at[0], at[1], at[2], @PKG@.AbilNum.SU_AIRRADIUS + cxr(), null);
    if (t == null) { if (pr != null) send(pr, "Sunder from Above: no enemy near your landing.", "#ffc800"); return "sunder:none"; }
    @PKG@.AbilJob b = sbJob(j.caster, j.pkey, ai, 2, at, null, 0.0, 0.0, j.amount * @PKG@.AbilNum.SU_AIRPOWER * cxm(), now);
    b.tref = t;
    sunderNums(b, c, 2);
    return "sunder:" + sunderRun(b, st, cb, now);
  }
  if (ai == @PKG@.AbilDefs.RIFT) {
    @PKG@.AbilJob b = sbJob(j.caster, j.pkey, ai, 2, at, null, 0.0, 180.0, 0.0, now);
    b.freeze = breachPctOf(c, @PKG@.AbilNum.RC_BREACH, 0, 0.0, 0.0, @PKG@.AbilNum.AB_CAP);
    b.chill = @PKG@.AbilNum.RC_SLOW + 5.0 * (double) (c == null ? 0 : c.eff(@PKG@.AbilModDefs.SLOW));
    b.secs = cxds(@PKG@.AbilNum.RC_TIME);
    return "rift:" + riftRun(b, st, cb, now);
  }
  if (ai == @PKG@.AbilDefs.SHATTER) {
    @PKG@.AbilJob b = sbJob(j.caster, j.pkey, ai, 2, at, null, @PKG@.AbilNum.SA_AIRRADIUS + cxr(), 180.0, 0.0, now);
    shatterNums(b, c, j.amount, (int) j.len);
    return "shatter:" + shatterRun(b, st, cb, now);
  }
  return "none";
}''')
# the echoes of the Spellblade (echoRun2's tail): Sunder's strike, Rift Cleave's second rift, Shattering Arc's second arc
late25(r'''
public static String echoRun3(@PKG@.AbilJob j, @ST@ st, @CB@ cb, @REF@ cr, long now) {
  if (j.ai == @PKG@.AbilDefs.SUNDER) {
    @PKG@.AbilJob s2 = sbJob(j.caster, j.pkey, j.ai, j.sh, new double[] { j.x, j.y, j.z }, null, 0.0, 0.0, j.amount, now);
    s2.tref = j.tref;
    s2.cx = j.cx;
    return "sunder:" + sunderRun(s2, st, cb, now);
  }
  if (j.ai == @PKG@.AbilDefs.SHATTER) {
    @PKG@.AbilJob s2 = sbJob(j.caster, j.pkey, j.ai, 2, new double[] { j.x, j.y, j.z }, new double[] { j.dx, j.dz }, j.r, j.width, j.amount, now);
    s2.cx = j.cx;
    return "shatter:" + shatterRun(s2, st, cb, now);
  }
  if (j.ai == @PKG@.AbilDefs.RIFT) {
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
    @PKG@.AbilZone z = riftZone(j.caster, j.pkey, aw, new double[] { j.x, j.y, j.z }, new double[] { j.dx, j.dz }, j.left, j.r, j.freeze, j.chill, j.secs, j.width, j.len, j.total, j.amount, now);
    if (z != null) { z.echoed = true; z.shape = j.sh; z.name = "Echo rift"; }
    @PR@ pr = prOf(j.caster);
    if (pr != null && z != null) say(pr, "Echo: a weaker rift.");
    return z == null ? "rift:none" : "rift:" + @PKG@.AbilMath.fmt(z.pct);
  }
  return null;
}''')

# ---------------------------------------------------------------- THE HOOKS
# the WEAPON hit going out (DamageLock's outgoing hook): Imbue's element part (our multiplier until SkyyGear reads classes:fn:imbue -
# gear:imbue = true switches it off: no double count) and Keen Edge (T5)
late25(r'''
public static String outHit3(@ST@ st, @CB@ buf, @REF@ t, @DMG@ d, java.util.UUID u, long now) {
  try {
    if (u == null || t == null || d == null || d.isCancelled()) return null;
    float a0 = d.getAmount();
    if (!(a0 > 0.0f) || @PKG@.AbilDmg.mine(d)) return null;
    if (buf.getComponent(t, @NPC@.getComponentType()) == null) return null;
    if (@PKG@.ClassStore.classIndex(u) != sbCi()) return null;
    @PR@ pr = prOf(u);
    @REF@ att = pr == null ? null : pr.getReference();
    if (att == null || !sbWeapon(u, hand(buf, att))) return null;
    double m = 1.0;
    String out = "";
    double[] imb = imbueOf(u, now);
    if (imb != null && !Boolean.TRUE.equals(@PKG@.ClassCfg.bridge().get("gear:imbue"))) {
      int n = momN(u, now);
      m = m * (1.0 + imb[2] / 100.0 * (1.0 + (double) n * @PKG@.AbilNum.MO_ELEMPERSTACK / 100.0));
      out = out + " imbue";
    }
    if ((sbFlags(u, now) & 16L) != 0L) { m = m * (1.0 + @PKG@.AbilNum.MO_KEEN / 100.0); out = out + " keen"; }
    if (m != 1.0) d.setAmount((float) ((double) a0 * m));
    return out.length() == 0 ? null : out.trim() + " x" + @PKG@.AbilMath.fmt(m);
  } catch (Throwable x) { @PKG@.ClassCfg.warnLimited("a Spellblade hit bonus failed: " + x); return null; }
}''')
# the LANDED hit (AbilFrostSys, Inspect group): Momentum from Spellblade weapon hits (+1 an enemy, at most maxPerSwing a swing, the
# rhythm bonus), Imbue's status + its counted use, Tempest (PA5: every 5th hit while Unstoppable = a ring of the element)
late25(r'''
public static String hitLanded3(@CB@ buf, @REF@ t, @DMG@ d, long now) {
  try {
    if (d == null || t == null || d.isCancelled() || !(d.getAmount() > 0.0f)) return null;
    if (@PKG@.AbilDmg.mine(d)) return null;
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DENT@)) return null;
    @REF@ att = ((@DENT@) src).getRef();
    if (att == null || !att.isValid() || att.equals(t)) return null;
    Object po = buf.getComponent(att, @PR@.getComponentType());
    if (!(po instanceof @PR@)) return null;
    java.util.UUID u = ((@PR@) po).getUuid();
    if (u == null || buf.getComponent(t, @NPC@.getComponentType()) == null) return null;
    if (@PKG@.ClassStore.classIndex(u) != sbCi()) return null;
    SB_LIVE = true;
    if (!sbWeapon(u, hand(buf, att))) return null;
    long[] x = momX(u);
    long fl = sbFlags(u, now);
    int gain = 0;
    boolean same = x[2] > 0L && now >= x[2] && now - x[2] < ms(@PKG@.AbilNum.MO_SWING);
    if (same) {
      if ((double) x[3] < @PKG@.AbilNum.MO_MAXPERSWING) { x[3] = x[3] + 1L; gain = (int) Math.round(@PKG@.AbilNum.MO_PERHIT); }
    } else {
      x[2] = now;
      x[3] = 1L;
      gain = (int) Math.round(@PKG@.AbilNum.MO_PERHIT);
      if (x[1] > 0L && now >= x[1] && now - x[1] < 2000L) gain = gain + (int) Math.round(@PKG@.AbilNum.MO_RHYTHM);   // the swing started in rhythm
      x[1] = 0L;
    }
    x[0] = now;
    int n = gain > 0 ? momAdd(u, gain, now) : momN(u, now);
    String out = "mom+" + gain + "=" + n;
    double amt = (double) d.getAmount();
    double[] imb = imbueOf(u, now);
    if (imb != null) {
      String sr = imbueStatus(buf, t, att, u, amt, false, now);
      if (sr != null) out = out + " " + sr;
      if (imb[5] < 0.5) { imb[5] = 1.0; used(u, @PKG@.ClassCfg.pkey(u), @PKG@.AbilDefs.IMBUE, null); }
    }
    if ((fl & 2L) != 0L && momTier(n) == 2) {   // Tempest (PA5): every 5th hit while Unstoppable releases a ring of your element
      x[5] = x[5] + 1L;
      long every = Math.round(@PKG@.AbilNum.MO_TEMPESTEVERY);
      if (every > 0L && x[5] % every == 0L) {
        @VEC@ p = pos(buf, att);
        int el = imb != null ? (int) imb[1] : attOf(@PKG@.ClassCfg.pkey(u), 1);
        double h = hOf(hand(buf, att)) * @PKG@.AbilNum.MO_TEMPESTPOWER;
        int rn = 0;
        if (p != null) {
          java.util.ArrayList hs = sbCone(buf, att, p.x, p.y, p.z, 0.0, 1.0, @PKG@.AbilNum.MO_TEMPESTRADIUS, 180.0);
          double[] sm = statMul(u, imb, now);
          for (int i = 0; i < hs.size(); i++) {
            @REF@ e = (@REF@) hs.get(i);
            if (hit(buf, e, att, u, h, "Tempest")) rn++;
            statusOn(buf, e, att, u, el, h, sm[0], sm[1], now, true);
          }
          particle(FX_SHOCK, p.x, p.y + 0.2, p.z, buf);
        }
        out = out + " tempest=" + rn;
      }
    }
    LAST_SB = out;
    return out;
  } catch (Throwable x0) { return null; }
}''')
# the PLAYER hit (AbilShieldSys, after armour): a heavy hit costs Momentum, Unstoppable strips the knockback (+ Vanguard PC5 -15 %),
# a Sundered attacker deals less (Weakened)
late25(r'''
public static String inHit3(@ST@ st, @CB@ buf, @REF@ r, @DMG@ d, long now) {
  if (d == null || r == null || d.isCancelled()) return null;
  float a0 = d.getAmount();
  if (!(a0 > 0.0f) || @PKG@.AbilDmg.mine(d)) return null;
  Object po = buf.getComponent(r, @PR@.getComponentType());
  if (!(po instanceof @PR@)) return null;
  java.util.UUID u = ((@PR@) po).getUuid();
  if (u == null) return null;
  double amt = (double) a0;
  String out = "";
  @REF@ att = null;
  @DSRC@ src = d.getSource();
  if (src instanceof @DENT@) { try { att = ((@DENT@) src).getRef(); } catch (Throwable t0) { att = null; } }
  if (att != null && !@PKG@.AbilStore.SUNDER.isEmpty()) {
    Object so = @PKG@.AbilStore.SUNDER.get(att);
    if (so instanceof double[] && ((double[]) so)[0] > (double) now) { amt = amt * (1.0 - ((double[]) so)[1] / 100.0); out = out + " weakened"; }
  }
  if (!@PKG@.AbilStore.MOMS.isEmpty() && @PKG@.AbilStore.MOMS.containsKey(u)) {
    int n = momN(u, now);
    if (n > 0) {
      double mx = max(map(buf, r), @DST@.getHealth());
      if (mx > 0.0 && amt >= mx * @PKG@.AbilNum.MO_HEAVYHIT / 100.0) { momLose(u, (int) Math.round(@PKG@.AbilNum.MO_HEAVYDROP), now, "heavy hit"); out = out + " heavy"; n = momN(u, now); }
      if (momTier(n) == 2) {
        buf.tryRemoveComponent(r, @KBC@.getComponentType());
        out = out + " unstoppable";
        if ((sbFlags(u, now) & 8L) != 0L) { amt = amt * (1.0 - @PKG@.AbilNum.MO_VANGUARDCUT / 100.0); out = out + " vanguard"; }
      }
    }
  }
  if (amt < (double) a0 - 1.0E-6) d.setAmount((float) (amt < 0.0 ? 0.0 : amt));
  return out.length() == 0 ? null : out.trim();
}''')

# ---------------------------------------------------------------- the class tree (research/classes/Spellblade.md), the panel texts, the prune
late25(r'''
public static void treeApply4(@PKG@.AbilCtx c) {
  if (c == null || c.ai < 0 || !"Spellblade".equals(c.cls)) return;
  int ai = c.ai;
  double q = c.amt("T6", 5.0);   // Tempo: every Spellblade cooldown -5 %
  if (q > 0.0) c.cdMult = c.cdMult * (1.0 - (q > 90.0 ? 90.0 : q) / 100.0);
  if ((ai == @PKG@.AbilDefs.BREACH || ai == @PKG@.AbilDefs.RIFT) && c.node("PA2")) c.costAdd = c.costAdd + 3.0;   // Burning Rift: +3 Mana
  if (ai == @PKG@.AbilDefs.IMBUE && c.node("PA1")) c.durAdd = c.durAdd - @PKG@.AbilNum.EI_TWINCUT;               // Twin Attunement: -2 s
  if (ai == @PKG@.AbilDefs.SUNDER && c.node("PB2")) c.cdAdd = c.cdAdd + ms(@PKG@.AbilNum.SU_SPLITCD);           // Armour Split: +4 s
  if (ai == @PKG@.AbilDefs.BREACH && c.node("PB4")) c.durAdd = c.durAdd - 1.0;                                    // Marked for Death: -1 s
}''')
late25(r'''
public static String modText3(int ai, int mi, int lvl, int e, int l1) {
  double ep = @PKG@.AbilCfg.ECHO_BASE + @PKG@.AbilCfg.ECHO_STEP * (double) l1;
  if (mi == @PKG@.AbilModDefs.ECHO) {
    if (ai == @PKG@.AbilDefs.SUNDER) return "a second strike 1 s later at " + @PKG@.AbilMath.fmt(ep) + " %";
    if (ai == @PKG@.AbilDefs.RIFT) return "a weaker rift 1 s after it ends (" + @PKG@.AbilMath.fmt(ep) + " %)";
    if (ai == @PKG@.AbilDefs.SHATTER) return "a second arc 1 s later at " + @PKG@.AbilMath.fmt(ep) + " % - spends nothing";
  }
  if (mi == @PKG@.AbilModDefs.CHAIN) {
    if (ai == @PKG@.AbilDefs.BREACH) return "Breach jumps to " + e + " more enem" + (e == 1 ? "y" : "ies") + " the arc missed";
    if (ai == @PKG@.AbilDefs.IMBUE) return "the status jumps to " + e + " more within " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.EI_CHAINRANGE) + " blocks";
    if (ai == @PKG@.AbilDefs.SUNDER) return "also strikes the nearest enemy within " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.SU_CHAINRANGE) + " at " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.SU_CHAINPCT) + " %";
  }
  if (mi == @PKG@.AbilModDefs.DURATION && (ai == @PKG@.AbilDefs.BREACH || ai == @PKG@.AbilDefs.SUNDER)) return "+" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.MOD_DUR * (double) e) + " % longer (at most +2 s)";
  if (mi == @PKG@.AbilModDefs.POWER && (ai == @PKG@.AbilDefs.BREACH || ai == @PKG@.AbilDefs.RIFT || ai == @PKG@.AbilDefs.SHATTER)) return "+" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.MOD_POWER * (double) e) + " % damage and Breach";
  if (mi == @PKG@.AbilModDefs.POWER && ai == @PKG@.AbilDefs.SUNDER) return "+" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.MOD_POWER * (double) e) + " % damage and Weaken";
  if (mi == @PKG@.AbilModDefs.POWER && ai == @PKG@.AbilDefs.IMBUE) return "+" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.MOD_POWER * (double) e) + " % element damage";
  if (mi == @PKG@.AbilModDefs.SLOW && ai == @PKG@.AbilDefs.RIFT) return "the rift slows " + (5 * e) + " % more";
  if (mi == @PKG@.AbilModDefs.KNOCK && ai == @PKG@.AbilDefs.SHATTER) return "the arc throws enemies back " + (2 * e) + " blocks";
  if (mi == @PKG@.AbilModDefs.LEECH && ai == @PKG@.AbilDefs.SHATTER) return "you heal " + (3 * e) + " % of the damage";
  if (mi == @PKG@.AbilModDefs.RADIUS && ai == @PKG@.AbilDefs.RIFT) return "+" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.MOD_RADIUS * (double) e) + " blocks longer rift / wider ring";
  return null;
}''')
late25(r'''
public static void pruneMobs3(long now) {
  pruneD(@PKG@.AbilStore.BREACH, now, 0, 0);
  pruneD(@PKG@.AbilStore.SUNDER, now, 0, 0);
  pruneD(@PKG@.AbilStore.SHOCKD, now, 0, 0);
  if (!@PKG@.AbilStore.STAGD.isEmpty()) {
    java.util.Iterator it = @PKG@.AbilStore.STAGD.keySet().iterator();
    while (it.hasNext()) {
      Object k = it.next();
      boolean dead = false;
      try { dead = (k instanceof @REF@) && !((@REF@) k).isValid(); } catch (Throwable t) { dead = false; }
      if (dead || @PKG@.AbilStore.STAGD.size() > 1024) it.remove();
    }
  }
  if (!@PKG@.AbilStore.CHILLS.isEmpty()) {
    java.util.Iterator it = @PKG@.AbilStore.CHILLS.keySet().iterator();
    while (it.hasNext()) {
      Object k = it.next();
      Object v = @PKG@.AbilStore.CHILLS.get(k);
      long last = 0L;
      if (v instanceof long[]) for (int i = 0; i < ((long[]) v).length; i++) if (((long[]) v)[i] > last) last = ((long[]) v)[i];
      boolean dead = false;
      try { dead = (k instanceof @REF@) && !((@REF@) k).isValid(); } catch (Throwable t) { dead = false; }
      if (dead || now - last > 10000L) it.remove();
    }
  }
  if (!@PKG@.AbilStore.DOTS.isEmpty()) {
    java.util.Iterator it = @PKG@.AbilStore.DOTS.keySet().iterator();
    while (it.hasNext()) {
      Object k = it.next();
      Object v = @PKG@.AbilStore.DOTS.get(k);
      boolean any = false;
      if (v instanceof java.util.ArrayList) {
        java.util.ArrayList l = (java.util.ArrayList) v;
        synchronized (l) { for (int i = 0; i < l.size(); i++) if (((@PKG@.AbilJob) l.get(i)).left > 0) any = true; }
      }
      if (!any) it.remove();
    }
  }
  pruneD(@PKG@.AbilStore.IMBUE, now, 0, 0);
}''')

for _m in L25:
    assert '"""' not in _m
_WL_END = '''  if (out.length() > 0) LAST_BER = "world left" + out;
  return out.length() == 0 ? null : out.trim();
}
"""
]'''
rep(_WL_END, _WL_END[:-2] + ''',
''' + ",\n".join('r"""\n%s\n"""' % _m for _m in L25) + '''
]''')

# ================================================================================================ dispatch: jobs, zones, landings, echoes, mod texts, the tree, the prune
rep('''  if (j.kind == 24) { pinRun(j, st, cb, now); return false; }
  return false;''', '''  if (j.kind == 24) { pinRun(j, st, cb, now); return false; }
  if (j.kind >= 25) return runJob5(j, st, cb, now);   // 0.1.25: the Spellblade arcs + the Burn / Poison ticks
  return false;''')
rep('''  if (z.kind == 20) return netTick(z, st, cb, now);
  return false;''', '''  if (z.kind == 20) return netTick(z, st, cb, now);
  if (z.kind >= 21) return zoneTick5(z, st, cb, now);   // 0.1.25: the rifts
  return false;''')
rep('''  if (ai == @PKG@.AbilDefs.BANNER) return "banner:" + bannerAt(pr, cb, cr, j.caster, j.pkey, aw, at, 2, now);
  return "none";''', '''  if (ai == @PKG@.AbilDefs.BANNER) return "banner:" + bannerAt(pr, cb, cr, j.caster, j.pkey, aw, at, 2, now);
  if (ai >= @PKG@.AbilDefs.BREACH) return landSb(j, st, cb, cr, at, now);   // 0.1.25: the Spellblade's mid-air shapes
  return "none";''')
rep('''  if (j.ai == @PKG@.AbilDefs.EXPLO) return "blast:" + blastAt(cb, cr, j.caster, j.x, j.y, j.z, j.r, j.amount, j.push, j.cx, null, true);
  return null;''', '''  if (j.ai == @PKG@.AbilDefs.EXPLO) return "blast:" + blastAt(cb, cr, j.caster, j.x, j.y, j.z, j.r, j.amount, j.push, j.cx, null, true);
  if (j.ai >= @PKG@.AbilDefs.BREACH) return echoRun3(j, st, cb, cr, now);   // 0.1.25: Sunder, Rift Cleave, Shattering Arc
  return null;''')
rep('''public static String modText2(int ai, int mi, int lvl, int e, int l1) {
  if (mi == @PKG@.AbilModDefs.ECHO) {''', '''public static String modText2(int ai, int mi, int lvl, int e, int l1) {
  if (ai >= @PKG@.AbilDefs.BREACH) { String t25 = modText3(ai, mi, lvl, e, l1); if (t25 != null) return t25; }   // 0.1.25: the Spellblade
  if (mi == @PKG@.AbilModDefs.ECHO) {''')
rep('''  boolean arc = "Archer".equals(c.cls);
  if (!war && !ber && !arc) return;''', '''  boolean arc = "Archer".equals(c.cls);
  if (!war && !ber && !arc) { treeApply4(c); return; }   // 0.1.25: the Spellblade''')
rep('''  pruneD(@PKG@.AbilStore.EXPL, now, 0, 0);
  if (!@PKG@.AbilStore.EXPLC.isEmpty()) {''', '''  pruneD(@PKG@.AbilStore.EXPL, now, 0, 0);
  pruneMobs3(now);   // 0.1.25: Breach, Sunder, Shock, Stagger, Chills, the damage-over-time lists, Imbue
  if (!@PKG@.AbilStore.EXPLC.isEmpty()) {''')

# ================================================================================================ castAt0: the Sunder target before anything is paid, the executors
rep('''  if (ai == @PKG@.AbilDefs.BANNER && sh == 1) at = ahead(st, ref, @PKG@.AbilNum.WB_AHEAD);''',
    '''  if (ai == @PKG@.AbilDefs.BANNER && sh == 1) at = ahead(st, ref, @PKG@.AbilNum.WB_AHEAD);
  @REF@ sbT = null;   // 0.1.25: Sunder strikes the enemy you look at - found before anything is paid
  if (ai == @PKG@.AbilDefs.SUNDER && sh != 2) {
    double sr = @PKG@.AbilNum.SU_RANGE + (sh == 1 ? @PKG@.AbilNum.SU_STEP : 0.0);
    sbT = lookMob(st, ref, sr);
    if (sbT == null) { refuse(pr, "No enemy in front of you within " + @PKG@.AbilMath.fmt(sr) + " blocks to Sunder - nothing was spent."); return "notarget"; }
  }''')
rep('''    else if (ai == @PKG@.AbilDefs.NET) extra = netCast(pr, st, ref, u, k, aw, sh, h, at, now);''',
    '''    else if (ai == @PKG@.AbilDefs.NET) extra = netCast(pr, st, ref, u, k, aw, sh, h, at, now);
    // 0.1.25: THE SPELLBLADE (Breach / Sunder / Rift Cleave / Shattering Arc land first in the air; Imbue imbues now + bursts on landing)
    else if (ai == @PKG@.AbilDefs.BREACH) extra = breachCast(pr, st, ref, u, k, aw, sh, h, now);
    else if (ai == @PKG@.AbilDefs.IMBUE) extra = imbueCast(pr, st, ref, u, k, aw, sh, h, item, now);
    else if (ai == @PKG@.AbilDefs.SUNDER) extra = sunderCast(pr, st, ref, u, k, aw, sh, h, sbT, now);
    else if (ai == @PKG@.AbilDefs.RIFT) extra = riftCast(pr, st, ref, u, k, aw, sh, h, now);
    else if (ai == @PKG@.AbilDefs.SHATTER) extra = shatterCast(pr, st, ref, u, k, aw, sh, h, now);''')

# ================================================================================================ the hooks: outMult (Breach + Mark), DamageLock, AbilShieldSys, AbilFrostSys, the swing, the tick
rep('''    if (!@PKG@.AbilStore.MARKD.isEmpty()) {
      Object o = @PKG@.AbilStore.MARKD.get(t);
      if (o instanceof double[] && ((double[]) o)[0] > tn) m = m * (1.0 + ((double[]) o)[1] / 100.0);
    }
    if (!@PKG@.AbilStore.ROOTS.isEmpty()) {''', '''    double mk25 = 0.0;
    if (!@PKG@.AbilStore.MARKD.isEmpty()) {
      Object o = @PKG@.AbilStore.MARKD.get(t);
      if (o instanceof double[] && ((double[]) o)[0] > tn) mk25 = ((double[]) o)[1];
    }
    double br25 = @PKG@.AbilStore.BREACH.isEmpty() ? 0.0 : breachPct(t, now);   // 0.1.25: Breach + Mark on one target = the higher + 5 (Skyy Q5)
    if (mk25 > 0.0 && br25 > 0.0) m = m * (1.0 + ((mk25 > br25 ? mk25 : br25) + @PKG@.AbilNum.EL_BREACHMARK) / 100.0);
    else if (mk25 > 0.0) m = m * (1.0 + mk25 / 100.0);
    else if (br25 > 0.0) m = m * (1.0 + br25 / 100.0);
    if (!@PKG@.AbilStore.SUNDER.isEmpty() || !@PKG@.AbilStore.SHOCKD.isEmpty() || !@PKG@.AbilStore.STAGD.isEmpty()) m = m * outMult3(acc, t, cu, now);   // 0.1.25
    if (!@PKG@.AbilStore.ROOTS.isEmpty()) {''')
rep('''                  "if ($5 != null && (!@PKG@.AbilStore.RAGE.isEmpty() || !@PKG@.AbilStore.FURY.isEmpty() || !@PKG@.AbilStore.WAR.isEmpty() || !@PKG@.AbilStore.GUARDED.isEmpty() "
                  "|| !@PKG@.AbilStore.MARKD.isEmpty() || !@PKG@.AbilStore.ROOTS.isEmpty() || !@PKG@.AbilStore.EXPL.isEmpty())) @PKG@.Abil.outHit2($1, $2, $3, $4, $5, System.currentTimeMillis()); }"))''',
    '''                  "if ($5 != null && (!@PKG@.AbilStore.RAGE.isEmpty() || !@PKG@.AbilStore.FURY.isEmpty() || !@PKG@.AbilStore.WAR.isEmpty() || !@PKG@.AbilStore.GUARDED.isEmpty() "
                  "|| !@PKG@.AbilStore.MARKD.isEmpty() || !@PKG@.AbilStore.ROOTS.isEmpty() || !@PKG@.AbilStore.EXPL.isEmpty() "
                  # 0.1.25: Breach / Sunder / Shock / Stagger (the target side) + the Spellblade's Imbue and Keen Edge (its own hook, first)
                  "|| !@PKG@.AbilStore.BREACH.isEmpty() || !@PKG@.AbilStore.SUNDER.isEmpty() || !@PKG@.AbilStore.SHOCKD.isEmpty() || !@PKG@.AbilStore.STAGD.isEmpty())) @PKG@.Abil.outHit2($1, $2, $3, $4, $5, System.currentTimeMillis()); "
                  "if ($5 != null && @PKG@.Abil.SB_LIVE) @PKG@.Abil.outHit3($1, $2, $3, $4, $5, System.currentTimeMillis()); }"))''')
rep('''      @PKG@.Abil.inHit2(st, buf, r, (@DMG@) ev, now);   // 0.1.24: Rallying Guard, Oath, the banner, Challenge, Presence, Retribution, Barbed Chain''',
    '''      @PKG@.Abil.inHit2(st, buf, r, (@DMG@) ev, now);   // 0.1.24: Rallying Guard, Oath, the banner, Challenge, Presence, Retribution, Barbed Chain
    if (!@PKG@.AbilStore.MOMS.isEmpty() || !@PKG@.AbilStore.SUNDER.isEmpty()) @PKG@.Abil.inHit3(st, buf, r, (@DMG@) ev, now);   // 0.1.25: Momentum, Unstoppable, Weakened''')
rep('''    if (!@PKG@.AbilStore.FRENZ.isEmpty() || !@PKG@.AbilStore.RAGE.isEmpty() || !@PKG@.AbilStore.BANNERS.isEmpty())
      @PKG@.Abil.hitLanded2(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);''',
    '''    if (!@PKG@.AbilStore.FRENZ.isEmpty() || !@PKG@.AbilStore.RAGE.isEmpty() || !@PKG@.AbilStore.BANNERS.isEmpty())
      @PKG@.Abil.hitLanded2(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);
    // 0.1.25: Spellblade Momentum, Imbue statuses, Tempest - only once a Spellblade was seen since the start
    if (@PKG@.Abil.SB_LIVE) @PKG@.Abil.hitLanded3(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);''')
rep('''    if ("Primary".equals(ty)) { if (!@PKG@.AbilStore.FRENZ.isEmpty()) @PKG@.Abil.onSwing(e, chunk.getReferenceTo(idx), buf, System.currentTimeMillis()); return; }   // 0.1.24 FIX ROUND: Blood Frenzy pays per swing, hit or miss''',
    '''    if ("Primary".equals(ty)) {
      if (!@PKG@.AbilStore.FRENZ.isEmpty()) @PKG@.Abil.onSwing(e, chunk.getReferenceTo(idx), buf, System.currentTimeMillis());   // 0.1.24 FIX ROUND: Blood Frenzy pays per swing, hit or miss
      if (!@PKG@.AbilStore.MOMX.isEmpty()) @PKG@.Abil.momSwing(e, chunk.getReferenceTo(idx), buf, System.currentTimeMillis());   // 0.1.25: the Spellblade's rhythm
      return;
    }''')
rep('''    try { runeTick((@PR@) po, u, r, acc, now); } catch (Throwable t1) { @PKG@.ClassCfg.warnLimited("the ability rune tick failed: " + t1); }''',
    '''    try { runeTick((@PR@) po, u, r, acc, now); } catch (Throwable t1) { @PKG@.ClassCfg.warnLimited("the ability rune tick failed: " + t1); }
    if (!@PKG@.AbilStore.MOMS.isEmpty() || !SB_LIVE) { try { momTick(r, acc, u, now); } catch (Throwable t2) { @PKG@.ClassCfg.warnLimited("the Momentum tick failed: " + t2); } }   // 0.1.25''')

# ================================================================================================ the HUD (Momentum), the imbue bridge, ClassQuit, /classadmin abil info, the plugin texts
rep('''    out[45] = Boolean.valueOf(@PKG@.AbilCfg.SHAPES);
    out[46] = "abil3";''', '''    out[45] = Boolean.valueOf(@PKG@.AbilCfg.SHAPES);
    out[46] = "abil3";
    out[47] = @PKG@.Abil.momText(u);   // 0.1.25: "Momentum 14 (Unstoppable)" or "" (SkyyHud draws it in a later round)''')
rep('''abfn = pool.makeClass(PKG + ".AbilFn")''', '''# 0.1.25: classes:fn:imbue (research/cloud/Element-System-Spec.md 11): apply(String uuid | UUID) -> "Fire;30" while that player's Imbue
# runs (element;% incl. Momentum), else null. Any thread, never throws. SkyyGear reads it for its element split (then publishes gear:imbue).
abimb = pool.makeClass(PKG + ".ImbueFn")
abimb.addInterface(pool.get("java.util.function.Function"))
C(abimb, "public ImbueFn() { }")
abfn = pool.makeClass(PKG + ".AbilFn")''')
rep('''# ---- AbilWorld.run (after Abil: it calls the executors) + AbilTick''', '''M(abimb, r"""
public Object apply(Object o) {
  try {
    java.util.UUID u = null;
    if (o instanceof java.util.UUID) u = (java.util.UUID) o;
    else if (o instanceof String) u = java.util.UUID.fromString(((String) o).trim());
    if (u == null) return null;
    if (@PKG@.ClassStore.classIndex(u) != @PKG@.Abil.sbCi()) return null;   // FIX 2 (critic): a pending Imbue never follows a switch to another class
    long now = System.currentTimeMillis();
    double[] imb = @PKG@.Abil.imbueOf(u, now);
    if (imb == null) return null;
    int n = @PKG@.Abil.momN(u, now);
    double pct = imb[2] * (1.0 + (double) n * @PKG@.AbilNum.MO_ELEMPERSTACK / 100.0);
    return @PKG@.Abil.ELN[(int) imb[1]] + ";" + @PKG@.AbilMath.fmt(pct);
  } catch (Throwable t) { return null; }
}""")
# ---- AbilWorld.run (after Abil: it calls the executors) + AbilTick''')
rep('''  b.put("rebirth:part:classes", new @PKG@.ClassRb());        // 0.1.23: the rebirth participant (SkyyRebirth's two-phase commit)''',
    '''  b.put("rebirth:part:classes", new @PKG@.ClassRb());        // 0.1.23: the rebirth participant (SkyyRebirth's two-phase commit)
  b.put("classes:fn:imbue", new @PKG@.ImbueFn());            // 0.1.25: the Spellblade's Imbue element (SkyyGear's element split, later)''')
rep('''  try { @PKG@.ClassCfg.bridge().remove("rebirth:part:classes"); } catch (Throwable t) { }   // 0.1.23''',
    '''  try { @PKG@.ClassCfg.bridge().remove("rebirth:part:classes"); } catch (Throwable t) { }   // 0.1.23
  try { @PKG@.ClassCfg.bridge().remove("classes:fn:imbue"); } catch (Throwable t) { }       // 0.1.25''')
rep('''          crb, abnum):                   # 0.1.23: + the rebirth participant, the Monk + Assassin numbers''',
    '''          crb, abnum,                    # 0.1.23: + the rebirth participant, the Monk + Assassin numbers
          abimb):                        # 0.1.25: + classes:fn:imbue''')
rep('''    @PKG@.AbilStore.PAID.remove(u);   // FIX ROUND: the swing-start cost record''', '''    @PKG@.AbilStore.PAID.remove(u);   // FIX ROUND: the swing-start cost record
    @PKG@.AbilStore.MOMS.remove(u);   // 0.1.25: the Spellblade's Momentum + Imbue end with the session
    @PKG@.AbilStore.MOMX.remove(u);
    @PKG@.AbilStore.IMBUE.remove(u);
    @PKG@.AbilStore.SBP.remove(u);    // FIX 2''')
rep('''" | last: " + LAST_WAR + " / " + LAST_BER + " / " + LAST_ARC, null);   // 0.1.24''',
    '''" | last: " + LAST_WAR + " / " + LAST_BER + " / " + LAST_ARC, null);   // 0.1.24
    send(pr, "Spellblade: " + momText(t) + " | Breached " + BREACHED + ", Sundered " + SUNDERED + ", imbues " + IMBUED + ", statuses " + STATUSES + ", Momentum +" + MOMGAIN + " / -" + MOMLOST + ", rifts " + RIFTS + ", shatters " + SHATTERS + ", attunes " + ATTUNES + " | rebirth slots " + rbSlots(@PKG@.ClassCfg.pkey(t)) + " | last: " + LAST_SB, null);   // 0.1.25''')
rep('''Archer Pinning Shot, Rapid Fire, Explosive Arrow, Arrow Rain or Hunter's Net; sprinting''',
    '''Archer Pinning Shot, Rapid Fire, Explosive Arrow, Arrow Rain or Hunter's Net; Spellblade Arcane Breach, Elemental Imbue, Sunder, Rift Cleave or Shattering Arc with Momentum and element statuses; sprinting''')
rep('''SkyWynn classes: Archer, Warrior, Mage, Berserker, Priest, Assassin, Monk.''', '''SkyWynn classes: Archer, Warrior, Mage, Berserker, Priest, Assassin, Monk, Spellblade.''')
rep('''Monk + Assassin + Warrior + Berserker + Archer abilities, rebirth participant rebirth:part:classes;''',
    '''Monk + Assassin + Warrior + Berserker + Archer + Spellblade abilities, rebirth participant rebirth:part:classes (+ rebirth modifier slots), classes:fn:imbue;''')

# ================================================================================================ done
assert s.count("registerCommand(") == REG0, "no new command"
assert s.count("registerSystem(") == SYS0, "no new system"
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote %s (%d changes, %d lines)" % (dst, len(CHANGES), s.count(LF)))
