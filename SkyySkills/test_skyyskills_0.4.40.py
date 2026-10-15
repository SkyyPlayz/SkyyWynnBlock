"""SkyySkills 0.4.40 - harness for the TREE buttons round (tools/skills_0_4_40_patch.py): SkillBonus.treeName / treeAvailable / treeFor and
the /skills + Stats page buttons for every tree SkyyTrees publishes (Alchemy, Smithing, Fishing, Ranching / Orchard -> Farming, the class
row -> /tree class).
Build first: python tools/skills_0_4_40_patch.py && python SkyySkills/build_skyyskills_0.4.40.py
             (+ SkyyRebirth/SkyyRebirth-0.3.3.jar for the inherited G39 phase; SkyyTrees/SkyyTrees-0.3.11.jar = the SET pin, read only)

    python SkyySkills/test_skyyskills_0.4.40.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.39 -> 0.4.40: exactly the planned members differ; SkillBonus +treeFor; no class added
  G40 EXECUTED with the REAL SkyyTrees 0.3.11 tree:names texts (TreeDefs.NAMES_CSV / NAMES_CSV_CLASS read from its jar):
               treeName per slot; treeAvailable with no SkyyTrees / SkyyTrees 0.1 (no tree:names) / 0.3.11 without and with the class
               tree / a short list; treeFor = a class slot only for the player's current class; the REAL SkillsPage.build: a TREE
               binding on every row SkyyTrees has a tree for (class row = sktree<Sorcery slot> for a Mage), the STATS buttons on the
               same spot in every row; the REAL StatsPage.build: SKILL TREE on Fishing / Ranching / Sorcery (own class) / a Combat view,
               none on another class's page (Fury for a Mage)
  0.4.39's phases on the 0.4.40 jar (G39, G38, F fakes, G37, R3, RS, RB, R, X, D live) - the checks pinning 0.4.39's version text or
               0.4.38's "no TREE for the 3 new rows" are expected to differ (EXPECTED40 below, re-checked in G40)
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.40"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.39.jar")
TREES_JAR = os.path.join(ROOT, "SkyyTrees", "SkyyTrees-0.3.11.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "skills0440", "sk")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")
os.environ.setdefault("SKYYROUTE_SESSION", os.path.join(SCRATCH, "routesession"))

EXPECT = {
    "SkillBonus": ["+m treeFor", "~m treeAvailable", "~m treeName"],
    "SkillsPage": ["~m build"],                              # treeFor(u, sl)
    "StatsPage": ["~m build", "~m handleDataEvent"],         # treeFor(u, s); a Combat view's click -> the class slot
    # version texts
    "SkillCfg": ["~m load"],
    "SkyySkillsPlugin": ["~m setup"],
    "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = []


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T39 = tmod("test_skyyskills_0.4.39.py", "t0439")
T38 = T39.T38
path = T38.path


def run_g40(out, jar, scratch, _home):
    from jpype import JClass, JArray, JImplements, JOverride, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, TREES_JAR], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, Sto, Defs, Bon = J("SkillCfg"), J("SkillStore"), J("SkillDefs"), J("SkillBonus")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    TD = JClass("com.skyy.trees.TreeDefs")
    csv, csv_cls = str(TD.NAMES_CSV), str(TD.NAMES_CSV_CLASS)
    K.check(csv == "Mining,Foraging,Farming,Cooking,Acrobatics,Exploration,Alchemy,Smithing,Fishing" and csv_cls == csv + ",Class",
            "G40 SkyyTrees 0.3.11 tree:names texts: %s / %s" % (csv, csv_cls))
    N = int(Defs.N)
    lab = [str(Defs.LABELS[i]) for i in range(N)]
    cls_slots = [int(x) for x in Defs.CLASS_SLOT]
    want_name = {"Mining": "mining", "Foraging": "foraging", "Farming": "farming", "Cooking": "cooking", "Acrobatics": "acrobatics",
                 "Exploration": "exploration", "Alchemy": "alchemy", "Smithing": "smithing", "Fishing": "fishing", "Ranching": "farming",
                 "Orchard": "farming"}
    got = dict((lab[i], None if Bon.treeName(i) is None else str(Bon.treeName(i))) for i in range(N))
    K.check(all(got[l] == w for l, w in want_name.items()) and all(got[lab[c]] == "class" for c in cls_slots) and got["Combat"] is None
            and Bon.treeName(-1) is None and Bon.treeName(N) is None, "G40 treeName: %s" % got)
    br = Sto.bridge()

    @JImplements("java.util.function.Function")
    class Const(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            return self.v
    lvl = Const(JClass("java.lang.Integer")(0))

    def setup(names, on=True):
        if on:
            br.put("tree:fn:level", lvl)
        else:
            br.remove("tree:fn:level")
        if names is None:
            br.remove("tree:names")
        else:
            br.put("tree:names", names)

    def avail():
        return sorted(lab[i] for i in range(N) if bool(Bon.treeAvailable(i)))
    setup(csv_cls, on=False)
    K.check(avail() == [], "G40 treeAvailable: SkyyTrees not running (no tree:fn:level) = no button anywhere")
    setup(None)
    K.check(avail() == sorted(["Mining", "Foraging", "Farming", "Cooking", "Ranching", "Orchard"]), "G40 treeAvailable: SkyyTrees 0.1 (no tree:names) = its 4 trees (+ Ranching / Orchard on Farming): %s" % avail())
    setup(csv)
    base = sorted(list(want_name))
    K.check(avail() == base, "G40 treeAvailable: SkyyTrees 0.3.11, class trees off = every gathering / crafting / movement skill, no class slot: %s" % avail())
    setup(csv_cls)
    K.check(avail() == sorted(base + [lab[c] for c in cls_slots]), "G40 treeAvailable: SkyyTrees 0.3.11 + Class = also every class slot: %s" % avail())
    setup(" mining , ACROBATICS")
    K.check(avail() == ["Acrobatics", "Mining"], "G40 treeAvailable: a short list (spaces, any case) = only those: %s" % avail())
    setup("Farming")
    K.check(avail() == ["Farming", "Orchard", "Ranching"], "G40 treeAvailable: Farming alone = Farming + Ranching + Orchard (one shared tree)")
    UUID = JClass("java.util.UUID")
    me = UUID(0x5117, 40)
    mage = cls_slots[[str(c) for c in Defs.CLASSES].index("Mage")]
    fury = int(Defs.FURY)
    K.check(lab[mage] == "Sorcery" and lab[fury] == "Fury", "G40 slots: Sorcery %d, Fury %d" % (mage, fury))
    setup(csv_cls)
    br.remove("class:" + me.toString())
    K.check(Bon.treeFor(me, mage) is None and Bon.treeFor(None, mage) is None and str(Bon.treeFor(me, int(Defs.FISHING))) == "fishing",
            "G40 treeFor: no class = no class-tree button; Fishing still 'fishing'")
    br.put("class:" + me.toString(), "Mage")
    K.check(str(Bon.treeFor(me, mage)) == "class" and Bon.treeFor(me, fury) is None and str(Bon.treeFor(me, int(Defs.RANCHING))) == "farming"
            and Bon.treeFor(me, int(Defs.COMBAT)) is None, "G40 treeFor: a Mage -> Sorcery 'class', Fury none, Ranching 'farming', Combat none")
    setup(csv)
    K.check(Bon.treeFor(me, mage) is None, "G40 treeFor: class trees off in SkyyTrees (no ,Class) = no class-tree button")
    # ================================================================ the REAL pages
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    dd = [0] * (2 * N)
    for sl in (0, 1, 2, 16, 17, 18, 10, 11, 12, 4, 13, mage):
        dd[sl] = 4000
    Sto.DATA.put(me.toString(), JArray(JLong)(dd))

    def run_build(pg):
        b, ev = UCB(), UEB()
        err = None
        try:
            pg.build(None, b, ev, None)
        except Exception as e:
            err = str(e)
        cmds = [(None if c.selector is None else str(c.selector), None if c.data is None else str(c.data), None if c.text is None else str(c.text))
                for c in b.getCommands()]
        evs = [None if e.data is None else str(e.data) for e in ev.getEvents()]
        return err, cmds, evs
    rows = [int(x) for x in Defs.ROW_SLOTS]
    for names, cls_on in ((csv_cls, True), (csv, False)):
        setup(names)
        err, cmds, evs = run_build(J("SkillsPage")(pr))
        K.check(err is None, "G40 /skills (class trees %s): built: %s" % (cls_on, err))
        tb = sorted(int(e.split("sktree")[1].split('"')[0]) for e in evs if e and "sktree" in e)
        want = sorted([sl for sl in rows if sl != int(Defs.COMBAT)] + ([mage] if cls_on else []))
        K.check(tb == want, "G40 /skills (class trees %s): TREE bindings on %s (want %s)" % (cls_on, [lab[x] for x in tb], [lab[x] for x in want]))
        import re
        kids = {}
        for c in cmds:
            m = re.match(r"^#SkyySkRow(\d+)$", c[0] or "")
            if m and c[2]:
                kids.setdefault(int(m.group(1)), []).append(c[2])
        K.check(sorted(kids) == list(range(len(rows))), "G40 /skills (class trees %s): %d rows drawn" % (cls_on, len(kids)))
        tree_rows = sorted(i for i in kids if any(("TextButton #SkyySkTree%d " % i) in k for k in kids[i]))
        K.check(tree_rows == sorted(i for i, sl in enumerate(rows) if (mage if sl == int(Defs.COMBAT) else sl) in want),
                "G40 /skills (class trees %s): a TREE button on rows %s" % (cls_on, tree_rows))

        # the columns stay put: each row = panel, TREE button or the same-size gap, STATS button - the same anchors in every row
        def anch(k):
            a = re.search(r"Anchor: \(([^)]*)\)", k)
            return re.sub(r"Height: \d+", "Height: h", a.group(1)) if a else None
        shapes = set()
        for i in kids:
            ks = kids[i]
            shapes.add((len(ks), tuple(anch(k) for k in ks), re.sub(r"\d+", "#", ks[-1].split("{")[0])))
        K.notes.append("G40 row shapes (class trees %s): %s" % (cls_on, sorted(shapes)))
        K.check(len(shapes) == 1 and list(shapes)[0][0] == 3 and "TextButton #SkyySkStat#" in list(shapes)[0][2],
                "G40 /skills (class trees %s): every row = panel + TREE/gap + STATS with the same anchors: %s" % (cls_on, sorted(shapes)))
    setup(csv_cls)
    for sl, want, what in ((int(Defs.FISHING), True, "Fishing"), (int(Defs.RANCHING), True, "Ranching"), (int(Defs.ALCHEMY), True, "Alchemy"),
                           (mage, True, "Sorcery (own class)"), (int(Defs.COMBAT), True, "a Combat view (= the Mage's Sorcery)"),
                           (fury, False, "Fury (not the player's class)")):
        err, cmds, evs = run_build(J("StatsPage")(pr, sl))
        has = any("sttree" in (e or "") for e in evs)
        K.check(err is None and has == want, "G40 Stats page %s: SKILL TREE %s (got %s, err %s)" % (what, want, has, err))
    br.remove("class:" + me.toString())
    err, cmds, evs = run_build(J("StatsPage")(pr, int(Defs.COMBAT)))
    K.check(err is None and not any("sttree" in (e or "") for e in evs), "G40 Stats page Combat with no class: no SKILL TREE")
    Sto.DATA.remove(me.toString())
    setup(None, on=False)
    K.save()


# 0.4.39's phases on this jar: checks that pin 0.4.39's version text or 0.4.38's "no TREE for the 3 new rows" differ on purpose
EXPECTED40 = ("G config: the fresh xp.properties ends with the 0.4.39 block", "G page (trees True): TREE buttons only where SkyyTrees has a tree")


def wrap(fn):
    def run(out, jar, scratch, home):
        tmp = out + ".i40.json"
        fn(tmp, jar, scratch, home)
        d = json.load(open(tmp))
        K = HK.Child(out)
        K.ok, K.notes = d["ok"], d["notes"]
        for f in d["fails"]:
            if any(f.startswith(e) for e in EXPECTED40):
                K.ok += 1
                K.notes.append("expected in 0.4.40 (re-checked in G40): " + f[:140])
            else:
                K.fails.append(f)
        K.save()
    return run


if __name__ == "__main__":
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("g40", run_g40), ("g39", wrap(T39.run_g39)), ("g38", wrap(T39.wrap(T38.run_g38))), ("fake15", T38.run_fake15),
                   ("fake25", T38.run_fake25), ("g37", wrap(T39.wrap(T38.run_g37))), ("r3", wrap(T39.wrap(T38.run_r3))),
                   ("restart", T38.run_restart), ("r1", T38.run_r1), ("route", T38.run_route), ("exec", T38.run_exec),
                   ("live", wrap(T39.wrap(T38.run_live)))],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
