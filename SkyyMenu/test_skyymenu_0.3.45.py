"""Harness for SkyyMenu 0.3.45 (elem1: the element sections on Your Stats + SkyyGear's own tree rows in the Trees column;
tools/menu_0_3_45_patch.py). Build first:
    python tools/menu_0_3_45_patch.py && python SkyyMenu/build_skyymenu_0.3.45.py
    python SkyyMenu/test_skyymenu_0.3.45.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the SkyyMenu 0.3.19 engine stand-ins, -Xverify:all):
  S    static   the patch re-runs to identical bytes; no new system / command; line endings kept
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.44 -> 0.3.45: exactly the listed members differ
  EL   EXECUTED on real bridge values: the Elements rows from a gear:fn:elemTotals stub ("Fire 9% / 12 Def", Poison "20% over 10s"), no
       SkyyGear 0.3.39 = one row naming it; the strong / weak chart (5 rows, +25% on the beaten element, -25% on its own, - elsewhere, "beats
       Air") from mob:elem:wheel / numbers + the defaults without SkyyMobs + a new wheel / numbers; the wheel / boss / exception rows; the
       reactions; gear:trees:<uuid> in the Trees column (+ SkyyTrees' gear:extras, only those wait for tree:reads:SkyyGear); the section order
       Main, Combat, Gathering, Elements, Strong and weak, Reactions, Sources; the PAGE BUILT: page rules + assert_menu_page, the chart header
       row's own labels set, a chart cell coloured green / red / dim, Refresh = exactly one packet
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "dev"))
import harness_kit as HK
import skyybuild as B
import skyyui as SUI

_s42 = importlib.util.spec_from_file_location("test_skyymenu_0_3_42", os.path.join(HERE, "test_skyymenu_0.3.42.py"))
T42 = importlib.util.module_from_spec(_s42)
_s42.loader.exec_module(T42)
T35 = T42.T35
T19 = T42.T19

VERSION = "0.3.45"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.44.jar")
GEN = os.path.join(HERE, "build_skyymenu_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.44.py")
PATCH = os.path.join(ROOT, "tools", "menu_0_3_45_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "elem1", "menu")))
PKG = "com.skyy.menu."
ADDED = []
EXPECT = {
    "StatsCalc": ["+f EL_COLS", "+f EL_EXC", "+f EL_HEAD", "+f EL_N", "+f EL_NOGEAR", "+f EL_RX", "+f EL_WHEEL", "+m elemIdx", "+m elemNums", "+m elemRows",
                  "+m elemTotals", "+m wheelOf", "~<clinit>", "~m allRows", "~m treesKv"],
    "StatsPage": ["~m build"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "MenuData": ["~<clinit>"], "OpsPage": ["~<clinit>"],
    "SkyyMenuPlugin": ["~m setup"],          # the version texts
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check("VERSION = \"0.3.45\"" in g and g.count('VERSION = "0.3.45"') == 1, "S VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_el(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_e")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_e")
    sdir = os.path.join(home, "settings")
    os.makedirs(os.path.join(home, "layouts"), exist_ok=True)
    os.makedirs(sdir, exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    SS, SR = JV("SetStore"), JV("SetReg")
    SS.DIR = Paths.get(sdir)
    SR.ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    SR.registerOwn()
    JV("MenuIO").begin()
    MH = JV("MenuHub")
    BR = JV("MenuUtil").bridge()
    E.br = BR
    MH.register()
    UUID = JClass("java.util.UUID")
    SC = JV("StatsCalc")
    sx = UUID.fromString("00000000-0000-0000-0000-000000000345")

    @JImplements("java.util.function.Function")
    class Tot(object):
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, o):
            return self.ans

    def section(name):
        al = [[None if y is None else str(y) for y in r_] for r_ in SC.allRows(sx, None)]
        i = [k for k, r_ in enumerate(al) if r_[0] is None and r_[1] == name][0]
        rs = []
        for r_ in al[i + 1:]:
            if r_[0] is None and r_[1] is not None:
                break
            rs.append(r_)
        return al, rs
    # ---- Elements: no SkyyGear 0.3.39
    al, rs = section("Elements")
    heads = [r_[1] for r_ in al if r_[0] is None and r_[1] is not None]
    K.eq(heads, ["Main", "Combat", "Gathering", "Elements", "Strong and weak", "Reactions", "Sources"], "EL the sections in order")
    K.eq(rs, [["Elements", "-", "needs SkyyGear 0.3.39 (element damage + Defence)"]], "EL without gear:fn:elemTotals: one row naming SkyyGear 0.3.39")
    BR.put("gear:fn:elemTotals", Tot("Earth:3/8,Thunder:0/2,Water:5/0,Fire:9/12,Air:0/0,Poison:20"))
    _a, rs = section("Elements")
    K.eq(rs[3], ["Fire", "9% / 12 Def", "damage % of your hits / Defence vs Fire"], "EL Fire 9% / 12 Def")
    K.eq([r_[0] for r_ in rs], ["Earth", "Thunder", "Water", "Fire", "Air", "Poison"], "EL one row per element + Poison")
    K.eq(rs[5][:2], ["Poison", "20% over 10s"], "EL Poison 20% over 10s (poison.time default)")
    BR.put("gear:fn:elemTotals", Tot(None))
    _a, rs = section("Elements")
    K.eq(rs[0][:2], ["Elements", "-"], "EL a null answer (cache not filled yet) = one row: %s" % rs[0])
    # ---- the chart: defaults (no SkyyMobs)
    _a, rs = section("Strong and weak")
    K.eq(rs[0], [None, None, "", "Earth mob", "Thunder mob", "Water mob", "Fire mob", "Air mob", "", "Your element", "Beats"], "EL the chart's own column header row")
    tr = [r_ for r_ in rs if r_[0] and r_[0].startswith("Your ")]
    K.eq([r_[0] for r_ in tr], ["Your Earth", "Your Thunder", "Your Water", "Your Fire", "Your Air"], "EL one row per element (wheel order)")
    K.eq(tr[3][:9], ["Your Fire", "beats Air", "", "-", "-", "-", "-25%", "+25%", ""], "EL Your Fire: +25% on Air mobs, -25% on Fire mobs, - elsewhere")
    K.eq(tr[4][1], "beats Earth", "EL Air beats Earth (the wheel closes)")
    names = [r_[0] for r_ in rs if r_[0]]
    K.check(["Wheel", "Bosses", "Exceptions"] == [n for n in names if not n.startswith("Your ")], "EL the wheel / boss / exception rows")
    K.check([r_ for r_ in rs if r_[0] == "Wheel"][0][2] == "Earth, Thunder, Water, Fire, Air - each beats the next, Air beats Earth" and [r_ for r_ in rs if r_[0] == "Bosses"][0][1] == "-50%",
            "EL the wheel line + the boss -50% (defaults)")
    BR.put("mob:elem:wheel", "Fire>Water>Earth>Thunder>Air")
    BR.put("mob:elem:numbers", "40;10;60")
    _a, rs = section("Strong and weak")
    tr = [r_ for r_ in rs if r_[0] and r_[0].startswith("Your ")]
    K.eq(tr[0][:9], ["Your Fire", "beats Water", "", "-", "-", "+40%", "-10%", "-", ""], "EL SkyyMobs' wheel + numbers: Fire beats Water +40, own -10")
    K.eq([r_ for r_ in rs if r_[0] == "Bosses"][0][1], "-60%", "EL the boss number from mob:elem:numbers")
    BR.put("mob:elem:wheel", "junk")
    _a, rs = section("Strong and weak")
    K.eq([r_ for r_ in rs if r_[0] == "Wheel"][0][2], "Earth, Thunder, Water, Fire, Air - each beats the next, Air beats Earth", "EL a bad wheel = the default")
    K.eq([r_ for r_ in rs if r_[0] == "Exceptions"][0][2], "Yeti, Frost Golems, frost skeletons + zombies: weak to Fire", "EL elem1fix2: the default exceptions (no mob:elem:custom)")
    BR.put("mob:elem:custom", JClass("java.lang.Boolean").TRUE)
    _a, rs = section("Strong and weak")
    K.eq([r_ for r_ in rs if r_[0] == "Exceptions"][0][2], "your own table (Server Setup, Mobs, Elements)", "EL elem1fix2: an edited SkyyMobs table = no default exception names")
    BR.remove("mob:elem:custom")
    BR.remove("mob:elem:wheel")
    BR.remove("mob:elem:numbers")
    _a, rs = section("Reactions")
    K.eq([r_[0] for r_ in rs], ["Wildfire", "Shatter", "Steam", "Quake"], "EL the four planned reactions")
    K.check(all(r_[1] == "later" for r_ in rs), "EL ... all marked later")
    # ---- the Trees column: SkyyGear's gear:trees
    BR.put("gear:fn:stats", Tot(None))
    BR.put("gear:stats:" + str(sx), "str:40,cc:10")
    BR.put("gear:trees:" + str(sx), "str:4,cc:3")
    rs0 = [[None if y is None else str(y) for y in r_] for r_ in SC.rows(sx, 0, None)]
    st_ = [r_ for r_ in rs0 if r_[0] == "Strength"][0]
    K.eq(st_, ["Strength", "44", "", "-", "+40", "-", "-", "+4", "-"], "EL Strength: SkyyGear's own tree rows (gear:trees) in the Trees column (no tree:reads needed)")
    xm = JClass("java.util.concurrent.ConcurrentHashMap")()
    xm.put("trees", "str:3")
    BR.put("gear:extras:" + str(sx), xm)
    rs0 = [[None if y is None else str(y) for y in r_] for r_ in SC.rows(sx, 0, None)]
    K.eq([r_ for r_ in rs0 if r_[0] == "Strength"][0][7], "+4", "EL SkyyTrees' gear:extras still wait for tree:reads:SkyyGear")
    BR.put("tree:reads:SkyyGear", "gear:extras")
    rs0 = [[None if y is None else str(y) for y in r_] for r_ in SC.rows(sx, 0, None)]
    K.eq([r_ for r_ in rs0 if r_[0] == "Strength"][0][7], "+7", "EL ... then both add (4 + 3)")
    al = [[None if y is None else str(y) for y in r_] for r_ in SC.allRows(sx, None)]
    K.check(al[-1][0] == "Total" and "Rebirth" in al[-1][2] and "tree" not in al[-1][2], "EL the legend's Total note names only the Rebirth bonus now: %s" % al[-1])
    # ---- the page itself
    BR.put("gear:fn:elemTotals", Tot("Earth:3/8,Thunder:0/2,Water:5/0,Fire:9/12,Air:0/0,Poison:20"))
    al = [[None if y is None else str(y) for y in r_] for r_ in SC.allRows(sx, None)]
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = E.jf(UniC.class_, "playersByUuid").get(UniC.get())

    def openp(X, pg):
        X.pm.openCustomPage(X.ref, X.st, pg)
        E.pump(X)
        return pg

    def click(X, pg, a):
        n_ = len(E.sent(X))
        pg.handleDataEvent(X.ref, X.st, '{"a":"%s"}' % a)
        k_ = E.kinds(X, n_)
        E.pump(X)
        return k_
    PS = E.player(sx, name="SkyyStatE")
    byU.put(sx, PS.pr)
    stp = openp(PS, JV("StatsPage")(PS.pr, 0))
    c3, e3 = T35.build_page(stp, PS)
    apps3, _x = T35.page_rules(K, c3, e3, "Your Stats (elements)")
    try:
        info = SUI.assert_menu_page(apps3, hub="character", what="Your Stats", sets=[(s, T35.unq(d)) for ty, s, t, d in c3 if ty == "Set"])
        K.check(True, "EL assert_menu_page (rows %d)" % info["rows"])
    except Exception as ex:
        K.check(False, "EL assert_menu_page: %s" % ex)
    sets3 = dict((s, T35.unq(d)) for ty, s, t, d in c3 if ty == "Set")
    ich = [i for i, r_ in enumerate(al) if r_[0] is None and r_[1] is None and len(r_) >= 11][0]
    K.eq([sets3.get("#SkyyStatC%dn%d.Text" % (ich, k_)) for k_ in range(6)] + [sets3.get("#SkyyStatN%d.Text" % ich), sets3.get("#SkyyStatV%d.Text" % ich)],
         ["Earth mob", "Thunder mob", "Water mob", "Fire mob", "Air mob", "", "Your element", "Beats"], "EL the page sets the chart header's own labels")
    ifr = [i for i, r_ in enumerate(al) if r_[0] == "Your Fire"][0]
    cells = dict((k_, [t for ty, s, t, d in c3 if (t or "").startswith("Label #SkyyStatC%dn%d " % (ifr, k_))]) for k_ in range(6))
    K.check("#7ee08a" in cells[4][0] and "#ff7a7a" in cells[3][0] and "#7f93a6" in cells[0][0], "EL the chart cells: +25% green, -25% red, - dim")
    ifi = [i for i, r_ in enumerate(al) if r_[0] == "Fire" and len(r_) == 3][0]
    K.eq(sets3.get("#SkyyStatV%d.Text" % ifi), "9% / 12 Def", "EL the page sets the Fire row")
    kd = click(PS, stp, "trefresh")
    K.eq(len(kd), 1, "EL Refresh answers with exactly one packet (%s)" % kd)
    MH.clearAll()
    JV("MenuIO").stop(2000)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("el", run_el), ("live", T35.run_live)], script=__file__, live=(T35.LIVE_DIR, "Skyy_SkyyMenu"))
