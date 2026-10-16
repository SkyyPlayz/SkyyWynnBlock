"""Harness for SkyyMenu 0.3.31 (round craft01: THE CRAFTING HUB; tools/menu_0_3_31_patch.py). Build first:
    python tools/menu_0_3_31_patch.py && python SkyyMenu/build_skyymenu_0.3.31.py

    python SkyyMenu/test_skyymenu_0.3.31.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the 0.3.19 / 0.3.30 harnesses' engine stand-ins: a recording packet sink, a component
store, worlds, the Universe, the REAL PageManager / WindowManager, a command manager that records lines):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.30 -> 0.3.31: MenuData (the hub title / command / blurb / stand-in tables), the plugin's setup, the version texts;
                + HubCraftCmd; non-class entries: manifest.json only
  N31  EXECUTED: hub:def:smithing = {Crafting, crafting, ...} (the id unchanged); the stand-in tabs: Crafting (order 5, /craft) before
       Smithing (order 10, gear:fn:smithing / /smithing), Reforge / Upgrade / Identify unchanged; SkyySacks' own Crafting tab put before
       SkyyMenu is kept (never replaced), one put after replaces the stand-in; /crafting = MenuHub.run(smithing) -> the Crafting tab
       (/craft), with gear:fn:smithing the Smithing tab still opens SkyyGear's page; the Home hub tile reads "Crafting hub ... Command:
       /crafting"; saved shortcuts tab:smithing:recipes / hub:smithing still resolve; clearAll keeps the owner's tab
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.30 harness's run_live on this jar)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

_orig_compare = HK.run_compare
_s30 = importlib.util.spec_from_file_location("test_skyymenu_0_3_30", os.path.join(HERE, "test_skyymenu_0.3.30.py"))
T30 = importlib.util.module_from_spec(_s30)
_s30.loader.exec_module(T30)
HK.run_compare = _orig_compare     # the 0.3.30 harness swapped in its own non-class list; 0.3.31 changes classes + manifest.json only
T19 = T30.T19

VERSION = "0.3.31"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.30.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "craft01", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMenu")
ADDED = ["HubCraftCmd"]
EXPECT = {
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~m header"],
    "MenuData": ["~<clinit>"],
    "OpsPage": ["~<clinit>"],
    "SkyyMenuPlugin": ["~m setup"],
}


def run_n31(out, jar, scratch, _home):
    from jpype import JClass, JArray, JImplements, JOverride
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_n31")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_n31")
    lay_dir = os.path.join(home, "layouts")
    os.makedirs(lay_dir, exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(lay_dir)
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    JV("SetReg").registerOwn()
    JV("MenuIO").begin()
    HB, MH, MD = JV("HubBar"), JV("MenuHub"), JV("MenuData")
    br = JV("MenuUtil").bridge()
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = T30.jf(UniC.class_, "playersByUuid").get(UniC.get())
    TRUE = JClass("java.lang.Boolean").TRUE
    Obj, Int = JClass("java.lang.Object"), JClass("java.lang.Integer")
    SysC = JClass("java.lang.System")
    same = lambda a, b_: a is not None and b_ is not None and int(SysC.identityHashCode(a)) == int(SysC.identityHashCode(b_))
    calls = []

    @JImplements("java.util.function.Function")
    class F(object):
        def __init__(self, r, tag=""):
            self.r, self.tag = r, tag

        @JOverride
        def apply(self, x):
            try:
                calls.append((self.tag, [str(v) for v in x] if hasattr(x, "__len__") and not isinstance(x, str) else str(x)))
            except Exception:
                calls.append((self.tag, str(x)))
            return self.r
    P = E.player(E.PLAIN, name="SkyyPlain")
    byU.put(E.PLAIN, P.pr)
    E.UniH.PL.add(P.pr)
    E.PLAYERS.add(P.pr)
    u = P.pr.getUuid()

    def cmd_on(*names):
        for n_ in names:
            E.CM.cmds.put(n_, E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    lines = lambda: [str(x) for x in E.CM.lines]
    hubs = list(SUI.HUBS)
    si = hubs.index("smithing")
    K.check(str(MD.HUB_ID[si]) == "smithing" and str(MD.HUB_TITLE[si]) == "Crafting" and str(MD.HUB_CMD[si]) == "crafting",
            "N31: the hub id stays 'smithing', its title is Crafting and its command /crafting")
    K.check([str(MD.HUB_TITLE[i]) for i in range(len(hubs)) if i != si] == [SUI.HUB_DEFS[h][0] for h in hubs if h != "smithing"],
            "N31: every other hub keeps its title")
    cmd_on("smithing", "reforge", "upgrade", "identify", "craft", "quests", "merchants", "explore", "requip", "vault", "ah", "bazaar", "pets",
           "party", "guild", "tree", "class", "collections", "profiles", "skyyhud", "crafting")
    n = int(MH.register())
    K.eq(n, 7, "N31: Menu's 7 own tabs put")
    d = br.get("hub:def:smithing")
    K.check(d is not None and str(d[0]) == "Crafting" and str(d[1]) == "crafting" and str(d[2]) == "Skyy_Menu_Icon_HubSmithing",
            "N31: hub:def:smithing = {Crafting, crafting, its icon} (row 1 says Crafting on every hub page)")
    rc, gr = br.get("hub:tab:smithing:recipes"), br.get("hub:tab:smithing:gear")
    K.check(rc is not None and str(rc[1]) == "Crafting" and int(rc[2]) == 5 and str(rc[3]) == "craft" and str(rc[6]) == "smithing_recipes",
            "N31: the Crafting stand-in = {Crafting, 5, /craft, its icon} (the same as SkyySacks 0.8.11's own tab)")
    K.check(gr is not None and str(gr[1]) == "Smithing" and int(gr[2]) == 10 and str(gr[3]) == "smithing" and gr[4] is not None,
            "N31: Gear is now SMITHING (order 10, gear:fn:smithing, else /smithing)")
    K.eq([str(t[0]) for t in HB.tabs("smithing", u)], ["recipes", "gear", "reforge", "upgrade", "identify"],
         "N31: the Crafting hub's row 2: Crafting, Smithing, then Reforge / Upgrade / Identify")
    K.eq([str(t[1]) for t in HB.tabs("smithing", u)][:2], ["Crafting", "Smithing"], "N31: the two main pages' labels")
    # /crafting -> the hub's first page (no last tab yet) = Crafting -> /craft as the player
    E.CM.lines.clear()
    r = str(MH.run(P.pr, "smithing"))
    K.check(r == "command" and lines() == ["craft"], "N31: /crafting (MenuHub.run smithing) opens Crafting = /craft (%s %s)" % (r, lines()))
    # with SkyyGear the Smithing tab still opens its page through the bridge
    del calls[:]
    br.put("gear:fn:smithing", F(TRUE, "gear"))
    r = str(HB.open(P.pr, u, "smithing", "gear"))
    K.check(r == "bridge" and calls and calls[0][0] == "gear" and calls[0][1][1] == "craft", "N31: Crafting > Smithing = gear:fn:smithing {uuid, craft} (%s)" % calls)
    br.remove("gear:fn:smithing")
    # the Home tile of the hub + saved shortcuts
    hm = JV("MenuPage")(P.pr, "main")
    P.pm.openCustomPage(P.ref, P.st, hm)
    E.pump(P)
    lk = hm.look("hub:smithing", True)
    body = str(lk[2])
    K.check(str(lk[1]) == "Crafting" and "Crafting hub" in body and "Command: /crafting" in body and "Crafting, Smithing" in body,
            "N31: the Home hub tile: Crafting, its blurb, its tabs, /crafting (%s)" % body.replace("\n", " | "))
    lt = hm.look("tab:smithing:recipes", True)
    K.check(lt is not None and str(lt[1]) == "Crafting" and str(lt[5]) == "ok" and "Crafting > Crafting" in str(lt[2]),
            "N31: a saved shortcut tab:smithing:recipes still resolves (Crafting > Crafting)")
    K.check(str(hm.look("tab:smithing:gear", True)[1]) == "Smithing", "N31: a saved shortcut to Gear now reads Smithing")
    K.check(str(ML.canon("tile:crafting")) == "tab:smithing:recipes", "N31: the old Crafting tile is still the Crafting tab (one entry)")
    # SkyySacks' own tab: put AFTER us replaces the stand-in; clearAll leaves it
    own = JArray(Obj)(["SkyySacks", "Crafting", Int(5), "craft", None, None, "smithing_recipes"])
    br.put("hub:tab:smithing:recipes", own)
    removed = int(MH.clearAll())
    K.check(same(br.get("hub:tab:smithing:recipes"), own) and br.get("hub:tab:smithing:gear") is None and br.get("hub:def:smithing") is None,
            "N31: clearAll removes Menu's stand-ins + defs, never SkyySacks' own Crafting tab (%d removed)" % removed)
    # put BEFORE us: never replaced
    HB.mine().remove("hub:tab:smithing:recipes")
    MH.register()
    K.check(same(br.get("hub:tab:smithing:recipes"), own), "N31: SkyySacks' Crafting tab put BEFORE SkyyMenu is kept (no stand-in over it)")
    MH.clearAll()
    # /crafting: the command class (everyone; runs the smithing hub)
    z = zipfile.ZipFile(jar)
    cb = z.read("com/skyy/menu/HubCraftCmd.class")
    pc = z.read("com/skyy/menu/SkyyMenuPlugin.class")
    K.check(b"crafting" in cb and b"hytale:Adventurer" in cb and b"smithing" in cb and b"HubCraftCmd" in pc and b"/crafting" in pc,
            "N31: HubCraftCmd = /crafting for hytale:Adventurer, runs MenuHub.run(smithing); the plugin registers it")
    try:
        c = JV("HubCraftCmd")()
        K.check(str(c.getName()) == "crafting", "N31: the command's name is crafting")
    except Exception as e:
        K.notes.append("N31: HubCraftCmd not constructible in the bare JVM (%s) - checked in the class bytes" % str(e)[:100])
    JV("MenuIO").stop(2000)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("n31", run_n31), ("live", T30.run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
