"""SkyyTrees 0.3.10 - harness for THE SPELLBLADE TREE + THE REBIRTH MODIFIER SLOTS + THE FISHING TREE + THE FARMING AVERAGE
(tools/trees_0_3_10_patch.py), on top of every 0.3.9 section (kept as the regression, now against the real SkyyClasses 0.1.25). 0.3.10
sections inside AB: AB17 the Spellblade's node names / readers (SkyyClasses 0.1.25 lists the K nodes; the SkyyArmory + later ones stay
waiting), free A1 / M1A buys, the REAL panel for a Spellblade, slots 3 + 4 from rebirths 5 / 10 (Next slot, the closed-slot text, equip
into slot 3, the card's "+2"), the Imbue element row (Change -> class:fn:abilDo attune); AB18 the Fishing tree (tree 8: its tab, every
catch node "coming" until SkyyFishing lists it, Sea Legs buyable, Fishing Wisdom -> skill:bonus xp.fishing once SkyySkills lists it,
tree:fn:bonus Fishing.*); AB19 the Farming average (skill:farmavg:<uuid> = the Farming tree's level; OFF / absent = the Farming level).
=== 0.3.9 harness notes (kept) ===
SkyyTrees 0.3.9 - harness for the WARRIOR + BERSERKER + ARCHER NODES (tools/trees_0_3_9_patch.py), on top of every 0.3.7 / 0.3.8 section
(kept as the regression, now against the real SkyyClasses 0.1.24). 0.3.9 section inside AB: AB16 the three classes' node names, the stand-in
texts, the reader list (applied path nodes listed, the waiting ones not), free A1 + M1A buys for each class, the REAL SkyyClasses panel on a
Warrior's class tab, tree:fn:abil read back by SkyyClasses, the no-abilities line. Child JVMs run the game's own JRE with the cached
HytaleServer.jar copy on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder. The live save
data is only ever READ and copied into scratch (checked afterwards).

    python SkyyTrees/test_skyytrees_0.3.9.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyyTrees-0.3.9.jar] [--prev SkyyTrees-0.3.8.jar] [--classes SkyyClasses/SkyyClasses-0.1.24.jar] [--live <Skyy_SkyyTrees>]

SECTIONS (the 0.3.8 harness's, see test_skyytrees_0.3.8.py): A load + verify both jars; CC class compare 0.3.8 -> 0.3.9 (no class added,
structural changes only in the classes the patch names); JT assets + manifest; AB executed with the real SkyyClasses 0.1.24 (AB1-AB16);
ST start twice on a scratch copy of the live Skyy_SkyyTrees; Z the engine-access audit.
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.10", "0.3.9"
PKG = "com.skyy.trees."
CPKG = "com.skyy.classes."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "classes4fix", "tr")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyTrees-%s.jar" % PREV_VERSION)))
CL_JAR = os.path.abspath(arg("--classes", os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.25.jar")))
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
    ck("the Mage and the Priest have theirs first" not in gsrc, "AB14 C4: the no-abilities text no longer says only the Mage and the Priest (0.3.9: it names no class)")
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
    # ================================================================================================ 0.3.9 sections
    # ---------------- AB16 the Warrior + Berserker + Archer nodes (SkyyClasses 0.1.24 lists them) - every class has ability lines now
    CLS_ = [str(x) for x in Cls.CLASSES]
    ci_w, ci_b, ci_a = CLS_.index("Warrior"), CLS_.index("Berserker"), CLS_.index("Archer")
    ck([str(Cls.name(ci_w, MIX[x])) for x in ("A1", "A2", "A3", "A4", "M2B")] == ["Rallying Guard", "Shield Shockwave", "Iron Chain", "Challenge or Oath", "Shield Shockwave Mod II"],
       "AB16: the Warrior's A1-A4 name its ability lines (+ a modifier slot): %s" % [str(Cls.name(ci_w, MIX[x])) for x in ("A1", "A2", "A3", "A4", "M2B")])
    ck([str(Cls.name(ci_b, MIX[x])) for x in ("A1", "A2", "A3", "A4")] == ["Enrage", "Whirlwind", "Earthsplitter", "Frenzy or Banner"]
       and [str(Cls.name(ci_a, MIX[x])) for x in ("A1", "A2", "A3", "A4")] == ["Pinning Shot", "Rapid Fire", "Explosive Arrow", "Rain or Net"],
       "AB16: the Berserker's and the Archer's")
    ck("x1.5" in str(Cls.now(ci_a, MIX["PB3"])) and "+15% damage" in str(Cls.now(ci_a, MIX["PA5"])), "AB16: the stand-in texts (Deadeye x1.5, Grand Trapper from everyone): %s / %s"
       % (Cls.now(ci_a, MIX["PB3"]), Cls.now(ci_a, MIX["PA5"])))
    m24 = re.search(rb"Class\.Mage\.A1[ -~]*", zipfile.ZipFile(CL_JAR).read("com/skyy/classes/SkyyClassesPlugin.class"))
    rd24 = (m24.group(0).decode() if m24 else "").split(",")
    ck(all("Class.%s.%s" % (c_, n_) in rd24 for c_ in ("Warrior", "Berserker", "Archer") for n_ in ("A1", "A2", "A3", "A4", "M1A", "M4B"))
       and all(x_ in rd24 for x_ in ("Class.Warrior.T1", "Class.Warrior.PB4", "Class.Berserker.T4", "Class.Berserker.PC4", "Class.Archer.PA1", "Class.Archer.PC5")),
       "AB16: SkyyClasses 0.1.24 lists the three classes' A / M nodes + the path nodes it applies (%d keys)" % len(rd24))
    ck(not [x_ for x_ in ("Class.Warrior.PA3", "Class.Warrior.PA4", "Class.Warrior.PC2", "Class.Berserker.PA2", "Class.Archer.T1", "Class.Berserker.PB1") if x_ in rd24],
       "AB16: the waiting nodes stay unlisted (Guardian's Oath node / Bastion / Last Stand / Shared Fury - Skyy's calls; other mods' nodes)")
    bridge.put("tree:reads:SkyyClasses", ",".join(rd24))
    for cname, ci_ in (("Warrior", ci_w), ("Berserker", ci_b), ("Archer", ci_a)):
        bridge.put("class:" + str(me), cname)
        bridge.put("profile:class:" + str(me), cname)
        d = fresh()
        LV["lvl"] = 30
        r16 = str(Ops.buy(me, d, ci_, 30, MIX["A1"], AL(), False))
        ck(bool(d.cown[ci_ * NN + MIX["A1"]]) and "free" in str(Ops.typeLine(ci_, MIX["A1"])), "AB16: a %s buys A1 for free: %s" % (cname, r16))
        r16b = str(Ops.buy(me, d, ci_, 30, MIX["M1A"], AL(), False))
        ck(bool(d.cown[ci_ * NN + MIX["M1A"]]), "AB16: ... and its first modifier slot: %s" % r16b)
    bridge.put("class:" + str(me), "Warrior")
    bridge.put("profile:class:" + str(me), "Warrior")
    d = fresh()
    for n_ in ("A1", "A2", "M1A"):
        Ops.buy(me, d, ci_w, 30, MIX[n_], AL(), False)
    AS.TREEC.clear()
    page = Page(pr, NT)
    err, texts, evs = render(page)
    ck(err is None and [t for t in texts if t.startswith("Rallying Guard")] and "Primary - Ability 2 key" in texts and [x for x in evs if "trab0" in x],
       "AB16: the class tab builds the REAL SkyyClasses panel for a Warrior (Rallying Guard card, keys, events): %s" % err)
    csv16 = str(T("TreeAbilFn")().apply(me))
    ck(set(["A1", "A2", "M1A"]) <= set(x.split("=")[0] for x in csv16.split(",")), "AB16: tree:fn:abil for the Warrior: %s" % csv16)
    AS.TREEC.clear()
    ck(bool(C("Abil").lineOn(csv16, C("AbilDefs").find("RallyingGuard"))) and not bool(C("Abil").lineOn(csv16, C("AbilDefs").find("IronChain"))),
       "AB16: SkyyClasses reads it: Rallying Guard's line on, Iron Chain's (A3) not bought")
    gsrc9 = open(os.path.join(HERE, "build_skyytrees_%s.py" % VERSION), encoding="utf8").read()
    ck("abilities come in a later build.\";" in gsrc9 and "Monk and Assassin have theirs" not in gsrc9, "AB16: the no-abilities line names no classes (all have abilities)")
    bridge.put("class:" + str(me), "Mage")
    bridge.put("profile:class:" + str(me), "Mage")
    LV["lvl"] = 30
    # ================================================================================================ 0.3.10 sections
    import re as re10
    AS.TREEC.clear()

    def evn(evs_, pre):
        o_ = []
        for x_ in evs_:
            for m_ in re10.finditer(r'"(%s[0-9a-z]*)"' % pre, x_):
                o_.append(m_.group(1))
        return o_
    # ---------------- AB17 the Spellblade: nodes, readers, buys, the panel, slots 3 + 4, the Imbue element
    CLS_ = [str(x) for x in Cls.CLASSES]
    ck(CLS_[-1] == "Spellblade" and len(CLS_) == 8, "AB17: the Spellblade is class 8 of the class tree: %s" % CLS_)
    ci_s = CLS_.index("Spellblade")
    ck(str(Cls.CICON[CLS_.index("Monk")]) == "Weapon_Staff_Bo_Wood" and str(Cls.CICON[ci_s]) == "Weapon_Longsword_Iron",
       "AB17 fix: CICON - the Monk keeps the Bo staff, the Spellblade gets the longsword: %s" % [str(x) for x in Cls.CICON])
    ck([str(Cls.name(ci_s, MIX[x])) for x in ("A1", "A2", "A3", "A4", "M3B")] == ["Arcane Breach", "Elemental Imbue", "Sunder", "Rift or Shatter", "Sunder Mod II"],
       "AB17: A1-A4 name the Spellblade's lines: %s" % [str(Cls.name(ci_s, MIX[x])) for x in ("A1", "A2", "A3", "A4", "M3B")])
    ck([str(Cls.name(ci_s, MIX[x])) for x in ("T4", "T5", "T6", "PA1", "PB4", "PC5")] == ["Second Wind", "Keen Edge", "Tempo", "Twin Attunement", "Marked for Death", "Vanguard"],
       "AB17: trunk + path node names")
    ck("-5%" in str(Cls.now(ci_s, MIX["T6"])) or "5%" in str(Cls.now(ci_s, MIX["T6"])), "AB17: Tempo shows its live amount: %s" % Cls.now(ci_s, MIX["T6"]))
    m25 = re.search(rb"Class\.Mage\.A1[ -~]*", zipfile.ZipFile(CL_JAR).read("com/skyy/classes/SkyyClassesPlugin.class"))
    rd25 = (m25.group(0).decode() if m25 else "").split(",")
    SB_K = ["T4", "T5", "T6", "PA1", "PA2", "PA5", "PB1", "PB2", "PB4", "PC3", "PC5"]
    ck(all("Class.Spellblade." + n_ in rd25 for n_ in ["A1", "A2", "A3", "A4", "M1A", "M4B"] + SB_K),
       "AB17: SkyyClasses 0.1.25 lists the Spellblade's A / M nodes + the 11 K nodes (%d keys)" % len(rd25))
    ck(not [x_ for x_ in ("T1", "T2", "T3", "PA3", "PA4", "PB3", "PB5", "PC1", "PC2", "PC4") if "Class.Spellblade." + x_ in rd25],
       "AB17: the SkyyArmory / later nodes are not listed (they wait)")
    bridge.put("tree:reads:SkyyClasses", ",".join(rd25))
    ck(not bool(Cls.coming(ci_s, MIX["T4"])) and bool(Cls.coming(ci_s, MIX["T1"])) and bool(Cls.coming(ci_s, MIX["PA3"])),
       "AB17: Second Wind applied (SkyyClasses), Long Arm waits for SkyyArmory, Reaction for a later build")
    ck(int(Cls.minOf(ci_s, MIX["T1"])) >= 5 and int(Cls.minOf(ci_s, MIX["PA5"])) >= 75, "AB17: the template's class level gates (T1 5, PA5 75): %d / %d"
       % (int(Cls.minOf(ci_s, MIX["T1"])), int(Cls.minOf(ci_s, MIX["PA5"]))))
    R["notes"].append("AB17 TreeCfg.HAS310 (defaults, no file) = %s" % bool(Cfg.HAS310))
    bridge.put("class:" + str(me), "Spellblade")
    bridge.put("profile:class:" + str(me), "Spellblade")
    # fix round: the test path for a Spellblade at class level 0 (no Battlemagic row yet) - Server Setup unlock levels 0 -> A1-A4 + slots buyable
    ACf = C("AbilCfg")
    u17 = [ACf.UNLOCK_A1, ACf.UNLOCK_A2, ACf.UNLOCK_A2X, ACf.UNLOCK_A1X]
    ACf.UNLOCK_A1 = 0
    ACf.UNLOCK_A2 = 0
    ACf.UNLOCK_A2X = 0
    ACf.UNLOCK_A1X = 0
    LV["lvl"] = 0
    d0 = fresh()
    r17z = [str(Ops.buy(me, d0, ci_s, 0, MIX[n_], AL(), False)) for n_ in ("A1", "A2", "A3", "A4", "M1A", "M1B", "M2A", "M4A")]
    ck(all(bool(d0.cown[ci_s * NN + MIX[n_]]) for n_ in ("A1", "A2", "A3", "A4", "M1A", "M1B", "M2A", "M4A")),
       "AB17 fix: class level 0 + unlock levels 0 -> a Spellblade buys A1-A4 and modifier slots: %s" % r17z)
    ck(bool(C("AbilDefs").owns(C("AbilDefs").find("Sunder"), 0, False, "A")), "AB17 fix: SkyyClasses owns Sunder at class level 0 with unlock levels 0")
    # fix round 2 (critic): the in-game route to Burning Rift (PA2) at class level 0 - Test: extra AP + the chain's Class level per node = 0
    ch2 = []
    n2 = MIX["PA2"]
    while n2 >= 0:
        ch2.insert(0, n2)
        n2 = int(Cls.NPAR1[n2])
    xap0 = Cfg.C_EXTRA_AP
    min0 = [int(Cfg.C_MIN[ci_s * NN + n_]) for n_ in ch2]
    Cfg.C_EXTRA_AP = 50
    for n_ in ch2:
        Cfg.C_MIN[ci_s * NN + n_] = 0
    r2x = [(NID[n_], str(Ops.buy(me, d0, ci_s, 0, n_, AL(), False))) for n_ in ch2 if not bool(d0.cown[ci_s * NN + n_]) and not bool(Cls.coming(ci_s, n_))]
    ck(bool(d0.cown[ci_s * NN + MIX["PA2"]]) and bool(Cls.intactOf(JArray(JBoolean)([bool(d0.cown[ci_s * NN + n_]) for n_ in range(NN)]), ci_s)[MIX["PA2"]]),
       "AB17 fix 2: class level 0 + Test: extra AP 50 + the chain's class levels 0 -> Burning Rift (PA2) bought past the waiting T1: %s" % r2x)
    R["notes"].append("AB17 fix 2: the Burning Rift chain %s (bought %s; coming skipped %s)"
                      % ([NID[n_] for n_ in ch2], [x_[0] for x_ in r2x], [NID[n_] for n_ in ch2 if bool(Cls.coming(ci_s, n_))]))
    for i_, n_ in enumerate(ch2):
        Cfg.C_MIN[ci_s * NN + n_] = min0[i_]
    Cfg.C_EXTRA_AP = xap0
    ACf.UNLOCK_A1, ACf.UNLOCK_A2, ACf.UNLOCK_A2X, ACf.UNLOCK_A1X = u17
    LV["lvl"] = 30
    d = fresh()
    r17 = [str(Ops.buy(me, d, ci_s, 30, MIX[n_], AL(), False)) for n_ in ("A1", "A2", "M1A", "M1B", "M2A")]
    ck(all(bool(d.cown[ci_s * NN + MIX[n_]]) for n_ in ("A1", "A2", "M1A", "M1B", "M2A")), "AB17: a Spellblade buys A1, A2 and three modifier slots free: %s" % r17)
    LV["lvl"] = 30
    csv17 = str(T("TreeAbilFn")().apply(me))
    AS.TREEC.clear()
    ck(bool(C("Abil").lineOn(csv17, C("AbilDefs").find("ArcaneBreach"))) and bool(C("Abil").lineOn(csv17, C("AbilDefs").find("ElementalImbue")))
       and not bool(C("Abil").lineOn(csv17, C("AbilDefs").find("Sunder"))), "AB17: SkyyClasses reads tree:fn:abil: Breach + Imbue on, Sunder not bought (%s)" % csv17)
    AS.set(str(me), JArray(JString)(["u.ArcaneBreach", "u.ElementalImbue"]), JArray(JString)(["40", "40"]))
    RBN17 = {"n": 0}
    bridge.put("rebirth:fn:count", Fn(lambda o: Integer.valueOf(RBN17["n"])))
    AS.RBN.clear()
    page = Page(pr, NT)
    err, texts, evs = render(page)
    ck(err is None and [t for t in texts if t.startswith("Arcane Breach")] and [t for t in texts if t.startswith("Elemental Imbue")],
       "AB17: the class tab builds the REAL panel for a Spellblade (Breach + Imbue cards): %s" % err)
    ck(not [t for t in texts if t.endswith(" +1") or t.endswith(" +2")], "AB17: no rebirths -> no '+N' on the cards")
    click(page, "trab0")
    err, texts, evs = render(page)
    ck(err is None and [t for t in texts if t.startswith("Modifier slot 1 of 2")] and "trtree" in evn(evs, "tr") and "trmnx" not in evn(evs, "tr"),
       "AB17: no rebirths: Breach's detail = slot 1 of 2, the button = Tree node: %s %s" % (err, [t for t in texts if t.startswith("Modifier slot")]))
    RBN17["n"] = 10
    AS.RBN.clear()
    page = Page(pr, NT)
    err, texts, evs = render(page)
    ck(err is None and [t for t in texts if t.endswith(" +2")], "AB17: rebirth 10 -> Breach's slot-2 text says +2: %s" % [t for t in texts if "slot" in t.lower() or "+2" in t][:6])
    click(page, "trab0")
    err, texts, evs = render(page)
    ck(err is None and [t for t in texts if t.startswith("Modifier slot 1 of 4")] and "trmnx" in evn(evs, "tr"),
       "AB17: rebirth 10: slot 1 of 4, the button = Next slot (trmnx): %s" % [t for t in texts if t.startswith("Modifier slot")])
    ck([t for t in texts if "Rebirth: +2 slots." in t], "AB17: the how-text names the rebirth slots")
    click(page, "trmnx")
    click(page, "trmnx")
    ck(int(page.mslot) == 2, "AB17: Next slot twice -> slot 3 (%d)" % int(page.mslot))
    err, texts, evs = render(page)
    ck(err is None and [t for t in texts if t.startswith("Modifier slot 3 of 4 - empty")], "AB17: slot 3 shown empty: %s" % [t for t in texts if t.startswith("Modifier slot")])
    eq17 = [x_ for x_ in evn(evs, "trme") if x_[4:].isdigit()]
    ck(len(eq17) >= 1, "AB17: slot 3 has Equip buttons: %s" % eq17)
    if eq17:
        click(page, eq17[0])
        msg17 = str(page.msg)
        err, texts, evs = render(page)
        ck([t for t in texts if t.startswith("Modifier slot 3 of 4 - now ")], "AB17: equip into slot 3 (rebirth slot): %s / %s" % (msg17, [t for t in texts if t.startswith("Modifier slot")]))
        R["notes"].append("AB17 slot 3 equip: %s" % msg17)
    RBN17["n"] = 5
    AS.RBN.clear()
    click(page, "trmnx")
    err, texts, evs = render(page)
    ck(int(page.mslot) == 3 and [t for t in texts if t.startswith("Modifier slot 4 - opens at rebirth 10")], "AB17: rebirth 5: slot 4 says it opens at rebirth 10: %s"
       % [t for t in texts if t.startswith("Modifier slot")])
    ev17, mx17 = ACf.RB_SLOT_EVERY, ACf.RB_SLOT_MAX
    ACf.RB_SLOT_EVERY = 3
    RBN17["n"] = 3
    AS.RBN.clear()
    err, texts, evs = render(page)
    ck(int(page.mslot) == 3 and [t for t in texts if t.startswith("Modifier slot 4 - opens at rebirth 6")], "AB17 fix: rb.modSlotEvery 3 -> slot 4 opens at rebirth 6: %s"
       % [t for t in texts if t.startswith("Modifier slot")])
    ACf.RB_SLOT_MAX = 1
    AS.RBN.clear()
    err, texts, evs = render(page)
    ck([t for t in texts if t.startswith("Modifier slot 4 - no more slots")], "AB17 fix: rb.modSlotMax 1 -> slot 4 says no more slots: %s"
       % [t for t in texts if t.startswith("Modifier slot")])
    ACf.RB_SLOT_EVERY, ACf.RB_SLOT_MAX = ev17, mx17
    RBN17["n"] = 5
    AS.RBN.clear()
    click(page, "trmnx")
    ck(int(page.mslot) == 0, "AB17: Next slot wraps to slot 1")
    # the Imbue element row
    RBN17["n"] = 0
    AS.RBN.clear()
    page = Page(pr, NT)
    click(page, "trab1")
    err, texts, evs = render(page)
    el0 = [t for t in texts if t.startswith("Element: ")]
    ck(err is None and el0 and el0[0].startswith("Element: Fire") and "trmat" in evn(evs, "tr"),
       "AB17: Elemental Imbue's detail: 'Element: Fire' + Change: %s %s" % (err, el0))
    click(page, "trmat")
    msg_ = str(page.msg)
    err, texts, evs = render(page)
    el1 = [t for t in texts if t.startswith("Element: ")]
    ck(el1 and not el1[0].startswith("Element: Fire") and not msg_.startswith("-"), "AB17: Change -> the next element (class:fn:abilDo attune): %s / %s" % (msg_, el1))
    page = Page(pr, NT)
    click(page, "trab0")
    err, texts, evs = render(page)
    ck(not [t for t in texts if t.startswith("Element: ")] and "trmat" not in evn(evs, "tr"), "AB17: Breach has no element row")
    bridge.remove("rebirth:fn:count")
    AS.RBN.clear()
    AS.set(str(me), JArray(JString)(["u.ArcaneBreach", "u.ElementalImbue"]), JArray(JString)(["0", "0"]))
    bridge.put("class:" + str(me), "Mage")
    bridge.put("profile:class:" + str(me), "Mage")
    # ---------------- AB18 the Fishing tree
    TD = T("TreeDefs")
    TRS = [str(x) for x in TD.TREES]
    ck(TRS[8] == "Fishing" and int(NT) == 9, "AB18: Fishing is tree 8, the class tab is page 9: %s / %d" % (TRS, int(NT)))
    names8 = [str(TD.NAME[96 + j]) for j in range(12)]
    ck(names8 == ["Fishing Fortune", "Quick Bite", "Fishing Wisdom", "Sea Legs", "Treasure Hunter", "Strong Line", "Bait Saver", "Rare Catch",
                  "Steady Reel", "Fortune II", "Twin Catch", "Sea Hunter"], "AB18: the 12 Fishing nodes: %s" % names8)
    CALC = T("TreeCalc")
    for m_ in ("SkyySkills", "SkyyGear", "SkyySacks", "SkyyFishing"):
        bridge.remove("tree:reads:" + m_)
    ck([bool(CALC.coming(96 + j)) for j in range(12)] == [True, True, True, False] + [True] * 8, "AB18: every Fishing node but Sea Legs waits for its reader")
    ck(str(TD.COMING_WHO[96]) == "SkyyFishing" and str(TD.COMING_WHO[98]) == "SkyySkills", "AB18: Fortune waits for SkyyFishing, Wisdom for SkyySkills: %s / %s"
       % (TD.COMING_WHO[96], TD.COMING_WHO[98]))
    d = fresh()
    d.uid = me
    LV["lvl"] = 100
    Cfg.EXTRA_DUST = 10 ** 9
    r18a = str(T("TreeOps").buy(pr, 8, 1))
    ck(r18a.startswith("Fishing Fortune is coming with SkyyFishing") and int(d.lv[96]) == 0, "AB18: Fishing Fortune refused while coming: %s" % r18a)
    r18b = str(T("TreeOps").buy(pr, 8, 4))
    ck(r18b == "Unlocked Sea Legs!" and int(d.lv[99]) == 1, "AB18: Sea Legs unlocks before any reader (applied by SkyyTrees): %s" % r18b)
    r18c = str(T("TreeOps").buy(pr, 8, 4))
    ck(r18c == "Sea Legs is now level 2", "AB18: ... levels up with Fishing Dust: %s" % r18c)
    Fx = T("TreeFx")
    v18 = [float(x) for x in Fx.compute(me)]
    ck(abs(v18[99] - 2.0) < 1e-9, "AB18: effect vector Sea Legs = 2 (+2 max Health): %s" % v18[99])
    va18 = Fx.compute(me)
    hp18 = float(Fx.healthOf(me, va18))
    va18[99] = 0.0
    ck(abs(hp18 - float(Fx.healthOf(me, va18)) - 2.0) < 1e-9, "AB18 fix: skyytree_health (healthOf) adds Sea Legs: +%s" % (hp18 - float(Fx.healthOf(me, va18))))
    bridge.put("tree:reads:SkyyFishing", "Fishing.NFortune,Fishing.NBite")
    bridge.put("tree:reads:SkyySkills", "Fishing.NWisdom")
    ck(not bool(CALC.coming(96)) and bool(CALC.coming(100)), "AB18: SkyyFishing lists Fortune -> Fortune buyable, Treasure still waits")
    r18d = str(T("TreeOps").buy(pr, 8, 1))
    r18e = str(T("TreeOps").buy(pr, 8, 3))
    ck(r18d == "Unlocked Fishing Fortune!" and r18e == "Unlocked Fishing Wisdom!", "AB18: Fortune + Wisdom unlock once listed: %s / %s" % (r18d, r18e))
    Fx.refresh(me)
    bm18 = bridge.get("skill:bonus:" + str(me))
    bmt = dict(bm18.get("trees")) if bm18 is not None and bm18.get("trees") is not None else {}
    ck(abs(float(bmt.get("xp.fishing", 0)) - 0.01) < 1e-9, "AB18: skill:bonus xp.fishing 0.01 (Fishing Wisdom Lv 1): %s" % bmt)
    TB18 = T("TreeBonusFn")()
    ck(abs(float(TB18.apply(JArray(JObject)([me, JString("Fishing.NFortune")]))) - 0.01) < 1e-12
       and float(TB18.apply(JArray(JObject)([me, JString("Fishing.NTreasure")]))) == 0.0, "AB18: tree:fn:bonus Fishing.NFortune = 0.01, Treasure 0")
    ck(str(bridge.get("tree:" + str(me))).find("Fishing:") >= 0, "AB18: tree:<uuid> lists Fishing: %s" % bridge.get("tree:" + str(me)))
    page = Page(pr, 8)
    err, texts, evs = render(page)
    ck(err is None and "Fishing Fortune" in " | ".join(texts) and "Sea Legs" in " | ".join(texts), "AB18: the Fishing tab builds (nodes shown): %s" % err)
    ck([x_ for x_ in evn(evs, "trtab") if x_ == "trtab8"], "AB18: the tab row binds trtab8: %s" % evn(evs, "trtab"))
    page = Page(pr, 0)
    err, texts, evs = render(page)
    ck(err is None and "trtab8" in evn(evs, "trtab"), "AB18: other tree pages show the Fishing tab too")
    rs18 = str(T("TreeOps").respec(pr, 8))
    ck(rs18.startswith("Respec done") and int(d.lv[99]) == 0, "AB18: respec Fishing: %s" % rs18)
    Cfg.EXTRA_DUST = 0
    for m_ in ("SkyySkills", "SkyyFishing"):
        bridge.remove("tree:reads:" + m_)
    # ---------------- AB19 the Farming average
    TF = TRS.index("Farming")
    LV["lvl"] = 30
    # fix round: skill:fn:level answers "farmingavg" (SkyySkills 0.4.37+, the ACTIVE profile); the bridge number only says it exists
    LVN = {}
    def lvn(o):
        k_ = str(o[1])
        if k_ in LVN:
            return None if LVN[k_] is None else Integer.valueOf(LVN[k_])
        return Integer.valueOf(LV["lvl"])
    bridge.put("skill:fn:level", Fn(lvn))
    ck(int(CALC.level(me, TF)) == 30, "AB19: no skill:farmavg -> the Farming level (30)")
    LVN["farmingavg"] = 14
    ck(int(CALC.level(me, TF)) == 30, "AB19 fix: no skill:farmavg (older SkyySkills) -> farmingavg is not asked, the Farming level")
    bridge.put("skill:farmavg:" + str(me), Integer.valueOf(12))
    ck(int(CALC.level(me, TF)) == 14 and int(CALC.level(me, 0)) == 30, "AB19 fix: the Farming tree's level = skill:fn:level farmingavg (14), not the bridge number (12); Mining stays 30")
    bridge.put("skill:farmavg:" + str(me), Integer.valueOf(50))
    ck(int(CALC.level(me, TF)) == 14, "AB19 fix: a stale skill:farmavg (an old profile's 50) is ignored -> 14")
    LVN["farmingavg"] = None
    ck(int(CALC.level(me, TF)) == 50, "AB19 fix: farmingavg answers nothing -> the bridge number (50)")
    LVN["farmingavg"] = 14
    Cfg.FARM_AVG = False
    ck(int(CALC.level(me, TF)) == 30, "AB19: farming.average OFF -> the Farming level")
    Cfg.FARM_AVG = True
    bridge.put("skill:farmavg:" + str(me), JString("x"))
    ck(int(CALC.level(me, TF)) == 30, "AB19: a non-number -> the Farming level")
    bridge.put("skill:farmavg:" + str(me), Integer.valueOf(12))
    LVN["farmingavg"] = -4
    ck(int(CALC.level(me, TF)) == 0, "AB19: a negative average -> 0")
    bridge.remove("skill:farmavg:" + str(me))
    bridge.put("skill:fn:level", Fn(lambda o: Integer.valueOf(LV["lvl"])))
    ck(bool(Cfg.FARM_AVG), "AB19: farming.average defaults ON")

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
            check(not cc["added"] and not cc["gone"], "CC: no class added or removed: %s %s" % (cc["added"], cc["gone"]))
            gone = dict((c, v["fields_gone"]) for c, v in cls_.items() if v["fields_gone"])
            check(not gone, "CC: no field removed: %s" % gone)
            struct = dict((c, sorted(m.split("(")[0] for m in v["structural"])) for c, v in cls_.items() if v["structural"] and c not in KIT)
            print("CC. 0.3.9 -> 0.3.10 structural: %s" % struct)
            print("CC. new fields: %s" % dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"]))
            # 0.3.10: the Spellblade (TreeClass data + NEW310), the panel (TreePage), the Fishing tree (TreeDefs data, TreeFx bonus map),
            # farming.average + HAS310 (TreeCfg), the Farming average (TreeCalc.farmAvg / level)
            allowed = {"TreeClass", "TreePage", "TreeDefs", "TreeFx", "TreeCfg", "TreeCalc"}
            # the tree count (8 -> 9), the node count (96 -> 108) and the class count (7 -> 8) are static final ints javassist inlines into
            # every method that loops over them - those methods change their constants only (the CfgFile clinit = the version text)
            allowed |= {"CfgFile", "TreeAbil", "TreeClassOps", "TreeData", "TreeKit", "TreeProbeCmd", "TreeRb", "TreeSkillCmd", "TreeStore"}
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
        print("JT. assets that differ from 0.3.9: %s" % diff[:20])
        check(all(x.startswith("Server/") or x.startswith("Common/") for x in diff), "JT: only generated assets differ from 0.3.9's: %s" % diff[:5])
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        mnd, mpd = dict(mn), dict(mp)
        mnd.pop("Description", None)
        mpd.pop("Description", None)
        check(json.dumps(mnd, sort_keys=True) == json.dumps(mpd, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.9's but the version (+ description)")
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
            nz = lambda r: T34.norm_start(r).replace(VERSION, "0.3.X").replace(PREV_VERSION, "0.3.X").replace("100 of 100 nodes", "88 of 88 nodes")   # 0.3.10: + the 12 Fishing nodes
            sn, sp = sts["new"]["starts"], sts["prev"]["starts"]
            check(nz(sn[0]) == nz(sp[0]), "ST: start 1 of 0.3.10 = 0.3.9's: %s / %s" % (sn[0]["changed"], sp[0]["changed"]))
            check(sn[1]["changed"] == [] and sn[1]["sum"] == sn[0]["sum"], "ST: start 2 changes nothing and reads the same: %s" % sn[1]["changed"])
            print("ST. start twice on the live copy: start 1 changed %s (same as 0.3.9), start 2 nothing" % sn[0]["changed"])
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
