"""Harness for SkyyVault 0.1.11 (round vault1: vault:fn:view / vault:fn:act for the new screen's Vault items view; tools/vault_0_1_11_patch.py).
Build first: python tools/vault_0_1_11_patch.py && python SkyyVault/build_skyyvault_0.1.11.py

    python SkyyVault/test_skyyvault_0.1.11.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  vault1fix  (the fix round after the critics) X: a throw after the stack left the vault / the inventory (a javassist hotbar whose
         reads throw: once, then always) - rescueTake / rescuePut put the counted rest back, items conserved; buy refuses a confirm-size
         price without confirmed 1 (the token stays); the one amount box for take / put (part stacks, bad amounts, filters, a full inventory)
  A      every class loads + initialises with -Xverify:all
  C      class compare 0.1.10 -> 0.1.11 (+ VActFn; exactly the members the patch touches)
  S      static: the patch re-runs to identical bytes; one new class, no command / system; in act the shown-value checks come before the
         token is used and the token before any item moves; every array change sits in a *0 helper under the VData monitor
  X      exec on the 0.1.6 harness's stand-in universe (a real World thread check, real ItemContainers, the REAL VSessions.open2 window):
         view (every line), take / put / move / buy / page / open, each refusal (off thread, unknown op, stale token, the same token
         twice, a wrong / switched profile, a new profile epoch, profile busy, the slot changed since the view, the inventory changed,
         a full inventory, a full / locked page, a page arrow slot, a vault arrow item, a price change), an open vault window (synced,
         then closed before an item op), racing presses (8 threads queue presses with ONE token: exactly one runs), a saver thread
         snapshotting during 300 moves / swaps (every snapshot holds every item exactly once) and ITEM + COIN CONSERVATION after
         every step (vault memory + vault FILE + inventory, per item id; the purse)
  LIVE   START TWICE on a scratch COPY of the live Skyy_SkyyVault: start 1 (fresh class loader) views every live vault (= the file),
         a put + take round trip on each (the file holds the same items after), start 2 (a new loader) views the same; 0.1.10 reads the
         files 0.1.11 wrote (rollback) with the same items
  AA     engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, re, subprocess, importlib.util, threading, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.11"
PKG = "com.skyy.vault."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyVault-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(os.path.join(HERE, "SkyyVault-0.1.10.jar"))
GEN = os.path.join(HERE, "build_skyyvault_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyvault_0.1.10.py")
PATCH = os.path.join(ROOT, "tools", "vault_0_1_11_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "vault1", "harness")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyVault")


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],   # the kit's version texts
    "SkyyVaultPlugin": ["~m setup", "~m shutdown"],     # the two keys + the ready line; removed at shutdown
    "VStore": ["~m toDoc"],                              # the version text in every saved file
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["VActFn"]


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read().replace("\r\n", "\n")
    o = open(GEN_OLD, encoding="utf8", newline="").read().replace("\r\n", "\n")
    K.check(g.startswith('"""SkyyVault 0.1.11 - build script') and g.count('VERSION = "0.1.11"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("pool.makeClass(") - o.count("pool.makeClass("), 1, "S one new class (VActFn)")
    a = g[g.index("public static String act(String op"):]
    a = a[:a.index('"""')]
    i_chk, i_tok, i_free = a.index("String pre = check(op"), a.index("if (!TOK.remove(us, rec)) return OLD;"), a.index("freeSession(p, ref, st, u)")
    K.check(a.index("prOf(u)") < a.index("TOK.get(us)") < a.index("VSessions.gate(u)") < a.index("return PROF;") < i_chk < i_tok < i_free,
            "S act order: world thread, token, gate, profile, shown-value checks, token used, then the window closed and the op")
    for nm in ("out", "in", "keep", "slotFree", "mv"):
        w = g[g.index("public static %s %s(" % ("String" if nm == "keep" else "int" if nm == "slotFree" else "boolean", nm)):]
        w = w[:w.index('"""')]
        K.check("synchronized (d) { return %s0(" % nm in w, "S %s: one call under the VData monitor" % nm)
    tk = g[g.index("public static String take(java.util.UUID u"):]
    K.check(tk.index("long before = invCount(") < tk.index("if (!out(d, pg, sl, x))") < tk.index("c.addItemStack(rem)") < tk.index("moved = invCount(st, ref, id) - before;") < tk.index("where = keep(d, pg, sl, back"),
            "S take: counted, out of the vault, into the inventory, counted, the counted rest kept")
    pt = g[g.index("public static String put(java.util.UUID u"):]
    K.check(pt.index("long before = invCount(") < pt.index("c.removeItemStackFromSlot((short) sl, true)") < pt.index("gone = before - invCount(") < pt.index("if (in(d, tp, ts, it))"),
            "S put: counted, out of the inventory (its filters kept), counted, into the vault")
    K.check(tk.index("if (!out(d, pg, sl, x))") < tk.index("try {") < tk.index("c.addItemStack(rem)") < tk.index("return rescueTake(") < tk.index('"""'),
            "S vault1fix: everything after the stack left the vault sits in a try whose catch runs rescueTake")
    K.check(pt.index("c.removeItemStackFromSlot((short) sl, true)") < pt.index("gone = before - invCount(") < pt.index("return rescuePut(") < pt.index('"""'),
            "S vault1fix: everything after the inventory remove sits in a try whose catch runs rescuePut")
    bz = g[g.index('if (op.equals("buy")) {'):]
    K.check(bz.index("if (now != pr)") < bz.index("needsConfirm(now) && !ok") < bz.index("return null;"), "S vault1fix: buy refuses a confirm-size price without confirmed 1 (in check: the token stays)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    old_keys = ("vault:fn:findLL", "vault:fn:takeLL", "vault:fn:doneLL", "vault:fn:putBack", "storage:fn:find:vault", "vault:fn:openBank")
    K.check(all(g.count(k) >= o.count(k) for k in old_keys) and "vault:fn:view" not in o, "S every old bridge key still put")
    K.save()


def loader(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)([JClass("java.io.File")(jar).toURI().toURL()])
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def universe(jar):
    """the JVM + the 0.1.6 harness's stand-in universe (World thread = this thread, two players with real storage / hotbar
    containers, a PageManager that takes setPageWithWindows / openCustomPageWithWindows)"""
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    T6 = tmod("test_skyyvault_0.1.6.py", "tv016_for11")
    L = {"new": loader(jar), "old": loader(OLD_JAR)}
    E = T6.common(JClass, L)
    E["L"] = L
    return E


def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JShort, JArray
    K = HK.Child(out)
    OA = lambda xs: JArray(JClass("java.lang.Object"))(xs)
    E = universe(jar)
    jc, BR, ISC, Paths, Long = E["jc"], E["BR"], E["ISC"], E["Paths"], E["Long"]
    UID, P1 = E["UID"], E["P1"]
    US = str(UID)
    Cfg, Store, VS, Dat, LL, Act = jc("new", "VCfg"), jc("new", "VStore"), jc("new", "VSessions"), jc("new", "VData"), jc("new", "VLL"), jc("new", "VActFn")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyVault")
    Boolean = JClass("java.lang.Boolean")
    ACTIVE = [US]

    REENTER = []      # (op, tok, arg) = a second press with the same token arriving while the first is between its look-up and its use

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, u):
            if REENTER:
                p_ = REENTER.pop()
                REENTER.append(("done", act(*p_)))
            return ACTIVE[0] if str(u) == US else str(u)
    PURSE = {"p": 0}

    @JImplements("java.util.function.Function")
    class Take:
        @JOverride
        def apply(self, a):
            n = int(a[1])
            if PURSE["p"] < n:
                return Boolean.FALSE
            PURSE["p"] -= n
            return Boolean.TRUE

    @JImplements("java.util.function.Function")
    class Add:
        @JOverride
        def apply(self, a):
            PURSE["p"] += int(a[1])
            return Long.valueOf(PURSE["p"])
    KEYFN, TAKE, ADD = KeyFn(), Take(), Add()
    home = [None]

    def setup(name, inside=False):
        d = os.path.join(scratch, "x", name)
        os.makedirs(os.path.join(d, "vaults"), exist_ok=True)
        home[0] = d
        Cfg.DIR = Paths.get(d)
        Cfg.VDIR = Paths.get(d).resolve("vaults")
        Cfg.FILE = Paths.get(d).resolve("config.properties")
        Cfg.LOGF = Paths.get(d).resolve("vault.log")
        Cfg.NAMESF = Paths.get(d).resolve("names.properties")
        Cfg.FREE_PAGES, Cfg.MAX_PAGES, Cfg.SLOTS = 1, 10, 36
        Cfg.ARROWS, Cfg.ARROW_LAYOUT = True, ("inside" if inside else "row")
        Cfg.PAGE_MODE, Cfg.OPEN_MODE = False, "chest"
        Cfg.AFTER_SWITCH_MS, Cfg.SAVE_DELAY_MS = 30000, 1000
        Cfg.BUY_CONFIRM = 50000
        for m in ("CACHE", "PENDING", "BUYING", "LASTBUY", "NAMES"):
            getattr(Store, m).clear()
        Store.SAVER, Store.STOPPING = None, False
        for m in ("SESSIONS", "LAST", "EPOCHS", "SWITCHED", "BUSYSEEN", "ONLINE"):
            getattr(VS, m).clear()
        for m in ("PEND", "QUEUED", "SEEN", "HELD"):
            getattr(LL, m).clear()
        Act.TOK.clear()
        Cfg.WARNED.clear()
        E["Q"].clear()
        BR.clear()
        BR.put("profile:fn:key", KEYFN)
        BR.put("coins:fn:take", TAKE)
        BR.put("coins:fn:add", ADD)
        BR.put("vault:fn:view", Act(1))
        BR.put("vault:fn:act", Act(2))
        ACTIVE[0] = US
        E["CURRUN"].set(E["RUN"])
        for c in (P1["storage"], P1["hot"]):
            c.clear()
        vd = Dat(UID, 36)
        vd.unlocked = 3
        vd.page(3)
        for i, (iid, q) in enumerate((("Ore_Iron", 20), ("Wood_Oak_Log", 64), ("Ore_Iron", 5), ("Gem_Ruby", 1))):
            vd.page(1)[i] = ISC(iid, q)
        vd.page(1)[10] = ISC("Tool_Pickaxe_Iron", 1, JClass("org.bson.BsonDocument").parse('{"SkyyGear": {"v": 1}}'))
        vd.page(2)[0] = ISC("Ore_Gold", 7)
        vd.rev = 1
        Store.CACHE.put(UID, vd)
        K.check(bool(LL.persist(vd)), "X %s: the starting vault file is written" % name)
        P1["storage"].setItemStackForSlot(JShort(0), ISC("Plant_Wheat", 12), False)
        P1["storage"].setItemStackForSlot(JShort(1), ISC("Ore_Iron", 3), False)
        P1["hot"].setItemStackForSlot(JShort(0), ISC("Tool_Sword_Iron", 1), False)
        return d, vd

    def view(page=0):
        r = BR.get("vault:fn:view").apply(OA([UID, str(page)]) if page else UID)
        return None if r is None else str(r)

    def parse(v):
        o = collections.OrderedDict()
        for ln in v.split("\n"):
            f = ln.split("|")
            o.setdefault(f[0], []).append(f[1:])
        return o

    def act(op, tok, arg, pk=None):
        r = BR.get("vault:fn:act").apply(OA([op, UID, tok, pk if pk is not None else ACTIVE[0], arg]))
        return None if r is None else str(r)

    def tok_of():
        v = view()
        return parse(v)["h"][0][1]

    def counts_mem(vd):
        c = collections.Counter()
        for pg in range(1, int(vd.pages.size()) + 1):
            for x in vd.pageCopy(pg):
                if x is not None and not x.isEmpty():
                    c[str(x.getItemId())] += int(x.getQuantity())
        for i in range(int(vd.orphans.size())):
            dd = vd.orphans.get(i).asDocument()
            c[str(dd.getString("id").getValue())] += int(dd.getInt32("qty").getValue())
        return c

    def counts_file():
        p = os.path.join(home[0], "vaults", US + ".json")
        c = collections.Counter()
        if not os.path.exists(p):
            return c
        doc = json.loads(open(p, encoding="utf8").read())
        num = lambda v: int(next(iter(v.values()))) if isinstance(v, dict) else int(v)
        for pgd in doc.get("content", []):
            for sd in pgd.get("slots", []):
                c[sd["id"]] += num(sd["qty"])
        for sd in doc.get("orphans", []):
            c[sd["id"]] += num(sd["qty"])
        return c

    def counts_inv():
        c = collections.Counter()
        for cc in (P1["storage"], P1["hot"]):
            for i in range(int(cc.getCapacity())):
                x = cc.getItemStack(JShort(i))
                if x is not None and not x.isEmpty():
                    c[str(x.getItemId())] += int(x.getQuantity())
        return c

    def total(vd, file=False):
        return (counts_file() if file else counts_mem(vd)) + counts_inv()

    def conserved(vd, base, what, file=True):
        m = total(vd)
        ok = K.check(m == base, "X %s: items conserved in memory + inventory (%s vs %s)" % (what, dict(m - base), dict(base - m)))
        if file:
            f = total(vd, file=True)
            ok = K.check(f == base, "X %s: items conserved in the vault FILE + inventory (%s vs %s)" % (what, dict(f - base), dict(base - f))) and ok
        return ok

    # ---------------- view
    d, vd = setup("view")
    base = total(vd)
    v = view()
    pv = parse(v)
    h = pv["h"][0]
    K.check(len(h) == 13 and h[0] == "ok" and h[2] == US and h[3] == "1" and h[4] == "3" and h[5] == "10" and h[6] == "36" and h[7] == "36"
            and h[8] == "6" and h[9] == "1" and h[12] == "0", "X view h line: %s" % h)
    K.eq(sorted((s[0], s[1], s[2]) for s in pv["s"]), sorted([("1", "Ore_Iron", "20"), ("2", "Wood_Oak_Log", "64"), ("3", "Ore_Iron", "5"),
                                                             ("4", "Gem_Ruby", "1"), ("11", "Tool_Pickaxe_Iron", "1")]), "X view s lines = page 1")
    K.check([s for s in pv["s"] if s[1] == "Tool_Pickaxe_Iron"][0][6] == "1" and [s for s in pv["s"] if s[1] == "Gem_Ruby"][0][6] == "0", "X view s: the metadata flag")
    K.eq(sorted((i[0], i[1], i[2], i[3]) for i in pv["i"]), sorted([("1", "1", "Plant_Wheat", "12"), ("1", "2", "Ore_Iron", "3"), ("0", "1", "Tool_Sword_Iron", "1")]), "X view i lines = the inventory")
    K.eq(sorted(tuple(c) for c in pv["c"]), [("0", "9"), ("1", "36")], "X view c lines (no backpack component)")
    K.eq([p[:2] for p in pv["p"]], [[str(n), "own" if n <= 3 else "next" if n == 4 else "locked"] for n in range(1, 11)], "X view p lines")
    K.check(pv["b"][0][:5] == ["buy", "4", "100000", "1", "0"] and pv["b"][0][6].startswith("Buy page 4 - 100k"), "X view b line: %s" % pv["b"][0])
    K.check(pv["t"][0][0].startswith("Page 1 of 3 - 5 of 36 slots used"), "X view t line: %s" % pv["t"])
    K.check("r" not in pv, "X no arrow slots in the row layout")
    pv2 = parse(view(2))
    K.check(pv2["h"][0][3] == "2" and [s[:3] for s in pv2["s"]] == [["1", "Ore_Gold", "7"]], "X view of page 2")
    pv5 = parse(view(5))
    K.check(pv5["h"][0][3] == "5" and "s" not in pv5 and "locked" in pv5["t"][0][0] and "Buy page 4 first" in pv5["t"][0][0], "X view of a locked page: no slots, the locked line (%s)" % pv5["t"])
    K.check(view(99) is not None and parse(view(99))["h"][0][3] == "1", "X a page beyond the last = the page the vault opens on")
    # off thread: nothing read, nothing done
    E["CURRUN"].set(None)
    t = Act.TOK.get(US)
    K.check(view() is None and act("take", "x", "1:1:20:Ore_Iron") is None and Act.TOK.get(US) == t, "X off the world thread: null, the token untouched")
    E["CURRUN"].set(E["RUN"])
    K.check(BR.get("vault:fn:view").apply("not a uuid") is None and BR.get("vault:fn:act").apply("junk") is None
            and BR.get("vault:fn:act").apply(OA([None, UID])) is None, "X bad arguments: null, never a throw")
    K.check(act("explode", "x", "") == "-Unknown vault action - nothing moved.", "X an unknown op")
    K.check(act("refresh", None, None) == "", "X refresh: nothing to say, no token")
    conserved(vd, base, "after the views")

    # ---------------- take
    tok = tok_of()
    r = act("take", tok, "1:1:20:Ore_Iron")
    K.check(r == "+Took 20 Ore_Iron from vault page 1 slot 1.", "X take a whole stack: %s" % r)
    K.check(vd.pageCopy(1)[0] is None and counts_inv()["Ore_Iron"] == 23, "X take: the slot is empty, the inventory holds it")
    conserved(vd, base, "take")
    K.check(act("take", tok, "1:3:5:Ore_Iron") == str(Act.OLD) and vd.pageCopy(1)[2] is not None, "X the same token again: the older-copy line, nothing moved")
    t1 = tok_of()
    t2 = tok_of()
    K.check(act("take", t1, "1:3:5:Ore_Iron") == str(Act.OLD) and vd.pageCopy(1)[2] is not None, "X a stale token (an older view): nothing moved")
    K.check(act("take", t2, "1:3:5:Ore_Iron", pk=US + "-p2") == str(Act.PROF), "X a profileKey that is not the view's: profile line")
    ACTIVE[0] = US + "-p2"
    K.check(act("take", t2, "1:3:5:Ore_Iron", pk=US) == str(Act.PROF), "X the active profile switched since the view: profile line")
    ACTIVE[0] = US
    BR.put("profile:epoch:" + US, "e2")
    K.check(act("take", t2, "1:3:5:Ore_Iron") == str(Act.PROF) and vd.pageCopy(1)[2] is not None, "X a new profile epoch since the view: nothing moved")
    t3 = tok_of()
    BR.put("profile:busy:" + US, Boolean.TRUE)
    r = act("take", t3, "1:3:5:Ore_Iron")
    K.check(r is not None and r.startswith("-Your profile is still loading") and vd.pageCopy(1)[2] is not None, "X profile busy: the vault is shut (%s)" % r)
    K.check(view().startswith("off|Your profile is still loading") and Act.TOK.get(US) is None, "X view while busy: off, no token")
    BR.remove("profile:busy:" + US)
    VS.SWITCHED.clear()
    VS.BUSYSEEN.clear()
    t4 = tok_of()
    K.check(act("take", t4, "1:3:4:Ore_Iron") == str(Act.CHG) and act("take", t4, "1:4:1:Ore_Iron") == str(Act.CHG), "X a quantity / item the slot does not hold: changed line")
    vd.page(1)[2] = ISC("Ore_Iron", 6)
    vd.rev = vd.rev + 1
    base = total(vd)   # the test itself changed the vault (a stand-in for a drag elsewhere)
    K.check(act("take", t4, "1:3:5:Ore_Iron") == str(Act.CHG), "X the slot changed since the view: nothing moved")
    K.check(act("take", t4, "1:3:6:Ore_Iron").startswith("+Took 6"), "X ... the token stayed alive: the press with what the slot holds now runs")
    K.check(act("take", tok_of(), "7:1:1:Ore_Iron").startswith("-Vault page 7 is not yours") and act("take", tok_of(), "1:99:1:x") == str(Act.BAD)
            and act("take", tok_of(), "nonsense") == str(Act.BAD), "X a locked page / a bad slot / a bad arg")
    conserved(vd, base, "take refusals")
    # a full inventory: nothing moves, the very same stack stays
    for c, n in ((P1["storage"], 36), (P1["hot"], 9)):
        for i in range(n):
            if c.getItemStack(JShort(i)) is None:
                c.setItemStackForSlot(JShort(i), ISC("Fill_%d_%d" % (n, i), 1), False)
    base = total(vd)
    x0 = vd.pageCopy(1)[1]
    r = act("take", tok_of(), "1:2:64:Wood_Oak_Log")
    K.check(r == "-Your inventory is full - nothing moved." and vd.pageCopy(1)[1] == x0, "X a full inventory: nothing moved, the same stack in its slot (%s)" % r)
    conserved(vd, base, "full inventory", file=False)
    # a partial fit: the only slot with room holds Wood_Oak_Log 10 short of its max stack (the stand-in's Item.UNKNOWN): 10 move, 54 stay
    mx = int(ISC("Wood_Oak_Log", 1).getItem().getMaxStack())
    P1["storage"].setItemStackForSlot(JShort(35), ISC("Wood_Oak_Log", mx - 10), False)
    base = total(vd)
    r = act("take", tok_of(), "1:2:64:Wood_Oak_Log")
    left = vd.pageCopy(1)[1]
    K.check(r == "+Took 10 Wood_Oak_Log from vault page 1 - your inventory is full, 54 stayed in the vault." and left is not None
            and int(left.getQuantity()) == 54 and str(left.getItemId()) == "Wood_Oak_Log" and int(P1["storage"].getItemStack(JShort(35)).getQuantity()) == mx,
            "X a partial fit (max stack %d): 10 taken, the counted 54 stayed in its slot (%s)" % (mx, r))
    conserved(vd, base, "partial take")
    # keep(): its slot, else the first free slot of any owned page, else an orphan in the file (never dropped)
    base = total(vd)
    st0 = ISC("Keep_Probe", 2)
    vd.page(1)[0] = ISC("Blocker", 1)
    want_at = "1:%d" % ([i for i in range(36) if vd.pageCopy(1)[i] is None][0] + 1)
    K.eq(str(Act.keep(vd, 1, 0, st0, -1, -1)), want_at, "X keep: a taken slot -> the first free slot")
    base = base + collections.Counter({"Blocker": 1, "Keep_Probe": 2})
    for pg in (1, 2, 3):
        for i in range(36):
            if vd.pageCopy(pg)[i] is None:
                vd.page(pg)[i] = ISC("Pad", 1)
                base = base + collections.Counter({"Pad": 1})
    K.eq(str(Act.keep(vd, 1, 0, ISC("Keep_Probe", 3), -1, -1)), "file", "X keep: a full vault -> an orphan in the file")
    base = base + collections.Counter({"Keep_Probe": 3})
    Act.saveNow(UID, vd)
    K.check(any(str(vd.orphans.get(i).asDocument().getString("id").getValue()) == "Keep_Probe" for i in range(int(vd.orphans.size()))), "X keep: the orphan is in the vault")
    conserved(vd, base, "keep fallbacks")
    # an unreadable vault file: view off, act refused
    Store.CACHE.clear()
    open(os.path.join(home[0], "vaults", US + ".json"), "w").write("{ not json")
    v = view()
    K.check(v.startswith("off|Your vault file cannot be read") and Act.TOK.get(US) is None, "X an unreadable vault file: view off, no token (%s)" % v[:60])
    K.check(act("take", "x", "1:1:1:Pad") == str(Act.OLD), "X ... and every act is refused")

    # ---------------- put
    d, vd = setup("put")
    base = total(vd)
    r = act("put", tok_of(), "1:1:12:0:Plant_Wheat")
    K.check(r == "+Put 12 Plant_Wheat into vault page 1 slot 5." and P1["storage"].getItemStack(JShort(0)) is None, "X put into the first free slot of the shown page: %s" % r)
    conserved(vd, base, "put")
    r = act("put", tok_of(), "0:1:1:2:Tool_Sword_Iron")
    K.check(r == "+Put 1 Tool_Sword_Iron into vault page 2 slot 2.", "X put from the hotbar onto page 2: %s" % r)
    conserved(vd, base, "put page 2")
    K.check(act("put", tok_of(), "1:2:2:0:Ore_Iron") == str(Act.INVC) and act("put", tok_of(), "1:30:1:0:Air") == str(Act.INVC), "X the inventory slot does not hold that: nothing moved")
    K.check(act("put", tok_of(), "1:2:3:5:Ore_Iron").startswith("-Vault page 5 is not yours"), "X put onto a locked page")
    P1["storage"].setItemStackForSlot(JShort(5), ISC("Skyy_Vault_Next", 1), False)
    K.check(act("put", tok_of(), "1:6:1:0:Skyy_Vault_Next").startswith("-That is a vault page arrow"), "X a vault arrow item never goes in")
    P1["storage"].removeItemStackFromSlot(JShort(5), False)
    K.check(act("put", tok_of(), "3:1:3:0:Ore_Iron") == str(Act.BAD) and act("put", tok_of(), "1:2:3:x") == str(Act.BAD), "X a bad section / arg")
    # an inventory slot whose own filter refuses REMOVE (a locked slot): the item stays, nothing moved

    @JImplements("com.hypixel.hytale.server.core.inventory.container.filter.SlotFilter")
    class NoRemove:
        @JOverride
        def test(self, a, c, slot, st):
            return False
    FAT = JClass("com.hypixel.hytale.server.core.inventory.container.filter.FilterActionType")
    P1["storage"].setSlotFilter(FAT.REMOVE, JShort(1), NoRemove())
    r = act("put", tok_of(), "1:2:3:0:Ore_Iron")
    K.check(r == "-That item cannot leave your inventory slot - nothing moved." and counts_inv()["Ore_Iron"] == 3, "X a slot filter that refuses the remove is kept (%s)" % r)
    P1["storage"].setSlotFilter(FAT.REMOVE, JShort(1), None)
    conserved(vd, base, "filtered slot")
    for i in range(36):
        if vd.pageCopy(3)[i] is None:
            vd.page(3)[i] = ISC("Stone_%d" % i, 1)
    vd.rev = vd.rev + 1
    base = total(vd)
    r = act("put", tok_of(), "1:2:3:3:Ore_Iron")
    K.check(r == "-Vault page 3 is full - nothing moved. Pick another page." and counts_inv()["Ore_Iron"] == 3, "X put onto a full page: nothing moved")
    conserved(vd, base, "full page", file=False)

    # ---------------- move (+ swap), the arrow slots of arrowLayout=inside
    d, vd = setup("move", inside=True)
    base = total(vd)
    pv = parse(view())
    K.eq(pv.get("r"), [["28"], ["36"]], "X inside layout: the arrow slots on r lines")
    r = act("move", tok_of(), "1:1:20:2:5:0:Ore_Iron:-")
    K.check(r == "+Moved 20 Ore_Iron to vault page 2 slot 5." and vd.pageCopy(1)[0] is None and str(vd.pageCopy(2)[4].getItemId()) == "Ore_Iron", "X move to an empty slot: %s" % r)
    r = act("move", tok_of(), "1:2:64:2:1:7:Wood_Oak_Log:Ore_Gold")
    K.check(r.startswith("+Swapped Wood_Oak_Log and Ore_Gold") and str(vd.pageCopy(1)[1].getItemId()) == "Ore_Gold" and str(vd.pageCopy(2)[0].getItemId()) == "Wood_Oak_Log", "X move onto a full slot swaps: %s" % r)
    conserved(vd, base, "move + swap")
    K.check(act("move", tok_of(), "1:3:5:1:28:0:Ore_Iron:-").startswith("-That slot holds the page arrow") and act("move", tok_of(), "1:3:5:1:36:0:Ore_Iron:-").startswith("-That slot holds the page arrow"),
            "X never onto a page arrow slot")
    K.check(act("move", tok_of(), "1:3:5:1:3:0:Ore_Iron:-").startswith("-That is the same slot") and act("move", tok_of(), "1:3:5:2:1:0:Ore_Iron:-") == str(Act.CHG)
            and act("move", tok_of(), "1:3:5:9:1:0:Ore_Iron:-").startswith("-That vault page is not yours"), "X same slot / target changed / locked page")
    r = act("put", tok_of(), "1:1:12:1:Plant_Wheat")
    K.check(r == "+Put 12 Plant_Wheat into vault page 1 slot 1.", "X put skips nothing it should not (slot 1 free again): %s" % r)
    conserved(vd, base, "move refusals")

    # ---------------- a saver thread snapshotting during 300 moves / swaps: every snapshot holds every item exactly once
    d, vd = setup("race")
    want = counts_mem(vd)
    bad, snaps, stop = [], [0], [False]

    def snapper():
        while not stop[0]:
            doc = vd.snap()[0]
            c = collections.Counter()
            cont = doc.getArray("content")
            for i in range(int(cont.size())):
                sl = cont.get(i).asDocument().getArray("slots")
                for k in range(int(sl.size())):
                    sd = sl.get(k).asDocument()
                    c[str(sd.getString("id").getValue())] += int(sd.getInt32("qty").getValue())
            snaps[0] += 1
            if c != want:
                bad.append(dict(c))
    th = threading.Thread(target=snapper)
    th.start()
    import random
    rnd = random.Random(11)
    done = 0
    for n in range(300):
        filled = []
        for pg in (1, 2, 3):
            arr = vd.pageCopy(pg)
            for i in range(36):
                if arr[i] is not None:
                    filled.append((pg, i + 1, str(arr[i].getItemId()), int(arr[i].getQuantity())))
        fp, fs, iid, q = rnd.choice(filled)
        tp, ts = rnd.randint(1, 3), rnd.randint(1, 36)
        cur = vd.pageCopy(tp)[ts - 1]
        arg = "%d:%d:%s:%d:%d:%s:%s:%s" % (fp, fs, q, tp, ts, int(cur.getQuantity()) if cur else 0, iid, str(cur.getItemId()) if cur else "-")
        r = act("move", tok_of(), arg)
        if r and r.startswith("+"):
            done += 1
    stop[0] = True
    th.join()
    K.check(not bad and snaps[0] > 20 and done > 200, "X 300 moves / swaps (%d done) under %d saver snapshots: every snapshot holds every item once (bad %s)" % (done, snaps[0], bad[:2]))
    K.check(counts_mem(vd) == want and counts_file() == want, "X after the race: memory and file hold every item once")

    # ---------------- racing presses: 8 threads queue a press with ONE token; the world thread runs them: exactly one moves
    d, vd = setup("presses")
    base = total(vd)
    tok = tok_of()
    q = []
    lock = threading.Lock()

    def presser():
        with lock:
            q.append(("take", tok, "1:4:1:Gem_Ruby"))
    ths = [threading.Thread(target=presser) for _ in range(8)]
    for t_ in ths:
        t_.start()
    for t_ in ths:
        t_.join()
    res = [act(*p) for p in q]
    K.check(sum(1 for r in res if r.startswith("+Took 1 Gem_Ruby")) == 1 and sum(1 for r in res if r == str(Act.OLD)) == 7, "X 8 racing presses, one token: one take, 7 older-copy lines (%s)" % collections.Counter(res))
    conserved(vd, base, "racing presses")
    # a press that arrives while another press with the same token is between its token look-up and its token use (the profile
    # look-up of the first press runs the second): exactly one of the two runs
    tok = tok_of()
    REENTER.append(("page", tok, "2"))
    r_out = act("page", tok, "2")
    r_in = REENTER.pop()[1] if REENTER and REENTER[-1][0] == "done" else None
    REENTER[:] = []
    K.check(sorted([r_out, r_in]) == sorted(["+Showing vault page 2 of 3.", str(Act.OLD)]), "X two overlapping presses, one token: exactly one runs (%s / %s)" % (r_out, r_in))
    tok = tok_of()
    REENTER.append(("take", tok, "1:2:64:Wood_Oak_Log"))
    r_out = act("take", tok, "1:2:64:Wood_Oak_Log")
    r_in = REENTER.pop()[1] if REENTER and REENTER[-1][0] == "done" else None
    REENTER[:] = []
    K.check(sum(1 for r in (r_out, r_in) if r and r.startswith("+Took")) == 1, "X two overlapping takes, one token: one take (%s / %s)" % (r_out, r_in))
    conserved(vd, base, "overlapping presses")
    # the token use itself from 8 Java-visible threads at once (ConcurrentHashMap.remove(key, record))
    tok_of()
    rec = Act.TOK.get(US)
    wins = []
    bar = threading.Barrier(8)

    def racer():
        bar.wait()
        wins.append(bool(Act.TOK.remove(US, rec)))
    ths = [threading.Thread(target=racer) for _ in range(8)]
    for t_ in ths:
        t_.start()
    for t_ in ths:
        t_.join()
    K.eq(sum(wins), 1, "X the atomic token use from 8 threads: exactly one winner")

    # ---------------- an open vault window: synced first, closed before an item op
    d, vd = setup("window")
    base = total(vd)
    r = VS.open2(P1["pr"], P1["ref"], E["STORE"], 1, 2, None)
    s = VS.current(UID)
    K.check(s is not None and int(s.page) == 1, "X the vault chest window is open on page 1 (%s)" % r)
    K.check(parse(view())["h"][0][12] == "1", "X view says the window is open")
    s.view.setItemStackForSlot(JShort(20), ISC("Ore_Copper", 9), False)   # a drag into the open window (the change listener syncs)
    P1["storage"].removeItemStackFromSlot(JShort(0), False)               # ... from the inventory (the engine's half of the drag)
    base = base - collections.Counter({"Plant_Wheat": 12}) + collections.Counter({"Ore_Copper": 9})
    pv = parse(view())
    K.check(any(s_[1] == "Ore_Copper" and s_[0] == "21" for s_ in pv["s"]), "X view shows what the open window holds (synced)")
    r = act("take", pv["h"][0][1], "1:21:9:Ore_Copper")
    K.check(r == "+Took 9 Ore_Copper from vault page 1 slot 21." and VS.current(UID) is None, "X take with the window open: the window closed first, then the take (%s)" % r)
    conserved(vd, base, "window")

    # ---------------- page / open / buy (+ coins)
    d, vd = setup("buy")
    base = total(vd)
    K.check(act("page", tok_of(), "2") == "+Showing vault page 2 of 3." and int(VS.lastPage(UID)) == 2 and parse(view())["h"][0][3] == "2", "X page 2: the page the vault opens on")
    r = act("page", tok_of(), "4")
    K.check(r.startswith("-Page 4 is locked - it costs 100,000 coins") and int(VS.lastPage(UID)) == 2, "X page 4 (locked): the locked line (%s)" % r)
    K.check(act("page", tok_of(), "0") == str(Act.BAD), "X page 0: bad request")
    PURSE["p"] = 250000
    r = act("buy", tok_of(), "4:90000")
    K.check(r.startswith("=The price of vault page 4 changed to 100,000") and PURSE["p"] == 250000 and int(vd.unlocked) == 3, "X buy at a price the view did not show: nothing charged (%s)" % r)
    K.check(act("buy", tok_of(), "5:125000:1") == str(Act.CHG) and act("buy", tok_of(), "3:0").startswith("=Vault page 3 is already yours"), "X buy of a page that is not the next one")
    tk = tok_of()
    r = act("buy", tk, "4:100000:1")
    K.check(r.startswith("+Bought vault page 4 for 100,000 coins") and PURSE["p"] == 150000 and int(vd.unlocked) == 4, "X buy page 4: %s" % r)
    K.check(act("buy", tk, "4:100000:1") == str(Act.OLD) and PURSE["p"] == 150000, "X the same buy press again: nothing charged")
    r = act("buy", tok_of(), "5:125000:1")
    K.check(r.startswith("-You just bought vault page 4") and PURSE["p"] == 150000 and int(vd.unlocked) == 4, "X the page's double-click guard (%s)" % r)
    Store.LASTBUY.clear()
    r = act("buy", tok_of(), "5:125000:1")
    K.check(r.startswith("+Bought vault page 5") and PURSE["p"] == 25000, "X page 5: %s" % r)
    Store.LASTBUY.clear()
    r = act("buy", tok_of(), "6:150000:1")
    K.check(r.startswith("-Vault page 6 costs 150,000 coins - you do not have enough") and PURSE["p"] == 25000 and int(vd.unlocked) == 5, "X too poor: nothing (%s)" % r)

    @JImplements("java.util.function.Function")
    class Lv:
        @JOverride
        def apply(self, u):
            return JClass("java.lang.Integer").valueOf(1)
    BR.put("bank:fn:level", Lv())
    PURSE["p"] = 10 ** 9
    pv = parse(view())
    K.check(pv["b"][0][:3] == ["bank", "6", "150000"] and pv["b"][0][4] == "2" and pv["b"][0][6] == "Page 6 needs Bank Lv 2", "X view b: the bank-level gate (%s)" % pv["b"])
    r = act("buy", pv["h"][0][1], "6:150000:1")
    K.check(r.startswith("-Vault page 6 needs Bank Lv 2") and PURSE["p"] == 10 ** 9, "X the bank gate: nothing charged (%s)" % r)
    BR.remove("bank:fn:level")
    r = act("open", tok_of(), "2")
    K.check(r is not None and r.startswith("+Vault page 2") and VS.current(UID) is not None and int(VS.current(UID).page) == 2, "X open 2: the chest window of page 2 (%s)" % r)
    r = act("open", tok_of(), "9")
    K.check(r.startswith("-") and int(VS.current(UID).page) == 2, "X open a locked page: refused (%s)" % r)
    conserved(vd, base, "page / open / buy")

    # ---------------- vault1fix 2: the confirm rule is enforced in act (economy.md LOCKED: arrow, Buy button and /vault buy share it)
    d, vd = setup("confirm")
    base = total(vd)
    PURSE["p"] = 10 ** 9
    pv = parse(view())
    tk = pv["h"][0][1]
    K.check(pv["b"][0][3] == "1", "X confirm: b says confirm 1 for page 4 (100,000 >= buyConfirmCoins 50,000)")
    for arg in ("4:100000", "4:100000:0"):
        r = act("buy", tk, arg)
        K.check(r == "-Buy page 4 for 100,000 coins? Confirm it first - nothing was charged." and PURSE["p"] == 10 ** 9 and int(vd.unlocked) == 3,
                "X confirm: buy %s without confirmed 1 is refused, nothing charged (%s)" % (arg, r))
    r = act("buy", tk, "4:100000:1")
    K.check(r.startswith("+Bought vault page 4") and PURSE["p"] == 10 ** 9 - 100000 and int(vd.unlocked) == 4, "X confirm: the refusal kept the token; buy 4:100000:1 runs (%s)" % r)
    Store.LASTBUY.clear()
    Cfg.BUY_CONFIRM = 10 ** 9
    pv = parse(view())
    r = act("buy", pv["h"][0][1], "5:125000")
    K.check(pv["b"][0][3] == "0" and r.startswith("+Bought vault page 5") and int(vd.unlocked) == 5, "X confirm: below buyConfirmCoins no confirm is needed (%s)" % r)
    K.check(act("buy", tok_of(), "6:150000:1:9") == str(Act.BAD), "X confirm: a 4-field buy is a bad request")
    Cfg.BUY_CONFIRM = 50000
    conserved(vd, base, "confirm")

    # ---------------- vault1fix 3: the one amount box (ui.md LOCKED 2026-10-10) for take / put
    d, vd = setup("amount")
    base = total(vd)
    r = act("take", tok_of(), "1:2:64:10:Wood_Oak_Log")
    x2 = vd.pageCopy(1)[1]
    K.check(r == "+Took 10 Wood_Oak_Log from vault page 1 slot 2 - 54 left in the vault." and x2 is not None and int(x2.getQuantity()) == 54
            and counts_inv()["Wood_Oak_Log"] == 10, "X amount: take 10 of 64, 54 stay in the slot (%s)" % r)
    conserved(vd, base, "take amount")
    K.check(act("take", tok_of(), "1:2:54:99:Wood_Oak_Log") == str(Act.BAD) and act("take", tok_of(), "1:2:54:-1:Wood_Oak_Log") == str(Act.BAD)
            and act("take", tok_of(), "1:2:54:5:6:Wood_Oak_Log") == str(Act.BAD), "X amount: above the stack / negative / too many fields = bad request")
    r = act("take", tok_of(), "1:1:20:0:Ore_Iron")
    K.check(r == "+Took 20 Ore_Iron from vault page 1 slot 1." and vd.pageCopy(1)[0] is None, "X amount 0 = the whole stack (%s)" % r)
    r = act("take", tok_of(), "1:3:5:5:Ore_Iron")
    K.check(r == "+Took 5 Ore_Iron from vault page 1 slot 3." and vd.pageCopy(1)[2] is None, "X amount = the stack = the whole stack (%s)" % r)
    conserved(vd, base, "take amount 2")
    r = act("put", tok_of(), "1:1:12:0:5:Plant_Wheat")
    w0 = P1["storage"].getItemStack(JShort(0))
    K.check(r == "+Put 5 Plant_Wheat into vault page 1 slot 1." and w0 is not None and int(w0.getQuantity()) == 7
            and int(vd.pageCopy(1)[0].getQuantity()) == 5, "X amount: put 5 of 12, 7 stay in the inventory slot (%s)" % r)
    conserved(vd, base, "put amount")
    K.check(act("put", tok_of(), "1:1:7:0:8:Plant_Wheat") == str(Act.BAD), "X amount: put more than the slot holds = bad request")
    P1["storage"].setSlotFilter(FAT.REMOVE, JShort(0), NoRemove())
    r = act("put", tok_of(), "1:1:7:0:3:Plant_Wheat")
    K.check(r == "-That item cannot leave your inventory slot - nothing moved." and int(P1["storage"].getItemStack(JShort(0)).getQuantity()) == 7, "X amount: the slot filter still holds (%s)" % r)
    P1["storage"].setSlotFilter(FAT.REMOVE, JShort(0), None)
    conserved(vd, base, "put amount filtered")
    # a part-amount take into a nearly full inventory: only what fits leaves, the counted rest stays
    P1["storage"].setItemStackForSlot(JShort(2), ISC("Wood_Oak_Log", mx), False)
    for c, n in ((P1["storage"], 36), (P1["hot"], 9)):
        for i in range(n):
            if c.getItemStack(JShort(i)) is None:
                c.setItemStackForSlot(JShort(i), ISC("Fill_%d_%d" % (n, i), 1), False)
    P1["storage"].removeItemStackFromSlot(JShort(35), False)
    P1["storage"].setItemStackForSlot(JShort(35), ISC("Wood_Oak_Log", mx - 3), False)
    base = total(vd)
    r = act("take", tok_of(), "1:2:54:20:Wood_Oak_Log")
    K.check(r == "+Took 3 Wood_Oak_Log from vault page 1 - your inventory is full, 51 stayed in the vault." and int(vd.pageCopy(1)[1].getQuantity()) == 51,
            "X amount 20 with room for 3: 3 taken, 51 stay (%s)" % r)
    conserved(vd, base, "take amount, full")

    # ---------------- vault1fix 1: a throw after the stack left the vault / the inventory never loses or dupes it (rescueTake / rescuePut)
    # the hotbar is swapped for a javassist subclass of SimpleItemContainer whose getItemStack throws once it is armed (armed right after
    # its own addItemStack / removeItemStackFromSlot returns): MODE 1 = one throw (the rescue's recount works), MODE 2 = every read throws
    # (the rescue falls back to the engine's remainder / the remove's own transaction)
    CtPool = JClass("javassist.ClassPool")(True)
    CtPool.appendClassPath(B.SERVER_JAR)
    CtNM, CtNC, CtF = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")
    IC_ = "com.hypixel.hytale.server.core.inventory."
    bc = CtPool.makeClass(IC_ + "container.SkyyVault11Boom", CtPool.get(IC_ + "container.SimpleItemContainer"))
    for f_ in ("public static int MODE = 0;", "public static boolean ARMED = false;", "public static int BOOMS = 0;"):
        bc.addField(CtF.make(f_, bc))
    bc.addConstructor(CtNC.make("public SkyyVault11Boom(short n) { super(n); }", bc))
    for m_ in ("public %sItemStack getItemStack(short s) { if (ARMED && MODE > 0) { if (MODE == 1) ARMED = false; BOOMS = BOOMS + 1; "
               "throw new IllegalStateException(\"harness boom\"); } return super.getItemStack(s); }" % IC_,
               "public %stransaction.ItemStackTransaction addItemStack(%sItemStack x) { %stransaction.ItemStackTransaction t = super.addItemStack(x); "
               "if (MODE > 0) ARMED = true; return t; }" % (IC_, IC_, IC_),
               "public %stransaction.SlotTransaction removeItemStackFromSlot(short s, boolean f) { %stransaction.SlotTransaction t = "
               "super.removeItemStackFromSlot(s, f); if (MODE > 0) ARMED = true; return t; }" % (IC_, IC_),
               "public %stransaction.ItemStackSlotTransaction removeItemStackFromSlot(short s, int q, boolean a, boolean f) { "
               "%stransaction.ItemStackSlotTransaction t = super.removeItemStackFromSlot(s, q, a, f); if (MODE > 0) ARMED = true; return t; }" % (IC_, IC_)):
        bc.addMethod(CtNM.make(m_, bc))
    Boom = JClass(bc.toClass(E["SIC"].class_).getName())
    comp = E["STORE"].getClass().getField("M").get(None).get(P1["ref"])
    HotC = JClass(IC_ + "InventoryComponent$Hotbar")
    hk = [k_ for k_ in comp.keySet() if isinstance(comp.get(k_), HotC)][0]
    old_hot, old_comp = P1["hot"], comp.get(hk)

    def boom_hot():
        b_ = Boom(JShort(9))
        comp.put(hk, HotC(b_, jpype.JByte(0)))
        P1["hot"] = b_
        return b_

    def disarm():
        Boom.MODE, Boom.ARMED = 0, False
    try:
        for mode in (1, 2):
            # take 64 Wood_Oak_Log: the storage has room for 10, the boom hotbar is full; the count after the add throws
            d, vd = setup("rescue-take-%d" % mode)
            hb = boom_hot()
            for i in range(9):
                hb.setItemStackForSlot(JShort(i), ISC("Hot_%d" % i, 1), False)
            for i in range(36):
                if P1["storage"].getItemStack(JShort(i)) is None:
                    P1["storage"].setItemStackForSlot(JShort(i), ISC("Fill_%d" % i, 1), False)
            P1["storage"].removeItemStackFromSlot(JShort(35), False)
            P1["storage"].setItemStackForSlot(JShort(35), ISC("Wood_Oak_Log", mx - 10), False)
            base = total(vd)
            tk = tok_of()
            Boom.MODE, Boom.BOOMS = mode, 0
            r = act("take", tk, "1:2:64:Wood_Oak_Log")
            booms = int(Boom.BOOMS)
            disarm()
            x2 = vd.pageCopy(1)[1]
            K.check(booms >= 1 and r == "-That did not finish - 54 Wood_Oak_Log stayed in your vault. See the server log." and x2 is not None
                    and int(x2.getQuantity()) == 54 and int(P1["storage"].getItemStack(JShort(35)).getQuantity()) == mx,
                    "X rescue take (mode %d, %d throws): the 10 that fit are in the inventory, the counted 54 back in the vault (%s)" % (mode, booms, r))
            conserved(vd, base, "rescue take mode %d" % mode)
            lg = open(os.path.join(home[0], "vault.log"), encoding="utf8").read()
            K.check("RESCUE " + US + " take page 1 slot 2" in lg and "LOST-RISK" not in lg, "X rescue take (mode %d): vault.log RESCUE line" % mode)
            # put from the boom hotbar: the count after the remove throws (whole stack, then an amount)
            d, vd = setup("rescue-put-%d" % mode)
            hb = boom_hot()
            hb.setItemStackForSlot(JShort(2), ISC("Ore_Copper", 9), False)
            base = total(vd)
            Boom.MODE, Boom.BOOMS = mode, 0
            r = act("put", tok_of(), "0:3:9:0:Ore_Copper")
            booms = int(Boom.BOOMS)
            disarm()
            K.check(booms >= 1 and r == "-That did not finish - 9 Ore_Copper went into your vault. See the server log." and hb.getItemStack(JShort(2)) is None
                    and str(vd.pageCopy(1)[4].getItemId()) == "Ore_Copper" and int(vd.pageCopy(1)[4].getQuantity()) == 9,
                    "X rescue put (mode %d, %d throws): the 9 that left the hotbar are in the vault (%s)" % (mode, booms, r))
            conserved(vd, base, "rescue put mode %d" % mode)
            hb.setItemStackForSlot(JShort(3), ISC("Ore_Tin", 8), False)
            base = total(vd)
            Boom.MODE, Boom.BOOMS = mode, 0
            r = act("put", tok_of(), "0:4:8:0:3:Ore_Tin")
            booms = int(Boom.BOOMS)
            disarm()
            K.check(booms >= 1 and r == "-That did not finish - 3 Ore_Tin went into your vault. See the server log." and int(hb.getItemStack(JShort(3)).getQuantity()) == 5,
                    "X rescue put amount 3 of 8 (mode %d, %d throws): 3 in the vault, 5 stay (%s)" % (mode, booms, r))
            conserved(vd, base, "rescue put amount mode %d" % mode)
            lg = open(os.path.join(home[0], "vault.log"), encoding="utf8").read()
            K.check(lg.count("RESCUE " + US + " put ") == 2 and "LOST-RISK" not in lg, "X rescue put (mode %d): vault.log RESCUE lines" % mode)
    finally:
        disarm()
        comp.put(hk, old_comp)
        P1["hot"] = old_hot
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass, JShort, JArray
    K = HK.Child(out)
    E = universe(jar)
    jf, BR, Paths = E["jf"], E["BR"], E["Paths"]
    P1, PLAYERS = E["P1"], E["PLAYERS"]
    vd_dir = os.path.join(home, "vaults")
    uids = sorted(f[:-5] for f in os.listdir(vd_dir) if f.endswith(".json"))
    K.check(len(uids) >= 1, "LIVE live vault files: %d" % len(uids))
    OA = lambda xs: JArray(JClass("java.lang.Object"))(xs)

    def file_items(u):
        doc = json.loads(open(os.path.join(vd_dir, u + ".json"), encoding="utf8").read())
        num = lambda v: int(next(iter(v.values()))) if isinstance(v, dict) else int(v)
        c = collections.Counter()
        for pgd in doc.get("content", []):
            for sd in pgd.get("slots", []):
                c[(num(pgd["page"]), num(sd["slot"]) + 1, sd["id"], num(sd["qty"]))] += 1
        for sd in doc.get("orphans", []):
            c[("orphan", sd["id"], num(sd["qty"]))] += 1
        return c

    def start(k, ld):
        J = lambda n: JClass(PKG + n, loader=ld)
        C = J("VCfg")
        C.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyVault")
        C.DIR = Paths.get(home)
        C.VDIR = Paths.get(vd_dir)
        C.FILE = Paths.get(os.path.join(home, "config.properties"))
        C.LOGF = Paths.get(os.path.join(home, "vault.log"))
        C.NAMESF = Paths.get(os.path.join(home, "names.properties"))
        C.load()
        J("VStore").STOPPING = False
        J("VStore").SAVER = None
        BR.clear()
        if k == "new":
            BR.put("vault:fn:view", J("VActFn")(1))
            BR.put("vault:fn:act", J("VActFn")(2))
        return J

    def be(u):
        pr = P1["pr"]
        jf(pr.getClass(), "uuid").set(pr, JClass("java.util.UUID").fromString(u))
        PLAYERS.clear()
        PLAYERS.put(JClass("java.util.UUID").fromString(u), pr)
        for c in (P1["storage"], P1["hot"]):
            c.clear()

    def views(J):
        out = {}
        for u in uids:
            be(u)
            uu = JClass("java.util.UUID").fromString(u)
            d = J("VStore").load(uu)
            pages = int(d.unlocked)
            got = collections.Counter()
            for pg in range(1, pages + 1):
                v = str(BR.get("vault:fn:view").apply(OA([uu, str(pg)])))
                for ln in v.split("\n"):
                    f = ln.split("|")
                    if f[0] == "s":
                        got[(pg, int(f[1]), f[2], int(f[3]))] += 1
            out[u] = got
        return out
    before = dict((u, file_items(u)) for u in uids)
    # start 1
    J = start("new", loader(jar))
    h0 = HK.tree_hash(home)
    v1 = views(J)
    K.check(all(v1[u] == collections.Counter(dict((k_, n) for k_, n in before[u].items() if k_[0] != "orphan")) for u in uids),
            "LIVE start 1: every live vault's view = its file (%d vaults)" % len(uids))
    K.check(HK.tree_hash(home) == h0, "LIVE start 1: viewing writes nothing")
    # a put + take round trip on each live vault (the scratch copy): the file holds the same items after
    trips = 0
    for u in uids:
        be(u)
        uu = JClass("java.util.UUID").fromString(u)
        d = J("VStore").load(uu)
        P1["storage"].setItemStackForSlot(JShort(0), E["ISC"]("Harness_Probe", 3), False)
        v = str(BR.get("vault:fn:view").apply(uu))
        tok, pk, pg = v.split("\n")[0].split("|")[2:5]
        room = [int(ln.split("|")[1]) for ln in v.split("\n") if ln.startswith("p|") and ln.split("|")[2] == "own" and int(ln.split("|")[3]) < int(ln.split("|")[4])]
        if not room:
            K.notes.append("LIVE %s: every page full - round trip skipped" % u[:8])
            P1["storage"].clear()
            continue
        r = str(BR.get("vault:fn:act").apply(OA(["put", uu, tok, pk, "1:1:3:%d:Harness_Probe" % room[0]])))
        m = re.match(r"\+Put 3 Harness_Probe into vault page (\d+) slot (\d+)\.", r)
        K.check(m is not None and P1["storage"].getItemStack(JShort(0)) is None, "LIVE %s: put the probe (%s)" % (u[:8], r))
        v = str(BR.get("vault:fn:view").apply(uu))
        tok = v.split("\n")[0].split("|")[2]
        r2 = str(BR.get("vault:fn:act").apply(OA(["take", uu, tok, pk, "%s:%s:3:Harness_Probe" % (m.group(1), m.group(2))]))) if m else ""
        K.check(r2.startswith("+Took 3 Harness_Probe") and int(P1["storage"].getItemStack(JShort(0)).getQuantity()) == 3, "LIVE %s: took it back (%s)" % (u[:8], r2))
        K.check(file_items(u) == before[u], "LIVE %s: the vault file holds exactly the items it had" % u[:8])
        trips += 1
        P1["storage"].clear()
    K.notes.append("LIVE round trips: %d of %d vaults" % (trips, len(uids)))
    J("VStore").flushAll()
    # start 2 (a fresh loader = fresh statics)
    J2 = start("new", loader(jar))
    v2 = views(J2)
    K.check(v2 == v1, "LIVE start 2 views what start 1 saw")
    # rollback: 0.1.10 reads every file 0.1.11 wrote with the same items
    J3 = start("old", loader(OLD_JAR))
    ok = True
    for u in uids:
        d = J3("VStore").load(JClass("java.util.UUID").fromString(u))
        c = collections.Counter()
        for pg in range(1, int(d.unlocked) + 1):
            arr = d.pageCopy(pg)
            for i in range(len(arr)):
                if arr[i] is not None and not arr[i].isEmpty():
                    c[(pg, i + 1, str(arr[i].getItemId()), int(arr[i].getQuantity()))] += 1
        ok = ok and c == v1[u]
    K.check(ok, "LIVE 0.1.10 (rollback) reads the files 0.1.11 wrote with the same items")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyVault", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyVault"))
