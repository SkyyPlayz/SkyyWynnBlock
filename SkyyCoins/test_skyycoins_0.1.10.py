"""Harness for SkyyCoins 0.1.10 (BALANCE PASS P7: the coin curve + coins:fn:curve, death 5 % + safe worlds, CoinMigP7; tools/coins_0_1_10_patch.py).
Build first: python tools/coins_0_1_10_patch.py && python SkyyCoins/build_skyycoins_0.1.10.py

    python SkyyCoins/test_skyycoins_0.1.10.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.9 -> 0.1.10: + CoinCurve, CoinMigP7; only the members the round names differ
  X  exec     EXECUTES the new code: CoinCurve.at / fn / check / use (= tools/balance_model.py p7_curve_from_text at every level 0..200),
              coins:fn:curve through the bridge object, CoinConfig.lossOf + safeWorld (1,000 -> 950; island / shard worlds 0; empty list),
              CoinConfig.load (fresh file = the default text with the marker; a bad curve line = one WARN + the default), CoinMigP7 on a
              fresh / 10-25 (LF and CRLF, date header kept) / hand-set 7-12 / half-moved / already-migrated file (History copy, change
              log rows, marker, bytes outside the two values), the KIT end to end (coins.curve refused when bad; penaltyMin set -> field +
              file line; the java.util.Properties header kept)
  D  live     the 0.1.6 start-twice phase on a scratch COPY of the live NewBetaTest Skyy_SkyyCoins, then the 0.1.10 setup order
              (CoinConfig.load, CoinMigP7.run, CoinXfer.load, CoinSnd.load, CfgPub.start) TWICE on the copy: the first moves exactly
              penaltyMin / penaltyMax 10 / 25 -> 5 / 5 (+ marker, + kit history / change files), the second changes nothing
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, math, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.10"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCoins-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCoins-0.1.9.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp7", "coins")))
PKG = "com.skyy.coins."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCoins")
EXPECT = {
    "CoinConfig": ["+f DEFAULT_TEXT", "+f SAFE", "+m lossOf", "+m safeWorld", "~<clinit>", "~m load", "~m save"],
    "CoinFn": ["~m apply"],
    "CoinTask": ["+f worldName", "~m run"],
    "CoinTick": ["~m dispatch"],
    "DeathPenaltyCmd": ["~m applySpec"],
    "SkyyCoinsPlugin": ["~m setup", "~m shutdown"],
    "CfgFile": ["~<clinit>", "~m init"],
    "CfgRows": ["+f DL2", "~<clinit>", "~m defLines", "~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = ["CoinCurve", "CoinMigP7"]
CURVE_TEXT = ("1:0.476,8:0.848,10:1,15:1.51,20:2.28,28:4.41,30:5.2,35:8.49,40:13.8,48:30.3,50:36.8,55:50.5,60:69.2,68:115,70:130,75:179,"
              "80:246,88:410,90:466,95:641,100:881")
MARK_ID = "Balance P7 economy (SkyyCoins 0.1.10)"


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


T16 = tmod(os.path.join(HERE, "test_skyycoins_0.1.6.py"), "tc016")
T16.OLD_JAR = OLD_JAR
T16.LIVE_DIR = LIVE_DIR


def model():
    return tmod(os.path.join(ROOT, "tools", "balance_model.py"), "bm_p7")


def setup_kit(J, home):
    """what setup() does before the kit starts, on the folder `home` (= .../mods/Skyy_SkyyCoins)"""
    from jpype import JClass, JArray
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    CS = J("CoinStore")
    CS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCoins")
    CS.DIR = P(os.path.join(home, "balances"))
    CS.JOURNAL = P(os.path.join(home, "balances-journal.properties"))
    CS.recover()
    J("CoinConfig").FILE = P(os.path.join(home, "config.properties"))
    J("CoinConfig").load()
    msg = str(J("CoinMigP7").run(J("CoinConfig").FILE))
    J("CoinXfer").FILE = P(os.path.join(home, "transfers.properties"))
    J("CoinXfer").load()
    J("CoinSnd").load(P(home))
    J("CfgPub").start(P(os.path.dirname(home)), CS.LOG)
    return msg


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JInt, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    bm = model()
    L = T16.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    CC, CF, MG, Fn = J("CoinCurve"), J("CoinConfig"), J("CoinMigP7"), J("CoinFn")
    CC.use()
    # ---- the curve: the Java table = the model's text reader at every level, the spec's harness points
    K.check(str(CC.DEF) == CURVE_TEXT == bm.P7_CURVE_TEXT == bm.p7_curve_text(), "CURVE the built-in default = tools/balance_model.py p7_curve_text()")
    worst = max(abs(float(CC.at(lv)) / bm.p7_curve_from_text(CURVE_TEXT, lv) - 1) for lv in range(0, 201))
    K.check(worst < 1e-9, "CURVE CoinCurve.at = the model's p7_curve_from_text at every level 0..200 (worst rel. diff %.2e)" % worst)
    K.check(abs(float(CC.at(10)) - 1.0) < 1e-12 and abs(float(CC.at(90)) - 466) < 1e-9, "CURVE Lv 10 = 1.0, Lv 90 = 466")
    a44 = float(CC.at(44))
    K.check(abs(a44 / math.sqrt(13.8 * 30.3) - 1) < 0.01, "CURVE log-linear: Lv 44 = sqrt(13.8 x 30.3) +-1 %% (%.3f)" % a44)
    K.check(float(CC.at(0)) == float(CC.at(1)) and float(CC.at(-5)) == float(CC.at(1)) and float(CC.at(200)) == float(CC.at(100)), "CURVE clamps below 1 and above 100")
    f = Fn("curve")
    K.check(abs(float(f.apply(JClass("java.lang.Integer")(50))) - 36.8) < 1e-9, "BRIDGE coins:fn:curve apply(Integer 50) = 36.8")
    arr = JArray(JClass("java.lang.Object"))([JClass("java.lang.Integer")(90)])
    K.check(abs(float(f.apply(arr)) - 466) < 1e-9, "BRIDGE apply(Object[] { 90 }) = 466")
    K.check(f.apply("lots") is None and f.apply(None) is None and f.apply(JArray(JClass("java.lang.Object"))([])) is None, "BRIDGE a bad argument -> null")
    K.check(CC.check("coins.curve", "1:1,10:2") is None and CC.check("coins.curve", CURVE_TEXT) is None, "CHECK a good curve passes")
    for bad in ("", "1:1", "10:1,5:2", "1:0,10:1", "1:-2,10:1", "a:b,c:d", "1:1;10:2", "1:1,1:2"):
        K.check(CC.check("coins.curve", bad) is not None, "CHECK refuses %r" % bad)
    w0 = int(J("CoinStore").WARNS.get()) if hasattr(J("CoinStore"), "WARNS") else None
    CC.TEXT = "1:1,oops"
    CC.use()
    K.check(abs(float(CC.at(50)) - 36.8) < 1e-9, "CURVE a bad running text = the default (and one WARN)")
    CC.TEXT = "1:1,100:100"
    CC.after("coins.curve")
    K.check(abs(float(CC.at(10)) - 100 ** (9 / 99.0)) < 1e-9, "CURVE after= re-reads a typed curve at once (live)")
    CC.TEXT = CC.DEF
    CC.use()
    # ---- death
    CF.SAFE = "skyy-island-,skyy-shard-"
    K.eq(int(CF.lossOf(1000, "default", 5)), 50, "DEATH purse 1,000 in the hub at 5 % loses 50 (keeps 950)")
    K.eq(int(CF.lossOf(1000, "skyy-island-abc", 5)), 0, "DEATH on an island: nothing")
    K.eq(int(CF.lossOf(1000, "skyy-shard-p1", 5)), 0, "DEATH in a shard world: nothing")
    K.eq(int(CF.lossOf(1000, None, 5)), 0, "DEATH fix: a world whose name cannot be read costs nothing (CoinTask WARNs; the name comes from CoinTick first)")
    K.eq(int(CF.lossOf(0, "default", 5)) + int(CF.lossOf(-3, "default", 5)) + int(CF.lossOf(1000, "default", 0)), 0, "DEATH nothing to lose / 0 %")
    K.eq(int(CF.lossOf(19, "default", 5)), 0, "DEATH 5 % of 19 floors to 0")
    K.eq(int(CF.lossOf(1000, "default", 250)), 1000, "DEATH a percent above 100 counts as 100")
    CF.SAFE = ""
    K.eq(int(CF.lossOf(1000, "skyy-island-abc", 5)), 50, "DEATH empty safe list = every world costs")
    CF.SAFE = " skyy-island- , ,zone-9"
    K.check(bool(CF.safeWorld("zone-9-a")) and bool(CF.safeWorld("skyy-island-x")) and not bool(CF.safeWorld("default")), "DEATH the list is trimmed, blanks skipped")
    # ---- CoinConfig.load: fresh file + values
    from jpype import JClass as JC
    Paths = JC("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JC("java.lang.String"))([]))
    d = os.path.join(scratch, "x1", "mods", "Skyy_SkyyCoins")
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, "config.properties")
    CF.FILE = P(fp)
    CF.MIN, CF.MAX = 9, 9
    CF.load()
    t = open(fp, "rb").read().decode("latin-1")
    K.check(MARK_ID in t and "penaltyMin=5\n" in t and "penaltyMax=5\n" in t and "penalty.safeWorlds=skyy-island-,skyy-shard-\n" in t and ("coins.curve=" + CURVE_TEXT) in t,
            "LOAD a fresh file = the default text (marker, 5 / 5, safe worlds, curve)")
    K.check(int(CF.MIN) == 5 and int(CF.MAX) == 5 and str(CF.SAFE) == "skyy-island-,skyy-shard-", "LOAD the fresh values")
    K.eq(str(MG.run(CF.FILE)), "", "MIG a fresh file (marker) is not migrated")
    open(fp, "wb").write(b"penaltyMin=3\npenaltyMax=8\ncoins.curve=1:2,10:4\n")
    CF.load()
    K.check(int(CF.MIN) == 3 and int(CF.MAX) == 8 and str(CF.SAFE) == "skyy-island-,skyy-shard-" and abs(float(CC.at(10)) - 4.0) < 1e-12,
            "LOAD typed values read; an absent safe list = the default")
    open(fp, "wb").write(b"penaltyMin=3\npenaltyMax=8\ncoins.curve=garbage\n")
    CF.load()
    K.check(abs(float(CC.at(50)) - 36.8) < 1e-9, "LOAD a bad curve line = the default (WARN)")
    os.remove(fp)
    # ---- CoinMigP7 on the file texts (update() is the whole text step; run() the file path through the kit's History)
    hdr = "#SkyyCoins config - death penalty percent range\n#Thu Oct 15 20:58:59 MDT 2026\n"
    r = MG.update(hdr + "penaltyMax=25\npenaltyMin=10\n")
    K.check(r is not None and int(r[1]) == 2 and str(r[0]) == hdr + "# migrated: " + MARK_ID + str(MG.MARK)[len("# migrated: " + MARK_ID):] + "\npenaltyMax=5\npenaltyMin=5\n",
            "MIG 10 / 25 -> 5 / 5 in place, the date header kept, the marker above the first key: %r" % (str(r[0]) if r is not None else None))
    crlf = (hdr + "penaltyMax=25\npenaltyMin=10\n").replace("\n", "\r\n")
    r = MG.update(crlf)
    K.check(r is not None and int(r[1]) == 2 and str(r[0]).count("\r\n") == crlf.count("\r\n") + 1 and "\n" not in str(r[0]).replace("\r\n", ""), "MIG CRLF kept on every line")
    r = MG.update(hdr + "penaltyMax=12\npenaltyMin=7\n")
    K.check(r is not None and int(r[1]) == 0 and "penaltyMin=7" in str(r[2]) and str(r[0]).endswith("penaltyMax=12\npenaltyMin=7\n"), "MIG a /deathpenalty-set pair (7-12) is kept + named")
    r = MG.update(hdr + "penaltyMax=25\npenaltyMin=5\n")
    K.check(r is not None and int(r[1]) == 0 and "penaltyMax=25" in str(r[0]), "MIG half at the old default (min hand-set to 5): both kept")
    r = MG.update("penaltyMin=10\n")
    K.check(r is not None and int(r[1]) == 0, "MIG only one of the two keys: kept (absent = default)")
    K.check(MG.update(hdr + str(MG.MARK) + "\npenaltyMax=25\npenaltyMin=10\n") is None, "MIG a file with the marker: nothing")
    # run() through the kit: History copy, change log, marker; second run nothing
    d2 = os.path.join(scratch, "x2", "mods", "Skyy_SkyyCoins")
    os.makedirs(d2, exist_ok=True)
    fp2 = os.path.join(d2, "config.properties")
    open(fp2, "wb").write((hdr + "penaltyMax=25\npenaltyMin=10\n").encode("latin-1"))
    CF.FILE = P(fp2)
    CF.load()
    K.check(int(CF.MIN) == 10 and int(CF.MAX) == 25, "RUN the old file reads 10-25 before the update")
    msg = str(MG.run(CF.FILE))
    after = open(fp2, "rb").read().decode("latin-1")
    K.check("5 % of the carried coins" in msg and int(CF.MIN) == 5 and int(CF.MAX) == 5 and after.startswith(hdr) and after.endswith("penaltyMax=5\npenaltyMin=5\n"),
            "RUN moved + re-read: %s" % msg[:90])
    hist = os.path.join(d2, "config-history")
    baks = [x for x in os.listdir(hist)] if os.path.isdir(hist) else []
    K.check(any(open(os.path.join(hist, b_), "rb").read() == (hdr + "penaltyMax=25\npenaltyMin=10\n").encode("latin-1") for b_ in baks if os.path.isfile(os.path.join(hist, b_))),
            "RUN History holds the old file byte for byte: %s" % baks)
    logs = [os.path.join(dp_, fn_) for dp_, dn_, fns in os.walk(d2) for fn_ in fns if "change" in fn_]
    lt = "".join(open(x, encoding="latin-1").read() for x in logs)
    K.check("SkyyCoins 0.1.10\t-\tupdate\tpenaltyMin\t10\t5\tok" in lt and "update\tpenaltyMax\t25\t5\tok" in lt, "RUN one change-log row per key (Undo in Server Setup -> Changes): %s" % logs)
    K.eq(str(MG.run(CF.FILE)), "", "RUN a second start does nothing")
    K.eq(open(fp2, "rb").read().decode("latin-1"), after, "RUN the file is unchanged by the second start")
    # ---- the kit end to end on a fresh folder: the rows, a typed curve refused, a min change writes the line in place
    d3 = os.path.join(scratch, "x3", "mods", "Skyy_SkyyCoins")
    os.makedirs(d3, exist_ok=True)
    open(os.path.join(d3, "config.properties"), "wb").write((hdr + "penaltyMax=25\npenaltyMin=10\n").encode("latin-1"))
    L2 = T16.loader_for(jar)
    J2 = lambda n: JClass(PKG + n, loader=L2)
    m3 = setup_kit(J2, d3)
    K.check("5 %" in m3 and int(J2("CoinConfig").MIN) == 5, "KIT setup order: the update runs before the kit starts")
    Fn2, CC2, CF2 = J2("CfgFn"), J2("CoinCurve"), J2("CoinConfig")
    rb = str(Fn2.cmdSetConsole("coins.curve", "10:1,5:2"))
    K.check(str(CC2.TEXT) == CURVE_TEXT, "KIT a curve with falling levels is refused (field unchanged): %s" % rb[:80])
    rg = str(Fn2.cmdSetConsole("coins.curve", "1:1,100:50"))
    K.check(str(CC2.TEXT) == "1:1,100:50" and abs(float(CC2.at(100)) - 50) < 1e-9, "KIT a good curve applies at once (after=): %s" % rg[:60])
    rm = str(Fn2.cmdSetConsole("penaltyMin", "7"))
    rx = str(Fn2.cmdSetConsole("penaltyMax", "12"))
    K.check(int(CF2.MIN) == 7 and int(CF2.MAX) == 12, "KIT penaltyMin / Max set live: %s / %s" % (rm[:50], rx[:50]))
    rs = str(Fn2.cmdSetConsole("penalty.safeWorlds", "skyy-island-"))
    K.check(str(CF2.SAFE) == "skyy-island-" and not bool(CF2.safeWorld("skyy-shard-x")), "KIT the safe list set live: %s" % rs[:50])
    J2("CfgPub").shutdown()
    t3 = open(os.path.join(d3, "config.properties"), "rb").read().decode("latin-1")
    K.check(t3.startswith(hdr) and "penaltyMin=7" in t3 and "penaltyMax=12" in t3 and "coins.curve=1:1,100:50" in t3 and "penalty.safeWorlds=skyy-island-" in t3,
            "KIT lines written in place, the date header kept: %r" % t3[-160:])
    CF2.load()
    K.check(int(CF2.MIN) == 7 and int(CF2.MAX) == 12 and str(CF2.SAFE) == "skyy-island-", "KIT a restart reads the edited file")
    # ---- static: setup order + the death call site
    gen = open(os.path.join(HERE, "build_skyycoins_%s.py" % VERSION), encoding="utf8").read()
    i_load, i_mig, i_kit = gen.index("{PKG}.CoinConfig.load();\n  String p7"), gen.index("{PKG}.CoinMigP7.run("), gen.index("{PKG}.CfgPub.start(")
    K.check(i_load < i_mig < i_kit, "STATIC setup: load -> CoinMigP7 -> kit")
    K.check(gen.count("{PKG}.CoinConfig.lossOf(balNow, wn, pct)") == 1 and "coins in the bank are safe" in gen, "STATIC the death task uses lossOf and names the bank")
    K.check('bridge().put("coins:fn:curve"' in gen and 'bridge().remove("coins:fn:curve")' in gen, "STATIC coins:fn:curve published + removed at shutdown")
    K.check("{PKG}.CoinConfig.save();\n    pr.sendMessage" not in gen and gen.count('{PKG}.CfgFn.cmdSet("penaltyMin"') == 2, "STATIC /deathpenalty writes through the kit rows")
    K.save()


def run_live(out, jar, scratch, home):
    import json
    from jpype import JClass
    tmp = os.path.join(scratch, "live16.json")
    T16.run_live(tmp, jar, scratch, home)          # 0.1.6: every live purse reads the same as the pinned jar, nothing written
    prev = json.load(open(tmp))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = prev["ok"], list(prev["fails"]), list(prev["notes"])
    cfg0 = open(os.path.join(home, "config.properties"), "rb").read().decode("latin-1")
    h0 = HK.tree_hash(home)
    bal0 = HK.tree_hash(os.path.join(home, "balances"))
    snaps, msgs = [], []
    for start in (1, 2):
        L = T16.loader_for(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        msgs.append(setup_kit(J, home))
        K.note = None
        if start == 1:
            K.check(int(J("CoinConfig").MIN) == (5 if "penaltyMin=10" in cfg0 and "penaltyMax=25" in cfg0 else int(J("CoinConfig").MIN)),
                    "DL1: after the update the live copy runs at %s-%s %%" % (J("CoinConfig").MIN, J("CoinConfig").MAX))
        J("CfgPub").shutdown()
        snaps.append(HK.tree_hash(home))
    new = sorted(set(snaps[0]) - set(h0))
    changed = sorted(k for k in h0 if snaps[0].get(k) != h0[k])
    K.check(changed == ["config.properties"] and all(n.startswith(("config-history", "config-changes")) for n in new),
            "DL the first start changes only config.properties (+ kit history / change files): changed %s new %s" % (changed, new))
    K.check(snaps[0] == snaps[1] and msgs[1] == "", "DL the second start changes nothing")
    K.check(HK.tree_hash(os.path.join(home, "balances")) == bal0, "DL no balance file changed")
    cfg1 = open(os.path.join(home, "config.properties"), "rb").read().decode("latin-1")
    exp = cfg0.replace("penaltyMax=25", "penaltyMax=5").replace("penaltyMin=10", "penaltyMin=5")
    lines0 = [x for x in cfg0.split("\n")]
    first_key = [i for i, x in enumerate(lines0) if x and not x.startswith("#")][0]
    exp = "\n".join(lines0[:first_key] + [x for x in cfg1.split("\n") if MARK_ID in x] + exp.split("\n")[first_key:])
    K.check(cfg1 == exp, "DL config.properties = the live text with exactly the two values moved and the marker above the first key")
    K.notes.append("DL live config before: %r -> after: %r; INFO: %s" % (cfg0, cfg1, msgs[0]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyCoins", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyCoins"))
