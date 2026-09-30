"""SkyySkills 0.4.9 - bare-JVM harness for the cast check round (tools/skills_0_4_9_patch.py): every cast CHECKS what it SPENDS (generated
overrides of the charged cast step interactions + the default drains, next to the 32 item overrides of 0.4.8), the gate simulation, the
real-gate guard and the interaction pack check - plus every 0.4.8 check that still applies (Base Mana by class, ManaMig, max Mana).

    python SkyySkills/test_skyyskills_0.4.9.py [--jar <SkyySkills-0.4.9.jar>] [--old <SkyySkills-0.4.8.jar>] [--dir <scratch>]
                                               [--live <Skyy_SkyySkills folder>] [--keep]

Build first (python tools/skills_0_4_9_patch.py, then python SkyySkills/build_skyyskills_0.4.9.py). The old jar = the SET pin 0.4.8.
Child processes start fresh JVMs (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + ONE mod jar; TEMP / TMP /
java.io.tmpdir in the scratch folder). The live world is READ ONLY: its Skyy_SkyySkills folder (xp.properties, config-history/, players/) is
copied into the scratch folder and only that copy is ever written. Assets.zip is only read.
  A  every class of the 0.4.9 jar AND of the 0.4.8 jar loads and initializes under -Xverify:all
  S  the jar's Server/ files = the 32 item overrides of 0.4.8 (BYTE-IDENTICAL to the 0.4.8 jar's, still exactly the items whose
     InteractionVars carry a non-zero Mana number, only those numbers / 5) + the 8 interaction overrides, nothing else
  I  every interaction override against an INDEPENDENT read of Assets.zip: at the vanilla path, the JSON equals vanilla except its one
     Mana number (the three StatsCondition checks: Costs.Mana; the four default drains: StatModifiers.Mana = vanilla / 5); the staff step:
     only Type Simple -> StatsCondition + Costs {Mana} right after Type (keys = the wand check's, Failed = the vanilla Staff_Cast_Fail click);
     putting the old number back (staff: Costs out, Type Simple) gives vanilla; no other interaction / root interaction carries a Mana
     number except the unreferenced Tests/StatsCondition; no interaction inherits one of the eight by Parent
  W  the GATE SIMULATION with the harness's OWN walker (item slot -> root -> Charging -> charged step asset by NAME -> its Next / Replace
     vars, item vars only through a Replace): per weapon family and for every caster item, on vanilla, on the LIVE 0.4.8 jar and on
     0.4.9: the Mana a cast checks and what it spends. 0.4.9: check == spend == vanilla spend / 5 (wand 5, staff 10, spellbook 20, Rusty
     blunderbuss 10; the plain blunderbuss / Crystal_Red / Crystal_Ice spend 0 behind the family check), and a cast simulation from a
     starting pool (30 Mana: wand 6 casts, staff 3, spellbook 1, Rusty blunderbuss 3; 0.4.8 live: wand 2, staff free forever, spellbook
     1, blunderbuss 0) plus the Mana windows of the in-game steps (wand 5-24, staff 10-49, spellbook 20-99 castable in 0.4.9)
  X  the build script's own SPELL GEN block (exec'd here) on synthetic assets: spell_plan (0.4.8 rules, unchanged), spell_casts (a string
     names the asset - an item var of the same name is ignored; a Replace reads the var, else its DefaultValue; Parent inheritance; a drain
     without a check / on a Failed branch), spell_int_plan (check = the family's spend, a Simple step converted, two spends behind one
     check refused, an unknown Mana interaction refused, a used test asset refused, a converted step inherited by Parent refused, a drain
     outside a check refused) and spell_verify (vanilla vs final: check = spend = vanilla / 5, a cast that became free refused)
  B  base Mana: no class / Warrior / Mage / Priest / an unknown class / lower case, the part switch, the stat type max, the Overall page
     line, the config rows, the table's check= hook and the loader's problem report (unchanged from 0.4.8)
  L  START TWICE ON A SCRATCH COPY OF THE LIVE DATA (Skyy_SkyySkills, already moved by 0.4.8 on 2026-09-30): ManaMig.run finds nothing to
     move both times, xp.properties / config-history / players stay byte-identical, the table read is Mage 30, Priest 30 (no migration
     re-run, no new history entry)
  M  the migration regression (ManaMig is byte-identical to 0.4.8) on scratch copies of the PRE-MOVE file the live config history kept
     (the 0.4.7 file): the same 12 cases as 0.4.8 (LF, hand-edited, CRLF, spaced, unknown class, empty list, edited comment, no comment,
     continued line, table already there, pre-0.4.6 file, no file), each twice, exact bytes, history entry once
  G  the guard on the REAL gate: Mage 5 -> one WARN (once), 30 -> quiet, back to 5 -> WARN again, the live SkyyClasses kit (a Priest
     spellbook kit), kits off / on, the part switched off, a kit weapon that spends 0 behind a check (Crystal_Red: "needs 10 Mana to cast
     (it spends 0)"), tick() timing; ManaCost.costOf / spendOf = the gate table = the harness's own simulation of the jar's assets
  K  the item pack check (0.4.8 texts unchanged) and the NEW interaction pack check: intReport texts (all active with the live checks,
     another pack wins, a live check that differs / is not a StatsCondition / did not resolve, not readable, missing ids), liveCheck on
     engine StatsConditionInteraction objects (review finding 4: the RESOLVED costs entry of the Mana index = what canAfford compares; a
     decoded Mana cost with no resolved entry -> -4), intCheck in the bare JVM (nothing readable), packTick (items + interactions each once,
     6 tries, then one INFO each), and intCheck on the ENGINE's own IndexedLookupTableAssetMap.putAll behind a stand-in Interaction store
     (vanilla, then this jar, then a later pack: the last one loaded wins)
  E  (review finding 5) the 8 generated interaction files decoded by the ENGINE's own Interaction codec (Interaction.CODEC with the
     Simple / StatsCondition / ChangeStat subtypes registered like InteractionModule.setup, an AssetExtraInfo, stand-in stat / item /
     interaction stores): the 4 checks are StatsConditions whose RESOLVED Mana cost is 5 / 20 / 10 / 10 (liveCheck on the decoded object
     says the same), the 4 drains ChangeStats of Mana -5 / -5 / -5 / -15, no validation result, no unknown key, each engine object equal to
     vanilla's except that number; the staff step = the wand check's StatsCondition around exactly the vanilla Simple step. Nested Next /
     Failed trees and Effects are stub ids in jar and vanilla alike (contained assets need the full registry; I proves them vanilla).
     Controls: a mistyped key is reported unknown; the staff step typed back to Simple ignores Costs
  Q  the build's SET-pin check exec'd on tools/deploy_set.py (read only) with the SkyySkills pin as it is, 0.4.8 and 0.4.9
  P  max Mana on the ENGINE's EntityStatMap / EntityStatValue (mock asset store), unchanged from 0.4.8
  F  class bytes 0.4.8 vs 0.4.9: only ManaCost, ManaGuard and SkyySkillsPlugin (ready line) changed, the version / default-text carriers
     SkillCfg / CfgRows / CfgFn by the version string only, ManaMig / OverallCfg / Overall / the pages and everything else byte-identical;
     manifest: Version / Name / Description only
Nothing is deployed. Default scratch folder: tools/dev/scratch/skills049/harness (deleted at the end unless --keep; --dir must be a folder
INSIDE tools/dev/scratch/). Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, copy, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.4.9", "0.4.8"
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


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills049", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyySkills-%s.jar" % OLD_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
# the live world's SkyySkills data folder (read only; copied into the scratch folder): xp.properties (moved to Base Mana by class by 0.4.8
# on 2026-09-30) and config-history/ (which holds the file as it was BEFORE that move = the 0.4.7 file, used for the migration regression)
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
LIVE = os.path.join(LIVE_DIR, "xp.properties")
ASSETS = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
# 0.4.9: the interaction overrides (id -> kind, vanilla number (None = no check), new number) - the research's fix list (1.4 #1-#8)
INT_WANT = {"Wand_Cast_Left_Charged": ("check", 25, 5), "Spellbook_Cast_Hurl_Charged": ("check", 25, 20),
            "Gun_Shoot_Flintlock_Charged": ("check", 50, 10), "Staff_Cast_Summon_Charged": ("check+", None, 10),
            "Wand_Cast_Cost": ("drain", -25, -5), "Staff_Cast_Cost": ("drain", -25, -5), "Spellbook_Cast_Cost": ("drain", -25, -5),
            "Gun_Shoot_Cost": ("drain", -75, -15)}
CHECKS = [k for k, v in sorted(INT_WANT.items()) if v[0].startswith("check")]
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
    # ---------------------------------------------------------------- L: start twice on a scratch COPY of the live data (0.4.9)
    # the live Skyy_SkyySkills folder was already moved to Base Mana by class by 0.4.8: setup's ManaMig.run -> SkillCfg.load -> (kit start)
    # -> ManaMig.keepCopy, twice; nothing may be written (no migration re-run, no history entry)
    lc = os.path.join(SCRATCH, "live-copy")

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                    for r, ds, fs in os.walk(d) for f in fs)
    s0 = snap(lc)
    lr = []
    for k in range(2):
        Cfg.FILE = path(os.path.join(lc, "xp.properties"))
        Hist.DIR = None
        r = [str(x) for x in Mig.run()]
        Cfg.load()
        hist_of(lc)
        kc = str(Mig.keepCopy())
        lr.append([r, kc, str(OCfg.tableText()), bool(OCfg.LEGACY), str(OCfg.WARNED), float(OCfg.baseFor("Mage")), float(OCfg.baseFor("Priest"))])
    s1 = snap(lc)
    D["livecopy"] = {"runs": lr, "same": s0 == s1, "n": len(s0), "changed": sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k)),
                     "hist": sorted(k for k in s0 if k.startswith("config-history/")), "players": len([k for k in s0 if k.startswith("players/")])}

    # the migration regression runs on the PRE-MOVE file the live config history kept (= the 0.4.7 file the 0.4.8 move started from)
    live = open(os.path.join(SCRATCH, "pre-xp.properties"), "rb").read()
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
    # 0.4.9: the real gate table (from the build's gate simulation) + the interaction overrides
    gids = [str(x) for x in Cost.GIDS]
    D["gate"] = {"n": int(Cost.GN), "ids": gids, "check": [str(x) for x in Cost.GCHECK], "gate": [int(x) for x in Cost.GATE],
                 "gate_old": [int(x) for x in Cost.GATE_OLD], "spend": [int(x) for x in Cost.SPEND], "spend_old": [int(x) for x in Cost.SPEND_OLD],
                 "costOf": dict((i, int(Cost.costOf(i))) for i in gids + ["Weapon_Sword_Crude", "Weapon_Staff_Crystal_Flame"]),
                 "spendOf": dict((i, int(Cost.spendOf(i))) for i in gids + ["Weapon_Sword_Crude"]), "null": [int(Cost.costOf(None)), int(Cost.spendOf(None))],
                 "int_n": int(Cost.INT_N), "int_ids": [str(x) for x in Cost.INT_IDS], "int_kind": [str(x) for x in Cost.INT_KIND],
                 "int_old": [int(x) for x in Cost.INT_OLD], "int_new": [int(x) for x in Cost.INT_NEW]}

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
    # 0.4.9: kit weapons that spend 0 behind a check (Crystal_Red behind the staff check, the plain Blunderbuss behind the flintlock check)
    greset()
    bridge.put("config:fn:SkyyClasses", KitFn({"Mage": "Weapon_Staff_Crystal_Red:1", "Priest": "Weapon_Gun_Blunderbuss:1,Weapon_Wand_Wood:1",
                                               "__on__": "true"}))
    gread({"mana.classBase.Mage": "5", "mana.classBase.Priest": "30"})
    g["free5"] = grun()
    gread({"mana.classBase.Mage": "10", "mana.classBase.Priest": "30"})
    g["free10"] = grun()
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
    kk["ibare"] = [str(x) for x in Guard.intCheck()]           # no interaction asset store in a bare JVM
    Guard.PACK_DONE, Guard.PACK_TRIES, Guard.PACK_LAST = False, 0, ""
    Guard.ITEMS_DONE, Guard.INT_DONE, Guard.INT_LAST = False, False, ""
    tt_ = []
    for n in (9, 10, 11, 19, 20, 25):
        Guard.tick(n)
        tt_.append(int(Guard.PACK_TRIES))
    for n in (30, 40, 50, 60):
        Guard.tick(n)
    tt_.append([int(Guard.PACK_TRIES), bool(Guard.PACK_DONE), str(Guard.PACK_LAST)])
    Guard.tick(70)
    tt_.append(int(Guard.PACK_TRIES))
    tt_.append([bool(Guard.ITEMS_DONE), bool(Guard.INT_DONE), str(Guard.INT_LAST)])
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

    # ---------------------------------------------------------------- K2: the interaction pack check (0.4.9)
    iids = [str(x) for x in Cost.INT_IDS]
    ikind = [str(x) for x in Cost.INT_KIND]
    inew = [int(x) for x in Cost.INT_NEW]
    JFA = jpype.JArray(jpype.JFloat)

    def irep(packs, live_):
        return [str(x) for x in Guard.intReport(None if packs is None else JSA(packs), None if live_ is None else JFA(live_))]
    good = [float(inew[i]) if ikind[i].startswith("check") else -1.0 for i in range(len(iids))]
    ki = {"ids": iids, "kind": ikind, "new": inew}
    ki["all"] = irep([PKs] * len(iids), good)
    oth = [PKs] * len(iids)
    oth[iids.index("Wand_Cast_Left_Charged")] = "Other:Mod"
    ki["other"] = irep(oth, good)
    bad = list(good)
    bad[iids.index("Wand_Cast_Left_Charged")] = 25.0            # this jar's pack, but the engine decoded the vanilla 25
    bad[iids.index("Staff_Cast_Summon_Charged")] = -2.0         # not a StatsCondition (the vanilla Simple step)
    ki["bad"] = irep([PKs] * len(iids), bad)
    ki["unread"] = irep([PKs] * len(iids), [-1.0] * len(iids))
    ki["nolive"] = irep([PKs] * len(iids), None)
    ki["none"] = irep([None] * len(iids), None)
    ki["null"] = irep(None, None)
    ms2 = [PKs] * len(iids)
    ms2[iids.index("Gun_Shoot_Cost")] = None
    ki["miss"] = irep(ms2, good)
    # liveCheck on the engine's own interaction objects (allocated without a constructor, rawCosts set like the codec does and costs like its
    # afterDecode does: EntityStatsModule.resolveEntityStats = stat index -> cost; review finding 4: liveCheck reports costs' Mana entry, the
    # number StatsConditionInteraction.canAfford compares). Stat indexes as in P below (Stamina 2, Mana 3); section E does it with the codec.
    ICL = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction")
    SCB = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionBaseInteraction")
    SCI = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionInteraction")
    SIM = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.SimpleInteraction")
    O2F = JClass("it.unimi.dsi.fastutil.objects.Object2FloatOpenHashMap")
    I2F = JClass("it.unimi.dsi.fastutil.ints.Int2FloatOpenHashMap")
    DST_ = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    setf(None, DST_, "STAMINA", Integer(2))
    setf(None, DST_, "MANA", Integer(3))

    def sc(mana, stamina=None, resolved="same"):
        # resolved: "same" = costs resolved from rawCosts like the engine; None = costs null (nothing resolved); a number = costs' Mana entry
        # differs from the decoded one; "nomana" = only the Stamina entry resolved
        o = U.allocateInstance(SCI.class_)
        mp = O2F()
        if mana is not None:
            mp.addTo("Mana", jpype.JFloat(mana))
        if stamina is not None:
            mp.addTo("Stamina", jpype.JFloat(stamina))
        setf(o, SCB, "rawCosts", mp)
        if resolved is not None:
            cm = I2F()
            if stamina is not None or resolved == "nomana":
                cm.put(jpype.JInt(2), jpype.JFloat(1.5 if stamina is None else stamina))
            if mana is not None and resolved != "nomana":
                cm.put(jpype.JInt(3), jpype.JFloat(mana if resolved == "same" else resolved))
            setf(o, SCB, "costs", cm)
        setf(o, ICL, "id", "x")
        return o
    ki["live"] = [float(Guard.liveCheck(sc(5.0))), float(Guard.liveCheck(sc(None, 1.5))), float(Guard.liveCheck(U.allocateInstance(SIM.class_))),
                  float(Guard.liveCheck(None)), float(Guard.liveCheck(U.allocateInstance(SCI.class_))),
                  float(Guard.liveCheck(sc(5.0, None, None))), float(Guard.liveCheck(sc(5.0, None, "nomana"))),
                  float(Guard.liveCheck(sc(5.0, None, 25.0)))]
    unres = list(good)
    unres[iids.index("Wand_Cast_Left_Charged")] = -4.0          # this jar's pack, decoded Mana 5, but not resolved to the Mana stat
    ki["unres"] = irep([PKs] * len(iids), unres)
    # intCheck on the ENGINE's IndexedLookupTableAssetMap (what Interaction.getAssetMap() is): putAll per pack in load order behind a
    # stand-in Interaction asset store - vanilla (the old numbers), this jar (the new ones), a later pack (one interaction)
    ILT_ = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    iputm = ILT_.class_.getDeclaredMethod("putAll", JStr.class_, JClass("com.hypixel.hytale.assetstore.codec.AssetCodec").class_,
                                          JClass("java.util.Map").class_, JClass("java.util.Map").class_, JClass("java.util.Map").class_)
    iputm.setAccessible(True)

    @JImplements("java.util.function.IntFunction")
    class NewIArr(object):
        @JOverride
        def apply(self, n):
            return Arr.newInstance(ICL.class_, n)
    iold = [int(x) for x in Cost.INT_OLD]

    def iobj(i, num):
        if ikind[i] == "drain":
            return U.allocateInstance(SIM.class_)        # the drains are ChangeStat in the game; only their pack is read
        if num is None or num < 0:
            return U.allocateInstance(SIM.class_)        # the vanilla staff step: a Simple interaction, no check
        return sc(float(num))

    def iengine(loads):
        dm = ILT_(NewIArr())
        for pk, which in loads:
            assets, paths = HM(), HM()
            for i, num in which:
                assets.put(iids[i], iobj(i, num))
                paths.put(iids[i], path(os.path.join(work, "ipacks", pk.replace(":", "_").replace(" ", "_"), iids[i] + ".json")))
            iputm.invoke(dm, pk, codec, assets, paths, HM())
        st3 = U.allocateInstance(Fake_.class_)
        setf(st3, AS_, "assetMap", dm)
        setf(None, ICL, "ASSET_STORE", st3)
        r = [str(x) for x in Guard.intCheck()] + [str(dm.getAssetPack(iids[0])), str(dm.getAssetPack(iids[iids.index("Wand_Cast_Left_Charged")]))]
        setf(None, ICL, "ASSET_STORE", None)
        return r
    vanilla_l = [(i, iold[i]) for i in range(len(iids))]
    mine_l = [(i, inew[i]) for i in range(len(iids))]
    ki["engine_ok"] = iengine([("Hytale:Hytale", vanilla_l), (PKs, mine_l)])
    wi = iids.index("Wand_Cast_Left_Charged")
    ki["engine_clash"] = iengine([("Hytale:Hytale", vanilla_l), (PKs, mine_l), ("Other:Mod", [(wi, 25)])])
    ki["engine_vanilla_only"] = iengine([("Hytale:Hytale", vanilla_l)])
    D["ipack"] = ki
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

    # ---------------------------------------------------------------- E: the generated files through the ENGINE's own Interaction codec
    # (0.4.9 review finding 5). Interaction.CODEC (AssetCodecMapCodec, "Type" -> subtype) with the three subtypes these files use,
    # registered the way InteractionModule.setup does (bytecode: CODEC.register("Simple", SimpleInteraction.class, SimpleInteraction.CODEC),
    # "StatsCondition", "ChangeStat" likewise); decodeJson with an AssetExtraInfo like the asset store's own load; stand-in stores: the
    # stat types (engine IndexedLookupTableAssetMap.putAll - Costs / StatModifiers keys are validated against it and afterDecode resolves
    # them to stat indexes), Item (register touches it) and Interaction (the stub ids below). The nested Next / Failed trees and the
    # blunderbuss check's Effects are replaced by stub ids in the jar file AND in vanilla alike: they are contained assets that need the
    # full asset registry, and section I already proves them identical to vanilla. Then ManaGuard.liveCheck runs on the decoded objects.
    E_ = {}
    ILM = JClass("java.util.LinkedHashMap")
    AEI = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo")
    ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
    CSI = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.ChangeStatInteraction")
    smap = ILT(NewArr())
    sa, sp = ILM(), ILM()
    for nm in ["Health", "Oxygen", "Stamina", "Mana", "StaminaRegenDelay"]:
        tt = U.allocateInstance(EST.class_)
        setf(tt, EST, "id", nm)
        sa.put(nm, tt)
        sp.put(nm, path(os.path.join(work, "estats", nm + ".json")))
    iputm.invoke(smap, "Hytale:Hytale", codec, sa, sp, HM())
    ste = U.allocateInstance(Fake.class_)
    setf(ste, AS, "assetMap", smap)
    setf(ste, AS, "tClass", EST.class_)
    setf(None, EST, "ASSET_STORE", ste)
    E_["mana_index"] = [int(smap.getIndex("Mana")), int(smap.getIndex("Stamina"))]
    setf(None, DST, "MANA", Integer(int(smap.getIndex("Mana"))))
    sti = U.allocateInstance(Fake.class_)
    setf(sti, AS, "assetMap", DAM())
    setf(sti, AS, "tClass", ITEM.class_)
    setf(None, ITEM, "ASSET_STORE", sti)
    idm = DAM()
    ia, ip = ILM(), ILM()
    for x in ("StubNext", "StubFailed"):
        ia.put(x, U.allocateInstance(SIM.class_))
        ip.put(x, path(os.path.join(work, "estub", x + ".json")))
    putm.invoke(idm, "Hytale:Hytale", codec, ia, ip, HM())
    stn = U.allocateInstance(Fake.class_)
    setf(stn, AS, "assetMap", idm)
    setf(stn, AS, "tClass", ICL.class_)
    setf(None, ICL, "ASSET_STORE", stn)
    for tname, tcls in (("Simple", SIM), ("StatsCondition", SCI), ("ChangeStat", CSI)):
        ICL.CODEC.register(tname, tcls.class_, tcls.CODEC)

    def edec(txt, key, stub=True, extra=None, typ=None):
        j = json.loads(txt)
        if stub:
            for k_ in ("Next", "Failed"):
                if k_ in j:
                    j[k_] = "Stub" + k_
            j.pop("Effects", None)
        if extra:
            j.update(extra)
        if typ:
            j["Type"] = typ
        ei = AEI(path(os.path.join(work, "estub", key + ".json")), ADT(ICL.class_, key, None))
        try:
            o = ICL.CODEC.decodeJson(RJR.fromJsonString(json.dumps(j, indent=2)), ei)
        except Exception as e:
            t = e
            while t.getCause() is not None:
                t = t.getCause()
            return {"err": str(t)[:300]}
        vr = ei.getValidationResults()
        return {"cls": str(o.getClass().getSimpleName()), "str": str(o), "live": float(Guard.liveCheck(o)),
                "failed": bool(vr.hasFailed()), "results": None if vr.getResults() is None else [str(r) for r in vr.getResults()],
                "unknown": [str(k_) for k_ in ei.getUnknownKeys()]}
    jz_ = zipfile.ZipFile(jar)
    az_ = zipfile.ZipFile(ASSETS)
    rows = {}
    for n in jz_.namelist():
        if n.startswith("Server/Item/Interactions/") and n.endswith(".json"):
            key_ = os.path.basename(n)[:-5]
            rows[key_] = {"path": n, "jar": edec(jz_.read(n).decode("utf-8"), key_), "van": edec(az_.read(n).decode("utf-8-sig"), key_)}
    E_["rows"] = rows
    wj = jz_.read(rows["Wand_Cast_Left_Charged"]["path"]).decode("utf-8")
    sj = jz_.read(rows["Staff_Cast_Summon_Charged"]["path"]).decode("utf-8")
    # controls: a mistyped key is reported as unknown (so "no unknown keys" means something); the staff step typed back to Simple decodes
    # as a SimpleInteraction whose Costs is an unknown key (research 1.2: a Costs key on a Simple interaction is ignored)
    E_["typo"] = edec(wj, "Wand_Cast_Left_Charged", extra={"Costz": {"Mana": 5}})
    E_["simple"] = edec(sj, "Staff_Cast_Summon_Charged", typ="Simple")
    setf(None, ICL, "ASSET_STORE", None)
    setf(None, ITEM, "ASSET_STORE", None)
    setf(None, EST, "ASSET_STORE", st)
    setf(None, DST, "MANA", Integer(3))
    D["codec"] = E_
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
                  "version_only": all(version_only(mo[k], mn[k]) for k in changed),
                  "vo": [k for k in changed if version_only(mo[k], mn[k])]}
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
    jar_srv = sorted(n for n in jz.namelist() if n.startswith("Server/Item/Items/"))
    check(jar_srv == sorted(v[0] for v in changed.values()), "S: the jar's Server/Item/Items files are exactly the %d vanilla items with a "
          "non-zero Mana number, at their vanilla paths (jar %d)" % (len(changed), len(jar_srv)))
    # 0.4.9: the item overrides are the 0.4.8 ones, byte for byte; the only other Server/ files are the 8 interaction overrides
    oz = zipfile.ZipFile(OLD_JAR)
    old_srv = sorted(n for n in oz.namelist() if n.startswith("Server/"))
    check(old_srv == jar_srv and all(oz.read(n) == jz.read(n) for n in jar_srv),
          "S: the %d item overrides are byte-identical to the 0.4.8 jar's (0.4.8 had %d Server/ files)" % (len(jar_srv), len(old_srv)))
    other = sorted(n for n in jz.namelist() if n.startswith("Server/") and n not in jar_srv)
    check(len(other) == 8 and all(n.startswith("Server/Item/Interactions/") for n in other)
          and sorted(os.path.basename(n)[:-5] for n in other) == sorted(INT_WANT), "S: the other Server/ files are the 8 interaction "
          "overrides: %s" % [os.path.basename(n) for n in other])
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


def mana_scan(x, path, out):
    """every Costs / StatModifiers Mana number in x (independent of the build's scanner): [(path, field, value)]"""
    if isinstance(x, dict):
        for f in ("Costs", "StatModifiers"):
            if isinstance(x.get(f), dict) and "Mana" in x[f]:
                out.append((tuple(path), f, x[f]["Mana"]))
        for k, v in x.items():
            mana_scan(v, path + [k], out)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            mana_scan(v, path + [i], out)
    return out


def check_int_overrides():
    """I: the 8 interaction overrides against Assets.zip (read only)"""
    az, jz = zipfile.ZipFile(ASSETS), zipfile.ZipFile(JAR)
    ints, roots = {}, {}
    for n in az.namelist():
        if n.endswith(".json") and n.startswith("Server/Item/Interactions/"):
            ints.setdefault(os.path.basename(n)[:-5], []).append(n)
        elif n.endswith(".json") and n.startswith("Server/Item/RootInteractions/"):
            roots[os.path.basename(n)[:-5]] = n
    check(all(len(v) == 1 for v in ints.values()), "I: every interaction id is in Assets.zip once")
    ints = dict((k, v[0]) for k, v in ints.items())
    wand = json.loads(az.read(ints["Wand_Cast_Left_Charged"]).decode("utf-8-sig"))
    rows = []
    for sid, (kind, old, new) in sorted(INT_WANT.items()):
        p = ints.get(sid)
        ok = bool(p) and p in jz.namelist()
        check(ok, "I: %s is overridden at its vanilla path %s" % (sid, p))
        if not ok:
            continue
        v = json.loads(az.read(p).decode("utf-8-sig"))
        raw = jz.read(p).decode("utf-8")
        n_ = json.loads(raw)
        check(raw == json.dumps(n_, indent=2, ensure_ascii=True) + "\n", "I: %s is plain 2-space JSON text" % sid)
        if kind in ("drain", "check"):
            f = "StatModifiers" if kind == "drain" else "Costs"
            check(v.get("Type") == ("ChangeStat" if kind == "drain" else "StatsCondition") and v.get(f) == {"Mana": old} and "Parent" not in v,
                  "I: vanilla %s is a %s with %s {Mana: %s}" % (sid, v.get("Type"), f, old))
            d = leaf_diff(v, n_, [], [])
            check(d == [((f, "Mana"), "value")] and n_[f]["Mana"] == new and list(n_.keys()) == list(v.keys()),
                  "I: %s differs from vanilla ONLY in %s.Mana %s -> %s: %s" % (sid, f, old, n_.get(f), d))
            back = copy.deepcopy(n_)
            back[f]["Mana"] = old
            check(back == v and json.dumps(back) == json.dumps(v), "I: %s with the old number put back IS vanilla (key order too)" % sid)
            rows.append((sid, kind, old, n_[f]["Mana"]))
        else:
            check(v.get("Type") == "Simple" and "Costs" not in v and "Parent" not in v, "I: vanilla %s is a Simple step without a check" % sid)
            check(list(n_.keys()) == ["Type", "Costs"] + list(v.keys())[1:] and n_["Type"] == "StatsCondition" and n_["Costs"] == {"Mana": new},
                  "I: %s = vanilla + Type StatsCondition + Costs {Mana: %d} right after Type: %s" % (sid, new, list(n_.keys())))
            back = dict((k, copy.deepcopy(n_[k])) for k in n_ if k != "Costs")
            back["Type"] = "Simple"
            check(back == v and json.dumps(back) == json.dumps(v), "I: %s with Costs removed and Type Simple IS vanilla" % sid)
            check(sorted(n_.keys()) == sorted(wand.keys()), "I: the converted %s has exactly the keys of the wand check %s" % (sid, sorted(wand.keys())))
            fl = n_["Failed"]
            check(fl.get("Type") == "Replace" and fl.get("DefaultValue") == {"Interactions": ["Staff_Cast_Fail"]} and "Staff_Cast_Fail" in ints
                  and "Staff_Cast_Fail" in roots, "I: its Failed branch is the vanilla Staff_Cast_Fail click (as the wand's Wand_Cast_Fail)")
            rows.append((sid, kind, None, n_["Costs"]["Mana"]))
    found = []
    for sid, p in sorted(ints.items()):
        for hit in mana_scan(json.loads(az.read(p).decode("utf-8-sig")), [], []):
            found.append((sid, hit))
    rfound = [(r, h) for r, p in sorted(roots.items()) for h in mana_scan(json.loads(az.read(p).decode("utf-8-sig")), [], [])]
    want = sorted([k for k, v in INT_WANT.items() if v[0] != "check+"] + ["StatsCondition"])
    check(sorted(s_ for s_, h in found) == want and all(h[0] == () for s_, h in found) and not rfound,
          "I: the only Mana numbers in Server/Item/Interactions + RootInteractions are the 7 overridden ones + Tests/StatsCondition, all at the top: "
          "%s %s" % ([(s_, h) for s_, h in found if s_ not in want], rfound[:3]))
    check(ints.get("StatsCondition", "").startswith("Server/Item/Interactions/Tests/") and ints["StatsCondition"] not in jz.namelist(),
          "I: the test asset Tests/StatsCondition is left alone")
    allj = [json.loads(az.read(p).decode("utf-8-sig")) for p in list(ints.values()) + list(roots.values())]
    heirs = [x.get("Parent") for x in allj if isinstance(x, dict) and x.get("Parent") in INT_WANT]
    check(not heirs, "I: no vanilla interaction inherits one of the eight by Parent: %s" % heirs)
    print("I. interaction overrides (only the Mana number; the staff step: Type + Costs):")
    for r in rows:
        print("   %-28s %-6s %5s -> %3d" % (r[0], r[1], "none" if r[2] is None else r[2], r[3]))
    return rows


def gate_sim(items, ints, roots):
    """W: the harness's OWN gate simulation (independent of the build's spell_casts): per item, the charged steps its Primary / Secondary
    reach BY NAME (root -> interaction -> a Charging step's held Next entries, through a StatsCondition wrapper's Next), and for each the
    Mana it checks (the step asset's own Costs.Mana when it is a StatsCondition, else None = no check) and what it spends (every Replace
    under the step's Next: the item's var of that name, else the DefaultValue; an entry's own StatModifiers.Mana, else its Parent
    asset's). items / ints / roots = {id: JSON}. Returns {item: [(step, check, spend)]} for the items that reach a charged step."""
    def interaction_names(name, seen):
        d = ints.get(name)
        if not isinstance(d, dict) or name in seen:
            return []
        seen.add(name)
        if d.get("Type") == "Charging":
            return [v for k, v in sorted((d.get("Next") or {}).items()) if isinstance(v, str) and float(k) > 0]
        if isinstance(d.get("Next"), str):
            return interaction_names(d["Next"], seen)
        return []

    def mana_of(entry):
        if isinstance(entry, str):
            return ((ints.get(entry) or {}).get("StatModifiers") or {}).get("Mana", 0)
        own = (entry.get("StatModifiers") or {})
        if "Mana" in own:
            return own["Mana"]
        return (((ints.get(entry.get("Parent")) or {}).get("StatModifiers") or {}).get("Mana", 0)) if "StatModifiers" not in entry else 0

    def replaces(x, out):
        if isinstance(x, dict):
            if x.get("Type") == "Replace":
                out.append(x)
                return out
            for v in x.values():
                replaces(v, out)
        elif isinstance(x, list):
            for v in x:
                replaces(v, out)
        return out
    res = {}
    for iid, d in sorted(items.items()):
        iv = d.get("InteractionVars") or {}
        steps = []
        for slot in ("Primary", "Secondary"):
            r = (d.get("Interactions") or {}).get(slot)
            if not isinstance(r, str) or r not in roots:
                continue
            for name in roots[r].get("Interactions") or []:
                if isinstance(name, str):
                    for st in interaction_names(name, set()):
                        if st not in [s_ for s_, c_, p_ in steps]:
                            sd = ints[st]
                            chk = (sd.get("Costs") or {}).get("Mana") if sd.get("Type") == "StatsCondition" else None
                            spend = 0
                            for rp in replaces(sd.get("Next"), []):
                                val = iv.get(rp.get("Var"), rp.get("DefaultValue"))
                                ents = [val] if isinstance(val, str) else ((val or {}).get("Interactions") or [])
                                spend += sum(-m for m in (mana_of(e) for e in ents) if isinstance(m, (int, float)) and m < 0)
                            steps.append((st, chk, spend))
        if steps:
            res[iid] = steps
    return res


def sim_casts(pool, chk, spend, cap=100):
    """casts in a row from a Mana pool: a cast needs Mana >= its check (None = no check) and spends its spend (the engine clamps at 0);
    cap = 'free forever'"""
    n = 0
    while n < cap and (chk is None or pool >= chk):
        pool = max(0, pool - spend)
        n += 1
    return n


def check_gate_sim(gate):
    """W: the gate simulation on vanilla, the LIVE 0.4.8 jar and 0.4.9, compared with the jar's ManaCost gate table (gate = D["gate"])"""
    az = zipfile.ZipFile(ASSETS)

    def read(prefix, z, enc="utf-8-sig"):
        out = {}
        for n in z.namelist():
            if n.startswith(prefix) and n.endswith(".json"):
                out[os.path.basename(n)[:-5]] = json.loads(z.read(n).decode(enc))
        return out
    v_items, v_ints, v_roots = read("Server/Item/Items/", az), read("Server/Item/Interactions/", az), read("Server/Item/RootInteractions/", az)
    worlds = {}
    for tag, jar in (("vanilla", None), ("0.4.8", OLD_JAR), ("0.4.9", JAR)):
        it_, in_ = dict(v_items), dict(v_ints)
        if jar:
            jz = zipfile.ZipFile(jar)
            it_.update(read("Server/Item/Items/", jz, "utf-8"))
            in_.update(read("Server/Item/Interactions/", jz, "utf-8"))
        worlds[tag] = gate_sim(it_, in_, v_roots)
    # every held Charging step of every item was walked (bows, knives ...): only the known cast steps may check or spend Mana, in any world
    stray = sorted(set((w, i, st) for w, res in worlds.items() for i, steps in res.items() for st, c_, s_ in steps
                       if (c_ is not None or s_ > 0) and st not in CHECKS))
    check(not stray, "W: no charged step other than the 4 cast steps checks or spends Mana (walked %d items with a held Charging step): %s" % (
        len(worlds["vanilla"]), stray[:4]))
    for w in worlds:
        worlds[w] = dict((i, [x for x in steps if x[0] in CHECKS]) for i, steps in worlds[w].items() if any(x[0] in CHECKS for x in steps))
    new, old48, van = worlds["0.4.9"], worlds["0.4.8"], worlds["vanilla"]
    check(sorted(new) == sorted(van) == sorted(old48) and len(new) == 34, "W: 34 items reach a charged cast step in every world (%d / %d / %d)" % (
        len(van), len(old48), len(new)))
    check(all(len(v) == 1 for v in new.values()), "W: one charged cast step per item")
    fam = {}
    for iid in sorted(new):
        st, c9, s9 = new[iid][0]
        stv, cv, sv = van[iid][0]
        st8, c8, s8 = old48[iid][0]
        check(st == stv == st8, "W: %s casts through the same step in every world (%s)" % (iid, st))
        if s9 > 0:
            check(c9 == s9 == rule(sv), "W: %s checks %s = spends %s = vanilla spend %s / 5" % (iid, c9, s9, sv))
        else:
            check(sv == 0 and c9 == INT_WANT[st][2], "W: %s spends 0 (vanilla too) behind the %s check %s" % (iid, st, c9))
        fam.setdefault((st, cv, sv, c8, s8, c9, s9), []).append(iid)
    # the jar's gate table (what ManaGuard compares with) = this independent simulation
    tab = dict((gate["ids"][i], (gate["check"][i], gate["gate_old"][i], gate["gate"][i], gate["spend_old"][i], gate["spend"][i]))
               for i in range(len(gate["ids"])))
    mine = dict((i, (new[i][0][0], van[i][0][1] or 0, new[i][0][1], van[i][0][2], new[i][0][2])) for i in new)
    check(tab == mine and gate["n"] == len(mine), "W: ManaCost's gate table (GIDS / GCHECK / GATE_OLD / GATE / SPEND_OLD / SPEND) = the harness's "
          "own simulation of the jar's assets: %s" % sorted(set(tab.items()) ^ set(mine.items()))[:4])
    check(all(gate["costOf"][i] == new[i][0][1] and gate["spendOf"][i] == new[i][0][2] for i in new) and gate["costOf"]["Weapon_Sword_Crude"] == -1
          and gate["costOf"]["Weapon_Staff_Crystal_Flame"] == -1 and gate["spendOf"]["Weapon_Sword_Crude"] == -1 and gate["null"] == [-1, -1],
          "W: ManaCost.costOf / spendOf = the real check / spend (-1 for a sword, the Crystal_Flame staff, null)")
    # the families and a 30-Mana caster's casts in a row (the research's numbers), vanilla / 0.4.8 LIVE / 0.4.9
    rep_items = {"wand": "Weapon_Wand_Wood", "staff": "Weapon_Staff_Wood", "spellbook": "Weapon_Spellbook_Fire", "blunderbuss": "Weapon_Gun_Blunderbuss_Rusty"}
    want30 = {"wand": (2, 6), "staff": (100, 3), "spellbook": (1, 1), "blunderbuss": (0, 3)}
    for nm, iid in sorted(rep_items.items()):
        st, c9, s9 = new[iid][0]
        _, c8, s8 = old48[iid][0]
        got = (sim_casts(30, c8, s8), sim_casts(30, c9, s9))
        check(got == want30[nm], "W: %s (%s) from 30 Mana: 0.4.8 LIVE %s casts, 0.4.9 %s (want %s)" % (nm, iid, got[0], got[1], want30[nm]))
    # the in-game steps' Mana windows: in 0.4.9 a cast works anywhere in the window and is refused just below the check
    windows = {"wand": ("Weapon_Wand_Wood", 6, 24), "staff": ("Weapon_Staff_Wood", 10, 49), "spellbook": ("Weapon_Spellbook_Fire", 20, 99)}
    for nm, (iid, lo, hi) in sorted(windows.items()):
        st, c9, s9 = new[iid][0]
        _, c8, s8 = old48[iid][0]
        ok9 = all(sim_casts(m, c9, s9, cap=1) == 1 for m in range(lo, hi + 1)) and sim_casts(c9 - 1, c9, s9, cap=1) == 0
        blocked8 = [m for m in range(lo, hi + 1) if sim_casts(m, c8, s8, cap=1) == 0]
        check(ok9, "W: %s: 0.4.9 casts at every Mana %d-%d and refuses at %d" % (nm, lo, hi, c9 - 1))
        print("   window %-9s %d-%d Mana: 0.4.9 all cast (refused below %d); 0.4.8 LIVE refused at %s" % (
            nm, lo, hi, c9, ("%d-%d" % (blocked8[0], blocked8[-1])) if blocked8 else "none (no check at all)"))
    print("W. gate simulation (harness walker; vanilla check/spend | 0.4.8 LIVE check/spend | 0.4.9 check/spend):")
    for key in sorted(fam, key=lambda k: (k[0], k[2])):
        st, cv, sv, c8, s8, c9, s9 = key
        nm = fam[key]
        print("   %-28s %4s/%3d | %4s/%3d | %3d/%3d : %d item(s) %s" % (st, "none" if cv is None else cv, sv, "none" if c8 is None else c8, s8,
                                                                        c9, s9, len(nm), ", ".join(nm) if len(nm) <= 3 else ", ".join(nm[:2]) + ", ..."))
    print("   30 Mana, casts in a row (0.4.8 LIVE -> 0.4.9): " + ", ".join(
        "%s %s -> %d" % (nm, "free forever" if want30[nm][0] >= 100 else want30[nm][0], want30[nm][1]) for nm in sorted(want30)))
    return fam


def check_spell_gen():
    src = open(SCRIPT, encoding="utf-8").read()
    blk = src[src.index("# >>> SPELL GEN"):src.index("# <<< SPELL GEN")]
    ns = {"json": json}
    exec(compile(blk, "SPELL GEN", "exec"), ns)
    plan, new = ns["spell_plan"], ns["spell_new"]
    check("spell_leaks" not in ns, "X: 0.4.8's spell_leaks (the wrong model: an item var named like an interaction replaces it) is gone")

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
    # ---- 0.4.9: spell_casts / spell_int_plan / spell_verify on a synthetic copy of the vanilla caster shapes
    casts, iplan, verify = ns["spell_casts"], ns["spell_int_plan"], ns["spell_verify"]

    def rep_(var, default):
        return {"Interactions": [{"Type": "Replace", "Var": var, "DefaultValue": {"Interactions": [default]}}]}

    def charged(typ, cost, pre, **extra):
        d = {"Type": typ}
        if cost is not None:
            d["Costs"] = {"Mana": cost}
        d.update({"$Comment": "Prepare Delay", "RunTime": 0.167,
                  "Next": {"Type": "Parallel", "Interactions": [rep_(pre + "_Cost", pre.split("_Cast")[0] + "_Cast_Cost" if "Gun" not in pre else "Gun_Shoot_Cost"),
                                                                rep_(pre + "_Launch", "Launch")]},
                  "Failed": {"Type": "Replace", "Var": pre + "_Fail", "DefaultValue": {"Interactions": ["Fail"]}}})
        d.update(extra)
        return d
    V_INTS = {"Wand_Primary": {"Type": "Charging", "Next": {"0": {"Type": "Chaining", "Next": ["Swing"]}, "0.35": "Wand_Cast_Left_Charged"}},
              "Wand_Cast_Left_Charged": charged("StatsCondition", 25, "Wand_Cast_Left"),
              "Wand_Cast_Cost": {"Type": "ChangeStat", "StatModifiers": {"Mana": -25}},
              "Staff_Primary": {"Type": "Charging", "Next": {"0": "Swing", "1": "Staff_Cast_Summon_Charged"}},
              "Staff_Cast_Summon_Charged": charged("Simple", None, "Staff_Cast_Summon"),
              "Staff_Cast_Cost": {"Type": "ChangeStat", "StatModifiers": {"Mana": -25}},
              "Spellbook_Primary": {"Type": "Charging", "Next": {"1": "Spellbook_Cast_Hurl_Charged"}},
              "Spellbook_Cast_Hurl_Charged": charged("StatsCondition", 25, "Spellbook_Cast_Hurl"),
              "Spellbook_Cast_Cost": {"Type": "ChangeStat", "Next": {"Type": "ModifyInventory", "AdjustHeldItemQuantity": -1},
                                      "StatModifiers": {"Mana": -25}},
              "Gun_Shoot_Flintlock_Charging": {"Type": "Charging", "Next": {"2": "Gun_Shoot_Flintlock_Charged"}},
              "Gun_Shoot_Flintlock_Charged": charged("StatsCondition", 50, "Gun_Shoot"),
              "Gun_Shoot_Cost": {"Type": "ChangeStat", "StatModifiers": {"Mana": -75}},
              "StatsCondition": {"Type": "StatsCondition", "Costs": {"Mana": 25}},
              "Swing": {"Type": "Simple"}, "Launch": {"Type": "Simple"}, "Fail": {"Type": "Simple"}}
    V_ROOTS = dict((k, {"Interactions": [k]}) for k in ("Wand_Primary", "Staff_Primary", "Spellbook_Primary", "Gun_Shoot_Flintlock_Charging"))
    V_PATHS = dict((k, "Server/Item/Interactions/T/%s.json" % k) for k in V_INTS)

    def caster(root, check_var, check_parent, check, cost_var, cost_parent, spend, **vars_):
        iv = {cost_var: {"Interactions": [{"Parent": cost_parent, "StatModifiers": {"Mana": spend}}]}}
        if check_var:
            iv[check_var] = {"Interactions": [{"Parent": check_parent, "Costs": {"Mana": check}}]}
        iv.update(vars_)
        return {"InteractionVars": iv, "Interactions": {"Primary": root, "Secondary": root}}

    def world(w, s, r, b, g1, g0):
        # the item vars as vanilla (w = 25 ...) or as the 0.4.8 overrides (w = 5 ...) have them
        return {"W": caster("Wand_Primary", "Wand_Cast_Left_Charged", "Wand_Cast_Left_Charged", w, "Wand_Cast_Left_Cost", "Wand_Cast_Cost", -w),
                "S": caster("Staff_Primary", "Staff_Cast_Summon_Charged", "Staff_Cast_Summon_Charged", s, "Staff_Cast_Summon_Cost", "Staff_Cast_Cost", -s),
                "R": caster("Staff_Primary", "Staff_Cast_Summon_Charged", "Staff_Cast_Summon_Charged", 0, "Staff_Cast_Summon_Cost", "Staff_Cast_Cost", r),
                "B": caster("Spellbook_Primary", "Spellbook_Cast_Hurl_Charged", "Spellbook_Cast_Hurl_Charged", b, "Spellbook_Cast_Hurl_Cost",
                            "Spellbook_Cast_Cost", -b),
                "G1": caster("Gun_Shoot_Flintlock_Charging", "Gun_Shoot_Flintlock_Charged", "Gun_Shoot_Flintlock_Charged", 50, "Gun_Shoot_Cost",
                             "Gun_Shoot_Cost", g1),
                "G0": caster("Gun_Shoot_Flintlock_Charging", "Gun_Shoot_Flintlock_Charged", "Gun_Shoot_Flintlock_Charged", 50, "Gun_Shoot_Cost",
                             "Gun_Shoot_Cost", g0),
                "Sword": {"Interactions": {"Primary": "Swing"}}}
    VAN = world(25, 50, 0, 100, -50, 0)
    NEW = world(5, 10, 0, 20, -10, 0)

    def summary(r):
        return ([(c[0], c[1], [v for v, s_ in c[2]]) for c in r["casts"]], [(v, s_) for v, s_, w_ in r["free"]], [v for v, s_, w_ in r["fail"]],
                [v for v, s_, w_ in r["gain"]])

    def raises(fn, *a):
        try:
            fn(*a)
        except SystemExit as e:
            return str(e)
        return None
    # the engine's rules: the charged step is the asset named in the Charging Next - the item var of the same name (5) is NOT used
    rw = summary(casts(NEW["W"], V_INTS, V_ROOTS))
    check(rw == ([(25, ("int", "Wand_Cast_Left_Charged"), [-5])], [], [], []),
          "X: spell_casts: the wand is checked by the Wand_Cast_Left_Charged ASSET (25), its var of that name (5) is dead; the drain var (-5) is "
          "read by the Replace: %s" % (rw,))
    rs = summary(casts(NEW["S"], V_INTS, V_ROOTS))
    check(rs == ([], [(-10, ("var", "Staff_Cast_Summon_Cost"))], [], []), "X: spell_casts: the vanilla staff step (Simple) checks nothing - "
          "its spend is free: %s" % (rs,))
    rd = summary(casts({"Interactions": {"Primary": "Wand_Primary"}}, V_INTS, V_ROOTS))
    check(rd == ([(25, ("int", "Wand_Cast_Left_Charged"), [-25])], [], [], []), "X: spell_casts: no drain var -> the Replace DefaultValue "
          "(Wand_Cast_Cost -25, source the asset): %s" % (rd,))
    rb = casts(NEW["B"], V_INTS, V_ROOTS)
    check(summary(rb)[0] == [(25, ("int", "Spellbook_Cast_Hurl_Charged"), [-20])], "X: spell_casts: a var entry inherits Type (ChangeStat) "
          "from its Parent and keeps its own Mana: %s" % (summary(rb),))
    ff = copy.deepcopy(NEW["W"])
    ff["InteractionVars"]["Wand_Cast_Left_Fail"] = {"Interactions": [{"Type": "ChangeStat", "StatModifiers": {"Mana": -3}}]}
    check(summary(casts(ff, V_INTS, V_ROOTS))[2] == [-3], "X: spell_casts: a drain on the check's Failed branch is reported")
    gv = {"InteractionVars": {"G": {"Interactions": [{"Parent": "Wand_Cast_Left_Charged", "Costs": {"Mana": 7}}]}},
          "Interactions": {"Primary": {"Interactions": [{"Type": "Replace", "Var": "G", "DefaultValue": {"Interactions": ["Swing"]}}]}}}
    check(summary(casts(gv, V_INTS, V_ROOTS))[0] == [(7, ("var", "G"), [-25])], "X: spell_casts: a check reached THROUGH a Replace var is the "
          "var's (7, inheriting Type / Next from its Parent)")
    mg = {"Interactions": {"Primary": {"Interactions": [{"Parent": "Wand_Cast_Cost", "StatModifiers": {"Stamina": -1}}]}}}
    e = raises(casts, mg, V_INTS, V_ROOTS)
    check(e and "whether the engine merges" in e, "X: spell_casts: a StatModifiers block without Mana over a Mana parent is refused: %s" % e)
    # spell_int_plan on the 0.4.8-style items
    pl, fams, heirs, tests = iplan(NEW, V_INTS, V_PATHS, V_ROOTS, DIV)
    got = [(x[0], x[2], x[3], x[4]) for x in pl]
    check(got == [("Gun_Shoot_Cost", "drain", -75, -15), ("Gun_Shoot_Flintlock_Charged", "check", 50, 10), ("Spellbook_Cast_Cost", "drain", -25, -5),
                  ("Spellbook_Cast_Hurl_Charged", "check", 25, 20), ("Staff_Cast_Cost", "drain", -25, -5),
                  ("Staff_Cast_Summon_Charged", "check+", None, 10), ("Wand_Cast_Cost", "drain", -25, -5),
                  ("Wand_Cast_Left_Charged", "check", 25, 5)], "X: spell_int_plan: check = the family's spend (wand 5, spellbook 20 not 25/5, "
                                                               "flintlock 10), the Simple staff step converted (10), default drains / 5: %s" % got)
    st = [x for x in pl if x[0] == "Staff_Cast_Summon_Charged"][0][5]
    check(list(st.keys()) == ["Type", "Costs", "$Comment", "RunTime", "Next", "Failed"] and st["Type"] == "StatsCondition"
          and st["Costs"] == {"Mana": 10} and st["Next"] == V_INTS["Staff_Cast_Summon_Charged"]["Next"],
          "X: spell_int_plan: the converted staff step = vanilla + Type StatsCondition + Costs right after Type: %s" % list(st.keys()))
    check(fams["Staff_Cast_Summon_Charged"][2] == ["R"] and fams["Gun_Shoot_Flintlock_Charged"][2] == ["G0"] and tests == ["StatsCondition"]
          and not heirs, "X: spell_int_plan: items that spend 0 behind a check are listed (R, G0); the unreferenced test asset is left alone")
    two = dict(NEW)
    two["W2"] = caster("Wand_Primary", None, None, 0, "Wand_Cast_Left_Cost", "Wand_Cast_Cost", -7)
    e = raises(iplan, two, V_INTS, V_PATHS, V_ROOTS, DIV)
    check(e and "must spend one number" in e, "X: spell_int_plan: two spends behind one check are refused: %s" % e)
    odd = dict(V_INTS)
    odd["Odd"] = {"Type": "ChangeStat", "StatModifiers": {"Mana": -3}}
    e = raises(iplan, NEW, odd, dict(V_PATHS, Odd="Server/Item/Interactions/T/Odd.json"), V_ROOTS, DIV)
    check(e and "not a known cast check" in e, "X: spell_int_plan: a Mana number on an unknown interaction is refused: %s" % e)
    used = dict(V_INTS)
    used["Swing"] = {"Type": "Simple", "Next": "StatsCondition"}
    e = raises(iplan, NEW, used, V_PATHS, V_ROOTS, DIV)
    check(e and "no longer a test asset" in e, "X: spell_int_plan: a test asset that something references is refused: %s" % e)
    heir = dict(V_INTS)
    heir["Heir"] = {"Parent": "Staff_Cast_Summon_Charged"}
    e = raises(iplan, NEW, heir, dict(V_PATHS, Heir="Server/Item/Interactions/T/Heir.json"), V_ROOTS, DIV)
    check(e and "would change it too" in e, "X: spell_int_plan: an interaction inheriting the converted step is refused: %s" % e)
    ek = dict(V_INTS)
    ek["Staff_Cast_Summon_Charged"] = dict(V_INTS["Staff_Cast_Summon_Charged"], Effects={"ItemAnimationId": "x"})
    e = raises(iplan, NEW, ek, V_PATHS, V_ROOTS, DIV)
    check(e and "neither a StatsCondition" in e, "X: spell_int_plan: a Simple step with keys the wand check does not have is refused: %s" % e)
    fr = dict(NEW)
    fr["Free"] = {"Interactions": {"Primary": {"Interactions": [{"Type": "ChangeStat", "StatModifiers": {"Mana": -4}}]}}}
    e = raises(iplan, fr, V_INTS, V_PATHS, V_ROOTS, DIV)
    check(e and "outside a known cast check" in e, "X: spell_int_plan: a Mana spend outside every known check is refused: %s" % e)
    e = raises(iplan, NEW, V_INTS, V_PATHS, dict(V_ROOTS, R2={"Interactions": [{"Type": "ChangeStat", "StatModifiers": {"Mana": -1}}]}), DIV)
    check(e and "root interaction R2" in e, "X: spell_int_plan: a root interaction with a Mana number is refused: %s" % e)
    nest = dict(V_INTS)
    nest["Launch"] = {"Type": "Simple", "Next": {"Type": "ChangeStat", "StatModifiers": {"Mana": -2}}}
    e = raises(iplan, NEW, nest, V_PATHS, V_ROOTS, DIV)
    check(e and "inside the interaction" in e, "X: spell_int_plan: a Mana number nested inside an interaction is refused: %s" % e)
    e = raises(iplan, dict(NEW, GV=gv), V_INTS, V_PATHS, V_ROOTS, DIV)
    check(e and "only the known charged cast steps check Mana" in e, "X: spell_int_plan: a check reached through a var is refused: %s" % e)
    # spell_verify: vanilla items + interactions vs the final ones
    FINAL = dict(V_INTS)
    for x in pl:
        FINAL[x[0]] = x[5]
    rows = verify(VAN, NEW, V_INTS, FINAL, V_ROOTS, DIV)
    check(rows == [("B", "Spellbook_Cast_Hurl_Charged", 25, 20, 100, 20), ("G0", "Gun_Shoot_Flintlock_Charged", 50, 10, 0, 0),
                   ("G1", "Gun_Shoot_Flintlock_Charged", 50, 10, 50, 10), ("R", "Staff_Cast_Summon_Charged", 0, 10, 0, 0),
                   ("S", "Staff_Cast_Summon_Charged", 0, 10, 50, 10), ("W", "Wand_Cast_Left_Charged", 25, 5, 25, 5)],
          "X: spell_verify: per item check = spend = vanilla spend / 5 (0 = vanilla had no check): %s" % rows)
    e = raises(verify, VAN, NEW, V_INTS, dict(FINAL, Wand_Cast_Left_Charged=V_INTS["Wand_Cast_Left_Charged"]), V_ROOTS, DIV)
    check(e and "checks 25 Mana but spends 5" in e, "X: spell_verify: the 0.4.8 state (wand check 25, spend 5) is refused: %s" % e)
    e = raises(verify, VAN, NEW, V_INTS, dict(FINAL, Staff_Cast_Summon_Charged=V_INTS["Staff_Cast_Summon_Charged"]), V_ROOTS, DIV)
    check(e and "without a check first" in e, "X: spell_verify: a staff that still casts without a check is refused: %s" % e)
    e = raises(verify, VAN, dict(NEW, W=world(0, 10, 0, 20, -10, 0)["W"]), V_INTS, FINAL, V_ROOTS, DIV)
    check(e and "expected vanilla / 5" in e, "X: spell_verify: a cast whose spend is not vanilla / 5 (here: made free) is refused: %s" % e)
    print("X. SPELL GEN block exec'd on synthetic items: spell_plan (Parent / shape / rounding), spell_casts (engine rules), spell_int_plan "
          "and spell_verify (check = spend = vanilla / 5, refusals) hold")


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
    # the scratch COPY of the live data folder (the live folder is never written): xp.properties, config-history/, players/, placed/
    shutil.copytree(LIVE_DIR, os.path.join(SCRATCH, "live-copy"))
    livenow = open(LIVE, "rb").read()
    # the file as it was before the 0.4.8 move (= the 0.4.7 file): the live config history's entry "xp.properties before mana.magicBase ..."
    hdir = os.path.join(LIVE_DIR, "config-history")
    pre_name = None
    for ln in open(os.path.join(hdir, "index.log"), encoding="utf-8").read().splitlines():
        cols = ln.split("\t")
        if len(cols) >= 5 and cols[1] == "Skyy_SkyySkills/xp.properties" and cols[4].startswith("xp.properties before mana.magicBase"):
            pre_name = cols[0].replace("#", ".") + ".bak"
    if not pre_name or not os.path.isfile(os.path.join(hdir, pre_name)):
        sys.exit("the live config history has no pre-move copy of xp.properties (%s) - the migration regression needs it" % pre_name)
    live = open(os.path.join(hdir, pre_name), "rb").read()
    open(os.path.join(SCRATCH, "pre-xp.properties"), "wb").write(live)
    check(b"mana.magicBase=20\n" in live and b"mana.classBase." not in live and b"mana.classBase.Mage=30\n" in livenow
          and b"mana.magicBase=" not in livenow.replace(b"# Base Mana by class (SkyySkills 0.4.8) replaced mana.magicBase=", b""),
          "L: the live file was moved by 0.4.8 (table, no old pair) and the history kept the 0.4.7 file (%s)" % pre_name)
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
    check(c["staff"] == 10 and c["wand"] == 5 and c["none"] == -1, "S: ManaCost.costOf staff 10 / wand 5 / sword -1 (0.4.9: the real checks)")
    # I + W
    check_int_overrides()
    g_ = D["gate"]
    check(g_["int_n"] == 8 and g_["int_ids"] == sorted(INT_WANT) and all(
        g_["int_kind"][i] == INT_WANT[x][0] and g_["int_old"][i] == (-1 if INT_WANT[x][1] is None else INT_WANT[x][1])
        and g_["int_new"][i] == INT_WANT[x][2] for i, x in enumerate(g_["int_ids"])),
        "I: ManaCost's interaction table = the research's fix list: %s" % list(zip(g_["int_ids"], g_["int_kind"], g_["int_old"], g_["int_new"])))
    check_gate_sim(g_)
    # L
    lcd = D["livecopy"]
    check(lcd["same"] and not lcd["changed"] and lcd["n"] >= 2 and lcd["hist"], "L: two starts on the copy of the live Skyy_SkyySkills folder "
          "(%d files, %d in config-history, %d player files) wrote nothing: %s" % (lcd["n"], len(lcd["hist"]), lcd["players"], lcd["changed"][:4]))
    for k_, run in enumerate(lcd["runs"]):
        check(run[0] == ["", "nothing to move"] and run[1] == "" and run[2] == "Mage 30, Priest 30" and run[3] is False and run[4] == ""
              and run[5] == 30.0 and run[6] == 30.0, "L: start %d on the live copy: ManaMig finds nothing to move, no history entry, table Mage 30, "
                                                     "Priest 30, no WARN: %s" % (k_ + 1, run))
    print("L. live data copy (%d files): 2 starts, ManaMig %r both times, nothing written, table %s" % (
        lcd["n"], lcd["runs"][0][0][1], lcd["runs"][0][2]))
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
    # 0.4.9: a kit weapon that spends 0 behind a check (Crystal_Red behind the staff check 10, the plain Blunderbuss behind the flintlock 10)
    WF = ("Base Mana check: Mage starts with 5 max Mana, but the kit weapon Weapon_Staff_Crystal_Red needs 10 Mana to cast (it spends 0) (kit "
          "from SkyyClasses) - a new Mage cannot cast it. Raise Mage in Server Setup > Skills > Overall and Mana > Base Mana by class. Nothing "
          "was changed automatically.")
    IF5 = ("Base Mana check (kits from SkyyClasses, spell costs /5): Priest 30 Mana >= Weapon_Gun_Blunderbuss 10 (spends 0: free while Mana is "
           "10+), Weapon_Wand_Wood 5 (6 casts); 1 class(es) below their kit weapon's Mana cost (see the WARN)")
    IF10 = ("Base Mana check (kits from SkyyClasses, spell costs /5): Mage 10 Mana >= Weapon_Staff_Crystal_Red 10 (spends 0: free while Mana is "
            "10+), Priest 30 Mana >= Weapon_Gun_Blunderbuss 10 (spends 0: free while Mana is 10+), Weapon_Wand_Wood 5 (6 casts)")
    check(g["free5"] == [WF, IF5], "G: Crystal_Red kit at 5 Mana -> WARN 'needs 10 Mana to cast (it spends 0)': %s" % g["free5"])
    check(g["free10"] == [IF10], "G: Crystal_Red kit at 10 Mana -> quiet, 'spends 0: free while Mana is 10+': %s" % g["free10"])
    tk = g["tick"]
    check(tk[0] == [False, ""] and tk[1][0] is True and tk[1][1] is False and tk[1][2] == I30 and tk[2] == "x" and tk[3] == I30
          and tk[4] == [I30, 7], "G: tick: not before 10 s, runs once, again after a config load and after a SkyyClasses epoch change: %s" % tk)
    print("G. guard lines (real checks):\n   WARN %s\n   INFO %s\n   INFO %s\n   WARN %s\n   WARN %s\n   INFO %s" % (W5, I5, I30, WL, WF, IF10))
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
    KNI = ("Cast checks /5: the game's interaction assets could not be read to see which pack each of the 8 overridden interactions comes "
           "from - not checked")
    check(k["tick"] == [0, 1, 1, 1, 2, 2, [6, True, KN], 6, [False, False, KNI]],
          "K: pack check (items + interactions) at 10 s, then every 10 s, 6 tries, then one INFO each and done: %s" % k["tick"])
    check(k["ibare"] == ["", "the game's interaction assets could not be read"], "K: the bare JVM's intCheck -> no line, try again: %s" % k["ibare"])
    check(k["engine_ok"] == ["info", KA, PKW, PKW, PKW], "K: engine DefaultAssetMap, vanilla then this jar -> all active: %s" % k["engine_ok"][:1])
    KE = ("Spell costs /5: 2 of 32 item overrides are NOT active - another asset pack wins for %s (Hytale:Hytale), %s (Other:Mod). Those items "
          "keep that pack's Mana cost (of two packs with the same item, the one loaded last wins); 30 active." % (ids[0], ids[3]))
    check(k["engine_clash"] == ["warn", KE, "Hytale:Hytale", PKW, "Other:Mod"],
          "K: engine DefaultAssetMap, vanilla -> this jar (without one item) -> a later pack (one item): the last pack loaded wins: %s" % k["engine_clash"])
    print("K. pack check (engine DefaultAssetMap.putAll, last pack loaded wins):\n   INFO %s\n   WARN %s\n   INFO %s" % (KA, KE, KN))
    # K2 (0.4.9): the interaction pack check + the live cast checks
    ki = D["ipack"]
    ii = ki["ids"]
    check(ii == sorted(INT_WANT), "K2: ManaCost.INT_IDS = the 8 interaction overrides: %s" % ii)
    LV = ("; live cast checks Gun_Shoot_Flintlock_Charged 10, Spellbook_Cast_Hurl_Charged 20, Staff_Cast_Summon_Charged 10, "
          "Wand_Cast_Left_Charged 5 (= what each cast spends)")
    IA = "Cast checks /5: all 8 interaction overrides are active (the game's interaction assets take them from %s)" % PKW
    check(ki["all"] == ["info", IA + LV], "K2: all active, live checks = spends -> one INFO: %s" % ki["all"])
    IO = ("Cast checks /5: 1 of 8 interaction overrides are NOT active - another asset pack wins for Wand_Cast_Left_Charged (Other:Mod). Those "
          "casts keep that pack's Mana check / spend (of two packs with the same interaction, the one loaded last wins); 7 active; live cast "
          "checks Gun_Shoot_Flintlock_Charged 10, Spellbook_Cast_Hurl_Charged 20, Staff_Cast_Summon_Charged 10 (= what each cast spends).")
    check(ki["other"] == ["warn", IO], "K2: another pack wins the wand check -> one WARN naming it: %s" % ki["other"])
    IB = ("Cast checks /5: all 8 interaction overrides come from %s; the live cast check differs: Staff_Cast_Summon_Charged is not a Mana check "
          "(not a StatsCondition; it should check 10), Wand_Cast_Left_Charged checks 25 instead of 5 - the Mana a cast needs is not what it "
          "spends; live cast checks Gun_Shoot_Flintlock_Charged 10, Spellbook_Cast_Hurl_Charged 20 (= what each cast spends)." % PKW)
    check(ki["bad"] == ["warn", IB], "K2: this jar's pack but a live check that differs / is not a StatsCondition -> WARN: %s" % ki["bad"])
    IU = IA + "; 4 live cast check(s) not readable"
    check(ki["unread"] == ["info", IU] and ki["nolive"] == ki["unread"], "K2: live checks not readable -> INFO says so: %s" % ki["unread"])
    check(ki["none"] == ["", "the game's interaction assets could not be read"] and ki["null"] == ki["none"], "K2: nothing readable -> no line")
    check(ki["miss"] == ["info", "Cast checks /5: 7 of 8 interaction overrides are active (the game's interaction assets take them from %s)%s; "
                                 "1 not in the game's interaction assets (Gun_Shoot_Cost)" % (PKW, LV)], "K2: one id missing: %s" % ki["miss"])
    check(ki["live"] == [5.0, -3.0, -2.0, -1.0, -1.0, -4.0, -4.0, 25.0],
          "K2: liveCheck on engine objects: StatsConditionInteraction Mana 5 -> 5, Stamina only -> -3, a SimpleInteraction -> -2, null / no "
          "rawCosts -> -1, decoded Mana 5 but costs null / costs without the Mana index -> -4, costs' Mana 25 (the gate's number) -> 25: %s"
          % ki["live"])
    IR = ("Cast checks /5: all 8 interaction overrides come from %s; the live cast check differs: Wand_Cast_Left_Charged has a Mana cost the "
          "engine did not resolve to the Mana stat (its gate does not check it; it should check 5) - the Mana a cast needs is not what it "
          "spends; live cast checks Gun_Shoot_Flintlock_Charged 10, Spellbook_Cast_Hurl_Charged 20, Staff_Cast_Summon_Charged 10 (= what each "
          "cast spends)." % PKW)
    check(ki["unres"] == ["warn", IR], "K2: this jar's pack, a decoded Mana cost that did not resolve (-4) -> WARN naming it: %s" % ki["unres"])
    check(ki["engine_ok"] == ["info", IA + LV, PKW, PKW], "K2: engine IndexedLookupTableAssetMap, vanilla then this jar -> all active, live "
                                                         "checks read from the winners: %s" % ki["engine_ok"])
    check(ki["engine_clash"] == ["warn", IO, PKW, "Other:Mod"], "K2: engine map, a later pack with the wand check wins it: %s" % ki["engine_clash"])
    IV = ("Cast checks /5: 8 of 8 interaction overrides are NOT active - another asset pack wins for %s. Those casts keep that pack's Mana check / "
          "spend (of two packs with the same interaction, the one loaded last wins); 0 active." % ", ".join("%s (Hytale:Hytale)" % x for x in ii))
    check(ki["engine_vanilla_only"] == ["warn", IV, "Hytale:Hytale", "Hytale:Hytale"], "K2: engine map with only vanilla -> WARN: %s" % ki["engine_vanilla_only"][:1])
    print("K2. interaction pack check (engine IndexedLookupTableAssetMap.putAll, StatsConditionInteraction rawCosts + resolved costs):\n"
          "   INFO %s\n   WARN %s\n   WARN %s\n   WARN %s\n   INFO %s" % (IA + LV, IO, IB, IR, KNI))
    # Q
    check_pin_bump()
    # P
    pk = D["perks"]
    wantp = [[30.0, 0.0], [30.0, 30.0], [30.0, 30.0], [10.0, 10.0], [30.0, 10.0], [30.0, 22.0], [30.0, 22.0]]
    check([x[1] for x in pk] == wantp, "P: max / current Mana: %s" % pk)
    print("P. max Mana on the engine's stat classes: " + "; ".join("%s %s/%s" % (x[0], x[1][1], x[1][0]) for x in pk))
    # E (review finding 5): the 8 generated files decoded by the engine's own Interaction codec
    ec = D["codec"]
    mi = ec["mana_index"][0]
    er = ec["rows"]
    check(sorted(er) == sorted(INT_WANT), "E: the jar's 8 interaction files were decoded: %s" % sorted(er))
    clean = lambda r: "err" not in r and not r["failed"] and r["results"] is None and r["unknown"] == []
    for iid in sorted(INT_WANT):
        kind, old, new_ = INT_WANT[iid]
        r = er.get(iid, {})
        rj, rv = r.get("jar", {"err": "missing"}), r.get("van", {"err": "missing"})
        check(clean(rj) and clean(rv), "E: %s decodes through the engine codec with no validation result and no unknown key (jar %s / vanilla %s)"
              % (iid, rj.get("err") or (rj["results"], rj["unknown"]), rv.get("err") or (rv["results"], rv["unknown"])))
        if "err" in rj or "err" in rv:
            continue
        if kind == "drain":
            nj = "unknownEntityStats={Mana=>%.1f}, entityStats={%d=>%.1f}" % (new_, mi, new_)
            nv = "unknownEntityStats={Mana=>%.1f}, entityStats={%d=>%.1f}" % (old, mi, old)
            check(rj["cls"] == rv["cls"] == "ChangeStatInteraction" and rj["str"].count(nj) == 1 and rj["str"].replace(nj, nv) == rv["str"]
                  and rj["live"] == -2.0, "E: %s = a ChangeStat of Mana %d resolved to the Mana stat (vanilla %d), otherwise the engine "
                                          "object equals vanilla's: %s" % (iid, new_, old, rj["str"][:160]))
            continue
        nj = "rawCosts={Mana=>%.1f}, costs={%d=>%.1f}" % (new_, mi, new_)
        check(rj["cls"] == "StatsConditionInteraction" and rj["str"].count(nj) == 1 and rj["live"] == float(new_),
              "E: %s = a StatsCondition whose resolved Mana check (the number canAfford compares) is %d, and liveCheck on the decoded object "
              "says %s: %s" % (iid, new_, rj["live"], rj["str"][:160]))
        if old is not None:
            nv = "rawCosts={Mana=>%.1f}, costs={%d=>%.1f}" % (old, mi, old)
            check(rv["cls"] == "StatsConditionInteraction" and rj["str"].replace(nj, nv) == rv["str"] and rv["live"] == float(old),
                  "E: %s: the decoded object equals vanilla's except the Mana check %d -> %d: %s" % (iid, old, new_, rv["str"][:160]))
        else:
            pre = ("StatsConditionInteraction{}StatsConditionBaseInteraction{%s, lessThan=false, lenient=false, valueType=Absolute}"
                   "SimpleInstantInteraction{} " % nj)
            wand = er.get("Wand_Cast_Left_Charged", {}).get("jar", {}).get("str", "")
            check(rv["cls"] == "SimpleInteraction" and rv["live"] == -2.0 and rj["str"] == pre + rv["str"]
                  and wand.split("SimpleInstantInteraction{} ")[0] == pre.split("SimpleInstantInteraction{} ")[0].replace(
                      "=>%.1f}, costs={%d=>%.1f}" % (new_, mi, new_), "=>5.0}, costs={%d=>5.0}" % mi),
                  "E: %s: vanilla decodes as a Simple interaction (no check); the jar's decodes as the wand check's StatsCondition (Mana %d, "
                  "resolved) wrapped around exactly the vanilla step (RunTime, Next, Failed, rules ...): %s" % (iid, new_, rj["str"][:200]))
    ty, si = ec["typo"], ec["simple"]
    check("err" not in ty and ty["unknown"] == ["Costz"] and ty["live"] == 5.0, "E: control - a mistyped key is reported as unknown: %s" % ty.get("unknown", ty))
    check("err" not in si and si["cls"] == "SimpleInteraction" and si["unknown"] == ["Costs"] and si["live"] == -2.0,
          "E: control - the staff step typed back to Simple ignores Costs (an unknown key there; research 1.2): %s" % si.get("unknown", si))
    print("E. engine Interaction codec (Mana stat index %d): %s; controls: typo -> unknown %s, Simple + Costs -> unknown %s" % (
        mi, ", ".join("%s %s %s" % (k_, er[k_]["jar"].get("cls", "?"), er[k_]["jar"].get("live")) for k_ in sorted(er)),
        ty.get("unknown"), si.get("unknown")))
    # F
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    added = sorted(set(zn.namelist()) - set(zo.namelist()))
    check(not (set(zo.namelist()) - set(zn.namelist())), "F: no entry of 0.4.8 is gone")
    check([n for n in added if not n.startswith("Server/")] == [] and len(added) == 8
          and all(n.startswith("Server/Item/Interactions/") for n in added), "F: new entries = only the 8 interaction overrides: %s" % added)
    diff = sorted(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    bc = json.load(open(bco))
    EXPECT = {"com/skyy/skills/ManaCost.class", "com/skyy/skills/ManaGuard.class", "com/skyy/skills/SkyySkillsPlugin.class", "manifest.json"}
    check(EXPECT <= set(diff), "F: ManaCost, ManaGuard, SkyySkillsPlugin and the manifest changed: %s" % diff)
    extra = [n for n in diff if n not in EXPECT]
    for n in extra:
        cc = bc.get(n)
        check(cc is not None and not cc["new"] and not cc["gone"] and cc["fields_same"] and cc["version_only"],
              "F: %s differs by more than the version string: %s" % (n, cc))
    check(sorted(extra) == ["com/skyy/skills/CfgFn.class", "com/skyy/skills/CfgRows.class", "com/skyy/skills/SkillCfg.class"],
          "F: the version carriers (version string only): %s" % extra)
    for n in ("ManaMig", "OverallCfg", "Overall", "SkillKit", "SkillTick", "SkillsPage", "StatsPage", "OverallPage", "Perks", "SkillStore", "SkillXp",
              "AcroSys", "OverallFn", "Xbow"):
        nn = "com/skyy/skills/%s.class" % n
        if nn in zo.namelist():
            check(nn not in diff, "F: %s is byte-identical" % n)
    mc = bc.get("com/skyy/skills/ManaCost.class", {})
    check(mc.get("changed") == ["<clinit>()V", "costOf(Ljava/lang/String;)I"]
          and sorted(mc.get("new", [])) == ["gi(Ljava/lang/String;)I", "spendOf(Ljava/lang/String;)I"]
          and not mc.get("gone") and not mc.get("fields_gone")
          and sorted(mc.get("fields_new", [])) == sorted(["GN I", "GIDS [Ljava/lang/String;", "GCHECK [Ljava/lang/String;", "GATE_OLD [I", "GATE [I",
                                                          "SPEND_OLD [I", "SPEND [I", "INT_N I", "INT_IDS [Ljava/lang/String;",
                                                          "INT_KIND [Ljava/lang/String;", "INT_OLD [I", "INT_NEW [I"]),
          "F: ManaCost: costOf changed (the real check), gi / spendOf + the gate / interaction tables new, nothing gone: %s" % mc)
    mgd = bc.get("com/skyy/skills/ManaGuard.class", {})
    # packReport differs only by the PACK constant javassist inlined ("Skyy:0.4.8 SkyySkills" -> "Skyy:0.4.9 SkyySkills"); <clinit> = the new fields
    check(sorted(mgd.get("changed", [])) == ["<clinit>()V", "packReport([Ljava/lang/String;)[Ljava/lang/String;", "packTick()V", "run()[Ljava/lang/String;"]
          and "packReport([Ljava/lang/String;)[Ljava/lang/String;" in mgd.get("vo", [])
          and sorted(mgd.get("new", [])) == ["intCheck()[Ljava/lang/String;", "intReport([Ljava/lang/String;[F)[Ljava/lang/String;",
                                             "liveCheck(Ljava/lang/Object;)F"] and not mgd.get("gone") and not mgd.get("fields_gone")
          and sorted(mgd.get("fields_new", [])) == ["INT_DONE Z", "INT_LAST Ljava/lang/String;", "ITEMS_DONE Z", "RAW Ljava/lang/reflect/Field;",
                                                    "RES Ljava/lang/reflect/Field;"],
          "F: ManaGuard: run / packTick changed, liveCheck / intReport / intCheck new, nothing gone: %s" % mgd)
    pl = bc.get("com/skyy/skills/SkyySkillsPlugin.class", {})
    check(pl.get("changed") == ["setup()V"] and not pl.get("new") and not pl.get("gone"), "F: SkyySkillsPlugin: only setup() changed (ready line): %s" % pl)
    mo, mn = json.loads(zo.read("manifest.json")), json.loads(zn.read("manifest.json"))
    kd = sorted(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k))
    check(kd == ["Description", "Name", "Version"] and mn["IncludesAssetPack"] is True and mn["Version"] == VERSION,
          "F: manifest: only %s differ" % kd)
    check(not [n for n in zn.namelist() if n.endswith(".ui")], "F: no .ui files (inline pages only)")
    print("F. class bytes: differ %s; new entries %d interaction overrides; methods: %s" % (
        ", ".join(n.split("/")[-1] for n in diff), len(added),
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
