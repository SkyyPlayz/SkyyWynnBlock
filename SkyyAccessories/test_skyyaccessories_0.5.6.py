"""Bare-JVM harness for SkyyAccessories 0.5.6 - the Lantern recipes follow the Tree Sap collection + the 'Hidden lights: most' text fix
(tools/acc_0_5_6_patch.py; Skyy 2026-10-05 LOCKED, docs/answered/economy.md). The 0.5.5 harness (test_skyyaccessories_0.5.5.py) still
covers every class 0.5.6 leaves byte-identical (B below proves which).

    python SkyyAccessories/test_skyyaccessories_0.5.6.py [--jar <SkyyAccessories-0.5.6.jar>] [--old <SkyyAccessories-0.5.5.jar>]
                                                         [--coll <SkyyCollections-0.2.7.jar>] [--dir <scratch>] [--live <folder>] [--keep]

One JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath), each jar in its own
class loader (SkyyCollections 0.2.7 too, for the bridge section).
  A  every class of both jars loads, verifies and initialises
  B  0.5.5 -> 0.5.6: the new class AccKnow; AccEffects.tick + AccCfg.writeDefaults (the default file's comment) the only changed
     Accessories methods; the kit's CfgRows (the row help / default text), CfgHist (KEEP 20 -> 10 only); every other class byte-identical or version-only; the jar files: exactly the four
     Lantern item JSONs differ, each only by Recipe.KnowledgeRequired = true; the manifest only Version / Name
  K  AccKnow on the engine's real PlayerConfigData: free (no coll:lantern) -> all four known, every other known recipe kept; managed ->
     exactly the Lantern ids in coll:recipes:<uuid>; locked below the tier / known at it (the ids SkyyCollections 0.2.7's own
     CollUnlocks.compute publishes for 0, 49, 50, 249, 250, 999, 1000, 9999, 10000 sap); coll:recipes missing / not a String = no change;
     hold (seen, then gone) = no change; REVIEW FIXES: "off" = free (also after a managed run); coll:recipes missing past ABSENT_MS =
     no Lantern known (K9); a profile:epoch change = change nothing for SETTLE_MS (K10; E5-E7 on the real store); idempotent (second apply false); an admin's /recipe learn of a locked Lantern undone; a
     Lantern item never touched (nothing but the known set is read or written)
  E  AccKnow.tick on a REAL ECS Store (ComponentRegistry + the engine's Player component, EntityModule stand-in): a player entity's
     PlayerConfigData follows coll:recipes; null args / profile loading (profile:busy) / hold = -1 and nothing written; the packet send
     (CraftingPlugin.sendKnownRecipes needs Universe + a PacketHandler) fails in the bare JVM -> caught (one WARN), the knowledge stays set
  X  THE BRIDGE with either mod absent: SkyyCollections absent (no coll:lantern) -> free; SkyyCollections 0.2.7 loaded but
     SkyyAccessories absent (its validate in the bare JVM finds no Lantern recipe) -> it publishes no coll:lantern, so nothing locks;
     SkyyCollections 0.2.7 lanMerge + lanPublish -> coll:lantern a plain java.lang.String; the values are plain Strings both ways
  H  HIDDEN LIGHTS: the jar's own solver (AccDefs.lanTable) gives the identical table for lantern.lights 1, 2 and 3 and a ring from 4
     (Legendary: 4 -> 3 ring lights) - what the new row help and config comment say; the row help / comment text in the jar
  L  START TWICE on a scratch COPY of the live Skyy_SkyyAccessories folder (migrate051, migrate055, load, notices, the config kit start /
     shutdown): every file byte-identical after both starts
Nothing outside the scratch folder is written (default tools/dev/scratch/lantern-sap-fix/acc056, deleted at the end unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, struct, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.5.6", "0.5.5"
PKG = "com.skyy.accessories."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


SCRATCH_ROOT = os.path.abspath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "lantern-sap-fix", "acc056")))
assert SCRATCH.startswith(SCRATCH_ROOT + os.sep), "--dir must be inside tools/dev/scratch/"
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD_VERSION)))
COLL = os.path.abspath(arg("--coll", os.path.join(ROOT, "SkyyCollections", "SkyyCollections-0.2.7.jar")))
LIVE = os.path.abspath(arg("--live", os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData",
                                                   "Saves", "HUD mod", "mods", "Skyy_SkyyAccessories")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
LAN_IDS = ["Skyy_Talisman_Lantern_%s" % w for w in ("Common", "Uncommon", "Rare", "Epic")]
SFX = "_Recipe_Generated_0"


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


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
            raise ValueError("constant pool tag %d" % tag)
        k += 1
    return out


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


def run():
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride
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

    L = {"old": loader(OLD), "new": loader(JAR), "coll": loader(COLL)}
    F = {"old": jarfiles(OLD), "new": jarfiles(JAR)}
    CB = dict((k, dict((n[:-6].replace("/", "."), b) for n, b in F[k].items() if n.endswith(".class"))) for k in ("old", "new"))

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
    check(set(new) - set(old) == {PKG + "AccKnow"} and not set(old) - set(new), "B. classes: + AccKnow only: %s" % sorted(set(old) ^ set(new)))
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

    DECLARED = {"AccEffects": ["tick"], "AccCfg": ["writeDefaults"], "CfgRows": ["<clinit>"], "CfgHist": ["compact", "snapshot", "versions"]}
    kinds = {}
    tick_diff = None
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
        fo = sorted((str(f.getName()), str(f.getSignature())) for f in po.getDeclaredFields())
        fn = sorted((str(f.getName()), str(f.getSignature())) for f in pn.getDeclaredFields())
        check(fo == fn, "B. %s: fields changed: %s" % (short, sorted(set(fo) ^ set(fn))))
        mo, mn = methods(po), methods(pn)
        check(set(mo) == set(mn), "B. %s: methods added / gone: %s" % (short, sorted(set(mo) ^ set(mn))))
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and not vonly(mo[k], mn[k]))
        vers = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and vonly(mo[k], mn[k]))
        check(changed == DECLARED.get(short, []), "B. %s: changed methods %s, declared %s" % (short, changed, DECLARED.get(short, [])))
        if short == "CfgHist":
            check(all([x.replace("bipush 20", "bipush 10") for x in mo[k]] == mn[k] for k in mo if mo[k] != mn[k]),
                  "B. CfgHist: only KEEP 20 -> 10")
        if short == "AccCfg":
            k = [k for k in mo if k.startswith("writeDefaults(")][0]
            ldo = [x for x in mo[k] if x.startswith("ldc ")]
            ldn = [x for x in mn[k] if x.startswith("ldc ")]
            check([x for x in mo[k] if not x.startswith("ldc ")] == [x for x in mn[k] if not x.startswith("ldc ")] and
                  len(ldo) == len(ldn) and sum(1 for a, b in zip(ldo, ldn) if a != b) == 1 and any("1-3 give one light" in x for x in ldn),
                  "B. AccCfg.writeDefaults: only the default text constant changed (the lantern.lights comment)")
        if short == "AccEffects":
            k = [k for k in mo if k.startswith("tick(")][0]
            a, b = mo[k], mn[k]
            # 0.5.6 appends exactly: aload ref, aload store, aload u, invokestatic AccKnow.tick, pop - before the final return
            tick_diff = (len(b) - len(a), [x for x in b if "AccKnow" in x])
            check(b[:len(a) - 1] == a[:len(a) - 1] or len(b) == len(a) + 5, "B. AccEffects.tick: 0.5.5's body + the AccKnow call (%s)" % (tick_diff,))
        kinds[short] = "methods %s + version only %s" % (changed, vers)
    for k in DECLARED:
        check(k in kinds and kinds[k].startswith("methods"), "B. %s is one of the changed classes: %s" % (k, kinds.get(k)))
    check(tick_diff is not None and len(tick_diff[1]) == 1 and "AccKnow.tick" in tick_diff[1][0], "B. AccEffects.tick calls AccKnow.tick once: %s" % (tick_diff,))
    # the jar's other files
    fo_, fn_ = dict((k, v) for k, v in F["old"].items() if not k.endswith(".class")), dict((k, v) for k, v in F["new"].items() if not k.endswith(".class"))
    check(set(fo_) == set(fn_), "B. the same jar files: %s" % sorted(set(fo_) ^ set(fn_)))
    diff = sorted(k for k in fo_ if k in fn_ and fo_[k] != fn_[k])
    want = sorted(["Server/Item/Items/Utility/%s.json" % i for i in LAN_IDS] + ["manifest.json"])
    check(diff == want, "B. changed files = the four Lantern JSONs + the manifest: %s" % diff)
    for i in LAN_IDS:
        p = "Server/Item/Items/Utility/%s.json" % i
        jo, jn = json.loads(fo_[p]), json.loads(fn_[p])
        check(jn["Recipe"].pop("KnowledgeRequired", None) is True and jo == jn, "B. %s: only Recipe.KnowledgeRequired = true added" % i)
    kr = sorted(os.path.basename(p)[:-5] for p, v in fn_.items() if p.startswith("Server/Item/Items/") and p.endswith(".json")
                and (json.loads(v).get("Recipe") or {}).get("KnowledgeRequired"))
    check(kr == sorted(LAN_IDS), "B. exactly the four Lantern recipes are knowledge recipes: %s" % kr)
    mo_, mn_ = json.loads(fo_["manifest.json"]), json.loads(fn_["manifest.json"])
    check(mn_["Version"] == VERSION and dict((k, v) for k, v in mo_.items() if k not in ("Version", "Name")) ==
          dict((k, v) for k, v in mn_.items() if k not in ("Version", "Name")), "B. manifest: only Version / Name")
    print("B. %d classes byte-identical; version only: %s; method-level: %s; files: %s" % (
        sum(1 for v in kinds.values() if v == "identical"), sorted(k for k, v in kinds.items() if v == "version constants"),
        dict((k, v) for k, v in kinds.items() if v.startswith("methods")), diff))

    # ---------------- K. AccKnow on the real PlayerConfigData
    System = JClass("java.lang.System")
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", BR)
    Know = JClass(PKG + "AccKnow", loader=L["new"])
    Store = JClass(PKG + "AccStore", loader=L["new"])
    PCD = JClass("com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData")
    UUID, HashSet = JClass("java.util.UUID"), JClass("java.util.HashSet")
    u = UUID.fromString("00000000-0000-0000-0000-00000000aa01")
    OTHER = ["Skyy_Sack_Mining_Small", "Armor_Bronze_Chest", "Food_Pie_Apple"]

    def pcd(known):
        d = PCD()
        hs = HashSet()
        for x in known:
            hs.add(x)
        d.setKnownRecipes(hs)
        return d

    def kset(d):
        return sorted(str(x) for x in d.getKnownRecipes())

    def reset():
        BR.clear()
        Know.SEEN = False
        Know.LASTEP.clear()
        Know.CHANGEDAT.clear()
        Know.ABSENT.clear()
        Know.SETTLE_MS = 6000
        Know.ABSENT_MS = 10000

    reset()
    d = pcd(OTHER)
    w = Know.wanted(u)
    check(str(Know.mode()) == "free" and sorted(str(x) for x in w) == sorted(LAN_IDS), "K1 free (no coll:lantern): all four wanted")
    check(Know.apply(d, w) and kset(d) == sorted(OTHER + LAN_IDS), "K1 free: all four known, the others kept: %s" % kset(d))
    check(not Know.apply(d, Know.wanted(u)), "K1 idempotent: a second apply changes nothing")
    # managed
    BR.put("coll:lantern", "TreeSap|1|3|5|8")
    BR.put("coll:recipes:" + str(u), "Tool_Hoe_Copper_Recipe_Generated_0,%s,%s, Skyy_Sack_Mining_Small_Recipe_Generated_0" % (LAN_IDS[0] + SFX, LAN_IDS[1] + SFX))
    w = Know.wanted(u)
    check(str(Know.mode()) == "managed" and sorted(str(x) for x in w) == LAN_IDS[:2], "K2 managed: Normal + Unique wanted: %s" % w)
    check(Know.apply(d, w) and kset(d) == sorted(OTHER + LAN_IDS[:2]), "K2 Rare / Legendary taken out of the known set, the rest kept: %s" % kset(d))
    # driven by SkyyCollections 0.2.7's own compute (coll:recipes source) at the tier thresholds
    CReg = JClass("com.skyy.collections.CollReg", loader=L["coll"])
    CStore = JClass("com.skyy.collections.CollStore", loader=L["coll"])
    CUnl = JClass("com.skyy.collections.CollUnlocks", loader=L["coll"])
    CData = JClass("com.skyy.collections.CollData", loader=L["coll"])
    Paths, Long, HashMap = JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.util.HashMap")
    cb = os.path.join(SCRATCH, "coll", "Skyy_SkyyCollections")
    os.makedirs(cb)
    CReg.BASE = Paths.get(cb)
    CStore.DIR = Paths.get(cb).resolve("counts")
    CReg.loadAll()
    R = CReg.D
    allr = HashSet()
    for i in LAN_IDS:
        allr.add(i + SFX)
    eff = JArray(JClass("int"))(4)
    rec = HashMap()
    CReg.lanMerge(rec, R, allr, eff)
    CReg.RECIPES = rec
    CReg.VALIDATED = True
    CReg.lanPublish(eff)
    check(isinstance(BR.get("coll:lantern"), str) and str(BR.get("coll:lantern")) == "TreeSap|1|3|5|8", "X1 SkyyCollections 0.2.7 publishes coll:lantern as a String")
    for n, exp in ((0, 0), (49, 0), (50, 1), (249, 1), (250, 2), (999, 2), (1000, 3), (9999, 3), (10000, 4), (20000, 4)):
        cd = CData()
        if n:
            cd.items.put("Ingredient_Tree_Sap", Long.valueOf(n))
        ids = CUnl.compute(cd)
        BR.put("coll:recipes:" + str(u), ",".join(str(x) for x in ids))
        d2 = pcd(OTHER + LAN_IDS)
        Know.apply(d2, Know.wanted(u))
        check(kset(d2) == sorted(OTHER + LAN_IDS[:exp]), "K3 %d sap -> exactly %d Lantern(s) known: %s" % (n, exp, [x for x in kset(d2) if "Lantern" in x]))
    # bought tiers never give one (Collections' coin rule, seen from here)
    cd = CData()
    cd.meta.put("_bought.TreeSap", Long.valueOf(9))
    BR.put("coll:recipes:" + str(u), ",".join(str(x) for x in CUnl.compute(cd)))
    d3 = pcd([])
    Know.apply(d3, Know.wanted(u))
    check(kset(d3) == [], "K4 every TreeSap tier BOUGHT, no sap -> no Lantern known")
    # an admin's /recipe learn of a locked Lantern is undone
    BR.put("coll:recipes:" + str(u), LAN_IDS[0] + SFX)
    d4 = pcd([LAN_IDS[3]])
    check(Know.apply(d4, Know.wanted(u)) and kset(d4) == [LAN_IDS[0]], "K5 a learned locked Legendary is taken out, Normal added")
    # no coll:recipes / not a String -> change nothing (review fix: for ABSENT_MS; then no Lantern known)
    BR.remove("coll:recipes:" + str(u))
    check(Know.wanted(u) is None, "K6 coll:recipes missing -> null (change nothing)")
    check(Know.wanted(u) is None, "K6 coll:recipes missing again within 10 s -> still null")
    Know.ABSENT_MS = 0
    w9 = Know.wanted(u)
    check(w9 is not None and w9.size() == 0, "K9 review fix: coll:recipes missing past ABSENT_MS -> an empty set (no Lantern known): %s" % w9)
    d9 = pcd(OTHER + LAN_IDS)
    check(Know.apply(d9, w9) and kset(d9) == sorted(OTHER), "K9 ... every Lantern recipe unknown, the others kept: %s" % kset(d9))
    BR.put("coll:recipes:" + str(u), LAN_IDS[0] + SFX)
    check(sorted(str(x) for x in Know.wanted(u)) == LAN_IDS[:1] and not Know.ABSENT.containsKey(u), "K9 republished -> its set again, timer cleared")
    BR.remove("coll:recipes:" + str(u))
    check(Know.wanted(u) is None, "K9 missing again -> the timer restarts (null first)")
    Know.ABSENT_MS = 10000
    Know.ABSENT.clear()
    # review fix: 6 s settle after a profile:epoch change (the coll:recipes republish), as SkyySacks' settledKey
    BR.put("coll:recipes:" + str(u), LAN_IDS[0] + SFX + "," + LAN_IDS[3] + SFX)
    BR.put("profile:epoch:" + str(u), JClass("java.lang.Long")(1))
    check(sorted(str(x) for x in Know.wanted(u)) == [LAN_IDS[0], LAN_IDS[3]], "K10 first epoch seen = the baseline, no settle")
    BR.put("profile:epoch:" + str(u), JClass("java.lang.Long")(2))
    check(Know.wanted(u) is None and Know.CHANGEDAT.containsKey(u), "K10 review fix: epoch changed -> null (settling)")
    BR.put("coll:recipes:" + str(u), LAN_IDS[0] + SFX)
    check(Know.wanted(u) is None, "K10 still settling (6 s) even after the republish")
    Know.SETTLE_MS = 0
    check(sorted(str(x) for x in Know.wanted(u)) == LAN_IDS[:1] and not Know.CHANGEDAT.containsKey(u), "K10 settled -> the new profile's set only")
    Know.SETTLE_MS = 6000
    BR.remove("profile:epoch:" + str(u))
    check(sorted(str(x) for x in Know.wanted(u)) == LAN_IDS[:1], "K10 epoch absent = no change (no settle)")
    BR.put("coll:recipes:" + str(u), LAN_IDS[0] + SFX)
    BR.put("coll:recipes:" + str(u), JClass("java.lang.Integer")(5))
    check(Know.wanted(u) is None, "K6 coll:recipes not a String -> null")
    check(not Know.apply(d4, None) and kset(d4) == [LAN_IDS[0]], "K6 apply(null) changes nothing")
    # hold
    BR.remove("coll:lantern")
    check(str(Know.mode()) == "hold" and Know.wanted(u) is None, "K7 coll:lantern seen then gone -> hold (change nothing)")
    # review fix: "off" after a managed run (a reload hid TreeSap) -> free at once, not hold
    BR.put("coll:lantern", "off")
    w8 = Know.wanted(u)
    check(str(Know.mode()) == "free" and w8 is not None and sorted(str(x) for x in w8) == sorted(LAN_IDS), "K8 review fix: coll:lantern \"off\" after managed -> free, all four")
    d8 = pcd([LAN_IDS[0]])
    check(Know.apply(d8, w8) and kset(d8) == sorted(LAN_IDS), "K8 ... all four known")
    BR.put("coll:lantern", "TreeSap|1|3|5|8")
    check(str(Know.mode()) == "managed", "K8 tiers back -> managed")
    BR.remove("coll:lantern")
    reset()
    check(str(Know.mode()) == "free", "K7 a fresh JVM without SkyyCollections -> free")
    print("K/X1. AccKnow: free / managed / thresholds / bought / learn undone / missing / hold")

    # ---------------- X. SkyyCollections loaded, SkyyAccessories absent: its bare-JVM validate finds no Lantern recipe -> no coll:lantern
    BR.clear()
    CReg.loadRewards()
    v = str(CReg.validate())
    check(str(BR.get("coll:lantern")) == "off" and "SkyyAccessories not installed" in v, "X2 SkyyCollections without SkyyAccessories: coll:lantern \"off\" (%s)" % v[-60:])
    Know.SEEN = False
    check(str(Know.mode()) == "free", "X2 ... and SkyyAccessories (if it came later) would keep every Lantern craftable")
    Know.SEEN = True
    check(str(Know.mode()) == "free", "X2 review fix: ... also after a managed run in this JVM (\"off\" = free, not hold)")

    # ---------------- E. AccKnow.tick on a real ECS store
    CR = JClass("com.hypixel.hytale.component.ComponentRegistry")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    ES, ERS = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore"), JClass("com.hypixel.hytale.component.EmptyResourceStorage")
    AR = JClass("com.hypixel.hytale.component.AddReason")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    US = uf.get(None)

    @JImplements("java.util.function.Supplier")
    class Sup(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def get(self):
            return self.f()

    def fld(C_, name_):
        f_ = C_.class_.getDeclaredField(name_)
        f_.setAccessible(True)
        return f_

    reg = CR()
    T_PLA = reg.registerComponent(PLA, Sup(lambda: None))
    em_f = fld(EMc, "instance")
    em_old = em_f.get(None)
    em = US.allocateInstance(EMc.class_)
    fld(EMc, "playerComponentType").set(em, T_PLA)
    em_f.set(None, em)
    try:
        st = reg.addStore(ES(None), ERS.get())
        pl = US.allocateInstance(PLA.class_)
        dd = pcd(OTHER)
        fld(PLA, "data").set(pl, dd)
        h = reg.newHolder()
        h.addComponent(T_PLA, pl)
        ref = st.addEntity(h, AR.SPAWN)
        check(st.getComponent(ref, PLA.getComponentType()) is not None, "E0 a real Store with a Player entity")
        BR.clear()
        Know.SEEN = False
        BR.put("coll:lantern", "TreeSap|1|3|5|8")
        BR.put("coll:recipes:" + str(u), LAN_IDS[0] + SFX + "," + LAN_IDS[1] + SFX)
        r = int(Know.tick(ref, st, u))
        check(r == -1 and kset(dd) == sorted(OTHER + LAN_IDS[:2]),
              "E1 tick: the player's knowledge set from coll:recipes (Normal + Unique), the packet send fails in the bare JVM -> caught: %d %s" % (r, kset(dd)))
        check(int(Know.tick(ref, st, u)) == 0, "E1 second tick: already right (0, no packet)")
        BR.put("coll:recipes:" + str(u), LAN_IDS[0] + SFX)
        BR.put("profile:busy:" + str(u), "1")
        check(int(Know.tick(ref, st, u)) == -1 and kset(dd) == sorted(OTHER + LAN_IDS[:2]), "E2 profile loading -> skipped, nothing written")
        BR.remove("profile:busy:" + str(u))
        BR.remove("coll:lantern")
        check(int(Know.tick(ref, st, u)) == -1 and kset(dd) == sorted(OTHER + LAN_IDS[:2]), "E3 hold -> skipped, nothing written")
        check(int(Know.tick(None, st, u)) == -1 and int(Know.tick(ref, None, u)) == -1 and int(Know.tick(ref, st, None)) == -1, "E4 null args -> -1")
        # review fixes on the real store: "off" frees; an epoch change settles; a missing coll:recipes past ABSENT_MS locks
        BR.put("coll:lantern", "off")
        check(int(Know.tick(ref, st, u)) == -1 and kset(dd) == sorted(OTHER + LAN_IDS), "E5 \"off\" -> all four known (packet send caught)")
        BR.put("coll:lantern", "TreeSap|1|3|5|8")
        BR.put("coll:recipes:" + str(u), LAN_IDS[0] + SFX)
        BR.put("profile:epoch:" + str(u), JClass("java.lang.Long")(7))
        Know.tick(ref, st, u)
        check(kset(dd) == sorted(OTHER + LAN_IDS[:1]), "E6 managed: Normal only")
        BR.put("profile:epoch:" + str(u), JClass("java.lang.Long")(8))
        BR.put("coll:recipes:" + str(u), LAN_IDS[0] + SFX + "," + LAN_IDS[3] + SFX)
        check(int(Know.tick(ref, st, u)) == -1 and kset(dd) == sorted(OTHER + LAN_IDS[:1]), "E6 epoch changed -> settling, nothing written")
        Know.SETTLE_MS = 0
        Know.tick(ref, st, u)
        check(kset(dd) == sorted(OTHER + [LAN_IDS[0], LAN_IDS[3]]), "E6 settled -> the new set")
        Know.SETTLE_MS = 6000
        BR.remove("coll:recipes:" + str(u))
        Know.ABSENT_MS = 0
        check(int(Know.tick(ref, st, u)) == -1 and kset(dd) == sorted(OTHER + [LAN_IDS[0], LAN_IDS[3]]), "E7 coll:recipes gone: first tick waits")
        Know.tick(ref, st, u)
        check(kset(dd) == sorted(OTHER), "E7 review fix: still gone past ABSENT_MS -> no Lantern known")
        Know.ABSENT_MS = 10000
    finally:
        em_f.set(None, em_old)
    print("E. AccKnow.tick on a real ECS store")

    # ---------------- H. hidden lights: the jar's own solver
    Defs = JClass(PKG + "AccDefs", loader=L["new"])

    def table(n):
        Defs.LAN_LIGHTS = n
        Defs.LAN_SIG = ""
        Defs.lanTable()
        return [(int(Defs.LAN_TAB_H[t]), int(Defs.LAN_TAB_L[t]), round(float(Defs.LAN_TAB_R[t]), 3), int(Defs.LAN_TAB_M[t]), int(Defs.LAN_TAB_P[t])) for t in range(1, 5)]
    t1, t2, t3, t4, t7 = table(1), table(2), table(3), table(4), table(7)
    check(t1 == t2 == t3 and all(x[3] == 0 for x in t1), "H1 lantern.lights 1, 2, 3 -> the identical one-light table: %s" % t1)
    check(t4[3][3] == 3 and t4 != t1 and t7[3][3] == 5, "H1 4 -> a ring of 3 (Legendary %s), 7 (default) -> 5 around" % (t4[3],))
    Defs.LAN_LIGHTS = 7
    Defs.LAN_SIG = ""
    Defs.lanTable()
    rows = new[PKG + "CfgRows"].decode("latin-1")
    check("1-3 = one light above the wearer; 4-9 = that light + a ring of 3-8 lights around it." in rows and
          "1 = one light only (0.5.4)" not in rows, "H2 the Server Setup row help says 1-3 = one light, 4-9 = + a ring")
    allb = b"".join(new.values()).decode("latin-1")
    check("1-3 give one light above the wearer" in allb and "4-9 give that light + a ring of 3-8 around it" in allb, "H2 the config default comment")

    # ---------------- L. start twice on a scratch copy of the live folder
    if not os.path.isdir(LIVE):
        print("note: no live Skyy_SkyyAccessories folder - L skipped")
        return
    lm = os.path.join(SCRATCH, "l-mods")
    dlive = os.path.join(lm, "Skyy_SkyyAccessories")
    shutil.copytree(LIVE, dlive)
    before0 = snap(dlive)
    P_ = lambda n: JClass(PKG + n, loader=L["new"])
    notes = []
    for rnd in range(2):
        P_("AccStore").DIR = Paths.get(os.path.join(dlive, "bags"))
        P_("AccCfg").FILE = Paths.get(os.path.join(dlive, "config.properties"))
        m51 = str(P_("AccCfg").migrate051())
        m55 = str(P_("AccCfg").migrate055())
        cs = str(P_("AccCfg").load(True))
        P_("AccNotice").FILE = Paths.get(os.path.join(dlive, "notices.properties"))
        P_("AccNotice").load()
        P_("CfgPub").start(Paths.get(lm), None)
        P_("CfgPub").shutdown()
        notes.append((m51, m55, cs[:80]))
    after = snap(dlive)
    chg = sorted(k for k in set(before0) | set(after) if before0.get(k) != after.get(k))
    check(not chg, "L two starts on a copy of the live data: no file changed (%d files) %s" % (len(before0), chg[:4]))
    print("L. two starts on the live copy: %d files unchanged; %s" % (len(before0), notes[-1]))
    BR.clear()


def main():
    for j in (JAR, OLD, COLL):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first (tools/acc_0_5_6_patch.py + build_skyyaccessories_0.5.6.py; SkyyCollections 0.2.7)")
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
    print("SkyyAccessories %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:40]:
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
