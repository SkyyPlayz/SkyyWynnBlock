"""Harness for SkyyShards 0.4.2 (MENU PATTERN S4 windows + SHARD CO-OP COLLECT; tools/shards_0_4_2_patch.py).
Build first: python tools/shards_0_4_2_patch.py && python SkyyShards/build_skyyshards_0.4.2.py

    python SkyyShards/test_skyyshards_0.4.2.py [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.1 -> 0.4.2: no class added / removed; exactly the planned members differ (EXPECT); non-class entries: the manifest only
  X    exec     the 0.4 harness's exec phase (X1-X8 on real containers) on this jar, DERIVED for the planned 0.4.2 changes only (co-op gets the
                Collect buttons by default, the exit page's Leave Shard id, the bench Craft tab = one scroll list) - every other X1-X8 check as it
                was - plus:
                X9  CO-OP COLLECT: a co-op member collects exactly what is stored (owner then finds nothing); a double click pays once; owner
                    + member + a 2nd member + a double click AT ONCE (real threads) pay exactly the stored total once (no copy, nothing lost);
                    a full member inventory keeps the rest in the shard (the owner collects it later: total = stored); the member is refused
                    storage / Auto-Compactor / Time Compressor / Grow (file, items and coins unchanged); the owner still buys; a visitor and
                    a trusted player are refused Collect; shard.coopCollect off = co-op refused again (no Collect buttons)
                X10 THE REAL WINDOWS (Menu-Pattern 3.6): every view built into its real packet (menu 4 tabs x owner / member, a grown and a
                    full Collect list, exit, totem, bench 3 tabs): root <= 1600 x 980, at most ONE tab row (#...Tabs) of 32 px buttons, no
                    Back / < Menu / pager text (markup + b.set), no Prev / Next binding, the lists are TopScrolling scroll lists, rule 7 (a
                    short list's rows are taller, a long one normal), one Primary outside the tab row; ShPage.growSize = SUI.grow_pick;
                    SUI.assert_proven on the built markup
  M    mig      ShCfg.migCoop EXECUTED on real files (the SkyyRebirth 0.3.4 test): an untouched LF / CRLF shard.coopCollect=false -> true +
                marker (every other byte kept, the old bytes in config-history, one config-changes.log line, loadCfg reads ON); run twice =
                nothing; hand-edited values kept (+ marker, no change-log line); no line -> appended; config-history not writable = untouched,
                next run migrates; no file = nothing, a fresh file carries the marker; the row default is true; setup() order
  D    live     the 0.4 live phase (start twice reading a scratch COPY of the live NewBetaTest Skyy_SkyyShards: nothing written)
  D2   live2    migCoop on a scratch COPY of the live NewBetaTest Skyy_SkyyShards: start 1 = only that line + the marker (+ history / change
                log), start 2 + the config kit = nothing written
  AA   engine-access audit
Scratch: tools/dev/scratch/menuS4/shards/h (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util, re, threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

VERSION = "0.4.2"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS4", "shards", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.1.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
LIVE_SH = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyShards")
TRUSTED = "0b0b0b0b-1111-2222-3333-888888888888"
MEMBER2 = "0a0a0a0a-1111-2222-3333-999999999999"

# ====================================================================================================== the 0.4 harness, derived
_T04_SRC = open(os.path.join(HERE, "test_skyyshards_0.4.py"), encoding="utf8").read()
_DER = []


def der(old, new):
    global _T04_SRC
    assert _T04_SRC.count(old) == 1, "the 0.4 harness changed: %s" % old[:120]
    _T04_SRC = _T04_SRC.replace(old, new)
    _DER.append(old[:60])


der('''    K.check("#SkyyShPick" not in resm["binds"] and "#SkyyShCAll" not in resm["binds"] and "#SkyyShCRow0Btn" not in resm["binds"] and "#SkyyShEnter" in resm["binds"],
            "X7 co-op: Enter, no Pick up, no Collect buttons (shard.coopCollect off)")''',
    '''    K.check("#SkyyShPick" not in resm["binds"] and "#SkyyShCAll" in resm["binds"] and "#SkyyShCRow0Btn" in resm["binds"] and "#SkyyShEnter" in resm["binds"]
            and bool(Cfg.COOP_COLLECT) and "#SkyyShUBuy" not in resm["binds"],
            "X7 co-op (0.4.2: shard.coopCollect ON by default): Enter + the Collect buttons, no Pick up, no Buy upgrade")''')
der('''    Cfg.COOP_COLLECT = True
    K.check("#SkyyShCAll" in build(page(mu, ISL, FK, 0))["binds"], "X7 with shard.coopCollect on, co-op gets Collect")
    Cfg.COOP_COLLECT = False
''', '''    Cfg.COOP_COLLECT = False
    _roff = build(page(mu, ISL, FK, 0))
    K.check("#SkyyShCAll" not in _roff["binds"] and "#SkyyShCRow0Btn" not in _roff["binds"], "X7 with shard.coopCollect off, co-op gets no Collect buttons")
    Cfg.COOP_COLLECT = True
''')
der('''    K.check(rx["binds"] == ["#SkyyShXBack", "#SkyyShXClose"] and rx["sets"].get("#SkyyShXTitle.Text") == "Farming Shard" and "SkyyShTab0" not in rx["mk"],
            "X7 the exit page: Back to Island + Close only, no tabs")''',
    '''    K.check(rx["binds"] == ["#SkyyShXLeave", "#SkyyShXClose"] and rx["sets"].get("#SkyyShXTitle.Text") == "Farming Shard" and "SkyyShTab0" not in rx["mk"]
            and "Leave Shard" in rx["mk"], "X7 the exit page (0.4.2): Leave Shard + Close only, no tabs")''')
_a = _T04_SRC.index('''    K.check("#SkyyShBKCraft" in rk["binds"] and int(pb.kN) == 7, "X7 the bench Craft tab (7 rows a page)")''')
_b = _T04_SRC.index('''"X7 ... and the extra shards last (any bench)")\n''', _a) + len('''"X7 ... and the extra shards last (any bench)")\n''')
_T04_SRC = _T04_SRC[:_a] + '''    K.check("#SkyyShBKCraft" in rk["binds"] and int(pb.kN) > 7 and "#SkyyShBKPrev" not in rk["binds"] and "#SkyyShBKNext" not in rk["binds"]
            and "SkyyShBKList" in rk["mk"] and "Page " not in str(pb.kCap), "X7 the bench Craft tab (0.4.2): every recipe in ONE scroll list, no pager (%d rows)" % int(pb.kN))
    lst = [str(Cfg.CRAFT_ID[int(pb.kIdx[i])]) for i in range(int(pb.kN))]
    _cat = [0 if "Skyy_Totem_" in x else (1 if "TotemMod" in x else (2 if x.startswith("Skyy_Shard_") else 9)) for x in lst]
    K.check(lst[0] == "Skyy_Totem_HarvestSpirit" and _cat == sorted(_cat) and set(_cat) == set([0, 1, 2])
            and not any(x in ("Skyy_Totem_LumberSpirit", "Skyy_Totem_QuarrySpirit") for x in lst),
            "X7 Farming's bench lists Farming's totems first, then the modifiers, then the extra shards; no other shard's totem (%s)" % lst[:3])
    pb.act("bknext", None, None); pb.act("bknext", None, None); build(pb)
    K.check([str(Cfg.CRAFT_ID[int(pb.kIdx[i])]) for i in range(int(pb.kN))] == lst, "X7 the old bknext click is a harmless no-op (one page)")
''' + _T04_SRC[_b:]
_DER.append("bench craft")
der('''    K.save()


# ====================================================================================================== D: live (start twice)''',
    '''    X9_X10(locals())
    K.save()


# ====================================================================================================== D: live (start twice)''')
T04 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_derived", loader=None))
T04.__file__ = os.path.join(HERE, "test_skyyshards_0.4.py")
_HK_COMPARE = HK.run_compare          # the 0.4 harness swaps in its own 0.3.2 -> 0.4 compare: keep the kit's
exec(compile(_T04_SRC, T04.__file__ + " (derived for 0.4.2)", "exec"), T04.__dict__)
HK.run_compare = _HK_COMPARE
T04.LIVE_DIR = os.path.dirname(LIVE_SH)
T04.X9_X10 = None          # set below (X9_X10 is defined after the derived module)

EXPECT = {}          # filled from the observed 0.4.1 -> 0.4.2 compare (see the bottom)

_TXT = re.compile(r'Text:\s*"((?:[^"\\]|\\.)*)"')


def X9_X10(L):
    """runs inside the derived run_exec (its fixtures: roles, inventories, coins, pages)"""
    from jpype import JClass, JLong, JString
    K, Cfg, St, Core, Page, PFn, Role, Inv, Mth, Kind = (L[n] for n in ("K", "Cfg", "St", "Core", "Page", "PFn", "Role", "Inv", "Mth", "Kind"))
    ou, mu, vu, FK, inv, count, build, page, roles, coins = (L[n] for n in ("ou", "mu", "vu", "FK", "inv", "count", "build", "page", "roles", "coins"))
    OWNER = T04.OWNER
    UUID = JClass("java.util.UUID")
    tu, m2 = UUID.fromString(TRUSTED), UUID.fromString(MEMBER2)
    roles[TRUSTED] = "trusted"
    roles[MEMBER2] = "member"
    PROD = str(Kind.PROD[FK])
    NOW = int(Core.NOW_TEST)
    K.check(bool(Cfg.COOP_COLLECT), "X9 shard.coopCollect is ON by default (the loaded default file)")

    def fill(per):
        """every Farming island of the owner holds `per` items (production frozen at NOW, no bonus, no compactor); returns the total"""
        St.LOCK.lock()
        try:
            p = St.get(OWNER)
            p.remove("farming.compactor")
            tot = 0
            for i in range(int(Mth.SLOTS)):
                if bool(Mth.hasIsland(FK, p, i)):
                    p.setProperty("farming.i%d.stored" % i, str(per))
                    p.setProperty("farming.i%d.ench" % i, "0")
                    p.setProperty("farming.i%d.last" % i, str(NOW))
                    tot += per
            K.check(St.save(OWNER, p) is None, "X9 (fixture saved)")
        finally:
            St.LOCK.unlock()
        return tot

    def stored():
        St.LOCK.lock()
        try:
            p = St.get(OWNER)
            Mth.settleAll(FK, p, JLong(NOW))
            return sum(int(Mth.stored(FK, p, i)) for i in range(int(Mth.SLOTS)) if bool(Mth.hasIsland(FK, p, i)))
        finally:
            St.LOCK.unlock()
    S = fill(150)
    K.check(S > 0 and stored() == S, "X9 the fixture: %d %s stored in the owner's Farming islands (production frozen)" % (S, PROD))
    TM = inv(9, 36)
    rm = str(Core.collect(mu, OWNER, FK, -1, TM))
    K.check(rm.startswith("+Collected") and count(TM, PROD) == S and stored() == 0, "X9 a co-op member collects everything stored (%d): %s" % (S, rm[:80]))
    K.check(str(Core.collect(mu, OWNER, FK, -1, TM)).startswith("=Nothing is stored") and count(TM, PROD) == S, "X9 the member's double click pays once")
    TO = inv(9, 36)
    K.check(str(Core.collect(ou, OWNER, FK, -1, TO)).startswith("=Nothing is stored") and count(TO, PROD) == 0, "X9 ... and the owner then finds nothing (no copy)")
    clog = open(os.path.join(str(Cfg.DIR), "collect.log"), encoding="utf-8").read()
    K.check(("%s %s slot -1 debit %d given %d back 0" % (str(mu), OWNER, S, S)) in clog, "X9 collect.log names the member, the owner's shard, debit = given")
    # at once: owner all + member all + member 2 all + the owner's own double click + member slot 0 (real threads, one barrier)
    for rnd in range(3):
        S2 = fill(120 + rnd)
        who = [(ou, -1), (mu, -1), (m2, -1), (ou, -1), (mu, 0)]
        invs = [inv(9, 36) for _ in who]
        res = [None] * len(who)
        bar = threading.Barrier(len(who))

        def run(j):
            bar.wait()          # (jpype attaches the thread on its first Java call)
            res[j] = str(Core.collect(who[j][0], OWNER, FK, who[j][1], invs[j]))
        th = [threading.Thread(target=run, args=(j,)) for j in range(len(who))]
        for t_ in th:
            t_.start()
        for t_ in th:
            t_.join(60)
        got = sum(count(c, PROD) for c in invs)
        K.check(got == S2 and stored() == 0 and all(r is not None and (r.startswith("+Collected") or r.startswith("=Nothing")) for r in res),
                "X9 round %d: owner + member + member 2 + a double click + a slot click AT ONCE pay exactly %d once (got %d): %s"
                % (rnd + 1, S2, got, [r[:12] for r in res]))
    # a full member inventory: what does not fit stays in the shard; the owner collects the rest; total = stored
    S3 = fill(150)
    TF = inv(1)
    rf = str(Core.collect(mu, OWNER, FK, -1, TF))
    a1 = count(TF, PROD)
    left = stored()
    TO2 = inv(9, 36)
    ro = str(Core.collect(ou, OWNER, FK, -1, TO2))
    K.check(0 < a1 < S3 and left == S3 - a1 and count(TO2, PROD) == left and stored() == 0,
            "X9 a full member inventory: %d given, %d stay in the shard, the owner collects them (total %d = stored): %s / %s" % (a1, left, S3, rf[:60], ro[:40]))
    # the member is refused storage / upgrades / Grow: file, items and coins unchanged
    TU = inv(9, 36)
    for it_, n_ in (("Skyy_Ench_Wheat", 64), ("Ingredient_Void_Essence", 64), ("Plant_Seeds_Wheat_Eternal", 64)):
        Inv.give(TU, it_, JLong(n_))
    before = dict((str(k), str(St.get(OWNER).getProperty(k))) for k in St.get(OWNER).stringPropertyNames())
    c0 = coins["bal"]
    ib = [count(TU, x) for x in ("Skyy_Ench_Wheat", "Ingredient_Void_Essence", "Plant_Seeds_Wheat_Eternal")]
    outs = [str(Core.buyStorage(mu, OWNER, FK, TU)), str(Core.buyCompactor(mu, OWNER, FK, TU)), str(Core.buyCompressor(mu, OWNER, FK, TU)),
            str(Core.grow(mu, OWNER, FK, 0, TU))]
    after = dict((str(k), str(St.get(OWNER).getProperty(k))) for k in St.get(OWNER).stringPropertyNames())
    K.check(all(o.startswith("-Only the island owner can buy upgrades and grow islands") for o in outs) and after == before and coins["bal"] == c0
            and [count(TU, x) for x in ("Skyy_Ench_Wheat", "Ingredient_Void_Essence", "Plant_Seeds_Wheat_Eternal")] == ib,
            "X9 a co-op member is refused storage / Auto-Compactor / Time Compressor / Grow - shard file, items, coins unchanged: %s" % [o[:50] for o in outs])
    for it_, n_ in (("Skyy_Ench_Wheat", 64),):
        Inv.give(TO2, it_, JLong(n_))
    rbo = str(Core.buyStorage(ou, OWNER, FK, TO2))
    K.check(not rbo.startswith("-Only the island owner"), "X9 the owner still buys storage: %s" % rbo[:70])
    S4 = fill(100)
    for u_, nm in ((vu, "a visitor"), (tu, "a trusted player")):
        TV = inv(9, 36)
        rv = str(Core.collect(u_, OWNER, FK, -1, TV))
        K.check(rv.startswith("-Only the island owner and co-op members") and count(TV, PROD) == 0 and stored() == S4, "X9 %s is refused Collect: %s" % (nm, rv[:60]))
    Cfg.COOP_COLLECT = False
    TV = inv(9, 36)
    roff = str(Core.collect(mu, OWNER, FK, -1, TV))
    K.check(roff.startswith("-Only the island owner can collect") and count(TV, PROD) == 0 and stored() == S4, "X9 shard.coopCollect off: co-op refused again: %s" % roff[:60])
    Cfg.COOP_COLLECT = True
    # the page: the member's Collect click goes through the same collect
    Page.TEST_INV = TM
    pgm = page(mu, "skyy-island-" + OWNER, FK, 0)
    rpm = build(pgm)
    m_before = count(TM, PROD)
    ra = str(pgm.act("colall", None, None))
    K.check("#SkyyShCAll" in rpm["binds"] and "#SkyyShIGrow" not in rpm["binds"] and ra.startswith("+Collected") and count(TM, PROD) == m_before + S4 and stored() == 0,
            "X9 the member's page: Collect all collects (%s), no Grow button" % ra[:50])
    pgm.tab = 2
    K.check("#SkyyShIGrow" not in build(pgm)["binds"] and str(pgm.act("grow", None, None)).startswith("-Only the island owner can buy upgrades"),
            "X9 the member's Islands tab: no Grow button; a forged grow click is refused")
    pgm.tab = 1
    K.check(not [b_ for b_ in build(pgm)["binds"] if b_ in ("#SkyyShUBuy", "#SkyyShUCBuy", "#SkyyShUTBuy")] and str(pgm.act("buy", None, None)).startswith("-Only the island owner"),
            "X9 the member's Upgrades tab: no Buy buttons; a forged buy click is refused")

    # ---------------- X10 THE REAL WINDOWS
    PG = JClass(PKG + "ShPage")
    hs = [56, 81, 112]
    from jpype import JArray, JInt
    K.eq([int(PG.growSize(n, 490, JArray(JInt)(hs), 4)) for n in range(0, 12)],
         [SUI.grow_pick(n, 490, hs, gap=4) for n in range(0, 12)], "X10 ShPage.growSize = the kit's Python twin SUI.grow_pick")
    PRI = SUI.TEX["btn" + SUI.BUTTONS["primary"][0]]
    views = []
    for tab in range(4):
        for u_, nm in ((ou, "owner"), (mu, "member")):
            pg = page(u_, "skyy-island-" + OWNER, FK, 0)
            pg.tab = tab
            views.append(("menu tab %d %s" % (tab, nm), pg))
    SHW = "skyy-shard-" + OWNER
    views.append(("exit", page(ou, SHW, FK, 0)))
    pt = page(ou, SHW, FK, 1)
    pt.near = False
    views.append(("totem", pt))
    for bt in range(3):
        pb = page(ou, SHW, FK, 2)
        pb.bTab = bt
        views.append(("bench tab %d" % bt, pb))
    bad, proven = [], []
    for nm, pg in views:
        r = build(pg)
        mk = r["mk"]
        m_ = re.search(r"Group #(\w+) \{ Anchor: \(Width: (\d+), Height: (\d+)\); \}", mk)
        if not m_ or int(m_.group(2)) > 1600 or int(m_.group(3)) > 980:
            bad.append((nm, "size", m_ and m_.groups()))
        rows = set(re.findall(r"Group #(\w+Tabs) \{", mk))
        if len(rows) > 1:
            bad.append((nm, "tab rows", rows))
        for rid in rows:
            hts = [int(x.group(1)) for x in re.finditer(r"TextButton #%s\d+ \{ Anchor: \(Width: \d+, Height: (\d+)\)" % (rid[:-4] + "Tab"), mk)]
            if not hts or set(hts) != set([32]):
                bad.append((nm, "tab heights", hts))
        texts = _TXT.findall(mk) + [v for k_, v in r["sets"].items() if k_.endswith(".Text")]
        for t_ in texts:
            if SUI.MENU_BACK_RE.match(t_) or SUI.MENU_PAGER_RE.match(t_) or t_.strip().lower() in ("previous", "next"):
                bad.append((nm, "back / pager text", t_))
        if [b_ for b_ in r["binds"] if b_ in ("#SkyyShBKPrev", "#SkyyShBKNext", "#SkyyShXBack") or b_.endswith("Back")]:
            bad.append((nm, "pager / back binding", r["binds"]))
        pri = [x for x in re.findall(r"TextButton #(\w+) \{[^{}]*?" + re.escape(PRI), mk) if "Tab" not in x]
        if len(pri) > 1:
            bad.append((nm, "primaries", pri))
        for lid in ("SkyyShCList", "SkyyShBKList", "SkyyShBRList"):
            if lid in mk and not re.search(r"Group #%s \{[^{}]*LayoutMode: TopScrolling" % lid, mk):
                bad.append((nm, "not a scroll list", lid))
        proven.append(mk)
    K.check(not bad, "X10 every real window (%d views): <= 1600 x 980, one 32 px tab row at most, no Back / pager text or binding, scroll lists, "
            "one Primary: %s" % (len(views), bad[:4]))
    K.check(sum(1 for nm, pg in views if "SkyyShCList" in build(pg)["mk"]) >= 2 and "SkyyShBKList" in build(views[-3][1])["mk"]
            and "SkyyShBRList" in build(views[-2][1])["mk"], "X10 the Collect / Craft / Tier up lists are there")
    try:
        SUI.assert_proven(proven, what="SkyyShards 0.4.2 built windows")
        K.check(True, "X10 SUI.assert_proven on the built markup of every view")
    except Exception as e:
        K.check(False, "X10 SUI.assert_proven on the built markup: %s" % str(e)[:300])
    # rule 7 on the real menu: 2 islands = taller rows, 6 islands = normal rows
    St.LOCK.lock()
    try:
        p = St.get(OWNER)
        nis = sum(1 for i in range(int(Mth.SLOTS)) if bool(Mth.hasIsland(FK, p, i)))
    finally:
        St.LOCK.unlock()
    pg = page(ou, "skyy-island-" + OWNER, FK, 0)
    mk = build(pg)["mk"]
    hrow = re.search(r"Group #SkyyShCRow0 \{ Anchor: \(Width: \d+, Height: (\d+)", mk)
    want = [56, 0, 0]
    want_h = SUI.grow_row_sizes(568 - 78, 56, gap=4)[SUI.grow_pick(nis, 568 - 78, SUI.grow_row_sizes(568 - 78, 56, gap=4), gap=4)]
    K.check(hrow is not None and int(hrow.group(1)) == want_h, "X10 rule 7: %d island(s) -> Collect rows %s px (want %d)" % (nis, hrow and hrow.group(1), want_h))
    pb = page(ou, SHW, FK, 2)
    pb.bTab = 1
    rb = build(pb)
    hr = re.search(r"Group #SkyyShBRRow0 \{ Anchor: \(Width: \d+, Height: (\d+)", rb["mk"])
    RHS = SUI.grow_row_sizes(568 - 78, 50, gap=4)
    K.check(int(pb.rN) == 0 or (hr is not None and int(hr.group(1)) == RHS[SUI.grow_pick(int(pb.rN), 490, RHS, gap=4)]),
            "X10 rule 7 on the bench Tier up list: %d row(s) -> %s px" % (int(pb.rN), hr and hr.group(1)))
    K.notes.append("X10 views: %s" % [v[0] for v in views])


T04.X9_X10 = X9_X10


# ====================================================================================================== M: the migration
def kit_home(home):
    from jpype import JClass, JArray
    Pth = JClass("java.nio.file.Paths")
    path = lambda p_: Pth.get(p_, JArray(JClass("java.lang.String"))([]))
    R = lambda n: JClass(PKG + n)
    R("CfgRows").HOME = path(home)
    R("CfgHist").init()
    R("CfgLog").init()
    Cfg = R("ShCfg")
    Cfg.DIR = path(home)
    Cfg.FILE = path(os.path.join(home, "config.properties"))
    return Cfg, path


def setup_calls(jar):
    """the invoke order inside SkyyShardsPlugin.setup() (javassist, read only)"""
    from jpype import JClass
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    m = pool.get(PKG + "SkyyShardsPlugin").getDeclaredMethod("setup")
    ci = m.getMethodInfo().getCodeAttribute().iterator()
    cp = m.getMethodInfo().getConstPool()
    names = []
    while ci.hasNext():
        i = ci.next()
        op = ci.byteAt(i)
        if op in (0xb6, 0xb7, 0xb8, 0xb9):
            idx = ci.u16bitAt(i + 1)
            cls = cp.getInterfaceMethodrefClassName(idx) if op == 0xb9 else cp.getMethodrefClassName(idx)
            nm = cp.getInterfaceMethodrefName(idx) if op == 0xb9 else cp.getMethodrefName(idx)
            names.append("%s.%s" % (str(cls).split(".")[-1], nm))
    return names


def tree(d):
    out = {}
    for r, _ds, fs in os.walk(d):
        for f in fs:
            p = os.path.join(r, f)
            out[os.path.relpath(p, d).replace(os.sep, "/")] = open(p, "rb").read()
    return out


def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    home = os.path.join(scratch, "m", "mods", "Skyy_SkyyShards")
    os.makedirs(home)
    Cfg, path = kit_home(home)
    cfgf = os.path.join(home, "config.properties")
    hist_d = os.path.join(home, "config-history")
    chg_f = os.path.join(home, "config-changes.log")
    MARK = str(Cfg.MIG_MARK).encode("latin-1")
    KEY = b"shard.coopCollect"

    def hist_has(b_):
        return os.path.isdir(hist_d) and any(open(os.path.join(hist_d, f_), "rb").read() == b_ for f_ in os.listdir(hist_d) if f_.endswith(".bak"))

    def chg():
        return open(chg_f, encoding="utf-8").read().splitlines() if os.path.isfile(chg_f) else []

    def mig(b_):
        open(cfgf, "wb").write(b_)
        return str(Cfg.migCoop(path(cfgf))), open(cfgf, "rb").read()

    live_cfg = os.path.join(LIVE_SH, "config.properties")
    A_ = open(live_cfg, "rb").read() if os.path.isfile(live_cfg) else None     # read only (the live file is never written)
    K.check(A_ is not None and A_.count(b"\n" + KEY + b"=false") == 1, "M the live NewBetaTest config.properties (read only) holds shard.coopCollect=false")
    if A_ is None:
        A_ = b"# head\nshards.on=true\nshard.coopCollect=false\nshard.regrowSec=90\n"
    nl = b"\r\n" if b"\r\n" in A_ else b"\n"
    wantA = A_.replace(nl + KEY + b"=false" + nl, nl + KEY + b"=true" + nl + MARK + nl)
    n0 = len(chg())
    rA, gotA = mig(A_)
    cl = chg()
    K.check(gotA == wantA and gotA != A_ and "shard.coopCollect false -> true" in rA and hist_has(A_) and len(cl) == n0 + 1
            and "\tshard.coopCollect\tfalse\ttrue\tok" in cl[-1] and "SkyyShards 0.4.2" in cl[-1],
            "M the live text (untouched false) -> true: the marker under it, every other byte kept, the old bytes in config-history, one change-log "
            "line false -> true (Undo = false) (%s / %s)" % (rA[:70], cl[-1:]))
    Cfg.COOP_COLLECT = False
    Cfg.loadCfg(False)
    K.check(bool(Cfg.COOP_COLLECT), "M loadCfg reads the migrated file: co-op may collect")
    rA2 = str(Cfg.migCoop(path(cfgf)))
    K.check(rA2 == "" and open(cfgf, "rb").read() == gotA and len(chg()) == n0 + 1, "M run once: the second start changes nothing (%r)" % rA2)
    other = A_.replace(b"\r\n", b"\n") if nl == b"\r\n" else A_.replace(b"\n", b"\r\n")
    onl = b"\r\n" if nl == b"\n" else b"\n"
    rC, gotC = mig(other)
    K.check(gotC == other.replace(onl + KEY + b"=false" + onl, onl + KEY + b"=true" + onl + MARK + onl) and hist_has(other) and len(chg()) == n0 + 2,
            "M the same file in the other line ending (%s): true + marker in that ending, every other byte kept (%s)" % ("CRLF" if onl == b"\r\n" else "LF", rC[:50]))
    K.check(str(Cfg.migCoop(path(cfgf))) == "" and open(cfgf, "rb").read() == gotC and len(chg()) == n0 + 2, "M ... run twice: nothing")
    n1 = len(chg())
    for b_, label in ((b"a=1\nshard.coopCollect=true\nshard.regrowSec=90\n", "true"), (b"a=1\r\nshard.coopCollect = TRUE\r\nshard.regrowSec=90\r\n", "TRUE (CRLF)"),
                      (b"shard.coopCollect=no\nshard.regrowSec=90\n", "no"), (b"shard.coopCollect=\\\n  false\nshard.regrowSec=90\n", "a continued value"),
                      (b"shard.coopCollect=false\nshard.coopCollect=true\n", "false then true (last wins)")):
        r_, got_ = mig(b_)
        if label == "a continued value":
            want_ = b"shard.coopCollect=\\\n  false\n" + MARK + b"\nshard.regrowSec=90\n"
        elif label == "false then true (last wins)":
            want_ = b"shard.coopCollect=false\nshard.coopCollect=true\n" + MARK + b"\n"
        else:
            n_ = b"\r\n" if b"\r\n" in b_ else b"\n"
            ls = b_.split(n_)
            k_ = [i for i, x in enumerate(ls) if x.startswith(KEY)][-1]
            want_ = n_.join(ls[:k_ + 1] + [MARK] + ls[k_ + 1:])
        Cfg.loadCfg(False)
        K.check(got_ == want_ and "kept" in r_ and len(chg()) == n1 and hist_has(b_),
                "M an admin's shard.coopCollect (%s) is KEPT: only the marker is added, no change-log line (%r)" % (label, r_[:60]))
        if label == "no":
            K.check(not bool(Cfg.COOP_COLLECT), "M ... shard.coopCollect=no still reads OFF (an admin's choice)")
    D_ = b"shards.on=true\nshard.regrowSec=90\n"
    rD, gotD = mig(D_)
    Cfg.loadCfg(False)
    K.check(gotD == D_ + KEY + b"=true\n" + MARK + b"\n" and "line added" in rD and len(chg()) == n1 + 1 and bool(Cfg.COOP_COLLECT),
            "M no shard.coopCollect line (it read the old default false) -> shard.coopCollect=true appended + marker, one change-log line (%r)" % gotD)
    D2 = b"shards.on=true"
    rD2, gotD2 = mig(D2)
    K.check(gotD2 == D2 + b"\n" + KEY + b"=true\n" + MARK + b"\n", "M no line and no final newline: appended on its own line (%r)" % gotD2)
    import shutil
    shutil.rmtree(hist_d)
    open(hist_d, "wb").write(b"x")
    E_ = b"x=1\nshard.coopCollect=false\n"
    nE = len(chg())
    rE, gotE = mig(E_)
    K.check(rE == "" and gotE == E_ and len(chg()) == nE, "M config-history not writable: the file is untouched, no change-log line (%r)" % rE)
    os.remove(hist_d)
    rE2, gotE2 = str(Cfg.migCoop(path(cfgf))), open(cfgf, "rb").read()
    K.check(gotE2 == b"x=1\nshard.coopCollect=true\n" + MARK + b"\n" and hist_has(E_), "M ... the next start migrates it (%s)" % rE2[:50])
    os.remove(cfgf)
    K.check(str(Cfg.migCoop(path(cfgf))) == "" and not os.path.exists(cfgf), "M no file: nothing to do")
    Cfg.COOP_COLLECT = False
    c = str(Cfg.loadCfg(True))
    fresh = open(cfgf, "rb").read()
    K.check(bool(Cfg.COOP_COLLECT) and fresh.count(b"\n" + KEY + b"=true\n" + MARK + b"\n") == 1 and Cfg.migPlan(fresh.decode("latin-1")) is None
            and str(Cfg.migCoop(path(cfgf))) == "" and open(cfgf, "rb").read() == fresh,
            "M a fresh 0.4.2 file: shard.coopCollect=true + the marker, ON, migCoop never touches it (%s)" % c[:50])
    os.remove(cfgf)
    open(cfgf, "wb").write(b"shards.on=true\n")
    Cfg.COOP_COLLECT = False
    Cfg.loadCfg(False)
    K.check(bool(Cfg.COOP_COLLECT), "M a file without shard.coopCollect reads ON (the code default is true)")
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in JClass(PKG + "CfgRows").header()[7])
    K.check(rows["shard.coopCollect"][4] == "true" and rows["shard.coopCollect"][1] == "Co-op may collect" and "owner-only" in rows["shard.coopCollect"][10],
            "M the Server Setup row: 'Co-op may collect', default true, help names owner-only storage / upgrades / Grow: %s" % rows["shard.coopCollect"][:5])
    calls = setup_calls(jar)
    idx = lambda n: calls.index(n) if n in calls else -1
    K.check(0 <= idx("ShCfg.migCoop") < idx("ShCfg.loadCfg") < idx("CfgPub.start") and idx("CfgHist.init") < idx("ShCfg.migCoop")
            and idx("CfgLog.init") < idx("ShCfg.migCoop"),
            "M setup(): CfgHist.init / CfgLog.init, then migCoop, then loadCfg, then CfgPub.start: %s"
            % [c_ for c_ in calls if c_.split(".")[0] in ("ShCfg", "CfgPub", "CfgHist", "CfgLog")][:8])
    K.save()


def run_live2(out, jar, scratch, home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    K = HK.Child(out)
    mods = os.path.dirname(home)
    cfgf = os.path.join(home, "config.properties")
    old = open(cfgf, "rb").read()
    t0 = tree(home)
    Cfg, path = kit_home(home)
    r1 = str(Cfg.migCoop(path(cfgf)))
    c1 = str(Cfg.loadCfg(True))
    t1 = tree(home)
    new = open(cfgf, "rb").read()
    MARK = str(Cfg.MIG_MARK).encode("latin-1")
    nl = b"\r\n" if b"\r\n" in old else b"\n"
    added = sorted(set(t1) - set(t0))
    K.check(new == old.replace(nl + b"shard.coopCollect=false" + nl, nl + b"shard.coopCollect=true" + nl + MARK + nl) and new != old and bool(Cfg.COOP_COLLECT),
            "D2 start 1 on the live copy: shard.coopCollect false -> true + the marker, every other byte kept, co-op may collect (%s)" % r1[:80])
    K.check(all(a_.startswith("config-history/") or a_ == "config-changes.log" for a_ in added)
            and all(t1[k_] == t0[k_] for k_ in t0 if k_ != "config.properties"),
            "D2 start 1 adds only config-history + config-changes.log; nothing else changed: %s" % added)
    r2 = str(Cfg.migCoop(path(cfgf)))
    Cfg.loadCfg(True)
    K.check(r2 == "" and tree(home) == t1, "D2 start 2 writes nothing (%r)" % r2)
    JClass(PKG + "CfgPub").start(path(mods), None)
    JClass(PKG + "CfgPub").flush()
    K.check(tree(home) == t1, "D2 the config kit starts on the migrated file and writes nothing")
    K.notes.append("D2 live: %s | %s" % (r1[:120], c1[:80]))
    K.save()


EXPECT = {
    "ShCfg": ["~<clinit>", "+f MIG_ID", "+f MIG_MARK", "+f MIG_KEY", "+f MIG_OLD", "+f MIG_NEW", "+f MIG_WHO", "+f MIG_LAST",
              "+m migPlan", "+m migSame", "+m migFileIdx", "+m migSaved", "+m migLine", "+m migCoop", "~m loadCfg",
              "~m writeDefaults"],          # writeDefaults: the DEFAULT_TEXT constant (inlined) now holds shard.coopCollect=true + the marker
    "ShCore": ["+m gateOwn", "~m buyStorage", "~m buyCompactor", "~m buyCompressor", "~m grow0"],
    # actBench: the row counts KROWS / RROWS (bksel / brsel bounds); fill: the co-op summary line
    "ShPage": ["+m growSize", "~m buildFull", "~m buildExit", "~m buildBench", "~m fillBenchCraft", "~m fillBenchTier", "~m fill", "~m actBench"],
    "ShStore": ["~m save", "~m migrate"],          # the version text only (the file header "SkyyShards 0.4.2", the forms-migration log line)
    "SkyyShardsPlugin": ["~m setup"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],
}

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("exec", T04.run_exec), ("mig", run_mig), ("live", T04.run_live), ("live2", run_live2)], script=__file__,
           live=(LIVE_SH, "mods/Skyy_SkyyShards"))
