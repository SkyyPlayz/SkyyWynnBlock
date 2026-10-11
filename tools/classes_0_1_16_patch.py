"""Derive SkyyClasses/build_skyyclasses_0.1.16.py from the CURRENT generated 0.1.15 (build_skyyclasses_0.1.15.py = the tools/deploy_set.py
SET pin). Run:  python tools/classes_0_1_16_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.16.py   then
                python SkyyClasses/test_skyyclasses_0.1.16.py --dir <tools/dev/scratch/...>   (never --deploy: coordinated deploy)
EDITED-SCRIPTS RULE (commit ab75b6c): the lineage is Skyy's EDITED 0.1.6 -> classes_0_1_7_patch.py -> ... -> classes_0_1_15_patch.py -> the
generated 0.1.15 read here; tools/classes_0_1_6_patch.py is NEVER re-run. Edit THIS file, never the generated build script.

0.1.16 = THE CLASS ABILITY ENGINE, ROUND R1 (research/cloud/Ability-Engine-Plan.md section 8 R1; engine design
research/cloud/Class-Ability-Engine-Spec.md; keys research/cloud/Ability-Input-Design.md; numbers research/cloud/Class-Ability-Spec-Draft.md
section 2 after the 2026-10-08 power split, research/Class-Power-Split.md). Skyy's locks (docs/answered/classes.md):
  "we decided 4 ability's, 2 active at a time. the 2 you pick are your primary ability's, and work when walking or sprinting. thew other
   2 are set to crouch. so crouching uses your alt ability's."  + popup batch 6 unlock levels 1/10/20/30 (A1 1, A2 10, A2-alt 20,
   A1-alt 30) + Mana AND Stamina costs by the class split (Mage 78/22, Priest 73/27), every ability affordable at unlock.
  Plan defaults ACCEPTED (task): /cast until Hytale 0.7's rune keys; an admin grant for the Lv 10+ abilities (testing); an ability keeps
  working after a weapon swap - the weapon is checked at the CAST only.
WHAT IS NEW
  - AbilDefs = the registry: the 5 designed abilities of the Mage (Meteor A1, Mana Barrier A2, Frost Nova A2-alt, Starfall / Arcane Beam
    A1-alt A / B) and the Priest (Sacred Heal, Shield Bubble, Guardian Spirit = passive, Sanctuary / Martyr's Grace). BUILT in R1: Meteor +
    Sacred Heal (WALKING shape = every shape until R5). The others answer "comes in a later update" (nothing spent).
  - Owned by class level (skill:fn:level, the class skill): A1 at 1, A2 at 10, A2-alt at 20, A1-alt at 30 (rows abil.unlock.*); the A1-alt
    pick (A / B) is the loadout key alt (default A; the Abilities page comes in R7). /classadmin abil <player> grant owns all four.
  - Loadout per PROFILE (tools/PROFILES-CONTRACT.md rules 1 + 2): Skyy_SkyyClasses/abilities/<pkey>.properties (p1, p2 = the 2 primaries,
    a1, a2 = the 2 crouch alts, alt = the A1-alt pick, grant = admin grant); no file = the defaults (p1 A1, p2 A2, a1 A2-alt, a2 A1-alt).
    Cache keyed by the pkey String; atomic tmp + move writes off the world thread; an unreadable file is never overwritten. /cast swap
    swaps the two primaries (out of combat only - skill:fn:combat).
  - /cast 1 | /cast 2 = your primaries; CROUCH held at the cast = the alt on that key (Skyy's lock); /cast 3 | 4 (alt1 | alt2) = the alts
    directly (typing a command while crouched may not be possible - UNVERIFIED); /cast or /cast list = the list; /cast swap.
  - The pipeline (engine spec 4): part on -> slot -> profile not busy -> class -> class has abilities -> alive -> crouch -> owned -> built
    -> the class's OWN weapon in the main hand (ClassRules.allowed AND the item belongs to the class) -> cooldown -> Mana AND Stamina
    (creative free) -> the target (Meteor: a spot within its range) -> world list not full -> PAY (subtractStatValue) -> arm the cooldown
    -> run. Refusals cost nothing, start no cooldown and send at most one line per abil.refuse seconds.
  - Cooldowns: memory only, key pkey|ability (a relog keeps them, a profile has its own, a server restart resets - engine spec Q5).
  - METEOR: a spot within ab.Meteor.range (25) blocks (TargetUtil.getTargetLocation); a warning burst there (vanilla Fire_AoE_Spawn);
    ab.Meteor.delay (1 s) later an explosion (vanilla Explosion_Medium) and ab.Meteor.power (3.0) x H damage to every NPC enemy within
    ab.Meteor.radius (4) blocks: H = one charged shot of the staff / wand held at the cast (armory:fn:info charged damage x its tune %),
    abil.hitFallback (25) for weapons SkyyArmory does not know. Damage$EntitySource(caster), cause PROJECTILE, through executeDamage =
    the whole damage pipeline. Players are never hit (no PvP from abilities in R1).
  - SACRED HEAL: everyone within ab.SacredHeal.radius (9) blocks: ab.SacredHeal.heal (25) % of their max Health, the Priest +selfBonus
    (20) % more, players outside the party priestHeal.othersPercent; then a heal over time of ab.SacredHeal.hot (40) % of that instant
    heal over ab.SacredHeal.hotTime (4) s, the targets picked at the cast. Its own cap channel: abil.healCap (60) % of max Health per
    target per cast (no HealBudget). Divinity XP through skill:fn:healxp (others / self rate), the heal chat lines (HealMsg).
  - AbilTick = an EntityTickingSystem on Player (isParallel false, once per world tick - the SkyyArmory TravTick pattern) runs the
    delayed jobs (Meteor impact, heal-over-time pulses) on the world thread; AbilWorld = one job list per world (at most abil.maxLive, 48).
  - DAMAGE TAG (plan 4.2 finding): every Damage the engine creates is put in AbilDmg.TAG (a weak identity map, Damage has no equals);
    DamageLock skips tagged damage, so a Meteor still hurts after the Mage swapped to food. Bridge class:fn:abilhit apply(Object damage)
    -> UUID caster or null: SkyySkills 0.4.28 credits the KILL XP of tagged damage to the caster's class skill without the held-item test
    (VERIFIED in HytaleServer.jar: executeDamage invokes the event with the SAME Damage object and DamageSystems$ApplyDamage hands that
    object to DeathComponent.tryAddComponent = KillSys' getDeathInfo()).
  - Bridge class:fn:abil apply(UUID) -> Object[16] = 4 x {String name, Long msLeft, Long msTotal, String state} for p1, p2, a1, a2
    (state ready / cooldown / locked / soon / passive / empty) - SkyyHud's Abilities widget (R2); null without a class with abilities.
  - Server Setup -> Classes: categories Abilities (part.abilities, abil.creativeFree, abil.castChat, abil.refuse, abil.healCap,
    abil.unlock.a1 / a2 / a2alt / a1alt, abil.hitFallback) + Ability numbers (ab.Meteor.walk.mana / .stamina / .cooldown, power, radius,
    delay, range; ab.SacredHeal.walk.mana / .stamina / .cooldown, heal, selfBonus, radius, hot, hotTime). Times in seconds. No
    migration: a missing key reads its default. Player switch classes.abilChat (cast + hit lines; refusals always show).
  - /classadmin abil <player> grant | ungrant | reset (cooldowns) | info.
  - Particles reuse VANILLA ids only (no asset pack); the build proves each is a finite one-shot particle system in Assets.zip.
NOT IN R1: shapes other than walking (R5), the HUD widget (SkyyHud R2), zones / Mana Barrier / Shield Bubble (R3), rune keys (R4), the
  Abilities page (R7), Echo / levels by use (R8), PvP damage from abilities.
FIX ROUND (2026-10-09, three critics): the job keeps the caster's profile key - a profile switch before the Meteor impact = nobody hurt, during
  the heal over time = heals but no XP; a cached ability-file read takes no lock and the write + its retry sleep run on the AbilSave monitor
  (the world thread never waits on disk); DIRTY keys - a failed write is retried 5 s later (5 tries) and the plugin's shutdown flushes what
  is left; an executor that throws after the payment refunds Mana + Stamina + the cooldown (the Meteor job is queued last); Sacred Heal with
  nobody hurt in range is a refusal (nothing spent); rows abil.maxLive (48, 8-256) and abil.safeWords (the SkyyArmory grapple.noYankWords
  default: pets / mounts / traders are never hit); refusals play the vanilla fail sound SFX_Bow_No_Ammo (2D, the caster only).
FIX ROUND 2 (2026-10-09, second critics): a cost whose stat (Mana / Stamina) cannot be read is a refusal ("nostats", never a free cast);
  Sacred Heal does every fallible step (party checks, amounts, the heal-over-time job) BEFORE the first heal, and an error after the first
  heal ends the cast there (no refund, no XP for the unfinished cast); a job more than 30 s past its time is dropped unrun (a world that
  emptied right after a cast - no stale Meteor minutes later; it also stops counting toward abil.maxLive); /cast swap needs both primaries
  owned; a spellbook's H = the same-metal SkyyArmory staff (Weapon_Spellbook_<Metal> -> Weapon_Staff_<Metal>); row abil.cdMessage (off =
  the cooldown refusal is the click only). Rows abil.input (R4 rune keys) and abil.tick (R3 zones / auras) wait for the rounds that use them.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.15.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.16.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.15"' in s and "GENERATED by tools/classes_0_1_15_patch.py from the generated 0.1.14" in s, \
    "build_skyyclasses_0.1.15.py is not the generated 0.1.15"
assert "DEF_HEAL_MSG_MS = 10000   # LOCKED Skyy 2026-09-25" in s and "DEF_HEAL_SELF_PCT = 100 " in s, "0.1.15 is not the edited-lineage script"
assert "AbilDefs" not in s and "class:fn:abil" not in s
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


# ================================================================================================ docstring, Run line, version
rep('''"""SkyyClasses 0.1.15 - build script (javassist via jpype). GENERATED by tools/classes_0_1_15_patch.py from the generated 0.1.14 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_14_patch.py -> 0.1.14) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.16 - build script (javassist via jpype). GENERATED by tools/classes_0_1_16_patch.py from the generated 0.1.15 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_15_patch.py -> 0.1.15) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
0.1.16 (2026-10-09; research/cloud/Ability-Engine-Plan.md round R1; Skyy LOCKED 4 abilities / 2 primary + 2 crouch alts, unlock 1/10/20/30):
  THE CLASS ABILITY ENGINE - /cast 1 | 2 (crouch = the alt on that key), /cast 3 | 4, /cast list, /cast swap; registry of the Mage +
  Priest kits (Meteor + Sacred Heal BUILT, walking shape); loadout per profile (Skyy_SkyyClasses/abilities/<pkey>.properties); Mana +
  Stamina costs, memory cooldowns per profile; AbilTick (world-thread delayed jobs); ability damage tagged (DamageLock skips it; kill XP
  via class:fn:abilhit -> SkyySkills 0.4.28); bridges class:fn:abil (HUD) + class:fn:abilhit; /classadmin abil; Server Setup ->
  Classes -> Abilities + Ability numbers (no migration). Full notes in tools/classes_0_1_16_patch.py.
  FIX ROUND: profile key on delayed jobs, lock-free cached reads, dirty-file retry + shutdown flush, refund on a failed cast, Sacred Heal
  needs someone hurt, abil.maxLive + abil.safeWords rows, the refusal fail sound.
  FIX ROUND 2: unreadable Mana / Stamina = refusal; Sacred Heal prepares before healing; stale jobs dropped; swap needs both primaries;
  spellbook H = the same-metal staff; row abil.cdMessage.
''')
rep('''Run:   python build_skyyclasses_0.1.15.py           -> SkyyClasses/SkyyClasses-0.1.15.jar''',
    '''Run:   python build_skyyclasses_0.1.16.py           -> SkyyClasses/SkyyClasses-0.1.16.jar''')
rep('VERSION = "0.1.15"\n', 'VERSION = "0.1.16"\n')
rep('''      Atomic writes (tmp + move).
"""''', '''      0.1.16: Skyy_SkyyClasses/abilities/<pkey>.properties (p1, p2, a1, a2 = ability ids of the 4 slots, alt = A / B the A1-alt pick,
      grant = true when an admin granted all four; no file = the defaults; written by /cast swap and /classadmin abil).
      Atomic writes (tmp + move).
"""''')

# ================================================================================================ Python tables (before CFG_LINES)
ABIL_PY = r'''
# =====================================================================================================================
# 0.1.16: THE ABILITY ENGINE, round R1 (research/cloud/Ability-Engine-Plan.md; tools/classes_0_1_16_patch.py has the notes)
# =====================================================================================================================
# (id, display name, class, tier, built, passive): tier 0 = A1, 1 = A2, 2 = A2-alt, 3 = A1-alt A, 4 = A1-alt B (picking A locks out B)
ABILS = [
    ("Meteor", "Meteor", "Mage", 0, True, False),
    ("ManaBarrier", "Mana Barrier", "Mage", 1, False, False),
    ("FrostNova", "Frost Nova", "Mage", 2, False, False),
    ("Starfall", "Starfall", "Mage", 3, False, False),
    ("ArcaneBeam", "Arcane Beam", "Mage", 4, False, False),
    ("SacredHeal", "Sacred Heal", "Priest", 0, True, False),
    ("ShieldBubble", "Shield Bubble", "Priest", 1, False, False),
    ("GuardianSpirit", "Guardian Spirit", "Priest", 2, False, True),
    ("Sanctuary", "Sanctuary", "Priest", 3, False, False),
    ("MartyrsGrace", "Martyr's Grace", "Priest", 4, False, False),
]
assert sorted((c, t) for _i, _n, c, t, _b, _p in ABILS) == sorted((c, t) for c in ("Mage", "Priest") for t in range(5))
# Server Setup rows (key, FIELD, type, default, min, max, unit, category, flags, label, help). Costs = research/cloud/Class-Ability-Spec-
# Draft.md section 2 (walking shape, after the 2026-10-08 power split: Mage 78 / 22, Priest 73 / 27); times in SECONDS.
ABIL_ROWS = [
    ("part.abilities", "PART", "bool", True, "", "", "", "abil", "live,part,danger", "Class abilities",
     "Off: /cast does nothing for anyone. Loadouts and cooldowns are kept."),
    ("abil.creativeFree", "CREATIVE_FREE", "bool", True, "", "", "", "abil", "live", "Creative casts are free",
     "ON: players in creative pay no Mana or Stamina for abilities."),
    ("abil.castChat", "CAST_CHAT", "bool", True, "", "", "", "abil", "live", "Ability chat lines",
     "Cast and hit lines in chat. Players can hide theirs in /settings. Refusals always show."),
    ("abil.refuse", "REFUSE", "dec", 1.0, "0", "10", "s", "abil", "live,adv", "Refusal message interval",
     "At most one 'ready in 4 s' or 'Not enough Mana' line per player this often."),
    # FIX ROUND 2 (critic: the plan's R1 row abil.cdMessage, Engine-Spec section 13: bool, default true, live)
    ("abil.cdMessage", "CD_MSG", "bool", True, "", "", "", "abil", "live", "Cooldown message",
     "Off: casting during the cooldown shows no 'ready in 4 s' line (the click still plays)."),
    ("abil.healCap", "HEAL_CAP", "int", 60, "10", "100", "%", "abil", "live", "Ability heal cap per cast",
     "No ability heals one player more than this % of their max Health per cast."),
    ("abil.unlock.a1", "UNLOCK_A1", "int", 1, "0", "200", "", "abil", "live", "Ability 1 unlock level",
     "Class skill level that unlocks Ability 1 (Mage Meteor, Priest Sacred Heal)."),
    ("abil.unlock.a2", "UNLOCK_A2", "int", 10, "0", "200", "", "abil", "live", "Ability 2 unlock level",
     "Class skill level that unlocks Ability 2 (Mana Barrier, Shield Bubble)."),
    ("abil.unlock.a2alt", "UNLOCK_A2X", "int", 20, "0", "200", "", "abil", "live", "Ability 2 alt unlock level",
     "Class skill level that unlocks the Ability 2 alt (Frost Nova, Guardian Spirit)."),
    ("abil.unlock.a1alt", "UNLOCK_A1X", "int", 30, "0", "200", "", "abil", "live", "Ability 1 alt unlock level",
     "Class skill level for the Ability 1 alt (Starfall / Arcane Beam, Sanctuary / Martyr's Grace)."),
    ("abil.hitFallback", "H_FALLBACK", "dec", 25.0, "1", "10000", "", "abil", "live,adv", "Base hit for unknown weapons",
     "One full hit (H) for weapons SkyyArmory does not know (vanilla staves, grimoires)."),
    # FIX ROUND (critic: the plan's abil.maxLive row was missing - Engine-Spec line 347: default 48, 8-256, live / adv)
    ("abil.maxLive", "MAX_LIVE", "int", 48, "8", "256", "", "abil", "live,adv", "Most running abilities per world",
     "Meteors and heals over time running at once in one world. More casts wait (nothing spent)."),
    # FIX ROUND (critic: only Invulnerable NPCs were spared - the SkyyArmory grapple.noYankWords list, same default)
    ("abil.safeWords", "SAFE_WORDS", "text", "Merchant,Trader,Shopkeeper,Vendor,NPC,Pet,Mount,Tamed,Hub", "", "200", "", "abil", "live,adv",
     "Never hit (role name words)", "Mobs whose role name holds one of these words are never hurt by abilities (pets, traders)."),
    ("ab.Meteor.walk.mana", "M_MANA", "dec", 23.0, "0", "1000", "", "abilx", "live", "Meteor Mana", "Mana per Meteor."),
    ("ab.Meteor.walk.stamina", "M_STAM", "dec", 2.0, "0", "100", "", "abilx", "live", "Meteor Stamina", "Stamina per Meteor."),
    ("ab.Meteor.walk.cooldown", "M_CD", "dec", 14.0, "0", "600", "s", "abilx", "live", "Meteor cooldown", "Seconds before Meteor can be cast again."),
    ("ab.Meteor.power", "M_POWER", "dec", 3.0, "0", "100", "x", "abilx", "live", "Meteor damage (x one staff hit)",
     "Damage = this x one charged shot of the staff held (a spellbook = its same-metal staff)."),
    ("ab.Meteor.radius", "M_RADIUS", "dec", 4.0, "1", "16", "blocks", "abilx", "live", "Meteor size", "Enemies this close to the impact are hit."),
    ("ab.Meteor.delay", "M_DELAY", "dec", 1.0, "0", "5", "s", "abilx", "live", "Meteor fall time", "Seconds from the cast to the impact."),
    ("ab.Meteor.range", "M_RANGE", "dec", 25.0, "4", "64", "blocks", "abilx", "live", "Meteor reach", "How far away the spot you look at may be."),
    ("ab.SacredHeal.walk.mana", "S_MANA", "dec", 18.0, "0", "1000", "", "abilx", "live", "Sacred Heal Mana", "Mana per Sacred Heal."),
    ("ab.SacredHeal.walk.stamina", "S_STAM", "dec", 2.0, "0", "100", "", "abilx", "live", "Sacred Heal Stamina", "Stamina per Sacred Heal."),
    ("ab.SacredHeal.walk.cooldown", "S_CD", "dec", 14.0, "0", "600", "s", "abilx", "live", "Sacred Heal cooldown",
     "Seconds before Sacred Heal can be cast again."),
    ("ab.SacredHeal.heal", "S_HEAL", "int", 25, "0", "100", "%", "abilx", "live", "Sacred Heal (% of max Health)",
     "Instant heal for everyone in range. Players outside your party get the othersPercent share."),
    ("ab.SacredHeal.selfBonus", "S_SELF", "int", 20, "0", "200", "%", "abilx", "live", "Sacred Heal extra on yourself",
     "The Priest heals themself this % more (25% x 1.2 = 30%)."),
    ("ab.SacredHeal.radius", "S_RADIUS", "dec", 9.0, "1", "32", "blocks", "abilx", "live", "Sacred Heal range", "Players this close to the Priest are healed."),
    ("ab.SacredHeal.hot", "S_HOT", "int", 40, "0", "200", "%", "abilx", "live", "Heal over time (% of instant)",
     "After the instant heal: this % of it again, spread over the heal-over-time length."),
    ("ab.SacredHeal.hotTime", "S_HOT_TIME", "dec", 4.0, "0", "30", "s", "abilx", "live", "Heal over time length",
     "Seconds the heal over time lasts (one pulse a second). 0 = no heal over time."),
]
for _r in ABIL_ROWS:
    assert len(_r[9]) <= 40 and len(_r[10]) <= 100, _r[0]
assert [_r[3] for _r in ABIL_ROWS if _r[0].startswith("ab.Meteor.walk.")] == [23.0, 2.0, 14.0], "Meteor 23 Mana + 2 Stamina / 14 s (spec 2.3)"
assert [_r[3] for _r in ABIL_ROWS if _r[0].startswith("ab.SacredHeal.walk.")] == [18.0, 2.0, 14.0], "Sacred Heal 18 Mana + 2 Stamina / 14 s (spec 2.4)"
# the cost split check (research/Class-Power-Split.md + plan 4.3): power 30 (Meteor) / 25 (Sacred Heal) x 78/22 (Mage), 73/27 (Priest)
assert (round(30 * 0.78), max(1, int(30 * 0.22 / 4 + 0.5))) == (23, 2) and (round(25 * 0.73), max(1, int(25 * 0.27 / 4 + 0.5))) == (18, 2)


def abil_text(v):
    """a row default as the config kit's canonical text"""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return v
    if isinstance(v, int):
        return str(v)
    return dnum(v)


ABIL_LINES = [
    "# ---------- Class abilities (0.1.16) - /cast 1 and /cast 2 cast your two primary abilities, crouch = your alts ----------",
    "# part.abilities = false: /cast does nothing (loadouts and cooldowns are kept). abil.unlock.* = class skill level for each ability.",
    "# ab.<Ability>.walk.mana / .stamina / .cooldown = the cost and cooldown (seconds); the other ab.* rows are the ability's numbers.",
    "# Meteor damage = power x one charged shot of the staff or wand held (abil.hitFallback for weapons SkyyArmory does not know).",
] + ["%s=%s" % (_r[0], abil_text(_r[3])) for _r in ABIL_ROWS]
'''
rep('''SYNC_STEADY_MS = 1500       # 0.1.3 review fix: the profile class is written into a profile file only after (epoch, pkey, class) held this long
''', '''SYNC_STEADY_MS = 1500       # 0.1.3 review fix: the profile class is written into a profile file only after (epoch, pkey, class) held this long
''' + ABIL_PY)

# ================================================================================================ the default config file + engine tokens
rep('''    "arrows.cooldownHours=%d" % DEF_ARROWS_HOURS,
]
F(cfg, "public static java.nio.file.Path FILE;")''', '''    "arrows.cooldownHours=%d" % DEF_ARROWS_HOURS,
] + ABIL_LINES   # 0.1.16
F(cfg, "public static java.nio.file.Path FILE;")''')
rep('''    "SAS":  "com.hypixel.hytale.protocol.packets.inventory.SetActiveSlot",
}''', '''    "SAS":  "com.hypixel.hytale.protocol.packets.inventory.SetActiveSlot",
    # 0.1.16: the ability engine (every member probed below; the SkyyArmory 0.1.14 shapes - TravTick, ArmoryTrav.particle / near / hit)
    "ETS":  "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "CAC":  "com.hypixel.hytale.component.ComponentAccessor",
    "MSC":  "com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent",
    "MST":  "com.hypixel.hytale.protocol.MovementStates",
    "TU":   "com.hypixel.hytale.server.core.util.TargetUtil",
    "PTU":  "com.hypixel.hytale.server.core.universe.world.ParticleUtil",
    "DSYS": "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems",
    "DCS":  "com.hypixel.hytale.server.core.modules.entity.damage.DamageCause",
    "INVU": "com.hypixel.hytale.server.core.modules.entity.component.Invulnerable",
    "DTH":  "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    # FIX ROUND: the refusal fail sound (plan 4.1) - the SkyyArmory ArmoryTrav.sound shapes
    "SNU":  "com.hypixel.hytale.server.core.universe.world.SoundUtil",
    "SEV":  "com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent",
    "SCAT": "com.hypixel.hytale.protocol.SoundCategory",
}''')
rep('''B.probe(pool, T["WLD"], "isInThread")
''', '''B.probe(pool, T["WLD"], "isInThread")
# 0.1.16 (ability engine): every new engine member, with the exact descriptors the engine code calls
for c, m in ((T["ETS"], "tick"), (T["ETS"], "isParallel"), (T["MSC"], "getComponentType"), (T["MSC"], "getMovementStates"), (T["MST"], "crouching"),
             (T["TU"], "getTargetLocation"), (T["TU"], "getAllEntitiesInSphere"), (T["PTU"], "spawnParticleEffect"), (T["DSYS"], "executeDamage"),
             (T["DCS"], "PROJECTILE"), (T["INVU"], "getComponentType"), (T["DTH"], "getComponentType"), (T["ESM"], "subtractStatValue"),
             (T["DST"], "getMana"), (T["DST"], "getStamina"), (T["ES"], "getRefFromUUID"), (T["UNI"], "getPlayer"),
             (T["SNU"], "playSoundEvent2dToPlayer"), (T["SEV"], "getAssetMap"), (T["SCAT"], "SFX"), (T["NPC"], "getRoleName")):   # + FIX ROUND
    B.probe(pool, c, m)
assert str(pool.get(T["SNU"]).getMethod("playSoundEvent2dToPlayer", "(Lcom/hypixel/hytale/server/core/universe/PlayerRef;ILcom/hypixel/hytale/protocol/SoundCategory;)V").getName()) == "playSoundEvent2dToPlayer"
assert str(pool.get(T["NPC"]).getMethod("getRoleName", "()Ljava/lang/String;").getName()) == "getRoleName"
for c, m, d in ((T["TU"], "getTargetLocation", "(Lcom/hypixel/hytale/component/Ref;DLcom/hypixel/hytale/component/ComponentAccessor;)Lorg/joml/Vector3d;"),
                (T["TU"], "getAllEntitiesInSphere", "(Lorg/joml/Vector3d;DLcom/hypixel/hytale/component/ComponentAccessor;)Ljava/util/List;"),
                (T["PTU"], "spawnParticleEffect", "(Ljava/lang/String;Lorg/joml/Vector3dc;Lcom/hypixel/hytale/component/ComponentAccessor;)V"),
                (T["DSYS"], "executeDamage", "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/server/core/modules/entity/damage/Damage;)V"),
                (T["ESM"], "subtractStatValue", "(IF)F"), (T["ESM"], "addStatValue", "(IF)F"),
                (T["ETS"], "tick", "(FILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V")):
    assert str(pool.get(c).getMethod(m, d).getName()) == m, "%s.%s%s" % (c, m, d)
pool.get(T["DMG"]).getConstructor("(Lcom/hypixel/hytale/server/core/modules/entity/damage/Damage$Source;Lcom/hypixel/hytale/server/core/modules/entity/damage/DamageCause;F)V")
pool.get(T["DENT"]).getConstructor("(Lcom/hypixel/hytale/component/Ref;)V")
assert pool.get("org.joml.Vector3d").subtypeOf(pool.get("org.joml.Vector3dc")), "Vector3d is a Vector3dc"
assert pool.get(T["CB"]).subtypeOf(pool.get(T["CAC"])) and pool.get(T["ST"]).subtypeOf(pool.get(T["CAC"])), "Store / CommandBuffer are ComponentAccessors"
''')

# ================================================================================================ AbilCfg (fields before CFG.emit + load)
ABIL_CFG = r'''
# ================= 0.1.16 AbilCfg: the ability rows (Server Setup -> Classes -> Abilities / Ability numbers), read by ClassCfg.load =================
abcfg = pool.makeClass(PKG + ".AbilCfg")
for _r in ABIL_ROWS:
    _jt = {"bool": "boolean", "int": "long", "dec": "double", "text": "String"}[_r[2]]
    _dv = ("true" if _r[3] else "false") if _r[2] == "bool" else ("%dL" % _r[3] if _r[2] == "int" else (jstr(_r[3]) if _r[2] == "text" else jdbl(_r[3])))
    F(abcfg, "public static volatile %s %s = %s;" % (_jt, _r[1], _dv))
M(abcfg, r"""
public static double clampD(double v, double lo, double hi) {
  if (!(v >= lo)) return lo;
  if (v > hi) return hi;
  return v;
}""")
M(abcfg, r"""
public static long clampL(long v, long lo, long hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}""")
_ab_read = []
for _r in ABIL_ROWS:
    if _r[2] == "bool":
        _ab_read.append('  %s = @PKG@.ClassCfg.bool(p, %s, %s);' % (_r[1], jstr(_r[0]), "true" if _r[3] else "false"))
    elif _r[2] == "text":
        _ab_read.append('  %s = @PKG@.ClassCfg.txt(p, %s, %s);' % (_r[1], jstr(_r[0]), jstr(_r[3])))
    elif _r[2] == "int":
        _ab_read.append('  %s = clampL(@PKG@.ClassCfg.lng(p, %s, %dL), %sL, %sL);' % (_r[1], jstr(_r[0]), _r[3], _r[4], _r[5]))
    else:
        _ab_read.append('  %s = clampD(@PKG@.ClassCfg.dbl(p, %s, %s), %s, %s);' % (_r[1], jstr(_r[0]), jdbl(_r[3]), jdbl(float(_r[4])), jdbl(float(_r[5]))))
M(abcfg, "public static void read(java.util.Properties p) {\n" + "\n".join(_ab_read) + "\n}")
M(abcfg, r"""
public static String text() {
  return " abilities=" + (PART ? "on" : "off") + " (unlock " + UNLOCK_A1 + "/" + UNLOCK_A2 + "/" + UNLOCK_A2X + "/" + UNLOCK_A1X
    + ", Meteor " + @PKG@.ClassCfg.fmtNum(M_MANA) + "+" + @PKG@.ClassCfg.fmtNum(M_STAM) + "/" + @PKG@.ClassCfg.fmtNum(M_CD) + "s"
    + ", Sacred Heal " + @PKG@.ClassCfg.fmtNum(S_MANA) + "+" + @PKG@.ClassCfg.fmtNum(S_STAM) + "/" + @PKG@.ClassCfg.fmtNum(S_CD) + "s)";
}""")
'''
rep('''# the 0.1.6 + 0.1.7 part of load() / summary(): "kits=on priestHeal=on healShare=25% self=50% radius=16 arrows=on 64xWeapon_Arrow_Crude/24h"
''', ABIL_CFG + '''# the 0.1.6 + 0.1.7 part of load() / summary(): "kits=on priestHeal=on healShare=25% self=50% radius=16 arrows=on 64xWeapon_Arrow_Crude/24h"
''')
rep('''    + " arrows=" + (ARROWS_ON ? "on" : "off") + " " + ARROWS_AMOUNT + "x" + ARROWS_ITEM + "/" + ARROWS_HOURS + "h";
}""")''', '''    + " arrows=" + (ARROWS_ON ? "on" : "off") + " " + ARROWS_AMOUNT + "x" + ARROWS_ITEM + "/" + ARROWS_HOURS + "h" + @PKG@.AbilCfg.text();
}""")''')
rep('''    ARROWS_HOURS = ah;
    return "switchCost=" + SWITCH_COST''', '''    ARROWS_HOURS = ah;
    @PKG@.AbilCfg.read(p);   // 0.1.16: the ability rows (missing keys = their defaults; clamps = the row bounds)
    return "switchCost=" + SWITCH_COST''')

# ================================================================================================ the config rows
rep('''CFG_CATS = [("lock", "Weapon lock"), ("picker", "Class picker"), ("kits", "Class kits"), ("priest", "Priest heal"),   # 0.1.6: + kits, priest
            ("arrows", "Archer arrows")]                                                                                 # 0.1.7: + arrows''',
    '''CFG_CATS = [("lock", "Weapon lock"), ("picker", "Class picker"), ("kits", "Class kits"), ("priest", "Priest heal"),   # 0.1.6: + kits, priest
            ("arrows", "Archer arrows"),                                                                                 # 0.1.7: + arrows
            ("abil", "Abilities"), ("abilx", "Ability numbers")]                                                         # 0.1.16''')
rep('''# build check: every row bound to a config.properties key has the default the default file writes (the file and the kit agree)
_DFL = CFG.parse_props''', '''# 0.1.16: the ability rows (research/cloud/Ability-Engine-Plan.md section 9 R1; keys read by AbilCfg.read through ClassCfg.load)
for _r in ABIL_ROWS:
    CFG_ROWS.append((_r[0], _r[9], _r[7], _r[2], abil_text(_r[3]), _r[4], _r[5], "", _r[6], _r[8], _r[10],
                     "field:AbilCfg.%s@config.properties:%s" % (_r[1], _r[0])))
# build check: every row bound to a config.properties key has the default the default file writes (the file and the kit agree)
_DFL = CFG.parse_props''')
rep('''assert len(CFG_ROWS) == 5 + 2 + 1 + 2 * len(CLASSES) + 11 + 4, "row count"''',
    '''assert len(CFG_ROWS) == 5 + 2 + 1 + 2 * len(CLASSES) + 11 + 4 + len(ABIL_ROWS), "row count"   # 0.1.16: + the ability rows''')

# ================================================================================================ AbilDmg (before DamageLock) + DamageLock skip
ABIL_DMG = r'''
# ================= 0.1.16 AbilDmg: the Damage objects the ability engine created (DamageLock skips them; class:fn:abilhit names the caster) =================
# VERIFIED (HytaleServer.jar bytecode): DamageSystems.executeDamage = CommandBuffer.invoke(ref, damage) - every damage system gets the SAME
# object, and DamageSystems$ApplyDamage passes it to DeathComponent.tryAddComponent (= the death info SkyySkills' KillSys reads). Damage does not
# override equals / hashCode, so a WeakHashMap is an identity map whose entries leave with the Damage.
abdmg = pool.makeClass(PKG + ".AbilDmg")
F(abdmg, "public static final java.util.Map TAG = java.util.Collections.synchronizedMap(new java.util.WeakHashMap());")
M(abdmg, r"""
public static void tag(Object d, java.util.UUID caster, String what) {
  if (d == null || caster == null) return;
  TAG.put(d, new Object[] { caster, what == null ? "" : what });
}""")
M(abdmg, r"""
public static boolean mine(Object d) {
  return d != null && TAG.containsKey(d);
}""")
M(abdmg, r"""
public static java.util.UUID casterOf(Object d) {
  if (d == null) return null;
  Object o = TAG.get(d);
  if (!(o instanceof Object[])) return null;
  Object[] a = (Object[]) o;
  return a.length > 0 && a[0] instanceof java.util.UUID ? (java.util.UUID) a[0] : null;
}""")
M(abdmg, r"""
public static String whatOf(Object d) {
  if (d == null) return null;
  Object o = TAG.get(d);
  if (!(o instanceof Object[])) return null;
  Object[] a = (Object[]) o;
  return a.length > 1 && a[1] instanceof String ? (String) a[1] : null;
}""")
# class:fn:abilhit apply(Object damage) -> UUID caster (or null: not ability damage). Any thread, never throws.
abhit = pool.makeClass(PKG + ".AbilHitFn")
abhit.addInterface(pool.get("java.util.function.Function"))
C(abhit, "public AbilHitFn() { }")
M(abhit, r"""
public Object apply(Object o) {
  try {
    if (o instanceof Object[]) { Object[] a = (Object[]) o; o = a.length > 0 ? a[0] : null; }
    return @PKG@.AbilDmg.casterOf(o);
  } catch (Throwable t) { return null; }
}""")

'''
rep('''# ================= DamageLock: cancel damage dealt with a weapon the attacker's class may not use =================
''', ABIL_DMG + '''# ================= DamageLock: cancel damage dealt with a weapon the attacker's class may not use =================
''')
rep('''    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled()) return;
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DENT@)) return;
    java.util.UUID u = null;''', '''    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled()) return;
    if (@PKG@.AbilDmg.mine(d)) return;   // 0.1.16: ability damage - the weapon was checked at the cast (plan 4.2: a swap must not zero it)
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DENT@)) return;
    java.util.UUID u = null;''')

# ================================================================================================ the engine (after PriestHealSys)
ENGINE_SRC = r'''
# =====================================================================================================================
# 0.1.16: THE ABILITY ENGINE (round R1). Registry -> loadout store -> pipeline -> executors -> AbilTick. Notes: tools/classes_0_1_16_patch.py
# =====================================================================================================================
_CLS_NAMES = [c["name"] for c in CLASSES]
# the particles the abilities spawn: VANILLA ids only (no asset pack), each proven here to be a finite one-shot system in Assets.zip
FX = {"FX_MARK": "Fire_AoE_Spawn", "FX_HIT": "Explosion_Medium", "FX_HEAL": "Magic_Hit"}
_psys = dict((n.rsplit("/", 1)[1][:-len(".particlesystem")], n) for n in _ASSETS.namelist() if n.startswith("Server/Particles/") and n.endswith(".particlesystem"))
_pspn = dict((n.rsplit("/", 1)[1][:-len(".particlespawner")], n) for n in _ASSETS.namelist() if n.startswith("Server/Particles/") and n.endswith(".particlespawner"))
for _k, _id in FX.items():
    assert _id in _psys, "%s: vanilla particle system %s is missing from Assets.zip" % (_k, _id)
    _pj = json.loads(_ASSETS.read(_psys[_id]).decode("utf8"))
    assert _pj.get("Spawners"), "%s has no spawners" % _id
    for _e in _pj["Spawners"]:
        _sj = json.loads(_ASSETS.read(_pspn[_e["SpawnerId"]]).decode("utf8"))
        _tp = _sj.get("TotalParticles")
        assert (_tp and _tp.get("Max", 0) > 0) or _e.get("LifeSpan") or _sj.get("LifeSpan") or _pj.get("LifeSpan"),             "%s spawner %s never stops - an ability may only spawn one-shot particles" % (_id, _e["SpawnerId"])
print("ability particles (vanilla, finite one-shots): %s" % ", ".join(sorted(FX.values())))
# FIX ROUND (critic: plan 4.1 - refusals play the fail sound): the vanilla "no ammo" click = the staff's own fail sound (SkyyArmory Staff_Cast_Fail)
SND_FAIL = "SFX_Bow_No_Ammo"
assert [n for n in _ASSETS.namelist() if n.startswith("Server/Audio/SoundEvents/") and n.endswith("/" + SND_FAIL + ".json")], "vanilla sound %s missing" % SND_FAIL
abdefs = pool.makeClass(PKG + ".AbilDefs")
F(abdefs, "public static final String[] IDS = %s;" % jarr([a[0] for a in ABILS]))
F(abdefs, "public static final String[] NAMES = %s;" % jarr([a[1] for a in ABILS]))
F(abdefs, "public static final int[] CLS = new int[] { %s };" % ", ".join(str(_CLS_NAMES.index(a[2])) for a in ABILS))
F(abdefs, "public static final int[] TIER = new int[] { %s };" % ", ".join(str(a[3]) for a in ABILS))
F(abdefs, "public static final boolean[] BUILT = new boolean[] { %s };" % ", ".join("true" if a[4] else "false" for a in ABILS))
F(abdefs, "public static final boolean[] PASSIVE = new boolean[] { %s };" % ", ".join("true" if a[5] else "false" for a in ABILS))
F(abdefs, "public static final int METEOR = %d;" % [a[0] for a in ABILS].index("Meteor"))
F(abdefs, "public static final int SACRED = %d;" % [a[0] for a in ABILS].index("SacredHeal"))
M(abdefs, r"""
public static int find(String s) {
  if (s == null) return -1;
  String t = s.trim();
  if (t.length() == 0) return -1;
  for (int i = 0; i < IDS.length; i++) if (IDS[i].equalsIgnoreCase(t) || NAMES[i].equalsIgnoreCase(t)) return i;
  return -1;
}""")
M(abdefs, r"""
public static int of(int ci, int tier) {
  for (int i = 0; i < IDS.length; i++) if (CLS[i] == ci && TIER[i] == tier) return i;
  return -1;
}""")
M(abdefs, r"""
public static boolean classHas(int ci) {
  return ci >= 0 && of(ci, 0) >= 0;
}""")
M(abdefs, r"""
public static long unlock(int tier) {
  if (tier <= 0) return @PKG@.AbilCfg.UNLOCK_A1;
  if (tier == 1) return @PKG@.AbilCfg.UNLOCK_A2;
  if (tier == 2) return @PKG@.AbilCfg.UNLOCK_A2X;
  return @PKG@.AbilCfg.UNLOCK_A1X;
}""")
# the A1-alt pick: "B" = tier 4 (A1-alt B), anything else = tier 3 (A1-alt A, the default) - picking one locks out the other
M(abdefs, r"""
public static int pickTier(String pick) {
  return pick != null && pick.trim().equalsIgnoreCase("B") ? 4 : 3;
}""")
M(abdefs, r"""
public static boolean owns(int ai, int level, boolean grant, String pick) {
  if (ai < 0 || ai >= IDS.length) return false;
  int t = TIER[ai];
  if (t >= 3 && t != pickTier(pick)) return false;
  if (grant) return true;
  return (long) level >= unlock(t);
}""")
# the default loadout: p1 = A1, p2 = A2 (the two primaries), a1 = A2-alt, a2 = the picked A1-alt (the two crouch alts) - plan 3.1
M(abdefs, r"""
public static String[] defaults(int ci, String pick) {
  int[] tiers = new int[] { 0, 1, 2, pickTier(pick) };
  String[] r = new String[4];
  for (int i = 0; i < 4; i++) {
    int a = of(ci, tiers[i]);
    r[i] = a < 0 ? "" : IDS[a];
  }
  return r;
}""")
# a stored loadout is used only when it is exactly a re-ordering of this class's 4 owned slots (else the defaults - another class's file,
# a hand edit, a pick change); returns the canonical ids or null
M(abdefs, r"""
public static String[] valid(String[] st, int ci, String pick) {
  if (st == null || st.length != 4) return null;
  String[] d = defaults(ci, pick);
  String[] r = new String[4];
  boolean[] used = new boolean[4];
  for (int i = 0; i < 4; i++) {
    int a = find(st[i]);
    if (a < 0 || CLS[a] != ci) return null;
    int hit = -1;
    for (int j = 0; j < 4; j++) if (!used[j] && IDS[a].equals(d[j])) hit = j;
    if (hit < 0) return null;
    used[hit] = true;
    r[i] = IDS[a];
  }
  return r;
}""")
M(abdefs, r"""
public static double mana(int ai) {
  if (ai == METEOR) return @PKG@.AbilCfg.M_MANA;
  if (ai == SACRED) return @PKG@.AbilCfg.S_MANA;
  return 0.0;
}""")
M(abdefs, r"""
public static double stamina(int ai) {
  if (ai == METEOR) return @PKG@.AbilCfg.M_STAM;
  if (ai == SACRED) return @PKG@.AbilCfg.S_STAM;
  return 0.0;
}""")
M(abdefs, r"""
public static long cdMs(int ai) {
  double s = 0.0;
  if (ai == METEOR) s = @PKG@.AbilCfg.M_CD;
  if (ai == SACRED) s = @PKG@.AbilCfg.S_CD;
  if (!(s > 0.0)) return 0L;
  return Math.round(s * 1000.0);
}""")
M(abdefs, r"""
public static String key(int slot) {
  if (slot == 0) return "/cast 1";
  if (slot == 1) return "/cast 2";
  if (slot == 2) return "crouch + /cast 1 (or /cast 3)";
  return "crouch + /cast 2 (or /cast 4)";
}""")

# ---- AbilMath: the pure rules (bare-JVM tested)
abmath = pool.makeClass(PKG + ".AbilMath")
M(abmath, r"""
public static int slotOf(String a) {
  if (a == null) return -1;
  String s = a.trim().toLowerCase();
  if (s.equals("1") || s.equals("p1")) return 0;
  if (s.equals("2") || s.equals("p2")) return 1;
  if (s.equals("3") || s.equals("alt1") || s.equals("a1")) return 2;
  if (s.equals("4") || s.equals("alt2") || s.equals("a2")) return 3;
  return -1;
}""")
# Skyy's lock: crouch held at the cast = the alt on that key (a primary key 1 / 2 -> alt 1 / 2); the alt keys stay alts
M(abmath, r"""
public static int resolve(int slot, boolean crouch) {
  if (slot < 0 || slot > 3) return -1;
  if (crouch && slot < 2) return slot + 2;
  return slot;
}""")
M(abmath, r"""
public static long secs(long ms) {
  if (ms <= 0L) return 0L;
  return (ms + 999L) / 1000L;
}""")
M(abmath, r"""
public static String readyText(long ms) {
  return "ready in " + secs(ms) + " s";
}""")
M(abmath, r"""
public static boolean enough(double have, double need) {
  if (!(need > 0.0)) return true;
  return have + 1.0E-4 >= need;
}""")
M(abmath, r"""
public static String fmt(double x) {
  if (x != x || Double.isInfinite(x)) return "0";
  double r = (double) Math.round(x * 10.0) / 10.0;
  if (r == Math.floor(r)) return String.valueOf((long) r);
  return String.valueOf(r);
}""")
# Sacred Heal's instant heal for one target: pct % of max Health, the Priest selfBonus % more
M(abmath, r"""
public static double heal(double max, long pct, boolean self, long selfBonus) {
  if (!(max > 0.0) || pct <= 0L) return 0.0;
  double h = max * (double) pct / 100.0;
  if (self && selfBonus > 0L) h = h * (1.0 + (double) selfBonus / 100.0);
  return h;
}""")
M(abmath, r"""
public static double capLeft(double max, long capPct, double done) {
  if (!(max > 0.0)) return 0.0;
  double c = max * (double) capPct / 100.0 - done;
  return c > 0.0 ? c : 0.0;
}""")
# H = one charged shot of the weapon held: armory:fn:info element 3 (charged damage) x element 5 (the weapon's tune %); else the fallback
M(abmath, r"""
public static double hOf(Object[] info, double fallback) {
  if (info != null && info.length > 3 && info[3] instanceof Number) {
    double d = ((Number) info[3]).doubleValue();
    double t = 100.0;
    if (info.length > 5 && info[5] instanceof Number) t = ((Number) info[5]).doubleValue();
    if (!(t >= 0.0) || Double.isInfinite(t)) t = 100.0;
    double h = d * t / 100.0;
    if (h > 0.0 && !Double.isInfinite(h)) return h;
  }
  return fallback > 0.0 ? fallback : 1.0;
}""")
M(abmath, r"""
public static int ticks(double secs) {
  if (!(secs > 0.0)) return 0;
  long n = Math.round(secs);
  if (n < 1L) n = 1L;
  if (n > 60L) n = 60L;
  return (int) n;
}""")
M(abmath, r"""
public static boolean inRange(double dx, double dy, double dz, double r) {
  return dx * dx + dy * dy + dz * dz <= r * r;
}""")
# FIX ROUND: a role name holding one of the comma-separated words (case-insensitive; SkyyArmory GrappleMath.bossName, verbatim rule)
M(abmath, r"""
public static boolean words(String role, String words) {
  if (role == null || words == null) return false;
  String r = role.toLowerCase();
  String[] ws = words.split(",");
  for (int i = 0; i < ws.length; i++) {
    String w = ws[i].trim().toLowerCase();
    if (w.length() > 0 && r.indexOf(w) >= 0) return true;
  }
  return false;
}""")

# ---- AbilStore: loadout per profile (abilities/<pkey>.properties), memory cooldowns (pkey|ability), refusal throttle
abst = pool.makeClass(PKG + ".AbilStore")
absave = pool.makeClass(PKG + ".AbilSave")
F(abst, "public static java.nio.file.Path DIR;")
for _f in ("DATA", "FAILAT", "CD", "CDLEN", "TOLD", "DIRTY"):   # FIX ROUND: + DIRTY (keys changed in memory, not yet on disk)
    F(abst, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
F(abst, "public static volatile long SAVES = 0L;")
# FIX ROUND (critic: the world thread waited on the AbilStore monitor while a save slept in its move-retry loop): a cached read takes no
# lock (load); only a cache MISS reads the file under the AbilStore monitor (loadMiss); the write + its retry sleep run under the AbilSave
# monitor (AbilSave.write), which no world-thread path takes
M(abst, r"""
public static synchronized java.util.Properties loadMiss(String k) {
  if (k == null) return new java.util.Properties();
  java.util.Properties p = (java.util.Properties) DATA.get(k);
  if (p != null) return p;
  p = new java.util.Properties();
  Long failed = (Long) FAILAT.get(k);
  if (failed != null && System.currentTimeMillis() - failed.longValue() < 2000L) return p;
  try {
    if (DIR != null) {
      java.nio.file.Path f = DIR.resolve(k + ".properties");
      if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
        java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
        try { p.load(in); } finally { in.close(); }
      }
    }
  } catch (Throwable t) {
    FAILAT.put(k, Long.valueOf(System.currentTimeMillis()));
    @PKG@.ClassCfg.warnLimited("could not read ability file " + k + " (not cached, retried every 2 s, never overwritten meanwhile): " + t);
    return new java.util.Properties();
  }
  FAILAT.remove(k);
  DATA.put(k, p);
  return p;
}""")
M(abst, r"""
public static java.util.Properties load(String k) {
  if (k == null) return new java.util.Properties();
  java.util.Properties p = (java.util.Properties) DATA.get(k);
  if (p != null) return p;
  return loadMiss(k);
}""")
M(absave, r"""
public static synchronized boolean write(String k) {
  java.util.Properties p = (java.util.Properties) @PKG@.AbilStore.DATA.get(k);
  java.nio.file.Path DIR = @PKG@.AbilStore.DIR;
  if (p == null || DIR == null) return false;
  boolean ok = false;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyClasses abilities (p1 p2 = primaries, a1 a2 = crouch alts, alt = A1-alt pick A or B, grant = admin grant)"); } finally { out.close(); }
    java.nio.file.Path dst = DIR.resolve(k + ".properties");
    int tries = 0;
    while (!ok) {
      try {
        java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
        ok = true;
      } catch (java.nio.file.FileSystemException ade) {
        tries++;
        if (tries >= 5) throw ade;
        Thread.sleep(20L);
      }
    }
    @PKG@.AbilStore.SAVES = @PKG@.AbilStore.SAVES + 1L;
  } catch (Throwable t) { @PKG@.ClassCfg.warn("could not save ability file " + k + ": " + t); }
  return ok;
}""")
# FIX ROUND (critic: a failed or never-run write was lost): the key leaves DIRTY before the write reads DATA, and comes back when it fails
M(abst, r"""
public static boolean save(String k) {
  if (k == null) return false;
  DIRTY.remove(k);
  boolean ok = @PKG@.AbilSave.write(k);
  if (!ok && DATA.get(k) != null) DIRTY.put(k, Boolean.TRUE);
  return ok;
}""")
# every key still DIRTY written now (the plugin's shutdown; a stop right after /cast swap or a grant no longer loses it); returns the count
M(abst, r"""
public static int flush() {
  int n = 0;
  java.util.Iterator it = new java.util.ArrayList(DIRTY.keySet()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (save(k)) n++;
  }
  return n;
}""")
absave.addInterface(pool.get("java.lang.Runnable"))
F(absave, "public String k;")
F(absave, "public int tries;")
C(absave, "public AbilSave(String k, int tries) { this.k = k; this.tries = tries; }")
# a failed write is tried again 5 s later (at most 5 times; a newer change or the shutdown flush may have written it meanwhile)
M(absave, r"""
public void run() {
  try {
    if (@PKG@.AbilStore.save(this.k)) return;
    if (this.tries < 5 && @PKG@.AbilStore.DIRTY.containsKey(this.k))
      @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.AbilSave(this.k, this.tries + 1), 5L, java.util.concurrent.TimeUnit.SECONDS);
  } catch (Throwable t) { }
}""")
F(abst, "public static volatile boolean SYNC = false;")   # HARNESS SEAM ONLY (false in the game): write on the caller's thread
M(abst, r"""
public static void saveSoon(String k) {
  if (k == null) return;
  DIRTY.put(k, Boolean.TRUE);
  if (SYNC) { save(k); return; }
  try { @HSV@.SCHEDULED_EXECUTOR.execute(new @PKG@.AbilSave(k, 0)); } catch (Throwable t) { save(k); }
}""")
# copy-on-write: keys[i] = vals[i] (null = remove); false = the file could not be read (never written then)
M(abst, r"""
public static synchronized boolean set(String k, String[] keys, String[] vals) {
  java.util.Properties old = load(k);
  if (DATA.get(k) != old) return false;
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  for (int i = 0; i < keys.length && i < vals.length; i++) {
    if (vals[i] == null) p.remove(keys[i]);
    else p.setProperty(keys[i], vals[i]);
  }
  DATA.put(k, p);
  return true;
}""")
M(abst, r"""
public static boolean granted(String k) {
  return "true".equalsIgnoreCase(load(k).getProperty("grant", "").trim());
}""")
M(abst, r"""
public static String pick(String k) {
  String v = load(k).getProperty("alt", "A").trim();
  return v.equalsIgnoreCase("B") ? "B" : "A";
}""")
M(abst, r"""
public static String[] slots(String k, int ci) {
  java.util.Properties p = load(k);
  String pk = pick(k);
  String[] st = new String[] { p.getProperty("p1"), p.getProperty("p2"), p.getProperty("a1"), p.getProperty("a2") };
  String[] v = @PKG@.AbilDefs.valid(st, ci, pk);
  return v != null ? v : @PKG@.AbilDefs.defaults(ci, pk);
}""")
M(abst, r"""
public static long left(String k, String id, long now) {
  Object o = CD.get(k + "|" + id);
  if (!(o instanceof Long)) return 0L;
  long l = ((Long) o).longValue() - now;
  return l > 0L ? l : 0L;
}""")
M(abst, r"""
public static long total(String k, String id) {
  Object o = CDLEN.get(k + "|" + id);
  return o instanceof Long ? ((Long) o).longValue() : 0L;
}""")
M(abst, r"""
public static void purge(long now) {
  java.util.Iterator it = CD.keySet().iterator();
  while (it.hasNext()) {
    Object key = it.next();
    Object v = CD.get(key);
    if (!(v instanceof Long) || ((Long) v).longValue() <= now) { it.remove(); CDLEN.remove(key); }
  }
}""")
M(abst, r"""
public static void arm(String k, String id, long now, long ms) {
  String key = k + "|" + id;
  if (ms <= 0L) { CD.remove(key); CDLEN.remove(key); return; }
  CD.put(key, Long.valueOf(now + ms));
  CDLEN.put(key, Long.valueOf(ms));
  if (CD.size() > 4096) purge(now);
}""")
M(abst, r"""
public static int clearCd(String k) {
  int n = 0;
  java.util.Iterator it = CD.keySet().iterator();
  while (it.hasNext()) {
    Object key = it.next();
    if (String.valueOf(key).startsWith(k + "|")) { it.remove(); CDLEN.remove(key); n++; }
  }
  return n;
}""")
M(abst, r"""
public static boolean throttle(java.util.UUID u, long now, long gapMs) {
  if (u == null) return true;
  Object o = TOLD.get(u);
  if (o instanceof Long && now - ((Long) o).longValue() < gapMs && now >= ((Long) o).longValue()) return false;
  TOLD.put(u, Long.valueOf(now));
  return true;
}""")

# ---- AbilJob: one delayed job (kind 1 = Meteor impact, 2 = a heal-over-time pulse series)
abjob = pool.makeClass(PKG + ".AbilJob")
for _f in ("public int kind;", "public long at;", "public java.util.UUID caster;", "public String what;", "public double x;", "public double y;",
           "public double z;", "public double r;", "public double amount;", "public java.util.UUID[] targets;", "public double[] per;",
           "public double[] done;", "public double[] cap;", "public int left;", "public long every;", "public int hits;", "public String name;",
           "public String pkey;"):   # FIX ROUND: + pkey = the caster's profile at the cast
    F(abjob, _f)
C(abjob, r"""
public AbilJob(int kind, long at, java.util.UUID caster, String what, double x, double y, double z, double r, double amount) {
  this.kind = kind;
  this.at = at;
  this.caster = caster;
  this.what = what;
  this.x = x;
  this.y = y;
  this.z = z;
  this.r = r;
  this.amount = amount;
  this.left = 0;
  this.every = 0L;
  this.hits = -1;
}""")

# ---- AbilWorld: the job list of one world (world name -> list), run by AbilTick once per world tick
abworld = pool.makeClass(PKG + ".AbilWorld")
F(abworld, "public static final java.util.concurrent.ConcurrentHashMap BY = new java.util.concurrent.ConcurrentHashMap();")
F(abworld, "public String name;")
F(abworld, "public java.util.ArrayList jobs;")
F(abworld, "public volatile long lastNs;")
C(abworld, "public AbilWorld(String name) { this.name = name; this.jobs = new java.util.ArrayList(); this.lastNs = 0L; }")
M(abworld, r"""
public static @PKG@.AbilWorld of(String n) {
  String key = n == null ? "" : n;
  @PKG@.AbilWorld w = (@PKG@.AbilWorld) BY.get(key);
  if (w == null) {
    w = new @PKG@.AbilWorld(key);
    Object o = BY.putIfAbsent(key, w);
    if (o != null) w = (@PKG@.AbilWorld) o;
  }
  return w;
}""")
M(abworld, r"""
public static String nameOf(Object ext) {
  try {
    if (ext instanceof @ES@) {
      @WLD@ w = ((@ES@) ext).getWorld();
      return w == null ? null : w.getName();
    }
  } catch (Throwable t) { }
  return null;
}""")
M(abworld, r"""
public static @PKG@.AbilWorld at(@ST@ st) {
  if (st == null || BY.isEmpty()) return null;
  String n = nameOf(st.getExternalData());
  return n == null ? null : (@PKG@.AbilWorld) BY.get(n);
}""")
# FIX ROUND 2 (critic: jobs of a world that emptied waited for its next player tick - minutes later): a job more than STALE ms past its time
# is dropped unrun (no late Meteor, no late XP) and no longer counts toward abil.maxLive
F(abworld, "public static final long STALE = 30000L;")
M(abworld, r"""
public synchronized int prune(long now) {
  int n = 0;
  java.util.Iterator it = this.jobs.iterator();
  while (it.hasNext()) {
    @PKG@.AbilJob j = (@PKG@.AbilJob) it.next();
    if (j.at + STALE < now) { it.remove(); n++; }
  }
  return n;
}""")
M(abworld, "public synchronized boolean full() { prune(System.currentTimeMillis()); return (long) this.jobs.size() >= @PKG@.AbilCfg.MAX_LIVE; }")   # FIX ROUND: row abil.maxLive
M(abworld, "public synchronized boolean idle() { return this.jobs.isEmpty(); }")
M(abworld, "public synchronized int size() { return this.jobs.size(); }")
M(abworld, "public synchronized void add(@PKG@.AbilJob j) { if (j != null) this.jobs.add(j); }")
M(abworld, r"""
public synchronized java.util.ArrayList due(long now) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator it = this.jobs.iterator();
  while (it.hasNext()) {
    @PKG@.AbilJob j = (@PKG@.AbilJob) it.next();
    if (j.at + STALE < now) { it.remove(); continue; }   // FIX ROUND 2: stale = dropped unrun
    if (j.at <= now) { out.add(j); it.remove(); }
  }
  return out;
}""")

# ---- Abil: the cast pipeline + executors (world thread: commands and AbilTick)
abil = pool.makeClass(PKG + ".Abil")
for _k, _v in FX.items():
    F(abil, "public static final String %s = %s;" % (_k, jstr(_v)))
F(abil, "public static final String SND_FAIL = %s;" % jstr(SND_FAIL))   # FIX ROUND: the refusal fail sound (vanilla)
for _f in ("public static volatile java.util.function.Function NEAR = null;",    # HARNESS SEAM ONLY (null in the game = TargetUtil sphere)
           "public static volatile java.util.function.Function AIM = null;",     # HARNESS SEAM ONLY (null = TargetUtil.getTargetLocation)
           "public static volatile java.util.function.Function HAND = null;",    # HARNESS SEAM ONLY (null = InventoryComponent.getItemInHand)
           "public static volatile java.util.List PSEEN = null;",                # HARNESS SEAM ONLY (null): every particle id spawned
           "public static volatile java.util.List SAID = null;",                 # HARNESS SEAM ONLY (null): every chat line sent
           "public static volatile java.util.List SOUNDS = null;",               # HARNESS SEAM ONLY (null): every sound id played
           "public static volatile String LAST = \"\";"):                        # the last cast outcome (harness + /classadmin abil info)
    F(abil, _f)
M(abil, r"""
public static void send(@PR@ pr, String text, String color) {
  java.util.List l = SAID;
  if (l != null) l.add(text);
  try {
    if (pr == null || !pr.isValid()) return;
    if (color == null) pr.sendMessage(@MSG@.raw("[Classes] " + text));
    else pr.sendMessage(@MSG@.raw("[Classes] " + text).color(color));
  } catch (Throwable t) { }
}""")
M(abil, r"""
public static void say(@PR@ pr, String text) {
  try {
    if (pr == null || !@PKG@.AbilCfg.CAST_CHAT) return;
    if (!@PKG@.ClassCfg.notifyOn(pr.getUuid(), "classes.abilChat")) return;
  } catch (Throwable t) { return; }
  send(pr, text, "#8fe39a");
}""")
# FIX ROUND (critic: plan 4.1 "refusals ... play the fail sound"): the vanilla no-ammo click, to the caster only (2D), with the refusal line
M(abil, r"""
public static void failSound(@PR@ pr) {
  java.util.List l = SOUNDS;
  if (l != null) l.add(SND_FAIL);
  try {
    if (pr == null || !pr.isValid()) return;
    int i = @SEV@.getAssetMap().getIndex(SND_FAIL);
    if (i >= 0) @SNU@.playSoundEvent2dToPlayer(pr, i, @SCAT@.SFX);
  } catch (Throwable t) { }
}""")
M(abil, r"""
public static void refuse(@PR@ pr, String text) {
  try {
    if (pr == null) return;
    long gap = Math.round(@PKG@.AbilCfg.REFUSE * 1000.0);
    if (!@PKG@.AbilStore.throttle(pr.getUuid(), System.currentTimeMillis(), gap)) return;
  } catch (Throwable t) { return; }
  send(pr, text, "#ffc800");
  failSound(pr);
}""")
# FIX ROUND 2: a throttled refusal with no line (row abil.cdMessage off) - the click only
M(abil, r"""
public static void click(@PR@ pr) {
  try {
    if (pr == null) return;
    long gap = Math.round(@PKG@.AbilCfg.REFUSE * 1000.0);
    if (!@PKG@.AbilStore.throttle(pr.getUuid(), System.currentTimeMillis(), gap)) return;
  } catch (Throwable t) { return; }
  failSound(pr);
}""")
M(abil, r"""
public static int level(java.util.UUID u, int ci) {
  try {
    Object f = @PKG@.ClassCfg.bridge().get("skill:fn:level");
    if (!(f instanceof java.util.function.Function)) return (int) @PKG@.AbilCfg.UNLOCK_A1;   // no SkyySkills: Ability 1 only
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, @PKG@.ClassDefs.SKILLS[ci] });
    if (r instanceof Number) {
      int l = ((Number) r).intValue();
      return l < 0 ? 0 : l;
    }
  } catch (Throwable t) { }
  return 0;
}""")
M(abil, r"""
public static long combatMs(java.util.UUID u) {
  try {
    Object f = @PKG@.ClassCfg.bridge().get("skill:fn:combat");
    if (!(f instanceof java.util.function.Function)) return 0L;
    Object r = ((java.util.function.Function) f).apply(u);
    return r instanceof Number ? ((Number) r).longValue() : 0L;
  } catch (Throwable t) { return 0L; }
}""")
M(abil, r"""
public static String hand(@CAC@ acc, @REF@ r) {
  try {
    java.util.function.Function f = HAND;
    if (f != null) {
      Object o = f.apply(r);
      return o == null ? null : String.valueOf(o);
    }
    @IS@ it = @INVC@.getItemInHand(acc, r);
    return (it == null || it.isEmpty()) ? null : it.getItemId();
  } catch (Throwable t) { return null; }
}""")
M(abil, r"""
public static boolean crouching(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @MSC@.getComponentType());
    if (!(o instanceof @MSC@)) return false;
    @MST@ m = ((@MSC@) o).getMovementStates();
    return m != null && m.crouching;
  } catch (Throwable t) { return false; }
}""")
M(abil, r"""
public static @ESM@ map(@CAC@ acc, @REF@ r) {
  try { return (@ESM@) acc.getComponent(r, @ESM@.getComponentType()); } catch (Throwable t) { return null; }
}""")
M(abil, r"""
public static double cur(@ESM@ m, int i) {
  if (m == null || i < 0) return -1.0;
  @ESV@ v = m.get(i);
  return v == null ? -1.0 : (double) v.get();
}""")
M(abil, r"""
public static double max(@ESM@ m, int i) {
  if (m == null || i < 0) return -1.0;
  @ESV@ v = m.get(i);
  return v == null ? -1.0 : (double) v.getMax();
}""")
M(abil, r"""
public static boolean alive(@CAC@ acc, @REF@ r) {
  try {
    if (r == null || !r.isValid()) return false;
    if (acc.getComponent(r, @DTH@.getComponentType()) != null) return false;
    @ESM@ m = map(acc, r);
    if (m == null) return true;
    double h = cur(m, @DST@.getHealth());
    return h < 0.0 || h > 0.0;
  } catch (Throwable t) { return false; }
}""")
M(abil, r"""
public static boolean creative(@CAC@ acc, @REF@ r) {
  try { return @PKG@.Kit.creative((@PLA@) acc.getComponent(r, @PLA@.getComponentType())); } catch (Throwable t) { return false; }
}""")
M(abil, r"""
public static @VEC@ pos(@CAC@ acc, @REF@ r) {
  try {
    @TC@ tc = (@TC@) acc.getComponent(r, @TC@.getComponentType());
    return tc == null ? null : tc.getPosition();
  } catch (Throwable t) { return null; }
}""")
# the spot the player looks at within range blocks (the first block hit; null = nothing that close)
M(abil, r"""
public static double[] aim(@CAC@ acc, @REF@ r, double range) {
  try {
    double[] a = null;
    java.util.function.Function f = AIM;
    if (f != null) {
      Object o = f.apply(new Object[] { r, Double.valueOf(range) });
      if (o instanceof double[]) a = (double[]) o;
    } else {
      @VEC@ v = @TU@.getTargetLocation(r, range, acc);
      if (v != null) a = new double[] { v.x, v.y, v.z };
    }
    if (a == null || a.length < 3) return null;
    @VEC@ p = pos(acc, r);
    if (p != null && !@PKG@.AbilMath.inRange(a[0] - p.x, a[1] - p.y, a[2] - p.z, range + 2.0)) return null;
    return a;
  } catch (Throwable t) { return null; }
}""")
M(abil, r"""
public static java.util.List near(@CAC@ acc, double x, double y, double z, double r) {
  try {
    java.util.function.Function f = NEAR;
    if (f != null) {
      Object o = f.apply(new double[] { x, y, z, r });
      return o instanceof java.util.List ? new java.util.ArrayList((java.util.List) o) : new java.util.ArrayList();
    }
    java.util.List l = @TU@.getAllEntitiesInSphere(new @VEC@(x, y, z), r, acc);
    return l == null ? new java.util.ArrayList() : new java.util.ArrayList(l);
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("ability area query failed: " + t); return new java.util.ArrayList(); }
}""")
M(abil, r"""
public static void particle(String id, double x, double y, double z, @CAC@ acc) {
  java.util.List seen = PSEEN;
  if (seen != null) seen.add(id);
  try { @PTU@.spawnParticleEffect(id, new @VEC@(x, y, z), acc); } catch (Throwable t) { if (seen == null) @PKG@.ClassCfg.warnLimited("ability particle " + id + " failed: " + t); }
}""")
M(abil, r"""
public static double hOf(String item) {
  Object[] a = null;
  try {
    Object f = @PKG@.ClassCfg.bridge().get("armory:fn:info");
    if (f instanceof java.util.function.Function && item != null) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { "staff", item });
      if (!(r instanceof Object[])) r = ((java.util.function.Function) f).apply(new Object[] { "wand", item });
      // FIX ROUND 2 (critic: spellbooks got the flat fallback): a spellbook = the charged shot of its same-metal SkyyArmory staff
      if (!(r instanceof Object[]) && item.startsWith("Weapon_Spellbook_"))
        r = ((java.util.function.Function) f).apply(new Object[] { "staff", "Weapon_Staff_" + item.substring(17) });
      if (r instanceof Object[]) a = (Object[]) r;
    }
  } catch (Throwable t) { a = null; }
  return @PKG@.AbilMath.hOf(a, @PKG@.AbilCfg.H_FALLBACK);
}""")
# an NPC enemy: alive, with stats, not a player (no PvP from abilities in R1), not Invulnerable (traders), no abil.safeWords role (pets, mounts)
M(abil, r"""
public static boolean enemy(@CAC@ acc, @REF@ t, @REF@ caster) {
  try {
    if (t == null || !t.isValid()) return false;
    if (caster != null && t.equals(caster)) return false;
    if (acc.getComponent(t, @PR@.getComponentType()) != null) return false;
    Object no = acc.getComponent(t, @NPC@.getComponentType());
    if (no == null) return false;
    if (acc.getComponent(t, @INVU@.getComponentType()) != null) return false;
    // FIX ROUND (critic: tamed / mount / pet NPCs that are not Invulnerable were hit): a role holding an abil.safeWords word is never hit
    String role = null;
    try { if (no instanceof @NPC@) role = ((@NPC@) no).getRoleName(); } catch (Throwable r0) { role = null; }
    if (@PKG@.AbilMath.words(role, @PKG@.AbilCfg.SAFE_WORDS)) return false;
    if (map(acc, t) == null) return false;
    return alive(acc, t);
  } catch (Throwable x) { return false; }
}""")
# one ability hit through the WHOLE damage pipeline (Filter: class lock - skipped by the tag -, Gear / Armory tune, armour; Inspect;
# Apply; death = the caster's kill): the SkyyArmory ArmoryTrav.hit shape, Damage$EntitySource(caster), cause PROJECTILE
M(abil, r"""
public static boolean hit(@CB@ buf, @REF@ t, @REF@ caster, java.util.UUID cu, double amount, String what) {
  try {
    if (!(amount > 0.0) || caster == null || !caster.isValid() || t == null || !t.isValid()) return false;
    @DCS@ cause = @DCS@.PROJECTILE;
    if (cause == null) return false;
    @DMG@ d = new @DMG@(new @DENT@(caster), cause, (float) amount);
    @PKG@.AbilDmg.tag(d, cu, what);
    @DSYS@.executeDamage(t, buf, d);
    return true;
  } catch (Throwable x) { @PKG@.ClassCfg.warnLimited("an ability hit failed: " + x); return false; }
}""")
# heal one player by want, at most capLeft, never above max Health; returns the HP really healed
M(abil, r"""
public static double apply(@CAC@ acc, @REF@ r, double want, double capLeft) {
  if (want > capLeft) want = capLeft;
  if (!(want > 0.01)) return 0.0;
  @ESM@ m = map(acc, r);
  if (m == null) return 0.0;
  int hi = @DST@.getHealth();
  if (hi < 0) return 0.0;
  @ESV@ hv = m.get(hi);
  if (hv == null) return 0.0;
  double ask = @PKG@.HealTask.room(want, hv.get(), hv.getMax());
  if (!(ask > 0.01)) return 0.0;
  m.addStatValue(hi, (float) ask);
  return ask;
}""")
# a player who can be healed now: ready, not creative, alive
M(abil, r"""
public static boolean healable(@CAC@ acc, @REF@ r) {
  try {
    if (r == null || !r.isValid()) return false;
    @PLA@ pl = (@PLA@) acc.getComponent(r, @PLA@.getComponentType());
    if (pl == null || pl.isWaitingForClientReady() || @PKG@.Kit.creative(pl)) return false;
    return alive(acc, r);
  } catch (Throwable t) { return false; }
}""")
# ---- METEOR (walking shape): the warning at the spot now, the impact ab.Meteor.delay later (AbilTick)
M(abil, r"""
public static String meteorCast(@ST@ st, java.util.UUID u, @PKG@.AbilWorld aw, double[] at, String item, long now) {
  double h = hOf(item);
  double amt = h * @PKG@.AbilCfg.M_POWER;
  long delay = Math.round(@PKG@.AbilCfg.M_DELAY * 1000.0);
  @PKG@.AbilJob j = new @PKG@.AbilJob(1, now + delay, u, "Meteor", at[0], at[1], at[2], @PKG@.AbilCfg.M_RADIUS, amt);
  j.pkey = @PKG@.ClassCfg.pkey(u);
  particle(FX_MARK, at[0], at[1] + 0.1, at[2], st);
  aw.add(j);   // FIX ROUND: last - castNow refunds a cast whose executor throws, so nothing may be queued before that point
  return " H=" + @PKG@.AbilMath.fmt(h) + " damage=" + @PKG@.AbilMath.fmt(amt) + " at=" + @PKG@.AbilMath.fmt(at[0]) + "," + @PKG@.AbilMath.fmt(at[1]) + "," + @PKG@.AbilMath.fmt(at[2]);
}""")
M(abil, r"""
public static int meteorImpact(@PKG@.AbilJob j, @ST@ st, @CB@ cb) {
  particle(FX_HIT, j.x, j.y + 0.5, j.z, cb);
  @REF@ cr = null;
  try { cr = ((@ES@) cb.getExternalData()).getRefFromUUID(j.caster); } catch (Throwable t) { cr = null; }
  if (cr == null || !cr.isValid()) { j.hits = 0; return 0; }          // the caster left this world: the meteor lands, nobody is hurt
  // FIX ROUND (critics: a profile switch before the impact paid the NEW profile's class XP): the caster switched profile -> nobody is hurt
  if (j.pkey != null && !j.pkey.equals(@PKG@.ClassCfg.pkey(j.caster))) { j.hits = 0; return 0; }
  java.util.List l = near(cb, j.x, j.y, j.z, j.r);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t)) continue;
    if (!enemy(cb, t, cr)) continue;
    if (hit(cb, t, cr, j.caster, j.amount, "Meteor")) n++;
  }
  j.hits = n;
  @PR@ pr = @UNI@.get().getPlayer(j.caster);
  if (pr != null) say(pr, n == 0 ? "Meteor hit nothing." : "Meteor hit " + n + (n == 1 ? " enemy" : " enemies") + " (" + @PKG@.AbilMath.fmt(j.amount) + " damage each before armour).");
  return n;
}""")
# ---- SACRED HEAL (walking shape): the instant heal now (the Priest + players within range), a heal-over-time job for those healed
# the other players of this world within rad blocks of c (us = uuids, rs = refs; the caller puts the Priest first)
M(abil, r"""
public static void gather(@ST@ st, java.util.UUID u, @VEC@ c, double rad, java.util.ArrayList us, java.util.ArrayList rs) {
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ p = (@PR@) it.next();
    if (p == null || !p.isValid()) continue;
    java.util.UUID pu = p.getUuid();
    if (pu == null || pu.equals(u)) continue;
    @REF@ r = p.getReference();
    if (r == null || !r.isValid() || r.getStore() != st) continue;
    @VEC@ q = pos(st, r);
    if (q == null || !@PKG@.AbilMath.inRange(q.x - c.x, q.y - c.y, q.z - c.z, rad)) continue;
    us.add(pu);
    rs.add(r);
  }
}""")
# FIX ROUND (critic: a Sacred Heal with nobody hurt still cost 18 Mana + the cooldown; plan 4.1 "refusals cost nothing", spec draft: the cast
# counts when it heals someone): how many players in range would really be healed now (healable, below max Health, a heal share > 0)
M(abil, r"""
public static int needHeal(@ST@ st, @REF@ ref, java.util.UUID u) {
  @VEC@ c = pos(st, ref);
  if (c == null) return 0;
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  us.add(u);
  rs.add(ref);
  gather(st, u, c, @PKG@.AbilCfg.S_RADIUS, us, rs);
  int n = 0;
  for (int i = 0; i < us.size(); i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    @REF@ r = (@REF@) rs.get(i);
    if (!healable(st, r)) continue;
    @ESM@ m = map(st, r);
    double mx = max(m, @DST@.getHealth());
    double h = cur(m, @DST@.getHealth());
    if (!(mx > 0.0) || !(h >= 0.0) || !(mx - h > 0.01)) continue;
    boolean isSelf = t.equals(u);
    boolean party = isSelf || @PKG@.HealTask.inParty(u, t);
    double want = @PKG@.HealTask.split(@PKG@.AbilMath.heal(mx, @PKG@.AbilCfg.S_HEAL, isSelf, @PKG@.AbilCfg.S_SELF), party, @PKG@.ClassCfg.HEAL_OTHERS_PCT);
    if (want > 0.01) n++;
  }
  return n;
}""")
# FIX ROUND 2 (critic: an error after the first heal / the XP refunded the cast, so the heals + XP stayed free): PREPARE every fallible
# step first (party checks, each target's amount and cap, the heal-over-time job) - an error there is refunded by castNow; then COMMIT
# (heals, lines, XP, the job): an error there ends the cast where it is, NO refund (heals may have landed) and no XP for the unfinished cast
M(abil, r"""
public static String healCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, @PKG@.AbilWorld aw, long now) {
  @VEC@ c = pos(st, ref);
  if (c == null) return " nopos";
  double rad = @PKG@.AbilCfg.S_RADIUS;
  boolean xpOk = !creative(st, ref);
  String healer = pr.getUsername();
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  us.add(u);
  rs.add(ref);
  gather(st, u, c, rad, us, rs);
  int n = us.size();
  java.util.UUID[] tu = new java.util.UUID[n];
  double[] want = new double[n];
  double[] per = new double[n];
  double[] done = new double[n];
  double[] cap = new double[n];
  boolean[] go = new boolean[n];
  int ticks = @PKG@.AbilMath.ticks(@PKG@.AbilCfg.S_HOT_TIME);
  for (int i = 0; i < n; i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    @REF@ r = (@REF@) rs.get(i);
    tu[i] = t;
    if (!healable(st, r)) continue;
    double mx = max(map(st, r), @DST@.getHealth());
    if (!(mx > 0.0)) continue;
    boolean isSelf = t.equals(u);
    boolean party = isSelf || @PKG@.HealTask.inParty(u, t);
    want[i] = @PKG@.HealTask.split(@PKG@.AbilMath.heal(mx, @PKG@.AbilCfg.S_HEAL, isSelf, @PKG@.AbilCfg.S_SELF), party, @PKG@.ClassCfg.HEAL_OTHERS_PCT);
    cap[i] = @PKG@.AbilMath.capLeft(mx, @PKG@.AbilCfg.HEAL_CAP, 0.0);
    if (ticks > 0) per[i] = want[i] * (double) @PKG@.AbilCfg.S_HOT / 100.0 / (double) ticks;
    go[i] = true;
  }
  @PKG@.AbilJob j = null;
  if (ticks > 0 && @PKG@.AbilCfg.S_HOT > 0L) {
    long every = Math.round(@PKG@.AbilCfg.S_HOT_TIME * 1000.0 / (double) ticks);
    if (every < 50L) every = 50L;
    j = new @PKG@.AbilJob(2, now + every, u, "SacredHeal", c.x, c.y, c.z, rad, 0.0);
    j.targets = tu;
    j.per = per;
    j.done = done;
    j.cap = cap;
    j.left = ticks;
    j.every = every;
    j.name = healer;
    j.pkey = @PKG@.ClassCfg.pkey(u);
  }
  double others = 0.0;
  double self = 0.0;
  int healed = 0;
  try {
    for (int i = 0; i < n; i++) {
      if (!go[i]) continue;
      java.util.UUID t = tu[i];
      @REF@ r = (@REF@) rs.get(i);
      double got = apply(st, r, want[i], cap[i]);
      done[i] = got;
      @VEC@ q = pos(st, r);
      if (q != null) particle(FX_HEAL, q.x, q.y + 1.0, q.z, st);
      if (!(got > 0.0)) continue;
      healed++;
      if (t.equals(u)) { self = self + got; @PKG@.HealMsg.given(u, u, got); }
      else { others = others + got; @PKG@.HealMsg.given(u, t, got); @PKG@.HealMsg.taken(t, u, healer, got); }
    }
    if (xpOk) {
      if (others > 0.0) @PKG@.HealTask.xp(u, others);
      if (self > 0.0) @PKG@.HealTask.xpSelf(u, self);
    }
    if (j != null) aw.add(j);
  } catch (Throwable x) {
    @PKG@.ClassCfg.warn("Sacred Heal stopped after " + healed + " heal(s) - no refund (heals already landed), no XP, no heal over time: " + x);
    return " partial healed=" + healed + " hp=" + @PKG@.AbilMath.fmt(others + self);
  }
  say(pr, "Sacred Heal: " + (healed == 0 ? "nobody needed healing" : "+" + @PKG@.AbilMath.fmt(others + self) + " HP to " + healed + (healed == 1 ? " player" : " players")) + (j != null ? ", healing over " + ticks + " s." : "."));
  return " targets=" + n + " healed=" + healed + " hp=" + @PKG@.AbilMath.fmt(others + self);
}""")
# one heal-over-time pulse (AbilTick, the world thread); true = more pulses follow
M(abil, r"""
public static boolean hotTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb) {
  double others = 0.0;
  double self = 0.0;
  boolean xpOk = false;
  @PR@ hp = @UNI@.get().getPlayer(j.caster);
  if (hp != null && hp.isValid()) {
    @REF@ hr = hp.getReference();
    xpOk = hr != null && hr.isValid() && !(hr.getStore() == st && creative(cb, hr));
  }
  // FIX ROUND (critics): the Priest switched profile since the cast -> the pulses still heal, but pay no Divinity XP to the new profile
  if (xpOk && j.pkey != null && !j.pkey.equals(@PKG@.ClassCfg.pkey(j.caster))) xpOk = false;
  for (int i = 0; j.targets != null && i < j.targets.length; i++) {
    if (j.per == null || i >= j.per.length || !(j.per[i] > 0.0)) continue;
    java.util.UUID t = j.targets[i];
    @PR@ tp = @UNI@.get().getPlayer(t);
    if (tp == null || !tp.isValid()) continue;
    @REF@ tr = tp.getReference();
    if (tr == null || !tr.isValid() || tr.getStore() != st) continue;
    if (!healable(cb, tr)) continue;
    double got = apply(cb, tr, j.per[i], j.cap[i] - j.done[i]);
    j.done[i] = j.done[i] + got;
    if (!(got > 0.0)) continue;
    if (t.equals(j.caster)) { self = self + got; @PKG@.HealMsg.given(j.caster, j.caster, got); }
    else { others = others + got; @PKG@.HealMsg.given(j.caster, t, got); @PKG@.HealMsg.taken(t, j.caster, j.name, got); }
  }
  if (xpOk) {
    if (others > 0.0) @PKG@.HealTask.xp(j.caster, others);
    if (self > 0.0) @PKG@.HealTask.xpSelf(j.caster, self);
  }
  j.left = j.left - 1;
  j.at = j.at + j.every;
  return j.left > 0;
}""")
M(abil, r"""
public static boolean runJob(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  if (j == null) return false;
  if (j.kind == 1) { meteorImpact(j, st, cb); return false; }
  if (j.kind == 2) return hotTick(j, st, cb);
  return false;
}""")
M(abil, r"""
public static String noClass() {
  return @PKG@.ClassCfg.profilesOn() ? "Create a profile with a class (/profiles) to get abilities." : "Choose a class with /class to get abilities.";
}""")
'''
ENGINE_CAST = r'''
M(abil, r"""
public static String castNow(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg) {
  if (pr == null || st == null || ref == null || !ref.isValid()) return "bad";
  java.util.UUID u = pr.getUuid();
  if (!@PKG@.AbilCfg.PART) { refuse(pr, "Class abilities are switched off on this server."); return "off"; }
  int slot = @PKG@.AbilMath.slotOf(arg);
  if (slot < 0) { send(pr, "Usage: /cast 1 or /cast 2 (crouch = your alt), /cast 3 or 4 = your alts, /cast list, /cast swap", "#ffc800"); return "usage"; }
  if (@PKG@.Kit.busy(u)) { refuse(pr, "Your profile is still loading - try again in a moment."); return "busy"; }
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0) { refuse(pr, noClass()); return "noclass"; }
  if (!@PKG@.AbilDefs.classHas(ci) || !@PKG@.ClassDefs.ENABLED[ci]) { refuse(pr, @PKG@.ClassDefs.NAMES[ci] + " abilities are coming later - the Mage and the Priest get theirs first."); return "noabil"; }
  if (!alive(st, ref)) return "dead";
  boolean crouch = crouching(st, ref);
  int s = @PKG@.AbilMath.resolve(slot, crouch);
  String k = @PKG@.ClassCfg.pkey(u);
  String[] sl = @PKG@.AbilStore.slots(k, ci);
  int ai = @PKG@.AbilDefs.find(sl[s]);
  if (ai < 0) { refuse(pr, "No ability on " + @PKG@.AbilDefs.key(s) + "."); return "empty"; }
  String nm = @PKG@.AbilDefs.NAMES[ai];
  int lv = level(u, ci);
  if (!@PKG@.AbilDefs.owns(ai, lv, @PKG@.AbilStore.granted(k), @PKG@.AbilStore.pick(k))) {
    refuse(pr, (s >= 2 ? "No alt yet - " : "") + nm + " unlocks at " + @PKG@.ClassDefs.SKILLS[ci] + " " + @PKG@.AbilDefs.unlock(@PKG@.AbilDefs.TIER[ai]) + " (you are " + lv + ").");
    return "locked";
  }
  if (@PKG@.AbilDefs.PASSIVE[ai]) { refuse(pr, nm + " is a passive - it will work on its own once it is built (a later update)."); return "passive"; }
  if (!@PKG@.AbilDefs.BUILT[ai]) { refuse(pr, nm + " comes in a later update - nothing was spent."); return "soon"; }
  String item = hand(st, ref);
  if (item == null || @PKG@.ClassDefs.ownerOf(item) != ci || !@PKG@.ClassRules.allowed(u, item)) {
    refuse(pr, "Hold your " + @PKG@.ClassDefs.NAMES[ci] + " weapon (" + @PKG@.ClassDefs.WTEXT[ci] + ") to cast " + nm + ".");
    return "weapon";
  }
  long now = System.currentTimeMillis();
  String id = @PKG@.AbilDefs.IDS[ai];
  long left = @PKG@.AbilStore.left(k, id, now);
  if (left > 0L) {
    if (@PKG@.AbilCfg.CD_MSG) refuse(pr, nm + " is " + @PKG@.AbilMath.readyText(left) + ".");
    else click(pr);   // FIX ROUND 2: row abil.cdMessage off = the click only
    return "cooldown";
  }
  boolean free = @PKG@.AbilCfg.CREATIVE_FREE && creative(st, ref);
  double mana = free ? 0.0 : @PKG@.AbilDefs.mana(ai);
  double stam = free ? 0.0 : @PKG@.AbilDefs.stamina(ai);
  @ESM@ m = map(st, ref);
  int mi = @DST@.getMana();
  int si = @DST@.getStamina();
  double hm = cur(m, mi);
  double hs = cur(m, si);
  // FIX ROUND 2 (critic: an unreadable stat skipped both the check and the payment = a free cast): a cost needs its stat
  if ((mana > 0.0 && !(hm >= 0.0)) || (stam > 0.0 && !(hs >= 0.0))) {
    refuse(pr, "Your Mana and Stamina are not ready yet - try again in a moment (nothing was spent).");
    return "nostats";
  }
  if (mana > 0.0 && hm >= 0.0 && !@PKG@.AbilMath.enough(hm, mana)) {
    refuse(pr, "Not enough Mana for " + nm + ": " + @PKG@.AbilMath.fmt(hm) + " / " + @PKG@.AbilMath.fmt(mana) + ".");
    return "mana";
  }
  if (stam > 0.0 && hs >= 0.0 && !@PKG@.AbilMath.enough(hs, stam)) {
    refuse(pr, "Not enough Stamina for " + nm + ": " + @PKG@.AbilMath.fmt(hs) + " / " + @PKG@.AbilMath.fmt(stam) + ".");
    return "stamina";
  }
  double[] at = null;
  if (ai == @PKG@.AbilDefs.METEOR) {
    at = aim(st, ref, @PKG@.AbilCfg.M_RANGE);
    if (at == null) { refuse(pr, "Look at the ground within " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.M_RANGE) + " blocks to call the Meteor down - nothing was spent."); return "aim"; }
  }
  if (ai == @PKG@.AbilDefs.SACRED && needHeal(st, ref, u) == 0) {   // FIX ROUND: nobody to heal = a refusal (nothing spent, no cooldown)
    refuse(pr, "Nobody within " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.S_RADIUS) + " blocks needs healing - nothing was spent.");
    return "noneed";
  }
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(w == null ? @PKG@.AbilWorld.nameOf(st.getExternalData()) : w.getName());
  if (aw.full()) { refuse(pr, "Too many abilities are running in this world - try again in a moment."); return "full"; }
  if (mana > 0.0 && hm >= 0.0) m.subtractStatValue(mi, (float) mana);
  if (stam > 0.0 && hs >= 0.0) m.subtractStatValue(si, (float) stam);
  long cd = @PKG@.AbilDefs.cdMs(ai);
  @PKG@.AbilStore.arm(k, id, now, cd);
  say(pr, nm + "! -" + @PKG@.AbilMath.fmt(mana) + " Mana, -" + @PKG@.AbilMath.fmt(stam) + " Stamina. Ready again in " + @PKG@.AbilMath.secs(cd) + " s.");
  String extra = "";
  // FIX ROUND (critic: an executor that throws after the payment kept the Mana, Stamina and cooldown): give all three back
  try {
    if (ai == @PKG@.AbilDefs.METEOR) extra = meteorCast(st, u, aw, at, item, now);
    else if (ai == @PKG@.AbilDefs.SACRED) extra = healCast(pr, st, ref, u, aw, now);
  } catch (Throwable x) {
    if (mana > 0.0 && hm >= 0.0) m.addStatValue(mi, (float) mana);
    if (stam > 0.0 && hs >= 0.0) m.addStatValue(si, (float) stam);
    @PKG@.AbilStore.arm(k, id, now, 0L);
    @PKG@.ClassCfg.warn("ability " + id + " failed after paying - Mana, Stamina and the cooldown were given back: " + x);
    send(pr, nm + " could not be cast - your Mana, Stamina and cooldown were given back (the server log has the details).", "#ffc800");
    return "failed";
  }
  return "ok:" + id + (crouch && slot < 2 ? " crouch" : "") + " mana=" + @PKG@.AbilMath.fmt(mana) + " stamina=" + @PKG@.AbilMath.fmt(stam) + extra;
}""")
# ---- THE PIPELINE (engine spec 4; plan 4.1). Returns the outcome (LAST): ok:<id> ... or the refusal word. World thread (the command).
M(abil, r"""
public static String cast(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg) {
  String r = castNow(pr, st, ref, w, arg);
  LAST = r;
  return r;
}""")
'''
ENGINE_REST = r'''
# ---- /cast list, /cast swap, /classadmin abil, the HUD bridge
M(abil, r"""
public static String stateOf(int ai, String k, int lv, boolean grant, String pick, long now) {
  if (ai < 0) return "empty";
  if (!@PKG@.AbilDefs.owns(ai, lv, grant, pick)) return "locked";
  if (@PKG@.AbilDefs.PASSIVE[ai]) return "passive";
  if (!@PKG@.AbilDefs.BUILT[ai]) return "soon";
  return @PKG@.AbilStore.left(k, @PKG@.AbilDefs.IDS[ai], now) > 0L ? "cooldown" : "ready";
}""")
M(abil, r"""
public static String[] listLines(java.util.UUID u) {
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0) return new String[] { noClass() };
  if (!@PKG@.AbilDefs.classHas(ci)) return new String[] { @PKG@.ClassDefs.NAMES[ci] + " abilities are coming later - the Mage and the Priest get theirs first." };
  String k = @PKG@.ClassCfg.pkey(u);
  int lv = level(u, ci);
  boolean grant = @PKG@.AbilStore.granted(k);
  String pick = @PKG@.AbilStore.pick(k);
  String[] sl = @PKG@.AbilStore.slots(k, ci);
  long now = System.currentTimeMillis();
  String[] out = new String[6];
  out[0] = "Abilities - " + @PKG@.ClassDefs.NAMES[ci] + ", " + @PKG@.ClassDefs.SKILLS[ci] + " " + lv + (grant ? " (admin grant: all four)" : "") + (@PKG@.AbilCfg.PART ? "" : " - switched OFF on this server") + ":";
  for (int i = 0; i < 4; i++) {
    int ai = @PKG@.AbilDefs.find(sl[i]);
    String st = stateOf(ai, k, lv, grant, pick, now);
    String nm = ai < 0 ? "-" : @PKG@.AbilDefs.NAMES[ai];
    String tx = st;
    if (st.equals("ready")) tx = "ready (" + @PKG@.AbilMath.fmt(@PKG@.AbilDefs.mana(ai)) + " Mana + " + @PKG@.AbilMath.fmt(@PKG@.AbilDefs.stamina(ai)) + " Stamina, cooldown " + @PKG@.AbilMath.secs(@PKG@.AbilDefs.cdMs(ai)) + " s)";
    if (st.equals("cooldown")) tx = @PKG@.AbilMath.readyText(@PKG@.AbilStore.left(k, @PKG@.AbilDefs.IDS[ai], now));
    if (st.equals("locked")) tx = "unlocks at " + @PKG@.ClassDefs.SKILLS[ci] + " " + @PKG@.AbilDefs.unlock(@PKG@.AbilDefs.TIER[ai]);
    if (st.equals("soon")) tx = "comes in a later update";
    if (st.equals("passive")) tx = "passive - comes in a later update";
    out[i + 1] = "  " + @PKG@.AbilDefs.key(i) + ": " + nm + " - " + tx;
  }
  out[5] = "  /cast swap = swap your two primaries (out of combat). Hytale 0.7 brings real ability keys.";
  return out;
}""")
M(abil, r"""
public static String[] list(@PR@ pr) {
  String[] l = listLines(pr.getUuid());
  for (int i = 0; i < l.length; i++) send(pr, l[i], i == 0 ? "#8fe39a" : null);
  return l;
}""")
M(abil, r"""
public static String swap(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0 || !@PKG@.AbilDefs.classHas(ci)) { send(pr, ci < 0 ? noClass() : "Your class has no abilities yet.", "#ffc800"); return "noclass"; }
  if (combatMs(u) > 0L) { send(pr, "Leave combat first - abilities are swapped only out of combat.", "#ffc800"); return "combat"; }
  String k = @PKG@.ClassCfg.pkey(u);
  String[] sl = @PKG@.AbilStore.slots(k, ci);
  // FIX ROUND 2 (critic: a level-1 Mage could swap a locked ability onto /cast 1): both primaries must be owned
  int lv = level(u, ci);
  boolean grant = @PKG@.AbilStore.granted(k);
  String pick = @PKG@.AbilStore.pick(k);
  for (int i = 0; i < 2; i++) {
    int ai = @PKG@.AbilDefs.find(sl[i]);
    if (ai >= 0 && !@PKG@.AbilDefs.owns(ai, lv, grant, pick)) {
      send(pr, "Both primaries must be unlocked to swap - " + @PKG@.AbilDefs.NAMES[ai] + " unlocks at " + @PKG@.ClassDefs.SKILLS[ci] + " " + @PKG@.AbilDefs.unlock(@PKG@.AbilDefs.TIER[ai]) + " (you are " + lv + ").", "#ffc800");
      return "locked";
    }
  }
  if (!@PKG@.AbilStore.set(k, new String[] { "p1", "p2", "a1", "a2" }, new String[] { sl[1], sl[0], sl[2], sl[3] })) {
    send(pr, "Your ability file could not be read - nothing changed (see the server log).", "#ffc800");
    return "unread";
  }
  @PKG@.AbilStore.saveSoon(k);
  send(pr, "Swapped: /cast 1 = " + @PKG@.AbilDefs.NAMES[@PKG@.AbilDefs.find(sl[1])] + ", /cast 2 = " + @PKG@.AbilDefs.NAMES[@PKG@.AbilDefs.find(sl[0])] + ".", "#8fe39a");
  return "ok";
}""")
M(abil, r"""
public static String adminDo(@PR@ pr, String who, String act) {
  java.util.UUID t = @PKG@.ClassStore.resolve(who);
  if (t == null) { send(pr, "Unknown player - use an online name or a uuid.", "#ffc800"); return "who"; }
  String k = @PKG@.ClassCfg.pkey(t);
  String a = act == null ? "" : act.trim().toLowerCase();
  if (a.equals("grant") || a.equals("ungrant")) {
    boolean on = a.equals("grant");
    if (!@PKG@.AbilStore.set(k, new String[] { "grant" }, new String[] { on ? "true" : null })) { send(pr, "The ability file of " + k + " could not be read - nothing changed.", "#ffc800"); return "unread"; }
    @PKG@.AbilStore.saveSoon(k);
    send(pr, (on ? "Granted all four abilities to " : "Removed the ability grant of ") + t + " (profile " + k + ") - for testing; class levels decide again after ungrant.", "#8fe39a");
    @PR@ tp = @UNI@.get().getPlayer(t);
    if (tp != null && tp.isValid() && on) send(tp, "An admin granted you all four class abilities for testing - /cast list.", "#8fe39a");
    return on ? "grant" : "ungrant";
  }
  if (a.equals("reset")) {
    int n = @PKG@.AbilStore.clearCd(k);
    send(pr, "Cleared " + n + " ability cooldown(s) of " + t + " (profile " + k + ").", "#8fe39a");
    return "reset";
  }
  if (a.equals("info")) {
    String[] l = listLines(t);
    for (int i = 0; i < l.length; i++) send(pr, (i == 0 ? t + ": " : "") + l[i], null);
    send(pr, "Last cast on this server: " + LAST, null);
    return "info";
  }
  send(pr, "Usage: /classadmin abil <player|uuid> <grant|ungrant|reset|info>", "#ffc800");
  return "usage";
}""")
# the node is re-checked here (the command's requirePermission is the first gate); a permission lookup that throws = no permission
M(abil, r"""
public static String admin(@PR@ pr, String who, String act) {
  boolean ok = false;
  try { ok = pr.hasPermission("skyyclasses.admin"); } catch (Throwable t) { ok = false; }
  if (!ok) { send(pr, "no permission (skyyclasses.admin)", "#ffc800"); return "denied"; }
  return adminDo(pr, who, act);
}""")
# class:fn:abil apply(UUID) -> Object[16] = 4 x {String name, Long msLeft, Long msTotal, String state} (p1, p2, a1, a2); null = no class with
# abilities. Any thread (memory + one cached file read), never throws.
abfn = pool.makeClass(PKG + ".AbilFn")
abfn.addInterface(pool.get("java.util.function.Function"))
C(abfn, "public AbilFn() { }")
M(abfn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof java.util.UUID)) return null;
    java.util.UUID u = (java.util.UUID) o;
    int ci = @PKG@.ClassStore.classIndex(u);
    if (!@PKG@.AbilDefs.classHas(ci)) return null;
    String k = @PKG@.ClassCfg.pkey(u);
    int lv = @PKG@.Abil.level(u, ci);
    boolean grant = @PKG@.AbilStore.granted(k);
    String pick = @PKG@.AbilStore.pick(k);
    String[] sl = @PKG@.AbilStore.slots(k, ci);
    long now = System.currentTimeMillis();
    Object[] out = new Object[16];
    for (int i = 0; i < 4; i++) {
      int ai = @PKG@.AbilDefs.find(sl[i]);
      out[i * 4] = ai < 0 ? "" : @PKG@.AbilDefs.NAMES[ai];
      out[i * 4 + 1] = Long.valueOf(ai < 0 ? 0L : @PKG@.AbilStore.left(k, @PKG@.AbilDefs.IDS[ai], now));
      out[i * 4 + 2] = Long.valueOf(ai < 0 ? 0L : @PKG@.AbilStore.total(k, @PKG@.AbilDefs.IDS[ai]));
      out[i * 4 + 3] = @PKG@.Abil.stateOf(ai, k, lv, grant, pick, now);
    }
    return out;
  } catch (Throwable t) { return null; }
}""")
# ---- AbilWorld.run (after Abil: it calls the executors) + AbilTick
M(abworld, r"""
public void run(@ST@ st, @CB@ cb, long now) {
  java.util.ArrayList d = due(now);
  for (int i = 0; i < d.size(); i++) {
    @PKG@.AbilJob j = (@PKG@.AbilJob) d.get(i);
    boolean again = false;
    try { again = @PKG@.Abil.runJob(j, st, cb, now); } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("ability job failed: " + t); }
    if (again) add(j);
  }
}""")
abtick = pool.makeClass(PKG + ".AbilTick", pool.get(T["ETS"]))
C(abtick, "public AbilTick() { super(); }")
M(abtick, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(abtick, "public boolean isParallel(int a, int b) { return false; }")
M(abtick, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(store);
    if (aw == null || aw.idle()) return;
    long ns = System.nanoTime();
    if (ns - aw.lastNs < 20000000L && ns >= aw.lastNs) return;     // once per world tick (the first player of the tick runs it)
    aw.lastNs = ns;
    aw.run(store, cb, System.currentTimeMillis());
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("ability tick failed: " + t); }
}""")
# ---- /cast (player): bare = the list; the usage variant takes one word (HANDOFF COMMAND RULES 2: a variant per positional form)
castc = pool.makeClass(PKG + ".CastCmd", pool.get(T["APC"]))
casta = pool.makeClass(PKG + ".CastArgCmd", pool.get(T["APC"]))
F(casta, "public @RA@ slotArg;")
C(casta, r"""
public CastArgCmd() {
  super("Cast a class ability: /cast 1 or 2 (crouch = your alt), /cast 3 or 4 (alts), /cast list, /cast swap");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  this.slotArg = withRequiredArg("slot", "1 | 2 (crouch = alt) | 3 | 4 | list | swap", @ATY@.STRING);
}""")
M(casta, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    String a = String.valueOf(ctx.get(this.slotArg)).trim().toLowerCase();
    if (a.equals("list")) { @PKG@.Abil.list(pr); return; }
    if (a.equals("swap")) { @PKG@.Abil.swap(pr); return; }
    @PKG@.Abil.cast(pr, store, ref, world, a);
  } catch (Throwable t) {
    @PKG@.ClassCfg.warn("/cast failed: " + t);
    pr.sendMessage(@MSG@.raw("[Classes] Could not cast - the server log has the details."));
  }
}""")
C(castc, r"""
public CastCmd() {
  super("cast", "Cast a class ability: /cast 1 or /cast 2 (crouch = your alt), /cast 3 or 4 = alts, /cast list, /cast swap");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addUsageVariant(new @PKG@.CastArgCmd());
}""")
M(castc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.Abil.list(pr); } catch (Throwable t) { @PKG@.ClassCfg.warn("/cast list failed: " + t); }
}""")
# ---- /classadmin abil <player> <grant|ungrant|reset|info> (requirePermission + empty groups: the AdminKitCmd pattern)
aabil = pool.makeClass(PKG + ".AdminAbilCmd", pool.get(T["APC"]))
F(aabil, "public @RA@ playerArg;")
F(aabil, "public @RA@ actArg;")
C(aabil, r"""
public AdminAbilCmd() {
  super("abil", "(admin) Class abilities: /classadmin abil <player|uuid> <grant|ungrant|reset|info>");
  requirePermission("skyyclasses.admin");
  setPermissionGroups(new String[0]);
  this.playerArg = withRequiredArg("player", "online player name or uuid", @ATY@.STRING);
  this.actArg = withRequiredArg("action", "grant | ungrant | reset | info", @ATY@.STRING);
}""")
M(aabil, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.Abil.admin(pr, String.valueOf(ctx.get(this.playerArg)), String.valueOf(ctx.get(this.actArg))); }
  catch (Throwable t) { pr.sendMessage(@MSG@.raw("[Classes] Usage: /classadmin abil <player|uuid> <grant|ungrant|reset|info>")); }
}""")
'''
rep('''# ================= 0.1.6 KitHooks (config kit hooks: check= of the kit rows, the 7 "Use my hotbar" actions) + KitHotbarTask =================
''', ENGINE_SRC + ENGINE_CAST + ENGINE_REST + '''
# ================= 0.1.6 KitHooks (config kit hooks: check= of the kit rows, the 7 "Use my hotbar" actions) + KitHotbarTask =================
''')

# ================================================================================================ wiring: ready, quit, admin, setup, jar
rep('''    @PKG@.ClassStore.load(u);
    @PKG@.Kit.owedLater(pr);   // 0.1.6: owed kit items of this profile (the load above just filled KITQ at a join)''',
    '''    @PKG@.ClassStore.load(u);
    @PKG@.AbilStore.load(@PKG@.ClassCfg.pkey(u));   // 0.1.16: the ability loadout of the active profile, read off the world thread
    @PKG@.Kit.owedLater(pr);   // 0.1.6: owed kit items of this profile (the load above just filled KITQ at a join)''')
rep('''    @PKG@.HealBudget.forget(u);
    @PKG@.HealMsg.forget(u);
  } catch (Throwable t) { }''', '''    @PKG@.HealBudget.forget(u);
    @PKG@.HealMsg.forget(u);
    @PKG@.AbilStore.TOLD.remove(u);   // 0.1.16 (cooldowns stay: keyed by profile, a relog must not reset them)
  } catch (Throwable t) { }''')
rep('''  super("classadmin", "(admin) /classadmin set <player> <class> | reset <player> | info <player> | kit <player> [class] | reload");''',
    '''  super("classadmin", "(admin) /classadmin set <player> <class> | reset <player> | info <player> | kit <player> [class] | abil <player> <action> | reload");''')
rep('''  addSubCommand(new @PKG@.AdminKitCmd());
  addSubCommand(new @PKG@.AdminReloadCmd());''', '''  addSubCommand(new @PKG@.AdminKitCmd());
  addSubCommand(new @PKG@.AdminAbilCmd());   // 0.1.16
  addSubCommand(new @PKG@.AdminReloadCmd());''')
rep('''  pr.sendMessage(@MSG@.raw("[Classes] /classadmin set <player|uuid> <class> | reset <player|uuid> | info <player|uuid> | kit <player|uuid> [class] | reload"));''',
    '''  pr.sendMessage(@MSG@.raw("[Classes] /classadmin set <player|uuid> <class> | reset <player|uuid> | info <player|uuid> | kit <player|uuid> [class] | abil <player|uuid> <grant|ungrant|reset|info> | reload"));''')
rep('''  @PKG@.ClassStore.DIR = base.resolve("players");
''', '''  @PKG@.ClassStore.DIR = base.resolve("players");
  @PKG@.AbilStore.DIR = base.resolve("abilities");   // 0.1.16: the ability loadout per profile
''')
rep('''  b.put("class:fn:ally", new @PKG@.AllyFn());       // 0.1.12: traversal lock-ons / friendly fire = party only
''', '''  b.put("class:fn:ally", new @PKG@.AllyFn());       // 0.1.12: traversal lock-ons / friendly fire = party only
  b.put("class:fn:abil", new @PKG@.AbilFn());       // 0.1.16: the 4 ability slots + cooldowns (SkyyHud's Abilities widget, R2)
  b.put("class:fn:abilhit", new @PKG@.AbilHitFn()); // 0.1.16: Damage -> the casting player (SkyySkills 0.4.28 kill XP of ability damage)
''')
rep('''  getCommandRegistry().registerCommand(new @PKG@.ClassAdminCmd());
''', '''  getCommandRegistry().registerCommand(new @PKG@.ClassAdminCmd());
  getCommandRegistry().registerCommand(new @PKG@.CastCmd());   // 0.1.16: /cast (never /abilities - vanilla 0.7 owns it)
''')
rep('''protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''', '''protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.AbilStore.flush(); } catch (Throwable t) { }   // 0.1.16 FIX ROUND: ability files changed but not yet written to disk
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''')
rep('''  getEntityStoreRegistry().registerSystem(new @PKG@.DeployGuard());     // 0.1.7: Priest-only Healing Totem, judged when it lands
''', '''  getEntityStoreRegistry().registerSystem(new @PKG@.DeployGuard());     // 0.1.7: Priest-only Healing Totem, judged when it lands
  getEntityStoreRegistry().registerSystem(new @PKG@.AbilTick());        // 0.1.16: the delayed ability jobs (Meteor impact, heal over time)
''')
rep('''  @PKG@.ClassCfg.regSetting("classes.healTaken", "Priest heals - healed by others", "combat", true, "Skyy healed you +12 HP - one line every 10 s at most. The heal happens either way");
''', '''  @PKG@.ClassCfg.regSetting("classes.healTaken", "Priest heals - healed by others", "combat", true, "Skyy healed you +12 HP - one line every 10 s at most. The heal happens either way");
  @PKG@.ClassCfg.regSetting("classes.abilChat", "Ability chat lines", "combat", true, "Meteor! -23 Mana, -2 Stamina and what it hit. Refusals (cooldown, not enough Mana) always show");
''')
rep('''log("[SkyyClasses] __VER__ ready (__KIT__) - /class, /class kit, /class arrows, /classadmin; classes''',
    '''log("[SkyyClasses] __VER__ ready (__KIT__) - /class, /class kit, /class arrows, /cast, /classadmin; classes''')
rep('''for c in (cfg, kcfg, hooks, defs, st_, rul, afn, gfn, ksoon, knew, srec, strk, lock, dgd, hbud, hmsg, kit_, ktask, arw, htask, hfn, alfn, phs, khooks,
          kht, kmig, page, opn, rtk, rdy, quit_, ctick, kcmd, acmd, cmd, aset, ares, ainf, akit2, akit, arel, adm, pl):''',
    '''for c in (cfg, kcfg, hooks, defs, st_, rul, afn, gfn, ksoon, knew, srec, strk, lock, dgd, hbud, hmsg, kit_, ktask, arw, htask, hfn, alfn, phs, khooks,
          kht, kmig, page, opn, rtk, rdy, quit_, ctick, kcmd, acmd, cmd, aset, ares, ainf, akit2, akit, arel, adm, pl,
          abcfg, abdmg, abhit, abdefs, abmath, abst, absave, abjob, abworld, abil, abfn, abtick, castc, casta, aabil):   # 0.1.16: + 15 ability classes''')
rep('''Priests heal their party and own the Healing Totem; the wand heal orb and traversal lock-ons go through class:fn:heal / class:fn:ally. /class to choose''',
    '''Priests heal their party and own the Healing Totem; the wand heal orb and traversal lock-ons go through class:fn:heal / class:fn:ally; class abilities with /cast (Mage Meteor, Priest Sacred Heal; crouch = your alts). /class to choose''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0 + 1 and s.count("registerSystem(") == SYS0 + 1
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.1.15 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.1.15 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
