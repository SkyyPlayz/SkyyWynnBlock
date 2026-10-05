"""SkyyParty 0.1.7 - bare-JVM harness for the TPA / Accept TPA buttons (Skyy 2026-10-03), copied forward from the 0.1.6 harness.

    python SkyyParty/test_skyyparty_0.1.7.py [--jar <SkyyParty-0.1.7.jar>] [--old <SkyyParty-0.1.6.jar>] [--dir <scratch folder>] [--keep]

Build the jar first (python SkyyParty/build_skyyparty_0.1.7.py). Child processes start fresh JVMs (the game's own JRE, -Xverify:all,
-XX:-UsePerfData, HytaleServer.jar + ONE mod jar on the classpath; javassist only for the bytecode step) and check:
  A  every class of the 0.1.7 jar AND of the 0.1.6 jar loads and initializes under -Xverify:all
  B  the 13 page states of the 0.1.6 harness (NO SkyyEssentials bridge) + 5 TPA states (a stand-in SkyyEssentials: ess:fn:tpa /
     tpaccept / tpaPending Functions on skyy.bridge) are built by the REAL PartyPage.build of both jars (fake online players)
  C  without SkyyEssentials: identical event bindings, ids and texts, except the one disclosed line: in a party with other members the
     default info line ends "  (TPA buttons need SkyyEssentials.)". With it: 0.1.6's bindings + EXACTLY the expected TPA bindings
     (#SkyyPTpa<i> "tpa:<uuid>" on every other ONLINE member's row - none on offline rows or the viewer's own; #SkyyPTpAcc
     "tpaccept:<from>" only while a request waits), the expected info line, every 0.1.6 id kept
  D  per state, the 0.1.7 markup as the client gets it: SUI.check_markup / check_page, only kit + bar data colours, no Width 0 /
     FlexWeight / ..., the body fills 768 px exactly, every member row (with Promote + Kick + TPA) leaves >= ROW_SLACK px, bar fills > 0
  E  PartyPage.fillPx = the 0.1.5 bar maths
  G  clicks (the REAL handleDataEvent, new jar): TPA -> ess:fn:tpa got { me, member, FALSE } and its answer (without "[TPA] ") is the
     page line; Accept TPA -> ess:fn:tpaccept got { me, from }; SkyyEssentials gone -> "TPA needs SkyyEssentials ..."; a throwing
     bridge -> "That didn't work ..."; a bad uuid; an unknown payload is answered (info reset) - 0.1.6 sent nothing; Refresh re-reads
     the waiting request; bytecode: every handleDataEvent path ends in rebuild() or closePage (3 rebuild calls incl. the catch)
  F  class bytes 0.1.6 vs 0.1.7: only PartyPage (build, handleDataEvent changed; essOn, tpaPending, tpaLine, tpaCall, tpaAccept new),
     SkyyPartyPlugin (setup: the ready line) and the config kit's CfgFn / CfgRows (version string) differ
Not testable without the game (UNVERIFIED in the build report): the look on a client, the real SkyyEssentials teleport (its own
harness compares its bridge with its commands). Nothing is deployed. Default scratch folder: tools/dev/scratch/tpa/party (git-ignored),
deleted at the end unless --keep; TEMP/TMP and java.io.tmpdir point into it. Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.7", "0.1.6"
PKG = "com.skyy.party."
ROW_SLACK = 10                       # = build_skyyparty_0.1.7.py ROW_SLACK
BODY_INNER_H = 840 - 38 - 2 * 17     # 768: the plain frame's body (1400 x 840, title 38, padding 17)
ROW_INNER_W = 1366 - 2 * 4 - 12 - 2 * 8   # 1330: the list well's padding, the 12 px scrollbar reserve, the row padding
BAR_W = 160
DATA_COLORS = ("#d04848", "#e0b040", "#4a8ae0")   # = UI_DATA_COLORS (health, stamina, mana)
EXPECTED_DIFF = {"com/skyy/party/PartyPage.class", "com/skyy/party/SkyyPartyPlugin.class", "com/skyy/party/CfgFn.class",
                 "com/skyy/party/CfgRows.class", "manifest.json"}


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "tpa", "party")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyParty-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyParty-%s.jar" % OLD_VERSION)))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _jvm_start(jars, extra_cp=()):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR] + list(jars) + list(extra_cp), convertStrings=True)
    return B


# ============================================================================================ child: build every page state of one jar
STATES = ["alone", "invites off", "click result", "invite pending", "invite ran out", "leader of 2", "member of 2",
          "leader of 5 odd stats", "long names", "leader of 7", "member of 10", "leader click message", "invite while in a party",
          # 0.1.7: a stand-in SkyyEssentials bridge
          "TPA member of 3", "TPA leader of 3, request waiting", "TPA here waiting, not in a party", "TPA leader of 7",
          "TPA click result, request waiting"]
NOTE = "  (TPA buttons need SkyyEssentials.)"
# states whose default info line gets the no-SkyyEssentials note (in a party with other members, no click result)
NOTE_STATES = {"leader of 2", "member of 2", "leader of 5 odd stats", "long names", "leader of 7", "member of 10", "invite while in a party"}


def U_(n):
    return "00000000-0000-5ce0-0000-%012x" % n


# per TPA state: the expected new bindings (selector, a-payload) in build() order and the expected 0.1.7 info line
TPA_EXP = {
    "TPA member of 3": ([("#SkyyPTpa0", "tpa:" + U_(2))], "Party leader: Alex. Party chat: /pc <message>"),
    "TPA leader of 3, request waiting": ([("#SkyyPTpa1", "tpa:" + U_(2)), ("#SkyyPTpa2", "tpa:" + U_(3)), ("#SkyyPTpAcc", "tpaccept:" + U_(2))],
                                         "Alex wants to teleport to you - press Accept TPA."),
    "TPA here waiting, not in a party": ([("#SkyyPTpAcc", "tpaccept:" + U_(5))], "Zoe wants you to teleport to them - press Accept TPA."),
    "TPA leader of 7": ([("#SkyyPTpa%d" % k, "tpa:" + U_(n)) for k, n in ((1, 2), (3, 4), (4, 5), (6, 7))],
                        "You lead this party. Promote, Kick or TPA a member on their row."),
    "TPA click result, request waiting": ([("#SkyyPTpa1", "tpa:" + U_(2)), ("#SkyyPTpAcc", "tpaccept:" + U_(2))],
                                          "Request sent to Alex. They have 60s to accept. /tpacancel to cancel."),
}


def run_states(jar, out):
    from jpype import JClass, JObject, JArray, JImplements, JOverride
    _jvm_start([jar])
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    loaded, load_fails = 0, []
    for n in names:
        try:
            Cls.forName(n, True, loader)
            loaded += 1
        except Exception as e:
            load_fails.append("%s: %s" % (n, e))
    res = {"jar": jar, "classes": len(names), "loaded": loaded, "load_fails": load_fails, "states": {}, "fill": None}
    if load_fails:
        json.dump(res, open(out, "w"), indent=1)
        return

    Store, Party, Page = JClass(PKG + "PartyStore"), JClass(PKG + "Party"), JClass(PKG + "PartyPage")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Universe = JClass("com.hypixel.hytale.server.core.universe.Universe")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Holder = JClass("com.hypixel.hytale.component.Holder")
    UUID, ArrayList, Long = JClass("java.util.UUID"), JClass("java.util.ArrayList"), JClass("java.lang.Long")
    CHM, System = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.System")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    uni = U.allocateInstance(Universe.class_)
    players = CHM()
    setf(uni, Universe, "playersByUuid", players)
    setf(None, Universe, "instance", uni)
    holder = U.allocateInstance(Holder.class_)

    @JImplements("java.util.function.Function")
    class InvitesOff(object):
        @JOverride
        def apply(self, o):
            return JClass("java.lang.Boolean").FALSE if str(o[1]) == "party.invites" else JClass("java.lang.Boolean").TRUE

    bridge = Store.bridge()

    def uid(n):
        return UUID(0x5ce0, n)

    def ref(n, name, online=True):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", uid(n))
        setf(pr, PRef, "username", name)
        if online:
            setf(pr, PRef, "holder", holder)
            players.put(uid(n), pr)
        else:
            bridge.put("party:name:" + str(uid(n)), name)
        return pr

    def party(ns):
        l = ArrayList()
        for n in ns:
            l.add(uid(n))
        p = Party(l)
        for n in ns:
            Store.PARTY_OF.put(uid(n), p)

    def stats(n, s):
        bridge.put("party:stats:" + str(uid(n)), s)

    def reset():
        Store.PARTY_OF.clear()
        Store.INVITES.clear()
        players.clear()
        for k in list(bridge.keySet()):
            if str(k).startswith("party:") or str(k).startswith("settings:") or str(k).startswith("ess:"):
                bridge.remove(k)

    # 0.1.7: a stand-in SkyyEssentials (the three bridge Functions; tpaPending answers PENDING[0])
    PENDING = [None]

    @JImplements("java.util.function.Function")
    class EssTpa(object):
        @JOverride
        def apply(self, o):
            return "[TPA] Request sent."

    @JImplements("java.util.function.Function")
    class EssPend(object):
        @JOverride
        def apply(self, o):
            if PENDING[0] is None:
                return None
            a = JArray(JObject)(3)
            a[0], a[1], a[2] = JClass("java.lang.String")(PENDING[0][0]), JClass("java.lang.String")(PENDING[0][1]), \
                JClass("java.lang.Boolean").valueOf(PENDING[0][2])
            return a

    def ess(pending=None):
        PENDING[0] = pending
        bridge.put("ess:fn:tpa", EssTpa())
        bridge.put("ess:fn:tpaccept", EssTpa())
        bridge.put("ess:fn:tpaPending", EssPend())

    def invite(to_n, from_n, from_name, ms):
        a = JArray(JObject)(3)
        a[0], a[1], a[2] = uid(from_n), Long(System.currentTimeMillis() + ms), JClass("java.lang.String")(from_name)
        Store.INVITES.put(uid(to_n), a)

    def setup(state):
        """The world of one state; returns (viewer PlayerRef, page info)."""
        reset()
        me = ref(1, "Steve")
        info = ""
        if state == "invites off":
            bridge.put("settings:fn:get", InvitesOff())
        elif state == "click result":
            info = "Nobody called Bob is online right now."
        elif state == "invite pending":
            ref(2, "Alex")
            invite(1, 2, "Alex", 41500)
        elif state == "invite ran out":
            invite(1, 2, "Alex", -3000)
        elif state == "leader of 2":
            ref(2, "Alex")
            party([1, 2])
            stats(1, "18,20,9,10,0,0,world-a")
            stats(2, "20,20,10,10,40,50,world-a")
        elif state == "member of 2":
            ref(2, "Alex", online=False)
            party([2, 1])
            stats(1, "7,20,3,10,0,0,world-a")
        elif state == "leader of 5 odd stats":
            ref(2, "Alex")
            ref(3, "Bea")
            ref(4, "Cid")
            ref(5, "Dot", online=False)
            bridge.put("party:name:" + str(uid(9)), "Zed")
            party([1, 2, 3, 4, 5])
            stats(1, "25,20,-4,10,9,0,skyy-island-" + str(uid(1)))                   # over max, negative, mana none
            stats(2, "5,0,0,0,0,0,skyy-island-" + str(uid(1)) + "-p2")               # zero max everywhere, on my island
            stats(3, "12,20,10,10,30,30,skyy-island-" + str(uid(3)))                 # on their own island
            stats(4, "12,20,x,10,30,30,skyy-island-" + str(uid(9)))                  # malformed -> "...", someone else's island
            stats(5, "2147483647,2147483647,1,2147483647,0,5,hub")                   # offline: no where
        elif state == "long names":
            ref(2, "Abcdefghijklmnop")
            ref(3, "Qrstuvwxyzabcdef")
            setf(me, PRef, "username", "Mmmmmmmmmmmmmmmm")
            party([2, 1, 3])
            stats(1, "20,20,10,10,0,0,skyy-island-" + str(uid(2)))
            stats(2, "20,20,10,10,0,0,skyy-island-" + str(uid(2)))
            stats(3, "20,20,10,10,0,0,a-very-long-world-name-for-the-where-column")
        elif state in ("leader of 7", "leader click message"):
            ns = [1, 2, 3, 4, 5, 6, 7]
            for n in ns[1:]:
                ref(n, "Member%d" % n, online=(n % 3 != 0))
            party(ns)
            for n in ns:
                stats(n, "%d,20,%d,10,%d,50,world-%s" % (n * 2, n, n * 5, "a" if n % 2 else "b"))
            if state == "leader click message":
                info = "Member2 was kicked from the party."
        elif state == "member of 10":
            ns = [4, 2, 3, 1, 5, 6, 7, 8, 9, 10]
            for n in ns:
                if n != 1:
                    ref(n, "Player%d" % n, online=(n % 4 != 0))
            party(ns)
            for n in ns:
                if n != 7:
                    stats(n, "%d,30,%d,12,0,0,world-a" % (n, n))
        elif state == "invite while in a party":
            ref(2, "Alex")
            ref(3, "Bea")
            party([1, 2])
            invite(1, 3, "Bea", 30000)
        elif state == "TPA member of 3":
            ess()
            ref(2, "Alex")
            ref(3, "Bea", online=False)
            party([2, 1, 3])
            stats(1, "20,20,10,10,0,0,world-a")
            stats(2, "20,20,10,10,0,0,world-b")
        elif state in ("TPA leader of 3, request waiting", "TPA click result, request waiting"):
            ess((str(uid(2)), "Alex", False))
            ref(2, "Alex")
            if state == "TPA leader of 3, request waiting":
                ref(3, "Bea")
                party([1, 2, 3])
            else:
                party([1, 2])
                info = "Request sent to Alex. They have 60s to accept. /tpacancel to cancel."
            stats(2, "20,20,10,10,0,0,world-b")
        elif state == "TPA here waiting, not in a party":
            ess((str(uid(5)), "Zoe", True))
        elif state == "TPA leader of 7":
            ess()
            ns = [1, 2, 3, 4, 5, 6, 7]
            for n in ns[1:]:
                ref(n, "Member%d" % n, online=(n % 3 != 0))
            party(ns)
            for n in ns:
                stats(n, "%d,20,%d,10,%d,50,world-%s" % (n * 2, n, n * 5, "a" if n % 2 else "b"))
        return me, info

    for state in STATES:
        me, info = setup(state)
        page = Page(me)
        page.info = info
        b, ev = UCB(), UEB()
        try:
            page.build(None, b, ev, None)
            err = None
        except Exception as e:
            err = str(e)
        cmds = [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]
        evs = [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data),
                bool(e.locksInterface)] for e in ev.getEvents()]
        res["states"][state] = {"error": err, "commands": cmds, "events": evs}

    if hasattr(Page, "fillPx"):
        cases = []
        vals = [-2147483648, -100, -1, 0, 1, 2, 3, 7, 10, 19, 20, 21, 99, 100, 101, 159, 160, 161, 1000, 99999, 2147483646, 2147483647]
        import random
        rnd = random.Random(16)
        for c in vals:
            for m in vals:
                cases.append((c, m))
        for _ in range(4527):
            cases.append((rnd.randint(-50, 5000), rnd.randint(-5, 5000)))
        res["fill"] = [[c, m, int(Page.fillPx(c, m))] for c, m in cases]
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: the clicks (0.1.7 jar)
def run_clicks(jar, out):
    from jpype import JClass, JObject, JArray, JImplements, JOverride
    _jvm_start([jar])
    Store, Party, Page = JClass(PKG + "PartyStore"), JClass(PKG + "Party"), JClass(PKG + "PartyPage")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Universe = JClass("com.hypixel.hytale.server.core.universe.Universe")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Holder = JClass("com.hypixel.hytale.component.Holder")
    UUID, ArrayList = JClass("java.util.UUID"), JClass("java.util.ArrayList")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    uni = U.allocateInstance(Universe.class_)
    players = CHM()
    setf(uni, Universe, "playersByUuid", players)
    setf(None, Universe, "instance", uni)
    holder = U.allocateInstance(Holder.class_)
    bridge = Store.bridge()
    me = U.allocateInstance(PRef.class_)
    setf(me, PRef, "uuid", UUID(0x5ce0, 1))
    setf(me, PRef, "username", "Steve")
    setf(me, PRef, "holder", holder)
    players.put(UUID(0x5ce0, 1), me)
    alex = U.allocateInstance(PRef.class_)
    setf(alex, PRef, "uuid", UUID(0x5ce0, 2))
    setf(alex, PRef, "username", "Alex")
    setf(alex, PRef, "holder", holder)
    players.put(UUID(0x5ce0, 2), alex)
    l = ArrayList()
    l.add(UUID(0x5ce0, 1))
    l.add(UUID(0x5ce0, 2))
    p = Party(l)
    Store.PARTY_OF.put(UUID(0x5ce0, 1), p)
    Store.PARTY_OF.put(UUID(0x5ce0, 2), p)
    CALLS = []
    MODE = ["ok"]
    PEND = [None]

    def rec(kind, o):
        CALLS.append([kind] + [None if x is None else str(x) for x in o])

    @JImplements("java.util.function.Function")
    class FT(object):
        @JOverride
        def apply(self, o):
            rec("tpa", o)
            if MODE[0] == "throw":
                raise JClass("java.lang.IllegalStateException")("boom")
            return "[TPA] Request sent to Alex. They have 60s to accept. /tpacancel to cancel."

    @JImplements("java.util.function.Function")
    class FA(object):
        @JOverride
        def apply(self, o):
            rec("tpaccept", o)
            if MODE[0] == "throw":
                raise JClass("java.lang.IllegalStateException")("boom")
            return "[TPA] Accepted. Alex is teleporting to you."

    @JImplements("java.util.function.Function")
    class FP(object):
        @JOverride
        def apply(self, o):
            CALLS.append(["pending", str(o)])
            if PEND[0] is None:
                return None
            a = JArray(JObject)(3)
            a[0], a[1], a[2] = JClass("java.lang.String")(str(UUID(0x5ce0, 2))), JClass("java.lang.String")("Alex"), JClass("java.lang.Boolean").FALSE
            return a

    def on():
        bridge.put("ess:fn:tpa", FT())
        bridge.put("ess:fn:tpaccept", FA())
        bridge.put("ess:fn:tpaPending", FP())

    def off():
        for k in ("ess:fn:tpa", "ess:fn:tpaccept", "ess:fn:tpaPending"):
            bridge.remove(k)

    page = Page(me)
    res = {}

    def click(a, info0="old line"):
        del CALLS[:]
        page.info = info0
        try:
            page.handleDataEvent(None, None, json.dumps({"a": a}, separators=(",", ":")))
            err = None
        except Exception as e:
            err = str(e)
        return {"info": None if page.info is None else str(page.info), "calls": list(CALLS), "err": err}

    def built():
        b, ev = UCB(), UEB()
        page.build(None, b, ev, None)
        return [[str(e.selector), str(e.data)] for e in ev.getEvents()]

    u2 = str(UUID(0x5ce0, 2))
    on()
    res["tpa"] = click("tpa:" + u2)
    res["tpaccept"] = click("tpaccept:" + u2)
    res["tpaccept bad uuid"] = click("tpaccept:not-a-uuid")
    res["unknown"] = click("bogus")
    res["refresh"] = click("refresh")
    MODE[0] = "throw"
    res["tpa throws"] = click("tpa:" + u2)
    res["tpaccept throws"] = click("tpaccept:" + u2)
    MODE[0] = "ok"
    off()
    res["tpa no ess"] = click("tpa:" + u2)
    res["tpaccept no ess"] = click("tpaccept:" + u2)
    # Refresh re-reads the waiting request (no periodic update: only a build reads it)
    on()
    PEND[0] = None
    page.info = ""
    res["build no request"] = built()
    PEND[0] = True
    res["build request"] = built()
    del CALLS[:]
    res["pending reads per build"] = (built(), len([c for c in CALLS if c[0] == "pending"]))
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: bytecode method compare (javassist)
def run_bytecode(old, new, out):
    import skyybuild as B
    from jpype import JClass
    _jvm_start([], [B.JAVASSIST])
    ClassPool, BAIS = JClass("javassist.ClassPool"), JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def listing(pool, data):
        cc = pool.makeClass(BAIS(data))
        ms = {}
        behaviors = list(cc.getDeclaredBehaviors())
        if cc.getClassInitializer() is not None:
            behaviors.append(cc.getClassInitializer())
        for mm in behaviors:
            key = "%s%s" % (mm.getName(), mm.getSignature())
            if mm.getMethodInfo().getCodeAttribute() is None:
                ms[key] = ""
                continue
            it = mm.getMethodInfo().getCodeAttribute().iterator()
            cpool = mm.getMethodInfo().getConstPool()
            lines = []
            while it.hasNext():
                ln = str(IP.instructionString(it, it.next(), cpool))
                ln = re.sub(r"#\d+ = ", "", ln).replace("ldc_w ", "ldc ")
                ln = re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln)
                lines.append(ln)
            ms[key] = "\n".join(lines)
        fields = sorted("%s %s" % (f.getName(), f.getSignature()) for f in list(cc.getDeclaredFields()))
        consts = {}
        for f in list(cc.getDeclaredFields()):
            ca = f.getFieldInfo().getConstantValue()
            if ca:
                consts[str(f.getName())] = str(cc.getClassFile().getConstPool().getLdcValue(ca))
        return ms, fields, consts

    zo, zn = zipfile.ZipFile(old), zipfile.ZipFile(new)
    res = {}
    for n in sorted(set(zo.namelist()) & set(zn.namelist())):
        if not n.endswith(".class"):
            continue
        a, b = zo.read(n), zn.read(n)
        if a == b:
            continue
        mo, fo, co = listing(ClassPool(False), a)
        if n.endswith("PartyPage.class"):
            # G (bytecode): every handleDataEvent path is answered - rebuild() three times (invite, actions, catch), close via closePage
            hd = [v for k, v in listing(ClassPool(False), b)[0].items() if k.startswith("handleDataEvent")][0]
            res["_handle"] = {"rebuild": hd.count("CustomUIPage.rebuild") + hd.count("PartyPage.rebuild"), "close": hd.count("closePage")}
        mn, fn, cn = listing(ClassPool(False), b)
        changed = sorted(k for k in set(mo) & set(mn) if mo[k] != mn[k])
        consts = dict((k, [co.get(k), cn.get(k)]) for k in set(co) | set(cn) if co.get(k) != cn.get(k))
        res[n] = {"changed": changed, "gone": sorted(set(mo) - set(mn)), "new": sorted(set(mn) - set(mo)), "fields_same": fo == fn,
                  "consts": consts,
                  # changed only by the version string ("0.1.5" -> "0.1.6")
                  "version_only": all(mo[k].replace(OLD_VERSION, "V") == mn[k].replace(VERSION, "V") for k in changed)
                  and all((x or "").replace(OLD_VERSION, "V") == (y or "").replace(VERSION, "V") for x, y in consts.values())}
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent: comparisons
def js(v):
    """The Java string a Set command carries (its data is JSON); non-strings come back as their JSON text."""
    try:
        x = json.loads(v)
    except Exception:
        return v
    if isinstance(x, dict) and list(x) == ["0"]:      # UICommandBuilder.set(String, String) sends {"0": value}
        x = x["0"]
    return x if isinstance(x, str) else v


_ID_RE = re.compile(r"(?:^|[;{}])\s*[A-Z][A-Za-z]*\s+#([A-Za-z0-9]+)\s*\{")
_TEXT_RE = re.compile(r'\bText: "((?:[^"\\]|\\.)*)"')
_COL_RE = re.compile(r"(?:Background|TextColor|Color):\s*(#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?:\(\s*[0-9.]+\s*\))?)")


def ids_of(state):
    out = []
    for t, sel, data, text in state["commands"]:
        if t == "AppendInline" and text:
            out += _ID_RE.findall(text)
    return out


def sets_of(state):
    return dict((sel, js(data)) for t, sel, data, text in state["commands"] if t == "Set" and sel and sel.endswith(".Text"))


def inline_texts(state):
    return sorted(x for t, sel, data, text in state["commands"] if t == "AppendInline" and text for x in _TEXT_RE.findall(text) if x)


def own_anchor(mk):
    """The element's own Anchor (the first one after its opening brace) as {key: int}."""
    rest = mk[mk.index("{") + 1:]
    m = re.search(r"Anchor:\s*\(([^)]*)\)", rest)
    if not m:
        return {}
    nxt = rest.find("{")
    if nxt != -1 and nxt < m.start():
        return {}                     # the first Anchor belongs to a child element: the element itself has none
    out = {}
    for part in m.group(1).split(","):
        k, v = part.split(":")
        out[k.strip()] = int(v.strip())
    return out


def a_of(ev):
    try:
        return json.loads(ev[2]).get("a")
    except Exception:
        return None


def compare_state(name, old, new, SUI, counts):
    check(old["error"] is None and new["error"] is None, "%s: build() ran in both jars (%s / %s)" % (name, old["error"], new["error"]))
    if old["error"] or new["error"]:
        return
    # C1 bindings: 0.1.6's exactly, plus (with SkyyEssentials) exactly the expected TPA bindings
    exp, exp_info = TPA_EXP.get(name, ([], None))
    tsel = set(x[0] for x in exp)
    extra = [(e[1], a_of(e)) for e in new["events"] if e[1] in tsel or (e[1] or "").startswith(("#SkyyPTpa", "#SkyyPTpAcc"))]
    rest = [e for e in new["events"] if not (e[1] in tsel or (e[1] or "").startswith(("#SkyyPTpa", "#SkyyPTpAcc")))]
    check(old["events"] == rest, "%s: 0.1.6's event bindings kept identical (%d / %d)" % (name, len(old["events"]), len(rest)))
    check(extra == exp, "%s: TPA bindings %s, want %s" % (name, extra, exp))
    check(all(e[0] == "Activating" for e in new["events"] if e[1] in tsel), "%s: TPA bindings are Activating" % name)
    counts["bindings"] += len(new["events"])
    counts["tpa_bindings"] += len(extra)
    # C2 ids
    oi, ni = ids_of(old), ids_of(new)
    miss = sorted(set(oi) - set(ni))
    check(not miss, "%s: no 0.1.6 id missing: %s" % (name, miss))
    counts["ids"] += len(set(oi))
    # C3 texts (+ the disclosed compact-row difference of 0.1.5)
    os_, ns_ = sets_of(old), sets_of(new)
    n_members = len([1 for k in ns_ if re.fullmatch(r"#SkyyPName\d+\.Text", k)])
    compact = n_members > 5
    for k in sorted(set(os_) | set(ns_)):
        a, b = os_.get(k), ns_.get(k)
        if a == b:
            counts["texts"] += 1
            continue
        if k == "#SkyyPInfo.Text":
            if exp_info is not None:
                check(b == exp_info, "%s: info line %r, want %r" % (name, b, exp_info))
                counts["disclosed"] += 1
                continue
            if name in NOTE_STATES and b == (a or "") + NOTE:
                counts["disclosed"] += 1
                continue
        m = re.fullmatch(r"#SkyyP(Name|Wh|Role|On)(\d+)\.Text", k)
        if compact and m:
            kind, i = m.group(1), m.group(2)
            if kind == "Name" and a == "* " + (b or "") and i == "0":
                counts["disclosed"] += 1
                continue
            if kind == "Wh" and a == "Offline" and b == "" and ns_.get("#SkyyPOn%s.Text" % i) == "Offline":
                counts["disclosed"] += 1
                continue
            if kind in ("Role", "On") and a is None and b is not None:
                counts["disclosed"] += 1
                continue
        check(False, "%s: text %s: 0.1.5 %r / 0.1.6 %r" % (name, k, a, b))
    if name in NOTE_STATES:
        check(ns_.get("#SkyyPInfo.Text", "").endswith(NOTE), "%s: the no-SkyyEssentials note is shown" % name)
    nt = [x for x in inline_texts(new) if x not in ("TPA", "Accept TPA")]
    check(inline_texts(old) == nt, "%s: inline texts identical (+ TPA / Accept TPA): %s / %s" % (name, inline_texts(old), inline_texts(new)))
    check(inline_texts(new).count("TPA") == len([x for x in exp if x[0].startswith("#SkyyPTpa")])
          and inline_texts(new).count("Accept TPA") == len([x for x in exp if x[0] == "#SkyyPTpAcc"]), "%s: one TPA button per binding" % name)
    # D the 0.1.6 markup as the client gets it
    ap = SUI.Appends()
    allowed = SUI.allowed_colors() | set(SUI.norm_color(c) for c in DATA_COLORS)
    body, rows, fills = [], {}, []
    for idx, (t, sel, data, text) in enumerate(new["commands"]):
        if t == "AppendInline":
            parent = None if sel is None else sel.lstrip("#")
            check(idx != 0 or parent is None, "%s: the first append is the page root" % name)
            try:
                SUI.check_markup(text, prefix="SkyyP", root=(parent is None))
            except ValueError as e:
                check(False, "%s: check_markup: %s" % (name, e))
            ap.append((parent, text))
            for c in _COL_RE.findall(text):
                check(SUI.norm_color(c) in allowed, "%s: colour %s is a kit / data colour" % (name, c))
                counts["colours"] += 1
            for bad in ("Width: 0,", "Width: 0)", "FlexWeight", "WrapMaxLines", "LetterSpacing", "LayoutMode: Right", "LayoutMode: Center",
                        "LayoutMode: Full", "ItemGrid"):
                check(bad not in text, "%s: no %s in %s" % (name, bad.strip(",)"), text[:80]))
            if parent == "SkyyParty":
                body.append(own_anchor(text))
            m = re.fullmatch(r"SkyyPRow(\d+)", parent or "")
            if m:
                rows.setdefault(m.group(1), []).append(own_anchor(text))
            if parent and re.fullmatch(r"SkyyP(Hp|St|Mp)\d+B", parent):
                fills.append(own_anchor(text))
        elif t == "Set":
            ident, prop = sel.lstrip("#").rsplit(".", 1)
            ap.sets.append((ident, prop, js(data)))
    try:
        SUI.check_page(ap, "SkyyP")
        counts["check_page"] += 1
    except ValueError as e:
        check(False, "%s: check_page: %s" % (name, e))
    counts["appends"] += len(ap)
    tot = sum(a.get("Height", 0) + a.get("Top", 0) + a.get("Bottom", 0) for a in body)
    check(tot == BODY_INNER_H, "%s: the body children fill %d px exactly (got %d)" % (name, BODY_INNER_H, tot))
    for i, parts in rows.items():
        w = sum(a.get("Width", 0) + a.get("Left", 0) + a.get("Right", 0) for a in parts)
        check(w <= ROW_INNER_W - ROW_SLACK, "%s: row %s is %d px of %d (slack >= %d)" % (name, i, w, ROW_INNER_W, ROW_SLACK))
        counts["min_slack"] = min(counts["min_slack"], ROW_INNER_W - w)
    for a in fills:
        check(0 < a.get("Width", 0) <= BAR_W, "%s: a bar fill is 1..%d px wide (%s)" % (name, BAR_W, a))
    counts["fills"] += len(fills)
    counts["states"] += 1


def main():
    if "--run" in sys.argv:
        run_states(arg("--run"), arg("--out"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    if "--clicks" in sys.argv:
        run_clicks(arg("--clicks"), arg("--out"))
        return
    for j in (JAR, OLD_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not SCRATCH.replace("\\", "/").lower().startswith(os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower()):
        sys.exit("--dir must be inside tools/dev/scratch/ (it is deleted afterwards): " + SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    me = os.path.abspath(__file__)
    outs = {}
    for tag, j in (("new", JAR), ("old", OLD_JAR)):
        outs[tag] = os.path.join(SCRATCH, "states-%s.json" % tag)
        p = subprocess.run([sys.executable, me, "--run", j, "--out", outs[tag], "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(outs[tag]), "child JVM for %s ran" % j)
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "bytecode child ran")
    clo = os.path.join(SCRATCH, "clicks.json")
    p = subprocess.run([sys.executable, me, "--clicks", JAR, "--out", clo, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(clo), "clicks child ran")
    if FAILS:
        return finish()
    new, old = json.load(open(outs["new"])), json.load(open(outs["old"]))
    # A
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                            os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    # B-D
    import skyyui as SUI
    counts = dict(states=0, bindings=0, tpa_bindings=0, ids=0, texts=0, disclosed=0, colours=0, check_page=0, appends=0, fills=0,
                  min_slack=10 ** 6)
    for st in STATES:
        check(st in new["states"] and st in old["states"], "B: state %s built by both jars" % st)
        if st in new["states"] and st in old["states"]:
            compare_state(st, old["states"][st], new["states"][st], SUI, counts)
    print("B-D. %(states)d states: %(bindings)d bindings (%(tpa_bindings)d TPA, the rest = 0.1.6's), %(ids)d 0.1.6 ids all kept, "
          "%(texts)d texts identical (+ %(disclosed)d disclosed info lines); %(check_page)d check_page / %(appends)d appends through check_markup, "
          "%(colours)d colours audited, %(fills)d bar fills (all > 0), min row slack %(min_slack)d px" % counts)
    # E
    fill = new.get("fill") or []
    bad = []
    for c, m, got in fill:
        exp = 0 if m <= 0 else (BAR_W * min(max(c, 0), m)) // m
        if exp != got:
            bad.append((c, m, got, exp))
    check(len(fill) > 5000 and not bad, "E: fillPx = the 0.1.5 bar maths on %d cases: %s" % (len(fill), bad[:5]))
    print("E. fillPx: %d cases, %d mismatches" % (len(fill), len(bad)))
    # F
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    check(sorted(zo.namelist()) == sorted(zn.namelist()), "F: same entries in both jars")
    diff = set(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    same = len(set(zo.namelist()) & set(zn.namelist())) - len(diff)
    check(diff <= EXPECTED_DIFF, "F: only %s differ, got %s" % (sorted(EXPECTED_DIFF), sorted(diff)))
    bc = json.load(open(bco))
    pp = bc.get("com/skyy/party/PartyPage.class", {})
    hd = bc.pop("_handle", {})
    check(hd.get("rebuild") == 3 and hd.get("close") == 1, "G: handleDataEvent answers every path (rebuild x3 incl. the catch, closePage x1): %s" % hd)
    check(sorted(m.split("(")[0] for m in pp.get("changed", [])) == ["build", "handleDataEvent"]
          and sorted(m.split("(")[0] for m in pp.get("new", [])) == ["essOn", "tpaAccept", "tpaCall", "tpaLine", "tpaPending"]
          and not pp.get("gone"), "F: PartyPage: build + handleDataEvent changed, the 5 TPA helpers new, nothing gone: %s" % pp)
    sp = bc.get("com/skyy/party/SkyyPartyPlugin.class", {})
    check(sp.get("changed") == ["setup()V"] and not sp.get("new") and not sp.get("gone") and sp.get("fields_same"),
          "F: SkyyPartyPlugin: only setup() (the ready line) changed: %s" % sp)
    for k in ("com/skyy/party/CfgFn.class", "com/skyy/party/CfgRows.class"):
        c = bc.get(k)
        if c is None:
            continue
        check(not c.get("new") and not c.get("gone") and c.get("fields_same") and c.get("version_only"),
              "F: %s: only the version string differs: %s" % (k, c))
    # G. clicks
    cl = json.load(open(clo))
    me1, u2 = U_(1), U_(2)
    g = cl["tpa"]
    check(g["err"] is None and g["calls"] in ([["tpa", me1, u2, "false"]], [["tpa", me1, u2, "False"]]) and g["info"] == "Request sent to Alex. They have 60s to accept. /tpacancel to cancel.",
          "G: TPA -> ess:fn:tpa { me, member, false }, its line without [TPA] on the page: %s" % g)
    g = cl["tpaccept"]
    check(g["err"] is None and g["calls"] == [["tpaccept", me1, u2]] and g["info"] == "Accepted. Alex is teleporting to you.",
          "G: Accept TPA -> ess:fn:tpaccept { me, from }: %s" % g)
    g = cl["tpaccept bad uuid"]
    check(g["calls"] == [] and g["info"] == "That request is gone - press Refresh.", "G: a bad uuid is answered: %s" % g)
    check(cl["unknown"]["info"] == "" and cl["unknown"]["err"] is None, "G: an unknown payload is answered (info reset, rebuilt): %s" % cl["unknown"])
    check(cl["refresh"]["info"] == "", "G: Refresh clears the line")
    check(cl["tpa throws"]["info"] == "That didn't work - try /tpa <name> in chat." and cl["tpa throws"]["err"] is None, "G: a throwing ess:fn:tpa: %s" % cl["tpa throws"])
    check(cl["tpaccept throws"]["info"] == "That didn't work - try /tpaccept in chat.", "G: a throwing ess:fn:tpaccept: %s" % cl["tpaccept throws"])
    check(cl["tpa no ess"]["info"] == cl["tpaccept no ess"]["info"] == "TPA needs SkyyEssentials, which is not on this server."
          and cl["tpa no ess"]["calls"] == [], "G: SkyyEssentials gone: %s" % cl["tpa no ess"])
    acc = [e for e in cl["build request"] if e[0] == "#SkyyPTpAcc"]
    check(not [e for e in cl["build no request"] if e[0] == "#SkyyPTpAcc"] and len(acc) == 1 and ('"tpaccept:%s"' % u2) in acc[0][1],
          "G: Accept TPA appears on the next build once a request waits (Refresh / any click): %s" % acc)
    check(cl["pending reads per build"][1] == 1, "G: one ess:fn:tpaPending read per build (no polling)")
    print("G. clicks: %d cases answered" % len(cl))
    print("F. class bytes: %d entries identical, differ: %s; methods: %s" % (
        same, ", ".join(sorted(n.split("/")[-1] for n in diff)),
        "; ".join("%s %s" % (n.split("/")[-1][:-6], dict((x, bc[n][x]) for x in ("changed", "new", "gone", "consts") if bc[n][x]))
                  for n in sorted(bc))))
    return finish()


def finish():
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    print("SkyyParty %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
