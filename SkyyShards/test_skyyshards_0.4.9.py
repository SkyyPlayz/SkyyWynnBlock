"""Harness for SkyyShards 0.4.9 (the starter archipelago round R3: the Shard Upgrade Map tab + the shard re-balance: +3 % a sub-upgrade level,
Offline Harvest 0-5, storage keeps its time; tools/shards_0_4_9_patch.py).
Build first:
    python tools/shards_0_4_9_patch.py && python SkyyShards/build_skyyshards_0.4.9.py
    python SkyyShards/test_skyyshards_0.4.9.py [--keep]

  S    static   the patch re-runs to identical bytes; no new registerSystem / registerCommand; ShMig049 + ShMap written; setup order
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.8 -> 0.4.9: exactly the planned members differ (EXPECT)
  48   the 0.4.8 harness phases on the 0.4.9 jar (exec, exec47, exec46, centre47, config, mig, players, geo); checks of behaviour 0.4.9 replaces
       on purpose are kept as notes (superseded: the Islands tab ids, 3 days offline for a NEW shard, the x1.25 maxed island)
  K    config   EXECUTED loadCfg: a fresh file (the 0.4.9 rows + marker, bonus 3), hand edits + junk lists, the Server Setup rows
  M    mig      ShMig049 on a scratch COPY of the live config + a 0.4.8-default file: the 3 lines, History, change log, run twice = once,
                hand-edited lines kept, a fresh 0.4.9 file untouched
  X    exec     EVERY NEW CODE PATH: Offline Harvest (no key = 5 / a new shard 0, offMs at every level, manual 2 h, the ceiling), buyOffline
                (costs = the ladder steps + items, refusals, refunds, max), +3 % a level (x1.000 new, x3.049 maxed), storage x the multiplier
  U    page     the Map tab EXECUTED on the real UICommandBuilder: opens on the Map, rail + map + 3 panel views, every binding, the island
                pictures + lines, the panel texts (shard / island / buy), every click (centre, islands, zoom, rail switch + refusal, every
                purchase button), ONE packet per click: the keep update at 150 / 200 % (sendUpdate builder recorded) and its fall-backs
                (kind switch / structural change / a picture not pre-placed / the switch off), the page data of every shard + zoom
  W    width    every runtime Map text of every shard x tier x size x level fits its label (the client's glyph widths)
  D    live     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards: the migrations once, the real profile's shards = Offline
                Harvest 5 (grandfathered), its Map tab builds for every shard; a second start writes nothing
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, math, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import balance_model as BM

VERSION = "0.4.9"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shard049", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.8.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.8.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_9_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_8", os.path.join(HERE, "test_skyyshards_0.4.8.py"))
T48 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T48)
sys.argv[:] = _argv
T48.JAR = JAR
T47, T46 = T48.T47, T48.T46
T46.JAR = JAR
T47.JAR = JAR
T42 = T46.T42
OWNER, MEMBER = T46.OWNER, T46.MEMBER
KINDS = ["Mining", "Foraging", "Farming", "Ranching", "Orchard", "Combat"]
KK = [k.lower() for k in KINDS]
MKD, FOK, FK, RK, OK_, CK = 0, 1, 2, 3, 4, 5
MIG = [("isl.amount.bonus", "0.5", "3"), ("isl.deco.pct", "0.5", "3"), ("isl.irrigation.pct", "0.5", "3")]
MK = "skyyshards-0.4.9-bonus"
NL_ = chr(10)
OFF_H = [12, 18, 24, 36, 48, 72]
LADDER = [230, 550, 1400, 3400, 6300, 14500, 37000, 105000, 375000, 1260000]
GOOD, BAD, GOLD, TEXT, WARN = "#39f493", "#ff6b6b", "#E8A93B", "#96a9be", "#ffcc00"


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.9 - build script') and g.count('VERSION = "0.4.9"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check("smig48, smig49, st, knd, isl48, lv," in g and "[admc, gfn, dfn, smap, pl]" in g, "S ShMig049 + ShMap written out")
    K.check("STARTER SHARD DOORS" in g and "0.4.9: THE SHARD UPGRADE MAP" in g, "S the ready line names the round")
    HK.jvm([B.SERVER_JAR, JAR, B.JAVASSIST], verify=False)
    calls = T42.setup_calls(jar)
    K.check(calls.index("ShMig048.run") < calls.index("ShMig049.run") < calls.index("ShCfg.loadCfg") < calls.index("CfgPub.start"),
            "S setup order: ShMig048, ShMig049, loadCfg, CfgPub.start")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    import zipfile
    with zipfile.ZipFile(jar) as z:
        names = z.namelist()
    data = [n for n in names if n.startswith("com/skyy/shards/map/") and n.endswith("K.txt")]
    pics = [n for n in names if n.startswith("Common/UI/Custom/SkyyShards/Map/") and n.endswith("@2x.png")]
    K.check(len(data) == 18 and len(pics) > 60 and not [n for n in names if n.lower().endswith(".ui")], "S the jar: %d page data files (6 shards x 3 zooms), %d map pictures, no .ui" % (len(data), len(pics)))
    K.save()


# ---------------------------------------------------------------------------------------------------------- the 0.4.8 phases (superseded notes)
SUP48 = ("X automated: 3 days",                         # 0.4.9: a shard made now starts at Offline Harvest 0 = 12 h (no key = 3 days)
         "X a maxed Large: x",                           # 0.4.9: +3 % a level -> x3.049 (Skyy 2026-10-24: "+2% or more per lvl")
         "X page: the sub-upgrade + Grow buttons bound",  # 0.4.9: the Islands tab is the Map tab (other ids: phase U)
         "X page: the Buy view for T3 Carrot")


def _superseded(sup, fn):
    """run an older harness phase; its checks whose text starts with one of `sup` are behaviour 0.4.9 replaces on purpose (kept as notes)"""
    old_child = HK.Child

    class Sup(old_child):
        def check(self, cond, what):
            if any(str(what).startswith(x) for x in sup):
                self.notes.append("superseded by 0.4.9: " + str(what)[:110])
                return True
            return old_child.check(self, cond, what)
    HK.Child = Sup
    try:
        fn()
    finally:
        HK.Child = old_child


def run_exec48(out, jar, scratch, home):
    _superseded(SUP48, lambda: T48.run_exec(out, jar, os.path.join(scratch, "e48"), home))


def run_exec47(out, jar, scratch, home):
    T48.run_exec47(out, jar, scratch, home)


def run_exec46(out, jar, scratch, home):
    T48.run_exec46(out, jar, scratch, home)


def run_centre47(out, jar, scratch, home):
    T48.run_centre47(out, jar, scratch, home)


def run_config48(out, jar, scratch, home):
    # 0.4.9: isl.deco.pct is 3 in a fresh file now (the 0.4.8 row list said 0.5) - every other 0.4.8 row is checked
    _superseded(("K a fresh file holds every 0.4.8 row",), lambda: T48.run_config(out, jar, os.path.join(scratch, "k48"), home))


def run_mig48(out, jar, scratch, home):
    T48.run_mig(out, jar, os.path.join(scratch, "m48"), home)


def run_players48(out, jar, scratch, home):
    # the map migration's collect.log line names the RUNNING version ("map migration (SkyyShards 0.4.9) <pkey>") - checked here instead
    _superseded(("P one collect.log line with the Undo",), lambda: T48.run_players(out, jar, os.path.join(scratch, "p48"), home))
    d_ = json.load(open(out))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = d_["ok"], d_["fails"], d_["notes"]
    log = os.path.join(scratch, "p48", "p", "x", "collect.log")
    if not os.path.isfile(log):
        log = os.path.join(scratch, "p48", "x", "collect.log")
    txt = open(log, encoding="utf8").read() if os.path.isfile(log) else ""
    K.check("map migration (SkyyShards 0.4.9) 0a0a0a0a-1111-2222-3333-000000000001" in txt and "Undo:" in txt, "P the map migration's collect.log line (running version 0.4.9) with the Undo")
    K.save()


def run_geo48(out, jar, scratch, home):
    T48.run_geo(out, jar, os.path.join(scratch, "g48"), home)


# ---------------------------------------------------------------------------------------------------------- K: config
def run_config(out, jar, scratch, _home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    home = os.path.join(scratch, "k1", "mods", "Skyy_SkyyShards")
    os.makedirs(home)
    Cfg, path = T42.kit_home(home)
    Cfg.loadCfg(True)
    t = open(os.path.join(home, "config.properties"), "rb").read().replace(b"\r\n", b"\n").decode("latin-1")
    lines = t.split("\n")
    want = ["isl.amount.bonus=3", "isl.deco.pct=3", "isl.irrigation.pct=3", "up.offline.hours=12,18,24,36,48,72", "up.offline.steps=3,5,6,7,8",
            "up.offline.ench=1,2,4,8,16", "shard.ui.keepScroll=true", "shard.maxOfflineSec=259200"]
    K.eq([w for w in want if w not in lines], [], "K a fresh file holds every 0.4.9 row")
    K.check(t.count(MK) == 1 and t.count("skyyshards-0.4.8-map") == 1, "K a fresh file carries the 0.4.9 marker (and 0.4.8's)")
    K.check(float(Cfg.AMT_BONUS) == 3.0 and float(Cfg.DECO_PCT) == 3.0 and float(Cfg.IRR_PCT) == 3.0 and [float(x) for x in Cfg.OFF_H] == [float(x) for x in OFF_H]
            and [int(x) for x in Cfg.OFF_STEP] == [3, 5, 6, 7, 8] and [int(x) for x in Cfg.OFF_ENCH] == [1, 2, 4, 8, 16] and bool(Cfg.UI_KEEP), "K the fields read")
    open(os.path.join(home, "config.properties"), "a", encoding="latin-1").write(
        "\nup.offline.hours=1,2,junk\nup.offline.steps=4\nup.offline.ench=0,0,0,0,0,0,0\nshard.ui.keepScroll=false\nisl.deco.pct=200\n")
    Cfg.loadCfg(False)
    K.check([float(x) for x in Cfg.OFF_H] == [float(x) for x in OFF_H] and [int(x) for x in Cfg.OFF_STEP] == [4] * 5 and [int(x) for x in Cfg.OFF_ENCH] == [1, 2, 4, 8, 16]
            and not bool(Cfg.UI_KEEP) and float(Cfg.DECO_PCT) == 100.0,
            "K hand edits: a junk list = the default (+ WARN), one number repeats, 7 numbers = the default, keepScroll off, clamp 100")
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in JClass(PKG + "CfgRows").header()[7])
    K.check(all(x in rows for x in ("up.offline.hours", "up.offline.steps", "up.offline.ench", "shard.ui.keepScroll", "isl.amount.bonus")), "K the Server Setup rows exist")
    K.check(rows["isl.amount.bonus"][4] == "3" and rows["up.offline.hours"][4] == "12,18,24,36,48,72" and rows["shard.ui.keepScroll"][4] == "true",
            "K the rows' defaults: %s / %s / %s" % (rows["isl.amount.bonus"][4], rows["up.offline.hours"][4], rows["shard.ui.keepScroll"][4]))
    K.save()


# ---------------------------------------------------------------------------------------------------------- M: ShMig049
def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    Mig = JClass(PKG + "ShMig049")
    nf = [0]

    def world(b_):
        nf[0] += 1
        home = os.path.join(scratch, "m%d" % nf[0], "mods", "Skyy_SkyyShards")
        os.makedirs(home)
        Cfg, path = T42.kit_home(home)
        f = os.path.join(home, "config.properties")
        if b_ is not None:
            open(f, "wb").write(b_)
        return home, f, Cfg, path

    def props(b_):
        P_ = JClass("java.util.Properties")()
        P_.load(JClass("java.io.ByteArrayInputStream")(b_))
        return dict((str(k), str(P_.getProperty(k))) for k in P_.stringPropertyNames())

    def hist(home):
        hd = os.path.join(home, "config-history")
        return [open(os.path.join(hd, n), "rb").read() for n in sorted(os.listdir(hd)) if n.endswith(".bak")] if os.path.isdir(hd) else []

    def chg(home):
        f = os.path.join(home, "config-changes.log")
        return [l.split("\t") for l in open(f, encoding="utf8").read().splitlines()] if os.path.isfile(f) else []
    live = os.path.join(T46.LIVE_SH, "config.properties")
    A_ = open(live, "rb").read() if os.path.isfile(live) else None
    K.check(A_ is not None, "M the live NewBetaTest config.properties exists (read only)")
    if A_ is not None:
        home, f, Cfg, path = world(A_)
        r = str(Mig.run(path(f)))
        b1 = open(f, "rb").read()
        pa, pb = props(A_), props(b1)
        moved = [k for k, o, w in MIG if pa.get(k) is not None and pa.get(k).replace(" ", "") == o]
        K.check(all(pb[k] == dict((x[0], x[2]) for x in MIG)[k] for k in moved) and all(pb[k] == pa[k] for k in pa if k not in moved) and len(pb) == len(pa),
                "M the live config: %d lines on their old default moved (%s), every other line the same: %s" % (len(moved), moved, r[:200]))
        K.check(b1.count(MK.encode()) == 1 and (b"\r\n" in A_) == (b"\r\n" in b1), "M the marker once, line endings kept")
        r2 = str(Mig.run(path(f)))
        K.check(r2 == "" and open(f, "rb").read() == b1, "M run twice = once (the marker)")
    # a 0.4.8-default file (CRLF) with one hand edit and a spaced line
    old = "".join("%s=%s\r\n" % (k, o) for k, o, w in MIG).replace("isl.deco.pct=0.5", "isl.deco.pct=1").replace("isl.irrigation.pct=0.5", "isl.irrigation.pct = 0.50")
    old = "# keep me\r\nshard.on=true\r\n" + old
    home, f, Cfg, path = world(old.encode("latin-1"))
    r = str(Mig.run(path(f)))
    b2 = open(f, "rb").read()
    p2 = props(b2)
    K.check(p2["isl.amount.bonus"] == "3" and p2["isl.deco.pct"] == "1" and p2["isl.irrigation.pct"] == "3" and "kept - an admin changed it" in r
            and b"\r\n" in b2 and b"\n" not in b2.replace(b"\r\n", b"") and b2.startswith(b"# keep me\r\nshard.on=true\r\n"),
            "M hand-edited isl.deco.pct=1 kept (INFO), a spaced 0.50 still matched, CRLF + every other byte kept: %s" % r[-160:])
    K.check(any(h == old.encode("latin-1") for h in hist(home)) and len([c for c in chg(home) if len(c) > 6 and c[1] == "SkyyShards 0.4.9"]) == 2,
            "M History holds the old bytes, one change-log line per moved line (2)")
    Cfg.loadCfg(False)
    K.check(float(Cfg.AMT_BONUS) == 3.0 and float(Cfg.DECO_PCT) == 1.0, "M loadCfg after the update: 3 / the kept 1")
    home, f, Cfg, path = world(None)
    Cfg.loadCfg(True)
    b0 = open(f, "rb").read()
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == b0, "M a fresh 0.4.9 file: nothing to do (its marker)")
    home, f, Cfg, path = world(b"shard.on=true\n")
    r = str(Mig.run(path(f)))
    K.check("no setting line held the old default" in r and open(f, "rb").read().count(MK.encode()) == 1, "M a file without the rows: only the marker (missing = the new built-in 3)")
    K.save()


# ---------------------------------------------------------------------------------------------------------- the shared fixture
def _setup(scratch, K):
    L = T48._setup(scratch, K)
    from jpype import JClass
    for n in ("ShMap", "ShMig049"):
        L[n] = JClass(PKG + n)
    return L


def _build(pg):
    """build the page on the real UICommandBuilder: appended markup, the sets (selector -> value), the bindings (selector -> data), the size"""
    from jpype import JClass
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    CPk = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPage")
    LIFE = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime")
    b, ev = UCB(), UEB()
    pg.build(None, b, ev, None)
    return _cmds(b, ev, CPk, LIFE)


def _cmds(b, ev=None, CPk=None, LIFE=None):
    appended, sets = [], {}
    cmds = b.getCommands()
    for c in cmds:
        t_ = str(c.type)
        if "Append" in t_:
            appended.append(str(c.text) if c.text is not None else "")
        if c.selector is not None and c.data is not None and "Set" in t_:
            v_ = str(c.data)
            try:
                j_ = json.loads(v_)
                v_ = j_.get("0", j_) if isinstance(j_, dict) else j_
            except Exception:
                pass
            sets[str(c.selector)] = v_
    datas = {}
    size = 0
    if ev is not None:
        for e in ev.getEvents():
            try:
                datas[str(e.selector)] = str(e.data)
            except Exception:
                datas[str(e.selector)] = str(e)
        if CPk is not None:
            size = int(CPk("SkyySh", True, True, LIFE.CanDismiss, cmds, ev.getEvents()).computeSize())
    return dict(mk="\n".join(appended), sets=sets, datas=datas, binds=list(datas), size=size, n=len(cmds))


def _act(datas, sel):
    d = datas.get(sel, "")
    i = d.find('"a"')
    if i < 0:
        return None
    j = d.find('"', d.find(":", i) + 1)
    return d[j + 1:d.find('"', j + 1)]


# ---------------------------------------------------------------------------------------------------------- X: Offline Harvest, the bonus, storage
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JInt, JString, JArray, JObject
    K = HK.Child(out)
    L = _setup(os.path.join(scratch, "x"), K)
    St, Isl, Mth, Core, Door, Cfg, Tot = (L[n] for n in ("ShStore", "ShIsl", "ShMath", "ShCore", "ShDoor", "ShCfg", "ShTotem"))
    inv, count, UUID, coins, PyFn = (L[n] for n in ("inv", "count", "UUID", "coins", "PyFn"))
    ou = UUID.fromString(OWNER)
    W = "skyy-island-" + OWNER
    now = 1790000000000
    Core.NOW_TEST = now
    Isl.LEVEL_TEST = PyFn(lambda a: JInt(9))
    r = str(Door.door(ou, OWNER, "farming", W, 29, 129, -31))
    p = St.get(OWNER)
    g = lambda key: str(p.getProperty(key)) if p.getProperty(key) is not None else None
    K.check(r == "+" and g("farming.offline") == "0" and int(Isl.offLv(FK, p)) == 0, "X a NEW shard (the door's T1 island): Offline Harvest 0 written with the island")
    # ---- no key = a shard owned before 0.4.9 = level 5 (the old 3 days)
    p.setProperty("mining.i0.type", "copper"); p.setProperty("mining.i0.size", "1"); p.setProperty("mining.i0.last", str(now)); p.setProperty("mining.auto", "1")
    K.check(int(Isl.offLv(MKD, p)) == 5 and int(Isl.offMs(MKD, p)) == 259200000, "X no key (owned before 0.4.9): level 5 = 3 days, nothing lost")
    # ---- offMs: Automated = the level's hours, the server ceiling, manual = 2 h
    got = []
    p.setProperty("farming.auto", "1")
    for lv in range(6):
        p.setProperty("farming.offline", str(lv))
        got.append(int(Isl.offMs(FK, p)) // 3600000)
    K.eq(got, OFF_H, "X Automated: Offline Harvest 0..5 = 12 / 18 / 24 / 36 / 48 / 72 h")
    Cfg.MAX_OFF_SEC = 86400
    K.check(int(Isl.offMs(FK, p)) == 86400000, "X shard.maxOfflineSec 1 day is the ceiling over level 5")
    Cfg.MAX_OFF_SEC = 259200
    p.remove("farming.auto")
    p.setProperty("farming.offline", "3")
    K.check(int(Isl.offMs(FK, p)) == 7200000, "X manual phase: shard.manualOfflineSec 2 h still applies")
    p.setProperty("farming.offline", "0")
    Cfg.MAN_OFF_SEC = 100000
    K.check(int(Isl.offMs(FK, p)) == 12 * 3600000, "X manual with a long manualOfflineSec: the level's 12 h caps it")
    Cfg.MAN_OFF_SEC = 7200
    p.setProperty("farming.offline", "junk")
    K.check(int(Isl.offLv(FK, p)) == 0, "X a junk level reads 0")
    p.setProperty("farming.offline", "0")
    # ---- settle honours the cap: 30 h away at level 0 (Automated) = 12 h of items
    p.setProperty("farming.auto", "1")
    p.setProperty("farming.i0.stored", "0"); p.setProperty("farming.i0.last", str(now - 30 * 3600000))
    made = int(Mth.settle(FK, p, 0, now))
    rt = float(Mth.rate(FK, p, 0, now))
    K.check(abs(made - math.floor(12 * 60 * rt)) <= 1, "X settle after 30 h at level 0: %d items = 12 h at %.3f / min" % (made, rt))
    # ---- buyOffline: level 0 -> 1 = ladder step 3 (1,400) + 1 Enchanted Wheat; refusals; level 5 max
    cs = inv(27, 27)
    coins["bal"] = 2000000
    b0 = coins["bal"]
    p.setProperty("farming.auto", "0")
    T48._fill(L, cs, [("Skyy_Ench_Wheat", 5)])
    r = str(Core.buyOffline(ou, OWNER, FK, cs))
    K.check(r.startswith("-Buy Automation first") and coins["bal"] == b0 and count(cs, "Skyy_Ench_Wheat") == 5 and g("farming.offline") == "0",
            "FIX3 before Automation: Offline Harvest refused, nothing taken: %s" % r)
    p.setProperty("farming.auto", "1")
    cs = inv(27, 27)
    r = str(Core.buyOffline(ou, OWNER, FK, cs))
    K.check(r.startswith("-You need 1 Enchanted Wheat") and coins["bal"] == b0 and g("farming.offline") == "0", "X no Enchanted Wheat: refused, nothing taken: %s" % r)
    T48._fill(L, cs, [("Skyy_Ench_Wheat", 40)])
    coins["fail"] = True
    r = str(Core.buyOffline(ou, OWNER, FK, cs))
    coins["fail"] = False
    K.check(r.startswith("-The coins could not be taken") and count(cs, "Skyy_Ench_Wheat") == 40 and g("farming.offline") == "0", "X coins refused: the items are back")
    St.FAIL_TEST = True
    r = str(Core.buyOffline(ou, OWNER, FK, cs))
    St.FAIL_TEST = False
    K.check(r.startswith("-It could not be saved") and count(cs, "Skyy_Ench_Wheat") == 40 and coins["bal"] == b0 and g("farming.offline") == "0", "X a refused save: items + coins back")
    paid = []
    for want in range(1, 6):
        b_ = coins["bal"]
        e_ = count(cs, "Skyy_Ench_Wheat")
        r = str(Core.buyOffline(ou, OWNER, FK, cs))
        paid.append((b_ - coins["bal"], e_ - count(cs, "Skyy_Ench_Wheat")))
        K.check(r.startswith("+Offline Harvest %d/5" % want) and g("farming.offline") == str(want), "X buy level %d: %s" % (want, r))
    K.eq(paid, [(1400, 1), (6300, 2), (14500, 4), (37000, 8), (105000, 16)], "X the five levels cost the ladder steps 3 / 5 / 6 / 7 / 8 + 1 / 2 / 4 / 8 / 16 Enchanted Wheat")
    K.check(str(Core.buyOffline(ou, OWNER, FK, cs)).startswith("=Offline Harvest is at its highest level"), "X level 5: '='")
    # fix 2: the Storage buy message names the base a NEW island holds (the file is put back after)
    _snap = dict((str(k_), str(p.getProperty(k_))) for k_ in p.stringPropertyNames())
    r = str(Core.buyStorage(ou, OWNER, FK, cs))
    K.check(r.startswith("+Storage is now tier 2") and r.endswith(" items a new island (more with island upgrades)."), "FIX2 the Storage buy message: %s" % r)
    p.clear()
    for k_, v_ in _snap.items():
        p.setProperty(k_, v_)
    K.check(abs(float(BM.p11_cost(BM.P11_UP_H[2], BM.P11_UP_LV[2])) - 1400) < 1, "X tools/balance_model.py --p11 prices the same step")
    # a co-op member / a locked shard / another profile: gateOwn refuses
    mu = UUID.fromString(MEMBER)
    p.setProperty("mining.offline", "0")
    K.check(str(Core.buyOffline(mu, OWNER, MKD, cs)).startswith("-"), "X a co-op member cannot buy Offline Harvest")
    Isl.LEVEL_TEST = PyFn(lambda a: JInt(1))
    K.check("locked" in str(Core.buyOffline(ou, OWNER, MKD, cs)), "X a locked shard refuses (the door lock)")
    Isl.LEVEL_TEST = PyFn(lambda a: JInt(9))
    # ---- +3 % a level: a new island x1.000, a maxed Large x1.45^3
    p.setProperty("farming.i0.size", "1")
    for f_ in ("amt", "deco", "irr"):
        p.setProperty("farming.i0." + f_, "0")
    K.check(abs(float(Isl.mult(FK, p, 0, 1)) - 1.0) < 1e-12, "X a new island: x1.000 (today's output - Skyy: new islands stay the same)")
    p.setProperty("farming.i0.amt", "1")
    K.check(abs(float(Isl.mult(FK, p, 0, 1)) - 1.03) < 1e-12, "X one Amount level: +3 %")
    p.setProperty("farming.i0.size", "3")
    for f_ in ("amt", "deco", "irr"):
        p.setProperty("farming.i0." + f_, "5")
    mx = float(Isl.mult(FK, p, 0, 3))
    K.check(abs(mx - 1.45 ** 3) < 1e-9 and abs(mx - BM.p11_mult(3, 5, 5, 5)) < 1e-9, "X a maxed Large: x%.4f = 1.45^3 = balance_model --p11" % mx)
    # ---- storage keeps its time: capOf x the island's multiplier (never less)
    c0 = int(Mth.cap(FK, p))
    K.check(int(Mth.capOf(FK, p, 0)) == int(math.floor(c0 * mx)) and int(Mth.capOf(FK, p, 5)) == c0, "X storage: a maxed Large holds x%.3f (%d of %d); an empty slot the plain cap" % (mx, int(Mth.capOf(FK, p, 0)), c0))
    for f_ in ("amt", "deco", "irr"):
        p.setProperty("farming.i0." + f_, "0")
    p.setProperty("farming.i0.size", "1")
    K.check(int(Mth.capOf(FK, p, 0)) == c0, "X a new island: the 0.4.8 storage exactly")
    K.save()


# ---------------------------------------------------------------------------------------------------------- U: the Map tab
def run_page(out, jar, scratch, _home):
    from jpype import JClass, JInt, JString, JArray, JObject
    K = HK.Child(out)
    L = _setup(os.path.join(scratch, "u"), K)
    St, Isl, Mth, Core, Door, Cfg, Page, Map, Role = (L[n] for n in ("ShStore", "ShIsl", "ShMath", "ShCore", "ShDoor", "ShCfg", "ShPage", "ShMap", "ShRole"))
    inv, count, UUID, coins, PyFn = (L[n] for n in ("inv", "count", "UUID", "coins", "PyFn"))
    ou = UUID.fromString(OWNER)
    W = "skyy-island-" + OWNER
    now = 1790000000000
    Core.NOW_TEST = now
    lv = {"Farming": 9, "Mining": 2, "Orchard": 9, "Foraging": 9, "Ranching": 9}
    Isl.LEVEL_TEST = PyFn(lambda a: JInt(lv[str(a[2])]) if str(a[2]) in lv else JInt(-1))
    for kk_, xyz in (("farming", (29, 129, -31)), ("mining", (-43, 124, 4))):
        Door.door(ou, OWNER, kk_, W, xyz[0], xyz[1], xyz[2])
    p = St.get(OWNER)
    St.LOCK.lock()
    try:
        Mth.starter(OK_, p, L["JLong"](now))
        p.setProperty("orchard.placed", "skyy-island-elsewhere|1|2|3")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    S = dict((str(n), i) for i, n in enumerate(Page.SLOT_NAME))
    cs = inv(27, 27, 9)
    coins["bal"] = 100000
    T48._fill(L, cs, [("Plant_Crop_Lettuce_Item", 130), ("Plant_Seeds_Lettuce", 40), ("Plant_Crop_Wheat_Item", 600), ("Skyy_Ench_Wheat", 60),
                      ("Wood_Oak_Trunk", 300), ("Rock_Stone_Cobble", 300), ("Ingredient_Water_Essence", 60), ("Ingredient_Void_Essence", 40)])
    Page.TEST_INV = cs
    pg = Page(ou, W)
    pg.kind = FK
    pg.view = 0
    K.check(int(pg.tab) == 1 and int(pg.mview) == 0 and int(pg.zoom) == 0, "U a new menu opens on the Map tab, the shard view, 100 %")
    bd = _build(pg)
    mk, sets, datas = bd["mk"], bd["sets"], bd["datas"]
    K.check("Group #SkyyShMCv {" in mk and "SkyyShMOut" not in mk and "Group #SkyyShMRail {" in mk,
            "U 100 %: rail + canvas (no scroll box) + panel drawn")
    want = dict([("#SkyyShMHubB", "mhub"), ("#SkyyShMZmO", "mzo"), ("#SkyyShMZmI", "mzi"), ("#SkyyShTab1", "tab1"), ("#SkyyShTab3", "tab3"), ("#SkyyShTab0", "tab0"),
                 ("#SkyyShMBAuto", "iauto"), ("#SkyyShMBStore", "buy"), ("#SkyyShMBComp", "cmpbuy"), ("#SkyyShMBTime", "tcbuy"), ("#SkyyShMBOff", "offbuy"),
                 ("#SkyyShMBSz", "grow"), ("#SkyyShMBU0", "isub0"), ("#SkyyShMBU1", "isub1"), ("#SkyyShMBU2", "isub2"), ("#SkyyShMBSd", "iseed"),
                 ("#SkyyShMBSdB", "iseedb"), ("#SkyyShMBBuy", "ibuy"), ("#SkyyShEnter", "enter")]
                + [("#SkyyShMRk%d" % k, "mk%d" % k) for k in range(6)] + [("#SkyyShMN%dB" % i, "mn%d" % i) for i in range(15)])
    bad = [(s_, _act(datas, s_), a_) for s_, a_ in want.items() if _act(datas, s_) != a_]
    K.check(not bad, "U every map binding is there with its action (%d): %s" % (len(want), bad[:4]))
    unb = [s_ for s_ in datas if (s_.lstrip("#") + " {") not in mk]
    K.check(not unb, "U every binding's element is drawn: %s" % unb[:4])
    tex = [str(x) for x in pg.mTex]
    K.check(tex[0] == "Cf0d060S1" and tex[1] in ("Ready", "Open") and tex[2:] == ["Locked"] * 13 and len(tex) == 15,
            "U the Farming map: T1 Wheat yours Small, T2 Lettuce the next one (%s), the rest locked" % tex[1])
    K.check(('"SkyyShards/Map/Node/Cf0d060S1.png"' in mk) and ('"SkyyShards/Map/Node/%s.png"' % tex[1]) in mk and mk.count('"SkyyShards/Map/Node/Locked.png"') >= 13,
            "U the island pictures are drawn by the keep map")
    lit = [bool(x) for x in pg.mLit]
    K.check(lit[0] and not any(lit[1:]) and len(lit) == 15, "U one gold line (hub -> the T1 island)")
    K.check(int(pg.mV) == 0 and sets.get("#SkyyShMV0.Visible") is True and sets.get("#SkyyShMV1.Visible") is False and sets.get("#SkyyShMV2.Visible") is False,
            "U the shard view shows (the other two views hidden)")
    tx = lambda n: str(pg.mTx[S[n]])
    co = lambda n: str(pg.mCol[S[n]]).lower()
    K.check(tx("V0Nm") == "Farming Shard" and tx("V0Sb").startswith("1 island - 0 at Large") and tx("RAutoN") == "Automation" and tx("RAutoA").startswith("Manual now (50 %)")
            and tx("RAutoC") == "550 coins (you have 100,000)" and co("RAutoC") == GOOD.lower() and tx("RAutoI").startswith("128 Wheat (you have"),
            "U shard view: head + Automation (550 coins + 128 Wheat, green): %s / %s / %s" % (tx("V0Sb"), tx("RAutoC"), tx("RAutoI")))
    K.check(tx("ROffN") == "Offline Harvest 0 of 5" and tx("ROffA").startswith("Manual: 2 h (Automation: 12 h) -> next 18 h") and tx("ROffC") == "Buy Automation first"
            and co("ROffC") == BAD.lower() and tx("ROffI") == "" and not bool(pg.mOn[4]) and sets.get("#SkyyShMBOff.Visible") is False,
            "FIX3 shard view before Automation: Offline Harvest 0 -> 1 says red 'Buy Automation first', no button: %s / %s / %s" % (tx("ROffA"), tx("ROffC"), tx("ROffI")))
    K.check(tx("RStoreN") == "Storage I of V" and tx("RStoreA").startswith("Now ") and tx("RTimeN") == "Time Compressor 0 of 3" and tx("RCompN") == "Auto-Compactor 0 of 2",
            "U shard view: Storage / Time Compressor / Auto-Compactor rows")
    K.check(all(bool(pg.mOn[i]) for i in range(4)) and sets.get("#SkyyShMBStore.Visible") is True and sets.get("#SkyyShMBBuy.Visible") is False,
            "U the owner's four shard buttons show (Offline waits for Automation); the island buttons are hidden")
    # fix 2: the Storage line names the base a NEW island holds
    K.check(tx("RStoreA").endswith(" a new island"), "FIX2 the Storage line says 'a new island' (the base before island upgrades): %s" % tx("RStoreA"))
    # fix 1: the Totem modifiers block (read-only): the bench tier, none placed, then placed + in the bag
    K.check(tx("V0Md") == "Totem modifiers - Totem Bench I of IV" and tx("V0Nt").startswith("None on your totems yet. Craft them and tier up totems at the Totem Bench"),
            "FIX1 the shard view's modifiers block: %s / %s" % (tx("V0Md"), tx("V0Nt")))
    _tot0 = p.getProperty("farming.i0.totems")
    p.setProperty("farming.i0.totems", "harvest_spirit:1:wider:faster:0:fixmod1,harvest_spirit:1:wider::0:fixmod2")
    T48._fill(L, cs, [("Skyy_TotemMod_Compost", 3)])
    pg.fill(OWNER, cs)
    K.check(tx("V0Nt").startswith("On your totems: Wider Area x2, Faster x1 - 3 more in your bag. Craft them"),
            "FIX1 placed modifiers counted per kind + the bag: %s" % tx("V0Nt"))
    if _tot0 is None:
        p.remove("farming.i0.totems")
    else:
        p.setProperty("farming.i0.totems", _tot0)
    pg.fill(OWNER, cs)
    K.check(sets.get("#SkyyShMRk2S.Text", "").startswith("Farming 9 - 1 island") and sets.get("#SkyyShMRk0S.Text") == "Locked - Mining 5"
            and sets.get("#SkyyShMRk4S.Text") == "1 island - portal elsewhere" and sets.get("#SkyyShMRk1S.Text") == "No shard yet",
            "U the rail: Farming 9 - 1 island / red Locked - Mining 5 / Orchard elsewhere / no Foraging shard: %s" % [sets.get("#SkyyShMRk%dS.Text" % k) for k in range(6)])
    K.check(str(pg.railCol[0]).lower() == BAD.lower(), "U a locked shard's rail line is red")
    K.check(bd["size"] < 1500000 and int(pg.mapEls) > 60, "U packet size %d, map elements %d" % (bd["size"], int(pg.mapEls)))
    # ---- clicks: an island to buy (T2), my island (T1), the centre
    K.eq(str(pg.act("mn1", None, None)), "", "U click T2: no status line")
    pg.fill(OWNER, cs)
    K.check(int(pg.mview) == 1 and int(pg.sel) == 1 and int(pg.mV) == 2 and tx("V2Nm") == "T2 Lettuce Island" and tx("V2R0") == "3,500 coins (you have 100,000)"
            and tx("V2R1") == "128 Lettuce (you have 130)" and tx("V2R2") == "32 Lettuce Seeds (you have 40)" and tx("V2Sb").startswith("Next in line") and bool(pg.mOn[len(pg.mOn) - 1]),
            "U the buy view of T2: 3,500 coins + 128 Lettuce + 32 seeds (green), Buy island shown: %s" % [tx("V2R%d" % i) for i in range(3)])
    pg.act("mn2", None, None)
    pg.fill(OWNER, cs)
    K.check(int(pg.mV) == 2 and "Buy the T2 Lettuce island first" in tx("V2G") and co("V2G") == BAD.lower() and not bool(pg.mOn[len(pg.mOn) - 1]),
            "U T3 Carrot: red 'Buy the T2 Lettuce island first', no Buy button: %s" % tx("V2G"))
    pg.act("mn0", None, None)
    pg.fill(OWNER, cs)
    K.check(int(pg.mV) == 1 and tx("V1Nm") == "T1 Wheat Island" and tx("V1Sb").startswith("Small (13 x 13) - Manual phase") and tx("RSzN") == "Size: Small"
            and tx("RSzA") == "Grow: max the 3 below first (0/5, 0/5, 0/5)" and co("RSzA") == BAD.lower() and tx("RU0N") == "Crop Amount 0/5"
            and tx("RU0A") == "Next: +3 % output - 60 -> 68 % of spots" and tx("RU1A") == "Next: +3 % output - adds flowers" and tx("RU2A") == "Next: +3 % output - adds a water pool"
            and tx("RU0C") == "40 coins (you have 100,000)" and tx("RU0I").startswith("16 Wheat"), "U the island view of T1: size, the grow gate, 3 subs at +3 %%: %s / %s / %s"
            % (tx("RU0A"), tx("RU1A"), tx("RU0I")))
    K.check(int(pg.mPip[0]) == 1 and [int(pg.mPip[i]) for i in (1, 2, 3)] == [0, 0, 0] and tx("SdA").startswith("Seed store: 0 Wheat Seeds - 8 Eternal cells"),
            "U pips: Small = 1 of 3, the subs 0/5; the seed store line")
    # ---- purchases from the panel (the 0.4.8 actions): sub-upgrade, buy T2, Automation, Offline Harvest
    r = str(pg.act("isub1", None, None))
    K.check(r.startswith("+Decorations 1/5") and str(p.getProperty("farming.i0.deco")) == "1", "U the Decorations button: %s" % r)
    pg.act("mn1", None, None)
    r = str(pg.act("ibuy", None, None))
    K.check(r.startswith("+The T2 Lettuce island is yours") and int(Isl.slotOf(FK, p, int(Isl.LAD0[FK]) + 1)) >= 0, "U Buy island from the buy view: %s" % r)
    pg.fill(OWNER, cs)
    K.check(int(pg.mV) == 1 and str(pg.mTex[1]) == "Cf0d060S1" and bool(pg.mLit[1]), "U T2 is mine now: its picture + its gold line, the island view")
    r = str(pg.act("iauto", None, None))
    K.check(r.startswith("+Automation!"), "U the Automation button: %s" % r)
    r = str(pg.act("offbuy", None, None))
    K.check(r.startswith("+Offline Harvest 1/5") and str(p.getProperty("farming.offline")) == "1", "U the Offline Harvest button: %s" % r)
    pg.act("mhub", None, None)
    pg.fill(OWNER, cs)
    K.check(int(pg.mview) == 0 and int(pg.mV) == 0 and tx("RAutoA").startswith("Automated") and co("RAutoA") == GOOD.lower() and not bool(pg.mOn[0])
            and tx("ROffA") == "Harvests 18 h -> next 24 h" and tx("ROffN") == "Offline Harvest 1 of 5", "U the centre again: Automated (no button), Offline 1: %s" % tx("ROffA"))
    # ---- the rail: switch to Mining (its portal is here; locked = look, don't touch), Orchard refused (portal elsewhere)
    r = str(pg.act("mk4", None, None))
    K.check(r.startswith("-Open the Orchard Shard from its own portal") and int(pg.kind) == FK, "U rail: Orchard's portal is elsewhere - refused, the menu stays: %s" % r)
    r = str(pg.act("mk0", None, None))
    bd = _build(pg)
    K.check(r == "" and int(pg.kind) == MKD and bool(pg.locked) and not any(bool(pg.mOn[i]) for i in range(len(pg.mOn))) and str(pg.mTex[0]) == "C8fc8ffS1"
            and len(list(pg.mTex)) == 11 and "Locked - reach Mining 5" in tx("V0Sb") and _act(bd["datas"], "#SkyyShMN10B") == "mn10" and "#SkyyShMN11B" not in bd["datas"],
            "U rail: Mining (portal here) opens - 11 islands, locked: no buttons, the lock line: %s" % tx("V0Sb"))
    K.check(str(pg.act("offbuy", None, None)).startswith("-Mining Shard - locked"), "U a locked shard's purchase is refused anyway (the click re-checks)")
    pg.act("mk2", None, None)
    # ---- zoom + THE KEEP UPDATE: at 200 % a click answers with one sendUpdate (recorded in test mode), the view never rebuilt
    pg.act("mzi", None, None)
    pg.act("mzi", None, None)
    pg.act("mzi", None, None)
    K.eq(int(pg.zoom), 2, "U zoom in stops at 200 %")
    bd = _build(pg)
    K.check("Group #SkyyShMOut" in bd["mk"] and pg.kst is not None and int(pg.kZ) == 2 and bd["sets"].get("#SkyyShMZmL.Text") == "200 %",
            "U 200 %: the 2-axis scroll box, keep state drawn, the zoom label")
    k0 = int(pg.keeps)
    pg.kLast = None
    pg.handleDataEvent(None, None, '{"a":"mn0"}')
    kb = _cmds(pg.kLast) if pg.kLast is not None else None
    K.check(kb is not None and int(pg.keeps) == k0 + 1 and kb["sets"].get("#SkyyShMV1.Visible") is True and kb["sets"].get("#SkyyShMV0.Visible") is False
            and kb["n"] < 900 and "" == kb["mk"], "U keep: click T1 at 200 %% = ONE update (%s commands, no append): the island view shows" % (kb and kb["n"]))
    K.check(kb is not None and any("SkyyShMSel" in s_ for s_ in kb["sets"]), "U keep: the halo moved (its Anchor / Visible): %s" % (kb and [s_ for s_ in kb["sets"] if "Sel" in s_]))
    pg.kLast = None
    pg.handleDataEvent(None, None, '{"a":"isub0"}')
    kb = _cmds(pg.kLast) if pg.kLast is not None else None
    K.check(kb is not None and int(pg.keeps) == k0 + 2 and str(p.getProperty("farming.i0.amt")) == "1" and kb["sets"].get("#SkyyShStatus0.Visible") is True
            and kb["sets"].get("#SkyyShStatus0.Text", "").startswith("Crop Amount 1/5"), "U keep: a purchase at 200 %% = one update: the status line green + texts: %s" % (kb and kb["sets"].get("#SkyyShStatus0.Text")))
    # buy T3 Carrot at 200 %: a picture change (Ready/Open -> mine) that is pre-placed (cand) -> still in place
    T48._fill(L, cs, [("Plant_Crop_Carrot_Item", 130), ("Plant_Seeds_Carrot", 40)])
    coins["bal"] = 200000
    pg.handleDataEvent(None, None, '{"a":"mn2"}')
    pg.kLast = None
    pg.handleDataEvent(None, None, '{"a":"ibuy"}')
    kb = _cmds(pg.kLast) if pg.kLast is not None else None
    K.check(kb is not None and int(Isl.slotOf(FK, p, int(Isl.LAD0[FK]) + 2)) >= 0 and any(k_.startswith("#SkyyShMN2") and k_.endswith(".Visible") for k_ in kb["sets"])
            and any(k_.startswith("#SkyyShME") and k_.endswith(".Visible") for k_ in kb["sets"]), "U keep: buying T3 swaps its picture + lights its line in place")
    # fall-backs: the rail switch (not keepable), a structural change (the lock), a picture that is not pre-placed, the switch off, 100 %
    f0 = int(pg.kFalls)
    lv["Farming"] = 1
    pg.kLast = None
    pg.handleDataEvent(None, None, '{"a":"mhub"}')
    K.check(pg.kLast is None and int(pg.kFalls) == f0 + 1, "U keep fall-back: the shard became locked (kSig) -> a rebuild, no update")
    lv["Farming"] = 9
    _build(pg)
    tex2 = list(str(x) for x in pg.mTex)
    tex2[5] = "Cf0d060Done"
    from jpype import JArray as _JA, JString as _JS
    ub = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    K.check(not bool(Map.mapUpdK(ub, pg.kst, _JA(_JS)(tex2), pg.mLit, -1)) and len(ub.getCommands()) == 0, "U keep fall-back: a picture that is not pre-placed -> false, nothing added")
    Cfg.UI_KEEP = False
    pg.kLast = None
    pg.handleDataEvent(None, None, '{"a":"mn1"}')
    K.check(pg.kLast is None, "U shard.ui.keepScroll off: every click redraws")
    Cfg.UI_KEEP = True
    pg.act("mzo", None, None); pg.act("mzo", None, None)
    _build(pg)
    pg.kLast = None
    pg.handleDataEvent(None, None, '{"a":"mn0"}')
    K.check(pg.kLast is None and int(pg.zoom) == 0, "U at 100 % a click rebuilds (nothing scrolls there)")
    # ---- tabs: Totems / Collect still build; the old Islands tab number shows the Map; the co-op view; Combat (1 island)
    for t_, txt_ in ((3, "SkyyShTHead"), (0, "SkyyShCHead")):
        pg.tab = t_
        bdt = _build(pg)
        K.check(("#%s {" % txt_) in bdt["mk"] and "SkyyShMCv" not in bdt["mk"] and _act(bdt["datas"], "#SkyyShTab1") == "tab1", "U tab %d builds (Map tab button bound)" % t_)
    pg.act("tab2", None, None)
    _build(pg)
    K.eq(int(pg.tab), 1, "U the old Islands tab number shows the Map")
    mp_ = Page(UUID.fromString(MEMBER), W)
    mp_.kind = FK
    bdm = _build(mp_)
    K.check(not any(bool(mp_.mOn[i]) for i in range(len(mp_.mOn))) and "#SkyyShMHubB" in bdm["datas"], "U a co-op member sees the map, no purchase button")
    # every shard's page data reads + draws at every zoom (all 18 files)
    for kd in range(6):
        for z in range(3):
            n = len(list(Map.linesK(kd, z)))
            K.check(n > 10, "U page data K%dZ%d: %d lines" % (kd, z, n))
    K.check(int(Map.READS.get()) >= 18, "U the 18 page data files were read (cached once)")
    Page.TEST_INV = None
    Isl.LEVEL_TEST = None
    K.save()


# ---------------------------------------------------------------------------------------------------------- W: every runtime text fits its label
def run_width(out, jar, scratch, _home):
    from jpype import JClass, JInt
    import skyyui as SUI
    K = HK.Child(out)
    L = _setup(os.path.join(scratch, "w"), K)
    St, Isl, Mth, Core, Door, Cfg, Page = (L[n] for n in ("ShStore", "ShIsl", "ShMath", "ShCore", "ShDoor", "ShCfg", "ShPage"))
    inv, UUID, coins, PyFn = (L[n] for n in ("inv", "UUID", "coins", "PyFn"))
    ou = UUID.fromString(OWNER)
    W = "skyy-island-" + OWNER
    Core.NOW_TEST = 1790000000000
    Isl.LEVEL_TEST = PyFn(lambda a: JInt(99))
    names = [str(x) for x in Page.SLOT_NAME]
    ws = [int(x) for x in Page.SLOT_W]
    szs = [int(x) for x in Page.SLOT_SIZE]
    fl = [int(x) for x in Page.SLOT_FLAGS]
    for kk_ in KK:
        Door.door(ou, OWNER, kk_, W, 1, 2, 3)
    p = St.get(OWNER)
    coins["bal"] = 99999999999
    cs = inv(9)
    T48._fill(L, cs, [("Skyy_Ench_Wheat", 9)])
    Page.TEST_INV = cs
    pg = Page(ou, W)
    pg.view = 0
    worst, bad, n = {}, [], 0

    def measure():
        nonlocal n
        for i, t in enumerate(str(x) for x in pg.mTx):
            if not t:
                continue
            n += 1
            bold = bool(fl[i] & 1)
            lines = T48._lines(t, ws[i] - 4, szs[i]) if (fl[i] & 2) else (1 if SUI.text_width(t, szs[i], bold) <= ws[i] - 4 else 2)
            lim = 2 if (fl[i] & 2) else 1
            if lines > lim and (names[i], t) not in bad:
                bad.append((names[i], t))
            if len(t) > len(worst.get(names[i], "")):
                worst[names[i]] = t
    for kd in range(6):
        pg.kind = kd
        n_isl = int(Isl.LADN[kd])
        for ti in range(n_isl):
            sl = int(Isl.freeSlot(kd, p)) if int(Isl.slotOf(kd, p, int(Isl.LAD0[kd]) + ti)) < 0 else int(Isl.slotOf(kd, p, int(Isl.LAD0[kd]) + ti))
            for sz in (1, 2, 3):
                for lvl in range(6):
                    St.LOCK.lock()
                    try:
                        if sl >= 0:
                            p.setProperty("%s.i%d.type" % (KK[kd], sl), str(Isl.KEY[int(Isl.LAD0[kd]) + ti]))
                            p.setProperty("%s.i%d.size" % (KK[kd], sl), str(sz))
                            p.setProperty("%s.i%d.last" % (KK[kd], sl), "1790000000000")
                            for f_ in ("amt", "deco", "irr"):
                                p.setProperty("%s.i%d.%s" % (KK[kd], sl, f_), str(lvl if lvl < 5 or sz < 3 else 5))
                        p.setProperty(KK[kd] + ".offline", str(min(lvl, 5)))
                    finally:
                        St.LOCK.unlock()
                    for mv in (0, 1):
                        pg.mview = mv
                        pg.sel = ti
                        pg.fill(OWNER, cs)
                        measure()
                    pg.mview = 1
                    pg.sel = min(ti + 1, n_isl - 1)          # the buy view of the next tier
                    pg.fill(OWNER, cs)
                    measure()
    # every material requirement row at the worst counts (99,999 of an item, 99,999,999,999 coins) - the synthetic rows of reqLine
    pg.mapInit()
    rq = [i for i, nm_ in enumerate(names) if nm_.endswith(("C", "I", "J")) and nm_.startswith("R")] + [i for i, nm_ in enumerate(names) if nm_.startswith("V2R")]
    ids_ = set()
    for kd in range(6):
        for ti in range(int(Isl.LADN[kd])):
            t_ = int(Isl.LAD0[kd]) + ti
            for tm in (Cfg.MAT_AMT, Cfg.MAT_DECO, Cfg.MAT_IRR, Cfg.MAT_GROW, Cfg.BUY_ITEMS[kd], Cfg.AUTO_ITEMS[kd]):
                for part in range(3):
                    m_ = Isl.mats(kd, t_, tm, part, 5)
                    for iid in m_[0]:
                        ids_.add(str(iid))
        ids_.add(str(L["ShKind"].UPG[kd]))
    ids_.add("Ingredient_Void_Essence")
    for iid in sorted(ids_) + [None]:
        for si in rq:
            for need in ((5, 640) if iid else (230, 49920500)):            # items: at most 640 of one; coins: up to a whole T15 island
                pg.reqLine(si, 99999 if iid else 99999999999, need, Page.nameOf(iid) if iid else "coins")
                tt = str(pg.mTx[si])
                n += 1
                if SUI.text_width(tt, szs[si], bool(fl[si] & 1)) > ws[si] - 4 and (names[si], tt) not in bad:
                    bad.append((names[si], tt))
    for nm_, t_ in bad:
        print("W too long %s (%d px): %s" % (nm_, ws[names.index(nm_)], t_))
    K.check(not bad and n > 5000, "W %d runtime Map texts of 6 shards x every tier x 3 sizes x 6 levels fit their labels (one line / two wrapped): %d too long %s" % (n, len(bad), bad[:4]))
    for nm_ in ("RU1A", "RU0C", "RU0I", "V2A", "V2G", "RSzA", "ROffA", "V0Sb", "V1Ot"):
        print("W longest %s: %s" % (nm_, worst.get(nm_)))
    Page.TEST_INV = None
    K.save()


# ---------------------------------------------------------------------------------------------------------- D: live copy, start twice
def run_live49(out, jar, scratch, home):
    from jpype import JClass, JInt
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    Cfg, path = T42.kit_home(home)
    M4, M5, M6, M8, M9 = (JClass(PKG + n) for n in ("ShMig044", "ShMig045", "ShMig046", "ShMig048", "ShMig049"))
    St, Isl, Page, Map = JClass(PKG + "ShStore"), JClass(PKG + "ShIsl"), JClass(PKG + "ShPage"), JClass(PKG + "ShMap")
    sd = os.path.join(home, "shards")

    def start():
        T42.kit_home(home)
        rs = (str(Cfg.migCoop(Cfg.FILE)), str(M4.run(Cfg.FILE)), str(M5.run(Cfg.FILE)), str(M6.run(Cfg.FILE)), str(M8.run(Cfg.FILE)), str(M9.run(Cfg.FILE)))
        Cfg.loadCfg(True)
        St.DIR = path(sd)
        St.CACHE.clear()
        keys = [f[:-11] for f in sorted(os.listdir(sd)) if f.endswith(".properties")] if os.path.isdir(sd) else []
        return rs, [(k, St.get(k)) for k in keys]
    rs, profs = start()
    K.check(rs[5].startswith("config.properties updated for SkyyShards 0.4.9") and float(Cfg.AMT_BONUS) == 3.0, "D start 1: ShMig049 runs once (%s); bonus 3 %%" % rs[5][:160])
    K.check(len(profs) >= 1 and all(str(p.getProperty("map.done")) == "1" for k, p in profs), "D start 1: every real profile loaded (%d; the 0.4.8 map migration as before)" % len(profs))
    for k, p in profs:
        own = [kd for kd in range(6) if p.getProperty(KK[kd] + ".i0.type") is not None]
        K.check(all(int(Isl.offLv(kd, p)) == 5 and p.getProperty(KK[kd] + ".offline") is None for kd in own),
                "D the real profile's shards (%s): Offline Harvest 5 = the old 3 days, no key written" % [KINDS[kd] for kd in own])
        Page.TEST_INV = None
        for kd in range(6):
            pg = Page(JClass("java.util.UUID").fromString(k[:36]), "skyy-island-" + k)
            pg.kind = kd
            pg.view = 0
            Isl.LEVEL_TEST = None
            pg.fill(k, None)
            K.check(len(list(pg.mTex)) == int(Map.NN[kd]) and str(pg.mTx[0]).endswith("Shard"), "D the real profile's %s map fills (%d islands)" % (KINDS[kd], int(Map.NN[kd])))
    t1 = T42.tree(home)
    rs2, profs2 = start()
    K.check(rs2 == ("", "", "", "", "", "") and T42.tree(home) == t1, "D start 2: nothing runs, no file changes")
    K.save()


EXPECT = {   # checked by hand 2026-10-24: the version texts (CfgFile / CfgFn / CfgRows, ShStore.migrate / migrate2 / save log lines); the rest = the round
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
    "ShCfg": ["+f DEF_OFF_ENCH", "+f DEF_OFF_H", "+f DEF_OFF_STEP", "+f OFF_ENCH", "+f OFF_H", "+f OFF_STEP", "+f UI_KEEP", "~<clinit>", "~m loadCfg", "~m writeDefaults"],
    "ShCore": ["+m buyOffline", "+m buyOffline0", "+m offCoins", "+m offEnch", "+m offStep", "~m buyStorage"],   # fix 2: the buy message wording
    "ShIsl": ["+m offH", "+m offLv", "~m offMs"], "ShMath": ["~m capOf", "~m starter"],
    "ShPage": ["+f DECO_TXT", "+f KP_LINE", "+f KP_NAME", "+f KP_REQ", "+f KP_ST", "+f SLOT_FLAGS", "+f SLOT_NAME", "+f SLOT_SIZE", "+f SLOT_W", "+f STYLES",
               "+f kFalls", "+f kKind", "+f kLast", "+f kSigD", "+f kZ", "+f keeps", "+f kst", "+f mCol", "+f mHint", "+f mLit", "+f mOn", "+f mPip", "+f mTex",
               "+f mTx", "+f mV", "+f mapEls", "+f mview", "+f railCol", "+f railSub", "+f wnNow", "+f zoom", "+m canSwitch", "+m decoTxt", "+m fillMap",
               "+m fillRail", "+m hrs", "+m kSets", "+m kSig", "+m kTry", "+m kUpd", "+m kci", "+m keepable", "+m mapInit", "+m nameOf", "+m reqLine", "+m reqMats",
               "+m stSets", "~<clinit>", "~c ", "~c ", "~m act", "~m build", "~m buildFull", "~m fill", "~m fillTotems", "~m handleDataEvent"],
    "ShStore": ["~m migrate", "~m migrate2", "~m save"], "SkyyShardsPlugin": ["~m setup"]}

# C: the kit's compare allows only manifest.json among the non-class entries - 0.4.9 adds the map pictures + page data (phase S counts them;
# phase U draws them): the compare runs on a copy of the new jar without them
import re as _re
import zipfile as _zf
_ORIG_COMPARE = HK.run_compare
MAP_ENTRY = _re.compile(r"\A(?:Common/UI/Custom/SkyyShards/Map/|com/skyy/shards/map/)")


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    cp = os.path.join(SCRATCH, "compare-%s.jar" % VERSION)
    with _zf.ZipFile(jar) as zi, _zf.ZipFile(cp, "w", _zf.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if not MAP_ENTRY.match(n):
                zo.writestr(n, zi.read(n))
    _ORIG_COMPARE(out, cp, old_jar, pkg, expect, added, removed)


HK.run_compare = _compare

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ShMap", "ShMig049"],
           phases=[("static", run_static), ("exec48", run_exec48), ("exec47", run_exec47), ("exec46", run_exec46), ("centre47", run_centre47),
                   ("config48", run_config48), ("mig48", run_mig48), ("players48", run_players48), ("geo48", run_geo48),
                   ("config", run_config), ("mig", run_mig), ("exec", run_exec), ("page", run_page), ("width", run_width), ("live", run_live49)],
           script=__file__, live=(T46.LIVE_SH, "mods/Skyy_SkyyShards"))
