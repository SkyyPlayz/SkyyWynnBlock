"""Harness for SkyyCollections 0.2.31 (Balance P6 part B: shorter curves, curve.scale, Enchanted alloys at V + V, CollP6Mig + CollP6EnchMig;
tools/collections_0_2_31_patch.py). Build first:
    python tools/collections_0_2_31_patch.py && python SkyyCollections/build_skyycollections_0.2.31.py
    python SkyyCollections/test_skyycollections_0.2.31.py [--jar <SkyyCollections-0.2.31.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  S    static   the patch re-runs to identical bytes; line endings kept; two new classes, no new command / system; setup order
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.30 -> 0.2.31 (EXPECT below)
  P6   EXECUTED on a fresh folder: CollReg.loadAll -> the fresh collections.properties (marker, P6 curves, curve.scale), every collection's tier
       sizes = tools/balance_model.py p6_scaled(curve, scale) (Copper II 40 / V 250, OakLog II 70, Wheat II 130, Corn, Cobblestone, Thorium,
       Adamantite, RawChicken 100 %); a bad curve.scale = WARN + the default; CollKit.checkScale; CollEnch: Dusk / Azurvane / Cinder / Lumen
       tier 5, Bronze / Electrum 6; CollRewards.settle on a 1,000-Copper profile paid to II: tiers III-V coins + XP once (fake coins / skills
       bridge), a second settle pays 0, the item tiers stay owed (no inventory in a bare JVM - never marked paid without the item)
  MIG  CollP6Mig.update / CollP6EnchMig.update on the REAL 0.2.30 default texts (the old jar's regText / configText): only the planned keys
       (Properties), the marker, one row each; a second run null; a hand-edited curve kept + noted; CRLF kept; the run path (History first,
       change-log rows) on a scratch folder
  LIVE the setup migrations + CollReg.loadAll on a scratch COPY of the live Skyy_SkyyCollections (NewBetaTest), twice: only the planned keys
       change, History copy, one change-log row per changed line; the second start changes nothing; WesleyPlayz-style counts re-read
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import balance_model as BM

VERSION, OLD_VERSION = "0.2.31", "0.2.30"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)
GEN = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyycollections_%s.py" % OLD_VERSION)
PATCH = os.path.join(ROOT, "tools", "collections_0_2_31_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp6b", "coll")))
PKG = "com.skyy.collections."
EXPECT = {"CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],   # the new row + the kit's version texts
          "CollEnch": ["~<clinit>"],          # Dusk / Azurvane / Cinder / Lumen TDEF + TIER 6 -> 5
          "CollKit": ["+m checkScale"],
          "CollReg": ["+f DEF_SCALE", "+m parseScale", "+m scaled", "+m thrOf", "~m configText", "~m maxTier", "~m parseReg", "~m regText", "~m threshold", "~m tierOf"],
          "RegData": ["+f scale", "+f scaleText", "+f thrC"],
          "SkyyCollectionsPlugin": ["~m setup"]}
ADDED = ["CollP6EnchMig", "CollP6Mig"]
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
CURVES_OLD, CURVES_NEW = BM.P6_CURVE_OLD, BM.P6_CURVE_NEW


def snapd(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read()) for r, ds, fs in os.walk(d) for f in fs)


def _props(txt):
    from jpype import JClass
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.StringReader")(txt))
    return dict((str(k), str(p.getProperty(k))) for k in p.stringPropertyNames())


def boot(base):
    from jpype import JClass
    Reg = JClass(PKG + "CollReg")
    JClass(PKG + "CollUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCollTest")
    Reg.BASE = JClass("java.nio.file.Paths").get(base)
    JClass(PKG + "CollStore").DIR = Reg.BASE.resolve("counts")
    return Reg


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.31"') == 1 and '[SkyyCollections] 0.2.31 ready (' in g and '[SkyyCollections] 0.2.30 ready' not in g, "S version + ready line")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count(' = K("') - o.count(' = K("'), 2, "S two new classes")
    su = g[g.index("public void setup() {\n  @PKG@.CollUtil.LOG = getLogger();"):] if "\r\n" not in g else g[g.index("public void setup() {"):]
    K.check(su.index("CollCoinMig.run(base)") < su.index("CollEnch28Mig.run(base)") < su.index("CollP6Mig.run(base)") < su.index("CollP6EnchMig.run(base)") < su.index("CollReg.loadAll()"),
            "S setup: ... CollEnch28Mig -> CollP6Mig -> CollP6EnchMig -> loadAll")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _old_text(name):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    oc = JClass(PKG + "CollReg", loader=ld)
    return str(getattr(oc, name)())


def run_p6(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    base = os.path.join(scratch, "p6", "Skyy_SkyyCollections")
    os.makedirs(os.path.join(base, "counts"))
    Reg = boot(base)
    msg = str(Reg.loadAll())
    R = Reg.D
    K.check(R is not None and int(R.n) > 50, "P6 the default registry loads (%s)" % msg[:120])
    t = open(os.path.join(base, "collections.properties"), encoding="latin-1").read()
    want_lines = ["curve.%s=%s" % (k, ",".join(str(x) for x in CURVES_NEW[k])) for k in "BSRE"]
    K.check(all(("\n" + l + "\n") in t for l in want_lines) and "Balance P6 gathering (SkyyCollections 0.2.31)" in t, "P6 the fresh file: marker + the P6 curves")
    sc = BM.p6_scale_default() + [("RawChicken", 100), ("RawBeef", 100), ("RawPork", 100), ("Wildmeat", 100)]
    want_sc = ",".join("%s:%d" % r for r in sc)
    K.eq(str(R.scaleText), want_sc, "P6 curve.scale default = tools/balance_model.py p6_scale_default + the four meat collections at 100")
    K.check(("\ncurve.scale=" + want_sc + "\n") in t, "P6 the fresh file carries curve.scale")
    ids = [str(x) for x in R.id]
    cats = ["Farming", "Mining", "Foraging", "Combat", "Fishing"]
    scd = dict((k.lower(), v) for k, v in sc)
    bad = []
    for c in range(int(R.n)):
        cur = "BSRE"[int(R.curve[c])]
        pc = scd.get(ids[c].lower(), scd.get(cats[int(R.cat[c])].lower(), 100))
        want = [BM.p6_scaled(x, pc) for x in CURVES_NEW[cur]]
        for i in range(1, len(want)):
            if want[i] <= want[i - 1]:
                want[i] = want[i - 1] + 1
        got = [int(Reg.threshold(R, c, i + 1)) for i in range(int(Reg.maxTier(R, c)))]
        if got != want or int(R.scale[c]) != pc:
            bad.append((ids[c], got[:4], want[:4], int(R.scale[c]), pc))
    K.check(not bad, "P6 every collection's tier sizes = p6_scaled(curve, scale) (%d collections): %s" % (int(R.n), bad[:4]))
    ix = dict((s, i) for i, s in enumerate(ids))

    def tiers(cid):
        c = ix[cid]
        return [int(Reg.threshold(R, c, i + 1)) for i in range(int(Reg.maxTier(R, c)))]
    K.eq(tiers("Copper")[:5], [15, 40, 100, 175, 250], "P6 Copper (S, Mining 100 %) I-V")
    K.eq(tiers("OakLog")[1], 70, "P6 Oak Log II = 70 (B x 180 %, spec 11.7 step 2)")
    K.eq(tiers("Wheat")[1], 130, "P6 Wheat II = 130 (S x 330 %)")
    K.eq(tiers("Corn")[1], 265, "P6 Corn II = 265 (S x 660 %)")
    K.eq(tiers("Cobblestone")[:2], [45, 120], "P6 Cobblestone I-II (B x 300 %)")
    K.eq(tiers("Thorium")[:2], [8, 20], "P6 Thorium (R) I-II")
    K.eq(tiers("Adamantite")[:5], [4, 10, 25, 45, 60], "P6 Adamantite (E) I-V")
    K.eq(tiers("RawChicken")[:2], [15, 40], "P6 RawChicken at 100 % (kill drops)")
    K.eq(int(Reg.tierOf(R, ix["Copper"], 1000)), 7, "P6 1,000 Copper = tier VII (was IV)")
    # a bad curve.scale = one WARN + the default; an admin's text is used
    t2 = t.replace("\ncurve.scale=" + want_sc + "\n", "\ncurve.scale=Mining:200,Foraging\n")
    open(os.path.join(base, "collections.properties"), "w", encoding="latin-1", newline="\n").write(t2)
    Reg.loadAll()
    K.check(str(Reg.D.scaleText) == want_sc and int(Reg.threshold(Reg.D, ix["Copper"], 2)) == 40, "P6 a bad curve.scale -> the default")
    t3 = t.replace("\ncurve.scale=" + want_sc + "\n", "\ncurve.scale=Mining:200,copper:50\n")
    open(os.path.join(base, "collections.properties"), "w", encoding="latin-1", newline="\n").write(t3)
    Reg.loadAll()
    R3 = Reg.D
    K.check(int(Reg.threshold(R3, ix["Copper"], 2)) == 20 and int(Reg.threshold(R3, ix["Iron"], 2)) == 80 and int(Reg.threshold(R3, ix["OakLog"], 2)) == 40,
            "P6 an admin's curve.scale: an id wins over its category (Copper 50 %, Iron Mining 200 %, Oak none = 100 %)")
    t4 = t.replace("\ncurve.scale=" + want_sc + "\n", "\ncurve.scale=Mining:100\n")          # fix round 2: the switch-off the migration's INFO line names
    open(os.path.join(base, "collections.properties"), "w", encoding="latin-1", newline="\n").write(t4)
    Reg.loadAll()
    R4 = Reg.D
    K.check(int(Reg.threshold(R4, ix["OakLog"], 2)) == CURVES_NEW["B"][1] and int(Reg.threshold(R4, ix["Corn"], 2)) == CURVES_NEW["S"][1]
            and int(Reg.threshold(R4, ix["Cobblestone"], 2)) == CURVES_NEW["B"][1], "P6 curve.scale=Mining:100 = every collection on the curve as written (Oak / Corn / Cobblestone II = 40)")
    open(os.path.join(base, "collections.properties"), "w", encoding="latin-1", newline="\n").write(t)
    Reg.loadAll()
    R = Reg.D
    Kit = JClass(PKG + "CollKit")
    K.check(Kit.checkScale("curve.scale", "Foraging:180,Wheat:330") is None and Kit.checkScale("curve.scale", "") is None and Kit.checkScale("curve.scale", "Wheat") is not None
            and Kit.checkScale("curve.scale", "Wheat:0") is not None and Kit.checkScale("curve.scale", "Wheat:x") is not None, "P6 CollKit.checkScale")
    En = JClass(PKG + "CollEnch")
    keys = [str(x) for x in En.KEY]
    tdef = dict(zip(keys, [int(x) for x in En.TDEF]))
    tlive = dict(zip(keys, [int(x) for x in En.TIER]))
    K.eq([tdef[a] for a in ("Dusk", "Azurvane", "Cinder", "Lumen", "Bronze", "Electrum")], [5, 5, 5, 5, 6, 6], "P6 Enchanted alloys: Dusk / Azurvane / Cinder / Lumen at V, Bronze / Electrum VI (defaults)")
    K.eq([tlive[a] for a in ("Dusk", "Lumen", "Bronze")], [5, 5, 6], "P6 the live Enchanted tiers after loadAll (no lines = the defaults)")
    cf = open(os.path.join(base, "config.properties"), encoding="latin-1").read()
    K.check("\nench.tier.dusk=5\n" in cf and "\nench.tier.bronze=6\n" in cf and "Balance P6 enchanted alloys (SkyyCollections 0.2.31)" in cf, "P6 the fresh config file: alloy lines + the marker")
    # settle: 1,000 Copper paid to II -> III .. VII coins + XP once, items owed (no inventory here)
    paid = {"coins": [], "xp": []}

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, a):
            paid["coins"].append(int(a[1]))
            return JClass("java.lang.Long")(int(a[1]))

    @JImplements("java.util.function.Function")
    class Xp(object):
        @JOverride
        def apply(self, a):
            paid["xp"].append((str(a[1]), int(a[2]), str(a[3])))
            return JClass("java.lang.Boolean").TRUE
    br.put("coins:fn:add", Coins())
    br.put("skill:fn:addxp", Xp())
    U = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-00000000c0de")
    key = str(U)
    open(os.path.join(base, "counts", key + ".properties"), "w", encoding="latin-1", newline="\n").write(
        "Ore_Copper=1000\n_paid.Copper=2\n_paidxp.Copper=2\n_paiditem.Copper=2\n_schema=2\n")
    St = JClass(PKG + "CollStore")
    Rw = JClass(PKG + "CollRewards")
    d = St.dataK(key)
    c = ix["Copper"]
    ct = int(St.countTier(d, R, c))
    r1 = [int(x) for x in Rw.settle(d, R, c, U, key)]
    want_c = sum(int(Reg.coinsAt(R, c, t_)) for t_ in range(3, ct + 1))
    want_x = sum(int(g[1]) for t_ in range(3, ct + 1) for g in Reg.xpAt(R, c, t_))
    K.check(ct == 7 and r1[0] == want_c and r1[1] == want_x and paid["coins"] == [int(Reg.coinsAt(R, c, t_)) for t_ in range(3, ct + 1) if int(Reg.coinsAt(R, c, t_)) > 0],
            "P6 settle: tiers III-VII coins %d + XP %d paid once each (got %s, coins %s)" % (want_c, want_x, r1, paid["coins"]))
    K.check(int(St.meta(d, "_paid.Copper")) == 7 and int(St.meta(d, "_paidxp.Copper")) == 7, "P6 settle: the paid markers at VII")
    pi = int(St.meta(d, "_paiditem.Copper"))
    items_owed = [t_ for t_ in range(3, ct + 1) if Reg.itemAt(R, c, t_) is not None]
    K.check(pi == 2 and r1[2] == (1 if items_owed else 0), "P6 settle: the item tiers %s stay owed without an inventory (_paiditem %d, owed flag %d)" % (items_owed, pi, r1[2]))
    n0 = (len(paid["coins"]), len(paid["xp"]))
    r2 = [int(x) for x in Rw.settle(d, R, c, U, key)]
    K.check(r2[0] == 0 and r2[1] == 0 and (len(paid["coins"]), len(paid["xp"])) == n0, "P6 a second settle pays 0 (%s)" % r2)
    K.notes.append("P6 Copper tiers %s; 1,000 Copper = VII; paid coins %s, XP %s" % (tiers("Copper"), paid["coins"], paid["xp"]))
    K.save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    JClass(PKG + "CollUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCollTest")
    old_reg, old_cfg = _old_text("regText"), _old_text("configText")
    M1, M2 = JClass(PKG + "CollP6Mig"), JClass(PKG + "CollP6EnchMig")
    po = _props(old_reg)
    K.check(all(po.get("curve." + k) == ",".join(str(x) for x in CURVES_OLD[k]) for k in "BSRE"), "MIG the 0.2.30 default file holds the old curves")
    r = M1.update(old_reg)
    pn = _props(str(r[0]))
    want = dict(po)
    want.update(dict(("curve." + k, ",".join(str(x) for x in CURVES_NEW[k])) for k in "BSRE"))
    K.eq(sorted(k for k in set(pn) | set(want) if pn.get(k) != want.get(k)), [], "MIG CollP6Mig: only the four curve lines move (Properties)")
    K.check(int(r[1]) == 4 and len(r[3]) == 12 and str(r[2]) == "" and "Balance P6 gathering (SkyyCollections 0.2.31)" in str(r[0]), "MIG 4 rows, the marker, no note")
    K.check(M1.update(str(r[0])) is None, "MIG a second CollP6Mig update = null (marker)")
    lines = str(r[0]).split("\n")
    K.check(lines.index([l for l in lines if "Balance P6 gathering" in l][0]) + 1 == lines.index([l for l in lines if l.startswith("curve.B=")][0]), "MIG the marker sits above curve.B")
    hand = old_reg.replace("\ncurve.R=25,50,100,250,500,1000,2500,5000\n", "\ncurve.R=20,40,80\n")
    rh = M1.update(hand)
    ph = _props(str(rh[0]))
    K.check(ph["curve.R"] == "20,40,80" and ph["curve.S"] == ",".join(str(x) for x in CURVES_NEW["S"]) and int(rh[1]) == 3 and "curve.R=20,40,80" in str(rh[2]), "MIG a hand-edited curve is kept + noted: %s" % str(rh[2])[:80])
    rc = M1.update(old_reg.replace("\n", "\r\n"))
    K.check(_props(str(rc[0])) == want and "\n" not in str(rc[0]).replace("\r\n", ""), "MIG CRLF kept")
    pc = _props(old_cfg)
    K.check(all(pc.get("ench.tier." + a) == "6" for a in ("dusk", "azurvane", "cinder", "lumen", "bronze")), "MIG the 0.2.30 default config holds the alloys at 6")
    r2 = M2.update(old_cfg)
    p2 = _props(str(r2[0]))
    want2 = dict(pc)
    want2.update(dict(("ench.tier." + a, "5") for a in ("dusk", "azurvane", "cinder", "lumen")))
    K.eq(sorted(k for k in set(p2) | set(want2) if p2.get(k) != want2.get(k)), [], "MIG CollP6EnchMig: only the four alloy lines 6 -> 5 (Bronze / Electrum stay)")
    K.check(int(r2[1]) == 4 and M2.update(str(r2[0])) is None and "Balance P6 enchanted alloys" in str(r2[0]), "MIG 4 rows + marker; second run null")
    nol = "\n".join(l for l in old_cfg.split("\n") if not l.startswith("ench.tier.dusk=") and not l.startswith("ench.tier.lumen="))
    r3 = M2.update(nol)
    K.check(r3 is not None and int(r3[1]) == 2 and _props(str(r3[0])).get("ench.tier.dusk") is None, "MIG a file without the dusk / lumen lines: only the two present move (absent = the default 5)")
    # the run path on a scratch folder (History first, change-log rows, the Properties check)
    base = os.path.join(scratch, "mig", "Skyy_SkyyCollections")
    os.makedirs(base)
    open(os.path.join(base, "collections.properties"), "w", encoding="latin-1", newline="\n").write(old_reg)
    open(os.path.join(base, "config.properties"), "w", encoding="latin-1", newline="\n").write(old_cfg)
    P = JClass("java.nio.file.Paths").get(base)
    m1, m2 = str(M1.run(P)), str(M2.run(P))
    K.check("4 curve line(s)" in m1 and "4 ench.tier line(s)" in m2, "MIG run: %s | %s" % (m1[:100], m2[:100]))
    lg = open(os.path.join(base, "config-changes.log"), encoding="utf-8").read()
    K.eq(lg.count("\tSkyyCollections 0.2.31\t-\tupdate\t"), 8, "MIG one change-log row per moved line")
    hist = [os.path.join(r_, f_) for r_, _d, fs in os.walk(os.path.join(base, "config-history")) for f_ in fs]
    K.check(any(open(h, "rb").read() == old_reg.encode("latin-1") for h in hist) and any(open(h, "rb").read() == old_cfg.encode("latin-1") for h in hist),
            "MIG both old files kept in config-history")
    s1 = snapd(base)
    K.check(str(M1.run(P)) == "" and str(M2.run(P)) == "" and snapd(base) == s1, "MIG a second start changes nothing")
    # fix round 2 (critic): a kept admin curve -> the INFO line says curve.scale multiplies it + how to switch it off; tiers can fall
    base2 = os.path.join(scratch, "mig2", "Skyy_SkyyCollections")
    os.makedirs(base2)
    open(os.path.join(base2, "collections.properties"), "w", encoding="latin-1", newline="\n").write(hand)
    mh = str(M1.run(JClass("java.nio.file.Paths").get(base2)))
    K.check("3 curve line(s)" in mh and "curve.R=20,40,80" in mh and "curve.scale=Mining:100" in mh and "a tier can fall" in mh, "MIG a kept curve: the INFO line names curve.scale: %s" % mh[:240])
    K.check("curve.scale=Mining:100" not in m1 and "a tier can fall" in m1, "MIG no kept curve: no curve.scale note, the tiers-can-fall line stays")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Reg = boot(home)
    P = JClass("java.nio.file.Paths").get(home)
    s0 = snapd(home)
    po = dict((f, _props(open(os.path.join(home, f), encoding="latin-1").read())) for f in ("collections.properties", "config.properties"))
    lgp = os.path.join(home, "config-changes.log")
    log0 = open(lgp, "rb").read() if os.path.isfile(lgp) else b""
    msgs = []
    for cn in ("CollBagMigrate", "CollBypassMig", "CollCoinMig", "CollEnch28Mig", "CollP6Mig", "CollP6EnchMig"):
        msgs.append(str(JClass(PKG + cn).run(P)))
    Reg.loadAll()
    s1 = snapd(home)
    pn = dict((f, _props(open(os.path.join(home, f), encoding="latin-1").read())) for f in ("collections.properties", "config.properties"))
    ch = sorted("%s:%s" % (f, k) for f in pn for k in set(po[f]) | set(pn[f]) if po[f].get(k) != pn[f].get(k))
    allowed = set(["collections.properties:curve." + k for k in "BSRE"] + ["config.properties:ench.tier." + a for a in ("dusk", "azurvane", "cinder", "lumen")])
    K.check(set(ch) <= allowed and "collections.properties:curve.S" in ch, "LIVE start 1 changes only the planned keys: %s (msgs %s)" % (ch, [m[:90] for m in msgs if m]))
    K.notes.append("LIVE start 1 changed %s; messages %s" % (ch, [m for m in msgs if m]))
    lg = open(lgp, "rb").read()[len(log0):].decode("utf-8")
    K.eq(lg.count("\tSkyyCollections 0.2.31\t-\tupdate\t"), len(ch), "LIVE one change-log row per changed line")
    hist = [os.path.join(r_, f_) for r_, _d, fs in os.walk(os.path.join(home, "config-history")) for f_ in fs]
    K.check(any(open(h, "rb").read() == s0["collections.properties"] for h in hist), "LIVE the old collections.properties kept in config-history")
    for cn in ("CollBagMigrate", "CollBypassMig", "CollCoinMig", "CollEnch28Mig", "CollP6Mig", "CollP6EnchMig"):
        JClass(PKG + cn).run(P)
    Reg.loadAll()
    s2 = snapd(home)
    K.check(s1 == s2, "LIVE start 2 changes no file: %s" % sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k))[:6])
    R = Reg.D
    ids = [str(x) for x in R.id]
    K.check(int(Reg.threshold(R, ids.index("Copper"), 2)) == 40 and int(Reg.threshold(R, ids.index("OakLog"), 2)) == 70, "LIVE the live registry reads the P6 curves + curve.scale (Copper II 40, Oak II 70)")
    St = JClass(PKG + "CollStore")
    cdir = os.path.join(home, "counts")
    rows = []
    for f in sorted(os.listdir(cdir)) if os.path.isdir(cdir) else []:
        if not f.endswith(".properties"):
            continue
        d = St.dataK(f[:-11])
        if d is None:
            continue
        up = [(ids[c], int(St.meta(d, "_paid." + ids[c])), int(St.countTier(d, R, c))) for c in range(int(R.n)) if int(St.countTier(d, R, c)) > int(St.meta(d, "_paid." + ids[c]))]
        rows.append("%s: %d collections gain tiers (e.g. %s)" % (f[:8], len(up), up[:4]))
    K.notes.append("LIVE the one-time catch-up per profile (paid on the next credit): " + "; ".join(rows))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyCollections", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("p6", run_p6), ("mig", run_mig), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
