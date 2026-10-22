"""Harness for SkyyShards 0.4.4 (Balance P6 part A: the totem idle share 20 / 40 / 60 / 80 / 100 % by totem tier; tools/shards_0_4_4_patch.py).
Build first: python tools/shards_0_4_4_patch.py && python SkyyShards/build_skyyshards_0.4.4.py

    python SkyyShards/test_skyyshards_0.4.4.py [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.3 -> 0.4.4: + the class ShMig044; exactly the planned members differ (EXPECT)
  R    rates    the REAL ShTotem / ShMath maths on shard Properties (a Farming shard, one Wheat island):
                R1 the FULL SHARD of today (1 Large island, 5 Harvest Spirits of tier k, no augments / booster / compressor): islandRate x 60 =
                   20 / 40 / 60 / 80 / 100 % of 500 x q x D(3k-1) (q = 1.5 Wheat) within 1 % (337.5 / 1,215 / 2,767.5 / 4,962 / 7,792.5 an hour);
                   0.4.3's defaults on the same island printed (300 / 1,350 / 3,150 / 3,600 / 3,600)
                R2 one Harvest Spirit I on the starter (Small) island = 1.125 / min (67.5 an hour; was 1)
                R3 the per-tier cap: WMAXS = 12 / 24 / 48 / 96 / 192 by tier; a single number "12" = 12 for every tier (0.4.3's rule: a tier V
                   worker on Large capped at 12); "0" = no cap; junk / 6 numbers = the default list (+ WARN); "5,10" = 5, 10, 10, 10, 10
                R4 ShMath.settle over one real hour of a Totem V full island (storage big enough) makes 7,792 items (the lazy maths)
                R5 tier-up costs: the Farming totems' costs are paid in Enchanted Wheat (ShKind.UPG = the island's own Enchanted crop)
                R6 Server Setup text (fix): the Tier II..V speed rows have no "x" unit and say "Items a minute"
  X    xp       (fix, critic) idle Farming XP per totem tier: XPWS = 24 / 46 / 66 / 85 / 103 (xp.wheat list; parser cases); ShTotem.xpPer
                = the tier's XP on a full island, the rate-weighted mix on a mixed one, the highest totem tier without a worker; a REAL
                ShCore.collect of 1,000 stored Wheat on a Totem V Large island pays 51,500 Farming XP (1,000 x 103 x 50 %) through skill:fn:addxp,
                the mixed island floor(1,000 x mix x 50 %), a single number "4" = 2,000 (the old rule), "0" = no XP call; the Collect tab
                preview (ShPage.fill) shows the same XP; a full shard hour at 50 % = 20..100 % x an active Zone k hour x 50 % within 3 %
  R7   (fix 2) storage tier N = 3 days of a full Large Totem N island (243 / 875 / 1,993 / 3,573 / 5,611 stacks; settle over 3 days fits)
  X2   (fix 2) XP priced when MADE: Tier I stock collected after swapping in Tier V pays 24 each (preview too); xpn / xpw pair rules
  M    mig      ShMig044 on scratch files: the NewBetaTest config (read only, copied; CRLF?): the 6 totem lines move 0.4.3 -> 0.4.4, the marker
                appended in the file's own ending, Properties differ only there, History = the old bytes, 6 change-log lines; loadCfg reads
                them; start 2 changes nothing; a hand edit (rate3 = 9) + a doubled rate4 kept + named; a single-number workerMax 20 kept;
                Undo through the kit; a fresh start (loadCfg writes the default) carries the marker and nothing is done; History blocked =
                untouched, the next start updates
  D    live     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards: the setup chain (migCoop, ShMig044, loadCfg) twice: start 1
                changes only the 6 lines (+ marker, History, change log), start 2 nothing; then 0.4's run_live (reads, nothing written)
  AA   engine-access audit
UNVERIFIED (needs the game): the shard menu's numbers in game; SkyySkills' real handling of the bigger shard XP calls; slots 2-6 cannot be filled yet (a later round re-scales by the island count).
Scratch: tools/dev/scratch/balp6afix2/shards (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.4"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp6afix2", "shards")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.3.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_2", os.path.join(HERE, "test_skyyshards_0.4.2.py"))
T42 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T42)
T04 = T42.T04
LIVE_SH = T42.LIVE_SH
TARGET = [337.5, 1215.0, 2767.5, 4962.0, 7792.5]
OLD_RATE = ["1", "1.25", "1.5", "1.75", "2"]
NEW_RATE = ["1.125", "1.125", "1.3179", "1.3557", "1.4117"]
MK = "skyyshards-0.4.4-p6"
STORE = [243, 875, 1993, 3573, 5611]
OLD_STORE = ["1", "3", "6", "12", "24"]


def shard(J, size, tier, n, slots=1):
    p = J("java.util.Properties")()
    for s in range(slots):
        p.setProperty("farming.i%d.type" % s, "wheat")
        p.setProperty("farming.i%d.size" % s, str(size))
        p.setProperty("farming.i%d.totems" % s, ",".join("harvest_spirit:%d:::0:u%d%d" % (tier, s, i) for i in range(n)))
    p.setProperty("farming.placed", "1")
    return p


def run_rates(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Cfg, Tot, Mth, Kind = (JClass(PKG + n) for n in ("ShCfg", "ShTotem", "ShMath", "ShKind"))
    FK = 2
    t0 = 1790000000000
    K.eq([round(float(x), 4) for x in Cfg.RATES], [float(x) for x in NEW_RATE], "R the totem.rate1..5 defaults (0.4.4)")
    K.eq([float(x) for x in Cfg.WMAXS], [12.0, 24.0, 48.0, 96.0, 192.0], "R3 the worker cap per tier defaults to 12,24,48,96,192")
    got = []
    for k in range(5):
        p = shard(JClass, 3, k + 1, 5)
        r = float(Mth.rate(FK, p, 0, JLong(t0)))
        got.append(r * 60.0)
        K.check(abs(r * 60.0 / TARGET[k] - 1.0) < 0.01, "R1 full shard Totem %s: %.1f items an hour = %d %% of an active Zone %d farming hour (target %.1f)"
                % ("I II III IV V".split()[k], r * 60.0, 20 * (k + 1), k + 1, TARGET[k]))
    # 0.4.3's numbers on the same island (its defaults put back for one measure)
    rt0 = Cfg.RATES
    wm0 = Cfg.WMAXS
    import jpype
    Cfg.RATES = jpype.JArray(jpype.JDouble)([float(x) for x in OLD_RATE])
    Cfg.WMAXS = jpype.JArray(jpype.JDouble)([12.0] * 5)
    old = [float(Mth.rate(FK, shard(JClass, 3, k + 1, 5), 0, JLong(t0))) * 60.0 for k in range(5)]
    K.eq([round(x) for x in old], [300, 1350, 3150, 3600, 3600], "R1 0.4.3's defaults on the same full island (for the record): %s / h" % [round(x) for x in old])
    Cfg.RATES = rt0
    Cfg.WMAXS = wm0
    print("R1 full shard per hour: 0.4.3 %s -> 0.4.4 %s (targets %s)" % ([round(x) for x in old], [round(x, 1) for x in got], TARGET))
    K.eq(round(float(Mth.rate(FK, shard(JClass, 1, 1, 1), 0, JLong(t0))), 4), 1.125, "R2 one Harvest Spirit I on the starter Small island = 1.125 / min")
    # R3 the caps
    pV = shard(JClass, 3, 5, 1)
    K.eq(round(float(Mth.rate(FK, pV, 0, JLong(t0))), 3), 25.975, "R3 a tier V worker on Large: 25.975 / min (under its 192 cap)")
    for txt, want in (("12", [12.0] * 5), ("0", [0.0] * 5), ("5,10", [5.0, 10.0, 10.0, 10.0, 10.0]), ("12, 24 ,48,96,192", [12.0, 24.0, 48.0, 96.0, 192.0]),
                      ("abc", [12.0, 24.0, 48.0, 96.0, 192.0]), ("1,2,3,4,5,6", [12.0, 24.0, 48.0, 96.0, 192.0]), (None, [12.0, 24.0, 48.0, 96.0, 192.0]),
                      ("-3,999999", [0.0, 100000.0, 100000.0, 100000.0, 100000.0])):
        K.eq([float(x) for x in Cfg.wmaxOf(JString(txt) if txt is not None else None)], want, "R3 totem.workerMax=%r -> %s" % (txt, want))
    Cfg.WMAXS = Cfg.wmaxOf(JString("12"))
    K.eq(round(float(Mth.rate(FK, pV, 0, JLong(t0))), 3), 12.0, "R3 a single number 12 = the 0.4.3 rule: the tier V worker capped at 12")
    Cfg.WMAXS = Cfg.wmaxOf(JString("0"))
    K.eq(round(float(Mth.rate(FK, pV, 0, JLong(t0))), 3), 25.975, "R3 0 = no cap")
    Cfg.WMAXS = wm0
    # R4 one hour of the lazy maths (ShMath.settle) on a full Totem V island, storage made big enough
    Cfg.ST1 = 1000
    p = shard(JClass, 3, 5, 5)
    p.setProperty("farming.i0.last", str(t0))
    p.setProperty("farming.i0.stored", "0")
    made = int(Mth.settle(FK, p, 0, JLong(t0 + 3600000)))
    K.check(abs(made - 7792) <= 1 and int(p.getProperty("farming.i0.stored")) == made, "R4 settle over one hour of a full Totem V island makes %d (7,792)" % made)
    # R7 (fix 2, critic): storage tier N holds 3 days of a full Large island at Totem N (Skyy "20-100%, 3 days")
    Cfg.ST1 = 243
    K.eq([int(Cfg.ST1), int(Cfg.ST2), int(Cfg.ST3), int(Cfg.ST4), int(Cfg.ST5)], STORE, "R7 storage.tier1..5 defaults = %s stacks" % STORE)
    for k in (0, 4):
        p = shard(JClass, 3, k + 1, 5)
        p.setProperty("farming.storage", str(k + 1))
        p.setProperty("farming.i0.last", str(t0))
        p.setProperty("farming.i0.stored", "0")
        made = int(Mth.settle(FK, p, 0, JLong(t0 + 259200000)))
        cap = int(Mth.capOf(FK, p, 0))
        K.check(made >= int(TARGET[k] * 72) - 10 and made <= cap and cap == 100 * STORE[k],
                "R7 3 days of a full Totem %s island at storage tier %d: %d made, cap %d (storage lasts the 3-day bank)" % ("I II III IV V".split()[k], k + 1, made, cap))
    K.eq(str(Kind.UPG[FK]), "Skyy_Ench_Wheat", "R5 Farming totem tier-ups are paid in Enchanted Wheat (the island's own crop)")
    c = str(Tot.costFor(FK, 1, Tot.upCost(1)))
    K.check(c.startswith("Skyy_Ench_Wheat:1") and "Ingredient_Life_Essence:10" in c, "R5 Totem I -> II costs %s (counts unchanged)" % c)
    bs = open(os.path.join(HERE, "build_skyyshards_%s.py" % VERSION), encoding="utf8").read()
    K.check('"0", "100", "", "", "live",\n      "Items a minute of a tier %s worker' in bs and '"", "x", "live",\n      "Speed of a tier' not in bs,
            "R6 the Tier II..V speed rows: no 'x' unit, 'Items a minute ... times its crops in range'")
    K.save()


XPW = [24, 46, 66, 85, 103]
P3Z = [80, 280, 605, 1050, 1600]   # P3 3.3 XP of the Zone k crop (T 3k-1)


def run_xp(out, jar, scratch, _home):
    from jpype import JClass, JArray, JLong, JInt, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    _s3 = importlib.util.spec_from_file_location("test_skyyshards_0_3_x", os.path.join(HERE, "test_skyyshards_0.3.py"))
    T3 = importlib.util.module_from_spec(_s3)
    _s3.loader.exec_module(T3)
    Sys = JClass("java.lang.System")
    Sys.getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg, St, Mth, Tot, Core, Page, Pay = (JClass(PKG + n) for n in ("ShCfg", "ShStore", "ShMath", "ShTotem", "ShCore", "ShPage", "ShPay"))
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    PyFn = T3.fn_class()
    base = os.path.join(scratch, "xp")
    os.makedirs(base, exist_ok=True)
    pth = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    Cfg.DIR = pth(base)
    Cfg.FILE = pth(os.path.join(base, "config.properties"))
    Cfg.loadCfg(True)
    txt = open(os.path.join(base, "config.properties"), encoding="utf-8").read()
    K.check("xp.wheat=24,46,66,85,103" in txt.splitlines() and [int(x) for x in Cfg.XPWS] == XPW and int(Cfg.XP_WHEAT) == 24 and int(Cfg.XP_PCT) == 50,
            "X the default file + loadCfg: xp.wheat=24,46,66,85,103, XPWS, XP_WHEAT = 24, shard.xpPercent 50")
    for t_, want in (("4", [4] * 5), ("0", [0] * 5), ("5,10", [5, 10, 10, 10, 10]), (" 24, 46 ,66,85,103", XPW), ("abc", XPW), ("1,2,3,4,5,6", XPW),
                     (None, XPW), ("-3,99999", [0, 1000, 1000, 1000, 1000]), ("2.6", [3] * 5)):
        K.eq([int(x) for x in Cfg.xpwOf(JString(t_) if t_ is not None else None)], want, "X xp.wheat=%r -> %s" % (t_, want))
    t0 = 1790000000000
    FK = 2
    for k in range(5):
        p = shard(JClass, 3, k + 1, 5)
        K.check(abs(float(Tot.xpPer(FK, p, 0, 3, JLong(t0))) - XPW[k]) < 1e-9, "X xpPer full Totem %d island = %d" % (k + 1, XPW[k]))
        xph = float(Mth.rate(FK, p, 0, JLong(t0))) * 60.0 * float(Tot.xpPer(FK, p, 0, 3, JLong(t0))) * 0.5
        tgt = 0.2 * (k + 1) * 500 * P3Z[k] * 0.5
        K.check(abs(xph / tgt - 1.0) < 0.03, "X full shard Totem %d: %.0f idle XP an hour = %d %% x %d active x 50 %% (%.0f) within 3 %%"
                % (k + 1, xph, 20 * (k + 1), 500 * P3Z[k], tgt))
    pm = shard(JClass, 3, 1, 1)
    pm.setProperty("farming.i0.totems", "harvest_spirit:1:::0:a,harvest_spirit:5:::0:b")
    ra, rb = 1.125, 25.975
    mix = (ra * 24 + rb * 103) / (ra + rb)
    K.check(abs(float(Tot.xpPer(FK, pm, 0, 3, JLong(t0))) - mix) < 1e-3, "X xpPer mixed island (I + V workers): rate-weighted %.3f" % mix)
    pn = shard(JClass, 3, 1, 0)
    pn.setProperty("farming.i0.totems", "rain:4:::0:r")
    K.eq(float(Tot.xpPer(FK, pn, 0, 3, JLong(t0))), 85.0, "X xpPer without a worker = the highest totem tier (a Rain Totem IV -> 85)")
    pn.setProperty("farming.i0.totems", "")
    K.eq(float(Tot.xpPer(FK, pn, 0, 3, JLong(t0))), 24.0, "X xpPer without totems = tier I (24)")
    K.eq(float(Tot.xpPer(0, pn, 0, 3, JLong(t0))), float(Cfg.xpOf(0)), "X xpPer of another shard = its flat xpOf (unchanged)")
    # a REAL Collect (the 0.3 harness stand-ins: item store, containers, bridge functions)
    T3.item_store([("Plant_Crop_Wheat_Item", 100), ("Skyy_Ench_Wheat", 100), ("Rock_Stone", 100)])
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    inv = lambda: JArray(IC)([SIC(JClass("java.lang.Short")(40).shortValue()) for _ in range(2)])
    Cfg.KEY_TEST = PyFn(lambda u: str(u))
    St.DIR = pth(os.path.join(base, "shards"))
    St.CACHE.clear()
    OWN = "0f0f0f0f-1111-2222-3333-444444444444"
    ou = UUID.fromString(OWN)
    xp_calls = []
    fns = JClass("java.util.HashMap")()
    fns.put("skill:fn:addxp", PyFn(lambda a: (xp_calls.append((str(a[1]), int(a[2]), str(a[3]))), JClass("java.lang.Boolean").TRUE)[1]))
    fns.put("coll:fn:add", PyFn(lambda a: JClass("java.lang.Boolean").TRUE))
    fns.put("coins:fn:get", PyFn(lambda u: JLong(0)))
    fns.put("coll:fn:tier", PyFn(lambda a: JInt(9)))
    Pay.TEST_FNS = fns
    T1 = t0 + 3600000
    Core.NOW_TEST = T1
    V5 = ",".join("harvest_spirit:5:::0:u%d" % i for i in range(5))

    def put(totems, stored):
        po = St.get(OWN)
        po.clear()
        po.setProperty("pkey", OWN)
        Mth.starter(po, JLong(t0))
        po.setProperty("farming.i0.size", "3")
        po.setProperty("farming.storage", "5")
        po.setProperty("farming.i0.totems", totems)
        po.setProperty("farming.i0.stored", str(stored))
        po.setProperty("farming.i0.last", str(T1))
        po.setProperty("farming.placed", "skyy-island-%s|3|129|3" % OWN)
        St.save(OWN, po)
        return po
    try:
        put(V5, 1000)
        pg = Page(ou, "skyy-island-" + OWN)
        TI = inv()
        pg.fill(OWN, TI)
        K.check("+51,500 Farming XP" in str(pg.cAll[1]), "X the Collect tab preview (ShPage.fill) of 1,000 Totem V wheat: %s" % pg.cAll[1])
        r = str(Core.collect(ou, OWN, -1, TI))
        K.check(r.startswith("+Collected 1,000 Wheat") and xp_calls and xp_calls[-1] == ("Farming", 51500, "shard:farming") and "+51,500 Farming XP" in r,
                "X a real Collect: 1,000 Totem V wheat -> 51,500 Farming XP (1,000 x 103 x 50 %%): %s | %s" % (r, xp_calls[-1:]))
        put("harvest_spirit:1:::0:a,harvest_spirit:5:::0:b", 1000)
        xm = float(Tot.xpPer(FK, St.get(OWN), 0, 3, JLong(T1)))
        r = str(Core.collect(ou, OWN, -1, inv()))
        K.eq(xp_calls[-1][1], int(1000 * xm * 0.5 + 1e-9), "X a real Collect on the mixed island pays floor(1,000 x %.3f x 50 %%)" % xm)
        # fix 2 (critic): XP priced when MADE - Tier I workers fill the store, a Tier V swapped in before Collect pays Tier I XP
        V1 = ",".join("harvest_spirit:1:::0:w%d" % i for i in range(5))
        po = put(V1, 0)
        po.setProperty("farming.i0.last", str(T1 - 3600000))
        Mth.settleAll(FK, po, JLong(T1))
        n1 = int(po.getProperty("farming.i0.stored"))
        K.check(abs(n1 - 337) <= 1 and int(po.getProperty("farming.i0.xpn")) == n1 and abs(float(po.getProperty("farming.i0.xpw")) - 24.0 * n1) < 1e-6,
                "X fix2 one hour of 5 Tier I workers: %d stored, xpn %s, xpw %s (= 24 each)" % (n1, po.getProperty("farming.i0.xpn"), po.getProperty("farming.i0.xpw")))
        po.setProperty("farming.i0.last", str(T1))
        po.setProperty("farming.i0.totems", V5)   # the swap (placeTotem settles first, as above)
        St.save(OWN, po)
        pg = Page(ou, "skyy-island-" + OWN)
        pg.fill(OWN, inv())
        want1 = int(n1 * 24 * 0.5 + 1e-9)
        K.check(("+{:,} Farming XP".format(want1)) in str(pg.cAll[1]), "X fix2 the preview after the swap shows the Tier I XP %d: %s" % (want1, pg.cAll[1]))
        r = str(Core.collect(ou, OWN, -1, inv()))
        K.eq(xp_calls[-1][1], want1, "X fix2 Tier I stock collected after swapping in Tier V pays %d x 24 x 50 %% (not x 103)" % n1)
        po = St.get(OWN)
        K.check(str(po.getProperty("farming.i0.xpn")) == "0" and float(po.getProperty("farming.i0.xpw")) == 0.0, "X fix2 after Collect xpn / xpw = 0 / 0")
        for xn, xw, want, why in (("1000", "24000", 12000, "matching pair: 24 each"), ("999", "24000", 51500, "xpn not the stored count (0.4.3 / rollback): the current tiers"),
                                  ("1000", "abc", 51500, "junk xpw: the current tiers"), ("1000", "1e12", 51500, "over the top tier: capped at 103")):
            po = put(V5, 1000)
            po.setProperty("farming.i0.xpn", xn)
            po.setProperty("farming.i0.xpw", xw)
            St.save(OWN, po)
            r = str(Core.collect(ou, OWN, -1, inv()))
            K.eq(xp_calls[-1][1], want, "X fix2 %s -> %d XP" % (why, want))
        po = put(V5, 1000)
        po.setProperty("farming.i0.xpn", "1000")
        po.setProperty("farming.i0.xpw", "24000")
        St.save(OWN, po)
        small = JArray(IC)([SIC(JClass("java.lang.Short")(2).shortValue())])
        r = str(Core.collect(ou, OWN, -1, small))
        po = St.get(OWN)
        K.check(xp_calls[-1][1] == 2400 and str(po.getProperty("farming.i0.stored")) == "800" and str(po.getProperty("farming.i0.xpn")) == "800"
                and abs(float(po.getProperty("farming.i0.xpw")) - 19200.0) < 1e-6,
                "X fix2 a part Collect (200 fit): 2,400 XP, the 800 back keep 24 each (xpn %s, xpw %s): %s" % (po.getProperty("farming.i0.xpn"), po.getProperty("farming.i0.xpw"), r[:60]))
        Cfg.XPWS = Cfg.xpwOf(JString("4"))
        put(V5, 1000)
        r = str(Core.collect(ou, OWN, -1, inv()))
        K.eq(xp_calls[-1][1], 2000, "X xp.wheat=4 (one number) = the 0.4.3 rule: 1,000 x 4 x 50 %% = 2,000")
        Cfg.XPWS = Cfg.xpwOf(JString("0"))
        Cfg.XP_WHEAT = 0
        n0 = len(xp_calls)
        put(V5, 1000)
        r = str(Core.collect(ou, OWN, -1, inv()))
        K.check(len(xp_calls) == n0 and r.startswith("+Collected 1,000 Wheat") and "XP" not in r.split("Wheat", 1)[1].split("Harvest", 1)[0],
                "X xp.wheat=0: no XP call, the items still collected: %s" % r)
        Cfg.XPWS = Cfg.xpwOf(None)
        Cfg.XP_WHEAT = 24
    except Exception as ex:
        K.check(False, "X the Collect run failed: %s" % str(ex)[:400])
    K.save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass, JString
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    Mig = JClass(PKG + "ShMig044")
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

    def hist(home):
        hd = os.path.join(home, "config-history")
        return [open(os.path.join(hd, n), "rb").read() for n in sorted(os.listdir(hd)) if n.endswith(".bak")] if os.path.isdir(hd) else []

    def chg(home):
        f = os.path.join(home, "config-changes.log")
        return [l.split("\t") for l in open(f, encoding="utf8").read().splitlines()] if os.path.isfile(f) else []

    def props(b_):
        P_ = JClass("java.util.Properties")()
        P_.load(JClass("java.io.ByteArrayInputStream")(b_))
        return dict((str(k), str(P_.getProperty(k))) for k in P_.stringPropertyNames())
    keys = ["totem.rate%d" % i for i in range(1, 6)] + ["totem.workerMax", "xp.wheat"] + ["storage.tier%d" % i for i in range(1, 6)]
    news = NEW_RATE + ["12,24,48,96,192", "24,46,66,85,103"] + [str(x) for x in STORE]
    live = os.path.join(LIVE_SH, "config.properties")
    A_ = open(live, "rb").read() if os.path.isfile(live) else None
    K.check(A_ is not None, "M the live NewBetaTest config.properties exists (read only)")
    if A_ is not None:
        home, f, Cfg, path = world(A_)
        r = str(Mig.run(path(f)))
        b1 = open(f, "rb").read()
        nl = b"\r\n" if b"\r\n" in A_ else b"\n"
        pa, pb = props(A_), props(b1)
        K.check(sorted(k for k in pb if pa.get(k) != pb.get(k)) == sorted(keys) and all(pb[k] == v for k, v in zip(keys, news)),
                "M live: exactly the 12 lines (totem speeds, cap, xp.wheat, storage tiers) moved to the 0.4.4 defaults: %s" % [(k, pa.get(k), pb.get(k)) for k in keys])
        K.check(b1.endswith(("# ---------- SkyyShards 0.4.4 (marker %s" % MK).encode() + b1.split(MK.encode())[1].split(nl)[0] + nl)
                and b1.count(b"\r\n") == A_.count(b"\r\n") + (1 if nl == b"\r\n" else 0), "M live: the marker line appended in the file's own line ending")
        K.check(hist(home) == [A_], "M live: config-history holds the old bytes")
        cl = chg(home)
        K.check(sorted((x[4], x[5], x[6]) for x in cl) == sorted(zip(keys, OLD_RATE + ["12", "4"] + OLD_STORE, news)) and all(x[1] == "SkyyShards 0.4.4" and x[7] == "ok" for x in cl),
                "M live: one change-log line per moved value (12): %s" % [x[4:7] for x in cl])
        Cfg.loadCfg(False)
        K.check([round(float(x), 4) for x in Cfg.RATES] == [float(x) for x in NEW_RATE] and [float(x) for x in Cfg.WMAXS] == [12.0, 24.0, 48.0, 96.0, 192.0]
                and [int(x) for x in Cfg.XPWS] == XPW and [int(Cfg.ST1), int(Cfg.ST2), int(Cfg.ST3), int(Cfg.ST4), int(Cfg.ST5)] == STORE,
                "M live: loadCfg reads the moved values (+ the idle XP list, the storage tiers)")
        K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == b1 and len(hist(home)) == 1, "M live: start 2 changes nothing (marker)")
        K.check("totem.rate1 1 -> 1.125" in r and "runs once" in r, "M live: the INFO line names the changes: %s" % r[:160])
    # hand edits, doubled line, a single-number workerMax
    syn = b"# head\ntotem.rate1=1.0\ntotem.rate2=1.25\ntotem.rate3=9\ntotem.rate4=1.75\ntotem.rate4=1.75\ntotem.rate5 = 2\r\ntotem.workerMax=20\nx=1\nxp.wheat=10\nstorage.tier2=3\nstorage.tier5=50"
    home, f, Cfg, path = world(syn)
    r = str(Mig.run(path(f)))
    t = open(f, "rb").read().decode("latin-1")
    K.check(t.startswith("# head\ntotem.rate1=1.125\ntotem.rate2=1.125\ntotem.rate3=9\ntotem.rate4=1.75\ntotem.rate4=1.75\ntotem.rate5 = 1.4117\r\ntotem.workerMax=20\nx=1\nxp.wheat=10\nstorage.tier2=875\nstorage.tier5=50\n# ---------- SkyyShards 0.4.4"),
            "M syn: rate1 (1.0 = 1 by value), rate2, rate5 (spaced, its CRLF kept) moved; the hand-edited rate3 9, the doubled rate4 and the admin's workerMax 20 kept: %r" % t[:260])
    K.check("totem.rate3=9 kept - an admin changed it" in r and "totem.rate4=1.75 kept - the line is doubled" in r and "totem.workerMax=20 kept" in r and "xp.wheat=10 kept - an admin changed it" in r and "storage.tier5=50 kept - an admin changed it" in r,
            "M syn: the kept lines are named: %s" % r.replace("\n", " | ")[:300])
    K.eq(len(chg(home)), 4, "M syn: 4 change-log lines (rate1, rate2, rate5, storage.tier2)")
    Cfg.loadCfg(False)
    K.eq([float(x) for x in Cfg.WMAXS], [20.0] * 5, "M syn: the kept single-number cap 20 = every tier (the old rule)")
    K.eq([int(x) for x in Cfg.XPWS], [10] * 5, "M syn: the kept single-number xp.wheat 10 = every tier (the old rule)")
    # Undo through the kit (Server Setup -> Changes -> Undo = a console set of the old value)
    CP, Fn = JClass(PKG + "CfgPub"), JClass(PKG + "CfgFn")
    CP.start(path(os.path.dirname(home)), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyShards"))
    ru = str(Fn.cmdSetConsole(JString("totem.rate1"), JString("1")))
    rw = str(Fn.cmdSetConsole(JString("totem.workerMax"), JString("12,24,48,96,192")))
    CP.shutdown()
    t2 = open(f, "rb").read().decode("latin-1")
    K.check("totem.rate1=1" in t2.splitlines() and "totem.workerMax=12,24,48,96,192" in t2.splitlines() and abs(float(Cfg.RATES[0]) - 1.0) < 1e-9,
            "M undo: the kit sets rate1 back to 1 (and the cap list): %s | %s (the kit's own write evens out the mixed line endings)" % (ru, rw))
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read().decode("latin-1") == t2, "M undo: the next start keeps the undone value (marker)")
    # fresh: no file -> loadCfg writes the default (marker inside) -> nothing to do
    home, f, Cfg, path = world(None)
    K.check(str(Mig.run(path(f))) == "" and not os.path.exists(f), "M fresh: no file -> nothing done")
    Cfg.loadCfg(True)
    t3 = open(f, "rb").read()
    K.check(MK.encode() in t3 and b"totem.rate5=1.4117" in t3 and b"totem.workerMax=12,24,48,96,192" in t3 and b"totem.rate1=1.125" in t3 and b"xp.wheat=24,46,66,85,103" in t3 and b"storage.tier5=5611" in t3,
            "M fresh: the default file carries the marker and the 0.4.4 values")
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == t3 and hist(home) == [], "M fresh: the update finds the marker - nothing written")
    # History blocked
    home, f, Cfg, path = world(b"totem.rate1=1\n")
    open(os.path.join(home, "config-history"), "wb").write(b"not a folder")
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == b"totem.rate1=1\n", "M nohist: config-history cannot be made -> the file is untouched")
    os.remove(os.path.join(home, "config-history"))
    T42.kit_home(home)
    K.check(str(Mig.run(path(f))) != "" and b"totem.rate1=1.125" in open(f, "rb").read(), "M nohist: the next start updates it")
    K.save()


def run_live44(out, jar, scratch, home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    calls = T42.setup_calls(jar)
    K.check(calls.index("ShCfg.migCoop") < calls.index("ShMig044.run") < calls.index("ShCfg.loadCfg") < calls.index("CfgPub.start"),
            "D setup order: migCoop, ShMig044.run, loadCfg, CfgPub.start")
    Cfg, path = T42.kit_home(home)
    Mig = JClass(PKG + "ShMig044")
    t0 = T42.tree(home)
    rs = []
    for s in (1, 2):
        T42.kit_home(home)
        rs.append((str(Cfg.migCoop(Cfg.FILE)), str(Mig.run(Cfg.FILE))))
        r = str(Cfg.loadCfg(True))
        K.check(not r.startswith("default"), "D start %d: the live config is read" % s)
        K.check([round(float(x), 4) for x in Cfg.RATES] == [float(x) for x in NEW_RATE], "D start %d: the 0.4.4 totem speeds" % s)
    t1 = T42.tree(home)
    ch = sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k))
    K.check(all(k == "config.properties" or k.startswith("config-history/") or k == "config-changes.log" for k in ch) and "config.properties" in ch,
            "D start 1 changed only config.properties (+ History, change log): %s" % ch)
    K.check(rs[1] == ("", ""), "D start 2: no update ran")
    K.save()


EXPECT = {
    "ShCfg": ["+f WMAXS", "+f WMAX_DEF", "+m wmaxOf", "+f XPWS", "+f XPW_DEF", "+m xpwOf", "~<clinit>", "~m loadCfg", "~m writeDefaults"],   # loadCfg: the cap list + rate1 default; clinit: the defaults
    "ShMath": ["+m xpCapOf", "+m xpAvg", "+m xpSet", "~m settle"],   # 0.4.4 fix 2: XP priced when made
    "ShTotem": ["~m workerRate", "+m xpPer"], "ShCore": ["~m collect0"], "ShPage": ["~m fill"],   # 0.4.4 fix: idle XP per totem tier
    "ShStore": ["~m save", "~m migrate"], "SkyyShardsPlugin": ["~m setup"], "CfgRows": ["~m header", "~<clinit>"], "CfgFn": ["~m opExport"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ShMig044"],
           phases=[("rates", run_rates), ("xp", run_xp), ("mig", run_mig), ("live", run_live44), ("live2", T04.run_live)],
           script=__file__, live=(LIVE_SH, "mods/Skyy_SkyyShards"))
