"""SkyyParty 0.1.6 - bare-JVM harness for the look-only restyle (vanilla UI pass B1, review fixes 2026-09-29).

    python SkyyParty/test_skyyparty_0.1.6.py [--jar <SkyyParty-0.1.6.jar>] [--old <SkyyParty-0.1.5.jar>] [--dir <scratch folder>] [--keep]

Build the jar first (python SkyyParty/build_skyyparty_0.1.6.py). Child processes start fresh JVMs (the game's own JRE, -Xverify:all,
-XX:-UsePerfData, HytaleServer.jar + ONE mod jar on the classpath; javassist only for the bytecode step) and check:
  A  every class of the 0.1.6 jar AND of the 0.1.5 jar loads and initializes under -Xverify:all
  B  13 page states are built by the REAL PartyPage.build of both jars with the real UICommandBuilder / UIEventBuilder (fake online
     players: an Unsafe-allocated Universe + PlayerRefs; no world, no client): alone, invites OFF, a click result, invite pending,
     invite ran out, leader / member of 2, leader of 5 with missing / zero / over-max / negative stats and islands, 16-letter names,
     leader of 7, member of 10, leader with a click message, a pending invite while in a party
  C  per state: identical event bindings (type, selector, EventData, lock flag, order); no 0.1.5 element id missing; identical b.set
     texts (the one disclosed difference: 0.1.5's compact rows for more than 5 members - "* " before the leader's name, "Offline" in
     the where line - are now the normal rows with a role line and an Online / Offline line); identical inline texts (heads, buttons)
  D  per state, the 0.1.6 markup as the client gets it: SUI.check_markup on every append (the first = the page root) + SUI.check_page
     (parents exist, no duplicate id, every b.set target exists); only kit colours or the 3 declared bar data colours; no Width 0, no
     FlexWeight / WrapMaxLines / LetterSpacing / LayoutMode Right, Center, Full, no ItemGridSlot; the body children fill 768 px
     exactly; every member row leaves >= ROW_SLACK px beyond the 12 px scrollbar reserve; a bar fill exists only when > 0 px
  E  PartyPage.fillPx = the 0.1.5 bar maths (clamp to 0..max, 0 when max <= 0, long product) at 160 px, incl. negatives and MAX_VALUE
  F  class bytes 0.1.5 vs 0.1.6: only PartyPage, SkyyPartyPlugin (ready line) and the config kit's CfgFn / CfgRows (version string)
     differ; method by method (constant-pool indices ignored) only PartyPage.build / fillPx (new) / style + statCol (gone),
     SkyyPartyPlugin.setup and the CfgFn / CfgRows version constant
Not testable without the game (UNVERIFIED in the build report): the look itself on a client (the kit base look), the scrollbar width,
text widths. Nothing is deployed. Default scratch folder: tools/dev/scratch/skyyparty-016 (git-ignored), deleted at the end unless --keep;
TEMP/TMP and java.io.tmpdir point into it. Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.6", "0.1.5"
PKG = "com.skyy.party."
ROW_SLACK = 10                       # = build_skyyparty_0.1.6.py ROW_SLACK
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


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyyparty-016")))
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
          "leader of 5 odd stats", "long names", "leader of 7", "member of 10", "leader click message", "invite while in a party"]


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
            if str(k).startswith("party:") or str(k).startswith("settings:"):
                bridge.remove(k)

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


def compare_state(name, old, new, SUI, counts):
    check(old["error"] is None and new["error"] is None, "%s: build() ran in both jars (%s / %s)" % (name, old["error"], new["error"]))
    if old["error"] or new["error"]:
        return
    # C1 bindings
    check(old["events"] == new["events"], "%s: event bindings identical (%d / %d)" % (name, len(old["events"]), len(new["events"])))
    counts["bindings"] += len(new["events"])
    # C2 ids
    oi, ni = ids_of(old), ids_of(new)
    miss = sorted(set(oi) - set(ni))
    check(not miss, "%s: no 0.1.5 id missing: %s" % (name, miss))
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
    check(inline_texts(old) == inline_texts(new), "%s: inline texts identical: %s / %s" % (name, inline_texts(old), inline_texts(new)))
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
    counts = dict(states=0, bindings=0, ids=0, texts=0, disclosed=0, colours=0, check_page=0, appends=0, fills=0, min_slack=10 ** 6)
    for st in STATES:
        check(st in new["states"] and st in old["states"], "B: state %s built by both jars" % st)
        if st in new["states"] and st in old["states"]:
            compare_state(st, old["states"][st], new["states"][st], SUI, counts)
    print("B-D. %(states)d states: %(bindings)d bindings identical, %(ids)d 0.1.5 ids all kept, %(texts)d texts identical "
          "(+ %(disclosed)d disclosed compact-row changes); %(check_page)d check_page / %(appends)d appends through check_markup, "
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
    check(pp.get("changed") == ["build(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;"
                                "Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;Lcom/hypixel/hytale/component/Store;)V"]
          and pp.get("new") == ["fillPx(II)I"] and sorted(m.split("(")[0] for m in pp.get("gone", [])) == ["statCol", "style"],
          "F: PartyPage: only build changed, fillPx new, style / statCol gone: %s" % pp)
    sp = bc.get("com/skyy/party/SkyyPartyPlugin.class", {})
    check(sp.get("changed") == ["setup()V"] and not sp.get("new") and not sp.get("gone") and sp.get("fields_same"),
          "F: SkyyPartyPlugin: only setup() (the ready line) changed: %s" % sp)
    for k in ("com/skyy/party/CfgFn.class", "com/skyy/party/CfgRows.class"):
        c = bc.get(k)
        if c is None:
            continue
        check(not c.get("new") and not c.get("gone") and c.get("fields_same") and c.get("version_only"),
              "F: %s: only the version string differs: %s" % (k, c))
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
