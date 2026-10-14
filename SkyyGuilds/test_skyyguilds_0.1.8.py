"""Harness for SkyyGuilds 0.1.8 (same-account guild bank fences; tools/guilds_0_1_8_patch.py).
Build first: python tools/guilds_0_1_8_patch.py && python SkyyGuilds/build_skyyguilds_0.1.8.py

    python SkyyGuilds/test_skyyguilds_0.1.8.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the fake Universe + G / World of test_skyyguilds_0.1.7.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.7 -> 0.1.8: exactly the listed members differ, no class added
  X  exec     DIFF  1,500 random steps (create / invite / accept / deposit / withdraw / limits / leave with refunds / kick / disband /
                    ticks ...) on 0.1.7 and 0.1.8 side by side, TWICE: (1) no SkyyProfiles (profile key = the uuid), (2) every player on a
                    fixed profile <uuid>-p2 with the REAL SkyyCoins 0.1.8 coins:fn:sameacct on the bridge (switch ON): identical results,
                    states, purses and guild files (the new pnet.* lines aside, which must add up to each player's net); coins conserved
                    SAME  the REAL coins:fn:sameacct, per-profile purses (a stand-in SkyyCoins that pays the ACTIVE profile of profile:fn:key):
                    deposit on profile 1 -> withdraw on profile 2 refused (all fenced), nothing moved (bank, purses, file); with another
                    player's coins in the bank: "at most" the free part, "all" = the free part; the switch OFF = allowed (0.1.7);
                    coins:fn:sameacct missing = blocked; back on profile 1 the coins come out; a deposit + withdraw on the same profile 2
                    unaffected; a leave from profile 2 = no refund of profile 1's coins (the note says so; the contribution kept, not
                    forfeited); a leave from profile 1 = the 35 % refund to profile 1's purse; a kick of a member who is on profile 2 =
                    no refund of profile 1's coins; DISBAND / the last member's leave on profile 2 = refused, nothing changed; on profile
                    1 = paid to profile 1; an ADMIN delete is not fenced; a refused add rolls the ledger back with the bank; the ledger
                    survives a restart (new loader, the file) and 0.1.7 reads + rewrites a 0.1.8 file (pnet dropped, bank intact)
  D  live     start twice on a scratch COPY of the live Skyy_SkyyGuilds with 0.1.7 and 0.1.8: the same guilds, banks, members and published
              values; 0.1.8 changes exactly the files 0.1.7 changes (test_skyyguilds_0.1.7.py run_live)
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, random, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.8"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGuilds-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGuilds-0.1.7.jar")
COINS_JAR = os.path.join(ROOT, "SkyyCoins", "SkyyCoins-0.1.8.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "econ39", "guilds")))
PKG = "com.skyy.guilds."


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T7 = _load("t_g017", os.path.join(HERE, "test_skyyguilds_0.1.7.py"))
T7.OLD_JAR = OLD_JAR          # its run_live compares OLD_JAR with the jar given = 0.1.7 vs 0.1.8
NAMES = T7.NAMES
LIVE_DIR = T7.LIVE_DIR
EXPECT = {
    "Guild": ["+f pnet", "~c "],
    "GuildStore": ["+f FENCED", "~<clinit>", "+m pnetAdd", "+m pnetDrop", "+m sameBlocked", "+m fenced", "+m profName", "+m fenceWho",
                   "+m keyOfMember", "+m fenceNote", "+m pnetWd", "+m switching", "+m keyMoved", "~m propsOf", "~m loadGuildFile",
                   "+m depositEnd", "-m depositEnd", "~m deposit",                       # depositEnd(..., String pk): a new signature
                   "+m withdrawBegin", "-m withdrawBegin", "~m withdrawEnd", "~m withdraw",   # withdrawBegin(..., String pk)
                   "~m refundInfo", "~m leaveNote", "~m payRefund", "~m kick", "~m removeMember", "~m leave",
                   "+m disbandNow", "~m disbandNow", "~m adminDelete"],                  # disbandNow(..., boolean fence) + the old form
    "SkyyGuildsPlugin": ["~m setup"],
    "CfgRows": ["~m header", "~<clinit>"], "GCfg": ["~m load"], "CfgFn": ["~m opExport"],
}
ADDED = []


def files_nop(g):
    """the guild files without the 0.1.8 pnet.* lines"""
    return dict((k, [l for l in v if not l.startswith("pnet.")]) for k, v in g.files().items())


def pnet_sums_ok(g):
    """fix F3: the ledger in every guild file (no pre-0.1.8 coins in these tests; a player without pnet lines is not checked - dropped
    when they left with nothing): each pnet line has 0 <= withdrawn <= deposited (never negative), a player's pnet DEPOSITS are at most
    the deposits of their net.<uuid> line (lines dropped at a leave with nothing left / untracked coins), and what their profiles still have (deposited - withdrawn) is at least their net value
    (withdrawals of other players' coins are not booked, so the ledger can only be MORE careful than the net)"""
    bad = []
    for f, lines in g.files().items():
        net, pd, po = {}, {}, {}
        for l in lines:
            if l.startswith("net.") and "~guild" not in l:
                k, v = l[4:].split("=", 1)
                d, w = (int(x) for x in v.split("|"))
                net[k] = (d, d - w)
            elif l.startswith("pnet."):
                k, v = l[5:].split("=", 1)
                d, w = (int(x) for x in v.split("|"))
                if not (0 <= w <= d):
                    bad.append((f, k, "negative", d, w))
                pd[k[:36]] = pd.get(k[:36], 0) + d
                po[k[:36]] = po.get(k[:36], 0) + d - w
        for u in pd:
            nd, nv = net.get(u, (0, 0))
            if pd[u] > nd or po[u] < nv:
                bad.append((f, u, pd[u], po[u], nd, nv))
    return bad


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    W = T7.World(scratch)
    U = W.uid
    BR = W.BR
    CL = T7.loader_for(COINS_JAR)
    CoinFn, Xfer = JClass("com.skyy.coins.CoinFn", loader=CL), JClass("com.skyy.coins.CoinXfer", loader=CL)
    SAME = CoinFn("sameacct")
    PROF = {}
    # fix F2 race hooks: SWK = a profile switch that lands on a later profile:fn:key read of player "uid" (after "skip" more reads; with
    # "armOnGet" it is armed by that player's next coins:fn:get); SWT["after"] = a switch right after a coins:fn:take
    SWK = {"uid": None, "skip": 0, "to": None, "armOnGet": False, "armed": False}
    SWT = {"after": None}

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, u):
            us = str(u)
            if SWK["uid"] == us and SWK["armed"]:
                if SWK["skip"] > 0:
                    SWK["skip"] -= 1
                else:
                    PROF[us] = SWK["to"]
                    SWK["uid"] = None
            return PROF.get(us, us)
    KEYFN = KeyFn()

    def flip_on_key(uid, to, skip, arm_on_get=False):
        SWK.update({"uid": uid, "skip": skip, "to": to, "armOnGet": arm_on_get, "armed": not arm_on_get})

    # ================================================================ DIFF x2
    def diff(label, profiles, steps=1500, seed=818):
        BR.clear()
        W.coins_on()
        PROF.clear()
        if profiles:
            for i in NAMES:
                PROF[str(U(i))] = str(U(i)) + "-p2"
            BR.put("profile:fn:key", KEYFN)
            BR.put("coins:fn:sameacct", SAME)
            Xfer.BLOCK_SAME = True
        for k in ("old", "new"):
            W.PURSES[k].clear()
            for i in NAMES:
                W.PURSES[k][str(U(i))] = 50000
        o = T7.G(W, OLD_JAR, os.path.join(scratch, label + "7"), "old")
        n = T7.G(W, jar, os.path.join(scratch, label + "8"), "new")
        o.start()
        n.start()
        W.online(list(NAMES))
        rnd = random.Random(seed)
        diffs, okops = 0, {}
        OPS = ["create", "invite", "accept", "deposit", "deposit", "withdraw", "withdraw", "limit", "promote", "demote", "transfer", "leave",
               "leave2", "kick", "disband", "tick", "flush", "join", "join", "join", "deposit", "kick", "leave2"]

        def members_of():
            out_ = {}
            for gid, v in n.state().items():
                out_[gid] = dict((nn, v[6][str(U(nn))][0]) for nn in NAMES if str(U(nn)) in v[6])
            return out_
        for step in range(steps):
            op = rnd.choice(OPS)
            a, b = rnd.choice(list(NAMES)), rnd.choice(list(NAMES))
            amt = rnd.choice(["500", "2k", "all", "1", "100000", "abc", "half", "0", "300", "1k"])
            mo = members_of()
            free = [x for x in NAMES if not any(x in m for m in mo.values())]
            if mo and rnd.random() < 0.7:
                gm = mo[rnd.choice(sorted(mo))]
                lead = [x for x, r in gm.items() if r == 2]
                low = [x for x, r in gm.items() if r < 2]
                if op in ("deposit", "withdraw", "leave", "leave2"):
                    a = rnd.choice(sorted(gm))
                elif op in ("kick", "promote", "demote", "transfer", "limit", "disband", "invite") and lead:
                    a = lead[0]
                    if low:
                        b = rnd.choice(low)
                    elif free:
                        b = rnd.choice(free)
                elif op == "join" and lead and free:
                    a, b = lead[0], rnd.choice(free)
            if op == "join":
                o.call("invite", U(a), NAMES[a], NAMES[b])
                n.call("invite", U(a), NAMES[a], NAMES[b])
                op, a = "accept", b
            args = None
            if op == "create":
                args = ("create", U(a), NAMES[a], "Guild%d" % rnd.randint(1, 4))
            elif op == "invite":
                args = ("invite", U(a), NAMES[a], NAMES[b])
            elif op == "accept":
                args = ("accept", U(a), NAMES[a])
            elif op in ("deposit", "withdraw"):
                args = (op, U(a), NAMES[a], amt)
            elif op == "limit":
                args = ("setLimit", U(a), NAMES[a], rnd.choice(["admin", "member"]), rnd.choice(["none", "0", "1k", "5000"]))
            elif op in ("promote", "demote", "kick"):
                args = (op, U(a), NAMES[a], NAMES[b])
            elif op == "transfer":
                args = ("transfer", U(a), NAMES[a], NAMES[b], True)
            elif op in ("leave", "leave2"):
                args = ("leave", U(a), NAMES[a], op == "leave")
            elif op == "disband":
                args = ("disband", U(a), NAMES[a], True)
            elif op == "tick":
                W.CUR[0] = "old"
                o.Tick().run()
                W.CUR[0] = "new"
                n.Tick().run()
                r_o = r_n = None
            else:
                o.GS.flushDirty()
                n.GS.flushDirty()
                r_o = r_n = None
            if args is not None:
                r_o, r_n = o.call(*args), n.call(*args)
            if isinstance(r_n, str) and r_n.startswith("+"):
                okops[op] = okops.get(op, 0) + 1
                if "got back" in r_n:
                    okops["refund"] = okops.get("refund", 0) + 1
            if r_o != r_n:
                diffs += 1
                if diffs <= 4:
                    K.check(False, "X DIFF(%s) step %d %s: 0.1.7 %r vs 0.1.8 %r" % (label, step, (args or (op,))[0], r_o, r_n))
            if o.state() != n.state() or W.PURSES["old"] != W.PURSES["new"]:
                diffs += 1
                if diffs <= 4:
                    K.check(False, "X DIFF(%s) step %d %s: the guild state / purses differ" % (label, step, op))
            tot = sum(W.PURSES["new"].values()) + sum(v[3] for v in n.state().values())
            if tot != 50000 * len(NAMES):
                diffs += 1
                if diffs <= 4:
                    K.check(False, "X DIFF(%s) step %d: coins not conserved (%d)" % (label, step, tot))
            if step % 50 == 49:
                o.GS.flushDirty()
                n.GS.flushDirty()
                fo, fn_ = o.files(), files_nop(n)
                bad = pnet_sums_ok(n)
                if fo != fn_ or bad:
                    diffs += 1
                    if diffs <= 4:
                        K.check(False, "X DIFF(%s) step %d: guild files differ / pnet does not add up %s" % (label, step, bad[:2]))
        K.eq(diffs, 0, "X DIFF(%s): %d random steps identical on 0.1.7 and 0.1.8 (results, state, purses, files without pnet.*), the ledger never negative + its deposits = net deposits (fix F3), coins conserved" % (label, steps))
        K.check(all(okops.get(x, 0) >= 3 for x in ("create", "accept", "deposit", "withdraw", "leave", "kick", "disband")) and okops.get("refund", 0) >= 1,
                "X DIFF(%s) covered every money path: %s" % (label, okops))
        any_p = any(l.startswith("pnet." + ("" if not profiles else "")) for v in n.files().values() for l in v)
        K.check(any_p and all(("-p2=" in l) == bool(profiles) for v in n.files().values() for l in v if l.startswith("pnet.")),
                "X DIFF(%s): pnet lines written with the active profile key (%s)" % (label, "<uuid>-p2" if profiles else "<uuid>"))
        o.GS.stopIO()
        n.GS.stopIO()
    diff("solo", False)
    diff("p2", True)

    # ================================================================ SAME: per-profile purses + the real coins:fn:sameacct
    BR.clear()
    PROF.clear()
    PP = {}
    FAIL = {"add": False, "addk": set(), "takek": set()}

    def key(u):
        return PROF.get(str(u), str(u))

    @JImplements("java.util.function.Function")
    class PGet:
        @JOverride
        def apply(self, u):
            if SWK["uid"] == str(u) and SWK["armOnGet"]:
                SWK["armed"] = True
            return W.Long.valueOf(PP.get(key(u), 0))

    @JImplements("java.util.function.Function")
    class PAdd:
        @JOverride
        def apply(self, a):
            k = key(a[0])
            if FAIL["add"] or k in FAIL["addk"]:
                return None
            PP[k] = PP.get(k, 0) + int(a[1])
            return W.Long.valueOf(PP[k])

    @JImplements("java.util.function.Function")
    class PTake:
        @JOverride
        def apply(self, a):
            k = key(a[0])
            if k in FAIL["takek"]:
                return None
            if PP.get(k, 0) < int(a[1]):
                return W.Boolean.FALSE
            PP[k] = PP.get(k, 0) - int(a[1])
            if SWT["after"] is not None:
                PROF[str(a[0])] = SWT["after"]          # fix F2: the switch lands right after the take
            return W.Boolean.TRUE

    def coins_up():
        BR.put("coins:fn:get", PGet())
        BR.put("coins:fn:add", PAdd())
        BR.put("coins:fn:take", PTake())
        BR.put("profile:fn:key", KEYFN)
        BR.put("coins:fn:sameacct", SAME)
    coins_up()
    Xfer.BLOCK_SAME = True
    d8 = os.path.join(scratch, "same8")
    n = T7.G(W, jar, d8, "new")
    n.start()
    GS = n.GS
    W.online(list(NAMES))
    s1, a1 = str(U(1)), str(U(2))
    P1, P2 = s1, s1 + "-p2"           # Steve's profile 1 (the bare uuid) and profile 2

    def on(p):
        PROF[s1] = p
    for k_ in (P1, P2, a1, str(U(3)), str(U(3)) + "-p2"):
        PP[k_] = 100000
    on(P1)
    K.check(str(GS.create(U(1), NAMES[1], "Fence")).startswith("+"), "SAME Steve (profile 1) creates a guild")
    gid = str(GS.gidOf(s1))
    g = GS.GUILDS.get(gid)

    def bank():
        return int(g.bank)

    def gfile():
        GS.flushDirty()
        return open(os.path.join(d8, "guilds", gid + ".properties"), encoding="latin-1").read()

    def strip(t):
        return "\n".join(l for l in t.splitlines() if not l.startswith("#"))
    r = str(GS.deposit(U(1), NAMES[1], "1000"))
    K.check(r.startswith("+Deposited 1000") and PP[P1] == 99000 and bank() == 1000 and "pnet." + P1 + "=1000|0" in gfile(), "SAME deposit on profile 1 booked to profile 1: %s" % r)
    on(P2)
    f0, pp0 = strip(gfile()), dict(PP)
    r = str(GS.withdraw(U(1), NAMES[1], "1"))
    K.check(r.startswith("-All 1,000 coins in the guild bank came from your other profile (profile 1) - coins never move between your own profiles")
            and bank() == 1000 and PP == pp0 and strip(gfile()) == f0, "SAME profile 2 withdraw refused (all fenced), nothing moved: %s" % r)
    r = str(GS.withdraw(U(1), NAMES[1], "all"))
    K.check(r.startswith("-All 1,000 coins") and bank() == 1000, "SAME profile 2 withdraw all refused: %s" % r)
    # another player's coins in the bank: profile 2 may take those only
    K.check(str(GS.invite(U(1), NAMES[1], NAMES[2])).startswith("+") and str(GS.accept(U(2), NAMES[2])).startswith("+"), "SAME Alex joins")
    GS.setLimit(U(1), NAMES[1], "member", "none")
    r = str(GS.deposit(U(2), NAMES[2], "500"))
    K.check(r.startswith("+Deposited 500") and bank() == 1500, "SAME Alex deposits 500: %s" % r)
    r = str(GS.withdraw(U(1), NAMES[1], "600"))
    K.check(r.startswith("-You can withdraw at most 500 coins on this profile: 1,000 coins in the guild bank came from your other profile (profile 1)") and bank() == 1500,
            "SAME profile 2: at most the free part (Alex's 500): %s" % r)
    r = str(GS.withdraw(U(1), NAMES[1], "all"))
    K.check(r.startswith("+Withdrew 500") and PP[P2] == 100500 and bank() == 1000, "SAME profile 2: 'all' = the free part (500): %s" % r)
    r = str(GS.withdraw(U(1), NAMES[1], "1"))
    K.check(r.startswith("-All 1,000 coins"), "SAME profile 2: nothing free left: %s" % r)
    # own deposit + withdraw on profile 2 unaffected (bank 1,300 = profile 1's 1,000 + profile 2's 300)
    GS.deposit(U(1), NAMES[1], "300")
    r = str(GS.withdraw(U(1), NAMES[1], "300"))
    K.check(r.startswith("+Withdrew 300") and PP[P2] == 100500 and bank() == 1000, "SAME profile 2 takes back what profile 2 put in: %s" % r)
    # the switch OFF = 0.1.7; no coins:fn:sameacct = blocked
    Xfer.BLOCK_SAME = False
    r = str(GS.withdraw(U(1), NAMES[1], "100"))
    K.check(r.startswith("+Withdrew 100") and PP[P2] == 100600, "SAME the SkyyCoins switch OFF: profile 2 may withdraw profile 1's coins (0.1.7): %s" % r)
    Xfer.BLOCK_SAME = True
    BR.remove("coins:fn:sameacct")
    r = str(GS.withdraw(U(1), NAMES[1], "1"))
    K.check(r.startswith("-All 900 coins"), "SAME coins:fn:sameacct missing = blocked (the default): %s" % r)
    BR.put("coins:fn:sameacct", SAME)
    # back on profile 1: its coins come out there
    on(P1)
    r = str(GS.withdraw(U(1), NAMES[1], "900"))
    K.check(r.startswith("+Withdrew 900") and PP[P1] == 99900 and bank() == 0, "SAME back on profile 1: its coins come out there: %s" % r)
    K.check(not pnet_sums_ok(n), "SAME the ledger adds up to the nets: %s" % pnet_sums_ok(n))
    # a refused add rolls the ledger back with the bank
    GS.deposit(U(1), NAMES[1], "400")
    pn0 = list(g.pnet.get(P1))
    FAIL["add"] = True
    r = str(GS.withdraw(U(1), NAMES[1], "400"))
    FAIL["add"] = False
    K.check(r.startswith("-SkyyCoins could not put the coins") and list(g.pnet.get(P1)) == pn0 and bank() == 400, "SAME a refused add: the ledger + bank rolled back: %s" % r)

    # ---- leave / kick: Bea deposits on profile 1, leaves from profile 2
    b3, B1, B2 = str(U(3)), str(U(3)), str(U(3)) + "-p2"
    GS.invite(U(1), NAMES[1], NAMES[3])
    GS.accept(U(3), NAMES[3])
    PROF[b3] = B1
    GS.deposit(U(3), NAMES[3], "1000")
    PROF[b3] = B2
    bk0, pb2 = bank(), PP[B2]
    note = str(GS.leaveNote(g, g.member(b3)))
    r = str(GS.leave(U(3), NAMES[3], True))
    K.check("1,000 coins your other profile (profile 1) put in are not counted here - leave from that profile to get its refund." in note,
            "SAME leave note on profile 2: %s" % note)
    K.check(r.startswith("+You left Fence.") and PP[B2] == pb2 and bank() == bk0 and int(GS.netValue(g, b3)) == 1000 and g.pnet.get(B1) is not None,
            "SAME leave from profile 2: no refund of profile 1's coins, the contribution kept (not forfeited): %s" % r)
    # Bea rejoins and leaves from profile 1: the 35 % refund goes to profile 1
    GS.invite(U(1), NAMES[1], NAMES[3])
    GS.accept(U(3), NAMES[3])
    PROF[b3] = B1
    pb1 = PP[B1]
    r = str(GS.leave(U(3), NAMES[3], True))
    K.check(r.startswith("+You left Fence. You got back 350 coins") and PP[B1] == pb1 + 350 and int(GS.netValue(g, b3)) == 0
            and not any(k_.startswith(b3) for k_ in [str(x) for x in g.pnet.keySet()]), "SAME leave from profile 1: 35 %% back to profile 1, nothing left, the ledger lines gone: %s" % r)
    # kick: Bea (member) deposited on profile 1, now on profile 2
    GS.invite(U(1), NAMES[1], NAMES[3])
    GS.accept(U(3), NAMES[3])
    PROF[b3] = B1
    GS.deposit(U(3), NAMES[3], "1000")
    PROF[b3] = B2
    pb2 = PP[B2]
    r = str(GS.kick(U(1), NAMES[1], NAMES[3]))
    K.check(r.startswith("+Removed Bea from the guild.") and PP[B2] == pb2 and int(GS.netValue(g, b3)) == 1000, "SAME kick of a member on profile 2: no refund of profile 1's coins: %s" % r)

    # ---- disband: Steve's share would include profile 1's coins
    GS.kick(U(1), NAMES[1], NAMES[2])
    on(P1)
    GS.withdraw(U(1), NAMES[1], "all")
    GS.deposit(U(1), NAMES[1], "2000")
    on(P2)
    f0, bk0, pp0 = strip(gfile()), bank(), dict(PP)
    r = str(GS.disband(U(1), NAMES[1], True))
    K.check(r.startswith("-Your share of the guild bank") and "your other profile (profile 1) put in - coins never move between your own profiles" in r
            and bank() == bk0 and PP == pp0 and strip(gfile()) == f0 and GS.GUILDS.containsKey(gid), "SAME disband on profile 2: refused, nothing changed: %s" % r)
    r = str(GS.leave(U(1), NAMES[1], True))
    K.check(r.startswith("-Your share of the guild bank") and GS.GUILDS.containsKey(gid), "SAME the last member's leave on profile 2: refused: %s" % r)
    on(P1)
    pp1 = PP[P1]
    r = str(GS.disband(U(1), NAMES[1], True))
    K.check(r.startswith("+Fence is disbanded.") and PP[P1] == pp1 + bk0, "SAME disband on profile 1: the bank to profile 1: %s" % r)
    # an admin delete is not fenced
    on(P1)
    GS.create(U(1), NAMES[1], "Fence2")
    g2 = GS.GUILDS.get(str(GS.gidOf(s1)))
    GS.deposit(U(1), NAMES[1], "700")
    on(P2)
    GS.CONFIRM.clear()
    GS.adminDelete(U(8), NAMES[8], "Fence2")
    pp2 = PP[P2]
    r = str(GS.adminDelete(U(8), NAMES[8], "Fence2"))
    K.check(r.startswith("+Fence2 is disbanded.") and PP[P2] == pp2 + 700, "SAME an admin delete is not fenced (paid to the active profile, logged): %s" % r)

    # ---- more paths: a throwing coins:fn:sameacct = blocked; two other profiles = "and others"; a kick whose refund cannot be paid
    # (the counted part leaves the kicked profile's ledger); a disband payout that cannot be taken back (the stuck share books the profile)
    on(P1)
    GS.create(U(1), NAMES[1], "Paths")
    gp = GS.GUILDS.get(str(GS.gidOf(s1)))
    GS.deposit(U(1), NAMES[1], "100")
    P3 = s1 + "-p3"
    PP[P3] = 100000
    on(P3)
    GS.deposit(U(1), NAMES[1], "100")

    @JImplements("java.util.function.Function")
    class Boom:
        @JOverride
        def apply(self, a):
            raise RuntimeError("boom")
    BR.put("coins:fn:sameacct", Boom())
    on(P2)
    r = str(GS.withdraw(U(1), NAMES[1], "1"))
    K.check(r.startswith("-All 200 coins in the guild bank came from your other profile (profile 1 and others)"), "SAME a throwing coins:fn:sameacct = blocked; two other profiles = 'profile 1 and others': %s" % r)
    BR.put("coins:fn:sameacct", SAME)
    GS.invite(U(1), NAMES[1], NAMES[3])
    GS.accept(U(3), NAMES[3])
    PROF[b3] = B2
    GS.deposit(U(3), NAMES[3], "1000")
    FAIL["addk"].add(B2)
    r = str(GS.kick(U(1), NAMES[1], NAMES[3]))
    FAIL["addk"].clear()
    K.check("could not be paid" in r and int(GS.netValue(gp, b3)) == 0 and gp.pnet.get(B2) is None,
            "SAME a kick whose refund cannot be paid: the contribution goes to the guild, the kicked profile's ledger lines with it: %s" % r)
    GS.invite(U(1), NAMES[1], NAMES[2])
    GS.accept(U(2), NAMES[2])
    GS.deposit(U(2), NAMES[2], "300")
    on(P3)
    GS.withdraw(U(1), NAMES[1], "100")          # fix F1: profile 3's coins out first - a payee with ANY fenced coins is refused now
    on(P1)
    w0 = int(gp.pnet.get(P1)[1])
    FAIL["addk"].add(a1)
    FAIL["takek"].add(P1)
    r = str(GS.disband(U(1), NAMES[1], True))
    FAIL["addk"].clear()
    FAIL["takek"].clear()
    sh = int(gp.pnet.get(P1)[1]) - w0
    K.check(r.startswith("-SkyyCoins could not pay") and sh > 0 and GS.GUILDS.containsKey(str(gp.id)) and not pnet_sums_ok(n),
            "SAME a disband payout that cannot be taken back: the stuck share (%d) is booked to the profile it went to: %s %s" % (sh, r, pnet_sums_ok(n)[:2]))
    GS.CONFIRM.clear()
    GS.adminDelete(U(8), NAMES[8], "Paths")
    r = str(GS.adminDelete(U(8), NAMES[8], "Paths"))
    K.check(r.startswith("+Paths is disbanded") and not pnet_sums_ok(n), "SAME Paths deleted by an admin; every file's ledger (deleted/ too) adds up: %s %s" % (r, pnet_sums_ok(n)[:2]))

    # ================================================================ FIX ROUND checks (one per fix)
    # ---- F1: two depositors, the Leader on profile 2 - the old 'share <= bank - fenced' let profile 1's coins out
    on(P1)
    GS.create(U(1), NAMES[1], "Fix1")
    gf = GS.GUILDS.get(str(GS.gidOf(s1)))
    gidf = str(gf.id)
    GS.invite(U(1), NAMES[1], NAMES[2])
    GS.accept(U(2), NAMES[2])
    GS.deposit(U(1), NAMES[1], "1000")
    GS.deposit(U(2), NAMES[2], "1000")
    on(P2)
    GS.CONFIRM.clear()
    GS.flushDirty()
    ffp = os.path.join(d8, "guilds", gidf + ".properties")
    pp0, bk0, ff0 = dict(PP), int(gf.bank), strip(open(ffp, encoding="latin-1").read())
    r = str(GS.disband(U(1), NAMES[1], True))
    GS.flushDirty()
    K.check(r.startswith("-Your share of the guild bank (1,000 coins) would include coins your other profile (profile 1) put in") and PP == pp0
            and int(gf.bank) == bk0 == 2000 and GS.GUILDS.containsKey(gidf) and strip(open(ffp, encoding="latin-1").read()) == ff0,
            "FIX F1 disband by the Leader on profile 2 with a 2nd depositor (bank 2,000, share 1,000 = bank - fenced): refused, nothing changed: %s" % r)
    # the fenced payee is ANOTHER member (Alex put in on profile 1, is now on profile 2): Steve (profile 1) disbands -> refused, names Alex
    on(P1)
    A1, A2 = a1, a1 + "-p2"
    PP[A2] = 100000
    PROF[a1] = A2
    r = str(GS.disband(U(1), NAMES[1], True))
    K.check(r.startswith("-Alex's share of the guild bank") and "Alex must switch to that profile first" in r and GS.GUILDS.containsKey(gidf),
            "FIX F1 a fenced OTHER member (on their 2nd profile) blocks a disband, named: %s" % r)
    PROF[a1] = A1
    pa1, ps1 = PP[A1], PP[P1]
    r = str(GS.disband(U(1), NAMES[1], True))
    K.check(r.startswith("+Fix1 is disbanded.") and PP[P1] == ps1 + 1000 and PP[A1] == pa1 + 1000,
            "FIX F1 everyone on the profile that paid: the disband goes through, each share to its own profile: %s" % r)
    del PROF[a1]

    # ---- F2: profile switch races
    on(P1)
    GS.create(U(1), NAMES[1], "Fix2")
    g2f = GS.GUILDS.get(str(GS.gidOf(s1)))
    BUSY = "profile:busy:" + s1
    # (a) a switch running at the deposit: refused, nothing moved, the reservation released
    BR.put(BUSY, W.Boolean.TRUE)
    pp0 = dict(PP)
    r = str(GS.deposit(U(1), NAMES[1], "500"))
    BR.remove(BUSY)
    K.check(r == "-A profile switch is running - nothing moved. Try again in a moment." and PP == pp0 and int(g2f.bank) == 0
            and int(g2f.busy) == 0 and int(g2f.pendIn) == 0 and g2f.pnet.isEmpty(), "FIX F2 deposit while a switch runs: refused, nothing moved, reservation released: %s" % r)
    # (b) the switch lands right AFTER the take: the coins came from profile 1 and are booked to profile 1 (read right before the take)
    SWT["after"] = P2
    r = str(GS.deposit(U(1), NAMES[1], "500"))
    SWT["after"] = None
    K.check(r.startswith("+Deposited 500") and PP[P1] == pp0[P1] - 500 and PP[P2] == pp0[P2] and list(g2f.pnet.get(P1)) == [500, 0] and g2f.pnet.get(P2) is None,
            "FIX F2 a switch right after the take: booked to the profile that paid (profile 1): %s" % r)
    K.check(str(GS.withdraw(U(1), NAMES[1], "1")).startswith("-All 500 coins"), "FIX F2 ... and profile 2 cannot take them")
    # (c) a withdraw whose profile flips after the guild lock, before coins:fn:add: rolled back, nothing moved
    on(P1)
    pp0, pn0 = dict(PP), list(g2f.pnet.get(P1))
    flip_on_key(s1, P2, 1)
    r = str(GS.withdraw(U(1), NAMES[1], "500"))
    K.check(r == "-Your profile changed (or a profile switch is running) - nothing moved. Try again in a moment." and PP == pp0 and int(g2f.bank) == 500
            and list(g2f.pnet.get(P1)) == pn0 and int(g2f.busy) == 0, "FIX F2 withdraw: the profile flipped before the add -> rolled back (bank, ledger, purses): %s" % r)
    on(P1)
    # (d) a refund while the member is switching: the leave is refused, the kick waits - nothing forfeited
    GS.invite(U(1), NAMES[1], NAMES[3])
    GS.accept(U(3), NAMES[3])
    PROF[b3] = B1
    GS.deposit(U(3), NAMES[3], "1000")
    BB = "profile:busy:" + b3
    BR.put(BB, W.Boolean.TRUE)
    bk0, pb1, pb2 = int(g2f.bank), PP[B1], PP[B2]
    r = str(GS.leave(U(3), NAMES[3], True))
    r2 = str(GS.kick(U(1), NAMES[1], NAMES[3]))
    BR.remove(BB)
    K.check("a profile switch is running" in r and r2.startswith("-Bea is switching profiles right now") and int(g2f.bank) == bk0 and PP[B1] == pb1
            and g2f.member(b3) is not None and int(GS.netValue(g2f, b3)) == 1000, "FIX F2 leave / kick refund while switching: refused, nothing moved, Bea still a member: %s | %s" % (r, r2))
    # (e) the switch flips between the refund's file write and coins:fn:add: rolled back (bank, ledger, purses)
    pn0 = list(g2f.pnet.get(B1))
    flip_on_key(b3, B2, 1, True)
    r = str(GS.leave(U(3), NAMES[3], True))
    K.check("a profile switch is running" in r and int(g2f.bank) == bk0 and list(g2f.pnet.get(B1)) == pn0 and PP[B1] == pb1 and PP[B2] == pb2
            and g2f.member(b3) is not None, "FIX F2 refund: the profile flipped after the write -> rolled back: %s" % r)
    # (e2) the switch lands between the refund's sum (refundInfo) and its payment: the fence for the new profile differs -> refused
    PROF[b3] = B1
    flip_on_key(b3, B2, 0, True)
    r = str(GS.leave(U(3), NAMES[3], True))
    K.check("a profile switch is running" in r and int(g2f.bank) == bk0 and PP[B1] == pb1 and PP[B2] == pb2 and g2f.member(b3) is not None,
            "FIX F2 refund: the profile flipped after the refund was counted -> refused: %s" % r)
    PROF[b3] = B1
    # (f) a disband payout whose payee flips mid-payout: the paid shares go back, refused
    pp0, bk0 = dict(PP), int(g2f.bank)
    flip_on_key(b3, B2, 1, True)
    r = str(GS.disband(U(1), NAMES[1], True))
    K.check(r.startswith("-Bea switched profiles during the payout") and GS.GUILDS.containsKey(str(g2f.id)) and int(g2f.bank) == bk0
            and PP[P1] == pp0[P1] and PP[B1] == pp0[B1] and PP[B2] == pp0[B2], "FIX F2 disband: a payee flipped mid-payout -> every paid share back, refused: %s" % r)
    PROF[b3] = B1
    SWK["uid"] = None
    BR.put(BB, W.Boolean.TRUE)
    r = str(GS.disband(U(1), NAMES[1], True))
    BR.remove(BB)
    K.check(r.startswith("-Bea is switching profiles right now") and GS.GUILDS.containsKey(str(g2f.id)), "FIX F2 disband while a payee is switching: refused up front: %s" % r)

    # ---- F3: untracked (pre-0.1.8) coins taken out on profile 1 no longer leave a negative ledger that unfences a later deposit
    on(P1)
    GS.kick(U(1), NAMES[1], NAMES[3])
    GS.CONFIRM.clear()
    GS.disband(U(1), NAMES[1], True)
    GS.create(U(1), NAMES[1], "Fix3")
    g3f = GS.GUILDS.get(str(GS.gidOf(s1)))
    g3f.bank = 1000          # 1,000 coins from before 0.1.8: no ledger line
    GS.netAdd(g3f, s1, 1000, 0)
    r = str(GS.withdraw(U(1), NAMES[1], "1000"))
    K.check(r.startswith("+Withdrew 1000") and g3f.pnet.get(P1) is None, "FIX F3 untracked coins out on profile 1: nothing booked (no negative ledger): %s" % r)
    GS.deposit(U(1), NAMES[1], "500")
    on(P2)
    r = str(GS.withdraw(U(1), NAMES[1], "1"))
    K.check(r.startswith("-All 500 coins") and list(g3f.pnet.get(P1)) == [500, 0], "FIX F3 a later profile 1 deposit is fenced from profile 2: %s" % r)
    on(P1)
    GS.invite(U(1), NAMES[1], NAMES[2])
    GS.accept(U(2), NAMES[2])
    GS.deposit(U(2), NAMES[2], "300")
    r = str(GS.withdraw(U(1), NAMES[1], "800"))
    K.check(r.startswith("+Withdrew 800") and list(g3f.pnet.get(P1)) == [500, 500], "FIX F3 profile 1 takes 800 (its 500 + Alex's 300): booked only its own 500: %s" % r)
    GS.deposit(U(1), NAMES[1], "200")
    GS.deposit(U(2), NAMES[2], "100")
    pn0 = list(g3f.pnet.get(P1))
    FAIL["add"] = True
    r = str(GS.withdraw(U(1), NAMES[1], "300"))
    FAIL["add"] = False
    K.check(r.startswith("-SkyyCoins could not put the coins") and list(g3f.pnet.get(P1)) == pn0, "FIX F3 a refused add takes back exactly what was booked (200 of 300): %s %s" % (r, pn0))
    K.check(not pnet_sums_ok(n), "FIX F3 the ledger is never negative anywhere: %s" % pnet_sums_ok(n)[:2])
    GS.CONFIRM.clear()
    GS.adminDelete(U(8), NAMES[8], "Fix3")
    GS.adminDelete(U(8), NAMES[8], "Fix3")
    # ---- the ledger survives a restart; 0.1.7 reads + rewrites a 0.1.8 file
    on(P1)
    GS.create(U(1), NAMES[1], "Fence3")
    gid3 = str(GS.gidOf(s1))
    GS.deposit(U(1), NAMES[1], "250")
    GS.flushDirty()
    GS.stopIO()
    n2 = T7.G(W, jar, d8, "new")
    n2.start()
    on(P2)
    r = str(n2.GS.withdraw(U(1), NAMES[1], "1"))
    K.check(r.startswith("-All 250 coins"), "SAME after a restart (new loader, the file): the fence holds: %s" % r)
    n2.GS.flushDirty()
    n2.GS.stopIO()
    f3 = os.path.join(d8, "guilds", gid3 + ".properties")
    K.check("pnet." + P1 + "=250|0" in open(f3, encoding="latin-1").read(), "SAME the file has pnet.<profile key>")
    open(f3, "a", encoding="latin-1").write("pnet.bad/key=5|0" + chr(10) + "pnet." + s1 + "-p9=x|y" + chr(10))
    n3 = T7.G(W, jar, d8, "new")
    n3.start()
    g3 = n3.GS.GUILDS.get(gid3)
    ks = sorted(str(x) for x in g3.pnet.keySet())
    K.check(ks == sorted([P1, s1 + "-p9"]) and list(g3.pnet.get(s1 + "-p9")) == [0, 0], "SAME the loader: a bad key is skipped, a bad number reads 0: %s" % ks)
    n3.GS.stopIO()
    d7 = os.path.join(scratch, "rb7")
    os.makedirs(os.path.join(d7, "guilds"), exist_ok=True)
    import shutil
    shutil.copy(f3, os.path.join(d7, "guilds", gid3 + ".properties"))
    o7 = T7.G(W, OLD_JAR, d7, "old")
    o7.start()
    g7 = o7.GS.GUILDS.get(gid3)
    K.check(g7 is not None and int(g7.bank) == 250 and int(o7.GS.netValue(g7, s1)) == 250, "ROLLBACK 0.1.7 reads a 0.1.8 file (bank + net intact)")
    g7.dirty = True
    o7.GS.flushDirty()
    o7.GS.stopIO()
    t7 = open(os.path.join(d7, "guilds", gid3 + ".properties"), encoding="latin-1").read()
    K.check("pnet." not in t7 and "bank=250" in t7, "ROLLBACK 0.1.7 rewrites it without pnet.* (the fences are gone again), the bank intact")
    K.notes.append("SAME fenced refusals counted: %d" % int(GS.FENCED.get()))
    gen = open(os.path.join(HERE, "build_skyyguilds_%s.py" % VERSION), encoding="utf8").read()
    K.check("guild bank coins between one player's own profiles" in gen, "static: the ready line names the same-account rule")
    K.save()


def run_live(out, jar, scratch, home):
    return T7.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    for j_ in (OLD_JAR, COINS_JAR):
        assert os.path.isfile(j_), j_
    HK.run(name="SkyyGuilds", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyGuilds"))
