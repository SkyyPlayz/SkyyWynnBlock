"""Harness for SkyySacks 0.8.13 (/recipes leaves /craft - SkyyCollections 0.2.22 owns it; tools/sacks_0_8_13_patch.py).
Build first: python tools/sacks_0_8_13_patch.py && python SkyySacks/build_skyysacks_0.8.13.py

    python SkyySacks/test_skyysacks_0.8.13.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.8.12 -> 0.8.13: only CraftCmd's constructor (the alias) + the version texts (plugin setup, CfgRows.header,
                CfgFn.opExport) differ; RecipeCmp + SackDefs identical (tables frozen to 52298ac); non-class: only manifest.json
  CMD  EXECUTED: new CraftCmd() on the real engine command classes - name "craft", NO alias "recipes", the Adventurer group, extra
                arguments allowed; the bytecode: the constructor no longer calls addAliases; every non-class file byte-identical
  D    live     start twice on a scratch COPY of the live NewBetaTest Skyy_SkyySacks config (SackMig089 + SackCfg.reload): no file changed
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.8.13"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.12.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubcoll", "sacks")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyySacks")
PKG = "com.skyy.sacks."
ADDED = []
EXPECT = {
    "CraftCmd": ["~c "],                       # no addAliases("recipes")
    "SkyySacksPlugin": ["~m setup"],           # the version on the ready line
    "CfgRows": ["~m header"],                  # the config kit's version text
    "CfgFn": ["~m opExport"],                  # the config kit's version text
}   # RecipeCmp / SackDefs are byte-identical: the patch freezes their tables to 52298ac (what 0.8.12 was built with)


def run_cmd(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    c = JClass(PKG + "CraftCmd")()
    K.eq(str(c.getName()), "craft", "CMD the command is /craft")
    al = sorted(str(a) for a in (c.getAliases() or []))
    K.eq(al, [], "CMD /craft has no alias any more (0.8.12: recipes) - %s" % al)
    try:
        groups = sorted(str(g) for g in c.getPermissionGroups())
        K.eq(groups, ["hytale:Adventurer"], "CMD the Adventurer group (HANDOFF command rules)")
    except AttributeError:
        K.notes.append("CMD permission groups: no getter on this engine (the bytecode check below + tools/ci/lint.py)")
    pool = JClass("javassist.ClassPool")(True)
    pool.insertClassPath(jar)
    cc = pool.get(PKG + "CraftCmd")
    calls = []
    ci = cc.getDeclaredConstructors()[0].getMethodInfo().getCodeAttribute().iterator()
    cp = cc.getClassFile().getConstPool()
    while ci.hasNext():
        i = ci.next()
        op = ci.byteAt(i)
        if op in (0xb6, 0xb7, 0xb8, 0xb9):
            calls.append(str(cp.getMethodrefName(ci.u16bitAt(i + 1))) if op != 0xb9 else str(cp.getInterfaceMethodrefName(ci.u16bitAt(i + 1))))
    K.check("addAliases" not in calls and "setPermissionGroups" in calls and "setAllowsExtraArguments" in calls,
            "CMD bytecode: the constructor calls setPermissionGroups + setAllowsExtraArguments, never addAliases (%s)" % calls)
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    K.eq(sorted(set(ea) ^ set(eb)), [], "CMD no non-class file added / removed")
    K.eq(sorted(n for n in ea if ea[n] != eb.get(n) and n != "manifest.json"), [], "CMD every non-class file but manifest.json byte-identical")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    f = os.path.join(home, "config.properties")
    h0 = HK.tree_hash(home)
    Cfg = JClass(PKG + "SackCfg")
    res = []
    for start in (1, 2):
        Cfg.FILE = Paths.get(f)
        Cfg.MTIME = -1
        JClass(PKG + "SackMig089").run(Cfg.FILE)
        Cfg.reload()
        res.append(HK.tree_hash(home))
    K.check(os.path.isfile(f), "D the live copy has a config.properties")
    K.check(res[0] == h0 and res[1] == h0, "D neither start changed a file of the copy (%d files)" % len(h0))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyySacks", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("cmd", run_cmd), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyySacks"))
