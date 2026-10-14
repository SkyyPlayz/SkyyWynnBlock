"""Harness for SkyyMenu 0.3.22 (the Shards tile; tools/menu_0_3_22_patch.py).
Build first: python tools/menu_0_3_22_patch.py && python SkyyMenu/build_skyymenu_0.3.22.py

    python SkyyMenu/test_skyymenu_0.3.22.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.21 -> 0.3.22: exactly MenuData.<clinit> (the entry tables: one more main tile) + the version texts differ; no class added
  S  shards   THE NEW TILE, executed: the MenuData tables hold "Shards" at main slot 11 (row 1, col 2, left of Island Menu) with the action
              bridge:shard:fn:open, the rule need shard:fn:open, icon Portal_Device, no permission / unlock; every other main tile keeps
              its 0.3.21 slot, action and rule (table compare against the 0.3.21 jar in the same JVM); MenuPage.tileVisible (the real
              method on a page object): Shards hidden without shard:fn:open, hidden while it holds a non-Function, shown with a
              Function; the reserved free slots 27 / 39 / 41 stay free
  T, N, D    the 0.3.21 checks carried forward: test_skyymenu_0.3.21.py's run_tabs and the run_name / run_live it carries, run on
              the 0.3.22 jar exactly as they ran on 0.3.21 (0.3.19's run_exec needs SkyyMenu-0.3.18.jar side by side, which the local
              tidy removed - its paths are untouched by this change: MenuData tables only)
  AA engine-access audit
Scratch: tools/dev/scratch/shards01/menu (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("test_skyymenu_0_3_21", os.path.join(HERE, "test_skyymenu_0.3.21.py"))
T21 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T21)
T20, T19 = T21.T20, T21.T19

VERSION = "0.3.22"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.21.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shards01", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = T19.LIVE_DIR
EXPECT = {
    "MenuData": ["~<clinit>"],
    "CfgRows": ["~m header"],                     # the version text
    "CfgFn": ["~m opExport"],                     # the version text
    "SkyyMenuPlugin": ["~m setup"],               # the ready line's version
}
ADDED = []


def run_shards(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Sys = JClass("java.lang.System")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    D = JClass(PKG + "MenuData")
    views, slots, names, acts = list(D.E_VIEW), list(D.E_SLOT), list(D.E_NAME), list(D.E_ACT)
    needs, unl, perms, icons = list(D.E_NEED), list(D.E_UNLOCK), list(D.E_PERM), list(D.E_ICON)
    main = [i for i in range(len(views)) if str(views[i]) == "main"]
    sh = [i for i in main if str(names[i]) == "Shards"]
    K.check(len(sh) == 1, "S one Shards tile in the main view")
    i = sh[0]
    K.eq((int(slots[i]), str(acts[i]), str(needs[i]), str(unl[i]), str(perms[i]), str(icons[i])),
         (11, "bridge:shard:fn:open", "shard:fn:open", "", "", "Portal_Device"), "S Shards: slot 11, bridge:shard:fn:open, need shard:fn:open, icon Portal_Device")
    used = set(int(slots[j]) for j in main)
    K.check(not (used & {27, 39, 41}) and len(used) == len(main), "S main slots unique, the reserved 27 / 39 / 41 still free")
    # every other main tile = 0.3.21's (old jar in its own class loader)
    URL = JClass("java.net.URL")
    UCL = JClass("java.net.URLClassLoader")
    File = JClass("java.io.File")
    old = UCL([File(OLD_JAR).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()], None)
    OD = JClass("java.lang.Class").forName(PKG + "MenuData", True, old)

    def f(cls, name):
        return list(cls.getField(name).get(None))
    ov, osl, on, oa, onn = f(OD, "E_VIEW"), f(OD, "E_SLOT"), f(OD, "E_NAME"), f(OD, "E_ACT"), f(OD, "E_NEED")
    old_main = sorted((str(on[j]), int(osl[j]), str(oa[j]), str(onn[j])) for j in range(len(ov)) if str(ov[j]) == "main")
    new_main = sorted((str(names[j]), int(slots[j]), str(acts[j]), str(needs[j])) for j in main if str(names[j]) != "Shards")
    K.eq(new_main, old_main, "S every other main tile keeps its 0.3.21 slot, action and rule")
    old_other = sorted((str(ov[j]), str(on[j]), int(osl[j])) for j in range(len(ov)) if str(ov[j]) != "main")
    new_other = sorted((str(views[j]), str(names[j]), int(slots[j])) for j in range(len(views)) if str(views[j]) != "main")
    K.eq(new_other, old_other, "S the other views (Teleport, Players ...) unchanged")
    # tileVisible: the real method on a page object (no constructor needed for this rule: no perm, no unlock)
    U_ = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    U_.setAccessible(True)
    U = U_.get(None)
    MP = JClass(PKG + "MenuPage")
    pg = U.allocateInstance(MP.class_)
    K.check(not pg.tileVisible(i, False) and not pg.tileVisible(i, True), "S Shards hidden while SkyyShards publishes no shard:fn:open")
    br.put("shard:fn:open", JClass("java.lang.String")("not a function"))
    K.check(not pg.tileVisible(i, False), "S hidden while shard:fn:open is not a Function")
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Fn(object):
        @JOverride
        def apply(self, a):
            return JClass("java.lang.Boolean").TRUE
    br.put("shard:fn:open", Fn())
    K.check(bool(pg.tileVisible(i, False)), "S shown while shard:fn:open is a Function")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("shards", run_shards), ("tabs", T21.run_tabs), ("name", T20.run_name), ("live", T19.run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
