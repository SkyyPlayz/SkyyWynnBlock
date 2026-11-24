"""Harness for SkyyCollections 0.2.37 (the bridge coll:fn:act - /collections' reads + clicks for SkyyMenu's new screen;
tools/collections_0_2_37_patch.py). Build first:
    python tools/collections_0_2_37_patch.py && python SkyyCollections/build_skyycollections_0.2.37.py
      (SkyyGear/SkyyGear-0.3.29.jar gone? set SKYY_GEAR_0329_JAR to a copy extracted from backups/archive/old-jars-20261022.tar.xz)
    python SkyyCollections/test_skyycollections_0.2.37.py [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  S    static37  the patch re-runs to identical bytes; line endings kept; ONE class added (CollActFn), no new command / system; setup puts
                 coll:fn:act (CLOSED reset first), shutdown sets CLOSED first and removes it; CollActFn calls the page's CollBypass.click /
                 offer, CollCraft.query / open, CollNew.seen, CollPage.recipeRows / statusColor (bytecode); reads reach no file call
  A / C / AA     -Xverify:all, class compare 0.2.36 -> 0.2.37 (CollActFn added; setup / shutdown + the version texts), engine-access audit
  TW   twin37    TWO players on the REAL page stand-ins (tools/hub_tab_kit, the real CollPage + PageManager + UICommandBuilder), coin
                 unlocks ON, a purse each: A clicks /collections (CollPage.handleDataEvent: cbuy twice, cpk<i>, opening a collection =
                 the NEW markers seen), B sends coll:fn:act (state / detail read first for the token, profile key and offer, like the
                 Menu). Scripted + 300 random steps (gathering, buy one press / two presses / refused, craft a known / locked recipe,
                 seen): the SAME answer (the page's text + its colour's mark) and the same counts / bought tiers / NEW markers / purse /
                 /craft commands after every step. READ = PAGE: B's reads for A = what A's pages draw (Overview sums, the 4 category
                 cards, each category's card names / progress / Next lines, a collection's name / total / progress / tier states +
                 thresholds + rewards / recipe names + tags / Buy label + info)
  ACT  act37     the bridge's own rules: state / detail lines, not online, changed profile key, stale token (a reload), a changed offer
                 (never pays an unseen price), the 350 ms double click (never arms + pays at once), closing, unknown op / bad
                 arguments / unknown collection / non-array / null / a UUID string, refresh, coins:fn:take refusing, never throws
  LIVE live      0.2.35's live phase (every setup migration + CollReg.loadAll twice on a scratch COPY of the live Skyy_SkyyCollections:
                 no file changes)
  LV37 live37    on another scratch COPY: start twice, then every live profile's coll:fn:act state + one detail per category answer and
                 write no file
  OLD  rbg page fit   0.2.36's phases on the 0.2.37 jar
Exit code 1 on any failure.
"""
import os, sys, re, json, random, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import skyyui as SUI

VERSION, OLD_VERSION = "0.2.37", "0.2.36"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)
GEN = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyycollections_%s.py" % OLD_VERSION)
PATCH = os.path.join(ROOT, "tools", "collections_0_2_37_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wbr1", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyCollectionsPlugin": ["~m setup", "~m shutdown"],
          "CollTier": ["~<clinit>"]}   # NOT this round: the build-time copy of the shared tools/tier_tags.py table (it grew since 0.2.36 was built)
ADDED = ["CollActFn"]
UA, UB = "00000000-0000-0000-0000-00000000a37a", "00000000-0000-0000-0000-00000000b37b"


def tmod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    old, cmp0 = list(sys.argv), HK.run_compare
    sys.argv[:] = [old[0]]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv[:] = old
        HK.run_compare = cmp0
    return m


def T(v):
    return tmod(os.path.join(HERE, "test_skyycollections_%s.py" % v), "tco" + v.replace(".", ""))


def P_(n):
    from jpype import JClass
    return JClass(PKG + n)


def call(Fn, op, u, tok=None, pk=None, arg=None):
    from jpype import JArray, JObject, JString
    a = [JString(op), u, None if tok is None else JString(tok), None if pk is None else JString(pk), None if arg is None else JString(arg)]
    return str(Fn.apply(JArray(JObject)(a)))


def lines(st, k):
    return [ln[len(k) + 1:] for ln in st.split("\n") if ln.startswith(k + "|")]


def mark(t):
    """CollPage.statusColor's rule (the page's colour of a text) as a mark"""
    if t is None or t == "":
        return ""
    if t.startswith("Bought the tier "):
        return "+" + t
    if t.startswith("Click Buy again "):
        return "=" + t
    return "-" + t


def pyfn(f):
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class _F(object):
        @JOverride
        def apply(self, a):
            return f(a)
    return _F()


# ------------------------------------------------------------------------------------------------------------------- S
def run_static37(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.37"') == 1 and '[SkyyCollections] 0.2.37 ready (' in g, "S version + ready line")
    for w in ("registerSystem(", "registerCommand("):
        K.eq(g.count(w), o.count(w), "S no new %s" % w)
    K.eq(g.count(" = K(") - o.count(" = K("), 1, "S one class added (CollActFn)")
    su = g[g.index("public void setup() {"):]
    su = su[:su.index("protected void shutdown()")]
    K.check(su.index("CollActFn.CLOSED = false;") < su.index('b.put("coll:fn:act", new @PKG@.CollActFn());'), "S setup: CLOSED reset, then coll:fn:act put")
    sd = g[g.index("protected void shutdown() {"):]
    K.check(sd.index("CollActFn.CLOSED = true;") < sd.index('remove("coll:fn:act")') < sd.index("this.saver.cancel"), "S shutdown: CLOSED first, key removed")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    HK.jvm([B.JAVASSIST, B.SERVER_JAR], verify=False)
    gr = PW.calls(jar)
    a = gr.get("CollActFn.act", set())
    K.check({PKG + "CollBypass.click", PKG + "CollBypass.offer", PKG + "CollCraft.query", PKG + "CollCraft.open", PKG + "CollNew.seen"} <= a,
            "S CollActFn.act calls the page's CollBypass.click / offer, CollCraft.query / open, CollNew.seen")
    K.check(PKG + "CollPage.recipeRows" in gr.get("CollActFn.detail", set()) and PKG + "CollPage.statusColor" in gr.get("CollActFn.mark", set()),
            "S detail reads CollPage.recipeRows; the mark = CollPage.statusColor")
    IO = set(PW.IO_TARGETS)
    io_of = lambda h: sorted(m for m in PW.reach(gr, h, PKG) if any(c in IO for c in gr.get(m, ())))
    pg_io = set(io_of("CollPage.build"))
    for h in ("CollActFn.state", "CollActFn.detail"):
        bad = sorted(set(io_of(h)) - pg_io)
        K.check(h in gr and not bad, "S %s reaches no file call the page's own draw (CollPage.build: the counts file load) does not: %s" % (h, bad))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- stage
def stage(K, scratch, sub):
    from jpype import JClass
    t23 = T("0.2.23")
    E, Reg, Store, PA = t23.stage_player(K, scratch, JAR, sub, UA)
    PB = E.mkp(E.UUID.fromString(UB), "BridgeB")
    Reg.BYPASS = True
    Long, Bool = JClass("java.lang.Long"), JClass("java.lang.Boolean")
    purse = {UA: 100000, UB: 100000}
    flags = {"take": True}

    def take(a):
        u, n = str(a[0]), int(a[1])
        if not flags["take"] or purse.get(u, 0) < n:
            return Bool.FALSE
        purse[u] -= n
        return Bool.TRUE

    def add(a):
        purse[str(a[0])] = purse.get(str(a[0]), 0) + int(a[1])
        return Long(purse[str(a[0])])
    E.bridge.put("coins:fn:take", pyfn(take))
    E.bridge.put("coins:fn:add", pyfn(add))
    E.CM.cmds.put("craft", E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    # a bare JVM has no recipe assets: give 4 collections (each curve a coin wall allows) recipes at tiers 1-5, as 0.2.36's page phase does
    R = Reg.D
    m = JClass("java.util.HashMap")()
    done, curves = 0, set()
    items = ["Ingredient_Bar_Iron", "Armor_Copper_Head", "Armor_Copper_Chest", "Tool_Pickaxe_Mithril", "Weapon_Sword_Iron", "Zzz_Thing"]
    for c in range(int(R.n)):
        if done >= 4 or bool(R.hidden[c]) or bool(R.nobypass[c]) or int(Reg.BYP_WALL[int(R.curve[c])]) <= 0 or str(R.id[c]) in ("Wheat", "OakLog"):
            continue
        for t in range(1, 6):
            m.put("%d.%d" % (c, t), t23.jstrs(["%s_C%d_Recipe_Generated_0" % (items[(t + done) % len(items)], c), "Zz_Item%d_%d_Recipe_Generated_0" % (c, t)]))
        done += 1
    Reg.RECIPES = m
    return t23, E, Reg, Store, PA, PB, purse, flags


def ci(R, cid):
    """the index of the collection whose id is cid (the bridge's ids are R.id - byId holds lower-case keys)"""
    for c in range(int(R.n)):
        if str(R.id[c]) == str(cid):
            return c
    raise KeyError(cid)


def buyable(Reg):
    """collections a coin unlock can buy from tier I (wall > 0, a buyable recipe up to the wall) - the page's CollBypass rules"""
    R = Reg.D
    Byp = P_("CollBypass")
    out = []
    for c in range(int(R.n)):
        if bool(R.hidden[c]) or bool(R.nobypass[c]):
            continue
        wall = int(Reg.BYP_WALL[int(R.curve[c])])
        mx = int(Reg.maxTier(R, c))
        if wall > 0 and bool(Byp.chainBuyable(c, 1, min(wall, mx))):
            out.append(str(R.id[c]))
    return out


def give(Store, Reg, u, cid, n):
    from jpype import JClass
    R = Reg.D
    c = ci(R, (cid))
    d = Store.data(u)
    it = str(R.items[c][0])
    cur = d.items.get(it)
    d.items.put(it, JClass("java.lang.Long").valueOf((0 if cur is None else int(cur)) + n))


def snap(Store, Reg, u, purse, cids):
    from jpype import JClass
    R = Reg.D
    d = Store.data(u)
    Byp, New = P_("CollBypass"), P_("CollNew")
    out = {}
    for cid in cids:
        c = ci(R, (cid))
        out[cid] = (int(Store.sum(d, R, c)), int(Store.boughtTier(d, R, c)), [bool(New.isNew(d, R, c, t)) for t in range(1, int(Reg.maxTier(R, c)) + 1)])
    out["purse"] = purse[str(u)]
    return out


# ------------------------------------------------------------------------------------------------------------------- TW
def run_twin37(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    t23, E, Reg, Store, PA, PB, purse, flags = stage(K, scratch, "tw")
    uA, uB = PA.pr.getUuid(), PB.pr.getUuid()
    R = Reg.D
    Fn = P_("CollActFn")()
    Act = P_("CollActFn")
    New = P_("CollNew")
    cids = [str(R.id[c]) for c in range(int(R.n)) if not bool(R.hidden[c])]
    pick = buyable(Reg)[:3] + [x for x in ("Wheat", "OakLog") if x in cids] + [cids[-1]]
    K.check(len(pick) >= 4, "TW collections to play with: %s" % pick)
    diffs, steps = [], [0]
    state = {"pg": None}

    def page_open(cid):
        state["pg"] = t23.open_coll(E, PA, ci(R, (cid)))
        return state["pg"]

    def page_click(word):
        pg = state["pg"]
        st0 = str(pg.status)
        cur = t23.click(E, PA, pg, word)
        return pg, cur, st0

    def bread(cid):
        """the Menu draws the collection: detail, then seen (what the page's own draw does once)"""
        dt = call(Fn, "detail", uB, arg=cid)
        h = lines(dt, "h")[0].split("|")
        Act.LASTOP.clear()
        call(Fn, "seen", uB, h[0], h[1], cid)
        Act.LASTOP.clear()
        return dt, h

    def redraw(cid):
        dt, h = bread(cid)

    def cmp(what, ra, rb, ca=None, cb=None):
        steps[0] += 1
        sa, sb = snap(Store, Reg, uA, purse, pick), snap(Store, Reg, uB, purse, pick)
        if ra != rb or sa != sb or ca != cb:
            diffs.append((what, ra, rb, [k for k in sa if sa[k] != sb[k]], ca, cb))

    def buy(cid):
        Act.LASTOP.clear()
        page_open(cid)
        pg, cur, st0 = page_click("cbuy")
        ra = mark(str(pg.status))
        dt, h = bread(cid)
        b = lines(dt, "b")
        if b:
            nt, pr = b[0].split("|")[:2]
            rb = call(Fn, "buy", uB, h[0], h[1], "%s|%s|%s" % (cid, nt, pr))
        else:
            y = lines(dt, "y")
            rb = call(Fn, "buy", uB, h[0], h[1], "%s|1|1" % cid)
            if y and rb != "-" + y[0]:
                rb = "MISMATCH refusal %s / %s" % (rb, y)
        redraw(cid)                                 # the answer redraws the view (the page rebuilds after its click)
        cmp("buy " + cid, ra, rb)

    def craft(cid, i):
        Act.LASTOP.clear()
        pg = page_open(cid)
        rows = list(pg.prid) if pg.prid is not None else []
        if i >= len(rows):
            return
        rid = str(rows[i])
        E.CM.lines.clear()
        pg, cur, st0 = page_click("cpk%d" % i)
        ca = [str(x) for x in E.CM.lines]
        ra = "+" if ca else mark(str(pg.status))
        E.CM.lines.clear()
        dt, h = bread(cid)
        rb = call(Fn, "craft", uB, h[0], h[1], rid)
        cb = [str(x) for x in E.CM.lines]
        if not rb.startswith("+"):
            redraw(cid)                             # a refused craft: the page rebuilds with the reason
        cmp("craft %s %s" % (cid, rid), ra, rb, [x.split(" ", 1)[1] for x in ca], [x.split(" ", 1)[1] for x in cb])

    def seen(cid):
        Act.LASTOP.clear()
        page_open(cid)
        t23.HT.build(state["pg"], PA)          # drawing the collection's page = its NEW markers seen (the page's own draw)
        dt, h = bread(cid)
        rb = call(Fn, "seen", uB, h[0], h[1], cid)
        cmp("seen " + cid, "", rb)

    def gain(cid, n):
        give(Store, Reg, uA, cid, n)
        give(Store, Reg, uB, cid, n)
        cmp("gain %s %d" % (cid, n), "", "")

    def marknew(cid, t0, t1):
        c = ci(R, (cid))
        for u in (uA, uB):
            New.mark(Store.data(u), str(u), R, c, t0, t1)
        cmp("mark new " + cid, "", "")

    # ---- scripted
    c0 = pick[0]
    buy(c0)                                         # undiscovered: "Collect one first"
    gain(c0, 1)
    buy(c0)                                         # press 1: Click Buy again
    buy(c0)                                         # press 2: pays
    buy(c0)                                         # the next tier: press 1
    flags["take"] = False
    buy(c0)                                         # press 2: SkyyCoins refuses -> "You need ... coins"
    flags["take"] = True
    gain(pick[1], int(Reg.threshold(R, ci(R, (pick[1])), 3)))
    marknew(pick[1], 1, 3)
    seen(pick[1])
    for i in range(4):
        craft(pick[1], i)
        craft(c0, i)
    Reg.BYPASS = False
    buy(c0)                                         # coin unlocks off: the page's refusal
    Reg.BYPASS = True
    K.check(not diffs, "TW scripted: the same answer + state after every step (%d steps): %s" % (steps[0], diffs[:3]))
    K.check(purse[UA] == purse[UB] < 100000, "TW scripted: both paid the same coins (%s / %s)" % (purse[UA], purse[UB]))
    readpage(K, t23, E, Reg, Store, PA, Fn, "scripted")
    # ---- random
    rnd = random.Random(37)
    n0 = steps[0]
    for k in range(300):
        cid = rnd.choice(pick)
        r = rnd.random()
        if r < 0.35:
            buy(cid)
        elif r < 0.55:
            craft(cid, rnd.randrange(0, 6))
        elif r < 0.65:
            seen(cid)
        elif r < 0.72:
            c = ci(R, (cid))
            mx = int(Reg.maxTier(R, c))
            a = rnd.randrange(1, mx + 1)
            marknew(cid, a, min(mx, a + 1))
        elif r < 0.77:
            flags["take"] = not flags["take"]
        else:
            c = ci(R, (cid))
            gain(cid, rnd.choice([1, 5, 50, max(1, int(Reg.threshold(R, c, rnd.randrange(1, 4))) // 3)]))
    flags["take"] = True
    K.check(not diffs, "TW 300 random steps: the same answer + state every time (%d steps): %s" % (steps[0] - n0, diffs[:3]))
    K.check(purse[UA] == purse[UB], "TW random: the same purse (%s)" % purse[UA])
    readpage(K, t23, E, Reg, Store, PA, Fn, "after the random run")
    K.notes.append("TW %d twin steps; purse %s" % (steps[0], purse[UA]))
    K.save()


def readpage(K, t23, E, Reg, Store, P, Fn, tag):
    """the bridge reads for P = what P's /collections pages draw"""
    R = Reg.D
    u = P.pr.getUuid()
    Page, Craft, Util = P_("CollPage"), P_("CollCraft"), P_("CollUtil")
    st = call(Fn, "state", u)
    h = lines(st, "h")[0].split("|")
    pg = t23.open_coll(E, P, -1)
    sets = t23.sets_of(t23.HT.build(pg, P)[0])
    tx = lambda s: t23.txt(sets, s)
    K.eq(tx("#SkyyCSum.Text"), "Tiers %s / %s      Maxed %s      Recipes unlocked %s      Score %s" % (h[3], h[4], h[5], h[7], h[3]), "READ %s: the Overview sums" % tag)
    ks = [k.split("|") for k in lines(st, "k")]
    K.eq([(tx("#SkyyCCatNm%d.Text" % i), tx("#SkyyCCatFound%d.Text" % i), tx("#SkyyCCatTiers%d.Text" % i)) for i in range(4)],
         [(k[7], "%s of %s found" % (k[1], k[2]), "Tiers %s / %s     Maxed %s" % (k[3], k[4], k[5])) for k in ks], "READ %s: the 4 category cards" % tag)
    cs = [c.split("|", 6) for c in lines(st, "c")]
    ps = dict((p.split("|")[0], p.split("|", 2)[1:]) for p in lines(st, "p"))
    bad = []
    for cat in range(4):
        pg = t23.click(E, P, pg, "ccat%d" % cat)
        sets = t23.sets_of(t23.HT.build(pg, P)[0])
        mine = [c for c in cs if c[1] == str(cat)]
        found = [c for c in mine if int(c[2]) > 0]
        for n, c in enumerate(found):
            got = (t23.txt(sets, "#SkyyCCd%dNm.Text" % n), t23.txt(sets, "#SkyyCCdProg%d.Text" % n),
                   t23.txt(sets, "#SkyyCCdNext%d.Text" % n))
            want = (c[6], str(Craft.fitPx(ps[c[0]][0], Page.CDTEXT)), str(Craft.fitPx(ps[c[0]][1], Page.CDNEXT2)))
            if got != want:
                bad.append((cat, n, got, want))
        if len(pg.cards) != len(mine):
            bad.append((cat, "cards", len(pg.cards), len(mine)))
    K.check(not bad, "READ %s: every category's cards (order, name, progress, Next line) = the c / p lines: %s" % (tag, bad[:3]))
    bad = []
    for c in [c for c in cs if int(c[2]) > 0][:8] + [c for c in cs if int(c[2]) == 0][:2]:
        cid = c[0]
        dt = call(Fn, "detail", u, arg=cid)
        dh = lines(dt, "h")[0].split("|")
        pg = t23.open_coll(E, P, ci(R, (cid)))
        sets = t23.sets_of(t23.HT.build(pg, P)[0])
        tx = lambda s: t23.txt(sets, s)
        if (tx("#SkyyCDName.Text"), tx("#SkyyCDTotal.Text"), tx("#SkyyCDProg.Text"), tx("#SkyyCFrom.Text")) != (
                dh[10], "Total collected: " + str(Util.fmt(int(dh[4]))), lines(dt, "g")[0], "From: " + lines(dt, "m")[0].split("|", 2)[2]):
            bad.append((cid, "head", tx("#SkyyCDName.Text"), tx("#SkyyCDProg.Text"), lines(dt, "g")))
        for r in lines(dt, "r"):
            t, s_, thr, rew = r.split("|", 3)
            fits = [str(Craft.fitPx(rew, w)) for w in (Page.TIERREW, Page.TIERREW2, Page.TIERREW3)]
            if (tx("#SkyyCTr%sS.Text" % t), tx("#SkyyCThr%s.Text" % t)) != (s_, str(Util.fmt(int(thr)))) or tx("#SkyyCRew%s.Text" % t) not in fits:
                bad.append((cid, "tier", t, tx("#SkyyCTr%sS.Text" % t), s_, tx("#SkyyCRew%s.Text" % t), rew))
        for i, q in enumerate(lines(dt, "q")[:int(Page.PRMAX)]):
            rid, ok, ti, tag_, cc, nm = q.split("|", 5)
            if tx("#SkyyCPr%dG.Text" % i) != tag_ or tx("#SkyyCPr%dN.Text" % i) not in (str(Craft.fitPx(nm, Page.RPNAME)), str(Craft.fitPx(nm, Page.RPNAME2))) or str(pg.prid[i]) != rid:
                bad.append((cid, "recipe", i, tx("#SkyyCPr%dN.Text" % i), nm))
        b, y = lines(dt, "b"), lines(dt, "y")
        if b:
            nt, pr, info = b[0].split("|", 2)
            if (tx("#SkyyCBuyLbl.Text"), tx("#SkyyCBuyInfo.Text")) != ("Buy tier %s unlocks - %s coins" % (Util.roman(int(nt)), pr), info):
                bad.append((cid, "buy", tx("#SkyyCBuyLbl.Text"), tx("#SkyyCBuyInfo.Text"), b))
        elif y and tx("#SkyyCBuyInfo.Text") != y[0]:
            bad.append((cid, "nobuy", tx("#SkyyCBuyInfo.Text"), y))
    K.check(not bad, "READ %s: 10 collection pages (head, tiers, rewards, recipes, Buy) = the detail lines: %s" % (tag, bad[:3]))


# ------------------------------------------------------------------------------------------------------------------- ACT
def run_act37(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JString
    K = HK.Child(out)
    t23, E, Reg, Store, PA, PB, purse, flags = stage(K, scratch, "ac")
    u = PB.pr.getUuid()
    R = Reg.D
    Act = P_("CollActFn")
    Fn = Act()
    st = call(Fn, "state", u)
    h = lines(st, "h")[0].split("|")
    K.check(len(h) == 9 and h[0].startswith("c") and h[1] == UB and h[2] == "1" and h[8] == "1", "ACT state header: %s" % h)
    K.check(len(lines(st, "k")) == 4 and len(lines(st, "c")) == len([c for c in range(int(R.n)) if not bool(R.hidden[c])]) and not lines(st, "p"),
            "ACT 4 category lines, one c line per shown collection, no p line (nothing found)")
    cid = buyable(Reg)[0]
    c = ci(R, (cid))
    give(Store, Reg, u, cid, 1)
    tok, pk = h[0], h[1]
    dt = call(Fn, "detail", u, arg=cid)
    dh = lines(dt, "h")[0].split("|")
    K.check(len(dh) == 11 and dh[2] == cid and dh[4] == "1" and len(lines(dt, "r")) == int(Reg.maxTier(R, c)) and lines(dt, "b"), "ACT detail: header, a tier line each, an offer: %s" % dh)
    nt, pr = lines(dt, "b")[0].split("|")[:2]
    K.eq(call(Fn, "refresh", u, tok, pk), "", "ACT refresh")
    r1 = call(Fn, "buy", u, tok, pk, "%s|%s|%s" % (cid, nt, pr))
    K.check(r1.startswith("=Click Buy again within 10 s to pay "), "ACT buy press 1 arms: %s" % r1)
    K.eq(call(Fn, "buy", u, tok, pk, "%s|%s|%s" % (cid, nt, pr)), "=One moment.", "ACT press 2 within 350 ms = One moment (never arms and pays in one go)")
    K.eq(purse[UB], 100000, "ACT ... nothing paid")
    Act.LASTOP.clear()
    give(Store, Reg, u, cid, 1)                    # one more gathered: the price drops
    r2 = call(Fn, "buy", u, tok, pk, "%s|%s|%s" % (cid, nt, pr))
    K.check(r2 == "=The offer changed - look again. Nothing changed." and purse[UB] == 100000, "ACT a changed price: refused, nothing paid (%s)" % r2)
    dt = call(Fn, "detail", u, arg=cid)
    nt, pr = lines(dt, "b")[0].split("|")[:2]
    Act.LASTOP.clear()
    call(Fn, "buy", u, tok, pk, "%s|%s|%s" % (cid, nt, pr))
    Act.LASTOP.clear()
    r3 = call(Fn, "buy", u, tok, pk, "%s|%s|%s" % (cid, nt, pr))
    K.check(r3.startswith("+Bought the tier ") and purse[UB] == 100000 - int(pr) and int(Store.boughtTier(Store.data(u), R, c)) == int(nt), "ACT press 2 pays: %s" % r3)
    for arg in ("", cid, "%s|x|1" % cid, "%s|1" % cid):
        Act.LASTOP.clear()
        K.eq(call(Fn, "buy", u, tok, pk, arg), "-Pick a collection's offer first." if arg not in ("",) else "-No collection ''.", "ACT bad buy argument %r" % arg)
    Act.LASTOP.clear()
    K.eq(call(Fn, "buy", u, tok, pk, "Nope|1|1"), "-No collection 'Nope'.", "ACT buy: unknown collection")
    Act.LASTOP.clear()
    K.eq(call(Fn, "craft", u, tok, pk, ""), "-That recipe is not on this page any more.", "ACT craft without a recipe")
    Act.LASTOP.clear()
    K.eq(call(Fn, "craft", u, tok, pk, "Nope_Recipe_Generated_0"), "-That recipe is not unlocked yet.", "ACT craft a locked recipe")
    Act.LASTOP.clear()
    K.eq(call(Fn, "seen", u, tok, pk, "Nope"), "-No collection 'Nope'.", "ACT seen: unknown collection")
    K.eq(call(Fn, "detail", u, arg="Nope"), "-No collection 'Nope'.", "ACT detail: unknown collection")
    Act.LASTOP.clear()
    K.eq(call(Fn, "frob", u, tok, pk, ""), "-Unknown collections action.", "ACT unknown op")
    K.check(call(Fn, "seen", u, tok, "other", cid).startswith("=Your profile changed"), "ACT a changed profile key")
    K.check(call(Fn, "seen", u, tok, None, cid).startswith("=Your profile changed"), "ACT no profile key")
    K.check(call(Fn, "seen", u, "c0", pk, cid).startswith("=The collections changed"), "ACT a stale token")
    Reg.loadAll()                                  # /collections reload: a new registry -> a new stamp
    K.check(call(Fn, "seen", u, tok, pk, cid).startswith("=The collections changed"), "ACT a reload makes the old page stale")
    tok = lines(call(Fn, "state", u), "h")[0].split("|")[0]
    Act.LASTOP.clear()
    K.eq(call(Fn, "seen", u, tok, pk, cid), "", "ACT ... the new token works (seen answers '')")
    Act.CLOSED = True
    K.check(call(Fn, "seen", u, tok, pk, cid).startswith("-Collections are shutting down"), "ACT closing: refused")
    K.check(call(Fn, "state", u).startswith("h|"), "ACT closing: a read still answers")
    Act.CLOSED = False
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = t23.HT.jf(UniC.class_, "playersByUuid").get(UniC.get())
    byU.remove(u)
    K.eq(call(Fn, "seen", u, tok, pk, cid), "-You are not online.", "ACT not online")
    byU.put(u, PB.pr)
    K.eq(str(Fn.apply("nope")), "-Unknown collections action.", "ACT a non-array argument")
    K.eq(str(Fn.apply(None)), "-Unknown collections action.", "ACT null")
    K.check(str(Fn.apply(JArray(JObject)([JString("state"), JString(UB)]))).startswith("h|"), "ACT the player as a UUID string")
    K.eq(str(Fn.apply(JArray(JObject)([JString("state"), JString("x")]))), "-Something went wrong - try again.", "ACT a bad UUID string never throws")
    Reg.D = None
    K.check(call(Fn, "state", u).split("|")[3] == "0" and call(Fn, "detail", u, arg=cid) == "-Collections are not loaded.", "ACT no registry: ready 0, detail refused")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- LIVE
def run_live(out, jar, scratch, home):
    T("0.2.35").run_live(out, jar, scratch, home)


def run_live37(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    t31 = T("0.2.35").t31()
    Reg = t31.boot(home)
    P = JClass("java.nio.file.Paths").get(home)
    MIGS = ("CollBagMigrate", "CollBypassMig", "CollCoinMig", "CollEnch28Mig", "CollP6Mig", "CollP6EnchMig", "CollP7Mig")
    for _ in range(2):
        for cn in MIGS:
            JClass(PKG + cn).run(P)
        Reg.loadAll()
    s1 = t31.snapd(home)
    R = Reg.D
    cur = {"k": None}
    br.put("profile:fn:key", pyfn(lambda a: cur["k"]))
    Fn = P_("CollActFn")()
    U = JClass("java.util.UUID")
    n = 0
    for f in sorted(os.listdir(os.path.join(home, "counts"))):
        if not f.endswith(".properties"):
            continue
        key = f[:-len(".properties")]
        try:
            u = U.fromString(key[:36])
        except Exception:
            continue
        cur["k"] = key
        st = call(Fn, "state", u)
        h = lines(st, "h")[0].split("|")
        found = [c.split("|") for c in lines(st, "c") if int(c.split("|")[2]) > 0]
        ok = h[1] == key and h[2] == "1" and len(lines(st, "k")) == 4 and len(lines(st, "p")) == len(found)
        dets = []
        for cat in range(4):
            mine = [c for c in found if c[1] == str(cat)]
            if mine:
                dt = call(Fn, "detail", u, arg=mine[0][0])
                dets.append(lines(dt, "h")[0].split("|")[2] == mine[0][0] and len(lines(dt, "r")) >= 1)
        K.check(ok and all(dets), "LV37 profile %s: state (%d found, tiers %s / %s) + %d details answer" % (key, len(found), h[3], h[4], len(dets)))
        n += 1
    K.check(n >= 1, "LV37 %d live profile(s) read" % n)
    K.check(t31.snapd(home) == s1, "LV37 reading every profile wrote no file")
    K.save()


def run_rbg(out, jar, scratch, home):
    T("0.2.36").run_rbg(out, jar, scratch, home)


def run_page(out, jar, scratch, home):
    T("0.2.36").run_page(out, jar, scratch, home)


def run_fit(out, jar, scratch, home):
    T("0.2.36").run_fit(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyCollections", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static37", run_static37), ("twin37", run_twin37), ("act37", run_act37), ("live", run_live), ("live37", run_live37),
                   ("rbg", run_rbg), ("page", run_page), ("fit", run_fit)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyCollections"))
