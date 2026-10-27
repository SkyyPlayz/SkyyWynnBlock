"""Harness for SkyyShards 0.4.13 (THE TOTEM PAGE + THE TOTEM BENCH rebuilt from the approved mockups, the per-player range aura;
tools/shards_0_4_13_patch.py, on top of 0.4.12).
Build first:
    python tools/shards_0_4_13_patch.py && python SkyyShards/build_skyyshards_0.4.13.py
    python SkyyShards/test_skyyshards_0.4.13.py [--keep]

  S    static   the patch re-runs to identical bytes; no new registerSystem / registerCommand; the ready line; the 0.4.10 hotfix + the 0.4.12
                payment path kept; the three new config rows; the vanilla particles exist in Assets.zip
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.12 -> 0.4.13: exactly the planned members differ (EXPECT); the only new non-class files are the range pictures
  412  every 0.4.12 harness phase on the 0.4.13 jar (and through it 0.4.11 ... 0.4.6), incl. BG (every cost from the Pocket Dimension),
       PHASE O / O2 (the in-order selector walks), width and F (the click flows)
  O3   walk     EXECUTED: every new page variant built on the real UICommandBuilder and walked IN ORDER as the client runs it (every
                selector exists when its command runs, every binding's element exists): the totem page (owner / co-op, worker / support /
                Harvest Moon / a wrong-shard totem, tier I-V, 0 / 1 / 2 modifiers, burning / empty booster, aura on / off, seeds yes / no /
                automated, full / empty inventory, a gone totem) and the bench (every shard, bench I-IV + upgrading, every category, every
                grid slot selected, locked / ready / missing slots, the Totem Pole category with and without hand-held totems, owner /
                co-op); packet sizes
  F3   flows    EXECUTED clicks through handleDataEvent: bcat / bg / Craft / Make pole (the binding's own data) / Upgrade bench on the bench;
                Give / Take seeds, Add (tmodadd<n>) / Remove a modifier, Add booster, Tier up (the binding's data), Show range on / off,
                onDismiss (the aura stays totem.rangeAuraSec, 0 = gone); every click answers with ONE full page (no keep update) and the
                buttons drawn are exactly the ones that work
  AU   aura     the config rows (defaults, reload), partOr (a bad particle name falls back + one WARN), auraSet geometry, the tick hand-off
  LK   lock     EXECUTED with real threads: another thread holds ShStore.LOCK -> a "WorldThread" opens the shard page within 400 ms and gets
                the busy page (walks clean, Close bound), a click says busy, the WARN names the holder; a lock-order inversion with another
                lock finishes in < 3 s (no deadlock); a non-world thread gives up after WAIT_MS; ShTick on its own daemon thread
  BZ   busy     EXECUTED (review 2026-10-26 fixes): a second thread holds ShStore.LOCK from the first bag count of a click (a WorldThread,
                50 ms): benchUp / tierUpPlaced / a shard craft take NOTHING (items, bags, coins, crafted mark); owed / owedXp keep the credit in
                memory (busy first lock, busy write-back after a refusal, paid-then-busy = never twice); a new profile's first get is not cached
                unmigrated; a hand-placed totem tiers up on its spot (8th part, posOf, paint); ShPlace re-queues a busy check
  PL   place    EXECUTED: placeHere refusals (centre pads, off the island, on another totem, the count limit), the entry's "dx;dz" part
                (pad entries byte-identical), covAt / workerRate around its spot, the paint + nearest + aura at its spot, its page, Pick up
  D    live     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards (the 0.4.10 live phase)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.13"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "totemfix", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.12.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.12.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_13_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_12", os.path.join(HERE, "test_skyyshards_0.4.12.py"))
T412 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T412)
sys.argv[:] = _argv
T412.JAR = JAR
T411 = T412.T411
T410, T49, T48, T46 = T411.T410, T411.T49, T411.T48, T411.T46
for _m in (T411, T410, T49, T48, T46, T411.T47):
    _m.JAR = JAR
OWNER, MEMBER = T49.OWNER, T49.MEMBER
FK = 2
SUP = T49._superseded
GOOD, BAD = T49.GOOD, T49.BAD
SEL = re.compile(r"#([A-Za-z0-9]+)")


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.13 - build script') and g.count('VERSION = "0.4.13"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check("upgrade at the side) + totem poles placed by hand anywhere on an island + a timed data lock (a world thread never waits on it) on our own tick thread; 0.4.12" in g
            and "0.4.12: every shard + Totem Bench cost counts and pays from the Pocket Dimension too" in g, "S the ready line names the round (and keeps 0.4.12's)")
    K.check("this.kShown = kShownSig(this.kZ)" in g and "if (this.kst != null) kSets(b); else stSets(b);" in g, "S the 0.4.10 hotfix is kept")
    K.check(g.count("public static long[] payInvBags(") == 1 and g.count("takeAll(cs, ids, q, kept)") == 0, "S the 0.4.12 payment path is kept (payInvBags, no inventory-only take)")
    for row in ("totem.rangeAuraSec", "totem.rangeEdge", "totem.rangeCell"):
        K.check(g.count('("%s", ' % row) == 1 and g.count('"%s=' % row) == 1, "S the Server Setup row + config line %s" % row)
    import zipfile
    import serverjar as SJ
    az = set(zipfile.ZipFile(SJ.assets_zip()).namelist())
    for pp in ("Block_Top_Glow", "Seed_Place_Dust"):
        K.check(any(n.endswith("/" + pp + ".particlesystem") for n in az), "S the vanilla particle %s is in Assets.zip" % pp)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


# ---------------------------------------------------------------------------------------------------------- shared
def _L(scratch, K):
    L, ou, W, p, lv = T410._world(scratch, K)
    from jpype import JClass
    for n in ("ShAura", "ShTotem", "ShInv", "ShKind", "ShGeo"):
        L[n] = JClass(PKG + n)
    return L, ou, W, p, lv


def _set(L, p, key, val):
    St = L["ShStore"]
    St.LOCK.lock()
    try:
        if val is None:
            p.remove(key)
        else:
            p.setProperty(key, val)
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()


def _binds(pg):
    """the page's bindings after a build: selector -> the "a" value"""
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    pg.build(None, b, ev, None)
    out = {}
    for e in ev.getEvents():
        out[str(e.selector)] = T49._act({str(e.selector): str(e.data)}, str(e.selector))
    return out, b, ev


def _size(b, ev):
    from jpype import JClass
    CPk = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPage")
    LIFE = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime")
    return int(CPk("SkyySh", True, True, LIFE.CanDismiss, b.getCommands(), ev.getEvents()).computeSize())


# ---------------------------------------------------------------------------------------------------------- the text boxes of the two pages
# (field, width of its label, size, bold, lines it may take) - the markup in tools/shards_0_4_13_patch.py (PAGES)
WTXT = [("wName", 276, 16, True, 1), ("wTag", 276, 13, False, 1), ("wRole", 276, 13, False, 1), ("wRgTx", 276, 13, False, 1), ("wRgCap", 276, 13, False, 3),
        ("wOut", 170, 30, False, 1), ("wOutU", 247, 15, False, 1), ("wOut2", 417, 14, False, 1), ("wOut3", 417, 13, False, 2), ("wOutW", 417, 13, False, 1),
        ("wSd[0]", 417, 14, False, 1), ("wSd[1]", 417, 13, False, 1), ("wSd[2]", 417, 13, False, 1), ("wSd[3]", 417, 13, False, 2),
        ("wBo[0]", 359, 14, True, 1), ("wBo[1]", 359, 13, False, 2), ("wBo[2]", 417, 13, False, 1),
        ("wTu[0]", 417, 16, True, 1), ("wTu[1]", 417, 14, False, 1), ("wTu[2]", 417, 14, False, 1), ("wTu[3]", 417, 14, False, 1), ("wTu[4]", 417, 14, False, 1),
        ("wTu[5]", 417, 13, False, 2), ("wMNm[0]", 257, 14, True, 1), ("wMNm[1]", 257, 14, True, 1), ("wMEf[0]", 257, 12, False, 2), ("wMEf[1]", 257, 12, False, 2),
        ("wMl[0]", 327, 13, True, 1), ("wMl[5]", 327, 13, True, 1), ("wMdC", 417, 13, False, 1)]
BTXT = [("bTitle", 520, 16, True, 1), ("bSub", 520, 13, False, 1), ("gTitle", 496, 14, True, 1), ("gEmpty", 460, 13, False, 3), ("qNm", 396, 17, True, 1),
        ("qTag", 396, 13, False, 1), ("qDs", 396, 13, False, 4), ("qInTx[0]", 92, 13, True, 1), ("qInTx[1]", 92, 13, True, 1), ("qInTx[2]", 92, 13, True, 1),
        ("qCo", 396, 14, False, 1), ("qBag", 396, 13, False, 1), ("qWhy", 396, 13, False, 2), ("vTx[0]", 276, 14, True, 1), ("vTx[1]", 276, 13, False, 3),
        ("vTx[2]", 276, 13, False, 1), ("vTx[3]", 276, 13, False, 1), ("vTx[4]", 276, 13, False, 1), ("vTx[5]", 276, 13, False, 2),
        ("vCTx[0]", 84, 13, True, 1), ("gLk[0]", 72, 12, True, 1)]


def _fits(pg, table, bad):
    import skyyui as SUI
    for fld, w, size, bold, lines in table:
        nm, ix = (fld.split("[")[0], int(fld.split("[")[1][:-1])) if "[" in fld else (fld, None)
        v = getattr(pg, nm)
        if v is None:
            continue
        t = str(v[ix]) if ix is not None else str(v)
        if not t:
            continue
        n = (1 if SUI.text_width(t, size, bold) <= w - 4 else 2) if lines == 1 else T48._lines(t, w - 4, size)
        if n > lines and (fld, t) not in bad:
            bad.append((fld, t))


# ---------------------------------------------------------------------------------------------------------- O3: the in-order walk
def run_walk3(out, jar, scratch, _home):
    from jpype import JLong
    K = HK.Child(out)
    L, ou, W, p, lv = _L(os.path.join(scratch, "o3"), K)
    Page, PFn, Cfg, Core, Inv, Tot = L["ShPage"], L["ShPageFn"], L["ShCfg"], L["ShCore"], L["ShInv"], L["ShTotem"]
    mu = L["UUID"].fromString(MEMBER)
    SHW = "skyy-shard-" + OWNER
    now = 1790000000000
    T48.add_items([(i_, 100) for i_ in ("Plant_Seeds_Wheat", "Plant_Seeds_Wheat_Eternal", "Ingredient_Water_Essence", "Ingredient_Life_Essence")
                   + tuple(str(x) for x in Tot.MOD_ITEMS)])
    full_cs = L["inv"](27, 27, 9)
    for i_, n_ in [("Plant_Seeds_Wheat", 200), ("Plant_Seeds_Wheat_Eternal", 4), ("Ingredient_Water_Essence", 10), ("Ingredient_Life_Essence", 50)] + [(str(x), 1) for x in Tot.MOD_ITEMS]:
        Inv.give(full_cs, i_, JLong(n_))
    empty_cs = L["inv"](27, 27, 9)
    seen = {"n": 0, "max": 0, "types": set()}
    bad = []
    wide = []

    def chk(pg, what):
        r = T410.full(pg)
        seen["n"] += 1
        seen["types"] |= r["types"]
        if r["miss"] or r["unbound"]:
            bad.append((what, r["miss"][:3], r["unbound"][:3]))
        return r

    def sizes(pg, what):
        _b, b, ev = _binds(pg)
        s = _size(b, ev)
        seen["max"] = max(seen["max"], s)
        if s >= 1500000:
            bad.append((what, "packet %d" % s, ""))
    later = str(now + 600000)
    ENTRIES = [("default", "harvest_spirit:2:wider::0:pp0001,rain:1:::0:pp0002:gf"),
               ("tier5 two mods burning", "harvest_spirit:5:wider:faster:%s:pp0003,fertilizer:3:compost:storage:0:pp0013" % later),
               ("tier4 bench cap", "harvest_spirit:4:::0:pp0004,sun_blessing:2:rare::0:pp0014"),
               ("wrong shard + moon", "sap_tap:2:::0:pp0005,harvest_moon:1:::0:pp0006,scarecrow:3:faster::0:pp0007"),
               ("placed by hand", "harvest_spirit:3:wider::0:pp0008::4;-3,rain:2:::0:pp0009:gf:-4;2")]
    walked_totem = 0
    for en_name, en in ENTRIES:
        _set(L, p, "farming.i0.totems", en)
        for seeds_, auto_ in (("0", None), ("50", None), ("50", "1")):
            _set(L, p, "farming.i0.seed", seeds_)
            _set(L, p, "farming.auto", auto_)
            for inv_name, cs in (("full", full_cs), ("empty", empty_cs)):
                Page.TEST_INV = cs
                for aura in (False, True):
                    for u, who in ((ou, "owner"), (mu, "co-op")):
                        Core.AURA.clear()
                        for tp in range(4):
                            pg = PFn(FK, 1).make(None, u, SHW)
                            if pg is None:
                                bad.append(("totem page refused for %s" % who, [], []))
                                continue
                            pg.near = False
                            pg.sel = 0
                            pg.tpad = tp
                            if aura:
                                Core.auraToggle(u, OWNER, FK, 0, min(tp, 1))
                            what = "totem page %s / seeds %s auto %s / %s inventory / aura %s / %s / pad %d" % (en_name, seeds_, auto_, inv_name, aura, who, tp)
                            chk(pg, what)
                            if bool(pg.dHas):
                                _fits(pg, WTXT, wide)
                            walked_totem += 1
                            if tp == 0 and aura and inv_name == "full":
                                sizes(pg, what)
    _set(L, p, "farming.auto", None)
    _set(L, p, "farming.i0.seed", "0")
    _set(L, p, "farming.i0.totems", ENTRIES[0][1])
    Page.TEST_INV = full_cs
    # the bench: every shard, bench I-IV + upgrading, every category, every slot selected; owner + co-op; Totem Pole with hand-held totems
    ids_ = [("Ingredient_Life_Essence", 400), ("Ingredient_Fire_Essence", 200), ("Ingredient_Ice_Essence", 200), ("Skyy_Ench_Wheat", 400),
            ("Ingredient_Water_Essence", 200), ("Plant_Crop_Wheat_Item", 600)]
    T48.add_items([(i_, 100) for i_, _n in ids_])
    full_cs = L["inv"](27, 27, 27, 9)
    for i_, n_ in ids_ + [("Plant_Seeds_Wheat", 200), ("Plant_Seeds_Wheat_Eternal", 4)] + [(str(x), 1) for x in Tot.MOD_ITEMS[:3]]:
        Inv.give(full_cs, i_, JLong(n_))
    Page.TEST_INV = full_cs
    for _n in range(2):
        r_ = str(Core.craftAt(ou, OWNER, FK, [str(x) for x in Cfg.CRAFT_ID].index("Skyy_Totem_Rain"), full_cs))
        K.check(r_.startswith("+"), "O3 fixture: a hand-held Rain Totem I crafted for the Totem Pole category: %s" % r_)
    walked_bench, cells = 0, 0
    for kd in range(6):
        for u, who in ((ou, "owner"), (mu, "co-op")):
            for bt, up in ((1, False), (2, False), (2, True), (3, False), (4, False)):
                key = str(L["ShKind"].KEYS[kd])
                _set(L, p, key + ".bench", str(bt))
                _set(L, p, key + ".benchUpAt", str(now + 3600000) if up else None)
                _set(L, p, key + ".benchTo", str(bt + 1) if up else None)
                for inv_name, cs in (("full", full_cs), ("empty", empty_cs)):
                    if inv_name == "empty" and (bt, up) not in ((1, False), (4, False)):
                        continue
                    Page.TEST_INV = cs
                    pg = PFn(kd, 2).make(None, u, SHW)
                    if pg is None:
                        continue
                    for cat in range(5):
                        pg.handleDataEvent(None, None, json.dumps({"a": "bcat%d" % cat}))
                        r = chk(pg, "bench %s %s bench %d%s %s cat %d" % (key, who, bt, " (upgrading)" if up else "", inv_name, cat))
                        _fits(pg, BTXT, wide)
                        walked_bench += 1
                        if kd == FK and bt == 1 and who == "owner" and inv_name == "full" and cat == 0:
                            sizes(pg, "bench farming")
                        n = int(pg.gN)
                        for c in range(n):
                            pg.handleDataEvent(None, None, json.dumps({"a": "bg%d" % c}))
                            chk(pg, "bench %s %s bench %d %s cat %d slot %d" % (key, who, bt, inv_name, cat, c))
                            _fits(pg, BTXT, wide)
                            cells += 1
                            if int(pg.gSel) != c:
                                bad.append(("bench %s cat %d: slot %d clicked, slot %d shown selected" % (key, cat, c, int(pg.gSel)), [], []))
    for kd in range(6):
        key = str(L["ShKind"].KEYS[kd])
        for sfx in (".bench", ".benchUpAt", ".benchTo"):
            _set(L, p, key + sfx, None)
    dist = sorted(set(m_[2] for _w, ms_, _u in bad for m_ in (ms_ if isinstance(ms_, list) else [])))
    K.check(not bad, "O3 every selector exists when its command runs + every binding's element, over %d builds: %d bad, missing %s; first %s"
            % (seen["n"], len(bad), dist[:10], bad[:2]))
    K.check(walked_totem >= 380 and walked_bench >= 400 and cells >= 900, "O3 %d totem page + %d bench builds + %d slot selections walked" % (walked_totem, walked_bench, cells))
    K.check(not wide, "O3 every totem page / bench text fits its box (%d too long): %s" % (len(wide), wide[:12]))
    K.check(0 < seen["max"] < 1500000, "O3 the biggest totem / bench page packet is %d bytes" % seen["max"])
    Page.TEST_INV = None
    L["ShIsl"].LEVEL_TEST = None
    K.save()


# ---------------------------------------------------------------------------------------------------------- F3: the clicks
def run_flows3(out, jar, scratch, _home):
    from jpype import JLong
    K = HK.Child(out)
    L, ou, W, p, lv = _L(os.path.join(scratch, "f3"), K)
    Page, PFn, Cfg, Core, Inv, Tot, St, count = L["ShPage"], L["ShPageFn"], L["ShCfg"], L["ShCore"], L["ShInv"], L["ShTotem"], L["ShStore"], L["count"]
    coins = L["coins"]
    SHW = "skyy-shard-" + OWNER
    cs = L["inv"](27, 27, 9)
    Page.TEST_INV = cs
    T48.add_items([(i_, 100) for i_ in ("Ingredient_Lightning_Essence", "Ingredient_Life_Essence", "Ingredient_Water_Essence", "Plant_Seeds_Wheat",
                                        "Plant_Seeds_Wheat_Eternal", "Skyy_Ench_Wheat", "Plant_Crop_Wheat_Item") + tuple(str(x) for x in Tot.MOD_ITEMS)])

    def give(items):
        for i_, n_ in items:
            Inv.give(cs, i_, JLong(n_))

    def good(pg):
        return str(pg.stCol).lower() == GOOD.lower()
    give([("Plant_Crop_Wheat_Item", 600), ("Ingredient_Water_Essence", 60)])

    def click(pg, a, what):
        """one click as the server answers it: handleDataEvent, then (testMode: no rebuild) ONE full build - never a keep update"""
        pg.kLast = None
        pg.handleDataEvent(None, None, json.dumps({"a": a}))
        K.check(pg.kLast is None, "F3 %s: no in-place update - the click answers with one full page" % what)
        r = T410.full(pg)
        K.check(not r["miss"] and not r["unbound"], "F3 %s: the page after the click walks clean %s %s" % (what, r["miss"][:2], r["unbound"][:2]))
        return str(pg.stText)

    # ---- the bench
    pb = PFn(FK, 2).make(None, ou, SHW)
    T410.full(pb)
    K.check(int(pb.bCat) == 0 and str(pb.gTitle) == "Workers" and int(pb.gSel) >= 0, "F3 the bench opens on Workers with the first recipe picked (%s, slot %d)" % (pb.gTitle, int(pb.gSel)))
    b0, _b, _e = _binds(pb)
    K.check(b0.get("#SkyyShBCat3") == "bcat3" and b0.get("#SkyyShBG0") == "bg0" and b0.get("#SkyyShBClose") == "close", "F3 the category + slot + Close bindings: %s" % sorted(b0)[:8])
    click(pb, "bcat3", "bench Modifiers")
    mi_ids = set(str(x) for x in Tot.MOD_ITEMS)
    K.check(int(pb.bCat) == 3 and str(Cfg.CRAFT_ID[int(pb.kSel)]) in mi_ids and all(str(pb.gIt[i]) in mi_ids for i in range(int(pb.gN))),
            "F3 bcat3: the grid holds only the 6 modifiers, the first picked (%s)" % Cfg.CRAFT_ID[int(pb.kSel)])
    need = [int(pb.needOf(FK, int(pb.gRef[i]))) for i in range(int(pb.gN))]
    K.check(need == sorted(need), "F3 ... sorted by bench tier (then name): %s" % need)
    click(pb, "bg1", "bench Modifiers slot 2")
    K.check(int(pb.kSel) == int(pb.gRef[1]) and int(pb.gSel) == 1, "F3 bg1 picks the second modifier")
    give([("Skyy_Ench_Wheat", 400), ("Ingredient_Life_Essence", 400), ("Ingredient_Lightning_Essence", 100), ("Plant_Seeds_Wheat_Eternal", 2),
          ("Plant_Seeds_Wheat", 300)])
    click(pb, "bg0", "bench Modifiers slot 1")
    b1, _b, _e = _binds(pb)
    craft = b1.get("#SkyyShBCraft")
    K.check(bool(pb.qCan) == (craft == "bkcraft"), "F3 Craft is bound exactly when it can craft (qCan %s, binding %s): %s" % (pb.qCan, craft, pb.qWhy))
    mid = str(Cfg.CRAFT_ID[int(pb.kSel)])
    h0 = count(cs, mid)
    st_ = click(pb, "bkcraft", "bench Craft")
    K.check(good(pb) and count(cs, mid) == h0 + 1, "F3 Craft crafts the picked modifier: %s" % st_)
    # an empty category holds (Totem Pole without totems) and its gempty text shows
    Page.TEST_INV = L["inv"](9)
    click(pb, "bcat4", "bench Totem Pole (no totems)")
    K.check(int(pb.bCat) == 4 and int(pb.gN) == 0 and not bool(pb.qHas) and "Totem I" in str(pb.gEmpty), "F3 Totem Pole without hand-held totems: empty + says what to do: %s" % pb.gEmpty)
    Page.TEST_INV = cs
    r_ = str(Core.craftAt(L["UUID"].fromString(OWNER), OWNER, FK, [str(x) for x in Cfg.CRAFT_ID].index("Skyy_Totem_Rain"), cs))
    K.check(r_.startswith("+"), "F3 a hand-held Rain Totem I: %s" % r_)
    click(pb, "bcat4", "bench Totem Pole")
    K.check(int(pb.gN) >= 1 and bool(pb.qHas) and str(pb.qNm).startswith("Rain Totem I"), "F3 Totem Pole lists the hand-held Rain Totem I: %s" % pb.qNm)
    b2, _b, _e = _binds(pb)
    mk = b2.get("#SkyyShBMkP")
    K.check((mk or "").startswith("brup:") == bool(pb.qCan), "F3 Make pole is bound exactly when it can (qCan %s): %s / %s" % (pb.qCan, mk, pb.qWhy))
    K.check(bool(pb.qCan) and (mk or "").startswith("brup:%d:%d:1:" % (int(pb.rCi[int(pb.rSel)]), int(pb.rSi[int(pb.rSel)]))),
            "F3 Make pole carries the picked Totem I (slot, tier, uid): %s" % mk)
    st_ = click(pb, mk or "brup:", "bench Make pole (the binding's data)")
    K.check(good(pb) and st_.startswith("Rain Totem I is now Rain Totem Pole II"), "F3 Make pole tiers the hand-held totem up: %s" % st_)
    st_ = click(pb, mk or "brup:", "bench Make pole again (the old page)")
    K.check(not good(pb), "F3 ... the same old click never tiers twice: %s" % st_)
    for sfx_, v_ in ((".bench", "1"), (".benchUpAt", None), (".benchTo", None)):
        _set(L, p, "farming" + sfx_, v_)
    click(pb, "bcat0", "bench Workers again")
    K.check(int(pb.bCat) == 0, "F3 back on Workers")
    b3, _b, _e = _binds(pb)
    up = b3.get("#SkyyShBEUp")
    K.check(up == "bebench" and bool(pb.vCan) and str(pb.vTx[0]).startswith("Bench I -> II unlocks"), "F3 Upgrade bench bound exactly when it can (%s): %s / %s / %s / show %s" % (pb.vCan, up, pb.vTx[0], pb.vTx[5], pb.vShow))
    if up:
        st_ = click(pb, "bebench", "bench Upgrade")
        K.check(good(pb) and st_.startswith("Bench II"), "F3 Upgrade bench starts the upgrade: %s" % st_)
        K.check(str(pb.vTx[0]).startswith("Upgrading to Bench II") and not bool(pb.vShow), "F3 ... the side panel shows the timer, no button: %s" % pb.vTx[0])
    # ---- the totem page
    _set(L, p, "farming.i0.totems", "harvest_spirit:2:wider::0:pp0001,rain:1:::0:pp0002:gf")
    _set(L, p, "farming.i0.seed", "0")
    pt = PFn(FK, 1).make(None, ou, SHW)
    pt.near = False
    pt.sel = 0
    pt.tpad = 0
    T410.full(pt)
    bt, _b, _e = _binds(pt)
    K.check(str(pt.wName) == "Harvest Spirit Totem Pole II" and str(pt.wRar).lower() == str(Page.TQC[1]).lower() and str(pt.wTag).startswith("T2 Totem - pad 1 - "),
            "F3 the totem card: %s / %s / %s" % (pt.wName, pt.wRar, pt.wTag))
    K.check(bt.get("#SkyyShWRg") == "trange" and bt.get("#SkyyShWSdG") == "wseed" and "#SkyyShWSdT" not in bt and bt.get("#SkyyShWPick") == "tpick",
            "F3 Show range, Give seeds (you carry seeds), no Take seeds (the store is empty), Pick up: %s" % sorted(bt))
    K.check(bt.get("#SkyyShWMs0Rm") == "tmodrem1" and "#SkyyShWMs1Rm" not in bt, "F3 Remove only on the filled slot")
    h_s = count(cs, "Plant_Seeds_Wheat")
    st_ = click(pt, "wseed", "Give seeds")
    K.check(good(pt) and count(cs, "Plant_Seeds_Wheat") < h_s and int(L["ShIsl"].seeds(FK, p, 0)) > 0, "F3 Give seeds fills the island's store from the page: %s" % st_)
    bt, _b, _e = _binds(pt)
    K.check(bt.get("#SkyyShWSdT") == "wseedb", "F3 ... now Take seeds is drawn")
    st_ = click(pt, "wseedb", "Take seeds")
    K.check(good(pt) and int(L["ShIsl"].seeds(FK, p, 0)) == 0, "F3 Take seeds empties the store back: %s" % st_)
    fid = str(Tot.MOD_ITEMS[1])
    give([(fid, 2)])
    T410.full(pt)
    bt, _b, _e = _binds(pt)
    K.check(bt.get("#SkyyShWMl1Add") == "tmodadd1" and "#SkyyShWMl2Add" not in bt or count(cs, str(Tot.MOD_ITEMS[2])) > 0,
            "F3 Add is drawn on the modifiers you have: %s" % sorted(k_ for k_ in bt if "Ml" in k_))
    st_ = click(pt, "tmodadd1", "Add a picked modifier")
    K.check(good(pt) and str(Core.at(FK, p, 0, 0)[3]) == "faster", "F3 tmodadd1 adds Faster into the free slot: %s" % st_)
    bt, _b, _e = _binds(pt)
    K.check(not any("Add" in k_ for k_ in bt), "F3 ... both slots full: no Add button anywhere: %s" % [k_ for k_ in bt if "Add" in k_])
    st_ = click(pt, "tmodrem2", "Remove modifier 2")
    K.check(good(pt) and str(Core.at(FK, p, 0, 0)[3]) == "", "F3 Remove gives it back: %s" % st_)
    give([("Ingredient_Water_Essence", 5)])
    T410.full(pt)
    bt, _b, _e = _binds(pt)
    K.check(bt.get("#SkyyShWBoost") == "tboost", "F3 Add booster drawn (you carry an essence)")
    st_ = click(pt, "tboost", "Add booster")
    K.check(st_.startswith("Booster burning") and bool(pt.wBoOn), "F3 Add booster: %s" % st_)
    bt, _b, _e = _binds(pt)
    K.check("#SkyyShWBoost" not in bt and "still burning" in str(pt.wBo[2]), "F3 ... burning: no button, the reason instead: %s" % pt.wBo[2])
    up = bt.get("#SkyyShWUp")
    K.check((up or "").startswith("tup:") == bool(pt.wTuCan), "F3 Tier up bound exactly when it can (%s): %s / %s" % (pt.wTuCan, up, pt.wTu[5]))
    K.check(up is None and "stops at" in str(pt.wTu[5]) and str(pt.wTuC[5]).lower() == BAD.lower(),
            "F3 a Bench I caps a Pole II: no Tier up button, the reason in red instead (0.4.7 drew the button and refused): %s" % pt.wTu[5])
    # Tier up when it works: bench IV, the cost in hand -> the button carries island / pad / tier / type / uid, the click tiers up
    _set(L, p, "farming.bench", "4")
    f_ = Core.at(FK, p, 0, 0)
    rc_ = Core.recipe(Tot.costAt(FK, "Skyy_Totem_HarvestSpirit", Tot.doc(f_, JLong(1790000000000)).toJson()))
    T48.add_items([(str(x), 100) for x in rc_[0]])
    give([(str(i_), int(q_)) for i_, q_ in zip(rc_[0], rc_[1])])
    T410.full(pt)
    bt, _b, _e = _binds(pt)
    want = "tup:0:0:2:harvest_spirit:%s" % str(f_[5])
    K.check(bool(pt.wTuCan) and bt.get("#SkyyShWUp") == want and "-> Grand Pole III" in str(pt.wTu[0]), "F3 Tier up drawn when it works, its data %s (want %s): %s" % (bt.get("#SkyyShWUp"), want, pt.wTu[0]))
    st_ = click(pt, want, "Tier up")
    K.check(good(pt) and str(Core.at(FK, p, 0, 0)[1]) == "3", "F3 Tier up tiers the placed totem up: %s" % st_)
    st_ = click(pt, want, "Tier up again (the old page)")
    K.check(not good(pt) and str(Core.at(FK, p, 0, 0)[1]) == "3", "F3 ... the old click never tiers twice: %s" % st_)
    _set(L, p, "farming.bench", "1")
    # aura on / off / closing
    Core.AURA.clear()
    st_ = click(pt, "trange", "Show range on")
    a_ = Core.AURA.get(ou)
    K.check(a_ is not None and st_.startswith("Range") and bool(pt.wAura), "F3 Show range: the aura is on for THIS player only: %s" % st_)
    c_ = list(a_[1])
    spot = list(L["ShGeo"].totemSpot(FK, 0))
    K.check(abs(c_[0] - spot[0]) < 1e-6 and abs(c_[2] - spot[2]) < 1e-6 and int(c_[3]) == int(Tot.range(Core.at(FK, p, 0, 0), JLong(1790000000000))) and int(c_[5]) >= 1,
            "F3 ... its centre is the island centre, the radius the totem's range: %s" % c_[:6])
    bt, _b, _e = _binds(pt)
    K.check(bt.get("#SkyyShWRg") == "trange", "F3 ... the toggle stays bound (Hide range)")
    import time
    t0 = time.time() * 1000
    Cfg.AURA_SEC = 30
    pt.onDismiss(None, None)
    u_ = float(Core.AURA.get(ou)[1][4])
    K.check(t0 + 29000 <= u_ <= t0 + 31500, "F3 closing the page: the aura stays 30 s (until %d ms from now)" % (u_ - t0))
    Cfg.AURA_SEC = 0
    pt.onDismiss(None, None)
    K.check(Core.AURA.get(ou) is None, "F3 totem.rangeAuraSec 0: closing ends it at once")
    Cfg.AURA_SEC = 30
    click(pt, "trange", "Show range on again")
    st_ = click(pt, "trange", "Show range off")
    K.check(Core.AURA.get(ou) is None and st_ == "Range hidden." and not bool(pt.wAura), "F3 Hide range ends it: %s" % st_)
    # a co-op member: no owner buttons, Show range still theirs
    pm = PFn(FK, 1).make(None, L["UUID"].fromString(MEMBER), SHW)
    pm.near = False
    T410.full(pm)
    bm, _b, _e = _binds(pm)
    K.check(sorted(bm) == ["#SkyyShWClose", "#SkyyShWRg"], "F3 a co-op member gets Show range + Close only: %s" % sorted(bm))
    # a gone totem
    pt.tpad = 4
    T410.full(pt)
    bg_, _b, _e = _binds(pt)
    K.check(not bool(pt.dHas) or int(pt.tpad) < 4, "F3 a pad without a totem: the page says it is gone")
    Page.TEST_INV = None
    L["ShIsl"].LEVEL_TEST = None
    K.save()


# ---------------------------------------------------------------------------------------------------------- AU: the aura's config + engine hand-off
def run_aura(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    L, ou, W, p, lv = _L(os.path.join(scratch, "au"), K)
    Cfg, Core, PyFn = L["ShCfg"], L["ShCore"], L["PyFn"]
    K.check(int(Cfg.AURA_SEC) == 30 and str(Cfg.AURA_EDGE) == "Block_Top_Glow" and str(Cfg.AURA_CELL) == "Seed_Place_Dust", "AU the defaults: 30 s, Block_Top_Glow, Seed_Place_Dust")
    Bool = JClass("java.lang.Boolean")
    Cfg.PART_TEST = PyFn(lambda n: Bool.TRUE if str(n) in ("Block_Top_Glow", "Seed_Place_Dust", "Willow_Fruit") else Bool.FALSE)
    K.check(str(Cfg.partOr("Willow_Fruit", "Block_Top_Glow", "totem.rangeEdge")) == "Willow_Fruit", "AU partOr: a real particle system is used")
    K.check(str(Cfg.partOr("No_Such_Particle", "Block_Top_Glow", "totem.rangeEdge")) == "Block_Top_Glow", "AU partOr: an unknown name falls back to the default (one WARN)")
    K.check(str(Cfg.partOr("", "Seed_Place_Dust", "totem.rangeCell")) == "Seed_Place_Dust", "AU partOr: empty = the default")
    Cfg.PART_TEST = None
    r = int(Core.auraSet(ou, OWNER, FK, 0, 0, 123456789))
    a_ = Core.AURA.get(ou)
    K.check(r >= 3 and a_ is not None and str(a_[0]) == "skyy-shard-" + OWNER and int(a_[1][4]) == 123456789, "AU auraSet: the shard world, the range %d, the until" % r)
    K.check(int(Core.auraSet(ou, OWNER, FK, 0, 7, 1)) == -1, "AU auraSet: no totem on that pad = nothing")
    Core.auraKeep(ou, OWNER, FK, 0, 0)
    K.check(float(Core.AURA.get(ou)[1][4]) > 1.7e12, "AU auraKeep refreshes an open page's aura (10 minutes)")
    Core.AURA.clear()
    Core.auraKeep(ou, OWNER, FK, 0, 0)
    K.check(Core.AURA.get(ou) is None, "AU auraKeep never turns an aura on")
    # the tick drops an ended aura without a world call
    Core.auraSet(ou, OWNER, FK, 0, 0, 1)
    JClass(PKG + "ShTick")().run()
    K.check(Core.AURA.get(ou) is None, "AU the 1 s tick removes an aura whose time is over")
    K.check(int(JClass(PKG + "ShAura").HALF[0]) == 6 and int(JClass(PKG + "ShAura").HALF[2]) == 14, "AU ShAura's island halves = the shard grid (6 / 10 / 14)")
    K.save()



# ---------------------------------------------------------------------------------------------------------- LK: the data lock never freezes a world
def run_lock(out, jar, scratch, _home):
    import threading, time
    from jpype import JClass
    K = HK.Child(out)
    L, ou, W, p, lv = _L(os.path.join(scratch, "lk"), K)
    Page, PFn, St, Core = L["ShPage"], L["ShPageFn"], L["ShStore"], L["ShCore"]
    Lk = JClass(PKG + "ShLock")
    Thread = JClass("java.lang.Thread")
    LOCK = St.LOCK
    K.check(str(LOCK.getClass().getName()) == PKG + "ShLock", "LK ShStore.LOCK is the timed ShLock")
    LOCK.lock(); LOCK.lock(); LOCK.unlock(); LOCK.unlock()
    K.check(not LOCK.isLocked(), "LK reentrant: the same thread locks twice, unlocks twice")
    # 1. Skyy's freeze: another thread HOLDS the lock and never lets go; a world thread opens the shard page
    stop = threading.Event()
    held = threading.Event()

    def holder():
        Thread.currentThread().setName("SkyyTest-stuck-holder")
        LOCK.lock()
        held.set()
        try:
            stop.wait(10)
        finally:
            LOCK.unlock()
    th = threading.Thread(target=holder)
    th.start()
    held.wait(5)
    res = {}

    def world():
        Thread.currentThread().setName("WorldThread - skyy-island-test")
        pg = PFn(FK, 0).make(None, ou, W)
        t0 = time.time()
        b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
        ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
        try:
            pg.build(None, b, ev, None)
            res["ms"] = (time.time() - t0) * 1000
            res["walk"] = T410.walk(b.getCommands())
            res["busy"] = any("SkyyShZ" in str(c.text) for c in b.getCommands() if c.text is not None)
            res["binds"] = [str(e.selector) for e in ev.getEvents()]
            pg.handleDataEvent(None, None, json.dumps({"a": "buy"}))
            res["click"] = str(pg.stText)
        except Exception as e:
            res["err"] = repr(e)
    t0n = int(Lk.TIMEOUTS.get())
    wt = threading.Thread(target=world)
    wt.start()
    wt.join(20)
    K.check(not wt.is_alive() and "err" not in res, "LK the world thread came back (no freeze): %s" % res.get("err"))
    K.check(res.get("ms", 9999) < 400, "LK ... within %.0f ms while another thread held the lock (WORLD_MS %d)" % (res.get("ms", -1), int(Lk.WORLD_MS)))
    K.check(bool(res.get("busy")) and res.get("walk", (0, [1]))[1] == [] and res.get("binds") == ["#SkyyShZClose"],
            "LK ... the player got the small busy page (walks clean, Close bound): %s" % res.get("binds"))
    K.check("busy right now" in res.get("click", ""), "LK a click while busy says so: %s" % res.get("click"))
    K.check(int(Lk.TIMEOUTS.get()) > t0n and "SkyyTest-stuck-holder" in str(Lk.LAST), "LK one WARN names the HOLDER thread + its stack: %s" % str(Lk.LAST)[:120])
    stop.set()
    th.join(10)
    # 2. a lock-order inversion with another mod's lock (SkyySacks / SkyyIslands): both sides finish
    X = JClass("java.util.concurrent.locks.ReentrantLock")()
    done = {"a": False, "b": None}

    def side_a():   # ours: our lock, then the other mod's
        Thread.currentThread().setName("SkyyShards-tick")
        LOCK.lock()
        try:
            time.sleep(0.2)
            X.lock()
            try:
                done["a"] = True
            finally:
                X.unlock()
        finally:
            LOCK.unlock()

    def side_b():   # theirs: their lock, then a shard bridge that takes ours
        Thread.currentThread().setName("WorldThread - other-mod")
        X.lock()
        try:
            time.sleep(0.1)
            try:
                LOCK.lock()
                LOCK.unlock()
                done["b"] = "got it"
            except Exception as e:
                done["b"] = "busy" if "busy" in str(e).lower() or "ShBusy" in repr(e) else repr(e)
        finally:
            X.unlock()
    t0 = time.time()
    ta, tb = threading.Thread(target=side_a), threading.Thread(target=side_b)
    ta.start(); tb.start()
    ta.join(10); tb.join(10)
    el = time.time() - t0
    K.check(not ta.is_alive() and not tb.is_alive() and done["a"] and done["b"] == "busy" and el < 3,
            "LK a lock-order inversion breaks by itself in %.2f s: our side finished, theirs gave up on our lock (%s) - no deadlock" % (el, done["b"]))
    K.check(not LOCK.isLocked(), "LK ... and nothing is left locked")
    # 3. a non-world thread waits WAIT_MS at most
    hold2 = threading.Event()
    stop2 = threading.Event()

    def h2():
        LOCK.lock()
        hold2.set()
        try:
            stop2.wait(10)
        finally:
            LOCK.unlock()
    t2 = threading.Thread(target=h2)
    t2.start()
    hold2.wait(5)
    Thread.currentThread().setName("SkyyShards-tick")
    t0 = time.time()
    try:
        LOCK.lock()
        LOCK.unlock()
        got = "locked"
    except Exception:
        got = "busy"
    el = (time.time() - t0) * 1000
    stop2.set()
    t2.join(10)
    K.check(got == "busy" and el < int(Lk.WAIT_MS) + 600, "LK the tick thread gives up after %d ms (%s), never waits forever" % (el, got))
    # 4. the tick is on our own daemon thread
    g = open(GEN, encoding="utf8").read()
    K.check("SCHEDULED_EXECUTOR.scheduleAtFixedRate" not in g and "newSingleThreadScheduledExecutor(new @PKG@.ShThreads())" in g and "this.exec.shutdownNow()" in g,
            "LK ShTick runs on Shards' own scheduler (not HytaleServer.SCHEDULED_EXECUTOR), shut down with the plugin")
    tf = JClass(PKG + "ShThreads")().newThread(JClass("java.lang.Thread")())
    K.check(str(tf.getName()) == "SkyyShards-tick" and bool(tf.isDaemon()), "LK ... a daemon thread named SkyyShards-tick")
    K.save()


# ---------------------------------------------------------------------------------------------------------- PL: totem poles placed by hand
def run_place(out, jar, scratch, _home):
    from jpype import JLong, JClass
    K = HK.Child(out)
    L, ou, W, p, lv = _L(os.path.join(scratch, "pl"), K)
    Page, Cfg, Core, Inv, Tot, Geo = L["ShPage"], L["ShCfg"], L["ShCore"], L["ShInv"], L["ShTotem"], L["ShGeo"]
    cs = L["inv"](27, 27, 9)
    Page.TEST_INV = cs
    T48.add_items([(i_, 100) for i_ in ("Plant_Crop_Wheat_Item", "Ingredient_Life_Essence")])
    for i_, n_ in (("Plant_Crop_Wheat_Item", 900), ("Ingredient_Life_Essence", 80)):
        Inv.give(cs, i_, JLong(n_))
    ri = [str(x) for x in Cfg.CRAFT_ID].index("Skyy_Totem_HarvestSpirit")
    for _n in range(3):
        r_ = str(Core.craftAt(ou, OWNER, FK, ri, cs))
        K.check(r_.startswith("+"), "PL fixture: a Harvest Spirit Totem Pole I crafted: %s" % r_)

    def poles():
        return [list(x) for x in Inv.totems(cs) if str(x[2]) == "Skyy_Totem_HarvestSpirit"]
    _set(L, p, "farming.i0.totems", None)
    _set(L, p, "farming.i0.size", "3")
    a0 = poles()[0]
    n_all = len(poles())
    K.check(str(Core.placeHere(ou, OWNER, FK, 0, int(a0[0]), int(a0[1]), 0, 1, cs)).startswith("-The island's centre holds"), "PL the centre 3 x 3 (the pads) is refused")
    K.check(str(Core.placeHere(ou, OWNER, FK, 0, int(a0[0]), int(a0[1]), 14, 2, cs)).startswith("-That spot is off the island"), "PL the rim / outside is refused")
    r = str(Core.placeHere(ou, OWNER, FK, 0, int(a0[0]), int(a0[1]), 6, -4, cs))
    e = [str(x) for x in Tot.entries(FK, p, 0)]
    K.check(r.startswith("+Placed Harvest Spirit Totem Pole I here on island 1") and len(e) == 1 and e[0].endswith("::6;-4") and len(poles()) == n_all - 1,
            "PL placed by hand at (6, -4): the item taken, the entry carries its spot: %s / %s" % (r, e))
    f = Tot.parse(e[0])
    K.check(list(Tot.posOf(f)) == [6, -4] and str(Tot.fmt(f)) == e[0], "PL parse / fmt keep the spot (round trip)")
    old = "harvest_spirit:2:wider::0:pp0001"
    K.check(str(Tot.fmt(Tot.parse(old))) == old and str(Tot.fmt(Tot.parse(old + ":gf"))) == old + ":gf" and Tot.posOf(Tot.parse(old)) is None,
            "PL a pad entry is byte-identical (the 0.4.12 form), no spot")
    rr = int(Tot.range(f, JLong(1790000000000)))
    K.check(int(Tot.covOf(3, f, rr)) == int(Tot.covAt(3, rr, 6, -4)) and int(Tot.covAt(3, rr, 0, 0)) == int(Tot.cov(3, rr)),
            "PL its coverage is counted around its spot (covAt(0, 0) = the old centred table)")
    wr = float(Tot.workerRate(FK, f, 3, JLong(1790000000000)))
    K.check(wr > 0, "PL it works: %.3f items / min" % wr)
    cx, cz = int(Geo.ox(FK)) + int(Geo.SX[0]), int(Geo.OZ) + int(Geo.SZ[0])
    sp = [int(x) for x in Geo.spotOf(FK, p, 0, 0)]
    K.check(sp == [cx + 6, int(Geo.Y) + 1, cz - 4], "PL its block stands on its spot: %s" % sp)
    lst = JClass("java.util.ArrayList")()
    Geo.pads(lst, FK, p, 0)
    cells = [[int(v) for v in x] for x in lst]
    K.check([cx + 6, int(Geo.Y) + 1, cz - 4] in [c_[:3] for c_ in cells if c_[3] >= int(Geo.TOTEM)] and all(c_[3] == int(Geo.AIR) for c_ in cells[:5]),
            "PL the region paint puts its totem block there, every pad stays empty")
    K.check([int(x) for x in Core.nearest(p, FK, float(cx + 6) + 0.5, float(cz - 4) + 0.5)] == [0, 0], "PL right-clicking it opens ITS page (nearest = its spot)")
    a1 = poles()[0]
    K.check(str(Core.placeHere(ou, OWNER, FK, 0, int(a1[0]), int(a1[1]), 6, -4, cs)).startswith("-Another totem stands right there"), "PL never on another totem")
    K.check([int(x) for x in Core.spotFor(p, FK, cx + 3, cz - 9)] == [0, 3, -9] and Core.spotFor(p, FK, cx + 40, cz) is None, "PL spotFor: a block column -> its island + spot (none beside the island)")
    Core.AURA.clear()
    K.check(int(Core.auraSet(ou, OWNER, FK, 0, 0, 1)) == rr and [float(x) for x in Core.AURA.get(ou)[1]][6:8] == [6.0, -4.0], "PL its aura is drawn around its own spot")
    Core.AURA.clear()
    pt = L["ShPageFn"](FK, 1).make(None, ou, "skyy-shard-" + OWNER)
    pt.near = False
    pt.sel = 0
    pt.tpad = 0
    r_ = T410.full(pt)
    K.check(not r_["miss"] and int(pt.wPic) == -1 and "placed by hand" in str(pt.wTag) and "Placed by hand at 6, -4" in str(pt.wRgCap), "PL its page: placed by hand, no centred picture: %s" % pt.wTag)
    n0 = len(poles())
    r = str(Core.pickTotem(ou, OWNER, FK, 0, 0, cs))
    K.check(r.startswith("+Harvest Spirit Totem Pole I is in your inventory") and len(Tot.entries(FK, p, 0)) == 0 and len(poles()) == n0 + 1, "PL Pick up gives it back: %s" % r)
    _set(L, p, "farming.i0.size", "1")
    lim = int(L["ShMath"].pads(1))
    got, r = 0, ""
    for _n in range(lim + 1):
        a_ = poles()
        if not a_:
            break
        r = str(Core.placeHere(ou, OWNER, FK, 0, int(a_[0][0]), int(a_[0][1]), 2 + _n, 3, cs))
        got += 1 if r.startswith("+") else 0
    K.check(got == min(lim, 3) and (got < lim or got == 3 or r.startswith("-This island has all its totems")), "PL a Small island takes %d totems by hand (limit %d): %s" % (got, lim, r))
    Page.TEST_INV = None
    K.save()


# ---------------------------------------------------------------------------------------------------------- BZ: a busy lock never loses anything
# (research/Shards-0.4.13-Review.md 1-5): EXECUTED with a real second thread holding ShStore.LOCK while the calling thread is a "WorldThread"
# (50 ms). The holder starts from INSIDE the first Pocket Dimension count of the click (sacks:fn:count = needTxt / haveAll, after the early
# reads) - exactly where the first 0.4.13 build paid and then met the busy lock.
def run_busy(out, jar, scratch, _home):
    import threading, time
    from jpype import JClass, JInt, JLong
    K = HK.Child(out)
    L = T411._L(os.path.join(scratch, "bz"), K)
    St, Isl, Core, Door, Cfg, Page, Inv, Tot, Geo, Kind = (L[n] for n in ("ShStore", "ShIsl", "ShCore", "ShDoor", "ShCfg", "ShPage", "ShInv", "ShTotem", "ShGeo", "ShKind"))
    inv, count, UUID, coins, PyFn, br, fns = (L[n] for n in ("inv", "count", "UUID", "coins", "PyFn", "br", "fns"))
    Thread = JClass("java.lang.Thread")
    LOCK = St.LOCK
    bags = T412._bags(L)
    ou = UUID.fromString(OWNER)
    W = "skyy-island-" + OWNER
    now = 1790000000000
    Core.NOW_TEST = now
    Isl.LEVEL_TEST = PyFn(lambda a: JInt(99))
    Door.door(ou, OWNER, "farming", W, 29, 129, -31)
    p = St.get(OWNER)
    _set(L, p, "farming.bench", "1")
    K.check(p is not None and int(Core.benchTier(FK, p, JLong(now))) == 1, "BZ fixture: the owner's Farming shard, Totem Bench I")
    hold = {"stop": None, "t": None}

    def grab():
        """another thread takes the lock and keeps it until release()"""
        held, stop = threading.Event(), threading.Event()

        def h():
            Thread.currentThread().setName("SkyyTest-bz-holder")
            while not LOCK.tryLock():
                time.sleep(0.002)
            held.set()
            try:
                stop.wait(15)
            finally:
                LOCK.unlock()
        t = threading.Thread(target=h)
        t.start()
        held.wait(5)
        hold["stop"], hold["t"] = stop, t

    def release():
        if hold["stop"] is not None:
            hold["stop"].set()
            hold["t"].join(10)
        hold["stop"] = hold["t"] = None
    arm = {"on": False}
    c0 = br.get("sacks:fn:count")

    def cnt(a):
        if arm["on"]:
            arm["on"] = False
            grab()
        return c0.apply(a)
    br.put("sacks:fn:count", PyFn(cnt))
    me = str(Thread.currentThread().getName())

    def busy_call(fn):
        """fn() on a "WorldThread" with the holder armed at the first bag count: (result, busy?)"""
        arm["on"] = True
        Thread.currentThread().setName("WorldThread - skyy-island-bz")
        r, b = None, False
        try:
            r = str(fn())
        except Exception as e:
            b = "ShBusy" in repr(e) or "ShBusy" in str(type(e)) or "busy" in str(e).lower()
            r = repr(e)[:160]
        finally:
            Thread.currentThread().setName(me)
            arm["on"] = False
            release()
        return r, b

    def snap():
        return (dict(bags["have"]), T412._owed(bags), dict(bags["committed"]), coins["bal"])
    cs = inv(27, 27, 9)
    Page.TEST_INV = cs
    # ---- 1. benchUp: busy at the payment = nothing taken (bag items, coins, the bench)
    bt = Core.recipe(Cfg.benchItems(2, FK).strip())
    bids, bq = [str(x) for x in bt[0]], [int(x) for x in bt[1]]
    bags["have"] = dict(zip(bids, bq))
    s0 = snap()
    r, b = busy_call(lambda: Core.benchUp(ou, OWNER, FK, cs))
    K.check(b and snap() == s0 and p.getProperty("farming.benchUpAt") is None and str(p.getProperty("farming.bench") or "1") == "1",
            "BZ benchUp meets a busy lock at the payment: ShBusy, NOTHING taken (bag items %s, coins %d, bench unchanged): %s" % (bags["have"], coins["bal"], r))
    r = str(Core.benchUp(ou, OWNER, FK, cs))
    K.check(r.startswith("+Bench II") and all(bags["have"][i_] == 0 for i_ in bids) and coins["bal"] <= s0[3] and T412._owed(bags) == 0, "BZ ... then (free lock) the upgrade goes through: %s" % r)
    _set(L, p, "farming.bench", "4")
    _set(L, p, "farming.benchTo", None)
    _set(L, p, "farming.benchUpAt", None)
    # ---- 2. tierUpPlaced (a pad totem): busy at the payment = nothing taken, the totem unchanged
    ent = "harvest_spirit:1:::0:bz0001"
    _set(L, p, "farming.i0.totems", ent)
    ti = [str(x) for x in Tot.KEYS].index("harvest_spirit")
    c = str(Tot.costAt(FK, Tot.ITEMS[ti], Tot.doc(Tot.onPad(ent), JLong(now)).toJson()))
    rc = Core.recipe(c)
    tids, tq = [str(x) for x in rc[0]], [int(x) for x in rc[1]]
    bags["have"] = dict(zip(tids, tq))
    s0 = snap()
    r, b = busy_call(lambda: Core.tierUpPlaced0(ou, OWNER, FK, 0, 0, 1, "harvest_spirit", "bz0001", cs))
    K.check(b and snap() == s0 and [str(x) for x in Tot.entries(FK, p, 0)] == [ent], "BZ tierUpPlaced meets a busy lock at the payment: ShBusy, nothing taken, still tier I: %s" % r)
    r = str(Core.tierUpPlaced0(ou, OWNER, FK, 0, 0, 1, "harvest_spirit", "bz0001", cs))
    K.check(r.startswith("+") and str(Tot.entries(FK, p, 0)[0]).startswith("harvest_spirit:2:") and all(bags["have"][i_] == 0 for i_ in tids), "BZ ... then it tiers up: %s" % r)
    # ---- 3. a HAND-PLACED totem tiers up on its spot (the 8th part kept; no pad, no stale block)
    T48.add_items([(i_, 100) for i_ in ("Plant_Crop_Wheat_Item", "Ingredient_Life_Essence")])
    for i_, n_ in (("Plant_Crop_Wheat_Item", 900), ("Ingredient_Life_Essence", 80)):
        Inv.give(cs, i_, JLong(n_))
    ri = [str(x) for x in Cfg.CRAFT_ID].index("Skyy_Totem_HarvestSpirit")
    bags["have"] = {}
    r = str(Core.craftAt(ou, OWNER, FK, ri, cs))
    K.check(r.startswith("+"), "BZ fixture: a Harvest Spirit Totem Pole I crafted: %s" % r)
    _set(L, p, "farming.i0.totems", None)
    _set(L, p, "farming.i0.size", "3")
    a0 = [list(x) for x in Inv.totems(cs) if str(x[2]) == "Skyy_Totem_HarvestSpirit"][0]
    r = str(Core.placeHere(ou, OWNER, FK, 0, int(a0[0]), int(a0[1]), 6, -4, cs))
    e0 = [str(x) for x in Tot.entries(FK, p, 0)]
    K.check(r.startswith("+Placed") and len(e0) == 1 and e0[0].endswith("::6;-4"), "BZ fixture: placed by hand at (6, -4): %s" % e0)
    f0 = Tot.parse(e0[0])
    uid = str(f0[5])
    sp0 = [int(x) for x in Geo.spotOf(FK, p, 0, 0)]
    c = str(Tot.costAt(FK, Tot.ITEMS[ti], Tot.doc(Tot.onPad(e0[0]), JLong(now)).toJson()))
    rc = Core.recipe(c)
    bags["have"] = dict(zip([str(x) for x in rc[0]], [int(x) for x in rc[1]]))
    r = str(Core.tierUpPlaced0(ou, OWNER, FK, 0, 0, 1, "harvest_spirit", uid, cs))
    e1 = [str(x) for x in Tot.entries(FK, p, 0)]
    f1 = Tot.parse(e1[0]) if e1 else None
    K.check(r.startswith("+") and len(e1) == 1 and e1[0].startswith("harvest_spirit:2:") and e1[0].endswith(":" + uid + "::6;-4"),
            "BZ a hand-placed totem tiers up and its entry still ends in its spot ('::6;-4', 8 parts): %s / %s" % (r, e1))
    K.check(f1 is not None and list(Tot.posOf(f1)) == [6, -4] and str(Tot.fmt(f1)) == e1[0] and [int(x) for x in Geo.spotOf(FK, p, 0, 0)] == sp0,
            "BZ ... posOf unchanged (6, -4), fmt round trip, its block spot unchanged %s" % sp0)
    lst = JClass("java.util.ArrayList")()
    Geo.pads(lst, FK, p, 0)
    cells = [[int(v) for v in x] for x in lst]
    K.check(sp0 in [c_[:3] for c_ in cells if c_[3] >= int(Geo.TOTEM)] and all(c_[3] == int(Geo.AIR) for c_ in cells[:5]),
            "BZ ... the paint keeps its block on its spot and every pad empty (no pad totem, no stale block)")
    # ---- 4. craft a shard: busy at the payment = nothing taken, no crafted mark
    fns.put("rebirth:fn:count", PyFn(lambda k_: JInt(5)))
    ris = [(i, int(Kind.ofShard(x))) for i, x in enumerate(Cfg.CRAFT_ID) if int(Kind.ofShard(x)) >= 0 and not bool(Core.hasShard(OWNER, int(Kind.ofShard(x))))]
    K.check(bool(ris), "BZ fixture: a shard recipe the profile may craft: %s" % ris[:3])
    if ris:
        ri, sk = ris[0]
        Cfg.CRAFT[ri] = "Plant_Crop_Wheat_Item:10;100"   # the shard recipes are off by default (0.4.6) - an admin re-adds one
        rc = Core.recipe(Cfg.CRAFT[ri])
        sids, sq = [str(x) for x in rc[0]], [int(x) for x in rc[1]]
        T48.add_items([(i_, 100) for i_ in sids])
        bags["have"] = dict(zip(sids, sq))
        sid = str(Kind.SHARD[sk])
        mk = str(Kind.KEYS[sk]) + ".crafted"
        s0 = snap() + tuple(count(cs, i_) for i_ in sids)
        r, b = busy_call(lambda: Core.craftAt(ou, OWNER, FK, ri, cs))
        K.check(b and snap() + tuple(count(cs, i_) for i_ in sids) == s0 and p.getProperty(str(mk)) is None and count(cs, sid) == 0,
                "BZ craft %s meets a busy lock at the payment: ShBusy, nothing taken, no crafted mark, no shard: %s" % (sid, r))
        r = str(Core.craftAt(ou, OWNER, FK, ri, cs))
        K.check(r.startswith("+Crafted") and str(p.getProperty(str(mk))) == "1" and count(cs, sid) == 1 and sum(count(cs, i_) + bags["have"].get(i_, 0) for i_ in sids) == sum(s0[4:]) + sum(s0[0].get(i_, 0) for i_ in sids) - sum(sq),
                "BZ ... then it is crafted (mark saved, one shard): %s / %s=%s, %d shard(s), bags %s" % (r, mk, p.getProperty(str(mk)), count(cs, sid), bags["have"]))
    # ---- 5. the Collect credits (owed / owedXp): a busy lock keeps them in memory, paid later - never lost, never twice
    got = {"coll": 0, "xp": 0, "ok": True, "arm": False}

    def coll_add(a):
        if got["arm"]:
            got["arm"] = False
            grab()
        if not got["ok"]:
            return L["Bool"].FALSE
        got["coll"] += int(a[2])
        return L["Bool"].TRUE

    def xp_add(a):
        if got["arm"]:
            got["arm"] = False
            grab()
        if not got["ok"]:
            return L["Bool"].FALSE
        got["xp"] += int(a[2])
        return L["Bool"].TRUE
    fns.put("coll:fn:add", PyFn(coll_add))
    fns.put("skill:fn:addxp", PyFn(xp_add))
    IT = "Plant_Crop_Wheat_Item"
    mkey = OWNER + "|owed.coll." + IT
    xkey = OWNER + "|owed.xp"
    Core.MEM_OWED.clear()

    def wt(fn):
        Thread.currentThread().setName("WorldThread - skyy-island-bz")
        try:
            return int(fn())
        finally:
            Thread.currentThread().setName(me)

    def mem(k_):
        v = Core.MEM_OWED.get(k_)
        return None if v is None else int(v)
    # 5a. the first lock busy: all of it waits
    grab()
    try:
        r1 = wt(lambda: Core.owed(ou, IT, JLong(50)))
        r2 = wt(lambda: Core.owedXp(ou, "Farming", JLong(70)))
    finally:
        release()
    K.check(r1 == 50 and r2 == 70 and got["coll"] == 0 and got["xp"] == 0 and mem(mkey) == 50 and mem(xkey) == 70,
            "BZ owed / owedXp meet a busy lock: 50 collection + 70 XP wait in memory (returned as waiting): %d / %d, mem %s / %s" % (r1, r2, mem(mkey), mem(xkey)))
    r1, r2 = int(Core.owed(ou, IT, JLong(0))), int(Core.owedXp(ou, "Farming", JLong(0)))
    K.check(r1 == 0 and r2 == 0 and got["coll"] == 50 and got["xp"] == 70 and mem(mkey) is None and mem(xkey) is None,
            "BZ ... the next Collect pays exactly them (50 + 70), memory empty: %d / %d, paid %s, mem %s / %s" % (r1, r2, got, mem(mkey), mem(xkey)))
    # 5b. the second lock busy after a refused credit: the file part + the new part both still wait
    _set(L, p, "owed.coll." + IT, "30")
    _set(L, p, "owed.xp", "40")
    got["ok"] = False
    got["arm"] = True
    r1 = wt(lambda: Core.owed(ou, IT, JLong(50)))
    release()
    got["arm"] = True
    r2 = wt(lambda: Core.owedXp(ou, "Farming", JLong(60)))
    release()
    got["ok"] = True
    K.check(r1 == 80 and r2 == 100 and str(p.getProperty("owed.coll." + IT)) == "30" and str(p.getProperty("owed.xp")) == "40" and mem(mkey) == 50 and mem(xkey) == 60,
            "BZ refused + busy on the write-back: the file keeps 30 / 40, memory the new 50 / 60 (%d / %d waiting)" % (r1, r2))
    c0_, x0_ = got["coll"], got["xp"]
    Core.owed(ou, IT, JLong(0)); Core.owedXp(ou, "Farming", JLong(0))
    K.check(got["coll"] - c0_ == 80 and got["xp"] - x0_ == 100 and p.getProperty("owed.coll." + IT) is None and p.getProperty("owed.xp") is None and mem(mkey) is None and mem(xkey) is None,
            "BZ ... the next Collect pays 80 + 100 exactly once, file + memory empty")
    # 5c. PAID but the write-back busy: the old file count is cancelled in memory (never paid twice)
    _set(L, p, "owed.coll." + IT, "30")
    got["arm"] = True
    r1 = wt(lambda: Core.owed(ou, IT, JLong(50)))
    release()
    c1_ = got["coll"]
    K.check(r1 == 0 and c1_ - c0_ - 80 == 80 and str(p.getProperty("owed.coll." + IT)) == "30" and mem(mkey) == -30,
            "BZ paid 80 (50 + the file's 30), the write-back busy: memory -30 cancels the file's 30 (%s)" % mem(mkey))
    r1 = int(Core.owed(ou, IT, JLong(10)))
    K.check(r1 == 0 and got["coll"] - c1_ == 10 and p.getProperty("owed.coll." + IT) is None and mem(mkey) is None,
            "BZ ... the next Collect pays only its own 10 (the 30 never twice), file + memory clean")
    # ---- 6. the first load of a profile meets a busy lock: nothing cached half-migrated, the next get migrates it
    k2 = OWNER + "-p7"
    open(os.path.join(L["sd"], k2 + ".properties"), "w", encoding="latin-1").write("pkey=%s\nfarming.bench=1\n" % k2)
    K.check(not bool(St.CACHE.containsKey(k2)), "BZ fixture: an unloaded profile file %s" % k2)
    grab()
    Thread.currentThread().setName("WorldThread - skyy-island-bz")
    gb = None
    try:
        St.get(k2)
        gb = "no busy"
    except Exception as e:
        gb = "busy" if "ShBusy" in repr(e) or "busy" in str(e).lower() else repr(e)
    finally:
        Thread.currentThread().setName(me)
        release()
    K.check(gb == "busy" and not bool(St.CACHE.containsKey(k2)), "BZ ShStore.get of a new profile while busy: ShBusy, NOT cached unmigrated (%s)" % gb)
    q2 = St.get(k2)
    K.check(q2 is not None and str(q2.getProperty("forms")) == "1" and bool(St.CACHE.containsKey(k2)), "BZ ... the next get loads AND migrates it (forms=1)")
    # ---- 7. grow0 / ShPlace / the tick: a busy lock never masks itself or loses a check
    g = open(GEN, encoding="utf8").read()
    K.check("finally { if (held) @PKG@.ShStore.LOCK.unlock(); }" in g and "finally { @PKG@.ShStore.LOCK.lock(); held = true; }" in g, "BZ grow0's re-lock tracks a held flag (no IllegalMonitorStateException over ShBusy)")
    Pl = JClass(PKG + "ShPlace")
    Pl.PENDING.clear()
    from jpype import JArray, JObject
    a = JArray(JObject)([JClass("java.lang.String")(W), JClass("java.lang.Integer")(1), JClass("java.lang.Integer")(2), JClass("java.lang.Integer")(3), JClass("java.lang.Long")(now), ou])
    grab()
    Thread.currentThread().setName("WorldThread - skyy-island-bz")
    try:
        ok = bool(Pl.undo(OWNER, a, JLong(now)))
    finally:
        Thread.currentThread().setName(me)
        release()
    K.check(not ok and bool(Pl.PENDING.containsKey(OWNER)), "BZ ShPlace: a busy unplace puts the placement check back in PENDING (checked again a second later)")
    Pl.PENDING.clear()
    K.check("catch (@PKG@.ShBusy b) { continue; }   // 0.4.13 review: busy = next second\n        LAST_REGROW.put(nm" in g, "BZ ShTick: the regrow timestamp moves only after the mask")
    Isl.LEVEL_TEST = None
    Page.TEST_INV = None
    br.put("sacks:fn:count", c0)
    K.save()


# ---------------------------------------------------------------------------------------------------------- the 0.4.12 phases on the 0.4.13 jar
def run_players48(out, jar, scratch, home):
    """the map migration's collect.log line names the RUNNING version: 0.4.13 now"""
    SUP(("P one collect.log line with the Undo",), lambda: T48.run_players(out, jar, os.path.join(scratch, "p48"), home))
    d_ = json.load(open(out))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = d_["ok"], d_["fails"], d_["notes"]
    txt = ""
    for root, _d, fs in os.walk(os.path.join(scratch, "p48")):
        for f_ in fs:
            if f_ == "collect.log":
                txt += open(os.path.join(root, f_), encoding="utf8").read()
    K.check("map migration (SkyyShards 0.4.13) 0a0a0a0a-1111-2222-3333-000000000001" in txt and "Undo:" in txt,
            "P the map migration's collect.log line (running version 0.4.13) with the Undo")
    K.save()


EXPECT = {   # 0.4.12 -> 0.4.13, checked by hand 2026-10-26: the version texts (CfgFn / CfgRows / CfgFile, ShStore log lines, the ready line), the
    # three config rows (ShCfg), the aura (ShCore + ShTick + ShAura), the two pages (ShPage: the new fields + fills + the click handlers + the busy
    # page), the timed lock (ShStore.LOCK = ShLock, our own tick thread: SkyyShardsPlugin), the hand-placed poles (ShTotem parse / fmt / covAt,
    # ShGeo pads / spotOf, ShCore placeAt / spotFor / nearest / pickTotem, ShWorld2 clearAt, ShHand placeHand / use)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'ShCfg': ['+f AURA_CELL', '+f AURA_EDGE', '+f AURA_SEC', '+m partOr', '~<clinit>', '~m loadCfg', '~m writeDefaults'],
    'ShCore': ['+f AURA', '+f AURA_OPEN_MS', '+m auraClose', '+m auraKeep', '+m auraOn', '+m auraSet', '+m auraToggle', '+m memAdj', '+m placeAt', '+m placeHere', '+m spotFor', '~<clinit>',
               '~m benchUp', '~m craft', '~m grow0', '~m nearest', '~m owed', '~m owedXp', '~m pickTotem', '~m tierUpPlaced0'],   # review fixes: benchUp / craft / tierUpPlaced0 / owed* / grow0
    'ShCheck': ['~m run'],
    'ShLv20': ['~m grant'],
    'ShPlace': ['+m undo', '~m verify'],
    'ShGeo': ['+m spotOf', '~m pads'],
    'ShHand': ['+m placeHand', '~m use'],
    'ShPage': ['+f BARW', '+f BUSY', '+f CATS', '+f RPB', '+f RPM', '+f TQC', '+f TQN', '+f WEATHER', '+f bCat', '+f bHold', '+f gDot', '+f gEd', '+f gEmpty', '+f gIt', '+f gLk', '+f gN', '+f gRef', '+f gSel', '+f gTitle', '+f qBag', '+f qCan', '+f qCo', '+f qCoC', '+f qDs', '+f qHas', '+f qIn', '+f qInC', '+f qInIt', '+f qInTx', '+f qIt', '+f qNm', '+f qRar', '+f qTag', '+f qWhy', '+f qWhyC', '+f rCost', '+f rTy', '+f vCC', '+f vCIt', '+f vCTx', '+f vCan', '+f vCn', '+f vEd', '+f vIt', '+f vN', '+f vPip', '+f vShow', '+f vTx', '+f vTxC', '+f wAura', '+f wBarF', '+f wBo', '+f wBoC', '+f wBoCan', '+f wBoIt', '+f wBoOn', '+f wItem', '+f wMAdd', '+f wMEf', '+f wMEfC', '+f wMHas', '+f wMIt', '+f wMNm', '+f wMNmC', '+f wMRem', '+f wMdC', '+f wMl', '+f wMlC', '+f wName', '+f wOut', '+f wOut2', '+f wOut3', '+f wOut3C', '+f wOutC', '+f wOutU', '+f wOutW', '+f wPic', '+f wRar', '+f wRgCap', '+f wRgTx', '+f wRole', '+f wSd', '+f wSdC', '+f wSdGive', '+f wSdTake', '+f wTag', '+f wTu', '+f wTuC', '+f wTuCan', '+m before', '+m build0', '+m buildBusy', '+m catList', '+m catOf', '+m fillBenchGrid', '+m fillBenchSide', '+m fillPickCraft', '+m fillPickPole', '+m fillTotemPage', '+m needOf', '+m onDismiss', '+m qSlots', '+m shortN', '+m weather', '~<clinit>', '~c ', '~c ', '~m act', '~m actBench', '~m build', '~m buildBench', '~m buildTotem', '~m fillBench', '~m fillBenchTier', '~m fillTotems', '~m handleDataEvent'],
    'ShStore': ['~<clinit>', '~m get', '~m migrate', '~m migrate2', '~m save'],
    'ShTick': ['~m run'],
    'ShTotem': ['+f HALFS', '+m covAt', '+m covOf', '+m posOf', '~<clinit>', '~m fmt', '~m parse', '~m workerRate'],
    'ShWorld2': ['+m clearAt'],
    'SkyyShardsPlugin': ['+f exec', '~m setup', '~m shutdown'],
}
_ORIG_COMPARE = T411._ORIG_COMPARE
RANGE_PIC = re.compile(r"\ACommon/UI/Custom/SkyyShards/Map/Range/S[123]R\d+@2x\.png\Z")


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the only new non-class files: the range pictures; the classes as EXPECT"""
    import zipfile as _zf
    with _zf.ZipFile(jar) as a, _zf.ZipFile(old_jar) as b:
        na = dict((n_, a.read(n_)) for n_ in a.namelist() if not n_.endswith(".class"))
        nb = dict((n_, b.read(n_)) for n_ in b.namelist() if not n_.endswith(".class"))
    ch = sorted(n_ for n_ in set(na) | set(nb) if na.get(n_) != nb.get(n_) and n_ != "manifest.json" and not RANGE_PIC.match(n_))
    newp = sorted(n_ for n_ in na if RANGE_PIC.match(n_) and n_ not in nb)
    assert not ch, "C non-class files differ: %s" % ch[:8]
    assert len(newp) == 43, "C the range pictures: %d" % len(newp)
    print("C. %d non-class files identical (manifest.json aside) + %d new range pictures" % (len(nb), len(newp)))
    cps = []
    for j, tag in ((jar, VERSION), (old_jar, "old")):
        cp = os.path.join(SCRATCH, "compare-%s.jar" % tag)
        with _zf.ZipFile(j) as zi, _zf.ZipFile(cp, "w", _zf.ZIP_DEFLATED) as zo:
            for n_ in zi.namelist():
                if not T49.MAP_ENTRY.match(n_):
                    zo.writestr(n_, zi.read(n_))
        cps.append(cp)
    _ORIG_COMPARE(out, cps[0], cps[1], pkg, expect, added, removed)


HK.run_compare = _compare


def _p(fn, sup=()):
    return lambda out, jar, scratch, home: SUP(tuple(sup), lambda: fn(out, jar, os.path.join(scratch, "p412"), home))


SUP413 = ()
SUP47 = ("X the rebuilt page carries tier 2", "X the page's Tier up click carries", "X the bench's Make pole tab lists only", "X the Make pole click carries")
# 0.4.13: Tier up is drawn only when it works (F3 checks its data + click); Make pole is the bench's Totem Pole category (bCat 4, #SkyyShBMkP - F3)   # 0.4.13: a bench-capped Tier up is not drawn (the reason is - "only buttons you can use"); flows3 checks it
_b47 = T411.T47._build


class _Datas(dict):
    def __missing__(self, k):
        return ""


def _build47(pg):
    """0.4.7's page build, a missing binding = "" (its check is superseded above; the clicks after it run as before)"""
    r = _b47(pg)
    r["datas"] = _Datas(r["datas"])
    return r


T411.T47._build = _build47


if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ShAura", "ShBusy", "ShClear", "ShLock", "ShThreads"],
           phases=[("static", run_static), ("lock", run_lock), ("busy", run_busy), ("place", run_place), ("walk3", run_walk3), ("flows3", run_flows3), ("aura", run_aura),
                   ("bags", _p(T412.run_bags, SUP413)),
                   ("exec48", _p(T49.run_exec48, SUP413)), ("exec47", _p(T49.run_exec47, SUP47)), ("exec46", _p(T49.run_exec46, SUP413)),
                   ("centre47", _p(T49.run_centre47, SUP413)), ("config48", _p(T49.run_config48, SUP413)), ("mig48", _p(T410.run_mig48, SUP413)),
                   ("players48", _p(run_players48, SUP413)), ("geo48", _p(T49.run_geo48, SUP413)), ("config49", _p(T49.run_config, SUP413)),
                   ("mig49", _p(T49.run_mig, SUP413)), ("exec49", _p(T49.run_exec, SUP413)), ("page49", _p(T49.run_page, SUP413)),
                   ("width", _p(T49.run_width, SUP413)), ("order", _p(T410.run_order, SUP413)), ("flows", _p(T410.run_flows, SUP413)),
                   ("zones", _p(T411.run_zones, SUP413)), ("balance", _p(T411.run_balance, SUP413)), ("land", _p(T411.run_land, SUP413)),
                   ("night", _p(T411.run_night, SUP413)), ("spawn", _p(T411.run_spawn, SUP413)), ("buy", _p(T411.run_buy, SUP413)),
                   ("config", _p(T411.run_config, SUP413)), ("gate", _p(T411.run_gate, SUP413)), ("order2", _p(T411.run_order2, SUP413)),
                   ("live", T411.run_live411)],
           script=__file__, live=(T46.LIVE_SH, "mods/Skyy_SkyyShards"))
