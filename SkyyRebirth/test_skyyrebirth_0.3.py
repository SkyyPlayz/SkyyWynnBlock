"""SkyyRebirth 0.3 - harness for REBIRTH R4 (the Continue button: SkyyBazaar 0.1.11 bazaar:fn:closeall / wouldclose + SkyyAuctions 0.1.5
ah:fn:closeall / wouldclose, the step-0 order) and R8 (THE REBIRTH TREE) - tools/rebirth_0_3_patch.py.
Build first: python tools/rebirth_0_3_patch.py && python SkyyRebirth/build_skyyrebirth_0.3.py

    python SkyyRebirth/test_skyyrebirth_0.3.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Reuses the 0.2 harness's World (the REAL SkyyRebirth 0.3 + SkyySkills 0.4.36 + SkyyCoins 0.1.7 + SkyyBank 0.1.11 jars in one class loader on
scratch files), seed() and Checker (test_skyyrebirth_0.2.py, definitions only) and the 0.1.5 Auction House harness's record maker + Ah loader
(SkyyAuctions/test_skyyauctions_0.1.5.py) for a REAL SkyyAuctions 0.1.5 on a scratch folder; SkyyBazaar 0.1.11's real BzRebirthFn.
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.2 -> 0.3: exactly the planned members differ; RbTree, RbJob, RbRefresh added
  X   exec     EVERY NEW CODE PATH:
               TREE - the catalogue (88 nodes, ids, rows 3/3/2/2/1, Dust = <Arm>.dust, keystones); cost = ceil(1.08^k) recomputed here (+ a
               growth of 2 and the 1,000,000,000 cap); rows open at 8 levels (a chain, rowNeed clamped to the row); fx texts; node states;
               BUY rules: switched off / no node / locked row / not enough points / a changed level (a duplicate click) / max level / a
               rebirth running (BUSY, an open journal) / an unreadable file - each refused with the file byte-identical; a buy = pts - cost,
               spent + cost, node + 1 in ONE file; a keystone sets its title; REFUND (one arm / all): exactly spent back, nodes cleared, the
               keystone title back to Void-Touched <n>; admin test POINTS; a FUZZ of 3000 random buys / refunds / points: points NEVER
               negative, pts + spent = granted, spent = sum cost(k < levels) per arm; ECHO raises the points of the next rebirth (journaled
               once); rebirth:fn:stat / title / cos / node / dustmult; skill:bonus:<uuid> source "rebirth" read by the REAL SkyySkills
               SkillBonus (xpBonus / dd), removed when the player leaves; rebirth:title:<uuid>; the PAGE in every state (node click, Back,
               Buy inline + queued on the real SkyyRebirth-IO with the page refreshed from RbJob.run, the disc colours, the bindings); the
               page packet (both views) under CustomPage.MAX_SIZE; THE FIT of the real node-view texts; /rebirthadmin points / refund
               MARKETS (real SkyyAuctions 0.1.5 + SkyyBazaar 0.1.11): requirement line 6 = ok / closable (Continue offered) / unclaimed sale
               coins (blocked, no Continue) / a listing that can't be pulled / a jar missing / a bad answer; the hover lines; CONTINUE end to
               end (the listings CANCELLED + item owed, then the full rebirth); Continue refused on unclaimed coins (nothing closed, nothing
               reset) and on a read-only listing (the others closed, nothing reset); THE STEP-0 ORDER (a wouldclose spy: rebirth:busy:<uuid>
               is TRUE on the bridge and the REAL AuctionHouse AhUtil.rebirthBusy sees it during the re-check; a new listing there = refused,
               busy FALSE again at once, no journal); Continue with an open rebirth refused; RbRun mode 5 inline + on SkyyRebirth-IO; dryrun
               prints both wouldclose answers
  KK  kill     the 0.2 real-kill proof (40 rebirths, killed at random, recovered: all-old or all-new) + a TREE KILL: a child JVM buys /
               refunds non-stop on 20 profiles and is killed at a random moment (4 rounds); after a restart every file parses, points >= 0,
               pts + spent = granted, spent = the cost sum of the levels held
  D   live     START TWICE on scratch COPIES of the live Skyy_SkyySkills / Coins / Bank / Rebirth / Auctions: no copied file changes (the
               0.2 config.properties without the tree lines reads the defaults); every live key's market answer from a REAL SkyyAuctions
               on the copy (read-only: nothing written)
  AA  engine-access audit
FIX ROUND (critics): rebirth:busy only through RbPub.busyPut (synchronized; a publish hammer thread never leaves a stale value - 3000
rounds); Buy sends the shown key + level (a late duplicate refused, a profile switched under the page refused, nothing charged); the
requirement / market scan cached in the node view (a wouldclose counter); THE NEXUS CLICK (= Rebirth / Continue, from the node view too,
nothing when neither is offered); the 7 node strengths live (fx / bonus / echo / stat follow Server Setup); /rebirthadmin points <arm|all>
reset (levels, spent and points gone, the keystone title reverts); the live footer (tree.rowNeed); the publish tick every 1 s.
Exit code 1 on any failure.
"""
import os, sys, json, shutil, subprocess, hashlib, math, random, time, importlib.util, copy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.3"
RB = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.2.jar")
AH_JAR = os.path.join(ROOT, "SkyyAuctions", "SkyyAuctions-0.1.5.jar")
BZ_JAR = os.path.join(ROOT, "SkyyBazaar", "SkyyBazaar-0.1.11.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rebirth4", "rb")))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T2 = _load("t_rb02", os.path.join(HERE, "test_skyyrebirth_0.2.py"))   # World / seed / Checker (definitions only)
T2.JAR = JAR                                                             # its World loads OUR jar
T2.SCRATCH = SCRATCH
TA = _load("t_ah015", os.path.join(ROOT, "SkyyAuctions", "test_skyyauctions_0.1.5.py"))   # mk + Ah (definitions only)
props, sha, tree, seed, pts_py = T2.props, T2.sha, T2.tree, T2.seed, T2.pts
U0 = T2.U0
MODS_LIVE = T2.MODS_LIVE
LIVE_DIR = T2.LIVE_DIR

EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],      # the kit: 4 rows, a category, the version text
    "RbAdmin": ["~m help", "~m run"],                                                               # points / refund
    "RbAdminArgsCmd": ["~c "], "RbAdminCmd": ["~c "],                                               # the usage texts
    "RbCfg": ["+f COST_GROWTH", "+f ROW_NEED", "+f STAT_CAP", "+f STAT_PER", "+f W_DD", "+f W_ECHO", "+f W_KEY", "+f W_KSTAT", "+f W_SPEED",
              "+f W_STAT", "+f W_XP", "~<clinit>", "~m loadCfg", "~m writeDefaults"],
    "RbCheck": ["+m ask", "+m closeAll", "+m closeWhy", "+m closed", "+m detail", "+m head", "+m line1", "+m market", "+m marketClear",
                "~m gains", "~m reqs", "~m tip"],                                                   # R4 markets; gains = Echo
    "RbFn": ["~m apply"],                                                                           # modes 6-8 stat / title / cos
    "RbPage": ["+<clinit>", "+f COL_MAX", "+f COL_PART", "+f allowed", "+f armedKind", "+f buyKey", "+f buyLevel", "+f buySel", "+f cGain",
               "+f cReq", "+f canBuy", "+f foot", "+f goKind", "+f gone", "+f lastRef", "+f reqAt", "+f reqK", "+f reqN",
               "+f lastStore", "+f nc", "+f nt", "+f ntc", "+f nvCost", "+f nvHave", "+f nvHaveCol", "+f nvLevel", "+f nvLive", "+f nvName",
               "+f nvNext", "+f nvNow", "+f nvRow", "+f nvRowCol", "+f nvStCol", "+f nvStatus", "+f nvSub", "+f nvSubCol", "+f pending",
               "+f pt", "+f sel", "+f status", "+f view", "+m act", "+m buy", "+m click", "+m colorOf", "+m fillNode", "+m fillTree",
               "+m jobDone", "+m onDismiss", "+m refresh", "+m textOf", "-f goOn", "-m click", "~c ", "~c ", "~m build", "~m fill",
               "~m handleDataEvent"],                                                               # the tree page (click now takes cont)
    "RbPub": ["+m busyPut", "~m clearAll", "~m publish", "~m tick"],                                # title + skill:bonus source; busy monitor
    "RbRun": ["~m run"],                                                                            # mode 5 = Continue
    "RbStore": ["~m writeNow"],                                                                     # the file comment's version
    "RbTx": ["+m continueNow", "+m playerStart", "-m playerStart", "~m applyOwn", "~m begin", "~m begin0", "~m decide", "~m dryRun",
             "~m finish", "~m status"],                                                             # step 0 order, Echo, Continue; status: title (fix 2)
    "SkyyRebirthPlugin": ["~m setup", "~m shutdown"],
}
ADDED = ["RbTree", "RbJob", "RbRefresh"]
ARMS = ["Class", "Foraging", "Mining", "Smithing", "Alchemy", "Farming", "Fishing", "Cooking"]
ROWS = [0, 0, 0, 1, 1, 1, 2, 2, 3, 3, 4]


def cost_py(k, g=1.08):
    x = g ** k
    if not x < 1.0e9:
        return 1000000000
    return max(1, int(math.ceil(x - 1e-9)))


def rb_file(base, k):
    return os.path.join(base, "Skyy_SkyyRebirth", "players", k + ".properties")


def write_rb(base, k, d):
    os.makedirs(os.path.dirname(rb_file(base, k)), exist_ok=True)
    open(rb_file(base, k), "w", encoding="latin-1").write("".join("%s=%s\n" % (a, b) for a, b in d.items()))


def tree_ok(p, granted, g=1.08):
    """(ok, why): pts >= 0, pts + spent = granted, spent = the cost sum of the levels held - per arm"""
    for i, arm in enumerate(ARMS):
        pts = int(p.get("pts." + arm, "0"))
        sp = int(p.get("spent." + arm, "0"))
        lv = sum(int(v) for a, v in p.items() if a.startswith("node." + arm + "."))
        if pts < 0 or sp < 0:
            return False, "%s negative (%d / %d)" % (arm, pts, sp)
        if pts + sp != granted.get(arm, 0):
            return False, "%s pts %d + spent %d != granted %d" % (arm, pts, sp, granted.get(arm, 0))
        if sp != sum(cost_py(x, g) for x in range(lv)):
            return False, "%s spent %d != cost sum of %d levels %d" % (arm, sp, lv, sum(cost_py(x, g) for x in range(lv)))
    return True, ""


# ====================================================================================================== the real Auction House on scratch
def ah_world(home, recs):
    """a REAL SkyyAuctions 0.1.5 (its own loader) on a scratch folder holding recs; returns the TA.Ah (a.Fn(0) closeall, a.Fn(1) wouldclose)"""
    os.makedirs(home, exist_ok=True)
    TA.T4.write_records(home, recs)
    a = TA.Ah(AH_JAR, home)
    a.start()
    return a


def ah_recs(k, now, kinds):
    """records of profile k: 'closable' (ACTIVE BIN), 'sold' (SOLD, sale coins unclaimed), 'ro' (a newer schema = read-only, blocks),
    'item' (EXPIRED, the item waiting = a claim that never blocks)"""
    t = TA.T4.template()
    out, rid = [], 5000
    for kind in kinds:
        rid += 1
        if kind == "closable":
            out.append(TA.mk(t, rid, k, now=now, qty=2, name="Copper Sword %d" % rid))
        elif kind == "sold":
            out.append(TA.mk(t, rid, k, "SOLD", now=now, claims={"sellerCoins": "OWED"}, name="Sold Thing %d" % rid,
                             buyer={"uuid": TA.uu(3), "key": TA.uu(3), "name": "B3", "profile": "P", "at": TA.L(now)}))
        elif kind == "ro":
            out.append(TA.mk(t, rid, k, now=now, v=2, name="Future Thing %d" % rid))
        elif kind == "item":
            out.append(TA.mk(t, rid, k, "EXPIRED", now=now, qty=4, claims={"sellerItem": "OWED"}, name="Old Thing %d" % rid))
        out.append(TA.mk(t, rid + 500, TA.uu(4), now=now, name="Someone Else %d" % rid))   # another seller's listing (never touched)
    return out


def bazaar_fns():
    from jpype import JClass, JArray
    Lb = JClass("java.net.URLClassLoader")(JArray(JClass("java.net.URL"))([JClass("java.io.File")(BZ_JAR).toURI().toURL()]),
                                           JClass("java.lang.ClassLoader").getSystemClassLoader())
    F = JClass("com.skyy.bazaar.BzRebirthFn", loader=Lb)
    return F(0), F(1)


# ====================================================================================================== X
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    Obj, Str, Integer, Long, Bool = (JClass("java.lang.Object"), JClass("java.lang.String"), JClass("java.lang.Integer"), JClass("java.lang.Long"),
                                     JClass("java.lang.Boolean"))
    OA = lambda *xs: JArray(Obj)(list(xs))
    k = U0
    W0 = T2.World(os.path.join(scratch, "w0"))
    CK = T2.Checker(K, W0)
    T = JClass(RB + "RbTree", loader=W0.L)
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    now = int(JClass("java.lang.System").currentTimeMillis())

    @JImplements("java.util.function.Function")
    class Spy(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)

    def fresh(name, markets=True, **kw):
        base = os.path.join(scratch, name)
        seed(base, k, CK.cls_total, **kw)
        W = T2.World(base)
        W.br.put("class:" + k, "Archer")
        for i_, nm_ in ((6, "stat"), (7, "title"), (8, "cos")):
            W.br.put("rebirth:fn:" + nm_, W.Fnc(i_))     # 0.3's new functions (the 0.2 World registers 0-5)
        if markets:
            bz0, bz1 = bazaar_fns()
            W.br.put("bazaar:fn:closeall", bz0)
            W.br.put("bazaar:fn:wouldclose", bz1)
            a = ah_world(os.path.join(base, "Skyy_SkyyAuctions"), ah_recs(k, now, []))
            W.br.put("ah:fn:closeall", a.Fn(0))
            W.br.put("ah:fn:wouldclose", a.Fn(1))
        f = W.files(k)
        return W, base, dict((m_, sha(f[m_])) for m_ in ("skills", "coins", "bank"))

    def tree_of(W):
        return JClass(RB + "RbTree", loader=W.L)

    # ---------------------------------------------------------------- the catalogue + the pure rules
    ids = [str(x) for x in T.NID]
    K.check(len(ids) == 88 and len(set(ids)) == 88 and [int(x) for x in T.NROW] == ROWS * 8 and [int(x) for x in T.NARM] == [i // 11 for i in range(88)],
            "X catalogue: 88 unique ids, rows 3/3/2/2/1 per arm in canvas order")
    K.check(all(ids[11 * a].split(".")[0] == ARMS[a] for a in range(8)) and all(ids[11 * a + 10].endswith(".key") and int(T.NMAX[11 * a + 10]) == 1 for a in range(8))
            and all(ids[11 * a + 1] == ARMS[a] + ".dust" and int(T.NMAX[11 * a + 1]) == 4 for a in range(1, 8)),
            "X catalogue: arms in page order, keystones 1 level, Void Dust = <Arm>.dust with 4 levels (spec U4; rebirth:fn:dustmult reads it)")
    K.check([str(x) for x in T.NTITLE if str(x)] == ["Void Ascendant"] + ["%s Ascendant" % a for a in ARMS[1:]], "X catalogue: the 8 keystone titles")
    K.check([int(T.cost(x)) for x in range(70)] == [cost_py(x) for x in range(70)], "X cost: ceil(1.08^k) for k 0-69 (Rebirth-Research 2.4)")
    K.check([int(T.armMax(a_)) for a_ in range(8)] == [51] + [50] * 7, "X a Class arm holds 51 levels, a skill arm 50 (Void Dust 4)")
    K.notes.append("a whole skill arm (50 levels) costs %d points, the Class arm (51) %d at tree.costGrowth 1.08" % (sum(cost_py(x) for x in range(50)), sum(cost_py(x) for x in range(51))))
    W0.Cfg.COST_GROWTH = 2.0
    K.check([int(T.cost(x)) for x in (0, 1, 10, 29, 30, 60)] == [1, 2, 1024, 536870912, 1000000000, 1000000000], "X cost: growth 2 + the 1,000,000,000 cap")
    W0.Cfg.COST_GROWTH = 1.08
    JP = JClass("java.util.Properties")

    def P(d):
        p = JP()
        for a_, b_ in d.items():
            p.setProperty(a_, str(b_))
        return p
    p0 = P({})
    K.check(int(T.openRows(p0, 2)) == 1 and int(T.need(2, 0)) == 8 and int(T.need(2, 2)) == 8, "X rows: only row 1 open at 0 levels; need 8")
    p1 = P({"node.Mining.xp": 5, "node.Mining.dust": 3})
    p2 = P({"node.Mining.xp": 5, "node.Mining.dust": 2, "node.Mining.echo": 1, "node.Mining.dd": 5, "node.Mining.tool": 3,
            "node.Mining.dd2": 5, "node.Mining.echo2": 3, "node.Mining.xp3": 9})
    K.check(int(T.openRows(p1, 2)) == 2 and int(T.rowLevels(p1, 2, 0)) == 8 and int(T.openRows(p2, 2)) == 4 and int(T.lv(p2, 2 * 11 + 9)) == 5,
            "X rows: 8 levels open the next row; rows chain (p2: rows 1-4 open); a hand-edited level over the max reads as the max")
    W0.Cfg.ROW_NEED = 10
    K.check(int(T.need(2, 0)) == 10 and int(T.need(2, 2)) == 10 and int(T.openRows(p1, 2)) == 1, "X rows: tree.rowNeed 10 (row 3 holds 10)")
    W0.Cfg.ROW_NEED = 8
    K.check(str(T.fx(2 * 11, 3)) == "+6 % Mining XP" and str(T.fx(2 * 11 + 1, 2)) == "+50 % Mining Dust" and str(T.fx(2 * 11 + 4, 2)) == "+2 rebirth modifier levels on your pickaxe and Multitool"
            and str(T.fx(2 * 11, 0)) == "nothing yet" and str(T.fx(2 * 11 + 10, 1)) == "+10 % Mining XP and the title" and str(T.fx(4 * 11 + 4, 5)) == "Alchemy works 15 % faster",
            "X fx: Wisdom / Dust (dust.perNode) / tool / keystone / speed texts")
    K.check([int(T.state(p2, 2 * 11 + s_)) for s_ in (0, 2, 3, 6, 8, 10)] == [4, 3, 4, 4, 2, 1] and int(T.state(p1, 2 * 11 + 8)) == 0 and int(T.state(p1, 2 * 11 + 6)) == 1,
            "X node states: maxed / part / open 0 / next row / locked")
    K.check(int(T.echoPct(p2, 2)) == 16 and int(T.echoed(10, 16.0)) == 11 and int(T.echoed(0, 50.0)) == 0 and int(T.echoed(7, 0.0)) == 7, "X echo: 4 % a level, floor")
    # FIX ROUND: every node strength is a live Server Setup row
    W0.Cfg.W_XP, W0.Cfg.W_DD, W0.Cfg.W_ECHO, W0.Cfg.W_KEY, W0.Cfg.W_STAT, W0.Cfg.W_KSTAT, W0.Cfg.W_SPEED = 3.5, 1.0, 2.5, 12.0, 0.5, 4.0, 1.25
    _psx = P({"node.Class.hp": 3, "node.Class.hp2": 2, "node.Class.key": 1})
    _bm = dict((str(a_), round(float(b_), 6)) for a_, b_ in T.bonusMap(p2).items())
    K.check(str(T.fx(2 * 11, 2)) == "+7 % Mining XP" and str(T.fx(2 * 11 + 10, 1)) == "+12 % Mining XP and the title" and str(T.fx(4 * 11 + 4, 2)) == "Alchemy works 2.5 % faster"
            and str(T.fx(10, 1)) == "+4 % all stats and the title" and str(T.fx(2 * 11 + 4, 2)) == "+2 rebirth modifier levels on your pickaxe and Multitool"
            and float(T.echoPct(p2, 2)) == 10.0 and int(T.echoed(10, float(T.echoPct(p2, 2)))) == 11 and _bm == {"xp.mining": 0.35, "dd.mining": 0.10}
            and float(T.stat(_psx, 3, "health")) == 2.5 and float(T.stat(_psx, 3, "all")) == 13.0,
            "STRENGTHS live: Wisdom 3.5 / Fortune 1 / Echo 2.5 / keystone 12 / stat 0.5 / keystone stat 4 / speed 1.25 change the texts, the bonus, Echo and stats (tools fixed): %s" % _bm)
    W0.Cfg.W_XP, W0.Cfg.W_DD, W0.Cfg.W_ECHO, W0.Cfg.W_KEY, W0.Cfg.W_STAT, W0.Cfg.W_KSTAT, W0.Cfg.W_SPEED = 2.0, 2.0, 4.0, 10.0, 1.0, 2.0, 3.0
    bm = T.bonusMap(p2)
    K.check(dict((str(a_), round(float(b_), 6)) for a_, b_ in bm.items()) == {"xp.mining": 0.20, "dd.mining": 0.20}, "X bonusMap: xp + xp3 = 20 %%, dd + dd2 = 20 %%: %s" % bm)
    K.check(int(T.big(P({"x": -5}), "x")) == 0 and int(T.big(P({"x": "9999999999999"}), "x")) == 1000000000 and int(T.big(P({"x": "zz"}), "x")) == 0,
            "X big: negative -> 0, huge -> 1e9, junk -> 0")
    K.check([int(T.armIndex(x)) for x in ("mining", "CLASS", "all", "nope", None)] == [2, 0, -1, -2, -2] and str(T.shortN(100000)) == "99999+",
            "X armIndex / shortN")
    ps = P({"node.Class.hp": 3, "node.Class.hp2": 2, "node.Class.key": 1, "title": "Void Ascendant", "cos.3": 1, "cos.6": 1})
    K.check(float(T.stat(ps, 3, "all")) == 11.0 and float(T.stat(ps, 3, "health")) == 5.0 and float(T.stat(ps, 50, "ALL")) == 32.0
            and float(T.stat(ps, 3, "mana")) == 0.0 and str(T.title(ps)) == "Void Ascendant" and str(T.cos(ps)) == "3,6",
            "X stat: all = min(30, 3 x n) + keystone 2; health = Class nodes; title; cos")

    # ---------------------------------------------------------------- BUY rules on a real profile file
    W, base, H = fresh("buy")
    u = W.uuid(k)
    Tw = tree_of(W)
    write_rb(base, k, {"n": 1, "pts.Mining": 20, "pts.Class": 2, "title": "Void-Touched I"})
    W.Sto.CACHE.clear()
    f = rb_file(base, k)

    def same(what, fn):
        h0 = sha(f)
        r = str(fn())
        K.check(r.startswith("-") and sha(f) == h0, "BUY refused, file byte-identical: %s (%s)" % (what, r))
        return r
    same("switched off", lambda: Tw.buy(k, u, 22, 0, False))
    same("no node", lambda: Tw.buy(k, u, 88, 0, True))
    r = same("locked row (Mining row 2)", lambda: Tw.buy(k, u, 2 * 11 + 3, 0, True))
    K.check("still locked" in r, "BUY locked row text: %s" % r)
    same("a changed level (expect 1, is 0)", lambda: Tw.buy(k, u, 22, 1, True))
    seq = []
    for i_ in range(5):
        seq.append(str(Tw.buy(k, u, 22, i_, True)))
    p = props(f)
    K.check(all(x.startswith("+") for x in seq) and p["node.Mining.xp"] == "5" and p["pts.Mining"] == str(20 - sum(cost_py(x) for x in range(5)))
            and p["spent.Mining"] == str(sum(cost_py(x) for x in range(5))), "BUY 5 levels: node 5, pts / spent by the cost curve: %s" % seq[-1])
    same("max level", lambda: Tw.buy(k, u, 22, 5, True))
    _c1 = str(Tw.buy(k, u, 0, 0, True))
    K.check(_c1.startswith("+Vitality level 1 bought - 1 Class point spent."), "BUY Class: the first level costs 1: %s" % _c1)
    same("not enough points (Class: 1 left, the 2nd level costs ceil(1.08) = 2)", lambda: Tw.buy(k, u, 1, 0, True))
    K.check(props(f)["pts.Class"] == "1" and props(f)["spent.Class"] == "1", "BUY points never below 0: Class 1 left, 1 spent")
    W.Sto.BUSY.put(k, "tx")
    same("a rebirth running (BUSY)", lambda: Tw.buy(k, u, 23, 0, True))
    W.Sto.BUSY.remove(k)
    os.makedirs(os.path.join(base, "Skyy_SkyyRebirth", "journal"), exist_ok=True)
    jf = os.path.join(base, "Skyy_SkyyRebirth", "journal", k + ".journal")
    open(jf, "w").write("BEGIN x\n")
    same("a rebirth journal open", lambda: Tw.buy(k, u, 23, 0, True))
    os.remove(jf)
    for _x in range(3):
        Tw.buy(k, u, 23, _x, True)    # Void Dust 3 -> row 1 holds 8 -> row 2 opens
    r = str(Tw.buy(k, u, 2 * 11 + 3, 0, True))
    K.check(r.startswith("+Mining Fortune level 1 bought"), "BUY row 2 opens at 8 levels in row 1: %s" % r)
    K.check(float(W.br.get("rebirth:fn:dustmult").apply(OA(k, "Mining"))) == 2.0 * 1.75 and int(W.br.get("rebirth:fn:node").apply(OA(k, "Mining.xp"))) == 5,
            "BUY rebirth:fn:dustmult = 2 x (1 + 0.25 x 3) after Void Dust 3; rebirth:fn:node Mining.xp 5")
    # unreadable file
    W.Sto.CACHE.clear()
    fb = os.path.join(scratch, "buy_badfile")
    shutil.copytree(base, fb)
    bad = rb_file(fb, k)
    os.remove(bad)
    os.makedirs(bad)
    Wb = T2.World(fb)
    r = str(tree_of(Wb).buy(k, u, 22, 5, True))
    K.check(r.startswith("-Your rebirth file cannot be read"), "BUY unreadable file refused: %s" % r)
    # keystone title + refund
    W.Cfg.COST_GROWTH = 1.0
    r = str(Tw.addPts(k, u, 2, 500))
    K.check(r.startswith("+Added 500 test points to the Mining arm"), "POINTS admin: %s" % r)
    for idx in range(22, 33):
        lv_ = props(f)
        l = int(lv_.get("node." + ids[idx], "0"))
        while l < int(T.NMAX[idx]):
            rr = str(Tw.buy(k, u, idx, l, True))
            if not rr.startswith("+"):
                break
            l += 1
    p = props(f)
    K.check(p.get("node.Mining.key") == "1" and p.get("title") == "Mining Ascendant", "BUY the keystone: title Mining Ascendant: %s" % p.get("title"))
    W.Cfg.COST_GROWTH = 1.08
    spent_m, pts_m = int(p["spent.Mining"]), int(p["pts.Mining"])
    r = str(Tw.refund(k, u, 2))
    p = props(f)
    K.check(r.startswith("+Refunded the Mining arm: 50 levels reset") and int(p["pts.Mining"]) == pts_m + spent_m and "spent.Mining" not in p
            and not any(a_.startswith("node.Mining.") for a_ in p) and p.get("title") == "Void-Touched I" and p.get("spent.Class") == "1",
            "REFUND one arm: exactly spent back, nodes gone, the keystone title back to Void-Touched I, Class untouched: %s / before %s" % (r, sorted(lv_.items())))
    r = str(Tw.refund(k, u, -1))
    p = props(f)
    K.check(r.startswith("+Refunded every arm") and p.get("pts.Class") == "2" and not any(a_.startswith("spent.") or a_.startswith("node.") for a_ in p),
            "REFUND all: every arm back")
    K.check(str(Tw.refund(k, u, 9)).startswith("-Usage") and str(Tw.addPts(k, u, 2, 0)).startswith("-Usage") and str(Tw.addPts(k, u, 2, 100001)).startswith("-Usage"),
            "REFUND / POINTS bad arguments")
    W.Sto.BUSY.put(k, "tx")
    K.check(str(Tw.refund(k, u, 2)).startswith("-A rebirth is running") and str(Tw.addPts(k, u, 2, 5)).startswith("-A rebirth is running")
            and str(Tw.wipe(k, u, 2)).startswith("-A rebirth is running"), "REFUND / POINTS / RESET refused while busy")
    W.Sto.BUSY.remove(k)
    # FIX ROUND: points <arm|all> reset = the arm's levels, spent AND points gone (test points too); the keystone title reverts
    write_rb(base, k, {"n": 1, "pts.Mining": 500, "spent.Mining": 9, "node.Mining.xp": 3, "node.Mining.key": 1, "title": "Mining Ascendant",
                       "pts.Class": 4, "spent.Class": 1, "node.Class.hp": 1})
    r = str(Tw.wipe(k, u, 2))
    p = props(f)
    K.check(r.startswith("+Reset the Mining arm: 4 levels and 509 points") and not any(a_.endswith(".Mining") or a_.startswith("node.Mining.") for a_ in p)
            and p.get("title") == "Void-Touched I" and p.get("pts.Class") == "4" and p.get("node.Class.hp") == "1", "RESET one arm: Mining wiped, title reverts, Class untouched: %s" % r)
    r = str(Tw.wipe(k, u, -1))
    p = props(f)
    K.check(r.startswith("+Reset every arm") and not any(a_.startswith("pts.") or a_.startswith("spent.") or a_.startswith("node.") for a_ in p) and p.get("n") == "1",
            "RESET all: no points, spent or levels left (n kept)")
    K.check(str(Tw.wipe(k, u, 9)).startswith("-Usage"), "RESET bad arm")

    # ---------------------------------------------------------------- FUZZ: points never negative, totals exact
    W, base, H = fresh("fuzz", markets=False)
    u = W.uuid(k)
    Tw = tree_of(W)
    f = rb_file(base, k)
    write_rb(base, k, {"n": 0})
    W.Sto.CACHE.clear()
    rnd = random.Random(7)
    granted = dict((a_, 0) for a_ in ARMS)
    bad = []
    ok_buys = 0
    for step in range(3000):
        x = rnd.random()
        if x < 0.06:
            a_ = rnd.randrange(-1, 8)
            n_ = rnd.randint(1, 40)
            if str(Tw.addPts(k, u, a_, n_)).startswith("+"):
                for i_, arm in enumerate(ARMS):
                    if a_ < 0 or a_ == i_:
                        granted[arm] += n_
        elif x < 0.08:
            Tw.refund(k, u, rnd.randrange(-1, 8))
        else:
            idx = rnd.randrange(88)
            pp = props(f) or {}
            l = min(int(pp.get("node." + ids[idx], "0")), int(T.NMAX[idx]))
            if rnd.random() < 0.1:
                l += 1        # a stale page
            r = str(Tw.buy(k, u, idx, l, True))
            ok_buys += 1 if r.startswith("+") else 0
        if step % 50 == 0:
            good, why = tree_ok(props(f) or {}, granted)
            if not good:
                bad.append((step, why))
    good, why = tree_ok(props(f), granted)
    K.check(good and not bad and ok_buys > 300, "FUZZ 3000 random buys / refunds / points: %d buys, pts never < 0, pts + spent = granted, spent = cost sum: %s %s" % (ok_buys, why, bad[:2]))

    # ---------------------------------------------------------------- ECHO in the decision + skill:bonus + title + stat via the bridge
    W, base, H = fresh("echo")
    u = W.uuid(k)
    write_rb(base, k, {"n": 0, "node.Mining.echo": 5, "node.Mining.echo2": 5, "node.Mining.xp": 2, "node.Mining.dd": 1, "node.Mining.key": 1,
                       "node.Mining.dust": 0, "title": "Mining Ascendant"})
    W.Sto.CACHE.clear()
    dr = [str(x) for x in W.Tx.dryRun(u)]
    base_m = CK.points["Mining"]
    want_m = int(base_m * 140 // 100)
    K.check(("pts.Mining=%d;" % want_m) in dr[-1] and any(x.startswith("=market (a player rebirth needs ok:0:0 from both): bazaar:fn:wouldclose ok:0:0:0:0, ah:fn:wouldclose ok:0:0:0:0") for x in dr),
            "ECHO dryrun: Mining %d -> %d points (+40 %%); the market line: %s" % (base_m, want_m, dr[-1][:90]))
    W.Tx.adminStart(u, -1)
    p = props(rb_file(base, k))
    jd = os.path.join(base, "Skyy_SkyyRebirth", "journal", "done")
    dj = open(os.path.join(jd, os.listdir(jd)[0]), encoding="utf8").read()
    K.check(p.get("pts.Mining") == str(want_m) and p.get("pts.Class") == str(CK.points["Class"]) and ("pts.Mining=%d;" % want_m) in dj and p.get("title") == "Void-Touched I",
            "ECHO the rebirth journals + pays the echoed points once (Mining %s), the new title Void-Touched I" % p.get("pts.Mining"))
    W.Sto.CACHE.clear()
    W.Pub.publish(u)
    SB = JClass("com.skyy.skills.SkillBonus", loader=W.L)
    SD = W.SDefs
    sbm = W.br.get("skill:bonus:" + k)
    K.check(sbm is not None and dict((str(a_), round(float(b_), 6)) for a_, b_ in sbm.get("rebirth").items()) == {"xp.mining": 0.14, "dd.mining": 0.02},
            "BONUS skill:bonus:<uuid>[rebirth] = Wisdom 2 x 2 %% + keystone 10 %%, Fortune 2 %%: %s" % (sbm and sbm.get("rebirth")))
    K.check(round(float(SB.xpBonus(u, int(SD.MINING))), 6) == 0.14 and round(float(SB.dd(u, 0)), 6) == 0.02 and float(SB.xpBonus(u, int(SD.FORAGING))) == 0.0,
            "BONUS the REAL SkyySkills 0.4.36 SkillBonus reads it: Mining XP +14 %%, Mining double drops +2 %%, Foraging 0")
    K.check(str(W.br.get("rebirth:title:" + k)) == "Void-Touched I" and str(W.br.get("rebirth:fn:title").apply(k)) == "Void-Touched I"
            and float(W.br.get("rebirth:fn:stat").apply(OA(k, "all"))) == 3.0 and str(W.br.get("rebirth:fn:cos").apply(k)) == "",
            "TITLE / STAT / COS on the bridge after rebirth 1 (all stats +3 %%)")
    W.Cfg.TEST_ONLINE = JClass("java.util.ArrayList")()
    W.Pub.PUB.put(u, Bool.TRUE)
    W.Pub.tick()
    K.check(sbm.get("rebirth") is None and W.br.get("rebirth:title:" + k) is None, "BONUS a leaver: the rebirth source + title removed (tick)")
    W.Cfg.TEST_ONLINE = None
    W.Pub.publish(u)
    W.Pub.clearAll()
    K.check(sbm.get("rebirth") is None and W.br.get("rebirth:title:" + k) is None, "BONUS shutdown (clearAll): removed")
    W.Pub.publish(u)
    k2 = k + "-p2"
    W.keymap[k] = k2
    W.Sto.LOADING.put(k2, Bool.TRUE)     # the new profile's file not read yet (IO queue)
    W.Sto.IO = JClass("java.util.concurrent.Executors").newSingleThreadExecutor()
    W.Sto.IO.shutdown()                  # a stopped executor: get() cannot read it -> not ready
    W.Pub.publish(u)
    K.check(sbm.get("rebirth") is None and W.br.get("rebirth:title:" + k) is None, "BONUS a profile switch while the new file is read: the old profile's bonus + title removed")
    W.Sto.IO = None
    W.Sto.LOADING.clear()
    W.keymap.clear()

    # ---------------------------------------------------------------- FIX ROUND 2: status shows the title + uncapped points; an unreadable file at decide = abort
    W2, base2, H2 = fresh("status2")
    u2 = W2.uuid(k)
    write_rb(base2, k, {"n": 1, "pts.Mining": 5000, "spent.Mining": 0, "title": "Mining Ascendant"})
    W2.Sto.CACHE.clear()
    st2 = [str(x) for x in W2.Tx.status(u2)]
    K.check("Mining 5000" in st2[0] and "=Title: Mining Ascendant" in st2, "STATUS /rebirthadmin status: points past 1000 (%s) + the title line" % st2[0][:80])
    os.remove(rb_file(base2, k))
    os.makedirs(rb_file(base2, k))      # a directory where the file should be: readNow fails (null)
    try:
        dr2 = [str(x) for x in W2.Tx.dryRun(u2)]
    finally:
        os.rmdir(rb_file(base2, k))
    K.check(dr2[-1].startswith("-Would abort as a player rebirth: the rebirth file of this profile cannot be read"),
            "DECIDE an unreadable rebirth file aborts (never commits a reward without Echo): %s" % dr2[-1][:90])
    W2.Sto.CACHE.clear()

    # ---------------------------------------------------------------- MARKETS: requirement line 6 with the REAL SkyyAuctions 0.1.5 + SkyyBazaar 0.1.11
    W.Cfg.HUB_TEST = "hub"
    W.Cfg.ON = True

    def mkt(name, kinds, ah=True, bz=True):
        Wm, bm_, Hm = fresh(name, markets=False)
        bz0, bz1 = bazaar_fns()
        if bz:
            Wm.br.put("bazaar:fn:closeall", bz0)
            Wm.br.put("bazaar:fn:wouldclose", bz1)
        a = ah_world(os.path.join(bm_, "Skyy_SkyyAuctions"), ah_recs(k, now, kinds))
        if ah:
            Wm.br.put("ah:fn:closeall", a.Fn(0))
            Wm.br.put("ah:fn:wouldclose", a.Fn(1))
        Wm.Cfg.HUB_TEST = "hub"
        Wm.Cfg.ON = True
        return Wm, bm_, Hm, a
    cases = [("m_ok", [], True, True, "OK  No Bazaar / AH orders", False),
             ("m_close", ["closable", "closable"], True, True, "NO  2 to close - Continue", True),
             ("m_coins", ["closable", "sold"], True, True, "NO  Claim AH sale coins first", False),
             ("m_ro", ["closable", "ro"], True, True, "NO  1 can't be closed yet", False),
             ("m_item", ["item"], True, True, "OK  No Bazaar / AH orders", False),
             ("m_noah", [], False, True, "NO  Needs SkyyAuctions 0.1.5", False),
             ("m_nobz", [], True, False, "NO  Needs SkyyBazaar 0.1.11+", False)]
    rows = {}
    for name, kinds, ah, bz, want, cont in cases:
        Wm, bm_, Hm, a = mkt(name, kinds, ah, bz)
        um = Wm.uuid(k)
        rq = Wm.Chk.reqs(um, "hub", 0)
        rows[name] = (str(rq[0][5]), bool(rq[3]), bool(rq[2]), [str(x) for x in rq[4]])
        K.check(str(rq[0][5]) == want and bool(rq[3]) == cont and bool(rq[2]) == (want.startswith("OK")),
                "MARKET %s: line 6 %r, Continue %s, all met %s" % (name, str(rq[0][5]), bool(rq[3]), bool(rq[2])))
    K.check(any("will be cancelled, the item waits in /ah > Manage" in x for x in rows["m_close"][3])
            and any("SOLD - claim your 500 coins in /ah > Manage first" in x for x in rows["m_coins"][3])
            and any("can't be pulled yet" in x for x in rows["m_ro"][3])
            and any("kept through a rebirth" in x for x in rows["m_item"][3]), "MARKET the hover lines use the contract's page wording")
    Wm, bm_, Hm, a = mkt("m_bad", [])
    Wm.br.put("ah:fn:wouldclose", Spy(lambda o: "err:exception"))
    rq = Wm.Chk.reqs(Wm.uuid(k), "hub", 0)
    tip = str(Wm.Chk.tip(0, rq, Wm.Chk.gains(Wm.uuid(k), 0)))
    K.check(str(rq[0][5]) == "NO  Bazaar / AH not answering" and "err:exception" in tip, "MARKET a bad answer: not answering (the raw answer in the hover)")
    Wm, bm_, Hm, a = mkt("m_tip", ["closable"])
    rq = Wm.Chk.reqs(Wm.uuid(k), "hub", 0)
    tip = str(Wm.Chk.tip(0, rq, Wm.Chk.gains(Wm.uuid(k), 0)))
    K.check("BAZAAR / AH" in tip and "click the Nexus (or Continue on the left) twice" in tip and "THE TREE" in tip, "MARKET the Nexus hover: the orders + 'click the Nexus (or Continue)'")

    # ---- CONTINUE end to end (inline, IO not running): the 2 listings CANCELLED + owed, then the full rebirth
    Wm, bm_, Hm, a = mkt("cont_full", ["closable", "closable"])
    um = Wm.uuid(k)
    pg = Wm.Page(um, "hub")
    pg.build(None, UCB(), UEB(), None)
    K.check(int(pg.goKind) == 2, "CONTINUE the page offers Continue (goKind 2)")
    pg.handleDataEvent(None, None, '{"a":"rbcont"}')
    K.check(str(pg.last) == "=armed" and "Closes orders (fees kept)" in (pg.build(None, UCB(), UEB(), None) or str(pg.note)), "CONTINUE first press arms + the warning note: %s" % pg.note)
    pg.armedAt = int(JClass("java.lang.System").currentTimeMillis()) - 2000
    pg.handleDataEvent(None, None, '{"a":"rbgo"}')
    K.check(str(pg.last) == "=armed", "CONTINUE armed, then Rebirth pressed = a different button: armed again, nothing started")
    pg.armedAt = int(JClass("java.lang.System").currentTimeMillis()) - 2000
    pg.armedKind = 2
    pg.handleDataEvent(None, None, '{"a":"rbcont"}')
    K.check(str(pg.last).startswith("+Closing your Bazaar / AH orders"), "CONTINUE second press: started (%s)" % pg.last)
    CK.new(Wm, k, "CONTINUE full rebirth")
    ls = TA.disk(os.path.join(bm_, "Skyy_SkyyAuctions"))
    mine = [d for d in ls.values() if d["seller"]["key"] == k]
    K.check(len(mine) == 2 and all(d["state"] == "CANCELLED" and d["claims"]["sellerItem"] == "OWED" for d in mine)
            and all(d["state"] == "ACTIVE" for d in ls.values() if d["seller"]["key"] != k),
            "CONTINUE the AH listings are CANCELLED with the item owed (in /ah > Manage); someone else's untouched")
    K.check(any("Closed 2 Bazaar / AH order(s)" in str(t) for t in Wm.told), "CONTINUE the player is told how many closed")

    # ---- Continue refused: unclaimed sale coins (nothing closed, nothing reset)
    Wm, bm_, Hm, a = mkt("cont_coins", ["closable", "sold"])
    um = Wm.uuid(k)
    ah0 = tree(os.path.join(bm_, "Skyy_SkyyAuctions", "listings"))
    K.check(str(Wm.Tx.playerStart(um, "hub", True)).startswith("-Continue is not offered now"), "CONTINUE refused at the click when sale coins wait")
    r = str(Wm.Tx.continueNow(k, um))
    K.check(r.startswith("-The Auction House closed 0 and could not close 1") and tree(os.path.join(bm_, "Skyy_SkyyAuctions", "listings")) == ah0,
            "CONTINUE forced with unclaimed coins: the AH closes NOTHING, nothing reset (%s)" % r[:90])
    CK.old(Wm, k, Hm, "CONTINUE with unclaimed coins")
    # claim the coins (the real AH, coins into the real SkyyCoins purse) -> Continue works and the claimed coins count for the bank bonus
    rc = a.S.claimCoins(um, k, "5002")
    K.check(rc is not None, "CONTINUE the sale coins claimed in the real AH: %s" % rc)
    rq = Wm.Chk.reqs(um, "hub", 0)
    K.check(str(rq[0][5]) == "NO  1 to close - Continue" and bool(rq[3]), "CONTINUE after claiming: Continue offered")
    # ---- Continue refused: a listing that can't be pulled (the others are closed, nothing reset)
    Wm, bm_, Hm, a = mkt("cont_ro", ["closable", "ro"])
    um = Wm.uuid(k)
    r = str(Wm.Tx.continueNow(k, um))
    lsd = TA.disk(os.path.join(bm_, "Skyy_SkyyAuctions"))
    K.check(r.startswith("-The Auction House closed 1 and could not close 1") and lsd["5001.json"]["state"] == "CANCELLED" and lsd["5002.json"]["state"] == "ACTIVE",
            "CONTINUE with a read-only listing: the closable one closed, the read-only stays, nothing reset (%s)" % r[:80])
    CK.old(Wm, k, Hm, "CONTINUE with a read-only listing")
    # ---- other closeall answers
    Wm, bm_, Hm, a = mkt("cont_err", ["closable"])
    um = Wm.uuid(k)
    Wm.br.put("bazaar:fn:closeall", Spy(lambda o: "err:write-failed:0:1"))
    ah1 = tree(os.path.join(bm_, "Skyy_SkyyAuctions", "listings"))
    K.check(str(Wm.Tx.continueNow(k, um)).startswith("-The Bazaar could not save everything") and tree(os.path.join(bm_, "Skyy_SkyyAuctions", "listings")) == ah1,
            "CONTINUE closeWhy write-failed; the AH is not touched when the Bazaar did not close")
    Wm.br.put("bazaar:fn:closeall", Spy(lambda o: "err:odd"))
    K.check(str(Wm.Tx.continueNow(k, um)).startswith("-The Bazaar could not close everything (err:odd)"), "CONTINUE closeWhy other")
    Wm.br.remove("bazaar:fn:closeall")
    K.check(str(Wm.Tx.continueNow(k, um)).startswith("-Rebirth needs SkyyBazaar 0.1.11+"), "CONTINUE closeWhy a missing jar")
    Wm.br.put("ah:fn:closeall", Spy(lambda o: (_ for _ in ()).throw(RuntimeError("x"))))
    K.check(str(Wm.Chk.closeAll("ah:fn:closeall", k)) == "err:exception" and int(Wm.Chk.closed("ok:3")) == 3 and int(Wm.Chk.closed("ok:x")) == -1
            and int(Wm.Chk.closed(None)) == -1, "CONTINUE closeAll catches a throw; closed() parses")
    Wm.Sto.BUSY.put(k, "tx")
    K.check(str(Wm.Tx.continueNow(k, um)).startswith("-A rebirth is already running"), "CONTINUE refused while a rebirth is open (no closeall)")
    Wm.Sto.BUSY.remove(k)

    # ---- THE STEP-0 ORDER: a spy on ah:fn:wouldclose sees rebirth:busy:<uuid> TRUE (and the real AH's rebirthBusy) during the re-check
    Wm, bm_, Hm, a = mkt("order", [])
    um = Wm.uuid(k)
    seen = []
    real = a.Fn(1)

    def spy_new_listing(o):
        seen.append((bool(Wm.br.get("rebirth:busy:" + k) == Bool.TRUE), bool(a.U.rebirthBusy(um)), bool(Wm.Sto.BUSY.containsKey(k))))
        return "ok:1:0:0:0\n9999\t1\t1\t5\t0\tNew Listing" if len(seen) > 1 else str(real.apply(o))
    Wm.br.put("ah:fn:wouldclose", Spy(spy_new_listing))
    r = str(Wm.Tx.playerStart(um, "hub", False))     # page check passes (call 1), the step-0 re-check sees a new listing (call 2)
    K.check(r.startswith("-You have open Bazaar / AH orders") and len(seen) == 2 and seen[0] == (False, False, False) and seen[1] == (True, True, True),
            "STEP 0: the re-check runs AFTER busy is claimed and published (bridge TRUE, the REAL AuctionHouse sees it): %s / %s" % (r[:60], seen))
    K.check(not Wm.Sto.BUSY.containsKey(k) and Wm.br.get("rebirth:busy:" + k) == Bool.FALSE and not os.path.exists(os.path.join(bm_, "Skyy_SkyyRebirth", "journal", k + ".journal")),
            "STEP 0 (d): refused before BEGIN - busy cleared, rebirth:busy FALSE at once, no journal")
    # FIX ROUND: rebirth:busy:<uuid> only through the synchronized RbPub.busyPut - a tick (publish) hammering from another thread never
    # leaves a stale value after begin's claim / a release (critic: tick read BUSY false, begin put TRUE, tick put FALSE)
    import threading
    MOD = JClass("java.lang.reflect.Modifier")
    _bp = Wm.Pub.class_.getDeclaredMethod("busyPut", JClass("java.util.UUID").class_, Str.class_)
    stop_ = [False]
    hits_ = [0]

    def hammer_():
        while not stop_[0]:
            Wm.Pub.publish(um)
            hits_[0] += 1
    th_ = threading.Thread(target=hammer_)
    th_.start()
    stale_ = 0
    try:
        for _i in range(3000):
            Wm.Sto.BUSY.put(k, "starting")
            Wm.Pub.busyPut(um, k)
            if Wm.br.get("rebirth:busy:" + k) != Bool.TRUE:
                stale_ += 1
            Wm.Sto.BUSY.remove(k)
            Wm.Pub.busyPut(um, k)
            if Wm.br.get("rebirth:busy:" + k) != Bool.FALSE:
                stale_ += 1
    finally:
        stop_[0] = True
        th_.join()
    K.check(MOD.isSynchronized(_bp.getModifiers()) and MOD.isStatic(_bp.getModifiers()) and stale_ == 0 and hits_[0] > 0,
            "BUSY MONITOR: busyPut is static synchronized; 3000 claim / release rounds against a publish hammer (%d publishes): %d stale values" % (hits_[0], stale_))
    CK.old(Wm, k, Hm, "STEP 0 refused")
    seen[:] = []
    Wm.br.put("ah:fn:wouldclose", Spy(lambda o: (seen.append(1), str(real.apply(o)))[1]))
    r = str(Wm.Tx.playerStart(um, "hub", False))
    K.check(r.startswith("+The void is imprinting") and len(seen) == 2, "STEP 0 with ok:0:0 both times: the rebirth runs (%s)" % r[:50])
    CK.new(Wm, k, "STEP 0 ok")
    K.check(Wm.br.get("rebirth:busy:" + k) == Bool.FALSE, "STEP 0 a finished rebirth republishes busy FALSE at once")
    # the admin force path skips the market (documented)
    Wm, bm_, Hm, a = mkt("force", ["sold"])
    r = str(Wm.Tx.adminStart(Wm.uuid(k), -1))
    K.check(r.startswith("+Rebirth tx"), "FORCE: /rebirthadmin rebirth ignores the market (admin test path)")
    # an aborted rebirth republishes busy FALSE at once
    Wm, bm_, Hm, a = mkt("abort_pub", [])
    um = Wm.uuid(k)
    Wm.br.put("rebirth:busy:" + k, Bool.TRUE)
    cf = Wm.files(k)["coins"]
    os.remove(cf)
    os.makedirs(cf)
    Wm.Tx.adminStart(um, -1)
    K.check(Wm.br.get("rebirth:busy:" + k) == Bool.FALSE and not Wm.Sto.BUSY.containsKey(k), "ABORT: a cancelled rebirth republishes rebirth:busy FALSE at once")

    # ---- RbRun mode 5 inline (a refusal told) + Continue handed to SkyyRebirth-IO from the page
    Wm, bm_, Hm, a = mkt("run5", ["closable", "sold"])
    um = Wm.uuid(k)
    Wm.Run(k, 5, um).run()
    K.check(any("could not close" in str(t) for t in Wm.told), "RUN mode 5 refused: told in chat")
    Wm, bm_, Hm, a = mkt("run5_io", ["closable"])
    um = Wm.uuid(k)
    Wm.Sto.start()
    try:
        pg = Wm.Page(um, "hub")
        pg.build(None, UCB(), UEB(), None)
        t1 = int(JClass("java.lang.System").currentTimeMillis())
        pg.click(t1, "hub", True)
        r_io = str(pg.click(t1 + 1000, "hub", True))
        ok_io = PW.wait_until(lambda: not Wm.Sto.BUSY.containsKey(k) and not Wm.journals()[0] and len(Wm.journals()[1]) > 0, 15)
    finally:
        Wm.Sto.stop()
    K.check(r_io.startswith("+Closing your Bazaar / AH orders") and ok_io, "CONTINUE via SkyyRebirth-IO (RbRun mode 5): closed + reborn (%s)" % r_io[:50])
    CK.new(Wm, k, "CONTINUE via IO")
    # ---- FIX ROUND: THE NEXUS CLICK = the button the left panel offers (Skyy 2026-10-12: "you click it, then confirm to rebirth")
    Wm, bm_, Hm, a = mkt("nexus", ["closable"])
    um = Wm.uuid(k)
    pg = Wm.Page(um, "hub")
    pg.handleDataEvent(None, None, '{"a":"n25"}')
    ev = UEB()
    pg.build(None, UCB(), ev, None)
    nx_bound = any("SkyyRbNexusB" in str(e_.selector) for e_ in ev.getEvents())
    K.check(int(pg.view) == 1 and int(pg.goKind) == 2 and nx_bound, "NEXUS bound in the node view too (Continue offered)")
    pg.handleDataEvent(None, None, '{"a":"nexus"}')
    K.check(int(pg.view) == 0 and int(pg.sel) == -1 and str(pg.last) == "=armed" and int(pg.armedKind) == 2, "NEXUS first click: back to the rebirth view, Continue armed (%s)" % pg.last)
    pg.armedAt = int(JClass("java.lang.System").currentTimeMillis()) - 2000
    pg.handleDataEvent(None, None, '{"a":"nexus"}')
    K.check(str(pg.last).startswith("+Closing your Bazaar / AH orders"), "NEXUS second click confirms: Continue runs (%s)" % pg.last)
    CK.new(Wm, k, "NEXUS Continue")
    # FIX ROUND 2: leaving the rebirth view disarms - a Nexus click from the node view only arms (the armed note was not on screen)
    Wm, bm_, Hm, a = mkt("nexus2", ["closable"])
    um = Wm.uuid(k)
    pg = Wm.Page(um, "hub")
    pg.build(None, UCB(), UEB(), None)
    pg.handleDataEvent(None, None, '{"a":"nexus"}')
    armed1 = str(pg.last) == "=armed" and int(pg.armedAt) > 0
    pg.armedAt = int(JClass("java.lang.System").currentTimeMillis()) - 2000
    pg.handleDataEvent(None, None, '{"a":"n25"}')
    dis_sel = int(pg.armedAt) == 0
    pg.armedAt = int(JClass("java.lang.System").currentTimeMillis()) - 2000     # even if something left it armed: the node view never confirms
    pg.build(None, UCB(), UEB(), None)
    pg.handleDataEvent(None, None, '{"a":"nexus"}')
    K.check(armed1 and dis_sel and str(pg.last) == "=armed" and int(pg.view) == 0 and not Wm.Sto.BUSY.containsKey(k) and not Wm.journals()[0] and len(Wm.journals()[1]) == 0,
            "NEXUS armed -> a node click disarms; a Nexus click from the node view only ARMS, nothing starts (%s)" % pg.last)
    pg.armedAt = int(JClass("java.lang.System").currentTimeMillis()) - 2000
    pg.handleDataEvent(None, None, '{"a":"n25"}')
    pg.armedAt = int(JClass("java.lang.System").currentTimeMillis()) - 2000
    pg.handleDataEvent(None, None, '{"a":"back"}')
    K.check(int(pg.armedAt) == 0 and int(pg.view) == 0 and len(Wm.journals()[1]) == 0, "NEXUS Back from the node view disarms too")

    # ---------------------------------------------------------------- THE PAGE: node view, Buy, colours, bindings, packet size, the fit
    W, base, H = fresh("page")
    u = W.uuid(k)
    W.Cfg.HUB_TEST = "hub"
    write_rb(base, k, {"n": 0, "pts.Mining": 10, "node.Mining.xp": 5, "node.Mining.dust": 2, "node.Mining.echo": 1, "title": "Void-Touched I"})
    W.Sto.CACHE.clear()
    W.Cfg.ON = False
    W.Cfg.PERM_TEST = Spy(lambda o: Bool.FALSE)
    scans = []
    _real_wc = W.br.get("ah:fn:wouldclose")
    W.br.put("ah:fn:wouldclose", Spy(lambda o: (scans.append(1), str(_real_wc.apply(o)))[1]))
    pg = W.Page(u, "hub")
    ev = UEB()
    pg.build(None, UCB(), ev, None)
    K.check(int(pg.view) == 0 and int(pg.sel) == -1 and len(ev.getEvents()) == 90 and int(pg.goKind) == 0, "PAGE view 0: 88 node bindings + Close + the Nexus (rebirth off: no Rebirth)")
    K.check("8 levels in a row open the next row" in str(pg.foot) and len(scans) == 1, "PAGE footer reads tree.rowNeed; one market scan on opening: %s" % pg.foot)
    nc = [str(x) for x in pg.nc]
    nt = [str(x) for x in pg.nt]
    K.check(nc[22] == "#8fc8ff(0.85)" and nt[22] == "5" and nc[23] == "#8fc8ff(0.45)" and nt[23] == "2" and nc[24] == "#8fc8ff(0.45)" and nc[25] == "#2a3346"
            and nt[25] == "0" and nc[28] == "#1a2131" and nt[28] == "0/8" and nc[30] == "#121825" and nt[30] == "" and nc[0] == "#2a3346" and nc[3] == "#1a2131",
            "PAGE disc colours: maxed / part / open 0 / next row '0/8' / locked; Class row 2 next: %s %s" % (nc[22:31], nt[22:31]))
    pg.handleDataEvent(None, None, '{"a":"n25"}')
    ev = UEB()
    cm = UCB()
    pg.build(None, cm, ev, None)
    K.check(int(pg.view) == 1 and int(pg.sel) == 25 and str(pg.nc[25]) == "#ffe2a8" and str(pg.nvName) == "Mining Fortune" and str(pg.nvSub) == "Mining - Row 2"
            and str(pg.nvLevel) == "Level 0 / 5" and str(pg.nvNow) == "Now: nothing yet" and str(pg.nvNext) == "Next: +2 % double Mining drops"
            and str(pg.nvCost) == "Cost: %d Mining points" % cost_py(8) and str(pg.nvHave) == "You have 10 Mining points" and not pg.canBuy
            and str(pg.nvStatus) == "Rebirth is switched off - only admins can buy while it is off." and len(ev.getEvents()) == 90,
            "PAGE node view (off, not admin): the node, cost %d, no Buy binding (88 + Back + Nexus): %s / %s" % (cost_py(8), pg.nvCost, pg.nvStatus))
    K.check(len(scans) == 1, "PAGE CACHE: a node click reuses the requirement / market scan (no AH lock per click): %d scans" % len(scans))
    W.Cfg.PERM_TEST = Spy(lambda o: Bool.TRUE)
    ev = UEB()
    pg.build(None, UCB(), ev, None)
    K.check(pg.canBuy and len(ev.getEvents()) == 91 and str(pg.nvStatus) == "Press Buy to spend %d Mining points." % cost_py(8),
            "PAGE admin while off: Buy bound (88 + Back + Nexus + Buy): %s" % pg.nvStatus)
    pg.handleDataEvent(None, None, '{"a":"buy"}')
    p = props(rb_file(base, k))
    K.check(str(pg.status).startswith("+Mining Fortune level 1 bought") and not pg.pending and p.get("node.Mining.dd") == "1", "PAGE Buy inline: bought (%s)" % pg.status)
    # FIX ROUND: a LATE duplicate Buy (after the job finished, before the page was rebuilt) sends the level the view showed -> refused
    _st1 = pg.status
    _h1 = sha(rb_file(base, k))
    pg.handleDataEvent(None, None, '{"a":"buy"}')
    K.check(str(pg.status).startswith("-Mining Fortune changed meanwhile (now level 1)") and sha(rb_file(base, k)) == _h1,
            "PAGE a late duplicate Buy: refused, nothing charged (%s)" % pg.status)
    # FIX ROUND: a profile switched under the open page: Buy refused, nothing charged on either profile
    W.keymap[k] = k + "-p2"
    pg.handleDataEvent(None, None, '{"a":"buy"}')
    K.check(str(pg.status) == "-Your active profile changed - look at the node again." and sha(rb_file(base, k)) == _h1 and not os.path.exists(rb_file(base, k + "-p2")),
            "PAGE Buy after a profile switch: refused, nothing charged (%s)" % pg.status)
    W.keymap.clear()
    pg.status = _st1
    pg.build(None, UCB(), UEB(), None)
    K.check(str(pg.nvLevel) == "Level 1 / 5" and str(pg.nvStCol) == "#39f493", "PAGE after Buy: level 1, the green result line")
    pg.handleDataEvent(None, None, '{"a":"n28"}')
    pg.build(None, UCB(), UEB(), None)
    K.check(str(pg.nvRow) == "Locked - buy 8 levels in Row 2 first (1 now)" and not pg.canBuy, "PAGE a node in the next row: %s" % pg.nvRow)
    K.check(len(scans) == 1, "PAGE CACHE: node-view rebuilds (Buy, other nodes) still reuse the scan: %d" % len(scans))
    pg.handleDataEvent(None, None, '{"a":"n30"}')
    pg.build(None, UCB(), UEB(), None)
    K.check(str(pg.nvRow) == "Locked - open Row 3 first" and not pg.canBuy, "PAGE a node two rows on: %s" % pg.nvRow)
    pg.handleDataEvent(None, None, '{"a":"n32"}')
    pg.build(None, UCB(), UEB(), None)
    K.check(str(pg.nvRow) == "Locked - open Row 4 first" and str(pg.nvSub) == "Mining - Row 5 keystone", "PAGE the keystone two rows away: %s" % pg.nvRow)
    pg.handleDataEvent(None, None, '{"a":"n22"}')
    pg.build(None, UCB(), UEB(), None)
    K.check(str(pg.nvNext) == "Next: max level reached" and str(pg.nvCost) == "Cost: -" and str(pg.nvStatus) == "This node is at its max level.", "PAGE a maxed node")
    pg.handleDataEvent(None, None, '{"a":"back"}')
    W.Cfg.ROW_NEED = 5
    pg.build(None, UCB(), UEB(), None)
    K.check(int(pg.view) == 0 and int(pg.sel) == -1, "PAGE Back: the rebirth view")
    K.check(len(scans) == 2 and "5 levels in a row open the next row" in str(pg.foot), "PAGE CACHE: the rebirth view scans again; the footer follows tree.rowNeed 5: %s" % pg.foot)
    W.Cfg.ROW_NEED = 8
    pg.handleDataEvent(None, None, '{"a":"n25"}')
    pg.handleDataEvent(None, None, '{"a":"nexus"}')
    K.check(str(pg.last) == "=nothing" and int(pg.view) == 0 and int(pg.sel) == -1, "NEXUS click with nothing offered (off): back to the rebirth view, nothing armed")
    W.br.put("ah:fn:wouldclose", _real_wc)
    for junk in (None, "", '{"a":"n999"}', '{"a":"nx"}', '{"b":"n1"}', '{"a":"close"}', '{"a"'):
        pg.handleDataEvent(None, None, junk)
    K.check(int(pg.view) == 0, "PAGE junk events ignored")
    # Buy queued on the real SkyyRebirth-IO: pending, then RbJob.run hands the result to the page
    pg.handleDataEvent(None, None, '{"a":"n25"}')
    pg.build(None, UCB(), UEB(), None)
    W.Sto.start()
    try:
        pg.handleDataEvent(None, None, '{"a":"buy"}')
        pend = bool(pg.pending)
        pg.handleDataEvent(None, None, '{"a":"buy"}')        # a double click while queued: ignored
        okq = PW.wait_until(lambda: not pg.pending and pg.status is not None, 10)
    finally:
        W.Sto.stop()
    p = props(rb_file(base, k))
    K.check(okq and str(pg.status).startswith("+Mining Fortune level 2 bought") and p.get("node.Mining.dd") == "2", "PAGE Buy on SkyyRebirth-IO: pending, then the result (a double click bought once): %s %s" % (pend, pg.status))
    # RbJob.run without a page (admin) tells in chat; RbRefresh with nothing to refresh; a live page's refresh hop without a server
    Job = JClass(RB + "RbJob", loader=W.L)
    Job(3, k, u, 2, 5, True, None).run()
    K.check(any("Added 5 test points" in str(t) for t in W.told), "RbJob.run (no page): the admin result in chat")
    Rf = JClass(RB + "RbRefresh", loader=W.L)
    try:
        Rf(None).run()
        Rf(pg).run()
        lp = W.Page(None)
        lp.sel = 25
        Job(1, k, u, 25, 2, True, lp).run()
        K.check(str(lp.status).startswith("+") or str(lp.status).startswith("-"), "RbJob.run with a live page (no server): the result set, the refresh hop fails quietly: %s" % lp.status)
        lp.onDismiss(None, None)
        K.check(bool(lp.gone), "RbPage.onDismiss marks the page gone (RbRefresh then skips it)")
        try:
            lp.refresh()
        except Exception:
            pass   # rebuild() needs a live player: the call path is what the audit checks

    except Exception as e:
        K.check(False, "RbRefresh / RbJob.run / onDismiss without a server: %s" % e)
    # the rebirth button states
    W.Cfg.ON = True
    pg.handleDataEvent(None, None, '{"a":"back"}')
    ev = UEB()
    pg.build(None, UCB(), ev, None)
    K.check(int(pg.goKind) == 1 and len(ev.getEvents()) == 91, "PAGE on + everything met: Rebirth bound (88 + Close + Rebirth + Nexus)")
    K.check(str(pg.click(1000, "hub", False)) == "=armed" and str(pg.click(1300, "hub", False)) == "=armed" and int(pg.armedAt) == 1000, "PAGE arm + double click")
    pg.armedAt = 0
    # the page packet, both views, at the biggest state: under CustomPage.MAX_SIZE
    CP = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPage")
    LIFE = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime")
    sizes = []
    for view in ("back", "n32"):
        pg.handleDataEvent(None, None, '{"a":"%s"}' % view)
        b_, e_ = UCB(), UEB()
        pg.build(None, b_, e_, None)
        sizes.append(int(CP("SkyyRb", True, True, LIFE.CanDismiss, b_.getCommands(), e_.getEvents()).computeSize()))
    K.check(max(sizes) < int(CP.MAX_SIZE), "PAGE packet: rebirth view %d / node view %d bytes < CustomPage.MAX_SIZE %d" % (sizes[0], sizes[1], int(CP.MAX_SIZE)))
    K.notes.append("PAGE packet sizes: rebirth view %d, node view %d of %d" % (sizes[0], sizes[1], int(CP.MAX_SIZE)))
    # THE FIT: every node at every level, the real node-view texts in the rows the markup declares
    import re as _re
    import skyyui as SUI
    heights = {}
    for view in ("n25", "back"):
        pg.handleDataEvent(None, None, '{"a":"%s"}' % view)
        b_ = UCB()
        pg.build(None, b_, UEB(), None)
        for cmd in b_.getCommands():
            tx = None if cmd.text is None else str(cmd.text)
            for m_ in _re.finditer(r"Label #(SkyyRb(?:Nv\w+|Pt\d|Req\d|Note)) \{ Anchor: \(([^)]*)\)", tx or ""):
                hm = _re.search(r"Height: (\d+)", m_.group(2))
                if hm:
                    heights[m_.group(1)] = int(hm.group(1))
    SZ = {"SkyyRbNvName": (16, True), "SkyyRbNvSub": (13, True), "SkyyRbNvLive": (12, False), "SkyyRbNvLevel": (14, True), "SkyyRbNvNow": (13, False),
          "SkyyRbNvNext": (13, False), "SkyyRbNvCost": (14, False), "SkyyRbNvHave": (14, False), "SkyyRbNvRow": (13, False), "SkyyRbNvStatus": (13, True)}
    SZ.update(dict(("SkyyRbPt%d" % i_, (13, False)) for i_ in range(8)))
    texts = []
    write_rb(base, k, dict([("n", 10), ("title", "x")] + [("pts." + a_, 999999999) for a_ in ARMS]))
    W.Sto.CACHE.clear()
    W.Cfg.DUST_NODE = 5.0
    for idx in range(88):
        for l in range(int(T.NMAX[idx]) + 1):
            d = dict([("n", 10)] + [("pts." + a_, 999999999) for a_ in ARMS])
            d["node." + ids[idx]] = l
            W.Sto.CACHE.put(k, P(d))
            pg.sel = idx
            pg.view = 1
            pg.status = None
            pg.build(None, UCB(), UEB(), None)
            for fld in ("nvName", "nvSub", "nvLive", "nvLevel", "nvNow", "nvNext", "nvCost", "nvHave", "nvRow", "nvStatus"):
                texts.append(("SkyyRb" + fld[0].upper() + fld[1:], str(getattr(pg, fld))))
            texts += [("SkyyRbPt%d" % i_, str(x)) for i_, x in enumerate(pg.pt)]
    W.Cfg.DUST_NODE = 0.25
    over = []
    for rid, tx in texts:
        if not tx or rid not in heights:
            continue
        sz, bd = SZ[rid]
        lines = SUI.text_lines(tx, 260 - 24, SUI.fs(sz), bold=bd)
        if lines * SUI.line_height(SUI.fs(sz), bold=bd) > heights[rid] + 0.5:
            over.append((rid, tx, lines, heights[rid]))
    K.check(not over and len(texts) > 4000 and len([h for h in heights if h.startswith("SkyyRbNv")]) == 11 and len([h for h in heights if h.startswith("SkyyRbPt")]) == 8,
            "FIT: %d real node-view texts (every node at every level, 999999999 points, Dust x5) fit their rows: %s (rows %s)" % (len(texts), over[:3], sorted(heights)))

    # ---------------------------------------------------------------- /rebirthadmin points / refund + status + config
    W, base, H = fresh("admin")
    u = W.uuid(k)
    A = W.Adm
    r1 = [str(x) for x in A.run(u, "points mining 50", 1)]
    r2 = [str(x) for x in A.run(u, "points all 3", 1)]
    p = props(rb_file(base, k))
    K.check(r1[0].startswith("+Added 50") and r2[0].startswith("+Added 3 test points to every arm") and p.get("pts.Mining") == "53" and p.get("pts.Cooking") == "3",
            "ADMIN points (inline): %s" % r1)
    K.check(str(A.run(u, "points mining", 1)[0]).startswith("-Usage") and str(A.run(u, "points moon 5", 1)[0]).startswith("-Usage")
            and str(A.run(u, "refund", 1)[0]).startswith("-Usage") and str(A.run(u, "points mining 0", 1)[0]).startswith("-Usage"), "ADMIN bad arguments")
    W.Sto.start()
    try:
        rq = str(A.run(u, "refund mining", 1)[0])
        okr = PW.wait_until(lambda: any("Refunded the Mining arm" in str(t) for t in W.told), 10)
    finally:
        W.Sto.stop()
    K.check(rq.startswith("=Queued") and okr, "ADMIN refund on SkyyRebirth-IO: queued, told in chat")
    K.check(any("points <arm|all> <n>" in str(x) and "points <arm|all> reset" in str(x) for x in A.run(u, "help", 1)), "ADMIN help lists points / reset / refund")
    rr_ = [str(x) for x in A.run(u, "points all reset", 1)]
    p = props(rb_file(base, k))
    K.check(rr_[0].startswith("+Reset every arm") and not any(a_.startswith("pts.") for a_ in p) and str(A.run(u, "points mining resetx", 1)[0]).startswith("-Usage")
            and str(A.run(u, "points mining reset 3", 1)[0]).startswith("-Usage"), "ADMIN points all reset (RbJob op 4): the test points are gone: %s" % rr_)
    cfgf = os.path.join(base, "Skyy_SkyyRebirth", "config.properties")
    txt = open(cfgf, encoding="utf8").read()
    K.check("tree.costGrowth=1.08" in txt and "tree.rowNeed=8" in txt and "stat.perRebirth=3" in txt and "stat.cap=30" in txt
            and all(x_ in txt for x_ in ("tree.wisdom=2", "tree.fortune=2", "tree.echo=4", "tree.keyXp=10", "tree.statNode=1", "tree.keyStat=2", "tree.speed=3")),
            "CONFIG the default text has the tree rows + the 7 node strengths")
    open(cfgf, "w", encoding="utf8").write(txt.replace("tree.costGrowth=1.08", "tree.costGrowth=9").replace("tree.rowNeed=8", "tree.rowNeed=0").replace("stat.cap=30", "stat.cap=x")
                                            .replace("tree.echo=4", "tree.echo=99").replace("tree.wisdom=2", "tree.wisdom=2.5").replace("tree.keyXp=10", "tree.keyXp=-3"))
    W.Cfg.loadCfg(False)
    K.check(float(W.Cfg.COST_GROWTH) == 2.0 and int(W.Cfg.ROW_NEED) == 1 and float(W.Cfg.STAT_CAP) == 30.0 and float(W.Cfg.W_ECHO) == 25.0
            and float(W.Cfg.W_XP) == 2.5 and float(W.Cfg.W_KEY) == 0.0, "CONFIG tree rows clamp / a bad number = default (echo 99 -> 25, keyXp -3 -> 0, wisdom 2.5 read)")
    open(cfgf, "w", encoding="utf8").write("rebirth.on=false\n")
    W.Cfg.loadCfg(False)
    K.check(float(W.Cfg.COST_GROWTH) == 1.08 and int(W.Cfg.ROW_NEED) == 8 and float(W.Cfg.STAT_PER) == 3.0 and float(W.Cfg.W_XP) == 2.0 and float(W.Cfg.W_ECHO) == 4.0
            and float(W.Cfg.W_KEY) == 10.0, "CONFIG a 0.2 file without the tree lines reads the defaults")
    CPub = JClass(RB + "CfgPub", loader=W.L)
    CPub.start(W.path(base), W.Cfg.LOG)
    hdr = W.br.get("config:def:SkyyRebirth")
    K.check(hdr is not None and len(hdr[7]) == 20 and str(hdr[3]) == VERSION, "CONFIG config:def:SkyyRebirth: 20 rows, version %s" % VERSION)
    CPub.shutdown()

    # ---------------------------------------------------------------- static
    g = PW.calls(jar)
    K.check(RB + "RbStore.save" in g.get("RbTree.buy", set()) and RB + "RbStore.readNow" in g.get("RbTree.buy", set()), "static: a buy reads fresh and saves once (RbStore.save)")
    K.check(RB + "RbJob.submit" in g.get("RbPage.buy", set()) and RB + "RbTree.buy" not in g.get("RbPage.buy", set()), "static: the page never writes itself (RbJob.submit)")
    K.check(RB + "RbRefresh.<init>" in g.get("RbJob.run", set()) and any("getCustomPage" in x for x in g.get("RbRefresh.run", set()))
            and RB + "RbPage.refresh" in g.get("RbRefresh.run", set()) and any("rebuild" in x for x in g.get("RbPage.refresh", set())),
            "static: RbJob.run -> RbRefresh -> RbPage.refresh (rebuild is protected) only while it is the open page")
    K.check(RB + "RbCheck.marketClear" in g.get("RbTx.begin0", set()) and RB + "RbPub.publish" in g.get("RbTx.begin", set()), "static: begin0 re-checks the market; begin republishes busy on a refusal")
    K.check(RB + "RbTree.push" in g.get("RbPub.publish", set()) and RB + "RbTree.unpush" in g.get("RbPub.tick", set()) and RB + "RbTree.unpush" in g.get("RbPub.clearAll", set()),
            "static: the bonus + title publish / unpublish")
    K.check(RB + "RbPub.busyPut" in g.get("RbTx.begin", set()) and RB + "RbPub.busyPut" in g.get("RbPub.publish", set())
            and not any("java.util.Map.put" in x for x in g.get("RbTx.begin", set())) and RB + "RbTree.wipe" in g.get("RbJob.exec", set()),
            "static: rebirth:busy only through RbPub.busyPut (begin no longer puts it itself); RbJob op 4 = RbTree.wipe")
    _gen = open(os.path.join(HERE, "build_skyyrebirth_%s.py" % VERSION), encoding="utf8").read()
    K.check("new @PKG@.RbTick(), 5L, 1L, java.util.concurrent.TimeUnit.SECONDS" in _gen, "static: the publish tick runs every second (a profile switch moves the bonus + title within 1 s)")
    su = g.get("SkyyRebirthPlugin.setup", set())
    K.check("java.util.Map.put" in su and any("RbFn.<init>" in x for x in su), "static: setup publishes the functions (stat / title / cos executed above through RbFn)")
    K.save()


# ====================================================================================================== KK: the tree under a real kill
def run_treekiller(out, jar, scratch, _home):
    HK.jvm([B.SERVER_JAR], verify=False)
    from jpype import JClass
    d = HK.arg("--kdir")
    W = T2.World(d, start=False)
    T = JClass(RB + "RbTree", loader=W.L)
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(d, "Skyy_SkyyRebirth", "players")) if f.endswith(".properties"))
    rnd = random.Random(int(HK.arg("--seed", "1")))
    open(os.path.join(d, "ready"), "w").write("1")
    while True:
        kk = rnd.choice(keys)
        u = W.uuid(kk[:36])
        idx = rnd.randrange(88)
        if rnd.random() < 0.03:
            T.refund(kk, u, rnd.randrange(-1, 8))
            continue
        p = W.Sto.readNow(kk)
        T.buy(kk, u, idx, int(T.lv(p, idx)), True)


def run_kill(out, jar, scratch, _home):
    K = HK.Child(out)
    env = dict(os.environ)
    for rnd in range(4):
        d = os.path.join(scratch, "kill%d" % rnd)
        for i in range(40):
            kk = "00000000-0000-4000-8000-%012d" % (5000 + i)
            seed(d, kk, 10, purse=1000 + i, bank=50000 + i)
        p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--phase", "killer", "--out", os.path.join(scratch, "kk.json"), "--dir", scratch,
                              "--jar", jar, "--kdir", d], env=env)
        t0 = time.time()
        while not os.path.exists(os.path.join(d, "ready")) and time.time() - t0 < 120:
            time.sleep(0.02)
        time.sleep(random.Random(rnd).uniform(0.05, 1.2))
        p.kill()
        p.wait()
        K.check(not os.path.exists(os.path.join(d, "finished")), "KK%d: killed mid-run (rc %s)" % (rnd, p.returncode))
    for rnd in range(4):
        d = os.path.join(scratch, "tkill%d" % rnd)
        for i in range(20):
            kk = "00000000-0000-4000-8000-%012d" % (7000 + i) + ("-p2" if i % 2 else "")
            write_rb(d, kk, dict([("n", 2)] + [("pts." + a_, 400) for a_ in ARMS]))
        p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--phase", "treekiller", "--out", os.path.join(scratch, "tk.json"), "--dir", scratch,
                              "--jar", jar, "--kdir", d, "--seed", str(rnd)], env=env)
        t0 = time.time()
        while not os.path.exists(os.path.join(d, "ready")) and time.time() - t0 < 120:
            time.sleep(0.02)
        time.sleep(random.Random(100 + rnd).uniform(0.5, 2.5))
        p.kill()
        p.wait()
        K.check(p.returncode != 0, "TK%d: the tree child killed mid-run (rc %s)" % (rnd, p.returncode))
    K.save()


def run_killcheck(out, jar, scratch, _home):
    T2.run_killcheck(out, jar, scratch, _home)
    from jpype import JClass
    K = HK.Child(out + ".tree")
    for rnd in range(4):
        d = os.path.join(scratch, "tkill%d" % rnd)
        W = T2.World(d)
        T = JClass(RB + "RbTree", loader=W.L)
        bad, levels = [], 0
        for f in sorted(os.listdir(os.path.join(d, "Skyy_SkyyRebirth", "players"))):
            if not f.endswith(".properties"):
                continue
            kk = f[:-11]
            p = props(os.path.join(d, "Skyy_SkyyRebirth", "players", f))
            good, why = tree_ok(p, dict((a_, 400) for a_ in ARMS))
            levels += sum(int(v) for a_, v in p.items() if a_.startswith("node."))
            if not good:
                bad.append((kk, why))
            r = str(T.buy(kk, W.uuid(kk[:36]), 0, int(T.lv(W.Sto.readNow(kk), 0)), True))   # the next buy works after the kill (a stale .tmp is harmless)
            if not (r.startswith("+") or "max level" in r or "Not enough" in r):
                bad.append((kk, "buy after the kill: " + r))
        K.notes.append("TK%d: %d tree levels held across 20 profiles after the kill, %d bad" % (rnd, levels, len(bad)))
        K.check(not bad and levels > 0, "TK%d after the kill: every profile file parses, points >= 0, pts + spent = 400 per arm, spent = the cost sum (%d levels held), a buy works after it: %s"
                % (rnd, levels, bad[:2]))
    K.save()
    a = json.load(open(out))
    b = json.load(open(out + ".tree"))
    a["ok"] = a.get("ok", 0) + b.get("ok", 0)
    a["fails"] = a.get("fails", []) + b.get("fails", [])
    a["notes"] = a.get("notes", []) + b.get("notes", [])
    json.dump(a, open(out, "w"), indent=1)


# ====================================================================================================== D: start twice on live copies
def run_live(out, jar, scratch, home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR], verify=True)
    K = HK.Child(out)
    mods = os.path.dirname(home)
    for m_ in ("Skyy_SkyyCoins", "Skyy_SkyyBank", "Skyy_SkyyRebirth", "Skyy_SkyyAuctions"):
        if os.path.isdir(os.path.join(MODS_LIVE, m_)) and not os.path.isdir(os.path.join(mods, m_)):
            shutil.copytree(os.path.join(MODS_LIVE, m_), os.path.join(mods, m_))
    live_rb = os.path.isdir(os.path.join(mods, "Skyy_SkyyRebirth"))
    before = dict((m_, tree(os.path.join(mods, m_))) for m_ in ("Skyy_SkyySkills", "Skyy_SkyyCoins", "Skyy_SkyyBank", "Skyy_SkyyRebirth", "Skyy_SkyyAuctions"))
    W1 = T2.World(mods)
    s1 = tree(mods)
    W2 = T2.World(mods)
    s2 = tree(mods)
    after = dict((m_, tree(os.path.join(mods, m_))) for m_ in before)
    K.check(W1.open == 0 and W2.open == 0, "D no rebirth journal open on the live copy")
    if live_rb:
        K.check(after == before, "D every copied folder (Skills / Coins / Bank / Rebirth / Auctions) byte-identical after two starts (the live 0.2 config read as is)")
        K.check(float(W2.Cfg.COST_GROWTH) == 1.08 and int(W2.Cfg.ROW_NEED) == 8, "D the live config without the tree lines reads the defaults")
    else:
        K.check(all(after[m_] == before[m_] for m_ in before if m_ != "Skyy_SkyyRebirth"), "D the copied folders byte-identical (no live Skyy_SkyyRebirth yet)")
    K.check(s1 == s2, "D start 2 changes nothing")
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(mods, "Skyy_SkyySkills", "players")) if f.endswith(".properties") and len(f) in (47, 50, 51))
    ahh = os.path.join(mods, "Skyy_SkyyAuctions")
    if os.path.isdir(ahh):
        a = TA.Ah(AH_JAR, ahh)
        a.start()
        W2.br.put("ah:fn:wouldclose", a.Fn(1))
        bz0, bz1 = bazaar_fns()
        W2.br.put("bazaar:fn:wouldclose", bz1)
        t0 = tree(ahh)
        res = {}
        for kk in keys:
            mk = W2.Chk.market(kk)
            res[str(mk[1])] = res.get(str(mk[1]), 0) + 1
        K.check(len(keys) > 0 and tree(ahh) == t0 and all(r_.startswith("OK") or r_.startswith("NO") for r_ in res), "D every live profile key's market line from a REAL SkyyAuctions on the copy, nothing written: %s" % res)
        K.notes.append("D live market lines: %s" % res)
    tt = JClass(RB + "RbTree", loader=W2.L)
    n_ok = 0
    for kk in keys:
        p = W2.Sto.readNow(kk)
        n_ok += 1 if p is not None and int(tt.armLevels(p, 0)) >= 0 else 0
    _theirs = ("Skyy_SkyyAuctions/", "Skyy_Market/")        # the real SkyyAuctions started on the copy keeps its own files
    s3 = dict((a_, b_) for a_, b_ in tree(mods).items() if not a_.startswith(_theirs))
    s2r = dict((a_, b_) for a_, b_ in s2.items() if not a_.startswith(_theirs))
    K.check(n_ok == len(keys) and s3 == s2r, "D every live profile reads in the tree (%d), nothing of ours written: %s"
            % (n_ok, sorted(set(s3.items()) ^ set(s2r.items()))[:4]))
    K.save()


if __name__ == "__main__":
    if "--phase" in sys.argv and HK.arg("--phase") == "killer":
        T2.run_killer(None, JAR, SCRATCH, None)
        sys.exit(0)
    if "--phase" in sys.argv and HK.arg("--phase") == "treekiller":
        run_treekiller(None, JAR, SCRATCH, None)
        sys.exit(0)
    for j_ in (T2.SK_JAR, T2.CO_JAR, T2.BK_JAR, T2.PF_JAR, AH_JAR, BZ_JAR):
        assert os.path.isfile(j_), j_
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("kill", run_kill), ("killcheck", run_killcheck), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyySkills"))
