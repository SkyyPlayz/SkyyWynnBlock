"""Harness for SkyyAccessories 0.5.20 (THE LIFELONG ACCESSORY BAG; tools/accessories_0_5_20_patch.py + tools/skyyonce.py).
Build first: python tools/accessories_0_5_20_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.20.py

    python SkyyAccessories/test_skyyaccessories_0.5.20.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.5.19 -> 0.5.20: + the 7 AccOnce classes; only the listed members differ; non-class entries: only the manifest + the bag
                item JSON (no Recipe), the Workbench tab's client levels and server.lang (the bag's tooltip) - checked in S
  S    assets   the bag item has no recipe any more, its tooltip says it stays with you + /accbag, nothing else in the item files changed
  LIFE tools/skyyonce_harness.py L1-L14 on the jar's AccOnce* (REAL containers / windows / events / Player / WindowManager)
  CF   config   lifelong.bag: a fresh file writes it (on); a file without it = on, bytes untouched; false = off; the Server Setup edit sets
                AccDefs.LIFELONG live; the row is in the Accessory Bag section; the bytecode of AccCmd calls AccOnce.recall (the /accbag recall)
                and the plugin registers AccOnceDropSys / ThrowSys / InvSys + the PlayerReadyEvent hook and publishes / unpublishes
  D    live     start twice on a scratch COPY of the live NewBetaTest Skyy_SkyyAccessories (config load, the kit, AccOnce publish): no file
                changed by either start (the missing lifelong.bag line = on, never written), no lifelong/ folder appears without a sweep
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

VERSION = "0.5.20"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.19.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "life01", "acc")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyAccessories")
PKG = "com.skyy.accessories."
BAG = "Skyy_Accessory_Bag"
ADDED = ["AccOnce", "AccOnceTask", "AccOnceDropSys", "AccOnceThrowSys", "AccOnceInvSys", "AccOnceReady", "AccOnceFn"]
EXPECT = {
    "AccDefs": ["+f LIFELONG", "~<clinit>"],
    "AccCfg": ["+f LIFE_KEY", "~m load", "~m writeDefaults"],
    "AccCmd": ["~c ", "~m execute"],
    "CfgFile": ["~<clinit>"],
    "SkyyAccessoriesPlugin": ["~m setup", "~m shutdown"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "WbRank": ["~<clinit>"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_assets(out, jar, scratch, _home):
    K = HK.Child(out)
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    K.eq(sorted(set(ea) ^ set(eb)), [], "S: no non-class file added / removed")
    changed = sorted(n for n in ea if ea[n] != eb.get(n))
    bagp = "Server/Item/Items/Utility/%s.json" % BAG
    nb, ob = json.loads(eb[bagp]), json.loads(ea[bagp])
    K.check("Recipe" in ob and "Recipe" not in nb, "S: the bag item had a recipe and has none now")
    ob.pop("Recipe", None)
    ob.pop("ItemLevel", None)
    K.eq(nb, ob, "S: nothing else in the bag item changed (Recipe + its Workbench-tab ItemLevel gone)")
    lvl = []
    for n in changed:
        if n.startswith("Server/Item/Items/") and n != bagp:
            a, b = json.loads(ea[n]), json.loads(eb[n])
            if set(a) == set(b) and all(a[k] == b[k] for k in a if k != "ItemLevel"):
                lvl.append(n)
            else:
                K.check(False, "S: %s changed beyond its ItemLevel" % n)
    K.notes.append("S: %d tab items moved one ItemLevel down (the bag left the tab)" % len(lvl))
    langs = [n for n in changed if n.endswith(".lang")]
    for n in langs:
        la = dict(l.split("=", 1) for l in ea[n].decode("utf-8").splitlines() if "=" in l)
        lb = dict(l.split("=", 1) for l in eb[n].decode("utf-8").splitlines() if "=" in l)
        diff = sorted(k for k in set(la) | set(lb) if la.get(k) != lb.get(k))
        K.eq(diff, sorted(["items.%s.description" % BAG, "server.items.%s.description" % BAG]), "S: %s: only the bag's tooltip changed" % n)
        K.check("/accbag brings it back" in lb.get("server.items.%s.description" % BAG, ""), "S: the tooltip names /accbag")
    rest = [n for n in changed if n not in lvl and n != bagp and n not in langs and n != "manifest.json"]
    K.eq(rest, [], "S: no other file changed")
    K.save()


def run_life(out, jar, scratch, _home):
    K = HK.Child(out)
    OH.life_phase(K, jar, PKG, "AccOnce", BAG, ("AccDefs", "LIFELONG"), os.path.join(scratch, "life"), "SkyyAccessories", once_flag=("AccDefs", "STARTER"))
    K.save()


def run_cfg(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg, Defs = JClass(PKG + "AccCfg"), JClass(PKG + "AccDefs")
    mods = os.path.join(scratch, "cf", "mods")
    d = os.path.join(mods, "Skyy_SkyyAccessories")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "config.properties")
    Cfg.FILE = Paths.get(f)
    Cfg.load(True)
    t = open(f, encoding="latin-1").read()
    K.check("lifelong.bag=true" in t and bool(Defs.LIFELONG), "CF a first start writes lifelong.bag=true (on)")
    old = b"slots=18\r\nregenEverySeconds=5\r\n"
    open(f, "wb").write(old)
    Defs.LIFELONG = False
    Cfg.reload()
    K.check(bool(Defs.LIFELONG) and open(f, "rb").read() == old, "CF a file without the key = on, its bytes untouched")
    open(f, "wb").write(old + b"lifelong.bag=false\r\n")
    Cfg.reload()
    K.check(not bool(Defs.LIFELONG), "CF lifelong.bag=false = off")
    CP, Fn = JClass(PKG + "CfgPub"), JClass(PKG + "CfgFn")
    CP.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyAccessories"))
    r = str(Fn.cmdSetConsole("lifelong.bag", "true"))
    K.check(bool(Defs.LIFELONG), "CF the Server Setup edit sets AccDefs.LIFELONG live: %s" % r)
    CP.shutdown()
    K.check("lifelong.bag=true" in open(f, encoding="latin-1").read(), "CF ... and writes the line")
    br = JClass("java.lang.System").getProperties().get("skyy.bridge")
    hdr = br.get("config:def:SkyyAccessories") if br is not None else None
    rows = [[str(v) for v in r_] for r_ in hdr[7]] if hdr is not None else []
    K.eq([r_[0] for r_ in rows if r_[2] == "bag"], ["slots", "notice.boosters", "starter.bag", "craft.bag", "craft.autoEquip", "lifelong.bag"],
         "CF the rows in the Accessory Bag section (+ lifelong.bag)")
    # bytecode: the recall in /accessories (/acc, /accbag) and the plugin's setup / shutdown
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)

    def calls(cn, mn):
        out_ = []
        m = [x for x in cp.get(PKG + cn).getDeclaredMethods() if str(x.getName()) == mn][0]
        ci = m.getMethodInfo().getCodeAttribute().iterator()
        cpl = m.getMethodInfo().getConstPool()
        IP = JClass("javassist.bytecode.InstructionPrinter")
        while ci.hasNext():
            out_.append(str(IP.instructionString(ci, ci.next(), cpl)))
        return "\n".join(out_)
    ex = calls("AccCmd", "execute")
    K.check("AccOnce.recall" in ex and "AccOnce.recallText" in ex and ex.index("AccOnce.recall") < ex.index("openCustomPage"),
            "CF /accessories (/acc, /accbag) runs AccOnce.recall BEFORE it opens the page")
    su = calls("SkyyAccessoriesPlugin", "setup")
    K.check(all(("%s.<init>" % c) in su for c in ("AccOnceDropSys", "AccOnceThrowSys", "AccOnceInvSys", "AccOnceReady")) and "AccOnce.publish" in su
            and "registerGlobal" in su and "lifelong" in su, "CF setup registers the three systems + the ready hook, publishes, sets AccOnce.DIR (lifelong)")
    K.check("AccOnce.unpublish" in calls("SkyyAccessoriesPlugin", "shutdown"), "CF shutdown unpublishes")
    K.save()


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    f = os.path.join(home, "config.properties")
    t0 = open(f, "rb").read() if os.path.isfile(f) else None
    h0 = HK.tree_hash(home)
    snaps, on = [], []
    for start in (1, 2):
        L = loader_for(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        J("AccStore").DIR = Paths.get(os.path.join(home, "bags"))
        J("AccCfg").FILE = Paths.get(f)
        J("AccCfg").migrate051()
        J("AccCfg").migrate055()
        J("AccCfg").migrate0518()
        J("AccCfg").load(True)
        J("AccNotice").FILE = Paths.get(os.path.join(home, "notices.properties"))
        J("AccNotice").load()
        J("AccSnd").load(Paths.get(home))
        J("AccOnce").DIR = Paths.get(os.path.join(home, "lifelong"))
        J("AccOnce").publish()
        J("CfgPub").start(Paths.get(mods), None)
        J("CfgPub").shutdown()
        J("AccOnce").unpublish()
        on.append(bool(J("AccDefs").LIFELONG))
        snaps.append(HK.tree_hash(home))
    K.check(t0 is not None and b"lifelong.bag" not in t0, "D the live config.properties has no lifelong.bag line (a 0.5.19 file)")
    K.check(on == [True, True], "D both starts: the missing line = on")
    K.check(snaps[0] == h0 and snaps[1] == h0, "D neither start changed any file of the copy (%d files)" % len(h0))
    K.check(not os.path.exists(os.path.join(home, "lifelong")), "D no lifelong/ folder without a sweep")
    K.save()


# the compare's non-class check: this round also changes the bag item (no recipe), the tab items' ItemLevel and the bag's tooltip (phase S)
HK.run_compare = OH.compare_allowing(lambda n: n.endswith(".lang") or n.startswith("Server/Item/Items/"))


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("assets", run_assets), ("life", run_life), ("cfg", run_cfg), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyAccessories"))
