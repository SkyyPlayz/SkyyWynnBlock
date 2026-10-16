"""SkyyTrees 0.3.18 - harness for THE TOP-DOWN CLASS TREE + MODIFIERS OUT OF THE TREE + WHAT AN ABILITY DOES (tools/trees_0_3_18_patch.py),
with the REAL SkyyClasses 0.1.30 jar in the same JVM. Build first:
    python tools/trees_0_3_18_patch.py && python SkyyTrees/build_skyytrees_0.3.18.py
    (and python tools/classes_0_1_30_patch.py && python SkyyClasses/build_skyyclasses_0.1.30.py)

    python SkyyTrees/test_skyytrees_0.3.18.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch. The live save data is only READ (copied).
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.17 -> 0.3.18: exactly the members of EXPECT differ (no class added / removed)
  OLD  0.3.17's TreeClass on the fixture player files (its own JVM): the AP each spends (the refund proof's "before")
  X    EXECUTED (Trees 0.3.18 + Classes 0.1.30 in one JVM, one skyy.bridge map):
       LY  the node table: 37 nodes, no modifier node, every node where the layout puts it (page / row / column), the abilities at their
           unlock depth, the buy rules = 0.3.17's (parents, needs, locks, AP), the level gates through the real class:fn:abilUnlock
       RU  the rules on the new layout (TreeClass.reason / intactOf / TreeClassOps.buy): an ability needs only its level (A2 at Lv 10 with
           nothing but the Root), P1 without A1 stays intact (its parent is ROOT), T2 needs T1, PA1 needs T1 + Lv 20, the A4 pick-one
       GO  the gold bars: ROOT -> A1 lights with A1 or P1 / T1 / TS; T1 -> A2 and A2 -> T2 light when T2 is bought through T1 without A2;
           A3 -> PA1 lights with T1 + PA1; the Priest's TS / the Assassin's A4b bars hidden for the others
       MG  the one-time modifier node update (abiltree3) on fixture files: the ids leave the owned list + the order, the record
           (.modRefund), the refund = the AP 0.3.17 spent on them (OLD), the History copy is the untouched file, the change-log line, the
           chat line once (TreeMsg.note318 via takeNote318), a second read = nothing; a blocked History copy = the ids written back, no
           marker (tried again at the next read); a file without modifier nodes: only the marker; two classes; grandfathered = 0 back
       BR  tree:fn:modOwned answers null (no gate) for any input; tree:fn:abil lists no modifier node
       PG  THE PAGE on the real classes (render + clicks): an ability node's detail shows the walking cost + what it does + how it grows
           (class:fn:abilDoes), a stat node keeps its 0.3.17 lines, page 2 renders A3 / T4 / the paths / the A4 pair; the focus view's tiles
           ("... on Meteor" / "Unlocks at Meteor Lv 4: ..."), a locked tile's click says where it unlocks (no node selected), the
           Lattice's "What it does" box = the sentence; without class:fn:abilDoes the 0.3.17 texts show
  LIVE start twice on a scratch COPY of the live Skyy_SkyyTrees: trees.properties + the config start twice = no byte change; every live
       player file read -> the update (History copy, record) -> saved -> read + saved again = the same file; every non-modifier node owned
       before is still owned
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import deploy_set as DS

VERSION, PREV = "0.3.18", "0.3.17"
PKG, CPKG = "com.skyy.trees.", "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-%s.jar" % PREV)
CL_JAR = os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.30.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "cls0130", "ht")))
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyTrees")
ADDED = []
EXPECT = {   # why: the node table is shorter (NN 62 -> 37, inlined in every loop / index) + the moved cells (the tables in <clinit>)
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup"],   # the version + the ap.modifier row text
    "TreeAbMig": ["+f APPLIED3", "+f LAST3", "+m apply3", "+m done3", "+m logIn", "+m snapshotIn", "~<clinit>", "~m apply", "~m copyOnce",
                  "~m logLine", "~m needs", "~m snapFail", "~m snapshot"],
    "TreeCfg": ["~<clinit>", "~m apply", "~m load"],
    "TreeClass": ["+f MODASKS", "+m doesOf", "+m modSid", "+m tileText", "~<clinit>", "~m abilMin", "~m apEach", "~m bonus", "~m bonusLevel",
                  "~m cardText", "~m cardText2", "~m comingWho", "~m coveredBy", "~m csvOf", "~m firstOf", "~m gate", "~m gfCheck", "~m gfOf",
                  "~m hidden", "~m icon", "~m intact", "~m intactAt", "~m intactOf", "~m isGf", "~m isSwitch", "~m keepLane", "~m kind",
                  "~m laneHas", "~m laneOwned", "~m lit", "~m maint0", "~m minOf", "~m modOwned", "~m name", "~m nodeIdx", "~m nodeIdx", "~m now",
                  "~m on", "~m ownOf", "~m parseKey", "~m passed", "~m pathOf", "~m ranked", "~m reason", "~m reasonText", "~m sid",
                  "~m skipKind", "~m skips", "~m slotComing", "~m spent", "~m stat", "~m state", "~m states", "~m sum", "~m switchOn", "~m used",
                  "~m waiting"],
    "TreeClassOps": ["~<clinit>", "~m anyBought", "~m buy", "~m buyText", "~m costLine", "~m flip", "~m howLine", "~m probeData", "~m typeLine", "~m undo"],
    "TreeData": ["+f cmodGf", "+f cmodKeep", "+f cmodRef", "+f cnote3", "+f mig3Next", "+f tree3", "~c "],
    "TreeFx": ["~m postTree"], "TreeKit": ["~m checkClassNode"], "TreeMig": ["~<clinit>"], "TreeMig33": ["~<clinit>"],
    "TreeMsg": ["+m note318"], "TreePage": ["~m abilEv", "~m buildClass", "~m cicon", "~m handleDataEvent"],
    "TreeStore": ["+m mig3Locked", "+m takeNote318", "~m clearClass", "~m rbReset", "~m readFile", "~m rootOwn", "~m setClassOwn", "~m setOn", "~m snap"],
    "TreeTick": ["~m tick"],
}

# the fixture player files (0.3.17 wrote them like this): key -> text
FIX = {
    "fx-mage": "v=2\nabil.tree2=done\nClass.Mage=ROOT,A1,A1.Power,A1.Radius,P1,T1,A2,A2.Power\n"
               "Class.Mage.order=A1,A1.Power,T1,A1.Radius,A2,A2.Power\nClass.Mage.gf=A1.Radius\n",
    "fx-none": "v=2\nabil.tree2=done\nClass.Warrior=ROOT,A1,T1,P1,P2\nClass.Warrior.order=A1,T1\n",
    "fx-two": "v=2\nabil.tree2=done\nClass.Spellblade=ROOT,P2,X2,P3,A1,A1.Chain\nClass.Spellblade.order=ROOT,P2,X2,P3,A1,A1.Chain\n"
              "Class.Assassin=ROOT,A1,A1.Duration,A1.Efficiency,A2,A2.Echo\nClass.Assassin.gf=A1.Duration,A1.Efficiency,A2.Echo\n",
    "fx-block": "v=2\nabil.tree2=done\nClass.Mage=ROOT,A1,A1.Power,A1.Radius\nClass.Mage.gf=A1.Radius\n",
}
FIX_LVL = 30


def _home(scratch, tag):
    h = os.path.join(scratch, tag)
    shutil.rmtree(h, ignore_errors=True)
    os.makedirs(os.path.join(h, "players"))
    for k, t in FIX.items():
        open(os.path.join(h, "players", k + ".properties"), "wb").write(t.encode("latin-1"))
    return h


# ======================================================================================================== OLD: 0.3.17's AP on the fixtures
def run_old(out, jar, scratch, _home_):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, OLD_JAR], verify=False)
    T = lambda n: JClass(PKG + n)
    Cls, Store, Cfg, Paths = T("TreeClass"), T("TreeStore"), T("TreeCfg"), JClass("java.nio.file.Paths")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyTrees")
    Cfg.CLASS_ON = True
    h = _home(scratch, "old-home")
    Store.DIR = Paths.get(os.path.join(h, "players"))
    res = {}
    for k in FIX:
        d = Store.readFile(JString(k))
        res[k] = {}
        for ci, cn in enumerate([str(x) for x in Cls.CLASSES]):
            it = Cls.intactOf(Cls.ownOf(d, ci), ci)
            res[k][cn] = int(Cls.spent(it, ci, Cls.gfOf(d, ci)))
    json.dump(res, open(os.path.join(scratch, "old-ap.json"), "w"))
    K.check(res["fx-mage"]["Mage"] == 5, "OLD: 0.3.17 spends 5 AP on fx-mage (A1, A1.Power, T1, A2, A2.Power; A1.Radius kept free): %s" % res["fx-mage"]["Mage"])
    K.save()
    sys.stdout.flush()
    os._exit(0)


# ======================================================================================================== X
def run_x(out, jar, scratch, _home_):
    from jpype import JClass, JArray, JString, JObject, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, CL_JAR], verify=True)
    T = lambda n: JClass(PKG + n)
    C = lambda n: JClass(CPKG + n)
    Cls, Ops, Page, Store, Cfg, Data, Mig, Msg = T("TreeClass"), T("TreeClassOps"), T("TreePage"), T("TreeStore"), T("TreeCfg"), T("TreeData"), T("TreeAbMig"), T("TreeMsg")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Paths, Integer, Long, Boolean = JClass("java.nio.file.Paths"), JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    UUID, ArrayList = JClass("java.util.UUID"), JClass("java.util.ArrayList")
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)
    me = UUID(0x7ee5, 318)
    km = str(me)
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    bridge = Store.bridge()

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    LV = {"lvl": 30}
    bridge.put("skill:fn:level", Fn(lambda o: Integer.valueOf(LV["lvl"])))
    bridge.put("skill:fn:combat", Fn(lambda o: Long.valueOf(0)))
    bridge.put("coins:fn:take", Fn(lambda o: Boolean.TRUE))

    def setcls(cn):
        bridge.put("profile:" + km, "1")
        bridge.put("class:" + km, cn)
        bridge.put("profile:class:" + km, cn)
    setcls("Mage")
    home = os.path.join(scratch, "x-home")
    os.makedirs(os.path.join(home, "classes", "players"), exist_ok=True)
    LOGC = JClass("com.hypixel.hytale.logger.HytaleLogger")
    CC_ = C("ClassCfg")
    CC_.LOG = LOGC.get("SkyyClasses")
    CC_.FILE = Paths.get(os.path.join(home, "classes", "config.properties"))
    CC_.load()
    C("ClassStore").DIR = Paths.get(os.path.join(home, "classes", "players"))
    AS = C("AbilStore")
    AS.DIR = Paths.get(os.path.join(home, "classes", "abilities"))
    AS.SYNC = True
    for k_, v_ in {"class:fn:abilPanel": C("AbilPanelFn")(), "class:fn:abilMods": C("AbilModsFn")(), "class:fn:abilDo": C("AbilDoFn")(),
                   "class:fn:abilUnlock": C("AbilUnlockFn")(), "class:fn:migInfo": C("AbilMigFn")(), "class:fn:abilDoes": C("AbilDoesFn")()}.items():
        bridge.put(k_, v_)
    m_ = re.search(rb"Class\.Mage\.A1[ -~]*", zipfile.ZipFile(CL_JAR).read("com/skyy/classes/SkyyClassesPlugin.class"))
    bridge.put("tree:reads:SkyyClasses", m_.group(0).decode() if m_ else "")
    bridge.put("tree:fn:abil", T("TreeAbilFn")())
    bridge.put("tree:fn:modOwned", T("TreeModFn")())
    Cfg.LOG = LOGC.get("SkyyTrees")
    Cfg.CLASS_ON = True
    NN, NC = int(Cls.NN), int(Cls.NC)
    CLASSES = [str(x) for x in Cls.CLASSES]
    NID = [str(x) for x in Cls.NID]
    MIX = dict((n, i) for i, n in enumerate(NID))
    CID = [str(x) for x in Cls.CID]
    NROLE = [int(x) for x in Cls.NROLE]
    NT = int(T("TreeDefs").NT)
    mage = CLASSES.index("Mage")

    # ------------------------------------------------------------------ LY
    pos = dict((NID[n], (int(Cls.NPAGE[n]), int(Cls.NROW[n]), int(Cls.NCOL[n]))) for n in range(NN))
    WANT = {"ROOT": (0, 0, 4), "A1": (0, 1, 4), "P1": (0, 2, 2), "T1": (0, 2, 4), "TS": (0, 2, 6), "P2": (0, 3, 2), "A2": (0, 3, 4),
            "X1": (0, 4, 1), "X2": (0, 4, 3), "T2": (0, 4, 4), "P3": (0, 5, 2), "T3": (0, 5, 4), "P4": (0, 6, 2),
            "A3": (1, 0, 4), "T4": (1, 1, 4), "A4a": (1, 2, 3), "A4b": (1, 2, 5), "T5": (1, 3, 4), "T6": (1, 4, 4)}
    for i_, (pre, el, col) in enumerate((("PA", "LE", 0), ("PB", "CE", 2), ("PC", "RE", 6))):
        for k_ in range(1, 6):
            WANT[pre + str(k_)] = (1, k_, col)
        WANT[el] = (1, 6, col)
    K.check(NN == 37 and 3 not in NROLE and not [c for c in CID if "." in c], "LY: 37 nodes per class, no modifier node (role 3 / a dotted id)")
    K.check(pos == WANT, "LY: every node where the top-down layout puts it: %s" % sorted(k for k in WANT if pos.get(k) != WANT[k]))
    gates = dict((a, int(Cls.minOf(mage, MIX[a]))) for a in ("A1", "A2", "A3", "A4a", "A4b", "T1", "T2", "T3", "T4", "PA1", "PA2"))
    K.check(gates == {"A1": 1, "A2": 10, "A3": 20, "A4a": 30, "A4b": 30, "T1": 5, "T2": 10, "T3": 15, "T4": 25, "PA1": 20, "PA2": 30},
            "LY: the level gates (abilities through SkyyClasses' class:fn:abilUnlock): %s" % gates)
    par = dict((NID[n], (int(Cls.NPAR1[n]), int(Cls.NPAR2[n]), int(Cls.NNEED[n]), int(Cls.NLOCK[n]), int(Cls.NAP[n]))) for n in range(NN))
    K.check(par["T2"][0] == MIX["T1"] and par["T4"][0] == MIX["T3"] and par["PA1"][0] == MIX["T1"] and par["P1"][0] == MIX["ROOT"]
            and par["A2"][0] == MIX["ROOT"] and par["A4a"][3] == MIX["A4b"] and par["P3"][:2] == (MIX["X1"], MIX["X2"]),
            "LY: the parents (the buy rule) are 0.3.17's: T2 <- T1, T4 <- T3, PA1 <- T1, P1 <- ROOT, the abilities <- ROOT, the A4 lock")
    K.check(sum(int(x) for x in Cls.APB) == 32 * NC, "LY: a full class tree = 32 AP for every class: %s" % [int(x) for x in Cls.APB])

    # ------------------------------------------------------------------ RU
    def ownset(ids):
        o = JArray(JClass("boolean"))(NN)
        for i in ids:
            o[MIX[i]] = True
        return o
    def reason(ids, nid, lvl, ap=50, ci=None):
        ci = mage if ci is None else ci
        o = ownset(ids)
        return int(Cls.reason(o, Cls.intactOf(o, ci), ci, MIX[nid], lvl, ap))
    war = CLASSES.index("Warrior")   # its T1 / PA1 are live nodes (SkyyClasses applies them): no "waiting" skip in the way
    K.check(reason(["ROOT"], "A2", 10) == 0 and reason(["ROOT"], "A2", 9) == 7 and reason(["ROOT"], "A3", 20) == 0,
            "RU: an ability needs only its class level (A2 at Lv 10, A3 at Lv 20, with nothing but the Root)")
    ru = [reason(["ROOT"], "T2", 30, ci=war), reason(["ROOT", "T1"], "T2", 30, ci=war), reason(["ROOT", "T1"], "PA1", 19, ci=war),
          reason(["ROOT", "T1"], "PA1", 20, ci=war), reason(["ROOT"], "PA1", 30, ci=war)]
    K.check(ru == [3, 0, 7, 0, 3], "RU: (Warrior) T2 needs T1, PA1 needs T1 + Lv 20 (0.3.17's rules): %s" % ru)
    it = Cls.intactOf(ownset(["ROOT", "P1", "P2"]), mage)
    K.check(bool(it[MIX["P1"]]) and bool(it[MIX["P2"]]), "RU: P1 / P2 stay intact without A1 (their parent is the Root)")
    K.check(reason(["ROOT", "A4a"], "A4b", 30) == 5, "RU: the A4 pair stays pick-one")

    # ------------------------------------------------------------------ GO
    LA, LB = [int(x) for x in Cls.LA], [int(x) for x in Cls.LB]

    def gold(ids, a, b):
        li = [i for i in range(len(LA)) if LA[i] == MIX[a] and LB[i] == MIX[b]]
        assert len(li) == 1, (a, b)
        o = ownset(ids)
        return bool(Cls.linkGold(li[0], Cls.intactOf(o, mage)))
    K.check(not gold(["ROOT", "T1", "T2"], "T1", "A2") and not gold(["ROOT", "T1", "T2"], "A2", "T2") and not gold(["ROOT", "T1"], "T1", "A2")
            and gold(["ROOT", "T1", "A2"], "T1", "A2") and not gold(["ROOT", "T1", "A2"], "A2", "T2") and gold(["ROOT", "T1", "A2", "T2"], "A2", "T2"),
            "GO: fix round: T1 -> A2 -> T2 lights only with A2 owned (no lit bar through an unowned ability); both ends owned = lit")
    K.check(not gold(["ROOT", "P1"], "ROOT", "A1") and not gold(["ROOT", "P1"], "A1", "P1") and gold(["ROOT", "A1", "P1"], "A1", "P1") and gold(["ROOT", "A1"], "ROOT", "A1"),
            "GO: fix round: ROOT -> A1 lights with A1; A1 -> P1 with A1 and P1")
    K.check(not gold(["ROOT", "T1", "PA1"], "A3", "PA1") and gold(["ROOT", "T1", "A3", "PA1"], "A3", "PA1") and not gold(["ROOT", "T1", "T2", "T3", "T4"], "A3", "T4")
            and gold(["ROOT", "T1", "T2", "T3", "A3", "T4"], "A3", "T4"),
            "GO: fix round: page 2's bars from A3 light only with A3 owned (PA1, T4)")
    for cn, hid in (("Warrior", "TS"), ("Assassin", "A4b")):
        c_ = CLASSES.index(cn)
        sh = Cls.pieceShow(c_, int(Cls.NPAGE[MIX[hid]]))
        li = [i for i in range(len(LA)) if LB[i] == MIX[hid]][0]
        pl1, pl2 = [int(x) for x in Cls.PL1], [int(x) for x in Cls.PL2]
        base = int(Cls.NPAGE[MIX[hid]]) * int(Cls.NSLOT) * 8
        own_q = [q for q in range(int(Cls.NSLOT) * 8) if (pl1[base + q] == li and pl2[base + q] < 0)]
        K.check(own_q and not [q for q in own_q if bool(sh[q])], "GO: the %s's %s bar is hidden (%d pieces)" % (cn, hid, len(own_q)))

    # ------------------------------------------------------------------ MG
    old = json.load(open(os.path.join(scratch, "old-ap.json")))
    h = _home(scratch, "mg-home")
    pdir = os.path.join(h, "players")
    Store.DIR = Paths.get(pdir)
    os.makedirs(os.path.join(h, "history", "abiltree3", "fx-block.properties"))   # a blocked History copy for fx-block
    Store.DATA.clear()
    got = {}
    for k in FIX:
        d = Store.readFile(JString(k))
        got[k] = d
        Store.DATA.put(k, d)
    dm = got["fx-mage"]
    own_m = [CID[mage * NN + n] for n in range(NN) if bool(dm.cown[mage * NN + n])]
    it_m = Cls.intactOf(Cls.ownOf(dm, mage), mage)
    new_ap = int(Cls.spent(it_m, mage, Cls.gfOf(dm, mage)))
    K.check(sorted(own_m) == sorted(["ROOT", "A1", "P1", "T1", "A2"]) and bool(dm.tree3) and str(dm.corder[mage]) == "A1,T1,A2"
            and str(dm.cmodRef[mage]) == "A1.Power,A1.Radius,A2.Power", "MG: fx-mage: the modifier ids left the owned list + the order; the record (%s / %s)" % (own_m, dm.corder[mage]))
    K.check(old["fx-mage"]["Mage"] - new_ap == 2 and int(dm.cnote3[mage]) == 2,
            "MG: THE REFUND: 0.3.17 spent %d AP, 0.3.18 spends %d - the 2 paid modifier nodes (A1.Power, A2.Power) came back, A1.Radius was kept free (0 back); the notice says %d"
            % (old["fx-mage"]["Mage"], new_ap, int(dm.cnote3[mage])))
    hist = os.path.join(h, "history", "abiltree3", "fx-mage.properties")
    K.check(os.path.isfile(hist) and open(hist, "rb").read() == FIX["fx-mage"].encode("latin-1"), "MG: the History copy is the untouched file")
    log = open(os.path.join(h, "abiltree3-changes.log"), encoding="utf8").read()
    K.check("\tfx-mage\tupdate\tMage: 3 modifier node(s) left the tree (A1.Power A1.Radius A2.Power) - 2 AP back (1 were kept free" in log
            and "Undo: stop the server, copy history/abiltree3/fx-mage.properties" in log, "MG: the change-log line with the Undo: %s" % log[:200])
    K.check(bool(Store.saveNow("fx-mage")), "MG: saved")
    txt = open(os.path.join(pdir, "fx-mage.properties"), encoding="latin-1").read()
    K.check("abil.tree3=done" in txt and "Class.Mage.modRefund=A1.Power,A1.Radius,A2.Power" in txt and "Class.Mage.modNotice=2" in txt
            and re.search(r"^Class\.Mage=ROOT,A1,P1,T1,A2$", txt, re.M) and "A1.Power" not in re.search(r"^Class\.Mage=.*$", txt, re.M).group(0)
            and "Class.Mage.gf" not in txt, "MG: the saved file (marker, record, notice; no modifier id owned; the gf line went with its only ids): %s" % txt.replace("\n", " | "))
    Store.DATA.clear()
    d2 = Store.readFile(JString("fx-mage"))
    K.check(bool(d2.tree3) and int(d2.cnote3[mage]) == 2 and str(d2.cmodRef[mage]) == "A1.Power,A1.Radius,A2.Power"
            and [CID[mage * NN + n] for n in range(NN) if bool(d2.cown[mage * NN + n])] == [CID[mage * NN + n] for n in range(NN) if bool(dm.cown[mage * NN + n])],
            "MG: read again = the same state (the marker; no second update)")
    K.check(open(os.path.join(h, "abiltree3-changes.log"), encoding="utf8").read() == log, "MG: ... and no second log line")
    Store.DATA.put("fx-mage", d2)
    n1 = Store.takeNote318(d2)
    n2 = Store.takeNote318(d2)
    K.check(n1 is not None and int(n1[mage]) == 2 and n2 is None and int(d2.cnote3[mage]) == 0, "MG: the chat notice is taken once")
    # fx-two: two classes; the Assassin's were all kept free (-1 = the line, 0 AP back)
    dt = got["fx-two"]
    sb, asn = CLASSES.index("Spellblade"), CLASSES.index("Assassin")
    K.check(int(dt.cnote3[sb]) == 1 and int(dt.cnote3[asn]) == -1 and str(dt.cmodRef[asn]) == "A1.Duration,A1.Efficiency,A2.Echo"
            and not [n for n in range(NN) if bool(dt.cown[asn * NN + n]) and "." in CID[asn * NN + n]] and bool(dt.cown[asn * NN + MIX["A2"]]),
            "MG: two classes in one file: Spellblade 1 AP back, Assassin 0 back (all kept free) but told")
    K.check(old["fx-two"]["Spellblade"] - int(Cls.spent(Cls.intactOf(Cls.ownOf(dt, sb), sb), sb, Cls.gfOf(dt, sb))) == 1, "MG: fx-two Spellblade refund = 0.3.17's spend - 0.3.18's")
    dn = got["fx-none"]
    K.check(bool(dn.tree3) and not os.path.exists(os.path.join(h, "history", "abiltree3", "fx-none.properties")) and int(dn.cnote3[CLASSES.index("Warrior")]) == 0,
            "MG: a file without modifier nodes: only the marker (no History copy, no notice)")
    db = got["fx-block"]
    K.check(not bool(db.tree3) and str(db.cmodKeep[mage]) == "A1.Power,A1.Radius" and str(db.cmodGf[mage]) == "A1.Radius" and db.cmodRef[mage] is None,
            "MG: a blocked History copy: the update waits (ids kept, the free one remembered)")
    Store.saveNow("fx-block")
    tb = open(os.path.join(pdir, "fx-block.properties"), encoding="latin-1").read()
    K.check("abil.tree3" not in tb and re.search(r"^Class\.Mage=ROOT,A1,A1\.Power,A1\.Radius$", tb, re.M) and re.search(r"^Class\.Mage\.gf=A1\.Radius$", tb, re.M),
            "MG: ... saved with the modifier ids + their gf written back, no marker: %s" % tb.replace("\n", " | "))
    K.check(not bool(Mig.snapshotIn(JString("fx-block"), JString("abiltree3"))) and not bool(db.tree3),
            "MG: fix round: while the History copy is still blocked the retry does nothing")
    os.rmdir(os.path.join(h, "history", "abiltree3", "fx-block.properties"))
    # fix round (critic: "nothing retries it in the running server"): TreeClass.maint's retry = snapshotIn + TreeStore.mig3Locked
    K.check(bool(Mig.snapshotIn(JString("fx-block"), JString("abiltree3"))), "MG: fix round: the History copy works once unblocked")
    s3 = Store.mig3Locked(db)
    K.check(s3 is not None and "2 modifier node(s) left the tree (A1.Power A1.Radius) - 1 AP back (1 were kept free" in str(s3) and bool(db.tree3)
            and db.cmodKeep[mage] is None and db.cmodGf[mage] is None and str(db.cmodRef[mage]) == "A1.Power,A1.Radius" and int(db.cnote3[mage]) == 1
            and Store.mig3Locked(db) is None, "MG: fix round: THE RETRY in the running server: the update runs once (1 AP back, the free one 0): %s" % s3)
    Store.DATA.put("fx-block", db)
    Store.saveNow("fx-block")
    tb2 = open(os.path.join(pdir, "fx-block.properties"), encoding="latin-1").read()
    K.check("abil.tree3=done" in tb2 and re.search(r"^Class\.Mage=ROOT,A1$", tb2, re.M) and "Class.Mage.gf" not in tb2 and "Class.Mage.modNotice=1" in tb2,
            "MG: fix round: ... saved after the retry (marker, no modifier id, notice): %s" % tb2.replace("\n", " | "))
    open(os.path.join(pdir, "fx-block.properties"), "wb").write(FIX["fx-block"].encode("latin-1"))   # the untouched file again for the read test
    Store.DATA.clear()
    db2 = Store.readFile(JString("fx-block"))
    K.check(bool(db2.tree3) and str(db2.cmodRef[mage]) == "A1.Power,A1.Radius" and int(db2.cnote3[mage]) == 1, "MG: ... the next read updates it")
    # the chat line (TreeMsg.note318 on the page's player)
    Store.DATA.clear()
    dq = Data()
    dq.tree2 = True
    dq.tree3 = True
    dq.cnote3[mage] = 3
    Store.DATA.put(km, dq)
    SAIDM = []
    try:
        Msg.note318(pr, me)
    except Exception as e:
        SAIDM.append(str(e)[:200])
    K.check(int(dq.cnote3[mage]) == 0, "MG: TreeMsg.note318 takes the notice (the message itself goes to the player: %s)" % SAIDM[:1])

    # ------------------------------------------------------------------ BR
    mf = T("TreeModFn")()
    K.check(mf.apply(JArray(JObject)([me, JString("Meteor"), JString("Power")])) is None and mf.apply(JArray(JObject)([me, JString("A1"), JString("Radius")])) is None
            and mf.apply(None) is None, "BR: tree:fn:modOwned answers null (no gate)")

    # ------------------------------------------------------------------ PG
    Store.DIR = Paths.get(os.path.join(home, "trees-players"))
    os.makedirs(os.path.join(home, "trees-players"), exist_ok=True)

    def fresh():
        Store.DATA.clear()
        Store.DIRTY.clear()
        AS.TREEC.clear()
        d = Data()
        d.tree2 = True
        d.tree3 = True
        Store.DATA.put(km, d)
        return d

    def render(page):
        b, ev = UCB(), UEB()
        err = None
        try:
            page.build(None, b, ev, None)
        except Exception as e:
            err = str(e)[:300]
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
        return err, texts, evs

    def click(page, a):
        try:
            page.handleDataEvent(None, None, '{"a":"%s"}' % a)
            return None
        except Exception as e:
            return str(e)[:200]
    LV["lvl"] = 30
    d = fresh()
    AS.set(km, JArray(JString)(["u.Meteor", "alt", "p1", "e.Meteor"]), JArray(JString)(["30", "A", "Meteor", "Power,"]))
    undo = ArrayList()
    for n_ in ("A1", "T1", "A2"):
        Ops.buy(me, d, mage, 30, MIX[n_], undo, False)
    page = Page(pr, NT)
    page.csel = MIX["A1"]
    page.cpage = 0
    err, texts, evs = render(page)
    met = [str(x) for x in C("AbilDoes").info("Meteor")]
    K.check(err is None, "PG: the class tab builds: %s" % err)
    K.check((met[2] + " - Ability - 1 AP") in texts and (met[1] + " " + met[3]) in texts,
            "PG: the Meteor node's detail: its walking cost + type, what it does + how it grows: %s" % [t for t in texts if "Mana" in t or "meteor" in t][:3])
    K.check(any(t.startswith("Now: ") for t in texts), "PG: the Now line is there")
    page.csel = MIX["P1"]
    err, texts, evs = render(page)
    K.check(err is None and [t for t in texts if t.startswith("Gives: ")] and not [t for t in texts if met[1] in t], "PG: a stat node keeps its 0.3.17 lines (Gives: ...), no ability sentence")
    page.cpage = 1
    page.csel = MIX["A3"]
    err, texts, evs = render(page)
    fn_ = [str(x) for x in C("AbilDoes").info("FrostNova")]
    K.check(err is None and (fn_[1] + " " + fn_[3]) in texts and all(any(('"trc%d"' % (MIX[x] + 1)) in e for e in evs) for x in ("A3", "T4", "A4a", "A4b", "PA1", "PB1", "PC1", "LE")),
            "PG: page 2 renders A3 (Frost Nova's detail), T4, the A4 pair and the paths (every cell clickable)")
    page.cpage = 0
    page.csel = MIX["A1"]
    K.check(click(page, "tyca0") is None and bool(page.amode) and str(page.afoc) == "Meteor", "PG: clicking Meteor focuses it: %s" % page.msg)
    err, texts, evs = render(page)
    K.check(err is None and met[1] in texts, "PG: the Lattice's 'What it does' box = Meteor's sentence: %s" % err)
    tiles = [t for t in texts if t.startswith(("+", "Unlocks at"))]
    K.check([t for t in tiles if t.endswith(" on Meteor")] and [t for t in tiles if t.startswith("Unlocks at Meteor Lv 4: ") or t.startswith("Unlocks at Lv 4: ")]
            and not [t for t in texts if "in the tree (" in t], "PG: the tiles: the unlocked one says what it changes on Meteor, a locked one where it unlocks: %s" % tiles)
    K.check(click(page, "tyft1") is None and str(page.msg) == "Ability: Radius+ unlocks at Meteor Lv 4 - use Meteor to level it up (no Ability Points)"
            and bool(page.amode) and int(page.csel) == MIX["A1"], "PG: a locked tile's click says where it unlocks (no node selected): %s" % page.msg)
    K.check(click(page, "tyft0") is None and int(page.hk) == 2 and str(page.hmod) == "Power", "PG: an unlocked tile still holds its modifier: %s" % page.msg)
    bridge.remove("class:fn:abilDoes")
    page.amode = False
    page.csel = MIX["A1"]
    err, texts, evs = render(page)
    K.check(err is None and not (met[1] + " " + met[3]) in texts and [t for t in texts if t.startswith("Gives: ")], "PG: without class:fn:abilDoes the 0.3.17 texts show")
    bridge.put("class:fn:abilDoes", C("AbilDoesFn")())
    abl = str(T("TreeAbilFn")().apply(me))
    K.check("A1" in abl and "." not in abl, "BR: tree:fn:abil lists the owned ability nodes, no modifier id: %s" % abl)
    K.save()
    sys.stdout.flush()
    os._exit(0)


# ======================================================================================================== LIVE: start twice on a copy
def run_live(out, jar, scratch, home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    T = lambda n: JClass(PKG + n)
    Cls, Store, Cfg, Paths = T("TreeClass"), T("TreeStore"), T("TreeCfg"), JClass("java.nio.file.Paths")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyTrees")

    def snap(d):
        o = {}
        for r, _ds, fs in os.walk(d):
            for f in fs:
                p = os.path.join(r, f)
                o[os.path.relpath(p, d)] = open(p, "rb").read()
        return o
    b = Paths.get(home)
    s0 = snap(home)
    for i in range(2):
        Cfg.FILE = b.resolve("trees.properties")
        Store.DIR = b.resolve("players")
        st = [str(Cfg.load())]
        for mn in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317"):
            try:
                st.append(str(T(mn).run(b))[:60])
            except Exception as e:
                st.append("%s: %s" % (mn, str(e)[:80]))
        s1 = snap(home)
        K.check(sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k)) == [], "LIVE: start %d (config + its updates) changes no file: %s" % (i + 1, st[1:]))
    NN = int(Cls.NN)
    CLASSES = [str(x) for x in Cls.CLASSES]
    CID = [str(x) for x in Cls.CID]
    pdir = os.path.join(home, "players")
    files = sorted(f[:-11] for f in os.listdir(pdir) if f.endswith(".properties")) if os.path.isdir(pdir) else []
    for k in files:
        raw = open(os.path.join(pdir, k + ".properties"), encoding="latin-1").read()
        before = {}
        for ln in raw.splitlines():
            m = re.match(r"Class\.([A-Za-z]+)=(.*)$", ln)
            if m:
                before[m.group(1)] = [x.strip() for x in m.group(2).split(",") if x.strip()]
        Store.DATA.clear()
        d = Store.readFile(JString(k))
        lost = []
        for cn, ids in before.items():
            if cn not in CLASSES:
                continue
            c = CLASSES.index(cn)
            own = set(CID[c * NN + n] for n in range(NN) if bool(d.cown[c * NN + n]))
            lost += ["%s.%s" % (cn, x) for x in ids if "." not in x and x not in own]
        mods = [x for v in before.values() for x in v if "." in x]
        K.check(not bool(d.bad) and not lost and bool(d.tree3), "LIVE %s: read + updated, no non-modifier node lost (%s), %d modifier node(s) refunded" % (k[:13], lost, len(mods)))
        if mods:
            hp = os.path.join(home, "history", "abiltree3", k + ".properties")
            K.check(os.path.isfile(hp) and open(hp, encoding="latin-1").read() == raw, "LIVE %s: its History copy is the untouched file" % k[:13])
        Store.DATA.put(k, d)
        Store.saveNow(k)
        t1 = open(os.path.join(pdir, k + ".properties"), encoding="latin-1").read()
        Store.DATA.clear()
        d2 = Store.readFile(JString(k))
        Store.DATA.put(k, d2)
        Store.saveNow(k)
        t2 = open(os.path.join(pdir, k + ".properties"), encoding="latin-1").read()
        strip = lambda t: "\n".join(l for l in t.splitlines() if not l.startswith("#"))
        K.check(strip(t1) == strip(t2) and "abil.tree3=done" in t1, "LIVE %s: read + save a second time = the same file" % k[:13])
        K.notes.append("LIVE %s: %s -> %s" % (k[:13], before, [l for l in t1.splitlines() if l.startswith("Class.")]))
    K.check(len(files) >= 1, "LIVE: %d live player file(s) on the copy" % len(files))
    K.save()
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("old", run_old), ("x", run_x), ("live", run_live)], script=__file__, live=(LIVE, "Skyy_SkyyTrees"))
