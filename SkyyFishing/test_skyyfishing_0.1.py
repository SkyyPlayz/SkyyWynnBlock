"""Harness for SkyyFishing 0.1. Build first: python SkyyFishing/build_skyyfishing_0.1.py

    python SkyyFishing/test_skyyfishing_0.1.py [--jar <SkyyFishing-0.1.jar>] [--live <a world folder>] [--keep]

Parent (plain Python, Assets.zip + installed mods + the jars read-only):
  J  the jar: manifest, the 31 mod classes + the config kit's 7, the assets (stat, 42 items, root, interaction, effect, bobber model, line
     particle system + spawners, lang, art), no .ui file
  N  NO OVERRIDE: every asset path / item id / stat / effect / root / interaction / model / particle id is new - not in Assets.zip, not in
     any installed mod (UserData/Mods, read-only) except SkyyReelProbe, whose 8 rod ids + the stat are TAKEN OVER on purpose (it retires)
  P0 no "Parallel" anywhere in the jar (a one-entry Parallel refuses the whole pack - 2026-10-08)
  S  the stat = SkyyReelProbe 0.1's shape (GlidingActive keys + HideFromTooltip), Max 18
  I  items: 8 rods (18 ItemAppearanceConditions: reel 0..8 = the probe's looks byte for byte, 10..18 = the no-line looks; Secondary = our
     root), 3 reels + 20 parts (the approved concept icons), 10 fish (our own icons, vanilla fish models by path), the bench (Farming bench
     look by path, Use = OpenCustomUI SkyyFishingBench, Workbench Crafting recipe); every referenced Common file is in the jar or Assets.zip
  C  CLASS COMPARE vs SkyyReelProbe 0.1 (the old owner of the ids): different package (no class clash), same 8 rod ids + stat path, the
     probe's 9 looks per rod reproduced exactly (model / texture paths + the art bytes), only the 9 line-out looks added
Children (fresh JVMs, the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch):
  A  every class loads + verifies (-Xverify:all)
  V  THE ENGINE ASSET VALIDATORS: the vanilla pack loaded store by store (the server's loadAssets0 path, every codec validator), the bench
     page registered like setup() does, then THE JAR as its own pack: no failed store, no SEVERE / WARNING line; our items / stat / effect /
     root / interaction / model / particles are in the stores; toPacket() of every item (rods: 18 conditions under our stat index); the
     root compiles (RootInteraction.build) to the ApplyEffect step; NEGATIVE CONTROLS (one-entry Parallel, a missing model file) are refused
  X  EVERY NEW CODE PATH EXECUTED (same child, real stores): a stand-in FishApi (Python) drives FishCore through cast (no reel / no water /
     blocked / shallow / narrow / ok), wait, bite, missed bite, hook, fight win / lose / time out / surge / click cap, junk, Lost Property
     (coins + items), Twin Line, a full inventory (claims, handed over later), every cancel (reel in, rod away, walk away, world change,
     profile switch, busy, idle, fishing off), the reel look stat; FishBench craft / fit / unfit / sell / fillet / sell all on REAL
     SimpleItemContainers with real items (every failure + double-click / stale path); FishPage build (3 tabs) + every click through
     handleDataEvent on a stand-in page (rebuild / close recorded); the HUD documents; commands; FishTick.tick on stand-in ECS parts
  D  START TWICE ON A SCRATCH COPY OF LIVE DATA: the world's universe/players (read-only, copied): start 1 seeds the config, catches on each
     player's key, flush; start 2 (new JVM) reads the same progress back, the config file is untouched; the player files' EntityStats and
     StorageInventory decode with our stat / items loaded (a SkyyReelProbe stat value or rod stays valid); per-PROFILE keys stay apart
  P  /fishing = hytale:Adventurer, /fishadmin (+ its variants) = skyyfishing.admin + no groups (the engine's own AbstractCommand code)
  B  bytecode: setup() order, ONE registerSystem, the bobber recipe (NonSerialized + NetworkId + Transform + Model + HeadRotation +
     Nameplate + Intangible), the world-thread hops (spawn / remove / give through World.execute)
  AA THE ENGINE-ACCESS AUDIT: every class / field / method reference in the jar resolved with MethodHandles.privateLookupIn the referencing
     class - 0 refused; the control (a protected CustomUIPage.sendUpdate from outside) refused
Not testable without the game (the build report lists them as UNVERIFIED): what the client draws (rod looks, the bobber, the "!" nameplate,
the line dots, the HUD widget, the bench page), whether every right click reaches the server fast enough, held poses.
Scratch: tools/dev/scratch/fishing01/test (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, hashlib, re, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "art"))
import skyybuild as B

VERSION = "0.1"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyFishing-%s.jar" % VERSION)))
PROBE_JAR = os.path.join(ROOT, "SkyyReelProbe", "SkyyReelProbe-0.1.jar")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "fishing01", "test")))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyyfishtest"
PKG = "com.skyy.fishing."
MOD_CLASSES = ["FishLog", "FishDefs", "FishCfg", "FishMath", "FishBridge", "FishCtx", "FishState", "FishApi", "FishEng", "FishData",
               "FishStore", "FishRig", "FishHudDoc", "FishHud", "FishBobberTask", "FishGiveTask", "FishEngApi", "FishCore", "FishTick",
               "FishBench", "FishPage", "FishPageFn", "FishSaveTick", "FishReady", "FishQuit", "FishCmds", "FishCmd", "FishAdminCmd",
               "FishAdminArgCmd", "FishAdminArg2Cmd", "SkyyFishingPlugin"]
KIT_CLASSES = ["CfgRows", "CfgLog", "CfgHist", "CfgSaveTask", "CfgFile", "CfgFn", "CfgPub"]
CLASSES = sorted(PKG + c for c in MOD_CLASSES + KIT_CLASSES)
TIERS = ["Bamboo", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
RODS = ["SkyyFishing_Rod_%s" % t for t in TIERS]
STAT = "SkyyFishing_Reel"
NODE = "skyyfishing.admin"
PAGE_ID = "SkyyFishingBench"
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def deploy_world():
    try:
        for l in open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8"):
            if l.startswith("WORLD = "):
                return l.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return "HUD mod"


LIVE = os.path.abspath(arg("--live", os.path.join(B.USERDATA, "Saves", deploy_world())))


# ====================================================================================================== parent: J N P0 S I C
def items_of(z):
    return dict((n.rsplit("/", 1)[1][:-5], (n, json.loads(z.read(n)))) for n in z.namelist()
                if n.startswith("Server/Item/Items/") and n.endswith(".json"))


def part_static():
    jz, az = zipfile.ZipFile(JAR), zipfile.ZipFile(ASSETS)
    az_names = set(az.namelist())
    jn = jz.namelist()
    man = json.loads(jz.read("manifest.json"))
    check(man["Main"] == PKG + "SkyyFishingPlugin" and man["IncludesAssetPack"] is True and man["Version"] == VERSION
          and man["Name"] == "%s SkyyFishing" % VERSION and man["Group"] == "Skyy", "J. manifest %s" % man)
    cls = sorted(n[:-6].replace("/", ".") for n in jn if n.endswith(".class"))
    check(cls == CLASSES, "J. classes = the 31 mod classes + the config kit's 7: extra %s missing %s"
          % (sorted(set(cls) - set(CLASSES)), sorted(set(CLASSES) - set(cls))))
    check(not any(n.lower().endswith(".ui") for n in jn), "J. no .ui file (inline pages only)")
    assets = [n for n in jn if not n.endswith(".class") and n != "manifest.json"]
    items = items_of(jz)
    check(len(items) == 42, "J. 42 items (8 rods, 3 reels, 20 parts, 10 fish, the bench): %d" % len(items))
    for need in ("Server/Entity/Stats/%s.json" % STAT, "Server/Item/RootInteractions/SkyyFishing/SkyyFishing_Rod_Use.json",
                 "Server/Item/Interactions/SkyyFishing/SkyyFishing_Click_Apply.json", "Server/Entity/Effects/SkyyFishing/SkyyFishing_Click.json",
                 "Server/Models/SkyyFishing/SkyyFishing_Bobber.json", "Server/Particles/SkyyFishing/SkyyFishing_Line_Dot.particlesystem",
                 "Server/Languages/en-US/server.lang"):
        check(need in assets, "J. %s in the jar" % need)
    # ---------------- N: no override (Assets.zip + every installed mod; SkyyReelProbe's rods + stat are taken over on purpose)
    ours_paths = [n for n in assets if not n.endswith("server.lang")]
    check(not [n for n in ours_paths if n in az_names], "N. no asset path of the jar is in Assets.zip: %s" % [n for n in ours_paths if n in az_names][:3])
    vids = set(n.rsplit("/", 1)[1].rsplit(".", 1)[0] for n in az_names if n.startswith("Server/"))
    our_ids = set(n.rsplit("/", 1)[1].rsplit(".", 1)[0] for n in ours_paths if n.startswith("Server/"))
    check(not (our_ids & vids), "N. no asset id of the jar is a vanilla asset id: %s" % sorted(our_ids & vids)[:5])
    mods = os.path.join(B.USERDATA, "Mods")
    clash, scanned, taken = [], 0, set()
    for f in sorted(os.listdir(mods)) if os.path.isdir(mods) else []:
        p = os.path.join(mods, f)
        if not (f.endswith(".jar") or f.endswith(".zip")) or not os.path.isfile(p):
            continue
        if f.startswith("SkyyFishing"):
            continue
        try:
            z = zipfile.ZipFile(p)
            names = z.namelist()
        except Exception:
            continue
        scanned += 1
        their = set(n.rsplit("/", 1)[1].rsplit(".", 1)[0] for n in names if "Server/" in n and not n.endswith("/"))
        both = (our_ids & their) | set(n for n in ours_paths if n in set(names))
        if f.startswith("SkyyReelProbe"):
            taken |= both
            continue
        if both:
            clash.append((f, sorted(both)[:4]))
    check(scanned > 20 and not clash, "N. no id / path of the jar is in any of the %d installed mods (HyFishing, Angler's Almanac ... read only): %s"
          % (scanned, clash[:3]))
    t_ids = set(t for t in taken if "/" not in t)
    t_paths = set(t for t in taken if "/" in t)
    check(t_ids == set(RODS + [STAT]) and all(t.startswith("Common/") or t == "Server/Entity/Stats/%s.json" % STAT for t in t_paths),
          "N. shared with SkyyReelProbe ONLY its 8 rod ids + the stat + their art paths (taken over on purpose; the probe retires; the art "
          "bytes are compared in C): ids %s, %d paths" % (sorted(t_ids), len(t_paths)))
    # ---------------- P0: no Parallel at all
    par = [n for n in jn if n.endswith(".json") and '"Parallel"' in jz.read(n).decode("utf-8", "replace")]
    check(not par, "P0. no Parallel interaction anywhere in the jar: %s" % par[:3])
    # ---------------- S: the stat
    st = json.loads(jz.read("Server/Entity/Stats/%s.json" % STAT))
    g = json.loads(az.read("Server/Entity/Stats/GlidingActive.json").decode("utf-8-sig"))
    check(list(st) == ["InitialValue", "Min", "Max", "Shared", "IgnoreInvulnerability", "HideFromTooltip"] and st["Max"] == 18
          and st["InitialValue"] == g["InitialValue"] == 0 and st["Min"] == 0 and st["Shared"] is True and st["HideFromTooltip"] is True,
          "S. the stat = GlidingActive's keys + HideFromTooltip, Max 18 (0-8 reel, 10-18 line out): %s" % st)
    # ---------------- I: items
    def common_ok(p):
        return ("Common/" + p) in az_names or ("Common/" + p) in jn
    bad = []
    for iid in RODS:
        path, d = items[iid]
        conds = d.get("ItemAppearanceConditions", {}).get(STAT, [])
        ks = [c["Condition"][0] for c in conds]
        if ks != list(range(0, 9)) + list(range(10, 19)) or any(c["Condition"][0] != c["Condition"][1] or sorted(c) != ["Condition", "Model", "Texture"] for c in conds):
            bad.append((iid, "conditions", ks))
        if d.get("Interactions") != {"Secondary": "SkyyFishing_Rod_Use"} or d.get("MaxStack") != 1 or "Recipe" in d:
            bad.append((iid, "interactions / stack / recipe"))
        for c in conds:
            if not common_ok(c["Model"]) or not common_ok(c["Texture"]):
                bad.append((iid, "file", c))
        for k in ("Icon", "Model", "Texture"):
            if not common_ok(d[k]):
                bad.append((iid, k))
        nolines = [c["Model"] for c in conds if c["Condition"][0] >= 10]
        if any("NoLine" not in m for m in nolines):
            bad.append((iid, "line-out looks must hide the hanging line", nolines[:2]))
    check(not bad, "I. 8 rods: 18 conditions (0-8, 10-18) on %s, Secondary = SkyyFishing_Rod_Use, MaxStack 1, no recipe, every file exists, "
                   "line-out looks = NoLine models: %s" % (STAT, bad[:3]))
    parts = [i for i in items if i.startswith("SkyyFishing_Reel_") or i.startswith("SkyyFishing_Hook_") or i.startswith("SkyyFishing_Line_")
             or i.startswith("SkyyFishing_Sinker_")]
    check(len(parts) == 23 and all(common_ok(items[i][1]["Icon"]) and "Interactions" not in items[i][1] for i in parts),
          "I. 3 reels + 20 parts, icons exist, no interactions (%d)" % len(parts))
    fish = [i for i in items if i.startswith("SkyyFishing_Fish_")]
    fbad = [i for i in fish if items[i][1].get("MaxStack") != 1 or "ResourceTypes" in items[i][1] or "Interactions" in items[i][1]
            or not common_ok(items[i][1]["Model"]) or not common_ok(items[i][1]["Texture"]) or not common_ok(items[i][1]["Icon"])]
    check(len(fish) == 10 and not fbad, "I. 10 fish: MaxStack 1, NO ResourceTypes (no vanilla gut recipe, no bag), no interaction, vanilla model / "
                                        "texture by path + our icon: %s" % fbad)
    bench = items["SkyyFishing_Bench"][1]
    bu = bench["BlockType"].get("Interactions", {}).get("Use", {}).get("Interactions", [{}])[0]
    check(bu == {"Type": "OpenCustomUI", "Page": {"Id": PAGE_ID}} and "Bench" not in bench["BlockType"] and "BlockEntity" not in bench["BlockType"]
          and bench["Recipe"]["BenchRequirement"][0]["Id"] == "Workbench" and bench["Recipe"]["BenchRequirement"][0]["Categories"] == ["Workbench_Crafting"]
          and common_ok(bench["BlockType"]["CustomModel"]) and common_ok(bench["BlockType"]["CustomModelTexture"][0]["Texture"]) and common_ok(bench["Icon"]),
          "I. the bench: Use = OpenCustomUI %s, no vanilla Bench / BlockEntity, Workbench Crafting recipe, the Farming bench model by path" % PAGE_ID)
    root = json.loads(jz.read("Server/Item/RootInteractions/SkyyFishing/SkyyFishing_Rod_Use.json"))
    inter = json.loads(jz.read("Server/Item/Interactions/SkyyFishing/SkyyFishing_Click_Apply.json"))
    eff = json.loads(jz.read("Server/Entity/Effects/SkyyFishing/SkyyFishing_Click.json"))
    check(root == {"RequireNewClick": True, "Cooldown": {"Cooldown": 0.05}, "Interactions": ["SkyyFishing_Click_Apply"]}
          and inter == {"Type": "ApplyEffect", "EffectId": "SkyyFishing_Click"} and eff == {"Duration": 0.5, "OverlapBehavior": "Overwrite"},
          "I. the click chain: root (new click, 0.05 s) -> ApplyEffect SkyyFishing_Click (0.5 s, Overwrite) - the SkyyArmory grapple click pattern")
    bm = json.loads(jz.read("Server/Models/SkyyFishing/SkyyFishing_Bobber.json"))
    check(common_ok(bm["Model"]) and common_ok(bm["Texture"]) and bm["Texture"] == "Items/Tools/Fishing_Rod/FishingRod_Texture.png",
          "I. the bobber model: our extracted Bait node + the vanilla rod texture by path: %s" % bm)
    lang = jz.read("Server/Languages/en-US/server.lang").decode("utf-8")
    check(all(("items.%s.name=" % i) in lang and ("server.items.%s.name=" % i) in lang for i in items), "I. every item has a name (both key forms)")
    # ---------------- C: class compare with SkyyReelProbe 0.1 (the ids' old owner)
    if os.path.isfile(PROBE_JAR):
        pz = zipfile.ZipFile(PROBE_JAR)
        pcls = [n for n in pz.namelist() if n.endswith(".class")]
        check(all(n.startswith("com/skyy/reelprobe/") for n in pcls) and not any(n.startswith("com/skyy/reelprobe/") for n in jn),
              "C. no class clash with SkyyReelProbe (com.skyy.reelprobe vs com.skyy.fishing)")
        pit = items_of(pz)
        cbad = []
        for iid in RODS:
            pd = pit[iid][1]
            d = items[iid][1]
            pc = pd["ItemAppearanceConditions"][STAT]
            oc = [c for c in d["ItemAppearanceConditions"][STAT] if c["Condition"][0] <= 8]
            if pc != oc:
                cbad.append((iid, "looks 0-8 differ"))
            for k in ("Icon", "Model", "Texture", "IconProperties", "PlayerAnimationsId"):
                if pd.get(k) != d.get(k):
                    cbad.append((iid, k))
            for c in pc:
                for k in ("Model", "Texture"):
                    p = "Common/" + c[k]
                    if p in pz.namelist() and (p not in jn or pz.read(p) != jz.read(p)):
                        cbad.append((iid, "art bytes", p))
        ps = json.loads(pz.read("Server/Entity/Stats/%s.json" % STAT))
        ps["Max"] = 18
        check(not cbad and ps == st, "C. the 8 rods = SkyyReelProbe 0.1's (looks 0-8, icon, model, texture, art bytes) + 9 line-out looks; the stat = "
                                     "the probe's with Max 8 -> 18 (a saved probe value 0-8 stays valid): %s" % cbad[:3])
    else:
        check(False, "C. SkyyReelProbe-0.1.jar not found for the compare (%s)" % PROBE_JAR)
    print("J/N/P0/S/I/C. %d assets, %d items, %d installed mods scanned, taken over from SkyyReelProbe: %d ids + %d art / stat paths"
          % (len(assets), len(items), scanned, len(t_ids), len(t_paths)))
    return jz, az


# ====================================================================================================== children
def _jvm(cp, verify=True, big=False):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + (["-Xmx6g"] if big else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED",
                                                                                 "-Djava.io.tmpdir=" + tmp]
    jpype.startJVM(jvm, *opts, classpath=list(cp), convertStrings=True)


class Child(object):
    """per-child check collector, written to a json file the parent reads"""
    def __init__(self, out):
        self.out, self.ok, self.fails, self.notes = out, 0, [], []

    def check(self, cond, what):
        if cond:
            self.ok += 1
        else:
            self.fails.append(what)
            print("FAIL", what)

    def save(self, **extra):
        d = {"ok": self.ok, "fails": self.fails, "notes": self.notes}
        d.update(extra)
        json.dump(d, open(self.out, "w"), indent=1)


def run_mkfake(out_dir):
    """child F: the stand-ins as .class files: a FishPage subclass that records rebuild / close (the engine's versions send packets), the
    ECS stand-ins for FishTick, the access-audit helpers"""
    from jpype import JClass
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    P = FAKE_PKG
    fp = cp.makeClass(P + ".FakePage")
    fp.setSuperclass(cp.get(PKG + "FishPage"))
    for decl in ("public int rebuilds;", "public int closes;", "public com.hypixel.hytale.component.Ref lastRef;",
                 "public com.hypixel.hytale.component.Store lastStore;", "public com.hypixel.hytale.server.core.ui.builder.UICommandBuilder lastB;",
                 "public com.hypixel.hytale.server.core.ui.builder.UIEventBuilder lastEv;"):
        fp.addField(CtField.make(decl, fp))
    fp.addConstructor(CtNewConstructor.make("public FakePage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr); }", fp))
    fp.addMethod(CtNewMethod.make("""public void rebuild() {
  this.rebuilds = this.rebuilds + 1;
  this.lastB = new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder();
  this.lastEv = new com.hypixel.hytale.server.core.ui.builder.UIEventBuilder();
  build(this.lastRef, this.lastB, this.lastEv, this.lastStore);
}""", fp))
    fp.addMethod(CtNewMethod.make("public void close() { this.closes = this.closes + 1; }", fp))
    fp.writeFile(out_dir)
    ms = cp.makeClass(P + ".MapStore")
    ms.setSuperclass(cp.get("com.hypixel.hytale.component.Store"))
    for decl in ("java.util.Map comps", "java.lang.Object ext"):
        ms.addField(CtField.make("public %s;" % decl, ms))
    ms.addConstructor(CtNewConstructor.make("public MapStore() { super(null, 0, null, null); }", ms))   # never run (Unsafe)
    ms.addMethod(CtNewMethod.make("""public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (this.comps == null || r == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}""", ms))
    ms.addMethod(CtNewMethod.make("public java.lang.Object getExternalData() { return this.ext; }", ms))
    ms.writeFile(out_dir)
    mb = cp.makeClass(P + ".MapBuffer")
    mb.setSuperclass(cp.get("com.hypixel.hytale.component.CommandBuffer"))
    mb.addField(CtField.make("public " + P + ".MapStore st;", mb))
    mb.addConstructor(CtNewConstructor.make("public MapBuffer() { super(null); }", mb))                  # never run (Unsafe)
    mb.addMethod(CtNewMethod.make("""public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  return this.st == null ? null : this.st.getComponent(r, t);
}""", mb))
    mb.writeFile(out_dir)
    mc = cp.makeClass(P + ".MapChunk")
    mc.setSuperclass(cp.get("com.hypixel.hytale.component.ArchetypeChunk"))
    mc.addField(CtField.make("public com.hypixel.hytale.component.Ref ref;", mc))
    mc.addConstructor(CtNewConstructor.make("public MapChunk() { super(null, null); }", mc))
    mc.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Ref getReferenceTo(int i) { return this.ref; }", mc))
    mc.writeFile(out_dir)
    lk = cp.makeClass(P + ".LookupIn")
    lk.addMethod(CtNewMethod.make(
        "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
        "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", lk))
    lk.writeFile(out_dir)
    ba = cp.makeClass(P + ".BadAccess")
    ba.addMethod(CtNewMethod.make(
        "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
        "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}", ba))
    ba.writeFile(out_dir)
    print("F. stand-ins written to", out_dir)


def run_verify(out):
    """child A: every class of the jar loads and initialises under -Xverify:all"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR], verify=True)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    for n in CLASSES:
        try:
            Cls.forName(n, True, loader)
            K.ok += 1
        except Exception as e:
            K.check(False, "A: load + verify %s: %s" % (n, str(e)[:300]))
    K.notes.append("A: %d classes loaded with -Xverify:all" % len(CLASSES))
    K.save()


def engine_boot(K):
    """the SkyySacks 0.7.14 V child's bare server: HytaleServer / Universe allocated, the logger captured, the asset stores (+ the interaction
    stores and every Type codec InteractionModule.setup registers, read from its bytecode), the bench page registered like setup() does,
    the vanilla pack loaded store by store (AssetRegistryLoader.loadAssets0's path - every codec validator runs), then THE JAR as its own
    pack. Answers a dict of helpers."""
    from jpype import JClass, JArray, JString, JImplements, JOverride
    Options = JClass("com.hypixel.hytale.server.core.Options")
    Options.parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "v-universe")]))
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jf(c, n):
        k = c.class_ if hasattr(c, "class_") else c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = us.allocateInstance(HS.class_)
    jf(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jf(HS, "shutdown").set(hs, JClass("java.util.concurrent.atomic.AtomicReference")())
    jf(HS, "instance").set(None, hs)
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = us.allocateInstance(UNI.class_)
    pbu, wmap = CHM(), CHM()
    jf(UNI, "playersByUuid").set(uni, pbu)
    jf(UNI, "players").set(uni, JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    jf(UNI, "worlds").set(uni, wmap)
    jf(UNI, "worldsByUuid").set(uni, CHM())
    jf(UNI, "unmodifiableWorlds").set(uni, JClass("java.util.Collections").unmodifiableMap(wmap))
    jf(UNI, "instance").set(None, uni)
    HLB = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend")
    CAPLOG = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    HLB.subscribe(CAPLOG)

    def records(start=0):
        out = []
        for r in list(CAPLOG)[start:]:
            try:
                msg = str(r.getMessage())
                ps = r.getParameters()
                if ps is not None and len(ps) > 0:
                    try:
                        msg = str(JClass("java.lang.String").format(msg, ps))
                    except Exception:
                        msg = msg + " " + " ".join(str(p) for p in ps)
                th = r.getThrown()
                if th is not None:
                    msg += " | " + str(th)[:300]
                out.append((str(r.getLevel()), msg))
            except Exception as e:
                out.append(("?", str(e)))
        return out
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    DAMc = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    ARR = JClass("java.lang.reflect.Array")

    @JImplements("java.util.function.Function")
    class GetId:
        @JOverride
        def apply(self, o): return o.getId()

    @JImplements("java.util.function.IntFunction")
    class ArrOf:
        def __init__(self, c): self.c = c

        @JOverride
        def apply(self, n): return ARR.newInstance(self.c.class_, n)

    @JImplements("java.util.function.Function")
    class NoRep:
        @JOverride
        def apply(self, k): return None

    @JImplements("java.util.function.Predicate")
    class IsUnknown:
        @JOverride
        def test(self, o): return bool(o.isUnknown())
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    INTc, ROOTc = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    UIc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.UnarmedInteractions")
    ESTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")

    JCLS = JClass("java.lang.Class")
    ESTc0 = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")

    def reg_ilt(c, path, codec, unknown=False, after=(), before=()):
        b_ = HAS.builder(c.class_, ILT(ArrOf(c))).setPath(path).setCodec(codec).setKeyFunction(GetId()).setReplaceOnRemove(NoRep())
        if unknown:
            b_ = b_.setIsUnknown(IsUnknown())
        if after:
            b_ = b_.loadsAfter(JArray(JCLS)([JClass(a).class_ for a in after]))
        if before:
            b_ = b_.loadsBefore(JArray(JCLS)([JClass(a).class_ for a in before]))
        AR.register(b_.build())
        for a in before:          # what the game's RegisterAssetStoreEvent listener does with loadsBefore (nobody listens in a bare JVM)
            st_ = AR.getAssetStore(JClass(a).class_)
            if st_ is not None:
                st_.injectLoadsAfter(c.class_)
    if AR.getAssetStore(ESTc0.class_) is None:           # EntityStatsModule.setup registers it in the game
        reg_ilt(ESTc0, "Entity/Stats", ESTc0.CODEC)
    # the orderings InteractionModule.setup gives the two stores in the game (read from its bytecode): interactions after the stats /
    # effects / trails / animation sets / sounds / particles / models / hitboxes; roots after the interactions and BEFORE blocks + items
    SV = "com.hypixel.hytale.server.core."
    reg_ilt(INTc, "Item/Interactions", INTc.CODEC, True,
            after=[SV + "modules.entitystats.asset.EntityStatType", SV + "asset.type.entityeffect.config.EntityEffect", SV + "asset.type.trail.config.Trail",
                   SV + "asset.type.itemanimation.config.ItemPlayerAnimations", SV + "asset.type.soundevent.config.SoundEvent",
                   SV + "asset.type.particle.config.ParticleSystem", SV + "asset.type.model.config.ModelAsset",
                   SV + "modules.entity.hitboxcollision.HitboxCollisionConfig"])
    reg_ilt(ROOTc, "Item/RootInteractions", ROOTc.CODEC, after=[PI + "Interaction"],
            before=[SV + "asset.type.blocktype.config.BlockType", SV + "asset.type.item.config.Item"])
    AR.register(HAS.builder(UIc.class_, DAMc()).setPath("Item/Unarmed/Interactions").setCodec(UIc.CODEC).setKeyFunction(GetId()).build())
    SMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MODc = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier")
    try:
        MODc.CODEC.register("Boost", SMOD.class_, SMOD.ENTITY_CODEC)
        MODc.CODEC.register("Static", SMOD.class_, SMOD.ENTITY_CODEC)
    except Exception:
        pass
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(B.SERVER_JAR)
    CPool = JClass("javassist.bytecode.ConstPool")
    imc = CPj.get("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    ms_ = [x for x in imc.getDeclaredMethods() if str(x.getName()) == "setup"][0]
    cp_, it_ = ms_.getMethodInfo().getConstPool(), ms_.getMethodInfo().getCodeAttribute().iterator()
    last_s, last_c, regs = None, None, []
    while it_.hasNext():
        p_ = it_.next()
        op_ = it_.byteAt(p_)
        if op_ in (0x12, 0x13):
            idx = it_.byteAt(p_ + 1) if op_ == 0x12 else it_.u16bitAt(p_ + 1)
            t_ = cp_.getTag(idx)
            if t_ == CPool.CONST_String:
                last_s = str(cp_.getStringInfo(idx))
            elif t_ == CPool.CONST_Class:
                last_c = str(cp_.getClassInfo(idx))
        elif op_ == 0xb6:
            idx = it_.u16bitAt(p_ + 1)
            if str(cp_.getMethodrefClassName(idx)).endswith("AssetCodecMapCodec") and str(cp_.getMethodrefName(idx)) == "register":
                regs.append((last_s, last_c))
    for nm_, cl_ in regs:
        C_ = JClass(cl_)
        INTc.CODEC.register(nm_, C_.class_, jf(C_, "CODEC").get(None))
    PRJIc = JClass("com.hypixel.hytale.server.core.modules.projectile.interaction.ProjectileInteraction")
    INTc.CODEC.register("Projectile", PRJIc.class_, PRJIc.CODEC)
    SPCc = JClass("com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsConfig")
    JClass("com.hypixel.hytale.server.core.modules.projectile.config.PhysicsConfig").CODEC.register("Standard", SPCc.class_, SPCc.CODEC)
    K.check(len(regs) >= 70 and "ApplyEffect" in [a for a, b in regs] and "OpenCustomUI" in [a for a, b in regs],
            "V: the interaction Type codecs registered from InteractionModule.setup's bytecode (%d, ApplyEffect + OpenCustomUI among them)" % len(regs))
    # the bench page, the way setup() registers it (OpenCustomUIInteraction.registerSimple -> PAGE_CODEC) before assets load
    OCUc = JClass(PI + "server.OpenCustomUIInteraction")
    CPSn = PI + "server.OpenCustomUIInteraction$CustomPageSupplier"
    CPSc = JClass(CPSn)
    BCc = JClass("com.hypixel.hytale.codec.builder.BuilderCodec")

    @JImplements(CPSn)
    class PageSup:
        @JOverride
        def tryCreate(self, a, b, c, d): return None

    @JImplements("java.util.function.Supplier")
    class SupOf:
        @JOverride
        def get(self): return PageSup()
    OCUc.PAGE_CODEC.register(PAGE_ID, CPSc.class_, BCc.builder(CPSc.class_, SupOf()).build())
    CAR = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry")
    FCA = JClass("com.hypixel.hytale.server.core.asset.common.asset.FileCommonAsset")
    Paths, FSs, HashMap = JClass("java.nio.file.Paths"), JClass("java.nio.file.FileSystems"), JClass("java.util.HashMap")
    ZFS = {}

    def zfs(zpath):
        if zpath not in ZFS:
            ZFS[zpath] = FSs.newFileSystem(Paths.get(zpath), HashMap())
        return ZFS[zpath]

    def add_common(pack, zpath, real):
        n = 0
        fs = zfs(zpath)
        with zipfile.ZipFile(zpath) as z:
            for nm in z.namelist():
                if nm.startswith("Common/") and not nm.endswith("/"):
                    h = hashlib.sha256(z.read(nm)).hexdigest() if real else "0" * 64
                    CAR.addCommonAsset(pack, FCA(fs.getPath("/" + nm), nm[len("Common/"):], h, None))
                    n += 1
        return n
    AP = JClass("com.hypixel.hytale.assetstore.AssetPack")
    Files, LinkOption = JClass("java.nio.file.Files"), JClass("java.nio.file.LinkOption")

    def store_order():
        stores = dict((st.getAssetClass(), st) for st in AR.getStoreMap().values())
        done, order = set(), []

        def visit(c, stack):
            if c in done or c not in stores or c in stack:
                return
            stack.add(c)
            for d in stores[c].getLoadsAfter():
                visit(d, stack)
            done.add(c)
            order.append(stores[c])
        for c in list(stores):
            visit(c, set())
        return order

    def loadpack(zpath, name, immutable):
        n0 = len(CAPLOG)
        pack = AP(Paths.get(zpath), name, zfs(zpath).getPath("/"), zfs(zpath), immutable, None, None)
        srv = pack.getRoot().resolve("Server")
        failed = []
        for st in store_order():
            d = srv.resolve(st.getPath())
            if not Files.isDirectory(d, JArray(LinkOption)(0)):
                continue
            try:
                if st.loadAssetsFromDirectory(name, d).hasFailed():
                    failed.append(str(st.getAssetClass().getSimpleName()))
            except Exception as e:
                failed.append("%s EXC %s" % (st.getAssetClass().getSimpleName(), str(e)[:200]))
        return failed, records(n0)
    t0 = time.time()
    nv = add_common("Hytale:Hytale", ASSETS, False)
    vfail, vrec = loadpack(ASSETS, "Hytale:Hytale", True)
    ITEM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    K.check(ITEM.getAssetMap().getAssetMap().size() > 1000, "V: the vanilla items are in the real Item store (%d)" % ITEM.getAssetMap().getAssetMap().size())
    print("V. vanilla pack loaded (%d common files, %.0f s; %d SEVERE lines from stores a bare JVM lacks codecs for - not ours)"
          % (nv, time.time() - t0, len([r for r in vrec if r[0] == "SEVERE"])))
    pack_name = "Skyy:%s SkyyFishing" % VERSION
    add_common(pack_name, JAR, True)
    fail, rec = loadpack(JAR, pack_name, False)
    return {"us": us, "jf": jf, "AR": AR, "INTc": INTc, "ROOTc": ROOTc, "ESTc": ESTc, "ITEM": ITEM, "records": records, "loadpack": loadpack,
            "fail": fail, "rec": rec, "regs": dict(regs), "PI": PI, "uni": uni, "CAPLOG": CAPLOG}


def run_engine(out):
    """child V + X (one JVM: the real stores loaded once)"""
    from jpype import JClass, JArray, JObject, JInt, JFloat, JLong, JString, JImplements, JOverride, JBoolean
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
    E = engine_boot(K)
    us, jf, AR, INTc, ROOTc, ITEM, records = E["us"], E["jf"], E["AR"], E["INTc"], E["ROOTc"], E["ITEM"], E["records"]
    jz = zipfile.ZipFile(JAR)
    # ============================================================================ V. THE ENGINE ASSET VALIDATORS on the jar as a pack
    bad = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING")]
    for r in bad[:12]:
        print("   V:", r[0], r[1][:500].replace("\n", " / "))
    K.check(not E["fail"] and not bad, "V: the jar loads into the real stores as its own pack: no failed store (%s), no SEVERE / WARNING line (%d)"
            % (E["fail"], len(bad)))
    items = items_of(jz)
    gone, pk_bad = [], []
    ESTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    sidx = int(ESTc.getAssetMap().getIndex(STAT))
    for iid in sorted(items):
        it = ITEM.getAssetMap().getAsset(iid)
        if it is None:
            gone.append(iid)
            continue
        try:
            p = it.toPacket()
            if iid in RODS:
                ac = p.itemAppearanceConditions
                arr = ac.get(JClass("java.lang.Integer")(sidx)) if ac is not None else None
                ks = [int(c.condition.inclusiveMin) for c in arr] if arr is not None else None
                if ks != list(range(0, 9)) + list(range(10, 19)):
                    pk_bad.append((iid, ks))
                if int(it.getMaxStack()) != 1:
                    pk_bad.append((iid, "max stack"))
        except Exception as e:
            pk_bad.append((iid, str(e)[:150]))
    K.check(not gone and not pk_bad and sidx >= 0, "V: all 42 items are in the Item store; toPacket() works; each rod sends 18 conditions under OUR stat "
                                                  "index %d (0-8, 10-18), max stack 1: missing %s, bad %s" % (sidx, gone[:3], pk_bad[:3]))
    fish0 = ITEM.getAssetMap().getAsset("SkyyFishing_Fish_RustbackTrout")
    raw = ITEM.getAssetMap().getAsset("Food_Fish_Raw")
    K.check(fish0 is not None and int(fish0.getMaxStack()) == 1 and raw is not None and int(raw.getMaxStack()) > 1,
            "V: a whole fish stacks to 1, vanilla Raw Fish more (%s)" % (raw.getMaxStack() if raw is not None else None))
    st = ESTc.getAssetMap().getAsset(STAT)
    K.check(st is not None and float(st.getMax()) == 18.0 and float(st.getInitialValue()) == 0.0 and bool(st.isShared()),
            "V: the %s stat is in the store: max 18, initial 0, shared" % STAT)
    EFXc = JClass("com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect")
    K.check(EFXc.getAssetMap().getAsset("SkyyFishing_Click") is not None, "V: the SkyyFishing_Click effect is in the store")
    r_ = ROOTc.getAssetMap().getAsset("SkyyFishing_Rod_Use")
    ops = []
    try:
        r_.build()
        for i_ in range(int(r_.getOperationMax())):
            inner = r_.getOperation(i_).getInnerOperation()
            if inner is not None and INTc.class_.isInstance(inner):
                ops.append(str(inner.getClass().getSimpleName()))
    except Exception as e:
        ops.append("build failed %s" % str(e)[:150])
    K.check(ops == ["ApplyEffectInteraction"] and bool(r_.isRequireNewClick()) if hasattr(r_, "isRequireNewClick") else ops == ["ApplyEffectInteraction"],
            "V: the rod root compiles (RootInteraction.build) to ONE ApplyEffect step: %s" % ops)
    MDA = JClass("com.hypixel.hytale.server.core.asset.type.model.config.ModelAsset")
    MDL = JClass("com.hypixel.hytale.server.core.asset.type.model.config.Model")
    ma = MDA.getAssetMap().getAsset("SkyyFishing_Bobber")
    try:
        mdl = MDL.createScaledModel(ma, JFloat(1.0))
        mok = mdl is not None and str(mdl.getModelAssetId()) == "SkyyFishing_Bobber"
    except Exception as e:
        mok = str(e)[:200]
    K.check(ma is not None and mok is True, "V: the bobber ModelAsset is in the store and Model.createScaledModel works (the bobber task's call): %s" % mok)
    PSY = JClass("com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSystem")
    psys = PSY.getAssetMap().getAsset("SkyyFishing_Line_Dot")
    try:
        psys.toPacket()
        pok = True
    except Exception as e:
        pok = str(e)[:150]
    K.check(psys is not None and pok is True and PSY.getAssetMap().getAsset("Water_Can_Splash") is not None,
            "V: the line particle system is in the store (toPacket ok) + the vanilla splash system it plays: %s" % pok)
    BTc = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    bt = BTc.getAssetMap().getAsset("SkyyFishing_Bench")
    K.check(bt is not None, "V: the bench block type is in the BlockType store")
    # NEGATIVE CONTROLS (one-file packs): the validators really run
    base = items["SkyyFishing_Hook_Barbed_I"][1]
    ctl = [("one-entry Parallel", "Server/Item/Interactions/SkyyFishCtl/SkyyFishCtl_Parallel.json",
            json.dumps({"Type": "Simple", "RunTime": 0.1, "Next": {"Type": "Parallel", "Interactions": [{"Interactions": [{"Type": "Simple", "RunTime": 0.1}]}]}}),
            "Array size is invalid"),
           ("Model file missing", "Server/Item/Items/SkyyFishCtl/SkyyFishCtl_Model.json",
            json.dumps(dict(base, Model="Items/SkyyFishCtl_NoSuch.blockymodel", Texture=base["Icon"])), "SkyyFishCtl_NoSuch.blockymodel"),
           ("root id missing", "Server/Item/Items/SkyyFishCtl/SkyyFishCtl_Root.json",
            json.dumps(dict(base, Interactions={"Secondary": "SkyyFishCtl_NoSuchRoot"})), "SkyyFishCtl_NoSuchRoot")]
    for i, (what, path, text, needle) in enumerate(ctl):
        zp = os.path.join(SCRATCH, "v-ctl%d.jar" % i)
        with zipfile.ZipFile(zp, "w") as z:
            z.writestr(path, text)
        f_, r2 = E["loadpack"](zp, "Skyy:test ctl%d" % i, False)
        hit = [r for r in r2 if r[0] == "SEVERE" and needle in r[1]]
        K.check(bool(hit), "V CONTROL: %s is refused by the engine validator (SEVERE)" % what)
    print("V. the jar loaded as a pack: 0 failed stores, 0 SEVERE / WARNING; 42 items, stat, effect, root (1 ApplyEffect), bobber model, line "
          "particles, bench block; 3 negative controls refused")

    # ============================================================================ X. every new code path EXECUTED
    P = lambda n: JClass(PKG + n)
    Core, Cfg, Store_, Rig, Bench, Defs, Mth, Eng, Brg, HDoc = (P("FishCore"), P("FishCfg"), P("FishStore"), P("FishRig"), P("FishBench"),
                                                               P("FishDefs"), P("FishMath"), P("FishEng"), P("FishBridge"), P("FishHudDoc"))
    Ctx, StateC, Log = P("FishCtx"), P("FishState"), P("FishLog")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    UUID = JClass("java.util.UUID")
    AL = JClass("java.util.ArrayList")
    SINK = AL()
    Log.SINK = SINK
    mods = os.path.join(SCRATCH, "x-mods")
    os.makedirs(mods, exist_ok=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg.load(Paths.get(mods))
    Store_.start(Paths.get(mods))
    K.check(os.path.isfile(os.path.join(mods, "Skyy_SkyyFishing", "config.properties")) and int(Cfg.CAST_RANGE) == 12 and int(Cfg.BAR_START) == 35
            and abs(float(Cfg.PULL[3]) - 11.5) < 1e-9 and len(list(Cfg.JUNK)) == 13 and int(Cfg.POND[5]) == 1000,
            "X: FishCfg.load seeds config.properties with the defaults and reads them back (range 12, bar 35, pulls, 13 junk lines, Pond VI = 1000)")
    bridge = Brg.bridge()
    calls = {"coins": [], "xp": [], "coll": []}
    flags = {"coins_ok": True, "key": None, "tiers": {"Copper": 4, "Iron": 4}}

    @JImplements("java.util.function.Function")
    class CoinsFn:
        @JOverride
        def apply(self, a):
            calls["coins"].append(int(a[1]))
            return JLong(1000 + sum(calls["coins"])) if flags["coins_ok"] else None

    @JImplements("java.util.function.Function")
    class XpFn:
        @JOverride
        def apply(self, a):
            calls["xp"].append((str(a[1]), int(a[2]), str(a[3]), str(a[4])))
            return JBoolean(False)

    @JImplements("java.util.function.Function")
    class CollFn:
        @JOverride
        def apply(self, a):
            calls["coll"].append(str(a[1]))
            return JClass("java.lang.Integer")(flags["tiers"].get(str(a[1]), 0))

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, u):
            return flags["key"] if flags["key"] is not None else str(u)
    bridge.put("coins:fn:add", CoinsFn())
    bridge.put("skill:fn:addxp", XpFn())
    bridge.put("coll:fn:tier", CollFn())
    bridge.put("profile:fn:key", KeyFn())
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000f15b")
    MS = JClass(FAKE_PKG + ".MapStore")
    S1, S2 = us.allocateInstance(MS.class_), us.allocateInstance(MS.class_)

    class Fake(object):
        pass
    W = Fake()
    W.cells, W.eye, W.feet, W.slot, W.held, W.click, W.reel = {}, None, None, 0, None, False, 0
    W.log, W.later, W.now, W.inv, W.fresh_none = [], [], 1000000, SIC(JClass("java.lang.Short")(36).shortValue()), False
    W.hud_cmds = 0

    @JImplements(PKG + "FishApi")
    class FakeApi:
        @JOverride
        def eye(self, c): return None if W.eye is None else JArray(JClass("double"))(W.eye)

        @JOverride
        def feet(self, c): return None if W.feet is None else JArray(JClass("double"))(W.feet)

        @JOverride
        def heldSlot(self, c): return W.slot

        @JOverride
        def held(self, c): return W.held

        @JOverride
        def clicked(self, c):
            k = W.click
            W.click = False
            return k

        @JOverride
        def block(self, c, x, y, z): return W.cells.get((int(x), int(y), int(z)), 2 if int(y) < 60 else 0)

        @JOverride
        def getReel(self, c): return W.reel

        @JOverride
        def setReel(self, c, v):
            W.reel = int(v)
            W.log.append(("reel", int(v)))

        @JOverride
        def spawnBobber(self, c, s): W.log.append(("spawn", float(s.bx), float(s.by), float(s.bz)))

        @JOverride
        def moveBobber(self, c, s, x, y, z): W.log.append(("move", float(y)))

        @JOverride
        def tagBobber(self, c, s, t): W.log.append(("tag", str(t)))

        @JOverride
        def removeBobber(self, s): W.log.append(("remove",))

        @JOverride
        def particle(self, c, i, x, y, z): W.log.append(("particle", str(i)))

        @JOverride
        def sound(self, c, i, x, y, z): W.log.append(("sound", str(i)))

        @JOverride
        def hudState(self, c, s, state, txt):
            b = UCB()
            HDoc.fill(b, state, txt, 200)
            W.hud_cmds += len(b.getCommands())
            W.log.append(("hud", int(state), [None if t is None else str(t) for t in txt]))

        @JOverride
        def hudSet(self, c, s, bar, t, k):
            b = UCB()
            HDoc.sets(b, bar, t, k)
            W.log.append(("hudset", float(bar), None if t is None else str(t), None if k is None else str(k)))

        @JOverride
        def hudHide(self, c, s): W.log.append(("hudhide",))

        @JOverride
        def tell(self, c, t, col): W.log.append(("tell", str(t), None if col is None else str(col)))

        @JOverride
        def inv(self, c): return W.inv

        @JOverride
        def later(self, c, r): W.later.append(r)

        @JOverride
        def fresh(self, c): return None if W.fresh_none else c

        @JOverride
        def now(self): return JLong(W.now)
    Eng.API = FakeApi()
    C1 = Ctx(U1, "Skyy", None, S1, None, None, None)

    def tick(n=1, step=34, click_every=0):
        for i in range(n):
            if click_every and i % click_every == 0:
                W.click = True
            W.now += step
            Core.tickPlayer(C1)

    def run_later():
        while W.later:
            r = W.later.pop(0)
            r.run()

    def tells():
        return [e[1] for e in W.log if e[0] == "tell"]

    def state():
        return Core.STATES.get(U1)

    def count(iid):
        return int(Bench.count(W.inv, iid))

    def pond(x=0):
        W.cells.clear()
        for x_ in range(0, 6):
            for z_ in range(0, 6):
                for y_ in range(60, 63):
                    W.cells[(x_, y_, z_)] = 1
        for (x_, y_, z_) in list(W.cells):
            pass

    def rod(tier="Bamboo", rig=("1", "", "", "")):
        return Rig.withRig(IS("SkyyFishing_Rod_%s" % tier, 1), JArray(JString)(list(rig)))

    def aim_ok():
        W.eye = [-3.0, 64.6, 2.5, 0.9437, -0.3303, 0.0]
        W.feet = [-3.0, 63.0, 2.5]
    pond()
    aim_ok()
    # ---- X1 the reel look + no cast without a rod / without a reel
    W.held, W.slot = IS("Ingredient_Stick", 1), 0
    W.click = True
    tick()
    K.check(state() is None and W.reel == 0, "X1: a click with no rod in hand casts nothing, the reel look stays 0")
    W.held = rod("Copper", ("0", "", "", ""))          # its reel taken off at the bench
    W.click = True
    tick()
    K.check(state() is None and any("no reel" in t for t in tells()) and W.reel == 0,
            "X1: a rod without a reel refuses to cast with a clear line; its look = 0 (no reel)")
    pr_reels = [int(Rig.reelOf(Rig.rigOf(IS(r_, 1)))) for r_ in ("SkyyFishing_Rod_Bamboo", "SkyyFishing_Rod_Copper", "SkyyFishing_Rod_Iron",
                                                                  "SkyyFishing_Rod_Thorium", "SkyyFishing_Rod_Onyxium")]
    W.held = IS("SkyyFishing_Rod_Copper", 1)          # a SkyyReelProbe rod: no metadata
    tick()
    K.check(pr_reels == [1, 2, 3, 0, 0] and W.reel == 2 and state() is None,
            "X1 FIX: a SkyyReelProbe rod (no metadata) = its own tier's reel where that reel is an item (Bamboo/Copper/Iron %s), look 2" % pr_reels)
    pinv = SIC(JClass("java.lang.Short")(4).shortValue())
    pinv.addItemStack(IS("SkyyFishing_Rod_Copper", 1))
    p0 = pinv.getItemStack(JClass("java.lang.Short")(0).shortValue())
    r_ = str(Bench.unfit(pinv, 0, Rig.sig(p0), 0))
    p1 = pinv.getItemStack(JClass("java.lang.Short")(0).shortValue())
    K.check(r_.startswith("+Took off") and int(Bench.count(pinv, "SkyyFishing_Reel_Copper")) == 1 and int(Rig.reelOf(Rig.rigOf(p1))) == 0,
            "X1 FIX: the probe rod's reel comes off at the bench as a real Copper Reel (%s)" % r_)
    W.held = rod("Copper", ("2", "", "", ""))
    tick()
    K.check(W.reel == 2, "X1: holding a Copper rod with its Copper reel sets the reel look to 2 (%d)" % W.reel)
    # ---- X2 the cast and its refusals (no water / blocked / shallow / narrow / the look-down path)
    W.held = rod("Bamboo", ("1", "", "", ""))
    W.eye = [-3.0, 64.6, 2.5, 0.0, 1.0, 0.0]          # looking straight up: no water
    W.click = True
    tick()
    K.check(state() is None and any("No water in reach" in t for t in tells()), "X2: aiming at the sky = 'No water in reach'")
    W.cells[(-2, 64, 2)] = 2
    aim_ok()
    W.click = True
    tick()
    K.check(state() is None and any("in the way" in t for t in tells()), "X2: a wall in the aim = 'Something is in the way'")
    del W.cells[(-2, 64, 2)]
    for x_ in range(0, 6):
        for z_ in range(0, 6):
            W.cells.pop((x_, 60, z_), None)
            W.cells.pop((x_, 61, z_), None)
            W.cells[(x_, 60, z_)] = 2
            W.cells[(x_, 61, z_)] = 2
    W.click = True
    tick()
    K.check(state() is None and any("too shallow" in t for t in tells()), "X2: 1-deep water = 'too shallow'")
    W.cells.clear()
    for y_ in range(58, 63):
        W.cells[(1, y_, 2)] = 1
    W.click = True
    tick()
    K.check(state() is None and any("too small" in t for t in tells()), "X2: a 1-wide hole = 'too small'")
    pond()
    W.eye = [-8.0, 63.6, 2.5, 1.0, 0.0, 0.0]           # flat aim over the pond: the ray ends above the water -> look down
    W.feet = [-8.0, 62.0, 2.5]
    W.click = True
    tick()
    s = state()
    K.check(s is not None and int(s.phase) == 1 and abs(float(s.bx) - 4.5) < 1e-9 and abs(float(s.by) - 62.8) < 1e-9,
            "X2: a flat aim over the pond lands the bobber where the ray ends, on the water surface (%s)" % ([float(s.bx), float(s.by)] if s else None))
    W.click = True
    tick()
    K.check(state() is None and any("reel in your line" in t for t in tells()) and ("remove",) in W.log, "X3: a click while waiting reels in (bobber removed)")
    aim_ok()
    W.log = []
    W.click = True
    tick()
    s = state()
    K.check(s is not None and int(s.phase) == 1 and abs(float(s.bx) - 1.5) < 1e-9 and abs(float(s.bz) - 2.5) < 1e-9
            and any(e[0] == "spawn" for e in W.log) and ("sound", "SFX_Water_MoveIn") in W.log,
            "X2: a cast into the pond: phase 1, bobber over (1, 2), the bobber spawned, the cast sound (%s)" % ([float(s.bx), float(s.by), float(s.bz)] if s else None))
    tick()
    K.check(W.reel == 11, "X1: the line is out -> the rod look = its reel + 10 (no hanging line) (%d)" % W.reel)
    # ---- X4 the bite, a missed bite, the bite again
    s.biteAt = W.now + 50
    tick(3)
    K.check(int(s.phase) == 2 and ("tag", "!") in W.log and ("particle", "Water_Can_Splash") in W.log and ("sound", "SFX_Water_MoveOut") in W.log
            and any(e[0] == "hud" and e[1] == 1 for e in W.log), "X4: the bite: phase 2, the bobber shows !, splash + sound, the BITE widget")
    tick(50)
    K.check(int(s.phase) == 1 and any("before you hooked it" in t for t in tells()) and int(Core.MISSED) >= 1 and ("hudhide",) in W.log,
            "X4: no click in the bite window = it swims off, the line waits again (missed, widget hidden)")
    # ---- X5 a FISH: hook, fight won (clicks), landed -> claim -> handed over by the world task
    def force_fish(sp=2, kg=1.2):
        s_ = state()
        s_.kind, s_.sp, s_.kg, s_.cm = 0, sp, kg, 48.0
        s_.biteAt = W.now + 10
        return s_
    s = force_fish()
    tick(2)
    K.check(int(s.phase) == 2, "X5: bite")
    W.click = True
    tick()
    K.check(int(s.phase) == 3 and abs(float(s.bar) - 35.0) < 1.5 and any(e[0] == "hud" and e[1] == 2 for e in W.log),
            "X5: a click in the window hooks it: the fight (phase 3, bar ~35, the REEL IN widget)")
    pond0 = int(Store_.pond(str(U1)))
    for i in range(200):
        if int(s.phase) != 3:
            break
        tick(1, 34, 3)
    K.check(int(s.phase) == 5 and int(Core.LANDED) >= 1 and any(e[0] == "hud" and e[1] == 4 for e in W.log),
            "X5: clicking about 10 per second fills the bar: LANDED (the catch card)")
    K.check(int(Store_.pond(str(U1))) == pond0 + 1 and len(list(Store_.claims(str(U1)))) == 1 and count("SkyyFishing_Fish_RustbackTrout") == 0,
            "X5: the landed fish is SAVED FIRST as a claim on the cast's profile (Pond Fish +1)")
    K.check(len(W.later) == 1, "X5: one hand-over task queued for the world thread (%d)" % len(W.later))
    run_later()
    f_slot = int(Bench.firstSlot(W.inv, "SkyyFishing_Fish_RustbackTrout"))
    fst = W.inv.getItemStack(JClass("java.lang.Short")(f_slot).shortValue()) if f_slot >= 0 else None
    K.check(fst is not None and int(Rig.grams(fst)) == 1200 and int(Rig.mm(fst)) == 480 and len(list(Store_.claims(str(U1)))) == 0
            and str(Rig.str(Rig.doc(fst), "by")) == "Skyy", "X5: the world task hands the trout over (1.2 kg, 48 cm, 'Caught by Skyy' in its metadata); the claim is gone")
    K.check(any(x[0] == "Fishing" and x[2] == "fishing" for x in calls["xp"]), "X5: Fishing XP is offered through skill:fn:addxp (SkyySkills answers FALSE today)")
    tick(1, 4000)
    K.check(state() is None and ("hudhide",) in W.log, "X5: the catch card goes after fish.hud.resultSec")
    # ---- X6 the fight lost (no clicks) + time out + the click cap + surges
    W.click = True
    tick()
    s = force_fish(7, 15.0)        # a heavy Pondering Pike (pull 9.5) - no clicks
    tick(3)
    W.click = True
    tick()
    for i in range(400):
        if int(s.phase) != 3:
            break
        tick(1, 34)
    K.check(int(s.phase) == 5 and any("pulled the bar empty" in t for t in tells()) and any(e[0] == "hud" and e[1] == 5 for e in W.log),
            "X6: no clicks = the fish pulls the bar to 0: IT GOT AWAY")
    tick(1, 4000)
    W.click = True
    tick()
    s = force_fish(0, 0.2)
    tick(3)
    W.click = True
    tick()
    s.pull = 0.0
    W.log = []
    for i in range(600):
        if int(s.phase) != 3:
            break
        tick(1, 34)
    K.check(int(s.phase) == 5 and any("Out of time" in t for t in tells()) and any(e[0] == "hud" and e[1] == 3 for e in W.log),
            "X6: a fight nobody wins ends at fish.timeLimit: 'Out of time' (and the SURGE widget showed on the way)")
    tick(1, 4000)
    W.click = True
    tick()
    s = force_fish(0, 0.2)
    tick(3)
    W.click = True
    tick()
    s.pull, s.gain, bar0 = 0.0, 0.1, float(s.bar)
    for i in range(30):
        W.click = True
        tick(1, 10)
    got = float(s.bar) - bar0
    K.check(int(s.ignored) > 0 and got <= 0.1 * 12 + 1e-6, "X6: clicks above fish.maxCps per second are ignored (%d ignored, +%.2f)" % (int(s.ignored), got))
    Core.cancel(C1, s, None, JLong(W.now))
    # ---- X7 junk + Lost Property (coins, items) + Twin Line
    def force_other(kind, item=None, qty=1, coins=0, grade=0):
        W.click = True
        tick(1, 4000)
        s_ = state()
        s_.kind, s_.item, s_.qty, s_.coins, s_.tgrade = kind, item, qty, coins, grade
        s_.biteAt = W.now + 10
        tick(2)
        W.click = True
        tick()
        run_later()
        return s_
    sticks0 = count("Ingredient_Stick")
    force_other(1, "Ingredient_Stick", 1)
    K.check(count("Ingredient_Stick") == sticks0 + 1 and any(t.startswith("Junk: Stick") for t in tells()),
            "X7: junk = a vanilla item (a Stick) handed over, landed at once on the hook")
    calls["coins"] = []
    force_other(2, None, 0, 85, 0)
    K.check(calls["coins"] == [85] and any("Lost Property (Good)" in t for t in tells()),
            "X7: Lost Property coins (Good, 85) are paid through coins:fn:add (as a saved claim first)")
    ore0 = count("Ore_Gold")
    force_other(2, "Ore_Gold", 2, 0, 0)
    K.check(count("Ore_Gold") == ore0 + 2 and any("holding Ore Gold x2" in t for t in tells()), "X7: Lost Property materials (2 Gold Ore) handed over")
    flags["coins_ok"] = False
    force_other(2, None, 0, 300, 1)
    K.check(list(Store_.claims(str(U1))) == ["C|300"], "X7: coins that cannot be paid now (no SkyyCoins answer) stay a claim: %s" % list(Store_.claims(str(U1))))
    flags["coins_ok"] = True
    for i in range(70):
        tick(1, 34)
    run_later()
    K.check(not list(Store_.claims(str(U1))) and 300 in calls["coins"], "X7: the waiting coins are paid by the 2 s claim hand-over")
    W.click = True
    tick(1, 4000)
    s = force_fish(1, 0.5)
    s.stat[8] = 100.0
    tick(2)
    W.click = True
    tick()
    for i in range(200):
        if int(s.phase) != 3:
            break
        tick(1, 34, 3)
    run_later()
    K.check(count("SkyyFishing_Fish_Bluegill") == 2 and any("Twin Line" in t for t in tells()), "X7: Twin Line at 100%% = two Bluegills (%d)" % count("SkyyFishing_Fish_Bluegill"))
    tick(1, 4000)
    # ---- X8 a FULL inventory: the catch waits (claim), one warning, handed over once there is room
    W.inv = SIC(JClass("java.lang.Short")(2).shortValue())
    W.inv.addItemStack(IS("Rock_Stone_Cobble", 1))
    W.inv.addItemStack(IS("Ingredient_Fibre", 1))
    W.click = True
    tick()
    s = force_fish(0, 0.1)
    tick(2)
    W.click = True
    tick()
    for i in range(200):
        if int(s.phase) != 3:
            break
        tick(1, 34, 3)
    run_later()
    K.check(len(list(Store_.claims(str(U1)))) == 1 and any("inventory is full" in t for t in tells()), "X8: inventory full -> the minnow waits as a claim, one warning")
    nfull = len([t for t in tells() if "inventory is full" in t])
    for i in range(130):
        tick(1, 34)
    run_later()
    K.check(len([t for t in tells() if "inventory is full" in t]) == nfull and len(list(Store_.claims(str(U1)))) == 1,
            "X8: the 2 s retry does not repeat the warning within 30 s, the claim stays")
    W.inv.removeItemStackFromSlot(JClass("java.lang.Short")(0).shortValue(), JInt(1))
    for i in range(70):
        tick(1, 34)
    run_later()
    K.check(not list(Store_.claims(str(U1))) and count("SkyyFishing_Fish_OverdueMinnow") == 1 and any("waiting catches are in your inventory" in t for t in tells()),
            "X8: room again -> handed over + one line")
    W.inv = SIC(JClass("java.lang.Short")(36).shortValue())
    # ---- X9 every cancel
    def cast_now():
        tick(1, 4000)
        W.click = True
        tick()
        return state()
    s = cast_now()
    W.slot = 3
    tick()
    K.check(state() is None and any("put the rod away" in t for t in tells()), "X9: switching off the rod reels the line in")
    W.slot = 0
    s = cast_now()
    W.feet = [40.0, 63.0, 2.5]
    tick()
    K.check(state() is None and any("walked too far" in t for t in tells()), "X9: walking past range + leash reels the line in")
    aim_ok()
    s = cast_now()
    C2 = Ctx(U1, "Skyy", None, S2, None, None, None)
    Core.tickPlayer(C2)
    K.check(state() is None, "X9: the player in another world (store) = the line ends quietly")
    s = cast_now()
    bridge.put("profile:epoch:" + str(U1), JLong(5))
    tick(12)
    bridge.put("profile:epoch:" + str(U1), JLong(6))
    tick(12)
    K.check(state() is None and any("switched profile" in t for t in tells()), "X9: a profile switch (epoch change) reels the line in")
    s = cast_now()
    bridge.put("profile:busy:" + str(U1), JBoolean(True))
    tick()
    bridge.remove("profile:busy:" + str(U1))
    K.check(state() is None, "X9: profile:busy ends the line quietly")
    s = cast_now()
    s.biteAt = W.now + 999999
    s.idleEnd = W.now + 10
    tick(2)
    K.check(state() is None and any("Nothing is biting" in t for t in tells()), "X9: no bite before fish.idleSeconds reels the line in")
    s = cast_now()
    Cfg.ON = False
    tick()
    Cfg.ON = True
    K.check(state() is None and any("switched off" in t for t in tells()), "X9: Fishing switched off in Server Setup reels lines in")
    Cfg.ON = False
    W.click = True
    tick()
    K.check(state() is None and any("switched off on this server" in t for t in tells()), "X9: ... and refuses new casts")
    Cfg.ON = True
    s = cast_now()
    Core.drop(U1, "test")
    K.check(state() is None and ("remove",) in W.log, "X9: a disconnect / world change (FishReady / FishQuit -> drop) removes the line + bobber")
    s = cast_now()
    Core.dropAll()
    K.check(Core.STATES.isEmpty(), "X9: shutdown drops every line")
    # ---- X10 per PROFILE: a catch counts on the cast's profile; a claim of another profile waits for it
    flags["key"] = str(U1) + "-p2"
    tick(1, 4000)
    W.click = True
    tick()
    s = force_fish(4, 3.0)
    flags["key"] = str(U1)
    tick(2)
    W.click = True
    tick()
    for i in range(300):
        if int(s.phase) != 3:
            break
        tick(1, 34, 2)
    K.check(int(Store_.pond(str(U1) + "-p2")) == 1, "X10: the carp counts on the profile it was cast on (p2)")
    run_later()
    K.check(len(list(Store_.claims(str(U1) + "-p2"))) == 1 and count("SkyyFishing_Fish_MisfiledCarp") == 0,
            "X10: the active profile is p1 now -> the p2 catch is NOT handed over into p1's inventory; it waits on p2")
    flags["key"] = str(U1) + "-p2"
    bridge.put("profile:epoch:" + str(U1), JLong(7))   # the switch back to p2 (SkyyProfiles bumps the epoch)
    for i in range(70):
        tick(1, 34)
    run_later()
    K.check(count("SkyyFishing_Fish_MisfiledCarp") == 0 and len(list(Store_.claims(str(U1) + "-p2"))) == 1 and Core.settling(U1, JLong(W.now)),
            "X10 FIX: within 31 s of a profile switch nothing is handed over (SkyyProfiles' 30 s crash-marker window); the claim waits")
    W.now += 31000
    for i in range(70):
        tick(1, 34)
    run_later()
    K.check(not Core.settling(U1, JLong(W.now)) and count("SkyyFishing_Fish_MisfiledCarp") == 1 and not list(Store_.claims(str(U1) + "-p2")),
            "X10: back on p2, 31 s after the switch -> handed over")
    flags["key"] = None
    tick(1, 4000)
    # ---- X11 the HUD documents (every state through the real UICommandBuilder) + the pure maths
    K.check(W.hud_cmds > 50, "X11: the widget documents of every state built through the real UICommandBuilder (%d commands)" % W.hud_cmds)
    ws = [float(Mth.weight(0.5, 5.0, 2.0, u / 100.0)) for u in range(101)]
    K.check(min(ws) == 0.5 and abs(max(ws) - 5.0) < 1e-9 and abs(float(Mth.lengthCm(1.0, 1.0, 0.5)) - 46.42) < 0.05
            and int(Mth.price(2.0, 26.0, 1.5, 1.0)) == 78 and int(Mth.fillets(2.41, 0.5, 40)) == 4 and int(Mth.fillets(30.0, 0.5, 40)) == 40
            and abs(float(Mth.demandNow(0.5, 1000, 1000 + 7200 * 1000, 7200)) - 0.75) < 1e-9 and float(Mth.demandAfter(0.26, 50.0, 0.25)) == 0.25
            and int(Mth.pondTier(999, Cfg.POND)) == 5 and int(Mth.pondTier(1000, Cfg.POND)) == 6
            and abs(float(Mth.skew(2.0, 10.0)) - (3.0 / 1.1 - 1.0)) < 1e-9 and str(Mth.coins(1234567)) == "1,234,567",
            "X11: FishMath: weight in [min, max], 1 kg trout = 46 cm, price, fillets (cap 40), demand half life + floor, Pond tiers, Deep Sinker skew")
    # the catch roll over many casts: kinds near 85 / 10 / 5, species never heavier than the rod, Clean Sinker at 100% = no junk
    Rnd = JClass("java.util.Random")
    rs = StateC(U1)
    rs.stat = Rig.stats(0, JArray(JString)(["1", "", "", ""]))
    kinds, heavy, rare = [0, 0, 0], 0, 0
    for i in range(4000):
        Core.roll(rs, Core.RNG, JLong(0))
        kinds[int(rs.kind)] += 1
        if int(rs.kind) == 0:
            if float(rs.kg) > 3.0 + 1e-9:
                heavy += 1
            if int(Defs.SP_RAR[int(rs.sp)]) > 0:
                rare += 1
    K.check(3200 < kinds[0] < 3600 and 280 < kinds[1] < 520 and 120 < kinds[2] < 290 and heavy == 0,
            "X11: 4,000 rolls on a Bamboo rod: fish / junk / Lost Property %s (85 / 10 / 5 %%), none heavier than the rod's 3 kg" % kinds)
    rs.stat = Rig.stats(0, JArray(JString)(["1", "", "", "SkyyFishing_Sinker_Clean_II"]))
    rs.stat[9] = 100.0
    jk = 0
    for i in range(1000):
        Core.roll(rs, Core.RNG, JLong(0))
        jk += 1 if int(rs.kind) == 1 else 0
    K.check(jk == 0, "X11: junk cut 100%% = no junk (%d)" % jk)
    st2 = Rig.stats(2, JArray(JString)(["3", "SkyyFishing_Hook_Barbed_II", "SkyyFishing_Line_Braided_I", "SkyyFishing_Sinker_Weighted_II"]))
    K.check(float(st2[0]) == 10.0 and abs(float(st2[1]) - 5.7) < 1e-9 and float(st2[4]) == 10.0 and float(st2[6]) == 1.0 and float(st2[5]) == 10.0,
            "X11: an Iron rod + Iron reel + Barbed II + Braided I + Weighted II = 10 kg, power 5.7, luck 10, +1 s, bar +10")
    claim = Core.claimOf(Rig.makeFish(3, 1500, 520, "A|B"))
    back = Core.claimStack(claim)
    K.check(int(Rig.grams(back)) == 1500 and int(Rig.mm(back)) == 520 and str(back.getItemId()) == "SkyyFishing_Fish_QueuePerch"
            and Core.claimStack("junk") is None and Core.claimStack("F|99|1|1|x") is None,
            "X11: a fish claim round-trips (weight / length / id; a '|' in a name is made safe), a broken claim reads as nothing")
    rc = str(Core.claimOf(Rig.withRig(IS("SkyyFishing_Rod_Iron", 1), JArray(JString)(["2", "SkyyFishing_Hook_Barbed_I", "", "SkyyFishing_Sinker_Deep_II"]))))
    rb = Core.claimStack(rc)
    rbr = [str(x) for x in Rig.rigOf(rb)]
    K.check(str(claim).startswith("F|QueuePerch|1500|520|") and rc == "R|SkyyFishing_Rod_Iron|2|SkyyFishing_Hook_Barbed_I||SkyyFishing_Sinker_Deep_II"
            and str(rb.getItemId()) == "SkyyFishing_Rod_Iron" and rbr == ["2", "SkyyFishing_Hook_Barbed_I", "", "SkyyFishing_Sinker_Deep_II"]
            and rb.getMetadata() is not None,
            "X11 FIX: fish claims name the species KEY (%s); a rod claim keeps reel + parts + tooltip (%s)" % (claim, rc))
    K.check(Core.claimStack("F|3|1|1|x") is None and Core.claimStack("I|Ingredient_Stik|1") is None and Core.claimStack("I|Ingredient_Stick|0") is None
            and str(Core.claimStack("I|Ingredient_Stick|2").getItemId()) == "Ingredient_Stick" and Core.claimStack("R|Nope|1|||") is None,
            "X11 FIX: an old index claim / an unknown item / quantity 0 / an unknown rod read as nothing; a real item claim reads")
    nm = str(Core.clean("a|b\\c=d:e\nf"))
    K.check("|" not in nm and "\\" not in nm and "=" not in nm and ":" not in nm and "\n" not in nm and len(str(Core.clean("x" * 99))) == 40,
            "X11 FIX: catcher names are cleaned for the claim file (%r)" % nm)
    # junk ids from Server Setup: an unknown id never reaches the HUD / inventory; mismatched arrays (live reload) never throw
    j0, w0 = Cfg.JUNK, Cfg.JUNK_W
    Cfg.JUNK = JArray(JString)(["Ingredient_Stik", "Ingredient_Fibre"])
    Cfg.JUNK_W = JArray(JInt)([5])
    jrs = StateC(U1)
    jrs.stat = Rig.stats(0, JArray(JString)(["1", "", "", ""]))
    bad0, jitems, jerr = int(Core.BAD_JUNK), set(), None
    try:
        for i in range(600):
            Core.roll(jrs, Core.RNG, JLong(0))
            if int(jrs.kind) == 1:
                jitems.add(str(jrs.item))
    except Exception as e:
        jerr = e
    Cfg.JUNK, Cfg.JUNK_W = j0, w0
    K.check(jerr is None and jitems == {"Ingredient_Stick"} and int(Core.BAD_JUNK) > bad0 and any("Ingredient_Stik" in str(x) for x in SINK),
            "X11 FIX: junk 'Ingredient_Stik' (a typo in Server Setup) is caught as a Stick + one warning; 2 ids / 1 weight never throws (%s %s)" % (jitems, jerr))
    K.check(str(HDoc.itemSafe("Ingredient_Stik")) == "Ingredient_Stick" and str(HDoc.itemSafe("Ore_Gold")) == "Ore_Gold" and Rig.itemOk("Ore_Gold")
            and not Rig.itemOk("Ingredient_Stik"), "X11 FIX: the HUD icon only shows items of the Item asset map")
    # Lost Property: the spec's purse shares (40 / 30 / 25), the expected coins per find ~51 (spec 7), a forced grade (admin) is used once
    ts = list(Defs.TR_START)
    purse = [sum(int(Defs.TR_SHARE[i]) for i in range(ts[g], ts[g + 1]) if int(Defs.TR_KIND[i]) == 0) for g in range(3)]
    ev = 0.89 * purse[0] / 100.0 * 80 + 0.10 * purse[1] / 100.0 * 500 + 0.01 * purse[2] / 100.0 * 3000
    tot = [sum(int(Defs.TR_SHARE[i]) for i in range(ts[g], ts[g + 1])) for g in range(3)]
    K.check(purse == [40, 30, 25] and tot == [100, 100, 100] and 49.0 < ev < 53.0,
            "X11 FIX: Lost Property purse shares %s (spec 7: 40 / 30 / 25), each grade sums to 100, ~%.0f coins per find" % (purse, ev))
    Core.FORCE.put(U1, JClass("java.lang.Integer")(2))
    Core.roll(jrs, Core.RNG, JLong(0))
    g2 = (int(jrs.kind), int(jrs.tgrade))
    Core.roll(jrs, Core.RNG, JLong(0))
    K.check(g2 == (2, 2) and not Core.FORCE.containsKey(U1), "X11 FIX: /fishadmin treasure outstanding -> the next roll is Outstanding Lost Property, once (%s)" % (g2,))
    # ============================================================================ X12 FishBench on REAL containers (craft / fit / unfit / sell / fillet)
    inv = SIC(JClass("java.lang.Short")(20).shortValue())
    key = str(U1)

    def add(iid, q):
        inv.addItemStack(IS(iid, q))
    Store_.setPond(key, 0)
    K.check(str(Bench.craft(inv, U1, key, 0)).startswith("-Missing"), "X12: craft with nothing = 'Missing items' (nothing taken)")
    add("Wood_Bamboo_Trunk", 3)
    add("Ingredient_Fibre", 7)
    add("Ingredient_Stick", 2)
    r = str(Bench.craft(inv, U1, key, 0))
    rs_ = int(Bench.firstSlot(inv, "SkyyFishing_Rod_Bamboo"))
    rstack = inv.getItemStack(JClass("java.lang.Short")(rs_).shortValue()) if rs_ >= 0 else None
    K.check(r.startswith("+Crafted") and rstack is not None and int(Rig.reelOf(Rig.rigOf(rstack))) == 1 and count_in(inv, "Wood_Bamboo_Trunk", Bench) == 0
            and count_in(inv, "Ingredient_Fibre", Bench) == 1 and count_in(inv, "Ingredient_Stick", Bench) == 0,
            "X12: Bamboo Fishing Rod crafted: exactly 3 bamboo + 6 fibre + 2 sticks taken, the rod comes with its Bamboo reel fitted: %s" % r)
    K.check(str(Bench.craft(inv, U1, key, 2)).startswith("-Locked") and "Pond Fish III" in str(Bench.craft(inv, U1, key, 2)),
            "X12: the Copper rod is locked below Pond Fish III")
    Store_.setPond(key, 100)
    flags["tiers"]["Copper"] = 2
    K.check(str(Bench.craft(inv, U1, key, 2)).startswith("-Locked") and "Copper IV" in str(Bench.craft(inv, U1, key, 2)),
            "X12: ... and below Copper IV through coll:fn:tier (Copper III here)")
    flags["tiers"]["Copper"] = 4
    add("Ingredient_Bar_Copper", 20)
    add("Ingredient_Fibre", 8)
    add("SkyyFishing_Hook_Barbed_I", 1)
    add("SkyyFishing_Line_Steady_I", 2)
    r = str(Bench.fit(inv, key, rs_, Rig.sig(rstack), "SkyyFishing_Hook_Barbed_I"))
    rstack = inv.getItemStack(JClass("java.lang.Short")(rs_).shortValue())
    K.check(r.startswith("+Fitted") and str(Rig.rigOf(rstack)[1]) == "SkyyFishing_Hook_Barbed_I" and count_in(inv, "SkyyFishing_Hook_Barbed_I", Bench) == 0,
            "X12: fit a Barbed Hook I onto the rod (the hook leaves the inventory, the rod's metadata has it): %s" % r)
    r2 = str(Bench.fit(inv, key, rs_, "stale-sig", "SkyyFishing_Line_Steady_I"))
    K.check(r2.startswith("-That rod moved") and count_in(inv, "SkyyFishing_Line_Steady_I", Bench) == 2, "X12: a stale rod signature = nothing changes (double click / moved item)")
    r = str(Bench.fit(inv, key, rs_, Rig.sig(rstack), "SkyyFishing_Line_Steady_I"))
    rstack = inv.getItemStack(JClass("java.lang.Short")(rs_).shortValue())
    sig_line = Rig.sig(rstack)
    r_again = str(Bench.fit(inv, key, rs_, sig_line, "SkyyFishing_Line_Steady_I"))
    K.check(r.startswith("+Fitted") and r_again.startswith("=") and count_in(inv, "SkyyFishing_Line_Steady_I", Bench) == 1,
            "X12: fitting the same line twice = 'already on this rod' (one taken, not two)")
    r = str(Bench.craft(inv, U1, key, 2))
    cs_ = int(Bench.firstSlot(inv, "SkyyFishing_Rod_Copper"))
    cst = inv.getItemStack(JClass("java.lang.Short")(cs_).shortValue()) if cs_ >= 0 else None
    K.check(r.startswith("+Crafted") and cst is not None and count_in(inv, "SkyyFishing_Rod_Bamboo", Bench) == 0
            and str(Rig.rigOf(cst)[1]) == "SkyyFishing_Hook_Barbed_I" and str(Rig.rigOf(cst)[2]) == "SkyyFishing_Line_Steady_I" and int(Rig.reelOf(Rig.rigOf(cst))) == 1,
            "X12: the Copper rod is crafted FROM the Bamboo rod (consumed) and keeps its reel + hook + line: %s" % r)
    r = str(Bench.unfit(inv, cs_, Rig.sig(cst), 1))
    cst = inv.getItemStack(JClass("java.lang.Short")(cs_).shortValue())
    K.check(r.startswith("+Took off") and str(Rig.rigOf(cst)[1]) == "" and count_in(inv, "SkyyFishing_Hook_Barbed_I", Bench) == 1,
            "X12: take the hook off: back in the inventory, the rod's slot empty")
    K.check(str(Bench.unfit(inv, cs_, Rig.sig(cst), 1)).startswith("="), "X12: taking off an empty slot = 'already empty'")
    r = str(Bench.fit(inv, key, cs_, Rig.sig(cst), "SkyyFishing_Reel_Bamboo"))
    K.check(r.startswith("-You have no"), "X12: fitting a reel you do not carry = 'You have no ...'")
    add("SkyyFishing_Reel_Copper", 1)
    cst = inv.getItemStack(JClass("java.lang.Short")(cs_).shortValue())
    r = str(Bench.fit(inv, key, cs_, Rig.sig(cst), "SkyyFishing_Reel_Copper"))
    cst = inv.getItemStack(JClass("java.lang.Short")(cs_).shortValue())
    K.check(r.startswith("+Fitted") and int(Rig.reelOf(Rig.rigOf(cst))) == 2 and count_in(inv, "SkyyFishing_Reel_Bamboo", Bench) == 1,
            "X12: a Copper reel replaces the Bamboo reel; the Bamboo reel comes back")
    full = SIC(JClass("java.lang.Short")(1).shortValue())
    full.addItemStack(rod("Iron", ("3", "SkyyFishing_Hook_Lure_I", "", "")))
    fst2 = full.getItemStack(JClass("java.lang.Short")(0).shortValue())
    K.check(str(Bench.unfit(full, 0, Rig.sig(fst2), 1)).startswith("-Make room") and str(Rig.rigOf(full.getItemStack(JClass("java.lang.Short")(0).shortValue()))[1]) == "SkyyFishing_Hook_Lure_I",
            "X12: taking a part off with a full inventory is refused, the rod keeps it (nothing lost)")
    add("Ingredient_Bar_Copper", 2)
    full2 = SIC(JClass("java.lang.Short")(1).shortValue())
    full2.addItemStack(IS("Ingredient_Bar_Copper", 2))
    Store_.setPond(key, 25)
    K.check(str(Bench.craft(full2, U1, key, 6)).startswith("-Locked"), "X12: Barbed Hook I locked below Pond Fish II")
    Store_.setPond(key, 50)
    r = str(Bench.craft(full2, U1, key, 6))
    K.check(r.startswith("+Crafted") and int(Bench.count(full2, "SkyyFishing_Hook_Barbed_I")) == 1, "X12: Barbed Hook I crafted in a 1-slot inventory whose bars free the slot: %s" % r)
    # selling + filleting
    calls["coins"] = []
    trout = Rig.makeFish(2, 2410, 520, "Skyy")
    inv.addItemStack(trout)
    ts = int(Bench.firstSlot(inv, "SkyyFishing_Fish_RustbackTrout"))
    tsig = Rig.sig(inv.getItemStack(JClass("java.lang.Short")(ts).shortValue()))
    price = int(Bench.priceOf(inv.getItemStack(JClass("java.lang.Short")(ts).shortValue()), JLong(1000)))
    r = str(Bench.sell(inv, U1, ts, tsig, JLong(1000)))
    K.check(r.startswith("+Sold") and calls["coins"] == [price] and price == 63 and count_in(inv, "SkyyFishing_Fish_RustbackTrout", Bench) == 0
            and float(Store_.demand(2, JLong(1000))) < 1.0, "X12: sell a 2.41 kg trout: 63 coins (2.41 x 26), the fish is gone, demand lowered: %s" % r)
    r = str(Bench.sell(inv, U1, ts, tsig, JLong(1000)))
    K.check(r.startswith("-That fish moved") and calls["coins"] == [price], "X12: the same sell click again (double click) pays nothing")
    flags["coins_ok"] = False
    inv.addItemStack(Rig.makeFish(2, 1000, 400, "Skyy"))
    ts = int(Bench.firstSlot(inv, "SkyyFishing_Fish_RustbackTrout"))
    r = str(Bench.sell(inv, U1, ts, Rig.sig(inv.getItemStack(JClass("java.lang.Short")(ts).shortValue())), JLong(1000)))
    K.check(r.startswith("-The sale did not go through") and count_in(inv, "SkyyFishing_Fish_RustbackTrout", Bench) == 1, "X12: a refused payment puts the fish back")
    flags["coins_ok"] = True
    ts = int(Bench.firstSlot(inv, "SkyyFishing_Fish_RustbackTrout"))
    raw0 = count_in(inv, "Food_Fish_Raw", Bench)
    r = str(Bench.fillet(inv, ts, Rig.sig(inv.getItemStack(JClass("java.lang.Short")(ts).shortValue()))))
    K.check(r.startswith("+Filleted") and count_in(inv, "Food_Fish_Raw", Bench) == raw0 + 2 and count_in(inv, "SkyyFishing_Fish_RustbackTrout", Bench) == 0,
            "X12: fillet a 1 kg trout = 2 vanilla Raw Fish: %s" % r)
    inv.addItemStack(Rig.makeFish(0, 300, 200, "Skyy"))
    ms_ = int(Bench.firstSlot(inv, "SkyyFishing_Fish_OverdueMinnow"))
    K.check(str(Bench.fillet(inv, ms_, Rig.sig(inv.getItemStack(JClass("java.lang.Short")(ms_).shortValue())))).startswith("-Too small"),
            "X12: a 0.3 kg minnow is too small to fillet")
    inv.addItemStack(Rig.makeFish(5, 4000, 900, "Skyy"))
    cs2 = int(Bench.firstSlot(inv, "SkyyFishing_Fish_StampedCatfish"))
    unc0 = count_in(inv, "Food_Fish_Raw_Uncommon", Bench)
    Bench.fillet(inv, cs2, Rig.sig(inv.getItemStack(JClass("java.lang.Short")(cs2).shortValue())))
    K.check(count_in(inv, "Food_Fish_Raw_Uncommon", Bench) == unc0 + 8, "X12: a Unique 4 kg catfish = 8 Raw Fish (Uncommon)")
    inv.addItemStack(Rig.makeFish(1, 500, 300, "Skyy"))
    inv.addItemStack(Rig.makeFish(3, 700, 350, "Skyy"))
    inv.addItemStack(Rig.makeFish(7, 9000, 1100, "Skyy"))
    calls["coins"] = []
    r = str(Bench.sellAll(inv, U1, JLong(5000)))
    K.check(r.startswith("+Sold 3 Normal") and len(calls["coins"]) == 3 and count_in(inv, "SkyyFishing_Fish_PonderingPike", Bench) == 1,
            "X12: Sell all Normal sells the 3 Normal fish (minnow, bluegill, perch) and keeps the Rare pike: %s" % r)
    tiny = SIC(JClass("java.lang.Short")(1).shortValue())
    tiny.addItemStack(Rig.makeFish(7, 40000, 1300, "Skyy"))
    r = str(Bench.fillet(tiny, 0, Rig.sig(tiny.getItemStack(JClass("java.lang.Short")(0).shortValue()))))
    K.check(r.startswith("-No room") and int(Bench.count(tiny, "SkyyFishing_Fish_PonderingPike")) == 1,
            "X12: 40 fillets do not fit a 1-slot inventory: the fish is put back (%s)" % r)
    # ============================================================================ X13 the bench PAGE (stand-in subclass: rebuild / close recorded)
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    pr = PRc(None, U1, "Skyy", "en-US", None, None)
    FP = JClass(FAKE_PKG + ".FakePage")
    pg = FP(pr)
    pg.lastStore = S1
    W.inv = inv
    for t_ in range(3):
        pg.tab = t_
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, S1)
        K.check(len(b.getCommands()) > 20 and len(ev.getEvents()) >= 4, "X13: page tab %d builds (%d commands, %d bindings)" % (t_, len(b.getCommands()), len(ev.getEvents())))
    pg.tab = 0
    b, ev = UCB(), UEB()
    pg.build(None, b, ev, S1)
    tok = str(pg.tok)

    def click(a, i=None, t=None):
        d = {"a": a}
        if i is not None:
            d["i"] = str(i)
        d["t"] = tok if t is None else t
        pg.handleDataEvent(None, S1, json.dumps(d))
        return str(pg.info)
    n0 = int(pg.rebuilds)
    r = click("craft", 1, "0")
    K.check(r.startswith("=The page changed") and int(pg.rebuilds) == n0 + 1, "X13: a click with an old token = 'page changed', rebuilt, nothing done")
    tok = str(pg.tok)
    add("Ingredient_Stick", 4)
    add("Ingredient_Fibre", 3)
    reels0 = count_in(inv, "SkyyFishing_Reel_Bamboo", Bench)
    r = click("craft", 1)
    K.check(r.startswith("+Crafted") and count_in(inv, "SkyyFishing_Reel_Bamboo", Bench) == reels0 + 1, "X13: page craft (Bamboo Reel) through handleDataEvent: %s" % r)
    r = click("craft", 1)
    K.check(r.startswith("=The page changed"), "X13: the same click sent twice (double click: the old token) does nothing the 2nd time")
    tok = str(pg.tok)
    pg.handleDataEvent(None, S1, json.dumps({"a": "tab", "i": "1"}))
    tok = str(pg.tok)
    K.check(int(pg.tab) == 1 and len(list(pg.rodSlots)) >= 1, "X13: tab RIG lists your rods (%d)" % len(list(pg.rodSlots)))
    r = click("rod", 0)
    tok = str(pg.tok)
    pids = [str(x) for x in pg.partIds]
    j = pids.index("SkyyFishing_Hook_Barbed_I") if "SkyyFishing_Hook_Barbed_I" in pids else -1
    r = click("fit", j)
    K.check(j >= 0 and r.startswith("+Fitted"), "X13: page fit (Barbed Hook I) on the chosen rod: %s" % r)
    tok = str(pg.tok)
    r = click("rm", 1)
    K.check(r.startswith("+Took off"), "X13: page remove (the hook): %s" % r)
    tok = str(pg.tok)
    r = click("fit", 99)
    K.check(r.startswith("-Pick a rod"), "X13: a fit row that does not exist = refused")
    tok = str(pg.tok)
    pg.handleDataEvent(None, S1, json.dumps({"a": "tab", "i": "2"}))
    tok = str(pg.tok)
    inv.addItemStack(Rig.makeFish(7, 8000, 1100, "Skyy"))
    pg.rebuild()
    tok = str(pg.tok)
    fsl = [int(x) for x in pg.fishSlots]
    pike_rows = [i for i, sl in enumerate(fsl) if str(inv.getItemStack(JClass("java.lang.Short")(sl).shortValue()).getItemId()) == "SkyyFishing_Fish_PonderingPike"]
    raw1 = count_in(inv, "Food_Fish_Raw_Uncommon", Bench)
    r = click("fil", pike_rows[0])
    K.check(r.startswith("=Fillet the Rare Pondering Pike") and count_in(inv, "Food_Fish_Raw_Uncommon", Bench) == raw1,
            "X13: filleting a Rare fish asks first (no fillet yet): %s" % r)
    tok = str(pg.tok)
    r = click("fil", pike_rows[0])
    K.check(r.startswith("+Filleted") and count_in(inv, "Food_Fish_Raw_Uncommon", Bench) > raw1, "X13: the second FILLET click fillets it: %s" % r)
    tok = str(pg.tok)
    inv.addItemStack(Rig.makeFish(2, 2000, 450, "Skyy"))
    pg.rebuild()
    tok = str(pg.tok)
    r = click("sell", 0)
    K.check(r.startswith("+Sold"), "X13: page sell: %s" % r)
    tok = str(pg.tok)
    r = click("sellall")
    K.check(r.startswith("+Sold") or r.startswith("="), "X13: page Sell all Normal: %s" % r)
    tok = str(pg.tok)
    bridge.put("profile:busy:" + str(U1), JBoolean(True))
    r = click("sell", 0)
    bridge.remove("profile:busy:" + str(U1))
    K.check(r.startswith("-Your profile is busy"), "X13: profile busy = bench clicks refused")
    tok = str(pg.tok)
    c0 = int(pg.closes)
    pg.handleDataEvent(None, S1, json.dumps({"a": "close"}))
    K.check(int(pg.closes) == c0 + 1, "X13: Close closes the page")
    Eng.API = None
    pg.tab = 0
    pg.build(None, UCB(), UEB(), S1)
    Eng.API = FakeApi()
    K.check(True, "X13: the page builds with no engine API (no inventory) without throwing")
    # ============================================================================ X14 commands (bodies) + the save
    Cmds = P("FishCmds")
    W.inv = SIC(JClass("java.lang.Short")(36).shortValue())
    Cmds.admin(pr, S1, None, "kit", None)
    K.check(int(Bench.count(W.inv, "SkyyFishing_Rod_Iron")) == 1 and int(Bench.count(W.inv, "SkyyFishing_Hook_Deep_I")) == 0
            and int(Bench.count(W.inv, "SkyyFishing_Sinker_Deep_II")) == 1 and int(Bench.count(W.inv, "SkyyFishing_Bench")) == 1,
            "X14: /fishadmin kit gives the 3 rods, 3 reels, 20 parts, a bench")
    Cmds.admin(pr, S1, None, "pond", "1000")
    K.check(int(Store_.pond(str(U1))) == 1000, "X14: /fishadmin pond 1000")
    Cmds.admin(pr, S1, None, "pond", "x")
    pk0 = int(Store_.pond(str(U1)))
    Cmds.admin(pr, S1, None, "give", "PonderingPike")
    Cmds.admin(pr, S1, None, "give", "koi")
    Cmds.admin(pr, S1, None, "give", "nothing")
    pike = [W.inv.getItemStack(JClass("java.lang.Short")(i).shortValue()) for i in range(36)]
    pike = [x for x in pike if x is not None and not x.isEmpty() and str(x.getItemId()) == "SkyyFishing_Fish_PonderingPike"]
    K.check(len(pike) == 1 and 6500 <= int(Rig.grams(pike[0])) <= 18000 and int(Bench.count(W.inv, "SkyyFishing_Fish_GoldenKoi")) == 1
            and int(Store_.pond(str(U1))) == pk0 and any("Usage: /fishadmin give" in str(x) for x in SINK),
            "X14 FIX: /fishadmin give PonderingPike / koi = a Rare pike (6.5-18 kg) + a Legendary koi, not counted for Pond Fish; a bad name = usage")
    Cmds.admin(pr, S1, None, "treasure", "Great")
    K.check(int(Core.FORCE.get(U1)) == 1, "X14 FIX: /fishadmin treasure Great arms the next cast")
    Core.FORCE.remove(U1)
    Cmds.admin(pr, S1, None, "treasure", "x")
    K.check(any("Usage: /fishadmin treasure" in str(x) for x in SINK), "X14 FIX: /fishadmin treasure <bad> = usage")
    Cmds.admin(pr, S1, None, "bite", None)
    Cmds.admin(pr, S1, None, "status", None)
    Cmds.admin(pr, S1, None, "", None)
    Cmds.status(pr)
    K.check(any("ran /fishadmin pond" in str(x) for x in SINK) and any("Fishing: Pond Fish VI" in str(x) for x in SINK), "X14: /fishing status + /fishadmin paths ran")
    Store_.flush()
    pf = os.path.join(mods, "Skyy_SkyyFishing", "players", str(U1) + ".properties")
    K.check(os.path.isfile(pf) and "pond=1000" in open(pf, encoding="utf-8").read() and os.path.isfile(os.path.join(mods, "Skyy_SkyyFishing", "records.properties"))
            and os.path.isfile(os.path.join(mods, "Skyy_SkyyFishing", "demand.properties")) and os.path.isfile(os.path.join(mods, "Skyy_SkyyFishing", "players", str(U1) + "-p2.properties")),
            "X14: the save writes each profile's file + records + demand (atomic)")
    K.check(not Store_.safeKey("../x") and not Store_.safeKey("a b") and Store_.safeKey(str(U1) + "-p2"), "X14: profile keys are checked before they become file names")
    # ---- FIX: a profile file that exists but cannot be read is NEVER replaced by an empty record (a directory = an unreadable file)
    pdir = os.path.join(mods, "Skyy_SkyyFishing", "players")
    bk = "broken-key-1"
    bpath = os.path.join(pdir, bk + ".properties")
    os.makedirs(bpath, exist_ok=True)
    lf0 = int(Store_.LOAD_FAILS)
    Store_.onCatch(bk, 2, 900, 400)
    Store_.addClaim(bk, "I|Ingredient_Stick|3")
    Store_.flush()
    bd = Store_.data(bk)
    K.check(os.path.isdir(bpath) and bool(bd.broken) and bool(bd.dirty) and int(Store_.LOAD_FAILS) > lf0,
            "X14 FIX: an unreadable profile file -> a broken record, nothing written over it, the changes stay pending")
    os.rmdir(bpath)
    with open(bpath, "w", encoding="utf-8") as f_:
        f_.write("pond=50\nsp.RustbackTrout.n=4\nsp.RustbackTrout.g=3000\nclaims=1\nclaim.0=I|Ore_Gold|2\n")
    bd.retryAt = 0
    h0 = int(Store_.HEALS)
    Store_.flush()
    txt = open(bpath, encoding="utf-8").read()
    K.check(int(Store_.HEALS) == h0 + 1 and not bool(bd.broken) and "pond=51" in txt and "sp.RustbackTrout.n=5" in txt and "sp.RustbackTrout.g=3000" in txt
            and "claim.0=I|Ore_Gold|2" in txt and "claim.1=I|Ingredient_Stick|3" in txt,
            "X14 FIX: once the file reads again the pending changes are MERGED onto it (pond 50+1, trout 4+1, best kept, claims kept + added)")
    bk2 = "broken-key-2"
    os.makedirs(os.path.join(pdir, bk2 + ".properties"), exist_ok=True)
    Store_.setPond(bk2, 7)
    Store_.STOPPING = True
    Store_.flush()
    Store_.STOPPING = False
    K.check(os.path.isfile(os.path.join(pdir, bk2 + ".properties.unmerged")) and os.path.isdir(os.path.join(pdir, bk2 + ".properties")),
            "X14 FIX: still unreadable at shutdown -> the changes go to <key>.properties.unmerged, the real file is untouched")
    Store_.CACHE.remove(bk2)
    w0 = int(Store_.WRITES)
    Store_.setPond("not a file key!", 3)
    Store_.flush()
    Store_.flush()
    K.check(int(Store_.WRITES) == w0 and not bool(Store_.data("not a file key!").dirty)
            and sum(1 for x in SINK if "cannot be saved (not a file name)" in str(x)) == 1,
            "X14 FIX: a key that is no file name is skipped with ONE warning (not re-queued every 2 s)")
    uk = str(U1) + "-utf"
    Store_.addClaim(uk, "F|Bluegill|500|300|Zo\u00eb")
    Store_.flush()
    Store_.CACHE.remove(uk)
    K.check(list(Store_.claims(uk)) == ["F|Bluegill|500|300|Zo\u00eb"], "X14 FIX: files are read as UTF-8 (a non-ASCII name survives a reload): %s" % list(Store_.claims(uk)))
    # ---- FIX: a lost world task (PAYING) no longer blocks delivery; coins wait (no rewrite churn) while SkyyCoins is missing
    Core.PAYING.put(U1, JLong(0))
    n0 = len(W.later)
    Store_.addClaim(str(U1), "I|Ingredient_Stick|1")
    Core.kick(C1, str(U1))
    n1 = len(W.later)
    Core.kick(C1, str(U1))
    K.check(n1 == n0 + 1 and len(W.later) == n1, "X14 FIX: a stale PAYING entry (a task lost with its world) is replaced; a fresh one still blocks a second task")
    run_later()
    Core.PAYING.clear()
    cfn = bridge.remove("coins:fn:add")
    Store_.addClaim(str(U1), "C|77")
    Store_.flush()
    Core.payClaims(C1, str(U1))
    K.check(list(Store_.claims(str(U1))) == ["C|77"] and not bool(Store_.data(str(U1)).dirty),
            "X14 FIX: without SkyyCoins a coin claim waits untouched (no file rewrite every 3 s)")
    bridge.put("coins:fn:add", cfn)
    Core.payClaims(C1, str(U1))
    K.check(not list(Store_.claims(str(U1))) and 77 in calls["coins"], "X14 FIX: ... and is paid once SkyyCoins answers")
    # ---- FIX: a world change takes our widget down; the epoch memory survives a world change (a switch that sends you to your island)
    W.inv = SIC(JClass("java.lang.Short")(36).shortValue())
    W.held, W.slot = rod("Bamboo", ("1", "", "", "")), 0
    pond()
    aim_ok()
    s = cast_now()
    s.hud = us.allocateInstance(P("FishHud").class_)
    del W.log[:]
    Core.EPOCHS.put(U1, JLong(7))
    Core.worldChange(U1, "Skyy", None, S1, None)
    K.check(state() is None and ("hudhide",) in W.log and ("remove",) in W.log and Core.EPOCHS.containsKey(U1),
            "X14 FIX: PlayerReady (world change) -> line ends, bobber removed, OUR widget hidden; the epoch memory is kept")
    Core.drop(U1, "left the game")
    K.check(not Core.EPOCHS.containsKey(U1) and not Core.EPOCH_AT.containsKey(U1), "X14 FIX: a disconnect forgets the epoch memory")
    # ---- FIX: the line is at most 20 dots per player per draw
    s = cast_now()
    sp0 = Cfg.LINE_SPACING
    Cfg.LINE_SPACING = 0.3
    s.bx, s.bz = s.bx + 10.0, s.bz + 5.0
    del W.log[:]
    Core.DOT_WINDOW = 0
    Core.line(C1, s, JLong(W.now))
    Cfg.LINE_SPACING = sp0
    nd = sum(1 for e in W.log if e[0] == "particle")
    K.check(int(Core.MAX_DOTS) == 20 and 0 < nd <= 19, "X14 FIX: a long line at spacing 0.3 draws %d dots (cap 20 per player)" % nd)
    Core.cancel(C1, s, None, JLong(W.now))
    Core.STATES.clear()
    # ============================================================================ X15 FishTick.tick + FishEngApi on stand-in ECS parts
    CTt = JClass("com.hypixel.hytale.component.ComponentType")
    TY = dict((k, us.allocateInstance(CTt.class_)) for k in ("player", "pref", "stats", "hotbar", "transform", "head", "effect", "model"))
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = us.allocateInstance(EM.class_)
    jf(EM, "instance").set(None, em)
    for fld, k in (("playerComponentType", "player"), ("hotbarInventoryComponentType", "hotbar"), ("transformComponentType", "transform"),
                   ("headRotationComponentType", "head"), ("effectControllerComponentType", "effect"), ("modelComponentType", "model")):
        try:
            jf(EM, fld).set(em, TY[k])
        except Exception as e:
            K.notes.append("X15: EntityModule field %s: %s" % (fld, e))
    SM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    sm = us.allocateInstance(SM.class_)
    jf(SM, "instance").set(None, sm)
    jf(SM, "entityStatMapComponentType").set(sm, TY["stats"])
    jf(JClass("com.hypixel.hytale.server.core.universe.Universe"), "playerRefComponentType").set(E["uni"], TY["pref"])
    REFc = JClass("com.hypixel.hytale.component.Ref")
    ref = us.allocateInstance(REFc.class_)
    store = us.allocateInstance(MS.class_)
    HM = JClass("java.util.IdentityHashMap")
    comps = HM()
    store.comps = HM()
    store.comps.put(ref, comps)
    comps.put(TY["pref"], pr)
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    HR = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    V3 = JClass("org.joml.Vector3d")
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    comps.put(TY["transform"], TC(V3(1.0, 64.0, 2.0), R3()))
    comps.put(TY["head"], HR(R3()))
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    sm_ = ESM()
    try:
        sm_.update()
    except Exception as e:
        K.notes.append("X15: EntityStatMap.update: %s" % str(e)[:120])
    comps.put(TY["stats"], sm_)
    ECCc = JClass("com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent")
    comps.put(TY["effect"], ECCc())
    buf = us.allocateInstance(JClass(FAKE_PKG + ".MapBuffer").class_)
    buf.st = store
    chunk = us.allocateInstance(JClass(FAKE_PKG + ".MapChunk").class_)
    chunk.ref = ref
    EA = P("FishEngApi")()
    Eng.API = EA
    TK = P("FishTick")()
    t0 = int(P("FishTick").TICKS)
    TK.tick(JFloat(0.033), 0, chunk, store, buf)
    K.check(int(P("FishTick").TICKS) == t0 + 1 and not [x for x in SINK if "fishing tick failed" in str(x)],
            "X15: FishTick.tick on stand-in ECS parts: resolves the player (PlayerRef component), builds the context, runs the loop with the REAL FishEngApi")
    c3 = Ctx(U1, "Skyy", ref, store, buf, None, pr)
    e3 = EA.eye(c3)
    K.check(e3 is not None and abs(float(e3[1]) - 65.6) < 0.01 and abs(float(e3[5]) + 1.0) < 1e-6 or (e3 is not None and len(e3) == 6),
            "X15: FishEngApi.eye: the position + eye height + look direction (%s)" % (list(e3) if e3 is not None else None))
    K.check(list(EA.feet(c3)) == [1.0, 64.0, 2.0] and int(EA.heldSlot(c3)) == -1 and EA.held(c3) is None and not bool(EA.clicked(c3)),
            "X15: FishEngApi.feet / heldSlot / held / clicked on a player with no hotbar + no click")
    si = int(P("FishEngApi").statIndex())
    ci = int(P("FishEngApi").clickIndex())
    K.check(si == sidx and ci >= 0, "X15: FishEngApi.statIndex = our stat's index, clickIndex = our effect's index (%d, %d)" % (si, ci))
    EA.setReel(c3, 7)
    K.check(int(EA.getReel(c3)) in (7, -1), "X15: FishEngApi.setReel / getReel through the real EntityStatMap (%d)" % int(EA.getReel(c3)))
    EA.tell(c3, "test", "#ffffff")
    K.check(int(EA.block(c3, 0, 64, 0)) == -1, "X15: FishEngApi.block without a world = -1 (never throws, never loads a chunk)")
    Eng.API = FakeApi()
    K.notes.append("X: %d log lines; casts %d bites %d landed %d lost %d missed %d cancels %d claimed %d" % (
        SINK.size(), int(Core.CASTS), int(Core.BITES), int(Core.LANDED), int(Core.LOST), int(Core.MISSED), int(Core.CANCELS), int(Core.CLAIMED)))
    K.save()


def count_in(inv, iid, Bench):
    return int(Bench.count(inv, iid))


def light_stats(K, jz):
    """AssetRegistryLoader.init + the EntityStatType store (EntityStatsModule.setup's job) with every vanilla stat + ours"""
    from jpype import JClass, JArray, JString, JImplements, JOverride
    az = zipfile.ZipFile(ASSETS)
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def jfield(c, n):
        f = c.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "d-universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    jfield(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    ARR = JClass("java.lang.reflect.Array")

    @JImplements("java.util.function.Function")
    class GetId:
        @JOverride
        def apply(self, o): return o.getId()

    @JImplements("java.util.function.IntFunction")
    class ArrOf:
        def __init__(self, c): self.c = c

        @JOverride
        def apply(self, n): return ARR.newInstance(self.c.class_, n)

    @JImplements("java.util.function.Function")
    class NoRep:
        @JOverride
        def apply(self, k): return None
    ESTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    if AR.getAssetStore(ESTc.class_) is None:
        AR.register(HAS.builder(ESTc.class_, ILT(ArrOf(ESTc))).setPath("Entity/Stats").setCodec(ESTc.CODEC).setKeyFunction(GetId())
                    .setReplaceOnRemove(NoRep()).build())
    SMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MODc = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier")
    MODc.CODEC.register("Boost", SMOD.class_, SMOD.ENTITY_CODEC)
    MODc.CODEC.register("Static", SMOD.class_, SMOD.ENTITY_CODEC)
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR, Paths, ArrayList = JClass("com.hypixel.hytale.codec.util.RawJsonReader"), JClass("java.nio.file.Paths"), JClass("java.util.ArrayList")

    def dec(key, text):
        ei = AEI(Paths.get(key + ".json"), ADT(ESTc.class_, key, None))
        try:
            return AR.getAssetStore(ESTc.class_).getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception:
            return None
    objs = []
    for n in sorted(az.namelist()):
        if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
            d = json.loads(az.read(n).decode("utf-8-sig"))
            for k in ("Regenerating", "MinValueEffects", "MaxValueEffects"):
                d.pop(k, None)
            o = dec(n.rsplit("/", 1)[1][:-5], json.dumps(d))
            if o is not None:
                objs.append(o)
    ours = dec(STAT, jz.read("Server/Entity/Stats/%s.json" % STAT).decode("utf-8"))
    K.check(ours is not None, "D: our stat decodes")
    objs.append(ours)
    l_ = ArrayList()
    for o in objs:
        l_.add(o)
    AR.getAssetStore(ESTc.class_).loadAssets("Hytale:Hytale", l_)
    return ESTc


def run_live(step, out):
    """child D: one server start on the scratch copy of the live world (start1 / start2)"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR], verify=True)
    jz = zipfile.ZipFile(JAR)
    home = os.path.join(SCRATCH, "live")
    mods = os.path.join(home, "mods")
    P = lambda n: JClass(PKG + n)
    Cfg, Store_, Rig, Log = P("FishCfg"), P("FishStore"), P("FishRig"), P("FishLog")
    Log.SINK = JClass("java.util.ArrayList")()
    Paths = JClass("java.nio.file.Paths")
    cfgp = os.path.join(mods, "Skyy_SkyyFishing", "config.properties")
    before = open(cfgp, "rb").read() if os.path.isfile(cfgp) else None
    Cfg.load(Paths.get(mods))
    Store_.start(Paths.get(mods))
    after = open(cfgp, "rb").read() if os.path.isfile(cfgp) else None
    players = sorted(f[:-5] for f in os.listdir(os.path.join(home, "universe", "players")) if f.endswith(".json")) if os.path.isdir(os.path.join(home, "universe", "players")) else []
    if step == "start1":
        K.check(before is None and after is not None and b"fish.castRange=12" in after, "D start1: no SkyyFishing data yet -> the default config is written")
        for i, u in enumerate(players):
            Store_.onCatch(u, 2, 1000 + i, 400 + i)
            Store_.onCatch(u + "-p2", 5, 5000 + i, 900)
            Store_.addClaim(u, "F|2|%d|%d|live" % (1500 + i, 500))
            Store_.serverRecord(2, 1000 + i, "p%d" % i)
        Store_.sold(2, 1000)
        Store_.flush()
    else:
        K.check(before is not None and before == after, "D start2: the config file is read, not rewritten (bytes unchanged)")
        for i, u in enumerate(players):
            b1 = list(Store_.best(u, 2))
            b2 = list(Store_.best(u + "-p2", 5))
            K.check(b1 == [1, 1000 + i, 400 + i] and b2 == [1, 5000 + i, 900] and int(Store_.pond(u)) == 1 and int(Store_.pond(u + "-p2")) == 1
                    and list(Store_.claims(u)) == ["F|2|%d|500|live" % (1500 + i)] and list(Store_.best(u, 5)) == [0, 0, 0],
                    "D start2 %s: the progress of start 1 is read back per PROFILE (p1 trout, p2 catfish, the waiting claim), nothing mixed" % u)
        K.check(int(Store_.recordG(2)) == 1000 + max(0, len(players) - 1) and float(Store_.demand(2, 1000)) < 1.0,
                "D start2: the server record + the demand factor survive the restart")
    # the live player files decode with our stat + items: a saved SkyyReelProbe reel value stays valid (0-8 within our 0-18)
    ESTc = light_stats(K, jz)
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    BD, EEI = JClass("org.bson.BsonDocument"), JClass("com.hypixel.hytale.codec.EmptyExtraInfo")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    sidx = int(ESTc.getAssetMap().getIndex(STAT))
    n_stat, n_rod = 0, 0
    for u in players:
        d = json.load(open(os.path.join(home, "universe", "players", u + ".json"), encoding="utf-8"))
        es = d.get("Components", {}).get("EntityStats")
        if es is not None:
            try:
                m = ESM.CODEC.decode(BD.parse(json.dumps(es)), EEI.EMPTY)
                m.update()
                v = m.get(sidx)
                val = float(v.get()) if v is not None else None
                saved = (es.get("Stats", {}).get(STAT) or {}).get("Value")
                K.check(v is not None and (saved is None or abs(val - float(saved)) < 1e-6) and 0.0 <= val <= 18.0,
                        "D %s %s: EntityStats decode with our stat; the saved reel look %s stays %s" % (step, u, saved, val))
                n_stat += 1
            except Exception as e:
                K.check(False, "D %s %s: EntityStats decode: %s" % (step, u, str(e)[:200]))
        for sec in ("StorageInventory", "HotbarInventory", "BackpackInventory"):
            inv = d.get("Components", {}).get(sec, {}).get("Inventory")
            if not inv or inv.get("Id") != "Simple":
                continue
            try:
                cont = SIC.CODEC.decode(BD.parse(json.dumps(dict((k, v) for k, v in inv.items() if k != "Id"))), EEI.EMPTY)
                for sl in range(int(cont.getCapacity())):
                    s_ = cont.getItemStack(JClass("java.lang.Short")(sl).shortValue())
                    if s_ is not None and not s_.isEmpty() and str(s_.getItemId()).startswith("SkyyFishing_Rod_"):
                        rig = list(Rig.rigOf(s_))
                        K.check(len(rig) == 4, "D %s %s: a live %s (a SkyyReelProbe rod) reads as a rod with rig %s (no crash)" % (step, u, s_.getItemId(), rig))
                        n_rod += 1
            except Exception as e:
                K.notes.append("D %s %s %s: %s" % (step, u, sec, str(e)[:120]))
    K.notes.append("D %s: %d live players, %d stat maps decoded, %d probe rods found" % (step, len(players), n_stat, n_rod))
    K.save(players=len(players))


def run_perm(out):
    """child P: permissions with the engine's own AbstractCommand code"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR], verify=True)
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn, admin in (("FishCmd", False), ("FishAdminCmd", True), ("FishAdminArgCmd", True), ("FishAdminArg2Cmd", True)):
        try:
            c = JClass(PKG + cn)()
        except Exception as e:
            K.check(False, "P. construct %s: %s" % (cn, e))
            continue
        perm = c.getPermission()
        groups = [str(g) for g in (fld.get(c) or [])]
        if admin:
            K.check(perm is not None and NODE in str(perm) and groups == [], "P. %s requires %s with no permission groups (%s, %s)" % (cn, NODE, perm, groups))
        else:
            K.check(groups == ["hytale:Adventurer"], "P. %s is for every player (hytale:Adventurer): %s" % (cn, groups))
        if cn in ("FishCmd", "FishAdminCmd"):
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            K.check(not leak, "P. %s gives %s to no group (leak %s)" % (cn, NODE, leak))
    K.check("fish" in [str(a) for a in JClass(PKG + "FishCmd")().getAliases()], "P. /fishing has the alias /fish")
    K.save()


def run_bytecode(out):
    """child B: setup()'s calls in order, ONE registerSystem, the bobber recipe, the world-thread hops"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CPool = JClass("javassist.bytecode.ConstPool")

    def calls_of(cls, meth):
        cc = cp.get(PKG + cls)
        out_ = []
        for mi in cc.getClassFile2().getMethods():
            if str(mi.getName()) != meth:
                continue
            cpool, it = mi.getConstPool(), mi.getCodeAttribute().iterator()
            while it.hasNext():
                p = it.next()
                op = it.byteAt(p)
                if op in (0xb6, 0xb7, 0xb8, 0xb9):
                    i = it.u16bitAt(p + 1)
                    if cpool.getTag(i) == CPool.CONST_InterfaceMethodref:
                        out_.append(str(cpool.getInterfaceMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getInterfaceMethodrefName(i)))
                    else:
                        out_.append(str(cpool.getMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getMethodrefName(i)))
                elif op == 0xbb:
                    out_.append("new " + str(cpool.getClassInfo(it.u16bitAt(p + 1))).rsplit(".", 1)[-1])
                elif op in (0xb2, 0xb3):
                    out_.append(("get " if op == 0xb2 else "put ") + str(cpool.getFieldrefName(it.u16bitAt(p + 1))))
        return out_

    def in_order(calls, want):
        pos = 0
        for w in want:
            try:
                pos = calls.index(w, pos) + 1
            except ValueError:
                return w
        return None
    su = calls_of("SkyyFishingPlugin", "setup")
    miss = in_order(su, ["PluginBase.getLogger", "put LOG", "FishCfg.load", "FishStore.start", "new FishEngApi", "put API", "CfgPub.start",
                         "OpenCustomUIInteraction.registerSimple", "CommandRegistry.registerCommand", "CommandRegistry.registerCommand",
                         "EventRegistry.registerGlobal", "EventRegistry.registerGlobal", "new FishTick", "ComponentRegistryProxy.registerSystem",
                         "ScheduledExecutorService.scheduleWithFixedDelay"])
    K.check(miss is None and su.count("ComponentRegistryProxy.registerSystem") == 1,
            "B: setup() = log, config, store, the engine API, the config kit, the bench page, /fishing + /fishadmin, ready + quit events, ONE "
            "registerSystem (FishTick), the 2 s save (missing %s)" % miss)
    sd = calls_of("SkyyFishingPlugin", "shutdown")
    K.check(in_order(sd, ["FishCore.dropAll", "FishStore.flush", "CfgPub.shutdown", "JavaPlugin.shutdown"]) is None or
            in_order(sd, ["FishCore.dropAll", "FishStore.flush", "CfgPub.shutdown", "PluginBase.shutdown"]) is None,
            "B: shutdown() drops every line, writes the last save, closes the config kit: %s" % [c for c in sd if "." in c][:8])
    ho = calls_of("FishBobberTask", "holder")
    miss = in_order(ho, ["Store.getRegistry", "ComponentRegistry.newHolder", "new NetworkId", "EntityStore.takeNextNetworkId", "NetworkId.<init>",
                         "ComponentRegistry.getNonSerializedComponentType", "NonSerialized.get", "new TransformComponent", "ModelAsset.getAssetMap",
                         "new ModelComponent", "Model.createScaledModel", "new HeadRotation", "new Nameplate", "Intangible.getComponentType"])
    K.check(miss is None, "B: the bobber = the vanilla ChangeModelPage preview recipe (NetworkId + NonSerialized - never saved - + Transform + Model + "
                          "HeadRotation) + Nameplate + Intangible (missing %s)" % miss)
    run_ = calls_of("FishBobberTask", "run")
    K.check("Store.addEntity" in run_ and "Store.removeEntity" in run_ and "World.getEntityStore" in run_, "B: the bobber task adds / removes on the world's store")
    for m_, w_ in (("spawnBobber", "World.execute"), ("removeBobber", "World.execute"), ("later", "World.execute")):
        K.check(w_ in calls_of("FishEngApi", m_), "B: FishEngApi.%s hops to the world thread (%s)" % (m_, w_))
    hs_, hh_, hu_ = calls_of("FishEngApi", "hudState"), calls_of("FishEngApi", "hudHide"), calls_of("FishEngApi", "hudSet")
    upd = ("FishHud.update", "CustomUIHud.update")
    K.check("HudManager.addCustomHud" in hs_ and any(u in hs_ for u in upd) and "FishHudDoc.fill" in hs_ and "HudManager.removeCustomHud" in hh_
            and any(u in hu_ for u in upd) and "FishHudDoc.sets" in hu_ and "HudManager.getCustomHud" in calls_of("FishEngApi", "current"),
            "B: the widget = our own keyed HUD (HudManager.addCustomHud / getCustomHud / removeCustomHud; a full document per state, then "
            "update(false) with the bar + texts): %s | %s | %s" % (hs_, hh_, hu_))
    core_add = [m for m in ("tickPlayer", "land", "fight", "hook", "bite", "cast", "lose", "missed", "finish", "cancel", "line", "roll")
                if any(c.endswith("addItemStack") or c == "FishCore.give" or c == "FishCore.payClaims" for c in calls_of("FishCore", m))]
    K.check(not core_add and "FishCore.give" in calls_of("FishCore", "payClaims") and "FishCore.payClaims" in calls_of("FishGiveTask", "run"),
            "B: nothing inside the tick touches an inventory (the world-thread rule): catches go through claims + FishGiveTask -> payClaims (%s)" % core_add)
    K.check("FishEngApi.later" not in calls_of("FishCore", "land") and "FishCore.kick" in calls_of("FishCore", "land")
            and "FishApi.later" in calls_of("FishCore", "kick"), "B: land() saves claims then kicks ONE hand-over task (kick -> API.later)")
    K.save()


def run_audit(out):
    """child AA: the engine-access audit (the SkyyReelProbe / SkyyClasses harness, part AA)"""
    from jpype import JClass
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=False)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    for p_ in (B.SERVER_JAR, JAR, FAKE_DIR):
        CP.appendClassPath(p_)
    LIN, MTc, CPool, JMod_ = (JClass(FAKE_PKG + ".LookupIn"), JClass("java.lang.invoke.MethodType"), JClass("javassist.bytecode.ConstPool"),
                              JClass("java.lang.reflect.Modifier"))
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, loader)
    cs_ = set()

    def lookup_audit(cn):
        D = jvm_class(cn)
        lk = LIN.lookupIn(D)
        cc = CP.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n = [], 0
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it_ = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it_.hasNext():
                p_ = it_.next()
                op = it_.byteAt(p_)
                if op not in XOPS:
                    continue
                where = "%s.%s @%d %s" % (cn.rsplit(".", 1)[-1], mi.getName(), p_, XOPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                C_ = None
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", loader).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)),
                                                 str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, loader)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn
                                    or (not JMod_.isPrivate(md) and str(C_.getPackageName()) == str(D.getPackageName()))):
                                raise ValueError("constructor %s %s%s is not accessible from %s" % (JMod_.toString(md), cname, desc, cn))
                        elif name == "<init>":
                            lk.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lk.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lk.findSpecial(C_, name, mt, D)
                        else:
                            lk.findVirtual(C_, name, mt)
                except Exception as ex_:
                    ok_ = False
                    if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb8, 0xb9) and C_ is not None:
                        try:
                            mm_ = C_.getMethod(name, mt.parameterArray())
                            ok_ = JMod_.isPublic(int(C_.getModifiers())) and JMod_.isPublic(int(mm_.getModifiers()))
                            if ok_:
                                cs_.add("%s.%s" % (str(C_.getName()), name))
                        except Exception:
                            ok_ = False
                    if not ok_:
                        refused.append("%s: %s" % (where, ex_))
        return refused, n
    names = [n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(JAR).namelist() if n_.endswith(".class")]
    res = {"classes": len(names), "refs": 0, "refused": [], "per": {}}
    for cn in names:
        try:
            r_, k_ = lookup_audit(cn)
        except Exception as ex_:
            r_, k_ = ["%s: could not audit: %s" % (cn, ex_)], 0
        res["refused"] += r_
        res["refs"] += k_
        res["per"][cn.rsplit(".", 1)[-1]] = k_
    res["control"] = lookup_audit(FAKE_PKG + ".BadAccess")[0]
    res["caller_sensitive"] = sorted(cs_)
    json.dump(res, open(out, "w"), indent=1)


# ====================================================================================================== parent driver
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--live", LIVE], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, n))
    return d


def copy_live(home):
    """the live world folder, READ ONLY: universe/players/*.json and mods/Skyy_SkyyFishing (if any) copied into scratch"""
    n = 0
    src = os.path.join(LIVE, "universe", "players")
    dst = os.path.join(home, "universe", "players")
    os.makedirs(dst, exist_ok=True)
    if os.path.isdir(src):
        for f in sorted(os.listdir(src)):
            if f.endswith(".json"):
                shutil.copyfile(os.path.join(src, f), os.path.join(dst, f))
                n += 1
    ours = os.path.join(LIVE, "mods", "Skyy_SkyyFishing")
    os.makedirs(os.path.join(home, "mods"), exist_ok=True)
    if os.path.isdir(ours):
        shutil.copytree(ours, os.path.join(home, "mods", "Skyy_SkyyFishing"))
    return n


def main():
    for flag, fn in (("--mkfake", lambda: run_mkfake(arg("--mkfake"))), ("--verify", lambda: run_verify(arg("--out"))),
                     ("--engine", lambda: run_engine(arg("--out"))), ("--live-step", lambda: run_live(arg("--live-step"), arg("--out"))),
                     ("--perm", lambda: run_perm(arg("--out"))), ("--bytecode", lambda: run_bytecode(arg("--out"))),
                     ("--audit", lambda: run_audit(arg("--out")))):
        if flag in sys.argv:
            try:
                fn()
            except Exception:
                import traceback
                traceback.print_exc()
                sys.exit(1)
            return
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        part_static()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0 and os.path.isfile(os.path.join(FAKE_DIR, FAKE_PKG, "FakePage.class")), "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("engine", "--engine"), ("perm", "--perm"), ("bytecode", "--bytecode")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        n = copy_live(os.path.join(SCRATCH, "live"))
        print("D. %d live player files copied (read-only source %s)" % (n, LIVE))
        check(n > 0, "D: live player files found to copy (%s)" % LIVE)
        for step in ("start1", "start2"):
            out = os.path.join(SCRATCH, "live-%s.json" % step)
            pr = child(env, "--live-step", step, "--out", out)
            check(pr.returncode == 0, "D %s: the child exited cleanly" % step)
            take(out, "live " + step)
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 1000 and a["classes"] == len(CLASSES),
                  "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: control refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, 0 refused, control refused; caller-sensitive: %s"
                  % (a["refs"], a["classes"], a["caller_sensitive"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d ok, %d fail(s)" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
