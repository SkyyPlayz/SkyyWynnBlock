"""Harness for SkyyMenu 0.3.49 (Augments A4 charts on Your Stats; tools/menu_0_3_49_patch.py). Build first:
    python tools/menu_0_3_49_patch.py && python SkyyMenu/build_skyymenu_0.3.49.py
    python SkyyMenu/test_skyymenu_0.3.49.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the SkyyMenu 0.3.19 engine stand-ins, -Xverify:all):
  S    static   the patch re-runs to identical bytes; no new system / command; line endings kept; non-class jar entries = manifest only;
                the matrix = what SkyyClasses' SET engine really does: every elemRx(c, s, <reaction>, <element>, ...) call of the SET
                script, grouped per hitting element, = the reaction words of that matrix row (+ RX_NAMES order)
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.48 -> 0.3.49: exactly the listed members differ
  EL   EXECUTED on bridge stand-ins (the real StatsCalc / StatsPage):
       OFF     no SkyyClasses engine: sections Main .. Elements, Strong and weak, Element states, Reactions, Sources; the "Element
               states off - needs SkyyClasses 0.1.51" row; both heads say "Not running"; the 9 states + matrix + 15 reactions still listed
       POISON  gear:fn:elemTotals: Poison row = "modifier, not an element ..."; the element rows unchanged
       STATE   classes:fn:elemHit -> "class only"; + gear:elemStates TRUE -> "on"; SkyyClasses elem.on = false -> "off" (switched off)
       NUMS    config:fn:SkyyClasses numbers rows: steam=40 -> Steam +40%, a bad douse keeps +25%, an unknown key ignored, wetTime=7.5 ->
               Wet 7.5s, burnTime=5 -> Burning 5s, elecFlinch 0.4 -> "flinch 0.4s"; no "{" / "?" left anywhere; elNum 0.25 / 4 / NaN
       POWER   no gear:fn:elemPower -> the tooltip rule row; "Earth:0,Thunder:3,Water:x,Fire:6,Air:0" -> "Thunder 3, Fire 6"; all 0 ->
               "none"; classes:fn:imbue "Thunder;30" -> "Imbue +5 Thunder"; null / junk -> no Imbue row
       MATRIX  the column header row, 5 rows (Earth .. Air) of 10 strings with the element colour, the Fire row's cells
       PAGE    the real page build: page rules + assert_menu_page, the matrix header labels set, a reaction cell in the hitting
               element's colour / a plain effect soft white / "-" dim, the strong / weak chart cells still green / red / dim,
               Refresh = exactly one packet (+ its size)
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "dev"))
import harness_kit as HK
import skyybuild as B
import skyyui as SUI
import skyyelem as EL

_s45 = importlib.util.spec_from_file_location("test_skyymenu_0_3_45", os.path.join(HERE, "test_skyymenu_0.3.45.py"))
T45 = importlib.util.module_from_spec(_s45)
_s45.loader.exec_module(T45)
T35 = T45.T35
T19 = T45.T19

VERSION = "0.3.49"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.48.jar")
GEN = os.path.join(HERE, "build_skyymenu_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.48.py")
PATCH = os.path.join(ROOT, "tools", "menu_0_3_49_patch.py")
CLASSES_PY = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.52.py")          # the SET pin
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "aug4", "menu")))
PKG = "com.skyy.menu."
ADDED = []
EXPECT = {
    "StatsCalc": ["+f EL_CLN", "+f EL_IMBP", "+f EL_MX", "+f EL_MXC", "+f EL_MXH", "+f EL_NK", "+f EL_NROW", "+f EL_NV", "+f EL_OFF", "+f EL_PMAX", "+f EL_PWHOW",
                  "+f EL_RULE", "+f EL_RXL", "+f EL_RXW", "+f EL_ST", "+f EL_STT", "+f EL_STV", "+m elFill", "+m elNum", "+m elNums",
                  "+m elState", "+m elemPower", "+m rxCol", "+m rxrow", "-f EL_RX", "~<clinit>", "~m elemRows"],
    "StatsPage": ["~m build"],
    # the version string only (as in 0.3.48)
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "SkyyMenuPlugin": ["~m setup"], "MenuData": ["~<clinit>"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
RX15 = ["Steam", "Thaw", "Melt", "Fanned", "Douse", "Conduct", "Mud", "Electrocute", "Grounded", "Storm", "Smother", "Shatter", "Sandblast",
        "Wildfire", "Wind Chill"]
SOFT, DIM = "#d6e4ee", "#7f93a6"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.3.49"') == 1, "S VERSION")
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
    # the matrix vs the SET SkyyClasses engine: elemRx(c, s, <rx>, <element>, ...) per hitting element
    ct = open(CLASSES_PY, encoding="utf8").read()
    rxn = eval(re.search(r"RX_NAMES = (\[[^\]]*\])", ct).group(1))
    eng = {}
    for m in re.finditer(r"elemRx\(c, s, (\d+), (\d), ", ct):
        eng.setdefault(int(m.group(2)), set()).add(rxn[int(m.group(1))].title())
    mx = eval(re.search(r"^EL_MX = (\[.*?\]\)\])$", g, re.M | re.S).group(1))
    page = dict((EL.NAMES.index(m_[0]), set(w for c, rx in m_[2] if rx for w in c.split(" / "))) for m_ in mx)
    K.eq(sorted((k, sorted(v)) for k, v in eng.items()), sorted((k, sorted(v)) for k, v in page.items()),
         "S each matrix row's reaction words = the reactions SkyyClasses 0.1.52 runs for that hitting element")
    K.eq(sorted(r.upper() for r in RX15), sorted(rxn), "S the 15 reactions = SkyyClasses RX_NAMES")
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
    sx = UUID.fromString("00000000-0000-0000-0000-000000000349")
    TRUE = JClass("java.lang.Boolean").TRUE

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, ans):
            self.ans = ans
            self.args = []

        @JOverride
        def apply(self, o):
            self.args.append(o)
            return self.ans(o) if callable(self.ans) else self.ans

    def section(name):
        al = [[None if y is None else str(y) for y in r_] for r_ in SC.allRows(sx, None)]
        hd = [k for k, r_ in enumerate(al) if r_[0] is None and r_[1] == name]
        if not hd:
            return al, None, []
        i = hd[0]
        rs = []
        for r_ in al[i + 1:]:
            if r_[0] is None and r_[1] is not None:
                break
            rs.append(r_)
        return al, al[i], rs

    def row(rs, name):
        f = [r_ for r_ in rs if r_[0] == name]
        return f[0] if f else None

    # ---- OFF: no SkyyClasses engine, no SkyyGear
    al, h, rs = section("Elements")
    heads = [r_[1] for r_ in al if r_[0] is None and r_[1] is not None]
    K.eq(heads, ["Main", "Combat", "Gathering", "Elements", "Strong and weak", "Element states", "Reactions", "Sources"], "OFF the sections in order")
    K.eq(h[2], "Your element damage (held weapon), Defence and Element Power.", "OFF the Elements note names Power")
    K.eq([r_[0] for r_ in rs], ["Elements", "Element Power", "Element states"], "OFF Elements: the SkyyGear row, Power, states")
    K.eq(row(rs, "Element Power"), ["Element Power", "-", "see your weapon's tooltip: augment tiers + 3 a rolled line"], "OFF Power = the tooltip rule (no gear:fn:elemPower)")
    K.eq(row(rs, "Element states"), ["Element states", "off", "needs SkyyClasses 0.1.51 (the element states engine)"], "OFF no classes:fn:elemHit = needs SkyyClasses 0.1.51")
    _a, hs, srs = section("Element states")
    _a, hr, rrs = section("Reactions")
    K.check(hs[2].startswith("Not running") and hr[2].startswith("Not running"), "OFF both heads say not running: %s / %s" % (hs[2], hr[2]))
    K.eq([r_[0] for r_ in srs], ["Burning", "Wet", "Chilled", "Frozen", "Shocked", "Quaked", "Gusted", "Poisoned", "Bosses"], "OFF the 7 states + Poisoned + Bosses")
    K.eq(row(srs, "Poisoned")[1], "modifier", "OFF Poisoned is a modifier")
    K.check("not an element" in row(srs, "Poisoned")[2], "OFF ... 'not an element'")
    K.eq(row(srs, "Burning")[1:], ["4s, 3 stacks", "Fire hit: 2% of the hit a second, Water / Earth end it"], "OFF Burning at the defaults")
    K.eq(row(srs, "Shocked")[1:], ["+5% taken", "Thunder hit, 3s: 30% jumps 3 blocks, flinch every 2 hits"], "OFF Shocked at the defaults")
    K.eq(row(srs, "Quaked")[1:], ["0.4s stun", "every 3 Earth hits: -10% Defence for 4s"], "OFF Quaked (0.4 shown exactly)")
    # ---- POISON: gear:fn:elemTotals
    BR.put("gear:fn:elemTotals", Fn("Earth:3/8,Thunder:0/2,Water:5/0,Fire:9/12,Air:0/0,Poison:20"))
    _a, _h, rs = section("Elements")
    K.eq([r_[0] for r_ in rs], ["Earth", "Thunder", "Water", "Fire", "Air", "Poison", "Element Power", "Element states"], "POISON element rows, Poison, Power, states")
    K.eq(row(rs, "Fire"), ["Fire", "9% / 12 Def", "damage % of your hits / Defence vs Fire"], "POISON Fire row unchanged")
    K.eq(row(rs, "Poison"), ["Poison", "20% over 10s", "modifier, not an element: of each hit, stacks, no reactions"], "POISON = a modifier")
    # ---- STATE
    hit = Fn(TRUE)
    BR.put("classes:fn:elemHit", hit)
    _a, _h, rs = section("Elements")
    K.eq(row(rs, "Element states")[1:], ["class only", "class statuses only - weapon hits: Server Setup, Gear"], "STATE engine, no gear:elemStates = class only")
    _a, hs, csr = section("Element states")
    K.eq(hs[2], "What a hit leaves on a target, at Power 5 (10 = double).", "STATE the states head note when it runs")
    K.eq(csr[0], ["Class hits", "30% element", "class statuses (Imbue...): Power 5, this % of the hit"], "FIX4 class only: the Class hits note row first (R.classPart)")
    _a, hr, _x = section("Reactions")
    K.eq(hr[2], "Hit a target that has a state: row = your hit, column = its state.", "STATE the reactions head note when it runs")
    BR.put("gear:elemStates", TRUE)
    _a, _h, rs = section("Elements")
    K.eq(row(rs, "Element states")[1], "on", "STATE + gear:elemStates = on")
    _a, _h, csr = section("Element states")
    K.check(row(csr, "Class hits") is None and csr[0][0] == "Burning", "FIX4 on: no Class hits note row")
    K.eq(len(hit.args), 0, "STATE the page never CALLS classes:fn:elemHit (presence only)")
    cfgv = {"elem.on": "false", "ab.Reactions.numbers": "steam=40,douse=abc,nope=3,elecFlinch=0.4", "ab.ElemStates.numbers": "wetTime=7.5,chainMax=5",
            "ab.Elements.numbers": "burnTime=5,burnStacks=3"}
    cfg = Fn(lambda o: cfgv.get(str(o[1])) if str(o[0]) == "get" else None)
    BR.put("config:fn:SkyyClasses", cfg)
    _a, _h, rs = section("Elements")
    K.eq(row(rs, "Element states")[1:], ["off", "off in Server Setup, Classes, Abilities tab"], "STATE elem.on false = off (FIX2: names the Abilities tab)")
    _a, _h, csr = section("Element states")
    K.check(row(csr, "Class hits") is None, "FIX4 switched off: no Class hits note row")
    _a, hs, _x = section("Element states")
    K.check(hs[2].startswith("Not running"), "STATE switched off: the states head says not running")
    cfgv["elem.on"] = "true"
    # ---- NUMS
    _a, _h, srs = section("Element states")
    _a, _h, rrs = section("Reactions")
    K.eq(row(rrs, "Steam")[1], "+40%", "NUMS steam=40 -> Steam +40%")
    K.eq(row(rrs, "Douse")[1], "+25%", "NUMS a bad douse value keeps the default +25%")
    K.eq(row(srs, "Wet")[1], "7.5s", "NUMS wetTime=7.5 -> Wet 7.5s")
    K.eq(row(srs, "Burning")[1], "5s, 3 stacks", "NUMS burnTime=5 -> Burning 5s")
    K.eq(row(rrs, "Electrocute")[2], "Thunder on Wet: flinch 0.4s, chains to 5 Wet enemies", "NUMS elecFlinch / chainMax filled")
    K.check(any("ab.Reactions.numbers" == str(a[1]) for a in cfg.args), "NUMS read through config:fn:SkyyClasses get")
    al = [[None if y is None else str(y) for y in r_] for r_ in SC.allRows(sx, None)]
    K.check(not [r_ for r_ in al for x in r_ if x is not None and ("{" in x or "?" in x or "(" == x[:1])], "NUMS no '{' / '?' left in any row")
    K.eq([str(SC.elNum(v)) for v in (0.25, 4.0, 1.5, float("nan"), 12.345)], ["0.25", "4", "1.5", "0", "12.35"], "NUMS elNum")
    BR.remove("config:fn:SkyyClasses")
    # ---- POWER
    _a, _h, rs = section("Elements")
    K.check(row(rs, "Imbue") is None, "POWER no classes:fn:imbue = no Imbue row")
    BR.put("gear:fn:elemPower", Fn("Earth:0,Thunder:3,Water:x,Fire:6,Air:0"))
    _a, _h, rs = section("Elements")
    K.eq(row(rs, "Element Power"), ["Element Power", "held weapon", "Thunder 3, Fire 6"], "POWER gear:fn:elemPower -> Thunder 3, Fire 6")
    BR.put("gear:fn:elemPower", Fn("Earth:12,Thunder:10,Water:99,Fire:6,Air:0"))
    _a, _h, rs = section("Elements")
    K.eq(row(rs, "Element Power")[2], "Earth 10, Thunder 10, Water 10, Fire 6", "FIX3 Power shown clamped to the engine's 10")
    BR.put("gear:fn:elemPower", Fn("Earth:0,Thunder:0,Water:0,Fire:0,Air:0"))
    _a, _h, rs = section("Elements")
    K.eq(row(rs, "Element Power")[1:], ["none", "no element Power on your held weapon"], "POWER all 0 = none")
    BR.put("gear:fn:elemPower", Fn(None))
    _a, _h, rs = section("Elements")
    K.eq(row(rs, "Element Power")[1], "-", "POWER a null answer = the rule row")
    BR.remove("gear:fn:elemPower")
    imb = Fn("Thunder;30")
    BR.put("classes:fn:imbue", imb)
    _a, _h, rs = section("Elements")
    K.eq(row(rs, "Imbue"), ["Imbue", "+5 Thunder", "Element Power while your Imbue runs"], "POWER Imbue Thunder;30 -> +5 Thunder")
    K.check(str(imb.args[-1]) == str(sx), "POWER classes:fn:imbue gets the player's UUID")
    BR.put("classes:fn:imbue", Fn("junk"))
    _a, _h, rs = section("Elements")
    K.check(row(rs, "Imbue") is None, "POWER junk answer = no Imbue row")
    BR.put("classes:fn:imbue", Fn("Fire;10"))
    # ---- MATRIX
    al, hr, rrs = section("Reactions")
    K.eq(rrs[0], [None, None, "", "Burning", "Wet", "Chilled / Frozen", "Shocked", "Quaked", "Gusted", "Your hit", "It causes"], "MATRIX column header row")
    mrows = [r_ for r_ in rrs if len(r_) == 10]
    K.eq([r_[0] for r_ in mrows], ["Earth hit", "Thunder hit", "Water hit", "Fire hit", "Air hit"], "MATRIX 5 rows, Wynn order")
    K.eq([r_[9] for r_ in mrows], [EL.COLORS[n] for n in EL.NAMES], "MATRIX each row carries its element colour")
    K.eq(row(rrs, "Fire hit")[:9], ["Fire hit", "Burning", "", "+1 stack", "Steam", "Thaw / Melt", "-", "-", "Fanned"], "MATRIX the Fire row")
    K.eq(row(rrs, "Thunder hit")[3:9], ["-", "Electrocute", "-", "Refresh", "Grounded", "Storm"], "MATRIX the Thunder row")
    K.eq([r_[0] for r_ in rrs if len(r_) == 3], RX15 + ["One a hit", "Poison"], "MATRIX the 15 reaction rows + the rules")
    K.eq(row(rrs, "Poison")[1:], ["no reactions", "a weapon modifier, not an element - nothing reacts with it"], "MATRIX Poison = no reactions")
    K.eq([str(SC.rxCol(JClass("java.lang.String")[:]([x for x in row(rrs, "Fire hit")]), k)) for k in range(6)],
         [SOFT, EL.COLORS["Fire"], EL.COLORS["Fire"], DIM, DIM, EL.COLORS["Fire"]], "MATRIX rxCol: reaction = Fire orange, plain = soft, - = dim")
    # ---- PAGE
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
    PS = E.player(sx, name="SkyyStatA4")
    byU.put(sx, PS.pr)
    stp = openp(PS, JV("StatsPage")(PS.pr, 0))
    c3, e3 = T35.build_page(stp, PS)
    apps3, _x = T35.page_rules(K, c3, e3, "Your Stats (A4 charts)")
    try:
        info = SUI.assert_menu_page(apps3, hub="character", what="Your Stats", sets=[(s, T35.unq(d)) for ty, s, t, d in c3 if ty == "Set"])
        K.check(True, "PAGE assert_menu_page (rows %d)" % info["rows"])
    except Exception as ex:
        K.check(False, "PAGE assert_menu_page: %s" % ex)
    sets3 = dict((s, T35.unq(d)) for ty, s, t, d in c3 if ty == "Set")
    al = [[None if y is None else str(y) for y in r_] for r_ in SC.allRows(sx, None)]
    ich = [i for i, r_ in enumerate(al) if r_[0] is None and r_[1] is None and len(r_) >= 11 and r_[3] == "Burning"][0]
    K.eq([sets3.get("#SkyyStatC%dn%d.Text" % (ich, k_)) for k_ in range(6)] + [sets3.get("#SkyyStatN%d.Text" % ich), sets3.get("#SkyyStatV%d.Text" % ich)],
         ["Burning", "Wet", "Chilled / Frozen", "Shocked", "Quaked", "Gusted", "Your hit", "It causes"], "PAGE the matrix header labels set")

    def cell(ri, k_):
        return [t for ty, s, t, d in c3 if (t or "").startswith("Label #SkyyStatC%dn%d " % (ri, k_))][0]
    ifh = [i for i, r_ in enumerate(al) if r_[0] == "Fire hit"][0]
    K.check(EL.COLORS["Fire"] in cell(ifh, 1) and SOFT in cell(ifh, 0) and DIM in cell(ifh, 3), "PAGE Fire hit: Steam orange, +1 stack soft, - dim")
    K.eq(sets3.get("#SkyyStatC%dn1.Text" % ifh), "Steam", "PAGE the Steam cell text")
    iah = [i for i, r_ in enumerate(al) if r_[0] == "Air hit"][0]
    K.check(EL.COLORS["Air"] in cell(iah, 0), "PAGE Air hit: Wildfire in the Air colour")
    ifr = [i for i, r_ in enumerate(al) if r_[0] == "Your Fire"][0]
    K.check("#7ee08a" in cell(ifr, 4) and "#ff7a7a" in cell(ifr, 3) and DIM in cell(ifr, 0), "PAGE the strong / weak chart cells still +green / -red / dim")
    iim = [i for i, r_ in enumerate(al) if r_[0] == "Imbue"][0]
    K.eq(sets3.get("#SkyyStatV%d.Text" % iim), "+5 Fire", "PAGE the Imbue row set")
    n0 = len(E.sent(PS))
    kd = click(PS, stp, "trefresh")
    K.eq(len(kd), 1, "PAGE Refresh answers with exactly one packet (%s)" % kd)
    sz = sum(len(str(t or "")) + len(str(d or "")) for ty, s, t, d in c3)
    K.notes.append("PAGE the page = %d commands, ~%d characters of markup + values, %d list rows" % (len(c3), sz, len(al)))
    K.check(sz < 1500000, "PAGE the page stays far below a packet limit (~%d characters)" % sz)
    MH.clearAll()
    JV("MenuIO").stop(2000)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("el", run_el), ("live", T35.run_live)], script=__file__, live=(T35.LIVE_DIR, "Skyy_SkyyMenu"))
