"""Harness for SkyyShards 0.4.34 (the Mining quarry: Silver / Gold everywhere, Precious finds, the zone's stone types - tools/shards_0_4_34_patch.py,
on top of 0.4.33). Build first:
    python tools/shards_0_4_34_patch.py && python SkyyShards/build_skyyshards_0.4.34.py
    python SkyyShards/test_skyyshards_0.4.34.py [--keep] [--only label,label] [--dir <scratch>]

  S34   static  the patch re-runs to identical bytes; header / VERSION / ready line / rollback note; no new class / registerSystem / registerCommand;
                the five Server Setup rows; line endings kept
  R34   rates   EXECUTED seeded CLICK production on every zone's quarry (Lucky 5 + Precious 5, Vein size 10): Silver / Gold / ore / stone counted
                against the tabled per-block chance (ShClk.rareQ), Zone 3 the most Silver, Zone 4 / 5 the least Gold, every block 1 stone,
                the host share ~ click.mine.hostPercent, every zone stone seen, nothing but real ids
  P34   spirits EXECUTED settle on every zone's quarry: Silver / Gold = floor(made x chance) exactly, stones = made (the exact host / zone rotation),
                a second settle carries the fractions (two settles = one), the storage room (good finds first, nothing over the limit), the Mining XP
                owed at once, the spirit rows at 0 % = nothing, Smithy = bars
  U34   upgrade the Precious finds row on the page (labels, have / need lines, the ku9 button), buy (exact cost = Lucky's at that level), a double click
                buys once, not enough coins / items = nothing paid, a stale page / another profile = nothing, the highest level, the chance after
  C34   carry   the Auto-Compactor compacts stones + Silver / Gold bars in the quarry storage (usedOf unchanged); Collect all and Shard Link give the
                same items with the same credit (an Enchanted stone = 100 of its base, an Enchanted ingot = 100 of its ore) and XP; a grid cell
  O34   others  Foraging / Farming / Ranching / Orchard / Combat settle + clicks are byte-identical with the new paths on or off (MQ34_OFF_TEST); the
                0.4.30 fold knows prec / qsf (no unknown-key refusal; prec = the higher)
  then 0.4.33's phases (minus static / livemig33) on THIS jar with MQ34_OFF_TEST on (= 0.4.33's quarry: every earlier check), A verify, C compare,
  AA audit, livemig34 = the start-twice on a scratch copy of the live data with the new paths ON.
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.34"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "mzone2", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.33.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.33.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_34_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

_T33 = open(os.path.join(HERE, "test_skyyshards_0.4.33.py"), encoding="utf8").read()
assert _T33.count('VERSION = "0.4.33"\n') == 1, "the 0.4.33 harness changed"
_T33 = _T33.replace('VERSION = "0.4.33"\n', 'VERSION = "%s"\n' % VERSION)
# the 0.4.30 page check counted the quarry's rows (9); 0.4.34 adds the 10th (Precious finds) - the only earlier number this round changes
_argv = list(sys.argv)
T433 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_33", loader=None))
T433.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.33.py")
exec(compile(_T33, T433.__file__, "exec"), T433.__dict__)
sys.argv[:] = _argv
T432 = T433.T432
T431 = T432.T431
T430 = T431.T430
T428, T427, T425, T424, T423 = T431.T428, T431.T427, T431.T425, T431.T424, T431.T423
T49, T410, T411 = T431.T49, T431.T410, T431.T411
for _m in (T433, T432, T431, T430, T428):
    _m.JAR = JAR
    _m.SCRATCH = SCRATCH
OWNER = T428.OWNER
T0 = T428.T0
MI, FO, FK, RA, OR, CK = 0, 1, 2, 3, 4, 5
NEW = ("static", "rates34", "spirits34", "upgrade34", "carry34", "others34", "livemig34")
PHASE = HK.arg("--phase")
LEGACY = PHASE is not None and PHASE not in NEW and PHASE not in ("mkfake", "verify", "compare", "audit")

# the earlier phases run on 0.4.33's quarry exactly (ShCfg.MQ34_OFF_TEST: host stone only, no spirit stone / finds, no Precious, no storage compaction)
_jvm0 = HK.jvm


def _jvm(cp, verify=True):
    _jvm0(cp, verify)
    if LEGACY:
        try:
            from jpype import JClass
            JClass(PKG + "ShCfg").MQ34_OFF_TEST = True
        except Exception:
            pass


HK.jvm = _jvm

PICK = "Tool_Pickaxe_Onyxium"
ZONE_STONES = {1: ["Rock_Basalt_Cobble", "Rock_Marble_Cobble"],   # fixer: no Rock_Chalk (no collection)
               2: ["Rock_Sandstone_White_Cobble", "Rock_Sandstone_Red_Cobble", "Rock_Volcanic_Cobble"],
               3: ["Rock_Slate_Cobble", "Rock_Basalt_Cobble", "Rock_Stone_Cobble"],
               4: ["Rock_Basalt_Cobble", "Rock_Slate_Cobble", "Rock_Quartzite_Cobble"],
               5: ["Rock_Volcanic_Cobble", "Rock_Magma_Cooled_Cobble", "Rock_Basalt_Cobble"]}
DC = {"Rock_Stone_Cobble": "Skyy_Ench_Cobblestone", "Rock_Basalt_Cobble": "Skyy_Ench_Basalt", "Rock_Marble_Cobble": "Skyy_Ench_Marble",
      "Rock_Sandstone_Cobble": "Skyy_Ench_Sandstone", "Rock_Shale_Cobble": "Skyy_Ench_Shale", "Rock_Slate_Cobble": "Skyy_Ench_Slate",
      "Rock_Volcanic_Cobble": "Skyy_Ench_Volcanic", "Rock_Quartzite_Cobble": "Skyy_Ench_Quartzite", "Ingredient_Bar_Silver": "Skyy_Ench_Silver",
      "Ingredient_Bar_Gold": "Skyy_Ench_Gold"}
COLL_ALIAS = {"Rock_Magma_Cooled_Cobble": "Rock_Magma_Cooled"}   # fixer: the credit id of a quarry stone (SkyyCollections tracks the block)


def coll_ids():
    """every item id a SkyyCollections 0.2.36 collection tracks (its add(...) lines) - the real coll:fn:add refuses any other id"""
    src = open(os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.36.py"), encoding="utf8").read()
    ids = set()
    for m_ in re.finditer(r'^add\("[^"]+", "[A-Za-z]+", "[A-Z]", "[^"]*", \[([^\]]*)\]', src, re.M):
        ids |= set(re.findall(r'"([A-Za-z0-9_]+)"', m_.group(1)))
    # the metal ores (a loop of add(metal, ..., ["Ore_" + metal]) + the zone metals' Ore_<M>_SkyWynn)
    ids |= set("Ore_" + m_ for m_ in ("Copper", "Iron", "Silver", "Gold", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"))
    ids |= set(re.findall(r"Ore_[A-Za-z]+_SkyWynn", open(os.path.join(ROOT, "SkyyShards", "build_skyyshards_0.4.34.py"), encoding="utf8").read()))
    return ids


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.34 - build script') and 'VERSION = "0.4.34"\n' in g, "S34 header + VERSION")
    for w in ("registerSystem(", "registerCommand(", 'mk("'):
        K.eq(g.count(w), o.count(w), "S34 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.34: the Mining quarry" in g, "S34 the ready line names the round")
    K.check("ROLLBACK 0.4.34 -> 0.4.33 alone" in g and "SAVED DATA: mining.i<n>.prec" in g and "NUMBERS (new" in g, "S34 the rollback / saved-data / numbers notes")
    for key in ("click.mine.precPermille", "click.mine.precMax", "click.mine.hostPercent", "click.mine.spiritStonePercent", "click.mine.spiritRarePercent"):
        K.check(('("%s", ' % key) in g and ('p.getProperty(\\"%s\\")' % key) in g, "S34 Server Setup row + load line: %s" % key)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S34 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S34 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S34 jar newer than the script, the script newer than the patch")
    z = zipfile.ZipFile(jar)
    zo = zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(set(z.namelist()) ^ set(zo.namelist())), [], "S34 the same jar entries as 0.4.33 (no new class, no picture)")
    # fixer: every quarry stone (each zone's host cobbles + other stones) is credited by a real SkyyCollections collection (after the alias)
    ci = coll_ids()
    K.check(len(ci) > 50 and "Rock_Stone_Cobble" in ci and "Rock_Magma_Cooled" in ci and "Rock_Chalk" not in ci, "S34 SkyyCollections 0.2.36 tracked ids read (%d)" % len(ci))
    zs = re.search(r"^QZ_EXTRA = (\[\[.*?\]\])\r?\n", g, re.M | re.S)
    hosts = re.search(r"^QZ_HOSTS = (\[[^\]]*\])", g, re.M)
    allst = set(re.findall(r'"([A-Za-z0-9_]+)"', zs.group(1) if zs else "")) | set(eval(hosts.group(1)) if hosts else [])
    K.check(len(allst) >= 10 and "Rock_Chalk" not in allst, "S34 the quarry stones read from the build (%d), no Rock_Chalk" % len(allst))
    K.eq(sorted(s_ for s_ in allst if COLL_ALIAS.get(s_, s_) not in ci), [], "S34 every quarry stone has a SkyyCollections collection (no credit waiting forever)")
    K.save()


# ---------------------------------------------------------------------------------------------------- helpers
def _env(scratch, K, name):
    from jpype import JClass
    L, ou, W_, p, lv, got = T431._env(scratch, K, name)
    for k_ in ("Ranching", "Orchard", "Mining", "Foraging", "Farming"):
        lv[k_] = 100
    L["ShLink"] = JClass(PKG + "ShLink")
    L["ShLink"].PAGE_MS = 0
    L["ShLink"].FN_TEST = None
    ids = set(DC) | set(DC.values()) | set(s for v in ZONE_STONES.values() for s in v) | {"Rock_Shale_Cobble", "Rock_Sandstone_Cobble", "Rock_Magma_Cooled_Cobble",
                                                                                         "Ore_Silver", "Ore_Gold", PICK}
    T411.T48.add_items([(i, 100) for i in sorted(ids)])
    L["ShCfg"].MQ34_OFF_TEST = False
    return L, ou, W_, p, lv, got


def _keys(L):
    Isl = L["ShIsl"]
    L0 = int(Isl.LAD0[MI])
    return [str(Isl.KEY[L0 + i]) for i in range(int(Isl.LADN[MI]))]


def _quarry(L, p, z, sz=3, extra=None, totems=True, storage="5"):
    """one Mining quarry in zone z at slot 0 (the zone's first ore), nothing else Mining"""
    keys = _keys(L)
    ty = keys[2 * (z - 1)]

    def f():
        for k_ in list(p.stringPropertyNames()):
            if str(k_).startswith("mining."):
                p.remove(k_)
        p.setProperty("mining.i0.type", ty); p.setProperty("mining.i0.size", str(sz)); p.setProperty("mining.i0.last", str(T0))
        p.setProperty("mining.i0.stored", "0")
        if totems:
            p.setProperty("mining.i0.totems", "quarry_spirit:3:::0:mq%04d" % z)
        p.setProperty("mining.auto", "1"); p.setProperty("mining.paused", "0"); p.setProperty("mining.storage", storage)
        p.setProperty("mining.placed", L["W_"] + "|1|2|3")
        for k_, v_ in (extra or {}).items():
            p.setProperty(k_, str(v_))
    T430._set(L, p, f)
    return ty


def _drops(p):
    return T425._drops(p, 0, "mining")


def _locked(L, fn):
    St = L["ShStore"]
    St.LOCK.lock()
    try:
        return fn()
    finally:
        St.LOCK.unlock()


def host_cnt(x, hp):
    return (x // 100) * hp + min(x % 100, hp)


def ext_cnt(g, e, j):
    return g // e + (1 if g % e > j else 0)


# ---------------------------------------------------------------------------------------------------- R34: the click rates per zone
def run_rates(out, jar, scratch, _home):
    from jpype import JString, JClass, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "r34")
    Ck, Core, Cfg, Isl, M = L["ShClk"], L["ShCore"], L["ShCfg"], L["ShIsl"], L["ShMath"]
    Cfg.CK_CPS = 1000
    table = []
    nodes = 160
    res = {}
    for z in range(1, 6):
        ty = _quarry(L, p, z, totems=False, extra={"mining.i0.nsize": 10, "mining.i0.luck": 5, "mining.i0.prec": 5, "mining.i0.amt": 5})
        t = int(Isl.ofKey(MI, JString(ty)))
        host = str(Ck.Q_COB[t - int(Isl.LAD0[MI])])
        bl = int(Ck.blocksAt(10))
        tally, ok_nodes, msgs = {}, 0, []
        for n in range(nodes):
            Core.NOW_TEST = T0 + z * 10 ** 10 + n * 10 ** 6   # the node memory is per quarry slot: a later clock each zone
            Ck.RND_TEST = JClass("java.util.Random")(JLong(9000 + 31 * z + n))
            Ck.RND2_TEST = JClass("java.util.Random")(JLong(7000 + 17 * z + n))
            s = ""
            for _ in range(60):
                s = str(Ck.chop(ou, JString(OWNER), MI, 0, 0, JString(PICK))[0])
                if s.startswith("+") or s.startswith("-"):
                    break
            if s.startswith("+Mined"):
                ok_nodes += 1
            if len(msgs) < 2:
                msgs.append(s)
            for i, q in _drops(p).items():
                tally[i] = tally.get(i, 0) + q
            T430._set(L, p, lambda: p.remove("mining.i0.drops"))
        Ck.RND_TEST = None
        Ck.RND2_TEST = None
        blocks = ok_nodes * bl
        ps, pg = float(Ck.rareQ(5, 5, z, False)), float(Ck.rareQ(5, 5, z, True))
        sil, gol = tally.get("Ore_Silver", 0), tally.get("Ore_Gold", 0)
        stones = dict((i, q) for i, q in tally.items() if i.startswith("Rock_"))
        res[z] = dict(sil=sil, gol=gol, blocks=blocks, stones=stones, ps=ps, pg=pg)
        table.append("Zone %d: %d nodes x %d blocks = %d | Silver %d (want ~%.0f = %.1f %%) | Gold %d (want ~%.0f = %.1f %%) | stones %s"
                     % (z, ok_nodes, bl, blocks, sil, blocks * ps, ps * 100, gol, blocks * pg, pg * 100, stones))
        K.check(ok_nodes == nodes, "R34 zone %d: every node mined (%d / %d): %s" % (z, ok_nodes, nodes, msgs[:1]))
        K.eq(sum(stones.values()), blocks, "R34 zone %d: exactly one stone a block" % z)
        K.check(set(stones) <= {host} | set(ZONE_STONES[z]) and set(stones) == {host} | set(ZONE_STONES[z]),
                "R34 zone %d: the stones = the host %s + the zone's %s (%s)" % (z, host, ZONE_STONES[z], sorted(stones)))
        hs = stones.get(host, 0) - (0 if host not in ZONE_STONES[z] else 0)
        if host not in ZONE_STONES[z] and blocks:
            K.check(abs(hs / float(blocks) - 0.5) < 0.05, "R34 zone %d: the host share ~ 50 %% (%.3f)" % (z, hs / float(blocks)))
        for nm, got_, want in (("Silver", sil, blocks * ps), ("Gold", gol, blocks * pg)):
            sd = math.sqrt(max(want * (1 - want / max(blocks, 1)), 1.0))
            K.check(abs(got_ - want) <= 4 * sd + 2, "R34 zone %d: %s %d ~ %.1f (4 sd = %.1f)" % (z, nm, got_, want, 4 * sd))
        K.check(all(str(i) in L["ITEMS_ALL"] for i in tally) if "ITEMS_ALL" in L else True, "R34 zone %d: real ids only" % z)
        K.check(all(i.startswith(("Rock_", "Ore_")) for i in tally), "R34 zone %d: only stone / ore ids in storage: %s" % (z, sorted(tally)))
    K.check(res[3]["sil"] > max(res[z]["sil"] for z in (1, 2, 4, 5)), "R34 Zone 3 has the most Silver: %s" % [res[z]["sil"] for z in range(1, 6)])
    K.check(res[3]["gol"] > max(res[z]["gol"] for z in (1, 2, 4, 5)) and max(res[4]["gol"], res[5]["gol"]) < min(res[1]["gol"], res[2]["gol"]),
            "R34 Zone 3 the most Gold, zones 4 / 5 the least: %s" % [res[z]["gol"] for z in range(1, 6)])
    # the chance table (Lv 0 / Precious 5 / Lucky 5 + Precious 5)
    rt = []
    for lk, pr in ((0, 0), (0, 5), (5, 5)):
        rt.append("L%d P%d: Silver %s | Gold %s" % (lk, pr, " ".join("%.2f" % (float(Ck.rareQ(lk, pr, z, False)) * 100) for z in range(1, 6)),
                                                   " ".join("%.2f" % (float(Ck.rareQ(lk, pr, z, True)) * 100) for z in range(1, 6))))
    K.eq([round(float(Ck.rareQ(0, 0, z, False)) * 100, 3) for z in range(1, 6)], [1.0, 1.0, 2.0, 1.0, 0.5], "R34 Silver Lv 0 by zone (%)")
    K.eq([round(float(Ck.rareQ(5, 5, z, True)) * 100, 3) for z in range(1, 6)], [8.8, 8.8, 16.5, 3.3, 3.3], "R34 Gold Lucky 5 + Precious 5 by zone (%)")
    K.eq([round(float(Ck.rareQ(2, 0, z, False)), 6) for z in range(1, 6)], [round(float(Ck.rareP(2, z, False)), 6) for z in range(1, 6)], "R34 rareQ(Precious 0) = 0.4.33's rareP")
    print("R34 rate table (per block, %):")
    for r in rt + table:
        print("R34  " + r)
    K.notes += rt + table
    K.save()


# ---------------------------------------------------------------------------------------------------- P34: the spirits (settle)
def run_spirits(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "p34")
    Ck, Core, Cfg, Isl, M, St = L["ShClk"], L["ShCore"], L["ShCfg"], L["ShIsl"], L["ShMath"], L["ShStore"]
    per, pct = int(Cfg.xpOf(MI)), int(Cfg.XP_PCT)
    for z in range(1, 6):
        ty = _quarry(L, p, z, extra={"mining.i0.luck": 3, "mining.i0.prec": 2})
        t = int(Isl.ofKey(MI, JString(ty)))
        host = str(Ck.Q_COB[t - int(Isl.LAD0[MI])])
        ps, pg = float(Ck.rareQ(3, 2, z, False)), float(Ck.rareQ(3, 2, z, True))
        x0 = int(St.lng(p, JString("owed.xp.Mining"), 0))
        made1 = int(_locked(L, lambda: M.settle(MI, p, 0, T0 + 3 * 3600000)))
        d1 = _drops(p)
        made2 = int(_locked(L, lambda: M.settle(MI, p, 0, T0 + 7 * 3600000)))
        d2 = _drops(p)
        made = made1 + made2
        K.check(made1 > 50 and made2 > 50, "P34 zone %d: the spirits made %d + %d ore" % (z, made1, made2))
        sil, gol = d2.get("Ore_Silver", 0), d2.get("Ore_Gold", 0)
        K.eq(d1.get("Ore_Silver", 0), int(math.floor(made1 * ps + 1e-9)), "P34 zone %d: 1st settle Silver = floor(made x %.4f)" % (z, ps))
        K.eq(sil, int(math.floor(made * ps + 1e-9)), "P34 zone %d: two settles = one (Silver, the fraction carried)" % z)
        K.eq(gol, int(math.floor(made * pg + 1e-9)), "P34 zone %d: two settles = one (Gold)" % z)
        e = len(ZONE_STONES[z])
        want = {}
        want[host] = host_cnt(made, 50)
        g = made - host_cnt(made, 50)
        for j, s in enumerate(ZONE_STONES[z]):
            want[s] = want.get(s, 0) + ext_cnt(g, e, j)
        st = dict((i, q) for i, q in d2.items() if i.startswith("Rock_"))
        K.eq(st, dict((i, q) for i, q in want.items() if q), "P34 zone %d: the stones = made (%d), host 50 %% + the zone's in turn" % (z, made))
        x1 = int(St.lng(p, JString("owed.xp.Mining"), 0))
        K.eq(x1 - x0, ((sil + gol) * per * pct) // 100, "P34 zone %d: Silver + Gold owe their Mining XP at once (%d x %d x %d %%)" % (z, sil + gol, per, pct))
        K.check(str(p.getProperty("mining.i0.qsf") or "").count(";") == 3, "P34 zone %d: the running fractions saved (%s)" % (z, p.getProperty("mining.i0.qsf")))
    # the storage room: a tiny limit - the good finds first, never over the limit
    _quarry(L, p, 3, extra={"mining.i0.luck": 5, "mining.i0.prec": 5}, storage="0")
    lim = int(_locked(L, lambda: M.limOf(MI, p, 0)))
    _locked(L, lambda: M.settle(MI, p, 0, T0 + 48 * 3600000))
    use = int(_locked(L, lambda: M.usedOf(MI, p, 0)))
    K.check(use <= lim, "P34 storage: used %d <= limit %d after a long settle" % (use, lim))
    d = _drops(p)
    K.check(d.get("Ore_Silver", 0) > 0 and d.get("Ore_Gold", 0) > 0, "P34 ... Silver / Gold got in (%s)" % d)
    # the rows at 0 %: nothing extra; Smithy: bars
    Cfg.MQ_SP_STONE = 0
    Cfg.MQ_SP_RARE = 0
    _quarry(L, p, 1)
    _locked(L, lambda: M.settle(MI, p, 0, T0 + 3 * 3600000))
    K.eq(_drops(p), {}, "P34 spiritStonePercent / spiritRarePercent 0: no stone, no finds")
    Cfg.MQ_SP_STONE = 100
    Cfg.MQ_SP_RARE = 100
    _quarry(L, p, 3, extra={"mining.i0.luck": 5, "mining.i0.prec": 5})
    T430._set(L, p, lambda: p.setProperty("mining.i0.totems", "quarry_spirit:3:::0:mq0003,autosmelt_pole:1:::1:mq0004"))
    _locked(L, lambda: M.settle(MI, p, 0, T0 + 3 * 3600000))
    d = _drops(p)
    K.check(d.get("Ingredient_Bar_Silver", 0) > 0 and "Ore_Silver" not in d and d.get("Ingredient_Bar_Gold", 0) > 0, "P34 the Smithy smelts the spirits' Silver / Gold: %s" % d)
    # a non-quarry (2nd Mining island of a zone, before the fold) adds nothing
    K.check(int(M.quarryExtra(FO, p, 0, 100, 1000)) == 0, "P34 another kind: nothing")
    Cfg.MQ34_OFF_TEST = True
    _quarry(L, p, 1)
    _locked(L, lambda: M.settle(MI, p, 0, T0 + 3 * 3600000))
    K.eq(_drops(p), {}, "P34 MQ34_OFF_TEST: 0.4.33's spirits (no extras)")
    K.check(p.getProperty("mining.i0.qsf") is None, "P34 ... no qsf key written")
    Cfg.MQ34_OFF_TEST = False
    K.save()


# ---------------------------------------------------------------------------------------------------- U34: the Precious finds row
def run_upgrade(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "u34")
    Ck, Core, Cfg, Isl, M, St, Cmb = L["ShClk"], L["ShCore"], L["ShCfg"], L["ShIsl"], L["ShMath"], L["ShStore"], L["ShCombat"]
    Ck.HAND_TEST = PICK
    ty = _quarry(L, p, 3, sz=2, totems=False, extra={"mining.i0.luck": 2})
    t = int(Isl.ofKey(MI, JString(ty)))
    cv = float(Cfg.curve(Isl.band(Isl.TIER[t])))

    def cost(lvl):
        c = int(Isl.coins(Isl.subH(2, lvl), cv))
        m = Isl.mats(MI, t, Cmb.subMat(MI, 0), 1, lvl)
        return c, dict(zip([str(x) for x in m[0]], [int(x) for x in m[1]]))
    rows = []
    for lvl in range(1, 6):
        c, m = cost(lvl)
        rows.append("Precious %d (Zone 3, Medium): %s coins + %s" % (lvl, "{:,}".format(c), " + ".join("%d %s" % (q, i) for i, q in sorted(m.items()))))
        lc = int(Isl.coins(Isl.subH(2, lvl), cv))
        lm = Isl.mats(MI, t, Cmb.subMat(MI, 0), 1, lvl)
        K.check(lc == c and [str(x) for x in lm[0]] == list(m), "U34 Precious %d costs what Lucky %d costs" % (lvl, lvl))
    print("U34 cost table:")
    for r in rows:
        print("U34  " + r)
    K.notes += rows
    c1, m1 = cost(1)
    cs = T427._give(L, [(i, q) for i, q in m1.items()] + [(PICK, 1)])
    cnt = lambda i: int(L["count"](cs, i))
    L["coins"]["bal"] = 10 ** 12
    pg = T427._page(L, ou, W_, MI)
    bd = T49._build(pg)
    K.eq(len(pg.ckUpL), 10, "U34 the quarry page has 10 rows")
    K.check(str(pg.ckUpL[9]) == "Lv 0 / 5" and str(pg.ckUpE[9]) == "Silver 6 -> 8 %, Gold 4.5 -> 6 %" and bool(pg.ckUpOk[9]) and int(pg.ckUpSeen[9]) == 0,
            "U34 row 9: Lv 0 / 5, Silver 6 -> 8 %%, Gold 4.5 -> 6 %% (Zone 3, Lucky 2 counted): %s / %s" % (pg.ckUpL[9], pg.ckUpE[9]))
    K.check(str(pg.ckUpE[6]).find("Silver 6 -> 8 %") >= 0, "U34 the Lucky row before Precious: %s" % pg.ckUpE[6])
    lines = [str(pg.ckCL[27 + j]) for j in range(3)]
    K.check(lines[0].endswith("/ {:,} coins".format(c1)) and all(int(pg.ckCG[27 + j]) == 1 for j in range(3) if lines[j]), "U34 ... have / need lines, green: %s" % lines)
    K.check('"ku9:0"' in bd["datas"].get("#SkyyShKU9X", ""), "U34 ... the Upgrade button carries the level shown (ku9:0)")
    r_ = T410.full(pg)
    K.check(not r_["miss"] and not r_["unbound"], "U34 the page walks clean %s %s" % (r_["miss"][:2], r_["unbound"][:2]))
    # not enough coins
    L["coins"]["bal"] = c1 - 1
    r = T427._ev(pg, "ku9:0")
    K.check(p.getProperty("mining.i0.prec") is None and L["coins"]["bal"] == c1 - 1 and all(cnt(i) == q for i, q in m1.items()), "U34 one coin short: nothing paid (%s)" % r[:80])
    L["coins"]["bal"] = 10 ** 12
    # not enough items
    it0 = sorted(m1)[0]
    cs = T427._give(L, [(i, q - (1 if i == it0 else 0)) for i, q in m1.items()])
    r = T427._ev(pg, "ku9:0")
    K.check(p.getProperty("mining.i0.prec") is None and L["coins"]["bal"] == 10 ** 12 and int(L["count"](cs, it0)) == m1[it0] - 1, "U34 one %s short: nothing paid (%s)" % (it0, r[:80]))
    # a stale page / another profile
    cs = T427._give(L, [(i, q) for i, q in m1.items()])
    k0 = pg.key
    pg.key = "00000000-0000-0000-0000-000000000000-p9"
    r = str(pg.act("ku9:0", None, None))
    K.check(r.startswith("=The page is up to date") and p.getProperty("mining.i0.prec") is None, "U34 another profile's page: nothing (%s)" % r[:70])
    pg.key = k0
    s0 = pg.ckSlot
    pg.ckSlot = 5
    r = T427._ev(pg, "ku9:0")
    K.check(p.getProperty("mining.i0.prec") is None and L["coins"]["bal"] == 10 ** 12, "U34 a stale quarry slot: nothing (%s)" % r[:70])
    pg.ckSlot = s0
    # bought
    T49._build(pg)
    b0 = L["coins"]["bal"]
    r = T427._ev(pg, "ku9:0")
    K.check(str(p.getProperty("mining.i0.prec")) == "1" and b0 - L["coins"]["bal"] == c1 and all(cnt(i) == 0 for i in m1), "U34 Precious 1 bought: exactly %d coins + %s (%s)" % (c1, m1, r[:110]))
    K.check("Silver 8 % a block, Gold 6 %" in r, "U34 ... the message gives the new chance: %s" % r)
    disk = open(os.path.join(str(St.DIR), OWNER + ".properties"), encoding="latin-1").read()
    K.check("mining.i0.prec=1" in disk, "U34 ... saved at once")
    # a double click (the page still shows level 0)
    c2, m2 = cost(2)
    cs = T427._give(L, [(i, q) for i, q in m2.items()])
    b1 = L["coins"]["bal"]
    r = T427._ev(pg, "ku9:0")
    K.check(str(p.getProperty("mining.i0.prec")) == "1" and L["coins"]["bal"] == b1 and all(cnt(i) == q for i, q in m2.items()), "U34 a double click buys once (%s)" % r[:70])
    T49._build(pg)
    K.check(str(pg.ckUpL[9]) == "Lv 1 / 5" and int(pg.ckUpSeen[9]) == 1, "U34 ... the row now Lv 1 / 5")
    K.check(str(pg.ckUpE[6]).find("Silver 8 -> 10 %") >= 0, "U34 the Lucky row shows the chance with Precious 1: %s" % pg.ckUpE[6])
    # up to the top
    for lvl in range(2, 6):
        c, m = cost(lvl)
        cs = T427._give(L, [(i, q) for i, q in m.items()])
        T49._build(pg)
        r = T427._ev(pg, "ku9:%d" % (lvl - 1))
        K.eq(str(p.getProperty("mining.i0.prec")), str(lvl), "U34 Precious %d bought (%s)" % (lvl, r[:60]))
    T49._build(pg)
    K.check(str(pg.ckUpL[9]) == "Lv 5 / 5" and not bool(pg.ckUpOk[9]) and str(pg.ckUpE[9]) == "Silver 16 %, Gold 12 %", "U34 the top: no button, %s" % pg.ckUpE[9])
    r = str(Ck.buyPrec(ou, JString(OWNER), MI, 0, 5, cs))
    K.check(r.startswith("=Precious finds is at its highest"), "U34 ... a buy at the top: %s" % r)
    K.check(abs(float(Ck.rareQ(2, 5, 3, False)) - 0.16) < 1e-9, "U34 Zone 3 Silver with Lucky 2 + Precious 5 = 16 %")
    # the 0.4.30 page check with 10 rows: a Zone 1 quarry with Copper only - Ore nodes as before, the caption says where Iron is added
    _quarry(L, p, 1, sz=1, totems=False, extra={"mining.i0.amt": 1})
    pg1 = T427._page(L, ou, W_, MI)
    T49._build(pg1)
    K.check(len(pg1.ckUpL) == 10 and str(pg1.ckUpE[1]).startswith("Nodes ") and "Add Iron on the Ores row." in str(pg1.ckCap) and len(str(pg1.ckCap)) <= 125,
            "U34 (was MP30's 9-row check) 10 rows, Ore nodes as before, the caption says where Iron is added: %s" % pg1.ckCap)
    # another kind
    K.check(str(Ck.buyPrec(ou, JString(OWNER), FO, 0, 0, cs)).startswith("-Precious finds is a Mining"), "U34 a Foraging island: refused")
    # Precious max lowered: the level clamps (no refund, nothing lost)
    T430._set(L, p, lambda: p.setProperty("mining.i0.prec", "5"))
    Cfg.MQ_PREC_MAX = 3
    K.eq(int(Ck.prec(p, MI, 0)), 3, "U34 click.mine.precMax 3: level 5 counts as 3 (the saved 5 kept)")
    K.eq(str(p.getProperty("mining.i0.prec")), "5", "U34 ... the file keeps 5")
    Cfg.MQ_PREC_MAX = 5
    K.save()


# ---------------------------------------------------------------------------------------------------- C34: Auto-Compactor, Collect, Shard Link
def run_carry(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "c34")
    Ck, Core, Cfg, Isl, M, St = L["ShClk"], L["ShCore"], L["ShCfg"], L["ShIsl"], L["ShMath"], L["ShStore"]
    per, pct = int(Cfg.xpOf(MI)), int(Cfg.XP_PCT)
    ci = coll_ids()
    for variant in ("cmp", "nosm", "plain"):   # fixer: + "nosm" = an Auto-Compactor with the Smithy off (the island does not compress)
        _quarry(L, p, 1, extra={"mining.compactor": 0 if variant == "plain" else 1, "mining.i0.luck": 5, "mining.i0.prec": 5,
                                "mining.i0.drops": "Rock_Stone_Cobble:60,Rock_Sandstone_White_Cobble:5,Ingredient_Bar_Silver:95"})
        if variant != "nosm":
            T430._set(L, p, lambda: p.setProperty("mining.i0.totems", "quarry_spirit:1:::0:mq0001,autosmelt_pole:1:::1:mq0002"))
        else:
            T430._set(L, p, lambda: p.setProperty("mining.i0.totems", "quarry_spirit:1:::0:mq0001"))
        made = int(_locked(L, lambda: M.settle(MI, p, 0, T0 + 2 * 3600000)))
        d = _drops(p)
        u1 = int(_locked(L, lambda: M.usedOf(MI, p, 0)))
        base = {}
        for i, q in d.items():
            b = [k_ for k_, v_ in DC.items() if v_ == i]
            if b:
                base[b[0]] = base.get(b[0], 0) + 100 * q
            else:
                base[i] = base.get(i, 0) + q
        stock = int(M.stored(MI, p, 0)) + 100 * int(M.comp(MI, p, 0))
        if variant == "cmp":
            K.check(d.get("Skyy_Ench_Cobblestone", 0) >= 1 and d.get("Rock_Stone_Cobble", 0) < 100 and d.get("Rock_Sandstone_White_Cobble", 0) >= 5 and not any("White" in i for i in d if i.startswith("Skyy_")),
                    "C34 Auto-Compactor: Cobblestone -> Enchanted Cobblestone, < 100 left; White Sandstone (no Enchanted form) stays: %s" % d)
            K.check(all(d.get(b_, 0) < 100 for b_ in DC), "C34 ... every stone / bar with an Enchanted form under 100: %s" % d)
            K.check(d.get("Skyy_Ench_Silver", 0) >= 1 or base.get("Ingredient_Bar_Silver", 0) < 100, "C34 ... Silver bars -> Enchanted Silver Ingot: %s" % d)
            K.eq(u1, sum(base.values()) + stock, "C34 usedOf counts an Enchanted stone / ingot as 100 (no free room)")
        elif variant == "nosm":
            K.check(not bool(_locked(L, lambda: M.compOn(MI, p, 0))), "C34 nosm: the Smithy off - the island does not compress (limit = the plain cap)")
            K.check(d.get("Skyy_Ench_Cobblestone", 0) >= 1 and d.get("Rock_Stone_Cobble", 0) < 100, "C34 nosm: the Auto-Compactor still compacts the stones: %s" % d)
            K.eq(u1, sum(base.values()) + stock, "C34 nosm: usedOf counts an Enchanted stone / ingot as 100 against the plain cap (no free room)")
            # fill it: hours of spirits never pass the plain cap in base items
            snapf = T433._props(p)
            lim0 = int(_locked(L, lambda: M.limOf(MI, p, 0)))
            T430._set(L, p, lambda: p.setProperty("mining.i0.stored", str(lim0 - int(_locked(L, lambda: M.usedOf(MI, p, 0))) - 1500 + int(M.stored(MI, p, 0)))))
            _locked(L, lambda: M.settle(MI, p, 0, T0 + 200 * 3600000))
            df = _drops(p)
            truef = sum((100 if i in DC.values() else 1) * q for i, q in df.items()) + int(M.stored(MI, p, 0)) + 100 * int(M.comp(MI, p, 0))
            lim = int(_locked(L, lambda: M.limOf(MI, p, 0)))
            K.check(any(i.startswith("Skyy_Ench_") for i in df) and truef <= lim and truef >= lim - 200 and int(_locked(L, lambda: M.usedOf(MI, p, 0))) == truef,
                    "C34 nosm: a full quarry stops at its plain cap in base items (%d of %d; %s)" % (truef, lim, df))
            T433._restore(L, p, snapf)
        else:
            K.check(not any(i.startswith("Skyy_Ench_") for i in d), "C34 no Auto-Compactor: nothing compacted: %s" % d)
        snap = T433._props(p)
        r, inv, coll_c, xp_c = T433._collect(L, ou, MI, got)
        K.check(r.startswith("+Collected"), "C34 %s: Collect all ran: %s" % (variant, r[:120]))
        for i, q in d.items():
            K.eq(inv.get(i, 0), q, "C34 %s: Collect gave every %s" % (variant, i))
        ore = {"Ingredient_Bar_Silver": "Ore_Silver", "Ingredient_Bar_Gold": "Ore_Gold"}
        want = {}
        for b_, q in base.items():
            cid = ore.get(b_, b_)
            want[cid] = want.get(cid, 0) + q
        K.eq(dict((i, coll_c.get(i, 0)) for i in want), want, "C34 %s: the collection credit (an Enchanted stone / ingot = 100 of its base, a bar = its ore)" % variant)
        K.eq(sorted(i for i in coll_c if i not in ci), [], "C34 %s: every id credited is one a real SkyyCollections collection tracks" % variant)
        T433._restore(L, p, snap)
        sk = T433.Sacks(OWNER)
        n, pool, coll_l, xp_l = T433._link(L, ou, MI, got, sk)
        K.check(n > 0, "C34 %s: Shard Link moved %d" % (variant, n))
        K.eq(coll_l, coll_c, "C34 %s: Shard Link credit = Collect's" % variant)
        K.eq(xp_l, xp_c, "C34 %s: Shard Link XP = Collect's" % variant)
        K.eq(dict((i, q) for i, q in pool.items() if i in d), dict((i, q) for i, q in inv.items() if i in d), "C34 %s: Shard Link items = Collect's (the storage part)" % variant)
        T433._restore(L, p, snap)
        # a grid cell = one kind
        cs = L["inv"](27, 27, 9)
        one = "Skyy_Ench_Cobblestone" if variant != "plain" else "Rock_Basalt_Cobble"
        c0 = dict(got["coll"])
        r = str(Core.collect0(ou, JString(OWNER), MI, 0, cs, JString(one)))
        K.check(int(L["count"](cs, one)) == d.get(one, 0) and d.get(one, 0) > 0, "C34 %s: a grid cell collects %s only (%s)" % (variant, one, r[:80]))
        if variant != "plain":
            K.eq(got["coll"].get("Rock_Stone_Cobble", 0) - c0.get("Rock_Stone_Cobble", 0), 100 * d.get(one, 0), "C34 ... credited 100 Cobblestone each")
        T433._restore(L, p, snap)
    # fixer: Cooled Magma cobble (Zone 4 host since 0.4.24, a Zone 5 stone) credits the Volcanic collection's Rock_Magma_Cooled - Collect + Shard Link
    for z_ in (4, 5):
        _quarry(L, p, z_, totems=False, extra={"mining.compactor": 1, "mining.i0.drops": "Rock_Magma_Cooled_Cobble:7,Rock_Volcanic_Cobble:3"})
        snap = T433._props(p)
        r, inv, coll_c, xp_c = T433._collect(L, ou, MI, got)
        K.check(inv.get("Rock_Magma_Cooled_Cobble", 0) == 7, "C34 zone %d: Collect gives the 7 Cooled Magma cobble (%s)" % (z_, r[:100]))
        K.eq((coll_c.get("Rock_Magma_Cooled", 0), coll_c.get("Rock_Magma_Cooled_Cobble", 0), coll_c.get("Rock_Volcanic_Cobble", 0)), (7, 0, 3),
             "C34 zone %d: Collect credits Cooled Magma cobble as Rock_Magma_Cooled (the Volcanic collection)" % z_)
        K.check(p.getProperty("owed.coll.Rock_Magma_Cooled_Cobble") is None, "C34 zone %d: nothing left waiting for a collection that does not exist" % z_)
        T433._restore(L, p, snap)
        sk = T433.Sacks(OWNER)
        n, pool, coll_l, xp_l = T433._link(L, ou, MI, got, sk)
        K.check(n > 0 and pool.get("Rock_Magma_Cooled_Cobble", 0) == 7, "C34 zone %d: Shard Link moves the cobble (%d, %s)" % (z_, n, pool))
        K.eq(coll_l, coll_c, "C34 zone %d: Shard Link credit = Collect's" % z_)
        T433._restore(L, p, snap)
    # a click compacts too
    _quarry(L, p, 1, totems=False, extra={"mining.compactor": 1, "mining.i0.nsize": 10, "mining.i0.drops": "Rock_Stone_Cobble:99"})
    Cfg.CK_CPS = 1000
    from jpype import JClass, JLong
    Core.NOW_TEST = T0 + 10 ** 9
    Ck.RND_TEST = JClass("java.util.Random")(JLong(5))
    Ck.RND2_TEST = JClass("java.util.Random")(JLong(6))
    for _ in range(60):
        s = str(Ck.chop(ou, JString(OWNER), MI, 0, 0, JString(PICK))[0])
        if s.startswith("+") or s.startswith("-"):
            break
    Ck.RND_TEST = None
    Ck.RND2_TEST = None
    d = _drops(p)
    K.check(s.startswith("+Mined") and d.get("Skyy_Ench_Cobblestone", 0) == 1 and d.get("Rock_Stone_Cobble", 0) < 100, "C34 a click with 99 stored: 1 Enchanted Cobblestone (%s | %s)" % (d, s[:140]))
    K.save()


# ---------------------------------------------------------------------------------------------------- O34: other shards unchanged + the fold
def run_others(out, jar, scratch, _home):
    from jpype import JString, JClass, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "o34")
    Ck, Core, Cfg, Isl, M, St = L["ShClk"], L["ShCore"], L["ShCfg"], L["ShIsl"], L["ShMath"], L["ShStore"]
    for kd in (FO, FK, RA, OR, CK):
        outs = []
        for off in (False, True):
            Cfg.MQ34_OFF_TEST = off
            T433._seed(L, p, kd)
            _locked(L, lambda: M.settleAll(kd, p, T0 + 5 * 3600000))
            outs.append(T433._props(p))
        K.eq(outs[0], outs[1], "O34 %s: settle byte-identical with the 0.4.34 paths on / off" % T433.KN[kd])
    Cfg.MQ34_OFF_TEST = False
    # a Foraging click: the same with on / off
    res = []
    for off in (False, True):
        Cfg.MQ34_OFF_TEST = off
        T423._foraging(L, p)
        Ck.XPA.clear()
        Core.NOW_TEST = T0 + (2 if off else 1) * 10 ** 9
        Ck.RND_TEST = JClass("java.util.Random")(JLong(77))
        Ck.RND2_TEST = JClass("java.util.Random")(JLong(78))
        s = ""
        for _ in range(80):
            s = str(Ck.chop(ou, JString(OWNER), FO, 0, 0, JString("Tool_Hatchet_Iron"))[0])
            if s.startswith("+") or s.startswith("-"):
                break
        Ck.RND_TEST = None
        Ck.RND2_TEST = None
        res.append((s, T425._drops(p, 0, "foraging")))
    K.eq(res[0], res[1], "O34 a Foraging click: the same felled tree with on / off")
    Cfg.MQ34_OFF_TEST = False
    # a Mining click with the paths off = 0.4.33 (one host stone kind, no compaction)
    _quarry(L, p, 1, totems=False, extra={"mining.compactor": 1})
    Cfg.MQ34_OFF_TEST = True
    Core.NOW_TEST = T0 + 10 ** 9
    Ck.RND_TEST = JClass("java.util.Random")(JLong(3))
    for _ in range(60):
        s = str(Ck.chop(ou, JString(OWNER), MI, 0, 0, JString(PICK))[0])
        if s.startswith("+") or s.startswith("-"):
            break
    Ck.RND_TEST = None
    Cfg.MQ34_OFF_TEST = False
    K.check(set(i for i in _drops(p) if i.startswith("Rock_")) == {"Rock_Stone_Cobble"}, "O34 MQ34_OFF_TEST: a click gives the host stone only (0.4.33): %s" % _drops(p))
    # the 0.4.30 fold knows prec + qsf
    keys = _keys(L)

    def two():
        for k_ in list(p.stringPropertyNames()):
            if str(k_).startswith("mining.") or str(k_) == "mzone.done":
                p.remove(k_)
        for s_, ty in ((0, keys[0]), (1, keys[1])):
            p.setProperty("mining.i%d.type" % s_, ty); p.setProperty("mining.i%d.size" % s_, "1"); p.setProperty("mining.i%d.last" % s_, str(T0))
            p.setProperty("mining.i%d.stored" % s_, "0"); p.setProperty("mining.i%d.totems" % s_, "quarry_spirit:1:::0:fd%04d" % s_)
        p.setProperty("mining.i0.prec", "1"); p.setProperty("mining.i1.prec", "3"); p.setProperty("mining.i1.qsf", "0.5;0.25;10;7")
        p.setProperty("mining.auto", "1"); p.setProperty("mining.paused", "0"); p.setProperty("mining.storage", "5")
        p.setProperty("mining.placed", L["W_"] + "|1|2|3")
    T430._set(L, p, two)
    Core.NOW_TEST = T0
    St.migrate5(JString(OWNER), p)
    K.check(str(p.getProperty("mzone.done")) == "1" and str(p.getProperty("mining.i0.prec")) == "3" and p.getProperty("mining.i1.type") is None
            and not any(str(k_).startswith("mining.i1.") for k_ in p.stringPropertyNames()),
            "O34 the 0.4.30 fold: a 2nd island with prec / qsf folds (prec = the higher 3, its keys gone)")
    K.save()


def run_live(out, jar, scratch, home):
    T431.run_live(out, jar, scratch, home)


ROWS30 = "MP 9 rows (Ore nodes as before), the caption says where Iron is added: "


def run_page30(out, jar, scratch, home):
    """0.4.30's page phase as it is; its one row-count check (9 rows) is the number this round changes (10: Precious finds) - that check is
    replaced by U34's (10 rows, Ore nodes as before, the same caption), every other check of the phase stands"""
    dict(T433.PHASES)["page30"](out, jar, scratch, home)
    d = json.load(open(out))
    left = [x for x in d["fails"] if not x.startswith(ROWS30)]
    if len(left) != len(d["fails"]):
        d["notes"].append("page30: the 9-row check is U34's 10-row check now (Precious finds): " + "; ".join(x for x in d["fails"] if x.startswith(ROWS30)))
        d["ok"] += len(d["fails"]) - len(left)
        d["fails"] = left
        json.dump(d, open(out, "w"), indent=1)


EXPECT = {   # 0.4.33 -> 0.4.34: the rows + their fields, ShMath (Enchanted forms, the use, settle, quarryExtra / qCap), ShClk (Precious, stones, the click),
            # the credit (ShCore.owedAs, ShLink.credAs), the page (row 9), the fold's key lists (ShStore <clinit>); the rest = the @VERSION@ string
    'CfgFile': ['~<clinit>'], 'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'], 'CfgRows1': ['~<clinit>'], 'CfgRows2': ['~<clinit>'],
    'ShCfg': ['+f MQ34_OFF_TEST', '+f MQ_HOST', '+f MQ_PREC', '+f MQ_PREC_MAX', '+f MQ_SP_RARE', '+f MQ_SP_STONE', '~<clinit>', '~m loadCfg'],
    'ShClk': ['+f DCM', '+f RND2_TEST', '+f SPX', '+f ZS_A', '+f ZS_ID', '+m addTo0', '+m buyPrec', '+m dcOn', '+m extCnt', '+m hostCnt', '+m hostPct',
              '+m prec', '+m rareQ', '+m rnd2', '+m stones', '+m stonesAt', '+m zsId', '+m zsN', '~<clinit>', '~m buyLuck', '~m mine'],
    'ShCore': ['~m owedAs'], 'ShFill': ['~m markFixed'], 'ShLink': ['~m credAs'],
    'ShMath': ['+f DC_B', '+f DC_E', '+m dcBase', '+m dcCompact', '+m dcHeld', '+m qCap', '+m quarryExtra', '~<clinit>', '~m settle', '~m usedOf'],
    'ShPage': ['~m actQuarry', '~m buildClick', '~m ckPre', '~m fillQuarry'],
    'ShStore': ['~<clinit>', '~m migrate', '~m migrate2', '~m migrate3', '~m migrate4', '~m migrate5', '~m migrate6', '~m mzFold', '~m save'],
    'SkyyShardsPlugin': ['~m setup'],
}

PHASES = [("static", run_static), ("rates34", run_rates), ("spirits34", run_spirits), ("upgrade34", run_upgrade), ("carry34", run_carry),
          ("others34", run_others)] + [(x[0], run_page30) if x[0] == "page30" else x for x in T433.PHASES if x[0] not in ("static", "livemig33")] +          [("livemig34", run_live)]


if __name__ == "__main__":
    ph = PHASES
    if "--only" in sys.argv and "--phase" not in sys.argv:
        want = set(HK.arg("--only").split(","))
        ph = [x for x in PHASES if x[0] in want]
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=ph, script=__file__, live=(T431.T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
