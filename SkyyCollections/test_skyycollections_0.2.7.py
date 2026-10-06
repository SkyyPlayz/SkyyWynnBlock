"""Bare-JVM harness for SkyyCollections 0.2.7 - the Lantern recipes unlock from the Tree Sap collection (tools/coll_0_2_7_patch.py;
Skyy 2026-10-05 LOCKED, docs/answered/economy.md). Extends SkyyCollections/test_skyycollections_0.2.6.py (its class-file comparison and
JVM set-up, copied forward); the 0.2.6 / 0.2.5 harnesses still cover everything 0.2.7 leaves byte-identical.

    python SkyyCollections/test_skyycollections_0.2.7.py [--jar <SkyyCollections-0.2.7.jar>] [--old <SkyyCollections-0.2.6.jar>]
                                                         [--dir <scratch>] [--live <Skyy_SkyyCollections folder>] [--keep]

One JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath), each jar in its own
class loader.
  A  every class of both jars loads, verifies and initialises
  B  class bytes 0.2.6 -> 0.2.7: the same classes; every class byte-identical or version-constants-only, except the DECLARED methods
     (CollUtil bagRank / prettyItem + isLantern / lanRarity; CollReg loadConfig / validate / rewardTextB / configText / clinit + loadLan /
     lanPresent / lanMerge / lanPublish + the LAN_* fields; CollBypass buyable / unlockText; CollKit rewardToken + checkLanTier;
     SkyyCollectionsPlugin shutdown; the kit's CfgRows / CfgFile rows, CfgHist KEEP 20 -> 10 only); manifest: only Version / Name; the page id unchanged (C)
  T  THE TIERS: the default config text holds the four lantern.tier lines (1 / 3 / 5 / 8); loadConfig on a fresh folder, an existing
     file without lantern lines (defaults), custom values, bad / out-of-range values (default + WARN text), 20 and 21
  M  THE MERGE (CollReg.lanMerge on the real registry): all four at TreeSap 1 / 3 / 5 / 8; nothing when SkyyAccessories is absent
     (empty set) - coll:lantern absent; clamping a tier past the ladder; a hidden / missing TreeSap -> nothing, LAN_ON false; no
     duplicate on a second merge; lanPublish puts / removes coll:lantern (plain String); validate() in the bare JVM = the REAL absent
     path (the asset store has no Lantern recipe): no coll:lantern, the note, a Lantern token in rewards.properties ignored + counted
  U  UNLOCKS (CollUnlocks.compute, the coll:recipes source) per Lantern at its tier's threshold - 1 (locked) and at it (unlocked), for
     the default and for custom tiers; the other collections' recipes unchanged; the tier rows / chat lines name "<Rarity> Lantern
     Accessory recipe"; CollUtil.isLantern / bagRank
  K  COINS NEVER BUY IT: a BOUGHT TreeSap tier (meta _bought.TreeSap = 9, no sap) unlocks no Lantern (compute, every bagMax word);
     buyable false (bags free or not); chainBuyable false; offer() with coin unlocks ON refuses a TreeSap purchase; the bought row says
     "(gather this tier)" (also with free bags); unlockText names it "must be gathered"; Iron's bag rules unchanged
  A  REVIEW FIX: the opt-in auto recipe rule (CollUnlocks.compute, auto=true) on a fake CraftingRecipe store holding the four Lantern
     recipes + a control recipe (Tree Sap input): the control unlocks, a Lantern only at its tier (60 / 300 / 1000 / 10000 sap); M2 / M6 /
     M7: coll:lantern = "off" when not managed (also after a reload that hides TreeSap)
  S  SERVER SETUP checks: checkLanTier (1..9 ok, 0 / 10 / text refused, 20 without a registry), rewardToken refuses a Lantern id
  L  START TWICE on a scratch COPY of the live Skyy_SkyyCollections folder (CollBagMigrate.run, CollBypassMig.run, loadAll, validate,
     CfgPub start / shutdown): every file byte-identical after both starts (0.2.7 writes nothing), the tiers = the defaults
Nothing outside the scratch folder is written (default tools/dev/scratch/lantern-sap-fix/coll027, deleted at the end unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.2.7", "0.2.6"
PKG = "com.skyy.collections."
SCRIPT = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


SCRATCH_ROOT = os.path.abspath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "lantern-sap-fix", "coll027")))
assert SCRATCH.startswith(SCRATCH_ROOT + os.sep), "--dir must be inside tools/dev/scratch/"
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)))
LIVE = os.path.abspath(arg("--live", os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData",
                                                   "Saves", "HUD mod", "mods", "Skyy_SkyyCollections")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
LAN_RIDS = ["Skyy_Talisman_Lantern_%s_Recipe_Generated_0" % w for w in ("Common", "Uncommon", "Rare", "Epic")]
LAN_NAMES = ["Normal", "Unique", "Rare", "Legendary"]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def cp_utf8(b):
    """[(start, end, bytes)] of every CONSTANT_Utf8 entry of a class file"""
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
            raise ValueError("constant pool tag %d" % tag)
        k += 1
    return out


def classes(jar):
    z = zipfile.ZipFile(jar)
    out = dict((n[:-6].replace("/", "."), z.read(n)) for n in z.namelist() if n.endswith(".class"))
    z.close()
    return out


def manifest(jar):
    z = zipfile.ZipFile(jar)
    m = json.loads(z.read("manifest.json").decode("utf8"))
    z.close()
    return m


def snap(dd):
    out = {}
    for root, _ds, fs in os.walk(dd):
        for f in fs:
            p = os.path.join(root, f)
            out[os.path.relpath(p, dd)] = open(p, "rb").read()
    return out


def run():
    import jpype
    from jpype import JClass, JArray
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")

    def loader(jar):
        urls = JArray(URL)(1)
        urls[0] = File(jar).toURI().toURL()
        return URLCL(urls, sysl)

    L = {"old": loader(OLD), "new": loader(JAR)}
    CB = {"old": classes(OLD), "new": classes(JAR)}

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
    check(set(old) == set(new), "B. the same classes: %s" % sorted(set(old) ^ set(new)))
    CP = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def ct(b):
        return CP(False).makeClass(BAIS(b))

    def code_of(m):
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        cp = mi.getConstPool()
        if ca is None:
            return ["<no code>"]
        it, rows = ca.iterator(), []
        while it.hasNext():
            pos = it.next()
            rows.append((pos, re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cp)))))
        idx = dict((p, i) for i, (p, _t) in enumerate(rows))
        idx[int(ca.getCodeLength())] = len(rows)
        out = []
        for _p, t in rows:
            t = re.sub(r"^ldc_w ", "ldc ", t)
            mm = re.match(r"^(if\w*|goto(?:_w)?|jsr(?:_w)?) (\d+)$", t)
            if mm:
                t = "%s @%d" % (mm.group(1), idx[int(mm.group(2))])
            out.append(t)
        et = ca.getExceptionTable()
        for i in range(et.size()):
            ctp = et.catchType(i)
            out.append("try @%d @%d @%d %s" % (idx[et.startPc(i)], idx[et.endPc(i)], idx[et.handlerPc(i)], cp.getClassInfo(ctp) if ctp else "any"))
        return out

    def methods(c):
        out = {}
        for m in list(c.getDeclaredMethods()) + list(c.getDeclaredConstructors()):
            out[str(m.getMethodInfo().getName()) + str(m.getSignature())] = code_of(m)
        ci = c.getClassInitializer()
        if ci is not None:
            out["<clinit>"] = code_of(ci)
        return out

    def vonly(a, b):
        return len(a) == len(b) and all(x == y or x.replace(OLD_VERSION, VERSION) == y for x, y in zip(a, b))

    DECLARED = {
        "CollUtil": ["bagRank", "prettyItem"],
        "CollReg": ["<clinit>", "configText", "loadConfig", "rewardTextB", "validate"],
        "CollBypass": ["buyable", "unlockText"],
        "CollKit": ["rewardToken"],
        "CollUnlocks": ["compute"],                       # review fix: the auto rule skips a Lantern recipe
        "SkyyCollectionsPlugin": ["shutdown"],
        "CfgRows": ["<clinit>"],
        "CfgFile": ["<clinit>"],                         # the kit's row arrays: 28 -> 32 rows (the four Lantern rows)
        "CfgHist": ["compact", "snapshot", "versions"],  # the inlined CfgRows.KEEP: 20 -> 10 (checked below: nothing else)
    }
    ADDED = {
        "CollUtil": ["isLantern(Ljava/lang/String;)Z", "lanRarity(Ljava/lang/String;)Ljava/lang/String;"],
        "CollReg": ["lanMerge(Ljava/util/HashMap;Lcom/skyy/collections/RegData;Ljava/util/Set;[I)Ljava/lang/String;",
                    "lanPresent()Ljava/util/HashSet;", "lanPublish([I)V", "loadLan(Ljava/util/Properties;)Ljava/lang/String;"],
        "CollKit": ["checkLanTier(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"],
    }
    NEWFIELDS = {"CollReg": ["LAN_COLL", "LAN_DEF", "LAN_KEY", "LAN_NOTE", "LAN_ON", "LAN_RID", "LAN_TIER"]}
    kinds = {}
    for n in sorted(set(old) & set(new)):
        short = n[len(PKG):]
        if old[n] == new[n]:
            kinds[short] = "identical"
            continue
        co, cn = cp_utf8(old[n]), cp_utf8(new[n])
        if len(co) == len(cn):
            rebuilt, okv = new[n], True
            for (s0, e0, t0), (s1, e1, t1) in reversed(list(zip(co, cn))):
                if t0 == t1:
                    continue
                if t0.decode("utf8").replace(OLD_VERSION, VERSION) != t1.decode("utf8"):
                    okv = False
                    break
                rebuilt = rebuilt[:s1] + old[n][s0:e0] + rebuilt[e1:]
            if okv and rebuilt == old[n]:
                kinds[short] = "version constants"
                continue
        po, pn = ct(old[n]), ct(new[n])
        fo = set(str(f.getName()) for f in po.getDeclaredFields())
        fn = set(str(f.getName()) for f in pn.getDeclaredFields())
        check(not (fo - fn) and sorted(fn - fo) == NEWFIELDS.get(short, []), "B. %s: fields added / gone: %s" % (short, sorted(fo ^ fn)))
        mo, mn = methods(po), methods(pn)
        check(not (set(mo) - set(mn)) and sorted(set(mn) - set(mo)) == sorted(ADDED.get(short, [])),
              "B. %s: methods added / gone: %s" % (short, sorted(set(mo) ^ set(mn))))
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and not vonly(mo[k], mn[k]))
        vers = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and vonly(mo[k], mn[k]))
        check(changed == DECLARED.get(short, []), "B. %s: changed methods %s, declared %s" % (short, changed, DECLARED.get(short, [])))
        if short == "CfgHist":
            check(all([x.replace("bipush 20", "bipush 10") for x in mo[k]] == mn[k] for k in mo if mo[k] != mn[k]),
                  "B. CfgHist: only KEEP 20 -> 10 (bipush 20 -> bipush 10)")
        kinds[short] = "methods %s + version only %s" % (changed, vers)
    for k in DECLARED:
        check(k in kinds and kinds[k].startswith("methods"), "B. %s is one of the changed classes: %s" % (k, kinds.get(k)))
    mo_, mn_ = manifest(OLD), manifest(JAR)
    check(mn_["Version"] == VERSION and mn_["Name"] == VERSION + " SkyyCollections"
          and dict((k, v) for k, v in mo_.items() if k not in ("Version", "Name")) == dict((k, v) for k, v in mn_.items() if k not in ("Version", "Name")),
          "B. manifest: only Version / Name changed")
    zo, zn = zipfile.ZipFile(OLD), zipfile.ZipFile(JAR)
    oth = sorted(set(x for x in zo.namelist() + zn.namelist() if not x.endswith(".class") and x != "manifest.json"))
    check(all(x in zo.namelist() and x in zn.namelist() and zo.read(x) == zn.read(x) for x in oth), "B. every other jar file identical: %d" % len(oth))
    ident = sorted(k for k, v in kinds.items() if v == "identical")
    print("B. %d classes byte-identical; version constants only: %s; method-level: %s" % (
        len(ident), sorted(k for k, v in kinds.items() if v == "version constants"),
        dict((k, v) for k, v in kinds.items() if v.startswith("methods"))))

    # ---------------- C. page id (the page is 0.2.5's / 0.2.6's)
    text = open(SCRIPT, encoding="utf8").read()
    chk = None
    for nd in ast.parse(text).body:
        if isinstance(nd, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "COLL_PAGE_CHECKED" for t in nd.targets):
            chk = ast.literal_eval(nd.value)
    plug = new[PKG + "SkyyCollectionsPlugin"].decode("latin1")
    mm = re.search(r"0\.2\.7 ready \(skyyui [^,]*, page ([0-9a-f]{12})\)", plug)
    check(chk == "be0dca34bcb2" and mm is not None and mm.group(1) == chk, "C. page id in the ready line %s == checked %s" % (mm and mm.group(1), chk))

    # ---------------- the new jar's world
    Paths, Long, HashMap, HashSet = JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.util.HashMap"), JClass("java.util.HashSet")
    Props, Bool = JClass("java.util.Properties"), JClass("java.lang.Boolean")
    System = JClass("java.lang.System")
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", BR)

    def jc(name):
        return JClass(PKG + name, loader=L["new"])

    Reg, Store, Util, Unl, Byp, Kit = jc("CollReg"), jc("CollStore"), jc("CollUtil"), jc("CollUnlocks"), jc("CollBypass"), jc("CollKit")
    JIntArr = JArray(JClass("int"))

    # ---------------- T. the tiers
    base = os.path.join(SCRATCH, "fresh", "Skyy_SkyyCollections")
    os.makedirs(base)
    Reg.BASE = Paths.get(base)
    Store.DIR = Paths.get(base).resolve("counts")
    msg = str(Reg.loadAll())
    cfg = open(os.path.join(base, "config.properties"), "rb").read().decode("latin-1")
    check(all(("lantern.tier.%s=%d" % (n.lower(), t)) in cfg.splitlines() for n, t in zip(LAN_NAMES, (1, 3, 5, 8))),
          "T1 the fresh default file holds the four lantern.tier lines")
    check(list(Reg.LAN_TIER) == [1, 3, 5, 8] and "lantern=1/3/5/8" in msg, "T1 fresh: tiers 1/3/5/8 (%s)" % msg[-60:])
    R = Reg.D
    c = int(R.byId.get("treesap"))
    check(str(R.name[c]) == "Tree Sap" and int(Reg.maxTier(R, c)) == 9 and list(R.thr[R.curve[c]]) == [50, 100, 250, 500, 1000, 2500, 5000, 10000, 20000],
          "T1 TreeSap: Standard curve, 9 tiers")

    def load_cfg(lines):
        open(os.path.join(base, "config.properties"), "w").write("\n".join(lines) + "\n")
        return str(Reg.loadConfig()), list(Reg.LAN_TIER)

    old_lines = [ln for ln in cfg.splitlines() if not ln.startswith("lantern.")]
    m1, t1 = load_cfg(old_lines)
    check(t1 == [1, 3, 5, 8], "T2 an existing file without lantern lines -> the defaults %s" % t1)
    m2, t2 = load_cfg(old_lines + ["lantern.tier.normal=2", "lantern.tier.unique= 4 ", "lantern.tier.rare=6", "lantern.tier.legendary=9"])
    check(t2 == [2, 4, 6, 9] and "lantern=2/4/6/9" in m2, "T3 custom tiers read %s" % t2)
    m3, t3 = load_cfg(old_lines + ["lantern.tier.normal=0", "lantern.tier.unique=abc", "lantern.tier.rare=21", "lantern.tier.legendary=20"])
    check(t3 == [1, 3, 5, 20], "T4 bad values -> defaults, 20 kept: %s" % t3)
    load_cfg(cfg.splitlines())

    # ---------------- M. the merge
    ALL = HashSet()
    for r in LAN_RIDS:
        ALL.add(r)

    def merged(tiers, have, hidden=False):
        Reg.LAN_TIER = JIntArr(tiers)
        out = HashMap()
        eff = JIntArr(4)
        if hidden:
            R.hidden[c] = True
        try:
            note = str(Reg.lanMerge(out, R, have, eff))
        finally:
            R.hidden[c] = False
        at = {}
        for e in out.entrySet():
            for rid in e.getValue():
                at.setdefault(str(rid), []).append(str(e.getKey()))
        return out, note, list(eff), at, bool(Reg.LAN_ON)

    out, note, eff, at, on = merged([1, 3, 5, 8], ALL)
    check(on and eff == [1, 3, 5, 8] and [at.get(r) for r in LAN_RIDS] == [["%d.%d" % (c, t)] for t in (1, 3, 5, 8)],
          "M1 all four at TreeSap 1/3/5/8: %s %s" % (at, note))
    Reg.lanPublish(JIntArr(eff))
    check(str(BR.get("coll:lantern")) == "TreeSap|1|3|5|8" and isinstance(BR.get("coll:lantern"), str), "M1 coll:lantern published: %s" % BR.get("coll:lantern"))
    out2, note2, eff2, at2, on2 = merged([1, 3, 5, 8], HashSet())
    check(not on2 and not at2 and "not installed" in note2, "M2 SkyyAccessories absent -> nothing merged: %s" % note2)
    Reg.lanPublish(JIntArr(eff2))
    check(isinstance(BR.get("coll:lantern"), str) and str(BR.get("coll:lantern")) == "off", "M2 review fix: coll:lantern = \"off\" when not managed: %s" % BR.get("coll:lantern"))
    out3, note3, eff3, at3, on3 = merged([1, 3, 12, 30], ALL)
    check(on3 and eff3 == [1, 3, 9, 9] and at3[LAN_RIDS[2]] == ["%d.9" % c] and at3[LAN_RIDS[3]] == ["%d.9" % c], "M3 tiers past the ladder -> the last tier: %s" % eff3)
    out4, note4, eff4, at4, on4 = merged([1, 3, 5, 8], ALL, hidden=True)
    check(not on4 and not at4 and "no TreeSap" in note4, "M4 hidden TreeSap -> nothing merged: %s" % note4)
    # no duplicate on a second merge into the same map; another collection's recipe at that key kept
    out5 = HashMap()
    out5.put("%d.1" % c, JArray(JClass("java.lang.String"))(["Some_Other_Recipe_Generated_0"]))
    Reg.LAN_TIER = JIntArr([1, 1, 1, 1])
    Reg.lanMerge(out5, R, ALL, JIntArr(4))
    Reg.lanMerge(out5, R, ALL, JIntArr(4))
    v5 = [str(x) for x in out5.get("%d.1" % c)]
    check(v5 == ["Some_Other_Recipe_Generated_0"] + LAN_RIDS, "M5 one merge per id, existing tokens kept: %s" % v5)
    # validate() in this bare JVM = the real "SkyyAccessories absent" path (no Lantern recipe in the asset store)
    Reg.LAN_TIER = JIntArr([1, 3, 5, 8])
    rw = open(os.path.join(base, "rewards.properties"), "a")
    rw.write("TreeSap.2=recipe:%s,coins:5\n" % LAN_RIDS[3])
    rw.close()
    Reg.loadRewards()
    BR.put("coll:lantern", "TreeSap|1|1|1|1")
    v = str(Reg.validate())
    check(len(Reg.lanPresent()) == 0, "M6 bare JVM: no Lantern recipe in the asset store")
    check("SkyyAccessories not installed" in v and "1 Lantern token(s) in rewards.properties ignored" in v and str(BR.get("coll:lantern")) == "off",
          "M6 validate (absent): note + ignored token + coll:lantern \"off\": %s" % v)
    # review fix: a managed run, then a reload that hides TreeSap -> "off" (SkyyAccessories frees every Lantern), never a removed key
    merged([1, 3, 5, 8], ALL)
    Reg.lanPublish(JIntArr([1, 3, 5, 8]))
    check(str(BR.get("coll:lantern")) == "TreeSap|1|3|5|8", "M7 managed: tier string")
    _o, _n, _e, _a, _on = merged([1, 3, 5, 8], ALL, hidden=True)
    Reg.lanPublish(JIntArr(_e))
    check(not _on and str(BR.get("coll:lantern")) == "off", "M7 review fix: TreeSap hidden on a reload -> coll:lantern \"off\": %s" % BR.get("coll:lantern"))
    check(not any(LAN_RIDS[3] in [str(x) for x in Reg.recipesAt(c, t)] for t in range(1, 10)), "M6 the ignored token is in no tier")
    check(int(Reg.coinsAt(R, c, 2)) == 100 + 5, "M6 the coins token on that line is still read (100 + 5): %s" % Reg.coinsAt(R, c, 2))

    # ---------------- U. unlocks per tier threshold
    def recipes_at_merge(tiers):
        Reg.LAN_TIER = JIntArr(tiers)
        out = HashMap()
        Reg.lanMerge(out, R, ALL, JIntArr(4))
        Reg.RECIPES = out
        Reg.VALIDATED = True

    def data(n, bought=0):
        d = jc("CollData")()
        if n:
            d.items.put("Ingredient_Tree_Sap", Long.valueOf(n))
        if bought:
            d.meta.put("_bought.TreeSap", Long.valueOf(bought))
        return d

    def got(d):
        return [r for r in LAN_RIDS if r in set(str(x) for x in Unl.compute(d))]

    thr = [50, 100, 250, 500, 1000, 2500, 5000, 10000, 20000]
    for tiers in ([1, 3, 5, 8], [2, 4, 6, 9]):
        recipes_at_merge(tiers)
        for k, t in enumerate(tiers):
            below, at_ = got(data(thr[t - 1] - 1)), got(data(thr[t - 1]))
            check(LAN_RIDS[k] not in below and LAN_RIDS[k] in at_,
                  "U1 tiers %s: %s Lantern locked at %d sap, unlocked at %d" % (tiers, LAN_NAMES[k], thr[t - 1] - 1, thr[t - 1]))
            check(at_ == [r for j, r in enumerate(LAN_RIDS) if tiers[j] <= t], "U1 tiers %s at %d sap: exactly the lower Lanterns %s" % (tiers, thr[t - 1], at_))
        check(got(data(0)) == [] and got(data(49)) == [] and got(data(10 ** 9)) == LAN_RIDS, "U1 tiers %s: 0 / 49 sap none, huge all" % tiers)
    recipes_at_merge([1, 3, 5, 8])
    # Skyy's live counts (318 sap on the main profile): Normal + Unique
    check(got(data(318)) == LAN_RIDS[:2], "U2 318 sap (Skyy's main profile) -> Normal + Unique")
    rl = [str(x) for x in Reg.rewardLines(R, c, 8)]
    check(rl[0] == "Legendary Lantern Accessory recipe", "U3 tier VIII chat line: %s" % rl)
    check([str(Util.prettyRecipe(r)) for r in LAN_RIDS] == ["%s Lantern Accessory" % n for n in LAN_NAMES], "U3 the four names")
    rt = str(Reg.rewardText(R, c, 1))
    check(rt.startswith("Normal Lantern Accessory recipe - +"), "U3 tier I row: %s" % rt)
    check(all(Util.isLantern(r) and int(Util.bagRank(r)) == 9 for r in LAN_RIDS) and not Util.isLantern("Skyy_Sack_Mining_Small_Recipe_Generated_0")
          and int(Util.bagRank("Skyy_Sack_Mining_Large_Recipe_Generated_0")) == 4 and not Util.isLantern(None), "U4 isLantern / bagRank")

    # ---------------- K. coins never buy a Lantern
    for bm in range(5):
        Reg.BYP_BAGMAX = bm
        check(got(data(0, bought=9)) == [] and got(data(60, bought=9)) == LAN_RIDS[:1], "K1 bagMax %d: bought tiers unlock no Lantern" % bm)
    Reg.BYP_BAGMAX = 2
    for fr in (False, True):
        BR.put("sacks:freebags", Bool(fr))
        check(all(not Byp.buyable(r, fr) for r in LAN_RIDS), "K2 buyable false (free bags %s)" % fr)
        check(not Byp.chainBuyable(c, 1, 9), "K2 chainBuyable TreeSap 1..9 false (free %s)" % fr)
        row = str(Reg.rewardTextB(R, c, 3, True))
        check(row.startswith("Unique Lantern Accessory recipe (gather this tier)"), "K3 bought row (free %s): %s" % (fr, row))
        ut = str(Byp.unlockText(c, 1))
        check("Normal Lantern Accessory must be gathered" in ut, "K3 unlockText (free %s): %s" % (fr, ut))
    BR.remove("sacks:freebags")
    Reg.BYPASS = True
    o = Byp.offer(data(60), R, c)
    check(o[2] is not None and "Nothing more here can be bought" in str(o[2]), "K4 coin unlocks ON: a TreeSap purchase refused: %s" % o[2])
    Reg.BYPASS = False
    iron = int(R.byId.get("iron"))
    check(Byp.buyable("Skyy_Sack_Mining_Medium_Recipe_Generated_0", False) and not Byp.buyable("Skyy_Sack_Mining_Rare_Recipe_Generated_0", False),
          "K5 bag rules unchanged (unique buyable, rare not)")

    # ---------------- A. review fix: the opt-in auto rule never adds a Lantern recipe (CollUnlocks.compute, AUTO loop) - EXECUTED on a
    # fake CraftingRecipe asset store (the SkyyCooking harness pattern): the four Lantern recipes + a control recipe, Tree Sap inputs only
    US_ = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    US_.setAccessible(True)
    us = US_.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    jp = CP(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStoreColl", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStoreColl() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    FakeStore = fake.toClass(AS.class_)

    def jf(C_, name_):
        f_ = C_.class_.getDeclaredField(name_)
        f_.setAccessible(True)
        return f_

    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    BRQ, BTP = JClass("com.hypixel.hytale.protocol.BenchRequirement"), JClass("com.hypixel.hytale.protocol.BenchType")
    crr_id = jf(CRR, "id")

    def recipe(rid, out):
        r_ = CRR(JArray(MQ)([MQ("Ingredient_Tree_Sap", None, None, 1, None)]), MQ(out, None, None, 1, None), JArray(MQ)([MQ(out, None, None, 1, None)]),
                 1, JArray(BRQ)([BRQ(BTP.Crafting, "Workbench", None, 0, None)]), 1.0, False, 0)
        crr_id.set(r_, rid)
        return r_

    CONTROL = "Skyy_Test_Sap_Thing_Recipe_Generated_0"
    st_ = us.allocateInstance(FakeStore)
    dm_ = DAM()
    hm_ = HashMap()
    for rid_ in LAN_RIDS + [CONTROL]:
        hm_.put(rid_, recipe(rid_, rid_.replace("_Recipe_Generated_0", "")))
    jf(DAM, "assetMap").set(dm_, hm_)
    jf(AS, "assetMap").set(st_, dm_)
    crr_store = jf(CRR, "ASSET_STORE")
    keep_store = crr_store.get(None)
    crr_store.set(None, st_)
    try:
        check(CRR.getAssetMap().getAsset(LAN_RIDS[3]) is not None, "A0 fake CraftingRecipe store holds the Lantern recipes")
        recipes_at_merge([1, 3, 5, 8])
        Reg.AUTO = True
        for n_, exp_ in ((60, LAN_RIDS[:1]), (300, LAN_RIDS[:2]), (1000, LAN_RIDS[:3]), (10000, LAN_RIDS)):
            ids_ = set(str(x) for x in Unl.compute(data(n_)))
            check(CONTROL in ids_, "A1 auto ON, %d sap: the auto loop ran (the control recipe unlocked)" % n_)
            check([r for r in LAN_RIDS if r in ids_] == exp_, "A1 review fix: auto ON, %d sap -> only the tier Lanterns %s: %s" % (n_, exp_, [r for r in LAN_RIDS if r in ids_]))
        ids_ = set(str(x) for x in Unl.compute(data(0, bought=9)))
        check(not any(r in ids_ for r in LAN_RIDS), "A2 auto ON + every TreeSap tier bought, no sap -> no Lantern")
        Reg.AUTO = False
        ids_ = set(str(x) for x in Unl.compute(data(60)))
        check(CONTROL not in ids_ and [r for r in LAN_RIDS if r in ids_] == LAN_RIDS[:1], "A3 auto OFF: no control recipe, Normal only")
    finally:
        Reg.AUTO = False
        crr_store.set(None, keep_store)
    print("A. auto recipe rule: Lanterns only at their Tree Sap tiers (executed on a fake recipe store)")

    # ---------------- S. Server Setup checks
    for v_, ok in (("1", True), ("8", True), ("9", True), (" 3 ", True), ("0", False), ("10", False), ("x", False), ("", False)):
        r = Kit.checkLanTier("lantern.tier.rare", v_)
        check((r is None) == ok, "S1 checkLanTier %r -> %s" % (v_, r))
    keepD = Reg.D
    Reg.D = None
    check(Kit.checkLanTier("k", "20") is None and Kit.checkLanTier("k", "21") is not None, "S1 no registry: 1-20")
    Reg.D = keepD
    r = str(Kit.rewardToken("recipe:" + LAN_RIDS[0]))
    check("Lantern recipes rows" in r, "S2 the Tier rewards table refuses a Lantern token: %s" % r)
    print("T/M/U/K/S. lantern tiers, merge, unlocks per threshold, coin rule and Server Setup checks done")

    # ---------------- L. start twice on a scratch copy of the live folder
    if not os.path.isdir(LIVE):
        print("note: no live Skyy_SkyyCollections folder - L skipped")
        return
    lm = os.path.join(SCRATCH, "l-mods")
    d = os.path.join(lm, "Skyy_SkyyCollections")
    shutil.copytree(LIVE, d)          # read-only source, scratch copy
    before0 = snap(d)
    notes = []
    for rnd in range(2):
        Reg.BASE = Paths.get(d)
        Store.DIR = Paths.get(d).resolve("counts")
        bm_ = str(jc("CollBagMigrate").run(Paths.get(d)))
        cm_ = str(jc("CollBypassMig").run(Paths.get(d)))
        la = str(Reg.loadAll())
        va = str(Reg.validate())
        jc("CfgPub").start(Paths.get(lm), None)
        jc("CfgPub").shutdown()
        notes.append((bm_, cm_, la[-40:], va[-80:]))
        check(list(Reg.LAN_TIER) == [1, 3, 5, 8], "L%d tiers = the defaults on the live copy" % rnd)
    after = snap(d)
    chg = sorted(k for k in set(before0) | set(after) if before0.get(k) != after.get(k))
    check(not chg, "L two starts on a copy of the live data: no file changed (%d files) %s" % (len(before0), chg[:4]))
    print("L. two starts on the live copy: %d files unchanged; %s" % (len(before0), notes[-1]))
    BR.clear()


def main():
    for j in (JAR, OLD):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first (python tools/coll_0_2_7_patch.py, python SkyyCollections/build_skyycollections_0.2.7.py)")
            return 1
    if os.path.exists(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(SCRATCH)
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    os.environ["TEMP"] = tmp
    os.environ["TMP"] = tmp
    try:
        run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        FAILS.append("harness error: %s" % e)
    print("SkyyCollections %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:40]:
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
