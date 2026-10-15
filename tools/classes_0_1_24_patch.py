"""Derive SkyyClasses/build_skyyclasses_0.1.24.py from the generated 0.1.23 (the SET pin; the EDITED lineage: Skyy's edited 0.1.6 ->
classes_0_1_7_patch.py -> ... -> classes_0_1_23_patch.py -> 0.1.23; classes_0_1_6_patch.py is never re-run). 0.1.23 stays untouched; its
line endings are kept.
Run:  python tools/classes_0_1_24_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.24.py   (never --deploy)
Test: python SkyyClasses/test_skyyclasses_0.1.24.py [--dir <scratch>] [--keep]

0.1.24 (2026-10-14) = WARRIOR + BERSERKER + ARCHER ON THE RUNE FRAMEWORK (Skyy 2026-10-14 "Run the queue" - the queued round "Warrior,
Berserker and Archer abilities"; "Basically we are making our own runes and modifiers, then controlling them in the skill tree, instead of
the vanilla controller, to lock then per class. (If 2 of your abilities have echo modifier, the modifiers are unlocked and level separately
per ability"; popup M10 "Priest + Monk + Assassin, then Warrior + Berserker, then Archer"). Built on the 0.1.22 / 0.1.23 framework -
nothing forked: the 15 new abilities are rows of the same tables (one Server Setup text row "ab.<Ability>.numbers" each - the 64 KB
settings-class cap; their walking Mana / Stamina / cooldown live in that row too), the same pipeline (castAt0), jobs, zones and hooks.
Every class now has abilities, so vanilla runes are blocked for all of them (Skyy M2; abil.vanillaRunes unlocks them).
  THE 15 ABILITIES (research/classes/Warrior.md, Berserker.md, Archer.md, research/cloud/Class-Ability-Shapes.md 2 / 3 / 6,
    Class-Ability-Spec-Draft.md 2.1 / 2.2 / 2.5, docs/answered/classes.md - newest wins; costs = power x the class split,
    research/Class-Power-Split.md: Warrior 38 / 62, Berserker 23 / 77, Archer 43 / 57):
    Warrior  A1 Rallying Guard (5 + 2; 24 s): you + party within 10 + other players within 6 (picked at the cast) take 20 % less for 10 s;
             mobs within 8 turn on you for 6 s (MarkedEntitySupport target slots set to you - UNVERIFIED P12). Charge Rally (sprint: also
             every ally you pass within 4 blocks for 1.5 s, taunt 6), on landing (taunt 10), Hold the Line (crouch: taunt 16 for 6 s, only
             you take 10 % less). Echo (Skyy 2026-10-08, replaces Ward): the cut lingers 3 s at the echo strength, no second taunt.
             A2 Shield Shockwave (4 + 2; 12 s): a 6-block cone (90 degrees): 1.0 H + stun 1.5 s (the boss stun clock). Charging Slam
             (sprint: 2-block step, 7 blocks, 1.2 H, 1.2 s), Ground Pound (on landing: a 4-block ring, knock-up), Ring (crouch: 360
             degrees, 3 blocks, 0.8 H). Echo (replaces Slow): a weaker cone 1 s later, stun 0.5 s.
             A2-alt Iron Chain (5 + 2; 14 s): the enemy you look at within 15 blocks is dragged to you, 0.6 H, stun 1 s, the vanilla 0.7
             chain rune's Ability_Hooked effect (Skyy: "iron chain is already one of the runes in 0.7" - its look reused; the vanilla
             chain projectile + beam are client interactions our key cancels, so the hook is ours: an instant pull). Meet Halfway
             (sprint), Hook Down (air: yanked up), Anchor (crouch: 20 blocks, slower, stun 1.5 + root 1). Bosses are only dragged with Pull.
             A1-alt A Challenge (5 + 2; 20 s; Skyy 2026-10-08): the enemy you look at within 12 must fight you 8 s, you take 30 % less from
             it, 20 % of its hits reflect back. Charging Challenge (sprint: 2-block step, 6 s), on landing (nearest within 8), Duel
             (crouch: 10 s, 40 % / 30 %).
             A1-alt B Guardian's Oath (5 + 2; 22 s; Skyy 2026-10-08): link the party member you look at (else the most hurt) within 15
             for 8 s: 40 % of the damage they take goes to you (your own cut first), you take 15 % less while linked. Oath Rush (sprint:
             the nearest within 8 + 20 % speed 3 s), on landing (the most hurt), Shared Burden (crouch: 10 s, 50 %, you 25 % less).
    Berserker A1 Enrage (3 + 3; 30 s): players within 8 + party within 16 PICKED ONCE (Skyy L127: not an aura): +10 % -> +20 % damage over
             10 s, holds 5 s, ends; you double (+20 -> +40, cap 60). War Charge (sprint: + everyone you pass within 4 for 2 s), War Leap
             (on landing, ranges +2), Lone Rage (crouch: you only, peak +10 points, holds 8 s).
             A2 Whirlwind (3 + 2; 14 s): spin 3 s, everything within 3 blocks 0.5 H every 0.5 s, heals you 10 % of it. Cyclone Charge
             (sprint: 2.5 s, 2.5 blocks), Spinning Drop (on landing + a 1.0 H slam), Grinder (crouch: rooted, every 0.4 s, 3.5 blocks).
             Echo (Skyy L139): a weaker spin 1 s after the spin ends.
             A2-alt Earthsplitter (3 + 3; 12 s): a 12-block shockwave line, 2.0 H, knock-up; +1 % per 1 % Health missing (cap +50 %).
             Running Split (sprint: 16 blocks, narrower, 1.8 H), Crater (on landing: a 5-block ring), Fissure (crouch: 1 s wind-up, 8
             blocks, 2.4 H, slowed 2 s).
             A1-alt A Blood Frenzy (toggle; Skyy L129-L138): on (1 + 1) / off (free, then 10 s before it can go on again); every landed
             swing = 1 stack (max 25, each decays 6 s after it was gained), 0.7 Mana + 0.6 Stamina EVERY swing, hit or miss (L129; taken
             when the swing starts: the Primary InteractionChainStartEvent; a landed hit the start hook missed pays) + 0.15 + 0.1 a second (off
             when either runs out); per stack you +1.5 % damage, +0.5 % move speed (+1 % attack speed: shown only - no attack-speed door
             yet), allies in the AURA (players within 8, party within 16, only while inside) half. Charging Frenzy (sprint: 3 stacks),
             on landing (2 stacks), Blood Bank (crouch: half the stacks of the last run within 20 s, aura 6 / 12). Floor (Skyy L130): the
             stacks never fall below 5 (Lv 1) / 10 (Lv 2+) once reached, never with Duration+.
             A1-alt B Warlord's Banner (9 + 8; 40 s counted from the fall; Skyy L132-L135): a banner at your feet 30 s, 12 blocks: in range
             players +8 % damage + 8 % defence, party +12 %, you +16 % (+ attack speed: shown only); every mob killed in range +1 s
             (mini-boss +3, boss +5, total 60 s); it falls when its time ends or you leave its range. Vanguard Banner (sprint: 6 ahead),
             on landing (+2 blocks), Rooted Banner (crouch: 10 blocks, 40 s, leaving range only pauses YOUR buff). Echo: the buff lingers
             4 s at the echo strength on everyone who was in range. No banner model (P11): a particle column + ring at the spot.
    Archer   A1 Pinning Shot (4 + 1; 12 s): an arrow down your look (30 blocks, the first 2 enemies near the line): 1.2 H, Rooted 2 s (the
             vanilla Root; bosses slowed), Marked 6 s (+15 % damage taken from everyone; +1 a level to 25). Running Pin (sprint: 24
             blocks, root 2.5), Rain Pin (air: 3 arrows into a 3-block patch below you, 0.6 H each), Steady Aim (crouch: 40 blocks,
             +1 pierce, Mark 20, you stand still 0.5 s).
             A2 Rapid Fire (6 + 2; 20 s): 15 arrows in 3 s down your look (re-aimed every arrow), each 0.5 H. Running Fire (sprint: 12,
             spread), Hover Fire (air: slow fall while firing - UNVERIFIED feel), Braced (crouch: 15 in 2 s, +10 %, rooted). Seeker (Skyy
             2026-10-08): an arrow passing within 1 block (+0.5 a level) of an enemy hits it; never with Ricochet.
             A2-alt Explosive Arrow (5 + 2; 14 s): your next arrow hit within 15 s deals 2x and blasts 4 blocks (a stand-in for "your next
             CHARGED shot": the server cannot read the draw yet). Quick Fuse (sprint: 1.5x, 3 blocks), Mortar (air: 5 blocks + knock-up),
             Set Charge (crouch: sticks, blasts 1 s later at 2.5x). Echo (Skyy 2026-10-08, replaces Lingering): a weaker blast 1 s later.
             A1-alt A Arrow Rain (7 + 2; 20 s): a 6-block rain where you look for 3 s: 2.0 H in total per enemy, Slowed 30 %, still inside
             after 2 s: Rooted 1.5 s + Marked. Trailing Rain (sprint: 4 blocks behind you), Overhead Rain (air: below you, 7 blocks, no
             delay), Kneeling Volley (crouch: 1 s still, 8 blocks, 4 s, slow 40 %). Echo (Skyy 2026-10-08): a second shower right after.
             A1-alt B Hunter's Net (6 + 2; 18 s): a 4-block root zone where you look for 3 s, 0.5 H, Marked 8 s (10 %). Snare Line (sprint:
             a 2 x 6 strip behind you), Drop Net (air: below you, 5 blocks, 3.5 s), Set Trap (crouch: at your feet, arms after 1 s,
             springs when an enemy steps in, 20 s).
  DAMAGE SCALING (Enrage, Blood Frenzy, the banner, Marked, Aegis Core, Lasting Roots, Grand Trapper): one multiplier (Abil.outMult) on
    every weapon hit (DamageLock's outHook, players' hits on NPCs) and every ability hit (Abil.hit) - no effect assets; defence (the
    banner, Rallying Guard, Challenge, Oath) in the player damage hook after armour (Abil.inHit2, AbilShieldSys).
  MODIFIERS (Skyy M8, per ability, unlocked + levelled separately per ability): four new ones in the shared table - Pull, Leech, Floor,
    Seeker; Floor never pairs with Duration+, Seeker never with Ricochet (AbilModDefs.excl, refused at equip, ignored if a file holds both).
    Rallying Guard Duration+ Radius+ Power+ Echo; Shield Shockwave Radius+ Knockback+ Echo Power+; Iron Chain Pull Chain Slow Power+;
    Challenge Duration+ Power+ Chain Ward; Guardian's Oath Duration+ Power+ Radius+ Ward; Enrage Duration+ Radius+ Power+ Leech; Whirlwind
    Duration+ Radius+ Pull Leech Echo; Earthsplitter Power+ Split Slow Knockback+; Blood Frenzy Duration+ Floor Power+ Leech Haste;
    Warlord's Banner Radius+ Duration+ Power+ Ward Echo; Pinning Shot Pierce Split Duration+ Power+; Rapid Fire Ricochet Pierce Duration+
    Slow Seeker; Explosive Arrow Radius+ Split Knockback+ Echo; Arrow Rain Radius+ Duration+ Lingering Power+ Echo; Hunter's Net Radius+
    Duration+ Pull Split.
  RUNES: 15 more hidden rune items SkyyAbility_Warrior_* / _Berserker_* / _Archer_* (the 0.1.22 rune shape, our own icons from
    art/ability-icons; Challenge + Guardian's Oath have no art yet - STAND-IN icons Unbreakable / BulwarkStance until the art round).
  THE CLASS TREE (SkyyTrees 0.3.9 lists the Warrior / Berserker / Archer A / M nodes): path nodes applied (Class-Tree-Paths.md 1 / 2 / 5):
    Warrior T1 Shield Training (Shockwave stun +0.25 s; the blocking half is not ours), T6 Veteran, PA1 Shield Wall (party radius +2, the
    guarded cannot be knocked back, your own cut -4), PA2 Interpose (allies with you between them and the attacker take 25 % less; you
    -10 % speed), PA5 Aegis Core (+3 s, the guarded party heals 3 % a second, your damage -15 %), PB1 Thorns of Command, PB2 Battle Cry,
    PB3 Barbed Chain, PB4 Retribution, PB5 Presence, PC4 Shockwave Surge; Berserker T4 Rage Reserve, T6 Unyielding, PA1 War Horn, PA3
    Banner Bearer, PA4 Rally, PA5 Warbringer, PB2 Bleed, PB3 Crimson Frenzy, PB4 Blood Pact, PC2 Seismic, PC3 Staggering Spin, PC4 Ground
    Pound; Archer PA1 Lasting Roots, PA2 Trap Arrows, PA3 Deep Net, PA4 Marksman's Snare, PA5 Grand Trapper, PB1 Far Sight, PB2 Focus Mark,
    PB3 Deadeye (crit = x1.5 = abil.critStand), PB4 Piercing Aim, PC1 Wide Volley, PC2 Chain Reaction, PC3 Quick Hands, PC4 Storm Cloud,
    PC5 Arrow Tempest. WAITING (not listed): Warrior PA3 "Guardian's Oath" (the node shares the A1-alt B's name - Skyy's call), PA4
    Bastion (Bulwark Stance is parked), PC2 Last Stand (Unbreakable was dropped); Berserker PA2 Shared Fury (the live text vs the proposed
    rage swap - Skyy's call); every L / G / A / X node (other mods).
  SHIELDS = WARRIOR ONLY (Skyy 2026-10-08 "shields warrior only"): Weapon_Shield_ leaves FREE_WEAPONS and becomes a Warrior weapon (the
    class lock: another class holding a shield in either hand deals no damage, "Only Warriors can use shields"). The kit shield step is
    unchanged (the Warrior kit's Wood Shield still goes into the off-hand).
  Saved data: abilities/<pkey>.properties gains u.<Id> / e.<Id> / m.<Id>.<Mod> lines for the new abilities (the 0.1.22 keys) - an older jar
    ignores them. No migration. ClassRb (rebirth:part:classes) is unchanged - it walks every ability of the class.
  FIX ROUND (critics 2026-10-14): Blood Frenzy pays per SWING hit or miss (above; tools are not attacks); a world switch (PlayerReadyEvent)
    ends the caster's Blood Frenzy (banked, a line) and Warlord's Banner (falls, its cooldown starts, a line) unless the arrival world holds
    them - before, a frenzy left in a world nobody ticks (a solo island after /hub) stayed "on"; a kill only feeds a banner of its own world
    (AbilWorld.holds); the frenzy bank is written only while that frenzy was the live one (no re-add after a quit).
  FIX ROUND 2 (critics 2026-10-14): Shield Shockwave needs a shield in the main hand or the off-hand (utility) slot - refused with a line
    before anything is paid; Explosive Arrow's blast gets the RAW arrow damage (each blast hit applies its own Enrage / Frenzy / banner /
    Mark multiplier - before, neighbours got it twice); a quit ends the Warlord's Banner without arming its cooldown (a relog finds it
    ready); the Blood Bank stacks are keyed by the profile key (PROFILES-CONTRACT rule 2); a swing-start Frenzy payment covers ONE landed
    swing (consumed) - a swing the start hook missed pays on its hit.
  ROLLBACK to 0.1.23: abil.runeHud off + one login of every Warrior / Berserker / Archer first (their runes leave the ability slots), else
    those rune items stay as dead items in the AbilitySlots until removed by hand; their abilities simply stop; shields are free again.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.23.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.24.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.23"' in s and "GENERATED by tools/classes_0_1_23_patch.py from the generated 0.1.22" in s, \
    "build_skyyclasses_0.1.23.py is not the generated 0.1.23"
assert "RallyingGuard" not in s and "inHit2" not in s
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
NOTE = HEAD[HEAD.index("0.1.24 (2026-10-14)"):].rstrip()

# ================================================================================================ docstring, version
rep('''"""SkyyClasses 0.1.23 - build script (javassist via jpype). GENERATED by tools/classes_0_1_23_patch.py from the generated 0.1.22 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_22_patch.py -> 0.1.22) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.24 - build script (javassist via jpype). GENERATED by tools/classes_0_1_24_patch.py from the generated 0.1.23 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_23_patch.py -> 0.1.23) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''' + NOTE.replace(LF, LF + "  ").replace("  " + LF, LF) + '''
  Notes in tools/classes_0_1_24_patch.py. CHECKED with SkyyClasses/test_skyyclasses_0.1.24.py.
=== 0.1.23 (history; still true unless 0.1.24 above says otherwise) ===
''')
rep('VERSION = "0.1.23"', 'VERSION = "0.1.24"')

# ================================================================================================ SHIELDS = WARRIOR ONLY (Skyy 2026-10-08)
rep('''     "weapons": [("Weapon_Sword_", "swords"), ("Weapon_Longsword_", "longswords"), ("Weapon_Spear_", "spears")],
     # 0.1.10 (LOCKED Skyy 2026-10-01): + a Wood Shield - it goes into the off-hand when that is empty (Kit.offhand)
     "weapon_text": "Swords / Longswords / Spears", "kit": "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1"},''',
    '''     # 0.1.24 (LOCKED Skyy 2026-10-08 "shields warrior only"): shields are a Warrior weapon (they left FREE_WEAPONS)
     "weapons": [("Weapon_Sword_", "swords"), ("Weapon_Longsword_", "longswords"), ("Weapon_Spear_", "spears"), ("Weapon_Shield_", "shields")],
     # 0.1.10 (LOCKED Skyy 2026-10-01): + a Wood Shield - it goes into the off-hand when that is empty (Kit.offhand)
     "weapon_text": "Swords / Longswords / Spears / Shields", "kit": "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1"},''')
rep('''FREE_WEAPONS = [("Weapon_Shield_", "shields")]''',
    '''FREE_WEAPONS = []   # 0.1.24 (Skyy 2026-10-08 "shields warrior only"): shields moved to the Warrior; class:weapons:free is empty now''')
rep('''print("  %-25s %3d items (%s)" % ("free (shields)", len([i for i in _by_owner.get(FREE, []) if i.startswith("Weapon_Shield_")]), "usable by all"))''',
    '''print("  %-25s %3d items (%s)" % ("shields (0.1.24)", len([i for i in _real if i.startswith("Weapon_Shield_")]), "Warrior only"))''')
rep('''assert (OFFHAND_PREFIX, "shields") in FREE_WEAPONS and classify("Weapon_Shield_Wood")[0] == FREE, "shields must stay free for every class"''',
    '''WARRIOR_I24 = [i for i, c in enumerate(CLASSES) if c["name"] == "Warrior"][0]
assert not FREE_WEAPONS and all(classify(i) == (WARRIOR_I24, "shields") for i in _real if i.startswith(OFFHAND_PREFIX)), \\
    "0.1.24: every shield is a Warrior weapon (Skyy 2026-10-08 'shields warrior only')"''')

# ================================================================================================ the ability table
NEW2 = [("RallyingGuard", "Rallying Guard", "Warrior", 0), ("ShieldShockwave", "Shield Shockwave", "Warrior", 1),
        ("IronChain", "Iron Chain", "Warrior", 2), ("Challenge", "Challenge", "Warrior", 3), ("GuardiansOath", "Guardian's Oath", "Warrior", 4),
        ("Enrage", "Enrage", "Berserker", 0), ("Whirlwind", "Whirlwind", "Berserker", 1), ("Earthsplitter", "Earthsplitter", "Berserker", 2),
        ("BloodFrenzy", "Blood Frenzy", "Berserker", 3), ("WarlordsBanner", "Warlord's Banner", "Berserker", 4),
        ("PinningShot", "Pinning Shot", "Archer", 0), ("RapidFire", "Rapid Fire", "Archer", 1), ("ExplosiveArrow", "Explosive Arrow", "Archer", 2),
        ("ArrowRain", "Arrow Rain", "Archer", 3), ("HuntersNet", "Hunter's Net", "Archer", 4)]
NEW2_IDS = [a[0] for a in NEW2]
rep('''    ("VanishingAct", "Vanishing Act", "Assassin", 3, True, False),
]
assert sorted((c, t) for _i, _n, c, t, _b, _p in ABILS) == sorted([(c, t) for c in ("Mage", "Priest", "Monk") for t in range(5)] + [("Assassin", t) for t in range(4)])''',
    '''    ("VanishingAct", "Vanishing Act", "Assassin", 3, True, False),
    # 0.1.24: Warrior + Berserker + Archer (research/classes/Warrior.md, Berserker.md, Archer.md; newest wins)
''' + "".join('    (%r, %r, %r, %d, True, False),\n' % a for a in NEW2) + ''']
assert sorted((c, t) for _i, _n, c, t, _b, _p in ABILS) == sorted([(c, t) for c in ("Mage", "Priest", "Monk", "Warrior", "Berserker", "Archer") for t in range(5)] + [("Assassin", t) for t in range(4)])''')

# ================================================================================================ costs per shape (the split)
# id -> (prefix, category, [(power, cooldown) walk, sprint, air, crouch]); the plan = power x the class split (asserted by the build)
POW2 = [("RallyingGuard", "RG", "abilwba", [(12, 24), (12, 24), (12, 24), (8, 18)]),
        ("ShieldShockwave", "SS", "abilwba", [(10, 12), (12, 12), (10, 14), (10, 10)]),
        ("IronChain", "IC", "abilwba", [(12, 14), (12, 14), (12, 16), (12, 16)]),
        ("Challenge", "CH", "abilwba", [(12, 20), (12, 20), (12, 22), (16, 24)]),
        ("GuardiansOath", "GO", "abilwba", [(12, 22), (12, 22), (12, 22), (16, 26)]),
        ("Enrage", "EN", "abilwba", [(14, 30), (14, 30), (14, 30), (10, 26)]),
        ("Whirlwind", "WW", "abilwba", [(12, 14), (12, 14), (12, 16), (12, 16)]),
        ("Earthsplitter", "ES", "abilwba", [(14, 12), (14, 12), (14, 14), (16, 14)]),
        ("BloodFrenzy", "BF", "abilwba", [(4, 10), (4, 10), (4, 10), (4, 10)]),
        ("WarlordsBanner", "WB", "abilwba", [(40, 40), (40, 40), (40, 40), (45, 40)]),
        ("PinningShot", "PN", "abilwba", [(10, 12), (10, 12), (12, 12), (10, 14)]),
        ("RapidFire", "RF", "abilwba", [(14, 20), (14, 20), (16, 20), (14, 22)]),
        ("ExplosiveArrow", "EA", "abilwba", [(12, 14), (10, 12), (12, 16), (12, 16)]),
        ("ArrowRain", "AR", "abilwba", [(16, 20), (16, 20), (16, 22), (20, 24)]),
        ("HuntersNet", "HN", "abilwba", [(14, 18), (14, 18), (14, 20), (12, 18)])]
PLAN2 = {"RallyingGuard": [(5, 2, 24), (5, 2, 24), (5, 2, 24), (3, 1, 18)], "ShieldShockwave": [(4, 2, 12), (5, 2, 12), (4, 2, 14), (4, 2, 10)],
         "IronChain": [(5, 2, 14), (5, 2, 14), (5, 2, 16), (5, 2, 16)], "Challenge": [(5, 2, 20), (5, 2, 20), (5, 2, 22), (6, 2, 24)],
         "GuardiansOath": [(5, 2, 22), (5, 2, 22), (5, 2, 22), (6, 2, 26)], "Enrage": [(3, 3, 30), (3, 3, 30), (3, 3, 30), (2, 2, 26)],
         "Whirlwind": [(3, 2, 14), (3, 2, 14), (3, 2, 16), (3, 2, 16)], "Earthsplitter": [(3, 3, 12), (3, 3, 12), (3, 3, 14), (4, 3, 14)],
         "BloodFrenzy": [(1, 1, 10)] * 4, "WarlordsBanner": [(9, 8, 40), (9, 8, 40), (9, 8, 40), (10, 9, 40)],
         "PinningShot": [(4, 1, 12), (4, 1, 12), (5, 2, 12), (4, 1, 14)], "RapidFire": [(6, 2, 20), (6, 2, 20), (7, 2, 20), (6, 2, 22)],
         "ExplosiveArrow": [(5, 2, 14), (4, 1, 12), (5, 2, 16), (5, 2, 16)], "ArrowRain": [(7, 2, 20), (7, 2, 20), (7, 2, 22), (9, 3, 24)],
         "HuntersNet": [(6, 2, 18), (6, 2, 18), (6, 2, 20), (5, 2, 18)]}
SNAMES2 = {"RallyingGuard": ["Rallying Guard", "Charge Rally", "Rally on Landing", "Hold the Line"],
           "ShieldShockwave": ["Shield Shockwave", "Charging Slam", "Ground Pound", "Ring"],
           "IronChain": ["Iron Chain", "Meet Halfway", "Hook Down", "Anchor"],
           "Challenge": ["Challenge", "Charging Challenge", "Challenge from Above", "Duel"],
           "GuardiansOath": ["Guardian's Oath", "Oath Rush", "Oath on Landing", "Shared Burden"],
           "Enrage": ["Enrage", "War Charge", "War Leap", "Lone Rage"],
           "Whirlwind": ["Whirlwind", "Cyclone Charge", "Spinning Drop", "Grinder"],
           "Earthsplitter": ["Earthsplitter", "Running Split", "Crater", "Fissure"],
           "BloodFrenzy": ["Blood Frenzy", "Charging Frenzy", "Landing Frenzy", "Blood Bank"],
           "WarlordsBanner": ["Warlord's Banner", "Vanguard Banner", "Landing Banner", "Rooted Banner"],
           "PinningShot": ["Pinning Shot", "Running Pin", "Rain Pin", "Steady Aim"],
           "RapidFire": ["Rapid Fire", "Running Fire", "Hover Fire", "Braced"],
           "ExplosiveArrow": ["Explosive Arrow", "Quick Fuse", "Mortar", "Set Charge"],
           "ArrowRain": ["Arrow Rain", "Trailing Rain", "Overhead Rain", "Kneeling Volley"],
           "HuntersNet": ["Hunter's Net", "Snare Line", "Drop Net", "Set Trap"]}
rep('''    ("VanishingAct", "VA", "abilas", [(16, 28), (16, 28), (16, 28), (16, 30)]),
]''', '''    ("VanishingAct", "VA", "abilas", [(16, 28), (16, 28), (16, 28), (16, 30)]),
    # 0.1.24 (research/cloud/Class-Ability-Shapes.md 2 / 3 / 6: the old Mana-only power numbers x the 2026-10-08 split; Challenge +
    # Guardian's Oath have no shape table yet - power 12 like Iron Chain, the crouch shape 16)
''' + "".join("    (%r, %r, %r, %r),\n" % p for p in POW2) + ''']''')
rep('''    "VanishingAct": ["Vanishing Act", "Smoke Trail", "Smoke Drop", "Ambush Smoke"],
}''', '''    "VanishingAct": ["Vanishing Act", "Smoke Trail", "Smoke Drop", "Ambush Smoke"],
''' + "".join("    %r: %r,\n" % (k, SNAMES2[k]) for k in NEW2_IDS) + '''}''')
rep('''    "VanishingAct": [(7, 2, 28), (7, 2, 28), (7, 2, 28), (7, 2, 30)],
}
_SPLIT = {"Mage": (0.78, 0.22), "Priest": (0.73, 0.27), "Monk": (0.38, 0.62), "Assassin": (0.43, 0.57)}   # 0.1.23: + Monk, Assassin''',
    '''    "VanishingAct": [(7, 2, 28), (7, 2, 28), (7, 2, 28), (7, 2, 30)],
    # 0.1.24: research/cloud/Class-Ability-Spec-Draft.md 2.1 / 2.2 / 2.5 (Warrior 38 / 62, Berserker 23 / 77, Archer 43 / 57)
''' + "".join("    %r: %r,\n" % (k, PLAN2[k]) for k in NEW2_IDS) + '''}
_SPLIT = {"Mage": (0.78, 0.22), "Priest": (0.73, 0.27), "Monk": (0.38, 0.62), "Assassin": (0.43, 0.57),   # 0.1.23: + Monk, Assassin
          "Warrior": (0.38, 0.62), "Berserker": (0.23, 0.77), "Archer": (0.43, 0.57)}                     # 0.1.24''')
# 0.1.24: NO walking rows for the 15 (the CfgRows static initialiser was at 60.7 KB of 64 KB): their walking Mana / Stamina / cooldown are
# keys of their numbers text row (AbilNum.<P>_MANA / _STAM / _CD); every other shape follows the walking numbers (AbilDefs.scale / shift)
rep('''        if _k > 0 and _id in NEW_ABIL_IDS:
            continue          # 0.1.23: the walking rows only (the 64 KB cap) - the other shapes follow them (AbilDefs.scale)''',
    '''        if _k > 0 and _id in NEW_ABIL_IDS:
            continue          # 0.1.23: the walking rows only (the 64 KB cap) - the other shapes follow them (AbilDefs.scale)
        if _id in NEW2_IDS:
            continue          # 0.1.24: no rows at all (the 64 KB cap) - the walking numbers are keys of ab.<Ability>.numbers''')
rep('''NEW_ABIL_IDS = ['FlowingForm', ''', '''NEW2_IDS = %r   # 0.1.24: costs + cooldown in their numbers row (AbilNum)
NEW_ABIL_IDS = ['FlowingForm', ''' % NEW2_IDS)
rep('''        if _id in NEW_ABIL_IDS:   # 0.1.23: the walking row + the plan's shape numbers (scaled / shifted with it)
            _pk = PLAN_43[_id]
            _ix = {"MANA": 0, "STAM": 1, "CD": 2}[kind]
            if kind == "CD":
                _l.append("  if (ai == %d) { double w = @PKG@.AbilCfg.%s_CD; if (sh == 1) return shift(w, %r); if (sh == 2) return shift(w, %r); if (sh == 3) return shift(w, %r); return w; }"
                          % (_i, _p, float(_pk[1][2] - _pk[0][2]), float(_pk[2][2] - _pk[0][2]), float(_pk[3][2] - _pk[0][2])))
            else:
                _l.append("  if (ai == %d) { double w = @PKG@.AbilCfg.%s_%s; if (sh == 1) return scale(w, %r, %r); if (sh == 2) return scale(w, %r, %r); if (sh == 3) return scale(w, %r, %r); return w; }"
                          % (_i, _p, kind, float(_pk[0][_ix]), float(_pk[1][_ix]), float(_pk[0][_ix]), float(_pk[2][_ix]), float(_pk[0][_ix]), float(_pk[3][_ix])))
            continue''', '''        if _id in NEW_ABIL_IDS or _id in NEW2_IDS:   # 0.1.23: the walking row + the plan's shape numbers (scaled / shifted with it)
            _pk = PLAN_43[_id]
            _ix = {"MANA": 0, "STAM": 1, "CD": 2}[kind]
            _cl = "AbilNum" if _id in NEW2_IDS else "AbilCfg"   # 0.1.24: the walking numbers of the 15 live in AbilNum
            if kind == "CD":
                _l.append("  if (ai == %d) { double w = @PKG@.%s.%s_CD; if (sh == 1) return shift(w, %r); if (sh == 2) return shift(w, %r); if (sh == 3) return shift(w, %r); return w; }"
                          % (_i, _cl, _p, float(_pk[1][2] - _pk[0][2]), float(_pk[2][2] - _pk[0][2]), float(_pk[3][2] - _pk[0][2])))
            else:
                _l.append("  if (ai == %d) { double w = @PKG@.%s.%s_%s; if (sh == 1) return scale(w, %r, %r); if (sh == 2) return scale(w, %r, %r); if (sh == 3) return scale(w, %r, %r); return w; }"
                          % (_i, _cl, _p, kind, float(_pk[0][_ix]), float(_pk[1][_ix]), float(_pk[0][_ix]), float(_pk[2][_ix]), float(_pk[0][_ix]), float(_pk[3][_ix])))
            continue''')

# ================================================================================================ the numbers rows of the 15 (AbilNum)
NUM2 = {
    # WARRIOR (research/cloud/Class-Ability-Spec-Draft.md 2.1 + docs/answered/classes.md 2026-10-08 L163 / L166 / L168)
    "RallyingGuard": ("RG", "abilwba", [("mana", 5.0), ("stamina", 2.0), ("cooldown", 24.0), ("time", 10.0), ("cut", 20.0), ("cutCap", 40.0),
                      ("party", 10.0), ("players", 6.0), ("taunt", 8.0), ("tauntTime", 6.0), ("chargeTime", 1.5), ("chargeRadius", 4.0),
                      ("chargeTaunt", 6.0), ("landTaunt", 10.0), ("holdTaunt", 16.0), ("holdTime", 6.0), ("holdCut", 10.0), ("echoTime", 3.0)]),
    "ShieldShockwave": ("SS", "abilwba", [("mana", 4.0), ("stamina", 2.0), ("cooldown", 12.0), ("range", 6.0), ("angle", 45.0), ("power", 1.0),
                        ("stun", 1.5), ("stunLevel", 0.03), ("step", 2.0), ("sprintRange", 7.0), ("sprintPower", 1.2), ("sprintStun", 1.2),
                        ("poundRadius", 4.0), ("poundStun", 1.5), ("poundUp", 4.0), ("ringRadius", 3.0), ("ringPower", 0.8), ("echoStun", 0.5),
                        ("retriPct", 20.0), ("retriGap", 20.0)]),
    "IronChain": ("IC", "abilwba", [("mana", 5.0), ("stamina", 2.0), ("cooldown", 14.0), ("range", 15.0), ("power", 0.6), ("stun", 1.0),
                  ("meetStun", 0.8), ("hookPower", 0.8), ("hookUp", 6.0), ("anchorRange", 20.0), ("anchorStun", 1.5), ("anchorRoot", 1.0),
                  ("anchorPull", 60.0), ("chainRange", 4.0), ("barbed", 25.0), ("barbedTime", 5.0)]),
    "Challenge": ("CH", "abilwba", [("mana", 5.0), ("stamina", 2.0), ("cooldown", 20.0), ("range", 12.0), ("time", 8.0), ("cut", 30.0),
                  ("reflect", 20.0), ("step", 2.0), ("sprintTime", 6.0), ("landRadius", 8.0), ("duelTime", 10.0), ("duelCut", 40.0),
                  ("duelReflect", 30.0), ("chainRange", 4.0)]),
    "GuardiansOath": ("GO", "abilwba", [("mana", 5.0), ("stamina", 2.0), ("cooldown", 22.0), ("range", 15.0), ("time", 8.0), ("share", 40.0),
                      ("cut", 15.0), ("rushRange", 8.0), ("rushSpeed", 20.0), ("burdenTime", 10.0), ("burdenShare", 50.0),
                      ("burdenCut", 25.0), ("leash", 30.0)]),
    # BERSERKER (2.5 + L127-L139)
    "Enrage": ("EN", "abilwba", [("mana", 3.0), ("stamina", 3.0), ("cooldown", 30.0), ("grow", 10.0), ("hold", 5.0), ("start", 10.0),
               ("peak", 20.0), ("selfMult", 2.0), ("selfCap", 60.0), ("players", 8.0), ("party", 16.0), ("chargeTime", 2.0),
               ("chargeRadius", 4.0), ("leapAdd", 2.0), ("loneBonus", 10.0), ("loneHold", 8.0), ("hornDelay", 3.0), ("hornStart", 15.0),
               ("rallyShield", 10.0), ("fade", 3.0)]),
    "Whirlwind": ("WW", "abilwba", [("mana", 3.0), ("stamina", 2.0), ("cooldown", 14.0), ("time", 3.0), ("radius", 3.0), ("every", 0.5),
                  ("power", 0.5), ("heal", 10.0), ("sprintTime", 2.5), ("sprintRadius", 2.5), ("dropPower", 1.0), ("grindEvery", 0.4),
                  ("grindRadius", 3.5), ("bleed", 0.2), ("bleedTime", 4.0)]),
    "Earthsplitter": ("ES", "abilwba", [("mana", 3.0), ("stamina", 3.0), ("cooldown", 12.0), ("length", 12.0), ("width", 2.0), ("power", 2.0),
                      ("up", 3.0), ("missingCap", 50.0), ("sprintLength", 16.0), ("sprintWidth", 1.4), ("sprintPower", 1.8),
                      ("craterRadius", 5.0), ("wind", 1.0), ("fissureLength", 8.0), ("fissurePower", 2.4), ("fissureSlow", 2.0),
                      ("splitAngle", 20.0), ("poundRadius", 2.5), ("poundPower", 1.5), ("pactCost", 10.0), ("pactBonus", 30.0)]),
    "BloodFrenzy": ("BF", "abilwba", [("mana", 1.0), ("stamina", 1.0), ("cooldown", 10.0), ("hitMana", 0.7), ("hitStam", 0.6),
                    ("drainMana", 0.15), ("drainStam", 0.1), ("max", 25.0), ("decay", 6.0), ("dmg", 1.5), ("move", 0.5), ("ally", 50.0),
                    ("players", 8.0), ("party", 16.0), ("chargeStacks", 3.0), ("landStacks", 2.0), ("bankWindow", 20.0),
                    ("bankShare", 50.0), ("bankPlayers", 6.0), ("bankParty", 12.0), ("hasteAt", 10.0), ("hasteSpeed", 10.0),
                    ("countAt", 10.0)]),
    "WarlordsBanner": ("WB", "abilwba", [("mana", 9.0), ("stamina", 8.0), ("cooldown", 40.0), ("time", 30.0), ("radius", 12.0),
                       ("players", 8.0), ("party", 12.0), ("self", 16.0), ("killAdd", 1.0), ("miniAdd", 3.0), ("bossAdd", 5.0),
                       ("cap", 60.0), ("ahead", 6.0), ("landAdd", 2.0), ("rootedRadius", 10.0), ("rootedTime", 40.0), ("echoTime", 4.0),
                       ("bearerHeal", 1.0), ("bearerTime", 25.0)]),
    # ARCHER (2.2 + L170 / L171)
    "PinningShot": ("PN", "abilwba", [("mana", 4.0), ("stamina", 1.0), ("cooldown", 12.0), ("range", 30.0), ("pierce", 2.0), ("power", 1.2),
                    ("root", 2.0), ("mark", 15.0), ("markCap", 25.0), ("markTime", 6.0), ("width", 0.8), ("sprintRange", 24.0),
                    ("sprintRoot", 2.5), ("rainPower", 0.6), ("rainRadius", 3.0), ("steadyRange", 40.0), ("steadyMark", 20.0),
                    ("steadyStill", 0.5), ("farRange", 45.0), ("trapRoot", 2.0), ("trapLife", 8.0)]),
    "RapidFire": ("RF", "abilwba", [("mana", 6.0), ("stamina", 2.0), ("cooldown", 20.0), ("arrows", 15.0), ("time", 3.0), ("power", 0.5),
                  ("range", 30.0), ("width", 0.6), ("sprintArrows", 12.0), ("spread", 8.0), ("hoverTime", 2.5), ("hoverFall", 1.0),
                  ("bracedTime", 2.0), ("bracedBonus", 10.0), ("bounce", 6.0), ("focusEvery", 0.4), ("focusBonus", 25.0)]),
    "ExplosiveArrow": ("EA", "abilwba", [("mana", 5.0), ("stamina", 2.0), ("cooldown", 14.0), ("window", 15.0), ("mult", 2.0), ("radius", 4.0),
                       ("quickMult", 1.5), ("quickRadius", 3.0), ("mortarRadius", 5.0), ("mortarUp", 4.0), ("setDelay", 1.0),
                       ("setMult", 2.5), ("burnTime", 3.0), ("burnPower", 0.2)]),
    "ArrowRain": ("AR", "abilwba", [("mana", 7.0), ("stamina", 2.0), ("cooldown", 20.0), ("range", 25.0), ("radius", 6.0), ("time", 3.0),
                  ("power", 2.0), ("slow", 30.0), ("rootAfter", 2.0), ("root", 1.5), ("mark", 15.0), ("markTime", 6.0), ("behind", 4.0),
                  ("overRadius", 7.0), ("delay", 0.5), ("volleyRadius", 8.0), ("volleyTime", 4.0), ("volleySlow", 40.0),
                  ("volleyWind", 1.0)]),
    "HuntersNet": ("HN", "abilwba", [("mana", 6.0), ("stamina", 2.0), ("cooldown", 18.0), ("range", 20.0), ("radius", 4.0), ("time", 3.0),
                   ("power", 0.5), ("mark", 10.0), ("markTime", 8.0), ("stripLength", 6.0), ("stripWidth", 2.0), ("dropRadius", 5.0),
                   ("dropTime", 3.5), ("trapArm", 1.0), ("trapLife", 20.0), ("trapRadius", 3.0), ("pull", 4.0)]),
}
assert sorted(NUM2) == sorted(NEW2_IDS)
for _aid in NEW2_IDS:
    _pk = PLAN2[_aid][0]
    _kv = dict(NUM2[_aid][2])
    assert (_kv["mana"], _kv["stamina"], _kv["cooldown"]) == tuple(float(x) for x in _pk), "%s: the walking numbers = the plan" % _aid


def _fld(pre, key):
    """the AbilNum field of a numbers key: RG + cutCap -> RG_CUTCAP; mana / stamina / cooldown -> _MANA / _STAM / _CD (AbilDefs reads them)"""
    return pre + "_" + {"mana": "MANA", "stamina": "STAM", "cooldown": "CD"}.get(key, key.upper())


_NL2 = []
for _aid in NEW2_IDS:
    _pre, _cat, _kvs = NUM2[_aid]
    for _k, _v in _kvs:
        _hi = "1000" if _k == "mana" else ("100" if _k == "stamina" else ("600" if _k == "cooldown" else "10000"))
        _NL2.append('_n("ab.%s.%s", "%s", "dec", %r, "0", "%s", "", "%s", "%s", "%s")' % (_aid, _k, _fld(_pre, _k), float(_v), _hi, _cat, _k, _k))
rep('''# the text rows (one per ability, in ABILS order) + the AbilNum fields they fill''',
    '''# 0.1.24: WARRIOR + BERSERKER + ARCHER (research/cloud/Class-Ability-Spec-Draft.md 2.1 / 2.2 / 2.5, Class-Ability-Shapes.md 2 / 3 / 6;
# mana / stamina / cooldown = the WALKING shape (no ab.<Ability>.walk.* rows: the 64 KB cap); every number a key of ab.<Ability>.numbers)
''' + "\n".join(_NL2) + '''
# the text rows (one per ability, in ABILS order) + the AbilNum fields they fill''')
rep('''assert sorted(NUM_ABILS) == sorted(["FlowingForm", "HundredFists", "StillWater", "PalmStrike", "CycloneKick", "CloakFirstStrike", "Toxin", "GodKiller", "VanishingAct"])''',
    '''assert sorted(NUM_ABILS) == sorted(["FlowingForm", "HundredFists", "StillWater", "PalmStrike", "CycloneKick", "CloakFirstStrike", "Toxin", "GodKiller", "VanishingAct"]
                                  + %r)   # 0.1.24''' % NEW2_IDS)
rep('''    _r("ab.%s.numbers" % _aid, "%s_NUMS" % _pre, "text", NUM_TEXT[_aid], "", "400", "", _rs[0][7], (_nm + " numbers")[:40],
       "key=value: time s, radius/range blocks, speed/slow/weaken %, power x one hit; no key = its default")''',
    '''    _r("ab.%s.numbers" % _aid, "%s_NUMS" % _pre, "text", NUM_TEXT[_aid], "", "400", "", _rs[0][7], (_nm + " numbers")[:40],
       ("key=value: time s, radius/range blocks, speed/slow/weaken %, power x one hit; no key = its default" if _aid not in NEW2_IDS else
        "key=value: mana stamina cooldown = walking cost; s, blocks, %, power x one hit; no key = default"))''')
rep('''            ("abilmk", "Monk abilities"), ("abilas", "Assassin abilities")]                                 # 0.1.23''',
    '''            ("abilmk", "Monk abilities"), ("abilas", "Assassin abilities"),                                 # 0.1.23
            ("abilwba", "Warrior Bers. Archer")]   # 0.1.24 (one category: the config kit allows 16)''')
rep('''_r("abil.vanillaRunes", "VAN_RUNES", "bool", False, "", "", "", "abilk", "Vanilla runes for ability classes",''',
    '''_r("abil.vanillaRunes", "VAN_RUNES", "bool", False, "", "", "", "abilk", "Vanilla runes for every class",''')

# affordability at the unlock level (research/Class-Power-Split.md pools: Warrior = Monk, Archer = Assassin, Berserker 12 + 2 / 22 + 0.16)
rep('''         ("Assassin", 1): (26, 19.12), ("Assassin", 10): (44, 20.2), ("Assassin", 20): (64, 21.4), ("Assassin", 30): (84, 22.6)}''',
    '''         ("Assassin", 1): (26, 19.12), ("Assassin", 10): (44, 20.2), ("Assassin", 20): (64, 21.4), ("Assassin", 30): (84, 22.6),
         ("Warrior", 1): (23, 20.13), ("Warrior", 10): (41, 21.3), ("Warrior", 20): (61, 22.6), ("Warrior", 30): (81, 23.9),      # 0.1.24
         ("Archer", 1): (26, 19.12), ("Archer", 10): (44, 20.2), ("Archer", 20): (64, 21.4), ("Archer", 30): (84, 22.6),
         ("Berserker", 1): (14, 22.16), ("Berserker", 10): (32, 23.6), ("Berserker", 20): (52, 25.2), ("Berserker", 30): (72, 26.8)}''')
rep('''assert _aff == 37 + 20 + 16, _aff          # the plan's "all 37 shape rows PASS" + 0.1.23: Monk 5 x 4, Assassin 4 x 4''',
    '''assert _aff == 37 + 20 + 16 + 60, _aff     # the plan's "all 37 shape rows PASS" + 0.1.23: Monk 5 x 4, Assassin 4 x 4 + 0.1.24: 15 x 4''')
DESC2 = {
    "RallyingGuard": "You + your party take 20 % less, mobs turn on you. Sprint - grab allies as you run. Air - on landing. Crouch - Hold the Line.",
    "ShieldShockwave": "Walk - a cone that stuns and hits. Sprint - Charging Slam (steps in). Air - Ground Pound on landing. Crouch - Ring (all around).",
    "IronChain": "Walk - drag the enemy you look at to you. Sprint - meet halfway. Air - yank it up. Crouch - Anchor (farther, rooted).",
    "Challenge": "Walk - the enemy you look at must fight you: you take less, its hits reflect. Sprint - step in. Air - on landing. Crouch - Duel.",
    "GuardiansOath": "Link an ally: you take part of their damage, and less yourself. Sprint - the nearest + speed. Air - the most hurt. Crouch - more.",
    "Enrage": "You + allies near you (picked once) deal more, growing for 10 s. Sprint - grab more. Air - on landing. Crouch - Lone Rage (you).",
    "Whirlwind": "Spin: hit everything around you, heal from it. Sprint - Cyclone Charge. Air - a slam on landing. Crouch - Grinder (rooted).",
    "Earthsplitter": "Walk - a shockwave line that knocks up (stronger at low Health). Sprint - longer. Air - Crater on landing. Crouch - Fissure.",
    "BloodFrenzy": "Toggle: every hit a stack (damage + speed), allies near you half. Sprint - 3 stacks. Air - 2. Crouch - Blood Bank.",
    "WarlordsBanner": "A banner: damage + defence in range, kills keep it up, falls if you leave. Sprint - ahead. Air - where you land. Crouch - Rooted.",
    "PinningShot": "Walk - an arrow that roots + Marks the first 2. Sprint - on the move. Air - 3 arrows below you. Crouch - Steady Aim (farther).",
    "RapidFire": "15 arrows down your look in 3 s. Sprint - while running. Air - hover while firing. Crouch - Braced (faster, stronger, rooted).",
    "ExplosiveArrow": "Your next arrow hit explodes for 2x. Sprint - Quick Fuse. Air - Mortar (bigger, knock-up). Crouch - Set Charge (later, 2.5x).",
    "ArrowRain": "Walk - arrows rain where you look (slow, root, Mark). Sprint - behind you. Air - below you. Crouch - Kneeling Volley.",
    "HuntersNet": "Walk - a net that roots + Marks where you look. Sprint - a strip behind you. Air - below you. Crouch - Set Trap (hidden).",
}
rep('''ABIL_DESCS_.update({   # 0.1.23''', '''ABIL_DESCS_.update(%r)   # 0.1.24
ABIL_DESCS_.update({   # 0.1.23''' % DESC2)

# ================================================================================================ modifier + rune tables
rep('''        ("Ricochet", "Ricochet", True), ("Haste", "Haste", False)]   # 0.1.23: Skyy M8 "equip ricochet twice ... double the ricochet"''',
    '''        ("Ricochet", "Ricochet", True), ("Haste", "Haste", False),   # 0.1.23: Skyy M8 "equip ricochet twice ... double the ricochet"
        ("Pull", "Pull", True), ("Leech", "Leech", True), ("Floor", "Floor", False), ("Seeker", "Seeker", False)]   # 0.1.24 (L130, L170)
# 0.1.24: modifier pairs that never go together on one ability (Skyy L130 "cannot pair with duration", L170 "not with ricochet")
MOD_EXCL = [("Floor", "Duration"), ("Seeker", "Ricochet")]''')
MODS2 = {"RallyingGuard": ["Duration", "Radius", "Power", "Echo"], "ShieldShockwave": ["Radius", "Knockback", "Echo", "Power"],
         "IronChain": ["Pull", "Chain", "Slow", "Power"], "Challenge": ["Duration", "Power", "Chain", "Ward"],
         "GuardiansOath": ["Duration", "Power", "Radius", "Ward"], "Enrage": ["Duration", "Radius", "Power", "Leech"],
         "Whirlwind": ["Duration", "Radius", "Pull", "Leech", "Echo"], "Earthsplitter": ["Power", "Split", "Slow", "Knockback"],
         "BloodFrenzy": ["Duration", "Floor", "Power", "Leech", "Haste"], "WarlordsBanner": ["Radius", "Duration", "Power", "Ward", "Echo"],
         "PinningShot": ["Pierce", "Split", "Duration", "Power"], "RapidFire": ["Ricochet", "Pierce", "Duration", "Slow", "Seeker"],
         "ExplosiveArrow": ["Radius", "Split", "Knockback", "Echo"], "ArrowRain": ["Radius", "Duration", "Lingering", "Power", "Echo"],
         "HuntersNet": ["Radius", "Duration", "Pull", "Split"]}
rep('''    "VanishingAct": ["Radius", "Duration", "Slow", "Efficiency"],
}''', '''    "VanishingAct": ["Radius", "Duration", "Slow", "Efficiency"],
    # 0.1.24 (research/classes/Warrior.md, Berserker.md, Archer.md; newest wins: Rallying Guard Echo replaces Ward, Shield Shockwave Echo
    # replaces Slow, Explosive Arrow Echo replaces Lingering, Arrow Rain + Whirlwind + Banner + Echo, Rapid Fire + Seeker, Frenzy + Floor;
    # Challenge / Guardian's Oath have no list in the class file - proposed here)
''' + "".join("    %r: %r,\n" % (k, MODS2[k]) for k in NEW2_IDS) + '''}''')
rep('''assert "Lingering" not in AB_MODS["Toxin"], "Toxin: Echo replaced Lingering (Skyy 2026-10-08)"''',
    '''assert "Lingering" not in AB_MODS["Toxin"], "Toxin: Echo replaced Lingering (Skyy 2026-10-08)"
assert all("Echo" in AB_MODS[_a] for _a in ("RallyingGuard", "ShieldShockwave", "Whirlwind", "WarlordsBanner", "ArrowRain", "ExplosiveArrow")), \\
    "Skyy's Echo locks (L132, L139, 2026-10-08 Warrior + Archer reviews)"
assert "Ward" not in AB_MODS["RallyingGuard"] and "Slow" not in AB_MODS["ShieldShockwave"] and "Lingering" not in AB_MODS["ExplosiveArrow"], \\
    "Echo replaced Ward / Slow / Lingering (Skyy 2026-10-08)"
assert "Seeker" in AB_MODS["RapidFire"] and "Ricochet" in AB_MODS["RapidFire"] and "Floor" in AB_MODS["BloodFrenzy"], "Skyy L170 / L130"
assert all(a in MOD_IDS and b in MOD_IDS for a, b in MOD_EXCL)''')
NOUN2 = {"RallyingGuard": "damage cut", "ShieldShockwave": "damage", "IronChain": "damage", "Challenge": "damage cut", "GuardiansOath": "damage cut",
         "Enrage": "damage buff", "Whirlwind": "damage", "Earthsplitter": "damage", "BloodFrenzy": "buff per stack", "WarlordsBanner": "buff",
         "PinningShot": "damage", "RapidFire": "arrow damage", "ExplosiveArrow": "blast damage", "ArrowRain": "damage", "HuntersNet": "damage"}
rep('''           "VanishingAct": "smoke"}''', '''           "VanishingAct": "smoke",
''' + "".join("           %r: %r,\n" % (k, NOUN2[k]) for k in NEW2_IDS) + '''           }''')
rep('''                                      "CloakFirstStrike", "Toxin", "GodKiller", "VanishingAct"]''',
    '''                                      "CloakFirstStrike", "Toxin", "GodKiller", "VanishingAct"] + %r   # 0.1.24''' % NEW2_IDS)
rep('''          "Assassin": ["T6", "PA1", "PA2", "PA3", "PA4", "PA5", "PB1", "PB2", "PB3", "PB5"]}''',
    '''          "Assassin": ["T6", "PA1", "PA2", "PA3", "PA4", "PA5", "PB1", "PB2", "PB3", "PB5"],
          # 0.1.24 (Class-Tree-Paths.md 1 / 2 / 5): the nodes this build applies; Warrior PA3 / PA4 / PC2 + Berserker PA2 wait (Skyy's calls)
          "Warrior": ["T1", "T6", "PA1", "PA2", "PA5", "PB1", "PB2", "PB3", "PB4", "PB5", "PC4"],
          "Berserker": ["T4", "T6", "PA1", "PA3", "PA4", "PA5", "PB2", "PB3", "PB4", "PC2", "PC3", "PC4"],
          "Archer": ["PA1", "PA2", "PA3", "PA4", "PA5", "PB1", "PB2", "PB3", "PB4", "PC1", "PC2", "PC3", "PC4", "PC5"]}''')
rep('''TREE_READS = ",".join("Class.%s.%s" % (_c, _n) for _c in ("Mage", "Priest", "Monk", "Assassin") for _n in TREE_SLOTS + TREE_K[_c])''',
    '''TREE_READS = ",".join("Class.%s.%s" % (_c, _n) for _c in ("Mage", "Priest", "Monk", "Assassin", "Warrior", "Berserker", "Archer") for _n in TREE_SLOTS + TREE_K[_c])''')
rep('''    "# 0.1.23: ab.FlowingForm.* ... ab.VanishingAct.* = the Monk + Assassin abilities; rb.classCap0 = the rebirth soft-cap floor.",
''', '''    "# 0.1.23: ab.FlowingForm.* ... ab.VanishingAct.* = the Monk + Assassin abilities; rb.classCap0 = the rebirth soft-cap floor.",
    "# 0.1.24: ab.RallyingGuard.numbers ... ab.HuntersNet.numbers = the Warrior / Berserker / Archer abilities (walking cost inside).",
''')
# the rune icons: Challenge + Guardian's Oath have no art yet - honest stand-ins until the art round
rep('''    _png = open(os.path.join(_ICON_SRC, _a[2], _a[0] + ".png"), "rb").read()''',
    '''    _png = open(os.path.join(_ICON_SRC, _a[2], ICON_STANDIN.get(_a[0], _a[0]) + ".png"), "rb").read()   # 0.1.24: stand-in icons''')
rep('''RUNE_LANG = ["ui.abilityKeywords.SkyyClass = Class ability"]''',
    '''RUNE_LANG = ["ui.abilityKeywords.SkyyClass = Class ability"]
ICON_STANDIN = {"Challenge": "Unbreakable", "GuardiansOath": "BulwarkStance"}   # 0.1.24: no art yet (Challenge / Guardian's Oath) - the parked alts' icons
assert all(not os.path.isfile(os.path.join(_ICON_SRC, "Warrior", _k + ".png")) for _k in ICON_STANDIN), "real art arrived - drop the stand-in"''')
# 0.1.24: the vanilla effect + particles the new abilities use (checked against Assets.zip like the others)
rep('''assert "Server/Entity/Effects/Status/Vulnerable.json" in _azn, "the vanilla Vulnerable effect moved (Concussive Palm)"''',
    '''assert "Server/Entity/Effects/Status/Vulnerable.json" in _azn, "the vanilla Vulnerable effect moved (Concussive Palm)"
assert "Server/Entity/Effects/Status/Root.json" in _azn and json.loads(_ASSETS.read("Server/Entity/Effects/Status/Root.json").decode("utf-8-sig"))["ApplicationEffects"]["MovementEffects"]["DisableAll"] is True, \\
    "0.1.24: the vanilla Root effect (Pinning Shot, Arrow Rain, Hunter's Net, Anchor, Grinder) no longer stops movement"
assert "Server/Entity/Effects/Abilities/Ability_Hooked.json" in _azn, "0.1.24: the vanilla chain rune's Hooked effect moved (Iron Chain)"''')
rep('''      "FX_TOXIN": "Impact_Poison", "FX_SMOKE": "Impact_Feathers_Black", "FX_GOD": "Impact_Critical"}''',
    '''      "FX_TOXIN": "Impact_Poison", "FX_SMOKE": "Impact_Feathers_Black", "FX_GOD": "Impact_Critical",
      # 0.1.24: Warrior / Berserker / Archer (finite one-shots, checked below like the others)
      "FX_RALLY": "Block_Land_Hard_Dust", "FX_SHOCK": "Dungeon_Goblin_Mace_Slam", "FX_CHAIN": "Impact_Mace_Basic", "FX_SPLIT": "Ability_GroundSlam_Spike",
      "FX_SPLIT0": "Ability_GroundSlam_Line", "FX_CRATER": "Gobliterator_Slam", "FX_SPIN": "Impact_Battleaxe_Bash", "FX_GRIND": "Gobliterator_Out_Of_Control_Spin",
      "FX_ARROW": "Impact_Shortbow_Bash", "FX_BOLT": "Impact_Crossbow_Bash", "FX_BOOM": "Impact_Explosion", "FX_BANNER": "Impact_Sword_Strong",
      "FX_NET": "Block_Hit_Dust", "FX_RAGE": "Impact_Sword_Charged", "FX_FIRE": "Impact_Fire"}''')

# ================================================================================================ AbilDefs: the new indices
rep('''                  ("STILLW", "StillWater"), ("CLOAK", "CloakFirstStrike"), ("TOXIN", "Toxin"), ("GODK", "GodKiller"), ("VANISH", "VanishingAct")):''',
    '''                  ("STILLW", "StillWater"), ("CLOAK", "CloakFirstStrike"), ("TOXIN", "Toxin"), ("GODK", "GodKiller"), ("VANISH", "VanishingAct"),
                  # 0.1.24
                  ("RALLY", "RallyingGuard"), ("SHOCK", "ShieldShockwave"), ("IRONC", "IronChain"), ("CHALL", "Challenge"), ("OATH", "GuardiansOath"),
                  ("ENRAGE", "Enrage"), ("WHIRL", "Whirlwind"), ("ESPLIT", "Earthsplitter"), ("FRENZY", "BloodFrenzy"), ("BANNER", "WarlordsBanner"),
                  ("PIN", "PinningShot"), ("RAPID", "RapidFire"), ("EXPLO", "ExplosiveArrow"), ("RAIN", "ArrowRain"), ("NET", "HuntersNet")):''')

# ================================================================================================ AbilModDefs: the pairs that never go together
rep('''public static long modNextX(long uses, int extra) {
  long n = modNext(uses);
  if (n > 0L || extra <= 0) return n;
  for (int k = 1; k <= extra && k <= 50; k++) { long s = stepX(k); if (uses < s) return s - uses; }
  return 0L;
}""")''', '''public static long modNextX(long uses, int extra) {
  long n = modNext(uses);
  if (n > 0L || extra <= 0) return n;
  for (int k = 1; k <= extra && k <= 50; k++) { long s = stepX(k); if (uses < s) return s - uses; }
  return 0L;
}""")
# 0.1.24: modifier pairs that never go together on one ability (Skyy L130 Floor / Duration+, L170 Seeker / Ricochet)
F(abmods, "public static final int[] EXA = new int[] { %s };" % ", ".join(str(MOD_IDS.index(a)) for a, b in MOD_EXCL))
F(abmods, "public static final int[] EXB = new int[] { %s };" % ", ".join(str(MOD_IDS.index(b)) for a, b in MOD_EXCL))
M(abmods, r"""
public static boolean excl(int a, int b) {
  if (a < 0 || b < 0) return false;
  for (int i = 0; i < EXA.length; i++) if ((EXA[i] == a && EXB[i] == b) || (EXA[i] == b && EXB[i] == a)) return true;
  return false;
}""")''')
rep('''      if (mlvl(p, id, mi) < 2) continue;
    }
    r[j] = mi;''', '''      if (mlvl(p, id, mi) < 2) continue;
    }
    if (j == 1 && r[0] >= 0 && @PKG@.AbilModDefs.excl(r[0], mi)) continue;   // 0.1.24: Floor / Duration+, Seeker / Ricochet
    r[j] = mi;''')
rep('''      if (mlvl(p, aid, mi) < 2) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " can go in both slots from modifier Lv 2.";
    }''', '''      if (mlvl(p, aid, mi) < 2) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " can go in both slots from modifier Lv 2.";
    }
    if (other >= 0 && other != mi && @PKG@.AbilModDefs.excl(mi, other)) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " never goes together with " + @PKG@.AbilModDefs.MNAME[other] + " - take " + @PKG@.AbilModDefs.MNAME[other] + " out first.";   // 0.1.24''')

# ================================================================================================ AbilJob / AbilZone / AbilCtx fields, AbilStore maps
rep('''           "public Object tref;", "public double stun;", "public double push;"):''',
    '''           "public Object tref;", "public double stun;", "public double push;",
           # 0.1.24: a direction (Shockwave cone, Earthsplitter line, Pinning Shot); kind 17 Shockwave, 18 Iron Chain, 19 Earthsplitter,
           # 20 Rapid Fire (channel), 21 a delayed blast (Set Charge), 22 a bleed, 23 a burning patch, 24 Pinning Shot
           "public double dx;", "public double dy;", "public double dz;", "public boolean counted;"):''')
rep('''           "public long lookUntil;"):''', '''           "public long lookUntil;",
           # 0.1.24: kind 13 Rallying Guard, 14 Challenge, 15 Enrage, 16 Whirlwind, 17 Blood Frenzy, 18 Warlord's Banner, 19 Arrow Rain,
           # 20 Hunter's Net; list = the players / refs it keeps, seen2 = counted kills, d3 / d4 / t3 / n3 = per kind
           "public java.util.ArrayList list;", "public java.util.HashSet seen2;", "public double d3;", "public double d4;", "public long t3;",
           "public int n3;"):''')
rep('''           "public String tree;", "public double h;", "public double paid;", "public int hits;", "public java.util.HashSet seen;"):''',
    '''           "public String tree;", "public double h;", "public double paid;", "public int hits;", "public java.util.HashSet seen;",
           "public double x1;"):   # 0.1.24: Retribution's free Shockwave (stun x2)''')
rep('''           "FLOWS", "STANCES", "CLOAKS", "STRIKE", "ARMED", "AWED", "SPD", "MARKS", "PALMS", "POISONED", "SLIPAT", "RBN"):''',
    '''           "FLOWS", "STANCES", "CLOAKS", "STRIKE", "ARMED", "AWED", "SPD", "MARKS", "PALMS", "POISONED", "SLIPAT", "RBN",
           # 0.1.24: UUID -> double[] Rallying Guard {until, cut %, echo until, echo cut %, flags 1 wall 2 interpose 4 thorns 8 presence 16
           # aegis}; UUID -> UUID who guards; mob Ref -> long[] taunt {until, msb, lsb, presence}; mob Ref -> long[] Challenge {until, msb,
           # lsb, cut x100, reflect x100}; UUID -> double[] Oath ally {until, share %, msb, lsb, counted}; UUID -> double[] Oath warrior
           # {until, cut %}; UUID -> double[] Enrage {t0, grow ms, hold until, start %, peak %, fade ms, leech %, counted}; UUID ->
           # double[] Blood Frenzy buff {%, until}; UUID -> double[] banner {damage %, defence %, until}; mob Ref -> double[] Marked {until,
           # %, stacks}; mob Ref -> long[] rooted {until, msb, lsb, flags 1 Lasting Roots 2 Grand Trapper}; UUID -> double[] Explosive
           # Arrow {until, mult, radius, delay ms, up, shape}; UUID -> AbilCtx its cast; UUID -> the running frenzy / banner / spin zone;
           # mob Ref -> long[] Barbed Chain {until, msb, lsb}; UUID -> double[] Retribution {ready, last used, (time, damage) x 8}; mob Ref
           # -> long[] Deadeye {until, msb, lsb}; UUID -> double[] {stacks, at} the last frenzy; UUID -> Long the last frenzy swing; mob Ref
           # -> long[] bleeding {until}; FIX ROUND: UUID -> Long the last frenzy cost taken at a swing START (the chain-start hook)
           "GUARDED", "GUARDBY", "TAUNTS", "CHALLS", "OATHS", "OATHW", "RAGE", "FURY", "WAR", "MARKD", "ROOTS", "EXPL", "EXPLC", "FRENZ",
           "BANNERS", "SPINS", "CHAINED", "RETRI", "DEADEYE", "BANKED", "SWINGS", "BLEEDS", "PAID"):''')
rep('''           "public static volatile String LAST_MONK = \\"\\";", "public static volatile String LAST_ASN = \\"\\";"):
    F(abil, _f)''', '''           "public static volatile String LAST_MONK = \\"\\";", "public static volatile String LAST_ASN = \\"\\";"):
    F(abil, _f)
# 0.1.24: the Warrior / Berserker / Archer counters (the harness + /classadmin abil info) and seams
for _f in ("public static volatile java.util.List TAUNTL = null;",                 # HARNESS SEAM ONLY (null): every mob made to target its taunter
           "public static final java.util.Map XFER = java.util.Collections.synchronizedMap(new java.util.WeakHashMap());",   # Oath transfers (identity)
           "public static volatile long TAUNTED = 0L;", "public static volatile long GUARDS = 0L;", "public static volatile long SHOCKS = 0L;",
           "public static volatile long CHAINS = 0L;", "public static volatile long REFLECTS = 0L;", "public static volatile long OATHED = 0L;",
           "public static volatile long RAGES = 0L;", "public static volatile long SPINHITS = 0L;", "public static volatile long SPLITS = 0L;",
           "public static volatile long FRENZYHITS = 0L;", "public static volatile long FRENZYSWINGS = 0L;", "public static volatile long BANNERKILLS = 0L;", "public static volatile long PINS = 0L;",
           "public static volatile long ARROWS = 0L;", "public static volatile long BLASTS = 0L;", "public static volatile long RAINHITS = 0L;",
           "public static volatile long NETTED = 0L;", "public static volatile long ROOTED = 0L;", "public static volatile long MARKED = 0L;",
           "public static volatile String LAST_WAR = \\"\\";", "public static volatile String LAST_BER = \\"\\";", "public static volatile String LAST_ARC = \\"\\";"):
    F(abil, _f)''')

L24 = []


def late24(src):
    L24.append(src.strip("\n"))


# ---------------------------------------------------------------- shared: tree nodes, time, picking allies, bosses, taunts, roots, marks
late24(r'''
public static boolean nd(@PKG@.AbilCtx c, String cls, String id) {
  return c != null && cls.equals(c.cls) && c.node(id);
}''')
late24(r'''
public static long ms(double secs) {
  return Math.round(secs * 1000.0);
}''')
late24(r'''
public static boolean bossT(@CAC@ acc, @REF@ t) {
  return @PKG@.AbilMath.bossRole(roleOf(acc, t), @PKG@.AbilCfg.BOSS_WORDS);
}''')
late24(r'''
public static java.util.UUID uOf(long msb, long lsb) {
  return new java.util.UUID(msb, lsb);
}''')
# self + party members within party blocks + other players within players blocks (alive, same world); returns the number added
late24(r'''
public static int pickAllies(@ST@ st, @CAC@ acc, java.util.UUID u, double[] c, double party, double players, java.util.ArrayList us, java.util.ArrayList rs) {
  if (c == null || u == null) return 0;
  java.util.ArrayList cu = new java.util.ArrayList();
  java.util.ArrayList cr = new java.util.ArrayList();
  gatherAt(st, acc, c, party > players ? party : players, cu, cr);
  int n = 0;
  for (int i = 0; i < cu.size(); i++) {
    java.util.UUID t = (java.util.UUID) cu.get(i);
    @REF@ r = (@REF@) cr.get(i);
    if (us.contains(t) || !alive(acc, r)) continue;
    boolean self = t.equals(u);
    boolean pty = self || @PKG@.HealTask.inParty(u, t);
    @VEC@ q = pos(acc, r);
    if (q == null) continue;
    if (!self && !@PKG@.AbilMath.inRange(q.x - c[0], q.y - c[1], q.z - c[2], pty ? party : players)) continue;
    us.add(t);
    rs.add(r);
    n++;
  }
  return n;
}''')
# the nearest enemy to a point within r (null = none)
late24(r'''
public static @REF@ nearest(@CAC@ acc, @REF@ cr, double x, double y, double z, double r, @REF@ skip) {
  java.util.List l = near(acc, x, y, z, r);
  @REF@ best = null;
  double bd = 1.0E18;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if ((skip != null && t.equals(skip)) || !enemy(acc, t, cr)) continue;
    @VEC@ q = pos(acc, t);
    if (q == null) continue;
    double d = (q.x - x) * (q.x - x) + (q.y - y) * (q.y - y) + (q.z - z) * (q.z - z);
    if (d > r * r) continue;
    if (d < bd) { bd = d; best = t; }
  }
  return best;
}''')
# THE TAUNT (UNVERIFIED P12): every target slot of the mob that holds another player -> the taunter; none -> its default target slot
late24(r'''
public static int tauntOne(@CAC@ acc, @REF@ t, @REF@ who) {
  java.util.List l = TAUNTL;
  if (l != null) { l.add(t); return 1; }
  try {
    if (t == null || who == null || !t.isValid() || !who.isValid()) return 0;
    Object o = acc.getComponent(t, @MES@.getComponentType());
    if (!(o instanceof @MES@)) return 0;
    @MES@ m = (@MES@) o;
    int n = 0;
    boolean has = false;
    int c = m.getMarkedEntitySlotCount();
    for (int i = 0; i < c; i++) {
      @REF@ x = m.getMarkedEntityRef(i);
      if (x == null) continue;
      if (x.equals(who)) { has = true; continue; }
      if (acc.getComponent(x, @PR@.getComponentType()) == null) continue;
      m.setMarkedEntity(i, who);
      n++;
    }
    if (n == 0 && !has) { m.setMarkedEntity(@MES@.DEFAULT_TARGET_SLOT, who); n = 1; }
    return n;
  } catch (Throwable e) { return 0; }
}''')
late24(r'''
public static int tauntArea(@CAC@ acc, @REF@ cr, java.util.UUID u, double x, double y, double z, double r, double secs, boolean presence, long now) {
  java.util.List l = near(acc, x, y, z, r);
  java.util.HashSet seen = new java.util.HashSet();
  long until = now + ms(secs);
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(acc, t, cr)) continue;
    @VEC@ q = pos(acc, t);
    if (q == null || !@PKG@.AbilMath.inRange(q.x - x, q.y - y, q.z - z, r + 0.5)) continue;
    @PKG@.AbilStore.TAUNTS.put(t, new long[] { until, u.getMostSignificantBits(), u.getLeastSignificantBits(), presence ? 1L : 0L });
    tauntOne(acc, t, cr);
    n++;
  }
  if (n > 0) TAUNTED = TAUNTED + (long) n;
  return n;
}''')
# every tick of a Warrior zone: this caster's live taunts + challenges pull their mobs back onto the Warrior
late24(r'''
public static int tauntKeep(@CAC@ acc, @REF@ cr, java.util.UUID u, long now) {
  if (u == null || cr == null) return 0;
  long ms0 = u.getMostSignificantBits();
  long ls0 = u.getLeastSignificantBits();
  int n = 0;
  for (int k = 0; k < 2; k++) {
    java.util.concurrent.ConcurrentHashMap mp = k == 0 ? @PKG@.AbilStore.TAUNTS : @PKG@.AbilStore.CHALLS;
    if (mp.isEmpty()) continue;
    java.util.Iterator it = mp.keySet().iterator();
    while (it.hasNext()) {
      Object key = it.next();
      Object v = mp.get(key);
      if (!(v instanceof long[]) || !(key instanceof @REF@)) continue;
      long[] a = (long[]) v;
      if (a[0] <= now || a[1] != ms0 || a[2] != ls0) continue;
      if (!enemy(acc, (@REF@) key, cr)) continue;
      tauntOne(acc, (@REF@) key, cr);
      n++;
    }
  }
  return n;
}''')
# a root (the vanilla Root): bosses are only slowed (Grand Trapper: rooted half as long); Lasting Roots / Grand Trapper remember it
late24(r'''
public static int rootMob(@CAC@ acc, @REF@ t, java.util.UUID u, double secs, long now, boolean lasting, boolean grand) {
  if (t == null || !(secs > 0.0)) return -1;
  double s = secs;
  if (bossT(acc, t)) {
    if (!grand) { effect(acc, t, EF_SLOW, secs); return 0; }
    s = secs * 0.5;
  }
  boolean ok = effect(acc, t, "Root", s);
  if (lasting || grand) @PKG@.AbilStore.ROOTS.put(t, new long[] { now + ms(s), u.getMostSignificantBits(), u.getLeastSignificantBits(), (lasting ? 1L : 0L) + (grand ? 2L : 0L) });
  ROOTED = ROOTED + 1L;
  return ok ? 1 : -1;
}''')
# Marked: +pct % damage taken from everyone (Abil.outMult); Focus Mark (Archer PB2): stacks per hit, up to 3, +5 % each
late24(r'''
public static double markMob(@CAC@ acc, @REF@ t, double pct, double secs, boolean focus, long now) {
  if (t == null || !(pct > 0.0) || !(secs > 0.0)) return 0.0;
  Object o = @PKG@.AbilStore.MARKD.get(t);
  double st = 1.0;
  if (focus && o instanceof double[] && ((double[]) o)[0] > (double) now) {
    st = ((double[]) o)[2] + 1.0;
    if (st > 3.0) st = 3.0;
  }
  double p = pct + 5.0 * (st - 1.0);
  @PKG@.AbilStore.MARKD.put(t, new double[] { (double) (now + ms(secs)), p, st });
  MARKED = MARKED + 1L;
  @VEC@ q = pos(acc, t);
  if (q != null) particle(FX_GOD, q.x, q.y + 2.0, q.z, acc);
  return p;
}''')
# THE OUTGOING MULTIPLIER: the attacker's Enrage / Blood Frenzy / banner / Aegis Core, the target's Mark / Lasting Roots / Grand Trapper
late24(r'''
public static double ragePct(double[] g, long now) {
  if (g == null || g.length < 7) return 0.0;
  double t = (double) now;
  if (t < g[0]) return 0.0;
  double e = t - g[0];
  if (e < g[1]) return g[3] + (g[4] - g[3]) * e / (g[1] > 1.0 ? g[1] : 1.0);
  if (t < g[2]) return g[4];
  if (g[5] > 0.0 && t < g[2] + g[5]) return g[4] * (1.0 - (t - g[2]) / g[5]);
  return 0.0;
}''')
late24(r'''
public static double outMult(@CAC@ acc, @REF@ t, java.util.UUID cu, long now) {
  double m = 1.0;
  double tn = (double) now;
  if (cu != null) {
    if (!@PKG@.AbilStore.RAGE.isEmpty()) {
      Object o = @PKG@.AbilStore.RAGE.get(cu);
      if (o instanceof double[]) { double p = ragePct((double[]) o, now); if (p > 0.0) m = m * (1.0 + p / 100.0); }
    }
    if (!@PKG@.AbilStore.FURY.isEmpty()) {
      Object o = @PKG@.AbilStore.FURY.get(cu);
      if (o instanceof double[] && ((double[]) o)[1] > tn) m = m * (1.0 + ((double[]) o)[0] / 100.0);
    }
    if (!@PKG@.AbilStore.WAR.isEmpty()) {
      Object o = @PKG@.AbilStore.WAR.get(cu);
      if (o instanceof double[] && ((double[]) o)[2] > tn) m = m * (1.0 + ((double[]) o)[0] / 100.0);
    }
    if (!@PKG@.AbilStore.GUARDED.isEmpty()) {
      Object o = @PKG@.AbilStore.GUARDED.get(cu);
      if (o instanceof double[] && ((double[]) o)[0] > tn && (((long) ((double[]) o)[4]) & 16L) != 0L) m = m * 0.85;
    }
  }
  if (t != null) {
    if (!@PKG@.AbilStore.MARKD.isEmpty()) {
      Object o = @PKG@.AbilStore.MARKD.get(t);
      if (o instanceof double[] && ((double[]) o)[0] > tn) m = m * (1.0 + ((double[]) o)[1] / 100.0);
    }
    if (!@PKG@.AbilStore.ROOTS.isEmpty()) {
      Object o = @PKG@.AbilStore.ROOTS.get(t);
      if (o instanceof long[]) {
        long[] r = (long[]) o;
        if (r[0] > now) {
          if ((r[3] & 2L) != 0L) m = m * 1.15;
          if ((r[3] & 1L) != 0L && cu != null && r[1] == cu.getMostSignificantBits() && r[2] == cu.getLeastSignificantBits()) m = m * 1.10;
        }
      }
    }
  }
  return m;
}''')
# a transfer (Guardian's Oath): the damage on the Warrior, from the attacker (never a player source), skipped by inHit2
late24(r'''
public static boolean xfer(@CB@ buf, @REF@ to, @REF@ att, double amount) {
  if (!(amount > 0.0) || to == null || !to.isValid() || att == null || !att.isValid()) return false;
  try {
    @DCS@ cause = @DCS@.PROJECTILE;
    if (cause == null) return false;
    @DMG@ d = new @DMG@(new @DENT@(att), cause, (float) amount);
    XFER.put(d, Boolean.TRUE);
    @DSYS@.executeDamage(to, buf, d);
    return true;
  } catch (Throwable x) { @PKG@.ClassCfg.warnLimited("a Guardian's Oath transfer failed: " + x); return false; }
}''')
# Interpose (Warrior PA2): the Warrior stands within 4 blocks of the ally, on the attacker's side (within 60 degrees)
late24(r'''
public static boolean interposed(@CAC@ acc, @REF@ r, @REF@ att, java.util.UUID ally) {
  try {
    Object wo = @PKG@.AbilStore.GUARDBY.get(ally);
    if (!(wo instanceof java.util.UUID) || ally.equals(wo)) return false;
    @REF@ wr = ((@ES@) acc.getExternalData()).getRefFromUUID((java.util.UUID) wo);
    @VEC@ p = pos(acc, r);
    @VEC@ a = pos(acc, att);
    @VEC@ w = wr == null || !wr.isValid() ? null : pos(acc, wr);
    if (p == null || a == null || w == null) return false;
    double ax = a.x - p.x;
    double az = a.z - p.z;
    double wx = w.x - p.x;
    double wz = w.z - p.z;
    double la = Math.sqrt(ax * ax + az * az);
    double lw = Math.sqrt(wx * wx + wz * wz);
    if (!(la > 0.1) || !(lw > 0.1) || lw > 4.0 || lw > la) return false;
    return (ax * wx + az * wz) / (la * lw) >= 0.5;
  } catch (Throwable x) { return false; }
}''')
# Retribution (Warrior PB4): the damage of the last 5 s; 20 % of max Health -> the next Shockwave is free and stuns twice as long
late24(r'''
public static void retriNote(@CAC@ acc, @REF@ r, java.util.UUID u, double amt, long now) {
  Object o = @PKG@.AbilStore.RETRI.get(u);
  if (!(o instanceof double[])) return;
  double[] g = (double[]) o;
  int slot = 2;
  for (int i = 2; i + 1 < g.length; i = i + 2) if (g[i] < g[slot]) slot = i;
  g[slot] = (double) now;
  g[slot + 1] = amt;
  double sum = 0.0;
  for (int i = 2; i + 1 < g.length; i = i + 2) if ((double) now - g[i] <= 5000.0) sum = sum + g[i + 1];
  double mx = max(map(acc, r), @DST@.getHealth());
  if (mx > 0.0 && sum >= mx * @PKG@.AbilNum.SS_RETRIPCT / 100.0 && g[0] < 0.5) { g[0] = 1.0; @PR@ pr = prOf(u); if (pr != null) say(pr, "Retribution: your next Shield Shockwave is free and stuns twice as long."); }
}''')
late24(r'''
public static boolean retriTake(java.util.UUID u, @PKG@.AbilCtx c, long now) {
  Object o = @PKG@.AbilStore.RETRI.get(u);
  if (!(o instanceof double[]) || c == null || !nd(c, "Warrior", "PB4")) return false;
  double[] g = (double[]) o;
  if (g[0] < 0.5 || (double) now - g[1] < @PKG@.AbilNum.SS_RETRIGAP * 1000.0) return false;
  g[0] = 0.0;
  g[1] = (double) now;
  c.x1 = 1.0;
  return true;
}''')
# Barbed Chain (Warrior PB3): the mobs this Warrior dragged take 25 % of the damage dealt to them for 5 s
late24(r'''
public static int barbed(@CB@ buf, @REF@ r, java.util.UUID u, double amt, long now) {
  if (@PKG@.AbilStore.CHAINED.isEmpty() || !(amt > 0.0)) return 0;
  long ms0 = u.getMostSignificantBits();
  long ls0 = u.getLeastSignificantBits();
  int n = 0;
  java.util.Iterator it = @PKG@.AbilStore.CHAINED.keySet().iterator();
  while (it.hasNext()) {
    Object key = it.next();
    Object v = @PKG@.AbilStore.CHAINED.get(key);
    if (!(v instanceof long[]) || !(key instanceof @REF@)) continue;
    long[] a = (long[]) v;
    if (a[0] <= now || a[1] != ms0 || a[2] != ls0 || !enemy(buf, (@REF@) key, r)) continue;
    if (hit(buf, (@REF@) key, r, u, amt * @PKG@.AbilNum.IC_BARBED / 100.0, "IronChain")) n++;
  }
  return n;
}''')
# THE PLAYER DAMAGE HOOK (AbilShieldSys, after armour): Rallying Guard (+ Shield Wall, Interpose, Thorns), Oath, the banner's defence,
# Challenge (cut + reflect), Presence, Retribution, Barbed Chain, the Oath transfer
late24(r'''
public static String inHit2(@ST@ st, @CB@ buf, @REF@ r, @DMG@ d, long now) {
  if (d == null || r == null || d.isCancelled()) return null;
  float a0 = d.getAmount();
  if (!(a0 > 0.0f) || @PKG@.AbilDmg.mine(d) || XFER.containsKey(d)) return null;
  Object po = buf.getComponent(r, @PR@.getComponentType());
  if (!(po instanceof @PR@)) return null;
  if (buf.getComponent(r, @INVU@.getComponentType()) != null) return null;
  java.util.UUID u = ((@PR@) po).getUuid();
  if (u == null) return null;
  @REF@ att = null;
  @DSRC@ src = d.getSource();
  if (src instanceof @DENT@) { try { att = ((@DENT@) src).getRef(); } catch (Throwable t0) { att = null; } }
  if (att != null && (!att.isValid() || att.equals(r))) att = null;
  boolean mob = att != null && buf.getComponent(att, @NPC@.getComponentType()) != null;
  double tn = (double) now;
  double amt = (double) a0;
  String out = "";
  long ms0 = u.getMostSignificantBits();
  long ls0 = u.getLeastSignificantBits();
  Object go = @PKG@.AbilStore.GUARDED.get(u);
  if (go instanceof double[]) {
    double[] g = (double[]) go;
    double cut = g[0] > tn ? g[1] : (g[2] > tn ? g[3] : 0.0);
    if (cut > 0.0) { amt = amt * (1.0 - (cut > 90.0 ? 90.0 : cut) / 100.0); out = out + " guard"; }
    long fl = (long) g[4];
    if (g[0] > tn) {
      if ((fl & 1L) != 0L) { buf.tryRemoveComponent(r, @KBC@.getComponentType()); out = out + " wall"; }
      if ((fl & 2L) != 0L && att != null && interposed(buf, r, att, u)) { amt = amt * 0.75; out = out + " interpose"; }
      if ((fl & 4L) != 0L && mob) {
        amt = amt * 1.05;
        if (hit(buf, att, r, u, (double) a0 * 0.15, "RallyingGuard")) { REFLECTS = REFLECTS + 1L; out = out + " thorns"; }
      }
    }
  }
  Object ow = @PKG@.AbilStore.OATHW.get(u);
  if (ow instanceof double[] && ((double[]) ow)[0] > tn) { amt = amt * (1.0 - ((double[]) ow)[1] / 100.0); out = out + " oath"; }
  Object wo = @PKG@.AbilStore.WAR.get(u);
  if (wo instanceof double[] && ((double[]) wo)[2] > tn) { amt = amt * (1.0 - ((double[]) wo)[1] / 100.0); out = out + " banner"; }
  if (att != null && !@PKG@.AbilStore.CHALLS.isEmpty()) {
    Object co = @PKG@.AbilStore.CHALLS.get(att);
    if (co instanceof long[]) {
      long[] c = (long[]) co;
      if (c[0] > now && c[1] == ms0 && c[2] == ls0) {
        amt = amt * (1.0 - (double) c[3] / 10000.0);
        if (c[4] > 0L && hit(buf, att, r, u, (double) a0 * (double) c[4] / 10000.0, "Challenge")) REFLECTS = REFLECTS + 1L;
        out = out + " challenge";
      }
    }
  }
  if (att != null && !@PKG@.AbilStore.TAUNTS.isEmpty()) {
    Object to = @PKG@.AbilStore.TAUNTS.get(att);
    if (to instanceof long[] && ((long[]) to)[0] > now && ((long[]) to)[3] == 1L) {
      long[] tv = (long[]) to;
      if (tv[1] == ms0 && tv[2] == ls0) { amt = amt * 1.1; out = out + " presence+"; }
      else { amt = amt * 0.8; out = out + " presence-"; }
    }
  }
  if (!@PKG@.AbilStore.RETRI.isEmpty() && @PKG@.AbilStore.RETRI.containsKey(u)) retriNote(buf, r, u, amt, now);
  if (!@PKG@.AbilStore.CHAINED.isEmpty() && barbed(buf, r, u, amt, now) > 0) out = out + " barbed";
  Object oa = @PKG@.AbilStore.OATHS.get(u);
  if (oa instanceof double[] && ((double[]) oa)[0] > tn && att != null) {
    double[] o = (double[]) oa;
    java.util.UUID w = uOf((long) o[2], (long) o[3]);
    @REF@ wr = casterRef(buf, w);
    @VEC@ p = pos(buf, r);
    @VEC@ q = wr == null ? null : pos(buf, wr);
    if (wr != null && wr.isValid() && alive(buf, wr) && p != null && q != null && @PKG@.AbilMath.inRange(p.x - q.x, p.y - q.y, p.z - q.z, @PKG@.AbilNum.GO_LEASH)) {
      double take = amt * o[1] / 100.0;
      Object wc = @PKG@.AbilStore.OATHW.get(w);
      double wcut = wc instanceof double[] && ((double[]) wc)[0] > tn ? ((double[]) wc)[1] : 0.0;
      if (xfer(buf, wr, att, take * (1.0 - wcut / 100.0))) {
        amt = amt - take;
        OATHED = OATHED + 1L;
        out = out + " oath>";
        if (o[4] < 0.5) { o[4] = 1.0; used(w, @PKG@.ClassCfg.pkey(w), @PKG@.AbilDefs.OATH, null); }
      }
    }
  }
  if (amt < (double) a0 - 1.0E-6) d.setAmount((float) (amt < 0.0 ? 0.0 : amt));
  return out.length() == 0 ? null : out.trim();
}''')

# ---------------------------------------------------------------- RALLYING GUARD (zone kind 13)
late24(r'''
public static void guardPut(java.util.UUID t, java.util.UUID by, double cut, long until, double ech, long eu, long flags) {
  Object o = @PKG@.AbilStore.GUARDED.get(t);
  if (o instanceof double[]) {
    double[] g = (double[]) o;
    if (g[0] > (double) System.currentTimeMillis() && g[1] > cut && !t.equals(by)) return;   // a stronger guard stays
  }
  @PKG@.AbilStore.GUARDED.put(t, new double[] { (double) until, cut, (double) eu, ech, (double) flags });
  @PKG@.AbilStore.GUARDBY.put(t, by);
  GUARDS = GUARDS + 1L;
}''')
late24(r'''
public static String rallyAt(@PR@ pr, @ST@ st, @CAC@ acc, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double[] me = here(acc, ref);
  if (me == null || aw == null) return " nopos";
  boolean wall = nd(c, "Warrior", "PA1");
  boolean inter = nd(c, "Warrior", "PA2");
  boolean aegis = nd(c, "Warrior", "PA5");
  boolean thorns = nd(c, "Warrior", "PB1");
  boolean pres = nd(c, "Warrior", "PB5");
  double rad = cxr();
  double main = c == null ? 1.0 : c.main;
  double secs = cxds(sh == 3 ? @PKG@.AbilNum.RG_HOLDTIME : @PKG@.AbilNum.RG_TIME) + (aegis && sh != 3 ? 3.0 : 0.0);
  double tt = cxds(sh == 3 ? @PKG@.AbilNum.RG_HOLDTIME : @PKG@.AbilNum.RG_TAUNTTIME);
  double tr = (sh == 1 ? @PKG@.AbilNum.RG_CHARGETAUNT : (sh == 2 ? @PKG@.AbilNum.RG_LANDTAUNT : (sh == 3 ? @PKG@.AbilNum.RG_HOLDTAUNT : @PKG@.AbilNum.RG_TAUNT))) + rad + (pres ? 4.0 : 0.0);
  double cut = (sh == 3 ? @PKG@.AbilNum.RG_HOLDCUT : @PKG@.AbilNum.RG_CUT) * main;
  if (cut > @PKG@.AbilNum.RG_CUTCAP) cut = @PKG@.AbilNum.RG_CUTCAP;
  double own = cut - (wall ? 4.0 : 0.0);
  if (own < 0.0) own = 0.0;
  double ep = c != null && !c.echo ? c.echoPct : 0.0;
  long until = now + ms(secs);
  long eu = ep > 0.0 ? until + ms(@PKG@.AbilNum.RG_ECHOTIME) : 0L;
  long selfF = (thorns ? 4L : 0L) + (pres ? 8L : 0L) + (aegis ? 16L : 0L);
  long allyF = (wall ? 1L : 0L) + (inter ? 2L : 0L);
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  if (sh == 3) { us.add(u); rs.add(ref); }
  else pickAllies(st, acc, u, me, @PKG@.AbilNum.RG_PARTY + rad + (wall ? 2.0 : 0.0), @PKG@.AbilNum.RG_PLAYERS + rad, us, rs);
  if (!us.contains(u)) { us.add(u); rs.add(ref); }
  int others = 0;
  for (int i = 0; i < us.size(); i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    boolean self = t.equals(u);
    guardPut(t, u, self ? own : cut, until, (self ? own : cut) * ep, eu, self ? selfF : allyF);
    if (!self) {
      others++;
      @PR@ tp = prOf(t);
      if (tp != null) say(tp, pname(u) + "'s Rallying Guard: you take " + @PKG@.AbilMath.fmt(cut) + " % less for " + @PKG@.AbilMath.fmt(secs) + " s.");
    }
  }
  int n = tauntArea(acc, ref, u, me[0], me[1], me[2], tr, tt, pres, now);
  @PKG@.AbilZone z = new @PKG@.AbilZone(13, u, me[0], me[1], me[2], @PKG@.AbilNum.RG_CHARGERADIUS + rad, now, now + ms(secs > tt ? secs : tt));
  z.pkey = k;
  z.ai = @PKG@.AbilDefs.RALLY;
  z.shape = sh;
  z.follow = true;
  z.h = h;
  z.name = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.RALLY, sh);
  z.pct = cut;
  z.d1 = cut * ep;
  z.t1 = until;
  z.t2 = eu;
  z.t3 = sh == 1 ? now + ms(@PKG@.AbilNum.RG_CHARGETIME) : 0L;
  z.n1 = (int) allyF;
  z.n2 = n;
  z.nextHeal = now + 1000L;
  z.hit = new java.util.HashSet(us);
  aw.addZone(z);
  if (inter && sh != 3) speedSet(acc, ref, u, -10, secs);
  particle(FX_RALLY, me[0], me[1] + 0.1, me[2], acc);
  if ((n > 0 || others > 0) && c != null && !c.echo) used(u, k, @PKG@.AbilDefs.RALLY, c);
  if (pr != null) say(pr, z.name + ": " + (sh == 3 ? "you take " + @PKG@.AbilMath.fmt(own) + " % less" : (others + 1) + (others == 0 ? " (you)" : " players") + " take " + @PKG@.AbilMath.fmt(cut) + " % less") + " for " + @PKG@.AbilMath.fmt(secs) + " s - " + n + (n == 1 ? " enemy turns" : " enemies turn") + " on you.");
  LAST_WAR = "rally " + z.name + " cut=" + @PKG@.AbilMath.fmt(cut) + " guarded=" + (others + 1) + " taunted=" + n;
  return " cut=" + @PKG@.AbilMath.fmt(cut) + " own=" + @PKG@.AbilMath.fmt(own) + " guarded=" + (others + 1) + " taunted=" + n + " r=" + @PKG@.AbilMath.fmt(tr) + (ep > 0.0 ? " echo" : "");
}''')
late24(r'''
public static boolean rallyTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  boolean ok = live(cb, cr, z.caster, z.pkey);
  @PKG@.AbilCtx c = z.cx;
  if (!ok || z.ended || now >= z.until) {
    if (ok && c != null && nd(c, "Warrior", "PB2") && !z.echoed) {   // Battle Cry: a shockwave on every taunted enemy
      z.echoed = true;
      int b = 0;
      long ms0 = z.caster.getMostSignificantBits();
      long ls0 = z.caster.getLeastSignificantBits();
      java.util.Iterator it = new java.util.ArrayList(@PKG@.AbilStore.TAUNTS.keySet()).iterator();
      while (it.hasNext()) {
        Object key = it.next();
        Object v = @PKG@.AbilStore.TAUNTS.get(key);
        if (!(v instanceof long[]) || !(key instanceof @REF@)) continue;
        long[] a = (long[]) v;
        if (a[1] != ms0 || a[2] != ls0 || !enemy(cb, (@REF@) key, cr)) continue;
        if (hit(cb, (@REF@) key, cr, z.caster, z.h * cxm(), "RallyingGuard")) b++;
      }
      particle(FX_SHOCK, z.x, z.y + 0.1, z.z, cb);
      @PR@ bp = prOf(z.caster);
      if (bp != null) say(bp, "Battle Cry: " + b + (b == 1 ? " taunted enemy hit." : " taunted enemies hit."));
      LAST_WAR = "battle cry " + b;
    }
    if (ok && c != null && nd(c, "Warrior", "PA2") && z.shape != 3) speedClear(cb, cr, z.caster);
    return false;
  }
  zoneFollow(z, cb);
  tauntKeep(cb, cr, z.caster, now);
  if (z.t3 > now) {   // Charge Rally: every ally you pass
    java.util.ArrayList us = new java.util.ArrayList(z.hit);
    java.util.ArrayList rs = new java.util.ArrayList();
    for (int i = 0; i < us.size(); i++) rs.add(null);
    int n0 = us.size();
    pickAllies(st, cb, z.caster, new double[] { z.x, z.y, z.z }, z.r, z.r, us, rs);
    for (int i = n0; i < us.size(); i++) {
      java.util.UUID t = (java.util.UUID) us.get(i);
      guardPut(t, z.caster, z.pct, z.t1, z.d1, z.t2, (long) z.n1);
      z.hit.add(t);
      @PR@ tp = prOf(t);
      if (tp != null) say(tp, pname(z.caster) + "'s Charge Rally: you take " + @PKG@.AbilMath.fmt(z.pct) + " % less.");
    }
  }
  if (c != null && nd(c, "Warrior", "PA5") && now >= z.nextHeal && now < z.t1) {   // Aegis Core: the guarded heal 3 % a second
    z.nextHeal = now + 1000L;
    java.util.Iterator it = z.hit.iterator();
    while (it.hasNext()) {
      java.util.UUID t = (java.util.UUID) it.next();
      if (!t.equals(z.caster) && !@PKG@.HealTask.inParty(z.caster, t)) continue;
      @REF@ r = casterRef(cb, t);
      if (r == null || !r.isValid() || !healable(cb, r)) continue;
      double mx = max(map(cb, r), @DST@.getHealth());
      if (mx > 0.0) z.absorbed = z.absorbed + apply(cb, r, mx * 0.03, mx * 0.03);
    }
  }
  if (now >= z.nextFx) { z.nextFx = now + 1000L; particle(FX_RALLY, z.x, z.y + 0.1, z.z, cb); }
  return true;
}''')

# ---------------------------------------------------------------- SHIELD SHOCKWAVE (job kind 17)
# FIX ROUND 2 (critic: Shockwave never looked for a shield): a shield (Weapon_Shield_*) in the main hand or the active utility (off-hand)
# slot - the same two reads DamageLock's class lock uses; refused before anything is paid
late24(r'''
public static boolean shieldIn(@CAC@ acc, @REF@ r) {
  String h = hand(acc, r);
  if (h != null && h.startsWith("Weapon_Shield_")) return true;
  try {
    Object o = acc.getComponent(r, @UTIL@.getComponentType());
    if (!(o instanceof @UTIL@)) return false;
    @IS@ ui = ((@UTIL@) o).getActiveItem();
    return ui != null && !ui.isEmpty() && ui.getItemId() != null && ui.getItemId().startsWith("Weapon_Shield_");
  } catch (Throwable t) { return false; }
}''')
late24(r'''
public static String shockCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double[] f = flat(st, ref);
  double[] me = here(st, ref);
  if (me == null) return " nopos";
  if (sh == 1 && f != null) push(st, ref, f[0] * @PKG@.AbilNum.SS_STEP * @PKG@.AbilCfg.PUSH_PER_BLOCK, 0.0, f[1] * @PKG@.AbilNum.SS_STEP * @PKG@.AbilCfg.PUSH_PER_BLOCK);
  return " " + shockJob(aw, c, u, k, me, f, sh, h, now);
}''')
late24(r'''
public static String shockJob(@PKG@.AbilWorld aw, @PKG@.AbilCtx c, java.util.UUID u, String k, double[] at, double[] f, int sh, double h, long now) {
  double pw = sh == 1 ? @PKG@.AbilNum.SS_SPRINTPOWER : (sh == 3 ? @PKG@.AbilNum.SS_RINGPOWER : @PKG@.AbilNum.SS_POWER);
  @PKG@.AbilJob j = new @PKG@.AbilJob(17, now, u, "ShieldShockwave", at[0], at[1], at[2], 0.0, h * pw * cxm());
  j.pkey = k;
  j.ai = @PKG@.AbilDefs.SHOCK;
  j.sh = sh;
  j.r = (sh == 1 ? @PKG@.AbilNum.SS_SPRINTRANGE : (sh == 2 ? @PKG@.AbilNum.SS_POUNDRADIUS : (sh == 3 ? @PKG@.AbilNum.SS_RINGRADIUS : @PKG@.AbilNum.SS_RANGE))) + cxr();
  j.width = sh == 2 || sh == 3 || f == null ? 180.0 : @PKG@.AbilNum.SS_ANGLE;
  j.dx = f == null ? 0.0 : f[0];
  j.dz = f == null ? 0.0 : f[1];
  double stun = sh == 1 ? @PKG@.AbilNum.SS_SPRINTSTUN : (sh == 2 ? @PKG@.AbilNum.SS_POUNDSTUN : @PKG@.AbilNum.SS_STUN);
  if (nd(c, "Warrior", "T1")) stun = stun + 0.25;
  if (c != null && c.lvl > 1) { double add = @PKG@.AbilNum.SS_STUNLEVEL * (double) (c.lvl - 1); stun = stun + (add > 0.6 ? 0.6 : add); }
  if (c != null && c.x1 > 0.0) stun = stun * 2.0;
  j.stun = stun;
  j.push = sh == 2 ? @PKG@.AbilNum.SS_POUNDUP : 0.0;
  aw.add(j);
  return "cone=" + @PKG@.AbilMath.fmt(j.r) + "/" + @PKG@.AbilMath.fmt(j.width) + " hit=" + @PKG@.AbilMath.fmt(j.amount) + " stun=" + @PKG@.AbilMath.fmt(stun) + (c != null && c.x1 > 0.0 ? " retribution" : "");
}''')
late24(r'''
public static int shockRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_WAR = "shock gone"; return -1; }
  @PKG@.AbilCtx c = j.cx;
  boolean echo = c != null && c.echo;
  double x0 = j.x;
  double y0 = j.y;
  double z0 = j.z;
  if (j.sh != 2) { @VEC@ p = pos(cb, cr); if (p != null) { x0 = p.x; y0 = p.y; z0 = p.z; } }
  int kb = c == null ? 0 : c.eff(@PKG@.AbilModDefs.KNOCK);
  boolean surge = nd(c, "Warrior", "PC4");
  java.util.List l = near(cb, x0, y0, z0, j.r);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    @VEC@ q = pos(cb, t);
    if (q == null) continue;
    double dx = q.x - x0;
    double dz = q.z - z0;
    double dd = Math.sqrt(dx * dx + dz * dz);
    if (dd > j.r) continue;
    if (j.width < 180.0 && dd > 0.3) {
      double cs = (dx * j.dx + dz * j.dz) / dd;
      if (cs > 1.0) cs = 1.0;
      if (cs < -1.0) cs = -1.0;
      if (Math.toDegrees(Math.acos(cs)) > j.width) continue;
    }
    if (hit(cb, t, cr, j.caster, j.amount, "ShieldShockwave")) n++;
    stunMob(cb, t, j.caster, j.stun, now);
    double up = j.push > 0.0 ? j.push * @PKG@.AbilCfg.PUSH_PER_BLOCK : 0.0;
    if (kb > 0 || up > 0.0) {
      double f = 2.0 * (double) kb * @PKG@.AbilCfg.PUSH_PER_BLOCK;
      if (dd > 0.05) push(cb, t, dx / dd * f, up > 0.0 ? up : f * 0.25, dz / dd * f);
      else push(cb, t, 0.0, up, 0.0);
    }
  }
  particle(FX_SHOCK, x0 + j.dx * 1.5, y0 + 0.1, z0 + j.dz * 1.5, cb);
  SHOCKS = SHOCKS + 1L;
  if (surge && n > 0) {
    double mx = max(map(cb, cr), @DST@.getHealth());
    int hn = n > 5 ? 5 : n;
    if (mx > 0.0) apply(cb, cr, mx * 0.03 * (double) hn, mx * 0.03 * (double) hn);
  }
  if (!echo && c != null && c.echoPct > 0.0) {
    @PKG@.AbilCtx e = c.echoOf(c.echoPct);
    @PKG@.AbilJob ej = new @PKG@.AbilJob(10, now + ms(@PKG@.AbilCfg.ECHO_DELAY), j.caster, "ShieldShockwave", j.x, j.y, j.z, j.r, c.main > 0.0 ? j.amount * e.main / c.main : j.amount * c.echoPct);
    ej.pkey = j.pkey;
    ej.ai = j.ai;
    ej.sh = j.sh;
    ej.dx = j.dx;
    ej.dz = j.dz;
    ej.width = j.width;
    ej.stun = @PKG@.AbilNum.SS_ECHOSTUN;
    ej.cx = e;
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
    if (aw != null) aw.add(ej);
  }
  if (n > 0 && !echo) used(j.caster, j.pkey, @PKG@.AbilDefs.SHOCK, c);
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, (echo ? "Echo: " : "") + @PKG@.AbilDefs.sname(@PKG@.AbilDefs.SHOCK, j.sh) + ": " + n + (n == 1 ? " enemy" : " enemies") + " stunned " + @PKG@.AbilMath.fmt(j.stun) + " s.");
  LAST_WAR = "shock" + (echo ? " echo" : "") + " " + n + " stun=" + @PKG@.AbilMath.fmt(j.stun);
  return n;
}''')

# ---------------------------------------------------------------- IRON CHAIN (job kind 18) - the vanilla chain rune's Hooked look
late24(r'''
public static String chainCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, @REF@ t, long now) {
  if (t == null) return " notarget";
  @PKG@.AbilJob j = new @PKG@.AbilJob(18, now, u, "IronChain", 0.0, 0.0, 0.0, 0.0, h * (sh == 2 ? @PKG@.AbilNum.IC_HOOKPOWER : @PKG@.AbilNum.IC_POWER) * cxm());
  j.pkey = k;
  j.ai = @PKG@.AbilDefs.IRONC;
  j.sh = sh;
  j.tref = t;
  aw.add(j);
  return " chain=" + @PKG@.AbilMath.fmt(j.amount);
}''')
late24(r'''
public static int chainOne(@CB@ cb, @REF@ cr, @REF@ x, @PKG@.AbilJob j, @PKG@.AbilCtx c, boolean pull, long now) {
  @VEC@ p = pos(cb, cr);
  @VEC@ q = pos(cb, x);
  if (p == null || q == null) return 0;
  int pl = c == null ? 0 : c.eff(@PKG@.AbilModDefs.PULL);
  double dx = p.x - q.x;
  double dz = p.z - q.z;
  double d = Math.sqrt(dx * dx + dz * dz);
  if (pull && d > 1.6) {
    double dist = d - 1.5;
    double sp = dist * @PKG@.AbilCfg.PUSH_PER_BLOCK * (1.0 + 0.25 * (double) pl) * (j.sh == 3 ? @PKG@.AbilNum.IC_ANCHORPULL / 100.0 : 1.0);
    if (j.sh == 2) push(cb, x, dx / d * sp * 0.3, @PKG@.AbilNum.IC_HOOKUP * @PKG@.AbilCfg.PUSH_PER_BLOCK * 0.5, dz / d * sp * 0.3);
    else if (j.sh == 1) { push(cb, x, dx / d * sp * 0.5, 1.0, dz / d * sp * 0.5); push(cb, cr, -dx / d * sp * 0.5, 0.5, -dz / d * sp * 0.5); }
    else push(cb, x, dx / d * sp, 1.5, dz / d * sp);
  }
  effect(cb, x, "Ability_Hooked", 0.8);
  double stun = j.sh == 1 ? @PKG@.AbilNum.IC_MEETSTUN : (j.sh == 3 ? @PKG@.AbilNum.IC_ANCHORSTUN : @PKG@.AbilNum.IC_STUN);
  if (c != null && c.lvl > 1) { double add = 0.02 * (double) (c.lvl - 1); stun = stun + (add > 0.4 ? 0.4 : add); }
  stunMob(cb, x, j.caster, stun, now);
  if (j.sh == 3) rootMob(cb, x, j.caster, stun + @PKG@.AbilNum.IC_ANCHORROOT, now, false, false);
  int sl = c == null ? 0 : c.eff(@PKG@.AbilModDefs.SLOW);
  if (sl > 0) effect(cb, x, EF_SLOW, 1.0 + (double) sl);
  if (nd(c, "Warrior", "PB3")) @PKG@.AbilStore.CHAINED.put(x, new long[] { now + ms(@PKG@.AbilNum.IC_BARBEDTIME), j.caster.getMostSignificantBits(), j.caster.getLeastSignificantBits() });
  particle(FX_CHAIN, q.x, q.y + 1.0, q.z, cb);
  return 1;
}''')
late24(r'''
public static int chainRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_WAR = "chain gone"; return -1; }
  if (!(j.tref instanceof @REF@)) return -1;
  @REF@ t = (@REF@) j.tref;
  if (!enemy(cb, t, cr)) { LAST_WAR = "chain dead"; return -1; }
  @PKG@.AbilCtx c = j.cx;
  int pl = c == null ? 0 : c.eff(@PKG@.AbilModDefs.PULL);
  boolean boss = bossT(cb, t);
  boolean pull = !boss || pl > 0;
  int n = 0;
  if (hit(cb, t, cr, j.caster, j.amount, "IronChain")) n++;
  chainOne(cb, cr, t, j, c, pull, now);
  int ch = c == null ? 0 : c.eff(@PKG@.AbilModDefs.CHAIN);
  @VEC@ q = pos(cb, t);
  java.util.HashSet done = new java.util.HashSet();
  done.add(t);
  int extra = 0;
  for (int i = 0; i < ch && q != null; i++) {
    java.util.List l = near(cb, q.x, q.y, q.z, @PKG@.AbilNum.IC_CHAINRANGE);
    @REF@ best = null;
    double bd = 1.0E18;
    for (int k = 0; k < l.size(); k++) {
      Object o = l.get(k);
      if (!(o instanceof @REF@)) continue;
      @REF@ x = (@REF@) o;
      if (done.contains(x) || !enemy(cb, x, cr)) continue;
      @VEC@ w = pos(cb, x);
      if (w == null) continue;
      double dd = (w.x - q.x) * (w.x - q.x) + (w.z - q.z) * (w.z - q.z);
      if (dd > @PKG@.AbilNum.IC_CHAINRANGE * @PKG@.AbilNum.IC_CHAINRANGE) continue;
      if (dd < bd) { bd = dd; best = x; }
    }
    if (best == null) break;
    done.add(best);
    if (hit(cb, best, cr, j.caster, j.amount, "IronChain")) n++;
    chainOne(cb, cr, best, j, c, !bossT(cb, best) || pl > 0, now);
    extra++;
  }
  CHAINS = CHAINS + 1L;
  if (n > 0) used(j.caster, j.pkey, @PKG@.AbilDefs.IRONC, c);
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.IRONC, j.sh) + ": hooked" + (pull ? "" : " (too heavy to drag - Pull drags bosses)") + (extra > 0 ? ", +" + extra + " more (Chain)." : "."));
  LAST_WAR = "chain " + (pull ? "pulled" : "held") + " extra=" + extra;
  return n;
}''')

# ---------------------------------------------------------------- CHALLENGE (zone kind 14)
late24(r'''
public static String challAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, @REF@ t, long now) {
  if (t == null || aw == null) return " notarget";
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double main = c == null ? 1.0 : c.main;
  double secs = cxds(sh == 3 ? @PKG@.AbilNum.CH_DUELTIME : (sh == 1 ? @PKG@.AbilNum.CH_SPRINTTIME : @PKG@.AbilNum.CH_TIME));
  double cut = (sh == 3 ? @PKG@.AbilNum.CH_DUELCUT : @PKG@.AbilNum.CH_CUT) * main;
  double refl = (sh == 3 ? @PKG@.AbilNum.CH_DUELREFLECT : @PKG@.AbilNum.CH_REFLECT) * main;
  if (cut > 80.0) cut = 80.0;
  if (refl > 100.0) refl = 100.0;
  if (sh == 1) {
    @VEC@ p = pos(acc, ref);
    @VEC@ q = pos(acc, t);
    if (p != null && q != null) {
      double dx = q.x - p.x;
      double dz = q.z - p.z;
      double dd = Math.sqrt(dx * dx + dz * dz);
      double sp = @PKG@.AbilNum.CH_STEP * @PKG@.AbilCfg.PUSH_PER_BLOCK;
      if (dd > 1.5) push(acc, ref, dx / dd * sp, 0.0, dz / dd * sp);
    }
  }
  long until = now + ms(secs);
  java.util.ArrayList ts = new java.util.ArrayList();
  ts.add(t);
  int ch = c == null ? 0 : c.eff(@PKG@.AbilModDefs.CHAIN);
  @VEC@ q0 = pos(acc, t);
  for (int i = 0; i < ch && q0 != null; i++) {
    @REF@ b = null;
    double bd = 1.0E18;
    java.util.List l = near(acc, q0.x, q0.y, q0.z, @PKG@.AbilNum.CH_CHAINRANGE);
    for (int m = 0; m < l.size(); m++) {
      Object o = l.get(m);
      if (!(o instanceof @REF@) || ts.contains(o) || !enemy(acc, (@REF@) o, ref)) continue;
      @VEC@ w = pos(acc, (@REF@) o);
      if (w == null) continue;
      double dd = (w.x - q0.x) * (w.x - q0.x) + (w.z - q0.z) * (w.z - q0.z);
      if (dd > @PKG@.AbilNum.CH_CHAINRANGE * @PKG@.AbilNum.CH_CHAINRANGE) continue;
      if (dd < bd) { bd = dd; b = (@REF@) o; }
    }
    if (b == null) break;
    ts.add(b);
  }
  for (int i = 0; i < ts.size(); i++) {
    @REF@ x = (@REF@) ts.get(i);
    @PKG@.AbilStore.CHALLS.put(x, new long[] { until, u.getMostSignificantBits(), u.getLeastSignificantBits(), Math.round(cut * 100.0), Math.round(refl * 100.0) });
    tauntOne(acc, x, ref);
    @VEC@ w = pos(acc, x);
    if (w != null) particle(FX_RAGE, w.x, w.y + 1.0, w.z, acc);
  }
  TAUNTED = TAUNTED + (long) ts.size();
  int wl = c == null ? 0 : c.lv(@PKG@.AbilModDefs.WARD);
  if (wl > 0) {
    double mx = max(map(acc, ref), @DST@.getHealth());
    if (mx > 0.0) wardGive(u, mx * 3.0 * (double) wl / 100.0, until);
  }
  double[] me = here(acc, ref);
  @PKG@.AbilZone z = new @PKG@.AbilZone(14, u, me == null ? 0.0 : me[0], me == null ? 0.0 : me[1], me == null ? 0.0 : me[2], 1.0, now, until);
  z.pkey = k;
  z.ai = @PKG@.AbilDefs.CHALL;
  z.shape = sh;
  z.follow = true;
  z.name = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.CHALL, sh);
  z.hit = new java.util.HashSet(ts);
  aw.addZone(z);
  if (c != null && !c.echo) used(u, k, @PKG@.AbilDefs.CHALL, c);
  if (pr != null) say(pr, z.name + ": " + (ts.size() == 1 ? "it" : ts.size() + " enemies") + " must fight you " + @PKG@.AbilMath.fmt(secs) + " s - you take " + @PKG@.AbilMath.fmt(cut) + " % less from " + (ts.size() == 1 ? "it" : "them") + ", " + @PKG@.AbilMath.fmt(refl) + " % of " + (ts.size() == 1 ? "its" : "their") + " hits reflect.");
  LAST_WAR = "challenge " + ts.size() + " cut=" + @PKG@.AbilMath.fmt(cut) + " reflect=" + @PKG@.AbilMath.fmt(refl);
  return " targets=" + ts.size() + " cut=" + @PKG@.AbilMath.fmt(cut) + " reflect=" + @PKG@.AbilMath.fmt(refl) + " secs=" + @PKG@.AbilMath.fmt(secs);
}''')
late24(r'''
public static boolean challTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  if (!live(cb, cr, z.caster, z.pkey) || z.ended || now >= z.until) { LAST_WAR = "challenge end"; return false; }
  zoneFollow(z, cb);
  int live0 = 0;
  java.util.Iterator it = z.hit.iterator();
  while (it.hasNext()) { Object o = it.next(); if (o instanceof @REF@ && enemy(cb, (@REF@) o, cr)) live0++; }
  if (live0 == 0) { @PR@ pr = prOf(z.caster); if (pr != null) say(pr, "Challenge won."); LAST_WAR = "challenge won"; return false; }
  tauntKeep(cb, cr, z.caster, now);
  return true;
}''')

# ---------------------------------------------------------------- GUARDIAN'S OATH (no zone: the OATHS / OATHW records, the damage hook)
late24(r'''
public static java.util.UUID oathPick(@ST@ st, @CAC@ acc, @REF@ ref, java.util.UUID u, int sh, double range, double[] at) {
  double[] c = at != null ? at : here(acc, ref);
  if (c == null) return null;
  if (sh == 0 || sh == 3) {
    java.util.UUID lp = lookPlayer(acc, ref, range);
    if (lp != null && !lp.equals(u) && @PKG@.HealTask.inParty(u, lp)) return lp;
  }
  java.util.ArrayList cu = new java.util.ArrayList();
  java.util.ArrayList cr = new java.util.ArrayList();
  gatherAt(st, acc, c, range, cu, cr);
  java.util.UUID best = null;
  double bk = 1.0E18;
  for (int i = 0; i < cu.size(); i++) {
    java.util.UUID t = (java.util.UUID) cu.get(i);
    @REF@ r = (@REF@) cr.get(i);
    if (t.equals(u) || !@PKG@.HealTask.inParty(u, t) || !alive(acc, r)) continue;
    double key;
    if (sh == 1) {
      @VEC@ q = pos(acc, r);
      if (q == null) continue;
      key = (q.x - c[0]) * (q.x - c[0]) + (q.y - c[1]) * (q.y - c[1]) + (q.z - c[2]) * (q.z - c[2]);
    } else {
      @ESM@ m = map(acc, r);
      double mx = max(m, @DST@.getHealth());
      double hh = cur(m, @DST@.getHealth());
      key = mx > 0.0 && hh >= 0.0 ? hh / mx : 1.0;
    }
    if (key < bk) { bk = key; best = t; }
  }
  return best;
}''')
late24(r'''
public static String oathAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String k, int sh, java.util.UUID t, long now) {
  if (t == null) return " noally";
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double main = c == null ? 1.0 : c.main;
  double secs = cxds(sh == 3 ? @PKG@.AbilNum.GO_BURDENTIME : @PKG@.AbilNum.GO_TIME);
  double share = sh == 3 ? @PKG@.AbilNum.GO_BURDENSHARE : @PKG@.AbilNum.GO_SHARE;
  if (share > 90.0) share = 90.0;
  double cut = (sh == 3 ? @PKG@.AbilNum.GO_BURDENCUT : @PKG@.AbilNum.GO_CUT) * main;
  if (cut > 60.0) cut = 60.0;
  long until = now + ms(secs);
  @PKG@.AbilStore.OATHS.put(t, new double[] { (double) until, share, (double) u.getMostSignificantBits(), (double) u.getLeastSignificantBits(), 0.0 });
  @PKG@.AbilStore.OATHW.put(u, new double[] { (double) until, cut });
  int wl = c == null ? 0 : c.lv(@PKG@.AbilModDefs.WARD);
  if (wl > 0) {
    double mx = max(map(acc, ref), @DST@.getHealth());
    if (mx > 0.0) wardGive(t, mx * 3.0 * (double) wl / 100.0, until);
  }
  if (sh == 1) haste(acc, ref, u, (int) @PKG@.AbilNum.GO_RUSHSPEED, 3.0);
  @PR@ tp = prOf(t);
  if (tp != null) say(tp, pname(u) + " swore an oath: " + @PKG@.AbilMath.fmt(share) + " % of the damage you take goes to them for " + @PKG@.AbilMath.fmt(secs) + " s.");
  double[] me = here(acc, ref);
  if (me != null) particle(FX_RALLY, me[0], me[1] + 1.0, me[2], acc);
  String nm = pname(t);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.OATH, sh) + ": linked to " + nm + " - " + @PKG@.AbilMath.fmt(share) + " % of their damage comes to you, you take " + @PKG@.AbilMath.fmt(cut) + " % less.");
  LAST_WAR = "oath " + nm + " share=" + @PKG@.AbilMath.fmt(share) + " cut=" + @PKG@.AbilMath.fmt(cut);
  return " ally=" + nm + " share=" + @PKG@.AbilMath.fmt(share) + " cut=" + @PKG@.AbilMath.fmt(cut) + " secs=" + @PKG@.AbilMath.fmt(secs);
}''')

late24(r'''
public static String pname(java.util.UUID u) {
  @PR@ p = prOf(u);
  String n = p == null ? null : p.getUsername();
  return n == null || n.length() == 0 ? "A player" : n;
}''')

# ---------------------------------------------------------------- ENRAGE (zone kind 15 = the controller: War Charge, War Horn, Rally)
late24(r'''
public static void rageGive(java.util.UUID t, long t0, long growMs, long holdUntil, double start, double peak, long fadeMs, double leech) {
  Object o = @PKG@.AbilStore.RAGE.get(t);
  if (o instanceof double[]) {
    double[] g = (double[]) o;
    long now = System.currentTimeMillis();
    if (ragePct(g, now) > ragePct(new double[] { (double) t0, (double) growMs, (double) holdUntil, start, peak, (double) fadeMs, 0.0, 0.0 }, now)) return;
  }
  @PKG@.AbilStore.RAGE.put(t, new double[] { (double) t0, (double) growMs, (double) holdUntil, start, peak, (double) fadeMs, leech, 0.0 });
  RAGES = RAGES + 1L;
}''')
late24(r'''
public static String rageAt(@PR@ pr, @ST@ st, @CAC@ acc, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double[] me = here(acc, ref);
  if (me == null || aw == null) return " nopos";
  double main = c == null ? 1.0 : c.main;
  boolean horn = nd(c, "Berserker", "PA1");
  boolean bringer = nd(c, "Berserker", "PA5");
  double rad = cxr() + (sh == 2 ? @PKG@.AbilNum.EN_LEAPADD : 0.0);
  double start = horn ? @PKG@.AbilNum.EN_HORNSTART : @PKG@.AbilNum.EN_START;
  double peak = @PKG@.AbilNum.EN_PEAK * main + (c == null ? 0.0 : c.amt("T4", 3.0)) + (sh == 3 ? @PKG@.AbilNum.EN_LONEBONUS : 0.0);
  double sp = peak * @PKG@.AbilNum.EN_SELFMULT - (horn ? 5.0 : 0.0);
  if (bringer) { peak = peak * 0.9; sp = sp * 0.9; }
  if (sp > @PKG@.AbilNum.EN_SELFCAP) sp = @PKG@.AbilNum.EN_SELFCAP;
  if (start > peak) start = peak;
  double ss = start * @PKG@.AbilNum.EN_SELFMULT;
  if (ss > sp) ss = sp;
  long grow = ms(@PKG@.AbilNum.EN_GROW);
  long hold = ms(cxds(sh == 3 ? @PKG@.AbilNum.EN_LONEHOLD : @PKG@.AbilNum.EN_HOLD));
  long fade = bringer ? ms(@PKG@.AbilNum.EN_FADE) : 0L;
  double leech = c == null ? 0.0 : 3.0 * (double) c.eff(@PKG@.AbilModDefs.LEECH);
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  if (sh != 3) pickAllies(st, acc, u, me, @PKG@.AbilNum.EN_PARTY + rad, @PKG@.AbilNum.EN_PLAYERS + rad, us, rs);
  if (!us.contains(u)) { us.add(u); rs.add(ref); }
  int others = 0;
  for (int i = 0; i < us.size(); i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    boolean self = t.equals(u);
    rageGive(t, now, grow, now + grow + hold, self ? ss : start, self ? sp : peak, fade, self ? leech : 0.0);
    if (!self) {
      others++;
      @PR@ tp = prOf(t);
      if (tp != null) say(tp, pname(u) + "'s Enrage: your damage grows to +" + @PKG@.AbilMath.fmt(peak) + " %.");
    }
  }
  @PKG@.AbilZone z = new @PKG@.AbilZone(15, u, me[0], me[1], me[2], @PKG@.AbilNum.EN_CHARGERADIUS + rad, now, now + grow + hold + fade);
  z.pkey = k;
  z.ai = @PKG@.AbilDefs.ENRAGE;
  z.shape = sh;
  z.follow = true;
  z.name = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.ENRAGE, sh);
  z.d1 = start;
  z.d2 = peak;
  z.t1 = horn && sh != 3 ? now + ms(@PKG@.AbilNum.EN_HORNDELAY) : 0L;
  z.t2 = nd(c, "Berserker", "PA4") && sh != 3 ? now + grow : 0L;
  z.t3 = sh == 1 ? now + ms(@PKG@.AbilNum.EN_CHARGETIME) : 0L;
  z.n1 = (int) grow;
  z.n2 = (int) (hold + grow);
  z.n3 = (int) fade;
  z.hit = new java.util.HashSet(us);
  aw.addZone(z);
  particle(FX_RAGE, me[0], me[1] + 1.0, me[2], acc);
  if (pr != null) say(pr, z.name + ": you +" + @PKG@.AbilMath.fmt(ss) + " -> +" + @PKG@.AbilMath.fmt(sp) + " % damage" + (others > 0 ? ", " + others + (others == 1 ? " ally" : " allies") + " +" + @PKG@.AbilMath.fmt(start) + " -> +" + @PKG@.AbilMath.fmt(peak) + " %" : "") + " over " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.EN_GROW) + " s.");
  LAST_BER = "enrage " + z.name + " allies=" + others + " peak=" + @PKG@.AbilMath.fmt(peak) + " self=" + @PKG@.AbilMath.fmt(sp);
  return " allies=" + others + " start=" + @PKG@.AbilMath.fmt(start) + " peak=" + @PKG@.AbilMath.fmt(peak) + " self=" + @PKG@.AbilMath.fmt(ss) + "/" + @PKG@.AbilMath.fmt(sp) + (horn ? " horn" : "") + (bringer ? " fade" : "");
}''')
late24(r'''
public static int rageJoin(@ST@ st, @CB@ cb, @PKG@.AbilZone z, double party, double players, long now) {
  java.util.ArrayList us = new java.util.ArrayList(z.hit);
  java.util.ArrayList rs = new java.util.ArrayList();
  for (int i = 0; i < us.size(); i++) rs.add(null);
  int n0 = us.size();
  pickAllies(st, cb, z.caster, new double[] { z.x, z.y, z.z }, party, players, us, rs);
  for (int i = n0; i < us.size(); i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    rageGive(t, z.start, (long) z.n1, z.start + (long) z.n2, z.d1, z.d2, (long) z.n3, 0.0);
    z.hit.add(t);
    @PR@ tp = prOf(t);
    if (tp != null) say(tp, pname(z.caster) + "'s Enrage: your damage grows to +" + @PKG@.AbilMath.fmt(z.d2) + " %.");
  }
  return us.size() - n0;
}''')
late24(r'''
public static boolean rageTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  if (!live(cb, cr, z.caster, z.pkey) || z.ended || now >= z.until) { LAST_BER = "enrage end"; return false; }
  zoneFollow(z, cb);
  if (z.t3 > now) rageJoin(st, cb, z, z.r, z.r, now);   // War Charge: everyone you pass
  if (z.t1 > 0L && now >= z.t1) {                       // War Horn: a second call picks up the late
    z.t1 = 0L;
    int n = rageJoin(st, cb, z, @PKG@.AbilNum.EN_PARTY + cxr(), @PKG@.AbilNum.EN_PLAYERS + cxr(), now);
    @PR@ pr = prOf(z.caster);
    if (pr != null) say(pr, "War Horn: " + n + (n == 1 ? " more ally." : " more allies."));
    particle(FX_RAGE, z.x, z.y + 1.0, z.z, cb);
  }
  if (z.t2 > 0L && now >= z.t2) {                       // Rally: at the peak, a 10 % shield for everyone picked
    z.t2 = 0L;
    int n = 0;
    java.util.Iterator it = z.hit.iterator();
    while (it.hasNext()) {
      java.util.UUID t = (java.util.UUID) it.next();
      @REF@ r = casterRef(cb, t);
      if (r == null || !r.isValid()) continue;
      double mx = max(map(cb, r), @DST@.getHealth());
      if (mx > 0.0 && wardGive(t, mx * @PKG@.AbilNum.EN_RALLYSHIELD / 100.0, z.until) > 0.0) n++;
    }
    LAST_BER = "rally shield " + n;
  }
  return true;
}''')

# ---------------------------------------------------------------- WHIRLWIND (zone kind 16)
late24(r'''
public static String spinAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double[] me = here(acc, ref);
  if (me == null || aw == null) return " nopos";
  Object old = @PKG@.AbilStore.SPINS.get(u);
  if (old instanceof @PKG@.AbilZone) { ((@PKG@.AbilZone) old).ended = true; ((@PKG@.AbilZone) old).why = "replaced"; }
  boolean bleed = nd(c, "Berserker", "PB2");
  boolean stag = nd(c, "Berserker", "PC3");
  double secs = cxds(sh == 1 ? @PKG@.AbilNum.WW_SPRINTTIME : @PKG@.AbilNum.WW_TIME);
  double r = (sh == 1 ? @PKG@.AbilNum.WW_SPRINTRADIUS : (sh == 3 ? @PKG@.AbilNum.WW_GRINDRADIUS : @PKG@.AbilNum.WW_RADIUS)) + cxr();
  @PKG@.AbilZone z = new @PKG@.AbilZone(16, u, me[0], me[1], me[2], r, now, now + ms(secs));
  z.pkey = k;
  z.ai = @PKG@.AbilDefs.WHIRL;
  z.shape = sh;
  z.follow = true;
  z.h = h;
  z.name = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.WHIRL, sh);
  z.amount = h * @PKG@.AbilNum.WW_POWER * cxm();
  z.d1 = sh == 3 ? @PKG@.AbilNum.WW_GRINDEVERY : @PKG@.AbilNum.WW_EVERY;
  z.pct = stag ? 0.0 : @PKG@.AbilNum.WW_HEAL + 5.0 * (double) (c == null ? 0 : c.eff(@PKG@.AbilModDefs.LEECH));
  z.n1 = c == null ? 0 : c.eff(@PKG@.AbilModDefs.PULL);
  z.n2 = bleed ? 1 : 0;
  z.n3 = stag ? 1 : 0;
  z.nextHeal = now;
  z.hit = new java.util.HashSet();
  aw.addZone(z);
  @PKG@.AbilStore.SPINS.put(u, z);
  if (sh == 3) effect(acc, ref, "Root", secs);
  particle(FX_SPIN, me[0], me[1] + 1.0, me[2], acc);
  if (pr != null) say(pr, z.name + ": " + @PKG@.AbilMath.fmt(secs) + " s, " + @PKG@.AbilMath.fmt(r) + " blocks" + (z.pct > 0.0 ? ", heals " + @PKG@.AbilMath.fmt(z.pct) + " % of it." : "."));
  LAST_BER = "spin " + z.name + " r=" + @PKG@.AbilMath.fmt(r);
  return " r=" + @PKG@.AbilMath.fmt(r) + " tick=" + @PKG@.AbilMath.fmt(z.amount) + " every=" + @PKG@.AbilMath.fmt(z.d1) + " heal=" + @PKG@.AbilMath.fmt(z.pct) + (bleed ? " bleed" : "") + (stag ? " stagger" : "");
}''')
late24(r'''
public static boolean spinTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  boolean ok = live(cb, cr, z.caster, z.pkey);
  @PKG@.AbilCtx c = z.cx;
  if (!ok || z.ended || now >= z.until) {
    if (@PKG@.AbilStore.SPINS.get(z.caster) == z) @PKG@.AbilStore.SPINS.remove(z.caster);
    if (ok && !"replaced".equals(z.why) && c != null && !c.echo && c.echoPct > 0.0) {   // Echo: a weaker spin 1 s after the spin ends
      @PKG@.AbilCtx e = c.echoOf(c.echoPct);
      @PKG@.AbilJob ej = new @PKG@.AbilJob(10, now + ms(@PKG@.AbilCfg.ECHO_DELAY), z.caster, "Whirlwind", z.x, z.y, z.z, z.r, z.h);
      ej.pkey = z.pkey;
      ej.ai = @PKG@.AbilDefs.WHIRL;
      ej.sh = z.shape == 3 ? 3 : 0;
      ej.cx = e;
      @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
      if (aw != null) aw.add(ej);
    }
    @PR@ pr = prOf(z.caster);
    if (pr != null && ok && !"replaced".equals(z.why)) say(pr, (c != null && c.echo ? "Echo spin" : z.name) + ": " + z.hits + (z.hits == 1 ? " hit." : " hits."));
    LAST_BER = "spin end " + z.hits;
    return false;
  }
  zoneFollow(z, cb);
  if (now < z.nextHeal) return true;
  z.nextHeal = now + ms(z.d1);
  java.util.List l = near(cb, z.x, z.y, z.z, z.r);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  double dealt = 0.0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    @VEC@ q = pos(cb, t);
    if (q == null || !@PKG@.AbilMath.inRange(q.x - z.x, q.y - z.y, q.z - z.z, z.r + 0.5)) continue;
    if (hit(cb, t, cr, z.caster, z.amount, "Whirlwind")) { n++; dealt = dealt + z.amount; }
    {
      double dx = q.x - z.x;
      double dz = q.z - z.z;
      double d = Math.sqrt(dx * dx + dz * dz);
      if (d > 0.6 && z.n1 > 0) push(cb, t, -dx / d * (double) z.n1 * @PKG@.AbilCfg.PUSH_PER_BLOCK * 0.5, 0.2, -dz / d * (double) z.n1 * @PKG@.AbilCfg.PUSH_PER_BLOCK * 0.5);
      else if (z.n3 == 1 && d > 0.05) push(cb, t, dx / d * @PKG@.AbilCfg.PUSH_PER_BLOCK, 0.3, dz / d * @PKG@.AbilCfg.PUSH_PER_BLOCK);
    }
    if (z.n2 == 1) bleedOn(cb, t, z.caster, z.pkey, z.h * @PKG@.AbilNum.WW_BLEED * cxm(), now);
  }
  z.hits = z.hits + n;
  SPINHITS = SPINHITS + (long) n;
  if (dealt > 0.0 && z.pct > 0.0) apply(cb, cr, dealt * z.pct / 100.0, dealt * z.pct / 100.0);
  if (n > 0 && !z.echoed && (c == null || !c.echo)) { z.echoed = true; used(z.caster, z.pkey, @PKG@.AbilDefs.WHIRL, c); }
  particle(z.shape == 3 ? FX_GRIND : FX_SPIN, z.x, z.y + 1.0, z.z, cb);
  return true;
}''')
# Bleed (Berserker PB2): 0.2 H a second for 4 s (job kind 22, one per mob; a new hit refreshes it)
late24(r'''
public static boolean bleedOn(@CB@ cb, @REF@ t, java.util.UUID u, String k, double perSec, long now) {
  Object o = @PKG@.AbilStore.BLEEDS.get(t);
  long until = now + ms(@PKG@.AbilNum.WW_BLEEDTIME);
  if (o instanceof long[] && ((long[]) o)[0] > now) { ((long[]) o)[0] = until; return false; }
  @PKG@.AbilStore.BLEEDS.put(t, new long[] { until });
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(cb.getExternalData()));
  @PKG@.AbilJob j = new @PKG@.AbilJob(22, now + 1000L, u, "Whirlwind", 0.0, 0.0, 0.0, 0.0, perSec);
  j.pkey = k;
  j.ai = @PKG@.AbilDefs.WHIRL;
  j.tref = t;
  j.every = 1000L;
  aw.add(j);
  return true;
}''')
late24(r'''
public static boolean bleedTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey) || !(j.tref instanceof @REF@)) return false;
  @REF@ t = (@REF@) j.tref;
  Object o = @PKG@.AbilStore.BLEEDS.get(t);
  if (!(o instanceof long[]) || ((long[]) o)[0] <= now || !enemy(cb, t, cr)) { @PKG@.AbilStore.BLEEDS.remove(t); return false; }
  hit(cb, t, cr, j.caster, j.amount, "Whirlwind");
  j.at = now + 1000L;
  return true;
}''')

# ---------------------------------------------------------------- EARTHSPLITTER (job kind 19; Fissure 1 s later)
late24(r'''
public static String splitCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, double[] at, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double[] me = at != null && sh == 2 ? at : here(st, ref);
  double[] f = flat(st, ref);
  if (me == null) return " nopos";
  double pw = sh == 1 ? @PKG@.AbilNum.ES_SPRINTPOWER : (sh == 3 ? @PKG@.AbilNum.ES_FISSUREPOWER : @PKG@.AbilNum.ES_POWER);
  double amt = h * pw * cxm();
  String pact = "";
  if (nd(c, "Berserker", "PB4")) {   // Blood Pact: pay 10 % of your current Health for +30 % (it cannot kill you)
    @ESM@ m = map(st, ref);
    double hp = cur(m, @DST@.getHealth());
    double cost = hp * @PKG@.AbilNum.ES_PACTCOST / 100.0;
    if (hp - cost < 1.0) cost = hp - 1.0;
    if (cost > 0.0 && m != null) { m.subtractStatValue(@DST@.getHealth(), (float) cost); amt = amt * (1.0 + @PKG@.AbilNum.ES_PACTBONUS / 100.0); pact = " pact=" + @PKG@.AbilMath.fmt(cost); }
  }
  @PKG@.AbilJob j = new @PKG@.AbilJob(19, now + (sh == 3 ? ms(@PKG@.AbilNum.ES_WIND) : 0L), u, "Earthsplitter", me[0], me[1], me[2], 0.0, amt);
  j.pkey = k;
  j.ai = @PKG@.AbilDefs.ESPLIT;
  j.sh = sh;
  boolean seis = nd(c, "Berserker", "PC2");
  j.len = (sh == 1 ? @PKG@.AbilNum.ES_SPRINTLENGTH : (sh == 3 ? @PKG@.AbilNum.ES_FISSURELENGTH : @PKG@.AbilNum.ES_LENGTH)) * (seis ? 0.75 : 1.0) + cxr();
  j.width = seis ? 3.0 : (sh == 1 ? @PKG@.AbilNum.ES_SPRINTWIDTH : @PKG@.AbilNum.ES_WIDTH);
  j.r = sh == 2 ? @PKG@.AbilNum.ES_CRATERRADIUS + cxr() : 0.0;
  j.dx = f == null ? 0.0 : f[0];
  j.dz = f == null ? 1.0 : f[1];
  aw.add(j);
  if (sh == 3 && pr != null) say(pr, "Fissure: the ground cracks in " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.ES_WIND) + " s...");
  return " len=" + @PKG@.AbilMath.fmt(j.len) + " width=" + @PKG@.AbilMath.fmt(j.width) + " hit=" + @PKG@.AbilMath.fmt(amt) + pact;
}''')
late24(r'''
public static int splitRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_BER = "split gone"; return -1; }
  @PKG@.AbilCtx c = j.cx;
  double hp = cur(map(cb, cr), @DST@.getHealth());
  double mx = max(map(cb, cr), @DST@.getHealth());
  double miss = mx > 0.0 && hp >= 0.0 ? (1.0 - hp / mx) * 100.0 : 0.0;
  if (miss > @PKG@.AbilNum.ES_MISSINGCAP) miss = @PKG@.AbilNum.ES_MISSINGCAP;
  if (miss < 0.0) miss = 0.0;
  double amt = j.amount * (1.0 + miss / 100.0);
  int sp = c == null ? 0 : c.lv(@PKG@.AbilModDefs.SPLIT);
  int kb = c == null ? 0 : c.eff(@PKG@.AbilModDefs.KNOCK);
  int sl = c == null ? 0 : c.eff(@PKG@.AbilModDefs.SLOW);
  double up = @PKG@.AbilNum.ES_UP * @PKG@.AbilCfg.PUSH_PER_BLOCK;
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  int lines = sp > 0 && j.sh != 2 ? 3 : 1;
  for (int ln = 0; ln < lines; ln++) {
    double ang = ln == 0 ? 0.0 : Math.toRadians(ln == 1 ? @PKG@.AbilNum.ES_SPLITANGLE : -@PKG@.AbilNum.ES_SPLITANGLE);
    double dx = j.dx * Math.cos(ang) - j.dz * Math.sin(ang);
    double dz = j.dx * Math.sin(ang) + j.dz * Math.cos(ang);
    double fac = ln == 0 ? 1.0 : (50.0 + 10.0 * (double) (sp - 1)) / 100.0;
    double reach = j.sh == 2 ? j.r : j.len;
    java.util.List l = near(cb, j.x, j.y, j.z, reach + 1.0);
    for (int i = 0; i < l.size(); i++) {
      Object o = l.get(i);
      if (!(o instanceof @REF@)) continue;
      @REF@ t = (@REF@) o;
      if (seen.contains(t) || !enemy(cb, t, cr)) continue;
      @VEC@ q = pos(cb, t);
      if (q == null) continue;
      double vx = q.x - j.x;
      double vz = q.z - j.z;
      if (j.sh == 2) { if (vx * vx + vz * vz > j.r * j.r) continue; }
      else {
        double along = vx * dx + vz * dz;
        double side = Math.abs(vx * dz - vz * dx);
        if (along < -0.5 || along > j.len || side > j.width / 2.0 + 0.5) continue;
      }
      seen.add(t);
      if (hit(cb, t, cr, j.caster, amt * fac, "Earthsplitter")) n++;
      double hl = Math.sqrt(vx * vx + vz * vz);
      double f = 2.0 * (double) kb * @PKG@.AbilCfg.PUSH_PER_BLOCK;
      if (hl > 0.05) push(cb, t, vx / hl * f, up, vz / hl * f);
      else push(cb, t, 0.0, up, 0.0);
      double slow = (j.sh == 3 ? @PKG@.AbilNum.ES_FISSURESLOW : 0.0) + (sl > 0 ? 1.0 + (double) sl : 0.0);
      if (slow > 0.0) effect(cb, t, EF_SLOW, slow);
    }
    if (j.sh != 2) for (int s2 = 1; s2 <= 4; s2++) particle(FX_SPLIT, j.x + dx * j.len * (double) s2 / 4.0, j.y + 0.1, j.z + dz * j.len * (double) s2 / 4.0, cb);
  }
  particle(j.sh == 2 ? FX_CRATER : FX_SPLIT0, j.x, j.y + 0.1, j.z, cb);
  if (nd(c, "Berserker", "PC4") && j.sh != 2) {   // Ground Pound: the end of the line slams
    double ex = j.x + j.dx * j.len;
    double ez = j.z + j.dz * j.len;
    java.util.List l2 = near(cb, ex, j.y, ez, @PKG@.AbilNum.ES_POUNDRADIUS);
    for (int i = 0; i < l2.size(); i++) {
      Object o = l2.get(i);
      if (!(o instanceof @REF@) || !enemy(cb, (@REF@) o, cr)) continue;
      @VEC@ w2 = pos(cb, (@REF@) o);
      if (w2 == null || !@PKG@.AbilMath.inRange(w2.x - ex, w2.y - j.y, w2.z - ez, @PKG@.AbilNum.ES_POUNDRADIUS)) continue;
      if (hit(cb, (@REF@) o, cr, j.caster, (c == null ? 25.0 : c.h) * @PKG@.AbilNum.ES_POUNDPOWER * cxm(), "Earthsplitter")) n++;
      stunMob(cb, (@REF@) o, j.caster, 1.0, now);
    }
    particle(FX_CRATER, ex, j.y + 0.1, ez, cb);
  }
  SPLITS = SPLITS + 1L;
  if (n > 0) used(j.caster, j.pkey, @PKG@.AbilDefs.ESPLIT, c);
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.ESPLIT, j.sh) + ": " + n + (n == 1 ? " enemy" : " enemies") + " knocked up" + (miss >= 1.0 ? " (+" + @PKG@.AbilMath.fmt(miss) + " % - your missing Health)." : "."));
  LAST_BER = "split " + n + " lines=" + lines + " miss=" + @PKG@.AbilMath.fmt(miss);
  return n;
}''')

# ---------------------------------------------------------------- BLOOD FRENZY (zone kind 17 = the toggle aura)
late24(r'''
public static String frenzyAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double[] me = here(acc, ref);
  if (me == null || aw == null) return " nopos";
  Object old = @PKG@.AbilStore.FRENZ.get(u);
  if (old instanceof @PKG@.AbilZone) { ((@PKG@.AbilZone) old).ended = true; ((@PKG@.AbilZone) old).why = "replaced"; }
  int mx = (int) @PKG@.AbilNum.BF_MAX;
  if (mx < 1) mx = 1;
  int st0 = sh == 1 ? (int) @PKG@.AbilNum.BF_CHARGESTACKS : (sh == 2 ? (int) @PKG@.AbilNum.BF_LANDSTACKS : 0);
  if (sh == 3) {
    Object bo = @PKG@.AbilStore.BANKED.get(k);   // FIX ROUND 2: by the profile key (PROFILES-CONTRACT rule 2)
    if (bo instanceof double[] && (double) now - ((double[]) bo)[1] < @PKG@.AbilNum.BF_BANKWINDOW * 1000.0) st0 = (int) Math.floor(((double[]) bo)[0] * @PKG@.AbilNum.BF_BANKSHARE / 100.0);
  }
  if (st0 > mx) st0 = mx;
  @PKG@.AbilZone z = new @PKG@.AbilZone(17, u, me[0], me[1], me[2], 1.0, now, now + 86400000L);
  z.pkey = k;
  z.ai = @PKG@.AbilDefs.FRENZY;
  z.shape = sh;
  z.follow = true;
  z.name = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.FRENZY, sh);
  z.ring = new long[mx];
  for (int i = 0; i < st0; i++) z.ring[i] = now;
  z.total = st0;
  z.t1 = now;
  z.d1 = (sh == 3 ? @PKG@.AbilNum.BF_BANKPLAYERS : @PKG@.AbilNum.BF_PLAYERS) + cxr();
  z.d2 = (sh == 3 ? @PKG@.AbilNum.BF_BANKPARTY : @PKG@.AbilNum.BF_PARTY) + cxr();
  z.pct = nd(c, "Berserker", "PB3") ? 1.2 : 1.0;
  int fl = c == null ? 0 : c.lv(@PKG@.AbilModDefs.FLOOR);
  z.n1 = fl <= 0 ? 0 : (fl == 1 ? 5 : 10);
  z.n2 = st0;
  z.n3 = c == null ? 0 : c.lv(@PKG@.AbilModDefs.HASTE);
  z.d3 = c == null ? 0.0 : 2.0 * (double) c.eff(@PKG@.AbilModDefs.LEECH);
  z.list = new java.util.ArrayList();
  z.nextHeal = now;
  aw.addZone(z);
  @PKG@.AbilStore.FRENZ.put(u, z);
  particle(FX_RAGE, me[0], me[1] + 1.0, me[2], acc);
  if (pr != null) say(pr, z.name + " ON" + (st0 > 0 ? " (" + st0 + " stacks)" : "") + " - every hit a stack; press again to turn it off.");
  LAST_BER = "frenzy on " + z.name + " stacks=" + st0;
  return " stacks=" + st0 + " aura=" + @PKG@.AbilMath.fmt(z.d1) + "/" + @PKG@.AbilMath.fmt(z.d2) + (z.n1 > 0 ? " floor=" + z.n1 : "");
}''')
late24(r'''
public static String frenzyOff(@PR@ pr, java.util.UUID u, String k, long now) {
  Object o = @PKG@.AbilStore.FRENZ.get(u);
  if (!(o instanceof @PKG@.AbilZone)) return "noop";
  @PKG@.AbilZone z = (@PKG@.AbilZone) o;
  z.ended = true;
  z.why = "off";
  long cd = @PKG@.AbilDefs.cdMs(@PKG@.AbilDefs.FRENZY, 0);
  @PKG@.AbilStore.arm(k, "BloodFrenzy", now, cd);
  if (pr != null) say(pr, "Blood Frenzy off - it can go on again in " + @PKG@.AbilMath.secs(cd) + " s.");
  LAST_BER = "frenzy off";
  return "ok:BloodFrenzy off cd=" + cd;
}''')
late24(r'''
public static int frenzyStacks(@PKG@.AbilZone z, long now) {
  if (z == null || z.ring == null) return 0;
  double dm = z.cx == null ? 1.0 : z.cx.durMult;
  return @PKG@.AbilMath.live(z.ring, now, Math.round(@PKG@.AbilNum.BF_DECAY * dm * 1000.0));
}''')
# FIX ROUND (critic: LOCKED Skyy 2026-10-07 "make the ability cost mana and stamina per attack (regardless of weather you hit or not.)"):
# the per-swing cost is taken when the swing STARTS - the Primary InteractionChainStartEvent our AbilRuneSys already listens to (VERIFIED:
# InteractionManager.syncStart fires it for EVERY client-started chain, any InteractionType, after the cooldown check), so a miss pays too;
# a landed hit with no swing-start payment in the last PAY_MS (the start hook missed it) still pays here, so a cost is never skipped.
late24(r'''
public static String frenzyPay(@PKG@.AbilZone z, @CB@ buf, @REF@ att) {
  boolean free = @PKG@.AbilCfg.CREATIVE_FREE && creative(buf, att);
  if (free) return null;
  @ESM@ m = map(buf, att);
  double cm = @PKG@.AbilNum.BF_HITMANA * z.pct * (z.cx == null ? 1.0 : z.cx.costMult);
  double cs = @PKG@.AbilNum.BF_HITSTAM * z.pct * (z.cx == null || z.cx.costMult > 1.0 ? 1.0 : z.cx.costMult);
  double mana = cur(m, @DST@.getMana());
  double stam = cur(m, @DST@.getStamina());
  if (mana >= 0.0 && mana < cm) { z.ended = true; z.why = "mana"; return "out of mana"; }
  if (stam >= 0.0 && stam < cs) { z.ended = true; z.why = "stamina"; return "out of stamina"; }
  if (m != null) { if (cm > 0.0) m.subtractStatValue(@DST@.getMana(), (float) cm); if (cs > 0.0) m.subtractStatValue(@DST@.getStamina(), (float) cs); }
  return null;
}''')
late24(r'''
public static boolean frenzyPaid(java.util.UUID u, long now) {
  Object o = u == null ? null : @PKG@.AbilStore.PAID.remove(u);   // FIX ROUND 2: consumed - one swing-start payment covers ONE landed swing
  if (!(o instanceof Long)) return false;
  long t = ((Long) o).longValue();
  return now >= t && now - t < 3000L;
}''')
late24(r'''
public static String frenzySwing(@REF@ r, @CB@ buf, long now) {
  try {
    if (r == null || !r.isValid() || @PKG@.AbilStore.FRENZ.isEmpty()) return null;
    Object po = buf.getComponent(r, @PR@.getComponentType());
    if (!(po instanceof @PR@)) return null;
    java.util.UUID u = ((@PR@) po).getUuid();
    Object o = u == null ? null : @PKG@.AbilStore.FRENZ.get(u);
    if (!(o instanceof @PKG@.AbilZone)) return null;
    @PKG@.AbilZone z = (@PKG@.AbilZone) o;
    if (z.ended) return null;
    String h = hand(buf, r);
    if (h != null && h.startsWith("Tool_")) return "tool";   // mining / chopping with a tool is not an attack
    String p = frenzyPay(z, buf, r);
    if (p != null) return p;
    @PKG@.AbilStore.PAID.put(u, Long.valueOf(now));
    FRENZYSWINGS = FRENZYSWINGS + 1L;
    return "paid";
  } catch (Throwable t) { return null; }
}''')
late24(r'''
public static String onSwing(@ICSE@ e, @REF@ r, @CB@ buf, long now) {
  if (e == null || e.isCancelled() || @PKG@.AbilStore.FRENZ.isEmpty()) return null;
  return frenzySwing(r, buf, now);
}''')
late24(r'''
public static String frenzyHit(@PKG@.AbilZone z, @CB@ buf, @REF@ att, double amt, long now) {
  if (z == null || z.ended || z.ring == null || z.ring.length == 0) return null;
  Object so = @PKG@.AbilStore.SWINGS.get(z.caster);
  if (so instanceof Long && now - ((Long) so).longValue() < 150L && now >= ((Long) so).longValue()) return "same swing";
  @PKG@.AbilStore.SWINGS.put(z.caster, Long.valueOf(now));
  if (!frenzyPaid(z.caster, now)) {   // FIX ROUND: the swing start already paid (hit or miss) - else pay here
    String p = frenzyPay(z, buf, att);
    if (p != null) return p;
  }
  int o = 0;
  for (int i = 1; i < z.ring.length; i++) if (z.ring[i] < z.ring[o]) o = i;
  z.ring[o] = now;
  z.total = z.total + 1;
  FRENZYHITS = FRENZYHITS + 1L;
  if (z.cx != null && nd(z.cx, "Berserker", "PB3")) {   // Crimson Frenzy: every stack heals you 0.5 %, allies in the aura 0.25 %
    double mx = max(map(buf, att), @DST@.getHealth());
    if (mx > 0.0) apply(buf, att, mx * 0.005, mx * 0.005);
    for (int i = 0; z.list != null && i < z.list.size(); i++) {
      @REF@ r = casterRef(buf, (java.util.UUID) z.list.get(i));
      if (r == null || !r.isValid() || !healable(buf, r)) continue;
      double am = max(map(buf, r), @DST@.getHealth());
      if (am > 0.0) apply(buf, r, am * 0.0025, am * 0.0025);
    }
  }
  if (z.d3 > 0.0 && amt > 0.0) apply(buf, att, amt * z.d3 / 100.0, amt * z.d3 / 100.0);
  return "stack " + frenzyStacks(z, now);
}''')
late24(r'''
public static boolean frenzyTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  boolean ok = live(cb, cr, z.caster, z.pkey);
  if (!ok) z.why = "left";
  if (ok && !z.ended) {
    zoneFollow(z, cb);
    boolean free = @PKG@.AbilCfg.CREATIVE_FREE && creative(cb, cr);
    long dt = now - z.t1;
    if (dt < 0L) dt = 0L;
    z.t1 = now;
    if (!free && dt > 0L) {
      @ESM@ m = map(cb, cr);
      double dm = @PKG@.AbilNum.BF_DRAINMANA * z.pct * (double) dt / 1000.0;
      double ds = @PKG@.AbilNum.BF_DRAINSTAM * z.pct * (double) dt / 1000.0;
      double mana = cur(m, @DST@.getMana());
      double stam = cur(m, @DST@.getStamina());
      if (mana >= 0.0 && dm > 0.0) { if (mana < dm) { z.ended = true; z.why = "mana"; } else m.subtractStatValue(@DST@.getMana(), (float) dm); }
      if (!z.ended && stam >= 0.0 && ds > 0.0) { if (stam < ds) { z.ended = true; z.why = "stamina"; } else m.subtractStatValue(@DST@.getStamina(), (float) ds); }
    }
  }
  int stk = frenzyStacks(z, now);
  if (!ok || z.ended) {
    if (@PKG@.AbilStore.FRENZ.get(z.caster) == z) {
      @PKG@.AbilStore.FRENZ.remove(z.caster);
      @PKG@.AbilStore.FURY.remove(z.caster);
      if (ok) speedClear(cb, cr, z.caster);
      @PKG@.AbilStore.BANKED.put(z.pkey, new double[] { (double) stk, (double) now });   // FIX ROUND: only while it was still the live one (a quit removed it); FIX ROUND 2: by pkey
    }
    if (!"off".equals(z.why) && !"replaced".equals(z.why) && !"left".equals(z.why)) {   // out of Mana / Stamina: the 10 s wait starts now
      @PKG@.AbilStore.arm(z.pkey, "BloodFrenzy", now, @PKG@.AbilDefs.cdMs(@PKG@.AbilDefs.FRENZY, 0));
      @PR@ pr = prOf(z.caster);
      if (pr != null) say(pr, "Blood Frenzy ended - out of " + ("mana".equals(z.why) ? "Mana" : "Stamina") + " (" + stk + " stacks).");
    }
    LAST_BER = "frenzy end " + z.why + " stacks=" + stk;
    return false;
  }
  if (z.n1 > 0 && z.n2 >= z.n1 && stk < z.n1) {   // Floor: once reached, never below it
    for (int i = 0; i < z.ring.length && stk < z.n1; i++) {
      if (z.ring[i] > 0L && now - z.ring[i] < Math.round(@PKG@.AbilNum.BF_DECAY * (z.cx == null ? 1.0 : z.cx.durMult) * 1000.0)) continue;
      z.ring[i] = now;
      stk++;
    }
  }
  if (stk > z.n2) z.n2 = stk;
  double main = z.cx == null ? 1.0 : z.cx.main;
  double dmg = (double) stk * @PKG@.AbilNum.BF_DMG * main;
  double mv = (double) stk * @PKG@.AbilNum.BF_MOVE * main;
  @PKG@.AbilStore.FURY.put(z.caster, new double[] { dmg, (double) (now + 700L) });
  int pct = (int) Math.round(mv) + (z.n3 > 0 && (double) stk >= @PKG@.AbilNum.BF_HASTEAT ? (int) @PKG@.AbilNum.BF_HASTESPEED : 0);
  speedFlow(cb, cr, z.caster, pct, now);
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  pickAllies(st, cb, z.caster, new double[] { z.x, z.y, z.z }, z.d2, z.d1, us, rs);
  z.list = new java.util.ArrayList();
  double share = @PKG@.AbilNum.BF_ALLY / 100.0;
  for (int i = 0; i < us.size(); i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    if (t.equals(z.caster)) continue;
    z.list.add(t);
    if (stk <= 0) continue;
    @PKG@.AbilStore.FURY.put(t, new double[] { dmg * share, (double) (now + 700L) });
    int ap = (int) Math.round(mv * share);
    if (ap > 0) speedKeep(cb, (@REF@) rs.get(i), t, ap, 1.5);
  }
  if (!z.echoed && (double) z.n2 >= @PKG@.AbilNum.BF_COUNTAT) { z.echoed = true; used(z.caster, z.pkey, @PKG@.AbilDefs.FRENZY, z.cx); }
  if (now >= z.nextFx) { z.nextFx = now + 1000L; if (stk > 0) particle(FX_RAGE, z.x, z.y + 1.0, z.z, cb); }
  return true;
}''')

# ---------------------------------------------------------------- WARLORD'S BANNER (zone kind 18)
late24(r'''
public static String bannerAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, double[] at, int sh, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  if (at == null || aw == null) return " nopos";
  Object old = @PKG@.AbilStore.BANNERS.get(u);
  if (old instanceof @PKG@.AbilZone) { ((@PKG@.AbilZone) old).ended = true; ((@PKG@.AbilZone) old).why = "replaced"; }
  boolean bearer = nd(c, "Berserker", "PA3");
  double r = (sh == 3 ? @PKG@.AbilNum.WB_ROOTEDRADIUS : @PKG@.AbilNum.WB_RADIUS) + cxr() + (sh == 2 ? @PKG@.AbilNum.WB_LANDADD : 0.0);
  double secs = cxds((sh == 3 ? @PKG@.AbilNum.WB_ROOTEDTIME : @PKG@.AbilNum.WB_TIME) - (bearer ? @PKG@.AbilNum.WB_TIME - @PKG@.AbilNum.WB_BEARERTIME : 0.0));   // Banner Bearer: 5 s shorter
  @PKG@.AbilZone z = new @PKG@.AbilZone(18, u, at[0], at[1], at[2], r, now, now + ms(secs));
  z.pkey = k;
  z.ai = @PKG@.AbilDefs.BANNER;
  z.shape = sh;
  z.name = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.BANNER, sh);
  z.pct = c == null ? 1.0 : c.main;
  z.t1 = now + ms(@PKG@.AbilNum.WB_CAP);
  z.d1 = c == null ? 0.0 : 3.0 * (double) c.lv(@PKG@.AbilModDefs.WARD);
  z.n1 = bearer ? 1 : 0;
  z.seen2 = new java.util.HashSet();
  z.hit = new java.util.HashSet();
  z.nextHeal = now;
  z.t3 = now;
  aw.addZone(z);
  @PKG@.AbilStore.BANNERS.put(u, z);
  for (int i = 0; i < 4; i++) particle(FX_BANNER, at[0], at[1] + (double) i * 0.8, at[2], acc);
  ring(FX_RALLY, z, acc);
  if (pr != null) say(pr, z.name + ": " + @PKG@.AbilMath.fmt(r) + " blocks, " + @PKG@.AbilMath.fmt(secs) + " s - +" + @PKG@.AbilMath.fmt(@PKG@.AbilNum.WB_SELF * z.pct) + " % damage and defence for you, +" + @PKG@.AbilMath.fmt(@PKG@.AbilNum.WB_PARTY * z.pct) + " % your party, +" + @PKG@.AbilMath.fmt(@PKG@.AbilNum.WB_PLAYERS * z.pct) + " % others" + (sh == 3 ? " (leaving only pauses yours)." : " - it falls if you leave its range."));
  LAST_BER = "banner " + z.name + " r=" + @PKG@.AbilMath.fmt(r) + " secs=" + @PKG@.AbilMath.fmt(secs);
  return " r=" + @PKG@.AbilMath.fmt(r) + " secs=" + @PKG@.AbilMath.fmt(secs) + " main=" + @PKG@.AbilMath.fmt(z.pct) + (bearer ? " bearer" : "");
}''')
late24(r'''
public static void bannerEnd(@PKG@.AbilZone z, @CB@ cb, long now) {
  if ("world".equals(z.why) || "quit".equals(z.why)) { z.ended = true; return; }   // FIX ROUND: worldLeft already ended it (cooldown armed, line sent); FIX ROUND 2: a quit arms nothing
  z.ended = true;
  if (@PKG@.AbilStore.BANNERS.get(z.caster) == z) @PKG@.AbilStore.BANNERS.remove(z.caster);
  if (!"replaced".equals(z.why)) @PKG@.AbilStore.arm(z.pkey, "WarlordsBanner", now, cdCx(z.cx, @PKG@.AbilDefs.BANNER, z.shape));   // 40 s from the fall
  @PKG@.AbilCtx c = z.cx;
  int en = 0;
  if (c != null && !c.echo && c.echoPct > 0.0 && !"replaced".equals(z.why)) {   // Echo: the buff lingers on everyone who was in range
    long eu = now + ms(@PKG@.AbilNum.WB_ECHOTIME);
    java.util.Iterator it = z.hit.iterator();
    while (it.hasNext()) {
      java.util.UUID t = (java.util.UUID) it.next();
      Object wo = @PKG@.AbilStore.WAR.get(t);
      double p = wo instanceof double[] ? ((double[]) wo)[0] : 0.0;
      if (!(p > 0.0)) continue;
      @PKG@.AbilStore.WAR.put(t, new double[] { p * c.echoPct, p * c.echoPct, (double) eu });
      en++;
    }
    if (en > 0) ECHOES = ECHOES + 1L;
  }
  @PR@ pr = prOf(z.caster);
  if (pr != null && !"replaced".equals(z.why) && !"gone".equals(z.why)) say(pr, "Your banner fell" + ("range".equals(z.why) ? " - you left its range" : "") + (z.hits > 0 ? " (" + z.hits + (z.hits == 1 ? " kill" : " kills") + " kept it up)" : "") + (en > 0 ? " - its echo lingers on " + en + "." : "."));
  LAST_BER = "banner end " + z.why + " kills=" + z.hits + " echo=" + en;
}''')
late24(r'''
public static boolean bannerTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  boolean ok = live(cb, cr, z.caster, z.pkey);
  if (!ok && (z.why == null || z.why.length() == 0)) z.why = "gone";
  @VEC@ p = ok ? pos(cb, cr) : null;
  boolean inside = p != null && @PKG@.AbilMath.inRange(p.x - z.x, p.y - z.y, p.z - z.z, z.r);
  if (ok && !z.ended && !inside && z.shape != 3) { z.ended = true; z.why = "range"; }
  if (!ok || z.ended || now >= z.until) {
    if (z.why == null || z.why.length() == 0) z.why = "time";
    bannerEnd(z, cb, now);
    return false;
  }
  double m = z.pct;
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  gatherAt(st, cb, new double[] { z.x, z.y, z.z }, z.r, us, rs);
  z.hit = new java.util.HashSet();
  boolean heal = z.n1 == 1 && now >= z.nextHeal;
  if (heal) z.nextHeal = now + 1000L;
  boolean ward = z.d1 > 0.0 && now >= z.t3;
  if (ward) z.t3 = now + 10000L;
  for (int i = 0; i < us.size(); i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    @REF@ r = (@REF@) rs.get(i);
    if (!alive(cb, r)) continue;
    boolean self = t.equals(z.caster);
    double tier = self ? @PKG@.AbilNum.WB_SELF : (@PKG@.HealTask.inParty(z.caster, t) ? @PKG@.AbilNum.WB_PARTY : @PKG@.AbilNum.WB_PLAYERS);
    @PKG@.AbilStore.WAR.put(t, new double[] { tier * m, tier * m, (double) (now + 700L) });
    z.hit.add(t);
    if (heal) { double mx = max(map(cb, r), @DST@.getHealth()); if (mx > 0.0 && healable(cb, r)) z.absorbed = z.absorbed + apply(cb, r, mx * @PKG@.AbilNum.WB_BEARERHEAL / 100.0, mx * @PKG@.AbilNum.WB_BEARERHEAL / 100.0); }
    if (ward) { double mx = max(map(cb, r), @DST@.getHealth()); if (mx > 0.0) wardGive(t, mx * z.d1 / 100.0, now + 10000L); }
  }
  if (!z.echoed && now - z.start >= 10000L) { z.echoed = true; used(z.caster, z.pkey, @PKG@.AbilDefs.BANNER, z.cx); }
  if (now >= z.nextFx) {
    z.nextFx = now + 1000L;
    particle(FX_BANNER, z.x, z.y + 1.5, z.z, cb);
    particle(FX_BANNER, z.x, z.y + 2.5, z.z, cb);
    ring(FX_RALLY, z, cb);
  }
  return true;
}''')
# every mob killed in a banner's range: +1 s (mini-boss = Boss Hunter's elite words +3 s, boss +5 s), the whole banner at most 60 s
late24(r'''
public static String bannerKill(@CAC@ acc, @REF@ t, long now) {
  @VEC@ q = pos(acc, t);
  if (q == null) return null;
  @PKG@.AbilWorld aw = null;
  try { aw = @PKG@.AbilWorld.at(t.getStore()); } catch (Throwable x0) { aw = null; }
  String out = null;
  java.util.Iterator it = new java.util.ArrayList(@PKG@.AbilStore.BANNERS.values()).iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @PKG@.AbilZone)) continue;
    @PKG@.AbilZone z = (@PKG@.AbilZone) o;
    if (z.ended || z.seen2 == null || z.seen2.contains(t) || !@PKG@.AbilMath.inRange(q.x - z.x, q.y - z.y, q.z - z.z, z.r)) continue;
    if (aw == null || !aw.holds(z)) continue;   // FIX ROUND: same x / y / z in ANOTHER world is not in range
    z.seen2.add(t);
    String role = roleOf(acc, t);
    double add = @PKG@.AbilMath.bossRole(role, @PKG@.AbilCfg.BOSS_WORDS) ? @PKG@.AbilNum.WB_BOSSADD : (@PKG@.AbilMath.bossRole(role, @PKG@.AbilCfg.GK_ELITE) ? @PKG@.AbilNum.WB_MINIADD : @PKG@.AbilNum.WB_KILLADD);
    long nu = z.until + ms(add);
    if (nu > z.t1) nu = z.t1;
    if (nu > z.until) z.until = nu;
    z.hits = z.hits + 1;
    BANNERKILLS = BANNERKILLS + 1L;
    out = "banner+" + @PKG@.AbilMath.fmt(add);
  }
  return out;
}''')
# the landed hook (AbilFrostSys, Inspect group): Blood Frenzy stacks + cost, Enrage's leech + its counted use, banner kills
late24(r'''
public static String hitLanded2(@CB@ buf, @REF@ t, @DMG@ d, long now) {
  try {
    if (d == null || t == null || d.isCancelled() || !(d.getAmount() > 0.0f)) return null;
    if (buf.getComponent(t, @NPC@.getComponentType()) == null) return null;
    String out = "";
    if (!@PKG@.AbilStore.BANNERS.isEmpty() && !alive(buf, t)) { String bk = bannerKill(buf, t, now); if (bk != null) out = bk; }
    if (@PKG@.AbilDmg.mine(d)) return out.length() == 0 ? null : out;
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DENT@)) return out.length() == 0 ? null : out;
    @REF@ att = ((@DENT@) src).getRef();
    if (att == null || !att.isValid() || att.equals(t)) return out.length() == 0 ? null : out;
    Object po = buf.getComponent(att, @PR@.getComponentType());
    if (!(po instanceof @PR@)) return out.length() == 0 ? null : out;
    java.util.UUID u = ((@PR@) po).getUuid();
    if (u == null) return out.length() == 0 ? null : out;
    double amt = (double) d.getAmount();
    Object fz = @PKG@.AbilStore.FRENZ.get(u);
    if (fz instanceof @PKG@.AbilZone) { String f = frenzyHit((@PKG@.AbilZone) fz, buf, att, amt, now); if (f != null) out = out + " " + f; }
    Object ro = @PKG@.AbilStore.RAGE.get(u);
    if (ro instanceof double[] && ragePct((double[]) ro, now) > 0.0) {
      double[] g = (double[]) ro;
      if (g[6] > 0.0) { apply(buf, att, amt * g[6] / 100.0, amt * g[6] / 100.0); out = out + " leech"; }
      if (g[7] < 0.5) {
        g[7] = 1.0;
        int ci = @PKG@.ClassStore.classIndex(u);
        if (ci >= 0 && "Berserker".equals(@PKG@.ClassDefs.NAMES[ci])) used(u, @PKG@.ClassCfg.pkey(u), @PKG@.AbilDefs.ENRAGE, null);
      }
    }
    return out.trim().length() == 0 ? null : out.trim();
  } catch (Throwable x) { return null; }
}''')

# ---------------------------------------------------------------- ARCHER: the arrow line (the enemies near a ray, nearest first)
late24(r'''
public static java.util.ArrayList rayHits(@CAC@ acc, @REF@ cr, double ex, double ey, double ez, double dx, double dy, double dz, double range, double width, java.util.HashSet skip) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.ArrayList ds = new java.util.ArrayList();
  java.util.List l = near(acc, ex + dx * range * 0.5, ey + dy * range * 0.5, ez + dz * range * 0.5, range * 0.5 + width + 1.5);
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || (skip != null && skip.contains(t)) || !enemy(acc, t, cr)) continue;
    @VEC@ q = pos(acc, t);
    if (q == null) continue;
    double vx = q.x - ex;
    double vy = q.y + 0.9 - ey;
    double vz = q.z - ez;
    double along = vx * dx + vy * dy + vz * dz;
    if (along < 0.0 || along > range) continue;
    double px = vx - dx * along;
    double py = vy - dy * along;
    double pz = vz - dz * along;
    if (px * px + py * py + pz * pz > (width + 0.6) * (width + 0.6)) continue;
    int k = 0;
    while (k < ds.size() && ((Double) ds.get(k)).doubleValue() < along) k++;
    ds.add(k, Double.valueOf(along));
    out.add(k, t);
  }
  return out;
}''')
late24(r'''
public static double[] yaw(double dx, double dy, double dz, double deg) {
  double a = Math.toRadians(deg);
  double c = Math.cos(a);
  double s = Math.sin(a);
  return new double[] { dx * c - dz * s, dy, dx * s + dz * c };
}''')
late24(r'''
public static boolean archerNode(java.util.UUID u, String id) {
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0 || !"Archer".equals(@PKG@.ClassDefs.NAMES[ci])) return false;
  return @PKG@.AbilModDefs.csvHas(treeCsv(u), id);
}''')

# ---------------------------------------------------------------- PINNING SHOT (job kind 24; the look is read at the cast)
late24(r'''
public static String pinCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double[] lk = look(st, ref);
  double[] me = here(st, ref);
  if (me == null) return " nopos";
  @PKG@.AbilJob j = new @PKG@.AbilJob(24, now, u, "PinningShot", 0.0, 0.0, 0.0, 0.0, h * (sh == 2 ? @PKG@.AbilNum.PN_RAINPOWER : @PKG@.AbilNum.PN_POWER) * cxm());
  j.pkey = k;
  j.ai = @PKG@.AbilDefs.PIN;
  j.sh = sh;
  if (sh == 2 || lk == null) { j.x = me[0]; j.y = me[1]; j.z = me[2]; j.dx = 0.0; j.dy = -1.0; j.dz = 0.0; }
  else { j.x = lk[0]; j.y = lk[1]; j.z = lk[2]; j.dx = lk[3]; j.dy = lk[4]; j.dz = lk[5]; }
  boolean far = nd(c, "Archer", "PB1");
  j.len = sh == 1 ? @PKG@.AbilNum.PN_SPRINTRANGE : (sh == 3 ? @PKG@.AbilNum.PN_STEADYRANGE : (far ? @PKG@.AbilNum.PN_FARRANGE : @PKG@.AbilNum.PN_RANGE));
  if (sh == 3) effect(st, ref, "Root", @PKG@.AbilNum.PN_STEADYSTILL);
  aw.add(j);
  return " range=" + @PKG@.AbilMath.fmt(j.len) + " hit=" + @PKG@.AbilMath.fmt(j.amount);
}''')
late24(r'''
public static int pinRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_ARC = "pin gone"; return -1; }
  @PKG@.AbilCtx c = j.cx;
  boolean lasting = nd(c, "Archer", "PA1");
  boolean grand = nd(c, "Archer", "PA5");
  boolean focus = nd(c, "Archer", "PB2");
  boolean far = nd(c, "Archer", "PB1");
  double durm = c == null ? 1.0 : c.durMult;
  double root = (j.sh == 1 ? @PKG@.AbilNum.PN_SPRINTROOT : @PKG@.AbilNum.PN_ROOT) * durm + (lasting ? 1.0 : 0.0);
  if (c != null && c.lvl > 1) { double add = 0.02 * (double) (c.lvl - 1); root = root + (add > 0.4 ? 0.4 : add); }
  double mark0 = j.sh == 3 ? @PKG@.AbilNum.PN_STEADYMARK : @PKG@.AbilNum.PN_MARK;
  double mark = mark0 + (double) (c == null ? 0 : c.lvl - 1);
  double cap = @PKG@.AbilNum.PN_MARKCAP + (j.sh == 3 ? mark0 - @PKG@.AbilNum.PN_MARK : 0.0);
  if (mark > cap) mark = cap;
  mark = mark + 3.0 * (double) (c == null ? 0 : c.eff(@PKG@.AbilModDefs.POWER)) - (lasting ? 5.0 : 0.0);
  double mt = @PKG@.AbilNum.PN_MARKTIME * durm;
  int pierce = focus ? 1 : (int) @PKG@.AbilNum.PN_PIERCE + (c == null ? 0 : c.eff(@PKG@.AbilModDefs.PIERCE)) + (j.sh == 3 ? 1 : 0);
  java.util.ArrayList ts = new java.util.ArrayList();
  java.util.ArrayList fs = new java.util.ArrayList();
  double ex = j.x;
  double ey = j.y;
  double ez = j.z;
  if (j.sh == 2) {   // Rain Pin: 3 arrows into the patch below you - the 3 nearest enemies in it
    java.util.List l = near(cb, j.x, j.y - 1.0, j.z, @PKG@.AbilNum.PN_RAINRADIUS + cxr());
    java.util.ArrayList ds = new java.util.ArrayList();
    double rr = @PKG@.AbilNum.PN_RAINRADIUS + cxr();
    for (int i = 0; i < l.size(); i++) {
      Object o = l.get(i);
      if (!(o instanceof @REF@) || ts.contains(o) || !enemy(cb, (@REF@) o, cr)) continue;
      @VEC@ q = pos(cb, (@REF@) o);
      if (q == null) continue;
      double dd = (q.x - j.x) * (q.x - j.x) + (q.z - j.z) * (q.z - j.z);
      if (dd > rr * rr || Math.abs(q.y - j.y) > 4.0) continue;
      int k = 0;
      while (k < ds.size() && ((Double) ds.get(k)).doubleValue() < dd) k++;
      ds.add(k, Double.valueOf(dd));
      ts.add(k, o);
    }
    while (ts.size() > 3) ts.remove(ts.size() - 1);
    for (int i = 0; i < ts.size(); i++) fs.add(Double.valueOf(1.0));
  } else {
    int sp = c == null ? 0 : c.lv(@PKG@.AbilModDefs.SPLIT);
    java.util.HashSet sk = new java.util.HashSet();
    for (int a = 0; a < (sp > 0 ? 3 : 1); a++) {
      double[] d = a == 0 ? new double[] { j.dx, j.dy, j.dz } : yaw(j.dx, j.dy, j.dz, a == 1 ? 12.0 : -12.0);
      java.util.ArrayList hs = rayHits(cb, cr, ex, ey, ez, d[0], d[1], d[2], j.len, @PKG@.AbilNum.PN_WIDTH, sk);
      int take = a == 0 ? pierce : 1;
      for (int i = 0; i < hs.size() && i < take; i++) { sk.add(hs.get(i)); ts.add(hs.get(i)); fs.add(Double.valueOf(a == 0 ? 1.0 : (50.0 + 5.0 * (double) (sp - 1)) / 100.0)); }
    }
  }
  int n = 0;
  @VEC@ last = null;
  for (int i = 0; i < ts.size(); i++) {
    @REF@ t = (@REF@) ts.get(i);
    double dmg = j.amount * ((Double) fs.get(i)).doubleValue();
    @VEC@ q = pos(cb, t);
    if (far && q != null) {
      double dd = Math.sqrt((q.x - ex) * (q.x - ex) + (q.y - ey) * (q.y - ey) + (q.z - ez) * (q.z - ez));
      if (dd > 20.0) dmg = dmg * 1.1; else if (dd < 8.0) dmg = dmg * 0.9;
    }
    if (hit(cb, t, cr, j.caster, dmg, "PinningShot")) n++;
    rootMob(cb, t, j.caster, root, now, lasting, grand);
    markMob(cb, t, mark, mt, focus, now);
    if (q != null) { particle(FX_ARROW, q.x, q.y + 1.0, q.z, cb); last = q; }
  }
  if (j.sh != 2) for (int s2 = 1; s2 <= 5; s2++) particle(FX_BOLT, ex + j.dx * j.len * (double) s2 / 6.0, ey + j.dy * j.len * (double) s2 / 6.0, ez + j.dz * j.len * (double) s2 / 6.0, cb);
  if (nd(c, "Archer", "PA2")) {   // Trap Arrows: a root trap where the arrow stopped (2 s root, lasts 8 s)
    double tx = last != null ? last.x : ex + j.dx * j.len;
    double ty = last != null ? last.y : ey + j.dy * j.len;
    double tz = last != null ? last.z : ez + j.dz * j.len;
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
    if (aw != null) netZone(cb, j.caster, j.pkey, aw, new double[] { tx, ty, tz }, 2.0, @PKG@.AbilNum.PN_TRAPROOT, 4, now, @PKG@.AbilNum.PN_TRAPLIFE, 0.0);
  }
  PINS = PINS + 1L;
  if (n > 0) used(j.caster, j.pkey, @PKG@.AbilDefs.PIN, c);
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.PIN, j.sh) + ": " + n + (n == 1 ? " enemy" : " enemies") + " rooted " + @PKG@.AbilMath.fmt(root) + " s and Marked (+" + @PKG@.AbilMath.fmt(mark) + " %).");
  LAST_ARC = "pin " + n + " root=" + @PKG@.AbilMath.fmt(root) + " mark=" + @PKG@.AbilMath.fmt(mark);
  return n;
}''')

# ---------------------------------------------------------------- RAPID FIRE (job kind 20 = the channel, one arrow per step)
late24(r'''
public static String rapidCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  boolean focus = nd(c, "Archer", "PB4");
  boolean quick = nd(c, "Archer", "PC3");
  double arrows = sh == 1 ? @PKG@.AbilNum.RF_SPRINTARROWS : @PKG@.AbilNum.RF_ARROWS;
  if (quick) arrows = arrows * 1.2;
  arrows = Math.floor(arrows * (c == null ? 1.0 : c.durMult) + 0.5);
  if (arrows < 1.0) arrows = 1.0;
  double secs = sh == 2 ? @PKG@.AbilNum.RF_HOVERTIME : (sh == 3 ? @PKG@.AbilNum.RF_BRACEDTIME : @PKG@.AbilNum.RF_TIME);
  long every = focus ? ms(@PKG@.AbilNum.RF_FOCUSEVERY) : Math.round(secs * 1000.0 / arrows);
  if (every < 50L) every = 50L;
  double amt = h * @PKG@.AbilNum.RF_POWER * cxm() * (sh == 3 ? 1.0 + @PKG@.AbilNum.RF_BRACEDBONUS / 100.0 : 1.0) * (focus ? 1.0 + @PKG@.AbilNum.RF_FOCUSBONUS / 100.0 : 1.0);
  @PKG@.AbilJob j = new @PKG@.AbilJob(20, now, u, "RapidFire", 0.0, 0.0, 0.0, 0.0, amt);
  j.pkey = k;
  j.ai = @PKG@.AbilDefs.RAPID;
  j.sh = sh;
  j.left = (int) arrows;
  j.total = (int) arrows;
  j.every = every;
  j.hits = 0;
  aw.add(j);
  if (sh == 3) effect(st, ref, "Root", secs);
  return " arrows=" + (int) arrows + " every=" + every + " hit=" + @PKG@.AbilMath.fmt(amt) + (focus ? " focus" : "");
}''')
late24(r'''
public static boolean rapidTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_ARC = "rapid gone"; return false; }
  @PKG@.AbilCtx c = j.cx;
  double[] lk = look(cb, cr);
  if (lk != null) {
    double[] d = new double[] { lk[3], lk[4], lk[5] };
    double spread = (j.sh == 1 ? @PKG@.AbilNum.RF_SPREAD : 0.0) + (nd(c, "Archer", "PC1") ? 20.0 : 0.0);
    if (spread > 0.0) d = yaw(d[0], d[1], d[2], (Math.random() - 0.5) * spread);
    int sk = c == null ? 0 : c.lv(@PKG@.AbilModDefs.SEEKER);
    int rc = c == null ? 0 : c.eff(@PKG@.AbilModDefs.RICOCHET);
    if (sk > 0) rc = 0;
    double width = @PKG@.AbilNum.RF_WIDTH + (sk > 0 ? 1.0 + 0.5 * (double) (sk - 1) : 0.0);
    int pierce = 1 + (c == null ? 0 : c.eff(@PKG@.AbilModDefs.PIERCE));
    int sl = c == null ? 0 : c.eff(@PKG@.AbilModDefs.SLOW);
    java.util.ArrayList hs;
    if (nd(c, "Archer", "PB4")) {   // Piercing Aim: every arrow at the Marked enemy in front of you (no spread, no ricochet)
      hs = new java.util.ArrayList();
      java.util.ArrayList all = rayHits(cb, cr, lk[0], lk[1], lk[2], d[0], d[1], d[2], @PKG@.AbilNum.RF_RANGE, width + 2.0, null);
      for (int i = 0; i < all.size() && hs.isEmpty(); i++) { Object mo = @PKG@.AbilStore.MARKD.get(all.get(i)); if (mo instanceof double[] && ((double[]) mo)[0] > (double) now) hs.add(all.get(i)); }
      if (hs.isEmpty()) hs = rayHits(cb, cr, lk[0], lk[1], lk[2], d[0], d[1], d[2], @PKG@.AbilNum.RF_RANGE, width, null);
      rc = 0;
    } else hs = rayHits(cb, cr, lk[0], lk[1], lk[2], d[0], d[1], d[2], @PKG@.AbilNum.RF_RANGE, width, null);
    int n = 0;
    @REF@ last = null;
    java.util.HashSet done = new java.util.HashSet();
    for (int i = 0; i < hs.size() && i < pierce; i++) {
      @REF@ t = (@REF@) hs.get(i);
      done.add(t);
      if (hit(cb, t, cr, j.caster, j.amount, "RapidFire")) n++;
      if (sl > 0) effect(cb, t, EF_SLOW, 0.5 + 0.25 * (double) sl);
      @VEC@ q = pos(cb, t);
      if (q != null) particle(FX_ARROW, q.x, q.y + 1.0, q.z, cb);
      last = t;
    }
    for (int b = 0; b < rc && last != null; b++) {   // Ricochet: the arrow flies on to the nearest other enemy (half damage)
      @VEC@ q = pos(cb, last);
      if (q == null) break;
      @REF@ nx = null;
      double bd = 1.0E18;
      java.util.List l = near(cb, q.x, q.y, q.z, @PKG@.AbilNum.RF_BOUNCE);
      for (int m = 0; m < l.size(); m++) {
        Object o = l.get(m);
        if (!(o instanceof @REF@) || done.contains(o) || !enemy(cb, (@REF@) o, cr)) continue;
        @VEC@ w = pos(cb, (@REF@) o);
        if (w == null) continue;
        double dd = (w.x - q.x) * (w.x - q.x) + (w.y - q.y) * (w.y - q.y) + (w.z - q.z) * (w.z - q.z);
        if (dd > @PKG@.AbilNum.RF_BOUNCE * @PKG@.AbilNum.RF_BOUNCE) continue;
        if (dd < bd) { bd = dd; nx = (@REF@) o; }
      }
      if (nx == null) break;
      done.add(nx);
      if (hit(cb, nx, cr, j.caster, j.amount * 0.5, "RapidFire")) n++;
      last = nx;
    }
    if (n == 0) particle(FX_BOLT, lk[0] + d[0] * 6.0, lk[1] + d[1] * 6.0, lk[2] + d[2] * 6.0, cb);
    j.hits = j.hits + n;
    ARROWS = ARROWS + 1L;
    if (n > 0 && !j.counted) { j.counted = true; used(j.caster, j.pkey, @PKG@.AbilDefs.RAPID, c); }
  }
  if (j.sh == 2 && !onGround(cb, cr)) push(cb, cr, 0.0, -@PKG@.AbilNum.RF_HOVERFALL, 0.0);   // Hover Fire: a slow fall while you shoot (UNVERIFIED feel)
  j.left = j.left - 1;
  if (j.left <= 0) {
    @PR@ pr = prOf(j.caster);
    if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.RAPID, j.sh) + ": " + j.hits + (j.hits == 1 ? " hit" : " hits") + " from " + j.total + " arrows.");
    LAST_ARC = "rapid " + j.hits + "/" + j.total;
    return false;
  }
  j.at = now + j.every;
  return true;
}''')
# Arrow Tempest (Archer PC5): casting Rapid Fire cuts Explosive Arrow's cooldown by 30 % of its length, and the other way round
late24(r'''
public static long tempest(String k, int other, long now) {
  String id = @PKG@.AbilDefs.IDS[other];
  long left = @PKG@.AbilStore.left(k, id, now);
  if (left <= 0L) return 0L;
  long full = @PKG@.AbilStore.total(k, id);
  if (full <= 0L) full = @PKG@.AbilDefs.cdMs(other, 0);
  long cut = Math.round((double) full * 0.3);
  long nl = left - cut;
  @PKG@.AbilStore.arm(k, id, now, nl > 0L ? nl : 0L);
  return cut;
}''')

# ---------------------------------------------------------------- EXPLOSIVE ARROW (armed; the next arrow hit -> the blast; Set Charge = job kind 21)
late24(r'''
public static String exploArm(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, int sh, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double main = c == null ? 1.0 : c.main;
  double m0 = sh == 1 ? @PKG@.AbilNum.EA_QUICKMULT : (sh == 3 ? @PKG@.AbilNum.EA_SETMULT : @PKG@.AbilNum.EA_MULT);
  double mult = 1.0 + (m0 - 1.0) * main;
  boolean storm = nd(c, "Archer", "PC4");
  double r = (sh == 1 ? @PKG@.AbilNum.EA_QUICKRADIUS : (sh == 2 ? @PKG@.AbilNum.EA_MORTARRADIUS : @PKG@.AbilNum.EA_RADIUS)) + cxr() + (storm ? 1.5 : 0.0);
  double up = sh == 2 ? @PKG@.AbilNum.EA_MORTARUP : (storm ? 2.0 : 0.0);
  double delay = sh == 3 ? @PKG@.AbilNum.EA_SETDELAY * 1000.0 : 0.0;
  @PKG@.AbilStore.EXPL.put(u, new double[] { (double) (now + ms(@PKG@.AbilNum.EA_WINDOW)), mult, r, delay, up, (double) sh });
  if (c != null) @PKG@.AbilStore.EXPLC.put(u, c);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.EXPLO, sh) + ": your next arrow hit within " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.EA_WINDOW) + " s " + (sh == 3 ? "sticks and blasts 1 s later" : "explodes") + " - " + @PKG@.AbilMath.fmt(mult) + "x, " + @PKG@.AbilMath.fmt(r) + " blocks.");
  LAST_ARC = "explo armed x" + @PKG@.AbilMath.fmt(mult) + " r=" + @PKG@.AbilMath.fmt(r);
  return " mult=" + @PKG@.AbilMath.fmt(mult) + " r=" + @PKG@.AbilMath.fmt(r) + (delay > 0.0 ? " set" : "") + (up > 0.0 ? " up" : "");
}''')
late24(r'''
public static int blastAt(@CB@ cb, @REF@ cr, java.util.UUID u, double x, double y, double z, double r, double amt, double up, @PKG@.AbilCtx c, @REF@ skip, boolean echo) {
  java.util.List l = near(cb, x, y, z, r);
  java.util.HashSet seen = new java.util.HashSet();
  int kb = c == null ? 0 : c.eff(@PKG@.AbilModDefs.KNOCK);
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || (skip != null && t.equals(skip)) || !enemy(cb, t, cr)) continue;
    @VEC@ q = pos(cb, t);
    if (q == null || !@PKG@.AbilMath.inRange(q.x - x, q.y - y, q.z - z, r + 0.5)) continue;
    if (hit(cb, t, cr, u, amt, "ExplosiveArrow")) n++;
    if (kb > 0 || up > 0.0) {
      double dx = q.x - x;
      double dz = q.z - z;
      double d = Math.sqrt(dx * dx + dz * dz);
      double f = 2.0 * (double) kb * @PKG@.AbilCfg.PUSH_PER_BLOCK;
      double vy = up * @PKG@.AbilCfg.PUSH_PER_BLOCK;
      if (d > 0.05) push(cb, t, dx / d * f, vy > 0.0 ? vy : f * 0.25, dz / d * f);
      else push(cb, t, 0.0, vy, 0.0);
    }
  }
  particle(FX_BOOM, x, y + 0.5, z, cb);
  if (!echo && c != null) {
    int sp = c.lv(@PKG@.AbilModDefs.SPLIT);
    if (sp > 0) {   // Split: 3 bomblets around the blast
      double bp = (40.0 + 5.0 * (double) (sp - 1)) / 100.0;
      for (int b = 0; b < 3; b++) {
        double a = 2.0943951023931953 * (double) b;
        n = n + blastAt(cb, cr, u, x + Math.cos(a) * 2.0, y, z + Math.sin(a) * 2.0, 2.0, amt * bp, 0.0, null, null, true);
      }
    }
    if (nd(c, "Archer", "PC2")) {   // Chain Reaction: a burning patch 3 s + a second small blast on a Marked enemy close by
      @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(cb.getExternalData()));
      @PKG@.AbilJob bj = new @PKG@.AbilJob(23, System.currentTimeMillis() + 1000L, u, "ExplosiveArrow", x, y, z, 2.5, c.h * @PKG@.AbilNum.EA_BURNPOWER * c.main);
      bj.pkey = c.pkey;
      bj.ai = @PKG@.AbilDefs.EXPLO;
      bj.left = (int) Math.round(@PKG@.AbilNum.EA_BURNTIME);
      bj.every = 1000L;
      bj.cx = c;
      aw.add(bj);
      java.util.List l2 = near(cb, x, y, z, 10.0);
      for (int i = 0; i < l2.size(); i++) {
        Object o = l2.get(i);
        if (!(o instanceof @REF@) || (skip != null && o.equals(skip)) || !enemy(cb, (@REF@) o, cr)) continue;
        Object mo = @PKG@.AbilStore.MARKD.get(o);
        if (!(mo instanceof double[]) || ((double[]) mo)[0] <= (double) System.currentTimeMillis()) continue;
        @VEC@ q = pos(cb, (@REF@) o);
        if (q != null) n = n + blastAt(cb, cr, u, q.x, q.y, q.z, 2.0, amt * 0.5, 0.0, null, null, true);
        break;
      }
    }
  }
  BLASTS = BLASTS + 1L;
  return n;
}''')
# the arrow hit (DamageLock's outgoing hook through outHit2): consume the armed blast; returns the multiplier for the arrow's own damage
late24(r'''
public static double explode(@ST@ st, @CB@ buf, @REF@ t, @REF@ att, java.util.UUID u, double[] e, double dmg, long now) {
  @PKG@.AbilStore.EXPL.remove(u);
  Object co = @PKG@.AbilStore.EXPLC.remove(u);
  @PKG@.AbilCtx c = co instanceof @PKG@.AbilCtx ? (@PKG@.AbilCtx) co : null;
  @VEC@ q = pos(buf, t);
  if (q == null) return 1.0;
  double mult = e[1];
  boolean storm = nd(c, "Archer", "PC4");
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  if (aw == null) aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(buf.getExternalData()));
  if (e[3] > 0.0) {   // Set Charge: it sticks and blasts later (the target too)
    @PKG@.AbilJob j = new @PKG@.AbilJob(21, now + Math.round(e[3]), u, "ExplosiveArrow", q.x, q.y, q.z, e[2], dmg * mult);
    j.pkey = @PKG@.ClassCfg.pkey(u);
    j.ai = @PKG@.AbilDefs.EXPLO;
    j.tref = t;
    j.push = e[4];
    j.cx = c;
    aw.add(j);
    LAST_ARC = "explo set";
    return 1.0;
  }
  int n = blastAt(buf, att, u, q.x, q.y, q.z, e[2], dmg * mult, e[4], c, t, false) + 1;
  if (c != null && !c.echo && c.echoPct > 0.0) {   // Echo: a weaker blast on the same spot 1 s later
    @PKG@.AbilCtx ec = c.echoOf(c.echoPct);
    @PKG@.AbilJob ej = new @PKG@.AbilJob(10, now + ms(@PKG@.AbilCfg.ECHO_DELAY), u, "ExplosiveArrow", q.x, q.y, q.z, e[2], dmg * mult * c.echoPct);
    ej.pkey = @PKG@.ClassCfg.pkey(u);
    ej.ai = @PKG@.AbilDefs.EXPLO;
    ej.push = e[4];
    ej.cx = ec;
    aw.add(ej);
  }
  used(u, @PKG@.ClassCfg.pkey(u), @PKG@.AbilDefs.EXPLO, c);
  @PR@ pr = prOf(u);
  if (pr != null) say(pr, "Explosive Arrow! " + n + (n == 1 ? " enemy hit." : " enemies hit."));
  LAST_ARC = "explo " + n + " x" + @PKG@.AbilMath.fmt(mult);
  return storm ? mult * 0.85 : mult;
}''')
late24(r'''
public static int blastRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) return -1;
  double x = j.x;
  double y = j.y;
  double z = j.z;
  if (j.tref instanceof @REF@ && ((@REF@) j.tref).isValid()) { @VEC@ q = pos(cb, (@REF@) j.tref); if (q != null) { x = q.x; y = q.y; z = q.z; } }
  int n = blastAt(cb, cr, j.caster, x, y, z, j.r, j.amount, j.push, j.cx, null, false);
  @PKG@.AbilCtx c = j.cx;
  if (c != null && !c.echo && c.echoPct > 0.0) {
    @PKG@.AbilJob ej = new @PKG@.AbilJob(10, now + ms(@PKG@.AbilCfg.ECHO_DELAY), j.caster, "ExplosiveArrow", x, y, z, j.r, j.amount * c.echoPct);
    ej.pkey = j.pkey;
    ej.ai = @PKG@.AbilDefs.EXPLO;
    ej.push = j.push;
    ej.cx = c.echoOf(c.echoPct);
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
    if (aw != null) aw.add(ej);
  }
  if (n > 0) used(j.caster, j.pkey, @PKG@.AbilDefs.EXPLO, c);
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, "Set Charge: " + n + (n == 1 ? " enemy hit." : " enemies hit."));
  LAST_ARC = "explo set blast " + n;
  return n;
}''')
late24(r'''
public static boolean burnTick2(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) return false;
  java.util.List l = near(cb, j.x, j.y, j.z, j.r);
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    hit(cb, t, cr, j.caster, j.amount, "ExplosiveArrow");
  }
  particle(FX_FIRE, j.x, j.y + 0.2, j.z, cb);
  j.left = j.left - 1;
  j.at = now + 1000L;
  return j.left > 0;
}''')

# ---------------------------------------------------------------- ARROW RAIN (zone kind 19)
late24(r'''
public static @PKG@.AbilZone rainZone(@CAC@ acc, java.util.UUID u, String k, @PKG@.AbilWorld aw, double[] at, int sh, double h, long now, double mana, double stam) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  if (at == null || aw == null) return null;
  boolean snare = nd(c, "Archer", "PA4");
  double r = (sh == 2 ? @PKG@.AbilNum.AR_OVERRADIUS : (sh == 3 ? @PKG@.AbilNum.AR_VOLLEYRADIUS : @PKG@.AbilNum.AR_RADIUS)) + cxr();
  double secs = cxds(sh == 3 ? @PKG@.AbilNum.AR_VOLLEYTIME : @PKG@.AbilNum.AR_TIME);
  double delay = sh == 2 ? 0.0 : (sh == 3 ? @PKG@.AbilNum.AR_VOLLEYWIND : @PKG@.AbilNum.AR_DELAY);
  long begin = now + ms(delay);
  @PKG@.AbilZone z = new @PKG@.AbilZone(19, u, at[0], at[1], at[2], r, now, begin + ms(secs));
  z.pkey = k;
  z.ai = @PKG@.AbilDefs.RAIN;
  z.shape = sh;
  z.h = h;
  z.name = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.RAIN, sh);
  z.amount = h * @PKG@.AbilNum.AR_POWER * cxm() * (snare ? 0.85 : 1.0) * 0.5 / (secs > 0.5 ? secs : 0.5);
  z.pct = sh == 3 ? @PKG@.AbilNum.AR_VOLLEYSLOW : @PKG@.AbilNum.AR_SLOW;
  if (c != null && c.lvl > 1) { double add = 0.5 * (double) (c.lvl - 1); z.pct = z.pct + (add > 10.0 ? 10.0 : add); }
  z.d1 = snare ? 1.5 : @PKG@.AbilNum.AR_ROOTAFTER;
  z.d2 = @PKG@.AbilNum.AR_MARK * (c == null ? 1.0 : c.main);
  z.t3 = begin;
  z.nextHeal = begin;
  z.x2 = at[0];
  z.z2 = at[2];
  z.d3 = mana;
  z.d4 = stam;
  z.n3 = 0;
  z.hit = new java.util.HashSet();
  aw.addZone(z);
  ring(FX_ARROW, z, acc);
  return z;
}''')
late24(r'''
public static boolean rainTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  boolean ok = live(cb, cr, z.caster, z.pkey);
  @PKG@.AbilCtx c = z.cx;
  if (ok && z.shape == 3 && now < z.t3 && z.n2 == 0) {   // Kneeling Volley: moving in the first second gives everything back
    @VEC@ p = pos(cb, cr);
    if (p != null && !@PKG@.AbilMath.inRange(p.x - z.x2, 0.0, p.z - z.z2, @PKG@.AbilCfg.CHAN_MOVE)) {
      @ESM@ m = map(cb, cr);
      if (m != null) { if (z.d3 > 0.0) m.addStatValue(@DST@.getMana(), (float) z.d3); if (z.d4 > 0.0) m.addStatValue(@DST@.getStamina(), (float) z.d4); }
      @PKG@.AbilStore.arm(z.pkey, "ArrowRain", now, 0L);
      @PR@ pr = prOf(z.caster);
      if (pr != null) send(pr, "Kneeling Volley broke - you moved. Your Mana, Stamina and cooldown were given back.", "#ffc800");
      LAST_ARC = "volley moved";
      return false;
    }
  }
  if (!ok || z.ended || now >= z.until) {
    if (ok && z.n2 == 0 && c != null && !c.echo) {
      @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
      int lg = c.lv(@PKG@.AbilModDefs.LINGER);
      if (lg > 0 && aw != null) {   // Lingering: the ground stays a slowing zone (no damage)
        @PKG@.AbilZone lz = rainZone(cb, z.caster, z.pkey, aw, new double[] { z.x, z.y, z.z }, 0, 0.0, now, 0.0, 0.0);
        if (lz != null) { lz.n2 = 1; lz.amount = 0.0; lz.t3 = now; lz.nextHeal = now; lz.until = now + ms(2.0 + (double) lg); lz.r = z.r; }
      }
      if (c.echoPct > 0.0 && aw != null) {   // Echo: a second, weaker shower right after
        @PKG@.AbilJob ej = new @PKG@.AbilJob(10, now, z.caster, "ArrowRain", z.x, z.y, z.z, z.r, z.h);
        ej.pkey = z.pkey;
        ej.ai = @PKG@.AbilDefs.RAIN;
        ej.sh = z.shape == 1 ? 0 : z.shape;
        ej.cx = c.echoOf(c.echoPct);
        aw.add(ej);
      }
    }
    @PR@ pr = prOf(z.caster);
    if (pr != null && ok && z.n2 == 0) say(pr, (c != null && c.echo ? "Echo rain" : z.name) + ": " + z.hits + (z.hits == 1 ? " hit." : " hits."));
    LAST_ARC = "rain end " + z.hits;
    return false;
  }
  if (z.shape == 1 && ok) {   // Trailing Rain: 4 blocks behind you
    @VEC@ p = pos(cb, cr);
    double[] f = flat(cb, cr);
    if (p != null) { z.x = p.x - (f == null ? 0.0 : f[0] * @PKG@.AbilNum.AR_BEHIND); z.y = p.y; z.z = p.z - (f == null ? 0.0 : f[1] * @PKG@.AbilNum.AR_BEHIND); }
  }
  if (now < z.t3) { if (now >= z.nextFx) { z.nextFx = now + 500L; ring(FX_ARROW, z, cb); } return true; }
  if (now < z.nextHeal) return true;
  z.nextHeal = now + 500L;
  java.util.List l = near(cb, z.x, z.y, z.z, z.r);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  boolean lasting = nd(c, "Archer", "PA1");
  boolean grand = nd(c, "Archer", "PA5");
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    @VEC@ q = pos(cb, t);
    if (q == null || (q.x - z.x) * (q.x - z.x) + (q.z - z.z) * (q.z - z.z) > z.r * z.r || Math.abs(q.y - z.y) > 6.0) continue;
    if (z.amount > 0.0 && hit(cb, t, cr, z.caster, z.amount, "ArrowRain")) n++;
    effect(cb, t, z.pct >= 40.0 ? EF_SLOW : spdId(-(int) Math.round(z.pct)), 1.0);
    if (z.n2 == 1) continue;
    Object eo = z.healed.get(t);
    long[] ev;
    if (!(eo instanceof long[])) { ev = new long[] { now, 0L }; z.healed.put(t, ev); }
    else ev = (long[]) eo;
    if (ev[1] == 0L && (double) (now - ev[0]) >= z.d1 * 1000.0) {
      ev[1] = 1L;
      rootMob(cb, t, z.caster, @PKG@.AbilNum.AR_ROOT, now, lasting, grand);
      markMob(cb, t, z.d2, @PKG@.AbilNum.AR_MARKTIME, false, now);
    }
  }
  z.hits = z.hits + n;
  RAINHITS = RAINHITS + (long) n;
  if (n > 0 && !z.echoed && (c == null || !c.echo) && z.n2 == 0) { z.echoed = true; used(z.caster, z.pkey, @PKG@.AbilDefs.RAIN, c); }
  if (now >= z.nextFx) { z.nextFx = now + 1000L; ring(FX_ARROW, z, cb); }
  return true;
}''')

# ---------------------------------------------------------------- HUNTER'S NET (zone kind 20; n1: 0 a net, 1 the Snare Line strip, 3 a Set Trap, 4 a Trap Arrows trap)
late24(r'''
public static @PKG@.AbilZone netZone(@CAC@ acc, java.util.UUID u, String k, @PKG@.AbilWorld aw, double[] at, double r, double rootSecs, int mode, long now, double life, double amt) {
  if (at == null || aw == null) return null;
  @PKG@.AbilZone z = new @PKG@.AbilZone(20, u, at[0], at[1], at[2], r < 0.5 ? 0.5 : r, now, now + ms(mode == 3 || mode == 4 ? life : rootSecs));
  z.pkey = k;
  z.ai = @PKG@.AbilDefs.NET;
  z.n1 = mode;
  z.d1 = rootSecs;
  z.amount = amt;
  z.t3 = mode == 3 ? now + ms(@PKG@.AbilNum.HN_TRAPARM) : now;
  z.hit = new java.util.HashSet();
  z.name = mode == 4 ? "Trap Arrow" : "Hunter's Net";
  aw.addZone(z);
  if (mode != 3) ring(FX_NET, z, acc);
  return z;
}''')
late24(r'''
public static String netCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, double[] at, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  boolean deep = nd(c, "Archer", "PA3");
  double[] me = here(st, ref);
  if (me == null) return " nopos";
  double amt = h * @PKG@.AbilNum.HN_POWER * cxm();
  double secs = cxds(sh == 2 ? @PKG@.AbilNum.HN_DROPTIME : @PKG@.AbilNum.HN_TIME) + (deep ? 1.0 : 0.0);
  double r = (sh == 2 ? @PKG@.AbilNum.HN_DROPRADIUS : @PKG@.AbilNum.HN_RADIUS) + cxr() - (deep ? 1.0 : 0.0);
  @PKG@.AbilZone z;
  if (sh == 3) {
    z = netZone(st, u, k, aw, me, @PKG@.AbilNum.HN_TRAPRADIUS + cxr(), secs, 3, now, @PKG@.AbilNum.HN_TRAPLIFE, amt);
  } else if (sh == 1) {
    double[] f = flat(st, ref);
    z = netZone(st, u, k, aw, me, @PKG@.AbilNum.HN_STRIPWIDTH / 2.0 + cxr() * 0.5, secs, 1, now, 0.0, amt);
    if (z != null) { z.x2 = me[0] - (f == null ? 0.0 : f[0] * @PKG@.AbilNum.HN_STRIPLENGTH); z.z2 = me[2] - (f == null ? 0.0 : f[1] * @PKG@.AbilNum.HN_STRIPLENGTH); }
  } else z = netZone(st, u, k, aw, sh == 2 ? me : at, r, secs, 0, now, 0.0, amt);
  if (z == null) return " nopos";
  z.shape = sh;
  z.name = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.NET, sh);
  int sp = c == null ? 0 : c.lv(@PKG@.AbilModDefs.SPLIT);
  int extra = 0;
  if (sp > 0 && (sh == 0 || sh == 2)) {   // Split: 3 smaller nets
    double[] f = flat(st, ref);
    double sx = f == null ? 1.0 : -f[1];
    double sz = f == null ? 0.0 : f[0];
    for (int a = -1; a <= 1; a = a + 2) {
      @PKG@.AbilZone s2 = netZone(st, u, k, aw, new double[] { z.x + sx * 3.0 * (double) a, z.y, z.z + sz * 3.0 * (double) a }, z.r * 0.6, secs, 0, now, 0.0, amt * (0.5 + 0.1 * (double) (sp - 1)));
      if (s2 != null) { s2.shape = sh; s2.name = z.name; extra++; }
    }
  }
  if (pr != null) say(pr, z.name + (sh == 3 ? ": a hidden trap at your feet (arms in " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.HN_TRAPARM) + " s, " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.HN_TRAPLIFE) + " s)." : ": everything inside is rooted " + @PKG@.AbilMath.fmt(secs) + " s and Marked."));
  LAST_ARC = "net " + z.name + " r=" + @PKG@.AbilMath.fmt(z.r) + (extra > 0 ? " +" + extra : "");
  return " r=" + @PKG@.AbilMath.fmt(z.r) + " secs=" + @PKG@.AbilMath.fmt(secs) + (extra > 0 ? " split=" + extra : "") + (deep ? " deep" : "");
}''')
late24(r'''
public static boolean netIn(@PKG@.AbilZone z, double qx, double qz) {
  if (z.n1 != 1) return (qx - z.x) * (qx - z.x) + (qz - z.z) * (qz - z.z) <= z.r * z.r;
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
late24(r'''
public static boolean netTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  if (!live(cb, cr, z.caster, z.pkey) || z.ended || now >= z.until) {
    @PR@ pr = prOf(z.caster);
    if (pr != null && z.hits > 0) say(pr, z.name + ": " + z.hits + (z.hits == 1 ? " enemy caught." : " enemies caught."));
    LAST_ARC = "net end " + z.hits;
    return false;
  }
  @PKG@.AbilCtx c = z.cx;
  java.util.List l = near(cb, z.x, z.y, z.z, (z.n1 == 1 ? @PKG@.AbilNum.HN_STRIPLENGTH + z.r : z.r) + 1.0);
  if (z.n1 == 3 || z.n1 == 4) {   // a trap: armed after 1 s (Set Trap), springs into a net when an enemy steps in
    if (now < z.t3) return true;
    for (int i = 0; i < l.size(); i++) {
      Object o = l.get(i);
      if (!(o instanceof @REF@) || !enemy(cb, (@REF@) o, cr)) continue;
      @VEC@ q = pos(cb, (@REF@) o);
      if (q == null || !netIn(z, q.x, q.z)) continue;
      z.n1 = z.n1 == 4 ? 5 : 0;
      z.until = now + ms(z.d1);
      if (z.n1 == 0) z.r = @PKG@.AbilNum.HN_RADIUS + (c == null ? 0.0 : c.radAdd + c.radTree);
      ring(FX_NET, z, cb);
      @PR@ pr = prOf(z.caster);
      if (pr != null) say(pr, z.name + " sprang!");
      break;
    }
    if (z.n1 == 3 || z.n1 == 4) return true;
  }
  boolean lasting = nd(c, "Archer", "PA1");
  boolean grand = nd(c, "Archer", "PA5");
  boolean deep = nd(c, "Archer", "PA3");
  int pl = c == null ? 0 : c.eff(@PKG@.AbilModDefs.PULL);
  boolean drag = deep || pl > 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!enemy(cb, t, cr)) continue;
    @VEC@ q = pos(cb, t);
    if (q == null || !netIn(z, q.x, q.z)) continue;
    if (!z.hit.contains(t)) {
      z.hit.add(t);
      z.hits = z.hits + 1;
      NETTED = NETTED + 1L;
      if (z.amount > 0.0) hit(cb, t, cr, z.caster, z.amount, "HuntersNet");
      if (z.n1 != 5) markMob(cb, t, @PKG@.AbilNum.HN_MARK * (c == null ? 1.0 : c.main), @PKG@.AbilNum.HN_MARKTIME, false, now);
      if (!drag) rootMob(cb, t, z.caster, (double) (z.until - now) / 1000.0, now, lasting, grand);
      else z.healed.put(t, Long.valueOf(0L));   // dragged first, rooted after 2 s
      if (!z.echoed && z.n1 != 5) { z.echoed = true; used(z.caster, z.pkey, @PKG@.AbilDefs.NET, c); }
    }
    if (drag && now - z.start >= 2000L && z.healed.get(t) instanceof Long && ((Long) z.healed.get(t)).longValue() == 0L) {
      z.healed.put(t, Long.valueOf(1L));
      rootMob(cb, t, z.caster, (double) (z.until - now) / 1000.0, now, lasting, grand);
    }
    if (drag && now - z.start < 2000L) {   // Pull / Deep Net: dragged to the centre
      double dx = z.x - q.x;
      double dz = z.z - q.z;
      double d = Math.sqrt(dx * dx + dz * dz);
      double f = (pl > 0 ? (double) pl : 1.0) * @PKG@.AbilNum.HN_PULL * 0.25;
      if (d > 0.8) push(cb, t, dx / d * f, 0.1, dz / d * f);
    }
  }
  if (now >= z.nextFx) { z.nextFx = now + 1000L; ring(FX_NET, z, cb); }
  return true;
}''')

# ---------------------------------------------------------------- the class tree, Warrior + Berserker + Archer (Class-Tree-Paths.md 1 / 2 / 5)
late24(r'''
public static void treeApply3(@PKG@.AbilCtx c) {
  if (c == null || c.ai < 0) return;
  int ai = c.ai;
  boolean war = "Warrior".equals(c.cls);
  boolean ber = "Berserker".equals(c.cls);
  boolean arc = "Archer".equals(c.cls);
  if (!war && !ber && !arc) return;
  double q = c.amt("T6", 5.0);
  if ((war || ber) && q > 0.0) c.cdMult = c.cdMult * (1.0 - (q > 90.0 ? 90.0 : q) / 100.0);
  if (war) {
    if (ai == @PKG@.AbilDefs.SHOCK && c.node("PC4")) c.treeMain = c.treeMain * 0.8;
    if (ai == @PKG@.AbilDefs.RALLY && c.node("PB2")) c.cdAdd = c.cdAdd + 3000L;
    if (c.node("PB4") && c.u != null && !@PKG@.AbilStore.RETRI.containsKey(c.u)) @PKG@.AbilStore.RETRI.put(c.u, new double[18]);
  }
  if (ber) {
    if (ai == @PKG@.AbilDefs.ENRAGE && c.node("PA4")) c.costAdd = c.costAdd + 6.0;
    if (ai == @PKG@.AbilDefs.ENRAGE && c.node("PA2")) c.cdAdd = c.cdAdd + 0L;   // Shared Fury waits (Skyy's call) - no cost added
    if (ai == @PKG@.AbilDefs.WHIRL && c.node("PB2")) c.treeMain = c.treeMain * 0.9;
    if (ai == @PKG@.AbilDefs.ESPLIT && c.node("PC4")) c.cdAdd = c.cdAdd + 3000L;
  }
  if (arc) {
    if (c.node("PA5")) c.cdMult = c.cdMult * 1.1;
    if (ai == @PKG@.AbilDefs.PIN && c.node("PA2")) c.costAdd = c.costAdd + 2.0;
    if (ai == @PKG@.AbilDefs.EXPLO && c.node("PC2")) c.cdAdd = c.cdAdd + 2000L;
    if ((ai == @PKG@.AbilDefs.RAPID || ai == @PKG@.AbilDefs.EXPLO) && c.node("PC5")) c.costMult = c.costMult * 1.2;
    if (ai == @PKG@.AbilDefs.RAPID && c.node("PC1")) c.treeMain = c.treeMain * 0.9;
    if (ai == @PKG@.AbilDefs.RAPID && c.node("PC3")) c.treeMain = c.treeMain * 0.92;
    if (ai == @PKG@.AbilDefs.RAIN && c.node("PA4")) c.treeMain = c.treeMain * 1.0;   // Marksman's Snare: the -15 % sits in rainZone
    if (ai == @PKG@.AbilDefs.NET && c.node("PA3")) c.radTree = c.radTree + 0.0;      // Deep Net: the -1 radius sits in netCast
  }
}''')
# the panel texts of the modifiers on the 15 (null = the shared text)
late24(r'''
public static String modText2(int ai, int mi, int lvl, int e, int l1) {
  if (mi == @PKG@.AbilModDefs.ECHO) {
    double ep = @PKG@.AbilCfg.ECHO_BASE + @PKG@.AbilCfg.ECHO_STEP * (double) l1;
    if (ai == @PKG@.AbilDefs.RALLY) return "the cut lingers " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.RG_ECHOTIME) + " s at " + @PKG@.AbilMath.fmt(ep) + " %";
    if (ai == @PKG@.AbilDefs.BANNER) return "the buff lingers " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.WB_ECHOTIME) + " s at " + @PKG@.AbilMath.fmt(ep) + " %";
    if (ai == @PKG@.AbilDefs.RAIN) return "a second shower right after at " + @PKG@.AbilMath.fmt(ep) + " %";
    if (ai == @PKG@.AbilDefs.WHIRL) return "a second spin 1 s after at " + @PKG@.AbilMath.fmt(ep) + " %";
    return null;
  }
  if (mi == @PKG@.AbilModDefs.SPLIT) {
    if (ai == @PKG@.AbilDefs.ESPLIT) return "3 lines in a fan, the side ones " + @PKG@.AbilMath.fmt(50.0 + 10.0 * (double) l1) + " %";
    if (ai == @PKG@.AbilDefs.PIN) return "3 arrows, the side ones " + @PKG@.AbilMath.fmt(50.0 + 5.0 * (double) l1) + " %";
    if (ai == @PKG@.AbilDefs.EXPLO) return "3 bomblets at " + @PKG@.AbilMath.fmt(40.0 + 5.0 * (double) l1) + " %";
    if (ai == @PKG@.AbilDefs.NET) return "3 nets, the side ones smaller (" + @PKG@.AbilMath.fmt(50.0 + 10.0 * (double) l1) + " %)";
  }
  if (mi == @PKG@.AbilModDefs.CHAIN) {
    if (ai == @PKG@.AbilDefs.IRONC) return "also hooks " + e + " more within " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.IC_CHAINRANGE) + " blocks";
    if (ai == @PKG@.AbilDefs.CHALL) return "also challenges " + e + " more within " + @PKG@.AbilMath.fmt(@PKG@.AbilNum.CH_CHAINRANGE) + " blocks";
  }
  if (mi == @PKG@.AbilModDefs.SLOW) {
    if (ai == @PKG@.AbilDefs.IRONC || ai == @PKG@.AbilDefs.ESPLIT) return "slowed for " + (1 + e) + " s";
    if (ai == @PKG@.AbilDefs.RAPID) return "each hit slows " + @PKG@.AbilMath.fmt(0.5 + 0.25 * (double) e) + " s";
  }
  if (mi == @PKG@.AbilModDefs.PULL) {
    if (ai == @PKG@.AbilDefs.IRONC) return "drags " + (25 * e) + " % faster - and drags bosses too";
    if (ai == @PKG@.AbilDefs.WHIRL) return "draws enemies into the spin (" + @PKG@.AbilMath.fmt(0.5 * (double) e) + " blocks a tick)";
    if (ai == @PKG@.AbilDefs.NET) return "drags enemies to its centre for 2 s, then roots";
  }
  if (mi == @PKG@.AbilModDefs.LEECH) {
    if (ai == @PKG@.AbilDefs.ENRAGE) return "you heal " + (3 * e) + " % of your hits while enraged";
    if (ai == @PKG@.AbilDefs.WHIRL) return "+" + (5 * e) + " % healing from the spin";
    if (ai == @PKG@.AbilDefs.FRENZY) return "you heal " + (2 * e) + " % of each hit";
  }
  if (mi == @PKG@.AbilModDefs.FLOOR) return "never below " + (lvl <= 1 ? 5 : 10) + " stacks once reached (not with Duration+)";
  if (mi == @PKG@.AbilModDefs.SEEKER) return "arrows passing within " + @PKG@.AbilMath.fmt(1.0 + 0.5 * (double) l1) + " blocks swerve in (not with Ricochet)";
  if (mi == @PKG@.AbilModDefs.RICOCHET && ai == @PKG@.AbilDefs.RAPID) return "bounces to " + e + " more (half damage, not with Seeker)";
  if (mi == @PKG@.AbilModDefs.WARD) {
    if (ai == @PKG@.AbilDefs.CHALL) return "a shield of " + (3 * lvl) + " % max Health while it lasts";
    if (ai == @PKG@.AbilDefs.OATH) return "the ally gets a shield of " + (3 * lvl) + " % of your max Health";
    if (ai == @PKG@.AbilDefs.BANNER) return "everyone near it: a shield of " + (3 * lvl) + " % max Health every 10 s";
  }
  if (mi == @PKG@.AbilModDefs.HASTE && ai == @PKG@.AbilDefs.FRENZY) return "+" + (long) @PKG@.AbilNum.BF_HASTESPEED + " % move speed above " + (long) @PKG@.AbilNum.BF_HASTEAT + " stacks (the attack-speed stand-in)";
  if (mi == @PKG@.AbilModDefs.LINGER && ai == @PKG@.AbilDefs.RAIN) return "the ground keeps slowing " + (2 + lvl) + " s";
  if (mi == @PKG@.AbilModDefs.DURATION && ai == @PKG@.AbilDefs.FRENZY) return "stacks last " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.MOD_DUR * (double) e) + " % longer (not with Floor)";
  if (mi == @PKG@.AbilModDefs.DURATION && ai == @PKG@.AbilDefs.RAPID) return "+" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.MOD_DUR * (double) e) + " % arrows";
  return null;
}''')
# the echoes of the 15 (echoRun's tail): Shockwave, Whirlwind, Arrow Rain, Explosive Arrow
late24(r'''
public static String echoRun2(@PKG@.AbilJob j, @ST@ st, @CB@ cb, @REF@ cr, long now) {
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  if (j.ai == @PKG@.AbilDefs.SHOCK) {
    @PKG@.AbilJob s = new @PKG@.AbilJob(17, now, j.caster, "ShieldShockwave", j.x, j.y, j.z, j.r, j.amount);
    s.pkey = j.pkey;
    s.ai = j.ai;
    s.sh = j.sh;
    s.dx = j.dx;
    s.dz = j.dz;
    s.width = j.width;
    s.stun = j.stun;
    s.cx = j.cx;
    return "shock:" + shockRun(s, st, cb, now);
  }
  if (j.ai == @PKG@.AbilDefs.WHIRL) return aw == null ? "noworld" : "spin:" + spinAt(prOf(j.caster), cb, cr, j.caster, j.pkey, aw, j.sh, j.amount, now);
  if (j.ai == @PKG@.AbilDefs.RAIN) {
    @PKG@.AbilZone z = rainZone(cb, j.caster, j.pkey, aw, new double[] { j.x, j.y, j.z }, j.sh, j.amount, now, 0.0, 0.0);
    if (z != null) { z.t3 = now; z.nextHeal = now; }
    @PR@ pr = prOf(j.caster);
    if (pr != null && z != null) say(pr, "Echo: a second, weaker Arrow Rain.");
    return z == null ? "rain:none" : "rain:" + @PKG@.AbilMath.fmt(z.r);
  }
  if (j.ai == @PKG@.AbilDefs.EXPLO) return "blast:" + blastAt(cb, cr, j.caster, j.x, j.y, j.z, j.r, j.amount, j.push, j.cx, null, true);
  return null;
}''')
late24(r'''
public static boolean runJob4(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  if (j.kind == 17) { shockRun(j, st, cb, now); return false; }
  if (j.kind == 18) { chainRun(j, st, cb, now); return false; }
  if (j.kind == 19) { splitRun(j, st, cb, now); return false; }
  if (j.kind == 20) return rapidTick(j, st, cb, now);
  if (j.kind == 21) { blastRun(j, st, cb, now); return false; }
  if (j.kind == 22) return bleedTick(j, st, cb, now);
  if (j.kind == 23) return burnTick2(j, st, cb, now);
  if (j.kind == 24) { pinRun(j, st, cb, now); return false; }
  return false;
}''')
late24(r'''
public static boolean zoneTick4(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind == 13) return rallyTick(z, st, cb, now);
  if (z.kind == 14) return challTick(z, st, cb, now);
  if (z.kind == 15) return rageTick(z, st, cb, now);
  if (z.kind == 16) return spinTick(z, st, cb, now);
  if (z.kind == 17) return frenzyTick(z, st, cb, now);
  if (z.kind == 18) return bannerTick(z, st, cb, now);
  if (z.kind == 19) return rainTick(z, st, cb, now);
  if (z.kind == 20) return netTick(z, st, cb, now);
  return false;
}''')
# the mob / player maps of the 15 pruned once a second (AbilTick -> pruneMobs)
late24(r'''
public static void pruneD(java.util.concurrent.ConcurrentHashMap m, long now, int i, int j) {
  if (m.isEmpty()) return;
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    Object v = m.get(k);
    boolean dead = false;
    try { dead = (k instanceof @REF@) && !((@REF@) k).isValid(); } catch (Throwable t) { dead = false; }
    if (dead || !(v instanceof double[]) || ((double[]) v).length <= (i > j ? i : j) || (((double[]) v)[i] <= (double) now && ((double[]) v)[j] <= (double) now)) it.remove();
  }
}''')
late24(r'''
public static void pruneMobs2(long now) {
  if (!@PKG@.AbilStore.TAUNTS.isEmpty()) pruneIdx(@PKG@.AbilStore.TAUNTS, now, 0);
  if (!@PKG@.AbilStore.CHALLS.isEmpty()) pruneIdx(@PKG@.AbilStore.CHALLS, now, 0);
  if (!@PKG@.AbilStore.ROOTS.isEmpty()) pruneIdx(@PKG@.AbilStore.ROOTS, now, 0);
  if (!@PKG@.AbilStore.CHAINED.isEmpty()) pruneIdx(@PKG@.AbilStore.CHAINED, now, 0);
  if (!@PKG@.AbilStore.DEADEYE.isEmpty()) pruneIdx(@PKG@.AbilStore.DEADEYE, now, 0);
  if (!@PKG@.AbilStore.BLEEDS.isEmpty()) pruneIdx(@PKG@.AbilStore.BLEEDS, now, 0);
  pruneD(@PKG@.AbilStore.MARKD, now, 0, 0);
  pruneD(@PKG@.AbilStore.GUARDED, now, 0, 2);
  pruneD(@PKG@.AbilStore.OATHS, now, 0, 0);
  pruneD(@PKG@.AbilStore.OATHW, now, 0, 0);
  pruneD(@PKG@.AbilStore.FURY, now, 1, 1);
  pruneD(@PKG@.AbilStore.WAR, now, 2, 2);
  pruneD(@PKG@.AbilStore.EXPL, now, 0, 0);
  if (!@PKG@.AbilStore.EXPLC.isEmpty()) {
    java.util.Iterator it = @PKG@.AbilStore.EXPLC.keySet().iterator();
    while (it.hasNext()) if (!@PKG@.AbilStore.EXPL.containsKey(it.next())) it.remove();
  }
  if (!@PKG@.AbilStore.RAGE.isEmpty()) {
    java.util.Iterator it = @PKG@.AbilStore.RAGE.keySet().iterator();
    while (it.hasNext()) {
      Object v = @PKG@.AbilStore.RAGE.get(it.next());
      if (!(v instanceof double[]) || ((double[]) v).length < 7 || ((double[]) v)[2] + ((double[]) v)[5] <= (double) now) it.remove();
    }
  }
}''')
# Deadeye (Archer PB3) + Explosive Arrow on a weapon hit (DamageLock's outgoing hook, after outHit) + the outgoing multiplier
late24(r'''
public static String outHit2(@ST@ st, @CB@ buf, @REF@ t, @DMG@ d, java.util.UUID u, long now) {
  try {
    if (u == null || t == null || d == null || d.isCancelled()) return null;
    float a0 = d.getAmount();
    if (!(a0 > 0.0f)) return null;
    if (buf.getComponent(t, @NPC@.getComponentType()) == null) return null;
    double mult = outMult(buf, t, u, now);
    String out = "";
    if (!@PKG@.AbilStore.MARKD.isEmpty() || !@PKG@.AbilStore.EXPL.isEmpty()) {
      @PR@ pr = prOf(u);
      @REF@ att = pr == null ? null : pr.getReference();
      String item = att == null ? null : hand(buf, att);
      boolean bow = item != null && (item.startsWith("Weapon_Shortbow_") || item.startsWith("Weapon_Crossbow_"));
      if (bow) {
        Object mo = @PKG@.AbilStore.MARKD.get(t);
        if (mo instanceof double[] && ((double[]) mo)[0] > (double) now && archerNode(u, "PB3")) {
          Object lo = @PKG@.AbilStore.DEADEYE.get(t);
          boolean fresh = !(lo instanceof long[]) || ((long[]) lo)[0] <= now || ((long[]) lo)[1] != u.getMostSignificantBits() || ((long[]) lo)[2] != u.getLeastSignificantBits();
          if (fresh) {
            @PKG@.AbilStore.DEADEYE.put(t, new long[] { now + 6000L, u.getMostSignificantBits(), u.getLeastSignificantBits() });
            mult = mult * (1.0 + (double) @PKG@.AbilCfg.CRIT_STAND / 100.0);
            out = out + " deadeye";
          }
        }
        Object eo = @PKG@.AbilStore.EXPL.get(u);
        if (eo instanceof double[]) {
          double[] e = (double[]) eo;
          if (e[0] <= (double) now) { @PKG@.AbilStore.EXPL.remove(u); @PKG@.AbilStore.EXPLC.remove(u); }
          // FIX ROUND 2: the RAW arrow damage into the blast - each blast hit() applies its own outMult (no double Enrage / Mark ...)
          else { mult = mult * explode(st, buf, t, att, u, e, (double) a0, now); out = out + " explode"; }
        }
      }
    }
    if (mult != 1.0) d.setAmount((float) ((double) a0 * mult));
    return out.length() == 0 ? (mult != 1.0 ? "x" + @PKG@.AbilMath.fmt(mult) : null) : out.trim() + " x" + @PKG@.AbilMath.fmt(mult);
  } catch (Throwable x) { @PKG@.ClassCfg.warnLimited("a Warrior / Berserker / Archer hit bonus failed: " + x); return null; }
}''')

# FIX ROUND (critic: a frenzy / banner left behind in a world nobody ticks - a solo island after /hub - stayed "on": swings paid for
# nothing and the next press said "off"): every PlayerReadyEvent (fires on every world switch) ends them unless the arrival world holds them
late24(r'''
public static String worldLeft(java.util.UUID u, @ST@ st) {
  if (u == null) return null;
  @PKG@.AbilWorld aw = null;
  try { aw = @PKG@.AbilWorld.at(st); } catch (Throwable x0) { aw = null; }
  long now = System.currentTimeMillis();
  String out = "";
  @PR@ pr = prOf(u);
  Object fo = @PKG@.AbilStore.FRENZ.get(u);
  if (fo instanceof @PKG@.AbilZone && !(aw != null && aw.holds((@PKG@.AbilZone) fo))) {
    @PKG@.AbilZone z = (@PKG@.AbilZone) fo;
    boolean was = !z.ended;
    z.ended = true;
    z.why = "left";
    @PKG@.AbilStore.FRENZ.remove(u);
    @PKG@.AbilStore.FURY.remove(u);
    @PKG@.AbilStore.PAID.remove(u);
    @PKG@.AbilStore.BANKED.put(z.pkey, new double[] { (double) frenzyStacks(z, now), (double) now });   // FIX ROUND 2: by pkey
    if (was && pr != null) say(pr, "Blood Frenzy off - you changed world (press it again to turn it on here).");
    out = out + " frenzy";
  }
  Object bo = @PKG@.AbilStore.BANNERS.get(u);
  if (bo instanceof @PKG@.AbilZone && !(aw != null && aw.holds((@PKG@.AbilZone) bo))) {
    @PKG@.AbilZone z = (@PKG@.AbilZone) bo;
    boolean was = !z.ended;
    z.ended = true;
    z.why = "world";
    @PKG@.AbilStore.BANNERS.remove(u);
    if (was) {
      @PKG@.AbilStore.arm(z.pkey, "WarlordsBanner", now, cdCx(z.cx, @PKG@.AbilDefs.BANNER, z.shape));   // the fall starts the cooldown
      if (pr != null) say(pr, "Your Warlord's Banner fell - you changed world.");
    }
    out = out + " banner";
  }
  if (out.length() > 0) LAST_BER = "world left" + out;
  return out.length() == 0 ? null : out.trim();
}''')

for _m in L24:
    assert '"""' not in _m
rep('''public static boolean zoneTick3(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind == 8) return flowTick(z, st, cb, now);
  if (z.kind == 9) return stanceTick(z, st, cb, now);
  if (z.kind == 10) return cloudTick(z, st, cb, now);
  if (z.kind == 11) return smokeTick(z, st, cb, now);
  if (z.kind == 12) return cloakTick(z, st, cb, now);
  return false;
}
"""
]''', '''public static boolean zoneTick3(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind == 8) return flowTick(z, st, cb, now);
  if (z.kind == 9) return stanceTick(z, st, cb, now);
  if (z.kind == 10) return cloudTick(z, st, cb, now);
  if (z.kind == 11) return smokeTick(z, st, cb, now);
  if (z.kind == 12) return cloakTick(z, st, cb, now);
  if (z.kind >= 13) return zoneTick4(z, st, cb, now);   // 0.1.24: Warrior / Berserker / Archer
  return false;
}
""",
''' + ",\n".join('r"""\n%s\n"""' % _m for _m in L24) + '''
]''')

# ================================================================================================ dispatch: jobs, zones, the per-player zone kinds
rep('''  if (j.kind == 16) return poisonTick(j, st, cb, now);
  return false;''', '''  if (j.kind == 16) return poisonTick(j, st, cb, now);
  if (j.kind >= 17) return runJob4(j, st, cb, now);   // 0.1.24
  return false;''')
rep('''|| z.kind == 12) { this.zones.add(z); this.nz = this.zones.size(); return 0; }''',
    '''|| z.kind == 12 || z.kind >= 13) { this.zones.add(z); this.nz = this.zones.size(); return 0; }   /* 0.1.24: the Warrior / Berserker / Archer zones keep their own limits (one banner, one frenzy / spin each; nets + rains end in seconds; Split makes 3 nets) */''')
rep('''|| o.kind == 12) continue;''', '''|| o.kind == 12 || o.kind >= 13) continue;''')
rep('''  if (!monk && !asn) return;''', '''  if (!monk && !asn) { treeApply3(c); return; }   // 0.1.24: Warrior + Berserker + Archer''')
rep('''  int l1 = lvl - 1;
  if (mi == @PKG@.AbilModDefs.POWER)''', '''  int l1 = lvl - 1;
  if (ai >= @PKG@.AbilDefs.RALLY) { String t24 = modText2(ai, mi, lvl, e, l1); if (t24 != null) return t24; }   // 0.1.24
  if (mi == @PKG@.AbilModDefs.POWER)''')
rep('''    LAST_ECHO = "cloud";
    return false;
  }
  return false;''', '''    LAST_ECHO = "cloud";
    return false;
  }
  String e24 = echoRun2(j, st, cb, cr, now);   // 0.1.24: Shockwave, Whirlwind, Arrow Rain, Explosive Arrow
  if (e24 != null) LAST_ECHO = e24;
  return false;''')
rep('''  if (!@PKG@.AbilStore.PALMS.isEmpty()) pruneIdx(@PKG@.AbilStore.PALMS, now, 3);
}''', '''  if (!@PKG@.AbilStore.PALMS.isEmpty()) pruneIdx(@PKG@.AbilStore.PALMS, now, 3);
  pruneMobs2(now);   // 0.1.24
}''')

# ================================================================================================ castAt0: texts, pre-checks, the toggle, Retribution, cooldowns, the executors
rep(''' abilities come in a later update (the Mage, Priest, Monk and Assassin have theirs).''', ''' abilities come in a later update.''', 3)
rep('''    if (palmT == null) { refuse(pr, "No enemy in front of you within " + @PKG@.AbilMath.fmt(pr0) + " blocks - nothing was spent."); return "notarget"; }
  }''', '''    if (palmT == null) { refuse(pr, "No enemy in front of you within " + @PKG@.AbilMath.fmt(pr0) + " blocks - nothing was spent."); return "notarget"; }
  }
  // 0.1.24: the targets found before anything is paid (Iron Chain, Challenge, Guardian's Oath) + the aimed spots (Arrow Rain, Hunter's Net)
  @REF@ wT = null;
  java.util.UUID oathT = null;
  if (ai == @PKG@.AbilDefs.SHOCK && !shieldIn(st, ref)) {   // FIX ROUND 2: Shield Shockwave needs a shield (main hand or off-hand)
    refuse(pr, nm + " needs a shield in your hand or off-hand - nothing was spent.");
    LAST_WAR = "shock noshield";
    return "noshield";
  }
  if (ai == @PKG@.AbilDefs.IRONC) {
    double icr = (sh == 3 ? @PKG@.AbilNum.IC_ANCHORRANGE : @PKG@.AbilNum.IC_RANGE) - (nd(cx, "Warrior", "PB3") ? 3.0 : 0.0);
    wT = lookMob(st, ref, icr);
    if (wT == null) { refuse(pr, "No enemy in your look within " + @PKG@.AbilMath.fmt(icr) + " blocks to hook - nothing was spent."); return "notarget"; }
  }
  if (ai == @PKG@.AbilDefs.CHALL && sh != 2) {
    double chr = @PKG@.AbilNum.CH_RANGE + (sh == 1 ? @PKG@.AbilNum.CH_STEP : 0.0);
    wT = lookMob(st, ref, chr);
    if (wT == null) { refuse(pr, "No enemy in your look within " + @PKG@.AbilMath.fmt(chr) + " blocks to challenge - nothing was spent."); return "notarget"; }
  }
  if (ai == @PKG@.AbilDefs.OATH && sh != 2) {
    double gr = (sh == 1 ? @PKG@.AbilNum.GO_RUSHRANGE : @PKG@.AbilNum.GO_RANGE) + cxr();
    oathT = oathPick(st, st, ref, u, sh, gr, null);
    if (oathT == null) { refuse(pr, "No party member within " + @PKG@.AbilMath.fmt(gr) + " blocks to swear the oath to - nothing was spent."); return "noally"; }
  }
  if ((ai == @PKG@.AbilDefs.RAIN || ai == @PKG@.AbilDefs.NET) && sh == 0) {
    double ar = ai == @PKG@.AbilDefs.RAIN ? @PKG@.AbilNum.AR_RANGE : @PKG@.AbilNum.HN_RANGE;
    at = aim(st, ref, ar);
    if (at == null) { refuse(pr, "Look at the ground within " + @PKG@.AbilMath.fmt(ar) + " blocks - nothing was spent."); return "aim"; }
  }
  if (ai == @PKG@.AbilDefs.BANNER && sh == 1) at = ahead(st, ref, @PKG@.AbilNum.WB_AHEAD);''')
rep('''  String dn = @PKG@.AbilDefs.sname(ai, sh);
  long left = @PKG@.AbilStore.left(k, id, now);''', '''  String dn = @PKG@.AbilDefs.sname(ai, sh);
  if (ai == @PKG@.AbilDefs.FRENZY && @PKG@.AbilStore.FRENZ.get(u) instanceof @PKG@.AbilZone && !((@PKG@.AbilZone) @PKG@.AbilStore.FRENZ.get(u)).ended) return frenzyOff(pr, u, k, now);   // 0.1.24: any press turns it off (free)
  long left = @PKG@.AbilStore.left(k, id, now);''')
rep('''  if (mana > 0.0 && hm >= 0.0) m.subtractStatValue(mi, (float) mana);''',
    '''  if (ai == @PKG@.AbilDefs.SHOCK && retriTake(u, cx, now)) { mana = 0.0; stam = 0.0; }   // 0.1.24: Retribution - this Shockwave is free
  if (mana > 0.0 && hm >= 0.0) m.subtractStatValue(mi, (float) mana);''')
rep('''  long cd = cdCx(cx, ai, sh);
  @PKG@.AbilStore.arm(k, id, now, cd);''', '''  long cd = cdCx(cx, ai, sh);
  if (ai == @PKG@.AbilDefs.FRENZY) cd = 0L;                                   // 0.1.24: Blood Frenzy's 10 s start when it goes OFF
  if (ai == @PKG@.AbilDefs.BANNER) cd = cd + ms(@PKG@.AbilNum.WB_CAP);        // the banner's 40 s count from its fall (re-armed then)
  @PKG@.AbilStore.arm(k, id, now, cd);
  if ((ai == @PKG@.AbilDefs.RAPID || ai == @PKG@.AbilDefs.EXPLO) && nd(cx, "Archer", "PC5")) tempest(k, ai == @PKG@.AbilDefs.RAPID ? @PKG@.AbilDefs.EXPLO : @PKG@.AbilDefs.RAPID, now);   // Arrow Tempest''')
rep('''Stamina. Ready again in " + @PKG@.AbilMath.secs(cd) + " s.");''',
    '''Stamina. Ready again in " + (ai == @PKG@.AbilDefs.BANNER ? @PKG@.AbilMath.secs(cdCx(cx, ai, sh)) + " s after it falls." : (ai == @PKG@.AbilDefs.FRENZY ? @PKG@.AbilMath.secs(cdCx(cx, ai, sh)) + " s after you turn it off." : @PKG@.AbilMath.secs(cd) + " s.")));''')
rep('''    else if (ai == @PKG@.AbilDefs.VANISH) extra = vanishCast(pr, st, ref, u, k, aw, sh, now);''',
    '''    else if (ai == @PKG@.AbilDefs.VANISH) extra = vanishCast(pr, st, ref, u, k, aw, sh, now);
    // 0.1.24: WARRIOR + BERSERKER + ARCHER (the mid-air shapes of most wait for the landing; Iron Chain, Pinning Shot, Rapid Fire,
    // Explosive Arrow, Arrow Rain and Hunter's Net fire in the air)
    else if (sh == 2 && (ai == @PKG@.AbilDefs.RALLY || ai == @PKG@.AbilDefs.SHOCK || ai == @PKG@.AbilDefs.CHALL || ai == @PKG@.AbilDefs.OATH
             || ai == @PKG@.AbilDefs.ENRAGE || ai == @PKG@.AbilDefs.WHIRL || ai == @PKG@.AbilDefs.ESPLIT || ai == @PKG@.AbilDefs.FRENZY || ai == @PKG@.AbilDefs.BANNER)) {
      aw.add(landJob(u, k, ai, h, now));
      extra = " land";
    }
    else if (ai == @PKG@.AbilDefs.RALLY) extra = rallyAt(pr, st, st, ref, u, k, aw, sh, h, now);
    else if (ai == @PKG@.AbilDefs.SHOCK) extra = shockCast(pr, st, ref, u, k, aw, sh, h, now);
    else if (ai == @PKG@.AbilDefs.IRONC) extra = chainCast(pr, st, ref, u, k, aw, sh, h, wT, now);
    else if (ai == @PKG@.AbilDefs.CHALL) extra = challAt(pr, st, ref, u, k, aw, sh, wT, now);
    else if (ai == @PKG@.AbilDefs.OATH) extra = oathAt(pr, st, ref, u, k, sh, oathT, now);
    else if (ai == @PKG@.AbilDefs.ENRAGE) extra = rageAt(pr, st, st, ref, u, k, aw, sh, now);
    else if (ai == @PKG@.AbilDefs.WHIRL) extra = spinAt(pr, st, ref, u, k, aw, sh, h, now);
    else if (ai == @PKG@.AbilDefs.ESPLIT) extra = splitCast(pr, st, ref, u, k, aw, sh, h, null, now);
    else if (ai == @PKG@.AbilDefs.FRENZY) extra = frenzyAt(pr, st, ref, u, k, aw, sh, now);
    else if (ai == @PKG@.AbilDefs.BANNER) extra = bannerAt(pr, st, ref, u, k, aw, at, sh, now);
    else if (ai == @PKG@.AbilDefs.PIN) extra = pinCast(pr, st, ref, u, k, aw, sh, h, now);
    else if (ai == @PKG@.AbilDefs.RAPID) extra = rapidCast(pr, st, ref, u, k, aw, sh, h, now);
    else if (ai == @PKG@.AbilDefs.EXPLO) extra = exploArm(pr, st, ref, u, k, sh, now);
    else if (ai == @PKG@.AbilDefs.RAIN) {
      double[] rp = sh == 0 ? at : here(st, ref);
      @PKG@.AbilZone rz = rainZone(st, u, k, aw, rp, sh, h, now, mana, stam);
      if (rz == null) throw new IllegalStateException("no spot for the rain");
      if (pr != null) say(pr, rz.name + ": arrows rain on " + @PKG@.AbilMath.fmt(rz.r) + " blocks" + (sh == 3 ? " in 1 s (stay still)." : (sh == 1 ? " behind you." : ".")));
      LAST_ARC = "rain " + rz.name + " r=" + @PKG@.AbilMath.fmt(rz.r);
      extra = " r=" + @PKG@.AbilMath.fmt(rz.r) + " pulse=" + @PKG@.AbilMath.fmt(rz.amount) + " slow=" + @PKG@.AbilMath.fmt(rz.pct);
    }
    else if (ai == @PKG@.AbilDefs.NET) extra = netCast(pr, st, ref, u, k, aw, sh, h, at, now);''')
rep('''  if (ai == @PKG@.AbilDefs.VANISH) { @PKG@.AbilZone sz = smokeAt(cb, j.caster, j.pkey, aw, at, @PKG@.AbilNum.VA_AI_R + cxr(), 2, now); return sz == null ? "smoke:none" : "smoke:" + @PKG@.AbilMath.fmt(sz.r); }
  return "none";''', '''  if (ai == @PKG@.AbilDefs.VANISH) { @PKG@.AbilZone sz = smokeAt(cb, j.caster, j.pkey, aw, at, @PKG@.AbilNum.VA_AI_R + cxr(), 2, now); return sz == null ? "smoke:none" : "smoke:" + @PKG@.AbilMath.fmt(sz.r); }
  // 0.1.24: the landing shapes of the Warrior + Berserker
  if (ai == @PKG@.AbilDefs.RALLY) return "rally:" + rallyAt(pr, st, cb, cr, j.caster, j.pkey, aw, 2, j.amount, now);
  if (ai == @PKG@.AbilDefs.SHOCK) return "pound:" + shockJob(aw, j.cx, j.caster, j.pkey, at, flat(cb, cr), 2, j.amount, now);
  if (ai == @PKG@.AbilDefs.CHALL) {
    @REF@ ct = nearest(cb, cr, at[0], at[1], at[2], @PKG@.AbilNum.CH_LANDRADIUS + cxr(), null);
    if (ct == null) { if (pr != null) send(pr, "Challenge from Above: no enemy near your landing.", "#ffc800"); return "chall:none"; }
    return "chall:" + challAt(pr, cb, cr, j.caster, j.pkey, aw, 2, ct, now);
  }
  if (ai == @PKG@.AbilDefs.OATH) {
    java.util.UUID ot = oathPick(st, cb, cr, j.caster, 2, @PKG@.AbilNum.GO_RANGE + cxr(), at);
    if (ot == null) { if (pr != null) send(pr, "Oath on Landing: no party member near your landing.", "#ffc800"); return "oath:none"; }
    return "oath:" + oathAt(pr, cb, cr, j.caster, j.pkey, 2, ot, now);
  }
  if (ai == @PKG@.AbilDefs.ENRAGE) return "rage:" + rageAt(pr, st, cb, cr, j.caster, j.pkey, aw, 2, now);
  if (ai == @PKG@.AbilDefs.WHIRL) {
    int nb = burst(cb, cr, j.caster, at[0], at[1], at[2], @PKG@.AbilNum.WW_RADIUS + cxr(), j.amount * @PKG@.AbilNum.WW_DROPPOWER * cxm(), "Whirlwind");
    return "spin:" + spinAt(pr, cb, cr, j.caster, j.pkey, aw, 2, j.amount, now) + " slam=" + nb;
  }
  if (ai == @PKG@.AbilDefs.ESPLIT) return "split:" + splitCast(pr, st, cr, j.caster, j.pkey, aw, 2, j.amount, at, now);
  if (ai == @PKG@.AbilDefs.FRENZY) return "frenzy:" + frenzyAt(pr, cb, cr, j.caster, j.pkey, aw, 2, now);
  if (ai == @PKG@.AbilDefs.BANNER) return "banner:" + bannerAt(pr, cb, cr, j.caster, j.pkey, aw, at, 2, now);
  return "none";''')

# ================================================================================================ the hooks: Abil.hit (the multiplier), AbilShieldSys, DamageLock, AbilFrostSys
rep('''    @DMG@ d = new @DMG@(new @DENT@(caster), cause, (float) amount);''',
    '''    double amt0 = amount * outMult(buf, t, cu, System.currentTimeMillis());   // 0.1.24: Enrage / Frenzy / banner / Mark ... on ability hits too
    @DMG@ d = new @DMG@(new @DENT@(caster), cause, (float) amt0);''')
rep('''    if (!@PKG@.AbilStore.STANCES.isEmpty() || !@PKG@.AbilStore.AWED.isEmpty() || !@PKG@.AbilStore.FLOWS.isEmpty()) @PKG@.Abil.inHit(st, buf, r, (@DMG@) ev, now);   // 0.1.23: Still Water, Awe, Iron Skin''',
    '''    if (!@PKG@.AbilStore.STANCES.isEmpty() || !@PKG@.AbilStore.AWED.isEmpty() || !@PKG@.AbilStore.FLOWS.isEmpty()) @PKG@.Abil.inHit(st, buf, r, (@DMG@) ev, now);   // 0.1.23: Still Water, Awe, Iron Skin
    if (!@PKG@.AbilStore.GUARDED.isEmpty() || !@PKG@.AbilStore.OATHW.isEmpty() || !@PKG@.AbilStore.OATHS.isEmpty() || !@PKG@.AbilStore.WAR.isEmpty()
        || !@PKG@.AbilStore.CHALLS.isEmpty() || !@PKG@.AbilStore.TAUNTS.isEmpty() || !@PKG@.AbilStore.RETRI.isEmpty() || !@PKG@.AbilStore.CHAINED.isEmpty())
      @PKG@.Abil.inHit2(st, buf, r, (@DMG@) ev, now);   // 0.1.24: Rallying Guard, Oath, the banner, Challenge, Presence, Retribution, Barbed Chain''')
rep('''_oh[0].setBody(jv("{ if ($5 != null && (!@PKG@.AbilStore.STRIKE.isEmpty() || !@PKG@.AbilStore.ARMED.isEmpty() || !@PKG@.AbilStore.MARKS.isEmpty() "
                  "|| !@PKG@.AbilStore.POISONED.isEmpty())) @PKG@.Abil.outHit($1, $2, $3, $4, $5, System.currentTimeMillis()); }"))''',
    '''_oh[0].setBody(jv("{ if ($5 != null && (!@PKG@.AbilStore.STRIKE.isEmpty() || !@PKG@.AbilStore.ARMED.isEmpty() || !@PKG@.AbilStore.MARKS.isEmpty() "
                  "|| !@PKG@.AbilStore.POISONED.isEmpty())) @PKG@.Abil.outHit($1, $2, $3, $4, $5, System.currentTimeMillis()); "
                  # 0.1.24: Enrage / Blood Frenzy / the banner / Aegis Core / Marked / roots / Deadeye / Explosive Arrow - fast exit while none runs
                  "if ($5 != null && (!@PKG@.AbilStore.RAGE.isEmpty() || !@PKG@.AbilStore.FURY.isEmpty() || !@PKG@.AbilStore.WAR.isEmpty() || !@PKG@.AbilStore.GUARDED.isEmpty() "
                  "|| !@PKG@.AbilStore.MARKD.isEmpty() || !@PKG@.AbilStore.ROOTS.isEmpty() || !@PKG@.AbilStore.EXPL.isEmpty())) @PKG@.Abil.outHit2($1, $2, $3, $4, $5, System.currentTimeMillis()); }"))''')
rep('''    if (!@PKG@.AbilStore.FLOWS.isEmpty() || !@PKG@.AbilStore.CLOAKS.isEmpty() || !@PKG@.AbilStore.POISONED.isEmpty() || @PKG@.Abil.SLIP_ON)
      @PKG@.Abil.hitLanded(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);''',
    '''    if (!@PKG@.AbilStore.FLOWS.isEmpty() || !@PKG@.AbilStore.CLOAKS.isEmpty() || !@PKG@.AbilStore.POISONED.isEmpty() || @PKG@.Abil.SLIP_ON)
      @PKG@.Abil.hitLanded(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);
    // 0.1.24: Blood Frenzy stacks + cost, Enrage's leech + its counted use, banner kills - fast exit while none runs
    if (!@PKG@.AbilStore.FRENZ.isEmpty() || !@PKG@.AbilStore.RAGE.isEmpty() || !@PKG@.AbilStore.BANNERS.isEmpty())
      @PKG@.Abil.hitLanded2(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);''')
rep('''attacks do not break the cloak, NO Slip Away: " + t3); }''', '''attacks do not break the cloak, NO Slip Away, NO Blood Frenzy stacks, NO banner kill time: " + t3); }''')

# ================================================================================================ FIX ROUND: AbilWorld.holds, the swing hook, the world switch
rep('''M(abworld, "public synchronized int zoneCount() { return this.zones.size(); }")''',
    '''M(abworld, "public synchronized int zoneCount() { return this.zones.size(); }")
M(abworld, "public synchronized boolean holds(@PKG@.AbilZone z) { return z != null && this.zones.contains(z); }")   # 0.1.24 FIX ROUND''')
rep('''    if (chunk == null || !(ev instanceof @ICSE@) || !@PKG@.AbilCfg.PART || !@PKG@.AbilCfg.RUNE_KEYS) return;
    @ICSE@ e = (@ICSE@) ev;
    String ty = String.valueOf(e.getType());''',
    '''    if (chunk == null || !(ev instanceof @ICSE@) || !@PKG@.AbilCfg.PART) return;
    @ICSE@ e = (@ICSE@) ev;
    String ty = String.valueOf(e.getType());
    if ("Primary".equals(ty)) { if (!@PKG@.AbilStore.FRENZ.isEmpty()) @PKG@.Abil.onSwing(e, chunk.getReferenceTo(idx), buf, System.currentTimeMillis()); return; }   // 0.1.24 FIX ROUND: Blood Frenzy pays per swing, hit or miss
    if (!@PKG@.AbilCfg.RUNE_KEYS) return;''')
rep('''    @PKG@.Abil.mirrorSoon(u);   // 0.1.22: the ability rune slots are looked at on the next tick
    if (@PKG@.ClassStore.SESSION.putIfAbsent(u, Boolean.TRUE) != null) return;''',
    '''    @PKG@.Abil.mirrorSoon(u);   // 0.1.22: the ability rune slots are looked at on the next tick
    try { @PKG@.Abil.worldLeft(u, st); } catch (Throwable w0) { }   // 0.1.24 FIX ROUND: a frenzy / banner left in the old world ends
    if (@PKG@.ClassStore.SESSION.putIfAbsent(u, Boolean.TRUE) != null) return;''')

# ================================================================================================ ClassQuit, /classadmin abil info, the plugin texts
rep('''    @PKG@.AbilStore.SLIPAT.remove(u);''', '''    @PKG@.AbilStore.SLIPAT.remove(u);
    @PKG@.AbilStore.GUARDED.remove(u);   // 0.1.24: the leaver's guard / oath / buffs / armed arrow / zones (they end at their next tick)
    @PKG@.AbilStore.GUARDBY.remove(u);
    @PKG@.AbilStore.OATHS.remove(u);
    @PKG@.AbilStore.OATHW.remove(u);
    @PKG@.AbilStore.RAGE.remove(u);
    @PKG@.AbilStore.FURY.remove(u);
    @PKG@.AbilStore.WAR.remove(u);
    @PKG@.AbilStore.EXPL.remove(u);
    @PKG@.AbilStore.EXPLC.remove(u);
    @PKG@.AbilStore.FRENZ.remove(u);
    Object qb = @PKG@.AbilStore.BANNERS.remove(u);   // FIX ROUND 2: a quit ends the banner without arming its cooldown (relog = reset)
    if (qb instanceof @PKG@.AbilZone) { ((@PKG@.AbilZone) qb).ended = true; ((@PKG@.AbilZone) qb).why = "quit"; }
    @PKG@.AbilStore.SPINS.remove(u);
    @PKG@.AbilStore.RETRI.remove(u);
    try { @PKG@.AbilStore.BANKED.remove(@PKG@.ClassCfg.pkey(u)); } catch (Throwable qb0) { }   // FIX ROUND 2: keyed by pkey
    @PKG@.AbilStore.SWINGS.remove(u);
    @PKG@.AbilStore.PAID.remove(u);   // FIX ROUND: the swing-start cost record''')
rep('''" | last: " + LAST_MONK + " / " + LAST_ASN + " | rebirth: " + rbLine(@PKG@.ClassCfg.pkey(t)) + (FROST_ON ? "" : " | LANDED-HIT HOOK OFF (no combo / uncloak / Slip Away)"), null);''',
    '''" | last: " + LAST_MONK + " / " + LAST_ASN + " | rebirth: " + rbLine(@PKG@.ClassCfg.pkey(t)) + (FROST_ON ? "" : " | LANDED-HIT HOOK OFF (no combo / uncloak / Slip Away)"), null);
    send(pr, "Warrior / Berserker / Archer: taunted " + TAUNTED + ", guards " + GUARDS + ", shockwaves " + SHOCKS + ", chains " + CHAINS + ", reflects " + REFLECTS + ", oath transfers " + OATHED + ", rages " + RAGES + ", spin hits " + SPINHITS + ", splits " + SPLITS + ", frenzy hits " + FRENZYHITS + ", frenzy swings paid " + FRENZYSWINGS + ", banner kills " + BANNERKILLS + ", pins " + PINS + ", arrows " + ARROWS + ", blasts " + BLASTS + ", rain hits " + RAINHITS + ", netted " + NETTED + ", rooted " + ROOTED + ", marked " + MARKED + " | last: " + LAST_WAR + " / " + LAST_BER + " / " + LAST_ARC, null);   // 0.1.24''')
rep('''Assassin Cloak + First Strike, Toxin, God Killer, Vanishing Act; sprinting''',
    '''Assassin Cloak + First Strike, Toxin, God Killer, Vanishing Act; Warrior Rallying Guard, Shield Shockwave, Iron Chain, Challenge or Guardian's Oath; Berserker Enrage, Whirlwind, Earthsplitter, Blood Frenzy or Warlord's Banner; Archer Pinning Shot, Rapid Fire, Explosive Arrow, Arrow Rain or Hunter's Net; sprinting''')
rep('''the SkyyTrees ability panel bridges, Monk + Assassin abilities, rebirth participant rebirth:part:classes; bridge class:fn:loadoutGet''',
    '''the SkyyTrees ability panel bridges, Monk + Assassin + Warrior + Berserker + Archer abilities, rebirth participant rebirth:part:classes; bridge class:fn:loadoutGet''')

# ================================================================================================ done
assert s.count("registerCommand(") == REG0, "no new command"
assert s.count("registerSystem(") == SYS0, "no new system"
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote %s (%d changes, %d lines)" % (dst, len(CHANGES), s.count(LF)))
