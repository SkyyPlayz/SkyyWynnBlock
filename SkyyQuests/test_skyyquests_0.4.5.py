"""SkyyQuests 0.4.5 harness (the bridge quest:fn:act - World > Quests' reads + clicks for SkyyMenu's new World tab;
tools/quests_0_4_5_patch.py) on top of the 0.4.4 harness (test_skyyquests_0.4.4.py -> 0.4.3 -> ... -> 0.3: every older phase runs again on
the 0.4.5 jar).

    python SkyyQuests/test_skyyquests_0.4.5.py [--keep] [--only twin45,act45,...]

  A / C / AA  verify (-Xverify:all), class compare 0.4.4 -> 0.4.5 (QActFn added; setup / shutdown + the version texts), engine-access audit
  S45   static45  the patch re-runs to identical bytes, line endings kept, one class added, no new command / system; setup puts quest:fn:act
                  (CLOSED reset first); shutdown sets CLOSED first and removes the key; QActFn.act calls the page's QEng.action /
                  claimTask (bytecode) and reaches no file call / sleep
  TW45  twin45    TWO players on the REAL engine (tools/hub_tab_kit stand-ins, the real QLogPage + PageManager): A clicks World > Quests
                  (QLogPage.handleDataEvent), B sends quest:fn:act (state read first for the token / profile key / shown flags, like the
                  Menu). Scripted (track / untrack, skip / unskip, claim1, claim all, hide / show, the payer paying) + 400 random clicks:
                  the SAME answer after every step, the same task rows / track / skips / claims / coins paid. READ = PAGE: the bridge's
                  state for A = what A's page draws (line list order + names + x / y + lock text, Open + Done tab task names in order +
                  progress, the task panel's reward / hint / where / state, Claim all (n), the tracked line)
  ACT45 act45     the bridge's own rules: state lines (h 8 fields, l / w / t / x), not online, still loading (ready 0 + refused),
                  changed profile key, stale token (a /questadmin reload), stale track / skip flags (nothing flips), the 350 ms double
                  click, closing, unknown op / bad arguments / non-array / null / a UUID string, refresh, never throws
  LIVE45 live45   START TWICE on a scratch COPY of the live Skyy_SkyyQuests (NewBetaTest): no file written; every live profile's
                  quest:fn:act state answers (ready, the lines) and reading it writes nothing
  OLD   every 0.4.4 phase on the 0.4.5 jar (archi44 have44 fs44 live44 wid43 ... live41); live44's "start 1 writes the archipelago
        file" is waived when the live world already has it (0.4.4 is deployed there - LIVE45 checks start 1 + 2 write nothing)
Scratch: tools/dev/scratch/wbr1/quests (deleted unless --keep). Exit 1 on any failure.
"""
import os, sys, re, json, random, shutil, subprocess, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.4.5"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "wbr1", "quests")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)]
import harness_kit as HK
import skyybuild as B
import perfworld_kit as PW

_spec = importlib.util.spec_from_file_location("test_skyyquests_0_4_4", os.path.join(HERE, "test_skyyquests_0.4.4.py"))
T044 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T044)
T043, T040, T03 = T044.T043, T044.T040, T044.T03

JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyQuests-0.4.4.jar")
GEN = os.path.join(HERE, "build_skyyquests_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyquests_0.4.4.py")
PATCH = os.path.join(TOOLS, "quests_0_4_5_patch.py")
SCRATCH, FAKE_DIR, PKG = T03.SCRATCH, T03.FAKE_DIR, T03.PKG
EXPECT = {"SkyyQuestsPlugin": ["~m setup", "~m shutdown"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]}
ADDED = ["QActFn"]

# the live world already runs 0.4.4: its quests/archipelago.properties exists, so 0.4.4's "start 1 writes it" cannot hold there
_LIVE_HAS = os.path.isfile(os.path.join(T040.LIVE_Q, "quests", "archipelago.properties"))
_W45 = ("LV44 start 1 writes exactly ONE new file",)
_chk044 = HK.Child.check


def _check45(self, cond, what):
    if not cond and _LIVE_HAS and str(what).startswith(_W45):
        self.notes.append("WAIVED (0.4.5: the live world already has archipelago.properties - LIVE45 checks start 1 + 2 write nothing): %s" % str(what)[:160])
        return cond
    return _chk044(self, cond, what)


HK.Child.check = _check45


# ---------------------------------------------------------------------------------------------------- helpers
def call(Fn, op, u, tok=None, pk=None, arg=None):
    from jpype import JArray, JObject, JString
    a = [JString(op), u, None if tok is None else JString(tok), None if pk is None else JString(pk), None if arg is None else JString(arg)]
    return str(Fn.apply(JArray(JObject)(a)))


def parse(st):
    """the state text -> {h: [...], l: [[...]], w: {...}, t: [[...]], x: {...}}"""
    r = {"h": None, "l": [], "w": {}, "t": [], "x": {}}
    for ln in st.split("\n"):
        k, _, rest = ln.partition("|")
        if k == "h":
            r["h"] = rest.split("|")
        elif k == "l":
            r["l"].append(rest.split("|", 5))
        elif k == "w":
            a, _, b = rest.partition("|")
            r["w"][a] = b
        elif k == "t":
            r["t"].append(rest.split("|", 9))
        elif k == "x":
            a, b, c = rest.split("|", 2)
            r["x"][(a, b)] = c
    return r


def snap(X, s, u, coins):
    """the state that matters (player-neutral): every line's task rows, track, skips, done keys, issued, claims, hideTut, coins paid"""
    pk = str(s.pk)
    rows = {}
    for L in X.Defs.LINES:
        if bool(L.daily):
            continue                           # the Daily Jobs: each player's own random picks of the day (not a click's doing)
        rows[str(L.id)] = [str(v) for v in s.rowsOf(L)]
    p = X.Eng.player(u)
    return {"rows": rows, "track": str(s.track), "skip": sorted(str(k) for k in s.skip.keySet()), "done": sorted(str(k) for k in s.done.keySet()),
            "issued": sorted(str(k) for k in s.issued), "claims": sorted(str(c).replace(pk, "<pk>").rsplit(":", 1)[0] for c in s.claims),
            "hide": bool(p.hideTut), "coins": list(coins.get(str(u), []))}


ZPAY = T040.ZPAY
ZTWO = ("line=ztwo\nname=Two Line\nauto=true\norder=5\n" + "".join(
    "task.%d.id=t%d\ntask.%d.name=Two task %d\ntask.%d.type=break\ntask.%d.match=Two_%d\ntask.%d.count=%d\ntask.%d.reward=coins:%d\n"
    "task.%d.hint=Break %d Two_%d blocks | anywhere\n" % (i, i, i, i, i, i, i, i, 3, i, 10 + i, i, 3, i) for i in range(1, 7)))


def stage(K, scratch, name):
    from jpype import JClass
    X = T040.QStage(K, scratch, name, extra_lines=(("zpay.properties", ZPAY), ("ztwo.properties", ZTWO), ("zbig.properties", T040.BIG_LINE)))
    PyFn = T03.fn_class()
    Long = JClass("java.lang.Long")
    coins = {}
    X.E.bridge.put("coins:fn:add", PyFn(lambda a: (coins.setdefault(str(a[0]), []).append(int(a[1])) or Long(1000))))
    X.E.bridge.put("profile:fn:key", PyFn(lambda a: str(a)))
    X.Sto.STOPPED = False
    return X, coins


# ---------------------------------------------------------------------------------------------------- S45
def run_static45(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyQuests 0.4.5 - build script') and g.count('VERSION = "0.4.5"') == 1, "S45 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.eq(g.count(w), o.count(w), "S45 no new %s" % w)
    K.eq(g.count(" = K(") - o.count(" = K("), 1, "S45 one class added (QActFn)")
    su = g[g.index("public void setup() {"):]
    su = su[:su.index("protected void shutdown()")]
    K.check(su.index("QActFn.CLOSED = false;") < su.index('b.put("quest:fn:act", new @PKG@.QActFn());'), "S45 setup: CLOSED reset, then quest:fn:act put")
    sd = g[g.index("protected void shutdown() {"):]
    K.check(sd.index("QActFn.CLOSED = true;") < sd.index('remove("quest:fn:act")') < sd.index("QTick.EXEC"), "S45 shutdown: CLOSED first, key removed")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S45 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S45 line endings kept")
    HK.jvm([B.JAVASSIST, B.SERVER_JAR], verify=False)
    gr = PW.calls(jar)
    a = gr.get("QActFn.act", set())
    K.check({PKG + "QEng.action", PKG + "QEng.claimTask", PKG + "QEng.findTask"} <= a, "S45 QActFn.act calls the page's QEng.action / claimTask / findTask")
    st = gr.get("QActFn.state", set())
    K.check({PKG + "QLogPage.after", PKG + "QLogPage.lockWhy", PKG + "QLogPage.words", PKG + "QLogPage.placeName", PKG + "QState.rowsOf"} <= st,
            "S45 QActFn.state reads through the page's own helpers (after / lockWhy / words / placeName) and QState.rowsOf")
    IO = set(PW.IO_TARGETS) | {"java.nio.file.Files.createDirectories", "java.nio.file.Files.exists"}
    for h in ("QActFn.apply", "QActFn.state"):
        r = PW.reach(gr, h, PKG)
        bad = sorted(m for m in r if any(c in IO for c in gr.get(m, ())))
        sl = sorted(m for m in r if any(c in PW.SLEEP for c in gr.get(m, ())))
        K.check(h in gr and not bad and not sl, "S45 %s reaches no file call / sleep (%d methods): %s %s" % (h, len(r), bad, sl))
    K.save()


# ---------------------------------------------------------------------------------------------------- TW45
def run_twin45(out, jar, scratch, home):
    from jpype import JClass, JLong
    K = HK.Child(out)
    X, coins = stage(K, scratch, "tw")
    Eng, Defs, Pay = X.Eng, X.Defs, X.Pay
    Fn = X.P("QActFn")()
    Act = X.P("QActFn")
    TB = T044.TB
    PlA, uA, pA, sA = X.player(1, "PageA")
    PlB, uB, pB, sB = X.player(2, "BridgeB")
    pg = X.open(PlA)
    K.check(pg is not None, "TW the World > Quests page opens for A")
    nsteps = [0]
    diffs = []
    TRACE = []

    def both_events(ev):
        for u in (uA, uB):
            Eng.count(u, TB["break"], ev, 1, "w", False)
        Eng.rebuild(uA, sA)
        Eng.rebuild(uB, sB)

    def bread():
        return parse(call(Fn, "state", uB))

    def page_do(steps):
        nonlocal pg
        for a in steps:
            pg = X.click(PlA, pg, a)
            TRACE.append((a, str(pg.line), str(pg.task), int(pg.sub), str(pg.info)[:40]))
        return str(pg.info)

    def bridge(op, arg):
        Act.LASTOP.clear()                     # a person clicks slower than 350 ms (the ACT phase checks the guard itself)
        h = bread()["h"]
        return call(Fn, op, uB, h[0], h[1], arg)

    def cmp(what, ra, rb):
        nsteps[0] += 1
        sa, sb = snap(X, sA, uA, coins), snap(X, sB, uB, coins)
        if ra != rb or sa != sb:
            dk = [k for k in sa if sa[k] != sb[k]]
            det = [(ln, sa["rows"][ln], sb["rows"][ln]) for ln in sa["rows"] if sa["rows"][ln] != sb["rows"][ln]][:1] if "rows" in dk else []
            diffs.append((what, ra, rb, dk, det, TRACE[-6:], X.E.logs[-3:] if hasattr(X.E, "logs") else ""))

    def track(line):
        ra = page_do(["line:" + line, "track"])
        shown = "1" if bread()["h"][3] == line else "0"
        rb = bridge("track", line + "|" + shown)
        cmp("track " + line, ra, rb)

    def subof(line, task):
        st = [t for t in bread()["t"] if t[0] == line and t[1] == task]
        return "sub:done" if st and st[0][2] == "2" else "sub:open"      # the page's tab that lists the task

    def skip(line, task):
        ra = page_do(["line:" + line, subof(line, task), "task:" + task, "skip"])
        st = [t for t in bread()["t"] if t[0] == line and t[1] == task]
        shown = "1" if st and st[0][2] == "3" else "0"
        rb = bridge("skip", line + "." + task + "|" + shown)
        cmp("skip %s.%s" % (line, task), ra, rb)

    def claim1(line, task):
        ra = page_do(["line:" + line, subof(line, task), "task:" + task, "claim1"])
        rb = bridge("claim1", line + "." + task)
        cmp("claim1 %s.%s" % (line, task), ra, rb)

    def simple(a):
        ra = page_do([a])
        rb = bridge(a, None)
        cmp(a, ra, rb)

    def pay(t):
        Pay.payAll(JLong(t))
        cmp("pay", "", "")

    # ---- scripted: every page action
    tut = [t[1] for t in bread()["t"] if t[0] == "tutorial"][1]     # a task the page lists (the page acts only on what it shows)
    track("ztwo")
    track("ztwo")                                  # untrack
    track("zpay")
    track("tutorial")
    skip("ztwo", "t2")
    skip("ztwo", "t2")                             # unskip
    skip("tutorial", tut)
    skip("ztwo", "t5")
    simple("hide")
    simple("hide")
    simple("show")
    claim1("zpay", "pa")                           # nothing waits yet
    simple("claim")                                # nothing waits yet
    both_events("Pay_A")
    both_events("Pay_B")
    for i in range(3):
        both_events("Two_1")
    pay(int(time.time() * 1000))                   # pays now (coins:fn:add answers)
    both_events("Two_2")
    both_events("Two_2")
    both_events("Two_2")
    claim1("ztwo", "t2")
    simple("claim")
    pay(int(time.time() * 1000) + 2000)
    skip("ztwo", "t1")                             # a done task: "already done"
    K.check(not diffs, "TW scripted: the SAME answer and the same state after every step (%d steps): %s" % (nsteps[0], diffs[:3]))
    K.check(sum(coins.get(str(uA), [])) == sum(coins.get(str(uB), [])) > 0, "TW scripted: both paid the same coins (%s / %s)" % (coins.get(str(uA)), coins.get(str(uB))))
    # ---- READ = PAGE (A's own page vs the bridge read for A)
    readpage(K, X, PlA, uA, Fn)
    pg = X.E.pg(PlA)                               # readpage opened its own World > Quests page: click on that one from here on
    # ---- random clicks
    rnd = random.Random(45)
    lines = ["tutorial", "zpay", "ztwo", "zbig"]
    evs = ["Two_%d" % i for i in range(1, 7)] + ["Big_%d" % i for i in range(1, 12)] + ["Pay_A", "Pay_B"]
    n0 = nsteps[0]
    for i in range(400):
        r = rnd.random()
        L = rnd.choice(lines)
        tasks = [t[1] for t in bread()["t"] if t[0] == L] or [str(Defs.line(L).tasks[0].id)]   # the tasks the page lists
        if r < 0.18:
            track(L)
        elif r < 0.45:
            skip(L, rnd.choice(tasks))
        elif r < 0.6:
            claim1(L, rnd.choice(tasks))
        elif r < 0.68:
            simple(rnd.choice(["claim", "hide", "show"]))
        elif r < 0.95:
            both_events(rnd.choice(evs))
        else:
            pay(int(time.time() * 1000) + 3000 * i)
    K.check(not diffs, "TW 400 random clicks: the SAME answer and the same state every time (%d steps): %s" % (nsteps[0] - n0, diffs[:3]))
    K.check(sum(coins.get(str(uA), [])) == sum(coins.get(str(uB), [])), "TW random: the same coins paid (%d)" % sum(coins.get(str(uA), [])))
    readpage(K, X, PlA, uA, Fn, tag="after the random run")
    K.notes.append("TW %d twin steps, coins %s" % (nsteps[0], sum(coins.get(str(uA), []))))
    K.save()


def readpage(K, X, Pl, u, Fn, tag="scripted"):
    """the bridge read for u = what u's World > Quests page draws"""
    pg = X.open(Pl)
    st = parse(call(Fn, "state", u))
    s = X.Eng.stateOf(X.Eng.player(u))
    apps, sets, evs, _c = X.built(pg, Pl, "READ " + tag)
    nl = len(T040.line_rows(apps))
    K.eq([sets.get("#SkyyQlLN%d.Text" % i) for i in range(nl)], [l[5] for l in st["l"]], "READ %s: the line list (names, order)" % tag)
    want_sub = []
    for l in st["l"]:
        if l[1] == "2":
            want_sub.append(st["w"][l[0]])
        else:
            want_sub.append("(tracked on HUD)" if l[1] == "0" else ("All done" if l[1] == "3" else ""))
    K.eq([sets.get("#SkyyQlLS%d.Text" % i) for i in range(nl)], want_sub, "READ %s: the line sub texts (tracked / all done / how to start)" % tag)
    K.eq([sets.get("#SkyyQlLC%d.Text" % i) for i in range(nl) if st["l"][i][1] != "2"],
         ["%s / %s" % (l[2], l[3]) for l in st["l"] if l[1] != "2"], "READ %s: x / y per open line" % tag)
    K.eq(st["h"][5], str(int(s.claimCount())), "READ %s: claims waiting" % tag)
    if int(s.claimCount()) > 0:
        K.eq(sets.get("#SkyyQlClaim.Text"), "Claim all (%s)" % st["h"][5], "READ %s: Claim all (n)" % tag)
    bad = []
    for l in st["l"]:
        if l[1] == "2":
            continue
        lid = l[0]
        rows = [t for t in st["t"] if t[0] == lid]
        for sub, keep in ((0, lambda t: t[2] in ("0", "1", "4")), (1, lambda t: t[2] == "2")):
            pg = X.click(Pl, pg, "line:" + lid)
            pg = X.click(Pl, pg, "sub:open" if sub == 0 else "sub:done")
            apps, sets, evs, _c = X.built(pg, Pl, "READ %s %s sub %d" % (tag, lid, sub))
            want = [t for t in rows if keep(t)] + ([t for t in rows if t[2] == "3"] if sub == 0 else [])
            n = len(T040.task_rows(apps))
            got = [sets.get("#SkyyQlN%d.Text" % i) for i in range(n)]
            wn = [(t[4] + "  " if t[4] else "") + t[9] + ("  (optional)" if t[3] == "1" else "") for t in want]
            if got != wn:
                bad.append(("names", lid, sub, got[:4], wn[:4]))
            for i, t in enumerate(want[:n]):
                if t[2] in ("0", "2", "3", "4"):
                    ps = "Done" if t[2] == "2" else ("Skipped" if t[2] == "3" else t[5].replace("/", " / "))
                    if sets.get("#SkyyQlP%d.Text" % i) != ps:
                        bad.append(("prog", lid, t[1], sets.get("#SkyyQlP%d.Text" % i), ps))
            for i, t in enumerate(want[:3]):
                pg = X.click(Pl, pg, "task:" + t[1])
                apps, sets, evs, _c = X.built(pg, Pl, "READ panel")
                rw = t[8]
                rwt = "No reward" if not rw else ("Paid: " + rw if t[2] == "2" else ("Waiting: " + rw if t[2] == "1" else rw))
                wh = "Where: " + t[7] if t[7] else ""
                hint = st["x"].get((lid, t[1]), "")
                sx = {"1": "Ready to claim - your reward is waiting", "2": "Done", "3": "Skipped - it still counts and pays if you do it later",
                      "4": "Next in line - its progress already counts"}.get(t[2], "Open (optional)" if t[3] == "1" else "Open")
                got3 = (sets.get("#SkyyQlDRew.Text"), sets.get("#SkyyQlDWhere.Text"), sets.get("#SkyyQlDHint.Text"), sets.get("#SkyyQlDState.Text"))
                if got3 != (rwt, wh, hint, sx):
                    bad.append(("panel", lid, t[1], got3, (rwt, wh, hint, sx)))
    K.check(not bad, "READ %s: every line's Open + Done task rows, progress and task panel = the bridge's t / x lines: %s" % (tag, bad[:3]))
    tr = str(s.track)
    K.eq(st["h"][3], tr, "READ %s: the tracked line" % tag)


# ---------------------------------------------------------------------------------------------------- ACT45
def run_act45(out, jar, scratch, home):
    from jpype import JClass, JArray, JObject, JString
    K = HK.Child(out)
    X, coins = stage(K, scratch, "ac")
    Eng, Defs = X.Eng, X.Defs
    Act = X.P("QActFn")
    Fn = Act()
    Pl, u, p, s = X.player(3, "Act")
    st = parse(call(Fn, "state", u))
    h = st["h"]
    K.check(len(h) == 8 and h[0].startswith("q") and h[1] == str(u) and h[2] == "1" and int(h[7]) == len(st["l"]) >= 3, "ACT state header: %s" % h)
    K.check(all(len(l) == 6 for l in st["l"]) and all(len(t) == 10 for t in st["t"]), "ACT every l line has 6 fields, every t line 10")
    two = [t for t in st["t"] if t[0] == "ztwo"]
    K.check(len(two) == 6 and two[0][9] == "Two task 1" and two[0][5] == "0/3" and two[0][6] == "0" and st["x"][("ztwo", "t1")] == "Break 3 Two_1 blocks | anywhere",
            "ACT t rows: name, progress 0/3, fill 0, the hint keeps its '|': %s / %s" % (two[0], st["x"].get(("ztwo", "t1"))))
    K.check(two[0][8] == "11 coins", "ACT the reward in the page's words: %s" % two[0][8])
    tok, pk = h[0], h[1]
    K.eq(call(Fn, "refresh", u, tok, pk), "", "ACT refresh answers ''")
    K.eq(call(Fn, "track", u, tok, pk, "ztwo|0"), "+Tracking Two Line in your quest widget.", "ACT track")
    K.eq(call(Fn, "track", u, tok, pk, "ztwo|0"), "=One moment.", "ACT the same op + arg within 350 ms = One moment (nothing runs twice)")
    K.eq(str(s.track), "ztwo", "ACT ... the line stays tracked")
    Act.LASTOP.clear()
    K.eq(call(Fn, "track", u, tok, pk, "ztwo|0"), "=That changed since you looked - look again. Nothing changed.", "ACT a stale track (shown untracked, it is tracked) flips nothing")
    K.eq(str(s.track), "ztwo", "ACT ... still tracked")
    Act.LASTOP.clear()
    K.check(call(Fn, "skip", u, tok, pk, "ztwo.t3|1").startswith("=That changed") and not bool(s.isSkipped("ztwo.t3")), "ACT a stale skip (shown skipped, it is not) changes nothing")
    Act.LASTOP.clear()
    K.check(call(Fn, "skip", u, tok, pk, "ztwo.t3|0").startswith("+Skipped") and bool(s.isSkipped("ztwo.t3")), "ACT skip")
    for arg, want in (("ztwo", "-Pick a quest line first."), ("ztwo|x", "-Pick a quest line first."), ("|1", "-Pick a quest line first.")):
        Act.LASTOP.clear()
        K.eq(call(Fn, "track", u, tok, pk, arg), want, "ACT bad track argument %r" % arg)
    Act.LASTOP.clear()
    K.eq(call(Fn, "skip", u, tok, pk, "nope.nope|0"), "-No task 'nope.nope' (see /quests).", "ACT skip: an unknown task")
    Act.LASTOP.clear()
    K.eq(call(Fn, "skip", u, tok, pk, "ztwo.t3"), "=Pick a task first.", "ACT skip without the shown flag")
    for arg in ("", "ztwo", "ztwo.", ".t1"):
        Act.LASTOP.clear()
        K.eq(call(Fn, "claim1", u, tok, pk, arg), "=Pick a task first.", "ACT claim1 %r" % arg)
    Act.LASTOP.clear()
    K.eq(call(Fn, "claim1", u, tok, pk, "ztwo.t1"), "=Nothing is waiting for Two task 1.", "ACT claim1: the page's own answer")
    Act.LASTOP.clear()
    K.eq(call(Fn, "frob", u, tok, pk, ""), "-Unknown quest action.", "ACT unknown op")
    K.check(call(Fn, "track", u, tok, "someone-else", "zpay|0").startswith("=Your profile changed") and str(s.track) == "ztwo", "ACT a changed profile key: nothing changes")
    K.check(call(Fn, "track", u, tok, None, "zpay|0").startswith("=Your profile changed"), "ACT no profile key")
    K.check(call(Fn, "track", u, "q0", pk, "zpay|0").startswith("=The quest list changed") and str(s.track) == "ztwo", "ACT a stale token: nothing changes")
    Defs.load()                                    # /questadmin reload: a new LINES array -> a new stamp
    K.check(call(Fn, "track", u, tok, pk, "zpay|0").startswith("=The quest list changed") and str(s.track) == "ztwo", "ACT a /questadmin reload makes the old page stale")
    tok = parse(call(Fn, "state", u))["h"][0]
    Act.LASTOP.clear()
    K.check(call(Fn, "track", u, tok, pk, "zpay|0").startswith("+Tracking"), "ACT ... the new token works")
    p.loaded = False
    K.eq(parse(call(Fn, "state", u))["h"][2], "0", "ACT still loading: state ready 0")
    K.check(call(Fn, "claim", u, tok, pk).startswith("-Your quests are still loading"), "ACT still loading: refused (the page's words)")
    p.loaded = True
    Eng.PLAYERS.remove(u)
    K.eq(call(Fn, "claim", u, tok, pk), "-You are not online.", "ACT not online")
    K.eq(parse(call(Fn, "state", u))["h"][1:3], ["-", "0"], "ACT not online: state h has no profile key, ready 0")
    Eng.PLAYERS.put(u, p)
    Act.CLOSED = True
    K.check(call(Fn, "claim", u, tok, pk).startswith("-Quests are shutting down"), "ACT closing: refused")
    K.check(call(Fn, "state", u).startswith("h|"), "ACT closing: a read still answers")
    Act.CLOSED = False
    K.eq(str(Fn.apply("nope")), "-Unknown quest action.", "ACT a non-array argument")
    K.eq(str(Fn.apply(None)), "-Unknown quest action.", "ACT null")
    K.eq(str(Fn.apply(JArray(JObject)([JString("state")]))), "-Unknown quest action.", "ACT a one-element array")
    K.check(str(Fn.apply(JArray(JObject)([JString("state"), JString(str(u))]))).startswith("h|" + tok), "ACT the player as a UUID string")
    K.eq(str(Fn.apply(JArray(JObject)([JString("state"), JString("not-a-uuid")]))), "-Something went wrong - try again.", "ACT a bad UUID string never throws")
    K.check(X.E.bridge.get("quest:fn:act") is None, "ACT the stage itself puts no key (setup does - S45)")
    K.save()


# ---------------------------------------------------------------------------------------------------- LIVE45
def run_live45(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    if home is None or not os.path.isdir(home):
        K.check(False, "LV45 no live copy")
        K.save()
        return
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(mods)
    X = T040.QStage(K, scratch, "lv45", base=home)
    h1 = HK.tree_hash(mods)
    K.check(_LIVE_HAS or True, "LV45 live has archipelago.properties: %s" % _LIVE_HAS)
    new1 = sorted(k for k in set(h0) | set(h1) if h0.get(k) != h1.get(k))
    K.check(not new1 or (not _LIVE_HAS and new1 == [os.path.join("Skyy_SkyyQuests", "quests", "archipelago.properties")]), "LV45 start 1 writes nothing: %s" % new1)
    X.Env.start()
    K.eq(HK.tree_hash(mods), h1, "LV45 start 2 writes nothing")
    Fn = X.P("QActFn")()
    U = JClass("java.util.UUID")
    n = 0
    for f in sorted(os.listdir(os.path.join(home, "players"))):
        pk = f[:-len(".properties")]
        try:
            u = U.fromString(pk)
        except Exception:
            continue
        p = X.P("QP")(u, None)
        p.pk = pk
        p.world = "skyy-island-a1"
        p.loaded = True
        X.Eng.PLAYERS.put(u, p)
        s = X.Sto.read(pk, u)
        s.owner = u
        X.Sto.CACHE.put(pk, s)
        X.Eng.rebuild(u, s)
        st = parse(call(Fn, "state", u))
        K.check(st["h"][1] == pk and st["h"][2] == "1" and int(st["h"][7]) == len(st["l"]) >= 1 and st["t"], "LV45 %s: quest:fn:act state answers (%s lines, %d tasks)" % (f, st["h"][7], len(st["t"])))
        n += 1
    K.check(n >= 1, "LV45 %d live profile(s) read" % n)
    K.eq(HK.tree_hash(mods), h1, "LV45 reading every profile wrote nothing")
    K.save()


if __name__ == "__main__":
    if "--mkfake" in sys.argv:
        T03.mkfake(HK.arg("--mkfake"), JAR)
        sys.exit(0)
    if "--phase" not in sys.argv:
        shutil.rmtree(FAKE_DIR, ignore_errors=True)
        os.makedirs(FAKE_DIR, exist_ok=True)
        env = dict(os.environ)
        env["TEMP"] = env["TMP"] = os.path.join(FAKE_DIR, "tmp")
        env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
        os.makedirs(env["TEMP"], exist_ok=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mkfake", FAKE_DIR, "--jar", JAR, "--dir", SCRATCH], env=env)
        if r.returncode != 0:
            sys.exit("the stand-in classes were not compiled")
    lg = T044.T033.legacy
    T034, T033, T042, T041 = T044.T034, T044.T033, T044.T042, T044.T041
    phases = [("static45", run_static45), ("twin45", run_twin45), ("act45", run_act45), ("live45", run_live45),
              ("archi44", T044.run_archi44), ("have44", T044.run_have44), ("fs44", T044.run_fs44), ("live44", T044.run_live44),
              ("wid43", T043.run_wid43), ("acc42", T042.run_acc42), ("gear41", T041.run_gear41), ("page40", T040.run_page40),
              ("claim40", T040.run_claim40), ("mig34", T034.run_mig34), ("fish34", T034.run_fish34),
              ("merge", T033.run_merge), ("chain", T033.run_chain), ("migt", T033.run_migt),
              ("isl", lg(T040.T032.run_isl)), ("snd", lg(T040.T031.run_snd)), ("defs", lg(T03.run_defs)), ("engine", lg(T03.run_engine)),
              ("life", lg(T03.run_life)), ("pay", lg(T03.run_pay)), ("crash", lg(T03.run_crash)), ("static", lg(T03.run_static)),
              ("npc", lg(T03.run_npc)), ("board", lg(T03.run_board)), ("fish", lg(T03.run_fish)), ("live40", T040.run_live40),
              ("live41", T041.run_live41)]
    if not os.path.isfile(T034.FISH17):
        print("NOTE: %s is not built here - phases fish34 + fish skipped (nothing in 0.4.5 touches fishing)" % T034.FISH17)
        phases = [ph for ph in phases if ph[0] not in ("fish34", "fish")]
    only = HK.arg("--only")
    if only:
        phases = [ph for ph in phases if ph[0] in only.split(",")]
    try:
        HK.run("SkyyQuests", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, phases, os.path.abspath(__file__), live=(T040.LIVE_Q, "Skyy_SkyyQuests"))
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(FAKE_DIR, ignore_errors=True)
    sys.exit(1 if HK.FAILS else 0)
