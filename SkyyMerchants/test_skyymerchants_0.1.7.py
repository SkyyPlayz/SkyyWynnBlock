"""Harness for SkyyMerchants 0.1.7 (BALANCE PASS P7: zones on the 20-level bands, each weapon in its metal's zone, coin-curve prices, price.hours,
MerchMigP7; tools/merchants_0_1_7_patch.py). Build first: python tools/merchants_0_1_7_patch.py && python SkyyMerchants/build_skyymerchants_0.1.7.py

    python SkyyMerchants/test_skyymerchants_0.1.7.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py):
  A   verify   every class loads + initialises
  C   compare  0.1.6 -> 0.1.7: MerchShop (curve / p7round / fallbackPrice / FB_LV / restock), MerchCfg (+ PRICE_HOURS, defaults), + MerchMigP7,
               the kit's rows / files, the plugin setup only
  X   exec     EXECUTES the new code: MerchShop.curveOwn = tools/balance_model.py p7_curve_from_text at every level 0..200; curve() takes
               SkyyCoins' coins:fn:curve when it is on the bridge (a stand-in Function), its own copy when it is missing / answers junk;
               fallbackPrice = the model's p7_merchant_price at Lv 4 .. 104 (Lv 10 15.5k), price.hours 3.75 doubles it, 0 / junk = 1.875;
               the stock table (MerchCfg.load of the default file): Weapon_Sword_Iron-class rows in zone 1, Mithril / Onyxium in no zone
               (zone 5 = no merchant), Adamantite in zone 4; every row's price = the model at its band middle; MerchMigP7.update on the
               live text / a fresh default (marker = nothing) / a hand-edited line (kept + named) / CRLF; run() through the kit's History +
               change log, a second run nothing
  D   live     a scratch COPY of the live NewBetaTest Skyy_SkyyMerchants: MerchMig + MerchMigP7 + MerchCfg.load + the kit TWICE: the first
               changes only config.properties (exactly the 47 zone / weapon lines + the marker; + kit files), the second nothing; the
               merchants registry (merchants/) untouched
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.7"
PKG = "com.skyy.merchants."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMerchants-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMerchants-0.1.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp7", "me")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMerchants")
EXPECT = {"CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
          "MerchCfg": ["+f PRICE_HOURS", "+m dv", "~<clinit>", "~m applyAll", "~m applyScalars", "~m seed"],   # applyAll / seed: the defaults they inline
          "MerchShop": ["+f CV_F", "+f CV_LV", "+f G10", "+m curve", "+m curveOwn", "+m p7round", "~<clinit>", "~m fallbackPrice", "~m restock"],
          "SkyyMerchantsPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["MerchMigP7"]


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


def loader(jar):
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def gen_tables():
    """WEAPONS / WEAPONS_016 / ZONES of the generated script (literals)"""
    import ast
    t = ast.parse(open(os.path.join(HERE, "build_skyymerchants_%s.py" % VERSION), encoding="utf8").read())
    out = {}
    for n in t.body:
        if isinstance(n, ast.Assign):
            for x in n.targets:
                if getattr(x, "id", "") in ("WEAPONS", "WEAPONS_016", "ZONES", "ZONES_016", "MIG7_ROWS"):
                    out[x.id] = ast.literal_eval(n.value)
    return out


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    bm = tmod(os.path.join(ROOT, "tools", "balance_model.py"), "bm_p7")
    import tier_tags as TT
    L = loader(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Shop, Cfg, Mg = J("MerchShop"), J("MerchCfg"), J("MerchMigP7")
    worst = max(abs(float(Shop.curveOwn(lv)) / bm.p7_curve_from_text(bm.P7_CURVE_TEXT, lv) - 1) for lv in range(0, 201))
    K.check(worst < 1e-9, "CURVE the built-in copy = the model's coin curve at every level 0..200 (worst %.1e)" % worst)
    K.check(abs(float(Shop.G10) - bm.p7_G_mid(1)) < 1e-6, "CURVE G10 = the model's focused gathering hour at Lv 10 (%.2f)" % float(Shop.G10))
    br = JClass("java.lang.System").getProperties()
    if br.get("skyy.bridge") is None:
        br.put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    m = br.get("skyy.bridge")

    @JImplements("java.util.function.Function")
    class Fake(object):
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, a):
            return self.ans

    m.put("coins:fn:curve", Fake(JClass("java.lang.Double")(2.0)))
    K.check(abs(float(Shop.curve(50)) - 2.0) < 1e-12, "BRIDGE SkyyCoins' coins:fn:curve answer is used (stand-in 2.0)")
    m.put("coins:fn:curve", Fake("junk"))
    K.check(abs(float(Shop.curve(50)) - 36.8) < 1e-9, "BRIDGE a junk answer -> the built-in copy")
    m.remove("coins:fn:curve")
    K.check(abs(float(Shop.curve(90)) - 466) < 1e-9, "BRIDGE no SkyyCoins -> the built-in copy")
    Cfg.PRICE_HOURS = 1.875
    for lv in (4, 8, 10, 11, 20, 24, 44, 64, 84, 100, 104):
        K.eq(int(Shop.fallbackPrice(None, lv)), bm.p7_merchant_price(lv), "PRICE fallback at Lv %d = the model (1.875 h of G)" % lv)
    K.check(15000 <= int(Shop.fallbackPrice(None, 10)) <= 16000, "PRICE Lv 10 ~15.5k (%d)" % int(Shop.fallbackPrice(None, 10)))
    Cfg.PRICE_HOURS = 3.75
    K.eq(int(Shop.fallbackPrice(None, 10)), bm.p7_merchant_price(10, hours=3.75), "PRICE price.hours 3.75 = twice the hours")
    Cfg.PRICE_HOURS = 0.0
    K.eq(int(Shop.fallbackPrice(None, 10)), bm.p7_merchant_price(10), "PRICE price.hours 0 = the 1.875 default")
    Cfg.PRICE_HOURS = 1.875
    K.check(int(Shop.p7round(15304.0)) == 15500 and int(Shop.p7round(624.0)) == 620 and int(Shop.p7round(195720.0)) == 195000, "PRICE rounding 10 / 100 / 500 / 5,000")
    K.check(list(Shop.FB_LV) == sorted(Shop.FB_LV, key=lambda x: 0) and all(int(v) in (4, 11, 19, 24, 44, 64, 84, 104) for v in Shop.FB_LV),
            "FALLBACK levels = metal band middles only")
    # ---- the default file: zones + stock
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    mods = os.path.join(scratch, "x1", "mods")
    os.makedirs(os.path.join(mods, "Skyy_SkyyMerchants"), exist_ok=True)
    Cfg.load(P(mods))
    zs = dict((str(z.key), (int(z.lo), int(z.hi))) for z in Cfg.ZONES)
    K.eq(zs, {"zone1": (1, 20), "zone2": (20, 40), "zone3": (40, 60), "zone4": (60, 80)}, "ZONES the 20-level bands")
    zone = dict((str(z.key), z) for z in Cfg.ZONES)
    items = dict((str(i.id), i) for i in Cfg.ITEMS)
    gt = gen_tables()
    K.eq(len(items), 44, "STOCK 44 rows read from the default file")
    for i, zn, pr, st, src in gt["WEAPONS"]:
        it = items[i]
        b = None
        for w in i.split("_"):
            if w in TT.LADDER and w in TT.METAL_BANDS:
                b = TT.METAL_BANDS[w]
                break
        if b is not None:
            want_z = min(5, (TT.tier_for_level(b[0]) + 2) // 3)
            K.check(zn == str(want_z), "STOCK %s sold in its metal's zone %d" % (i, want_z))
            K.eq(int(it.price), bm.p7_merchant_price((b[0] + b[1]) // 2), "STOCK %s price = the model at its band middle" % i)
        inz = [k for k, z in zone.items() if bool(it.inZone(z))]
        K.check(inz == (["zone" + zn] if zn != "5" else []), "STOCK %s offered in %s" % (i, inz))
    K.check(not [i for i in items if ("Mithril" in i or "Onyxium" in i) and any(bool(items[i].inZone(z)) for z in zone.values())],
            "STOCK no Mithril / Onyxium weapon in zones 1-4 (no Zone 5 merchant yet)")
    K.check(bool(items["Weapon_Spear_Adamantite_Saurian"].inZone(zone["zone4"])) and bool(items["Sword_Iron_Green"].inZone(zone["zone1"])), "STOCK Adamantite zone 4, Iron zone 1")
    # ---- the migration text step
    live_txt = open(os.path.join(ROOT, "tools", "dev", "scratch", "balp7", "live", "Skyy_SkyyMerchants", "config.properties"), "rb").read().decode("latin-1") \
        if os.path.isfile(os.path.join(ROOT, "tools", "dev", "scratch", "balp7", "live", "Skyy_SkyyMerchants", "config.properties")) else None
    rows = gt["MIG7_ROWS"]
    K.eq(len(rows), 47, "MIG 47 planned lines (3 zones + 44 weapons)")
    old_lines = "".join("%s=%s\n" % (k, o) for k, o, n in rows)
    r = Mg.update("# head\n" + old_lines)
    want = "# head\n" + "".join("%s=%s\n" % (k, n) for k, o, n in rows) + str(Mg.MARK) + "\n"
    K.check(r is not None and int(r[1]) == 47 and str(r[0]) == want, "MIG every 0.1.6 line moves, the marker at the end")
    r2 = Mg.update(("# head\n" + old_lines).replace("\n", "\r\n"))
    K.check(r2 is not None and str(r2[0]) == want.replace("\n", "\r\n"), "MIG CRLF kept")
    hand = ("# head\n" + old_lines).replace("weapon.Sword_Iron_Green=1/2500/1", "weapon.Sword_Iron_Green=1/9999/1")
    r3 = Mg.update(hand)
    K.check(r3 is not None and int(r3[1]) == 46 and "weapon.Sword_Iron_Green=1/9999/1" in str(r3[0]) and "Sword_Iron_Green" in str(r3[2]), "MIG a hand-set price is kept + named")
    K.check(Mg.update(str(Cfg.DEFAULT_TEXT)) is None, "MIG a fresh 0.1.7 file carries the marker (nothing to do)")
    # run() through the kit: History + change log; then nothing
    d2 = os.path.join(scratch, "x2", "mods")
    os.makedirs(os.path.join(d2, "Skyy_SkyyMerchants"), exist_ok=True)
    f2 = os.path.join(d2, "Skyy_SkyyMerchants", "config.properties")
    src_txt = live_txt if live_txt is not None else "# head\n" + old_lines
    open(f2, "wb").write(src_txt.encode("latin-1"))
    msg = str(Mg.run(P(d2)))
    t2 = open(f2, "rb").read().decode("latin-1")
    K.check("47 zone / weapon line(s) moved" in msg and str(Mg.LAST) == "rewrote", "RUN moved: %s" % msg[:100])
    hist = os.path.join(d2, "Skyy_SkyyMerchants", "config-history")
    K.check(os.path.isdir(hist) and any(open(os.path.join(hist, x), "rb").read() == src_txt.encode("latin-1") for x in os.listdir(hist) if os.path.isfile(os.path.join(hist, x))),
            "RUN History holds the old file byte for byte")
    lt = "".join(open(os.path.join(dp, fn), encoding="latin-1").read() for dp, dn, fns in os.walk(os.path.join(d2, "Skyy_SkyyMerchants")) for fn in fns if "change" in fn)
    K.check(lt.count("SkyyMerchants 0.1.7 update\t-\tupdate\t") == 47 and "update\tzone.zone2\tdefault/Env_Zone2/20-30\tdefault/Env_Zone2/20-40\tok" in lt,
            "RUN one change-log row per line (Undo)")
    K.eq(str(Mg.run(P(d2))), "", "RUN a second start does nothing")
    K.eq(open(f2, "rb").read().decode("latin-1"), t2, "RUN the file is unchanged by the second start")
    Cfg.load(P(d2))
    K.eq(dict((str(z.key), (int(z.lo), int(z.hi))) for z in Cfg.ZONES), {"zone1": (1, 20), "zone2": (20, 40), "zone3": (40, 60), "zone4": (60, 80)},
         "RUN the migrated file loads the new bands")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    mods = os.path.dirname(home)
    cfg0 = open(os.path.join(home, "config.properties"), "rb").read().decode("latin-1")
    h0 = HK.tree_hash(home)
    reg0 = HK.tree_hash(os.path.join(home, "merchants")) if os.path.isdir(os.path.join(home, "merchants")) else {}
    snaps, msgs = [], []
    for start in (1, 2):
        L = loader(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        J("MerchLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyMerchants")
        J("MerchMig").run(P(mods))
        msgs.append(str(J("MerchMigP7").run(P(mods))))
        J("MerchCfg").load(P(mods))
        J("CfgPub").start(P(mods), J("MerchLog").LOG)
        zs = dict((str(z.key), (int(z.lo), int(z.hi))) for z in J("MerchCfg").ZONES)
        K.eq(zs, {"zone1": (1, 20), "zone2": (20, 40), "zone3": (40, 60), "zone4": (60, 80)}, "D%d the live copy runs on the 20-level bands" % start)
        J("CfgPub").shutdown()
        snaps.append(HK.tree_hash(home))
    new = sorted(set(snaps[0]) - set(h0))
    changed = sorted(k for k in h0 if snaps[0].get(k) != h0[k])
    K.check(changed == ["config.properties"] and all(n.startswith(("config-history", "config-changes")) for n in new),
            "D the first start changes only config.properties (+ kit files): changed %s new %s" % (changed, new))
    K.check(snaps[0] == snaps[1] and msgs[1] == "", "D the second start changes nothing")
    reg1 = HK.tree_hash(os.path.join(home, "merchants")) if os.path.isdir(os.path.join(home, "merchants")) else {}
    K.check(reg0 == reg1, "D the merchants registry is untouched")
    cfg1 = open(os.path.join(home, "config.properties"), "rb").read().decode("latin-1")
    gt = gen_tables()
    exp = cfg0
    for k, o, n in gt["MIG7_ROWS"]:
        exp = exp.replace("%s=%s\r\n" % (k, o), "%s=%s\r\n" % (k, n)).replace("%s=%s\n" % (k, o), "%s=%s\n" % (k, n))
    K.check(cfg1.startswith(exp.rstrip("\r\n")) and cfg1.count("\n") == cfg0.count("\n") + 1 and "SkyyMerchants 0.1.7 Balance P7 update" in cfg1,
            "D config.properties = the live text with the 47 lines moved + the marker line")
    K.notes.append("D INFO: %s" % msgs[0][:200])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMerchants", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMerchants"))
