"""Bare-JVM harness for SkyyAccessories 0.5.13 - THE WORKBENCH TAB ORDER (tools/accessories_0_5_13_patch.py; Skyy 2026-10-13: "since the
tutorial asks you to craft this, id move it to the top. sort them by tier, and per tier,m sort them by easiest to craft.").

    python SkyyAccessories/test_skyyaccessories_0.5.13.py [--jar <0.5.13 jar>] [--old <0.5.12 jar>] [--sacks <SkyySacks jar>] [--dir <scratch>]
                                                          [--live <folder>] [--keep]

Every JVM = the game's JRE, -Xverify:all, -XX:-UsePerfData, java.io.tmpdir / TEMP / TMP in the scratch folder.
  O  the order, computed HERE independently from the new jar's own item JSONs + Assets.zip (read-only) with the build's material table:
     Workbench Accessory I first, tiers ascending (item rarity, no exceptions: the Unique-coloured Accessory Bag = 2), cost then English name ascending inside a tier, every
     upgrade after what it consumes, Omni Accessory last
JVM 1 (both jars, each in its own class loader):
  A  every class of both jars loads, verifies and initialises
  B  0.5.12 -> 0.5.13 class compare: the same classes; changed beyond the version string = exactly WbRank (config kit Cfg* listed, never a
     fail); every non-class file byte-identical except manifest.json (items, recipes, lang, art unchanged)
  R  the new WbRank EXECUTED: ORDER / TIER = the independent order; rank() == the Python mirror on every id (tab ids, recipe ids, edge ids,
     old bag ids, vanilla ids); Collections.sort with the comparator = the mirror; the 0.5.12 WbRank still = the shared kit's rank_py
     (control); a future line sorts after its tier's listed recipes and before the next tier / the Omni
  L  start twice on a scratch COPY of the live Skyy_SkyyAccessories folder: no file changed
JVM 2 (the new jar + the live SkyySacks jar on the class path - both Workbench tab copies):
  W  the shared kit's harness_checks (tools/skyywbtab.py, unchanged) with the NEW order as its expectation: the tab added / idempotent /
     owner wins in both start orders, copy-on-write, overridden Workbench definitions, the asset-reload path, recipe reloads keep the
     order, a REAL SimpleCraftingWindow's windowData craftableRecipes (what the client receives) = Workbench Accessory I first ... Omni
     last. Waived (printed): the checks that SkyySacks' OWN fallback comparator equals the new order (it keeps the old kit order; with
     SkyyAccessories running the owner's set always wins - asserted in both start orders) and the kit's "future line right after
     Legendary Speed" (replaced by R's future-line check).
JVMs 3-5 (the 0.5.12 harness's children, unchanged): Q21 the real entity tracker Lantern checks on the 0.5.13 jar; S the seeded Lantern
  scenario on 0.5.12 and 0.5.13 - traces IDENTICAL, fast path / safety net / OWNER writes as in 0.5.12.
Nothing outside the scratch folder is written (default tools/dev/scratch/accsort/acc0513, deleted at the end unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, struct, zipfile, subprocess
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.5.13", "0.5.12"
PKG = "com.skyy.accessories."
BUILD = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
H0512 = os.path.join(HERE, "test_skyyaccessories_0.5.12.py")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


SCRATCH_ROOT = os.path.abspath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "accsort", "acc0513")))
assert SCRATCH.startswith(SCRATCH_ROOT + os.sep), "--dir must be inside tools/dev/scratch/"
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD_VERSION)))
SACKS = os.path.abspath(arg("--sacks", os.path.join(ROOT, "SkyySacks", "SkyySacks-0.8.1.jar")))
LIVE = os.path.abspath(arg("--live", os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData",
                                                   "Saves", "HUD mod", "mods", "Skyy_SkyyAccessories")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
FIRST, OMNI, BAG = "Skyy_Accessory_Workbench_T1", "Skyy_Accessory_Omni", "Skyy_Accessory_Bag"
SUF = "_Recipe_Generated_0"


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


# ============================================================================================================== O. the independent order
def build_tables():
    """MAT_TIER / ORD_BASE / ORD_EXPAND exactly as the build script defines them (its data block, executed alone)"""
    src = open(BUILD, encoding="utf8").read()
    a_, b_ = src.index('ORD_FIRST = "Skyy_Accessory_Workbench_T1"'), src.index("def _ord_items():")
    ns = {"OMNI": OMNI}
    exec(compile(src[a_:b_], BUILD + " [order data]", "exec"), ns)
    return ns


def independent_order(jar):
    import skyybuild as B
    T = build_tables()
    mat, base, expand = T["MAT_TIER"], T["ORD_BASE"], T["ORD_EXPAND"]
    z = zipfile.ZipFile(jar)
    own = dict((os.path.basename(n)[:-5], json.loads(z.read(n))) for n in z.namelist()
               if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    lang = dict(l.split("=", 1) for l in z.read("Server/Languages/en-US/server.lang").decode("utf8").splitlines() if "=" in l)
    z.close()
    az = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    van = dict((os.path.basename(n)[:-5], n) for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    memo = {}

    def cost(i):
        if i in memo:
            return memo[i]
        if i in mat:
            v = Fraction(base) ** (mat[i] - 1)
        else:
            assert i in own or i.startswith(expand), "no tier and no recipe to expand: " + i
            node = own[i] if i in own else json.loads(az.read(van[i]).decode("utf-8-sig"))
            r = node["Recipe"]
            v = sum((cost(x.get("ItemId") or "res:" + x["ResourceTypeId"]) * int(x.get("Quantity", 1)) for x in r["Input"]),
                    Fraction(0)) / int(r.get("OutputQuantity") or 1)
        memo[i] = v
        return v
    q = {"Skyy_Acc_Normal": 1, "Skyy_Acc_Unique": 2, "Skyy_Acc_Rare": 3, "Skyy_Acc_Legendary": 4}
    tab = sorted(i for i, n in own.items() if n.get("Recipe") and any("Workbench_SkyyAccessories" in (b.get("Categories") or [])
                                                                       for b in n["Recipe"].get("BenchRequirement") or []))
    rows = sorted((q[own[i]["Quality"]], cost(i), lang["server.items.%s.name" % i], i) for i in tab
                  if i not in (FIRST, OMNI))
    order = [FIRST] + [r[3] for r in rows]
    tiers = [0] + [r[0] for r in rows]
    az.close()
    return tab, order, tiers, own, dict((i, cost(i)) for i in tab), lang


def run_order_checks():
    tab, order, tiers, own, costs, lang = independent_order(JAR)
    check(len(tab) == 51 and order[0] == FIRST and OMNI not in order and sorted(order + [OMNI]) == tab,
          "O 51 tab recipes: Workbench Accessory I first, the Omni Accessory not in the table (kept last by the kit rule)")
    check(lang["server.items.%s.name" % FIRST] == "Workbench Accessory I", "O the first entry is the item named 'Workbench Accessory I'")
    check(all(tiers[k] <= tiers[k + 1] for k in range(len(tiers) - 1)) and tiers[1:].count(1) >= 15 and 4 in tiers,
          "O tiers ascending (Normal, Unique, Rare, Legendary)")
    ok = True
    for k in range(1, len(order) - 1):
        a_, b_ = order[k], order[k + 1]
        if tiers[k] == tiers[k + 1] and (costs[a_], lang["server.items.%s.name" % a_]) > (costs[b_], lang["server.items.%s.name" % b_]):
            ok = False
    check(ok, "O inside every tier: cost ascending, ties by English name")
    pos = dict((i, k) for k, i in enumerate(order + [OMNI]))
    bad = [(i, x["ItemId"]) for i in tab for x in own[i]["Recipe"]["Input"] if x.get("ItemId") in pos and pos[x["ItemId"]] > pos[i]]
    check(not bad, "O every upgrade lists after what it consumes %s" % bad[:3])
    check(costs[OMNI] == max(costs.values()), "O the Omni Accessory (last) is also the most expensive recipe")
    q = {"Skyy_Acc_Normal": 1, "Skyy_Acc_Unique": 2, "Skyy_Acc_Rare": 3, "Skyy_Acc_Legendary": 4}
    # fixer 1: every entry's tier = the rarity colour the player sees (the Bag included -> the first Unique, not inside the Normal block)
    vis = [q[own[i]["Quality"]] for i in order[1:]]
    check(vis == tiers[1:] and q[own[FIRST]["Quality"]] == 1,
          "O every listed entry's tier = its own rarity colour (no exception)")
    check(own[BAG]["Quality"] == "Skyy_Acc_Unique" and tiers[pos[BAG]] == 2 and tiers[pos[BAG] - 1] == 1
          and pos[BAG] < pos["Skyy_Talisman_Vitality_Uncommon"],
          "O the Accessory Bag (Unique colour) sorts as the first Unique, right after the Normal block (pos %d)" % pos[BAG])
    # fixer 3: the Bag stays pocket-craftable (Fieldcraft) as well as in the tab - docs/answered/bags.md 2026-10-01 lock
    breq = own[BAG]["Recipe"].get("BenchRequirement") or []
    check(any(b.get("Id") == "Fieldcraft" for b in breq)
          and any("Workbench_SkyyAccessories" in (b.get("Categories") or []) for b in breq),
          "O the Accessory Bag recipe is in pocket crafting (Fieldcraft) AND the tab: %r" % [b.get("Id") for b in breq])
    # fixer 2 (interpretation, documented): Farming Bench IV-VII = Legendary rarity, sorted by cost inside tier 4, numerals still ascending
    fb = [pos["Skyy_Accessory_Farmingbench_T%d" % n] for n in range(4, 8)]
    check(fb == sorted(fb) and all(tiers[p_] == 4 for p_ in fb), "O Farming Bench IV < V < VI < VII, all in the Legendary block %s" % fb)
    print("O. order (independent): %s ... %s; tiers %s" % (", ".join(order[:6]), ", ".join(order[-3:] + [OMNI]),
                                                          "/".join(str(tiers.count(t)) for t in (1, 2, 3, 4))))
    return order, tiers


# ============================================================================================================== JVM helpers
def cp_utf8(b):
    n = struct.unpack(">H", b[8:10])[0]
    i, k, out = 10, 1, []
    while k < n:
        tag = b[i]
        if tag == 1:
            ln = struct.unpack(">H", b[i + 1:i + 3])[0]
            out.append((i, i + 3 + ln, b[i + 3:i + 3 + ln]))
            i += 3 + ln
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            i += 5
        elif tag in (5, 6):
            i += 9
            k += 1
        elif tag in (7, 8, 16, 19, 20):
            i += 3
        elif tag == 15:
            i += 4
        else:
            raise ValueError("cp tag %d" % tag)
        k += 1
    return out


SKYYUI = re.compile(r"skyyui [0-9.]+ [0-9a-f]{12}")


def norm(t):
    return SKYYUI.sub("skyyui #", t)


def normcls(b):
    out, last = [], 0
    for s0, e0, t in cp_utf8(b):
        nt = norm(t.decode("utf8").replace(OLD_VERSION, VERSION)).encode("utf8")
        out.append(b[last:s0 + 1])
        out.append(struct.pack(">H", len(nt)) + nt)
        last = e0
    out.append(b[last:])
    return b"".join(out)


def jarfiles(jar):
    z = zipfile.ZipFile(jar)
    out = dict((n, z.read(n)) for n in z.namelist() if not n.endswith("/"))
    z.close()
    return out


def snap(dd):
    out = {}
    for root, _ds, fs in os.walk(dd):
        for f in fs:
            p = os.path.join(root, f)
            out[os.path.relpath(p, dd)] = open(p, "rb").read()
    return out


def startjvm(cp):
    import jpype
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST] + cp, convertStrings=True)


def method_code(jarbytes, meth):
    from jpype import JClass
    pool = JClass("javassist.ClassPool")(True)
    cc = pool.makeClass(JClass("java.io.ByteArrayInputStream")(jarbytes))
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    out = []
    for m in cc.getDeclaredMethods():
        if str(m.getName()) == meth:
            bo = BOS()
            IP.print_(m, PS(bo))
            out.append(str(bo.toString()))
    cc.detach()
    return "\n".join(out)


def mirror(order, tiers):
    import skyywbtab as WB
    old_rank = WB.rank_py
    pos = dict((i, k) for k, i in enumerate(order))

    def rank(rid):
        if rid is None:
            return 9900000
        b = WB.base_py(rid)
        if b in pos:
            return tiers[pos[b]] * 1000000 + 1000 + pos[b]
        r = old_rank(rid)
        return r + 500000 if 1000000 <= r < 5000000 else r
    return rank, old_rank


def probe_ids(order):
    import skyywbtab as WB
    ids = list(order) + [OMNI] + [i + SUF for i in order + [OMNI]] + list(WB.EXPECTED) + [i + SUF for i in WB.EXPECTED]
    ids += WB.EDGE_IDS + WB.VANILLA_WB + ["Skyy_Talisman_Lantern_Common_Recipe_Generated_1", "Skyy_Talisman_Crit_Uncommon",
                                         "Skyy_Accessory_Farmingbench_T8", "Skyy_Accessory_Newbench_T1", "Skyy_Talisman_Vitality_Ring"]
    return ids


# ============================================================================================================== JVM 1
def run_unit():
    from jpype import JClass, JArray, JString
    order, tiers = run_order_checks()
    startjvm([])
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    Paths, System = JClass("java.nio.file.Paths"), JClass("java.lang.System")

    def loader(jar):
        urls = JArray(URL)(1)
        urls[0] = File(jar).toURI().toURL()
        return URLCL(urls, sysl)

    L = {"old": loader(OLD), "new": loader(JAR)}
    F = {"old": jarfiles(OLD), "new": jarfiles(JAR)}
    CB = dict((k, dict((n[:-6].replace("/", "."), b) for n, b in F[k].items() if n.endswith(".class"))) for k in ("old", "new"))
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", BR)
    # ---------------- A
    na = {"old": 0, "new": 0}
    for k in ("old", "new"):
        for n in sorted(CB[k]):
            try:
                Cls.forName(n, True, L[k])
                OKS[0] += 1
                na[k] += 1
            except Exception as e:
                check(False, "A. %s: load %s: %s" % (k, n, e))
    print("A. loaded + verified + initialised: %s %d, %s %d classes (-Xverify:all)" % (OLD_VERSION, na["old"], VERSION, na["new"]))
    if FAILS:
        return
    # ---------------- B
    old, new = CB["old"], CB["new"]
    check(set(new) == set(old), "B. the same classes: %s" % sorted(set(old) ^ set(new)))
    same, vonly, other = 0, [], []
    for n in sorted(set(old) & set(new)):
        if old[n] == new[n]:
            same += 1
            continue
        co, cn = cp_utf8(old[n]), cp_utf8(new[n])
        ok = len(co) == len(cn)
        rebuilt = new[n]
        if ok:
            for (s0, e0, t0), (s1, e1, t1) in reversed(list(zip(co, cn))):
                if t0 == t1:
                    continue
                if norm(t0.decode("utf8").replace(OLD_VERSION, VERSION)) != norm(t1.decode("utf8")):
                    ok = False
                    break
                rebuilt = rebuilt[:s1] + old[n][s0:e0] + rebuilt[e1:]
        if ok and (rebuilt == old[n] or normcls(old[n]) == normcls(new[n])):
            vonly.append(n[len(PKG):])
        else:
            other.append(n[len(PKG):])
    kit = [n for n in other if n.startswith("Cfg")]
    real = sorted(n for n in other if not n.startswith("Cfg"))
    check(real == ["WbRank"], "B. changed beyond the version string = exactly WbRank: %s" % real)
    print("B. classes: %d byte-identical, %d version string only, changed: %s; config kit classes following tools/skyycfg.py: %s"
          % (same, len(vonly), real, kit or "none"))
    fo_ = dict((k, v) for k, v in F["old"].items() if not k.endswith(".class"))
    fn_ = dict((k, v) for k, v in F["new"].items() if not k.endswith(".class"))
    diff = sorted(k for k in set(fo_) | set(fn_) if fo_.get(k) != fn_.get(k))
    check(diff == ["manifest.json"], "B. every non-class file byte-identical but manifest.json (items, recipes, lang, art): %s" % diff)
    mo_, mn_ = json.loads(fo_["manifest.json"]), json.loads(fn_["manifest.json"])
    check(mn_["Version"] == VERSION and dict((k, v) for k, v in mo_.items() if k not in ("Version", "Name")) ==
          dict((k, v) for k, v in mn_.items() if k not in ("Version", "Name")), "B. manifest: only Version / Name")
    # ---------------- R. the new WbRank EXECUTED
    import skyywbtab as WB
    rank, old_rank = mirror(order, tiers)
    RN, RO = JClass(PKG + "WbRank", loader=L["new"]), JClass(PKG + "WbRank", loader=L["old"])
    check([str(x) for x in RN.ORDER] == order and [int(x) for x in RN.TIER] == tiers,
          "R ORDER / TIER in the jar = the independent order (%d ids)" % len(order))
    ids = probe_ids(order)
    bad = [i for i in ids if int(RN.rank(JString(i))) != rank(i)]
    check(not bad and int(RN.rank(None)) == 9900000, "R new WbRank.rank == the mirror on %d ids %s" % (len(ids), bad[:4]))
    badold = [i for i in ids if int(RO.rank(JString(i))) != old_rank(i)]
    check(not badold, "R control: the 0.5.12 WbRank.rank == the shared kit's rank_py %s" % badold[:4])
    jl = JClass("java.util.ArrayList")()
    for i in reversed(ids):
        jl.add(JString(i))
    JClass("java.util.Collections").sort(jl, RN())
    check([str(x) for x in jl] == sorted(ids, key=lambda i: (rank(i), i)), "R Collections.sort(WbRank) = the mirror's order")
    tab_r = [i + SUF for i in order + [OMNI]]
    ts = JClass("java.util.TreeSet")(RN())
    for i in reversed(tab_r):
        ts.add(JString(i))
    got = [str(x) for x in ts]
    check(got == tab_r and got[0] == FIRST + SUF and got[-1] == OMNI + SUF, "R a TreeSet(WbRank) of the 51 recipe ids iterates Workbench "
          "Accessory I first ... Omni Accessory last")
    lg = [int(RN.rank(JString(i + SUF))) for i, t in zip(order, tiers) if t == 4]
    crit = int(RN.rank(JString("Skyy_Talisman_Crit_Epic" + SUF)))
    check(crit > max(lg) and crit < int(RN.rank(JString(OMNI))) and
          int(RN.rank(JString("Skyy_Talisman_Crit_Uncommon"))) < int(RN.rank(JString("Skyy_Talisman_Vitality_Rare"))) and
          int(RN.rank(JString("Skyy_Talisman_Crit_Uncommon"))) > int(RN.rank(JString("Skyy_Accessory_Armor_Bench_T2"))),
          "R a future accessory line sorts after its tier's listed recipes, before the next tier and the Omni Accessory")
    rc = method_code(new[PKG + "WbRank"], "rank")
    check("WbRank.rankOld" in rc and "WbRank.idx" in rc and "ORDER" in rc and "TIER" in rc, "R rank() = the table, then the kit rule (rankOld)")
    cpi = re.compile(r" #\d+ = ")   # constant-pool slot numbers differ between the two class files; the resolved targets must not
    check(cpi.sub(" # = ", method_code(new[PKG + "WbRank"], "rankOld")) == cpi.sub(" # = ", method_code(old[PKG + "WbRank"], "rank")),
          "R rankOld = the 0.5.12 rank instruction for instruction (constant-pool slot numbers aside)")
    print("R. WbRank: %d ids = mirror; TreeSet: %s, %s ... %s" % (len(ids), got[0], got[1], got[-1]))
    # ---------------- L. start twice on a scratch copy of the live folder
    if not os.path.isdir(LIVE):
        print("note: no live Skyy_SkyyAccessories folder - L skipped")
        return
    J = lambda n, k="new": JClass(PKG + n, loader=L[k])
    lm = os.path.join(SCRATCH, "l-mods")
    dlive = os.path.join(lm, "Skyy_SkyyAccessories")
    shutil.copytree(LIVE, dlive)
    before0 = snap(dlive)
    notes = []
    for rnd in range(2):
        J("AccStore").DIR = Paths.get(os.path.join(dlive, "bags"))
        J("AccCfg").FILE = Paths.get(os.path.join(dlive, "config.properties"))
        m51 = str(J("AccCfg").migrate051())
        m55 = str(J("AccCfg").migrate055())
        cs = str(J("AccCfg").load(True))
        J("AccNotice").FILE = Paths.get(os.path.join(dlive, "notices.properties"))
        J("AccNotice").load()
        J("AccLantern").pubLamp()
        J("CfgPub").start(Paths.get(lm), None)
        J("CfgPub").shutdown()
        notes.append((m51, m55, cs[:90]))
    after = snap(dlive)
    chg = sorted(k for k in set(before0) | set(after) if before0.get(k) != after.get(k))
    check(not chg, "L two starts on a copy of the live data: no file changed (%d files) %s" % (len(before0), chg[:4]))
    print("L. two starts on the live copy: %d files unchanged; %s" % (len(before0), notes[-1]))
    BR.clear()


# ============================================================================================================== JVM 2
WAIVE = ("W SkyySacks WbRank.rank == rank_py", "W SkyySacks WbRank sorts like the Python mirror",
         "W start SkyySacks: the tab's recipe set is SkyySacks's TreeSet in the expected order",
         "W a future accessory line sorts into its tier (after the known Legendary lines)")


def run_wb():
    import skyywbtab as WB
    import skyybuild as B
    order, tiers = run_order_checks()
    startjvm([JAR, SACKS])
    rank, old_rank = mirror(order, tiers)
    # the kit's harness, unchanged, fed the NEW order: its rank mirror + its tab-id list (51 recipes + the old bag ids, so the pattern
    # fallback is exercised too) - module globals, read at call time
    ids = sorted(list(order) + [OMNI] + [i for i in WB.EXPECTED if i.startswith("Skyy_Sack_")], key=lambda i: (rank(i), i))
    WB.rank_py = rank
    WB.EXPECTED = ids
    waived = []

    def chk(cond, what):
        if not cond and what.startswith(WAIVE):
            waived.append(what)
            return True
        return check(cond, what)
    try:
        lines = WB.harness_checks(chk, B.SERVER_JAR, mods=("SkyyAccessories", "SkyySacks"))
        for l in lines:
            print(l[:400])
    except Exception as e:
        import traceback
        traceback.print_exc()
        check(False, "W harness_checks error: %s" % e)
    check(ids[0] == FIRST and ids.index(OMNI) > max(ids.index(i) for i in order), "W the expectation itself: Workbench Accessory I first, "
          "Omni after every listed accessory")
    check(len(waived) <= len(WAIVE) + 2 and all(w.startswith(WAIVE) for w in waived), "W waived only the listed checks: %s" % waived)
    print("W. waived (SkyySacks' own fallback order / the old future-line rule): %d - %s" % (len(waived), "; ".join(w[:70] for w in waived)))


# ============================================================================================================== parent
def child(mode, jar, out, extra=(), script=None):
    env = dict(os.environ)
    env.pop("JAVA_TOOL_OPTIONS", None)
    tmp = os.path.join(SCRATCH, "tmp")
    env["TEMP"], env["TMP"] = tmp, tmp
    return subprocess.call([sys.executable, script or os.path.abspath(__file__), "--child", mode, "--cjar", jar, "--out", out, "--dir",
                            SCRATCH] + list(extra), env=env, cwd=ROOT)


def main():
    if "--child" in sys.argv:
        mode, out = arg("--child"), arg("--out")
        try:
            if mode == "unit":
                run_unit()
            elif mode == "wb":
                run_wb()
        except Exception as e:
            import traceback
            traceback.print_exc()
            FAILS.append("harness error (%s): %s" % (mode, e))
        json.dump({"ok": OKS[0], "fails": FAILS}, open(out, "w"))
        return 0
    for j in (JAR, OLD, SACKS):
        if not os.path.isfile(j):
            print("no jar at", j)
            return 1
    if os.path.getmtime(JAR) < os.path.getmtime(BUILD):
        print("the jar is older than", BUILD, "- rebuild it first")
        return 1
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    os.environ["TEMP"] = os.environ["TMP"] = os.path.join(SCRATCH, "tmp")
    res = {}
    for name, mode, jar, extra, script in (("unit", "unit", JAR, (), None), ("wb", "wb", JAR, (), None),
                                           ("q21-new", "q21", JAR, (), H0512),
                                           ("scen-old", "scen", OLD, ("--newjar",), H0512), ("scen-new", "scen", JAR, ("--newjar",), H0512)):
        out = os.path.join(SCRATCH, name + ".json")
        print("---- JVM %s (%s)" % (name, os.path.basename(jar)))
        sys.stdout.flush()
        rc = child(mode, jar, out, extra, script)
        try:
            res[name] = json.load(open(out))
        except Exception as e:
            check(False, "%s: no result (exit %s): %s" % (name, rc, e))
    for k in ("unit", "wb"):
        u = res.get(k, {"ok": 0, "fails": ["missing"]})
        OKS[0] += u["ok"]
        FAILS.extend(u["fails"])
    qn = res.get("q21-new")
    if qn:
        check(not qn["fails"] and qn["ok"] >= 10, "Q21 the real tracker Lantern checks all pass on 0.5.13 (%d ok, fails %s)" % (qn["ok"], qn["fails"][:3]))
        print("Q21. run_tracker (0.5.5 harness via the 0.5.12 harness, unchanged) on 0.5.13: %d ok %d fail" % (qn["ok"], len(qn["fails"])))
    so, sn = res.get("scen-old"), res.get("scen-new")
    if so and sn:
        to, tn = so["trace"], sn["trace"]
        first = next((k for k in range(min(len(to), len(tn))) if to[k] != tn[k]), None)
        check(len(to) == len(tn) and first is None, "S the Lantern scenario traces are IDENTICAL on 0.5.12 and 0.5.13 (first difference: %s)"
              % (None if first is None else (to[first], tn[first])))
        check(sn["FAST"] > 0 and sn["WALKS"] > 0 and sn["FAST"] > 5 * sn["WALKS"] and so["FAST"] == sn["FAST"] and so["WALKS"] == sn["WALKS"],
              "S 0.5.13 takes the 0.5.12 fast path / safety net exactly as 0.5.12 (fast %d / %d, walk %d / %d)"
              % (sn["FAST"], so["FAST"], sn["WALKS"], so["WALKS"]))
        check(sn.get("countset", {}).get("ok") and sn.get("ownerputs") == [0, 1], "S counting set + OWNER writes as in 0.5.12: %s %s"
              % (sn.get("countset"), sn.get("ownerputs")))
        print("S. Lantern scenario: %d trace entries identical on 0.5.12 / 0.5.13; fast %d / walk %d; OWNER writes %s"
              % (len(tn), sn["FAST"], sn["WALKS"], sn.get("ownerputs")))
    print("SkyyAccessories %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:40]:
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP and "--child" not in sys.argv:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
