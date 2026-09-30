"""SkyyProfiles 0.1.3 - bare-JVM page-state harness for the look-only restyle (vanilla UI pass; review fixes 2026-09-29, second pass).
The first SkyyProfiles harness in the repo (review finding 2: the pages had no committed regression test).

    python SkyyProfiles/test_skyyprofiles_0.1.3.py [--jar <SkyyProfiles-0.1.3.jar>] [--old <SkyyProfiles-0.1.2.jar>] [--dir <scratch>] [--keep]

Build the jar first (python tools/profiles_0_1_3_patch.py, then python SkyyProfiles/build_skyyprofiles_0.1.3.py). Child processes start
fresh JVMs (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + ONE mod jar on the classpath; javassist only for the
bytecode step) and check:
  A  every class of the 0.1.3 jar AND of the 0.1.2 jar loads and initializes under -Xverify:all
  B  22 page states built by the REAL ProfilePage.buildList / buildCreate of both jars with the engine's own UICommandBuilder /
     UIEventBuilder (the page from its own constructor with an Unsafe-allocated PlayerRef; the player's profile Properties built here;
     bridge class:list / class:fn:kitnew; ProfCfg.MAX_PROFILES): list view with 1 / 2 / 3 / 6 / 7-over-max profiles, a pending switch,
     no class, an extra class, long names, info lines; Create Profile first / new, with / without kits, picks, class:list with 2 /
     8 / 9 classes, a picked coming-later class
  C  per state: identical event bindings (type, selector, EventData, lock flag, order); no 0.1.2 element id missing; every 0.1.2
     visible text (inline or b.set) is still shown by 0.1.3 (inline or b.set)
  D  per state, the 0.1.3 markup as the client gets it: SUI.check_markup on every append (the first = the page root) + SUI.check_page
     (parents exist, no duplicate id, every b.set target exists); every binding targets an element that exists; only kit colours or
     the declared data colours (UI_DATA_COLORS); no Width 0 / FlexWeight / WrapMaxLines / LetterSpacing / LayoutMode Right, Center,
     Full / ItemGrid; the page root 1100 x 980 (one size for both views, spec 4.2); a layout model of the whole page (LayoutMode Top /
     Left / none, Anchor margins, Padding, Full): every child inside its parent's content box, the body children fill 908 px
     exactly; text: every label's text measured with the client's own Nunito Sans glyph advances (read-only) - one line fits its
     width, wrapped text fits its height at the font's 1.364 line height (slack 0.1 em); contrast: every non-button label's colour on
     its effective background (the ContainerPatch centre pixel, decoded from Assets.zip read-only, + the colour backgrounds above it)
     is >= 3.0:1
  E  the SKYY CARD block: byte-identical in SkyyClasses/build_skyyclasses_0.1.8.py and here, = CARD_SHA of both patches; exec'd alone
     with the kit, every look (selected / pending / normal / off / empty) and both cell kinds render and pass check_markup
  F  class bytes 0.1.2 vs 0.1.3: only ProfilePage, SkyyProfilesPlugin (ready line), CfgFn / CfgRows (version string) and manifest.json
     differ; method by method (constant-pool indices ignored) only ProfilePage.buildList / buildCreate and SkyyProfilesPlugin.setup,
     and CfgFn / CfgRows by the version string only
Not testable without the game (UNVERIFIED in the build report): the kit base look on a client (probe pages base1-3), the real line
height / clipping of labels, colours as rendered. Nothing is deployed. Default scratch folder: tools/dev/scratch/skyyprofiles-013
(git-ignored), deleted at the end unless --keep; TEMP/TMP and java.io.tmpdir point into it. Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, hashlib, struct, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.3", "0.1.2"
PKG = "com.skyy.profiles."
PREFIX = "SkyyPf"
PAGE_W, PAGE_H = 1100, 980
BODY_ID, BODY_INNER_H = "SkyyPf", 980 - 38 - 2 * 17       # 908
MIN_CONTRAST = 3.0
EXPECTED_DIFF = {"com/skyy/profiles/ProfilePage.class", "com/skyy/profiles/SkyyProfilesPlugin.class", "com/skyy/profiles/CfgFn.class",
                 "com/skyy/profiles/CfgRows.class", "manifest.json"}
SCRIPT = os.path.join(HERE, "build_skyyprofiles_%s.py" % VERSION)
TWIN = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.8.py")          # the other script with the SKYY CARD block
PATCHES = [os.path.join(TOOLS, "profiles_0_1_3_patch.py"), os.path.join(TOOLS, "classes_0_1_8_patch.py")]


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyyprofiles-013")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyProfiles-%s.jar" % OLD_VERSION)))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


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


# ============================================================================================ child: build every page state of one jar
DAY, HOUR = 86400000, 3600000
CREATED = 1700000000000          # 2023-11-14 (a fixed date: the text is identical in both child JVMs)
LONG = "Abcdefghijklmnopqrstuvwxyzabcdef"     # 32 letters (ProfNames / admin names are cut to 32)
STATES = [
    # (name, view, first, profiles [(id, name, class, lastPlayed-ago-ms or 0 = never)], active, pending, pickName, pickClass, info,
    #  max, class:list, kits)
    ("list one", 0, False, [("1", "Profile 1", "Warrior", 3 * DAY + HOUR)], "1", None, "", None, "", 6, None, False),
    ("list two pending", 0, False, [("1", "Main", "Archer", 5 * HOUR + 1800000), ("2", "Alt", "Priest", 0)], "1", "2", "", None, "", 6,
     None, False),
    ("list three active 2", 0, False, [("1", "Apple", "Mage", 30 * DAY), ("2", "Berry", "Berserker", 2 * HOUR), ("3", "Cherry", "Priest",
                                                                                                                 0)], "2", None, "", None,
     "Switched to Berry.", 6, None, False),
    ("list six full", 0, False, [(str(i), "Profile %d" % i, c, i * DAY) for i, c in
                                 zip(range(1, 7), ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Warrior"])], "4", None, "", None,
     "All 6 profile slots are used.", 6, None, False),
    ("list over max", 0, False, [(str(i), "P%d" % i, "Mage", i * HOUR * 50) for i in range(1, 8)], "3", "5", "", None, "", 3, None, False),
    ("list no class", 0, False, [("1", "Old save", "", 4 * DAY), ("2", "New", "Warrior", HOUR * 3)], "2", None, "", None, "", 6, None,
     False),
    ("list extra class", 0, False, [("1", "Dark", "Necromancer", DAY * 2), ("2", "Light", "Priest", HOUR * 5)], "1", "2", "", None, "", 6,
     "Archer,Warrior:Blades,Mage,Berserker,Priest,Necromancer:Death", True),
    ("list long names", 0, False, [("1", LONG, "Berserker", DAY), ("2", LONG[::-1], "Archer", 3 * DAY), ("12", "Twelve", "Mage", 9 * DAY)],
     "12", "1", "", None, "Your profile file was repaired.", 6, None, False),
    ("list pending is active", 0, False, [("1", "Solo", "Priest", DAY)], "1", "1", "", None, "", 1, None, False),
    ("list one of one", 0, False, [("1", "Only", "Archer", 7 * DAY)], "1", None, "", None, "", 1, None, False),
    ("create first", 1, True, [], None, None, "Profile 1", None, "", 6, None, False),
    ("create first pick kits", 1, True, [], None, None, "Mango", "Archer", "Your current class Archer is pre-selected.", 6, None, True),
    ("create new", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Kiwi", None, "", 6, None, True),
    ("create new pick", 1, False, [("1", "Main", "Warrior", DAY), ("2", "Alt", "Mage", HOUR * 9)], "2", None, "Lychee", "Priest", "", 6,
     None, False),
    ("create two classes", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Papaya", "Mage", "", 6, "Warrior,Mage", True),
    ("create eight classes", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Guava", None, "", 6,
     "Archer,Warrior,Mage,Berserker,Priest,Assassin:Stealth,Shaman:Totems,Necromancer:Death", True),
    ("create nine classes", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Fig", "Necromancer", "", 6,
     "Archer,Warrior,Mage,Berserker,Priest,Necromancer:Death,Druid:Nature,Monk:Fists,Bard:Songs", True),
    ("create info later", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Plum", None, "Assassin is coming later.", 6, None,
     False),
    ("create long name", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, LONG, "Berserker", "", 6, None, True),
    ("create first later pick", 1, True, [], None, None, "Pear", "Assassin", "", 6, None, False),
    ("create first berserker", 1, True, [], None, None, "Grape", "Berserker", "", 6, None, True),
    ("create after make error", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Lime", "Warrior",
     "You are in combat - try again in a few seconds.", 6, None, False),
]


def run_states(jar, out):
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
    res = {"jar": jar, "classes": len(names), "loaded": loaded, "load_fails": load_fails, "states": {}}
    if load_fails:
        json.dump(res, open(out, "w"), indent=1)
        return
    Page, Cfg = JClass(PKG + "ProfilePage"), JClass(PKG + "ProfCfg")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UUID, Props, System = JClass("java.util.UUID"), JClass("java.util.Properties"), JClass("java.lang.System")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    @JImplements("java.util.function.Function")
    class KitNew(object):
        @JOverride
        def apply(self, o):
            return JClass("java.lang.Boolean").TRUE

    bridge = Cfg.bridge()
    me = UUID(0x9f013, 1)
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    max0 = int(Cfg.MAX_PROFILES)
    for (name, view, first, profs, active, pending, pick_name, pick_class, info, mx, clist, kits) in STATES:
        for k in ("class:list", "class:fn:kitnew"):
            bridge.remove(k)
        if clist is not None:
            bridge.put("class:list", clist)
        if kits:
            bridge.put("class:fn:kitnew", KitNew())
        Cfg.MAX_PROFILES = mx
        now = int(System.currentTimeMillis())
        p = Props()
        for pid, pname, pcls, ago in profs:
            p.setProperty("p.%s.name" % pid, pname)
            p.setProperty("p.%s.class" % pid, pcls)
            p.setProperty("p.%s.created" % pid, str(CREATED + int(pid) * DAY))
            p.setProperty("p.%s.lastPlayed" % pid, str(now - ago) if ago else "0")
        if active:
            p.setProperty("active", active)
        page = Page(pr, 0, first)                   # view 0 in the constructor: no prepareCreate (no player file needed)
        page.view, page.pending, page.pickName, page.pickClass, page.info = view, pending, pick_name, pick_class, info
        b, ev = UCB(), UEB()
        try:
            if view == 1:
                page.buildCreate(b, ev, me, p)
            else:
                page.buildList(b, ev, me, p)
            err = None
        except Exception as e:
            err = str(e)
        cmds = [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]
        evs = [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data),
                bool(e.locksInterface)] for e in ev.getEvents()]
        res["states"][name] = {"error": err, "commands": cmds, "events": evs}
    Cfg.MAX_PROFILES = max0
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: bytecode method compare (javassist)
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
                  "consts": consts,
                  "version_only": all(mo[k].replace(OLD_VERSION, "V") == mn[k].replace(VERSION, "V") for k in changed)
                  and all((x or "").replace(OLD_VERSION, "V") == (y or "").replace(VERSION, "V") for x, y in consts.values())}
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent: markup model (shared with the
# SkyyClasses 0.1.8 harness part Y - the same code; the SKYY CARD component is one component in both mods)
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
    leaves its parent's content box in issues (decorations with a negative anchor - the gold ornaments - are skipped). Each node
    gets "box" (x, y, w, h) and "inner" (its content box); returns the node list in placement order."""
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
                continue                                     # a decoration (ornament) placed outside on purpose
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


# ---------------------------------------------------------------------------- text (the client's own Nunito Sans glyph advances)
FONT_DIR = None
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
    return {"size": int(fs.group(1)) if fs else 16, "bold": "RenderBold: true" in st, "upper": "RenderUppercase: true" in st,
            "wrap": "Wrap: true" in st, "secondary": 'FontName: "Secondary"' in st, "color": col.group(1) if col else None}


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
                check(tw <= w, "%s: #%s text %.0f px in %d px (%r)" % (name, nd["id"] or "label", tw, w, txt))
                check(st["size"] + 4 <= h, "%s: #%s a %d px line in %d px" % (name, nd["id"], st["size"], h))
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
            bg = None                                   # another texture (the title bar, a button): not measured
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


def texts_of(state):
    """Every visible text of a state: inline Text values + b.set .Text values (non-empty)."""
    inl = [x for t, sel, data, text in state["commands"] if t == "AppendInline" and text for x in _TEXT_RE.findall(text) if x]
    return set(inl) | set(v for v in sets_of(state).values() if v)


def compare_state(name, old, new, SUI, counts, data_colors, page_w, page_h, body_id, body_h):
    check(old["error"] is None and new["error"] is None, "%s: the page built in both jars (%s / %s)" % (name, old["error"], new["error"]))
    if old["error"] or new["error"]:
        return
    # C1 bindings
    check(old["events"] == new["events"], "%s: event bindings identical (%d / %d)" % (name, len(old["events"]), len(new["events"])))
    counts["bindings"] += len(new["events"])
    # C2 ids
    oi, ni = ids_of(old), ids_of(new)
    miss = sorted(set(oi) - set(ni))
    check(not miss, "%s: no old id missing: %s" % (name, miss))
    counts["ids"] += len(set(oi))
    # C3 texts
    ot, nt = texts_of(old), texts_of(new)
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
                SUI.check_markup(text, prefix=PREFIX_OF[0], root=(parent is None))
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
        SUI.check_page(ap, PREFIX_OF[0])
        counts["check_page"] += 1
    except ValueError as e:
        check(False, "%s: check_page: %s" % (name, e))
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


PREFIX_OF = [PREFIX]


def new_counts():
    return dict(states=0, bindings=0, ids=0, texts=0, colours=0, check_page=0, appends=0, placed=0, min_row_slack=10 ** 6, wrapped=0,
                lines=0, buttons=0, max_lines_fill=0.0, max_line_fill=0.0, widest=(0.0, ""), shrunk=set(), text_skipped=False,
                contrasts=0, min_contrast=(99.0, ""), max_payload=0)


def report_counts(counts):
    print("B-D. %(states)d states: %(bindings)d bindings identical, %(ids)d old ids all kept, %(texts)d old texts all shown; "
          "%(check_page)d check_page / %(appends)d appends through check_markup, %(colours)d colours audited, %(placed)d elements placed "
          "by the layout model (tightest Left row slack %(min_row_slack)d px), largest payload %(max_payload)d chars" % counts)
    if counts["text_skipped"]:
        print("   text widths: SKIPPED (no client glyph tables)")
    else:
        print("   text: %d single lines (widest %.0f%%: %s), %d wrapped labels (fullest %.0f%% of their height), %d buttons%s" % (
            counts["lines"], 100 * counts["widest"][0], counts["widest"][1], counts["wrapped"], 100 * counts["max_lines_fill"],
            counts["buttons"], (" (shrink-to-fit at 17 px: %s)" % ", ".join(sorted(counts["shrunk"]))) if counts["shrunk"] else ""))
    print("   contrast: %d labels, lowest %.2f:1 (%s), ContainerPatch centre #%02x%02x%02x" % (
        counts["contrasts"], counts["min_contrast"][0], counts["min_contrast"][1], *patch_centre()))


# ---------------------------------------------------------------------------- E: the SKYY CARD block on its own
def card_block(path):
    src = open(path, encoding="utf8").read().replace("\r\n", "\n")
    a = src.index("# =====================================================================================================================\n# SKYY CARD")
    b = src.index("# ======================================================================= (end of the shared SKYY CARD block)")
    return src[a:b + len("# ======================================================================= (end of the shared SKYY CARD block)")]


def patch_card(path):
    s = open(path, encoding="utf8").read()
    a = s.index("CARD_BLOCK = r'''") + len("CARD_BLOCK = r'''")
    sha = re.search(r'^CARD_SHA = "([0-9a-f]{64})"', s, re.M).group(1)
    return s[a:s.index("'''", a)], sha


class _KitRecorder(object):
    """The kit module as the SKYY CARD block sees it, recording every (parent, markup) it hands to java_append."""

    def __init__(self, sui):
        self._sui, self.appends = sui, []

    def __getattr__(self, name):
        return getattr(self._sui, name)

    def java_append(self, parent, markup, b="b", page_root=True):
        self.appends.append((parent, markup))
        return self._sui.java_append(parent, markup, b, page_root)


def check_card_block(SUI, data_colors):
    mine, twin = card_block(SCRIPT), card_block(TWIN)
    check(mine == twin, "E: the SKYY CARD block is byte-identical in %s and %s" % (os.path.basename(SCRIPT), os.path.basename(TWIN)))
    sha = hashlib.sha256(mine.encode("utf8")).hexdigest()
    for p in PATCHES:
        blk, psha = patch_card(p)
        check(blk == mine and psha == sha, "E: %s carries the same block and CARD_SHA (%s)" % (os.path.basename(p), psha[:12]))
    rec = _KitRecorder(SUI)
    ns = {"SUI": rec, "re": re}
    exec(compile(mine, "SKYY CARD", "exec"), ns)
    allowed = SUI.allowed_colors() | set(SUI.norm_color(c) for c in data_colors)
    n = n_mk = 0
    lines = [{"id": "Nm", "text": "safe(t)", "kind": "rowName", "h": 24, "col": SUI.J("col", "#d9443f"),
              "tag": {"id": "Rl", "text": "safe(r)", "col": SUI.J("col", "#d9443f"), "w": 200}},
             {"id": "Sk", "text": "safe(s)", "kind": "fieldLabel", "h": 20, "col": "value"},
             {"id": "Ds", "text": "safe(d)", "kind": "rowSub", "h": 40, "col": "rowSub", "wrap": True}]
    for look in list(ns["CARD_LOOKS"]) + [[("selected", "sel"), ("pending", "pend"), ("normal", "on"), "off"]]:
        for icons, on in ((None, None), ("ic", "on")):
            del rec.appends[:]
            java = ns["card_java"]({"list": PREFIX + "List", "card": PREFIX + "Card" + SUI.J("i", "1"),
                                    "text": PREFIX + "Txt" + SUI.J("i", "1"), "act": PREFIX + "Act" + SUI.J("i", "1")}, 1058, look, lines,
                                   icons=icons,
                                   icon_item=SUI.J("safe(x)", "Weapon_Sword_Crude"), icon_max=3 if icons else 1, on=on)
            check(len(rec.appends) == 12 and java.count("appendInline(") == 12 and java.count(".Text\"") == 4,
                  "E: card_java(%s, %s): 12 appends + 4 b.set texts (got %d / %d)" % (look, icons, len(rec.appends), java.count(".Text\"")))
            for parent, mk in rec.appends:
                try:
                    SUI.check_markup(mk, prefix=PREFIX)
                except ValueError as e:
                    check(False, "E: card markup (%s): %s" % (look, e))
                for v in (mk.variants() if isinstance(mk, SUI.Choice) else [mk]):
                    for c in _COL_RE.findall(SUI.render(v)):
                        check(SUI.norm_color(c) in allowed, "E: card colour %s (%s) is a kit / data colour" % (c, look))
                n_mk += 1
            n += 1
    check(set(ns["CARD_LOOKS"]) == {"selected", "pending", "normal", "off", "empty"}, "E: the five card looks")
    check(ns["CARD_LOOKS"]["selected"] == ("rowPressed", "selected"), "E: the selected look = the row pressed step + the blue bar "
                                                                      "(review fix: contrast)")
    for look, (bg, bar) in ns["CARD_LOOKS"].items():
        check(bg in SUI.COLOR and bar in SUI.COLOR, "E: look %s uses kit colours (%s, %s)" % (look, bg, bar))
    check(ns["card_list_h"](8) == 8 + 8 * 88 and ns["card_text_w"](1058, 3) == 1058 - 4 - 216 - 200 - 12, "E: card sizes")
    print("E. SKYY CARD block: identical in both scripts + both patches (sha %s), %d look x cell variants, %d markups checked"
          % (sha[:12], n, n_mk))


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
    if not SCRATCH.replace("\\", "/").lower().startswith(os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower()):
        sys.exit("--dir must be inside tools/dev/scratch/ (it is deleted afterwards): " + SCRATCH)
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
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                            os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    # B-D
    import skyyui as SUI
    SUI.verify(quiet=True)
    src = open(SCRIPT, encoding="utf8").read()
    data_colors = eval(re.search(r"^UI_DATA_COLORS = (\[.*?\](?:\s*\+\s*\[.*?\])?)\n", src, re.M | re.S).group(1))
    counts = new_counts()
    for st in STATES:
        nm = st[0]
        check(nm in new["states"] and nm in old["states"], "B: state %s built by both jars" % nm)
        if nm in new["states"] and nm in old["states"]:
            compare_state(nm, old["states"][nm], new["states"][nm], SUI, counts, data_colors, PAGE_W, PAGE_H, BODY_ID, BODY_INNER_H)
    report_counts(counts)
    # E
    check_card_block(SUI, data_colors)
    # F
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    check(sorted(zo.namelist()) == sorted(zn.namelist()), "F: same entries in both jars")
    diff = set(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    same = len(set(zo.namelist()) & set(zn.namelist())) - len(diff)
    check(diff <= EXPECTED_DIFF, "F: only %s differ, got %s" % (sorted(EXPECTED_DIFF), sorted(diff)))
    check(not [n for n in zn.namelist() if n.endswith(".ui")], "F: no .ui files in the jar (inline pages only)")
    mo, mn = json.loads(zo.read("manifest.json")), json.loads(zn.read("manifest.json"))
    check(set(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k)) <= {"Version", "Name", "Description"} and mn.get("Version") == VERSION,
          "F: manifest: only the version differs: %s" % sorted(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k)))
    bc = json.load(open(bco))
    pg = bc.get("com/skyy/profiles/ProfilePage.class", {})
    sig = "(Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;" \
          "Ljava/util/UUID;Ljava/util/Properties;)V"
    check(pg.get("changed") == ["buildCreate" + sig, "buildList" + sig] and not pg.get("new") and not pg.get("gone")
          and pg.get("fields_same"), "F: ProfilePage: only buildList / buildCreate changed: %s" % pg)
    sp = bc.get("com/skyy/profiles/SkyyProfilesPlugin.class", {})
    check(sp.get("changed") == ["setup()V"] and not sp.get("new") and not sp.get("gone") and sp.get("fields_same"),
          "F: SkyyProfilesPlugin: only setup() (the ready line) changed: %s" % sp)
    for k in ("com/skyy/profiles/CfgFn.class", "com/skyy/profiles/CfgRows.class"):
        c = bc.get(k)
        if c is None:
            continue
        check(not c.get("new") and not c.get("gone") and c.get("fields_same") and c.get("version_only"),
              "F: %s: only the version string differs: %s" % (k, c))
    print("F. class bytes: %d entries identical, differ: %s; methods: %s" % (
        same, ", ".join(sorted(n.split("/")[-1] for n in diff)),
        "; ".join("%s %s" % (n.split("/")[-1][:-6], dict((x, bc[n][x]) for x in ("changed", "new", "gone", "consts") if bc[n][x]))
                  for n in sorted(bc))))
    return finish()


def finish():
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyyProfiles %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
