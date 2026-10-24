"""Harness for SkyyShards 0.4.7 (tier up on the totem's own page; the bench = craft + Make pole; the totem in the island's middle;
tools/shards_0_4_7_patch.py). Build first:
    python tools/shards_0_4_7_patch.py && python SkyyShards/build_skyyshards_0.4.7.py
    python SkyyShards/test_skyyshards_0.4.7.py

  S    static   the patch re-runs to identical bytes; no new registerSystem / registerCommand; ShCore.upgrade gone
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.6 -> 0.4.7: exactly the planned members differ (EXPECT)
  X46  regress  the 0.4.6 harness's EXEC phase on the 0.4.7 jar (level 20 shards, buying islands, the Islands tab)
  X    exec     THE PAGE TIER UP on real SimpleItemContainers + a Magic Bags stub (sacks:fn:count / take / put / commit): the rows
                ('Tier up: <cost>' + one '(you have N)' row per ingredient, green / red), the click carries what the page showed, not
                enough = nothing taken, inventory first then bags, double click = once, the bench cap, a refused save / a short bag
                take / a record changed meanwhile = everything back, co-op refused (and no buttons), the Totems tab button too;
                THE BENCH: Make pole lists only hand-held Totem I items, a pole totem is refused there, a hand-held one still works
  G    centre   the totem in the middle: pad 1 = the centre, no pillar on a new island; an existing (0.4.6) island painted on a block
                map: the pillar top + the old pad-1 totem block cleared, the totem re-seated on the centre, pads 2-5 untouched, a
                foreign block kept, the marker saved - and a second paint touches nothing (once only)
  D    live     the 0.4.6 START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.7"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shards047", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.6.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.6.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_7_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_6", os.path.join(HERE, "test_skyyshards_0.4.6.py"))
T46 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T46)
sys.argv[:] = _argv
T46.JAR = JAR          # the 0.4.6 fixture / exec phase run on THIS jar
OWNER, MEMBER = T46.OWNER, T46.MEMBER
FK = 2


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.7 - build script') and g.count('VERSION = "0.4.7"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check("ShCore.upgrade(" not in g and "Tier up at the Totem Bench" not in g and "tierUpPlaced" in g, "S the bench pointer is gone, tierUpPlaced is in")
    K.check("PADS = [(0, 0)," in g and "add(out, cx, Y + 2, cz, BRICK)" not in g, "S pad 1 = the centre, no pillar")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec46(out, jar, scratch, home):
    T46.run_exec(out, jar, os.path.join(scratch, "r46"), home)


def _setup(scratch, K):
    from jpype import JClass, JLong, JString
    L = T46._fixture(scratch, K)
    J = lambda n: JClass(PKG + n)
    for n in ("ShGeo", "ShFill", "ShPageFn"):
        L[n] = J(n)
    br, PyFn = L["br"], L["PyFn"]
    bags = {"have": {}, "ledger": {}, "short": False, "hook": None}

    def b_count(a):
        return JLong(bags["have"].get(str(a[1]), 0))

    def b_take(a):
        i_, n_ = str(a[1]), int(a[2])
        m = min(n_, bags["have"].get(i_, 0))
        if bags["short"]:
            m = max(0, m - 1)
        bags["have"][i_] = bags["have"].get(i_, 0) - m
        bags["ledger"][i_] = bags["ledger"].get(i_, 0) + m
        if bags["hook"]:
            bags["hook"]()
        return JLong(m)

    def b_put(a):
        i_, n_ = str(a[1]), int(a[2])
        m = min(n_, bags["ledger"].get(i_, 0))
        bags["ledger"][i_] -= m
        bags["have"][i_] = bags["have"].get(i_, 0) + m
        return JLong(m)

    def b_commit(a):
        i_, n_ = str(a[1]), int(a[2])
        m = min(n_, bags["ledger"].get(i_, 0))
        bags["ledger"][i_] -= m
        return JLong(m)
    for k_, f_ in (("count", b_count), ("take", b_take), ("put", b_put), ("commit", b_commit)):
        br.put("sacks:fn:" + k_, PyFn(f_))
    L["bags"] = bags
    return L


def _build(pg):
    import json as _json
    from jpype import JClass
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    b, ev = UCB(), UEB()
    pg.build(None, b, ev, None)
    appended = []
    for c in b.getCommands():
        if "Append" in str(c.type):
            appended.append(str(c.text) if c.text is not None else "")
    datas = {}
    for e in ev.getEvents():
        try:
            datas[str(e.selector)] = str(e.data)
        except Exception:
            datas[str(e.selector)] = str(e)
    return dict(binds=list(datas), datas=datas, mk="\n".join(appended))


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString, JArray
    K = HK.Child(out)
    L = _setup(os.path.join(scratch, "x47"), K)
    St, Core, Inv, Tot, Page, Mth = (L[n] for n in ("ShStore", "ShCore", "ShInv", "ShTotem", "ShPage", "ShMath"))
    inv, count, UUID, bags = L["inv"], L["count"], L["UUID"], L["bags"]
    GOOD, BAD = "#39f493", "#ff6b6b"
    ou, mu = UUID.fromString(OWNER), UUID.fromString(MEMBER)
    now = 1790000000000
    SHW = "skyy-shard-" + OWNER
    log = os.path.join(scratch, "x47", "x", "collect.log")

    def entries():
        return str(St.get(OWNER).getProperty("farming.i0.totems"))

    def set_entries(s):
        St.LOCK.lock()
        try:
            po = St.get(OWNER)
            po.setProperty("farming.i0.totems", s)
            St.save(OWNER, po)
        finally:
            St.LOCK.unlock()
    St.LOCK.lock()
    try:
        po = St.get(OWNER)
        Mth.starter(FK, po, JLong(now))
        St.save(OWNER, po)
    finally:
        St.LOCK.unlock()
    set_entries("harvest_spirit:1:wider::0:hs0001,scarecrow:1:::0:sc0002")
    ti = int(Tot.idx("harvest_spirit"))
    f0 = Tot.onPad("harvest_spirit:1:wider::0:hs0001")
    c = str(Tot.costAt(FK, Tot.ITEMS[ti], Tot.doc(f0, JLong(now)).toJson()))
    rc = Core.recipe(c)
    ids, q = [str(x) for x in rc[0]], [int(x) for x in rc[1]]
    K.check(len(ids) == 2 and ids[1] == "Ingredient_Life_Essence", "X the Farming I -> II cost has two ingredients: %s" % c)
    EN, ES = ids
    TP = inv(9, 9)
    Page.TEST_INV = TP

    def page(u):
        pg = Page(u, SHW)
        pg.view = 3
        pg.kind = FK
        pg.near = False
        pg.sel = 0
        pg.tpad = 0
        return pg
    pt = page(ou)
    rb = _build(pt)
    words = str(Page.costWords(c))
    K.eq(str(pt.dTx[7]), "Tier up: " + words, "X the row says 'Tier up: <cost>' (no bench): %s" % pt.dTx[7])
    K.check(str(pt.dCol[7]) == BAD and str(pt.dTx[8]).endswith("(you have 0)") and str(pt.dCol[8]) == BAD and str(pt.dCol[9]) == BAD,
            "X with nothing: the row + both ingredient rows red, '(you have 0)': %s | %s" % (pt.dTx[8], pt.dTx[9]))
    K.check("#SkyyShWUp" in rb["binds"] and "tup:0:0:1:harvest_spirit:hs0001" in rb["datas"]["#SkyyShWUp"],
            "X the page's Tier up click carries island / pad / tier / type / uid: %s" % rb["datas"].get("#SkyyShWUp", "")[:120])
    K.check("Totem Bench" not in " ".join(str(pt.dTx[i]) for i in range(7, 10)), "X no Tier up row sends the player to the bench")
    CLICK = "tup:0:0:1:harvest_spirit:hs0001"
    # not enough: nothing taken
    Inv.give(TP, EN, JLong(q[0]))
    Inv.give(TP, ES, JLong(q[1] - 1))
    r = str(pt.act(CLICK, None, None))
    K.check(r.startswith("-You need %d " % q[1]) and "(you have %d)" % (q[1] - 1) in r and count(TP, EN) == q[0] and count(TP, ES) == q[1] - 1
            and entries().startswith("harvest_spirit:1:"), "X not enough = refused, nothing taken, still tier 1: %s" % r)
    # bags count for the page and the click: inventory first, then bags
    bags["have"][ES] = 5
    _build(pt)
    K.check(str(pt.dTx[9]) == "%d %s (you have %d)" % (q[1], Tot.pretty(ES), q[1] + 4) and str(pt.dCol[9]) == GOOD and str(pt.dCol[7]) == GOOD
            and str(pt.dCol[8]) == GOOD, "X the bags count: '%s' green, the Tier up row green" % pt.dTx[9])
    r = str(pt.act(CLICK, None, None))
    e = entries()
    K.check(r == "+Harvest Spirit Totem Pole I is now Harvest Spirit Totem Pole II." and e.startswith("harvest_spirit:2:wider::0:hs0001,")
            and count(TP, EN) == 0 and count(TP, ES) == 0 and bags["have"][ES] == 4 and bags["ledger"].get(ES) == 0,
            "X enough: tier 2 (modifier + uid kept); inventory first (all of it), 1 from the bags, the bag part committed: %s / %s" % (r, e))
    K.check("tierup slot 0 pad 0" in open(log, encoding="utf-8").read() and "(from bags: 1 " + ES in open(log, encoding="utf-8").read(), "X one collect.log tierup line (bags named)")
    K.check(e.endswith("scarecrow:1:::0:sc0002"), "X the other pad is untouched")
    # double click (the same old page data)
    Inv.give(TP, EN, JLong(50)); Inv.give(TP, ES, JLong(500))
    r = str(pt.act(CLICK, None, None))
    K.check(r.startswith("=That totem is Harvest Spirit Totem Pole II now") and count(TP, EN) == 50 and count(TP, ES) == 500 and entries().startswith("harvest_spirit:2:"),
            "X a double click / old page = nothing more: %s" % r)
    # the bench cap (Bench I = up to Pole II)
    rb = _build(pt)
    K.check("tup:0:0:2:harvest_spirit:hs0001" in rb["datas"]["#SkyyShWUp"] and "stops at" in str(pt.dTx[8]) and str(pt.dCol[8]) == BAD,
            "X the rebuilt page carries tier 2; a Bench I says it stops at Pole II: %s" % pt.dTx[8])
    r = str(pt.act("tup:0:0:2:harvest_spirit:hs0001", None, None))
    K.check(r.startswith("-Your Farming Totem Bench (Bench I) lets totems tier up to") and count(TP, EN) == 50 and count(TP, ES) == 500, "X the bench cap: refused, nothing taken: %s" % r)
    St.LOCK.lock()
    try:
        po = St.get(OWNER)
        po.setProperty("farming.bench", "4")
        St.save(OWNER, po)
    finally:
        St.LOCK.unlock()
    # a refused save: everything back (inventory + bags)
    c2 = str(Tot.costAt(FK, Tot.ITEMS[ti], Tot.doc(Tot.onPad("harvest_spirit:2:wider::0:hs0001"), JLong(now)).toJson()))
    rc2 = Core.recipe(c2)
    q2 = [int(x) for x in rc2[1]]
    TQ = inv(9, 9)
    Page.TEST_INV = TQ
    Inv.give(TQ, EN, JLong(q2[0])); Inv.give(TQ, ES, JLong(q2[1] - 3))
    bags["have"][ES] = 3
    St.FAIL_TEST = True
    r = str(pt.act("tup:0:0:2:harvest_spirit:hs0001", None, None))
    St.FAIL_TEST = False
    K.check(r == "-Could not be saved - your items are back." and count(TQ, EN) == q2[0] and count(TQ, ES) == q2[1] - 3 and bags["have"][ES] == 3
            and entries().startswith("harvest_spirit:2:"), "X a refused save: still tier 2, inventory AND bag items back: %s" % r)
    # a short bag take: everything back
    bags["short"] = True
    r = str(pt.act("tup:0:0:2:harvest_spirit:hs0001", None, None))
    bags["short"] = False
    K.check(r == "-The cost could not be taken - everything is back." and count(TQ, EN) == q2[0] and count(TQ, ES) == q2[1] - 3 and bags["have"][ES] == 3,
            "X a short bag take: everything back: %s" % r)
    # the record changes between paying and saving (the bag take hook edits it): everything back, the new record kept

    def hook():
        bags["hook"] = None
        set_entries("harvest_spirit:4:wider::0:hs0001,scarecrow:1:::0:sc0002")
    bags["hook"] = hook
    r = str(pt.act("tup:0:0:2:harvest_spirit:hs0001", None, None))
    K.check(r == "-That totem changed meanwhile - your items are back." and count(TQ, EN) == q2[0] and count(TQ, ES) == q2[1] - 3 and bags["have"][ES] == 3
            and entries().startswith("harvest_spirit:4:"), "X the record changed meanwhile: nothing written, everything back: %s" % r)
    set_entries("harvest_spirit:2:wider::0:hs0001,scarecrow:1:::0:sc0002")
    r = str(pt.act("tup:0:0:2:harvest_spirit:hs0001", None, None))
    K.check(r.startswith("+Harvest Spirit Totem Pole II is now") and entries().startswith("harvest_spirit:3:") and count(TQ, ES) == 0 and bags["have"][ES] == 0,
            "X Bench IV: Pole II -> III, inventory then bags: %s" % r)
    # another totem on that pad now / a broken click / the old 'tup'
    K.check(str(pt.act("tup:0:0:3:harvest_spirit:other", None, None)).startswith("-That pad holds another totem now"), "X another uid = refused")
    K.check(str(pt.act("tup", None, None)).startswith("=The page is up to date now"), "X a bare 'tup' (an old page) = refreshed, nothing done")
    K.check(str(pt.act("tup:x:0:1:a:b", None, None)) == "-Pick a totem first.", "X a broken click = refused")
    # an old uid-less record gets a uid, a gf flag is cleared
    set_entries("harvest_spirit:3:wider::0:hs0001,rain:1:::0::gf")
    Inv.give(TQ, EN, JLong(100)); Inv.give(TQ, ES, JLong(500))
    pt.tpad = 1
    rb = _build(pt)
    K.check("tup:0:1:1:rain:" in rb["datas"]["#SkyyShWUp"], "X pad 2's click: %s" % rb["datas"]["#SkyyShWUp"][:120])
    r = str(pt.act("tup:0:1:1:rain:", None, None))
    e1 = entries().split(",")[1]
    K.check(r.startswith("+Rain Totem Pole I is now Rain Totem Pole II") and e1.startswith("rain:2:::0:") and len(e1.split(":")[5]) > 0 and not e1.endswith(":gf"),
            "X an old uid-less gf Rain I on a pad -> Pole II, a uid given, gf cleared: %s / %s" % (r, e1))
    # co-op: no buttons, refused
    pm = page(mu)
    rm = _build(pm)
    K.check("#SkyyShWUp" not in rm["binds"] and "#SkyyShWModAdd" not in rm["binds"], "X co-op: the totem page has no buttons")
    r = str(Core.tierUpPlaced(mu, OWNER, FK, 0, 0, 3, "harvest_spirit", "hs0001", TQ))
    K.check(r.startswith("-Only the island owner can place, pick up or change totems"), "X co-op refused: %s" % r)
    # the shard menu's Totems tab: the same click
    St.LOCK.lock()
    try:
        po = St.get(OWNER)
        po.setProperty("farming.placed", "skyy-island-" + OWNER + "|9|129|9")   # the portal on the owner's island (the menu opens there)
        St.save(OWNER, po)
    finally:
        St.LOCK.unlock()
    pg = Page(ou, "skyy-island-" + OWNER)
    pg.kind = FK
    pg.tab = 3
    rg = _build(pg)
    K.check("#SkyyShTUp" in rg["binds"] and rg["datas"]["#SkyyShTUp"].find("tup:0:0:3:harvest_spirit:hs0001") >= 0 and str(pg.dTx[7]).startswith("Tier up: "),
            "X the Totems tab's Tier up carries the same data: %s (dHas %s mine %s binds %s)" % (rg["datas"].get("#SkyyShTUp", "")[:120], pg.dHas, pg.mine, [b_ for b_ in rg["binds"] if "SkyyShT" in b_]))
    # ---- THE BENCH: Make pole = hand-held Totem I only; a pole totem item is refused there
    TB = inv(9, 9)
    T0 = JLong(now)
    Inv.giveStack(TB, Tot.stack(Tot.parse("harvest_spirit:1:::0:hp0001"), T0))
    Inv.giveStack(TB, Tot.stack(Tot.parse("rain:1:::0:rh0001"), T0))
    Inv.give(TB, EN, JLong(50)); Inv.give(TB, ES, JLong(200))
    Page.TEST_INV = TB
    pb = JClass(PKG + "ShPageFn")(FK, 2).make(None, ou, SHW)
    pb.bTab = 1
    rbb = _build(pb)
    K.check(int(pb.rN) == 1 and str(pb.rName[0]) == "Rain Totem I" and "Make pole" in rbb["mk"] and "Tier up" not in rbb["mk"],
            "X the bench's Make pole tab lists only the hand-held Rain Totem I (rN %d), no 'Tier up' label" % int(pb.rN))
    hp = [(a[0], a[1]) for a in [list(x) for x in Inv.totems(TB)] if str(a[2]) == "Skyy_Totem_HarvestSpirit"][0]
    r = str(Core.tierUp(ou, OWNER, FK, int(hp[0]), int(hp[1]), "hp0001", 1, TB))
    K.check(r.startswith("-Harvest Spirit Totem Pole I tiers up on its own page") and count(TB, EN) == 50, "X a pole totem is refused at the bench, nothing taken: %s" % r)
    clk = "brup:%d:%d:1:rh0001" % (int(pb.rCi[0]), int(pb.rSi[0]))
    K.check(clk in rbb["datas"].get("#SkyyShBRUp", ""), "X the Make pole click carries the Rain I: %s" % rbb["datas"].get("#SkyyShBRUp", "")[:100])
    ra = str(pb.act(clk, None, None))
    K.check(ra.startswith("+Rain Totem I is now Rain Totem Pole II"), "X Make pole still makes a hand-held Rain I a Pole II: %s" % ra)
    pe = JClass(PKG + "ShPageFn")(FK, 0).make(None, ou, SHW)
    if pe is not None and int(pe.view) == 1:
        _build(pe)
        K.check("tiers up" not in str(pe.xTx[1]), "X the exit page no longer says the bench tiers up: %s" % pe.xTx[1])
    Page.TEST_INV = None
    K.save()


def run_centre(out, jar, scratch, _home):
    from jpype import JClass, JLong
    K = HK.Child(out)
    L = _setup(os.path.join(scratch, "c47"), K)
    St, Tot, Geo, Fill, Mth = (L[n] for n in ("ShStore", "ShTotem", "ShGeo", "ShFill", "ShMath"))
    now = 1790000000000
    St.LOCK.lock()
    try:
        po = St.get(OWNER)
        Mth.starter(FK, po, JLong(now))
        po.setProperty("farming.i0.totems", "harvest_spirit:1:::0:hs0001,scarecrow:1:::0:sc0002")
        for f_ in ("type", "size", "stored", "last"):
            po.setProperty("farming.i1." + f_, str(po.getProperty("farming.i0." + f_)))
        St.save(OWNER, po)
    finally:
        St.LOCK.unlock()
    cx, cz, Y = int(Geo.ox(FK) + Geo.SX[0]), int(Geo.OZ + Geo.SZ[0]), int(Geo.Y)
    cx1, cz1 = int(Geo.ox(FK) + Geo.SX[1]), int(Geo.OZ + Geo.SZ[1])
    K.eq([int(x) for x in Geo.padPos(FK, 0, 0)], [cx, Y + 1, cz], "G pad 1 = the island centre")
    K.eq([int(x) for x in Geo.padPos(FK, 0, 1)], [cx + 1, Y + 1, cz], "G pad 2 stays where it was (1, 0)")
    isl = JClass("java.util.ArrayList")()
    Geo.island(isl, FK, 0, 1)
    K.check(not any(int(b[0]) == cx and int(b[2]) == cz and int(b[1]) > Y for b in isl), "G a new island: nothing above the centre floor (no pillar)")
    BRICK = str(Geo.IDS[Geo.BRICK])
    HS = str(Geo.IDS[Geo.TOTEM + Tot.idx("harvest_spirit")])
    SC = str(Geo.IDS[Geo.TOTEM + Tot.idx("scarecrow")])
    k_ = lambda x, y, z: "%d,%d,%d" % (x, y, z)
    M = JClass("java.util.HashMap")()
    # a 0.4.6 island 1: the 2-block brick pillar on the centre, pad 1's totem at (0, -1), pad 2's at (1, 0); island 2: someone's stone on the pillar top
    M.put(k_(cx, Y + 1, cz), BRICK); M.put(k_(cx, Y + 2, cz), BRICK)
    M.put(k_(cx, Y + 1, cz - 1), HS); M.put(k_(cx + 1, Y + 1, cz), SC)
    M.put(k_(cx1, Y + 1, cz1), BRICK); M.put(k_(cx1, Y + 2, cz1), "Rock_Stone")
    Fill.TEST_BLOCKS = M
    want = Geo.region(St.get(OWNER), FK)
    fx = JClass("java.util.HashSet")()
    Fill.paintX(None, want, fx)
    g = lambda x, y, z: (str(M.get(k_(x, y, z))) if M.get(k_(x, y, z)) is not None else "")
    K.check(g(cx, Y + 1, cz) == HS and g(cx, Y + 2, cz) == "" and g(cx, Y + 1, cz - 1) == "" and g(cx + 1, Y + 1, cz) == SC,
            "G island 1: the totem stands on the centre, the pillar top + the old pad-1 block are gone, pad 2 untouched (%s / %s / %s / %s)"
            % (g(cx, Y + 1, cz), g(cx, Y + 2, cz), g(cx, Y + 1, cz - 1), g(cx + 1, Y + 1, cz)))
    K.check(g(cx1, Y + 2, cz1) == "Rock_Stone" and g(cx1, Y + 1, cz1) == "", "G island 2 (no totem): the centre pad is AIR, a foreign block on the pillar top is KEPT")
    K.eq(sorted(int(x) for x in fx), [0, 1], "G both islands' fix spots were done")
    K.eq(int(Fill.markFixed("skyy-shard-" + OWNER, FK, fx)), 2, "G the markers are written")
    pr = open(os.path.join(scratch, "c47", "x", "shards", OWNER + ".properties"), encoding="latin-1").read()
    K.check("farming.i0.centre=1" in pr and "farming.i1.centre=1" in pr, "G the markers are on disk")
    # once only: a brick put back on the old pillar top + a totem block on the old pad spot (as if built later) are never touched again
    M.put(k_(cx, Y + 2, cz), BRICK); M.put(k_(cx, Y + 1, cz - 1), HS)
    want2 = Geo.region(St.get(OWNER), FK)
    K.check(not any(int(b[3]) < 0 for b in want2), "G a fixed island carries no fix entries any more")
    fx2 = JClass("java.util.HashSet")()
    Fill.paintX(None, want2, fx2)
    K.check(g(cx, Y + 2, cz) == BRICK and g(cx, Y + 1, cz - 1) == HS and g(cx, Y + 1, cz) == HS and fx2.size() == 0 and int(Fill.markFixed("skyy-shard-" + OWNER, FK, fx2)) == 0,
            "G a second paint touches nothing (the fix ran once)")
    # the crops-only regrow never carries fix entries; a buy/new island (no marker) has nothing to clear and is marked by its first paint
    K.check(not any(int(b[3]) < 0 for b in Geo.crops(St.get(OWNER), FK)), "G the regrow list has no fix entries")
    Fill.TEST_BLOCKS = None
    K.save()


def run_live47(out, jar, scratch, home):
    """D on a scratch COPY of NewBetaTest's Skyy_SkyyShards (0.4.6 already deployed there): start twice = no update runs, nothing written;
    then every real profile's shard region painted on a block map seeded with the 0.4.6 pillar + pad-1 totem: the totem on the centre,
    the markers written into the COPY, a second paint touches nothing"""
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    T42 = T46.T42
    Cfg, path = T42.kit_home(home)
    M4, M5, M6 = JClass(PKG + "ShMig044"), JClass(PKG + "ShMig045"), JClass(PKG + "ShMig046")
    t0 = T42.tree(home)
    for s_ in (1, 2):
        T42.kit_home(home)
        rs = (str(Cfg.migCoop(Cfg.FILE)), str(M4.run(Cfg.FILE)), str(M5.run(Cfg.FILE)), str(M6.run(Cfg.FILE)))
        r = str(Cfg.loadCfg(True))
        K.check(not r.startswith("default") and rs == ("", "", "", ""), "D start %d: the live config is read, no update runs: %s" % (s_, rs))
    K.check(T42.tree(home) == t0, "D two starts changed no file")
    St, Tot, Geo, Fill, Kind, Mth = (JClass(PKG + n) for n in ("ShStore", "ShTotem", "ShGeo", "ShFill", "ShKind", "ShMath"))
    sd = os.path.join(home, "shards")
    St.DIR = path(sd)
    keys = [f[:-11] for f in sorted(os.listdir(sd)) if f.endswith(".properties")] if os.path.isdir(sd) else []
    n_isl, n_tot, bad = 0, 0, []
    for k in keys:
        p = St.get(k)
        if p is None:
            continue
        for kd in range(int(Kind.N)):
            M = JClass("java.util.HashMap")()
            kk = lambda x, y, z: "%d,%d,%d" % (x, y, z)
            Y = int(Geo.Y)
            spots = []
            for sl in range(6):
                if not Mth.hasIsland(kd, p, sl):
                    continue
                cx, cz = int(Geo.ox(kd) + Geo.SX[sl]), int(Geo.OZ + Geo.SZ[sl])
                M.put(kk(cx, Y + 1, cz), str(Geo.IDS[Geo.BRICK])); M.put(kk(cx, Y + 2, cz), str(Geo.IDS[Geo.BRICK]))
                e = [str(x) for x in Tot.entries(kd, p, sl)]
                t0_ = int(Tot.idx(str(Tot.parse(e[0])[0]))) if e else -1
                if t0_ >= 0:
                    M.put(kk(cx, Y + 1, cz - 1), str(Geo.IDS[Geo.TOTEM + t0_]))
                spots.append((sl, cx, cz, t0_))
            if not spots:
                continue
            Fill.TEST_BLOCKS = M
            fx = JClass("java.util.HashSet")()
            Fill.paintX(None, Geo.region(p, kd), fx)
            for sl, cx, cz, t0_ in spots:
                n_isl += 1
                c1 = M.get(kk(cx, Y + 1, cz))
                want = str(Geo.IDS[Geo.TOTEM + t0_]) if t0_ >= 0 else None
                ok = (str(c1) == want if want else c1 is None) and M.get(kk(cx, Y + 2, cz)) is None and M.get(kk(cx, Y + 1, cz - 1)) is None
                n_tot += 1 if t0_ >= 0 else 0
                if not ok:
                    bad.append((k[:8], kd, sl))
            Fill.markFixed("skyy-shard-" + k, kd, fx)
            fx2 = JClass("java.util.HashSet")()
            M.put(kk(spots[0][1], Y + 2, spots[0][2]), "Rock_Stone")
            Fill.paintX(None, Geo.region(St.get(k), kd), fx2)
            if fx2.size() != 0 or str(M.get(kk(spots[0][1], Y + 2, spots[0][2]))) != "Rock_Stone":
                bad.append((k[:8], kd, "second paint"))
    Fill.TEST_BLOCKS = None
    K.check(n_isl > 0 and not bad, "D every real island (%d, %d with a pad-1 totem): the totem on the centre, no pillar, fixed once: %s" % (n_isl, n_tot, bad[:5]))
    K.save()


EXPECT = {   # checked by hand 2026-10-23: the version texts (CfgFn, CfgRows, ShStore, setup), the tier-up + bag payment (ShCore), the centre
            # pad (ShGeo, ShFill, ShTotem PDX), the pages (ShPage)
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
    "ShCore": ["+m bagCall", "+m bagCount", "+m haveAll", "+m payInvBags", "+m refundPaid", "+m tierUpPlaced", "+m tierUpPlaced0", "-m upgrade",
               "~m placeTotem0", "~m tierUp"],
    "ShFill": ["+f TEST_BLOCKS", "+m markFixed", "+m paintX", "~<clinit>", "~m clear", "~m idAt", "~m paint", "~m put", "~m run"],
    "ShGeo": ["+f FIX_BRICK", "+f FIX_PAD", "+f OPX", "+f OPZ", "+m fixes", "~m island", "~m region"],
    "ShPage": ["+f dTier", "+f dType", "+f dUid", "+m tierRows", "~m act", "~m buildBench", "~m buildFull", "~m buildTotem", "~m fillBench",
               "~m fillBenchTier", "~m fillExit", "~m fillTotems"],
    "ShStore": ["~m migrate", "~m save"], "ShTotem": ["~<clinit>"], "SkyyShardsPlugin": ["~m setup"]}

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec46", run_exec46), ("exec", run_exec), ("centre", run_centre), ("live", run_live47)],
           script=__file__, live=(T46.LIVE_SH, "mods/Skyy_SkyyShards"))
