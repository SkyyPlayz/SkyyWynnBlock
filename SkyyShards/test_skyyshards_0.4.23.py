"""Harness for SkyyShards 0.4.23 (the Foraging Shard clicker - tools/shards_0_4_23_patch.py, on top of 0.4.22).
Build first:
    python tools/shards_0_4_23_patch.py && python SkyyShards/build_skyyshards_0.4.23.py
    python SkyyShards/test_skyyshards_0.4.23.py [--keep]

  S23  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand; line endings kept; the jar ships
                every clicker picture (registered, our own PNGs) + the Skyglass theme; no periodic page update; one Primary a view
  CK   click    EXECUTED no hatchet, a pickaxe, the click cap (8 counted a second, the rest do nothing), the chops a tree takes (T1 / T2 hatchet, Breaking
                Power), the fall: logs into foraging.i0.drops (saved), the XP (25 % of xp.oak per base log, fractions wait), regrow (memory) + the weather
                totem, Fortune (every source; the gear source only on its only.foraging), storage full (nothing felled), a refused save (the tree stands
                again, nothing added), a co-op member who may not collect, the clicker switched off, nothing else in the file moved (no migration)
  CC   collect  EXECUTED the grid shows the chopped logs merged with the stock, a cell / Collect all pay them first (collection credit, no XP), a full
                inventory keeps the rest in .drops, a refused save takes nothing, Collect all after both = no dupe / no loss
  CU   upgrade  EXECUTED Tree size (not enough coins / items: nothing taken; bought: exact coins + Enchanted Oak; a stale double click buys once; the
                highest level; a co-op member refused), Tree count / Weather / Decorations / Island size through the page (stale level refused, Grow
                only at 5 / 5 / 5), the Spirit row opens the Totems tab
  CZ   zones    EXECUTED the zone of every tier, a Zone 2 island refused under Foraging 20 (buyIsland0: the Map tab too), bought at 20; an owned island
                in a locked zone stays open; the map cards (lock, Open, Buy, the shown island)
  PG23 page     the Foraging footer has Shard clicker (Farming not), kopen -> view 5, every variant walks clean (sizes 1-3, the map), the tree squares
                carry kt<spot>:<slot>, a click pops "+3 Oak Log", the store cells, the element count, the packet size, kback / kstore / Totems
  then 0.4.22's phases (combat22, farm22, page22) and 0.4.21's / older ones, A verify, C compare, AA audit, live START TWICE
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.23"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "forage1", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.22.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.22.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_23_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.22 harness (it loads 0.4.21 and older): its version moves to this one in memory
_T22 = open(os.path.join(HERE, "test_skyyshards_0.4.22.py"), encoding="utf8").read()
assert _T22.count('VERSION = "0.4.22"') == 3, "the 0.4.22 harness changed"   # its module line, its 0.4.21 loader, its own static check (not run here)
_T22 = _T22.replace('VERSION = "0.4.22"', 'VERSION = "0.4.23"')
assert _T22.count('"arena (SkyyShards 0.4.22) "') == 1
_T22 = _T22.replace('"arena (SkyyShards 0.4.22) "', '"arena (SkyyShards 0.4.23) "')   # the rebuild's collect.log line names the running version (@VERSION@)
_argv = list(sys.argv)
T422 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_22", loader=None))
T422.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.22.py")
exec(compile(_T22, T422.__file__, "exec"), T422.__dict__)
sys.argv[:] = _argv
T421 = T422.T421
T420, T419, T411, T410, T49, T416, T415, T413 = T421.T420, T421.T419, T421.T411, T421.T410, T421.T49, T421.T416, T421.T415, T421.T413
T422.JAR = T421.JAR = T420.JAR = T419.JAR = T420.T418.JAR = T419.T417.JAR = JAR
T422.SCRATCH = T421.SCRATCH = T420.SCRATCH = T419.SCRATCH = T420.T418.SCRATCH = T416.SCRATCH = T415.SCRATCH = T419.T417.SCRATCH = SCRATCH
OWNER, MEMBER = T420.OWNER, T420.MEMBER
FO, FK = 1, 2
T0 = 1790000000000
OAK, EOAK = "Wood_Oak_Trunk", "Skyy_Ench_Oak"


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.23 - build script') and 'VERSION = "0.4.23"\n' in g, "S23 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S23 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.23:" in g, "S23 the ready line names the round")
    blk = g[g.index("# ================= 0.4.23 THE SHARD CLICKER"):g.index("# ================= 0.4.9 ShMap")]
    K.check("scheduleAtFixedRate" not in blk and "sendUpdate" not in blk, "S23 no periodic page update (HANDOFF section 2): the spirits work by the clock")
    K.check("public static String collectS(" in g and g.count("public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs, String only)") == 1,
            "S23 collect0 = the chopped drops first + the 0.4.22 Collect (collectS)")
    K.check("ALLC = ALLC + [ckc]" in g, "S23 ShClk is written")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S23 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S23 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S23 the jar is newer than the build script, the build script newer than the patch")
    with zipfile.ZipFile(jar) as z:
        names = z.namelist()
        clk = [n for n in names if n.startswith("Common/UI/Custom/SkyyShards/Map/Clk") and n.endswith("@2x.png")]
        glass = [n for n in names if n.startswith("Common/UI/Custom/SkyyGlass/")]
        K.check(len(clk) == 66 and all(z.read(n)[:8] == b"\x89PNG\r\n\x1a\n" for n in clk), "S23 the 66 clicker pictures are in the jar (%d)" % len(clk))
        K.check(all(("Clk%s" % t) in " ".join(clk) for t in ["Tree%d@" % i for i in range(1, 16)] + ["Isl1@", "Isl2@", "Isl3@", "Sky@", "Lock@", "Map15@"]),
                "S23 ... 15 trees, 3 islands, the sky, the lock, 15 map islands")
        K.check(len(glass) >= 20 and not any(n.endswith(".ui") for n in names), "S23 the Skyglass theme files ship (%d), no .ui file" % len(glass))
        # our own pictures: none is byte-equal to a vanilla file of Assets.zip
        import serverjar as _SJ
        az = zipfile.ZipFile(_SJ.assets_zip())
        van = set()
        for n in az.namelist():
            if n.lower().endswith(".png") and "/UI/" in n:
                van.add(az.getinfo(n).CRC)
        K.check(not any(z.getinfo(n).CRC in van for n in clk), "S23 no clicker picture is a vanilla UI file (CRC)")
    K.save()


def _foraging(L, p, size=1, amt=0, irr=0, deco=0, stored=0, lim_tier=5):
    St = L["ShStore"]
    St.LOCK.lock()
    try:
        for k_ in list(p.stringPropertyNames()):
            if str(k_).startswith("foraging."):
                p.remove(k_)
        p.setProperty("foraging.i0.type", "oak"); p.setProperty("foraging.i0.size", str(size)); p.setProperty("foraging.i0.last", str(T0))
        p.setProperty("foraging.i0.stored", str(stored)); p.setProperty("foraging.i0.amt", str(amt)); p.setProperty("foraging.i0.irr", str(irr))
        p.setProperty("foraging.i0.deco", str(deco)); p.setProperty("foraging.auto", "1"); p.setProperty("foraging.paused", "0")
        p.setProperty("foraging.storage", str(lim_tier)); p.setProperty("foraging.i0.totems", "lumber_spirit:1:::0:fo0001")
        p.setProperty("foraging.placed", L["W_"] + "|1|2|3")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()


def _env(scratch, K, name):
    from jpype import JClass, JString
    L, ou, W_, p, lv = T420._W0(os.path.join(scratch, name), K)
    L["W_"] = W_
    L["ShClk"] = JClass(PKG + "ShClk")
    T411.T48.add_items([(OAK, 100), (EOAK, 64), ("Wood_Beech_Trunk", 100), ("Skyy_Ench_Beech", 64), ("Plant_Sapling_Beech", 64), ("Plant_Sapling_Oak", 64),
                        ("Tool_Hatchet_Copper", 1), ("Tool_Hatchet_Iron", 1), ("Ingredient_Water_Essence", 100), ("Rock_Stone_Cobble", 100)])
    M, Core, Cfg = L["ShMath"], L["ShCore"], L["ShCfg"]
    M.ONLINE.put(OWNER, True)
    Core.NOW_TEST = T0
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER))
    lv["Foraging"] = 30
    got = T420._kit(L, p, K)
    return L, ou, W_, p, lv, got


def _drops(p, slot=0):
    s = p.getProperty("foraging.i%d.drops" % slot)
    if s is None:
        return {}
    out = {}
    for part in str(s).split(","):
        i, q = part.rsplit(":", 1)
        out[i] = out.get(i, 0) + int(q)
    return out


def run_click(out, jar, scratch, _home):
    from jpype import JLong, JString, JObject, JDouble
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "ck")
    M, St, Core, Cfg, Ck, Isl = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"]
    br = L["br"]
    _foraging(L, p, amt=5)
    now = [T0]

    def adv(ms):
        now[0] += ms
        Core.NOW_TEST = now[0]

    def chop(spot=0, hand="Tool_Hatchet_Copper", slot=0):
        r = Ck.chop(ou, JString(OWNER), FO, slot, spot, JString(hand) if hand else None)
        return str(r[0]), str(r[1])

    snap = dict((str(k_), str(p.getProperty(k_))) for k_ in p.stringPropertyNames())
    # no hatchet / a pickaxe: nothing happens
    for h in (None, "Tool_Pickaxe_Iron"):
        s, pp = chop(hand=h)
        K.check(s.startswith("-Hold a hatchet") and pp == "", "CK no hatchet (%s): %s" % (h, s))
    K.eq([int(Ck.axeTier(JString(x))) for x in ("Tool_Hatchet_Copper", "Tool_Hatchet_Iron", "Tool_Hatchet_Crude", "Tool_Hatchet_Lumen_SkyWynn",
                                                "Tool_Hatchet_Pickaxe_Multitool_Dusk_SkyWynn", "Tool_Hatchet_Weird", "Mod_Multitool_Cobalt", "Tool_Pickaxe_Iron")],
         [1, 2, 1, 15, 6, 1, 7, 0], "CK the hatchet tiers (tier_tags; an unknown hatchet = its metal word, else T1; a pickaxe = 0)")
    # the click cap: 20 clicks in one millisecond = 8 counted
    c0, cap0 = int(Ck.CHOPS.get()), int(Ck.CAPPED.get())
    for _ in range(20):
        chop()
    K.eq((int(Ck.CHOPS.get()) - c0, int(Ck.CAPPED.get()) - cap0), (8, 12), "CK the click cap: 8 counted, 12 did nothing")
    K.eq(_drops(p), {}, "CK ... 8 chops of 12 fell nothing yet")
    Cfg.CK_CPS = 1000   # the logic below without the cap (it was just proven)
    # the 4 left fell it (T1 Copper on T1 Oak = 1 a chop)
    adv(1000)
    xp0 = got["xp"]
    res = [chop() for _ in range(4)]
    K.check(res[2][1] == "11 / 12" and res[3][0].startswith("+Felled a T1 Oak tree: +3 Oak Log") and res[3][1] == "+3 Oak Log", "CK 12 chops fell it: %s / %s" % (res[2], res[3]))
    K.eq(_drops(p), {OAK: 3}, "CK ... 3 logs into foraging.i0.drops")
    disk = open(os.path.join(str(St.DIR), OWNER + ".properties"), encoding="utf8").read().replace(chr(92) + ":", ":")
    K.check("foraging.i0.drops=Wood_Oak_Trunk:3" in disk, "CK ... saved at once")
    K.eq(got["xp"] - xp0, 4, "CK ... XP = 25 % of xp.oak (6) x 3 = 4.5 -> 4 paid, the half waits")
    # regrow: the same tree is growing back; the second spot works; the half XP point comes with the next fall
    s, pp = chop()
    K.check(s.startswith("=That tree is growing back - 10 s"), "CK a felled tree grows back (10 s): %s" % s)
    for _ in range(12):
        chop(spot=1)
    adv(1000)
    K.eq(_drops(p), {OAK: 6}, "CK spot 2 fell too: 6 logs")
    K.eq(got["xp"] - xp0, 9, "CK ... 4.5 + 4.5 = 9 XP paid in all")
    adv(9000)
    s, pp = chop()
    K.check(s == "" and pp == "1 / 12", "CK after 10 s the tree stands again: %r %r" % (s, pp))
    # a spot the island does not have (Tree Amount 0, Small: treeN), a stale island slot
    n = int(Isl.treeN(1, 5))
    s, pp = chop(spot=n)
    K.check(s.startswith("=The page is up to date"), "CK spot %d is not on the island: %s" % (n, s))
    s, pp = chop(slot=3)
    K.check(s.startswith("-That island is not yours yet"), "CK an island slot without island: %s" % s)
    # T2 Iron on T1 Oak = 1.25 a chop -> 10 chops; Breaking Power 100 % (an accessory) = 2.5 -> 5 chops; the gear source never counts for BP
    adv(1000)
    k2 = 2
    for i in range(9):
        s, pp = chop(spot=k2, hand="Tool_Hatchet_Iron")
    K.check(pp == "11.25 / 12", "CK a T2 hatchet on T1 wood: 1.25 a chop (9 chops = 11.25): %s" % pp)
    s, pp = chop(spot=k2, hand="Tool_Hatchet_Iron")
    K.check(s.startswith("+Felled"), "CK ... the 10th fells it: %s" % s)
    adv(1000)
    bon = L["JClass"]("java.util.concurrent.ConcurrentHashMap")() if "JClass" in L else None
    from jpype import JClass
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    HM = JClass("java.util.HashMap")
    m = CHM()
    acc = HM(); acc.put("bp.foraging", JDouble(1.0)); m.put("acc", acc)
    gear = HM(); gear.put("bp.foraging", JDouble(5.0)); m.put("gear", gear)
    br.put("skill:bonus:" + str(ou), m)
    K.check(abs(float(Ck.bp(ou)) - 1.0) < 1e-9, "CK Breaking Power = the sources but gear (1.0): %s" % Ck.bp(ou))
    for i in range(4):
        s, pp = chop(spot=3)
    K.check(pp == "8 / 12", "CK ... 2 a chop (4 chops = 8): %s" % pp)
    chop(spot=3)
    s, pp = chop(spot=3)
    K.check(s.startswith("+Felled"), "CK ... the 6th fells it: %s" % s)
    adv(1000)
    # Fortune: dd.foraging of every source; the gear source only when its only.foraging names the log
    m.clear()
    gear = HM(); gear.put("dd.foraging", JDouble(1.0)); gear.put("only.foraging", "Wood_"); m.put("gear", gear)
    tr = HM(); tr.put("dd.foraging", JDouble(0.5)); m.put("trees", tr)
    K.check(abs(float(Ck.fortune(ou, JString(OAK))) - 1.5) < 1e-9, "CK Fortune 1.5 (hatchet 1.0 on wood + tree node 0.5)")
    gear.put("only.foraging", "Rock_,Ore_")
    K.check(abs(float(Ck.fortune(ou, JString(OAK))) - 0.5) < 1e-9, "CK ... a pickaxe's Fortune never counts on wood (0.5)")
    gear.put("only.foraging", "Wood_")
    K.eq([int(Ck.extras(JDouble(1.5), JDouble(0.2))), int(Ck.extras(JDouble(1.5), JDouble(0.7))), int(Ck.extras(JDouble(0.0), JDouble(0.0)))], [2, 1, 0],
         "CK extras: 1.5 = one sure + 50 % a second")
    d0 = _drops(p).get(OAK, 0)
    xp1 = got["xp"]
    for spot in (4, 5):
        for _ in range(12):
            if spot == 5 and _ == 0:
                adv(1000)
            chop(spot=spot)
    adv(1000)
    gotl = _drops(p).get(OAK, 0) - d0
    K.check(12 <= gotl <= 18, "CK two falls at Fortune 1.5: 3 logs + 1-2 extra each = 12-18 (%d)" % gotl)
    K.eq(got["xp"] - xp1, 9, "CK ... Fortune extras pay no XP (9 for the 6 base logs)")
    m.clear()
    # FIXER forage1fix: the WORLD's tier gate (SkyyGear, Skyy 2026-10-13): one tier up = 2.5x the chops, two up = 10x, three+ up refused; above = faster
    K.eq([round(float(Ck.dmg(a_, w_, JDouble(0.0))), 6) for a_, w_ in ((1, 1), (2, 1), (5, 1), (9, 1), (1, 2), (1, 3), (1, 4), (1, 15), (13, 15), (14, 15))],
         [1.0, 1.25, 2.0, 3.0, 0.4, 0.1, 0.0, 0.0, 0.1, 0.4], "FX1 dmg: same tier 1, +25 %/tier above (max x4), 1 up 0.4, 2 up 0.1, 3+ up 0 (refused)")
    K.eq(round(float(Ck.dmg(1, 2, JDouble(1.0))), 6), 0.8, "FX1 ... Breaking Power still multiplies (0.4 x 2)")
    K.eq(round(12 / float(Ck.dmg(1, 2, JDouble(0.0)))), 30, "FX1 ... a Copper hatchet on T2 wood: 30 chops = 2.5x the 12")
    Cfg.CK_UP1 = 50
    K.eq(round(float(Ck.dmg(1, 2, JDouble(0.0))), 6), 0.5, "FX1 ... click.oneTierUp is live")
    Cfg.CK_UP1 = 40
    t4 = int(Isl.LAD0[FO]) + 3   # the 4th wood of the Foraging ladder (T4, 3 tiers above Copper), then the 3rd (T3, 2 above)
    for tt_, ok_ in ((t4, False), (t4 - 1, True)):
        St.LOCK.lock()
        try:
            p.setProperty("foraging.i0.type", str(Isl.KEY[tt_]))
            wt_ = int(Isl.TIER[int(Isl.ty(FO, p, 0))])
        finally:
            St.LOCK.unlock()
        adv(1000)
        c2 = int(Ck.CHOPS.get())
        d0_ = float(Ck.state(JString(OWNER + "|0"))[0][0])
        s, pp = chop(spot=0)
        d1_ = float(Ck.state(JString(OWNER + "|0"))[0][0])
        if ok_:
            K.check(s == "" and pp.endswith(" / 12") and abs(d1_ - d0_ - 0.1) < 1e-9 and int(Ck.CHOPS.get()) == c2 + 1,
                    "FX1 a Copper hatchet on T%d wood (2 up): 0.1 a chop (10x the chops): %r %r %s" % (wt_, s, pp, d1_ - d0_))
        else:
            K.check(wt_ == 4 and s.startswith("-Your T1 hatchet is too low a tier for T4 wood") and int(Ck.CHOPS.get()) == c2,
                    "FX1 a Copper hatchet on T%d wood (3 up): refused, no chop counted: %s" % (wt_, s))
    St.LOCK.lock()
    try:
        p.setProperty("foraging.i0.type", "oak")
    finally:
        St.LOCK.unlock()
    # FIXER forage1fix: the XP fraction waits per player AND profile (a switch never carries it over)
    K.eq([int(Ck.accXp(JString("u|A"), JDouble(0.6))), int(Ck.accXp(JString("u|B"), JDouble(0.6))), int(Ck.accXp(JString("u|A"), JDouble(0.6)))],
         [0, 0, 1], "FX2 XP fractions are kept per profile: A 0.6 + 0.6 = 1, B 0.6 stays")
    # the weather totem: Irrigation 3 = 7 s regrow; at least click.minRegrowSec
    K.eq([int(Ck.regrowMs(i)) for i in (0, 3, 5)], [10000, 7000, 5000], "CK regrow 10 / 7 / 5 s at Weather 0 / 3 / 5")
    Cfg.CK_RMIN = 8
    K.eq(int(Ck.regrowMs(5)), 8000, "CK ... never below click.minRegrowSec")
    Cfg.CK_RMIN = 3
    # storage full: nothing chopped, nothing felled
    St.LOCK.lock()
    try:
        lim = int(M.limOf(FO, p, 0))
        p.setProperty("foraging.i0.stored", str(lim - int(M.heldN(FO, p, 0))))
        p.setProperty("foraging.i0.last", str(now[0]))
    finally:
        St.LOCK.unlock()
    c1 = int(Ck.CHOPS.get())
    s, pp = chop(spot=6)
    K.check(s.startswith("-This island's storage is full") and int(Ck.CHOPS.get()) == c1, "CK storage full: the click does nothing: %s" % s)
    # room for 1: a fall stores 1, says the rest did not fit
    St.LOCK.lock()
    try:
        p.setProperty("foraging.i0.stored", str(lim - int(M.heldN(FO, p, 0)) - 1))
    finally:
        St.LOCK.unlock()
    for i in range(12):
        s, pp = chop(spot=6)
        if i == 7:
            adv(1000)
    K.check(s.startswith("+Felled a T1 Oak tree: +1 Oak Log") and "did not fit" in s, "CK room for 1: %s" % s)
    K.eq(int(M.usedOf(FO, p, 0)), lim, "CK ... the island is exactly full")
    St.LOCK.lock()
    try:
        p.setProperty("foraging.i0.stored", "0")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    # a refused save: nothing added, the tree stands again (one more chop fells it)
    adv(1000)
    for i in range(11):
        chop(spot=7)
    adv(1000)
    before = _drops(p)
    St.FAIL_TEST = True
    s, pp = chop(spot=7)
    St.FAIL_TEST = False
    K.check(s.startswith("-The shard file could not be saved") and _drops(p) == before, "CK a refused save adds nothing: %s" % s)
    s, pp = chop(spot=7)
    K.check(s.startswith("+Felled"), "CK ... the tree stood again: one chop fells it: %s" % s)
    # the clicker switched off; a member who may not collect
    Cfg.CK_ON = False
    s, pp = chop(spot=0)
    K.check(s.startswith("-The shard clicker is switched off"), "CK switched off: %s" % s)
    Cfg.CK_ON = True
    Cfg.COOP_COLLECT = False
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER if str(u) == str(ou) else str(u)))
    mu = L["UUID"].fromString(MEMBER)
    r = Ck.chop(mu, JString(OWNER), FO, 0, 0, JString("Tool_Hatchet_Copper"))
    K.check(str(r[0]).startswith("-"), "CK a co-op member who may not collect: %s" % r[0])
    Cfg.COOP_COLLECT = True
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER))
    # no migration: every key that is not production / the clicker's own is as it was
    keep = dict((k_, v_) for k_, v_ in snap.items() if not re.search(r"\.(last|stored|drops|offAt|sacc|seed)$", k_))
    now_ = dict((str(k_), str(p.getProperty(k_))) for k_ in p.stringPropertyNames())
    Cfg.CK_CPS = 8
    K.eq(dict((k_, now_.get(k_)) for k_ in keep), keep, "CK no migration: the island's type / size / upgrades / totems are the clicker levels, untouched")
    K.check(not any(k_.endswith(".nsize") for k_ in now_), "CK ... no new key but the drops")
    K.save()


def run_collect(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "cc")
    M, St, Core, Cfg, Ck = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"]
    _foraging(L, p, stored=40)
    St.LOCK.lock()
    try:
        p.setProperty("foraging.i0.drops", OAK + ":25")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    g = dict((str(i), int(q)) for i, q in zip(*Core.gridOf(FO, p)))
    K.eq(g, {OAK: 65}, "CC the grid: the chopped logs merged with the stock (25 + 40)")
    K.eq(int(M.usedOf(FO, p, 0)), 65, "CC ... both use the island's storage")
    cs = L["inv"](1)   # one free slot: 100 logs fit
    got["coll"].clear(); got["xp"] = 0
    r = str(Core.collectKind(ou, JString(OWNER), FO, OAK, cs))
    K.check(r.startswith("+Collected 25 Oak Log (chopped); Collected 40 Oak Log"), "CC a cell click pays the chopped logs first, then the stock: %s" % r[:120])
    K.eq(int(L["count"](cs, OAK)), 65, "CC ... 65 logs in the inventory")
    K.eq(got["coll"].get(OAK, 0), 65, "CC ... the Oak collection +65 (25 chopped + 40)")
    K.eq(got["xp"], int(40 * int(Cfg.xpOf(FO)) * int(Cfg.XP_PCT) // 100), "CC ... XP only for the stock (the chopped logs paid at the click)")
    K.check(p.getProperty("foraging.i0.drops") is None and int(M.stored(FO, p, 0)) == 0, "CC ... the store is empty")
    # a full inventory: the chopped logs stay, exactly
    St.LOCK.lock()
    try:
        p.setProperty("foraging.i0.drops", OAK + ":150")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    cs2 = L["inv"](1)
    r = str(Core.collect(ou, JString(OWNER), FO, -1, cs2))
    K.check(r.startswith("+Collected 100 Oak Log (chopped). 50 did not fit"), "CC one free slot: 100 out, 50 stay: %s" % r)
    K.eq(_drops(p), {OAK: 50}, "CC ... 50 back in .drops")
    cs3 = L["inv"](1)
    cs3[0].addItemStack(L["IS"]("Wood_Beech_Trunk", 100))
    r = str(Core.collect(ou, JString(OWNER), FO, -1, cs3))
    K.check(r.startswith("-Your inventory is full") and _drops(p) == {OAK: 50}, "CC a full inventory: nothing moves: %s" % r)
    St.FAIL_TEST = True
    r = str(Core.collect(ou, JString(OWNER), FO, -1, L["inv"](5)))
    St.FAIL_TEST = False
    K.check(r.startswith("-Collect failed") and _drops(p) == {OAK: 50}, "CC a refused save takes nothing: %s" % r)
    cs4 = L["inv"](5)
    r = str(Core.collect(ou, JString(OWNER), FO, 0, cs4))
    K.check(r.startswith("+Collected 50 Oak Log (chopped)") and int(L["count"](cs4, OAK)) == 50 and p.getProperty("foraging.i0.drops") is None,
            "CC an island row's Collect pays them too: %s" % r)
    # the Farming shard (no drops) answers exactly as 0.4.22
    K.check(Core.collectHeld(ou, JString(OWNER), FK, -1, cs4, None) is None, "CC a shard with no chopped drops: the 0.4.22 Collect alone")
    K.save()


def run_upgrade(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "cu")
    M, St, Core, Cfg, Ck, Isl, Page = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShPage"]
    coins = L["coins"]
    _foraging(L, p)
    cv = float(Cfg.curve(int(Isl.band(1))))
    c1 = int(Ck.nodeCoins(1, cv))
    m1 = Ck.nodeMats(FO, int(Isl.LAD0[FO]), 1)
    K.check(c1 > 0 and [str(x) for x in m1[0]] == [EOAK] and [int(x) for x in m1[1]] == [1], "CU Tree size 1 costs %d coins + 1 Enchanted Oak" % c1)
    cs = L["inv"](10)
    coins["bal"] = c1 - 1
    r = str(Ck.buyNode(ou, JString(OWNER), FO, 0, 0, cs))
    K.check(r.startswith("-You need 1 Enchanted Oak") or r.startswith("-You need"), "CU no Enchanted Oak: refused: %s" % r)
    cs[0].addItemStack(L["IS"](EOAK, 5))
    r = str(Ck.buyNode(ou, JString(OWNER), FO, 0, 0, cs))
    K.check(r.startswith("-You need %s coins" % "{:,}".format(c1)) and int(L["count"](cs, EOAK)) == 5, "CU not enough coins: nothing taken: %s" % r)
    coins["bal"] = 1000000
    r = str(Ck.buyNode(ou, JString(OWNER), FO, 0, 0, cs))
    K.check(r.startswith("+Tree size 1/10") and coins["bal"] == 1000000 - c1 and int(L["count"](cs, EOAK)) == 4 and p.getProperty("foraging.i0.nsize") == "1",
            "CU bought: exact coins + 1 Enchanted Oak, nsize 1: %s" % r)
    r = str(Ck.buyNode(ou, JString(OWNER), FO, 0, 0, cs))
    K.check(r.startswith("=The page is up to date") and coins["bal"] == 1000000 - c1, "CU a stale double click buys once: %s" % r)
    K.eq(int(Ck.logsAt(1)), 4, "CU ... 4 logs a felled tree now")
    St.LOCK.lock()
    try:
        p.setProperty("foraging.i0.nsize", "10")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    r = str(Ck.buyNode(ou, JString(OWNER), FO, 0, 10, cs))
    K.check(r.startswith("=Tree size is at its highest"), "CU the highest level: %s" % r)
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER if str(u) == str(ou) else str(u)))
    r = str(Ck.buyNode(L["UUID"].fromString(MEMBER), JString(OWNER), FO, 0, -1, cs))
    K.check(r.startswith("-"), "CU a co-op member cannot buy: %s" % r)
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER))
    # the page: Tree count (sub 0) with the level it showed; a stale level refused; Island size only at 5 / 5 / 5; Spirit -> the Totems tab
    Page.TEST_INV = cs
    cs[0].addItemStack(L["IS"](OAK, 100))
    pg = Page(ou, W_)
    pg.kind = FO
    pg.view = 0
    Ck.HAND_TEST = "Tool_Hatchet_Copper"
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    T49._build(pg)
    K.check(int(pg.view) == 5 and bool(pg.ckUpOk[1]) and str(pg.ckUpE[1]) == "Trees %d -> %d" % (int(Isl.treeN(1, 0)), int(Isl.treeN(1, 1))), "CU the Tree count row: %s / %s" % (pg.ckUpE[1], pg.ckUpC[1]))
    cs[0].addItemStack(L["IS"]("Ingredient_Water_Essence", 50)); cs[0].addItemStack(L["IS"]("Rock_Stone_Cobble", 100))
    b0 = coins["bal"]
    pg.handleDataEvent(None, None, json.dumps({"a": "ku1:0"}))
    K.check(str(pg.stText).startswith("Tree Amount 1/5") and p.getProperty("foraging.i0.amt") == "1" and coins["bal"] < b0, "CU Tree count bought: %s" % pg.stText)
    b1 = coins["bal"]
    pg.handleDataEvent(None, None, json.dumps({"a": "ku1:0"}))
    K.check("up to date" in str(pg.stText) and coins["bal"] == b1 and p.getProperty("foraging.i0.amt") == "1", "CU ... the same click again buys nothing: %s" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku4:1"}))
    K.check("Max all 3 upgrades first" in str(pg.stText) and p.getProperty("foraging.i0.size") == "1", "CU Island size waits for 5 / 5 / 5: %s" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku3:0"}))
    K.check(p.getProperty("foraging.i0.irr") == "1", "CU Weather totem = Irrigation 1: %s" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku5:0"}))
    K.check(p.getProperty("foraging.i0.deco") == "1", "CU Decorations 1: %s" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku2:1"}))
    K.check(int(pg.view) == 0 and int(pg.tab) == 3 and int(pg.sel) == 0, "CU the Spirit row opens the Totems tab on this island")
    K.save()


def run_zones(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "cz")
    M, St, Core, Cfg, Ck, Isl, Page = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShPage"]
    coins = L["coins"]
    L0 = int(Isl.LAD0[FO])
    K.eq([int(Isl.zoneOf(L0 + i)) for i in range(15)], [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5], "CZ three woods a zone")
    K.eq([int(Isl.zoneNeed(FO, L0 + i)) for i in (0, 3, 6, 9, 12)], [0, 20, 40, 60, 80], "CZ the zones open at Foraging 0 / 20 / 40 / 60 / 80")
    K.eq(int(Isl.zoneNeed(FK, int(Isl.LAD0[FK]) + 5)), 0, "CZ ... Foraging only this round (Farming open)")
    _foraging(L, p)
    St.LOCK.lock()
    try:   # T1 Oak, T2 Beech, T3 Maple owned -> the next is T4 (Zone 2)
        for s, ty in ((1, str(Isl.KEY[L0 + 1])), (2, str(Isl.KEY[L0 + 2]))):
            p.setProperty("foraging.i%d.type" % s, ty); p.setProperty("foraging.i%d.size" % s, "1"); p.setProperty("foraging.i%d.last" % s, str(T0)); p.setProperty("foraging.i%d.stored" % s, "0")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    lv["Foraging"] = 19
    cs = L["inv"](20)
    coins["bal"] = 100000000
    r = str(Core.buyIsland(ou, JString(OWNER), FO, 3, cs))
    K.check(r.startswith("-Zone 2 is locked: the T4 ") and "Foraging 20 (you: 19)" in r, "CZ Foraging 19: the Zone 2 island waits: %s" % r)
    K.eq(int(Isl.slotOf(FO, p, L0 + 3)), -1, "CZ ... nothing bought")
    lv["Foraging"] = 20
    r = str(Core.buyIsland(ou, JString(OWNER), FO, 3, cs))
    K.check(not r.startswith("-Zone"), "CZ Foraging 20: the lock opens (the cost decides now): %s" % r)
    # an owned island in a locked zone stays open on the map
    St.LOCK.lock()
    try:
        p.setProperty("foraging.i5.type", str(Isl.KEY[L0 + 6])); p.setProperty("foraging.i5.size", "2"); p.setProperty("foraging.i5.last", str(T0)); p.setProperty("foraging.i5.stored", "0")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    lv["Foraging"] = 10
    Ck.HAND_TEST = "Tool_Hatchet_Copper"
    pg = Page(ou, W_)
    pg.kind = FO
    pg.view = 0
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    pg.handleDataEvent(None, None, json.dumps({"a": "kmap"}))
    bd = T49._build(pg)
    r_ = T410.full(pg)
    K.check(not r_["miss"] and not r_["unbound"], "CZ the map walks clean %s %s" % (r_["miss"][:2], r_["unbound"][:2]))
    K.check(not bool(pg.ckMLock[6]) and str(pg.ckMS[6]) == "Yours - Medium" and int(pg.ckMB[6]) == 1, "CZ the owned T7 island in locked Zone 3: open (%s)" % pg.ckMS[6])
    K.check(bool(pg.ckMLock[7]) and str(pg.ckMS[7]).startswith("Locked: ") and "#SkyyShKM7Lk" in bd["mk"], "CZ a T8 island not owned in Zone 3: locked + the lock picture")
    K.check(str(pg.ckZS[1]).startswith("Locked - ") and "(you: 10)" in str(pg.ckZS[1]), "CZ the Zone 2 header: %s" % pg.ckZS[1])
    K.check(int(pg.ckMB[0]) == 0 and str(pg.ckMS[0]).startswith("Shown now"), "CZ the shown island: %s" % pg.ckMS[0])
    pg.handleDataEvent(None, None, json.dumps({"a": "km6"}))
    K.check(int(pg.ckMode) == 0 and int(pg.ckSlot) == 5, "CZ Open = that island in the clicker (slot %s)" % pg.ckSlot)
    T49._build(pg)
    K.check(int(pg.ckSz) == 2 and str(pg.ckChip).startswith("T7 "), "CZ ... Medium T7 shown: %s" % pg.ckChip)
    K.save()


def run_page23(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "pg23")
    M, St, Core, Cfg, Ck, Isl, Page = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShPage"]
    _foraging(L, p, stored=12)
    Page.TEST_INV = L["inv"](20)
    Ck.HAND_TEST = "Tool_Hatchet_Copper"
    pg = Page(ou, W_)
    pg.kind = FO
    pg.view = 0
    pg.handleDataEvent(None, None, json.dumps({"a": "tab0"}))
    bm = T49._build(pg)
    K.check("#SkyyShClk" in bm["mk"] and bm["datas"].get("#SkyyShClk", "").find('"kopen"') >= 0, "PG23 the Foraging footer: Shard clicker -> kopen")
    pf = Page(ou, W_)
    pf.kind = FK
    pf.view = 0
    K.check("#SkyyShClk" not in T49._build(pf)["mk"], "PG23 the Farming footer has no clicker")
    pf.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    K.eq(int(pf.view), 0, "PG23 ... and kopen does nothing there")
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    K.eq(int(pg.view), 5, "PG23 kopen -> the clicker (view 5)")
    for sz in (1, 2, 3):
        St.LOCK.lock()
        try:
            p.setProperty("foraging.i0.size", str(sz)); p.setProperty("foraging.i0.amt", "5"); p.setProperty("foraging.i0.deco", "5"); p.setProperty("foraging.i0.irr", "5")
            p.setProperty("foraging.i0.totems", ",".join("lumber_spirit:1:::%d:fo%04d" % (q, q) for q in range(5)) if False else "lumber_spirit:1:::0:fo0001")
            St.save(OWNER, p)
        finally:
            St.LOCK.unlock()
        bd = T49._build(pg)
        r_ = T410.full(pg)
        K.check(not r_["miss"] and not r_["unbound"], "PG23 size %d walks clean %s %s" % (sz, r_["miss"][:2], r_["unbound"][:2]))
        n = int(Isl.treeN(sz, 5))
        hits = [s_ for s_ in bd["datas"] if s_.startswith("#SkyyShKH")]
        K.eq(len(hits), n, "PG23 size %d: %d tree squares" % (sz, n))
        K.check(all(('"kt%s:0"' % s_[len("#SkyyShKH"):]) in bd["datas"][s_] for s_ in hits), "PG23 ... each names its spot + the island slot")
        K.check("#SkyyShKIsl" in bd["mk"] and "ClkIsl%d.png" % sz in bd["mk"] and "#SkyyShKD4" in bd["mk"] and "#SkyyShKWx" in bd["mk"] and "#SkyyShKTo0" in bd["mk"],
                "PG23 ... the island picture, the 5 decorations, the weather totem, a spirit totem")
        els = bd["mk"].count("{") - bd["mk"].count('"{')
        K.check(els < 1000, "PG23 ... %d elements (well under ~1,600)" % els)
        K.check(bd["size"] < 1000000, "PG23 ... the packet stays small (%d bytes)" % bd["size"])
    # a click on a tree: the pop, the status
    bd = T49._build(pg)
    for i in range(12):
        pg.handleDataEvent(None, None, json.dumps({"a": "kt0:0"}))
        if i == 7:
            Core.NOW_TEST = T0 + 2000
    bd = T49._build(pg)
    K.check(str(pg.stText).startswith("Felled a T1 Oak tree: +3 Oak Log") and str(pg.ckPop) == "+3 Oak Log", "PG23 a tree falls: %s / %s" % (pg.stText, pg.ckPop))
    K.check("#SkyyShKPop" in bd["mk"] and bd["sets"].get("#SkyyShKPop.Text") == "+3 Oak Log", "PG23 ... the gold pop over it")
    K.check("ClkStump1.png" in bd["mk"], "PG23 ... it shows as a stump while it grows back")
    K.check(any(str(x) == OAK for x in pg.sgId) and "#SkyyShKC0B" in bd["datas"] and '"gc:%s"' % OAK in bd["datas"]["#SkyyShKC0B"], "PG23 the store cell: click = collect that kind")
    K.check("#SkyyShKCAll" in bd["datas"], "PG23 Collect all (owner)")
    pg.handleDataEvent(None, None, json.dumps({"a": "kt0:9"}))
    K.check("up to date" in str(pg.stText), "PG23 a stale island slot: %s" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "kstore"}))
    K.check(int(pg.view) == 0 and int(pg.tab) == 0, "PG23 Storage tab -> the shard menu's Collect tab")
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    pg.handleDataEvent(None, None, json.dumps({"a": "kback"}))
    K.check(int(pg.view) == 0 and int(pg.tab) == 1, "PG23 Shard menu -> the menu's Map tab")
    # no hatchet: the info line says so; the clicker off: no button, kopen refused
    Ck.HAND_TEST = None
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    T49._build(pg)
    K.check(str(pg.ckInfo).startswith("Hold a hatchet"), "PG23 no hatchet in hand: %s" % pg.ckInfo)
    Cfg.CK_ON = False
    pg.view = 0
    bm = T49._build(pg)
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    K.check("#SkyyShClk" not in bm["mk"] and int(pg.view) == 0 and "switched off" in str(pg.stText), "PG23 the clicker off: no button, kopen refused")
    Cfg.CK_ON = True
    # a co-op member (may collect): the trees can be chopped, no upgrade buttons
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER if str(u) == str(ou) else str(u)))
    pv = Page(L["UUID"].fromString(MEMBER), W_)
    pv.kind = FO
    pv.view = 0
    Ck.HAND_TEST = "Tool_Hatchet_Copper"
    pv.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    bv = T49._build(pv)
    K.check(bool(pv.manage) and any(s_.startswith("#SkyyShKH") for s_ in bv["datas"]) and not any(s_.startswith("#SkyyShKU") for s_ in bv["datas"] if s_ != "#SkyyShKU2X"),
            "PG23 a co-op member: trees yes, upgrades no")
    K.save()


EXPECT = {   # 0.4.22 -> 0.4.23, checked by hand 2026-11-21: the version texts (CfgFile / CfgFn / CfgRows / ShFill.markFixed / ShStore / the ready line) + the round
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'ShCfg': ['+f CK_CPS', '+f CK_DROPS', '+f CK_HP', '+f CK_NS_H', '+f CK_NS_MAX', '+f CK_NS_PER', '+f CK_NS_Q', '+f CK_ON', '+f CK_REGROW',
              '+f CK_RMIN', '+f CK_TSTEP', '+f CK_UP1', '+f CK_UP2', '+f CK_WSTEP', '+f CK_XP_PCT', '+f CK_ZLV', '+f DEF_CK_NS_H', '+f DEF_CK_NS_Q', '+f DEF_CK_ZLV', '~<clinit>', '~m loadCfg'],
    'ShCore': ['+m collectHeld', '+m collectS', '~m buyIsland0', '~m collect0', '~m gridOf'],
    'ShFill': ['~m markFixed'],
    'ShIsl': ['+m zoneNeed', '+m zoneNo', '+m zoneOf'],
    'ShPage': ['+f CKCY', '+f CKO1', '+f CKO2', '+f CKO3', '+f CKTW', '+f CKW1', '+f CKW2', '+f CKW3', '+f CKX1', '+f CKX2', '+f CKX3', '+f CKY1', '+f CKY2',
               '+f CKY3', '+f CK_RQN', '+f CK_STUMP', '+f CK_TREE', '+f ckAmt', '+f ckAxe', '+f ckCap', '+f ckChip', '+f ckDeco', '+f ckGrow', '+f ckHand',
               '+f ckInfo', '+f ckLv', '+f ckMB', '+f ckMCur', '+f ckMLock', '+f ckMN', '+f ckMS', '+f ckMode', '+f ckNext', '+f ckNs', '+f ckPop', '+f ckPopI',
               '+f ckSlot', '+f ckSpN', '+f ckSto', '+f ckStump', '+f ckSz', '+f ckT', '+f ckTi', '+f ckTn', '+f ckTree', '+f ckUpC', '+f ckUpCap', '+f ckUpE',
               '+f ckUpL', '+f ckUpOk', '+f ckUpSeen', '+f ckWx', '+f ckZS', '+m actClick', '+m buildClick', '+m ckCost', '+m ckSize', '+m fillClick', '+m handId',
               '~<clinit>', '~m act', '~m build0', '~m buildFull'],
    'ShStore': ['~m migrate', '~m migrate2', '~m save'],
    'SkyyShardsPlugin': ['~m setup'],
}


def _compare23(out, jar, old_jar, pkg, expect, added, removed=()):
    """the clicker's NEW non-class files (its pictures under SkyyShards/Map/Clk, the Skyglass theme) are new only (never in 0.4.22); the compare of 0.4.19
    (every other non-class file identical) + the kit's class compare run on a copy of the new jar without them"""
    NEWP = ("Common/UI/Custom/SkyyShards/Map/Clk", "Common/UI/Custom/SkyyGlass/")
    with zipfile.ZipFile(jar) as a, zipfile.ZipFile(old_jar) as b:
        na, nb = set(a.namelist()), set(b.namelist())
    new = sorted(n for n in na - nb if not n.endswith(".class"))
    assert all(n.startswith(NEWP) for n in new) and not any(n.startswith(NEWP) for n in nb), "C new non-class files outside the clicker's folders: %s" % [n for n in new if not n.startswith(NEWP)][:8]
    print("C. %d new non-class files (the clicker pictures + the Skyglass theme)" % len(new))
    cp = os.path.join(SCRATCH, "compare-%s.jar" % VERSION)
    with zipfile.ZipFile(jar) as zi, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if not n.startswith(NEWP):
                zo.writestr(n, zi.read(n))
    T419._compare(out, cp, old_jar, pkg, expect, added, removed)


def run_bytecode23(out, jar, scratch, home):
    """0.4.15's lock scan on THIS jar; its control (the 0.4.14 jar's known leak) only when that jar is on the disk"""
    if os.path.isfile(T415.OLD_JAR):
        return T415.run_bytecode(out, jar, scratch, home)
    K = HK.Child(out)
    import jpype
    if not jpype.isJVMStarted():
        HK.jvm([T415.B.JAVASSIST], verify=False)
    n, bad = T415.lock_scan(jar)
    K.check(n > 60 and not bad, "LB the bytecode scan: %d methods take / release ShStore.LOCK, no path leaves one with a different hold count: %s" % (n, bad[:4]))
    print("LB note: the control scan needs SkyyShards-0.4.14.jar (not on this disk) - skipped")
    K.save()


def run_live(out, jar, scratch, home):
    T421.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run_compare = _compare23
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ShClk"],
           phases=[("static", run_static), ("click23", run_click), ("collect23", run_collect), ("upgrade23", run_upgrade), ("zones23", run_zones),
                   ("page23", run_page23),
                   ("combat22", T422.run_combat), ("farm22", T422.run_farm), ("page22", T422.run_page22),
                   ("geo", T421.run_geo), ("rebuild", T421.run_rebuild), ("level", T421.run_level), ("bags", T421.run_bags), ("page21", T421.run_page21),
                   ("comp", T420.run_comp), ("sell20", T420.run_sell), ("mig20", T420.run_mig20), ("ore", T420.run_ore), ("deb", T420.run_deb), ("page20", T420.run_page20), ("livecomp", T420.run_livecomp),
                   ("off", T419.run_off), ("mig", T419.run_mig), ("sell", T419.run_sell), ("page", T419.run_page),
                   ("open", T416._h(T416._g(T416.run_open), True)), ("bytecode", run_bytecode23),
                   ("flows3", T416._h(T416._g(T413.run_flows3))), ("page49", T419.run_page49),
                   ("live", run_live)],
           script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
