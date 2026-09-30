"""SkyySkills 0.4.8 - bare-JVM harness for the level-1 magic round (tools/skills_0_4_8_patch.py): spell costs / 5 (generated item
overrides), Base Mana by class (+ the one-time move of mana.magicBase / mana.magicClasses), the kit-weapon guard and the max Mana path.

    python SkyySkills/test_skyyskills_0.4.8.py [--jar <SkyySkills-0.4.8.jar>] [--old <SkyySkills-0.4.7.jar>] [--dir <scratch>]
                                               [--live <xp.properties>] [--keep]

Build first (python tools/skills_0_4_8_patch.py, then python SkyySkills/build_skyyskills_0.4.8.py). The old jar = the SET pin 0.4.7.
Child processes start fresh JVMs (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + ONE mod jar; TEMP / TMP /
java.io.tmpdir in the scratch folder). The live world is READ ONLY: its Skyy_SkyySkills/xp.properties is copied into the scratch folder and
only that copy is ever written.
  A  every class of the 0.4.8 jar AND of the 0.4.7 jar loads and initializes under -Xverify:all
  S  the jar's Server/Item/Items overrides against an INDEPENDENT scan of Assets.zip (read only): exactly the items whose InteractionVars
     carry a non-zero Mana number (32 today), each at the vanilla path; every cast check and drain = vanilla / 5 rounded half up, at least
     1, 0 stays 0; the JSON equals vanilla except those numbers (path by path); a check and its drain stay equal where vanilla had them
     equal; items with only 0 costs are not overridden; Parent: no overridden item has one and no Assets.zip item inherits from one
  X  the build script's own SPELL GEN block (exec'd here) on synthetic items: Parent inheritance (child and grandchild take the
     overridden parent's cost, a child with its own InteractionVars under a Mana parent is refused, a child with its own Mana cost is
     overridden itself), refused shapes (extra stat, unknown parent interaction, a cost outside InteractionVars, a fractional number,
     two checks), all-zero items left alone, the rounding, and spell_leaks (a vanilla default cost the item does not set, once each; a
     cost inherited through an interaction Parent - asset alias or inline -; an override that does not set its Parent's cost; the same
     interaction referenced directly after an override used it as a Parent)
  B  base Mana: no class / Warrior / Mage / Priest / an unknown class / lower case, the part switch, the stat type max, the Overall page
     line, the config rows (the mana.classBase table, the read-only spell.manaDivisor, no mana.magicBase / mana.magicClasses), the
     table's check= hook and the loader's problem report
  M  the migration on scratch COPIES: the exact live file (LF), a hand-edited pair, the live file in CRLF, reordered / spaced / 20.0,
     an unknown class, an empty class list, an edited 0.4.7 comment (kept + the stale note), no 0.4.7 comment (no note), a continued
     line (refused -> legacy table), a file that already has the table, a pre-0.4.6 file (block appended, table read in the same load),
     no file (fresh defaults); every case run twice (second start = no change) and the exact bytes compared with the expected rewrite
     (only the two lines changed, plus the untouched 0.4.7 comment -> the 0.4.8 default comment (review finding 2), line endings kept,
     no tmp file left); after a move ManaMig.keepCopy (setup, after CfgPub.start) puts the exact pre-move file into the kit's history
     (one .bak + its index line with who / summary), a second start adds nothing, no move = no history entry
  G  the guard: Mage 5 -> one WARN (once), 30 -> quiet, back to 5 -> WARN again, the live SkyyClasses kit through config:fn:SkyyClasses
     (a Priest spellbook kit), SkyyClasses' Class kits off (no WARN) and on again, the part switched off, and tick() timing (not before
     10 s, once, again on a config load / SkyyClasses epoch)
  K  the pack check (review finding 3): packReport texts (all active, another pack wins, not readable, missing ids, a long list cut),
     packCheck in the bare JVM (nothing readable, no exception), the retry timing (10 s apart, 6 tries, then one INFO), and packCheck on
     the ENGINE's own DefaultAssetMap.putAll behind a stand-in Item asset store (vanilla pack, then this jar, then a later pack: the
     last one loaded wins)
  Q  the build's SET-pin check (review finding 1) exec'd on tools/deploy_set.py (read only) with the SkyySkills pin as it is, bumped to
     0.4.8 and to 0.4.9: it passes every time (no fixed SkyySkills version asserted)
  P  max Mana on the ENGINE's EntityStatMap / EntityStatValue (mock asset store): Mage 30 with no refill, Warrior clamps to 10, back to
     Mage keeps 10 (no free refill), a relog while the class is not published yet holds the modifier (no dip)
  F  class bytes 0.4.7 vs 0.4.8: only the Mana classes changed (OverallCfg, Overall, SkillKit, SkillTick, SkyySkillsPlugin + the version /
     default-text carriers SkillCfg, CfgRows, CfgFn), ManaCost / ManaMig / ManaGuard are new, the three page classes and everything else
     byte-identical; manifest: Version / Name / Description / IncludesAssetPack only
Nothing is deployed. Default scratch folder: tools/dev/scratch/skills048/harness (deleted at the end unless --keep; --dir must be a folder
INSIDE tools/dev/scratch/). Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, copy, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.4.8", "0.4.7"
PKG = "com.skyy.skills."
SCRIPT = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
DIV = 5
# the 0.4.6 / 0.4.7 default comment above the old pair, and the 0.4.8 default comment the move puts in its place (review finding 2)
OLD_DOC = ["# Base Mana: every player's max Mana starts at mana.base; players whose class is listed in mana.magicClasses start at mana.magicBase",
           "# instead (their base is that number, not mana.base plus it). Vanilla max Mana is 0; Mana refills by itself (+1 every 0.2 s after",
           "# 6 s without taking damage)."]
NEW_DOC = ["# Base Mana: every player's max Mana starts at mana.base. A class listed below (Base Mana by class, one line per class:",
           "# mana.classBase.<Class>=<Mana>) starts at its own number instead - that number IS its base, not mana.base plus it (SkyySkills",
           "# 0.4.8, replaced mana.magicBase / mana.magicClasses). Vanilla max Mana is 0; Mana refills by itself (+1 every 0.2 s after 6 s",
           "# without taking damage). Spells cost the vanilla Mana / 5 (wand 5, staff 10, spellbook 20 - fixed in the jar)."]
STALE = "# (other comments in this file that name mana.magicBase / mana.magicClasses describe those old keys - 0.4.8 no longer reads them)"
DOC_LF = ("\n".join(OLD_DOC) + "\n").encode("latin-1")
DOC_EDIT = (b"# 6 s without taking damage).\n", b"# 6 s without taking damage). Edited by an admin.\n")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills048", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyySkills-%s.jar" % OLD_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills", "xp.properties")))
ASSETS = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
KEEP = "--keep" in sys.argv
FAILS, OKS, GUARD_OK = [], [0], [False]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _jvm_start(cp):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR] + list(cp), convertStrings=True)
    return B


# ============================================================================================ child: the javassist stand-in asset store
def run_mkfake(out_dir):
    """EntityStatType.getAssetStore() needs a non-null AssetStore; AssetStore is abstract and HytaleAssetStore's <clinit> needs the server
    options, so a bare subclass (never constructed: allocated with Unsafe) is generated here and put on the P child's classpath."""
    import jpype
    from jpype import JClass
    import skyybuild as B
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", classpath=[B.JAVASSIST], convertStrings=True)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    c = cp.makeClass("skyytest.FakeStore")
    c.setSuperclass(cp.get("com.hypixel.hytale.assetstore.AssetStore"))
    c.writeFile(out_dir)


# ============================================================================================ child: load + functional tests
def run_child(jar, out, full, fake):
    import jpype
    from jpype import JClass, JImplements, JOverride
    _jvm_start([jar] + ([fake] if full else []))
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    loaded, fails = 0, []
    for n in names:
        try:
            Cls.forName(n, True, loader)
            loaded += 1
        except Exception as e:
            fails.append("%s: %s" % (n, e))
    res = {"jar": jar, "classes": len(names), "loaded": loaded, "load_fails": fails, "checks": [], "data": {}}
    if fails or not full:
        json.dump(res, open(out, "w"), indent=1)
        return
    C = res["checks"]
    D = res["data"]

    def ck(ok, what):
        C.append([bool(ok), what])

    Paths, JStr = JClass("java.nio.file.Paths"), JClass("java.lang.String")
    Props, UUID = JClass("java.util.Properties"), JClass("java.util.UUID")
    Arr = JClass("java.lang.reflect.Array")
    Float, Integer = JClass("java.lang.Float"), JClass("java.lang.Integer")
    Cfg, OCfg, Ovl = JClass(PKG + "SkillCfg"), JClass(PKG + "OverallCfg"), JClass(PKG + "Overall")
    Mig, Guard, Cost = JClass(PKG + "ManaMig"), JClass(PKG + "ManaGuard"), JClass(PKG + "ManaCost")
    Store, Perks, Kit, Rows = JClass(PKG + "SkillStore"), JClass(PKG + "Perks"), JClass(PKG + "SkillKit"), JClass(PKG + "CfgRows")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def path(p):
        return Paths.get(p, Arr.newInstance(JStr.class_, 0))

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    def props(d):
        p = Props()
        for k, v in d.items():
            p.setProperty(k, v)
        return p

    @JImplements("java.util.function.Function")
    class Const(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            return self.v

    @JImplements("java.util.function.Function")
    class KitFn(object):
        def __init__(self, kits):
            self.kits = kits

        @JOverride
        def apply(self, o):
            try:
                if str(o[0]) == "get" and str(o[1]) == "kits.enabled":
                    return self.kits.get("__on__")
                if str(o[0]) == "get" and str(o[1]).startswith("kit."):
                    return self.kits.get(str(o[1])[4:])
            except Exception:
                return None
            return None

    bridge = Store.bridge()
    work = os.path.join(SCRATCH, "child")
    os.makedirs(work, exist_ok=True)
    Store.DIR = path(os.path.join(work, "players"))
    u = UUID(0x5117, 8)
    key = u.toString()
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")

    def mkpr():
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", u)
        setf(pr, PRef, "username", "Skyy")
        return pr

    # ---------------------------------------------------------------- M: the migration on scratch copies
    Hist = JClass(PKG + "CfgHist")

    def hist_of(home):
        # the kit's history folder the way CfgPub.start sets it up (CfgRows.HOME = <mods>/Skyy_SkyySkills, CfgHist.init)
        Rows.HOME = path(home)
        Hist.init()
        hd = os.path.join(home, "config-history")
        return hd

    def hist_files(hd):
        if not os.path.isdir(hd):
            return {}
        return dict((n, open(os.path.join(hd, n), "rb").read().decode("latin-1")) for n in sorted(os.listdir(hd)))

    def mig_case(name, data):
        d = os.path.join(work, "mig-" + name)
        os.makedirs(d, exist_ok=True)
        f = os.path.join(d, "xp.properties")
        if data is not None:
            open(f, "wb").write(data)
        Cfg.FILE = path(f)
        Hist.DIR = None                     # the kit has not started yet when ManaMig.run runs (setup order)
        r1 = [str(x) for x in Mig.run()]
        b1 = open(f, "rb").read() if os.path.exists(f) else None
        Cfg.load()
        t1 = [str(OCfg.tableText()), bool(OCfg.LEGACY), str(OCfg.WARNED), float(OCfg.baseFor("Mage")), float(OCfg.baseFor("Priest")),
              float(OCfg.baseFor("Warrior"))]
        hd = hist_of(os.path.join(work, "home-" + name, "Skyy_SkyySkills"))   # then CfgPub.start, then ManaMig.keepCopy
        k1 = str(Mig.keepCopy())
        h1 = hist_files(hd)
        b2 = open(f, "rb").read()
        Hist.DIR = None
        r2 = [str(x) for x in Mig.run()]
        b3 = open(f, "rb").read()
        Cfg.load()
        hist_of(os.path.join(work, "home-" + name, "Skyy_SkyySkills"))
        k2 = str(Mig.keepCopy())
        h2 = hist_files(hd)
        b4 = open(f, "rb").read()
        return {"r1": r1, "r2": r2, "t1": t1, "b1": None if b1 is None else b1.decode("latin-1"), "b2": b2.decode("latin-1"),
                "b3": b3.decode("latin-1"), "b4": b4.decode("latin-1"), "files": sorted(os.listdir(d)), "k1": k1, "k2": k2,
                "h1": h1, "h2": h2}
    live = open(os.path.join(SCRATCH, "live-xp.properties"), "rb").read()
    D["mig"] = {}
    D["mig"]["live"] = mig_case("live", live)
    D["mig"]["hand"] = mig_case("hand", live.replace(b"mana.magicBase=20\n", b"mana.magicBase=25\n")
                                .replace(b"mana.magicClasses=Mage,Priest\n", b"mana.magicClasses=Mage\n"))
    D["mig"]["crlf"] = mig_case("crlf", live.replace(b"\n", b"\r\n"))
    D["mig"]["spaced"] = mig_case("spaced", live.replace(b"mana.magicBase=20\n", b"  mana.magicBase : 20.0  \n")
                                  .replace(b"mana.magicClasses=Mage,Priest\n", b"mana.magicClasses = priest, MAGE\n"))
    D["mig"]["druid"] = mig_case("druid", live.replace(b"mana.magicClasses=Mage,Priest\n", b"mana.magicClasses=Mage,Druid\n"))
    D["mig"]["empty"] = mig_case("empty", live.replace(b"mana.magicClasses=Mage,Priest\n", b"mana.magicClasses=\n"))
    D["mig"]["note"] = mig_case("note", live.replace(DOC_EDIT[0], DOC_EDIT[1]))
    D["mig"]["nodoc"] = mig_case("nodoc", live.replace(DOC_LF, b""))
    D["mig"]["cont"] = mig_case("cont", live.replace(b"mana.magicClasses=Mage,Priest\n", b"mana.magicClasses=Mage,\\\n    Priest\n"))
    D["mig"]["both"] = mig_case("both", live.replace(b"mana.base=10\n", b"mana.base=10\nmana.classBase.Priest=12\n"))
    D["mig"]["old"] = mig_case("old", b"# a SkyySkills 0.4.5 file\nmultiplier=1.0\n")
    D["mig"]["fresh"] = mig_case("fresh", None)

    # ---------------------------------------------------------------- B: base Mana per class (after the fresh defaults were read)
    Cfg.FILE = path(os.path.join(work, "mig-fresh", "xp.properties"))
    Cfg.load()
    b = {}
    for cls in (None, "Warrior", "Mage", "Priest", "Druid", "mage", "Archer", "Berserker"):
        if cls is None:
            bridge.remove("profile:class:" + key)
        else:
            bridge.put("profile:class:" + key, cls)
        b[str(cls)] = [float(Ovl.baseTarget(u)), float(Ovl.baseMana(u, jpype.JFloat(5.0))), [str(x) for x in Ovl.nowLines(u, 0)]]
    D["base"] = b
    OCfg.MANA_ON = False
    bridge.put("profile:class:" + key, "Mage")
    D["base_off"] = [float(Ovl.baseTarget(u)), [str(x) for x in Ovl.nowLines(u, 0)]]
    OCfg.MANA_ON = True
    bridge.remove("profile:class:" + key)
    D["text"] = str(OCfg.text())
    D["hook"] = [None if OCfg.checkClassBase(k, v) is None else str(OCfg.checkClassBase(k, v)) for k, v in
                 (("mana.classBase[Mage]", "30"), ("mana.classBase[mage]", "30"), ("mana.classBase[Druid]", "30"), ("mana.classBase[Druid]", None),
                  ("mana.classBase[Shaman]", "0"))]
    OCfg.WARNED = ""
    OCfg.read(props({"mana.classBase.Druid": "30", "mana.classBase.mage": "40", "mana.classBase.Mage": "30", "mana.classBase.Priest": "abc",
                     "mana.classBase.Archer": "99999"}))
    D["problems"] = [str(OCfg.tableText()), str(OCfg.WARNED), float(OCfg.baseFor("Priest")), float(OCfg.baseFor("Archer"))]
    rows = dict((str(Rows.KEYS[i]), [str(Rows.TYPES[i]), str(Rows.FLAGS[i]), str(Rows.DEFS[i]), str(Rows.OPTS[i]), str(Rows.LABELS[i]),
                                     str(Rows.MINS[i]), str(Rows.MAXS[i]), str(Rows.CATS[i])]) for i in range(len(Rows.KEYS)))
    D["rows"] = {"n": len(Rows.KEYS), "classBase": rows.get("mana.classBase"), "div": rows.get("spell.manaDivisor"),
                 "old": [k for k in ("mana.magicBase", "mana.magicClasses") if k in rows], "kit": str(Rows.KIT)}
    D["customGet"] = str(Kit.customGet("spell.manaDivisor"))
    D["cost"] = {"div": int(Cost.DIVISOR), "n": int(Cost.N), "ids": [str(x) for x in Cost.IDS], "cost": [int(x) for x in Cost.COST],
                 "drain": [int(x) for x in Cost.DRAIN], "old": [int(x) for x in Cost.OLD], "old_drain": [int(x) for x in Cost.OLD_DRAIN],
                 "staff": int(Cost.costOf("Weapon_Staff_Wood")), "wand": int(Cost.costOf("Weapon_Wand_Wood")), "none": int(Cost.costOf("Weapon_Sword_Crude"))}

    # ---------------------------------------------------------------- G: the kit-weapon guard
    def greset():
        Guard.WARNED.clear()
        Guard.LAST = ""

    def gread(d):
        base = {"mana.base.enabled": "true", "mana.base": "10"}
        base.update(d)
        OCfg.read(props(base))

    def grun():
        return [str(x) for x in Guard.run()]
    bridge.remove("config:fn:SkyyClasses")
    bridge.remove("config:epoch:SkyyClasses")
    g = {}
    greset()
    gread({"mana.classBase.Mage": "5", "mana.classBase.Priest": "30"})
    g["mage5"] = grun()
    g["mage5_again"] = grun()
    gread({"mana.classBase.Mage": "30", "mana.classBase.Priest": "30"})
    g["mage30"] = grun()
    g["mage30_again"] = grun()
    gread({"mana.classBase.Mage": "5", "mana.classBase.Priest": "30"})
    g["mage5_back"] = grun()
    greset()
    bridge.put("config:fn:SkyyClasses", KitFn({"Mage": "Weapon_Staff_Wood:1", "Priest": "Weapon_Spellbook_Fire:1,Weapon_Wand_Wood:1",
                                               "Warrior": "Weapon_Sword_Crude:1", "Archer": "Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64"}))
    gread({"mana.classBase.Mage": "30", "mana.classBase.Priest": "10"})
    g["live_priest10"] = grun()
    # SkyyClasses' Class kits switched off: nothing to check (no WARN even for Mage 5); switched on again: the WARN comes back
    greset()
    bridge.put("config:fn:SkyyClasses", KitFn({"Mage": "Weapon_Staff_Wood:1", "Priest": "Weapon_Spellbook_Fire:1", "__on__": "false"}))
    gread({"mana.classBase.Mage": "5", "mana.classBase.Priest": "30"})
    g["kits_off"] = grun()
    g["kits_off_again"] = grun()
    bridge.put("config:fn:SkyyClasses", KitFn({"Mage": "Weapon_Staff_Wood:1", "Priest": "Weapon_Spellbook_Fire:1", "__on__": "true"}))
    g["kits_on"] = grun()
    bridge.remove("config:fn:SkyyClasses")     # back to the built-in kit table for the rest
    greset()
    gread({"mana.base.enabled": "false", "mana.classBase.Mage": "30", "mana.classBase.Priest": "30"})
    g["off"] = grun()
    # tick timing
    greset()
    gread({"mana.classBase.Mage": "30", "mana.classBase.Priest": "30"})
    Guard.STARTED = False
    Guard.EPOCH = -2
    OCfg.GUARD_DIRTY = True
    t = []
    Guard.tick(9)
    t.append([bool(Guard.STARTED), str(Guard.LAST)])
    Guard.tick(10)
    t.append([bool(Guard.STARTED), bool(OCfg.GUARD_DIRTY), str(Guard.LAST)])
    Guard.LAST = "x"
    Guard.tick(11)
    t.append(str(Guard.LAST))                 # nothing changed -> not run (LAST stays "x")
    OCfg.GUARD_DIRTY = True
    Guard.tick(12)
    t.append(str(Guard.LAST))                 # config load -> run (LAST = the summary again)
    Guard.LAST = "y"
    bridge.put("config:epoch:SkyyClasses", JClass("java.lang.Long")(7))
    Guard.tick(13)
    t.append([str(Guard.LAST), int(Guard.EPOCH)])   # SkyyClasses config changed -> run
    g["tick"] = t
    D["guard"] = g
    bridge.remove("config:fn:SkyyClasses")
    bridge.remove("config:epoch:SkyyClasses")

    # ---------------------------------------------------------------- K: the pack check (review finding 3)
    JSA = jpype.JArray(JStr)
    AS_ = JClass("com.hypixel.hytale.assetstore.AssetStore")
    Fake_ = JClass("skyytest.FakeStore")
    ITEM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    ids = [str(x) for x in Cost.IDS]
    PKs = str(Guard.PACK)
    kk = {"pack": PKs, "ids": ids}

    def prep(lst):
        return [str(x) for x in Guard.packReport(None if lst is None else JSA(lst))]
    kk["all"] = prep([PKs] * len(ids))
    two = [PKs] * len(ids)
    two[0], two[5] = "Hytale:Hytale", "Other:Mod"
    kk["two"] = prep(two)
    kk["none"] = prep([None] * len(ids))
    kk["null"] = prep(None)
    ms = [PKs] * len(ids)
    ms[1], ms[2] = None, None
    kk["miss"] = prep(ms)
    kk["many"] = prep(["Other:Mod"] * 10 + [PKs] * (len(ids) - 10))
    kk["bare"] = [str(x) for x in Guard.packCheck()]           # no item asset store in a bare JVM
    Guard.PACK_DONE, Guard.PACK_TRIES, Guard.PACK_LAST = False, 0, ""
    tt_ = []
    for n in (9, 10, 11, 19, 20, 25):
        Guard.tick(n)
        tt_.append(int(Guard.PACK_TRIES))
    for n in (30, 40, 50, 60):
        Guard.tick(n)
    tt_.append([int(Guard.PACK_TRIES), bool(Guard.PACK_DONE), str(Guard.PACK_LAST)])
    Guard.tick(70)
    tt_.append(int(Guard.PACK_TRIES))
    kk["tick"] = tt_
    # the ENGINE's DefaultAssetMap: putAll per pack in load order (vanilla, this jar, a later pack), behind a stand-in Item asset store
    codec = jpype.JProxy("com.hypixel.hytale.assetstore.codec.AssetCodec", dict={"getData": lambda a: None})
    putm = DAM.class_.getDeclaredMethod("putAll", JStr.class_, JClass("com.hypixel.hytale.assetstore.codec.AssetCodec").class_,
                                        JClass("java.util.Map").class_, JClass("java.util.Map").class_, JClass("java.util.Map").class_)
    putm.setAccessible(True)
    HM = JClass("java.util.HashMap")

    def engine(loads):
        dm = DAM()
        for pk, keys in loads:
            assets, paths = HM(), HM()
            for x in keys:
                assets.put(x, U.allocateInstance(ITEM.class_))
                paths.put(x, path(os.path.join(work, "packs", pk.replace(":", "_").replace(" ", "_"), x + ".json")))
            putm.invoke(dm, pk, codec, assets, paths, HM())
        st2 = U.allocateInstance(Fake_.class_)
        setf(st2, AS_, "assetMap", dm)
        setf(None, ITEM, "ASSET_STORE", st2)
        r = [str(x) for x in Guard.packCheck()] + [str(dm.getAssetPack(ids[0])), str(dm.getAssetPack(ids[1])), str(dm.getAssetPack(ids[3]))]
        setf(None, ITEM, "ASSET_STORE", None)
        return r
    kk["engine_ok"] = engine([("Hytale:Hytale", ids + ["Weapon_Sword_Crude"]), (PKs, ids)])
    kk["engine_clash"] = engine([("Hytale:Hytale", ids + ["Weapon_Sword_Crude"]), (PKs, ids[1:]), ("Other:Mod", [ids[3]])])
    D["pack"] = kk

    # ---------------------------------------------------------------- P: max Mana on the engine's own stat classes
    EST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    ESV = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    Fake = JClass("skyytest.FakeStore")

    @JImplements("java.util.function.IntFunction")
    class NewArr(object):
        @JOverride
        def apply(self, n):
            return Arr.newInstance(EST.class_, n)
    snames, smax = ["Health", "Oxygen", "Stamina", "Mana"], [100.0, 100.0, 10.0, 0.0]
    types = Arr.newInstance(EST.class_, len(snames))
    for i in range(len(snames)):
        tt = U.allocateInstance(EST.class_)
        setf(tt, EST, "id", snames[i])
        setf(tt, EST, "min", Float(0.0))
        setf(tt, EST, "max", Float(smax[i]))
        types[i] = tt
    amap = ILT(NewArr())
    setf(amap, ILT, "array", types)
    st = U.allocateInstance(Fake.class_)
    setf(st, AS, "assetMap", amap)
    setf(None, EST, "ASSET_STORE", st)
    for fld, idx in (("HEALTH", 0), ("OXYGEN", 1), ("STAMINA", 2), ("MANA", 3)):
        setf(None, DST, fld, Integer(idx))
    m = ESM()
    vals = Arr.newInstance(ESV.class_, len(snames))
    for i in range(len(snames)):
        v = U.allocateInstance(ESV.class_)
        setf(v, ESV, "id", snames[i])
        setf(v, ESV, "index", Integer(i))
        setf(v, ESV, "value", Float(smax[i]))
        setf(v, ESV, "min", Float(0.0))
        setf(v, ESV, "max", Float(smax[i]))
        vals[i] = v
    setf(m, ESM, "values", vals)
    Cfg.FILE = path(os.path.join(work, "mig-fresh", "xp.properties"))
    Cfg.load()
    bridge.remove("class:fn:allowed")
    pr = mkpr()
    p = []

    def mana():
        mv = m.get(3)
        return [float(mv.getMax()), float(mv.get())]
    bridge.put("profile:class:" + key, "Mage")
    Perks.ovl(u, pr, None, None, m)
    p.append(["Mage first second (value 0 = a new player)", mana()])
    m.setStatValue(3, 30.0)
    p.append(["regen filled it", mana()])
    Perks.ovl(u, pr, None, None, m)
    p.append(["Mage steady second", mana()])
    bridge.put("profile:class:" + key, "Warrior")
    Perks.ovl(u, pr, None, None, m)
    p.append(["switched to a Warrior profile", mana()])
    bridge.put("profile:class:" + key, "Mage")
    Perks.ovl(u, pr, None, None, m)
    p.append(["back to the Mage profile", mana()])
    m.setStatValue(3, 22.0)
    # relog: a new PlayerRef, SkyyClasses installed, no class published yet -> the 0.4.6 hold writes nothing
    bridge.put("class:fn:allowed", Const(True))
    bridge.remove("profile:class:" + key)
    pr2 = mkpr()
    Perks.ovl(u, pr2, None, None, m)
    p.append(["relog, class not published yet (hold)", mana()])
    bridge.put("profile:class:" + key, "Mage")
    Perks.ovl(u, pr2, None, None, m)
    p.append(["class published (Mage)", mana()])
    bridge.remove("class:fn:allowed")
    D["perks"] = p
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: bytecode method compare (javassist)
def version_only(a, b):
    la, lb = a.split(chr(10)), b.split(chr(10))
    return len(la) == len(lb) and all(x == y or x.replace(OLD_VERSION, VERSION, 1) == y for x, y in zip(la, lb))


def run_bytecode(old, new, out):
    import skyybuild as B
    from jpype import JClass
    _jvm_start([B.JAVASSIST])
    ClassPool, BAIS = JClass("javassist.ClassPool"), JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def listing(pool, data):
        cc = pool.makeClass(BAIS(data))
        ms = {}
        behaviors = list(cc.getDeclaredBehaviors())
        if cc.getClassInitializer() is not None:
            behaviors.append(cc.getClassInitializer())
        for mm in behaviors:
            k = "%s%s" % (mm.getName(), mm.getSignature())
            if mm.getMethodInfo().getCodeAttribute() is None:
                ms[k] = ""
                continue
            it = mm.getMethodInfo().getCodeAttribute().iterator()
            cpool = mm.getMethodInfo().getConstPool()
            lines = []
            while it.hasNext():
                ln = str(IP.instructionString(it, it.next(), cpool))
                ln = re.sub(r"#\d+ = ", "", ln).replace("ldc_w ", "ldc ")
                ln = re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln)
                lines.append(ln)
            ms[k] = "\n".join(lines)
        fields = sorted("%s %s" % (f.getName(), f.getSignature()) for f in list(cc.getDeclaredFields()))
        return ms, fields

    zo, zn = zipfile.ZipFile(old), zipfile.ZipFile(new)
    res = {}
    for n in sorted(set(zo.namelist()) & set(zn.namelist())):
        if not n.endswith(".class"):
            continue
        a, b = zo.read(n), zn.read(n)
        if a == b:
            continue
        mo, fo = listing(ClassPool(False), a)
        mn, fn = listing(ClassPool(False), b)
        changed = sorted(k for k in set(mo) & set(mn) if mo[k] != mn[k])
        res[n] = {"changed": changed, "gone": sorted(set(mo) - set(mn)), "new": sorted(set(mn) - set(mo)), "fields_same": fo == fn,
                  "fields_gone": sorted(set(fo) - set(fn)), "fields_new": sorted(set(fn) - set(fo)),
                  "version_only": all(version_only(mo[k], mn[k]) for k in changed)}
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent: S + X (Python only)
def mana_entries(d):
    """[(var, index, field, value)] of an item's InteractionVars Mana numbers (independent of the build's scanner)"""
    out = []
    iv = d.get("InteractionVars")
    if not isinstance(iv, dict):
        return out
    for var, val in iv.items():
        if isinstance(val, dict) and isinstance(val.get("Interactions"), list):
            for i, e in enumerate(val["Interactions"]):
                if isinstance(e, dict):
                    for f in ("Costs", "StatModifiers"):
                        if isinstance(e.get(f), dict) and "Mana" in e[f]:
                            out.append((var, i, f, e[f]["Mana"]))
    return out


def rule(v):
    if v == 0:
        return 0
    m = max(1, int(math.floor(abs(v) / float(DIV) + 0.5)))
    return m if v > 0 else -m


def leaf_diff(a, b, p, out):
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            out.append((tuple(p), "keys"))
            return out
        for k in a:
            leaf_diff(a[k], b[k], p + [k], out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((tuple(p), "len"))
            return out
        for i in range(len(a)):
            leaf_diff(a[i], b[i], p + [i], out)
    elif a != b or type(a) != type(b):
        out.append((tuple(p), "value"))
    return out


def check_spell_overrides():
    az, jz = zipfile.ZipFile(ASSETS), zipfile.ZipFile(JAR)
    items = {}
    for n in az.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            items[os.path.basename(n)[:-5]] = (n, json.loads(az.read(n).decode("utf-8-sig")))
    mana = dict((i, (p, d, mana_entries(d))) for i, (p, d) in items.items() if mana_entries(d))
    changed = dict((i, v) for i, v in mana.items() if any(e[3] != 0 for e in v[2]))
    zero = sorted(i for i, v in mana.items() if not any(e[3] != 0 for e in v[2]))
    jar_srv = sorted(n for n in jz.namelist() if n.startswith("Server/"))
    check(jar_srv == sorted(v[0] for v in changed.values()), "S: the jar's Server/ files are exactly the %d vanilla items with a non-zero Mana "
          "number, at their vanilla paths (jar %d)" % (len(changed), len(jar_srv)))
    check(len(changed) == 32 and len(zero) == 2 and zero == ["Weapon_Staff_Crystal_Ice", "Weapon_Staff_Crystal_Red"],
          "S: 32 overrides today, only-0 items left alone: %s" % zero)
    table = []
    for i in sorted(changed):
        p, d, ents = changed[i]
        if p not in jz.namelist():
            continue
        nd = json.loads(jz.read(p).decode("utf-8"))
        want = {}
        for (var, k, f, v) in ents:
            want[("InteractionVars", var, "Interactions", k, f, "Mana")] = rule(v)
        diff = leaf_diff(d, nd, [], [])
        got = dict((pp, None) for pp, why in diff)
        check(all(why == "value" for pp, why in diff) and set(got) == set(pp for pp, nv in want.items()
                                                                           if nv != copy.deepcopy(d)["InteractionVars"][pp[1]]["Interactions"][pp[3]][pp[4]]["Mana"]),
              "S: %s differs from vanilla ONLY in its Mana numbers: %s" % (i, diff[:4]))
        back = copy.deepcopy(nd)
        for (var, k, f, v) in ents:
            nv = nd["InteractionVars"][var]["Interactions"][k][f]["Mana"]
            check(nv == rule(v) and isinstance(nv, int), "S: %s %s %s Mana %s -> %s (want %s)" % (i, var, f, v, nv, rule(v)))
            back["InteractionVars"][var]["Interactions"][k][f]["Mana"] = v
        check(back == d, "S: %s with the old numbers put back IS the vanilla item" % i)
        c = [e for e in ents if e[2] == "Costs"]
        dr = [e for e in ents if e[2] == "StatModifiers"]
        check(len(c) == 1 and len(dr) == 1, "S: %s has one cast check and one drain" % i)
        if len(c) == 1 and len(dr) == 1:
            nc = nd["InteractionVars"][c[0][0]]["Interactions"][c[0][1]]["Costs"]["Mana"]
            ndr = nd["InteractionVars"][dr[0][0]]["Interactions"][dr[0][1]]["StatModifiers"]["Mana"]
            if c[0][3] == -dr[0][3]:
                check(nc == -ndr, "S: %s check and drain stay equal (%s / %s)" % (i, nc, ndr))
            table.append((i, c[0][3], nc, -dr[0][3], -ndr))
        check("Parent" not in d, "S: %s has no item Parent (its own file holds the cost)" % i)
    kids = sorted(i for i, (p, d) in items.items() if d.get("Parent") in mana)
    check(not kids, "S: no Assets.zip item inherits from a Mana item by Parent (%s)" % kids)
    for i, v in sorted(mana.items()):
        if i in zero:
            check(v[0] not in jz.namelist(), "S: only-0 item %s is not overridden" % i)
    print("S. %d overrides, %d only-0 items left alone, %d children by Parent; costs (cast check old -> new, drain old -> new):" % (
        len(changed), len(zero), len(kids)))
    fam = {}
    for (i, oc, nc, od, ndr) in table:
        key = (oc, nc, od, ndr)
        fam.setdefault(key, []).append(i)
    for key in sorted(fam):
        print("   %3d -> %2d / %3d -> %2d : %s" % (key + (", ".join(fam[key]),)))
    return table


def check_spell_gen():
    src = open(SCRIPT, encoding="utf-8").read()
    blk = src[src.index("# >>> SPELL GEN"):src.index("# <<< SPELL GEN")]
    ns = {"json": json}
    exec(compile(blk, "SPELL GEN", "exec"), ns)
    plan, leaks, new = ns["spell_plan"], ns["spell_leaks"], ns["spell_new"]

    def wand(cost, drain, **extra):
        d = {"Icon": "x.png", "InteractionVars": {
            "Wand_Cast_Left_Charged": {"Interactions": [{"Parent": "Wand_Cast_Left_Charged", "Costs": {"Mana": cost}}]},
            "Wand_Cast_Left_Cost": {"Interactions": [{"Parent": "Wand_Cast_Cost", "StatModifiers": {"Mana": drain}}]},
            "Wand_Cast_Left_Launch": "Wand_Cast_Launch"}, "Interactions": {"Primary": "Wand_Primary"}}
        d.update(extra)
        return d

    def it(d):
        return dict((k, ("Server/Item/Items/%s.json" % k, v)) for k, v in d.items())

    def refused(items):
        try:
            plan(it(items), DIV)
        except SystemExit as e:
            return str(e)
        return None
    pl, inh, un = plan(it({"P": wand(25, -25), "C": {"Parent": "P", "Icon": "c.png"}, "G": {"Parent": "C"}}), DIV)
    check([x[0] for x in pl] == ["P"] and inh == {"C": "P", "G": "P"} and not un, "X: child + grandchild without InteractionVars inherit "
          "the overridden parent's cost; only the parent file is overridden: %s %s" % ([x[0] for x in pl], inh))
    check(pl and pl[0][3]["InteractionVars"]["Wand_Cast_Left_Charged"]["Interactions"][0]["Costs"]["Mana"] == 5
          and pl[0][3]["InteractionVars"]["Wand_Cast_Left_Cost"]["Interactions"][0]["StatModifiers"]["Mana"] == -5, "X: 25 / -25 -> 5 / -5")
    r = refused({"P": wand(25, -25), "C": {"Parent": "P", "InteractionVars": {"Other": "Wand_Cast_Launch"}}})
    check(r and "merges" in r, "X: a child with its own InteractionVars (no Mana) under a Mana parent is refused: %s" % r)
    pl, inh, un = plan(it({"P": wand(25, -25), "C": wand(50, -50, Parent="P")}), DIV)
    check([x[0] for x in pl] == ["C", "P"] and not inh, "X: a child with its own Mana cost is overridden itself (C 50 -> 10)")
    bad_extra = wand(25, -25)
    bad_extra["InteractionVars"]["Wand_Cast_Left_Charged"]["Interactions"][0]["Costs"]["Stamina"] = 5
    r = refused({"P": bad_extra})
    check(r and "more than Mana" in r, "X: a Costs block with more than Mana is refused: %s" % r)
    bad_par = wand(25, -25)
    bad_par["InteractionVars"]["Wand_Cast_Left_Charged"]["Interactions"][0]["Parent"] = "Something_New"
    r = refused({"P": bad_par})
    check(r and "not a known Mana" in r, "X: an unknown Parent interaction is refused: %s" % r)
    r = refused({"P": wand(25, -25, Interactions={"Primary": {"Interactions": [{"Type": "StatsCondition", "Costs": {"Mana": 5}}]}})})
    check(r and "outside InteractionVars" in r, "X: a Mana cost outside InteractionVars is refused: %s" % r)
    r = refused({"P": wand(25.0, -25)})
    check(r and "whole number" in r, "X: a fractional Mana number is refused: %s" % r)
    two = wand(25, -25)
    two["InteractionVars"]["Second"] = {"Interactions": [{"Parent": "Staff_Cast_Summon_Charged", "Costs": {"Mana": 10}}]}
    r = refused({"P": two})
    check(r and "exactly one of each" in r, "X: two cast checks are refused: %s" % r)
    r = refused({"P": wand(-5, -25)})
    check(r and "wrong sign" in r, "X: a negative cast check is refused: %s" % r)
    pl, inh, un = plan(it({"Z": wand(0, 0), "Y": {"Parent": "Z"}}), DIV)
    check(not pl and un == ["Z"] and inh == {"Y": "Z"}, "X: an all-zero item is left alone (and its child just inherits the zeros)")
    check([new(v, DIV) for v in (0, 1, 2, 3, 7, 8, 12, 13, 25, 50, 100, -25, -50, -2)] == [0, 1, 1, 1, 1, 2, 2, 3, 5, 10, 20, -5, -10, -1],
          "X: rounding half up, at least 1, 0 stays 0, sign kept")
    ints = {"Wand_Primary": {"Type": "Charging", "Next": {"0.35": "Wand_Cast_Left_Charged"}},
            "Wand_Cast_Left_Charged": {"Type": "StatsCondition", "Costs": {"Mana": 25}, "Next": {"Type": "Replace", "Var": "Wand_Cast_Left_Cost",
                                                                                              "DefaultValue": {"Interactions": ["Wand_Cast_Cost"]}}},
            "Wand_Cast_Cost": {"Type": "ChangeStat", "StatModifiers": {"Mana": -25}}, "Wand_Cast_Launch": {"Type": "Simple"}}
    roots = {"Wand_Primary": {"Interactions": ["Wand_Primary"]}}
    good = wand(25, -25)
    lk = leaks({"W": good, "Bare": {"Interactions": {"Primary": "Wand_Primary"}}}, ints, roots)
    check(sorted(lk) == [("Bare", "Wand_Cast_Cost StatModifiers Mana -25 (a vanilla default the item does not set)"),
                         ("Bare", "Wand_Cast_Left_Charged Costs Mana 25 (a vanilla default the item does not set)")],
          "X: spell_leaks: the wand with its own vars has none, a bare item on the same root leaks the default check + drain once each: %s" % lk)
    # an interaction that inherits a cost by an interaction Parent (asset or inline), and an override whose Parent's cost it does not set
    ints2 = dict(ints)
    ints2["Alias_Cost"] = {"Parent": "Wand_Cast_Cost"}
    ints2["Alias_Free"] = {"Parent": "Wand_Cast_Cost", "StatModifiers": {"Mana": 0}}
    lk = leaks({"A": {"Interactions": {"Primary": "Alias_Cost"}},
                "F": {"Interactions": {"Primary": "Alias_Free"}},
                "I": {"Interactions": {"Primary": {"Interactions": [{"Parent": "Wand_Cast_Cost", "Next": "Wand_Cast_Launch"}]}}},
                "O": {"InteractionVars": {"Wand_Cast_Left_Cost": {"Interactions": [{"Parent": "Wand_Cast_Cost"}]}},
                      "Interactions": {"Primary": {"Interactions": [{"Type": "Replace", "Var": "Wand_Cast_Left_Cost"}]}}},
                "D": {"InteractionVars": {"X": {"Interactions": [{"Parent": "Wand_Cast_Cost", "StatModifiers": {"Mana": -5}}]}},
                      "Interactions": {"Primary": {"Interactions": [{"Type": "Replace", "Var": "X"}, "Wand_Cast_Cost"]}}}}, ints2, roots)
    check(sorted(lk) == [("A", "Alias_Cost StatModifiers Mana -25 (a vanilla default the item does not set)"),
                         ("D", "Wand_Cast_Cost StatModifiers Mana -25 (a vanilla default the item does not set)"),
                         ("I", "an inline StatModifiers Mana -25 (inherited from its Parent Wand_Cast_Cost)"),
                         ("O", "Wand_Cast_Left_Cost -> Parent Wand_Cast_Cost StatModifiers Mana -25 (the override does not set it)")],
          "X: spell_leaks follows interaction Parents (asset alias, inline), an override that does not set its Parent's cost, and the same "
          "interaction referenced directly after an override used it as a Parent; an alias that sets its own 0 is fine: %s" % lk)
    print("X. SPELL GEN block exec'd on synthetic items: Parent / shape / rounding / leak rules hold")


def expected_move(raw, table, comment):
    """the file after the move, computed independently: the pair -> comment + table lines; the untouched 0.4.6 / 0.4.7 comment (3 whole
    lines) -> the 0.4.8 comment; any other comment line naming the old keys stays and STALE goes right under the new comment line"""
    text = raw.decode("latin-1")
    lines = text.split("\n")
    out, hits, stale, head = [], 0, False, None
    i = 0
    while i < len(lines):
        ln = lines[i]
        e = "\r" if ln.endswith("\r") else ""
        body = ln[:-1] if e else ln
        if [x[:-1] if x.endswith("\r") else x for x in lines[i:i + len(OLD_DOC)]] == OLD_DOC:
            out.extend(x + e for x in NEW_DOC)
            i += len(OLD_DOC)
            continue
        st = body.lstrip(" \t\f")
        if st.startswith(("#", "!")) and ("mana.magicBase" in body or "mana.magicClasses" in body):
            stale = True
        if not st.startswith(("#", "!")) and re.match(r"mana\.magic(Base|Classes)([ \t\f=:]|$)", st):
            if hits == 0:
                out.append(comment + e)
                head = (len(out), e)
                out.extend("mana.classBase.%s=%s%s" % (c, v, e) for c, v in table)
                if not table:
                    out.append("# (no class listed - every class starts at mana.base)" + e)
            hits += 1
            i += 1
            continue
        out.append(ln)
        i += 1
    if stale and head:
        out.insert(head[0], STALE + head[1])
    return "\n".join(out)


def check_pin_bump():
    """Q (review finding 1): the build's SET-pin check, exec'd on deploy_set.py as it is and with the SkyySkills pin bumped"""
    src = open(SCRIPT, encoding="utf-8").read()
    a = src.index('_s0 = _dst.index("SET = [")')
    b = src.index("\n", src.index("len(_pins) >= 20 and _packs", a))
    blk = src[a:b]
    check(not re.search(r'\("SkyySkills", "[0-9.]+"\) in _pins', src), "Q: the build asserts no fixed SkyySkills pin")
    dst = open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8").read()
    cur = re.search(r'\("SkyySkills", "([0-9.]+)"\)', dst[dst.index("SET = ["):]).group(1)
    got = []
    for ver in (cur, "0.4.8", "0.4.9"):
        text = dst[:dst.index("SET = [")] + re.sub(r'\("SkyySkills", "[0-9.]+"\)', '("SkyySkills", "%s")' % ver, dst[dst.index("SET = ["):], count=1)
        ns = {"_dst": text, "_sre": re}
        try:
            exec(compile(blk, "SET pins", "exec"), ns)
            ok = ("SkyySkills", ver) in ns["_pins"]
        except AssertionError as e:
            ok = False
        check(ok, "Q: the build's SET-pin check passes with the SkyySkills pin at %s" % ver)
        got.append(ver)
    print("Q. the build's SET-pin check passes with SkyySkills pinned at %s" % ", ".join(got))


# ============================================================================================ main
def main():
    if "--mkfake" in sys.argv:
        run_mkfake(arg("--mkfake"))
        return
    if "--run" in sys.argv:
        run_child(arg("--run"), arg("--out"), "--full" in sys.argv, arg("--fake"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    for j in (JAR, OLD_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not os.path.isfile(LIVE):
        sys.exit("the live xp.properties is not at %s (pass --live <file>; it is only ever read and copied)" % LIVE)
    scratch_root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    if here == scratch_root or not here.startswith(scratch_root + "/"):
        sys.exit("--dir must be a folder INSIDE tools/dev/scratch/ (the whole folder is deleted afterwards), not %s" % SCRATCH)
    GUARD_OK[0] = True
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    live = open(LIVE, "rb").read()
    open(os.path.join(SCRATCH, "live-xp.properties"), "wb").write(live)   # the scratch COPY (the live file is never written)
    me = os.path.abspath(__file__)
    fake = os.path.join(SCRATCH, "fake")
    p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(os.path.join(fake, "skyytest", "FakeStore.class")), "the stand-in asset store class was generated")
    outs = {}
    for tag, j, full in (("new", JAR, True), ("old", OLD_JAR, False)):
        outs[tag] = os.path.join(SCRATCH, "run-%s.json" % tag)
        cmd = [sys.executable, me, "--run", j, "--out", outs[tag], "--dir", SCRATCH, "--fake", fake] + (["--full"] if full else [])
        p = subprocess.run(cmd, env=env)
        check(p.returncode == 0 and os.path.isfile(outs[tag]), "child JVM for %s ran" % os.path.basename(j))
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "bytecode child ran")
    if FAILS:
        return finish()
    new, old = json.load(open(outs["new"])), json.load(open(outs["old"]))
    # A
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"][:3]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                            os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    for ok, what in new["checks"]:
        check(ok, what)
    if FAILS:
        return finish()
    D = new["data"]
    # S + X
    table = check_spell_overrides()
    check_spell_gen()
    c = D["cost"]
    check(c["div"] == DIV and c["n"] == len(table) == 32 and c["ids"] == [t[0] for t in table]
          and c["cost"] == [t[2] for t in table] and c["drain"] == [t[4] for t in table] and c["old"] == [t[1] for t in table]
          and c["old_drain"] == [t[3] for t in table], "S: ManaCost (the guard's table) = the jar's overrides")
    check(c["staff"] == 10 and c["wand"] == 5 and c["none"] == -1, "S: ManaCost.costOf staff 10 / wand 5 / sword -1")
    # B
    b = D["base"]
    want = {"None": 10.0, "Warrior": 10.0, "Mage": 30.0, "Priest": 30.0, "Druid": 10.0, "mage": 30.0, "Archer": 10.0, "Berserker": 10.0}
    for k, v in want.items():
        check(b[k][0] == v and b[k][1] == v - 5.0, "B: base Mana %s = %s (modifier over a stat type max of 5: %s): %s" % (k, v, v - 5.0, b[k][:2]))
    check(b["Mage"][2][-1] == "Base Mana 30 - the Mage base (Base Mana by class)" and b["mage"][2][-1] == b["Mage"][2][-1],
          "B: Overall page line for a Mage: %r" % b["Mage"][2][-1])
    check(b["Warrior"][2][-1] == "Base Mana 10 (by class: Mage 30, Priest 30)" and b["None"][2][-1] == b["Warrior"][2][-1],
          "B: Overall page line without a listed class: %r" % b["Warrior"][2][-1])
    check(D["base_off"][0] == 0.0 and D["base_off"][1][-1] == "Base Mana from Skills is off on this server", "B: the part switched off: %s" % D["base_off"])
    check(D["text"].endswith("base mana 10, class Mana table Mage 30, Priest 30"), "B: ready-line piece: %r" % D["text"])
    check(D["hook"][0] is None and D["hook"][1] is None and D["hook"][3] is None and D["hook"][4] is None
          and D["hook"][2] == "Unknown class Druid - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Shaman.",
          "B: check= hook (Mage / mage ok, Druid refused, a removal ok, Shaman 0 ok): %s" % D["hook"])
    pr = D["problems"]
    check(pr[0] == "Archer 10000, Mage 30" and pr[2] == 10.0 and pr[3] == 10000.0 and "Druid is not a class (left out)" in pr[1]
          and "Mage is listed twice (mage left out)" in pr[1] and "Priest=abc is not a number (left out)" in pr[1],
          "B: loader problems (unknown class, a second spelling, not a number, clamp): %s" % pr)
    rw = D["rows"]
    check(rw["n"] == 173 and rw["classBase"] == ["table", "live", "", "dec;type;Base Mana", "Base Mana by class", "0", "10000", "overall"]
          and rw["div"] == ["int", "ro", "5", "", "Spell Mana costs divided by", "", "", "overall"] and not rw["old"] and rw["kit"] == "1.1",
          "B: config rows: 173, the mana.classBase table, the read-only divisor, no old pair: %s" % rw)
    check(D["customGet"] == "5", "B: SkillKit.customGet(spell.manaDivisor) = 5 (what Server Setup shows)")
    # M
    mg = D["mig"]
    CM = "# Base Mana by class (SkyySkills 0.4.8) replaced mana.magicBase=%s + mana.magicClasses=%s (%s):"
    DEFW = "the old defaults, now Skyy's 0.4.8 default"
    ADMW = "an admin's values, kept"
    livet = live.decode("latin-1")
    cases = {
        "live": (live, [("Mage", "30"), ("Priest", "30")], CM % ("20", "Mage,Priest", DEFW), "info"),
        "hand": (live.replace(b"mana.magicBase=20\n", b"mana.magicBase=25\n").replace(b"mana.magicClasses=Mage,Priest\n", b"mana.magicClasses=Mage\n"),
                 [("Mage", "25")], CM % ("25", "Mage", ADMW), "info"),
        "crlf": (live.replace(b"\n", b"\r\n"), [("Mage", "30"), ("Priest", "30")], CM % ("20", "Mage,Priest", DEFW), "info"),
        "spaced": (live.replace(b"mana.magicBase=20\n", b"  mana.magicBase : 20.0  \n").replace(b"mana.magicClasses=Mage,Priest\n",
                                                                                             b"mana.magicClasses = priest, MAGE\n"),
                   [("Mage", "30"), ("Priest", "30")], CM % ("20", "Priest,Mage", DEFW), "info"),
        "druid": (live.replace(b"mana.magicClasses=Mage,Priest\n", b"mana.magicClasses=Mage,Druid\n"), [("Mage", "20")],
                  CM % ("20", "Mage", ADMW), "info"),
        "empty": (live.replace(b"mana.magicClasses=Mage,Priest\n", b"mana.magicClasses=\n"), [], CM % ("20", "", ADMW), "info"),
        "note": (live.replace(DOC_EDIT[0], DOC_EDIT[1]), [("Mage", "30"), ("Priest", "30")], CM % ("20", "Mage,Priest", DEFW), "info"),
        "nodoc": (live.replace(DOC_LF, b""), [("Mage", "30"), ("Priest", "30")], CM % ("20", "Mage,Priest", DEFW), "info"),
    }
    check(live.count(DOC_LF) == 1 and live.count(DOC_EDIT[0]) == 1 and live.count(b"mana.magicBase") == 2,
          "M: the live copy has the untouched 0.4.7 comment once (and no other comment naming the old keys)")
    for nm, (src, tab, com, lvl) in cases.items():
        r = mg[nm]
        exp = expected_move(src, tab, com)
        check(r["r1"][0] == lvl and r["b1"] == exp, "M %s: first start rewrote exactly the two lines (+ the 0.4.7 comment / the stale "
              "note) (%s)" % (nm, r["r1"]))
        docd = src.replace(b"\r\n", b"\n").count(DOC_LF) > 0
        check((r["b1"].replace("\r\n", "\n").count("\n".join(NEW_DOC) + "\n") == 1) == docd
              and ("\n".join(OLD_DOC) + "\n" not in r["b1"].replace("\r\n", "\n")) and (STALE in r["b1"]) == (nm == "note"),
              "M %s: 0.4.7 comment %s, stale note %s" % (nm, "replaced" if docd else "not there / edited", "added" if nm == "note" else "none"))
        check(r["b2"] == r["b1"] and r["b3"] == r["b1"] and r["b4"] == r["b1"] and r["r2"][0] == "",
              "M %s: SkillCfg.load and a second start change nothing (%s)" % (nm, r["r2"]))
        check(r["files"] == ["xp.properties"], "M %s: no tmp file left: %s" % (nm, r["files"]))
        tt = ", ".join("%s %s" % x for x in tab)
        check(r["t1"][0] == tt and r["t1"][1] is False, "M %s: table after the move = %r (%s)" % (nm, tt, r["t1"][:3]))
        # the file as it was before the move went into the kit's history once the kit started (one .bak + its index line), the second
        # start keeps nothing new
        baks = [n for n in r["h1"] if n.endswith(".bak")]
        idx = r["h1"].get("index.log", "")
        check(r["k1"].endswith(".bak") and baks == [r["k1"]] and r["h1"][r["k1"]] == src.decode("latin-1")
              and idx.count("\n") == 1 and idx.split("\t")[3:] == ["SkyySkills 0.4.8", "xp.properties before mana.magicBase / "
                                                                   "mana.magicClasses moved to Base Mana by class\n"]
              and idx.split("\t")[1] == "Skyy_SkyySkills/xp.properties",
              "M %s: the pre-move file is kept as one kit history entry (%s, index %r)" % (nm, r["k1"], idx[:160]))
        check(r["k2"] == "" and r["h2"] == r["h1"], "M %s: the second start adds no history entry" % nm)
        if nm == "crlf":
            check(r["b1"].count("\r\n") == r["b1"].count("\n") and r["b1"].count("\n") == livet.count("\n") + 2,
                  "M crlf: every line still ends in CRLF (two lines more than the source: pair 2 -> 3, comment 3 -> 4)")
    check(mg["live"]["r1"][1] == "xp.properties: mana.magicBase=20 + mana.magicClasses=Mage,Priest (the untouched 0.4.7 defaults) became "
          "Base Mana by class Mage 30, Priest 30 (the 0.4.8 default); only those lines and the 0.4.7 Base Mana comment changed.",
          "M live: INFO line %r" % mg["live"]["r1"][1])
    check(mg["hand"]["r1"][1] == "xp.properties: mana.magicBase=25 + mana.magicClasses=Mage had been changed by an admin - kept as Base Mana "
          "by class Mage 25; the 0.4.8 default Mage 30, Priest 30 was NOT applied (Server Setup > Skills > Overall and Mana > Base Mana by "
          "class). Only those lines and the 0.4.7 Base Mana comment changed.", "M hand: INFO line %r" % mg["hand"]["r1"][1])
    check(mg["note"]["r1"][1] == "xp.properties: mana.magicBase=20 + mana.magicClasses=Mage,Priest (the untouched 0.4.7 defaults) became "
          "Base Mana by class Mage 30, Priest 30 (the 0.4.8 default); only those lines changed (a note under the new comment says other "
          "comments naming the old keys are stale).", "M note: INFO line %r" % mg["note"]["r1"][1])
    check(mg["nodoc"]["r1"][1] == "xp.properties: mana.magicBase=20 + mana.magicClasses=Mage,Priest (the untouched 0.4.7 defaults) became "
          "Base Mana by class Mage 30, Priest 30 (the 0.4.8 default); only those lines changed.", "M nodoc: INFO line %r" % mg["nodoc"]["r1"][1])
    # the live file after the move, around the Base Mana block (what an admin reads)
    lb = mg["live"]["b1"].split("\n")
    li = lb.index("mana.base.enabled=true")
    check(lb[li - 4:li] == NEW_DOC and lb[li + 1:li + 5] == ["mana.base=10", CM % ("20", "Mage,Priest", DEFW), "mana.classBase.Mage=30",
                                                              "mana.classBase.Priest=30"],
          "M live: the Base Mana block reads as the 0.4.8 default comment + table: %s" % lb[li - 4:li + 5])
    fb = mg["fresh"]["b2"].split("\n")
    fi = fb.index("mana.base.enabled=true")
    check(fb[fi - 4:fi] == NEW_DOC, "M: the move's new comment = the fresh default file's comment: %s" % fb[fi - 4:fi])
    check(mg["hand"]["t1"][3:] == [25.0, 10.0, 10.0], "M hand: Mage 25, Priest now the plain base 10: %s" % mg["hand"]["t1"][3:])
    check("(Druid is not a class - left out)" in mg["druid"]["r1"][1], "M druid: the unknown class is named: %r" % mg["druid"]["r1"][1])
    check(mg["empty"]["t1"][0] == "" and mg["empty"]["t1"][3] == 10.0, "M empty: no class listed -> every class starts at 10")
    ct = mg["cont"]
    check(ct["r1"][0] == "warn" and ct["b1"] == livet.replace("mana.magicClasses=Mage,Priest\n", "mana.magicClasses=Mage,\\\n    Priest\n")
          and ct["t1"][0] == "Mage 20, Priest 20" and ct["t1"][1] is True and "did not happen" in ct["t1"][2],
          "M cont: a continued line is refused, nothing written, the old pair is read as the table (legacy WARN): %s" % [ct["r1"], ct["t1"]])
    check(ct["r2"][0] == "warn" and ct["b3"] == ct["b1"], "M cont: the next start tries again (and still writes nothing)")
    bt = mg["both"]
    check(bt["r1"][0] == "" and bt["b1"] == livet.replace("mana.base=10\n", "mana.base=10\nmana.classBase.Priest=12\n")
          and bt["t1"][0] == "Priest 12" and "no longer used" in bt["t1"][2], "M both: the table wins, the old lines are left alone + WARN: %s" % bt["t1"])
    od = mg["old"]
    check(od["r1"][0] == "" and od["t1"][0] == "Mage 30, Priest 30" and "mana.classBase.Mage=30" in od["b2"] and od["b3"] == od["b2"],
          "M old: a pre-0.4.6 file gets the block appended and its table is read in the same load: %s" % od["t1"][:2])
    fr = mg["fresh"]
    check(fr["r1"][0] == "" and fr["b1"] is None and fr["t1"][0] == "Mage 30, Priest 30" and "\nmana.magicBase=" not in fr["b2"]
          and "\nmana.classBase.Priest=30\n" in fr["b2"],
          "M fresh: no file -> the default file with the table: %s" % fr["t1"][:2])
    for nm in ("cont", "both", "old", "fresh"):
        check(mg[nm]["k1"] == "" and mg[nm]["h1"] == {} and mg[nm]["k2"] == "" and mg[nm]["h2"] == {},
              "M %s: no move -> no history entry (%s)" % (nm, [mg[nm]["k1"], sorted(mg[nm]["h1"])]))
    print("M. migration: %d cases twice each (live file %d bytes, LF); pre-move copy kept as %s" % (len(mg), len(live), mg["live"]["k1"]))
    print("   INFO %s" % mg["live"]["r1"][1])
    print("   INFO %s" % mg["hand"]["r1"][1])
    print("   WARN %s" % ct["r1"][1])
    print("   WARN %s" % ct["t1"][2])
    print("   WARN %s" % bt["t1"][2])
    # G
    g = D["guard"]
    W5 = ("Base Mana check: Mage starts with 5 max Mana, but the kit weapon Weapon_Staff_Wood costs 10 Mana per cast (kit from the built-in "
          "table) - a new Mage cannot cast it. Raise Mage in Server Setup > Skills > Overall and Mana > Base Mana by class. Nothing was "
          "changed automatically.")
    I5 = ("Base Mana check (built-in kit table - SkyyClasses not found, spell costs /5): Priest 30 Mana >= Weapon_Wand_Wood 5 (6 casts); "
          "1 class(es) below their kit weapon's Mana cost (see the WARN)")
    I30 = ("Base Mana check (built-in kit table - SkyyClasses not found, spell costs /5): Mage 30 Mana >= Weapon_Staff_Wood 10 (3 casts), "
           "Priest 30 Mana >= Weapon_Wand_Wood 5 (6 casts)")
    check(g["mage5"] == [W5, I5], "G: Mage 5 -> one WARN + the summary: %s" % g["mage5"])
    check(g["mage5_again"] == [], "G: the same numbers again -> nothing (once per class)")
    check(g["mage30"] == [I30], "G: Mage 30 -> quiet (only the new summary): %s" % g["mage30"])
    check(g["mage30_again"] == [], "G: 30 again -> nothing")
    check(g["mage5_back"] == [W5, I5], "G: back to 5 -> WARN again: %s" % g["mage5_back"])
    WL = ("Base Mana check: Priest starts with 10 max Mana, but the kit weapon Weapon_Spellbook_Fire costs 20 Mana per cast (kit from "
          "SkyyClasses) - a new Priest cannot cast it. Raise Priest in Server Setup > Skills > Overall and Mana > Base Mana by class. "
          "Nothing was changed automatically.")
    IL = ("Base Mana check (kits from SkyyClasses, spell costs /5): Mage 30 Mana >= Weapon_Staff_Wood 10 (3 casts); 1 class(es) below "
          "their kit weapon's Mana cost (see the WARN)")
    check(g["live_priest10"] == [WL, IL], "G: the live SkyyClasses kit (Priest spellbook 20, base 10): %s" % g["live_priest10"])
    OFF = ("Base Mana check (kits from SkyyClasses, spell costs /5): class kits are off in SkyyClasses (Server Setup > Classes > Class kits) "
           "- no kit weapon to check")
    WON = ("Base Mana check: Mage starts with 5 max Mana, but the kit weapon Weapon_Staff_Wood costs 10 Mana per cast (kit from SkyyClasses) "
           "- a new Mage cannot cast it. Raise Mage in Server Setup > Skills > Overall and Mana > Base Mana by class. Nothing was changed "
           "automatically.")
    ION = ("Base Mana check (kits from SkyyClasses, spell costs /5): Priest 30 Mana >= Weapon_Spellbook_Fire 20 (1 cast); 1 class(es) below "
           "their kit weapon's Mana cost (see the WARN)")
    check(g["kits_off"] == [OFF] and g["kits_off_again"] == [], "G: SkyyClasses kits off -> no WARN, one INFO: %s" % g["kits_off"])
    check(g["kits_on"] == [WON, ION], "G: kits on again -> the Mage WARN is back (1 cast singular): %s" % g["kits_on"])
    check(len(g["off"]) == 3 and all("starts with 0 max Mana (the Base Mana part is off)" in x for x in g["off"][:2]),
          "G: Base Mana switched off -> Mage and Priest WARN: %s" % g["off"])
    tk = g["tick"]
    check(tk[0] == [False, ""] and tk[1][0] is True and tk[1][1] is False and tk[1][2] == I30 and tk[2] == "x" and tk[3] == I30
          and tk[4] == [I30, 7], "G: tick: not before 10 s, runs once, again after a config load and after a SkyyClasses epoch change: %s" % tk)
    print("G. guard lines:\n   WARN %s\n   INFO %s\n   INFO %s\n   WARN %s" % (W5, I5, I30, WL))
    # K
    k = D["pack"]
    ids = k["ids"]
    PKW = "Skyy:%s SkyySkills" % VERSION
    check(k["pack"] == PKW and ids == [t[0] for t in table], "K: the expected pack is %r (manifest Group:Name): %r" % (PKW, k["pack"]))
    KA = "Spell costs /5: all 32 item overrides are active (the game's item assets take them from %s)" % PKW
    check(k["all"] == ["info", KA], "K: all active -> one INFO: %s" % k["all"])
    KT = ("Spell costs /5: 2 of 32 item overrides are NOT active - another asset pack wins for %s (Hytale:Hytale), %s (Other:Mod). Those items "
          "keep that pack's Mana cost (of two packs with the same item, the one loaded last wins); 30 active." % (ids[0], ids[5]))
    check(k["two"] == ["warn", KT], "K: another pack wins for two -> one WARN naming them: %s" % k["two"])
    check(k["none"] == ["", "the game's item assets could not be read"] and k["null"] == k["none"] and k["bare"] == k["none"],
          "K: nothing readable (all null, no array, the bare JVM's packCheck) -> no line, try again: %s %s %s" % (k["none"], k["null"], k["bare"]))
    check(k["miss"] == ["info", "Spell costs /5: 30 of 32 item overrides are active (the game's item assets take them from %s); 2 not in the "
                                "game's item assets (%s, %s)" % (PKW, ids[1], ids[2])], "K: two ids missing -> INFO naming them: %s" % k["miss"])
    KM = ("Spell costs /5: 10 of 32 item overrides are NOT active - another asset pack wins for %s, .... Those items keep that pack's Mana "
          "cost (of two packs with the same item, the one loaded last wins); 22 active." % ", ".join("%s (Other:Mod)" % x for x in ids[:8]))
    check(k["many"] == ["warn", KM], "K: a long list is cut after 8: %s" % k["many"])
    KN = "Spell costs /5: the game's item assets could not be read to see which pack each of the 32 overridden items comes from - not checked"
    check(k["tick"] == [0, 1, 1, 1, 2, 2, [6, True, KN], 6], "K: pack check at 10 s, then every 10 s, 6 tries, then one INFO and done: %s" % k["tick"])
    check(k["engine_ok"] == ["info", KA, PKW, PKW, PKW], "K: engine DefaultAssetMap, vanilla then this jar -> all active: %s" % k["engine_ok"][:1])
    KE = ("Spell costs /5: 2 of 32 item overrides are NOT active - another asset pack wins for %s (Hytale:Hytale), %s (Other:Mod). Those items "
          "keep that pack's Mana cost (of two packs with the same item, the one loaded last wins); 30 active." % (ids[0], ids[3]))
    check(k["engine_clash"] == ["warn", KE, "Hytale:Hytale", PKW, "Other:Mod"],
          "K: engine DefaultAssetMap, vanilla -> this jar (without one item) -> a later pack (one item): the last pack loaded wins: %s" % k["engine_clash"])
    print("K. pack check (engine DefaultAssetMap.putAll, last pack loaded wins):\n   INFO %s\n   WARN %s\n   INFO %s" % (KA, KE, KN))
    # Q
    check_pin_bump()
    # P
    pk = D["perks"]
    wantp = [[30.0, 0.0], [30.0, 30.0], [30.0, 30.0], [10.0, 10.0], [30.0, 10.0], [30.0, 22.0], [30.0, 22.0]]
    check([x[1] for x in pk] == wantp, "P: max / current Mana: %s" % pk)
    print("P. max Mana on the engine's stat classes: " + "; ".join("%s %s/%s" % (x[0], x[1][1], x[1][0]) for x in pk))
    # F
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    added = sorted(set(zn.namelist()) - set(zo.namelist()))
    check(not (set(zo.namelist()) - set(zn.namelist())), "F: no entry of 0.4.7 is gone")
    check([n for n in added if not n.startswith("Server/")] == ["com/skyy/skills/ManaCost.class", "com/skyy/skills/ManaGuard.class",
                                                                  "com/skyy/skills/ManaMig.class"], "F: new classes: %s" % [n for n in added if not n.startswith("Server/")])
    diff = sorted(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    bc = json.load(open(bco))
    EXPECT = {"com/skyy/skills/OverallCfg.class", "com/skyy/skills/Overall.class", "com/skyy/skills/SkillKit.class",
              "com/skyy/skills/SkillTick.class", "com/skyy/skills/SkyySkillsPlugin.class", "com/skyy/skills/SkillCfg.class",
              "com/skyy/skills/CfgRows.class", "manifest.json"}
    extra = [n for n in diff if n not in EXPECT]
    for n in extra:
        cc = bc.get(n)
        check(cc is not None and not cc["new"] and not cc["gone"] and cc["fields_same"] and cc["version_only"],
              "F: %s differs by more than the version string: %s" % (n, cc))
    for n in ("SkillsPage", "StatsPage", "OverallPage", "Perks", "SkillStore", "SkillXp", "AcroSys", "OverallFn", "Xbow"):
        nn = "com/skyy/skills/%s.class" % n
        if nn in zo.namelist():
            check(nn not in diff, "F: %s is byte-identical" % n)
    ov = bc.get("com/skyy/skills/Overall.class", {})
    check(sorted(ov.get("changed", [])) == ["baseTarget(Ljava/util/UUID;)F", "magic(Ljava/util/UUID;)Z", "magicText()Ljava/lang/String;",
                                             "nowLines(Ljava/util/UUID;I)Ljava/util/ArrayList;"] and not ov.get("new") and not ov.get("gone"),
          "F: Overall: only baseTarget / magic / magicText / nowLines changed: %s" % ov)
    sk = bc.get("com/skyy/skills/SkillKit.class", {})
    check(sk.get("changed") == ["customGet(Ljava/lang/String;)Ljava/lang/String;"] and not sk.get("new") and not sk.get("gone"),
          "F: SkillKit: only customGet changed: %s" % sk)
    tk_ = bc.get("com/skyy/skills/SkillTick.class", {})
    check(tk_.get("changed") == ["run()V"], "F: SkillTick: only run() changed: %s" % tk_)
    pl = bc.get("com/skyy/skills/SkyySkillsPlugin.class", {})
    check(pl.get("changed") == ["setup()V"] and not pl.get("new") and not pl.get("gone"), "F: SkyySkillsPlugin: only setup() changed: %s" % pl)
    oc = bc.get("com/skyy/skills/OverallCfg.class", {})
    check(sorted(oc.get("fields_gone", [])) == ["MAGIC [Ljava/lang/String;", "MAGIC_BASE D", "MAGIC_TEXT Ljava/lang/String;"]
          and not oc.get("gone"), "F: OverallCfg: MAGIC / MAGIC_BASE / MAGIC_TEXT gone, nothing removed but them: %s" % oc)
    mo, mn = json.loads(zo.read("manifest.json")), json.loads(zn.read("manifest.json"))
    kd = sorted(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k))
    check(kd == ["Description", "IncludesAssetPack", "Name", "Version"] and mn["IncludesAssetPack"] is True and mn["Version"] == VERSION,
          "F: manifest: only %s differ" % kd)
    check(not [n for n in zn.namelist() if n.endswith(".ui")], "F: no .ui files (inline pages only)")
    print("F. class bytes: differ %s; new %s; methods: %s" % (
        ", ".join(n.split("/")[-1] for n in diff), ", ".join(n.split("/")[-1] for n in added if not n.startswith("Server/")),
        "; ".join("%s %s" % (n.split("/")[-1][:-6], dict((x, bc[n][x]) for x in ("changed", "new", "gone", "fields_gone", "fields_new")
                                                         if bc[n][x])) for n in sorted(bc))))
    return finish()


def finish():
    if not KEEP and GUARD_OK[0]:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyySkills %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
