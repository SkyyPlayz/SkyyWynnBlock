"""Harness for SkyyBazaar 0.1.16 (round tools01 part B: the Enchanted Stick product + its one-time update migrate116; tools/bazaar_0_1_16_patch.py).
Build first: python tools/bazaar_0_1_16_patch.py && python SkyyBazaar/build_skyybazaar_0.1.16.py

    python SkyyBazaar/test_skyybazaar_0.1.16.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the 0.1.15 / 0.1.14 harnesses are loaded as libraries, never edited):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.15 -> 0.1.16: exactly the listed members differ (migrate116 + its 3 fields, the marker in writeModes / loadModes, setup,
               the tables in <clinit>, the version texts)
  M   mig16    the one-time update, EXECUTED: a 0.1.15 folder (LF, CRLF, no final newline) then the 0.1.16 jar: exactly ONE line appended
               (= the jar's seed line, the file's own newline style; every old byte stays as the prefix), the config-history copy = the
               old bytes, M116_LOG = the head + one ADDED line with its undo (written to trades.log the way setup does), the marker
               migrated.0.1.16 (kept by writeModes), a second start changes nothing; an admin's own Skyy_Ench_Stick line (own price) is
               KEPT (added 0, no backup, no rewrite); a lost marker re-runs as a no-op; a fresh install seeds the product (the update
               runs at the next start and finds it 'already' listed); NEW0110 = the original 19 ids (= 0.1.15's), NEW0116 = the Stick;
               the Stick is in no 0.1.14 / 0.1.15 price-update table
  P   price    the Enchanted Stick's quotes at demand 1.0 (buy 1 / sell 1 / 64), buy > sell, buy then sell back never pays, crafting it
               from 100 bought Sticks and selling it never pays, the jar's own loop guard (loopingEdges / warnLoops) finds no paying
               recipe, AUTO + processed, the bridge publishes its quote
  O   order    Foraging = 0.1.15's order with the Enchanted Stick right after the Stick; every other tab = 0.1.15's order; the product is in
               Foraging only
  D   live     a scratch COPY of the live Skyy_SkyyBazaar (NewBetaTest; read-only source): the 0.1.16 start appends exactly the Stick line
               (once), its live quote; a SECOND start changes no products / pricing / config file
  AA  engine-access audit
Scratch: tools/dev/scratch/tools01-ench/bz (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.16"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.1.15.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "tools01-ench", "bz")))
PKG = "com.skyy.bazaar."
STICK = "Skyy_Ench_Stick"
ADDED = []
EXPECT = {
    # ~m init: PROC_SPEC / EDGE_SPEC are compile-time String constants inlined into init (+ the Stick's recipe line)
    "Catalog": ["+f NEW0116", "+f MIGRATED116", "+f M116_LOG", "+m migrate116", "~<clinit>", "~m init", "~m loadModes", "~m writeModes"],
    "CfgFn": ["~m opExport"],                      # the version text
    "CfgRows": ["~m header"],                      # the version text
    "SkyyBazaarPlugin": ["~m setup"],              # the version text + migrate116
}

# the 0.1.15 harness (its Bz15 helper; it loads the 0.1.14 one) - loaded as a module, never edited
_spec = importlib.util.spec_from_file_location("bz015test", os.path.join(HERE, "test_skyybazaar_0.1.15.py"))
T15 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T15)
T14, Bz15, rb, tabs = T15.T14, T15.Bz15, T15.rb, T15.tabs


class Bz16(object):
    """the 0.1.16 jar's data classes in their own loader, started on folder d exactly like SkyyBazaarPlugin.setup() (its data steps,
    migrate115 + migrate116 included; the migrate116 lines go to trades.log like setup writes them)"""

    def __init__(self, jar, d):
        from jpype import JClass
        self.L = T14.loader_for(jar)
        g = lambda n: JClass(PKG + n, loader=self.L)
        self.M, self.C, self.Cfg, self.U = g("Market"), g("Catalog"), g("BzCfg"), g("BzUtil")
        self.U.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar")
        dp = JClass("java.nio.file.Paths").get(d)
        os.makedirs(d, exist_ok=True)
        self.C.FILE = dp.resolve("products.properties")
        self.C.PFILE = dp.resolve("pricing.properties")
        self.M.FILE = dp.resolve("market.properties")
        self.M.LOGFILE = dp.resolve("trades.log")
        self.Cfg.load(dp)
        self.mig = [self.C.migrate(), self.C.migrate14(), self.C.migrate19(), self.C.migrate110()]
        self.m114 = self.C.migrate114()
        self.m115 = self.C.migrate115()
        self.m116 = self.C.migrate116()
        self.m116log = [str(x) for x in self.C.M116_LOG]
        self.n = int(self.C.load())
        self.M.load()
        self.C.reprice()
        self.M.publishAll()
        self.C.flushIfDirty()
        if self.m116 is not None:
            for x in self.m116log:
                self.M.log(x)
        self.C.M116_LOG.clear()
        self.M.flush()
        self.M.flushLog()
        self.ids = [str(p.id) for p in self.C.all()]

    def q(self, i, n=1, buy=True):
        return int(self.M.quote(i, n, buy))


def lines_of(b):
    return [x for x in b.replace(b"\r\n", b"\n").split(b"\n") if x]


# ------------------------------------------------------------------------------------------------------------------- M: mig16
def run_mig16(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    from jpype import JClass
    # ---- the tables
    old = Bz15(OLD_JAR, os.path.join(scratch, "t15"))
    new = Bz16(jar, os.path.join(scratch, "fresh"))
    n0110_old, n0110_new = [str(x) for x in old.C.NEW0110], [str(x) for x in new.C.NEW0110]
    K.check(len(n0110_new) == 19 and n0110_new == n0110_old and STICK not in n0110_new, "M: NEW0110 = 0.1.15's 19 ids (frozen; migrate110 unchanged)")
    K.eq([str(x) for x in new.C.NEW0116], [STICK], "M: NEW0116 = the Enchanted Stick")
    for f in ("M14_ID", "M114_ID", "M115_ID", "NEW019"):
        K.check(STICK not in [str(x) for x in getattr(new.C, f)], "M: the Stick is in no earlier update table (%s)" % f)
    seed = str(new.C.seedLine(STICK))
    K.check(re.match(r"^Skyy_Ench_Stick=Foraging,[0-9.]+,Enchanted Stick$", seed) is not None, "M: the seed line %s" % seed)
    K.notes.append("M: seed line %s" % seed)
    # ---- fresh install: the product is seeded; the update (no pricing.properties yet) waits for the next start, then finds it listed
    fp = os.path.join(scratch, "fresh", "products.properties")
    K.check(STICK in new.ids and lines_of(rb(fp)).count(seed.encode()) == 1, "M fresh: the Stick is seeded once (%s)" % new.m116)
    snap = rb(fp)
    f2 = Bz16(jar, os.path.join(scratch, "fresh"))
    K.check(f2.m116 is None or str(f2.m116).startswith("MIGRATE-0.1.16 added 0 already 1"), "M fresh 2nd start: %s" % f2.m116)
    K.check(rb(fp) == snap or [x for x in lines_of(rb(fp)) if x.startswith(b"Skyy_Ench_Stick=")] == [seed.encode()],
            "M fresh 2nd start: still exactly one Stick line")
    K.check(not os.path.isdir(os.path.join(scratch, "fresh", "config-history")) or not [x for x in os.listdir(os.path.join(scratch, "fresh", "config-history"))
                                                                                      if "products" in x], "M fresh: no history copy (nothing appended)")
    # ---- a 0.1.15 folder (LF / CRLF / no final newline) -> 0.1.16
    for tag in ("lf", "crlf", "nofinal"):
        d = os.path.join(scratch, "m16_" + tag)
        Bz15(OLD_JAR, d)
        pf, prf = os.path.join(d, "products.properties"), os.path.join(d, "pricing.properties")
        t = rb(pf).replace(b"\r\n", b"\n")
        K.check(b"Skyy_Ench_Stick=" not in t, "M %s: 0.1.15 has no Stick line" % tag)
        if tag == "crlf":
            t = t.replace(b"\n", b"\r\n")
        if tag == "nofinal":
            t = t.rstrip(b"\n")
        open(pf, "wb").write(t)
        before = rb(pf)
        b = Bz16(jar, d)
        after = rb(pf)
        nl = b"\r\n" if tag == "crlf" else b"\n"
        want = before + (nl if tag == "nofinal" else b"") + seed.encode() + nl
        # the reprice may move AUTO prices of the new line only; the update's own write is checked against migrate116's head + bytes
        K.check(str(b.m116).startswith("MIGRATE-0.1.16 added 1 already 0 backup config-history/"), "M %s: %s" % (tag, b.m116))
        K.check(after == want, "M %s: exactly ONE line appended (the seed line, the file's newline style), every old byte stays" % tag)
        hd = os.path.join(d, "config-history")
        baks = sorted(x for x in os.listdir(hd) if "~products.properties." in x) if os.path.isdir(hd) else []
        K.check(len(baks) == 1 and rb(os.path.join(hd, baks[0])) == before, "M %s: the config-history copy = the old bytes (%s)" % (tag, baks))
        K.eq(b.m116log[1:], ["MIGRATE-0.1.16 ADDED %s (undo: delete that line from products.properties, then /bazaaradmin reload)" % seed],
             "M %s: one ADDED line with its undo" % tag)
        tl = rb(os.path.join(d, "trades.log")) or b""
        K.check(all(x.encode() in tl for x in b.m116log), "M %s: trades.log carries the MIGRATE-0.1.16 lines" % tag)
        pr = rb(prf)
        K.check(pr.count(b"migrated.0.1.16=") == 1, "M %s: the marker is written once" % tag)
        b.C.writeModes(b.C.MIGRATED)
        K.check(rb(prf).count(b"migrated.0.1.16=") == 1 and b"migrated.0.1.15=" in rb(prf), "M %s: writeModes keeps the 0.1.16 marker (and 0.1.15's)" % tag)
        K.check(STICK in b.ids and STICK in [str(p.id) for p in b.C.inCat("Foraging")], "M %s: the Stick lists in Foraging" % tag)
        snap = (rb(pf), rb(prf))
        b2 = Bz16(jar, d)
        K.check(b2.m116 is None and (rb(pf), rb(prf)) == snap, "M %s: a second start changes nothing (%s)" % (tag, b2.m116))
    # ---- an admin already listed it (own price): migrate116 keeps the file byte for byte (nothing appended, no backup)
    d = os.path.join(scratch, "m16_admin")
    Bz15(OLD_JAR, d)
    pf = os.path.join(d, "products.properties")
    open(pf, "ab").write(b"Skyy_Ench_Stick=Foraging,999,My Stick\n")
    before = rb(pf)
    C_ = JClass(PKG + "Catalog", loader=T14.loader_for(jar))
    dp = JClass("java.nio.file.Paths").get(d)
    C_.FILE, C_.PFILE = dp.resolve("products.properties"), dp.resolve("pricing.properties")
    h = str(C_.migrate116())
    K.check(h.startswith("MIGRATE-0.1.16 added 0 already 1") and "backup config-history" not in h, "M admin: %s" % h)
    K.check(rb(pf) == before, "M admin: migrate116 keeps the admin's products.properties byte for byte")
    K.check(not os.path.isdir(os.path.join(d, "config-history")) or not [x for x in os.listdir(os.path.join(d, "config-history")) if "products" in x],
            "M admin: no history copy")
    b = Bz16(jar, d)
    K.check(b.m116 is None, "M admin: the next start does not run it again")
    K.notes.append("M admin: after load + reprice the admin's line holds base %s (AUTO %s: an AUTO processed good follows its recipe, like every "
                   "Enchanted product; /bazaaradmin mode fixed keeps an admin price)" % (b.C.get(STICK).base, bool(b.C.isAuto(STICK))))
    # ---- a lost marker re-runs as a no-op
    prf = os.path.join(d, "pricing.properties")
    txt = rb(prf).decode("latin-1")
    open(prf, "wb").write("".join(ln for ln in txt.splitlines(True) if "0.1.16" not in ln).encode("latin-1"))
    pb_ = rb(pf)
    b = Bz16(jar, d)
    K.check(str(b.m116).startswith("MIGRATE-0.1.16 added 0 already 1") and rb(pf) == pb_, "M rerun: a lost marker re-runs as a no-op (%s)" % b.m116)
    # ---- no migrated.0.1.4 (a pre-0.1.4 file): the update waits (migrate110's rule)
    d = os.path.join(scratch, "m16_pre14")
    os.makedirs(d)
    open(os.path.join(d, "pricing.properties"), "wb").write(b"# old\n")
    C_ = JClass(PKG + "Catalog", loader=T14.loader_for(jar))
    dp = JClass("java.nio.file.Paths").get(d)
    C_.FILE, C_.PFILE = dp.resolve("products.properties"), dp.resolve("pricing.properties")
    K.check(C_.migrate116() is None and rb(os.path.join(d, "pricing.properties")) == b"# old\n", "M pre-0.1.4: migrate116 waits, writes nothing")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- P: price
def run_price(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    b = Bz16(jar, os.path.join(scratch, "p16"))
    K.check(bool(b.C.isProc(STICK)) and bool(b.C.isAuto(STICK)), "P: the Enchanted Stick is an AUTO processed good")
    base, sbase = float(b.C.get(STICK).base), float(b.C.get("Ingredient_Stick").base)
    buy1, sell1, buy64, sell64 = b.q(STICK), b.q(STICK, 1, False), b.q(STICK, 64), b.q(STICK, 64, False)
    sticks100 = b.q("Ingredient_Stick", 100)
    K.notes.append("P: Enchanted Stick base %g (Stick %g): buy 1 = %d, sell 1 = %d, buy 64 = %d, sell 64 = %d; 100 Sticks buy for %d, sell for %d"
                   % (base, sbase, buy1, sell1, buy64, sell64, sticks100, b.q("Ingredient_Stick", 100, False)))
    K.check(buy1 > sell1 > 0 and buy64 > sell64 > 0, "P: buy > sell > 0 (1: %d / %d, 64: %d / %d)" % (buy1, sell1, buy64, sell64))
    K.check(sell1 < sticks100, "P: crafting it from 100 bought Sticks and selling it never pays (%d < %d)" % (sell1, sticks100))
    K.check(base > 100 * sbase, "P: it carries the processed-goods premium over 100 Sticks (%g > %g)" % (base, 100 * sbase))
    # buy then sell straight back never pays (1 and 64; the demand is put back to 1.0 after each)
    rt = []
    for n in (1, 64):
        b1 = b.q(STICK, n)
        b.M.apply(STICK, n, True)
        s1 = b.q(STICK, n, False)
        b.M.apply(STICK, n, False)
        rt.append((n, b1, s1))
        b.M.F.remove(STICK)
    K.check(all(s1 < b1 for n, b1, s1 in rt), "P: buy 1 / 64 then sell them straight back never pays %s" % rt)
    sp = float(b.M.SPREAD)
    K.eq(int(b.C.loopingEdges(sp).size()), 0, "P: Catalog.loopingEdges finds no paying recipe (spread %g)" % sp)
    K.eq(int(b.C.warnLoops(sp)), 0, "P: Catalog.warnLoops = 0")
    from jpype import JClass
    b.M.publishAll()
    br = JClass("java.lang.System").getProperties().get("skyy.bridge")
    K.check(int(br.get("bazaar:buy:" + STICK)) == b.q(STICK) and int(br.get("bazaar:sell:" + STICK)) == b.q(STICK, 1, False),
            "P: the bridge publishes the Stick's quotes (bazaar:buy / bazaar:sell)")
    K.save(price={"base": base, "buy1": buy1, "sell1": sell1, "buy64": buy64, "sell64": sell64})


# ------------------------------------------------------------------------------------------------------------------- O: order
def run_order(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    bo = Bz15(OLD_JAR, os.path.join(scratch, "o15"))
    bn = Bz16(jar, os.path.join(scratch, "o16"))
    to, tn = tabs(bo), tabs(bn)
    K.eq(list(tn), list(to), "O: the same tabs in the same order")
    fo = tn["Foraging"]
    k = fo.index("Ingredient_Stick")
    K.eq(fo[k + 1], STICK, "O: the Enchanted Stick sits right after the Stick")
    K.eq([i for i in fo if i != STICK], to["Foraging"], "O: Foraging keeps 0.1.15's order for every other product (%d)" % len(to["Foraging"]))
    for t in tn:
        if t != "Foraging":
            K.eq(tn[t], to[t], "O: %s keeps its 0.1.15 order (%d)" % (t, len(tn[t])))
    K.eq([t for t in tn if STICK in tn[t]], ["Foraging"], "O: the Stick is in the Foraging tab only")
    K.eq(sorted(set(bn.ids) - set(bo.ids)), [STICK], "O: the one new product")
    K.notes.append("O: Foraging around it: %s" % ", ".join(fo[max(0, k - 2):k + 4]))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D: live
def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    files = ("products.properties", "pricing.properties", "market.properties", "config.properties")
    before = dict((f, rb(os.path.join(home, f))) for f in files)
    had = before["products.properties"] is not None and b"Skyy_Ench_Stick=" in before["products.properties"]
    K.check(before["pricing.properties"] is not None and b"migrated.0.1.10=" in before["pricing.properties"], "D: the live copy has run 0.1.10+ (marker found)")
    on115 = b"migrated.0.1.15=" in before["pricing.properties"]
    K.notes.append("D: the live data is on %s" % ("0.1.15" if on115 else "0.1.14 (no migrated.0.1.15): migrate115 (x4.5) runs first, then migrate116"))
    b = Bz16(jar, home)
    K.check(b.n > 400, "D: %d live products load" % b.n)
    K.notes.append("D: migrate115 %s | migrate116 %s" % (b.m115, b.m116))
    K.check((b.m115 is None) == on115, "D: migrate115 runs only on 0.1.14 data")
    if had:
        K.check(str(b.m116).startswith("MIGRATE-0.1.16 added 0 already 1"), "D: the live file already lists it: %s" % b.m116)
    else:
        K.check(str(b.m116).startswith("MIGRATE-0.1.16 added 1 already 0"), "D: the update appended it: %s" % b.m116)
    al, bl = lines_of(before["products.properties"]), lines_of(rb(os.path.join(home, "products.properties")))
    ida = [x.split(b"=", 1)[0] for x in al]
    idb = [x.split(b"=", 1)[0] for x in bl]
    K.eq((idb[:len(ida)] == ida, idb[len(ida):]), (True, [] if had else [STICK.encode()]),
         "D: every old line stays in place (prices may move by migrate115 / the reprice), only the Stick line is appended at the end")
    K.check(had or bl[-1].startswith(b"Skyy_Ench_Stick=Foraging,") and bl[-1].endswith(b",Enchanted Stick"), "D: the appended line %s" % bl[-1:])
    K.check(len([x for x in bl if x.startswith(b"Skyy_Ench_Stick=")]) == 1, "D: exactly one Stick line")
    K.check(before["config.properties"] == rb(os.path.join(home, "config.properties")), "D: config.properties untouched")
    K.notes.append("D: live Stick quote buy 1 = %d, sell 1 = %d (live demand)" % (b.q(STICK), b.q(STICK, 1, False)))
    snap = dict((f, rb(os.path.join(home, f))) for f in ("products.properties", "pricing.properties", "config.properties"))
    b2 = Bz16(jar, home)
    K.check(b2.m116 is None, "D2: the update does not run twice")
    K.eq([f for f in snap if rb(os.path.join(home, f)) != snap[f]], [], "D2: the second start changes no products / pricing / config file")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("mig16", run_mig16), ("price", run_price), ("order", run_order), ("live", run_live)], script=__file__,
           live=(T15.LIVE_DIR, "Skyy_SkyyBazaar"))
