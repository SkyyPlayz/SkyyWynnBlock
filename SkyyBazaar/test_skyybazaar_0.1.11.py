"""Harness for SkyyBazaar 0.1.11 (rebirth R4: bazaar:fn:closeall / bazaar:fn:wouldclose; tools/bazaar_0_1_11_patch.py).
Build first: python tools/bazaar_0_1_11_patch.py && python SkyyBazaar/build_skyybazaar_0.1.11.py

    python SkyyBazaar/test_skyybazaar_0.1.11.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.10 -> 0.1.11: exactly the listed members differ (+ BzRebirthFn)
  X  exec     EVERY NEW PATH: a fresh folder started like setup() with 0.1.10 and 0.1.11 (same products, same quotes), trades made;
              BzRebirthFn op 0 (closeall) -> "ok:0" for profile keys, IDEMPOTENT (again ok:0), one CLOSEALL line per call in trades.log
              (after the Market log flush), products / pricing / market files byte-identical; op 1 (wouldclose) -> "ok:0:0:0:0" and
              writes nothing; bad keys (null, "", "  ", a number) -> err:bad-key on both. The err:exception catch is defensive only:
              nothing in it can be made to throw from outside (Market.LOGQ is final) - not executed
  D  live     start twice on a scratch COPY of the live Skyy_SkyyBazaar with 0.1.11: the first start gives exactly 0.1.10's result on
              its own copy (products / pricing bytes, factors, quotes - the live folder may still owe 0.1.10's one-time update); the second
              start changes no products / pricing / config file; closeall / wouldclose for a key
  AA engine-access audit
NOT executed here: SkyyBazaarPlugin.setup / shutdown's two bridge put / remove lines (the smoke test boots setup).
Scratch: tools/dev/scratch/market4/bazaar (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.11"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.1.10.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "market4", "bazaar")))
PKG = "com.skyy.bazaar."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyBazaar")
EXPECT = {
    "SkyyBazaarPlugin": ["~m setup", "~m shutdown"],
    "CfgFn": ["~m opExport"],      # the version text
    "CfgRows": ["~m header"],      # the version text
}
ADDED = ["BzRebirthFn"]
KEYS = ["00000077-0000-4000-8000-000000000077", "00000077-0000-4000-8000-000000000077-p2", "some profile key"]


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


class Bz(object):
    """one jar's Market / Catalog / BzCfg in its own loader, started on folder d like SkyyBazaarPlugin.setup() (its data steps)"""

    def __init__(self, jar, d):
        from jpype import JClass
        self.L = loader_for(jar)
        g = lambda n: JClass(PKG + n, loader=self.L)
        self.M, self.C, self.Cfg, self.U = g("Market"), g("Catalog"), g("BzCfg"), g("BzUtil")
        self.Fn = g("BzRebirthFn") if jar != OLD_JAR else None
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
        for lst, mg in ((self.C.M19_LOG, self.C.migrate19()), (self.C.M110_LOG, self.C.migrate110())):
            if mg is not None:
                for i in range(lst.size()):
                    self.M.log(lst.get(i))
            lst.clear()
        self.n = int(self.C.load())
        self.M.load()
        self.C.reprice()
        self.M.publishAll()
        self.C.flushIfDirty()
        self.M.flush()
        self.ids = [str(p.id) for p in self.C.all()]

    def state(self, ids=None):
        return {i: (float(self.M.factor(i)), int(self.M.quote(i, 1, True)), int(self.M.quote(i, 1, False))) for i in (ids or self.ids)}


def rb(p):
    return open(p, "rb").read() if os.path.exists(p) else None


def files(d, skip=("trades.log",)):
    out = {}
    for base, _ds, fs in os.walk(d):
        for f in fs:
            if f not in skip:
                out[os.path.relpath(os.path.join(base, f), d)] = rb(os.path.join(base, f))
    return out


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    d11, d10 = os.path.join(scratch, "f11"), os.path.join(scratch, "f10")
    b11, b10 = Bz(jar, d11), Bz(OLD_JAR, d10)
    K.eq(b11.n, b10.n, "X fresh: the same %d products as 0.1.10" % b10.n)
    K.check(b11.state() == b10.state(), "X fresh: every product quotes as on 0.1.10")
    for b in (b11, b10):
        b.M.apply("Ore_Copper", 64, True)
        b.M.apply("Wood_Oak_Trunk", 20, False)
        b.M.flush()
    K.check(b11.state() == b10.state(), "X after trades: the same factors and quotes")
    f0 = files(d11)
    log0 = rb(os.path.join(d11, "trades.log")) or b""
    c, w = b11.Fn(0), b11.Fn(1)
    for k in KEYS:
        K.eq(str(c.apply(k)), "ok:0", "X closeall(%r) = ok:0 (no orders in 0.1.x)" % k)
        K.eq(str(c.apply(k)), "ok:0", "X closeall(%r) again = ok:0 (idempotent)" % k)
        K.eq(str(w.apply(k)), "ok:0:0:0:0", "X wouldclose(%r) = ok:0:0:0:0" % k)
    for bad in (None, "", "   ", JInt(5)):
        K.eq(str(c.apply(bad)), "err:bad-key", "X closeall(%r) = err:bad-key" % (bad,))
        K.eq(str(w.apply(bad)), "err:bad-key", "X wouldclose(%r) = err:bad-key" % (bad,))
    b11.M.flush()
    b11.M.flushLog()
    K.check(files(d11) == f0, "X closeall / wouldclose changed no products / pricing / market / config file")
    log1 = rb(os.path.join(d11, "trades.log")) or b""
    new = log1[len(log0):].decode("utf8")
    K.check(log1.startswith(log0), "X trades.log only grew")
    K.eq(new.count(" CLOSEALL key="), 2 * len(KEYS), "X one CLOSEALL line per closeall call (%r)" % new[:160])
    K.check("CLOSEALL key=some_profile_key closed=0" in new, "X the key's spaces are written as _")
    K.check(b11.state() == b10.state(), "X quotes unchanged by closeall")
    # the catch path: a broken log queue -> err:exception, never thrown
    q = b11.M.LOGQ
    fld = JClass("java.lang.Class").forName(PKG + "Market", True, b11.L).getDeclaredField("LOGQ")
    mods = fld.getModifiers()
    if JClass("java.lang.reflect.Modifier").isFinal(mods):
        K.notes.append("X: Market.LOGQ is final, nothing inside closeall can throw from outside - the err:exception catch is NOT executed (defensive only)")
    else:
        b11.M.LOGQ = None
        K.eq(str(c.apply(KEYS[0])), "err:exception", "X a failure inside closeall -> err:exception (caught)")
        b11.M.LOGQ = q
    K.save()


def run_live(out, jar, scratch, home):
    import re
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    ref = os.path.join(scratch, "live10")
    shutil.copytree(home, ref)
    b10 = Bz(OLD_JAR, ref)          # what 0.1.10 does with the live folder (it may run its own one-time update first)
    b = Bz(jar, home)
    K.eq(rb(os.path.join(home, "products.properties")), rb(os.path.join(ref, "products.properties")), "D1: products.properties = 0.1.10's result")
    strip = lambda x: re.sub(rb"migrated\.0\.1\.10=[^\r\n]*", b"migrated.0.1.10=*", x or b"")
    K.eq(strip(rb(os.path.join(home, "pricing.properties"))), strip(rb(os.path.join(ref, "pricing.properties"))), "D1: pricing.properties = 0.1.10's result (marker time aside)")
    K.check(b.state() == b10.state(), "D1: every product's factor and quote = 0.1.10's (%d products)" % b.n)
    keep = ("products.properties", "pricing.properties", "config.properties")
    snap = HK.tree_hash(home)
    b2 = Bz(jar, home)
    now = HK.tree_hash(home)
    K.eq([k for k in keep if now.get(k) != snap.get(k)], [], "D2: the second start changes no products / pricing / config file")
    K.check(b2.state() == b.state(), "D2: same quotes")
    K.eq(str(b2.Fn(1).apply(KEYS[0])), "ok:0:0:0:0", "D: wouldclose on the live copy")
    K.eq(str(b2.Fn(0).apply(KEYS[0])), "ok:0", "D: closeall on the live copy")
    K.notes.append("D: %d live products" % b2.n)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyBazaar"))
