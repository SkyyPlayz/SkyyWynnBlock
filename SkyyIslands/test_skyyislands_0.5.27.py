"""Harness for SkyyIslands 0.5.27 (the bridge island:fn:act for SkyyMenu's new World tab; tools/islands_0_5_27_patch.py).
Build first: python tools/islands_0_5_27_patch.py && python SkyyIslands/build_skyyislands_0.5.27.py

    python SkyyIslands/test_skyyislands_0.5.27.py [--jar <jar>] [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; tools/hub_tab_kit.stage = the engine stand-ins with the REAL PageManager, the island menu
driven as test_skyyislands_0.5.18.py drives it; -Xverify:all):
  S      static  the patch re-runs to identical bytes, line endings kept, one class added (IslandActFn), no new system / command / listener;
                 setup puts island:fn:act (CLOSED cleared first), shutdown sets CLOSED first and removes the key
  A / C / AA     -Xverify:all, class compare 0.5.26 -> 0.5.27 (only the listed members differ, IslandActFn added), engine-access audit
  TWIN   exec    the SAME scripted run twice on the same island files, each in its own child JVM: once through the REAL
                 IslandMenuPage.handleDataEvent (the page's row lists set as its build sets them), once through island:fn:act (a state
                 read first for the token + profile key + the shown toggle / grid values, as the Menu will). ~70 steps by 3 players: name
                 box notes, invite / trust by name + every refusal, decline / accept, promote / demote / kick (2 presses) and the refusals
                 for a non-owner, untrust, the permission grid (allow / deny / unknown flag / a member refused), reset permissions (2
                 presses), visit modes, the visitor limit -/+, visit ping / PvP / mob spawning, unban, expel / trust / ban (2 presses) of an
                 online player, leave (2 presses, the screen closes), disband (2 presses), reset (presses 1 + 2), refresh between arms:
                 after EVERY step the same answer line (or the screen closed on both) and the same armed press; at the end the same
                 island files and the same co-op map
  ACT    exec    the bridge's own rules: every state line (h 28 fields, n / z / r / c / m / p / t / d / f / v / b / i), caps, a '|' in a
                 name kept, offline state; the server stopping / offline / no world / not the world thread / stale token / changed profile
                 key (arm dropped) / double click within 350 ms (arm kept) / arm expiry / an arm dropped by another op / an arm from
                 another profile / reset arm = reset.confirmSeconds; stale toggles and grid cells refused (file unchanged); unknown op /
                 bad arguments never throw; create / go run IslandCmd.go / goHome and close the screen; the third reset press runs
                 resetNow; the bytecode: act calls the page's IslandCoop / IslandCmd methods
  REG    the 0.5.26 phases (data, shift, retry, place, fix, cmd) + 0.5.25's (archi, door, fix2, life, cfg) + 0.5.24 / 0.5.23's (unload,
         early, ids, boss, clear, time) on the 0.5.27 jar
  LIVE   live: a scratch COPY of the live Skyy_SkyyIslands - every island file reads + archiStatus (0.5.26's phase); liveact: island:fn:act
         state answers for every island owner of the copy, nothing on disk changed; live2: START TWICE (0.5.25's one-time update path)
Not testable without the game (UNVERIFIED): the real teleports of create / go / leave / reset, the real screen closing on a client.
Exit code 1 on any failure.
"""
import os, sys, re, json, time, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "isl1", "h")]
import skyybuild as B
import harness_kit as HK
import hub_tab_kit as HT


def _load(name, fn):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(sp)
    argv = list(sys.argv)
    sp.loader.exec_module(m)
    sys.argv[:] = argv
    return m


T26 = _load("isl526", "test_skyyislands_0.5.26.py")
T25, T24, T23 = T26.T25, T26.T24, T26.T23
T18 = _load("isl518", "test_skyyislands_0.5.18.py")

VERSION, OLD = "0.5.27", "0.5.26"
PKG = "com.skyy.islands."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir"))
GEN = os.path.join(HERE, "build_skyyislands_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyislands_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "islands_0_5_27_patch.py")
LIVE_DIR = T25.LIVE_DIR
ADDED = ["IslandActFn"]
EXPECT = {   # the version text only ("SkyyIslands 0.5.27" in the default config header / the kit's export header) + setup / shutdown
    "SkyyIslandsPlugin": ["~m setup", "~m shutdown"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "IslandCfg": ["~m load"],
}
UO, UA, UB, UC = ("00000000-0000-0000-0000-0000000016c%d" % i for i in (1, 2, 3, 4))
BAN1, BAN2, TR1 = "00000000-0000-0000-0007-000000000001", "00000000-0000-0000-0007-000000000002", "00000000-0000-0000-0008-000000000001"
NAMES = {"O": (UO, "Owner"), "A": (UA, "Alby"), "B": (UB, "Bea"), "C": (UC, "Cid")}
ISLAND_FILE = ("v=5\nworld=skyy-island-harness\nownerName=Owner\ntrusted=%s\nbanned=%s,%s\nname.%s=Bannie\n" % (TR1, BAN1, BAN2, BAN1))
SEEN = re.compile(r"\A(.*?) \(\d+ s\)")


# ---------------------------------------------------------------------------------------------------------------- static
def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyIslands 0.5.27 - build script') and g.count('VERSION = "0.5.27"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "registerGlobal("):
        K.eq(g.count(w), o.count(w), "S no new %s" % w)
    K.eq(g.count(" = K(") - o.count(" = K("), 1, "S one class added (IslandActFn)")
    su = g[g.index("public void setup() {"):]
    su = su[:su.index("protected void shutdown()")]
    K.check(su.index("IslandActFn.CLOSED = false;") < su.index('b.put("island:fn:act", new @PKG@.IslandActFn())'), "S setup clears CLOSED, then puts island:fn:act")
    sd = g[g.index("protected void shutdown() {"):]
    K.check(sd.index("IslandActFn.CLOSED = true;") < sd.index("ticker.cancel") and 'b.remove("island:fn:act");' in sd, "S shutdown: CLOSED first, key removed")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    # the page itself is unchanged (no page id change, no handleDataEvent change)
    K.check(g[g.index('M(page, r"""\npublic void handleDataEvent('):g.index("# /island subcommands")] ==
            o[o.index('M(page, r"""\npublic void handleDataEvent('):o.index("# /island subcommands")], "S the page's handleDataEvent is unchanged")
    K.check(re.search(r'IS_PAGE_CHECKED = "3be00278ccc6"', g) is not None, "S the page id gate is the 0.5.18 page")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- the stage
class Stage(object):
    """the island menu's stage (0.5.18's setup) + the owner's island file + 4 players online, the world thread = this thread"""

    def __init__(self, scratch, jar, tag):
        from jpype import JClass
        self.home = os.path.join(scratch, tag, "Skyy_SkyyIslands")
        os.makedirs(os.path.join(self.home, "islands"), exist_ok=True)
        with open(os.path.join(self.home, "islands", UO + ".properties"), "w", encoding="latin-1", newline="\n") as f:
            f.write(ISLAND_FILE)
        self.E, self.J = T18.setup(os.path.join(scratch, tag), jar, self.home)
        E = self.E
        self.IS, self.PG, self.Act = self.J("IslandStore"), self.J("IslandMenuPage"), self.J("IslandActFn")
        self.UUID = E.UUID
        self.X = {}
        for w, (u, n) in NAMES.items():
            self.X[w] = E.mkp(E.UUID.fromString(u), n)
        self.AL = JClass("java.util.ArrayList")
        Cls = JClass("java.lang.Class")
        fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
        fu.setAccessible(True)
        self.U = fu.get(None)
        self.Thread = JClass("java.lang.Thread")
        self.TT = JClass("com.hypixel.hytale.server.core.util.thread.TickingThread")
        self.RUN = JClass("com.hypixel.hytale.server.core.util.thread.TickingThread$Run")
        self.AR = JClass("java.util.concurrent.atomic.AtomicReference")
        self.thread(self.Thread.currentThread())

    def thread(self, th):
        """the world W1's current run thread (World.isInThread = currentRun.thread == the caller)"""
        r = self.U.allocateInstance(self.RUN.class_)
        HT.jf(self.RUN.class_, "thread").set(r, th)
        HT.jf(self.TT.class_, "currentRun").set(self.E.W1, self.AR(r))

    def key(self, w):
        return str(self.IS.pkey(self.UUID.fromString(NAMES[w][0])))

    def files(self):
        d_ = os.path.join(self.home, "islands")
        out = {}
        for f in sorted(os.listdir(d_)):
            fp = os.path.join(d_, f)
            if os.path.isfile(fp) and f.endswith(".properties"):
                out[f] = "\n".join(ln for ln in open(fp, encoding="latin-1").read().splitlines() if not ln.startswith("#") and not ln.startswith("since."))
        return out

    def open(self, w):
        P = self.X[w]
        pg = self.E.pg(P)
        if pg is None or str(pg.getClass().getName()) != PKG + "IslandMenuPage":
            pg = self.PG(P.pr)
            P.pm.openCustomPage(P.ref, P.st, pg)
            self.E.pump(P)
            pg = self.E.pg(P)
        return pg


def resolve(S, a):
    """@X = player X's profile key, #X = player X's UUID"""
    if a is None:
        return None
    if a.startswith("@") and a[1:] in NAMES:
        return S.key(a[1:])
    if a.startswith("#") and a[1:] in NAMES:
        return NAMES[a[1:]][0]
    return a


# the scripted run: (who, op, arg); arg @X / #X resolved per run; BAN1 / TR1 literal keys
SCEN = [
    ("O", "name", "Alby"), ("O", "name", ""), ("O", "invite", "Alby"), ("O", "invite", ""), ("O", "invite", "Nobodyhere"),
    ("O", "trust", "Bea"), ("O", "trust", "Bea"), ("A", "decline", None), ("A", "decline", None), ("O", "invite", "Alby"),
    ("A", "accept", None), ("A", "accept", None), ("O", "promote", "@A"), ("O", "promote", "@A"), ("O", "demote", "@A"), ("O", "demote", "@A"),
    ("A", "promote", "@O"), ("A", "disband", None), ("A", "kick", "@A"), ("A", "kick", "@A"), ("O", "kick", "@A"), ("O", "refresh", None),
    ("O", "kick", "@A"), ("O", "name", "x"), ("O", "kick", "@A"), ("O", "kick", "@A"), ("O", "kick", "@A"), ("O", "invite", "Alby"),
    ("A", "accept", None), ("O", "untrust", "@B"), ("O", "untrust", "@B"), ("O", "untrust", TR1), ("O", "trust", "Alby"),
    ("O", "perm", "00v"), ("O", "perm", "00v"), ("O", "perm", "03m"), ("O", "perm", "05a"), ("O", "perm", "13t"), ("O", "perm", "99v"),
    ("A", "perm", "01t"), ("O", "permreset", None), ("O", "refresh", None), ("O", "permreset", None), ("O", "permreset", None),
    ("O", "mode", "0"), ("O", "mode", "2"), ("O", "mode", "1"), ("O", "mode", "1"), ("A", "mode", "0"),
    ("O", "limit", "1"), ("O", "limit", "1"), ("O", "limit", "-1"), ("A", "limit", "1"),
    ("O", "notify", None), ("O", "notify", None), ("O", "pvp", None), ("O", "pvp", None), ("O", "spawning", None), ("O", "spawning", None),
    ("A", "pvp", None), ("O", "unban", BAN1), ("O", "unban", BAN1), ("A", "unban", BAN2),
    ("O", "expel", "#C"), ("O", "expel", "#A"), ("O", "vtrust", "#C"), ("O", "vtrust", "#C"), ("A", "vtrust", "#B"),
    ("O", "ban", "#C"), ("O", "ban", "#C"), ("O", "ban", "#C"), ("O", "ban", "#A"), ("O", "ban", "#A"), ("O", "unban", "@C"),
    ("B", "leave", None), ("B", "leave", None), ("A", "leave", None), ("A", "name", "x"), ("A", "leave", None), ("A", "leave", None),
    ("O", "invite", "Alby"), ("A", "accept", None), ("O", "disband", None), ("O", "disband", None), ("O", "disband", None),
    ("A", "disband", None), ("O", "accept", None), ("B", "reset", None), ("O", "reset", None), ("O", "reset", None),
    ("O", "refresh", None), ("O", "reset", None), ("O", "name", "y")]
PAGE_OP = {"name": "name", "invite": "invite", "trust": "trust", "accept": "acc", "decline": "dec", "leave": "leave", "disband": "disb",
           "reset": "reset", "permreset": "pdef", "notify": "vn", "pvp": "ipvp", "spawning": "ispawn", "refresh": "refresh"}


def page_click(S, w, op, a):
    """one step through the REAL page: the payload the page's own button sends (row lists set as the page's build sets them)"""
    P = S.X[w]
    pg = S.open(w)
    d = None
    if op in ("name", "invite", "trust"):
        d = {"a": op, "@IsName": a}
    elif op in PAGE_OP:
        d = {"a": PAGE_OP[op]}
    elif op in ("promote", "demote", "kick"):
        rk = S.AL()
        rk.add(a)
        pg.rowKeys = rk
        d = {"a": {"promote": "pr", "demote": "dm", "kick": "kk"}[op] + "0"}
    elif op in ("untrust", "unban"):
        rk = S.AL()
        rk.add(a)
        if op == "untrust":
            pg.trustKeys = rk
        else:
            pg.banKeys = rk
        d = {"a": ("ut" if op == "untrust" else "vu") + "0"}
    elif op in ("expel", "vtrust", "ban"):
        rk = S.AL()
        rk.add(a)
        pg.visUuids = rk
        d = {"a": {"expel": "ve", "vtrust": "vt", "ban": "vb"}[op] + "0"}
    elif op == "mode":
        d = {"a": "vm" + a}
    elif op == "limit":
        d = {"a": "vlm" if a == "-1" else "vlp"}
    elif op == "perm":
        d = {"a": "pc" + a}
    pg.handleDataEvent(P.ref, P.st, json.dumps(d))
    S.E.pump(P)
    cur = S.E.pg(P)
    if cur is None:
        return ["CLOSED", ""]
    return [str(cur.info), str(cur.confirm)]


def parse(st):
    lines = str(st).split("\n")
    h = lines[0].split("|")
    return h, lines


def bridge_state(S, fn, w, arg=None):
    from jpype import JArray, JObject, JString
    u = S.UUID.fromString(NAMES[w][0])
    return str(fn.apply(JArray(JObject)([JString("state"), u, None, None, None if arg is None else JString(arg)])))


def bridge_call(S, fn, w, op, a, tok=None, pk=None, raw=False):
    from jpype import JArray, JObject, JString
    u = S.UUID.fromString(NAMES[w][0])
    if tok is None or pk is None:
        h, _l = parse(bridge_state(S, fn, w))
        tok = h[2] if tok is None else tok
        pk = h[3] if pk is None else pk
    return str(fn.apply(JArray(JObject)([JString(op), u, JString(tok), JString(pk), None if a is None else JString(a)])))


def shown_arg(S, fn, w, op, a):
    """the Menu's toggle / grid arg: the value the read shows"""
    h, lines = parse(bridge_state(S, fn, w))
    if op in ("notify", "pvp", "spawning"):
        return h[{"notify": 16, "pvp": 17, "spawning": 18}[op]]
    if op == "perm":
        fl, r = int(a[:2]), "vtma".index(a[2])
        for ln in lines:
            p = ln.split("|")
            if p[0] == "f" and int(p[1]) == fl:
                return a + "|" + ("1" if r >= int(p[3]) else "0")
        return a + "|1"
    return a


def bridge_click(S, fn, w, op, a, last):
    """one step through island:fn:act: a state read (token + profile key), the op; the stand-in screen shows whether it closed"""
    P = S.X[w]
    S.open(w)                                   # the Menu's screen stand-in (closing it is visible)
    arg = shown_arg(S, fn, w, op, a)
    if op != "refresh":                         # refresh answers before the double-click guard (it never counts as the last op)
        if last.get(w) == (op, arg):
            time.sleep(0.4)                     # a real second press (the 350 ms double-click guard is ACT's)
        last[w] = (op, arg)
    ans = bridge_call(S, fn, w, op, arg)
    S.E.pump(P)
    if S.E.pg(P) is None:
        return ["CLOSED", ""], ans
    h, _l = parse(bridge_state(S, fn, w))
    return [ans, h[25]], ans


def run_twin(out, jar, scratch, _home, tag):
    K = HK.Child(out)
    S = Stage(scratch, jar, "twin-" + tag)
    fn = S.E.bridge.get("island:fn:act")
    if tag == "bridge":
        fn = S.Act()
    rec, raw = [], []
    last = {}
    for w, op, a in SCEN:
        ra = resolve(S, a)
        try:
            if tag == "page":
                r = page_click(S, w, op, ra)
            else:
                r, an = bridge_click(S, fn, w, op, ra, last)
                raw.append([w, op, an])
        except Exception as ex:
            r = ["EXC %s" % ex, ""]
        # the invited line names the seconds left - drop them (both runs, timing only)
        r[0] = re.sub(r"\(\d+ s\)", "(N s)", re.sub(r"\d+ s left", "N s left", r[0]))
        rec.append([w, op, a] + r)
    mo = dict((str(k), str(S.IS.MEMBER_OF.get(k))) for k in S.IS.MEMBER_OF.keySet())
    K.save(rec=rec, raw=raw, files=S.files(), coop=mo)


def run_twin_page(out, jar, scratch, home):
    run_twin(out, jar, scratch, home, "page")


def run_twin_bridge(out, jar, scratch, home):
    run_twin(out, jar, scratch, home, "bridge")
    K = HK.Child(out)
    a = json.load(open(os.path.join(scratch, "twinpage.json")))
    b = json.load(open(out))
    K.eq(len(b["rec"]), len(SCEN), "TWIN every step ran on the bridge")
    K.eq(len(a["rec"]), len(SCEN), "TWIN every step ran on the page")
    diff = [(x, y) for x, y in zip(a["rec"], b["rec"]) if x != y]
    for x, y in diff[:6]:
        K.notes.append("page %s / bridge %s" % (x, y))
    K.check(not diff, "TWIN every step: the page's answer line + armed press = the bridge's (%d steps, %d differ)" % (len(SCEN), len(diff)))
    K.check(not [r for r in a["rec"] + b["rec"] if r[3].startswith("EXC") or "went wrong" in r[3]], "TWIN no step threw / went wrong")
    plus = [r for r in b["rec"] if r[3].startswith("+")]
    minus = [r for r in b["rec"] if r[3].startswith("-")]
    eq_ = [r for r in b["rec"] if r[3].startswith("=")]
    closed = [r for r in b["rec"] if r[3] == "CLOSED"]
    K.check(len(plus) >= 25 and len(minus) >= 20 and len(eq_) >= 10 and len(closed) == 1,
            "TWIN the run covers done / refused / question lines and one closing leave (%d + / %d - / %d = / %d closed)" % (len(plus), len(minus), len(eq_), len(closed)))
    leave = [r for r in b["raw"] if r[1] == "leave" and r[2].startswith("+")]
    K.check(len(leave) == 1 and "You left" in leave[0][2], "TWIN the closing leave answered the page's + line too: %s" % leave[:1])
    arms = sorted(set(r[4] for r in b["rec"] if r[4]))
    K.check({"disb", "leave", "pdef", "reset1", "reset2"} <= set(arms) and [x for x in arms if x.startswith("kk:")] and [x for x in arms if x.startswith("vb:")],
            "TWIN every confirm kind armed at least once: %s" % arms)
    K.check(a["files"] == b["files"] and len(b["files"]) >= 1, "TWIN the island files at the end = the page's (%d files)" % len(b["files"]))
    K.check(a["coop"] == b["coop"], "TWIN the co-op map at the end = the page's (%s)" % b["coop"])
    for r in b["rec"]:
        K.notes.append("step %s" % r)
    K.save(rec=b["rec"], files=b["files"])


# ---------------------------------------------------------------------------------------------------------------- ACT
def run_act(out, jar, scratch, _home):
    from jpype import JArray, JObject, JString, JClass
    K = HK.Child(out)
    S = Stage(scratch, jar, "act")
    E, IS, Act = S.E, S.IS, S.Act
    fn = Act()
    O, A, Bp, C = S.X["O"], S.X["A"], S.X["B"], S.X["C"]
    ko, ka = S.key("O"), S.key("A")

    def st(w, arg=None):
        return parse(bridge_state(S, fn, w, arg))

    def call(w, op, a=None, tok=None, pk=None):
        return bridge_call(S, fn, w, op, a, tok, pk)

    def settle():
        Act.LASTOP.clear()
    # ---- state lines
    h, lines = st("O")
    K.eq(len(h), 28, "ACT h line: 28 fields")
    K.check(h[1] == "1" and h[2] == ko and h[3] == ko and h[4] == "4" and h[5] == "1" and h[6] == "0" and h[7] == "1" and h[9] == "1" and h[11] == "2",
            "ACT h: has, token = profile key = the owner's key, Owner, own, readable, co-op 1, trusted 1, banned 2: %s" % h[:12])
    K.check(h[13] == "0" and h[25] == "" and h[26] == "0" and h[27] == "skyy-island-harness" and h[20] == "0", "ACT h: Public, nothing armed, the world, not loaded")
    kinds = [ln.split("|")[0] for ln in lines]
    K.check(kinds[1] == "n" and lines[1] == "n|Owner" and "c" in kinds and "d" in kinds, "ACT n / c / d lines: %s" % kinds[:6])
    K.eq(kinds.count("f"), len(list(S.J("IslandPerms").LABELS)), "ACT one f line per permission row")
    K.eq(kinds.count("m"), 1, "ACT m: the owner row")
    m0 = [ln for ln in lines if ln.startswith("m|")][0].split("|")
    K.check(m0[1] == ko and m0[2] == "4" and m0[3] == "1" and m0[6] == "1" and m0[7] == "Owner", "ACT m: owner first, role 4, online, me: %s" % m0)
    K.check([ln for ln in lines if ln.startswith("b|%s|Bannie" % BAN1)] and kinds.count("b") == 2 and kinds.count("t") == 1, "ACT b / t lines")
    rr = [ln for ln in lines if ln.startswith("r|")]
    K.check(rr == ["r|"], "ACT r: the owner may reset now (%s)" % rr)
    s = IS.settings(JString(ko))
    s.names.put(JString(BAN2), JString("Pipe|Name"))
    h2, l2 = st("O", "0|0|0|1")
    c = [ln for ln in l2 if ln.startswith("c|")][0].split("|")
    K.check(c[1:] == ["0", "1", "0", "1", "0", "0", "1", "2"] and len([x for x in l2 if x.startswith("b|")]) == 1 and not [x for x in l2 if x.startswith("m|") or x.startswith("t|")],
            "ACT caps 0|0|0|1: c line %s, one b line" % c)
    h3, l3 = st("O", "0|0|0|5")
    K.check([x for x in l3 if x == "b|%s|Pipe|Name" % BAN2], "ACT a '|' in the last field is kept")
    s.names.remove(JString(BAN2))
    ha, la = st("A")
    K.check(ha[1] == "0" and ha[5] == "1" and ha[4] == "4" and not [x for x in la if x.startswith("f|")], "ACT a player without an island: has 0, own 1 (the Create view), no grid")
    # invite: the i line
    K.check(call("O", "invite", "Alby").startswith("+Invited Alby"), "ACT invite Alby")
    ha, la = st("A")
    il = [x for x in la if x.startswith("i|")]
    K.check(il and il[0].split("|")[2] == "1" and il[0].endswith("|Owner") and il[0].split("|")[4] == "Owner", "ACT i line for the invited player: %s" % il)
    hp = [x for x in st("O")[1] if x.startswith("p|")]
    K.check(hp and hp[0].startswith("p|Alby ("), "ACT p line (invited text) for the owner: %s" % hp)
    # offline state: no i / r lines, still answers
    E.UniH.PL.remove(A.pr)
    E.PLAYERS.remove(A.pr)
    byU = HT.jf(JClass("com.hypixel.hytale.server.core.universe.Universe").class_, "playersByUuid").get(JClass("com.hypixel.hytale.server.core.universe.Universe").get())
    byU.remove(A.pr.getUuid())
    ho, lo = st("A")
    K.check(ho[0] == "h" and not [x for x in lo if x.startswith("i|")], "ACT offline: state answers without an i line")
    K.eq(call("A", "accept", None, ho[2], ho[3]), "-You are not online.", "ACT offline: refused")
    byU.put(A.pr.getUuid(), A.pr)
    E.UniH.PL.add(A.pr)
    E.PLAYERS.add(A.pr)
    K.check(call("A", "accept").startswith("+You joined"), "ACT accept")
    settle()
    # ---- refusals before any op
    Act.CLOSED = True
    K.check(call("O", "kick", ka).startswith("-Islands are shutting down"), "ACT closing: refused")
    Act.CLOSED = False
    K.check(call("O", "kick", ka, tok="other").startswith("=Your island changed"), "ACT stale token")
    K.check(call("O", "kick", ka, pk="other").startswith("=Your profile changed"), "ACT changed profile key")
    K.check(call("O", "kick", ka, tok=None, pk=None) .startswith("=Click Sure?"), "ACT kick arms")
    K.eq(st("O")[0][25], "kk:" + ka, "ACT armed kk:<key>")
    K.eq(call("O", "kick", ka), "=One moment.", "ACT the same press within 350 ms = One moment")
    K.eq(st("O")[0][25], "kk:" + ka, "ACT the double click keeps the arm")
    settle()
    K.check(call("O", "kick", ka, tok="other").startswith("=Your island changed") and st("O")[0][25] == "", "ACT a stale token drops the arm")
    settle()
    call("O", "kick", ka)
    arm = Act.ARM.get(JString(UO))
    K.check(arm is not None and 9000 <= int(arm[3]) - int(JClass("java.lang.System").currentTimeMillis()) <= 10000, "ACT the kick arm lasts 10 s")
    arm[3] = JClass("java.lang.Long")(1)
    settle()
    K.check(call("O", "kick", ka).startswith("=Click Sure?") and IS.contains(IS.settings(JString(ko)).members, JString(ka)), "ACT an expired arm re-arms (no kick)")
    settle()
    K.check(call("O", "name", "x").startswith("=Click Invite") and st("O")[0][25] == "", "ACT another op drops the arm")
    settle()
    K.check(call("O", "kick", ka).startswith("=Click Sure?"), "ACT kick arms again")
    arm = Act.ARM.get(JString(UO))
    arm[1] = JString("another-profile")
    settle()
    K.check(call("O", "kick", ka).startswith("=Click Sure?") and IS.contains(IS.settings(JString(ko)).members, JString(ka)), "ACT an arm from another profile does not confirm")
    settle()
    # the world thread
    S.thread(S.Thread())
    f0 = S.files()
    K.check(call("O", "mode", "2").startswith("-That has to run from the island screen"), "ACT not the world thread: refused")
    K.eq(S.files(), f0, "ACT not the world thread: nothing changed")
    S.thread(S.Thread.currentThread())
    ext = HT.jf(O.st.getClass(), "externalData")
    ev = ext.get(O.st)
    ext.set(O.st, None)
    K.check(call("O", "mode", "2").startswith("-You are not in a world right now"), "ACT no world: refused")
    ext.set(O.st, ev)
    settle()
    # stale toggles / grid cells
    f0 = S.files()
    h = st("O")[0]
    K.eq(call("O", "pvp", "1" if h[17] == "0" else "0"), "=That changed since you looked - look again. Nothing changed.", "ACT a stale PvP toggle is refused")
    K.eq(call("O", "notify", ""), "=That changed since you looked - look again. Nothing changed.", "ACT a toggle without the shown value is refused")
    K.eq(call("O", "spawning", "x"), "=That changed since you looked - look again. Nothing changed.", "ACT a toggle with a bad shown value is refused")
    line0 = [x for x in st("O")[1] if x.startswith("f|0|")][0].split("|")
    yes0 = "1" if 0 >= int(line0[3]) else "0"
    K.eq(call("O", "perm", "00v|" + ("0" if yes0 == "1" else "1")), "=That changed since you looked - look again. Nothing changed.", "ACT a stale grid cell is refused")
    K.eq(S.files(), f0, "ACT the stale clicks changed nothing on disk")
    K.check(call("O", "perm", "00v|" + yes0).startswith("+"), "ACT the fresh grid cell runs clickPerm")
    for bad in ("00", "0xv|1", "00q|1", "00v"):
        settle()
        K.eq(call("O", "perm", bad), "-Unknown permission.", "ACT perm %r: unknown permission" % bad)
    settle()
    K.eq(call("O", "limit", "5"), "-Unknown island action.", "ACT limit 5: refused")
    K.eq(call("O", "kick", ""), "-That player is not a co-op member here.", "ACT kick without a key")
    K.eq(call("O", "expel", "not-a-uuid"), "-That player is not online any more.", "ACT expel a non-UUID")
    K.check(call("O", "mode", "x").startswith("-Unknown visit mode"), "ACT mode x: unknown visit mode")
    K.eq(call("O", "fly"), "-Unknown island action.", "ACT unknown op")
    for o_ in (None, JString("x"), JArray(JObject)([]), JArray(JObject)([JString("kick")]), JArray(JObject)([JString("kick"), JString("not-a-uuid")])):
        r = str(fn.apply(o_))
        K.check(r.startswith("-"), "ACT bad call %s -> %s" % (o_, r[:40]))
    K.check(str(fn.apply(JArray(JObject)([JString("state"), JString(UO)]))).startswith("h|1|"), "ACT a UUID as text works (state)")
    K.eq(call("O", "refresh"), "", "ACT refresh answers ''")
    # isl1fix: refresh (the Menu sends it on open / tab change / close) drops every armed confirm - a reopened screen starts at press 1
    settle()
    K.check(call("O", "kick", ka).startswith("=Click Sure?"), "FIX kick arms")
    K.eq(call("O", "refresh"), "", "FIX refresh after the kick arm")
    K.eq(st("O")[0][25], "", "FIX refresh drops the kick arm")
    settle()
    K.check(call("O", "kick", ka).startswith("=Click Sure?") and IS.contains(IS.settings(JString(ko)).members, JString(ka)),
            "FIX after refresh one Kick press only re-arms (the member stays)")
    call("O", "refresh")
    settle()
    f0 = S.files()
    K.check(call("O", "reset").startswith("=This DELETES"), "FIX reset press 1")
    time.sleep(0.4)
    K.check(call("O", "reset").startswith("=Last warning"), "FIX reset press 2")
    K.eq(st("O")[0][25], "reset2", "FIX armed reset2")
    K.eq(call("O", "refresh"), "", "FIX refresh (the screen closed / reopened)")
    K.eq(st("O")[0][25], "", "FIX refresh drops the reset2 arm")
    time.sleep(0.4)
    K.check(call("O", "reset").startswith("=This DELETES"), "FIX after refresh the next Reset press is press 1 again (no resetNow)")
    K.eq(S.files(), f0, "FIX the refreshed reset changed nothing on disk")
    for op_, a_ in (("permreset", None), ("disband", None)):
        call("O", "refresh")
        settle()
        r1 = call("O", op_, a_)
        armd = st("O")[0][25]
        call("O", "refresh")
        K.check(st("O")[0][25] == "", "FIX refresh drops the %s arm (%r, was %r)" % (op_, r1[:40], armd))
    call("O", "refresh")
    settle()
    # isl1fix: arming prunes expired arms and old double-click stamps of other players
    Long = JClass("java.lang.Long")
    nowj = int(JClass("java.lang.System").currentTimeMillis())
    Act.ARM.put(JString("ghost-expired"), JArray(JObject)([JString("kk:x"), JString("p"), JString("t"), Long(1)]))
    Act.ARM.put(JString("ghost-live"), JArray(JObject)([JString("kk:x"), JString("p"), JString("t"), Long(nowj + 60000)]))
    Act.LASTOP.put(JString("ghost-old"), JArray(JObject)([JString("x|"), Long(1)]))
    Act.LASTOP.put(JString("ghost-new"), JArray(JObject)([JString("x|"), Long(nowj + 60000)]))
    K.check(call("O", "kick", ka).startswith("=Click Sure?"), "FIX kick arms (prune runs)")
    K.check(not Act.ARM.containsKey(JString("ghost-expired")) and Act.ARM.containsKey(JString("ghost-live")), "FIX prune drops an expired arm, keeps a live one")
    K.check(not Act.LASTOP.containsKey(JString("ghost-old")) and Act.LASTOP.containsKey(JString("ghost-new")) and Act.LASTOP.containsKey(JString(UO)),
            "FIX prune drops an old double-click stamp, keeps fresh ones")
    K.eq(st("O")[0][25], "kk:" + ka, "FIX the new arm is kept after the prune")
    Act.ARM.remove(JString("ghost-live"))
    Act.LASTOP.remove(JString("ghost-new"))
    call("O", "refresh")
    # reset: the arm lasts reset.confirmSeconds; the third press runs resetNow
    settle()
    rc = int(S.J("IslandCfg").RESET_CONFIRM)
    K.check(call("O", "reset").startswith("=This DELETES"), "ACT reset press 1")
    arm = Act.ARM.get(JString(UO))
    K.check(arm is not None and str(arm[0]) == "reset1" and rc * 1000 - 1000 <= int(arm[3]) - int(JClass("java.lang.System").currentTimeMillis()) <= rc * 1000,
            "ACT the reset arm lasts reset.confirmSeconds (%d s)" % rc)
    time.sleep(0.4)
    K.check(call("O", "reset").startswith("=Last warning"), "ACT reset press 2")
    time.sleep(0.4)
    S.open("O")
    r3 = call("O", "reset")
    K.notes.append("third reset press: %s" % r3)
    K.check(r3.startswith("-") or r3.startswith("+"), "ACT reset press 3 runs resetNow: %s" % r3[:100])
    # create / go: the page's calls, the screen closes, answer ''
    settle()
    S.open("C")
    gc = call("C", "create")
    K.check(gc == "" or gc.startswith("-Something"), "ACT create answered %r" % gc[:80])
    K.notes.append("create: %r, screen open after: %s" % (gc, E.pg(C) is not None))
    settle()
    S.open("O")
    gg = call("O", "go")
    K.notes.append("go: %r, screen open after: %s" % (gg, E.pg(O) is not None))
    K.check(gg == "" and E.pg(O) is None, "ACT go: answered '' and the screen is closed")
    K.check(gc == "" and E.pg(C) is None, "ACT create: answered '' and the screen is closed")
    # the bytecode: act calls the page's methods
    import perfworld_kit as PW
    g = PW.calls(jar)
    want = ["IslandCoop." + m for m in ("accept", "decline", "leave", "disband", "disbandProblem", "resetCheck", "resetNow", "resetWarning",
                                        "invite", "trust", "promoteKey", "kickByKey", "untrustByKey", "unbanByKey", "setMode", "changeLimit",
                                        "toggleNotify", "togglePvp", "toggleSpawning", "clickPerm", "resetPerms", "expelOn", "ban")] + \
           ["IslandCmd.go", "IslandCmd.goHome", "IslandStore.findOnline", "IslandStore.cleanName", "IslandStore.tell", "IslandActFn.close"]
    miss = [m for m in want if PKG + m not in g.get("IslandActFn.act", set())]
    K.check(not miss, "ACT the bytecode: act calls the page's methods (%d): missing %s" % (len(want), miss))
    K.check(PKG + "IslandCoop.inviteFor" in g.get("IslandActFn.state", set()) and PKG + "IslandCoop.acceptProblem" in g.get("IslandActFn.state", set())
            and PKG + "IslandCoop.pendingText" in g.get("IslandActFn.state", set()), "ACT the bytecode: state reads the page's helpers")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- live
def run_liveact(out, jar, scratch, home):
    from jpype import JArray, JObject, JString
    K = HK.Child(out)
    h0 = HK.tree_hash(home)
    E, J = T18.setup(os.path.join(scratch, "liveact"), jar, home)
    fn = J("IslandActFn")()
    d = os.path.join(home, "islands")
    owners = [f[:-11] for f in sorted(os.listdir(d)) if f.endswith(".properties") and len(f) == 36 + 11] if os.path.isdir(d) else []
    K.check(bool(owners), "LIVEACT the copy has island owners (%d)" % len(owners))
    bad = []
    for o in owners:
        r = str(fn.apply(JArray(JObject)([JString("state"), E.UUID.fromString(o), None, None, None])))
        h = r.split("\n")[0].split("|")
        if len(h) != 28 or h[0] != "h":
            bad.append((o, r[:80]))
    K.check(not bad, "LIVEACT state answers 28 header fields for every owner (%d): %s" % (len(owners), bad[:3]))
    K.check(HK.tree_hash(home) == h0, "LIVEACT nothing changed on disk")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("twinpage", run_twin_page), ("twinbridge", run_twin_bridge), ("act", run_act),
                   ("data", T26.run_data), ("shift", T26.run_shift), ("retry", T26.run_retry), ("place", T26.run_place), ("fix", T26.run_fix),
                   ("cmd", T26.run_cmd), ("archi", T25.run_archi), ("door", T25.run_door), ("fix2", T25.run_fix2), ("life", T25.run_life),
                   ("cfg", T25.run_cfg), ("unload", T24.run_unload), ("early", T23.run_early), ("ids", T23.run_ids), ("boss", T23.run_boss),
                   ("clear", T23.run_clear), ("time", T23.run_time), ("live", T26.run_live26), ("liveact", run_liveact), ("live2", T25.run_live2)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyIslands"))
