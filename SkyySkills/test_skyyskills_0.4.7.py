"""SkyySkills 0.4.7 - bare-JVM side-by-side harness for the look-only restyle of /skills (+ its Top 10 view), the Stats page and the
Overall page (vanilla UI pass; the first committed SkyySkills page harness). The approach of SkyyProfiles/test_skyyprofiles_0.1.3.py.

    python SkyySkills/test_skyyskills_0.4.7.py [--jar <SkyySkills-0.4.7.jar>] [--old <SkyySkills-0.4.6.jar>] [--dir <scratch>] [--keep]

Build first (python tools/skills_0_4_7_patch.py, then python SkyySkills/build_skyyskills_0.4.7.py). The old jar defaults to
SkyySkills/SkyySkills-0.4.6.jar (the jar the live set runs - same bytes as the deployed Mods/SkyySkills.jar when this was written).
Child processes start fresh JVMs (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + ONE mod jar on the classpath;
javassist only for the bytecode step; TEMP / TMP / java.io.tmpdir in the scratch folder) and check:
  A  every class of the 0.4.7 jar AND of the 0.4.6 jar loads and initializes under -Xverify:all
  B  the page states below built by the REAL SkillsPage / StatsPage / OverallPage build() of both jars (each page from its own
     constructor with an Unsafe-allocated PlayerRef; ref / store null - build() never reads them) with the engine's own
     UICommandBuilder / UIEventBuilder. The state is set through the jar's own public statics and the skyy.bridge map exactly as the
     other mods would: SkillStore.DATA (the XP array of the player's profile key), class:<uuid> / class:skill:<uuid> /
     class:fn:allowed (SkyyClasses), tree:fn:level / tree:names (SkyyTrees), skill:stats:Cooking (SkyyCooking), the SkillTop cache
     (the leaderboard rows), AcroCfg / OverallCfg switches. States: the overview with no class / a class / old Combat XP / SkyyTrees off,
     0.1-style and 0.2-style (all six trees, a partial list) / Acrobatics off / max levels; the Top 10 view with 3 rows (you first,
     punctuated names), 12 rows (you 11th), none, you not ranked; Stats for fresh / mid / max / legacy Combat / another class's skill
     (the note) / your class skill / Alchemy / Exploration / Cooking with SkyyCooking lines / Acrobatics with tree lines / Divinity /
     Smithing at 0; Overall fresh / with a class / max / switched off. Review fix states: Acrobatics with EVERY tree effect posted
     the way SkyyTrees 0.2.4 posts them (move:<uuid>["trees.acrobatics"] speed / jump / fallDamage + skill:bonus:<uuid>["trees"]
     dodge / double jump / XP, bridge.bonus.xpSkills incl. Acrobatics) - its "Skill tree:" line is 957 px at 18 px in a 910 px
     well - and Cooking with a 948 px SkyyCooking hook line: both shrink (ShrinkTextToFit) and must fit at the 15 px floor.
  C  per state: identical event bindings (type, selector, EventData, lock flag, order); no 0.4.6 element id missing; every 0.4.6
     visible text (inline or b.set) still shown by 0.4.7 - compared after 0.4.6's safe() character mapping (0.4.6 blanked , : ; " and
     turned { } into ( ) in inline text; 0.4.7 b.sets the text as it is) and whitespace collapsing (0.4.6 indented boost lines with 3
     spaces and spread a Top 10 line with runs of spaces; 0.4.7 shows the four parts of that line in four columns, joined here)
  D  per state, the 0.4.7 markup as the client gets it: SUI.check_markup on every append (the first = the page root) + SUI.check_page
     (parents exist, no duplicate id, every b.set target exists) + SUI.assert_proven (only properties deployed pages use: no
     FlexWeight, no LayoutMode Center / Right / Full, no WrapMaxLines, nothing UNVERIFIED); every binding targets an element that
     exists; only kit colours or the 16 skill colours (UI_PAGE_COLORS of the build script, checked = SkillDefs.COLORS of both jars;
     the chat-only UI_CHAT_COLORS are NOT allowed on a page - review 2); the page root size of that page; a layout model of the
     whole page (LayoutMode Top / Left / none, Anchor margins, Padding, Full): every child inside its parent's content box, the body
     children fill the body exactly; text: every label's text measured with the client's own Nunito Sans / Lexend glyph advances
     (read-only) - one line fits its width (a label with ShrinkTextToFit: at its MinShrinkTextToFitFontSize floor; the labels that
     really shrink are listed), wrapped text fits its height (1.364 em line height, slack 0.1 em), every button label fits
     at the 12 px ShrinkTextToFit floor; contrast: every non-button label's colour on its effective background (the ContainerPatch
     centre pixel decoded from Assets.zip read-only + the colour backgrounds above it) is >= 3.0:1
  F  class bytes 0.4.6 vs 0.4.7: only the three page classes, SkyySkillsPlugin (the ready line) and manifest.json differ (+ any class
     that only carries an embedded version string - CfgFn / CfgRows / SkillCfg: the config kit's version and the default
     xp.properties header "# SkyySkills 0.4.7 - XP rules" - checked instruction by instruction); method by method (constant-pool indices ignored): SkillsPage / StatsPage /
     OverallPage only build() changed (StatsPage lost its line / wrapLine helpers, OverallPage its line / wrapLine / gap / sep helpers
     and the HEAD / PANEL / TITLE / BTN style fields), every handleDataEvent and constructor is byte-identical (same clicks = same
     pages opened, same data read - nothing else is touched by these pages), SkyySkillsPlugin only setup() (the ready line)
Not testable without the game (UNVERIFIED in the build report): the kit base look on a client (probe pages base1-4), the real line
height / clipping of labels, colours as rendered. Nothing is deployed. Default scratch folder: tools/dev/scratch/skyyskills-047
(git-ignored), deleted at the end unless --keep; --dir must be a folder INSIDE tools/dev/scratch/ (never the scratch root itself
or a sibling such as tools/dev/scratch-x - the whole folder is deleted). Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, struct, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.4.7", "0.4.6"
PKG = "com.skyy.skills."
SCRIPT = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
MIN_CONTRAST = 3.0
PAGES = {  # page: (check_markup prefix, root w, root h, body id, body inner height)
    "skills": ("SkyySk", 960, 786, "SkyySkills", 786 - 38 - 34),
    "top": ("SkyySk", 960, 786, "SkyySkills", 786 - 38 - 34),
    "stats": ("SkyyS", 960, 848, "SkyySkStats", 848 - 38 - 34),
    "overall": ("SkyyOv", 960, 689, "SkyyOvBody", 689 - 38 - 34),
}
EXPECTED_DIFF = {"com/skyy/skills/SkillsPage.class", "com/skyy/skills/StatsPage.class", "com/skyy/skills/OverallPage.class",
                 "com/skyy/skills/SkyySkillsPlugin.class", "manifest.json"}


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyyskills-047")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyySkills-%s.jar" % OLD_VERSION)))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]
GUARD_OK = [False]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _jvm_start(jars, extra_cp=()):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR] + list(jars) + list(extra_cp), convertStrings=True)
    return B


# ============================================================================================ the page states (both jars, same input)
# slots: 0 Mining, 1 Foraging, 2 Farming, 3 Combat (legacy), 4 Acrobatics, 5 Archery, 6 Swordsmanship, 7 Assassination, 8 Shaman,
# 9 Sorcery, 10 Alchemy, 11 Smithing, 12 Cooking, 13 Exploration, 14 Fury, 15 Divinity. xp = {slot: (level, fraction of the next level)}
ALL6 = "Mining,Foraging,Farming,Cooking,Acrobatics,Exploration"
MID = {0: (12, 0.4), 1: (3, 0.9), 2: (0, 0.2), 4: (15, 0.5), 10: (7, 0.1), 11: (1, 0.5), 12: (22, 0.3), 13: (4, 0.4)}
HIGH = {0: (100, 0.0), 1: (64, 0.25), 2: (41, 0.7), 4: (88, 0.95), 10: (55, 0.5), 11: (30, 0.0), 12: (99, 0.99), 13: (77, 0.1)}
ME = "me"
# a SkyyCooking hook line (no length limit) 948 px wide at 18 px: longer than the 910 px well, it fits at the 15 px shrink floor (790)
LONG_HOOK = "Dishes you cook get +30% food buff strength and +45 s food buff length (x0.75 for campfire dishes, grades from 25)"
FULL_TREE_LINE = "Skill tree: +14.8% speed, +0.68 blocks jump, -14.5% fall damage, +22.5% dodge push, double jump 95%, +12.5% XP"


def _with(base, slot, lv):
    d = dict(base)
    d[slot] = lv
    return d


STATES = [
    # (name, page, env) - env keys: xp, cls, cskill, allowed, trees (None / "v1" / a tree:names text), view, top, slot, cook, acro_off,
    # overall_off, mana_off, move (the trees.acrobatics movement source), bonus (skill:bonus:<uuid>["trees"]), xp_on (a slot put in
    # bridge.bonus.xpSkills)
    ("skills fresh", "skills", {}),
    ("skills warrior trees v1", "skills", {"xp": _with(MID, 6, (30, 0.6)), "cls": "Warrior", "cskill": "Swordsmanship", "allowed": True,
                                           "trees": "v1"}),
    ("skills priest all trees high", "skills", {"xp": _with(HIGH, 15, (55, 0.5)), "cls": "Priest", "allowed": True, "trees": ALL6}),
    ("skills old combat xp", "skills", {"xp": {3: (9, 0.3), 0: (2, 0.0)}, "trees": "v1"}),
    ("skills acrobatics off mage", "skills", {"xp": _with(MID, 9, (5, 0.0)), "cls": "Mage", "allowed": True, "acro_off": True}),
    ("skills partial trees", "skills", {"xp": MID, "cls": "Berserker", "trees": "Mining,Acrobatics"}),
    ("top mining three", "top", {"xp": MID, "view": 0, "top": [(ME, (12, 0.4)), ("Alex, the 2nd", (9, 0.0)), ("Sam (profile 2)", (1, 0.5))]}),
    ("top twelve you eleventh", "top", {"xp": MID, "view": 12, "top": [("Player%d" % n, (60 - 3 * n, 0.1)) for n in range(10)]
                                         + [(ME, (22, 0.3)), ("Last", (1, 0.0))]}),
    ("top nobody", "top", {"view": 13, "top": []}),
    ("top not ranked", "top", {"xp": MID, "view": 6, "cls": "Warrior", "top": [("Zed \"Q\" {x}: y; z", (80, 0.5)), ("Bee", (2, 0.0))]}),
    ("top max xp", "top", {"xp": HIGH, "view": 0, "top": [(ME, (100, 0.0)), ("Rival", (100, 0.0))]}),
    ("stats mining fresh", "stats", {"slot": 0}),
    ("stats mining mid tree", "stats", {"xp": MID, "slot": 0, "cls": "Warrior", "trees": "v1"}),
    ("stats combat legacy", "stats", {"xp": {3: (6, 0.2)}, "slot": 3}),
    ("stats archery not current", "stats", {"xp": {5: (20, 0.5), 6: (3, 0.0)}, "slot": 5, "cls": "Warrior"}),
    ("stats class skill current", "stats", {"xp": {6: (30, 0.6)}, "slot": 3, "cls": "Warrior", "cskill": "Swordsmanship"}),
    ("stats mining max", "stats", {"xp": HIGH, "slot": 0, "trees": ALL6}),
    ("stats alchemy", "stats", {"xp": MID, "slot": 10}),
    ("stats exploration", "stats", {"xp": MID, "slot": 13, "trees": ALL6}),
    ("stats cooking hook", "stats", {"xp": MID, "slot": 12, "trees": "v1", "cook": ["+30% food buff strength", "+45 s food buff length",
                                                                                     "Cooking level 22 of 100", "Better grades from 25",
                                                                                     "Campfire dishes x0.75"]}),
    ("stats acrobatics trees", "stats", {"xp": MID, "slot": 4, "trees": ALL6}),
    # review fix: every Acrobatics tree effect (SkyyTrees 0.2.4 values with decimals; dodge under acro.treeDodgeMax 0.25, XP bonus
    # with Acrobatics in bridge.bonus.xpSkills) -> "Skill tree: +14.8% speed, +0.68 blocks jump, -14.5% fall damage, +22.5% dodge
    # push, double jump 95%, +12.5% XP" = 957 px at 18 px in the 910 px well: it must shrink and fit at the 15 px floor (798 px)
    ("stats acrobatics full tree line", "stats", {"xp": MID, "slot": 4, "trees": ALL6,
                                                  "move": {"speed": 0.148, "jump": 0.68, "fallDamage": -0.145},
                                                  "bonus": {"dodge.acrobatics": 0.225, "doublejump.acrobatics": 0.95, "xp.acrobatics": 0.125},
                                                  "xp_on": 4}),
    ("stats cooking long hook line", "stats", {"xp": MID, "slot": 12, "trees": "v1", "cook": [LONG_HOOK, "+45 s food buff length"]}),
    ("stats divinity priest", "stats", {"xp": {15: (12, 0.5)}, "slot": 15, "cls": "Priest", "allowed": True}),
    ("stats fury not current max", "stats", {"xp": {14: (100, 0.0)}, "slot": 14, "cls": "Mage"}),
    ("stats smithing zero", "stats", {"slot": 11}),
    ("overall fresh", "overall", {}),
    ("overall mage", "overall", {"xp": _with(MID, 9, (18, 0.0)), "cls": "Mage", "allowed": True}),
    ("overall max priest", "overall", {"xp": dict((s, (100, 0.0)) for s in (0, 1, 2, 4, 10, 11, 12, 13, 15)), "cls": "Priest",
                                       "allowed": True}),
    ("overall off", "overall", {"xp": MID, "overall_off": True, "mana_off": True}),
]


def run_states(jar, out):
    from jpype import JClass, JImplements, JOverride, JArray, JLong, JBoolean
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
    res = {"jar": jar, "classes": len(names), "loaded": loaded, "load_fails": load_fails, "states": {}}
    if load_fails:
        json.dump(res, open(out, "w"), indent=1)
        return
    Defs, Store, Top = JClass(PKG + "SkillDefs"), JClass(PKG + "SkillStore"), JClass(PKG + "SkillTop")
    res["colors"] = [str(c) for c in Defs.COLORS]       # the skill colours the pages show (= UI_PAGE_COLORS of the build script)
    SkillsPage, StatsPage, OverallPage = JClass(PKG + "SkillsPage"), JClass(PKG + "StatsPage"), JClass(PKG + "OverallPage")
    AcroCfg, OverallCfg, BridgeCfg = JClass(PKG + "AcroCfg"), JClass(PKG + "OverallCfg"), JClass(PKG + "BridgeCfg")
    JBool, HashMap, CHM = JArray(JBoolean), JClass("java.util.HashMap"), JClass("java.util.concurrent.ConcurrentHashMap")
    Float, Double = JClass("java.lang.Float"), JClass("java.lang.Double")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UUID, ArrayList, System = JClass("java.util.UUID"), JClass("java.util.ArrayList"), JClass("java.lang.System")
    Long, ObjArr = JClass("java.lang.Long"), JArray(JClass("java.lang.Object"))
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    @JImplements("java.util.function.Function")
    class Const(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            return self.v

    Defs.setTable(Defs.DEFAULT_PER)
    cum, per = list(Defs.CUM), list(Defs.PER)

    def xp_of(lv, frac):
        if lv >= len(per):
            return int(cum[len(per)]) + 12345
        return int(cum[lv]) + int(per[lv] * frac)

    bridge = Store.bridge()
    me = UUID(0x5117, 7)
    key = me.toString()
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    acro0, ov0, mana0 = bool(AcroCfg.ENABLED), bool(OverallCfg.ON), bool(OverallCfg.MANA_ON)
    bxp0 = BridgeCfg.BONUS_XP
    bkeys = ["class:" + key, "class:skill:" + key, "class:fn:allowed", "tree:fn:level", "tree:names", "skill:stats:Cooking",
             "profile:class:" + key, "profile:fn:key", "move:" + key, "skill:bonus:" + key]
    for (name, page, env) in STATES:
        for k in bkeys:
            bridge.remove(k)
        Store.DATA.clear()
        for i in range(len(Top.CACHE)):
            Top.CACHE[i] = None
            Top.AT[i] = 0
        AcroCfg.ENABLED = not env.get("acro_off", False)
        OverallCfg.ON = not env.get("overall_off", False)
        OverallCfg.MANA_ON = not env.get("mana_off", False)
        d = [0] * (2 * int(Defs.N))
        for sl, (lv, fr) in env.get("xp", {}).items():
            d[sl] = xp_of(lv, fr)
        Store.DATA.put(key, JArray(JLong)(d))
        if env.get("cls"):
            bridge.put("class:" + key, env["cls"])
        if env.get("cskill"):
            bridge.put("class:skill:" + key, env["cskill"])
        if env.get("allowed"):
            bridge.put("class:fn:allowed", Const(JClass("java.lang.Boolean").TRUE))
        if env.get("trees"):
            bridge.put("tree:fn:level", Const(JClass("java.lang.Integer")(0)))
            if env["trees"] != "v1":
                bridge.put("tree:names", env["trees"])
        if env.get("cook") is not None:
            lst = ArrayList()
            for t in env["cook"]:
                lst.add(t)
            bridge.put("skill:stats:Cooking", Const(lst))
        if env.get("move"):                 # SkyyTrees 0.2.4 TreeFx.acroPost: the flat movement source trees.acrobatics (tools/skyymove.py)
            e = HashMap()
            e.put("layer", "flat")
            for k2, v2 in env["move"].items():
                e.put(k2, Float(v2))
            src = CHM()
            src.put("trees.acrobatics", e)
            bridge.put("move:" + key, src)
        if env.get("bonus"):                # SkyyTrees skill:bonus:<uuid>: source "trees" -> {"dodge.acrobatics": 0.225, ...}
            e = HashMap()
            for k2, v2 in env["bonus"].items():
                e.put(k2, Double(v2))
            src = CHM()
            src.put("trees", e)
            bridge.put("skill:bonus:" + key, src)
        bx = [False] * int(Defs.N)
        if env.get("xp_on") is not None:    # bridge.bonus.xpSkills lists that skill (default: none)
            bx[env["xp_on"]] = True
        BridgeCfg.BONUS_XP = JBool(bx) if env.get("xp_on") is not None else bxp0
        if "top" in env:
            rows = ArrayList()
            for nm, (lv, fr) in env["top"]:
                if nm == ME:
                    rows.add(ObjArr(["Skyy", Long(xp_of(lv, fr)), key]))
                else:
                    rows.add(ObjArr([nm, Long(xp_of(lv, fr)), "k-" + nm]))
            Top.CACHE[env["view"]] = rows
            Top.AT[env["view"]] = System.currentTimeMillis()
        if page in ("skills", "top"):
            pg = SkillsPage(pr)
            if page == "top":
                pg.view = env["view"]
        elif page == "stats":
            pg = StatsPage(pr, env["slot"])
        else:
            pg = OverallPage(pr)
        b, ev = UCB(), UEB()
        try:
            pg.build(None, b, ev, None)
            err = None
        except Exception as e:
            err = str(e)
        cmds = [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]
        evs = [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data),
                bool(e.locksInterface)] for e in ev.getEvents()]
        res["states"][name] = {"error": err, "commands": cmds, "events": evs, "page": page}
    AcroCfg.ENABLED, OverallCfg.ON, OverallCfg.MANA_ON = acro0, ov0, mana0
    BridgeCfg.BONUS_XP = bxp0
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: bytecode method compare (javassist)
def version_only(a, b):
    """Two method listings differ only by embedded version strings: every differing instruction is the same line with the FIRST
    "0.4.6" turned into "0.4.7" (a "SkyySkills 0.4.6 - XP rules" file header, an ldc "0.4.6"; later history mentions of 0.4.6 in the
    same constant must stay equal)."""
    la, lb = a.split(chr(10)), b.split(chr(10))
    return len(la) == len(lb) and all(x == y or x.replace(OLD_VERSION, VERSION, 1) == y for x, y in zip(la, lb))


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
                  "version_only": all(version_only(mo[k], mn[k]) for k in changed)
                  and all((x or "").replace(OLD_VERSION, VERSION, 1) == (y or "") for x, y in consts.values())}
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent: markup model (the SkyyProfiles 0.1.3
# harness model: parse, place, measure)
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
                continue
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


# ---------------------------------------------------------------------------- text (the client's own glyph advances, read-only)
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
    st = props.get("Style", "")
    fs = re.search(r"FontSize: (\d+)", st)
    col = re.search(r"TextColor: (#[0-9A-Fa-f]{6,8}(?:\([0-9.]+\))?)", st)
    mn = re.search(r"MinShrinkTextToFitFontSize: (\d+)", st)
    return {"size": int(fs.group(1)) if fs else 16, "bold": "RenderBold: true" in st, "upper": "RenderUppercase: true" in st,
            "wrap": "Wrap: true" in st, "secondary": 'FontName: "Secondary"' in st, "color": col.group(1) if col else None,
            "shrink": int(mn.group(1)) if mn and "ShrinkTextToFit: true" in st else None}


def check_texts(name, order, sets, counts):
    """Every label's text fits: one line in its content width; wrapped text in its content height (lines x 1.364 em <= h + 0.1 em);
    a single line needs size + 4 px of height. Buttons: the label fits at the ShrinkTextToFit floor (12 px)."""
    if font_table(False) is None:
        counts["text_skipped"] = True
        return
    for nd in order:
        if nd["type"] == "Label":
            st = _style(nd["props"])
            txt = sets.get(nd["id"]) if nd["id"] and nd["id"] in sets else None
            if txt is None:
                m = re.match(r'"((?:[^"\\]|\\.)*)"', nd["props"].get("Text", '""'))
                txt = m.group(1) if m else ""
            if not txt:
                continue
            _x, _y, w, h = nd["inner"]
            lh = font_table(st["bold"], st["secondary"])[1]
            if st["wrap"]:
                nl, widest = wrap_lines(txt, w, st["size"], st["bold"], st["upper"])
                need = nl * lh * st["size"]
                ok = need <= h + 0.1 * st["size"] and widest <= w
                check(ok, "%s: #%s %d lines need %.1f px of %d (%r)" % (name, nd["id"], nl, need, h, txt))
                counts["wrapped"] += 1
                counts["max_lines_fill"] = max(counts["max_lines_fill"], need / float(h))
            else:
                tw = text_w(txt, st["size"], st["bold"], st["upper"], st["secondary"])
                check(st["size"] + 4 <= h, "%s: #%s a %d px line in %d px" % (name, nd["id"], st["size"], h))
                counts["lines"] += 1
                if st["shrink"]:            # ShrinkTextToFit: the client shrinks the line down to its floor - it must fit there
                    counts["shrink_labels"] += 1
                    tmin = text_w(txt, st["shrink"], st["bold"], st["upper"], st["secondary"])
                    check(tmin <= w, "%s: #%s text %.0f px even at its %d px shrink floor in %d px (%r)" % (
                        name, nd["id"] or "label", tmin, st["shrink"], w, txt))
                    if tw > w:
                        counts["label_shrunk"].add("%s #%s %.0f px at %d -> %.0f px at %d of %d" % (
                            name, nd["id"], tw, st["size"], tmin, st["shrink"], w))
                        counts["shrunk_states"].add(name)
                        counts["max_shrink_fill"] = max(counts["max_shrink_fill"], tmin / float(w))
                        continue
                else:
                    check(tw <= w, "%s: #%s text %.0f px in %d px (%r)" % (name, nd["id"] or "label", tw, w, txt))
                counts["max_line_fill"] = max(counts["max_line_fill"], tw / float(w))
                if tw / float(w) >= counts["widest"][0]:
                    counts["widest"] = (tw / float(w), "%s #%s %.0f/%d px" % (name, nd["id"], tw, w))
        elif nd["type"] == "TextButton":
            m = re.match(r'"((?:[^"\\]|\\.)*)"', nd["props"].get("Text", '""'))
            txt = m.group(1) if m else ""
            if not txt:
                continue
            _x, _y, w, _h = nd["inner"]
            size = int(re.search(r"FontSize: (\d+)", nd["props"].get("Style", "FontSize: 17")).group(1))
            at = text_w(txt, size, True, True)
            at12 = text_w(txt, 12, True, True)
            check(at12 <= w, "%s: button #%s %r does not fit even at 12 px (%.0f of %d)" % (name, nd["id"], txt, at12, w))
            counts["buttons"] += 1
            if at > w:
                counts["shrunk"].add("%s (%.0f/%d)" % (txt, at, w))


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


def check_contrast(name, root, counts):
    """Every non-button label: its TextColor on the effective background (ContainerPatch centre under the body, then every colour
    Background above it, alpha-composited) is >= MIN_CONTRAST. The title bar (a texture) and buttons are skipped."""
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
            bg = None
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
            stack.extend((k, bg) for k in nd["kids"])


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


def norm(t):
    """0.4.6's safe() mapping (, : ; " -> space, { } -> ( )) and whitespace collapsed: how 0.4.6 showed a text vs how 0.4.7 does."""
    t = t.replace(":", " ").replace(";", " ").replace(",", " ").replace('"', " ").replace("{", "(").replace("}", ")")
    return " ".join(t.split())


def texts_of(state, top_rows=False):
    """Every visible text of a state (normalized): inline Text values + b.set .Text values (non-empty); top_rows=True also adds the
    0.4.7 Top 10 table rows as one line each (the cells C0..C3 of #SkyySkTopRow<i> joined - 0.4.6 showed them as one label)."""
    inl = [x for t, sel, data, text in state["commands"] if t == "AppendInline" and text for x in _TEXT_RE.findall(text) if x]
    sets = sets_of(state)
    out = set(norm(x) for x in inl) | set(norm(v) for v in sets.values() if v)
    if top_rows:
        for i in range(10):
            cells = [sets.get("SkyySkTopRow%dC%d" % (i, c)) for c in range(4)]
            if all(cells):
                out.add(norm(" ".join(cells)))
    out.discard("")
    return out


def compare_state(name, old, new, SUI, counts, data_colors):
    check(old["error"] is None and new["error"] is None, "%s: the page built in both jars (%s / %s)" % (name, old["error"], new["error"]))
    if old["error"] or new["error"]:
        return
    prefix, page_w, page_h, body_id, body_h = PAGES[new["page"]]
    # C1 bindings
    check(old["events"] == new["events"], "%s: event bindings identical (%d / %d)" % (name, len(old["events"]), len(new["events"])))
    counts["bindings"] += len(new["events"])
    # C2 ids
    oi, ni = ids_of(old), ids_of(new)
    miss = sorted(set(oi) - set(ni))
    check(not miss, "%s: no old id missing: %s" % (name, miss))
    counts["ids"] += len(set(oi))
    # C3 texts
    ot, nt = texts_of(old), texts_of(new, top_rows=(new["page"] == "top"))
    lost = sorted(ot - nt, key=str)
    check(not lost, "%s: old texts no longer shown: %s" % (name, lost))
    counts["texts"] += len(ot)
    # D markup as the client gets it
    ap = SUI.Appends()
    allowed = SUI.allowed_colors() | set(SUI.norm_color(c) for c in data_colors)
    size = 0
    for idx, (t, sel, data, text) in enumerate(new["commands"]):
        if t == "AppendInline":
            parent = None if sel is None else sel.lstrip("#")
            check(idx != 0 or parent is None, "%s: the first append is the page root" % name)
            try:
                SUI.check_markup(text, prefix=prefix, root=(parent is None))
            except ValueError as e:
                check(False, "%s: check_markup: %s" % (name, e))
            ap.append((parent, text))
            size += len(text)
            for c in _COL_RE.findall(text):
                check(SUI.norm_color(c) in allowed, "%s: colour %s is a kit / data colour" % (name, c))
                counts["colours"] += 1
        elif t == "Set":
            ident, prop = sel.lstrip("#").rsplit(".", 1)
            ap.sets.append((ident, prop, js(data)))
            size += len(data or "")
        else:
            check(False, "%s: unexpected command %s" % (name, t))
    counts["max_payload"] = max(counts["max_payload"], size)
    try:
        SUI.check_page(ap, prefix)
        counts["check_page"] += 1
    except ValueError as e:
        check(False, "%s: check_page: %s" % (name, e))
    try:
        SUI.assert_proven(ap, what=name)
        counts["proven"] += 1
    except ValueError as e:
        check(False, "%s: assert_proven: %s" % (name, e))
    counts["appends"] += len(ap)
    root, ids = build_tree(ap)
    a0 = _pairs(root["props"].get("Anchor"))
    check((a0.get("Width"), a0.get("Height")) == (page_w, page_h), "%s: page root %s x %s (want %d x %d)" % (
        name, a0.get("Width"), a0.get("Height"), page_w, page_h))
    for e in new["events"]:
        check(e[1] and e[1].lstrip("#") in ids, "%s: binding target %s exists" % (name, e[1]))
    issues = []
    order = layout(root, issues)
    check(not issues, "%s: layout: %s" % (name, issues[:4]))
    counts["placed"] += len(order)
    tot, inner = body_fill(ids, body_id)
    check(inner == body_h and tot == body_h, "%s: the body children fill %d px exactly (got %d of %d)" % (name, body_h, tot, inner))
    for nd in order:                                  # the Left rows: record the tightest one
        if nd["props"].get("LayoutMode") == "Left" and nd["kids"]:
            counts["min_row_slack"] = min(counts["min_row_slack"], nd["inner"][2] - nd["used"])
    check_texts(name, order, dict((i, v) for i, p, v in ap.sets if p == "Text"), counts)
    check_contrast(name, root, counts)
    counts["states"] += 1


def new_counts():
    return dict(states=0, bindings=0, ids=0, texts=0, colours=0, check_page=0, proven=0, appends=0, placed=0, min_row_slack=10 ** 6,
                wrapped=0, lines=0, buttons=0, max_lines_fill=0.0, max_line_fill=0.0, widest=(0.0, ""), shrunk=set(), text_skipped=False,
                contrasts=0, min_contrast=(99.0, ""), max_payload=0, shrink_labels=0, label_shrunk=set(), shrunk_states=set(),
                max_shrink_fill=0.0)


def report_counts(counts):
    print("B-D. %(states)d states: %(bindings)d bindings identical, %(ids)d old ids all kept, %(texts)d old texts all shown; "
          "%(check_page)d check_page + %(proven)d assert_proven / %(appends)d appends through check_markup, %(colours)d colours audited, "
          "%(placed)d elements placed by the layout model (tightest Left row slack %(min_row_slack)d px), largest payload %(max_payload)d "
          "chars" % counts)
    if counts["text_skipped"]:
        print("   text widths: SKIPPED (no client glyph tables)")
    else:
        print("   text: %d single lines (widest %.0f%%: %s), %d wrapped labels (fullest %.0f%% of their height), %d buttons%s" % (
            counts["lines"], 100 * counts["widest"][0], counts["widest"][1], counts["wrapped"], 100 * counts["max_lines_fill"],
            counts["buttons"], (" (shrink-to-fit: %s)" % ", ".join(sorted(counts["shrunk"]))) if counts["shrunk"] else ""))
        print("   shrink-to-fit lines: %d labels carry ShrinkTextToFit, %d of them shrink (fullest %.0f%% at the floor): %s" % (
            counts["shrink_labels"], len(counts["label_shrunk"]), 100 * counts["max_shrink_fill"],
            "; ".join(sorted(counts["label_shrunk"])) or "none"))
    print("   contrast: %d labels, lowest %.2f:1 (%s), ContainerPatch centre #%02x%02x%02x" % (
        counts["contrasts"], counts["min_contrast"][0], counts["min_contrast"][1], *patch_centre()))


def data_colors_of_script():
    """(page, chat, data) colour lists of the build script: UI_PAGE_COLORS (the 16 skill colours - the ONLY data colours a page may
    show), UI_CHAT_COLORS (chat lines only) and UI_DATA_COLORS (= page + chat, what tools/ci/lint.py reads), evaluated the way lint
    does (their earlier module constants resolved). The page audit allows kit colours + the PAGE list only (review 2: the old union
    with the chat colours would have let a chat colour in page markup pass)."""
    import ast
    src = open(SCRIPT, encoding="utf8").read()
    env = {}
    for stmt in ast.parse(src).body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            nm = stmt.targets[0].id
            if nm in ("_B5C", "CLASS_ROWS", "EXTRA_ROWS", "UI_PAGE_COLORS", "UI_CHAT_COLORS", "UI_DATA_COLORS"):
                env[nm] = eval(compile(ast.Expression(stmt.value), SCRIPT, "eval"), {}, dict(env))

    def hexes(v, out):
        if isinstance(v, str):
            if re.fullmatch(r"#[0-9A-Fa-f]{6}", v):
                out.append(v.lower())
        elif isinstance(v, (list, tuple)):
            for x in v:
                hexes(x, out)
        return out
    return tuple(hexes(env.get(nm, []), []) for nm in ("UI_PAGE_COLORS", "UI_CHAT_COLORS", "UI_DATA_COLORS"))


# ============================================================================================ main
def main():
    if "--run" in sys.argv:
        run_states(arg("--run"), arg("--out"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    for j in (JAR, OLD_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    scratch_root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    if here == scratch_root or not here.startswith(scratch_root + "/"):     # a strict sub-folder: never the root, never scratch-x
        sys.exit("--dir must be a folder INSIDE tools/dev/scratch/ (the whole folder is deleted afterwards), not %s" % SCRATCH)
    GUARD_OK[0] = True
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    me = os.path.abspath(__file__)
    outs = {}
    for tag, j in (("new", JAR), ("old", OLD_JAR)):
        outs[tag] = os.path.join(SCRATCH, "states-%s.json" % tag)
        p = subprocess.run([sys.executable, me, "--run", j, "--out", outs[tag], "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(outs[tag]), "child JVM for %s ran" % j)
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
    if FAILS:
        return finish()
    # B-D
    import skyyui as SUI
    SUI.verify(quiet=True)
    data_colors, chat_colors, lint_colors = data_colors_of_script()
    jar_colors = sorted(c.lower() for c in new.get("colors", []))
    check(len(data_colors) == 16 and sorted(data_colors) == jar_colors and jar_colors == sorted(c.lower() for c in old.get("colors", [])),
          "D: UI_PAGE_COLORS = the 16 SkillDefs.COLORS of both jars (%d: %s / jar %s)" % (len(data_colors), data_colors, jar_colors))
    check(chat_colors and not set(chat_colors) & set(data_colors) and lint_colors == data_colors + chat_colors,
          "D: UI_CHAT_COLORS (%d) are chat-only (none is a skill colour) and UI_DATA_COLORS = UI_PAGE_COLORS + UI_CHAT_COLORS (lint)"
          % len(chat_colors))
    counts = new_counts()
    per_page = {}
    for nm, page, _env in STATES:
        check(nm in new["states"] and nm in old["states"], "B: state %s built by both jars" % nm)
        if nm in new["states"] and nm in old["states"]:
            compare_state(nm, old["states"][nm], new["states"][nm], SUI, counts, data_colors)
            per_page[page] = per_page.get(page, 0) + 1
    report_counts(counts)
    print("   states per view: %s" % ", ".join("%s %d" % kv for kv in sorted(per_page.items())))
    # a few state-specific facts (the rules the pages show must still be there in 0.4.7)
    st = new["states"]
    sk = sets_of(st["skills warrior trees v1"])
    check(sk.get("SkyySkRow8Nm", "").startswith("Swordsmanship"), "B: the class row shows the class skill name (%r)" % sk.get("SkyySkRow8Nm"))
    ev_a = lambda nm: [json.loads(e[2]).get("a") for e in st[nm]["events"] if e[2]]
    check(sorted(a for a in ev_a("skills warrior trees v1") if a.startswith("sktree")) == ["sktree0", "sktree1", "sktree12", "sktree2"],
          "B: SkyyTrees 0.1 (no tree:names): TREE only for Mining / Foraging / Farming / Cooking: %s" % ev_a("skills warrior trees v1"))
    check(sorted(a for a in ev_a("skills partial trees") if a.startswith("sktree")) == ["sktree0", "sktree4"],
          "B: tree:names Mining,Acrobatics -> TREE for those two only")
    check(sum(1 for e in st["skills priest all trees high"]["events"] if "sktree" in (e[2] or "")) == 6, "B: all six trees -> six TREE buttons")
    check(not any("sktree" in (e[2] or "") for e in st["skills fresh"]["events"]), "B: SkyyTrees off -> no TREE button")
    check(sets_of(st["skills old combat xp"]).get("SkyySkRow8Pg", "").startswith("Old Combat XP (level 9)"), "B: the old Combat XP line")
    check(sets_of(st["top nobody"]).get("SkyySkTopNone") == "Nobody has any XP yet.", "B: the empty Top 10 line")
    check(sets_of(st["top twelve you eleventh"]).get("SkyySkRank", "").startswith("Your rank #11 of 12"), "B: rank 11 of 12")
    check(sets_of(st["top not ranked"]).get("SkyySkRank") == "You are not ranked yet", "B: not ranked")
    check(sets_of(st["top not ranked"]).get("SkyySkTopRow0C1") == 'Zed "Q" {x}: y; z', "B: a punctuated name is shown as it is (b.set)")
    check("SkyyStNote" in sets_of(st["stats archery not current"]) and "SkyyStNote" not in sets_of(st["stats mining mid tree"]),
          "B: the 'not a <class> right now' note only for another class's skill")
    check(sets_of(st["stats mining max"]).get("SkyyStNextHd") is None and
          any("Max level reached" in (x[3] or "") for x in st["stats mining max"]["commands"]), "B: max level head")
    check(sum(1 for k in sets_of(st["stats cooking hook"]) if k.startswith("SkyyStNow")) >= 5, "B: SkyyCooking's lines on the Stats page")
    check("sttree" in ev_a("stats mining mid tree") and "sttree" not in ev_a("stats mining fresh")
          and "sttree" not in ev_a("stats alchemy"), "B: SKILL TREE only when that skill has a tree")
    check(any("Max Overall Level reached" in (x[3] or "") for x in st["overall max priest"]["commands"]), "B: max Overall head")
    # F
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    check(sorted(zo.namelist()) == sorted(zn.namelist()), "F: same entries in both jars")
    diff = set(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    same = len(set(zo.namelist()) & set(zn.namelist())) - len(diff)
    bc = json.load(open(bco))
    extra = sorted(diff - EXPECTED_DIFF)
    for n in extra:
        c = bc.get(n)
        check(c is not None and not c["new"] and not c["gone"] and c["fields_same"] and c["version_only"],
              "F: %s differs by more than the version string: %s" % (n, c))
    check(not [n for n in zn.namelist() if n.endswith(".ui")], "F: no .ui files in the jar (inline pages only)")
    mo, mn = json.loads(zo.read("manifest.json")), json.loads(zn.read("manifest.json"))
    check(set(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k)) <= {"Version", "Name", "Description"} and mn.get("Version") == VERSION
          and mo.get("Description") == mn.get("Description"),
          "F: manifest: only the version differs: %s" % sorted(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k)))
    B = "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;" \
        "Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;Lcom/hypixel/hytale/component/Store;)V"
    U = "Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;"
    sp = bc.get("com/skyy/skills/SkillsPage.class", {})
    check(sp.get("changed") == ["build" + B] and not sp.get("new") and not sp.get("gone") and sp.get("fields_same"),
          "F: SkillsPage: only build() changed: %s" % sp)
    tp = bc.get("com/skyy/skills/StatsPage.class", {})
    check(tp.get("changed") == ["build" + B] and not tp.get("new") and tp.get("fields_same")
          and tp.get("gone") == ["line(%sLjava/lang/String;Ljava/lang/String;Ljava/lang/String;IZI)V" % U,
                                 "wrapLine(%sLjava/lang/String;Ljava/lang/String;Ljava/lang/String;II)V" % U],
          "F: StatsPage: only build() changed, line / wrapLine gone: %s" % tp)
    op = bc.get("com/skyy/skills/OverallPage.class", {})
    check(op.get("changed") == ["build" + B] and not op.get("new") and not op.get("fields_new")
          and op.get("gone") == ["gap(%sI)V" % U, "line(%sLjava/lang/String;Ljava/lang/String;Ljava/lang/String;IZZZI)V" % U,
                                 "sep(%s)V" % U, "wrapLine(%sLjava/lang/String;Ljava/lang/String;Ljava/lang/String;II)V" % U]
          and op.get("fields_gone") == ["BTN Ljava/lang/String;", "HEAD Ljava/lang/String;", "PANEL Ljava/lang/String;", "TITLE Ljava/lang/String;"],
          "F: OverallPage: only build() changed, its style fields and line / wrapLine / gap / sep helpers gone: %s" % op)
    for k, c in (("SkillsPage", sp), ("StatsPage", tp), ("OverallPage", op)):
        check(not any(m.startswith("handleDataEvent") or m.startswith("<init>") for m in c.get("changed", []) + c.get("gone", [])),
              "F: %s: handleDataEvent and the constructor are byte-identical (the same clicks open the same pages)" % k)
    pl = bc.get("com/skyy/skills/SkyySkillsPlugin.class", {})
    check(pl.get("changed") == ["setup()V"] and not pl.get("new") and not pl.get("gone") and pl.get("fields_same"),
          "F: SkyySkillsPlugin: only setup() (the ready line) changed: %s" % pl)
    print("F. class bytes: %d entries identical, differ: %s; methods: %s" % (
        same, ", ".join(sorted(n.split("/")[-1] for n in diff)),
        "; ".join("%s %s" % (n.split("/")[-1][:-6], dict((x, bc[n][x]) for x in ("changed", "new", "gone", "fields_gone", "consts")
                                                         if bc[n][x]))
                  for n in sorted(bc))))
    return finish()


def finish():
    if not KEEP and GUARD_OK[0]:        # only a --dir that passed the strict sub-folder guard in main() is ever deleted
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyySkills %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
