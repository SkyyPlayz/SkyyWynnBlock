"""Derive SkyySkills/build_skyyskills_0.4.4.py from 0.4.3 (same style as skills_0_4_3_patch.py: rep(old, new) with asserted single anchors,
newline-agnostic; 0.4.3 stays untouched, its line endings are preserved). Edit THIS file, not the generated script.
0.4.4 = Berserker + Priest (research/Classes-Berserker-Priest-Spec.md section 3, the only spec; Skyy's decisions 2026-09-25,
SkyWynn-Decisions.md change notes 1-2):
 - SLOTS 14 Fury (Combat.Berserker) and 15 Divinity (Combat.Priest) APPENDED after Exploration (N = 16; slots 0-13 keep index + key).
 - CLASS SLOT TABLE: SkillDefs.CLASS0 / CLASS_END removed, SkillDefs.CLASS_SLOT = {5,6,7,8,9,14,15} + isClass / classIdx / classSlot;
   the 11 sites of spec 3.2 switched (indexOf x2, slotOfClass, skillName, weaponOk, killSlot, levelsOf, moveLegacy, Perks.tick,
   StatsPage lines / how / build). The Shaman placeholder icon becomes Weapon_Deployable_Slowness_Totem.
 - DIVINITY XP FROM HEALING (spec 3.4): bridge skill:fn:healxp (SkillHealFn -> HealXp.offer -> BridgeXp.offer on slot 15), own 60 s
   cap ring (HealXp.HWIN), DivCfg (divinity.* keys, appended once to an existing xp.properties), 3 Server Setup rows (spec 3.5).
 - PAGES (spec 3.6): the Stats page's Divinity "Boosts right now" heal line; how(Combat) and every skill-list text name Fury / Divinity.
Run:  python tools/skills_0_4_4_patch.py   then   python SkyySkills/build_skyyskills_0.4.4.py   (NO --deploy: coordinated deploy)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.3.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.4.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.3"
s = raw.decode("utf8").replace("\r\n", "\n")
REG0 = s.count("registerSystem(")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:100]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:100])
    s = s.replace(old, new)


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


# ================================================================ header / version
rep('''"""SkyySkills 0.4.3 - build script (derived from 0.4.2 by tools/skills_0_4_3_patch.py - edit the patch, not this file;
0.4.2 was derived from 0.4.1 by tools/skills_0_4_2_patch.py, 0.4.1 from 0.4 by tools/skills_0_4_1_patch.py, 0.4 from 0.3.2 by
tools/skills_0_4_patch.py, 0.3.2 from 0.3.1 by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.3 (research/Server-Setup-Spec.md''', '''"""SkyySkills 0.4.4 - build script (derived from 0.4.3 by tools/skills_0_4_4_patch.py - edit the patch, not this file;
0.4.3 was derived from 0.4.2 by tools/skills_0_4_3_patch.py, 0.4.2 from 0.4.1 by tools/skills_0_4_2_patch.py, 0.4.1 from 0.4 by
tools/skills_0_4_1_patch.py, 0.4 from 0.3.2 by tools/skills_0_4_patch.py, 0.3.2 from 0.3.1 by tools/skills_0_3_2_patch.py, 0.3 from 0.2
by tools/skills_0_3_patch.py)
0.4.4 (research/Classes-Berserker-Priest-Spec.md section 3 - BERSERKER + PRIEST; Skyy's decisions 2026-09-25, SkyWynn-Decisions.md change
  notes 1-2). Pairs with SkyyClasses 0.1.6 (class:list + class:weapons:Berserker|Priest, and the placeholder Priest heal that calls
  skill:fn:healxp) and SkyyProfiles 0.1.2; every mix loads and is safe (spec 5): with SkyyClasses 0.1.5 the two new slots simply stay
  empty and skill:fn:healxp is never called. NEVER DOWNGRADE to 0.4.3 once 0.4.4 has saved Fury or Divinity XP: 0.4.3's snap() drops the
  two unknown keys on its next save.
  SLOTS 14 Fury (key Combat.Berserker, icon Weapon_Battleaxe_Iron, #d9443f) and 15 Divinity (key Combat.Priest, icon Weapon_Wand_Wood,
    #f2e6a0), APPENDED after Exploration: N = 16, slots 0-13 keep their index and key (build-asserted against the 0.4.3 list), player
    files gain Combat.Berserker / Combat.Priest (+ .paid) on the next save (0 for everyone). An old Combat.Berserker line from the 0.3
    spike would become Fury XP (only a file untouched since 0.3 can still hold one - accepted, spec 3.1). The Shaman placeholder row's
    icon is Weapon_Deployable_Slowness_Totem (the wand belongs to the Priest now).
  CLASS SLOT TABLE (spec 3.2): class slots are no longer contiguous, so the SkillDefs fields CLASS0 / CLASS_END are GONE (nothing may do slot
    arithmetic any more; javassist would refuse a leftover reference) and SkillDefs.CLASS_SLOT = {5, 6, 7, 8, 9, 14, 15} follows the order
    of SkillDefs.CLASSES = Archer, Warrior, Assassin, Shaman, Mage, Berserker, Priest (FURY = 14, DIVINITY = 15), with isClass / classIdx /
    classSlot. The 11 sites use them: indexOf (exact and 3+ letter class names), SkillClass.slotOfClass, skillName, weaponOk, the killSlot
    hint, SkillStore.levelsOf (skill:<uuid>), moveLegacy (the legacy Combat move needs ALL seven class slots at 0), Perks.tick (as 0.4.3
    was, a Berserker = slot 14 threw ArrayIndexOutOfBounds inside the try: no health / stamina / mana perks, no republish), StatsPage
    lines / how / build. Everything class-based then follows class:<uuid> as for Archery: kills (KillSys -> killSlot -> weaponOk with
    class:weapons:Berserker|Priest from SkyyClasses 0.1.6; a wand-orb kill is judged by the main hand at death, the staff rule), the
    party share (PartyXp pays THEIR class slot), the combat perk row (health per class level, perk.combat.damagePerLevel), skill:<uuid>
    ("Fury:3", "Divinity:7"), skill:fn:level / skill:fn:xp ("Fury", "Divinity", "Berserker", "Priest", "Combat.Berserker",
    "Combat.Priest"; prefixes fur / div / ber / pri), /skills top | stats | xp. No per-skill rows: combat.* and perk.combat.* already apply
    to every class skill.
  DIVINITY XP FROM HEALING (spec 3.4): bridge skill:fn:healxp = Function apply(Object[]{UUID healer, Number hpHealedOnOthers, String
    source [, String expectKey]}) -> Boolean (SkillHealFn -> HealXp.offer; put in setup, removed in shutdown with the other functions).
    Only SkyyClasses 0.1.6 calls it (source "classes:heal", right after its placeholder Priest heal; self-heals are never sent). FALSE =
    refused: divinity.healXp.enabled off (or healXpPerHp 0), hp not a positive finite number, the healer's class skill is not Divinity
    (SkillClass.slot != 15), their class still follows a profile switch (SkillClass.consistent), the per-minute cap is used up, or
    BridgeXp.offer refuses (offline, profile key differs from expectKey, bridge.maxXpPerCall / maxXpPerMinute). XP = hp x
    divinity.healXpPerHp (0.2: a healed point is worth a damaged point, combat XP = monster max health x 0.2), the fraction paid by
    chance; 0 XP -> TRUE (nothing to pay). Cap: HealXp.HWIN, a 60 s window per player, divinity.healXpMaxPerMinute (300, 0 = no limit),
    counted in heal XP BEFORE the xp multiplier (the same with the default multiplier 1), not reset by a profile switch (the
    BridgeXp.WIN rule); ALL OR NOTHING (spec 3.4 "over the cap -> FALSE", the BridgeXp.allow rule): a grant that would cross it is
    refused whole = FALSE (nothing recorded; a later, smaller heal may still fit) + at most one WARN per player per minute
    (HealXp.warnLimited). Then BridgeXp.offer(u, 15, xp, source, expectKey, null, 0, false) queues a BridgeTask on the player's world
    thread (profile key + creative re-checked there), applies the xp multiplier like a kill, counts toward bridge.maxXpPerMinute and
    prints the normal "+2 Divinity XP" line (skills.xpGain); a refused offer gives its share of the cap back. A task the world thread
    drops later (creative - SkyyClasses' HealTask already skips creative Priests, spec 2.4 -, logged off or profile switched in between)
    keeps its share until the 60 s window ends: it fails closed (no XP is ever paid that way, the healer's own budget is only smaller for
    the rest of that minute), the same as BridgeXp.WIN for skill:fn:addxp / craftxp; the game mode is not read here because this
    function runs on any thread (components only on the world thread). Never throws, no file I/O, any thread.
  CONFIG (spec 3.5): 3 rows, 154 in total - divinity.healXp.enabled (parts, live,part,danger), divinity.healXpPerHp (combat, dec 0-100),
    divinity.healXpMaxPerMinute (combat, int 0-1000000000); reload: binding like every row. The "Divinity" block is in a fresh
    xp.properties and appended ONCE to an existing file without divinity.healXp.enabled (DivCfg.ensureDefaults, the PartyCfg pattern,
    inside SkillCfg.load = before CfgPub.start); the code defaults are the same numbers; the loader clamps to the row bounds.
  PAGES (spec 3.6): /skills is unchanged (the class row already shows the ACTIVE class's skill: a Berserker sees Fury with the battleaxe,
    a Priest Divinity with the wand; still 9 rows, 640 x 690). Stats page: Fury / Divinity show level, bar, class perks ("+X% damage with
    Berserker weapons (against monsters)"), next level, how-to "Earn XP by defeating monsters with Priest weapons - Spellbook / Wand" + the
    party text; for Divinity one more "Boosts right now" line: "Healing party members pays 0.2 Divinity XP per HP (up to 300 a minute)",
    or "Divinity XP from healing is off on this server" (a line, not the how-to: the how-to label is 45 px high).
  TEXTS: the unknown-skill message, the /skills stats | top | xp skill helps, the /skills xp no-class line, how(Combat) ("... / Berserker
    Fury / Priest Divinity (Assassin and Shaman later)"), the xp.properties load summary, the ready line and the manifest description.
  CHECKED in a bare JVM (2026-09-25, scratch harness under tools/dev/scratch/r6-skyyskills, deleted afterwards; 175 checks): all 83
    classes load + initialise under -Xverify:all; N = 16, slots 0-13 keep their keys, NAMES / LABELS / ICONS / COLORS of 14 / 15, the
    Shaman icon, CLASSES order, CLASS_SLOT / FURY / DIVINITY, isClass / classIdx / classSlot over -1..17, perkRow 14 / 15 = the combat
    row; indexOf (fury, divinity, berserker, priest, fur / div / ber / pri, Combat.Berserker / Combat.Priest, the old names, unknown =
    -1); a hand-written 0.4.3 player file loads with Fury / Divinity 0 (paid 0) and saves every old key + paid marker unchanged plus the
    two new keys; levelsOf for a Priest (Divinity with XP), a Berserker (Fury at 0 = the current class) and an Archer; moveLegacy refuses
    while slot 14 or 15 has XP and for a non-class slot, then moves into Divinity; slotOfClass, skillName, weaponOk(slot 14) answers
    false without throwing, weaponsText; Perks.tick for a Berserker reaches LASTCLS + the republish (skill:<uuid> with Fury:0); Stats
    page how(14) / how(15) / how(Combat), the Divinity heal line (on, off, no cap), no heal line under "Level L+1 adds", the Berserker
    damage line; DivCfg: fresh file = DEFAULTS, a 0.4.3 file gets the block appended once at the end (a second load adds nothing),
    custom values + clamps (500 -> 100, -5 -> 0, abc -> 0.2, 5e9 -> 1e9), the load summary; HealXp.amount (exact, the fraction by chance:
    mean 0.2 over 20000 rolls, edges), take / give (partial pay up to the cap, used up, give back, new window, cap 0 = no limit;
    take is all or nothing since the 2026-09-25 review fix, see REVIEW FIXES);
    skill:fn:healxp gates (bad arguments, no class, Warrior, part off, rate 0, 0 XP -> TRUE, NaN / negative / infinite / 0 hp, class
    still following a profile switch, cap used up) and a refused offer (no Universe in a bare JVM) giving its cap share back; the kit:
    config:def 154 rows / 8 categories, the three Divinity rows (category, type, default, bounds, flags), get, typed values outside the
    bounds refused, part OFF asks / ON does not, the file lines change in place and the reload routine applies the new values.
  REVIEW FIXES (2026-09-25): the heal cap is ALL OR NOTHING (spec 3.4; take returns boolean, offer sends the whole base); a SkyyClasses
    0.1.6+ build script whose CLASSES roster cannot be parsed now FAILS the build (it matched the real 0.1.6 roster); /skills xp lists
    the same skills as stats / top. Re-checked in a bare JVM (-Xverify:all, 106 checks, scratch deleted): all classes load; take (fits,
    crossing refused with nothing recorded, exact fit, used up, new window, want > cap, cap 0, want 0), give; offer (no class, Warrior,
    over the cap = FALSE with nothing recorded, a refused offer gives the share back, bad hp, rate 0, 0 XP = TRUE, no cap, switch off),
    SkillHealFn, statsLine.
  UNVERIFIED (needs the game): a real Priest heal from SkyyClasses 0.1.6 through skill:fn:healxp -> BridgeXp.offer -> BridgeTask (TRUE,
    the "+N Divinity XP" line, the cap in practice); Fury / Divinity kill XP with real axes / maces / wands (class:weapons:* published by
    SkyyClasses 0.1.6; a wand-orb kill judged by the main hand at death); the party share into Fury / Divinity; the /skills class row
    (battleaxe / wand icon) and the Stats page note "You are not a Berserker right now" on a client; the three rows in SkyyMenu's Server
    Setup (Parts and Combat tabs).
  NOT HERE (other mods / later): the Priest heal itself, class kits and the Create Profile cards (SkyyClasses 0.1.6, SkyyProfiles
    0.1.2); SkyyGuilds' xpSkills default without Fury / Divinity (spec F1); Mana for Priests / Mages (spec Q6).
0.4.3 (research/Server-Setup-Spec.md''')
rep('''Run:   python build_skyyskills_0.4.3.py            -> SkyySkills/SkyySkills-0.4.3.jar
       python build_skyyskills_0.4.3.py --deploy   -> also copies''', '''Run:   python build_skyyskills_0.4.4.py            -> SkyySkills/SkyySkills-0.4.4.jar
       python build_skyyskills_0.4.4.py --deploy   -> also copies''')
rep('VERSION = "0.4.3"', 'VERSION = "0.4.4"')

# ================================================================ default xp.properties: the Divinity block (appended once, DivCfg)
after('''L.append("")
L.extend(PARTY_L)
PARTY_DEFAULTS = "\\n".join(PARTY_L) + "\\n"
assert all(ord(ch) < 128 for ch in PARTY_DEFAULTS) and '"' not in PARTY_DEFAULTS
PARTY_LIT = json.dumps(PARTY_DEFAULTS)
''', '''# 0.4.4: Divinity XP from Priest heals (research/Classes-Berserker-Priest-Spec.md 3.4 / 3.5). Appended once to a file without
# divinity.healXp.enabled (DivCfg.ensureDefaults).
DIV_L = []
DIV_L.append("# ---------- Divinity (SkyySkills 0.4.4) - Priest heals from SkyyClasses 0.1.6 (skill:fn:healxp) ----------")
DIV_L.append("# Comments must stay on their own lines.")
DIV_L.append("# A Priest (class skill Divinity) earns healXpPerHp Divinity XP for every 1 HP their weapon hits heal on OTHER party members")
DIV_L.append("# (healing themself pays nothing). healXpMaxPerMinute: most heal XP per Priest in one 60 second window, counted before the xp")
DIV_L.append("# multiplier (0 = no limit). Kills pay Divinity XP like every class skill (combat.* keys) and are not counted here.")
DIV_L.append("divinity.healXp.enabled=true")
DIV_L.append("divinity.healXpPerHp=0.2")
DIV_L.append("divinity.healXpMaxPerMinute=300")
L.append("")
L.extend(DIV_L)
DIV_DEFAULTS = "\\n".join(DIV_L) + "\\n"
assert all(ord(ch) < 128 for ch in DIV_DEFAULTS) and '"' not in DIV_DEFAULTS
DIV_LIT = json.dumps(DIV_DEFAULTS)
''')

# ================================================================ classes
after('''karm = pool.makeClass(PKG + ".SkillKitArm")
''', '''# 0.4.4: Divinity XP from Priest heals (research/Classes-Berserker-Priest-Spec.md 3.4): config, cap ring + offer, bridge Function
dvc  = pool.makeClass(PKG + ".DivCfg")
hxp  = pool.makeClass(PKG + ".HealXp")
hfn  = pool.makeClass(PKG + ".SkillHealFn")
''')

# ================================================================ SkillDefs: two appended class slots + the class slot table (spec 3.1 / 3.2)
rep('''CLASS_ROWS = [("Archer", "Archery", "Weapon_Shortbow_Iron", "#8fd67a"), ("Warrior", "Swordsmanship", "Weapon_Sword_Iron", "#e0b060"),
              ("Assassin", "Assassination", "Weapon_Daggers_Iron", "#b58cff"), ("Shaman", "Shaman skill", "Weapon_Wand_Wood", "#ff7a5c"),
              ("Mage", "Sorcery", "Weapon_Staff_Iron", "#7fb0e0")]
for _c in CLASS_ROWS: must(_c[2])
# 0.4: slots 10-12, 0.4.1: slot 13 Exploration = slots 10-13 (append-only; they are >= CLASS0 but NOT classes - class loops stop at
# CLASS_END = 10)
EXTRA_ROWS = [("Alchemy", "Alchemy", "Potion_Health", "#7fe0d0"), ("Smithing", "Smithing", "Ingredient_Bar_Iron", "#c0c8d0"),
              ("Cooking", "Cooking", "Food_Pie_Apple", "#ffb070"), ("Exploration", "Exploration", "Tool_Map", "#e0a040")]
for _c in EXTRA_ROWS: must(_c[2])
SLOT_NAMES = ["Mining", "Foraging", "Farming", "Combat", "Acrobatics"] + ["Combat." + c[0] for c in CLASS_ROWS] + [c[0] for c in EXTRA_ROWS]
SLOT_LABELS = ["Mining", "Foraging", "Farming", "Combat", "Acrobatics"] + [c[1] for c in CLASS_ROWS] + [c[1] for c in EXTRA_ROWS]
SLOT_ICONS = ICONS + [c[2] for c in CLASS_ROWS] + [c[2] for c in EXTRA_ROWS]
SLOT_COLORS = ["#8fc8ff", "#8fe08a", "#f0d060", "#ff8a7a", "#c8a0ff"] + [c[3] for c in CLASS_ROWS] + [c[3] for c in EXTRA_ROWS]
assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 14
assert SLOT_NAMES[10:] == ["Alchemy", "Smithing", "Cooking", "Exploration"] and SLOT_NAMES[5 + len(CLASS_ROWS) - 1] == "Combat.Mage"
''', '''# 0.4.4 (research/Classes-Berserker-Priest-Spec.md 3.1): Berserker / Fury and Priest / Divinity are APPENDED after Exploration = storage
# slots 14 and 15 (saved keys Combat.Berserker / Combat.Priest). The Shaman placeholder icon is the Slowness Totem (the wand is Priest's).
CLASS_ROWS = [("Archer", "Archery", "Weapon_Shortbow_Iron", "#8fd67a"), ("Warrior", "Swordsmanship", "Weapon_Sword_Iron", "#e0b060"),
              ("Assassin", "Assassination", "Weapon_Daggers_Iron", "#b58cff"),
              ("Shaman", "Shaman skill", "Weapon_Deployable_Slowness_Totem", "#ff7a5c"),
              ("Mage", "Sorcery", "Weapon_Staff_Iron", "#7fb0e0"),
              ("Berserker", "Fury", "Weapon_Battleaxe_Iron", "#d9443f"), ("Priest", "Divinity", "Weapon_Wand_Wood", "#f2e6a0")]
for _c in CLASS_ROWS: must(_c[2])
# 0.4.4 (spec 3.2): the storage slot of each CLASS_ROWS entry (same order = SkillDefs.CLASSES). Class slots are NOT contiguous any more
# (5-9, then 14-15 after the four extra rows): every class loop / index goes through SkillDefs.CLASS_SLOT / isClass / classIdx /
# classSlot - the SkillDefs fields CLASS0 / CLASS_END are gone, so no code can do slot arithmetic with them.
CLASS_SLOT = [5, 6, 7, 8, 9, 14, 15]
assert len(CLASS_SLOT) == len(CLASS_ROWS) and len(set(CLASS_SLOT)) == len(CLASS_SLOT)
# the class roster SkyyClasses 0.1.6 publishes (spec 2.1; display order there is different, names must match)
_ROSTER = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Shaman"]
assert sorted(c[0] for c in CLASS_ROWS) == sorted(_ROSTER), "CLASS_ROWS names != the SkyyClasses 0.1.6 roster"
def _classes_roster():
    """names in the newest SkyyClasses build script's CLASSES list (read only), or (version, None) when it cannot be parsed
    (for a 0.1.6+ script that fails the build below)"""
    import glob, re as _re
    best, path = None, None
    for f in glob.glob(os.path.join(HERE, "..", "SkyyClasses", "build_skyyclasses_*.py")):
        m = _re.search(r"build_skyyclasses_(\\d+(?:\\.\\d+)*)\\.py$", f.replace("\\\\", "/"))
        if m:
            v = tuple(int(x) for x in m.group(1).split("."))
            if best is None or v > best: best, path = v, f
    if path is None: return None, None
    t = open(path, encoding="utf8").read()
    m = _re.search(r"^CLASSES = \\[(.*?)^\\]", t, _re.M | _re.S)
    if not m: return best, None
    names = _re.findall(r'"name":\\s*"([A-Za-z]+)"', m.group(1))
    return best, (names or None)
_cv, _cn = _classes_roster()
if _cv is not None and _cv >= (0, 1, 6):
    # a 0.1.6+ script whose CLASSES list cannot be parsed must FAIL the build (never look like "nothing to compare yet")
    if _cn is None:
        raise SystemExit("could not parse the SkyyClasses %s roster (CLASSES = [ ... ] with 'name' entries) - update _classes_roster()"
                         % ".".join(map(str, _cv)))
    assert sorted(_cn) == sorted(c[0] for c in CLASS_ROWS), "SkyyClasses %s roster %s != SkyySkills CLASS_ROWS" % (".".join(map(str, _cv)), _cn)
    print("class roster = SkyyClasses %s: %s" % (".".join(map(str, _cv)), ", ".join(_cn)))
else:
    print("class roster checked against the spec (newest SkyyClasses build script %s is older than 0.1.6 - nothing to compare yet)" % (".".join(map(str, _cv)) if _cv else "none"))
# 0.4: slots 10-12, 0.4.1: slot 13 Exploration = slots 10-13 (append-only; NOT classes)
EXTRA_ROWS = [("Alchemy", "Alchemy", "Potion_Health", "#7fe0d0"), ("Smithing", "Smithing", "Ingredient_Bar_Iron", "#c0c8d0"),
              ("Cooking", "Cooking", "Food_Pie_Apple", "#ffb070"), ("Exploration", "Exploration", "Tool_Map", "#e0a040")]
for _c in EXTRA_ROWS: must(_c[2])
_SL = [None] * (5 + len(CLASS_ROWS) + len(EXTRA_ROWS))
_B5 = ["Mining", "Foraging", "Farming", "Combat", "Acrobatics"]
_B5C = ["#8fc8ff", "#8fe08a", "#f0d060", "#ff8a7a", "#c8a0ff"]
for _i in range(5):
    _SL[_i] = (_B5[_i], _B5[_i], ICONS[_i], _B5C[_i])
for _i, _c in enumerate(CLASS_ROWS):
    assert _SL[CLASS_SLOT[_i]] is None, "slot %d used twice" % CLASS_SLOT[_i]
    _SL[CLASS_SLOT[_i]] = ("Combat." + _c[0], _c[1], _c[2], _c[3])
_FREE = [_i for _i, _x in enumerate(_SL) if _x is None]
assert _FREE == [10, 11, 12, 13], _FREE
for _j, _c in zip(_FREE, EXTRA_ROWS):
    _SL[_j] = (_c[0], _c[1], _c[2], _c[3])
SLOT_NAMES = [_x[0] for _x in _SL]
SLOT_LABELS = [_x[1] for _x in _SL]
SLOT_ICONS = [_x[2] for _x in _SL]
SLOT_COLORS = [_x[3] for _x in _SL]
assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 16
# append-only: every 0.4.3 slot keeps its index and saved key (player files store slots by NAMES; snap() writes only NAMES)
assert SLOT_NAMES[:14] == ["Mining", "Foraging", "Farming", "Combat", "Acrobatics", "Combat.Archer", "Combat.Warrior", "Combat.Assassin",
                           "Combat.Shaman", "Combat.Mage", "Alchemy", "Smithing", "Cooking", "Exploration"], SLOT_NAMES
assert SLOT_NAMES[10:14] == ["Alchemy", "Smithing", "Cooking", "Exploration"] and SLOT_NAMES[14:] == ["Combat.Berserker", "Combat.Priest"]
assert SLOT_LABELS[14:] == ["Fury", "Divinity"] and SLOT_LABELS[8] == "Shaman skill"
assert len(set(l.lower() for l in SLOT_LABELS)) == len(SLOT_LABELS) and len(set(n.lower() for n in SLOT_NAMES)) == len(SLOT_NAMES)
FURY_SLOT = CLASS_SLOT[[c[0] for c in CLASS_ROWS].index("Berserker")]
DIVINITY_SLOT = CLASS_SLOT[[c[0] for c in CLASS_ROWS].index("Priest")]
assert (FURY_SLOT, DIVINITY_SLOT) == (14, 15)
''')
rep('''defs.addField(CtField.make("public static final int CLASS0 = 5;", defs))
''', '''defs.addField(CtField.make("public static final int[] CLASS_SLOT = new int[] { %s };" % ", ".join(str(x) for x in CLASS_SLOT), defs))   # 0.4.4
''')
rep('''defs.addField(CtField.make("public static final int CLASS_END = %d;" % (5 + len(CLASS_ROWS)), defs))
''', '')
rep('''defs.addField(CtField.make("public static final int EXPLORATION = 13;", defs))   # 0.4.1
''', '''defs.addField(CtField.make("public static final int EXPLORATION = 13;", defs))   # 0.4.1
defs.addField(CtField.make("public static final int FURY = %d;" % FURY_SLOT, defs))           # 0.4.4 Berserker
defs.addField(CtField.make("public static final int DIVINITY = %d;" % DIVINITY_SLOT, defs))   # 0.4.4 Priest
''')
rep('''defs.addMethod(CtNewMethod.make("""
public static boolean isClass(int s) {
  return s >= CLASS0 && s < CLASS_END;
}""", defs))
''', '''# 0.4.4 (spec 3.2): class slots come from the table (5-9, 14, 15) - methods before their callers (perkRow, indexOf)
defs.addMethod(CtNewMethod.make("""
public static boolean isClass(int s) {
  for (int i = 0; i < CLASS_SLOT.length; i++) if (CLASS_SLOT[i] == s) return true;
  return false;
}""", defs))
# storage slot -> index into CLASSES, -1 = not a class slot
defs.addMethod(CtNewMethod.make("""
public static int classIdx(int s) {
  for (int i = 0; i < CLASS_SLOT.length; i++) if (CLASS_SLOT[i] == s) return i;
  return -1;
}""", defs))
# index into CLASSES -> storage slot, -1 = out of range
defs.addMethod(CtNewMethod.make("""
public static int classSlot(int i) {
  return i >= 0 && i < CLASS_SLOT.length ? CLASS_SLOT[i] : -1;
}""", defs))
''')
# sites 1 + 2: indexOf
rep('''  for (int i = 0; i < CLASSES.length; i++) if (CLASSES[i].toLowerCase().equals(t)) return CLASS0 + i;''',
    '''  for (int i = 0; i < CLASSES.length; i++) if (CLASSES[i].toLowerCase().equals(t)) return classSlot(i);''')
rep('''    for (int i = 0; i < CLASSES.length; i++) if (CLASSES[i].toLowerCase().startsWith(t)) return CLASS0 + i;''',
    '''    for (int i = 0; i < CLASSES.length; i++) if (CLASSES[i].toLowerCase().startsWith(t)) return classSlot(i);''')

# ================================================================ DivCfg (after PartyCfg: SkillCfg.load, compiled later, calls it)
before('''# ================= BridgeCfg (0.4): bridge.* keys (skill:fn:addxp / skill:fn:craftxp) =================
''', r'''# ================= DivCfg (0.4.4): divinity.* of xp.properties - Divinity XP from Priest heals (Classes-Berserker-Priest-Spec 3.4 / 3.5) ==
# Read by SkillCfg.load (/skills reload and the kit's reload routine re-read it); appended ONCE to an existing file without
# divinity.healXp.enabled (the PartyCfg pattern; the code defaults are the same numbers). Clamps = the Server Setup row bounds.
dvc.addField(CtField.make("public static final String DEFAULTS = " + DIV_LIT + ";", dvc))
for decl in ("boolean ON = true", "double PER_HP = 0.2", "long MAX_MIN = 300L"):
    dvc.addField(CtField.make("public static volatile " + decl + ";", dvc))
dvc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ON = {PKG}.SkillCfg.bool(p, "divinity.healXp.enabled", true);
  double r = {PKG}.SkillCfg.dbl(p, "divinity.healXpPerHp", 0.2);
  PER_HP = (Double.isNaN(r) || r < 0.0) ? 0.0 : (r > 100.0 ? 100.0 : r);
  long m = {PKG}.SkillCfg.lng(p, "divinity.healXpMaxPerMinute", 300L);
  MAX_MIN = m < 0L ? 0L : (m > 1000000000L ? 1000000000L : m);
}}""", dvc))
dvc.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  if (p.getProperty("divinity.healXp.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Divinity section (divinity.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Divinity section to xp.properties: " + t); }}
}}""", dvc))
dvc.addMethod(CtNewMethod.make("""
public static boolean on() {
  return ON && PER_HP > 0.0;
}""", dvc))
# 0.2 -> "0.2", 1.0 -> "1", 0.125 -> "0.125" (3 decimals at most)
dvc.addMethod(CtNewMethod.make("""
public static String num(double v) {
  if (Double.isNaN(v) || Double.isInfinite(v)) return "0";
  if (v == Math.floor(v) && Math.abs(v) < 1.0E15) return String.valueOf((long) v);
  return String.valueOf(Math.round(v * 1000.0) / 1000.0);
}""", dvc))
dvc.addMethod(CtNewMethod.make("""
public static String text() {
  if (!on()) return "off";
  return "on (" + num(PER_HP) + " XP per HP healed on others" + (MAX_MIN > 0L ? ", up to " + MAX_MIN + " a minute" : "") + ")";
}""", dvc))
# the Stats page's Divinity "Boosts right now" line (spec 3.6)
dvc.addMethod(CtNewMethod.make("""
public static String statsLine() {
  if (!on()) return "Divinity XP from healing is off on this server";
  return "Healing party members pays " + num(PER_HP) + " Divinity XP per HP" + (MAX_MIN > 0L ? " (up to " + MAX_MIN + " a minute)" : "");
}""", dvc))

''')
rep('''    {PKG}.PartyCfg.ensureDefaults(p);
''', '''    {PKG}.PartyCfg.ensureDefaults(p);
    {PKG}.DivCfg.ensureDefaults(p);
''')
rep('''    {PKG}.PartyCfg.read(p);
''', '''    {PKG}.PartyCfg.read(p);
    {PKG}.DivCfg.read(p);
''')
rep('''+ ", party combat XP " + {PKG}.PartyCfg.text() + ", bridge skills " +''',
    '''+ ", party combat XP " + {PKG}.PartyCfg.text() + ", divinity heal XP " + {PKG}.DivCfg.text() + ", bridge skills " +''')

# ================================================================ SkillClass sites 3-6 + the unknown-skill text
rep('''  for (int i = 0; i < {PKG}.SkillDefs.CLASSES.length; i++) if ({PKG}.SkillDefs.CLASSES[i].equalsIgnoreCase(t)) return {PKG}.SkillDefs.CLASS0 + i;''',
    '''  for (int i = 0; i < {PKG}.SkillDefs.CLASSES.length; i++) if ({PKG}.SkillDefs.CLASSES[i].equalsIgnoreCase(t)) return {PKG}.SkillDefs.classSlot(i);''')
rep('''  if (s >= {PKG}.SkillDefs.CLASS0 && s == slot(u)) {{''', '''  if ({PKG}.SkillDefs.isClass(s) && s == slot(u)) {{''')
rep('''  Object po = {PKG}.SkillStore.bridge().get("class:weapons:" + {PKG}.SkillDefs.CLASSES[slot - {PKG}.SkillDefs.CLASS0]);''',
    '''  Object po = {PKG}.SkillStore.bridge().get("class:weapons:" + {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(slot)]);''')
# sites 6 (killSlot hint), 10 (StatsPage.lines damage line), 11a (StatsPage.how), 11b (StatsPage.build note)
rep('''{PKG}.SkillDefs.CLASSES[s - {PKG}.SkillDefs.CLASS0]''', '''{PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)]''', count=4)
rep('''or a class skill: archery, swordsmanship, assassination, shaman, sorcery."''',
    '''or a class skill: archery, swordsmanship, sorcery, fury, divinity, assassination, shaman."''')

# ================================================================ SkillStore sites 7 + 8
rep('''  for (int s = {PKG}.SkillDefs.CLASS0; s < {PKG}.SkillDefs.CLASS_END; s++) {{
    if (s != cs && d[s] <= 0L) continue;''', '''  for (int j = 0; j < {PKG}.SkillDefs.CLASS_SLOT.length; j++) {{
    int s = {PKG}.SkillDefs.CLASS_SLOT[j];
    if (s != cs && d[s] <= 0L) continue;''')
rep('''  for (int k = {PKG}.SkillDefs.CLASS0; k < {PKG}.SkillDefs.CLASS_END; k++) if (d[k] > 0L) return -1L;''',
    '''  for (int j = 0; j < {PKG}.SkillDefs.CLASS_SLOT.length; j++) if (d[{PKG}.SkillDefs.CLASS_SLOT[j]] > 0L) return -1L;''')

# ================================================================ HealXp part 1 (the cap ring; before Acro.retainOnline, which prunes it)
before('''# ================= Perks (0.3): flat stat perks, legacy combat migration, double drops =================
''', r'''# ================= HealXp part 1 (0.4.4): the Divinity heal XP cap (research/Classes-Berserker-Priest-Spec.md 3.4) =================
# HWIN: UUID -> long[]{window start ms, heal XP granted in it} - base heal XP, BEFORE the xp multiplier. Per physical player, NOT reset by
# a profile switch (the BridgeXp.WIN rule); pruned to online players by Acro.retainOnline. HWARN: UUID -> Long last warning ms (one
# server-log line per player per minute).
hxp.addField(CtField.make("public static final java.util.HashMap HWIN = new java.util.HashMap();", hxp))
hxp.addField(CtField.make("public static final java.util.HashMap HWARN = new java.util.HashMap();", hxp))
hxp.addMethod(CtNewMethod.make(f"""
public static synchronized void warnLimited(java.util.UUID u, String text) {{
  long now = System.currentTimeMillis();
  Object last = HWARN.get(u);
  if (last instanceof Long && now - ((Long) last).longValue() < 60000L) return;
  HWARN.put(u, Long.valueOf(now));
  {PKG}.SkillCfg.warn("Divinity heal XP for " + u + ": " + text);
}}""", hxp))
# all or nothing (spec 3.4 "over the cap -> FALSE", the BridgeXp.allow rule): true = the whole `want` fits in this player's 60 s window
# and is recorded; false = it would cross divinity.healXpMaxPerMinute, nothing recorded (a later, smaller heal may still fit). cap <= 0 =
# no limit, nothing recorded.
hxp.addMethod(CtNewMethod.make("""
public static synchronized boolean take(java.util.UUID u, long want, long cap, long now) {
  if (want <= 0L) return false;
  if (cap <= 0L) return true;
  long[] w = (long[]) HWIN.get(u);
  if (w == null || now - w[0] >= 60000L || now < w[0]) { w = new long[] { now, 0L }; HWIN.put(u, w); }
  if (want > cap - w[1]) return false;
  w[1] = w[1] + want;
  return true;
}""", hxp))
# a refused offer gives its share back
hxp.addMethod(CtNewMethod.make("""
public static synchronized void give(java.util.UUID u, long amt) {
  if (amt <= 0L) return;
  long[] w = (long[]) HWIN.get(u);
  if (w == null) return;
  w[1] = w[1] > amt ? w[1] - amt : 0L;
}""", hxp))
hxp.addMethod(CtNewMethod.make("""
public static synchronized void retain(java.util.Set online) {
  HWIN.keySet().retainAll(online);
  HWARN.keySet().retainAll(online);
}""", hxp))
# hp x rate, the fraction paid by chance (PartyXp.amount style: 1 HP x 0.2 = 1 XP a fifth of the time); 0 for a non-positive / NaN input
hxp.addMethod(CtNewMethod.make("""
public static long amount(double hp, double rate) {
  if (Double.isNaN(hp) || Double.isNaN(rate) || !(hp > 0.0) || !(rate > 0.0)) return 0L;
  double x = hp * rate;
  if (x >= 9.0E15) return 9000000000000000L;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}""", hxp))
''')

# ================================================================ Perks.tick (site 9) + Acro.retainOnline prunes the heal ring
rep('''    String cn = cs < 0 ? "" : {PKG}.SkillDefs.CLASSES[cs - {PKG}.SkillDefs.CLASS0];''',
    '''    String cn = cs < 0 ? "" : {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(cs)];''')
rep('''    {PKG}.BridgeXp.retain(online);
  }} catch (Throwable t) {{ }}''', '''    {PKG}.BridgeXp.retain(online);
    {PKG}.HealXp.retain(online);
  }} catch (Throwable t) {{ }}''')

# ================================================================ HealXp.offer (after BridgeXp.offer, which it calls)
before('''# ================= PartyXp (0.4.2 stage 2, beta backlog 6: "party should share combat XP") =================
''', '''# ================= HealXp part 2 (0.4.4): skill:fn:healxp -> Divinity XP (research/Classes-Berserker-Priest-Spec.md 3.4) =================
# true = accepted (queued on the player's world thread) or nothing to pay; false = refused (see the header: part off / rate 0, bad hp, not
# a Priest (class skill Divinity = slot 15), class still following a profile switch, heal would cross the cap (all or nothing),
# BridgeXp.offer refused). The cap ring counts the base heal XP; a refused offer gives its share back (a task the world thread drops later
# keeps it for the rest of the window - fails closed, see the header). Any thread, no I/O, never throws.
hxp.addMethod(CtNewMethod.make(f"""
public static boolean offer(java.util.UUID u, double hp, String source, String expect) {{
  try {{
    if (u == null || !{PKG}.DivCfg.on()) return false;
    if (Double.isNaN(hp) || Double.isInfinite(hp) || hp <= 0.0) return false;
    if ({PKG}.SkillClass.slot(u) != {PKG}.SkillDefs.DIVINITY || !{PKG}.SkillClass.consistent(u)) return false;
    long base = amount(hp, {PKG}.DivCfg.PER_HP);
    if (base <= 0L) return true;
    long cap = {PKG}.DivCfg.MAX_MIN;
    if (!take(u, base, cap, System.currentTimeMillis())) {{ warnLimited(u, "divinity.healXpMaxPerMinute " + cap + " reached - refused " + base + " XP from " + source); return false; }}
    long r = -1L;
    try {{ r = {PKG}.BridgeXp.offer(u, {PKG}.SkillDefs.DIVINITY, base, source, expect, null, 0, false); }} catch (Throwable t) {{ r = -1L; }}
    if (r < 0L) {{ if (cap > 0L) give(u, base); return false; }}
    return true;
  }} catch (Throwable t) {{ return false; }}
}}""", hxp))
''')

# ================================================================ skill:fn:healxp Function (after SkillAddFn)
before('''# ================= skill:fn:craftxp (0.4): apply(Object[]{UUID, String recipeId, Number crafts, String source [, String expectKey]}) -> Long | null
''', '''# ================= skill:fn:healxp (0.4.4): apply(Object[]{UUID healer, Number hpHealedOnOthers, String source [, String expectKey]}) -> Boolean
# Published for SkyyClasses 0.1.6 (source "classes:heal"); HealXp.offer has every rule.
hfn.addInterface(pool.get("java.util.function.Function"))
hfn.addConstructor(CtNewConstructor.make("public SkillHealFn() { }", hfn))
hfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) arg;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof Number)) return Boolean.FALSE;
    String src = a.length > 2 && a[2] != null ? String.valueOf(a[2]) : "?";
    String expect = a.length > 3 && a[3] instanceof String ? (String) a[3] : null;
    return {PKG}.HealXp.offer((java.util.UUID) a[0], ((Number) a[1]).doubleValue(), src, expect) ? Boolean.TRUE : Boolean.FALSE;
  }} catch (Throwable t) {{ return Boolean.FALSE; }}
}}""", hfn))
''')

# ================================================================ Stats page: the Divinity heal line (spec 3.6) + how(Combat)
before('''  if (!next) {{
    String tl = treeLine(u, s);''', '''  if (s == {PKG}.SkillDefs.DIVINITY && !next) out.add({PKG}.DivCfg.statsLine());
''')
rep('''"Your combat skill is your class skill - Archer Archery / Warrior Swordsmanship / Mage Sorcery (Assassin and Shaman later)"''',
    '''"Your combat skill is your class skill - Archer Archery / Warrior Swordsmanship / Mage Sorcery / Berserker Fury / Priest Divinity (Assassin and Shaman later)"''')

# ================================================================ Server Setup rows (spec 3.5)
after('''    ("bridge.bonus.enabled", "Skill tree bonuses", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: SkyyTrees Wisdom (more XP) and Fortune (double drops) nodes are ignored.", "reload"),
''', '''    ("divinity.healXp.enabled", "Divinity XP from healing", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: Priest heals pay no Divinity XP (kills still do). Levels are kept.", "reload"),
''')
after('''    ("combat.classWeaponOnly", "Only class weapons earn XP", "combat", "bool", "true", "", "", "", "", "live",
     "On: only the class's own weapons earn combat XP. Off: anything SkyyClasses lets the class use.", "reload"),
''', '''    # 0.4.4 Divinity XP from Priest heals (skill:fn:healxp, SkyyClasses 0.1.6); kills pay Fury / Divinity through the rows above
    ("divinity.healXpPerHp", "Divinity XP per HP healed", "combat", "dec", "0.2", "0", "100", "", "", "live",
     "XP per 1 HP a Priest heals on OTHER party members (healing themself pays nothing).", "reload"),
    ("divinity.healXpMaxPerMinute", "Divinity heal XP per minute", "combat", "int", "300", "0", "1000000000", "", "", "live",
     "Most Divinity XP healing pays one Priest in 60 s (0 = no limit). Kills are not counted.", "reload"),
''')
after('''print("config rows: %d (%d tables), %d not in the default file (zero perk stats, adv)" % (len(CFG_ROWS), sum(1 for _r in CFG_ROWS if _r[3] == "table"), len(_absent)))
''', '''assert len(CFG_ROWS) == 154, "0.4.3 had 151 rows + 3 Divinity rows (spec 7.1), got %d" % len(CFG_ROWS)   # 0.4.4
for _k in ("divinity.healXp.enabled", "divinity.healXpPerHp", "divinity.healXpMaxPerMinute"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp, _k
''')

# ================================================================ commands: skill arg help texts + the no-class line
rep('''"mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | assassination | shaman | sorcery"''',
    '''"mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | sorcery | fury | divinity | assassination | shaman"''', count=2)
# /skills xp: the same list as stats / top (0.4.3 left out assassination | shaman there although SkillClass.argSlot accepts every class
# skill for all three commands)
rep('''"mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | sorcery"''',
    '''"mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | sorcery | fury | divinity | assassination | shaman"''')
rep('''or name a class skill (archery, swordsmanship, sorcery).''', '''or name a class skill (archery, swordsmanship, sorcery, fury, divinity).''')

# ================================================================ plugin: skill:fn:healxp published in setup, removed in shutdown
rep('''  {PKG}.SkillStore.bridge().put("skill:fn:felledBy", new {PKG}.FelledByFn());
''', '''  {PKG}.SkillStore.bridge().put("skill:fn:felledBy", new {PKG}.FelledByFn());
  {PKG}.SkillStore.bridge().put("skill:fn:healxp", new {PKG}.SkillHealFn());
''')
rep('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:felledBy"); }} catch (Throwable t) {{ }}
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:felledBy"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:healxp"); }} catch (Throwable t) {{ }}
''')
rep('''+ "; bridge skill:fn:addxp + skill:fn:craftxp; trees bridge on (tree bonuses "''',
    '''+ "; divinity heal XP " + {PKG}.DivCfg.text() + "; bridge skill:fn:addxp + skill:fn:craftxp + skill:fn:healxp; trees bridge on (tree bonuses "''')
rep('''fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft, skit, karm):
    c.writeFile(OUT)''', '''fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft, skit, karm, dvc, hxp, hfn):
    c.writeFile(OUT)''')
rep('''kills with class weapons (nearby SkyyParty members get a share in their own class skill)''',
    '''kills with class weapons (nearby SkyyParty members get a share in their own class skill), Priest heals on party members (Divinity, from SkyyClasses)''')
rep('''and your class combat skill (SkyyClasses) to level 100.''',
    '''and your class combat skill (SkyyClasses: Archery, Swordsmanship, Sorcery, Fury, Divinity) to level 100.''')

# ================================================================ post-conditions
assert s.count('VERSION = "0.4.4"') == 1 and "0.4.3 - build script" not in s
# no class-slot arithmetic left in the Java (the fields are gone, so javassist would also refuse a leftover reference)
for _bad in ("SkillDefs.CLASS0", "SkillDefs.CLASS_END", "CLASS0 + i", "public static final int CLASS0", "public static final int CLASS_END",
             "s >= CLASS0", "- {PKG}.SkillDefs.CLASS0]"):
    assert _bad not in s, "class-slot arithmetic left: " + _bad
assert s.count("classIdx(") >= 7 and s.count("classSlot(i)") == 3 and s.count("SkillDefs.CLASS_SLOT") >= 3
# javassist: methods before their callers
assert s.index("public static int classSlot(int i) {") < s.index("public static int perkRow(int s) {") < s.index("public static int indexOf(String s) {")
assert s.index("public static boolean isClass(int s) {") < s.index("public static int perkRow(int s) {")
assert s.index("public static String statsLine() {") < s.index("public static java.util.ArrayList lines(java.util.UUID u, int s, int lv, boolean next) {{")
assert s.index("public static void ensureDefaults(java.util.Properties p) {{\n  if (p.getProperty(\"divinity.healXp.enabled\")") < s.index("public static synchronized String load() {{")
assert s.index("public static synchronized void retain(java.util.Set online) {\n  HWIN") < s.index("{PKG}.HealXp.retain(online);")
assert s.index("public static long offer(java.util.UUID u, int slot, long base,") < s.index("public static boolean offer(java.util.UUID u, double hp,")
assert s.index("public static boolean offer(java.util.UUID u, double hp,") < s.index("return {PKG}.HealXp.offer((java.util.UUID) a[0]")
assert s.index("public static int classIdx(int s) {") < s.index("public static void tick(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref) {{")
# bridge function lifecycle, one Divinity block, no new ECS system, the class list
assert s.count('bridge().put("skill:fn:healxp"') == 1 and s.count('bridge().remove("skill:fn:healxp")') == 1
assert s.count("L.extend(DIV_L)") == 1 and s.count("{PKG}.DivCfg.ensureDefaults(p);") == 1 and s.count("{PKG}.DivCfg.read(p);") == 1
assert s.index("{PKG}.PartyCfg.ensureDefaults(p);") < s.index("{PKG}.DivCfg.ensureDefaults(p);") < s.index("{PKG}.SkillDefs.setTable({PKG}.SkillDefs.DEFAULT_PER);")
assert "skit, karm, dvc, hxp, hfn):" in s and s.count("registerSystem(") == REG0   # no new ECS system
# review fixes (2026-09-25): the heal cap is all or nothing and offers the whole base; the three skill helps are one list; a 0.1.6+
# SkyyClasses roster that cannot be parsed fails the build
assert s.count("public static synchronized boolean take(java.util.UUID u, long want, long cap, long now) {") == 1 and "long g = take(" not in s
assert "BridgeXp.offer(u, {PKG}.SkillDefs.DIVINITY, base, source, expect, null, 0, false)" in s
assert s.count('"mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | sorcery | fury | divinity | assassination | shaman"') == 3
assert 'raise SystemExit("could not parse the SkyyClasses %s roster' in s
assert s.count('"Weapon_Deployable_Slowness_Totem"') == 1 and s.count('("Priest", "Divinity", "Weapon_Wand_Wood", "#f2e6a0")') == 1
# config publication stays the LAST statement of setup()
_su = s[s.index("public void setup() {{"):]
_su = _su[:_su.index('}}""", pl))')]
assert _su.rstrip().endswith("{PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());")
assert _su.index("{PKG}.SkillCfg.load();") < _su.index('put("skill:fn:healxp"') < _su.index("CfgPub.start(")
for ident in re.findall(r"#(Skyy[A-Za-z0-9_]*)", s):
    assert "_" not in ident, "UI id with an underscore: " + ident
assert "--deploy" in s   # the script keeps its optional deploy switch; this workflow never passes it
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.4.3
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
