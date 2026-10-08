"""Harness for SkyyReelProbe 0.1. Build first: python SkyyReelProbe/build_skyyreelprobe_0.1.py

    python SkyyReelProbe/test_skyyreelprobe_0.1.py [--jar <SkyyReelProbe-0.1.jar>] [--live <a players folder>] [--keep] [--fast]

Parent (plain Python, Assets.zip + the jar read-only):
  J  the jar: manifest (Main, IncludesAssetPack), exactly the 8 expected classes, the asset files (stat + 8 items + lang + 84 art files),
     no .ui file
  N  NO OVERRIDE: every asset path / item id / the stat id is new - not in Assets.zip, not in any installed mod in UserData/Mods
     (read-only scan of every .jar / .zip there, minus SkyyReelProbe itself)
  S  the stat JSON = vanilla GlidingActive's keys in its order (InitialValue 0, Min 0, Shared, IgnoreInvulnerability) with Max 8, no
     Regenerating / MinValueEffects, + HideFromTooltip (the vanilla MagicCharges key)
  I  the 8 rod items: no Recipe / Interactions / Weapon / Tags / Parent; hold fields = Weapon_Wand_Wood's; MaxStack 1; Categories
     Items.Tools (= Template_Glider); Icon = the rod's render; default Model / Texture = the rod's own reel (look K = its tier number);
     ItemAppearanceConditions on SkyyFishing_Reel = 9 entries K 0..8, each exactly {Condition [K, K], Model, Texture} (Template_Glider's
     key spelling, no ConditionValueType); K 0 = the NoReel model; every referenced file is in the jar or Assets.zip; lang lines
  ART tools/art/make_fishing.py: main() output (run into scratch) byte-identical to the generator's local outputs in models-local/art/
     fishing (= the pre-change generator: same 87 files) [skipped with --fast or when models-local is absent]; reel_looks() twice =
     the same bytes = the jar's art bytes; every variant texture has the default texture's size and differs from it ONLY on the Reel +
     Crank faces (+ their clamp-to-edge columns on 64-wide textures); reel = the rod's own tier gives the default texture byte for byte;
     the 8 reel looks of a rod are pairwise different; NoReel model = the rod model minus exactly Reel + Crank; icons = the alt/ renders
Children (fresh JVMs: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch):
  F  the stand-in classes (MapStore / MapChunk / FakeHotbar / LookupIn / BadAccess) generated with javassist into scratch
  A  every class loads and verifies
  L  RpLogic on plain data (rodIndex, the auto table Bamboo 2 .. Mithril 8, Onyxium 1, parseReel, reelName, toReel NaN, heldText)
  E  ENGINE CODECS (AssetRegistryLoader.init + the stat / interaction stores): GlidingActive + every vanilla stat + OURS decode through
     EntityStatType's codec (no unknown key, no validation failure; ours: max 8, shared, ignoreInvulnerability, hideFromTooltip, no regen)
     and load; the 8 rods decode through Item's codec (no unknown key, no validation failure) and load; Item.toPacket() carries the
     appearance conditions under OUR stat's index with Condition [K, K] Absolute + the right model / texture for K 0..8
  X  EVERY NEW CODE PATH EXECUTED on engine stand-ins (real EntityStatMap / EntityStatValue / InventoryComponent containers / Item
     assets / InventorySetActiveSlotEvent; allocated modules; MapStore answering components per Ref): RpStat.index / map / value / get /
     set (clamp 0..8, read back, stat missing), heldId; RpCmds.status / help / give (8 rods into storage first, then a full inventory:
     nothing dropped, the 'no room' line) / setReel (turns auto off) / applyAuto / toggleAuto / run (give, auto, 0-8, garbage);
     RpSlotSys.handle (hotbar section, other sections ignored, auto off ignored, rods -> the next tier's reel, a non-rod -> 0, a broken
     event logged once); ReelProbeCmd.execute + ReelProbeArgCmd.execute through reflection with a real CommandContext; plugin
     shutdown clears auto; setup()'s calls in their order (bytecode)
  P  /reelprobe + its usage variant: permission node skyyreelprobe.admin, empty permission groups, getPermissionGroupsRecursive() gives
     the node to no group
  D  START TWICE ON A SCRATCH COPY OF LIVE DATA: the live player files (Saves/<deploy world>/universe/players, read-only, copied) ->
     start 1 (child JVM): the real EntityStatMap codec decodes each player's EntityStats with the stat loaded, the reel starts at 0,
     RpStat.set 5, encoded back; start 2 (new child): the reel is still 5, every other stat value + modifier unchanged; probe REMOVED
     (new child, stat not loaded): the engine keeps the entry in EntityStatMap.unknown, RpStat answers -1 (no throw) and the entry
     survives the next save; probe ADDED BACK (new child): the reel is 5 again
     RODS LEFT BEHIND (fix 0.1 critic): start 1 puts a SkyyFishing_Rod_Cobalt stack into a free StorageInventory slot of each copy;
     every step decodes the StorageInventory through SimpleItemContainer.CODEC: the rod stack keeps its id + slot through every save;
     probe REMOVED: ItemStack.getItem() = Item.UNKNOWN (id "Unknown"), the stack is still in the container and still sent to the client
     (toProtocolMap carries it with its itemId); probe ADDED BACK: getItem() is the rod again; the other slots are unchanged
  AA the ENGINE-ACCESS AUDIT: every class / field / method / constructor reference in the jar looked up with
     MethodHandles.privateLookupIn the referencing class (the JVM's own access rules) - 0 refused; the control (a class calling the
     protected CustomUIPage.sendUpdate from outside) refused
Not testable without the game (the build report lists them as UNVERIFIED): what the client draws (the swapped model / texture in first
and third person, on other players, the dropped rod, the icons), the held pose, the hotbar event on a real scroll, and what the CLIENT
shows for a left-behind rod after the probe is removed (the server keeps + sends it; the client has no item asset for that id).
Scratch: tools/dev/scratch/reelprobe01/test (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, hashlib

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


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyReelProbe-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "reelprobe01", "test")))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyyreeltest"
PKG = "com.skyy.reelprobe."
CLASSES = sorted(PKG + c for c in ["RpLog", "RpLogic", "RpStat", "RpCmds", "RpSlotSys", "ReelProbeArgCmd", "ReelProbeCmd",
                                   "SkyyReelProbePlugin"])
TIERS = ["Bamboo", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
RODS = ["SkyyFishing_Rod_%s" % t for t in TIERS]
STAT = "SkyyFishing_Reel"
NODE = "skyyreelprobe.admin"
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
LOCAL_ART = os.path.join(ROOT, "models-local", "art", "fishing")
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


LIVE = os.path.abspath(arg("--live", os.path.join(B.USERDATA, "Saves", deploy_world(), "universe", "players")))


# ====================================================================================================== parent: J N S I ART
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


def part_static():
    jz, az = zipfile.ZipFile(JAR), zipfile.ZipFile(ASSETS)
    az_names = set(az.namelist())
    # ---------------- J
    man = json.loads(jz.read("manifest.json"))
    check(man["Main"] == PKG + "SkyyReelProbePlugin" and man["IncludesAssetPack"] is True and man["Version"] == VERSION
          and man["Name"] == "%s SkyyReelProbe" % VERSION, "J. manifest %s" % man)
    cls = sorted(n[:-6].replace("/", ".") for n in jz.namelist() if n.endswith(".class"))
    check(cls == CLASSES, "J. classes %s" % cls)
    assets = sorted(n for n in jz.namelist() if not n.endswith(".class") and n != "manifest.json")
    art = [n for n in assets if n.startswith("Common/")]
    check(not any(n.lower().endswith(".ui") for n in jz.namelist()), "J. no .ui file")
    check(len(art) == 84 and len(assets) == 84 + 8 + 2, "J. assets = 84 art + 8 items + stat + lang (%d / %d)" % (len(art), len(assets)))
    check("Server/Entity/Stats/%s.json" % STAT in assets and "Server/Languages/en-US/server.lang" in assets, "J. stat + lang present")
    items = items_of(jz)
    check(sorted(items) == sorted(RODS), "J. items %s" % sorted(items))
    print("J. jar: %d classes, %d assets (%d art)" % (len(cls), len(assets), len(art)))
    # ---------------- N
    for n in assets:
        if not n.endswith("server.lang"):
            check(n not in az_names, "N. %s exists in Assets.zip" % n)
    az_ids = set(n.rsplit("/", 1)[1][:-5] for n in az_names if n.startswith("Server/Item/") and n.endswith(".json"))
    az_stats = set(n.rsplit("/", 1)[1][:-5] for n in az_names if n.startswith("Server/Entity/Stats/"))
    for i in RODS:
        check(i not in az_ids, "N. rod id %s is new" % i)
    check(STAT not in az_stats, "N. stat %s is new" % STAT)
    mods = B.MODS_DIR
    seen, scanned = {}, 0
    mine = set(assets)
    for f in sorted(os.listdir(mods)) if os.path.isdir(mods) else []:
        p = os.path.join(mods, f)
        if not (f.endswith(".jar") or f.endswith(".zip")) or f.startswith("SkyyReelProbe") or not os.path.isfile(p):
            continue
        try:
            with zipfile.ZipFile(p) as mz:
                names = mz.namelist()
        except Exception:
            continue
        scanned += 1
        for n in names:
            base = n.rsplit("/", 1)[-1]
            if (n in mine and not n.endswith("server.lang")) or ("/Item/" in n and n.endswith(".json") and base[:-5] in RODS) or \
                    (n.endswith("Entity/Stats/%s.json" % STAT)):
                seen.setdefault(n, []).append(f)
    check(not seen, "N. paths / ids also shipped by installed mods: %s" % dict(list(seen.items())[:5]))
    print("N. no override: Assets.zip + %d installed mod files" % scanned)
    # ---------------- S
    glide = json.loads(az.read("Server/Entity/Stats/GlidingActive.json").decode("utf-8-sig"))
    stat_txt = jz.read("Server/Entity/Stats/%s.json" % STAT).decode("utf-8")
    st = json.loads(stat_txt)
    exp = [k for k in glide if k not in ("Regenerating", "MinValueEffects")] + ["HideFromTooltip"]
    check(list(st) == exp, "S. stat keys in GlidingActive's order + HideFromTooltip: %s" % list(st))
    check(st == {"InitialValue": 0, "Min": 0, "Max": 8, "Shared": True, "IgnoreInvulnerability": True, "HideFromTooltip": True},
          "S. stat values %s" % st)
    for k in ("InitialValue", "Min", "Shared", "IgnoreInvulnerability"):
        check(st[k] == glide[k], "S. %s = GlidingActive's %r" % (k, glide[k]))
    check(json.loads(az.read("Server/Entity/Stats/MagicCharges.json").decode("utf-8-sig")).get("HideFromTooltip") is True,
          "S. HideFromTooltip is the vanilla MagicCharges key")
    # ---------------- I
    van = dict((n.rsplit("/", 1)[1][:-5], n) for n in az_names if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    wand = json.loads(az.read(van["Weapon_Wand_Wood"]).decode("utf-8-sig"))
    glider = json.loads(az.read(van["Template_Glider"]).decode("utf-8-sig"))
    gc = glider["ItemAppearanceConditions"]["GlidingActive"][0]
    la = lang_of(jz)
    jn = set(jz.namelist())

    def exists(rel):
        return ("Common/" + rel) in jn or ("Common/" + rel) in az_names
    for ti, (tier, iid) in enumerate(zip(TIERS, RODS)):
        d = items[iid]
        for k in ("Recipe", "Interactions", "Weapon", "Tags", "Parent", "Particles", "InteractionVars", "Utility"):
            check(k not in d, "I. %s has no %s" % (iid, k))
        for k in ("PlayerAnimationsId", "DroppedItemAnimation", "ItemSoundSetId", "Quality"):
            check(d.get(k) == wand[k], "I. %s %s = Weapon_Wand_Wood's (%r)" % (iid, k, wand[k]))
        check(d["MaxStack"] == 1 and d["Categories"] == glider["Categories"] == ["Items.Tools"], "I. %s MaxStack 1, Items.Tools" % iid)
        check(d["Icon"] == "Icons/ItemsGenerated/%s.png" % iid and ("Common/" + d["Icon"]) in jn, "I. %s icon shipped" % iid)
        check(d["IconProperties"] == {"Scale": 0.2763, "Translation": [-40.51, -43.16], "Rotation": [45, 90, 0]},
              "I. %s IconProperties = the shared rod view %s" % (iid, d["IconProperties"]))
        check(exists(d["Model"]) and exists(d["Texture"]), "I. %s default model / texture exist" % iid)
        conds = d["ItemAppearanceConditions"]
        check(list(conds) == [STAT], "I. %s conditions only on %s" % (iid, STAT))
        cs = conds[STAT]
        check([c["Condition"] for c in cs] == [[k, k] for k in range(9)], "I. %s Condition [K, K] for K 0..8" % iid)
        check(all(sorted(c) == sorted(gc) == ["Condition", "Model", "Texture"] for c in cs),
              "I. %s every entry = Template_Glider's keys (no ConditionValueType)" % iid)
        check(all(exists(c["Model"]) and exists(c["Texture"]) for c in cs), "I. %s every look's files exist" % iid)
        check(cs[0]["Model"].endswith("%s_NoReel.blockymodel" % iid) and cs[0]["Texture"] == d["Texture"], "I. %s K 0 = NoReel + default" % iid)
        check(cs[ti + 1]["Model"] == d["Model"] and cs[ti + 1]["Texture"] == d["Texture"], "I. %s K %d (own reel) = the default look" % (iid, ti + 1))
        check(all(c["Model"] == d["Model"] for c in cs[1:]), "I. %s K 1..8 share the rod model" % iid)
        check(len(set(c["Texture"] for c in cs[1:])) == 8, "I. %s K 1..8 = 8 different textures" % iid)
        for pre in ("", "server."):
            for k in ("name", "description"):
                check(("%sitems.%s.%s" % (pre, iid, k)) in la, "I. lang %sitems.%s.%s" % (pre, iid, k))
        check(d["TranslationProperties"] == {"Name": "server.items.%s.name" % iid, "Description": "server.items.%s.description" % iid},
              "I. %s TranslationProperties" % iid)
    check(la["server.items.SkyyFishing_Rod_Cobalt.name"] == "Cobalt Fishing Rod (reel probe)", "I. names say the tier")
    print("I. 8 rods x 9 looks checked")
    return jz, az


def part_art(jz, az):
    import make_fishing as MF
    import skyyart as SA
    # main() unchanged: its outputs into scratch = the generator's local outputs (made before reel_looks existed)
    if "--fast" not in sys.argv and os.path.isfile(os.path.join(LOCAL_ART, "manifest.json")):
        out = os.path.join(SCRATCH, "art_main")
        old = MF.OUT
        MF.OUT = out
        try:
            MF.main()
        finally:
            MF.OUT = old
        diff, n = [], 0
        for r, d, fs in os.walk(out):
            for f in fs:
                p = os.path.join(r, f)
                rel = os.path.relpath(p, out)
                n += 1
                lp = os.path.join(LOCAL_ART, rel)
                if not os.path.isfile(lp) or open(lp, "rb").read() != open(p, "rb").read():
                    diff.append(rel)
        check(n == 87 and not diff, "ART. make_fishing main() = the local outputs byte for byte (%d files, differ %s)" % (n, diff[:5]))
        print("ART. main() unchanged: %d files byte-identical to models-local/art/fishing" % n)
    else:
        print("ART. main() comparison skipped (--fast or no models-local)")
    l1, l2 = MF.reel_looks(az), MF.reel_looks(az)

    def flat(l):
        return dict((p, b) for r in l["rods"] for p, b in r["files"].items())
    f1 = flat(l1)
    check(f1 == flat(l2) and json.dumps([dict((k, v) for k, v in r.items() if k != "files") for r in l1["rods"]]) ==
          json.dumps([dict((k, v) for k, v in r.items() if k != "files") for r in l2["rods"]]), "ART. reel_looks deterministic (two runs)")
    check(sorted(f1) == sorted(n for n in jz.namelist() if n.startswith("Common/")) and all(jz.read(p) == b for p, b in f1.items()),
          "ART. the jar's 84 art files = reel_looks() byte for byte")
    P = MF.palettes(az)
    base = MF.rod_base(az)
    rects = SA.node_rects(base, list(MF.REEL_NODES))

    def allowed(x, y, w):
        for rr in rects:
            x0, y0, x1, y1 = rr
            if y0 <= y < y1 and (x0 <= x < x1 or (w > 32 and x >= 32 and x1 > 31 >= x0)):
                return True
        return False
    for r in l1["rods"]:
        tier = r["tier"]
        dflt_b = f1.get(r["texture"]) or SA._read(az, r["texture"])
        dflt = SA.png_decode(dflt_b)
        texs = []
        for lk in r["looks"][1:]:
            tb = f1.get(lk["texture"]) or SA._read(az, lk["texture"])
            texs.append(tb)
            t = SA.png_decode(tb)
            check((t.w, t.h) == (dflt.w, dflt.h), "ART. %s reel %d texture size = default" % (tier, lk["reel"]))
            bad = []
            for y in range(t.h):
                for x in range(t.w):
                    if t.get(x, y) != dflt.get(x, y) and not allowed(x, y, t.w):
                        bad.append((x, y))
            check(not bad, "ART. %s reel %d differs from the default only on the Reel + Crank faces (outside: %s)" % (tier, lk["reel"], bad[:4]))
        check(len(set(texs)) == 8, "ART. %s: the 8 reel looks are pairwise different" % tier)
        own = MF.build_rod(az, P, tier, tier)[1]
        check((own.w, own.h) == (dflt.w, dflt.h) and bytes(own.px) == bytes(dflt.px),
              "ART. %s: reel = own tier gives the default texture pixel for pixel" % tier)
        model = json.loads((f1.get(r["model"]) or SA._read(az, r["model"])).decode("utf-8-sig"))
        noreel = json.loads(f1[r["noreel_model"]].decode("utf-8"))
        names_m, names_n = SA.node_names(model), SA.node_names(noreel)
        if r["model"] == MF.ROD_MODEL:
            names_m = SA.node_names(base)
        check(sorted(set(names_m) - set(names_n)) == sorted(MF.REEL_NODES) and set(names_n) <= set(names_m),
              "ART. %s NoReel = the rod model minus exactly Reel + Crank" % tier)
        ic = SA.png_decode(f1[r["icon"]])
        check((ic.w, ic.h) == (64, 64), "ART. %s icon 64x64" % tier)
        alt = os.path.join(LOCAL_ART, "alt", "%s_Render.png" % r["item"])
        if os.path.isfile(alt):
            check(open(alt, "rb").read() == f1[r["icon"]], "ART. %s icon = the alt/ render Skyy picked ('second row for the rod')" % tier)
    print("ART. reel_looks: %d files, every variant confined to the reel faces" % len(f1))


# ====================================================================================================== children
def _jvm(cp, verify=True):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
    jpype.startJVM(jvm, *opts, classpath=list(cp), convertStrings=True)


def run_mkfake(out_dir):
    """child F: the stand-ins as .class files (the SkyyClasses 0.1.12 harness pattern): subclasses of engine classes, always created with
    Unsafe.allocateInstance (no constructor runs)."""
    from jpype import JClass
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    P = FAKE_PKG
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
    ms.addMethod(CtNewMethod.make("""public void putComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) {
  java.util.Map m = (java.util.Map) this.comps.get(r);
  if (m == null) { m = new java.util.IdentityHashMap(); this.comps.put(r, m); }
  m.put(t, c);
}""", ms))
    ms.addMethod(CtNewMethod.make("public boolean isProcessing() { return false; }", ms))
    ms.addField(CtField.make("public com.hypixel.hytale.component.Archetype arch;", ms))
    ms.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Archetype getArchetype(com.hypixel.hytale.component.Ref r) { return this.arch; }", ms))
    ms.addMethod(CtNewMethod.make("public java.lang.Object getExternalData() { return this.ext; }", ms))
    ms.writeFile(out_dir)
    mc = cp.makeClass(P + ".MapChunk")
    mc.setSuperclass(cp.get("com.hypixel.hytale.component.ArchetypeChunk"))
    mc.addField(CtField.make("public com.hypixel.hytale.component.Ref ref;", mc))
    mc.addConstructor(CtNewConstructor.make("public MapChunk() { super(null, null); }", mc))   # never run (Unsafe)
    mc.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Ref getReferenceTo(int i) { return this.ref; }", mc))
    mc.writeFile(out_dir)
    fh = cp.makeClass(P + ".FakeHotbar")
    fh.setSuperclass(cp.get("com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar"))
    fh.addField(CtField.make("public com.hypixel.hytale.server.core.inventory.ItemStack item;", fh))
    fh.addField(CtField.make("public boolean boom;", fh))
    fh.addConstructor(CtNewConstructor.make("public FakeHotbar() { super(); }", fh))
    fh.addMethod(CtNewMethod.make("public com.hypixel.hytale.server.core.inventory.ItemStack getActiveItem() { if (this.boom) throw new IllegalStateException(\"boom\"); return this.item; }", fh))
    fh.writeFile(out_dir)
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


def engine_setup(K, with_stat, jz):
    """Options + allocated HytaleServer / Universe, AssetRegistryLoader.init, the stat / interaction stores, the stat modifier codecs,
    every vanilla stat (+ ours when with_stat) decoded through EntityStatType's codec and loaded. Answers a dict of helpers."""
    from jpype import JClass, JArray, JString, JImplements, JOverride
    az = zipfile.ZipFile(ASSETS)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def jfield(c, n):
        f = c.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    jfield(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    CHM, COLL = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Collections")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu, wmap = CHM(), CHM()
    for n, v in (("playersByUuid", pbu), ("players", COLL.unmodifiableCollection(pbu.values())), ("worlds", wmap), ("worldsByUuid", CHM()),
                 ("unmodifiableWorlds", COLL.unmodifiableMap(wmap))):
        jfield(UNI, n).set(uni, v)
    jfield(UNI, "instance").set(None, uni)
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
    ESTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    INTc, ROOTc = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    UIc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.UnarmedInteractions")
    K.check(AR.getAssetStore(ESTc.class_) is None, "E: the EntityStatType store is not registered by AssetRegistryLoader.init (registered here like "
                                                    "EntityStatsModule.setup)")
    AR.register(HAS.builder(ESTc.class_, ILT(ArrOf(ESTc))).setPath("Entity/Stats").setCodec(ESTc.CODEC).setKeyFunction(GetId())
                .setReplaceOnRemove(NoRep()).build())
    AR.register(HAS.builder(INTc.class_, ILT(ArrOf(INTc))).setPath("Item/Interactions").setCodec(INTc.CODEC).setKeyFunction(GetId())
                .setReplaceOnRemove(NoRep()).setIsUnknown(IsUnknown()).build())
    AR.register(HAS.builder(ROOTc.class_, ILT(ArrOf(ROOTc))).setPath("Item/RootInteractions").setCodec(ROOTc.CODEC).setKeyFunction(GetId())
                .setReplaceOnRemove(NoRep()).build())
    AR.register(HAS.builder(UIc.class_, DAMc()).setPath("Item/Unarmed/Interactions").setCodec(UIc.CODEC).setKeyFunction(GetId()).build())
    SMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MODc = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier")
    MODc.CODEC.register("Boost", SMOD.class_, SMOD.ENTITY_CODEC)      # EntityStatsModule.setup's two registrations (bytecode)
    MODc.CODEC.register("Static", SMOD.class_, SMOD.ENTITY_CODEC)
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR, Paths, ArrayList = JClass("com.hypixel.hytale.codec.util.RawJsonReader"), JClass("java.nio.file.Paths"), JClass("java.util.ArrayList")

    def dec(c, key, text):
        st = AR.getAssetStore(c.class_)
        ei = AEI(Paths.get(key + ".json"), ADT(c.class_, key, None))
        try:
            o = st.getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception as e:
            return None, "exception " + str(e)[:300]
        prob = []
        vr = ei.getValidationResults()
        if vr is not None and vr.hasFailed():
            prob.append("validation failed %s" % [str(x) for x in (vr.getResults() or [])][:3])
        uk = [str(x) for x in ei.getUnknownKeys()]
        if uk:
            prob.append("unknown keys %s" % uk)
        return o, "; ".join(prob)

    def load(c, objs, pack):
        l_ = ArrayList()
        for o in objs:
            l_.add(o)
        r_ = AR.getAssetStore(c.class_).loadAssets(pack, l_)
        return not r_.hasFailed()
    stats, sbad, glide = [], [], None
    for n in sorted(az.namelist()):
        if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
            d = json.loads(az.read(n).decode("utf-8-sig"))
            for k in ("Regenerating", "MinValueEffects", "MaxValueEffects"):   # need EntityStatsModule's condition / interaction codecs
                d.pop(k, None)
            o, why = dec(ESTc, n.rsplit("/", 1)[1][:-5], json.dumps(d))
            if o is None or why:
                sbad.append((n, why))
            else:
                stats.append(o)
                if n.endswith("/GlidingActive.json"):
                    glide = o
    K.check(not sbad and len(stats) >= 12, "E: the vanilla stats decode through EntityStatType's codec (%d): %s" % (len(stats), sbad[:3]))
    ours = None
    if with_stat:
        ours, why = dec(ESTc, STAT, jz.read("Server/Entity/Stats/%s.json" % STAT).decode("utf-8"))
        K.check(ours is not None and not why, "E: OUR stat decodes through EntityStatType's codec - no unknown key, no validation failure (%s)" % why)
        if ours is not None:
            stats.append(ours)
    K.check(bool(load(ESTc, stats, "Hytale:Hytale")), "E: the stats load into the store")
    return {"U": U, "jfield": jfield, "AR": AR, "dec": dec, "load": load, "ESTc": ESTc, "glide": glide, "ours": ours, "uni": uni, "az": az}


def copy_live_into(home):
    os.makedirs(home, exist_ok=True)
    n = 0
    if os.path.isdir(LIVE):
        for f in sorted(os.listdir(LIVE)):
            if f.endswith(".json"):
                shutil.copyfile(os.path.join(LIVE, f), os.path.join(home, f))      # read-only source; the copy is scratch
                n += 1
    return n


def stats_of(path):
    return json.load(open(path, encoding="utf-8"))["Components"]["EntityStats"]


def run_engine(step, out):
    """child: E + X + P (step start1) and the live-data steps start1 / start2 / removed / readded on scratch/live."""
    from jpype import JClass, JArray, JObject, JInt, JFloat, JByte
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR])
    jz = zipfile.ZipFile(JAR)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    for n in CLASSES:
        try:
            Cls.forName(n, True, loader)
            K.ok += 1
        except Exception as e:
            K.check(False, "A: load %s: %s" % (n, e))
    if K.fails:
        K.save()
        return
    with_stat = step != "removed"
    E = engine_setup(K, with_stat, jz)
    U, jfield, ESTc = E["U"], E["jfield"], E["ESTc"]
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    BD, EEI = JClass("org.bson.BsonDocument"), JClass("com.hypixel.hytale.codec.EmptyExtraInfo")
    Stat = JClass(PKG + "RpStat")
    idx = int(ESTc.getAssetMap().getIndex(STAT))
    K.check((idx >= 0) == with_stat and int(Stat.index()) == idx, "E: RpStat.index() = the store's index of %s (%d, loaded %s)" % (STAT, idx, with_stat))

    # ---------------- D: the live-data step (each step = one server start)
    home = os.path.join(SCRATCH, "live")
    live = sorted(f for f in os.listdir(home) if f.endswith(".json")) if os.path.isdir(home) else []
    seen = {}
    ITMd = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    LEFT = "SkyyFishing_Rod_Cobalt"
    if with_stat and step != "start1":                         # start1 loads the rods later (E); the other probe-present starts load them here
        lobjs = []
        for iid in RODS:
            it, why = E["dec"](ITMd, iid, jz.read("Server/Item/Items/SkyyReelProbe/%s.json" % iid).decode("utf-8"))
            if it is not None and not why:
                lobjs.append(it)
        K.check(len(lobjs) == 8 and bool(E["load"](ITMd, lobjs, "Skyy:0.1 SkyyReelProbe")), "D %s: the 8 rods load (probe present)" % step)
    rods_left = {}
    for f in live:
        p = os.path.join(home, f)
        d = json.load(open(p, encoding="utf-8"))
        # ---- rods left behind: a probe rod in the storage inventory across the four starts
        si = d["Components"].get("StorageInventory", {}).get("Inventory")
        if si is not None and si.get("Id") == "Simple":
            items = si.setdefault("Items", {})
            if step == "start1":
                free = [s for s in range(int(si.get("Capacity", 0))) if str(s) not in items]
                if free:
                    items[str(free[0])] = {"Id": LEFT, "Quantity": 1, "Durability": 0.0, "MaxDurability": 0.0, "Quality": 0,
                                           "OverrideDroppedItemAnimation": False}
            slot = [s for s, v in items.items() if v.get("Id") == LEFT]
            if not slot:
                K.notes.append("D %s %s: no free storage slot for the left-behind rod check" % (step, f))
            else:
                inner = dict((k, v) for k, v in si.items() if k != "Id")
                try:
                    cont = SIC.CODEC.decode(BD.parse(json.dumps(inner)), EEI.EMPTY)
                    st = cont.getItemStack(int(slot[0]))
                    gid = str(st.getItem().getId()) if st is not None else None
                    pk = cont.toProtocolMap().get(JClass("java.lang.Integer")(int(slot[0])))
                    K.check(st is not None and str(st.getItemId()) == LEFT and int(st.getQuantity()) == 1,
                            "D %s %s: the rod stack left in storage slot %s decodes with its id (%s)" % (step, f, slot[0], st))
                    if step == "removed":
                        K.check(gid == "Unknown" and pk is not None and str(pk.itemId) == LEFT,
                                "D removed %s: a left-behind rod = Item.UNKNOWN server-side (%s), stack kept + still sent to the client as %s"
                                % (f, gid, pk.itemId if pk is not None else None))
                    elif step != "start1":                     # start1 loads the rods after this step (E)
                        K.check(gid == LEFT, "D %s %s: probe present -> the left-behind rod is the real rod item again (%s)" % (step, f, gid))
                    enc_i = json.loads(str(SIC.CODEC.encode(cont, EEI.EMPTY).toJson()))
                    enc_i = dict([("Id", "Simple")] + list(enc_i.items()))
                    same = json.dumps(enc_i.get("Items", {}).get(slot[0]), sort_keys=True) == json.dumps(items[slot[0]], sort_keys=True)
                    K.check(same, "D %s %s: the saved file still carries the rod in slot %s" % (step, f, slot[0]))
                    rods_left[f] = sorted((k, v.get("Id"), v.get("Quantity")) for k, v in enc_i.get("Items", {}).items())
                    d["Components"]["StorageInventory"]["Inventory"] = enc_i
                except Exception as e:
                    K.check(False, "D %s %s: the storage inventory decodes / encodes through SimpleItemContainer.CODEC: %s" % (step, f, str(e)[:200]))
        es = d["Components"].get("EntityStats")
        if es is None:
            K.notes.append("%s has no EntityStats" % f)
            continue
        try:
            m = ESM.CODEC.decode(BD.parse(json.dumps(es)), EEI.EMPTY)
        except Exception as e:
            K.check(False, "D %s: %s decodes through EntityStatMap.CODEC: %s" % (step, f, str(e)[:200]))
            continue
        m.update()                                             # what the engine does when the component is loaded / assets change
        k0 = int(Stat.get(m))
        unk = jfield(ESM, "unknown").get(m)
        in_unknown = unk is not None and unk.containsKey(STAT)
        if step == "start1":
            K.check(k0 == 0, "D start1 %s: the reel starts at 0 (InitialValue)" % f)
            K.check(int(Stat.set(m, 5)) == 5 and int(Stat.get(m)) == 5, "D start1 %s: RpStat.set 5 through the real setStatValue" % f)
        elif step == "start2":
            K.check(k0 == 5, "D start2 %s: the reel is still 5 after a restart (%d)" % (f, k0))
        elif step == "removed":
            K.check(k0 == -1 and int(Stat.set(m, 3)) == -1, "D removed %s: stat not loaded -> RpStat.get / set answer -1, no throw" % f)
            K.check(in_unknown and abs(float(unk.get(STAT).get()) - 5.0) < 1e-6,
                    "D removed %s: the engine keeps the saved reel in EntityStatMap.unknown (value 5)" % f)
        elif step == "readded":
            K.check(k0 == 5 and not in_unknown, "D readded %s: the probe is back -> the reel is 5 again (%d)" % (f, k0))
        enc = json.loads(str(ESM.CODEC.encode(m, EEI.EMPTY).toJson()))
        K.check(enc.get("Stats", {}).get(STAT, {}).get("Value") == 5.0, "D %s %s: the saved file carries %s = 5 (%s)"
                % (step, f, STAT, enc.get("Stats", {}).get(STAT)))
        d["Components"]["EntityStats"] = enc
        json.dump(d, open(p, "w", encoding="utf-8"), indent=1)
        seen[f] = dict((k, v) for k, v in enc.get("Stats", {}).items() if k != STAT)
    K.notes.append("D %s: %d live player copies" % (step, len(seen)))
    if step != "start1":
        K.save(others=seen, rods=rods_left)
        return

    # ---------------- E: the stat decoded vs GlidingActive; the items through Item's codec + toPacket
    o, g = E["ours"], E["glide"]
    K.check(o is not None and g is not None and float(o.getMax()) == 8.0 and float(o.getMin()) == float(g.getMin()) == 0.0
            and float(o.getInitialValue()) == float(g.getInitialValue()) == 0.0 and bool(o.isShared()) == bool(g.isShared()) is True
            and bool(o.getIgnoreInvulnerability()) == bool(g.getIgnoreInvulnerability()) is True
            and bool(jfield(ESTc, "hideFromTooltip").get(o)) and (o.getRegenerating() is None or len(o.getRegenerating()) == 0)
            and o.getMinValueEffects() is None and o.getMaxValueEffects() is None,
            "E: the decoded stat = GlidingActive's (initial 0, min 0, shared, ignoreInvulnerability) + max 8, hidden, no regen / effects")
    ITMc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    objs, ibad = [], []
    for iid in RODS:
        it, why = E["dec"](ITMc, iid, jz.read("Server/Item/Items/SkyyReelProbe/%s.json" % iid).decode("utf-8"))
        if it is None or why:
            ibad.append((iid, why))
        else:
            objs.append(it)
    K.check(not ibad, "E: the 8 rods decode through Item's codec - no unknown key, no validation failure: %s" % ibad[:3])
    K.check(bool(E["load"](ITMc, objs, "Skyy:0.1 SkyyReelProbe")), "E: the 8 rods load into the Item store")
    pbad = []
    for ti, it in enumerate(objs):
        d = json.loads(jz.read("Server/Item/Items/SkyyReelProbe/%s.json" % RODS[ti]).decode("utf-8"))
        try:
            pk = it.toPacket()
            ac = pk.itemAppearanceConditions
            arr = ac.get(JClass("java.lang.Integer")(idx)) if ac is not None else None
            got = [(float(c.condition.inclusiveMin), float(c.condition.inclusiveMax), str(c.conditionValueType), str(c.model), str(c.texture))
                   for c in arr] if arr is not None else None
            exp = [(float(k), float(k), "Absolute", c["Model"], c["Texture"]) for k, c in enumerate(d["ItemAppearanceConditions"][STAT])]
            if ac is None or ac.size() != 1 or got != exp:
                pbad.append((RODS[ti], got[:2] if got else ac))
            if int(it.getMaxStack()) != 1 or str(pk.model) != d["Model"] or str(pk.texture) != d["Texture"]:
                pbad.append((RODS[ti], "model / texture / max stack"))
        except Exception as e:
            pbad.append((RODS[ti], str(e)[:200]))
    K.check(not pbad, "E: Item.toPacket() -> the client gets 9 conditions under OUR stat index %d, [K, K] Absolute + the right model / texture: %s"
            % (idx, pbad[:2]))

    # ---------------- X: stand-ins + every code path
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    TY = dict((k, U.allocateInstance(CT.class_)) for k in ("player", "pref", "stats", "hotbar", "storage", "backpack", "combined"))
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EM.class_)
    jfield(EM, "instance").set(None, em)
    for fld, k in (("playerComponentType", "player"), ("hotbarInventoryComponentType", "hotbar"), ("storageInventoryComponentType", "storage"),
                   ("backpackInventoryComponentType", "backpack"), ("combinedInventoryComponentType", "combined")):
        jfield(EM, fld).set(em, TY[k])
    SM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    sm = U.allocateInstance(SM.class_)
    jfield(SM, "instance").set(None, sm)
    jfield(SM, "entityStatMapComponentType").set(sm, TY["stats"])
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    jfield(UNI, "playerRefComponentType").set(E["uni"], TY["pref"])
    INVC = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent")
    CTA = JArray(CT)
    jfield(INVC, "STORAGE_HOTBAR_BACKPACK").set(None, CTA([TY["storage"], TY["hotbar"], TY["backpack"]]))
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    K.check(PLA.getComponentType() == TY["player"] and PRc.getComponentType() == TY["pref"] and ESM.getComponentType() == TY["stats"]
            and JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar").getComponentType() == TY["hotbar"],
            "X: the engine's own getComponentType() calls resolve through the allocated modules")
    MS, MCH, FH = JClass(FAKE_PKG + ".MapStore"), JClass(FAKE_PKG + ".MapChunk"), JClass(FAKE_PKG + ".FakeHotbar")
    IHM, UUID = JClass("java.util.IdentityHashMap"), JClass("java.util.UUID")
    COMPS = IHM()
    st = U.allocateInstance(MS.class_)
    st.comps = COMPS
    ARCH = JClass("com.hypixel.hytale.component.Archetype")          # a real Archetype holding the three inventory types (getCombined asks)
    for i_, k_ in enumerate(("player", "pref", "stats", "hotbar", "storage", "backpack", "combined")):
        jfield(CT, "index").set(TY[k_], JInt(i_ + 1))
    arch = U.allocateInstance(ARCH.class_)
    jfield(ARCH, "componentTypes").set(arch, CTA([None] + [TY[k_] for k_ in ("player", "pref", "stats", "hotbar", "storage", "backpack")]))
    st.arch = arch
    REF = JClass("com.hypixel.hytale.component.Ref")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    HOT = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar")
    STO, BKP = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage"), JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Backpack")
    nref = [0]

    def mkplayer(name, n, stats=True, storage=36):
        r_ = U.allocateInstance(REF.class_)
        jfield(REF, "store").set(r_, st)
        nref[0] += 1
        jfield(REF, "index").set(r_, JInt(nref[0]))
        COMPS.put(r_, IHM())
        pr_ = U.allocateInstance(PRc.class_)
        jfield(PRc, "uuid").set(pr_, UUID.fromString("00000000-0000-0000-0000-%012x" % (0xa000 + n)))
        jfield(PRc, "username").set(pr_, name)
        hb = U.allocateInstance(FH.class_)
        jfield(INVC, "inventory").set(hb, HOT(JClass("java.lang.Short")(9 if storage else 0)).getInventory())   # a real hotbar container
        c_ = COMPS.get(r_)
        c_.put(TY["pref"], pr_)
        c_.put(TY["player"], U.allocateInstance(PLA.class_))
        c_.put(TY["hotbar"], hb)
        sm_ = None
        if stats:
            sm_ = ESM()
            sm_.update()
            c_.put(TY["stats"], sm_)
        c_.put(TY["storage"], STO(JClass("java.lang.Short")(storage)))
        c_.put(TY["backpack"], BKP(JClass("java.lang.Short")(0)))
        return {"ref": r_, "pr": pr_, "hb": hb, "sm": sm_}

    def hold(p, iid):
        p["hb"].item = IS(iid, 1) if iid else None
    SINK = JClass("java.util.ArrayList")()
    LOGc = JClass(PKG + "RpLog")
    LOGc.SINK = SINK

    def said():
        out = [str(x) for x in SINK]
        SINK.clear()
        return out
    Cmds, Logic, Sys = JClass(PKG + "RpCmds"), JClass(PKG + "RpLogic"), JClass(PKG + "RpSlotSys")
    OK_, ERR_ = str(Cmds.OK), str(Cmds.ERR)
    import skyyui as SUI
    K.check(OK_ == SUI.COLOR["success"] and ERR_ == SUI.COLOR["error"], "X: chat colours = the vanilla kit's success / error colours")

    # L: RpLogic
    K.check([int(Logic.rodIndex(i)) for i in RODS] == list(range(8)) and int(Logic.rodIndex("Weapon_Wand_Wood")) == -1
            and int(Logic.rodIndex(None)) == -1, "L: rodIndex")
    K.check([int(Logic.autoReel(i)) for i in range(8)] == [2, 3, 4, 5, 6, 7, 8, 1] and int(Logic.autoReel(-1)) == 0 and int(Logic.autoReel(8)) == 0,
            "L: auto table: Bamboo rod -> 2 (Copper reel) .. Mithril -> 8 (Onyxium), Onyxium -> 1 (Bamboo); not a rod -> 0")
    K.check([int(Logic.parseReel(s)) for s in ("0", " 8 ", "5", "9", "-1", "10", "", None, "a", "3x")] == [0, 8, 5, -1, -1, -1, -1, -1, -1, -1],
            "L: parseReel")
    K.check(str(Logic.reelName(0)) == "no reel" and str(Logic.reelName(4)) == "Thorium reel" and str(Logic.reelName(8)) == "Onyxium reel"
            and str(Logic.reelName(9)) == "reel 9", "L: reelName")
    K.check(int(Logic.toReel(JFloat(float("nan")))) == -1 and int(Logic.toReel(JFloat(4.6))) == 5, "L: toReel")
    K.check(str(Logic.heldText(None)) == "nothing" and str(Logic.heldText(RODS[4])) == "the Cobalt Fishing Rod"
            and "not a probe rod" in str(Logic.heldText("Tool_Pickaxe_Iron")) and Logic.rodName(9) is None, "L: heldText / rodName")

    A = mkplayer("Skyy", 1)
    NB = mkplayer("NoStats", 2, stats=False)
    FULL = mkplayer("Full", 3, storage=0)
    # RpStat
    K.check(int(Stat.get(A["sm"])) == 0 and int(Stat.set(A["sm"], 3)) == 3 and int(Stat.get(A["sm"])) == 3, "X: RpStat get / set 3")
    K.check(int(Stat.set(A["sm"], 12)) == 8 and int(Stat.set(A["sm"], -4)) == 0, "X: RpStat clamps 12 -> 8, -4 -> 0")
    K.check(int(Stat.get(None)) == -1 and int(Stat.set(None, 2)) == -1 and Stat.value(None) is None and Stat.map(st, NB["ref"]) is None,
            "X: RpStat without a stat map answers -1 / null")
    hold(A, RODS[4])
    K.check(str(Stat.heldId(st, A["ref"])) == RODS[4] and Stat.heldId(st, NB["ref"]) is None, "X: heldId")
    # status + help
    Cmds.status(A["pr"], st, A["ref"])
    s = said()
    K.check(len(s) == 1 and s[0].startswith("|Reel look: 0 (no reel). Auto mode: off. In your hand: the Cobalt Fishing Rod."), "X: status line %s" % s)
    Cmds.status(NB["pr"], st, NB["ref"])
    s = said()
    K.check(len(s) == 1 and s[0].startswith(ERR_ + "|The SkyyFishing_Reel stat is not loaded"), "X: status without the stat %s" % s)
    Cmds.help(A["pr"])
    s = said()
    K.check(len(s) == 4 and all(x.startswith("|") for x in s) and "/reelprobe give" in s[1] and "8 Onyxium" in s[2] and "auto" in s[3],
            "X: help lines %s" % s)
    # give: storage first, all 8; then a full inventory
    Cmds.give(A["pr"], st, A["ref"])
    s = said()
    sto = COMPS.get(A["ref"]).get(TY["storage"]).getInventory()
    got = [str(sto.getItemStack(JClass("java.lang.Short")(i)).getItemId()) for i in range(8) if sto.getItemStack(JClass("java.lang.Short")(i)) is not None]
    K.check(s == [OK_ + "|You got 8 fishing rods."] and got == RODS, "X: give -> 8 rods in storage slots 0-7 in tier order (%s / %s)" % (s, got))
    Cmds.give(FULL["pr"], st, FULL["ref"])
    s = said()
    K.check(len(s) == 1 and s[0].startswith(ERR_ + "|No room for the Bamboo, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium rods - nothing was dropped"),
            "X: give into a full inventory -> the 'no room' line, nothing dropped %s" % s)
    # setReel turns auto off
    Cmds.AUTO.put(A["pr"].getUuid(), JClass("java.lang.Boolean").TRUE)
    Cmds.setReel(A["pr"], st, A["ref"], 6)
    s = said()
    K.check(s == [OK_ + "|Your Cobalt Fishing Rod now shows the Adamantite reel (reel look 6). Auto mode is off."] and int(Stat.get(A["sm"])) == 6
            and not bool(Cmds.autoOn(A["pr"].getUuid())), "X: setReel 6 (auto turned off) %s" % s)
    hold(A, "Tool_Pickaxe_Iron")
    Cmds.setReel(A["pr"], st, A["ref"], 0)
    s = said()
    K.check(s == [OK_ + "|Any probe rod you hold now shows no reel (reel look 0)."], "X: setReel 0 with no rod in hand %s" % s)
    Cmds.setReel(NB["pr"], st, NB["ref"], 2)
    s = said()
    K.check(len(s) == 1 and s[0].startswith(ERR_ + "|Could not set"), "X: setReel without the stat %s" % s)
    # toggleAuto on (applies now) / off
    hold(A, RODS[0])
    Cmds.toggleAuto(A["pr"], st, A["ref"])
    s = said()
    K.check(len(s) == 2 and s[0].startswith(OK_ + "|Auto mode is on") and s[1] == "|Auto: your Bamboo Fishing Rod shows the Copper reel (reel look 2)."
            and int(Stat.get(A["sm"])) == 2 and bool(Cmds.autoOn(A["pr"].getUuid())), "X: auto on applies to the rod in hand %s" % s)
    # RpSlotSys: hotbar events
    EVc = JClass("com.hypixel.hytale.server.core.event.events.ecs.InventorySetActiveSlotEvent")
    chunk = U.allocateInstance(MCH.class_)
    chunk.ref = A["ref"]
    sysx = Sys()
    K.check(sysx.getQuery() == TY["player"], "X: RpSlotSys query = the Player component type")

    def scroll(p, iid, section=-1):
        chunk.ref = p["ref"]
        hold(p, iid)
        sysx.handle(0, chunk, st, None, EVc(section, 0, JByte(1)))
    seq = []
    for ti in range(8):
        scroll(A, RODS[ti])
        seq.append(int(Stat.get(A["sm"])))
    s = said()
    K.check(seq == [2, 3, 4, 5, 6, 7, 8, 1], "X: scrolling the 8 rods with auto on -> reels %s (want 2..8, 1)" % seq)
    K.check(len(s) == 7 and s[-1] == "|Auto: your Onyxium Fishing Rod shows the Bamboo reel (reel look 1).",
            "X: one chat line per changed reel (the Bamboo rod's 2 was already set): %s" % s[-2:])
    scroll(A, RODS[7])
    K.check(said() == [], "X: same reel again -> no chat line")
    scroll(A, "Tool_Pickaxe_Iron")
    K.check(int(Stat.get(A["sm"])) == 0 and said() == [], "X: a non-rod in hand -> reel 0, silent")
    scroll(A, None)
    K.check(int(Stat.get(A["sm"])) == 0, "X: empty hand -> 0")
    scroll(A, RODS[3], section=-8)
    K.check(int(Stat.get(A["sm"])) == 0 and said() == [], "X: a tools-section event is ignored")
    Cmds.run(A["ref"], st, A["pr"], " AUTO ")
    s = said()
    K.check(s == [OK_ + "|Auto mode is off. Your reel look stays where it is - /reelprobe 0-8 sets it."] and not bool(Cmds.autoOn(A["pr"].getUuid())),
            "X: run('AUTO') toggles off %s" % s)
    scroll(A, RODS[3])
    K.check(int(Stat.get(A["sm"])) == 0, "X: auto off -> hotbar events change nothing")
    Cmds.AUTO.put(A["pr"].getUuid(), JClass("java.lang.Boolean").TRUE)
    Cmds.AUTO.put(NB["pr"].getUuid(), JClass("java.lang.Boolean").TRUE)
    scroll(NB, RODS[3])
    K.check(said() == [], "X: auto on but no stat map -> nothing, no throw")
    A["hb"].boom = True
    Sys.FAILED_ONCE = False
    chunk.ref = A["ref"]
    sysx.handle(0, chunk, st, None, EVc(-1, 0, JByte(1)))
    K.check(not bool(Sys.FAILED_ONCE), "X: heldId swallows a broken hotbar (no hook failure)")
    sysx.handle(0, chunk, st, None, None)
    K.check(bool(Sys.FAILED_ONCE), "X: a broken event is caught and logged once")
    A["hb"].boom = False
    Cmds.AUTO.clear()
    # run: give / 0-8 / garbage
    Cmds.run(A["ref"], st, A["pr"], "7")
    s = said()
    K.check(int(Stat.get(A["sm"])) == 7 and len(s) == 1 and s[0].startswith(OK_), "X: run('7') %s" % s)
    Cmds.run(A["ref"], st, A["pr"], "nine")
    s = said()
    K.check(len(s) == 5 and s[0] == ERR_ + "|Unknown option 'nine'." and int(Stat.get(A["sm"])) == 7, "X: run('nine') -> error + help %s" % s[:1])
    Cmds.run(FULL["ref"], st, FULL["pr"], "give")
    K.check(len(said()) == 1, "X: run('give')")
    # the two commands' execute() through reflection with a real CommandContext (argValues filled the way the parser does)
    CTXc = JClass("com.hypixel.hytale.server.core.command.system.CommandContext")
    APC = JClass("com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand")
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    STc = JClass("com.hypixel.hytale.component.Store")
    cmd, cmd1 = JClass(PKG + "ReelProbeCmd")(), JClass(PKG + "ReelProbeArgCmd")()

    def execute(c, ctx, p):
        m_ = c.getClass().getDeclaredMethod("execute", CTXc.class_, STc.class_, REF.class_, PRc.class_, WLD.class_)
        m_.setAccessible(True)
        m_.invoke(c, JArray(JObject)([ctx, st, p["ref"], p["pr"], None]))
    execute(cmd, None, A)
    s = said()
    K.check(len(s) == 5 and s[0].startswith("|Reel look: 7 (Mithril reel)"), "X: /reelprobe -> status + help %s" % s[:1])
    ctx = U.allocateInstance(CTXc.class_)
    av = JClass("java.util.HashMap")()
    av.put(cmd1.whatArg, "4")
    jfield(CTXc, "argValues").set(ctx, av)
    execute(cmd1, ctx, A)
    K.check(int(Stat.get(A["sm"])) == 4 and len(said()) == 1, "X: /reelprobe 4 through ReelProbeArgCmd.execute + CommandContext.get")
    execute(cmd1, None, A)
    s = said()
    K.check(s == [ERR_ + "|Usage: /reelprobe <give, auto, 0-8>"], "X: ReelProbeArgCmd without a context -> usage line %s" % s)
    # plugin: shutdown clears auto; setup()'s calls in order (bytecode - setup needs a running server's registries)
    PLc = JClass(PKG + "SkyyReelProbePlugin")
    plg = U.allocateInstance(PLc.class_)
    Cmds.AUTO.put(A["pr"].getUuid(), JClass("java.lang.Boolean").TRUE)
    try:
        sd = PLc.class_.getDeclaredMethod("shutdown")
        sd.setAccessible(True)
        sd.invoke(plg, JArray(JObject)([]))
    except Exception as e:
        K.notes.append("plugin shutdown: super.shutdown() on an allocated plugin: %s" % str(e)[:120])
    K.check(Cmds.AUTO.isEmpty(), "X: plugin shutdown clears auto mode")
    K.save(others=seen, rods=rods_left)


def run_perm(out):
    """child P: permissions with the engine's own AbstractCommand code"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in ("ReelProbeCmd", "ReelProbeArgCmd"):
        try:
            c = JClass(PKG + cn)()
        except Exception as e:
            K.check(False, "P. construct %s: %s" % (cn, e))
            continue
        perm = c.getPermission()
        groups = fld.get(c)
        K.check(perm is not None and NODE in str(perm.getId() if hasattr(perm, "getId") else perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        K.check(groups is not None and len(groups) == 0, "P. %s permission groups empty (%s)" % (cn, groups))
        if cn == "ReelProbeCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            K.check(not leak, "P. getPermissionGroupsRecursive gives %s to no group (leak: %s)" % (NODE, leak))
            K.check("rprobe" in [str(a) for a in c.getAliases()] and str(c.getName()) == "reelprobe", "P. /reelprobe + alias /rprobe")
    K.save()


def run_bytecode(out):
    """child: setup()'s calls in their order (javassist reads the jar's class file)"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    cc = cp.get(PKG + "SkyyReelProbePlugin")
    mi = [m for m in cc.getClassFile2().getMethods() if str(m.getName()) == "setup"][0]
    cpool, it = mi.getConstPool(), mi.getCodeAttribute().iterator()
    calls = []
    while it.hasNext():
        p = it.next()
        op = it.byteAt(p)
        if op in (0xb6, 0xb7, 0xb8, 0xb9):
            i = it.u16bitAt(p + 1)
            tag = cpool.getTag(i)
            if tag == JClass("javassist.bytecode.ConstPool").CONST_InterfaceMethodref:
                calls.append(str(cpool.getInterfaceMethodrefName(i)))
            else:
                calls.append(str(cpool.getMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getMethodrefName(i)))
        elif op == 0xbb:
            calls.append("new " + str(cpool.getClassInfo(it.u16bitAt(p + 1))).rsplit(".", 1)[-1])
        elif op == 0xb3:
            calls.append("put " + str(cpool.getFieldrefName(it.u16bitAt(p + 1))))
    want = ["PluginBase.getLogger", "put LOG", "PluginBase.getCommandRegistry", "new ReelProbeCmd", "ReelProbeCmd.<init>",
            "CommandRegistry.registerCommand", "PluginBase.getEntityStoreRegistry", "new RpSlotSys", "RpSlotSys.<init>",
            "ComponentRegistryProxy.registerSystem", "RpStat.index"]
    pos, ok = 0, True
    for w in want:
        try:
            pos = calls.index(w, pos) + 1
        except ValueError:
            ok = False
            break
    K.check(ok and calls.count("ComponentRegistryProxy.registerSystem") == 1, "X: setup() = LOG, registerCommand(/reelprobe), ONE registerSystem(RpSlotSys), "
                                                                             "the stat index, the ready line: %s" % calls)
    K.save()


def run_audit(out):
    """child AA: the engine-access audit (copied from the SkyyClasses 0.1.12 harness, part AA)"""
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


def main():
    if "--mkfake" in sys.argv:
        run_mkfake(arg("--mkfake"))
        return
    if "--engine" in sys.argv:
        run_engine(arg("--engine"), arg("--out"))
        return
    if "--perm" in sys.argv:
        run_perm(arg("--out"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--out"))
        return
    if "--audit" in sys.argv:
        run_audit(arg("--out"))
        return
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        jz, az = part_static()
        part_art(jz, az)
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0 and os.path.isfile(os.path.join(FAKE_DIR, FAKE_PKG, "MapStore.class")), "F: the stand-ins were generated")
        n = copy_live_into(os.path.join(SCRATCH, "live"))
        print("D. %d live player files copied (read-only source %s)" % (n, LIVE))
        check(n > 0, "D: live player files found to copy (%s)" % LIVE)
        orig = dict((f, stats_of(os.path.join(SCRATCH, "live", f))) for f in os.listdir(os.path.join(SCRATCH, "live")) if f.endswith(".json"))
        res = {}
        for step in ("start1", "start2", "removed", "readded"):
            out = os.path.join(SCRATCH, "engine-%s.json" % step)
            child(env, "--engine", step, "--out", out)
            res[step] = take(out, "engine " + step)
        # every other stat value + modifier unchanged by the probe across the four starts
        for f, es in orig.items():
            before = dict((k, v) for k, v in es.get("Stats", {}).items())
            for step in ("start2", "readded"):
                after = (res.get(step) or {}).get("others", {}).get(f)
                if after is None:
                    check(False, "D %s: no result for %s" % (step, f))
                    continue
                bad = [k for k in set(before) | set(after) if k != STAT and json.dumps(before.get(k), sort_keys=True) != json.dumps(after.get(k), sort_keys=True)]
                check(not bad, "D %s %s: every other stat (value + modifiers) unchanged: %s" % (step, f, bad[:4]))
        # rods left behind: the storage inventory = the original slots + the one Cobalt rod, identical in start2 / removed / readded
        nrod = 0
        for f in orig:
            inv0 = json.load(open(os.path.join(LIVE, f), encoding="utf-8"))["Components"].get("StorageInventory", {}).get("Inventory", {})
            base = sorted((k, v.get("Id"), v.get("Quantity")) for k, v in inv0.get("Items", {}).items())
            got = [(res.get(s) or {}).get("rods", {}).get(f) for s in ("start2", "removed", "readded")]
            if all(g is None for g in got):
                continue
            nrod += 1
            exp = None
            if got[0] is not None:
                extra = [tuple(x) for x in got[0] if tuple(x) not in base]
                exp = sorted(base + extra) if len(extra) == 1 and extra[0][1:] == ("SkyyFishing_Rod_Cobalt", 1) else None
            check(exp is not None and all(g is not None and sorted(tuple(x) for x in g) == exp for g in got),
                  "D %s: storage = the original slots + exactly one left-behind rod, unchanged across start2 / removed / readded" % f)
        check(nrod > 0, "D: the left-behind rod check ran on at least one live player copy (%d)" % nrod)
        for label, flag in (("perm", "--perm"), ("bytecode", "--bytecode")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            child(env, flag, "--out", out)
            take(out, label)
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 300 and a["classes"] == len(CLASSES),
                  "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: control refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, 0 refused, control refused; caller-sensitive: %s"
                  % (a["refs"], a["classes"], a["caller_sensitive"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d ok, %d fail(s)" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
