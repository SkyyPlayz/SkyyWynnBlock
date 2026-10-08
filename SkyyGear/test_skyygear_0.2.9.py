"""Bare-JVM check for SkyyGear 0.2.9 (THE MONK WEAPONS SCALE LIKE THE SAME-METAL SWORD: SkyyArmory 0.1.7's Weapon_Bo_<Metal>,
Weapon_Fist_Gauntlets_<Metal> and Weapon_Fist_Wraps_<Cloth> take Weapon_Sword_<metal>'s K - the kunai-twin rule generalised; Skyy LOCKED
docs/answered/gear.md 2026-10-07 MONK WEAPONS round, research/cloud/Monk-Kit-Spec.md 1.1 / 2.1). The 0.2.8 harness
(SkyyGear/test_skyygear_0.2.8.py, read only: every 0.1 ... 0.2.8 section, itself on the 0.2.7 harness text) runs on the 0.2.9 jar with
VERSION 0.2.9 and the new section AJ.

    python SkyyGear/test_skyygear_0.2.9.py [--jar <SkyyGear-0.2.9.jar>] [--dir <scratch folder>] [--live <config.properties>] [--keep]

  AJ 0.2.9 - every new path EXECUTED on the real classes:
     AJ1 GearBase.monkMetal / kunaiTwin on the 19 Monk ids (gauntlets + bo -> Weapon_Sword_<metal>, wraps -> Weapon_Sword_<the cloth's metal
         column>), the kunai still -> its daggers, vanilla ids / unknown metals / a bare prefix -> themselves;
     AJ2 K follows the twin: kOf + ratio of every Monk id == the twin sword's (so SkyyArmory's share of the sword holds at every level); the
         levels are untouched (band of each Monk id == 0.2.8's look); negative control: TWIN_PRE blanked -> the gauntlets are their own id again;
     AJ3 the class byte-compare 0.2.8 -> 0.2.9 (every difference listed) + the non-class entries (only manifest.json).
  The carried AH3 (start twice on a live copy) runs on the 0.2.9 jar unchanged; the carried AI4 (0.2.7 -> 0.2.8 compare) is history (AJ3).
Scratch: only under --dir (default tools/dev/scratch/gear029/harness), deleted at the end unless --keep. Exit code 1 on any unexpected failure.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
H28 = os.path.join(HERE, "test_skyygear_0.2.8.py")
_t28 = open(H28, encoding="utf-8").read()
_cut = _t28.rindex('_g = {"__name__": "__main__"')
_n28 = {"__name__": "skyygear_h28", "__file__": H28, "__builtins__": __builtins__}
exec(compile(_t28[:_cut], H28 + " (the 0.2.8 harness text, not run)", "exec"), _n28)
src = _n28["src"]
DEV28 = _n28["DEV27"] + _n28["DEVIATIONS28"]


def sub(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "harness text changed: anchor count %d (want %d): %s" % (n, count, old[:120])
    src = src.replace(old, new)


DEVIATIONS29 = [
    ("AD3: the other", "pre-existing (the pinned 0.2.8 harness fails it the same way): the live SET pins SkyyArmory 0.1.6 = 32 weapon item files (0.1.7: "
     "+19) where the 0.2.2 check counted 0.1's 15; its point holds - no other jar reads the breakdowns or ships an EntityUI asset (both lists empty)"),
    ("AG10: SkyyGear-0.2.5.jar", "pre-existing (the pinned 0.2.8 harness fails it the same way): the 0.2.4 -> 0.2.5 compare jar is no longer on disk - "
     "history; AJ3 compares 0.2.8 -> 0.2.9"),
]
sub('VERSION = "0.2.8"\nDEVIATIONS = %r' % (DEV28,), 'VERSION = "0.2.9"\nDEVIATIONS = %r' % (DEV28 + DEVIATIONS29,))
sub('os.path.join(TOOLS, "dev", "scratch", "gear028", "harness")', 'os.path.join(TOOLS, "dev", "scratch", "gear029", "harness")')
sub('print("DEVIATION (0.2.5/0.2.6/0.2.7/0.2.8, expected):"', 'print("DEVIATION (0.2.5/0.2.6/0.2.7/0.2.8/0.2.9, expected):"')
sub('expected 0.2.5 / 0.2.6 / 0.2.7 / 0.2.8 deviations (%d listed kinds seen)', 'expected 0.2.5 / 0.2.6 / 0.2.7 / 0.2.8 / 0.2.9 deviations (%d listed kinds seen)')
# AI4 (0.2.7 -> 0.2.8 compare) is history: AJ3 compares 0.2.8 -> 0.2.9
sub('''    jar027 = os.path.join(HERE, "SkyyGear-0.2.7.jar")
    if os.path.isfile(jar027) and "cls_members" in dir():''', '''    jar027 = None          # 0.2.9: the 0.2.7 -> 0.2.8 compare is history - AJ3 compares 0.2.8 -> 0.2.9
    if jar027 is None:
        print("AI4. NOTE (0.2.9) the 0.2.7 -> 0.2.8 class compare is history - AJ3 compares 0.2.8 -> 0.2.9")
    elif os.path.isfile(jar027) and "cls_members" in dir():''')

AJ_SRC = r'''    # ======================================================================================================================== AJ 0.2.9
    print("AJ. 0.2.9: the Monk weapon twin (K follows the same-metal sword) - executed, class compare")
    Cfg.apply(Props(), False)
    MKM_ = ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")
    MKW_ = (("Linen", "Copper"), ("Cotton", "Iron"), ("Silk", "Thorium"), ("Cindercloth", "Cobalt"), ("Shadoweave", "Adamantite"))
    MONK_ = dict([("Weapon_Bo_" + m_, "Weapon_Sword_" + m_) for m_ in MKM_] + [("Weapon_Fist_Gauntlets_" + m_, "Weapon_Sword_" + m_) for m_ in MKM_]
                 + [("Weapon_Fist_Wraps_" + c_, "Weapon_Sword_" + col_) for c_, col_ in MKW_])
    Base.clear()
    tw9 = dict((i_, str(Base.kunaiTwin(i_))) for i_ in MONK_)
    mm9 = dict((i_, str(Base.monkMetal(i_))) for i_ in MONK_)
    oth9 = [str(Base.kunaiTwin(i_)) for i_ in ("Weapon_Kunai_Copper", "Weapon_Sword_Copper", "Weapon_Fist_Gauntlets_Foo", "Weapon_Bo_", "Weapon_Bo", "Weapon_Staff_Bo_Wood",
                                              "Weapon_Fist_Claws_Copper")]
    check(tw9 == MONK_ and all(mm9[i_] == MONK_[i_][len("Weapon_Sword_"):] for i_ in MONK_)
          and oth9 == ["Weapon_Daggers_Copper", "Weapon_Sword_Copper", "Weapon_Fist_Gauntlets_Foo", "Weapon_Bo_", "Weapon_Bo", "Weapon_Staff_Bo_Wood",
                       "Weapon_Fist_Claws_Copper"] and Base.monkMetal("Weapon_Sword_Copper") is None,
          "AJ1: the 19 Monk ids twin to the same-metal sword (wraps: Linen Copper ... Shadoweave Adamantite), the kunai still to its daggers, vanilla "
          "ids / an unknown metal / a bare prefix / the vanilla Bo / later claws keep themselves: %s %s" % (sorted(set(tw9.values())), oth9))
    kb9 = dict((i_, (float(Base.kOf(i_, False)), float(Base.ratio(i_)))) for i_ in MONK_)
    ks9 = dict((i_, (float(Base.kOf(MONK_[i_], False)), float(Base.ratio(MONK_[i_])))) for i_ in MONK_)
    band9 = dict((i_, [int(x_) for x_ in Lvl.band(i_)]) for i_ in MONK_)
    keep9 = str(Defs.TWIN_PRE[0])
    Defs.TWIN_PRE[0] = "zzz"
    Base.clear()
    neg9 = str(Base.kunaiTwin("Weapon_Fist_Gauntlets_Copper"))
    Defs.TWIN_PRE[0] = keep9
    Base.clear()
    check(kb9 == ks9 and all(v_[0] > 0.0 for v_ in kb9.values()) and len(set(round(v_[0], 6) for v_ in kb9.values())) > 1
          and band9["Weapon_Bo_Copper"][:2] == [10, 18] and band9["Weapon_Fist_Gauntlets_Mithril"][:2] == [40, 49]
          and band9["Weapon_Fist_Wraps_Linen"][:2] == [10, 17] and band9["Weapon_Fist_Wraps_Cindercloth"][:2] == [30, 37] and neg9 == "Weapon_Fist_Gauntlets_Copper",
          "AJ2 (the sword share holds WITH SkyyGear): every Monk id's kOf + ratio == its twin sword's (e.g. Copper gauntlets %s = Copper sword %s), the "
          "bands untouched (bo / gauntlets by metal, wraps by SkyyGear's cloth rows); negative control: TWIN_PRE blanked -> the gauntlets are their "
          "own id again: %s" % (kb9["Weapon_Fist_Gauntlets_Copper"], ks9["Weapon_Fist_Gauntlets_Copper"], neg9))
    print("AJ1/2. twins %s; K (gauntlets / bo / wraps Copper column) %.4f / %.4f / %.4f" % (len(tw9), kb9["Weapon_Fist_Gauntlets_Copper"][0],
                                                                                          kb9["Weapon_Bo_Copper"][0], kb9["Weapon_Fist_Wraps_Linen"][0]))
    # ---- AJ3. class byte-compare 0.2.8 -> 0.2.9
    EXPECT029 = @@EXPECT029@@
    jar028 = os.path.join(HERE, "SkyyGear-0.2.8.jar")
    if os.path.isfile(jar028) and "cls_members" in dir():
        pa9 = Pool(False)
        pa9.appendClassPath(jar028)
        pa9.appendClassPath(B.SERVER_JAR)
        pa9.appendSystemPath()
        pb9 = Pool(False)
        pb9.appendClassPath(jar)
        pb9.appendClassPath(B.SERVER_JAR)
        pb9.appendSystemPath()
        na9 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar028).namelist() if n_.endswith(".class"))
        nb9 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar).namelist() if n_.endswith(".class"))
        diffs9 = {}
        for cn_ in sorted(set(na9) & set(nb9)):
            ma_, mb_ = cls_members(pa9, cn_), cls_members(pb9, cn_)
            dd_ = sorted(k_ for k_ in set(ma_) | set(mb_) if ma_.get(k_) != mb_.get(k_))
            if dd_:
                diffs9[cn_[len(PKG):]] = [("+" if k_ not in ma_ else ("-" if k_ not in mb_ else "~")) + k_ for k_ in dd_]
        print("AJ3. class compare 0.2.8 -> 0.2.9: %s" % json.dumps(diffs9, sort_keys=True))
        check(na9 == nb9, "AJ3: no class added or removed: %s" % sorted(set(na9) ^ set(nb9)))
        unexp9 = dict((c_, [m_ for m_ in v_ if m_ not in EXPECT029.get(c_, [])]) for c_, v_ in diffs9.items())
        unexp9 = dict((c_, v_) for c_, v_ in unexp9.items() if v_)
        missing9 = dict((c_, [m_ for m_ in v_ if m_ not in diffs9.get(c_, [])]) for c_, v_ in EXPECT029.items())
        missing9 = dict((c_, v_) for c_, v_ in missing9.items() if v_)
        check(not unexp9, "AJ3: no difference outside the listed 0.2.9 parts: %s" % unexp9)
        check(not missing9, "AJ3: every listed 0.2.9 part is really in the jar: %s" % missing9)
        za9, zb9 = zipfile.ZipFile(jar028), zipfile.ZipFile(jar)
        ea9 = [n_ for n_ in za9.namelist() if not n_.endswith(".class")]
        eb9 = [n_ for n_ in zb9.namelist() if not n_.endswith(".class")]
        ediff9 = sorted(n_ for n_ in set(ea9) | set(eb9) if n_ not in ea9 or n_ not in eb9 or za9.read(n_) != zb9.read(n_))
        check(ediff9 == ["manifest.json"], "AJ3: non-class entries: only manifest.json changed: %s" % ediff9)
    else:
        check(False, "AJ3: SkyyGear-0.2.8.jar (or the compare helper) not found - the class compare could not run")
    Cfg.apply(Props(), False)
    print("AJ. 0.2.9 done")

'''
EXPECT029 = {
    # VERSION text only: CfgRows VERSION, the export header, the fresh file's first line, the ready line
    'CfgFn': ['~m opExport([Ljava/lang/Object;)Ljava/lang/Object;'],
    'CfgRows': ['~<clinit>', '~f VERSION', '~m header()[Ljava/lang/Object;'],
    'GearCfg': ['~m defaultsText()Ljava/lang/String;'],
    'SkyyGearPlugin': ['~m setup()V'],
    # the three new tables
    'GearDefs': ['~<clinit>', '+f TWIN_PRE', '+f TWIN_CLOTH', '+f TWIN_COL'],
    # the twin
    'GearBase': ['+m monkMetal(Ljava/lang/String;)Ljava/lang/String;', '~m kunaiTwin(Ljava/lang/String;)Ljava/lang/String;'],
}
AJ_SRC = AJ_SRC.replace("@@EXPECT029@@", repr(EXPECT029))
RESTORE = "    # ---- restore the bare-JVM state this section changed (it is the last section; kept tidy anyway)\n"
sub(RESTORE, AJ_SRC + "\n" + RESTORE)
_g = {"__name__": "__main__", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(src, H28 + " (run as the SkyyGear 0.2.9 harness)", "exec"), _g)
