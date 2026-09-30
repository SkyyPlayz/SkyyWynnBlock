"""SkyyExploration 0.2.2 - bare-JVM harness for the look-only restyle (vanilla UI pass, batch B3 with SkyySkills 0.4.7 + SkyyTrees 0.2.5).

    python SkyyExploration/test_skyyexploration_0.2.2.py [--jar <SkyyExploration-0.2.2.jar>] [--old <SkyyExploration-0.2.1.jar>]
                                                         [--dir <scratch folder>] [--keep]

Build the jar first (python SkyyExploration/build_skyyexploration_0.2.2.py). The old jar defaults to SkyyExploration-0.2.1.jar next to
this file (byte-identical to the deployed one when this harness was written). Child processes start fresh JVMs (the game's own JRE,
-Xverify:all, -XX:-UsePerfData, HytaleServer.jar + ONE mod jar on the classpath; javassist only for the bytecode step) and check:
  A  every class of the 0.2.2 jar AND of the 0.2.1 jar loads and initializes under -Xverify:all
  B  the REAL ExplorePage.build (17 states: every tab; SkyySkills missing / no Exploration row / full; unreadable file; an excluded
     world; parts switched off; titles earned / locked / all, result texts; checklists off / none / page 1 / page 2 / another island /
     0% / 100%; footer without Skills + tree) and AdminPage.build (15 states: Spots empty / 12 spots with a pending remove on a row of
     page 1 (the selected-row look) + a 40-letter name of wide glyphs / page 2 nearest with kept boxes / an open spot on page 1; Checklist with a custom entry + pending remove / a spot + pending take-off / a vanished
     chest with chests off / checklists off / empty; Island with 12 players / a blank world; excluded worlds on Spots and Island; a bad
     and an edited + unsaved world file) of both jars, with the engine's real UICommandBuilder / UIEventBuilder (fake world / players:
     Unsafe-allocated Store, EntityStore, World, Universe, PlayerRefs; the mod's own data classes filled through their fields)
  C  per state: identical event bindings (type, selector, EventData, lock flag, order); every 0.2.1 element id still created; every
     0.2.1 b.set (Text, Value) identical - the one allowed difference (review fix): an admin list row name (#SkyyXa[C]RowN<i>) wider
     than its one-line 430 px column is cut to the widest prefix that fits + "..." (AdminPage.clip; a name that fits is unchanged);
     identical inline texts (the only addition: the frame title EXPLORATION of /explore), identical placeholders and identical
     TextField MaxLength per field
  D  per state, the 0.2.2 markup as the client gets it: SUI.check_markup on every append (the first = the page root) + SUI.check_page
     (parents exist, no duplicate id, every b.set target exists) + SUI.assert_proven (proven properties only: no FlexWeight,
     WrapMaxLines, LetterSpacing, LayoutMode Right / Center / Full, nothing UNVERIFIED); the enumerated values vanilla uses
     (VerticalAlignment Center / End only - assert_proven checks keys, not values; HorizontalAlignment Start / Center / End;
     LayoutMode Top / Left); only kit colours or the declared page data colours; the window body filled EXACTLY; every LayoutMode Top
     container with a Height holds its children, every LayoutMode Left row fits its width (widths inherited down Top columns); a
     progress fill only when > 0 px; RUNTIME TEXT FIT (review fix): every b.set Text of a one-line label fits its width (the kit's
     text_width, the label's own size / bold / uppercase / font), and every wrapped label with a Height holds its lines
  E  ExplorePage.msgColor on every result text 0.2.1 can show (title set / removed = success, refusals = error) and AdminPage.stColor on
     the + / - / = marks (the kit's vanilla success / error / info)
  F  class bytes 0.2.1 vs 0.2.2: only ExplorePage + AdminPage (the pages: handleDataEvent / jsonStr / ph / clearKeeps / ev3 unchanged;
     only the markup methods changed, the old style helpers + fields gone, the new helpers listed), SkyyExplorationPlugin (setup: the
     ready line), ExpCfg (the version string of its DEFAULTS header) and the config kit classes differ; method by method (constant-pool
     indices ignored). The config kit: tools/skyycfg.py is 1.1 now and 0.2.1 was built on 1.0 ("each adopter picks 1.1 up at its own
     next version"): the CfgRows row table (every static field both jars have) is identical but for the version in the DL0 header,
     only the kit 1.1 fields KIT / SIG_USS / VTYPES are new and no kit method is gone
The old jar: *.jar is git-ignored - on a fresh checkout rebuild it first (python SkyyExploration/build_skyyexploration_0.2.1.py, the
LIVE SET pin; that script is never edited).
Not testable without the game (UNVERIFIED in the build report): the look itself on a client (the kit base look + the 1.4 blocks), text
widths beyond the kit's font-table estimate. Nothing is deployed. Default scratch folder: tools/dev/scratch/skyyexploration-022
(git-ignored), deleted at the end unless --keep; TEMP/TMP and java.io.tmpdir point into it. Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.2.2", "0.2.1"
PKG = "com.skyy.explore."
EX_W, EX_H, XA_W, XA_H = 1120, 906, 1120, 925          # = build_skyyexploration_0.2.2.py EX_W / EX_H / XA_W / XA_H
# the PAGE data colours of build_skyyexploration_0.2.2.py (EXPLORE_COLOR, SECRET_COLOR, the GROUPS colours, KIND_COLOR); its
# CHAT_COLORS (UI_DATA_COLORS too, for the lint) colour chat lines only and are NOT allowed in page markup (review fix: #ffe08a / #ffb080
# / #ff9090 are chat-only)
DATA_COLORS = ("#e0a040", "#d890ff", "#8fe08a", "#f0d060", "#7fd0ff", "#bfe6ff", "#ff9a70", "#9fd0ff", "#9adf86", "#ffd27a", "#c8a0ff",
               "#ffb070")
PAGE_CLASSES = {"com/skyy/explore/ExplorePage.class", "com/skyy/explore/AdminPage.class"}
VERSION_ONLY = {"com/skyy/explore/ExpCfg.class"}                    # ExpCfg.DEFAULTS: "# SkyyExploration 0.2.2 - change these in game ..."
# the config kit (tools/skyycfg.py) is 1.1 now; 0.2.1 was built on 1.0 - every rebuild picks 1.1 up ("each adopter picks 1.1 up at its
# own next version", skyycfg.py header; bridge contract "1", file / log / history / export formats unchanged). F proves the ROW TABLE
# (every static field of CfgRows both jars have) is identical, only KIT / SIG_USS / VTYPES are new, and no kit method is gone.
CFG_KIT = {"com/skyy/explore/CfgFn.class", "com/skyy/explore/CfgRows.class", "com/skyy/explore/CfgFile.class",
           "com/skyy/explore/CfgSaveTask.class"}
EXPECTED_DIFF = PAGE_CLASSES | VERSION_ONLY | CFG_KIT | {"com/skyy/explore/SkyyExplorationPlugin.class", "manifest.json"}
# review fix: an admin list row name is one 18 px bold line in a 430 px column (build XA_ROW_TW); AdminPage.clip cuts a wider name
ROWN_RE = re.compile(r"^#SkyyXaC?RowN\d+\.Text$")
ROWN_W, ROWN_SIZE = 430, 18
WIDE_NAME = "WWWWWWWWWWWWWWWWWWWW MMMMMMMMMMMMMMMMMMM"     # 40 letters (the name field's MaxLength) of the widest glyphs


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyyexploration-022")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyExploration-%s.jar" % OLD_VERSION)))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _jvm_start(jars, extra_cp=()):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR] + list(jars) + list(extra_cp), convertStrings=True)
    return B


# ============================================================================================ child: build every page state of one jar
EX_STATES = ["ov fresh no skills", "ov full", "ov no row", "ov bad file", "ov excluded world", "ov parts off", "zones",
             "titles set msg", "titles locked msg", "titles all earned", "ck off", "ck none", "ck page 1", "ck page 2",
             "ck other island 0%", "ck 100%", "footer no skills no tree"]
XA_STATES = ["sp empty world", "sp 12 selected pending", "sp page 2 nearest keeps", "sp open spot keeps", "ck custom pending",
             "ck spot pending off", "ck chest gone chests off", "ck disabled none", "ck empty", "isl players", "isl blank world",
             "ex spots", "ex island switches", "file bad", "file edited unsaved"]
MSG_TEXTS = ["", "Title removed", "Your title is now Wanderer - it shows in front of your chat messages",
             "Pathfinder is locked - Exploration 10", "Unknown title - /title shows the list",
             "Your exploration file could not be read - nothing can change until an admin fixes it",
             "SkyySkills is not installed - there is no skills page"]
ST_TEXTS = ["", "+Spot added", "-Give the spot a name", "=Nothing changed", "plain"]


def run_states(jar, out):
    from jpype import JClass, JArray, JImplements, JOverride, JString, JLong, JBoolean
    _jvm_start([jar])
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    loaded, load_fails = 0, []
    for n in names:
        try:
            Cls.forName(n, True, loader)
            loaded += 1
        except Exception as e:
            load_fails.append("%s: %s" % (n, e))
    res = {"jar": jar, "classes": len(names), "loaded": loaded, "load_fails": load_fails, "ex": {}, "xa": {}, "msg": None, "st": None}
    if load_fails:
        json.dump(res, open(out, "w"), indent=1)
        return

    Cfg, Store_, Reg, Chest, IO = (JClass(PKG + n) for n in ("ExpCfg", "ExpStore", "SpotReg", "ChestReg", "ExpIO"))
    Data, SpotDef, EntryDef, Ops = JClass(PKG + "ExpData"), JClass(PKG + "SpotDef"), JClass(PKG + "EntryDef"), JClass(PKG + "ExAdminOps")
    ExPage, XaPage = JClass(PKG + "ExplorePage"), JClass(PKG + "AdminPage")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Universe = JClass("com.hypixel.hytale.server.core.universe.Universe")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Holder = JClass("com.hypixel.hytale.component.Holder")
    CStore = JClass("com.hypixel.hytale.component.Store")
    EStore = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    World = JClass("com.hypixel.hytale.server.core.universe.world.World")
    UUID, CHM, Paths = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.nio.file.Paths")
    LOS = JClass("it.unimi.dsi.fastutil.longs.LongOpenHashSet")
    Boolean, Long, System = JClass("java.lang.Boolean"), JClass("java.lang.Long"), JClass("java.lang.System")
    Defs = JClass(PKG + "ExpDefs")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    def sets(cls, name, val):          # a public static (volatile) field
        setf(None, cls, name, val)

    base = os.path.join(SCRATCH, "data-" + os.path.basename(jar))
    sets(Reg, "DIR", Paths.get(os.path.join(base, "worlds"), []))
    sets(Store_, "DIR", Paths.get(os.path.join(base, "players"), []))
    sets(Chest, "DIR", Paths.get(os.path.join(base, "chests"), []))
    sets(Cfg, "FILE", Paths.get(os.path.join(base, "config.properties"), []))   # never read or written (defaults = the static fields)
    uni = U.allocateInstance(Universe.class_)
    players, worlds = CHM(), CHM()
    setf(uni, Universe, "playersByUuid", players)
    setf(uni, Universe, "players", players.values())
    setf(uni, Universe, "worldsByUuid", worlds)
    setf(None, Universe, "instance", uni)
    holder = U.allocateInstance(Holder.class_)
    bridge = IO.bridge()
    DEFAULT_FLAGS = dict((k, bool(getattr(Cfg, k))) for k in ("CHESTS_ON", "LUCK_ON", "SPOTS_ON", "CHECK_ON"))

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            return self.v

    def uid(n):
        return UUID(0xe0e0, n)

    def world(name):
        w = U.allocateInstance(World.class_)
        setf(w, World, "name", name)
        wu = UUID(0xa0a0, sum(ord(c) for c in name))          # deterministic (never Python's salted hash)
        worlds.put(wu, w)
        es = U.allocateInstance(EStore.class_)
        setf(es, EStore, "world", w)
        st = U.allocateInstance(CStore.class_)
        setf(st, CStore, "externalData", es)
        return w, wu, st

    def player(n, name, wu=None):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", uid(n))
        setf(pr, PRef, "username", name)
        setf(pr, PRef, "holder", holder)
        if wu is not None:
            setf(pr, PRef, "worldUuid", wu)
            players.put(uid(n), pr)
        return pr

    def data(n, **kw):
        d = Data()
        d.key = str(uid(n))
        for k, v in kw.items():
            setattr(d, k, v)
        Store_.DATA.put(d.key, d)
        return d

    def spot(i, name, x, secret=False, check=True, xp=500):
        return SpotDef("s%d" % i, i, name, x, 64, -x, 6, xp, secret, check)

    def entry(i, typ, text, arg="", cnt=0, x=0):
        return EntryDef("c%d" % i, 100 + i, typ, arg, text, x, 70, x, cnt)

    def worlddef(wn, name, spots, entries, checklist=True, rxp=0, rco=0, sxp=-1, sexp=-1):
        wf = Chest.wf(wn)
        w = Reg.blank(wn, wf)
        w.name = name
        w.checklist = checklist
        w.rewardXp, w.rewardCoins, w.spotXp, w.secretXp = rxp, rco, sxp, sexp
        w.spots = JArray(SpotDef)(spots)
        w.entries = JArray(EntryDef)(entries)
        Reg.finish(w)
        Reg.W.put(wf, w)
        return w

    def found(d, wf, ids):
        m = CHM()
        for i in ids:
            m.put(i, Boolean.TRUE)
        d.found.put(wf, m)

    def opened(d, wf, coords):
        s = LOS()
        for (x, y, z) in coords:
            s.add(JLong(Defs.pack(x, y, z)))
        d.opened.put(wf, s)

    def reset():
        Store_.DATA.clear()
        Reg.W.clear(); Reg.BAD.clear(); Reg.STAMP.clear(); Reg.DIRTY.clear()
        Chest.W.clear()
        Ops.CONFIRM.clear()
        players.clear(); worlds.clear()
        for k in list(bridge.keySet()):
            ks = str(k)
            if ks.startswith(("skill", "tree:", "coins:", "profile", "config:fn:SkyySkills")):
                bridge.remove(k)
        for k, v in DEFAULT_FLAGS.items():
            sets(Cfg, k, v)

    def skills(level, row=True, xp=12345, tree=True, luck_tree=0.0):
        bridge.put("skill:fn:level", Fn(JClass("java.lang.Integer")(level)))
        bridge.put("skill:fn:xp", Fn(Long(xp)))
        if row:
            bridge.put("skill:" + str(uid(1)), "Mining:3,Exploration:%d" % level)
        if tree:
            bridge.put("tree:names", "Mining,Foraging,Exploration")
        if luck_tree:
            bridge.put("tree:fn:bonus", Fn(JClass("java.lang.Double")(luck_tree)))

    def cmds_of(b, ev):
        cmds = [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]
        evs = [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data),
                bool(e.locksInterface)] for e in ev.getEvents()]
        return cmds, evs

    HOME = "skyworld"
    ISLE = "Old Fen"
    for state in EX_STATES:
        reset()
        wn = "skyy-island-" + str(uid(1)) if state == "ov excluded world" else HOME
        _w, wu, st = world(wn)
        me = player(1, "Steve", wu)
        wf = Chest.wf(HOME)
        tab = 0
        page_msg, ck_world, ck_page = "", None, 0
        if state in ("ov full", "zones", "titles set msg", "titles locked msg", "ov excluded world", "ov parts off"):
            skills(12, luck_tree=0.6)
            d = data(1, owed=1234, quiet=True, chests=30, luck=3, total=1500, spots=5, secrets=2, title="wanderer")
            for r in ("Zone1_Spawn", "Zone1_Tier1", "Oceans", "Zone2_Tier1"):
                d.zones.put(r, Boolean.TRUE)
            s = LOS()
            for c in range(1, 140):
                s.add(JLong(c * 7919))
            d.chunks.put(wf, s)
            pa = JArray(JClass("long"))(1)
            pa[0] = 900
            d.paid.put(wf, pa)
            worlddef(HOME, "Skyworld", [spot(1, "Old Mill", 10), spot(2, "Sunken Bell", 40, secret=True), spot(3, "Watchtower", 80, check=False)],
                     [entry(1, 4, "Ring the bell")])
            found(d, wf, ["s1"])
            if state == "ov parts off":
                for k in DEFAULT_FLAGS:
                    sets(Cfg, k, False)
            if state == "zones":
                tab = 1
            if state == "titles set msg":
                tab, page_msg = 2, MSG_TEXTS[2]
            if state == "titles locked msg":
                tab, page_msg = 2, MSG_TEXTS[3]
        elif state == "ov fresh no skills":
            data(1)
        elif state == "ov no row":
            skills(0, row=False, tree=False)
            data(1, owed=77)
        elif state == "ov bad file":
            skills(3)
            data(1, bad=True)
        elif state == "titles all earned":
            skills(100)
            d = data(1, chests=300, total=20000, spots=30, secrets=12)
            for r in Defs.R_ID:
                d.zones.put(r, Boolean.TRUE)
            tab, page_msg = 2, MSG_TEXTS[1]
        elif state.startswith("ck ") or state == "footer no skills no tree":
            if state != "footer no skills no tree":
                skills(20)
            tab = 3 if state != "footer no skills no tree" else 0
            d = data(1)
            if state == "ck off":
                sets(Cfg, "CHECK_ON", False)
            elif state != "ck none" and state != "footer no skills no tree":
                sp = [spot(i, "Spot number %d" % i, i * 10, secret=(i % 4 == 0), check=(i != 5), xp=(0 if i == 6 else 250 * i)) for i in range(1, 16)]
                en = [entry(1, 1, "Open the chest by the mill", "10 70 10", x=10), entry(2, 2, "Open 5 loot chests here", cnt=5),
                      entry(3, 3, "Enter the Zone1 Tier1 region", "Zone1_Tier1"), entry(4, 4, "Ring the bell at the old tower"),
                      entry(5, 4, "A custom task with a very long text that has to wrap onto a second line in its row"),
                      entry(6, 2, "Open 2 loot chests here", cnt=2), entry(7, 4, "Talk to the keeper"),
                      entry(8, 4, "Find the lost map"), entry(9, 4, "Light the beacon"), entry(10, 4, "Climb the spire"),
                      entry(11, 4, "Cross the bridge")]
                wdA = worlddef(HOME, "Skyworld", sp, en, rxp=5000, rco=2500)
                wfB = Chest.wf("oldfen")
                worlddef("oldfen", ISLE, [spot(40, "Fen Hut", 5)], [entry(40, 4, "Wade the marsh")])
                if state in ("ck page 1", "ck page 2"):
                    found(d, wf, ["s1", "s4", "s7"])
                    opened(d, wf, [(10, 70, 10), (1, 2, 3), (4, 5, 6)])
                    zm = CHM()
                    zm.put("Zone1_Tier1", Boolean.TRUE)
                    d.zoneW.put(wf, zm)
                    d.ticks.put("c4", Boolean.TRUE)
                if state == "ck page 2":
                    ck_page = 1
                    d.doneW.put(wf, Boolean.TRUE)
                    bridge.put("coins:fn:add", Fn(Boolean.TRUE))
                if state == "ck other island 0%":
                    ck_world = wfB
                if state == "ck 100%":
                    found(d, wf, ["s%d" % i for i in range(1, 16)])
                    opened(d, wf, [(10, 70, 10)] + [(i, i, i) for i in range(1, 8)])
                    zm = CHM()
                    zm.put("Zone1_Tier1", Boolean.TRUE)
                    d.zoneW.put(wf, zm)
                    for c in (4, 5, 7, 8, 9, 10, 11):
                        d.ticks.put("c%d" % c, Boolean.TRUE)
            if state == "footer no skills no tree":
                page_msg = MSG_TEXTS[6]
        page = ExPage(me, tab)
        page.msg = page_msg
        page.ckWorld = ck_world
        page.ckPage = ck_page
        b, ev = UCB(), UEB()
        try:
            page.build(None, b, ev, st)
            err = None
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, e)
        cmds, evs = cmds_of(b, ev)
        res["ex"][state] = {"error": err, "commands": cmds, "events": evs}

    for state in XA_STATES:
        reset()
        wn = {"ex spots": "instance-dungeon-7", "ex island switches": "instance-dungeon-7"}.get(state, HOME)
        _w, wu, st = world(wn)
        me = player(1, "Admin", wu)
        wf = Chest.wf(wn)
        tab = 0
        page = None
        if state.startswith("sp "):
            if state != "sp empty world":
                names = ["Old Mill", "Sunken Bell", "Watchtower", "Old Mill", "Fen Hut", "Crystal Cave", "Lost Camp", "Iron Gate",
                         "Abcdefghijklmnopqrstuvwxyzabcdefghijklmn", "Moss Well", WIDE_NAME, "Last Light"]
                sp = [spot(i + 1, names[i], (i + 1) * 13, secret=(i % 3 == 1), check=(i % 2 == 0), xp=500 + 250 * i) for i in range(12)]
                worlddef(HOME, "Skyworld", sp, [entry(1, 4, "Ring the bell")], sxp=750)
            d = data(1, spots=2)
            found(d, wf, ["s2"])
            page = XaPage(me, 0)
            if state == "sp 12 selected pending":          # newest first: page 1 lists s12 .. s5 - the selected row is on screen
                page.selSpot = "s7"
                Ops.CONFIRM.put(uid(1), "rm|" + wf + "|s7|" + str(System.currentTimeMillis()))
                page.msg = ST_TEXTS[1]
            if state == "sp page 2 nearest keeps":
                page.page, page.sort, page.newSecret = 1, 1, True
                page.kNName, page.kNRad, page.kNXp = "Old Mill", "12", "abc"
                page.msg = ST_TEXTS[2]
            if state == "sp open spot keeps":
                page.selSpot = "s6"
                page.kEName = "New name"
                page.msg = ST_TEXTS[3]
        elif state.startswith("ck "):
            tab = 1
            if state != "ck empty":
                sp = [spot(1, "Old Mill", 10), spot(2, "Sunken Bell", 20, secret=True), spot(3, "Watchtower", 30, check=False)]
                en = [entry(1, 1, "Open the chest by the mill", "10 70 10", x=10), entry(2, 2, "Open 5 loot chests here", cnt=5),
                      entry(3, 3, "Enter the Zone1 Tier1 region", "Zone1_Tier1"), entry(4, 4, "Ring the bell at the old tower"),
                      entry(5, 4, "A custom task with a very long text that has to wrap onto a second line in its row"),
                      entry(6, 4, "Talk to the keeper"), entry(7, 4, "Find the lost map"), entry(8, 4, "Light the beacon")]
                worlddef(HOME, "Skyworld", sp, en, checklist=(state != "ck disabled none"))
                cm = CHM()
                cm.put(Long(Defs.pack(10, 70, 10)), "Zone1_Goblin_Tier1|")
                if state != "ck chest gone chests off":
                    Chest.W.put(wf, cm)
            else:
                worlddef(HOME, "Skyworld", [spot(3, "Watchtower", 30, check=False)], [])
            p2 = player(2, "Steve", wu)
            d2 = data(2)
            d2.ticks.put("c4", Boolean.TRUE)
            found(d2, wf, ["s1"])
            page = XaPage(me, 1)
            if state == "ck custom pending":
                page.selEntry, page.kCPlayer = "c4", "Steve"
                Ops.CONFIRM.put(uid(1), "ck|" + wf + "|c4|" + str(System.currentTimeMillis()))
            if state == "ck spot pending off":
                page.selEntry = "s2"
                Ops.CONFIRM.put(uid(1), "ckoff|" + wf + "|s2|" + str(System.currentTimeMillis()))
            if state == "ck chest gone chests off":
                page.selEntry = "c1"
                sets(Cfg, "CHESTS_ON", False)
                page.msg = ST_TEXTS[2]
            if state == "ck disabled none":
                sets(Cfg, "CHECK_ON", False)
        elif state.startswith("isl "):
            tab = 2
            if state == "isl players":
                worlddef(HOME, "Skyworld", [spot(1, "Old Mill", 10), spot(2, "Sunken Bell", 20, secret=True)],
                         [entry(1, 4, "Ring the bell")], rxp=5000, rco=2500, sxp=750, sexp=2000)
                bridge.put("coins:fn:add", Fn(Boolean.TRUE))
                for n in range(2, 14):
                    player(n, "Player%d%s" % (n, "abcdefghijk" if n == 3 else ""), wu)
                    if n % 4 == 0:
                        continue                      # not loaded yet
                    dd = data(n, bad=(n == 5))
                    if n % 3 == 0:
                        found(dd, wf, ["s1", "s2"])
                        dd.ticks.put("c1", Boolean.TRUE)
                        dd.doneW.put(wf, Boolean.TRUE)
                    bridge.put("profile:" + str(uid(n)), str(n % 3 + 1))
            page = XaPage(me, 2)
            page.msg = ST_TEXTS[1] if state == "isl players" else ""
        elif state.startswith("ex "):
            tab = 2 if state == "ex island switches" else 0
            page = XaPage(me, tab)
        elif state.startswith("file "):
            worlddef(HOME, "Skyworld", [spot(1, "Old Mill", 10)], [])
            if state == "file bad":
                Reg.BAD.put(wf, "could not be read")
            else:
                stamp = JArray(JClass("long"))(2)
                Reg.STAMP.put(wf, stamp)
                Reg.DIRTY.put(wf, Boolean.TRUE)
            page = XaPage(me, 0)
            page.msg = ST_TEXTS[3]
        b, ev = UCB(), UEB()
        try:
            page.build(None, b, ev, st)
            err = None
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, e)
        cmds, evs = cmds_of(b, ev)
        res["xa"][state] = {"error": err, "commands": cmds, "events": evs}

    rows = {}
    Rows, Mod = JClass(PKG + "CfgRows"), JClass("java.lang.reflect.Modifier")
    Arrays = JClass("java.util.Arrays")
    for f in Rows.class_.getDeclaredFields():
        if Mod.isStatic(f.getModifiers()):
            f.setAccessible(True)
            v = f.get(None)
            if v is not None and v.getClass().isArray():
                rows[str(f.getName())] = str(Arrays.deepToString(JArray(JClass("java.lang.Object"))([v])))
            else:
                rows[str(f.getName())] = None if v is None else str(v)
    res["cfgrows"] = rows
    if hasattr(ExPage, "msgColor"):
        res["msg"] = [[t, str(ExPage.msgColor(t))] for t in MSG_TEXTS]
    if hasattr(XaPage, "stColor"):
        res["st"] = [[t, str(XaPage.stColor(t))] for t in ST_TEXTS]
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: bytecode method compare (javassist)
def run_bytecode(old, new, out):
    import skyybuild as B
    from jpype import JClass
    _jvm_start([], [B.JAVASSIST])
    ClassPool, BAIS = JClass("javassist.ClassPool"), JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def listing(pool, data):
        cc = pool.makeClass(BAIS(data))
        ms = {}
        behaviors = list(cc.getDeclaredBehaviors())
        if cc.getClassInitializer() is not None:
            behaviors.append(cc.getClassInitializer())
        for mm in behaviors:
            key = "%s%s" % (mm.getName(), mm.getSignature())
            if mm.getMethodInfo().getCodeAttribute() is None:
                ms[key] = ""
                continue
            it = mm.getMethodInfo().getCodeAttribute().iterator()
            cpool = mm.getMethodInfo().getConstPool()
            lines = []
            while it.hasNext():
                ln = str(IP.instructionString(it, it.next(), cpool))
                ln = re.sub(r"#\d+ = ", "", ln).replace("ldc_w ", "ldc ")
                ln = re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln)
                lines.append(ln)
            ms[key] = "\n".join(lines)
        fields = sorted("%s %s" % (f.getName(), f.getSignature()) for f in list(cc.getDeclaredFields()))
        consts = {}
        for f in list(cc.getDeclaredFields()):
            ca = f.getFieldInfo().getConstantValue()
            if ca:
                consts[str(f.getName())] = str(cc.getClassFile().getConstPool().getLdcValue(ca))
        return ms, fields, consts

    zo, zn = zipfile.ZipFile(old), zipfile.ZipFile(new)
    res = {}
    for n in sorted(set(zo.namelist()) & set(zn.namelist())):
        if not n.endswith(".class"):
            continue
        a, b = zo.read(n), zn.read(n)
        if a == b:
            continue
        mo, fo, co = listing(ClassPool(False), a)
        mn, fn, cn = listing(ClassPool(False), b)
        changed = sorted(k for k in set(mo) & set(mn) if mo[k] != mn[k])
        consts = dict((k, [co.get(k), cn.get(k)]) for k in set(co) | set(cn) if co.get(k) != cn.get(k))
        res[n] = {"changed": changed, "gone": sorted(set(mo) - set(mn)), "new": sorted(set(mn) - set(mo)), "fields_same": fo == fn,
                  "fields_gone": sorted(set(fo) - set(fn)), "fields_new": sorted(set(fn) - set(fo)), "consts": dict((k, v) for k, v in consts.items()),
                  # changed only by the version string ("0.2.1" -> "0.2.2")
                  "version_only": all(mo[k].replace(OLD_VERSION, "V") == mn[k].replace(VERSION, "V") for k in changed)
                  and all((x or "").replace(OLD_VERSION, "V") == (y or "").replace(VERSION, "V") for x, y in consts.values())}
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent: comparisons
def js(v):
    """The Java value a Set command carries (its data is JSON); non-strings come back as their JSON text."""
    try:
        x = json.loads(v)
    except Exception:
        return v
    if isinstance(x, dict) and list(x) == ["0"]:      # UICommandBuilder.set(String, String) sends {"0": value}
        x = x["0"]
    return x if isinstance(x, str) else v


_ID_RE = re.compile(r"(?:^|[;{}])\s*[A-Z][A-Za-z]*\s+#([A-Za-z0-9]+)\s*\{")
_TEXT_RE = re.compile(r'(?<![A-Za-z])Text: "((?:[^"\\]|\\.)*)"')
_PH_RE = re.compile(r'PlaceholderText: "((?:[^"\\]|\\.)*)"')
_COL_RE = re.compile(r"(?:Background|TextColor|Color):\s*(#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?:\(\s*[0-9.]+\s*\))?)")


def ids_of(state):
    out = []
    for t, sel, data, text in state["commands"]:
        if t == "AppendInline" and text:
            out += _ID_RE.findall(text)
    return out


def sets_of(state):
    return dict((sel, js(data)) for t, sel, data, text in state["commands"] if t == "Set" and sel)


def inline_texts(state):
    return sorted(x for t, sel, data, text in state["commands"] if t == "AppendInline" and text for x in _TEXT_RE.findall(text) if x)


def placeholders(state):
    return sorted(x for t, sel, data, text in state["commands"] if t == "AppendInline" and text for x in _PH_RE.findall(text))


def props(SUI, mk):
    """(own anchor dict, padding (l, r, t, b), LayoutMode or None) of a markup's OUTER element."""
    own = SUI._own_props(mk)
    anc = SUI._anchor_vals(mk)
    pad = [0, 0, 0, 0]
    p = SUI._top_prop(own, "Padding")
    if p:
        for part in p.strip("()").split(","):
            k, _s, v = part.partition(":")
            k, v = k.strip(), v.strip()
            if not v:
                continue
            n = int(float(v))
            if k == "Full":
                pad = [pad[0] + n, pad[1] + n, pad[2] + n, pad[3] + n]
            elif k == "Horizontal":
                pad[0] += n; pad[1] += n
            elif k == "Vertical":
                pad[2] += n; pad[3] += n
            else:
                pad[{"Left": 0, "Right": 1, "Top": 2, "Bottom": 3}[k]] += n
    lm = SUI._top_prop(own, "LayoutMode")
    return anc, pad, lm


def layout_check(name, appends, SUI, counts, page_w, page_h, body_id):
    """The window body filled exactly; Top containers with a Height hold their children; Left rows fit their (inherited) width."""
    info, kids, order = {}, {}, []
    for parent, mk in appends:
        m = re.match(r"\s*[A-Z][A-Za-z]*\s+#([A-Za-z0-9]+)\s*\{", mk)
        eid = m.group(1) if m else None
        anc, pad, lm = props(SUI, mk)
        if eid:
            info[eid] = (parent, anc, pad, lm, mk)
            order.append(eid)
        kids.setdefault(parent, []).append((eid, anc))
    # content width / height of every element with an id (Width / Height or inherited down a Top column / the body)
    cw, ch = {}, {}
    for eid in order:
        parent, anc, pad, lm, _mk = info[eid]
        if parent is None:
            w, h = anc.get("Width"), anc.get("Height")
        elif eid == body_id:
            w, h = page_w, page_h - SUI.TITLE_H
        else:
            pw = cw.get(parent)
            plm = info[parent][3] if parent in info else None
            w = anc.get("Width", pw if plm in ("Top", None) else None)
            h = anc.get("Height")
        if w is not None:
            cw[eid] = w - pad[0] - pad[1]
        if h is not None:
            ch[eid] = h - pad[2] - pad[3]
    for eid in order:
        parent, anc, pad, lm, _mk = info[eid]
        ks = kids.get(eid, [])
        if not ks:
            continue
        if lm == "Top" and eid in ch:
            tot = sum(a.get("Height", 0) + a.get("Top", 0) + a.get("Bottom", 0) for _k, a in ks)
            if eid == body_id:
                check(tot == ch[eid], "%s: the window body children fill %d px exactly (got %d)" % (name, ch[eid], tot))
                counts["body_exact"] += 1
            else:
                check(tot <= ch[eid], "%s: #%s holds its children (%d of %d px)" % (name, eid, tot, ch[eid]))
            counts["columns"] += 1
        if lm == "Left" and eid in cw:
            tot = sum(a.get("Width", 0) + a.get("Left", 0) + a.get("Right", 0) for _k, a in ks)
            check(tot <= cw[eid], "%s: row #%s fits (%d of %d px)" % (name, eid, tot, cw[eid]))
            counts["rows"] += 1
            counts["min_row_slack"] = min(counts["min_row_slack"], cw[eid] - tot)
    return info, cw


_STYLE_NUM = re.compile(r"FontSize:\s*(\d+)")
_FONT_NAME = re.compile(r'FontName:\s*"([A-Za-z]*)"')


def text_fit(name, ap, SUI, counts, info, cw):
    """RUNTIME TEXT FIT (review fix): every b.set Text of a Label: one line (no Wrap) = its text_width fits the label's width; wrapped
    with a Height = its greedy word-wrapped lines x the line height fit that Height. Width = the label's Anchor Width, else the width it
    inherits down a Top column minus its Left / Right margins, minus its padding."""
    for ident, prop, val in ap.sets:
        if prop != "Text" or not isinstance(val, str) or not val or ident not in info:
            continue
        parent, anc, pad, lm, mk = info[ident]
        if not mk.lstrip().startswith("Label "):
            continue
        style = SUI._top_prop(SUI._own_props(mk), "Style") or ""
        m = _STYLE_NUM.search(style)
        if not m or ident not in cw:
            counts["unmeasured"] += 1
            continue
        size = int(m.group(1))
        bold, upper, wrap = "RenderBold: true" in style, "RenderUppercase: true" in style, "Wrap: true" in style
        fm = _FONT_NAME.search(style)
        font = fm.group(1) if fm and fm.group(1) else "Default"
        room = cw[ident]
        if "Width" not in anc:
            room -= anc.get("Left", 0) + anc.get("Right", 0) + 2 * anc.get("Horizontal", 0)
        if not wrap:
            need = SUI.text_width(val, size, bold, font, upper)
            check(need <= room + 0.5, "%s: #%s runtime text %r: %.1f px on one line in %d px" % (name, ident, val, need, room))
            counts["text_fit"] += 1
            counts["min_text_slack"] = min(counts["min_text_slack"], room - need)
        elif "Height" in anc:
            lines = SUI.text_lines(val, room, size, bold, font, upper)
            need = lines * SUI.line_height(size, font, bold)
            h = anc["Height"] - pad[2] - pad[3]
            check(need <= h + 1, "%s: #%s runtime text %r: %d lines = %.1f px in %d px high (%d wide)" % (name, ident, val, lines, need, h, room))
            counts["wrap_fit"] += 1


def clip_why(SUI, old, new):
    """'' when `new` is AdminPage.clip(old): old overruns the one-line row name, new = the widest prefix that fits + '...'."""
    if not isinstance(old, str) or not isinstance(new, str):
        return "not text"

    def w(t):
        return SUI.text_width(t, ROWN_SIZE, True)
    if w(old) <= ROWN_W:
        return "the 0.2.1 name fits (%.1f px) - it must stay unchanged" % w(old)
    if not new.endswith("...") or not old.startswith(new[:-3]):
        return "not a prefix + '...'"
    if w(new) > ROWN_W + 0.5:
        return "the clipped name is %.1f px, wider than %d" % (w(new), ROWN_W)
    n = len(new) - 3
    while n < len(old) and old[n] == " ":
        n += 1
    if n < len(old) and w(old[:n + 1] + "...") <= ROWN_W - 1:
        return "not the widest prefix: %r fits too" % (old[:n + 1] + "...")
    return ""


ENUMS = (("VerticalAlignment", ("Center", "End")), ("HorizontalAlignment", ("Start", "Center", "End")), ("LayoutMode", ("Top", "Left")))
_MAXLEN_RE = re.compile(r"TextField\s+#([A-Za-z0-9]+)\s*\{[^{}]*?MaxLength:\s*(\d+)")


def maxlens(state):
    return dict(x for t, sel, data, text in state["commands"] if t == "AppendInline" and text for x in _MAXLEN_RE.findall(text))


def compare_state(name, old, new, SUI, counts, prefix, page_w, page_h, body_id, title_added):
    check(old["error"] is None and new["error"] is None, "%s: build() ran in both jars (%s / %s)" % (name, old["error"], new["error"]))
    if old["error"] or new["error"]:
        return
    # C1 bindings
    check(old["events"] == new["events"], "%s: event bindings identical (%d / %d)" % (name, len(old["events"]), len(new["events"])))
    counts["bindings"] += len(new["events"])
    # C2 ids
    oi, ni = ids_of(old), ids_of(new)
    miss = sorted(set(oi) - set(ni))
    check(not miss, "%s: no 0.2.1 id missing: %s" % (name, miss))
    counts["ids"] += len(set(oi))
    counts["new_ids"] += len(set(ni) - set(oi))
    # C3 b.set values (Text, Value): every 0.2.1 set is there with the same value
    os_, ns_ = sets_of(old), sets_of(new)
    for k in sorted(os_):
        if ROWN_RE.match(k) and ns_.get(k) != os_[k]:
            why = clip_why(SUI, os_[k], ns_.get(k))
            check(not why, "%s: set %s: the clipped row name 0.2.1 %r / 0.2.2 %r: %s" % (name, k, os_[k], ns_.get(k), why))
            counts["clipped"] += 1
        else:
            check(ns_.get(k) == os_[k], "%s: set %s: 0.2.1 %r / 0.2.2 %r" % (name, k, os_[k], ns_.get(k)))
        counts["sets"] += 1
    counts["new_sets"] += len(set(ns_) - set(os_))
    mo, mn = maxlens(old), maxlens(new)
    check(mo == mn, "%s: TextField MaxLength identical: %s / %s" % (name, mo, mn))
    counts["maxlen"] += len(mo)
    ot, nt = inline_texts(old), inline_texts(new)
    if title_added:
        check(nt.count("Exploration") == ot.count("Exploration") + 1, "%s: the frame title Exploration added once" % name)
        nt = list(nt)
        nt.remove("Exploration")
    check(ot == nt, "%s: inline texts identical: %s / %s" % (name, ot, nt))
    counts["inline"] += len(ot)
    check(placeholders(old) == placeholders(new), "%s: placeholders identical: %s / %s" % (name, placeholders(old), placeholders(new)))
    counts["placeholders"] += len(placeholders(old))
    # D the 0.2.2 markup as the client gets it
    ap = SUI.Appends()
    allowed = SUI.allowed_colors() | set(SUI.norm_color(c) for c in DATA_COLORS)
    for idx, (t, sel, data, text) in enumerate(new["commands"]):
        if t == "AppendInline":
            parent = None if sel is None else sel.lstrip("#")
            check(idx != 0 or parent is None, "%s: the first append is the page root" % name)
            try:
                SUI.check_markup(text, prefix=prefix, root=(parent is None))
            except ValueError as e:
                check(False, "%s: check_markup: %s" % (name, e))
            ap.append((parent, text))
            for c in _COL_RE.findall(text):
                check(SUI.norm_color(c) in allowed, "%s: colour %s is a kit / data colour" % (name, c))
                counts["colours"] += 1
            for key, ok_vals in ENUMS:
                for v in re.findall(r"(?<![A-Za-z])" + key + r":\s*([A-Za-z]+)", text):
                    check(v in ok_vals, "%s: %s: %s is not a vanilla-proven value (%s)" % (name, key, v, "/".join(ok_vals)))
                    counts["enums"] += 1
            for bad in ("Width: 0,", "Width: 0)", "ItemGrid"):
                check(bad not in text, "%s: no %s in %s" % (name, bad.strip(",)"), text[:80]))
            if parent == "SkyyExCkBar":
                w = SUI._anchor_vals(text).get("Width", 0)
                check(0 < w <= page_w - 2 * SUI.CONTENT_PAD, "%s: the progress fill is 1..%d px (%s)" % (name, page_w - 34, w))
                counts["fills"] += 1
        elif t == "Set":
            ident, prop = sel.lstrip("#").rsplit(".", 1)
            ap.sets.append((ident, prop, js(data)))
    try:
        SUI.check_page(ap, prefix)
        counts["check_page"] += 1
    except ValueError as e:
        check(False, "%s: check_page: %s" % (name, e))
    try:
        SUI.assert_proven(ap, what=name)
        counts["proven"] += 1
    except ValueError as e:
        check(False, "%s: assert_proven: %s" % (name, e))
    counts["appends"] += len(ap)
    info, cw = layout_check(name, ap, SUI, counts, page_w, page_h, body_id)
    text_fit(name, ap, SUI, counts, info, cw)
    counts["states"] += 1


def main():
    if "--run" in sys.argv:
        run_states(arg("--run"), arg("--out"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    for j in (JAR, OLD_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not SCRATCH.replace("\\", "/").lower().startswith(os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower()):
        sys.exit("--dir must be inside tools/dev/scratch/ (it is deleted afterwards): " + SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    me = os.path.abspath(__file__)
    outs = {}
    for tag, j in (("new", JAR), ("old", OLD_JAR)):
        outs[tag] = os.path.join(SCRATCH, "states-%s.json" % tag)
        p = subprocess.run([sys.executable, me, "--run", j, "--out", outs[tag], "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(outs[tag]), "child JVM for %s ran" % j)
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "bytecode child ran")
    if FAILS:
        return finish()
    new, old = json.load(open(outs["new"])), json.load(open(outs["old"]))
    # A
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                            os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    # B-D
    import skyyui as SUI
    SUI.verify(quiet=True)
    for key, states, prefix, pw, ph, body, title_added in (("ex", EX_STATES, "SkyyEx", EX_W, EX_H, "SkyyExRoot", True),
                                                          ("xa", XA_STATES, "SkyyXa", XA_W, XA_H, "SkyyXaRoot", False)):
        counts = dict(states=0, bindings=0, ids=0, new_ids=0, sets=0, new_sets=0, inline=0, placeholders=0, colours=0, check_page=0,
                      proven=0, appends=0, fills=0, body_exact=0, columns=0, rows=0, min_row_slack=10 ** 6, clipped=0, maxlen=0,
                      enums=0, text_fit=0, wrap_fit=0, unmeasured=0, min_text_slack=10 ** 6)
        for st in states:
            check(st in new[key] and st in old[key], "B: %s state %s built by both jars" % (key, st))
            if st in new[key] and st in old[key]:
                compare_state("%s/%s" % (key, st), old[key][st], new[key][st], SUI, counts, prefix, pw, ph, body, title_added)
        print(("B-D %s. %%(states)d states: %%(bindings)d bindings identical, %%(ids)d 0.2.1 ids all kept (+%%(new_ids)d new ids), "
               "%%(sets)d 0.2.1 b.set values identical (+%%(new_sets)d new), %%(inline)d inline texts + %%(placeholders)d placeholders "
               "identical; %%(check_page)d check_page + %%(proven)d assert_proven / %%(appends)d appends through check_markup, "
               "%%(colours)d colours audited, %%(body_exact)d bodies filled exactly, %%(columns)d columns + %%(rows)d rows fit "
               "(min row slack %%(min_row_slack)d px), %%(fills)d progress fills > 0; %%(clipped)d row names clipped as allowed, "
               "%%(maxlen)d MaxLength identical, %%(enums)d enumerated values vanilla-proven, runtime text fit: %%(text_fit)d one-line "
               "(min slack %%(min_text_slack).1f px) + %%(wrap_fit)d wrapped labels (%%(unmeasured)d unmeasured)"
               % ("ExplorePage" if key == "ex" else "AdminPage")) % counts)
    # E
    msg = dict(new.get("msg") or [])
    exp = {"": SUI.STATUS["="], MSG_TEXTS[1]: SUI.STATUS["+"], MSG_TEXTS[2]: SUI.STATUS["+"]}
    for t in MSG_TEXTS:
        check(msg.get(t) == exp.get(t, SUI.STATUS["-"]), "E: msgColor(%r) = %s (got %s)" % (t, exp.get(t, SUI.STATUS["-"]), msg.get(t)))
    stc = dict(new.get("st") or [])
    exps = {"": SUI.COLOR["text"], ST_TEXTS[1]: SUI.STATUS["+"], ST_TEXTS[2]: SUI.STATUS["-"], ST_TEXTS[3]: SUI.STATUS["="],
            "plain": SUI.COLOR["text"]}
    for t in ST_TEXTS:
        check(stc.get(t) == exps[t], "E: stColor(%r) = %s (got %s)" % (t, exps[t], stc.get(t)))
    print("E. msgColor on %d result texts, stColor on %d marks" % (len(msg), len(stc)))
    # F
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    check(sorted(zo.namelist()) == sorted(zn.namelist()), "F: same entries in both jars")
    diff = set(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    same = len(set(zo.namelist()) & set(zn.namelist())) - len(diff)
    check(diff <= EXPECTED_DIFF and PAGE_CLASSES <= diff, "F: only %s differ, got %s" % (sorted(EXPECTED_DIFF), sorted(diff)))
    bc = json.load(open(bco))
    import skyycfg
    ro, rn = old.get("cfgrows") or {}, new.get("cfgrows") or {}
    both = sorted(set(ro) & set(rn) - {"VERSION"})
    vs = lambda v, ver: None if v is None else v.replace(ver, "V")      # DL0 = the default file text: its "# SkyyExploration 0.2.x" header
    check(len(both) >= 10 and all(vs(ro[k], OLD_VERSION) == vs(rn[k], VERSION) for k in both),
          "F: the config rows (CfgRows statics) are identical but for the version: %s" % [k for k in both if vs(ro[k], OLD_VERSION) != vs(rn[k], VERSION)])
    check(sorted(k for k in both if ro[k] != rn[k]) in ([], ["DL0"]), "F: only DL0 (the default file header) carries the version")
    check(ro.get("VERSION") == OLD_VERSION and rn.get("VERSION") == VERSION, "F: CfgRows.VERSION 0.2.1 -> 0.2.2")
    check(sorted(set(rn) - set(ro)) == ["KIT", "SIG_USS", "VTYPES"] and rn.get("KIT") == skyycfg.KIT_VERSION and not set(ro) - set(rn),
          "F: CfgRows gains only the kit 1.1 fields KIT / SIG_USS / VTYPES: %s / %s" % (sorted(set(rn) - set(ro)), sorted(set(ro) - set(rn))))
    for k in CFG_KIT:
        c = bc.get(k)
        check(c is not None and not c.get("gone"), "F: %s (config kit 1.0 -> 1.1): no method gone: %s" % (k, c and c.get("gone")))
    print("F. config kit 1.0 -> %s (tools/skyycfg.py; any rebuild picks it up): %d CfgRows row-table fields identical; new kit methods: %s"
          % (skyycfg.KIT_VERSION, len(both), "; ".join("%s %d" % (k.split("/")[-1][:-6], len(bc[k]["new"])) for k in sorted(CFG_KIT) if k in bc)))
    for k in VERSION_ONLY:
        c = bc.get(k)
        if c is None:
            continue
        check(not c.get("new") and not c.get("gone") and c.get("fields_same") and c.get("version_only"),
              "F: %s: only the version string differs: %s" % (k, c))
    sp = bc.get("com/skyy/explore/SkyyExplorationPlugin.class", {})
    check(sp.get("changed") == ["setup()V"] and not sp.get("new") and not sp.get("gone") and sp.get("fields_same"),
          "F: SkyyExplorationPlugin: only setup() (the ready line) changed: %s" % sp)
    ep = bc.get("com/skyy/explore/ExplorePage.class", {})
    B_SIG = "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;" \
            "Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;Lcom/hypixel/hytale/component/Store;)V"
    H_SIG = "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Ljava/lang/String;)V"
    check(("handleDataEvent" + H_SIG) not in ep.get("changed", []) and ("handleDataEvent" + H_SIG) not in ep.get("gone", []),
          "F: ExplorePage.handleDataEvent unchanged: %s" % ep.get("changed"))
    check(sorted(m.split("(")[0] for m in ep.get("new", [])) == ["card", "msgColor", "nz"] and
          sorted(m.split("(")[0] for m in ep.get("gone", [])) == ["card", "line"] and ep.get("fields_gone") == ["CARD_COLOR [Ljava/lang/String;"],
          "F: ExplorePage: card(..) re-signed, msgColor + nz new, line + CARD_COLOR gone: %s" % dict((x, ep.get(x)) for x in ("new", "gone", "fields_gone")))
    check(set(m.split("(")[0] for m in ep.get("changed", [])) <= {"<clinit>", "build", "overview", "zonesTab", "titlesTab", "checklistTab"},
          "F: ExplorePage: only the markup methods changed: %s" % ep.get("changed"))
    xp = bc.get("com/skyy/explore/AdminPage.class", {})
    for m in ("handleDataEvent" + H_SIG, "jsonStr(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
              "ph(Ljava/lang/String;)Ljava/lang/String;", "clearKeeps()V"):
        check(m not in xp.get("changed", []) and m not in xp.get("gone", []), "F: AdminPage.%s unchanged" % m.split("(")[0])
    check(sorted(m.split("(")[0] for m in xp.get("gone", [])) == ["box", "btn", "gap", "lab", "pager", "row", "sep", "vgap"] and
          sorted(m.split("(")[0] for m in xp.get("new", [])) == ["clip", "nz", "pager", "stColor", "val"] and
          sorted(f.split(" ")[0] for f in xp.get("fields_gone", [])) == ["SBLU", "SG", "SOFF", "SON", "SRED"] and not xp.get("fields_new"),
          "F: AdminPage: the old style helpers / fields gone, pager(.., pages) + clip / nz / val / stColor new: %s"
          % dict((x, xp.get(x)) for x in ("new", "gone", "fields_gone", "fields_new")))
    check(set(m.split("(")[0] for m in xp.get("changed", [])) <= {"build", "lists", "spotsTab", "checkTab", "switches", "islandTab"},
          "F: AdminPage: only the markup methods changed: %s" % xp.get("changed"))
    print("F. class bytes: %d entries identical, differ: %s; methods: %s" % (
        same, ", ".join(sorted(n.split("/")[-1] for n in diff)),
        "; ".join("%s %s" % (n.split("/")[-1][:-6], dict((x, bc[n][x]) for x in ("changed", "new", "gone", "fields_gone") if bc[n][x]))
                  for n in sorted(bc) if n not in VERSION_ONLY | CFG_KIT)))
    print("   version string only: %s" % ", ".join(sorted(n.split("/")[-1][:-6] for n in VERSION_ONLY if n in bc and bc[n].get("version_only"))))
    return finish()


def finish():
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyyExploration %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
