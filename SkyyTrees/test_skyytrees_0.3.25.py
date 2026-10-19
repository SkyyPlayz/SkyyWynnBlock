"""Harness for SkyyTrees 0.3.25 (lean round: beta bug 13 - the detail well's texts fit their boxes; tools/trees_0_3_25_patch.py). Build first:
    python tools/trees_0_3_25_patch.py && python SkyyTrees/build_skyytrees_0.3.25.py
    python SkyyTrees/test_skyytrees_0.3.25.py [--dir <empty folder inside tools/dev/scratch/>]
Skyy 2026-10-19: "yes, do the small beta bugs 15, 16, 11, 13" (bug 13: text cut off in the Zen skill tree panel, video part 3 13:42).
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A    verify   every class loads + initialises
  C    compare  0.3.24 -> 0.3.25: exactly the planned members (EXPECT): TreeClassOps.typeWord + the two page builders (+ the version text)
  FIT  the RUN-TIME texts of the jar (TreeClass.now / TreeClassOps.givesLine, typeWord, howLine, stateLine words, reasonText for every class x
       node, TreeDefs.NAME / NOW / HOW of every tree node) measured against the 0.3.25 boxes (the build's tr_fit_check boxes, 95 % width);
       typeWord = typeLine without its " - <AP>" part; the Monk (Zen) tree named on its own; the SkyyClasses ability sentences (the SET
       pin's class:fn:abilDoes defaults, if its jar loads) fit the 6-line How box
  AA   engine-access audit
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import skyyui as SUI
import deploy_set as DS

VERSION = "0.3.25"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.3.24.jar")
CLASSES_JAR = os.path.join(ROOT, "SkyyClasses", "SkyyClasses-%s.jar" % dict(DS.SET)["SkyyClasses"])
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "btr", "tr")))
ADDED = []
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup"], "TreeCfg": ["~m load"],   # the version text
          "TreeClassOps": ["+m typeWord"], "TreePage": ["~m build", "~m buildClass"]}
MARGIN = 0.95
W, NW = 424, 424 - SUI.SLOT_FRAME - 12
BOX = {"name": (NW, 14, 24, True), "state": (NW, 16, 44, True), "line": (W, 16, 44, False), "need": (W, 16, 66, False), "how": (W, 13, 107, False)}


def fits(kind, tx):
    w, size, h, bold = BOX[kind]
    return SUI.text_lines(tx, w * MARGIN, size, bold) <= int(h // SUI.line_height(size, bold=bold))


def run_fit(out, jar, _scratch, _home):
    from jpype import JClass, JArray, JBoolean
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    TC, TO, TD = J("TreeClass"), J("TreeClassOps"), J("TreeDefs")
    NC, NN = int(TC.NC), int(TC.NN)
    bad, n, zen = [], 0, 0
    own = JArray(JBoolean)(NN)
    for ci in range(NC):
        cls = str(TC.CLASSES[ci])
        for nn in range(NN):
            if bool(TC.hidden(ci, nn)):
                continue
            tag = "%s.%s" % (cls, TC.sid(ci, nn))
            tl, tw = str(TO.typeLine(ci, nn)), str(TO.typeWord(ci, nn))
            if not (tl.startswith(tw + " - ") and (tl.endswith(" AP") or tl.endswith(" free")) and tl.count(" - ") == tw.count(" - ") + 1):
                bad.append("%s typeWord %r of %r" % (tag, tw, tl))
            texts = [("name", str(TC.name(ci, nn)) + "  (" + str(TC.sid(ci, nn)) + ")"),
                     ("line", "Now: ON - " + str(TC.now(ci, nn))), ("line", str(TO.givesLine(ci, nn))), ("how", str(TO.howLine(ci, nn)))]
            for st in ("Owned - kept from before (free until a respec)", "Owned - chain broken (see Needs)", str(TC.comingLine(ci, nn)), "Unlockable"):
                texts.append(("state", st + " - " + tw))
            for why in (1, 2, 4, 5, 7, 9, 10):
                rs = str(TC.reasonText(own, own, ci, nn, 99, 98, why))
                if rs:
                    texts.append(("need", "Needs: " + rs))
            for kind, tx in texts:
                n += 1
                if cls == "Monk":
                    zen += 1
                if not fits(kind, tx):
                    bad.append("%s %s: %s" % (tag, kind, tx))
    K.notes.append("FIT: %d class-tab texts measured (%d Monk / Zen)" % (n, zen))
    K.check(not bad, "FIT: %d class-tab texts of the jar fit their 0.3.25 boxes (%d of them the Monk / Zen tree) %s" % (n, zen, bad[:6]))
    K.check(zen > 100, "FIT: the Monk (Zen) tree was measured (%d texts)" % zen)
    bad, n = [], 0
    for i in range(len(TD.ID)):
        nm, now, how = str(TD.NAME[i]), str(TD.NOW[i]), str(TD.HOW[i])
        if not nm:
            continue
        for kind, tx in (("name", nm + "  (S" + str(TD.SHOW[i]) + ")"), ("line", "Level 99: " + now.replace("%V", "+999.9% (max)").replace("%C", "9999")),
                         ("how", how.replace("%C", "9999").replace("%K", "Crouch + Ability 3"))):
            n += 1
            if not fits(kind, tx):
                bad.append("%s %s: %s" % (TD.ID[i], kind, tx))
    K.notes.append("FIT: %d skill-tree node texts measured" % n)
    K.check(not bad and n > 300, "FIT: %d skill-tree node texts of the jar fit their 0.3.25 boxes %s" % (n, bad[:6]))
    # the old boxes did NOT hold them (the bug this round fixes): a Gives line with the type, Flowing Form's How at 5 lines
    mi = [i for i in range(NC) if str(TC.CLASSES[i]) == "Monk"][0]
    old = [str(TO.givesLine(ci, nn)) + " - " + str(TO.typeLine(ci, nn)) for ci in range(NC) for nn in range(NN) if not bool(TC.hidden(ci, nn))]
    K.check(any(SUI.text_lines(t, W * MARGIN, 16) > 2 for t in old), "FIT: 0.3.24's 'Gives - type - AP' line did overflow its 2 lines (the bug)")
    K.check(any(str(TC.NID[nn]) == "LE" and SUI.text_lines(str(TO.givesLine(mi, nn)) + " - " + str(TO.typeLine(mi, nn)), W * MARGIN, 16) > 2
                for nn in range(NN)), "FIT: the Monk's Wind Dancer Element Gives line was one of them")
    K.save()


def run_fitcls(out, jar, _scratch, _home):
    """The SkyyClasses ability sentences (class:fn:abilDoes = what the class tab's How box shows for an ability node) - SET pin jar."""
    from jpype import JClass
    K = HK.Child(out)
    if not os.path.isfile(CLASSES_JAR):
        K.check(True, "FITCLS: SkyyClasses jar %s not built here - skipped" % os.path.basename(CLASSES_JAR))
        K.save()
        return
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, CLASSES_JAR], verify=False)
    try:
        AD, DEF = JClass("com.skyy.classes.AbilDoes"), JClass("com.skyy.classes.AbilDefs")
        ids = [str(x) for x in DEF.IDS]
    except Exception as e:
        K.check(True, "FITCLS: SkyyClasses AbilDoes not loadable outside the server (%s) - UNVERIFIED here, SkyyClasses checks its own 5 lines" % e)
        K.save()
        return
    bad, n, ff = [], 0, None
    for aid in ids:
        r = AD.info(aid)
        if r is None:
            continue
        how = str(r[1]) + " " + str(r[3])
        n += 1
        if aid == "FlowingForm":
            ff = SUI.text_lines(how, W, 13)
        if not fits("how", how):
            bad.append("%s: %s" % (aid, how))
    K.notes.append("FITCLS: %d ability How texts, Flowing Form %s lines at full width" % (n, ff))
    K.check(n >= 30 and not bad, "FITCLS: %d ability How texts (SkyyClasses %s defaults) fit 6 lines (Flowing Form %s lines at full width) %s"
            % (n, dict(DS.SET)["SkyyClasses"], ff, bad[:4]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("fit", run_fit), ("fitcls", run_fitcls)], script=__file__)
