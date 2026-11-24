"""Harness for SkyyGuilds 0.1.14 (tools/guilds_0_1_14_patch.py): the bridge guild:fn:act (the guild page's clicks for SkyyMenu's new Social
tab). Build first: python tools/guilds_0_1_14_patch.py && python SkyyGuilds/build_skyyguilds_0.1.14.py

    python SkyyGuilds/test_skyyguilds_0.1.14.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; a fake Universe (Unsafe-allocated) holds the online players, as test_skyyguilds_0.1.7.py):
  S     static   the patch re-runs to identical bytes, line endings kept, one class added (GuildActFn), no new command / system; setup puts
                 guild:fn:act, shutdown sets CLOSED first and removes the key
  A / C / AA     -Xverify:all, class compare 0.1.13 -> 0.1.14 (only the listed members differ, GuildActFn added), engine-access audit
  MIG / LVL      EVERY 0.1.13 check again on the 0.1.14 jar (test_skyyguilds_0.1.13.py's run_mig / run_lvl, executed as they are; only the
                 WHO text "SkyyGuilds <version>" follows the running version, as it did in 0.1.13)
  TWIN  exec     TWO GuildStores of the 0.1.14 jar (own class loaders, own data folders, own fake purses), the same players online:
                 world P is driven through the REAL GuildPage.handleDataEvent (page.info = the page's answer), world B through
                 guild:fn:act (state read first for the token + profile key, like the Menu). A scripted run (create / every refusal /
                 invite / decline / accept / deposit / withdraw + limits / hints / promote / demote / kick + transfer + leave + disband two
                 presses) and 600 random clicks: the SAME answer after every step, the same guilds / members / ranks / banks / nets / logs /
                 day counts and the same purses; coins conserved
  ACT   exec     the bridge's own rules on world B: state lines (header 26 fields, n / c / m / l / i lines, a '|' in a name kept, caps),
                 stale token / changed profile key / double click within 350 ms / offline / closing / unknown op / bad arguments / a
                 non-UUID target, arm expiry + an arm dropped by another op + an arm from another profile, profile:busy deposit /
                 withdraw, a refused coins:fn:take, the server stopping DURING a deposit (completes, conserved, then refused), two
                 threads depositing at once (conserved), refresh; the bytecode calls the page's GuildStore methods
  live  D        start TWICE on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGuilds (GNcMig -> GP5Mig -> GCfg.load -> loadAll): no
                 file changes, the guild loads, guild:fn:act state answers for its Leader
Scratch: tools/dev/scratch/guild1/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, json, random, shutil, subprocess, threading, time, glob, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "guild1", "harness")]
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.1.14", "0.1.13"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGuilds-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGuilds-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyguilds_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyguilds_%s.py" % OLD)
OLD_HARNESS = os.path.join(HERE, "test_skyyguilds_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "guilds_0_1_14_patch.py")
PKG = "com.skyy.guilds."
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGuilds")
EXPECT = {
    "SkyyGuildsPlugin": ["~m setup", "~m shutdown"],       # + guild:fn:act / CLOSED (and the version in the ready line)
    # the version text only ("SkyyGuilds 0.1.14" inlined: the default config header, the migrations' WHO, the kit's export header)
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "GCfg": ["~m load"],
    "GNcMig": ["~m logLine", "~m migrate"],
    "GP5Mig": ["~m logLine", "~m migrate"],
}
NAMES = {1: "Steve", 2: "Alex", 3: "Bea", 4: "Cid", 5: "Dot"}


# ---------------------------------------------------------------------------------------------------------------- 0.1.13's checks
def _old():
    src = open(OLD_HARNESS, encoding="utf8").read()
    src = src[:src.index("\nHK.run(")]
    assert src.count('"SkyyGuilds 0.1.13"') == 2, "0.1.13 harness: the two WHO checks"
    src = src.replace('"SkyyGuilds 0.1.13"', '"SkyyGuilds %s"' % VERSION)
    ns = {"__file__": OLD_HARNESS, "__name__": "test_skyyguilds_0_1_13"}
    exec(compile(src, OLD_HARNESS, "exec"), ns)
    return ns


def run_mig13(out, jar, scratch, home):
    _old()["run_mig"](out, jar, scratch, home)


def run_lvl13(out, jar, scratch, home):
    _old()["run_lvl"](out, jar, scratch, home)


# ---------------------------------------------------------------------------------------------------------------- static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGuilds 0.1.14 - build script') and g.count('VERSION = "0.1.14"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("makeClass(") - o.count("makeClass("), 1, "S one class added (GuildActFn)")
    su = g[g.index("public void setup() {"):]
    K.check('bridge().put("guild:fn:act", new @PKG@.GuildActFn())' in su[:su.index("protected void shutdown()")], "S setup puts guild:fn:act")
    sd = su[su.index("protected void shutdown() {"):]
    K.check(sd.index("GuildActFn.CLOSED = true;") < sd.index("ticker.cancel") and 'bridge().remove("guild:fn:act")' in sd, "S shutdown: CLOSED first, key removed")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- the worlds
class World(object):
    """fake Universe + players; the bridge with switchable fake purses (one per world), a profile key per player, failure switches"""

    def __init__(self):
        from jpype import JClass, JImplements, JOverride
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
        self.REFS = {}

        def pref(n):
            if n not in self.REFS:
                p = U.allocateInstance(PR.class_)
                setf(p, PR, "uuid", self.uid(n))
                setf(p, PR, "username", NAMES.get(n, "P%d" % n))
                setf(p, PR, "holder", holder)
                self.REFS[n] = p
            return self.REFS[n]
        self.pref = pref
        self.BR = self.CHM()
        self.System.getProperties().put("skyy.bridge", self.BR)
        self.PURSES = {}
        self.CUR = ["P"]
        self.FAIL = {"add": set(), "take": set(), "get": set()}
        self.HOOK = [None]
        self.PK = {}
        self.LOCK = threading.Lock()
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
                with W.LOCK:
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
                with W.LOCK:
                    P = W.PURSES[W.CUR[0]]
                    if P.get(u, 0) < n:
                        return W.Boolean.FALSE
                    P[u] = P.get(u, 0) - n
                    return W.Boolean.TRUE

        @JImplements("java.util.function.Function")
        class ProfKey:
            @JOverride
            def apply(self, u):
                return W.PK.get(str(u), str(u))
        for key, f in (("coins:fn:get", CoinsGet()), ("coins:fn:add", CoinsAdd()), ("coins:fn:take", CoinsTake()), ("profile:fn:key", ProfKey())):
            self.BR.put(key, f)
        self.KEEP = []

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


class GW(object):
    """one GuildStore of the jar on its own folder (own class loader)"""

    def __init__(self, W, jar, d, k):
        from jpype import JClass
        self.W, self.k, self.d = W, k, d
        self.L = loader_for(jar)
        g = lambda n: JClass(PKG + n, loader=self.L)
        self.GS, self.Cfg, self.Page, self.Act = g("GuildStore"), g("GCfg"), g("GuildPage"), g("GuildActFn")
        self.GS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyGuildsTest")
        os.makedirs(os.path.join(d, "guilds"), exist_ok=True)
        P = W.Paths
        self.GS.DIR = P.get(d)
        self.GS.GDIR = P.get(os.path.join(d, "guilds"))
        self.Cfg.FILE = P.get(os.path.join(d, "config.properties"))
        W.PURSES[k] = {}
        self.pages = {}
        self.fn = self.Act()

    def start(self):
        self.W.CUR[0] = self.k
        self.Cfg.load()
        self.GS.loadAll()
        self.GS.DAY = 1234
        self.GS.DAY_READ = int(self.W.System.currentTimeMillis()) + 10 ** 9

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
                              [re.sub(r"^\d+\|", "", str(x)) for x in g.log], int(g.busy), int(g.pendIn))
        inv = {}
        ii = self.GS.INVITES.keySet().iterator()
        while ii.hasNext():
            kk = ii.next()
            v = self.GS.INVITES.get(kk)
            inv[str(kk)] = (str(v[0]), str(v[1]))
        return out, inv

    # the guild page: its real click handler (page.info = the answer line it shows)
    def page(self, n):
        if n not in self.pages:
            self.pages[n] = self.Page(self.W.pref(n))
        return self.pages[n]

    def click(self, n, d, target=None):
        self.W.CUR[0] = self.k
        pg = self.page(n)
        if target is not None:
            from jpype import JClass
            al = JClass("java.util.ArrayList")()
            al.add(str(self.W.uid(target)))
            pg.rowIds = al
        pg.info = "<none>"
        pg.handleDataEvent(None, None, json.dumps(d))
        return str(pg.info)

    # the bridge: state first (token + profile key, as the Menu reads them), then the op
    def read(self, n, arg=None):
        self.W.CUR[0] = self.k
        return self.call(["state", self.W.uid(n), None, None, arg])

    def head(self, n):
        return self.read(n).split("\n")[0].split("|")

    def call(self, a):
        from jpype import JArray, JClass
        self.W.CUR[0] = self.k
        return str(self.fn.apply(JArray(JClass("java.lang.Object"))(a)))

    def op(self, n, op, arg=None, clear=True):
        h = self.head(n)
        if clear:
            self.Act.LASTOP.clear()    # the double-click guard is checked on its own (ACT); twins click as fast as the harness runs
        return self.call([op, self.W.uid(n), h[2], h[3], arg])


# page click payload <-> bridge op (the page's own keys: GuildPage.handleDataEvent)
def page_data(op, arg):
    if op == "create":
        return {"a": "create", "@GName": arg}, None
    if op in ("accept", "decline", "leave", "disband"):
        return {"a": op}, None
    if op == "invite":
        return {"a": "invite", "@GInvite": arg}, None
    if op in ("deposit", "withdraw"):
        return {"a": op, "@GAmount": arg}, None
    if op == "amounthint":
        return {"a": "amount", "@GAmount": arg}, None
    if op in ("limitadmin", "limitmember"):
        return {"a": "limadmin" if op == "limitadmin" else "limmember", "@GLimit": arg}, None
    if op == "limithint":
        return {"a": "limit", "@GLimit": arg}, None
    if op in ("promote", "demote", "kick", "transfer"):
        return {"a": ("lead" if op == "transfer" else op) + ":0"}, arg
    raise ValueError(op)


def run_twin(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    W = World()
    P = GW(W, jar, os.path.join(scratch, "twinP"), "P")
    Bw = GW(W, jar, os.path.join(scratch, "twinB"), "B")
    P.start()
    Bw.start()
    for k in ("P", "B"):
        for i in NAMES:
            W.PURSES[k][str(W.uid(i))] = 50000
    W.online(list(NAMES))
    U = W.uid
    TOTAL = sum(W.PURSES["B"].values())
    steps, diffs = [0], []

    def coins(gw):
        return sum(W.PURSES[gw.k].values()) + sum(int(g.bank) for g in gw.GS.GUILDS.values())

    def twin(n, op, arg=None, target=None, want=None):
        d, _t = page_data(op, arg)
        tu = target
        rp = P.click(n, d, target=tu)
        rb = Bw.op(n, op, str(U(tu)) if tu is not None else arg)
        steps[0] += 1
        sp, sb = P.state(), Bw.state()
        same = rp == rb and sp == sb and W.PURSES["P"] == W.PURSES["B"]
        if not same and len(diffs) < 6:
            diffs.append((n, op, arg, tu, rp, rb, sp == sb, W.PURSES["P"] == W.PURSES["B"]))
            print("   DIFF", n, op, arg, tu, "| page:", rp[:160], "| bridge:", rb[:160], "| state same:", sp == sb)
        if want is not None:
            K.check(rb.startswith(want[0]) and want[1] in rb, "TWIN %s %s %s %s: %r (want %r)" % (NAMES[n], op, arg, tu, rb[:200], want))
        return rb
    # ---- scripted: every page action, every refusal the page can give
    twin(1, "create", "x", want=("-", ""))
    twin(1, "create", "Test|Guild", want=("+You founded Test|Guild", ""))
    twin(1, "create", "Other", want=("-You are already in a guild", ""))
    twin(2, "invite", "Bea", want=("-You are not in a guild", ""))
    twin(1, "invite", "", want=("-Type the name", ""))
    twin(1, "invite", "Nobody", want=("-No online player called Nobody", ""))
    twin(1, "invite", "Steve", want=("-You can't invite yourself", ""))
    twin(1, "invite", "Alex", want=("+Invited Alex", ""))
    twin(2, "decline", want=("=You declined", ""))
    twin(2, "decline", want=("-You have no guild invite", ""))
    twin(2, "accept", want=("-You have no guild invite", ""))
    twin(1, "invite", "Alex")
    twin(2, "accept", want=("+Welcome to Test|Guild", ""))
    twin(2, "accept", want=("-You are already in a guild", ""))
    twin(1, "invite", "Alex", want=("-Alex is already in your guild", ""))
    for who in (3, 4):
        twin(1, "invite", NAMES[who])
        twin(who, "accept", want=("+Welcome", ""))
    twin(2, "deposit", "1k", want=("+Deposited 1000 coins", ""))
    twin(2, "deposit", "abc", want=("-That is not an amount", ""))
    twin(2, "deposit", "0", want=("-Nothing to deposit", ""))
    twin(1, "deposit", "2.5k", want=("+Deposited 2500", ""))
    twin(3, "deposit", "999999999", want=("-Not enough coins", ""))
    twin(4, "deposit", "4k", want=("+Deposited 4000", ""))
    twin(5, "deposit", "1k", want=("-You are not in a guild", ""))
    twin(2, "withdraw", "10", want=("-Members can't withdraw", ""))
    twin(2, "amounthint", "", want=("=Type an amount", "Deposit."))
    twin(2, "amounthint", "2k", want=("=Click Deposit to move 2k coins", ""))
    twin(1, "amounthint", "12345678901234567890", want=("=Click Deposit or Withdraw to move 1234567890123456 coins", ""))
    twin(1, "limithint", "", want=("=Type a daily limit", ""))
    twin(1, "limithint", "5k", want=("=Click Set Admin limit or Set Member limit to use 5k", ""))
    twin(2, "limitmember", "500", want=("-Only the Leader can set", ""))
    twin(1, "limitmember", "zzz", want=("-That is not a limit", ""))
    twin(1, "limitmember", "500", want=("+Members: 500 coins per game day", ""))
    twin(1, "limitadmin", "none", want=("=Admins already have", ""))
    twin(2, "withdraw", "600", want=("-You can take 500 more coins today", ""))
    twin(2, "withdraw", "500", want=("+Withdrew 500 coins", "Today: 500 / 500"))
    twin(2, "withdraw", "1", want=("-You reached today's withdraw limit", ""))
    twin(1, "withdraw", "100", want=("+Withdrew 100 coins", ""))
    twin(1, "withdraw", "99999999", want=("-The guild bank only has", ""))
    twin(1, "promote", target=2, want=("+Alex is now an Admin", ""))
    twin(1, "promote", target=2, want=("-Alex is already an Admin", ""))
    twin(1, "demote", target=2, want=("+Alex is now a Member", ""))
    twin(1, "demote", target=2, want=("-Alex is already a Member", ""))
    twin(1, "demote", target=1, want=("-The Leader can't be demoted", ""))
    twin(3, "promote", target=2, want=("-Only the Leader can promote", ""))
    twin(1, "promote", target=3, want=("+Bea is now an Admin", ""))
    twin(1, "promote", target=5, want=("-Nobody called", ""))
    twin(3, "kick", target=2, want=("=Click Sure? within 10 s to remove Alex", "gets back"))
    twin(3, "kick", target=2, want=("+Removed Alex from the guild.", "got back"))
    twin(3, "kick", target=1, want=("=Click Sure?", ""))
    twin(3, "kick", target=1, want=("-Admins can only kick Members", ""))
    twin(4, "kick", target=3, want=("=Click Sure?", ""))
    twin(4, "kick", target=3, want=("-Only the Leader and Admins can kick", ""))
    twin(1, "kick", target=1, want=("=Click Sure?", ""))
    twin(1, "kick", target=1, want=("-You can't kick yourself", ""))
    twin(1, "transfer", target=3, want=("=Click Confirm? within 10 s to make Bea the Leader", ""))
    twin(1, "amounthint", "")                                   # another click drops the armed Confirm (the page: this.confirm = "")
    twin(1, "transfer", target=3, want=("=Click Confirm?", ""))
    twin(1, "transfer", target=3, want=("+Bea is now the Leader of Test|Guild. You are an Admin.", ""))
    twin(4, "leave", want=("=Click Leave again within 10 s to leave Test|Guild.", "You get back"))
    twin(4, "leave", want=("+You left Test|Guild.", "got back"))
    twin(4, "leave", want=("-You are not in a guild", ""))
    twin(1, "disband", want=("-Only the Leader can disband", ""))
    twin(3, "disband", want=("=Disbanding deletes Test|Guild for all 2 members", ""))
    twin(3, "disband", want=("+Test|Guild is disbanded.", ""))
    twin(3, "disband", want=("-You are not in a guild", ""))
    twin(2, "create", "Solo", want=("+You founded Solo", ""))
    twin(2, "deposit", "700")
    twin(2, "leave", want=("=You are the last member: leaving DISBANDS Solo and pays the bank's 700 coins", ""))
    twin(2, "leave", want=("+Solo is disbanded", ""))
    K.check(not diffs, "TWIN scripted: %d steps, the page and guild:fn:act give the same answers, guilds and purses (%s)" % (steps[0], diffs[:2]))
    K.eq((coins(P), coins(Bw)), (TOTAL, TOTAL), "TWIN scripted: coins conserved in both worlds")
    # ---- random clicks: 600 steps, both worlds
    rnd = random.Random(1424)
    s0 = steps[0]
    ops = ["create", "invite", "accept", "decline", "deposit", "withdraw", "limitadmin", "limitmember", "promote", "demote", "kick", "kick",
           "transfer", "transfer", "leave", "leave", "disband", "disband", "amounthint", "limithint"]
    amts = ["500", "2k", "all", "1", "100000", "abc", "half", "0", "300", "1k", "none"]
    for _i in range(600):
        op = rnd.choice(ops)
        n = rnd.choice(list(NAMES))
        t = rnd.choice(list(NAMES))
        if op == "create":
            twin(n, op, "Guild %d" % rnd.randint(1, 3))
        elif op == "invite":
            twin(n, op, NAMES[t])
        elif op in ("accept", "decline", "leave", "disband"):
            twin(n, op)
        elif op in ("promote", "demote", "kick", "transfer"):
            twin(n, op, target=t)
        else:
            twin(n, op, rnd.choice(amts))
    K.check(not diffs, "TWIN random: %d clicks, the same answers, guilds and purses after every one (%s)" % (steps[0] - s0, diffs[:2]))
    K.eq((coins(P), coins(Bw)), (TOTAL, TOTAL), "TWIN random: coins conserved in both worlds")
    K.notes.append("TWIN: %d steps compared" % steps[0])
    K.save()


# ---------------------------------------------------------------------------------------------------------------- ACT (the bridge's own rules)
def run_act(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    W = World()
    G = GW(W, jar, os.path.join(scratch, "act"), "B")
    G.start()
    for i in NAMES:
        W.PURSES["B"][str(W.uid(i))] = 50000
    W.online([1, 2, 3, 4])
    U = W.uid
    A = G.Act
    total = lambda: sum(W.PURSES["B"].values()) + sum(int(g.bank) for g in G.GS.GUILDS.values())
    T0 = total()
    # ---- state not in a guild (+ an invite line)
    h = G.head(1)
    K.check(len(h) == 26 and h[:5] == ["h", "0", "-", str(U(1)), "-1"] and h[14] == "25" and h[15] == "10" and h[20] == "300" and h[23:] == ["", "", ""],
            "ACT state alone: 26 fields, not in a guild, token -, the profile key, max 25, share 10, invites 300 s (%s)" % h)
    K.check(G.op(1, "create", "Ab|Cd Club").startswith("+You founded Ab|Cd Club"), "ACT create a name with '|'")
    G.op(1, "invite", "Alex")
    st = G.read(2).split("\n")
    K.check(len(st) == 2 and st[1].startswith("i|") and st[1].split("|", 6)[6] == "Ab|Cd Club" and st[1].split("|")[5] == "Steve"
            and 0 < int(st[1].split("|")[1]) <= 300, "ACT state: the invite line (seconds, inviter, the whole name) %s" % st[1:])
    G.op(2, "accept")
    for i in range(3):
        G.op(2, "deposit", str(100 + i))
    s = G.read(1).split("\n")
    h = s[0].split("|")
    gid = str(G.GS.gidOf(str(U(1))))
    K.check(len(h) == 26 and h[1:5] == ["1", gid, str(U(1)), "2"] and h[11] == "303" and h[13] == "2" and h[18] == "-1" and h[19] == "1",
            "ACT state in a guild: token = guild id, Leader, bank 303, 2 members, no limit (%s)" % h)
    K.check(s[1] == "n|Ab|Cd Club" and s[2] == "c|2|2|3|3", "ACT state: n (the whole name) + c lines (%s / %s)" % (s[1], s[2]))
    ms = [x.split("|") for x in s if x.startswith("m|")]
    K.check([m[1] for m in ms] == [str(U(1)), str(U(2))] and ms[0][2] == "2" and ms[1][7] == "Alex" and ms[1][6] == "303",
            "ACT state: m lines in the page's order (Leader first; Alex's contribution 303) %s" % ms)
    ls = [x.split("|", 4) for x in s if x.startswith("l|")]
    K.check(len(ls) == 3 and ls[0][4] == "deposited 102 coins" and ls[2][4] == "deposited 100 coins" and ls[0][3] == "Alex" and ls[0][2] == "303",
            "ACT state: l lines newest first (%s)" % ls)
    s2 = G.read(1, "1|1").split("\n")
    K.check(s2[2] == "c|1|2|1|3" and len([x for x in s2 if x[:2] in ("m|", "l|")]) == 2, "ACT state caps 1|1 (%s)" % s2[2])
    K.check(G.read(1, "junk|-5").split("\n")[2] == "c|2|2|0|3", "ACT state: junk cap = default, negative = 0")
    # ---- token / profile key / double click / offline / closing / unknown
    tok, pk = gid, str(U(2))
    call = lambda n, op, t, p, a=None: G.call([op, U(n), t, p, a])
    A.LASTOP.clear()
    b0 = int(G.GS.GUILDS.get(gid).bank)
    K.eq(call(2, "deposit", "-", pk, "50"), "=Your guild changed - look again. Nothing changed.", "ACT a stale token (another guild / none) = refused")
    K.eq(call(2, "deposit", None, pk, "50"), "=Your guild changed - look again. Nothing changed.", "ACT no token = refused")
    K.eq(call(2, "deposit", tok, pk + "-p2", "50"), "=Your profile changed - here is this profile's guild. Nothing changed.", "ACT a profile key that is not the active one = refused")
    K.eq(int(G.GS.GUILDS.get(gid).bank), b0, "ACT ... nothing moved")
    r1 = call(2, "deposit", tok, pk, "50")
    r2 = call(2, "deposit", tok, pk, "50")
    K.check(r1.startswith("+Deposited 50") and r2 == "=One moment." and int(G.GS.GUILDS.get(gid).bank) == b0 + 50, "ACT a double click within 350 ms deposits ONCE (%s / %s)" % (r1, r2))
    time.sleep(0.4)
    K.check(call(2, "deposit", tok, pk, "50").startswith("+Deposited 50"), "ACT the same deposit after 350 ms = a new deposit")
    K.eq(call(2, "deposit", tok, pk, "51")[:10], "+Deposited", "ACT another amount at once is not a double click")
    W.online([1, 3, 4])
    K.eq(call(2, "deposit", tok, pk, "52"), "-You are not online.", "ACT an offline player: refused")
    K.check(G.read(2).startswith("h|1|" + gid + "|"), "ACT ... state still answers offline")
    W.online([1, 2, 3, 4])
    A.CLOSED = True
    K.eq(call(2, "deposit", tok, pk, "53"), "-Guilds are shutting down (the server is stopping) - nothing changed.", "ACT closing: refused")
    K.check(G.read(2).startswith("h|1|"), "ACT closing: state still answers")
    A.CLOSED = False
    OA = JClass("java.lang.Object")
    K.check(call(2, "zzz", tok, pk) == "-Unknown guild action." and str(G.fn.apply(None)) == "-Unknown guild action." and str(G.fn.apply("x")) == "-Unknown guild action."
            and G.call(["state"]) == "-Unknown guild action." and G.call(["state", "not-a-uuid"]).startswith("-Something went wrong"),
            "ACT unknown op / bad arguments = a line (never throws)")
    for o_ in ("kick", "promote", "demote", "transfer"):
        K.eq(call(1, o_, tok, str(U(1)), "Alex"), "-That player is not in your guild any more.", "ACT %s by NAME (not a uuid) refused" % o_)
    K.eq(call(1, "kick", tok, str(U(1)), str(U(2)).upper()), "-That player is not in your guild any more.", "ACT an upper-case uuid refused")
    K.eq(call(1, "refresh", None, None), "", "ACT refresh answers '' (no token needed)")
    # ---- arms: expiry, dropped by another op, another profile, refresh
    G.op(1, "invite", "Bea")
    G.op(3, "accept")
    tb = str(U(3))
    r = G.op(1, "kick", tb)
    K.check(r.startswith("=Click Sure?") and G.head(1)[21] == "kick:" + tb and 9 <= int(G.head(1)[22]) <= 10, "ACT kick arms (state shows the arm + seconds) %s" % G.head(1)[21:23])
    A.ARM.get(str(U(1)))[3] = W.Long.valueOf(int(W.System.currentTimeMillis()) - 1)
    K.check(G.head(1)[21] == "" and G.op(1, "kick", tb).startswith("=Click Sure?") and G.GS.gidOf(tb) is not None, "ACT an expired arm asks again (Bea stays)")
    G.op(1, "amounthint", "")
    K.check(G.op(1, "kick", tb).startswith("=Click Sure?") and G.GS.gidOf(tb) is not None, "ACT an arm dropped by another click asks again")
    K.eq(G.op(1, "refresh"), "", "ACT refresh")
    K.check(G.op(1, "kick", tb).startswith("=Click Sure?") and G.GS.gidOf(tb) is not None, "ACT refresh drops the arm")
    W.PK[str(U(1))] = str(U(1)) + "-p2"
    K.check(G.head(1)[21] == "" and G.op(1, "kick", tb).startswith("=Click Sure?") and G.GS.gidOf(tb) is not None,
            "ACT an arm from another profile never fires (asks again)")
    K.check(G.op(1, "transfer", tb).startswith("=Click Confirm?") and G.op(1, "kick", tb).startswith("=Click Sure?"), "ACT a transfer arm is not a kick arm")
    K.check(G.op(1, "kick", tb).startswith("+Removed Bea"), "ACT the second kick press within 10 s kicks")
    W.PK.pop(str(U(1)))
    A.LASTOP.clear()
    r1 = G.op(1, "leave", clear=False)
    h1 = G.head(1)
    r2 = G.call(["leave", U(1), h1[2], h1[3], None])
    K.check(r1.startswith("=Leaving makes Alex the new Leader") and r2 == "=One moment." and G.GS.gidOf(str(U(1))) is not None and G.head(1)[21] == "leave",
            "ACT a double click on Leave never confirms itself; the arm stays (%s / %s)" % (r1[:60], r2))
    # ---- coins: profile switch running, a refused take, the server stopping mid-deposit, two threads
    W.BR.put("profile:busy:" + str(U(2)), W.Boolean.TRUE)
    p2 = W.PURSES["B"][str(U(2))]
    b0 = int(G.GS.GUILDS.get(gid).bank)
    K.check(G.op(2, "deposit", "10").startswith("-A profile switch is running") and W.PURSES["B"][str(U(2))] == p2, "ACT deposit while profile:busy = refused, nothing moved")
    G.op(1, "limitmember", "none")
    K.check(G.op(2, "withdraw", "10").startswith("-Your profile changed (or a profile switch is running)") and W.PURSES["B"][str(U(2))] == p2
            and int(G.GS.GUILDS.get(gid).bank) == b0, "ACT withdraw while profile:busy = rolled back, nothing moved")
    W.BR.remove("profile:busy:" + str(U(2)))
    W.FAIL["take"].add(str(U(2)))
    K.check(G.op(2, "deposit", "10").startswith("-SkyyCoins could not take the coins") and int(G.GS.GUILDS.get(gid).bank) == b0, "ACT a refused coins:fn:take = nothing moved")
    W.FAIL["take"].clear()
    W.FAIL["add"].add(str(U(2)))
    K.check(G.op(2, "withdraw", "10").startswith("-SkyyCoins could not put the coins") and int(G.GS.GUILDS.get(gid).bank) == b0, "ACT a refused coins:fn:add = bank restored")
    W.FAIL["add"].clear()

    def stop_now(kind, u, n):
        A.CLOSED = True
    W.HOOK[0] = stop_now
    r = G.op(2, "deposit", "25")
    W.HOOK[0] = None
    K.check(r.startswith("+Deposited 25") and int(G.GS.GUILDS.get(gid).bank) == b0 + 25 and total() == T0 and int(G.GS.GUILDS.get(gid).busy) == 0,
            "ACT the server stopping DURING a deposit: it completes, coins conserved, no reservation left (%s)" % r[:60])
    K.check(G.op(2, "deposit", "25").startswith("-Guilds are shutting down"), "ACT ... the next op is refused")
    A.CLOSED = False
    errs = []

    def worker(k):
        try:
            for i in range(25):
                G.op(2 if k == 0 else 1, "deposit", str(10 + k * 100 + i), clear=False)
                G.op(1, "withdraw", str(5 + k), clear=False)
        except Exception as e:
            errs.append(str(e))
    th = [threading.Thread(target=worker, args=(k,)) for k in range(2)]
    for t in th:
        t.start()
    for t in th:
        t.join()
    K.check(not errs and total() == T0 and int(G.GS.GUILDS.get(gid).busy) == 0 and int(G.GS.GUILDS.get(gid).pendIn) == 0,
            "ACT two threads depositing / withdrawing at once: coins conserved, no reservation left (%s)" % errs[:2])
    K.eq(total(), T0, "ACT coins conserved over the whole phase")
    # ---- the bytecode: the ops call the page's GuildStore methods; the jar has no other new bridge key
    cb = zipfile.ZipFile(jar).read("com/skyy/guilds/GuildActFn.class")
    names = ("create", "accept", "decline", "invite", "deposit", "withdraw", "setLimit", "leaveWarning", "leave", "disbandWarning", "disband",
             "promote", "demote", "kick", "kickNote", "nameOfMember", "transfer", "canWithdraw", "snapshot", "inviteFor", "logParts", "levelInfo", "pkey")
    K.check(all(n_.encode() in cb for n_ in names) and b"com/skyy/guilds/GuildStore" in cb, "ACT bytecode: GuildActFn calls the page's GuildStore methods")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- live
def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar])
    System, CHM, Paths = JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.nio.file.Paths")
    System.getProperties().put("skyy.bridge", CHM())
    GS, Cfg, Mig, Nc, Act = (JClass(PKG + n) for n in ("GuildStore", "GCfg", "GP5Mig", "GNcMig", "GuildActFn"))
    GS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyGuildsTest")
    GS.DIR, GS.GDIR, Cfg.FILE = Paths.get(home), Paths.get(os.path.join(home, "guilds")), Paths.get(os.path.join(home, "config.properties"))

    def files():
        out_ = {}
        for p in sorted(glob.glob(os.path.join(home, "**", "*"), recursive=True)):
            if os.path.isfile(p):
                out_[os.path.relpath(p, home)] = open(p, "rb").read()
        return out_
    f0 = files()

    def start():
        Nc.migrate()
        Mig.migrate()
        Cfg.load()
        GS.GUILDS.clear()
        GS.BYNAME.clear()
        GS.BYPLAYER.clear()
        GS.loadAll()
    start()
    f1 = files()
    start()
    f2 = files()
    ch1 = sorted(k for k in set(f0) | set(f1) if f0.get(k) != f1.get(k))
    # Properties.store writes a "#<date>" comment line (1 s resolution): two starts that straddle a second differ only there,
    # so compare with that one line dropped - and check it really is the only difference
    import re as _re
    _DATE = _re.compile(rb"^#[A-Z][a-z]{2} [A-Z][a-z]{2} [ 0-9]\d \d\d:\d\d:\d\d [A-Za-z+0-9:-]+ \d{4}\r?$", _re.M)

    def nodate(d):
        return {k: (_DATE.sub(b"#<date>", v) if k.endswith(".properties") else v) for k, v in d.items()}
    K.check(nodate(f1) == nodate(f2), "D start 2 changes no file (only the store date comment may tick) (%s)"
            % sorted(k for k in set(f1) | set(f2) if nodate(f1).get(k) != nodate(f2).get(k)))
    K.check(nodate({"x.properties": b"#a\n#Sun Nov 22 15:04:09 MST 2026\nk=1\n"}) == nodate({"x.properties": b"#a\n#Mon Nov 23 01:00:00 MST 2026\nk=1\n"})
            and nodate({"x.properties": b"#Sun Nov 22 15:04:09 MST 2026\nk=1\n"}) != nodate({"x.properties": b"#Sun Nov 22 15:04:09 MST 2026\nk=2\n"}),
            "D date-comment filter: ignores only the date line, still sees a value change")
    K.check(all(k.startswith(("meta.properties", "players.properties", "guilds")) for k in ch1), "D start 1 rewrites only the guild store's own files: %s" % ch1)
    g_ids = [str(x) for x in GS.GUILDS.keySet()]
    print("   live guilds:", g_ids, "files changed by start 1:", ch1)
    K.check(len(g_ids) >= 1, "D the live guild(s) load: %s" % g_ids)
    fn = Act()
    for gid in g_ids:
        g = GS.GUILDS.get(gid)
        lead = g.leader()
        s = str(fn.apply(JArray(JClass("java.lang.Object"))(["state", lead.uid, None, None, None]))).split("\n")
        h = s[0].split("|")
        K.check(len(h) == 26 and h[1:3] == ["1", gid] and h[4] == "2" and s[1] == "n|" + str(g.name) and int(h[13]) == g.members.size()
                and int(h[11]) == int(g.bank), "D guild:fn:act state for %s's Leader %s: %s" % (gid, lead.name, s[0][:200]))
        print("   live state:", s[0][:160], "|", s[1])
    K.save()


HK.run(name="SkyyGuilds", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["GuildActFn"],
       phases=[("static", run_static), ("mig13", run_mig13), ("lvl13", run_lvl13), ("twin", run_twin), ("act", run_act), ("live", run_live)],
       script=__file__, live=(LIVE_DIR, "Skyy_SkyyGuilds"))
