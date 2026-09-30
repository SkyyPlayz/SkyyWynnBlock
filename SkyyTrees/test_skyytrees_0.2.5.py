"""Bare-JVM + render check for SkyyTrees 0.2.5 (the vanilla-look restyle of the /tree page), kept next to the build so the build
report's JVM and render claims can be re-run by anyone. SkyyTrees had no committed harness (the 0.2.4 checks lived in a deleted
scratch folder), so this one carries the pilots' page-state machinery forward (SkyyClasses/test_skyyclasses_0.1.8.py part Y: the
markup model, text fit and contrast code are the same) and adds the old-vs-new click check.

    python SkyyTrees/test_skyytrees_0.2.5.py [--jar <SkyyTrees-0.2.5.jar>] [--old <SkyyTrees-0.2.4.jar>] [--dir <scratch>] [--keep]

Build the jar first (python tools/trees_0_2_5_patch.py, then python SkyyTrees/build_skyytrees_0.2.5.py). Child processes start fresh
JVMs (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar read-only + ONE mod jar; TEMP / TMP / java.io.tmpdir in the
scratch folder; on a JDK 26+ JRE also --enable-final-field-mutation=ALL-UNNAMED, JEP 500: the PlayerRef set-up below writes its
two final fields uuid / username - allowed and silent instead of the "mutated reflectively" warning a future JRE turns into an
error; an older JRE does not know the option and does not get it) and the parent compares:
  A  every class of both jars loads and verifies (-Xverify:all)
  B  page states: the REAL TreePage.build of the 0.2.5 AND the 0.2.4 jar (the page from its own constructor with an Unsafe-allocated
     PlayerRef; TreeData objects installed in TreeStore.DATA; bridge skill:fn:level / skill:fn:xp / skill:<uuid>; TreeCfg overrides)
     for 72 grid states (6 trees x the 12 selectable nodes on a per-tree profile: locked, unlockable, owned, off, maxed, coming later,
     can / cannot pay) + special states (no SkyySkills, no XP bridge, unreadable file, negative balance, armed respec, every result
     text kind, huge Dust / tokens, a server-disabled node, Exploration unknown to SkyySkills, out-of-range tree / node). Per state:
     identical event bindings (type, selector, EventData, lock flag, order), no 0.2.4 element id missing, every 0.2.4 text still
     shown (inline Text or b.set).
  C  the 0.2.5 markup as the client gets it: SUI.check_markup / check_page, SUI.assert_proven on every appended markup, binding targets
     exist, only kit colours + the six tree colours (TCOLOR) in the page markup - UI_DATA_COLORS is split into its page part (TCOLOR)
     and its chat part (the Message.color literals, each checked to be a real chat colour of the script and never allowed on the
     page), no FlexWeight / WrapMaxLines / LetterSpacing / LayoutMode Right, Center, Full / ItemGrid; the page root 1440 x 892;
     the node grid on the vanilla list well (#SkyyTrGrid: #000000(0.15), padding 4); a layout model (every child inside its parent,
     the body children fill 820 px exactly); every label's text
     measured with the client's Nunito Sans / Lexend advances (read-only) fits (one line: its width; wrapped: its height at 1.364 em
     + 0.1 em); every non-button label >= 3.0:1 on its effective background (the ContainerPatch centre pixel decoded from Assets.zip +
     the colour / button-style backgrounds and full covers above it); the result line colour = infoColor() of the message class.
  D  clicks: the same scripted handleDataEvent sequences (select, unlock, level up, refuse, toggle, arm + respec with a coin price,
     the respec cooldown, tabs, garbage payloads, < Skills without SkyySkills, an unreadable file, the draft slots) in both jars:
     identical page state (tree, node, message, arm), node levels / off flags / respec times, coin calls and dirty files after
     every click.
  E  class bytes 0.2.4 vs 0.2.5: only TreePage (build rewritten, line() gone, infoColor() new, the six old-look colour fields and
     their static init gone), SkyyTreesPlugin.setup (the ready line with the kit id) and the version strings (TreeCfg's default
     file header, the config kit classes) differ; every asset file (the 87 swing-speed / chop JSON files) and every other class is
     byte-identical; same jar entries; manifest: only the version. The ready line's kit id is the id of tools/skyyui.py on disk
     (SUI.kit_id()): a jar built on another kit fails - rebuild it on the final committed kit before the deploy round.
  F  the state children print no final-field mutation warning.
Not testable without the game (UNVERIFIED in the build report): the look itself (the kit's base probe pages base1-base4 first), the
client parsing the page, real clicks / sounds. Nothing is deployed. Default scratch folder: tools/dev/scratch/skyytrees-025
(git-ignored). At the end (unless --keep) the harness removes only what it made: the whole folder when it created it, otherwise
just its own entries (tmp, players-old / players-new, states-*.json, bytecode.json) that were not there before - a --dir that
points at a real folder is never wiped. Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, json, zipfile, struct, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.2.5", "0.2.4"
PKG = "com.skyy.trees."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyytrees-025")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyTrees-%s.jar" % OLD_VERSION)))
SCRIPT = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


PREFIX = "SkyyTr"
PAGE_W, PAGE_H = 1440, 892
BODY_ID, BODY_INNER_H = "SkyyTrRoot", 892 - 38 - 2 * 17        # 820
ASSET_JSON = 87                                                 # the swing-speed / chop asset JSON files in both jars
# the harness's own entries in the scratch folder (the only things it removes from a folder it did not create)
OWN_ENTRIES = ("tmp", "players-old", "players-new", "states-old.json", "states-new.json", "bytecode.json")
MIN_CONTRAST = 3.0
TREES = ["Mining", "Foraging", "Farming", "Cooking", "Acrobatics", "Exploration"]
EXPECTED_DIFF = {"com/skyy/trees/TreePage.class", "com/skyy/trees/SkyyTreesPlugin.class", "com/skyy/trees/TreeCfg.class",
                 "manifest.json"}      # + the config kit classes (com/skyy/trees/Cfg*.class) when they embed the version (checked)

# ---- the per-tree profiles of the grid states (levels / XP chosen so every node state shows up somewhere)
PROFILES = {
    "Mining": dict(level=34, xp=2000000, nodes={"MSpeed": 10, "MFortune": 7, "MWisdom": 15, "MStamina": 3, "MVeins": 2},
                   off=["MWisdom"]),
    "Foraging": dict(level=60, xp=200000000, nodes={"FSpeed": 10, "FFortune": 20, "FVigor": 5, "FSap": 2, "FCoins": 1, "FSpread": 3,
                                                   "FSpeed2": 4, "FFeller": 5}, off=["FSap"]),
    "Farming": dict(level=20, xp=90000, nodes={"AFortune": 3, "ASeeds": 1, "AHearty": 2}, off=[]),
    "Cooking": dict(level=10, xp=30000, nodes={"CGourmet": 25, "CBatch": 1}, off=["CBatch"]),
    "Acrobatics": dict(level=45, xp=5000000, nodes={"RSpeed": 25, "RJump": 4, "RStamina": 2, "RDodge": 1, "RDouble": 3, "RFall2": 2,
                                                    "RStamina3": 1}, off=["RDouble"]),
    "Exploration": dict(level=5, xp=4000, nodes={"EHeart": 2}, off=[]),
}


def st(name, tree=0, sel=1, msg="", armed=False, levels="profile", xps="profile", nodes=None, off=None, bad=False, en_off=(),
       extra_dust=0, extra_tokens=0, known=None, respec_coins=0):
    """one page state: levels / xps = "profile" (each tree's PROFILES level / xp), a {tree: n} dict, or None (no bridge Function);
    nodes / off = {"Tree.Id": level} / ["Tree.Id"] (None = every profile's nodes / off flags)."""
    if nodes is None:
        nodes = dict(("%s.%s" % (tn, k), v) for tn, p in PROFILES.items() for k, v in p["nodes"].items())
    if off is None:
        off = ["%s.%s" % (tn, k) for tn, p in PROFILES.items() for k in p["off"]]
    if levels == "profile":
        levels = dict((tn, p["level"]) for tn, p in PROFILES.items())
    if xps == "profile":
        xps = dict((tn, p["xp"]) for tn, p in PROFILES.items())
    return dict(name=name, tree=tree, sel=sel, msg=msg, armed=armed, levels=levels, xps=xps, nodes=nodes, off=list(off), bad=bad,
                en_off=list(en_off), extra_dust=extra_dust, extra_tokens=extra_tokens, known=known, respec_coins=respec_coins)


RESULT_TEXTS = [  # (message, the result colour kind infoColor must give it)
    ("Unlocked Gem Finder!", "success"), ("Mining Speed is now level 11", "success"), ("Tree Feller is now level 6 - MAX", "success"),
    ("Heavy Pick turned off - its level is kept", "success"), ("Heavy Pick turned on", "success"),
    ("Respec done - every Mining token and all your Mining Dust are back", "success"),
    ("Click Respec again within 10 s to reset the whole Acrobatics tree (everything spent comes back)", "warning"),
    ("Node S7 of the Exploration tree is coming later - Skyy designs the rest of this draft tree later", "info"),
    ("Needs 1,234,567 more Foraging Dust", "error"), ("Vein Burst needs Mining 60", "error"), ("Mining Fortune is already maxed", "error"),
    ("You can respec Mining again in 10 min", "error"), ("SkyySkills is not installed - there is no skills page", "error"),
    ("A respec costs 5,000 coins - you do not have enough", "error"), ("", "info"),
    ("Your Exploration balance is negative (costs changed) - respec first, it is free right now", "error")]

STATES = [st("grid %s S%d" % (tn, s), tree=t, sel=s) for t, tn in enumerate(TREES) for s in range(1, 13)]
STATES += [
    st("no skills", levels=None, xps=None),
    st("no xp bridge", tree=1, sel=12, xps=None),
    st("unreadable file", tree=2, sel=4, bad=True, nodes={}, off=[]),
    st("negative balance", tree=0, sel=5, levels={"Mining": 5}, xps={"Mining": 100}),
    st("armed respec acrobatics", tree=4, sel=7, armed=True, msg=RESULT_TEXTS[6][0]),
    st("armed respec exploration", tree=5, sel=1, armed=True),
    st("huge dust and tokens", tree=1, sel=12, extra_dust=123456789012, extra_tokens=1000),
    st("server-disabled node", tree=0, sel=10, en_off=["Mining.MHeavy"]),
    st("exploration unknown", tree=5, sel=2, known="Mining:34,Foraging:60,Farming:20,Cooking:10,Acrobatics:45"),
    st("tree out of range", tree=9, sel=0),
    st("node out of range", tree=3, sel=13),
    st("level 100 all maxed", tree=0, sel=12, levels={"Mining": 100}, xps={"Mining": 10 ** 12},
       nodes=dict(("Mining." + k, v) for k, v in {"MSpeed": 25, "MFortune": 20, "MWisdom": 15, "MStamina": 10, "MGems": 10, "MVeins": 15,
                                                    "MCoins": 10, "MSpread": 10, "MRunner": 10, "MHeavy": 20, "MBars": 10, "MVein": 5}.items()),
       off=[]),
    st("fresh level 0", tree=2, sel=1, levels={"Farming": 0}, xps={"Farming": 0}, nodes={}, off=[]),
]
STATES += [st("result %d" % n, tree=n % 6, sel=1 + n % 12, msg=m) for n, (m, _k) in enumerate(RESULT_TEXTS)]

# ---- D: click sequences (payloads as the client sends them: {"a":"<payload>"})
CLICKS = [
    ("mining buy toggle respec", st("c1", tree=0, sel=1, respec_coins=500),
     ["trnode5", "trbuy", "trbuy", "trtoggle", "trtoggle", "trnode12", "trbuy", "trnode3", "trbuy", "trtoggle", "trrespec", "trrespec",
      "trrespec", "trrespec", "trtab4", "trnode7", "trbuy", "trtoggle", "trtab9", "trnode13", "junk", "trback"]),
    ("foraging feller", st("c2", tree=1, sel=12), ["trbuy", "trnode10", "trbuy", "trbuy", "trnode12", "trbuy", "trtab1", "trnode11", "trbuy"]),
    ("exploration draft slots", st("c3", tree=5, sel=6), ["trbuy", "trtoggle", "trnode4", "trbuy", "trrespec", "trrespec", "trnode2", "trbuy"]),
    ("no skills", st("c4", levels=None, xps=None), ["trback", "trbuy", "trnode2", "trbuy", "trrespec", "trrespec"]),
    ("unreadable file", st("c5", tree=2, bad=True, nodes={}, off=[]), ["trbuy", "trtoggle", "trrespec", "trrespec", "trtab0", "trbuy"]),
    ("negative balance respec", st("c6", tree=0, sel=1, levels={"Mining": 5}, xps={"Mining": 100}, respec_coins=500),
     ["trbuy", "trrespec", "trrespec", "trbuy"]),
]


# ============================================================================================================== child JVMs
def _jre_major(jvm):
    """The major Java version of the JRE a jvm.dll belongs to (<home>/bin/server/jvm.dll -> <home>/release JAVA_VERSION); 0 =
    unknown (then no version-specific option is passed)."""
    home = os.path.dirname(os.path.dirname(os.path.dirname(jvm)))
    try:
        m = re.search(r'^JAVA_VERSION="(\d+)', open(os.path.join(home, "release"), encoding="utf8", errors="replace").read(), re.M)
    except OSError:
        return 0
    return int(m.group(1)) if m else 0


def _jvm_start(jars, extra_cp=()):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    opts = ["-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
    if _jre_major(jvm) >= 26:       # JEP 500 (JDK 26+): setf() below writes PlayerRef's final uuid / username - allow it explicitly
        opts.append("--enable-final-field-mutation=ALL-UNNAMED")      # (a JRE before 26 rejects the unknown option: not passed there)
    jpype.startJVM(jvm, *opts, classpath=[B.SERVER_JAR] + list(jars) + list(extra_cp), convertStrings=True)
    return B


def run_states(jar, out, tag):
    from jpype import JClass, JImplements, JOverride
    _jvm_start([jar])
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    loaded, load_fails = 0, []
    for n in names:
        try:
            Cls.forName(n, True, loader)
            loaded += 1
        except Exception as e:
            load_fails.append("%s: %s" % (n, e))
    res = {"jar": jar, "classes": len(names), "loaded": loaded, "load_fails": load_fails, "states": {}, "clicks": {}, "colors": {}}
    if load_fails:
        json.dump(res, open(out, "w"), indent=1)
        os._exit(0)
    Page, Store, Cfg, Defs, Data = (JClass(PKG + x) for x in ("TreePage", "TreeStore", "TreeCfg", "TreeDefs", "TreeData"))
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UUID, Paths, Long, Integer, Boolean = (JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"),
                                           JClass("java.lang.Integer"), JClass("java.lang.Boolean"))
    System = JClass("java.lang.System")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    @JImplements("java.util.function.Function")
    class ByTree(object):
        def __init__(self, table, boxed):
            self.table, self.boxed = table, boxed

        @JOverride
        def apply(self, o):
            return self.boxed(int(self.table.get(str(o[1]), 0)))

    COIN_CALLS = []

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            COIN_CALLS.append(int(o[1].longValue()))
            return Boolean.TRUE

    pdir = os.path.join(SCRATCH, "players-" + tag)
    os.makedirs(pdir, exist_ok=True)
    Store.DIR = Paths.get(pdir)
    bridge = Store.bridge()
    me = UUID(0x7ee5, 25)
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    en0 = [bool(x) for x in Cfg.EN]

    def setup(spec):
        for k in list(bridge.keySet()):
            if str(k).startswith(("skill:", "coins:", "profile", "tree:", "move:")):
                bridge.remove(k)
        Store.DATA.clear()
        Store.DIRTY.clear()
        for fn in os.listdir(pdir):
            os.remove(os.path.join(pdir, fn))
        for i, v in enumerate(en0):
            Cfg.EN[i] = v
        for key in spec["en_off"]:
            Cfg.EN[int(Defs.idx(key))] = False
        Cfg.EXTRA_DUST = spec["extra_dust"]
        Cfg.EXTRA_TOKENS = spec["extra_tokens"]
        Cfg.RESPEC_COINS = spec["respec_coins"]
        if spec["levels"] is not None:
            bridge.put("skill:fn:level", ByTree(spec["levels"], Integer))
        if spec["xps"] is not None:
            bridge.put("skill:fn:xp", ByTree(spec["xps"], Long))
        if spec["known"] is not None:
            bridge.put("skill:" + str(me), spec["known"])
        bridge.put("coins:fn:take", Coins())
        del COIN_CALLS[:]
        d = Data()
        for key, v in spec["nodes"].items():
            d.lv[int(Defs.idx(key))] = v
        for key in spec["off"]:
            d.off[int(Defs.idx(key))] = True
        d.bad = bool(spec["bad"])
        Store.DATA.put(str(me), d)
        page = Page(pr, spec["tree"])
        page.sel = spec["sel"]
        page.msg = spec["msg"]
        if spec["armed"]:
            page.armT = spec["tree"]
            page.armAt = System.currentTimeMillis()
        return page, d

    def render(page):
        b, ev = UCB(), UEB()
        try:
            page.build(None, b, ev, None)
            err = None
        except Exception as e:
            err = str(e)
        cmds = [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]
        evs = [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data),
                bool(e.locksInterface)] for e in ev.getEvents()]
        return {"error": err, "commands": cmds, "events": evs}

    for spec in STATES:
        page, _d = setup(spec)
        res["states"][spec["name"]] = render(page)
    for name, spec, clicks in CLICKS:
        page, d = setup(spec)
        steps = []
        for p in clicks:
            err = None
            try:
                page.handleDataEvent(None, None, '{"a":"%s"}' % p)
            except Exception as e:
                err = str(e)[:200]
            steps.append({"click": p, "err": err, "tree": int(page.tree), "sel": int(page.sel), "msg": None if page.msg is None else str(page.msg),
                          "armT": int(page.armT), "armed": int(page.armAt) > 0, "lv": [int(x) for x in d.lv], "off": [bool(x) for x in d.off],
                          "respec": [int(x) > 0 for x in d.respecAt], "credit": [int(x) for x in d.credit], "coins": list(COIN_CALLS),
                          "dirty": sorted(str(k) for k in Store.DIRTY.keySet())})
        res["clicks"][name] = {"steps": steps, "after": render(page)}
    if hasattr(Page, "infoColor"):
        for m, _k in RESULT_TEXTS:
            res["colors"][m] = str(Page.infoColor(m))
        res["colors"][None] = str(Page.infoColor(None))
    for i, v in enumerate(en0):
        Cfg.EN[i] = v
    json.dump(res, open(out, "w"), indent=1)
    sys.stdout.flush()
    os._exit(0)          # the scheduler threads a respec may start (HytaleServer.SCHEDULED_EXECUTOR) must not keep the child alive


# ============================================================================================ child: bytecode method compare (javassist)
def vnorm(text):
    """a listing / constant with every version token as V: the default file header says "SkyyTrees 0.2.5" where 0.2.4 said
    "SkyyTrees 0.2.4", while its history comments ("# 0.2.4: ...") name 0.2.4 in both - so both versions map to V on both sides"""
    return text.replace(OLD_VERSION, "V").replace(VERSION, "V")


def run_bytecode(old, new, out):
    import skyybuild as B
    from jpype import JClass
    _jvm_start([], [B.JAVASSIST])
    ClassPool, BAIS = JClass("javassist.ClassPool"), JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def listing(pool, data):
        cc = pool.makeClass(BAIS(data))
        ms = {}
        behaviors = list(cc.getDeclaredBehaviors())
        if cc.getClassInitializer() is not None:
            behaviors.append(cc.getClassInitializer())
        for mm in behaviors:
            key = "%s%s" % (mm.getName(), mm.getSignature())
            if mm.getMethodInfo().getCodeAttribute() is None:
                ms[key] = ""
                continue
            it = mm.getMethodInfo().getCodeAttribute().iterator()
            cpool = mm.getMethodInfo().getConstPool()
            lines = []
            while it.hasNext():
                ln = str(IP.instructionString(it, it.next(), cpool))
                ln = re.sub(r"#\d+ = ", "", ln).replace("ldc_w ", "ldc ")
                ln = re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln)
                lines.append(ln)
            ms[key] = "\n".join(lines)
        fields = sorted("%s %s" % (f.getName(), f.getSignature()) for f in list(cc.getDeclaredFields()))
        consts = {}
        for f in list(cc.getDeclaredFields()):
            ca = f.getFieldInfo().getConstantValue()
            if ca:
                consts[str(f.getName())] = str(cc.getClassFile().getConstPool().getLdcValue(ca))
        return ms, fields, consts

    zo, zn = zipfile.ZipFile(old), zipfile.ZipFile(new)
    res = {}
    for n in sorted(set(zo.namelist()) & set(zn.namelist())):
        if not n.endswith(".class"):
            continue
        a, b = zo.read(n), zn.read(n)
        if a == b:
            continue
        mo, fo, co = listing(ClassPool(False), a)
        mn, fn, cn = listing(ClassPool(False), b)
        changed = sorted(k for k in set(mo) & set(mn) if mo[k] != mn[k])
        consts = dict((k, [co.get(k), cn.get(k)]) for k in set(co) | set(cn) if co.get(k) != cn.get(k))
        res[n] = {"changed": changed, "gone": sorted(set(mo) - set(mn)), "new": sorted(set(mn) - set(mo)), "fields_same": fo == fn,
                  "fields_gone": sorted(set(fo) - set(fn)), "fields_new": sorted(set(fn) - set(fo)), "consts": consts,
                  "version_only": all(vnorm(mo[k]) == vnorm(mn[k]) for k in changed)
                  and all(vnorm(x or "") == vnorm(y or "") for x, y in consts.values())}
    json.dump(res, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ parent: markup model (the same code as
# SkyyClasses/test_skyyclasses_0.1.8.py part Y + SkyyProfiles/test_skyyprofiles_0.1.3.py; a Button's style background and a full-size
# cover Group now count as backgrounds for the contrast of the labels after them - the kit's icon cells)
def js(v):
    """The Java string a Set command carries (its data is JSON); non-strings come back as their JSON text."""
    try:
        x = json.loads(v)
    except Exception:
        return v
    if isinstance(x, dict) and list(x) == ["0"]:      # UICommandBuilder.set(String, String) sends {"0": value}
        x = x["0"]
    return x if isinstance(x, str) else v


_OPEN = re.compile(r"([A-Z][A-Za-z]*)(?:\s+#([A-Za-z0-9]+))?\s*\{")
_PROP = re.compile(r"([A-Za-z]+)\s*:")
_ID_RE = re.compile(r"(?:^|[;{}])\s*[A-Z][A-Za-z]*\s+#([A-Za-z0-9]+)\s*\{")
_TEXT_RE = re.compile(r'\bText: "((?:[^"\\]|\\.)*)"')
_COL_RE = re.compile(r"(?:Background|TextColor|Color):\s*(#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?:\(\s*[0-9.]+\s*\))?)")


def parse_markup(mk):
    """The element tree of one inline markup: [{"type", "id", "props": {name: raw value}, "kids": [...]}] (quotes respected)."""
    pos, n = [0], len(mk)

    def ws():
        while pos[0] < n and mk[pos[0]] in " \t\r\n":
            pos[0] += 1

    def value():
        start, depth = pos[0], 0
        while pos[0] < n:
            c = mk[pos[0]]
            if c == '"':
                pos[0] += 1
                while mk[pos[0]] != '"':
                    pos[0] += 2 if mk[pos[0]] == "\\" else 1
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c == ";" and depth == 0:
                v = mk[start:pos[0]].strip()
                pos[0] += 1
                return v
            pos[0] += 1
        raise ValueError("property without ';': %s" % mk[start:start + 60])

    def elem():
        m = _OPEN.match(mk, pos[0])
        if not m:
            raise ValueError("no element at: %s" % mk[pos[0]:pos[0] + 60])
        node = {"type": m.group(1), "id": m.group(2), "props": {}, "kids": []}
        pos[0] = m.end()
        while True:
            ws()
            if pos[0] >= n:
                raise ValueError("unclosed element %s" % node["type"])
            if mk[pos[0]] == "}":
                pos[0] += 1
                return node
            if _OPEN.match(mk, pos[0]):
                node["kids"].append(elem())
                continue
            m2 = _PROP.match(mk, pos[0])
            if not m2:
                raise ValueError("unexpected markup at: %s" % mk[pos[0]:pos[0] + 60])
            pos[0] = m2.end()
            node["props"][m2.group(1)] = value()

    out = []
    while True:
        ws()
        if pos[0] >= n:
            return out
        out.append(elem())


def _pairs(v):
    """'(Width: 10, Top: -3)' -> {"Width": 10, "Top": -3}"""
    out = {}
    if not v:
        return out
    inner = v.strip()
    if inner.startswith("(") and inner.endswith(")"):
        inner = inner[1:-1]
    for part in inner.split(","):
        if ":" in part:
            k, x = part.split(":", 1)
            try:
                out[k.strip()] = int(x.strip())
            except ValueError:
                pass
    return out


def _box4(d, h_key="Horizontal", v_key="Vertical"):
    """Left / Right / Top / Bottom of an Anchor or Padding dict (Full / Horizontal / Vertical expanded; None where unset)."""
    f = d.get("Full")
    hz, vt = d.get(h_key, f), d.get(v_key, f)
    return (d.get("Left", hz), d.get("Right", hz), d.get("Top", vt), d.get("Bottom", vt))


def build_tree(appends):
    """One tree of every (parent, markup) append of a page: returns (root node, {id: node})."""
    ids, root = {}, None
    for parent, mk in appends:
        nodes = parse_markup(mk)
        for nd in nodes:
            stack = [nd]
            while stack:
                x = stack.pop()
                if x["id"]:
                    ids[x["id"]] = x
                stack.extend(x["kids"])
        if parent is None:
            root = nodes[0]
        else:
            ids[parent]["kids"].extend(nodes)
    return root, ids


def layout(root, issues):
    """Place every element (LayoutMode Top / Left / none, Anchor margins, Width / Height, Padding, Full). Records every child that
    leaves its parent's content box in issues (decorations with a negative anchor are skipped). Each node gets "box" (x, y, w, h)
    and "inner" (its content box); returns the node list in placement order."""
    order = []
    a0 = _pairs(root["props"].get("Anchor"))
    todo = [(root, 0, 0, a0.get("Width", 0), a0.get("Height", 0), "root")]
    while todo:
        nd, x, y, w, h, path = todo.pop(0)
        nd["box"] = (x, y, w, h)
        order.append(nd)
        pl, pr_, pt, pb = (v or 0 for v in _box4(_pairs(nd["props"].get("Padding"))))
        ix, iy, iw, ih = x + pl, y + pt, w - pl - pr_, h - pt - pb
        nd["inner"] = (ix, iy, iw, ih)
        mode = nd["props"].get("LayoutMode")
        cur = 0
        name = nd["id"] or nd["type"]
        for k in nd["kids"]:
            a = _pairs(k["props"].get("Anchor"))
            l, r, t, bt = _box4(a)
            kid = "%s>%s" % (path, k["id"] or k["type"])
            if any(v is not None and v < 0 for v in (l, r, t, bt)):
                continue                                     # a decoration placed outside on purpose
            if a.get("Full") is not None and mode is None:
                f = a["Full"]
                todo.append((k, ix + f, iy + f, iw - 2 * f, ih - 2 * f, kid))
                continue
            if mode == "Top":
                kw = a.get("Width", iw - (l or 0) - (r or 0))
                kh = a.get("Height")
                if kh is None:
                    kh = ih - cur - (t or 0) - (bt or 0)
                cur += t or 0
                ky, kx = iy + cur, ix + (l or 0)
                cur += kh + (bt or 0)
                if cur > ih:
                    issues.append("%s: children of #%s need %d px of %d (LayoutMode Top)" % (kid, name, cur, ih))
                if (l or 0) + kw + (r or 0) > iw:
                    issues.append("%s: %d px wide in #%s's %d" % (kid, (l or 0) + kw + (r or 0), name, iw))
            elif mode == "Left":
                kh = a.get("Height", ih - (t or 0) - (bt or 0))
                kw = a.get("Width")
                if kw is None:
                    kw = iw - cur - (l or 0) - (r or 0)
                cur += l or 0
                kx, ky = ix + cur, iy + (t or 0)
                cur += kw + (r or 0)
                if cur > iw:
                    issues.append("%s: children of #%s need %d px of %d (LayoutMode Left)" % (kid, name, cur, iw))
                if (t or 0) + kh + (bt or 0) > ih:
                    issues.append("%s: %d px high in #%s's %d" % (kid, (t or 0) + kh + (bt or 0), name, ih))
            else:
                kw, kh = a.get("Width"), a.get("Height")
                if kw is None:
                    kw, kx = iw - (l or 0) - (r or 0), ix + (l or 0)
                else:
                    kx = ix + (l if l is not None else (iw - r - kw if r is not None else (iw - kw) // 2))
                if kh is None:
                    kh, ky = ih - (t or 0) - (bt or 0), iy + (t or 0)
                else:
                    ky = iy + (t if t is not None else (ih - bt - kh if bt is not None else (ih - kh) // 2))
                if kx < ix or ky < iy or kx + kw > ix + iw or ky + kh > iy + ih:
                    issues.append("%s: box %s outside #%s's content box %s" % (kid, (kx, ky, kw, kh), name, (ix, iy, iw, ih)))
            todo.append((k, kx, ky, kw, kh, kid))
        nd["used"] = cur
    return order


def body_fill(ids, body_id):
    """px the LayoutMode Top children of the body take (margins included), and the body's content height."""
    nd = ids[body_id]
    tot = 0
    for k in nd["kids"]:
        a = _pairs(k["props"].get("Anchor"))
        _l, _r, t, bt = _box4(a)
        tot += (t or 0) + a.get("Height", 0) + (bt or 0)
    return tot, nd["inner"][3]


# ---------------------------------------------------------------------------- text (the client's own glyph advances)
_FONTS = {}


def font_table(bold, secondary=False):
    """{codepoint: advance (em)} + line height from the client's glyph JSON (read-only); None when the client folder is absent."""
    import skyyui as SUI
    name = "Lexend-Bold" if secondary else ("NunitoSans-ExtraBold" if bold else "NunitoSans-Medium")
    if name in _FONTS:
        return _FONTS[name]
    p = os.path.join(SUI.GAME_DIR, "Client", "Data", "Shared", "UI", "Fonts", name + ".json")
    if not os.path.isfile(p):
        _FONTS[name] = None
        return None
    d = json.load(open(p, encoding="utf8"))
    adv = dict((g["unicode"], g["advance"]) for g in d["glyphs"])
    _FONTS[name] = (adv, d["metrics"]["lineHeight"])
    return _FONTS[name]


def text_w(text, size, bold, upper, secondary=False):
    ft = font_table(bold, secondary)
    if ft is None:
        return None
    adv = ft[0]
    t = text.upper() if upper else text
    return sum(adv.get(ord(c), adv.get(ord("M"), 0.8)) for c in t) * size


def wrap_lines(text, width, size, bold, upper):
    """Greedy word wrap at spaces: the number of lines and the widest line (px)."""
    words = text.split(" ")
    lines, cur = [], ""
    for wd in words:
        cand = wd if not cur else cur + " " + wd
        if text_w(cand, size, bold, upper) <= width or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    return len(lines), max(text_w(x, size, bold, upper) for x in lines)


def _style(props):
    st_ = props.get("Style", "")
    fs = re.search(r"FontSize: (\d+)", st_)
    col = re.search(r"TextColor: (#[0-9A-Fa-f]{6,8}(?:\([0-9.]+\))?)", st_)
    return {"size": int(fs.group(1)) if fs else 16, "bold": "RenderBold: true" in st_, "upper": "RenderUppercase: true" in st_,
            "wrap": "Wrap: true" in st_, "secondary": 'FontName: "Secondary"' in st_, "color": col.group(1) if col else None}


def check_texts(name, order, sets, counts):
    """Every label's text fits: one line in its content width; wrapped text in its content height (lines x 1.364 em <= h + 0.1 em);
    a single line needs size + 4 px of height. Buttons: the label fits at the ShrinkTextToFit floor (12 px)."""
    if font_table(False) is None:
        counts["text_skipped"] = True
        return
    for nd in order:
        if nd["type"] == "Label":
            st_ = _style(nd["props"])
            txt = sets.get(nd["id"]) if nd["id"] and nd["id"] in sets else None
            if txt is None:
                m = re.match(r'"((?:[^"\\]|\\.)*)"', nd["props"].get("Text", '""'))
                txt = m.group(1) if m else ""
            if not txt:
                continue
            _x, _y, w, h = nd["inner"]
            lh = font_table(st_["bold"], st_["secondary"])[1]
            if st_["wrap"]:
                nl, widest = wrap_lines(txt, w, st_["size"], st_["bold"], st_["upper"])
                need = nl * lh * st_["size"]
                ok = need <= h + 0.1 * st_["size"] and widest <= w
                check(ok, "%s: #%s %d lines need %.1f px of %d (%r)" % (name, nd["id"], nl, need, h, txt))
                counts["wrapped"] += 1
                counts["max_lines_fill"] = max(counts["max_lines_fill"], need / float(h))
            else:
                tw = text_w(txt, st_["size"], st_["bold"], st_["upper"], st_["secondary"])
                check(tw <= w, "%s: #%s text %.0f px in %d px (%r)" % (name, nd["id"] or "label", tw, w, txt))
                check(st_["size"] + 4 <= h, "%s: #%s a %d px line in %d px" % (name, nd["id"], st_["size"], h))
                counts["lines"] += 1
                counts["max_line_fill"] = max(counts["max_line_fill"], tw / float(w))
                if tw / float(w) >= counts["widest"][0]:
                    counts["widest"] = (tw / float(w), "%s #%s %.0f/%d px" % (name, nd["id"], tw, w))
        elif nd["type"] == "TextButton":
            m = re.match(r'"((?:[^"\\]|\\.)*)"', nd["props"].get("Text", '""'))
            txt = m.group(1) if m else ""
            if not txt:
                continue
            _x, _y, w, _h = nd["inner"]
            at17 = text_w(txt, 17, True, True)
            at12 = text_w(txt, 12, True, True)
            check(at12 <= w, "%s: button #%s %r does not fit even at 12 px (%.0f of %d)" % (name, nd["id"], txt, at12, w))
            counts["buttons"] += 1
            if at17 > w:
                counts["shrunk"].add("%s (%.0f/%d)" % (txt, at17, w))


# ---------------------------------------------------------------------------- contrast (WCAG ratio on the effective background)
_PATCH_CENTRE = [None]


def patch_centre():
    """The centre pixel of Common/ContainerPatch.png from Assets.zip (read-only; a tiny PNG decoder: 8-bit RGB / RGBA, no interlace)."""
    if _PATCH_CENTRE[0] is not None:
        return _PATCH_CENTRE[0]
    import skyyui as SUI
    z = zipfile.ZipFile(SUI.ASSETS_ZIP)
    path = SUI._zip_path(SUI.TEX["patch"])
    data = z.read(path if path in z.namelist() else path[:-4] + "@2x.png")          # the client picks the @2x file when only it exists
    pos, idat, w = 8, b"", None
    while pos < len(data):
        ln, typ = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype, _c, _f, inter = struct.unpack(">IIBBBBB", body)
            assert depth == 8 and ctype in (2, 6) and inter == 0, (depth, ctype, inter)
            bpp = 4 if ctype == 6 else 3
        elif typ == b"IDAT":
            idat += body
        pos += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows, prev, i = [], bytearray(stride), 0
    for _y in range(h):
        f, line = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b_, c = prev[x], (prev[x - bpp] if x >= bpp else 0)
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b_) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b_) // 2) & 255
            elif f == 4:
                pp = a + b_ - c
                pa, pb, pc = abs(pp - a), abs(pp - b_), abs(pp - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else (b_ if pb <= pc else c))) & 255
        rows.append(line)
        prev = line
    px = rows[h // 2][(w // 2) * bpp:(w // 2) * bpp + 3]
    _PATCH_CENTRE[0] = (px[0], px[1], px[2])
    return _PATCH_CENTRE[0]


def _rgba(c):
    m = re.fullmatch(r"#([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})?(?:\(\s*([0-9.]+)\s*\))?", c.strip())
    hx = m.group(1)
    a = float(m.group(3)) if m.group(3) else (int(m.group(2), 16) / 255.0 if m.group(2) else 1.0)
    return int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16), a


def _over(top, base):
    r, g, b, a = top
    return tuple(a * c + (1 - a) * d for c, d in zip((r, g, b), base))


def _lum(rgb):
    def ch(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    a, b = _lum(fg), _lum(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


_BTN_BG = re.compile(r"Default:\s*\(Background:\s*(#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?:\(\s*[0-9.]+\s*\))?)\)")


def check_contrast(name, root, counts):
    """Every non-button label: its TextColor on the effective background (ContainerPatch centre under the body, then every colour
    Background above it, a Button's ButtonStyle Default background, and a full-size cover Group placed before it among its
    siblings - alpha-composited) is >= MIN_CONTRAST. The title bar (a texture) and text buttons are skipped."""
    import skyyui as SUI
    stack = [(root, None)]
    while stack:
        nd, bg = stack.pop()
        b = nd["props"].get("Background", "")
        if SUI.TEX["patch"] in b:
            bg = patch_centre()
        elif b.startswith("#") and bg is not None:
            bg = _over(_rgba(b), bg)
        elif b and not b.startswith("#"):
            bg = None                                   # another texture (the title bar): not measured
        if nd["type"] == "Button" and bg is not None:
            m = _BTN_BG.search(nd["props"].get("Style", ""))
            if m:
                bg = _over(_rgba(m.group(1)), bg)
        if nd["type"] == "Label" and bg is not None:
            col = _style(nd["props"])["color"]
            if col:
                r = contrast(_over(_rgba(col), bg), bg)
                check(r >= MIN_CONTRAST, "%s: #%s colour %s on %s = %.2f:1 (< %.1f)" % (
                    name, nd["id"] or "label", col, "#%02x%02x%02x" % tuple(int(round(v)) for v in bg), r, MIN_CONTRAST))
                counts["contrasts"] += 1
                if r < counts["min_contrast"][0]:
                    counts["min_contrast"] = (r, "%s #%s %s" % (name, nd["id"] or "label", col))
        if nd["type"] != "TextButton":
            kid_bg = bg
            for k in nd["kids"]:
                stack.append((k, kid_bg))
                a = _pairs(k["props"].get("Anchor"))
                kb = k["props"].get("Background", "")
                if a.get("Full") == 0 and kb.startswith("#") and kid_bg is not None and not k["kids"]:
                    kid_bg = _over(_rgba(kb), kid_bg)      # a full cover (the sold-out overlay): the siblings after it sit on it


# ---------------------------------------------------------------------------- per state
def ids_of(state):
    out = []
    for t, sel, data, text in state["commands"]:
        if t == "AppendInline" and text:
            out += _ID_RE.findall(text)
    return out


def sets_of(state):
    return dict((sel.lstrip("#")[:-len(".Text")], js(data)) for t, sel, data, text in state["commands"]
                if t == "Set" and sel and sel.endswith(".Text"))


def texts_of(state):
    """Every visible text of a state: inline Text values + b.set .Text values (non-empty)."""
    inl = [x for t, sel, data, text in state["commands"] if t == "AppendInline" and text for x in _TEXT_RE.findall(text) if x]
    return set(inl) | set(v for v in sets_of(state).values() if v)


def compare_state(name, old, new, SUI, counts, page_colors):
    """page_colors = the data colours the PAGE may carry (TCOLOR); the chat colours of UI_DATA_COLORS are not allowed here."""
    check(old["error"] is None and new["error"] is None, "%s: the page built in both jars (%s / %s)" % (name, old["error"], new["error"]))
    if old["error"] or new["error"]:
        return
    check(old["events"] == new["events"], "%s: event bindings identical (%d / %d)" % (name, len(old["events"]), len(new["events"])))
    counts["bindings"] += len(new["events"])
    oi, ni = ids_of(old), ids_of(new)
    miss = sorted(set(oi) - set(ni))
    check(not miss, "%s: no old id missing: %s" % (name, miss))
    counts["ids"] += len(set(oi))
    ot, nt = texts_of(old), texts_of(new)
    lost = sorted(ot - nt, key=str)
    check(not lost, "%s: old texts no longer shown: %s" % (name, lost))
    counts["texts"] += len(ot)
    ap = SUI.Appends()
    allowed = SUI.allowed_colors() | set(SUI.norm_color(c) for c in page_colors)
    size = 0
    for idx, (t, sel, data, text) in enumerate(new["commands"]):
        if t == "AppendInline":
            parent = None if sel is None else sel.lstrip("#")
            check(idx != 0 or parent is None, "%s: the first append is the page root" % name)
            try:
                SUI.check_markup(text, prefix=PREFIX, root=(parent is None))
            except ValueError as e:
                check(False, "%s: check_markup: %s" % (name, e))
            ap.append((parent, text))
            size += len(text)
            for c in _COL_RE.findall(text):
                check(SUI.norm_color(c) in allowed, "%s: colour %s is a kit / data colour" % (name, c))
                counts["colours"] += 1
            for bad in ("Width: 0,", "Width: 0)", "FlexWeight", "WrapMaxLines", "LetterSpacing", "LayoutMode: Right", "LayoutMode: Center",
                        "LayoutMode: Full", "ItemGrid"):
                check(bad not in text, "%s: no %s in %s" % (name, bad.strip(",)"), text[:80]))
        elif t == "Set":
            ident, prop = sel.lstrip("#").rsplit(".", 1)
            ap.sets.append((ident, prop, js(data)))
            size += len(data or "")
    counts["max_payload"] = max(counts["max_payload"], size)
    try:
        SUI.check_page(ap, PREFIX)
        counts["check_page"] += 1
    except ValueError as e:
        check(False, "%s: check_page: %s" % (name, e))
    try:
        SUI.assert_proven(ap, what=name)
        counts["proven"] += 1
    except SUI.UnprovenError as e:
        check(False, "%s: %s" % (name, e))
    counts["appends"] += len(ap)
    root, ids = build_tree(ap)
    a0 = _pairs(root["props"].get("Anchor"))
    check((a0.get("Width"), a0.get("Height")) == (PAGE_W, PAGE_H), "%s: page root %s x %s (want %d x %d)" % (
        name, a0.get("Width"), a0.get("Height"), PAGE_W, PAGE_H))
    for e in new["events"]:
        check(e[1] and e[1].lstrip("#") in ids, "%s: binding target %s exists" % (name, e[1]))
    grid = ids.get("SkyyTrGrid")
    check(grid is not None and SUI.norm_color(grid["props"].get("Background", "")) == SUI.norm_color(SUI.COLOR["well"])
          and _pairs(grid["props"].get("Padding")) == {"Full": SUI.WELL_LIST_PAD} and grid["props"].get("LayoutMode") == "Top",
          "%s: the node grid #SkyyTrGrid is the vanilla list well (%s)" % (name, None if grid is None else grid["props"]))
    if grid is not None:
        rows = [k["id"] for k in grid["kids"]]
        check(len(rows) == 6 and all(r and r.startswith("SkyyTrRow") for r in rows),
              "%s: the six tier rows sit on the grid well (%s)" % (name, rows))
        counts["grid_well"] += 1
    issues = []
    order = layout(root, issues)
    check(not issues, "%s: layout: %s" % (name, issues[:4]))
    counts["placed"] += len(order)
    tot, inner = body_fill(ids, BODY_ID)
    check(inner == BODY_INNER_H and tot == BODY_INNER_H, "%s: the body children fill %d px exactly (got %d of %d)" % (
        name, BODY_INNER_H, tot, inner))
    for nd in order:
        if nd["props"].get("LayoutMode") == "Left" and nd["kids"]:
            counts["min_row_slack"] = min(counts["min_row_slack"], nd["inner"][2] - nd["used"])
    check_texts(name, order, dict((i, v) for i, p, v in ap.sets if p == "Text"), counts)
    check_contrast(name, root, counts)
    counts["states"] += 1
    return ids


def new_counts():
    return dict(states=0, bindings=0, ids=0, texts=0, colours=0, check_page=0, proven=0, appends=0, placed=0, min_row_slack=10 ** 6,
                wrapped=0, lines=0, buttons=0, max_lines_fill=0.0, max_line_fill=0.0, widest=(0.0, ""), shrunk=set(), text_skipped=False,
                contrasts=0, min_contrast=(99.0, ""), max_payload=0, grid_well=0)


def report_counts(counts):
    print("B-C. %(states)d states: %(bindings)d bindings identical, %(ids)d old ids all kept, %(texts)d old texts all shown; "
          "%(check_page)d check_page + %(proven)d assert_proven / %(appends)d appends through check_markup, %(colours)d colours audited "
          "(kit + tree colours only), node grid on the list well in %(grid_well)d states, %(placed)d elements placed by the layout "
          "model (tightest Left row slack %(min_row_slack)d px), largest payload %(max_payload)d chars" % counts)
    if counts["text_skipped"]:
        print("   text widths: SKIPPED (no client glyph tables)")
    else:
        print("   text: %d single lines (widest %.0f%%: %s), %d wrapped labels (fullest %.0f%% of their height), %d buttons%s" % (
            counts["lines"], 100 * counts["widest"][0], counts["widest"][1], counts["wrapped"], 100 * counts["max_lines_fill"],
            counts["buttons"], (" (shrink-to-fit at 17 px: %s)" % ", ".join(sorted(counts["shrunk"]))) if counts["shrunk"] else ""))
    print("   contrast: %d labels, lowest %.2f:1 (%s), ContainerPatch centre #%02x%02x%02x" % (
        counts["contrasts"], counts["min_contrast"][0], counts["min_contrast"][1], *patch_centre()))


# ============================================================================================ parent
def cleanup(created, before):
    """Remove only what this run made: the whole scratch folder when the harness created it, otherwise just its own entries
    (OWN_ENTRIES) that were not there before the run - a --dir pointing at a real folder is never wiped."""
    if created:
        shutil.rmtree(SCRATCH, ignore_errors=True)
        return
    for e in OWN_ENTRIES:
        p = os.path.join(SCRATCH, e)
        if e in before or not os.path.exists(p):
            continue
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
        else:
            os.remove(p)


def main():
    if "--states" in sys.argv:
        run_states(arg("--states"), arg("--out"), arg("--tag"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    for j, ver in ((JAR, VERSION), (OLD_JAR, OLD_VERSION)):
        if not os.path.isfile(j):
            how = ("python tools/trees_0_2_5_patch.py, then python SkyyTrees/build_skyytrees_%s.py" % ver) if ver == VERSION else \
                ("python SkyyTrees/build_skyytrees_%s.py, without --deploy; or pass --old <a copy of the installed Mods/SkyyTrees.jar>, "
                 "the deployed %s" % (ver, ver))
            sys.exit("no %s jar at %s - build it first (%s)" % (ver, j, how))
    created = not os.path.exists(SCRATCH)
    before = set(os.listdir(SCRATCH)) if not created else set()
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    me = os.path.abspath(__file__)
    outs = {}
    for tag, j in (("new", JAR), ("old", OLD_JAR)):
        outs[tag] = os.path.join(SCRATCH, "states-%s.json" % tag)
        p = subprocess.run([sys.executable, me, "--states", j, "--out", outs[tag], "--tag", tag, "--dir", SCRATCH], env=env,
                           stderr=subprocess.PIPE, encoding="utf8", errors="replace")
        sys.stderr.write(p.stderr or "")
        check(p.returncode == 0 and os.path.isfile(outs[tag]), "state child JVM for %s ran" % j)
        check("mutated reflectively" not in (p.stderr or ""), "F: the %s state child mutated no final field without the JEP 500 "
              "option (--enable-final-field-mutation=ALL-UNNAMED)" % tag)
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "bytecode child ran")
    if not FAILS:
        run_parent(outs, bco)
    if not KEEP:
        cleanup(created, before)
    print("SkyyTrees %s vs %s: %d checks passed, %d failed" % (VERSION, OLD_VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyyTrees %s bare-JVM + render check:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(0 if not FAILS else 1)


def run_parent(outs, bco):
    new, old = json.load(open(outs["new"])), json.load(open(outs["old"]))
    # ---- A
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                            os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    if new["load_fails"] or old["load_fails"]:
        return
    import skyyui as SUI
    SUI.verify(quiet=True)
    src = open(SCRIPT, encoding="utf8").read()
    tcolor = eval(re.search(r"^TCOLOR = (\[.*?\])\n", src, re.M).group(1))
    data_colors = eval(re.search(r"^UI_DATA_COLORS = (.*?)\r?\n", src, re.M).group(1), {"TCOLOR": tcolor})
    check(data_colors[:len(tcolor)] == tcolor, "C: UI_DATA_COLORS starts with the tree colours")
    # UI_DATA_COLORS = the page part (the tree colours: the level line) + the chat part (Message.color literals). Only the page part
    # may appear in the page markup; every chat colour must be a real chat colour of the script and no kit colour (so the page audit,
    # kit colours + TCOLOR, can never let it through).
    page_colors, chat_colors = list(tcolor), data_colors[len(tcolor):]
    allowed_kit = SUI.allowed_colors()
    for c in chat_colors:
        used = re.findall(r'\.color\("%s"\)|TreeMsg\.say\([^\r\n]*, "%s"\);' % (re.escape(c), re.escape(c)), src)
        check(used and SUI.norm_color(c) not in allowed_kit and c not in page_colors,
              "C: chat colour %s is a Message colour of the script (%d uses), not a kit / page colour" % (c, len(used)))
    print("C. data colours: page %s (tree colours), chat %s (Message.color only; not allowed in the page markup)" % (
        " ".join(page_colors), " ".join(chat_colors)))
    # ---- B + C
    counts = new_counts()
    kinds = {"success": SUI.COLOR["success"], "error": SUI.COLOR["error"], "warning": SUI.COLOR["warning"], "info": SUI.COLOR["info"]}
    for spec in STATES:
        nm = spec["name"]
        check(nm in new["states"] and nm in old["states"], "B: state %s built by both jars" % nm)
        if nm not in new["states"] or nm not in old["states"]:
            continue
        ids = compare_state(nm, old["states"][nm], new["states"][nm], SUI, counts, page_colors)
        if ids is not None and "SkyyTrMsg" in ids:
            want = dict((m, k) for m, k in RESULT_TEXTS).get(spec["msg"])
            got = _style(ids["SkyyTrMsg"]["props"])["color"]
            if want is not None:
                check(SUI.norm_color(got) == SUI.norm_color(kinds[want]), "C: %s: the result line colour %s is the %s colour" % (nm, got, want))
    report_counts(counts)
    for m, k in RESULT_TEXTS:
        check(new["colors"].get(m) == kinds[k], "C: infoColor(%r) = %s (want %s %s)" % (m, new["colors"].get(m), k, kinds[k]))
    check(new["colors"].get("null") == kinds["info"], "C: infoColor(null) = the info colour")
    check(not old["colors"], "C: 0.2.4 has no infoColor (it is new in 0.2.5)")
    print("C. result colours: %d message kinds -> infoColor (done green, refused red, arm yellow, coming later / empty info blue)"
          % len(RESULT_TEXTS))
    # ---- D clicks
    nsteps = 0
    for name, _spec, clicks in CLICKS:
        a, b = old["clicks"].get(name), new["clicks"].get(name)
        check(a is not None and b is not None, "D: click sequence %s ran in both jars" % name)
        if a is None or b is None:
            continue
        for sa, sb in zip(a["steps"], b["steps"]):
            check(sa == sb, "D: %s: after %s the page / data / coins / dirty state is identical (%s / %s)" % (
                name, sa["click"], dict((k, v) for k, v in sa.items() if sa.get(k) != sb.get(k)),
                dict((k, v) for k, v in sb.items() if sa.get(k) != sb.get(k))))
            nsteps += 1
        check(len(a["steps"]) == len(b["steps"]) == len(clicks), "D: %s: every click ran" % name)
        check(a["after"]["events"] == b["after"]["events"], "D: %s: the page after the clicks has the same bindings" % name)
        compare_state("after " + name, a["after"], b["after"], SUI, new_counts(), page_colors)
    effects = sorted(set(s["msg"] for _n, _s, _c in CLICKS for s in new["clicks"][_n]["steps"] if s["msg"]))
    coins = [s["coins"] for s in new["clicks"]["mining buy toggle respec"]["steps"]]
    check(coins[-1] == [500], "D: the priced respec took 500 coins once (%s)" % coins[-1])
    lv0, lv1 = new["clicks"]["mining buy toggle respec"]["steps"][0]["lv"], new["clicks"]["mining buy toggle respec"]["steps"][2]["lv"]
    check(lv1 != lv0, "D: unlock / level up changed the node levels")
    print("D. clicks: %d sequences, %d clicks with identical effects in both jars (%d distinct result texts, e.g. %s)" % (
        len(CLICKS), nsteps, len(effects), "; ".join(effects[:4])))
    # ---- E class bytes + jar entries
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    check(sorted(zo.namelist()) == sorted(zn.namelist()), "E: same entries in both jars")
    diff = set(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    same = len(set(zo.namelist()) & set(zn.namelist())) - len(diff)
    assets = [n for n in zn.namelist() if n.endswith(".json") and n != "manifest.json"]
    check(len(assets) == ASSET_JSON and not [n for n in assets if n in diff],
          "E: every asset file byte-identical (%d JSON, want %d)" % (len(assets), ASSET_JSON))
    kitcls = set(n for n in diff if re.match(r"com/skyy/trees/Cfg[A-Za-z]*\.class$", n))
    check(diff - kitcls <= EXPECTED_DIFF, "E: only %s (+ Cfg* kit classes) differ, got %s" % (sorted(EXPECTED_DIFF), sorted(diff)))
    check(not [n for n in zn.namelist() if n.endswith(".ui")], "E: no .ui files in the jar (inline pages only)")
    plug = zn.read("com/skyy/trees/SkyyTreesPlugin.class")
    km = re.search(rb"ready \((skyyui [0-9.]+ [0-9a-f]{12})\) - /tree; ", plug)
    jar_kit = km.group(1).decode("ascii") if km else None
    check(jar_kit == SUI.kit_id(), "E: the ready line's kit id %s is the kit on disk %s (a jar built on another kit: rebuild it)"
          % (jar_kit, SUI.kit_id()))
    print("E. kit id in the ready line: %s (tools/skyyui.py: %s)" % (jar_kit, SUI.kit_id()))
    mo, mn = json.loads(zo.read("manifest.json")), json.loads(zn.read("manifest.json"))
    mdiff = sorted(k for k in set(mo) | set(mn) if vnorm(str(mo.get(k))) != vnorm(str(mn.get(k))))
    check(not mdiff and mn.get("Version") == VERSION and mn.get("Name") == mo.get("Name", "").replace(OLD_VERSION, VERSION),
          "E: manifest: only the version (Version, the display name's version prefix) differs: %s" % mdiff)
    bc = json.load(open(bco))
    B_SIG = ("build(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;"
             "Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;Lcom/hypixel/hytale/component/Store;)V")
    pg = bc.get("com/skyy/trees/TreePage.class", {})
    check(pg.get("changed") == sorted([B_SIG, "<clinit>()V"]), "E: TreePage: build() + the static init changed: %s" % pg.get("changed"))
    check(pg.get("new") == ["infoColor(Ljava/lang/String;)Ljava/lang/String;"], "E: TreePage: infoColor() is the one new method: %s" % pg.get("new"))
    check(pg.get("gone") == ["line(Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;Ljava/lang/String;Ljava/lang/String;"
                             "Ljava/lang/String;IZI)V"], "E: TreePage: line() is the one method gone: %s" % pg.get("gone"))
    check(pg.get("fields_gone") == sorted(["BG [Ljava/lang/String;", "HV [Ljava/lang/String;", "FG [Ljava/lang/String;",
                                           "SOON_BG Ljava/lang/String;", "SOON_HV Ljava/lang/String;", "SOON_FG Ljava/lang/String;"])
          and not pg.get("fields_new"), "E: TreePage: only the six old-look colour fields are gone: %s / %s" % (
              pg.get("fields_gone"), pg.get("fields_new")))
    sp = bc.get("com/skyy/trees/SkyyTreesPlugin.class", {})
    check(sp.get("changed") == ["setup()V"] and not sp.get("new") and not sp.get("gone") and sp.get("fields_same"),
          "E: SkyyTreesPlugin: only setup() (the ready line) changed: %s" % sp)
    for k in sorted(set(bc) - {"com/skyy/trees/TreePage.class", "com/skyy/trees/SkyyTreesPlugin.class"}):
        c = bc[k]
        check(not c.get("new") and not c.get("gone") and c.get("fields_same") and c.get("version_only"),
              "E: %s: only the version string differs: %s" % (k, c))
    print("E. jar entries: %d identical (%d asset JSON), differ: %s; methods: %s" % (
        same, len(assets), ", ".join(sorted(n.split("/")[-1] for n in diff)),
        "; ".join("%s %s" % (n.split("/")[-1][:-6], dict((x, bc[n][x]) for x in ("changed", "new", "gone", "fields_gone") if bc[n].get(x)))
                  for n in sorted(bc))))


if __name__ == "__main__":
    main()
