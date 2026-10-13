"""Harness for SkyyBazaar 0.1.9 (Bags v2 with SkyySacks 0.8.0: the Fishing tab, the crystal shards in Mining; tools/bazaar_0_1_9_patch.py).
Build first: python tools/bazaar_0_1_9_patch.py && python SkyyBazaar/build_skyybazaar_0.1.9.py

    python SkyyBazaar/test_skyybazaar_0.1.9.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.8 -> 0.1.9: exactly the listed members differ
  X  exec     EVERY NEW PATH, executed:
              FRESH install: 0.1.9 seeds every product (the 9 crystal shards in Mining, the fish in Fishing), the tabs are Mining /
              Foraging / Farming / Fishing / Combat / Smithing (6 = the page's maximum), Farming holds no fish, every old product's quote = 0.1.8's.
              THE ONE-TIME UPDATE on a 0.1.8 folder (0.1.8 started there first, trades made): a verified history copy in config-history =
              the old bytes; products.properties = the old bytes + exactly the 9 crystal seed lines (LF and a CRLF file: its own line ending;
              a file without a final newline gets one first); an already-listed crystal (admin) is not added twice; pricing.properties keeps
              its bytes + the marker; trades.log gets the summary + one line per product with its undo; the fish lines still say Farming
              but show in Fishing only; an admin's own category (Seafood) still adds its tab; every factor / quote of an old product = 0.1.8's.
              RUN ONCE: a second start changes no file; writeModes keeps the marker (a later save). ROLLBACK: 0.1.8 on the migrated folder
              loads every product (the crystals in their file tab Mining) and quotes every old product as before.
              No pricing.properties (a fresh 0.1.8-less folder) / no migrated.0.1.4 = no update.
  D  live     start twice on a scratch COPY of the live Skyy_SkyyBazaar with 0.1.8 and 0.1.9: 0.1.9's first start appends the crystals once
              (history copy verified), the second changes nothing; every old product's factor and quote = 0.1.8's
  AA engine-access audit
Scratch: tools/dev/scratch/void080/bazaar (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.9"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.1.8.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "void080", "bazaar")))
PKG = "com.skyy.bazaar."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyBazaar")
CRYSTALS = ["Ingredient_Crystal_Blue", "Ingredient_Crystal_Cyan", "Ingredient_Crystal_Green", "Ingredient_Crystal_Pink", "Ingredient_Crystal_Purple",
            "Ingredient_Crystal_Red", "Ingredient_Crystal_White", "Ingredient_Crystal_Yellow", "Ingredient_Crystal_Void"]
TABS6 = ["Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing"]
# reviewed: BzPage / Trader = the "the Void" texts; Catalog = OLDBAG + migrate19 + the marker (+ HEADER / seed constants inlined in
# migrate / writeLines / <clinit>); CfgFn / CfgRows = the version text; SkyyBazaarPlugin.setup = migrate19 + its trades.log lines
EXPECT = {
    "BzPage": ["~m handleDataEvent", "~m infoColor", "~m render"],   # fix round 2: infoColor = the "Void bags" refusal colour
    "Catalog": ["+f M19_LOG", "+f MIGRATED19", "+f NEW019", "+f OLDBAG", "+f OLDBAG_ID", "+f OLDBAG_TAB", "+m migrate19", "~<clinit>", "~m init",
                "~m loadModes", "~m migrate", "~m tabsOf", "~m writeLines", "~m writeModes"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~m header"],
    "SkyyBazaarPlugin": ["~m setup"],
    "Trader": ["~m buy0", "~m sell0", "~m sellInventory"],   # fix round 2: buy0 / sell0 = the "Void bags" refusal text
}
ADDED = []


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


class Bz(object):
    """one jar's Market / Catalog / BzCfg in its own loader, started on folder d like SkyyBazaarPlugin.setup() (data steps)"""

    def __init__(self, jar, d, new=True):
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
        self.mig19 = None
        if new:
            self.mig19 = self.C.migrate19()
        self.n = int(self.C.load())
        self.M.load()
        self.C.reprice()
        self.M.publishAll()
        self.C.flushIfDirty()
        if new and self.mig19 is not None:
            for i in range(self.C.M19_LOG.size()):
                self.M.log(self.C.M19_LOG.get(i))
            self.C.M19_LOG.clear()
        self.M.flush()
        self.ids = [str(p.id) for p in self.C.all()]

    def state(self, ids=None):
        return {i: (float(self.M.factor(i)), int(self.M.quote(i, 1, True)), int(self.M.quote(i, 1, False))) for i in (ids or self.ids)}

    def tabs(self, pid):
        return [str(x) for x in self.C.tabsOf(self.C.get(pid))]


def rb(p):
    return open(p, "rb").read() if os.path.exists(p) else None


def run_exec(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    # ---- a fresh install
    df = os.path.join(scratch, "fresh9")
    f9 = Bz(jar, df)
    f8 = Bz(OLD_JAR, os.path.join(scratch, "fresh8"), new=False)
    K.check(all(c in f9.ids for c in CRYSTALS) and f9.n == f8.n + 9, "X fresh: 0.1.9 seeds every product + the 9 crystals (%d vs %d)" % (f9.n, f8.n))
    cats = [str(x) for x in f9.C.categories()]
    K.eq(cats, TABS6, "X fresh: the tabs are the six Void categories")
    fish = [i for i in f9.ids if i.startswith("Fish_") or i.startswith("Food_Fish_Raw")]
    K.check(len(fish) >= 10 and all(f9.tabs(i) == ["Fishing"] for i in fish), "X fresh: every fish product shows in Fishing only (%d)" % len(fish))
    farm = [str(p.id) for p in f9.C.inCat("Farming")]
    K.check(not any(i in fish for i in farm) and len(farm) > 50, "X fresh: Farming holds no fish")
    K.check(all(f9.tabs(c) == ["Mining"] for c in CRYSTALS) and all(str(f9.C.get(c).cat) == "Mining" for c in CRYSTALS), "X fresh: the crystals are Mining products")
    old = [i for i in f8.ids]
    s8, s9 = f8.state(old), f9.state(old)
    K.check(s8 == s9, "X fresh: every 0.1.8 product quotes the same on 0.1.9")
    import zipfile
    with zipfile.ZipFile(jar) as zj:
        trb, pgb = zj.read("com/skyy/bazaar/Trader.class"), zj.read("com/skyy/bazaar/BzPage.class")
    K.check(b"Void bags (the Pocket Dimension, old Magic Bags) can never be bought or sold" in trb and b"Magic Bags can never" not in trb
            and b"Void bags" in pgb and b"Magic Bags" not in pgb,
            "X (fix round 2): the locked-item refusal says 'Void bags (the Pocket Dimension, old Magic Bags)' and keeps its red colour")
    K.check(rb(os.path.join(df, "pricing.properties")) is not None and b"migrated.0.1.9=" in rb(os.path.join(df, "pricing.properties"))
            and str(f9.mig19).startswith("MIGRATE-0.1.9 added 0 already 9"), "X fresh: the update finds every crystal already seeded: adds 0, writes its marker (%s)" % f9.mig19)
    # ---- the one-time update on a 0.1.8 folder (LF, CRLF, no final newline, an admin crystal line, an admin fish category)
    for variant in ("lf", "crlf", "nofinal", "admin"):
        d8 = os.path.join(scratch, "m8-" + variant)
        a = Bz(OLD_JAR, d8, new=False)
        a.M.apply("Ore_Copper", 64, True)
        a.M.apply("Fish_Bluegill_Item", 20, False)
        a.M.flush()
        pp = os.path.join(d8, "products.properties")
        raw = rb(pp)
        if variant == "crlf":
            raw = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        elif variant == "nofinal":
            raw = raw.rstrip(b"\n")
        elif variant == "admin":
            raw = raw + b"Ingredient_Crystal_Red=Mining,99,Red Crystal Shards\n"
            raw = raw.replace(b"Fish_Catfish_Item=Farming,", b"Fish_Catfish_Item=Seafood,")
        open(pp, "wb").write(raw)
        ppr = rb(os.path.join(d8, "pricing.properties"))
        tl0 = rb(os.path.join(d8, "trades.log")) or b""
        before = Bz(OLD_JAR, d8, new=False)
        s_before = before.state(before.ids)
        d9 = os.path.join(scratch, "m9-" + variant)
        shutil.copytree(d8, d9)
        raw9 = rb(os.path.join(d9, "products.properties"))
        b9 = Bz(jar, d9)
        new = rb(os.path.join(d9, "products.properties"))
        nl = b"\r\n" if variant == "crlf" else b"\n"
        want_add = [c for c in CRYSTALS if not (variant == "admin" and c == "Ingredient_Crystal_Red")]
        seed = dict((str(l).split("=", 1)[0], str(l)) for l in b9.C.SEED)
        exp = raw9 + (nl if variant == "nofinal" else b"") + b"".join(seed[c].encode("utf-8") + nl for c in want_add)
        K.check(new == exp, "X update (%s): products.properties = the old bytes%s + exactly %d crystal seed lines (%s line endings)"
                % (variant, " + one newline" if variant == "nofinal" else "", len(want_add), "CRLF" if variant == "crlf" else "LF"))
        hd = os.path.join(d9, "config-history")
        hs = sorted(os.listdir(hd)) if os.path.isdir(hd) else []
        K.check(len(hs) == 1 and rb(os.path.join(hd, hs[0])) == raw9, "X update (%s): one verified history copy = the old products.properties" % variant)
        np_ = rb(os.path.join(d9, "pricing.properties"))
        K.check(np_.startswith(ppr) and b"migrated.0.1.9=" in np_[len(ppr):], "X update (%s): pricing.properties keeps its bytes + the marker" % variant)
        tl = (rb(os.path.join(d9, "trades.log")) or b"")[len(tl0):].decode("utf-8", "replace")
        K.check(("MIGRATE-0.1.9 added %d" % len(want_add)) in tl and tl.count("MIGRATE-0.1.9 ADDED") == len(want_add) and "undo" in tl,
                "X update (%s): trades.log: the summary + one line per added product with its undo" % variant)
        K.eq(b9.tabs("Fish_Bluegill_Item"), ["Fishing"], "X update (%s): a fish line still saying Farming shows in Fishing only" % variant)
        if variant == "admin":
            K.eq(b9.tabs("Fish_Catfish_Item"), ["Fishing", "Seafood"], "X update (admin): an admin's own category (Seafood) still adds its tab")
            K.check(abs(float(b9.C.get("Ingredient_Crystal_Red").base) - 99.0) < 1e-9, "X update (admin): the admin's crystal line kept (not added twice)")
        s_after = b9.state(before.ids)
        K.check(s_after == s_before, "X update (%s): every old product's factor and quote = 0.1.8's (trades kept)" % variant)
        # run once + writeModes keeps the marker
        snap = dict((f, rb(os.path.join(d9, f))) for f in ("products.properties", "pricing.properties"))
        b9b = Bz(jar, d9)
        K.check(b9b.mig19 is None and all(rb(os.path.join(d9, f)) == v for f, v in snap.items()), "X update (%s): a second start changes nothing" % variant)
        b9b.C.writeModes(b9b.C.MIGRATED)
        K.check(b"migrated.0.1.9=" in rb(os.path.join(d9, "pricing.properties")), "X update (%s): writeModes (a later save) keeps the 0.1.9 marker" % variant)
        # rollback: 0.1.8 on the migrated folder
        rbd = os.path.join(scratch, "rb-" + variant)
        shutil.copytree(d9, rbd)
        o8 = Bz(OLD_JAR, rbd, new=False)
        K.check(all(c in o8.ids for c in want_add) and o8.state(before.ids) == s_before, "X rollback (%s): 0.1.8 loads the crystals and quotes every old product as before" % variant)
    # no pricing.properties / no 0.1.4 marker -> no update
    dn = os.path.join(scratch, "nomark")
    os.makedirs(dn)
    open(os.path.join(dn, "products.properties"), "wb").write(b"Ore_Copper=Mining,5,Copper Ore\n")
    open(os.path.join(dn, "pricing.properties"), "wb").write(b"migrated.0.1.3=x\n")
    L9 = loader_for(jar)
    C9 = JClass(PKG + "Catalog", loader=L9)
    P = JClass("java.nio.file.Paths")
    C9.FILE = P.get(dn).resolve("products.properties")
    C9.PFILE = P.get(dn).resolve("pricing.properties")
    K.check(C9.migrate19() is None and rb(os.path.join(dn, "products.properties")) == b"Ore_Copper=Mining,5,Copper Ore\n", "X: without migrated.0.1.4 the update does not run")
    K.save()


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    base = os.path.dirname(home)
    d8 = os.path.join(base, "live8")
    shutil.copytree(home, d8)
    raw = rb(os.path.join(home, "products.properties"))
    a = Bz(OLD_JAR, d8, new=False)
    b = Bz(jar, home)
    added = rb(os.path.join(home, "products.properties"))
    K.check(added.startswith(raw) and added.count(b"Ingredient_Crystal_") >= raw.count(b"Ingredient_Crystal_"), "D: the live products.properties keeps every byte (+ the crystals)")
    n_add = sum(1 for c in CRYSTALS if (c + "=").encode() not in raw)
    K.check(added.count(b"\n") - raw.count(b"\n") == n_add + (0 if raw.endswith(b"\n") else 1), "D: exactly %d crystal lines appended" % n_add)
    hd = os.path.join(home, "config-history")
    hs = [f for f in os.listdir(hd) if f.startswith("Skyy_SkyyBazaar~products.properties") and rb(os.path.join(hd, f)) == raw] if os.path.isdir(hd) else []
    K.check(n_add == 0 or len(hs) == 1, "D: one verified history copy of the live file")
    sa, sb = a.state(a.ids), b.state(a.ids)
    K.check(all(abs(sa[i][0] - sb[i][0]) < 1e-9 and sa[i][1:] == sb[i][1:] for i in a.ids), "D: every live product's factor and quote = 0.1.8's")
    snap = HK.tree_hash(home)
    b2 = Bz(jar, home)
    K.check(b2.mig19 is None and HK.tree_hash(home).get("products.properties") == snap.get("products.properties"), "D: the second start appends nothing")
    K.eq(b2.tabs("Fish_Bluegill_Item"), ["Fishing"], "D: live fish show in Fishing")
    K.notes.append("D: %d live products, %d crystal lines appended, tabs %s" % (len(a.ids), n_add, [str(x) for x in b2.C.categories()]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyBazaar"))
