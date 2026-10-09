"""Derive SkyyClasses/build_skyyclasses_0.1.17.py from the CURRENT generated 0.1.16 (build_skyyclasses_0.1.16.py = the tools/deploy_set.py
SET pin). Run:  python tools/classes_0_1_17_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.17.py   then
                python SkyyClasses/test_skyyclasses_0.1.17.py --dir <tools/dev/scratch/...>   (never --deploy: coordinated deploy)
EDITED-SCRIPTS RULE (commit ab75b6c): the lineage is Skyy's EDITED 0.1.6 -> classes_0_1_7_patch.py -> ... -> classes_0_1_16_patch.py -> the
generated 0.1.16 read here; tools/classes_0_1_6_patch.py is NEVER re-run. Edit THIS file, never the generated build script.

0.1.17 = THE CLASS ABILITY ENGINE, ROUND R3 (research/cloud/Ability-Engine-Plan.md section 8 R3) + the bridge data the SkyyHud 0.3.18
Abilities widget (round R2) needs. Skyy's locks (docs/answered/classes.md): "we decided 4 ability's, 2 active at a time. the 2 you pick are
your primary ability's, and work when walking or sprinting. thew other 2 are set to crouch. so crouching uses your alt ability's." + lines
112-114 (Mana Barrier 12 s, damage drains Mana instead of Health 1 Mana per 2 HP, a placed dome, visible but see-through) + 145 / 147
(Shield Bubble 6 blocks / 12 s, HP = the caster's max Health, heal pulses at 75 / 50 / 25 / 0 %) + 173 (Mana AND Stamina by the class
split, every ability affordable when unlocked). Numbers: research/cloud/Class-Ability-Spec-Draft.md section 2 (2.3 Mana Barrier 16 Mana + 1
Stamina / 30 s; 2.4 Shield Bubble 20 Mana + 2 Stamina / 24 s, pulse 8 % max Health). R1 (0.1.16) behaviour is unchanged.
WHAT IS NEW
  - ManaBarrier + ShieldBubble are BUILT (walking shape = every shape until R5). Owned at class level 10 (abil.unlock.a2) as before.
  - The ZONE kind: AbilZone (one placed zone: kind 1 = Mana Barrier, 2 = Shield Bubble), kept in the world's AbilWorld next to the
    delayed jobs (zones + jobs count toward abil.maxLive); at most abil.maxZones (2) per player (a newer one ends the oldest). The
    spot = where you look within ab.<Ability>.range (8) blocks (TargetUtil, as Meteor), else at your feet; range 0 = always at your feet.
  - AbilShieldSys = a DamageEventSystem in the FILTER group, players only, ordered AFTER the engine's DamageSystems$ArmorDamageReduction
    (SystemDependency - SkyySkills' DefSys / SkyyGear's GearArmorSys place) + the unordered fallback AbilShieldSysU (registered only
    when the ordered one cannot be: one registerSystem per class). Abil.shield does the work:
      1. SHIELD BUBBLE: an ATTACK (Damage$EntitySource, projectiles included) on the Priest or a party member (HealTask.inParty) inside a
         bubble is taken from the bubble's HP first (overlapping bubbles: the one with the most HP). HP = ab.ShieldBubble.hp (100) % of
         the caster's max Health at the cast. Crossing 75 / 50 / 25 / 0 % queues a heal pulse (4 in all); 0 = broken. Arrows are blocked
         by soaking their damage (the projectile is not removed - plan question 9, probe P10 UNVERIFIED, nothing deleted).
      2. MANA BARRIER: what is left of any damage to the Mage INSIDE her own dome (not out-of-world / command damage) is paid with Mana:
         ab.ManaBarrier.ratio (2) HP per Mana, at most ab.ManaBarrier.maxAbsorb (100) % of her max Health per dome; at 0 Mana or the cap
         the dome ends. Fully soaked = the Damage is cancelled; partly = its amount lowered. The Mana is subtracted from the victim's own
         stat map in the handle (the world thread; the same component ApplyDamage writes).
  - AbilWorld.run (AbilTick, the world thread) ticks the zones every abil.tick (0.25 s): the heal pulses (ab.ShieldBubble.pulse 8 % max
    Health; the Priest + party full, other players inside the othersPercent share; the abil.healCap per target per bubble; Divinity XP
    like Sacred Heal), the absorb XP (0.5 per HP soaked: others at the heal rate, the Priest's own at the self rate), the see-through
    ring (vanilla Rings_Rings / Rings_Rings_Ice one-shots at 6-16 points every 1 s), the end (time, 0 Mana, the cap, broken, the caster
    gone / dead / another profile for the barrier; the bubble finishes on its own clock - no XP after a profile switch) with one line to
    the caster and a vanilla burst (Shield_Shatter when it breaks, Item_Break_GlassMagic otherwise).
  - HUD BRIDGE (round R2): class:fn:abil apply(UUID) -> Object[44]. [0-15] unchanged (4 x {name, Long msLeft, Long msTotal, state});
    [16-19] ability id per slot ("" = none), [20-23] Double Mana cost, [24-27] Double Stamina cost, [28-31] Boolean affordable now (null
    = not known: no fresh sample / not ready or cooling down), [32] Boolean crouching, [33] the class name, [34] Double Mana now, [35]
    Double Stamina now, [36] Boolean free (creative + abil.creativeFree), [37] "abil2" (this layout), [38-41] Long unlock level per slot,
    [42] Long sample age ms, [43] null (spare). The world-thread values (Mana, Stamina, crouch, creative) come from a SAMPLE AbilTick takes
    on the world thread at most every 0.2 s, only for players whose HUD asked within 5 s (AbilStore.WANT; zero cost without the widget).
  - Server Setup -> Classes: Abilities + abil.tick (0.25 s), abil.maxZones (2); Ability numbers + ab.ManaBarrier.walk.mana / .stamina /
    .cooldown (16 / 1 / 30 s), .time 12 s, .radius 4, .range 8, .ratio 2, .maxAbsorb 100 %; ab.ShieldBubble.walk.mana / .stamina /
    .cooldown (20 / 2 / 24 s), .time 12 s, .radius 6, .range 8, .hp 100 %, .pulse 8 %. No migration (a missing key reads its default).
    Names follow R1's ab.<Ability>.* rows (the plan's sketch called them barrier.ratio / barrier.radius / bubble.pulse).
FIX ROUND (critics of 2026-10-09):
  - Mana Barrier spot: the dome must cover the Mage - a look point farther than ab.ManaBarrier.radius - 0.5 from her feet puts it at her
    feet (spec: "at the caster's feet"; the plan's look point only when she is inside it). The bubble keeps the plain look-point rule.
  - Mana Barrier needs ab.ManaBarrier.keep (4) Mana LEFT after its cost (a cast at exactly 16 Mana made a dome that ended at once); the
    HUD bridge's "affordable" counts it too. New row, no migration.
  - AbilShieldSys is also ordered AFTER the engine filters that DROP a hit (DamageSystems$FilterUnkillable - Invulnerable / Intangible /
    invulnerable effects -, $FilterPlayerWorldConfig - player damage off -, $PlayerDamageFilterSystem - spawn protection, PvP off), each
    only when its class resolves; Abil.shield also skips a victim with the Invulnerable component (the unordered fallback's guard). A hit
    those filters cancel no longer costs Mana or bubble HP.
  - Shield Bubble absorb XP is not paid for hits by PLAYERS (a party alt hitting an ally with PvP on farmed Divinity XP); the bubble
    still soaks them.
  - The rims draw a dome: the edge ring + an upper ring (0.7 r high, 0.7 r wide) + a top point (still small vanilla ring bursts).
  - barrierCast / bubbleCast send their line BEFORE the zone goes live (addZone last, as its comment says).
NOT IN R3: the Ward / Follow / Echo modifiers, the other shapes (R5), deleting hostile projectiles (P10), the HUD swap of rows (SkyyHud).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.16.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.17.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.16"' in s and "GENERATED by tools/classes_0_1_16_patch.py from the generated 0.1.15" in s, \
    "build_skyyclasses_0.1.16.py is not the generated 0.1.16"
assert "AbilZone" not in s and "AbilShieldSys" not in s
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
rep('''"""SkyyClasses 0.1.16 - build script (javassist via jpype). GENERATED by tools/classes_0_1_16_patch.py from the generated 0.1.15 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_15_patch.py -> 0.1.15) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.17 - build script (javassist via jpype). GENERATED by tools/classes_0_1_17_patch.py from the generated 0.1.16 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_16_patch.py -> 0.1.16) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
0.1.17 (2026-10-09; research/cloud/Ability-Engine-Plan.md round R3 + the R2 HUD bridge data):
  ZONES - Mage MANA BARRIER (a see-through dome where you look: damage to the Mage inside costs Mana instead of Health, 1 Mana per 2 HP,
  ends at 0 Mana / 100% max Health soaked / 12 s) and Priest SHIELD BUBBLE (6 blocks, 12 s, HP = your max Health, soaks attacks on you
  and your party inside, 4 heal pulses at 75 / 50 / 25 / 0 %); AbilShieldSys (Filter group, AFTER ArmorDamageReduction); zone tick in
  AbilTick; class:fn:abil -> Object[44] (+ ids, costs, affordable, crouch from a world-thread sample) for SkyyHud 0.3.18's Abilities
  widget; Server Setup rows abil.tick, abil.maxZones, ab.ManaBarrier.*, ab.ShieldBubble.* (no migration). Notes in
  tools/classes_0_1_17_patch.py.
''')
rep('''Run:   python build_skyyclasses_0.1.16.py           -> SkyyClasses/SkyyClasses-0.1.16.jar''',
    '''Run:   python build_skyyclasses_0.1.17.py           -> SkyyClasses/SkyyClasses-0.1.17.jar''')
rep('VERSION = "0.1.16"\n', 'VERSION = "0.1.17"\n')

# ================================================================================================ the registry + rows (Python tables)
rep('''    ("ManaBarrier", "Mana Barrier", "Mage", 1, False, False),''', '''    ("ManaBarrier", "Mana Barrier", "Mage", 1, True, False),          # 0.1.17: built (R3)''')
rep('''    ("ShieldBubble", "Shield Bubble", "Priest", 1, False, False),''', '''    ("ShieldBubble", "Shield Bubble", "Priest", 1, True, False),      # 0.1.17: built (R3)''')
rep('''    ("ab.SacredHeal.hotTime", "S_HOT_TIME", "dec", 4.0, "0", "30", "s", "abilx", "live", "Heal over time length",
     "Seconds the heal over time lasts (one pulse a second). 0 = no heal over time."),
]''', '''    ("ab.SacredHeal.hotTime", "S_HOT_TIME", "dec", 4.0, "0", "30", "s", "abilx", "live", "Heal over time length",
     "Seconds the heal over time lasts (one pulse a second). 0 = no heal over time."),
    # 0.1.17 (round R3): zones - research/cloud/Ability-Engine-Plan.md section 9 R3 (abil.tick waited for this round), spec draft 2.3 / 2.4
    ("abil.tick", "TICK", "dec", 0.25, "0.1", "1", "s", "abil", "live,adv", "Zone update interval",
     "How often placed zones (Mana Barrier, Shield Bubble) update, in seconds."),
    ("abil.maxZones", "MAX_ZONES", "int", 2, "1", "4", "", "abil", "live", "Most placed zones per player",
     "A new zone past this number ends that player's oldest zone."),
    ("ab.ManaBarrier.walk.mana", "B_MANA", "dec", 16.0, "0", "1000", "", "abilx", "live", "Mana Barrier Mana", "Mana per Mana Barrier."),
    ("ab.ManaBarrier.walk.stamina", "B_STAM", "dec", 1.0, "0", "100", "", "abilx", "live", "Mana Barrier Stamina", "Stamina per Mana Barrier."),
    ("ab.ManaBarrier.walk.cooldown", "B_CD", "dec", 30.0, "0", "600", "s", "abilx", "live", "Mana Barrier cooldown",
     "Seconds before Mana Barrier can be cast again."),
    ("ab.ManaBarrier.time", "B_TIME", "dec", 12.0, "1", "60", "s", "abilx", "live", "Mana Barrier length",
     "Seconds the dome lasts (it ends sooner at 0 Mana)."),
    ("ab.ManaBarrier.radius", "B_RADIUS", "dec", 4.0, "2", "12", "blocks", "abilx", "live", "Mana Barrier size",
     "Dome radius. Damage to the Mage inside drains Mana instead of Health."),
    ("ab.ManaBarrier.range", "B_RANGE", "dec", 8.0, "0", "32", "blocks", "abilx", "live", "Mana Barrier reach",
     "Where you look, at most this far, if the dome still covers you; else your feet. 0 = your feet."),
    ("ab.ManaBarrier.ratio", "B_RATIO", "dec", 2.0, "0.5", "10", "x", "abilx", "live", "Damage soaked per Mana",
     "2 = every 2 damage costs 1 Mana instead of Health."),
    ("ab.ManaBarrier.keep", "B_KEEP", "dec", 4.0, "0", "100", "", "abilx", "live", "Mana Barrier Mana kept",
     "Mana you must have LEFT after the cost to cast it (the dome soaks with it). 0 = any."),   # FIX ROUND
    ("ab.ManaBarrier.maxAbsorb", "B_MAX", "int", 100, "10", "500", "%", "abilx", "live", "Most damage soaked (% max Health)",
     "One dome soaks at most this % of your max Health, then it ends."),
    ("ab.ShieldBubble.walk.mana", "U_MANA", "dec", 20.0, "0", "1000", "", "abilx", "live", "Shield Bubble Mana", "Mana per Shield Bubble."),
    ("ab.ShieldBubble.walk.stamina", "U_STAM", "dec", 2.0, "0", "100", "", "abilx", "live", "Shield Bubble Stamina", "Stamina per Shield Bubble."),
    ("ab.ShieldBubble.walk.cooldown", "U_CD", "dec", 24.0, "0", "600", "s", "abilx", "live", "Shield Bubble cooldown",
     "Seconds before Shield Bubble can be cast again."),
    ("ab.ShieldBubble.time", "U_TIME", "dec", 12.0, "1", "60", "s", "abilx", "live", "Shield Bubble length",
     "Seconds the bubble lasts (it ends sooner when it breaks)."),
    ("ab.ShieldBubble.radius", "U_RADIUS", "dec", 6.0, "2", "16", "blocks", "abilx", "live", "Shield Bubble size",
     "Bubble radius. Attacks on you and your party inside hit the bubble first."),
    ("ab.ShieldBubble.range", "U_RANGE", "dec", 8.0, "0", "32", "blocks", "abilx", "live", "Shield Bubble reach",
     "Placed where you look, at most this far; else at your feet. 0 = always at your feet."),
    ("ab.ShieldBubble.hp", "U_HP", "int", 100, "10", "500", "%", "abilx", "live", "Bubble strength (% of your max Health)",
     "How much damage the bubble soaks before it breaks."),
    ("ab.ShieldBubble.pulse", "U_PULSE", "int", 8, "0", "50", "%", "abilx", "live", "Heal pulse (% of max Health)",
     "Heals everyone inside at 75 / 50 / 25 % bubble strength and when it breaks."),
]''')
rep('''assert (round(30 * 0.78), max(1, int(30 * 0.22 / 4 + 0.5))) == (23, 2) and (round(25 * 0.73), max(1, int(25 * 0.27 / 4 + 0.5))) == (18, 2)
''', '''assert (round(30 * 0.78), max(1, int(30 * 0.22 / 4 + 0.5))) == (23, 2) and (round(25 * 0.73), max(1, int(25 * 0.27 / 4 + 0.5))) == (18, 2)
# 0.1.17: spec draft 2.3 / 2.4 after the power split (power 20 Mana Barrier, 28 Shield Bubble - the old Mana-only numbers)
assert [_r[3] for _r in ABIL_ROWS if _r[0].startswith("ab.ManaBarrier.walk.")] == [16.0, 1.0, 30.0], "Mana Barrier 16 Mana + 1 Stamina / 30 s (spec 2.3)"
assert [_r[3] for _r in ABIL_ROWS if _r[0].startswith("ab.ShieldBubble.walk.")] == [20.0, 2.0, 24.0], "Shield Bubble 20 Mana + 2 Stamina / 24 s (spec 2.4)"
assert (int(20 * 0.78 + 0.5), max(1, int(20 * 0.22 / 4 + 0.5))) == (16, 1) and (int(28 * 0.73 + 0.5), max(1, int(28 * 0.27 / 4 + 0.5))) == (20, 2)
# affordable when unlocked (Skyy line 173; plan 4.4 pools at class level 10 = abil.unlock.a2: Mage 145 Mana / 14.5 Stamina, Priest 92 / 15.6)
assert [_r[3] for _r in ABIL_ROWS if _r[0] == "ab.ManaBarrier.keep"] == [4.0] and 16.0 + 4.0 <= 145   # FIX ROUND: + the Mana kept
assert 16.0 <= 145 and 1.0 <= 14.5 and 20.0 <= 92 and 2.0 <= 15.6 and [_r[3] for _r in ABIL_ROWS if _r[0] == "abil.unlock.a2"] == [10]
''')

# ================================================================================================ engine tokens + probes
rep('''    "SCAT": "com.hypixel.hytale.protocol.SoundCategory",
}''', '''    "SCAT": "com.hypixel.hytale.protocol.SoundCategory",
    # 0.1.17: the zone damage system's order (the SkyySkills DefSys shape)
    "SDEP": "com.hypixel.hytale.component.dependency.SystemDependency",
    "ORD":  "com.hypixel.hytale.component.dependency.Order",
}''')
rep('''pool.get(T["DMG"]).getConstructor("(Lcom/hypixel/hytale/server/core/modules/entity/damage/Damage$Source;Lcom/hypixel/hytale/server/core/modules/entity/damage/DamageCause;F)V")
''', '''pool.get(T["DMG"]).getConstructor("(Lcom/hypixel/hytale/server/core/modules/entity/damage/Damage$Source;Lcom/hypixel/hytale/server/core/modules/entity/damage/DamageCause;F)V")
# 0.1.17 (zones): every new engine member with the descriptor the code calls
for c, m in ((T["DMG"], "getCause"), (T["DMG"], "setCancelled"), (T["DMG"], "setAmount"), (T["DMG"], "getAmount"), (T["DMG"], "isCancelled"),
             (T["DCS"], "OUT_OF_WORLD"), (T["DCS"], "COMMAND"), (T["ORD"], "AFTER"), (T["ESM"], "subtractStatValue"), (T["DMOD"], "getFilterDamageGroup"),
             (T["ACH"], "getReferenceTo")):
    B.probe(pool, c, m)
for c, m, d in ((T["DMG"], "getCause", "()Lcom/hypixel/hytale/server/core/modules/entity/damage/DamageCause;"), (T["DMG"], "setAmount", "(F)V"),
                (T["DMG"], "getAmount", "()F"), (T["ESM"], "subtractStatValue", "(IF)F")):
    assert str(pool.get(c).getMethod(m, d).getName()) == m, "%s.%s%s" % (c, m, d)
pool.get(T["SDEP"]).getConstructor("(Lcom/hypixel/hytale/component/dependency/Order;Ljava/lang/Class;)V")
pool.get("com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction")
for _c in ("FilterUnkillable", "FilterPlayerWorldConfig", "PlayerDamageFilterSystem"):   # FIX ROUND: the filters AbilShieldSys also runs after
    assert str(pool.get("com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$" + _c).getMethod("getGroup", "()Lcom/hypixel/hytale/component/SystemGroup;").getName()) == "getGroup"
assert pool.get(T["DPRJ"]).subtypeOf(pool.get(T["DENT"])), "a projectile source is an entity source (the bubble soaks arrows as attacks)"
''')

# ================================================================================================ AbilCfg.text
rep('''    + ", Sacred Heal " + @PKG@.ClassCfg.fmtNum(S_MANA) + "+" + @PKG@.ClassCfg.fmtNum(S_STAM) + "/" + @PKG@.ClassCfg.fmtNum(S_CD) + "s)";''',
    '''    + ", Sacred Heal " + @PKG@.ClassCfg.fmtNum(S_MANA) + "+" + @PKG@.ClassCfg.fmtNum(S_STAM) + "/" + @PKG@.ClassCfg.fmtNum(S_CD) + "s"
    + ", Mana Barrier " + @PKG@.ClassCfg.fmtNum(B_MANA) + "+" + @PKG@.ClassCfg.fmtNum(B_STAM) + "/" + @PKG@.ClassCfg.fmtNum(B_CD) + "s"
    + ", Shield Bubble " + @PKG@.ClassCfg.fmtNum(U_MANA) + "+" + @PKG@.ClassCfg.fmtNum(U_STAM) + "/" + @PKG@.ClassCfg.fmtNum(U_CD) + "s)";''')

# ================================================================================================ particles (vanilla one-shots, proven finite by the build)
rep('''FX = {"FX_MARK": "Fire_AoE_Spawn", "FX_HIT": "Explosion_Medium", "FX_HEAL": "Magic_Hit"}''',
    '''FX = {"FX_MARK": "Fire_AoE_Spawn", "FX_HIT": "Explosion_Medium", "FX_HEAL": "Magic_Hit",
      # 0.1.17 zones: the see-through rims (Skyy line 114: visible, never blocking or flashing - small ring bursts on the edge), the bubble's
      # placing flash, its break and the quiet end
      "FX_BARRIER": "Rings_Rings", "FX_BUBBLE": "Rings_Rings_Ice", "FX_BUBBLE_ON": "Shield_Block", "FX_BREAK": "Shield_Shatter",
      "FX_END": "Item_Break_GlassMagic"}''')

# ================================================================================================ AbilDefs (indices + costs)
rep('''F(abdefs, "public static final int SACRED = %d;" % [a[0] for a in ABILS].index("SacredHeal"))
''', '''F(abdefs, "public static final int SACRED = %d;" % [a[0] for a in ABILS].index("SacredHeal"))
F(abdefs, "public static final int MANAB = %d;" % [a[0] for a in ABILS].index("ManaBarrier"))     # 0.1.17
F(abdefs, "public static final int BUBBLE = %d;" % [a[0] for a in ABILS].index("ShieldBubble"))   # 0.1.17
''')
rep('''public static double mana(int ai) {
  if (ai == METEOR) return @PKG@.AbilCfg.M_MANA;
  if (ai == SACRED) return @PKG@.AbilCfg.S_MANA;''', '''public static double mana(int ai) {
  if (ai == METEOR) return @PKG@.AbilCfg.M_MANA;
  if (ai == SACRED) return @PKG@.AbilCfg.S_MANA;
  if (ai == MANAB) return @PKG@.AbilCfg.B_MANA;
  if (ai == BUBBLE) return @PKG@.AbilCfg.U_MANA;''')
rep('''public static double stamina(int ai) {
  if (ai == METEOR) return @PKG@.AbilCfg.M_STAM;
  if (ai == SACRED) return @PKG@.AbilCfg.S_STAM;''', '''public static double stamina(int ai) {
  if (ai == METEOR) return @PKG@.AbilCfg.M_STAM;
  if (ai == SACRED) return @PKG@.AbilCfg.S_STAM;
  if (ai == MANAB) return @PKG@.AbilCfg.B_STAM;
  if (ai == BUBBLE) return @PKG@.AbilCfg.U_STAM;''')
rep('''  if (ai == SACRED) s = @PKG@.AbilCfg.S_CD;
''', '''  if (ai == SACRED) s = @PKG@.AbilCfg.S_CD;
  if (ai == MANAB) s = @PKG@.AbilCfg.B_CD;
  if (ai == BUBBLE) s = @PKG@.AbilCfg.U_CD;
''')

# ================================================================================================ AbilMath: the zone rules (pure)
rep('''# ---- AbilStore: loadout per profile (abilities/<pkey>.properties), memory cooldowns (pkey|ability), refusal throttle
''', '''# 0.1.17 zones (pure, bare-JVM tested). Mana Barrier: the HP soaked from amt = what the Mana pays for (mana x ratio) and what the dome may
# still soak (capLeft), never below 0
M(abmath, r"""
public static double barrierTake(double amt, double mana, double ratio, double capLeft) {
  if (!(amt > 0.0) || !(ratio > 0.0) || !(mana > 0.0) || !(capLeft > 0.0)) return 0.0;
  double t = amt;
  double byMana = mana * ratio;
  if (byMana < t) t = byMana;
  if (capLeft < t) t = capLeft;
  return t > 0.0 ? t : 0.0;
}""")
M(abmath, r"""
public static double bubbleTake(double amt, double hp) {
  if (!(amt > 0.0) || !(hp > 0.0)) return 0.0;
  return amt < hp ? amt : hp;
}""")
# the heal pulses a bubble has earned at hp of hpMax: one each at 75 / 50 / 25 % and the last at 0 (broken) - Skyy line 147
M(abmath, r"""
public static int pulsesDue(double hpMax, double hp) {
  if (!(hpMax > 0.0)) return 0;
  int n = 0;
  if (hp <= hpMax * 0.75 + 1.0E-6) n++;
  if (hp <= hpMax * 0.50 + 1.0E-6) n++;
  if (hp <= hpMax * 0.25 + 1.0E-6) n++;
  if (hp <= 1.0E-6) n++;
  return n;
}""")
# the rim points of a ring of radius r: one about every 2 blocks of its edge, 6 - 16
M(abmath, r"""
public static int ringPoints(double r) {
  if (!(r > 0.0)) return 6;
  long n = Math.round(6.283185307179586 * r / 2.0);
  if (n < 6L) n = 6L;
  if (n > 16L) n = 16L;
  return (int) n;
}""")

# ---- AbilStore: loadout per profile (abilities/<pkey>.properties), memory cooldowns (pkey|ability), refusal throttle
''')
rep('''for _f in ("DATA", "FAILAT", "CD", "CDLEN", "TOLD", "DIRTY"):   # FIX ROUND: + DIRTY (keys changed in memory, not yet on disk)''',
    '''for _f in ("DATA", "FAILAT", "CD", "CDLEN", "TOLD", "DIRTY",   # FIX ROUND: + DIRTY (keys changed in memory, not yet on disk)
           "WANT", "SAMPLE"):   # 0.1.17: UUID -> Long the HUD last asked (class:fn:abil); UUID -> double[] {Mana, Stamina, crouch, creative, at}''')

# ================================================================================================ AbilZone + AbilWorld zones
rep('''# ---- AbilWorld: the job list of one world (world name -> list), run by AbilTick once per world tick
abworld = pool.makeClass(PKG + ".AbilWorld")''', '''# ---- 0.1.17 AbilZone: one placed zone (kind 1 = Mana Barrier, 2 = Shield Bubble); its fields are touched on its world's thread only
abzone = pool.makeClass(PKG + ".AbilZone")
for _f in ("public int kind;", "public java.util.UUID caster;", "public String pkey;", "public String name;", "public double x;", "public double y;",
           "public double z;", "public double r;", "public long start;", "public long until;", "public long nextFx;", "public double hp;",
           "public double hpMax;", "public double absorbed;", "public double cap;", "public double ratio;", "public double manaPaid;",
           "public int pulsesDue;", "public int pulsesDone;", "public boolean ended;", "public String why;", "public double xpOthers;",
           "public double xpSelf;", "public java.util.HashMap healed;"):
    F(abzone, _f)
C(abzone, r"""
public AbilZone(int kind, java.util.UUID caster, double x, double y, double z, double r, long start, long until) {
  this.kind = kind;
  this.caster = caster;
  this.x = x;
  this.y = y;
  this.z = z;
  this.r = r;
  this.start = start;
  this.until = until;
  this.nextFx = start + 1000L;
  this.why = "";
  this.healed = new java.util.HashMap();
}""")

# ---- AbilWorld: the job list of one world (world name -> list), run by AbilTick once per world tick
abworld = pool.makeClass(PKG + ".AbilWorld")''')
rep('''C(abworld, "public AbilWorld(String name) { this.name = name; this.jobs = new java.util.ArrayList(); this.lastNs = 0L; }")''',
    '''F(abworld, "public java.util.ArrayList zones;")      # 0.1.17: the placed zones of this world
F(abworld, "public volatile int nz;")                 # 0.1.17: zones.size(), read without the lock (the damage hook's fast exit)
F(abworld, "public long nextZone;")                   # 0.1.17: the next zone tick (abil.tick)
C(abworld, "public AbilWorld(String name) { this.name = name; this.jobs = new java.util.ArrayList(); this.lastNs = 0L; this.zones = new java.util.ArrayList(); this.nz = 0; this.nextZone = 0L; }")''')
rep('''    if (j.at + STALE < now) { it.remove(); n++; }
  }
  return n;
}""")''', '''    if (j.at + STALE < now) { it.remove(); n++; }
  }
  java.util.Iterator iz = this.zones.iterator();   // 0.1.17: a zone of a world nobody ticks any more leaves STALE ms after its end
  while (iz.hasNext()) {
    @PKG@.AbilZone z = (@PKG@.AbilZone) iz.next();
    if (z.until + STALE < now) { iz.remove(); n++; }
  }
  this.nz = this.zones.size();
  return n;
}""")''')
rep('''M(abworld, "public synchronized boolean full() { prune(System.currentTimeMillis()); return (long) this.jobs.size() >= @PKG@.AbilCfg.MAX_LIVE; }")   # FIX ROUND: row abil.maxLive
M(abworld, "public synchronized boolean idle() { return this.jobs.isEmpty(); }")''',
    '''M(abworld, "public synchronized boolean full() { prune(System.currentTimeMillis()); return (long) (this.jobs.size() + this.zones.size()) >= @PKG@.AbilCfg.MAX_LIVE; }")   # FIX ROUND: row abil.maxLive; 0.1.17: + zones
M(abworld, "public synchronized boolean idle() { return this.jobs.isEmpty() && this.zones.isEmpty(); }")   # 0.1.17: + zones''')
rep('''M(abworld, "public synchronized void add(@PKG@.AbilJob j) { if (j != null) this.jobs.add(j); }")
''', '''M(abworld, "public synchronized void add(@PKG@.AbilJob j) { if (j != null) this.jobs.add(j); }")
# 0.1.17 zones: add (a player past abil.maxZones live zones ends the OLDEST of theirs first - it ends at its next tick), the copy the tick and
# the damage hook walk, drop
M(abworld, r"""
public synchronized int addZone(@PKG@.AbilZone z) {
  if (z == null) return 0;
  int ended = 0;
  while (true) {
    int mine = 0;
    @PKG@.AbilZone oldest = null;
    for (int i = 0; i < this.zones.size(); i++) {
      @PKG@.AbilZone o = (@PKG@.AbilZone) this.zones.get(i);
      if (o.ended || o.caster == null || !o.caster.equals(z.caster)) continue;
      mine++;
      if (oldest == null || o.start < oldest.start) oldest = o;
    }
    if ((long) mine < @PKG@.AbilCfg.MAX_ZONES || oldest == null) break;
    oldest.ended = true;
    oldest.why = "replaced";
    ended++;
  }
  this.zones.add(z);
  this.nz = this.zones.size();
  return ended;
}""")
M(abworld, r"""
public synchronized @PKG@.AbilZone[] zoneArr() {
  @PKG@.AbilZone[] a = new @PKG@.AbilZone[this.zones.size()];
  for (int i = 0; i < a.length; i++) a[i] = (@PKG@.AbilZone) this.zones.get(i);
  return a;
}""")
M(abworld, "public synchronized void dropZone(@PKG@.AbilZone z) { this.zones.remove(z); this.nz = this.zones.size(); }")
M(abworld, "public synchronized int zoneCount() { return this.zones.size(); }")
''')

# ================================================================================================ Abil: zones, the damage hook, the HUD sample (before castNow)
ZONE_SRC = r'''# ---- 0.1.17 ZONES (round R3): the spot, the two executors, the shield hook, the zone tick, the HUD sample
# the spot a zone goes: where the player looks within range blocks (Meteor's aim), else at the feet; range 0 = always at the feet
M(abil, r"""
public static double[] spot(@CAC@ acc, @REF@ r, double range) {
  double[] a = null;
  if (range > 0.0) a = aim(acc, r, range);
  if (a != null) return a;
  @VEC@ p = pos(acc, r);
  if (p == null) return null;
  return new double[] { p.x, p.y, p.z };
}""")
# the see-through rim: small vanilla one-shot ring bursts at ringPoints(r) points of the edge, 0.2 above the anchor; FIX ROUND (critic: a
# flat circle, not Skyy's dome): + an upper ring 0.7 r high and 0.7 r wide + one point on top, so the bursts outline a dome
M(abil, r"""
public static void ring(String id, @PKG@.AbilZone z, @CAC@ acc) {
  int n = @PKG@.AbilMath.ringPoints(z.r);
  for (int i = 0; i < n; i++) {
    double a = 6.283185307179586 * (double) i / (double) n;
    particle(id, z.x + Math.cos(a) * z.r, z.y + 0.2, z.z + Math.sin(a) * z.r, acc);
  }
  double r2 = z.r * 0.7;
  int n2 = @PKG@.AbilMath.ringPoints(r2);
  for (int i = 0; i < n2; i++) {
    double a = 6.283185307179586 * ((double) i + 0.5) / (double) n2;
    particle(id, z.x + Math.cos(a) * r2, z.y + r2, z.z + Math.sin(a) * r2, acc);
  }
  particle(id, z.x, z.y + z.r, z.z, acc);
}""")
M(abil, r"""
public static String spotText(@PKG@.AbilZone z) {
  return " at=" + @PKG@.AbilMath.fmt(z.x) + "," + @PKG@.AbilMath.fmt(z.y) + "," + @PKG@.AbilMath.fmt(z.z) + " r=" + @PKG@.AbilMath.fmt(z.r);
}""")
# ---- MANA BARRIER (walking shape): the dome; cap = maxAbsorb % of the Mage's max Health at the cast
M(abil, r"""
public static String barrierCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, @PKG@.AbilWorld aw, double[] at, long now) {
  double mh = max(map(st, ref), @DST@.getHealth());
  if (!(mh > 0.0)) mh = 100.0;
  long life = Math.round(@PKG@.AbilCfg.B_TIME * 1000.0);
  @PKG@.AbilZone z = new @PKG@.AbilZone(1, u, at[0], at[1], at[2], @PKG@.AbilCfg.B_RADIUS, now, now + life);
  z.pkey = @PKG@.ClassCfg.pkey(u);
  z.name = pr.getUsername();
  z.ratio = @PKG@.AbilCfg.B_RATIO;
  z.cap = mh * (double) @PKG@.AbilCfg.B_MAX / 100.0;
  ring(FX_BARRIER, z, st);
  say(pr, "Mana Barrier: a dome of " + @PKG@.AbilMath.fmt(z.r) + " blocks for " + @PKG@.AbilMath.secs(life) + " s - damage to you inside costs Mana ("
      + @PKG@.AbilMath.fmt(z.ratio) + " per Mana) instead of Health.");
  int gone = aw.addZone(z);   // last - castNow refunds a cast whose executor throws, so nothing may be live before this point (FIX ROUND: after say)
  return spotText(z) + " cap=" + @PKG@.AbilMath.fmt(z.cap) + (gone > 0 ? " replaced=" + gone : "");
}""")
# ---- SHIELD BUBBLE (walking shape): HP = hp % of the Priest's max Health at the cast
M(abil, r"""
public static String bubbleCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, @PKG@.AbilWorld aw, double[] at, long now) {
  double mh = max(map(st, ref), @DST@.getHealth());
  if (!(mh > 0.0)) mh = 100.0;
  long life = Math.round(@PKG@.AbilCfg.U_TIME * 1000.0);
  @PKG@.AbilZone z = new @PKG@.AbilZone(2, u, at[0], at[1], at[2], @PKG@.AbilCfg.U_RADIUS, now, now + life);
  z.pkey = @PKG@.ClassCfg.pkey(u);
  z.name = pr.getUsername();
  z.hpMax = mh * (double) @PKG@.AbilCfg.U_HP / 100.0;
  z.hp = z.hpMax;
  particle(FX_BUBBLE_ON, at[0], at[1] + 1.0, at[2], st);
  ring(FX_BUBBLE, z, st);
  say(pr, "Shield Bubble: " + @PKG@.AbilMath.fmt(z.hpMax) + " HP for " + @PKG@.AbilMath.secs(life) + " s - it soaks attacks on you and your party inside and heals at 75 / 50 / 25 % and when it breaks.");
  int gone = aw.addZone(z);   // last (see barrierCast)
  return spotText(z) + " hp=" + @PKG@.AbilMath.fmt(z.hpMax) + (gone > 0 ? " replaced=" + gone : "");
}""")
# THE SHIELD HOOK (AbilShieldSys.handle, the Filter group after armour; the world thread). r = the damaged PLAYER. Returns what it did
# (null = nothing - the harness reads it). 1: the strongest Shield Bubble covering an ally soaks an ATTACK; 2: the Mage's own Mana Barrier
# pays the rest with Mana. Fully soaked = cancelled, partly = the amount lowered.
M(abil, r"""
public static String shield(@ST@ st, @CB@ buf, @REF@ r, @DMG@ d, long now) {
  if (d == null || r == null || d.isCancelled()) return null;
  if (@PKG@.AbilWorld.BY.isEmpty()) return null;
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  if (aw == null || aw.nz <= 0) return null;
  float amt0 = d.getAmount();
  if (!(amt0 > 0.0f)) return null;
  if (@PKG@.AbilDmg.mine(d)) return null;
  @DCS@ cause = null;
  try { cause = d.getCause(); } catch (Throwable t) { cause = null; }
  if (cause != null && (cause == @DCS@.OUT_OF_WORLD || cause == @DCS@.COMMAND)) return null;
  Object po = buf.getComponent(r, @PR@.getComponentType());
  if (!(po instanceof @PR@)) return null;
  if (buf.getComponent(r, @INVU@.getComponentType()) != null) return null;   // FIX ROUND: invulnerable - the engine drops the hit (fallback guard)
  java.util.UUID u = ((@PR@) po).getUuid();
  if (u == null) return null;
  @VEC@ p = pos(buf, r);
  if (p == null) return null;
  @PKG@.AbilZone[] zs = aw.zoneArr();
  double amt = (double) amt0;
  String out = "";
  if (d.getSource() instanceof @DENT@) {
    // FIX ROUND (critic: a party alt hitting an ally farmed absorb XP): a hit by a PLAYER is soaked but pays no absorb XP
    boolean pvp = false;
    try {
      @REF@ att = ((@DENT@) d.getSource()).getRef();
      pvp = att != null && att.isValid() && buf.getComponent(att, @PR@.getComponentType()) != null;
    } catch (Throwable t) { pvp = false; }
    @PKG@.AbilZone best = null;
    for (int i = 0; i < zs.length; i++) {
      @PKG@.AbilZone z = zs[i];
      if (z.kind != 2 || z.ended || !(z.hp > 0.0) || now >= z.until) continue;
      if (!@PKG@.AbilMath.inRange(p.x - z.x, p.y - z.y, p.z - z.z, z.r)) continue;
      if (!u.equals(z.caster) && !@PKG@.HealTask.inParty(z.caster, u)) continue;
      if (best == null || z.hp > best.hp) best = z;
    }
    if (best != null) {
      double take = @PKG@.AbilMath.bubbleTake(amt, best.hp);
      best.hp = best.hp - take;
      if (best.hp < 1.0E-6) best.hp = 0.0;
      int due = @PKG@.AbilMath.pulsesDue(best.hpMax, best.hp);
      if (due > best.pulsesDue) best.pulsesDue = due;
      best.absorbed = best.absorbed + take;
      if (pvp) { }
      else if (u.equals(best.caster)) best.xpSelf = best.xpSelf + take;
      else best.xpOthers = best.xpOthers + take;
      amt = amt - take;
      out = "bubble:" + @PKG@.AbilMath.fmt(take);
    }
  }
  if (amt > 1.0E-4) {
    @PKG@.AbilZone bz = null;
    for (int i = 0; i < zs.length; i++) {
      @PKG@.AbilZone z = zs[i];
      if (z.kind != 1 || z.ended || now >= z.until || !u.equals(z.caster)) continue;
      if (z.pkey != null && !z.pkey.equals(@PKG@.ClassCfg.pkey(u))) continue;   // FIX3: a profile switch -> the dome is not this profile's (zoneTick ends it)
      if (!@PKG@.AbilMath.inRange(p.x - z.x, p.y - z.y, p.z - z.z, z.r)) continue;
      if (bz == null || z.cap - z.absorbed > bz.cap - bz.absorbed) bz = z;
    }
    if (bz != null) {
      @ESM@ m = map(buf, r);
      int mi = @DST@.getMana();
      double mana = cur(m, mi);
      if (mana >= 0.0) {
        double take = @PKG@.AbilMath.barrierTake(amt, mana, bz.ratio, bz.cap - bz.absorbed);
        if (take > 0.0) {
          double cost = take / bz.ratio;
          m.subtractStatValue(mi, (float) cost);
          bz.absorbed = bz.absorbed + take;
          bz.manaPaid = bz.manaPaid + cost;
          amt = amt - take;
          out = out + (out.length() > 0 ? " " : "") + "barrier:" + @PKG@.AbilMath.fmt(take) + "/" + @PKG@.AbilMath.fmt(cost);
          if (mana - cost <= 0.01) { bz.ended = true; bz.why = "mana"; }
          else if (bz.absorbed >= bz.cap - 1.0E-6) { bz.ended = true; bz.why = "cap"; }
        } else if (mana <= 0.01) { bz.ended = true; bz.why = "mana"; }
      }
    }
  }
  if (amt >= (double) amt0 - 1.0E-6) return null;
  if (amt <= 1.0E-3) {
    d.setAmount(0.0f);
    d.setCancelled(true);
    return out + " cancelled";
  }
  d.setAmount((float) amt);
  return out + " left=" + @PKG@.AbilMath.fmt(amt);
}""")
# the players of this world inside a zone (the caster included when inside): uuids + refs
M(abil, r"""
public static void inside(@ST@ st, @CAC@ acc, @PKG@.AbilZone z, java.util.ArrayList us, java.util.ArrayList rs) {
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ p = (@PR@) it.next();
    if (p == null || !p.isValid()) continue;
    java.util.UUID pu = p.getUuid();
    if (pu == null) continue;
    @REF@ r = p.getReference();
    if (r == null || !r.isValid() || r.getStore() != st) continue;
    @VEC@ q = pos(acc, r);
    if (q == null || !@PKG@.AbilMath.inRange(q.x - z.x, q.y - z.y, q.z - z.z, z.r)) continue;
    us.add(pu);
    rs.add(r);
  }
}""")
# XP is paid to the profile that cast it only, never in creative (the hotTick rule)
M(abil, r"""
public static boolean xpOk(@PKG@.AbilZone z, @ST@ st, @CAC@ acc) {
  @PR@ hp = @UNI@.get().getPlayer(z.caster);
  if (hp == null || !hp.isValid()) return false;
  @REF@ hr = hp.getReference();
  if (hr == null || !hr.isValid()) return false;
  if (hr.getStore() == st && creative(acc, hr)) return false;
  return z.pkey == null || z.pkey.equals(@PKG@.ClassCfg.pkey(z.caster));
}""")
# ONE heal pulse of a bubble: everyone inside, pulse % of their max Health (the Priest + party full, others the othersPercent share), the
# abil.healCap per target per bubble; Divinity XP like Sacred Heal; returns the HP healed
M(abil, r"""
public static double pulse(@PKG@.AbilZone z, @ST@ st, @CAC@ acc, boolean xp) {
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  inside(st, acc, z, us, rs);
  double others = 0.0;
  double self = 0.0;
  for (int i = 0; i < us.size(); i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    @REF@ r = (@REF@) rs.get(i);
    if (!healable(acc, r)) continue;
    double mx = max(map(acc, r), @DST@.getHealth());
    if (!(mx > 0.0)) continue;
    boolean isSelf = t.equals(z.caster);
    boolean party = isSelf || @PKG@.HealTask.inParty(z.caster, t);
    double want = @PKG@.HealTask.split(mx * (double) @PKG@.AbilCfg.U_PULSE / 100.0, party, @PKG@.ClassCfg.HEAL_OTHERS_PCT);
    Object dn = z.healed.get(t);
    double done = dn instanceof Double ? ((Double) dn).doubleValue() : 0.0;
    double got = apply(acc, r, want, @PKG@.AbilMath.capLeft(mx, @PKG@.AbilCfg.HEAL_CAP, done));
    if (!(got > 0.0)) continue;
    z.healed.put(t, Double.valueOf(done + got));
    @VEC@ q = pos(acc, r);
    if (q != null) particle(FX_HEAL, q.x, q.y + 1.0, q.z, acc);
    if (isSelf) { self = self + got; @PKG@.HealMsg.given(z.caster, z.caster, got); }
    else { others = others + got; @PKG@.HealMsg.given(z.caster, t, got); @PKG@.HealMsg.taken(t, z.caster, z.name, got); }
  }
  if (xp) {
    if (others > 0.0) @PKG@.HealTask.xp(z.caster, others);
    if (self > 0.0) @PKG@.HealTask.xpSelf(z.caster, self);
  }
  return others + self;
}""")
# the absorb XP the shield hook counted (spec draft 2.4: 0.5 XP per HP soaked - others at the heal rate, the Priest's own at the self rate)
M(abil, r"""
public static void payXp(@PKG@.AbilZone z, boolean xp) {
  double o = z.xpOthers;
  double s = z.xpSelf;
  z.xpOthers = 0.0;
  z.xpSelf = 0.0;
  if (!xp) return;
  if (o > 0.0) @PKG@.HealTask.xp(z.caster, o * 0.5);
  if (s > 0.0) @PKG@.HealTask.xpSelf(z.caster, s * 0.5);
}""")
M(abil, r"""
public static String endLine(@PKG@.AbilZone z) {
  String w = z.why == null ? "" : z.why;
  if (z.kind == 1) {
    String head = w.equals("mana") ? "Mana Barrier ended - out of Mana" : (w.equals("cap") ? "Mana Barrier ended - it soaked all it can" : (w.equals("replaced") ? "Mana Barrier ended - a newer zone replaced it" : "Mana Barrier ended"));
    return head + " (" + @PKG@.AbilMath.fmt(z.absorbed) + " damage soaked for " + @PKG@.AbilMath.fmt(z.manaPaid) + " Mana).";
  }
  String head = w.equals("broken") ? "Shield Bubble broke" : (w.equals("replaced") ? "Shield Bubble ended - a newer zone replaced it" : "Shield Bubble faded");
  return head + " (" + @PKG@.AbilMath.fmt(z.absorbed) + " damage soaked, " + z.pulsesDone + " heal pulse" + (z.pulsesDone == 1 ? "" : "s") + ").";
}""")
M(abil, r"""
public static void zoneEnd(@PKG@.AbilZone z, @CAC@ acc) {
  z.ended = true;
  particle("broken".equals(z.why) ? FX_BREAK : FX_END, z.x, z.y + 1.0, z.z, acc);
  if ("left".equals(z.why)) return;
  @PR@ pr = @UNI@.get().getPlayer(z.caster);
  if (pr != null) say(pr, endLine(z));
}""")
# one zone tick (AbilWorld.run, the world thread, every abil.tick); false = the zone is over (dropped by the caller)
M(abil, r"""
public static boolean zoneTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind == 1 && !z.ended) {
    @REF@ cr = null;
    try { cr = ((@ES@) cb.getExternalData()).getRefFromUUID(z.caster); } catch (Throwable t) { cr = null; }
    if (cr == null || !cr.isValid() || !alive(cb, cr) || (z.pkey != null && !z.pkey.equals(@PKG@.ClassCfg.pkey(z.caster)))) {
      z.why = "left";
    } else {
      double mana = cur(map(cb, cr), @DST@.getMana());
      if (mana >= 0.0 && mana <= 0.01) { z.ended = true; z.why = "mana"; }
    }
    if ("left".equals(z.why)) { zoneEnd(z, cb); return false; }
  }
  if (z.ended) { zoneEnd(z, cb); return false; }
  boolean xp = xpOk(z, st, cb);
  if (z.kind == 2) {
    while (z.pulsesDone < z.pulsesDue && z.pulsesDone < 4) {
      z.pulsesDone = z.pulsesDone + 1;
      pulse(z, st, cb, xp);
    }
    payXp(z, xp);
    if (!(z.hp > 0.0)) { z.why = "broken"; zoneEnd(z, cb); return false; }
  }
  if (now >= z.until) { z.why = "time"; zoneEnd(z, cb); return false; }
  if (now >= z.nextFx) {
    z.nextFx = now + 1000L;
    ring(z.kind == 1 ? FX_BARRIER : FX_BUBBLE, z, cb);
  }
  return true;
}""")
# the HUD SAMPLE (AbilTick, the world thread): Mana, Stamina, crouch, creative of a player whose HUD asked within 5 s, at most every 0.2 s
M(abil, r"""
public static void sample(@REF@ r, @CAC@ acc, long now) {
  try {
    if (r == null || !r.isValid()) return;
    Object o = acc.getComponent(r, @PR@.getComponentType());
    if (!(o instanceof @PR@)) return;
    java.util.UUID u = ((@PR@) o).getUuid();
    if (u == null) return;
    Object w = @PKG@.AbilStore.WANT.get(u);
    if (!(w instanceof Long)) return;
    if (now - ((Long) w).longValue() > 5000L) { @PKG@.AbilStore.WANT.remove(u); @PKG@.AbilStore.SAMPLE.remove(u); return; }
    Object s = @PKG@.AbilStore.SAMPLE.get(u);
    if (s instanceof double[]) {
      long at = (long) ((double[]) s)[4];
      if (now - at < 200L && now >= at) return;
    }
    @ESM@ m = map(acc, r);
    double mana = cur(m, @DST@.getMana());
    double stam = cur(m, @DST@.getStamina());
    @PKG@.AbilStore.SAMPLE.put(u, new double[] { mana, stam, crouching(acc, r) ? 1.0 : 0.0, creative(acc, r) ? 1.0 : 0.0, (double) now });
  } catch (Throwable t) { }
}""")
'''
rep('''M(abil, r"""
public static String castNow(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg) {''', ZONE_SRC + '''M(abil, r"""
public static String castNow(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg) {''')

# ================================================================================================ castNow: the spot + the two executors
rep('''  if (ai == @PKG@.AbilDefs.SACRED && needHeal(st, ref, u) == 0) {''', '''  if (ai == @PKG@.AbilDefs.MANAB || ai == @PKG@.AbilDefs.BUBBLE) {   // 0.1.17: where you look within the reach, else at your feet
    at = spot(st, ref, ai == @PKG@.AbilDefs.MANAB ? @PKG@.AbilCfg.B_RANGE : @PKG@.AbilCfg.U_RANGE);
    if (at == null) { refuse(pr, "Could not find where to place " + nm + " - nothing was spent."); return "aim"; }
  }
  if (ai == @PKG@.AbilDefs.MANAB && at != null) {   // FIX ROUND (critic: a dome she is not standing in): it must cover the Mage, else her feet
    @VEC@ me = pos(st, ref);
    if (me != null && !@PKG@.AbilMath.inRange(at[0] - me.x, at[1] - me.y, at[2] - me.z, @PKG@.AbilCfg.B_RADIUS - 0.5)) at = new double[] { me.x, me.y, me.z };
  }
  if (ai == @PKG@.AbilDefs.SACRED && needHeal(st, ref, u) == 0) {''')
rep('''    else if (ai == @PKG@.AbilDefs.SACRED) extra = healCast(pr, st, ref, u, aw, now);''',
    '''    else if (ai == @PKG@.AbilDefs.SACRED) extra = healCast(pr, st, ref, u, aw, now);
    else if (ai == @PKG@.AbilDefs.MANAB) extra = barrierCast(pr, st, ref, u, aw, at, now);    // 0.1.17
    else if (ai == @PKG@.AbilDefs.BUBBLE) extra = bubbleCast(pr, st, ref, u, aw, at, now);    // 0.1.17''')

# FIX ROUND (critic: a cast at exactly the cost made a dome that ended at once): Mana Barrier needs ab.ManaBarrier.keep Mana LEFT
rep('''  double[] at = null;
  if (ai == @PKG@.AbilDefs.METEOR) {''', '''  if (ai == @PKG@.AbilDefs.MANAB && !free && @PKG@.AbilCfg.B_KEEP > 0.0 && hm >= 0.0 && !@PKG@.AbilMath.enough(hm, mana + @PKG@.AbilCfg.B_KEEP)) {   // FIX ROUND
    refuse(pr, "Not enough Mana to power the Mana Barrier: " + @PKG@.AbilMath.fmt(mana) + " to cast + " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.B_KEEP)
        + " left to soak with (you have " + @PKG@.AbilMath.fmt(hm) + ") - nothing was spent.");
    return "mana";
  }
  double[] at = null;
  if (ai == @PKG@.AbilDefs.METEOR) {''')

# ================================================================================================ the HUD bridge: Object[44]
rep('''    long now = System.currentTimeMillis();
    Object[] out = new Object[16];
    for (int i = 0; i < 4; i++) {
      int ai = @PKG@.AbilDefs.find(sl[i]);
      out[i * 4] = ai < 0 ? "" : @PKG@.AbilDefs.NAMES[ai];
      out[i * 4 + 1] = Long.valueOf(ai < 0 ? 0L : @PKG@.AbilStore.left(k, @PKG@.AbilDefs.IDS[ai], now));
      out[i * 4 + 2] = Long.valueOf(ai < 0 ? 0L : @PKG@.AbilStore.total(k, @PKG@.AbilDefs.IDS[ai]));
      out[i * 4 + 3] = @PKG@.Abil.stateOf(ai, k, lv, grant, pick, now);
    }
    return out;''', '''    long now = System.currentTimeMillis();
    Object[] out = new Object[44];   // 0.1.17: [0-15] as 0.1.16; the rest = the R2 widget's data (tools/classes_0_1_17_patch.py)
    @PKG@.AbilStore.WANT.put(u, Long.valueOf(now));
    double[] smp = null;
    Object so = @PKG@.AbilStore.SAMPLE.get(u);
    if (so instanceof double[] && ((double[]) so).length >= 5) {
      double[] sv = (double[]) so;
      long at = (long) sv[4];
      if (now - at <= 3000L && at - now <= 1000L) smp = sv;
    }
    boolean free = smp != null && @PKG@.AbilCfg.CREATIVE_FREE && smp[3] > 0.5;
    for (int i = 0; i < 4; i++) {
      int ai = @PKG@.AbilDefs.find(sl[i]);
      out[i * 4] = ai < 0 ? "" : @PKG@.AbilDefs.NAMES[ai];
      out[i * 4 + 1] = Long.valueOf(ai < 0 ? 0L : @PKG@.AbilStore.left(k, @PKG@.AbilDefs.IDS[ai], now));
      out[i * 4 + 2] = Long.valueOf(ai < 0 ? 0L : @PKG@.AbilStore.total(k, @PKG@.AbilDefs.IDS[ai]));
      out[i * 4 + 3] = @PKG@.Abil.stateOf(ai, k, lv, grant, pick, now);
      double mc = ai < 0 ? 0.0 : @PKG@.AbilDefs.mana(ai);
      double sc = ai < 0 ? 0.0 : @PKG@.AbilDefs.stamina(ai);
      out[16 + i] = ai < 0 ? "" : @PKG@.AbilDefs.IDS[ai];
      out[20 + i] = Double.valueOf(mc);
      out[24 + i] = Double.valueOf(sc);
      out[38 + i] = Long.valueOf(ai < 0 ? 0L : @PKG@.AbilDefs.unlock(@PKG@.AbilDefs.TIER[ai]));
      String st = (String) out[i * 4 + 3];
      if (smp != null && smp[0] >= 0.0 && smp[1] >= 0.0 && ("ready".equals(st) || "cooldown".equals(st)))
        out[28 + i] = Boolean.valueOf(free || (@PKG@.AbilMath.enough(smp[0], mc + (ai == @PKG@.AbilDefs.MANAB ? @PKG@.AbilCfg.B_KEEP : 0.0)) && @PKG@.AbilMath.enough(smp[1], sc)));   // FIX ROUND: + the Mana Barrier keep
    }
    if (smp != null) {
      out[32] = Boolean.valueOf(smp[2] > 0.5);
      out[34] = Double.valueOf(smp[0]);
      out[35] = Double.valueOf(smp[1]);
      out[36] = Boolean.valueOf(free);
      out[42] = Long.valueOf(now - (long) smp[4]);
    }
    out[33] = @PKG@.ClassDefs.NAMES[ci];
    out[37] = "abil2";
    return out;''')

# ================================================================================================ AbilWorld.run: + the zones; AbilTick: + the HUD sample
rep('''    try { again = @PKG@.Abil.runJob(j, st, cb, now); } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("ability job failed: " + t); }
    if (again) add(j);
  }
}""")''', '''    try { again = @PKG@.Abil.runJob(j, st, cb, now); } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("ability job failed: " + t); }
    if (again) add(j);
  }
  if (this.nz > 0 && now >= this.nextZone) {   // 0.1.17: the zones, every abil.tick
    long every = Math.round(@PKG@.AbilCfg.TICK * 1000.0);
    if (every < 50L) every = 50L;
    this.nextZone = now + every;
    @PKG@.AbilZone[] zs = zoneArr();
    for (int i = 0; i < zs.length; i++) {
      boolean keep = false;
      try { keep = @PKG@.Abil.zoneTick(zs[i], st, cb, now); } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("ability zone failed (it ends): " + t); keep = false; }
      if (!keep) dropZone(zs[i]);
    }
  }
}""")''')
rep('''public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(store);''', '''public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (chunk != null && !@PKG@.AbilStore.WANT.isEmpty()) @PKG@.Abil.sample(chunk.getReferenceTo(idx), cb, System.currentTimeMillis());   // 0.1.17: the HUD sample
  } catch (Throwable t0) { }
  try {
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(store);''')

# ================================================================================================ AbilShieldSys (+ U) after AbilTick
rep('''# ---- /cast (player): bare = the list; the usage variant takes one word (HANDOFF COMMAND RULES 2: a variant per positional form)
castc = pool.makeClass(PKG + ".CastCmd", pool.get(T["APC"]))''', '''# ---- 0.1.17 AbilShieldSys: DamageEventSystem in the FILTER group, players only, AFTER the engine's DamageSystems$ArmorDamageReduction (the
# SkyySkills DefSys / SkyyGear GearArmorSys place: armour first, then the zones). AbilShieldSysU = the unordered fallback (one registerSystem
# per class; registered only when the ordered one could not be). The order vs SkyyGear / SkyySkills (also AFTER armour) is unordered (P5).
abshield = pool.makeClass(PKG + ".AbilShieldSys", pool.get(T["DES"]))
F(abshield, "public java.util.Set deps;")
F(abshield, "public static boolean FAILED_ONCE = false;")
F(abshield, 'public static final String ADR = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction";')
# FIX ROUND (critic: a hit the engine drops later still cost Mana / bubble HP): also AFTER the Filter-group systems that cancel hits (each
# only when its class resolves; ArmorDamageReduction stays required - no class = the unordered fallback)
F(abshield, 'public static final String[] DROPS = new String[] { "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$FilterUnkillable", '
            '"com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$FilterPlayerWorldConfig", '
            '"com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$PlayerDamageFilterSystem" };')
C(abshield, r"""
public AbilShieldSys(boolean ordered) {
  super();
  if (ordered) {
    java.util.LinkedHashSet s = new java.util.LinkedHashSet();
    s.add(new @SDEP@(@ORD@.AFTER, Class.forName(ADR)));
    for (int i = 0; i < DROPS.length; i++) {
      try { s.add(new @SDEP@(@ORD@.AFTER, Class.forName(DROPS[i]))); } catch (Throwable t) { }
    }
    this.deps = java.util.Collections.unmodifiableSet(s);
  } else this.deps = java.util.Collections.EMPTY_SET;
}""")
M(abshield, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(abshield, "public @SG@ getGroup() { return @DMOD@.get().getFilterDamageGroup(); }")
M(abshield, "public java.util.Set getDependencies() { return this.deps; }")
M(abshield, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@) || chunk == null) return;
    if (@PKG@.AbilWorld.BY.isEmpty()) return;
    @PKG@.Abil.shield(st, buf, chunk.getReferenceTo(idx), (@DMG@) ev, System.currentTimeMillis());
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ClassCfg.warn("ability zones: the damage hook failed (logged once, that hit was left alone): " + t); }
  }
}""")
abshieldu = pool.makeClass(PKG + ".AbilShieldSysU", abshield)
C(abshieldu, "public AbilShieldSysU() { super(false); }")
# ---- /cast (player): bare = the list; the usage variant takes one word (HANDOFF COMMAND RULES 2: a variant per positional form)
castc = pool.makeClass(PKG + ".CastCmd", pool.get(T["APC"]))''')

# ================================================================================================ wiring: quit, setup, jar
rep('''    @PKG@.AbilStore.TOLD.remove(u);   // 0.1.16 (cooldowns stay: keyed by profile, a relog must not reset them)''',
    '''    @PKG@.AbilStore.TOLD.remove(u);   // 0.1.16 (cooldowns stay: keyed by profile, a relog must not reset them)
    @PKG@.AbilStore.WANT.remove(u);   // 0.1.17: the HUD sample (zones run on: a Mana Barrier ends at its next tick, the caster is gone)
    @PKG@.AbilStore.SAMPLE.remove(u);''')
rep('''  getEntityStoreRegistry().registerSystem(new @PKG@.AbilTick());        // 0.1.16: the delayed ability jobs (Meteor impact, heal over time)
''', '''  getEntityStoreRegistry().registerSystem(new @PKG@.AbilTick());        // 0.1.16: the delayed ability jobs (Meteor impact, heal over time)
  try {
    getEntityStoreRegistry().registerSystem(new @PKG@.AbilShieldSys(true));   // 0.1.17: Mana Barrier / Shield Bubble, AFTER ArmorDamageReduction
  } catch (Throwable t) {
    @PKG@.ClassCfg.warn("could not order AbilShieldSys after ArmorDamageReduction (" + t + ") - unordered fallback: the zones still soak damage");
    try { getEntityStoreRegistry().registerSystem(new @PKG@.AbilShieldSysU()); } catch (Throwable t2) { @PKG@.ClassCfg.warn("could not register AbilShieldSysU - no Mana Barrier / Shield Bubble soaking this start: " + t2); }
  }
''')
rep('''          abcfg, abdmg, abhit, abdefs, abmath, abst, absave, abjob, abworld, abil, abfn, abtick, castc, casta, aabil):   # 0.1.16: + 15 ability classes''',
    '''          abcfg, abdmg, abhit, abdefs, abmath, abst, absave, abjob, abworld, abil, abfn, abtick, castc, casta, aabil,   # 0.1.16: + 15 ability classes
          abzone, abshield, abshieldu):   # 0.1.17: + the zone + its damage hook''')
rep('''class abilities with /cast (Mage Meteor, Priest Sacred Heal; crouch = your alts).''',
    '''class abilities with /cast (Mage Meteor + Mana Barrier, Priest Sacred Heal + Shield Bubble; crouch = your alts).''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0 + 2, "one AbilShieldSys + its fallback, no command"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.1.16 outside the recorded changes"
# javassist order: helpers before callers
for a_, b_ in (("public static double barrierTake(", "public static String shield("), ("public static int pulsesDue(", "public static String shield("),
               ("public synchronized int addZone(", "public static String barrierCast("), ("public static String barrierCast(", "public static String castNow("),
               ("public static String bubbleCast(", "public static String castNow("), ("public static double[] spot(", "public static String castNow("),
               ("public static double pulse(", "public static boolean zoneTick("), ("public static void zoneEnd(", "public static boolean zoneTick("),
               ("public static boolean zoneTick(", "public void run(@ST@ st, @CB@ cb, long now)"), ("public static void sample(", "public void tick(float dt"),
               ("public static String shield(", "public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {\n  try {\n    if (!(ev instanceof @DMG@) || chunk == null)"),
               ('abzone = pool.makeClass(PKG + ".AbilZone")', "public synchronized int prune(long now)")):
    assert s.index(a_) < s.index(b_), "javassist order: %s before %s" % (a_, b_)
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.1.16 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
