"""Bare-JVM harness for SkyyAccessories 0.5.8 - THE NEW ACCESSORY BAG LOOK (tools/accessories_0_5_8_patch.py; Skyy 2026-10-08 "the
accessory bag is a little too over decorated.  but i love the bags.", "as drawn, violet. start the bag round"). Art only: derived from
test_skyyaccessories_0.5.7.py - every 0.5.7 check (I, K, X, E, H, L) runs again on the 0.5.8 jar; B now compares 0.5.7 -> 0.5.8; G and V
are new (V = today's SkyyArmory lesson: the ENGINE'S OWN ASSET VALIDATORS on the jar, in a second JVM).

    python SkyyAccessories/test_skyyaccessories_0.5.8.py [--jar <SkyyAccessories-0.5.8.jar>] [--old <SkyyAccessories-0.5.7.jar>]
                                                         [--coll <SkyyCollections-0.2.7.jar>] [--dir <scratch>] [--live <folder>] [--keep]

JVM 1 (the game's JRE, -Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath), each jar in its own
class loader (SkyyCollections 0.2.7 too, for the bridge section).
  A  every class of both jars loads, verifies and initialises
  B  0.5.7 -> 0.5.8: the same classes, each byte-identical or version constants only (no method changed); the jar files: the Accessory
     Bag's 3 art files added, exactly the Accessory Bag JSON (ONLY Model / Texture / Icon / IconProperties, = the generator manifest)
     and the manifest changed, every other file (the 64 booster JSONs + 44 icons of 0.5.7, server.lang, qualities, the tab icon)
     byte-identical
  G  THE BAG ART: tools/art/make_bags.py run fresh in memory -> the 3 files are byte-identical to it and to models-local/art/bags (the
     sheet Skyy approved) when that folder exists; texture = the manifest size, icon 64 x 64 RGBA, the model parses; no vanilla path
     replaced; P0: no Parallel with fewer than 2 entries in any server JSON of the jar
  I  THE 0.5.7 ICONS (unchanged checks; the bag icon is the one allowed other SkyyAccessories_ icon)
  K, E, X, H, L  the 0.5.7 / 0.5.6 checks, unchanged (L = START TWICE on a scratch COPY of the live Skyy_SkyyAccessories folder)
JVM 2 (V - the ENGINE ASSET VALIDATORS; the SkyySacks 0.7.14 harness section V): the real asset stores + interaction codecs, the
  CommonAssetRegistry with every Common/ file of Assets.zip and the jar, the vanilla pack loaded store by store (the server's
  AssetRegistryLoader.loadAssets0 path with the codec validators), the jar's OpenCustomUI pages registered like the plugin's setup(),
  then the jar as its own pack: no failed store, not one SEVERE / WARNING line; every jar item in the Item store; the Accessory Bag's
  look in the store, toPacket() works. NEGATIVE CONTROLS: a one-entry Parallel and an item whose Model / Texture / Icon file does not
  exist MUST each be refused (the validators really run).
Nothing outside the scratch folder is written (default tools/dev/scratch/bags01/acc-harness, deleted at the end unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, struct, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.5.8", "0.5.7"
PKG = "com.skyy.accessories."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


SCRATCH_ROOT = os.path.abspath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "bags01", "acc-harness")))
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
    check(set(new) == set(old), "B. the same classes: %s" % sorted(set(old) ^ set(new)))
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
        fo = sorted((str(f.getName()), str(f.getSignature())) for f in po.getDeclaredFields())
        fn = sorted((str(f.getName()), str(f.getSignature())) for f in pn.getDeclaredFields())
        check(fo == fn, "B. %s: fields changed: %s" % (short, sorted(set(fo) ^ set(fn))))
        mo, mn = methods(po), methods(pn)
        check(set(mo) == set(mn), "B. %s: methods added / gone: %s" % (short, sorted(set(mo) ^ set(mn))))
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and not vonly(mo[k], mn[k]))
        check(changed == [], "B. %s: 0.5.8 is art only, yet methods changed: %s" % (short, changed))
        kinds[short] = "version only (method level)"
    # the jar's other files (0.5.8: the Accessory Bag look only); the look = the generator's manifest (make_bags run in memory, like the build)
    gen = make_bags_in_memory()
    _m = json.loads(gen["manifest.json"].decode("utf-8"))["accessory_bag"]
    BAG_LOOK = {"Model": _m["model_path"][7:], "Texture": _m["texture_path"][7:], "Icon": _m["icon_path"][7:], "IconProperties": _m["icon_properties"]}
    fo_, fn_ = dict((k, v) for k, v in F["old"].items() if not k.endswith(".class")), dict((k, v) for k, v in F["new"].items() if not k.endswith(".class"))
    BAGP = "Server/Item/Items/Utility/Skyy_Accessory_Bag.json"
    BAG_ART = ["Common/Icons/ItemsGenerated/SkyyAccessories_Bag.png", "Common/Items/SkyyAccessories/SkyyAccessories_Bag.blockymodel",
               "Common/Items/SkyyAccessories/SkyyAccessories_Bag_Texture.png"]
    added_new = sorted(set(fn_) - set(fo_))
    check(not set(fo_) - set(fn_), "B. no file gone: %s" % sorted(set(fo_) - set(fn_)))
    check(added_new == BAG_ART, "B. added = exactly the Accessory Bag's 3 art files: %s" % added_new)
    diff = sorted(k for k in fo_ if k in fn_ and fo_[k] != fn_[k])
    check(diff == sorted([BAGP, "manifest.json"]), "B. changed files = the Accessory Bag JSON + the manifest: %s" % diff)
    jo, jn = json.loads(fo_[BAGP]), json.loads(fn_[BAGP])
    VK = ("Model", "Texture", "Icon", "IconProperties")
    vo, vn = dict((k, jo.pop(k)) for k in VK), dict((k, jn.pop(k)) for k in VK)
    check(jo == jn and vo["Model"] == "Items/Back/BackpackBig.blockymodel" and vn == BAG_LOOK,
          "B. the Accessory Bag JSON: only Model / Texture / Icon / IconProperties changed, to the generator manifest's look: %s" % vn)
    unchanged = [p for p in fo_ if p in fn_ and p not in diff]
    check("Server/Languages/en-US/server.lang" in unchanged and len(unchanged) == len(fo_) - len(diff),
          "B. every other file byte-identical (%d, server.lang included)" % len(unchanged))
    mo_, mn_ = json.loads(fo_["manifest.json"]), json.loads(fn_["manifest.json"])
    check(mn_["Version"] == VERSION and dict((k, v) for k, v in mo_.items() if k not in ("Version", "Name")) ==
          dict((k, v) for k, v in mn_.items() if k not in ("Version", "Name")), "B. manifest: only Version / Name")
    print("B. %d classes byte-identical; version only: %s; files: +3 bag art files, the bag JSON (look only), manifest; %d other files identical" % (
        sum(1 for v in kinds.values() if v == "identical"), sorted(k for k, v in kinds.items() if v != "identical"), len(unchanged)))
    # the 0.5.7 icon section (I) below reads the 0.5.7 icon set from the new jar (unchanged since 0.5.7)
    BOOST_RE = re.compile(r"^Server/Item/Items/Utility/Skyy_Talisman_(?!NightVision_)[A-Za-z]+_[A-Za-z0-9]+\.json$")
    items_changed = sorted(p for p in fn_ if BOOST_RE.match(p))
    added = sorted(p for p in fn_ if re.match(r"^Common/Icons/ItemsGenerated/SkyyAccessories_[A-Za-z]+_(Normal|Unique|Rare|Legendary)\.png$", p))
    icon_of_new = dict((os.path.basename(p)[:-5], json.loads(fn_[p])["Icon"]) for p in items_changed)
    check(len(items_changed) == 64 and len(added) == 44 and all(fo_.get(p) == fn_[p] for p in items_changed + added),
          "B. the 64 booster JSONs and 44 own icons are 0.5.7's, byte for byte")
    # G: the bag art = a fresh make_bags run (in memory) = models-local/art/bags
    check(all(fn_[p] == gen.get(p) for p in BAG_ART), "G. the 3 bag art files are byte-identical to a fresh tools/art/make_bags.py run")
    ml = os.path.join(ROOT, "models-local", "art", "bags")
    if os.path.isdir(ml):
        check(all(os.path.isfile(os.path.join(ml, *p.split("/"))) and open(os.path.join(ml, *p.split("/")), "rb").read() == fn_[p] for p in BAG_ART),
              "G. ... and to models-local/art/bags (the sheet Skyy approved)")
    man = json.loads(gen["manifest.json"].decode("utf-8"))["accessory_bag"]
    tw, th = struct.unpack(">II", fn_[BAG_ART[2]][16:24])
    iw, ih = struct.unpack(">II", fn_[BAG_ART[0]][16:24])
    mdl = json.loads(fn_[BAG_ART[1]])
    check([tw, th] == man["texture_size"] and (iw, ih) == (64, 64) and fn_[BAG_ART[0]][24:26] == b"\x08\x06" and mdl.get("nodes"),
          "G. texture %d x %d (manifest %s), icon 64 x 64 RGBA, the model parses with nodes" % (tw, th, man["texture_size"]))
    with zipfile.ZipFile(ASSETS_ZIP) as az:
        van = set(az.namelist())
    check(not [p for p in BAG_ART if p in van], "G. no bag art path replaces a vanilla file")
    shortp = []

    def walk(p, x):
        if isinstance(x, dict):
            if x.get("Type") == "Parallel" and len(x.get("Interactions") or []) < 2:
                shortp.append(p)
            for v in x.values():
                walk(p, v)
        elif isinstance(x, list):
            for v in x:
                walk(p, v)
    nj = 0
    for p, b in fn_.items():
        if p.startswith("Server/") and p.endswith(".json"):
            walk(p, json.loads(b))
            nj += 1
    check(not shortp and nj > 90, "G (P0). no Parallel with fewer than 2 entries in the jar's %d server JSON files: %s" % (nj, shortp[:3]))
    print("G. bag art = the generator (+ models-local), %d x %d texture, P0 clean (%d JSON files)" % (tw, th, nj))

    # ---------------- I. the icons
    import subprocess
    import skyyart as SA
    gen = os.path.join(SCRATCH, "gen")
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "art", "make_accessory_icons.py"), "--out", gen], env=dict(os.environ),
                       capture_output=True, text=True)
    check(r.returncode == 0, "I0 the generator runs: %s" % (r.stderr[-300:],))
    man = json.load(open(os.path.join(gen, "manifest.json"), encoding="utf8"))
    check(len(man) == 44 and len(set(m["icon_path"] for m in man)) == 44, "I1 the generator's manifest: 44 icons")
    gen_png = dict((m["icon_path"], open(os.path.join(gen, *m["icon_path"].split("/")), "rb").read()) for m in man)
    check(sorted(gen_png) == added, "I1 the jar's icon paths = the generator's: %s" % sorted(set(gen_png) ^ set(added))[:4])
    check(all(fn_.get(p) == b for p, b in gen_png.items()), "I2 every jar PNG byte-identical to a fresh generator run (deterministic, the build ships its art)")
    ml = os.path.join(ROOT, "models-local", "art", "accessories")
    if os.path.isdir(ml):
        same = [p for p, b in gen_png.items() if os.path.isfile(os.path.join(ml, *p.split("/"))) and open(os.path.join(ml, *p.split("/")), "rb").read() == b]
        check(len(same) == 44, "I2 ... and to models-local/art/accessories (the sheet Skyy saw): %d of 44" % len(same))
    else:
        print("note: no models-local/art/accessories - I2 models-local compare skipped")
    want = {}
    for m in man:
        for iid in [m["item"]] + m["legacy_ids"]:
            want[iid] = m["icon_path"][len("Common/"):]
    check(len(want) == 64, "I3 the manifest maps 64 ids (40 line + 4 Lantern + 20 legacy): %d" % len(want))
    check(want == icon_of_new, "I3 every booster JSON's Icon = the generator manifest's icon for that id: %s" %
          sorted(k for k in set(want) | set(icon_of_new) if want.get(k) != icon_of_new.get(k))[:6])
    lines_ = sorted(set(m["line"] for m in man))
    check(lines_ == sorted(["Health", "Stamina", "Mana", "Regeneration", "Speed", "Runic", "Stonehide", "Razorfang", "Brawler", "Feather", "Lantern"]),
          "I3 the 11 lines: %s" % lines_)
    fam_of = {"Health": "Vitality", "Stamina": "Endurance", "Mana": "Intelligence", "Regeneration": "Regeneration", "Speed": "Speed",
              "Runic": "MagicPower", "Stonehide": "Defense", "Razorfang": "Crit", "Brawler": "Strength", "Feather": "Feather", "Lantern": "Lantern"}
    wordid = ["", "Common", "Uncommon", "Rare", "Epic"]
    for m in man:
        f, t = fam_of[m["line"]], m["tier"]
        exp = ("Skyy_Talisman_%s_%s" % (f, wordid[t]) if f in ("Vitality", "Endurance", "Intelligence", "Regeneration", "Speed", "Lantern")
               else "Skyy_Talisman_%s_T%d" % (f, t))
        check(m["item"] == exp and m["rarity"] == ["", "Normal", "Unique", "Rare", "Legendary"][t] and
              m["icon_path"].endswith("_%s_%s.png" % (m["line"], m["rarity"])), "I3 %s %s -> %s" % (m["line"], m["rarity"], m["item"]))
    for iid, rel in icon_of_new.items():
        check("Common/" + rel in fn_, "I4 %s: Icon %s exists in the jar under Common/" % (iid, rel))
    good = 0
    for p in added:
        b = fn_[p]
        img = SA.png_decode(b)
        px = img.px
        ok = (img.w, img.h) == (64, 64) and b[24] == 8 and b[25] == 6
        ok = ok and all(px[k] <= px[k - (k % 4) + 3] for k in range(len(px)) if k % 4 != 3)
        ok = ok and all(px[(y * 64 + x) * 4 + 3] == 0 for y in range(64) for x in range(64) if x < 2 or y < 2 or x >= 62 or y >= 62)
        ok = ok and any(px[k] for k in range(3, len(px), 4))
        good += 1 if check(ok, "I5 %s: 64x64 RGBA8, premultiplied, 2 px clear margin, not empty" % p) else 0
    check(len(set(fn_[p] for p in added)) == 44, "I5 44 distinct icons")
    nonb = [p for p in fn_ if p.startswith("Server/Item/Items/") and p not in items_changed and p != BAGP]   # 0.5.8: the bag has its own icon
    check(all(not json.loads(fn_[p])["Icon"].startswith("Icons/ItemsGenerated/SkyyAccessories_") for p in nonb),
          "I6 no other item (bench accessories, bag, Omni, Night Vision) uses our icons")
    print("I. icons: %d PNGs ok, = a fresh generator run, mapped to %d ids" % (good, len(icon_of_new)))

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


# ============================================================================================================== G + V (0.5.8)
ASSETS_ZIP = os.path.join(os.environ.get("APPDATA", os.path.join(os.path.expanduser("~"), "AppData", "Roaming")), "Hytale", "install",
                          "release", "package", "game", "latest", "Assets.zip")


def make_bags_in_memory():
    """tools/art/make_bags.py run exactly like the build runs it: write() into a dict, clean_old() a no-op (nothing written to disk)"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("make_bags_harness", os.path.join(TOOLS, "art", "make_bags.py"))
    mb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mb)
    got = {}

    def _w(rel, data):
        got[rel] = bytes(data)
        return rel
    mb.write = _w
    mb.clean_old = lambda: None
    mb.main()
    return got


def run_v():
    import time, hashlib
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JString, JImplements, JOverride
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-XX:-UsePerfData", "-Xmx6g", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST], convertStrings=True)
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
    # a bare server + universe (the stores ask HytaleServer.get() / Universe.get())
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

    def reg_ilt(c, path, codec, unknown=False):
        b_ = HAS.builder(c.class_, ILT(ArrOf(c))).setPath(path).setCodec(codec).setKeyFunction(GetId()).setReplaceOnRemove(NoRep())
        if unknown:
            b_ = b_.setIsUnknown(IsUnknown())
        AR.register(b_.build())
    # the stores InteractionModule registers in the game (the SkyyArmory 0.1.10 harness pattern)
    reg_ilt(INTc, "Item/Interactions", INTc.CODEC, True)
    reg_ilt(ROOTc, "Item/RootInteractions", ROOTc.CODEC)
    AR.register(HAS.builder(UIc.class_, DAMc()).setPath("Item/Unarmed/Interactions").setCodec(UIc.CODEC).setKeyFunction(GetId()).build())
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
    check(len(regs) >= 70 and "Simple" in [a for a, b in regs] and "Parallel" in [a for a, b in regs],
          "V: the interaction Type codecs registered from InteractionModule.setup's bytecode (%d)" % len(regs))
    # the bag pages, the way the plugin's setup() registers them (OpenCustomUIInteraction.registerSimple -> PAGE_CODEC) before assets load
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
    zj = zipfile.ZipFile(JAR)
    pages = set()

    def pwalk(x):
        if isinstance(x, dict):
            if x.get("Type") == "OpenCustomUI" and isinstance(x.get("Page"), dict):
                pages.add(x["Page"]["Id"])
            for v in x.values():
                pwalk(v)
        elif isinstance(x, list):
            for v in x:
                pwalk(v)
    for n in zj.namelist():
        if n.startswith("Server/") and n.endswith(".json"):
            pwalk(json.loads(zj.read(n)))
    for pid in sorted(pages):
        OCUc.PAGE_CODEC.register(pid, CPSc.class_, BCc.builder(CPSc.class_, SupOf()).build())
    # the common assets (the CommonAssetModule's job in the game): every Common/ file of Assets.zip and of the jar, at its zip path
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
        """AssetRegistryLoader.loadAssets0's per-store step: loadAssetsFromDirectory(pack, <root>/Server/<store path>) in dependency order"""
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
    nv = add_common("Hytale:Hytale", ASSETS_ZIP, False)
    vfail, vrec = loadpack(ASSETS_ZIP, "Hytale:Hytale", True)
    print("V. vanilla pack loaded (%d common files, %.0f s; %d SEVERE lines from stores a bare JVM lacks codecs for - not ours)"
          % (nv, time.time() - t0, len([r for r in vrec if r[0] == "SEVERE"])))
    ITEM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    IPA = JClass("com.hypixel.hytale.server.core.asset.type.itemanimation.config.ItemPlayerAnimations")
    check(IPA.getAssetMap().getAsset("Block") is not None and ITEM.getAssetMap().getAssetMap().size() > 1000,
          "V: the vanilla Block set and the vanilla items (%d) are in the real stores" % ITEM.getAssetMap().getAssetMap().size())
    # ---- THE JAR
    pack_name = "Skyy:%s SkyyAccessories" % VERSION
    add_common(pack_name, JAR, True)
    fail, rec = loadpack(JAR, pack_name, False)
    bad = [r for r in rec if r[0] in ("SEVERE", "WARNING")]
    for r in bad[:12]:
        print("   V:", r[0], r[1][:500].replace(chr(10), " / "))
    check(not fail and not bad, "V: the %s jar loads into the real stores: no failed store (%s), no SEVERE / WARNING line (%d)" % (VERSION, fail, len(bad)))
    jar_items = sorted(os.path.basename(n)[:-5] for n in zj.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    in_store = sorted(str(k) for k in ITEM.getAssetMap().getKeysForPack(pack_name))
    check(in_store == jar_items, "V: every one of the jar's %d items is in the Item store from this pack (%d): %s"
          % (len(jar_items), len(in_store), sorted(set(jar_items) ^ set(in_store))[:4]))
    node = json.loads(zj.read("Server/Item/Items/Utility/Skyy_Accessory_Bag.json"))
    it = ITEM.getAssetMap().getAsset("Skyy_Accessory_Bag")
    vals = {"Model": str(it.getModel()), "Texture": str(jf(ITEM, "texture").get(it)), "Icon": str(jf(ITEM, "icon").get(it))}
    try:
        it.toPacket()
        pk = True
    except Exception as e:
        pk = str(e)[:150]
    check(all(vals[k] == node[k] for k in vals) and jf(ITEM, "animation").get(it) is None and pk is True,
          "V: the Accessory Bag in the store = the jar's Model / Texture / Icon, no item animation, toPacket() works: %s %s" % (vals, pk))
    print("V. %s loaded into the real asset stores: 0 failed stores, 0 SEVERE / WARNING; %d items; the Accessory Bag look in the store"
          % (VERSION, len(in_store)))
    # ---- NEGATIVE CONTROLS (one-file packs in scratch): the validators really run
    base = dict(node)
    base.pop("Recipe", None)
    base.pop("Interactions", None)

    def item_with(**kv):
        d = json.loads(json.dumps(base))
        d.update(kv)
        return json.dumps(d)
    ctl = [
        ("one-entry Parallel", "Server/Item/Interactions/SkyyTestCtl/SkyyTestCtl_Parallel.json",
         json.dumps({"Type": "Simple", "RunTime": 0.1, "Next": {"Type": "Parallel", "Interactions": [{"Interactions": [{"Type": "Simple", "RunTime": 0.1}]}]}}),
         "Array size is invalid", True),
        ("Model file missing", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Model.json", item_with(Model="Items/SkyyAccessories/SkyyTestCtl_NoSuch.blockymodel"),
         "SkyyTestCtl_NoSuch.blockymodel", True),
        ("Texture file missing", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Tex.json", item_with(Texture="Items/SkyyAccessories/SkyyTestCtl_NoSuchT.png"),
         "SkyyTestCtl_NoSuchT.png", True),
        ("Icon file missing", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Icon.json", item_with(Icon="Icons/ItemsGenerated/SkyyTestCtl_NoSuchI.png"),
         "SkyyTestCtl_NoSuchI.png", True),
    ]
    caught = {}
    for i, (what, path, text, needle, must) in enumerate(ctl):
        zp = os.path.join(SCRATCH, "v-ctl%d.jar" % i)
        with zipfile.ZipFile(zp, "w") as z:
            z.writestr(path, text)
        f_, r_ = loadpack(zp, "Skyy:test ctl%d" % i, False)
        hit = [r for r in r_ if r[0] in ("SEVERE", "WARNING") and needle in r[1]]
        caught[what] = ("refused (SEVERE)" if any(r[0] == "SEVERE" for r in hit) else "warned" if hit else "NOT caught") + (" + store failed" if f_ else "")
        if must:
            check(hit and any(r[0] == "SEVERE" for r in hit), "V CONTROL: %s must be refused by the engine validator: %s" % (what, caught[what]))
    print("V. negative controls: " + "; ".join("%s -> %s" % (k, v) for k, v in caught.items()))


def main():
    if "--child-v" in sys.argv:
        try:
            run_v()
        except Exception as e:
            import traceback
            traceback.print_exc()
            FAILS.append("V harness error: %s" % e)
        print("V: %d ok, %d fail(s)" % (OKS[0], len(FAILS)))
        for f in FAILS[:20]:
            print("  FAIL", f)
        return 1 if FAILS else 0
    for j in (JAR, OLD, COLL):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first (tools/accessories_0_5_8_patch.py + build_skyyaccessories_0.5.8.py; SkyyCollections 0.2.7)")
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
    import subprocess
    sys.stdout.flush()
    env = dict(os.environ)
    env.pop("JAVA_TOOL_OPTIONS", None)
    print("---- JVM 2: the engine asset validators (V)")
    sys.stdout.flush()
    rcv = subprocess.call([sys.executable, os.path.abspath(__file__), "--child-v"] + sys.argv[1:], env=env, cwd=ROOT)
    if rcv:
        FAILS.append("V (the engine asset validators) failed - see above")
    else:
        OKS[0] += 1
    print("SkyyAccessories %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:40]:
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP and "--child-v" not in sys.argv:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
