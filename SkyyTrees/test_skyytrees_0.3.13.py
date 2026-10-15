"""SkyyTrees 0.3.13 - harness for THE ABILITY TREE REDESIGN R2 + R3 (tools/trees_0_3_13_patch.py), with the REAL SkyyClasses 0.1.26 jar in
the same JVM. Child JVMs run the game's own JRE with the cached HytaleServer.jar copy, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the
scratch folder. The live save data is only READ and copied into scratch (checked afterwards).

    python SkyyTrees/test_skyytrees_0.3.13.py --dir <empty folder inside tools/dev/scratch/> [--keep]

SECTIONS
  A   load + verify (-Xverify:all) both jars (0.3.13 + 0.3.12)
  CC  class compare 0.3.12 -> 0.3.13: + TreeAbMig / TreeModFn only, structural changes only in the classes the patch names
  X   EXECUTED with the real SkyyClasses 0.1.26 (bridges in one skyy.bridge map):
      X1 the node tables (per class: the 5 ability nodes, one modifier node per SkyyClasses modifier, the hidden slots, the saved ids,
         SkyyClasses' reader list names every one), the 3 AP rows (class.ap.ability / modifier / spine) through TreeCfg.apply
      X2 the rules through TreeClassOps.buy: the free Root (taken by the buy / the tick from class level 1), an ability for 1 AP, a modifier
         needs its ability + 1 AP (no ability-level gate), the A4 pick-one pair, the level gates, a hidden slot, the free spine, Undo, a
         respec clears the grandfather marks
      X3 the bridges: tree:fn:abil (the saved ids), tree:fn:modOwned, SkyyClasses' lineOn / modOk / modSlots / equipped on them, the alt
         pick following A4a / A4b (the loadout rows follow)
      X4 THE PAGE on the real classes: the owned-abilities list, every click path (focus, hold, place, mod into its own row, a wrong row,
         clearMod, a locked tile -> the node selected, combat refusal, the double, Max Up, Back, a tree cell, the probe), the Imbue element
         row (Spellblade), the Assassin's missing A4b column (no cell, no bar), a 4-modifier ability's hidden 5th slot; the old panel
         actions refused
      X5 the one-time profile update with the REAL class:fn:migInfo (History copies in both mods, the change-log line, A4 -> A4b, the
         usable modifiers -> nodes, the grandfather marks, the AP check at two class levels, TreeClass.maint: the update from the tick, the
         free Root, the check + its chat line), the rebirth reset clears the marks
      FZ THE FUZZ: 1000 random 0.3.12 profiles (1-3 classes, random spines / abilities / slots / trunks / paths / junk / retired ids /
         orders / rebirth gates, random SkyyClasses facts, 10 % with no answer first) -> the update: every old node kept or mapped, every
         usable modifier of an owned ability owned, nothing else; the AP check at a random level: paid only while the AP cover them, AP
         never negative but grandfathered, nothing intact before stops being intact; saved + read again = the same state, no second
         SkyyClasses call; a deferred profile keeps its old ids on disk and converts the same way later
      LY  the layout model of every rendered page (list, focus + Lattice, the element row, the Assassin, page 2): every flow container's
          children fit, anchored children stay inside their cell, the root <= 1600 x 980
  RP  every 0.3.11 replant scenario on the 0.3.13 jar
  FX  the critics' fix round (one check per fix, inside X1 / X2 / X4 / X5): an admin's OFF switch on an ability node (+ the old A4 line, the
      M1A-M4B lines logged), the free Root alone = nothing to respec (no coins, nothing armed), the update only after a VERIFIED History
      copy (a blocked copy = the old ids wait, the tick converts later), level 0 = the AP check waits, a throw in the tick's maintenance
      is caught, the AP number from the rows, the A4 pick-one bracket (one drop, column 7), a locked tile opens the node detail, the
      focus view's stats line, the rune icon of every ability node (panel [120..124])
  ST  start twice on a scratch copy of the live Skyy_SkyyTrees (= 0.3.12's start: nothing written)
  Z   the engine-access audit
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, random, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.13", "0.3.12"
PKG = "com.skyy.trees."
CPKG = "com.skyy.classes."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "abiltree2", "tr")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyTrees-%s.jar" % PREV_VERSION)))
CL_JAR = os.path.abspath(arg("--classes", os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.26.jar")))
_saved = list(sys.argv)
sys.argv = [sys.argv[0], "--dir", SCRATCH, "--jar", JAR, "--prev", PREV_JAR]
_spec = importlib.util.spec_from_file_location("test_skyytrees_0_3_12", os.path.join(HERE, "test_skyytrees_0.3.12.py"))
T312 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T312)
sys.argv = _saved
T312.SCRATCH, T312.JAR, T312.PREV_JAR = SCRATCH, JAR, PREV_JAR
T311 = T312.T311
T311.SCRATCH, T311.JAR, T311.PREV_JAR = SCRATCH, JAR, PREV_JAR
T310 = T312.T310
T310.SCRATCH, T310.JAR, T310.PREV_JAR = SCRATCH, JAR, PREV_JAR
LIVE = T310.LIVE
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ============================================================================================================ child: X (+ FZ, the page dumps)
def run_x(out):
    import jpype
    from jpype import JClass, JArray, JString, JObject, JBoolean, JImplements, JOverride
    import skyybuild as B
    import harness_kit as HK
    HK.jvm([B.SERVER_JAR, JAR, CL_JAR], verify=True)
    R = {"checks": [], "notes": [], "pages": {}}

    def ck(c, w):
        R["checks"].append([bool(c), w])
        if not c:
            print("FAIL", w)
    T = lambda n: JClass(PKG + n)
    C = lambda n: JClass(CPKG + n)
    Cls, Ops, Page, Store, Cfg, Data, Mig = T("TreeClass"), T("TreeClassOps"), T("TreePage"), T("TreeStore"), T("TreeCfg"), T("TreeData"), T("TreeAbMig")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Paths, Integer, Long, Boolean = JClass("java.nio.file.Paths"), JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    UUID, ArrayList, Props = JClass("java.util.UUID"), JClass("java.util.ArrayList"), JClass("java.util.Properties")
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)
    me = UUID(0x7ee5, 313)
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    bridge = Store.bridge()

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f
            self.n = 0

        @JOverride
        def apply(self, o):
            self.n += 1
            return self.f(o)
    LV = {"lvl": 30}
    PK = {}
    CB = {"ms": 0}
    bridge.put("skill:fn:level", Fn(lambda o: Integer.valueOf(LV["lvl"])))
    bridge.put("profile:fn:key", Fn(lambda o: JString(PK.get(str(o), str(o)))))
    bridge.put("skill:fn:combat", Fn(lambda o: Long.valueOf(CB["ms"])))
    COINS = Fn(lambda o: Boolean.TRUE)   # fix round: counted (the free Root alone takes no coins)
    bridge.put("coins:fn:take", COINS)

    def setcls(cn):
        bridge.put("class:" + str(me), cn)
        bridge.put("profile:class:" + str(me), cn)
    setcls("Mage")
    home = os.path.join(SCRATCH, "x-home")
    shutil.rmtree(home, ignore_errors=True)
    os.makedirs(os.path.join(home, "classes", "players"), exist_ok=True)
    LOGC = JClass("com.hypixel.hytale.logger.HytaleLogger")
    CC_ = C("ClassCfg")
    CC_.LOG = LOGC.get("SkyyClasses")
    CC_.FILE = Paths.get(os.path.join(home, "classes", "config.properties"))
    R["notes"].append("SkyyClasses config: " + str(CC_.load())[:120])
    C("ClassStore").DIR = Paths.get(os.path.join(home, "classes", "players"))
    AS = C("AbilStore")
    AS.DIR = Paths.get(os.path.join(home, "classes", "abilities"))
    AS.SYNC = True
    A = C("Abil")
    REALMIG0 = C("AbilMigFn")()
    REALMIG = Fn(lambda o: REALMIG0.apply(o))   # the real class:fn:migInfo, counted
    FNS = {"class:fn:abilPanel": C("AbilPanelFn")(), "class:fn:abilMods": C("AbilModsFn")(), "class:fn:abilDo": C("AbilDoFn")(),
           "class:fn:abilUnlock": C("AbilUnlockFn")(), "class:fn:migInfo": REALMIG}
    for k_, v_ in FNS.items():
        bridge.put(k_, v_)
    pdir = os.path.join(home, "trees", "players")
    os.makedirs(pdir, exist_ok=True)
    Store.DIR = Paths.get(pdir)
    Cfg.LOG = LOGC.get("SkyyTrees")
    Cfg.CLASS_ON = True
    m_ = re.search(rb"Class\.Mage\.A1[ -~]*", zipfile.ZipFile(CL_JAR).read("com/skyy/classes/SkyyClassesPlugin.class"))
    reads = m_.group(0).decode() if m_ else ""
    bridge.put("tree:reads:SkyyClasses", reads)
    bridge.put("tree:fn:abil", T("TreeAbilFn")())
    bridge.put("tree:fn:modOwned", T("TreeModFn")())
    NN, NC = int(Cls.NN), int(Cls.NC)
    CLASSES = [str(x) for x in Cls.CLASSES]
    NID = [str(x) for x in Cls.NID]
    MIX = dict((n, i) for i, n in enumerate(NID))
    CID = [str(x) for x in Cls.CID]
    NROLE = [int(x) for x in Cls.NROLE]
    NPAR1 = [int(x) for x in Cls.NPAR1]
    ABL = ["A1", "A2", "A3", "A4a", "A4b"]
    ci = CLASSES.index("Mage")
    NT = int(T("TreeDefs").NT)

    def fresh(cn="Mage"):
        Store.DATA.clear()
        Store.DIRTY.clear()
        AS.TREEC.clear()
        d = Data()
        d.tree2 = True
        Store.DATA.put(PK.get(str(me), str(me)), d)
        return d

    def own(d, c=None):
        c = ci if c is None else c
        return [CID[c * NN + n] for n in range(NN) if bool(d.cown[c * NN + n])]

    def sidx(c, sid):
        return int(Cls.nodeIdx(c, sid))

    def render(page, tag=None):
        b, ev = UCB(), UEB()
        err = None
        try:
            page.build(None, b, ev, None)
        except Exception as e:
            err = str(e)[:300]
        cmds = [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]
        texts = []
        for c in b.getCommands():
            if c.data is None:
                continue
            try:
                v = json.loads(str(c.data))
                texts += [str(x) for x in (v.values() if isinstance(v, dict) else [v])]
            except Exception:
                texts.append(str(c.data))
        evs = [str(e.data) for e in ev.getEvents() if e.data is not None]
        if tag:
            R["pages"][tag] = {"err": err, "cmds": cmds}
        return err, texts, evs, cmds

    def bound(evs, e):
        return any('"%s"' % e in x for x in evs)

    def click(page, a):
        try:
            page.handleDataEvent(None, None, '{"a":"%s"}' % a)
            return None
        except Exception as e:
            return str(e)[:200]
    AD, AMD, CD = C("AbilDefs"), C("AbilModDefs"), C("ClassDefs")
    CLN = [str(x) for x in CD.NAMES]

    # ================================================================================================ X1 the tables + the AP rows
    bad = []
    for c, cn in enumerate(CLASSES):
        cc = CLN.index(cn)
        for t, lid in enumerate(ABL):
            ai = int(AD.of(cc, t))
            an = MIX[lid]
            if bool(Cls.hidden(c, an)) != (ai < 0):
                bad.append("%s %s hidden %s" % (cn, lid, bool(Cls.hidden(c, an))))
            mods = [str(AMD.MID[int(AMD.at(ai, k))]) for k in range(int(AMD.count(ai)))] if ai >= 0 else []
            if ai >= 0 and (str(Cls.CABID[c * NN + an]) != str(AD.IDS[ai]) or CID[c * NN + an] != lid):
                bad.append("%s %s ability id %s" % (cn, lid, Cls.CABID[c * NN + an]))
            for k in range(5):
                m = MIX["%sm%d" % (lid, k + 1)]
                hid = bool(Cls.hidden(c, m))
                if hid != (k >= len(mods)):
                    bad.append("%s %sm%d hidden %s" % (cn, lid, k + 1, hid))
                elif not hid and (CID[c * NN + m] != "%s.%s" % (lid, mods[k]) or str(Cls.CMOD[c * NN + m]) != mods[k] or NPAR1[m] != an or NROLE[m] != 3):
                    bad.append("%s %s slot %d = %s" % (cn, lid, k + 1, CID[c * NN + m]))
    ck(not bad and NN == 62, "X1: per class the 5 ability nodes + one modifier node per SkyyClasses modifier (saved id <node>.<Mod>), the rest hidden: %s" % bad[:5])
    keys = set(reads.split(","))
    miss = [("Class.%s.%s" % (cn, CID[c * NN + n])) for c, cn in enumerate(CLASSES) for n in range(NN) if NROLE[n] in (2, 3) and not bool(Cls.hidden(c, n))
            and ("Class.%s.%s" % (cn, CID[c * NN + n])) not in keys]
    ck(not miss and len(reads) > 1000, "X1: SkyyClasses 0.1.26's tree:reads:SkyyClasses names every ability + modifier node (%d keys): %s" % (len(keys), miss[:4]))
    ck(not [k for k in keys if re.search(r"\.M[1-4][AB]$|\.A4$", k)], "X1: ... and no old A4 / M1A-M4B key")
    pz = Props()
    for k_, v_ in (("class.ap.ability", "2"), ("class.ap.modifier", "3"), ("class.ap.spine", "1"), ("class.nodes.Mage.A1", "true,0,5"), ("class.nodes.Mage.P1", "true,5,4")):
        pz.setProperty(k_, v_)
    Cfg.apply(pz)
    capv = [int(Cfg.C_AP[ci * NN + MIX[x]]) for x in ("A1", "A4b", "A1m1", "P1", "X2", "P4", "ROOT", "T1", "PA5")]
    ck(capv == [2, 2, 3, 1, 1, 1, 0, 1, 4] and int(Cfg.AP_IGN) == 1, "X1: the AP rows read live (ability 2, modifier 3, spine 1; the Root free; an old A1 line / a P1 AP not read): %s ign %d" % (capv, int(Cfg.AP_IGN)))
    Cfg.apply(Props())
    capv = [int(Cfg.C_AP[ci * NN + MIX[x]]) for x in ("A1", "A4b", "A1m1", "P1", "X2", "P4", "ROOT", "T1", "T6", "PA1", "LE")]
    ck(capv == [1, 1, 1, 0, 0, 0, 0, 1, 3, 2, 3], "X1: no lines = the defaults (ability 1, modifier 1, spine 0, Root 0, trunk / paths unchanged): %s" % capv)
    Cfg.CLASS_ON = True
    Kit = T("TreeKit")
    w1 = Kit.checkClassNode("class.nodes.Mage[M1B]", "true|0|2")
    w2 = Kit.checkClassNode("class.nodes.Mage[P1]", "true|5|2")
    w3 = Kit.checkClassNode("class.nodes.Mage[P1]", "true|5|0")
    ck(w1 is not None and "was an ability slot node" in str(w1) and w2 is not None and "spine node" in str(w2) and w3 is None,
       "X1: the Server Setup entry check: an old M1B line / a spine AP / the default: %s | %s | %s" % (w1, w2, w3))
    # FX (critic A3): an ability node keeps an admin's OFF switch (its own line; the 0.3.12 A4 line = both alts); old M lines are logged, not read
    pz = Props()
    for k_, v_ in (("class.nodes.Mage.A1", "false,0,0"), ("class.nodes.Mage.A4", "false,0,0"), ("class.nodes.Mage.M2A", "false,0,0"), ("class.nodes.Mage.M3B", "true,0,0")):
        pz.setProperty(k_, v_)
    Cfg.apply(pz)
    Cfg.CLASS_ON = True
    onv = [bool(Cls.on(ci, MIX[x])) for x in ("A1", "A2", "A3", "A4a", "A4b", "A1m1")]
    ck(onv == [False, True, True, False, False, True] and int(Cfg.AB_OFF) == 3 and int(Cfg.M_IGN) == 1 and int(Cfg.C_AP[ci * NN + MIX["A1"]]) == 1,
       "FX A3: A1=false switches Meteor's node off, the old A4=false both alts (3 off), an old M2A=false is counted as not read (1): %s %d %d" % (onv, int(Cfg.AB_OFF), int(Cfg.M_IGN)))
    d_ = Data()
    d_.tree2 = True
    Store.DATA.put(str(me), d_)
    rq = str(Ops.buy(me, d_, ci, 30, MIX["A1"], ArrayList(), False))
    ck(not bool(d_.cown[ci * NN + MIX["A1"]]) and "off" in rq.lower(), "FX A3: ... nobody can buy the switched-off ability: %s" % rq)
    Store.DATA.clear()
    wa = Kit.checkClassNode("class.nodes.Mage[A1]", "false|0|0")
    wb = Kit.checkClassNode("class.nodes.Mage[A4]", "false|0|0")
    ck(wa is not None and "only its on / off is read" in str(wa) and wb is not None and "both A4a and A4b" in str(wb), "FX A3: the entry check explains it: %s | %s" % (wa, wb))
    Cfg.apply(Props())
    Cfg.CLASS_ON = True
    ck(all(bool(Cls.on(ci, MIX[x])) for x in ("A1", "A4a", "A4b")) and int(Cfg.AB_OFF) == 0, "FX A3: no line = every ability node on")
    lvl_w = Kit.checkClassLevel("class.minLevel[Mage.A1m1]", "5")
    ck(lvl_w is not None and "modifier node" in str(lvl_w), "X1: a class level on a modifier node is asked about: %s" % lvl_w)

    # ================================================================================================ X2 the rules
    undo = ArrayList()
    LV["lvl"] = 1
    d = fresh()
    r = str(Ops.buy(me, d, ci, 1, MIX["A1"], undo, False))
    ck(set(own(d)) == {"ROOT", "A1"} and "1 AP spent - 0 left" in r, "X2: a Lv 1 Mage buys Meteor (A1) for 1 AP; the Root came free with it: %s %s" % (own(d), r))
    r = str(Ops.buy(me, d, ci, 1, MIX["A1m1"], undo, False))
    ck("A1.Power" not in own(d) and "needs 1 AP - you have 0" in r, "X2: Power+ for Meteor needs 1 AP: %s" % r)
    LV["lvl"] = 4
    r = str(Ops.buy(me, d, ci, 4, MIX["A1m1"], undo, False))
    ck("A1.Power" in own(d) and r.startswith("Unlocked Power+!"), "X2: at Lv 4 (3 AP) Power+ is bought - no Meteor level needed: %s" % r)
    r = str(Ops.buy(me, d, ci, 4, MIX["A2m1"], undo, False))
    ck("A2.Power" not in own(d) and "Mana Barrier" in r, "X2: a modifier without its ability node is refused: %s" % r)
    r = str(Ops.buy(me, d, ci, 4, MIX["A2"], undo, False))
    ck("A2" not in own(d) and "10" in r, "X2: Mana Barrier keeps its class level gate (10): %s" % r)
    LV["lvl"] = 30
    r = str(Ops.buy(me, d, ci, 30, MIX["A4a"], undo, False))
    r2 = str(Ops.buy(me, d, ci, 30, MIX["A4b"], undo, False))
    ck("A4a" in own(d) and "A4b" not in own(d) and "pick one of the two" in r2, "X2: the A4 alts - Starfall (A4a) bought, Arcane Beam (A4b) blocked: %s" % r2)
    ck(str(Cls.cardText(Cls.ownOf(d, ci), Cls.intact(d, ci), ci, MIX["A4b"], 30, 10, 0)) == "Pick one", "X2: ... its cell says Pick one")
    r = str(Ops.buy(me, d, ci, 30, MIX["A3m5"], undo, False))
    ck(r == "No such node", "X2: Frost Nova has 4 modifiers - its 5th slot does not exist: %s" % r)
    r = str(Ops.buy(me, d, ci, 30, MIX["P1"], undo, False))
    ck("P1" in own(d) and "0 AP spent" in r, "X2: the spine is free (class.ap.spine 0): %s" % r)
    r = str(Ops.undo(me, d, ci, undo, False))
    ck("P1" not in own(d) and r.startswith("Undo done"), "X2: Undo the newest unlock: %s" % r)
    undo.clear()
    undo.add(Integer.valueOf(ci * NN + MIX["A1"]))
    r = str(Ops.undo(me, d, ci, undo, False))
    ck("A1" in own(d) and "still needs it" in r, "X2: Undo of Meteor while Power+ is owned is refused: %s" % r)
    ck(str(Ops.typeLine(ci, MIX["A1m1"])) == "Modifier - 1 AP" and str(Ops.typeLine(ci, MIX["A1"])) == "Ability - 1 AP" and str(Ops.typeLine(ci, MIX["P1"])).endswith("free"),
       "X2: the detail's type lines: %s / %s / %s" % (Ops.typeLine(ci, MIX["A1m1"]), Ops.typeLine(ci, MIX["A1"]), Ops.typeLine(ci, MIX["P1"])))
    d.cgf[ci * NN + MIX["A1"]] = True
    ck(str(Cls.cardText2(d, Cls.ownOf(d, ci), Cls.intact(d, ci), ci, MIX["A1"], 30, 5, 2)) == "Kept" and str(Ops.costLine(d, 2, ci, MIX["A1"])).startswith("Cost: free - kept"),
       "X2: a grandfathered node's cell says Kept, its cost line free")
    # FX2 (second critics): a modifier cell names its modifier (owned / waiting for its ability); a buyable one keeps "Unlock N AP"
    ow_, it_ = Cls.ownOf(d, ci), Cls.intact(d, ci)
    cx_ = [str(Cls.cardText2(d, ow_, it_, ci, MIX[n_], 30, 5, s_)) for n_, s_ in (("A1m1", 2), ("A1m3", 1), ("A2m1", 0))]
    ck(cx_ == ["Power+", "Unlock 1 AP", str(Cls.name(ci, MIX["A2m1"]))] and str(Cls.cardText2(d, ow_, it_, ci, MIX["A2"], 30, 5, 0)) != str(Cls.name(ci, MIX["A2"])),
       "FX2: modifier cells: owned = its name, buyable = Unlock 1 AP, waiting for Mana Barrier = its name; an ability cell keeps its state word: %s" % cx_)
    sp0 =int(Cls.spent(Cls.intact(d, ci), ci, Cls.gfOf(d, ci)))
    d.cgf[ci * NN + MIX["A1"]] = False
    sp1 = int(Cls.spent(Cls.intact(d, ci), ci, Cls.gfOf(d, ci)))
    ck(sp1 == sp0 + 1, "X2: a grandfathered node costs 0 (spent %d -> %d)" % (sp0, sp1))
    d.cgf[ci * NN + MIX["A1"]] = True
    d.cgfChk[ci] = True
    d.crespecAt[ci] = 0
    d.cold[ci] = "A4,M1A"   # FX2: 0.3.12 ids still waiting for the update
    r = str(Ops.respec(me, d, ci, 30, False))
    ck(r.startswith("Respec done") and not any(bool(d.cgf[ci * NN + n]) for n in range(NN)) and not bool(d.cgfChk[ci]) and own(d) == [],
       "X2: a respec refunds everything and clears the grandfather marks: %s" % r)
    ck(d.cold[ci] is None, "FX2: ... and drops the 0.3.12 ids still waiting for the update (no old A4 comes back): %s" % d.cold[ci])

    # FX (critic A2): only the free Root owned -> "Nothing to respec" (no coins taken, no cooldown); the page does not arm
    d = fresh()
    LV["lvl"] = 30
    Store.rootOwn(d, ci)
    coins0 = COINS.n
    d.crespecAt[ci] = 0
    r = str(Ops.respec(me, d, ci, 30, False))
    ck(r.startswith("Nothing to respec") and COINS.n == coins0 and int(d.crespecAt[ci]) == 0 and bool(d.cown[ci * NN]),
       "FX A2: the free Root alone is nothing to respec (no coins, no cooldown): %s" % r)
    pgr = Page(pr, NT)
    click(pgr, "trrespec")
    ck(str(pgr.msg).startswith("Nothing to respec") and int(pgr.armT) == -1 and COINS.n == coins0, "FX A2: ... the page's Respec says so instead of arming: %s" % pgr.msg)
    Ops.buy(me, d, ci, 30, MIX["P1"], undo, False)
    click(pgr, "trrespec")
    ck(int(pgr.armT) == NT and str(pgr.msg).startswith("Click Respec again"), "FX A2: with a bought node the first click arms as before: %s" % pgr.msg)

    # ================================================================================================ X3 the bridges
    d = fresh()
    LV["lvl"] = 30
    for n_ in ("A1", "A1m1", "A1m2", "A2", "A4b", "A4bm4"):
        Ops.buy(me, d, ci, 30, MIX[n_], undo, False)
    csv = str(T("TreeAbilFn")().apply(me))
    ck(set(["ROOT", "A1", "A1.Power", "A1.Radius", "A2", "A4b", "A4b.Pierce"]) <= set(x.split("=")[0] for x in csv.split(",")) and "M1A" not in csv, "X3: tree:fn:abil = the saved ids: %s" % csv)
    MO = T("TreeModFn")()
    mo = [MO.apply(JArray(JObject)([me, JString(a_), JString(m_)])) for a_, m_ in (("Meteor", "Power"), ("A1", "Radius"), ("Meteor", "Split"), ("ArcaneBeam", "Pierce"), ("ManaBarrier", "Ward"), ("Nope", "Power"))]
    ck([bool(x) for x in mo] == [True, True, False, True, False, False], "X3: tree:fn:modOwned (ability id or node id): %s" % [str(x) for x in mo])
    Cfg.CLASS_ON = False
    ck(MO.apply(JArray(JObject)([me, JString("Meteor"), JString("Power")])) is None, "X3: class trees off -> null (no gate)")
    Cfg.CLASS_ON = True
    METEOR, MANAB, STARF, BEAM = int(AD.find("Meteor")), int(AD.find("ManaBarrier")), int(AD.find("Starfall")), int(AD.find("ArcaneBeam"))
    ck(bool(A.lineOn(csv, METEOR)) and bool(A.lineOn(csv, BEAM)) and not bool(A.lineOn(csv, STARF)) and not bool(A.lineOn(csv, int(AD.find("FrostNova")))),
       "X3: SkyyClasses: Meteor + Arcane Beam (A4b) usable, Starfall (A4a) + Frost Nova not")
    ck(bool(A.modOk(csv, METEOR, 0, 1)) and bool(A.modOk(csv, METEOR, 1, 1)) and not bool(A.modOk(csv, METEOR, 2, 25)) and bool(A.modOk(None, METEOR, 2, 6)) and not bool(A.modOk(None, METEOR, 2, 5)),
       "X3: modOk - the tree's node at Lv 1, a missing node never (even at Lv 25); no tree = the ability level (mods.unlock)")
    ck(int(A.modSlots(csv, METEOR)) == 2 and int(A.modSlots(csv, STARF)) == 0 and int(A.slotsOf(csv, STARF, str(me))) == 0, "X3: the 2 slots come with the ability node")
    kme = str(me)
    AS.set(kme, JArray(JString)(["e.Meteor", "u.Meteor"]), JArray(JString)(["Power,Split", "0"]))
    eqs = [int(x) for x in A.equipped(AS.load(kme), METEOR, 1, 2, JString(csv))]
    ck(eqs[0] >= 0 and eqs[1] == -1, "X3: equipped(): Power+ works at Meteor Lv 1, Split (no node) does not: %s" % eqs)
    AS.TREEC.clear()
    pk0 = str(AS.pick(kme))
    A.treeCsv(me)
    sl = [str(x) for x in AS.slots(kme, C("ClassStore").classIndex(me))]
    ck(str(AS.pick(kme)) == "B" and "ArcaneBeam" in sl and "Starfall" not in sl, "X3: the alt pick follows the tree (A4b -> B, was %s); the loadout rows follow: %s" % (pk0, sl))

    # ================================================================================================ X4 THE PAGE
    LV["lvl"] = 30
    d = fresh()
    AS.set(kme, JArray(JString)(["e.Meteor", "u.Meteor", "alt", "p1", "p2", "a1", "a2"]), JArray(JString)([None, "40", "A", None, None, None, None]))
    for n_ in ("A1", "A1m1", "A1m2", "A2"):
        Ops.buy(me, d, ci, 30, MIX[n_], undo, False)
    page = Page(pr, NT)
    err, texts, evs, cmds = render(page, "mage-list")
    ck(err is None, "X4: the class tab builds: %s" % err)
    ck("Meteor  Lv 3" in texts and "Mana Barrier  Lv 1" in texts and bound(evs, "tyca0") and bound(evs, "tyca1") and not bound(evs, "tyca2") and not bound(evs, "tyca3"),
       "X4: the Abilities column lists ONLY the owned abilities (Meteor Lv 3, Mana Barrier): %s" % [t for t in texts if "Lv" in t][:6])
    ck("Ability 2 key" in texts and "Ability 3 key" in texts and [t for t in texts if t.endswith("to Lv 4")], "X4: each card: the key it sits on + uses to the next level")
    ck(bound(evs, "trc%d" % (MIX["A1m3"] + 1)) and not bound(evs, "trc%d" % (MIX["A3m5"] + 1)), "X4: the graph has Split's node, not Frost Nova's missing 5th slot")
    ck(click(page, "tyca0") is None and bool(page.amode) and str(page.afoc) == "Meteor" and int(page.hk) == 1 and str(page.msg).startswith("Ability: holding Meteor"),
       "X4: clicking Meteor focuses + holds it: %s" % page.msg)
    err, texts, evs, cmds = render(page, "mage-focus")
    ck(err is None and "Meteor  Lv 3" in texts and "Ability 2 key - held" in texts, "X4: the focus card: %s" % err)
    tiles = [t for t in texts if t.startswith(("Power+", "Radius+", "Split", "Lingering", "Echo"))]
    ck("Power+ Lv 1" in tiles and "Radius+ Lv 1" in tiles and "Split" in tiles and len([e for e in range(5) if bound(evs, "tyft%d" % e)]) == 5
       and [t for t in texts if t.startswith("Not unlocked - node A1.Split in the tree (1 AP)")],
       "X4: its 5 modifier tiles (2 owned, 3 'Not unlocked - node ... in the tree'): %s" % tiles)
    # FX2 (second critics): the focus texts are the short forms that fit (asserted against the font metrics at build time)
    lb_ = [t for t in texts if t.startswith("Level bonus: ")]
    ck(lb_ and "A use" not in lb_[0] and not [t for t in tiles if "buy it in the tree" in t or " - held" in t], "FX2: the level bonus line is short (%s); tile names have no long tails" % lb_[:1])
    ck(not bound(evs, "tyca1") and bound(evs, "tyfb") and bound(evs, "tyfc"), "X4: the other abilities hide; Back + the focus card bound")
    stl = [t for t in texts if " Mana + " in t and "cooldown" in t]
    ck(stl and [t for t in texts if t.startswith("Level bonus: ") and "3 s" not in t], "FX C7: the focus view shows the stats line (Mana + Stamina + cooldown) and the level bonus: %s" % stl[:1])
    ck("Ability 2 key - Meteor" in texts and "Ability 3 key - Mana Barrier" in texts and "Crouch + Ability 2 - empty" in texts and "Crouch + Ability 3 - empty" in texts,
       "X4: the Lattice: 4 rows (keys + what sits there)")
    ck(all(bound(evs, "tyla%d" % r_) for r_ in range(4)) and all(bound(evs, "tylm%d" % q_) for q_ in (0, 1, 4, 5, 8, 9, 12, 13)) and not bound(evs, "tylm2"),
       "X4: every ability slot + 2 modifier slots per row bound (no slot 3 without rebirths)")
    ck(texts.count("Empty") == 4 and texts.count("Closed") == 4, "X4: the open slots say Empty (Meteor, Mana Barrier), the empty rows Closed")
    click(page, "tyla3")
    sl = [str(x) for x in AS.slots(kme, C("ClassStore").classIndex(me))]
    ck(str(page.msg).startswith("Done: Meteor is on crouch + Ability 3") and sl[3] == "Meteor" and sl[0] == "Starfall" and int(page.hk) == 0,
       "X4: hold Meteor + click the crouch + Ability 3 slot = it goes there (the empty row's Starfall trades places): %s %s" % (page.msg, sl))
    err, texts, evs, cmds = render(page)
    ck("Crouch + Ability 3 - Meteor" in texts and "Ability 2 key - empty" in texts, "X4: the Lattice shows the new row")
    click(page, "tyft0")
    ck(int(page.hk) == 2 and str(page.hmod) == "Power" and str(page.msg).startswith("Ability: holding Power+"), "X4: a tile holds that modifier: %s" % page.msg)
    click(page, "tylm12")
    ck(str(page.msg) == "Done: Meteor: slot 1 Power+, slot 2 empty." and str(AS.load(kme).getProperty("e.Meteor")) == "Power," and int(page.hk) == 0,
       "X4: ... then a modifier slot of Meteor's row = equipped (saved in SkyyClasses' file): %s" % page.msg)
    click(page, "tyft1")
    click(page, "tylm4")
    ck(str(page.msg).startswith("Ability: Radius+ goes in Meteor's own row") and int(page.hk) == 2, "X4: a modifier slot of ANOTHER row is refused: %s" % page.msg)
    click(page, "tylm13")
    ck(str(page.msg) == "Done: Meteor: slot 1 Power+, slot 2 Radius+.", "X4: Radius+ into slot 2: %s" % page.msg)
    click(page, "tylm12")
    ck(str(page.msg) == "Done: Meteor: slot 1 empty, slot 2 Radius+." and str(AS.load(kme).getProperty("e.Meteor")) == ",Radius", "X4: a filled slot clicked with nothing held empties it: %s" % page.msg)
    click(page, "tylm12")
    ck(str(page.msg).startswith("Ability: click a modifier tile first"), "X4: an empty slot with nothing held says what to do: %s" % page.msg)
    click(page, "tyft2")
    ck("node A1.Split" in str(page.msg) and int(page.csel) == MIX["A1m3"] and int(page.cpage) == 0 and int(page.hk) == 0,
       "X4: a locked tile names its node and selects it in the graph: %s" % page.msg)
    err, texts, evs, cmds = render(page)
    ck(not bool(page.amode) and "Split  (A1.Split)" in texts and bound(evs, "trbuy"),
       "FX C8: ... and leaves the focus: the node detail with Unlock shows at once (%s)" % [t for t in texts if "A1.Split" in t][:2])
    page.amode = True
    page.afoc = "Meteor"
    page.hk = 0
    CB["ms"] = 5000
    click(page, "tyfc")
    click(page, "tyla0")
    ck("out of combat" in str(page.msg) and [str(x) for x in AS.slots(kme, C("ClassStore").classIndex(me))][3] == "Meteor", "X4: in combat the loadout does not change: %s" % page.msg)
    err, texts, evs, cmds = render(page)
    ck([t for t in texts if t.startswith("In combat - change your loadout out of combat")], "X4: the Lattice says so")
    CB["ms"] = 0
    AS.set(kme, JArray(JString)(["m.Meteor.Power"]), JArray(JString)(["12"]))
    click(page, "tyft0")
    click(page, "tylm12")
    click(page, "tyft0")
    click(page, "tylm13")
    ck(str(page.msg) == "Done: Meteor: slot 1 Power+, slot 2 Power+.", "X4: Power+ Lv 2 doubles into both slots: %s" % page.msg)
    AS.set(kme, JArray(JString)(["rb.pick.Meteor"]), JArray(JString)(["1"]))
    page.hk = 0
    err, texts, evs, cmds = render(page, "mage-maxup")
    ck(bound(evs, "tymx") and [t for t in texts if t.startswith("Rebirth: 1 upgrade")], "X4: a rebirth upgrade shows Max Up in the focus view")
    click(page, "tymx")
    ck(str(page.msg).startswith("Ability: hold a modifier first"), "X4: Max Up needs a held modifier: %s" % page.msg)
    click(page, "tyft0")
    click(page, "tymx")
    ck(str(page.msg).startswith("Done: Power+ of Meteor can now reach modifier Lv") and str(AS.load(kme).getProperty("rb.modmax.Meteor.Power")) == "1",
       "X4: Max Up places the upgrade on the held modifier: %s" % page.msg)
    click(page, "tyfc")
    ck(int(page.hk) == 1, "X4: the focus card holds the ability")
    click(page, "tyfc")
    ck(int(page.hk) == 0 and str(page.msg) == "Ability: nothing held", "X4: ... a second click lets go")
    click(page, "tyfb")
    ck(not bool(page.amode) and str(page.msg) == "Ability: showing all your abilities", "X4: Back shows every owned ability again: %s" % page.msg)
    click(page, "tyca1")
    click(page, "trc%d" % (MIX["T1"] + 1))
    ck(not bool(page.amode) and int(page.hk) == 0 and int(page.csel) == MIX["T1"], "X4: a tree cell leaves the focus (node detail)")
    old_r = [str(Cls.ado(me, a_, "0", "1", JString(csv))) for a_ in ("swap", "pick", "equip", "unequip")]
    ck(all(x.startswith("-This ability panel changed in SkyyClasses 0.1.26") for x in old_r), "X4: the 0.3.12 actions are refused: %s" % old_r[0])
    pp = Page(pr, NT)
    pp.probe = True
    pp.pci = ci
    pp.pd = Ops.probeData(ci)
    r_ = str(pp.abilEv(me, pp.pd, ci, 30, "focus", 3))
    r2_ = str(pp.abilEv(me, pp.pd, ci, 30, "slot", 0))
    ck(r_.startswith("Ability: holding Meteor") and "off in the probe" in r2_, "X4: the probe may look (%s) but never change (%s)" % (r_[:40], r2_))
    err, texts, evs, cmds = render(pp, "probe")
    ck(err is None, "X4: the probe page builds: %s" % err)
    # the Spellblade's Imbue element row
    setcls("Spellblade")
    cs = CLASSES.index("Spellblade")
    d = fresh()
    for n_ in ("A1", "A2", "A2m1"):
        r_ = str(Ops.buy(me, d, cs, 30, MIX[n_], undo, False))
    page = Page(pr, NT)
    err, texts, evs, cmds = render(page)
    row_imb = [i_ for i_ in range(4) if bound(evs, "tyca%d" % i_)]
    ck(len(row_imb) == 2, "X4: a Spellblade with Arcane Breach + Elemental Imbue lists 2 abilities: %s" % row_imb)
    o_ = C("AbilPanelFn")().apply(me)
    imb = int(o_[111])
    click(page, "tyca%d" % imb)
    err, texts, evs, cmds = render(page, "spellblade-focus")
    ck(err is None and [t for t in texts if t.startswith("Imbue element: Fire")] and bound(evs, "tymat"), "X4: Imbue's row has the element picker: %s" % [t for t in texts if "element" in t.lower()][:2])
    att0 = str(AS.load(kme).getProperty("att1"))
    click(page, "tymat")
    ck(str(page.msg).startswith("Done: ") and str(AS.load(kme).getProperty("att1")) != att0, "X4: Change -> the next element (attune): %s" % page.msg)
    # the Assassin: no A4b column (no cell, no bar to it)
    setcls("Assassin")
    ca = CLASSES.index("Assassin")
    d = fresh()
    page = Page(pr, NT)
    err, texts, evs, cmds = render(page, "assassin-p1")
    roots, byid = T312.build_tree(cmds)
    ck(err is None and not bound(evs, "trc%d" % (MIX["A4b"] + 1)) and bound(evs, "trc%d" % (MIX["A4a"] + 1)), "X4: the Assassin's tree: A4a (Vanishing Act), no A4b cell")
    ck(byid.get("SkyyTrCS17") is not None and not byid["SkyyTrCS17"]["kids"] and byid.get("SkyyTrCS16") is not None and byid["SkyyTrCS16"]["kids"]
       and byid.get("SkyyTrCS15") is not None and byid["SkyyTrCS15"]["kids"], "X4: ... A4b's cell (row 1 column 8) stays empty; the bracket + A4a are drawn")
    ck("SkyyTrCG16" not in byid, "FX C5: ... the bracket's right arm into the missing A4b is not drawn (no right-gap stub at row 1 column 7)")
    setcls("Mage")
    d = fresh()
    page = Page(pr, NT)
    err, texts, evs, cmds = render(page, "mage-empty")
    roots, byid = T312.build_tree(cmds)
    ck(byid.get("SkyyTrCS17") is not None and byid["SkyyTrCS17"]["kids"] and "SkyyTrCG16" in byid and "SkyyTrCG15" in byid and "SkyyTrCD7" in byid,
       "X4: the Mage's A4 pair: A4b drawn, the bracket's two arms (right-gap stubs at columns 6 + 7) and the drop from row 0 column 7")
    sarms = [int(Cls.SARMS[k_]) for k_ in (7, 8, 16)]
    ck(sarms == [2 | 8, 0, 1 | 2 | 4] and [int(Cls.SK[k_]) for k_ in (15, 16, 17)] == [1, 4, 1],
       "FX C5: the pick-one bracket: ROOT's bar turns down at row 0 column 7, ONE drop into a junction at row 1 column 7 with arms into A4a (6) and A4b (8): %s" % sarms)
    ck(str(Page.cicon(ci, MIX["A4b"], JArray(JString)(["", "", "", "", "SkyyAbility_TestRune"]))) == "SkyyAbility_TestRune" and str(Page.cicon(ci, MIX["A4b"], JArray(JString)(["", "", "", "", ""]))) == str(Cls.icon(ci, MIX["A4b"])),
       "FX C9: an ability node shows the rune icon the panel names for it (the unpicked alt too), else its table icon")
    o_ = C("AbilPanelFn")().apply(me)
    ck(len(o_) == 129 and all(o_[120 + t_] is not None for t_ in range(5)), "FX C9: the panel has 129 fields, [120..124] = the rune icon per ability node: %s" % [str(o_[120 + t_]) for t_ in range(5)])
    pz = Props()
    pz.setProperty("class.ap.ability", "2")
    Cfg.apply(pz)
    Cfg.CLASS_ON = True
    err, texts, evs, cmds = render(page)
    ck([t for t in texts if t.startswith("No abilities yet - buy A1 in the tree (page 1, 2 AP)")] and str(Cls.apEach()) == "abilities 2 AP, modifiers 1 AP",
       "FX C3: the AP number in the texts follows the rows (ability 2): %s" % str(Cls.apEach()))
    Cfg.apply(Props())
    Cfg.CLASS_ON = True
    ck(str(Cls.apEach()) == "1 AP each", "FX C3: ... back to 1 AP each")
    ck([t for t in texts if t.startswith("No abilities yet")], "X4: no ability owned -> the column says how to get one")
    page.cpage = 1
    render(page, "mage-p2")

    # ================================================================================================ X5 the update with the real class:fn:migInfo
    k2 = str(me) + "-p3"
    AS.set(k2, JArray(JString)(["u.Meteor", "e.ManaBarrier", "alt"]), JArray(JString)(["200", "Ward,", "B"]))
    C("AbilSave").write(k2)
    tf = os.path.join(pdir, k2 + ".properties")
    open(tf, "w").write("name=Skyy\nv=2\nClass.Mage=ROOT,P1,P2,X1,P3,P4,A1,A2,M1A,M1B,A4,M4A,T1\nClass.Mage.order=ROOT,P1,A1,M1A,A4,T1\nClass.Priest=ROOT,A1,M1A\n")
    raw0 = open(tf, "rb").read()
    info = str(REALMIG.apply(JString(k2)))
    ck(info.startswith("alt=B") and "Meteor=Power,Radius,Split" in info and "ManaBarrier=Ward" in info, "X5: class:fn:migInfo answers the alt + the usable modifiers (level / equipped): %s" % info[:120])
    hist_c = os.path.join(home, "classes", "history", "abiltree2", k2 + ".properties")
    ck(os.path.isfile(hist_c), "X5: SkyyClasses copied its abilities file into history/abiltree2 first")
    Store.DATA.clear()
    d = Store.readFile(JString(k2))
    o2 = own(d)
    ck(set(o2) == {"ROOT", "P1", "P2", "X1", "P3", "P4", "A1", "A2", "A4b", "T1", "A1.Power", "A1.Radius", "A1.Split", "A2.Ward"} and bool(d.tree2) and bool(d.mig),
       "X5: the update: A4 -> A4b (alt B), M1A / M1B / M4A gone, the usable modifiers owned: %s" % o2)
    gf = [CID[ci * NN + n] for n in range(NN) if bool(d.cgf[ci * NN + n])]
    ck(set(gf) == {"A1", "A2", "A4b", "A1.Power", "A1.Radius", "A1.Split", "A2.Ward"} and bool(d.cgfChk[ci]), "X5: every converted node grandfathered, the AP check pending: %s" % gf)
    cp_ = CLASSES.index("Priest")
    ck(set(own(d, cp_)) == {"ROOT", "A1"} and not [CID[cp_ * NN + n] for n in range(NN) if bool(d.cown[cp_ * NN + n]) and NROLE[n] == 3],
       "X5: the Priest line: A1 kept, no Sacred Heal modifier was usable (no uses) -> none owned: %s" % own(d, cp_))
    ck(str(d.corder[ci]) == "ROOT,P1,A1,A4b,T1,A1.Power,A1.Radius,A1.Split,A2.Ward", "X5: the order list: A4 -> A4b in place, M1A dropped, the modifier nodes added: %s" % d.corder[ci])
    hist_t = os.path.join(home, "trees", "history", "abiltree2", k2 + ".properties")
    ck(os.path.isfile(hist_t) and open(hist_t, "rb").read() == raw0, "X5: the untouched tree file is in history/abiltree2 (byte for byte)")
    logt = os.path.join(home, "trees", "abiltree2-changes.log")
    lg = open(logt, encoding="utf8").read() if os.path.isfile(logt) else ""
    ck(k2 in lg and "Undo:" in lg and "A4 -> A4b" in lg, "X5: one change-log line with the Undo: %s" % lg[-200:])
    Store.DATA.put(k2, d)
    ck(bool(Store.saveNow(k2)), "X5: saved")
    txt = open(tf, encoding="latin-1").read()
    cl_line = [l for l in txt.splitlines() if l.startswith("Class.Mage=")][0]
    ck("abil.tree2=done" in txt and "A1.Power" in cl_line and not re.search(r"(^|[=,])(M1A|M1B|M4A|A4)(,|$)", cl_line) and "Class.Mage.gf=" in txt and "Class.Mage.gfchk=1" in txt,
       "X5: the saved file: the marker, the new ids, the grandfather list, the pending check: %s" % cl_line)
    n0 = REALMIG.n
    Store.DATA.clear()
    d2 = Store.readFile(JString(k2))
    ck(own(d2) == own(d) and [bool(x) for x in d2.cgf] == [bool(x) for x in d.cgf] and REALMIG.n == n0, "X5: read again = the same state, SkyyClasses not asked again")
    PK[str(me)] = k2
    Store.DATA.clear()
    Store.DATA.put(k2, d2)
    d2.uid = me
    LV["lvl"] = 2
    T("TreeClass").maint(pr, me, d2)
    gf2 = [CID[ci * NN + n] for n in range(NN) if bool(d2.cgf[ci * NN + n])]
    bal = int(Cls.ap(2)) - int(Cls.spent(Cls.intact(d2, ci), ci, Cls.gfOf(d2, ci)))
    ck(not bool(d2.cgfChk[ci]) and "A1" not in gf2 and len(gf2) == 6 and bal == 0, "X5: the AP check at Sorcery 2 (2 AP, T1 costs 1): A1 paid, the other 6 kept free, balance 0: %s bal %d" % (gf2, bal))
    lg = open(logt, encoding="utf8").read()
    ck("apcheck" in lg and "1 ability / modifier nodes paid" in lg, "X5: ... with its change-log line")
    Store.DATA.clear()
    d3 = Store.readFile(JString(k2))
    d3.cgfChk[ci] = True
    for n in range(NN):
        d3.cgf[ci * NN + n] = bool(d3.cown[ci * NN + n]) and NROLE[n] in (2, 3)
    Store.DATA.put(k2, d3)
    LV["lvl"] = 30
    T("TreeClass").maint(pr, me, d3)
    bal = int(Cls.ap(30)) - int(Cls.spent(Cls.intact(d3, ci), ci, Cls.gfOf(d3, ci)))
    ck(not any(bool(d3.cgf[ci * NN + n]) for n in range(NN)) and bal == 16 - 1 - 7, "X5: at Sorcery 30 (16 AP) all 7 are paid (balance %d)" % bal)
    d4 = Data()
    d4.tree2 = True
    Store.DATA.put(k2, d4)
    LV["lvl"] = 3
    T("TreeClass").maint(pr, me, d4)
    ck(bool(d4.cown[ci * NN + MIX["ROOT"]]), "X5: the tick takes the free Root from class level 1")
    open(tf, "w").write("Class.Mage=ROOT,A1,A4,M4A\n")
    Store.DATA.clear()
    bridge.remove("class:fn:migInfo")
    d5 = Store.readFile(JString(k2))
    ck(not bool(d5.tree2) and str(d5.cold[ci]) == "A4,M4A" and own(d5) == ["ROOT", "A1"], "X5: no SkyyClasses answer -> the old ids wait (kept): %s %s" % (d5.cold[ci], own(d5)))
    Store.DATA.put(k2, d5)
    Store.saveNow(k2)
    ck("A4,M4A" in open(tf, encoding="latin-1").read() and "abil.tree2" not in open(tf, encoding="latin-1").read(), "X5: ... and are written back as they were")
    bridge.put("class:fn:migInfo", REALMIG)
    d5.migNext = 0
    T("TreeClass").maint(pr, me, d5)
    ck(bool(d5.tree2) and "A4b" in own(d5) and d5.cold[ci] is None, "X5: the tick runs the update once SkyyClasses answers: %s" % own(d5))
    # FX (critic A1): a History copy that cannot be made (the name is taken by a folder) -> the update WAITS (old ids kept); unblocked -> converts
    k6 = str(me) + "-p6"
    tf6 = os.path.join(pdir, k6 + ".properties")
    open(tf6, "w").write("Class.Mage=ROOT,A1,A4,M1A\n")
    AS.set(k6, JArray(JString)(["alt"]), JArray(JString)(["A"]))
    C("AbilSave").write(k6)
    raw6 = open(tf6, "rb").read()
    hist6 = os.path.join(home, "trees", "history", "abiltree2", k6 + ".properties")
    os.makedirs(hist6, exist_ok=True)
    sf0 = int(Mig.SNAPFAILS)
    Store.DATA.clear()
    d6 = Store.readFile(JString(k6))
    ck(not bool(d6.tree2) and str(d6.cold[ci]) == "A4,M1A" and int(Mig.SNAPFAILS) == sf0 + 1 and not bool(Mig.snapshot(JString(k6))),
       "FX A1: no History copy possible -> the update waits, the old ids stay (%s), counted %d" % (d6.cold[ci], int(Mig.SNAPFAILS) - sf0))
    PK[str(me)] = k6
    Store.DATA.put(k6, d6)
    d6.migNext = 0
    T("TreeClass").maint(pr, me, d6)
    ck(not bool(d6.tree2), "FX A1: ... the tick does not convert either while the copy fails")
    os.rmdir(hist6)
    d6.migNext = 0
    T("TreeClass").maint(pr, me, d6)
    ck(bool(d6.tree2) and "A4a" in own(d6) and os.path.isfile(hist6) and open(hist6, "rb").read() == raw6,
       "FX A1: unblocked, the tick makes the checked copy (byte for byte) and then converts: %s" % own(d6))
    # FX2 (second critics): the History copy is refreshed - identical = kept; this run's different copy = refreshed in place; an EARLIER
    # run's different copy = kept as <k>.properties.<millis> + a fresh copy (a rollback, then the update again: the Undo stays right)
    hd2 = os.path.join(SCRATCH, "x-hist2")
    shutil.rmtree(hd2, ignore_errors=True)
    os.makedirs(hd2)
    sf2, hf2 = os.path.join(hd2, "src.properties"), os.path.join(hd2, "h", "k.properties")
    def rot2(): return sorted(f_ for f_ in os.listdir(os.path.dirname(hf2)) if f_.startswith("k.properties."))
    open(sf2, "wb").write(b"Class.Mage=ROOT,A1,A4\n")
    r0_ = bool(Mig.copyOnce(Paths.get(sf2), Paths.get(hf2)))
    r1_ = bool(Mig.copyOnce(Paths.get(sf2), Paths.get(hf2)))
    ck(r0_ and r1_ and rot2() == [] and open(hf2, "rb").read() == open(sf2, "rb").read(), "FX2: a new copy, then an identical one is kept (no extra copy)")
    open(sf2, "wb").write(b"Class.Mage=ROOT,A1,A4,M1A\n")
    ck(bool(Mig.copyOnce(Paths.get(sf2), Paths.get(hf2))) and rot2() == [] and open(hf2, "rb").read() == open(sf2, "rb").read(),
       "FX2: this run's copy of a changed file is refreshed in place (the 10 s retries never pile up)")
    old2 = open(hf2, "rb").read()
    t2_ = time.time() - 3600
    os.utime(hf2, (t2_, t2_))
    open(sf2, "wb").write(b"Class.Mage=ROOT,A1,A4,M1A,M1B\n")
    rt0 = int(Mig.ROTATED)
    ok2 = bool(Mig.copyOnce(Paths.get(sf2), Paths.get(hf2)))
    ck(ok2 and len(rot2()) == 1 and open(os.path.join(os.path.dirname(hf2), rot2()[0]), "rb").read() == old2 and open(hf2, "rb").read() == open(sf2, "rb").read()
       and int(Mig.ROTATED) == rt0 + 1, "FX2: an EARLIER run's different copy is kept as %s and a fresh copy is made" % rot2())
    shutil.rmtree(hd2, ignore_errors=True)
    # FX (critic A4): a class level of 0 is not known yet - the AP check waits
    d6.cgfChk[ci] = True
    LV["lvl"] = 0
    T("TreeClass").maint(pr, me, d6)
    ck(bool(d6.cgfChk[ci]), "FX A4: at class level 0 the AP check waits (the mark stays)")
    LV["lvl"] = 30
    T("TreeClass").maint(pr, me, d6)
    ck(not bool(d6.cgfChk[ci]), "FX A4: ... and runs once a real level shows")
    # FX (critic B3): a throw in the tick's maintenance is caught (logged once)
    d7 = Data()
    d7.tree2 = True
    d7.cown = None
    Cls.MAINT_FAILED = False
    errm = None
    try:
        T("TreeClass").maint(pr, me, d7)
    except Exception as e_:
        errm = str(e_)[:120]
    ck(errm is None and bool(Cls.MAINT_FAILED), "FX B3: a throw inside maint0 is caught and logged once: %s" % errm)
    PK[str(me)] = k2
    Store.DATA.clear()
    Store.DATA.put(k2, d5)
    d5.crb[ci] = True
    Store.rbReset(d5, JString("tx1234567890123-abcdef"))
    ck(not any(bool(x) for x in d5.cgf) and not any(bool(x) for x in d5.cgfChk) and "A4b" in str(d5.corder[ci]), "X5: a rebirth reset clears the grandfather marks (the nodes come back under the gate): %s" % d5.corder[ci])
    del PK[str(me)]

    # ================================================================================================ FZ THE FUZZ
    rnd = random.Random(1313)
    TIER_ABIL = {}
    for cn in CLASSES:
        cc = CLN.index(cn)
        TIER_ABIL[cn] = []
        for t in range(5):
            ai = int(AD.of(cc, t))
            TIER_ABIL[cn].append(None if ai < 0 else (str(AD.IDS[ai]), [str(AMD.MID[int(AMD.at(ai, k))]) for k in range(int(AMD.count(ai)))]))
    ALL_ABIL = [(cn, t, a) for cn in CLASSES for t, a in enumerate(TIER_ABIL[cn]) if a]
    INFO = {}
    MIGF = Fn(lambda o: None if INFO.get(str(o)) is None else JString(INFO[str(o)]))
    bridge.put("class:fn:migInfo", MIGF)
    fz = {"n": 0, "conv": 0, "deferred": 0, "gfkept": 0, "paid": 0, "neg": 0, "fails": []}

    def fail(w):
        if len(fz["fails"]) < 30:
            fz["fails"].append(w)

    def gen_class():
        ids = []
        if rnd.random() < 0.9: ids.append("ROOT")
        if rnd.random() < 0.7:
            ids += ["P1"]
            if rnd.random() < 0.7:
                ids += ["P2"]
                if rnd.random() < 0.6:
                    ids.append(rnd.choice(["X1", "X2", "X1", "X2", "X1X2"]))
                    if rnd.random() < 0.6:
                        ids.append("P3")
                        if rnd.random() < 0.5: ids.append("P4")
        ids = [x for i_ in ids for x in (["X1", "X2"] if i_ == "X1X2" else [i_])]
        for ln in range(1, 5):
            if rnd.random() < 0.6:
                ids.append("A%d" % ln)
                if rnd.random() < 0.6:
                    ids.append("M%dA" % ln)
                    if rnd.random() < 0.5: ids.append("M%dB" % ln)
            elif rnd.random() < 0.05:
                ids.append("M%dA" % ln)   # a hand edit: a slot without its ability
        nt = rnd.randint(0, 6)
        ids += ["T%d" % k for k in range(1, nt + 1)]
        if nt and rnd.random() < 0.7:
            pth = rnd.choice(["PA", "PB", "PC"])
            npn = rnd.randint(1, 5)
            ids += ["%s%d" % (pth, k) for k in range(1, npn + 1)]
            if npn == 5 and rnd.random() < 0.5: ids.append({"PA": "LE", "PB": "CE", "PC": "RE"}[pth])
        if rnd.random() < 0.05: ids.append("L2")
        if rnd.random() < 0.05: ids.append("Bogus")
        if rnd.random() < 0.1: ids.append("TS")
        rnd.shuffle(ids)
        return ids

    def gen_info():
        alt = rnd.choice(["A", "B"])
        parts = ["alt=" + alt]
        for cn, t, a in ALL_ABIL:
            us = [m for m in a[1] if rnd.random() < 0.35]
            if us: parts.append("%s=%s" % (a[0], ",".join(us)))
        return ";".join(parts), alt

    def expect(cn, ids, info, alt):
        c = CLASSES.index(cn)
        keep = set(i_ for i_ in ids if i_ in ("ROOT", "P1", "P2", "X1", "X2", "P3", "P4", "A1", "A2", "A3", "LE", "CE", "RE")
                   or re.fullmatch(r"T[1-6]|P[ABC][1-5]", i_))
        if "TS" in ids and not bool(Cls.hidden(c, MIX["TS"])): keep.add("TS")
        if "A4" in ids:
            keep.add("A4b" if (alt == "B" and TIER_ABIL[cn][4]) else "A4a")
        us = dict((p.split("=")[0], p.split("=")[1].split(",")) for p in info.split(";")[1:])
        conv = set()
        for t, lid in enumerate(ABL):
            if lid in keep and TIER_ABIL[cn][t]:
                conv.add(lid)
                for m in TIER_ABIL[cn][t][1]:
                    if m in us.get(TIER_ABIL[cn][t][0], []):
                        keep.add("%s.%s" % (lid, m))
                        conv.add("%s.%s" % (lid, m))
        return keep, conv
    for i in range(1000):
        k = "%s-p%d" % (str(UUID(0x5eed, i)), i % 50)
        cls_ = rnd.sample(CLASSES, rnd.choice([1, 1, 1, 2, 3]))
        info, alt = gen_info()
        lines = {}
        text = "name=Fz\nv=2\n"
        for cn in cls_:
            ids = gen_class()
            lines[cn] = ids
            text += "Class.%s=%s\n" % (cn, ",".join(ids))
            if rnd.random() < 0.3:
                text += "Class.%s.order=%s\n" % (cn, ",".join(rnd.sample(ids, len(ids))))
            if rnd.random() < 0.05:
                text += "Class.%s.rb=1\n" % cn
        f_ = os.path.join(pdir, k + ".properties")
        open(f_, "w").write(text)
        deferred = rnd.random() < 0.1
        INFO.pop(k, None)
        if not deferred:
            INFO[k] = info
        Store.DATA.clear()
        hist = os.path.join(home, "trees", "history", "abiltree2", k + ".properties")
        if os.path.exists(hist): os.remove(hist)
        d = Store.readFile(JString(k))
        fz["n"] += 1
        if deferred:
            fz["deferred"] += 1
            needs = any(x in ("A1", "A2", "A3", "A4") or re.fullmatch(r"M[1-4][AB]|A4", x) for ids in lines.values() for x in ids)
            if bool(d.tree2) == needs:
                fail("%s deferred: tree2 %s needs %s" % (k, bool(d.tree2), needs))
            Store.DATA.put(k, d)
            Store.saveNow(k)
            txt = open(f_, encoding="latin-1").read()
            for cn, ids in lines.items():
                for x in ids:
                    if re.fullmatch(r"A4|M[1-4][AB]", x) and needs:
                        line = [l for l in txt.splitlines() if l.startswith("Class.%s=" % cn)]
                        if not line or x not in line[0].split("=", 1)[1].split(","):
                            fail("%s deferred: %s lost from Class.%s" % (k, x, cn))
            INFO[k] = info
            Store.DATA.clear()
            d = Store.readFile(JString(k))
        if not bool(d.tree2):
            fail("%s: no update with the facts" % k)
            continue
        fz["conv"] += 1
        for cn, ids in lines.items():
            c = CLASSES.index(cn)
            keep, conv = expect(cn, ids, info, alt)
            got = set(own(d, c))
            if got != keep:
                fail("%s %s: owned %s want %s (old %s)" % (k, cn, sorted(got - keep), sorted(keep - got), ids))
                continue
            gfs = set(CID[c * NN + n] for n in range(NN) if bool(d.cgf[c * NN + n]))
            if gfs != conv or bool(d.cgfChk[c]) != bool(conv):
                fail("%s %s: grandfathered %s want %s" % (k, cn, sorted(gfs), sorted(conv)))
            lvl = rnd.randint(0, 100)
            it0 = [bool(x) for x in Cls.intactAt(d, c, lvl)]
            r_ = Cls.gfCheck(d, c, lvl)
            it1 = [bool(x) for x in Cls.intactAt(d, c, lvl)]
            if it0 != it1:
                fail("%s %s: the AP check changed what is intact" % (k, cn))
            for x in conv:
                n = sidx(c, x)
                if not it1[n] and not bool(d.crb[c]):
                    fail("%s %s: converted %s is not intact (it worked before)" % (k, cn, x))
            bal = int(Cls.ap(lvl)) - int(Cls.spent(Cls.intactAt(d, c, lvl), c, Cls.gfOf(d, c)))
            gfa = set(CID[c * NN + n] for n in range(NN) if bool(d.cgf[c * NN + n]))
            paid = conv - gfa
            fz["paid"] += len(paid)
            fz["gfkept"] += len(gfa)
            if bal < 0:
                fz["neg"] += 1
                if paid:
                    fail("%s %s: balance %d < 0 but %s were paid" % (k, cn, bal, sorted(paid)))
            elif not bool(d.crb[c]):
                left = [x for x in gfa if it1[sidx(c, x)] and int(Cfg.C_AP[c * NN + sidx(c, x)]) <= bal]
                if left:
                    fail("%s %s: %s still grandfathered with %d AP free" % (k, cn, left, bal))
            if conv and r_ is None:
                fail("%s %s: no AP check result" % (k, cn))
        Store.DATA.put(k, d)
        if not bool(Store.saveNow(k)):
            fail("%s: save failed" % k)
        txt = open(f_, encoding="latin-1").read()
        if "abil.tree2=done" not in txt or re.search(r"^Class\.[A-Za-z]+=.*(^|[=,])(A4|M[1-4][AB])(,|$)", txt, re.M):
            fail("%s: the saved file still has old ids / no marker" % k)
        n0 = MIGF.n
        Store.DATA.clear()
        d2 = Store.readFile(JString(k))
        if [bool(x) for x in d2.cown] != [bool(x) for x in d.cown] or [bool(x) for x in d2.cgf] != [bool(x) for x in d.cgf] \
                or [bool(x) for x in d2.cgfChk] != [bool(x) for x in d.cgfChk] or [str(x) for x in d2.corder] != [str(x) for x in d.corder] or MIGF.n != n0:
            fail("%s: read again differs (or SkyyClasses was asked again)" % k)
        if any(re.fullmatch(r"A4|M[1-4][AB]", x) for ids in lines.values() for x in ids) and not os.path.isfile(hist):
            fail("%s: no History copy" % k)
        if i % 50 == 49:
            for f2 in os.listdir(pdir):
                if f2.startswith(str(UUID(0x5eed, i))[:8]):
                    pass
    ck(not fz["fails"] and fz["n"] == 1000, "FZ: 1000 random 0.3.12 profiles (%d updated, %d deferred first, %d paid, %d kept free, %d negative-balance trees): %s"
       % (fz["conv"], fz["deferred"], fz["paid"], fz["gfkept"], fz["neg"], fz["fails"][:6]))
    R["notes"].append("FZ: %s" % {k_: v_ for k_, v_ in fz.items() if k_ != "fails"})
    bridge.put("class:fn:migInfo", REALMIG)
    json.dump(R, open(out, "w"))
    sys.stdout.flush()
    os._exit(0)


# ============================================================================================================ child: LV (the live profiles, copied)
def run_lv(out, trees_home, classes_home):
    """the one-time update on a scratch COPY of the live players/ files with the real SkyyClasses 0.1.26 reading a COPY of the live
    Skyy_SkyyClasses folder: every old node kept or mapped, no old id left, read twice = the same, the AP check pays what fits"""
    from jpype import JClass, JString, JImplements, JOverride
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
    Cls, Store, Cfg, Paths, Integer = T("TreeClass"), T("TreeStore"), T("TreeCfg"), JClass("java.nio.file.Paths"), JClass("java.lang.Integer")
    LOGC = JClass("com.hypixel.hytale.logger.HytaleLogger")
    Cfg.LOG = LOGC.get("SkyyTrees")
    CC_ = C("ClassCfg")
    CC_.LOG = LOGC.get("SkyyClasses")
    CC_.FILE = Paths.get(os.path.join(classes_home, "config.properties"))
    CC_.load()
    C("ClassStore").DIR = Paths.get(os.path.join(classes_home, "players"))
    C("AbilStore").DIR = Paths.get(os.path.join(classes_home, "abilities"))
    bridge = Store.bridge()

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    bridge.put("class:fn:migInfo", C("AbilMigFn")())
    pdir = os.path.join(trees_home, "players")
    Store.DIR = Paths.get(pdir)
    NN, NC = int(Cls.NN), int(Cls.NC)
    CLASSES = [str(x) for x in Cls.CLASSES]
    CID = [str(x) for x in Cls.CID]
    files = sorted(f[:-11] for f in os.listdir(pdir) if f.endswith(".properties")) if os.path.isdir(pdir) else []
    n_conv = 0
    for k in files:
        txt0 = open(os.path.join(pdir, k + ".properties"), encoding="latin-1").read()
        old = {}
        for ln in txt0.splitlines():
            m = re.match(r"Class\.([A-Za-z]+)=(.*)$", ln)
            if m:
                old[m.group(1)] = [x.strip() for x in m.group(2).split(",") if x.strip()]
        Store.DATA.clear()
        d = Store.readFile(JString(k))
        ok = not bool(d.bad) and bool(d.tree2)
        lost = []
        for cn, ids in old.items():
            if cn not in CLASSES:
                continue
            c = CLASSES.index(cn)
            own = set(CID[c * NN + n] for n in range(NN) if bool(d.cown[c * NN + n]))
            for x in ids:
                if re.fullmatch(r"M[1-4][AB]", x):
                    continue
                want = ("A4a", "A4b") if x == "A4" else (x,)
                if not (own & set(want)) and x not in ("L1", "L2", "L3", "L4", "C1", "C2", "C3", "C4", "R1", "R2", "R3", "R4", "LS", "CS", "RS"):
                    lost.append("%s.%s" % (cn, x))
        ck(ok and not lost, "LV %s: the live profile updates without losing a node: %s (old %s)" % (k[:13], lost, old))
        n_conv += 1 if old else 0
        Store.DATA.put(k, d)
        Store.saveNow(k)
        txt1 = open(os.path.join(pdir, k + ".properties"), encoding="latin-1").read()
        Store.DATA.clear()
        d2 = Store.readFile(JString(k))
        Store.DATA.put(k, d2)
        Store.saveNow(k)
        txt2 = open(os.path.join(pdir, k + ".properties"), encoding="latin-1").read()
        strip = lambda t: "\n".join(l for l in t.splitlines() if not l.startswith("#"))
        ck(strip(txt1) == strip(txt2) and "abil.tree2=done" in txt1, "LV %s: a second read + save writes the same file" % k[:13])
        R["notes"].append("LV %s: %s -> %s" % (k[:13], old, [l for l in txt1.splitlines() if l.startswith("Class.")]))
    ck(len(files) >= 1, "LV: %d live profile file(s) copied and updated (%d with class lines)" % (len(files), n_conv))
    json.dump(R, open(out, "w"))
    sys.stdout.flush()
    os._exit(0)


# ============================================================================================================ parent
def main():
    if "--x" in sys.argv:
        return run_x(arg("--out"))
    if "--lv" in sys.argv:
        return run_lv(arg("--out"), arg("--th"), arg("--ch"))
    if "--rp" in sys.argv:
        return T311.run_rp(arg("--out"))
    T = T310.t36()
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
    live_before = T310.snap(LIVE)
    me = os.path.abspath(__file__)

    def child(args_, out_):
        with open(out_ + ".log", "wb") as lf:
            subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT, cwd=SCRATCH)
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
            KIT = {"CfgFn", "CfgRows", "CfgPub", "CfgKit", "CfgHist", "CfgImp", "CfgText", "CfgFile"}
            check(sorted(cc["added"]) == ["TreeAbMig", "TreeModFn"] or sorted(x.split(".")[-1] for x in cc["added"]) == ["TreeAbMig", "TreeModFn"],
                  "CC: the new classes = TreeAbMig + TreeModFn: %s" % cc["added"])
            check(not cc["gone"], "CC: no class removed: %s" % cc["gone"])
            struct = dict((c, sorted(m.split("(")[0] for m in v["structural"])) for c, v in cls_.items() if v["structural"] and c not in KIT)
            print("CC. 0.3.12 -> 0.3.13 structural: %s" % struct)
            # + TreeFx.postTree (the inlined TreeClass.NN 44 -> 62), TreeMig / TreeMig33 <clinit> (their one-time blocks carry the class block lines:
            # + the 3 AP rows, no A / M lines) - constants only
            allowed = {"TreeClass", "TreeClassOps", "TreePage", "TreeStore", "TreeCfg", "TreeData", "TreeDefs", "TreeTick", "SkyyTreesPlugin", "TreeKit",
                       "TreeFx", "TreeMig", "TreeMig33"}
            check(struct.get("TreeFx") == ["postTree"] and struct.get("TreeMig") == ["<clinit>"] and struct.get("TreeMig33") == ["<clinit>"],
                  "CC: TreeFx / TreeMig / TreeMig33 differ only where a changed constant is inlined: %s" % [struct.get(x_) for x_ in ("TreeFx", "TreeMig", "TreeMig33")])
            check(set(struct) <= allowed, "CC: structural changes only in %s: %s" % (sorted(allowed), sorted(set(struct) - allowed)))
            newf = dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"])
            print("CC. new fields: %s" % newf)
            gone = dict((c, v["fields_gone"]) for c, v in cls_.items() if v["fields_gone"])
            check(not gone, "CC: no field removed: %s" % gone)
        zj = zipfile.ZipFile(JAR)
        mn = json.loads(zj.read("manifest.json"))
        check(mn.get("Version") == VERSION or VERSION in json.dumps(mn), "JT: manifest version %s" % VERSION)
        x = child(["--x"], os.path.join(SCRATCH, "x.json"))
        check(x is not None, "X ran")
        if x:
            for ok, what in x.get("checks", []):
                check(ok, what)
            for n_ in x.get("notes", []):
                print("X. note:", str(n_)[:300])
            print("X. %d executed checks" % len(x.get("checks", [])))
            check(len(x.get("checks", [])) >= 90, "X: every scenario ran (%d checks)" % len(x.get("checks", [])))
            nly = 0
            for tag, pg in sorted(x.get("pages", {}).items()):
                check(pg["err"] is None, "LY %s: built without an exception: %s" % (tag, pg["err"]))
                roots, byid = T312.build_tree(pg["cmds"])
                probs = T312.layout_problems(roots)
                check(not probs and roots, "LY %s: the layout model finds nothing outside its container (%d roots): %s" % (tag, len(roots), probs[:4]))
                for r_ in roots:
                    a_ = T312._pairs(r_["props"].get("Anchor"))
                    check(a_.get("Width", 0) <= 1600 and a_.get("Height", 0) <= 980, "LY %s: the page fits 1600 x 980 (%s x %s)" % (tag, a_.get("Width"), a_.get("Height")))
                nly += 1
            check(nly >= 8, "LY: %d pages checked" % nly)
        # LV: the update on a scratch COPY of the live profiles (players/ + the live Skyy_SkyyClasses folder for class:fn:migInfo)
        lv_t, lv_c = os.path.join(SCRATCH, "lv", "Skyy_SkyyTrees"), os.path.join(SCRATCH, "lv", "Skyy_SkyyClasses")
        live_c = os.path.join(os.path.dirname(LIVE), "Skyy_SkyyClasses")
        if os.path.isdir(os.path.join(LIVE, "players")):
            shutil.copytree(os.path.join(LIVE, "players"), os.path.join(lv_t, "players"))
        else:
            os.makedirs(os.path.join(lv_t, "players"))
        if os.path.isdir(live_c):
            shutil.copytree(live_c, lv_c)
        else:
            os.makedirs(lv_c)
        lv = child(["--lv", "--th", lv_t, "--ch", lv_c], os.path.join(SCRATCH, "lv.json"))
        check(lv is not None, "LV ran")
        if lv:
            for ok, what in lv.get("checks", []):
                check(ok, what)
            for n_ in lv.get("notes", []):
                print("LV. note:", str(n_)[:300])
        rp = child(["--rp"], os.path.join(SCRATCH, "rp.json"))
        check(rp is not None, "RP ran")
        if rp:
            for ok, what in rp.get("checks", []):
                check(ok, what)
            check(len(rp.get("checks", [])) >= 65, "RP: every 0.3.11 replant scenario ran on 0.3.13 (%d checks)" % len(rp.get("checks", [])))
        fake = os.path.join(SCRATCH, "fake")
        subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=SCRATCH)
        sts = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            sts[tag] = child(["--st", j, "--fake", fake, "--live", LIVE, "--tag", tag], os.path.join(SCRATCH, "st-%s.json" % tag))
            check(sts[tag] is not None and len(sts[tag].get("starts", [])) == 2, "ST (%s): two starts ran" % tag)
        if sts.get("new") and sts.get("prev"):
            T34 = T.t34()
            nz = lambda r: T34.norm_start(r).replace(VERSION, "0.3.X").replace(PREV_VERSION, "0.3.X")
            sn, sp = sts["new"]["starts"], sts["prev"]["starts"]
            check(nz(sn[0]) == nz(sp[0]), "ST: start 1 of 0.3.13 = 0.3.12's (the live file is not rewritten): %s / %s" % (sn[0]["changed"], sp[0]["changed"]))
            check(sn[1]["changed"] == [] and sn[1]["sum"] == sn[0]["sum"], "ST: start 2 changes nothing and reads the same: %s" % sn[1]["changed"])
            print("ST. start twice on the live copy: start 1 changed %s (same as 0.3.12), start 2 nothing" % sn[0]["changed"])
        au = child(["--audit", JAR, "--fake", fake], os.path.join(SCRATCH, "audit.json"))
        check(au is not None, "Z: the audit child ran")
        if au:
            check(not au.get("refused") and au.get("refs", 0) > 2000, "Z: engine-access audit: %s references, 0 refused: %s" % (au.get("refs"), str(au.get("refused"))[:400]))
            check(len(au.get("control") or []) >= 1, "Z: the audit's control is refused")
            print("Z. %s references, %d refused" % (au.get("refs"), len(au.get("refused") or [])))
        check(T310.snap(LIVE) == live_before, "the live Skyy_SkyyTrees folder was never written (only read + copied)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyTrees %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
