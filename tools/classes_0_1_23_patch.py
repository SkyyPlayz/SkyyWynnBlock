"""Derive SkyyClasses/build_skyyclasses_0.1.23.py from the generated 0.1.22 (the SET pin; the EDITED lineage: Skyy's edited 0.1.6 ->
classes_0_1_7_patch.py -> ... -> classes_0_1_22_patch.py -> 0.1.22; classes_0_1_6_patch.py is never re-run). 0.1.22 stays untouched; its
line endings are kept.
Run:  python tools/classes_0_1_23_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.23.py   (never --deploy)
Test: python SkyyClasses/test_skyyclasses_0.1.23.py [--dir <scratch>] [--keep]

0.1.23 (2026-10-14) = MONK + ASSASSIN ON THE RUNE FRAMEWORK + REBIRTH R6 (Skyy 2026-10-14: "Link ability's to the ability buttons, and
enable the class skill trees. Add the ability controls and their modifiers to the skill trees ..." + "Basically we are making our own
runes and modifiers, then controlling them in the skill tree, instead of the vanilla controller, to lock then per class. (If 2 of your
abilities have echo modifier, the modifiers are unlocked and level separately per ability" + popup M10 "Priest + Monk + Assassin, then
Warrior + Berserker, then Archer"). Built on 0.1.22's framework (the rune keys, levels by use, modifiers, the class-tree gate + panel
bridges) - nothing forked: the 9 new abilities are rows of the same tables, the same pipeline (castAt0), jobs, zones and hooks.
  THE 9 ABILITIES (research/classes/Monk.md + Assassin.md, research/cloud/Class-Ability-Shapes.md 7-8, Class-Ability-Spec-Draft.md 2.6-2.7,
    docs/answered/classes.md - newest wins; costs = power x the class split, research/Class-Power-Split.md: Monk 38 / 62, Assassin 43 / 57):
    Monk  A1 Flowing Form (2 Mana + 1 Stamina, then 0.65 + 0.25 a second; 40 s): a 30 s aura that FOLLOWS you (5 blocks): every hit you
          land = 1 combo stack (max 20, each decays 5 s after it was gained) = +2 % move speed a stack (our own speed effects
          SkyyAbility_Spd_*; the attack-speed half waits for SkyyGear - UNVERIFIED cross-mod), enemies in the aura are AWED: the first
          time they lose their target (MarkedEntitySupport cleared every tick for 1 s - UNVERIFIED P12) then -1 % defence and -0.5 % move
          per TOTAL combo of the run (our effects SkyyAbility_Awe_1..20, caps -20 % / -10 %), Awed 10 s after it ends / they leave.
          Ends early when Mana or Stamina runs out. Shapes: Flow Sprint (starts at 2 stacks, no Stamina drain the first 3 s), on landing,
          Centred (3 stacks, 4 blocks, drain -25 %). A counted use = 5 combo reached.
          A2 Palm Strike (3 + 1; 6 s): the enemy you look at within 4 blocks: 1.2 H, stun 0.75 s (the vanilla Stun, through the boss
          stun clock armory:fn:stunhit / abil.bossWords like Frost Nova), knockback 4 blocks. Rushing Palm (a 2-block step in, push 6,
          stun 0.5), Falling Palm (knocked DOWN, stun 1 s), Rooting Palm (no push, stun 1.25 s, Awe). Each level -0.1 s cooldown to a
          5.0 s floor. Echo (Skyy L123): a second palm on the same target 1 s later.
          A2-alt Cyclone Kick (4 + 2; 8 s): everything within 3 blocks 0.8 H + pushed 5 blocks. Sweeping Kick (a 4-block arc in front,
          push 6), Dropping Kick (on landing, a 4-block ring, push 5 + knock-up), Leg Sweep (3 blocks, no push, stun 1 s).
          A1-alt A Hundred Fists (3 + 1, then 0.7 + 0.3 a second; 40 s): Flowing Form where every 10th hit releases a shockwave on every
          Awed enemy in the aura (1.0 H each, at most one per 8 s). Sprint: 2 stacks + the first wave at 8 hits; landing = 1 combo;
          Tempest Palms (crouch): every 12th hit, 1.3 H, radius -1. Echo: each wave again 1 s later, weaker.
          A1-alt B Still Water (7 + 3; 25 s): a 10 s stance: deflects projectiles from the front (cancelled), counters melee hits (the hit
          is cancelled, the attacker takes 1.0 H; at most one counter per attacker each 0.4 s), every counter Awes. Flowing Water (6 s,
          counters only, keep moving), Falling Water (starts on landing, the landing counters everything within 2 blocks for 0.5 H), Deep
          Still (12 s, every direction, 1.3 H). Echo (Skyy L124): the melee counters stay 3 s (+0.5 s a level) after the stance.
    Assassin A1 Cloak + First Strike (6 + 2; 30 s): cloaked 8 s (the vanilla Intangible_Dark look on you; every 0.25 s the mobs within 24
          blocks that target you lose you - UNVERIFIED P12) - your attack breaks it; FIRST STRIKE: your next weapon hit within 10 s
          deals +50 % (abil.firstStrike - a stand-in for "+100 % crit chance": SkyyGear has no crit door for other mods yet - a question).
          Dash Cloak (6 s + 20 % speed 3 s), Silent Landing (no fall damage 3 s: the vanilla Immunity_Fall), Still Shadow (11 s while you
          stay still, moving drops it to 8 s; First Strike +20).
          A2 Toxin (5 + 2; 16 s): a 4-block poison cloud where you look (20 blocks) for 5 s: 0.25 H a second + Weakened 15 % (our
          SkyyAbility_Weaken_*: -15 % outgoing damage). Lobbed Vial (28 blocks, 3.5), Drop (below you), Pool (at your feet, 5 blocks, 6 s).
          Echo (Skyy 2026-10-08, replaces Lingering): a second, weaker cloud 1 s later. Chain: a dying poisoned enemy passes the poison to
          the nearest enemy within 6 blocks.
          A2-alt God Killer (6 + 2; 45 s): your next weapon hit on a boss / mini-boss (abil.bossWords) within 12 s deals 2x, 3x from behind
          (the vanilla backstab rule: the target's back +-80 degrees - a Shadow Step arrival counts). Stacks with First Strike. Hunter's
          Rush (8 s, +15 % speed), Death from Above (a hit while you fall counts as a backstab), Patient Kill (stand still 1 s to arm,
          20 s window). Echo (Skyy L118): the empowered strike again 1 s later, weaker (the boss multiplier, not First Strike).
          A1-alt Vanishing Act (7 + 2; 28 s; Skyy 2026-10-08 - Shadow Clone parked, so the Assassin has ONE Ability 1 alt): a 3 s cloak + a
          4-block smoke for 3 s: enemies inside lose you (2 s from entering) and are slowed 25 %. Smoke Trail (behind you), Smoke Drop
          (where you land, 5 blocks), Ambush Smoke (the cloak lasts while you stay inside, at most 5 s). First Strike as A1.
  MODIFIERS (Skyy M8, per ability, unlocked + levelled separately per ability): two new ones in the shared table - Ricochet (stackable:
    Skyy M8 "equip ricochet twice ... double the ricochet") and Haste (not stackable). Flowing Form Duration+ Radius+ Efficiency Power+;
    Hundred Fists Power+ Radius+ Echo Efficiency; Still Water Duration+ Power+ Knockback+ Ward Echo; Palm Strike Knockback+ Ricochet Slow
    Power+ Echo; Cyclone Kick Radius+ Knockback+ Slow Haste; Cloak + First Strike Duration+ Efficiency Power+ Haste; Toxin Radius+
    Duration+ Echo Chain; God Killer Power+ Duration+ Efficiency Haste Echo; Vanishing Act Radius+ Duration+ Slow Efficiency.
  RUNES: 9 more hidden rune items SkyyAbility_Monk_* / SkyyAbility_Assassin_* (the 0.1.22 rune shape, our own icons from
    art/ability-icons) - managed ONLY from the class tree panel (lock 2026-10-14); the hook, mirror, guard and fallback are 0.1.22's.
    Vanilla runes are blocked for Monks + Assassins now too (Skyy M2; abil.vanillaRunes unlocks them).
  THE CLASS TREE (SkyyTrees 0.3.8 lists the Monk + Assassin A / M nodes): A1-A4 enable the lines, M<n>A / M<n>B the modifier slots; path
    nodes applied (Class-Tree-Paths.md 6 / 7): Monk T6 Master's Poise, PA3 Aerial Palm (Falling Palm sends the target UP, stun -10 %), PA4
    Wind Step (airborne hits = 2 stacks, stacks decay after 4 s), PB3 Concussive Palm (stun 1.0 s + the vanilla Vulnerable 2 s, +3 Mana),
    PB4 Iron Skin (-10 % damage taken at 10+ stacks, -5 % move speed while the aura runs), PB5 Iron Fist (every 3rd palm on one target
    deals x1.5 = abil.critStand, cooldown +1 s), PC1 Calm Aura (Awed enemies deal -0.4 % per total combo, max -8 %; 1.5 % speed a stack),
    PC2 Reflexes (counters stun 0.5 s; stance -2 s), PC3 Deep Breath (stacks decay after 7.5 s; start +2 Mana), PC4 Tranquility (1 % max
    Health a second in the stance; -20 % move speed), PC5 Serenity (Awed enemies deal -15 % - a stand-in for their attack speed - and the
    distraction lasts 2 s; max combo 18); Assassin T6 Shadow's Patience, PA1 Longer Cloak (+2 s, the cloak breaks 0.3 s after your hit,
    cooldown +4 s), PA2 Lethal Opener (First Strike +15; a 2nd hit within 2 s has a 50 % chance of it again; window -2 s), PA3 Boss Hunter
    (2x -> 2.3x, also ab.GodKiller.eliteWords; cooldown +10 s), PA4 Slip Away (a kill recloaks you 2 s, once per 20 s; cost +4 Mana), PA5
    Death Mark (the First Strike target: your next hit within 5 s x1.5; First Strike -10 %), PB1 Potent Mix (poison stacks to 3, +30 % each;
    cloud radius -1), PB2 Cripple (Weaken 25 %, cloud 1 s shorter), PB3 Contagion (poisoned enemies poison those within 2 blocks; poison
    -15 %), PB5 Plague (the cloud lasts twice as long, Weakened enemies take +10 % from you; cooldown +6 s). WAITING (not listed): Monk
    PA1 PA2 PA5 PB1 PB2 + T3 T4 (SkyyArmory traversal / fist nodes), T5 Calm Breath (no Stamina-regen registry); Assassin PB4 Venom Blade
    (needs a per-mob poison stack system), PC1-PC4 (SkyyArmory), PC5 Shadow Blink (the kunai arrival); Mage PA4 Meteor from the Rift (the
    SkyyArmory blink), PC2 Siphon (needs a max-Health modifier for its trade-off); Priest PA2 (Skyy's call: Guiding Light vs Radiant Pulse),
    PB2 Elemental Bubble (an element picker page). Priest PB3 + PB4 are applied since 0.1.22.
  REBIRTH R6 (research/cloud/Rebirth-Spec.md 3.2 / 4.2 / 5; SkyyRebirth 0.2's two-phase protocol, the SkyyCoins 0.1.7 participant shape):
    rebirth:part:classes (ClassRb) apply(Object[] { op, pkey, txid, ... }) -> String, never throws:
      measure  "ok:classLvl=<L>;abilities=<n>" of the ACTIVE profile pkey (nothing written)
      prepare  measure + a BACKUP of abilities/<pkey>.properties (rebirth-backup/<pkey>/<txid>/, last 3 kept) + the STAGED file
               rebirth/<pkey>.rb-<txid>.properties (rb.Lr = the class level now, rb.S.<Id> = each ability's level now; tmp + fsync +
               atomic rename). An older txid's staged file is deleted (refused while rebirth:fn:decision says it committed).
      commit   ONE fsync'd atomic write of abilities/<pkey>.properties with rb.Lr, rb.S.<Id>, rb.pick.<Id> + 1 (one modifier upgrade to
               place per ability) and rb.lastTx = txid; "done" when rb.lastTx is already txid. Ability levels, uses, modifiers and
               equips are KEPT (Skyy 5b).
      abort    deletes the staged file (refused once committed); status = committed / staged / none.
    EFFECTIVE LEVEL (spec 3.2, at every cast + modifier read): while the class level L is under rb.Lr, an ability works at
      min(level, max(F(L), half + (S - half) x L / Lr)) with half = ceil(S / 2), F(L) = min(15, 1 + 14 L / rb.classCap0); a modifier at
      min(level, ceil(level x eff / S)). Unlocked modifiers stay unlocked. The panel shows "works at Lv x".
    CAP: abil.maxLevel + n (n = rebirth:fn:count, cached 5 s). +1 MODIFIER LEVEL per rebirth per ability: class:fn:abilDo "rbpick <Id>
      <Mod>" places one rb.pick.<Id> into rb.modmax.<Id>.<Mod> (that modifier may level one step past its top; the step after the last
      = last + (last - the one before)). SkyyTrees 0.3.8's modifier list shows the button (unlocked modifiers only). A 3rd modifier slot
      every 5th rebirth (Skyy LOCKED, docs/answered/economy.md 2026-10-13) is NOT built yet - an OPEN LOCKED item (a 3rd slot row on the
      class tree page + the modifier data, the panel and the cast context) that must land before SkyyRebirth lists "classes".
    SkyyRebirth must add "classes" to its part list (RbJournal.PARTS) - another round's file.
  FIX ROUND (critics 2026-10-14): Max Up refused while rebirth:fn:busy + rb.pick moves in ONE locked step (AbilStore.setAdd; the
    commit adds +1 there too - no minted level); rbN never caches a null answer; no soft cap while SkyySkills cannot answer (levelOr);
    speed: tick callers re-send the effect only near its end (speedKeep), clears fall back to a live haste (speedClear), a replaced
    stance never clears the new one; the smoke slow every 0.5 s, the Ambush look once (AbilZone.lookUntil); the mob maps pruned every
    second (AbilTick -> pruneMobs); an invulnerable Monk is never countered; the AbilFrostSys warning names the combo / uncloak / Slip
    Away (+ FROST_ON in abil info); texts name all four ability classes; the Server Setup help names units and the walking-row rule.
  FIX ROUND 2: Max Up (rbpick) is refused on a modifier still locked at the ability's level (the modRows rule).
  LOCKED GAPS (not built, recorded): Still Water Echo's "block+counter can interrupt an attack" (Skyy L124) - the incoming hit is blocked
    and countered, your own swing is not cancelled (needs an engine probe; no text claims the interrupt); Flowing Form's attack-speed half
    (Skyy L128 / L138) - movement speed only until SkyyGear exposes attack speed.
  Saved data: abilities/<pkey>.properties gains rb.lastTx, rb.Lr, rb.S.<Id>, rb.pick.<Id>, rb.modmax.<Id>.<Mod> after a rebirth - an
    older jar ignores them. No migration.
  ROLLBACK to 0.1.22: abil.runeHud off + one login of every Monk / Assassin first (their runes leave the ability slots), else those rune
    items stay as dead items in the AbilitySlots until removed by hand; their abilities simply stop (0.1.22 has none for them).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.22.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.23.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.22"' in s and "GENERATED by tools/classes_0_1_22_patch.py from the generated 0.1.21" in s, \
    "build_skyyclasses_0.1.22.py is not the generated 0.1.22"
assert "FlowingForm" not in s and "ClassRb" not in s
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
NOTE = HEAD[HEAD.index("0.1.23 (2026-10-14)"):].rstrip()

# ================================================================================================ docstring, version
rep('''"""SkyyClasses 0.1.22 - build script (javassist via jpype). GENERATED by tools/classes_0_1_22_patch.py from the generated 0.1.21 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_21_patch.py -> 0.1.21) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.23 - build script (javassist via jpype). GENERATED by tools/classes_0_1_23_patch.py from the generated 0.1.22 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_22_patch.py -> 0.1.22) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''' + NOTE.replace(LF, LF + "  ").replace("  " + LF, LF) + '''
  Notes in tools/classes_0_1_23_patch.py. CHECKED with SkyyClasses/test_skyyclasses_0.1.23.py.
=== 0.1.22 (history; still true unless 0.1.23 above says otherwise) ===
''')
rep('VERSION = "0.1.22"', 'VERSION = "0.1.23"')

# ================================================================================================ the ability table
rep('''    ("MartyrsGrace", "Martyr's Grace", "Priest", 4, True, False), # 0.1.18: built
]
assert sorted((c, t) for _i, _n, c, t, _b, _p in ABILS) == sorted((c, t) for c in ("Mage", "Priest") for t in range(5))''',
    '''    ("MartyrsGrace", "Martyr's Grace", "Priest", 4, True, False), # 0.1.18: built
    # 0.1.23: Monk + Assassin (research/classes/Monk.md + Assassin.md; the Assassin's A1-alt is Vanishing Act only - Shadow Clone parked)
    ("FlowingForm", "Flowing Form", "Monk", 0, True, False),
    ("PalmStrike", "Palm Strike", "Monk", 1, True, False),
    ("CycloneKick", "Cyclone Kick", "Monk", 2, True, False),
    ("HundredFists", "Hundred Fists", "Monk", 3, True, False),
    ("StillWater", "Still Water", "Monk", 4, True, False),
    ("CloakFirstStrike", "Cloak + First Strike", "Assassin", 0, True, False),
    ("Toxin", "Toxin", "Assassin", 1, True, False),
    ("GodKiller", "God Killer", "Assassin", 2, True, False),
    ("VanishingAct", "Vanishing Act", "Assassin", 3, True, False),
]
assert sorted((c, t) for _i, _n, c, t, _b, _p in ABILS) == sorted([(c, t) for c in ("Mage", "Priest", "Monk") for t in range(5)] + [("Assassin", t) for t in range(4)])''')

# ================================================================================================ costs per shape (the split)
rep('''    ("MartyrsGrace", "G", "abilp", [(30, 18), (30, 18), (30, 18), (34, 20)]),
]''', '''    ("MartyrsGrace", "G", "abilp", [(30, 18), (30, 18), (30, 18), (34, 20)]),
    # 0.1.23 (research/cloud/Class-Ability-Shapes.md 7 + 8: the old Mana-only power numbers x the 2026-10-08 split)
    ("FlowingForm", "FF", "abilmk", [(6, 40), (6, 40), (6, 40), (6, 40)]),
    ("PalmStrike", "PS", "abilmk", [(8, 6), (8, 6), (8, 7), (8, 6)]),
    ("CycloneKick", "CK", "abilmk", [(10, 8), (10, 8), (10, 9), (10, 9)]),
    ("HundredFists", "HF", "abilmk", [(8, 40), (8, 40), (8, 40), (8, 40)]),
    ("StillWater", "SW", "abilmk", [(18, 25), (16, 22), (18, 25), (20, 28)]),
    ("CloakFirstStrike", "CL", "abilas", [(14, 30), (14, 30), (14, 30), (12, 30)]),
    ("Toxin", "TX", "abilas", [(12, 16), (12, 16), (12, 16), (12, 18)]),
    ("GodKiller", "GK", "abilas", [(14, 45), (14, 45), (14, 45), (14, 50)]),
    ("VanishingAct", "VA", "abilas", [(16, 28), (16, 28), (16, 28), (16, 30)]),
]''')
rep('''    "MartyrsGrace": ["Martyr's Grace", "Grace in Motion", "Descent", "Martyr's Vow"],
}''', '''    "MartyrsGrace": ["Martyr's Grace", "Grace in Motion", "Descent", "Martyr's Vow"],
    "FlowingForm": ["Flowing Form", "Flow Sprint", "Flow Landing", "Centred"],
    "PalmStrike": ["Palm Strike", "Rushing Palm", "Falling Palm", "Rooting Palm"],
    "CycloneKick": ["Cyclone Kick", "Sweeping Kick", "Dropping Kick", "Leg Sweep"],
    "HundredFists": ["Hundred Fists", "Rushing Fists", "Falling Fists", "Tempest Palms"],
    "StillWater": ["Still Water", "Flowing Water", "Falling Water", "Deep Still"],
    "CloakFirstStrike": ["Cloak", "Dash Cloak", "Silent Landing", "Still Shadow"],
    "Toxin": ["Toxin", "Lobbed Vial", "Drop", "Pool"],
    "GodKiller": ["God Killer", "Hunter's Rush", "Death from Above", "Patient Kill"],
    "VanishingAct": ["Vanishing Act", "Smoke Trail", "Smoke Drop", "Ambush Smoke"],
}''')
# the spec draft 2.6 / 2.7 costs (2026-10-08) - the split must reproduce them
rep('''    "MartyrsGrace": [(22, 2, 18), (22, 2, 18), (22, 2, 18), (25, 2, 20)],
}
_SPLIT = {"Mage": (0.78, 0.22), "Priest": (0.73, 0.27)}''', '''    "MartyrsGrace": [(22, 2, 18), (22, 2, 18), (22, 2, 18), (25, 2, 20)],
    # 0.1.23: research/cloud/Class-Ability-Spec-Draft.md 2.6 / 2.7 (Monk 38 / 62, Assassin 43 / 57)
    "FlowingForm": [(2, 1, 40)] * 4,
    "PalmStrike": [(3, 1, 6), (3, 1, 6), (3, 1, 7), (3, 1, 6)],
    "CycloneKick": [(4, 2, 8), (4, 2, 8), (4, 2, 9), (4, 2, 9)],
    "HundredFists": [(3, 1, 40)] * 4,
    "StillWater": [(7, 3, 25), (6, 2, 22), (7, 3, 25), (8, 3, 28)],
    "CloakFirstStrike": [(6, 2, 30), (6, 2, 30), (6, 2, 30), (5, 2, 30)],
    "Toxin": [(5, 2, 16), (5, 2, 16), (5, 2, 16), (5, 2, 18)],
    "GodKiller": [(6, 2, 45), (6, 2, 45), (6, 2, 45), (6, 2, 50)],
    "VanishingAct": [(7, 2, 28), (7, 2, 28), (7, 2, 28), (7, 2, 30)],
}
_SPLIT = {"Mage": (0.78, 0.22), "Priest": (0.73, 0.27), "Monk": (0.38, 0.62), "Assassin": (0.43, 0.57)}   # 0.1.23: + Monk, Assassin''')

# ================================================================================================ the new Server Setup rows
rep('''_r("abil.echoDelay", "ECHO_DELAY", "dec", 1.0, "0.2", "10", "s", "abill", "Echo delay", "Seconds from the cast (or its end) to the echo.")
''', '''_r("abil.echoDelay", "ECHO_DELAY", "dec", 1.0, "0.2", "10", "s", "abill", "Echo delay", "Seconds from the cast (or its end) to the echo.")
# 0.1.23: THE MONK + ASSASSIN NUMBERS. The JVM caps a method at 64 KB and the config kit puts every row into CfgRows' static
# initialiser (0.1.22 already used 52.9 KB): so each ability's numbers are ONE text row "ab.<Ability>.numbers" (key=value list, every
# key optional) read into AbilNum (its own class) - every number still editable in Server Setup, the page 9 rows longer instead of 90.
NUM_ROWS = []


def _n(key, field, typ, dv, lo, hi, unit, cat, label, help_, flags="live"):
    NUM_ROWS.append((key, field, typ, dv, lo, hi, unit, cat, flags, label, help_))


# 0.1.23: MONK (research/cloud/Class-Ability-Spec-Draft.md 2.6, Class-Ability-Shapes.md 7)
_n("ab.FlowingForm.drainMana", "FF_DM", "dec", 0.65, "0", "20", "", "abilmk", "Flowing Form Mana a second", "Drained while the aura runs (Hundred Fists has its own).")
_n("ab.FlowingForm.drainStamina", "FF_DS", "dec", 0.25, "0", "20", "", "abilmk", "Flowing Form Stamina a second", "Drained while the aura runs. Out of Mana or Stamina = it ends.")
_n("ab.FlowingForm.time", "FF_TIME", "dec", 30.0, "1", "120", "s", "abilmk", "Flowing Form length", "Seconds the aura lasts (Hundred Fists too).")
_n("ab.FlowingForm.radius", "FF_RADIUS", "dec", 5.0, "1", "16", "blocks", "abilmk", "Flowing Form aura", "Enemies this close are Awed.")
_n("ab.FlowingForm.maxStacks", "FF_MAX", "int", 20, "1", "40", "", "abilmk", "Most combo stacks", "Every hit you land is one stack.")
_n("ab.FlowingForm.decay", "FF_DECAY", "dec", 5.0, "0.5", "30", "s", "abilmk", "Combo stack decay", "Each stack ends this long after it was gained.")
_n("ab.FlowingForm.movePerStack", "FF_MOVE", "dec", 2.0, "0", "10", "%", "abilmk", "Move speed a stack", "Your move speed per combo stack.")
_n("ab.FlowingForm.attackPerStack", "FF_ATK", "dec", 1.5, "0", "10", "%", "abilmk", "Attack speed a stack (later)", "Waits for SkyyGear's attack speed door - shown only.", "live,adv")
_n("ab.FlowingForm.awedDefence", "FF_ADEF", "dec", 1.0, "0", "5", "%", "abilmk", "Awe: defence per total combo", "Awed enemies take more damage (max -20 % defence, -10 % speed).")
_n("ab.FlowingForm.aweLinger", "FF_ALINGER", "dec", 10.0, "1", "60", "s", "abilmk", "Awe after leaving", "Enemies stay Awed this long after the aura.")
_n("ab.FlowingForm.distract", "FF_DISTRACT", "dec", 1.0, "0", "5", "s", "abilmk", "Awe: distracted for", "A newly Awed enemy loses its target this long.")
_n("ab.FlowingForm.sprintStacks", "FF_SP_ST", "int", 2, "0", "40", "", "abilmk", "Flow Sprint start stacks", "Flow Sprint (sprint) starts with this many stacks.")
_n("ab.FlowingForm.sprintFree", "FF_SP_FREE", "dec", 3.0, "0", "30", "s", "abilmk", "Flow Sprint free Stamina", "No Stamina drain this long after a Flow Sprint.")
_n("ab.FlowingForm.centredStacks", "FF_CR_ST", "int", 3, "0", "40", "", "abilmk", "Centred start stacks", "Centred (crouch) starts with this many stacks.")
_n("ab.FlowingForm.centredRadius", "FF_CR_R", "dec", 4.0, "1", "16", "blocks", "abilmk", "Centred aura", "Centred (crouch): a smaller aura.")
_n("ab.FlowingForm.centredDrain", "FF_CR_D", "int", 25, "0", "90", "%", "abilmk", "Centred: less drain", "Centred (crouch) drains this % less.")
_n("ab.FlowingForm.countAt", "FF_COUNT", "int", 5, "1", "40", "", "abilmk", "Counted use at combo", "A run counts as a use (ability level) at this total combo.", "live,adv")
_n("ab.HundredFists.drainMana", "HF_DM", "dec", 0.7, "0", "20", "", "abilmk", "Hundred Fists Mana a second", "Drained while it runs.")
_n("ab.HundredFists.drainStamina", "HF_DS", "dec", 0.3, "0", "20", "", "abilmk", "Hundred Fists Stamina a second", "Drained while it runs.")
_n("ab.HundredFists.every", "HF_EVERY", "int", 10, "2", "100", "", "abilmk", "Shockwave every N hits", "Every Nth combo hit sends a shockwave through the Awed.")
_n("ab.HundredFists.power", "HF_POWER", "dec", 1.0, "0", "20", "x", "abilmk", "Shockwave damage (x one hit)", "Each Awed enemy in the aura takes this.")
_n("ab.HundredFists.gap", "HF_GAP", "dec", 8.0, "0", "60", "s", "abilmk", "At most one shockwave every", "Seconds between two shockwaves.")
_n("ab.HundredFists.sprintEvery", "HF_SP_EVERY", "int", 8, "2", "100", "", "abilmk", "Rushing Fists first wave at", "Sprint shape: the first wave comes at this hit.")
_n("ab.HundredFists.tempestEvery", "HF_CR_EVERY", "int", 12, "2", "100", "", "abilmk", "Tempest Palms: every N hits", "Crouch shape: rarer, stronger waves.")
_n("ab.HundredFists.tempestPower", "HF_CR_POWER", "dec", 1.3, "0", "20", "x", "abilmk", "Tempest Palms damage", "x one hit (radius -1 block).")
_n("ab.StillWater.time", "SW_TIME", "dec", 10.0, "1", "60", "s", "abilmk", "Still Water length", "Seconds the stance lasts.")
_n("ab.StillWater.counter", "SW_POWER", "dec", 1.0, "0", "20", "x", "abilmk", "Counter damage (x one hit)", "A blocked melee hit strikes back this hard.")
_n("ab.StillWater.front", "SW_FRONT", "dec", 90.0, "10", "180", "", "abilmk", "Deflect angle (degrees)", "Projectiles within this many degrees of your look are deflected.")
_n("ab.StillWater.gap", "SW_GAP", "dec", 0.4, "0", "5", "s", "abilmk", "One counter per attacker every", "Seconds between two counters on one attacker.", "live,adv")
_n("ab.StillWater.sprintTime", "SW_SP_TIME", "dec", 6.0, "1", "60", "s", "abilmk", "Flowing Water length", "Sprint shape: counters only, you keep moving.")
_n("ab.StillWater.landRadius", "SW_AIR_R", "dec", 2.0, "0.5", "8", "blocks", "abilmk", "Falling Water landing", "The landing counters everything this close.")
_n("ab.StillWater.landPower", "SW_AIR_P", "dec", 0.5, "0", "20", "x", "abilmk", "Falling Water landing damage", "x one hit.")
_n("ab.StillWater.deepTime", "SW_CR_TIME", "dec", 12.0, "1", "60", "s", "abilmk", "Deep Still length", "Crouch shape: every direction.")
_n("ab.StillWater.deepPower", "SW_CR_P", "dec", 1.3, "0", "20", "x", "abilmk", "Deep Still counter", "x one hit.")
_n("ab.StillWater.echoTime", "SW_ECHO_T", "dec", 3.0, "0.5", "20", "s", "abilmk", "Still Water Echo length", "Counters stay this long after the stance (+0.5 s a level).")
_n("ab.PalmStrike.power", "PS_POWER", "dec", 1.2, "0", "20", "x", "abilmk", "Palm Strike damage (x one hit)", "One hit = abil.hitFallback for Monk weapons.")
_n("ab.PalmStrike.stun", "PS_STUN", "dec", 0.75, "0", "5", "s", "abilmk", "Palm Strike stun", "The vanilla Stun (bosses: the stun clock).")
_n("ab.PalmStrike.push", "PS_PUSH", "dec", 4.0, "0", "20", "blocks", "abilmk", "Palm Strike knockback", "Blocks the target is pushed.")
_n("ab.PalmStrike.reach", "PS_REACH", "dec", 4.0, "1", "12", "blocks", "abilmk", "Palm Strike reach", "The enemy you look at, this close.")
_n("ab.PalmStrike.cdFloor", "PS_CD_FLOOR", "dec", 5.0, "0", "60", "s", "abilmk", "Palm Strike cooldown floor", "Levels cut the cooldown down to this.")
_n("ab.PalmStrike.cdPerLevel", "PS_CD_LVL", "dec", 0.1, "0", "5", "s", "abilmk", "Palm Strike cooldown a level", "Seconds off per ability level above 1.")
_n("ab.PalmStrike.sprintStep", "PS_SP_STEP", "dec", 2.0, "0", "6", "blocks", "abilmk", "Rushing Palm step", "Sprint shape: you step in this far.")
_n("ab.PalmStrike.sprintPush", "PS_SP_PUSH", "dec", 6.0, "0", "20", "blocks", "abilmk", "Rushing Palm knockback", "Sprint shape knockback.")
_n("ab.PalmStrike.sprintStun", "PS_SP_STUN", "dec", 0.5, "0", "5", "s", "abilmk", "Rushing Palm stun", "Sprint shape stun.")
_n("ab.PalmStrike.airStun", "PS_AI_STUN", "dec", 1.0, "0", "5", "s", "abilmk", "Falling Palm stun", "Mid-air shape: knocked down.")
_n("ab.PalmStrike.rootStun", "PS_CR_STUN", "dec", 1.25, "0", "5", "s", "abilmk", "Rooting Palm stun", "Crouch shape: no knockback, Awe.")
_n("ab.CycloneKick.radius", "CK_RADIUS", "dec", 3.0, "1", "12", "blocks", "abilmk", "Cyclone Kick size", "Everything this close is kicked.")
_n("ab.CycloneKick.power", "CK_POWER", "dec", 0.8, "0", "20", "x", "abilmk", "Cyclone Kick damage (x one hit)", "Each enemy kicked.")
_n("ab.CycloneKick.push", "CK_PUSH", "dec", 5.0, "0", "20", "blocks", "abilmk", "Cyclone Kick push", "Blocks enemies are pushed out.")
_n("ab.CycloneKick.sweepRadius", "CK_SP_R", "dec", 4.0, "1", "12", "blocks", "abilmk", "Sweeping Kick size", "Sprint shape: an arc in front.")
_n("ab.CycloneKick.sweepPush", "CK_SP_PUSH", "dec", 6.0, "0", "20", "blocks", "abilmk", "Sweeping Kick push", "Sprint shape push.")
_n("ab.CycloneKick.dropRadius", "CK_AI_R", "dec", 4.0, "1", "12", "blocks", "abilmk", "Dropping Kick size", "Mid-air shape: a ring where you land.")
_n("ab.CycloneKick.legStun", "CK_CR_STUN", "dec", 1.0, "0", "5", "s", "abilmk", "Leg Sweep stun", "Crouch shape: knocked down, no push.")
_n("ab.CycloneKick.haste", "CK_HASTE", "int", 20, "0", "80", "%", "abilmk", "Haste: speed after the kick", "The Haste modifier (3 s + 1 s a level).")
# 0.1.23: ASSASSIN (research/cloud/Class-Ability-Spec-Draft.md 2.7, Class-Ability-Shapes.md 8)
_n("ab.CloakFirstStrike.time", "CL_TIME", "dec", 8.0, "1", "60", "s", "abilas", "Cloak length", "Your attack ends it sooner.")
_n("ab.CloakFirstStrike.window", "CL_WINDOW", "dec", 10.0, "1", "60", "s", "abilas", "First Strike window", "Your next hit within this is a First Strike.")
_n("ab.CloakFirstStrike.strike", "CL_STRIKE", "int", 50, "0", "500", "%", "abilas", "First Strike extra damage", "Stand-in for +100 % crit chance (SkyyGear has no crit door yet).")
_n("ab.CloakFirstStrike.lose", "CL_LOSE", "dec", 24.0, "2", "64", "blocks", "abilas", "Mobs that lose you", "While cloaked, mobs this close that target you lose you.")
_n("ab.CloakFirstStrike.dashTime", "CL_SP_TIME", "dec", 6.0, "1", "60", "s", "abilas", "Dash Cloak length", "Sprint shape.")
_n("ab.CloakFirstStrike.dashSpeed", "CL_SP_SPEED", "int", 20, "0", "80", "%", "abilas", "Dash Cloak speed", "For 3 s after a Dash Cloak.")
_n("ab.CloakFirstStrike.stillTime", "CL_CR_TIME", "dec", 11.0, "1", "60", "s", "abilas", "Still Shadow length", "Crouch shape, while you stay still (moving = 8 s).")
_n("ab.CloakFirstStrike.stillBonus", "CL_CR_BONUS", "int", 20, "0", "200", "%", "abilas", "Still Shadow First Strike bonus", "Added to the First Strike.")
_n("ab.CloakFirstStrike.haste", "CL_HASTE", "int", 20, "0", "80", "%", "abilas", "Haste: speed while cloaked", "The Haste modifier.")
_n("ab.Toxin.range", "TX_RANGE", "dec", 20.0, "2", "64", "blocks", "abilas", "Toxin reach", "The vial lands where you look, this far at most.")
_n("ab.Toxin.radius", "TX_RADIUS", "dec", 4.0, "1", "16", "blocks", "abilas", "Toxin cloud size", "Enemies inside are poisoned.")
_n("ab.Toxin.time", "TX_TIME", "dec", 5.0, "1", "60", "s", "abilas", "Toxin cloud length", "Seconds the cloud lasts.")
_n("ab.Toxin.poison", "TX_POISON", "dec", 0.25, "0", "10", "x", "abilas", "Poison a second (x one hit)", "Damage each second inside.")
_n("ab.Toxin.weaken", "TX_WEAKEN", "int", 15, "0", "30", "%", "abilas", "Weakened (less damage dealt)", "Poisoned enemies deal this % less.")
_n("ab.Toxin.lobRange", "TX_SP_RANGE", "dec", 28.0, "2", "64", "blocks", "abilas", "Lobbed Vial reach", "Sprint shape.")
_n("ab.Toxin.lobRadius", "TX_SP_R", "dec", 3.5, "1", "16", "blocks", "abilas", "Lobbed Vial cloud", "Sprint shape cloud size.")
_n("ab.Toxin.poolRadius", "TX_CR_R", "dec", 5.0, "1", "16", "blocks", "abilas", "Pool size", "Crouch shape: at your feet.")
_n("ab.Toxin.poolTime", "TX_CR_T", "dec", 6.0, "1", "60", "s", "abilas", "Pool length", "Crouch shape.")
_n("ab.Toxin.chainRange", "TX_CHAIN_R", "dec", 6.0, "1", "32", "blocks", "abilas", "Chain: jump range", "The Chain modifier: a dying poisoned enemy passes it this far.")
_n("ab.GodKiller.window", "GK_WINDOW", "dec", 12.0, "1", "120", "s", "abilas", "God Killer window", "Your next hit on a boss within this is empowered.")
_n("ab.GodKiller.mult", "GK_MULT", "dec", 2.0, "1", "20", "x", "abilas", "God Killer multiplier", "The empowered hit on a boss / mini-boss.")
_n("ab.GodKiller.backMult", "GK_BACK", "dec", 3.0, "1", "20", "x", "abilas", "God Killer from behind", "When the hit is a backstab.")
_n("ab.GodKiller.backAngle", "GK_ANGLE", "dec", 80.0, "10", "180", "", "abilas", "Backstab angle (degrees)", "Within this many degrees of the target's back.", "live,adv")
_r("ab.GodKiller.eliteWords", "GK_ELITE", "text", "Elite,Captain,Champion,Alpha,Brute", "", "200", "", "abilas", "Elites (Boss Hunter)",
   "Role words God Killer also takes with the Boss Hunter node.", "live,adv")
_n("ab.GodKiller.rushWindow", "GK_SP_WIN", "dec", 8.0, "1", "120", "s", "abilas", "Hunter's Rush window", "Sprint shape.")
_n("ab.GodKiller.rushSpeed", "GK_SP_SPEED", "int", 15, "0", "80", "%", "abilas", "Hunter's Rush speed", "During the window.")
_n("ab.GodKiller.patientWindow", "GK_CR_WIN", "dec", 20.0, "1", "120", "s", "abilas", "Patient Kill window", "Crouch shape (stand still 1 s to arm).")
_n("ab.GodKiller.haste", "GK_HASTE", "int", 25, "0", "80", "%", "abilas", "Haste: speed after the strike", "The Haste modifier (3 s + 1 s a level).")
_n("ab.VanishingAct.cloak", "VA_CLOAK", "dec", 3.0, "0.5", "30", "s", "abilas", "Vanishing Act cloak", "Seconds you are cloaked.")
_n("ab.VanishingAct.radius", "VA_RADIUS", "dec", 4.0, "1", "16", "blocks", "abilas", "Smoke size", "Enemies inside lose you and are slowed.")
_n("ab.VanishingAct.time", "VA_TIME", "dec", 3.0, "0.5", "30", "s", "abilas", "Smoke length", "Seconds the smoke stays.")
_n("ab.VanishingAct.lose", "VA_LOSE", "dec", 2.0, "0", "10", "s", "abilas", "Lose you for", "From the moment an enemy enters the smoke.")
_n("ab.VanishingAct.slow", "VA_SLOW", "int", 25, "0", "30", "%", "abilas", "Smoke slow", "Enemies inside move this % slower (Slow modifier: 50 %).")
_n("ab.VanishingAct.dropRadius", "VA_AI_R", "dec", 5.0, "1", "16", "blocks", "abilas", "Smoke Drop size", "Mid-air shape: where you land.")
_n("ab.VanishingAct.ambushCloak", "VA_CR_CLOAK", "dec", 5.0, "0.5", "30", "s", "abilas", "Ambush Smoke cloak", "Crouch shape: cloaked while inside, at most this.")
# the text rows (one per ability, in ABILS order) + the AbilNum fields they fill
NUM_ABILS = []
for _row in NUM_ROWS:
    _aid = _row[0].split(".")[1]
    if _aid not in NUM_ABILS:
        NUM_ABILS.append(_aid)
assert sorted(NUM_ABILS) == sorted(["FlowingForm", "HundredFists", "StillWater", "PalmStrike", "CycloneKick", "CloakFirstStrike", "Toxin", "GodKiller", "VanishingAct"])


def _numtxt(v):
    return str(int(v)) if float(v) == int(v) else repr(float(v))


NUM_TEXT = {}
for _aid in NUM_ABILS:
    _rs = [r_ for r_ in NUM_ROWS if r_[0].split(".")[1] == _aid]
    NUM_TEXT[_aid] = ",".join("%s=%s" % (r_[0].split(".")[2], _numtxt(r_[3])) for r_ in _rs)
    assert len(NUM_TEXT[_aid]) <= 380 and all(32 <= ord(c_) < 127 for c_ in NUM_TEXT[_aid]), _aid
    _pre = _rs[0][1].split("_")[0]
    _nm = dict((a[0], a[1]) for a in ABILS)[_aid]
    _r("ab.%s.numbers" % _aid, "%s_NUMS" % _pre, "text", NUM_TEXT[_aid], "", "400", "", _rs[0][7], (_nm + " numbers")[:40],
       "key=value: time s, radius/range blocks, speed/slow/weaken %, power x one hit; no key = its default")
# 0.1.23 shared
_r("abil.pushPerBlock", "PUSH_PER_BLOCK", "dec", 2.0, "0.5", "6", "", "abilmk", "Knockback speed per block", "How hard a knockback of N blocks pushes (speed = N x this).", "live,adv")
_r("abil.critStand", "CRIT_STAND", "int", 50, "0", "500", "%", "abilmk", "Ability crit (stand-in)", "Iron Fist's crit = this much extra until SkyyGear opens a crit door.", "live,adv")
_r("abil.speedCap", "SPEED_CAP", "int", 60, "0", "80", "%", "abilmk", "Most ability move speed", "Flowing Form + Haste together never go past this.", "live,adv")
# 0.1.23 REBIRTH R6 (research/cloud/Rebirth-Spec.md 3.2)
_r("rb.classCap0", "RB_CAP0", "int", 100, "1", "1000", "", "abill", "First-run class level cap", "Rebirth: the floor F(L) = min(15, 1 + 14 L / this).", "live,adv")
''')
rep('''            ("abilk", "Ability keys"), ("abill", "Ability levels")]                                         # 0.1.22''',
    '''            ("abilk", "Ability keys"), ("abill", "Ability levels"),                                         # 0.1.22
            ("abilmk", "Monk abilities"), ("abilas", "Assassin abilities")]                                 # 0.1.23''')
rep('''_r("abil.runeKeys", "RUNE_KEYS", "bool", True, "", "", "", "abilk", "Cast with the Ability 2 / 3 keys",
   "Mage + Priest: the keys cast your 2 primaries, crouch + key your alts (runes in the ability slots).")''',
    '''_r("abil.runeKeys", "RUNE_KEYS", "bool", True, "", "", "", "abilk", "Cast with the Ability 2 / 3 keys",
   "Classes with abilities: the keys cast your 2 primaries, crouch + key your alts (runes).")''')
rep('''_r("abil.vanillaRunes", "VAN_RUNES", "bool", False, "", "", "", "abilk", "Vanilla runes for Mage + Priest",''',
    '''_r("abil.vanillaRunes", "VAN_RUNES", "bool", False, "", "", "", "abilk", "Vanilla runes for ability classes",''')

# affordability at the unlock level (research/Class-Power-Split.md pools: base + per level; Monk 21 + 2 / 20 + 0.13, Assassin 24 + 2 / 19 + 0.12)
rep('''         ("Priest", 1): (47, 15.06), ("Priest", 10): (92, 15.6), ("Priest", 20): (142, 16.2), ("Priest", 30): (192, 16.8)}''',
    '''         ("Priest", 1): (47, 15.06), ("Priest", 10): (92, 15.6), ("Priest", 20): (142, 16.2), ("Priest", 30): (192, 16.8),
         ("Monk", 1): (23, 20.13), ("Monk", 10): (41, 21.3), ("Monk", 20): (61, 22.6), ("Monk", 30): (81, 23.9),            # 0.1.23
         ("Assassin", 1): (26, 19.12), ("Assassin", 10): (44, 20.2), ("Assassin", 20): (64, 21.4), ("Assassin", 30): (84, 22.6)}''')
rep('''assert _aff == 37, _aff          # the plan's "all 37 shape rows PASS"''',
    '''assert _aff == 37 + 20 + 16, _aff          # the plan's "all 37 shape rows PASS" + 0.1.23: Monk 5 x 4, Assassin 4 x 4''')
rep('''"Walk - heals the lowest players in a chain. Sprint - the one you look at first. Air - you first. Crouch - Martyr's Vow."}   # 0.1.18: the Abilities page's one line per ability''',
    '''"Walk - heals the lowest players in a chain. Sprint - the one you look at first. Air - you first. Crouch - Martyr's Vow."}   # 0.1.18: the Abilities page's one line per ability
ABIL_DESCS_.update({   # 0.1.23
    "FlowingForm": "An aura: every hit = a combo stack (speed), enemies near you are Awed. Sprint - 2 stacks. Air - on landing. Crouch - Centred.",
    "PalmStrike": "Walk - stun + knock back the enemy you look at. Sprint - step in. Air - knock it down. Crouch - Rooting Palm (Awe).",
    "CycloneKick": "Walk - kick everything around you away. Sprint - an arc in front. Air - a ring where you land. Crouch - Leg Sweep (stun).",
    "HundredFists": "Flowing Form where every 10th hit sends a shockwave through the Awed. Crouch - Tempest Palms (rarer, stronger).",
    "StillWater": "A stance: deflect projectiles, counter melee hits. Sprint - counters only. Air - on landing. Crouch - Deep Still (all around).",
    "CloakFirstStrike": "Cloaked (mobs lose you), your next hit is a First Strike. Sprint - faster. Air - no fall damage. Crouch - Still Shadow.",
    "Toxin": "Walk - a poison cloud where you look (Weakens). Sprint - thrown farther. Air - below you. Crouch - Pool at your feet.",
    "GodKiller": "Your next hit on a boss deals 2x (3x from behind). Sprint - faster. Air - falling hits backstab. Crouch - Patient Kill.",
    "VanishingAct": "A short cloak + smoke: enemies inside lose you, slowed. Sprint - behind you. Air - where you land. Crouch - Ambush Smoke.",
})''')

# ================================================================================================ modifier + rune tables
rep('''        ("Echo", "Echo", False)]
MOD_IDS = [m[0] for m in MODS]''', '''        ("Echo", "Echo", False),
        ("Ricochet", "Ricochet", True), ("Haste", "Haste", False)]   # 0.1.23: Skyy M8 "equip ricochet twice ... double the ricochet"
MOD_IDS = [m[0] for m in MODS]''')
rep('''    "MartyrsGrace": ["Power", "Chain", "Efficiency", "Ward", "Echo"],
}''', '''    "MartyrsGrace": ["Power", "Chain", "Efficiency", "Ward", "Echo"],
    # 0.1.23 (research/classes/Monk.md + Assassin.md, newest wins: Toxin Echo replaces Lingering 2026-10-08)
    "FlowingForm": ["Duration", "Radius", "Efficiency", "Power"],
    "PalmStrike": ["Knockback", "Ricochet", "Slow", "Power", "Echo"],
    "CycloneKick": ["Radius", "Knockback", "Slow", "Haste"],
    "HundredFists": ["Power", "Radius", "Echo", "Efficiency"],
    "StillWater": ["Duration", "Power", "Knockback", "Ward", "Echo"],
    "CloakFirstStrike": ["Duration", "Efficiency", "Power", "Haste"],
    "Toxin": ["Radius", "Duration", "Echo", "Chain"],
    "GodKiller": ["Power", "Duration", "Efficiency", "Haste", "Echo"],
    "VanishingAct": ["Radius", "Duration", "Slow", "Efficiency"],
}''')
rep('''assert "Follow" in AB_MODS["ShieldBubble"] and "Follow" in AB_MODS["ManaBarrier"], "Skyy's Follow locks (L113, L53)"''',
    '''assert "Follow" in AB_MODS["ShieldBubble"] and "Follow" in AB_MODS["ManaBarrier"], "Skyy's Follow locks (L113, L53)"
assert all("Echo" in AB_MODS[_a] for _a in ("PalmStrike", "StillWater", "GodKiller", "Toxin", "HundredFists")), "Skyy's Echo locks (L118, L123, L124, 2026-10-08)"
assert "Lingering" not in AB_MODS["Toxin"], "Toxin: Echo replaced Lingering (Skyy 2026-10-08)"''')
rep('''           "MartyrsGrace": "heal"}''', '''           "MartyrsGrace": "heal",
           "FlowingForm": "speed per stack", "PalmStrike": "damage", "CycloneKick": "damage", "HundredFists": "shockwave damage",
           "StillWater": "counter damage", "CloakFirstStrike": "First Strike damage", "Toxin": "poison damage", "GodKiller": "boss multiplier",
           "VanishingAct": "smoke"}''')
rep('''assert [a[0] for a in RUNE_ABILS] == ["Meteor", "ManaBarrier", "FrostNova", "Starfall", "ArcaneBeam", "SacredHeal", "ShieldBubble",
                                      "Sanctuary", "MartyrsGrace"]''',
    '''assert [a[0] for a in RUNE_ABILS] == ["Meteor", "ManaBarrier", "FrostNova", "Starfall", "ArcaneBeam", "SacredHeal", "ShieldBubble",
                                      "Sanctuary", "MartyrsGrace", "FlowingForm", "PalmStrike", "CycloneKick", "HundredFists", "StillWater",
                                      "CloakFirstStrike", "Toxin", "GodKiller", "VanishingAct"]''')
rep('''          "Priest": ["T3", "T4", "T6", "TS", "PA1", "PA3", "PA4", "PA5", "PB1", "PB3", "PB4", "PB5"]}   # fix round: + PB3 Layered Ward, PB4 Spirit Shield
TREE_SLOTS = ["A1", "A2", "A3", "A4", "M1A", "M1B", "M2A", "M2B", "M3A", "M3B", "M4A", "M4B"]
TREE_READS = ",".join("Class.%s.%s" % (_c, _n) for _c in ("Mage", "Priest") for _n in TREE_SLOTS + TREE_K[_c])''',
    '''          "Priest": ["T3", "T4", "T6", "TS", "PA1", "PA3", "PA4", "PA5", "PB1", "PB3", "PB4", "PB5"],   # fix round: + PB3 Layered Ward, PB4 Spirit Shield
          # 0.1.23 (Class-Tree-Paths.md 6 / 7): the nodes this build applies; the rest wait (SkyyArmory moves, a later hook)
          "Monk": ["T6", "PA3", "PA4", "PB3", "PB4", "PB5", "PC1", "PC2", "PC3", "PC4", "PC5"],
          "Assassin": ["T6", "PA1", "PA2", "PA3", "PA4", "PA5", "PB1", "PB2", "PB3", "PB5"]}
TREE_SLOTS = ["A1", "A2", "A3", "A4", "M1A", "M1B", "M2A", "M2B", "M3A", "M3B", "M4A", "M4B"]
TREE_READS = ",".join("Class.%s.%s" % (_c, _n) for _c in ("Mage", "Priest", "Monk", "Assassin") for _n in TREE_SLOTS + TREE_K[_c])''')
rep('''    "# abil.maxLevel ... = ability levels by use (diminishing returns); mods.* = the modifiers (unlock levels, steps, per level).",
''', '''    "# abil.maxLevel ... = ability levels by use (diminishing returns); mods.* = the modifiers (unlock levels, steps, per level).",
    "# 0.1.23: ab.FlowingForm.* ... ab.VanishingAct.* = the Monk + Assassin abilities; rb.classCap0 = the rebirth soft-cap floor.",
''')

# ================================================================================================ the effect assets (asset pack)
# our own entity effects: move speed tiers (players), Awe tiers (mobs), Weaken tiers (mobs), the cloak look. Every vanilla id they name is
# checked against Assets.zip; every number is ours (nothing copied - the damage-type KEY names are read from the vanilla Enrage buff).
rep('''RUNE_FILES["Server/Abilities/Keywords/SkyyClass.json"] = json.dumps({"Name": "server.ui.abilityKeywords.SkyyClass"}, indent=2)''',
    '''RUNE_FILES["Server/Abilities/Keywords/SkyyClass.json"] = json.dumps({"Name": "server.ui.abilityKeywords.SkyyClass"}, indent=2)
# 0.1.23: THE MONK + ASSASSIN EFFECTS (our numbers; vanilla ids only referenced)
_enr = json.loads(_ASSETS.read("Server/Entity/Effects/Abilities/Ability_Enrage_Buff.json").decode("utf-8-sig"))
DMG_TYPES = sorted(_enr["DamageResistance"])
OUT_TYPES = sorted(_enr["OutgoingDamage"])
assert len(DMG_TYPES) >= 6 and "Physical" in OUT_TYPES and "Projectile" in OUT_TYPES, (DMG_TYPES, OUT_TYPES)
_haste = json.loads(_ASSETS.read("Server/Entity/Effects/Npc/Bear_Voidtaken/Bear_Voidtaken_Roar_Haste.json").decode("utf-8-sig"))
assert _haste["ApplicationEffects"]["HorizontalSpeedMultiplier"] > 1.0, "HorizontalSpeedMultiplier is no longer an effect field"
assert "Server/Entity/ModelVFX/Intangible_Dark.json" in _azn, "the vanilla Intangible_Dark look moved (the cloak)"
assert "Server/Entity/Effects/Immunity/Immunity_Fall.json" in _azn, "the vanilla Immunity_Fall effect moved (Silent Landing)"
assert "Server/Entity/Effects/Status/Vulnerable.json" in _azn, "the vanilla Vulnerable effect moved (Concussive Palm)"
EF_IDS = []
for _n in range(0, 111):          # SkyyAbility_Spd_<n> = move speed (n - 30) %: -30 .. +80
    _pct = _n - 30
    if _pct == 0:
        continue
    _id = "SkyyAbility_Spd_%d" % _n
    EF_IDS.append(_id)
    RUNE_FILES["Server/Entity/Effects/SkyyClasses/%s.json" % _id] = json.dumps({
        "Duration": 1.5, "OverlapBehavior": "Overwrite", "Debuff": _pct < 0,
        "ApplicationEffects": {"HorizontalSpeedMultiplier": round(1.0 + _pct / 100.0, 4)}}, indent=2)
for _i in range(1, 21):           # SkyyAbility_Awe_<i>: -i % defence (every damage type), -i/2 % move speed
    _id = "SkyyAbility_Awe_%d" % _i
    EF_IDS.append(_id)
    RUNE_FILES["Server/Entity/Effects/SkyyClasses/%s.json" % _id] = json.dumps({
        "Duration": 10.0, "OverlapBehavior": "Overwrite", "Debuff": True,
        "ApplicationEffects": {"HorizontalSpeedMultiplier": round(1.0 - 0.005 * _i, 4)},
        "DamageResistance": dict((_t, [{"CalculationType": "Percent", "Amount": round(-0.01 * _i, 4)}]) for _t in DMG_TYPES)}, indent=2)
for _p in range(10, 41):          # SkyyAbility_Weaken_<p>: the poisoned deal p % less
    _id = "SkyyAbility_Weaken_%d" % _p
    EF_IDS.append(_id)
    RUNE_FILES["Server/Entity/Effects/SkyyClasses/%s.json" % _id] = json.dumps({
        "Duration": 2.0, "OverlapBehavior": "Overwrite", "Debuff": True,
        "OutgoingDamage": dict((_t, [{"CalculationType": "Percent", "Amount": round(-_p / 100.0, 4)}]) for _t in OUT_TYPES)}, indent=2)
EF_IDS.append("SkyyAbility_Cloak")
RUNE_FILES["Server/Entity/Effects/SkyyClasses/SkyyAbility_Cloak.json"] = json.dumps({
    "Duration": 8.0, "OverlapBehavior": "Overwrite", "ApplicationEffects": {"ModelVFXId": "Intangible_Dark"}}, indent=2)
for _id in EF_IDS:
    assert not [n for n in _azn if n.rsplit("/", 1)[-1].split(".")[0] == _id], "vanilla already has an asset named " + _id
print("0.1.23 effects: %d (speed tiers, Awe 1-20, Weaken 10-40, the cloak)" % len(EF_IDS))''')
rep('''        assert not [_i for _i in ("SkyyClass",) + tuple(rune_id(a) for a in RUNE_ABILS) if _i in _ids], "%s uses one of our ids" % _m''',
    '''        assert not [_i for _i in ("SkyyClass",) + tuple(rune_id(a) for a in RUNE_ABILS) + tuple(EF_IDS) if _i in _ids], "%s uses one of our ids" % _m''')

# ================================================================================================ AbilDefs: the new indices, the class-aware A1-alt pick
rep('''for _n_, _id_ in (("FROST", "FrostNova"), ("STARF", "Starfall"), ("BEAM", "ArcaneBeam"), ("GUARD", "GuardianSpirit"), ("SANCT", "Sanctuary"),
                  ("GRACE", "MartyrsGrace")):''',
    '''for _n_, _id_ in (("FROST", "FrostNova"), ("STARF", "Starfall"), ("BEAM", "ArcaneBeam"), ("GUARD", "GuardianSpirit"), ("SANCT", "Sanctuary"),
                  ("GRACE", "MartyrsGrace"),
                  # 0.1.23
                  ("FFORM", "FlowingForm"), ("PALM", "PalmStrike"), ("CYCLONE", "CycloneKick"), ("HFISTS", "HundredFists"),
                  ("STILLW", "StillWater"), ("CLOAK", "CloakFirstStrike"), ("TOXIN", "Toxin"), ("GODK", "GodKiller"), ("VANISH", "VanishingAct")):''')
# a class with ONE Ability 1 alt (the Assassin: Vanishing Act) - its pick is always A (tier 3)
rep('''M(abdefs, r"""
public static boolean owns(int ai, int level, boolean grant, String pick) {
  if (ai < 0 || ai >= IDS.length) return false;
  int t = TIER[ai];
  if (t >= 3 && t != pickTier(pick)) return false;''', '''M(abdefs, r"""
public static int pickTierC(int ci, String pick) {
  if (of(ci, 4) < 0) return 3;   // 0.1.23: one Ability 1 alt only (the Assassin)
  return pickTier(pick);
}""")
M(abdefs, r"""
public static boolean owns(int ai, int level, boolean grant, String pick) {
  if (ai < 0 || ai >= IDS.length) return false;
  int t = TIER[ai];
  if (t >= 3 && t != pickTierC(CLS[ai], pick)) return false;''')
rep('''public static String[] defaults(int ci, String pick) {
  int[] tiers = new int[] { 0, 1, 2, pickTier(pick) };''', '''public static String[] defaults(int ci, String pick) {
  int[] tiers = new int[] { 0, 1, 2, pickTierC(ci, pick) };''')

# ================================================================================================ AbilModDefs: a modifier past its top level (rebirth)
rep('''public static long modNext(long uses) {
  int[] st = steps();
  for (int i = 0; i < st.length; i++) if (uses < (long) st[i]) return (long) st[i] - uses;
  return 0L;
}""")''', '''public static long modNext(long uses) {
  int[] st = steps();
  for (int i = 0; i < st.length; i++) if (uses < (long) st[i]) return (long) st[i] - uses;
  return 0L;
}""")
# 0.1.23 REBIRTH: extra = the rebirth upgrades placed on this modifier (rb.modmax.<Id>.<Mod>): one more level each, the step after the
# last = last + (last - the one before)
M(abmods, r"""
public static long stepX(int k) {
  int[] st = steps();
  if (st.length == 0) return 0L;
  long last = (long) st[st.length - 1];
  long prev = st.length > 1 ? (long) st[st.length - 2] : 0L;
  long gap = last - prev;
  if (gap < 1L) gap = 1L;
  return last + gap * (long) k;
}""")
M(abmods, r"""
public static int modLevelX(long uses, int extra) {
  int l = modLevel(uses);
  if (extra <= 0 || l < steps().length + 1) return l;
  for (int k = 1; k <= extra && k <= 50; k++) if (uses >= stepX(k)) l++;
  return l;
}""")
M(abmods, r"""
public static long modNextX(long uses, int extra) {
  long n = modNext(uses);
  if (n > 0L || extra <= 0) return n;
  for (int k = 1; k <= extra && k <= 50; k++) { long s = stepX(k); if (uses < s) return s - uses; }
  return 0L;
}""")''')

# ================================================================================================ AbilJob / AbilZone fields, AbilStore maps
rep('''           "public @PKG@.AbilCtx cx;"):   # 0.1.22: the cast's resolved numbers (levels, modifiers, tree); kind 9 = Lingering, 10 = Echo''',
    '''           "public @PKG@.AbilCtx cx;",   # 0.1.22: the cast's resolved numbers (levels, modifiers, tree); kind 9 = Lingering, 10 = Echo
           # 0.1.23: tref = the target (a Ref); kind 11 = a Palm Strike, 12 = a Cyclone Kick, 14 = God Killer's echo hit, 15 = Patient
           # Kill's arming, 16 = a chained poison (Toxin Chain)
           "public Object tref;", "public double stun;", "public double push;"):''')
rep('''           "public @PKG@.AbilCtx cx;", "public boolean follow;", "public double h;", "public boolean echoed;", "public long nextCleanse;"):''',
    '''           "public @PKG@.AbilCtx cx;", "public boolean follow;", "public double h;", "public boolean echoed;", "public long nextCleanse;",
           # 0.1.23: kind 8 = the Flow aura (Flowing Form / Hundred Fists), 9 = the Still Water stance, 10 = a Toxin cloud, 11 = a Vanishing
           # Act smoke, 12 = a cloak; ring = the combo gain times, total = the run's combo, n1 / n2 / t1 / t2 / d1 / d2 = per kind
           "public long[] ring;", "public int total;", "public int n1;", "public int n2;", "public long t1;", "public long t2;",
           "public double d1;", "public double d2;", "public int ai;",
           "public long lookUntil;"):''')   # FIX ROUND: a cloak's look runs until (Ambush Smoke puts it on once up to its cap)
rep('''  if (z.kind == 3 || z.kind == 4 || z.kind == 7) { this.zones.add(z); this.nz = this.zones.size(); return 0; }   // 0.1.18: short effects never count (0.1.22: + 7)''',
    '''  if (z.kind == 3 || z.kind == 4 || z.kind == 7 || z.kind == 8 || z.kind == 9 || z.kind == 12) { this.zones.add(z); this.nz = this.zones.size(); return 0; }   // 0.1.18: short effects never count (0.1.22: + 7; 0.1.23: + the personal aura / stance / cloak)''')
rep('''      if (o.kind == 3 || o.kind == 4 || o.kind == 7) continue;   // 0.1.18: Frost Wake / Running Blessing are not placed zones (0.1.22: + the star well)''',
    '''      if (o.kind == 3 || o.kind == 4 || o.kind == 7 || o.kind == 8 || o.kind == 9 || o.kind == 12) continue;   // 0.1.18: Frost Wake / Running Blessing are not placed zones (0.1.22: + the star well; 0.1.23: + aura / stance / cloak)''')
rep('''           "TREEC", "LASTUSE", "MIRROR", "LASTHOOK", "LASTKEY", "WARD", "DIRTYAT", "VANTOLD", "CLEANQ", "WARDP", "MIRFAIL", "HINTED"):''',
    '''           "TREEC", "LASTUSE", "MIRROR", "LASTHOOK", "LASTKEY", "WARD", "DIRTYAT", "VANTOLD", "CLEANQ", "WARDP", "MIRFAIL", "HINTED",
           # 0.1.23: UUID -> the running Flow aura / Still Water stance / cloak (AbilZone); UUID -> double[] the First Strike {until, bonus %,
           # Death Mark, Lethal Opener second-hit until}; UUID -> double[] God Killer {until, mult, back mult, air, echo %, haste s, haste %};
           # mob Ref -> long[] Awe {until, tier, distract until, total combo, flags 1 calm 2 serenity, caster msb, lsb, last refresh}; UUID ->
           # int[] {speed %} the speed effect on; mob Ref -> long[] Death Mark {until, msb, lsb}; mob Ref -> long[] Iron Fist {palms, msb, lsb};
           # mob Ref -> long[] poisoned {until, msb, lsb, stacks, weakened until}; UUID -> Long the last Slip Away; pkey -> long[] {rebirth n, at}
           "FLOWS", "STANCES", "CLOAKS", "STRIKE", "ARMED", "AWED", "SPD", "MARKS", "PALMS", "POISONED", "SLIPAT", "RBN"):''')

# ================================================================================================ Abil fields (seams, counters)
rep('''           "public static final String[] CLEANSE = %s;" % jarr(CLEANSE)):
    F(abil, _f)''', '''           "public static final String[] CLEANSE = %s;" % jarr(CLEANSE)):
    F(abil, _f)
# 0.1.23: the Monk + Assassin counters (the harness + /classadmin abil info) and seams
for _f in ("public static volatile java.util.function.Function MOB = null;",       # HARNESS SEAM ONLY (null = TargetUtil.getTargetEntity / the front cone): Ref -> Ref
           "public static volatile java.util.List LOST = null;",                    # HARNESS SEAM ONLY (null): every mob made to lose its target
           "public static volatile long COMBOS = 0L;", "public static volatile long COUNTERS = 0L;", "public static volatile long DEFLECTS = 0L;",
           "public static volatile long WAVES = 0L;", "public static volatile long STRIKES = 0L;", "public static volatile long GODKILLS = 0L;",
           "public static volatile long POISONS = 0L;", "public static volatile long DISTRACTS = 0L;", "public static volatile long PALMHITS = 0L;",
           "public static volatile String LAST_MONK = \\"\\";", "public static volatile String LAST_ASN = \\"\\";"):
    F(abil, _f)''')

# ================================================================================================ the existing late methods: tree + rebirth hooks
rep('''  boolean mage = "Mage".equals(c.cls);
  boolean priest = "Priest".equals(c.cls);
  if (!mage && !priest) return;
  double q = c.amt("T6", 5.0);''', '''  boolean mage = "Mage".equals(c.cls);
  boolean priest = "Priest".equals(c.cls);
  if (!mage && !priest) { treeApply2(c); return; }   // 0.1.23: Monk + Assassin
  double q = c.amt("T6", 5.0);''')
# ctxFor: the rebirth cap + effective level + the modifier levels past their top
rep('''  String id = @PKG@.AbilDefs.IDS[ai];
  c.lvl = alvl(numOf(p, "u." + id));
  c.base = lvlMult(c.lvl);
  if (@PKG@.AbilCfg.MODS_ON) {
    int[] eq = equipped(p, ai, c.lvl, modSlots(csv, ai));
    c.m0 = eq[0];
    c.m1 = eq[1];
    c.l0 = c.m0 < 0 ? 0 : @PKG@.AbilModDefs.modLevel(numOf(p, "m." + id + "." + @PKG@.AbilModDefs.MID[c.m0]));
    c.l1 = c.m1 < 0 ? 0 : @PKG@.AbilModDefs.modLevel(numOf(p, "m." + id + "." + @PKG@.AbilModDefs.MID[c.m1]));
  }''', '''  String id = @PKG@.AbilDefs.IDS[ai];
  int stored = alvlk(k, numOf(p, "u." + id));                 // 0.1.23: the cap abil.maxLevel + rebirths
  c.lvl = effLvl(u, k, ai, stored);                            // 0.1.23: the rebirth soft cap (spec 3.2)
  c.base = lvlMult(c.lvl);
  if (@PKG@.AbilCfg.MODS_ON) {
    int[] eq = equipped(p, ai, stored, modSlots(csv, ai));     // unlocked modifiers stay unlocked (Skyy 5b)
    c.m0 = eq[0];
    c.m1 = eq[1];
    c.l0 = c.m0 < 0 ? 0 : modEff(p, id, stored, c.lvl, mlvl(p, id, c.m0));
    c.l1 = c.m1 < 0 ? 0 : modEff(p, id, stored, c.lvl, mlvl(p, id, c.m1));
  }''')
rep('''  treeApply(c);
  c.main = c.base * pw * c.treeMain;
  return c;''', '''  treeApply(c);
  if (ai == @PKG@.AbilDefs.PALM) c.cdAdd = c.cdAdd - palmCut(c.lvl);   // 0.1.23: Palm Strike -0.1 s a level to its floor
  c.main = c.base * pw * c.treeMain;
  return c;''')
rep('''    if (j == 1 && r[0] == mi) {
      if (!@PKG@.AbilModDefs.MSTACK[mi]) continue;
      if (@PKG@.AbilModDefs.modLevel(numOf(p, "m." + id + "." + @PKG@.AbilModDefs.MID[mi])) < 2) continue;
    }''', '''    if (j == 1 && r[0] == mi) {
      if (!@PKG@.AbilModDefs.MSTACK[mi]) continue;
      if (mlvl(p, id, mi) < 2) continue;
    }''')
# used(): the cap + the modifier levels past their top
rep('''    java.util.Properties p = @PKG@.AbilStore.load(k);
    long uses = numOf(p, "u." + id);
    int l0 = alvl(uses);''', '''    java.util.Properties p = @PKG@.AbilStore.load(k);
    long uses = numOf(p, "u." + id);
    int l0 = alvlk(k, uses);''')
rep('''      int ml0 = @PKG@.AbilModDefs.modLevel(mu);
      int ml1 = @PKG@.AbilModDefs.modLevel(mu + (long) add);''', '''      int mx0 = (int) numOf(p, "rb.modmax." + id + "." + @PKG@.AbilModDefs.MID[mi]);   // 0.1.23
      int ml0 = @PKG@.AbilModDefs.modLevelX(mu, mx0);
      int ml1 = @PKG@.AbilModDefs.modLevelX(mu + (long) add, mx0);''')
rep('''    int l1 = alvl(uses + 1L);
    @PR@ pr = prOf(u);''', '''    int l1 = alvlk(k, uses + 1L);
    @PR@ pr = prOf(u);''')
# the panel: cap, effective level, modifier levels, the one-alt class
rep('''  o[5] = Boolean.valueOf(grant || (long) lv >= @PKG@.AbilDefs.unlock(3));''',
    '''  o[5] = Boolean.valueOf(@PKG@.AbilDefs.of(ci, 4) >= 0 && (grant || (long) lv >= @PKG@.AbilDefs.unlock(3)));   // 0.1.23: the Assassin has one alt''')
rep('''    long uses = ai < 0 ? 0L : numOf(p, "u." + id);
    int l = alvl(uses);
    int slots = modSlots(csv, ai);
    int[] eq = ai < 0 ? new int[] { -1, -1 } : equipped(p, ai, l, slots);''', '''    long uses = ai < 0 ? 0L : numOf(p, "u." + id);
    int l = alvlk(k, uses);
    int slots = modSlots(csv, ai);
    int[] eq = ai < 0 ? new int[] { -1, -1 } : equipped(p, ai, l, slots);
    int le = ai < 0 ? l : effLvl(u, k, ai, l);   // 0.1.23: the rebirth soft cap''')
rep('''    if (ai >= 0 && @PKG@.AbilCfg.LEVELS && (long) l < @PKG@.AbilCfg.MAX_LVL) nx = @PKG@.AbilMath.levelStart(l + 1, @PKG@.AbilCfg.USES_COEF, @PKG@.AbilCfg.USES_EXP) - uses;''',
    '''    if (ai >= 0 && @PKG@.AbilCfg.LEVELS && (long) l < capOf(k)) nx = @PKG@.AbilMath.levelStart(l + 1, @PKG@.AbilCfg.USES_COEF, @PKG@.AbilCfg.USES_EXP) - uses;''')
rep('''    o[b + 9] = levelText(ai, l, uses);
    o[b + 10] = eq[0] < 0 ? "" : @PKG@.AbilModDefs.MNAME[eq[0]];
    o[b + 11] = Integer.valueOf(eq[0] < 0 ? 0 : @PKG@.AbilModDefs.modLevel(numOf(p, "m." + id + "." + @PKG@.AbilModDefs.MID[eq[0]])));
    o[b + 12] = eq[1] < 0 ? "" : @PKG@.AbilModDefs.MNAME[eq[1]];
    o[b + 13] = Integer.valueOf(eq[1] < 0 ? 0 : @PKG@.AbilModDefs.modLevel(numOf(p, "m." + id + "." + @PKG@.AbilModDefs.MID[eq[1]])));''',
    '''    o[b + 9] = levelText(ai, l, uses) + (le < l ? " (works at Lv " + le + " until your class level is back)" : "");
    o[b + 10] = eq[0] < 0 ? "" : @PKG@.AbilModDefs.MNAME[eq[0]];
    o[b + 11] = Integer.valueOf(eq[0] < 0 ? 0 : mlvl(p, id, eq[0]));
    o[b + 12] = eq[1] < 0 ? "" : @PKG@.AbilModDefs.MNAME[eq[1]];
    o[b + 13] = Integer.valueOf(eq[1] < 0 ? 0 : mlvl(p, id, eq[1]));''')
# modRows: cap + the rebirth upgrades (head field 10 = upgrades to place; row field 12 = the modifier's extra levels)
rep('''  long uses = numOf(p, "u." + aid);
  int l = alvl(uses);
  int slots = modSlots(csv, ai);
  int[] eq = equipped(p, ai, l, slots);
  String[] st = eqOf(p, aid);''', '''  long uses = numOf(p, "u." + aid);
  int l = alvlk(k, uses);
  int slots = modSlots(csv, ai);
  int[] eq = equipped(p, ai, l, slots);
  String[] st = eqOf(p, aid);
  long picks = numOf(p, "rb.pick." + aid);   // 0.1.23: rebirth upgrades still to place''')
rep('''    + "|" + (eq[0] < 0 ? "" : @PKG@.AbilModDefs.MID[eq[0]]) + "|" + (eq[1] < 0 ? "" : @PKG@.AbilModDefs.MID[eq[1]]) + "|" + gainText(ai, l);''',
    '''    + "|" + (eq[0] < 0 ? "" : @PKG@.AbilModDefs.MID[eq[0]]) + "|" + (eq[1] < 0 ? "" : @PKG@.AbilModDefs.MID[eq[1]]) + "|" + gainText(ai, l) + "|" + picks;''')
rep('''    long mu = numOf(p, "m." + aid + "." + @PKG@.AbilModDefs.MID[mi]);
    int ml = @PKG@.AbilModDefs.modLevel(mu);''', '''    long mu = numOf(p, "m." + aid + "." + @PKG@.AbilModDefs.MID[mi]);
    int mxx = (int) numOf(p, "rb.modmax." + aid + "." + @PKG@.AbilModDefs.MID[mi]);   // 0.1.23
    int ml = @PKG@.AbilModDefs.modLevelX(mu, mxx);''')
rep('''    long nx = @PKG@.AbilModDefs.modNext(mu);
    String next = l < at ? modText(ai, mi, 1, 1) : (nx > 0L ? "Lv " + (ml + 1) + ": " + modText(ai, mi, ml + 1, 1) : "top level");''',
    '''    long nx = @PKG@.AbilModDefs.modNextX(mu, mxx);
    String next = l < at ? modText(ai, mi, 1, 1) : (nx > 0L ? "Lv " + (ml + 1) + ": " + modText(ai, mi, ml + 1, 1) : "top level");''')
rep('''      + "|" + cnt + "|" + (@PKG@.AbilModDefs.MSTACK[mi] ? "1" : "0") + "|" + now + "|" + next + "|" + (dbl ? "1" : "0");''',
    '''      + "|" + cnt + "|" + (@PKG@.AbilModDefs.MSTACK[mi] ? "1" : "0") + "|" + now + "|" + next + "|" + (dbl ? "1" : "0") + "|" + mxx;''')
# equipMod: the double rule with the extra levels, the cap
rep('''  String[] e = eqOf(p, aid);
  int l = alvl(numOf(p, "u." + aid));''', '''  String[] e = eqOf(p, aid);
  int l = alvlk(k, numOf(p, "u." + aid));''')
rep('''      if (@PKG@.AbilModDefs.modLevel(numOf(p, "m." + aid + "." + @PKG@.AbilModDefs.MID[mi])) < 2) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " can go in both slots from modifier Lv 2.";''',
    '''      if (mlvl(p, aid, mi) < 2) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " can go in both slots from modifier Lv 2.";''')
# doAction: + rbpick (place a rebirth upgrade)
rep('''  } else if (x.equals("unequip")) {
    int sl = -1;
    try { sl = Integer.parseInt(b.trim()); } catch (Throwable t) { sl = -1; }
    r = equipMod(u, a, sl, "", csv, false);
  }''', '''  } else if (x.equals("unequip")) {
    int sl = -1;
    try { sl = Integer.parseInt(b.trim()); } catch (Throwable t) { sl = -1; }
    r = equipMod(u, a, sl, "", csv, false);
  } else if (x.equals("rbpick")) {
    r = rbPick(u, a, b);   // 0.1.23: one rebirth upgrade -> that modifier may reach one more level
  }''')
# castAt0: the class message, the Palm Strike / Toxin / Vanishing Act pre-checks (before paying), the new executors
rep('''  if (!@PKG@.AbilDefs.classHas(ci) || !@PKG@.ClassDefs.ENABLED[ci]) { refuse(pr, @PKG@.ClassDefs.NAMES[ci] + " abilities are coming later - the Mage and the Priest get theirs first."); return "noabil"; }''',
    '''  if (!@PKG@.AbilDefs.classHas(ci) || !@PKG@.ClassDefs.ENABLED[ci]) { refuse(pr, @PKG@.ClassDefs.NAMES[ci] + " abilities come in a later update (the Mage, Priest, Monk and Assassin have theirs)."); return "noabil"; }''')
rep('''  if ((ai == @PKG@.AbilDefs.MANAB || ai == @PKG@.AbilDefs.BUBBLE) && sh == 0) {
    at = spot(st, ref, ai == @PKG@.AbilDefs.MANAB ? @PKG@.AbilCfg.B_RANGE : @PKG@.AbilCfg.U_RANGE);''', '''  if (ai == @PKG@.AbilDefs.TOXIN && (sh == 0 || sh == 1)) {   // 0.1.23: the vial lands where you look
    double tr = sh == 1 ? @PKG@.AbilCfg.TX_SP_RANGE : @PKG@.AbilCfg.TX_RANGE;
    at = aim(st, ref, tr);
    if (at == null) { refuse(pr, "Look at the ground within " + @PKG@.AbilMath.fmt(tr) + " blocks to throw the vial - nothing was spent."); return "aim"; }
  }
  @REF@ palmT = null;
  if (ai == @PKG@.AbilDefs.PALM) {   // 0.1.23: the enemy you look at - found before anything is paid
    double pr0 = @PKG@.AbilCfg.PS_REACH + (sh == 1 ? @PKG@.AbilCfg.PS_SP_STEP : 0.0);
    palmT = lookMob(st, ref, pr0);
    if (palmT == null) { refuse(pr, "No enemy in front of you within " + @PKG@.AbilMath.fmt(pr0) + " blocks - nothing was spent."); return "notarget"; }
  }
  if ((ai == @PKG@.AbilDefs.MANAB || ai == @PKG@.AbilDefs.BUBBLE) && sh == 0) {
    at = spot(st, ref, ai == @PKG@.AbilDefs.MANAB ? @PKG@.AbilCfg.B_RANGE : @PKG@.AbilCfg.U_RANGE);''')
rep('''    else if (ai == @PKG@.AbilDefs.GRACE) {
      if (sh == 3) { aw.add(chanJob(u, k, ai, at, @PKG@.AbilCfg.G_VOW_T, mana, stam, now)); extra = " vow"; }
      else extra = graceRun(pr, st, st, ref, u, sh, k);
    }''', '''    else if (ai == @PKG@.AbilDefs.GRACE) {
      if (sh == 3) { aw.add(chanJob(u, k, ai, at, @PKG@.AbilCfg.G_VOW_T, mana, stam, now)); extra = " vow"; }
      else extra = graceRun(pr, st, st, ref, u, sh, k);
    }
    // 0.1.23: MONK + ASSASSIN
    else if (ai == @PKG@.AbilDefs.FFORM || ai == @PKG@.AbilDefs.HFISTS) {
      if (sh == 2) { aw.add(landJob(u, k, ai, h, now)); extra = " land"; }
      else extra = flowAt(pr, st, ref, u, k, aw, ai, sh, h, now);
    }
    else if (ai == @PKG@.AbilDefs.STILLW) {
      if (sh == 2) { aw.add(landJob(u, k, ai, h, now)); extra = " land"; }
      else extra = stanceAt(pr, st, ref, u, k, aw, sh, h, now);
    }
    else if (ai == @PKG@.AbilDefs.PALM) extra = palmCast(pr, st, ref, u, k, aw, sh, h, palmT, now);
    else if (ai == @PKG@.AbilDefs.CYCLONE) {
      if (sh == 2) { aw.add(landJob(u, k, ai, h, now)); extra = " land"; }
      else extra = kickCast(st, ref, u, k, aw, sh, h, at, now);
    }
    else if (ai == @PKG@.AbilDefs.CLOAK) extra = cloakCast(pr, st, ref, u, k, aw, sh, now);
    else if (ai == @PKG@.AbilDefs.TOXIN) extra = toxinCast(pr, st, ref, u, k, aw, sh, h, at, now);
    else if (ai == @PKG@.AbilDefs.GODK) {
      if (sh == 3) { aw.add(armJob(u, k, at, mana, stam, now)); extra = " arming"; }
      else extra = gkArm(pr, st, ref, u, k, sh, now);
    }
    else if (ai == @PKG@.AbilDefs.VANISH) extra = vanishCast(pr, st, ref, u, k, aw, sh, now);''')
# the job + zone dispatch
rep('''  if (j.kind == 9) return burnTick(j, st, cb, now);
  if (j.kind == 10) return echoRun(j, st, cb, now);
  return false;''', '''  if (j.kind == 9) return burnTick(j, st, cb, now);
  if (j.kind == 10) return echoRun(j, st, cb, now);
  if (j.kind == 11) { palmRun(j, st, cb, now); return false; }      // 0.1.23
  if (j.kind == 12) { kickRun(j, st, cb, now); return false; }
  if (j.kind == 14) { gkEchoRun(j, st, cb, now); return false; }
  if (j.kind == 15) { armRun(j, st, cb, now); return false; }
  if (j.kind == 16) return poisonTick(j, st, cb, now);
  return false;''')
rep('''public static boolean zoneTick0(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind >= 3) return zoneTick2(z, st, cb, now);''', '''public static boolean zoneTick0(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind >= 8) return zoneTick3(z, st, cb, now);   // 0.1.23: aura, stance, cloud, smoke, cloak
  if (z.kind >= 3) return zoneTick2(z, st, cb, now);''')
# echoes of the new abilities
rep('''  if (j.ai == @PKG@.AbilDefs.GRACE) {
    LAST_ECHO = "grace:" + graceRun(pr, st, cb, cr, j.caster, j.sh, j.pkey);
    return false;
  }
  return false;''', '''  if (j.ai == @PKG@.AbilDefs.GRACE) {
    LAST_ECHO = "grace:" + graceRun(pr, st, cb, cr, j.caster, j.sh, j.pkey);
    return false;
  }
  if (j.ai == @PKG@.AbilDefs.HFISTS) { LAST_ECHO = "wave:" + wave(cb, cr, j.caster, j.x, j.y, j.z, j.r, j.amount, true); return false; }   // 0.1.23
  if (j.ai == @PKG@.AbilDefs.TOXIN) {
    if (aw != null) { cloudAt(cb, j.caster, j.pkey, aw, new double[] { j.x, j.y, j.z }, j.r, j.secs, j.amount, j.sh, now); if (pr != null) say(pr, "Echo: a weaker Toxin cloud."); }
    LAST_ECHO = "cloud";
    return false;
  }
  return false;''')
# modText: the new abilities / modifiers
rep('''  if (mi == @PKG@.AbilModDefs.ECHO) return "again at " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.ECHO_BASE + @PKG@.AbilCfg.ECHO_STEP * (double) l1) + " % after " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.ECHO_DELAY) + " s";
  return "";''', '''  if (mi == @PKG@.AbilModDefs.ECHO && ai == @PKG@.AbilDefs.STILLW) return "counters stay " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.SW_ECHO_T + 0.5 * (double) l1) + " s after the stance";   // 0.1.23 (Skyy L124)
  if (mi == @PKG@.AbilModDefs.ECHO) return "again at " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.ECHO_BASE + @PKG@.AbilCfg.ECHO_STEP * (double) l1) + " % after " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.ECHO_DELAY) + " s";
  if (mi == @PKG@.AbilModDefs.RICOCHET) return "stuns enemies within " + @PKG@.AbilMath.fmt(2.5 + 0.5 * (double) (e - 1)) + " blocks of the target too";
  if (mi == @PKG@.AbilModDefs.HASTE) {
    if (ai == @PKG@.AbilDefs.CLOAK) return "+" + @PKG@.AbilCfg.CL_HASTE + " % speed while cloaked";
    long hp = ai == @PKG@.AbilDefs.GODK ? @PKG@.AbilCfg.GK_HASTE : @PKG@.AbilCfg.CK_HASTE;
    return "+" + hp + " % speed for " + (3 + l1) + " s after";
  }
  return "";''')
rep('''  if (mi == @PKG@.AbilModDefs.CHAIN) return "+" + e + " targets, " + @PKG@.AbilMath.fmt(chainCut(e)) + " % less drop" + (e > 5 ? " (drop floor: the Lv 5 one)" : "");''',
    '''  if (mi == @PKG@.AbilModDefs.CHAIN && ai == @PKG@.AbilDefs.TOXIN) return "a dying poisoned enemy passes it on (" + (2 + e) + " s)";   // 0.1.23
  if (mi == @PKG@.AbilModDefs.CHAIN) return "+" + e + " targets, " + @PKG@.AbilMath.fmt(chainCut(e)) + " % less drop" + (e > 5 ? " (drop floor: the Lv 5 one)" : "");''')
rep('''  if (mi == @PKG@.AbilModDefs.SLOW) {
    if (ai == @PKG@.AbilDefs.BEAM) return "slows for " + @PKG@.AbilMath.fmt(1.0 + 0.5 * (double) (e - 1)) + " s";''', '''  if (mi == @PKG@.AbilModDefs.SLOW) {
    if (ai == @PKG@.AbilDefs.BEAM) return "slows for " + @PKG@.AbilMath.fmt(1.0 + 0.5 * (double) (e - 1)) + " s";
    if (ai == @PKG@.AbilDefs.VANISH) return "the smoke slows 50 %";                                  // 0.1.23
    if (ai == @PKG@.AbilDefs.PALM || ai == @PKG@.AbilDefs.CYCLONE) return "slowed for " + (1 + e) + " s";''')
rep('''  if (mi == @PKG@.AbilModDefs.KNOCK) return "bursts at the end, push " + @PKG@.AbilMath.fmt(8.0 + 2.0 * (double) (e - 1));''',
    '''  if (mi == @PKG@.AbilModDefs.KNOCK && ai != @PKG@.AbilDefs.MANAB) return "pushed " + (2 * e) + " blocks farther";   // 0.1.23
  if (mi == @PKG@.AbilModDefs.KNOCK) return "bursts at the end, push " + @PKG@.AbilMath.fmt(8.0 + 2.0 * (double) (e - 1));''')
rep('''    if (ai == @PKG@.AbilDefs.GRACE) return "overheal = shield up to " + w;''', '''    if (ai == @PKG@.AbilDefs.GRACE) return "overheal = shield up to " + w;
    if (ai == @PKG@.AbilDefs.STILLW) return "a shield of " + w + " in the stance";   // 0.1.23''')
# land(): the new mid-air shapes
rep('''  if (ai == @PKG@.AbilDefs.SANCT) { sanctAt(pr, cb, j.caster, j.pkey, aw, at, now, @PKG@.AbilCfg.Y_RADIUS, @PKG@.AbilCfg.Y_TIME, @PKG@.AbilCfg.Y_HEAL, @PKG@.AbilCfg.Y_CUT, 2); return "sanct"; }
  return "none";''', '''  if (ai == @PKG@.AbilDefs.SANCT) { sanctAt(pr, cb, j.caster, j.pkey, aw, at, now, @PKG@.AbilCfg.Y_RADIUS, @PKG@.AbilCfg.Y_TIME, @PKG@.AbilCfg.Y_HEAL, @PKG@.AbilCfg.Y_CUT, 2); return "sanct"; }
  if (ai == @PKG@.AbilDefs.FFORM || ai == @PKG@.AbilDefs.HFISTS) return "flow:" + flowAt(pr, cb, cr, j.caster, j.pkey, aw, ai, 2, j.amount, now);   // 0.1.23
  if (ai == @PKG@.AbilDefs.STILLW) {
    String sr = stanceAt(pr, cb, cr, j.caster, j.pkey, aw, 2, j.amount, now);
    int nb = burst(cb, cr, j.caster, at[0], at[1], at[2], @PKG@.AbilCfg.SW_AIR_R + cxr(), j.amount * @PKG@.AbilCfg.SW_AIR_P * cxm(), "StillWater");
    return "stance:" + sr + " landing=" + nb;
  }
  if (ai == @PKG@.AbilDefs.CYCLONE) return "kick:" + kickRun(kickJob(j.caster, j.pkey, at, 2, j.amount, now), st, cb, now);
  if (ai == @PKG@.AbilDefs.VANISH) { @PKG@.AbilZone sz = smokeAt(cb, j.caster, j.pkey, aw, at, @PKG@.AbilCfg.VA_AI_R + cxr(), 2, now); return sz == null ? "smoke:none" : "smoke:" + @PKG@.AbilMath.fmt(sz.r); }
  return "none";''')
# /cast list: the class message
rep('''  if (!@PKG@.AbilDefs.classHas(ci)) return new String[] { @PKG@.ClassDefs.NAMES[ci] + " abilities are coming later - the Mage and the Priest get theirs first." };''',
    '''  if (!@PKG@.AbilDefs.classHas(ci)) return new String[] { @PKG@.ClassDefs.NAMES[ci] + " abilities come in a later update (the Mage, Priest, Monk and Assassin have theirs)." };''')
rep('''    if (st.equals("ready") || st.equals("cooldown")) {
      @PKG@.AbilCtx c = ctxFor(u, k, ai, i >= 2 && @PKG@.AbilCfg.SHAPES ? 3 : 0, csv);''', '''    if (st.equals("ready") || st.equals("cooldown")) {
      @PKG@.AbilCtx c = ctxFor(u, k, ai, i >= 2 && @PKG@.AbilCfg.SHAPES ? 3 : 0, csv);   // c.lvl = the working level (0.1.23: rebirth soft cap)''')
rep('''    if (st.equals("passive")) tx = "passive - always on (a killing blow on you or your party near you leaves them at " + @PKG@.AbilCfg.GS_HP + " % Health) - " + levelText(ai, alvl(numOf(p, "u." + @PKG@.AbilDefs.IDS[ai])), numOf(p, "u." + @PKG@.AbilDefs.IDS[ai]));''',
    '''    if (st.equals("passive")) tx = "passive - always on (a killing blow on you or your party near you leaves them at " + @PKG@.AbilCfg.GS_HP + " % Health) - " + levelText(ai, alvlk(k, numOf(p, "u." + @PKG@.AbilDefs.IDS[ai])), numOf(p, "u." + @PKG@.AbilDefs.IDS[ai]));''')
rep('''  long uses = numOf(p, "u." + @PKG@.AbilDefs.IDS[ai]);
  return levelText(ai, alvl(uses), uses);''', '''  long uses = numOf(p, "u." + @PKG@.AbilDefs.IDS[ai]);
  return levelText(ai, alvlk(@PKG@.ClassCfg.pkey(u), uses), uses);''')
# setPick: a class with one alt
rep('''  if (oa < 0 || na < 0) return "Your class has no Ability 1 alt.";''',
    '''  if (oa >= 0 && na < 0) return @PKG@.ClassDefs.NAMES[ci] + "s have one Ability 1 alt: " + @PKG@.AbilDefs.NAMES[oa] + ".";   // 0.1.23
  if (oa < 0 || na < 0) return "Your class has no Ability 1 alt.";''')
# /classadmin abil info: the 0.1.23 counters
rep('''    send(pr, "Keys: hook " + (HOOK_ON ? "on" : "OFF (" + HOOK_WHY + ")") + ", " + HOOKS + " key presses, " + RUNES + " key casts, " + FALLBACKS + " marker casts (" + FB_DUP + " doubles skipped), " + MIRRORS + " slot fixes (last: " + LAST_MIRROR + "), " + CLEANED + " stray runes removed | uses " + USES + ", echoes " + ECHOES + " | tree read fails " + TREE_ERR + " | tree: " + treeCsv(t), null);''',
    '''    send(pr, "Keys: hook " + (HOOK_ON ? "on" : "OFF (" + HOOK_WHY + ")") + ", " + HOOKS + " key presses, " + RUNES + " key casts, " + FALLBACKS + " marker casts (" + FB_DUP + " doubles skipped), " + MIRRORS + " slot fixes (last: " + LAST_MIRROR + "), " + CLEANED + " stray runes removed | uses " + USES + ", echoes " + ECHOES + " | tree read fails " + TREE_ERR + " | tree: " + treeCsv(t), null);
    send(pr, "Monk / Assassin: combo hits " + COMBOS + ", counters " + COUNTERS + ", deflects " + DEFLECTS + ", waves " + WAVES + ", palms " + PALMHITS + ", first strikes " + STRIKES + ", God Killer hits " + GODKILLS + ", poison pulses " + POISONS + ", targets lost " + DISTRACTS + " | last: " + LAST_MONK + " / " + LAST_ASN + " | rebirth: " + rbLine(@PKG@.ClassCfg.pkey(t)), null);''')

# ================================================================================================ the hooks: DamageLock (outgoing), AbilShieldSys (incoming), AbilFrostSys (landed)
rep('''    if (bad == null) return;
    d.setAmount(0.0f);
    d.setCancelled(true);
    buf.tryRemoveComponent(chunk.getReferenceTo(idx), @KBC@.getComponentType());''', '''    if (bad == null) {
      // 0.1.23: First Strike, Death Mark, God Killer, Plague (a weapon hit of an Assassin) - outHook's body is set after Abil exists
      if (u != null) outHook(st, buf, chunk.getReferenceTo(idx), d, u);
      return;
    }
    d.setAmount(0.0f);
    d.setCancelled(true);
    buf.tryRemoveComponent(chunk.getReferenceTo(idx), @KBC@.getComponentType());''')
# DamageLock is compiled before AbilStore / Abil exist: a stub now, its body after the Abil late bodies (OUTHOOK below)
rep('''M(lock, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {''', '''M(lock, "public static void outHook(@ST@ st, @CB@ buf, @REF@ t, @DMG@ d, java.util.UUID u) { }")   # 0.1.23: OUTHOOK (body set later)
M(lock, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {''')
rep('''print("Abil: %d late bodies set" % len(ABIL_LATE))''', '''print("Abil: %d late bodies set" % len(ABIL_LATE))
# 0.1.23 OUTHOOK: DamageLock hands an armed Assassin's weapon hit to Abil.outHit - fast exit while nobody has one armed
_oh = [_m for _m in lock.getDeclaredMethods() if str(_m.getName()) == "outHook"]
assert len(_oh) == 1
_oh[0].setBody(jv("{ if ($5 != null && (!@PKG@.AbilStore.STRIKE.isEmpty() || !@PKG@.AbilStore.ARMED.isEmpty() || !@PKG@.AbilStore.MARKS.isEmpty() "
                  "|| !@PKG@.AbilStore.POISONED.isEmpty())) @PKG@.Abil.outHit($1, $2, $3, $4, $5, System.currentTimeMillis()); }"))''')
rep('''    if (!@PKG@.AbilStore.WARD.isEmpty()) @PKG@.Abil.wardHit(st, buf, r, (@DMG@) ev, now);   // 0.1.22: Ward (Mana Barrier / Grace / Spirit)''',
    '''    if (!@PKG@.AbilStore.STANCES.isEmpty() || !@PKG@.AbilStore.AWED.isEmpty() || !@PKG@.AbilStore.FLOWS.isEmpty()) @PKG@.Abil.inHit(st, buf, r, (@DMG@) ev, now);   // 0.1.23: Still Water, Awe, Iron Skin
    if (!@PKG@.AbilStore.WARD.isEmpty()) @PKG@.Abil.wardHit(st, buf, r, (@DMG@) ev, now);   // 0.1.22: Ward (Mana Barrier / Grace / Spirit)''')
rep('''    if (!(ev instanceof @DMG@) || chunk == null || @PKG@.AbilStore.FROZEN.isEmpty()) return;
    @PKG@.Abil.frostHit(buf, chunk.getReferenceTo(idx), (@DMG@) ev, System.currentTimeMillis());''',
    '''    if (!(ev instanceof @DMG@) || chunk == null) return;
    long now0 = System.currentTimeMillis();
    if (!@PKG@.AbilStore.FROZEN.isEmpty()) @PKG@.Abil.frostHit(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);
    // 0.1.23: combo stacks (Flowing Form / Hundred Fists), the cloak breaks, Slip Away, Toxin Chain - fast exit while none runs
    if (!@PKG@.AbilStore.FLOWS.isEmpty() || !@PKG@.AbilStore.CLOAKS.isEmpty() || !@PKG@.AbilStore.POISONED.isEmpty() || @PKG@.Abil.SLIP_ON)
      @PKG@.Abil.hitLanded(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);''')
rep('''    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ClassCfg.warn("Frost Nova: the freeze-break hook failed (logged once, freezes then run their full time): " + t); }''',
    '''    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ClassCfg.warn("Frost Nova / combo hook failed (logged once, freezes then run their full time): " + t); }''')

# ================================================================================================ ClassQuit: nothing per player kept
rep('''    @PKG@.AbilStore.dropKeysOf(@PKG@.AbilStore.HINTED, u);   // second fix round''',
    '''    @PKG@.AbilStore.dropKeysOf(@PKG@.AbilStore.HINTED, u);   // second fix round
    @PKG@.AbilStore.FLOWS.remove(u);     // 0.1.23: the aura / stance / cloak end at their next tick (the caster is gone)
    @PKG@.AbilStore.STANCES.remove(u);
    @PKG@.AbilStore.CLOAKS.remove(u);
    @PKG@.AbilStore.STRIKE.remove(u);
    @PKG@.AbilStore.ARMED.remove(u);
    @PKG@.AbilStore.SPD.remove(u);
    @PKG@.AbilStore.SLIPAT.remove(u);''')

# ================================================================================================ the plugin: the rebirth participant (bridge)
rep('''  b.put("tree:reads:SkyyClasses", "__READS__");             // 0.1.22: the class tree nodes SkyyClasses applies (reader contract)''',
    '''  b.put("tree:reads:SkyyClasses", "__READS__");             // 0.1.22: the class tree nodes SkyyClasses applies (reader contract)
  b.put("rebirth:part:classes", new @PKG@.ClassRb());        // 0.1.23: the rebirth participant (SkyyRebirth's two-phase commit)''')

# ================================================================================================ 0.1.23 Java: particles, pure rules, Abil fields
rep('''      "FX_HOLY": "Totem_Heal_Extra", "FX_BLESS": "Potion_Health_Heal", "FX_GUARD": "Potion_Health_Implosion"}''',
    '''      "FX_HOLY": "Totem_Heal_Extra", "FX_BLESS": "Potion_Health_Heal", "FX_GUARD": "Potion_Health_Implosion",
      # 0.1.23: Monk + Assassin (finite one-shots, checked below like the others)
      "FX_PALM": "Impact_Mace_Bash", "FX_KICK": "Impact_Sword_Signature_Spin", "FX_COUNTER": "Impact_Shield_Bash", "FX_FLOW": "Block_Land_Soft_Dust",
      "FX_TOXIN": "Impact_Poison", "FX_SMOKE": "Impact_Feathers_Black", "FX_GOD": "Impact_Critical"}''')
rep('''F(abil, "public static volatile String LAST_LAND = \\"\\";")   # the last landing outcome (harness + /classadmin abil info)''',
    '''F(abil, "public static volatile String LAST_LAND = \\"\\";")   # the last landing outcome (harness + /classadmin abil info)
F(abil, "public static volatile boolean SLIP_ON = false;")   # 0.1.23: an Assassin with Slip Away (PA4) has cast since the start
F(abil, "public static volatile long NEXT_PRUNE = 0L;")      # FIX (critic): the next mob-map prune (AbilTick, once a second)
F(abil, "public static volatile boolean FROST_ON = false;")  # FIX (critic): AbilFrostSys registered (Frost Nova + the Monk / Assassin landed-hit hook)''')
# the pure rules (bare-JVM tested): the rebirth soft cap, the live combo stacks, the backstab angle
rep('''# ---- AbilStore: loadout per profile (abilities/<pkey>.properties), memory cooldowns (pkey|ability), refusal throttle
abst = pool.makeClass(PKG + ".AbilStore")''', '''# ---- 0.1.23 REBIRTH (research/cloud/Rebirth-Spec.md 3.2): the working level while the class level climbs back
M(abmath, r"""
public static int rbEff(int lvl, int S, int L, int lr, int cap0) {
  if (S <= 0 || lr <= 0 || L >= lr) return lvl;
  int l = L < 0 ? 0 : L;
  int c0 = cap0 < 1 ? 1 : cap0;
  int f = 1 + (int) ((14L * (long) l) / (long) c0);
  if (f > 15) f = 15;
  int half = (S + 1) / 2;
  int e = half + (int) (((long) (S - half) * (long) l) / (long) lr);
  if (e < f) e = f;
  if (e > S) e = S;
  return lvl < e ? lvl : e;
}""")
M(abmath, r"""
public static int rbModEff(int ml, int eff, int S) {
  if (S <= 0 || eff >= S || ml <= 0) return ml;
  long v = ((long) ml * (long) eff + (long) S - 1L) / (long) S;
  if (v < 1L) v = 1L;
  return v < (long) ml ? (int) v : ml;
}""")
# 0.1.23: the combo stacks still alive (gained less than dec ms ago)
M(abmath, r"""
public static int live(long[] ring, long now, long dec) {
  if (ring == null) return 0;
  int n = 0;
  for (int i = 0; i < ring.length; i++) if (ring[i] > 0L && now - ring[i] < dec && now >= ring[i]) n++;
  return n;
}""")
# 0.1.23: the vanilla backstab rule (SkyyArmory TravMath.behind, verbatim rule): the way target -> attacker within maxDeg of the back (sin yaw, cos yaw)
M(abmath, r"""
public static boolean behind(double tx, double tz, double yaw, double ax, double az, double maxDeg) {
  double dx = ax - tx;
  double dz = az - tz;
  double l = Math.sqrt(dx * dx + dz * dz);
  if (!(l > 1.0E-6) || Double.isNaN(yaw)) return false;
  double c = (dx * Math.sin(yaw) + dz * Math.cos(yaw)) / l;
  if (c > 1.0) c = 1.0;
  if (c < -1.0) c = -1.0;
  return Math.toDegrees(Math.acos(c)) < maxDeg;
}""")
# 0.1.23: the Awe tier of a total combo (1 - 20)
M(abmath, r"""
public static int aweTier(int total, double per, double main) {
  int t = (int) Math.floor((double) total * per * (main > 0.0 ? main : 1.0));
  if (t < 1) t = 1;
  if (t > 20) t = 20;
  return t;
}""")
# 0.1.23: Hundred Fists - the waves earned by a total combo (the first at 'first', then every 'every')
M(abmath, r"""
public static int waves(int total, int first, int every) {
  if (every <= 0) return 0;
  int f = first > 0 ? first : every;
  if (total < f) return 0;
  return 1 + (total - f) / every;
}""")
# ---- AbilStore: loadout per profile (abilities/<pkey>.properties), memory cooldowns (pkey|ability), refusal throttle
abst = pool.makeClass(PKG + ".AbilStore")''')
# a fsync'd write (the rebirth commit: the abilities file with rb.lastTx in ONE atomic write)
rep('''# FIX ROUND (critic: a failed or never-run write was lost): the key leaves DIRTY before the write reads DATA, and comes back when it fails''',
    '''# FIX (critic: a Max Up between the commit's read and its write minted a modifier level): set + add counters in ONE synchronized
# read-modify-write; 1 = done, 0 = a counter would go below 0 (nothing changed), -1 = the file cannot be read
M(abst, r"""
public static synchronized int setAdd(String k, String[] keys, String[] vals, String[] ak, long[] ad) {
  java.util.Properties old = load(k);
  if (DATA.get(k) != old) return -1;
  long[] nv = new long[ak.length];
  for (int i = 0; i < ak.length; i++) {
    long v = 0L;
    try { v = Long.parseLong(old.getProperty(ak[i], "0").trim()); } catch (Throwable t) { v = 0L; }
    if (v < 0L) v = 0L;
    v = v + ad[i];
    if (v < 0L) return 0;
    nv[i] = v;
  }
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  for (int i = 0; i < keys.length && i < vals.length; i++) {
    if (vals[i] == null) p.remove(keys[i]);
    else p.setProperty(keys[i], vals[i]);
  }
  for (int i = 0; i < ak.length; i++) {
    if (nv[i] == 0L) p.remove(ak[i]);
    else p.setProperty(ak[i], String.valueOf(nv[i]));
  }
  DATA.put(k, p);
  return 1;
}""")
# 0.1.23: the rebirth commit's write - the same tmp + move, the tmp fsync'd first (a power cut never leaves a torn file holding rb.lastTx)
M(absave, r"""
public static synchronized boolean writeSync(String k) {
  java.util.Properties p = (java.util.Properties) @PKG@.AbilStore.DATA.get(k);
  java.nio.file.Path DIR = @PKG@.AbilStore.DIR;
  if (p == null || DIR == null) return false;
  boolean ok = false;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try { p.store(out, "SkyyClasses abilities (p1 p2 = primaries, a1 a2 = crouch alts, alt = A1-alt pick A or B, grant = admin grant)"); out.flush(); out.getFD().sync(); } finally { out.close(); }
    java.nio.file.Path dst = DIR.resolve(k + ".properties");
    int tries = 0;
    while (!ok) {
      try {
        try { java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
        catch (java.nio.file.AtomicMoveNotSupportedException am) { java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
        ok = true;
      } catch (java.nio.file.FileSystemException ade) {
        tries++;
        if (tries >= 5) throw ade;
        Thread.sleep(20L);
      }
    }
    @PKG@.AbilStore.SAVES = @PKG@.AbilStore.SAVES + 1L;
    @PKG@.AbilStore.DIRTY.remove(k);
    @PKG@.AbilStore.DIRTYAT.remove(k);
  } catch (Throwable t) { @PKG@.ClassCfg.warn("could not save ability file " + k + " (rebirth): " + t); }
  return ok;
}""")
# FIX ROUND (critic: a failed or never-run write was lost): the key leaves DIRTY before the write reads DATA, and comes back when it fails''')

NEW_LATE = []


def late(src):
    NEW_LATE.append(src.strip("\n"))


# ---------------------------------------------------------------- rebirth: the cap, the working level, modifier levels
late(r'''
public static int rbN(String k) {
  if (k == null) return 0;
  try {
    long now = System.currentTimeMillis();
    Object o = @PKG@.AbilStore.RBN.get(k);
    if (o instanceof long[] && now - ((long[]) o)[1] < 5000L && now >= ((long[]) o)[1]) return (int) ((long[]) o)[0];
    int n = 0;
    Object f = @PKG@.ClassCfg.bridge().get("rebirth:fn:count");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(k);
      if (r instanceof Number) n = ((Number) r).intValue();
      else if (o instanceof long[]) return (int) ((long[]) o)[0];
      else return 0;   // FIX (critic): no answer yet (SkyyRebirth still reading the profile) - never cached as a false 0
    }
    if (n < 0) n = 0;
    if (n > 1000) n = 1000;
    @PKG@.AbilStore.RBN.put(k, new long[] { (long) n, now });
    return n;
  } catch (Throwable t) { return 0; }
}''')
late(r'''
public static long capOf(String k) {
  return @PKG@.AbilCfg.MAX_LVL + (long) rbN(k);
}''')
late(r'''
public static int alvlk(String k, long uses) {
  if (!@PKG@.AbilCfg.LEVELS) return 1;
  long cap = capOf(k);
  return @PKG@.AbilMath.levelOf(uses, (int) (cap > 1000L ? 1000L : cap), @PKG@.AbilCfg.USES_COEF, @PKG@.AbilCfg.USES_EXP);
}''')
# FIX (critic): the class level, -1 when SkyySkills cannot answer (Abil.level answers 0 or the Ability 1 unlock then)
late(r'''
public static int levelOr(java.util.UUID u, int ci) {
  try {
    Object f = @PKG@.ClassCfg.bridge().get("skill:fn:level");
    if (!(f instanceof java.util.function.Function) || ci < 0) return -1;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, @PKG@.ClassDefs.SKILLS[ci] });
    if (r instanceof Number) {
      int l = ((Number) r).intValue();
      return l < 0 ? 0 : l;
    }
  } catch (Throwable t) { }
  return -1;
}''')
late(r'''
public static int effLvl(java.util.UUID u, String k, int ai, int lvl) {
  if (ai < 0 || k == null || u == null) return lvl;
  java.util.Properties p = @PKG@.AbilStore.load(k);
  long s0 = numOf(p, "rb.S." + @PKG@.AbilDefs.IDS[ai]);
  long lr = numOf(p, "rb.Lr");
  if (s0 <= 0L || lr <= 0L) return lvl;
  int cl = levelOr(u, @PKG@.AbilDefs.CLS[ai]);
  if (cl < 0) return lvl;   // FIX (critic): SkyySkills cannot answer (loading / missing) - no soft cap (as SkyyTrees' covered)
  return @PKG@.AbilMath.rbEff(lvl, (int) (s0 > 1000L ? 1000L : s0), cl, (int) (lr > 100000L ? 100000L : lr), (int) @PKG@.AbilCfg.RB_CAP0);
}''')
late(r'''
public static int mlvl(java.util.Properties p, String id, int mi) {
  if (mi < 0) return 0;
  String m = @PKG@.AbilModDefs.MID[mi];
  return @PKG@.AbilModDefs.modLevelX(numOf(p, "m." + id + "." + m), (int) numOf(p, "rb.modmax." + id + "." + m));
}''')
late(r'''
public static int modEff(java.util.Properties p, String id, int stored, int eff, int ml) {
  if (eff >= stored) return ml;
  return @PKG@.AbilMath.rbModEff(ml, eff, stored);
}''')
late(r'''
public static long palmCut(int lvl) {
  double room = @PKG@.AbilCfg.PS_CD - @PKG@.AbilCfg.PS_CD_FLOOR;
  if (!(room > 0.0) || lvl <= 1) return 0L;
  double cut = @PKG@.AbilCfg.PS_CD_LVL * (double) (lvl - 1);
  if (cut > room) cut = room;
  return Math.round(cut * 1000.0);
}''')
# FIX (critic): SkyyRebirth's rebirth:fn:busy (the profile is inside a rebirth); no SkyyRebirth / any error = false
late(r'''
public static boolean rbBusy(String k) {
  try {
    Object f = @PKG@.ClassCfg.bridge().get("rebirth:fn:busy");
    if (f instanceof java.util.function.Function) return Boolean.TRUE.equals(((java.util.function.Function) f).apply(k));
  } catch (Throwable t) { }
  return false;
}''')
late(r'''
public static String rbPick(java.util.UUID u, String id, String mod) {
  int ci = @PKG@.ClassStore.classIndex(u);
  int ai = @PKG@.AbilDefs.find(id);
  if (u == null || ai < 0 || @PKG@.AbilDefs.CLS[ai] != ci) return "-That is not one of your abilities.";
  int mi = @PKG@.AbilModDefs.find(mod);
  if (mi < 0 || @PKG@.AbilModDefs.pos(ai, mi) < 0) return "-" + (mod == null ? "?" : mod) + " is not a " + @PKG@.AbilDefs.NAMES[ai] + " modifier.";
  if (combatMs(u) > 0L) return "-Leave combat first.";
  String k = @PKG@.ClassCfg.pkey(u);
  if (rbBusy(k)) return "-A rebirth is running on this profile - try again in a moment.";   // FIX (critic): never between the commit's steps
  String aid = @PKG@.AbilDefs.IDS[ai];
  int at = @PKG@.AbilModDefs.unlockAt(@PKG@.AbilModDefs.pos(ai, mi));   // FIX 2 (critic): never on a locked modifier (the modRows rule)
  if (alvlk(k, numOf(@PKG@.AbilStore.load(k), "u." + aid)) < at) return "-That modifier is still locked - it unlocks at " + @PKG@.AbilDefs.NAMES[ai] + " Lv " + at + ".";
  String mk = "rb.modmax." + aid + "." + @PKG@.AbilModDefs.MID[mi];
  int ok = @PKG@.AbilStore.setAdd(k, new String[0], new String[0], new String[] { "rb.pick." + aid, mk }, new long[] { -1L, 1L });   // FIX: one locked step
  if (ok < 0) return "-Your ability file could not be read - nothing changed (see the server log).";
  if (ok == 0) return "-No rebirth upgrade to place on " + @PKG@.AbilDefs.NAMES[ai] + " (one per rebirth per ability).";
  long now1 = numOf(@PKG@.AbilStore.load(k), mk);
  @PKG@.AbilStore.saveSoon(k);
  return "+" + @PKG@.AbilModDefs.MNAME[mi] + " of " + @PKG@.AbilDefs.NAMES[ai] + " can now reach modifier Lv " + (@PKG@.AbilModDefs.steps().length + 1 + (int) now1) + " (it still levels by use).";
}''')
late(r'''
public static String rbLine(String k) {
  if (k == null) return "";
  java.util.Properties p = @PKG@.AbilStore.load(k);
  String tx = p.getProperty("rb.lastTx", "");
  return "n=" + rbN(k) + " cap=" + capOf(k) + (tx.length() > 0 ? " lastTx=" + tx + " Lr=" + numOf(p, "rb.Lr") : "");
}''')
# ---------------------------------------------------------------- the class tree, Monk + Assassin (Class-Tree-Paths.md 6 / 7)
late(r'''
public static void treeApply2(@PKG@.AbilCtx c) {
  if (c == null || c.ai < 0) return;
  int ai = c.ai;
  boolean monk = "Monk".equals(c.cls);
  boolean asn = "Assassin".equals(c.cls);
  if (!monk && !asn) return;
  double q = c.amt("T6", 5.0);
  if (q > 0.0) c.cdMult = c.cdMult * (1.0 - (q > 90.0 ? 90.0 : q) / 100.0);
  if (monk) {
    if (ai == @PKG@.AbilDefs.PALM && c.node("PB3")) c.costAdd = c.costAdd + 3.0;
    if (ai == @PKG@.AbilDefs.PALM && c.node("PB5")) c.cdAdd = c.cdAdd + 1000L;
    if ((ai == @PKG@.AbilDefs.FFORM || ai == @PKG@.AbilDefs.HFISTS) && c.node("PC3")) c.costAdd = c.costAdd + 2.0;
    if (ai == @PKG@.AbilDefs.STILLW && c.node("PC2")) c.durAdd = c.durAdd - 2.0;
  }
  if (asn) {
    if (c.node("PA4")) SLIP_ON = true;
    if (ai == @PKG@.AbilDefs.CLOAK && c.node("PA1")) { c.durAdd = c.durAdd + 2.0; c.cdAdd = c.cdAdd + 4000L; }
    if (ai == @PKG@.AbilDefs.CLOAK && c.node("PA4")) c.costAdd = c.costAdd + 4.0;
    if (ai == @PKG@.AbilDefs.GODK && c.node("PA3")) c.cdAdd = c.cdAdd + 10000L;
    if (ai == @PKG@.AbilDefs.TOXIN) {
      if (c.node("PB1")) c.radTree = c.radTree - 1.0;
      if (c.node("PB2")) c.durAdd = c.durAdd - 1.0;
      if (c.node("PB3")) c.treeMain = c.treeMain * 0.85;
      if (c.node("PB5")) c.cdAdd = c.cdAdd + 6000L;
    }
  }
}''')
# ---------------------------------------------------------------- speed, Awe, losing a target, the boss stun clock
late(r'''
public static String spdId(int pct) {
  int p = pct < -30 ? -30 : (pct > 80 ? 80 : pct);
  return "SkyyAbility_Spd_" + (p + 30);
}''')
late(r'''
public static boolean speedSet(@CAC@ acc, @REF@ r, java.util.UUID u, int pct0, double secs) {
  if (u == null || r == null) return false;
  int cap = (int) @PKG@.AbilCfg.SPEED_CAP;
  int pct = pct0 > cap ? cap : pct0;
  if (pct < -30) pct = -30;
  Object o = @PKG@.AbilStore.SPD.get(u);
  long[] s = null;
  if (o instanceof long[]) s = (long[]) o;
  int old = s == null ? 0 : (int) s[0];
  if (pct == 0) {
    if (old != 0) unfreezeOne(acc, r, spdId(old));
    if (s != null) { s[0] = 0L; if (s.length > 3) s[3] = 0L; }
    return true;
  }
  if (old != 0 && old != pct) unfreezeOne(acc, r, spdId(old));
  if (s == null || s.length < 4) {   // FIX (critic): [3] = until when the applied effect runs (speedKeep refreshes only near its end)
    long[] s2 = new long[4];
    if (s != null) { s2[0] = s[0]; s2[1] = s[1]; s2[2] = s[2]; }
    s = s2;
    @PKG@.AbilStore.SPD.put(u, s);
  }
  s[0] = (long) pct;
  boolean ok = effect(acc, r, spdId(pct), secs);
  s[3] = ok ? System.currentTimeMillis() + Math.round(secs * 1000.0) : 0L;
  return ok;
}''')
# FIX (critic: every zone tick re-added the speed effect = a client packet 4x a second): the tick callers (the aura, a hasted cloak) keep the
# same speed without a new effect while more than 0.5 s of it is left
late(r'''
public static boolean speedKeep(@CAC@ acc, @REF@ r, java.util.UUID u, int pct, double secs) {
  Object o = @PKG@.AbilStore.SPD.get(u);
  if (pct != 0 && o instanceof long[] && ((long[]) o).length > 3 && ((long[]) o)[0] == (long) pct && ((long[]) o)[3] - System.currentTimeMillis() > 500L) return true;
  return speedSet(acc, r, u, pct, secs);
}''')
# FIX (critic: one speed slot for every source - an ending aura / stance / cloak wiped a running Haste): a clear falls back to a live haste
late(r'''
public static boolean speedClear(@CAC@ acc, @REF@ r, java.util.UUID u) {
  Object o = @PKG@.AbilStore.SPD.get(u);
  long now = System.currentTimeMillis();
  if (o instanceof long[] && ((long[]) o)[1] > now && ((long[]) o)[2] > 0L) {
    long[] s = (long[]) o;
    return speedSet(acc, r, u, (int) s[2], (double) (s[1] - now) / 1000.0);
  }
  return speedSet(acc, r, u, 0, 0.0);
}''')
late(r'''
public static boolean haste(@CAC@ acc, @REF@ r, java.util.UUID u, int pct, double secs) {
  if (u == null || !(secs > 0.0) || pct <= 0) return false;
  long now = System.currentTimeMillis();
  Object o = @PKG@.AbilStore.SPD.get(u);
  long[] s = o instanceof long[] ? (long[]) o : new long[4];
  s[1] = now + Math.round(secs * 1000.0);
  s[2] = (long) pct;
  @PKG@.AbilStore.SPD.put(u, s);
  return speedSet(acc, r, u, pct, secs);
}''')
late(r'''
public static void speedFlow(@CAC@ acc, @REF@ r, java.util.UUID u, int pct, long now) {
  Object o = @PKG@.AbilStore.SPD.get(u);
  int hp = 0;
  if (o instanceof long[] && ((long[]) o)[1] > now) hp = (int) ((long[]) o)[2];
  speedKeep(acc, r, u, pct > hp ? pct : hp, 1.5);   // FIX: no new effect every tick
}''')
late(r'''
public static String aweId(int tier) {
  return "SkyyAbility_Awe_" + (tier < 1 ? 1 : (tier > 20 ? 20 : tier));
}''')
late(r'''
public static int distract(@CAC@ acc, @REF@ t, @REF@ who) {
  java.util.List l = LOST;
  if (l != null) { l.add(t); DISTRACTS = DISTRACTS + 1L; return 1; }
  try {
    if (t == null || who == null || !t.isValid()) return 0;
    Object o = acc.getComponent(t, @MES@.getComponentType());
    if (!(o instanceof @MES@)) return 0;
    @MES@ m = (@MES@) o;
    int n = 0;
    int c = m.getMarkedEntitySlotCount();
    for (int i = 0; i < c; i++) {
      @REF@ x = m.getMarkedEntityRef(i);
      if (x != null && x.equals(who)) { m.clearMarkedEntity(i); n++; }
    }
    if (n > 0) DISTRACTS = DISTRACTS + 1L;
    return n;
  } catch (Throwable e) { return 0; }
}''')
late(r'''
public static void pruneMap(java.util.concurrent.ConcurrentHashMap m, long now) {
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    Object v = m.get(k);
    if (!(v instanceof long[]) || ((long[]) v)[0] <= now) it.remove();
  }
}''')
# FIX (critic: mob-keyed maps were pruned only past 512 entries - AWED stayed non-empty, refs pinned): pruned every second from AbilTick
late(r'''
public static void pruneIdx(java.util.concurrent.ConcurrentHashMap m, long now, int ix) {
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    Object v = m.get(k);
    boolean dead = false;
    try { dead = (k instanceof @REF@) && !((@REF@) k).isValid(); } catch (Throwable t) { dead = false; }
    if (dead || !(v instanceof long[]) || ((long[]) v).length <= ix || ((long[]) v)[ix] <= now) it.remove();
  }
}''')
late(r'''
public static void pruneMobs(long now) {
  NEXT_PRUNE = now + 1000L;
  if (!@PKG@.AbilStore.AWED.isEmpty()) pruneIdx(@PKG@.AbilStore.AWED, now, 0);
  if (!@PKG@.AbilStore.POISONED.isEmpty()) pruneIdx(@PKG@.AbilStore.POISONED, now, 4);
  if (!@PKG@.AbilStore.MARKS.isEmpty()) pruneIdx(@PKG@.AbilStore.MARKS, now, 0);
  if (!@PKG@.AbilStore.PALMS.isEmpty()) pruneIdx(@PKG@.AbilStore.PALMS, now, 3);
}''')
late(r'''
public static int aweOn(@CAC@ acc, @REF@ t, @REF@ cr, java.util.UUID u, int total, @PKG@.AbilCtx c, long now) {
  if (t == null || u == null) return 0;
  int tier = @PKG@.AbilMath.aweTier(total, @PKG@.AbilCfg.FF_ADEF, c == null ? 1.0 : c.main);
  boolean calm = c != null && "Monk".equals(c.cls) && c.node("PC1");
  boolean seren = c != null && "Monk".equals(c.cls) && c.node("PC5");
  long linger = Math.round(@PKG@.AbilCfg.FF_ALINGER * 1000.0);
  Object o = @PKG@.AbilStore.AWED.get(t);
  long[] a = null;
  if (o instanceof long[]) a = (long[]) o;
  boolean fresh = a == null || a[0] <= now;
  if (fresh) {
    a = new long[8];
    a[2] = now + Math.round(@PKG@.AbilCfg.FF_DISTRACT * (seren ? 2.0 : 1.0) * 1000.0);
    distract(acc, t, cr);
  } else if (a[1] != (long) tier && a[1] > 0L) unfreezeOne(acc, t, aweId((int) a[1]));
  if (fresh || a[1] != (long) tier || now - a[7] >= 2000L) { effect(acc, t, aweId(tier), (double) linger / 1000.0); a[7] = now; }
  a[0] = now + linger;
  a[1] = (long) tier;
  if ((long) total > a[3]) a[3] = (long) total;
  a[4] = (calm ? 1L : 0L) + (seren ? 2L : 0L);
  a[5] = u.getMostSignificantBits();
  a[6] = u.getLeastSignificantBits();
  @PKG@.AbilStore.AWED.put(t, a);
  if (@PKG@.AbilStore.AWED.size() > 512) pruneMap(@PKG@.AbilStore.AWED, now);
  return fresh ? 1 : 0;
}''')
late(r'''
public static int stunMob(@CAC@ acc, @REF@ t, java.util.UUID u, double secs, long now) {
  if (!(secs > 0.0) || t == null) return -1;
  long hold = Math.round(secs * 1000.0);
  long c = stunClock(t, u, roleOf(acc, t), hold);
  if (c == 0L) { effect(acc, t, EF_SLOW, secs); return 0; }
  if (c > 0L && c < hold) hold = c;
  return effect(acc, t, EF_STUN, (double) hold / 1000.0) ? 1 : -1;
}''')
late(r'''
public static @REF@ lookMob(@CAC@ acc, @REF@ ref, double range) {
  try {
    java.util.function.Function f = MOB;
    if (f != null) {
      Object o = f.apply(ref);
      return o instanceof @REF@ ? (@REF@) o : null;
    }
    @REF@ t = null;
    try { t = @TU@.getTargetEntity(ref, (float) range, acc); } catch (Throwable x0) { t = null; }
    if (t != null && t.isValid() && enemy(acc, t, ref)) return t;
    double[] lk = look(acc, ref);
    @VEC@ p = pos(acc, ref);
    if (lk == null || p == null) return null;
    double hl = Math.sqrt(lk[3] * lk[3] + lk[5] * lk[5]);
    if (!(hl > 1.0E-4)) return null;
    java.util.List l = near(acc, p.x, p.y, p.z, range);
    @REF@ best = null;
    double bd = 1.0E18;
    for (int i = 0; i < l.size(); i++) {
      Object o = l.get(i);
      if (!(o instanceof @REF@)) continue;
      @REF@ c = (@REF@) o;
      if (!enemy(acc, c, ref)) continue;
      @VEC@ q = pos(acc, c);
      if (q == null) continue;
      double dx = q.x - p.x;
      double dz = q.z - p.z;
      double d = Math.sqrt(dx * dx + dz * dz);
      if (d > 0.3 && (dx * lk[3] + dz * lk[5]) / (d * hl) < 0.5) continue;
      if (d < bd) { bd = d; best = c; }
    }
    return best;
  } catch (Throwable x) { return null; }
}''')
late(r'''
public static boolean facing(@CAC@ acc, @REF@ r, @REF@ att, double deg) {
  if (deg >= 180.0) return true;
  if (att == null || !att.isValid()) return false;
  double[] lk = look(acc, r);
  @VEC@ p = pos(acc, r);
  @VEC@ q = pos(acc, att);
  if (lk == null || p == null || q == null) return false;
  double dx = q.x - p.x;
  double dz = q.z - p.z;
  double d = Math.sqrt(dx * dx + dz * dz);
  double hl = Math.sqrt(lk[3] * lk[3] + lk[5] * lk[5]);
  if (!(d > 1.0E-4) || !(hl > 1.0E-4)) return true;
  double c = (dx * lk[3] + dz * lk[5]) / (d * hl);
  if (c > 1.0) c = 1.0;
  if (c < -1.0) c = -1.0;
  return Math.toDegrees(Math.acos(c)) <= deg;
}''')
late(r'''
public static boolean behindHit(@CAC@ acc, @REF@ t, @REF@ att) {
  try {
    @TC@ tc = (@TC@) acc.getComponent(t, @TC@.getComponentType());
    @VEC@ a = pos(acc, att);
    if (tc == null || a == null) return false;
    @VEC@ q = tc.getPosition();
    return @PKG@.AbilMath.behind(q.x, q.z, (double) tc.getRotation().yaw(), a.x, a.z, @PKG@.AbilCfg.GK_ANGLE);
  } catch (Throwable x) { return false; }
}''')
late(r'''
public static boolean bossFor(@CAC@ acc, @REF@ t, boolean elite) {
  String role = roleOf(acc, t);
  if (@PKG@.AbilMath.bossRole(role, @PKG@.AbilCfg.BOSS_WORDS)) return true;
  return elite && @PKG@.AbilMath.bossRole(role, @PKG@.AbilCfg.GK_ELITE);
}''')
# ---------------------------------------------------------------- FLOWING FORM / HUNDRED FISTS (zone kind 8)
late(r'''
public static String flowAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int ai, int sh, double h, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  Object old = @PKG@.AbilStore.FLOWS.get(u);
  if (old instanceof @PKG@.AbilZone) { ((@PKG@.AbilZone) old).ended = true; ((@PKG@.AbilZone) old).why = "replaced"; }
  boolean hf = ai == @PKG@.AbilDefs.HFISTS;
  double r = (sh == 3 ? @PKG@.AbilCfg.FF_CR_R : @PKG@.AbilCfg.FF_RADIUS) + cxr() - (hf && sh == 3 ? 1.0 : 0.0);
  if (r < 1.0) r = 1.0;
  long life = Math.round(cxds(@PKG@.AbilCfg.FF_TIME) * 1000.0);
  double[] me = here(acc, ref);
  @PKG@.AbilZone z = new @PKG@.AbilZone(8, u, me == null ? 0.0 : me[0], me == null ? 0.0 : me[1], me == null ? 0.0 : me[2], r, now, now + life);
  z.pkey = k;
  z.ai = ai;
  z.shape = sh;
  z.follow = true;
  z.h = h;
  z.name = @PKG@.AbilDefs.sname(ai, sh);
  double eff = c == null ? 1.0 : (c.costMult > 1.0 ? 1.0 : c.costMult);
  double dr = sh == 3 ? 1.0 - (double) @PKG@.AbilCfg.FF_CR_D / 100.0 : 1.0;
  z.amount = (hf ? @PKG@.AbilCfg.HF_DM : @PKG@.AbilCfg.FF_DM) * eff * dr;
  z.freeze = (hf ? @PKG@.AbilCfg.HF_DS : @PKG@.AbilCfg.FF_DS) * eff * dr;
  int mx = (int) @PKG@.AbilCfg.FF_MAX;
  if (c != null && "Monk".equals(c.cls) && c.node("PC5") && mx > 18) mx = 18;
  if (mx < 1) mx = 1;
  z.ring = new long[mx];
  int st0 = sh == 1 ? (int) @PKG@.AbilCfg.FF_SP_ST : (sh == 3 ? (int) @PKG@.AbilCfg.FF_CR_ST : 0);
  if (hf && sh == 2) st0 = 1;
  for (int i = 0; i < st0 && i < mx; i++) z.ring[i] = now;
  z.total = st0;
  z.t1 = now;
  z.t2 = sh == 1 ? now + Math.round(@PKG@.AbilCfg.FF_SP_FREE * 1000.0) : 0L;
  z.n1 = hf ? (int) (sh == 3 ? @PKG@.AbilCfg.HF_CR_EVERY : @PKG@.AbilCfg.HF_EVERY) : 0;
  z.d1 = hf && sh == 1 ? (double) @PKG@.AbilCfg.HF_SP_EVERY : 0.0;
  z.n2 = hf ? @PKG@.AbilMath.waves(z.total, (int) z.d1, z.n1) : 0;
  z.hits = 0;
  z.d2 = hf ? h * (sh == 3 ? @PKG@.AbilCfg.HF_CR_POWER : @PKG@.AbilCfg.HF_POWER) * cxm() : 0.0;
  z.nextHeal = 0L;
  z.hit = new java.util.HashSet();
  aw.addZone(z);
  @PKG@.AbilStore.FLOWS.put(u, z);
  particle(FX_FLOW, z.x, z.y + 0.1, z.z, acc);
  if (pr != null) say(pr, z.name + ": " + @PKG@.AbilMath.fmt((double) life / 1000.0) + " s, aura " + @PKG@.AbilMath.fmt(r) + " blocks - every hit builds your combo" + (hf ? ", every " + z.n1 + "th hit a shockwave." : "."));
  LAST_MONK = "flow " + z.name + " r=" + @PKG@.AbilMath.fmt(r) + " stacks=" + st0;
  return " r=" + @PKG@.AbilMath.fmt(r) + " life=" + life + " drain=" + @PKG@.AbilMath.fmt(z.amount) + "/" + @PKG@.AbilMath.fmt(z.freeze) + " stacks=" + st0 + (hf ? " every=" + z.n1 + " wave=" + @PKG@.AbilMath.fmt(z.d2) : "");
}''')
late(r'''
public static int stacks(@PKG@.AbilZone z, long now) {
  if (z == null || z.ring == null) return 0;
  long dec = Math.round(@PKG@.AbilCfg.FF_DECAY * 1000.0);
  if (z.cx != null && "Monk".equals(z.cx.cls)) {
    if (z.cx.node("PC3")) dec = 7500L;
    else if (z.cx.node("PA4")) dec = 4000L;
  }
  return @PKG@.AbilMath.live(z.ring, now, dec);
}''')
late(r'''
public static int flowHit(@PKG@.AbilZone z, @CAC@ acc, @REF@ att, long now) {
  if (z == null || z.ended || now >= z.until || z.ring == null || z.ring.length == 0) return 0;
  int add = 1;
  if (z.cx != null && "Monk".equals(z.cx.cls) && z.cx.node("PA4") && att != null && !onGround(acc, att)) add = 2;
  for (int k = 0; k < add; k++) {
    int o = 0;
    for (int i = 1; i < z.ring.length; i++) if (z.ring[i] < z.ring[o]) o = i;
    z.ring[o] = now;
  }
  z.total = z.total + add;
  COMBOS = COMBOS + (long) add;
  if (z.n1 > 0) {
    int w = @PKG@.AbilMath.waves(z.total, (int) z.d1, z.n1);
    if (w > z.n2) z.n2 = w;
  }
  return add;
}''')
late(r'''
public static int wave(@CB@ cb, @REF@ cr, java.util.UUID u, double x, double y, double z, double r, double amount, boolean echo) {
  if (cr == null || !cr.isValid() || !(amount > 0.0) || u == null) return 0;
  java.util.List l = near(cb, x, y, z, r + 1.0);
  java.util.HashSet seen = new java.util.HashSet();
  long now = System.currentTimeMillis();
  long ms = u.getMostSignificantBits();
  long ls = u.getLeastSignificantBits();
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    Object ao = @PKG@.AbilStore.AWED.get(t);
    if (!(ao instanceof long[])) continue;
    long[] a = (long[]) ao;
    if (a[0] <= now || a[5] != ms || a[6] != ls) continue;
    if (hit(cb, t, cr, u, amount, "HundredFists")) n++;
  }
  particle(FX_KICK, x, y + 0.5, z, cb);
  return n;
}''')
late(r'''
public static void flowEnd(@PKG@.AbilZone z, @CAC@ acc, @REF@ cr) {
  z.ended = true;
  Object fo = @PKG@.AbilStore.FLOWS.get(z.caster);
  if (cr != null && cr.isValid() && (fo == z || fo == null)) speedClear(acc, cr, z.caster);   // FIX: not a newer aura's speed; a haste stays
  if (fo == z) @PKG@.AbilStore.FLOWS.remove(z.caster);
  @PR@ pr = prOf(z.caster);
  String why = "mana".equals(z.why) ? " - out of Mana" : ("stamina".equals(z.why) ? " - out of Stamina" : ("replaced".equals(z.why) ? " - replaced" : ""));
  if (pr != null && !"left".equals(z.why)) say(pr, (z.name == null ? "Flowing Form" : z.name) + " ended" + why + " - " + z.total + " combo" + (z.n1 > 0 ? ", " + z.hits + (z.hits == 1 ? " shockwave." : " shockwaves.") : "."));
  LAST_MONK = "flow end " + z.why + " combo=" + z.total + " waves=" + z.hits;
}''')
late(r'''
public static boolean flowTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  boolean ok = live(cb, cr, z.caster, z.pkey);
  if (!ok) z.why = "left";
  if (ok && !z.ended && now < z.until) {
    zoneFollow(z, cb);
    boolean free = @PKG@.AbilCfg.CREATIVE_FREE && creative(cb, cr);
    long dt = now - z.t1;
    if (dt < 0L) dt = 0L;
    z.t1 = now;
    if (!free && dt > 0L) {
      @ESM@ m = map(cb, cr);
      double mana = cur(m, @DST@.getMana());
      double stam = cur(m, @DST@.getStamina());
      double dm = z.amount * (double) dt / 1000.0;
      double ds = now < z.t2 ? 0.0 : z.freeze * (double) dt / 1000.0;
      if (mana >= 0.0 && dm > 0.0) { if (mana < dm) { z.ended = true; z.why = "mana"; } else m.subtractStatValue(@DST@.getMana(), (float) dm); }
      if (!z.ended && stam >= 0.0 && ds > 0.0) { if (stam < ds) { z.ended = true; z.why = "stamina"; } else m.subtractStatValue(@DST@.getStamina(), (float) ds); }
    }
  }
  if (!ok || z.ended || now >= z.until) {
    if (z.why == null || z.why.length() == 0) z.why = "time";
    flowEnd(z, cb, cr);
    return false;
  }
  int stk = stacks(z, now);
  boolean monk = z.cx != null && "Monk".equals(z.cx.cls);
  double per = monk && z.cx.node("PC1") ? 1.5 : @PKG@.AbilCfg.FF_MOVE;
  double mul = z.cx == null ? 1.0 : z.cx.main;
  int pct = (int) Math.round((double) stk * per * mul) - (monk && z.cx.node("PB4") ? 5 : 0);
  speedFlow(cb, cr, z.caster, pct, now);
  java.util.List l = near(cb, z.x, z.y, z.z, z.r);
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    aweOn(cb, t, cr, z.caster, z.total, z.cx, now);
    z.hit.add(t);
  }
  java.util.Iterator it = z.hit.iterator();
  while (it.hasNext()) {
    @REF@ t = (@REF@) it.next();
    Object ao = @PKG@.AbilStore.AWED.get(t);
    if (t == null || !t.isValid() || !(ao instanceof long[]) || ((long[]) ao)[0] <= now) { it.remove(); continue; }
    if (now < ((long[]) ao)[2]) distract(cb, t, cr);
  }
  if (z.n1 > 0 && z.n2 > z.hits && now >= z.nextHeal) {
    z.hits = z.hits + 1;
    z.nextHeal = now + Math.round(@PKG@.AbilCfg.HF_GAP * 1000.0);
    int n = wave(cb, cr, z.caster, z.x, z.y, z.z, z.r, z.d2, false);
    WAVES = WAVES + 1L;
    if (z.cx != null && z.cx.echoPct > 0.0 && !z.cx.echo) {
      @PKG@.AbilCtx e = z.cx.echoOf(z.cx.echoPct);
      double ea = z.cx.main > 0.0 ? z.d2 * e.main / z.cx.main : z.d2 * z.cx.echoPct;
      echoJob(@PKG@.AbilWorld.at(st), z.cx, @PKG@.AbilDefs.HFISTS, z.shape, z.x, z.y, z.z, z.r, ea, now + Math.round(@PKG@.AbilCfg.ECHO_DELAY * 1000.0));
    }
    if (n > 0 && !z.echoed) { z.echoed = true; used(z.caster, z.pkey, z.ai, z.cx); }
    @PR@ pr = prOf(z.caster);
    if (pr != null) say(pr, "Shockwave! " + n + (n == 1 ? " Awed enemy hit." : " Awed enemies hit."));
    LAST_MONK = "wave " + n;
  }
  if (z.n1 == 0 && !z.echoed && z.total >= (int) @PKG@.AbilCfg.FF_COUNT) { z.echoed = true; used(z.caster, z.pkey, z.ai, z.cx); }
  if (now >= z.nextFx) { z.nextFx = now + 1000L; particle(FX_FLOW, z.x, z.y + 0.1, z.z, cb); }
  return true;
}''')
# ---------------------------------------------------------------- STILL WATER (zone kind 9)
late(r'''
public static String stanceAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  Object old = @PKG@.AbilStore.STANCES.get(u);
  if (old instanceof @PKG@.AbilZone) { ((@PKG@.AbilZone) old).ended = true; ((@PKG@.AbilZone) old).why = "replaced"; }
  double secs = sh == 1 ? @PKG@.AbilCfg.SW_SP_TIME : (sh == 3 ? @PKG@.AbilCfg.SW_CR_TIME : @PKG@.AbilCfg.SW_TIME);
  long life = Math.round(cxds(secs) * 1000.0);
  double[] me = here(acc, ref);
  @PKG@.AbilZone z = new @PKG@.AbilZone(9, u, me == null ? 0.0 : me[0], me == null ? 0.0 : me[1], me == null ? 0.0 : me[2], 1.0, now, now + life);
  z.pkey = k;
  z.ai = @PKG@.AbilDefs.STILLW;
  z.shape = sh;
  z.follow = true;
  z.h = h;
  z.name = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.STILLW, sh);
  z.amount = h * (sh == 3 ? @PKG@.AbilCfg.SW_CR_P : @PKG@.AbilCfg.SW_POWER) * cxm();
  z.n1 = 0;
  z.n2 = sh == 1 ? 0 : (sh == 3 ? 2 : 1);
  z.d1 = c != null && c.has(@PKG@.AbilModDefs.ECHO) ? @PKG@.AbilCfg.SW_ECHO_T + 0.5 * (double) (c.lv(@PKG@.AbilModDefs.ECHO) - 1) : 0.0;
  z.hits = 0;
  z.nextHeal = now + 1000L;
  z.hit = new java.util.HashSet();
  int wl = c == null ? 0 : c.lv(@PKG@.AbilModDefs.WARD);
  if (wl > 0) {
    double mx = max(map(acc, ref), @DST@.getHealth());
    if (mx > 0.0) wardGive(u, mx * 3.0 * (double) wl / 100.0, now + life);
  }
  aw.addZone(z);
  @PKG@.AbilStore.STANCES.put(u, z);
  if (c != null && "Monk".equals(c.cls) && c.node("PC4")) speedSet(acc, ref, u, -20, (double) life / 1000.0);
  if (pr != null) say(pr, z.name + ": " + @PKG@.AbilMath.fmt((double) life / 1000.0) + " s - melee hits are countered" + (z.n2 == 2 ? ", projectiles from every side deflected." : (z.n2 == 1 ? ", projectiles from the front deflected." : ".")));
  LAST_MONK = "stance " + z.name;
  return " counter=" + @PKG@.AbilMath.fmt(z.amount) + " life=" + life + " deflect=" + z.n2 + (z.d1 > 0.0 ? " echo=" + @PKG@.AbilMath.fmt(z.d1) : "") + (wl > 0 ? " ward" : "");
}''')
late(r'''
public static void stanceEnd(@PKG@.AbilZone z, @CAC@ acc, @REF@ cr) {
  z.ended = true;
  boolean mine = @PKG@.AbilStore.STANCES.get(z.caster) == z;   // FIX (critic): a replaced stance never clears the new one's Tranquility
  if (mine) @PKG@.AbilStore.STANCES.remove(z.caster);
  if (mine && cr != null && cr.isValid() && z.cx != null && "Monk".equals(z.cx.cls) && z.cx.node("PC4")) speedClear(acc, cr, z.caster);
  @PR@ pr = prOf(z.caster);
  if (pr != null && !"left".equals(z.why) && !"replaced".equals(z.why)) say(pr, "Still Water ended - " + z.hits + (z.hits == 1 ? " counter." : " counters."));
  LAST_MONK = "stance end " + z.why + " counters=" + z.hits;
}''')
late(r'''
public static boolean stanceTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  boolean ok = live(cb, cr, z.caster, z.pkey);
  if (!ok) z.why = "left";
  if (ok && !z.ended && now >= z.until && z.n1 == 0 && z.d1 > 0.0) {
    z.n1 = 1;
    z.n2 = 0;
    z.until = now + Math.round(z.d1 * 1000.0);
    if (z.cx != null && "Monk".equals(z.cx.cls) && z.cx.node("PC4") && @PKG@.AbilStore.STANCES.get(z.caster) == z) speedClear(cb, cr, z.caster);   // FIX
    @PR@ pr = prOf(z.caster);
    if (pr != null) say(pr, "Echo: your counters stay " + @PKG@.AbilMath.fmt(z.d1) + " s - move freely.");
  }
  if (!ok || z.ended || now >= z.until) {
    if (z.why == null || z.why.length() == 0) z.why = "time";
    stanceEnd(z, cb, cr);
    return false;
  }
  zoneFollow(z, cb);
  if (z.n1 == 0 && now >= z.nextHeal && z.cx != null && "Monk".equals(z.cx.cls) && z.cx.node("PC4")) {
    z.nextHeal = now + 1000L;
    double mx = max(map(cb, cr), @DST@.getHealth());
    if (mx > 0.0) z.absorbed = z.absorbed + apply(cb, cr, mx * 0.01, mx * 0.01);
  }
  if (now >= z.nextFx) { z.nextFx = now + 1000L; particle(FX_FLOW, z.x, z.y + 0.1, z.z, cb); }
  return true;
}''')
late(r'''
public static void counter(@CB@ buf, @REF@ r, java.util.UUID u, @REF@ att, @PKG@.AbilZone z, long now) {
  hit(buf, att, r, u, z.amount, "StillWater");
  COUNTERS = COUNTERS + 1L;
  z.hits = z.hits + 1;
  aweOn(buf, att, r, u, z.hits * 2, z.cx, now);
  @PKG@.AbilCtx c = z.cx;
  int kb = c == null ? 0 : c.eff(@PKG@.AbilModDefs.KNOCK);
  @VEC@ p = pos(buf, r);
  @VEC@ q = pos(buf, att);
  if (kb > 0 && p != null && q != null) {
    double dx = q.x - p.x;
    double dz = q.z - p.z;
    double d = Math.sqrt(dx * dx + dz * dz);
    double f = 2.0 * (double) kb * @PKG@.AbilCfg.PUSH_PER_BLOCK;
    if (d > 0.05) push(buf, att, dx / d * f, f * 0.25, dz / d * f);
  }
  if (c != null && "Monk".equals(c.cls) && c.node("PC2")) stunMob(buf, att, u, 0.5, now);
  if (q != null) particle(FX_COUNTER, q.x, q.y + 1.0, q.z, buf);
  if (!z.echoed) { z.echoed = true; used(u, z.pkey, @PKG@.AbilDefs.STILLW, c); }
  LAST_MONK = "counter " + z.hits + (z.n1 == 1 ? " echo" : "");
}''')
# the damage hook (AbilShieldSys - players hit, AFTER armour): Awe (Calm Aura / Serenity), Iron Skin, Still Water
late(r'''
public static String inHit(@ST@ st, @CB@ buf, @REF@ r, @DMG@ d, long now) {
  if (d == null || r == null || d.isCancelled()) return null;
  float a0 = d.getAmount();
  if (!(a0 > 0.0f) || @PKG@.AbilDmg.mine(d)) return null;
  @DSRC@ src = d.getSource();
  if (!(src instanceof @DENT@)) return null;
  Object po = buf.getComponent(r, @PR@.getComponentType());
  if (!(po instanceof @PR@)) return null;
  if (buf.getComponent(r, @INVU@.getComponentType()) != null) return null;   // FIX (critic): invulnerable - the engine drops this hit later
  java.util.UUID u = ((@PR@) po).getUuid();
  if (u == null) return null;
  @REF@ att = null;
  try { att = ((@DENT@) src).getRef(); } catch (Throwable t0) { att = null; }
  boolean proj = src instanceof @DPRJ@;
  String out = "";
  double amt = (double) a0;
  if (att != null && !@PKG@.AbilStore.AWED.isEmpty()) {
    Object ao = @PKG@.AbilStore.AWED.get(att);
    if (ao instanceof long[] && ((long[]) ao)[0] > now) {
      long[] a = (long[]) ao;
      double cut = 0.0;
      if ((a[4] & 1L) != 0L) { double cc = 0.4 * (double) a[3]; cut = cut + (cc > 8.0 ? 8.0 : cc); }
      if ((a[4] & 2L) != 0L) cut = cut + 15.0;
      if (cut > 0.0) { amt = amt * (1.0 - cut / 100.0); out = "awe-" + @PKG@.AbilMath.fmt(cut); }
    }
  }
  Object fo = @PKG@.AbilStore.FLOWS.get(u);
  if (fo instanceof @PKG@.AbilZone) {
    @PKG@.AbilZone fz = (@PKG@.AbilZone) fo;
    if (!fz.ended && fz.cx != null && "Monk".equals(fz.cx.cls) && fz.cx.node("PB4") && stacks(fz, now) >= 10) { amt = amt * 0.9; out = out + " skin"; }
  }
  Object so = @PKG@.AbilStore.STANCES.get(u);
  if (so instanceof @PKG@.AbilZone) {
    @PKG@.AbilZone z = (@PKG@.AbilZone) so;
    if (!z.ended && now < z.until && (z.pkey == null || z.pkey.equals(@PKG@.ClassCfg.pkey(u)))) {
      if (proj) {
        if (z.n1 == 0 && z.n2 > 0 && facing(buf, r, att, z.n2 == 2 ? 180.0 : @PKG@.AbilCfg.SW_FRONT)) {
          d.setAmount(0.0f);
          d.setCancelled(true);
          DEFLECTS = DEFLECTS + 1L;
          z.hits = z.hits + 0;
          return (out + " deflect").trim();
        }
      } else if (att != null && att.isValid() && enemy(buf, att, r)) {
        d.setAmount(0.0f);
        d.setCancelled(true);
        Object lo = z.healed.get(att);
        long gap = Math.round(@PKG@.AbilCfg.SW_GAP * 1000.0);
        if (!(lo instanceof Long) || now - ((Long) lo).longValue() >= gap || now < ((Long) lo).longValue()) {
          z.healed.put(att, Long.valueOf(now));
          counter(buf, r, u, att, z, now);
          return (out + " counter").trim();
        }
        return (out + " blocked").trim();
      }
    }
  }
  if (amt < (double) a0 - 1.0E-6) d.setAmount((float) amt);
  return out.length() == 0 ? null : out.trim();
}''')
# ---------------------------------------------------------------- PALM STRIKE (job kind 11)
late(r'''
public static String palmCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, @REF@ t, long now) {
  if (t == null) return " notarget";
  if (sh == 1) {
    @VEC@ p = pos(st, ref);
    @VEC@ q = pos(st, t);
    if (p != null && q != null) {
      double dx = q.x - p.x;
      double dz = q.z - p.z;
      double dd = Math.sqrt(dx * dx + dz * dz);
      double sp = @PKG@.AbilCfg.PS_SP_STEP * @PKG@.AbilCfg.PUSH_PER_BLOCK;
      if (dd > 0.5) push(st, ref, dx / dd * sp, 0.0, dz / dd * sp);
    }
  }
  @PKG@.AbilJob j = new @PKG@.AbilJob(11, now, u, "PalmStrike", 0.0, 0.0, 0.0, 0.0, h * @PKG@.AbilCfg.PS_POWER * cxm());
  j.pkey = k;
  j.ai = @PKG@.AbilDefs.PALM;
  j.sh = sh;
  j.tref = t;
  aw.add(j);
  return " palm=" + @PKG@.AbilMath.fmt(j.amount);
}''')
late(r'''
public static String palmRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_MONK = "palm gone"; return "gone"; }
  if (!(j.tref instanceof @REF@)) return "notarget";
  @REF@ t = (@REF@) j.tref;
  if (!enemy(cb, t, cr)) { LAST_MONK = "palm dead"; return "dead"; }
  @PKG@.AbilCtx c = j.cx;
  boolean echo = c != null && c.echo;
  boolean monk = c != null && "Monk".equals(c.cls);
  int sh = j.sh;
  double amt = j.amount;
  boolean crit = false;
  long ms = j.caster.getMostSignificantBits();
  long ls = j.caster.getLeastSignificantBits();
  if (!echo && monk && c.node("PB5")) {
    Object po = @PKG@.AbilStore.PALMS.get(t);
    long[] pc = null;
    if (po instanceof long[]) pc = (long[]) po;
    if (pc == null || pc[1] != ms || pc[2] != ls) pc = new long[] { 0L, ms, ls, 0L };
    pc[0] = pc[0] + 1L;
    pc[3] = now + 60000L;
    if (pc[0] >= 3L) { crit = true; pc[0] = 0L; }
    @PKG@.AbilStore.PALMS.put(t, pc);
    if (@PKG@.AbilStore.PALMS.size() > 512) pruneIdx(@PKG@.AbilStore.PALMS, now, 3);
    if (crit) amt = amt * (1.0 + (double) @PKG@.AbilCfg.CRIT_STAND / 100.0);
  }
  boolean ok = hit(cb, t, cr, j.caster, amt, "PalmStrike");
  if (ok) PALMHITS = PALMHITS + 1L;
  double stun = sh == 1 ? @PKG@.AbilCfg.PS_SP_STUN : (sh == 2 ? @PKG@.AbilCfg.PS_AI_STUN : (sh == 3 ? @PKG@.AbilCfg.PS_CR_STUN : @PKG@.AbilCfg.PS_STUN));
  if (monk && sh == 0 && c.node("PB3") && stun < 1.0) stun = 1.0;
  if (c != null && c.lvl > 1) stun = stun + 0.01 * (double) (c.lvl - 1);
  if (monk && sh == 2 && c.node("PA3")) stun = stun * 0.9;
  stunMob(cb, t, j.caster, stun, now);
  if (monk && c.node("PB3")) effect(cb, t, "Vulnerable", 2.0);
  @VEC@ p = pos(cb, cr);
  @VEC@ q = pos(cb, t);
  int kb = c == null ? 0 : c.eff(@PKG@.AbilModDefs.KNOCK);
  if (sh != 3 && p != null && q != null) {
    double blocks = (sh == 1 ? @PKG@.AbilCfg.PS_SP_PUSH : @PKG@.AbilCfg.PS_PUSH) + 2.0 * (double) kb;
    double f = blocks * @PKG@.AbilCfg.PUSH_PER_BLOCK;
    if (sh == 2) push(cb, t, 0.0, monk && c.node("PA3") ? f : -f, 0.0);
    else {
      double dx = q.x - p.x;
      double dz = q.z - p.z;
      double dd = Math.sqrt(dx * dx + dz * dz);
      if (dd > 0.05) push(cb, t, dx / dd * f, f * 0.25, dz / dd * f);
    }
  }
  if (sh == 3) aweOn(cb, t, cr, j.caster, 1, c, now);
  int sl = c == null ? 0 : c.eff(@PKG@.AbilModDefs.SLOW);
  if (sl > 0) effect(cb, t, EF_SLOW, 1.0 + (double) sl);
  int rc = c == null ? 0 : c.eff(@PKG@.AbilModDefs.RICOCHET);
  int rn = 0;
  if (rc > 0 && q != null) {
    double rr = 2.5 + 0.5 * (double) (rc - 1);
    java.util.List l = near(cb, q.x, q.y, q.z, rr);
    java.util.HashSet seen = new java.util.HashSet();
    for (int i = 0; i < l.size(); i++) {
      Object o = l.get(i);
      if (!(o instanceof @REF@)) continue;
      @REF@ x = (@REF@) o;
      if (x.equals(t) || !seen.add(x) || !enemy(cb, x, cr)) continue;
      if (stunMob(cb, x, j.caster, stun, now) >= 0) rn++;
    }
  }
  if (q != null) particle(FX_PALM, q.x, q.y + 1.0, q.z, cb);
  if (!echo && c != null && c.echoPct > 0.0) {
    @PKG@.AbilCtx e = c.echoOf(c.echoPct);
    @PKG@.AbilJob ej = new @PKG@.AbilJob(11, now + Math.round(@PKG@.AbilCfg.ECHO_DELAY * 1000.0), j.caster, "PalmStrike", 0.0, 0.0, 0.0, 0.0, c.main > 0.0 ? j.amount * e.main / c.main : j.amount * c.echoPct);
    ej.pkey = j.pkey;
    ej.ai = j.ai;
    ej.sh = sh;
    ej.tref = t;
    ej.cx = e;
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
    if (aw != null) aw.add(ej);
  }
  if (echo) ECHOES = ECHOES + 1L;
  if (ok && !echo) used(j.caster, j.pkey, @PKG@.AbilDefs.PALM, c);
  @PR@ pr = prOf(j.caster);
  if (pr != null && ok) say(pr, (echo ? "Echo: " : "") + @PKG@.AbilDefs.sname(@PKG@.AbilDefs.PALM, sh) + (crit ? " - CRIT (Iron Fist)" : "") + ": stun " + @PKG@.AbilMath.fmt(stun) + " s" + (rn > 0 ? ", " + rn + " more stunned (Ricochet)." : "."));
  LAST_MONK = "palm" + (echo ? " echo" : "") + (crit ? " crit" : "") + " stun=" + @PKG@.AbilMath.fmt(stun) + " ric=" + rn;
  return LAST_MONK;
}''')
# ---------------------------------------------------------------- CYCLONE KICK (job kind 12)
late(r'''
public static @PKG@.AbilJob kickJob(java.util.UUID u, String k, double[] at, int sh, double h, long now) {
  @PKG@.AbilJob j = new @PKG@.AbilJob(12, now, u, "CycloneKick", at[0], at[1], at[2], 0.0, h * @PKG@.AbilCfg.CK_POWER * cxm());
  j.pkey = k;
  j.ai = @PKG@.AbilDefs.CYCLONE;
  j.sh = sh;
  double r = sh == 1 ? @PKG@.AbilCfg.CK_SP_R : (sh == 2 ? @PKG@.AbilCfg.CK_AI_R : @PKG@.AbilCfg.CK_RADIUS);
  j.r = r + cxr();
  j.push = sh == 3 ? 0.0 : (sh == 1 ? @PKG@.AbilCfg.CK_SP_PUSH : @PKG@.AbilCfg.CK_PUSH);
  j.stun = sh == 3 ? @PKG@.AbilCfg.CK_CR_STUN : 0.0;
  return j;
}''')
late(r'''
public static String kickCast(@ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, double[] at, long now) {
  double[] c = at != null ? at : here(st, ref);
  if (c == null) return " nopos";
  @PKG@.AbilJob j = kickJob(u, k, c, sh, h, now);
  if (sh == 1) {
    double[] f = flat(st, ref);
    j.from = f == null ? 0.0 : f[0];
    j.to = f == null ? 0.0 : f[1];
  }
  aw.add(j);
  return " r=" + @PKG@.AbilMath.fmt(j.r) + " kick=" + @PKG@.AbilMath.fmt(j.amount) + " push=" + @PKG@.AbilMath.fmt(j.push) + (j.stun > 0.0 ? " stun=" + @PKG@.AbilMath.fmt(j.stun) : "");
}''')
late(r'''
public static int kickRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_MONK = "kick gone"; return -1; }
  @PKG@.AbilCtx c = j.cx;
  double cx0 = j.x;
  double cz0 = j.z;
  double cy0 = j.y;
  boolean arc = j.sh == 1 && (j.from != 0.0 || j.to != 0.0);
  if (j.sh != 2) {
    @VEC@ p = pos(cb, cr);
    if (p != null) { cx0 = p.x; cy0 = p.y; cz0 = p.z; }
  }
  java.util.List l = near(cb, cx0, cy0, cz0, j.r);
  java.util.HashSet seen = new java.util.HashSet();
  int kn = c == null ? 0 : c.eff(@PKG@.AbilModDefs.KNOCK);
  double kb = (j.push + 2.0 * (double) kn) * @PKG@.AbilCfg.PUSH_PER_BLOCK;
  int sl = c == null ? 0 : c.eff(@PKG@.AbilModDefs.SLOW);
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    @VEC@ q = pos(cb, t);
    if (q == null) continue;
    double dx = q.x - cx0;
    double dz = q.z - cz0;
    double dd = Math.sqrt(dx * dx + dz * dz);
    if (arc && dx * j.from + dz * j.to < 0.0) continue;
    if (hit(cb, t, cr, j.caster, j.amount, "CycloneKick")) n++;
    if (j.push > 0.0) {
      if (dd > 0.05) push(cb, t, dx / dd * kb, j.sh == 2 ? kb * 0.6 : kb * 0.25, dz / dd * kb);
      else push(cb, t, kb, kb * 0.25, 0.0);
    }
    if (j.stun > 0.0) stunMob(cb, t, j.caster, j.stun, now);
    if (sl > 0) effect(cb, t, EF_SLOW, 1.0 + (double) sl);
  }
  particle(FX_KICK, cx0, cy0 + 0.5, cz0, cb);
  int hs = c == null ? 0 : c.lv(@PKG@.AbilModDefs.HASTE);
  if (hs > 0) haste(cb, cr, j.caster, (int) @PKG@.AbilCfg.CK_HASTE, 3.0 + (double) (hs - 1));
  if (n > 0 && (c == null || !c.echo)) used(j.caster, j.pkey, @PKG@.AbilDefs.CYCLONE, c);
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.CYCLONE, j.sh) + ": " + n + (n == 1 ? " enemy kicked." : " enemies kicked."));
  LAST_MONK = "kick " + n + (hs > 0 ? " haste" : "");
  return n;
}''')
# ---------------------------------------------------------------- CLOAK + FIRST STRIKE (zone kind 12), VANISHING ACT (kind 11)
late(r'''
public static void strikeArm(java.util.UUID u, @PKG@.AbilCtx c, double bonus0, long now) {
  double bonus = bonus0;
  double win = @PKG@.AbilCfg.CL_WINDOW;
  boolean asn = c != null && "Assassin".equals(c.cls);
  boolean lethal = asn && c.node("PA2");
  if (lethal) { bonus = bonus + 15.0; win = win - 2.0; }
  boolean mark = asn && c.node("PA5");
  if (mark) bonus = bonus * 0.9;
  if (win < 0.5) win = 0.5;
  @PKG@.AbilStore.STRIKE.put(u, new double[] { (double) (now + Math.round(win * 1000.0)), bonus, mark ? 1.0 : 0.0, lethal ? 1.0 : 0.0, 0.0 });
}''')
late(r'''
public static @PKG@.AbilZone cloakAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, double secs, int sh, long now, int ai) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  Object old = @PKG@.AbilStore.CLOAKS.get(u);
  if (old instanceof @PKG@.AbilZone) { ((@PKG@.AbilZone) old).ended = true; ((@PKG@.AbilZone) old).why = "replaced"; }
  long life = Math.round(secs * 1000.0);
  double[] me = here(acc, ref);
  @PKG@.AbilZone z = new @PKG@.AbilZone(12, u, me == null ? 0.0 : me[0], me == null ? 0.0 : me[1], me == null ? 0.0 : me[2], @PKG@.AbilCfg.CL_LOSE, now, now + life);
  z.pkey = k;
  z.ai = ai;
  z.shape = sh;
  z.follow = true;
  z.name = ai < 0 ? "Cloak" : @PKG@.AbilDefs.sname(ai, sh);
  z.d1 = me == null ? 0.0 : me[0];
  z.d2 = me == null ? 0.0 : me[2];
  int hl = c == null || ai != @PKG@.AbilDefs.CLOAK ? 0 : c.lv(@PKG@.AbilModDefs.HASTE);
  z.n1 = hl > 0 ? (int) @PKG@.AbilCfg.CL_HASTE : 0;
  z.t2 = now + Math.round(cxds(@PKG@.AbilCfg.CL_TIME) * 1000.0);
  aw.addZone(z);
  @PKG@.AbilStore.CLOAKS.put(u, z);
  effect(acc, ref, "SkyyAbility_Cloak", secs);
  java.util.List l = near(acc, z.x, z.y, z.z, z.r);
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (o instanceof @REF@ && !((@REF@) o).equals(ref)) distract(acc, (@REF@) o, ref);
  }
  particle(FX_SMOKE, z.x, z.y + 1.0, z.z, acc);
  return z;
}''')
late(r'''
public static void cloakEnd(@PKG@.AbilZone z, @CAC@ acc, @REF@ cr) {
  z.ended = true;
  if (@PKG@.AbilStore.CLOAKS.get(z.caster) == z) {
    @PKG@.AbilStore.CLOAKS.remove(z.caster);
    if (cr != null && cr.isValid()) {
      unfreezeOne(acc, cr, "SkyyAbility_Cloak");
      if (z.n1 > 0) speedClear(acc, cr, z.caster);   // FIX: a running Dash Cloak / Hunter's Rush haste stays
    }
  }
  @PR@ pr = prOf(z.caster);
  if (pr != null && !"left".equals(z.why) && !"replaced".equals(z.why)) say(pr, "attack".equals(z.why) ? "Your attack broke the cloak." : "Your cloak faded.");
  LAST_ASN = "cloak end " + z.why;
}''')
late(r'''
public static boolean cloakTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  boolean ok = live(cb, cr, z.caster, z.pkey);
  if (!ok) z.why = "left";
  if (!ok || z.ended || now >= z.until) {
    if (z.why == null || z.why.length() == 0) z.why = "time";
    cloakEnd(z, cb, cr);
    return false;
  }
  zoneFollow(z, cb);
  if (z.shape == 3 && z.ai == @PKG@.AbilDefs.CLOAK) {
    double dx = z.x - z.d1;
    double dz = z.z - z.d2;
    if (dx * dx + dz * dz > 0.25 && z.until > z.t2) z.until = z.t2;
  }
  if (z.n1 > 0) speedKeep(cb, cr, z.caster, z.n1, 1.5);   // FIX: no new effect every tick
  java.util.List l = near(cb, z.x, z.y, z.z, z.r);
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (o instanceof @REF@ && !((@REF@) o).equals(cr) && cb.getComponent((@REF@) o, @NPC@.getComponentType()) != null) distract(cb, (@REF@) o, cr);
  }
  return true;
}''')
late(r'''
public static String cloakCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double secs = cxds(sh == 1 ? @PKG@.AbilCfg.CL_SP_TIME : (sh == 3 ? @PKG@.AbilCfg.CL_CR_TIME : @PKG@.AbilCfg.CL_TIME));
  @PKG@.AbilZone z = cloakAt(pr, st, ref, u, k, aw, secs, sh, now, @PKG@.AbilDefs.CLOAK);
  double bonus = (double) @PKG@.AbilCfg.CL_STRIKE * (c == null ? 1.0 : c.main) + (sh == 3 ? (double) @PKG@.AbilCfg.CL_CR_BONUS : 0.0);
  strikeArm(u, c, bonus, now);
  if (sh == 1) haste(st, ref, u, (int) @PKG@.AbilCfg.CL_SP_SPEED, 3.0);
  if (sh == 2) effect(st, ref, "Immunity_Fall", 3.0);
  double[] fs = (double[]) @PKG@.AbilStore.STRIKE.get(u);
  if (pr != null) say(pr, z.name + ": cloaked " + @PKG@.AbilMath.fmt(secs) + " s - your next hit within " + @PKG@.AbilMath.secs((long) fs[0] - now) + " s is a First Strike (+" + @PKG@.AbilMath.fmt(fs[1]) + " %).");
  LAST_ASN = "cloak " + z.name + " first=" + @PKG@.AbilMath.fmt(fs[1]);
  return " cloak=" + @PKG@.AbilMath.fmt(secs) + " first=" + @PKG@.AbilMath.fmt(fs[1]) + (z.n1 > 0 ? " haste" : "");
}''')
late(r'''
public static String slipAway(@PR@ pr, java.util.UUID u, @CB@ buf, @REF@ att, long now) {
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0 || !"Assassin".equals(@PKG@.ClassDefs.NAMES[ci])) return null;
  if (!@PKG@.AbilModDefs.csvHas(treeCsv(u), "PA4")) return null;
  Object lo = @PKG@.AbilStore.SLIPAT.get(u);
  if (lo instanceof Long && now - ((Long) lo).longValue() < 20000L && now >= ((Long) lo).longValue()) return null;
  @PKG@.AbilStore.SLIPAT.put(u, Long.valueOf(now));
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(buf.getExternalData()));
  cloakAt(pr, buf, att, u, @PKG@.ClassCfg.pkey(u), aw, 2.0, 0, now, -1);
  if (pr != null) say(pr, "Slip Away: cloaked for 2 s.");
  LAST_ASN = "slip away";
  return "slip";
}''')
late(r'''
public static @PKG@.AbilZone smokeAt(@CAC@ acc, java.util.UUID u, String k, @PKG@.AbilWorld aw, double[] at, double r, int sh, long now) {
  if (at == null || aw == null) return null;
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double secs = cxds(@PKG@.AbilCfg.VA_TIME) * (c == null ? 1.0 : c.main);
  @PKG@.AbilZone z = new @PKG@.AbilZone(11, u, at[0], at[1], at[2], r < 1.0 ? 1.0 : r, now, now + Math.round(secs * 1000.0));
  z.pkey = k;
  z.ai = @PKG@.AbilDefs.VANISH;
  z.shape = sh;
  z.name = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.VANISH, sh);
  z.pct = c != null && c.has(@PKG@.AbilModDefs.SLOW) ? 50.0 : (double) @PKG@.AbilCfg.VA_SLOW;
  z.hit = new java.util.HashSet();
  aw.addZone(z);
  particle(FX_SMOKE, z.x, z.y + 0.5, z.z, acc);
  ring(FX_SMOKE, z, acc);
  return z;
}''')
late(r'''
public static boolean smokeTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  if (!live(cb, cr, z.caster, z.pkey) || z.ended || now >= z.until) {
    @PR@ pr = prOf(z.caster);
    if (pr != null && z.hits > 0) say(pr, "The smoke cleared - " + z.hits + (z.hits == 1 ? " enemy lost you." : " enemies lost you."));
    LAST_ASN = "smoke end " + z.hits;
    return false;
  }
  long lose = Math.round(@PKG@.AbilCfg.VA_LOSE * 1000.0);
  java.util.List l = near(cb, z.x, z.y, z.z, z.r);
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    Object fo = z.healed.get(t);
    long[] fv;   // FIX (critic): { entered at, slow refreshed again at } - the slow effect is not re-sent every tick
    if (!(fo instanceof long[])) { fv = new long[] { now, 0L }; z.healed.put(t, fv); z.hits = z.hits + 1; }
    else fv = (long[]) fo;
    if (now - fv[0] < lose) distract(cb, t, cr);
    if (now >= fv[1]) { effect(cb, t, z.pct >= 50.0 ? EF_SLOW : spdId(-(int) z.pct), 1.0); fv[1] = now + 500L; }
  }
  if (z.hits > 0 && !z.echoed) { z.echoed = true; used(z.caster, z.pkey, @PKG@.AbilDefs.VANISH, z.cx); }
  if (z.shape == 3) {
    Object co = @PKG@.AbilStore.CLOAKS.get(z.caster);
    @VEC@ p = pos(cb, cr);
    if (co instanceof @PKG@.AbilZone && p != null && @PKG@.AbilMath.inRange(p.x - z.x, p.y - z.y, p.z - z.z, z.r)) {
      @PKG@.AbilZone ck = (@PKG@.AbilZone) co;
      long cap = ck.start + Math.round(@PKG@.AbilCfg.VA_CR_CLOAK * 1000.0);
      long want = now + 600L;
      if (want > cap) want = cap;
      if (want > ck.until) {
        ck.until = want;
        // FIX (critic): the cloak look is put on ONCE up to the Ambush cap (lookUntil = until when it runs); cloakEnd takes it off
        if (ck.lookUntil < want + 200L) { long vis = cap > want ? cap : want; effect(cb, cr, "SkyyAbility_Cloak", (double) (vis - now) / 1000.0); ck.lookUntil = vis; }
      }
    }
  }
  if (now >= z.nextFx) { z.nextFx = now + 1000L; ring(FX_SMOKE, z, cb); }
  return true;
}''')
late(r'''
public static String vanishCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double secs = cxds(@PKG@.AbilCfg.VA_CLOAK);
  cloakAt(pr, st, ref, u, k, aw, secs, sh, now, @PKG@.AbilDefs.VANISH);
  strikeArm(u, c, (double) @PKG@.AbilCfg.CL_STRIKE * (c == null ? 1.0 : c.main), now);
  if (sh == 2) {
    aw.add(landJob(u, k, @PKG@.AbilDefs.VANISH, 0.0, now));
    if (pr != null) say(pr, "Smoke Drop: cloaked - the smoke rises where you land.");
    return " cloak=" + @PKG@.AbilMath.fmt(secs) + " land";
  }
  double[] at = here(st, ref);
  if (sh == 1 && at != null) {
    double[] f = flat(st, ref);
    if (f != null) at = new double[] { at[0] - f[0] * 4.0, at[1], at[2] - f[1] * 4.0 };
  }
  @PKG@.AbilZone z = smokeAt(st, u, k, aw, at, @PKG@.AbilCfg.VA_RADIUS + cxr(), sh, now);
  if (z == null) return " nopos";
  if (pr != null) say(pr, z.name + ": cloaked " + @PKG@.AbilMath.fmt(secs) + " s, smoke " + @PKG@.AbilMath.fmt(z.r) + " blocks - enemies inside lose you.");
  LAST_ASN = "vanish " + z.name;
  return " cloak=" + @PKG@.AbilMath.fmt(secs) + " smoke=" + @PKG@.AbilMath.fmt(z.r) + " life=" + (z.until - now);
}''')
# ---------------------------------------------------------------- TOXIN (zone kind 10, chained poison job kind 16)
late(r'''
public static @PKG@.AbilZone cloudAt(@CAC@ acc, java.util.UUID u, String k, @PKG@.AbilWorld aw, double[] at, double r, double secs, double amt, int sh, long now) {
  if (at == null || aw == null) return null;
  @PKG@.AbilZone z = new @PKG@.AbilZone(10, u, at[0], at[1], at[2], r < 1.0 ? 1.0 : r, now, now + Math.round(secs * 1000.0));
  z.pkey = k;
  z.ai = @PKG@.AbilDefs.TOXIN;
  z.shape = sh;
  z.amount = amt;
  z.name = @PKG@.AbilDefs.sname(@PKG@.AbilDefs.TOXIN, sh);
  @PKG@.AbilCtx c = z.cx;
  boolean asn = c != null && "Assassin".equals(c.cls);
  z.pct = asn && c.node("PB2") ? 25.0 : (double) @PKG@.AbilCfg.TX_WEAKEN;
  z.n1 = asn && c.node("PB5") ? 1 : 0;
  z.nextHeal = now;
  z.hit = new java.util.HashSet();
  aw.addZone(z);
  particle(FX_TOXIN, z.x, z.y + 0.5, z.z, acc);
  return z;
}''')
late(r'''
public static String toxinCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, double[] at, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double[] spot = (sh == 2 || sh == 3 || at == null) ? here(st, ref) : at;
  if (spot == null) return " nopos";
  double r0 = sh == 1 ? @PKG@.AbilCfg.TX_SP_R : (sh == 3 ? @PKG@.AbilCfg.TX_CR_R : @PKG@.AbilCfg.TX_RADIUS);
  double s0 = sh == 3 ? @PKG@.AbilCfg.TX_CR_T : @PKG@.AbilCfg.TX_TIME;
  boolean plague = c != null && "Assassin".equals(c.cls) && c.node("PB5");
  double secs = cxds(s0) * (plague ? 2.0 : 1.0);
  double amt = h * @PKG@.AbilCfg.TX_POISON * cxm();
  @PKG@.AbilZone z = cloudAt(st, u, k, aw, spot, r0 + cxr(), secs, amt, sh, now);
  if (z == null) return " nopos";
  if (c != null && c.echoPct > 0.0 && !c.echo) {
    @PKG@.AbilCtx e = c.echoOf(c.echoPct);
    @PKG@.AbilJob ej = new @PKG@.AbilJob(10, now + Math.round(@PKG@.AbilCfg.ECHO_DELAY * 1000.0), u, "Toxin", spot[0], spot[1], spot[2], r0 + c.radTree, h * @PKG@.AbilCfg.TX_POISON * e.main);
    ej.pkey = k;
    ej.ai = @PKG@.AbilDefs.TOXIN;
    ej.sh = sh;
    ej.secs = s0 * (plague ? 2.0 : 1.0);
    ej.cx = e;
    aw.add(ej);
  }
  if (pr != null) say(pr, z.name + ": a poison cloud of " + @PKG@.AbilMath.fmt(z.r) + " blocks for " + @PKG@.AbilMath.fmt(secs) + " s (Weakened " + @PKG@.AbilMath.fmt(z.pct) + " %).");
  LAST_ASN = "toxin " + z.name;
  return " cloud r=" + @PKG@.AbilMath.fmt(z.r) + " life=" + (z.until - now) + " poison=" + @PKG@.AbilMath.fmt(amt) + " weaken=" + @PKG@.AbilMath.fmt(z.pct);
}''')
late(r'''
public static boolean poisonOne(@CB@ cb, @REF@ t, @REF@ cr, java.util.UUID u, double amt, double weak, boolean stacks, boolean plague, long now) {
  long ms = u.getMostSignificantBits();
  long ls = u.getLeastSignificantBits();
  Object po = @PKG@.AbilStore.POISONED.get(t);
  long[] p = null;
  if (po instanceof long[]) p = (long[]) po;
  if (p == null || p[1] != ms || p[2] != ls || p[0] <= now) p = new long[] { 0L, ms, ls, 0L, 0L, 0L };
  long st0 = p[3] + 1L;
  if (!stacks) st0 = 1L;
  if (st0 > 3L) st0 = 3L;
  p[3] = st0;
  p[0] = now + 1500L;
  p[4] = now + 2000L;
  p[5] = plague ? 1L : 0L;
  @PKG@.AbilStore.POISONED.put(t, p);
  if (@PKG@.AbilStore.POISONED.size() > 512) pruneIdx(@PKG@.AbilStore.POISONED, now, 4);
  double dmg = amt * (1.0 + 0.3 * (double) (st0 - 1L));
  boolean ok = hit(cb, t, cr, u, dmg, "Toxin");
  int w = (int) Math.round(weak);
  if (w >= 10) effect(cb, t, "SkyyAbility_Weaken_" + (w > 40 ? 40 : w), 2.0);
  POISONS = POISONS + 1L;
  return ok;
}''')
late(r'''
public static boolean cloudTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, z.caster);
  if (!live(cb, cr, z.caster, z.pkey) || z.ended || now >= z.until) {
    @PR@ pr = prOf(z.caster);
    if (pr != null && !z.echoed && z.cx != null && !z.cx.echo) say(pr, (z.name == null ? "Toxin" : z.name) + " poisoned nobody.");
    LAST_ASN = "cloud end";
    return false;
  }
  if (now >= z.nextHeal) {
    z.nextHeal = z.nextHeal + 1000L;
    @PKG@.AbilCtx c = z.cx;
    boolean asn = c != null && "Assassin".equals(c.cls);
    boolean stacks = asn && c.node("PB1");
    boolean contagion = asn && c.node("PB3");
    java.util.List l = near(cb, z.x, z.y, z.z, z.r);
    java.util.HashSet seen = new java.util.HashSet();
    int n = 0;
    for (int i = 0; i < l.size(); i++) {
      Object o = l.get(i);
      if (!(o instanceof @REF@)) continue;
      @REF@ t = (@REF@) o;
      if (!seen.add(t) || !enemy(cb, t, cr)) continue;
      if (poisonOne(cb, t, cr, z.caster, z.amount, z.pct, stacks, z.n1 == 1, now)) n++;
      z.hit.add(t);
      if (contagion) {
        @VEC@ q = pos(cb, t);
        if (q == null) continue;
        java.util.List l2 = near(cb, q.x, q.y, q.z, 2.0);
        for (int k2 = 0; k2 < l2.size(); k2++) {
          Object o2 = l2.get(k2);
          if (!(o2 instanceof @REF@)) continue;
          @REF@ t2 = (@REF@) o2;
          if (!seen.add(t2) || !enemy(cb, t2, cr)) continue;
          if (poisonOne(cb, t2, cr, z.caster, z.amount, z.pct, stacks, z.n1 == 1, now)) n++;
          z.hit.add(t2);
        }
      }
    }
    int cl = c == null ? 0 : c.lv(@PKG@.AbilModDefs.CHAIN);
    if (cl > 0) {
      java.util.Iterator it = new java.util.ArrayList(z.hit).iterator();
      while (it.hasNext()) {
        @REF@ t = (@REF@) it.next();
        if (t != null && t.isValid() && alive(cb, t)) continue;
        z.hit.remove(t);
        if (z.healed.containsKey(t)) continue;
        z.healed.put(t, Long.valueOf(now));
        @VEC@ q = t == null || !t.isValid() ? null : pos(cb, t);
        double qx = q == null ? z.x : q.x;
        double qy = q == null ? z.y : q.y;
        double qz = q == null ? z.z : q.z;
        java.util.List l3 = near(cb, qx, qy, qz, @PKG@.AbilCfg.TX_CHAIN_R);
        @REF@ best = null;
        double bd = 1.0E18;
        for (int k3 = 0; k3 < l3.size(); k3++) {
          Object o3 = l3.get(k3);
          if (!(o3 instanceof @REF@)) continue;
          @REF@ t3 = (@REF@) o3;
          if (t3.equals(t) || !enemy(cb, t3, cr)) continue;
          @VEC@ q3 = pos(cb, t3);
          if (q3 == null) continue;
          double dd = (q3.x - qx) * (q3.x - qx) + (q3.y - qy) * (q3.y - qy) + (q3.z - qz) * (q3.z - qz);
          if (dd < bd) { bd = dd; best = t3; }
        }
        if (best == null) continue;
        @PKG@.AbilJob pj = new @PKG@.AbilJob(16, now, z.caster, "Toxin", qx, qy, qz, 0.0, z.amount);
        pj.pkey = z.pkey;
        pj.ai = @PKG@.AbilDefs.TOXIN;
        pj.tref = best;
        pj.left = 2 + cl;
        pj.every = 1000L;
        pj.width = z.pct;
        @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
        if (aw != null) aw.add(pj);
        LAST_ASN = "chain";
      }
    }
    if (n > 0 && !z.echoed) { z.echoed = true; if (z.cx == null || !z.cx.echo) used(z.caster, z.pkey, @PKG@.AbilDefs.TOXIN, z.cx); }
    ring(FX_TOXIN, z, cb);
  }
  return true;
}''')
late(r'''
public static boolean poisonTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey) || !(j.tref instanceof @REF@)) return false;
  @REF@ t = (@REF@) j.tref;
  if (!enemy(cb, t, cr)) return false;
  poisonOne(cb, t, cr, j.caster, j.amount, j.width, false, false, now);
  @VEC@ q = pos(cb, t);
  if (q != null) particle(FX_TOXIN, q.x, q.y + 1.0, q.z, cb);
  j.left = j.left - 1;
  j.at = now + (j.every > 0L ? j.every : 1000L);
  return j.left > 0;
}''')
# ---------------------------------------------------------------- GOD KILLER (ARMED; Patient Kill job kind 15; echo job kind 14)
late(r'''
public static String gkArm(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String k, int sh, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double win = cxds(sh == 1 ? @PKG@.AbilCfg.GK_SP_WIN : (sh == 3 ? @PKG@.AbilCfg.GK_CR_WIN : @PKG@.AbilCfg.GK_WINDOW));
  boolean asn = c != null && "Assassin".equals(c.cls);
  boolean hunter = asn && c.node("PA3");
  double m = @PKG@.AbilCfg.GK_MULT + (hunter ? 0.3 : 0.0);
  double b = @PKG@.AbilCfg.GK_BACK + (hunter ? 0.3 : 0.0);
  double main = c == null ? 1.0 : c.main;
  m = 1.0 + (m - 1.0) * main;
  b = 1.0 + (b - 1.0) * main;
  int hl = c == null ? 0 : c.lv(@PKG@.AbilModDefs.HASTE);
  @PKG@.AbilStore.ARMED.put(u, new double[] { (double) (now + Math.round(win * 1000.0)), m, b, sh == 2 ? 1.0 : 0.0, c == null ? 0.0 : c.echoPct,
    hl > 0 ? 3.0 + (double) (hl - 1) : 0.0, hunter ? 1.0 : 0.0 });
  if (sh == 1) haste(acc, ref, u, (int) @PKG@.AbilCfg.GK_SP_SPEED, win);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.GODK, sh) + ": your next hit on a boss within " + @PKG@.AbilMath.fmt(win) + " s deals " + @PKG@.AbilMath.fmt(m) + "x (" + @PKG@.AbilMath.fmt(b) + "x from behind" + (sh == 2 ? " or while falling" : "") + ").");
  LAST_ASN = "god armed x" + @PKG@.AbilMath.fmt(m) + "/" + @PKG@.AbilMath.fmt(b);
  return " window=" + @PKG@.AbilMath.fmt(win) + " mult=" + @PKG@.AbilMath.fmt(m) + " back=" + @PKG@.AbilMath.fmt(b);
}''')
late(r'''
public static @PKG@.AbilJob armJob(java.util.UUID u, String k, double[] at, double mana, double stam, long now) {
  double[] a = at == null ? new double[] { 0.0, 0.0, 0.0 } : at;
  @PKG@.AbilJob j = new @PKG@.AbilJob(15, now + 1000L, u, "GodKiller", a[0], a[1], a[2], 0.0, 0.0);
  j.pkey = k;
  j.ai = @PKG@.AbilDefs.GODK;
  j.sh = 3;
  j.paidMana = mana;
  j.paidStam = stam;
  return j;
}''')
late(r'''
public static String armRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) return "gone";
  @PR@ pr = prOf(j.caster);
  @VEC@ p = pos(cb, cr);
  if (p == null) return "nopos";
  if (!@PKG@.AbilMath.inRange(p.x - j.x, p.y - j.y, p.z - j.z, @PKG@.AbilCfg.CHAN_MOVE)) {
    @ESM@ m = map(cb, cr);
    if (m != null) {
      if (j.paidMana > 0.0) m.addStatValue(@DST@.getMana(), (float) j.paidMana);
      if (j.paidStam > 0.0) m.addStatValue(@DST@.getStamina(), (float) j.paidStam);
    }
    @PKG@.AbilStore.arm(j.pkey, j.what, now, 0L);
    if (pr != null) send(pr, "Patient Kill broke - you moved. Your Mana, Stamina and cooldown were given back.", "#ffc800");
    LAST_ASN = "patient moved";
    return "moved";
  }
  return gkArm(pr, cb, cr, j.caster, j.pkey, 3, now);
}''')
late(r'''
public static String gkEchoRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey) || !(j.tref instanceof @REF@)) return "gone";
  @REF@ t = (@REF@) j.tref;
  if (!enemy(cb, t, cr)) return "dead";
  boolean ok = hit(cb, t, cr, j.caster, j.amount, "GodKiller");
  ECHOES = ECHOES + 1L;
  @VEC@ q = pos(cb, t);
  if (q != null) particle(FX_GOD, q.x, q.y + 1.0, q.z, cb);
  @PR@ pr = prOf(j.caster);
  if (pr != null && ok) say(pr, "Echo: God Killer strikes again (" + @PKG@.AbilMath.fmt(j.amount) + ").");
  LAST_ASN = "god echo";
  return ok ? "hit" : "miss";
}''')
# the outgoing hook (DamageLock - a weapon hit, Filter group): First Strike, Death Mark, God Killer, Plague
late(r'''
public static String outHit(@ST@ st, @CB@ buf, @REF@ t, @DMG@ d, java.util.UUID u, long now) {
  try {
    if (u == null || t == null || d == null || d.isCancelled()) return null;
    float a0 = d.getAmount();
    if (!(a0 > 0.0f)) return null;
    if (buf.getComponent(t, @PR@.getComponentType()) != null) return null;
    if (buf.getComponent(t, @NPC@.getComponentType()) == null) return null;
    long ms = u.getMostSignificantBits();
    long ls = u.getLeastSignificantBits();
    double mult = 1.0;
    String out = "";
    Object so = @PKG@.AbilStore.STRIKE.get(u);
    if (so instanceof double[]) {
      double[] f = (double[]) so;
      if ((double) now < f[0]) {
        mult = mult * (1.0 + f[1] / 100.0);
        STRIKES = STRIKES + 1L;
        out = "first+" + @PKG@.AbilMath.fmt(f[1]);
        if (f[2] > 0.0) @PKG@.AbilStore.MARKS.put(t, new long[] { now + 5000L, ms, ls, now });
        if (f[3] > 0.0) { f[3] = 0.0; f[0] = 0.0; f[4] = (double) (now + 2000L); }
        else @PKG@.AbilStore.STRIKE.remove(u);
        used(u, @PKG@.ClassCfg.pkey(u), @PKG@.AbilDefs.CLOAK, null);
        @PR@ fp = prOf(u);
        if (fp != null) say(fp, "First Strike! +" + @PKG@.AbilMath.fmt(f[1]) + " %.");
      } else if ((double) now < f[4]) {
        if (Math.random() < 0.5) { mult = mult * (1.0 + f[1] / 100.0); out = "second+" + @PKG@.AbilMath.fmt(f[1]); }
        @PKG@.AbilStore.STRIKE.remove(u);
      } else @PKG@.AbilStore.STRIKE.remove(u);
    }
    Object mo = @PKG@.AbilStore.MARKS.get(t);
    if (mo instanceof long[]) {
      long[] mk = (long[]) mo;
      if (mk[0] <= now) @PKG@.AbilStore.MARKS.remove(t);
      else if (mk[1] == ms && mk[2] == ls && now - mk[3] > 20L) { mult = mult * 1.5; @PKG@.AbilStore.MARKS.remove(t); out = out + " mark"; }
    }
    Object go = @PKG@.AbilStore.ARMED.get(u);
    if (go instanceof double[]) {
      double[] g = (double[]) go;
      if ((double) now >= g[0]) @PKG@.AbilStore.ARMED.remove(u);
      else if (bossFor(buf, t, g[6] > 0.0)) {
        @PR@ pr = prOf(u);
        @REF@ att = pr == null ? null : pr.getReference();
        boolean back = att != null && att.isValid() && (behindHit(buf, t, att) || (g[3] > 0.0 && !onGround(buf, att)));
        double gm = back ? g[2] : g[1];
        mult = mult * gm;
        @PKG@.AbilStore.ARMED.remove(u);
        GODKILLS = GODKILLS + 1L;
        out = out + " god" + @PKG@.AbilMath.fmt(gm) + (back ? "back" : "");
        if (g[5] > 0.0 && att != null) haste(buf, att, u, (int) @PKG@.AbilCfg.GK_HASTE, g[5]);
        if (g[4] > 0.0) {
          @PKG@.AbilJob ej = new @PKG@.AbilJob(14, now + Math.round(@PKG@.AbilCfg.ECHO_DELAY * 1000.0), u, "GodKiller", 0.0, 0.0, 0.0, 0.0, (double) a0 * gm * g[4]);
          ej.pkey = @PKG@.ClassCfg.pkey(u);
          ej.ai = @PKG@.AbilDefs.GODK;
          ej.tref = t;
          @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
          if (aw != null) aw.add(ej);
        }
        @VEC@ q = pos(buf, t);
        if (q != null) particle(FX_GOD, q.x, q.y + 1.0, q.z, buf);
        if (pr != null) say(pr, "God Killer! x" + @PKG@.AbilMath.fmt(gm) + (back ? " (from behind)." : "."));
        used(u, @PKG@.ClassCfg.pkey(u), @PKG@.AbilDefs.GODK, null);
      }
    }
    Object po = @PKG@.AbilStore.POISONED.get(t);
    if (po instanceof long[]) {
      long[] p = (long[]) po;
      if (p[4] > now && p[5] == 1L && p[1] == ms && p[2] == ls) { mult = mult * 1.1; out = out + " plague"; }
    }
    if (mult != 1.0) { d.setAmount((float) ((double) a0 * mult)); LAST_ASN = out.trim() + " x" + @PKG@.AbilMath.fmt(mult); }
    return out.length() == 0 ? null : out.trim();
  } catch (Throwable x) { @PKG@.ClassCfg.warnLimited("an Assassin hit bonus failed: " + x); return null; }
}''')
# the landed hook (AbilFrostSys - Inspect group): combo stacks, the cloak breaks, Slip Away
late(r'''
public static String hitLanded(@CB@ buf, @REF@ t, @DMG@ d, long now) {
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
    if (u == null) return null;
    if (buf.getComponent(t, @NPC@.getComponentType()) == null) return null;
    String out = "";
    Object fz = @PKG@.AbilStore.FLOWS.get(u);
    if (fz instanceof @PKG@.AbilZone) { int a = flowHit((@PKG@.AbilZone) fz, buf, att, now); if (a > 0) out = "combo+" + a; }
    Object cz = @PKG@.AbilStore.CLOAKS.get(u);
    if (cz instanceof @PKG@.AbilZone) {
      @PKG@.AbilZone z = (@PKG@.AbilZone) cz;
      if (!z.ended) {
        if (z.cx != null && "Assassin".equals(z.cx.cls) && z.cx.node("PA1")) { long g = now + 300L; if (g < z.until) z.until = g; z.why = "attack"; }
        else { z.ended = true; z.why = "attack"; }
        out = out + " uncloak";
      }
    }
    if (SLIP_ON && !alive(buf, t)) { String r = slipAway((@PR@) po, u, buf, att, now); if (r != null) out = out + " " + r; }
    return out.length() == 0 ? null : out.trim();
  } catch (Throwable x) { return null; }
}''')
# the zone dispatch of the 0.1.23 kinds
late(r'''
public static boolean zoneTick3(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind == 8) return flowTick(z, st, cb, now);
  if (z.kind == 9) return stanceTick(z, st, cb, now);
  if (z.kind == 10) return cloudTick(z, st, cb, now);
  if (z.kind == 11) return smokeTick(z, st, cb, now);
  if (z.kind == 12) return cloakTick(z, st, cb, now);
  return false;
}''')

for _m in NEW_LATE:
    assert '"""' not in _m
rep('''  return true;
}
"""
]


def _late_stub(src):''', '''  return true;
}
""",
''' + ",\n".join('r"""\n%s\n"""' % _m for _m in NEW_LATE) + '''
]


def _late_stub(src):''')

# ================================================================================================ ClassRb: the rebirth participant (rebirth:part:classes)
rep('''# THE LATE BODIES (every class above exists now)
for _src in ABIL_LATE:''', '''# 0.1.23 REBIRTH R6: ClassRb = rebirth:part:classes (research/cloud/Rebirth-Spec.md 4.2 / 4.3 / 5.2 / 5.3; the SkyyCoins 0.1.7 CoinRb shape)
crb = pool.makeClass(PKG + ".ClassRb")
crb.addInterface(pool.get("java.util.function.Function"))
C(crb, "public ClassRb() { }")
F(crb, "public static final java.util.concurrent.atomic.AtomicLong APPLIED = new java.util.concurrent.atomic.AtomicLong();")
F(crb, "public static volatile int FAIL_WRITE = 0;")   # HARNESS SEAM ONLY: the next N commit writes answer failed
M(crb, r"""
public static java.nio.file.Path home() {
  java.nio.file.Path d = @PKG@.AbilStore.DIR;
  return d == null ? null : d.getParent();
}""")
M(crb, r"""
public static boolean validKey(String k) {
  return k != null && k.length() >= 36 && k.length() <= 48 && k.matches("[0-9a-fA-F-]{36}(-p[0-9]{1,4})?");
}""")
M(crb, r"""
public static boolean validTx(String tx) {
  return tx != null && tx.matches("tx[0-9]{13}-[0-9a-f]{6}");
}""")
M(crb, r"""
public static java.util.UUID owner(String k) {
  try { return java.util.UUID.fromString(k.substring(0, 36)); } catch (Throwable t) { return null; }
}""")
M(crb, r"""
public static java.nio.file.Path staged(String k, String tx) {
  return home().resolve("rebirth").resolve(k + ".rb-" + tx + ".properties");
}""")
M(crb, r"""
public static void writeProps(java.nio.file.Path f, java.util.Properties p, String comment) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try { p.store(out, comment); out.flush(); out.getFD().sync(); } finally { out.close(); }
  try { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
  catch (java.nio.file.AtomicMoveNotSupportedException e) { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
}""")
M(crb, r"""
public static java.util.Properties readProps(java.nio.file.Path f) {
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    return p;
  } catch (Throwable t) { return null; }
}""")
M(crb, r"""
public static void deleteTree(java.io.File f) {
  if (f == null) return;
  java.io.File[] c = f.listFiles();
  if (c != null) for (int i = 0; i < c.length; i++) deleteTree(c[i]);
  f.delete();
}""")
M(crb, r"""
public static String decision(String tx) {
  try {
    Object f = @PKG@.ClassCfg.bridge().get("rebirth:fn:decision");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(tx);
      if (r instanceof String) return (String) r;
    }
  } catch (Throwable t) { }
  return "unknown";
}""")
M(crb, r"""
public static String cleanStale(String k, String tx) {
  java.io.File[] fs = home().resolve("rebirth").toFile().listFiles();
  if (fs == null) return null;
  String pre = k + ".rb-";
  for (int i = 0; i < fs.length; i++) {
    String nm = fs[i].getName();
    if (!nm.startsWith(pre)) continue;
    String old;
    if (nm.endsWith(".properties")) old = nm.substring(pre.length(), nm.length() - 11);
    else if (nm.endsWith(".properties.tmp")) old = nm.substring(pre.length(), nm.length() - 15);
    else continue;
    if (old.equals(tx)) continue;
    if ("commit".equals(decision(old))) return "err:an older rebirth of this profile is still finishing (" + old + ")";
    fs[i].delete();
  }
  return null;
}""")
M(crb, r"""
public static String committed(String k) {
  return @PKG@.AbilStore.load(k).getProperty("rb.lastTx", "");
}""")
M(crb, r"""
public static void backup(String k, String tx, java.util.Properties cur) throws java.io.IOException {
  java.nio.file.Path dir = home().resolve("rebirth-backup").resolve(k);
  java.util.Properties p = new java.util.Properties();
  p.putAll(cur);
  writeProps(dir.resolve(tx).resolve(k + ".properties"), p, "SkyyClasses rebirth backup of abilities/" + k + ".properties before " + tx + " - restore by hand while the server is stopped");
  java.io.File[] all = dir.toFile().listFiles();
  if (all == null || all.length <= 3) return;
  java.util.Arrays.sort(all);
  for (int i = 0; i < all.length - 3; i++) deleteTree(all[i]);
}""")
M(crb, r"""
public static String prepare(String k, String tx, boolean write) {
  java.util.UUID u = owner(k);
  if (u == null) return "err:bad profile key";
  if (!k.equals(@PKG@.ClassCfg.pkey(u))) return "err:the profile " + k + " is not the active one";
  int ci = @PKG@.ClassStore.classIndex(u);
  if (tx.equals(committed(k))) return "err:already committed";
  java.util.Properties cur = @PKG@.AbilStore.load(k);
  if (@PKG@.AbilStore.FAILAT.get(k) != null) return "err:the ability file of " + k + " cannot be read";
  int cl = ci < 0 ? 0 : @PKG@.Abil.level(u, ci);
  java.util.Properties sp = new java.util.Properties();
  int n = 0;
  for (int ai = 0; ai < @PKG@.AbilDefs.IDS.length; ai++) {
    if (ci < 0 || @PKG@.AbilDefs.CLS[ai] != ci) continue;
    String id = @PKG@.AbilDefs.IDS[ai];
    int l = @PKG@.Abil.alvlk(k, @PKG@.Abil.numOf(cur, "u." + id));
    long old = @PKG@.Abil.numOf(cur, "rb.S." + id);
    sp.setProperty("rb.S." + id, String.valueOf((long) l > old ? (long) l : old));
    n++;
  }
  String facts = "ok:classLvl=" + cl + ";abilities=" + n;
  if (!write) return facts;
  String stl = cleanStale(k, tx);
  if (stl != null) return stl;
  try {
    backup(k, tx, cur);
    sp.setProperty("rb.Lr", String.valueOf(cl));
    sp.setProperty("tx", tx);
    sp.setProperty("pkey", k);
    sp.setProperty("class", ci < 0 ? "" : @PKG@.ClassDefs.NAMES[ci]);
    writeProps(staged(k, tx), sp, "SkyyClasses rebirth " + tx + " - staged (the ability file is untouched until the commit)");
  } catch (Throwable t) { return "err:could not write the staged file: " + t; }
  return facts;
}""")
M(crb, r"""
public static boolean flush(String k) {
  if (FAIL_WRITE > 0) { FAIL_WRITE = FAIL_WRITE - 1; return false; }
  return @PKG@.AbilSave.writeSync(k);
}""")
M(crb, r"""
public static String commit(String k, String tx) {
  java.util.UUID u = owner(k);
  if (u == null) return "err:bad profile key";
  java.nio.file.Path sp = staged(k, tx);
  if (tx.equals(committed(k))) {
    if (!flush(k)) return "err:could not save the ability file of " + k + " (retried)";
    try { java.nio.file.Files.deleteIfExists(sp); } catch (Throwable t) { }
    return "done";
  }
  java.util.Properties p = readProps(sp);
  if (p == null || !tx.equals(p.getProperty("tx"))) return "err:no staged file for " + tx;
  @PKG@.AbilStore.load(k);
  if (@PKG@.AbilStore.FAILAT.get(k) != null) return "err:the ability file of " + k + " cannot be read";
  java.util.ArrayList ks = new java.util.ArrayList();
  java.util.ArrayList vs = new java.util.ArrayList();
  java.util.ArrayList pk = new java.util.ArrayList();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String key = (String) it.next();
    if (!key.startsWith("rb.S.")) continue;
    String id = key.substring(5);
    ks.add(key);
    vs.add(p.getProperty(key));
    pk.add("rb.pick." + id);   // FIX (critic): + 1 inside AbilStore.setAdd's lock (a Max Up can no longer slip between read and write)
  }
  ks.add("rb.Lr");
  vs.add(p.getProperty("rb.Lr", "0"));
  ks.add("rb.lastTx");
  vs.add(tx);
  String[] ka = new String[ks.size()];
  String[] va = new String[vs.size()];
  for (int i = 0; i < ka.length; i++) { ka[i] = (String) ks.get(i); va[i] = (String) vs.get(i); }
  String[] pa = new String[pk.size()];
  long[] pd = new long[pk.size()];
  for (int i = 0; i < pa.length; i++) { pa[i] = (String) pk.get(i); pd[i] = 1L; }
  if (@PKG@.AbilStore.setAdd(k, ka, va, pa, pd) <= 0) return "err:the ability file of " + k + " cannot be read";
  if (!flush(k)) {
    @PKG@.AbilStore.markDirty(k);
    return "err:could not save the ability file of " + k + " (the change is in memory; retried)";
  }
  try { java.nio.file.Files.deleteIfExists(sp); } catch (Throwable t) { }
  @PKG@.AbilStore.RBN.remove(k);
  APPLIED.incrementAndGet();
  return "ok";
}""")
M(crb, r"""
public static String abort(String k, String tx) {
  if (tx.equals(committed(k))) return "err:already committed";
  try {
    java.nio.file.Path sp = staged(k, tx);
    java.nio.file.Files.deleteIfExists(sp);
    java.nio.file.Files.deleteIfExists(sp.resolveSibling(sp.getFileName().toString() + ".tmp"));
  } catch (Throwable t) { return "err:" + t; }
  return "done";
}""")
M(crb, r"""
public static String status(String k, String tx) {
  if (tx.equals(committed(k))) return "committed";
  return java.nio.file.Files.exists(staged(k, tx), new java.nio.file.LinkOption[0]) ? "staged" : "none";
}""")
M(crb, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return "err:bad arguments";
    Object[] a = (Object[]) o;
    if (a.length < 3 || !(a[0] instanceof String) || !(a[1] instanceof String) || !(a[2] instanceof String)) return "err:bad arguments";
    String op = (String) a[0];
    String k = ((String) a[1]).trim();
    String tx = (String) a[2];
    if (!validKey(k)) return "err:bad profile key";
    if (!validTx(tx)) return "err:bad txid";
    if (@PKG@.AbilStore.DIR == null || home() == null) return "err:SkyyClasses is not started";
    if ("measure".equals(op)) return prepare(k, tx, false);
    if ("prepare".equals(op)) return prepare(k, tx, true);
    if ("commit".equals(op)) return commit(k, tx);
    if ("abort".equals(op)) return abort(k, tx);
    if ("status".equals(op)) return status(k, tx);
    return "err:unknown op " + op;
  } catch (Throwable t) { return "err:" + t; }
}""")
# THE LATE BODIES (every class above exists now)
for _src in ABIL_LATE:''')
rep('''          abmods, abctx, abrune, abinv, abrc, abmt, abic, abpf, abmf, abdf, abuf):   # 0.1.22: + the rune route, levels, modifiers, panel''',
    '''          abmods, abctx, abrune, abinv, abrc, abmt, abic, abpf, abmf, abdf, abuf,   # 0.1.22: + the rune route, levels, modifiers, panel
          crb):                          # 0.1.23: + the rebirth participant''')
rep('''  try { @PKG@.ClassCfg.bridge().remove("tree:reads:SkyyClasses"); } catch (Throwable t) { }   // 0.1.22: the reader list it put''',
    '''  try { @PKG@.ClassCfg.bridge().remove("tree:reads:SkyyClasses"); } catch (Throwable t) { }   // 0.1.22: the reader list it put
  try { @PKG@.ClassCfg.bridge().remove("rebirth:part:classes"); } catch (Throwable t) { }   // 0.1.23''')
rep('''the SkyyTrees ability panel bridges; bridge class:fn:loadoutGet''',
    '''the SkyyTrees ability panel bridges, Monk + Assassin abilities, rebirth participant rebirth:part:classes; bridge class:fn:loadoutGet''')
rep('''Mage Meteor, Mana Barrier, Frost Nova, Starfall or Arcane Beam; Priest Sacred Heal, Shield Bubble, the Guardian Spirit passive, Sanctuary or Martyr's Grace; sprinting''',
    '''Mage Meteor, Mana Barrier, Frost Nova, Starfall or Arcane Beam; Priest Sacred Heal, Shield Bubble, the Guardian Spirit passive, Sanctuary or Martyr's Grace; Monk Flowing Form, Palm Strike, Cyclone Kick, Hundred Fists or Still Water; Assassin Cloak + First Strike, Toxin, God Killer, Vanishing Act; sprinting''')
# the engine name the losing-a-target code needs
rep('''    "VTS":  "com.hypixel.hytale.protocol.VelocityThresholdStyle",''',
    '''    "VTS":  "com.hypixel.hytale.protocol.VelocityThresholdStyle",
    "MES":  "com.hypixel.hytale.server.npc.role.support.MarkedEntitySupport",   # 0.1.23: an NPC's targets (Awe, the cloak, the smoke)''')

# ================================================================================================ 0.1.23: the 64 KB cap - walking cost rows only, AbilNum
NEWA = ["FlowingForm", "PalmStrike", "CycloneKick", "HundredFists", "StillWater", "CloakFirstStrike", "Toxin", "GodKiller", "VanishingAct"]
rep('''        if _k == 0 and _id in ("Meteor", "ManaBarrier", "SacredHeal", "ShieldBubble"):
            continue          # their walking rows exist since 0.1.16 / 0.1.17 (same keys, same numbers - asserted below)''',
    '''        if _k == 0 and _id in ("Meteor", "ManaBarrier", "SacredHeal", "ShieldBubble"):
            continue          # their walking rows exist since 0.1.16 / 0.1.17 (same keys, same numbers - asserted below)
        if _k > 0 and _id in NEW_ABIL_IDS:
            continue          # 0.1.23: the walking rows only (the 64 KB cap) - the other shapes follow them (AbilDefs.scale)''')
rep('''_SPLIT = {"Mage": (0.78, 0.22), "Priest": (0.73, 0.27), "Monk": (0.38, 0.62), "Assassin": (0.43, 0.57)}   # 0.1.23: + Monk, Assassin''',
    '''_SPLIT = {"Mage": (0.78, 0.22), "Priest": (0.73, 0.27), "Monk": (0.38, 0.62), "Assassin": (0.43, 0.57)}   # 0.1.23: + Monk, Assassin
NEW_ABIL_IDS = %r   # 0.1.23: their sprint / air / crouch costs are the plan's numbers scaled by the walking row''' % NEWA)
rep('''        _l.append("  if (ai == %d) { if (sh == 1) return @PKG@.AbilCfg.%s_%s_SP; if (sh == 2) return @PKG@.AbilCfg.%s_%s_AI; if (sh == 3) return @PKG@.AbilCfg.%s_%s_CR; return @PKG@.AbilCfg.%s_%s; }"
                  % (_i, _p, kind, _p, kind, _p, kind, _p, kind))''',
    '''        if _id in NEW_ABIL_IDS:   # 0.1.23: the walking row + the plan's shape numbers (scaled / shifted with it)
            _pk = PLAN_43[_id]
            _ix = {"MANA": 0, "STAM": 1, "CD": 2}[kind]
            if kind == "CD":
                _l.append("  if (ai == %d) { double w = @PKG@.AbilCfg.%s_CD; if (sh == 1) return shift(w, %r); if (sh == 2) return shift(w, %r); if (sh == 3) return shift(w, %r); return w; }"
                          % (_i, _p, float(_pk[1][2] - _pk[0][2]), float(_pk[2][2] - _pk[0][2]), float(_pk[3][2] - _pk[0][2])))
            else:
                _l.append("  if (ai == %d) { double w = @PKG@.AbilCfg.%s_%s; if (sh == 1) return scale(w, %r, %r); if (sh == 2) return scale(w, %r, %r); if (sh == 3) return scale(w, %r, %r); return w; }"
                          % (_i, _p, kind, float(_pk[0][_ix]), float(_pk[1][_ix]), float(_pk[0][_ix]), float(_pk[2][_ix]), float(_pk[0][_ix]), float(_pk[3][_ix])))
            continue
        _l.append("  if (ai == %d) { if (sh == 1) return @PKG@.AbilCfg.%s_%s_SP; if (sh == 2) return @PKG@.AbilCfg.%s_%s_AI; if (sh == 3) return @PKG@.AbilCfg.%s_%s_CR; return @PKG@.AbilCfg.%s_%s; }"
                  % (_i, _p, kind, _p, kind, _p, kind, _p, kind))''')
rep('''M(abdefs, _cost_java("manaOf", "MANA"))''', '''# 0.1.23: a shape's cost = the plan's number x (the walking row / the plan's walking number), at least 1 while the row is above 0;
# a shape's cooldown = the walking row + the plan's difference (never below 0)
M(abdefs, r"""
public static double scale(double w, double b0, double b) {
  if (!(w > 0.0)) return 0.0;
  if (!(b0 > 0.0)) return w;
  double v = Math.floor(w * b / b0 + 0.5);
  return v < 1.0 ? 1.0 : v;
}""")
M(abdefs, r"""
public static double shift(double w, double d) {
  double v = w + d;
  return v < 0.0 ? 0.0 : v;
}""")
M(abdefs, _cost_java("manaOf", "MANA"))''')
rep('''        _mm = _ROWV["ab.%s.%s.mana" % (_a[0], _sh)] + (_ROWV["ab.ManaBarrier.keep"] if _a[0] == "ManaBarrier" else 0.0)
        assert _mm <= _pm and _ROWV["ab.%s.%s.stamina" % (_a[0], _sh)] <= _ps, "%s %s not affordable at its unlock" % (_a[0], _sh)''',
    '''        _k_ = SHAPES.index(_sh)
        _mm = _ROWV.get("ab.%s.%s.mana" % (_a[0], _sh), PLAN_43[_a[0]][_k_][0]) + (_ROWV["ab.ManaBarrier.keep"] if _a[0] == "ManaBarrier" else 0.0)
        assert _mm <= _pm and _ROWV.get("ab.%s.%s.stamina" % (_a[0], _sh), PLAN_43[_a[0]][_k_][1]) <= _ps, "%s %s not affordable at its unlock" % (_a[0], _sh)''')
# AbilNum: the numbers of the 9 abilities, parsed from their text rows (sync() when a row's text changed - one identity compare each)
rep('''abdefs = pool.makeClass(PKG + ".AbilDefs")
F(abdefs, "public static final String[] IDS = %s;" % jarr([a[0] for a in ABILS]))''', '''# 0.1.23 AbilNum: the Monk + Assassin numbers (ab.<Ability>.numbers text rows -> fields), its own class (the 64 KB cap)
abnum = pool.makeClass(PKG + ".AbilNum")
for _row in NUM_ROWS:
    if _row[2] == "int":
        F(abnum, "public static volatile long %s = %dL;" % (_row[1], int(_row[3])))
    else:
        F(abnum, "public static volatile double %s = %r;" % (_row[1], float(_row[3])))
for _aid in NUM_ABILS:
    F(abnum, "public static volatile String S_%s = null;" % [r_ for r_ in NUM_ROWS if r_[0].split(".")[1] == _aid][0][1].split("_")[0])
M(abnum, r"""
public static java.util.HashMap parse(String t) {
  java.util.HashMap m = new java.util.HashMap();
  if (t == null) return m;
  String[] p = t.split(",");
  for (int i = 0; i < p.length; i++) {
    int e = p[i].indexOf('=');
    if (e <= 0) continue;
    m.put(p[i].substring(0, e).trim(), p[i].substring(e + 1).trim());
  }
  return m;
}""")
M(abnum, r"""
public static double d(java.util.HashMap m, String k, double dflt, double lo, double hi) {
  Object o = m.get(k);
  if (!(o instanceof String)) return dflt;
  try {
    double v = Double.parseDouble((String) o);
    if (v != v || Double.isInfinite(v)) return dflt;
    if (v < lo) v = lo;
    if (v > hi) v = hi;
    return v;
  } catch (Throwable t) { return dflt; }
}""")
M(abnum, r"""
public static long l(java.util.HashMap m, String k, long dflt, long lo, long hi) {
  Object o = m.get(k);
  if (!(o instanceof String)) return dflt;
  try {
    long v = Math.round(Double.parseDouble((String) o));
    if (v < lo) v = lo;
    if (v > hi) v = hi;
    return v;
  } catch (Throwable t) { return dflt; }
}""")


def _sync_java():
    _l = ["public static void sync() {"]
    for _aid in NUM_ABILS:
        _rs = [r_ for r_ in NUM_ROWS if r_[0].split(".")[1] == _aid]
        _pre = _rs[0][1].split("_")[0]
        _l.append("  String t%s = @PKG@.AbilCfg.%s_NUMS;" % (_pre, _pre))
        _l.append("  if (t%s != S_%s) {" % (_pre, _pre))
        _l.append("    java.util.HashMap m%s = parse(t%s);" % (_pre, _pre))
        for r_ in _rs:
            _lo = float(r_[4]) if r_[4] != "" else 0.0
            _hi = float(r_[5]) if r_[5] != "" else 1.0E9
            if r_[2] == "int":
                _l.append("    %s = l(m%s, %s, %dL, %dL, %dL);" % (r_[1], _pre, jstr(r_[0].split(".")[2]), int(r_[3]), int(_lo), int(_hi)))
            else:
                _l.append("    %s = d(m%s, %s, %r, %r, %r);" % (r_[1], _pre, jstr(r_[0].split(".")[2]), float(r_[3]), _lo, _hi))
        _l.append("    S_%s = t%s;" % (_pre, _pre))
        _l.append("  }")
    _l.append("}")
    return "\\n".join(_l)


M(abnum, _sync_java())
abdefs = pool.makeClass(PKG + ".AbilDefs")
F(abdefs, "public static final String[] IDS = %s;" % jarr([a[0] for a in ABILS]))''')
rep('''          crb):                          # 0.1.23: + the rebirth participant''', '''          crb, abnum):                   # 0.1.23: + the rebirth participant, the Monk + Assassin numbers''')
# every 0.1.23 number moved into AbilNum: the Java reads @PKG@.AbilNum.<FIELD> (the fields of the _n rows of this patch)
_MOVED = re.findall(r'^_n\("ab\.[A-Za-z]+\.[A-Za-z]+", "([A-Z0-9_]+)"', open(__file__, encoding="utf8").read(), re.M)
assert len(_MOVED) == 88 and len(set(_MOVED)) == 88, len(_MOVED)
s = re.sub(r"@PKG@\.AbilCfg\.(%s)\b" % "|".join(_MOVED), r"@PKG@.AbilNum.\1", s)
CHANGES.append(("AbilNum", "AbilCfg"))
# AbilNum.sync() where the numbers are first read: a cast (castAt0), a cast context (ctxFor), the panel texts (modText)
rep('''public static String castAt0(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg, int forced, int door) {
  if (pr == null || st == null || ref == null || !ref.isValid()) return "bad";''', '''public static String castAt0(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg, int forced, int door) {
  if (pr == null || st == null || ref == null || !ref.isValid()) return "bad";
  @PKG@.AbilNum.sync();   // 0.1.23''')
rep('''public static @PKG@.AbilCtx ctxFor(java.util.UUID u, String k, int ai, int sh, String csv) {
  @PKG@.AbilCtx c = new @PKG@.AbilCtx();''', '''public static @PKG@.AbilCtx ctxFor(java.util.UUID u, String k, int ai, int sh, String csv) {
  @PKG@.AbilNum.sync();   // 0.1.23
  @PKG@.AbilCtx c = new @PKG@.AbilCtx();''')
rep('''public static String modText(int ai, int mi, int lvl, int cnt) {
  if (ai < 0 || mi < 0 || lvl <= 0) return "";''', '''public static String modText(int ai, int mi, int lvl, int cnt) {
  if (ai < 0 || mi < 0 || lvl <= 0) return "";
  @PKG@.AbilNum.sync();   // 0.1.23''')

# ================================================================================================ FIX ROUND (critics 2026-10-14)
# C4: the /abilities subtitle still named only the Mage and the Priest
rep('''  String sub = !has ? (ci < 0 ? @PKG@.Abil.noClass() : @PKG@.ClassDefs.NAMES[ci] + " abilities are coming later - the Mage and the Priest get theirs first.")''',
    '''  String sub = !has ? (ci < 0 ? @PKG@.Abil.noClass() : @PKG@.ClassDefs.NAMES[ci] + " abilities come in a later update (the Mage, Priest, Monk and Assassin have theirs).")''')
assert "the Mage and the Priest get theirs first" not in s
# B7: AbilFrostSys now carries the Monk combo, the uncloak and Slip Away - say so when it cannot register; FROST_ON for abil info
rep('''  try { getEntityStoreRegistry().registerSystem(new @PKG@.AbilFrostSys()); }   // 0.1.18: a landed hit breaks a Frost Nova freeze (Inspect group)
  catch (Throwable t3) { @PKG@.ClassCfg.warn("could not register AbilFrostSys - Frost Nova freezes run their full time this start: " + t3); }''',
    '''  try { getEntityStoreRegistry().registerSystem(new @PKG@.AbilFrostSys()); @PKG@.Abil.FROST_ON = true; }   // 0.1.18: a landed hit breaks a Frost Nova freeze (Inspect group)
  catch (Throwable t3) { @PKG@.ClassCfg.warn("could not register AbilFrostSys - this start: Frost Nova freezes run their full time, NO Monk combo stacks (Flowing Form / Hundred Fists), attacks do not break the cloak, NO Slip Away: " + t3); }''')
rep('''" | last: " + LAST_MONK + " / " + LAST_ASN + " | rebirth: " + rbLine(@PKG@.ClassCfg.pkey(t)), null);''',
    '''" | last: " + LAST_MONK + " / " + LAST_ASN + " | rebirth: " + rbLine(@PKG@.ClassCfg.pkey(t)) + (FROST_ON ? "" : " | LANDED-HIT HOOK OFF (no combo / uncloak / Slip Away)"), null);''')
# B5: the mob maps pruned once a second (the first player of any world tick)
rep('''  try {
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(store);
    if (aw == null || aw.idle()) return;''',
    '''  try {
    long nowP = System.currentTimeMillis();   // FIX (critic): expired / dead mob entries leave the Monk / Assassin maps once a second
    if (nowP >= @PKG@.Abil.NEXT_PRUNE) @PKG@.Abil.pruneMobs(nowP);
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(store);
    if (aw == null || aw.idle()) return;''')
# C6: the Monk / Assassin walking cost rows say their other shapes follow them
rep('''_lab + " Mana", "Mana per cast of this shape."))''',
    '''_lab + " Mana", ("Walking shape; sprint / air / crouch Mana scale with this row." if _id in NEW_ABIL_IDS else "Mana per cast of this shape.")))''')
rep('''_lab + " Stamina", "Stamina per cast of this shape."))''',
    '''_lab + " Stamina", ("Walking shape; sprint / air / crouch Stamina scale with this row." if _id in NEW_ABIL_IDS else "Stamina per cast of this shape.")))''')
rep('''"live", _lab + " cooldown", "Seconds before the ability can be cast again after this shape."))''',
    '''"live", _lab + " cooldown", ("Walking shape; sprint / air / crouch cooldowns move with this row." if _id in NEW_ABIL_IDS else "Seconds before the ability can be cast again after this shape.")))''')

# ================================================================================================ done
assert s.count("registerCommand(") == REG0, "no new command"
assert s.count("registerSystem(") == SYS0, "no new system"
for _old_new in CHANGES:
    pass
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote %s (%d changes, %d lines)" % (dst, len(CHANGES), s.count(LF)))
