"""Harness for SkyyCollections 0.2.32 (Balance P7: tier coins by item tier on the coin curve, tier.coinsByTier, CollP7Mig;
tools/collections_0_2_32_patch.py). Build first:
    python tools/collections_0_2_32_patch.py && python SkyyCollections/build_skyycollections_0.2.32.py
    python SkyyCollections/test_skyycollections_0.2.32.py [--jar <SkyyCollections-0.2.32.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  S    static   the patch re-runs to identical bytes; line endings kept; one new class, no new command / system; setup order
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.31 -> 0.2.32 (EXPECT below)
  P7   EXECUTED on a fresh folder: CollReg.loadAll -> the fresh collections.properties (marker + tier.coinsByTier=true); CollReg.coinsAt of every
       collection and tier = tools/balance_model.py p7_coll_coins (Copper V 190, Iron V 339, Chromium V 12,120, Titanium V 164,000, untagged
       Cobblestone V 400; a Combat collection's x2 on III / V / VII / last after it); CollReg.curveOwn = the model's curve at every level;
       coins:fn:curve on the bridge (a stand-in) is used, junk -> the own copy; tier.coinsByTier=false = the flat 0.2.31 numbers; settle on a
       1,000-Copper profile paid to II pays the CURVED coins of III .. VII once, a second settle 0
  MIG  CollP7Mig.update on the REAL 0.2.31 default text (the old jar's regText: marker only), an admin tier.coins (tier.coinsByTier=false
       appended + named), a file that already has tier.coinsByTier (kept), CRLF, the marker present (null); the run path (History first, one
       change-log row for the appended key) on a scratch folder, a second run nothing
  LIVE every setup migration + CollReg.loadAll on a scratch COPY of the live Skyy_SkyyCollections (NewBetaTest), twice: start 1 changes only
       0.2.31's planned keys (the live copy has not run 0.2.31 yet) + the P7 marker, the second start changes nothing; the live tier.coins is
       the default -> tier.coinsByTier stays absent (= true)
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD_VERSION = "0.2.32", "0.2.31"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)
GEN = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyycollections_%s.py" % OLD_VERSION)
PATCH = os.path.join(ROOT, "tools", "collections_0_2_32_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp7", "coll")))
PKG = "com.skyy.collections."
EXPECT = {"CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
          "CollReg": ["+f CB_ID", "+f CB_LV", "+f CV_F", "+f CV_LV", "+m coinLv", "+m curve", "+m curveOwn", "~<clinit>", "~m coinsAt", "~m parseReg", "~m regText"],
          "RegData": ["+f coinTier", "~c "],
          "SkyyCollectionsPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["CollP7Mig"]
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
MARK_ID = "Balance P7 economy (SkyyCollections 0.2.32)"
T31 = None


def tmod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    old = sys.argv
    sys.argv = [old[0]]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = old
    return m


def t31():
    global T31
    if T31 is None:
        T31 = tmod(os.path.join(HERE, "test_skyycollections_0.2.31.py"), "tco0231")
        T31.OLD_JAR = OLD_JAR          # its _old_text reads the PREVIOUS jar = 0.2.31 here
    return T31


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.32"') == 1 and '[SkyyCollections] 0.2.32 ready (' in g and '[SkyyCollections] 0.2.31 ready' not in g, "S version + ready line")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count(' = K("') - o.count(' = K("'), 1, "S one new class")
    su = g[g.index("public void setup() {"):]
    K.check(su.index("CollP6Mig.run(base)") < su.index("CollP6EnchMig.run(base)") < su.index("CollP7Mig.run(base)") < su.index("CollReg.loadAll()"),
            "S setup: ... CollP6Mig -> CollP6EnchMig -> CollP7Mig -> loadAll")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_p7(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    bm = tmod(os.path.join(ROOT, "tools", "balance_model.py"), "bm_p7")
    import tier_tags as TT
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    base = os.path.join(scratch, "p7", "Skyy_SkyyCollections")
    os.makedirs(os.path.join(base, "counts"))
    Reg = t31().boot(base)
    Reg.loadAll()
    txt = open(os.path.join(base, "collections.properties"), encoding="latin-1").read()
    K.check(MARK_ID in txt and "\ntier.coinsByTier=true\n" in txt, "P7 the fresh registry file: the marker + tier.coinsByTier=true")
    R = Reg.D
    ids = [str(x) for x in R.id]
    ix = dict((c, i) for i, c in enumerate(ids))
    worst = max(abs(float(Reg.curveOwn(lv)) / bm.p7_curve_from_text(bm.P7_CURVE_TEXT, lv) - 1) for lv in range(0, 201))
    K.check(worst < 1e-9, "CURVE the built-in copy = the model's coin curve at every level (worst %.1e)" % worst)
    for cid, want in (("Copper", 190), ("Iron", 339), ("Chromium", 12120), ("Titanium", 164000), ("Cobblestone", 400), ("Wheat", 190), ("OakLog", 190)):
        K.eq(int(Reg.coinsAt(R, ix[cid], 5)), want, "COINS %s tier V" % cid)
    # every collection x every tier = the model (tagged: x curve(band start of the lowest tagged item), untagged x1, Combat x2 on 3/5/7/last)
    tag = {}
    import ast
    for c in ids:
        tag[c] = None
    bad = []
    for c in ids:
        lv = int(Reg.coinLv(c))
        tier = None
        if lv > 0:
            tier = bm.BAND.index(lv) + 1
        for t in range(1, int(Reg.maxTier(R, ix[c])) + 1):
            k = min(t, 10)
            want = bm.p7_coll_coins(k, tier)
            cat = str(R.cat[ix[c]])
            got = int(Reg.coinsAt(R, ix[c], t))
            base_raw = got
            if "Combat" == str(JClass(PKG + "CollReg").CATS[R.cat[ix[c]]]) and (t in (3, 5, 7) or t == int(Reg.maxTier(R, ix[c]))):
                import math as _m
                want = int(_m.floor(want * float(R.combatMult) + 0.5))
            extra = JClass(PKG + "CollReg").REWARDS.get(c.lower() + "." + str(t))
            if extra is not None and any(str(x).startswith("coins:") for x in extra):
                continue
            if got != want:
                bad.append((c, t, got, want))
    K.check(not bad, "COINS every collection / tier = tools/balance_model.py p7_coll_coins (+ Combat x2): %d off %s" % (len(bad), bad[:6]))
    tagged = [c for c in ids if int(Reg.coinLv(c)) > 0]
    K.check(len(tagged) >= 55 and int(Reg.coinLv("copper")) == 1 and int(Reg.coinLv("Titanium")) == 88 and int(Reg.coinLv("Cobblestone")) == 0,
            "COINS %d tagged collections (Copper Lv 1, Titanium Lv 88, Cobblestone untagged)" % len(tagged))

    @JImplements("java.util.function.Function")
    class Cv(object):
        def __init__(self, a):
            self.a = a

        @JOverride
        def apply(self, x):
            return self.a
    br.put("coins:fn:curve", Cv(JClass("java.lang.Double")(2.0)))
    K.eq(int(Reg.coinsAt(R, ix["Copper"], 5)), 800, "BRIDGE SkyyCoins' coins:fn:curve is used (stand-in x2.0)")
    br.put("coins:fn:curve", Cv("junk"))
    K.eq(int(Reg.coinsAt(R, ix["Copper"], 5)), 190, "BRIDGE a junk answer -> the own copy")
    br.remove("coins:fn:curve")
    R.coinTier = False
    K.check(int(Reg.coinsAt(R, ix["Copper"], 5)) == 400 and int(Reg.coinsAt(R, ix["Titanium"], 5)) == 400, "SWITCH tier.coinsByTier false = the flat 0.2.31 numbers")
    R.coinTier = True
    # the file line read back
    open(os.path.join(base, "collections.properties"), "w", encoding="latin-1", newline="\n").write(txt.replace("tier.coinsByTier=true", "tier.coinsByTier=false"))
    Reg.loadAll()
    K.check(not bool(Reg.D.coinTier) and int(Reg.coinsAt(Reg.D, ix["Copper"], 5)) == 400, "SWITCH a false line in the file is read")
    open(os.path.join(base, "collections.properties"), "w", encoding="latin-1", newline="\n").write(txt)
    Reg.loadAll()
    R = Reg.D
    # settle: the curved coins once
    paid = {"coins": []}

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
    want_c = [int(Reg.coinsAt(R, c, t_)) for t_ in range(3, ct + 1)]
    K.check(ct >= 5 and r1[0] == sum(want_c) and paid["coins"] == [x for x in want_c if x > 0] and want_c[2] == 190,
            "SETTLE III .. %d pay the curved coins once: %s (got %s)" % (ct, want_c, paid["coins"]))
    n0 = len(paid["coins"])
    r2 = [int(x) for x in Rw.settle(d, R, c, U, key)]
    K.check(r2[0] == 0 and len(paid["coins"]) == n0, "SETTLE a second settle pays 0 - tiers already paid stay paid")
    K.save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    M = JClass(PKG + "CollP7Mig")
    old = t31()._old_text("regText")
    K.check("tier.coins=25,50,100,200,400,750,1500,3000,6000,12500" in old and MARK_ID not in old, "MIG the 0.2.31 default text (old jar)")
    r = M.update(old)
    K.check(r is not None and not bool(r[1]) and str(r[0]) == old + ("" if old.endswith("\n") else "\n") + str(M.MARK) + "\n", "MIG the 0.2.31 default: the marker only")
    K.eq(t31()._props(str(r[0])), t31()._props(old), "MIG the 0.2.31 default: no key changes")
    adm = old.replace("tier.coins=25,50,100,200,400,750,1500,3000,6000,12500", "tier.coins=10,20,30")
    r = M.update(adm)
    K.check(r is not None and bool(r[1]) and str(r[0]).endswith(str(M.MARK) + "\ntier.coinsByTier=false\n") and "10,20,30" in str(r[2]), "MIG an admin's tier.coins: tier.coinsByTier=false appended + named")
    pa, pb = t31()._props(adm), t31()._props(str(r[0]))
    K.check(set(pb) - set(pa) == {"tier.coinsByTier"} and all(pa[k] == pb[k] for k in pa), "MIG only tier.coinsByTier is added")
    has = adm + "tier.coinsByTier=true\n"
    r = M.update(has)
    K.check(r is not None and not bool(r[1]) and "already" in str(r[2]), "MIG a file that already has tier.coinsByTier keeps it")
    K.check(M.update(str(r[0])) is None, "MIG the marker present: nothing")
    crlf = adm.replace("\n", "\r\n")
    r = M.update(crlf)
    K.check(r is not None and str(r[0]).replace("\r\n", "") .count("\n") == 0 and str(r[0]).endswith("tier.coinsByTier=false\r\n"), "MIG CRLF kept")
    # the run path on a scratch folder (the kit's History + change log)
    base = os.path.join(scratch, "mig", "Skyy_SkyyCollections")
    os.makedirs(os.path.join(base, "counts"))
    Reg = t31().boot(base)
    Reg.loadAll()          # writes the fresh files (marker -> the update does nothing), the kit files list
    K.eq(str(M.run(JClass("java.nio.file.Paths").get(base))), "", "RUN a fresh 0.2.32 file: nothing")
    f = os.path.join(base, "collections.properties")
    open(f, "wb").write(adm.encode("latin-1"))
    msg = str(M.run(JClass("java.nio.file.Paths").get(base)))
    t1 = open(f, "rb").read().decode("latin-1")
    K.check("keeps it paying as written" in msg and t1.endswith("tier.coinsByTier=false\n"), "RUN an admin file: appended: %s" % msg[:100])
    hist = [os.path.join(r_, f_) for r_, _d, fs in os.walk(os.path.join(base, "config-history")) for f_ in fs]
    K.check(any(open(h, "rb").read() == adm.encode("latin-1") for h in hist), "RUN History holds the old file")
    lg = open(os.path.join(base, "config-changes.log"), encoding="utf-8").read() if os.path.isfile(os.path.join(base, "config-changes.log")) else ""
    K.check("SkyyCollections 0.2.32\t-\tupdate\ttier.coinsByTier\ttrue\tfalse\tok" in lg, "RUN one change-log row (Undo)")
    K.eq(str(M.run(JClass("java.nio.file.Paths").get(base))), "", "RUN a second start does nothing")
    K.eq(open(f, "rb").read().decode("latin-1"), t1, "RUN the file is unchanged by the second start")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Reg = t31().boot(home)
    P = JClass("java.nio.file.Paths").get(home)
    s0 = t31().snapd(home)
    po = dict((f, t31()._props(open(os.path.join(home, f), encoding="latin-1").read())) for f in ("collections.properties", "config.properties"))
    MIGS = ("CollBagMigrate", "CollBypassMig", "CollCoinMig", "CollEnch28Mig", "CollP6Mig", "CollP6EnchMig", "CollP7Mig")
    msgs = [str(JClass(PKG + cn).run(P)) for cn in MIGS]
    Reg.loadAll()
    s1 = t31().snapd(home)
    pn = dict((f, t31()._props(open(os.path.join(home, f), encoding="latin-1").read())) for f in ("collections.properties", "config.properties"))
    ch = sorted("%s:%s" % (f, k) for f in pn for k in set(po[f]) | set(pn[f]) if po[f].get(k) != pn[f].get(k))
    allowed = set(["collections.properties:curve." + k for k in "BSRE"] + ["config.properties:ench.tier." + a for a in ("dusk", "azurvane", "cinder", "lumen")])
    K.check(set(ch) <= allowed, "LIVE start 1 changes only 0.2.31's planned keys (nothing for P7 - the live tier.coins is the default): %s" % ch)
    K.check(MARK_ID in open(os.path.join(home, "collections.properties"), encoding="latin-1").read() and "tier.coinsByTier" not in pn["collections.properties"],
            "LIVE the P7 marker written, tier.coinsByTier absent (= on)")
    K.notes.append("LIVE start 1 changed %s; P7 message: %s" % (ch, msgs[-1][:160]))
    for cn in MIGS:
        JClass(PKG + cn).run(P)
    Reg.loadAll()
    s2 = t31().snapd(home)
    K.check(s1 == s2, "LIVE start 2 changes no file: %s" % sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k))[:6])
    R = Reg.D
    ids = [str(x) for x in R.id]
    K.check(int(Reg.coinsAt(R, ids.index("Copper"), 5)) == 190 and bool(R.coinTier), "LIVE the live registry pays Copper V 190")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyCollections", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("p7", run_p7), ("mig", run_mig), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
