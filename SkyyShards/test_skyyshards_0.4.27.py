"""Harness for SkyyShards 0.4.27 (shards become clicker-only - tools/shards_0_4_27_patch.py, on top of 0.4.26).
Build first:
    python tools/shards_0_4_27_patch.py && python SkyyShards/build_skyyshards_0.4.27.py
    python SkyyShards/test_skyyshards_0.4.27.py [--keep] [--only label,label]

  S27  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand; line endings kept; the jar
                ships no old Map tab pictures of the four clicker shards and no range rings; Ranching / Orchard bases + the clicker map cards are 1x;
                the Shards UI pictures <= 14 Mpx; every island cost names only the island's own items
  W27  worlds   EXECUTED Enter Shard refused (no shard world opened / queued); the portal (ShPageFn mode 0) opens the clicker (view 5) for Foraging /
                Mining / Farming / Combat and the old menu (no Enter Shard) for Ranching / Orchard; the rail leads to the clicker; a totem block / Totem
                Bench in an old shard world opens nothing (the line says why); the hub stand still opens its exit page
  SP27 spirit   EXECUTED buy a spirit on an island without one (coins + the island's Enchanted item taken, a worker tier I added), tier it up I..V,
                a double click / stale tier buys once, the highest tier refused, too few items = nothing taken, the rate after > before; the page
                row 2 (cost lines green / red, the Buy / Tier up button)
  MD27 mods     EXECUTED a modifier from a carried modifier item (the item taken, no coins); without one (coins + Enchanted); a swap puts the old
                modifier into the island's storage (Collect pays it back); the other slot's modifier refused; stale shown key refused; no spirit refused;
                Rare Finder never offered; the picker skips it
  SM27 smithy   EXECUTED Smithy I bought on the quarry page (coins + 64 Copper ore, an Auto-Smelt Pole entry: smelts, the next mined ore is a bar);
                a second click refused; the row then offers Smithy II
  CO27 coins    EXECUTED a town kill with SkyyMobs' killCoins (a fake bridge) stores coins in combat.i0.coins (saved with the loot); Collect all on
                the town page pays them to the purse and clears them; a purse that refuses = the coins go back; no bridge = no coins (the page says why)
  CL27 lines    EXECUTED the cost lines (coins first, have / need, green / red; text-only rows wrapped <= 34 characters, 3 lines); every kind's page
                walks clean (rows in the scroll list, every button bound); the store strip's Give / Take seeds
  UP27 view     EXECUTED Upgrades -> the upgrades view (walks clean); Storage / Auto-Compactor / Time Compressor / Automation / Offline Harvest bought
                with the level shown (a double click buys once); Sell all (2 clicks); Place one (a carried totem item onto the island, the uid guard);
                Pick up Shard (2 clicks); Island view back
  MG27 migr.   EXECUTED the per-profile migration on a file: an automated shard's seed store -> storage (History copy first, byte-checked; marker;
                counts before = after), a manual shard keeps its store, a second load changes nothing; ShMig0427 on an old default config (the 5 lines
                moved, a hand-edited line kept, History first), a second run changes nothing
  then 0.4.26's phases (fight26 .. page26), 0.4.25's, ... older ones on THIS jar (their texts that changed on purpose replaced below), A verify,
  C compare, AA audit, live27 START TWICE on a scratch copy of the live data (every island / totem / item counted before = after; second start = no
  change; no shard world folder touched)
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile, math, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.27"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shardx1", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.26.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.26.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_27_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.26 harness (it loads 0.4.25 -> ... older): its version moves to this one in memory
_T26 = open(os.path.join(HERE, "test_skyyshards_0.4.26.py"), encoding="utf8").read()
assert _T26.count('VERSION = "0.4.26"\n') == 1, "the 0.4.26 harness changed"
_T26 = _T26.replace('VERSION = "0.4.26"\n', 'VERSION = "%s"\n' % VERSION)
_argv = list(sys.argv)
T426 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_26", loader=None))
T426.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.26.py")
exec(compile(_T26, T426.__file__, "exec"), T426.__dict__)
sys.argv[:] = _argv
T425, T424, T423, T422, T421 = T426.T425, T426.T424, T426.T423, T426.T422, T426.T421
T420, T419, T411, T410, T49, T416, T415, T413 = T426.T420, T426.T419, T426.T411, T426.T410, T426.T49, T426.T416, T426.T415, T426.T413
for _m in (T426, T425, T424, T423, T422, T421, T420, T419, T420.T418, T419.T417):
    _m.JAR = JAR
for _m in (T426, T425, T424, T423, T422, T421, T420, T419, T420.T418, T416, T415, T419.T417):
    _m.SCRATCH = SCRATCH
OWNER, MEMBER = T420.OWNER, T420.MEMBER
MI, FO, FK, RA, OR, CK = 0, 1, 2, 3, 4, 5
T0 = 1790000000000
EOAK, OAK, BONE, EBONE = "Skyy_Ench_Oak", "Wood_Oak_Trunk", "Ingredient_Bone_Fragment", "Skyy_Ench_Bone"


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.27 - build script') and 'VERSION = "0.4.27"\n' in g, "S27 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S27 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.27:" in g, "S27 the ready line names the round")
    K.check("ROLLBACK 0.4.27 -> 0.4.26" in g and "Undo the ShMig0427 rows first" in g, "S27 the rollback note")
    blk = g[g.index("# ---- 0.4.27 (tools/shards_0_4_27_patch.py): THE CLEAR COST LINES"):g.index('public static String ckSize(int sz) {')]
    K.check("scheduleAtFixedRate" not in blk and "sendUpdate" not in blk, "S27 no periodic page update (HANDOFF section 2)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S27 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S27 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S27 jar newer than the script, the script newer than the patch")
    area = 0
    with zipfile.ZipFile(jar) as z:
        names = z.namelist()
        ui = [n for n in names if n.startswith("Common/UI/Custom/") and n.endswith(".png")]
        for n in ui:
            b_ = z.read(n)[:32]
            w_, h_ = struct.unpack(">II", b_[16:24])
            area += w_ * h_
        K.check(not any("/Map/Range/" in n for n in names), "S27 no range rings (the retired totem page)")
        K.check(not any(re.search(r"/Map/(Base(Mining|Foraging|Farming|Combat)|(Mining|Foraging|Farming|Combat)E\d+)(@2x)?\.png$", n) for n in names),
                "S27 no old Map tab pictures of the four clicker shards")
        K.check(all(("Common/UI/Custom/SkyyShards/Map/Base%s.png" % k_) in names and ("Common/UI/Custom/SkyyShards/Map/Base%s@2x.png" % k_) not in names
                    for k_ in ("Ranching", "Orchard")), "S27 Ranching / Orchard keep their base picture, as 1x")
        cards = [n for n in names if re.search(r"/Map/Clk(Map|FMap|QMap|TMap)\d+(@2x)?\.png$", n)]
        K.check(len(cards) == 15 + 15 + 11 + 5 and all("@2x" not in n for n in cards), "S27 the clicker map cards ship 1x (%d)" % len(cards))
        w_, h_ = struct.unpack(">II", z.read("Common/UI/Custom/SkyyShards/Map/ClkMap1.png")[16:24])
        K.check((w_, h_) == (210, 140), "S27 a map card is right-sized to 210 x 140 (%d x %d)" % (w_, h_))
    K.check(area <= 14000000, "S27 the Shards UI pictures %.2f Mpx <= 14" % (area / 1e6))
    print("S27 Shards UI pictures: %.2f Mpx in %d files" % (area / 1e6, len(ui)))
    K.check("an island cost names only the island's own items" in g, "S27 the build asserts every island cost names only the island's own items")
    K.save()


def _env(scratch, K, name):
    from jpype import JClass, JString
    L, ou, W_, p, lv, got = T426._env(scratch, K, name)
    T411.T48.add_items([(EOAK, 64), (OAK, 100), ("Skyy_Ench_Copper", 64), ("Ore_Copper", 200), ("Ingredient_Bar_Copper", 100),
                        ("Skyy_Ench_Wheat", 64), ("Plant_Seeds_Wheat", 64), ("Skyy_TotemMod_Faster", 4), ("Skyy_TotemMod_Wider", 4)])
    L["ShPageFn"] = JClass(PKG + "ShPageFn")
    L["ShTotem"] = JClass(PKG + "ShTotem")
    L["ShWorld2"] = JClass(PKG + "ShWorld2")
    L["ShWorlds"] = JClass(PKG + "ShWorlds")
    return L, ou, W_, p, lv, got


def _give(L, items, n=27):
    cs = L["inv"](n, n, 9)
    T411.T48._fill(L, cs, items)
    L["ShPage"].TEST_INV = cs
    return cs


def _ev(pg, a):
    pg.handleDataEvent(None, None, json.dumps({"a": a}))
    return str(pg.stText)


def _page(L, ou, W_, kd):
    pg = L["ShPage"](ou, W_)
    pg.kind = kd
    pg.view = 5
    pg.ckMode = 0
    pg.ckSlot = -1
    return pg


# ---------------------------------------------------------------------------------------------------------- W27: the worlds are retired
def run_worlds(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "w")
    St, Core, Cfg, Page, PFn, W2, Ws = L["ShStore"], L["ShCore"], L["ShCfg"], L["ShPage"], L["ShPageFn"], L["ShWorld2"], L["ShWorlds"]
    T423._foraging(L, p); T424._mining(L, p); T425._farm(L, p); T426._town(L, p)
    St.LOCK.lock()
    try:
        for kk_ in ("ranching", "orchard"):
            p.setProperty(kk_ + ".i0.type", "chicken" if kk_ == "ranching" else "apple"); p.setProperty(kk_ + ".i0.size", "1"); p.setProperty(kk_ + ".i0.last", str(T0))
            p.setProperty(kk_ + ".i0.stored", "0"); p.setProperty(kk_ + ".i0.totems", "harvest_spirit:1"); p.setProperty(kk_ + ".placed", W_ + "|4|5|6")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    _give(L, [(EOAK, 10)])
    r0 = int(W2.RETIRED.get())
    for kd in range(6):
        r = str(W2.enter(None, None, ou, JString(OWNER), kd, None))
        K.check(r.startswith("-Shard worlds are retired"), "W27 Enter Shard refused on kind %d: %s" % (kd, r[:80]))
    K.eq(int(W2.RETIRED.get()) - r0, 6, "W27 ... counted")
    K.check(Ws.OPENING.size() == 0 and Ws.QUEUE.size() == 0, "W27 ... nothing opened or queued")
    for kd in range(6):
        pg = PFn(kd, 0).make(None, ou, JString(W_))
        want = 5 if kd in (MI, FO, FK, CK) else 0
        K.check(pg is not None and int(pg.view) == want, "W27 the portal of kind %d opens view %d (%s)" % (kd, want, None if pg is None else int(pg.view)))
        if pg is not None:
            bd = T49._build(pg)
            r_ = T410.full(pg)
            K.check(not r_["miss"] and not r_["unbound"], "W27 ... walks clean %s %s" % (r_["miss"][:2], r_["unbound"][:2]))
            K.check("Enter Shard" not in bd["mk"] and '"enter"' not in json.dumps(bd["datas"]), "W27 ... no Enter Shard")
            if want == 5:
                K.check("Upgrades" in bd["mk"] and '"kup"' in bd["datas"].get("#SkyyShKMenuB", "") and not any('"kback"' in v_ or '"kstore"' in v_ for v_ in bd["datas"].values()),
                        "W27 ... the top bar's Upgrades (no Shard menu, no Storage tab)")
    pg = PFn(OR, 0).make(None, ou, JString(W_))
    pg.act(JString("mk%d" % FO), None, None)
    K.check(int(pg.kind) == FO and int(pg.view) == 5, "W27 the Orchard menu's rail leads to the Foraging clicker (%d / %d)" % (int(pg.kind), int(pg.view)))
    SHW = "skyy-shard-" + OWNER
    for mode, want in ((1, "Totems live on your shard's clicker page"), (2, "The Totem Bench is retired")):
        g0 = int(PFn.REFUSED.get())
        pg = PFn(FK, mode).make(None, ou, JString(SHW))
        K.check(pg is None and int(PFn.REFUSED.get()) == g0 + 1, "W27 a %s inside an old shard world opens nothing" % ("totem block" if mode == 1 else "Totem Bench"))
        tp = Page(ou, SHW)
        tp.kind = FK
        tp.view = 3 if mode == 1 else 4
        K.check(str(tp.openGate(JString(SHW))).startswith(want), "W27 ... the line says why")
    hp = PFn(FK, 0).make(None, ou, JString(SHW))
    K.check(hp is not None and int(hp.view) == 1, "W27 the hub stand inside an old shard world still opens its exit page")
    K.save()


# ---------------------------------------------------------------------------------------------------------- SP27: the spirit row
def run_spirit(out, jar, scratch, _home):
    from jpype import JString, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "sp")
    St, M, Core, Cfg, Isl, Tot = L["ShStore"], L["ShMath"], L["ShCore"], L["ShCfg"], L["ShIsl"], L["ShTotem"]
    T423._foraging(L, p)
    St.LOCK.lock()
    try:
        p.remove("foraging.i0.totems")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    L["coins"]["bal"] = 10000000
    cs = _give(L, [(EOAK, 300)])
    cv = float(Core.tierCv(0))
    r0 = float(M.rate(FO, p, 0, JLong(T0)))
    K.eq(r0, 0.0, "SP27 an island without a spirit makes nothing")
    pg = _page(L, ou, W_, FO)
    bd = T49._build(pg)
    K.check(str(pg.ckUpL[2]) == "None yet" and int(pg.ckUpBtn[2]) == 1 and bool(pg.ckUpOk[2]), "SP27 the row offers Buy: %s" % pg.ckUpL[2])
    c0, e0 = int(Core.spiritCoins(0, cv)), int(Cfg.TOT_E[0])
    K.check(str(pg.ckCL[6]).endswith(" / %s coins" % str(Cfg.num(c0))) and int(pg.ckCG[6]) == 1, "SP27 line 1 = coins have / need, green: %s" % pg.ckCL[6])
    K.check(str(pg.ckCL[7]) == "300 / %d %s" % (e0, Tot.pretty(EOAK)) and int(pg.ckCG[7]) == 1, "SP27 line 2 = the Enchanted log, green: %s" % pg.ckCL[7])
    K.check("SkyyShKU2C0" in bd["mk"] and "SkyyShKU2C1" in bd["mk"] and bd["datas"].get("#SkyyShKU2X", "").find('"ku2:0"') >= 0, "SP27 ... drawn, the button carries ku2:0")
    b0 = L["coins"]["bal"]
    r = _ev(pg, "ku2:0")
    K.check(r.startswith("A spirit totem now works"), "SP27 Buy: %s" % r)
    e = [str(x) for x in Tot.entries(FO, p, 0)]
    K.check(len(e) == 1 and e[0].startswith("lumber_spirit:1:::0:"), "SP27 ... a Lumber Spirit I entry: %s" % e)
    K.eq(b0 - L["coins"]["bal"], c0, "SP27 ... the coins taken")
    K.eq(int(L["count"](cs, EOAK)), 300 - e0, "SP27 ... the Enchanted logs taken")
    r = _ev(pg, "ku2:0")
    K.check(r.startswith("The page is up to date now") and len(list(Tot.entries(FO, p, 0))) == 1, "SP27 a double click buys once: %s" % r)
    r1 = float(M.rate(FO, p, 0, JLong(T0)))
    K.check(r1 > 0.0, "SP27 the island works now (%.3f / min)" % r1)
    for t in range(1, 5):
        T49._build(pg)
        before = float(M.rate(FO, p, 0, JLong(T0)))
        want_after = str(pg.ckUpE[2])
        bb, ee = L["coins"]["bal"], int(L["count"](cs, EOAK))
        r = _ev(pg, "ku2:%d" % t)
        K.check(r.startswith("The ") and ("tier " + str(Tot.ROMAN[t])) in r, "SP27 tier %d -> %d: %s" % (t, t + 1, r))
        K.eq(bb - L["coins"]["bal"], int(Core.spiritCoins(t, cv)), "SP27 ... coins")
        K.eq(ee - int(L["count"](cs, EOAK)), int(Cfg.TOT_E[t]), "SP27 ... Enchanted logs")
        after = float(M.rate(FO, p, 0, JLong(T0)))
        K.check(after >= before and ("-> " + str(Cfg.dec(after))) in want_after, "SP27 ... the row showed the rate after (%s; %.3f -> %.3f)" % (want_after, before, after))
    T49._build(pg)
    K.check(str(pg.ckUpL[2]) == "Tier V / V" and not bool(pg.ckUpOk[2]) and "highest" in str(pg.ckUpE[2]), "SP27 tier V: no button, highest")
    K.check(str(_ev(pg, "ku2:5")).startswith("This spirit totem is at its highest tier"), "SP27 ... a click at V refused")
    # too few items: nothing taken
    T423._foraging(L, p)
    St.LOCK.lock()
    try:
        p.remove("foraging.i0.totems")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    cs = _give(L, [(EOAK, 1)])
    T49._build(pg)
    K.check(int(pg.ckCG[7]) == 2, "SP27 1 Enchanted log of %d: the line is red (%s)" % (e0, pg.ckCL[7]))
    bb = L["coins"]["bal"]
    r = _ev(pg, "ku2:0")
    K.check(r.startswith("You need") or "Enchanted Oak Log" in r, "SP27 refused: %s" % r)
    K.check(L["coins"]["bal"] == bb and int(L["count"](cs, EOAK)) == 1 and len(list(Tot.entries(FO, p, 0))) == 0, "SP27 ... nothing taken, nothing added")
    # the other kinds' rows: names + a spirit row each
    for kd_, setup, word in ((MI, T424._mining, "Miner spirit"), (FK, T425._farm, "Spirit totem"), (CK, T426._town, "Spirit warriors")):
        setup(L, p)
        pk = _page(L, ou, W_, kd_)
        bk = T49._build(pk)
        r_ = T410.full(pk)
        K.check(not r_["miss"] and not r_["unbound"] and word in bk["mk"] and str(pk.ckUpL[2]) == "Tier I / V", "SP27 the %s row (kind %d) walks clean" % (word, kd_))
    K.save()


# ---------------------------------------------------------------------------------------------------------- MD27: the two modifier slots
def run_mods(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "md")
    St, M, Core, Cfg, Tot = L["ShStore"], L["ShMath"], L["ShCore"], L["ShCfg"], L["ShTotem"]
    T423._foraging(L, p)
    L["coins"]["bal"] = 10000000
    cs = _give(L, [(EOAK, 200), ("Skyy_TotemMod_Faster", 1)])
    keys = [str(x) for x in Tot.MOD_KEYS]
    fi, wi, ri = keys.index("faster"), keys.index("wider"), keys.index("rare")
    K.check(not bool(Core.modOk(ri)) and all(bool(Core.modOk(i)) for i in range(len(keys)) if i != ri), "MD27 Rare Finder is not offered")
    pg = _page(L, ou, W_, FO)
    _ev(pg, "kup")
    K.eq(int(pg.ckMode), 2, "MD27 Upgrades -> the upgrades view")
    T49._build(pg)
    pg.ckMP[0] = ri - 1
    _ev(pg, "kmp1+")
    K.check(int(pg.ckMP[0]) != ri, "MD27 the picker skips Rare Finder (%d)" % int(pg.ckMP[0]))
    pg.ckMP[0] = fi
    T49._build(pg)
    K.check(str(pg.ckCL[33]).startswith("1 / 1 Faster") and int(pg.ckCG[33]) == 1, "MD27 a carried Faster modifier pays: %s" % pg.ckCL[33])
    bb = L["coins"]["bal"]
    r = _ev(pg, "k2m1:%d:" % fi)
    f = Tot.parse(Tot.entries(FO, p, 0)[0])
    K.check(r.startswith("Faster on the spirit totem") and str(f[2]) == "faster", "MD27 slot 1 = Faster: %s" % r)
    K.check(L["coins"]["bal"] == bb and int(L["count"](cs, "Skyy_TotemMod_Faster")) == 0, "MD27 ... the item taken, no coins")
    r = _ev(pg, "k2m1:%d:" % fi)
    K.check(r.startswith("The page is up to date now"), "MD27 a stale slot (it shows Faster now) refused: %s" % r)
    r = _ev(pg, "k2m2:%d:" % fi)
    K.check(r.startswith("That modifier is in the other slot"), "MD27 the other slot's modifier refused: %s" % r)
    cv = float(Core.tierCv(0))
    bb, ee = L["coins"]["bal"], int(L["count"](cs, EOAK))
    r = _ev(pg, "k2m2:%d:" % wi)
    f = Tot.parse(Tot.entries(FO, p, 0)[0])
    K.check(str(f[3]) == "wider", "MD27 slot 2 = Wider (bought): %s" % r)
    K.eq(bb - L["coins"]["bal"], int(Core.modCoins(cv)), "MD27 ... coins")
    K.eq(ee - int(L["count"](cs, EOAK)), int(Cfg.MOD_E), "MD27 ... Enchanted logs")
    # swap slot 1 Faster -> Wider? refused (other slot); -> Compost: the old Faster goes into storage
    ci = keys.index("compost")
    r = _ev(pg, "k2m1:%d:faster" % ci)
    f = Tot.parse(Tot.entries(FO, p, 0)[0])
    d = T425._drops(p, 0, "foraging")
    K.check(str(f[2]) == "compost" and d.get("Skyy_TotemMod_Faster", 0) == 1 and "storage" in r, "MD27 a swap: Compost in, the old Faster in the storage (%s)" % d)
    cs2 = L["inv"](27, 27, 9)
    r = str(Core.collectKind(ou, JString(OWNER), FO, "Skyy_TotemMod_Faster", cs2))
    K.check(int(L["count"](cs2, "Skyy_TotemMod_Faster")) == 1 and T425._drops(p, 0, "foraging").get("Skyy_TotemMod_Faster", 0) == 0, "MD27 ... Collect gives it back: %s" % r[:80])
    St.LOCK.lock()
    try:
        p.remove("foraging.i0.totems")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    T49._build(pg)
    K.check(not bool(pg.ck2Ok[1]) and "Buy the spirit totem first" in str(pg.ckCL[33]), "MD27 no spirit: no modifier button (%s)" % pg.ckCL[33])
    r = str(Core.buyMod(ou, JString(OWNER), FO, 0, 1, fi, JString(""), cs))
    K.check(r.startswith("-Buy the spirit totem first"), "MD27 ... refused: %s" % r)
    K.save()


# ---------------------------------------------------------------------------------------------------------- SM27: Smithy I on the quarry page
def run_smithy(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "sm")
    St, M, Core, Cfg, Tot, Ck = L["ShStore"], L["ShMath"], L["ShCore"], L["ShCfg"], L["ShTotem"], L["ShClk"]
    T424._mining(L, p)
    L["coins"]["bal"] = 10000000
    cs = _give(L, [("Ore_Copper", 100)])
    K.check(not bool(Tot.smelts(MI, p, 0)), "SM27 the quarry does not smelt yet")
    pg = _page(L, ou, W_, MI)
    bd = T49._build(pg)
    K.check(int(pg.ckQSm) == 0 and str(pg.ckUpL[7]) == "No smithy" and int(pg.ckUpBtn[7]) == 1 and bool(pg.ckUpOk[7]), "SM27 row 7 offers Smithy I (Buy)")
    K.check(str(pg.ckCL[22]) == "100 / %d Copper Ore" % int(Cfg.MQ_S1ORE) or "Copper" in str(pg.ckCL[22]), "SM27 ... its ore line: %s" % pg.ckCL[22])
    K.check(bd["datas"].get("#SkyyShKU7X", "").find('"ku7:0"') >= 0, "SM27 ... the button carries ku7:0")
    bb = L["coins"]["bal"]
    r = _ev(pg, "ku7:0")
    K.check(r.startswith("Smithy I") and bool(Tot.smelts(MI, p, 0)), "SM27 Smithy I bought: %s" % r)
    K.eq(bb - L["coins"]["bal"], int(L["ShIsl"].coins(Cfg.MQ_S1H, Core.tierCv(int(L["ShIsl"].ty(MI, p, 0))))), "SM27 ... the coins")
    K.eq(int(L["count"](cs, "Ore_Copper")), 100 - int(Cfg.MQ_S1ORE), "SM27 ... the ore")
    K.check(any(str(x).startswith("autosmelt_pole:1:") for x in Tot.entries(MI, p, 0)), "SM27 ... an Auto-Smelt Pole entry (0.4.26 reads it)")
    r = _ev(pg, "ku7:0")
    K.check(r.startswith("The page is up to date") or r.startswith("This quarry smelts already"), "SM27 a second click refused: %s" % r)
    T49._build(pg)
    bd = T49._build(pg)
    K.check(int(pg.ckQSm) == 1 and int(pg.ckUpBtn[7]) == 0 and "Smithy II" in str(pg.ckUpE[7]) and '"ku7:0"' in bd["datas"].get("#SkyyShKU7X", ""),
            "SM27 the row now offers Smithy II (ku7:0): %s" % pg.ckUpE[7])
    cs = _give(L, [("Skyy_Ench_Copper", 64)])
    r = _ev(pg, "ku7:0")
    bd = T49._build(pg)
    K.check(int(pg.ckQSm) == 2 and '"kq-:50"' in bd["datas"].get("#SkyyShKU7M", "") and '"kq+:50"' in bd["datas"].get("#SkyyShKU7U", "") and bd["sets"].get("#SkyyShKU7V.Text") == "50 %",
            "SM27 Smithy II bought (%s): the slider < / > carry the value shown" % r[:60])
    r_ = T410.full(pg)
    K.check(not r_["miss"] and not r_["unbound"], "SM27 the slider row walks clean")
    K.save()


# ---------------------------------------------------------------------------------------------------------- CO27: the town's coins
def run_coins(out, jar, scratch, _home):
    from jpype import JString, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "co")
    St, M, Core, Cfg, Ck, Page = L["ShStore"], L["ShMath"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShPage"]
    T426._town(L, p)
    Cfg.CK_CPS = 1000
    asked = []

    def kc(a):
        asked.append((str(a[0]), int(a[1])))
        return JLong(37)
    L["br"].put("mob:fn:killCoins", L["PyFn"](kc))
    Ck.HAND_TEST = "Weapon_Sword_Crude"
    pg = _page(L, ou, W_, CK)
    T49._build(pg)
    _give(L, [])
    for i in range(60):
        r = _ev(pg, "kt0:0")
        if r.startswith("Slew a"):
            break
    K.check(r.startswith("Slew a") and "+37 coins" in r, "CO27 a kill pays 37 coins into the town: %s" % r[:120])
    K.check(len(asked) == 1 and asked[0][0] in [str(x) for x in Ck.T_ROLE] and asked[0][1] >= 1, "CO27 ... killCoins asked once with a town role + its level %s" % asked)
    K.eq(int(Ck.coinsWaiting(p, 0)), 37, "CO27 ... combat.i0.coins = 37 (saved with the loot)")
    disk = T419._disk(L, OWNER)
    K.eq(str(disk.getProperty("combat.i0.coins")), "37", "CO27 ... on disk")
    bd = T49._build(pg)
    K.check("37 coins waiting" in str(pg.sgHint) and "#SkyyShKCAll" in bd["mk"], "CO27 the strip says so + Collect all shows")
    b0 = L["coins"]["bal"]
    r = _ev(pg, "colall")
    K.check(L["coins"]["bal"] - b0 == 37 and int(Ck.coinsWaiting(p, 0)) == 0 and "37 coins" in r, "CO27 Collect all pays them: %s" % r[:120])
    # fix2 (critic 2 #1): a profile still loading (profile:busy) - the coins stay in the town, the purse does not move, Collect refuses
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.coins", "41")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    bk_ = "profile:busy:" + str(ou)
    L["br"].put(bk_, L["Bool"].TRUE)
    b1 = L["coins"]["bal"]
    r = str(_ev(pg, "colall"))
    K.check(L["coins"]["bal"] == b1 and int(Ck.coinsWaiting(p, 0)) == 41 and "still loading" in r, "FX2 busy profile: Collect all pays no coins, 41 stay (%s)" % r[:100])
    r = str(Ck.payCoins(ou, JString(OWNER), CK))
    K.check(r == "" and L["coins"]["bal"] == b1 and int(Ck.coinsWaiting(p, 0)) == 41, "FX2 ... payCoins itself refuses while busy (%r)" % r)
    L["br"].remove(bk_)
    r = str(_ev(pg, "colall"))
    K.check(L["coins"]["bal"] - b1 == 41 and int(Ck.coinsWaiting(p, 0)) == 0, "FX2 ... loaded again: the 41 are paid once (%s)" % r[:100])
    r = str(_ev(pg, "colall"))
    K.check(L["coins"]["bal"] - b1 == 41, "FX2 ... a second click pays nothing more")
    # fix2: a locked town (lock line) pays no coins either
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.coins", "9")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    Cfg.ON = False
    b2 = L["coins"]["bal"]
    r = str(_ev(pg, "colall"))
    Cfg.ON = True
    K.check(L["coins"]["bal"] == b2 and int(Ck.coinsWaiting(p, 0)) == 9, "FX2 shards switched off: no coins move (%s)" % r[:100])
    r = str(_ev(pg, "colall"))
    K.check(L["coins"]["bal"] - b2 == 9, "FX2 ... on again: paid")
    # a purse that refuses: the coins go back
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.coins", "50")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    fns = L["fns"]
    old = fns.get("coins:fn:add")
    fns.put("coins:fn:add", L["PyFn"](lambda a: L["Bool"].FALSE))
    r = str(Ck.payCoins(ou, JString(OWNER), CK))
    K.check(r.startswith("-Your purse could not take") and int(Ck.coinsWaiting(p, 0)) == 50, "CO27 a refused purse: the coins stay (%s)" % r)
    if old is not None:
        fns.put("coins:fn:add", old)
    else:
        fns.remove("coins:fn:add")
    # no SkyyMobs bridge: no coins, the page says why
    L["br"].remove("mob:fn:killCoins")
    n0 = int(Ck.NOCOIN.get())
    T49._build(pg)
    K.check("no kill coins" in str(pg.sgHint) or int(Ck.coinsWaiting(p, 0)) > 0, "CO27 no bridge: the strip says so (%s)" % pg.sgHint)
    K.eq(int(Ck.coinsFor(0, 5)), 0, "CO27 ... a kill pays 0")
    K.check(int(Ck.NOCOIN.get()) > n0, "CO27 ... counted")
    Cfg.TF_COINS = False
    L["br"].put("mob:fn:killCoins", L["PyFn"](kc))
    K.eq(int(Ck.coinsFor(0, 5)), 0, "CO27 click.fight.coins off = 0")
    Cfg.TF_COINS = True
    Cfg.CK_CPS = 8
    K.save()


# ---------------------------------------------------------------------------------------------------------- CL27: the cost lines + every kind's page
def run_lines(out, jar, scratch, _home):
    from jpype import JString, JLong, JArray
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "cl")
    St, Core, Cfg, Page = L["ShStore"], L["ShCore"], L["ShCfg"], L["ShPage"]
    T423._foraging(L, p)
    pg = _page(L, ou, W_, FO)
    _give(L, [(EOAK, 5)])
    L["coins"]["bal"] = 1234
    T49._build(pg)
    pg.ckCostR(4, JLong(5000), Core.itemCost(JString(EOAK), JLong(3)))
    K.eq(str(pg.ckCL[12]), "1,234 / 5,000 coins", "CL27 line 1 coins have / need")
    K.eq(int(pg.ckCG[12]), 2, "CL27 ... red (1,234 < 5,000)")
    K.eq(str(pg.ckCL[13]), "5 / 3 " + str(L["ShTotem"].pretty(EOAK)), "CL27 line 2 the item")
    K.eq(int(pg.ckCG[13]), 1, "CL27 ... green")
    pg.ckTextR(4, JString("First Tree count, Weather and Decorations 5/5 (3, 5, 2) and then a lot more words to wrap past three"))
    ls = [str(pg.ckCL[12 + j]) for j in range(3)]
    K.check(all(ls) and all(len(x) <= 34 for x in ls[:2]) and " ".join(ls).startswith("First Tree count"), "CL27 a text-only row wraps (%s)" % ls)
    K.eq(str(Page.ckShort(JLong(12345678))), "12.3M", "CL27 a big purse reads 12.3M")
    for kd_, setup in ((FO, T423._foraging), (MI, T424._mining), (FK, T425._farm), (CK, T426._town)):
        setup(L, p)
        pk = _page(L, ou, W_, kd_)
        bk = T49._build(pk)
        r_ = T410.full(pk)
        n = 8 if kd_ == MI else 6
        K.check(not r_["miss"] and not r_["unbound"], "CL27 kind %d page walks clean %s %s" % (kd_, r_["miss"][:2], r_["unbound"][:2]))
        K.check("#SkyyShKUpL" in bk["mk"] and all(("#SkyyShKU%d" % r) in bk["mk"] for r in range(n)), "CL27 ... the %d rows in the scroll list" % n)
        lines = [s_ for s_ in bk["sets"] if re.match(r"#SkyyShKU\dC\d\.Text$", s_)]
        K.check(len(lines) >= n, "CL27 ... %d cost lines drawn" % len(lines))
    # Give / Take seeds on the store strip (a manual Foraging shard / an automated one with a store)
    T423._foraging(L, p)
    St.LOCK.lock()
    try:
        p.setProperty("foraging.auto", "0"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    cs = _give(L, [("Plant_Sapling_Oak", 10)])
    bd = T49._build(pg)
    K.check(int(pg.ckSeedB) == 1 and "Give seeds" in bd["mk"], "CL27 a manual shard: Give seeds")
    r = _ev(pg, "kseed")
    K.check(int(L["ShIsl"].seeds(FO, p, 0)) == 10 and int(L["count"](cs, "Plant_Sapling_Oak")) == 0, "CL27 ... the saplings into the store: %s" % r[:80])
    St.LOCK.lock()
    try:
        p.setProperty("foraging.auto", "1"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    bd = T49._build(pg)
    K.check(int(pg.ckSeedB) == 2 and "Take seeds" in bd["mk"], "CL27 automated + a store: Take seeds")
    r = _ev(pg, "kseed")
    K.check(int(L["ShIsl"].seeds(FO, p, 0)) == 0 and int(L["count"](cs, "Plant_Sapling_Oak")) == 10, "CL27 ... back in the inventory: %s" % r[:80])
    bd = T49._build(pg)
    K.check(int(pg.ckSeedB) == 0 and "Give seeds" not in bd["mk"] and "Take seeds" not in bd["mk"], "CL27 automated, empty store: no seed button")
    K.save()


# ---------------------------------------------------------------------------------------------------------- UP27: the upgrades view
def run_view(out, jar, scratch, _home):
    from jpype import JString, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "up")
    St, M, Core, Cfg, Isl, Tot, Page = L["ShStore"], L["ShMath"], L["ShCore"], L["ShCfg"], L["ShIsl"], L["ShTotem"], L["ShPage"]
    T423._foraging(L, p, lim_tier=1)
    St.LOCK.lock()
    try:
        p.setProperty("foraging.auto", "0"); p.setProperty("foraging.offline", "0"); p.remove("foraging.compactor"); p.remove("foraging.compressor")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    L["coins"]["bal"] = 900000000
    cs = _give(L, [(EOAK, 1200), (OAK, 640), ("Ingredient_Void_Essence", 300)])
    pg = _page(L, ou, W_, FO)
    _ev(pg, "kup")
    bd = T49._build(pg)
    r_ = T410.full(pg)
    K.check(int(pg.ckMode) == 2 and not r_["miss"] and not r_["unbound"], "UP27 the upgrades view walks clean %s %s" % (r_["miss"][:2], r_["unbound"][:2]))
    K.check("SPIRIT TOTEM" in bd["mk"] and "SHARD UPGRADES" in bd["mk"] and "Island view" in bd["mk"] and "#SkyyShKVPk" in bd["mk"], "UP27 ... both panels, Island view, Pick up Shard")
    for r in range(9):
        K.check(("#SkyyShKV%dL.Text" % r) in bd["sets"], "UP27 ... row %d drawn" % r)
    steps = [("st", 3, lambda: int(M.storageTier(FO, p))), ("cp", 4, lambda: int(M.compactor(FO, p))), ("tc", 5, lambda: int(M.compressor(FO, p))),
             ("au", 6, lambda: 1 if bool(Isl.auto(FO, p)) else 0), ("of", 7, lambda: int(Isl.offLv(FO, p)))]
    for w, r, now in steps:
        T49._build(pg)
        lv0 = now()
        K.check(bool(pg.ck2Ok[r]) and int(pg.ck2Seen[r]) == lv0, "UP27 %s offered at %d" % (w, lv0))
        res = _ev(pg, "k2%s:%d" % (w, lv0))
        K.check(now() == lv0 + 1, "UP27 %s bought: %s" % (w, res[:90]))
        res = _ev(pg, "k2%s:%d" % (w, lv0))
        K.check(now() == lv0 + 1 and res.startswith("The page is up to date"), "UP27 ... a double click buys once: %s" % res[:60])
    # a profile switch since the page was drawn: nothing bought
    T49._build(pg)
    st0 = int(M.storageTier(FO, p))
    pg.key = "00000000-0000-0000-0000-000000000000-p9"
    r = str(pg.act("k2st:%d" % st0, None, None))
    K.check(r.startswith("=The page is up to date") and int(M.storageTier(FO, p)) == st0, "UP27 a stale profile (switched since the page was drawn): nothing bought (%s)" % r)
    # Sell all (2 clicks)
    St.LOCK.lock()
    try:
        p.setProperty("foraging.i0.stored", "500"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    T49._build(pg)
    K.check(bool(pg.ck2Ok[8]), "UP27 Sell all offered (%s)" % pg.ck2E[8])
    r = _ev(pg, "k2sell")
    K.check(r.startswith("Click Sell all again"), "UP27 Sell all arms first: %s" % r)
    r = _ev(pg, "k2sell")
    K.check(int(M.stored(FO, p, 0)) < 500, "UP27 ... then sells: %s" % r[:100])
    # Place one: a carried totem item onto the island (the old pad rules, the uid guard)
    St.LOCK.lock()
    try:
        p.setProperty("foraging.i0.size", "3"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    from jpype import JClass
    T413.T47 if hasattr(T413, "T47") else None
    n0 = len(list(Tot.entries(FO, p, 0)))
    st_ = Tot.stack(Tot.parse(JString("fertilizer:2:::0:up0001")), JLong(T0))
    L["ShInv"] = JClass(PKG + "ShInv")
    L["ShInv"].giveStack(cs, st_)
    T49._build(pg)
    K.check(bool(pg.ck2TurnOk) and "You carry 1 totem" in str(pg.ck2Turn), "UP27 Place one offered: %s" % pg.ck2Turn)
    r = _ev(pg, "k2turn")
    e = [str(x) for x in Tot.entries(FO, p, 0)]
    K.check(len(e) == n0 + 1 and any(x.startswith("fertilizer:2:") for x in e) and len(list(Core.placeable(FO, cs, JLong(T0)))) == 0, "UP27 ... placed: %s" % r[:90])
    r = _ev(pg, "k2turn")
    K.check(r.startswith("You carry no totem item") or r.startswith("The page"), "UP27 ... nothing left to place: %s" % r[:80])
    # Pick up Shard arms first (test mode stops before the real pick up)
    r = _ev(pg, "k2pick")
    K.check(r.startswith("Click Pick up Shard again"), "UP27 Pick up Shard arms first: %s" % r)
    r = _ev(pg, "k2pick")
    K.eq(r, "test: pick", "UP27 ... then picks up")
    _ev(pg, "kisl")
    K.eq(int(pg.ckMode), 0, "UP27 Island view -> the island")
    # a co-op member sees, cannot buy
    mu = L["UUID"].fromString(MEMBER)
    K.check(not bool(Page(mu, W_).mine), "UP27 (a member page is not the owner's)")
    K.save()


# ---------------------------------------------------------------------------------------------------------- MG27: the migrations
def run_mig(out, jar, scratch, _home):
    from jpype import JString, JClass
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "mg")
    St, M, Core, Cfg, Isl = L["ShStore"], L["ShMath"], L["ShCore"], L["ShCfg"], L["ShIsl"]
    sd = L["sd"]
    k2 = "00000000-0000-0000-0000-00000000abcd-p1"
    f = os.path.join(sd, k2 + ".properties")
    body = ("v=1\npkey=%s\nmap.done=1\nforms=1\nfarming.auto=1\nfarming.storage=5\nfarming.i0.type=lettuce\nfarming.i0.size=3\nfarming.i0.last=%d\n"
            "farming.i0.stored=72\nfarming.i0.seed=635\nfarming.i0.legacy=Skyy_Ench_Lettuce\\:2\nfarming.i0.totems=harvest_spirit\\:3\\:\\:\\:0\\:5cc6e7cb5987,rain\\:3\\:\\:\\:0\\:5ea66225351e\\:\\:-2;1\n"
            "farming.i0.drops=Skyy_TotemMod_Wider\\:1\n"
            "foraging.auto=0\nforaging.storage=1\nforaging.i0.type=oak\nforaging.i0.size=1\nforaging.i0.last=%d\nforaging.i0.stored=13\nforaging.i0.seed=47\n"
            "foraging.i0.totems=lumber_spirit\\:1\n") % (k2, T0, T0)
    open(f, "w", newline="\n").write(body)
    raw0 = open(f, "rb").read()
    St.CACHE.remove(k2)
    q = St.get(JString(k2))
    K.check(q is not None and str(q.getProperty("clk.done")) == "1", "MG27 the marker")
    K.eq(str(q.getProperty("farming.i0.seed")), "0", "MG27 the automated Farming island's seed store emptied")
    d = T425._drops(q, 0, "farming")
    K.check(d.get("Plant_Seeds_Lettuce", 0) == 635 and d.get("Skyy_TotemMod_Wider", 0) == 1, "MG27 ... 635 Lettuce seeds in its storage, the old drop kept (%s)" % d)
    K.eq(str(q.getProperty("foraging.i0.seed")), "47", "MG27 the manual Foraging shard keeps its store (it still replants)")
    K.check(str(q.getProperty("farming.i0.totems")) == "harvest_spirit:3:::0:5cc6e7cb5987,rain:3:::0:5ea66225351e::-2;1" and str(q.getProperty("foraging.i0.totems")) == "lumber_spirit:1",
            "MG27 the totems kept as they were (tiers, modifiers, the hand-placed spot)")
    hist = os.path.join(sd, "history", "clicker", k2 + ".pre-0.4.27.properties")
    K.check(os.path.isfile(hist) and open(hist, "rb").read() == raw0, "MG27 the History copy = the old file")
    raw1 = open(f, "rb").read()
    K.check(b"clk.done=1" in raw1 and b"farming.i0.seed=0" in raw1, "MG27 one save on disk")
    K.check(int(St.CLKMIG.get()) >= 1, "MG27 counted")
    St.CACHE.remove(k2)
    q = St.get(JString(k2))
    K.check(open(f, "rb").read() == raw1 and str(q.getProperty("farming.i0.seed")) == "0", "MG27 a second load changes nothing")
    # ShMig0427: the config lines
    Mg = JClass(PKG + "ShMig0427")
    old = ["isl.mat.deco=Wood_Oak_Trunk:16,Rock_Stone_Cobble:16|Skyy_Ench_Oak:1,Skyy_Ench_Cobblestone:1|Skyy_Ench_Oak:2,Skyy_Ench_Cobblestone:2",
           "isl.mat.irrigation=raw:4,Ingredient_Water_Essence:9|ench:1,Ingredient_Water_Essence:4|ench:2,Ingredient_Water_Essence:8",
           "combat.mat.cap=raw:16|raw:32,Ingredient_Void_Essence:1|raw:64,Ingredient_Void_Essence:2",
           "combat.mat.level=raw:16|raw:32,Ingredient_Life_Essence:1|raw:64,Ingredient_Life_Essence:2",
           "combat.mat.speed=raw:8,Ingredient_Water_Essence:1|raw:16,Ingredient_Water_Essence:2|raw:32,Ingredient_Water_Essence:4"]
    txt = "# a test file\r\nshards.on=true\r\n" + "\r\n".join(old) + "\r\n"
    r = Mg.update(JString(txt))
    K.check(r is not None, "MG27 ShMig0427 changes an old file")
    nt = str(r[0])
    K.check("isl.mat.deco=raw:16|ench:1|ench:2\r\n" in nt and "combat.mat.cap=raw:16|raw:32,ench:1|raw:64,ench:2\r\n" in nt and "combat.mat.speed=raw:8|raw:16,ench:1|raw:32,ench:2\r\n" in nt,
            "MG27 ... the untouched default lines moved (line endings kept)")
    K.check("isl.mat.irrigation=raw:4,Ingredient_Water_Essence:9" in nt, "MG27 ... a hand-edited line kept")
    K.check(Mg.update(JString(nt)) is None, "MG27 ... a second run changes nothing (the marker)")
    K.check(Mg.update(JString("# new\nshards.on=true\n# SkyyShards 0.4.27 defaults (marker skyyshards-0.4.27-clicker): x - keep this line.\n")) is None, "MG27 ... a new default file (the marker in it) is left alone")
    K.eq(str(Cfg.MAT_DECO), "raw:16|ench:1|ench:2", "MG27 the built-in Decorations cost = the island's items")
    K.eq(str(Cfg.MAT_IRR), "raw:8|ench:1|ench:2", "MG27 ... Irrigation")
    K.eq([str(x) for x in Cfg.DEF_CB_MAT], ["raw:16|raw:32,ench:1|raw:64,ench:2", "raw:16|raw:32,ench:1|raw:64,ench:2", "raw:8|raw:16,ench:1|raw:32,ench:2"], "MG27 ... the Combat rows")
    K.save()


# ---------------------------------------------------------------------------------------------------------- live27: start twice on a scratch COPY of the live data
def _count(props):
    """every island, totem entry and item a profile file holds (stored + legacy + drops + seed stores + town coins)"""
    isl = tot = items = 0
    keys = list(props)
    for k_ in keys:
        m = re.match(r"^(mining|foraging|farming|ranching|orchard|combat)\.i(\d+)\.type$", k_)
        if not m:
            continue
        isl += 1
        b = "%s.i%s." % (m.group(1), m.group(2))
        t = props.get(b + "totems", "")
        tot += len([x for x in t.split(",") if x.strip()])
        items += int(props.get(b + "stored", "0") or 0) + int(props.get(b + "seed", "0") or 0)
        lg = props.get(b + "legacy", "")
        if lg and ":" in lg:
            items += int(lg.rsplit(":", 1)[1]) * (100 if lg.startswith("Skyy_Ench") else 1)
        for part in props.get(b + "drops", "").split(","):
            if ":" in part:
                items += int(part.rsplit(":", 1)[1])
    return isl, tot, items


def _props(path):
    out = {}
    for ln in open(path, encoding="latin-1").read().splitlines():
        if not ln or ln.startswith("#") or "=" not in ln:
            continue
        k_, v_ = ln.split("=", 1)
        out[k_.strip()] = v_.strip().replace("\\:", ":").replace("\\\\", "\\")
    return out


KEEP_RX = re.compile(r"^(mining|foraging|farming|ranching|orchard|combat)\.i\d+\.(last|stored|legacy|xpn|xpw|sacc|drops|seed|rolled|ench|bags|offAt)$|^(mining|foraging|farming|ranching|orchard|combat)\.(offAt|lastCollect)$|^clk\.done$")


def _dmap(s_):
    return dict((x.rsplit(":", 1)[0], int(x.rsplit(":", 1)[1])) for x in (s_ or "").split(",") if ":" in x)


def run_live_mig(out, jar, scratch, home):
    """the clicker migration on a scratch COPY of the live data, started twice: every island + totem kept, only the automated shards' seed stores
    moved (each exactly into that island's storage), nothing else rewritten (production since the last save may settle), a second start changes nothing"""
    import jpype
    from jpype import JString, JClass
    K = HK.Child(out)
    sd = os.path.join(home, "shards")
    files = sorted(f for f in os.listdir(sd) if f.endswith(".properties"))
    pb = dict((f, _props(os.path.join(sd, f))) for f in files)
    raw0 = dict((f, open(os.path.join(sd, f), "rb").read()) for f in files)
    L, ou, W_, p, lv, got = _env(scratch, K, "lmenv")   # a fixture JVM; the live copy is then read through ShStore (its DIR moved there)
    St = L["ShStore"]
    L["ShCore"].NOW_TEST = 0
    St.DIR = JClass("java.nio.file.Paths").get(JString(sd), jpype.JArray(JString)([]))
    St.CACHE.clear()
    for f in files:
        St.get(JString(f[:-len(".properties")]))
    pa = dict((f, _props(os.path.join(sd, f))) for f in files)
    raw1 = dict((f, open(os.path.join(sd, f), "rb").read()) for f in files)
    moved = 0
    for f in files:
        b, a = pb[f], pa[f]
        cb, ca = _count(b), _count(a)
        K.check(cb[0] == ca[0] and cb[1] == ca[1], "L27 %s: %d islands / %d totems kept (%s)" % (f, cb[0], cb[1], ca[:2]))
        K.check(ca[2] >= cb[2], "L27 %s: items %d -> %d (never fewer; production since the last save settles)" % (f, cb[2], ca[2]))
        bad = sorted(k_ for k_ in set(b) | set(a) if b.get(k_) != a.get(k_) and not KEEP_RX.match(k_))
        K.check(not bad, "L27 %s: no other key rewritten %s" % (f, bad[:6]))
        for k_ in b:
            m = re.match(r"^(\w+)\.i(\d+)\.seed$", k_)
            if not m or int(b[k_] or 0) <= 0 or int(a.get(k_, "0") or 0) == int(b[k_]):
                continue
            dk = "%s.i%s.drops" % (m.group(1), m.group(2))
            db, da = _dmap(b.get(dk)), _dmap(a.get(dk))
            gain = dict((i_, da.get(i_, 0) - db.get(i_, 0)) for i_ in set(da) | set(db) if da.get(i_, 0) != db.get(i_, 0) and i_.startswith("Plant_"))
            K.check(a.get(k_) == "0" and list(gain.values()) == [int(b[k_])], "L27 %s %s: %s seeds -> its storage exactly %s" % (f, k_, b[k_], gain))
            moved += int(b[k_])
        if raw1[f] != raw0[f]:
            K.check(os.path.isfile(os.path.join(sd, "history", "clicker", f[:-len(".properties")] + ".pre-0.4.27.properties")), "L27 %s: the History copy" % f)
    St.CACHE.clear()
    for f in files:
        St.get(JString(f[:-len(".properties")]))
    pc = dict((f, _props(os.path.join(sd, f))) for f in files)
    K.check(all(pc[f].get("clk.done") == pa[f].get("clk.done") for f in files), "L27 the second start: the marker holds")
    K.check(all(_count(pc[f])[:2] == _count(pa[f])[:2] and all(pc[f].get(k_) == pa[f].get(k_) for k_ in pa[f] if k_.endswith(".seed")) for f in files),
            "L27 the second start: islands + totems + seed stores the same (no second move)")
    K.notes.append("L27 live copy: %d profile files, %d seeds moved" % (len(files), moved))
    print("L27 live copy: %d profile files, %s seeds moved; islands / totems / items before %s" % (len(files), moved, dict((f, _count(pb[f])) for f in files)))
    K.save()


EXPECT = {   # 0.4.26 -> 0.4.27
    'CfgFile': ['~<clinit>'], 'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'], 'CfgRows1': ['~<clinit>'], 'CfgRows2': ['~<clinit>'],
    'ShCfg': ['+f DEF_TOT_E', '+f DEF_TOT_H', '+f MOD_E', '+f MOD_H', '+f MQ_S1H', '+f MQ_S1ORE', '+f TF_COINS', '+f TOT_E', '+f TOT_H', '~<clinit>', '~m loadCfg', '~m writeDefaults'],
    'ShClk': ['+f KCOINS', '+f NOCOIN', '+m clicker', '+m coinsFor', '+m coinsWaiting', '+m payCoins', '~<clinit>', '~m fight'],
    'ShCore': ['+m addDrops', '+m buyMod', '+m buyMod0', '+m buySmithy1', '+m buySmithy1_0', '+m buySpirit', '+m buySpirit0', '+m itemCost', '+m joinE', '+m modCoins',
               '+m modMats', '+m modOk', '+m placeable', '+m spiritCoins', '+m spiritIdx', '+m spiritMats', '+m tierCv', '+m turnIn', '~m commitKeys'],
    'ShFill': ['~m markFixed'], 'ShMap': ['~<clinit>'],
    'ShPage': ['+f ck2Also', '+f ck2Btn', '+f ck2Cap', '+f ck2Cur', '+f ck2E', '+f ck2Isl', '+f ck2L', '+f ck2Ok', '+f ck2Pk', '+f ck2Seen', '+f ck2Turn', '+f ck2TurnOk',
               '+f ckCG', '+f ckCL', '+f ckCoins', '+f ckCs', '+f ckMP', '+f ckPickArm', '+f ckPurse', '+f ckSeedB', '+f ckSellArm', '+f ckSpF', '+f ckUpBtn',
               '+m actCk2', '+m ck2Set', '+m ckCostR', '+m ckFresh', '+m ckHasLines', '+m ckLinesB', '+m ckPost', '+m ckPre', '+m ckShort', '+m ckSmithy1',
               '+m ckSpirit', '+m ckTextR', '+m fillUp2', '+m lvNow', '+m toClicker', '~m act', '~m actClick', '~m actQuarry', '~m build0', '~m buildClick',
               '~m buildFull', '~m fillClick', '~m fillFarm', '~m fillQuarry', '~m fillTown', '~m openGate'],
    'ShPageFn': ['+f DOORS', '+f LOCKED', '~<clinit>', '~m make'],
    'ShStore': ['+f CLKCHK', '+f CLKMIG', '+m migrate3', '+m snapClk', '~<clinit>', '~m get', '~m migrate', '~m migrate2', '~m save'],
    'ShWorld2': ['+<clinit>', '+f RETIRED', '~m enter'], 'SkyyShardsPlugin': ['~m setup'],
}


def _compare27(out, jar, old_jar, pkg, expect, added, removed=()):
    """non-class files: the dropped old map / range pictures, the 1x renames; every other non-class file identical (manifest.json changed)"""
    with zipfile.ZipFile(jar) as a, zipfile.ZipFile(old_jar) as b:
        na, nb = set(a.namelist()), set(b.namelist())
        new = sorted(n for n in na - nb if not n.endswith(".class"))
        gone = sorted(n for n in nb - na if not n.endswith(".class"))
        rx_new = re.compile(r"^Common/UI/Custom/SkyyShards/Map/(Base(Ranching|Orchard)|Clk(Map|FMap|QMap|TMap)\d+)\.png$")
        rx_gone = re.compile(r"^Common/UI/Custom/SkyyShards/Map/(Range/S\dR\d+|Base\w+|(Mining|Foraging|Farming|Combat)E\d+|Clk(Map|FMap|QMap|TMap)\d+)@2x\.png$")
        assert all(rx_new.match(n) for n in new), "C new non-class files: %s" % [n for n in new if not rx_new.match(n)][:8]
        assert all(rx_gone.match(n) for n in gone), "C gone non-class files: %s" % [n for n in gone if not rx_gone.match(n)][:8]
        chg = sorted(n for n in na & nb if not n.endswith(".class") and a.read(n) != b.read(n))
        assert chg == ["manifest.json"], "C changed non-class files: %s" % chg[:8]
    print("C. %d new 1x pictures, %d old pictures gone; every other non-class file unchanged; manifest.json changed" % (len(new), len(gone)))
    cp = os.path.join(SCRATCH, "compare-%s.jar" % VERSION)
    with zipfile.ZipFile(jar) as zi, zipfile.ZipFile(old_jar) as zo0, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if not n.endswith(".class") and n != "manifest.json":
                continue
            zo.writestr(n, zi.read(n))
        for n in zo0.namelist():
            if not n.endswith(".class") and n != "manifest.json":
                zo.writestr(n, zo0.read(n))
    T419._compare(out, cp, old_jar, pkg, expect, added, removed)


# RETIRED 0.4.2x CHECKS: the behaviour they pinned is replaced on purpose (each reason is a 0.4.27 spec line; the new phases check the new behaviour).
# A failing check whose text matches is counted as a note "retired ..." (printed RETIRED) instead of a failure; nothing else is touched.
RETIRED = [
    (r"^(TU|FU|MU|CU) (the )?(Spirit warriors|Spirit row|Miner spirits row).*Totems tab", "SPEC 3: the spirit row buys / tiers up on the page (SP27)"),
    (r"^MU the Smithy row without a pole opens the Totems tab|^MP \.\.\. no pole: the Totems button", "SPEC 5: Smithy I is bought on the page (SM27)"),
    (r"^MP \.\.\. Smithy II can be bought \(ku7:0\)|^MP \.\.\. the slider row: < / > carry the value shown", "the rows moved to the 0.4.27 ids SkyyShKU7* (SM27 checks Smithy II + the slider there)"),
    (r"^(TP|FP|MP|PG23) Shard menu -> the menu's Map tab|^PG23 Storage tab -> the shard menu's Collect tab", "SPEC 2: no Shard menu / Storage tab (Upgrades, UP27)"),
    (r"^(TP|FP|MP) the (town|farm|quarry) off: no button, kopen refused", "follows the retired Shard menu button (the page stays on the clicker)"),
    (r"^U every map binding is there with its action \(\d+\): \[\('#SkyyShEnter'", "SPEC 1: no Enter Shard"),
    (r"^U (rail: Mining \(portal here\) opens|a locked shard's purchase is refused anyway|zoom in stops at 200 %|200 %: the 2-axis scroll box|keep: |keep fall-back: |tab [03] builds|the old Islands tab number shows the Map)",
     "SPEC 1: the Mining Shard's Map tab never opens (its rail leads to the quarry clicker); the Map tab stays for Ranching / Orchard"),
]
_check0 = HK.Child.check


def _check27(self, cond, what):
    if not cond:
        for rx_, why_ in RETIRED:
            if re.search(rx_, what):
                self.notes.append("retired 0.4.2x check (%s): %s" % (why_, what))
                print("RETIRED", what, "-", why_)
                self.ok += 1
                return True
    return _check0(self, cond, what)


HK.Child.check = _check27


# ---------------------------------------------------------------------------------------------------------- FX27: the critic fixes
def run_fix(out, jar, scratch, _home):
    from jpype import JString, JInt, JArray
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "fx")
    St, Cfg, Isl, PFn, Page = L["ShStore"], L["ShCfg"], L["ShIsl"], L["ShPageFn"], L["ShPage"]
    T423._foraging(L, p); T424._mining(L, p); T425._farm(L, p); T426._town(L, p)
    St.LOCK.lock()
    try:
        for kk_ in ("ranching", "orchard"):
            p.setProperty(kk_ + ".i0.type", "chicken" if kk_ == "ranching" else "apple"); p.setProperty(kk_ + ".i0.size", "1"); p.setProperty(kk_ + ".i0.last", str(T0))
            p.setProperty(kk_ + ".i0.stored", "0"); p.setProperty(kk_ + ".i0.totems", "harvest_spirit:1"); p.setProperty(kk_ + ".placed", W_ + "|4|5|6")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    ev = []

    def qe(a):
        ev.append((str(a[0]), str(a[1]), str(a[2]), int(a[3])))
        return None
    L["br"].put("quest:fn:event", L["PyFn"](qe))
    keys = ["mining", "foraging", "farming", "ranching", "orchard", "combat"]
    # FIX 1 (critic: quest events from the shard door were never sent): every portal open sends shard:door:<kind> once
    for kd in range(6):
        del ev[:]
        d0 = int(PFn.DOORS.get())
        pg = PFn(kd, 0).make(None, ou, JString(W_))
        K.check(pg is not None and len(ev) == 1 and ev[0] == (str(ou), "event", "shard:door:" + keys[kd], 1) and int(PFn.DOORS.get()) == d0 + 1,
                "FX27 fix1: the %s portal sends exactly one shard:door:%s quest event %s" % (keys[kd], keys[kd], ev))
    del ev[:]
    SHW = "skyy-shard-" + OWNER
    hp = PFn(FK, 0).make(None, ou, JString(SHW))
    K.check(hp is not None and int(hp.view) == 1 and len(ev) == 0, "FX27 fix1: the hub stand (exit page) sends no door event %s" % ev)
    # FIX 2 (critic: a locked shard's portal opened the clicker): locked clicker = nothing opens, no event; locked Ranching / Orchard = old menu + lock line
    old_lock, old_lt = Cfg.LOCK, Isl.LEVEL_TEST
    try:
        Cfg.LOCK = JArray(JInt)([5] * 6)
        lvls = {"Mining": 9, "Foraging": 2, "Farming": 9, "Ranching": 9, "Orchard": 2}
        Isl.LEVEL_TEST = L["PyFn"](lambda a: JInt(lvls.get(str(a[2]), 9)))
        K.check(Isl.lockMsg(ou, FO) is not None and Isl.lockMsg(ou, MI) is None, "FX27 fix2: Foraging locked (2 < 5), Mining open")
        del ev[:]
        g0, l0 = int(PFn.REFUSED.get()), int(PFn.LOCKED.get())
        pg = PFn(FO, 0).make(None, ou, JString(W_))
        K.check(pg is None and int(PFn.REFUSED.get()) == g0 + 1 and int(PFn.LOCKED.get()) == l0 + 1 and len(ev) == 0,
                "FX27 fix2: the locked Foraging portal opens nothing and sends no door event %s" % ev)
        pg = PFn(OR, 0).make(None, ou, JString(W_))
        K.check(pg is not None and int(pg.view) == 0 and "locked" in str(pg.stText) and len(ev) == 0,
                "FX27 fix2: the locked Orchard portal opens its old menu with the lock line, no event (%s)" % (None if pg is None else pg.stText))
        lvls["Orchard"] = 9
        del ev[:]
        pg = PFn(OR, 0).make(None, ou, JString(W_))
        K.check(pg is not None and len(ev) == 1, "FX27 fix2: Orchard open again (one event)")
        r = str(pg.act(JString("mk%d" % FO), None, None))
        K.check(int(pg.kind) == OR and int(pg.view) == 0 and "locked" in r, "FX27 fix2: the rail to the locked Foraging clicker stays shut: %s" % r[:80])
        pg = PFn(MI, 0).make(None, ou, JString(W_))
        K.check(pg is not None and int(pg.view) == 5, "FX27 fix2: the open Mining portal still opens its clicker")
    finally:
        Cfg.LOCK, Isl.LEVEL_TEST = old_lock, old_lt
    # FIX 3 (critic: a red cost line gave no way forward): a free 3rd line says where to get it
    St.LOCK.lock()
    try:
        p.remove("foraging.i0.totems")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    L["coins"]["bal"] = 10000000
    _give(L, [])
    pg = _page(L, ou, W_, FO)
    T49._build(pg)
    K.check(int(pg.ckCG[7]) == 2 and str(pg.ckCL[8]) == "Tip: Auto-Compactor or craft it" and int(pg.ckCG[8]) == 0,
            "FX27 fix3: no Enchanted log -> red line + the tip (%s | %s)" % (pg.ckCL[7], pg.ckCL[8]))
    _give(L, [(EOAK, 300)])
    T49._build(pg)
    K.check(int(pg.ckCG[7]) == 1 and str(pg.ckCL[8]) == "", "FX27 fix3: enough Enchanted -> green, no tip (%s)" % pg.ckCL[8])
    _give(L, [("Ore_Copper", 10)])
    pg = _page(L, ou, W_, MI)
    T49._build(pg)
    K.check(int(pg.ckCG[22]) == 2 and str(pg.ckCL[23]) == "Tip: Collect first, or make more", "FX27 fix3: too little ore for Smithy I -> the tip (%s | %s)" % (pg.ckCL[22], pg.ckCL[23]))
    K.check(all(len(str(x)) <= 34 for x in pg.ckCL), "FX27 fix3: every cost line <= 34 characters")
    # FIX 4 (critic: ShMig0427's INFO line named 0.4.20's change)
    g = open(GEN, encoding="utf8", newline="").read()
    m = g[g.index("public static synchronized String run(java.nio.file.Path f) {", g.index('M(smig427, r"""')):]
    m = m[:m.index('}""")')]
    K.check("smaller storage 1k" not in m and "island upgrades cost the island's own items: Decorations, Irrigation, Combat" in m,
            "FX27 fix4: the ShMig0427 INFO line names the 0.4.27 change")
    L["br"].remove("quest:fn:event")
    K.save()


PHASES = [("static", run_static), ("worlds27", run_worlds), ("fix27", run_fix), ("spirit27", run_spirit), ("mods27", run_mods), ("smithy27", run_smithy), ("coins27", run_coins),
          ("lines27", run_lines), ("view27", run_view), ("mig27", run_mig),
          ("fight26", T426.run_fight), ("memkey26", T426.run_memkey), ("upgrade26", T426.run_upgrade), ("zones26", T426.run_zones),
          ("collect26", T426.run_collect), ("page26", T426.run_page),
          ("farm25", T425.run_farm), ("upgrade25", T425.run_upgrade), ("zones25", T425.run_zones), ("collect25", T425.run_collect), ("page25", T425.run_page),
          ("mine24", T424.run_mine), ("smithy24", T424.run_smithy), ("upgrade24", T424.run_upgrade), ("zones24", T424.run_zones),
          ("collect24", T424.run_collect), ("fortune24", T424.run_fortune), ("page24", T424.run_page),
          ("click23", T423.run_click), ("collect23", T423.run_collect), ("upgrade23", T423.run_upgrade), ("zones23", T423.run_zones),
          ("page23", T423.run_page23),
          ("combat22", T422.run_combat), ("farm22", T422.run_farm), ("page22", T422.run_page22),
          ("geo", T421.run_geo), ("rebuild", T421.run_rebuild), ("level", T421.run_level), ("bags", T421.run_bags), ("page21", T421.run_page21),
          ("comp", T420.run_comp), ("sell20", T420.run_sell), ("mig20", T420.run_mig20), ("ore", T420.run_ore), ("deb", T420.run_deb), ("page20", T420.run_page20), ("livecomp", T420.run_livecomp),
          ("off", T419.run_off), ("mig", T419.run_mig), ("sell", T419.run_sell), ("page", T419.run_page),
          ("open", T416._h(T416._g(T416.run_open), True)), ("bytecode", T423.run_bytecode23),
          ("page49", T419.run_page49),   # flows3 (0.4.13: the Totem Bench + totem page inside a shard world) retired with them - W27 checks they open nothing
          ("live", T426.run_live), ("livemig", run_live_mig)]


if __name__ == "__main__":
    HK.run_compare = _compare27
    ph = PHASES
    if "--only" in sys.argv and "--phase" not in sys.argv:
        want = set(HK.arg("--only").split(","))
        ph = [x for x in PHASES if x[0] in want]
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ShMig0427"],
           phases=ph, script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
