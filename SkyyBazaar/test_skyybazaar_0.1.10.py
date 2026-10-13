"""Harness for SkyyBazaar 0.1.10 (the Enchanted materials are products; tools/bazaar_0_1_10_patch.py).
Build first: python tools/bazaar_0_1_10_patch.py && python SkyyBazaar/build_skyybazaar_0.1.10.py

    python SkyyBazaar/test_skyybazaar_0.1.10.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.9 -> 0.1.10: exactly the listed members differ
  X  exec     EVERY NEW PATH, executed:
              FRESH install: 0.1.10 seeds every product + the 19 Enchanted ones, each in its Void tab (Mining / Foraging / Farming =
              tools/skyyench.py), AUTO (processed) and priced = the build's seed (100 x the input's raw value x 1.2), quotes buy > sell;
              every 0.1.9 product quotes the same; the PREMIUM: reprice at 0 % / 22 % moves the Enchanted price to 100 x raw x 1.00 / 1.22
              (never stacked on the ingot premium: Enchanted Iron = 100 x the iron bar's raw value), buy -> compress -> sell never pays
              at any premium 0..22 (sell(Enchanted) < 100 x buy(input), every input candidate).
              THE ONE-TIME UPDATE on a 0.1.9 folder (0.1.9 started there first, trades made): history copy = the old bytes; products
              .properties = the old bytes + exactly the 19 seed lines (LF / CRLF / no final newline / an admin Enchanted line kept, not
              doubled); pricing.properties keeps its bytes + the marker migrated.0.1.10 (and the 0.1.9 one); trades.log summary + one line
              per product with its undo; every old product's factor / quote = 0.1.9's. RUN ONCE: a second start changes nothing;
              writeModes keeps both markers. ROLLBACK: 0.1.9 on the migrated folder loads every product and quotes the old ones as before.
              No migrated.0.1.4 marker = no update.
  D  live     start twice on a scratch COPY of the live Skyy_SkyyBazaar with 0.1.9 and 0.1.10: the first start appends the 19 lines once
              (history copy verified), the second changes nothing; every old product's factor and quote = 0.1.9's
  AA engine-access audit
Scratch: tools/dev/scratch/ench01/bazaar (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyench as EN

VERSION = "0.1.10"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.1.9.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ench01", "bazaar")))
PKG = "com.skyy.bazaar."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyBazaar")
ENCH = list(EN.IDS)
EXPECT = {
    # ~init: the generated PROC_SPEC / SEED constants (inlined String literals) gained the 19 Enchanted entries
    "Catalog": ["+f M110_LOG", "+f MIGRATED110", "+f NEW0110", "+m migrate110", "~<clinit>", "~m init", "~m loadModes", "~m writeModes"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~m header"],
    "SkyyBazaarPlugin": ["~m setup"],
}
ADDED = []
SEED_PY = {}   # the build's seed prices (read from the build output's PROC table at runtime: Catalog.SEED lines)


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


class Bz(object):
    """one jar's Market / Catalog / BzCfg in its own loader, started on folder d like SkyyBazaarPlugin.setup() (data steps);
    v10 = run 0.1.10's migrate110 (only the new jar has it)"""

    def __init__(self, jar, d, v10=True):
        from jpype import JClass
        self.L = loader_for(jar)
        g = lambda n: JClass(PKG + n, loader=self.L)
        self.M, self.C, self.Cfg, self.U = g("Market"), g("Catalog"), g("BzCfg"), g("BzUtil")
        P = JClass("java.nio.file.Paths")
        dp = P.get(d)
        os.makedirs(d, exist_ok=True)
        self.C.FILE = dp.resolve("products.properties")
        self.C.PFILE = dp.resolve("pricing.properties")
        self.M.FILE = dp.resolve("market.properties")
        self.M.LOGFILE = dp.resolve("trades.log")
        self.Cfg.load(dp)
        self.C.migrate()
        self.C.migrate14()
        self.mig19 = self.C.migrate19()
        self.mig110 = self.C.migrate110() if v10 else None
        self.n = int(self.C.load())
        self.M.load()
        self.C.reprice()
        self.M.publishAll()
        self.C.flushIfDirty()
        if self.mig19 is not None:
            for i in range(self.C.M19_LOG.size()):
                self.M.log(self.C.M19_LOG.get(i))
            self.C.M19_LOG.clear()
        if v10 and self.mig110 is not None:
            for i in range(self.C.M110_LOG.size()):
                self.M.log(self.C.M110_LOG.get(i))
            self.C.M110_LOG.clear()
        self.M.flush()
        self.ids = [str(p.id) for p in self.C.all()]

    def state(self, ids=None):
        return {i: (float(self.M.factor(i)), int(self.M.quote(i, 1, True)), int(self.M.quote(i, 1, False))) for i in (ids or self.ids)}

    def tabs(self, pid):
        return [str(x) for x in self.C.tabsOf(self.C.get(pid))]


def rb(p):
    return open(p, "rb").read() if os.path.exists(p) else None


def rb(p):
    return open(p, "rb").read() if os.path.exists(p) else None


def seed_prices(C):
    out = {}
    for l in C.SEED:
        k, v = str(l).split("=", 1)
        out[k] = float(v.split(",")[1])
    return out


def run_exec(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    # ---- a fresh install
    df = os.path.join(scratch, "fresh10")
    f10 = Bz(jar, df)
    f9 = Bz(OLD_JAR, os.path.join(scratch, "fresh9"), v10=False)
    K.check(all(e in f10.ids for e in ENCH) and f10.n == f9.n + 19, "X fresh: 0.1.10 seeds every product + the 19 Enchanted (%d vs %d)" % (f10.n, f9.n))
    seed = seed_prices(f10.C)
    for e in ENCH:
        p = f10.C.get(e)
        K.eq(f10.tabs(e), [EN.cat_of(e)], "X fresh: %s shows in %s only" % (e, EN.cat_of(e)))
        K.eq(str(p.cat), EN.cat_of(e), "X fresh: %s file category" % e)
        K.check(bool(f10.C.AUTO.contains(e)), "X fresh: %s is a processed (auto) good" % e)
        K.check(abs(float(p.base) - seed[e]) < 1e-6, "X fresh: %s base %s = the build's seed %s" % (e, p.base, seed[e]))
        b, s_ = int(f10.M.quote(e, 1, True)), int(f10.M.quote(e, 1, False))
        K.check(b > s_ > 0, "X fresh: %s quotes buy %d > sell %d > 0" % (e, b, s_))
    base = lambda i: float(f10.C.get(i).base)
    K.check(abs(base("Skyy_Ench_Cobblestone") - 100 * base("Rock_Stone_Cobble") * 1.2) < 0.011, "X price: Enchanted Cobblestone = 100 x cobble x 1.2 (%s)" % base("Skyy_Ench_Cobblestone"))
    K.check(abs(base("Skyy_Ench_Oak") - 100 * base("Wood_Oak_Trunk") * 1.2) < 0.011, "X price: Enchanted Oak = 100 x oak x 1.2")
    K.check(abs(base("Skyy_Ench_Wheat") - 100 * base("Plant_Crop_Wheat_Item") * 1.2) < 0.011, "X price: Enchanted Wheat = 100 x wheat x 1.2")
    K.check(abs(base("Skyy_Ench_Iron") - 100 * base("Ingredient_Bar_Iron")) < 1.0, "X price: Enchanted Iron Ingot = 100 iron ingots (premium not stacked: %s vs %s)" % (base("Skyy_Ench_Iron"), 100 * base("Ingredient_Bar_Iron")))
    rub = [i for i in f10.ids if i.startswith("Rubble_")]
    K.check(bool(rub) and abs(base("Skyy_Ench_Rubble") - 100 * min(base(i) for i in rub) * 1.2) < 0.011, "X price: Enchanted Rubble = 100 x the cheapest listed rubble x 1.2")
    old = list(f9.ids)
    K.check(f9.state(old) == f10.state(old), "X fresh: every 0.1.9 product quotes the same on 0.1.10")
    # ---- the premium: 0 % and 22 % (never stacked), and no buy -> compress -> sell loop at any premium
    f10.C.reprice0(0.0, 0, 0.10)
    K.check(abs(base("Skyy_Ench_Cobblestone") - 100 * base("Rock_Stone_Cobble")) < 0.011 and abs(base("Skyy_Ench_Iron") - 100 * base("Ingredient_Bar_Iron")) < 1.0,
            "X premium 0 %%: Enchanted = 100 x the input (cobble %s, iron %s)" % (base("Skyy_Ench_Cobblestone"), base("Skyy_Ench_Iron")))
    inputs = {}
    for t in EN.TABLE:
        inputs[EN.PREFIX + t[0]] = rub if t[1] == "R" else [t[2]]
    bad = []
    for prem in range(0, 23):
        f10.C.reprice0(prem / 100.0, prem, 0.10)
        for e, cand in inputs.items():
            sell = base(e) * 0.9
            buy = 100 * min(base(i) for i in cand) * 1.1
            if not sell < buy:
                bad.append((prem, e, sell, buy))
    K.eq(bad, [], "X loop: buy 100 inputs -> compress -> sell never pays at any premium 0..22 (19 x 23 cases)")
    f10.C.reprice0(0.22, 22, 0.10)
    K.check(abs(base("Skyy_Ench_Cobblestone") - 122.0) < 0.011, "X premium 22 %%: Enchanted Cobblestone 122 (%s)" % base("Skyy_Ench_Cobblestone"))
    f10.C.reprice0(0.20, 20, 0.10)
    K.check(rb(os.path.join(df, "pricing.properties")) is not None and b"migrated.0.1.10=" in rb(os.path.join(df, "pricing.properties"))
            and str(f10.mig110).startswith("MIGRATE-0.1.10 added 0 already 19"), "X fresh: the update finds every Enchanted product seeded: adds 0, writes its marker (%s)" % f10.mig110)
    # ---- the one-time update on a 0.1.9 folder (LF, CRLF, no final newline, an admin Enchanted line)
    for variant in ("lf", "crlf", "nofinal", "admin"):
        d9 = os.path.join(scratch, "m9-" + variant)
        a = Bz(OLD_JAR, d9, v10=False)
        a.M.apply("Ore_Copper", 64, True)
        a.M.apply("Wood_Oak_Trunk", 20, False)
        a.M.flush()
        pp = os.path.join(d9, "products.properties")
        raw = rb(pp)
        if variant == "crlf":
            raw = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        elif variant == "nofinal":
            raw = raw.rstrip(b"\n")
        elif variant == "admin":
            raw = raw + b"Skyy_Ench_Iron=Mining,999,Enchanted Iron Ingot\n"
        open(pp, "wb").write(raw)
        ppr = rb(os.path.join(d9, "pricing.properties"))
        tl0 = rb(os.path.join(d9, "trades.log")) or b""
        before = Bz(OLD_JAR, d9, v10=False)
        s_before = before.state([i for i in before.ids if not i.startswith(EN.PREFIX)])
        d10 = os.path.join(scratch, "m10-" + variant)
        shutil.copytree(d9, d10)
        raw10 = rb(os.path.join(d10, "products.properties"))
        ppr10 = rb(os.path.join(d10, "pricing.properties"))
        b10 = Bz(jar, d10)
        new = rb(os.path.join(d10, "products.properties"))
        nl = b"\r\n" if variant == "crlf" else b"\n"
        want_add = [e for e in ENCH if not (variant == "admin" and e == "Skyy_Ench_Iron")]
        sd = dict((str(l).split("=", 1)[0], str(l)) for l in b10.C.SEED)
        exp = raw10 + (nl if variant == "nofinal" else b"") + b"".join(sd[e].encode("utf-8") + nl for e in want_add)
        if variant == "admin":   # the admin's line stays where it is; an Enchanted product is AUTO, so its price follows its recipe (in place)
            exp = exp.replace(b"Skyy_Ench_Iron=Mining,999,Enchanted Iron Ingot\n", sd["Skyy_Ench_Iron"].encode("utf-8") + b"\n")
        K.check(new == exp, "X update (%s): products.properties = the old bytes%s + exactly %d Enchanted seed lines (%s)"
                % (variant, " + one newline" if variant == "nofinal" else "", len(want_add), "CRLF" if variant == "crlf" else "LF"))
        hd = os.path.join(d10, "config-history")
        hs = sorted(f for f in os.listdir(hd) if rb(os.path.join(hd, f)) == raw10) if os.path.isdir(hd) else []
        K.check(len(hs) == 1, "X update (%s): one verified history copy = the old products.properties" % variant)
        np_ = rb(os.path.join(d10, "pricing.properties"))
        K.check(np_.startswith(ppr10) and b"migrated.0.1.10=" in np_[len(ppr10):] and b"migrated.0.1.9=" in np_, "X update (%s): pricing.properties keeps its bytes + the marker" % variant)
        tl = (rb(os.path.join(d10, "trades.log")) or b"")[len(tl0):].decode("utf-8", "replace")
        K.check(("MIGRATE-0.1.10 added %d" % len(want_add)) in tl and tl.count("MIGRATE-0.1.10 ADDED") == len(want_add) and "undo" in tl,
                "X update (%s): trades.log: the summary + one line per added product with its undo" % variant)
        if variant == "admin":
            K.eq(new.count(b"Skyy_Ench_Iron="), 1, "X update (admin): the admin's Enchanted Iron line kept, not added twice")
        s_after = b10.state(list(s_before))
        K.check(s_after == s_before, "X update (%s): every old product's factor and quote = 0.1.9's (trades kept)" % variant)
        snap = dict((f, rb(os.path.join(d10, f))) for f in ("products.properties", "pricing.properties"))
        b10b = Bz(jar, d10)
        K.check(b10b.mig110 is None and all(rb(os.path.join(d10, f)) == v for f, v in snap.items()), "X update (%s): a second start changes nothing" % variant)
        b10b.C.writeModes(b10b.C.MIGRATED)
        pr2 = rb(os.path.join(d10, "pricing.properties"))
        K.check(b"migrated.0.1.10=" in pr2 and b"migrated.0.1.9=" in pr2, "X update (%s): writeModes (a later save) keeps both markers" % variant)
        rbd = os.path.join(scratch, "rb-" + variant)
        shutil.copytree(d10, rbd)
        o9 = Bz(OLD_JAR, rbd, v10=False)
        K.check(all(e in o9.ids for e in ENCH) and o9.state(list(s_before)) == s_before, "X rollback (%s): 0.1.9 loads the Enchanted lines and quotes every old product as before" % variant)
    dn = os.path.join(scratch, "nomark")
    os.makedirs(dn)
    open(os.path.join(dn, "products.properties"), "wb").write(b"Ore_Copper=Mining,5,Copper Ore\n")
    open(os.path.join(dn, "pricing.properties"), "wb").write(b"migrated.0.1.3=x\n")
    C10 = JClass(PKG + "Catalog", loader=loader_for(jar))
    P = JClass("java.nio.file.Paths")
    C10.FILE = P.get(dn).resolve("products.properties")
    C10.PFILE = P.get(dn).resolve("pricing.properties")
    K.check(C10.migrate110() is None and rb(os.path.join(dn, "products.properties")) == b"Ore_Copper=Mining,5,Copper Ore\n", "X: without migrated.0.1.4 the update does not run")
    K.notes.append("X: Enchanted seed prices %s" % ", ".join("%s %g" % (e[len(EN.PREFIX):], seed[e]) for e in ENCH))
    K.save()


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    base = os.path.dirname(home)
    d9 = os.path.join(base, "live9")
    shutil.copytree(home, d9)
    raw = rb(os.path.join(home, "products.properties"))
    a = Bz(OLD_JAR, d9, v10=False)
    b = Bz(jar, home)
    added = rb(os.path.join(home, "products.properties"))
    n_add = sum(1 for e in ENCH if (e + "=").encode() not in raw)
    K.check(added.startswith(raw), "D: the live products.properties keeps every byte")
    # the live folder may not have started 0.1.9 yet (deployed, no game start since): its 9 crystal lines (migrate19) come first then
    n_cr = sum(1 for c in ("Ingredient_Crystal_Blue", "Ingredient_Crystal_Cyan", "Ingredient_Crystal_Green", "Ingredient_Crystal_Pink",
                           "Ingredient_Crystal_Purple", "Ingredient_Crystal_Red", "Ingredient_Crystal_White", "Ingredient_Crystal_Yellow",
                           "Ingredient_Crystal_Void") if (c + "=").encode() not in raw)
    if n_cr:
        K.notes.append("D: the live copy had not run 0.1.9 yet - %d crystal lines (migrate19) appended first" % n_cr)
    K.check(added.count(b"\n") - raw.count(b"\n") == n_add + n_cr + (0 if raw.endswith(b"\n") else 1) and all((e + "=").encode() in added for e in ENCH)
            and added.rstrip(b"\n").split(b"\n")[-19:] == [("%s=" % e).encode() + l.split(b"=", 1)[1] for e, l in zip(ENCH, added.rstrip(b"\n").split(b"\n")[-19:])],
            "D: exactly %d Enchanted lines appended (%d new lines, final newline %s)" % (n_add, added.count(b"\n") - raw.count(b"\n"), raw.endswith(b"\n")))
    hd = os.path.join(home, "config-history")
    hs = [f for f in os.listdir(hd) if f.startswith("Skyy_SkyyBazaar~products.properties") and rb(os.path.join(hd, f)) == raw] if os.path.isdir(hd) else []
    K.check(n_add == 0 or len(hs) == 1, "D: one verified history copy of the live file")
    ids = [i for i in a.ids if not i.startswith(EN.PREFIX)]
    sa, sb = a.state(ids), b.state(ids)
    K.check(all(abs(sa[i][0] - sb[i][0]) < 1e-9 and sa[i][1:] == sb[i][1:] for i in ids), "D: every live product's factor and quote = 0.1.9's")
    snap = HK.tree_hash(home)
    b2 = Bz(jar, home)
    K.check(b2.mig110 is None and HK.tree_hash(home).get("products.properties") == snap.get("products.properties"), "D: the second start appends nothing")
    K.check(all(b2.tabs(e) == [EN.cat_of(e)] for e in ENCH), "D: live Enchanted products show in their Void tab")
    K.notes.append("D: %d live products, %d Enchanted lines appended, Enchanted Iron %s coins" % (len(a.ids), n_add, b2.C.get("Skyy_Ench_Iron").base))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyBazaar"))
