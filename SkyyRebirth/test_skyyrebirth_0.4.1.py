"""SkyyRebirth 0.4.1 - harness (tools/rebirth_0_4_1_patch.py: the market texts, the respec save-back gap, "petecho", the Head Start respec guard).
Build first: python tools/rebirth_0_4_1_patch.py && python SkyyRebirth/build_skyyrebirth_0.4.1.py

    python SkyyRebirth/test_skyyrebirth_0.4.1.py [--dir <empty folder inside tools/dev/scratch/>]

  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.0 -> 0.4.1: exactly the planned members differ (EXPECT)
  V / P / D    the WHOLE 0.4.0 harness (SkyyRebirth/test_skyyrebirth_0.4.0.py run_vp / run_page / run_live) against the 0.4.1 jar - VP, buy,
               the respec (charm ids from the page, save first, take after, put back on failure), the migration, the page, start twice on a
               scratch COPY of the live Skyy_SkyyRebirth
  F41 fixes    EXECUTED: a Bazaar coin claim names /bazaar > My orders (or /bazaar claim), an AH sale /ah > Manage; the requirement line
               "NO  Claim sale coins first"; closeWhy names the right place; the respec whose take is refused AND whose save-back fails stays
               done and free and names no charm; the 0.4.0 crit re-check (the page's charm ids travel with the job: a job carrying other ids
               is refused, nothing taken); fix round: rebirth:fn:stat "petecho" = Beastmastery Echo alone ("petxp" unchanged), Void
               Insight's text back to 0.4.0's; a player's respec is refused while Head Start has ranks and tree:fn:headUsed answers > 0 or
               null (nothing saved / changed), allowed at 0, without SkyyTrees, without Head Start ranks, and for the admin refund
  AA  engine-access audit
NOT COVERED: the "[Rebirth] Closed N ..." chat line of continueNow (a text in a path that needs the whole rebirth; unchanged logic).
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


VERSION = "0.4.1"
RB = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.4.0.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "st3fix", "rb")))
T40 = _load("t_rb040", os.path.join(HERE, "test_skyyrebirth_0.4.0.py"))
T40.VERSION, T40.JAR = VERSION, JAR
T40.T34.VERSION, T40.T34.JAR = VERSION, JAR
R = T40.R
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyRebirthPlugin": ["~m setup"],   # the version text
    "RbMig": ["~m migrate"], "RbStore": ["~m writeNow"],   # only the @VERSION@ text in the vp-migration.log line / the file comment
    "RbCheck": ["~m closeWhy", "~m detail", "~m market"],
    "RbTx": ["~m continueNow"],
    "RbTree": ["+m headBlock", "~m respec", "~m stat"],   # fix round: the Head Start guard + "petecho"
}


def run_f41(out, jar, scratch, _home):
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    from jpype import JClass
    K = HK.Child(out)
    Bag, Part, Const = T40.fakes()
    Cfg, St, Tr, Ck = R("RbCfg"), R("RbStore"), R("RbTree"), R("RbCheck")
    AL = JClass("java.util.ArrayList")
    home, pl, U, k = T40.world(scratch, "f41")
    # ---------------------------------------------------------------- 1. the market texts
    bz = "ok:0:1:1:50\nB1\t2\t3\t50\t0\tWheat"
    ah = "ok:0:1:1:70\nA1\t2\t1\t70\t0\tIron Sword"
    lb, la = AL(), AL()
    cb, ca = Ck.detail(bz, "Bazaar", lb), Ck.detail(ah, "AH", la)
    K.eq(str(lb.get(0)), "Wheat x3 SOLD - claim your 50 coins in /bazaar > My orders (or /bazaar claim) first", "F41 a Bazaar coin claim names /bazaar > My orders")
    K.eq(str(la.get(0)), "Iron Sword x1 SOLD - claim your 70 coins in /ah > Manage first", "F41 an AH sale still names /ah > Manage")
    K.check(int(cb[2]) == 1 and int(ca[2]) == 1, "F41 both count as a blocking coin claim")
    Cfg.BRIDGE.put("bazaar:fn:wouldclose", Const(bz))
    Cfg.BRIDGE.put("ah:fn:wouldclose", Const("ok:0:0:0:0"))
    m = Ck.market(k)
    K.check(int(m[0]) == 2 and str(m[1]) == "NO  Claim sale coins first" and "/bazaar > My orders" in str(list(m[3])),
            "F41 a Bazaar coin claim alone blocks with 'NO  Claim sale coins first' (was 'Claim AH sale coins'): %s %s" % (m[1], list(m[3])))
    w1 = str(Ck.closeWhy("err:blocked:2:1", "ok:0"))
    w2 = str(Ck.closeWhy("ok:3", "err:blocked:0:1"))
    K.check(w1.startswith("The Bazaar closed 2 and could not close 1 (claim your Bazaar coins in /bazaar > My orders or /bazaar claim)") and "/ah" not in w1,
            "F41 closeWhy (Bazaar): %s" % w1)
    K.check(w2.startswith("The Auction House closed 0 and could not close 1 (claim your AH sale coins in /ah > Manage") , "F41 closeWhy (AH): %s" % w2)
    # ---------------------------------------------------------------- 2. the respec: take refused AND the save-back fails -> done, free, no charm named
    Cfg.BRIDGE.put("acc:defs", T40.DEFS)
    f = os.path.join(pl, k + ".properties")
    open(f, "w").write("n=2\nv=4\nvp=10\nvpSpent=4\nnode.Class.echo=1\n")
    St.CACHE.clear()
    tmpd = os.path.join(pl, k + ".properties.tmp")
    from jpype import JImplements, JOverride
    Int = JClass("java.lang.Integer")

    @JImplements("java.util.function.Function")
    class BlockBag(object):
        """lists one charm; a take is refused AND blocks the tmp path, so the save-back after it fails"""
        def __init__(self):
            self.ids, self.calls = ["Skyy_Talisman_Speed_Uncommon"], []

        @JOverride
        def apply(self, o):
            a = list(o)
            self.calls.append(str(a[0]))
            if str(a[0]) == "list":
                return ",".join(self.ids)
            if str(a[0]) == "take":
                os.makedirs(tmpd, exist_ok=True)
                return Int(-1)
            return None
    bag = BlockBag()
    Cfg.BRIDGE.put("acc:fn:bag", bag)
    Cfg.RESPEC_CHARMS = 1
    r = str(Tr.respec(k, U, 4, "Skyy_Talisman_Speed_Uncommon", False, True))
    if os.path.isdir(tmpd):
        os.rmdir(tmpd)
    d = T40.props(f)
    K.check(r == "+Respec done: 1 ranks reset, 4 VP back." and bag.ids == ["Skyy_Talisman_Speed_Uncommon"] and "node.Class.echo" not in d and d.get("vp") == "14",
            "F41 take refused + save-back failed: the respec stays, FREE, and names no charm (was: 'the void took your ...'): %s / %s / %s" % (r, bag.ids, d))
    # ---------------------------------------------------------------- the 0.4.0 crit re-check: the page's ids travel with the job
    open(f, "w").write("n=2\nv=4\nvp=10\nvpSpent=4\nnode.Class.echo=1\n")
    St.CACHE.clear()
    bag2 = Bag(["Skyy_Talisman_Lantern_Common", "Skyy_Talisman_Speed_Uncommon"])
    Cfg.BRIDGE.put("acc:fn:bag", bag2)
    rx = str(Tr.respec(k, U, 4, "Skyy_Talisman_Speed_Uncommon", False, True))
    K.check("Your Void Charms changed - look again" in rx and not any(c[0] == "take" for c in bag2.calls) and T40.props(f).get("node.Class.echo") == "1",
            "F41 crit re-check: the job's ids (Speed) differ from what the bag would give now (Lantern, the lowest) = refused, nothing taken: %s" % rx)
    ok = str(Tr.respec(k, U, 4, "Skyy_Talisman_Lantern_Common", False, True))
    K.check(ok.startswith("+Respec done: 1 ranks reset, 4 VP back - the void took your Lantern (Normal)") and bag2.ids[0] is None
            and [c[0] for c in bag2.calls].index("take") > 0, "F41 crit re-check: the named charm is taken AFTER the save: %s" % ok)
    # ---------------------------------------------------------------- 3. fix round: "petecho" (pet XP follows the boosted skill XP - no Insight twice)
    K.eq(str(Tr.NLIVE[int(Tr.idx("Void.insight"))]), "on class XP and Mining, Foraging, Farming, Cooking, Alchemy and Smithing XP", "F41 Void Insight's text = 0.4.0's")
    Props = JClass("java.util.Properties")
    pp = Props()
    pp.setProperty("node.Void.insight", "3")
    pp.setProperty("node.Beast.echo", "2")
    pp.setProperty("vp", "40")
    be, al = float(Tr.echo(pp, int(Tr.I_BEAST))), float(Tr.allPct(pp))
    pe, px = float(Tr.stat(pp, 1, "petecho")), float(Tr.stat(pp, 1, "petxp"))
    K.check(be > 0 and al > 0 and abs(pe - be) < 1e-9 and abs(px - (al + be)) < 1e-9,
            "F41 petecho = Beastmastery Echo alone (%.3f), petxp unchanged = Insight + keep + Echo (%.3f)" % (pe, px))
    # ---------------------------------------------------------------- 4. fix round: Head Start vs the Nexus respec (tree:fn:headUsed)
    Cfg.RESPEC_CHARMS = 0
    Cfg.BRIDGE.remove("acc:fn:bag")
    ANS = {"v": None}
    ASK = []

    @JImplements("java.util.function.Function")
    class HeadUsed(object):
        @JOverride
        def apply(self, o):
            ASK.append(str(o))
            v = ANS["v"]
            return None if v is None else Int(v)
    HU = HeadUsed()
    HEADF = "n=2\nv=4\nvp=10\nvpSpent=4\nnode.Void.head=1\n"

    def respec_with(content, ans, fn=True, admin=False):
        open(f, "w").write(content)
        St.CACHE.clear()
        ANS["v"] = ans
        if fn:
            Cfg.BRIDGE.put("tree:fn:headUsed", HU)
        else:
            Cfg.BRIDGE.remove("tree:fn:headUsed")
        n0 = len(ASK)
        r_ = str(Tr.respec(k, U, -1 if admin else 4, None, admin, True))
        return r_, T40.props(f), len(ASK) - n0
    r1, d1, a1 = respec_with(HEADF, 2)
    K.check(r1 == "-A skill tree uses 2 Head Start points - respec it first (/tree), then the Nexus." and d1.get("node.Void.head") == "1" and d1.get("vp") == "10" and a1 == 1,
            "F41 Head Start 1 rank + a tree uses 2 Head Start points = refused, nothing saved: %s / %s" % (r1, d1))
    r2, d2, _a = respec_with(HEADF, None)
    K.check(r2.startswith("-Your skill trees are not loaded yet") and d2.get("node.Void.head") == "1", "F41 headUsed unknown (null) = refused, try again: %s" % r2)
    r3, d3, _a = respec_with(HEADF, 0)
    K.check(r3 == "+Respec done: 1 ranks reset, 4 VP back." and "node.Void.head" not in d3 and d3.get("vp") == "14", "F41 headUsed 0 = the respec goes on: %s / %s" % (r3, d3))
    r4, d4, a4 = respec_with(HEADF, 5, fn=False)
    K.check(r4.startswith("+Respec done") and "node.Void.head" not in d4, "F41 no SkyyTrees 0.4.2 (no tree:fn:headUsed) = allowed: %s" % r4)
    r5, d5, a5 = respec_with("n=2\nv=4\nvp=10\nvpSpent=4\nnode.Class.echo=1\n", 5)
    K.check(r5.startswith("+Respec done") and a5 == 0, "F41 no Head Start ranks = SkyyTrees not even asked: %s (asked %d)" % (r5, a5))
    r6, d6, a6 = respec_with(HEADF, 5, admin=True)
    K.check(r6.startswith("+Respec done") and a6 == 0, "F41 the admin refund is not asked: %s" % r6)
    Cfg.BRIDGE.remove("tree:fn:headUsed")
    K.save()


if __name__ == "__main__":
    assert os.path.isfile(B.JAVASSIST), B.JAVASSIST
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("vp", T40.run_vp), ("page", T40.run_page), ("f41", run_f41), ("live", T40.run_live)], script=__file__,
           live=(T40.LIVE_RB, "Skyy_SkyyRebirth"))
