"""Harness for SkyyAuctions 0.1.17 (no more "purse coins can be lost on death" texts - SkyyCoins 0.1.12 removed the coin death penalty;
tools/auctions_0_1_17_patch.py). Build first:
python tools/auctions_0_1_17_patch.py && python SkyyAuctions/build_skyyauctions_0.1.17.py

    python SkyyAuctions/test_skyyauctions_0.1.17.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--expect-dump]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py):
  A     verify   every class loads + initialises
  C     compare  the PINNED 0.1.16 jar -> 0.1.17: AhPage renderManage + handleDataEvent (the two Manage texts), AhCmds claim (the tip line
                 gone), AhCfg load / setPaused (the TEMPLATE constant, inlined), AhItem ttMap (the tools/tier_tags.py bake: 130 rows added
                 since the 0.1.16 build - augments etc. - none removed or changed; sort only) + the version texts - nothing else
  S     static   the patch re-runs to identical bytes, line endings kept; no "lost on death" / "deathpenalty" / "keeps them safe" string in
                 ANY class constant pool of the jar (0.1.16 had 4); the TEMPLATE's claimAllConfirmAbove comment; no new class / system / command
  CLAIM EXECUTED over the engine stand-ins (tools/hub_tab_harness.py + the SkyyBazaar 0.1.18 harness helpers, a fake SkyyCoins bridge, real
        inventories): a real sale (Create BIN through the page clicks, another player buys); claimAllConfirmAbove = 1; Manage -> Claim all ->
        the status line asks "Claim all <n> coins? Click Yes to confirm." (nothing paid yet); the armed Manage summary says "Claim <n> coins
        into your purse?"; Yes, claim all pays the coins. A second sale, then the /ah claim body (AhCmds.claim): the coins are paid, the
        claim message is sent, and NO tip line follows. Nothing sent to either player mentions death or /deathpenalty.
  X16   the 0.1.16 harness's exec phase (the price index) on this jar - unchanged behaviour
  HUB / RB   the 0.1.10 hub + 0.1.11 rebirth phases on this jar (through the 0.1.14 harness) - unchanged behaviour
  D     live     the 0.1.16 harness's live phase: a scratch COPY of the live Skyy_SkyyAuctions started TWICE - no file changes
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD_VERSION = "0.1.17", "0.1.16"
PKG = "com.skyy.auctions."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-%s.jar" % OLD_VERSION)
GEN = os.path.join(HERE, "build_skyyauctions_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyauctions_%s.py" % OLD_VERSION)
PATCH = os.path.join(ROOT, "tools", "auctions_0_1_17_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "fix1", "ah")))

_cmp0 = HK.run_compare
_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("ah0114test", os.path.join(HERE, "test_skyyauctions_0.1.14.py"))
T14 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T14)
_sp = importlib.util.spec_from_file_location("ah0116test", os.path.join(HERE, "test_skyyauctions_0.1.16.py"))
T16 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T16)
sys.argv[:] = _argv
HK.run_compare = _cmp0
T10, T11, TB, H = T14.T10, T14.T11, T14.TB, T14.H

EXPECT = {"AhPage": ["~m renderManage", "~m handleDataEvent"],          # the two Manage texts
          "AhCmds": ["~m claim", "~m status"],                           # the tip line gone + the version text
          "AhCfg": ["~m load", "~m setPaused"],                          # TEMPLATE (the claimAllConfirmAbove comment; a constant, inlined where read)
          "AhItem": ["~m ttMap"],            # the build-time tools/tier_tags.py bake: rows ADDED since the 0.1.16 build only (checked in S; sort only)
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyAuctionsPlugin": ["~m setup"]}   # the version texts
if "--expect-dump" in sys.argv:
    EXPECT = {}
BAD = ("lost on death", "deathpenalty", "keeps them safe", "coins waiting here are safe")


def cp_strings(b):
    """every CONSTANT_Utf8 of a class file (the strings the code can show)"""
    out, i = [], 10
    n = int.from_bytes(b[8:10], "big")
    k = 1
    while k < n:
        t = b[i]
        if t == 1:
            ln = int.from_bytes(b[i + 1:i + 3], "big")
            out.append(b[i + 3:i + 3 + ln].decode("utf-8", "replace"))
            i += 3 + ln
        elif t in (3, 4, 9, 10, 11, 12, 17, 18):
            i += 5
        elif t in (5, 6):
            i += 9
            k += 1
        elif t in (7, 8, 16, 19, 20):
            i += 3
        elif t == 15:
            i += 4
        else:
            raise ValueError("constant tag %d" % t)
        k += 1
    return out


def bad_strings(jar):
    z = zipfile.ZipFile(jar)
    hits = []
    for n in z.namelist():
        if n.endswith(".class"):
            for s in cp_strings(z.read(n)):
                if any(x in s.lower() for x in BAD):
                    hits.append("%s: %s" % (n.split("/")[-1], s[:120]))
    return hits


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyAuctions 0.1.17 - build script') and g.count('VERSION = "0.1.17"\n') + g.count('VERSION = "0.1.17"\r\n') == 1, "S header + VERSION")
    K.eq(tuple(g.count(x) - o.count(x) for x in ("registerSystem(", "registerCommand(", "makeClass(", "\nM(")), (0, 0, 0, 0), "S no new system / command / class / method")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    old_hits, new_hits = bad_strings(OLD_JAR), bad_strings(jar)
    K.check(len(old_hits) >= 4, "S 0.1.16 had the death texts (%d): %s" % (len(old_hits), old_hits))
    K.eq(new_hits, [], "S 0.1.17: no death-penalty string in any class constant pool")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S the same jar entries")
    cfg = [s for s in cp_strings(zb.read("com/skyy/auctions/AhCfg.class")) if "claimAllConfirmAbove = " in s]
    K.check(len(cfg) == 1 and "# claimAllConfirmAbove = Claim all asks first when this many coins or more are owed. 0 = never ask\n" in cfg[0],
            "S the TEMPLATE's claimAllConfirmAbove comment has no death text")
    ta, tb = tt_rows(OLD_JAR), tt_rows(jar)
    K.check(len(ta) > 500 and not (set(ta) - set(tb)) and not [k for k in ta if ta[k] != tb[k]],
            "S tier table: no row removed or changed since 0.1.16 (%d -> %d rows; %d added: %s ...)" % (len(ta), len(tb), len(set(tb) - set(ta)), sorted(set(tb) - set(ta))[:4]))
    import tier_tags as TT
    K.check(all(k in TT.ROWS for k in set(tb) - set(ta)), "S every added row is in tools/tier_tags.py ROWS")
    K.save()


def tt_rows(jar):
    """AhItem's baked tier table (the id:tier|... constant) as a dict"""
    d = {}
    for s in cp_strings(zipfile.ZipFile(jar).read("com/skyy/auctions/AhItem.class")):
        if s.count("|") > 50:
            for kv in s.split("|"):
                if ":" in kv:
                    k, v = kv.rsplit(":", 1)
                    d[k] = v
    return d


def run_claim(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    W = H.boot(scratch, jar, "claim")
    E = W.E
    J = lambda n: JClass(PKG + n)
    HB = J("HubBar")
    E.br = HB.map()
    home = os.path.join(scratch, "home_claim", "Skyy_SkyyAuctions")
    T10.prep(E, J, home)
    TB.fake_items(E, ["Ore_Iron", "Ore_Copper"])
    purse = {}
    TB.fake_coins(E.br, purse)
    P, O = W.P, W.O
    u, uo = P.pr.getUuid(), O.pr.getUuid()
    purse[str(u)] = 1000000
    purse[str(uo)] = 1000000
    for X in (P, O):
        E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    J("AhHubOpen").register()
    Cfg, Sto = J("AhCfg"), J("AhStore")
    Cfg.GRACE_MS = 0
    Cfg.CLAIMALL_ABOVE = 1
    n_p0, n_o0 = len(E.sent(P)), len(E.sent(O))

    def sell(item, price):
        TB.give(P, item, 10, slot=0)
        HB.open(P.pr, u, "market", "auctions")
        E.pump(P)
        TB.click(E, P, '{"a":"nav:create"}')
        p2, cm, ev, apps = TB.built(K, E, P, "CREATE %s" % item)
        idx = [i for i in range(len(list(p2.cellSec))) if int(p2.cellSec[i]) == 0 and int(p2.cellSlot[i]) == 0]
        TB.click(E, P, '{"a":"pick:%d","@AhPrice":""}' % idx[0])
        TB.click(E, P, '{"a":"preview","@AhPrice":"%d"}' % price)
        before = set(str(k) for k in Sto.LIVE.keySet())
        p2, ok = TB.click(E, P, '{"a":"create","@AhPrice":"%d"}' % price)
        new = [str(k) for k in Sto.LIVE.keySet() if str(k) not in before]
        K.check(len(new) == 1 and int(E.count(P, item)) == 0, "SELL %s listed for %d (%s)" % (item, price, p2.status))
        lid = new[0]
        pgo = J("AhPage")(O.pr, "browse")
        O.pm.openCustomPage(O.ref, O.st, pgo)
        E.pump(O)
        po, cmo, evo, appso = TB.built(K, E, O, "BUYER Browse")
        ri = [i for i in range(len(list(po.rowIds))) if str(po.rowIds[i]) == lid]
        po, ok = TB.click(E, O, '{"a":"view:%d","@AhSearch":""}' % ri[0])
        b0 = purse[str(uo)]
        po, ok = TB.click(E, O, '{"a":"buy"}')
        if po.armAct is not None:
            po, ok = TB.click(E, O, '{"a":"confirm"}')
        K.check(purse[str(uo)] == b0 - price and str(J("AhRec").state(Sto.get(lid))) == "SOLD", "SELL the buyer paid %d, the listing is SOLD" % price)
        return lid
    # ---------------------------------------------------------------- Manage: Claim all (confirm at >= 1 coin)
    sell("Ore_Iron", 500)
    HB.open(P.pr, u, "market", "auctions")
    E.pump(P)
    p2, ok = TB.click(E, P, '{"a":"nav:manage"}')
    TB.built(K, E, P, "MANAGE (coins owed)")
    owed = int(Sto.owedFor(p2.key)[1])
    K.check(owed > 0, "CLAIM coins are owed in Manage: %d" % owed)
    s0 = purse[str(u)]
    p2, ok = TB.click(E, P, '{"a":"claimall"}')
    st = str(p2.status)
    fmt = str(J("AhUtil").fmt(owed))
    K.eq(st, "Claim all %s coins? Click Yes to confirm." % fmt, "CLAIM Claim all at / above claimAllConfirmAbove: the status line")
    K.eq(purse[str(u)], s0, "CLAIM nothing paid before Yes")
    p2, cm, ev, apps = TB.built(K, E, P, "MANAGE (Claim all armed)")
    K.eq(str(TB.set_of(cm, "#SkyyAhMSumTxt.Text")), "Claim %s coins into your purse?" % fmt, "CLAIM the armed summary line")
    K.check(any(s == "#SkyyAhMClaimAll" for s, t in ev), "CLAIM the Yes, claim all button is bound")
    p2, ok = TB.click(E, P, '{"a":"claimyes"}')
    K.check(purse[str(u)] - s0 == owed, "CLAIM Yes, claim all paid the %d coins (%s)" % (purse[str(u)] - s0, p2.status))
    # ---------------------------------------------------------------- /ah claim (the AhCmds.claim body)
    sell("Ore_Copper", 700)
    k = str(J("AhUtil").pkey(u))
    owed2 = int(Sto.owedFor(k)[1])
    s1 = purse[str(u)]
    n0 = len(E.sent(P))
    J("AhCmds").claim(P.pr, P.ref, P.st)
    txt = str(E.strs_of(P, n0))
    K.check(purse[str(u)] - s1 == owed2 and owed2 > 0, "CMD /ah claim paid the %d coins" % (purse[str(u)] - s1))
    K.check(len(txt) > 0 and "Tip:" not in txt, "CMD the claim message is sent and no Tip line follows: %r" % txt[:300])
    allp, allo = str(E.strs_of(P, n_p0)).lower(), str(E.strs_of(O, n_o0)).lower()
    K.check(not any(x in allp or x in allo for x in BAD) and "death" not in allp and "death" not in allo,
            "NONE nothing sent to the seller or the buyer mentions death / /deathpenalty")
    K.notes.append("CMD /ah claim said: %r" % txt[:200])
    K.save()
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    ph = [("static", run_static), ("claim", run_claim), ("exec16", T16.run_exec), ("hub", T10.run_hub), ("rb", T11.run_rb),
          ("live", T16.run_live)]
    HK.run(name="SkyyAuctions", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=ph, script=__file__, live=(T16.LIVE_DIR, "Skyy_SkyyAuctions"))
