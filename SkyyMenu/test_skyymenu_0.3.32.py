"""Harness for SkyyMenu 0.3.32 (THE LIFELONG SKYWYNN MENU ITEM; tools/menu_0_3_32_patch.py + tools/skyyonce.py).
Build first: python tools/menu_0_3_32_patch.py && python SkyyMenu/build_skyymenu_0.3.32.py

    python SkyyMenu/test_skyymenu_0.3.32.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.31 -> 0.3.32: + the 7 MenuOnce classes; only the listed members differ; non-class: manifest + server.lang (phase S)
  S    assets   only the menu item's tooltip lines changed (it stays with you, /menuitem)
  LIFE tools/skyyonce_harness.py L1-L14 on the jar's MenuOnce* (REAL containers / windows / events / Player / WindowManager)
  CF   config   itemKeep: a fresh file writes itemKeep=true; absent = on, bytes untouched; false = off; the Server Setup row menu.itemKeep;
                /menuitem is an alias of /skymenu (MenuData.ALIASES, which the runtime alias check also uses); /skymenu still gives a new item
                when none is held (MenuUtil.giveMenuItem, unchanged); the plugin registers the three systems + the ready hook, publishes
  D    live     start twice on a scratch COPY of the live NewBetaTest Skyy_SkyyMenu config: no file changed, the missing itemKeep = on
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

VERSION = "0.3.32"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.31.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "life01", "menu")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMenu")
PKG = "com.skyy.menu."
ITEM = "Skyy_Menu"
ADDED = ["MenuOnce", "MenuOnceTask", "MenuOnceDropSys", "MenuOnceThrowSys", "MenuOnceInvSys", "MenuOnceReady", "MenuOnceFn"]
EXPECT = {
    "MenuCfg": ["+f KEEP_ITEM", "~<clinit>", "~m init", "~m load"],
    "MenuData": ["~<clinit>"],                 # the aliases (+ menuitem), the config file text, the Mods help line
    "OpsPage": ["~<clinit>"],                  # the Mods page's /skymenu line (shorter, + /menuitem)
    "SkyyMenuPlugin": ["~m setup", "~m shutdown"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFile": ["~<clinit>"],
    "CfgFn": ["~m opExport"],
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
        K.eq(diff, sorted(["items.%s.description" % ITEM, "server.items.%s.description" % ITEM]), "S: %s: only the menu item's tooltip" % n)
        K.check("/menuitem" in lb.get("server.items.%s.description" % ITEM, ""), "S: the tooltip names /menuitem")
    K.save()


def run_life(out, jar, scratch, _home):
    K = HK.Child(out)
    OH.life_phase(K, jar, PKG, "MenuOnce", ITEM, ("MenuCfg", "KEEP_ITEM"), os.path.join(scratch, "life"), "SkyyMenu")
    K.save()


def run_cfg(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg, Data = JClass(PKG + "MenuCfg"), JClass(PKG + "MenuData")
    d = os.path.join(scratch, "cf", "mods", "Skyy_SkyyMenu")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "config.properties")
    Cfg.FILE = Paths.get(f)
    Cfg.init()
    Cfg.KEEP_ITEM = False
    Cfg.load()
    t = open(f, encoding="latin-1").read()
    K.check("itemKeep=true" in t and bool(Cfg.KEEP_ITEM), "CF a fresh file writes itemKeep=true (on)")
    old = b"giveItem=true\r\nmodsHelp=true\r\n"
    open(f, "wb").write(old)
    Cfg.KEEP_ITEM = False
    Cfg.load()
    K.check(bool(Cfg.KEEP_ITEM) and open(f, "rb").read() == old, "CF a file without itemKeep = on, its bytes untouched")
    open(f, "wb").write(old + b"itemKeep=false\r\n")
    Cfg.load()
    K.check(not bool(Cfg.KEEP_ITEM) and not bool(JClass(PKG + "MenuOnce").on()), "CF itemKeep=false = off")
    os.remove(f)
    Cfg.KEEP_ITEM = False
    Cfg.load()
    K.check(bool(Cfg.KEEP_ITEM), "CF no file at all = on")
    K.check("menuitem" in [str(a) for a in Data.ALIASES], "CF /menuitem is an alias of /skymenu: %s" % [str(a) for a in Data.ALIASES])
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def code(cn, mn):
        c = cp.get(PKG + cn)
        out_ = []
        for m in [x for x in c.getDeclaredMethods() if str(x.getName()) == mn]:
            it = m.getMethodInfo().getCodeAttribute().iterator()
            cpl = m.getMethodInfo().getConstPool()
            while it.hasNext():
                out_.append(str(IP.instructionString(it, it.next(), cpl)))
        return "\n".join(out_)
    ex = code("MenuCmd", "execute")
    K.check("MenuUtil.giveMenuItem" in ex and ex.index("MenuUtil.giveMenuItem") < ex.index("openCustomPage"), "CF /skymenu (/menuitem) still gives a new item when none is held, before the menu opens")
    su = code("SkyyMenuPlugin", "setup")
    K.check(all(("%s.<init>" % c) in su for c in ("MenuOnceDropSys", "MenuOnceThrowSys", "MenuOnceInvSys", "MenuOnceReady")) and "MenuOnce.publish" in su,
            "CF setup registers the three systems + the ready hook and publishes")
    K.check("MenuOnce.unpublish" in code("SkyyMenuPlugin", "shutdown"), "CF shutdown unpublishes")
    # the Server Setup row (static: the kit's row table in the jar)
    rows = [str(r_[0]) for r_ in JClass(PKG + "CfgRows").ROWS] if hasattr(JClass(PKG + "CfgRows"), "ROWS") else None
    if rows is not None:
        K.check("menu.itemKeep" in rows, "CF the Server Setup row menu.itemKeep is in the table")
    else:
        K.check(b"menu.itemKeep" in zipfile.ZipFile(jar).read("com/skyy/menu/CfgRows.class"), "CF the Server Setup row menu.itemKeep is in CfgRows")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    f = os.path.join(home, "config.properties")
    t0 = open(f, "rb").read() if os.path.isfile(f) else None
    h0 = HK.tree_hash(home)
    Cfg = JClass(PKG + "MenuCfg")
    res = []
    for start in (1, 2):
        Cfg.FILE = Paths.get(f)
        Cfg.KEEP_ITEM = False
        Cfg.init()
        Cfg.load()
        res.append((bool(Cfg.KEEP_ITEM), HK.tree_hash(home)))
    K.check(t0 is not None and b"itemKeep" not in t0, "D the live config has no itemKeep line (a 0.3.31 file)")
    K.check(res[0][0] and res[1][0], "D both starts: the missing line = on")
    K.check(res[0][1] == h0 and res[1][1] == h0, "D neither start changed a file of the copy (%d files)" % len(h0))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("assets", run_assets), ("life", run_life), ("cfg", run_cfg), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyMenu"))
