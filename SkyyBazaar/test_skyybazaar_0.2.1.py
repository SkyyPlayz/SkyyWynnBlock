"""Harness for SkyyBazaar 0.2.1 (BALANCE PASS P7: the price table by tier, every other product on its 0.2.0 ratio, impactCoins 22,500, migrate021;
tools/bazaar_0_2_1_patch.py). Build first:
    python tools/bazaar_0_2_1_patch.py && python SkyyBazaar/build_skyybazaar_0.2.1.py --with SkyyMerchants/SkyyMerchants-0.1.7.jar
    python SkyyBazaar/test_skyybazaar_0.2.1.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; line endings kept; no new command / system; setup order migrate122 -> migrate021 -> load
  A     verify   every class loads + initialises
  C     compare  0.2.0 -> 0.2.1 (EXPECT below)
  T     table    the jar's re-price table (Catalog.M021_*) = tools/balance_model.py p7_table() for every ore / log / crop anchor, rubble 2.25 (every Rock_* kept),
                 no Eternal seed bag moved, every moved price %g-exact; the model's checks (skills within 0.85-1.15 per zone, on G, 1.2x steps,
                 the floor, 17 loop routes) pass
  Q     quote    a FRESH folder through the jar's own setup steps (every one-time update, load, reprice, publish): impactCoins 22,500; every
                 product's instant buy > instant sell at demand 1 (the floor on); Copper Ore sells 5, Cobblestone 3 (its sell cap 3.67), Wheat 4, Iron
                 Ore 6, Oak 7 (fixer: mined stone counts at the cobble price, so Zone 1 ores sell less); the fresh pricing.properties carries migrated.0.2.1 (nothing to migrate)
  D     live     a scratch COPY of the live NewBetaTest Skyy_SkyyBazaar through the same steps TWICE: the first moves exactly the lines still at
                 their 0.2.0 default (one MIGRATE-0.2.1 PRICE line with the undo each), keeps every other price (logged), impactCoins 45000 ->
                 22500 in place (the date header kept), the verified config-history copies, the marker last; book / orders untouched; the second
                 start writes nothing
  D2    live2    the same with an admin's price on a re-priced product (kept + a KEPT line) and an admin's impactCoins (kept)
  AA    audit    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, subprocess, importlib.util, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.2.1"
PKG = "com.skyy.bazaar."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.2.0.jar")
GEN = os.path.join(HERE, "build_skyybazaar_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyybazaar_0.2.0.py")
PATCH = os.path.join(ROOT, "tools", "bazaar_0_2_1_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp7", "bz")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyBazaar")
EXPECT = {"Catalog": ["+f IMP021_NEW", "+f IMP021_OLD", "+f IMP021_TXT", "+f M021_ID", "+f M021_LOG", "+f M021_NEW", "+f M021_OLD", "+f M021_OTXT",
                      "+f M021_TXT", "+f MIGRATED021", "+m m021", "+m migrate021", "~<clinit>", "~m loadModes", "~m writeModes"],
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "Market": ["~<clinit>", "~m load"], "SkyyBazaarPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
MIGS = ("migrate", "migrate14", "migrate19", "migrate110", "migrate114", "migrate115", "migrate116", "migrate119", "migrate120", "migrate122p", "migrate122", "migrate021")


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


def bz_prep(J, home):
    """the jar's data steps as SkyyBazaarPlugin.setup() runs them (every one-time update, load, reprice, publish); returns the MIGRATE lines"""
    from jpype import JClass
    J("BzUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar")
    d = JClass("java.nio.file.Paths").get(home)
    os.makedirs(home, exist_ok=True)
    C = J("Catalog")
    C.FILE = d.resolve("products.properties")
    C.PFILE = d.resolve("pricing.properties")
    J("Market").FILE = d.resolve("market.properties")
    J("Market").LOGFILE = d.resolve("trades.log")
    J("BzCfg").load(d)
    logs = []
    for m in MIGS:
        r = getattr(C, m)()
        if m == "migrate021" and r is not None:
            logs += [str(x) for x in list(C.M021_LOG)]
    C.load()
    J("Market").load()
    C.reprice()
    J("Market").publishAll()
    C.flushIfDirty()
    for x in logs:
        J("Market").log(x)
    C.M021_LOG.clear()
    J("Market").flushLog()
    return logs


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.1"') == 1 and g.startswith('"""SkyyBazaar 0.2.1'), "S version + header")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    su = g[g.index("String mig122 = @PKG@.Catalog.migrate122();"):]
    K.check(su.index("migrate122();") < su.index("migrate021();") < su.index("@PKG@.Catalog.load();"), "S setup: migrate122 -> migrate021 -> load")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _rosters_lowest_zone():
    """item id -> the lowest vanilla zone (1-4) whose world spawns drop it (Assets.zip, read-only) - the harness's own copy of rule 9's roster read"""
    import zipfile, re
    z = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    try:
        names = z.namelist()

        def js(n):
            try:
                return json.loads(z.read(n).decode("utf-8-sig"))
            except Exception:
                return None
        roles = dict((x.rsplit("/", 1)[1][:-5], x) for x in names if x.startswith("Server/NPC/Roles/") and x.endswith(".json"))
        drops = dict((x.rsplit("/", 1)[1][:-5], x) for x in names if x.startswith("Server/Drops/") and x.endswith(".json"))

        def items(c, out, d=0):
            if not isinstance(c, dict) or d > 12:
                return
            for k in c.get("Containers", []) or []:
                items(k, out, d + 1)
            if c.get("Type") == "Single" and (c.get("Item") or {}).get("ItemId"):
                out.add(c["Item"]["ItemId"])
            if c.get("Type") == "Droplist":
                items((js(drops.get(c.get("DroplistId"), "")) or {}).get("Container"), out, d + 1)

        def dl(r, seen=()):
            j = js(roles[r]) or {}
            v = (j.get("Modify") or {}).get("DropList") or j.get("DropList")
            if isinstance(v, dict):
                v = ((j.get("Parameters") or {}).get(v.get("Compute")) or {}).get("Value")
            if isinstance(v, str) and v:
                return v
            ref = j.get("Reference")
            return dl(ref, seen + (ref,)) if ref in roles and ref not in seen else None
        low = {}
        for n in names:
            if not (n.startswith("Server/NPC/Spawn/World/") and n.endswith(".json")):
                continue
            j = js(n) or {}
            zs = [int(m.group(1)) for m in (re.match(r"Env_Zone([1-4])_", e or "") for e in (j.get("Environments") or [])) if m]
            if not zs:
                continue
            for npc in j.get("NPCs") or []:
                r = npc.get("Id")
                d_ = dl(r) if r in roles else None
                if not d_ or d_ not in drops:
                    continue
                s = set()
                items((js(drops[d_]) or {}).get("Container"), s)
                for i in s:
                    low[i] = min(low.get(i, 9), min(zs))
        return low
    finally:
        z.close()


def run_table(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    bm = tmod(os.path.join(ROOT, "tools", "balance_model.py"), "bm_p7")
    import tier_tags as TT
    C = JClass(PKG + "Catalog")
    ids = [str(x) for x in C.M021_ID]
    old = dict(zip(ids, [float(x) for x in C.M021_OLD]))
    new = dict(zip(ids, [float(x) for x in C.M021_NEW]))
    txt = dict(zip(ids, [str(x) for x in C.M021_TXT]))
    tab = bm.p7_table()
    want = {}
    for n in bm.P7_ORE_T:
        for i in ("Ore_%s" % n, "Ore_%s_SkyWynn" % n):
            want[i] = tab["ore"][n]
    for c in bm.P7_CROP_T:
        want["Plant_Crop_Mushroom_Cap_Brown" if c == "Mushroom" else "Plant_Crop_%s_Item" % c] = tab["crop"][c]
    bad = []
    for i, v in want.items():
        if i in new and abs(new[i] - v) > 1e-9:
            bad.append((i, new[i], v))
    ores = [i for i in ids if i.startswith("Ore_") and i in want]
    K.check(not bad and len(ores) == 11, "T every ore / crop anchor = tools/balance_model.py p7_table() (%d ores; off %s)" % (len(ores), bad[:4]))
    logs = [i for i in ids if TT.family(i) == "log"]
    K.check(logs and all(abs(new[i] - tab["log"][TT.tier(i)]) < 1e-9 for i in logs), "T every log = its tier's P7 price, every species the same (%d)" % len(logs))
    # fixer: every Rock_* keeps its 0.2.0 price (cobble 4.5 = 2 rubble - the salvage chain), rubble stays 2.25 (already there)
    K.check(not [i for i in ids if i.startswith("Rock_") and not i.startswith("Rock_Gem_")] and all(new[i] == 2.25 for i in ids if i.startswith("Rubble_")),
            "T no plain Rock_* moves (cobble keeps 4.5 = 2 rubble), rubble 2.25")
    K.check(all(new[i] >= 4.5 for i in ids if i.startswith("Wood_") and i.endswith("_Planks")), "T fix: every moved plank >= 4.5 (2 sticks: 1 plank -> 2 halves -> 2 sticks)")
    K.check(not [i for i in ids if i.endswith("_Eternal")], "T no Eternal seed bag moved")
    K.check(all(float(txt[i]) == new[i] and ("%g" % new[i]) == txt[i] for i in ids), "T every moved price prints exactly (%g)")
    K.check(sum(1 for i in ids if new[i] < old[i]) > 0.9 * len(ids), "T most prices fall (%d of %d)" % (sum(1 for i in ids if new[i] < old[i]), len(ids)))
    # fix (critic): RULE 9 - the combat family moves by ONE factor per zone (the vanilla rosters, read here on their own), dearer from Zone 2 up
    zon = _rosters_lowest_zone()
    byz = {}
    for i in ids:
        if i in zon and old[i] > 0 and i.startswith("Ingredient_") and not i.startswith(("Ingredient_Bar_", "Ingredient_Fabric_Scrap_Linen", "Ingredient_Hide_Heavy", "Ingredient_Powder_", "Ingredient_Crystal_")):
            byz.setdefault(zon[i], []).append((i, new[i] / old[i]))
    f1 = [r for _i, r in byz.get(1, [])]
    K.check(len(f1) >= 8 and max(f1) / min(f1) < 1.08 and 0.3 < f1[0] < 1.5,
            "T rule 9: the Zone 1 combat drops share one factor (%d, x%.3f-%.3f)" % (len(f1), min(f1 or [0]), max(f1 or [0])))
    hi = [(z, i, r) for z in (2, 3, 4) for i, r in byz.get(z, [])]
    K.check(hi and all(r > 3 * max(f1) for _z, _i, r in hi), "T rule 9: each Zone 2-4 own drop is dearer than Zone 1's factor: %s" % ", ".join("Z%d %s x%.3g" % x for x in hi))
    K.check(abs(new.get("Ingredient_Hide_Light", 0) / old.get("Ingredient_Hide_Light", 1) - 0.5) > 0.05,
            "T rule 9: no more flat x0.5 fallback (Light Hide x%.3f)" % (new.get("Ingredient_Hide_Light", 0) / old.get("Ingredient_Hide_Light", 1)))
    rows = bm.p7_rows()
    K.check(all(r[2] for r in rows), "T the model's P7 checks all pass (%d rows): %s" % (len(rows), [r[0] for r in rows if not r[2]][:3]))
    K.check(abs(float(C.IMP021_OLD) - 45000.0) < 1e-9 and abs(float(C.IMP021_NEW) - 22500.0) < 1e-9 and abs(float(JClass(PKG + "Market").IMPACT) - 22500.0) < 1e-9,
            "T impactCoins 45000 -> 22500 (Market default)")
    K.notes.append("T samples: " + ", ".join("%s %g -> %g" % (i, old[i], new[i]) for i in ("Ore_Copper", "Ore_Iron", "Ore_Mithril", "Wood_Oak_Trunk", "Plant_Crop_Wheat_Item",
                                                                                         "Plant_Crop_Corn_Item", "Rock_Stone_Cobble", "Skyy_Ench_Copper", "Ingredient_Bar_Lead_SkyWynn") if i in new))
    K.save()


def run_quote(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    J = lambda n: JClass(PKG + n)
    d = os.path.join(scratch, "fresh", "Skyy_SkyyBazaar")
    bz_prep(J, d)
    C, M = J("Catalog"), J("Market")
    K.check(abs(float(M.IMPACT) - 22500.0) < 1e-9, "Q a fresh market.properties: impactCoins 22,500 (%s)" % M.IMPACT)
    pt = open(os.path.join(d, "pricing.properties"), encoding="latin-1").read()
    K.check("migrated.0.2.1=" in pt, "Q the fresh pricing.properties carries migrated.0.2.1")
    ids = sorted(str(p.id) for p in C.all())
    bad = [(i, int(M.quote(i, 1, True)), int(M.quote(i, 1, False))) for i in ids if int(M.quote(i, 1, True)) <= int(M.quote(i, 1, False))]
    K.check(not bad and len(ids) >= 540, "Q every product (%d): instant buy > instant sell at demand 1 (%s)" % (len(ids), bad[:4]))
    low = [(i, int(M.quote(i, 1, False))) for i in ids if int(M.quote(i, 1, False)) < 2]
    K.check(not low, "Q nothing sells under 2 coins (%s)" % low[:4])
    sv = dict((i, int(M.quote(i, 1, False))) for i in ("Ore_Copper", "Ore_Iron", "Rock_Stone_Cobble", "Plant_Crop_Wheat_Item", "Wood_Oak_Trunk", "Plant_Crop_Corn_Item"))
    bv = dict((i, int(M.quote(i, 1, True))) for i in sv)
    K.check(sv["Rock_Stone_Cobble"] == 3 and 4 <= sv["Ore_Copper"] <= 6 and 5 <= sv["Ore_Iron"] <= 7 and 3 <= sv["Plant_Crop_Wheat_Item"] <= 5 and 6 <= sv["Wood_Oak_Trunk"] <= 8,
            "Q sells: %s; buys: %s" % (sv, bv))
    K.notes.append("Q sells %s buys %s" % (sv, bv))
    K.save()


def live_run(K, jar, scratch, home, label, hand=None):
    from jpype import JClass
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    J = lambda n: JClass(PKG + n)
    C = J("Catalog")
    names = ("products.properties", "pricing.properties", "market.properties", "trades.log", "book.properties", "orders.properties", "config.properties")
    before = dict((n, open(os.path.join(home, n), "rb").read()) for n in names if os.path.isfile(os.path.join(home, n)))
    K.check(b"migrated.0.2.1=" not in before["pricing.properties"], "%s: the live copy has not run 0.2.1" % label)
    hd = os.path.join(home, "config-history")
    bak0 = set(os.listdir(hd)) if os.path.isdir(hd) else set()
    logs = bz_prep(J, home)
    after = dict((n, open(os.path.join(home, n), "rb").read()) for n in names if os.path.isfile(os.path.join(home, n)))
    for n in ("book.properties", "orders.properties", "config.properties"):
        if n in before:
            K.check(after.get(n) == before[n], "%s: %s byte-identical (orders / escrow / settings untouched)" % (label, n))
    K.check(after["pricing.properties"].startswith(before["pricing.properties"]) and b"migrated.0.2.1=" in after["pricing.properties"], "%s: the marker appended last" % label)
    ids = [str(x) for x in C.M021_ID]
    rp = dict(zip(ids, zip([float(x) for x in C.M021_OLD], [float(x) for x in C.M021_NEW], [str(x) for x in C.M021_OTXT], [str(x) for x in C.M021_TXT])))
    b, a = before["products.properties"], after["products.properties"]
    nl = b"\r\n" if b"\r\n" in b else b"\n"
    bl, al = b.rstrip(nl).split(nl), a.rstrip(nl).split(nl)
    K.check(len(bl) == len(al), "%s: no line added / removed (%d)" % (label, len(bl)))
    moved, kept, autos, bad = [], [], [], []
    for x, y in zip(bl, al):
        if x.startswith(b"#") or b"=" not in x:
            K.check(x == y, "%s: a comment line is kept" % label)
            continue
        i = x.split(b"=")[0].decode("latin-1")
        po, pn = float(x.split(b",")[1]), float(y.split(b",")[1])
        if x == y:
            if i in rp and abs(po - rp[i][1]) > 1e-9:
                kept.append((i, po))
            continue
        if i in rp and abs(po - rp[i][0]) < 1e-9 and abs(pn - rp[i][1]) < 1e-9 and x.split(b",")[0] == y.split(b",")[0] and x.rsplit(b",", 1)[1] == y.rsplit(b",", 1)[1]:
            moved.append(i)
        elif bool(C.isAuto(i)):
            autos.append(i)
        else:
            bad.append((i, po, pn))
    K.eq(bad, [], "%s: every changed line is a 0.2.0 default -> 0.2.1 default (price text only) or an AUTO good" % label)
    tl = after["trades.log"][len(before.get("trades.log", b"")):].decode("utf-8", "replace")
    K.check(all(("MIGRATE-0.2.1 PRICE %s %s -> %s (undo: /bazaaradmin price %s %s)" % (i, rp[i][2], rp[i][3], i, rp[i][2])) in tl for i in moved),
            "%s: each moved line has its MIGRATE-0.2.1 PRICE line with the undo (%d)" % (label, len(moved)))
    K.check(all(("MIGRATE-0.2.1 KEPT " + i + " ") in tl for i, _p in kept), "%s: each kept price is logged (%s)" % (label, kept[:6]))
    mk0, mk1 = before.get("market.properties", b""), after.get("market.properties", b"")
    if b"impactCoins=45000" in mk0:
        K.check(b"impactCoins=22500.0" in mk1 and mk1.split(b"\n")[0] == mk0.split(b"\n")[0], "%s: impactCoins 45000 -> 22500 in place, the header kept" % label)
    new_bak = sorted(set(os.listdir(hd)) - bak0) if os.path.isdir(hd) else []
    K.check(any(open(os.path.join(hd, x_), "rb").read() == b for x_ in new_bak), "%s: the old products.properties is in config-history (%s)" % (label, new_bak))
    K.notes.append("%s: %d lines moved, %d kept (%s), %d AUTO lines followed their inputs; head %s" % (label, len(moved), len(kept), kept[:5], len(autos), logs[:1]))
    h0 = HK.tree_hash(home)
    bz_prep(J, home)
    h1 = HK.tree_hash(home)
    K.check(h0 == h1, "%s: a second start writes nothing (%s)" % (label, sorted(k for k in set(h0) | set(h1) if h0.get(k) != h1.get(k))[:5]))
    return moved, kept


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    live_run(K, jar, scratch, home, "LIVE")
    K.save()


def run_live2(out, jar, scratch, home):
    K = HK.Child(out)
    fp = os.path.join(home, "products.properties")
    raw = open(fp, "rb").read()
    nl0 = b"\r\n" if b"\r\n" in raw else b"\n"
    old_l = [l for l in raw.split(nl0) if l.startswith(b"Ore_Iron=")][0]
    hand = old_l.replace(b",72,", b",73,")
    assert hand != old_l
    open(fp, "wb").write(raw.replace(nl0 + old_l + nl0, nl0 + hand + nl0))
    mp = os.path.join(home, "market.properties")
    if os.path.isfile(mp):
        m = open(mp, "rb").read()
        if b"impactCoins=45000" in m:
            open(mp, "wb").write(m.replace(b"impactCoins=45000.0", b"impactCoins=30000").replace(b"impactCoins=45000", b"impactCoins=30000"))
    moved, kept = live_run(K, jar, scratch, home, "LIVE2")
    K.check(("Ore_Iron", 73.0) in kept and "Ore_Iron" not in moved, "LIVE2: an admin's Iron Ore price (73) is kept")
    if os.path.isfile(mp):
        K.check(b"impactCoins=30000" in open(mp, "rb").read() or b"impactCoins=30000.0" in open(mp, "rb").read(), "LIVE2: an admin's impactCoins is kept")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("table", run_table), ("quote", run_quote), ("live", run_live), ("live2", run_live2)],
           live=(LIVE, "Skyy_SkyyBazaar"), script=__file__)
