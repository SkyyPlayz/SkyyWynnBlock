"""SkyyRebirth 0.5.2 - harness for COMBAT INTO CLASS, the SkyyRebirth part (tools/rebirth_0_5_2_patch.py): the Nexus loses its Combat arm (10
arms), Combat Echo = the Class arm's KILL ECHO (same saved key Combat.echo, costs, reader); Head Start's text; the rail's Adventure row opens
/tree acrobatics. Build first: python tools/rebirth_0_5_2_patch.py && python SkyyRebirth/build_skyyrebirth_0.5.2.py

    python SkyyRebirth/test_skyyrebirth_0.5.2.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Deploys + rolls back TOGETHER with SkyyTrees 0.6.0, SkyyClasses 0.1.47, SkyySkills 0.4.64.
Every 0.5.1 phase, run from test_skyyrebirth_0.5.1.py's own source with ONLY these expectations moved to 0.5.2 (each substitution asserted
once): the version / jar / script names (0.5.1 -> 0.5.2, the old jar 0.5.0 -> 0.5.1), 11 -> 10 arm names, the rail's third row /tree
acrobatics, and the jar check "vs the old jar only the manifest + the keep files" -> "only the manifest + the map (the Combat arm left the
layout)". Then:
  arms  EXECUTED: the RbTree node Combat.echo is named Kill Echo, sits on the Class arm of the map (NARMN), keeps its max / cost / strength
        and its reader (rebirth:reads via tree:reads:SkyySkills xp.combat); RbTree.echo of a profile with node.Combat.echo=2 = the same value
        as 0.5.1 (no power change); xp.combat (rebirth:fn:stat "combatxp") unchanged; no "Combat" arm label on any zoom; Head Start's text
NOT COVERED (UNVERIFIED in game): the look of the re-laid-out Nexus at 100 / 150 / 200 %.
"""
import os, sys, re, importlib.util, types, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "cls060", "rb")]
import skyybuild as B
import harness_kit as HK

SRC51 = os.path.join(HERE, "test_skyyrebirth_0.5.1.py")
SUBS = [   # (old, new) - every one asserted to occur exactly once in the 0.5.1 harness
    ('''K.check(g.startswith('"""SkyyRebirth 0.5.1 - build script') and g.count('VERSION = "0.5.1"') == 1, "S header + VERSION")''',
     '''K.check(g.startswith('"""SkyyRebirth 0.5.2 - build script') and g.count('VERSION = "0.5.2"') == 1, "S header + VERSION")'''),
    ('VERSION = "0.5.1"', 'VERSION = "0.5.2"'),
    ('OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.5.0.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.5.1.jar")'),
    ('GEN_OLD = os.path.join(HERE, "build_skyyrebirth_0.5.0.py")', 'GEN_OLD = os.path.join(HERE, "build_skyyrebirth_0.5.1.py")'),
    ('PATCH = os.path.join(TOOLS, "rebirth_0_5_1_patch.py")', 'PATCH = os.path.join(TOOLS, "rebirth_0_5_2_patch.py")'),
    ('''    K.eq(ch_, sorted(["manifest.json"] + [MAPRES + "Z%dK.txt" % i for i in range(1, ZN)]), "J vs 0.5.0: only the manifest + the 2 new keep files (every picture byte-identical)")''',
     '''    K.eq([n for n in ch_ if not n.startswith(MAPDIR) and not n.startswith(MAPRES)], ["manifest.json"], "J vs 0.5.1: only the manifest + the map (the Combat arm left the layout)")'''),
    ('''        K.check(len(labels) == 11, "J z%d: 11 arm names" % zi)''', '''        K.check(len(labels) == 10, "J z%d: 10 arm names (no Combat arm)" % zi)'''),
    ('''    for q, cmd in enumerate(("tree mining", "tree smithing", "tree combat", "tree class")):''',
     '''    for q, cmd in enumerate(("tree mining", "tree smithing", "tree acrobatics", "tree class")):'''),
]
_src = open(SRC51, encoding="utf-8").read()
for _o, _n in SUBS:
    assert _src.count(_o) == 1, "the 0.5.1 harness changed - this substitution no longer fits: %s" % _o[:80]
    _src = _src.replace(_o, _n)
_src = _src.replace('if __name__ == "__main__":', 'if False:')
T = types.ModuleType("test_skyyrebirth_0_5_1_on_0_5_2")
T.__file__ = SRC51
_argv = list(sys.argv)
exec(compile(_src, SRC51 + " (0.5.2 expectations)", "exec"), T.__dict__)
sys.argv[:] = _argv
VERSION, JAR, OLD_JAR, RB, SCRATCH = T.VERSION, T.JAR, T.OLD_JAR, T.RB, T.SCRATCH
assert VERSION == "0.5.2" and OLD_JAR.endswith("SkyyRebirth-0.5.1.jar")
EXPECT = {   # checked 2026-10-23 (the class compare vs 0.5.1 of the first harness run): the version text (CfgFn, CfgRows, RbMig, RbStore, the plugin),
            # the node name / text (RbTree), the 10-arm layout (RbMap), the rail command + the Kill Echo line (RbPage)
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "RbMap": ["~<clinit>"], "RbMig": ["~m migrate"],
    "RbPage": ["~<clinit>", "~m buildK", "~m fillTree", "~m kSets", "~m trees"], "RbStore": ["~m writeNow"], "RbTree": ["~<clinit>"],
    "SkyyRebirthPlugin": ["~m setup"],
}


def run_arms(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(RB + n)
    Tr, Mp = J("RbTree"), J("RbMap")
    ids = [str(x) for x in Tr.NID]
    k = ids.index("Combat.echo")
    K.eq(int(Tr.I_COMBAT), k, "ARM I_COMBAT = the Combat.echo node (saved key unchanged)")
    names = [str(x) for x in Tr.NNAME]
    K.eq(names[k], "Kill Echo", "ARM its name: Kill Echo")
    narm = [str(x) for x in Mp.NARMN]
    K.eq(narm[k], "Class", "ARM it sits on the Class arm of the map")
    K.check("Combat" not in narm, "ARM no node on a Combat arm")
    g = open(T.GEN, encoding="utf-8").read()
    o = open(T.GEN_OLD, encoding="utf-8").read()
    pat = re.compile(r'tnode\("Combat\.echo", "[^"]+", "[^"]+", (\d+), (\d+), (\d+), (\d+),')
    K.eq(pat.search(g).groups(), pat.search(o).groups(), "ARM same arm index / max / cost / strength as 0.5.1 (no power change)")
    K.check('reader=("SkyySkills", "xp.combat", _S56))   # 0.5.2' in g, "ARM the same reader (tree:reads:SkyySkills xp.combat)")
    P = JClass("java.util.Properties")()
    P.setProperty("node.Combat.echo", "2")
    e2 = float(Tr.echo(P, k))
    K.check(e2 > 0.0, "ARM a profile with Kill Echo 2: echo %.3f" % e2)
    K.check("in every tree (the class tree twice)" in g, "ARM Head Start's text names the class tree twice")
    z = zipfile.ZipFile(jar)
    for zi in range(3):
        t = z.read("com/skyy/rebirth/map/Z%d.txt" % zi).decode("utf-8")
        K.check('Text: "Combat"' not in t and 'Text: "Class"' in t, "ARM z%d: no Combat arm label, the Class label there" % zi)
    K.save()


def run_arms_old(out, jar, scratch, _home):
    """the same echo on the 0.5.1 jar (a separate JVM): the value Kill Echo 2 must equal"""
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=False)
    Tr = JClass(RB + "RbTree")
    P = JClass("java.util.Properties")()
    P.setProperty("node.Combat.echo", "2")
    K.notes.append("OLD echo=%r" % float(Tr.echo(P, int(Tr.I_COMBAT))))
    K.save(echo=float(Tr.echo(P, int(Tr.I_COMBAT))))


def run_arms_eq(out, jar, scratch, _home):
    """both echo values (the two phases' results) are the same"""
    import json
    K = HK.Child(out)
    a = json.load(open(os.path.join(scratch, "armsold.json")))
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=False)
    Tr = JClass(RB + "RbTree")
    P = JClass("java.util.Properties")()
    P.setProperty("node.Combat.echo", "2")
    K.eq(float(Tr.echo(P, int(Tr.I_COMBAT))), float(a["echo"]), "ARM Kill Echo 2 = Combat Echo 2 of 0.5.1 (the same strength)")
    K.save()


if __name__ == "__main__":
    assert os.path.isfile(B.JAVASSIST), B.JAVASSIST
    phases = [("static", T.run_static), ("jar", T.run_jar), ("vp", T.T40.run_vp), ("f41", T.T41.run_f41), ("f43", T.T43.run_f43), ("page", T.run_page),
              ("exec", T.run_exec), ("open", T.run_open), ("arms", run_arms), ("armsold", run_arms_old), ("armseq", run_arms_eq), ("live42", T.T42.run_live42)]
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=T.ADDED,
           phases=phases, script=__file__, live=(T.T40.LIVE_RB, "Skyy_SkyyRebirth"))
