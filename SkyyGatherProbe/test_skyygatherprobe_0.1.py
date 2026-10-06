"""Bare-JVM check for SkyyGatherProbe 0.1 (+ SkyyGatherProbeB 0.1). Build first: python SkyyGatherProbe/build_skyygatherprobe_0.1.py

    python SkyyGatherProbe/test_skyygatherprobe_0.1.py [--keep]

  J  both jars: manifests (Main, IncludesAssetPack), exactly the expected classes and asset files, no .ui file
  N  NO OVERRIDE: every item id / asset path is new - not in Assets.zip, not in any installed mod in UserData/Mods (read-only scan of
     every .jar / .zip there, minus our own probe jars); only jar A and jar B share an id (the P3 twin, on purpose)
  R  the recipes and gates as specced: P1 100 Ore_Iron / 100 Wood_Oak_Trunk (ratio 100), P2 KnowledgeRequired, P4 ResourceTypeId
     Wood_Hardwood_Trunk x 20 (Oak carries it), P5 a decodable 64x64 PNG that differs from the vanilla Ore_Iron icon, P6 blocks = the
     vanilla Ore_Iron_Stone except Breaking (OreIron Q3 / Rocks Q3), probe pickaxe = flattened Iron pickaxe with OreIron Q3, the twin
     MaxStack 7 (A) / 13 (B); every id has its two name + two description lang lines
  A  every class loads and verifies (game JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + both jars)
  L  GpLogic on plain data: isTrunk / species / isBase cases; verdict() over the REAL vanilla pickaxe specs (Assets.zip) gives the
     expected answers for both probe blocks, vanilla Iron ore and Adamantite ore (incl. the first-match rule)
  E  the engine still decides the way the desk read says (bytecode fingerprint of BlockHarvestUtils.getSpecPowerDamageBlock +
     damageSingleBlock); if Hytale changes it, this fails and the probe's verdict lines need a re-read
  P  /gprobe and both usage variants: permission node skyygatherprobe.admin, empty permission groups, the engine's
     getPermissionGroupsRecursive() hands the node to no group (crosscheck.py audits the same with the whole SET)
Not testable without the game: everything the probes are for (P1-P6 in-game behaviour, the tree scan on real chunks).
Scratch: tools/dev/scratch/gather-p0/test (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import skyyart as SA

VERSION = "0.1"
JAR = os.path.join(HERE, "SkyyGatherProbe-%s.jar" % VERSION)
JAR_B = os.path.join(HERE, "SkyyGatherProbeB-%s.jar" % VERSION)
PKG = "com.skyy.gatherprobe."
CLASSES = sorted(PKG + c for c in ["GpLog", "GpLogic", "GpTrees", "GpTask", "GpCmds", "GProbeArg2Cmd", "GProbeArgCmd", "GProbeCmd",
                                   "SkyyGatherProbePlugin"])
CLASSES_B = ["com.skyy.gatherprobeb.SkyyGatherProbeBPlugin"]
IDS = ["Skyy_GProbe_P1_Ore", "Skyy_GProbe_P1_Log", "Skyy_GProbe_P2_Know", "Skyy_GProbe_P3_Twin", "Skyy_GProbe_P4_Res",
       "Skyy_GProbe_P5_Icon", "Skyy_GProbe_P6_Ore", "Skyy_GProbe_P6_Rock", "Skyy_GProbe_P6_Pick"]
NODE = "skyygatherprobe.admin"
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
SCRATCH = os.path.join(TOOLS, "dev", "scratch", "gather-p0", "test")
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def items_of(z):
    return dict((n.rsplit("/", 1)[1][:-5], json.loads(z.read(n))) for n in z.namelist()
                if n.startswith("Server/Item/Items/") and n.endswith(".json"))


def lang_of(z):
    out = {}
    for l in z.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines():
        if "=" in l:
            k, v = l.split("=", 1)
            out[k] = v
    return out


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    za, zb, az = zipfile.ZipFile(JAR), zipfile.ZipFile(JAR_B), zipfile.ZipFile(ASSETS)
    # ---------------- J
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    check(ma["Main"] == PKG + "SkyyGatherProbePlugin" and ma["IncludesAssetPack"] is True, "J. jar A manifest")
    check(mb["Main"] == CLASSES_B[0] and mb["IncludesAssetPack"] is True, "J. jar B manifest")
    ca = sorted(n[:-6].replace("/", ".") for n in za.namelist() if n.endswith(".class"))
    cb = sorted(n[:-6].replace("/", ".") for n in zb.namelist() if n.endswith(".class"))
    check(ca == CLASSES, "J. jar A classes: %s" % ca)
    check(cb == CLASSES_B, "J. jar B classes: %s" % cb)
    check(not any(n.lower().endswith(".ui") for n in za.namelist() + zb.namelist()), "J. no .ui files")
    ia, ib = items_of(za), items_of(zb)
    check(sorted(ia) == sorted(IDS), "J. jar A items: %s" % sorted(ia))
    check(sorted(ib) == ["Skyy_GProbe_P3_Twin"], "J. jar B items: %s" % sorted(ib))
    assets_a = sorted(n for n in za.namelist() if not n.endswith(".class") and n != "manifest.json")
    check(len(assets_a) == len(IDS) + 2, "J. jar A assets = 9 items + lang + 1 icon: %s" % assets_a)

    # ---------------- N
    az_names = set(az.namelist())
    az_ids = set(n.rsplit("/", 1)[1][:-5] for n in az_names if n.startswith("Server/Item/") and n.endswith(".json"))
    for n in assets_a + [x for x in zb.namelist() if not x.endswith(".class") and x != "manifest.json"]:
        if not n.endswith("server.lang"):
            check(n not in az_names, "N. %s exists in Assets.zip" % n)
    for i in IDS:
        check(i not in az_ids and i.startswith("Skyy_GProbe_"), "N. id %s is new (not a vanilla id)" % i)
    mods = os.path.join(B.USERDATA, "Mods")
    seen, scanned = {}, 0
    for f in sorted(os.listdir(mods)) if os.path.isdir(mods) else []:
        p = os.path.join(mods, f)
        if not (f.endswith(".jar") or f.endswith(".zip")) or f.startswith("SkyyGatherProbe") or not os.path.isfile(p):
            continue
        try:
            with zipfile.ZipFile(p) as mz:
                names = mz.namelist()
        except Exception:
            continue
        scanned += 1
        for n in names:
            if "/Item/" in n and n.endswith(".json") and n.rsplit("/", 1)[1][:-5] in IDS:
                seen.setdefault(n.rsplit("/", 1)[1][:-5], []).append(f)
            if n.endswith("Icons/ItemsGenerated/Skyy_GProbe_P5_Icon.png"):
                seen.setdefault("P5 icon", []).append(f)
    check(not seen, "N. probe ids also defined by installed mods: %s" % seen)
    print("N. no override: %d ids new vs Assets.zip and %d installed mod files" % (len(IDS), scanned))

    # ---------------- R
    def rin(i):
        return ia[i]["Recipe"]["Input"]
    check(rin("Skyy_GProbe_P1_Ore") == [{"ItemId": "Ore_Iron", "Quantity": 100}], "R. P1 ore recipe")
    check(rin("Skyy_GProbe_P1_Log") == [{"ItemId": "Wood_Oak_Trunk", "Quantity": 100}], "R. P1 log recipe")
    for i in ("Skyy_GProbe_P1_Ore", "Skyy_GProbe_P1_Log", "Skyy_GProbe_P2_Know", "Skyy_GProbe_P4_Res", "Skyy_GProbe_P5_Icon"):
        r = ia[i]["Recipe"]
        check(r["BenchRequirement"] == [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Crafting"]}],
              "R. %s at the Workbench Crafting tab" % i)
        check(r["KnowledgeRequired"] is (i == "Skyy_GProbe_P2_Know"), "R. %s KnowledgeRequired" % i)
    for i in ("Skyy_GProbe_P3_Twin", "Skyy_GProbe_P6_Ore", "Skyy_GProbe_P6_Rock", "Skyy_GProbe_P6_Pick"):
        check("Recipe" not in ia[i] and "Parent" not in ia[i], "R. %s has no recipe and no parent" % i)
    check(rin("Skyy_GProbe_P4_Res") == [{"ResourceTypeId": "Wood_Hardwood_Trunk", "Quantity": 20}], "R. P4 recipe")
    van = dict((n.rsplit("/", 1)[1][:-5], n) for n in az_names if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    oak = json.loads(az.read(van["Wood_Oak_Trunk"]))
    check(any(r.get("Id") == "Wood_Hardwood_Trunk" for r in oak.get("ResourceTypes", [])), "R. Oak carries Wood_Hardwood_Trunk")
    icon_path = "Common/" + ia["Skyy_GProbe_P5_Icon"]["Icon"]
    check(icon_path in za.namelist(), "R. P5 icon shipped at its Icon path")
    png = za.read(icon_path)
    img = SA.png_decode(png)
    vimg = SA.png_decode(az.read("Common/Icons/ItemsGenerated/Ore_Iron.png"))
    check((img.w, img.h) == (vimg.w, vimg.h) == (64, 64), "R. P5 icon 64x64 like the vanilla icon")
    check(img.px != vimg.px, "R. P5 icon differs from the vanilla icon")
    alpha_same = all(img.px[k] == vimg.px[k] for k in range(3, len(img.px), 4))
    check(alpha_same, "R. P5 icon keeps the vanilla alpha (only colours change)")
    purple = 0
    for k in range(0, len(img.px), 4):
        if img.px[k + 3] > 200 and img.px[k + 2] > img.px[k + 1] + 20:
            purple += 1
    check(purple > 100, "R. P5 icon is purple (%d blue-over-green opaque pixels)" % purple)
    ois = json.loads(az.read(van["Ore_Iron_Stone"]))
    for i, gt in (("Skyy_GProbe_P6_Ore", "OreIron"), ("Skyy_GProbe_P6_Rock", "Rocks")):
        d = json.loads(json.dumps(ia[i]))
        br = d["BlockType"]["Gathering"]["Breaking"]
        check(br["GatherType"] == gt and br["Quality"] == 3, "R. %s Breaking %s Q3" % (i, gt))
        check(br["DropList"] == ois["BlockType"]["Gathering"]["Breaking"]["DropList"], "R. %s drops = vanilla Iron ore drops" % i)
        br.pop("Quality")
        br["GatherType"] = "OreIron"
        d.pop("TranslationProperties")
        o2 = dict(ois)
        o2.pop("TranslationProperties")
        check(d == o2, "R. %s = Ore_Iron_Stone except name + Breaking gate" % i)
    pk = ia["Skyy_GProbe_P6_Pick"]
    crude, iron = json.loads(az.read(van["Tool_Pickaxe_Crude"])), json.loads(az.read(van["Tool_Pickaxe_Iron"]))
    specs = pk["Tool"]["Specs"]
    check([s["GatherType"] for s in specs] == [s["GatherType"] for s in iron["Tool"]["Specs"]], "R. probe pickaxe specs = Iron's order")
    for s, v in zip(specs, iron["Tool"]["Specs"]):
        exp = dict(v)
        if v["GatherType"] == "OreIron":
            exp["Quality"] = 3
        check(s == exp, "R. probe pickaxe spec %s" % v["GatherType"])
    check(pk.get("Interactions") == crude.get("Interactions") and pk.get("Model") == iron.get("Model"), "R. probe pickaxe = Crude + Iron flattened")
    check(ia["Skyy_GProbe_P3_Twin"]["MaxStack"] == 7 and ib["Skyy_GProbe_P3_Twin"]["MaxStack"] == 13, "R. twin MaxStack 7 (A) / 13 (B)")
    la, lb = lang_of(za), lang_of(zb)
    for i in IDS:
        for pre in ("", "server."):
            for k in ("name", "description"):
                check(("%sitems.%s.%s" % (pre, i, k)) in la, "R. lang %sitems.%s.%s" % (pre, i, k))
    check("from jar A" in la["server.items.Skyy_GProbe_P3_Twin.name"] and "from jar B" in lb["server.items.Skyy_GProbe_P3_Twin.name"],
          "R. twin names say jar A / jar B")
    check(sorted(lb) == sorted(k for k in la if "Skyy_GProbe_P3_Twin" in k), "R. jar B lang = only the twin's 4 lines")

    # ---------------- A
    import jpype
    from jpype import JClass
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + SCRATCH,
                   classpath=[B.SERVER_JAR, JAR, JAR_B, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    for n in CLASSES + CLASSES_B:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("A. load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified %d classes (-Xverify:all)" % (len(CLASSES) + len(CLASSES_B)))
    if FAILS:
        return

    # ---------------- L
    L = JClass(PKG + "GpLogic")
    for s, t in (("Wood_Oak_Trunk", "Oak"), ("Wood_Fig_Blue_Trunk", "Fig_Blue"), ("Wood_Wisteria_Wild_Trunk", "Wisteria_Wild")):
        check(bool(L.isTrunk(s)) and str(L.species(s)) == t, "L. %s -> %s" % (s, t))
    for s in ("Wood_Oak_Trunk_Full", "Wood_Oak_Trunk_Half", "Wood_Oak_Branch_Long", "Wood_Oak_Roots", "Rock_Stone", None, "Wood__Trunk"):
        check(not bool(L.isTrunk(s)) and L.species(s) is None, "L. %r is not a natural trunk" % s)
    for self_, below, exp in (("Wood_Oak_Trunk", "Soil_Grass", True), ("Wood_Oak_Trunk", "Wood_Oak_Roots", True),
                              ("Wood_Oak_Trunk", "Rock_Stone", True), ("Wood_Oak_Trunk", "Wood_Oak_Trunk", False),
                              ("Wood_Oak_Trunk", "Empty", False), ("Wood_Oak_Trunk", "", False), ("Wood_Oak_Trunk", None, False),
                              ("Wood_Oak_Trunk", "Plant_Leaves_Oak", False), ("Wood_Oak_Trunk", "Wood_Oak_Branch_Long", False),
                              ("Wood_Oak_Trunk", "Wood_Birch_Trunk", False), ("Rock_Stone", "Soil_Grass", False)):
        check(bool(L.isBase(self_, below)) == exp, "L. isBase(%s, %s) = %s" % (self_, below, exp))
    JStr, JInt, JFloat = JClass("java.lang.String"), jpype.JInt, jpype.JFloat

    def verdict(item_id, gt, q):
        it = json.loads(az.read(van[item_id]))
        sp = it["Tool"]["Specs"] if "Tool" in it else crude["Tool"]["Specs"]
        if item_id == "Skyy_GProbe_P6_Pick":
            sp = specs
        gts = jpype.JArray(JStr)([s["GatherType"] for s in sp])
        qs = jpype.JArray(JInt)([int(s.get("Quality", 0)) for s in sp])
        pw = jpype.JArray(JFloat)([float(s["Power"]) for s in sp])
        return str(L.verdict(gts, qs, pw, gt, q))
    van["Skyy_GProbe_P6_Pick"] = van["Tool_Pickaxe_Iron"]
    for tool, gt, q, exp in (("Tool_Pickaxe_Crude", "OreIron", 3, "REFUSED"), ("Tool_Pickaxe_Mithril", "OreIron", 3, "REFUSED"),
                             ("Skyy_GProbe_P6_Pick", "OreIron", 3, "ALLOWED"), ("Tool_Pickaxe_Crude", "Rocks", 3, "REFUSED"),
                             ("Tool_Pickaxe_Copper", "Rocks", 3, "REFUSED"), ("Tool_Pickaxe_Iron", "Rocks", 3, "ALLOWED"),
                             ("Tool_Pickaxe_Thorium", "Rocks", 3, "ALLOWED"), ("Tool_Pickaxe_Crude", "OreIron", 0, "ALLOWED"),
                             ("Tool_Pickaxe_Iron", "OreAdamantite", 4, "REFUSED"), ("Tool_Pickaxe_Thorium", "OreAdamantite", 4, "ALLOWED"),
                             ("Tool_Pickaxe_Iron", "Woods", 0, "ALLOWED"), ("Tool_Pickaxe_Iron", "NoSuchType", 0, "NO SPEC")):
        v = verdict(tool, gt, q)
        check(v.startswith(exp), "L. verdict %s on %s Q%d = %s (got %s)" % (tool, gt, q, exp, v))
    # first-match rule: a later spec of the same type never rescues a refused first one
    v = str(L.verdict(jpype.JArray(JStr)(["OreIron", "OreIron"]), jpype.JArray(JInt)([0, 9]), jpype.JArray(JFloat)([1.0, 1.0]), "OreIron", 3))
    check(v.startswith("REFUSED"), "L. verdict uses the FIRST matching spec (engine rule): %s" % v)

    # ---------------- E
    IP = JClass("javassist.bytecode.InstructionPrinter")
    PS, BOS = JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    pool = JClass("javassist.ClassPool")(False)
    pool.appendSystemPath()
    pool.appendClassPath(B.SERVER_JAR)
    cc = pool.get("com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils")

    def dis(name):
        out = []
        for mm in cc.getDeclaredMethods():
            if str(mm.getName()) == name:
                bos = BOS()
                IP(PS(bos)).print_(mm)
                out.append(str(bos.toString()))
        return "\n".join(out)
    g = dis("getSpecPowerDamageBlock")
    check(g.count("ItemToolSpec.getQuality") == 2 and g.count("if_icmpge") == 3 and g.count("java.util.Objects.equals") == 1
          and "BlockBreakingDropType.getQuality" in g and "Item.getWeapon" in g and "ItemToolSpec.getAssetMap" in g,
          "E. getSpecPowerDamageBlock still = first spec of the block's GatherType, quality >= block quality, unarmed asset fallback")
    d = dis("damageSingleBlock")
    i0 = d.find("getSpecPowerDamageBlock")
    check(i0 > 0 and d.find("ItemToolSpec.getPower", i0) > i0 and "GatheringConfig.getUnbreakableBlockConfig" in d
          and "getIncorrectMaterialSoundLayerIndex" in d and d.find("DamageBlockEvent.<init>") > i0,
          "E. damageSingleBlock: power from the spec, the unbreakable effect + incorrect-material sound path, DamageBlockEvent after")
    print("E. engine bytecode fingerprint done")

    # ---------------- P
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in ("GProbeCmd", "GProbeArgCmd", "GProbeArg2Cmd"):
        try:
            c = JClass(PKG + cn)()
        except Exception as e:
            check(False, "P. construct %s: %s" % (cn, e))
            continue
        perm = c.getPermission()
        groups = fld.get(c)
        check(perm is not None and NODE in str(perm.getId() if hasattr(perm, "getId") else perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        check(groups is not None and len(groups) == 0, "P. %s permission groups empty (%s)" % (cn, groups))
        if cn == "GProbeCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            check(not leak, "P. getPermissionGroupsRecursive gives %s to no group (leak: %s)" % (NODE, leak))
    print("P. permissions done")


try:
    main()
finally:
    if "--keep" not in sys.argv:
        shutil.rmtree(SCRATCH, ignore_errors=True)
print("%d ok, %d fail(s)" % (OKS[0], len(FAILS)))
sys.exit(1 if FAILS else 0)
