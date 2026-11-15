"""Harness for SkyyCoins 0.1.12 (round bank2: no coin death penalty; tools/coins_0_1_12_patch.py).
Build first: python tools/coins_0_1_12_patch.py && python SkyyCoins/build_skyycoins_0.1.12.py

    python SkyyCoins/test_skyycoins_0.1.12.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.11 -> 0.1.12: + CoinMigDeath0; CoinConfig (MIN / MAX 0, the default text, load), CoinTask.run (no line at 0 %), the
              plugin's setup and the kit's version texts differ - nothing else
  S  static   the patch re-runs to identical bytes; one new class, no command / system; the death branch says nothing while MAX is 0
  X  exec     EXECUTES the new code: CoinConfig.load on a fresh file (0 / 0 + both markers), CoinMigDeath0.update on texts (5 / 5 -> 0 / 0,
              CRLF + LF kept, comments and order kept, an owner's 5 / 10 kept, a marker = done, a split line kept), CoinMigDeath0.run
              on scratch files (History copy = the old bytes, 2 change-log rows, the marker, a second run changes nothing), the chain
              10 / 25 -> CoinMigP7 -> 5 / 5 -> CoinMigDeath0 -> 0 / 0, lossOf(..., 0) = 0
  D  live     setup (load, CoinMigP7, CoinMigDeath0, kit) TWICE on a scratch COPY of the live NewBetaTest Skyy_SkyyCoins: the first start
              moves 5 / 5 -> 0 / 0 and adds only kit history / change files, the second changes nothing; every purse file untouched
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.12"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCoins-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(HK.arg("--old", os.path.join(HERE, "SkyyCoins-0.1.11.jar")))
GEN = os.path.join(HERE, "build_skyycoins_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyycoins_0.1.11.py")
PATCH = os.path.join(ROOT, "tools", "coins_0_1_12_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bank2", "coins")))
PKG = "com.skyy.coins."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCoins")
EXPECT = {
    "CoinConfig": ["~<clinit>", "~m load", "~m save"],
    "CoinTask": ["~m run"],
    "SkyyCoinsPlugin": ["~m setup"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["CoinMigDeath0"]


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)([JClass("java.io.File")(jar).toURI().toURL()])
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def P_(p):
    from jpype import JClass, JArray
    return JClass("java.nio.file.Paths").get(p, JArray(JClass("java.lang.String"))([]))


def setup(J, home):
    """what SkyyCoins 0.1.12 setup() does before the kit starts, on the folder home (= .../mods/Skyy_SkyyCoins)"""
    from jpype import JClass
    CS = J("CoinStore")
    CS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCoins")
    CS.DIR = P_(os.path.join(home, "balances"))
    CS.JOURNAL = P_(os.path.join(home, "balances-journal.properties"))
    CS.recover()
    J("CoinConfig").FILE = P_(os.path.join(home, "config.properties"))
    J("CoinConfig").load()
    m1 = str(J("CoinMigP7").run(J("CoinConfig").FILE))
    m2 = str(J("CoinMigDeath0").run(J("CoinConfig").FILE))
    J("CoinXfer").FILE = P_(os.path.join(home, "transfers.properties"))
    J("CoinXfer").load()
    J("CoinSnd").load(P_(home))
    J("CfgPub").start(P_(os.path.dirname(home)), CS.LOG)
    return m1, m2


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read().replace("\r\n", "\n")
    o = open(GEN_OLD, encoding="utf8", newline="").read().replace("\r\n", "\n")
    K.check(g.startswith('"""SkyyCoins 0.1.12 - build script') and g.count('VERSION = "0.1.12"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("pool.makeClass(") - o.count("pool.makeClass("), 1, "S one new class")
    run = g[g.index("public void run() {{\n  try {{\n    if (pr == null || !pr.isValid()) return;"):]
    K.check("if (balNow > 0L && {PKG}.CoinConfig.MAX > 0 && {PKG}.CoinConfig.safeWorld(wn)) pr.sendMessage(" in run, "S the safe-world line only while a loss is set")
    K.check("if (wn == null && balNow > 0L && {PKG}.CoinConfig.MAX > 0)" in run, "S the unknown-world warning only while a loss is set")
    K.check(g.index("CoinMigDeath0.run(") > g.index("CoinMigP7.run("), "S CoinMigDeath0 runs after CoinMigP7")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    L = loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    CF, MG, M7 = J("CoinConfig"), J("CoinMigDeath0"), J("CoinMigP7")
    K.check(int(CF.MIN) == 0 and int(CF.MAX) == 0, "X the fields default to 0 / 0")
    K.check(int(CF.lossOf(1000000, "default", 0)) == 0 and int(CF.lossOf(1000000, "default", 5)) == 50000, "X lossOf: 0 % = nothing, 5 % = 5 %")
    d = os.path.join(scratch, "x")
    os.makedirs(d, exist_ok=True)
    J("CoinStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCoins")
    # a fresh file
    cf = os.path.join(d, "fresh", "config.properties")
    os.makedirs(os.path.dirname(cf), exist_ok=True)
    CF.FILE = P_(cf)
    CF.load()
    t = open(cf, encoding="latin-1").read()
    K.check("\npenaltyMin=0\npenaltyMax=0\n" in t and "SkyyCoins 0.1.12" in t and "Balance P7 economy (SkyyCoins 0.1.10)" in t, "X a fresh file: 0 / 0 + both markers")
    K.check(int(CF.MIN) == 0 and int(CF.MAX) == 0, "X a fresh file loads 0 / 0")
    K.check(MG.update(t) is None and M7.update(t) is None, "X a fresh file needs no update")
    # update() on texts
    mk7 = "# migrated: Balance P7 economy (SkyyCoins 0.1.10) - x"
    for nl in ("\r\n", "\n"):
        src = nl.join(["# head", mk7, "penaltyMin=5", "penaltyMax = 5", "penalty.safeWorlds=skyy-island-", "coins.curve=1:1,10:1", ""])
        r = MG.update(src)
        K.check(r is not None and int(r[1]) == 2, "X update 5 / 5 (%r): 2 keys move" % nl)
        nt = str(r[0])
        K.check(("penaltyMin=0" + nl) in nt and ("penaltyMax = 0" + nl) in nt, "X the two value lines change in place (the 'key = value' spacing kept)")
        K.check(nt.count("SkyyCoins 0.1.12") == 1 and nt.replace(str(MG.MARK) + nl, "").replace("=0", "=5").replace("= 0", "= 5") == src, "X only the marker + the two values differ (%r)" % nl)
        K.check((nl == "\r\n") == ("\r\n" in nt) and (nl == "\n") == ("\r\n" not in nt), "X line endings kept (%r)" % nl)
        K.eq([str(x) for x in r[3]], ["penaltyMin", "5", "0", "penaltyMax", "5", "0"], "X the change rows")
    r = MG.update("penaltyMin=5\npenaltyMax=10\n")
    K.check(r is not None and int(r[1]) == 0 and "penaltyMax=10" in str(r[0]) and "penaltyMin=5\n" in str(r[0]) and "penaltyMin=5" in str(r[2]), "X an owner's 5 / 10 is kept (marker only): %s" % (r and str(r[2])))
    r = MG.update("penaltyMin=0\npenaltyMax=0\n")
    K.check(r is not None and int(r[1]) == 0, "X 0 / 0 already: nothing moves")
    r = MG.update("penaltyMin=5\\\n  \npenaltyMax=5\n")
    K.check(r is not None and int(r[1]) == 0, "X a value continued on the next line is never rewritten")
    K.check(MG.update("# " + str(MG.MARK_ID) + "\npenaltyMin=5\npenaltyMax=5\n") is None, "X the marker = done (null)")
    # run() on scratch homes (the kit's History / change log)
    for nm, body, want in (("five", "#SkyyCoins config\r\n" + mk7 + "\r\npenaltyMax=5\r\npenaltyMin=5\r\n", ("0", "0")),
                           ("owner", "#SkyyCoins config\n" + mk7 + "\npenaltyMax=20\npenaltyMin=5\n", ("5", "20")),
                           ("p7", "#SkyyCoins config - death penalty percent range\npenaltyMax=25\npenaltyMin=10\n", ("0", "0"))):
        home = os.path.join(d, nm, "Skyy_SkyyCoins")
        os.makedirs(home, exist_ok=True)
        f = os.path.join(home, "config.properties")
        open(f, "w", encoding="latin-1", newline="").write(body)
        old = open(f, "rb").read()
        m1, m2 = setup(J, home)
        J("CfgPub").shutdown()
        t = open(f, "rb").read().decode("latin-1")
        K.check(("penaltyMin=%s" % want[0]) in t and ("penaltyMax=%s" % want[1]) in t, "X %s: penaltyMin / Max = %s (%s | %s)" % (nm, want, m1[:60], m2[:80]))
        K.check(int(CF.MIN) == int(want[0]) and int(CF.MAX) == int(want[1]), "X %s: the fields follow (%s / %s)" % (nm, CF.MIN, CF.MAX))
        K.check(("\r\n" in body) == ("\r\n" in t), "X %s: line endings kept" % nm)
        hd = os.path.join(home, "config-history")
        hist = [open(os.path.join(r_, x), "rb").read() for r_, _ds, fs in os.walk(hd) for x in fs if not x.endswith(".log")]
        K.check(old in hist, "X %s: the old bytes are in config-history" % nm)
        log = open(os.path.join(home, "config-changes.log"), encoding="latin-1").read() if os.path.exists(os.path.join(home, "config-changes.log")) else ""
        rows = [l for l in log.splitlines() if "SkyyCoins 0.1.12" in l]
        K.eq(len(rows), 2 if nm != "owner" else 0, "X %s: change-log rows of the 0.1.12 update" % nm)
        b1 = open(f, "rb").read()
        m1b, m2b = setup(J, home)
        J("CfgPub").shutdown()
        K.check(open(f, "rb").read() == b1 and m2b == "" and m1b == "", "X %s: a second start changes nothing" % nm)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    h0 = HK.tree_hash(home)
    cfg0 = open(os.path.join(home, "config.properties"), encoding="latin-1").read()
    snaps, msgs = [], []
    for start in (1, 2):
        L = loader_for(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        msgs.append(setup(J, home))
        K.check(int(J("CoinConfig").MIN) == 0 and int(J("CoinConfig").MAX) == 0, "DL start %d: no coin death penalty (%s / %s)" % (start, J("CoinConfig").MIN, J("CoinConfig").MAX))
        J("CfgPub").shutdown()
        J("CoinStore").stopIO()
        snaps.append(HK.tree_hash(home))
    new = sorted(set(snaps[0]) - set(h0))
    changed = sorted(k for k in h0 if snaps[0].get(k) != h0[k])
    K.check(all(n.startswith(("config-history", "config-changes")) for n in new) and "config.properties" in changed
            and all(c in ("config.properties", "config-changes.log", os.path.join("config-history", "index.log")) for c in changed),
            "DL the first start changes only config.properties + kit history / change files: changed %s new %s" % (changed, new))
    K.check(not [k for k in h0 if k.startswith("balances") and snaps[0].get(k) != h0[k]], "DL every purse file untouched")
    cfg1 = open(os.path.join(home, "config.properties"), encoding="latin-1").read()
    K.check("penaltyMin=5" in cfg0 and "penaltyMin=0" in cfg1 and "penaltyMax=0" in cfg1, "DL the live 5 / 5 became 0 / 0")
    K.check(snaps[0] == snaps[1] and msgs[1] == ("", ""), "DL the second start changes nothing")
    K.notes.append("DL first start message: %r" % (msgs[0][1][:200],))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyCoins", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyCoins"))
