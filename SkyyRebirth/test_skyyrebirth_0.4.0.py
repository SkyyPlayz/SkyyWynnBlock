"""SkyyRebirth 0.4.0 - harness for VOID PARTICLES (tools/rebirth_0_4_0_patch.py; Skill-Trees-3-Spec 6 + 7 R4).
Build first: python tools/rebirth_0_4_0_patch.py && python SkyyRebirth/build_skyyrebirth_0.4.0.py

    python SkyyRebirth/test_skyyrebirth_0.4.0.py --dir <empty folder inside tools/dev/scratch/> [--keep]

  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.3.6 -> 0.4.0: exactly the planned members differ (RbAdminRefundCmd removed, RbMig added)
  V   vp       EXECUTED on real files in scratch (bare JVM, the server jar): VP(n) + overflow (rebirths 1, 5, 6, 12; the 11-skill cap); the
               ladders (costs + stronger strengths of targets.md 5a); buy (Insight, Echo, the shared Hand ladder, Head Start, a tool node,
               refused: switched off / busy / not enough / changed meanwhile / full); the keep buff (+0.25 % a VP, no cap, "Holding 76 VP:
               +19 % XP"); skill:bonus source rebirth + rebirth:fn:stat / node / vp / dustmult answers; RESPEC with a fake acc:fn:bag + acc:defs
               (the lowest rarity taken, expect mismatch, too few charms, no SkyyAccessories, a save failure puts the charm back, free with 0,
               admin refund); /rebirthadmin points / reset / refund; decide() VP from facts (Farming pooled, 11 cap, rebirth 6 + 7 with no
               limit, the max abort with a limit); applyOwn (VP, idempotent; an open 0.3.x decision's pts.* 1:1); THE MIGRATION (old file ->
               VP, nodes + keystone title gone, backup byte-identical, one log line with UNDO, run once, a v=4 file untouched, the rollback
               case, a backup failure = untouched + unreadable, then migrated); a WHOLE rebirth 6 -> 7 through the journal with fake parts
               (admin + live with the markets), the level-cap math (50 + 10 x n; SkyySkills clamps at 100)
  P   page     the hub page both views built for real (UICommandBuilder): check_page, assert_menu_page, sky paths, 21 node bindings +
               TooltipText, the VP counter line, the node view (Buy, Respec), Respec through handleDataEvent twice -> done, every left-panel
               text measured at 424 px
  D   live     a scratch COPY of the live NewBetaTest Skyy_SkyyRebirth: start twice (setup's order: migOn, migMax, loadCfg, CfgPub) - start 1
               = 0.3.6's rebirth.max 10 -> 0 only (the live file is still 0.3.4-era), start 2 writes nothing; no players/ = nothing migrated
  F   fixes    (fix round, critics) EXECUTED: xp.combat = Combat Echo alone; the reader gate (rebirth:reads:<Mod> / tree:reads:SkyySkills;
               refused + "coming with"); the respec takes only the charms the arming press named (bag changed = refused, nothing taken), never a
               charm outside acc:defs, saves BEFORE the take (a save failure = nothing taken; a refused take = the old profile back), VP clamp
               1e9; the bag is not read in the rebirth view; the migration's rollback-then-forward case (every node + vpSpent refunded) and
               the log line before the write (a failed write = untouched, a WRITE FAILED line, retried). FIX ROUND 2: a failed load through
               the cache answers null in every rebirth:fn mode, is retried only when due, heals on a later good read; RbPub keeps the last
               rebirth:n; status reads RbStore.peek (no migration); a published rebirth:reads list alone decides the gate; a 2-charm respec
               whose charm cannot go back stays done
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, re, importlib.util, shutil, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI
import deploy_set as DS

VERSION = "0.4.0"
RB = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.3.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rebirth04", "rb")))
LIVE_RB = os.path.join(B.USERDATA, "Saves", DS.WORLD, "mods", "Skyy_SkyyRebirth")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T34 = _load("t_rb034", os.path.join(HERE, "test_skyyrebirth_0.3.4.py"))
T34.VERSION, T34.JAR = VERSION, JAR

# the planned member changes 0.3.6 -> 0.4.0 (each reviewed: the tree -> the Nexus, VP, the respec, the migration hook, the kit's version texts)
EXPECT = {'CfgFile': ['~<clinit>'],
 'CfgFn': ['~m opExport'],
 'CfgRows': ['~<clinit>', '~m header'],
 'RbAdmin': ['~m help', '~m run'],
 'RbAdminArgsCmd': ['~c '],
 'RbAdminCmd': ['~c '],
 'RbAdminPointsCmd': ['-f armArg', '~c ', '~m execute'],
 'RbCfg': ['+f C_ECHO',
           '+f C_HEAD',
           '+f C_INSIGHT',
           '+f C_TOOL',
           '+f HEAD_PTS',
           '+f KEEP',
           '+f L_CLASS',
           '+f L_INSIGHT',
           '+f L_SKILL',
           '+f RESPEC_CHARMS',
           '+f VP_BASE',
           '+f VP_OVER',
           '+f VP_PER',
           '+f VP_SKILL',
           '+m chkLad',
           '+m chkLad3',
           '+m chkLadN',
           '+m chkPct',
           '+m lad',
           '+m ladOf',
           '+m ladTxt',
           '-f COST_GROWTH',
           '-f DUST_NODE',
           '-f ROW_NEED',
           '-f W_DD',
           '-f W_ECHO',
           '-f W_KEY',
           '-f W_KSTAT',
           '-f W_SPEED',
           '-f W_STAT',
           '-f W_XP',
           '~<clinit>',
           '~m loadCfg',
           '~m writeDefaults'],
 'RbCheck': ['~m gains', '~m tip'],
 'RbFn': ['~m apply'],
 'RbJob': ['+c ', '+f ids', '+f shown', '~c ', '~m exec'],
 'RbMath': ['+f CAP_SKILLS',
            '+f OLD_ARMS',
            '+m dust',
            '+m overflow',
            '+m vp',
            '-f ARMS',
            '-f ARM_B',
            '-f ARM_SKILL',
            '-m dust',
            '-m dustArm',
            '-m points',
            '~<clinit>'],
 'RbPage': ['+f armedIds',
            '+f armedShown',
            '+f armedWhat',
            '+f canRespec',
            '+f ntip',
            '+f nvKeep',
            '+f ptHand',
            '+f ptRe',
            '+f respecArmed',
            '+f respecIds',
            '+f respecPick',
            '+f respecPickAt',
            '+f respecPickK',
            '+f respecShown',
            '+f respecWhat',
            '+m fillRespec',
            '+m respec',
            '~<clinit>',
            '~m build',
            '~m fill',
            '~m fillNode',
            '~m fillTree',
            '~m handleDataEvent'],
 'RbPub': ['~m publish'],   # fix round 2: a failed load keeps the last values
 'RbStore': ['+f NEXT', '+f TRIES', '+m bad', '+m due', '+m failed', '+m heal', '+m peek', '+m readFile', '~<clinit>', '~m get', '~m loadNow', '~m readNow', '~m save', '~m writeNow'],
 'RbTree': ['+f ARM_NAME',
            '+f NRALT',
            '+f NRMOD',
            '+f NRTOK',
            '+m charmKey',
            '+m live',
            '+m soon',
            '+f HAND_MAX',
            '+f I_BEAST',
            '+f I_CLASS',
            '+f I_COMBAT',
            '+f I_HEAD',
            '+f I_INSIGHT',
            '+f NCOST',
            '+f NHAND',
            '+f NSHORT',
            '+f NSTR',
            '+f RESPECS',
            '+f XP_KEY',
            '+f XP_NODE',
            '+m addVp',
            '+m allPct',
            '+m bagFn',
            '+m charmInfo',
            '+m charmNames',
            '+m charmPick',
            '+m charmsBack',
            '+m cost',
            '+m costLad',
            '+m echo',
            '+m full',
            '+m handTotal',
            '+m held',
            '+m idx',
            '+m keepPct',
            '+m keepTxt',
            '+m ranks',
            '+m respec',
            '+m strLad',
            '+m strength',
            '+m wipe',
            '-f NBON',
            '-f NCAT',
            '-f NKIND',
            '-f NROW',
            '-f NSTAT',
            '-f NTITLE',
            '-m addPts',
            '-m armIndex',
            '-m armLevels',
            '-m armMax',
            '-m cost',
            '-m echoPct',
            '-m echoed',
            '-m need',
            '-m openRows',
            '-m per',
            '-m refund',
            '-m rowLevels',
            '-m state',
            '-m wipe',
            '~<clinit>',
            '~m bonusMap',
            '~m buy',
            '~m fx',
            '~m gate',
            '~m stat'],
 'RbTx': ['+m vpOf', '~m applyOwn', '~m decide', '~m dryRun', '~m finish', '~m status'],
 'SkyyRebirthPlugin': ['~m setup', '~m shutdown']}
ADDED = ["RbMig"]
REMOVED = ["RbAdminRefundCmd"]
R = lambda n: __import__("jpype").JClass(RB + n)


def cmds_of(b):
    out = []
    for c in list(b.getCommands()):
        g = lambda n: (lambda v: None if v is None else str(v))(getattr(c, n, None))
        out.append((g("type"), g("selector"), g("text"), g("data")))
    return out


def events_of(ev):
    return [(str(e.selector), str(getattr(e, "data", None))) for e in list(ev.getEvents())]


def unq(d):
    if d is None:
        return ""
    try:
        v = json.loads(d)
    except Exception:
        return d
    if isinstance(v, dict) and len(v) == 1:
        v = list(v.values())[0]
    return v if isinstance(v, str) else d


DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")


def world(scratch, name):
    """a fresh data home + bridge for one run: RbStore / RbJournal dirs, IO off (inline), the config defaults; returns (home, players, U, k)"""
    from jpype import JClass
    home = os.path.join(scratch, name, "Skyy_SkyyRebirth")
    os.makedirs(os.path.join(home, "players"))
    P_ = JClass("java.nio.file.Paths")
    Cfg = R("RbCfg")
    Cfg.BRIDGE = JClass("java.util.concurrent.ConcurrentHashMap")()
    Cfg.DIR = P_.get(home)
    Cfg.FILE = P_.get(os.path.join(home, "config.properties"))
    Cfg.loadCfg(False)
    St = R("RbStore")
    St.DIR = P_.get(os.path.join(home, "players"))
    St.CACHE.clear(); St.BAD.clear(); St.BUSY.clear(); St.PEND.clear(); St.NEXT.clear(); St.TRIES.clear()
    R("RbJournal").DIR = P_.get(os.path.join(home, "journal"))
    St.IO = None
    U = JClass("java.util.UUID").randomUUID()
    return home, os.path.join(home, "players"), U, str(U)


def _un(x):
    """a .properties escape (a backslash before a character) -> the character"""
    out, esc = [], False
    for ch in x:
        if esc or ch != chr(92):
            out.append(ch)
            esc = False
        else:
            esc = True
    return "".join(out)


def props(path):
    d = {}
    if not os.path.isfile(path):
        return d
    for ln in open(path, encoding="latin-1").read().splitlines():
        if ln.startswith("#") or "=" not in ln:
            continue
        k_, v_ = ln.split("=", 1)
        d[_un(k_.strip())] = _un(v_.strip())
    return d


def fakes():
    """Python Functions for the bridge: the Void Charms bag (acc:fn:bag), the rebirth parts, the markets"""
    from jpype import JImplements, JOverride, JClass
    Int, Bool = JClass("java.lang.Integer"), JClass("java.lang.Boolean")

    @JImplements("java.util.function.Function")
    class Bag(object):
        def __init__(self, ids):
            self.ids, self.calls, self.refuse_take, self.takes_ok, self.refuse_put = list(ids), [], False, None, False

        @JOverride
        def apply(self, o):
            a = list(o)
            op = str(a[0])
            self.calls.append((op,) + tuple(str(x) for x in a[3:]))
            if op == "list":
                return ",".join(x for x in self.ids if x)
            if op == "take":
                if self.refuse_take or self.takes_ok == 0:
                    return Int(-1)
                if self.takes_ok is not None:
                    self.takes_ok -= 1
                idv = str(a[3])
                if idv in self.ids:
                    i = self.ids.index(idv)
                    self.ids[i] = None
                    return Int(i)
                return Int(-1)
            if op == "put":
                idv, at = str(a[3]), int(a[4])
                if self.refuse_put:
                    return Bool.FALSE
                if 0 <= at < len(self.ids) and self.ids[at] is None:
                    self.ids[at] = idv
                else:
                    self.ids.append(idv)
                return Bool.TRUE
            return None

    @JImplements("java.util.function.Function")
    class Part(object):
        def __init__(self, name, facts):
            self.name, self.facts, self.ops = name, facts, []

        @JOverride
        def apply(self, o):
            a = list(o)
            op = str(a[0])
            self.ops.append(op)
            if op in ("prepare", "measure"):
                return "ok:" + self.facts
            if op == "commit":
                return "ok"
            if op == "abort":
                return "ok"
            return "ok"

    @JImplements("java.util.function.Function")
    class Const(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            return self.v
    return Bag, Part, Const


DEFS = ("Lantern:Lantern:1:Skyy_Talisman_Lantern_Common:Normal:1:x,Lantern:Lantern:4:Skyy_Talisman_Lantern_Epic:Legendary:4:x,"
        "Speed:Speed:2:Skyy_Talisman_Speed_Uncommon:Unique:2:x")


def run_vp(out, jar, scratch, _home):
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    from jpype import JClass, JArray
    K = HK.Child(out)
    Bag, Part, Const = fakes()
    Cfg, St, Tr, Mt, Tx, Mg = R("RbCfg"), R("RbStore"), R("RbTree"), R("RbMath"), R("RbTx"), R("RbMig")
    O = JClass("java.lang.Object")
    OA = lambda *xs: JArray(O)(list(xs))
    Ln = JClass("java.lang.Long")
    home, pl, U, k = world(scratch, "v")
    # ---------------------------------------------------------------- VP(n) + overflow (spec 6.1)
    K.eq([int(Mt.vp(1, 0, 0)), int(Mt.vp(1, 4, 0)), int(Mt.vp(5, 11, 0)), int(Mt.vp(3, 20, 0)), int(Mt.vp(6, 7, 12)), int(Mt.vp(12, 7, 36)), int(Mt.vp(0, 7, 12))],
         [30, 38, 92, 72, 106, 190, 0], "V VP(n) = 20 + 10 n + 2 x skills (max 11) + overflow; rebirth 6 / 12 (no limit) earn more; n 0 = 0")
    K.eq([int(Mt.overflow(1000, 1000)), int(Mt.overflow(4000, 1000)), int(Mt.overflow(16000, 1000)), int(Mt.overflow(10 ** 9, 1000)),
          int(Mt.overflow(500, 1000)), int(Mt.overflow(5, 0))], [0, 12, 36, 36, 0, 0], "V overflow: r 1 -> 0, 4 -> 12, 16 -> 36 (cap), under 1 / no cap -> 0")
    # ---------------------------------------------------------------- the ladders (targets.md 5a, STRONGER) + their Server Setup checks
    I = lambda nid: int(Tr.idx(nid))
    K.eq([float(Tr.strength(I("Void.insight"), r)) for r in range(6)], [0.0, 6.0, 14.0, 24.0, 36.0, 52.0], "V Void Insight +6/8/10/12/16 % all XP (sum)")
    K.eq([float(Tr.strength(I("Class.echo"), 5)), float(Tr.strength(I("Mining.echo"), 5)), float(Tr.strength(I("Hand.farming"), 3)),
          float(Tr.strength(I("Void.head"), 3)), float(Tr.strength(I("Mining.tool"), 4))], [36.0, 80.0, 34.0, 3.0, 4.0],
         "V Class Echo 36 %, skill Echo 80 %, Hand 3 ranks 34 %, Head Start 3 points, a tool 4 modifier levels")
    K.check(Cfg.chkLad("nexus.costEcho", "4,6,10,16,24") is None and Cfg.chkLad("x", "1,2,3") is not None and Cfg.chkPct("x", "8,11,15,20,101") is not None
            and Cfg.chkPct("x", "8,11,15,20,26") is None and Cfg.chkLad3("x", "20,30,45") is None and Cfg.chkLad("x", "a,b,c,d,e") is not None,
            "V the ladder rows' check hooks (5 / 3 numbers; strengths 0 - 100)")
    cfgf = os.path.join(home, "config.properties")
    open(cfgf, "w").write("nexus.costEcho=1,1,1\nnexus.insight=1,2,3,4,5\nnexus.keep=0.5\nvp.base=7\n")
    Cfg.loadCfg(False)
    K.check(str(Cfg.C_ECHO) == "4,6,10,16,24" and str(Cfg.L_INSIGHT) == "1,2,3,4,5" and float(Cfg.KEEP) == 0.5 and int(Cfg.VP_BASE) == 7,
            "V loadCfg: a bad ladder keeps the default, a good one is used, keep / base read")
    os.remove(cfgf)
    Cfg.loadCfg(False)
    K.check(str(Cfg.L_INSIGHT) == "6,8,10,12,16" and float(Cfg.KEEP) == 0.25 and int(Cfg.VP_BASE) == 20 and int(Cfg.RESPEC_CHARMS) == 1, "V no file: the defaults")
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in R("CfgRows").header()[7])
    K.check(all(x in rows for x in ("vp.base", "vp.perRebirth", "vp.perSkill", "vp.overflow", "nexus.keep", "nexus.insight", "nexus.classEcho",
                                     "nexus.skillEcho", "nexus.costInsight", "nexus.costEcho", "nexus.costHead", "nexus.costTool", "nexus.headStart",
                                     "nexus.respecCharms")) and not any(x.startswith("tree.") for x in rows) and "dust.perNode" not in rows,
            "V Server Setup: 14 Void Particle rows, the 0.3 tree rows gone: %s" % sorted(rows))
    # ---------------------------------------------------------------- buy
    f = os.path.join(pl, k + ".properties")
    open(f, "w").write("n=2\nv=4\nvp=200\n")
    buy = lambda nid, exp, al=True: str(Tr.buy(k, U, I(nid), exp, al))
    r1 = buy("Void.insight", 0)
    d = props(f)
    K.check(r1.startswith("+Void Insight rank 1 bought - 12 VP spent (Holding 188 VP: +47 % XP)") and d["vp"] == "188" and d["vpSpent"] == "12"
            and d["node.Void.insight"] == "1" and d["v"] == "4", "V buy Void Insight rank 1: 12 VP, saved (%s, %s)" % (r1, d))
    K.check("changed meanwhile" in buy("Void.insight", 0), "V a late duplicate Buy = changed meanwhile")
    K.check("switched off" in buy("Void.insight", 1, False), "V Buy while rebirth is off (not an admin) = refused")
    St.BUSY.put(k, "x")
    K.check("rebirth is running" in buy("Void.insight", 1), "V Buy while a rebirth runs = refused")
    St.BUSY.remove(k)
    # F the reader gate: no reader live = refused (nothing charged), then live through tree:reads:SkyySkills / rebirth:reads:<Mod>
    g0 = [buy("Hand.alchemy", 0), buy("Void.head", 0), buy("Combat.echo", 0), buy("Beast.echo", 0), buy("Fishing.tool", 0), buy("Hand.fishing", 0)]
    K.check(all(x_.startswith("-") and "is coming with" in x_ for x_ in g0) and props(f)["vp"] == "188"
            and [bool(Tr.live(I(n_))) for n_ in ("Void.insight", "Class.echo", "Mining.tool", "Hand.farming", "Hand.cooking", "Hand.smithing", "Hand.acrobatics")]
            == [True, True, True, True, True, False, False], "F no reader live: Alchemy / Head Start / Combat / Beasts / Pole / Fishing refused, nothing charged: %s" % [x_[:60] for x_ in g0])
    Cfg.BRIDGE.put("tree:reads:SkyySkills", "anything")
    Cfg.BRIDGE.put("rebirth:reads:SkyyTrees", "headstart")
    G2 = ("Hand.alchemy", "Hand.smithing", "Combat.echo", "Void.head", "Hand.fishing", "Hand.acrobatics", "Beast.echo", "Fishing.tool")
    K.check([bool(Tr.live(I(n_))) for n_ in G2] == [True, True, True, True, False, False, False, False],
            "F live: SkyySkills 0.4.56 key (no list) -> Alchemy / Smithing / Combat; rebirth:reads:SkyyTrees -> Head Start")
    Cfg.BRIDGE.put("rebirth:reads:SkyySkills", "xp.acrobatics, xp.fishing")
    K.check([bool(Tr.live(I(n_))) for n_ in G2] == [False, False, False, True, True, True, False, False],
            "F fix round 2: once SkyySkills publishes its list, the list alone decides (Alchemy / Smithing / Combat not listed = not buyable; spaces ok)")
    Cfg.BRIDGE.put("rebirth:reads:SkyySkills", "xp.combat,xp.alchemy,xp.smithing,xp.fishing,xp.acrobatics")
    K.check([bool(Tr.live(I(n_))) for n_ in G2] == [True, True, True, True, True, True, False, False], "F the full SkyySkills list: every Hand + Combat; Pets / pole still not")
    hand = [buy("Hand.farming", 0), buy("Hand.farming", 1), buy("Hand.farming", 2), buy("Hand.cooking", 0), buy("Hand.alchemy", 0), buy("Hand.fishing", 0)]
    p = St.readNow(k)
    K.check([h_[:1] for h_ in hand] == ["+"] * 5 + ["-"] and "4 VP" in hand[0] and "6 VP" in hand[1] and "10 VP" in hand[2] and "16 VP" in hand[3]
            and "24 VP" in hand[4] and "Hand Echo is full" in hand[5], "V the Hand shares ONE ladder: 4, 6, 10, 16, 24, then full: %s" % [h_[:40] for h_ in hand])
    K.eq([float(Tr.echo(p, I("Hand.farming"))), float(Tr.echo(p, I("Hand.cooking"))), float(Tr.echo(p, I("Hand.alchemy"))), int(Tr.handTotal(p))],
         [34.0, 8.0, 8.0, 5], "V each Hand skill counts its own ranks' strengths (Farming 34, Cooking 8, Alchemy 8)")
    heads = [buy("Void.head", i) for i in range(4)]
    K.check([h_[:1] for h_ in heads] == ["+", "+", "+", "-"] and "max rank" in heads[3] and "20 VP" in heads[0] and "45 VP" in heads[2], "V Head Start: 20, 30, 45, then max")
    t1 = buy("Mining.tool", 0)
    K.check(t1.startswith("+Void-Forged Pick rank 1 bought - 4 VP"), "V a tool node: 4 VP (%s)" % t1)
    p = St.readNow(k)
    left = int(Tr.held(p))
    K.check(left == 200 - 12 - 60 - 95 - 4 and int(Tr.big(p, "vpSpent")) == 12 + 60 + 95 + 4, "V held / spent add up (%d)" % left)
    K.check(buy("Void.insight", 1).startswith("+Void Insight rank 2 bought - 20 VP"), "V Void Insight rank 2: 20 VP")
    left -= 20
    poor = buy("Void.insight", 2)
    K.check(poor.startswith("-Not enough Void Particles: this rank costs 32 VP, you hold %d." % left), "V not enough VP (%s)" % poor)
    # ---------------------------------------------------------------- keep buff + the bridge answers
    K.eq([str(Tr.keepTxt(76)), str(Tr.keepTxt(0)), float(Tr.keepPct(4000))], ["Holding 76 VP: +19 % XP", "Holding 0 VP: +0 % XP", 1000.0],
         "V keep = +0.25 % a VP, no cap (4000 VP = +1000 %)")
    R("RbPub").publish(U)
    sb = Cfg.BRIDGE.get("skill:bonus:" + k)
    m = dict((str(a_), float(b_)) for a_, b_ in dict(sb.get("rebirth")).items()) if sb is not None and sb.get("rebirth") is not None else {}
    allp = 14.0 + 0.25 * left
    K.check(abs(m.get("xp.mining", 0) - allp / 100) < 1e-9 and abs(m.get("xp.ranching", 0) - (allp + 34) / 100) < 1e-9
            and abs(m.get("xp.cooking", 0) - (allp + 8) / 100) < 1e-9 and abs(m.get("xp.acrobatics", 0) - allp / 100) < 1e-9
            and "xp.exploration" not in m and "xp.combat" not in m and len(m) == 11 and not any(x.startswith("dd.") for x in m),
            "V skill:bonus source rebirth: Insight + keep + Echo for 11 keys, never Exploration, no double drops; F xp.combat absent with no Combat Echo (class XP gets all XP through classxp only): %s" % m)
    fs, fnode, fvp, fdust = R("RbFn")(6), R("RbFn")(2), R("RbFn")(9), R("RbFn")(3)
    stat = lambda nm: float(fs.apply(OA(U, nm)))
    K.check(abs(stat("classxp") - allp) < 1e-9 and stat("health") == 0.0 and stat("mana") == 0.0 and stat("all") == 6.0 and abs(stat("allxp") - allp) < 1e-9
            and abs(stat("keepxp") - 0.25 * left) < 1e-9 and stat("headstart") == 3.0 and stat("vp") == float(left) and abs(stat("petxp") - allp) < 1e-9,
            "V rebirth:fn:stat classxp / allxp / keepxp / petxp / headstart / vp; health / mana 0; all = 3 % x 2 rebirths")
    K.check(int(fnode.apply(OA(U, "Mining.tool"))) == 1 and int(fnode.apply(OA(U, "Mining.tool2"))) == 0 and int(fnode.apply(OA(U, "Mining.xp"))) == 0
            and int(fvp.apply(U)) == left and float(fdust.apply(OA(U, "Mining"))) == 2.0, "V rebirth:fn:node (SkyyGear ids), rebirth:fn:vp, dustmult x2 (n >= 1)")
    # ---------------------------------------------------------------- RESPEC (a Void Charm from the bag)
    Cfg.BRIDGE.put("acc:defs", DEFS)
    bag = Bag(["Skyy_Talisman_Lantern_Epic", "Skyy_Talisman_Speed_Uncommon", "Skyy_Talisman_Lantern_Common"])
    Cfg.BRIDGE.put("acc:fn:bag", bag)
    p = St.readNow(k)
    sp = int(Tr.big(p, "vpSpent"))
    K.eq([str(x) for x in Tr.charmPick(U, k, 1)], ["Skyy_Talisman_Lantern_Common"], "V the respec takes the LOWEST rarity charm")
    K.check(str(Tr.charmNames(Tr.charmPick(U, k, 2))) == "Lantern (Normal), Speed (Unique)", "V the names the page shows")
    K.check("changed meanwhile" in str(Tr.respec(k, U, sp + 1, "Skyy_Talisman_Lantern_Common", False, True)) and bag.ids[2] == "Skyy_Talisman_Lantern_Common", "V respec: a stale page = refused, nothing taken")
    rx = str(Tr.respec(k, U, sp, "Skyy_Talisman_Speed_Uncommon", False, True))
    K.check(rx.startswith("-Your Void Charms changed - look again (a respec now takes Lantern (Normal))") and bag.ids[2] == "Skyy_Talisman_Lantern_Common"
            and not any(c_[0] == "take" for c_ in bag.calls) and props(f).get("vpSpent") == str(sp), "F respec: the bag now picks another charm than the page named = refused, nothing taken (%s)" % rx)
    rr = str(Tr.respec(k, U, sp, "Skyy_Talisman_Lantern_Common", False, True))
    d = props(f)
    K.check(rr.startswith("+Respec done: 11 ranks reset, %d VP back - the void took your Lantern (Normal)" % sp) and bag.ids[2] is None
            and d["vp"] == str(left + sp) and "vpSpent" not in d and not any(x.startswith("node.") for x in d) and d["respecs"] == "1",
            "V RESPEC: 1 Void Charm (the Common Lantern) taken, every spent VP back, every rank 0 (%s)" % rr)
    K.check("Nothing to respec" in str(Tr.respec(k, U, 0, None, False, True)), "V nothing spent = nothing to respec")
    buy("Class.echo", 0)
    bag.ids = ["Skyy_Talisman_Furnace_T3", "Skyy_Talisman_Eternal_Flame"]
    K.check(len(list(Tr.charmPick(U, k, 1))) == 0 and "your Void Charms hold 0 it can take" in str(Tr.respec(k, U, 4, "", False, True))
            and bag.ids == ["Skyy_Talisman_Furnace_T3", "Skyy_Talisman_Eternal_Flame"], "F charms outside acc:defs (Furnace Charm tiers, Eternal Flame) are NEVER taken")
    bag.ids = []
    K.check("your Void Charms hold 0" in str(Tr.respec(k, U, 4, "", False, True)), "V no charm in the bag = refused")
    Cfg.BRIDGE.remove("acc:fn:bag")
    K.check("SkyyAccessories (Void Charms) is not loaded" in str(Tr.respec(k, U, 4, "", False, True)), "V no SkyyAccessories = refused")
    bag2 = Bag(["Skyy_Talisman_Speed_Uncommon"])
    Cfg.BRIDGE.put("acc:fn:bag", bag2)
    tmpd = os.path.join(pl, k + ".properties.tmp")
    os.makedirs(tmpd)
    rf = str(Tr.respec(k, U, 4, "Skyy_Talisman_Speed_Uncommon", False, True))
    os.rmdir(tmpd)
    K.check(rf.startswith("-Could not save - nothing changed, nothing taken") and bag2.ids == ["Skyy_Talisman_Speed_Uncommon"]
            and not any(c_[0] == "take" for c_ in bag2.calls) and props(f).get("node.Class.echo") == "1",
            "F the profile is saved BEFORE the take: a save failure = no take at all, nothing changed (%s)" % rf)
    bag2.refuse_take = True
    rt = str(Tr.respec(k, U, 4, "Skyy_Talisman_Speed_Uncommon", False, True))
    d = props(f)
    K.check("changed meanwhile - nothing was taken" in rt and d.get("node.Class.echo") == "1" and d.get("vpSpent") == "4" and d.get("respecs") == "1"
            and bag2.ids == ["Skyy_Talisman_Speed_Uncommon"], "F the bag refuses the take AFTER the save = the old profile saved back (rank + vpSpent), the charm kept: %s" % d)
    bag2.refuse_take = False
    vbig = dict(d)
    vbig["vp"], vbig["vpSpent"] = "999999990", "999999990"
    open(f, "w").write("".join("%s=%s\n" % kv_ for kv_ in vbig.items()))
    St.CACHE.clear()
    rbig = str(Tr.respec(k, U, 999999990, "Skyy_Talisman_Speed_Uncommon", False, True))
    K.check(rbig.startswith("+Respec done") and props(f)["vp"] == "1000000000" and bag2.ids == [None], "F respec: VP clamped at 1,000,000,000 (%s / %s)" % (rbig[:60], props(f).get("vp")))
    open(f, "w").write("".join("%s=%s\n" % kv_ for kv_ in d.items()))
    St.CACHE.clear()
    # fix round 2: a 2-charm respec whose 2nd take fails and whose 1st charm cannot go back = the respec STAYS (VP back), never charm gone + old ranks
    Cfg.RESPEC_CHARMS = 2
    bag3 = Bag(["Skyy_Talisman_Lantern_Common", "Skyy_Talisman_Speed_Uncommon"])
    Cfg.BRIDGE.put("acc:fn:bag", bag3)
    bag3.takes_ok, bag3.refuse_put = 1, True
    r2c = str(Tr.respec(k, U, 4, "Skyy_Talisman_Lantern_Common,Skyy_Talisman_Speed_Uncommon", False, True))
    d2c = props(f)
    K.check(r2c.startswith("+Respec done: 1 ranks reset, 4 VP back - the void took your Lantern (Normal) (your Void Charms changed meanwhile")
            and "node.Class.echo" not in d2c and "vpSpent" not in d2c and bag3.ids[0] is None and bag3.ids[1] == "Skyy_Talisman_Speed_Uncommon",
            "F fix round 2: 2 charms, take 2 fails, charm 1 cannot go back = the respec stays and names the charm taken (%s / %s)" % (r2c, d2c))
    open(f, "w").write("".join("%s=%s\n" % kv_ for kv_ in d.items()))
    St.CACHE.clear()
    bag3.ids, bag3.takes_ok, bag3.refuse_put, bag3.calls = ["Skyy_Talisman_Lantern_Common", "Skyy_Talisman_Speed_Uncommon"], 1, False, []
    r2d = str(Tr.respec(k, U, 4, "Skyy_Talisman_Lantern_Common,Skyy_Talisman_Speed_Uncommon", False, True))
    K.check("changed meanwhile - nothing was taken" in r2d and props(f).get("node.Class.echo") == "1" and bag3.ids[0] == "Skyy_Talisman_Lantern_Common"
            and [c_[0] for c_ in bag3.calls].count("put") == 1, "F ... the same with the put accepted: charm 1 back, the old profile back (%s)" % r2d)
    Cfg.BRIDGE.put("acc:fn:bag", bag2)
    Cfg.RESPEC_CHARMS = 0
    rfree = str(Tr.respec(k, U, 4, None, False, True))
    K.check(rfree.startswith("+Respec done: 1 ranks reset, 4 VP back.") and "took" not in rfree, "V nexus.respecCharms 0 = a free respec (%s)" % rfree)
    Cfg.RESPEC_CHARMS = 1
    # ---------------------------------------------------------------- /rebirthadmin points / reset / refund
    run = lambda line: [str(x) for x in R("RbAdmin").run(U, line, 0)]
    a1 = run("points 50")
    K.check(a1[0].startswith("+Added 50 test Void Particles") and int(Tr.held(St.readNow(k))) == left + sp + 50, "V points 50 (%s)" % a1)
    buy("Combat.echo", 0)
    R("RbPub").publish(U)
    mc = dict((str(a_), float(b_)) for a_, b_ in dict(Cfg.BRIDGE.get("skill:bonus:" + k).get("rebirth")).items())
    K.check(abs(mc.get("xp.combat", 0) - 0.08) < 1e-9 and mc.get("xp.mining", 0) > 0.08 and abs(stat("classxp") - stat("allxp")) < 1e-9,
            "F xp.combat = Combat Echo rank 1 ALONE (+8 %%), Insight + keep only via classxp: %s" % mc.get("xp.combat"))
    a2 = run("refund")
    K.check(a2[0].startswith("+Respec done: 1 ranks reset, 4 VP back") and "took" not in a2[0], "V refund = an admin respec, no charm (%s)" % a2)
    a3 = run("points reset")
    d = props(f)
    K.check(a3[0].startswith("+Reset: 0 ranks and") and "vp" not in d and "vpSpent" not in d, "V points reset (%s)" % a3)
    K.check(run("points")[0].startswith("-Usage: /rebirthadmin points <1-100000|reset>") and run("refund all")[0].startswith("-Usage: /rebirthadmin refund")
            and run("points 0")[0].startswith("-Usage"), "V the usage lines")
    K.check(any("points <n>" in x for x in run("help")), "V help names the new forms")
    # ---------------------------------------------------------------- decide (VP from the prepared facts)
    J_ = R("RbJ")

    def decide(newN, facts, mode="live"):
        j = J_()
        j.bad, j.k, j.newN, j.mode, j.tx = False, k, newN, mode, "tx0000000000000-abcdef"
        j.prepared.put("skills", facts)
        j.prepared.put("coins", "purse=0")
        j.prepared.put("bank", "bank=0")
        return [str(x) for x in Tx.decide(j)]
    F1 = "arm.class=4000/1000/100/100;arm.mining=500/500/50/50;arm.foraging=10/500/5/50;arm.farming=100/300/20/50;arm.ranching=200/300/30/50;arm.orchard=10/300/2/50"
    d1 = decide(1, F1)
    K.check(d1[0] == "commit" and d1[1].startswith("vp=44;vpSkills=1;vpOver=12;bonus="), "V decide rebirth 1: 20 + 10 + 2 x 1 (Mining; Farming + Ranching + Orchard pooled 310 / 900 = not at the cap) + 12 (class x4): %s" % d1)
    d1b = decide(1, F1.replace("arm.orchard=10/300/2/50", "arm.orchard=600/300/50/50"))
    K.check(d1b[1].startswith("vp=46;vpSkills=2;"), "V ... the pooled Farming arm at its cap (910 / 900) counts: %s" % d1b[1][:24])
    d6 = decide(6, F1)
    d7 = decide(7, "arm.class=900/1000/90/100", "force")
    K.check(d6[1].startswith("vp=94;") and d7[0] == "commit" and d7[1].startswith("vp=90;vpSkills=0;vpOver=0;"), "V rebirth 6 + 7 (no limit): %s / %s" % (d6[1][:30], d7[1][:30]))
    K.check(decide(1, "arm.class=900/1000/90/100")[0] == "abort", "V live: the class below its cap = abort")
    Cfg.MAX = 5
    K.check(decide(6, F1)[0] == "abort", "V a limit of 5: rebirth 6 = abort (past the max)")
    Cfg.MAX = 0
    allcap = ";".join("arm.%s=9/9/50/50" % s_ for s_ in ("mining", "foraging", "farming", "smithing", "alchemy", "fishing", "cooking"))
    K.check(decide(2, "arm.class=1000/1000/100/100;" + allcap)[1].startswith("vp=54;vpSkills=7;vpOver=0;"), "V every counted skill at its cap: +14")
    # ---------------------------------------------------------------- applyOwn: VP + idempotent; an open 0.3.x decision -> 1:1
    open(f, "w").write("n=5\nv=4\nvp=10\n")

    def apply(newN, rewards, tx):
        j = J_()
        j.bad, j.k, j.newN, j.tx, j.rewards = False, k, newN, tx, rewards
        return Tx.applyOwn(k, j)
    e1 = apply(6, "vp=96;vpSkills=2;vpOver=12;bonus=0;max=30000;bal=0", "tx0000000000001-aaaaaa")
    e2 = apply(6, "vp=96;vpSkills=2;vpOver=12;bonus=0;max=30000;bal=0", "tx0000000000001-aaaaaa")
    d = props(f)
    K.check(e1 is None and e2 is None and d["vp"] == "106" and d["vpEarned"] == "96" and d["n"] == "6" and d["title"] == "Void-Touched VI"
            and "vp=96" in d["hist.6"] and d["cos.6"] == "1", "V step 4: +96 VP, earned, n 6, title, cosmetic; run twice = once (%s)" % d)
    apply(7, "pts.Class=12;pts.Mining=8;pts.Cooking=0;bonus=0;max=30000;bal=0", "tx0000000000002-bbbbbb")
    K.check(props(f)["vp"] == "126", "V an open 0.3.x decision (pts.Class 12 + pts.Mining 8) = +20 VP 1:1")
    # ---------------------------------------------------------------- THE MIGRATION (the first read of a 0.3.x file)
    k2 = str(JClass("java.util.UUID").randomUUID()) + "-p2"
    f2 = os.path.join(pl, k2 + ".properties")
    oldb = b"#SkyyRebirth 0.3.6\r\nn=2\r\npts.Class=30\r\npts.Mining=12\r\nspent.Mining=15\r\nspent.Class=6\r\nnode.Mining.xp=3\r\nnode.Class.key=1\r\nnode.Mining.tool=2\r\ntitle=Void Ascendant\r\nhist.1=1 tx=a\r\n"
    open(f2, "wb").write(oldb)
    p2 = St.readNow(k2)
    d2 = props(f2)
    bk = os.path.join(home, "vp-backup")
    baks = os.listdir(bk) if os.path.isdir(bk) else []
    logl = open(os.path.join(home, "vp-migration.log"), encoding="utf-8").read().splitlines() if os.path.isfile(os.path.join(home, "vp-migration.log")) else []
    K.check(p2 is not None and d2.get("vp") == "63" and not any(x.startswith(("pts.", "spent.", "node.")) for x in d2) and d2.get("title") == "Void-Touched II"
            and d2.get("v") == "4" and d2.get("vpMig", "").startswith("0.4.0 pts=42 spent=21 nodes=3 vp=63") and d2.get("hist.1") == "1 tx=a",
            "V MIGRATION: 42 points left + 21 spent -> 63 VP, the old nodes gone, Void Ascendant -> Void-Touched II, v=4 + vpMig, history kept: %s" % d2)
    K.check(len(baks) == 1 and open(os.path.join(bk, baks[0]), "rb").read() == oldb and baks[0].startswith(k2 + ".properties."),
            "V the backup FIRST, byte-identical: %s" % baks)
    K.check(len(logl) == 1 and k2 in logl[0] and "+63 VP" in logl[0] and "UNDO:" in logl[0] and baks[0] in logl[0], "V one vp-migration.log line with the Undo: %s" % logl)
    St.CACHE.clear()
    p2b = St.readNow(k2)
    St.get(k2)
    K.check(int(Mg.MIGS.get()) == 1 and len(os.listdir(bk)) == 1 and len(open(os.path.join(home, "vp-migration.log")).read().splitlines()) == 1
            and int(Tr.held(p2b)) == 63, "V run once: reading it again changes nothing")
    k3 = str(JClass("java.util.UUID").randomUUID())
    f3 = os.path.join(pl, k3 + ".properties")
    open(f3, "wb").write(b"n=3\nv=4\nvp=9\nvpSpent=24\nnode.Void.insight=1\nnode.Class.echo=2\n")
    b3 = open(f3, "rb").read()
    St.readNow(k3)
    K.check(open(f3, "rb").read() == b3 and int(Mg.MIGS.get()) == 1, "V a v=4 file is never migrated (untouched bytes)")
    k4 = str(JClass("java.util.UUID").randomUUID())
    f4 = os.path.join(pl, k4 + ".properties")
    open(f4, "wb").write(b"n=3\nv=4\nvp=9\nvpSpent=24\nnode.Void.insight=1\nnode.Mining.dd=2\npts.Mining=5\n")
    St.readNow(k4)
    d4 = props(f4)
    K.check(d4.get("vp") == "38" and not any(x.startswith("node.") for x in d4) and "vpSpent" not in d4 and "pts.Mining" not in d4,
            "F the rollback case (v=4 + 0.3.6 points): every node line gone, +5 points + 24 spent VP back = 38 (VP conserved): %s" % d4)
    k4b = str(JClass("java.util.UUID").randomUUID())
    f4b = os.path.join(pl, k4b + ".properties")
    open(f4b, "wb").write(b"n=3\nv=4\nvp=0\nvpSpent=10\nnode.Mining.tool=3\nspent.Mining=2\n")
    St.readNow(k4b)
    d4b = props(f4b)
    K.check(d4b.get("vp") == "12" and "node.Mining.tool" not in d4b and "vpSpent" not in d4b, "F rollback then forward with a shared tool id: ranks gone, 10 + 2 VP back - never ranks AND refund: %s" % d4b)
    k5 = str(JClass("java.util.UUID").randomUUID())
    f5 = os.path.join(pl, k5 + ".properties")
    b5 = b"n=1\npts.Class=8\n"
    open(f5, "wb").write(b5)
    os.makedirs(os.path.join(home, "vp-backup-blocked"))
    open(os.path.join(home, "vp-backup-blocked", "x"), "w").write("a file where the folder should be")
    Mg.TEST_FAIL_BACKUP = True
    q5 = St.readNow(k5)
    K.check(q5 is None and St.BAD.containsKey(k5) and open(f5, "rb").read() == b5 and str(St.save(k5, JClass("java.util.Properties")())).find("not overwritten") >= 0
            and R("RbFn")(6).apply(OA(k5, "classxp")) is None, "V a backup failure: null, unreadable (never overwritten, no stat answer), the file untouched")
    Mg.TEST_FAIL_BACKUP = False
    logf = os.path.join(home, "vp-migration.log")
    nlog = len(open(logf, encoding="utf-8").read().splitlines())
    Mg.TEST_FAIL_WRITE = True
    q5w = St.readNow(k5)
    Mg.TEST_FAIL_WRITE = False
    ll = open(logf, encoding="utf-8").read().splitlines()
    K.check(q5w is None and open(f5, "rb").read() == b5 and len(ll) == nlog + 2 and "UNDO:" in ll[-2] and k5 in ll[-1] and "THE WRITE FAILED" in ll[-1],
            "F the log line is written BEFORE the file; a failed write = the file untouched + a WRITE FAILED line: %s" % ll[-1:])
    q5b = St.readNow(k5)
    K.check(q5b is not None and props(f5).get("vp") == "8" and not St.BAD.containsKey(k5), "V ... the next read migrates it")
    # through the cache path (RbStore.get on SkyyRebirth-IO in play = loadNow)
    k6 = str(JClass("java.util.UUID").randomUUID())
    open(os.path.join(pl, k6 + ".properties"), "wb").write(b"n=1\nspent.Fishing=7\nnode.Fishing.tool=1\n")
    g6 = St.get(k6)
    K.check(int(Tr.held(g6)) == 7 and int(Tr.lv(g6, I("Fishing.tool"))) == 0 and props(os.path.join(pl, k6 + ".properties")).get("v") == "4",
            "V the cache read (RbStore.get) migrates too; the old Fishing.tool level is refunded, not kept")
    # fix round 2: a FAILED load through the cache (RbStore.get -> loadNow caches EMPTY) answers NOTHING (never 0 rebirths), is retried, heals
    k7 = str(JClass("java.util.UUID").randomUUID())
    f7 = os.path.join(pl, k7 + ".properties")
    b7 = b"n=4\npts.Mining=6\n"
    open(f7, "wb").write(b7)
    Mg.TEST_FAIL_BACKUP = True
    g7 = St.get(k7)
    fns = dict((m_, R("RbFn")(m_)) for m_ in (0, 1, 2, 3, 6, 7, 8, 9))
    ans = [fns[0].apply(k7), fns[1].apply(OA(k7, "Mining", 50)), fns[2].apply(OA(k7, "Mining.tool")), fns[3].apply(OA(k7, "Mining")),
           fns[6].apply(OA(k7, "classxp")), fns[7].apply(k7), fns[8].apply(k7), fns[9].apply(k7)]
    K.check(bool(St.bad(k7)) and all(a_ is None for a_ in ans) and open(f7, "rb").read() == b7 and St.NEXT.containsKey(k7),
            "F fix round 2: a failed migration through the cache = every rebirth:fn answer null (count, cap, node, dustmult, stat, title, cos, vp), file untouched, a retry time: %s" % [str(a_) for a_ in ans])
    St.get(k7)
    St.get(k7)
    K.check(bool(St.bad(k7)) and int(St.TRIES.get(k7)) == 1, "F ... not retried before its time (1 min)")
    Mg.TEST_FAIL_BACKUP = False
    hv = St.readNow(k7)
    K.check(hv is not None and not bool(St.bad(k7)) and int(fns[0].apply(k7)) == 4 and int(fns[9].apply(k7)) == 6 and not St.NEXT.containsKey(k7),
            "F ... a later good read (a job's readNow) HEALS the cache: 4 rebirths, 6 VP answered at once")
    k8 = str(JClass("java.util.UUID").randomUUID())
    open(os.path.join(pl, k8 + ".properties"), "wb").write(b"n=2\nspent.Mining=3\n")
    Mg.TEST_FAIL_BACKUP = True
    St.get(k8)
    Mg.TEST_FAIL_BACKUP = False
    St.NEXT.put(k8, Ln(0))
    g8 = St.get(k8)
    K.check(not bool(St.bad(k8)) and int(Tr.held(g8)) == 3 and int(fns[0].apply(k8)) == 2 and not bool(St.bad(k8)) and not St.TRIES.containsKey(k8),
            "F ... the retry (its time come) migrates it through the cache: 2 rebirths, 3 VP")
    # RbPub: the ACTIVE profile's load fails -> its last rebirth:n / skill:bonus stay (never a false 0)
    R("RbPub").publish(U)
    nkey = "rebirth:n:" + str(U)
    n_before = Cfg.BRIDGE.get(nkey)
    sb_before = Cfg.BRIDGE.get("skill:bonus:" + k)
    rb_before = None if sb_before is None else sb_before.get("rebirth")
    fk = os.path.join(pl, k + ".properties")
    keep_k = open(fk, "rb").read()
    open(fk, "wb").write(b"n=9\npts.Class=1\n")
    St.CACHE.clear()
    Mg.TEST_FAIL_BACKUP = True
    R("RbPub").publish(U)
    Mg.TEST_FAIL_BACKUP = False
    sb_after = Cfg.BRIDGE.get("skill:bonus:" + k)
    K.check(n_before is not None and bool(St.bad(k)) and Cfg.BRIDGE.get(nkey) == n_before and (sb_after is None and rb_before is None or sb_after.get("rebirth") == rb_before),
            "F fix round 2: RbPub keeps the active profile's last rebirth:n (%s) + skill:bonus while its load failed" % n_before)
    # /rebirthadmin status on the world thread: RbStore.peek - a plain read, the 0.3 file NOT migrated there, named
    stl = [str(x_) for x_ in Tx.status(U)]
    K.check(any("still holds 0.3 tree points" in x_ for x_ in stl) and open(fk, "rb").read() == b"n=9\npts.Class=1\n" and any("rebirths 9" in x_ for x_ in stl),
            "F fix round 2: status reads RbStore.peek (no migration / fsync on the world thread): %s" % stl[:2])
    open(fk, "wb").write(keep_k)
    St.CACHE.clear(); St.BAD.clear(); St.NEXT.clear(); St.TRIES.clear()
    # ---------------------------------------------------------------- a WHOLE rebirth 6 -> 7 through the journal (fake parts), admin + live
    open(f, "w").write("n=6\nv=4\nvp=3\n")
    St.CACHE.clear()
    TOLD = JClass("java.util.ArrayList")()
    Tx.TEST_TOLD = TOLD
    parts = {"skills": Part("skills", "arm.class=4000/1000/100/100;arm.mining=50/50/50/50"), "coins": Part("coins", "purse=0"),
             "bank": Part("bank", "bank=0"), "gear": Part("gear", "x=1")}
    for n_, p_ in parts.items():
        Cfg.BRIDGE.put("rebirth:part:" + n_, p_)
    ra = str(Tx.adminStart(U, -1))
    d = props(f)
    K.check(ra.startswith("+Rebirth tx") and d["n"] == "7" and d["vp"] == str(3 + 20 + 70 + 2 + 12) and d["title"] == "Void-Touched VII"
            and not os.path.isfile(os.path.join(home, "journal", k + ".journal")) and all("commit" in p_.ops for p_ in parts.values()),
            "V a whole rebirth 6 -> 7 (admin): +104 VP (20 + 70 + 2 + 12), the journal done, every part committed (%s)" % d.get("vp"))
    K.check(any("+104 Void Particles" in str(t_) and "Holding 107 VP: +26.75 % XP" in str(t_) for t_ in TOLD), "V the done line: %s" % [str(t_)[:160] for t_ in TOLD])
    Cfg.BRIDGE.put("bazaar:fn:wouldclose", Const("ok:0:0:0:0"))
    Cfg.BRIDGE.put("ah:fn:wouldclose", Const("ok:0:0:0:0"))
    rl = str(Tx.startNow(k, U))
    K.check(rl.startswith("+tx") and props(f)["n"] == "8" and props(f)["vp"] == str(107 + 20 + 80 + 2 + 12), "V a live rebirth 7 -> 8 (markets clear): +114 VP (%s)" % rl)
    K.eq([int(Mt.cap(50, "Mining", n_)) for n_ in (0, 5, 6, 8)] + [int(Mt.cap(50, "Exploration", 8))], [50, 100, 110, 130, 50],
         "V the level cap math is unchanged (50 + 10 x n; SkyySkills levels.capMax clamps it at 100); Exploration never")
    K.check(int(Cfg.lim()) == 2147483647 and bool(Cfg.ON), "V rebirths unlimited (0.3.6) and rebirth ON by default")
    Tx.TEST_TOLD = None
    K.save()


def run_page(out, jar, scratch, _home):
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    from jpype import JClass, JArray
    K = HK.Child(out)
    Bag, Part, Const = fakes()
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Cfg, St, Tr = R("RbCfg"), R("RbStore"), R("RbTree")
    home, pl, U, k = world(scratch, "p")
    f = os.path.join(pl, k + ".properties")
    open(f, "w").write("n=2\nv=4\nvp=76\nvpSpent=36\nnode.Void.insight=2\nnode.Hand.farming=1\nnode.Mining.tool=1\n")
    Cfg.BRIDGE.put("acc:defs", DEFS)
    bag = Bag(["Skyy_Talisman_Lantern_Common"])
    Cfg.BRIDGE.put("acc:fn:bag", bag)
    Cfg.PERM_TEST = Const(JClass("java.lang.Boolean").TRUE)
    LIN_W = SUI.DETAIL_W - 24 - 8

    def built(pg, what):
        b_, e_ = UCB(), UEB()
        pg.build(None, b_, e_, None)
        c = cmds_of(b_)
        ev = events_of(e_)
        apps = SUI.Appends([(None if s_ is None else s_.lstrip("#"), t_) for ty, s_, t_, d_ in c if t_ is not None and ty and "Append" in ty])
        sets = [(s_, d_) for ty, s_, t_, d_ in c if ty == "Set"]
        try:
            SUI.check_page(apps, "Skyy")
            SUI.check_sky_paths(apps, tab_icons=True)
            info = SUI.assert_menu_page(apps, hub="character", what="P " + what, sets=[(s_, unq(d_)) for s_, d_ in sets])
            K.check(info["rows"] == 2 and info["subs"] == 1, "P %s: check_page + sky paths + assert_menu_page (1600 x 980, rows 1 + 2, one sub row)" % what)
        except Exception as ex:
            K.check(False, "P %s: the page checks: %s" % (what, ex))
        ids = set()
        for _p, mk in apps:
            ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
        bad = [s_ for s_, _d in sets if s_.lstrip("#").split(".")[0] not in ids] + [s_ for s_, _d in ev if s_.lstrip("#") not in ids]
        K.check(not bad, "P %s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(ev), bad[:4]))
        return c, ev, dict((s_, unq(d_)) for s_, d_ in sets)

    def fits(sets, what):
        rows = {"SkyyRbNv": 13, "SkyyRbPt": 13, "SkyyRbVp": 13, "SkyyRbReq": 13}
        over = []
        for s_, v_ in sets.items():
            idv = s_.lstrip("#").split(".")[0]
            if not s_.endswith(".Text") or not any(idv.startswith(r_) for r_ in rows):
                continue
            lines = SUI.text_lines(v_, LIN_W, SUI.fs(16 if idv == "SkyyRbNvName" else 13), bold=idv in ("SkyyRbNvName", "SkyyRbNvSub", "SkyyRbNvLevel", "SkyyRbNvStatus"))
            mx = {"SkyyRbNvLive": 3, "SkyyRbNvStatus": 3, "SkyyRbNvNow": 2, "SkyyRbNvNext": 2, "SkyyRbNvKeep": 2, "SkyyRbPtHand": 2}.get(idv, 1)
            if lines > mx:
                over.append((idv, v_, lines))
        K.check(not over, "P %s: every left-panel text fits its rows at 424 px: %s" % (what, over[:3]))
    nodes = ["SkyyRbN%dB" % i for i in range(21)]
    pg = R("RbPage")(U, "hub")
    c0, ev0, s0 = built(pg, "rebirth view")
    K.check(not any(c_[0] == "list" for c_ in bag.calls), "F the rebirth view never reads the Void Charms bag (no bag lock on every rebuild)")
    tipc = s0.get("#SkyyRbN%dB.TooltipText" % int(Tr.idx("Combat.echo")), "")
    K.check("Coming with SkyySkills - not buyable yet" in tipc, "F a node with no live reader: the hover says so: %r" % tipc[-90:])
    binds = sorted(s_.lstrip("#") for s_, _d in ev0)
    K.check(all(n_ in binds for n_ in nodes) and "SkyyRbNexusB" in binds and "SkyyRbClose" in binds and "SkyyRbN21B" not in binds, "P rebirth view: 21 node bindings + Nexus + Close")
    K.check(s0.get("#SkyyRbHint.Text", "").startswith("Holding 76 VP: +19 % XP - spent 36 VP"), "P THE VP COUNTER at the top: %r" % s0.get("#SkyyRbHint.Text"))
    tip0 = s0.get("#SkyyRbN0B.TooltipText", "")
    K.check("Void Insight - rank 2 / 5" in tip0 and "Next rank: +24 % all XP for 32 VP" in tip0 and "Keeping those 32 VP instead: +8 % all XP" in tip0
            and "You hold 76 VP (+19 % XP)" in tip0, "P the node hover: cost, what it gives, keeping instead: %r" % tip0)
    K.check(all(("#SkyyRbN%dB.TooltipText" % i) in s0 for i in range(21)), "P every node has its hover text")
    K.check(s0.get("#SkyyRbVp0.Text", "").startswith("Void Particles  +") and s0.get("#SkyyRbVp1.Text", "") == "Rebirth 3: 20 + 10 x 3 = 50 VP", "P What you would get = the VP sum: %r" % [s0.get("#SkyyRbVp%d.Text" % i) for i in range(4)])
    fits(s0, "rebirth view")
    pg.handleDataEvent(None, None, '{"a":"n0"}')
    c1, ev1, s1 = built(pg, "node view")
    b1 = sorted(s_.lstrip("#") for s_, _d in ev1)
    K.check("SkyyRbBuy" in b1 and "SkyyRbRespec" in b1 and "SkyyRbSub0" in b1, "P node view: Buy + Respec bound (VP enough, a charm in the bag)")
    K.check(s1.get("#SkyyRbNvKeep.Text") == "Keeping those 32 VP instead: +8 % all XP" and s1.get("#SkyyRbNvCost.Text") == "Cost: 32 VP"
            and s1.get("#SkyyRbNvLevel.Text") == "Rank 2 / 5" and s1.get("#SkyyRbPtRe.Text") == "Respec: 1 Void Charm (Lantern (Normal))",
            "P node view lines: %s" % dict((x, s1.get("#SkyyRbNv%s.Text" % x)) for x in ("Level", "Now", "Next", "Cost", "Have", "Keep", "Status")))
    fits(s1, "node view")
    pg.handleDataEvent(None, None, '{"a":"buy"}')
    K.check(str(pg.status).startswith("+Void Insight rank 3 bought - 32 VP spent (Holding 44 VP: +11 % XP)"), "P Buy from the page (inline job): %s" % pg.status)
    pg.handleDataEvent(None, None, '{"a":"n%d"}' % int(Tr.idx("Hand.cooking")))
    c2, ev2, s2 = built(pg, "node view (Hand)")
    K.check(s2.get("#SkyyRbNvLevel.Text") == "Rank 0 / 5 - Hand 1 / 5" and s2.get("#SkyyRbNvCost.Text") == "Cost: 6 VP" and s2.get("#SkyyRbPtHand.Text") == "Hand: Farming +8 %",
            "P a Hand node: the shared rank count + the 2nd Hand cost: %s" % [s2.get("#SkyyRbNvLevel.Text"), s2.get("#SkyyRbNvCost.Text"), s2.get("#SkyyRbPtHand.Text")])
    sp = int(Tr.big(St.readNow(k), "vpSpent"))
    r1 = str(pg.respec(1000000))
    K.check(r1 == "=armed" and "Press Respec again within 10 s: takes Lantern (Normal), gives %d VP back." % sp in str(pg.status), "P Respec press 1 = armed: %s" % pg.status)
    K.check(str(pg.respec(1000300)) == "=armed", "P a double-click (< 0.8 s) is not a confirm")
    r2 = str(pg.respec(1002000))
    d = props(f)
    K.check(r2.startswith("+Respec done: 5 ranks reset, %d VP back - the void took your Lantern (Normal)" % sp) and bag.ids == [None] and "vpSpent" not in d
            and d["vp"] == str(44 + sp), "P Respec press 2 (1 s later): done, the charm taken, every VP back: %s" % r2)
    c3, ev3, s3 = built(pg, "node view after the respec")
    K.check("SkyyRbRespec" not in [s_.lstrip("#") for s_, _d in ev3] and s3.get("#SkyyRbPtRe.Text") == "Respec: nothing spent yet", "P after it: Respec unbound, nothing spent")
    # F a node with no live reader: no Buy binding, "coming with"
    pg.handleDataEvent(None, None, '{"a":"n%d"}' % int(Tr.idx("Beast.echo")))
    c4, ev4, s4 = built(pg, "node view (no reader)")
    K.check("SkyyRbBuy" not in [s_.lstrip("#") for s_, _d in ev4] and s4.get("#SkyyRbNvLive.Text", "").startswith("Coming with SkyyPets")
            and "is coming with SkyyPets" in s4.get("#SkyyRbNvStatus.Text", ""), "F Beastmastery Echo with no SkyyPets reader: Buy unbound, coming with: %s" % s4.get("#SkyyRbNvStatus.Text"))
    fits(s4, "node view (no reader)")
    # F the respec takes ONLY what the arming press named: the bag changes between the presses = refused, nothing taken
    open(f, "a").write("vpSpent=6\nnode.Class.echo=1\n")
    St.CACHE.clear()
    bag.ids = ["Skyy_Talisman_Speed_Uncommon"]
    pg.handleDataEvent(None, None, '{"a":"n0"}')
    built(pg, "node view (respec again)")
    K.check(str(pg.respec(2000000)) == "=armed" and "takes Speed (Unique)" in str(pg.status), "F arming names the charm the bag holds NOW: %s" % pg.status)
    bag.ids = ["Skyy_Talisman_Lantern_Common", "Skyy_Talisman_Speed_Uncommon"]
    rc = str(pg.respec(2002000))
    K.check(str(pg.status).startswith("-Your Void Charms changed - look again") and bag.ids == ["Skyy_Talisman_Lantern_Common", "Skyy_Talisman_Speed_Uncommon"]
            and props(f).get("vpSpent") == "6", "F the bag changed between the presses: refused, nothing taken: %s / %s" % (rc, pg.status))
    bag.ids = []
    K.check(str(pg.respec(2020000)) == "-cannot" and "Respec: your Void Charms hold 0 of 1." in str(pg.status), "F arming with an empty bag = refused at once: %s" % pg.status)
    pg.handleDataEvent(None, None, '{"a":"back"}')
    K.check(int(pg.view) == 0, "P YOUR REBIRTH = back")
    K.save()


def run_live(out, jar, scratch, home):
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    from jpype import JClass
    K = HK.Child(out)
    mods = os.path.dirname(home)
    cfgf = os.path.join(home, "config.properties")
    t0 = T34.tree(home)
    Cfg, path = T34.kit_home(home)
    calls = T34.setup_calls(jar)
    idx = lambda n: calls.index(n) if n in calls else -1
    K.check(0 <= idx("RbCfg.migOn") < idx("RbCfg.migMax") < idx("RbCfg.loadCfg") < idx("CfgPub.start"), "D setup(): migOn, migMax, loadCfg, CfgPub.start (unchanged order)")
    r0, r1 = str(Cfg.migOn(path(cfgf))), str(Cfg.migMax(path(cfgf)))
    c1 = str(Cfg.loadCfg(True))
    t1 = T34.tree(home)
    added = sorted(set(t1) - set(t0))
    K.check(int(Cfg.MAX) == 0 and int(Cfg.VP_BASE) == 20 and float(Cfg.KEEP) == 0.25 and str(Cfg.L_SKILL) == "8,11,15,20,26",
            "D start 1: no limit, the Void Particle defaults (the file has no vp.* lines): %s" % c1[:120])
    K.check(all(a_.startswith("config-history/") or a_ == "config-changes.log" for a_ in added), "D start 1 adds only config-history / change log: %s" % added)
    St = R("RbStore")
    St.DIR = JClass("java.nio.file.Paths").get(os.path.join(home, "players"))
    K.check(not os.path.isdir(os.path.join(home, "players")), "D the live world has no rebirth profile files yet (nothing to migrate)")
    r2 = str(Cfg.migMax(path(cfgf)))
    Cfg.loadCfg(True)
    JClass(RB + "CfgPub").start(JClass("java.nio.file.Paths").get(mods), None)
    JClass(RB + "CfgPub").flush()
    K.check(r2 == "" and T34.tree(home) == t1, "D start 2 + the config kit write nothing")
    K.notes.append("D live: %s | %s" % (r1[:100], c1[:100]))
    K.save()


if __name__ == "__main__":
    assert os.path.isfile(B.JAVASSIST), B.JAVASSIST
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=ADDED, removed=REMOVED,
           phases=[("vp", run_vp), ("page", run_page), ("live", run_live)], script=__file__, live=(LIVE_RB, "Skyy_SkyyRebirth"))
