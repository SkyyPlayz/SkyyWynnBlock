"""Harness for SkyySacks 0.8.12 (THE LIFELONG POCKET DIMENSION ITEM; tools/sacks_0_8_12_patch.py + tools/skyyonce.py).
Build first: python tools/sacks_0_8_12_patch.py && python SkyySacks/build_skyysacks_0.8.12.py

    python SkyySacks/test_skyysacks_0.8.12.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.8.11 -> 0.8.12: + the 7 PdOnce classes; only the listed members differ; non-class: manifest + server.lang (phase S)
  S    assets   only the Pocket Dimension's tooltip lines changed (it stays with you, /pocket)
  LIFE tools/skyyonce_harness.py L1-L14 on the jar's PdOnce* (REAL containers / windows / events / Player / WindowManager)
  CF   config   bags.pocketKeep: absent = on; false = off; the Server Setup row in the SkyyVoid section; /pdadmin legacybags all (HOLDALL)
                switches every rule off; the bytecode: /sacks (/pd, /bags, /pocket) runs PdOnce.recall, "pocket" is an alias, the plugin
                registers the three systems + the ready hook, publishes / unpublishes
  D    live     start twice on a scratch COPY of the live NewBetaTest Skyy_SkyySacks config (SackMig089 + SackCfg.reload): no file changed,
                the missing bags.pocketKeep line = on
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyonce_harness as OH

VERSION = "0.8.12"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.11.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "life01", "sacks")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyySacks")
PKG = "com.skyy.sacks."
POCKET = "Skyy_Sack_Pocket"
ADDED = ["PdOnce", "PdOnceTask", "PdOnceDropSys", "PdOnceThrowSys", "PdOnceInvSys", "PdOnceReady", "PdOnceFn"]
EXPECT = {
    "SackCfg": ["+f POCKET_KEEP", "~<clinit>", "~m linkKeys", "~m reload"],
    "SacksCmd": ["~c ", "~m execute"],
    "SkyySacksPlugin": ["~m setup", "~m shutdown"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFile": ["~<clinit>"],
    "CfgFn": ["~m opExport"],
    "RecipeCmp": ["~<clinit>"],                # the committed tools/tier_tags.py (52298ac: + the egg rows) - the sort table
    "SackDefs": ["~m enchCat"],                # the committed tools/skyyench.py (52298ac: + the Enchanted Stick)
}
HK.run_compare = OH.compare_allowing(lambda n: n.endswith(".lang"))


def run_assets(out, jar, scratch, _home):
    K = HK.Child(out)
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    K.eq(sorted(set(ea) ^ set(eb)), [], "S: no non-class file added / removed")
    changed = sorted(n for n in ea if ea[n] != eb.get(n) and n != "manifest.json")
    K.check(changed and all(n.endswith(".lang") for n in changed), "S: only lang files changed: %s" % changed)
    for n in changed:
        la = dict(l.split("=", 1) for l in ea[n].decode("utf-8").splitlines() if "=" in l)
        lb = dict(l.split("=", 1) for l in eb[n].decode("utf-8").splitlines() if "=" in l)
        diff = sorted(k for k in set(la) | set(lb) if la.get(k) != lb.get(k))
        K.eq(diff, sorted(["items.%s.description" % POCKET, "server.items.%s.description" % POCKET]), "S: %s: only the Pocket Dimension's tooltip" % n)
        K.check("/pocket gives a new one" in lb.get("server.items.%s.description" % POCKET, ""), "S: the tooltip names /pocket")
    K.save()


def run_life(out, jar, scratch, _home):
    K = HK.Child(out)
    OH.life_phase(K, jar, PKG, "PdOnce", POCKET, ("SackCfg", "POCKET_KEEP"), os.path.join(scratch, "life"), "SkyySacks")
    K.save()


def run_cfg(out, jar, scratch, _home):
    from jpype import JClass, JBoolean
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Cfg, Vs, Once = JClass(PKG + "SackCfg"), JClass(PKG + "VoidStore"), JClass(PKG + "PdOnce")
    Props = JClass("java.util.Properties")
    p = Props()
    Cfg.POCKET_KEEP = False
    Cfg.linkKeys(p, JBoolean(True))
    K.check(bool(Cfg.POCKET_KEEP) and bool(Once.on()), "CF a file without bags.pocketKeep = on")
    p.setProperty("bags.pocketKeep", "false")
    Cfg.linkKeys(p, JBoolean(False))
    K.check(not bool(Cfg.POCKET_KEEP) and not bool(Once.on()), "CF bags.pocketKeep=false = off")
    p.setProperty("bags.pocketKeep", "true")
    Cfg.linkKeys(p, JBoolean(False))
    Vs.HOLDALL = True
    K.check(not bool(Once.on()), "CF /pdadmin legacybags all (HOLDALL) switches the rules off (that mode strips the item on purpose)")
    Vs.HOLDALL = False
    K.check(bool(Once.on()), "CF ... and back on after /pdadmin resume all")
    # the Server Setup row (the kit's header)
    mods = os.path.join(scratch, "cf", "mods")
    os.makedirs(os.path.join(mods, "Skyy_SkyySacks"), exist_ok=True)
    CP = JClass(PKG + "CfgPub")
    CP.start(JClass("java.nio.file.Paths").get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks"))
    br = JClass("java.lang.System").getProperties().get("skyy.bridge")
    hdr = br.get("config:def:SkyySacks") if br is not None else None
    rows = [[str(v) for v in r_] for r_ in hdr[7]] if hdr is not None else []
    row = [r_ for r_ in rows if r_[0] == "bags.pocketKeep"]
    K.check(len(row) == 1 and row[0][1] == "Pocket Dimension stays with you" and row[0][3] == "bool" and row[0][4] == "true",
            "CF the Server Setup row bags.pocketKeep (bool, default true): %s" % (row[0][:5] if row else None))
    r = str(JClass(PKG + "CfgFn").cmdSetConsole("bags.pocketKeep", "false"))
    K.check(not bool(Cfg.POCKET_KEEP), "CF the Server Setup edit sets SackCfg.POCKET_KEEP live: %s" % r)
    CP.shutdown()
    # bytecode
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def code(cn, mn, ctor=False):
        c = cp.get(PKG + cn)
        ms = list(c.getDeclaredConstructors()) if ctor else [x for x in c.getDeclaredMethods() if str(x.getName()) == mn]
        out_ = []
        for m in ms:
            it = m.getMethodInfo().getCodeAttribute().iterator()
            cpl = m.getMethodInfo().getConstPool()
            while it.hasNext():
                out_.append(str(IP.instructionString(it, it.next(), cpl)))
        return "\n".join(out_)
    ex = code("SacksCmd", "execute")
    K.check("PdOnce.recall" in ex and ex.index("PdOnce.recall") < ex.index("openCustomPageWithWindows") and "givePocket" not in ex,
            "CF /sacks (/pd, /bags, /pocket) runs PdOnce.recall before it opens the Void (VoidStore.givePocket no longer used there)")
    K.check('"pocket"' in code("SacksCmd", None, ctor=True), "CF \"pocket\" is an alias of /sacks")
    su = code("SkyySacksPlugin", "setup")
    K.check(all(("%s.<init>" % c) in su for c in ("PdOnceDropSys", "PdOnceThrowSys", "PdOnceInvSys", "PdOnceReady")) and "PdOnce.publish" in su,
            "CF setup registers the three systems + the ready hook and publishes")
    K.check("PdOnce.unpublish" in code("SkyySacksPlugin", "shutdown"), "CF shutdown unpublishes")
    Defs = JClass(PKG + "SackDefs")
    K.check(str(Defs.enchCat("Skyy_Ench_Stick")) == "Foraging" and str(Defs.homeOf("Skyy_Ench_Stick")) == "Foraging",
            "CF the Enchanted Stick (committed tools/skyyench.py, 52298ac) goes into the Foraging bag")
    K.check(Defs.enchCat("Skyy_Ench_NoSuch") is None, "CF an unknown Enchanted id has no home")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    f = os.path.join(home, "config.properties")
    t0 = open(f, "rb").read() if os.path.isfile(f) else None
    h0 = HK.tree_hash(home)
    Cfg = JClass(PKG + "SackCfg")
    res = []
    for start in (1, 2):
        Cfg.FILE = Paths.get(f)
        Cfg.MTIME = -1
        JClass(PKG + "SackMig089").run(Cfg.FILE)
        Cfg.POCKET_KEEP = False
        Cfg.reload()
        res.append((bool(Cfg.POCKET_KEEP), HK.tree_hash(home)))
    K.check(t0 is not None and b"bags.pocketKeep=" not in t0.replace(b"#bags.pocketKeep", b""), "D the live config has no bags.pocketKeep line (an 0.8.11 file)")
    K.check(res[0][0] and res[1][0], "D both starts: the missing line = on")
    K.check(res[0][1] == h0 and res[1][1] == h0, "D neither start changed a file of the copy (%d files)" % len(h0))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyySacks", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("assets", run_assets), ("life", run_life), ("cfg", run_cfg), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyySacks"))
