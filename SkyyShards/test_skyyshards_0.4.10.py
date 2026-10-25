"""Harness for SkyyShards 0.4.10 (HOTFIX: opening a shard menu disconnected the client - "Selected element in CustomUI command was not
found. Selector: #SkyyShStatus0.Text"; tools/shards_0_4_10_patch.py).
Build first:
    python tools/shards_0_4_10_patch.py && python SkyyShards/build_skyyshards_0.4.10.py
    python SkyyShards/test_skyyshards_0.4.10.py [--keep]

  S    static   the patch re-runs to identical bytes; no new registerSystem / registerCommand; the ready line names the hotfix
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.9 -> 0.4.10: exactly the planned members differ (EXPECT) - ShPage build / buildFull / kUpd + kShown / kShownSig
  49   every 0.4.9 harness phase on the 0.4.10 jar (and through it the 0.4.8 / 0.4.7 / 0.4.6 phases)
  O    order    THE CLIENT'S VIEW: every page variant (Map tab x 6 shards x 3 zooms x shard / island / buy view, owner / co-op / locked /
                switched off, the Collect + Totems tabs, the exit page, a totem's page, the bench's 3 tabs) is built on the real
                UICommandBuilder and its commands are walked IN ORDER like the client does: every selector a Set / Append touches must
                already exist at that moment; every event binding's element exists at the end. 0.4.9 fails this phase (the status line).
  F    flows    EXECUTED click flows on a simulated client (the page the client holds = the last full build): portal open -> click ->
                zoom 150 -> click -> zoom 200 -> purchases -> rail switch -> tabs -> back to the Map -> zoom out; a totem / bench page
                getting a Map click; the keep update only ever sent on the exact Map page variant the client shows (view / tab / shard /
                zoom), every selector it sets exists on that page; state drift (kShown cleared, tab changed without a build) = rebuild
  D    live     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards (0.4.9 live): no migration again, every real placed shard's
                menu opened + clicked through the simulated client, a second start writes nothing
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.10"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shhot", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.9.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.9.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_10_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_9", os.path.join(HERE, "test_skyyshards_0.4.9.py"))
T49 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T49)
sys.argv[:] = _argv
T49.JAR = JAR
T48 = T49.T48
T46, T42 = T49.T46, T49.T42
OWNER, MEMBER = T49.OWNER, T49.MEMBER
MKD, FOK, FK, RK, OK_, CK = 0, 1, 2, 3, 4, 5


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.10 - build script') and g.count('VERSION = "0.4.10"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check("0.4.10: the shard menu opens again" in g, "S the ready line names the hotfix")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


# ---------------------------------------------------------------------------------------------------------- the client's view of a command list
IDRX = re.compile(r"#([A-Za-z0-9]+)\s*\{")
SELRX = re.compile(r"#([A-Za-z0-9]+)")


def walk(cmds, have=()):
    """the commands IN ORDER, as the client runs them: every element a selector names must exist at that moment (else the client drops).
    returns (the elements after the list, [(index, type, selector)] missing, set of command types, number of appends)"""
    have = set(have)
    miss, types, nap = [], set(), 0
    for i, c in enumerate(cmds):
        t = str(c.type)
        types.add(t)
        sel = str(c.selector) if c.selector is not None else ""
        for n in SELRX.findall(sel):
            if n not in have:
                miss.append((i, t, sel))
        if "Append" in t or "Insert" in t:
            nap += 1
            have.update(IDRX.findall(str(c.text) if c.text is not None else ""))
        elif t == "Remove":
            for n in SELRX.findall(sel)[-1:]:
                have.discard(n)
        elif t == "Clear":
            miss.append((i, t, sel + " (Clear: not modelled)"))
    return have, miss, types, nap


def full(pg):
    """one full page build on the real builders, walked from an empty page"""
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    pg.build(None, b, ev, None)
    have, miss, types, nap = walk(b.getCommands())
    ubind = [str(e.selector) for e in ev.getEvents() if any(n not in have for n in SELRX.findall(str(e.selector)))]
    return dict(have=have, miss=miss, types=types, unbound=ubind, n=len(b.getCommands()))


def _world(scratch, K):
    """the 0.4.9 page fixture: an owner with the Farming + Mining portals on their island, Orchard elsewhere, items + coins"""
    L = T49._setup(scratch, K)
    from jpype import JInt
    St, Isl, Mth, Core, Door, Page = (L[n] for n in ("ShStore", "ShIsl", "ShMath", "ShCore", "ShDoor", "ShPage"))
    ou = L["UUID"].fromString(OWNER)
    W = "skyy-island-" + OWNER
    now = 1790000000000
    Core.NOW_TEST = now
    lv = {"Farming": 9, "Mining": 2, "Orchard": 9, "Foraging": 9, "Ranching": 9}
    Isl.LEVEL_TEST = L["PyFn"](lambda a: JInt(lv[str(a[2])]) if str(a[2]) in lv else JInt(-1))
    for kk_, xyz in (("farming", (29, 129, -31)), ("mining", (-43, 124, 4))):
        Door.door(ou, OWNER, kk_, W, xyz[0], xyz[1], xyz[2])
    p = St.get(OWNER)
    St.LOCK.lock()
    try:
        Mth.starter(OK_, p, L["JLong"](now))
        p.setProperty("orchard.placed", "skyy-island-elsewhere|1|2|3")
        p.setProperty("farming.i0.totems", "harvest_spirit:2:wider::0:pp0001,rain:1:::0:pp0002:gf")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    cs = L["inv"](27, 27, 9)
    L["coins"]["bal"] = 10000000
    T48._fill(L, cs, [("Plant_Crop_Lettuce_Item", 600), ("Plant_Seeds_Lettuce", 200), ("Plant_Crop_Wheat_Item", 1200), ("Skyy_Ench_Wheat", 200),
                      ("Plant_Crop_Carrot_Item", 400), ("Plant_Seeds_Carrot", 100), ("Wood_Oak_Trunk", 300), ("Rock_Stone_Cobble", 300),
                      ("Ingredient_Water_Essence", 60), ("Ingredient_Void_Essence", 40)])
    Page.TEST_INV = cs
    return L, ou, W, p, lv


def run_order(out, jar, scratch, _home):
    K = HK.Child(out)
    L, ou, W, p, lv = _world(os.path.join(scratch, "o"), K)
    Page, PFn, Cfg = L["ShPage"], L["ShPageFn"], L["ShCfg"]
    mu = L["UUID"].fromString(MEMBER)
    SHW = "skyy-shard-" + OWNER
    seen = {"variants": 0, "types": set()}
    bad = []

    def chk(pg, what):
        r = full(pg)
        seen["variants"] += 1
        seen["types"] |= r["types"]
        if r["miss"] or r["unbound"]:
            bad.append((what, r["miss"], r["unbound"]))
        return r

    for who, u in (("owner", ou), ("co-op", mu)):
        for kd in range(6):
            for tab in (1, 0, 3):
                for z in range(3):
                    for mv in ("hub", "mn0", "mn1", "mn2"):
                        if tab != 1 and (z > 0 or mv != "hub"):
                            continue
                        pg = Page(u, W)
                        pg.kind = kd
                        pg.view = 0
                        pg.tab = tab
                        pg.zoom = z
                        if mv != "hub":
                            pg.act(mv, None, None)
                        for st in ("", "+bought", "-no coins", "=info"):
                            pg.status(st)
                            chk(pg, "%s %s tab %d zoom %d %s status %r" % (who, KINDS[kd], tab, z, mv, st))
    # a locked shard, the switch off, the bench + exit + totem pages
    lv["Farming"] = 1
    pg = Page(ou, W); pg.kind = FK; pg.zoom = 2
    chk(pg, "locked Farming at 200 %")
    lv["Farming"] = 9
    Cfg.ON = False
    pg = Page(ou, W); pg.kind = FK
    chk(pg, "shards switched off")
    Cfg.ON = True
    for mode, name in ((0, "exit page (the hub stand)"), (1, "a totem's page"), (2, "the bench")):
        for u, who in ((ou, "owner"), (mu, "co-op")):
            pg = PFn(FK, mode).make(None, u, SHW)
            K.check(pg is not None, "O %s opens for the %s" % (name, who))
            if pg is None:
                continue
            pg.near = False
            for sub in range(3):
                if mode == 2:
                    pg.bTab = sub
                elif mode == 1:
                    pg.tpad = sub
                elif sub > 0:
                    break
                chk(pg, "%s %s %d" % (who, name, sub))
    # the portal open itself (ShPageFn.make, mode 0): every shard, owner + co-op
    for kd in range(6):
        for u, who in ((ou, "owner"), (mu, "co-op")):
            pg = PFn(kd, 0).make(None, u, W)
            if pg is not None:
                chk(pg, "portal open %s (%s)" % (KINDS[kd], who))
    dist = sorted(set(m_[2] for _w, ms_, _u in bad for m_ in ms_) | set(u_ for _w, _m, us_ in bad for u_ in us_))
    K.check(not bad, "O every selector exists when its command runs + every binding's element at the end, over %d page builds: %d builds bad, "
            "missing %s; first %s" % (seen["variants"], len(bad), dist[:12], bad[:1]))
    K.check(seen["variants"] > 400 and "Set" in seen["types"], "O %d builds walked; command types %s" % (seen["variants"], sorted(seen["types"])))
    Page.TEST_INV = None
    L["ShIsl"].LEVEL_TEST = None
    K.save()


KINDS = ["Mining", "Foraging", "Farming", "Ranching", "Orchard", "Combat"]


class Client(object):
    """the client: holds the elements of the last full page it got; a keep update is walked against that page"""

    def __init__(self, K, pg, name):
        self.K, self.pg, self.name = K, pg, name
        self.have, self.sig, self.fulls, self.keepsN, self.bad = None, None, 0, 0, []

    def sigNow(self):
        p = self.pg
        return (int(p.view), int(p.tab), int(p.kind), int(p.zoom))

    def open(self, what="open"):
        r = full(self.pg)
        self.fulls += 1
        if r["miss"] or r["unbound"]:
            self.bad.append(("%s: %s" % (self.name, what), r["miss"][:3], r["unbound"][:3]))
        self.have, self.sig = r["have"], self.sigNow()
        return "full"

    def click(self, a, want=None):
        """one click as the server answers it: the keep update (kLast in test mode) or the rebuild"""
        p = self.pg
        p.kLast = None
        p.handleDataEvent(None, None, json.dumps({"a": a}))
        if p.kLast is not None:
            have, miss, _t, nap = walk(p.kLast.getCommands(), self.have)
            self.keepsN += 1
            if miss or nap or self.sigNow() != self.sig or self.sig[0] != 0 or self.sig[1] != 1 or self.sig[3] < 1:
                self.bad.append(("%s: keep after %s on %s (now %s)" % (self.name, a, self.sig, self.sigNow()), miss[:3], nap))
            got = "keep"
        else:
            got = self.open("rebuild after " + a)
        if want is not None:
            self.K.check(got == want, "F %s: click %s -> %s (want %s)" % (self.name, a, got, want))
        return got


def run_flows(out, jar, scratch, _home):
    K = HK.Child(out)
    L, ou, W, p, lv = _world(os.path.join(scratch, "f"), K)
    Page, PFn, Cfg, Isl = L["ShPage"], L["ShPageFn"], L["ShCfg"], L["ShIsl"]
    SHW = "skyy-shard-" + OWNER
    # 1. the Farming portal on the farm island: open -> click -> zoom -> click ... (the flow Skyy hit)
    pg = PFn(FK, 0).make(None, ou, W)
    c = Client(K, pg, "Farming portal")
    c.open("portal open")
    K.check(int(pg.tab) == 1 and int(pg.zoom) == 0 and getattr(pg, "kShown", None) is not None, "F the portal opens the Map tab at 100 %% (kShown %s)" % getattr(pg, "kShown", None))
    c.click("mn0", "full")            # 100 %: a rebuild
    c.click("mhub", "full")
    c.click("mzi", "full")            # 150 %
    K.eq(str(pg.kShown), "v0t1k%dz1" % FK, "F kShown = the 150 % Farming Map page")
    c.click("mn0", "keep")            # the first click after the zoom: in place
    c.click("mn1", "keep")
    c.click("mn0", "keep")
    c.click("isub0", "keep")          # a purchase (Crop Amount) in place
    c.click("mn1", "keep")
    c.click("ibuy", None)             # buy T2 (in place when its picture is pre-placed, else a rebuild)
    c.click("mzi", "full")            # 200 %
    c.click("mhub", "keep")
    c.click("buy", None)              # Storage
    c.click("iauto", None)
    c.click("offbuy", None)
    c.click("mn0", "keep")
    c.click("grow", None)
    c.click("iseed", None)
    c.click("iseedb", None)
    # 2. the rail: Mining (locked, its portal here) and back - every switch rebuilds, the clicks after are safe
    c.click("mk0", "full")
    K.check(int(pg.kind) == MKD, "F the rail switched to Mining")
    c.click("mn0", "keep")            # Mining's own 200 % page: in place
    c.click("mhub", "keep")
    c.click("mk4", "full")            # Orchard's portal is elsewhere: refused, the page redraws (status)
    c.click("mk2", "full")
    c.click("mn0", "keep")
    # 3. tabs: Totems / Collect, a stale Map click while there, back to the Map (zoom kept, a new page = rebuild)
    c.click("tab3", "full")
    c.click("mn0", "full")            # a Map click while the client shows the Totems tab: NEVER in place
    c.click("buy", "full")
    c.click("tab0", "full")
    c.click("mhub", "full")
    c.click("isub0", "full")
    c.click("tab1", "full")
    c.click("mn1", "keep")            # back on the Map at 200 %: in place again
    c.click("mzo", "full")            # 150 %
    c.click("mn0", "keep")
    c.click("mzo", "full")            # 100 %
    c.click("mn1", "full")
    c.click("mhub", "full")
    # 4. state drift: the page state changed without a build -> never in place
    c.click("mzi", "full")
    pg.kShown = None
    c.click("mn0", "full")
    c.click("mn1", "keep")
    pg.tab = 3                        # the tab moved but the client still shows the Map: rebuild (kShown != the page it would update)
    c.click("mn0", "full")
    pg.tab = 1
    c.click("tab1", "full")
    pg.kind = MKD                     # the shard moved without a build
    c.click("mn0", "full")
    c.click("mk2", "full")
    pg.zoom = 2                       # the zoom moved without a build
    c.click("mn0", "full")
    c.click("mn1", "keep")
    Cfg.UI_KEEP = False
    c.click("mn0", "full")
    Cfg.UI_KEEP = True
    c.click("mn1", "keep")            # switched on again: the client still holds that full 200 % Map page (drawn in keep form) -> in place
    c.click("mn0", "keep")
    # 5. the other pages never send a keep update (they have no map)
    for mode, nm in ((0, "exit page"), (1, "totem page"), (2, "bench")):
        q = PFn(FK, mode).make(None, ou, SHW)
        if q is None:
            K.check(False, "F %s opens" % nm)
            continue
        q.near = False
        q.zoom = 2
        c2 = Client(K, q, nm)
        c2.open()
        for a in ("mn0", "mhub", "buy", "isub0", "ibuy", "grow", "iauto", "mzi", "mn1"):
            c2.click(a, "full")
        K.check(c2.keepsN == 0 and not c2.bad, "F %s: %d clicks, no keep update, every page complete: %s" % (nm, c2.fulls, c2.bad[:2]))
    # 6. a co-op member's page + a fresh page for every shard: open -> zoom 200 -> click
    for kd in range(6):
        for u, who in ((ou, "owner"), (L["UUID"].fromString(MEMBER), "co-op")):
            q = PFn(kd, 0).make(None, u, W)
            if q is None:
                continue
            c3 = Client(K, q, "%s %s" % (KINDS[kd], who))
            c3.open()
            c3.click("mn0")
            c3.click("mzi")
            c3.click("mzi")
            c3.click("mn0")
            c3.click("mhub")
            c3.click("mzo")
            c3.click("mn1")
            K.check(not c3.bad, "F %s %s: open -> zoom 200 -> clicks, every packet valid: %s" % (KINDS[kd], who, c3.bad[:2]))
    K.check(not c.bad, "F the Farming flow: %d full pages + %d in-place updates, every selector on the page the client holds: %s" % (c.fulls, c.keepsN, c.bad[:3]))
    K.check(c.keepsN >= 10, "F the in-place update still runs at 150 / 200 %% (%d times)" % c.keepsN)
    Page.TEST_INV = None
    Isl.LEVEL_TEST = None
    K.save()


# ---------------------------------------------------------------------------------------------------------- 0.4.9 phases that read the RUNNING version
# or the LIVE data (0.4.8 + 0.4.9 are deployed now: the live config already carries the ShMig048 / ShMig049 markers)
def run_mig48(out, jar, scratch, home):
    live = os.path.join(T46.LIVE_SH, "config.properties")
    done = os.path.isfile(live) and b"skyyshards-0.4.8-map" in open(live, "rb").read()
    sup = ("M History holds the old bytes",) if done else ()
    T49._superseded(sup, lambda: T48.run_mig(out, jar, os.path.join(scratch, "m48"), home))


def run_players48(out, jar, scratch, home):
    """the map migration's collect.log line names the RUNNING version: 0.4.10 now"""
    T49._superseded(("P one collect.log line with the Undo",), lambda: T48.run_players(out, jar, os.path.join(scratch, "p48"), home))
    d_ = json.load(open(out))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = d_["ok"], d_["fails"], d_["notes"]
    log = os.path.join(scratch, "p48", "p", "x", "collect.log")
    if not os.path.isfile(log):
        log = os.path.join(scratch, "p48", "x", "collect.log")
    txt = open(log, encoding="utf8").read() if os.path.isfile(log) else ""
    K.check("map migration (SkyyShards 0.4.10) 0a0a0a0a-1111-2222-3333-000000000001" in txt and "Undo:" in txt,
            "P the map migration's collect.log line (running version 0.4.10) with the Undo")
    K.save()


def run_live410(out, jar, scratch, home):
    """START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards (0.4.9 live): no migration runs again, every real shard's menu opens
    from its portal world and is walked in order (open -> 150 -> 200 -> island click -> centre), a second start writes nothing"""
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    Cfg, path = T42.kit_home(home)
    Ms = [JClass(PKG + n) for n in ("ShMig044", "ShMig045", "ShMig046", "ShMig048", "ShMig049")]
    St, Isl, Page = JClass(PKG + "ShStore"), JClass(PKG + "ShIsl"), JClass(PKG + "ShPage")
    sd = os.path.join(home, "shards")

    def start():
        T42.kit_home(home)
        rs = tuple([str(Cfg.migCoop(Cfg.FILE))] + [str(m.run(Cfg.FILE)) for m in Ms])
        Cfg.loadCfg(True)
        St.DIR = path(sd)
        St.CACHE.clear()
        keys = [f[:-11] for f in sorted(os.listdir(sd)) if f.endswith(".properties")] if os.path.isdir(sd) else []
        return rs, [(k, St.get(k)) for k in keys]
    t0 = T42.tree(home)
    rs, profs = start()
    K.check(all(r == "" for r in rs), "D start 1: every migration already ran on the live data (0.4.9 deployed) - none runs again: %s" % [r[:80] for r in rs])
    K.check(len(profs) >= 1, "D the real profiles load (%d)" % len(profs))
    Page.TEST_INV = None
    Isl.LEVEL_TEST = None
    n = 0
    for k, p in profs:
        for kd in range(6):
            pl = str(p.getProperty(KINDS[kd].lower() + ".placed") or "")
            if "|" not in pl:
                continue
            pg = Page(JClass("java.util.UUID").fromString(k[:36]), pl.split("|")[0])
            pg.kind = kd
            pg.view = 0
            c = Client(K, pg, "live %s %s" % (k[-6:], KINDS[kd]))
            c.open("portal open")
            for a in ("mn0", "mzi", "mn0", "mzi", "mn0", "mhub", "mn1", "tab3", "tab0", "tab1", "mzo"):
                c.click(a)
            n += 1
            K.check(not c.bad, "D the real %s Shard (%s): open + 11 clicks, every packet valid on the page the client holds (%d in place): %s"
                    % (KINDS[kd], pl.split("|")[0], c.keepsN, c.bad[:2]))
    K.check(n >= 1, "D at least one real placed shard walked (%d)" % n)
    t1 = T42.tree(home)
    rs2, _p2 = start()
    K.check(all(r == "" for r in rs2) and T42.tree(home) == t1, "D start 2: nothing runs, no file changes")
    K.save()


EXPECT = {   # 0.4.9 -> 0.4.10: the version texts (CfgFile / CfgFn / CfgRows, ShStore log lines, the ready line) + the hotfix in ShPage
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],
    "ShPage": ["+f kShown", "+m kShownSig", "~m build", "~m buildFull", "~m kUpd"],
    "ShStore": ["~m migrate", "~m migrate2", "~m save"], "SkyyShardsPlugin": ["~m setup"]}

import zipfile as _zf
_ORIG_COMPARE = T49._ORIG_COMPARE


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit compare allows only manifest.json among the non-class entries: both jars without the (identical) map files"""
    cps = []
    for j, tag in ((jar, VERSION), (old_jar, "old")):
        cp = os.path.join(SCRATCH, "compare-%s.jar" % tag)
        with _zf.ZipFile(j) as zi, _zf.ZipFile(cp, "w", _zf.ZIP_DEFLATED) as zo:
            for n in zi.namelist():
                if not T49.MAP_ENTRY.match(n):
                    zo.writestr(n, zi.read(n))
        cps.append(cp)
    with _zf.ZipFile(jar) as a, _zf.ZipFile(old_jar) as b:
        ma = dict((n, a.read(n)) for n in a.namelist() if T49.MAP_ENTRY.match(n))
        mb = dict((n, b.read(n)) for n in b.namelist() if T49.MAP_ENTRY.match(n))
    assert ma == mb and len(ma) > 100, "C the map pictures + page data differ from 0.4.9"
    print("C. the map pictures + page data are byte-identical to 0.4.9 (%d files)" % len(ma))
    _ORIG_COMPARE(out, cps[0], cps[1], pkg, expect, added, removed)


HK.run_compare = _compare


def _p49(fn):
    return lambda out, jar, scratch, home: fn(out, jar, os.path.join(scratch, "p49"), home)


if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec48", T49.run_exec48), ("exec47", T49.run_exec47), ("exec46", T49.run_exec46), ("centre47", T49.run_centre47),
                   ("config48", T49.run_config48), ("mig48", run_mig48), ("players48", run_players48), ("geo48", T49.run_geo48),
                   ("config", T49.run_config), ("mig", T49.run_mig), ("exec", T49.run_exec), ("page", T49.run_page), ("width", T49.run_width),
                   ("order", run_order), ("flows", run_flows), ("live", run_live410)],
           script=__file__, live=(T46.LIVE_SH, "mods/Skyy_SkyyShards"))
