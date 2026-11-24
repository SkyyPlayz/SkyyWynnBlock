"""Harness for SkyyShards 0.4.31 (one island per zone for Foraging / Farming / Ranching / Orchard - tools/shards_0_4_31_patch.py, on top of 0.4.30).
Build first:
    python tools/shards_0_4_31_patch.py && python SkyyShards/build_skyyshards_0.4.31.py
    python SkyyShards/test_skyyshards_0.4.31.py [--keep] [--only label,label] [--dir <scratch>]

  S31  static   the patch re-runs to identical bytes; header / VERSION / ready line / rollback note; no new registerSystem / registerCommand; line
                endings kept; 0.4.30 never reads the four kinds' .ores / azone.done (rollback = ignored keys)
  AZ31 model    EXECUTED for each of the 4 kinds: owns / zoneOwnedK / baseSlotK / nextTier / isBase with the 2nd type as an island AND as an upgrade
                (identical answers); the clicks: the added type's spot gives EXACTLY what a lone island of that type gives (seeded), the base type's
                spot its own product; the spot pictures; a one-type island = the 0.4.30 page (no per-spot pictures); Combat: an ores line owns nothing
  AP31 page     EXECUTED for each of the 4 kinds: the map = one card a zone (names, Shown now n / m, add X inside, First add, Locked, Buy), the 7th row
                (have / need lines = the 0.4.30 island price), the Add button (ku6:1), refused cases (too few items / coins, stale profile, the 2nd type
                as an island, tier order), bought (exact coins + items, saved), a double click buys once, the zone 2 island from its card (kb3), Open
                every owned zone (km), a locked zone, every row line fits; the cost table printed
  AG31 migration EXECUTED on files: Farming Wheat + Lettuce + Carrot (seed store, Eternal seeds, legacy Enchanted, stock, drops, XP tracking), Corn
                alone in Zone 2; Foraging Oak + Beech + Maple, Dry alone; Ranching Chicken + Cow; Orchard Apple + Berries; + a Mining fold in the same
                file (migrate5 then migrate6); every kind's totals before = after; History copy byte-checked, journal, ONE save, the 2nd load changes
                nothing; a re-bought island folds again; a lone 2nd type stays the zone island; refused cases change nothing
  AX31 spirits  the zone island's spirits share their output over its types (Farming: the crop XP owed at the spirits' XP; the stock's XP tracking
                counts only the stock), no upgrade = exactly 0.4.30, Ranching shares too, the spirit row word, Collect all pays the owed XP
  then 0.4.30's phases (minus the ones that pin the per-type map: RETIRED with why) on THIS jar, A verify, C compare, AA audit,
  live31 START TWICE on a scratch copy of the live data: per file and kind islands before - folded = after, totems, items (base units + seed
                stores + Eternal seeds) and owned types the same, markers + History copies, the second start changes nothing
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.31"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "azone1", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.30.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.30.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_31_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.30 harness (it loads 0.4.29 -> ... older): its version moves to this one in memory
_T30 = open(os.path.join(HERE, "test_skyyshards_0.4.30.py"), encoding="utf8").read()
assert _T30.count('VERSION = "0.4.30"\n') == 1, "the 0.4.30 harness changed"
_T30 = _T30.replace('VERSION = "0.4.30"\n', 'VERSION = "%s"\n' % VERSION)
_argv = list(sys.argv)
T430 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_30", loader=None))
T430.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.30.py")
exec(compile(_T30, T430.__file__, "exec"), T430.__dict__)
sys.argv[:] = _argv
T429, T428 = T430.T429, T430.T428
T427, T426, T425, T424, T423 = T430.T427, T430.T426, T430.T425, T430.T424, T430.T423
T419, T49, T410, T411, T416 = T430.T419, T430.T49, T430.T410, T430.T411, T430.T416
for _m in (T430, T429, T428):
    _m.JAR = JAR
    _m.SCRATCH = SCRATCH
OWNER = T428.OWNER
MI, FO, FK, RA, OR, CK = 0, 1, 2, 3, 4, 5
T0 = T428.T0
ZK = [dict(kd=FO, kind="foraging", base="oak", hand="Tool_Hatchet_Iron", skill="Foraging", zw="grove", Zw="Grove", tw="tree", tws="trees", Tws="Trees",
           spw="trees", worker="lumber_spirit", placed="|1|2|3", fell="+Felled"),
      dict(kd=FK, kind="farming", base="wheat", hand=None, skill="Farming", zw="farm", Zw="Farm", tw="crop", tws="crops", Tws="Crops",
           spw="plots", worker="harvest_spirit", placed="|1|2|3", fell="+Harvested"),
      dict(kd=RA, kind="ranching", base="chicken", hand=None, skill="Ranching", zw="ranch", Zw="Ranch", tw="animal", tws="animals", Tws="Animals",
           spw="animals", worker="harvest_spirit", placed="|3|5|6", fell="+Tended"),
      dict(kd=OR, kind="orchard", base="apple", hand=None, skill="Orchard", zw="orchard", Zw="Orchard", tw="fruit", tws="fruits", Tws="Fruits",
           spw="fruit trees", worker="harvest_spirit", placed="|4|5|6", fell="+Picked")]


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.31 - build script') and 'VERSION = "0.4.31"\n' in g, "S31 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S31 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.31:" in g, "S31 the ready line names the round")
    K.check("ROLLBACK 0.4.31 -> 0.4.30 alone" in g and "SAVED DATA: <kind>.i<n>.ores for foraging / farming / ranching / orchard" in g, "S31 the rollback + saved-data notes")
    K.check("azone.done" not in o and "public static boolean zoned" not in o and "if (!mineKd(kd)) return false;" in o,
            "S31 0.4.30 owns() reads .ores for Mining only and never azone.done (a rollback ignores the four kinds' upgrades)")
    K.check("COMBAT is NOT changed" in g and "MINING is NOT changed" in g, "S31 the notes say Combat + Mining are unchanged")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S31 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S31 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S31 jar newer than the script, the script newer than the patch")
    K.save()


def _set(L, p, fn):
    St = L["ShStore"]
    St.LOCK.lock()
    try:
        fn()
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()


def _keys(L, kd):
    Isl = L["ShIsl"]
    L0 = int(Isl.LAD0[kd])
    return [str(Isl.KEY[L0 + i]) for i in range(int(Isl.LADN[kd]))], [str(Isl.NAME[L0 + i]) for i in range(int(Isl.LADN[kd]))]


def _zfix(L, p, z, rows, ores=None, amt=5, irr=0, deco=0, totems=True):
    """one zoned kind: rows = [(slot, type key, size)]; every island the same sub levels; a worker totem each (or none)"""
    kind = z["kind"]

    def f():
        for k_ in list(p.stringPropertyNames()):
            if str(k_).startswith(kind + "."):
                p.remove(k_)
        for s, ty, sz in rows:
            b = "%s.i%d." % (kind, s)
            p.setProperty(b + "type", ty); p.setProperty(b + "size", str(sz)); p.setProperty(b + "last", str(T0)); p.setProperty(b + "stored", "0")
            p.setProperty(b + "amt", str(amt)); p.setProperty(b + "irr", str(irr)); p.setProperty(b + "deco", str(deco))
            if totems:
                p.setProperty(b + "totems", "%s:1:::0:az%02d%02d" % (z["worker"], z["kd"], s))
        if ores:
            p.setProperty("%s.i%d.ores" % (kind, rows[0][0]), ores)
        p.setProperty(kind + ".auto", "1"); p.setProperty(kind + ".paused", "0"); p.setProperty(kind + ".storage", "5")
        p.setProperty(kind + ".placed", L["W_"] + z["placed"])
    _set(L, p, f)


def _env(scratch, K, name):
    L, ou, W_, p, lv, got = T428._env(scratch, K, name)
    for z in ZK:
        lv[z["skill"]] = 100
    L["coins"]["bal"] = 10 ** 12
    L["ShClk"].HAND_TEST = None
    L["ShCfg"].CK_CPS = 1000
    return L, ou, W_, p, lv, got


def _cost(L, kd, li):
    Isl, Cfg, Core = L["ShIsl"], L["ShCfg"], L["ShCore"]
    t = int(Isl.LAD0[kd]) + li
    coins = int(Isl.coins(Cfg.BUY_H, Core.tierCv(t)))
    m = Isl.mats(kd, t, Cfg.BUY_ITEMS[kd], 0, 1)
    return coins, dict(zip([str(x) for x in m[0]], [int(x) for x in m[1]]))


def _items(L, ids):
    T411.T48.add_items([(i, 9999) for i in sorted(set(ids)) if i])


def _click(L, ou, z, slot, spot, now, seed, n=120):
    from jpype import JString, JClass, JLong
    Ck, Core = L["ShClk"], L["ShCore"]
    Core.NOW_TEST = now
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed))
    s = ""
    try:
        for _ in range(n):
            r = Ck.chop(ou, JString(OWNER), z["kd"], slot, spot, JString(z["hand"]) if z["hand"] else None)
            s = str(r[0])
            if s.startswith("+") or s.startswith("-"):
                break
    finally:
        Ck.RND_TEST = None
    return s


# ---------------------------------------------------------------------------------------------------------- AZ31: the model
def run_model(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "az")
    St, Isl, Ck, Cfg, Core = L["ShStore"], L["ShIsl"], L["ShClk"], L["ShCfg"], L["ShCore"]
    _items(L, ["Tool_Hatchet_Iron"])
    for zi, z in enumerate(ZK):
        kd, kind = z["kd"], z["kind"]
        keys, names = _keys(L, kd)
        L0 = int(Isl.LAD0[kd])
        K.check(bool(Isl.zoned(kd)) and [int(Isl.zoneOf(L0 + i)) for i in range(3)] == [1, 1, 1] and int(Isl.zoneOf(L0 + 3)) == 2,
                "AZ %s is zoned; ladder 0-2 = Zone 1, 3 = Zone 2 (%s)" % (kind, names[:4]))
        res = {}
        for model in ("island", "upgrade"):
            if model == "island":
                _zfix(L, p, z, [(0, keys[0], 2), (1, keys[1], 2)])
            else:
                _zfix(L, p, z, [(0, keys[0], 2)], ores=keys[1])
            St.LOCK.lock()
            try:
                ow = [bool(Isl.owns(kd, p, L0 + i)) for i in range(len(keys))]
                zo = [str(Isl.NAME[int(x)]) for x in Ck.zoneOwnedK(kd, p, 1)]
                res[model] = (ow, zo, int(Ck.baseSlotK(kd, p, 1)), int(Isl.nextTier(kd, p)), bool(Ck.isBase(p, kd, 0)), int(Isl.slotOf(kd, p, L0 + 1)),
                              bool(Ck.isBase(p, kd, 1)) if model == "island" else None)
            finally:
                St.LOCK.unlock()
        K.eq(res["island"][:5], res["upgrade"][:5], "AZ %s owns / zoneOwnedK / baseSlotK / nextTier / isBase: %s as an island = as an upgrade %s" % (kind, names[1], res["upgrade"][:5],))
        K.check(res["island"][5] == 1 and res["upgrade"][5] == -1 and res["upgrade"][1] == names[:2] and res["upgrade"][3] == 2 and res["island"][6] is False,
                "AZ %s ... the upgrade has no island, the zone island has %s + %s, next = rank 2; a 2nd island of the zone is not its base" % (kind, names[0], names[1]))
        # the clicks: the added type's spot = exactly a lone island of that type (seeded); spot 0 = the base type
        for model in ("upgrade", "lone"):
            Ck.XPA.clear()   # the XP fractions in memory: both models start from none
            if model == "upgrade":
                _zfix(L, p, z, [(0, keys[0], 2)], ores=keys[1], totems=False)
            else:
                _zfix(L, p, z, [(0, keys[1], 2)], totems=False)
            now = T0 + (10 + 4 * zi + (1 if model == "lone" else 0)) * 3600000
            s1 = _click(L, ou, z, 0, 1, now, 700 + zi)
            d1 = dict(T425._drops(p, 0, kind))
            res[model] = (s1, d1)
        K.check(res["upgrade"] == res["lone"] and res["upgrade"][0].startswith(z["fell"]) and names[1] in res["upgrade"][0],
                "AZ %s: the %s spot on the zone island gives EXACTLY what a lone %s island gives (seeded): %s / %s" % (kind, names[1], names[1], res["upgrade"], res["lone"]))
        _zfix(L, p, z, [(0, keys[0], 2)], ores=keys[1], totems=False)
        s0 = _click(L, ou, z, 0, 0, T0 + (30 + zi) * 3600000, 900 + zi)
        K.check(s0.startswith(z["fell"]) and names[0] in s0 and names[1] not in s0, "AZ %s: spot 0 = the base type %s (%s)" % (kind, names[0], s0[:80]))
        # a stale slot (a 2nd island of the zone, before its fold): nothing
        _zfix(L, p, z, [(0, keys[0], 2), (1, keys[1], 2)], totems=False)
        s2 = _click(L, ou, z, 1, 0, T0 + (40 + zi) * 3600000, 950 + zi, n=3)
        K.check(s2 == "" or s2.startswith("="), "AZ %s: a click on a 2nd island of the zone (not folded yet) gives nothing (%s)" % (kind, s2[:70]))
        # the page: per-spot pictures (2 types), none on a one-type island
        _zfix(L, p, z, [(0, keys[0], 2)], ores=keys[1])
        _items(L, [z["hand"]] if z["hand"] else [])
        T427._give(L, [(z["hand"], 1)] if z["hand"] else [])
        Ck.HAND_TEST = z["hand"]
        Core.NOW_TEST = T0 + 50 * 3600000
        pg = T427._page(L, ou, W_, kd)
        T49._build(pg)
        ta = [str(x) for x in pg.ckTexA] if pg.ckTexA is not None else []
        K.check(len(ta) > 1 and ta[0] != ta[1] and ta[0] == ta[2] and str(pg.ckChip).startswith("Zone 1 %s - Medium" % z["Zw"]) and str(pg.ckSto[0]) == "%s: %s, %s" % (z["Tws"], names[0], names[1]),
                "AZ %s page: spots alternate %s / %s pictures (%s / %s), chip %s, %s" % (kind, names[0], names[1], ta[:1], ta[1:2], pg.ckChip, pg.ckSto[0]))
        _zfix(L, p, z, [(0, keys[0], 2)])
        pg = T427._page(L, ou, W_, kd)
        T49._build(pg)
        K.check(pg.ckTexA is None and not str(pg.ckChip).startswith("Zone "), "AZ %s: a one-type island looks as in 0.4.30 (no per-spot pictures, chip %s)" % (kind, pg.ckChip))
        Ck.HAND_TEST = None
    # Combat: not zoned - an ores line owns nothing
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.type", "skeleton"); p.setProperty("combat.i0.size", "1"); p.setProperty("combat.i0.ores", "zone2")
        c2 = bool(Isl.owns(CK, p, int(Isl.LAD0[CK]) + 1))
        for k_ in ("combat.i0.type", "combat.i0.size", "combat.i0.ores"):
            p.remove(k_)
    finally:
        St.LOCK.unlock()
    K.check(not bool(Isl.zoned(CK)) and not c2 and bool(Isl.zoned(MI)), "AZ Combat is not zoned (an ores line owns nothing); Mining is")
    K.save()


# ---------------------------------------------------------------------------------------------------------- AP31: the page
def run_page(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "ap")
    St, Isl, Ck, Cfg, Core = L["ShStore"], L["ShIsl"], L["ShClk"], L["ShCfg"], L["ShCore"]
    table = []
    for zi, z in enumerate(ZK):
        kd, kind = z["kd"], z["kind"]
        keys, names = _keys(L, kd)
        L0 = int(Isl.LAD0[kd])
        LN = len(keys)
        allids = []
        for li in range(LN):
            c, m = _cost(L, kd, li)
            allids += list(m)
            zl = int(Isl.zoneOf(L0 + li))
            table.append((kind, names[li], zl, "zone island" if li % 3 == 0 else "upgrade", c, " + ".join("%d %s" % (q, i) for i, q in sorted(m.items()))))
        _items(L, allids + ([z["hand"]] if z["hand"] else []))
        Ck.HAND_TEST = z["hand"]
        Core.NOW_TEST = T0
        L["coins"]["bal"] = 10 ** 12
        lv[z["skill"]] = 100
        hand = [(z["hand"], 1)] if z["hand"] else []
        # Zone 1 = the base type only: the map + the 7th row
        _zfix(L, p, z, [(0, keys[0], 1)])
        c1, m1 = _cost(L, kd, 1)
        cs = T427._give(L, [(i, q) for i, q in m1.items()] + hand)
        cnt = lambda i: int(L["count"](cs, i))
        pg = T427._page(L, ou, W_, kd)
        bd = T49._build(pg)
        zn = " + ".join(names[:3])
        K.check(str(pg.ckMN[0]) == (zn if len(zn) <= 24 else names[0] + " + 2 more " + z["tws"]) and str(pg.ckMS[0]).startswith("Shown now - 1 / 3 %s; add %s inside" % (z["tws"], names[1])) and int(pg.ckMB[0]) == 1,
                "AP %s Zone 1 card: %s / %s / %d" % (kind, pg.ckMN[0], pg.ckMS[0], pg.ckMB[0]))
        K.check(all(str(pg.ckMN[c]) == "" and int(pg.ckMB[c]) == 0 for c in range(15) if c % 3), "AP %s ... one card a zone (no 2nd / 3rd type cards)" % kind)
        K.check(str(pg.ckMS[3]).startswith("First add %s in the Zone 1 %s" % (names[1], z["zw"])) and int(pg.ckMB[3]) == 0, "AP %s Zone 2 card: %s" % (kind, pg.ckMS[3]))
        if LN <= 9:
            K.check(str(pg.ckMN[9]) == "" and str(pg.ckZS[3]).startswith("No "), "AP %s Zones 4-5: no card (%s)" % (kind, pg.ckZS[3]))
        K.check(str(pg.ckUpL[6]) == "1 / 3 %s" % z["tws"] and str(pg.ckUpE[6]) == "Add %s: more %s" % (names[1], z["spw"]) and bool(pg.ckUpOk[6]) and int(pg.ckUpSeen[6]) == 1,
                "AP %s the 7th row: %s / %s" % (kind, pg.ckUpL[6], pg.ckUpE[6]))
        lines = [str(pg.ckCL[18 + j]) for j in range(3)]
        K.check(lines[0].endswith("/ {:,} coins".format(c1)) and all(int(pg.ckCG[18 + j]) == 1 for j in range(3) if lines[j]), "AP %s ... have / need lines, green: %s" % (kind, lines))
        K.check(str(pg.ckUpC[6]) == str(L["ShPage"].ckCost(c1, Isl.mats(kd, L0 + 1, Cfg.BUY_ITEMS[kd], 0, 1))), "AP %s ... = the 0.4.30 island price of %s (%s)" % (kind, names[1], pg.ckUpC[6]))
        K.check('"ku6:1"' in bd["datas"].get("#SkyyShKU6X", ""), "AP %s ... the Add button carries the type shown (ku6:1)" % kind)
        r_ = T410.full(pg)
        K.check(not r_["miss"] and not r_["unbound"], "AP %s the island view walks clean %s %s" % (kind, r_["miss"][:2], r_["unbound"][:2]))
        pg.ckMode = 1
        bm = T49._build(pg)
        K.check('"km0"' in bm["datas"].get("#SkyyShKM0X", "") and not any(("#SkyyShKM%dX" % c) in bm["datas"] for c in range(15) if c % 3),
                "AP %s ... the map: the Zone 1 card opens (km0), no 2nd / 3rd type cards" % kind)
        r_ = T410.full(pg)
        K.check(not r_["miss"] and not r_["unbound"], "AP %s the map walks clean %s %s" % (kind, r_["miss"][:2], r_["unbound"][:2]))
        pg.ckMode = 0
        T49._build(pg)
        # the 2nd type AS AN ISLAND: refused
        b0 = L["coins"]["bal"]
        r = str(Core.buyIsland(ou, JString(OWNER), kd, 1, cs))
        K.check(r.startswith("-%s is an upgrade of your Zone 1 %s" % (names[1], z["zw"])) and p.getProperty("%s.i1.type" % kind) is None and L["coins"]["bal"] == b0,
                "AP %s %s bought AS AN ISLAND: refused, nothing paid (%s)" % (kind, names[1], r))
        # tier order: the 3rd type before the 2nd
        c3, m3 = _cost(L, kd, 2)
        r = str(Ck.buyOre(ou, JString(OWNER), kd, 0, 2, cs))
        K.check(r.startswith("-Add %s first" % names[1]) and p.getProperty("%s.i0.ores" % kind) is None, "AP %s tier order: %s before %s (%s)" % (kind, names[1], names[2], r))
        # one item short / one coin short / a stale profile: refused
        it0 = sorted(m1)[0]
        cs2 = T427._give(L, [(i, q - (1 if i == it0 else 0)) for i, q in m1.items()] + hand)
        r = T427._ev(pg, "ku6:1")
        K.check(p.getProperty("%s.i0.ores" % kind) is None and L["coins"]["bal"] == b0 and int(L["count"](cs2, it0)) == m1[it0] - 1, "AP %s one %s short: refused, nothing paid (%s)" % (kind, it0, r[:80]))
        cs = T427._give(L, [(i, q) for i, q in m1.items()] + hand)
        L["coins"]["bal"] = c1 - 1
        r = T427._ev(pg, "ku6:1")
        K.check(p.getProperty("%s.i0.ores" % kind) is None and L["coins"]["bal"] == c1 - 1 and all(cnt(i) == q for i, q in m1.items()), "AP %s one coin short: refused (%s)" % (kind, r[:80]))
        L["coins"]["bal"] = 10 ** 12
        k0 = pg.key
        pg.key = "00000000-0000-0000-0000-000000000000-p9"
        r = str(pg.act("ku6:1", None, None))
        K.check(r.startswith("=The page is up to date") and p.getProperty("%s.i0.ores" % kind) is None, "AP %s a stale profile: refused (%s)" % (kind, r[:70]))
        pg.key = k0
        # bought
        T49._build(pg)
        b0 = L["coins"]["bal"]
        r = T427._ev(pg, "ku6:1")
        K.check(str(p.getProperty("%s.i0.ores" % kind)) == keys[1] and b0 - L["coins"]["bal"] == c1 and all(cnt(i) == 0 for i in m1),
                "AP %s Add %s: %s.i0.ores=%s, exactly %d coins + %s paid (%s)" % (kind, names[1], kind, keys[1], c1, m1, r[:80]))
        disk = open(os.path.join(str(St.DIR), OWNER + ".properties"), encoding="latin-1").read()
        K.check(("%s.i0.ores=%s" % (kind, keys[1])) in disk, "AP %s ... saved at once" % kind)
        b1 = L["coins"]["bal"]
        cs = T427._give(L, [(i, q) for i, q in m1.items()] + hand)
        r = T427._ev(pg, "ku6:1")
        K.check(str(p.getProperty("%s.i0.ores" % kind)) == keys[1] and L["coins"]["bal"] == b1 and all(cnt(i) == q for i, q in m1.items()), "AP %s a double click buys once (%s)" % (kind, r[:70]))
        T49._build(pg)
        K.check(str(pg.ckUpL[6]) == "2 / 3 %s" % z["tws"] and int(pg.ckUpSeen[6]) == 2 and str(pg.ckMS[0]).startswith("Shown now - 2 / 3 %s; add %s inside" % (z["tws"], names[2])),
                "AP %s ... the row offers %s next; the card 2 / 3 (%s)" % (kind, names[2], pg.ckMS[0]))
        # the 3rd type, then the Zone 2 island from its card
        cs = T427._give(L, [(i, q) for i, q in m3.items()] + hand)
        r = T427._ev(pg, "ku6:2")
        T49._build(pg)
        K.check(str(p.getProperty("%s.i0.ores" % kind)) == "%s,%s" % (keys[1], keys[2]) and str(pg.ckUpL[6]) == "3 / 3 %s" % z["tws"] and not bool(pg.ckUpOk[6])
                and str(pg.ckCL[18]).startswith("Every %s of Zone 1" % z["tw"]), "AP %s Add %s too: 3 / 3, no button (%s)" % (kind, names[2], pg.ckCL[18]))
        K.check(str(pg.ckMS[3]).startswith("Buy: ") and int(pg.ckMB[3]) == 2, "AP %s ... the Zone 2 card: Buy (%s)" % (kind, pg.ckMS[3]))
        c4, m4 = _cost(L, kd, 3)
        cs = T427._give(L, [(i, q) for i, q in m4.items()] + hand)
        b2 = L["coins"]["bal"]
        r = T427._ev(pg, "kb3")
        s2 = int(Isl.slotOf(kd, p, L0 + 3))
        T49._build(pg)
        K.check(s2 >= 0 and b2 - L["coins"]["bal"] == c4 and int(pg.ckSlot) == s2 and int(pg.ckUpSeen[6]) == 4, "AP %s the Zone 2 island bought from its card: %d coins, opened (slot %d) (%s)" % (kind, c4, s2, r[:70]))
        r = T427._ev(pg, "ku6:1")
        K.check(r.lower().find("already") >= 0 or r.startswith("The page is up to date"), "AP %s Zone 1's type on the Zone 2 page: nothing bought (%s)" % (kind, r[:80]))
        # Open every owned zone
        nz = (LN + 2) // 3
        rows = [(5 + (zz * 2) % 9, keys[3 * zz], 1 + zz % 3) for zz in range(nz)]
        _zfix(L, p, z, rows)
        _set(L, p, lambda: p.setProperty("%s.i%d.ores" % (kind, rows[0][0]), keys[1]))
        pg = T427._page(L, ou, W_, kd)
        T49._build(pg)
        for zz in range(nz):
            c = 3 * zz
            pg.ckMode = 1
            T49._build(pg)
            K.check(int(pg.ckMB[c]) == 1 and str(pg.ckMS[c]).split(" - ")[0] in ("Yours", "Shown now"), "AP %s the Zone %d card: %s (Open)" % (kind, zz + 1, pg.ckMS[c]))
            r = T427._ev(pg, "km%d" % c)
            T49._build(pg)
            K.check(int(pg.ckSlot) == rows[zz][0] and int(pg.ckMode) == 0, "AP %s ... Open enters it (slot %d)" % (kind, rows[zz][0]))
        # every row line fits, on every zone
        long_ = []
        for s, _t, _sz in rows:
            pg = T427._page(L, ou, W_, kd)
            pg.ckSlot = s
            T49._build(pg)
            long_ += [str(x) for x in list(pg.ckUpE) + list(pg.ckUpL) if x is not None and len(str(x)) > 38]
            long_ += [str(x) for x in pg.ckCL if x is not None and len(str(x)) > 40]
            long_ += [str(x) for x in list(pg.ckSto)[:2] + [pg.ckChip] if x is not None and len(str(x)) > 40]
        K.check(not long_, "AP %s every row line fits on every zone's page: %s" % (kind, long_[:4]))
        # a locked zone; an owned island in a locked zone still opens
        lv[z["skill"]] = 1
        _zfix(L, p, z, [(0, keys[0], 1)])
        pg = T427._page(L, ou, W_, kd)
        T49._build(pg)
        need = int(Isl.zoneNeed(kd, L0 + 3))
        if need > 1:
            K.check(bool(pg.ckMLock[3]) and str(pg.ckMS[3]).startswith("Locked: "), "AP %s a locked zone: %s" % (kind, pg.ckMS[3]))
            _zfix(L, p, z, [(0, keys[0], 1), (4, keys[3], 1)])
            T49._build(pg)
            K.check(not bool(pg.ckMLock[3]) and int(pg.ckMB[3]) == 1, "AP %s an owned island in a locked zone: Open (%s)" % (kind, pg.ckMS[3]))
        lv[z["skill"]] = 100
        Ck.HAND_TEST = None
    print("AP cost table: kind | type | zone | bought as | coins | items")
    for r in table:
        print("AP  %s | %s | Zone %d | %s | %s | %s" % (r[0], r[1], r[2], r[3], "{:,}".format(r[4]), r[5]))
    K.notes.append("AP cost table: " + json.dumps(table))
    K.save()


# ---------------------------------------------------------------------------------------------------------- AG31: the migration
def _units(L, props, kd, kind):
    """every item of a kind's islands in base units (an Enchanted = 100 of its base, a bar = its ore) + seed stores + Eternal seeds as items + the
    rare-find count; islands; totems; owned types"""
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
        t = int(Isl.ofKey(kd, JString(props[k_])))
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
        sd = int(props.get(b + "seed", "0") or 0)
        if sd and str(Isl.SEED[t]):
            put(str(Isl.SEED[t]), sd)
        et = int(props.get(b + "eternal", "0") or 0)
        if et and str(Isl.ESEED[t]):
            put(str(Isl.ESEED[t]), et)
        e = int(props.get(b + "ench", "0") or 0)
        if e:
            u["#rare"] = u.get("#rare", 0) + e
    return u, isl, tot, own


def _zones_of(L, props, kd, kind):
    from jpype import JString
    zs = {}
    for k_, v in props.items():
        if re.match(r"^%s\.i\d+\.type$" % kind, k_):
            zz = int(L["ShIsl"].zoneOf(L["ShIsl"].ofKey(kd, JString(v))))
            zs[zz] = zs.get(zz, 0) + 1
    return sum(n - 1 for n in zs.values())


HDR = ("v=1\npkey=%s\nmap.done=1\nclk.done=1\nclk2.done=1\nforms=1\nfarming.auto=1\nfarming.storage=3\nfarming.compactor=1\nforaging.auto=1\nforaging.storage=2\n"
       "ranching.auto=1\nranching.storage=1\norchard.auto=1\norchard.storage=1\nmining.auto=1\nmining.storage=2\n")
FARM_A = ("farming.i0.type=wheat\nfarming.i0.size=3\nfarming.i0.amt=5\nfarming.i0.deco=5\nfarming.i0.irr=5\nfarming.i0.nsize=5\nfarming.i0.eternal=138\nfarming.i0.seed=0\n"
          "farming.i0.last=%(T0)d\nfarming.i0.stored=5\nfarming.i0.legacy=Skyy_Ench_Wheat\\:9\nfarming.i0.centre=1\nfarming.i0.pl=0,0,0,38,27\nfarming.i0.sacc=0.1\n"
          "farming.i0.xpn=905\nfarming.i0.xpw=76925.0\n"
          "farming.i0.totems=fertilizer\\:3\\:\\:\\:0\\:9978e5ced5ee\\:\\:3;3,harvest_spirit\\:4\\:faster\\:storage\\:0\\:d07060ffe39a\n"
          "farming.i1.type=lettuce\nfarming.i1.size=3\nfarming.i1.amt=0\nfarming.i1.deco=0\nfarming.i1.irr=1\nfarming.i1.eternal=142\nfarming.i1.seed=7\n"
          "farming.i1.last=%(T0)d\nfarming.i1.stored=85\nfarming.i1.legacy=Skyy_Ench_Lettuce\\:2\nfarming.i1.centre=1\nfarming.i1.xpn=285\nfarming.i1.xpw=18810.0\n"
          "farming.i1.totems=harvest_spirit\\:3\\:\\:\\:0\\:5cc6e7cb5987,rain\\:3\\:\\:\\:0\\:5ea66225351e\\:\\:-2;1\n"
          "farming.i2.type=carrot\nfarming.i2.size=3\nfarming.i2.amt=3\nfarming.i2.deco=2\nfarming.i2.irr=3\nfarming.i2.eternal=15\nfarming.i2.seed=0\n"
          "farming.i2.last=%(T0)d\nfarming.i2.stored=33\nfarming.i2.legacy=Skyy_Ench_Carrot\\:3\nfarming.i2.drops=Plant_Crop_Carrot_Item\\:4\nfarming.i2.xpn=333\nfarming.i2.xpw=21978.0\n"
          "farming.i2.totems=harvest_spirit\\:3\\:\\:\\:0\\:8d85725b18ce\n"
          "farming.i3.type=corn\nfarming.i3.size=2\nfarming.i3.amt=5\nfarming.i3.last=%(T0)d\nfarming.i3.stored=42\nfarming.i3.totems=harvest_spirit\\:3\\:\\:\\:0\\:0cb9c2e0c8df\n")
FORA_A = ("foraging.i0.type=oak\nforaging.i0.size=3\nforaging.i0.amt=1\nforaging.i0.nsize=3\nforaging.i0.last=%(T0)d\nforaging.i0.stored=708\nforaging.i0.drops=Plant_Sapling_Oak\\:47\n"
          "foraging.i0.seed=0\nforaging.i0.seeded=1\nforaging.i0.tp=4\nforaging.i0.totems=lumber_spirit\\:1\\:\\:\\:1793767518886\\:\n"
          "foraging.i1.type=beech\nforaging.i1.size=1\nforaging.i1.amt=5\nforaging.i1.deco=5\nforaging.i1.irr=1\nforaging.i1.last=%(T0)d\nforaging.i1.stored=0\nforaging.i1.seed=4\n"
          "foraging.i2.type=maple\nforaging.i2.size=1\nforaging.i2.amt=5\nforaging.i2.deco=5\nforaging.i2.irr=2\nforaging.i2.last=%(T0)d\nforaging.i2.stored=9\n"
          "foraging.i3.type=dry\nforaging.i3.size=2\nforaging.i3.amt=1\nforaging.i3.deco=5\nforaging.i3.irr=2\nforaging.i3.last=%(T0)d\nforaging.i3.stored=0\n")
RAOR_A = ("ranching.i0.type=chicken\nranching.i0.size=1\nranching.i0.last=%(T0)d\nranching.i0.stored=303\nranching.i0.totems=harvest_spirit\\:1\n"
          "ranching.i1.type=cow\nranching.i1.size=2\nranching.i1.amt=2\nranching.i1.last=%(T0)d\nranching.i1.stored=17\nranching.i1.drops=Food_Beef_Raw\\:6\nranching.i1.totems=harvest_spirit\\:2\\:\\:\\:0\\:ra01\n"
          "orchard.i0.type=apple\norchard.i0.size=1\norchard.i0.last=%(T0)d\norchard.i0.stored=0\norchard.i0.seeded=1\norchard.i0.tp=0\norchard.i0.totems=harvest_spirit\\:1\n"
          "orchard.i1.type=berries\norchard.i1.size=1\norchard.i1.last=%(T0)d\norchard.i1.stored=29\norchard.i1.sacc=0.0\norchard.i1.seed=0\n")
MINE_A = ("mining.i0.type=copper\nmining.i0.size=2\nmining.i0.last=%(T0)d\nmining.i0.stored=73\nmining.i0.totems=quarry_spirit\\:2\\:wider\\:wider\\:0\\:57222b9d720b\n"
          "mining.i1.type=iron\nmining.i1.size=2\nmining.i1.last=%(T0)d\nmining.i1.stored=4925\nmining.i1.totems=quarry_spirit\\:2\\:wider\\:wider\\:0\\:85105ea1fda7\n")
FOLDED = {"farming": 2, "foraging": 2, "ranching": 1, "orchard": 1}


def run_mig(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "ag")
    St, Isl, Ck, Core = L["ShStore"], L["ShIsl"], L["ShClk"], L["ShCore"]
    sd = L["sd"]
    Core.NOW_TEST = T0
    _f = T430._file
    _log = T430._log
    hist = lambda k, v: os.path.join(sd, "history", "clicker", k + ".pre-%s.properties" % v)
    # A: the four kinds only (byte-checked History copy)
    kA = "00000000-0000-0000-0000-0000000a3101-p1"
    fA = _f(sd, kA, (HDR % kA) + (FARM_A + FORA_A + RAOR_A) % {"T0": T0})
    raw0 = open(fA, "rb").read()
    bA = T427._props(fA)
    m0, w0, c0 = int(St.AZMIG.get()), int(St.AZWAIT.get()), int(St.AZCHK.get())
    St.CACHE.remove(kA)
    q = St.get(JString(kA))
    aA = T427._props(fA)
    K.check(str(q.getProperty("azone.done")) == "1" and aA.get("azone.done") == "1" and int(St.AZMIG.get()) == m0 + 1 and "mzone.done" not in aA, "AG the marker, saved, counted (no Mining marker: nothing to fold there)")
    for z in ZK:
        kd, kind = z["kd"], z["kind"]
        ub, ua = _units(L, bA, kd, kind), _units(L, aA, kd, kind)
        K.check(ua[0] == ub[0] and ua[2] == ub[2] and ua[3] == ub[3] and ua[1] == ub[1] - FOLDED[kind],
                "AG %s: items (base units, seeds, Eternal seeds) / totems / owned types the same, islands %d -> %d: %s" % (kind, ub[1], ua[1], sorted(ua[0].items())[:6]))
    K.check(not any(k_.startswith(("farming.i1.", "farming.i2.")) for k_ in aA) and aA.get("farming.i0.ores") == "lettuce,carrot" and aA.get("farming.i3.type") == "corn" and "farming.i3.ores" not in aA,
            "AG Farming Zone 1: Lettuce + Carrot folded into the Wheat farm (ores lettuce,carrot); Corn alone stays the Zone 2 farm")
    K.eq((aA.get("farming.i0.size"), aA.get("farming.i0.amt"), aA.get("farming.i0.deco"), aA.get("farming.i0.irr"), aA.get("farming.i0.nsize"), aA.get("farming.i0.eternal")),
         ("3", "5", "5", "5", "5", "138"), "AG ... Large 5/5/5, Plot size 5 (the higher effective levels), its own 138 Eternal cells")
    tl = aA.get("farming.i0.totems", "").split(",")
    K.check(len(tl) == 5 and tl[0].startswith("fertilizer:3") and tl[2].endswith("5cc6e7cb5987") and tl[4].endswith("8d85725b18ce"), "AG ... every totem, the farm's first: %s" % tl)
    d0 = T425._drops(q, 0, "farming")
    K.check(d0.get("Plant_Crop_Lettuce_Item") == 85 + 200 and d0.get("Plant_Seeds_Lettuce_Eternal") == 142 and d0.get("Plant_Seeds_Lettuce") == 7
            and d0.get("Plant_Crop_Carrot_Item") == 33 + 300 + 4 and d0.get("Plant_Seeds_Carrot_Eternal") == 15,
            "AG ... Lettuce stock 85 + 2 Enchanted -> 285 Lettuce, its 142 Eternal + 7 plain seeds back as items; Carrot 33 + 300 + 4 + 15 Eternal (%s)" % d0)
    ow = int(aA.get("owed.xp", "0"))
    K.check(ow > 0 and "Farming XP owed" in _log(sd), "AG ... the folded stock's Collect XP owed at once (owed.xp %d), the journal says so" % ow)
    K.check(aA.get("foraging.i0.ores") == "beech,maple" and aA.get("foraging.i3.type") == "dry" and T425._drops(q, 0, "foraging").get("Plant_Sapling_Beech", 0) == 4
            and aA.get("foraging.i0.amt") == "1" and aA.get("foraging.i0.irr") == "0" and aA.get("foraging.i0.size") == "3",
            "AG Foraging: Beech + Maple folded into Oak (Beech's 4 saplings back as items; Large Oak keeps Tree count 1 / Weather 0 = the higher effective levels 11 / 10), Dry stays")
    K.check(aA.get("ranching.i0.ores") == "cow" and aA.get("ranching.i0.size") == "2" and T425._drops(q, 0, "ranching").get("Food_Beef_Raw") == 17 + 6
            and aA.get("orchard.i0.ores") == "berries" and T425._drops(q, 0, "orchard").get("Plant_Fruit_Berries_Red") == 29, "AG Ranching Cow -> the Chicken ranch (Medium, 23 Raw Beef); Orchard Berries -> the Apple orchard (29 Berries)")
    K.check(os.path.isfile(hist(kA, "0.4.31")) and open(hist(kA, "0.4.31"), "rb").read() == raw0, "AG the History copy = the old file (byte-checked)")
    lg = _log(sd)
    K.check("zone island migration" in lg and kA in lg and "Undo" in lg and "Lettuce (slot 1) -> the Wheat farm (slot 0)" in lg and "Cow (slot 1) -> the Chicken ranch (slot 0)" in lg,
            "AG the collect.log journal line names every fold + the Undo")
    raw1 = open(fA, "rb").read()
    St.CACHE.remove(kA)
    St.get(JString(kA))
    K.check(open(fA, "rb").read() == raw1 and int(St.AZMIG.get()) == m0 + 1, "AG a second load changes nothing")
    # a 0.4.30 rollback re-buys Lettuce as an island: the next 0.4.31 load folds it again (marker set)
    with open(fA, "ab") as fh:
        fh.write(("farming.i1.type=lettuce\nfarming.i1.size=1\nfarming.i1.last=%d\nfarming.i1.stored=50\nfarming.i1.totems=harvest_spirit\\:1\\:\\:\\:0\\:rb0199\n" % T0).encode("utf8"))
    bR = T427._props(fA)
    St.CACHE.remove(kA)
    qR = St.get(JString(kA))
    aR = T427._props(fA)
    uR, uR2 = _units(L, bR, FK, "farming"), _units(L, aR, FK, "farming")
    K.check(int(St.AZMIG.get()) == m0 + 2 and not any(k_.startswith("farming.i1.") for k_ in aR) and aR.get("farming.i0.ores") == "lettuce,carrot" and uR2[0] == uR[0] and uR2[2] == uR[2],
            "AG2 a re-bought Lettuce island folds again (listed once, items / totems kept)")
    K.check("bought again under 0.4.30" in _log(sd) and len([f_ for f_ in os.listdir(os.path.join(sd, "history", "clicker")) if f_.startswith(kA + ".pre-0.4.31.")]) == 2,
            "AG2 ... the journal says it was bought twice; a new timestamped History copy")
    # M: Mining + the four kinds in one file - migrate5 then migrate6
    kM = "00000000-0000-0000-0000-0000000a3102-p1"
    fM = _f(sd, kM, (HDR % kM) + (FARM_A + MINE_A) % {"T0": T0})
    rawM = open(fM, "rb").read()
    St.CACHE.remove(kM)
    St.get(JString(kM))
    aM = T427._props(fM)
    h31 = T427._props(hist(kM, "0.4.31")) if os.path.isfile(hist(kM, "0.4.31")) else {}
    K.check(aM.get("mzone.done") == "1" and aM.get("azone.done") == "1" and aM.get("mining.i0.ores") == "iron" and aM.get("farming.i0.ores") == "lettuce,carrot"
            and open(hist(kM, "0.4.30"), "rb").read() == rawM and h31.get("mzone.done") == "1" and h31.get("farming.i1.type") == "lettuce",
            "AG Mining + Farming in one file: migrate5 folds Iron (its copy = the old file), then migrate6 (its copy = the file after the Mining fold)")
    # B: Lettuce alone in Zone 1 = the zone farm; Wheat = its 7th row; nothing written
    kB = "00000000-0000-0000-0000-0000000a3103-p1"
    fB = _f(sd, kB, (HDR % kB) + "farming.i0.type=lettuce\nfarming.i0.size=1\nfarming.i0.last=%d\nfarming.i0.stored=9\n" % T0)
    rB = open(fB, "rb").read()
    c0 = int(St.AZCHK.get())
    St.CACHE.remove(kB)
    qB = St.get(JString(kB))
    St.LOCK.lock()
    try:
        bs, nx = int(Ck.baseSlotK(FK, qB, 1)), int(Isl.nextTier(FK, qB))
    finally:
        St.LOCK.unlock()
    K.check(open(fB, "rb").read() == rB and qB.getProperty("azone.done") is None and int(St.AZCHK.get()) == c0 + 1 and bs == 0 and nx == 0 and not os.path.isfile(hist(kB, "0.4.31")),
            "AG a Lettuce island alone: it is the Zone 1 farm, Wheat is next (its 7th row); nothing written, no marker")
    # refused cases: nothing changes
    def refused(kx, extra, what, setup=None, undo=None):
        fx = _f(sd, kx, (HDR % kx) + "orchard.i0.type=apple\norchard.i0.size=1\norchard.i0.last=%d\norchard.i0.stored=5\norchard.i1.type=berries\norchard.i1.size=1\norchard.i1.last=%d\norchard.i1.stored=6\n%s" % (T0, T0, extra))
        r0 = open(fx, "rb").read()
        wv = int(St.AZWAIT.get())
        if setup:
            setup()
        St.CACHE.remove(kx)
        qx = St.get(JString(kx))
        if undo:
            undo()
        K.check(open(fx, "rb").read() == r0 and qx.getProperty("azone.done") is None and qx.getProperty("orchard.i1.type") == "berries" and qx.getProperty("orchard.i0.ores") is None
                and int(St.AZWAIT.get()) == wv + 1 and str(qx.getProperty("orchard.i1.stored")) == "6", "AG %s: nothing changes (file, memory), counted as waiting" % what)
    refused("00000000-0000-0000-0000-0000000a3104-p1", "orchard.i1.weird=1\n", "an unknown island key")
    refused("00000000-0000-0000-0000-0000000a3105-p1", "", "a failing totals check", lambda: setattr(St, "AZ_FAIL_TEST", True), lambda: setattr(St, "AZ_FAIL_TEST", False))
    refused("00000000-0000-0000-0000-0000000a3106-p1", "", "a refused save", lambda: setattr(St, "FAIL_TEST", True), lambda: setattr(St, "FAIL_TEST", False))
    # fixer 2: an exception mid-fold (after the folds, before the checks) restores the copy - memory and file unchanged, counted as waiting; next load folds
    kt = "00000000-0000-0000-0000-0000000a3108-p1"
    refused(kt, "", "an error mid-fold (migrate6)", lambda: setattr(St, "AZ_THROW_TEST", True), lambda: setattr(St, "AZ_THROW_TEST", False))
    St.CACHE.remove(kt)
    qt = St.get(JString(kt))
    K.check(qt.getProperty("azone.done") == "1" and qt.getProperty("orchard.i0.ores") == "berries" and qt.getProperty("orchard.i1.type") is None,
            "AGX ... after the error the next load folds it (Berries listed on the Apple island)")
    km = "00000000-0000-0000-0000-0000000a3109-p1"
    fm = _f(sd, km, (HDR % km) + MINE_A % {"T0": T0})
    rm = open(fm, "rb").read()
    mw = int(St.MZWAIT.get())
    St.MZ_THROW_TEST = True
    try:
        St.CACHE.remove(km)
        qm = St.get(JString(km))
    finally:
        St.MZ_THROW_TEST = False
    K.check(open(fm, "rb").read() == rm and qm.getProperty("mzone.done") is None and qm.getProperty("mining.i1.type") == "iron" and qm.getProperty("mining.i0.ores") is None
            and str(qm.getProperty("mining.i1.stored")) == "4925" and int(St.MZWAIT.get()) == mw + 1 and not os.path.isfile(hist(km, "0.4.30")),
            "AGX an error mid-fold in migrate5 (Mining): nothing changes (file, memory), counted as waiting")
    St.CACHE.remove(km)
    qm = St.get(JString(km))
    K.check(qm.getProperty("mzone.done") == "1" and qm.getProperty("mining.i0.ores") == "iron" and qm.getProperty("mining.i1.type") is None,
            "AGX ... the next load folds Iron into the copper quarry")
    St.CACHE.remove("00000000-0000-0000-0000-0000000a3106-p1")
    q6 = St.get(JString("00000000-0000-0000-0000-0000000a3106-p1"))
    K.check(q6.getProperty("azone.done") == "1" and q6.getProperty("orchard.i0.ores") == "berries", "AG ... the next load (the disk writes again) migrates it")
    kh = "00000000-0000-0000-0000-0000000a3107-p1"
    blocker = hist(kh, "0.4.31")
    os.makedirs(blocker, exist_ok=True)
    refused(kh, "", "a refused History copy")
    shutil.rmtree(blocker)
    # the page on the folded file: the Wheat farm with Lettuce + Carrot plots, 3 / 3 crops
    def cp(k_src):
        q_ = St.get(JString(k_src))
        def f():
            for k_ in list(p.stringPropertyNames()):
                if str(k_).startswith("farming."):
                    p.remove(k_)
            for k_ in list(q_.stringPropertyNames()):
                if str(k_).startswith("farming."):
                    p.setProperty(k_, q_.getProperty(k_))
            p.setProperty("farming.placed", L["W_"] + "|1|2|3")
        _set(L, p, f)
    cp(kA)
    Core.NOW_TEST = T0
    pg = T427._page(L, ou, W_, FK)
    T49._build(pg)
    K.check(int(pg.ckSlot) == 0 and str(pg.ckChip).startswith("Zone 1 Farm - Large") and str(pg.ckMS[0]).startswith("Shown now - 3 / 3 crops") and str(pg.ckTexA[1]).endswith("ClkFCrop1.png")
            and str(pg.ckMS[3]).startswith("Yours - 1 / 3 crops; add Cauliflower inside"), "AG the folded farm on the page: %s / %s / %s" % (pg.ckChip, pg.ckMS[0], pg.ckMS[3]))
    cp(kB)
    pg = T427._page(L, ou, W_, FK)
    T49._build(pg)
    K.check(str(pg.ckUpE[6]) == "Add Wheat: more plots" and bool(pg.ckUpOk[6]) and int(pg.ckUpSeen[6]) == 0, "AG ... a Lettuce-only farm offers Wheat on its 7th row (%s)" % pg.ckUpE[6])
    K.save()


# ---------------------------------------------------------------------------------------------------------- AX31: the spirits
def run_spirits(out, jar, scratch, _home):
    from jpype import JString, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "ax")
    St, Isl, Ck, Cfg, Core, M, Tot = L["ShStore"], L["ShIsl"], L["ShClk"], L["ShCfg"], L["ShCore"], L["ShMath"], L["ShTotem"]
    pct0 = int(Cfg.XP_PCT)
    zf = ZK[1]

    def settle(kd, now):
        St.LOCK.lock()
        try:
            return int(M.settle(kd, p, 0, JLong(now)))
        finally:
            St.LOCK.unlock()
    # 1. no upgrade: exactly 0.4.30 (all stock, nothing new written)
    _zfix(L, p, zf, [(0, "wheat", 2)])
    _set(L, p, lambda: [p.remove(x) for x in ("owed.xp", "farming.i0.drops", "farming.i0.orr", "farming.i0.xpr")])
    made0 = settle(FK, T0 + 3600000)
    base0 = int(M.baseOf(FK, p, 0))
    K.check(made0 > 10 and base0 == made0 and p.getProperty("farming.i0.drops") is None and p.getProperty("farming.i0.orr") is None and p.getProperty("owed.xp") is None,
            "AX a farm with no upgrade: its spirits make %d Wheat, all stock, nothing new written" % made0)
    # 2. + Lettuce: the same count, shared; Lettuce in storage, its XP owed at the spirits' XP a crop; the stock's XP tracking = the stock only
    _zfix(L, p, zf, [(0, "wheat", 2)], ores="lettuce")
    _set(L, p, lambda: [p.remove(x) for x in ("owed.xp", "farming.i0.drops", "farming.i0.orr", "farming.i0.xpr", "farming.i0.xpn", "farming.i0.xpw")])
    St.LOCK.lock()
    try:
        xper = float(Tot.xpPer(FK, p, 0, 2, JLong(T0)))
    finally:
        St.LOCK.unlock()
    made1 = settle(FK, T0 + 3600000)
    d = T425._drops(p, 0, "farming")
    le = d.get("Plant_Crop_Lettuce_Item", 0)
    b1 = int(M.baseOf(FK, p, 0))
    K.check(made1 == made0 and b1 + le == made1 and le == made1 // 2, "AX Wheat + Lettuce: the same %d made - %d Wheat stock + %d Lettuce in storage (%s)" % (made1, b1, le, d))
    owh = int(p.getProperty("owed.xp") or 0) * 100 + int(p.getProperty("farming.i0.xpr") or 0)
    K.check(abs(owh - int(le * xper * pct0)) <= 1, "AX ... the Lettuce's XP owed at once: %d hundredths = %d x %.2f x %d%%" % (owh, le, xper, pct0))
    St.LOCK.lock()
    try:
        xa = float(M.xpAvg(FK, p, 0, JLong(T0 + 3600000)))
        xn = int(p.getProperty("farming.i0.xpn") or -1)
    finally:
        St.LOCK.unlock()
    K.check(xn == b1 and abs(xa - xper) < 0.01, "AX ... the stock's XP tracking counts the stock only (xpn %d = %d, %.2f a crop)" % (xn, b1, xa))
    # 3. Ranching: Chicken + Cow
    zr = ZK[2]
    _zfix(L, p, zr, [(0, "chicken", 2)], ores="cow")
    _set(L, p, lambda: [p.remove(x) for x in ("owed.xp.Ranching", "ranching.i0.drops", "ranching.i0.orr", "ranching.i0.xpr")])
    mr = settle(RA, T0 + 3600000)
    dr = T425._drops(p, 0, "ranching")
    K.check(mr > 0 and dr.get("Food_Beef_Raw", 0) == mr // 2 and int(p.getProperty("owed.xp.Ranching") or 0) * 100 + int(p.getProperty("ranching.i0.xpr") or 0) == (mr // 2) * int(Cfg.xpOf(RA)) * pct0,
            "AX Ranching Chicken + Cow: half the %d made is Raw Beef in storage, its XP owed (%s)" % (mr, dr))
    # 4. the spirit row says "crops a minute" on a shared farm; Collect all pays the storage + the owed XP
    _items(L, [])
    T427._give(L, [])
    for ores in (None, "lettuce"):
        _zfix(L, p, zf, [(0, "wheat", 2)], ores=ores)
        Core.NOW_TEST = T0
        pg = T427._page(L, ou, W_, FK)
        T49._build(pg)
        e2 = str(pg.ckUpE[2])
        K.check(e2.endswith(" a minute") and ("crops a minute" in e2) == (ores is not None) and len(e2) <= 38, "AX the spirit row (%s): %s" % (ores, e2))
    _zfix(L, p, zf, [(0, "wheat", 2)], ores="lettuce")
    Core.NOW_TEST = T0 + 3600000
    cs = T427._give(L, [])
    settle(FK, T0 + 3600000)
    ow = int(p.getProperty("owed.xp") or 0)
    r = str(Core.collect(ou, JString(OWNER), FK, -1, cs))
    K.check(r.startswith("+") and p.getProperty("farming.i0.drops") is None and ow > 0 and int(p.getProperty("owed.xp") or 0) == 0,
            "AX Collect all takes the Wheat + the Lettuce and pays the owed XP (%d) (%s)" % (ow, r[:100]))
    K.save()


# ---------------------------------------------------------------------------------------------------------- live31: START TWICE on a scratch COPY of the live data
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
    lasts = [int(v) for f in files for k_, v in pb[f].items() if re.match(r"^\w+\.i\d+\.last$", k_)]
    L["ShCore"].NOW_TEST = min(lasts) if lasts else 0   # no production between the save and this start: before / after compare exactly
    St.DIR = JClass("java.nio.file.Paths").get(JString(sd), jpype.JArray(JString)([]))
    St.CACHE.clear()
    for f in files:
        St.get(JString(f[:-len(".properties")]))
    pa = dict((f, T427._props(os.path.join(sd, f))) for f in files)
    rows = {}
    for f in files:
        k = f[:-len(".properties")]
        rows[f] = {}
        anyf = False
        for kd, kind in ((MI, "mining"), (FO, "foraging"), (FK, "farming"), (RA, "ranching"), (OR, "orchard"), (CK, "combat")):
            ub, ua = _units(L, pb[f], kd, kind), _units(L, pa[f], kd, kind)
            folded = _zones_of(L, pb[f], kd, kind) if kd != CK else 0
            anyf = anyf or (folded > 0 and kd != MI)
            rows[f][kind] = {"islands": [ub[1], ua[1]], "folded": folded, "totems": [ub[2], ua[2]], "owned": sorted(ua[3]),
                             "items": [sum(v for k_, v in ub[0].items() if k_ != "#rare"), sum(v for k_, v in ua[0].items() if k_ != "#rare")]}
            K.check(ua[1] == ub[1] - folded and ua[2] == ub[2] and ua[0] == ub[0] and ua[3] == ub[3],
                    "L31 %s %s: islands %d -> %d (%d folded), totems %d kept, items (base units + seeds + Eternal seeds) the same, owned %s kept" % (f, kind, ub[1], ua[1], folded, ua[2], sorted(ua[3])))
        if anyf:
            K.check(pa[f].get("azone.done") == "1" and os.path.isfile(os.path.join(sd, "history", "clicker", k + ".pre-0.4.31.properties")), "L31 %s: the marker + the History copy" % f)
        other = sorted(k_ for k_ in set(pb[f]) | set(pa[f]) if pb[f].get(k_) != pa[f].get(k_)
                       and not k_.startswith(("mining.", "foraging.", "farming.", "ranching.", "orchard.")) and k_ not in ("mzone.done", "azone.done", "owed.xp", "owed.xp.Mining", "owed.xp.Foraging", "owed.xp.Ranching"))
        K.check(not other, "L31 %s: no other key rewritten %s" % (f, other[:6]))
        K.check(all(pb[f].get(k_) == pa[f].get(k_) for k_ in set(pb[f]) | set(pa[f]) if k_.startswith("combat.")), "L31 %s: Combat untouched" % f)
        q = St.get(JString(k))
        St.LOCK.lock()
        try:
            for kd, kind in ((MI, "mining"), (FO, "foraging"), (FK, "farming"), (RA, "ranching"), (OR, "orchard")):
                for s in range(16):
                    if L["ShMath"].hasIsland(kd, q, s):
                        rows[f]["%s.i%d" % (kind, s)] = {"type": str(q.getProperty("%s.i%d.type" % (kind, s))), "ores": str(q.getProperty("%s.i%d.ores" % (kind, s))),
                                                         "used/limit": [int(L["ShMath"].usedOf(kd, q, s)), int(L["ShMath"].limOf(kd, q, s))],
                                                         "size/amt/deco/irr": [str(q.getProperty("%s.i%d.%s" % (kind, s, x))) for x in ("size", "amt", "deco", "irr")]}
        finally:
            St.LOCK.unlock()
    raw1 = dict((f, open(os.path.join(sd, f), "rb").read()) for f in files)
    St.CACHE.clear()
    for f in files:
        St.get(JString(f[:-len(".properties")]))
    K.check(all(open(os.path.join(sd, f), "rb").read() == raw1[f] for f in files), "L31 the second start: nothing changes (every file byte for byte)")
    K.notes.append("L31 live copy: " + json.dumps(rows))
    print("L31 live copy: %s" % json.dumps(rows, indent=1))
    K.save()


EXPECT = {   # 0.4.30 -> 0.4.31
    'CfgFn': ['~m opExport'], 'CfgRows': ['~m header'], 'ShFill': ['~m markFixed'], 'SkyyShardsPlugin': ['~m setup'], 'ShCore': ['~m buyIsland0'],
    'ShClk': ['+m baseSlotK', '+m zoneOwnedK', '~m buyOre0', '~m chop', '~m gather', '~m harvest', '~m isBase'],
    'ShIsl': ['+f ROWN', '+f SHW', '+f SPW', '+f TW', '+f TWS', '+f TWSC', '+f ZW', '+f ZWC', '+m zoned', '~<clinit>', '~m owns'],
    'ShMath': ['+m oweXpD', '~m oreShare', '~m settle', '~m shareOres'],
    'ShPage': ['+m zonePost', '~m actClick', '~m build0', '~m buildClick', '~m ckSpirit', '~m fillClick', '~m fillFarm', '~m fillOrch', '~m fillRanch'],
    'ShStore': ['+f AZCHK', '+f AZMIG', '+f AZWAIT', '+f AZ_FAIL_TEST', '+f AZ_KINDS', '+f AZ_THROW_TEST', '+f MZ_THROW_TEST', '+m azFolds', '+m azUnits', '+m migrate6', '+m snapAz', '~<clinit>', '~m get',
                '~m migrate', '~m migrate2', '~m migrate3', '~m migrate4', '~m migrate5', '~m mzFold', '~m save'],
}

# 0.4.30's phases run whole; RETIRED 0.4.2x / 0.4.30 CHECKS = the per-type map / caption / 6 rows they pinned are replaced on purpose (each reason is a
# 0.4.31 spec line; AP31 / AZ31 / AG31 check the new behaviour). A failing check whose text matches is counted as a note "retired ..." instead.
T427.RETIRED += [
    (r"^FX a Zone 2 ore / junk on the line: Copper alone .*; Foraging never shares", "SPEC 2: a Foraging zone island shares its spirits' output over its trees too (AX31)"),
    (r"^PG \.\.\. 8 cards, 5 zone panels", "SPEC 1: one card a zone (AP31: no 2nd / 3rd type cards)"),
    (r"^PG \.\.\. the Cow is the next to buy", "SPEC 2: Cow is an upgrade of the Zone 1 ranch, not a map card (AP31 buys it on the Animals row)"),
    (r"^PG \.\.\. the Cow bought on the map and shown: Cow is an upgrade of your Zone 1 ranch", "SPEC 2: a 2nd Zone 1 animal as an island is refused by design (AP31)"),
    (r"^PG \.\.\. paid 64 Raw Beef \+ 2 Capture Crates", "SPEC 2: the same price is paid on the Animals row (AP31 'exactly ... paid')"),
    (r"^MG28 islands / totems before = after \(3, 4, \d+\) -> \(2, 4, \d+\)", "SPEC 3: migrate6 folds the fixture's 2nd Zone 1 orchard island at the same load (AG31 checks the fold's totals)"),
    (r"^MG28 nothing else rewritten \['azone\.done', 'orchard\.", "SPEC 3: ... these keys are that fold's (AG31)"),
    (r"^FZ \.\.\. the farm clusters \(not the woods\)", "SPEC 1: one card a zone - FMap12 is the Zone 5 card, no FMap14 card (AP31)"),
    (r"^FZ the owned T7 Pumpkin island in locked Zone 3: open \(Yours - 1 / 3 crops", "SPEC 1: the zone card says 'Yours - n / m crops' (AP31 'an owned island in a locked zone: Open')"),
    (r"^FZ T8 Aubergine not owned in Zone 3: locked \+ the lock picture", "SPEC 1/2: Aubergine is no card any more - the Zone 3 farm's Crops row (AP31)"),
    (r"^CZ the owned T7 island in locked Zone 3: open \(Yours - 1 / 3 trees", "SPEC 1: the zone card says 'Yours - n / m trees' (AP31)"),
    (r"^CZ a T8 island not owned in Zone 3: locked \+ the lock picture", "SPEC 1/2: no card for the 2nd type of a zone - the Zone 3 grove's Trees row (AP31)"),
    (r"^CZ the shown island: Shown now - 3 / 3 trees", "SPEC 1: the shown zone card has Open too, as Mining's (AP31 'Open every owned zone')"),
    (r"^U Buy island from the buy view: -Lettuce is an upgrade of your Zone 1 farm", "SPEC 2: a 2nd Zone 1 crop is an upgrade, not an island (AP31)"),
    (r"^U T2 is mine now: its picture \+ its gold line", "SPEC 2: ... so no T2 island appears (AP31 buys Lettuce on the Crops row)"),
]


# orch28 clicked a Berries ISLAND in slot 1 of Zone 1 - one island a zone now: the same checks with Berries added to the Apple orchard (spot 1)
def _orch31_src():
    src = open(os.path.join(HERE, "test_skyyshards_0.4.28.py"), encoding="utf8").read()
    a = src.index("def run_orch(out, jar, scratch, _home):")
    b = src.index("# ------", a)
    f = src[a:b].replace("def run_orch(", "def run_orch31(")
    for old, new in (('    _orch(L, p, extra=[(1, "berries", 1)])\n', '    _orch(L, p)\n    St.LOCK.lock()\n    p.setProperty("orchard.i0.ores", "berries")\n    St.save(OWNER, p)\n    St.LOCK.unlock()\n'),
                     ("        pk(slot=1)\n", "        pk(spot=1)\n"),
                     ('    K.eq(T425._drops(p, 1, "orchard"), {"Plant_Fruit_Berries_Red": main2}, "OC the Berries bush',
                      '    K.eq(dict((k_, v_) for k_, v_ in T425._drops(p, 0, "orchard").items() if k_ != APL), {"Plant_Fruit_Berries_Red": main2}, "OC31 the Berries bush (spot 1 of the Apple orchard)'),
                     ('float(Ck.state(JString(OWNER + "|4|1"))[0][0]) == 0.0, "OC the orchard', 'float(Ck.state(JString(OWNER + "|4|0"))[0][1]) == 0.0, "OC31 the orchard'),
                     ('"OC ', '"OC31 ')):
        assert f.count(old) >= 1, old[:60]
        f = f.replace(old, new)
    ns = dict(T428.__dict__)
    exec(compile(f, "orch31", "exec"), ns)
    return ns["run_orch31"]


run_orch31 = _orch31_src()

PHASES = [("static", run_static), ("model31", run_model), ("page31", run_page), ("mig31", run_mig), ("spirit31", run_spirits), ("orch31", run_orch31)] + \
         [x for x in T430.PHASES if x[0] not in ("static", "livemig30", "orch28")] + [("livemig31", run_live)]


if __name__ == "__main__":
    HK.run_compare = T429._compare29
    ph = PHASES
    if "--only" in sys.argv and "--phase" not in sys.argv:
        want = set(HK.arg("--only").split(","))
        ph = [x for x in PHASES if x[0] in want]
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=ph, script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
