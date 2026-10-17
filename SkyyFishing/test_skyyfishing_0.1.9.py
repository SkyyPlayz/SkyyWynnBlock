"""Harness for SkyyFishing 0.1.9 (MENU PATTERN sweep S4: the Fishing Bench stays a pattern-3.6 window - one 32 px tab row, rule 7 row
tiers, empty states, Sell all = click twice; tools/fishing_0_1_9_patch.py).
Build first: python tools/fishing_0_1_9_patch.py && python SkyyFishing/build_skyyfishing_0.1.9.py

    python SkyyFishing/test_skyyfishing_0.1.9.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  A / C / AA  verify (-Xverify:all), class compare 0.1.8 -> 0.1.9 (exactly the planned members), engine-access audit
  PAGE18 / PAGE19  THE REAL WINDOW on each jar (one child JVM each, the same script): FishPage (a stand-in subclass records rebuild /
      close) on a real SimpleItemContainer (a stand-in Item store), FishCfg + FishStore on scratch, a coins:fn:add stand-in. The same
      clicks on both jars (craft the Wooden rod, pick it, fit + remove a hook, sell, fillet a Rare fish (asks first), sell all, close):
      after EVERY click the info line, the whole inventory (slot, item, count, metadata) and every coin payment must be IDENTICAL on
      0.1.8 and 0.1.9 (0.1.9's sell all needs the second click - the armed click changes nothing); every tab's bindings (selector +
      action, the token blanked) identical too.
      0.1.9 only, on the commands FishPage.build really sends (each tab, small + long lists): check_page, assert_proven, the window
      fits 1600 x 980 and its body fits, ONE tab row (#SkyyFbTabs, 32 px buttons, the active one the only Primary), no pager, no back /
      < Menu text (inline or b.set), every b.set / binding names an element that exists; rule 7: 1 rod / 2 fish = the 112 px rows,
      a long fish list = 56 px rows; the empty states; Sell all: armed label + info, a second click sells, another click / 5 s disarm.
  R / X / Q / ST  the 0.1.7 harness's phases on this jar (reel, exec, quest, live = start twice on a scratch COPY of the live
      Skyy_SkyyFishing) - no behaviour change there
Not testable without the game (UNVERIFIED): how the 112 px rows / 64 px icons look in the client; the small tab buttons' look.
Scratch: tools/dev/scratch/menuS4/fishing/h019 (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

VERSION = "0.1.9"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS4", "fishing", "h019")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyFishing-%s.jar" % VERSION)]
_spec = importlib.util.spec_from_file_location("test_skyyfishing_0_1_7", os.path.join(HERE, "test_skyyfishing_0.1.7.py"))
T17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T17)
T15 = T17.T15
_hs = importlib.util.spec_from_file_location("hub_tab_harness", os.path.join(ROOT, "tools", "hub_tab_harness.py"))
H = importlib.util.module_from_spec(_hs)
_hs.loader.exec_module(H)
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyFishing-0.1.8.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.fishing."
EXPECT = {
    "FishPage": ["+f allUntil", "+f RHS", "+m growSize", "~c ", "~<clinit>", "~m build", "~m handleDataEvent"],
    # the version text (as in every round): the config header, the export line, the /fishadmin stats line, the ready line
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "FishCmds": ["~m admin"], "SkyyFishingPlugin": ["~m setup"],
    "FishCfg": ["~m applyAll", "~m seed"],
}
ADDED = []
T17.WAIVE = T17.WAIVE + (
    ("C: non-class entries changed", "only manifest.json changes in 0.1.9 - the built-in compare checks it"),
)
U1S = "00000000-0000-4000-8000-0000000000f9"


def _api(W):
    from jpype import JImplements, JOverride

    @JImplements(PKG + "FishApi")
    class Api(object):
        @JOverride
        def eye(self, c): return None
        @JOverride
        def feet(self, c): return None
        @JOverride
        def heldSlot(self, c): return 0
        @JOverride
        def held(self, c): return None
        @JOverride
        def clicked(self, c): return False
        @JOverride
        def block(self, c, x, y, z): return -1
        @JOverride
        def getReel(self, c): return 0
        @JOverride
        def setReel(self, c, v): pass
        @JOverride
        def spawnBobber(self, c, s): pass
        @JOverride
        def moveBobber(self, c, s, x, y, z): pass
        @JOverride
        def tagBobber(self, c, s, t): pass
        @JOverride
        def removeBobber(self, s): pass
        @JOverride
        def particle(self, c, i, x, y, z): pass
        @JOverride
        def drawLine(self, c, pts, n, secs): pass
        @JOverride
        def sound(self, c, i, x, y, z): pass
        @JOverride
        def hudState(self, c, s, state, txt): pass
        @JOverride
        def hudSet(self, c, s, bar, t, cps): pass
        @JOverride
        def hudHide(self, c, s): pass
        @JOverride
        def tell(self, c, text, col): pass
        @JOverride
        def inv(self, c): return W["inv"]
        @JOverride
        def later(self, c, r): pass
        @JOverride
        def fresh(self, c): return c
        @JOverride
        def now(self): return W["t"]
    return Api()


def fake_page_class():
    """a FishPage subclass whose rebuild() builds into fresh real builders (the engine's sends packets) and close() is counted"""
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(True)
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR_NOW[0])
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    fp = cp.makeClass(PKG + "FishPageT")
    fp.setSuperclass(cp.get(PKG + "FishPage"))
    for decl in ("public int rebuilds;", "public int closes;", "public com.hypixel.hytale.server.core.ui.builder.UICommandBuilder lastB;",
                 "public com.hypixel.hytale.server.core.ui.builder.UIEventBuilder lastEv;"):
        fp.addField(CtField.make(decl, fp))
    fp.addConstructor(CtNewConstructor.make("public FishPageT(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr); }", fp))
    fp.addMethod(CtNewMethod.make("""public void rebuild() {
  this.rebuilds = this.rebuilds + 1;
  this.lastB = new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder();
  this.lastEv = new com.hypixel.hytale.server.core.ui.builder.UIEventBuilder();
  build(null, this.lastB, this.lastEv, null);
}""", fp))
    fp.addMethod(CtNewMethod.make("public void close() { this.closes = this.closes + 1; }", fp))
    fp.toClass(JClass(PKG + "FishPage").class_)
    return JClass(PKG + "FishPageT")


JAR_NOW = [None]


def player_ref(u):
    from jpype import JClass
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    try:
        return PRc(None, u, "Skyy", "en-US", None, None)
    except Exception:
        pass
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    o = uf.get(None).allocateInstance(PRc.class_)
    for f in PRc.class_.getDeclaredFields():
        t = str(f.getType().getName())
        n = str(f.getName()).lower()
        if JClass("java.lang.reflect.Modifier").isStatic(f.getModifiers()):
            continue
        f.setAccessible(True)
        if t == "java.util.UUID":
            f.set(o, u)
        elif t == "java.lang.String" and "name" in n:
            f.set(o, "Skyy")
        elif t == "java.lang.String" and "lang" in n:
            f.set(o, "en-US")
    return o


def run_page(out, jar_unused, scratch, _home, which):
    """one jar's real window: the click trace (compared by PAGE19) + on 0.1.9 the window checks"""
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    jar = OLD_JAR if which == "0.1.8" else JAR
    JAR_NOW[0] = jar
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Defs, Cfg, Store, Eng, Rig, Bench, Brg, Pg = P("FishDefs"), P("FishCfg"), P("FishStore"), P("FishEng"), P("FishRig"), P("FishBench"), P("FishBridge"), P("FishPage")
    IS, SIC, SH = JClass("com.hypixel.hytale.server.core.inventory.ItemStack"), JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"), JClass("java.lang.Short")
    UUID, Paths, Long = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long")
    # the stand-in Item store: every item id FishDefs names (+ a filler)
    ids = set(["Rock_Stone"])
    Mod = JClass("java.lang.reflect.Modifier")
    for f in Defs.class_.getDeclaredFields():
        if not Mod.isStatic(f.getModifiers()):
            continue
        f.setAccessible(True)
        v = f.get(None)
        vals = [v] if isinstance(v, str) else (list(v) if v is not None and str(f.getType().getName()) == "[Ljava.lang.String;" else [])
        for x in vals:
            if x is not None and re.match(r"\A[A-Z][A-Za-z]+_[A-Za-z0-9_]+\Z", str(x)):
                ids.add(str(x))
    T15.item_store(sorted(ids))
    mods = os.path.join(scratch, "mods-" + which)
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    Store.start(Paths.get(mods))
    br = Brg.bridge()
    coins = []

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            coins.append(int(o[1]))
            return Long(1000 + sum(coins))
    br.put("coins:fn:add", Coins())
    u = UUID.fromString(U1S)
    W = {"inv": SIC(SH(36).shortValue()), "t": 1000000}
    Eng.API = _api(W)
    inv = W["inv"]
    inv.addItemStack(IS("Ingredient_Stick", 6))
    inv.addItemStack(IS("Ingredient_Fibre", 7))
    inv.addItemStack(IS("SkyyFishing_Hook_Barbed_I", 2))
    sp = [str(x) for x in Defs.SP_KEY]
    rar = [int(x) for x in Defs.SP_RAR]
    common = [i for i in range(len(sp)) if rar[i] == 0]
    rare = [i for i in range(len(sp)) if rar[i] >= int(Cfg.FIL_CONFIRM_R)]
    inv.addItemStack(Rig.makeFish(common[0], 2000, 450, "Skyy"))
    inv.addItemStack(Rig.makeFish(common[1 % len(common)], 2600, 500, "Skyy"))
    inv.addItemStack(Rig.makeFish(rare[0], 8000, 1100, "Skyy"))

    def snap():
        o = []
        for s_ in range(int(inv.getCapacity())):
            st = inv.getItemStack(SH(s_).shortValue())
            if st is None or st.isEmpty():
                continue
            m = st.getMetadata()
            o.append([s_, str(st.getItemId()), int(st.getQuantity()), None if m is None else str(m.toJson())])
        return o
    FPT = fake_page_class()
    pr = player_ref(u)
    pg = FPT(pr)
    trace = []

    def bindings():
        evs = H.events_of(pg.lastEv)
        tok = str(pg.tok)
        return sorted("%s %s" % (s, re.sub(r"\b%s\b" % re.escape(tok), "TOK", " ".join(re.findall(r'\{"a": [^{}]*\}', t)))) for s, t in evs)

    def click(a, i=None, tok=True, rec=True):
        d = {"a": a}
        if i is not None:
            d["i"] = str(i)
        if tok:
            d["t"] = str(pg.tok)
        pg.handleDataEvent(None, None, json.dumps(d))
        r = str(pg.info)
        if rec:
            trace.append({"click": [a, i], "info": r, "inv": snap(), "coins": list(coins), "tab": int(pg.tab), "closes": int(pg.closes),
                          "bind": bindings() if pg.lastEv is not None else []})
        return r
    pg.rebuild()
    K.check(int(pg.rebuilds) == 1, "%s PAGE: the window builds (tab 0)" % which)
    trace.append({"click": ["open", None], "info": str(pg.info), "inv": snap(), "coins": [], "tab": 0, "closes": 0, "bind": bindings()})
    win = []                              # (what, cmds, evs, page) for the 0.1.9 window checks

    def keep(what):
        win.append((what, H.cmds_of(pg.lastB), H.events_of(pg.lastEv), str(pg.info)))
    keep("Parts")
    r = click("craft", 0)
    K.check(r.startswith("+Crafted the Wooden Fishing Rod"), "%s PAGE: craft the Wooden rod: %s" % (which, r))
    click("tab", 1, tok=False)
    keep("Rig, one rod")
    click("rod", 0)
    pids = [str(x) for x in pg.partIds]
    j = pids.index("SkyyFishing_Hook_Barbed_I") if "SkyyFishing_Hook_Barbed_I" in pids else 99
    r = click("fit", j)
    K.check(r.startswith("+Fitted"), "%s PAGE: fit the Barbed Hook I: %s" % (which, r))
    r = click("rm", 1)
    K.check(r.startswith("+Took off"), "%s PAGE: take the hook off: %s" % (which, r))
    click("tab", 2, tok=False)
    keep("Fillet and Sell, 3 fish")
    r = click("sell", 0)
    K.check(r.startswith("+Sold"), "%s PAGE: sell one fish: %s" % (which, r))
    fsl = [int(x) for x in pg.fishSlots]
    rr = [n_ for n_, sl in enumerate(fsl) if int(Defs.fishIndex(inv.getItemStack(SH(sl).shortValue()).getItemId())) == rare[0]]
    r = click("fil", rr[0])
    K.check(r.startswith("=Fillet the"), "%s PAGE: filleting a Rare fish asks first: %s" % (which, r))
    r = click("fil", rr[0])
    K.check(r.startswith("+Filleted"), "%s PAGE: the second Fillet click fillets it: %s" % (which, r))
    keep("Fillet and Sell, 1 fish")
    # sell all: 0.1.8 = one click, 0.1.9 = two (the first arms it: nothing changes)
    n_coins, inv0 = len(coins), snap()
    if which == "0.1.9":
        r = click("sellall", rec=False)
        K.check(r.startswith("=Sell every Normal fish") and snap() == inv0 and len(coins) == n_coins and int(pg.allUntil) > 0,
                "0.1.9 SELLALL: the first click arms it - nothing sold: %s" % r)
        keep("Sell all armed")
        click("tab", 2, tok=False, rec=False)
        K.check(int(pg.allUntil) == 0, "0.1.9 SELLALL: another click disarms it")
        keep("Sell all disarmed")
        r = click("sellall", rec=False)
        K.check(r.startswith("=Sell every") and snap() == inv0, "0.1.9 SELLALL: after a disarm the next click arms again (nothing sold)")
        pg.allUntil = int(JClass("java.lang.System").currentTimeMillis()) - 1
        r = click("sellall", rec=False)
        K.check(r.startswith("=Sell every") and snap() == inv0 and len(coins) == n_coins, "0.1.9 SELLALL: 5 s later the click arms again (nothing sold)")
    r = click("sellall")
    K.check(r.startswith("+Sold") and len(coins) > n_coins, "%s PAGE: sell all Normal sells: %s (%s)" % (which, r, coins[n_coins:]))
    keep("Fillet and Sell, empty")
    # a long fish list (rule 7: the normal rows) and an empty rod list
    for n_ in range(14):
        inv.addItemStack(Rig.makeFish(common[0], 1500 + 10 * n_, 400 + n_, "Skyy"))
    pg.rebuild()
    keep("Fillet and Sell, 14 fish")
    click("tab", 0, tok=False)
    click("tab", 1, tok=False)
    rs = int(Bench.firstSlot(inv, "SkyyFishing_Rod_Bamboo"))
    if rs >= 0:
        inv.removeItemStackFromSlot(SH(rs).shortValue(), jpype.JInt(1))
    click("tab", 1, tok=False)
    keep("Rig, no rod")
    click("close", tok=False)
    K.check(int(pg.closes) == 1, "%s PAGE: Close closes the window" % which)
    json.dump(trace, open(os.path.join(scratch, "trace-%s.json" % which), "w"), indent=0)
    K.notes.append("%s: %d clicks traced, %d coin payments %s" % (which, len(trace), len(coins), coins))
    if which == "0.1.9":
        window_checks(K, win, [int(x) for x in Pg.RHS])
        old = json.load(open(os.path.join(scratch, "trace-0.1.8.json")))
        K.eq(len(trace), len(old), "PAGE19: the same clicks as on 0.1.8")
        for a_, b_ in zip(old, trace):
            what = "%s %s" % tuple(a_["click"])
            K.eq(b_["info"], a_["info"], "SAME %s: the info line" % what)
            K.check(b_["inv"] == a_["inv"], "SAME %s: the whole inventory (slot, item, count, metadata) = 0.1.8's" % what)
            K.eq(b_["coins"], a_["coins"], "SAME %s: the coin payments" % what)
            K.eq([b_["tab"], b_["closes"]], [a_["tab"], a_["closes"]], "SAME %s: the tab / close" % what)
            K.eq(b_["bind"], a_["bind"], "SAME %s: every button binding (selector + action)" % what)
    Store.stopIO()
    K.save()


def window_checks(K, win, hs):
    """0.1.9: the commands FishPage.build really sent, per view"""
    K.eq(hs, [56, 81, 112], "rule 7: the row tiers (FishPage.RHS)")
    for what, cmds, evs, info in win:
        apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
        sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
        K.check(len(apps) > 5 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets" % (what, len(apps), len(sets)))

        def unq(d):
            try:
                v = json.loads(d)
            except Exception:
                return str(d)
            if isinstance(v, dict) and len(v) == 1:
                v = list(v.values())[0]
            return v if isinstance(v, str) else str(d)
        sv = [(s, unq(d)) for s, d in sets]
        try:
            SUI.check_page(apps, "SkyyFb")
            K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
        except Exception as e:
            K.check(False, "%s: check_page: %s" % (what, e))
        try:
            # the Rig total lines (#SkyyFbSt0-2, propValue: WrapMaxLines 1 = the kit's 'base' gate) are 0.1.1's, unchanged and live since
            # 0.1.1 - every OTHER element must be proven
            SUI.assert_proven([mk for p, mk in apps if not mk.startswith("Label #SkyyFbSt")], what=what)
            K.check(True, "%s: assert_proven" % what)
        except Exception as e:
            K.check(False, "%s: assert_proven: %s %s" % (what, e, [mk[:200] for p, mk in apps if "MaxLines" in mk]))
        m = re.match(r"Group #SkyyFb \{ Anchor: \(Width: (\d+), Height: (\d+)\); \}", apps[0][1])
        K.check(apps[0][0] is None and m and int(m.group(1)) <= SUI.MAX_PAGE_W and int(m.group(2)) <= SUI.MAX_PAGE_H,
                "%s: the window root fits 1600 x 980 (%s)" % (what, apps[0][1][:60]))
        K.check(any("#SkyyFbBar " in mk and 'Text: "Fishing Bench"' in mk for p, mk in apps), "%s: the title names the bench" % what)
        body_h = SUI.used_height(apps, "SkyyFbBody")
        K.check(body_h <= 760 - 38 - 2 * 17, "%s: the body fits the window (%d px of %d)" % (what, body_h, 760 - 38 - 34))
        decl = [(x.group(1), x.group(2)) for p, mk in apps for x in H.DECL_RE.finditer(mk)]
        rows = [i for t_, i in decl if t_ == "Group" and (i.endswith("Tabs") or i.endswith("Sub"))]
        K.eq(rows, ["SkyyFbTabs"], "%s: ONE tab row" % what)
        tabs = [mk for p, mk in apps if p == "SkyyFbTabs" and mk.startswith("TextButton")]
        K.check(len(tabs) == 3 and all("Height: 32)" in mk for mk in tabs), "%s: 3 tabs, 32 px high (the sub-tab style)" % what)
        prim = [mk for p, mk in apps for v in [mk] if "Common/Buttons/Primary.png" in mk.split("Hovered:")[0]]
        K.check(len(prim) == 1 and prim[0] in tabs, "%s: one Primary in the view = the active tab" % what)
        texts = [x.group(3) for p, mk in apps for x in SUI._TEXT_ELEM_RE.finditer(mk)] + [v for s, v in sv if s.endswith(".Text")]
        bad = [t for t in texts if SUI.MENU_BACK_RE.match(t) or SUI.MENU_PAGER_RE.match(t)]
        K.check(not bad and "Close" in texts, "%s: no back / < Menu / pager text (%d texts; the Close button kept): %s" % (what, len(texts), bad))
        ids = set(i for t_, i in decl)
        bs = [s for s, _t in evs if s]
        miss = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
        K.check(not miss, "%s: every b.set and binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), miss[:4]))
        rowh = lambda pre: sorted(set(int(mm.group(1)) for p, mk in apps if p in ("SkyyFbList", "SkyyFbRods") and re.match(r"Group #%s\d+ " % pre, mk)
                                      for mm in [re.search(r"Height: (\d+)", mk)] if mm))
        if what == "Parts":
            K.eq(rowh("SkyyFbR"), [56], "Parts: 25 recipes = the normal 56 px rows (they scroll)")
        if what == "Rig, one rod":
            K.eq(rowh("SkyyFbD"), [112], "Rig: one rod = the 112 px row (rule 7)")
        if what == "Fillet and Sell, 3 fish":
            K.eq(rowh("SkyyFbF"), [112], "Fillet and Sell: 3 fish = the 112 px rows (rule 7)")
            fil = [mk for p, mk in apps if re.match(r"TextButton #SkyyFbF\d+Fil ", mk)]
            K.check(len(fil) == 3 and all(re.search(r"Height: 112\b", mk) for mk in fil), "Fillet and Sell: the Fillet buttons grow with their rows")
        if what == "Fillet and Sell, 14 fish":
            K.eq(rowh("SkyyFbF"), [56], "Fillet and Sell: 14 fish = the normal 56 px rows (they scroll)")
        if what == "Fillet and Sell, empty":
            K.check(any(s == "#SkyyFbNoFish.Text" and "no whole fish" in v for s, v in sv) and any(
                "#SkyyFbNoFish " in mk and "Center" in mk for p, mk in apps), "Fillet and Sell: the empty state (centred, b.set)")
        if what == "Rig, no rod":
            K.check(any(s == "#SkyyFbNoRod.Text" and "no fishing rod" in v for s, v in sv), "Rig: no rod = the empty state")
        allb = [mk for p, mk in apps if mk.startswith("TextButton #SkyyFbAll ")]
        if what == "Sell all armed":
            K.check(len(allb) == 1 and 'Text: "Click again to sell all"' in allb[0] and any(s == "#SkyyFbStatus.Text" for s, v in sv),
                    "SELLALL: armed = the button says Click again to sell all")
        if what in ("Sell all disarmed", "Fillet and Sell, 3 fish"):
            K.check(len(allb) == 1 and 'Text: "Sell all Normal"' in allb[0], "%s: the button says Sell all Normal" % what)


def run_page18(out, jar, scratch, home):
    run_page(out, jar, scratch, home, "0.1.8")


def run_page19(out, jar, scratch, home):
    run_page(out, jar, scratch, home, "0.1.9")


if __name__ == "__main__":
    HK.run(name="SkyyFishing", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("page18", run_page18), ("page19", run_page19), ("reel", T17.run_reel), ("exec", T15.run_exec), ("quest", T15.run_quest),
                   ("live", T15.run_live)], script=__file__, live=(T15.LIVE_DIR, "Skyy_SkyyFishing"))
