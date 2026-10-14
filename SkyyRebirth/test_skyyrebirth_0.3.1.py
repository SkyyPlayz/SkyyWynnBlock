"""SkyyRebirth 0.3.1 - harness for the econ38 round (tools/rebirth_0_3_1_patch.py): /rebirthadmin crashtest / points / refund as sub-commands
(the engine parser accepts them now) + the Farming arm fed by Farming + Ranching + Orchard.
Build first: python tools/rebirth_0_3_1_patch.py && python SkyyRebirth/build_skyyrebirth_0.3.1.py

    python SkyyRebirth/test_skyyrebirth_0.3.1.py --dir <empty folder inside tools/dev/scratch/> [--keep]

The 0.3 harness (test_skyyrebirth_0.3.py) is reused with the round's jars: its World loads THIS jar + SkyySkills 0.4.38 + SkyyCoins 0.1.8
+ SkyyBank 0.1.11 (the round's pins) and its markets a real SkyyAuctions 0.1.6.
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.3 -> 0.3.1: exactly the planned members differ; RbAdminCrashCmd / RbAdminPointsCmd / RbAdminRefundCmd added
  N   new      EXECUTED:
               PARSER - the REAL RbAdminCmd of this jar, registered the engine's way (setOwner + completeRegistration), through the
               ENGINE's own parser (Tokenizer, ParserContext, AbstractCommand.acceptCall): /rebirthadmin crashtest 3, points Farming 5,
               points all reset, refund Mining, status, dryrun, rebirth, recover, backups, help and the bare /rebirthadmin all parse and
               reach the player command (the player-only answer); crashtest x (not a number) / crashtest 3 4 / refund are refused; the
               CONTROL: 0.3's jar refuses crashtest 3 (wrong number of parameters = the bug); each sub-command hands RbAdmin.run the
               same line (static) and needs skyyrebirth.admin (a sender without it is refused by the engine)
               FARMING ARM - RbMath.armAdd (sums, saturation, null pools); the /rebirth preview (RbCheck.gains) with the REAL SkyySkills
               0.4.38: Farming full + Ranching / Orchard 0 = 4 points (1/3 of the pools), all three full = 8, an old SkyySkills that
               answers Farming only = 8 (0.3's number); THE DECISION through a full admin rebirth: pts.Farming = the 3-pool number with
               SkyySkills 0.4.38's facts (arm.ranching / arm.orchard present), = Farming alone when the facts lack them (a rebirth
               prepared by 0.4.37 - a participant wrapper strips them); the other arms' points unchanged
  X / KK / D   test_skyyrebirth_0.3.py's exec, kill, killcheck and live (start twice on scratch copies of the live data) phases on this jar
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.3.1"
RB = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.3.jar")
SK_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.38.jar")
CO_JAR = os.path.join(ROOT, "SkyyCoins", "SkyyCoins-0.1.8.jar")
AH_JAR = os.path.join(ROOT, "SkyyAuctions", "SkyyAuctions-0.1.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "econ38", "rb")))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T3 = _load("t_rb03", os.path.join(HERE, "test_skyyrebirth_0.3.py"))
T2 = T3.T2
T3.VERSION = VERSION          # its config / generated-script checks read this version's
T3.JAR = T2.JAR = JAR
T2.SK_JAR, T2.CO_JAR = SK_JAR, CO_JAR
T3.AH_JAR = AH_JAR
LIVE_DIR = T3.LIVE_DIR

EXPECT = {
    "RbMath": ["+f FARM_ARM", "+f FARM_POOLS", "+m armAdd", "+m satAdd", "~<clinit>"],
    "RbCheck": ["+m runArr", "+m runFarm", "~m gains"],
    "RbTx": ["~m decide"],
    "RbAdminCmd": ["~c "],                                   # + the three addSubCommand calls
    "SkyyRebirthPlugin": ["~m setup"],                       # the ready line (version + the Farming arm text)
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],      # the kit's version text
    "RbStore": ["~m writeNow"],                              # the file comment's version
}
ADDED = ["RbAdminCrashCmd", "RbAdminPointsCmd", "RbAdminRefundCmd"]


def run_new(out, jar, scratch, _home):
    from jpype import JClass, JArray, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    URL, File = JClass("java.net.URL"), JClass("java.io.File")

    def loader(jars):
        return JClass("java.net.URLClassLoader")(JArray(URL)([File(j).toURI().toURL() for j in jars]),
                                                 JClass("java.lang.ClassLoader").getSystemClassLoader())
    # ================================================================ PARSER
    PM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
    HS = JClass("java.util.HashSet")
    Tok = JClass("com.hypixel.hytale.server.core.command.system.Tokenizer")
    PCx = JClass("com.hypixel.hytale.server.core.command.system.ParserContext")
    PRs = JClass("com.hypixel.hytale.server.core.command.system.ParseResult")
    MSGS = []

    def sender(nodes):
        ns = HS()
        for n_ in nodes:
            ns.add(n_)

        @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
        class Snd(object):
            @JOverride
            def getUsername(self):
                return "Tester"

            @JOverride
            def getUuid(self):
                return JClass("java.util.UUID")(1, 2)

            @JOverride
            def sendMessage(self, m):
                MSGS.append(str(m.getMessageId() or m.getRawText()))

            @JOverride
            def hasPermission(self, q, *rest):
                if isinstance(q, str) or str(q.getClass().getName()) == "java.lang.String":
                    r = PM.hasPermission(ns, str(q))
                else:
                    r = PM.hasPermission(ns, q)
                return bool(r) if r is not None else False
        return Snd()

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandOwner")
    class Owner(object):
        @JOverride
        def getName(self):
            return "SkyyHarness"
    owner = Owner()

    def root_of(j):
        L = loader([j])
        c = JClass(RB + "RbAdminCmd", loader=L)()
        c.setOwner(owner)
        try:
            c.completeRegistration()
        except Exception as e:
            K.notes.append("completeRegistration: %s" % str(e)[:100])
        return c, L

    def parse(root, line, snd):
        del MSGS[:]
        res = PRs()
        toks = Tok.parseArguments(line, res)
        if res.failed():
            return False, ["tokenizer"]
        ctx = PCx.of(toks, line, res)
        try:
            root.acceptCall(snd, ctx, res)
        except Exception as e:
            MSGS.append("EXC " + str(e)[:300])
        if res.failed():
            res.sendMessages(snd)
            return False, list(MSGS)
        return True, list(MSGS)
    admin, nobody = sender(["skyyrebirth.admin"]), sender([])
    new_root, _Ln = root_of(jar)
    old_root, _Lo = root_of(OLD_JAR)
    subs = sorted(str(x) for x in new_root.getSubCommands().keySet())
    K.check(subs == ["crashtest", "points", "refund"], "N parser: /rebirthadmin has the sub-commands crashtest / points / refund: %s" % subs)
    for line in ("rebirthadmin crashtest 3", "rebirthadmin crashtest 0", "rebirthadmin crashtest 7", "rebirthadmin points Farming 5",
                 "rebirthadmin points all reset", "rebirthadmin refund Mining", "rebirthadmin refund all", "rebirthadmin status",
                 "rebirthadmin dryrun", "rebirthadmin rebirth", "rebirthadmin recover", "rebirthadmin backups", "rebirthadmin help", "rebirthadmin"):
        ok, msgs = parse(new_root, line, admin)
        K.check(ok and "server.commands.errors.playerOrArg" in msgs, "N parser: /%s parses and reaches the player command (%s)" % (line, msgs[:2]))
    for line in ("rebirthadmin crashtest x", "rebirthadmin crashtest 3 4", "rebirthadmin refund", "rebirthadmin points Farming"):
        ok, msgs = parse(new_root, line, admin)
        K.check(not ok, "N parser: /%s is refused by the engine (%s)" % (line, msgs[:1]))
    ok, msgs = parse(old_root, "rebirthadmin crashtest 3", admin)
    K.check(not ok and any("wrongNumber" in x for x in msgs), "N parser CONTROL: 0.3 refuses /rebirthadmin crashtest 3 (the bug): %s" % msgs[:1])
    ok, msgs = parse(old_root, "rebirthadmin points Farming 5", admin)
    K.check(not ok, "N parser CONTROL: 0.3 refuses /rebirthadmin points Farming 5 too: %s" % msgs[:1])
    for line in ("rebirthadmin crashtest 3", "rebirthadmin refund all", "rebirthadmin status"):
        ok, msgs = parse(new_root, line, nobody)
        K.check(not ok or "server.commands.errors.playerOrArg" not in msgs, "N parser: /%s without skyyrebirth.admin is refused (%s)" % (line, msgs[:1]))
    g = PW.calls(jar)
    for cls, word in (("RbAdminCrashCmd", '"crashtest "'), ("RbAdminPointsCmd", '"points "'), ("RbAdminRefundCmd", '"refund "')):
        K.check(RB + "RbAdmin.run" in g.get(cls + ".execute", set()) and RB + "RbAdmin.send" in g.get(cls + ".execute", set()),
                "N static: %s.execute hands RbAdmin.run the line and sends its answer" % cls)
    gen = open(os.path.join(HERE, "build_skyyrebirth_%s.py" % VERSION), encoding="utf8").read()
    K.check(gen.count('requirePermission("skyyrebirth.admin");') >= 5 and '"crashtest " + String.valueOf(ctx.get(this.pointArg))' in gen
            and '"points " + String.valueOf(ctx.get(this.armArg)) + " " + String.valueOf(ctx.get(this.nArg))' in gen
            and '"refund " + String.valueOf(ctx.get(this.armArg))' in gen, "N static: each sub-command needs skyyrebirth.admin and builds 0.3's line")

    # ================================================================ FARMING ARM
    W0 = T2.World(os.path.join(scratch, "fw0"))
    M = W0.Mth
    from jpype import JLong
    LongA = JArray(JLong)
    a = M.armAdd(LongA([10, 100, 3, 100]), LongA([5, 100, 1, 100]))
    K.check(list(a) == [15, 200, 3, 100], "N armAdd: run + run, toCap + toCap, Farming's level / cap kept: %s" % list(a))
    K.check(list(M.armAdd(LongA([10, 100, 3, 100]), None)) == [10, 100, 3, 100] and list(M.armAdd(None, LongA([1, 2, 3, 4]))) == [1, 2, 3, 4]
            and M.armAdd(None, None) is None, "N armAdd: a missing pool counts nothing")
    big = (1 << 63) - 10
    K.check(list(M.armAdd(LongA([big, big, 0, 0]), LongA([100, 100, 0, 0])))[:2] == [(1 << 63) - 1, (1 << 63) - 1]
            and list(M.armAdd(LongA([-5, 10, 0, 0]), LongA([3, -1, 0, 0])))[:2] == [3, 10], "N armAdd: saturates at Long.MAX_VALUE, negatives count 0")
    D = W0.SDefs
    sl = dict((nm, int(D.indexOf(nm))) for nm in ("Farming", "Ranching", "Orchard"))
    K.check(all(v >= 16 or nm == "Farming" for nm, v in sl.items()) and len(set(sl.values())) == 3, "N SkyySkills 0.4.38 has the 3 farming slots: %s" % sl)
    tc = dict((nm, int(D.cumAt(s, int(D.maxOf(s))))) for nm, s in sl.items())
    k = T2.U0
    CK = T2.Checker(K, W0)

    def world(name, farm):
        base = os.path.join(scratch, name)
        T2.seed(base, k, CK.cls_total, extra_skills=farm)
        W = T2.World(base)
        W.br.put("class:" + k, "Archer")
        return W, base
    cases = [("f_only", {"Farming": tc["Farming"]}, T2.pts(tc["Farming"], tc["Farming"] + tc["Ranching"] + tc["Orchard"], 8)),
             ("all3", {"Farming": tc["Farming"], "Ranching": tc["Ranching"], "Orchard": tc["Orchard"]}, 8),
             ("half", {"Farming": tc["Farming"] // 2, "Ranching": tc["Ranching"] // 2, "Orchard": tc["Orchard"] // 2},
              T2.pts(tc["Farming"] // 2 + tc["Ranching"] // 2 + tc["Orchard"] // 2, tc["Farming"] + tc["Ranching"] + tc["Orchard"], 8))]
    K.check(cases[0][2] == 4, "N the expected 3-pool number for Farming full + 0 + 0 = floor(8 x sqrt(1/3)) = 4: %d" % cases[0][2])
    others = None
    for name, farm, want in cases:
        W, base = world("farm_" + name, farm)
        u = W.uuid(k)
        g_ = W.Chk.gains(u, 0)
        line = str(g_[0][5])
        K.check(line.startswith("Farming  +%d point" % want), "N preview %s: %s (want +%d)" % (name, line, want))
        r = str(W.Tx.adminStart(u, -1))
        rp = T2.props(W.files(k)["rebirth"])
        K.check(r.startswith("+Rebirth tx") and rp is not None and int(rp.get("pts.Farming", "0")) == want,
                "N decision %s: pts.Farming = %d (the 3 pools from arm.farming + arm.ranching + arm.orchard): %s" % (name, want, rp and rp.get("pts.Farming")))
        oth = dict((a_, b_) for a_, b_ in rp.items() if a_.startswith("pts.") and a_ != "pts.Farming")
        if others is None:
            others = oth
        K.check(oth == others and oth == dict(("pts." + a_, str(p_)) for a_, p_ in CK.points.items() if p_ > 0 and a_ != "Farming"),
                "N decision %s: the other arms' points unchanged (the spec curve): %s" % (name, oth))
    # an older SkyySkills (Farming only on skill:fn:run) = 0.3's number; facts without arm.ranching / arm.orchard = Farming alone
    W, base = world("farm_old", {"Farming": tc["Farming"]})
    u = W.uuid(k)
    real_run, real_part = W.br.get("skill:fn:run"), W.br.get("rebirth:part:skills")

    def only_farming(o):
        if str(o[1]).lower() in ("ranching", "orchard"):
            return None
        return real_run.apply(o)

    def strip(o):
        r_ = real_part.apply(o)
        s_ = str(r_)
        if s_.startswith("ok:"):
            s_ = "ok:" + ";".join(x for x in s_[3:].split(";") if not x.startswith(("arm.ranching=", "arm.orchard=")))
        return s_
    W.br.put("skill:fn:run", W.Fn(only_farming))
    line = str(W.Chk.gains(u, 0)[0][5])
    K.check(line.startswith("Farming  +8 point"), "N preview with an older SkyySkills (Farming only): %s = 0.3's 8" % line)
    W.br.put("skill:fn:run", real_run)
    W.br.put("rebirth:part:skills", W.Fn(strip))
    m_ = str(real_part.apply(JArray(JClass("java.lang.Object"))(["measure", k, "tx1760000000001-a1b2c3", JClass("java.lang.Integer")(1), ""])))
    K.check("arm.ranching=" in m_ and "arm.orchard=" in m_ and "arm.farming=" in m_, "N SkyySkills 0.4.38 measure has arm.farming / arm.ranching / arm.orchard: %s" % m_[:200])
    r = str(W.Tx.adminStart(u, -1))
    rp = T2.props(W.files(k)["rebirth"])
    K.check(r.startswith("+Rebirth tx") and rp is not None and int(rp.get("pts.Farming", "0")) == 8,
            "N decision from facts WITHOUT arm.ranching / arm.orchard (a rebirth prepared by 0.4.37) = Farming alone = 8: %s" % (rp and rp.get("pts.Farming")))
    K.save()


def run_exec(out, jar, scratch, home):
    return T3.run_exec(out, jar, scratch, home)


def run_kill(out, jar, scratch, home):
    return T3.run_kill(out, jar, scratch, home)


def run_killcheck(out, jar, scratch, home):
    return T3.run_killcheck(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    return T3.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    for j_ in (SK_JAR, CO_JAR, T2.BK_JAR, T2.PF_JAR, AH_JAR, T3.BZ_JAR, OLD_JAR):
        assert os.path.isfile(j_), j_
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("new", run_new), ("exec", run_exec), ("kill", run_kill), ("killcheck", run_killcheck), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
