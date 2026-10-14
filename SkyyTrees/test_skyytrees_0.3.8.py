"""SkyyTrees 0.3.8 - harness for the MONK + ASSASSIN NODES + REBIRTH R5 (tools/trees_0_3_8_patch.py), on top of every 0.3.7 section (kept as the
regression, now against the real SkyyClasses 0.1.23). 0.3.8 sections inside AB: AB9 the Monk / Assassin node texts + reader list + a
free A1 buy; AB10 THE REBIRTH GATE (the purchase order through buy / undo, coveredBy, the gate on at a low class level, waiting picks, the
refusal of a new paid node, the class level back, a respec, the file round trip); AB11 rebirth:part:trees at every step (bad calls,
measure, prepare + backup, status, abort, commit without a staged file, a torn / an older committed staged file, a failed write + the
retry, what the commit clears and keeps, idempotence); AB12 Dust x rebirth:fn:dustmult; AB13 the Max Up button (a rebirth upgrade placed
through the real SkyyClasses). Child JVMs
run the game's own JRE with the cached HytaleServer.jar copy on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir
in the scratch folder. The live save data is only ever READ and copied into scratch (checked afterwards).

    python SkyyTrees/test_skyytrees_0.3.7.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyyTrees-0.3.7.jar] [--prev SkyyTrees-0.3.6.jar] [--classes SkyyClasses/SkyyClasses-0.1.22.jar] [--live <Skyy_SkyyTrees>]

SECTIONS
  A   every class of both jars loads, verifies (-Xverify:all) and initialises (own class loader each)
  CC  CLASS COMPARE 0.3.6 -> 0.3.7: TreeAbilFn is the only new class; structural changes only in the classes the patch names
  JT  jar: every asset = 0.3.6's; manifest = 0.3.6's but the version
  AB  EXECUTED with the REAL SkyyClasses 0.1.22 on the skyy.bridge map (its AbilPanelFn / AbilModsFn / AbilDoFn / AbilUnlockFn) and with
      no SkyyClasses: the ability-line level gates (class:fn:abilUnlock, built-in 1 / 10 / 20 / 30), the A / M node rules (A1 without
      ROOT, M1A needs A1), tree:fn:abil (the intact csv; class trees off -> null) read back by SkyyClasses' own Abil.treeCsv, THE CLASS TAB
      render (the panel cards, slot / key / name texts, every event bound), and every panel EVENT through handleDataEvent: card details,
      modifier slot pick, equip (+ double), unequip, swap (pick + cancel), enable (buys the A node), the Ability 1 alt pick, back to the tree,
      a profile switch, the probe refusing actions
  ST  START TWICE on a scratch COPY of Skyy's live Skyy_SkyyTrees (the 0.3.4 harness's start routine): start 1 = 0.3.6's, start 2 nothing
  Z   the engine-access audit on the 0.3.7 jar: 0 refused
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.8", "0.3.7"
PKG = "com.skyy.trees."
CPKG = "com.skyy.classes."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "classes2", "tr")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyTrees-%s.jar" % PREV_VERSION)))
CL_JAR = os.path.abspath(arg("--classes", os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.23.jar")))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyTrees")))
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def t36():
    spec = importlib.util.spec_from_file_location("tt036", os.path.join(HERE, "test_skyytrees_0.3.6.py"))
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def snap(d):
    o = {}
    for r, _ds, fs in os.walk(d):
        for f in fs:
            p = os.path.join(r, f)
            o[os.path.relpath(p, d)] = open(p, "rb").read()
    return o


# ============================================================================================================ child: AB
def run_ab(out):
    import jpype
    from jpype import JClass, JArray, JBoolean, JInt, JString, JObject, JImplements, JOverride
    import skyybuild as B
    import harness_kit as HK
    HK.jvm([B.SERVER_JAR, JAR, CL_JAR], verify=True)
    R = {"checks": [], "notes": []}

    def ck(c, w):
        R["checks"].append([bool(c), w])
        if not c:
            print("FAIL", w)
    T = lambda n: JClass(PKG + n)
    C = lambda n: JClass(CPKG + n)
    Cls, Ops, Page, Store, Cfg, Data = T("TreeClass"), T("TreeClassOps"), T("TreePage"), T("TreeStore"), T("TreeCfg"), T("TreeData")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Paths, Integer, Long, Boolean = JClass("java.nio.file.Paths"), JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    UUID = JClass("java.util.UUID")
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)
    me = UUID(0x7ee5, 37)
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    bridge = Store.bridge()
    ck(bridge is not None and C("ClassCfg").bridge().equals(bridge) and System_id(bridge) == System_id(C("ClassCfg").bridge()),
       "AB0: SkyyTrees and SkyyClasses share the one skyy.bridge map")

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    LV = {"lvl": 30}
    PK = {}
    bridge.put("skill:fn:level", Fn(lambda o: Integer.valueOf(LV["lvl"])))
    bridge.put("profile:fn:key", Fn(lambda o: JString(PK.get(str(o), str(o)))))
    bridge.put("class:" + str(me), "Mage")
    bridge.put("profile:class:" + str(me), "Mage")
    # ---- the REAL SkyyClasses 0.1.22 (config defaults, scratch files)
    home = os.path.join(SCRATCH, "ab-home")
    shutil.rmtree(home, ignore_errors=True)
    os.makedirs(os.path.join(home, "classes", "players"), exist_ok=True)
    CC_ = C("ClassCfg")
    CC_.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyClasses")
    CC_.FILE = Paths.get(os.path.join(home, "classes", "config.properties"))
    R["notes"].append("SkyyClasses config: " + str(CC_.load())[:120])
    C("ClassStore").DIR = Paths.get(os.path.join(home, "classes", "players"))
    AS = C("AbilStore")
    AS.DIR = Paths.get(os.path.join(home, "classes", "abilities"))
    AS.SYNC = True
    FNS = {"class:fn:abilPanel": C("AbilPanelFn")(), "class:fn:abilMods": C("AbilModsFn")(), "class:fn:abilDo": C("AbilDoFn")(),
           "class:fn:abilUnlock": C("AbilUnlockFn")()}

    def classes(on):
        for k, v in FNS.items():
            if on:
                bridge.put(k, v)
            else:
                bridge.remove(k)
    # ---- SkyyTrees
    pdir = os.path.join(home, "trees", "players")
    os.makedirs(pdir, exist_ok=True)
    Store.DIR = Paths.get(pdir)
    Cfg.CLASS_ON = True
    NN = int(Cls.NN)
    NID = [str(x) for x in Cls.NID]
    MIX = dict((n, i) for i, n in enumerate(NID))
    ci = [str(x) for x in Cls.CLASSES].index("Mage")
    NT = int(T("TreeDefs").NT)
    bridge.put("tree:fn:abil", T("TreeAbilFn")())

    def fresh():
        Store.DATA.clear()
        Store.DIRTY.clear()
        d = Data()
        Store.DATA.put(str(me), d)
        return d

    def own(d):
        return [NID[n] for n in range(NN) if bool(d.cown[ci * NN + n])]

    def render(page):
        b, ev = UCB(), UEB()
        err = None
        try:
            page.build(None, b, ev, None)
        except Exception as e:
            err = str(e)[:300]
        texts = [str(c.text) for c in b.getCommands() if c.text is not None]
        datas = []
        for c in b.getCommands():
            if c.data is None:
                continue
            try:
                v = json.loads(str(c.data))
                datas += [str(x) for x in (v.values() if isinstance(v, dict) else [v])]
            except Exception:
                datas.append(str(c.data))
        evs = [str(e.data) for e in ev.getEvents() if e.data is not None]
        return err, texts + datas, evs

    def click(page, a):
        try:
            page.handleDataEvent(None, None, '{"a":"%s"}' % a)
            return None
        except Exception as e:
            return str(e)[:200]

    # ---------------- AB1 the ability-line level gates
    classes(False)
    ck([int(Cls.abilMin(MIX[x])) for x in ("A1", "A2", "A3", "A4")] == [1, 10, 20, 30] and int(Cls.abilMin(MIX["T1"])) == 0,
       "AB1: no SkyyClasses -> the built-in unlock levels 1 / 10 / 20 / 30 on A1-A4 (other nodes none)")
    classes(True)
    C("AbilCfg").UNLOCK_A2 = 12
    ck([int(Cls.abilMin(MIX[x])) for x in ("A1", "A2", "A3", "A4")] == [1, 12, 20, 30], "AB1: SkyyClasses' class:fn:abilUnlock rules (abil.unlock.a2 = 12)")
    C("AbilCfg").UNLOCK_A2 = 10
    ck(int(Cls.minOf(ci, MIX["A4"])) >= 30, "AB1: minOf = the higher of class.minLevel and the ability line's level")
    # ---------------- AB2 the node rules (SkyyClasses' reader list = the string its setup() puts, read from the jar)
    d = fresh()
    undo = JClass("java.util.ArrayList")()
    LV["lvl"] = 1
    r = str(Ops.buy(me, d, ci, 1, MIX["A1"], undo, False))
    ck("A1" not in own(d) and "comes with the class abilities" in r, "AB2: without SkyyClasses' reader list the A nodes wait (an older SkyyClasses): %s" % r)
    m_ = re.search(rb"Class\.Mage\.A1[ -~]*", zipfile.ZipFile(CL_JAR).read("com/skyy/classes/SkyyClassesPlugin.class"))
    reads = m_.group(0).decode() if m_ else ""
    ck(all("Class.%s.%s" % (c_, n_) in reads.split(",") for c_ in ("Mage", "Priest") for n_ in ("A1", "A2", "A3", "A4", "M1A", "M4B")),
       "AB2: SkyyClasses 0.1.22 lists Class.<Mage|Priest>.A1-A4 / M1A-M4B in tree:reads:SkyyClasses (%d keys)" % len(reads.split(",")))
    bridge.put("tree:reads:SkyyClasses", reads)
    d = fresh()
    r = str(Ops.buy(me, d, ci, 1, MIX["A1"], undo, False))
    ck("A1" in own(d) and "ROOT" not in own(d), "AB2: A1 (Meteor's line) is bought at level 1 without ROOT: %s" % r)
    r = str(Ops.buy(me, d, ci, 1, MIX["A2"], undo, False))
    ck("A2" not in own(d) and ("10" in r), "AB2: A2 waits for Sorcery 10: %s" % r)
    d2 = fresh()
    r = str(Ops.buy(me, d2, ci, 30, MIX["M1A"], undo, False))
    ck("M1A" not in own(d2), "AB2: M1A without A1 -> refused: %s" % r)
    LV["lvl"] = 30
    d = fresh()
    for n in ("A1", "A2", "M1A"):
        r = str(Ops.buy(me, d, ci, 30, MIX[n], undo, False))
    ck(own(d) == ["A1", "A2", "M1A"] or set(own(d)) == {"A1", "A2", "M1A"}, "AB2: A1, A2 then M1A bought: %s (%s)" % (own(d), r))
    # ---------------- AB3 tree:fn:abil
    csv = str(T("TreeAbilFn")().apply(me))
    ck(csv.split(",")[:3] == ["A1", "A2", "M1A"] or set(["A1", "A2", "M1A"]) <= set(x.split("=")[0] for x in csv.split(",")),
       "AB3: tree:fn:abil = the intact class nodes: %s" % csv)
    AS.TREEC.clear()
    ck(str(C("Abil").treeCsv(me)) == csv, "AB3: SkyyClasses' Abil.treeCsv reads the same text through the bridge")
    ck(list(C("Abil").runeWant(me)) == ["", ""], "AB3: (no rune items loaded in a bare JVM - the want list stays empty)")
    ck(bool(C("Abil").lineOn(csv, 0)) and bool(C("Abil").lineOn(csv, 1)) and not bool(C("Abil").lineOn(csv, 2)), "AB3: A1 / A2 enable Meteor / Mana Barrier, A3 not bought")
    Cfg.CLASS_ON = False
    ck(T("TreeAbilFn")().apply(me) is None, "AB3: class trees OFF -> null (SkyyClasses: no gate)")
    Cfg.CLASS_ON = True
    ck(T("TreeAbilFn")().apply(UUID.randomUUID()) is None and T("TreeAbilFn")().apply(JString("x")) is None, "AB3: no class / bad input -> null")
    # ---------------- AB4 THE CLASS TAB render
    AS.set(str(me), JArray(JString)(["u.Meteor", "m.Meteor.Power"]), JArray(JString)(["40", "12"]))   # Meteor Lv 3, Power+ Lv 2
    page = Page(pr, NT)
    err, texts, evs = render(page)
    alltext = " | ".join(texts)
    ck(err is None, "AB4: the class tab builds with the panel: %s" % err)
    ck("Meteor  Lv 3" in texts or [t for t in texts if t.startswith("Meteor  Lv 3")], "AB4: card 1 = Meteor Lv 3 (name text)")
    ck("Primary - Ability 2 key" in texts and "Primary - Ability 3 key" in texts, "AB4: the key texts of both primaries")
    ck([t for t in texts if t == "Empty slot 1"] and [t for t in texts if t.startswith("Tree: M1B")], "AB4: Meteor's slots: slot 1 open (M1A) + empty, slot 2 'Tree: M1B'")
    ck([t for t in texts if t.startswith("Unlocks at Sorcery 20") or t.startswith("Enable it: tree node A3")], "AB4: a later line shows how to get it")
    for e in ("trab0", "trmsa0", "trmsb1", "trsw3", "tren2"):
        ck([x for x in evs if '"%s"' % e in x or e in x], "AB4: event %s is bound" % e)
    R["notes"].append("AB4 event count %d, text count %d" % (len(evs), len(texts)))
    R["notes"].append("AB4 panel texts: %s" % [x for x in texts if len(x) < 60 and ("slot" in x or "Lv" in x or "Unlock" in x or "Enable" in x or "Tree:" in x or "+" in x)][:30])
    classes(False)
    err, texts, evs = render(page)
    ck(err is None and [t for t in texts if "show here with SkyyClasses 0.1.22" in t], "AB4: no SkyyClasses -> the page builds with the panel message")
    classes(True)
    # ---------------- AB5 the EVENTS
    page = Page(pr, NT)
    ck(click(page, "trab0") is None and bool(page.amode) and int(page.aslot) == 0, "AB5: the Meteor icon opens its detail (amode, slot 0)")
    err, texts, evs = render(page)
    ck(err is None and [t for t in texts if "Power+" in t] and [x for x in evs if "trme0" in x] and [x for x in evs if "trtree" in x] and [x for x in evs if "trmu" in x],
       "AB5: the detail lists the modifiers; equip / unequip / back-to-tree events bound: %s" % err)
    R["notes"].append("AB5 before equip: e.Meteor=%s" % AS.load(str(me)).getProperty("e.Meteor"))
    click(page, "trmsa0")
    R["notes"].append("AB5 after trmsa0: e.Meteor=%s msg=%s" % (AS.load(str(me)).getProperty("e.Meteor"), page.msg))
    click(page, "trme0")
    ck(str(page.msg) == "Done: Meteor: slot 1 Power+, slot 2 empty.", "AB5: equip Power+ in slot 1 through the page: %s" % page.msg)
    ck(str(AS.load(str(me)).getProperty("e.Meteor")) == "Power,", "AB5: ... saved in SkyyClasses' ability file")
    click(page, "trmsb0")
    click(page, "trme0")
    ck(str(page.msg).startswith("Modifier slot 2 of Meteor is not open - unlock M1B"), "AB5: slot 2 needs M1B: %s" % page.msg)
    Ops.buy(me, Store.DATA.get(str(me)), ci, 30, MIX["M1B"], JClass("java.util.ArrayList")(), False)
    click(page, "trme0")
    ck(str(page.msg) == "Done: Meteor: slot 1 Power+, slot 2 Power+.", "AB5: M1B bought -> Power+ Lv 2 DOUBLED: %s" % page.msg)
    click(page, "trmu")
    ck(str(page.msg) == "Done: Meteor: slot 1 Power+, slot 2 empty.", "AB5: unequip slot 2: %s" % page.msg)
    click(page, "trsw0")
    ck(str(page.msg).startswith("Ability: pick the card to swap Meteor with") and int(page.apend) == 0, "AB5: Swap - pick the first card")
    click(page, "trsw0")
    ck(str(page.msg) == "Ability: swap cancelled" and int(page.apend) == -1, "AB5: Swap again on the same card cancels")
    click(page, "trsw0")
    click(page, "trsw1")
    sl = [str(x) for x in AS.slots(str(me), C("ClassStore").classIndex(me))]
    ck(str(page.msg).startswith("Done: ") and sl[0] == "ManaBarrier" and sl[1] == "Meteor", "AB5: swap Meteor <-> Mana Barrier: %s %s" % (page.msg, sl))
    click(page, "trsw0")
    click(page, "trsw1")
    click(page, "tren2")
    ck("A3" in own(Store.DATA.get(str(me))) or "A3" in str(page.msg), "AB5: 'Enable' on Frost Nova's card buys A3: %s" % page.msg)
    pk0 = str(AS.pick(str(me)))
    Ops.buy(me, Store.DATA.get(str(me)), ci, 30, MIX["A4"], JClass("java.util.ArrayList")(), False)
    click(page, "tren2" if False else "tren3")
    R["notes"].append("AB5 alt card action: %s" % page.msg)
    click(page, "trtree")
    ck(not bool(page.amode), "AB5: 'Tree' goes back to the tree detail")
    # ---------------- AB6 profile switch + probe
    PK[str(me)] = str(me) + "-p2"
    AS.TREEC.clear()
    o = C("AbilPanelFn")().apply(me)
    ck(str(o[0]) == "ok" and int(o[18]) == 1, "AB6: profile 2 -> its own Meteor level (Lv 1) on the panel")
    del PK[str(me)]
    pp = Page(pr, NT)
    pp.probe = True
    pp.pci = ci
    pp.pd = Ops.probeData(ci)
    ck(str(pp.abilEv(me, pp.pd, ci, 30, "swap", 0, 0)).startswith("Ability panel actions are off in the probe"), "AB6: the probe never changes abilities")
    err, texts, evs = render(pp)
    ck(err is None, "AB6: the probe page builds: %s" % err)
    # ---------------- AB7 FIX ROUND (critics): the probe never puts its fake nodes into SkyyClasses' tree cache; the A / M nodes are free
    cached = AS.TREEC.get(me)
    real_csv = Cls.abilCsv(me)
    fake_csv = Cls.csvOf(pp.pd, Cls.intact(pp.pd, ci), ci)
    ck(cached is not None and str(cached[2]) == str(real_csv) and str(fake_csv) != str(real_csv),
       "AB7: the probe page's panel read the REAL tree (cache %s), never the probe's %s" % (None if cached is None else cached[2], str(fake_csv)[:60]))
    Props = JClass("java.util.Properties")
    pz = Props()
    for k_, v_ in (("class.nodes.Mage.A1", "true,0,1"), ("class.nodes.Mage.M1A", "true,0,1"), ("class.nodes.Mage.M1B", "true,0,2"),
                   ("class.nodes.Mage.A4", "true,0,3"), ("class.nodes.Mage.P1", "true,0,1"), ("class.nodes.Mage.ROOT", "true,0,1")):
        pz.setProperty(k_, v_)
    Cfg.apply(pz)
    capv = [int(Cfg.C_AP[ci * NN + MIX[x]]) for x in ("A1", "M1A", "M1B", "A4", "P1", "ROOT")]
    ck(capv == [0, 0, 0, 0, 1, 1], "AB7: the live file's AP numbers of the A / M lines (1 / 1 / 2 / 3) are not read - free; P1 / ROOT keep theirs: %s" % capv)
    Cfg.CLASS_ON = True
    LV["lvl"] = 1
    d = fresh()
    r1 = str(Ops.buy(me, d, ci, 1, MIX["ROOT"], undo, False))
    r2 = str(Ops.buy(me, d, ci, 1, MIX["A1"], undo, False))
    r3 = str(Ops.buy(me, d, ci, 1, MIX["M1A"], undo, False))
    r4 = str(Ops.buy(me, d, ci, 1, MIX["M1B"], undo, False))
    ck(set(own(d)) == {"ROOT", "A1", "M1A", "M1B"} and int(Cls.spent(Cls.intact(d, ci), ci)) == 1,
       "AB7: a Lv 1 Mage who spent the only AP on ROOT still enables Meteor + both its modifier slots (spent 1 AP): %s / %s" % (own(d), [r2[:50], r4[:50]]))
    AS.TREEC.clear()
    ck(str(C("Abil").treeCsv(me)).split(",")[:4] == ["ROOT", "A1", "M1A", "M1B"] or {"A1", "M1A", "M1B"} <= set(str(C("Abil").treeCsv(me)).split(",")),
       "AB7: ... and SkyyClasses sees them: %s" % C("Abil").treeCsv(me))
    ck(int(C("Abil").modSlots(C("Abil").treeCsv(me), 0)) == 2, "AB7: Meteor has its 2 modifier slots")
    # ---------------- AB8 SECOND FIX ROUND (critics): a failed tree read is "!err" (never null = no gate); A / M AP is ignored LOUDLY
    want8 = sum(1 for x_, v_ in (("A1", 1), ("M1A", 1), ("M1B", 2), ("A4", 3)) if v_ != int(Cls.NAP[MIX[x_]]))
    ck(want8 >= 1 and int(Cfg.AP_IGN) == want8, "AB8: the load counted the A / M lines whose AP an admin changed (not the old default; logged once): %d of %d" % (int(Cfg.AP_IGN), want8))
    Kit = T("TreeKit")
    w8 = Kit.checkClassNode("class.nodes.Mage[M1B]", "true|0|2")
    ck(w8 is not None and str(w8).startswith("?M1B is an ability / modifier slot node - those are always free"), "AB8: the Server Setup entry check warns: %s" % w8)
    w0 = Kit.checkClassNode("class.nodes.Mage[M1B]", "true|0|0")
    wp = Kit.checkClassNode("class.nodes.Mage[P1]", "true|0|2")
    ck((w0 is None or "always free" not in str(w0)) and (wp is None or "always free" not in str(wp)), "AB8: AP 0 on M1B / AP 2 on P1 -> no such warning: %s / %s" % (w0, wp))
    ck(str(Ops.typeLine(ci, MIX["A1"])) == "Ability line - free" and str(Ops.typeLine(ci, MIX["P1"])).endswith(" AP"),
       "AB8: the detail's type line: %s / %s" % (Ops.typeLine(ci, MIX["A1"]), Ops.typeLine(ci, MIX["P1"])))
    d = fresh()
    LV["lvl"] = 30
    for n in ("A1",):
        Ops.buy(me, d, ci, 30, MIX[n], undo, False)
    ck(str(T("TreeAbilFn")().apply(me)).split(",")[0] in ("A1", "ROOT") or "A1" in str(T("TreeAbilFn")().apply(me)), "AB8: a good tree -> its csv")
    d.bad = True
    ck(str(T("TreeAbilFn")().apply(me)) == "!err", "AB8: a BAD tree file -> '!err' (was null = every ability enabled)")
    te0 = int(C("Abil").TREE_ERR)
    AS.TREEC.clear()
    tc8 = C("Abil").treeCsv(me)
    ck(tc8 is not None and str(tc8) == "" and int(C("Abil").TREE_ERR) == te0 + 1 and not bool(C("Abil").lineOn(tc8, 0)),
       "AB8: ... SkyyClasses reads '' (closed, nothing cached) through the real bridge")
    d.bad = False
    Store.DATA.clear()
    ck(T("TreeAbilFn")().apply(me) is not None, "AB8: no data in memory -> loaded / or '!err', never null for a classed player: %s" % T("TreeAbilFn")().apply(me))
    # ================================================================================================ 0.3.8 sections
    # ---------------- AB9 the Monk + Assassin nodes (SkyyClasses 0.1.23 lists them)
    CLS_ = [str(x) for x in Cls.CLASSES]
    ci_k, ci_s = CLS_.index("Monk"), CLS_.index("Assassin")
    ck([str(Cls.name(ci_k, MIX[x])) for x in ("A1", "A2", "A3", "A4")] == ["Flowing Form", "Palm Strike", "Cyclone Kick", "Fists or Still Water"],
       "AB9: the Monk's A1-A4 name its ability lines")
    ck([str(Cls.name(ci_s, MIX[x])) for x in ("A1", "A4", "M4B")] == ["Cloak", "Vanishing Act", "Vanishing Act Mod II"], "AB9: the Assassin's (one Ability 1 alt: Vanishing Act)")
    ck("crits (x1.5)" in str(Cls.now(ci_k, MIX["PB5"])) and "deal 15% less" in str(Cls.now(ci_k, MIX["PC5"])), "AB9: the stand-in texts (Iron Fist, Serenity)")
    rd = reads.split(",")
    ck(all("Class.%s.%s" % (c_, n_) in rd for c_ in ("Monk", "Assassin") for n_ in ("A1", "A4", "M1A", "M4B", "T6")) and "Class.Monk.PB5" in rd
       and "Class.Assassin.PB4" not in rd and "Class.Monk.T3" not in rd, "AB9: SkyyClasses 0.1.23 lists the Monk / Assassin A / M nodes + the applied path nodes (Venom Blade, Vault Mastery wait)")
    bridge.put("class:" + str(me), "Monk")
    bridge.put("profile:class:" + str(me), "Monk")
    d = fresh()
    LV["lvl"] = 30
    r9 = str(Ops.buy(me, d, ci_k, 30, MIX["A1"], JClass("java.util.ArrayList")(), False))
    ck(bool(d.cown[ci_k * NN + MIX["A1"]]) and "free" in str(Ops.typeLine(ci_k, MIX["A1"])), "AB9: a Monk buys A1 (Flowing Form) for free: %s" % r9)
    r9b = str(Ops.buy(me, d, ci_k, 30, MIX["PB5"], JClass("java.util.ArrayList")(), False))
    R["notes"].append("AB9 PB5 buy at Lv 30 (path gate Lv 75): %s" % r9b)
    bridge.put("class:" + str(me), "Mage")
    bridge.put("profile:class:" + str(me), "Mage")
    # ---------------- AB10 THE REBIRTH GATE (the purchase order, AP cover, waiting picks, the buy refusal, a respec)
    TD = T("TreeDefs")
    ck(str(TD.orderEdit(None, "A1", True)) == "A1" and str(TD.orderEdit("A1,P1", "T1", True)) == "A1,P1,T1" and str(TD.orderEdit("A1,P1,T1", "P1", False)) == "A1,T1"
       and str(TD.orderEdit("A1,P1", "A1", True)) == "A1,P1" and TD.orderEdit("A1", "A1", False) is None, "AB10: orderEdit (add at the end / once, remove)")
    d = fresh()
    for n_ in ("ROOT", "P1", "T1", "T2"):
        Store.setClassOwn(d, ci, MIX[n_], True)
    ck(str(d.corder[ci]) == "ROOT,P1,T1,T2" and not bool(d.crb[ci]), "AB10: every class write keeps the purchase order (Class.Mage.order): %s" % d.corder[ci])
    Store.setClassOwn(d, ci, MIX["T1"], False)
    ck(str(d.corder[ci]) == "ROOT,P1,T2", "AB10: an Undo / take-back removes it from the order: %s" % d.corder[ci])
    own7 = JArray(JBoolean)([NID[n] in ("ROOT", "P1", "T1", "T2", "T3", "PA1", "A1") for n in range(NN)])
    ap_ = [int(Cfg.C_AP[ci * NN + MIX[x]]) for x in ("ROOT", "P1", "T1", "T2", "T3", "PA1", "A1")]
    cov = [bool(x) for x in Cls.coveredBy(own7, ci, "ROOT,P1,T1,T2,T3,PA1,A1", 3)]
    ck(cov[MIX["ROOT"]] and cov[MIX["P1"]] and cov[MIX["T1"]] and not cov[MIX["T2"]] and not cov[MIX["T3"]] and not cov[MIX["PA1"]] and cov[MIX["A1"]],
       "AB10: coveredBy - 3 AP cover ROOT + P1 + T1 (purchase order), T2 and everything bought after it wait; the free A1 always works (AP %s)" % ap_)
    cov2 = [bool(x) for x in Cls.coveredBy(own7, ci, "T3,ROOT", 3)]
    ck(cov2[MIX["T3"]] and cov2[MIX["ROOT"]] and not cov2[MIX["P1"]], "AB10: the ORDER decides (T3 bought first takes 2 of the 3 AP)")
    ck([bool(x) for x in Cls.coveredBy(own7, ci, None, 100)] == [bool(x) for x in own7], "AB10: enough AP -> every pick")
    d = fresh()
    LV["lvl"] = 30
    for n_ in ("ROOT", "P1", "A1"):
        Ops.buy(me, d, ci, 30, MIX[n_], JClass("java.util.ArrayList")(), False)
    ck(str(d.corder[ci]) == "ROOT,P1,A1", "AB10: the buys recorded in order: %s" % d.corder[ci])
    d.uid = me
    d.crb[ci] = True
    LV["lvl"] = 0
    it = [bool(x) for x in Cls.intact(d, ci)]
    ck(it[MIX["A1"]] and not it[MIX["P1"]], "AB10: the gate on (after a rebirth) at class level 0 (no AP): the free A node works, P1 waits (ROOT %s)" % it[MIX["ROOT"]])
    ck(int(Cls.waiting(d, ci)) >= 1, "AB10: waiting() counts the paid picks that wait (%d)" % int(Cls.waiting(d, ci)))
    rb_ = str(Ops.buy(me, d, ci, 0, MIX["X1"], JClass("java.util.ArrayList")(), False))
    ck("come back first" in rb_ and not bool(d.cown[ci * NN + MIX["X1"]]), "AB10: a NEW paid node waits while kept picks wait: %s" % rb_)
    LV["lvl"] = 60
    it2 = [bool(x) for x in Cls.intact(d, ci)]
    ck(it2[MIX["ROOT"]] and it2[MIX["P1"]] and int(Cls.waiting(d, ci)) == 0, "AB10: the class level back -> every kept pick works again")
    Store.clearClass(d, ci, JClass("java.lang.System").currentTimeMillis())
    ck(d.corder[ci] is None and not bool(d.crb[ci]), "AB10: a class respec frees everything (no order, no gate): %s" % d.corder[ci])
    # the file round trip: Class.Mage.order / .rb / rb.lastTx
    d = fresh()
    Ops.buy(me, d, ci, 60, MIX["ROOT"], JClass("java.util.ArrayList")(), False)
    d.crb[ci] = True
    d.rbTx = "tx1760000000000-cccccc"
    sp_ = Store.snap(str(me))
    ck(str(sp_.getProperty("Class.Mage.order")) == "ROOT" and str(sp_.getProperty("Class.Mage.rb")) == "1" and str(sp_.getProperty("rb.lastTx")) == "tx1760000000000-cccccc",
       "AB10: snap writes Class.Mage.order, Class.Mage.rb, rb.lastTx")
    Store.saveNow(str(me))
    Store.DATA.clear()
    d2 = Store.readFile(str(me))
    ck(str(d2.corder[ci]) == "ROOT" and bool(d2.crb[ci]) and str(d2.rbTx) == "tx1760000000000-cccccc" and d2.cextra.size() == 0, "AB10: readFile reads them back (no unknown line)")
    # ---------------- AB11 REBIRTH R5: rebirth:part:trees (measure / prepare / commit / done / abort / status, crashes)
    Store.DATA.clear()
    if os.path.isfile(os.path.join(pdir, str(me) + ".properties")):
        os.remove(os.path.join(pdir, str(me) + ".properties"))
    d = Store.data(me)
    TREES_ = [str(x) for x in TD.TREES]
    t_min, t_exp = TREES_.index("Mining"), TREES_.index("Exploration")
    d.lv[t_min * 12 + 0] = 3
    d.lv[t_min * 12 + 1] = 2
    d.off[t_min * 12 + 1] = True
    d.lv[t_exp * 12 + 0] = 4
    d.credit[t_min] = 777
    for n_ in ("ROOT", "P1"):
        Ops.buy(me, d, ci, 60, MIX[n_], JClass("java.util.ArrayList")(), False)
    Store.saveNow(str(me))
    RB = T("TreeRb")()
    Arr = lambda *a: JArray(JObject)([JString(x) for x in a])
    k = str(me)
    TX1, TX2 = "tx1760000000000-aaaaaa", "tx1760000000001-bbbbbb"
    ck(str(RB.apply(Arr("measure", "nope", TX1))) == "err:bad profile key" and str(RB.apply(Arr("measure", k, "x"))) == "err:bad txid"
       and str(RB.apply(Arr("zap", k, TX1))) == "err:unknown op zap" and str(RB.apply(JObject(None))) == "err:bad arguments", "AB11: bad calls answer err")
    ck(str(RB.apply(Arr("measure", k, TX1))) == "ok:nodes=2;classPicks=2", "AB11: measure - 2 skill nodes to clear (Exploration not counted), 2 class picks")
    fpath = os.path.join(pdir, k + ".properties")
    b0 = open(fpath, "rb").read()
    ck(str(RB.apply(Arr("prepare", k, TX1))) == "ok:nodes=2;classPicks=2", "AB11: prepare")
    stg = os.path.join(home, "trees", "rebirth", k + ".rb-" + TX1 + ".properties")
    ck(os.path.isfile(stg) and open(fpath, "rb").read() == b0 and os.path.isfile(os.path.join(home, "trees", "rebirth-backup", k, TX1, k + ".properties")),
       "AB11: a staged file + a backup copy, the live file untouched")
    ck(str(RB.apply(Arr("status", k, TX1))) == "staged" and str(RB.apply(Arr("abort", k, TX1))) == "done" and not os.path.isfile(stg)
       and str(RB.apply(Arr("status", k, TX1))) == "none", "AB11: status staged; abort deletes it (a crash before DECIDED changes nothing)")
    ck(str(RB.apply(Arr("commit", k, TX1))).startswith("err:no staged file"), "AB11: commit without a staged file -> err")
    RB.apply(Arr("prepare", k, TX1))
    open(os.path.join(home, "trees", "rebirth", k + ".rb-" + TX2 + ".properties.tmp"), "w").write("x")
    RB.apply(Arr("prepare", k, TX1))
    ck(not os.path.isfile(os.path.join(home, "trees", "rebirth", k + ".rb-" + TX2 + ".properties.tmp")), "AB11: a torn older staged file is cleaned")
    bridge.put("rebirth:fn:decision", Fn(lambda o: JString("commit")))
    open(os.path.join(home, "trees", "rebirth", k + ".rb-" + TX2 + ".properties"), "w").write("tx=" + TX2)
    ck(str(RB.apply(Arr("prepare", k, TX1))).startswith("err:an older rebirth"), "AB11: an older COMMITTED rebirth still finishing -> refused")
    os.remove(os.path.join(home, "trees", "rebirth", k + ".rb-" + TX2 + ".properties"))
    bridge.remove("rebirth:fn:decision")
    T("TreeRb").FAIL_WRITE = 1
    c1 = str(RB.apply(Arr("commit", k, TX1)))
    ck(c1.startswith("err:could not save") and str(Store.data(me).rbTx) == TX1, "AB11: a failed write -> err (applied in memory, retried)")
    c2 = str(RB.apply(Arr("commit", k, TX1)))
    ft = open(fpath, encoding="latin-1").read()
    ck(c2 == "done" and "rb.lastTx=" + TX1 in ft, "AB11: the retry -> done, rb.lastTx on disk (a crash after DECIDED rolls forward)")
    d = Store.data(me)
    ck(int(d.lv[t_min * 12 + 0]) == 0 and int(d.lv[t_min * 12 + 1]) == 0 and not bool(d.off[t_min * 12 + 1]) and int(d.credit[t_min]) == 0,
       "AB11: the skill trees are cleared (nodes, off flags, the Dust credit - no refund)")
    ck(int(d.lv[t_exp * 12 + 0]) == 4, "AB11: Exploration keeps its nodes (Rebirth-Spec U5)")
    ck(bool(d.cown[ci * NN + MIX["ROOT"]]) and bool(d.crb[ci]) and str(d.corder[ci]) == "ROOT,P1" and "Class.Mage.order=ROOT,P1" in ft and "Class.Mage.rb=1" in ft,
       "AB11: the class picks are KEPT in purchase order with the rebirth gate on")
    ck(str(RB.apply(Arr("commit", k, TX1))) == "done" and str(RB.apply(Arr("status", k, TX1))) == "committed" and str(RB.apply(Arr("abort", k, TX1))) == "err:already committed"
       and str(RB.apply(Arr("prepare", k, TX1))) == "err:already committed", "AB11: idempotent; abort / prepare after the commit refused")
    ck(bridge.get("rebirth:part:trees") is None, "AB11: (the plugin puts rebirth:part:trees at setup - not in this bare JVM)")
    # ---------------- AB12 Dust x rebirth:fn:dustmult
    CALC = T("TreeCalc")
    CALC.DMULT.clear()
    bal0 = list(CALC.balance(me, d, t_min, 10))
    bridge.put("rebirth:fn:dustmult", Fn(lambda o: JClass("java.lang.Double").valueOf(2.0)))
    CALC.DMULT.clear()
    bal1 = list(CALC.balance(me, d, t_min, 10))
    ck(abs(float(CALC.dustMult(me, t_min)) - 2.0) < 1e-9 and int(bal1[2]) >= 2 * int(bal0[2]) - 1, "AB12: Dust x 2 after the first rebirth: %s -> %s" % (bal0[2], bal1[2]))
    bridge.put("rebirth:fn:dustmult", Fn(lambda o: JClass("java.lang.Double").valueOf(500.0)))
    CALC.DMULT.clear()
    ck(float(CALC.dustMult(me, t_min)) == 1.0, "AB12: an answer out of range (500) -> 1")
    bridge.remove("rebirth:fn:dustmult")
    CALC.DMULT.clear()
    ck(float(CALC.dustMult(me, t_min)) == 1.0, "AB12: no SkyyRebirth -> 1")
    # ---------------- AB13 the Max Up button (a rebirth upgrade to place)
    d = fresh()
    LV["lvl"] = 30
    for n_ in ("A1", "M1A"):
        Ops.buy(me, d, ci, 30, MIX[n_], JClass("java.util.ArrayList")(), False)
    AS.set(str(me), JArray(JString)(["rb.pick.Meteor", "u.Meteor"]), JArray(JString)(["1", "40"]))
    AS.TREEC.clear()
    page = Page(pr, NT)
    click(page, "trab0")
    err, texts, evs = render(page)
    ck(err is None and [t for t in texts if t == "Rebirth: 1 upgrade - press Max Up"] and [x for x in evs if "trmx0" in x] and not [x for x in evs if "trme0" in x],
       "AB13: one upgrade to place -> every modifier row shows Max Up (trmx<k>), Equip waits: %s" % err)
    click(page, "trmx0")
    ck(str(page.msg).startswith("Done: Power+ of Meteor can now reach modifier Lv 6"), "AB13: Max Up places it on Power+ through SkyyClasses: %s" % page.msg)
    ck(AS.load(str(me)).getProperty("rb.pick.Meteor") is None and str(AS.load(str(me)).getProperty("rb.modmax.Meteor.Power")) == "1", "AB13: ... saved (rb.modmax.Meteor.Power=1)")
    err, texts, evs = render(page)
    ck(err is None and not [x for x in evs if "trmx" in x], "AB13: nothing left to place -> the normal buttons again")
    # ---------------- AB14 FIX ROUND (critics 2026-10-14): one check per fix
    AL = JClass("java.util.ArrayList")
    Dbl = JClass("java.lang.Double")
    # A1 a rebirth-gated class tree: the respec price follows the OWNED picks (it was 0 / the low level after a rebirth)
    d = fresh()
    d.uid = me
    for n_ in ("ROOT", "P1", "T1"):
        Ops.buy(me, d, ci, 60, MIX[n_], AL(), False)
    d.cfree[ci] = False
    p60 = int(Ops.priceOf(d, ci, 60, False))
    ck(p60 > 0 and p60 == int(Cls.respecPrice(60)), "AB14 A1: before a rebirth a Mage respec at Lv 60 costs %d" % p60)
    d.crb[ci] = True
    LV["lvl"] = 1
    so_ = int(Cls.spent(Cls.intactOf(Cls.ownOf(d, ci), ci), ci))
    L_ = int(Cls.rbPriceLvl(d, ci, 1))
    p1 = int(Ops.priceOf(d, ci, 1, False))
    ck(so_ > 0 and p1 > 0 and int(Cls.ap(L_)) >= so_ and (L_ == 1 or int(Cls.ap(L_ - 1)) < so_) and p1 == int(Cls.respecPrice(L_)),
       "AB14 A1: after a rebirth at class level 1 the respec costs the level the kept picks need (Lv %d = %d coins; 0.3.8 before the fix: 0)" % (L_, p1))
    ck((" %d x " % L_) in str(Ops.armText(ci, 1, False, False, p1)), "AB14 A1: the confirm text names that level: %s" % Ops.armText(ci, 1, False, False, p1))
    LV["lvl"] = 60
    ck(int(Ops.priceOf(d, ci, 60, False)) == p60, "AB14 A1: ... at the old class level the old price")
    # A3 the Dust multiplier: the last answer is kept when SkyyRebirth goes silent; a negative Dust balance respecs free only on a real answer
    CALC.DMULT.clear()
    CALC.DLAST.clear()
    bridge.put("rebirth:fn:dustmult", Fn(lambda o: Dbl.valueOf(2.0)))
    ck(abs(float(CALC.dustMult(me, t_min)) - 2.0) < 1e-9 and bool(CALC.dustKnown(me, t_min)), "AB14 A3: SkyyRebirth answers x2 (known)")
    bridge.remove("rebirth:fn:dustmult")
    CALC.DMULT.clear()
    ck(abs(float(CALC.dustMult(me, t_min)) - 2.0) < 1e-9 and not bool(CALC.dustKnown(me, t_min)), "AB14 A3: SkyyRebirth gone -> the last answer x2 stays (not x1), marked unknown")
    bridge.put("rebirth:fn:dustmult", Fn(lambda o: None))
    CALC.DMULT.clear()
    ck(abs(float(CALC.dustMult(me, t_min)) - 2.0) < 1e-9 and not bool(CALC.dustKnown(me, t_min)), "AB14 A3: ... answering null the same")
    bridge.remove("rebirth:fn:dustmult")
    CALC.DMULT.clear()
    CALC.DLAST.clear()
    TO = T("TreeOps")
    d = fresh()
    d.uid = me
    d.rbTx = "tx1760000000009-dddddd"
    bal, pick_ = [0, 0, 0, 0], None
    for lv_ in (1, 2, 3, 5, 8, 10, 15, 20, 30, 45, 60):   # a level + one node level with the tokens fine and the Dust negative
        LV["lvl"] = lv_
        for s_ in range(12):
            for v_ in range(1, 6):
                for j_ in range(12):
                    d.lv[t_min * 12 + j_] = 0
                d.lv[t_min * 12 + s_] = v_
                b_ = [int(x) for x in CALC.balance(me, d, t_min, int(CALC.level(me, t_min)))]
                if b_[0] >= b_[1] and b_[2] < b_[3]:
                    bal, pick_ = b_, (lv_, s_, v_)
                    break
            if pick_:
                break
        if pick_:
            break
    R["notes"].append("AB14 A3 setup (level, slot, node level): %s balance %s" % (pick_, bal))
    ck(bal[2] < bal[3], "AB14 A3 setup: a negative Dust balance on a rebirthed profile: %s" % bal)
    TAKES = []
    coins0 = bridge.get("coins:fn:take")
    bridge.put("coins:fn:take", Fn(lambda o: (TAKES.append(1), JClass("java.lang.Boolean").valueOf(False))[1]))
    d.respecAt[t_min] = JClass("java.lang.System").currentTimeMillis()   # respecced a moment ago (the cooldown runs; respec.coins default 0)
    r_no = str(TO.respec(pr, t_min))
    ck(r_no.startswith("You can respec Mining again in") and pick_ is not None and int(d.lv[t_min * 12 + pick_[1]]) == pick_[2], "AB14 A3: no dustmult answer -> NO free respec (the cooldown / coins apply): %s" % r_no)
    bridge.put("rebirth:fn:dustmult", Fn(lambda o: Dbl.valueOf(1.0)))
    CALC.DMULT.clear()
    r_yes = str(TO.respec(pr, t_min))
    if coins0 is None:
        bridge.remove("coins:fn:take")
    else:
        bridge.put("coins:fn:take", coins0)
    ck(r_yes.startswith("Respec done"), "AB14 A3: ... SkyyRebirth answers -> the negative balance respecs free as before: %s" % r_yes)
    bridge.remove("rebirth:fn:dustmult")
    CALC.DMULT.clear()
    LV["lvl"] = 60
    # A4 the rebirth backup holds the IN-MEMORY state (an unsaved change is in it)
    d = fresh()
    d.uid = me
    Ops.buy(me, d, ci, 60, MIX["ROOT"], AL(), False)
    Store.saveNow(k)
    d.credit[t_min] = 4242
    TX3 = "tx1760000000003-eeeeee"
    ck(str(RB.apply(Arr("prepare", k, TX3))).startswith("ok:"), "AB14 A4: prepare")
    bk_ = open(os.path.join(home, "trees", "rebirth-backup", k, TX3, k + ".properties"), encoding="latin-1").read()
    ck("4242" in bk_ and "4242" not in open(fpath, encoding="latin-1").read(), "AB14 A4: the backup has the unsaved Dust credit (memory), the live file not yet")
    RB.apply(Arr("abort", k, TX3))
    # C4 the noabil text
    gsrc = open(os.path.join(HERE, "build_skyytrees_%s.py" % VERSION), encoding="utf8").read()
    ck("the Mage and the Priest have theirs first" not in gsrc and "the Mage, Priest, Monk and Assassin have theirs" in gsrc, "AB14 C4: the no-abilities text names all four classes")
    # ---------------- AB15 FIX ROUND 2
    # A1 class level 0 right after a rebirth: the gated price is not skipped by the lvl < 1 return
    d = fresh()
    d.uid = me
    for n_ in ("ROOT", "P1", "T1"):
        Ops.buy(me, d, ci, 60, MIX[n_], AL(), False)
    d.cfree[ci] = False
    ck(int(Ops.priceOf(d, ci, 0, False)) == 0, "AB15 A1: no rebirth gate, class level 0 -> 0 as in 0.3.7")
    d.crb[ci] = True
    LV["lvl"] = 0
    L0_ = int(Cls.rbPriceLvl(d, ci, 0))
    p0_ = int(Ops.priceOf(d, ci, 0, False))
    ck(L0_ >= 1 and p0_ > 0 and p0_ == int(Cls.respecPrice(L0_)) and not bool(Ops.negBalance(d, ci, 0)),
       "AB15 A1: after a rebirth at class level 0 the respec costs Lv %d = %d coins (was free), not a negative balance" % (L0_, p0_))
    ck((" %d x " % L0_) in str(Ops.armText(ci, 0, False, False, p0_)) and "free" not in str(Ops.armText(ci, 0, False, False, p0_)), "AB15 A1: the confirm text names that level: %s" % Ops.armText(ci, 0, False, False, p0_))
    TAKES2 = []
    coins1 = bridge.get("coins:fn:take")
    bridge.put("coins:fn:take", Fn(lambda o: (TAKES2.append(int(o[1])), JClass("java.lang.Boolean").valueOf(False))[1]))
    d.crespecAt[ci] = 0
    r0_ = str(Ops.respec(me, d, ci, 0, False))
    if coins1 is None:
        bridge.remove("coins:fn:take")
    else:
        bridge.put("coins:fn:take", coins1)
    ck(r0_.endswith("you do not have enough") and TAKES2 == [p0_] and bool(d.cown[ci * int(Cls.NN) + MIX["ROOT"]]),
       "AB15 A1: ... the respec asks SkyyCoins for that price, no coins -> nothing cleared: %s" % r0_)
    # A2 kept picks above the AP cap (an admin lowered class.ap.max): priced at the cap level, never ~5000 levels up
    apmax0 = int(Cfg.AP_MAX)
    Cfg.AP_MAX = 1
    Lc_ = int(Cls.rbPriceLvl(d, ci, 0))
    Lc5_ = int(Cls.rbPriceLvl(d, ci, 5))
    Cfg.AP_MAX = apmax0
    ck(Lc_ <= 3 and Lc5_ == 5, "AB15 A2: picks above the cap -> the cap level (Lv %d at level 0, Lv %d at level 5; before: level + 5000)" % (Lc_, Lc5_))
    LV["lvl"] = 60
    # B1 Max Up only on an UNLOCKED modifier (the ability at Lv 1 = every modifier locked)
    d = fresh()
    LV["lvl"] = 30
    for n_ in ("A1", "M1A"):
        Ops.buy(me, d, ci, 30, MIX[n_], AL(), False)
    AS.set(str(me), JArray(JString)(["rb.pick.Meteor", "u.Meteor"]), JArray(JString)(["1", "0"]))
    AS.TREEC.clear()
    page = Page(pr, NT)
    click(page, "trab0")
    err, texts, evs = render(page)
    ck(err is None and [t for t in texts if t == "Rebirth: 1 upgrade - press Max Up"] and not [x for x in evs if "trmx" in x],
       "AB15 B1: Meteor Lv 1 (every modifier locked) -> no Max Up button anywhere: %s" % err)
    AS.set(str(me), JArray(JString)(["u.Meteor"]), JArray(JString)(["40"]))
    err, texts, evs = render(page)
    ck(err is None and [x for x in evs if "trmx0" in x], "AB15 B1: ... once Power+ unlocks its Max Up comes back")
    AS.set(str(me), JArray(JString)(["rb.pick.Meteor"]), JArray(JString)(["0"]))
    LV["lvl"] = 30
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


def System_id(o):
    from jpype import JClass
    return int(JClass("java.lang.System").identityHashCode(o))


# ============================================================================================================ parent
def main():
    if "--ab" in sys.argv:
        return run_ab(arg("--out"))
    T = t36()
    if "--load" in sys.argv:
        return T.run_load(arg("--load"), arg("--out"))
    if "--cc" in sys.argv:
        return T.sk().run_cc(arg("--cc"), arg("--prevjar"), arg("--out"), arg("--repl"))
    if "--st" in sys.argv:
        return T.t34().run_start(arg("--st"), arg("--fake"), arg("--live"), arg("--out"), arg("--tag"))
    if "--mkfake" in sys.argv:
        T.t34().t33().H.run_mkfake(arg("--mkfake"))
        return
    if "--audit" in sys.argv:
        H = T.t34().t33().H
        H.SCRATCH = SCRATCH
        H.run_audit(arg("--audit"), arg("--fake"), arg("--out"))
        return
    for j in (JAR, PREV_JAR, CL_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
    if not os.path.realpath(SCRATCH).startswith(sroot + os.sep):
        sys.exit("--dir must be inside tools/dev/scratch/ (deleted afterwards): %s" % SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_before = snap(LIVE)
    me = os.path.abspath(__file__)

    def child(args_, out_):
        with open(out_ + ".log", "wb") as lf:
            subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        if not os.path.isfile(out_):
            print(open(out_ + ".log", encoding="utf8", errors="replace").read()[-3000:])
            return None
        return json.load(open(out_))
    try:
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            r = child(["--load", j], os.path.join(SCRATCH, "load-%s.json" % tag)) or {}
            check(r and not r.get("load_fails") and r.get("classes", 0) >= 30,
                  "A (%s): %s classes load, verify (-Xverify:all), initialise %s" % (tag, r.get("classes"), r.get("load_fails", [])[:3]))
        rules = [[r"storage\.ChunkGrid\.", "storage.ChunkStore."]]
        cc = child(["--cc", JAR, "--prevjar", PREV_JAR, "--repl", json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules})],
                   os.path.join(SCRATCH, "cc.json"))
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            KIT = {"CfgFn", "CfgRows", "CfgPub", "CfgKit", "CfgHist", "CfgImp", "CfgText"}
            check([a.split(".")[-1] for a in cc["added"]] == ["TreeRb"] and not cc["gone"], "CC: TreeRb is the only new class: %s %s" % (cc["added"], cc["gone"]))
            gone = dict((c, v["fields_gone"]) for c, v in cls_.items() if v["fields_gone"])
            check(not gone, "CC: no field removed: %s" % gone)
            struct = dict((c, sorted(m.split("(")[0] for m in v["structural"])) for c, v in cls_.items() if v["structural"] and c not in KIT)
            print("CC. 0.3.7 -> 0.3.8 structural: %s" % struct)
            print("CC. new fields: %s" % dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"]))
            allowed = {"TreeClass", "TreePage", "TreeStore", "SkyyTreesPlugin", "TreeClassOps", "TreeData", "TreeDefs", "TreeCalc",
                       "TreeOps"}   # 0.3.8 (fix round: TreeOps.respec - no free respec off a missing Dust multiplier)
            # second fix round: the A / M lines' default AP is 0 now, so the lines the old one-time migrations APPEND (TreeMig ADD_LINE,
            # TreeMig33 ADD_LINE = CLASS_LINES) carry 0 too - their static data only, never their code
            for mc_ in ("TreeMig", "TreeMig33"):
                if mc_ in struct:
                    check(struct[mc_] == ["<clinit>"], "CC: %s changed in its static lines only: %s" % (mc_, struct[mc_]))
                    allowed |= {mc_}
            check(set(struct) <= allowed, "CC: structural changes only in %s: %s" % (sorted(allowed), sorted(set(struct) - allowed)))
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        np_ = set(n for n in zp.namelist() if not n.endswith(".class"))
        diff = sorted(n for n in (nn | np_) if n != "manifest.json" and (n not in nn or n not in np_ or zj.read(n) != zp.read(n)))
        check(not diff, "JT: every asset = 0.3.7's: %s" % diff[:5])
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mp, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.7's but the version")
        ab = child(["--ab"], os.path.join(SCRATCH, "ab.json"))
        check(ab is not None, "AB ran")
        if ab:
            for n in ab.get("notes", []):
                print("AB. " + n)
            for ok, what in ab.get("checks", []):
                check(ok, what)
            print("AB. %d executed checks" % len(ab.get("checks", [])))
            check(len(ab.get("checks", [])) >= 40, "AB: every scenario ran (%d checks)" % len(ab.get("checks", [])))
        fake = os.path.join(SCRATCH, "fake")
        subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sts = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            sts[tag] = child(["--st", j, "--fake", fake, "--live", LIVE, "--tag", tag], os.path.join(SCRATCH, "st-%s.json" % tag))
            check(sts[tag] is not None and len(sts[tag].get("starts", [])) == 2, "ST (%s): two starts ran" % tag)
        if sts.get("new") and sts.get("prev"):
            T34 = T.t34()
            nz = lambda r: T34.norm_start(r).replace(VERSION, "0.3.X").replace(PREV_VERSION, "0.3.X")
            sn, sp = sts["new"]["starts"], sts["prev"]["starts"]
            check(nz(sn[0]) == nz(sp[0]), "ST: start 1 of 0.3.8 = 0.3.7's: %s / %s" % (sn[0]["changed"], sp[0]["changed"]))
            check(sn[1]["changed"] == [] and sn[1]["sum"] == sn[0]["sum"], "ST: start 2 changes nothing and reads the same: %s" % sn[1]["changed"])
            print("ST. start twice on the live copy: start 1 changed %s (same as 0.3.7), start 2 nothing" % sn[0]["changed"])
        au = child(["--audit", JAR, "--fake", fake], os.path.join(SCRATCH, "audit.json"))
        check(au is not None, "Z: the audit child ran")
        if au:
            check(not au.get("refused") and au.get("refs", 0) > 2000, "Z: engine-access audit: %s references, 0 refused: %s" % (au.get("refs"), str(au.get("refused"))[:400]))
            check(len(au.get("control") or []) >= 1, "Z: the audit's control is refused")
            print("Z. %s references, %d refused" % (au.get("refs"), len(au.get("refused") or [])))
        check(snap(LIVE) == live_before, "the live Skyy_SkyyTrees folder was never written (only read + copied)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyTrees %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
