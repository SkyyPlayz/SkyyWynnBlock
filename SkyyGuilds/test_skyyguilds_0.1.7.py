"""Harness for SkyyGuilds 0.1.7 (lag fixes: off-lock writer, XP flush 60 s, publish on change, coin calls outside the lock; tools/guilds_0_1_7_patch.py).
Build first: python tools/guilds_0_1_7_patch.py && python SkyyGuilds/build_skyyguilds_0.1.7.py

    python SkyyGuilds/test_skyyguilds_0.1.7.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; a fake Universe (Unsafe-allocated) holds the online players, as test_skyyguilds_0.1.6.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.6 -> 0.1.7: exactly the listed members differ (+ GWriter)
  X  exec     0.1.6 and 0.1.7 side by side (own loaders, own data folders, own fake purses):
              DIFF  1,500 random steps (create / invite / accept / deposit / withdraw / limits / promote / demote / transfer / leave with
                    refunds / kick / disband / chat / XP / ticks) on both jars: identical results, purses, banks, nets, members and
                    guild files (after a synchronous flush) after every step; coins conserved
              LOCK  coins:fn:take / coins:fn:add run OUTSIDE the GuildStore lock on 0.1.7 (Thread.holdsLock in the stand-in: false; 0.1.6:
                    true); during the call the guild is reserved (busy 1, pendIn = the deposit) and a disband / leave / kick / last-member
                    leave / admin delete is refused with nothing changed; a second deposit counts the reservation against the bank cap;
                    the withdraw's lower bank is already on disk during coins:fn:add; refused take / add = nothing moved, reservation
                    released, the withdraw rolled back on disk
              WRITE takeFlush: XP-only dirties wait 60 s, an urgent (failed) guild goes at the next tick; the writer runs while the main
                    thread HOLDS the GuildStore lock (writes are outside it); an older snapshot never lands over a newer write (gen);
                    an archived guild's file is never recreated by a stale snapshot; writeFailed marks urgent; GWriter thread
                    SkyyGuilds-IO (daemon), submitWrites (inline without a writer), stopIO
              PUB   guild:info:<uuid> rebuilt only on change (a counting proxy as GuildStore.BRIDGE: a second tick with nothing changed
                    puts nothing); GuildTick.run on both jars gives the same bridge values; setOnline / touchN / publishGuildN counts
              REAL  the real SkyyCoins 0.1.6 CoinFn on the bridge: deposit + withdraw + refund move the same coins, balance files after flush
              FIX   (fix round E) coins:fn:flush runs right after a successful take (deposit: BEFORE the bank file is credited) and
                    add (withdraw: after the debited bank file), never after a refused take; a refused add of withdraw #1 while withdraw #2
                    of the same member went through keeps #2's day count; a level-curve change (GCfg.BASE) rebuilds guild:info without
                    any XP; the REAL SkyyCoins 0.1.6 purse file holds a deposit right after it (no explicit flush)
  D  live     start twice on a scratch COPY of the live Skyy_SkyyGuilds with 0.1.6 and 0.1.7: the same guilds, banks, members and published
              values; no file changed by 0.1.7 that 0.1.6 does not change
  AA engine-access audit
Scratch: tools/dev/scratch/perfecon/guilds (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, random, shutil, threading, time, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.7"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGuilds-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGuilds-0.1.6.jar")
COINS_JAR = os.path.join(ROOT, "SkyyCoins", "SkyyCoins-0.1.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfecon", "guilds")))
PKG = "com.skyy.guilds."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGuilds")
EXPECT = {
    "GMember": ["+f pInfo", "+f pXp", "+f pOnl", "+f pSize", "+f pRank", "+f pGName", "+f pTag", "+f pBase", "+f pStep"],
    "Guild": ["+f io", "+f gen", "+f written", "+f urgent", "+f flushedAt", "+f onl", "+f busy", "+f pendIn", "~c "],
    "GuildStore": ["+f BRIDGE", "+f IO", "+f XP_FLUSH_MS", "+f WRITES", "+m bridge0", "~m bridge", "+m pubMember", "+m publishGuildN",
                   "~m publishGuild", "~m addXp", "+m touchN", "~m touch", "+m setOnline", "+m writeGen0", "+m writeGen", "~m saveGuild",
                   "+m takeFlush", "+m writeFailed", "+m writeAll", "+m archive0", "~m archive", "~m disbandNow", "~m leave", "~m kick",
                   "+m depositBegin", "+m depositEnd", "~m deposit", "+m withdrawBegin", "+m withdrawEnd", "~m withdraw", "+m submitWrites",
                   "+m stopIO", "~<clinit>",
                   "+m coinsFlush", "~m coinsTake", "~m coinsAdd"],                   # fix round E: coins:fn:flush after take / add
    "GuildTick": ["~m run"],
    "SkyyGuildsPlugin": ["~m setup", "~m shutdown"],
    "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header", "~<clinit>"],   # header + <clinit>: the version text (default lines)
    "CfgHist": ["~m compact", "~m snapshot", "~m versions"],                        # KEEP 20 -> 10 (the constant is inlined)
    "GCfg": ["~m load"],                                                             # the default config text names the version
    "CfgFn": ["~m opExport"],                                                       # the version text
}
ADDED = ["GWriter"]
NAMES = {1: "Steve", 2: "Alex", 3: "Bea", 4: "Cid", 5: "Dot", 6: "Eve", 7: "Finn", 8: "Gus"}


class World(object):
    """the shared Java objects: fake Universe + players, the bridge with switchable fake purses (one per jar)"""

    def __init__(self, scratch):
        from jpype import JClass, JImplements, JOverride
        self.J = JClass
        Cls = JClass("java.lang.Class")
        self.UUID, self.Paths, self.Long, self.Boolean = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
        self.System = JClass("java.lang.System")
        self.CHM = JClass("java.util.concurrent.ConcurrentHashMap")
        PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        Universe = JClass("com.hypixel.hytale.server.core.universe.Universe")
        Holder = JClass("com.hypixel.hytale.component.Holder")
        fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
        fu.setAccessible(True)
        U = fu.get(None)

        def setf(obj, cls, name, val):
            f = cls.class_.getDeclaredField(name)
            f.setAccessible(True)
            f.set(obj, val)
        uni = U.allocateInstance(Universe.class_)
        self.PLAYERS = self.CHM()
        setf(uni, Universe, "playersByUuid", self.PLAYERS)
        setf(uni, Universe, "players", self.PLAYERS.values())
        setf(None, Universe, "instance", uni)
        holder = U.allocateInstance(Holder.class_)

        def pref(n):
            p = U.allocateInstance(PR.class_)
            setf(p, PR, "uuid", self.uid(n))
            setf(p, PR, "username", NAMES.get(n, "P%d" % n))
            setf(p, PR, "holder", holder)
            return p
        self.pref = pref
        self.BR = self.CHM()
        self.System.getProperties().put("skyy.bridge", self.BR)
        self.PURSES = {"old": {}, "new": {}}
        self.CUR = ["new"]
        self.FAIL = {"add": set(), "take": set(), "get": set()}
        self.HOOK = [None]
        W = self

        @JImplements("java.util.function.Function")
        class CoinsGet:
            @JOverride
            def apply(self, u):
                if str(u) in W.FAIL["get"]:
                    return None
                return W.Long.valueOf(W.PURSES[W.CUR[0]].get(str(u), 0))

        @JImplements("java.util.function.Function")
        class CoinsAdd:
            @JOverride
            def apply(self, a):
                u, n = str(a[0]), int(a[1])
                if W.HOOK[0] is not None:
                    W.HOOK[0]("add", u, n)
                if u in W.FAIL["add"]:
                    return None
                P = W.PURSES[W.CUR[0]]
                P[u] = P.get(u, 0) + n
                return W.Long.valueOf(P[u])

        @JImplements("java.util.function.Function")
        class CoinsTake:
            @JOverride
            def apply(self, a):
                u, n = str(a[0]), int(a[1])
                if W.HOOK[0] is not None:
                    W.HOOK[0]("take", u, n)
                if u in W.FAIL["take"]:
                    return None
                P = W.PURSES[W.CUR[0]]
                if P.get(u, 0) < n:
                    return W.Boolean.FALSE
                P[u] = P.get(u, 0) - n
                return W.Boolean.TRUE
        self.COINS = (CoinsGet(), CoinsAdd(), CoinsTake())
        self.coins_on()

    def coins_on(self):
        for key, f in zip(("coins:fn:get", "coins:fn:add", "coins:fn:take"), self.COINS):
            self.BR.put(key, f)

    def uid(self, n):
        return self.UUID(0x6d11d, n)

    def online(self, ns):
        self.PLAYERS.clear()
        for n in ns:
            self.PLAYERS.put(self.uid(n), self.pref(n))


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


class G(object):
    """one jar's GuildStore on its own folder"""

    def __init__(self, W, jar, d, k):
        from jpype import JClass
        self.W, self.k, self.d = W, k, d
        self.L = loader_for(jar)
        g = lambda n: JClass(PKG + n, loader=self.L)
        self.GS, self.Cfg, self.X, self.Tick = g("GuildStore"), g("GCfg"), g("XpTask"), g("GuildTick")
        self.GClass = g("Guild")
        os.makedirs(os.path.join(d, "guilds"), exist_ok=True)
        P = W.Paths
        self.GS.DIR = P.get(d)
        self.GS.GDIR = P.get(os.path.join(d, "guilds"))
        self.Cfg.FILE = P.get(os.path.join(d, "config.properties"))

    def start(self):
        self.W.CUR[0] = self.k
        self.Cfg.load()
        self.GS.loadAll()
        self.GS.DAY = 1234
        self.GS.DAY_READ = int(self.W.System.currentTimeMillis()) + 10 ** 9

    def call(self, name, *a):
        self.W.CUR[0] = self.k
        try:
            return str(getattr(self.GS, name)(*a))
        except Exception as e:
            return "EXC " + str(e)[:100]

    def state(self):
        out = {}
        it = self.GS.GUILDS.values().iterator()
        while it.hasNext():
            g = it.next()
            mem = {}
            mi = g.members.values().iterator()
            while mi.hasNext():
                m = mi.next()
                mem[str(m.uuid)] = (int(m.rank), int(m.contrib), str(m.name), int(m.wdDay), int(m.wdUsed))
            nets = {}
            ni = g.net.keySet().iterator()
            while ni.hasNext():
                kk = ni.next()
                v = g.net.get(kk)
                nets[str(kk)] = (int(v[0]), int(v[1]))
            out[str(g.id)] = (str(g.name), str(g.tag), int(g.xp), int(g.bank), int(g.limAdmin), int(g.limMember), mem, nets,
                              [re.sub(r"^\d+\|", "", str(x)) for x in g.log])
        return out

    def files(self):
        out = {}
        for p in sorted(glob.glob(os.path.join(self.d, "guilds", "**", "*.properties"), recursive=True)):
            lines = [l for l in open(p, encoding="latin-1").read().splitlines() if not l.startswith("#")]
            lines = [re.sub(r"^(log\.\d+=)\d+\|", r"\1", l) for l in lines]
            lines = [re.sub(r"^(member\.[^=]+=\d+\|)\d+\|", r"\1", l) for l in lines]   # the join time (ms apart on the two jars)
            lines = [l for l in lines if not l.startswith("disbanded=") and not l.startswith("created=") and not l.startswith("netSeed=")]
            out[re.sub(r"-\d+\.properties$", ".properties", os.path.relpath(p, self.d))] = sorted(lines)
        return out


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    import jpype
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    W = World(scratch)
    Sys = W.System
    o, n = G(W, OLD_JAR, os.path.join(scratch, "x6"), "old"), G(W, jar, os.path.join(scratch, "x7"), "new")
    o.start()
    n.start()
    br = W.BR
    K.eq(Sys.identityHashCode(n.GS.bridge()), Sys.identityHashCode(br), "X GuildStore.bridge = the System map")
    K.eq(Sys.identityHashCode(n.GS.BRIDGE), Sys.identityHashCode(br), "X GuildStore.BRIDGE caches it")
    K.eq(Sys.identityHashCode(n.GS.bridge0()), Sys.identityHashCode(br), "X bridge0")
    CR = JClass(PKG + "CfgRows", loader=n.L)
    K.eq(Sys.identityHashCode(CR.bridge()), Sys.identityHashCode(br), "X CfgRows.bridge = the same map")
    K.eq(int(CR.KEEP), 10, "X config kit KEEP 10")
    for k in ("old", "new"):
        for i in NAMES:
            W.PURSES[k][str(W.uid(i))] = 50000
    W.online(list(NAMES))
    # ---------------------------------------------------------------- DIFF
    rnd = random.Random(717)
    diffs = 0
    okops = {}
    U = W.uid
    OPS = ["create", "invite", "accept", "deposit", "deposit", "withdraw", "withdraw", "limit", "promote", "demote", "transfer", "leave",
           "leave2", "kick", "disband", "chat", "xp", "tick", "flush", "online", "tag", "join", "join", "join", "deposit", "kick", "kick", "leave2"]

    def members_of():
        """{gid: {n: rank}} from 0.1.7's memory (actors are picked from it so most ops can succeed)"""
        out = {}
        for gid, v in n.state().items():
            out[gid] = dict((nn, v[6][str(U(nn))][0]) for nn in NAMES if str(U(nn)) in v[6])
        return out
    for step in range(3000):
        op = rnd.choice(OPS)
        a, b = rnd.choice(list(NAMES)), rnd.choice(list(NAMES))
        amt = rnd.choice(["500", "2k", "all", "1", "100000", "abc", "half", "0", "300", "1k"])
        mo = members_of()
        free = [x for x in NAMES if not any(x in m for m in mo.values())]
        if mo and rnd.random() < 0.7:
            gm = mo[rnd.choice(sorted(mo))]
            lead = [x for x, r in gm.items() if r == 2]
            low = [x for x, r in gm.items() if r < 2]
            if op in ("deposit", "withdraw", "leave", "leave2", "chat", "xp"):
                a = rnd.choice(sorted(gm))
            elif op in ("kick", "promote", "demote", "transfer", "limit", "tag", "disband", "invite") and lead:
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
        if op == "create":
            args = ("create", U(a), NAMES[a], "Guild%d" % rnd.randint(1, 4))
        elif op == "invite":
            args = ("invite", U(a), NAMES[a], NAMES[b])
        elif op == "accept":
            args = ("accept", U(a), NAMES[a])
        elif op == "deposit":
            args = ("deposit", U(a), NAMES[a], amt)
        elif op == "withdraw":
            args = ("withdraw", U(a), NAMES[a], amt)
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
        elif op == "chat":
            args = ("chat", U(a), NAMES[a], "hi")
        elif op == "tag":
            args = ("setTag", U(a), NAMES[a], "T%d" % b)
        elif op == "xp":
            args = None
            gid = o.GS.gidOf(str(U(a)))
            gid2 = n.GS.gidOf(str(U(a)))
            ra = str(o.GS.addXp(gid, str(U(a)), 37)) if gid is not None else None
            rb = str(n.GS.addXp(gid2, str(U(a)), 37)) if gid2 is not None else None
            r_o, r_n = ra, rb
        elif op == "online":
            args = None
            W.online(rnd.sample(list(NAMES), rnd.randint(0, len(NAMES))))
            r_o = r_n = None
        elif op == "tick":
            args = None
            W.CUR[0] = "old"
            o.Tick().run()
            W.CUR[0] = "new"
            n.Tick().run()
            r_o = r_n = None
        else:
            args = None
            o.GS.flushDirty()
            n.GS.flushDirty()
            r_o = r_n = None
        if args is not None:
            if not hasattr(n.GS, args[0]):
                continue
            r_o, r_n = o.call(*args), n.call(*args)
        if isinstance(r_n, str) and r_n.startswith("+"):
            okops[op] = okops.get(op, 0) + 1
            if "got back" in r_n:
                okops["refund"] = okops.get("refund", 0) + 1
        if r_o != r_n:
            diffs += 1
            if diffs <= 4:
                K.check(False, "X DIFF step %d %s: 0.1.6 %r vs 0.1.7 %r" % (step, (args or (op,))[0], r_o, r_n))
        so, sn = o.state(), n.state()
        if so != sn:
            diffs += 1
            if diffs <= 4:
                K.check(False, "X DIFF step %d %s: the guild state differs" % (step, op))
        if W.PURSES["old"] != W.PURSES["new"]:
            diffs += 1
            if diffs <= 4:
                K.check(False, "X DIFF step %d %s: purses differ" % (step, op))
        tot = sum(W.PURSES["new"].values()) + sum(v[3] for v in sn.values())
        if tot != 50000 * len(NAMES):
            diffs += 1
            if diffs <= 4:
                K.check(False, "X DIFF step %d: coins not conserved (%d)" % (step, tot))
        if step % 50 == 49:
            o.GS.flushDirty()
            n.GS.flushDirty()
            fo, fn_ = o.files(), n.files()
            if fo != fn_:
                diffs += 1
                bad = [x for x in set(fo) | set(fn_) if fo.get(x) != fn_.get(x)][:2]
                det = [(x, sorted(set(fo.get(x) or []) - set(fn_.get(x) or []))[:4], sorted(set(fn_.get(x) or []) - set(fo.get(x) or []))[:4]) for x in bad]
                K.check(False, "X DIFF step %d: guild files differ %s" % (step, det))
    K.eq(diffs, 0, "X DIFF: 3,000 random steps identical on 0.1.6 and 0.1.7 (results, state, purses, files), coins conserved")
    K.notes.append("X DIFF: %d guilds at the end; successful ops %s" % (len(n.state()), okops))
    K.check(all(okops.get(x, 0) >= 5 for x in ("create", "accept", "deposit", "withdraw", "leave", "kick", "disband")) and okops.get("refund", 0) >= 1,
            "X DIFF covered every money path (5+ each, a paid leave / kick refund too): %s" % okops)
    # ---------------------------------------------------------------- LOCK: coin calls outside the GuildStore lock + the reservation
    for gg in (o, n):
        W.CUR[0] = gg.k
        gg.GS.GUILDS.clear()
        gg.GS.BYNAME.clear()
        gg.GS.BYPLAYER.clear()
        gg.GS.INVITES.clear()
        gg.GS.CONFIRM.clear()
    W.online(list(NAMES))
    for k in ("old", "new"):
        for i in NAMES:
            W.PURSES[k][str(W.uid(i))] = 50000
    for gg in (o, n):
        W.CUR[0] = gg.k
        gg.GS.create(U(1), NAMES[1], "LockGuild")
        for i in (2, 3):
            gg.GS.invite(U(1), NAMES[1], NAMES[i])
            gg.GS.accept(U(i), NAMES[i])
        gg.GS.deposit(U(3), NAMES[3], "1000")
    seen = {}

    def hook_for(gg):
        def hook(kind, u, amount):
            GSc = gg.GS.class_
            held = bool(JClass("java.lang.Thread").holdsLock(GSc))
            g = gg.GS.guildOf(str(U(1)))
            info = {"held": held, "busy": int(g.busy) if gg.k == "new" else None, "pendIn": int(g.pendIn) if gg.k == "new" else None}
            if gg.k == "new" and seen.get("probe_" + kind):
                seen["probe_" + kind] = False
                bank_file = [l for l in open(os.path.join(gg.d, "guilds", str(g.id) + ".properties"), encoding="latin-1").read().splitlines() if l.startswith("bank=")]
                info["bank_file"] = bank_file
                info["bank_mem"] = "bank=%d" % int(g.bank)
                info["disband"] = str(gg.GS.disband(U(1), NAMES[1], True))
                info["kick"] = str(gg.GS.kick(U(1), NAMES[1], NAMES[2]))
                info["leave"] = str(gg.GS.leave(U(2), NAMES[2], True))
                info["deposit2"] = str(gg.GS.deposit(U(2), NAMES[2], "2"))
                seen[(gg.k, kind)] = info
                return
            if (gg.k, kind) not in seen:
                seen[(gg.k, kind)] = info
        return hook
    for gg in (o, n):
        W.CUR[0] = gg.k
        W.HOOK[0] = hook_for(gg)
        seen["probe_take"] = seen["probe_add"] = gg.k == "new"
        gg.GS.deposit(U(2), NAMES[2], "300")
        gg.GS.withdraw(U(1), NAMES[1], "200")
        W.HOOK[0] = None
    K.check(seen[("old", "take")]["held"] and seen[("old", "add")]["held"], "X LOCK: 0.1.6 calls coins:fn:take / add INSIDE the GuildStore lock (the control)")
    t7, a7 = seen[("new", "take")], seen[("new", "add")]
    K.check(not t7["held"], "X LOCK: 0.1.7 deposit calls coins:fn:take OUTSIDE the GuildStore lock")
    K.check(not a7["held"], "X LOCK: 0.1.7 withdraw calls coins:fn:add OUTSIDE the GuildStore lock")
    K.eq((t7["busy"], t7["pendIn"]), (1, 300), "X LOCK: during the take the guild is reserved (busy 1, pendIn 300)")
    K.eq(a7["busy"], 1, "X LOCK: during the add the guild is reserved")
    K.eq(a7.get("bank_file"), [a7.get("bank_mem")], "X LOCK: the withdraw's lower bank is on disk before coins:fn:add (write-first)")
    for kind, info in (("take", t7), ("add", a7)):
        K.check(info["disband"].startswith("-A guild bank move is in progress"), "X LOCK (%s): a disband is refused: %r" % (kind, info["disband"]))
        K.check(info["kick"].startswith("-A guild bank move is in progress"), "X LOCK (%s): a kick is refused: %r" % (kind, info["kick"]))
        K.check(info["leave"].startswith("-A guild bank move is in progress"), "X LOCK (%s): a leave is refused: %r" % (kind, info["leave"]))
    K.check(t7["deposit2"].startswith("+"), "X LOCK: a second deposit during the first goes through (its own reservation): %r" % t7["deposit2"])
    g7 = n.GS.guildOf(str(U(1)))
    K.eq((int(g7.busy), int(g7.pendIn)), (0, 0), "X LOCK: reservations released")
    # the bank cap counts the reservation
    W.CUR[0] = "new"
    cap0 = int(n.Cfg.MAX_BANK)
    n.Cfg.MAX_BANK = int(g7.bank) + 500
    capres = {}

    def cap_hook(kind, u, amount):
        if kind == "take" and "inner" not in capres:
            capres["inner"] = str(n.GS.deposit(U(3), NAMES[3], "300"))
    W.HOOK[0] = cap_hook
    r1 = str(n.GS.deposit(U(2), NAMES[2], "300"))
    W.HOOK[0] = None
    K.check(r1.startswith("+") and capres["inner"].startswith("-The guild bank can hold at most"), "X LOCK: a deposit over the cap counting the reserved 300 is refused (%r / %r)" % (r1, capres["inner"]))
    n.Cfg.MAX_BANK = cap0
    # refusals: take refused / null, add null -> nothing moved, reservation released, withdraw rolled back on disk
    before = n.state()
    pb = dict(W.PURSES["new"])
    W.FAIL["take"].add(str(U(2)))
    r = str(n.GS.deposit(U(2), NAMES[2], "100"))
    W.FAIL["take"].clear()
    K.check(r.startswith("-SkyyCoins could not take"), "X a refused take: %r" % r)
    W.PURSES["new"][str(U(2))] = 5
    r = str(n.GS.deposit(U(2), NAMES[2], "5"))
    W.PURSES["new"][str(U(2))] = pb[str(U(2))]
    K.check(r.startswith("+"), "X a deposit of the whole purse: %r" % r)
    before = n.state()
    pb = dict(W.PURSES["new"])
    W.FAIL["add"].add(str(U(1)))
    r = str(n.GS.withdraw(U(1), NAMES[1], "50"))
    W.FAIL["add"].clear()
    K.check(r.startswith("-SkyyCoins could not put the coins"), "X a refused add: %r" % r)
    K.eq(n.state(), before, "X a refused add: the bank and day count are back")
    K.eq(W.PURSES["new"], pb, "X a refused add: purses unchanged")
    gfile = os.path.join(n.d, "guilds", str(g7.id) + ".properties")
    K.check(("bank=%d" % int(g7.bank)) in open(gfile, encoding="latin-1").read(), "X a refused add: the restored bank is on disk")
    K.eq((int(g7.busy), int(g7.pendIn)), (0, 0), "X refusals release the reservation")
    # ---------------------------------------------------------------- WRITE
    GS = n.GS
    W.CUR[0] = "new"
    GS.flushDirty()
    now = int(Sys.currentTimeMillis())
    g7.flushedAt = now
    GS.addXp(g7.id, str(U(1)), 5)
    K.check(bool(g7.dirty), "X WRITE: XP marks the guild dirty")
    K.eq(int(GS.takeFlush(now + 30000).size()), 0, "X WRITE: an XP-only change waits (30 s < 60 s)")
    jobs = GS.takeFlush(now + 61000)
    K.eq(int(jobs.size()), 1, "X WRITE: ... and is snapshotted at 60 s")
    K.check(not bool(g7.dirty), "X WRITE: the snapshot clears dirty")
    gen_snap = int(jobs.get(0)[2])
    # the writer runs while the main thread HOLDS the GuildStore lock
    done = []
    with jpype.synchronized(GS.class_):
        th = threading.Thread(target=lambda: (GS.writeAll(jobs), done.append(1)))
        th.start()
        th.join(10)
    K.eq(done, [1], "X WRITE: the snapshot is written while another thread holds the GuildStore lock (the write is outside it)")
    K.eq(int(g7.written), gen_snap, "X WRITE: written = the snapshot's generation")
    # an older snapshot never lands over a newer write
    g7.flushedAt = 0
    GS.addXp(g7.id, str(U(1)), 7)
    old_jobs = GS.takeFlush(now + 200000)
    xp_old = int(g7.xp)
    GS.addXp(g7.id, str(U(1)), 11)
    K.check(GS.saveGuild(g7), "X WRITE: a newer saveGuild")
    xp_new = int(g7.xp)
    GS.writeAll(old_jobs)
    txt = open(gfile, encoding="latin-1").read()
    K.check(("xp=%d" % xp_new) in txt and ("xp=%d" % xp_old) not in txt, "X WRITE: a stale snapshot (older gen) is skipped - the file keeps the newer write")
    # urgent: a failed write retried at the next tick
    blocker = os.path.join(scratch, "blocker")
    open(blocker, "w").write("x")
    real_gdir = GS.GDIR
    GS.GDIR = W.Paths.get(os.path.join(blocker, "g"))
    g7.flushedAt = int(Sys.currentTimeMillis())
    K.check(not GS.saveGuild(g7), "X WRITE: a write that fails")
    K.check(bool(g7.dirty) and bool(g7.urgent), "X WRITE: ... marks dirty + urgent")
    jobs = GS.takeFlush(int(Sys.currentTimeMillis()))
    K.eq(int(jobs.size()), 1, "X WRITE: an urgent guild goes at the next tick (no 60 s wait)")
    GS.writeAll(jobs)
    K.check(bool(g7.urgent), "X WRITE: writeFailed marks it urgent again")
    GS.GDIR = real_gdir
    GS.submitWrites(GS.takeFlush(int(Sys.currentTimeMillis())))
    K.check(not bool(g7.dirty) and ("xp=%d" % int(g7.xp)) in open(gfile, encoding="latin-1").read(), "X WRITE: submitWrites without a writer writes inline")
    # the writer thread
    GW = JClass(PKG + "GWriter", loader=n.L)
    th = GW(None).newThread(JClass("java.lang.Thread")())
    K.check(str(th.getName()) == "SkyyGuilds-IO" and th.isDaemon(), "X WRITE: SkyyGuilds-IO, daemon")
    ex = JClass("java.util.concurrent.Executors").newSingleThreadExecutor(GW(None))
    GS.IO = ex
    g7.flushedAt = 0
    GS.addXp(g7.id, str(U(1)), 13)
    GS.submitWrites(GS.takeFlush(int(Sys.currentTimeMillis())))
    GS.stopIO()
    K.check(GS.IO is None and ex.isShutdown() and ("xp=%d" % int(g7.xp)) in open(gfile, encoding="latin-1").read(), "X WRITE: the writer wrote, stopIO stopped it")
    GW(None).run()
    # a disbanded (archived) guild's file is never recreated by a stale snapshot
    g7.flushedAt = 0
    GS.addXp(g7.id, str(U(1)), 3)
    stale = GS.takeFlush(int(Sys.currentTimeMillis()) + 10 ** 6)
    W.PURSES["new"] = {k: v for k, v in W.PURSES["new"].items()}
    r = str(GS.disband(U(1), NAMES[1], True))
    K.check(r.startswith("+"), "X WRITE: disband: %r" % r)
    GS.writeAll(stale)
    K.check(not os.path.exists(gfile), "X WRITE: the stale snapshot did not bring the disbanded guild's file back")
    K.check(len(glob.glob(os.path.join(n.d, "guilds", "deleted", str(g7.id) + "-*.properties"))) == 1, "X WRITE: the archive is there")
    # ---------------------------------------------------------------- PUB: publish on change
    for gg in (o, n):
        W.CUR[0] = gg.k
        gg.GS.create(U(4), NAMES[4], "PubGuild")
        for i in (5, 6, 7):
            gg.GS.invite(U(4), NAMES[4], NAMES[i])
            gg.GS.accept(U(i), NAMES[i])
    W.online([4, 5, 6, 8])
    vals = {}
    for gg in (o, n):
        W.CUR[0] = gg.k
        for i in NAMES:
            br.remove("guild:info:" + str(U(i)))
            br.remove("guild:" + str(U(i)))
        gg.Tick().run()
        vals[gg.k] = {str(x): (None if br.get(x) is None else str(br.get(x))) for x in ["guild:info:" + str(U(i)) for i in (4, 5, 6, 7, 8)] + ["guild:" + str(U(i)) for i in (4, 5, 6, 7, 8)]}
    K.eq(vals["new"], vals["old"], "X PUB: GuildTick publishes the same guild:<uuid> / guild:info:<uuid> on both jars")
    K.check(any(v and "|3|4|" in v for v in vals["new"].values()), "X PUB: the online count (3 of 4 online) is in the info: %s" % [v for v in vals["new"].values() if v][:2])
    cm = counting_map(br)
    W.CUR[0] = "new"
    n.Tick().run()                 # the shared test bridge last held 0.1.6's values: settle on 0.1.7's
    n.GS.BRIDGE = cm
    n.Tick().run()
    K.eq({k: v for k, v in cm.puts.items() if k.startswith("guild:")}, {}, "X PUB: a tick with nothing changed puts no guild:* value")
    gp = n.GS.guildOf(str(U(4)))
    cm.puts.clear()
    n.GS.addXp(gp.id, str(U(4)), 500)
    K.check(cm.puts.get("guild:info:" + str(U(5)), 0) == 1, "X PUB: an XP change re-puts each member's info once")
    cm.puts.clear()
    W.online([4, 5, 6, 7, 8])
    n.Tick().run()
    K.check(cm.puts.get("guild:info:" + str(U(7)), 0) == 1 and cm.puts.get("guild:info:" + str(U(4)), 0) == 1, "X PUB: an online-count change re-puts the info")
    K.eq(int(gp.onl), 4, "X PUB: setOnline counted 4 online members")
    br.remove("guild:info:" + str(U(5)))
    cm.puts.clear()
    n.Tick().run()
    K.eq(sorted(k for k in cm.puts if k.startswith("guild:info:")), ["guild:info:" + str(U(5))], "X PUB: a removed value is put back (and only it)")
    n.GS.BRIDGE = br
    K.check(n.GS.touch(U(4), NAMES[4]) and not n.GS.touch(U(8), NAMES[8]), "X PUB: touch (member / not)")
    # ---------------------------------------------------------------- REAL SkyyCoins 0.1.6
    Lc = loader_for(COINS_JAR)
    CS = JClass("com.skyy.coins.CoinStore", loader=Lc)
    CS.DIR = W.Paths.get(os.path.join(scratch, "coins", "balances"))
    CS.JOURNAL = W.Paths.get(os.path.join(scratch, "coins", "balances-journal.properties"))
    Fn = JClass("com.skyy.coins.CoinFn", loader=Lc)
    for m in ("get", "add", "take", "flush"):
        br.put("coins:fn:" + m, Fn(m))
    for i in (4, 5, 6, 7):
        CS.set(U(i), 10000)
    W.CUR[0] = "new"
    rd = str(n.GS.deposit(U(5), NAMES[5], "2500"))
    p5 = os.path.join(scratch, "coins", "balances", str(U(5)) + ".properties")
    K.check(os.path.exists(p5) and "balance=7500" in open(p5).read(), "X REAL/FIX: the purse file holds the deposit right after it (coins:fn:flush)")
    rw = str(n.GS.withdraw(U(4), NAMES[4], "1000"))
    p4 = os.path.join(scratch, "coins", "balances", str(U(4)) + ".properties")
    K.check("balance=" in open(p4).read() and int([l for l in open(p4).read().splitlines() if l.startswith("balance=")][0].split("=")[1]) == int(CS.get(U(4))),
            "X REAL/FIX: the purse file holds the withdraw right after it")
    n.GS.leave(U(5), NAMES[5], False)
    rl = str(n.GS.leave(U(5), NAMES[5], True))
    CS.flushNow()
    bal = {}
    for i in (4, 5, 6, 7):
        p = os.path.join(scratch, "coins", "balances", str(U(i)) + ".properties")
        bal[i] = int([l for l in open(p).read().splitlines() if l.startswith("balance=")][0].split("=")[1])
    gp = n.GS.guildOf(str(U(4)))
    K.check(rd.startswith("+") and rw.startswith("+") and rl.startswith("+"), "X REAL: deposit / withdraw / leave with a refund on the real ledger: %r %r %r" % (rd[:40], rw[:40], rl[:60]))
    K.eq(sum(bal.values()) + int(gp.bank), 40000, "X REAL: purses on disk + bank = the coins that existed")
    K.eq(bal[5], 10000 - 2500 + 875, "X REAL: the leaver got 35% of 2,500 back")
    br.remove("coins:fn:flush")
    W.coins_on()
    # ---------------------------------------------------------------- FIX (round E)
    from jpype import JImplements, JOverride
    ev = []
    W.CUR[0] = "new"
    W.online(list(NAMES))
    for i in (1, 2, 3):
        W.PURSES["new"][str(U(i))] = 50000
    K.check(str(n.GS.create(U(1), NAMES[1], "FixGuild")).startswith("+"), "X FIX: a fresh guild (LockGuild was disbanded above)")
    for i in (2, 3):
        n.GS.invite(U(1), NAMES[1], NAMES[i])
        n.GS.accept(U(i), NAMES[i])
    n.GS.deposit(U(3), NAMES[3], "1000")
    g7 = n.GS.guildOf(str(U(1)))
    K.eq(int(g7.members.size()), 3, "X FIX: 3 members")
    gfile = os.path.join(n.d, "guilds", str(g7.id) + ".properties")

    def bankfile():
        return [l for l in open(gfile, encoding="latin-1").read().splitlines() if l.startswith("bank=")][0]

    @JImplements("java.util.function.Function")
    class FlushFn:
        @JOverride
        def apply(self, a):
            ev.append(("flush", bankfile(), int(g7.bank)))
            return JClass("java.lang.Integer").valueOf(1)
    W.BR.put("coins:fn:flush", FlushFn())
    W.HOOK[0] = lambda kind, u, amount: ev.append((kind, u, amount))
    b0 = bankfile()
    r = str(n.GS.deposit(U(2), NAMES[2], "40"))
    K.check(r.startswith("+"), "X FIX: deposit %r" % r)
    K.eq([e[0] for e in ev], ["take", "flush"], "X FIX: deposit = take, then coins:fn:flush")
    K.eq(ev[1][1], b0, "X FIX: the purse is flushed BEFORE the guild bank file is credited")
    K.check(bankfile() == "bank=%d" % int(g7.bank) and bankfile() != b0, "X FIX: ... and the bank file is credited after")
    del ev[:]
    r = str(n.GS.withdraw(U(1), NAMES[1], "30"))
    K.check(r.startswith("+"), "X FIX: withdraw %r" % r)
    K.eq([e[0] for e in ev], ["add", "flush"], "X FIX: withdraw = add, then coins:fn:flush")
    K.eq(ev[1][1], "bank=%d" % int(g7.bank), "X FIX: the bank file was already debited when the purse is flushed")
    del ev[:]
    W.FAIL["take"].add(str(U(2)))
    r = str(n.GS.deposit(U(2), NAMES[2], "10"))
    W.FAIL["take"].clear()
    pr0 = dict(W.PURSES["new"])
    W.PURSES["new"][str(U(3))] = 0
    r2 = str(n.GS.deposit(U(3), NAMES[3], "10"))
    W.PURSES["new"].update(pr0)
    K.check("flush" not in [e[0] for e in ev] and r.startswith("-") and r2.startswith("-"), "X FIX: a refused / failed take is not flushed (%r / %r)" % (r, r2))
    # withdraw #1's add refused while withdraw #2 of the same member went through: #2's day count stays
    W.HOOK[0] = None
    W.BR.remove("coins:fn:flush")
    m2 = g7.member(str(U(2)))
    oldLim = int(g7.limMember)
    g7.limMember = 1000
    m2.wdDay = 0
    m2.wdUsed = 0
    bank0 = int(g7.bank)
    inner = {}

    def wd_hook(kind, u, amount):
        if kind == "add" and u == str(U(2)) and "r2" not in inner:
            inner["r2"] = "running"
            W.FAIL["add"].discard(str(U(2)))
            inner["r2"] = str(n.GS.withdraw(U(2), NAMES[2], "100"))
            W.FAIL["add"].add(str(U(2)))
    W.HOOK[0] = wd_hook
    W.FAIL["add"].add(str(U(2)))
    r1 = str(n.GS.withdraw(U(2), NAMES[2], "150"))
    W.FAIL["add"].clear()
    W.HOOK[0] = None
    K.check(r1.startswith("-SkyyCoins could not put") and inner.get("r2", "").startswith("+"), "X FIX: #1 refused, #2 paid (%r / %r)" % (r1[:50], inner.get("r2", "")[:50]))
    K.eq((int(m2.wdDay), int(m2.wdUsed)), (1234, 100), "X FIX: the day count keeps withdraw #2's 100 (0.1.6's restore would set 0)")
    K.eq(int(g7.bank), bank0 - 100, "X FIX: the bank lost only #2's 100")
    K.check(("wd.%s=1234|100" % str(U(2))) in open(gfile, encoding="latin-1").read(), "X FIX: ... and that is on disk")
    m2.wdUsed = 0
    W.FAIL["add"].add(str(U(2)))
    r3 = str(n.GS.withdraw(U(2), NAMES[2], "50"))
    W.FAIL["add"].clear()
    K.eq((r3[:25], int(m2.wdDay), int(m2.wdUsed)), ("-SkyyCoins could not put ", 1234, 0), "X FIX: a lone refused add restores the exact old count (0.1.6)")
    g7.limMember = oldLim
    # level curve change -> guild:info rebuilt without XP
    W.online([1, 2, 3])
    n.GS.touch(U(1), NAMES[1])
    i0 = str(W.BR.get("guild:info:" + str(U(1))))
    b0c = int(n.Cfg.BASE)
    n.Cfg.BASE = b0c + 977
    n.GS.touch(U(1), NAMES[1])
    i1 = str(W.BR.get("guild:info:" + str(U(1))))
    n.Cfg.BASE = b0c
    n.GS.touch(U(1), NAMES[1])
    i2 = str(W.BR.get("guild:info:" + str(U(1))))
    K.check(i1 != i0 and i2 == i0, "X FIX: a level-curve change rebuilds guild:info (%r -> %r)" % (i0[:60], i1[:60]))
    K.save()


def counting_map(real):
    from jpype import JImplements, JOverride

    @JImplements("java.util.Map")
    class CountMap(object):
        def __init__(self):
            self.puts = {}

        @JOverride
        def size(self): return real.size()
        @JOverride
        def isEmpty(self): return real.isEmpty()
        @JOverride
        def containsKey(self, k): return real.containsKey(k)
        @JOverride
        def containsValue(self, v): return real.containsValue(v)
        @JOverride
        def get(self, k): return real.get(k)

        @JOverride
        def put(self, k, v):
            self.puts[str(k)] = self.puts.get(str(k), 0) + 1
            return real.put(k, v)
        @JOverride
        def remove(self, k): return real.remove(k)
        @JOverride
        def putAll(self, m): return real.putAll(m)
        @JOverride
        def clear(self): return real.clear()
        @JOverride
        def keySet(self): return real.keySet()
        @JOverride
        def values(self): return real.values()
        @JOverride
        def entrySet(self): return real.entrySet()
        @JOverride
        def equals(self, o): return real.equals(o)
        @JOverride
        def hashCode(self): return real.hashCode()
    return CountMap()


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    W = World(scratch)
    d6 = os.path.join(os.path.dirname(home), "live6")
    shutil.copytree(home, d6)
    b6, b7 = HK.tree_hash(d6), HK.tree_hash(home)
    for start in (1, 2):
        o, n = G(W, OLD_JAR, d6, "old"), G(W, jar, home, "new")
        o.start()
        vo = {k: str(v) for k, v in dict((str(k), W.BR.get(k)) for k in W.BR.keySet()).items() if k.startswith("guild:")}
        n.start()
        vn = {k: str(v) for k, v in dict((str(k), W.BR.get(k)) for k in W.BR.keySet()).items() if k.startswith("guild:")}
        K.eq(n.state(), o.state(), "D%d: the same guilds, banks, members, nets and logs" % start)
        K.eq(vn, vo, "D%d: the same published guild values" % start)
        o.GS.flushDirty()
        n.GS.flushDirty()
        K.notes.append("D%d: %d guilds" % (start, len(n.state())))
    a6, a7 = HK.tree_hash(d6), HK.tree_hash(home)
    ch6 = sorted(k for k in set(b6) | set(a6) if b6.get(k) != a6.get(k))
    ch7 = sorted(k for k in set(b7) | set(a7) if b7.get(k) != a7.get(k))
    K.eq(ch7, ch6, "D: 0.1.7 changes exactly the files 0.1.6 changes on two starts (%s)" % ch6)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyGuilds", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyGuilds"))
