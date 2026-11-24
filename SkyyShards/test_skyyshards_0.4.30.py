"""Harness for SkyyShards 0.4.30 (the Mining quarry = one island per zone - tools/shards_0_4_30_patch.py, on top of 0.4.29).
Build first:
    python tools/shards_0_4_30_patch.py && python SkyyShards/build_skyyshards_0.4.30.py
    python SkyyShards/test_skyyshards_0.4.30.py [--keep] [--only label,label] [--dir <scratch>]

  S30  static   the patch re-runs to identical bytes; header / VERSION / ready line / rollback note; no new registerSystem / registerCommand; line
                endings kept; 0.4.29 never reads mining.i<n>.ores (rollback = ignored key)
  MZ30 model    EXECUTED owns / zoneOwned / baseSlot / nextTier / isBase with Iron as an island AND as an ore upgrade (identical answers); the
                quarry's nodes per bought ore: the same seeded clicks give EXACTLY the same drops in both models (Copper even spots, Iron odd);
                the node pictures; another kind (Foraging) unchanged; a corrupt ores line (another zone's ore / junk) owns nothing
  MP30 page     EXECUTED the map = 5 zone cards (names, Yours n / m ores, Locked, Buy, "First add ..."), Open for EVERY owned zone (Zones 1-5, the
                shown one too), the Ores row (have / need lines = the 0.4.29 island price of that ore), Add ore bought (exact coins + items), a
                double click buys once, too few items / coins refused (nothing paid), a stale quarry slot / another profile refused, tier order
                (Add Iron first), Iron bought AS AN ISLAND refused once Zone 1 has a quarry, the Zone 2 quarry bought from its card (kb3), Open
                every zone; the cost table (every ore: coins + items) printed
  MG30 migration EXECUTED on files: Copper + Iron (+ Zone 3 Cobalt + Chromium) fold into their quarries (size / effective sub levels / Vein /
                Lucky / Smithy, every totem, every item in base units, rare finds, ores list), a lone Lead island stays the Zone 2 quarry, an
                Iron-only profile keeps Iron as the Zone 1 quarry (Copper = its Ores row); History copy byte-checked, the journal line, ONE save,
                the second load changes nothing; refused cases change nothing: an unknown island key, a failing totals check, a refused save,
                a refused History copy; a profile with one island a zone: nothing written, no marker; then the page on the folded file
  then 0.4.29's phases (minus the ones that assert the per-ore map: listed in SKIP with why) on THIS jar, A verify, C compare, AA audit,
  live30 START TWICE on a scratch copy of the live data: islands before - folded = after, totems and items (base units) the same, owned ores the
                same, the second start changes nothing
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.30"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "mzone1fix2", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.29.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.29.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_30_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.29 harness (it loads 0.4.28 -> ... older): its version moves to this one in memory
_T29 = open(os.path.join(HERE, "test_skyyshards_0.4.29.py"), encoding="utf8").read()
assert _T29.count('VERSION = "0.4.29"\n') == 1, "the 0.4.29 harness changed"
_T29 = _T29.replace('VERSION = "0.4.29"\n', 'VERSION = "%s"\n' % VERSION)
_argv = list(sys.argv)
T429 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_29", loader=None))
T429.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.29.py")
exec(compile(_T29, T429.__file__, "exec"), T429.__dict__)
sys.argv[:] = _argv
T428 = T429.T428
T427, T426, T425, T424, T423 = T429.T427, T429.T426, T429.T425, T429.T424, T429.T423
T419, T49, T410, T411, T416 = T429.T419, T429.T49, T429.T410, T429.T411, T429.T416
for _m in (T429, T428):
    _m.JAR = JAR
    _m.SCRATCH = SCRATCH
OWNER = T428.OWNER
MI, FO, FK, RA, OR, CK = 0, 1, 2, 3, 4, 5
T0 = T428.T0
CU, FE, CB = "Ore_Copper", "Ore_Iron", "Rock_Stone_Cobble"
BCU, BFE = "Ingredient_Bar_Copper", "Ingredient_Bar_Iron"


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.30 - build script') and 'VERSION = "0.4.30"\n' in g, "S30 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S30 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.30:" in g, "S30 the ready line names the round")
    K.check("ROLLBACK 0.4.30 -> 0.4.29 alone" in g and "SAVED DATA: mining.i<n>.ores" in g, "S30 the rollback + saved-data notes")
    K.check('"ores"' not in o and "mzone.done" not in o, "S30 0.4.29 never reads mining.i<n>.ores / mzone.done (a rollback ignores them)")
    K.check('"orr"' not in o and '"xpr"' not in o, "S30 FIX 0.4.29 never reads mining.i<n>.orr / xpr (a rollback ignores them)")
    K.check("int[] o = zoneOwned(p, z);\n  return @PKG@.ShIsl.zoneSlot" not in g and "public static int baseSlot(java.util.Properties p, int z) {\n  return @PKG@.ShIsl.zoneSlot(MK, p, z);" in g,
            "S30 FIX baseSlot no longer calls zoneOwned for nothing")
    K.check("EVERY ore owned through the Ores" in g and "rollback floor" in g and "the last save before the fold" in g, "S30 FIX the rollback note names every ore upgrade + the floor advice + the History copy's age")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S30 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S30 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S30 jar newer than the script, the script newer than the patch")
    K.save()


def _set(L, p, fn):
    St = L["ShStore"]
    St.LOCK.lock()
    try:
        fn()
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()


def _upgrade_model(L, p):
    """0.4.24's Copper + Iron fixture, Iron turned into an ore upgrade of the Copper quarry (what the migration makes)"""
    def f():
        for k_ in list(p.stringPropertyNames()):
            if str(k_).startswith("mining.i1."):
                p.remove(k_)
        p.setProperty("mining.i0.ores", "iron")
    _set(L, p, f)


def _owns(L, p):
    Isl = L["ShIsl"]
    return [bool(Isl.owns(MI, p, int(Isl.LAD0[MI]) + i)) for i in range(int(Isl.LADN[MI]))]


# ---------------------------------------------------------------------------------------------------------- MZ30: the model
def run_model(out, jar, scratch, _home):
    from jpype import JString, JClass, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = T428._env(scratch, K, "mz")
    St, Isl, Ck, Cfg, Core = L["ShStore"], L["ShIsl"], L["ShClk"], L["ShCfg"], L["ShCore"]
    L0 = int(Isl.LAD0[MI])
    names = [str(Isl.NAME[L0 + i]) for i in range(int(Isl.LADN[MI]))]
    zones = [int(Isl.zoneOf(L0 + i)) for i in range(len(names))]
    K.eq(names[:2], ["Copper", "Iron"], "MZ the Mining ladder starts Copper, Iron")
    K.notes.append("MZ ladder: " + json.dumps(list(zip(names, zones))))
    res = {}
    for model in ("island", "upgrade"):
        T424._mining(L, p, size=2, amt=5)
        if model == "upgrade":
            _upgrade_model(L, p)
        St.LOCK.lock()
        try:
            ow = _owns(L, p)
            zo = [str(Isl.NAME[int(x)]) for x in Ck.zoneOwned(p, 1)]
            res[model] = (ow, zo, int(Ck.baseSlot(p, 1)), int(Isl.nextTier(MI, p)), bool(Ck.isBase(p, MI, 0)), int(Isl.slotOf(MI, p, L0 + 1)))
        finally:
            St.LOCK.unlock()
    K.eq(res["island"][:5], res["upgrade"][:5], "MZ owns / zoneOwned / baseSlot / nextTier / isBase: Iron as an island = Iron as an ore upgrade %s" % (res["upgrade"][:5],))
    K.check(res["island"][5] == 1 and res["upgrade"][5] == -1 and res["upgrade"][1] == ["Copper", "Iron"] and res["upgrade"][3] == 2,
            "MZ ... the upgrade has no island (slotOf -1), the quarry mines Copper + Iron, the next buy = rank 2 (Zone 2)")
    # the nodes: the same seeded clicks in both models give the same drops (Copper on even spots, Iron on odd)
    Cfg.CK_CPS = 1000
    drops = {}
    for model in ("island", "upgrade"):
        T424._mining(L, p, size=2, amt=5)
        if model == "upgrade":
            _upgrade_model(L, p)
        _set(L, p, lambda: p.remove("mining.i0.totems"))   # FIX: the clicks alone (the spirits' ore share is FX30's - an island model has none)
        Ck.ALLOYACC.clear()
        now = T0 + (1 if model == "island" else 2) * 3600000
        log = []
        for spot in range(4):
            Core.NOW_TEST = now + spot * 100000
            Ck.RND_TEST = JClass("java.util.Random")(JLong(500 + spot))
            for _ in range(40):
                r = Ck.chop(ou, JString(OWNER), MI, 0, spot, JString("Tool_Pickaxe_Iron"))
                s = str(r[0])
                if s.startswith("+Mined"):
                    log.append(s.split(":")[0])
                    break
            Ck.RND_TEST = None
        drops[model] = (dict(T425._drops(p, 0, "mining")), log)
    K.check(drops["island"] == drops["upgrade"] and len(drops["upgrade"][1]) == 4, "MZ the same clicks, the same drops in both models: %s" % (drops["upgrade"],))
    K.check([x.endswith("Copper node") for x in drops["upgrade"][1]] == [True, False, True, False] and "Iron node" in drops["upgrade"][1][1],
            "MZ ... spots 0 / 2 Copper, 1 / 3 Iron (the bought ore's nodes): %s" % drops["upgrade"][1])
    K.check(FE in drops["upgrade"][0] or any(k_ == CB for k_ in drops["upgrade"][0]), "MZ ... Iron nodes give Iron finds / stone")
    # the page pictures: spot 1 = an Iron node
    cs = T427._give(L, [("Tool_Pickaxe_Iron", 1)])
    pg = T427._page(L, ou, W_, MI)
    Ck.HAND_TEST = "Tool_Pickaxe_Iron"
    Core.NOW_TEST = T0 + 9 * 3600000
    T49._build(pg)
    K.check(str(pg.ckTexA[0]).endswith("ClkQNode0.png") and str(pg.ckTexA[1]).endswith("ClkQNode1.png"), "MZ the quarry page: spot 0 Copper, spot 1 Iron (an upgrade)")
    K.check(str(pg.ckChip).startswith("Zone 1 Quarry") and "Copper, Iron" in str(pg.ckSto[0]), "MZ ... the chip + the ores line: %s / %s" % (pg.ckChip, pg.ckSto[0]))
    # corrupt lines own nothing: another zone's ore, junk
    _set(L, p, lambda: p.setProperty("mining.i0.ores", "iron,thorium, ,nonsense"))
    St.LOCK.lock()
    try:
        ow = _owns(L, p)
    finally:
        St.LOCK.unlock()
    K.check(ow[1] and not ow[2] and sum(ow) == 2, "MZ a Zone 2 ore / junk on the Zone 1 quarry owns nothing: %s" % ow)
    # Foraging unchanged: owns = an island
    T423._foraging(L, p)
    St.LOCK.lock()
    try:
        fo = [bool(Isl.owns(FO, p, int(Isl.LAD0[FO]) + i)) == (int(Isl.slotOf(FO, p, int(Isl.LAD0[FO]) + i)) >= 0) for i in range(int(Isl.LADN[FO]))]
        p.setProperty("foraging.i0.ores", "birch")
        fb = bool(Isl.owns(FO, p, int(Isl.LAD0[FO]) + 1))
        p.remove("foraging.i0.ores")
    finally:
        St.LOCK.unlock()
    K.check(all(fo) and not fb, "MZ Foraging: owns = its islands only (an ores line means nothing there)")
    K.save()


# ---------------------------------------------------------------------------------------------------------- MP30: the page
def _cost(L, li):
    Isl, Cfg, Core = L["ShIsl"], L["ShCfg"], L["ShCore"]
    t = int(Isl.LAD0[MI]) + li
    coins = int(Isl.coins(Cfg.BUY_H, Core.tierCv(t)))
    m = Isl.mats(MI, t, Cfg.BUY_ITEMS[MI], 0, 1)
    return coins, dict(zip([str(x) for x in m[0]], [int(x) for x in m[1]]))


def _zones(L, p, rows, lv=None):
    """Mining islands only: rows = [(slot, type, size)]"""
    def f():
        for k_ in list(p.stringPropertyNames()):
            if str(k_).startswith("mining."):
                p.remove(k_)
        for s, ty, sz in rows:
            p.setProperty("mining.i%d.type" % s, ty); p.setProperty("mining.i%d.size" % s, str(sz)); p.setProperty("mining.i%d.last" % s, str(T0))
            p.setProperty("mining.i%d.stored" % s, "0"); p.setProperty("mining.i%d.totems" % s, "quarry_spirit:1:::0:mz%04d" % s)
        p.setProperty("mining.auto", "1"); p.setProperty("mining.paused", "0"); p.setProperty("mining.storage", "5")
        p.setProperty("mining.placed", L["W_"] + "|1|2|3")
    _set(L, p, f)


def run_page(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = T428._env(scratch, K, "mp")
    St, Isl, Ck, Cfg, Core, Tot = L["ShStore"], L["ShIsl"], L["ShClk"], L["ShCfg"], L["ShCore"], L["ShTotem"]
    L0 = int(Isl.LAD0[MI])
    LN = int(Isl.LADN[MI])
    keys = [str(Isl.KEY[L0 + i]) for i in range(LN)]
    names = [str(Isl.NAME[L0 + i]) for i in range(LN)]
    Ck.HAND_TEST = "Tool_Pickaxe_Iron"
    L["coins"]["bal"] = 10 ** 12
    lv["Mining"] = 100
    # the cost table: every ore = the 0.4.29 island price
    rows = []
    for li in range(LN):
        c, m = _cost(L, li)
        rows.append((names[li], int(Isl.zoneOf(L0 + li)), "quarry" if li == min(i for i in range(LN) if int(Isl.zoneOf(L0 + i)) == int(Isl.zoneOf(L0 + li))) else "ore upgrade",
                     c, " + ".join("%d %s" % (q, i) for i, q in sorted(m.items()))))
    print("MP cost table: ore | zone | bought as | coins | items")
    for r in rows:
        print("MP  %s | Zone %d | %s | %s | %s" % (r[0], r[1], r[2], "{:,}".format(r[3]), r[4]))
    K.notes.append("MP cost table: " + json.dumps(rows))
    K.check(all(set(_cost(L, li)[1]) <= {str(Isl.PROD[L0 + li]), str(Isl.SMELT[L0 + li]), str(Isl.ENCH[L0 + li]), str(Isl.SMELTE[L0 + li]), str(Isl.tok(MI, L0 + li, JString("ench")))}
                for li in range(LN)), "MP every ore's price asks only that ore's own items (its bars + its Enchanted part, as its 0.4.29 island)")
    # Zone 1 = Copper only: the map + the Ores row
    _zones(L, p, [(0, "copper", 1)])
    c1, m1 = _cost(L, 1)
    cs = T427._give(L, [(i, q) for i, q in m1.items()] + [("Tool_Pickaxe_Iron", 1)])
    cnt = lambda i: int(L["count"](cs, i))
    pg = T427._page(L, ou, W_, MI)
    bd = T49._build(pg)
    K.check(str(pg.ckMN[0]) == "Copper + Iron" and str(pg.ckMS[0]).startswith("Shown now - 1 / 2 ores; add Iron inside") and int(pg.ckMB[0]) == 1,
            "MP the Zone 1 card: names its ores, Shown now 1 / 2, add Iron inside, Open (%s / %s / %d)" % (pg.ckMN[0], pg.ckMS[0], pg.ckMB[0]))
    K.check(all(str(pg.ckMN[c]) == "" for c in range(15) if c % 3), "MP ... one card a zone (no 2nd / 3rd ore cards)")
    K.check(str(pg.ckMS[3]).startswith("First add Iron in the Zone 1 quarry") and int(pg.ckMB[3]) == 0, "MP the Zone 2 card: First add Iron in the Zone 1 quarry (%s)" % pg.ckMS[3])
    K.check(str(pg.ckUpL[8]) == "1 / 2 ores" and str(pg.ckUpE[8]) == "Add Iron: more ore nodes" and bool(pg.ckUpOk[8]) and int(pg.ckUpSeen[8]) == 1,
            "MP the Ores row: 1 / 2 ores, Add Iron, buyable, carries rank 1 (%s / %s)" % (pg.ckUpL[8], pg.ckUpE[8]))
    lines = [str(pg.ckCL[24 + j]) for j in range(3)]
    K.check(lines[0].endswith("/ {:,} coins".format(c1)) and all(int(pg.ckCG[24 + j]) == 1 for j in range(3) if lines[j]),
            "MP ... have / need lines, all green: %s" % lines)
    K.check(str(pg.ckUpC[8]) == str(L["ShPage"].ckCost(c1, Isl.mats(MI, L0 + 1, Cfg.BUY_ITEMS[MI], 0, 1))), "MP ... = the 0.4.29 island price of Iron (%s)" % pg.ckUpC[8])
    K.check('"ku8:1"' in bd["datas"].get("#SkyyShKU8X", ""), "MP ... the Add ore button carries the ore shown (ku8:1)")
    pg.ckMode = 1
    bm = T49._build(pg)
    K.check('"km0"' in bm["datas"].get("#SkyyShKM0X", "") and not any(("#SkyyShKM%dX" % c) in bm["datas"] for c in range(15) if c % 3),
            "MP ... the map: the Zone 1 card's Open button (km0), no 2nd / 3rd ore cards")
    r_ = T410.full(pg)
    K.check(not r_["miss"] and not r_["unbound"], "MP the map walks clean %s %s" % (r_["miss"][:2], r_["unbound"][:2]))
    pg.ckMode = 0
    T49._build(pg)
    r_ = T410.full(pg)
    K.check(not r_["miss"] and not r_["unbound"], "MP the island view walks clean %s %s" % (r_["miss"][:2], r_["unbound"][:2]))
    K.check(len(pg.ckUpL) == 9 and str(pg.ckUpE[1]).startswith("Nodes ") and "Add Iron on the Ores row." in str(pg.ckCap) and len(str(pg.ckCap)) <= 125,
            "MP 9 rows (Ore nodes as before), the caption says where Iron is added: %s" % pg.ckCap)
    # direct island buy of Iron: refused (one island a zone)
    b0 = L["coins"]["bal"]
    r = str(Core.buyIsland(ou, JString(OWNER), MI, 1, cs))
    K.check(r.startswith("-Iron is an upgrade of your Zone 1 quarry") and p.getProperty("mining.i1.type") is None and L["coins"]["bal"] == b0,
            "MP Iron bought AS AN ISLAND: refused, nothing paid (%s)" % r)
    # too few items: refused
    it0 = sorted(m1)[0]
    cs2 = T427._give(L, [(i, q - (1 if i == it0 else 0)) for i, q in m1.items()])
    pg.ckSlot = 0
    r = T427._ev(pg, "ku8:1")
    K.check(p.getProperty("mining.i0.ores") is None and L["coins"]["bal"] == b0 and int(L["count"](cs2, it0)) == m1[it0] - 1,
            "MP one %s short: refused, nothing paid (%s)" % (it0, r[:90]))
    # too few coins: refused
    cs = T427._give(L, [(i, q) for i, q in m1.items()])
    L["coins"]["bal"] = c1 - 1
    r = T427._ev(pg, "ku8:1")
    K.check(p.getProperty("mining.i0.ores") is None and L["coins"]["bal"] == c1 - 1 and all(cnt(i) == q for i, q in m1.items()), "MP one coin short: refused, nothing paid (%s)" % r[:80])
    L["coins"]["bal"] = 10 ** 12
    # another profile with the page open: refused
    k0 = pg.key
    pg.key = "00000000-0000-0000-0000-000000000000-p9"
    r = str(pg.act("ku8:1", None, None))
    K.check(r.startswith("=The page is up to date") and p.getProperty("mining.i0.ores") is None, "MP a stale profile: refused (%s)" % r[:70])
    pg.key = k0
    # bought
    T49._build(pg)
    b0 = L["coins"]["bal"]
    r = T427._ev(pg, "ku8:1")
    K.check(str(p.getProperty("mining.i0.ores")) == "iron" and b0 - L["coins"]["bal"] == c1 and all(cnt(i) == 0 for i in m1),
            "MP Add ore Iron: mining.i0.ores=iron, exactly %d coins + %s paid (%s)" % (c1, m1, r[:80]))
    disk = open(os.path.join(str(St.DIR), OWNER + ".properties"), encoding="latin-1").read()
    K.check("mining.i0.ores=iron" in disk, "MP ... saved at once")
    b1 = L["coins"]["bal"]
    cs = T427._give(L, [(i, q) for i, q in m1.items()])
    r = T427._ev(pg, "ku8:1")
    K.check(str(p.getProperty("mining.i0.ores")) == "iron" and L["coins"]["bal"] == b1 and all(cnt(i) == q for i, q in m1.items()), "MP a double click buys once (%s)" % r[:70])
    T49._build(pg)
    K.check(str(pg.ckUpL[8]) == "2 / 2 ores" and not bool(pg.ckUpOk[8]) and str(pg.ckCL[24]).startswith("Every ore of Zone 1"), "MP ... the row: 2 / 2 ores, no button (%s)" % pg.ckCL[24])
    K.check(str(pg.ckMS[0]).startswith("Shown now - 2 / 2 ores") and str(pg.ckMS[3]).startswith("Buy: ") and int(pg.ckMB[3]) == 2, "MP ... the Zone 2 card: Buy (%s)" % pg.ckMS[3])
    # the Zone 2 quarry from its card (= the 0.4.29 Thorium island price)
    c2, m2 = _cost(L, 2)
    cs = T427._give(L, [(i, q) for i, q in m2.items()])
    b2 = L["coins"]["bal"]
    r = T427._ev(pg, "kb3")
    s2 = int(Isl.slotOf(MI, p, L0 + 2))
    K.check(s2 >= 0 and b2 - L["coins"]["bal"] == c2 and int(pg.ckSlot) == s2, "MP the Zone 2 quarry bought from its card: %d coins, the page opens it (slot %d) (%s)" % (c2, s2, r[:70]))
    T49._build(pg)
    K.check(str(pg.ckChip).startswith("Zone 2 Quarry") and int(pg.ckUpSeen[8]) == 3 and bool(pg.ckUpOk[8]), "MP ... Zone 2: its Ores row offers %s" % names[3])
    # a stale quarry slot: the page shows Zone 2, the event names Zone 1's ore
    r = T427._ev(pg, "ku8:1")
    K.check(r.lower().find("already") >= 0 or r.startswith("The page is up to date"), "MP Zone 1's ore on the Zone 2 page: nothing bought (%s)" % r[:80])
    # Open from the map: every zone
    _zones(L, p, [(0, "copper", 1), (4, keys[2], 1), (7, keys[4], 2), (9, keys[6], 3), (2, keys[8], 1)])
    _set(L, p, lambda: p.setProperty("mining.i0.ores", "iron"))
    pg = T427._page(L, ou, W_, MI)
    T49._build(pg)
    want = {0: 0, 3: 4, 6: 7, 9: 9, 12: 2}
    for c, s in sorted(want.items()):
        pg.ckMode = 1
        T49._build(pg)
        K.check(int(pg.ckMB[c]) == 1 and str(pg.ckMS[c]).split(" - ")[0] in ("Yours", "Shown now"), "MP the Zone %d card: %s (Open)" % (c // 3 + 1, pg.ckMS[c]))
        r = T427._ev(pg, "km%d" % c)
        T49._build(pg)
        K.check(int(pg.ckSlot) == s and int(pg.ckMode) == 0 and str(pg.ckChip).startswith("Zone %d Quarry" % (c // 3 + 1)), "MP ... Open enters it (slot %d, %s)" % (s, pg.ckChip))
    # the zone 5 card lists its three ores; tier order: Zone 3 page offers its 2nd ore only after Zone 2's (Lead) is added
    K.check(len(str(pg.ckMN[12])) <= 24, "MP the Zone 5 card name fits: %s" % pg.ckMN[12])
    pg.ckSlot = 7
    T49._build(pg)
    K.check(not bool(pg.ckUpOk[8]) and ("Add %s first" % names[3]) in " ".join(str(pg.ckCL[24 + j]) for j in range(3)), "MP tier order: the Zone 3 Ores row waits for %s (%s)" % (names[3], pg.ckCL[24]))
    c5, m5 = _cost(L, 5)
    cs = T427._give(L, [(i, q) for i, q in m5.items()])
    r = str(Ck.buyOre(ou, JString(OWNER), MI, 7, 5, cs))
    K.check(r.startswith("-Add %s first" % names[3]) and p.getProperty("mining.i7.ores") is None, "MP ... buyOre refuses it too (%s)" % r)
    # a zone locked by Mining level
    lv["Mining"] = 10
    _zones(L, p, [(0, "copper", 1)])
    _set(L, p, lambda: p.setProperty("mining.i0.ores", "iron"))
    pg = T427._page(L, ou, W_, MI)
    T49._build(pg)
    K.check(bool(pg.ckMLock[3]) and str(pg.ckMS[3]).startswith("Locked: Mining 20"), "MP a locked zone: %s" % pg.ckMS[3])
    _zones(L, p, [(0, "copper", 1), (4, keys[2], 1)])
    T49._build(pg)
    K.check(not bool(pg.ckMLock[3]) and int(pg.ckMB[3]) == 1 and str(pg.ckMS[3]).startswith("Yours - 1 / 2 ores"), "MP an owned zone in a locked zone: Open, no lock (%s)" % pg.ckMS[3])
    r = T427._ev(pg, "km3")
    K.check(int(pg.ckSlot) == 4, "MP ... and it opens (%s)" % r[:60])
    lv["Mining"] = 100
    # every row line still fits (<= 38 characters), on every zone
    _zones(L, p, [(0, "copper", 1), (4, keys[2], 1), (7, keys[4], 2), (9, keys[6], 3), (2, keys[8], 1)])
    long_ = []
    for s in (0, 4, 7, 9, 2):
        pg = T427._page(L, ou, W_, MI)
        pg.ckSlot = s
        T49._build(pg)
        long_ += [str(x) for x in list(pg.ckUpE) + list(pg.ckUpL) if x is not None and len(str(x)) > 38]
        long_ += [str(x) for x in pg.ckCL if x is not None and len(str(x)) > 40]
    K.check(not long_, "MP every row line fits on every zone's page: %s" % long_[:4])
    K.save()


# ---------------------------------------------------------------------------------------------------------- MG30: the migration
def _units(L, props, kind="mining"):
    """every item of a kind's islands in base units (an Enchanted = 100 of its base, a bar = its ore) + the rare-find count; islands; totems; owned ores"""
    Isl, Core = L["ShIsl"], L["ShCore"]
    from jpype import JString
    u = {}

    def put(i, n):
        b = Isl.enchBase(JString(i))
        if b is not None:
            i, n = str(b), n * 100
        o = Core.oreOfBar(JString(i))
        if o is not None:
            i = str(o)
        if n:
            u[i] = u.get(i, 0) + n
    isl = tot = 0
    own = set()
    for k_ in list(props):
        m = re.match(r"^%s\.i(\d+)\.type$" % kind, k_)
        if not m:
            continue
        isl += 1
        b = "%s.i%s." % (kind, m.group(1))
        t = int(Isl.ofKey(MI, JString(props[k_])))
        own.add(props[k_])
        for o_ in props.get(b + "ores", "").split(","):
            if o_.strip():
                own.add(o_.strip())
        tt = [x for x in props.get(b + "totems", "").split(",") if x.strip()]
        tot += len(tt)
        st = int(props.get(b + "stored", "0") or 0)
        if st:
            sm = any(x.startswith("autosmelt_pole") for x in tt) and str(Isl.SMELT[t])
            put(str(Isl.SMELT[t]) if sm else str(Isl.PROD[t]), st)
        lg = props.get(b + "legacy", "")
        if ":" in lg:
            put(lg.rsplit(":", 1)[0], int(lg.rsplit(":", 1)[1]))
        for part in props.get(b + "drops", "").split(","):
            if ":" in part:
                put(part.rsplit(":", 1)[0], int(part.rsplit(":", 1)[1]))
        e = int(props.get(b + "ench", "0") or 0)
        if e:
            u["#rare"] = u.get("#rare", 0) + e
    return u, isl, tot, own


def _file(sd, k, body):
    f = os.path.join(sd, k + ".properties")
    open(f, "w", newline="\n").write(body)
    return f


def _log(sd):
    lg = ""
    for root_, dirs_, fs_ in os.walk(os.path.dirname(sd)):
        for fn_ in fs_:
            if fn_.startswith("collect") and fn_.endswith(".log"):
                lg += open(os.path.join(root_, fn_), encoding="utf8", errors="replace").read()
    return lg


def _copy(L, p, q):
    """the OWNER profile's Mining = another profile's (the page reads the player's own profile)"""
    def f():
        for k_ in list(p.stringPropertyNames()):
            if str(k_).startswith("mining."):
                p.remove(k_)
        for k_ in list(q.stringPropertyNames()):
            if str(k_).startswith("mining."):
                p.setProperty(k_, q.getProperty(k_))
        if p.getProperty("mining.placed") is None:
            p.setProperty("mining.placed", L["W_"] + "|1|2|3")   # the shard is placed on the player's island (the page's owner check)
    _set(L, p, f)


def run_mig(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = T428._env(scratch, K, "mg")
    St, Isl, Ck, Core = L["ShStore"], L["ShIsl"], L["ShClk"], L["ShCore"]
    sd = L["sd"]
    L0 = int(Isl.LAD0[MI])
    keys = [str(Isl.KEY[L0 + i]) for i in range(int(Isl.LADN[MI]))]
    Core.NOW_TEST = T0
    hdr = "v=1\npkey=%s\nmap.done=1\nclk.done=1\nclk2.done=1\nforms=1\nmining.auto=1\nmining.storage=3\nmining.compactor=1\nmining.paused=0\n"
    # A: Iron (slot 0, bigger) + Copper (slot 1, the quarry), Zone 3 Cobalt + Chromium, Zone 2 Lead alone
    kA = "00000000-0000-0000-0000-0000000a3001-p1"
    body = (hdr % kA) + (
        "mining.i1.type=copper\nmining.i1.size=2\nmining.i1.amt=5\nmining.i1.deco=5\nmining.i1.irr=3\nmining.i1.luck=1\nmining.i1.nsize=2\nmining.i1.last=%d\n"
        "mining.i1.stored=40\nmining.i1.drops=Ore_Copper\\:5,Rock_Stone_Cobble\\:10\nmining.i1.cave=2\nmining.i1.centre=1\n"
        "mining.i1.totems=quarry_spirit\\:2\\:wider\\:wider\\:0\\:57222b9d720b,autosmelt_pole\\:1\\:\\:\\:0\\:a93bd45cb173\n"
        "mining.i0.type=iron\nmining.i0.size=3\nmining.i0.amt=1\nmining.i0.deco=2\nmining.i0.irr=0\nmining.i0.nsize=4\nmining.i0.smithy=1\nmining.i0.alloyPct=70\n"
        "mining.i0.last=%d\nmining.i0.stored=4579\nmining.i0.legacy=Skyy_Ench_Iron\\:3\nmining.i0.drops=Ore_Iron\\:7,Ore_Silver\\:2\nmining.i0.ench=2\nmining.i0.cave=2\n"
        "mining.i0.totems=quarry_spirit\\:2\\:wider\\:faster\\:0\\:85105ea1fda7,geode_pole\\:1\\:\\:\\:0\\:ab12cd34ef56\n"
        "mining.i2.type=%s\nmining.i2.size=1\nmining.i2.last=%d\nmining.i2.stored=11\nmining.i2.totems=quarry_spirit\\:1\n"
        "mining.i3.type=%s\nmining.i3.size=1\nmining.i3.amt=4\nmining.i3.last=%d\nmining.i3.stored=13\nmining.i3.totems=quarry_spirit\\:1\\:\\:\\:0\\:cc01\n"
        "mining.i5.type=%s\nmining.i5.size=1\nmining.i5.last=%d\nmining.i5.stored=3\n") % (T0, T0, keys[4], T0, keys[5], T0, keys[3], T0)
    fA = _file(sd, kA, body)
    raw0 = open(fA, "rb").read()
    bA = T427._props(fA)
    uA = _units(L, bA)
    m0, w0 = int(St.MZMIG.get()), int(St.MZWAIT.get())
    St.CACHE.remove(kA)
    q = St.get(JString(kA))
    aA = T427._props(fA)
    uA2 = _units(L, aA)
    K.check(str(q.getProperty("mzone.done")) == "1" and aA.get("mzone.done") == "1" and int(St.MZMIG.get()) == m0 + 1, "MG the marker, saved, counted")
    K.check(not any(k_.startswith("mining.i0.") for k_ in aA) and not any(k_.startswith("mining.i3.") for k_ in aA), "MG Iron (slot 0) and %s (slot 3) folded: their keys gone" % keys[5])
    K.eq(aA.get("mining.i1.ores"), "iron", "MG Zone 1: the Copper quarry (slot 1, the lowest tier) lists Iron")
    K.eq(aA.get("mining.i2.ores"), keys[5], "MG Zone 3: the %s quarry lists %s" % (keys[4], keys[5]))
    K.check(aA.get("mining.i5.type") == keys[3] and "mining.i5.ores" not in aA, "MG Zone 2: the lone %s island stays (it IS the Zone 2 quarry)" % keys[3])
    # size + subs: Copper Medium 5/5/3 (eff 10/10/8), Iron Large 1/2/0 (eff 11/12/10) -> Large 1/2/0 ... the higher effective each
    sub = (aA.get("mining.i1.size"), aA.get("mining.i1.amt"), aA.get("mining.i1.deco"), aA.get("mining.i1.irr"))
    K.eq(sub, ("3", "1", "2", "0"), "MG Zone 1: Large; Ore Amount / Decorations / Springs = the higher effective level (Iron's 11 / 12 / 10 > Copper's 10 / 10 / 8)")
    K.check((aA.get("mining.i1.nsize"), aA.get("mining.i1.luck"), aA.get("mining.i1.smithy"), aA.get("mining.i1.alloyPct")) == ("4", "1", "1", "70"),
            "MG ... Vein size 4 (Iron's), Lucky 1 (Copper's), Smithy II (Iron's) with its slider 70")
    K.eq(aA.get("mining.i2.amt"), "4", "MG Zone 3: Ore Amount 4 (the folded island's, both Small)")
    tl = aA.get("mining.i1.totems", "").split(",")
    K.check(tl == ["quarry_spirit:2:wider:wider:0:57222b9d720b", "autosmelt_pole:1:::0:a93bd45cb173", "quarry_spirit:2:wider:faster:0:85105ea1fda7", "geode_pole:1:::0:ab12cd34ef56"],
            "MG ... every totem (the quarry's first, tiers + modifiers + uids kept): %s" % tl)
    K.check(uA2[0] == uA[0] and uA2[2] == uA[2] and uA2[1] == uA[1] - 2 and uA2[3] == uA[3],
            "MG items (base units) / totems / owned ores the same, islands %d -> %d: %s" % (uA[1], uA2[1], uA2[0]))
    d1 = T425._drops(q, 1, "mining")
    K.check(d1.get(FE, 0) == 4579 + 7 and d1.get(BFE, 0) == 300 and d1.get("Ore_Silver") == 2 and d1.get(CU) == 5 and int(aA.get("mining.i1.ench", "0")) == 2,
            "MG ... Iron's stock 4579 + 7 drops -> 4586 Iron Ore, its 3 Enchanted Iron (made of bars) -> 300 Iron Bars, in the quarry's storage; rare finds 2 (%s)" % d1)
    hist = os.path.join(sd, "history", "clicker", kA + ".pre-0.4.30.properties")
    K.check(os.path.isfile(hist) and open(hist, "rb").read() == raw0, "MG the History copy = the old file (byte-checked)")
    lg = _log(sd)
    K.check("mining zone migration" in lg and kA in lg and "Undo" in lg and "Iron (slot 0) -> the Copper quarry (slot 1)" in lg, "MG the collect.log journal line names the fold + the Undo")
    raw1 = open(fA, "rb").read()
    St.CACHE.remove(kA)
    St.get(JString(kA))
    K.check(open(fA, "rb").read() == raw1 and int(St.MZMIG.get()) == m0 + 1, "MG a second load changes nothing")
    # fixer 2: a rollback to 0.4.29 re-buys Iron as an island (slot 0 is free again), then 0.4.30 again: it folds too, despite mzone.done
    with open(fA, "ab") as fh:
        fh.write(("mining.i0.type=iron\nmining.i0.size=1\nmining.i0.last=%d\nmining.i0.stored=50\nmining.i0.drops=Ore_Iron\\:3\n"
                  "mining.i0.totems=quarry_spirit\\:1\\:\\:\\:0\\:dd0199\n" % T0).encode("utf8"))
    rawR = open(fA, "rb").read()
    bR = T427._props(fA)
    uR = _units(L, bR)
    dR0 = T425._drops(q, 1, "mining").get(FE, 0)
    St.CACHE.remove(kA)
    qR = St.get(JString(kA))
    aR = T427._props(fA)
    uR2 = _units(L, aR)
    K.check(int(St.MZMIG.get()) == m0 + 2 and not any(k_.startswith("mining.i0.") for k_ in aR) and aR.get("mining.i1.ores") == "iron",
            "MG2 a 0.4.29 re-bought Iron island folds on the next 0.4.30 load (marker set): its keys gone, Iron listed once (%s)" % aR.get("mining.i1.ores"))
    K.check(uR2[0] == uR[0] and uR2[2] == uR[2] and uR2[1] == uR[1] - 1 and uR2[3] == uR[3],
            "MG2 ... items (base units) / totems / owned ores the same, islands %d -> %d" % (uR[1], uR2[1]))
    dR = T425._drops(qR, 1, "mining")
    K.check(dR.get(FE, 0) == dR0 + 53 and aR.get("mining.i1.totems", "").endswith("quarry_spirit:1:::0:dd0199"),
            "MG2 ... its 50 stock + 3 drops -> the quarry's Iron Ore (%d -> %d), its spirit appended" % (dR0, dR.get(FE, 0)))
    hl = [f_ for f_ in os.listdir(os.path.join(sd, "history", "clicker")) if f_.startswith(kA + ".pre-0.4.30.") and f_ != kA + ".pre-0.4.30.properties"]
    K.check(len(hl) == 1 and open(os.path.join(sd, "history", "clicker", hl[0]), "rb").read() == rawR and open(hist, "rb").read() == raw0,
            "MG2 ... a new timestamped History copy (%s); the first copy untouched" % hl)
    K.check("already on its Ores row - bought again under 0.4.29" in _log(sd), "MG2 ... the journal says Iron was bought twice (nothing refunded)")
    raw2 = open(fA, "rb").read()
    St.CACHE.remove(kA)
    q = St.get(JString(kA))
    K.check(open(fA, "rb").read() == raw2 and int(St.MZMIG.get()) == m0 + 2, "MG2 ... and the load after that changes nothing")
    # the page on the folded file: Zone 1 = Copper + Iron, Open, Iron nodes
    cs = T427._give(L, [("Tool_Pickaxe_Iron", 1)])
    Core.NOW_TEST = T0
    _copy(L, p, q)
    pg = T427._page(L, ou, W_, MI)
    L["ShClk"].HAND_TEST = "Tool_Pickaxe_Iron"
    T49._build(pg)
    K.check(int(pg.ckSlot) == 1 and str(pg.ckChip).startswith("Zone 1 Quarry - Large") and str(pg.ckMS[0]).startswith("Shown now - 2 / 2 ores") and str(pg.ckTexA[1]).endswith("ClkQNode1.png"),
            "MG the folded quarry on the page: Large, 2 / 2 ores, Iron nodes (%s / %s / %s / %s)" % (pg.ckChip, pg.ckMS[0], pg.ckCap, pg.stText))
    K.check(str(pg.ckMS[6]).startswith("Yours - 2 / 2 ores") and str(pg.ckMS[3]).startswith("Yours - 1 / 2 ores; add %s inside" % str(Isl.NAME[L0 + 2])), "MG ... Zone 3 Yours 2 / 2, Zone 2 Yours 1 / 2 (%s / %s)" % (pg.ckMS[6], pg.ckMS[3]))
    # B: Iron alone in Zone 1 = the quarry; Copper = its Ores row
    kB = "00000000-0000-0000-0000-0000000a3002-p1"
    fB = _file(sd, kB, (hdr % kB) + "mining.i0.type=iron\nmining.i0.size=1\nmining.i0.last=%d\nmining.i0.stored=9\n" % T0)
    rB = open(fB, "rb").read()
    c0 = int(St.MZCHK.get())
    St.CACHE.remove(kB)
    qB = St.get(JString(kB))
    St.LOCK.lock()
    try:
        bs, nx = int(Ck.baseSlot(qB, 1)), int(Isl.nextTier(MI, qB))
    finally:
        St.LOCK.unlock()
    K.check(open(fB, "rb").read() == rB and qB.getProperty("mzone.done") is None and int(St.MZCHK.get()) == c0 + 1 and bs == 0 and nx == 0
            and not os.path.isfile(os.path.join(sd, "history", "clicker", kB + ".pre-0.4.30.properties")),
            "MG an Iron island alone: it is the Zone 1 quarry, Copper is next (its Ores row); nothing written, no marker")
    _copy(L, p, qB)
    pg = T427._page(L, ou, W_, MI)
    T49._build(pg)
    K.check(str(pg.ckChip).startswith("Zone 1 Quarry") and str(pg.ckUpE[8]) == "Add Copper: more ore nodes" and bool(pg.ckUpOk[8]) and int(pg.ckUpSeen[8]) == 0,
            "MG ... its page: the Iron quarry offers Copper on the Ores row (%s)" % pg.ckUpE[8])
    # refused cases: nothing changes
    def refused(kx, extra, what, setup=None, undo=None):
        fx = _file(sd, kx, (hdr % kx) + "mining.i0.type=copper\nmining.i0.size=1\nmining.i0.last=%d\nmining.i0.stored=5\nmining.i1.type=iron\nmining.i1.size=1\nmining.i1.last=%d\nmining.i1.stored=6\n%s" % (T0, T0, extra))
        r0 = open(fx, "rb").read()
        b0 = T427._props(fx)
        wv = int(St.MZWAIT.get())
        if setup:
            setup()
        St.CACHE.remove(kx)
        qx = St.get(JString(kx))
        if undo:
            undo()
        K.check(open(fx, "rb").read() == r0 and qx.getProperty("mzone.done") is None and qx.getProperty("mining.i1.type") == "iron" and qx.getProperty("mining.i0.ores") is None
                and int(St.MZWAIT.get()) == wv + 1 and str(qx.getProperty("mining.i1.stored")) == "6", "MG %s: nothing changes (file, memory), counted as waiting" % what)
        return fx, b0
    refused("00000000-0000-0000-0000-0000000a3003-p1", "mining.i1.weird=1\n", "an unknown island key")
    refused("00000000-0000-0000-0000-0000000a3004-p1", "", "a failing totals check", lambda: setattr(St, "MZ_FAIL_TEST", True), lambda: setattr(St, "MZ_FAIL_TEST", False))
    fx, _b = refused("00000000-0000-0000-0000-0000000a3005-p1", "", "a refused save", lambda: setattr(St, "FAIL_TEST", True), lambda: setattr(St, "FAIL_TEST", False))
    St.CACHE.remove("00000000-0000-0000-0000-0000000a3005-p1")
    q5 = St.get(JString("00000000-0000-0000-0000-0000000a3005-p1"))
    K.check(q5.getProperty("mzone.done") == "1" and q5.getProperty("mining.i0.ores") == "iron", "MG ... the next load (the disk writes again) migrates it")
    hd = os.path.join(sd, "history", "clicker")
    kh = "00000000-0000-0000-0000-0000000a3006-p1"
    blocker = os.path.join(hd, kh + ".pre-0.4.30.properties")
    os.makedirs(blocker, exist_ok=True)   # a folder where the copy goes: the copy cannot be written
    refused(kh, "", "a refused History copy")
    shutil.rmtree(blocker)
    K.save()


# ---------------------------------------------------------------------------------------------------------- FX30: the fixer's checks
def _quarry(L, p, ores="iron", pole=False, owed=None):
    T424._mining(L, p, size=2, amt=5, pole=pole)
    def f():
        for k_ in list(p.stringPropertyNames()):
            if str(k_).startswith("mining.i1.") or str(k_) in ("mining.i0.drops", "mining.i0.orr", "mining.i0.xpr", "owed.xp.Mining", "mining.i0.legacy", "mining.compactor"):
                p.remove(k_)
        if ores:
            p.setProperty("mining.i0.ores", ores)
        if owed is not None:
            p.setProperty("owed.xp.Mining", str(owed))
    _set(L, p, f)


def run_fix(out, jar, scratch, _home):
    from jpype import JString, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = T428._env(scratch, K, "fx")
    St, Isl, Ck, Cfg, Core, M = L["ShStore"], L["ShIsl"], L["ShClk"], L["ShCfg"], L["ShCore"], L["ShMath"]
    per, pct0 = int(Cfg.xpOf(MI)), int(Cfg.XP_PCT)
    K.check(per > 0, "FX Mining XP per item > 0 (%d)" % per)

    def settle(q, now):
        St.LOCK.lock()
        try:
            return int(M.settle(MI, q, 0, JLong(now)))
        finally:
            St.LOCK.unlock()

    def base0():
        return int(M.baseOf(MI, p, 0))
    # 1. no ore upgrade: exactly as before (all stock, nothing in .drops, no new key)
    _quarry(L, p, ores=None)
    made0 = settle(p, T0 + 3600000)
    K.check(made0 > 10 and base0() == made0 and p.getProperty("mining.i0.drops") is None and p.getProperty("mining.i0.orr") is None
            and p.getProperty("owed.xp.Mining") is None and p.getProperty("mining.i0.xpr") is None,
            "FX a quarry with no ore upgrade: its spirits make %d Copper, all stock, nothing written beyond 0.4.29's keys" % made0)
    # 2. Copper + Iron upgrade: the same count, shared (Copper stock, Iron in storage), the XP for the Iron owed at once
    _quarry(L, p, ores="iron")
    made1 = settle(p, T0 + 3600000)
    d = T425._drops(p, 0, "mining")
    fe = d.get(FE, 0)
    K.check(made1 == made0 and base0() + fe == made1 and fe == made1 // 2 and base0() == made1 - made1 // 2 and set(d) == {FE},
            "FX Copper + Iron: the same %d made, shared - %d Copper stock + %d Iron Ore in storage (%s)" % (made1, base0(), fe, d))
    K.check(int(p.getProperty("owed.xp.Mining") or 0) * 100 + int(p.getProperty("mining.i0.xpr") or 0) == fe * per * pct0,
            "FX ... the Iron's Collect XP owed at once: owed.xp.Mining %s (+ %s hundredths) = %d x %d x %d%%" % (p.getProperty("owed.xp.Mining"), p.getProperty("mining.i0.xpr"), fe, per, pct0))
    # 3. the Auto-Smelt Pole: the Iron share comes as bars
    _quarry(L, p, ores="iron", pole=True)
    made2 = settle(p, T0 + 3600000)
    d = T425._drops(p, 0, "mining")
    K.check(made2 > 0 and d.get(BFE, 0) == made2 // 2 and FE not in d, "FX ... with the Auto-Smelt Pole the Iron share is Iron Bars (%s)" % d)
    # 4. round robin + the XP fraction carried (shard.xpPercent 33, one item at a time)
    _quarry(L, p, ores="iron", owed=5)
    seq = []
    Cfg.XP_PCT = 33
    try:
        St.LOCK.lock()
        try:
            for _ in range(6):
                seq.append(int(M.oreShare(MI, p, 0, JLong(1))))
            big = int(M.oreShare(MI, p, 0, JLong(7)))
        finally:
            St.LOCK.unlock()
    finally:
        Cfg.XP_PCT = pct0
    K.check(seq == [0, 1, 0, 1, 0, 1] and big == 3, "FX one item at a time: Copper, Iron, Copper, Iron ... then 7 -> 3 Iron (%s, %d)" % (seq, big))
    tot = 3 + big
    K.check(int(p.getProperty("owed.xp.Mining")) == 5 + (tot * per * 33) // 100 and int(p.getProperty("mining.i0.xpr") or 0) == (tot * per * 33) % 100,
            "FX ... shard.xpPercent 33: no XP fraction lost on small settles (owed %s, carried %s)" % (p.getProperty("owed.xp.Mining"), p.getProperty("mining.i0.xpr")))
    # 5. junk / another zone's ore on the line shares nothing extra; Foraging never shares
    _quarry(L, p, ores="thorium,nonsense")
    St.LOCK.lock()
    try:
        sh = [str(Isl.NAME[int(x)]) for x in M.shareOres(MI, p, 0)]
    finally:
        St.LOCK.unlock()
    T423._foraging(L, p)
    St.LOCK.lock()
    try:
        p.setProperty("foraging.i0.ores", "birch")
        fsh = len(M.shareOres(FO, p, 0))
        p.remove("foraging.i0.ores")
    finally:
        St.LOCK.unlock()
    K.check(sh == ["Copper"] and fsh == 0, "FX a Zone 2 ore / junk on the line: Copper alone (%s); Foraging never shares" % sh)
    # 6. the spirit row says "ore a minute" on a shared quarry, the ore's name otherwise
    T427._give(L, [("Tool_Pickaxe_Iron", 1)])
    Ck.HAND_TEST = "Tool_Pickaxe_Iron"
    for ores, want in ((None, "Copper Ore a minute"), ("iron", " ore a minute")):
        _quarry(L, p, ores=ores)
        Core.NOW_TEST = T0
        pg = T427._page(L, ou, W_, MI)
        T49._build(pg)
        K.check(str(pg.ckUpE[2]).endswith(want) and len(str(pg.ckUpE[2])) <= 38, "FX the spirit row (%s): %s" % (ores, pg.ckUpE[2]))
    # 7. Collect all: the Copper stock (Collect pays its XP) + the Iron in storage (its XP was owed) - the owed XP is paid with it
    _quarry(L, p, ores="iron")
    Core.NOW_TEST = T0 + 3600000
    cs = T427._give(L, [])
    settle(p, T0 + 3600000)
    ow = int(p.getProperty("owed.xp.Mining") or 0)
    r = str(Core.collect(ou, JString(OWNER), MI, -1, cs))
    K.check(r.startswith("+") and p.getProperty("mining.i0.drops") is None and int(M.baseOf(MI, p, 0)) == 0, "FX Collect all takes the Copper stock + the Iron (%s)" % r[:120])
    K.check(ow > 0 and int(p.getProperty("owed.xp.Mining") or 0) == 0, "FX ... the owed Iron XP (%d) is paid with that Collect" % ow)
    # 8. the migration: the folded stock's XP is owed (Collect pays none for .drops)
    sd = L["sd"]
    Core.NOW_TEST = T0
    kx = "00000000-0000-0000-0000-0000000a3101-p1"
    _file(sd, kx, ("v=1\npkey=%s\nmap.done=1\nclk.done=1\nclk2.done=1\nforms=1\nmining.auto=1\nmining.storage=3\nmining.paused=0\n" % kx) +
          ("mining.i0.type=copper\nmining.i0.size=1\nmining.i0.last=%d\nmining.i0.stored=5\nmining.i0.totems=quarry_spirit\\:1\\:\\:\\:0\\:fx01\n"
           "mining.i1.type=iron\nmining.i1.size=1\nmining.i1.last=%d\nmining.i1.stored=100\nmining.i1.legacy=Skyy_Ench_Iron\\:2\nmining.i1.drops=Ore_Iron\\:9\n"
           "mining.i1.totems=quarry_spirit\\:1\\:\\:\\:0\\:fx02\nowed.xp.Mining=4\n" % (T0, T0)))
    St.CACHE.remove(kx)
    q = St.get(JString(kx))
    want = 4 + (300 * per * pct0) // 100
    K.check(q.getProperty("mzone.done") == "1" and int(q.getProperty("owed.xp.Mining")) == want and "Mining XP owed" in _log(sd),
            "FX the fold owes the Collect XP of Iron's 100 stock + 2 Enchanted (300 units; not its 9 clicked drops): owed.xp.Mining 4 -> %s (want %d); journal says so" % (q.getProperty("owed.xp.Mining"), want))
    # 9. after the fold the old Iron spirit's share is Iron again (2 spirits, 2 ores)
    Core.NOW_TEST = T0 + 3600000
    d0 = T425._drops(q, 0, "mining")
    fe0 = d0.get(FE, 0)
    mk = settle(q, T0 + 3600000)
    fe1 = T425._drops(q, 0, "mining").get(FE, 0)
    K.check(fe0 + d0.get(BFE, 0) == 100 + 200 + 9 and mk > 0 and fe1 - fe0 == mk // 2, "FX ... then the quarry's 2 spirits make Copper AND Iron again (%d made, Iron in storage %d -> %d)" % (mk, fe0, fe1))
    K.save()


# ---------------------------------------------------------------------------------------------------------- live30: START TWICE on a scratch COPY of the live data
def run_live(out, jar, scratch, home):
    import jpype
    from jpype import JString, JClass
    K = HK.Child(out)
    sd = os.path.join(home, "shards")
    files = sorted(f for f in os.listdir(sd) if f.endswith(".properties"))
    pb = dict((f, T427._props(os.path.join(sd, f))) for f in files)
    raw0 = dict((f, open(os.path.join(sd, f), "rb").read()) for f in files)
    L, ou, W_, p, lv, got = T428._env(scratch, K, "lvenv")
    St = L["ShStore"]
    lasts = [int(v) for f in files for k_, v in pb[f].items() if re.match(r"^mining\.i\d+\.last$", k_)]
    L["ShCore"].NOW_TEST = min(lasts) if lasts else 0   # no production between the save and this start: before / after compare exactly
    St.DIR = JClass("java.nio.file.Paths").get(JString(sd), jpype.JArray(JString)([]))
    St.CACHE.clear()
    for f in files:
        St.get(JString(f[:-len(".properties")]))
    pa = dict((f, T427._props(os.path.join(sd, f))) for f in files)
    rows = {}
    for f in files:
        ub, ua = _units(L, pb[f]), _units(L, pa[f])
        zones = {}
        for k_, v in pb[f].items():
            if re.match(r"^mining\.i\d+\.type$", k_):
                z = int(L["ShIsl"].zoneOf(L["ShIsl"].ofKey(MI, JString(v))))
                zones[z] = zones.get(z, 0) + 1
        folded = sum(n - 1 for n in zones.values())
        rows[f] = {"owed.xp.Mining": [pb[f].get("owed.xp.Mining"), pa[f].get("owed.xp.Mining")], "islands": [ub[1], ua[1]], "totems": [ub[2], ua[2]], "items": [sum(v for k_, v in ub[0].items() if k_ != "#rare"), sum(v for k_, v in ua[0].items() if k_ != "#rare")],
                   "owned": sorted(ub[3]), "folded": folded}
        K.check(ua[1] == ub[1] - folded and ua[2] == ub[2] and ua[0] == ub[0] and ua[3] == ub[3],
                "L30 %s: islands %d -> %d (%d folded), totems %d kept, items (base units) the same, owned ores %s kept" % (f, ub[1], ua[1], folded, ua[2], sorted(ua[3])))
        if folded:
            K.check(pa[f].get("mzone.done") == "1" and os.path.isfile(os.path.join(sd, "history", "clicker", f[:-len(".properties")] + ".pre-0.4.30.properties")),
                    "L30 %s: the marker + the History copy" % f)
            hist = open(os.path.join(sd, "history", "clicker", f[:-len(".properties")] + ".pre-0.4.30.properties"), "rb").read()
            K.check(hist == raw0[f], "L30 %s: the History copy = the file before (byte-checked)" % f)
        else:
            K.check(open(os.path.join(sd, f), "rb").read() == raw0[f], "L30 %s: nothing to fold - not written" % f)
        other = sorted(k_ for k_ in set(pb[f]) | set(pa[f]) if pb[f].get(k_) != pa[f].get(k_) and not k_.startswith("mining.") and k_ not in ("mzone.done", "owed.xp.Mining"))
        K.check(not other, "L30 %s: no other shard's key rewritten %s" % (f, other[:6]))
        # the storage after the fold (said in the report)
        q = St.get(JString(f[:-len(".properties")]))
        St.LOCK.lock()
        try:
            for s in range(16):
                if L["ShMath"].hasIsland(MI, q, s):
                    rows[f]["slot%d" % s] = {"type": str(q.getProperty("mining.i%d.type" % s)), "ores": str(q.getProperty("mining.i%d.ores" % s)),
                                             "used": int(L["ShMath"].usedOf(MI, q, s)), "limit": int(L["ShMath"].limOf(MI, q, s)),
                                             "size/amt/deco/irr": [str(q.getProperty("mining.i%d.%s" % (s, x))) for x in ("size", "amt", "deco", "irr")],
                                             "totems": str(q.getProperty("mining.i%d.totems" % s))}
        finally:
            St.LOCK.unlock()
    raw1 = dict((f, open(os.path.join(sd, f), "rb").read()) for f in files)
    St.CACHE.clear()
    for f in files:
        St.get(JString(f[:-len(".properties")]))
    K.check(all(open(os.path.join(sd, f), "rb").read() == raw1[f] for f in files), "L30 the second start: nothing changes (every file byte for byte)")
    K.notes.append("L30 live copy: " + json.dumps(rows))
    print("L30 live copy: %s" % json.dumps(rows, indent=1))
    K.save()


EXPECT = {   # 0.4.29 -> 0.4.30
    'ShMath': ['+m oreShare', '+m oweXp', '+m shareOres', '~m settle'],
    'CfgFn': ['~m opExport'], 'CfgRows': ['~m header'], 'ShClk': ['+m buyOre', '+m buyOre0', '~m baseSlot', '~m mine', '~m zoneOwned'], 'ShCore': ['~m buyIsland0'],
    'ShFill': ['~m markFixed'], 'ShIsl': ['+m mineKd', '+m oreListed', '+m owns', '+m zoneSlot', '~m nextTier'],
    'ShPage': ['~<clinit>', '~m actQuarry', '~m buildClick', '~m ckPre', '~m ckSpirit', '~m fillQuarry'],
    'ShStore': ['+f MZCHK', '+f MZMIG', '+f MZWAIT', '+f MZ_DROP', '+f MZ_FAIL_TEST', '+f MZ_KEEP', '+m migrate5', '+m mzAdd', '+m mzBase', '+m mzFold', '+m mzIsl', '+m mzKnown',
                '+m mzLv', '+m mzOwn', '+m mzPut', '+m mzTot', '+m mzUnits', '+m snapZone', '~<clinit>', '~m get', '~m migrate', '~m migrate2', '~m migrate3', '~m migrate4', '~m save'],
    'SkyyShardsPlugin': ['~m setup'],
}

# 0.4.29's phases run whole; RETIRED 0.4.24 CHECKS = the per-ore map / caption / 8 rows they pinned is replaced on purpose (each reason is a 0.4.30 spec
# line; MP30 / MZ30 / MG30 check the new behaviour). A failing check whose text matches is counted as a note "retired ..." instead of a failure.
SKIP = {}
T427.RETIRED += [
    (r"^MU the Ore nodes row: Nodes \d+ -> \d+ / ", "SPEC 2: the quarry has a 9th row (Ores) - MP30 checks the 9 rows, the Ore nodes row included"),
    (r"^MZ the owned Cobalt island in locked Zone 3: open \(Yours - 1 / 2 ores", "SPEC 1: one card a zone - an owned quarry in a locked zone opens (MP30 'an owned zone in a locked zone')"),
    (r"^MZ Chromium not owned in Zone 3: locked \+ the lock picture", "SPEC 1/2: Chromium is no card any more - the Zone 3 quarry's Ores row (MP30)"),
    (r"^MZ Zone 1's two ores = the quarry shown: Shown now - 2 / 2 ores", "SPEC 1: one card a zone ('Shown now - 2 / 2 ores', MP30)"),
    (r"^MZ the map: 2 cards a zone \(no card 2 / 5 / 8 / 11\), 3 in zone 5", "SPEC 1: one card a zone (MP30: no 2nd / 3rd ore cards)"),
    (r"^MP FIX the Iron hint: .*Add Iron on the Ores row\.", "SPEC 2: Iron is added on the Ores row, not bought as an island (MP30 checks the caption)"),
]


PHASES = [("static", run_static), ("model30", run_model), ("page30", run_page), ("mig30", run_mig), ("fix30", run_fix)] + \
         [x for x in T429.PHASES if x[0] not in ("static", "livemig29") and x[0] not in SKIP] + [("livemig30", run_live)]


if __name__ == "__main__":
    HK.run_compare = T429._compare29
    ph = PHASES
    if "--only" in sys.argv and "--phase" not in sys.argv:
        want = set(HK.arg("--only").split(","))
        ph = [x for x in PHASES if x[0] in want]
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=ph, script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
