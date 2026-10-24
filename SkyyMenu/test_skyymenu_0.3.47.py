"""Harness for SkyyMenu 0.3.47 (Home > Right now shows unspent tree points; tools/menu_0_3_47_patch.py). Build first:
    python tools/menu_0_3_47_patch.py && python SkyyMenu/build_skyymenu_0.3.47.py
    python SkyyMenu/test_skyymenu_0.3.47.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the SkyyMenu 0.3.19 engine stand-ins, -Xverify:all):
  S    static   the patch re-runs to identical bytes; no new system / command; line endings kept; non-class jar entries = manifest only
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.46 -> 0.3.47: exactly the listed members differ
  NOW  EXECUTED - the real MenuPage (Home built, rows read from the built markup, clicks through handleDataEvent):
       ZERO    no SkyyTrees (no tree:<uuid>) / a non-String value / garbage entries / every tree spent -> no tree row, Nothing waiting
       ONE     one tree with points -> "5 unspent points in Mining  >"; 1 point = "1 unspent point in ..."; the click runs /tree mining as
               the player with exactly ONE page packet
       MANY    6 trees -> the top 3 by points (ties keep SkyyTrees' order; the class tree = "your class tree") + "and 3 more trees with
               points"; class row -> /tree class; the more row -> Character > Trees (the Trees tab's open path: hub tab -> /tree)
       ORDER   quest + tree rows + mod alerts: quest first, trees next, alerts last, 8 rows in all (AL_SHOW)
       NOCMD   /tree missing -> the click falls back to the Trees tab path (no /tree mining run), one packet, never throws
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "dev"))
import harness_kit as HK
import skyybuild as B

_s45 = importlib.util.spec_from_file_location("test_skyymenu_0_3_45", os.path.join(HERE, "test_skyymenu_0.3.45.py"))
T45 = importlib.util.module_from_spec(_s45)
_s45.loader.exec_module(T45)
T35 = T45.T35
T19 = T45.T19
T29 = T35.T29

VERSION = "0.3.47"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.46.jar")
GEN = os.path.join(HERE, "build_skyymenu_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.46.py")
PATCH = os.path.join(ROOT, "tools", "menu_0_3_47_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menu047", "menu")))
PKG = "com.skyy.menu."
ADDED = []
EXPECT = {
    "MenuPage": ["+m okTree", "+m openTree", "+m treeRows", "~m alertClick", "~m nowRows"],
    "MenuData": ["+f TR_SHOW", "~<clinit>"],
    # the version string only (VERSION in the Server Setup header / export / ops page / the ready line) - as in 0.3.46
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "SkyyMenuPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.3.47"') == 1, "S VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    diff = sorted(n for n in set(zn.namelist()) | set(zo.namelist()) if not n.endswith(".class")
                  and (n not in zn.namelist() or n not in zo.namelist() or zn.read(n) != zo.read(n)))
    K.check(diff == ["manifest.json"], "S non-class jar entries changed = manifest only: %s" % diff)
    K.save()


def run_now(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_t")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_t", "Skyy_SkyyMenu")
    for sub in ("layouts", "settings"):
        os.makedirs(os.path.join(home, sub), exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    JV("SetReg").registerOwn()
    JV("MenuIO").begin()
    HB, MH, MD = JV("HubBar"), JV("MenuHub"), JV("MenuData")
    br = JV("MenuUtil").bridge()
    E.br = br
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = E.jf(UniC.class_, "playersByUuid").get(UniC.get())
    Obj, Int, Dbl = JClass("java.lang.Object"), JClass("java.lang.Integer"), JClass("java.lang.Double")
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE

    @JImplements("java.util.function.Function")
    class F(object):
        def __init__(self, r):
            self.r = r

        @JOverride
        def apply(self, x):
            return self.r(x) if callable(self.r) else self.r

    def cmd_on(*names):
        for n_ in names:
            E.CM.cmds.put(n_, E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))

    def cmd_off(*names):
        for n_ in names:
            E.CM.cmds.remove(n_)

    P = E.player(E.UUID.fromString("00000000-0000-0000-0000-000000003470"), name="SkyyTrees047")
    byU.put(P.pr.getUuid(), P.pr)
    E.UniH.PL.add(P.pr)
    E.PLAYERS.add(P.pr)
    u = P.pr.getUuid()
    TK = "tree:" + str(u)
    cmd_on("tree", "quests")
    # the Trees tab as SkyyTrees registers it (no open Function here = the bar's command fallback /tree, as in game when its Function fails)
    HB.put("character", "trees", "SkyyTrees", "Trees", 20, "tree", None, None)
    MH.register()
    K.check(int(MD.TR_SHOW) == 3, "MenuData.TR_SHOW = 3")

    def openm():
        m = JV("MenuPage")(P.pr, "main")
        P.pm.openCustomPage(P.ref, P.st, m)
        E.pump(P)
        return m

    def rows(m):
        c, ev = T29.build_page(m, P)
        sets = dict((s_, d) for ty, s_, t, d in c if ty == "Set")
        def txt(v):   # a Set's data is the JSON {"0": <value>}
            return json.loads(str(v))["0"]
        return [txt(sets["#SkyyMHmA%d.Text" % i]) for i in range(8) if ("#SkyyMHmA%d.Text" % i) in sets], c

    def click(m, a):
        E.CM.lines.clear()
        n0 = len(E.sent(P))
        m.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % a)
        E.pump(P)
        return [str(x) for x in E.CM.lines], len(E.sent(P)) - n0

    def tree_rows(rs):
        return [r for r in rs if "unspent point" in r or "more tree" in r]

    # ================================================================ ZERO
    br.remove(TK)
    m = openm()
    rs, c = rows(m)
    K.check(rs == [] and any(t is not None and "Nothing waiting" in str(t) for ty, s_, t, d in c),
            "ZERO: no SkyyTrees (no tree:<uuid>) -> no Right now row, 'Nothing waiting' (%s)" % rs)
    K.check(len(JV("MenuPage").treeRows(u)) == 0 and len(JV("MenuPage").treeRows(None)) == 0, "ZERO: treeRows(no bridge / null uuid) = empty")
    br.put(TK, Int(5))
    K.check(len(JV("MenuPage").treeRows(u)) == 0, "ZERO: a non-String tree:<uuid> -> no rows, no throw")
    for bad in ("", "garbage", ",,,", "Mining:x/y", ":0/5", "Mi;ne:0/5", "Mining:5", "Mining/5:3", "Mining:9/5", "Class:3/3,Mining:0/0"):
        br.put(TK, bad)
        K.check(len(JV("MenuPage").treeRows(u)) == 0, "ZERO: bad / spent value %r -> no rows" % bad)
    br.put(TK, "Mining:0/0,Foraging:4/4,Farming:2/2,Class:7/7")
    m = openm()
    rs, c = rows(m)
    K.check(tree_rows(rs) == [], "ZERO: every tree spent -> no tree row (%s)" % rs)

    # ================================================================ ONE
    br.put(TK, "Mining:2/7,Foraging:3/3,Farming:x/1,Cooking:0/0,Class:4/4")
    m = openm()
    rs, c = rows(m)
    K.eq(rs, ["5 unspent points in Mining  >"], "ONE: one tree with points -> one row (a bad entry beside it skipped)")
    ln, np = click(m, "halert0")
    K.check(ln == ["tree mining"], "ONE: the click runs /tree mining as the player (%s)" % ln)
    K.eq(np, 1, "ONE: the click answers with exactly ONE page packet (the grid emptied; the command opens Trees' page)")
    br.put(TK, "Farming:4/5")
    m = openm()
    rs, c = rows(m)
    K.eq(rs, ["1 unspent point in Farming  >"], "ONE: 1 point -> 'point' (singular)")

    # ================================================================ MANY
    br.put(TK, "Mining:0/3,Foraging:0/9,Farming:1/2,Cooking:0/9,Fishing:1/5,Class:0/12")
    m = openm()
    rs, c = rows(m)
    K.eq(rs, ["12 unspent points in your class tree  >", "9 unspent points in Foraging  >", "9 unspent points in Cooking  >",
              "and 3 more trees with points  >"], "MANY: top 3 by points (tie keeps SkyyTrees' order) + the more row")
    ln, np = click(m, "halert0")
    K.check(ln == ["tree class"] and np == 1, "MANY: the class row runs /tree class, one packet (%s, %d)" % (ln, np))
    m = openm()
    rows(m)
    ln, np = click(m, "halert2")
    K.check(ln == ["tree cooking"] and np == 1, "MANY: row 3 runs /tree cooking (%s, %d)" % (ln, np))
    m = openm()
    rows(m)
    ln, np = click(m, "halert3")
    K.check(ln == ["tree"] and np == 1, "MANY: the more row opens Character > Trees (the Trees tab path -> its /tree fallback) (%s, %d)" % (ln, np))
    br.put(TK, "Mining:0/3,Foraging:0/9,Farming:1/2,Cooking:0/9")
    K.eq([list(map(str, r)) for r in JV("MenuPage").treeRows(u)][-1], ["and 1 more tree with points", "character:trees"], "MANY: 1 more -> singular")

    # ================================================================ ORDER + the AL_SHOW cap
    def hud(x):
        return JArray(Obj)(["Tutorial", "1 / 3", "Mine 10 iron", "3/10", Dbl(0.3), "", Int(-1), FALSE])
    br.put("quest:fn:hud", F(hud))
    br.put("home:alert:AAA", F("Alert a1|world:island\nAlert a2|world:island\nAlert a3|world:island"))
    br.put("home:alert:BBB", F("Alert b1|world:island\nAlert b2|world:island\nAlert b3|world:island"))
    br.put(TK, "Mining:0/3,Foraging:0/9,Farming:1/2,Cooking:0/9,Fishing:1/5,Class:0/12")
    m = openm()
    rs, c = rows(m)
    K.check(len(rs) == 8 and rs[0].startswith("Quest: Mine 10 iron") and rs[1].startswith("12 unspent points in your class tree")
            and rs[4] == "and 3 more trees with points  >" and rs[5:] == ["Alert a1  >", "Alert a2  >", "Alert a3  >"],
            "ORDER: quest, then the 4 tree rows, then the mod alerts, 8 rows in all (%s)" % rs)
    ln, np = click(m, "halert1")
    K.check(ln == ["tree class"], "ORDER: the class row (2nd) still runs /tree class (%s)" % ln)
    br.remove("quest:fn:hud")
    br.remove("home:alert:AAA")
    br.remove("home:alert:BBB")

    # ================================================================ NOCMD
    cmd_off("tree")
    br.put(TK, "Mining:2/7")
    m = openm()
    rs, c = rows(m)
    K.eq(rs, ["5 unspent points in Mining  >"], "NOCMD: the row is still drawn from the bridge")
    try:
        ln, np = click(m, "halert0")
        K.check("tree mining" not in ln and np == 1, "NOCMD: /tree missing -> the Trees tab path, no /tree mining, one packet (%s, %d)" % (ln, np))
    except Exception as e:
        K.check(False, "NOCMD: the click threw %s" % e)
    cmd_on("tree")
    br.remove(TK)
    MH.clearAll()
    JV("MenuIO").stop(2000)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("now", run_now), ("live", T35.run_live)], script=__file__, live=(T35.LIVE_DIR, "Skyy_SkyyMenu"))
