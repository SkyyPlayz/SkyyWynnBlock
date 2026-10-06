"""Bare-JVM check for SkyyGear 0.2.5 (the mob curve round's gear part: research/Mob-Curve-Spec.md 2.2-2.6 / 6.2 / 6.4 / 7.2-7.4, Reforge
level up cap +6, the vanilla armor box hidden). The 0.2.3 harness (SkyyGear/test_skyygear_0.2.3.py, read only - every 0.1 ... 0.2.3 section)
runs on the 0.2.5 jar with VERSION 0.2.5 and the new section AF appended inside its child run (it reuses the AC model: real Item / ItemArmor /
DamageCause / EntityStatMap objects and the ECS shim with the REAL GearHitSys, engine ArmorDamageReduction, GearArmorSys and GearTrueSys).

    python SkyyGear/test_skyygear_0.2.5.py [--jar <SkyyGear-0.2.5.jar>] [--dir <scratch folder>] [--live <config.properties>] [--keep]

Carried-forward checks that MUST read differently on 0.2.5 are listed in DEVIATIONS with the reason (each one is a changed DEFAULT - the
steep weapon curve, the armor Health curve, 7 new rows - or was already failing on the 0.2.4 jar with the 0.2.3 harness because SkyyArmory 0.1.1
is pinned); such a failure is printed as "DEVIATION (0.2.5, expected)" and does not fail the run; any other failure does. Section AF re-checks
each of those areas against the 0.2.5 numbers.
  AF 0.2.5 - every new code path EXECUTED:
     AF0/1 the curve constants = the spec typed independently; the 7 new rows (types, defaults, flags, tabs, units, limits), base.curve
         relabelled; the fresh file (the 0.2.5 block under base.curve, steal.maxPerSec under steal.windowS, the level up rows + coin table
         under cost.reforge.set); the loader (bad curves -> default + WARN, clamps, the coin table), costLevelUp;
     AF2 F = H = the old F at Lv 0-20, the spec 2.3 columns; every tooltip line + weapon multiplier of 15 items at Lv 1-20 identical to the
         0.2.4 curves; Lv 21-49 weapon hits x F, wand SHOTS x S, armor Health x H; spec 7.6 step 6 (Lv 25 Cobalt sword x1.24, chestplate
         +36, was +24); K unchanged for every family based at Lv 1-20 and every family base keeps its band-start multiplier exactly; the
         Lv 40 / Lv 20 worked rows through GearHit.weaponHit on real Damage objects; every wand / staff / spellbook shot line + spell range
         at Lv 1-49 = 0.2.4's; live curve edits; the ready line; /gear read; gear:fn:curve (the REAL GearFn mode 10: Double answers, bad
         input -> null, live) + its bridge registration (bytecode);
     AF3 the Life Steal cap: stealPay cases + the REAL GearFx.second payout on the real EntityStatMap (cap, rest dropped, cap 0 = off);
     AF4 Reforge LEVEL UP: lvlInfo in every state (cap +6, metal cap, your level, admin level, switch off, part.levels off, no class,
         unstamped, lvl0 kept); GearForge.levelUp end to end on real containers (coins first, 6 ups then refused, the band cap, not enough
         coins / no SkyyCoins / moved / unidentified refused before any coin moves, a stack of 2 split, a refused write -> refund); the sig;
         the Reforge page (level line + button on a real UICommandBuilder / UIEventBuilder, 'lvl' click -> ReforgePage.lvlUp: Before / After);
     AF5 the vanilla ARMOR box: which types are hidden (never shared / non-additive / non-gear / weapons) + WARNs; empty asset maps, the
         real ItemArmor.toPacket, the packet cache; EQUIVALENCE with 0.2.4 in 110+ cases (7 pieces incl. FLAT + BaseDamageResistance + Fall,
         Poison, Mana x 4 levels x active / under-level with level.armorNative on + off / levelling off + unidentified + a full set: max
         Health, max Mana and damage taken for 5 causes through the real chain); the engine alone applies nothing for a hidden piece; restore;
         the tooltip lines from the kept maps; an asset reload through the REAL GearBoxL listener with a real LoadedAssetsEvent; switched
         off / unordered; the wiring (bytecode);
     AF6 migrate025 on scratch COPIES of the live Skyy_SkyyGear folder (read only): exact bytes, INFO, every other value kept, ONE History
         copy, ONE change-log line, the loader, a SECOND start changes nothing, setup()'s whole file chain twice (no file changes the second
         time), Undo through the config kit (the next start keeps it), a hand-set base.curve kept + copied, already new, keys already there
         kept, CRLF, no anchors, a continued base.curve, a fresh file, History blocked, 400 random files vs java.util.Properties;
     AF10 the class byte-compare 0.2.4 -> 0.2.5 (every difference listed).
Scratch: only under --dir (default tools/dev/scratch/gear025/harness), deleted at the end unless --keep. Exit code 1 on any unexpected failure.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "test_skyygear_0.2.3.py")
src = open(BASE, encoding="utf-8").read()


def sub(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "test_skyygear_0.2.3.py changed: anchor count %d (want %d): %s" % (n, count, old[:120])
    src = src.replace(old, new)


DEVIATIONS = [
    ("Z7(a): the 0.1.2-updated live file has every value", "the fresh file has 0.2.5 values (base.curve = the new F + 13 keys) no 0.1.x update writes - AF6 checks migrate025"),
    ("Z8: the live data ends with every value of a fresh 0.2.5 file", "Z8 replays setup() only up to migrate023 (base.curve keeps the 0.2.1 default there) - AF6(a)/(c) run migrate025 on the same live copy"),
    ("AB7(a): the updated live file holds every value of a fresh 0.2 file", "the fresh file's 0.2.5 values - AF6"),
    ("AB7(i): the 0.1 file -> all five one-time updates run once", "the fresh file's 0.2.5 values - AF6"),
    ("AC1: the seven 0.2.1 rows are in Server Setup (65 rows", "72 rows (AF1)"),
    ("AC1: row types / defaults / flags", "base.curve's default is the steep F (AF1)"),
    ("AC1: the fresh file carries the 0.2.1 block", "the 0.2.5 block sits inside it, right under base.curve (AF1)"),
    ("AC1: the built-in defaults (no file)", "the built-in base.curve is the steep F (AF1)"),
    ("AC2: F(L) = the spec 3.1 table", "the steep F after Lv 20 (AF2; Lv 1-20 identical)"),
    ("AC2: R(L) = 1:1.0, 10:1.4, 20:1.7, 40:2.2, 100:3.0; F flat", "the check also asks F(100) = 5 - the new F is 90 from Lv 90; R is unchanged (AF2)"),
    ("AC2: metal Sword / Shortbow / Spear / Mace / Battleaxe items at their band start", "metal items from Lv 25 hit x2.8-3.4 of vanilla with the steep F (Mob-Curve-Spec 2.3)"),
    ("AC2: R10 noted", "with the steep F the Axe / Longsword / Club metal items no longer fall under vanilla from Lv 25 (the R10 risk is gone)"),
    ("AC3(a): Lv 40 through GearHit.weaponHit", "weapons x F(40) 9.6, spell shots keep 3.0 (AF2 checks the new Lv 40 row and the unchanged Lv 20 row)"),
    ("AC3(c): ... the same arrow with no damage step", "with the steep F the Lv 40 staff's SPELL multiplier (S) is now the smaller one, so the unchanged rule (the smallest live multiplier) keeps it"),
    ("AC3(c): finding 1 - an Iron crossbow Lv 15 bolt", "F(13) = 2.0999999 (the spec's 20:2.333333 point, 3e-7 off the old line): 12 x m = 25.1999988 misses the check's 1e-6; every rendered Lv 1-20 number is identical (AF2)"),
    ("AC3(c): a live weapon whose walk is incomplete", "the clamp keeps the smallest live multiplier - now the staff's spell multiplier (see above)"),
    ("AC4: chestplate Health per level through the lock plumbing", "armor Health follows H: Lv 40 = 9 x 9.6 = 86 (AF2 / AF5)"),
    ("AC4: switched back on -> Lv 40 = +27 again", "Lv 40 = +86 with H"),
    ("AC7: finding 3 - Weapon_Spellbook_Fire Lv 30", "the check derives its number from F; spells follow S = the old F (73, as in 0.2.4 - AF2)"),
    ("AC7: finding 3 - Weapon_Staff_Frost Lv 30", "the check derives its number from F; spells follow S = the old F (58, as in 0.2.4 - AF2)"),
    ("AC7: the other vanilla lines stay", "Cindercloth Lv 30 Health follows H (29; the check computes F); the Poison / Mana lines are unchanged (AF5(d))"),
    ("AC7: /gear read explains the base stats", "describe() names H for armor now (AF2)"),
    ("AE1: Server Setup rows xp.craft", "the check also counts 65 rows - 72 now (AF1)"),
    ("AE10: no class added or removed", "the historical 0.2.2 -> 0.2.3 compare - AF10 compares 0.2.4 -> 0.2.5"),
    ("AE10: no difference outside the listed 0.2.3 parts", "the historical 0.2.2 -> 0.2.3 compare - AF10 compares 0.2.4 -> 0.2.5"),
    # already failing with the 0.2.4 jar (2026-10-06 run): the SET pins SkyyArmory 0.1.1 (11-element answer: the traversal line, quick-shot
    # words, its projectile ladder) - the 0.2.3 harness predates it; SkyyArmory's own 0.1.1 harness checks those lines (section G2) and AF2
    # proves every shot line identical to 0.2.4's
    ("AD0: SkyyArmory's 31 projectiles", "pre-existing on 0.2.4: SkyyArmory 0.1.1 is pinned (its projectile set changed)"),
    ("AD1: every SkyyArmory wand + staff and the Wood wand at band start", "pre-existing on 0.2.4: SkyyArmory 0.1.1's quick-shot words / traversal line"),
    ("AD1: Skyy's sample - the Lv 6 Wood wand", "pre-existing on 0.2.4: ' - pierces - 16 blocks' (SkyyArmory 0.1.1)"),
    ("AD1: Weapon_Wand_Wood_Rotten", "pre-existing on 0.2.4: ' - pierces - 16 blocks' (SkyyArmory 0.1.1)"),
    ("AD1: Weapon_Wand_Tribal", "pre-existing on 0.2.4: ' - pierces - 16 blocks' (SkyyArmory 0.1.1)"),
    ("AD1: 'Damage by wand' Iron 150 %", "pre-existing on 0.2.4: the traversal line under the charged shot (SkyyArmory 0.1.1)"),
    ("AD1: Wood 200 % doubles only its QUICK shot", "pre-existing on 0.2.4: ' - pierces - 16 blocks' (SkyyArmory 0.1.1)"),
    ("AD1: SkyyArmory's 'Quick shot damage' 40", "pre-existing on 0.2.4: the traversal line (SkyyArmory 0.1.1)"),
    ("AD1: SkyyArmory 'Damage tune' off", "pre-existing on 0.2.4: the traversal line (SkyyArmory 0.1.1)"),
    ("AD1: part.base / base.mode off", "pre-existing on 0.2.4: the traversal line (SkyyArmory 0.1.1)"),
    ("AD1: gear:fn:describe (AH) and the Reforge page columns", "pre-existing on 0.2.4: the traversal line (SkyyArmory 0.1.1)"),
]

sub('VERSION = "0.2.3"', 'VERSION = "0.2.5"\nDEVIATIONS = %r\nDEV_SEEN = {}\nAF_EXPECT = %r' % (DEVIATIONS, None))
sub('os.path.join(TOOLS, "dev", "scratch", "gear023", "harness")', 'os.path.join(TOOLS, "dev", "scratch", "gear025", "harness")')
sub('''def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)''', '''def check(cond, what):
    if cond:
        OKS[0] += 1
        return
    for p_, why_ in DEVIATIONS:
        if what.startswith(p_):
            DEV_SEEN[p_] = DEV_SEEN.get(p_, 0) + 1
            print("DEVIATION (0.2.5, expected):", what[:150], "|", why_)
            return
    FAILS.append(what)
    print("FAIL", what)''')
sub('''        print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))''', '''        print("%d checks passed, %d failed, %d expected 0.2.5 deviations (%d listed kinds seen)" % (OKS[0], len(FAILS), sum(DEV_SEEN.values()), len(DEV_SEEN)))''')


AF_SRC = r'''    # ======================================================================================================================== AF 0.2.5
    # SkyyGear 0.2.5 = the mob curve round's gear part (research/Mob-Curve-Spec.md 2.2-2.6, 6.2, 6.4, 7.2-7.4; Reforge level up cap +6;
    # the vanilla armor box). Every new code path EXECUTED on the AC model (real Item / ItemArmor / DamageCause / ResistanceModifier /
    # EntityStatMap objects; the REAL GearHitSys + engine ArmorDamageReduction + GearArmorSys + GearTrueSys on the ECS shim).
    from jpype import JDouble
    print("AF. 0.2.5: three curves, gear:fn:curve, Life Steal cap, Reforge level up, the vanilla armor box, migrate025")
    OLDF, NEWF, HDEF, SDEF = str(Cfg.CURVE_OLD), str(Cfg.CURVE_DEF), str(Cfg.HP_DEF), str(Cfg.SPELL_DEF)
    SPEC_F = "1:1.0,4:1.6,10:2.0,20:2.3333333333333335,25:3.1,30:4.5,35:6.5,40:9.6,45:13.6,50:17.5,60:22.5,70:36.0,80:57.0,90:90.0"
    SPEC_H = "1:1.0,4:1.6,10:2.0,20:2.3333333333333335,25:3.7,30:5.4,35:7.3,40:9.6,45:12.8,50:16.3,60:21.0,70:30.0,80:43.0,90:62.0,100:88.0"
    SPEC_O = "1:1.0,4:1.6,10:2.0,40:3.0,100:5.0"
    check(NEWF == SPEC_F and OLDF == SPEC_O and SDEF == SPEC_O and HDEF == SPEC_H, "AF0: the jar's curve constants = research/Mob-Curve-Spec.md 2.2 (typed here "
          "independently; the Lv 20 point is 2.3333333333333335 = 7/3 - AF2 shows why not the spec's 2.333333)")

    def pyc(text_, lv_):
        pts_ = [(float(a_), float(b_)) for a_, b_ in (p_.split(":") for p_ in text_.split(","))]
        if lv_ <= pts_[0][0]:
            return pts_[0][1]
        for (l0_, v0_), (l1_, v1_) in zip(pts_, pts_[1:]):
            if lv_ <= l1_:
                return v0_ + (v1_ - v0_) * (lv_ - l0_) / (l1_ - l0_)
        return pts_[-1][1]

    def curves(f_=None, s_=None, h_=None):
        Cfg.BASE_CURVE = NEWF if f_ is None else f_
        Cfg.BASE_SPELL = SDEF if s_ is None else s_
        Cfg.BASE_HP = HDEF if h_ is None else h_

    # ---- AF1. the rows, the fresh default file, the loader
    Cfg.apply(Props(), False)
    rw5 = dict((str(k_), dict(t=str(t_), d=str(d_), f=str(f_), h=str(h_), o=str(o_), l=str(l_), u=str(u_), mn=str(a_), mx=str(b_), c=str(c_)))
               for k_, t_, d_, f_, h_, o_, l_, u_, a_, b_, c_ in zip(Rows.KEYS, Rows.TYPES, Rows.DEFS, Rows.FLAGS, Rows.HELPS, Rows.OPTS, Rows.LABELS,
                                                                    Rows.UNITS, Rows.MINS, Rows.MAXS, Rows.CATS))
    NEW25 = ["base.spellCurve", "base.hpCurve", "steal.maxPerSec", "reforge.levelUp", "reforge.levelCap", "cost.levelUp", "view.hideArmorBox"]
    check(len(rw5) == 72 and all(k_ in rw5 for k_ in NEW25), "AF1: 72 Server Setup rows (65 + the seven 0.2.5 rows): %d" % len(rw5))
    check(rw5["base.curve"]["l"] == "Weapon curve F(L)" and rw5["base.curve"]["d"] == SPEC_F and rw5["base.curve"]["f"] == "live,danger"
          and rw5["base.spellCurve"]["l"] == "Spell curve S(L)" and rw5["base.spellCurve"]["d"] == SPEC_O and rw5["base.spellCurve"]["t"] == "text"
          and rw5["base.hpCurve"]["l"] == "Armor Health curve H(L)" and rw5["base.hpCurve"]["d"] == SPEC_H and rw5["base.hpCurve"]["t"] == "text"
          and all(rw5[k_]["c"] == "base" and rw5[k_]["f"] == "live,danger" and rw5[k_]["h"].endswith(PH) for k_ in ("base.curve", "base.spellCurve", "base.hpCurve")),
          "AF1: the three curve rows (spec 6.2 labels, defaults = spec 2.2, Level stats tab, live + danger, Placeholder help)")
    check(rw5["steal.maxPerSec"]["t"] == "dec" and rw5["steal.maxPerSec"]["d"] == "5" and rw5["steal.maxPerSec"]["u"] == "%" and rw5["steal.maxPerSec"]["c"] == "combat"
          and (rw5["steal.maxPerSec"]["mn"], rw5["steal.maxPerSec"]["mx"]) == ("0", "100") and rw5["steal.maxPerSec"]["l"] == "Life Steal at most"
          and rw5["reforge.levelUp"]["t"] == "bool" and rw5["reforge.levelUp"]["d"] == "true" and rw5["reforge.levelUp"]["c"] == "costs"
          and rw5["reforge.levelCap"]["t"] == "int" and rw5["reforge.levelCap"]["d"] == "6" and (rw5["reforge.levelCap"]["mn"], rw5["reforge.levelCap"]["mx"]) == ("0", "50")
          and rw5["cost.levelUp"]["t"] == "table" and rw5["cost.levelUp"]["o"] == "int;none;Base|Per level" and rw5["cost.levelUp"]["u"] == "coins"
          and all(rw5[k_]["f"] == "live,danger" for k_ in ("steal.maxPerSec", "reforge.levelUp", "reforge.levelCap", "cost.levelUp"))
          and rw5["view.hideArmorBox"]["t"] == "bool" and rw5["view.hideArmorBox"]["d"] == "true" and rw5["view.hideArmorBox"]["f"] == "restart"
          and all(len(rw5[k_]["h"]) <= 100 and len(rw5[k_]["l"]) <= 40 for k_ in NEW25),
          "AF1: steal.maxPerSec (5 %, 0-100), reforge.levelUp / levelCap (6, 0-50) / cost.levelUp (Base | Per level coins), view.hideArmorBox (restart)")
    dt5 = str(Cfg.defaultsText())
    dl5 = dt5.split("\n")
    gl5 = [str(x) for x in Cfg.GC_LINES]
    ib5 = dl5.index("base.curve=" + SPEC_F)
    check(dl5[ib5 + 1:ib5 + 1 + len(gl5)] == gl5 and gl5[0] == str(Cfg.GC_MARK) and "base.spellCurve=" + SPEC_O in gl5 and "base.hpCurve=" + SPEC_H in gl5
          and "view.hideArmorBox=true" in gl5 and dt5.count(str(Cfg.GC_MARK_ID)) == 1 and "=" not in str(Cfg.GC_MARK) and len(gl5) == 7,
          "AF1: the fresh file: base.curve = the new F, then the 0.2.5 marker + Spell / Armor Health curve + hideArmorBox (help + key=value each)")
    iw5 = dl5.index("steal.windowS=3")
    ir5 = dl5.index("cost.reforge.set=2500,0")
    lul = [str(x) for x in Cfg.LU_LINES]
    check(dl5[iw5 + 1:iw5 + 3] == [str(Cfg.SM_ROWC[0]), "steal.maxPerSec=5"] and dl5[ir5 + 1:ir5 + 1 + len(lul)] == lul
          and lul[-7:] == ["cost.levelUp.normal=100,20", "cost.levelUp.unique=200,40", "cost.levelUp.rare=400,80", "cost.levelUp.legendary=1000,200",
                           "cost.levelUp.fabled=2000,400", "cost.levelUp.mythic=4000,800", "cost.levelUp.set=1000,200"]
          and "reforge.levelUp=true" in lul and "reforge.levelCap=6" in lul and dt5.startswith("# SkyyGear 0.2.5 - "),
          "AF1: the fresh file: steal.maxPerSec under steal.windowS, the level up rows + coin table under cost.reforge.set")
    check(str(Cfg.BASE_CURVE) == SPEC_F and str(Cfg.BASE_SPELL) == SPEC_O and str(Cfg.BASE_HP) == SPEC_H and float(Cfg.STEAL_MAX) == 5.0
          and bool(Cfg.LVLUP_ON) and int(Cfg.LVLUP_CAP) == 6 and bool(Cfg.HIDE_ABOX) and [int(x) for x in Cfg.LU_BASE] == [100, 200, 400, 1000, 2000, 4000, 1000]
          and [int(x) for x in Cfg.LU_PER] == [20, 40, 80, 200, 400, 800, 200], "AF1: the built-in defaults (no file)")
    pp5 = Props()
    for k_, v_ in (("base.spellCurve", "nonsense"), ("base.hpCurve", "1:1,1:2"), ("steal.maxPerSec", "500"), ("reforge.levelCap", "99"),
                   ("reforge.levelUp", "off"), ("view.hideArmorBox", "no"), ("cost.levelUp.rare", "7,8"), ("cost.levelUp.set", "bad")):
        pp5.setProperty(k_, v_)
    for k_ in [str(x) for x in Gear.ONCE.keySet()]:
        if k_.startswith("scurve:") or k_.startswith("hcurve:"):
            Gear.ONCE.remove(k_)
    Cfg.apply(pp5, True)
    check(str(Cfg.BASE_SPELL) == SPEC_O and str(Cfg.BASE_HP) == SPEC_H and Gear.ONCE.containsKey("scurve:nonsense") and Gear.ONCE.containsKey("hcurve:1:1,1:2")
          and float(Cfg.STEAL_MAX) == 100.0 and int(Cfg.LVLUP_CAP) == 50 and not bool(Cfg.LVLUP_ON) and not bool(Cfg.HIDE_ABOX)
          and int(Cfg.LU_BASE[2]) == 7 and int(Cfg.LU_PER[2]) == 8 and int(Cfg.LU_BASE[6]) == 1000 and int(Cfg.costLevelUp(2, 11)) == 7 + 8 * 11,
          "AF1: the loader: a bad curve -> its default + one WARN each, clamps (Life Steal 100, level cap 50), the coin table (rare 7 + 8 x level)")
    Cfg.apply(Props(), False)
    check(int(Cfg.costLevelUp(0, 11)) == 100 + 20 * 11 and int(Cfg.costLevelUp(-3, 5)) == 200 and int(Cfg.costLevelUp(4, 0)) == 2000,
          "AF1: costLevelUp = base + per level x the NEW level (Normal Lv 11 = 320; a bad rarity index = Normal)")
    print("AF1. rows + fresh file + loader done")

    # ---- AF2. the curves (spec 2.2 / 2.3) through GearBase / GearView / GearHit on the real model
    def lines5(iid_, lv_):
        t_, c_ = ArrayList(), ArrayList()
        View.statLines(iid_, doc(iid_, lv_), t_, c_)
        return [str(x) for x in t_]
    F5 = lambda l_: float(Base.curveF(l_))
    S5 = lambda l_: float(Base.curveS(l_))
    H5 = lambda l_: float(Base.curveH(l_))
    R5 = lambda l_: float(Base.curveR(l_))
    Base.clear()
    check(all(abs(F5(l_) - pyc(SPEC_O, l_)) < 1e-15 and abs(H5(l_) - pyc(SPEC_O, l_)) < 1e-15 and S5(l_) == pyc(SPEC_O, l_) for l_ in range(0, 21))
          and sum(1 for l_ in range(0, 21) if F5(l_) == pyc(SPEC_O, l_)) >= 19,
          "AF2: F and H equal the 0.2.1 F at item level 0-20 (bit for bit at 19 levels, 1 ulp at Lv 15 / 19); S = the 0.2.1 F")
    # why the jar writes 7/3: the spec's own text 20:2.333333 flips EXACT .5 roundings (shown here, not shipped)
    Cfg.BASE_CURVE = SPEC_F.replace("20:2.3333333333333335", "20:2.333333")
    spec_l13 = lines5("Weapon_Staff_Wood", 13)
    curves()
    check(spec_l13[0] == "Damage at Lv 13: 10" and lines5("Weapon_Staff_Wood", 13)[0] == "Damage at Lv 13: 11",
          "AF2: why 7/3 - with the spec's 20:2.333333 a Lv 13 Wood staff swing (5 x 2.1 = 10.5) would read 10 instead of 0.2.4's 11; the jar keeps 11")
    check([round(F5(l_), 2) for l_ in (25, 30, 33, 35, 40, 45, 49, 60, 90, 100)] == [3.1, 4.5, 5.7, 6.5, 9.6, 13.6, 16.72, 22.5, 90.0, 90.0]
          and [round(H5(l_), 2) for l_ in (25, 30, 35, 40, 49, 100)] == [3.7, 5.4, 7.3, 9.6, 15.6, 88.0]
          and [round(S5(l_), 2) for l_ in (25, 40, 49, 100)] == [2.5, 3.0, 3.3, 5.0] and all(abs(R5(l_) - pyc("1:1.0,10:1.4,20:1.7,40:2.2,100:3.0", l_)) < 1e-12 for l_ in range(0, 101)),
          "AF2: spec 2.3 F column (25 3.10 ... 49 16.72, flat 90 from Lv 90), H (40 9.6, 100 88), S = the old F (40 3.0), R unchanged")
    RIDS = ["Weapon_Wand_Wood", "Weapon_Staff_Wood", "Weapon_Sword_Crude", "Weapon_Sword_Copper", "Weapon_Sword_Iron", "Weapon_Shortbow_Crude",
            "Weapon_Crossbow_Iron", "Weapon_Kunai", "Weapon_Spellbook_Fire", "Armor_Copper_Chest", "Armor_Copper_Head", "Armor_Iron_Chest",
            "Armor_Thorium_Chest", "Armor_Cloth_Cindercloth_Head", "Armor_Cloth_Wool_Chest"]

    diff20 = []
    RIDS = sorted(set(RIDS) | set(i_ for i_ in ALLW if bool(Data.isGear(i_))) | set(ARMOR_AZ))
    for iid_ in RIDS:
        for lv_ in range(1, 21):
            curves()
            a_ = lines5(iid_, lv_)
            kk_ = not iid_.startswith("Armor_") and int(Lvl.band(str(Base.baseOf(iid_)))[0]) <= 20
            ma_ = float(Base.weaponMult(gstack(iid_, lv_), False)) if kk_ else 0.0
            curves(OLDF, OLDF, OLDF)
            b_ = lines5(iid_, lv_)
            mb_ = float(Base.weaponMult(gstack(iid_, lv_), False)) if kk_ else 0.0
            # a family based ABOVE Lv 20 (Spellbook Fire / Frost / Demon / Rekindle at 30 / 35) gets its new K by design (spec 2.2): its
            # items below their band start (only an admin /gear level makes one) read differently - skipped; AF2's K check covers the band start
            if not kk_ and not iid_.startswith("Armor_") and lv_ < int(Lvl.band(iid_)[0]):
                continue
            if a_ != b_ or abs(ma_ - mb_) > 1e-6:
                diff20.append((iid_, lv_, a_, b_))
    curves()
    check(not diff20, "AF2: every tooltip line at item level 1-20 = 0.2.4's (%d items: every gear weapon + every armor of the model, x 20 levels; the hit "
          "multiplier too for every family based at Lv 1-20): %s" % (len(RIDS), diff20[:2]))
    bad21 = []
    for lv_ in range(21, 50):
        mw_ = float(Base.mult("Weapon_Sword_Crude", doc("Weapon_Sword_Crude", lv_), False))
        ms_ = float(Base.mult("Weapon_Wand_Wood", doc("Weapon_Wand_Wood", lv_), True))
        ha_ = float(Base.armorTarget("Armor_Copper_Chest", doc("Armor_Copper_Chest", lv_))[0])
        if abs(mw_ - pyc(SPEC_F, lv_)) > 1e-9 or abs(ms_ - pyc(SPEC_O, lv_)) > 1e-9 or abs(ha_ - 9.0 * pyc(SPEC_H, lv_)) > 1e-4:
            bad21.append((lv_, mw_, ms_, ha_))
    check(not bad21, "AF2: Lv 21-49: a Crude sword hit x F(L), a Wood wand SHOT x S(L), a Copper chestplate 9 x H(L) Health: %s" % bad21[:3])
    # spec 7.6 step 6: a Lv 25 Cobalt sword ~24 % above 0.2.4, a Lv 25 Cobalt chestplate +36 Health (was +24)
    old_cob = imap.get("Armor_Cobalt_Chest")
    imap.put("Armor_Cobalt_Chest", armor_item("Armor_Cobalt_Chest", "Chest", 23, 0.12, None))
    mc_new = float(Base.mult("Weapon_Sword_Cobalt", doc("Weapon_Sword_Cobalt", 25), False))
    hc_new = int(Base.rint(float(Base.armorTarget("Armor_Cobalt_Chest", doc("Armor_Cobalt_Chest", 25))[0])))
    curves(OLDF, OLDF, OLDF)
    mc_old = float(Base.mult("Weapon_Sword_Cobalt", doc("Weapon_Sword_Cobalt", 25), False))
    hc_old = int(Base.rint(float(Base.armorTarget("Armor_Cobalt_Chest", doc("Armor_Cobalt_Chest", 25))[0])))
    curves()
    check(abs(mc_new / mc_old - 1.24) < 1e-9 and hc_new == 36 and hc_old == 24 and "Health at Lv 25: +36" in lines5("Armor_Cobalt_Chest", 25),
          "AF2: spec 7.6 step 6 - a Lv 25 Cobalt sword hits x%.3f of 0.2.4 (3.1 / 2.5), a Lv 25 Cobalt chestplate 'Health at Lv 25: +36' (was +%d)" % (mc_new / mc_old, hc_old))
    # K stays on F: families whose base starts at Lv 1-20 keep K exactly (F_new = F_old there); bases starting above Lv 20 (the own-base
    # spellbooks, Kunai's own band ...) get a new K and their own items still deal EXACTLY vanilla at their band start (spec 2.2, critic F9)
    kch, kbad, kown = [], [], []
    gw_ = [i_ for i_ in ALLW if bool(Data.isGear(i_))]
    for i_ in gw_:
        b_ = str(Base.baseOf(i_))
        lb_ = int(Lvl.band(b_)[0])
        st_ = int(Lvl.band(i_)[0])
        curves()
        kn_ = float(Base.kOf(i_, False))
        mst_ = float(Base.mult(i_, doc(i_, st_), False))
        curves(OLDF, OLDF, OLDF)
        ko_ = float(Base.kOf(i_, False))
        mso_ = float(Base.mult(i_, doc(i_, st_), False))
        curves()
        if lb_ <= 20:
            if abs(kn_ - ko_) > 1e-6 * max(1.0, abs(ko_)):
                kbad.append((i_, ko_, kn_))
        else:
            kch.append((i_, lb_, round(ko_, 4), round(kn_, 4)))
        if b_ == i_ and abs(mst_ - mso_) > 1e-9 * max(1.0, abs(mso_)):
            kown.append((i_, mso_, mst_))
    check(not kbad and not kown and len(kch) >= 2, "AF2: K unchanged for every family whose base starts at Lv 1-20 (%d gear weapons); the bases starting above "
          "Lv 20 get a new K and every family base keeps EXACTLY its band-start multiplier: %s / %s" % (len(gw_), kbad[:3], kown[:3]))
    print("AF2. new K (bases starting above Lv 20): %s" % kch)
    t40 = table_row(40)
    check(t40 == ("58-77", 75, 48, "58-106", 154, 115, 154, 75), "AF2: Lv 40 through GearHit.weaponHit (real Damage objects): wand swings 58-77 / orb 75 (S keeps "
          "3.0), staff 48 / orb 75, sword 58-106 / thrust 154, shortbow full draw 115 / headshot 154: %s" % (t40,))
    t20 = table_row(20)
    check(t20 == ("14-19", 58, 12, "14-26", 37, 28, 37, 58), "AF2: Lv 20 through GearHit.weaponHit = 0.2.4's worked row: %s" % (t20,))
    sp_bad = []
    sp_ids = [x_ for x_ in ALLW if x_.startswith(("Weapon_Wand_", "Weapon_Staff_", "Weapon_Spellbook_")) and bool(Data.isGear(x_))]
    nshots = 0
    for i_ in sp_ids:
        for lv_ in (1, 6, 15, 20, 25, 30, 35, 40, 45, 49):
            curves()
            a1_, a2_ = Base.shots(i_, doc(i_, lv_)), Base.spellRange(i_, doc(i_, lv_))
            a_ = (None if a1_ is None else [str(x) for x in a1_[:2]], None if a2_ is None else [float(x) for x in a2_])
            curves(OLDF, OLDF, OLDF)
            b1_, b2_ = Base.shots(i_, doc(i_, lv_)), Base.spellRange(i_, doc(i_, lv_))
            b_ = (None if b1_ is None else [str(x) for x in b1_[:2]], None if b2_ is None else [float(x) for x in b2_])
            if a1_ is not None:
                nshots += 1
            if a_ != b_:
                sp_bad.append((i_, lv_, a_, b_))
    curves()
    check(not sp_bad and len(sp_ids) >= 10, "AF2: every wand / staff / spellbook 'Spell at Lv' range + Charged / Quick shot line at Lv 1-49 = 0.2.4's (S = the old "
          "F; %d ids, %d shot answers): %s" % (len(sp_ids), nshots, sp_bad[:3]))
    Cfg.BASE_SPELL = "1:1.0,40:2.0"
    Cfg.BASE_HP = "1:1.0,40:4.0"
    s_l, h_l = S5(40), float(Base.armorTarget("Armor_Copper_Chest", doc("Armor_Copper_Chest", 40))[0])
    Cfg.BASE_SPELL = "garbage"
    Cfg.BASE_HP = "1:0"
    s_b, h_b = S5(40), H5(40)
    curves()
    check(s_l == 2.0 and abs(h_l - 36.0) < 1e-4 and s_b == 3.0 and h_b == 9.6, "AF2: base.spellCurve / base.hpCurve are live (S(40) 2.0, Health 36) and an unreadable text -> its default")
    bt5 = str(Cfg.baseText())
    check("spell shots S = " + SPEC_O in bt5 and "armor Health (H = " + SPEC_H in bt5 and "F = " + SPEC_F in bt5, "AF2: the ready line names F, S and H")
    ds5 = str(Base.describe("Armor_Copper_Chest", doc("Armor_Copper_Chest", 40)))
    check("Health 86.4 (H 9.6; the item's own 9)" in ds5, "AF2: /gear read names H and the item's own Health: %s" % ds5)
    # gear:fn:curve (spec 7.3): the REAL GearFn in mode 10, the setup wiring
    gf_ = J("GearFn")(10)
    OAf = JArray(JObject)

    def qa(w_, l_):
        return gf_.apply(OAf([w_, Integer.valueOf(l_)]))
    ans_ = [qa("F", 20), qa("F", 40), qa("S", 40), qa("H", 40), qa("R", 40), qa("f", 25), qa(" h ", 100)]
    check([round(float(x_), 6) for x_ in ans_] == [2.333333, 9.6, 3.0, 9.6, 2.2, 3.1, 88.0] and all("Double" in str(type(x_)) or isinstance(x_, float) for x_ in ans_),
          "AF2: gear:fn:curve answers a Double: F(20) 2.333333, F(40) 9.6 (SkyyMobs' WARN wants >= 2 x F(20)), S(40) 3.0, H(40) 9.6, R(40) 2.2, any case: %s" % ans_)
    jd_ = JObject(qa("F", 40), JClass("java.lang.Object"))
    check(str(jd_.getClass().getName()) == "java.lang.Double", "AF2: gear:fn:curve returns java.lang.Double (%s)" % jd_.getClass().getName())
    nul_ = [gf_.apply(None), gf_.apply("F"), gf_.apply(OAf(["F"])), gf_.apply(OAf(["X", Integer.valueOf(4)])), gf_.apply(OAf(["F", "4"])),
            gf_.apply(OAf([Integer.valueOf(1), Integer.valueOf(4)]))]
    Cfg.BASE_CURVE = "1:1.0,40:2.0"
    lv_ans = float(qa("F", 40))
    curves()
    check(all(x_ is None for x_ in nul_) and lv_ans == 2.0, "AF2: gear:fn:curve - bad input / unknown name -> null (never throws); it reads the live row (F(40) 2.0 after an edit)")
    su5 = code("SkyyGearPlugin", "setup")
    ic_ = [i_ for i_, l_ in enumerate(su5) if '"gear:fn:curve"' in l_ and i_ + 1 < len(su5) and "GearFn" in su5[i_ + 1]]
    win_ = su5[max(0, ic_[0] - 2):ic_[0] + 8] if ic_ else []
    check(len(ic_) == 1 and any(("bipush 10" in l_) or ("iconst_10" in l_) for l_ in win_) and any("GearFn" in l_ for l_ in win_),
          "AF2: setup() puts gear:fn:curve = new GearFn(10) into the bridge (bytecode): %s" % [l_.strip() for l_ in win_])
    print("AF2. curves + gear:fn:curve done")

    # ---- AF3. Life Steal cap (spec 2.5): stealPay + the REAL GearFx.second payout on the real stat map
    Cfg.STEAL_MAX = 5.0
    Cfg.STEAL_S = 3
    a3 = [float(Fx.stealPay(50.0, 200.0)), float(Fx.stealPay(20.0, 200.0)), float(Fx.stealPay(0.0, 200.0)), float(Fx.stealPay(50.0, 0.0))]
    Cfg.STEAL_MAX = 0.0
    a3.append(float(Fx.stealPay(50.0, 200.0)))
    Cfg.STEAL_MAX = 5.0
    Cfg.STEAL_S = 1
    a3.append(float(Fx.stealPay(50.0, 200.0)))
    Cfg.apply(Props(), False)
    check(a3 == [30.0, 20.0, 0.0, 50.0, 50.0, 10.0], "AF3: one payout <= 5 %% x max Health x the window (200 HP, 3 s -> 30; 1 s -> 10); under the cap = all; "
          "0 = no cap; an unknown max Health = no cap: %s" % a3)
    se5 = code("GearFx", "second")
    ip5 = [i_ for i_, l_ in enumerate(se5) if "GearFx.stealPay" in l_]
    ia5 = [i_ for i_, l_ in enumerate(se5) if "GearFx.add" in l_]
    check(len(ip5) == 1 and any(i_ > ip5[0] for i_ in ia5) and any("getMax" in l_ for l_ in se5[max(0, ip5[0] - 12):ip5[0]]),
          "AF3: GearFx.second pays Life Steal through stealPay(owed, max Health) -> add (bytecode)")
    inv5 = None
    try:
        inv5 = JClass("com.hypixel.hytale.server.core.inventory.Inventory")()
    except Exception as ex_:
        check(False, "AF3: a bare Inventory could not be made (%s)" % ex_)
    if inv5 is not None:
        for i_ in range(4):
            slot(i_, None)
        settle()
        sec_ = []

        def pay3(owed_):
            sm_.setStatValue(JInt(HP_I), JFloat(10.0))
            Fx.LEECH.put(U2, JArray(JDouble)([float(owed_), 0.0]))
            try:
                Fx.second(U2, None, buf_, ref_v, inv5)
            except Exception as ex2_:
                sec_.append(str(ex2_))
            return float(hv_.get()), float(Fx.LEECH.get(U2)[0]) if Fx.LEECH.get(U2) is not None else -1.0
        try:
            fill_single(ENG + "modules.entity.damage.DamageModule")
        except Exception:
            pass
        p1_ = pay3(50.0)
        Cfg.STEAL_MAX = 0.0
        p2_ = pay3(50.0)
        Cfg.STEAL_MAX = 5.0
        p3_ = pay3(8.0)
        Cfg.apply(Props(), False)
        check(not sec_ and p1_ == (25.0, 0.0) and p2_ == (60.0, 0.0) and p3_ == (18.0, 0.0),
              "AF3: the REAL GearFx.second (max Health 100, window 3 s): 50 owed -> +15 (the cap; the rest is dropped, not carried), cap 0 -> +50, "
              "8 owed -> +8: %s %s %s %s" % (p1_, p2_, p3_, sec_[:1]))
        Fx.forget(U2)
    print("AF3. Life Steal cap done")

    # ---- AF4. Reforge LEVEL UP (Skyy LOCKED 2026-10-04): lvlInfo, GearForge.levelUp (coins first, refund), the page
    SW = "Weapon_Sword_Copper"           # band 10-18 (the built-in table)
    old_coin = dict((k_, bridge.get(k_)) for k_ in ("coins:fn:take", "coins:fn:get", "coins:fn:add"))
    wallet = {"bal": 1000000, "take": [], "add": []}

    @JImplements("java.util.function.Function")
    class Take5:
        @JOverride
        def apply(self, o_):
            a_ = int(o_[1])
            if wallet["bal"] < a_:
                return JBoolean(False)
            wallet["bal"] -= a_
            wallet["take"].append(a_)
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class Get5:
        @JOverride
        def apply(self, o_):
            return JLong(wallet["bal"])

    @JImplements("java.util.function.Function")
    class Add5:
        @JOverride
        def apply(self, o_):
            a_ = int(o_[1])
            wallet["bal"] += a_
            wallet["add"].append(a_)
            return JLong(wallet["bal"])
    bridge.put("coins:fn:take", Take5())
    bridge.put("coins:fn:get", Get5())
    bridge.put("coins:fn:add", Add5())
    skills_on()
    bridge.put("class:skill:" + str(U1), "Divinity")
    setlv(U1, "Divinity", 30)
    Cfg.apply(Props(), False)

    def li4(d_):
        r_ = Forge.lvlInfo(U1, SW, d_)
        return [int(r_[0]), int(r_[1]), int(r_[2]), int(r_[3]), int(r_[4]), str(r_[5])]
    l10 = li4(doc(SW, 10))
    l15 = li4(doc(SW, 15))
    setlv(U1, "Divinity", 12)
    l12 = li4(doc(SW, 12))
    setlv(U1, "Divinity", 30)
    dA = doc(SW, 14)
    dA.put("lvlA", JClass("org.bson.BsonBoolean")(True))
    lA = li4(dA)
    d0 = doc(SW, 13)
    d0.put("lvl0", JClass("org.bson.BsonInt32")(10))
    l0 = li4(d0)
    d16 = doc(SW, 16)
    d16.put("lvl0", JClass("org.bson.BsonInt32")(10))
    l16 = li4(d16)
    Cfg.LVLUP_CAP = 0
    lc0 = li4(doc(SW, 10))
    Cfg.LVLUP_CAP = 6
    Cfg.LVLUP_ON = False
    loff = li4(doc(SW, 10))
    Cfg.LVLUP_ON = True
    Cfg.PART_LEVELS = False
    lpl = li4(doc(SW, 10))
    Cfg.PART_LEVELS = True
    bridge.remove("class:skill:" + str(U1))
    Gate.forget(U1)
    lnc = li4(doc(SW, 10))
    bridge.put("class:skill:" + str(U1), "Divinity")
    Gate.forget(U1)
    dun = doc(SW, 10)
    dun.remove("lvl")
    lun = li4(dun)
    check(l10[:5] == [0, 10, 11, 16, 10] and l15[:5] == [0, 15, 16, 18, 15] and l12[0] == 5 and "your Divinity is 12" in l12[5]
          and lA[0] == 2 and l0[:5] == [0, 13, 14, 16, 10] and l16[0] == 4 and "+6" in l16[5] and lc0[0] == 4 and loff[0] == 1 and lpl[0] == 1
          and lnc[0] in (5, 6) and lun[:5] == [0, 10, 11, 16, 10],
          "AF4: lvlInfo - made at Lv 10 + Divinity 30 -> up to Lv 16 (+6); made at 15 -> the Copper cap 18; Divinity 12 at Lv 12 -> never above your level; an "
          "admin level; lvl0 kept (made at 10, now 13 -> 16 max); +6 reached; cap 0; switch off; part.levels off; no class; an unstamped item (band start "
          "10): %s" % [l10, l15, l12[:2], lA[:1], l0[:5], l16[:1], lc0[:1], loff[:1], lpl[:1], lnc[:1], lun[:5]])
    gv5 = SIC(sh(9))
    c5 = SIC(sh(9))
    all5 = JArray(IC)([c5, gv5])
    give5 = JArray(IC)([gv5])
    st5 = Data.put(IS(SW, 1), doc(SW, 10, [("str", 12)]), U1)
    c5.setItemStackForSlot(sh(0), st5)
    mods0 = str(Data.mods(Data.gearDoc(st5.getMetadata())))

    def up5(cont_=None, slot_=0, fpx_=None):
        cont_ = c5 if cont_ is None else cont_
        s_ = cont_.getItemStack(sh(slot_))
        return Forge.levelUp(cont_, slot_, SW, Forge.fp(s_) if fpx_ is None else fpx_, U1, "tester", give5, all5)

    def dnow(cont_=None, slot_=0):
        s_ = (c5 if cont_ is None else cont_).getItemStack(sh(slot_))
        return Data.gearDoc(s_.getMetadata())
    res_ = [up5() for _i in range(6)]
    d6 = dnow()
    taken6 = list(wallet["take"])
    r7 = up5()
    check([int(r_[0]) for r_ in res_] == [1] * 6 and int(Lvl.level(SW, d6)) == 16 and int(d6.get("lvl0").asNumber().intValue()) == 10
          and int(Data.num(d6, "lvU", 0)) == 6 and taken6 == [100 + 20 * L_ for L_ in range(11, 17)] and int(Data.rarity(d6)) == 0
          and str(Data.mods(d6)) == mods0 and int(r7[0]) == 0 and "already +6 over Lv 10" in str(r7[1]) and wallet["take"] == taken6,
          "AF4: six level ups Lv 10 -> 16 (coins 320, 340 ... 420 taken first, lvl0 10, lvU 6, rarity + modifiers unchanged), the 7th refused before any coin moves: %s"
          % str(r7[1]))
    st15 = Data.put(IS(SW, 1), doc(SW, 15), U1)
    c5.setItemStackForSlot(sh(1), st15)
    rb15 = [int(up5(slot_=1)[0]) for _i in range(4)]
    r15m = str(up5(slot_=1)[1])
    check(rb15 == [1, 1, 1, 0] and int(Lvl.level(SW, dnow(slot_=1))) == 18 and "caps at Lv 18" in r15m,
          "AF4: made at Lv 15 -> three level ups to the Copper cap 18, then refused (%s)" % r15m)
    wallet["bal"] = 10
    tk0 = len(wallet["take"])
    st11 = Data.put(IS(SW, 1), doc(SW, 11), U1)
    c5.setItemStackForSlot(sh(2), st11)
    rp = up5(slot_=2)
    wallet["bal"] = 1000000
    bridge.remove("coins:fn:take")
    rn = up5(slot_=2)
    bridge.put("coins:fn:take", Take5())
    rm = up5(slot_=2, fpx_="nope")
    ud5 = Data.put(IS(SW, 1), Roll.unidDoc(SW, 1, "drop"), U1)
    c5.setItemStackForSlot(sh(3), ud5)
    ru = up5(slot_=3)
    check(int(rp[0]) == 0 and "Not enough coins: this level up costs 340" in str(rp[1]) and int(rn[0]) == 0 and "Coins are not available" in str(rn[1])
          and int(rm[0]) == 0 and "moved or changed" in str(rm[1]) and int(ru[0]) == 0 and "Identify it first" in str(ru[1])
          and len(wallet["take"]) == tk0 and int(Lvl.level(SW, dnow(slot_=2))) == 11,
          "AF4: refused before any coin moves - not enough coins, no SkyyCoins, the item moved, unidentified: %s" % [str(x_[1])[:50] for x_ in (rp, rn, rm, ru)])
    # a stack of 2: one item is levelled, the other moves to a free storage / backpack slot (coins once)
    st2 = Data.put(IS(SW, 2), doc(SW, 12), U1)
    c5.setItemStackForSlot(sh(4), st2)
    tk1 = len(wallet["take"])
    r2 = up5(slot_=4)
    gq = sum(int(gv5.getItemStack(sh(i_)).getQuantity()) for i_ in range(9) if gv5.getItemStack(sh(i_)) is not None and not gv5.getItemStack(sh(i_)).isEmpty())
    check(int(r2[0]) == 1 and int(c5.getItemStack(sh(4)).getQuantity()) == 1 and int(Lvl.level(SW, dnow(slot_=4))) == 13 and gq == 1
          and len(wallet["take"]) == tk1 + 1 and r2[6] is not None, "AF4: a stack of 2 -> one item levelled (Lv 13), the other moved to a free slot, coins once")
    # the write fails -> refund, the item unchanged (a container that refuses the write)
    ctc5 = JClass("javassist.CtNewConstructor")
    ctm5 = JClass("javassist.CtNewMethod")
    cf5 = JClass("javassist.CtField")
    fb5 = jp.makeClass("com.hypixel.hytale.server.core.inventory.container.SkyyTestFailBox25", jp.get("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"))
    fb5.addField(cf5.make("public static boolean FAIL = false;", fb5))
    fb5.addConstructor(ctc5.make("public SkyyTestFailBox25(short n) { super(n); }", fb5))
    fb5.addMethod(ctm5.make("public com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction setItemStackForSlot(short s, "
                            "com.hypixel.hytale.server.core.inventory.ItemStack st) { if (FAIL) throw new IllegalStateException(\"test: no writes\"); "
                            "return super.setItemStackForSlot(s, st); }", fb5))
    FailBox = JClass(fb5.toClass(SIC.class_).getName())
    fbox = FailBox(sh(3))
    fbox.setItemStackForSlot(sh(0), Data.put(IS(SW, 1), doc(SW, 12), U1))
    FailBox.FAIL = True
    tk2, ad2, bal2 = len(wallet["take"]), len(wallet["add"]), wallet["bal"]
    rf = Forge.levelUp(fbox, 0, SW, Forge.fp(fbox.getItemStack(sh(0))), U1, "tester", give5, JArray(IC)([fbox, gv5]))
    FailBox.FAIL = False
    check(int(rf[0]) == -1 and "refunded" in str(rf[1]) and len(wallet["take"]) == tk2 + 1 and len(wallet["add"]) == ad2 + 1 and wallet["bal"] == bal2
          and wallet["add"][-1] == wallet["take"][-1] and int(Lvl.level(SW, Data.gearDoc(fbox.getItemStack(sh(0)).getMetadata()))) == 12,
          "AF4: the inventory refuses the write -> the coins come back (taken %d, refunded %d), the item stays Lv 12: %s" % (wallet["take"][-1], wallet["add"][-1], str(rf[1])))
    # the tooltip / sig follow the new level (gear:fn:sig includes it - the AH sees the change)
    s16 = c5.getItemStack(sh(0))
    sg_a = str(View.bridgeSig(SW, 0, doc(SW, 10, [("str", 12)])))
    sg_b = str(View.bridgeSig(SW, 0, Data.gearDoc(s16.getMetadata())))
    check(sg_a != sg_b and any("Lv 16" in x_ for x_ in lines5(SW, 16)), "AF4: the bridge sig changes with the level (the AH sees a levelled item as different)")
    # the Reforge page: the level line + the second button (built on a real UICommandBuilder / UIEventBuilder), the lvl click guards + success
    page = J("ReforgePage")(pr1_)
    ucb, ueb = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")(), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    st12 = Data.put(IS(SW, 1), doc(SW, 12), U1)
    page.anvil(ucb, ueb, U1, st12, None)
    def flat5(xs_):
        return " ".join(" ".join(str(getattr(x_, a_, "")) for a_ in ("type", "selector", "data", "text")) for x_ in xs_)
    cmds = flat5(ucb.getCommands())
    evs = flat5(ueb.getEvents())
    check("#SkyyGBtnLevel" in cmds and "Level up to Lv 13: 360 coins (it can reach Lv 18)" in cmds and "#SkyyGLvlTxt" in cmds and "#SkyyGBtnForge" in cmds
          and "#SkyyGBtnLevel" in evs and "lvl" in evs, "AF4: the Reforge page shows 'Level up to Lv 13: 360 coins (it can reach Lv 18)' + a Level up button bound to 'lvl'")
    ucb2, ueb2 = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")(), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    page.anvil(ucb2, ueb2, U1, c5.getItemStack(sh(0)), None)
    cmds2 = flat5(ucb2.getCommands())
    check("Max level" in cmds2 and "already +6 over Lv 10" in cmds2, "AF4: an item at +6 shows 'Max level' and why")
    page.selSec = -1
    page.lvlUp(None)
    i_nosel = str(page.info)
    if inv5 is not None:
        INVk = "com.hypixel.hytale.server.core.inventory.Inventory"
        acf(INVk, "hotbar").set(inv5, mkinv("Hotbar", SIC(sh(9)), 0))
        acf(INVk, "storage").set(inv5, mkinv("Storage", SIC(sh(18))))
        acf(INVk, "backpack").set(inv5, mkinv("Backpack", SIC(sh(9))))
        hb5 = inv5.getHotbar()
        hb5.setItemStackForSlot(sh(0), Data.put(IS(SW, 1), doc(SW, 12), U1))
        page.epoch = Gear.epoch(U1)
        ok_pick = bool(page.pick(inv5, 0, 0))
        page.lastForge = 0
        page.lvlUp(inv5)
        i_ok = str(page.info)
        check(i_nosel.startswith("-Pick an item") and ok_pick and i_ok.startswith("+Levelled up! Your") and "is now Lv 13" in i_ok and bool(page.fresh)
              and int(Lvl.level(SW, page.after)) == 13 and int(Lvl.level(SW, page.before)) == 12
              and int(Lvl.level(SW, Data.gearDoc(hb5.getItemStack(sh(0)).getMetadata()))) == 13,
              "AF4: ReforgePage.lvlUp - no item picked -> asked to pick one; picked -> levelled (Before Lv 12 / After Lv 13 columns): %s / %s" % (i_nosel, i_ok))
        hb5.setItemStackForSlot(sh(0), None)
    hd5 = code("ReforgePage", "handleDataEvent")
    check(any('"lvl"' in l_ or "lvl" in l_ for l_ in hd5) and any("ReforgePage.lvlUp" in l_ for l_ in hd5), "AF4: a 'lvl' click calls ReforgePage.lvlUp (bytecode)")
    for k_, v_ in old_coin.items():
        if v_ is None:
            bridge.remove(k_)
        else:
            bridge.put(k_, v_)
    bridge.remove("class:skill:" + str(U1))
    skills_off()
    print("AF4. Reforge level up done")

    # ---- AF5. THE VANILLA ARMOR BOX: hidden per item type, SkyyGear applies every stat of those pieces (equivalence with 0.2.4)
    ABox = J("GearABox")
    ABox.ON = True
    ABox.ORDERED = True
    ABox.SNAP.clear()
    RCTF = RCTc.FLAT

    def armor5(iid_, slot_, stats_, res_, base_=0.0, calc_=None, ar_=None):
        it_ = UZ.allocateInstance(ItemZ.class_)
        fz(ItemZ, "id").set(it_, iid_)
        fz(ItemZ, "maxStack").setInt(it_, 1)
        if ar_ is None:
            sm5 = I2O()
            for k_, v_ in stats_.items():
                sm5.put(JInt(k_), JArray(SMO)([SMO(MTG.MAX, CAL.ADDITIVE if calc_ is None else calc_, JFloat(float(v_)))]))
            ar_ = IARc(IASc.valueOf(slot_), float(base_), sm5, None)
            dr5 = HashMap()
            for c_, parts_ in res_.items():
                dr5.put(cause_obj[c_], JArray(RMODc)([RMODc(RCTF if t_ == "F" else PERC, JFloat(float(a_))) for t_, a_ in parts_]))
            fz(IARc, "damageResistanceValues").set(ar_, dr5)
        fz(ItemZ, "armor").set(it_, ar_)
        return it_
    EXTRA5 = {"Armor_Bronze_Chest": armor5("Armor_Bronze_Chest", "Chest", {HP_I: 15}, {"Physical": [("F", 2.0), ("P", 0.08)], "Projectile": [("P", 0.08)],
                                                                                         "Fall": [("P", 0.1)]}, 1.0),
              "Armor_Steel_Chest": armor5("Armor_Steel_Chest", "Chest", {HP_I: 0.1}, {}, 0.0, CAL.MULTIPLICATIVE),
              "Skyy_Hat_Test": armor5("Skyy_Hat_Test", "Head", {HP_I: 3}, {"Physical": [("P", 0.02)]})}
    shared_ = armor5("Armor_Iron_Head", "Head", {HP_I: 8}, {"Physical": [("P", 0.05)]})
    EXTRA5["Armor_Iron_Head"] = shared_
    EXTRA5["Armor_Iron_Legs"] = armor5("Armor_Iron_Legs", "Legs", None, None, ar_=shared_.getArmor())
    old_x5 = dict((k_, imap.get(k_)) for k_ in EXTRA5)
    for k_, v_ in EXTRA5.items():
        imap.put(k_, v_)
    AKEY5 = str(Fx.armorKey())

    def engine5():
        # the engine's StatModifiersManager.addArmorStatModifiers: one ADDITIVE "Armor" MAX modifier per stat = the ASSETS' sums (empty for hidden types)
        full_ = Armor.fullSums(varm_, JFloat(1.0))
        for si_ in range(int(sm_.size())):
            v_ = full_.get(Integer.valueOf(si_))
            if v_ is None or float(v_) == 0.0:
                sm_.removeModifier(JInt(si_), AKEY5)
            else:
                sm_.putModifier(JInt(si_), AKEY5, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(float(v_))))

    def settle5():
        apass(False)
        engine5()
        apass(True)

    def state5(causes_=("Physical", "Projectile", "Fall", "Fire", "Poison")):
        settle5()
        return (float(hv_.getMax()), float(sm_.get(JInt(1)).getMax())) + tuple(float(mobhit(100.0, c_)) for c_ in causes_)

    def same5(a_, b_):
        return len(a_) == len(b_) and all(abs(x_ - y_) < 1e-3 for x_, y_ in zip(a_, b_))

    # FIXER (data-migration critic item 2, a 0.2.4 player saved with the engine's own "Armor" Health modifier): the REAL engine drops a
    # stale Armor modifier at the first Recalculate after load - a loaded stat map gets a NEW StatModifiersManager (recalculate = true,
    # it is not in the codec), and applyStatModifiers removes the Armor key of every stat the worn pieces no longer give (hidden types
    # give nothing: their asset map is empty), so the lock never stacks on a stale vanilla amount
    def stale5():
        jl_ = JClass("java.lang.Class")
        smm_ = JClass("com.hypixel.hytale.server.core.entity.StatModifiersManager")
        esm_ = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
        fr_ = smm_.class_.getDeclaredField("recalculate")
        fr_.setAccessible(True)
        fresh_ = bool(fr_.getBoolean(esm_().getStatModifiersManager()))
        ap_ = None
        for m_ in smm_.class_.getDeclaredMethods():
            if str(m_.getName()) == "applyStatModifiers":
                ap_ = m_
        ap_.setAccessible(True)
        hi_ = int(JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes").getHealth())
        mx0_ = float(sm_.get(JInt(hi_)).getMax())
        sm_.putModifier(JInt(hi_), AKEY5, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(24.0)))
        stale_ = float(sm_.get(JInt(hi_)).getMax())
        ap_.invoke(None, sm_, JClass("it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap")())
        gone_ = sm_.getModifier(JInt(hi_), AKEY5) is None
        return fresh_, gone_, stale_ - mx0_, float(sm_.get(JInt(hi_)).getMax()) - mx0_

    PIECES = [("Armor_Copper_Chest", 1), ("Armor_Copper_Head", 0), ("Armor_Thorium_Chest", 1), ("Armor_Cloth_Cindercloth_Head", 0),
              ("Armor_Bronze_Chest", 1), ("Armor_Iron_Chest", 1), ("Armor_Cobalt_Chest", 1)]
    skills_on()
    bridge.put("class:skill:" + str(U2), "Divinity")
    setlv(U2, "Divinity", 50)
    for i_ in range(4):
        slot(i_, None)
    ABox.applyAll(False)
    settle5()
    # (a) hide: which types, the maps, the packet
    pk_it = Gear.item("Armor_Copper_Chest")
    pk_ar = pk_it.getArmor()
    sm_orig, dr_orig = pk_ar.getStatModifiers(), pk_ar.getDamageResistanceValues()
    fz(ItemZ, "cachedPacket").set(pk_it, JClass("java.lang.ref.SoftReference")(JObject("x", JClass("java.lang.Object"))))
    for k_ in [str(x) for x in Gear.ONCE.keySet()]:
        if k_.startswith("abox"):
            Gear.ONCE.remove(k_)
    msg_s = str(ABox.start())
    hid5 = sorted(str(x) for x in ABox.SNAP.keySet())
    pkt = pk_ar.toPacket()
    check(all(i_ in hid5 for i_, _s in PIECES) and "Armor_Copper_Legs" in hid5 and "Armor_Cloth_Wool_Chest" in hid5
          and not any(i_ in hid5 for i_ in ("Armor_Iron_Head", "Armor_Iron_Legs", "Armor_Steel_Chest", "Skyy_Hat_Test"))
          and not any(i_.startswith("Weapon_") for i_ in hid5) and "vanilla armor box hidden on %d gear armor types" % len(hid5) in msg_s,
          "AF5(a): start() hides every gear armor type of the model (%d: %s), never a shared ItemArmor / a non-additive one / a non-gear item / a weapon: %s"
          % (len(hid5), hid5, msg_s))
    check(Gear.ONCE.containsKey("aboxshared:Armor_Iron_Head") and Gear.ONCE.containsKey("aboxshared:Armor_Iron_Legs") and Gear.ONCE.containsKey("aboxcalc:Armor_Steel_Chest"),
          "AF5(a): one WARN each for the shared and the non-additive types (they keep the vanilla box, levelled the 0.2.4 way)")
    check(pk_ar.getStatModifiers().isEmpty() and pk_ar.getDamageResistanceValues().isEmpty() and fz(ItemZ, "cachedPacket").get(pk_it) is None
          and (pkt.statModifiers is None or pkt.statModifiers.isEmpty()) and pkt.damageResistance is None
          and int(SysJ.identityHashCode(ABox.stats("Armor_Copper_Chest", pk_ar))) == int(SysJ.identityHashCode(sm_orig))
          and int(SysJ.identityHashCode(ABox.res("Armor_Copper_Chest", pk_ar))) == int(SysJ.identityHashCode(dr_orig)),
          "AF5(a): the asset's maps are EMPTY (ItemArmor.toPacket: no Health / resistance for the client box), the packet cache dropped, GearABox keeps the "
          "original map objects")
    check(bool(ABox.hidden("Armor_Copper_Chest")) and not bool(ABox.hidden("Armor_Iron_Head")) and int(ABox.applyAll(True)) == 0
          and abs(float(ABox.snapHealth("Armor_Copper_Chest")) - 9.0) < 1e-6 and abs(float(ABox.snapRes("Armor_Copper_Chest", "Physical")) - 0.0648) < 1e-6
          and float(ABox.snapHealth("Armor_Iron_Head")) == -1.0, "AF5(a): hidden() / snapHealth / snapRes; hiding twice = once")
    # (b) EQUIVALENCE: every piece, state and level gives exactly 0.2.4's Health / Mana max and damage taken (Physical, Projectile, Fall, Fire,
    # Poison through the REAL GearHitSys -> engine ArmorDamageReduction -> GearArmorSys -> GearTrueSys) - with the box hidden SkyyGear applies it all
    eqbad = []
    neq = 0
    STATES = [("active", 50, True, True), ("under-level, armorNative on", 1, True, True), ("under-level, armorNative off", 1, False, True),
              ("levelling off (base.armorOn)", 50, True, False)]
    for iid_, sl_ in PIECES:
        for lv_ in (int(Lvl.band(iid_)[0]), 20, 30, 40):
            for nm_, skl_, nat_, arm_ in STATES:
                setlv(U2, "Divinity", skl_)
                Cfg.ARMOR_NATIVE = nat_
                Cfg.BASE_ARMOR = arm_
                for i_ in range(4):
                    slot(i_, None)
                slot(sl_, Data.put(IS(iid_, 1), doc(iid_, lv_), U2))
                ABox.applyAll(False)
                a_ = state5()
                ABox.applyAll(True)
                b_ = state5()
                neq += 1
                if not same5(a_, b_):
                    eqbad.append((iid_, lv_, nm_, a_, b_))
    # unidentified + a full set (four hidden pieces at once)
    for i_ in range(4):
        slot(i_, None)
    slot(1, Data.put(IS("Armor_Copper_Chest", 1), Roll.unidDoc("Armor_Copper_Chest", 2, "drop"), U2))
    for nat_ in (True, False):
        Cfg.ARMOR_NATIVE = nat_
        ABox.applyAll(False)
        a_ = state5()
        ABox.applyAll(True)
        b_ = state5()
        neq += 1
        if not same5(a_, b_):
            eqbad.append(("unidentified chest", nat_, a_, b_))
    Cfg.ARMOR_NATIVE = True
    Cfg.BASE_ARMOR = True
    setlv(U2, "Divinity", 50)
    for i_, iid_ in enumerate(("Armor_Copper_Head", "Armor_Bronze_Chest", "Armor_Copper_Legs", "Armor_Copper_Hands")):
        slot(i_, Data.put(IS(iid_, 1), doc(iid_, 30), U2))
    ABox.applyAll(False)
    a_ = state5()
    ABox.applyAll(True)
    b_ = state5()
    neq += 1
    if not same5(a_, b_):
        eqbad.append(("full set Lv 30", a_, b_))
    check(not eqbad and neq >= 110, "AF5(b): hidden == 0.2.4 in %d cases (7 pieces incl. FLAT + BaseDamageResistance + Fall (Bronze), Poison (Thorium), Mana "
          "(Cindercloth) x 4 levels x active / under-level (armorNative on, off) / levelling off + unidentified + a full set): %s" % (neq, eqbad[:2]))
    # (c) the engine alone applies NOTHING for a hidden piece (the box is really gone server side too); restore puts the engine's numbers back
    for i_ in range(4):
        slot(i_, None)
    slot(1, Data.put(IS("Armor_Copper_Chest", 1), doc("Armor_Copper_Chest", 10), U2))
    settle5()
    eng_h = mobhit(100.0, systems_=[adr_])
    full_h = mobhit(100.0)
    mx_h = float(hv_.getMax())
    lk_h = lockv()
    hr_h = bool(Armor.hasResDelta(U2, varm_))
    Cfg.BASE_ARMOR = False
    hr_h2 = bool(Armor.hasResDelta(U2, varm_))
    Cfg.BASE_ARMOR = True
    ABox.applyAll(False)
    settle5()
    eng_r = mobhit(100.0, systems_=[adr_])
    check(eng_h == 100.0 and abs(full_h - 100.0 * (1 - 0.0648 * 1.4)) < 1e-3 and abs(mx_h - 118.0) < 1e-4 and abs(lk_h - 18.0) < 1e-4 and hr_h and hr_h2
          and abs(eng_r - 93.52) < 1e-3 and int(SysJ.identityHashCode(pk_ar.getStatModifiers())) == int(SysJ.identityHashCode(sm_orig))
          and int(SysJ.identityHashCode(pk_ar.getDamageResistanceValues())) == int(SysJ.identityHashCode(dr_orig)),
          "AF5(c): hidden Lv 10 Copper chestplate: the engine alone 100 (applies nothing), the full chain %.3f (9.1 %%), max Health 118 = the lock adds all 18 "
          "(lock %.1f); hasResDelta even with levelling off; restore -> the engine's own 6.48 %% again (%.2f)" % (full_h, lk_h, eng_r))
    ABox.applyAll(True)
    # (d) the tooltip: levelled lines always (no box below), the other lines from the kept maps (Poison, Mana, FLAT Physical, Fall)
    tl_c1 = lines5("Armor_Copper_Chest", 1)
    tl_th = lines5("Armor_Thorium_Chest", 20)
    tl_cc = lines5("Armor_Cloth_Cindercloth_Head", 30)
    tl_br = lines5("Armor_Bronze_Chest", 15)
    Cfg.BASE_ARMOR = False
    tl_off = lines5("Armor_Copper_Chest", 10)
    tl_bro = lines5("Armor_Bronze_Chest", 15)
    Cfg.BASE_ARMOR = True
    ds_h = str(Base.describe("Armor_Copper_Chest", doc("Armor_Copper_Chest", 10)))
    check(tl_c1[:2] == ["Health at Lv 1: +9", "Resistance at Lv 1: 6.5% (physical, projectile)"] and "Poison resistance: 10%" in tl_th
          and "Mana: 10" in tl_cc and "Physical resistance: 2" in tl_br and "Fall resistance: 10%" in tl_br and not any("Projectile resistance" in x_ for x_ in tl_br)
          and "Health: 9" in tl_off and "Armor: 6.5% physical, 6.5% projectile" in tl_off and "Armor: 10% fall, 2 physical, 8% physical, 8% projectile" in tl_bro and "the item's own 9" in ds_h and "vanilla armor box hidden" in ds_h,
          "AF5(d): tooltip - a Lv 1 Copper chestplate shows its (levelled) lines, Thorium Poison, Cindercloth Mana, Bronze FLAT Physical + Fall from the kept maps; "
          "levelling off -> the vanilla numbers from the kept maps (Health + the 'Armor:' resistance line); /gear read: %s / %s / %s / %s" % (tl_c1, tl_br, tl_off, tl_bro))
    ABox.applyAll(False)
    Cfg.BASE_ARMOR = False
    tl_nh = lines5("Armor_Copper_Chest", 10)
    Cfg.BASE_ARMOR = True
    ABox.applyAll(True)
    check(not any(x_.startswith("Armor:") for x_ in tl_nh) and "Health: 9" in tl_nh, "AF5(d): a type NOT hidden keeps 0.2's levelling-off lines exactly (no resistance line - the vanilla box shows it): %s" % tl_nh)
    # (e) an asset reload: the fresh Item comes back with the vanilla maps (not hidden) -> the LoadedAssetsEvent listener hides it again
    LAEc = JClass("com.hypixel.hytale.assetstore.event.LoadedAssetsEvent")
    fresh_ = armor_item("Armor_Copper_Chest", "Chest", 9, 0.0648, None)
    imap.put("Armor_Copper_Chest", fresh_)
    was_h = bool(ABox.hidden("Armor_Copper_Chest"))
    lm5 = HashMap()
    lm5.put("Armor_Copper_Chest", fresh_)
    ev5 = LAEc(ItemZ.class_, None, lm5, False, None)
    J("GearBoxL")().accept(ev5)
    check(not was_h and bool(ABox.hidden("Armor_Copper_Chest")) and fresh_.getArmor().getStatModifiers().isEmpty()
          and abs(float(ABox.snapHealth("Armor_Copper_Chest")) - 9.0) < 1e-6,
          "AF5(e): a reloaded Copper chestplate (fresh maps) is not treated as hidden until the REAL GearBoxL listener (LoadedAssetsEvent) hides it again")
    # (f) switched off / unordered: nothing is hidden
    ABox.applyAll(False)
    ABox.ON = False
    off_ = str(ABox.start())
    n_off = ABox.SNAP.size()
    ABox.ON = True
    ABox.ORDERED = False
    uo_ = str(ABox.start())
    n_uo = ABox.SNAP.size()
    ev6 = LAEc(ItemZ.class_, None, lm5, False, None)
    n_ev = int(ABox.onLoaded(ev6))
    ABox.ORDERED = True
    ABox.STARTED = False
    n_pre = int(ABox.onLoaded(ev6))
    ABox.STARTED = True
    check(n_pre == 0 and not bool(ABox.hidden("Armor_Copper_Chest")), "AF5(f): the listener waits for start() (the first asset load: the shared-ItemArmor test needs the whole item map)")
    check(n_off == 0 and "view.hideArmorBox off" in off_ and n_uo == 0 and "unordered" in uo_ and n_ev == 0 and not bool(ABox.hidden("Armor_Copper_Chest")),
          "AF5(f): view.hideArmorBox off / unordered armor systems -> no type is hidden (start + listener): %s / %s" % (off_, uo_))
    # (g) the wiring (bytecode)
    st_pl = code("SkyyGearPlugin", "start")
    fxs = code("GearFx", "setup")
    bl5 = code("GearBoxL", "accept")
    check(any("GearABox.start" in l_ for l_ in st_pl) and any("GearABox.ON" in l_ for l_ in su5) and any("HIDE_ABOX" in l_ for l_ in su5)
          and any("GearABox.ORDERED" in l_ for l_ in fxs) and any("GearABox.onLoaded" in l_ for l_ in bl5) and any("GearBox.onLoaded" in l_ for l_ in bl5),
          "AF5(g): setup() reads view.hideArmorBox into GearABox.ON, GearFx.setup sets GearABox.ORDERED from the ordered registrations, start() hides, "
          "GearBoxL re-hides after a reload")
    ra5 = code("GearArmor", "fix")
    check(any("GearABox.anyHidden" in l_ for l_ in ra5) and any("GearArmor.hiddenRes" in l_ for l_ in ra5), "AF5(g): GearArmor.fix adds the hidden pieces' resistance (bytecode)")
    for i_ in range(4):
        slot(i_, None)
    ABox.applyAll(False)
    settle5()
    for k_, v_ in old_x5.items():
        if v_ is None:
            imap.remove(k_)
        else:
            imap.put(k_, v_)
    imap.put("Armor_Copper_Chest", armor_item("Armor_Copper_Chest", "Chest", 9, 0.0648, None))
    if old_cob is None:
        imap.remove("Armor_Cobalt_Chest")
    else:
        imap.put("Armor_Cobalt_Chest", old_cob)
    ABox.SNAP.clear()
    bridge.remove("class:skill:" + str(U2))
    skills_off()
    Cfg.apply(Props(), False)
    st5_ = stale5()
    check(st5_[0] and st5_[1] and abs(st5_[2] - 24.0) < 1e-3 and abs(st5_[3]) < 1e-3,
          "AF5(stale): a loaded stat map recalculates (new StatModifiersManager, recalculate=true) and the REAL applyStatModifiers drops a "
          "stale saved Armor Health modifier (+24 -> +0) when no worn piece gives Health through the asset (fresh, gone, stale, after): %s" % (st5_,))
    print("AF5. vanilla armor box done")

    # ---- AF6. migrate025 on scratch COPIES (the live Skyy_SkyyGear folder, read only), start twice, hand edits, CRLF, anchors, History, Undo
    MD5 = os.path.join(SCRATCH, "work", "mc025")
    shutil.rmtree(MD5, ignore_errors=True)
    cfg_quiet()
    CfgPub5 = J("CfgPub")
    OA5 = JArray(JObject)
    INFO_ADD = ("base.spellCurve, base.hpCurve, view.hideArmorBox, steal.maxPerSec, reforge.levelUp, reforge.levelCap, cost.levelUp.normal, "
                "cost.levelUp.unique, cost.levelUp.rare, cost.levelUp.legendary, cost.levelUp.fabled, cost.levelUp.mythic, cost.levelUp.set")

    def mcase(name_, data_=None, folder_=None):
        d_ = os.path.join(MD5, name_, "mods", "Skyy_SkyyGear")
        if folder_ is not None:
            shutil.copytree(folder_, d_)
        else:
            os.makedirs(d_)
        f_ = os.path.join(d_, "config.properties")
        if data_ is not None:
            open(f_, "wb").write(data_)
        Cfg.DIR = Paths.get(d_)
        Cfg.FILE = Paths.get(f_)
        return d_, f_

    def exp25(text_, spell_=SPEC_O, hp_=SPEC_H, rewrite_=True):
        """an independent Python copy of the decision table + placement (the live shape: base.curve, steal.windowS and cost.reforge.* lines exist)"""
        cr_ = "\r" if "\r\n" in text_ else ""
        ls_ = text_.split("\n")

        def key(l_):
            t_ = l_.rstrip("\r").lstrip()
            if not t_ or t_[0] in "#!":
                return None
            return re.split(r"\s*[=:]\s*|\s+", t_, 1)[0]
        ic_ = max(i_ for i_, l_ in enumerate(ls_) if key(l_) == "base.curve")
        iw_ = max(i_ for i_, l_ in enumerate(ls_) if key(l_) == "steal.windowS")
        ir_ = max(i_ for i_, l_ in enumerate(ls_) if (key(l_) or "").startswith("cost.reforge."))
        if rewrite_:
            ls_[ic_] = "base.curve=" + SPEC_F + cr_
        gc_ = [str(Cfg.GC_MARK), str(Cfg.GC_ROWC[0]), "base.spellCurve=" + spell_, str(Cfg.GC_ROWC[1]), "base.hpCurve=" + hp_, str(Cfg.GC_ROWC[2]), "view.hideArmorBox=true"]
        ins_ = sorted([(ic_ + 1, gc_), (iw_ + 1, [str(x) for x in Cfg.SM_ROWC] + [str(x) for x in Cfg.SM_ROWL]), (ir_ + 1, [str(x) for x in Cfg.LU_LINES])], reverse=True)
        for at_, block_ in ins_:
            ls_[at_:at_] = [x_ + cr_ for x_ in block_]
        return "\n".join(ls_)
    live_dir = os.path.dirname(LIVE)
    have_live = os.path.isfile(LIVE) and str(Cfg.GC_MARK_ID).encode("latin-1") not in open(LIVE, "rb").read()
    if have_live:
        d, f = mcase("a-live", folder_=live_dir)
    else:
        d, f = mcase("a-live", "\n".join(l_ for l_ in dt5.split("\n") if l_ not in set(gl5) and l_ not in set(lul) and not l_.startswith("steal.maxPerSec")
                                            and l_ != str(Cfg.SM_ROWC[0])).replace("base.curve=" + SPEC_F, "base.curve=" + SPEC_O).encode("latin-1"))
    old6 = rb(f)
    t6 = old6.decode("latin-1")
    b6, l6 = baks(d), clog(d)
    r6 = str(Cfg.migrate025())
    g6 = rb(f)
    exp6 = exp25(t6).encode("latin-1")
    check(g6 == exp6, "AF6(a): the %s gets exactly: base.curve value -> the new F, the 0.2.5 block right under it, steal.maxPerSec under steal.windowS, the "
          "level up rows + table under the last cost.reforge line; every other byte + the LF endings kept" % ("LIVE copy" if have_live else "0.2.4-shaped default file"))
    info6 = ("config.properties updated to the 0.2.5 level curves: base.curve %s -> %s (weapons grow faster after Lv 20; the old file is in config-history; "
             "Server Setup -> Changes can undo it); new settings: %s" % (SPEC_O, SPEC_F, INFO_ADD))
    check(r6 == info6, "AF6(a): one INFO line: %s" % r6[:200])
    po6, pn6 = props(t6), props(g6.decode("latin-1"))
    newk6 = sorted(set(pn6) - set(po6))
    check(all(pn6.get(k_) == v_ for k_, v_ in po6.items() if k_ != "base.curve") and pn6.get("base.curve") == SPEC_F
          and newk6 == sorted(["base.spellCurve", "base.hpCurve", "view.hideArmorBox", "steal.maxPerSec", "reforge.levelUp", "reforge.levelCap"]
                              + ["cost.levelUp." + r_ for r_ in R7]) and pn6["base.spellCurve"] == SPEC_O and pn6["base.hpCurve"] == SPEC_H,
          "AF6(a): every other value kept (hand-edited ones too, e.g. Skyy's level.material.Copper=%s), base.curve = the new F, the 13 new keys at their "
          "defaults (spell = the old F, armor Health = H)" % po6.get("level.material.Copper"))
    b6n, l6n = baks(d), clog(d)
    nb6 = [x_ for x_ in b6n if x_ not in b6]
    i6 = idx(d)
    check(len(nb6) == 1 and rb(os.path.join(d, "config-history", nb6[0])) == old6 and i6[-1].split("\t")[3:] == ["SkyyGear 0.2.5", "before the 0.2.5 level curves"],
          "AF6(a): ONE new History copy = the old bytes ('before the 0.2.5 level curves', who SkyyGear 0.2.5), the older copies kept")
    check(l6n[:len(l6)] == l6 and len(l6n) == len(l6) + 1 and l6n[-1].split("\t")[1:] == ["SkyyGear 0.2.5", "-", "update", "base.curve", SPEC_O, SPEC_F, "ok"]
          and re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$", l6n[-1].split("\t")[0]),
          "AF6(a): ONE config-changes.log line 'base.curve old -> new' (who SkyyGear 0.2.5, via update), the earlier lines kept")
    Cfg.load()
    check(str(Cfg.BASE_CURVE) == SPEC_F and str(Cfg.BASE_SPELL) == SPEC_O and str(Cfg.BASE_HP) == SPEC_H and float(Cfg.STEAL_MAX) == 5.0 and int(Cfg.LVLUP_CAP) == 6,
          "AF6(a): the loader reads the updated file (F new, S old, H, Life Steal 5, level cap 6)")
    r6b = str(Cfg.migrate025())
    check(r6b == "" and rb(f) == g6 and baks(d) == b6n and clog(d) == l6n, "AF6(b): a SECOND start changes nothing (file, History, change log byte-identical)")
    # (c) the whole setup() file chain twice on another copy: the second start leaves every file as it was
    if have_live:
        d2, f2 = mcase("c-chain", folder_=live_dir)

        def chain():
            Cfg.importRolls(Cfg.FILE, Paths.get(os.path.join(d2, "..", "Skyy_SkyyRolls", "reforge.properties")))
            for m_ in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025"):
                getattr(Cfg, m_)()
            Cfg.load()

        def snapdir(dd_):
            out_ = {}
            for rt_, _ds, fs_ in os.walk(dd_):
                for fn_ in fs_:
                    if fn_ != "gear.log":
                        out_[os.path.relpath(os.path.join(rt_, fn_), dd_)] = rb(os.path.join(rt_, fn_))
            return out_
        Log.FILE = None
        chain()
        s1 = snapdir(d2)
        chain()
        s2 = snapdir(d2)
        check(s1 == s2 and props(s1["config.properties"].decode("latin-1")).get("base.curve") == SPEC_F,
              "AF6(c): setup()'s whole file chain (importRolls, migrate011 ... migrate023, migrate025, load) twice on a copy of the live folder: the second start "
              "changes no file (%d files)" % len(s1))
    # (d) Undo through the config kit the way SkyyMenu sends it (set back to the log line's old value); the next start keeps it
    cfg_quiet()
    Cfg.DIR, Cfg.FILE = Paths.get(d), Paths.get(f)
    Cfg.load()
    CfgPub5.start(Paths.get(os.path.dirname(d)), None)
    fn5 = bridge.get("config:fn:SkyyGear")
    lg5 = [str(x) for x in fn5.apply(OA5(["log", Integer.valueOf(20)]))]
    un5 = fn5.apply(OA5(["set", "base.curve", SPEC_O, None, "console", "yes", "console"]))
    CfgPub5.flush()
    cfg_quiet()
    gu5 = rb(f).decode("latin-1")
    bu5 = str(Cfg.BASE_CURVE)
    ru5 = str(Cfg.migrate025())
    check(any("\tupdate\tbase.curve\t" in l_ and l_.endswith("\tok") for l_ in lg5) and un5 is not None and str(un5[0]) == "ok"
          and props(gu5).get("base.curve") == SPEC_O and bu5 == SPEC_O and ru5 == "" and props(rb(f).decode("latin-1")).get("base.curve") == SPEC_O,
          "AF6(d): Server Setup -> Changes lists the update line; Undo (set base.curve back) is accepted, applies live, and the next start keeps it")
    cfg_quiet()
    # (e) hand-edited / other shapes (synthetic, from the same text)
    tx6 = t6
    dE, fE = mcase("e-custom", tx6.replace("base.curve=" + SPEC_O, "base.curve=1:1.0,40:4.0", 1).encode("latin-1"))
    rE = str(Cfg.migrate025())
    pE = props(rb(fE).decode("latin-1"))
    check(pE.get("base.curve") == "1:1.0,40:4.0" and pE.get("base.spellCurve") == "1:1.0,40:4.0" and pE.get("base.hpCurve") == "1:1.0,40:4.0"
          and "kept (custom)" in rE and len(clog(dE)) == 0 and rb(fE).decode("latin-1") == exp25(tx6.replace("base.curve=" + SPEC_O, "base.curve=1:1.0,40:4.0", 1), "1:1.0,40:4.0", "1:1.0,40:4.0", False),
          "AF6(e): a HAND-SET base.curve is kept and copied into the Spell + Armor Health curves (flat gear stays flat), noted, no change-log line")
    dF, fF = mcase("f-new", tx6.replace("base.curve=" + SPEC_O, "base.curve=" + SPEC_F, 1).encode("latin-1"))
    rF = str(Cfg.migrate025())
    check(rb(fF).decode("latin-1") == exp25(tx6.replace("base.curve=" + SPEC_O, "base.curve=" + SPEC_F, 1), rewrite_=False) and len(clog(dF)) == 0
          and rF.startswith("config.properties: base.curve did not hold the 0.2.1 default"), "AF6(f): base.curve already the new F -> the defaults for S / H, no change-log line")
    tG = tx6.replace("steal.windowS=", "base.hpCurve=1:2\nsteal.maxPerSec=9\nsteal.windowS=", 1).replace("cost.reforge.set=", "cost.levelUp.rare=1,1\ncost.reforge.set=", 1)
    dG, fG = mcase("g-kept", tG.encode("latin-1"))
    rG = str(Cfg.migrate025())
    gG = rb(fG).decode("latin-1")
    pG = props(gG)
    check(pG.get("base.hpCurve") == "1:2" and pG.get("steal.maxPerSec") == "9" and pG.get("cost.levelUp.rare") == "1,1" and gG.count("base.hpCurve=") == 1
          and gG.count("steal.maxPerSec=") == 1 and gG.count("cost.levelUp.rare=") == 1 and "base.hpCurve is already in the file - kept" in rG
          and "cost.levelUp.rare is already in the file - kept" in rG and pG.get("cost.levelUp.set") == "1000,200" and pG.get("base.spellCurve") == SPEC_O,
          "AF6(g): keys already in the file are kept (noted), never doubled; only the missing ones are added")
    tH = tx6.replace("\r\n", "\n").replace("\n", "\r\n")
    dH, fH = mcase("h-crlf", tH.encode("latin-1"))
    Cfg.migrate025()
    check(rb(fH).decode("latin-1") == exp25(tH) and ("\r\n" + str(Cfg.GC_MARK) + "\r\n") in rb(fH).decode("latin-1"), "AF6(h): a CRLF file gets CRLF lines, value rewrite keeps its CR")
    tI = "\n".join(l_ for l_ in tx6.split("\n") if not l_.startswith(("base.", "steal.windowS", "cost.reforge."))) + "\nlast.key=1"
    dI, fI = mcase("i-noanchor", tI.encode("latin-1"))
    Cfg.migrate025()
    gI = rb(fI).decode("latin-1")
    check(gI.startswith(tI + "\n" + str(Cfg.GC_MARK)) and props(gI).get("steal.maxPerSec") == "5" and props(gI).get("cost.levelUp.set") == "1000,200"
          and props(gI).get("base.hpCurve") == SPEC_H, "AF6(i): no base.* / steal.windowS / cost.reforge line -> one block appended at the end (steal + level up rows inside it)")
    tJ = tx6.replace("base.curve=" + SPEC_O, "base.curve=1:1.0,4:1.6,\\\n   10:2.0,40:3.0,100:5.0", 1)
    dJ, fJ = mcase("j-continued", tJ.encode("latin-1"))
    rJ = str(Cfg.migrate025())
    pJ = props(rb(fJ).decode("latin-1"))
    check(pJ.get("base.curve") == SPEC_O and pJ.get("base.spellCurve") == SPEC_O and pJ.get("base.hpCurve") == SPEC_O and "kept (custom)" in rJ and len(clog(dJ)) == 0
          and "1:1.0,4:1.6,\\\n   10:2.0" in rb(fJ).decode("latin-1"), "AF6(j): a base.curve continued over two physical lines is never rewritten (kept, both curves copy it - the 0.2.4 numbers)")
    dK, fK = mcase("k-fresh", dt5.encode("latin-1"))
    check(str(Cfg.migrate025()) == "" and rb(fK) == dt5.encode("latin-1") and not baks(dK), "AF6(k): a fresh 0.2.5 file (marker inside) is never touched")
    dL, fL = mcase("l-blocked", old6)
    open(os.path.join(dL, "config-history"), "w").write("not a folder")
    rL = str(Cfg.migrate025())
    gL = rb(fL)
    os.remove(os.path.join(dL, "config-history"))
    rL2 = str(Cfg.migrate025())
    check(rL == "" and gL == old6 and rL2 == info6 and rb(fL) == exp6, "AF6(l): History blocked -> WARN, file untouched; the next start updates it")
    # (m) 400 random files vs java.util.Properties: every key the old file had keeps its value (but base.curve old -> new), the new keys appear once
    import random as _rnd
    rg_ = _rnd.Random(25)
    keys_ = ["base.curve", "steal.windowS", "cost.reforge.rare", "cost.reforge.set", "base.mode", "level.x", "a.b", "steal.maxPerSec", "base.hpCurve"]
    rbad = []
    for n_ in range(400):
        ls_ = []
        for _j in range(rg_.randint(0, 12)):
            k_ = rg_.choice(keys_)
            v_ = rg_.choice([SPEC_O, SPEC_F, "1", "2,3", "", "1:1.0,40:4.0", "x\\", " spaced value "])
            sep_ = rg_.choice(["=", " = ", ":", " "])
            ls_.append(rg_.choice(["", "  ", "#c ", "! "]) + k_ + sep_ + v_ if rg_.random() < 0.9 else rg_.choice(["", "# comment", "  ", "\\"]))
        txt_ = rg_.choice(["\n", "\r\n"]).join(ls_) + rg_.choice(["", "\n", "\\"])
        try:
            r_ = Cfg.gcUpdate(txt_)
        except Exception as ex_:
            rbad.append((n_, "throws", str(ex_)))
            continue
        if r_ is None:
            continue
        po_, pn_ = props(txt_), props(str(r_[0]))
        for k_, v_ in po_.items():
            want_ = SPEC_F if (k_ == "base.curve" and str(r_[1]).startswith("base.curve")) else v_
            if pn_.get(k_) != want_:
                rbad.append((n_, k_, v_, pn_.get(k_)))
        for k_ in ["base.spellCurve", "base.hpCurve", "view.hideArmorBox", "steal.maxPerSec", "reforge.levelUp", "reforge.levelCap"] + ["cost.levelUp." + r2_ for r2_ in R7]:
            if pn_.get(k_) is None:
                rbad.append((n_, "missing", k_))
        if Cfg.gcUpdate(str(r_[0])) is not None:
            rbad.append((n_, "not run-once"))
    check(not rbad, "AF6(m): 400 random files vs java.util.Properties: old values kept (base.curve only when it was the old default), every new key present, run once: %s" % rbad[:3])
    # (n) FIXER (data-migration critic item 1): a CRLF file whose anchor entry is its LAST line with no final newline - every inserted line
    # (and the old last line) ends in CRLF, never a bare LF; the critic's exact case + every anchor as the unterminated last line + 600 random
    # pure-CRLF files (with and without a final newline); an LF file stays pure LF
    def crlf_ok(t_):
        return all(t_[i_ - 1] == "\r" for i_ in range(len(t_)) if t_[i_] == "\n" and i_ > 0) and not t_.startswith("\n")
    def lf_ok(t_):
        return "\r" not in t_
    cbad = []
    for case_ in ["cost.reforge.rare = 200\r\ncost.reforge.normal=100",
                  "a.b=1\r\nsteal.windowS=3",
                  "a.b=1\r\nbase.curve=" + SPEC_O,
                  "steal.windowS=3\r\ncost.reforge.set=9\r\nbase.curve=" + SPEC_O,
                  "base.curve=" + SPEC_O + "\r\ncost.reforge.set=9\r\nsteal.windowS=3"]:
        r_ = Cfg.gcUpdate(case_)
        if r_ is None or not crlf_ok(str(r_[0])) or str(r_[0]).endswith("\n"):
            cbad.append((case_, None if r_ is None else str(r_[0])[-160:]))
        lf_ = case_.replace("\r\n", "\n")
        r2_ = Cfg.gcUpdate(lf_)
        if r2_ is None or not lf_ok(str(r2_[0])):
            cbad.append(("LF", lf_))
    rgc_ = _rnd.Random(2505)
    ncr_ = [0]
    for n_ in range(900):
        ls_ = [rgc_.choice(keys_) + rgc_.choice(["=", " = ", ":"]) + rgc_.choice([SPEC_O, "1", "2,3", "x"]) if rgc_.random() < 0.85 else rgc_.choice(["# c", ""]) for _j in range(rgc_.randint(1, 10))]
        t_ = "\r\n".join(ls_) + rgc_.choice(["", "\r\n"])
        if "\r\n" not in t_:
            continue
        ncr_[0] += 1
        r_ = Cfg.gcUpdate(t_)
        if r_ is not None and not crlf_ok(str(r_[0])):
            cbad.append((n_, t_[-80:]))
    check(not cbad, "AF6(n): CRLF kept when the anchor is the unterminated last line (critic case, 5 anchors, %d random CRLF files; LF stays LF): %s" % (ncr_[0], cbad[:3]))
    Cfg.FILE = None
    Cfg.DIR = None
    Cfg.apply(Props(), False)
    cfg_quiet()
    shutil.rmtree(MD5, ignore_errors=True)
    sq5 = code("SkyyGearPlugin", "setup")
    p_ = lambda n_: min([i_ for i_, l_ in enumerate(sq5) if n_ in l_] or [-1])
    check(0 <= p_("GearCfg.migrate023") < p_("GearCfg.migrate025") < p_("GearCfg.load"), "AF6: setup() runs migrate023 -> migrate025 -> load (bytecode)")
    print("AF6. migrate025 done")

    # ---- AF10. class byte-compare 0.2.4 -> 0.2.5: every difference must be one of the listed 0.2.5 parts
    EXPECT025 = AF_EXPECT or {}
    jar024 = os.path.join(HERE, "SkyyGear-0.2.4.jar")
    if os.path.isfile(jar024) and "cls_members" in dir():
        pa8 = Pool(False)
        pa8.appendClassPath(jar024)
        pa8.appendClassPath(B.SERVER_JAR)
        pa8.appendSystemPath()
        pb8 = Pool(False)
        pb8.appendClassPath(jar)
        pb8.appendClassPath(B.SERVER_JAR)
        pb8.appendSystemPath()
        na8 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar024).namelist() if n_.endswith(".class"))
        nb8 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar).namelist() if n_.endswith(".class"))
        diffs8 = {}
        for cn_ in sorted(set(na8) & set(nb8)):
            ma_, mb_ = cls_members(pa8, cn_), cls_members(pb8, cn_)
            dd_ = sorted(k_ for k_ in set(ma_) | set(mb_) if ma_.get(k_) != mb_.get(k_))
            if dd_:
                diffs8[cn_[len(PKG):]] = [("+" if k_ not in ma_ else ("-" if k_ not in mb_ else "~")) + k_ for k_ in dd_]
        print("AF10. class compare 0.2.4 -> 0.2.5: %s" % json.dumps(diffs8, sort_keys=True))
        check(sorted(set(nb8) - set(na8)) == [PKG + "GearABox"] and not (set(na8) - set(nb8)), "AF10: one class added (GearABox), none removed: %s" % sorted(set(na8) ^ set(nb8)))
        unexp8 = dict((c_, [m_ for m_ in v_ if m_ not in EXPECT025.get(c_, [])]) for c_, v_ in diffs8.items())
        unexp8 = dict((c_, v_) for c_, v_ in unexp8.items() if v_)
        missing8 = dict((c_, [m_ for m_ in v_ if m_ not in diffs8.get(c_, [])]) for c_, v_ in EXPECT025.items())
        missing8 = dict((c_, v_) for c_, v_ in missing8.items() if v_)
        check(not unexp8, "AF10: no difference outside the listed 0.2.5 parts: %s" % unexp8)
        check(not missing8, "AF10: every listed 0.2.5 part is really in the jar: %s" % missing8)
        za8, zb8 = zipfile.ZipFile(jar024), zipfile.ZipFile(jar)
        ea8 = [n_ for n_ in za8.namelist() if not n_.endswith(".class")]
        eb8 = [n_ for n_ in zb8.namelist() if not n_.endswith(".class")]
        ediff8 = sorted(n_ for n_ in set(ea8) | set(eb8) if n_ not in ea8 or n_ not in eb8 or za8.read(n_) != zb8.read(n_))
        check(ediff8 == ["manifest.json"], "AF10: non-class entries: only manifest.json changed: %s" % ediff8)
    else:
        check(False, "AF10: SkyyGear-0.2.4.jar (or the compare helper) not found - the class compare could not run")
    print("AF. 0.2.5 done")

'''

# AF10: the members 0.2.4 -> 0.2.5 may differ in (filled from the reviewed compare; anything else fails)
EXPECT025 = {
    # config kit: the 7 new rows
    'CfgFile': ['~<clinit>'],
    # config kit: version text
    'CfgFn': ['~m opExport([Ljava/lang/Object;)Ljava/lang/Object;'],
    # config kit: rows + VERSION 0.2.4 -> 0.2.5
    'CfgRows': ['~<clinit>', '~f VERSION', '~m header()[Ljava/lang/Object;'],
    # the armor box: hidden pieces added whole (lock + resistance)
    'GearArmor': ['~m fix(Ljava/util/UUID;FFLcom/hypixel/hytale/server/core/modules/entity/damage/DamageCause;Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;Lcom/hypixel/hytale/server/core/universe/world/World;ZLcom/hypixel/hytale/server/core/entity/effect/EffectControllerComponent;)F', '~m hasResDelta(Ljava/util/UUID;Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;)Z', '~m healthDelta(Ljava/util/UUID;Lcom/hypixel/hytale/server/core/inventory/ItemStack;F)F', '+m hiddenRes(Ljava/util/UUID;Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;Ljava/util/Map;ZLcom/hypixel/hytale/server/core/universe/world/World;ZZ)V', '~m lockSums(Ljava/util/UUID;Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;F)Ljava/util/HashMap;', '~m resDelta(Ljava/util/UUID;Lcom/hypixel/hytale/server/core/inventory/ItemStack;Ljava/lang/String;)F'],
    # S + H curves, mult (spell -> S), armorTarget (H), describe; reF reads the new CURVE_DEF constant
    'GearBase': ['~<clinit>', '+f HP', '+f HSRC', '+f SP', '+f SSRC', '~m armorTarget(Ljava/lang/String;Lorg/bson/BsonDocument;)[F', '~m clear()V', '+m curveH(I)D', '+m curveS(I)D', '~m describe(Ljava/lang/String;Lorg/bson/BsonDocument;)Ljava/lang/String;', '~m mult(Ljava/lang/String;Lorg/bson/BsonDocument;Z)D', '~m reF(Ljava/lang/String;)[Ljava/lang/Object;', '+m reH(Ljava/lang/String;)[Ljava/lang/Object;', '+m reS(Ljava/lang/String;)[Ljava/lang/Object;'],
    # the listener also re-hides armor
    'GearBoxL': ['~m accept(Ljava/lang/Object;)V'],
    # rows, loader, migrate025, costLevelUp, defaults text
    'GearCfg': ['~<clinit>', '+f BASE_HP', '+f BASE_SPELL', '~f CURVE_DEF', '+f CURVE_OLD', '+f DLU_BASE', '+f DLU_PER', '+f GC_LINES', '+f GC_MARK', '+f GC_MARK_ID', '+f GC_ROWC', '+f GC_ROWK', '+f GC_WHO', '+f HIDE_ABOX', '+f HP_DEF', '+f LU_BASE', '+f LU_LINES', '+f LU_PER', '+f LU_ROWC', '+f LU_ROWK', '+f LU_ROWL', '+f LU_TBLC', '+f LU_TBLL', '+f LVLUP_CAP', '+f LVLUP_ON', '+f SM_ROWC', '+f SM_ROWK', '+f SM_ROWL', '+f SPELL_DEF', '+f STEAL_MAX', '~m apply(Ljava/util/Properties;Z)V', '~m baseText()Ljava/lang/String;', '+m costLevelUp(II)J', '~m defaultsText()Ljava/lang/String;', '+m gcLog(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;', '+m gcUpdate(Ljava/lang/String;)[Ljava/lang/Object;', '+m migrate025()Ljava/lang/String;'],
    # gear:fn:curve (mode 10)
    'GearFn': ['~m apply(Ljava/lang/Object;)Ljava/lang/Object;', '+m curve(Ljava/lang/Object;)Ljava/lang/Object;'],
    # Reforge level up core
    'GearForge': ['+m levelUp(Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;ILjava/lang/String;Ljava/lang/String;Ljava/util/UUID;Ljava/lang/String;[Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;[Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;)[Ljava/lang/Object;', '+m lvOut(IIIILjava/lang/String;)[Ljava/lang/Object;', '+m lvlInfo(Ljava/util/UUID;Ljava/lang/String;Lorg/bson/BsonDocument;)[Ljava/lang/Object;'],
    # Life Steal cap (second), ORDERED flags (setup)
    'GearFx': ['~m second(Ljava/util/UUID;Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/inventory/Inventory;)V', '~m setup(Lcom/hypixel/hytale/server/core/plugin/JavaPlugin;)V', '+m stealPay(DD)D'],
    # level up document + origin
    'GearRoll': ['+m levelUp(Ljava/lang/String;Lorg/bson/BsonDocument;I)Lorg/bson/BsonDocument;', '+m origin(Ljava/lang/String;Lorg/bson/BsonDocument;)I'],
    # armor lines from the kept maps, levelled lines always for hidden types
    'GearView': ['~m armorLines(Ljava/lang/String;Ljava/util/ArrayList;)V', '~m levelArmorLines(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/ArrayList;)Z', '~m otherArmorLines(Ljava/lang/String;Ljava/util/ArrayList;)V'],
    # level line + button, lvlUp click, subtitle
    'ReforgePage': ['~m anvil(Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;Ljava/util/UUID;Lcom/hypixel/hytale/server/core/inventory/ItemStack;Lcom/hypixel/hytale/server/core/inventory/Inventory;)V', '~m build(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;Lcom/hypixel/hytale/component/Store;)V', '~m handleDataEvent(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Ljava/lang/String;)V', '+m lvlUp(Lcom/hypixel/hytale/server/core/inventory/Inventory;)V'],
    # migrate025 + GearABox.ON (setup), GearABox.start (start)
    'SkyyGearPlugin': ['~m setup()V', '~m start()V'],
}
RESTORE = "    # ---- restore the bare-JVM state this section changed (it is the last section; kept tidy anyway)\n"
sub(RESTORE, AF_SRC + "\n" + RESTORE)
sub("AF_EXPECT = None", "AF_EXPECT = %r" % (EXPECT025,))
_g = {"__name__": "__main__", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(src, BASE + " (run as the SkyyGear 0.2.5 harness)", "exec"), _g)
