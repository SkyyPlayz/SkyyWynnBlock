"""SkyyRebirth 0.3.3 - harness for the rebirth wrap-up round (tools/rebirth_0_3_3_patch.py): TEXTS ONLY (the Class arm's "Works" lines, three
Server Setup helps, the manifest) - rebirth:fn:stat answers exactly as 0.3.2 and SkyySkills 0.4.39 now applies health / mana / all / classxp.
Build first: python tools/rebirth_0_3_3_patch.py && python SkyyRebirth/build_skyyrebirth_0.3.3.py

    python SkyyRebirth/test_skyyrebirth_0.3.3.py --dir <empty folder inside tools/dev/scratch/> [--keep]

  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.3.2 -> 0.3.3: exactly the planned members differ (texts + RbFn.apply's one stat line), no class added - every other
               code path (the journal, the participants, the tree buys) is byte-identical to 0.3.2
  S   stat     EXECUTED: the REAL RbFn(6) = rebirth:fn:stat on real players/<pkey>.properties: n = 0 / 1 / 5 / 10 / 12 (rebirth.max) and
               stat.cap 20, "all" + Void Ascendant, health / mana / damage / defense / classxp from the Class nodes, a pkey String and a
               UUID; the node panel texts (RbTree.NLIVE) of the Class arm say what applies each node now; the three Server Setup helps
               (kit header); the 0.3.2 texts are gone
  G   gear     test_skyyrebirth_0.3.2.py's gear phase on this jar (the 4-part rebirth end to end with the REAL SkyySkills 0.4.38 /
               SkyyCoins / SkyyBank / SkyyGear participants, the crash proof at every point, recovery) - the participants unchanged
  N   new      test_skyyrebirth_0.3.1.py's new phase (parser + Farming arm) on this jar
  D   live     test_skyyrebirth_0.3.2.py's live phase: START TWICE on a scratch COPY of the live data (+ Skyy_SkyyGear/lifelong), nothing written
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.3.3"
RB = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.3.2.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rebirth6", "rb")))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T32 = _load("t_rb032", os.path.join(HERE, "test_skyyrebirth_0.3.2.py"))
for _m in (T32, T32.T31, T32.T3, T32.T2):
    _m.VERSION = VERSION
    _m.JAR = JAR

EXPECT = {
    "RbTree": ["~<clinit>"],                                       # the Class arm's Works lines (NLIVE)
    "SkyyRebirthPlugin": ["~m setup"],                             # the ready line (version)
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],   # the three helps + the kit's version text
    "RbStore": ["~m writeNow"],                                    # the file comment's version
    "RbFn": ["~m apply"],                                          # fix round: mode 6 (rebirth:fn:stat) = null for an unreadable file
}
ADDED = []


def run_stat(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    R = lambda n: JClass(RB + n)
    Store, Cfg, Fn, Tree = R("RbStore"), R("RbCfg"), R("RbFn"), R("RbTree")
    d = os.path.join(scratch, "s", "players")
    os.makedirs(d)
    Store.DIR = JClass("java.nio.file.Paths").get(d, JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.String").class_, 0))
    f = Fn(6)
    UUID = JClass("java.util.UUID")
    seq = [0]

    def prof(lines):
        seq[0] += 1
        u = UUID(0x33000 + seq[0], 0x99)
        open(os.path.join(d, str(u) + ".properties"), "w").write("".join("%s=%s\n" % kv for kv in lines))
        return u

    def ask(key, name):
        r = f.apply(JArray(JObject)([key, JString(name)]))
        return None if r is None else float(r)
    for n, want in ((0, 0.0), (1, 3.0), (5, 15.0), (10, 30.0), (12, 30.0)):
        u = prof([("n", n)])
        K.check(ask(u, "all") == want and ask(u, "health") == 0.0 and ask(str(u), "all") == want,
                "S rebirth:fn:stat all at n = %d = %s (UUID and pkey String): got %s" % (n, want, ask(u, "all")))
    Cfg.STAT_CAP = 20.0
    u = prof([("n", 10)])
    K.check(ask(u, "all") == 20.0, "S stat.cap 20 -> 20 at n = 10")
    Cfg.STAT_CAP = 30.0
    u = prof([("n", 1), ("node.Class.hp", 3), ("node.Class.hp2", 2), ("node.Class.mana", 1), ("node.Class.mana2", 4), ("node.Class.key", 1),
              ("node.Class.xp", 5), ("node.Class.dmg", 4), ("node.Class.dmg2", 1), ("node.Class.def", 2), ("node.Class.def2", 3)])
    got = [ask(u, x) for x in ("all", "health", "mana", "damage", "defense", "classxp", "nonsense")]
    K.check(got == [5.0, 5.0, 5.0, 5.0, 5.0, 10.0, 0.0], "S the Class nodes: all 3 + Void Ascendant 2, health 3 + 2, mana 1 + 4, damage 4 + 1, defense 2 + 3, classxp 5 x 2: %s" % got)
    # fix round: a profile file that cannot be read (here: a FOLDER named <pkey>.properties) = RbStore.BAD -> rebirth:fn:stat answers
    # nothing (null = the stat mods keep the last values), while the count still answers 0 as in 0.3.2
    seq[0] += 1
    ub = UUID(0x33000 + seq[0], 0x99)
    os.makedirs(os.path.join(d, str(ub) + ".properties"))
    Store.get(str(ub))
    K.check(bool(Store.BAD.containsKey(str(ub))) and ask(ub, "all") is None and ask(ub, "health") is None and ask(str(ub), "classxp") is None
            and int(Fn(0).apply(ub)) == 0, "S an unreadable profile file: rebirth:fn:stat = no answer (null), count = 0: BAD %s all %s"
            % (bool(Store.BAD.containsKey(str(ub))), ask(ub, "all")))
    uo = prof([("n", 1)])
    K.check(ask(uo, "all") == 3.0 and not bool(Store.BAD.containsKey(str(uo))), "S a readable profile still answers (3 at n = 1)")
    K.check(f.apply(JString("not a key!")) is None and f.apply(JArray(JObject)([JString("bad key!"), JString("all")])) is None, "S a bad key = no answer")
    nid = [str(x) for x in Tree.NID]
    live = dict(zip(nid, [str(x) for x in Tree.NLIVE]))
    want_live = {"Class.hp": "now (SkyySkills: max Health)", "Class.hp2": "now (SkyySkills: max Health)", "Class.mana": "now (SkyySkills: max Mana)",
                 "Class.mana2": "now (SkyySkills: max Mana)", "Class.xp": "now (SkyySkills: class XP)", "Class.dmg": "when SkyyGear applies rebirth damage",
                 "Class.dmg2": "when SkyyGear applies rebirth damage", "Class.def": "when SkyyGear applies rebirth defense",
                 "Class.def2": "when SkyyGear applies rebirth defense", "Class.key": "now (title; Health, Mana, Stamina); damage / defense later"}
    K.check(all(live[k] == v for k, v in want_live.items()), "S the Class arm's Works lines: %s" % [(k, live[k]) for k in want_live if live[k] != want_live[k]])
    K.check(not any("after a later update (stats)" in x for x in live.values()) and live["Mining.tool"].startswith("now (SkyyGear"),
            "S no node still says 'after a later update (stats)'; the tool nodes keep their 0.3.2 line")
    rows = dict((str(r[0]), [str(x) for x in list(r)[:11]]) for r in R("CfgRows").header()[7])
    K.check("SkyySkills max Health / Mana / Stamina now" in rows["stat.perRebirth"][10] and "Health + Mana now" in rows["tree.statNode"][10]
            and "Health, Mana, Stamina now" in rows["tree.keyStat"][10] and rows["stat.perRebirth"][4] == "3" and rows["stat.cap"][4] == "30",
            "S Server Setup helps name what applies the stats; defaults unchanged")
    K.save()


if __name__ == "__main__":
    for j_ in (T32.T2.SK_JAR, T32.T2.CO_JAR, T32.T2.BK_JAR, T32.T2.PF_JAR, T32.GEAR_JAR, OLD_JAR):
        assert os.path.isfile(j_), j_
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("stat", run_stat), ("gear", T32.sub(T32.run_gear, "g")), ("new", T32.sub(T32.T31.run_new, "n")),
                   ("live", T32.run_live)],
           script=__file__, live=(T32.LIVE_DIR, "Skyy_SkyySkills"))
