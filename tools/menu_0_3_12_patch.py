"""Derive SkyyMenu/build_skyymenu_0.3.12.py from the LIVE SkyyMenu 0.3.11 (python tools/menu_0_3_12_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_11_patch.py -> 0.3.11 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch, never re-build it) -> this patch -> 0.3.12. 0.3.11's files stay untouched. This patch also writes
SkyyMenu/test_skyymenu_0.3.12.py from test_skyymenu_0.3.11.py (every check carried forward, the changes below recorded the same way).

0.3.12 = THE STATS PAGE DEFENSE ROW COUNTS THE SKILL DEFENSE. Skyy's own words: "swap foraging to giving defense instead of health. at
least 20 at lvl 100 class skill should slightly boost all stats." and "Show skill Defense and the class-balance damage % on the Stats
page (a small SkyyMenu build)? -> Yes, next (Recommended)".
  1. SkyySkills 0.4.25 publishes the skill Defense (Foraging + every skill's perk.<skill>.defensePerLevel + the class balance Defense) as
     skill:def:<uuid> = a Double (SkillDef.set: rounded to 2 decimals, 0..100000, REMOVED at 0 and when the player leaves). It is summed
     with the gear Defense in SkyyGear's own formula (SkillDef.factor: scale / (scale + gear + skill)) - the same units as gear Defense.
  2. StatsCalc.skillDef(u) reads it: a Double > 0 (NaN / infinite / <= 0 / missing / any other type = 0; above 100000 = 100000, the
     SkyySkills clamp). StatsCalc.defRow: 0 -> EXACTLY the 0.3.11 row (gearRow "def"); else total = gear + accessories + skill Defense
     and the breakdown gets "Skills +X" after Gear / Accessories. mainTab calls defRow where it called gearRow(.., "def").
     Fix round (review LOW 2): SkyyGear's part.stats "false" -> SkyySkills' SkillDef.reduce uses the skill Defense alone (GON), so defRow
     then drops the gear + accessory Defense and adds "gear stats off" (cfgOn("SkyyGear", "part.stats", true), SkyySkills' same test).
  3. The Class Weapon Damage row is UNCHANGED: SkyySkills 0.4.25 publishes nothing for the class balance damage % (ClassPower.boostDmg
     is only called inside its CombatDmgSys; no bridge key, no Function returns it - checked in build_skyyskills_0.4.25.py), and the task
     forbids reading the class level + the Server Setup classBoost.damage table here. Reported for a SkyySkills round (publish e.g.
     skill:dmg:<uuid>), then a menu round shows it.
  4. No saved data, no UI layout / text change (same rows, same page), ROUND_PINS = {} (SkyySkills 0.4.25 is the SET pin already).
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.11 outside them, byte for byte.
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.11.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.12.py")
tsrc = os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.11.py")
tdst = os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.12.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
OLD = s
assert 'VERSION = "0.3.11"' in s and "0.3.11: THE ACCESSORY BAG TILE" in s and "skill:def:" not in s, "not the generated 0.3.11 script"
CHANGES = []            # (new text, old text) of every change, in order: undone at the end


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyMenu") != "0.3.11":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.11" % _set.get("SkyyMenu"))

# the key + its meaning come from SkyySkills 0.4.25 (the SET pin): fail the patch if that script stops publishing it this way
_sk = open(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.25.py"), encoding="utf8").read()
assert 'String k = "skill:def:" + u.toString();' in _sk and "Double dv = Double.valueOf(x);" in _sk and "br.put(k, dv);" in _sk \
    and "(v > 100000.0 ? 100000.0 : v)" in _sk, "SkyySkills 0.4.25 no longer publishes skill:def:<uuid> as a Double (0..100000)"
assert "ClassPower.boostDmg(slot, clv)" in _sk and _sk.count("boostDmg(") == 2, \
    "SkyySkills 0.4.25 uses the class balance damage elsewhere now - re-check whether it is published (patch point 3)"

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.11: THE ACCESSORY BAG TILE''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.12: THE STATS PAGE DEFENSE ROW COUNTS THE SKILL DEFENSE (notes: tools/menu_0_3_12_patch.py; Skyy "Show skill Defense and the
       class-balance damage % on the Stats page (a small SkyyMenu build)? -> Yes, next (Recommended)"): Main tab Defense = gear +
       accessories + SkyySkills 0.4.25's skill:def:<uuid> (Foraging + class balance Defense, a Double), breakdown "Skills +X"; without
       it (older / no SkyySkills, any other type) the row is exactly 0.3.11's. Class Weapon Damage unchanged (SkyySkills 0.4.25 publishes
       no class balance damage %). No saved data, no layout change; ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.12.py (every 0.3.11 check carried forward + K6 0.3.11 -> 0.3.12 + SD the Defense row).
0.3.11: THE ACCESSORY BAG TILE''')
rep('VERSION = "0.3.11"\n', 'VERSION = "0.3.12"\n')

# ================================================================================================ ROUND_PINS note
rep('''# 0.3.11: EMPTY - ships with SkyyAccessories 0.5.9 (same icon on the Workbench tab) but needs nothing from it; the Mods list version
# catch-up (SkyyAccessories 0.5.5 there) stays a later round.
''', '''# 0.3.11: EMPTY - ships with SkyyAccessories 0.5.9 (same icon on the Workbench tab) but needs nothing from it; the Mods list version
# catch-up (SkyyAccessories 0.5.5 there) stays a later round.
# 0.3.12: EMPTY - reads SkyySkills 0.4.25's skill:def:<uuid> (already the SET pin); without it the Defense row is 0.3.11's.
''')

# ================================================================================================ StatsCalc: skillDef + defRow
rep('''  if (sb.length() == 0) sb.append(gearOn ? "nothing from your gear or accessories" : "SkyyGear is not on this server");
  add(rows, GL[k], num(gv + av) + GU[k], sb.toString());
}""")
''', '''  if (sb.length() == 0) sb.append(gearOn ? "nothing from your gear or accessories" : "SkyyGear is not on this server");
  add(rows, GL[k], num(gv + av) + GU[k], sb.toString());
}""")
# 0.3.12: the skill Defense SkyySkills 0.4.25 publishes (skill:def:<uuid> = Double, Foraging + class balance Defense, the same units as gear
# Defense - SkyySkills sums both in SkyyGear's formula). Only a Double > 0 counts (NaN / infinite / any other type / missing = 0, the
# SkyySkills clamp 100000 kept); 0 = the row is exactly 0.3.11's gearRow. Fix round: with SkyyGear's part.stats "false" (config:fn:SkyyGear
# get, cfgOn - the same test SkyySkills' SkillDef.gearCfg makes) SkyySkills reduces hits by the skill Defense ALONE, so the row then counts
# only the skill Defense and says "gear stats off" (key absent: still exactly 0.3.11's row).
M(scl, r"""
public static double skillDef(java.util.UUID u) {
  try {
    Object o = u == null ? null : br().get("skill:def:" + u.toString());
    if (!(o instanceof Double)) return 0.0;
    double v = ((Double) o).doubleValue();
    if (Double.isNaN(v) || Double.isInfinite(v) || !(v > 0.0)) return 0.0;
    return v > 100000.0 ? 100000.0 : v;
  } catch (Throwable t) { return 0.0; }
}""")
M(scl, r"""
public static void defRow(java.util.ArrayList rows, java.util.UUID u, java.util.HashMap g, java.util.HashMap a, boolean gearOn) {
  double sv = skillDef(u);
  if (!(sv > 0.0)) { gearRow(rows, g, a, gearOn, "def"); return; }
  int k = gi("def");
  if (k < 0) return;
  boolean gs = cfgOn("SkyyGear", "part.stats", true);
  double gv = gs ? get(g, "def") : 0.0;
  double av = gs ? get(a, "def") : 0.0;
  StringBuilder sb = new StringBuilder();
  part(sb, "Gear", gv, GU[k]);
  part(sb, "Accessories", av, GU[k]);
  part(sb, "Skills", sv, GU[k]);
  if (!gs) sb.append(sb.length() == 0 ? "gear stats off" : ", gear stats off");
  if (sb.length() == 0) sb.append(gearOn ? "nothing from your gear or accessories" : "SkyyGear is not on this server");
  add(rows, GL[k], num(gv + av + sv) + GU[k], sb.toString());
}""")
''')
rep('''  vitalRow(rows, "Stamina", vit, 2);
  gearRow(rows, g, a, gearOn, "def");
''', '''  vitalRow(rows, "Stamina", vit, 2);
  defRow(rows, u, g, a, gearOn);   // 0.3.12: + the skill Defense (skill:def:<uuid>); without it = gearRow(.., "def")
''')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.11 outside the recorded changes"
assert s.index("public static void gearRow(") < s.index("public static double skillDef(") < s.index("public static void defRow(") \
    < s.index("public static void mainTab("), "methods before callers"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.11 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))

# ================================================================================================ the harness: test_skyymenu_0.3.12.py
# COPIED FORWARD from test_skyymenu_0.3.11.py with every check; the changes are recorded and undone at the end the same way.
t, TNL = load(tsrc)
TOLD = t
TCH = []


def trep(old, new):
    global t
    n = t.count(old)
    assert n == 1, "harness anchor count %d: %s" % (n, old[:120])
    t = t.replace(old, new, 1)
    TCH.append((new, old))


trep('''"""Bare-JVM check for SkyyMenu 0.3.11 - THE ACCESSORY BAG TILE''', '''"""Bare-JVM check for SkyyMenu 0.3.12 - THE STATS PAGE DEFENSE ROW COUNTS THE SKILL DEFENSE (tools/menu_0_3_12_patch.py, which
also writes this file; deploys on its own, ROUND_PINS = {}). COPIED FORWARD from test_skyymenu_0.3.11.py with every check. Changes:
  K6 NEW (replaces K5): class compare 0.3.11 (the live pin, --prev) -> 0.3.12: no entry added or removed; changed exactly StatsCalc (+
     skillDef, defRow; mainTab calls defRow instead of gearRow "def"; every other method instruction-identical, the same fields),
     CfgRows / CfgFn / SkyyMenuPlugin / MenuData (the version string only), manifest.json (the version only)
  SD NEW: the Defense row EXECUTED on the bridge with 0.3.11's StatsCalc (the --prev jar, own class loader, same skyy.bridge) beside
     0.3.12's: skill:def:<uuid> absent / a String / Float / Integer / Long / NaN / infinite / negative / 0 -> every tab of 0.3.12 = 0.3.11
     row for row; a Double -> Defense = gear + accessories + skill ("Skills +X"), every OTHER row (Class Weapon Damage too) = 0.3.11's;
     without SkyyGear only "Skills +X"; a tiny value; huge clamped at 100000; removed again -> 0.3.11's row;
     SD7 (fix round) SkyyGear part.stats "false" -> skills only + "gear stats off" (key absent: still 0.3.11's row)
  KNOWN + the 3 F fails the 0.3.11 harness prints on the 0.3.11 jar today (2026-10-09: SET has SkyyExploration 0.2.4 and the new
     SkyyFishing 0.1) - still the later Mods-list version catch-up round
    python SkyyMenu/test_skyymenu_0.3.12.py [--jar <SkyyMenu-0.3.12.jar>] [--old <SkyyMenu-0.3.5.jar>] [--prev <SkyyMenu-0.3.11.jar>]
                                            [--dir <scratch folder>] [--keep]     (default scratch tools/dev/scratch/menu0312/menu-harness)
Below: the 0.3.11 text.
Bare-JVM check for SkyyMenu 0.3.11 - THE ACCESSORY BAG TILE''')
trep('VERSION = "0.3.11"\n', 'VERSION = "0.3.12"\n')
trep('PREVVER = "0.3.10"           # the live SET pin: K5\n', 'PREVVER = "0.3.11"           # the live SET pin: K6 + SD\n')
trep('MARK = ".skyymenu-0.3.11-harness"\n', 'MARK = ".skyymenu-0.3.12-harness"\n')
trep('os.path.join(SCRATCH_ROOT, "bagicon01", "menu-harness")', 'os.path.join(SCRATCH_ROOT, "menu0312", "menu-harness")')
trep('"SkyyMenu 0.3.11 harness scratch - safe to delete\\n"', '"SkyyMenu 0.3.12 harness scratch - safe to delete\\n"')
trep('"F4. ROUND_PINS = {} (0.3.11 needs no other mod version): %s"', '"F4. ROUND_PINS = {} (0.3.12 needs no other mod version): %s"')
# KNOWN: the 0.3.11 harness prints exactly 3 more F fails on the 0.3.11 jar today (2026-10-09: SET moved on - SkyyExploration 0.2.4,
# SkyyFishing 0.1 added) - the same Mods-list-behind-SET catch-up, not this round
trep('''# the 0.3.10 harness prints exactly these 7 extra F fails on the 0.3.10 jar today (checked 2026-10-08); the version catch-up is a later round
KNOWN_F = re.compile(r"^F\\. (Skyy(Hud|Sacks|Collections|Bank|Bazaar|Gear|Accessories|Trees|Mobs|Armory|GatherProbe|GatherProbeB|"''',
     '''# the 0.3.10 harness prints exactly these 7 extra F fails on the 0.3.10 jar today (checked 2026-10-08); the version catch-up is a later round
# 0.3.12: + the 3 the 0.3.11 harness prints on the 0.3.11 jar today (2026-10-09: SET has SkyyExploration 0.2.4 and the new SkyyFishing 0.1)
KNOWN_F = re.compile(r"^F\\. (Skyy(Hud|Sacks|Collections|Bank|Bazaar|Gear|Accessories|Trees|Mobs|Armory|GatherProbe|GatherProbeB|Exploration|Fishing|"''')
trep('''r"'SkyyReelProbe', 'SkyyTownProbe'\\]|the build script's MODS_VERSIONS''',
     '''r"'SkyyReelProbe', 'SkyyTownProbe'\\]|MODS lists exactly the SET mods: \\['SkyyFishing', 'SkyyGatherProbe', 'SkyyGatherProbeB', 'SkyyKeyProbe', "
                     r"'SkyyTownProbe'\\]|the build script's MODS_VERSIONS''')

# K5 (0.3.10 -> 0.3.11) -> K6 (0.3.11 -> 0.3.12)
_k5a = t.index("    # ---------------- K5 (0.3.11). class compare PREVVER")
_k5b = t.index("    # ---------------- IC (0.3.11). the icon item")
trep(t[_k5a:_k5b], """    # ---------------- K6 (0.3.12). class compare PREVVER (0.3.11, the live pin) -> VERSION: StatsCalc's Defense row + version strings
    if not os.path.isfile(PREVJAR):
        check(False, "K6. no %s to compare with" % PREVJAR)
    else:
        zp, zb = zipfile.ZipFile(PREVJAR), zipfile.ZipFile(JAR)
        np_, nb = set(zp.namelist()), set(zb.namelist())
        ch6 = sorted(x for x in np_ & nb if zp.read(x) != zb.read(x))
        P_ = "com/skyy/menu/"
        VER6 = [P_ + "CfgRows.class", P_ + "CfgFn.class", P_ + "SkyyMenuPlugin.class"]
        CHG6 = sorted(VER6 + [P_ + "MenuData.class", P_ + "StatsCalc.class", "manifest.json"])
        check(nb == np_, "K6. no entry added or removed: %s / %s" % (sorted(nb - np_), sorted(np_ - nb)))
        check(ch6 == CHG6, "K6. changed exactly %s: %s" % ([x.split("/")[-1] for x in CHG6], [x.split("/")[-1] for x in ch6]))
        for x in VER6:
            ok_, why_ = data_only(zp.read(x), zb.read(x))
            _sp, _sn = cp_strings(zp.read(x)), cp_strings(zb.read(x))
            _gone, _new = sorted(_sp - _sn), sorted(_sn - _sp)
            check(ok_ and len(_gone) == len(_new) >= 1 and all(g.replace(PREVVER, VERSION) in _new for g in _gone)
                  and all(n.replace(VERSION, PREVVER) in _gone for n in _new),
                  "K6. %s differs from %s only by the version string: %s %s / %s" % (x.split("/")[-1], PREVVER, why_, [g[-60:] for g in _gone], [n[-60:] for n in _new]))
        _mfo, _mfn = json.loads(zp.read("manifest.json").decode("utf-8")), json.loads(zb.read("manifest.json").decode("utf-8"))
        check(json.dumps(_mfo, sort_keys=True).replace(PREVVER, VERSION) == json.dumps(_mfn, sort_keys=True), "K6. manifest.json: the version only")
        ok_, why_ = data_only(zp.read(P_ + "MenuData.class"), zb.read(P_ + "MenuData.class"))
        _dp, _dn6 = cp_strings(zp.read(P_ + "MenuData.class")), cp_strings(zb.read(P_ + "MenuData.class"))
        check(ok_ and sorted(_dn6 - _dp) == [VERSION] and sorted(_dp - _dn6) in ([PREVVER], []),
              "K6. MenuData: data only, the own version %s -> %s: %s %s / %s" % (PREVVER, VERSION, why_, sorted(_dn6 - _dp), sorted(_dp - _dn6)))
        cp_, cn_ = ct(zp.read(P_ + "StatsCalc.class")), ct(zb.read(P_ + "StatsCalc.class"))
        mo6, mn6 = methods(cp_), methods(cn_)
        chg6 = sorted(k.split("(")[0] for k in mo6 if k in mn6 and mo6[k] != mn6[k])
        add6 = sorted(k.split("(")[0] for k in mn6 if k not in mo6)
        check(chg6 == ["mainTab"] and add6 == ["defRow", "skillDef"] and not [k for k in mo6 if k not in mn6] and fields_of(cp_) == fields_of(cn_),
              "K6. StatsCalc: + skillDef, defRow; only mainTab changed; the same fields; every other method instruction-identical: %s %s" % (chg6, add6))
        _mt = [k for k in mn6 if k.startswith("mainTab(")][0]

        def _calls(ls, nm):
            return len([l for l in ls if l.startswith("invokestatic") and ("StatsCalc." + nm + "(") in l])
        check(_calls(mo6[_mt], "gearRow") - 1 == _calls(mn6[_mt], "gearRow") and _calls(mn6[_mt], "defRow") == 1 and _calls(mo6[_mt], "defRow") == 0
              and len(mn6[_mt]) <= len(mo6[_mt]),
              "K6. mainTab: one gearRow(.., 'def') call became defRow(rows, u, g, a, gearOn): gearRow %d -> %d, defRow %d" % (
                  _calls(mo6[_mt], "gearRow"), _calls(mn6[_mt], "gearRow"), _calls(mn6[_mt], "defRow")))
        check({"skill:def:", "Skills"} <= cp_strings(zb.read(P_ + "StatsCalc.class")), "K6. StatsCalc reads skill:def:<uuid>, labels it Skills")
        same6 = sorted(x for x in np_ & nb if x not in ch6)
        check(len(same6) == len(np_) - len(CHG6), "K6. every other entry byte-identical (%d)" % len(same6))
        print("K6. %s -> %s: %d entries byte-identical; changed %s" % (PREVVER, VERSION, len(same6), [x.split("/")[-1] for x in ch6]))
        zp.close()
        zb.close()

""")

# SD after S1 (the bridge is set up, before the fix-round checks)
trep('''    # ---- S5 the fix round (review findings), static rows
''', '''    # ---- SD (0.3.12) the Defense row + skill:def:<uuid>, executed beside 0.3.11's StatsCalc (the --prev jar, its own loader, same bridge)
    SCalcP = JClass(PKG + "StatsCalc", loader=mkloader(PREVJAR)) if os.path.isfile(PREVJAR) else None
    check(SCalcP is not None, "SD. the 0.3.11 jar (--prev %s) is there to compare rows with" % PREVJAR)

    def prows(u_, tab):
        r_ = SCalcP.rows(u_, tab, None)
        return [tuple(str(x) for x in r_.get(i)) for i in range(int(r_.size()))]

    def tabs_of(f_, u_):
        return [f_(u_, k_) for k_ in range(5)]

    def no_def(tabs_):
        return [[r for r in tb if r[0] != "Defense"] for tb in tabs_]

    if SCalcP is not None:
        KD = "skill:def:" + us
        S_KEYS.append(KD)
        BRG.remove(KD)
        SD0n, SD0o = tabs_of(srows, SU), tabs_of(prows, SU)
        check(SD0n == SD0o and row(SD0n[0], "Defense") == ("Defense", "12", "Gear +12"),
              "SD1 no skill:def key: every tab = 0.3.11's, Defense = gear only: %s" % (row(SD0n[0], "Defense"),))
        _bad = [("a String", JStr("6.5")), ("a Float", Flt.valueOf(6.5)), ("an Integer", Integer.valueOf(7)), ("a Long", Lng.valueOf(7)),
                ("NaN", Dbl.valueOf(float("nan"))), ("+infinite", Dbl.valueOf(float("inf"))), ("negative", Dbl.valueOf(-3.0)), ("0", Dbl.valueOf(0.0))]
        for _what, _v in _bad:
            BRG.put(KD, _v)
            _n, _o = tabs_of(srows, SU), tabs_of(prows, SU)
            check(_n == _o == SD0o, "SD2 skill:def = %s -> every tab exactly 0.3.11's: %s" % (_what, row(_n[0], "Defense")))
        BRG.put(KD, Dbl.valueOf(6.5))
        SD3n, SD3o = tabs_of(srows, SU), tabs_of(prows, SU)
        check(row(SD3n[0], "Defense") == ("Defense", "18.5", "Gear +12, Skills +6.5") and row(SD3o[0], "Defense") == ("Defense", "12", "Gear +12"),
              "SD3 skill:def 6.5 (Double): Defense 12 + 6.5 = 18.5, 'Skills +6.5' (0.3.11 shows 12): %s" % (row(SD3n[0], "Defense"),))
        check(no_def(SD3n) == no_def(SD3o) and [r[0] for r in SD3n[0]] == [r[0] for r in SD3o[0]] and not under80(sum(SD3n, [])),
              "SD3 every other row of every tab = 0.3.11's, same order, under 80 characters")
        check(row(SD3n[1], "Class Weapon Damage") == row(SD0n[1], "Class Weapon Damage") == ("Class Weapon Damage", "+4.4%", "Swordsmanship level 22, with your class weapons"),
              "SD3 Class Weapon Damage unchanged with the key present / absent (SkyySkills 0.4.25 publishes no class balance damage %%): %s" % (row(SD3n[1], "Class Weapon Damage"),))
        _bc = []
        for _what, _v in _bad[:4]:
            BRG.put(KD, _v)
            _bc.append(row(srows(SU, 1), "Class Weapon Damage"))
        check(all(x == row(SD0n[1], "Class Weapon Damage") for x in _bc), "SD3 Class Weapon Damage unchanged with a non-Double key: %s" % _bc)
        BRG.put(KD, Dbl.valueOf(1.0e9))
        check(row(srows(SU, 0), "Defense") == ("Defense", "100,012", "Gear +12, Skills +100,000"), "SD4 huge clamped at 100000 (the SkyySkills clamp): %s" % (row(srows(SU, 0), "Defense"),))
        BRG.put(KD, Dbl.valueOf(0.01))
        check(row(srows(SU, 0), "Defense") == ("Defense", "12", "Gear +12"), "SD4 a tiny value (0.01): total 12, no 'Skills +0' part: %s" % (row(srows(SU, 0), "Defense"),))
        # accessories + skill; no gear at all; no SkyyGear on the server
        U2 = UUID.fromString("00000000-0000-0000-0000-0000000005d2")
        bput("gear:stats:" + str(U2), "def:10,str:4")
        bput("gear:extra:" + str(U2), "def:3")
        bput("skill:def:" + str(U2), Dbl.valueOf(20.0))
        check(row(srows(U2, 0), "Defense") == ("Defense", "33", "Gear +10, Accessories +3, Skills +20"), "SD5 gear 10 + accessories 3 + skills 20: %s" % (row(srows(U2, 0), "Defense"),))
        U3 = UUID.fromString("00000000-0000-0000-0000-0000000005d3")
        bput("skill:def:" + str(U3), Dbl.valueOf(4.5))
        _gf = BRG.remove("gear:fn:stats")
        R3n, R3o = tabs_of(srows, U3), tabs_of(prows, U3)
        BRG.put("skill:def:" + str(U3), Dbl.valueOf(0.01))
        R3t = row(srows(U3, 0), "Defense")
        BRG.put("skill:def:" + str(U3), Dbl.valueOf(4.5))
        if _gf is not None:
            BRG.put("gear:fn:stats", _gf)
        R3h = row(srows(U3, 0), "Defense")
        check(row(R3n[0], "Defense") == ("Defense", "4.5", "Skills +4.5") and row(R3o[0], "Defense") == ("Defense", "0", "SkyyGear is not on this server")
              and no_def(R3n) == no_def(R3o), "SD5 without SkyyGear: Defense = skills only; every other row 0.3.11's: %s" % (row(R3n[0], "Defense"),))
        check(R3t == ("Defense", "0", "SkyyGear is not on this server") and R3h == ("Defense", "4.5", "Skills +4.5"),
              "SD5 tiny skill Defense without SkyyGear -> 0.3.11's wording; with SkyyGear and no gear -> Skills only: %s %s" % (R3t, R3h))
        BRG.put("skill:def:" + str(U3), Dbl.valueOf(0.01))
        check(row(srows(U3, 0), "Defense") == ("Defense", "0", "nothing from your gear or accessories"), "SD5 tiny + SkyyGear on, no gear: %s" % (row(srows(U3, 0), "Defense"),))
        # SD7 (fix round): SkyyGear's part.stats "false" -> skill Defense alone (SkyySkills' SkillDef.reduce uses no gear Defense then)
        GPS = {"v": "false"}
        GASK = []

        def gcfg_fn(a):
            GASK.append(str(a[1]))
            if str(a[0]) == "get" and str(a[1]) == "part.stats":
                return GPS["v"]
            return None
        bput("config:fn:SkyyGear", SFn(gcfg_fn))
        BRG.put(KD, Dbl.valueOf(6.5))
        S7n, S7o = tabs_of(srows, SU), tabs_of(prows, SU)
        check(row(S7n[0], "Defense") == ("Defense", "6.5", "Skills +6.5, gear stats off") and "part.stats" in GASK
              and no_def(S7n) == no_def(S7o) and not under80(sum(S7n, [])),
              "SD7 part.stats false + skill 6.5: Defense = skills only, 'gear stats off', every other row 0.3.11's: %s" % (row(S7n[0], "Defense"),))
        check(row(srows(U2, 0), "Defense") == ("Defense", "20", "Skills +20, gear stats off"),
              "SD7 part.stats false: gear 10 + accessories 3 dropped, skills 20 stay: %s" % (row(srows(U2, 0), "Defense"),))
        GPS["v"] = " FALSE "
        check(row(srows(SU, 0), "Defense") == ("Defense", "6.5", "Skills +6.5, gear stats off"), "SD7 ' FALSE ' (trim, any case) = off: %s" % (row(srows(SU, 0), "Defense"),))
        BRG.put(KD, Dbl.valueOf(0.01))
        check(row(srows(SU, 0), "Defense") == ("Defense", "0", "gear stats off"), "SD7 part.stats off + tiny skill: %s" % (row(srows(SU, 0), "Defense"),))
        BRG.remove(KD)
        check(tabs_of(srows, SU) == tabs_of(prows, SU) and row(srows(SU, 0), "Defense") == ("Defense", "12", "Gear +12"),
              "SD7 part.stats off, no skill:def key: every tab exactly 0.3.11's (gear still shown, as 0.3.11 did)")
        BRG.put(KD, Dbl.valueOf(6.5))
        _sd7 = []
        for _pv in ("true", "maybe", None):
            GPS["v"] = _pv
            _sd7.append(row(srows(SU, 0), "Defense"))
        check(all(x == ("Defense", "18.5", "Gear +12, Skills +6.5") for x in _sd7), "SD7 part.stats true / unreadable / not set = on (SkyySkills' rule): %s" % _sd7)
        BRG.remove("config:fn:SkyyGear")
        check(row(srows(SU, 0), "Defense") == ("Defense", "18.5", "Gear +12, Skills +6.5"), "SD7 no config:fn:SkyyGear = on: %s" % (row(srows(SU, 0), "Defense"),))
        # SkyySkills drops the key (0 / the player left) -> 0.3.11's row again
        BRG.remove(KD)
        check(tabs_of(srows, SU) == SD0o, "SD6 key removed again: every tab = 0.3.11's")
    print("SD. Defense row: gear + accessories + skill:def (Double only), 0.3.11's rows otherwise; Class Weapon Damage unchanged")

    # ---- S5 the fix round (review findings), static rows
''')

# ---------------- checks on the harness
_ut = t
for _new, _old in reversed(TCH):
    assert _ut.count(_new) == 1, "a harness change is not unique any more: %s" % _new[:80]
    _ut = _ut.replace(_new, _old, 1)
assert _ut == TOLD, "the harness differs from 0.3.11's outside the recorded changes"
compile(t, tdst, "exec")
open(tdst, "w", encoding="utf8", newline="").write(t.replace(LF, TNL) if TNL != LF else t)
print("wrote", os.path.relpath(tdst, ROOT), "(%d lines; 0.3.11 had %d; %d changes)" % (t.count(LF), TOLD.count(LF), len(TCH)))
