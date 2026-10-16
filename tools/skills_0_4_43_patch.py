"""Derive SkyySkills/build_skyyskills_0.4.43.py from the GENERATED SkyySkills 0.4.42 (build_skyyskills_0.4.42.py = the tools/deploy_set.py SET
pin; 0.4.42 came from 0.4.41 by tools/skills_0_4_42_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.42 (nothing else changed); 0.4.42 stays untouched, its line endings are kept.
Run:  python tools/skills_0_4_43_patch.py   then   python SkyySkills/build_skyyskills_0.4.43.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.43.py

0.4.43 (2026-10-15) = BASE HEALTH REGEN (lean round skills0443; Skyy 2026-10-15: "and id add a little default health regent everyone spawns
with. then have it go up from there." Popups: "Base health regen for everyone: when should it tick?" -> "Always, faster out of combat
(Recommended)" (0.2 HP/s in fights, 1 HP/s after 5 s out of combat); "What makes health regen go up from there?" -> "Overall Level
(Recommended), A Health Regen stat on gear, Skill tree nodes").
  VANILLA 0.7.2 (Assets.zip Server/Entity/Stats/Health.json, read 2026-10-15): players in Adventure have NO passive Health regen - the two
  regen entries are NPCs (IsPlayer inverse, 5 % every 0.5 s after 15 s without damage) and Creative players (100 % every 0.5 s). Food and
  potions add timed HealthRegen effects. No SET jar overrides Health.json; the pack mod raz:Passive Health Regeneration (PassiveHealth-
  Regeneration.zip, an asset-only Health.json override) is switched OFF in every world - it would stack (0.1 % of max a second) if enabled.
  Ours is ADDED on top of whatever else heals (food / potion effects, SkyyGear's Raw Health Regen, SkyyAccessories' Regeneration, Priest
  heals, the Overall level-up heal): every source adds to the same Health stat and the engine never goes above max.
  1. HpRegen (new class): one pulse every 0.5 s per player from AcroSys (after ManaRegen.tick, world thread, own clock + own try), the
     amount = rate x the seconds since the last pulse (at most 1 s), straight onto the engine's Health stat (EntityStatMap.addStatValue on
     DefaultEntityStatTypes.getHealth() - the path Perks.ovl's level-up heal and ManaRegen use). Never while a DeathComponent is on the
     player or Health is 0 (dead), never above max (the room left is the cap), nothing at full Health.
     IN COMBAT = the SkyyWardrobe 0.2.2 / SkyyPets 0.3.0 gate: the newest of DamageDataComponent.lastDamageTime (hurt) and
     lastCombatAction (the engine's RecordLastCombat stamps it on the victim AND the attacker of every Damage) on the world clock is less
     than hp.regen.combatSeconds (5 s) old. So hitting a monster counts as fighting too. The stamps are the ones ManaRegen.carry keeps
     right across world switches.
     RATE (HP a second) = (base + Overall Level x per level + the flat bridge sources) x (1 + the % bridge sources / 100), at least 0, at
     most 1000: in combat hp.regen.inCombat (0.2) + hp.regen.perLevel.inCombat (0.02) per Overall Level; out of combat
     hp.regen.outOfCombat (1) + hp.regen.perLevel.outOfCombat (0.05) per level. Overall Level = skill:overall:<uuid> (Perks.ovl publishes
     it every second; memory only). Level 0: 0.2 / 1; level 25: 0.7 / 2.25; level 50: 1.2 / 3.5; level 100: 2.2 / 6 HP a second
     (base max Health 100 + 0.5 per Overall Level: a level 50 player refills 125 HP in about 36 s after a fight, about 1 % a second in one).
  2. BRIDGE skill:fn:hpregen (HpRegenFn, the skill:fn:manaregen shape; java.lang types only, never throws, any thread, memory only):
       {"add", UUID, String source, Number hpPerSecond} -> Boolean   flat HP a second in and out of combat (0 removes; -100..100)
       {"addpct", UUID, String source, Number percent}  -> Boolean   percent more of the whole regen (0 removes; -100..1000)
       {"remove", UUID, String source} -> Boolean                    both kinds of that source; TRUE = there was one
       {"clear", String source} -> Integer                           that source removed from every player (a provider's shutdown)
       {"get", UUID} -> Double[] {in combat, out of combat}           HP a second that apply to this player now
       {"now", UUID} -> Double                                        the rate of the last pulse (0 at full / dead / never ticked)
       {"fight", UUID} -> Boolean                                     the last pulse said "in combat"
       {"sources", UUID} -> String[]                                  "source=+2/s" / "source=+20%", sorted
       {"row", UUID} -> String[] {value, detail}                      SkyyMenu's Character > Stats row ("3.5/s", "1.2/s in combat; ...")
     Nothing registers yet: SkyyGear's Raw Health Regen / Health Regen % (GearFx, its own 2 s heal) and SkyyAccessories' Regeneration
     still heal by themselves; SkyyTrees has no Health regen node. The main session queues those halves (they move onto this registry).
  3. SERVER SETUP (Skills -> Overall and Mana): hp.regen.enabled, hp.regen.inCombat, hp.regen.outOfCombat, hp.regen.combatSeconds (s),
     hp.regen.perLevel.inCombat, hp.regen.perLevel.outOfCombat + the action "Health Regen: show mine". A fresh xp.properties lists the
     0.4.43 block; an existing file without it reads the same code defaults (no migration, nothing rewritten). The overall.healOnLevelUp
     help no longer says players have no Health regen.
  No saved data for the regen, no command, no new system registration, no item / asset change. Players who left: HpRegen.retain
  (Acro.retainOnline).
  (A) SPELLBLADE CLASS SKILL (Skyy 2026-10-15, a Spellblade profile's Character > Skills row read "Class skill - choose a class with /class"
  and the HUD "Battlemagic -": "bug with the spell blade not loading right in the skills menu"). Cause: SkyyClasses 0.1.25 added the 8th
  class (skill Battlemagic, colour #6fd0d8) as a card APPENDED after its CLASSES literal, and SkyySkills' CLASS_ROWS never got it (only
  FUTURE_CLASSES = the number tables) - no storage slot, so SkillClass.slotOfClass("Spellblade") = -1: the class row showed "choose a
  class", Spellblade kills paid NO class skill XP and the class skill counted 0 in the Overall Level / class Mana / class Stamina /
  class balance. Fix: CLASS_ROWS += ("Spellblade", "Battlemagic", Weapon_Longsword_Iron, #6fd0d8) = storage slot 19, APPENDED after
  Fishing / Ranching / Orchard (saved key Combat.Spellblade; no slot renumbered - the 0.4.4 Berserker / Priest and 0.4.37 recipe); the
  roster check also reads SkyyClasses' appended "CLASSES += [ ... ]" cards; FUTURE_CLASSES is empty (OverallCfg.TCLASSES keeps the same
  8 names in the same order, every Spellblade table line stays); KIT_FALLBACK + the Spellblade kit (Weapon_Longsword_Crude); alias
  "battle magic". Everything else is the generic class machinery (SkillDefs.CLASSES / CLASS_SLOT): class:<uuid> "Spellblade" -> slot
  19, the row title = class:skill:<uuid> "Battlemagic", kill XP, Overall Level, class Mana / Stamina / balance, leaderboards, rebirth
  (a rebirth staged without x.Combat.Spellblade leaves the slot as it is - the 0.4.37 rule covers slots >= 16).
  SAVED DATA: players/<pkey>.properties gains Combat.Spellblade + Combat.Spellblade.paid; an older file without them = 0 XP, paid = the
  level (no retroactive rewards). 0.4.42 reads only the keys it knows (readFile loops SkillDefs.NAMES) - it does NOT break on the new
  key, BUT its save rewrites the file from its own NAMES (snap), so the Battlemagic XP of a player who logs in under 0.4.42 is DROPPED.
  ROLLBACK FLOOR: rolling back below 0.4.43 loses Battlemagic XP of every Spellblade who plays on the older jar.
  (C) MINING VS FORAGING (Skyy 2026-10-15: "foraging levels like twice as fast as mining because breaking trees is easy." Popup "How
  should we even it out?" -> "felled logs give a little less xp, and increase the mining xp a bit"). New class XpEven, two NEW rows
  (Skills -> Gathering; fell.xpFactor keeps its 1.0 default, so no migration): fell.otherLogsPercent (70) - FellCredit.one pays every
  felled LOG but the one the player chopped (that one is BreakTask's normal break XP, untouched) at 70 % of (table XP x fell.xpFactor);
  leaves keep fell.leafXpFactor. mining.xpMultiplier (1.25) - BreakTask.run multiplies the Mining XP of a mined block (XP only: drops,
  Fortune, collections, bags and quests count the blocks, not the XP). Fractions are paid by chance (XpEven.pay: 1 XP stone x 1.25 =
  1 or 2, 1.25 on average; a 6 XP log at 70 % = 4 or 5, 4.2 on average) - plain rounding would leave 1 XP stone at 1.
  PACE (the table XP: stone 1, Copper 5, Iron 8 ... ores up to 50; logs 6 (rare woods 10-30), leaves 1): an 8-log oak felled from one
  chop paid 48 log XP, now 6 + 7 x 4.2 = 35.4 (-26 %); mining +25 %. From Skyy's "about 2x": if the other felled logs are 50-70 % of
  Foraging XP (the rest = the chopped log, leaves, branches), Foraging drops to 0.79-0.85 x and Mining rises to 1.25 x, so the gap goes
  from 2x to about 1.3x. Foraging stays a little faster (leaves still pay full); the next levers are both rows + Felled leaf XP.
  ROLLBACK to 0.4.42 otherwise safe (the regen is memory only; 0.4.42 ignores the six new config lines and players stop regenerating).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.42.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.43.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.4.42"' in s and s.startswith('"""SkyySkills 0.4.42 - build script') and "HpRegen" not in s, "not the generated 0.4.42 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.43 (2026-10-15)"):].rstrip() + "\n"

# ================================================================================================ docstring + version
rep('''"""SkyySkills 0.4.42 - build script (derived from the generated 0.4.41 by tools/skills_0_4_42_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.43 - build script (derived from the generated 0.4.42 by tools/skills_0_4_43_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.43.py.
0.4.42 was derived from the generated 0.4.41 by tools/skills_0_4_42_patch.py;
''')
rep('VERSION = "0.4.42"', 'VERSION = "0.4.43"')

# ================================================================================================ (A) the Spellblade's class skill Battlemagic = slot 19
# the roster check reads SkyyClasses' CLASSES literal AND every "CLASSES += [ ... ]" card after it (0.1.25 appends the Spellblade there)
rep('''    m = _re.search(r"^CLASSES = \\[(.*?)^\\]", t, _re.M | _re.S)
    if not m: return best, None
    names = _re.findall(r'"name":\\s*"([A-Za-z]+)"', m.group(1))
''', '''    m = _re.search(r"^CLASSES = \\[(.*?)^\\]", t, _re.M | _re.S)
    if not m: return best, None
    names = _re.findall(r'"name":\\s*"([A-Za-z]+)"', m.group(1))
    for _m43 in _re.finditer(r"^CLASSES \\+= \\[(.*?)^\\]", t, _re.M | _re.S):   # 0.4.43: + the appended cards (the Spellblade, SkyyClasses 0.1.25+)
        names += _re.findall(r'"name":\\s*"([A-Za-z]+)"', _m43.group(1))
''')
rep('''              ("Berserker", "Fury", "Weapon_Battleaxe_Iron", "#d9443f"), ("Priest", "Divinity", "Weapon_Wand_Wood", "#f2e6a0")]
''', '''              ("Berserker", "Fury", "Weapon_Battleaxe_Iron", "#d9443f"), ("Priest", "Divinity", "Weapon_Wand_Wood", "#f2e6a0"),
              ("Spellblade", "Battlemagic", "Weapon_Longsword_Iron", "#6fd0d8")]   # 0.4.43: APPENDED = storage slot 19 (saved key Combat.Spellblade); SkyyClasses' card colour
''')
rep('''CLASS_SLOT = [5, 6, 7, 8, 9, 14, 15]
''', '''CLASS_SLOT = [5, 6, 7, 8, 9, 14, 15, 19]   # 0.4.43: + Spellblade / Battlemagic = slot 19 (after Fishing / Ranching / Orchard; nothing renumbered)
''')
rep('''_ROSTER = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk"]   # 0.4.21: SkyyClasses 0.1.14 (Shaman -> Monk)
''', '''_ROSTER = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"]   # 0.4.21: SkyyClasses 0.1.14 (Shaman -> Monk); 0.4.43: + Spellblade (0.1.25)
''')
rep('''SKILL_ALIASES += [("discipline", "Monk")]
''', '''SKILL_ALIASES += [("discipline", "Monk")]
SKILL_ALIASES += [("battle magic", "Spellblade")]   # 0.4.43: the skill name with a space (commands / bridge callers)
''')
rep('''_SL = [None] * (5 + len(CLASS_ROWS) + len(EXTRA_ROWS))
''', '''_SL = [None] * (5 + len(CLASS_ROWS[:7]) + len(EXTRA_ROWS))   # 0.4.43: slots 0-15 as before; the Spellblade (slot 19) is appended after GATHER37_ROWS
''')
rep('''for _i, _c in enumerate(CLASS_ROWS):
    assert _SL[CLASS_SLOT[_i]] is None, "slot %d used twice" % CLASS_SLOT[_i]
''', '''for _i, _c in enumerate(CLASS_ROWS[:7]):
    assert _SL[CLASS_SLOT[_i]] is None, "slot %d used twice" % CLASS_SLOT[_i]
''')
rep('''_SL = _SL + [tuple(_c) for _c in GATHER37_ROWS]
''', '''_SL = _SL + [tuple(_c) for _c in GATHER37_ROWS]
# 0.4.43 (Skyy 2026-10-15 "bug with the spell blade not loading right in the skills menu"): the Spellblade's Battlemagic = storage slot 19
assert len(_SL) == 19 and len(CLASS_ROWS) == 8 and CLASS_ROWS[7][0] == "Spellblade" and CLASS_SLOT[7] == 19
_SL = _SL + [("Combat." + CLASS_ROWS[7][0], CLASS_ROWS[7][1], CLASS_ROWS[7][2], CLASS_ROWS[7][3])]
''')
rep('''assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 19   # 0.4.37: + Fishing, Ranching, Orchard''',
    '''assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 20   # 0.4.37: + Fishing, Ranching, Orchard; 0.4.43: + Battlemagic''')
rep('''assert SLOT_NAMES[16:] == ["Fishing", "Ranching", "Orchard"] == SLOT_LABELS[16:]   # 0.4.37
''', '''assert SLOT_NAMES[16:19] == ["Fishing", "Ranching", "Orchard"] == SLOT_LABELS[16:19]   # 0.4.37
assert SLOT_NAMES[19:] == ["Combat.Spellblade"] and SLOT_LABELS[19:] == ["Battlemagic"]   # 0.4.43
''')
rep('''FUTURE_CLASSES = ["Spellblade"]   # 0.4.25: classes the tables accept before SkyyClasses has them (OverallCfg.TCLASSES)
''', '''FUTURE_CLASSES = []   # 0.4.25: classes the tables accept before SkyyClasses has them (OverallCfg.TCLASSES); 0.4.43: the Spellblade is a real class row now
''')
rep('''FUTURE_CLASSES = ["Spellblade"]
P25_MARK_ID''', '''FUTURE_CLASSES = []   # 0.4.43: the Spellblade is CLASS_ROWS[7] now (TCLASSES keeps the same order: the 7 classes, then Spellblade)
P25_MARK_ID''')
rep('''('Berserker', 'Weapon_Battleaxe_Crude:1'), ('Priest', 'Weapon_Wand_Wood:1')]
assert [_c for _c, _k in KIT_FALLBACK]''', '''('Berserker', 'Weapon_Battleaxe_Crude:1'), ('Priest', 'Weapon_Wand_Wood:1')]
KIT_FALLBACK += [('Spellblade', 'Weapon_Longsword_Crude:1')]   # 0.4.43: SkyyClasses 0.1.25's Spellblade kit
assert [_c for _c, _k in KIT_FALLBACK]''')
rep('''    if (v == null && s >= @PKG@.SkillDefs.FISHING) continue;   // 0.4.37: staged by 0.4.36 (no Fishing / Ranching / Orchard yet) - left as they are
''', '''    if (v == null && s >= @PKG@.SkillDefs.FISHING) continue;   // 0.4.37: staged by 0.4.36 (no Fishing / Ranching / Orchard yet) - left as they are; 0.4.43: + Battlemagic (slot 19)
''')

# ================================================================================================ the two new classes
rep('''ftask42 = pool.makeClass(PKG + ".FortTask")    # 0.4.42: the one-shot task that sends a player's Fortune group
''', '''ftask42 = pool.makeClass(PKG + ".FortTask")    # 0.4.42: the one-shot task that sends a player's Fortune group
hpr43 = pool.makeClass(PKG + ".HpRegen")       # 0.4.43: base Health regen for everyone (+ Overall Level, + the skill:fn:hpregen registry)
hprfn43 = pool.makeClass(PKG + ".HpRegenFn")   # 0.4.43: skill:fn:hpregen
even43 = pool.makeClass(PKG + ".XpEven")       # 0.4.43 (C): felled logs %, the Mining XP multiplier
''')

# ================================================================================================ the default xp.properties block
rep('''assert len(G42_KEYS) == len(set(G42_KEYS)) == 3
''', '''assert len(G42_KEYS) == len(set(G42_KEYS)) == 3
# 0.4.43 (tools/skills_0_4_43_patch.py): base Health regen; a missing key reads the same code default (no migration). HPR_* = the code
# defaults (J14 tokens) = the default file = the row defaults.
HPR_IN, HPR_OUT, HPR_SECS, HPR_PL_IN, HPR_PL_OUT = "0.2", "1", "5", "0.02", "0.05"
EVEN_FELL, EVEN_MINE = "70", "1.25"   # 0.4.43 (C): felled logs (not the chopped one) %, Mining XP multiplier
G43_L = ["# ---------- Health regen + Mining vs Foraging XP (SkyySkills 0.4.43) ----------",
         "# Comments must stay on their own lines.",
         "# Every player slowly gets Health back: hp.regen.inCombat HP a second in a fight, hp.regen.outOfCombat HP a second once",
         "# hp.regen.combatSeconds have passed since they last hit something or got hurt. Each Overall Level adds the perLevel numbers",
         "# (Overall Level 50 = 1.2 in combat, 3.5 out of combat). Gear, accessories, potions and food heal on top. Never above max Health,",
         "# never while dead. hp.regen.enabled false turns this regen off.",
         "hp.regen.enabled=true", "hp.regen.inCombat=" + HPR_IN, "hp.regen.outOfCombat=" + HPR_OUT, "hp.regen.combatSeconds=" + HPR_SECS,
         "hp.regen.perLevel.inCombat=" + HPR_PL_IN, "hp.regen.perLevel.outOfCombat=" + HPR_PL_OUT,
         "# MINING VS FORAGING (Skyy 2026-10-15: felled logs give a little less XP, Mining XP a bit more): the log you chop keeps its full",
         "# Foraging XP, every other log of a felled tree pays fell.otherLogsPercent percent of it (on top of fell.xpFactor; leaves keep",
         "# fell.leafXpFactor). mining.xpMultiplier multiplies the Mining XP of every mined block (XP only - drops and collections unchanged).",
         "# A fraction is paid by chance (1.25 XP = 1 or 2, 1.25 on average).",
         "fell.otherLogsPercent=" + EVEN_FELL, "mining.xpMultiplier=" + EVEN_MINE]
L.append("")
L.extend(G43_L)
G43_DEFAULTS = "\\n".join(G43_L) + "\\n"
assert all(ord(ch) < 128 for ch in G43_DEFAULTS) and '"' not in G43_DEFAULTS and "\\\\" not in G43_DEFAULTS and all(len(_ln) <= 140 for _ln in G43_L if _ln.startswith("#"))
assert not any(_cre.match(r"#\\s*[A-Za-z][A-Za-z0-9._-]*\\s*[=:]\\s*\\S+\\s*$", _ln) for _ln in G43_L), "a comment looks like a template line"
G43_KEYS = [_ln.split("=", 1)[0] for _ln in G43_L if not _ln.startswith("#")]
assert len(G43_KEYS) == len(set(G43_KEYS)) == 8
''')

# ================================================================================================ HpRegen part 1 (before SkillCfg.load, which calls read)
P1 = '''# ================= 0.4.43 HpRegen part 1: fields, the xp.properties read, the pure maths, the registry (compiled before SkillCfg.load and
# Acro.retainOnline, which call them). CLK = UUID -> float[]{seconds since the last pulse}; STATE = UUID -> double[]{1 = in combat, the
# rate of the last pulse}; FLAT / PCT = UUID -> ConcurrentHashMap source -> Double (skill:fn:hpregen; memory only, providers re-post like
# skill:fn:manaregen). Any thread except where it says so.
for _d43 in ("public static volatile boolean ON = true;", "public static volatile double IN = (double) @HPR_IN@;", "public static volatile double OUT = (double) @HPR_OUT@;",
             "public static volatile long COMBAT_MS = (long) ((double) @HPR_SECS@ * 1000.0);", "public static volatile double PL_IN = (double) @HPR_PL_IN@;",
             "public static volatile double PL_OUT = (double) @HPR_PL_OUT@;", "public static final float PULSE = 0.5f;", "public static final double MAX_RATE = 1000.0;",
             "public static final java.util.concurrent.ConcurrentHashMap CLK = new java.util.concurrent.ConcurrentHashMap();",
             "public static final java.util.concurrent.ConcurrentHashMap STATE = new java.util.concurrent.ConcurrentHashMap();",
             "public static final java.util.concurrent.ConcurrentHashMap FLAT = new java.util.concurrent.ConcurrentHashMap();",
             "public static final java.util.concurrent.ConcurrentHashMap PCT = new java.util.concurrent.ConcurrentHashMap();",
             "public static final java.util.concurrent.atomic.AtomicLong PULSES = new java.util.concurrent.atomic.AtomicLong();",
             "public static final java.util.concurrent.atomic.AtomicLong HEALED_MILLI = new java.util.concurrent.atomic.AtomicLong();",
             "public static volatile boolean FAILED_ONCE = false;"):
    hpr43.addField(CtField.make(J14(_d43), hpr43))
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static double clampD(double v, double d, double lo, double hi) {
  if (Double.isNaN(v) || Double.isInfinite(v)) return d;
  return v < lo ? lo : (v > hi ? hi : v);
}"""), hpr43))
# the six keys; a missing or bad number = the code default, clamped to the Server Setup row bounds (hand-edited files too)
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "hp.regen.enabled", true);
  IN = clampD(@PKG@.SkillCfg.dbl(p, "hp.regen.inCombat", (double) @HPR_IN@), (double) @HPR_IN@, 0.0, 100.0);
  OUT = clampD(@PKG@.SkillCfg.dbl(p, "hp.regen.outOfCombat", (double) @HPR_OUT@), (double) @HPR_OUT@, 0.0, 100.0);
  double cs = clampD(@PKG@.SkillCfg.dbl(p, "hp.regen.combatSeconds", (double) @HPR_SECS@), (double) @HPR_SECS@, 0.0, 60.0);
  COMBAT_MS = Math.round(cs * 1000.0);
  PL_IN = clampD(@PKG@.SkillCfg.dbl(p, "hp.regen.perLevel.inCombat", (double) @HPR_PL_IN@), (double) @HPR_PL_IN@, 0.0, 10.0);
  PL_OUT = clampD(@PKG@.SkillCfg.dbl(p, "hp.regen.perLevel.outOfCombat", (double) @HPR_PL_OUT@), (double) @HPR_PL_OUT@, 0.0, 10.0);
}"""), hpr43))
# THE rate (pure): HP a second = (base + level x per level + flat) x (1 + pct / 100); below 0 = 0, at most MAX_RATE; off = 0
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static double rate(boolean fight, int lvl, double flat, double pct) {
  if (!ON) return 0.0;
  double r = (fight ? IN : OUT) + (double) (lvl > 0 ? lvl : 0) * (fight ? PL_IN : PL_OUT);
  if (!Double.isNaN(flat) && !Double.isInfinite(flat)) r = r + flat;
  if (!(r > 0.0)) return 0.0;
  double p = (Double.isNaN(pct) || Double.isInfinite(pct)) ? 0.0 : (pct < -100.0 ? -100.0 : pct);
  r = r * (1.0 + p / 100.0);
  if (!(r > 0.0)) return 0.0;
  return r > MAX_RATE ? MAX_RATE : r;
}"""), hpr43))
# HP to add this pulse (pure): rate x seconds, never past max (the room left), 0 when dead (DeathComponent or Health 0), at max or no pool
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static float amount(double rate, float secs, float cur, float max, boolean dead) {
  if (dead || !(rate > 0.0) || !(secs > 0.0f) || !(max > 0.0f) || !(cur > 0.0f) || !(cur < max)) return 0.0f;
  double a = rate * (double) secs;
  double room = (double) (max - cur);
  if (a > room) a = room;
  return a > 0.0 ? (float) a : 0.0f;
}"""), hpr43))
# ms from a world-clock stamp to now; -1 = no stamp (null / Instant.MIN = never), a stamp in the future, or unreadable (the Wardrobe gate's agoMs)
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static long agoMs(java.time.Instant then, java.time.Instant now) {
  if (then == null || now == null || then.equals(java.time.Instant.MIN)) return -1L;
  try {
    long ms = java.time.Duration.between(then, now).toMillis();
    return ms < 0L ? -1L : ms;
  } catch (Throwable t) { return -1L; }
}"""), hpr43))
# ms since the last fight = the newer of lastDamageTime (hurt) and lastCombatAction (hit or got hit); -1 = never
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static long sinceFight(java.time.Instant dmg, java.time.Instant act, java.time.Instant now) {
  long a = agoMs(dmg, now);
  long b = agoMs(act, now);
  if (a < 0L) return b;
  if (b < 0L) return a;
  return a < b ? a : b;
}"""), hpr43))
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static boolean fighting(long since, long win) {
  return since >= 0L && since < win;
}"""), hpr43))
# the sum of one registry for a player (NaN / infinite entries skipped)
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static double sum(java.util.concurrent.ConcurrentHashMap all, java.util.UUID u) {
  Object o = u == null ? null : all.get(u);
  if (!(o instanceof java.util.Map)) return 0.0;
  double s = 0.0;
  java.util.Iterator it = ((java.util.Map) o).values().iterator();
  while (it.hasNext()) {
    Object v = it.next();
    if (!(v instanceof Number)) continue;
    double x = ((Number) v).doubleValue();
    if (Double.isNaN(x) || Double.isInfinite(x)) continue;
    s = s + x;
  }
  return s;
}"""), hpr43))
# set (replace) one source in one registry; 0 removes; false = bad arguments (no player, source 1-64 characters, a finite number)
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static boolean put(java.util.concurrent.ConcurrentHashMap all, java.util.UUID u, String src, double v0, double lo, double hi) {
  if (u == null || src == null) return false;
  String s = src.trim();
  if (s.length() == 0 || s.length() > 64 || Double.isNaN(v0) || Double.isInfinite(v0)) return false;
  double v = v0 < lo ? lo : (v0 > hi ? hi : v0);
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) all.get(u);
  if (v == 0.0) {
    if (m != null) m.remove(s);
    return true;
  }
  if (m == null) {
    java.util.concurrent.ConcurrentHashMap nm = new java.util.concurrent.ConcurrentHashMap();
    Object o = all.putIfAbsent(u, nm);
    m = o == null ? nm : (java.util.concurrent.ConcurrentHashMap) o;
  }
  m.put(s, Double.valueOf(v));
  return true;
}"""), hpr43))
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static boolean remove(java.util.UUID u, String src) {
  if (u == null || src == null) return false;
  String s = src.trim();
  boolean had = false;
  Object a = FLAT.get(u);
  if (a instanceof java.util.Map && ((java.util.Map) a).remove(s) != null) had = true;
  Object b = PCT.get(u);
  if (b instanceof java.util.Map && ((java.util.Map) b).remove(s) != null) had = true;
  return had;
}"""), hpr43))
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static int clear(String src) {
  if (src == null) return 0;
  String s = src.trim();
  java.util.HashSet who = new java.util.HashSet();
  java.util.Iterator it = FLAT.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (e.getValue() instanceof java.util.Map && ((java.util.Map) e.getValue()).remove(s) != null) who.add(e.getKey());
  }
  it = PCT.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (e.getValue() instanceof java.util.Map && ((java.util.Map) e.getValue()).remove(s) != null) who.add(e.getKey());
  }
  return who.size();
}"""), hpr43))
# players who left: their clock + last state (the FLAT / PCT entries belong to the mods that registered them, like skill:fn:manaregen)
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static void retain(java.util.Set online) {
  CLK.keySet().retainAll(online);
  STATE.keySet().retainAll(online);
}"""), hpr43))
# ================= 0.4.43 (C) XpEven: Mining vs Foraging (Skyy 2026-10-15 "felled logs give a little less xp, and increase the mining xp a
# bit"). FELL_PCT = fell.otherLogsPercent (FellCredit: every felled log but the chopped one), MINE = mining.xpMultiplier (BreakTask: Mining
# XP of a mined block). pay(x, r) = the whole part + 1 when r < the fraction (r in [0, 1): ThreadLocalRandom in the game, fixed in the
# harness) - the average is exact, so 1 XP stone x 1.25 really pays 1.25 on average. Any thread, no I/O.
for _d43 in ("public static volatile double FELL_PCT = (double) @EVEN_FELL@;", "public static volatile double MINE = (double) @EVEN_MINE@;",
             "public static final java.util.concurrent.atomic.AtomicLong MINED = new java.util.concurrent.atomic.AtomicLong();",
             "public static final java.util.concurrent.atomic.AtomicLong FELLED = new java.util.concurrent.atomic.AtomicLong();"):
    even43.addField(CtField.make(J14(_d43), even43))
even43.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  FELL_PCT = @PKG@.HpRegen.clampD(@PKG@.SkillCfg.dbl(p, "fell.otherLogsPercent", (double) @EVEN_FELL@), (double) @EVEN_FELL@, 0.0, 500.0);
  MINE = @PKG@.HpRegen.clampD(@PKG@.SkillCfg.dbl(p, "mining.xpMultiplier", (double) @EVEN_MINE@), (double) @EVEN_MINE@, 0.0, 10.0);
}"""), even43))
even43.addMethod(CtNewMethod.make(J14(r"""
public static long pay(double x, double r) {
  if (!(x > 0.0) || Double.isInfinite(x)) return 0L;
  double w = Math.floor(x);
  return (long) w + (r < x - w ? 1L : 0L);
}"""), even43))
even43.addMethod(CtNewMethod.make(J14(r"""
public static long mine(long xp) {
  if (xp <= 0L) return xp;
  MINED.incrementAndGet();
  return pay((double) xp * MINE, java.util.concurrent.ThreadLocalRandom.current().nextDouble());
}"""), even43))
even43.addMethod(CtNewMethod.make(J14(r"""
public static long fellLog(double xp) {
  if (!(xp > 0.0)) return 0L;
  FELLED.incrementAndGet();
  return pay(xp * FELL_PCT / 100.0, java.util.concurrent.ThreadLocalRandom.current().nextDouble());
}"""), even43))
even43.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  return "felled logs " + ((double) Math.round(FELL_PCT * 100.0) / 100.0) + "% (the chopped log 100%), Mining XP x" + ((double) Math.round(MINE * 100.0) / 100.0);
}"""), even43))
'''
rep('''# ================= 0.4.39 SkSnd part 1 + RbStat part 1: fields, the xp.properties read, the pure helpers, the Server Setup check= hook
''', P1 + '''# ================= 0.4.39 SkSnd part 1 + RbStat part 1: fields, the xp.properties read, the pure helpers, the Server Setup check= hook
''')
rep('''    {PKG}.RbStat.read(p);       // 0.4.39: rebirth stat boosts (rebirth.stats)
''', '''    {PKG}.RbStat.read(p);       // 0.4.39: rebirth stat boosts (rebirth.stats)
    {PKG}.HpRegen.read(p);      // 0.4.43: base Health regen (hp.regen.*)
    {PKG}.XpEven.read(p);       // 0.4.43: fell.otherLogsPercent, mining.xpMultiplier
''')

# ================================================================================================ HpRegen part 2 + HpRegenFn (before AcroSys + the plugin)
P2 = '''# ================= 0.4.43 HpRegen part 2: the Overall Level, the world-thread pulse, the texts (Server Setup action, SkyyMenu's Stats row)
# the Overall Level Perks.ovl publishes every second (skill:overall:<uuid>, memory only); 0 = none yet
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static int level(java.util.UUID u) {
  try {
    if (u == null) return 0;
    Object o = @PKG@.SkillStore.bridge().get("skill:overall:" + u.toString());
    return o instanceof Number ? ((Number) o).intValue() : 0;
  } catch (Throwable t) { return 0; }
}"""), hpr43))
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static double rateFor(java.util.UUID u, boolean fight) {
  return rate(fight, level(u), sum(FLAT, u), sum(PCT, u));
}"""), hpr43))
# world thread, every tick from AcroSys (after ManaRegen.tick): one pulse per PULSE seconds, at most 1 s at a time. The combat state from
# the player's DamageDataComponent on this world's clock, the rate, then the Health stat (never dead, never above max). Own try.
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static void tick(java.util.UUID u, @ST@ store, @CB@ cb, @REF@ ref, float dt) {
  try {
    if (u == null) return;
    float[] c = (float[]) CLK.get(u);
    if (c == null) { c = new float[] { 0.0f }; CLK.put(u, c); }
    c[0] = c[0] + dt;
    if (c[0] < PULSE) return;
    float secs = c[0];
    c[0] = 0.0f;
    if (secs > 1.0f) secs = 1.0f;
    if (!ON) { STATE.remove(u); return; }
    @TMR@ tr = (@TMR@) store.getResource(@TMR@.getResourceType());
    java.time.Instant now = tr == null ? null : tr.getNow();
    boolean fight = false;
    @DDC@ dd = (@DDC@) cb.getComponent(ref, @DDC@.getComponentType());
    if (dd != null && now != null) fight = fighting(sinceFight(dd.getLastDamageTime(), dd.getLastCombatAction(), now), COMBAT_MS);
    double r = rateFor(u, fight);
    @ESM@ m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
    int hi = @DST@.getHealth();
    @ESV@ v = (m != null && hi >= 0) ? m.get(hi) : null;
    boolean dead = false;
    try { dead = cb.getComponent(ref, @DTH@.getComponentType()) != null; } catch (Throwable t) { dead = false; }
    float a = v == null ? 0.0f : amount(r, secs, v.get(), v.getMax(), dead);
    STATE.put(u, new double[] { fight ? 1.0 : 0.0, a > 0.0f ? r : 0.0 });
    PULSES.incrementAndGet();
    if (a > 0.0f) {
      m.addStatValue(hi, a);
      HEALED_MILLI.addAndGet(Math.round((double) a * 1000.0));
    }
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("Health regen failed (logged once): " + t); }
  }
}"""), hpr43))
# 2 decimals at most ("1.2", "0.05", "3")
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static String n2(double v) {
  return @PKG@.Overall.num((double) Math.round(v * 100.0) / 100.0);
}"""), hpr43))
# "gear=+2/s", "trees=+20%" for every bridge source of this player, sorted by source (flat first when a source has both)
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static String[] sources(java.util.UUID u) {
  java.util.TreeMap t = new java.util.TreeMap();
  Object a = u == null ? null : FLAT.get(u);
  if (a instanceof java.util.Map) {
    java.util.Iterator it = ((java.util.Map) a).entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      if (!(e.getValue() instanceof Number)) continue;
      double x = ((Number) e.getValue()).doubleValue();
      t.put(e.getKey() + " 1", e.getKey() + "=" + (x >= 0.0 ? "+" : "") + n2(x) + "/s");
    }
  }
  Object b = u == null ? null : PCT.get(u);
  if (b instanceof java.util.Map) {
    java.util.Iterator it = ((java.util.Map) b).entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      if (!(e.getValue() instanceof Number)) continue;
      double x = ((Number) e.getValue()).doubleValue();
      t.put(e.getKey() + " 2", e.getKey() + "=" + (x >= 0.0 ? "+" : "") + n2(x) + "%");
    }
  }
  String[] r = new String[t.size()];
  java.util.Iterator it = t.values().iterator();
  int i = 0;
  while (it.hasNext() && i < r.length) { r[i] = (String) it.next(); i++; }
  return r;
}"""), hpr43))
# the ready line / reload summary
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  if (!ON) return "off";
  return n2(IN) + "/s in combat, " + n2(OUT) + "/s " + n2((double) COMBAT_MS / 1000.0) + " s after a fight, +" + n2(PL_IN) + " / +" + n2(PL_OUT) + " per Overall Level";
}"""), hpr43))
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static String stats() {
  return PULSES.get() + " pulses, " + n2((double) HEALED_MILLI.get() / 1000.0) + " HP healed, " + STATE.size() + " players";
}"""), hpr43))
# SkyyMenu's Character > Stats row (pure on memory, any thread): {value, detail}; detail at most 60 characters (the Stats page's line
# rule: name + value + detail + 2 under 80) - the in-combat rate, the Overall Level part, then as many bridge sources as fit, "+N more"
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static String[] row(java.util.UUID u) {
  if (!ON) return new String[] { "-", "off in Server Setup" };
  int lv = level(u);
  String head = n2(rateFor(u, true)) + "/s in combat";
  if (lv > 0 && PL_OUT > 0.0) head = head + "; Overall Lv " + lv + " +" + n2((double) lv * PL_OUT);
  String[] src = sources(u);
  StringBuilder sb = new StringBuilder(head);
  int shown = 0;
  for (int i = 0; i < src.length; i++) {
    String x = String.valueOf(src[i]).replace('=', ' ');
    int more = src.length - i - 1;
    int tail = more > 0 ? 9 : 0;
    if (sb.length() + 2 + x.length() + tail > 60) break;
    sb.append(shown == 0 ? "; " : ", ").append(x);
    shown++;
  }
  if (shown < src.length) {
    String m = (shown == 0 ? "; +" : ", +") + (src.length - shown) + " more";
    if (sb.length() + m.length() <= 60) sb.append(m);
  }
  String d = sb.toString();
  if (d.length() > 60) d = d.substring(0, 57) + "...";
  return new String[] { n2(rateFor(u, false)) + "/s", d };
}"""), hpr43))
# Server Setup -> Skills -> Overall and Mana -> "Health Regen: show mine" (one status line, at most 120 characters)
hpr43.addMethod(CtNewMethod.make(J14(r"""
public static Object[] showAction(java.util.UUID who, String name) {
  String t;
  if (!ON) t = "Health regen is off (Health regen for everyone).";
  else {
    int lv = level(who);
    String[] src = sources(who);
    StringBuilder sb = new StringBuilder();
    sb.append("Health Regen ").append(n2(rateFor(who, false))).append("/s, in combat ").append(n2(rateFor(who, true))).append("/s (Overall Level ").append(lv).append(")");
    if (src.length == 0) sb.append(", no other sources");
    else {
      sb.append(", ");
      for (int i = 0; i < src.length; i++) {
        if (i > 0) sb.append(", ");
        sb.append(src[i]);
      }
    }
    t = sb.toString() + ".";
  }
  if (who == null) t = "In game: your own. " + t;
  if (t.length() > 120) t = t.substring(0, 117) + "...";
  return new Object[] { "ok", "", t };
}"""), hpr43))
# ================= skill:fn:hpregen (0.4.43): the Health regen registry + read-outs for other mods - java.lang types only, never throws,
# any thread, memory only (the ops are listed in the 0.4.43 notes at the top of this script)
hprfn43.addInterface(pool.get("java.util.function.Function"))
hprfn43.addConstructor(CtNewConstructor.make("public HpRegenFn() { }", hprfn43))
hprfn43.addMethod(CtNewMethod.make(J14(r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 2 || !(a[0] instanceof String)) return null;
    String op = ((String) a[0]).trim().toLowerCase();
    if (op.equals("clear")) {
      if (!(a[1] instanceof String)) return Integer.valueOf(0);
      return Integer.valueOf(@PKG@.HpRegen.clear((String) a[1]));
    }
    java.util.UUID u = null;
    if (a[1] instanceof java.util.UUID) u = (java.util.UUID) a[1];
    if (op.equals("get")) return new Double[] { Double.valueOf(@PKG@.HpRegen.rateFor(u, true)), Double.valueOf(@PKG@.HpRegen.rateFor(u, false)) };
    if (op.equals("now")) {
      Object o = u == null ? null : @PKG@.HpRegen.STATE.get(u);
      return Double.valueOf(o instanceof double[] ? ((double[]) o)[1] : 0.0);
    }
    if (op.equals("fight")) {
      Object o = u == null ? null : @PKG@.HpRegen.STATE.get(u);
      return Boolean.valueOf(o instanceof double[] && ((double[]) o)[0] > 0.0);
    }
    if (op.equals("sources")) return @PKG@.HpRegen.sources(u);
    if (op.equals("row")) return @PKG@.HpRegen.row(u);
    if (op.equals("add") || op.equals("addpct")) {
      if (u == null || a.length < 4 || !(a[2] instanceof String) || !(a[3] instanceof Number)) return Boolean.FALSE;
      boolean pct = op.equals("addpct");
      return Boolean.valueOf(@PKG@.HpRegen.put(pct ? @PKG@.HpRegen.PCT : @PKG@.HpRegen.FLAT, u, (String) a[2], ((Number) a[3]).doubleValue(), pct ? -100.0 : -100.0, pct ? 1000.0 : 100.0));
    }
    if (op.equals("remove")) {
      if (u == null || a.length < 3 || !(a[2] instanceof String)) return Boolean.FALSE;
      return Boolean.valueOf(@PKG@.HpRegen.remove(u, (String) a[2]));
    }
    return null;
  } catch (Throwable t) { return null; }
}"""), hprfn43))

'''
rep('''# ================= skill:fn:manaregen (0.4.12): the Mana Regen % registry for other mods - java.lang types only, never throws, any thread
''', P2 + '''# ================= skill:fn:manaregen (0.4.12): the Mana Regen % registry for other mods - java.lang types only, never throws, any thread
''')

# ================================================================================================ wiring: the pulse, retain, bridge, shutdown
rep('''    {PKG}.ManaRegen.tick(u, store, cb, ref, dt);   // 0.4.12: Mana regen in combat (own PULSE clock, own try; first, so no call below can skip it)
''', '''    {PKG}.ManaRegen.tick(u, store, cb, ref, dt);   // 0.4.12: Mana regen in combat (own PULSE clock, own try; first, so no call below can skip it)
    {PKG}.HpRegen.tick(u, store, cb, ref, dt);     // 0.4.43: base Health regen (own 0.5 s clock, own try)
''')
rep('''    {PKG}.ManaRegen.BLOCK.keySet().retainAll(online);   // 0.4.30: the regen blocks of players who left
''', '''    {PKG}.ManaRegen.BLOCK.keySet().retainAll(online);   // 0.4.30: the regen blocks of players who left
    {PKG}.HpRegen.retain(online);   // 0.4.43: the Health regen clocks + last states
''')
rep('''  {PKG}.SkillStore.bridge().put("skill:fn:regenblock", new {PKG}.RegenBlockFn());   // 0.4.30: SkyyArmory's Soul Bindings block natural Mana regen
''', '''  {PKG}.SkillStore.bridge().put("skill:fn:regenblock", new {PKG}.RegenBlockFn());   // 0.4.30: SkyyArmory's Soul Bindings block natural Mana regen
  {PKG}.SkillStore.bridge().put("skill:fn:hpregen", new {PKG}.HpRegenFn());   // 0.4.43: the Health regen registry + read-outs
''')
rep('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:regenblock"); }} catch (Throwable t) {{ }}   // 0.4.30
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:regenblock"); }} catch (Throwable t) {{ }}   // 0.4.30
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:hpregen"); }} catch (Throwable t) {{ }}   // 0.4.43
''')

# ================================================================================================ Server Setup rows
rep('''     "On: an Overall level up also heals the max Health it added (players have no Health regen).", "reload"),''',
    '''     "On: an Overall level up also heals the max Health it added at once (regen is slow).", "reload"),''')
rep('''     "A small sparkle at the block when Fortune gives extra drops. Only that player sees it.", "reload"),
]''', '''     "A small sparkle at the block when Fortune gives extra drops. Only that player sees it.", "reload"),
    # 0.4.43: base Health regen - G43_KEYS order, then its show action
    ("hp.regen.enabled", "Health regen for everyone", "overall", "bool", "true", "", "", "", "", "live",
     "Off: no SkyySkills Health regen. Food, potions, gear and accessories still heal.", "reload"),
    ("hp.regen.inCombat", "Health regen in combat", "overall", "dec", HPR_IN, "0", "100", "", "", "live",
     "HP a second while fighting (you hit something or got hurt a moment ago).", "reload"),
    ("hp.regen.outOfCombat", "Health regen out of combat", "overall", "dec", HPR_OUT, "0", "100", "", "", "live",
     "HP a second once the fight is over (see the next row).", "reload"),
    ("hp.regen.combatSeconds", "Out of combat after", "overall", "dec", HPR_SECS, "0", "60", "", "s", "live",
     "Seconds after your last hit or damage until the faster regen starts.", "reload"),
    ("hp.regen.perLevel.inCombat", "Regen per Overall Level (in combat)", "overall", "dec", HPR_PL_IN, "0", "10", "", "", "live",
     "Extra HP a second in combat per Overall Level. 0.02 = +1 at level 50.", "reload"),
    ("hp.regen.perLevel.outOfCombat", "Regen per Overall Level", "overall", "dec", HPR_PL_OUT, "0", "10", "", "", "live",
     "Extra HP a second out of combat per Overall Level. 0.05 = +2.5 at level 50.", "reload"),
    # 0.4.43 (C): Mining vs Foraging (new rows - fell.xpFactor keeps its 1.0 default, no migration)
    ("fell.otherLogsPercent", "Other felled logs XP", "gathering", "dec", EVEN_FELL, "0", "500", "", "%", "live",
     "Foraging XP of every felled log but the one you chop, in % (after Felled log XP).", "reload"),
    ("mining.xpMultiplier", "Mining XP multiplier", "gathering", "dec", EVEN_MINE, "0", "10", "", "x", "live",
     "Mining XP of every mined block x this (drops and collections unchanged).", "reload"),
    ("hp.regen.show", "Health Regen: show mine", "overall", "action", "", "", "", "Show my Health Regen", "", "live",
     "Your Health regen in and out of combat and what adds to it.", "action:HpRegen.showAction"),
]''')
rep('''assert [_r[0] for _r in CFG_ROWS][-22:-11] == G37_KEYS   # 0.4.39: the 8 G39 rows follow; 0.4.42: then the 3 G42 rows''',
    '''assert [_r[0] for _r in CFG_ROWS][-31:-20] == G37_KEYS   # 0.4.39: the 8 G39 rows follow; 0.4.42: then the 3 G42 rows; 0.4.43: then 8 G43 + 1 action''')
rep('''assert [_r[0] for _r in CFG_ROWS][-11:-3] == G39_KEYS
''', '''assert [_r[0] for _r in CFG_ROWS][-20:-12] == G39_KEYS
''')
rep('''assert [_r[0] for _r in CFG_ROWS][-3:] == G42_KEYS
''', '''assert [_r[0] for _r in CFG_ROWS][-12:-9] == G42_KEYS
for _k43 in G43_KEYS:   # 0.4.43: every new key a row once, row default = the default file (= the code default)
    _r43 = [_r for _r in CFG_ROWS if _r[0] == _k43]
    assert len(_r43) == 1 and _dp.get(_k43) is not None and ("\\n" + _k43 + "=" + _dp[_k43] + "\\n") in ("\\n" + G43_DEFAULTS), _k43
    assert _r43[0][2] == ("gathering" if _k43 in ("fell.otherLogsPercent", "mining.xpMultiplier") else "overall") and (_r43[0][3] == "bool" or _Dec(_r43[0][4]) == _Dec(_dp[_k43])), _k43
assert [_r[0] for _r in CFG_ROWS][-9:] == G43_KEYS + ["hp.regen.show"]
''')
rep('''assert len(CFG_ROWS) == 252, ("0.4.42: + 3 rows''', '''assert len(CFG_ROWS) == 261, ("0.4.43: + 9 rows (6 hp.regen.*, fell.otherLogsPercent, mining.xpMultiplier, the hp.regen.show action); 0.4.42: + 3 rows''')
rep('''"\\n" + G39_DEFAULTS + "\\n" + G42_DEFAULTS)   # 0.4.42: + G42''', '''"\\n" + G39_DEFAULTS + "\\n" + G42_DEFAULTS + "\\n" + G43_DEFAULTS)   # 0.4.43: + G43; 0.4.42: + G42''')

# ================================================================================================ the ready line + the jar's class list
rep('''"; rebirth stats " + {PKG}.RbStat.text() + "''', '''"; Health regen " + {PKG}.HpRegen.text() + " (bridge skill:fn:hpregen)" + "; Mining vs Foraging: " + {PKG}.XpEven.text() + "; rebirth stats " + {PKG}.RbStat.text() + "''')
rep('''          hubb, hopen, fort42, ftask42):   # 0.4.42: + Fortune, FortTask;''', '''          hubb, hopen, fort42, ftask42, hpr43, hprfn43, even43):   # 0.4.43: + HpRegen, HpRegenFn, XpEven; 0.4.42: + Fortune, FortTask;''')

# ================================================================================================ (C) wiring: Mining XP in BreakTask, felled logs in FellCredit
rep('''    if ((int) this.rule[0] == {PKG}.SkillDefs.FARMING) bamt = {PKG}.FarmTier.breakXp(this.u, this.ev, bamt);   // 0.4.35: half XP one tier up
''', '''    if ((int) this.rule[0] == {PKG}.SkillDefs.FARMING) bamt = {PKG}.FarmTier.breakXp(this.u, this.ev, bamt);   // 0.4.35: half XP one tier up
    if ((int) this.rule[0] == {PKG}.SkillDefs.MINING) bamt = {PKG}.XpEven.mine(bamt);   // 0.4.43: mining.xpMultiplier (XP only)
''')
rep('''      long xp = Math.round((double) rule[1] * fct);
''', '''      long xp = W.leaf[i] ? Math.round((double) rule[1] * fct) : {PKG}.XpEven.fellLog((double) rule[1] * fct);   // 0.4.43: other logs x fell.otherLogsPercent
''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "command / system registrations changed"
_i = s.index
assert _i("public static void read(java.util.Properties p) {\n  ON = @PKG@.SkillCfg.bool(p, \"hp.regen.enabled\"") < _i("{PKG}.HpRegen.read(p);")
assert _i("public static void retain(java.util.Set online) {\n  CLK.keySet()") < _i("{PKG}.HpRegen.retain(online);")
assert _i("public static void tick(java.util.UUID u, @ST@ store") < _i("{PKG}.HpRegen.tick(u, store, cb, ref, dt);")
assert _i("public static String text() {\n  if (!ON) return \"off\";\n  return n2(IN)") < _i("{PKG}.HpRegen.text() + \" (bridge skill:fn:hpregen)\"")
assert _i("hprfn43.addConstructor") < _i("new {PKG}.HpRegenFn()")
assert _i("public static Object[] showAction(java.util.UUID who, String name) {\n  String t;") < _i('"action:HpRegen.showAction"')
assert s.count("{PKG}.HpRegen.tick(") == 1 and s.count("m.addStatValue(hi, a);") == 1
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.4.42 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", dst, "(%d lines; 0.4.42 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
