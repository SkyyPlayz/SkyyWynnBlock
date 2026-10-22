"""Derive SkyySkills/build_skyyskills_0.4.58.py from the GENERATED SkyySkills 0.4.57 (build_skyyskills_0.4.57.py = the tools/deploy_set.py SET
pin, made by tools/skills_0_4_57_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with
0.4.57 (tools/soundpass_gen.Patch). Line endings kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_58_patch.py   then   python SkyySkills/build_skyyskills_0.4.58.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.58.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.4.58 (2026-10-20) = BALANCE PASS P4, the SkyySkills part (research/Balance-P4-Combat-Spec.md Part 2 + 3 + 6; FULL round with SkyyGear
  0.3.34, SkyyMobs 0.1.14, SkyyClasses 0.1.44, SkyyArmory 0.1.42, SkyyTrees 0.4.4 - deploy and roll back TOGETHER). Skyy (2026-10-18): "i think
  all the classes need balance a little bit, and tuned more into their role. so things like their speed, weight, defense, health, stamina, and
  mana are tuned for the class" + "scale down how much mana you get as you level, and mana regen a little" + popup 2026-10-20 "Mana ... OK?" ->
  "Bigger pool, slower regen (Recommended)" (Skyy approved the DIRECTION and the numbers Mage 80 / 9.5, Priest 40 / 7, Spellblade 50 / 3 -
  the pools in 3. are a BUILD RE-TUNE, NOT Skyy's numbers, awaiting Skyy's OK); every other spec question takes its recommended default
  (docs/answered/classes.md P4 line).
  1. CLASS STATS from the Class-Roles-Sheet ratings (spec 2.1 / 2.2; Server Setup -> Skills -> Class Power, switch class.stats.enabled):
     class.healthPct (Warrior +35, Berserker +15, Assassin -10, Mage -20, the rest 0 %) = ONE ADDITIVE max Health modifier skyyskill_classhp
     = pct x (the stat's base + every other ADDITIVE max Health modifier except the percent layers: SkyyRebirth's, SkyyAccessories' skyyacc_*),
     recomputed every second (Perks.tick). VERIFIED at build time (bytecode): EntityStatValue.computeModifiers SUMS the multiplicative amounts,
     so a multiplicative 1.35 would add to the others instead of multiplying - an additive percent layer is the exact one; RbStat's layer
     skips ours and ours skips it. class.defense (Warrior 45, Berserker / Spellblade / Archer / Priest 10, Monk / Assassin 5, Mage 0) adds to
     the skill Defense (SkillDef: hits x 100 / (100 + Defense)). class.damage (% of class WEAPON hits on MONSTERS - never players, never a
     SkyyClasses ability hit (class:fn:abilhit names the caster; spec 2.4: the factor corrects weapon DPS only);
     CombatDmgSys, one multiplication with the class perk): Warrior 100, Berserker 130, Spellblade 148, Monk 202, Assassin 120 - MEASURED by
     the build from the vanilla starter weapons' primary chains in Assets.zip (100 x rating x the Warrior's DPS / the class's DPS,
     tools/balance_model.py p4_measure; a factor outside 60-250 or more than 10 % off the shipped default STOPS the build), Archer 200
     (Mob-Curve-Spec 5.2), Mage / Priest 100 (the Mana budget decides). Stamina (stamina.classBase / classPerLevel): Berserker 12/0.16 ->
     13/0.17, Monk 10/0.13 -> 13/0.17, Assassin + Archer 9/0.12 -> 10/0.13, Priest 5/0.06 -> 4/0.05; Warrior, Mage, Spellblade unchanged.
  2. WEIGHT x ARMOR = SPEED (spec 2.3; Server Setup -> Skills -> Acrobatics): armor load = the sum over worn pieces of slot share (Head 0.2,
     Chest 0.35, Hands 0.15, Legs 0.3) x type load (Cloth 0, Light 1, Heavy 3; the type from SkyyGear 0.3.34's gear:fn:weight); speed % =
     class.speed + armor.perLoad 4 x (class.armorLoad, its own full-set load - the worn load) x class.weight (Warrior 0.25 ... Mage /
     Assassin 2): Warrior -3 cloth / -6 heavy, Mage +6 cloth / -18 heavy, Monk +18 / +12 / 0, Assassin +20 / +12 / -4. Posted on the shared
     movement protocol as source skills.classweight (flat layer) every second (Acro.bonuses); without SkyyGear the class's own armor is
     assumed (= the rated speed). The ceiling move.maxFactor 1.8: one more source skills.speedcap (pct layer) cancels whatever the other
     sources add past x1.8 (every applier computes the same total from the same sources - no fight).
  3. MANA (spec 3.2 + the BUILD RE-TUNE in tools/balance_model.py P4_MANA: the spec's pools ran dry in 16 s at Lv 20 and the first build's
     refill between charged shots made them never run dry): Base Mana / per class level Mage 45 / 9.5 -> 80 / 14.5, Priest 42 / 4.5 -> 60 /
     10, Spellblade 33 / 3 -> 70 / 6 (+ SkyyClasses 0.1.44 abil.costPerLevel Mage 0, Spellblade 2.5, others 1.5 %) - every caster runs dry
     in 20-28 s of non-stop casting at Lv 1 / 5 / 10 / 20 / 30 / 40 / 60 / 80 / 100 (balance_model --check). These pool and cost-growth
     numbers are the BUILD's, awaiting Skyy's OK (Skyy's approved pools run dry in 5-16 s with the real staff / wand costs); so is the new
     row mana.refillBelow (a BUILD DECISION, spec question 7's "after they run dry": without it the refill between charged shots kept
     every caster from ever running dry). Regen growth per class level
     (mana.regen.perLevel) 5 -> 3 %; mana.regen.class (% of every Mana refill; Spellblade 50: half the in-combat refill + half of vanilla's own
     refill taken back out of combat); the QUICK REFILL mana.refillPct (Mage / Priest / Spellblade 15 % of max Mana a second, in combat) runs
     once the bar is DRY (under mana.refillBelow 20 % of max) until it is full again, and waits mana.refillDelay 1 s after each charged shot
     / ability - SkyyClasses 0.1.44 and SkyyArmory 0.1.42 call the registry's new verb skill:fn:manaregen {"cast", UUID} -> Boolean; a
     player who never cast counts as long ago. ~80 % of the bar back in 6-7.5 s of basic attacks. The latch is updated every pulse BEFORE
     the full-bar early return (fix round: a bar the refill topped up exactly to full never cleared it), and a profile switch forgets it
     (ClassStat.forget). The Spellblade's 50 % share takes back at most half of what vanilla can still add (min(rate x secs, room)), so its
     bar reaches full.
  4. ONE-TIME UPDATE P4Mig (PROJECT-RULES 4; P3Mig's reviewed machinery, copied): ONCE on an existing xp.properties, setup() right after the P3
     updates, BEFORE SkillCfg.load. Each of the 15 P4 keys whose LAST entry is a one-line entry holding exactly its 0.4.57 default -> its
     0.4.58 default (value text only); any other value kept (one INFO line). Then ONE block in the file's own line ending: the P4 rows the
     file lacks + the run-once marker. config-history copy first (verified), one config-changes.log row per change (Undo), a Properties
     check (only the planned keys differ), atomicWrite. A fresh file carries the marker.
  SAVED DATA: none (player files untouched). New classes ClassStat, P4Mig; no new command or system.
  ROLLBACK to 0.4.57: only TOGETHER with the P4 set; Undo the P4Mig rows in Server Setup -> Changes first (0.4.57 reads the moved Mana /
  Stamina numbers as admin values and ignores the new rows). The class Health modifier skyyskill_classhp is saved with the player by the
  engine: switch class.stats.enabled off for a session before rolling back (that removes it), or it stays until 0.4.58 returns.
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.57.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.58.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.57"') and P.has("P3Mig"), "not the generated SkyySkills 0.4.57 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

P.rep('''"""SkyySkills 0.4.57 - build script (derived from the generated 0.4.56 by tools/skills_0_4_57_patch.py - edit the patch, not this file;
0.4.57 (2026-10-20) = BALANCE PASS P3''', '''"""SkyySkills 0.4.58 - build script (derived from the generated 0.4.57 by tools/skills_0_4_58_patch.py - edit the patch, not this file;
''' + NOTE + '''0.4.57 was derived from the generated 0.4.56 by tools/skills_0_4_57_patch.py;
0.4.57 (2026-10-20) = BALANCE PASS P3''')
P.rep('VERSION = "0.4.57"', 'VERSION = "0.4.58"')

# ================================================================================================================ the P4 data + the fresh default file
P4DATA = r'''# ================= 0.4.58 BALANCE P4 - the P4 rows, the P4 update plan and the fresh default file (tools/skills_0_4_58_patch.py) =================
# Every number comes from tools/balance_model.py (P4_CLASSES, P4_CLASS_DAMAGE, P4_MANA, P4_REGEN, ...: research/Balance-P4-Combat-Spec.md).
import balance_model as BM
P4_CLASSES = ["Archer", "Warrior", "Assassin", "Monk", "Mage", "Berserker", "Priest", "Spellblade"]     # OverallCfg.TCLASSES order


def _p4n(v):
    v = float(v)
    return str(int(v)) if v == int(v) else repr(v)


P4_HP = dict((c, BM.P4_CLASSES[c][1]) for c in P4_CLASSES)
P4_DEF = dict((c, BM.P4_CLASSES[c][2]) for c in P4_CLASSES)
P4_DMG = dict((c, BM.P4_CLASS_DAMAGE[c]) for c in P4_CLASSES)
P4_SPD = dict((c, BM.P4_CLASSES[c][5]) for c in P4_CLASSES)
P4_WGT = dict((c, BM.P4_RATE["weight"][BM.P4_CLASSES[c][0]]) for c in P4_CLASSES)
P4_NAT = dict((c, BM.P4_LOAD[BM.P4_CLASSES[c][6]]) for c in P4_CLASSES)
P4_REGEN = dict((c, BM.P4_REGEN_CLASS.get(c, 100)) for c in P4_CLASSES)
P4_REFILL = dict((c, BM.P4_REFILL[c]) for c in P4_CLASSES if c in BM.P4_REFILL)
# (key, 0.4.57 default, 0.4.58 default, change-log row) - spec 2.2 Stamina + 3.2 Mana
P4_KEYS = [("mana.classBase.Mage", "45", _p4n(BM.P4_MANA["Mage"][0])), ("mana.classBase.Priest", "42", _p4n(BM.P4_MANA["Priest"][0])),
           ("mana.classBase.Spellblade", "33", _p4n(BM.P4_MANA["Spellblade"][0])),
           ("mana.classPerLevel.Mage", "9.5", _p4n(BM.P4_MANA["Mage"][1])), ("mana.classPerLevel.Priest", "4.5", _p4n(BM.P4_MANA["Priest"][1])),
           ("mana.classPerLevel.Spellblade", "3", _p4n(BM.P4_MANA["Spellblade"][1])), ("mana.regen.perLevel", "5", "3"),
           ("stamina.classBase.Archer", "9", "10"), ("stamina.classBase.Assassin", "9", "10"), ("stamina.classBase.Monk", "10", "13"),
           ("stamina.classBase.Berserker", "12", "13"), ("stamina.classBase.Priest", "5", "4"),
           ("stamina.classPerLevel.Archer", "0.12", "0.13"), ("stamina.classPerLevel.Assassin", "0.12", "0.13"), ("stamina.classPerLevel.Monk", "0.13", "0.17"),
           ("stamina.classPerLevel.Berserker", "0.16", "0.17"), ("stamina.classPerLevel.Priest", "0.06", "0.05")]
P4_KEYS = [(_k, _o, _w, (_k[:_k.rindex(".")] + "[" + _k[_k.rindex(".") + 1:] + "]") if _k.split(".")[-1] in P4_CLASSES else _k) for _k, _o, _w in P4_KEYS]
for _k, _o, _w, _r in P4_KEYS:
    _c = _k.split(".")[-1]
    assert not _k.startswith("mana.classBase.") or float(_w) == BM.P4_MANA[_c][0], _k
    assert not _k.startswith("stamina.classBase.") or float(_w) == BM.P4_CLASSES[_c][3], _k
    assert not _k.startswith("stamina.classPerLevel.") or float(_w) == BM.P4_CLASSES[_c][4], _k
assert all(dict((_k, _w) for _k, _o, _w, _r in P4_KEYS)["mana.classPerLevel." + _c] == _p4n(BM.P4_MANA[_c][1]) for _c in ("Mage", "Priest", "Spellblade"))
assert [_w for _k, _o, _w, _r in P4_KEYS][:6] == ["80", "60", "70", "14.5", "10", "6"], "the build re-tune (balance_model P4_MANA)"
assert dict((_k, _w) for _k, _o, _w, _r in P4_KEYS)["mana.regen.perLevel"] == _p4n(BM.P4_REGEN[2])
P4_SCAL = [("class.stats.enabled", "true"), ("armor.load.cloth", _p4n(BM.P4_LOAD["Cloth"])), ("armor.load.light", _p4n(BM.P4_LOAD["Light"])),
           ("armor.load.heavy", _p4n(BM.P4_LOAD["Heavy"])), ("armor.slot.head", _p4n(BM.P4_SLOT["Head"])), ("armor.slot.chest", _p4n(BM.P4_SLOT["Chest"])),
           ("armor.slot.hands", _p4n(BM.P4_SLOT["Hands"])), ("armor.slot.legs", _p4n(BM.P4_SLOT["Legs"])), ("armor.perLoad", _p4n(BM.P4_PER_LOAD)),
           ("move.maxFactor", _p4n(BM.P4_MAX_FACTOR)), ("mana.refillDelay", _p4n(BM.P4_REFILL_DELAY)), ("mana.refillBelow", _p4n(BM.P4_REFILL_BELOW))]
P4_TABLES = [("class.healthPct", P4_HP), ("class.defense", P4_DEF), ("class.damage", P4_DMG), ("class.speed", P4_SPD), ("class.weight", P4_WGT),
             ("class.armorLoad", P4_NAT), ("mana.regen.class", P4_REGEN), ("mana.refillPct", P4_REFILL)]
P4_ADD = [(_k, _v, _k) for _k, _v in P4_SCAL] + [("%s.%s" % (_t, _c), _p4n(_d[_c]), "%s[%s]" % (_t, _c)) for _t, _d in P4_TABLES for _c in P4_CLASSES if _c in _d]
P4_MARK_ID = "Balance P4 combat (SkyySkills 0.4.58)"
P4_MARK = "# %s: class Health, Defense, damage, speed and weight, Stamina, Mana pools, regen and the quick refill" % P4_MARK_ID
P4_HEAD = ["", "# ---------- Balance P4: class stats, speed and Mana (SkyySkills 0.4.58) ----------",
           "# Comments must stay on their own lines.",
           "# CLASS STATS (class.stats.enabled): class.healthPct = percent more (or less) max Health, class.defense = Defense (hits x 100 / (100 +",
           "# Defense)), class.damage = percent of class weapon and ability hits on monsters (100 = unchanged; never on players).",
           "# SPEED: speed percent = class.speed + armor.perLoad x (class.armorLoad - the worn load) x class.weight; worn load = the sum over worn",
           "# pieces of armor.slot.<slot> x armor.load.<type> (the types from SkyyGear). move.maxFactor = the most total move speed (1.8 = +80 percent).",
           "# MANA: mana.regen.class = percent of every Mana refill a class gets; mana.refillPct = percent of max Mana a second in combat once",
           "# the bar ran dry (under mana.refillBelow percent of max) until it is full again, waiting mana.refillDelay seconds after each",
           "# charged shot or ability."]
for _t in P4_HEAD + [P4_MARK]:
    assert all(32 <= ord(_c) < 127 for _c in _t) and '"' not in _t and "\\" not in _t and (not _t or _t.startswith("# ")), _t
assert "=" not in P4_MARK and not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in P4_HEAD)
P4_BLOCK = "\n".join(P4_HEAD + ["%s=%s" % (_k, _v) for _k, _v, _r in P4_ADD] + [P4_MARK]) + "\n"


def p4_apply(text):
    """the Python twin of P4Mig.plan for an LF default file of one-line entries"""
    out, seen = [], set()
    for _ln in text.split("\n"):
        _t = _ln.strip()
        if _t and not _t.startswith("#") and not _t.startswith("!") and "=" in _ln:
            _k, _v = _ln.split("=", 1)
            _hit = [_e for _e in P4_KEYS if _e[0] == _k.strip()]
            if _hit and _v.strip() == _hit[0][1]:
                seen.add(_k.strip())
                _ln = _k + "=" + _hit[0][2]
        out.append(_ln)
    body = "\n".join(out)
    return body + ("" if body.endswith("\n") else "\n") + P4_BLOCK, seen


DEFAULTS_057 = DEFAULTS   # 0.4.58: the 0.4.57 default file (its asserts below read it as _dp57)
DEFAULTS, _p4seen = p4_apply(DEFAULTS_057)
assert sorted(_p4seen) == sorted(_k for _k, _o, _w, _r in P4_KEYS), sorted(set(_k for _k, _o, _w, _r in P4_KEYS) - _p4seen)
assert all(ord(ch) < 128 for ch in DEFAULTS) and len(DEFAULTS.encode("utf-8")) < 65000 and DEFAULTS.count(P4_MARK_ID) == 1, len(DEFAULTS)
# the code defaults of the rows P4 changes (a file without the line = the P4 value); the 0.4.57 blocks above keep the old values
P4_CLASS_BASE = [(_c, int(BM.P4_MANA[_c][0]) if _c in ("Mage", "Priest", "Spellblade") else _v) for _c, _v in CLASS_BASE_DEF]
P4_CLASS_MANA = [(_c, (_p4n(BM.P4_MANA[_c][1]) if _c in ("Mage", "Priest", "Spellblade") else _v)) for _c, _v in CLASS_MANA_DEF]
P4_STA_BASE = [(_c, _p4n(BM.P4_CLASSES[_c][3])) for _c, _v in P25_STA_BASE]
P4_STA_PER = [(_c, _p4n(BM.P4_CLASSES[_c][4])) for _c, _v in P25_STA_PER]
P4_PER_DEF = _p4n(BM.P4_REGEN[2])
assert dict(P4_CLASS_BASE) == {"Archer": 24, "Warrior": 21, "Assassin": 24, "Monk": 21, "Mage": 80, "Berserker": 12, "Priest": 60, "Spellblade": 70}, P4_CLASS_BASE
assert [str(_v) for _c, _v in P4_CLASS_MANA] == ["1", "1", "1", "1", "14.5", "1", "10", "6"], P4_CLASS_MANA
assert P4_STA_BASE == [("Archer", "10"), ("Warrior", "10"), ("Assassin", "10"), ("Monk", "13"), ("Mage", "4"), ("Berserker", "13"), ("Priest", "4"), ("Spellblade", "7")], P4_STA_BASE
assert P4_PER_DEF == "3"
# 2.4: the class damage factors, MEASURED from Assets.zip (balance_model.p4_measure: the vanilla starter weapon's primary chain, the Warrior's
# sword = 100 x rating); STOP when a factor leaves 60-250 % or the shipped default is more than 10 % off the measurement
P4_MEAS = BM.p4_measure()
P4_FACT = BM.p4_damage_factors(P4_MEAS)
for _c in P4_CLASSES:
    _m = P4_FACT[_c]
    assert _m is not None and 60.0 <= _m <= 250.0, "STOP (spec 2.4): the %s damage factor %s is outside 60-250 %% - review the class / weapon numbers" % (_c, _m)
    assert 60.0 <= P4_DMG[_c] <= 250.0 and abs(P4_DMG[_c] - _m) <= 0.1 * _m, "STOP: the shipped %s class.damage %s is not the measured %.0f" % (_c, P4_DMG[_c], _m)
print("0.4.58 class damage (measured, Assets.zip starter weapons, Lv 1 / 20 / 50 DPS scale alike: one F): " + "; ".join(
    "%s %s%% (%s)" % (_c, P4_DMG[_c], ("avg hit %.2f every %.3f s = %.1f DPS" % P4_MEAS[_c]) if P4_MEAS.get(_c) else "fixed")
    for _c in P4_CLASSES))
print("0.4.58: P4 update plan %d keys, %d lines appended; default file %d bytes" % (len(P4_KEYS), len(P4_ADD), len(DEFAULTS)))
'''
P.rep('''DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)''',
      P4DATA + '''DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)''')

# ================================================================================================================ code defaults of the P4 rows
P.rep('''mrg.addField(CtField.make("public static volatile double PER_LEVEL = " + KXP_PER_DEF + ".0;", mrg))''',
      '''mrg.addField(CtField.make("public static volatile double PER_LEVEL = " + P4_PER_DEF + ".0;", mrg))   # 0.4.58: 5 -> 3''')
P.rep('''    double mpl = dbl(p, "mana.regen.perLevel", {KXP_PER_DEF}.0);''', '''    double mpl = dbl(p, "mana.regen.perLevel", {P4_PER_DEF}.0);   // 0.4.58 P4: 5 -> 3''')
P.rep('''ovc.addField(CtField.make("public static final String[] DEF_CLS = %s;" % jarr([_c for _c, _v in CLASS_BASE_DEF]), ovc))
ovc.addField(CtField.make("public static final double[] DEF_BASE = new double[] { %s };" % ", ".join("%d.0" % _v for _c, _v in CLASS_BASE_DEF), ovc))''',
      '''ovc.addField(CtField.make("public static final String[] DEF_CLS = %s;" % jarr([_c for _c, _v in P4_CLASS_BASE]), ovc))
ovc.addField(CtField.make("public static final double[] DEF_BASE = new double[] { %s };" % ", ".join("%d.0" % _v for _c, _v in P4_CLASS_BASE), ovc))   # 0.4.58 P4''')
P.rep('''cman.addField(CtField.make("public static final String[] DEF_CLS = %s;" % jarr([_c for _c, _v in CLASS_MANA_DEF]), cman))
cman.addField(CtField.make("public static final double[] DEF_PER = new double[] { %s };" % ", ".join(repr(float(_v)) for _c, _v in CLASS_MANA_DEF), cman))''',
      '''cman.addField(CtField.make("public static final String[] DEF_CLS = %s;" % jarr([_c for _c, _v in P4_CLASS_MANA]), cman))
cman.addField(CtField.make("public static final double[] DEF_PER = new double[] { %s };" % ", ".join(repr(float(_v)) for _c, _v in P4_CLASS_MANA), cman))   # 0.4.58 P4''')
P.rep('''cpw.addField(CtField.make("public static final String[] DEF_CLS = %s;" % jarr([_c for _c, _v in P25_STA_BASE]), cpw))
cpw.addField(CtField.make("public static final double[] D0 = new double[] { %s };" % ", ".join(repr(float(_v)) for _c, _v in P25_STA_BASE), cpw))
cpw.addField(CtField.make("public static final double[] D1 = new double[] { %s };" % ", ".join(repr(float(_v)) for _c, _v in P25_STA_PER), cpw))''',
      '''cpw.addField(CtField.make("public static final String[] DEF_CLS = %s;" % jarr([_c for _c, _v in P4_STA_BASE]), cpw))
cpw.addField(CtField.make("public static final double[] D0 = new double[] { %s };" % ", ".join(repr(float(_v)) for _c, _v in P4_STA_BASE), cpw))   # 0.4.58 P4
cpw.addField(CtField.make("public static final double[] D1 = new double[] { %s };" % ", ".join(repr(float(_v)) for _c, _v in P4_STA_PER), cpw))''')

# ================================================================================================================ the asserts that read 0.4.57 values
P.rep('''_dp56 = {}   # 0.4.57: the 0.4.56 default file (the 0.4.56 blocks' own checks below read it)''',
      '''_dp57 = {}   # 0.4.58: the 0.4.57 default file (the 0.4.57 blocks' own checks below read it; the P4 rows moved in _dp)
for _ln in DEFAULTS_057.split("\\n"):
    _t = _ln.strip()
    if _t and not _t.startswith("#") and "=" in _t:
        _dp57[_t.split("=", 1)[0].strip()] = _t.split("=", 1)[1].strip()
_dp56 = {}   # 0.4.57: the 0.4.56 default file (the 0.4.56 blocks' own checks below read it)''')
P.rep('''for _cb, _cv in CLASS_BASE_DEF:
    assert _dp.get("mana.classBase." + _cb) == str(_cv) and ("\\nmana.classBase.%s=%d\\n" % (_cb, _cv)) in ("\\n" + OVL_DEFAULTS), _cb''',
      '''for _cb, _cv in CLASS_BASE_DEF:
    assert _dp57.get("mana.classBase." + _cb) == str(_cv) and ("\\nmana.classBase.%s=%d\\n" % (_cb, _cv)) in ("\\n" + OVL_DEFAULTS), _cb   # 0.4.58: the 0.4.57 file
assert all(_dp.get("mana.classBase." + _cb) == str(_cv) for _cb, _cv in P4_CLASS_BASE)   # 0.4.58 P4''')
P.rep('''for _cc, _cv in CLASS_MANA_DEF:
    assert _dp.get("mana.classPerLevel." + _cc) == str(_cv) and ("\\nmana.classPerLevel.%s=%s\\n" % (_cc, _cv)) in ("\\n" + CMAN_DEFAULTS), _cc''',
      '''for _cc, _cv in CLASS_MANA_DEF:
    assert _dp57.get("mana.classPerLevel." + _cc) == str(_cv) and ("\\nmana.classPerLevel.%s=%s\\n" % (_cc, _cv)) in ("\\n" + CMAN_DEFAULTS), _cc   # 0.4.58: the 0.4.57 file
assert all(_dp.get("mana.classPerLevel." + _cc) == str(_cv) for _cc, _cv in P4_CLASS_MANA)   # 0.4.58 P4''')
P.rep('''assert all(_dp.get("stamina.classBase." + _c) == _v for _c, _v in P25_STA_BASE) and all(_dp.get("stamina.classPerLevel." + _c) == _v for _c, _v in P25_STA_PER)''',
      '''assert all(_dp57.get("stamina.classBase." + _c) == _v for _c, _v in P25_STA_BASE) and all(_dp57.get("stamina.classPerLevel." + _c) == _v for _c, _v in P25_STA_PER)   # 0.4.58: the 0.4.57 file
assert all(_dp.get("stamina.classBase." + _c) == _v for _c, _v in P4_STA_BASE) and all(_dp.get("stamina.classPerLevel." + _c) == _v for _c, _v in P4_STA_PER)   # 0.4.58 P4''')
P.rep('''for _k in ("combat.xpFrom", "mana.regen.perLevel", "mana.regen.fromLevel"):
    _rw = [_r for _r in CFG_ROWS if _r[0] == _k]
    assert len(_rw) == 1 and _dp.get(_k) == _rw[0][4] and ("\\n" + _k + "=" + _rw[0][4] + "\\n") in ("\\n" + KXP_DEFAULTS), _k''',
      '''for _k in ("combat.xpFrom", "mana.regen.perLevel", "mana.regen.fromLevel"):
    _rw = [_r for _r in CFG_ROWS if _r[0] == _k]
    assert len(_rw) == 1 and _dp.get(_k) == _rw[0][4] and ("\\n" + _k + "=" + _dp57[_k] + "\\n") in ("\\n" + KXP_DEFAULTS), _k   # 0.4.58: the KXP block holds the 0.4.57 value''')
P.rep('''    ("mana.regen.perLevel", "Mana regen per class level", "overall", "dec", KXP_PER_DEF, "0", "100", "", "%", "live",''',
      '''    ("mana.regen.perLevel", "Mana regen per class level", "overall", "dec", P4_PER_DEF, "0", "100", "", "%", "live",   # 0.4.58 P4: 5 -> 3''')

# ================================================================================================================ the Server Setup rows
P4ROWS = r'''# 0.4.58 (Balance P4): the class stat tables (Class Power), the Mana rows (Overall and Mana), the speed rows (Acrobatics)
P4_ROWS_POWER = [
    ("class.stats.enabled", "Class stats (role tuning)", "power", "bool", "true", "", "", "", "", "live",
     "On: each class gets its Health %, Defense, damage factor and speed below (Balance P4).", "reload"),
    ("class.healthPct", "Class Health %", "power", "table", "", "-50", "100", "dec;type;Health %", "", "live",
     "Percent more (or less) max Health of a class (Warrior 35, Mage -20).", "reload;check=ClassStat.checkEntry"),
    ("class.defense", "Class Defense", "power", "table", "", "0", "200", "dec;type;Defense", "", "live",
     "Defense of a class (hits x 100 / (100 + Defense), with gear Defense). Warrior 45.", "reload;check=ClassStat.checkEntry"),
    ("class.damage", "Class damage %", "power", "table", "", "10", "400", "dec;type;Damage %", "", "live",
     "Class weapon and ability hits on monsters x this % (100 = unchanged). Never on players.", "reload;check=ClassStat.checkEntry"),
]
P4_ROWS_MANA = [
    ("mana.regen.class", "Mana regen by class %", "overall", "table", "", "0", "400", "dec;type;Regen %", "", "live",
     "Percent of every Mana refill a class gets (100 = unchanged, Spellblade 50).", "reload;check=ClassStat.checkEntry"),
    ("mana.refillPct", "Quick refill % a second", "overall", "table", "", "0", "100", "dec;type;% of max", "", "live",
     "In combat once the bar ran dry: percent of max Mana a second until full (waits after each cast).", "reload;check=ClassStat.checkEntry"),
    ("mana.refillDelay", "Quick refill wait", "overall", "dec", "1", "0", "60", "", "s", "live",
     "Seconds after the last charged shot or ability before the quick refill starts.", "reload"),
    ("mana.refillBelow", "Quick refill starts below", "overall", "dec", _p4n(BM.P4_REFILL_BELOW), "0", "100", "", "%", "live",
     "The bar counts as dry under this percent of max Mana; the quick refill then runs until it is full.", "reload"),
]
P4_ROWS_MOVE = [
    ("class.speed", "Class speed %", "acrobatics", "table", "", "-50", "50", "dec;type;Speed %", "", "live",
     "Move speed of a class in a full set of its own armor (Monk / Assassin 12, Warrior -6).", "reload;check=ClassStat.checkEntry"),
    ("class.weight", "Class weight", "acrobatics", "table", "", "0", "10", "dec;type;Weight x", "", "live",
     "How much each armor load point slows a class (Warrior 0.25 ... Mage 2).", "reload;check=ClassStat.checkEntry"),
    ("class.armorLoad", "Class own armor load", "acrobatics", "table", "", "0", "10", "dec;type;Load", "", "live",
     "The load of a class's own full armor set (Cloth 0, Light 1, Heavy 3).", "reload;check=ClassStat.checkEntry"),
    ("armor.load.cloth", "Armor load: Cloth", "acrobatics", "dec", "0", "0", "10", "", "", "live", "Load of a full Cloth set.", "reload"),
    ("armor.load.light", "Armor load: Light", "acrobatics", "dec", "1", "0", "10", "", "", "live", "Load of a full Light set.", "reload"),
    ("armor.load.heavy", "Armor load: Heavy", "acrobatics", "dec", "3", "0", "10", "", "", "live", "Load of a full Heavy set.", "reload"),
    ("armor.slot.head", "Load share: helmet", "acrobatics", "dec", "0.2", "0", "1", "", "", "live,adv", "Part of a set's load a helmet carries.", "reload"),
    ("armor.slot.chest", "Load share: chest", "acrobatics", "dec", "0.35", "0", "1", "", "", "live,adv", "Part of a set's load a chestplate carries.", "reload"),
    ("armor.slot.hands", "Load share: gloves", "acrobatics", "dec", "0.15", "0", "1", "", "", "live,adv", "Part of a set's load gloves carry.", "reload"),
    ("armor.slot.legs", "Load share: legs", "acrobatics", "dec", "0.3", "0", "1", "", "", "live,adv", "Part of a set's load leggings carry.", "reload"),
    ("armor.perLoad", "Speed lost per load point", "acrobatics", "dec", "4", "0", "50", "", "%", "live",
     "Move speed lost per load point, x the class weight (4 = a Mage in Heavy is 24 % slower).", "reload"),
    ("move.maxFactor", "Most total move speed", "acrobatics", "dec", "1.8", "1", "5", "", "x", "live",
     "No mix of skills, trees, abilities and talismans moves a player faster than this.", "reload"),
]
_i58 = [_r[0] for _r in CFG_ROWS].index("classBoost.regen") + 1
CFG_ROWS[_i58:_i58] = P4_ROWS_POWER
_i58 = [_r[0] for _r in CFG_ROWS].index("mana.regen.show") + 1
CFG_ROWS[_i58:_i58] = P4_ROWS_MANA
_i58 = [_r[0] for _r in CFG_ROWS].index(G44_KEYS[-1]) + 1
CFG_ROWS[_i58:_i58] = P4_ROWS_MOVE
'''
P.rep('''# ================= 0.4.8 ManaCost / ManaMig / ManaGuard (tools/skills_0_4_8_patch.py points 1-3) =================''',
      '''# ================= 0.4.8 ManaCost / ManaMig / ManaGuard (tools/skills_0_4_8_patch.py points 1-3) =================''')
P.rep('''# defaults = today's behaviour: every scalar row's default equals the default xp.properties line; the rows absent from it are exactly the''',
      P4ROWS + '''# defaults = today's behaviour: every scalar row's default equals the default xp.properties line; the rows absent from it are exactly the''')
P.rep('''assert [_r[0] for _r in CFG_ROWS if _r[2] == "power"] == ["stamina.class.enabled", "stamina.classBase", "stamina.classPerLevel", "mana.onHit",
                                                         "mana.onHitCooldownMs", "mana.onHitVsPlayers", "classBoost.enabled"] + ["classBoost." + _st for _st in P25_BOOST_STATS]''',
      '''assert [_r[0] for _r in CFG_ROWS if _r[2] == "power"] == ["stamina.class.enabled", "stamina.classBase", "stamina.classPerLevel", "mana.onHit",
                                                         "mana.onHitCooldownMs", "mana.onHitVsPlayers", "classBoost.enabled"] + ["classBoost." + _st for _st in P25_BOOST_STATS] + [_r[0] for _r in P4_ROWS_POWER]   # 0.4.58''')
P.rep('''assert len(CFG_ROWS) == 285, ("0.4.57:''', '''assert len(CFG_ROWS) == 285 + len(P4_ROWS_POWER) + len(P4_ROWS_MANA) + len(P4_ROWS_MOVE), ("0.4.58: + the P4 rows (4 Class Power, 4 Mana, 12 speed); 0.4.57:''')
P.rep('''assert [_r[0] for _r in CFG_ROWS][-9:] == G43_KEYS + ["hp.regen.show"]''',
      '''assert [_r[0] for _r in CFG_ROWS][-9:] == G43_KEYS + ["hp.regen.show"]
# 0.4.58: every P4 row once, its default = the P4 block (scalars) / its table entries in the P4 block
for _r58 in P4_ROWS_POWER + P4_ROWS_MANA + P4_ROWS_MOVE:
    assert [_r[0] for _r in CFG_ROWS].count(_r58[0]) == 1, _r58[0]
    if _r58[3] == "table":
        assert any(_k.startswith(_r58[0] + ".") for _k, _v, _rr in P4_ADD), _r58[0]
    else:
        assert ("\\n%s=%s\\n" % (_r58[0], _r58[4])) in ("\\n" + P4_BLOCK) and _dp.get(_r58[0]) == _r58[4], _r58[0]''')

# ================================================================================================================ ClassStat part 1 (pure: tables, read)
CST1 = r'''# ================= 0.4.58 ClassStat part 1 (Balance P4): the class stat / speed / Mana tables + their read (SkillCfg.load) - pure, any thread =================
# T = Object[] of the 8 table snapshots {String[] classes, double[] values, String text} in P4_TABLES order: 0 healthPct, 1 defense, 2 damage,
# 3 speed, 4 weight, 5 armorLoad, 6 regen class, 7 refill pct (null = not read yet = the defaults). Scalars below. CAST = UUID -> Long (ms of
# the last charged shot / ability, skill:fn:manaregen {"cast", UUID}).
cst.addField(CtField.make("public static final String[] PREFIX = %s;" % jarr([_t + "." for _t, _d in P4_TABLES]), cst))
cst.addField(CtField.make("public static final double[] LO = new double[] { -50.0, 0.0, 10.0, -50.0, 0.0, 0.0, 0.0, 0.0 };", cst))
cst.addField(CtField.make("public static final double[] HI = new double[] { 100.0, 200.0, 400.0, 50.0, 10.0, 10.0, 400.0, 100.0 };", cst))
cst.addField(CtField.make("public static final double[] DFLT = new double[] { 0.0, 0.0, 100.0, 0.0, 1.0, 1.0, 100.0, 0.0 };", cst))   # an unlisted class
cst.addField(CtField.make('public static final String[] LABEL = new String[] { "Class Health %", "Class Defense", "Class damage %", "Class speed %", "Class weight", "Class own armor load", "Mana regen by class %", "Quick refill % a second" };', cst))
for _i, (_t, _d) in enumerate(P4_TABLES):
    cst.addField(CtField.make("public static final String[] DC%d = %s;" % (_i, jarr([_c for _c in P4_CLASSES if _c in _d])), cst))
    cst.addField(CtField.make("public static final double[] DV%d = new double[] { %s };" % (_i, ", ".join(repr(float(_d[_c])) for _c in P4_CLASSES if _c in _d)), cst))
for _d in ("public static volatile boolean ON = true;", "public static volatile Object[] T = null;", 'public static volatile String WARNED = "";',
           "public static volatile double LOAD_C = %s;" % repr(float(BM.P4_LOAD["Cloth"])), "public static volatile double LOAD_L = %s;" % repr(float(BM.P4_LOAD["Light"])),
           "public static volatile double LOAD_H = %s;" % repr(float(BM.P4_LOAD["Heavy"])),
           "public static volatile double SH_HEAD = %s;" % repr(BM.P4_SLOT["Head"]), "public static volatile double SH_CHEST = %s;" % repr(BM.P4_SLOT["Chest"]),
           "public static volatile double SH_HANDS = %s;" % repr(BM.P4_SLOT["Hands"]), "public static volatile double SH_LEGS = %s;" % repr(BM.P4_SLOT["Legs"]),
           "public static volatile double PER_LOAD = %s;" % repr(float(BM.P4_PER_LOAD)), "public static volatile double MAX_FACTOR = %s;" % repr(float(BM.P4_MAX_FACTOR)),
           "public static volatile double REFILL_DELAY = %s;" % repr(float(BM.P4_REFILL_DELAY)),
           "public static volatile double REFILL_BELOW = %s;" % repr(float(BM.P4_REFILL_BELOW)),
           "public static final java.util.concurrent.ConcurrentHashMap DRY = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap CAST = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",
           'public static final String KEY_HP = "skyyskill_classhp";', 'public static final String SOURCE = "skills.classweight";',
           'public static final String CAP_SOURCE = "skills.speedcap";', "public static boolean FAILED_ONCE = false;", "public static boolean MFAILED_ONCE = false;"):
    cst.addField(CtField.make(_d, cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static double[] defVals(int i) {
  if (i == 0) return DV0;
  if (i == 1) return DV1;
  if (i == 2) return DV2;
  if (i == 3) return DV3;
  if (i == 4) return DV4;
  if (i == 5) return DV5;
  if (i == 6) return DV6;
  return DV7;
}"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static String[] defCls(int i) {
  if (i == 0) return DC0;
  if (i == 1) return DC1;
  if (i == 2) return DC2;
  if (i == 3) return DC3;
  if (i == 4) return DC4;
  if (i == 5) return DC5;
  if (i == 6) return DC6;
  return DC7;
}"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static Object[] t(int i) {
  Object[] a = T;
  if (a == null) {
    a = new Object[PREFIX.length];
    for (int k = 0; k < a.length; k++) a[k] = @PKG@.OverallCfg.mkTable(defCls(k), defVals(k));
    T = a;
  }
  return (Object[]) a[i];
}"""), cst))
# ClassTbl.parse with a lower bound (the speed / Health % tables take negatives): {String[], double[], text, problems}
cst.addMethod(CtNewMethod.make(J14(r"""
public static Object[] parse(java.util.Properties p, String prefix, double lo, double hi) {
  java.util.ArrayList cs = new java.util.ArrayList();
  java.util.ArrayList bs = new java.util.ArrayList();
  StringBuilder bad = new StringBuilder();
  java.util.Iterator it = new java.util.TreeSet(p.stringPropertyNames()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith(prefix)) continue;
    String e = k.substring(prefix.length()).trim();
    String c = @PKG@.OverallCfg.canonClass(e);
    String raw = p.getProperty(k);
    String shown = e.length() > 40 ? e.substring(0, 40) + "..." : e;
    if (c == null) { if (bad.length() > 0) bad.append("; "); bad.append(shown + " is not a class (left out)"); continue; }
    if (cs.contains(c)) { if (bad.length() > 0) bad.append("; "); bad.append(c + " is listed twice (" + shown + " left out)"); continue; }
    double v = Double.NaN;
    try { v = Double.parseDouble(raw.trim()); } catch (Throwable t) { v = Double.NaN; }
    if (Double.isNaN(v) || Double.isInfinite(v)) { if (bad.length() > 0) bad.append("; "); bad.append(shown + " is not a number (left out)"); continue; }
    cs.add(c);
    bs.add(Double.valueOf(v < lo ? lo : (v > hi ? hi : v)));
  }
  String[] c2 = new String[cs.size()];
  double[] b2 = new double[cs.size()];
  for (int i = 0; i < c2.length; i++) { c2[i] = (String) cs.get(i); b2[i] = ((Double) bs.get(i)).doubleValue(); }
  Object[] t = @PKG@.OverallCfg.mkTable(c2, b2);
  return new Object[] { t[0], t[1], t[2], bad.toString() };
}"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static double clampD(double v, double d, double lo, double hi) {
  if (Double.isNaN(v) || Double.isInfinite(v)) return d;
  return v < lo ? lo : (v > hi ? hi : v);
}"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "class.stats.enabled", true);
  Object[] a = new Object[PREFIX.length];
  StringBuilder w = new StringBuilder();
  for (int i = 0; i < a.length; i++) {
    Object[] r = parse(p, PREFIX[i], LO[i], HI[i]);
    a[i] = new Object[] { r[0], r[1], r[2] };
    String bad = (String) r[3];
    if (bad.length() > 0) { if (w.length() > 0) w.append(" | "); w.append(LABEL[i]).append(": ").append(bad); }
  }
  T = a;
  LOAD_C = clampD(@PKG@.SkillCfg.dbl(p, "armor.load.cloth", @LC@), @LC@, 0.0, 10.0);
  LOAD_L = clampD(@PKG@.SkillCfg.dbl(p, "armor.load.light", @LL@), @LL@, 0.0, 10.0);
  LOAD_H = clampD(@PKG@.SkillCfg.dbl(p, "armor.load.heavy", @LH@), @LH@, 0.0, 10.0);
  SH_HEAD = clampD(@PKG@.SkillCfg.dbl(p, "armor.slot.head", @SHH@), @SHH@, 0.0, 1.0);
  SH_CHEST = clampD(@PKG@.SkillCfg.dbl(p, "armor.slot.chest", @SHC@), @SHC@, 0.0, 1.0);
  SH_HANDS = clampD(@PKG@.SkillCfg.dbl(p, "armor.slot.hands", @SHG@), @SHG@, 0.0, 1.0);
  SH_LEGS = clampD(@PKG@.SkillCfg.dbl(p, "armor.slot.legs", @SHL@), @SHL@, 0.0, 1.0);
  PER_LOAD = clampD(@PKG@.SkillCfg.dbl(p, "armor.perLoad", @PLD@), @PLD@, 0.0, 50.0);
  MAX_FACTOR = clampD(@PKG@.SkillCfg.dbl(p, "move.maxFactor", @MXF@), @MXF@, 1.0, 5.0);
  REFILL_DELAY = clampD(@PKG@.SkillCfg.dbl(p, "mana.refillDelay", @RFD@), @RFD@, 0.0, 60.0);
  REFILL_BELOW = clampD(@PKG@.SkillCfg.dbl(p, "mana.refillBelow", @RFB@), @RFB@, 0.0, 100.0);
  String ws = w.toString();
  if (ws.length() > 0 && !ws.equals(WARNED)) @PKG@.SkillCfg.warn(ws);
  WARNED = ws;
}""".replace("@LC@", repr(float(BM.P4_LOAD["Cloth"]))).replace("@LL@", repr(float(BM.P4_LOAD["Light"]))).replace("@LH@", repr(float(BM.P4_LOAD["Heavy"])))
   .replace("@SHH@", repr(BM.P4_SLOT["Head"])).replace("@SHC@", repr(BM.P4_SLOT["Chest"])).replace("@SHG@", repr(BM.P4_SLOT["Hands"])).replace("@SHL@", repr(BM.P4_SLOT["Legs"]))
   .replace("@PLD@", repr(float(BM.P4_PER_LOAD))).replace("@MXF@", repr(float(BM.P4_MAX_FACTOR))).replace("@RFD@", repr(float(BM.P4_REFILL_DELAY))).replace("@RFB@", repr(float(BM.P4_REFILL_BELOW)))), cst))
# table i's value for a class: its entry, else the unlisted default (DFLT)
cst.addMethod(CtNewMethod.make(J14(r"""
public static double of(int i, String cls) {
  if (cls == null) return DFLT[i];
  Object[] t = t(i);
  String[] c = (String[]) t[0];
  double[] b = (double[]) t[1];
  for (int k = 0; k < c.length && k < b.length; k++) if (c[k].equalsIgnoreCase(cls.trim())) return b[k];
  return DFLT[i];
}"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static double healthPct(String cls) { return ON ? of(0, cls) : 0.0; }"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static double defenseOf(String cls) { return ON ? of(1, cls) : 0.0; }"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static double damageOf(String cls) { return ON ? of(2, cls) / 100.0 : 1.0; }"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static double regenOf(String cls) { return of(6, cls) / 100.0; }"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static double refillOf(String cls) { return of(7, cls) / 100.0; }"""), cst))
# the type load of a SkyyGear weight answer (1 Heavy, 2 Light, 3 Cloth); -1 = unknown
cst.addMethod(CtNewMethod.make(J14(r"""
public static double typeLoad(int w) {
  if (w == 1) return LOAD_H;
  if (w == 2) return LOAD_L;
  if (w == 3) return LOAD_C;
  return -1.0;
}"""), cst))
# the slot share of armor container slot s (the engine's ItemArmorSlot order: Head, Chest, Hands, Legs)
cst.addMethod(CtNewMethod.make(J14(r"""
public static double share(int s) {
  if (s == 0) return SH_HEAD;
  if (s == 1) return SH_CHEST;
  if (s == 2) return SH_HANDS;
  if (s == 3) return SH_LEGS;
  return 0.0;
}"""), cst))
# THE speed rule (pure): speed % of a class at a worn load (load < 0 = unknown -> its own armor = the rated speed)
cst.addMethod(CtNewMethod.make(J14(r"""
public static double speedPct(String cls, double load) {
  if (!ON || cls == null) return 0.0;
  double sp = of(3, cls), w = of(4, cls), nat = of(5, cls);
  double l = load < 0.0 ? nat : load;
  return sp + PER_LOAD * (nat - l) * w;
}"""), cst))
# the speedcap source's pct (pure): the pct that brings (1 + flat) (1 + pct) down to MAX_FACTOR (0 = none needed)
cst.addMethod(CtNewMethod.make(J14(r"""
public static double capPct(double flat, double pct) {
  double f = (1.0 + flat) * (1.0 + pct);
  if (!(f > MAX_FACTOR) || !(1.0 + flat > 0.0)) return 0.0;
  return MAX_FACTOR / (1.0 + flat) - 1.0 - pct;
}"""), cst))
# the quick refill amount (pure): Mana added this pulse (in combat, the delay passed since the last cast, room left)
cst.addMethod(CtNewMethod.make(J14(r"""
public static double refill(double pct, float max, float cur, float secs, long sinceCast, boolean fight, boolean dry) {
  if (!fight || !dry || !(pct > 0.0) || !(max > 0.0f) || !(cur < max) || !(secs > 0.0f)) return 0.0;
  if (sinceCast >= 0L && (double) sinceCast < REFILL_DELAY * 1000.0) return 0.0;
  double a = (double) max * pct * (double) secs;
  double room = (double) (max - cur);
  return a > room ? room : a;
}"""), cst))
# the DRY latch (build re-tune, balance_model P4_REFILL_BELOW): on once the bar is under REFILL_BELOW % of max, off once it is full again -
# the quick refill only runs while it is on (so it never stretches the 20-30 s of casting before the bar runs dry)
cst.addMethod(CtNewMethod.make(J14(r"""
public static boolean dryNow(boolean was, float max, float cur) {
  if (!(max > 0.0f) || cur >= max - 0.01f) return false;
  if ((double) cur < (double) max * REFILL_BELOW / 100.0) return true;
  return was;
}"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static boolean dry(java.util.UUID u, float max, float cur) {
  if (u == null) return false;
  boolean d = dryNow(DRY.containsKey(u), max, cur);
  if (d) DRY.put(u, Boolean.TRUE);
  else DRY.remove(u);
  return d;
}"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static void cast(java.util.UUID u, long now) { if (u != null) CAST.put(u, Long.valueOf(now)); }"""), cst))
# fix round (critic): a profile switch (Perks.switched) starts the new profile without the old one's dry latch / last cast / speed pct
cst.addMethod(CtNewMethod.make(J14(r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  DRY.remove(u);
  CAST.remove(u);
  LAST.remove(u);
}"""), cst))
# the class regen share (pure; k = regenOf): k 1 = a unchanged; k < 1 = a x k + (k - 1) x what vanilla's own refill can still add this
# pulse (its rate x secs, at most the room left) - fix round (critic): never more, so a k 0.5 bar still reaches full
cst.addMethod(CtNewMethod.make(J14(r"""
public static double share(double a, double rate, double secs, double k, float max, float cur) {
  if (k == 1.0) return a;
  double van = rate * secs;
  double room = (double) (max - cur);
  if (van > room) van = room;
  if (van < 0.0) van = 0.0;
  return a * k + van * (k - 1.0);
}"""), cst))
# CombatDmgSys (pure, fix round): the class damage factor only on WEAPON hits - a SkyyClasses ability hit cast by this player = 1
cst.addMethod(CtNewMethod.make(J14(r"""
public static double weaponOnly(double cf, java.util.UUID caster, java.util.UUID u) {
  if (caster != null && u != null && caster.equals(u)) return 1.0;
  return cf;
}"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static long sinceCast(java.util.UUID u, long now) {
  Object o = u == null ? null : CAST.get(u);
  return o instanceof Long ? now - ((Long) o).longValue() : -1L;
}"""), cst))
# check= hook of every P4 class table (the entry must be a class; the bounds are the row's own)
cst.addMethod(CtNewMethod.make(J14(r"""
public static String checkEntry(String key, String value) {
  return @PKG@.ClassTbl.checkEntry(key, value);
}"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  if (!ON) return "class stats off";
  return "class stats on (Health % " + (String) t(0)[2] + "; damage % " + (String) t(2)[2] + "; speed % " + (String) t(3)[2] + "), most move speed x" + MAX_FACTOR;
}"""), cst))
'''
P.rep('''# ManaHit part 1: mana.onHit.<Class> (Mana a landed class weapon hit gives back), mana.onHitCooldownMs, mana.onHitVsPlayers''',
      CST1 + '''# ManaHit part 1: mana.onHit.<Class> (Mana a landed class weapon hit gives back), mana.onHitCooldownMs, mana.onHitVsPlayers''')
P.rep('''    {PKG}.ClassPower.read(p);   // 0.4.25: class Stamina + the class balance tables''',
      '''    {PKG}.ClassPower.read(p);   // 0.4.25: class Stamina + the class balance tables
    {PKG}.ClassStat.read(p);    // 0.4.58 Balance P4: class Health / Defense / damage / speed / weight + the Mana refill rows''')

# ================================================================================================================ ClassStat part 2 (Health %, Defense)
CST2 = r'''# ================= 0.4.58 ClassStat part 2: the class Health percent layer + Defense of the active profile's class (Perks.tick, world thread) =================
# the percent layer's base = the stat's own max + every ADDITIVE max modifier except the percent layers (ours, SkyyRebirth's RbStat keys,
# SkyyAccessories' skyyacc_*): EntityStatValue.computeModifiers SUMS multiplicative amounts (bytecode, asserted below), so an additive
# amount = pct x that base is exactly pct percent of the flat max; ours never reads SkyyRebirth's / SkyyAccessories' percent and RbStat skips
# ours, but SkyyAccessories' own flatMax (0.5.29) skips only its own key, so its Health percent is taken on top of the class percent (one way,
# the same as skyyskill_rebirthhp today)
cst.addMethod(CtNewMethod.make(J14(r"""
public static boolean skip(Object k) {
  if (!(k instanceof String)) return true;
  String s = (String) k;
  return s.equals(KEY_HP) || s.startsWith("skyyacc_") || @PKG@.RbStat.skip(k);
}"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static float flatMax(@ESV@ v, int idx) {
  float base = @PKG@.Overall.typeMax(idx);
  java.util.Map mods = v.getModifiers();
  if (mods == null) return base;
  java.util.Iterator it = mods.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    if (skip(k)) continue;
    Object o = mods.get(k);
    if (!(o instanceof @SMO@)) continue;
    @SMO@ sm = (@SMO@) o;
    if (sm.getTarget() != @MTG@.MAX || sm.getCalculationType() != @CAL@.ADDITIVE) continue;
    base = base + sm.getAmount();
  }
  return base;
}"""), cst))
# the amount (pure): flat x pct / 100, rounded to 0.01; negatives allowed (Mage -20 %); 0 = nothing
cst.addMethod(CtNewMethod.make(J14(r"""
public static float amount(float flat, double pct) {
  if (pct == 0.0 || !(flat > 0.0f)) return 0.0f;
  return (float) Math.round((double) flat * pct) / 100.0f;
}"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static void health(java.util.UUID u, @ESM@ m) {
  if (m == null || u == null) return;
  try {
    int idx = @DST@.getHealth();
    @ESV@ v = m.get(idx);
    if (v == null) return;
    float amt = amount(flatMax(v, idx), healthPct(@PKG@.Overall.classOf(u)));
    @MOD@ cur = m.getModifier(idx, KEY_HP);
    if (amt == 0.0f) { if (cur != null) m.removeModifier(idx, KEY_HP); return; }
    @SMO@ want = new @SMO@(@MTG@.MAX, @CAL@.ADDITIVE, amt);
    if (cur != null && cur.equals(want)) return;
    m.putModifier(idx, KEY_HP, want);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("class Health percent failed (logged once): " + t); }
  }
}"""), cst))
cst.addMethod(CtNewMethod.make(J14(r"""
public static double defense(java.util.UUID u) {
  try { return defenseOf(@PKG@.Overall.classOf(u)); } catch (Throwable t) { return 0.0; }
}"""), cst))
# CombatDmgSys: the class damage factor (1 = none) of the class of this class skill slot
cst.addMethod(CtNewMethod.make(J14(r"""
public static double dmgFactor(int slot) {
  if (!ON || !@PKG@.SkillDefs.isClass(slot)) return 1.0;
  int ci = @PKG@.SkillDefs.classIdx(slot);
  if (ci < 0 || ci >= @PKG@.SkillDefs.CLASSES.length) return 1.0;
  return damageOf(@PKG@.SkillDefs.CLASSES[ci]);
}"""), cst))
# ManaRegen: the class regen share + quick refill pct of the player's current class (SkillClass.slot, memory only, any thread)
cst.addMethod(CtNewMethod.make(J14(r"""
public static String clsOf(java.util.UUID u) {
  try {
    int s = @PKG@.SkillClass.slot(u);
    if (s < 0 || !@PKG@.SkillDefs.isClass(s)) return null;
    return @PKG@.SkillDefs.CLASSES[@PKG@.SkillDefs.classIdx(s)];
  } catch (Throwable t) { return null; }
}"""), cst))
'''
P.rep('''# ---- ManaHit part 2: a landed class weapon hit queues Mana (ManaHitSys, Inspect group); AcroSys adds it on the world thread''',
      CST2 + '''# ---- ManaHit part 2: a landed class weapon hit queues Mana (ManaHitSys, Inspect group); AcroSys adds it on the world thread''')
P.rep('''    {PKG}.SkillDef.set(u, (double) total({PKG}.PerkCfg.DEF, lv) + {PKG}.ClassPower.boostDef(u, {PKG}.SkillStore.data(u)));   // 0.4.25: skill Defense''',
      '''    {PKG}.SkillDef.set(u, (double) total({PKG}.PerkCfg.DEF, lv) + {PKG}.ClassPower.boostDef(u, {PKG}.SkillStore.data(u)) + {PKG}.ClassStat.defense(u));   // 0.4.25: skill Defense; 0.4.58: + the class Defense''')
P.rep('''    {PKG}.RbStat.tick(u, m);   // 0.4.39: SkyyRebirth's stat boosts on max Health / Mana / Stamina''',
      '''    {PKG}.RbStat.tick(u, m);   // 0.4.39: SkyyRebirth's stat boosts on max Health / Mana / Stamina
    {PKG}.ClassStat.health(u, m);   // 0.4.58 Balance P4: the class Health percent (an additive layer, after the flat ones)''')
P.rep('''  return s.equals(KH) || s.equals(KM) || s.equals(KS) || s.startsWith("skyyacc_");
}"""), rbs39))''', '''  return s.equals(KH) || s.equals(KM) || s.equals(KS) || s.startsWith("skyyacc_") || s.equals("skyyskill_classhp");   // 0.4.58: + the class Health layer
}"""), rbs39))''')

# ================================================================================================================ the EntityStatValue probe (build time)
P.rep('''print("0.4.37 engine checks: FilterUnkillable cancels invulnerable damage (Filter group), pickups add a PickupItemComponent entity, throwItem "
      "fires DropItemEvent$Drop, effect durations readable")''', '''print("0.4.37 engine checks: FilterUnkillable cancels invulnerable damage (Filter group), pickups add a PickupItemComponent entity, throwItem "
      "fires DropItemEvent$Drop, effect durations readable")
# 0.4.58 (Balance P4 6.8 "probe it"): EntityStatValue.computeModifiers = (asset max + SUM of the ADDITIVE amounts) then x (SUM of the MULTIPLICATIVE
# amounts) - so the class Health percent must be an ADDITIVE amount of pct x (base + the other additives), never a multiplicative one
_cm58 = " ".join(_bc37("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue", "computeModifiers"))
assert _cm58.count("fadd") >= 2 and "CalculationType.ADDITIVE" in _cm58 and "CalculationType.MULTIPLICATIVE" in _cm58 \\
    and _cm58.index("fadd") < _cm58.index("CalculationType.ADDITIVE") < _cm58.index("CalculationType.MULTIPLICATIVE") and "CalculationType.compute" in _cm58, \\
    "EntityStatValue.computeModifiers no longer sums additive then multiplicative amounts - re-check ClassStat.health (the class Health percent)"
print("0.4.58 engine check: computeModifiers sums the ADDITIVE amounts, then the MULTIPLICATIVE ones (a percent layer must be additive)")''')

# ================================================================================================================ CombatDmgSys: the class damage factor
P.rep('''    if (!({PKG}.PerkCfg.ENABLED && {PKG}.PerkCfg.DMG > 0.0) && !{PKG}.ClassPower.B_ON) return;   // 0.4.25: or the class balance
    Object src = d.getSource();''', '''    boolean perkOn = ({PKG}.PerkCfg.ENABLED && {PKG}.PerkCfg.DMG > 0.0) || {PKG}.ClassPower.B_ON;   // 0.4.25: or the class balance
    if (!perkOn && !{PKG}.ClassStat.ON) return;   // 0.4.58: or the class damage factor
    Object src = d.getSource();''')
P.rep('''    if (!{PKG}.PerkCfg.DMG_PVP) {{
      {REF} tr = chunk.getReferenceTo(idx);
      if (tr != null && st.getComponent(tr, {PR}.getComponentType()) != null) return;
    }}
    java.util.UUID u = pr.getUuid();''', '''    {REF} tr = chunk.getReferenceTo(idx);
    boolean pvp = tr != null && st.getComponent(tr, {PR}.getComponentType()) != null;   // 0.4.58: the class factor never applies vs players
    if (pvp && !{PKG}.PerkCfg.DMG_PVP) return;
    java.util.UUID u = pr.getUuid();''')
P.rep('''    double bonus = {PKG}.Perks.damage(clv) + {PKG}.ClassPower.boostDmg(slot, clv);   // 0.4.25: + the class balance damage % (one multiplication)
    if (bonus <= 0.0) return;''', '''    double bonus = perkOn ? {PKG}.Perks.damage(clv) + {PKG}.ClassPower.boostDmg(slot, clv) : 0.0;   // 0.4.25: + the class balance damage % (one multiplication)
    double cf = pvp ? 1.0 : {PKG}.ClassStat.dmgFactor(slot);   // 0.4.58 Balance P4: the class damage factor (monsters only)
    if (bonus <= 0.0 && cf == 1.0) return;''')
P.rep('''    d.setAmount((float) (a * (1.0 + bonus)));
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("combat damage perk failed (logged once): " + t); }}''',
      '''    cf = {PKG}.ClassStat.weaponOnly(cf, {PKG}.SkillClass.abilCaster(d), u);   // fix round (spec 2.4): no class factor on an ability hit
    d.setAmount((float) (a * (1.0 + (bonus > 0.0 ? bonus : 0.0)) * cf));   // 0.4.58: x the class damage factor
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("combat damage perk failed (logged once): " + t); }}''')

# fix round (critic, PROFILES-CONTRACT rule 2): a profile switch forgets the old profile's Mana dry latch / last cast / class speed pct
P.rep('''  {PKG}.ManaHit.forget(u);   // 0.4.25: Mana on hit queued / timed for the old profile
}}""", perk))''', '''  {PKG}.ManaHit.forget(u);   // 0.4.25: Mana on hit queued / timed for the old profile
  {PKG}.ClassStat.forget(u);   // 0.4.58 fix round: the old profile's Mana dry latch / last cast / class speed pct
}}""", perk))''')

# ================================================================================================================ ManaRegen: class regen share + quick refill; the "cast" verb
P.rep('''    if (!(max > 0.0f) || !(cur < max)) return;
    float a = amount(rates(cb, ref, now, rv), pct, f, secs, cur, max);   // 0.4.13: + what vanilla withholds while charging
    if (a > 0.0f) m.addStatValue(mi, a);''', '''    boolean dry58 = {PKG}.ClassStat.dry(u, max, cur);   // build re-tune: the quick refill only once the bar ran dry, until full (fix round: before the full-bar return, so a full bar clears it)
    if (!(max > 0.0f) || !(cur < max)) return;
    float[] rr = rates(cb, ref, now, rv);
    float a = amount(rr, pct, f, secs, cur, max);   // 0.4.13: + what vanilla withholds while charging
    String cls58 = {PKG}.ClassStat.clsOf(u);   // 0.4.58 Balance P4: the class regen share (Spellblade 50 %) + the quick refill
    double k58 = {PKG}.ClassStat.regenOf(cls58);
    double d58 = {PKG}.ClassStat.share((double) a, (double) rr[1], (double) secs, k58, max, cur);   // < 1: + (k - 1) x what vanilla's own refill can still add
    long wall = System.currentTimeMillis();
    d58 = d58 + {PKG}.ClassStat.refill({PKG}.ClassStat.refillOf(cls58), max, cur, secs, {PKG}.ClassStat.sinceCast(u, wall), combatNow(u, wall) > 0L, dry58);
    if (d58 > 0.0) {{ double room = (double) (max - cur); m.addStatValue(mi, (float) (d58 > room ? room : d58)); }}
    else if (d58 < 0.0) {{ double back = -d58 > (double) cur ? (double) cur : -d58; if (back > 0.0) m.subtractStatValue(mi, (float) back); }}''')
P.rep('''    if (op.equals("get")) return Double.valueOf({PKG}.ManaRegen.total(u));''', '''    if (op.equals("cast")) {{   // 0.4.58 Balance P4: {{"cast", UUID}} - a charged shot / ability now (the quick refill waits mana.refillDelay)
      if (u == null) return Boolean.FALSE;
      {PKG}.ClassStat.cast(u, System.currentTimeMillis());
      return Boolean.TRUE;
    }}
    if (op.equals("get")) return Double.valueOf({PKG}.ManaRegen.total(u));''')
P.rep('''#   {"clear", String source} -> Integer                     that source removed from every player''',
      '''#   {"clear", String source} -> Integer                     that source removed from every player
#   {"cast", UUID} -> Boolean                               0.4.58: a charged shot / ability now (restarts the quick refill wait)''')

# ================================================================================================================ the speed source (Acro.bonuses)
CST3 = r'''# 0.4.58 ClassStat part 3 (Balance P4 2.3): the worn armor load + the class speed source + the speed ceiling, once a second (Acro.bonuses,
# world thread, right before MoveSync.sync). The load: armor slot s (Head, Chest, Hands, Legs) x its share x the type load of SkyyGear's
# gear:fn:weight answer; no SkyyGear (or an answer it cannot give) = -1 = the class's own armor (the rated speed)
cst.addMethod(CtNewMethod.make(f"""
public static double load({CB} cb, {REF} ref) {{
  Object f = {PKG}.SkillStore.bridge().get("gear:fn:weight");
  if (!(f instanceof java.util.function.Function)) return -1.0;
  {PLA} p = ({PLA}) cb.getComponent(ref, {PLA}.getComponentType());
  if (p == null || p.getInventory() == null) return -1.0;
  {ICON} c = p.getInventory().getArmor();
  if (c == null) return -1.0;
  double sum = 0.0;
  int cap = c.getCapacity();
  for (int s = 0; s < cap && s < 4; s++) {{
    {IS} is = c.getItemStack((short) s);
    if (is == null || is.isEmpty() || is.getItemId() == null) continue;
    Object w = ((java.util.function.Function) f).apply(is.getItemId());
    if (!(w instanceof Number)) return -1.0;
    double tl = typeLoad(((Number) w).intValue());
    if (tl < 0.0) return -1.0;
    sum = sum + share(s) * tl;
  }}
  return sum;
}}""", cst))
# the posting half (any thread with the protocol map; the harness drives it): the class source, then the ceiling source from every OTHER
# source's flat / pct speed (MoveSync's own sums, the cap source left out)
cst.addMethod(CtNewMethod.make(f"""
public static void post(java.util.UUID u, String cls, double load) {{
    double pct = (ON && cls != null) ? speedPct(cls, load) : 0.0;
    LAST.put(u, Double.valueOf(pct));
    {PKG}.MoveSync.post(u, SOURCE, "flat", (float) (pct / 100.0), 0.0f, 0.0f);
    float flat = 0.0f, pc = 0.0f;
    java.util.Map m = {PKG}.MoveSync.sources(u, false);
    if (m != null) {{
      java.util.Iterator it = m.entrySet().iterator();
      while (it.hasNext()) {{
        java.util.Map.Entry e = (java.util.Map.Entry) it.next();
        if (CAP_SOURCE.equals(e.getKey()) || !(e.getValue() instanceof java.util.Map)) continue;
        java.util.Map en = (java.util.Map) e.getValue();
        if ("pct".equals(en.get("layer"))) pc = pc + {PKG}.MoveSync.num(en.get("speed"));
        else flat = flat + {PKG}.MoveSync.num(en.get("speed"));
      }}
    }}
    {PKG}.MoveSync.post(u, CAP_SOURCE, "pct", (float) capPct((double) flat, (double) pc), 0.0f, 0.0f);
}}""", cst))
cst.addMethod(CtNewMethod.make(f"""
public static void move(java.util.UUID u, {CB} cb, {REF} ref) {{
  try {{
    String cls = {PKG}.Overall.classOf(u);
    post(u, cls, (ON && cls != null) ? load(cb, ref) : -1.0);
  }} catch (Throwable t) {{
    if (!MFAILED_ONCE) {{ MFAILED_ONCE = true; {PKG}.SkillCfg.warn("class speed (skills.classweight) failed (logged once): " + t); }}
  }}
}}""", cst))
'''
P.rep('''# once per second: publish this player's Acrobatics bonus (flat layer) and apply the protocol total''',
      CST3 + '''# once per second: publish this player's Acrobatics bonus (flat layer) and apply the protocol total''')
P.rep('''  {PKG}.MoveSync.post(u, SOURCE, "flat", (float) speedBonus(lvl), (float) jumpBonus(lvl), (float) (0.0 - fallBonus(lvl)));
  {PKG}.MoveSync.sync(u, pr, cb, ref, MOVE, MOD);''', '''  {PKG}.MoveSync.post(u, SOURCE, "flat", (float) speedBonus(lvl), (float) jumpBonus(lvl), (float) (0.0 - fallBonus(lvl)));
  {PKG}.ClassStat.move(u, cb, ref);   // 0.4.58 Balance P4: the class weight x armor speed source + the speed ceiling (before the sync)
  {PKG}.MoveSync.sync(u, pr, cb, ref, MOVE, MOD);''')

# ================================================================================================================ P4Mig (P3Mig's machinery, copied)
P.rep('''p3m = pool.makeClass(PKG + ".P3Mig")           # 0.4.57: the one-time Balance P3 update of an existing xp.properties (spec 6.1)''',
      '''p3m = pool.makeClass(PKG + ".P3Mig")           # 0.4.57: the one-time Balance P3 update of an existing xp.properties (spec 6.1)
cst = pool.makeClass(PKG + ".ClassStat")       # 0.4.58: Balance P4 - class Health / Defense / damage / speed / weight + the Mana refill
p4m = pool.makeClass(PKG + ".P4Mig")           # 0.4.58: the one-time Balance P4 update of an existing xp.properties''')


def _p3m(name):
    a = P.s.index('p3m.addMethod(CtNewMethod.make(J14(r"""\npublic static ' + name)
    b = P.s.index('"""), p3m))', a)
    return P.s[a + len('p3m.addMethod(CtNewMethod.make(J14(r"""'):b]


_IDX, _PLAN, _SAME, _RUN = _p3m("int idx("), _p3m("Object[] plan("), _p3m("boolean sameAfter("), _p3m("synchronized String run()")
_OLD = '''public static boolean oldHit(int i, String v) {
  return v != null && i >= 0 && i < OLDS.length && OLDS[i].equals(v);
}'''
_PLAN = _PLAN.replace("oldHit(", "oldHit(")
_PLAN = _PLAN.replace('''the 0.4.57 default has no such line (its skill keeps this list and its saved XP is not moved)" : "the 0.4.57 default is "''',
                      '''the 0.4.58 default has no such line" : "the 0.4.58 (Balance P4) default is "''')
assert "0.4.57" not in _PLAN, _PLAN
_RUN = _RUN.replace('''      @PKG@.CfgLog.enqueue(@PKG@.RbCoinMig.logLine(rows[i], rows[i + 1], rows[i + 2]).replace(@PKG@.RbCoinMig.WHO, rows[i].startsWith("levels") ? WHO_LV : WHO));   // fix round: the level rows point at curve-p3.log (fix 2: short - the Changes page clips at 110)''',
                    '''      @PKG@.CfgLog.enqueue(@PKG@.RbCoinMig.logLine(rows[i], rows[i + 1], rows[i + 2]).replace(@PKG@.RbCoinMig.WHO, WHO));''')
_RUN = _RUN.replace("xp.properties NOT updated for 0.4.57 (Balance P3)", "xp.properties NOT updated for 0.4.58 (Balance P4)").replace(
    '"before the 0.4.57 Balance P3 update"', '"before the 0.4.58 Balance P4 update"').replace(
    '"xp.properties updated for 0.4.57 (Balance P3: one level list, XP per action x tier, catch-up, past-life XP): "',
    '"xp.properties updated for 0.4.58 (Balance P4: class stats, speed, Stamina, Mana pools, regen + quick refill): "').replace(
    '"could not update xp.properties for 0.4.57 (Balance P3; the file is used as it is): "', '"could not update xp.properties for 0.4.58 (Balance P4; the file is used as it is): "')
assert "0.4.57" not in _RUN and "P3" not in _RUN and "WHO_LV" not in _RUN, _RUN
P4MIG = r'''# ---- P4Mig (0.4.58, PROJECT-RULES section 4; P3Mig's reviewed machinery, copied): ONCE on an EXISTING xp.properties, setup() right after the P3
# updates, BEFORE SkillCfg.load. Each P4 key whose LAST entry is a one-line entry holding exactly its 0.4.57 default (OLDS) -> NEWS; any other
# value kept (INFO). Then ONE block in the file's own line ending: HEAD + the ADDK lines the file lacks + the marker. config-history copy
# first (verified), one config-changes.log row per change (Undo; table entries as table[entry]), Properties check, atomicWrite. A failure =
# WARN, file untouched, retried next start.
p4m.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(P4_MARK_ID), p4m))
p4m.addField(CtField.make("public static final String MARK = %s;" % json.dumps(P4_MARK), p4m))
p4m.addField(CtField.make("public static final String HEAD = %s;" % json.dumps("\n".join(P4_HEAD) + "\n"), p4m))
p4m.addField(CtField.make("public static final String[] KEYS = %s;" % jarr([_e[0] for _e in P4_KEYS]), p4m))
p4m.addField(CtField.make("public static final String[] OLDS = %s;" % jarr([_e[1] for _e in P4_KEYS]), p4m))
p4m.addField(CtField.make("public static final String[] NEWS = %s;" % jarr([_e[2] for _e in P4_KEYS]), p4m))
p4m.addField(CtField.make("public static final String[] ROWK = %s;" % jarr([_e[3] for _e in P4_KEYS]), p4m))
p4m.addField(CtField.make("public static final String[] ADDK = %s;" % jarr([_e[0] for _e in P4_ADD]), p4m))
p4m.addField(CtField.make("public static final String[] ADDV = %s;" % jarr([_e[1] for _e in P4_ADD]), p4m))
p4m.addField(CtField.make("public static final String[] ADDR = %s;" % jarr([_e[2] for _e in P4_ADD]), p4m))
p4m.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.58";', p4m))
p4m.addMethod(CtNewMethod.make(J14(r"""''' + _IDX + r'''"""), p4m))
p4m.addMethod(CtNewMethod.make(J14(r"""
public static boolean oldHit(int i, String v) {
  return v != null && i >= 0 && i < OLDS.length && OLDS[i].equals(v);
}"""), p4m))
p4m.addMethod(CtNewMethod.make(J14(r"""''' + _PLAN + r'''"""), p4m))
p4m.addMethod(CtNewMethod.make(J14(r"""''' + _SAME + r'''"""), p4m))
p4m.addMethod(CtNewMethod.make(J14(r"""''' + _RUN + r'''"""), p4m))

'''
P.rep('''# ---- CurveP3Mig (0.4.57, spec 6.2, PROJECT-RULES section 4): ONCE, setup() right after Xp56Mig.run, BEFORE P3Mig (which only runs once this''',
      P4MIG + '''# ---- CurveP3Mig (0.4.57, spec 6.2, PROJECT-RULES section 4): ONCE, setup() right after Xp56Mig.run, BEFORE P3Mig (which only runs once this''')
P.rep('''  if ({PKG}.CurveP3Mig.run(base)) {{ {PKG}.P3Mig.run(); {PKG}.CurveP3Mig.after(base); }}''',
      '''  if ({PKG}.CurveP3Mig.run(base)) {{ {PKG}.P3Mig.run(); {PKG}.CurveP3Mig.after(base); }}
  {PKG}.P4Mig.run();          // 0.4.58 Balance P4: untouched class Mana / Stamina / regen defaults + the new P4 rows, once; History first''')
P.rep("rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, mn52, nc53, fa53, en54, xp56, sv3, p3x, p3m, cp3, lvf,",
      "rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, mn52, nc53, fa53, en54, xp56, sv3, p3x, p3m, cp3, cst, p4m, lvf,")

P.rep('''assert DEFAULTS.count(P3_MARK_ID) == 1 and DEFAULTS.endswith(P3_BLOCK) and _dp.get("levels.class.sameAsOthers") == "true"   # 0.4.57''',
      '''assert DEFAULTS_057.count(P3_MARK_ID) == 1 and DEFAULTS_057.endswith(P3_BLOCK) and _dp57.get("levels.class.sameAsOthers") == "true"   # 0.4.57 (0.4.58: the 0.4.57 file)
assert DEFAULTS.count(P3_MARK_ID) == 1 and DEFAULTS.endswith(P4_BLOCK) and DEFAULTS.count(P4_MARK_ID) == 1   # 0.4.58''')
P.rep(r'''assert all(("\n" + _k + "=" + _n + "\n") in ("\n" + DEFAULTS) for _k, _o, _n in _PRW), "a rewrite's new value is not the default file's"''',
      r'''assert all(("\n" + _k + "=" + _n + "\n") in ("\n" + DEFAULTS_057) for _k, _o, _n in _PRW), "a rewrite's new value is not the default file's"   # 0.4.58: the 0.4.57 file (P4Mig moves Mage / Priest after it)''')
P.rep(r'''assert all(("\n" + _a[0] + "=" + _a[1] + "\n") in ("\n" + DEFAULTS) for _a in _PADD), "an added line is not the default file's"''',
      r'''assert all(("\n" + _a[0] + "=" + _a[1] + "\n") in ("\n" + DEFAULTS_057) for _a in _PADD), "an added line is not the default file's"   # 0.4.58: the 0.4.57 file''')
P.rep(r'''assert all(("\n" + DEFAULTS).count("\n%s=%s\n" % (_k, _n)) == 1 for _k, _o, _n in MN52_KEYS)''',
      r'''assert all(("\n" + DEFAULTS_057).count("\n%s=%s\n" % (_k, _n)) == 1 for _k, _o, _n in MN52_KEYS)   # 0.4.58: the 0.4.57 file (P4Mig moves Priest + regen after it)''')
assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0
P.finish()
