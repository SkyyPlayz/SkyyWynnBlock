"""Bare-JVM page harness for SkyyIslands 0.5.4 - the look-only restyle of the island menu (IslandMenuPage, /island menu) on the shared
UI kit tools/skyyui.py. Committed next to the build so the build docstring's CHECKED claims can be re-run instead of trusted; copy it
to the next version and keep it passing.

    python SkyyIslands/test_skyyislands_0.5.4.py [--jar <SkyyIslands-0.5.4.jar>] [--old <SkyyIslands-0.5.3.jar>] [--dir <scratch>] [--keep]

Build first (python tools/islands_0_5_4_patch.py, then python SkyyIslands/build_skyyislands_0.5.4.py). When the kit output changed
the page, that build stops (the page gate): build once with SKYY_UNCHECKED_PAGE=1 (-> SkyyIslands-0.5.4-UNCHECKED.jar), run this
harness with --jar on it, set PAGE_CHECKED in the patch to the id F prints, regenerate, rebuild without the flag and re-run. One JVM (the game's JRE,
-Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath; EACH SkyyIslands jar in its own class loader,
so 0.5.3 - the live SET pin - and 0.5.4 run side by side; online players / island worlds are an Unsafe-allocated Universe + Worlds +
PlayerRefs, no server, no client). It checks:
  A  every class of both jars loads, verifies and initialises
  B  the restyle contract in bytes: the same class names; every class but IslandMenuPage and SkyyIslandsPlugin byte-identical or
     different ONLY in constant-pool strings that differ by the version ("0.5.3" -> "0.5.4": the config text and the config kit's
     version constant); SkyyIslandsPlugin = 0.5.3's bytes once its one ready-log constant is swapped back (and that constant names
     the kit and the page id); IslandMenuPage (javassist, constant-pool indices resolved): the same fields and superclass, and the
     constructor, safe, jsonStr, two, date, idx, closePage and handleDataEvent instruction-identical
  C  differential page builds, 0.5.3 vs 0.5.4, in 20 island states (no island, an invite with / without Accept, an island that is
     gone, an unreadable file, owner alone / with a full co-op / 8 co-op slots / customised grids / cooldown / every "click again"
     arm, island admin with and without the invite switch, plain member ...) x the 5 tabs x result marks, with the engine's own
     UICommandBuilder / UIEventBuilder: identical event bindings (type, selector, EventData, lock, ORDER), identical b.set lines
     (targets + values; countdowns normalised), identical inline texts (button labels, placeholder), every 0.5.3 element id still
     created; the 0.5.4 markup as sent passes SUI.check_markup (the page root included) and SUI.check_page, SUI.assert_proven
     (proven properties only, nothing UNVERIFIED), only kit colours or the declared UI_DATA_COLORS; the layout: the frame body
     column is filled exactly (908 px), #SkyyIsBody (713 px) holds every tab of every state, every LayoutMode Left row holds its
     children (widths) and every fixed-height column its children (heights); the column heads line up with their rows (review
     fix): the first glyph of "   What" sits over the first glyph of every permission name, "   On the island now" over every
     visitor name, "Banned" over every banned name (x = the ancestors' paddings + the earlier siblings' widths in Left rows +
     the leading spaces measured with the kit's text_width; within 1 px - 3 px on the fallback widths)
  D  clicks through handleDataEvent (the real page method; rebuild() / closePage() fail harmlessly outside a server and are caught
     by the page itself) - 4 scenarios, 60+ clicks per jar (tabs, name box, invite, trust, promote, demote, kick x2, untrust, the
     pagers, every permission column, reset to defaults x2, visit mode, limit, ping, expel, trust, ban x2, unban, PvP, spawning,
     reset arms, disband x2, leave x2, accept, decline, bogus payloads, close): identical result line, arm, name box, tab, pages,
     island files (every key / value; times normalised), invites and rebuilt page after every click
  E  text fit with the client's font tables (the kit's text_width; the fallback widths when the client is not installed): every
     button label fits its button minus 2 x its padding, every one-line label fits its box, every wrapped label its lines
  F  the page id: IS_PAGE_ID of the kit's page NOW (the generated script's page code run without a JVM) == IS_PAGE_CHECKED in the
     generated script == the page id in the jar's ready log line; the page gate (review fix): a mismatch stops the build
     (SystemExit) unless SKYY_UNCHECKED_PAGE=1, which only ever names the jar SkyyIslands-0.5.4-UNCHECKED.jar (never deployed by
     tools/deploy_set.py); a run on that -UNCHECKED jar always fails F (rebuild without the flag once PAGE_CHECKED is set)
Not testable without the game (UNVERIFIED in the build docstring): how the client draws the page, the textures / sounds, the real
PageManager, rebuild() and closePage() on a live page, teleports / chat lines to other players.
Nothing is deployed and nothing outside the scratch folder is written (default tools/dev/scratch/test-islands-054, deleted at the end
unless --keep; TEMP / TMP and java.io.tmpdir point into it). Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.5.4", "0.5.3"
PKG = "com.skyy.islands."
SCRIPT = os.path.join(HERE, "build_skyyislands_%s.py" % VERSION)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "test-islands-054")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyIslands-%s.jar" % OLD_VERSION)))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
COUNT = {}


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        if len(FAILS) < 60:
            print("FAIL", what)
    return cond


def tally(key, n=1):
    COUNT[key] = COUNT.get(key, 0) + n


# ------------------------------------------------------------------------------------------------ the kit's page, NOW (no JVM)
def kit_page():
    """Run the generated script's page code (the 0.5.4 look block and the tab builders) on the CURRENT kit with a stub M() - no
    javassist: returns (SUI, namespace) with IS_PAGE_ID, IS_PAGE_CHECKED, IS_BODY_H, IS_SH, UI_DATA_COLORS ..."""
    import skyyui as SUI
    SUI.verify(quiet=True)
    src = open(SCRIPT, encoding="utf8").read().replace("\r\n", "\n")
    a = src.index("# ---- 0.5.4: the island menu look")
    b = src.index('M(page, r"""\npublic void closePage(')
    c = src.index("IS_TAB_SRC = [is_src(")
    d = src.index('M(page, r"""\npublic void handleDataEvent(')
    udc = None
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "UI_DATA_COLORS" for t in n.targets):
            udc = ast.literal_eval(n.value)
    ns = {"SUI": SUI, "re": re, "os": os, "M": (lambda cls, s: None), "page": None, "T": {}, "UI_DATA_COLORS": udc,
          "KIT_ID": SUI.kit_id()}
    import io, contextlib
    # the page gate at the end of the page code stops an unchecked page; here the harness IS the check, so it runs the page code
    # with the override (F compares IS_PAGE_ID with IS_PAGE_CHECKED itself)
    was = os.environ.get("SKYY_UNCHECKED_PAGE")
    os.environ["SKYY_UNCHECKED_PAGE"] = "1"
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(src[a:b] + "\n" + src[c:d], SCRIPT, "exec"), ns)
    finally:
        if was is None:
            del os.environ["SKYY_UNCHECKED_PAGE"]
        else:
            os.environ["SKYY_UNCHECKED_PAGE"] = was
    return SUI, ns


def gate_src():
    """the page gate block of the generated script (between its '# ---- page gate' and '# ---- end page gate' lines)"""
    src = open(SCRIPT, encoding="utf8").read().replace("\r\n", "\n")
    a = src.index("# ---- page gate (0.5.4 review)")
    return src[a:src.index("# ---- end page gate", a)], src


# ------------------------------------------------------------------------------------------------ class-file helpers (no JVM)
def cp_split(b):
    """(utf8 entries [(start, end, bytes)], the class bytes with every Utf8 entry's bytes cut out) - the constant pool walk"""
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
    rest, pos = [], 0
    for s0, e0, _t in out:
        rest.append(b[pos:s0 + 1])
        pos = e0
    rest.append(b[pos:])
    return out, b"|".join(rest)


def version_only(old, new):
    """True when two class files differ only in Utf8 constants that are equal once the versions are normalised"""
    uo, ro = cp_split(old)
    un, rn = cp_split(new)
    if ro != rn or len(uo) != len(un):
        return False
    norm = lambda t: t.replace(OLD_VERSION.encode(), b"<V>").replace(VERSION.encode(), b"<V>")
    return all(a[2] == b[2] or norm(a[2]) == norm(b[2]) for a, b in zip(uo, un))


def classes(jar):
    z = zipfile.ZipFile(jar)
    out = dict((n[:-6].replace("/", "."), z.read(n)) for n in z.namelist() if n.endswith(".class"))
    z.close()
    return out


# ------------------------------------------------------------------------------------------------ markup helpers
TOP_RE = re.compile(r"\A\s*([A-Za-z]+)(?:\s+#([A-Za-z0-9_]+))?\s*\{")
TEXT_RE = re.compile(r'(?:\bText|PlaceholderText): "((?:[^"\\]|\\.)*)"')


def top_of(mk):
    m = TOP_RE.match(mk)
    return (m.group(1), m.group(2)) if m else (None, None)


def pad_of(SUI, mk):
    p = SUI._top_prop(SUI._own_props(mk), "Padding")
    out = {"Left": 0, "Right": 0, "Top": 0, "Bottom": 0}
    if not p:
        return out
    for k, v in re.findall(r"(Left|Right|Top|Bottom|Horizontal|Vertical|Full): (-?\d+)", p):
        v = int(v)
        if k in ("Horizontal", "Full"):
            out["Left"] += v
            out["Right"] += v
        if k in ("Vertical", "Full"):
            out["Top"] += v
            out["Bottom"] += v
        if k in out:
            out[k] += v
    return out


# ------------------------------------------------------------------------------------------------ the JVM part
def run():
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    SUI, K = kit_page()
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

    L = {"old": loader(OLD), "new": loader(JAR)}
    CB = {"old": classes(OLD), "new": classes(JAR)}

    # ---------------- A. load + verify + init, both jars
    for k in ("old", "new"):
        for n in sorted(CB[k]):
            try:
                Cls.forName(n, True, L[k])
                OKS[0] += 1
                tally("A classes " + k)
            except Exception as e:
                check(False, "A. %s: load %s: %s" % (k, n, e))
    print("A. loaded + verified + initialised: 0.5.3 %d, 0.5.4 %d classes (-Xverify:all)" % (COUNT.get("A classes old", 0),
                                                                                         COUNT.get("A classes new", 0)))
    if FAILS:
        return

    # ---------------- B. the restyle contract in bytes
    old, new = CB["old"], CB["new"]
    check(sorted(old) == sorted(new), "B. the same class names: %s" % sorted(set(old) ^ set(new)))
    page_c, plug_c = PKG + "IslandMenuPage", PKG + "SkyyIslandsPlugin"
    vonly = []
    for n in sorted(old):
        if n in (page_c, plug_c) or n not in new:
            continue
        if old[n] == new[n]:
            tally("B identical")
            OKS[0] += 1
        elif check(version_only(old[n], new[n]), "B. %s differs by more than the version string" % n):
            vonly.append(n.split(".")[-1])
    COUNT["B version only"] = vonly
    uo, _ro = cp_split(old[plug_c])
    un, _rn = cp_split(new[plug_c])
    ready_old = [e for e in uo if b"] 0.5.3 ready" in e[2]]
    ready_new = [e for e in un if b"] 0.5.4 ready" in e[2]]
    LOG_NEW = ""
    if check(len(ready_old) == 1 and len(ready_new) == 1, "B. one ready-log constant in each SkyyIslandsPlugin"):
        s0, e0, t0 = ready_old[0]
        s1, e1, t1 = ready_new[0]
        swapped = new[plug_c][:s1] + old[plug_c][s0:e0] + new[plug_c][e1:]
        check(swapped == old[plug_c] or version_only(old[plug_c], swapped),
              "B. SkyyIslandsPlugin = 0.5.3's bytes once the ready-log constant is swapped back")
        LOG_NEW = t1.decode("utf8")
        tail0 = t0.decode("utf8")[len("[SkyyIslands] 0.5.3 ready"):]
        m = re.match(r"\A\[SkyyIslands\] 0\.5\.4 ready \((skyyui [0-9.]+ [0-9a-f]{12}), page ([0-9a-f]{12})\)(.*)\Z", LOG_NEW, re.S)
        check(m is not None and m.group(3) == tail0, "B. the 0.5.4 ready constant = 0.5.3's + the kit and the page id: %r" % LOG_NEW[:120])
    CP = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def ct(bb):
        return CP(False).makeClass(BAIS(bb))

    def code_of(m):
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        cp = mi.getConstPool()
        if ca is None:
            return ["<no code>"]
        it, out = ca.iterator(), []
        while it.hasNext():
            pos = it.next()
            ln = re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cp))).replace("ldc_w ", "ldc ")
            out.append(re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln))
        et = ca.getExceptionTable()
        for i in range(et.size()):
            ctp = et.catchType(i)
            out.append("try %s" % (cp.getClassInfo(ctp) if ctp else "any"))
        return out

    def methods(c):
        out = {}
        for m in list(c.getDeclaredMethods()) + list(c.getDeclaredConstructors()):
            out[str(m.getMethodInfo().getName()) + str(m.getSignature())] = code_of(m)
        return out

    po, pn = ct(old[page_c]), ct(new[page_c])
    check(sorted((str(f.getName()), str(f.getSignature())) for f in po.getDeclaredFields())
          == sorted((str(f.getName()), str(f.getSignature())) for f in pn.getDeclaredFields()), "B. IslandMenuPage fields unchanged")
    check(str(po.getClassFile().getSuperclass()) == str(pn.getClassFile().getSuperclass()), "B. IslandMenuPage superclass unchanged")
    mo, mn = methods(po), methods(pn)
    gone = sorted(k.split("(")[0] for k in mo if k not in mn)
    added = sorted(k.split("(")[0] for k in mn if k not in mo)
    changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k])
    same = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] == mn[k])
    for keep in ("<init>", "safe", "jsonStr", "two", "date", "idx", "closePage", "handleDataEvent"):
        check(keep in same, "B. IslandMenuPage.%s is instruction-identical to 0.5.3" % keep)
    LOOKM = {"build", "buildTabs", "buildOverview", "buildMembers", "buildPerms", "buildVisitors", "buildIsland", "gap", "dot"}
    check(set(changed) <= LOOKM, "B. IslandMenuPage: only the look methods changed: %s" % changed)
    check(set(gone) <= {"style", "lbl", "btn", "row", "twoLine", "cell"}, "B. IslandMenuPage: only 0.5.3's look helpers are gone: %s" % gone)
    COUNT["B page"] = (same, changed, gone, added)
    print("B. %d classes byte-identical, %d differ only by the version string (%s); SkyyIslandsPlugin = 0.5.3 but its ready constant; "
          "IslandMenuPage: %d methods instruction-identical %s, changed %s, gone %s, new %d (%s)"
          % (COUNT.get("B identical", 0), len(vonly), ", ".join(vonly), len(same), same, changed, gone, len(added), ", ".join(added)))

    # ---------------- the fake server: Universe (players + worlds), Worlds, PlayerRefs; the shared bridge
    UUID, Paths, Long, Integer = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Integer")
    System, CHM, COWAL = JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.concurrent.CopyOnWriteArrayList")
    AtomicBoolean = JClass("java.util.concurrent.atomic.AtomicBoolean")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Universe = JClass("com.hypixel.hytale.server.core.universe.Universe")
    World = JClass("com.hypixel.hytale.server.core.universe.world.World")
    Holder = JClass("com.hypixel.hytale.component.Holder")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    uni = U.allocateInstance(Universe.class_)
    PLAYERS, WORLDS = CHM(), CHM()
    setf(uni, Universe, "playersByUuid", PLAYERS)
    setf(uni, Universe, "worlds", WORLDS)
    setf(None, Universe, "instance", uni)
    holder = U.allocateInstance(Holder.class_)
    BR = CHM()
    System.getProperties().put("skyy.bridge", BR)
    PROFILE = {}                      # uuid str -> active profile key (absent = the uuid = profile 1)

    @JImplements("java.util.function.Function")
    class ProfKey:
        @JOverride
        def apply(self, u):
            return PROFILE.get(str(u), str(u))

    def uid(n):
        return UUID(0x15a0, n)

    def key(n, prof=1):
        return str(uid(n)) + ("" if prof == 1 else "-p%d" % prof)

    NAMES = {1: "Steve", 2: "Alex", 3: "Bea", 4: "Cid", 5: "Dot", 6: "Eve", 7: "Finn", 8: "Gus", 9: "Hal", 10: "Ida", 11: "Jon",
             20: "Owen", 21: "Ivy", 30: "Olga", 40: "Pam", 41: "Quinn", 50: "Rex", 60: "Sam", 61: "Averyverylongnam"}
    REFS = {}

    def ref(n, online=True):
        if n in REFS:
            p = REFS[n]
        else:
            p = U.allocateInstance(PR.class_)
            setf(p, PR, "uuid", uid(n))
            setf(p, PR, "username", NAMES.get(n, "Player%d" % n))
            setf(p, PR, "holder", holder)
            REFS[n] = p
        if online:
            PLAYERS.put(uid(n), p)
        return p

    def world(name, ns):
        w = U.allocateInstance(World.class_)
        setf(w, World, "alive", AtomicBoolean(True))
        l = COWAL()
        for n in ns:
            l.add(ref(n))
        setf(w, World, "playerRefs", l)
        WORLDS.put(name.lower(), w)
        return w

    def jc(k, name):
        return JClass(PKG + name, loader=L[k])

    NOW = int(time.time() * 1000)
    FLAGS = ["build", "break", "containers", "doors", "crafting", "processing", "beds", "seats", "harvest", "animals", "mobs", "pickup",
             "drop", "other"]

    def island(owner, world_on=True, members=(), admins=(), trusted=(), banned=(), extra=None, names=None):
        """the properties of one island file (v=5); keys are profile keys / uuid strings"""
        p = {"v": "5", "ownerName": NAMES.get(owner, "Player%d" % owner)}
        if world_on:
            p["world"] = "skyy-island-" + key(owner)
        p["members"] = ",".join(members)
        p["admins"] = ",".join(admins)
        p["trusted"] = ",".join(trusted)
        p["banned"] = ",".join(banned)
        for kk, nm in (names or {}).items():
            p["name." + kk] = nm
        for i, m in enumerate(members):
            if i % 2 == 0:
                p["coopSince." + m] = str(1758000000000 + i * 86400000)
        p.update(extra or {})
        return p

    def invite(target, owner_key, inviter, owner_name, secs):
        a = JArray(JObject)(5)
        a[0], a[1], a[2] = JClass("java.lang.String")(owner_key), uid(inviter), Long(NOW + secs * 1000)
        a[3], a[4] = JClass("java.lang.String")(NAMES.get(inviter, "Player%d" % inviter)), JClass("java.lang.String")(owner_name)
        return uid(target), a

    MEMBERS5 = [key(2), key(3), key(4), key(5)]
    TRUSTED14 = [key(6), key(9)] + [key(200 + i, 2 if i % 3 == 0 else 1) for i in range(12)]
    BANNED11 = [str(uid(100 + i)) for i in range(11)]
    FULLNAMES = dict([(key(n), NAMES[n]) for n in (2, 3, 4, 5, 6, 9)] + [(key(200 + i, 2 if i % 3 == 0 else 1), "Trusty%d" % i) for i in range(12)]
                     + [(b, "Banned%d" % i) for i, b in enumerate(BANNED11)])
    GRID = {"perm.beds": "visitor", "perm.doors": "trusted", "perm.mobs": "admin", "perm.harvest": "owner"}

    # name: (files {owner n: props or "BAD"}, online players, worlds {owner n: [players on it]}, invites, cfg, page fields)
    def st(files, online=(1,), worlds=None, invites=(), cfg=None, page=None, profile=None, load=()):
        return {"files": files, "online": online, "worlds": worlds or {}, "invites": invites, "cfg": cfg or {}, "page": page or {},
                "profile": profile or {}, "load": load}

    FULL = island(1, members=MEMBERS5, admins=[key(2)], trusted=TRUSTED14, banned=BANNED11, names=FULLNAMES,
                  extra=dict(GRID, **{"visit.mode": "friends", "visit.limit": "7", "visit.notify": "1", "pvp": "1",
                                      "resetAt": str(NOW - 3600000)}))
    FULL_ARM = dict(FULL, resetAt="0")
    STATES = {
        "no island": st({}),
        "no island + invite": st({20: island(20)}, online=(1, 20), invites=[invite(1, key(20), 20, "Owen", 45)], load=(20,)),
        "island gone": st({30: island(30, world_on=False, members=[key(1)])}, load=(30,)),
        "file unreadable": st({1: "BAD"}),
        "owner alone": st({1: island(1)}),
        "owner full": st({1: FULL}, online=(1, 2, 4, 5, 6, 7, 8, 40), worlds={1: [1, 2, 6, 7, 8]},
                         invites=[invite(40, key(1), 1, "Steve", 42), invite(41, key(1), 1, "Steve", 17)],
                         page={"trustPage": 1, "banPage": 1}, profile={str(uid(4)): key(4, 2)}),
        "owner full page 1": st({1: FULL}, online=(1, 2, 4, 5, 6, 7, 8), worlds={1: [1, 61, 2, 6, 7, 8, 9, 10, 11]},
                                profile={str(uid(4)): key(4, 2)}),
        "owner 8 co-op slots": st({1: island(1, members=[key(n) for n in range(2, 9)], names=dict((key(n), NAMES[n]) for n in range(2, 9)))},
                                  online=(1, 2, 3), cfg={"COOP_MAX": 8}),
        "owner no build grid": st({1: island(1, extra={"perm.build": "member", "pvp": "0", "spawning": "1", "visit.mode": "closed"})}),
        "owner long denied list": st({1: island(1, extra={"perm.doors": "member", "perm.seats": "member", "perm.mobs": "member",
                                                          "perm.drop": "member", "perm.other": "member"})}),
        "owner + invite it can't take": st({1: island(1, members=[key(2)]), 20: island(20)}, online=(1, 2, 20),
                                           invites=[invite(1, key(20), 20, "Owen", 30)], load=(20,)),
        "admin": st({50: island(50, members=[key(1), key(21)], admins=[key(1)], trusted=[key(6)], banned=BANNED11[:3],
                                names={key(1): "Steve", key(21): "Ivy", key(6): "Eve"})},
                    online=(1, 50, 7), worlds={50: [50, 1, 7]}, load=(50,)),
        "admin, invites off": st({50: island(50, members=[key(1)], admins=[key(1)])}, online=(1, 50), load=(50,),
                                 cfg={"ADMINS_INVITE": False, "STRICT_OTHER": False}),
        "member": st({60: island(60, members=[key(1)], names={key(1): "Steve"}), 20: island(20)}, online=(1, 60, 20),
                     invites=[invite(1, key(20), 20, "Owen", 50)], load=(60, 20)),
    }
    ARMS = [("owner arm disb", "owner full", "disb"), ("owner arm reset1", "owner full", "reset1"),
            ("owner arm reset2", "owner full", "reset2"), ("owner arm pdef", "owner full", "pdef"),
            ("owner arm kick", "owner full", "kk:" + key(3)), ("owner arm ban", "owner full", "vb:" + str(uid(7))),
            ("member arm leave", "member", "leave")]
    for nm, base, arm in ARMS:
        s2 = dict(STATES[base])
        s2["files"] = dict(s2["files"])
        if base == "owner full":
            s2["files"][1] = FULL_ARM
        s2["page"] = dict(s2["page"], confirm=arm, confirmUntil=NOW + 600000)
        STATES[nm] = s2
    COUNT["C states"] = len(STATES)

    def setup(k, name):
        s = STATES[name]
        Store, Cfg = jc(k, "IslandStore"), jc(k, "IslandCfg")
        d = os.path.join(SCRATCH, "islands", k, re.sub(r"[^A-Za-z0-9]+", "-", name))
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        Store.DIR = Paths.get(d)
        for m in ("SETTINGS", "MEMBER_OF", "INVITES", "CONFIRM", "EXPELLED", "PINGED", "EXPELLING", "RESETTING", "LOCKS", "BAD",
                  "KITDONE", "CREATING", "WORLD_OWNER", "SEEN", "EPOCH", "WARNED"):
            getattr(Store, m).clear()
        Store.ISLAND_WORLDS.clear()
        Cfg.COOP_MAX, Cfg.ADMINS_INVITE, Cfg.STRICT_OTHER, Cfg.TRUSTED_MAX, Cfg.BANS_MAX = 5, True, True, 20, 100
        Cfg.RESET_HOURS, Cfg.RESET_CONFIRM, Cfg.INVITE_SECONDS = 24, 20, 60
        for f, v in s["cfg"].items():
            setattr(Cfg, f, v)
        PLAYERS.clear()
        WORLDS.clear()
        BR.clear()
        PROFILE.clear()
        PROFILE.update(s["profile"])
        BR.put("profile:fn:key", ProfKey())
        for n in s["online"]:
            ref(n)
        for owner, props in s["files"].items():
            f = os.path.join(d, key(owner) + ".properties")
            if props == "BAD":
                os.makedirs(f)                 # a folder where the file should be: the file exists but can't be read
            else:
                with open(f, "w", encoding="latin-1") as fh:
                    fh.write("".join("%s=%s\n" % (kk, v) for kk, v in props.items()))
        for owner, ns in s["worlds"].items():
            world("skyy-island-" + key(owner), ns)
        for owner in s["load"]:
            Store.settings(key(owner))         # registers co-op members (MEMBER_OF), as the server's start-up scan does
        for t, a in s["invites"]:
            # a fresh copy that expires <secs> after THIS setup (not after the harness start): the old and the new jar run of a
            # state see the same invites even when the run passes an invite's end in between (the 17 s invite of "owner full")
            a2 = JArray(JObject)(5)
            for i in range(5):
                a2[i] = a[i]
            a2[2] = Long(int(time.time() * 1000) + (int(a[2].longValue()) - NOW))
            Store.INVITES.put(t, a2)
        return Store, d

    def new_page(k, name, tab=0, info=""):
        pg = jc(k, "IslandMenuPage")(ref(1))
        pg.tab = tab
        pg.info = info
        for f, v in STATES[name]["page"].items():
            setattr(pg, f, v)
        return pg

    def build(pg):
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        cmds = [(str(c.type), None if c.selector is None else str(c.selector), None if c.text is None else str(c.text),
                 None if c.data is None else str(c.data)) for c in b.getCommands()]
        evs = [(str(e.type), str(e.selector), None if e.data is None else str(e.data), bool(e.locksInterface)) for e in ev.getEvents()]
        return cmds, evs

    NORM = [(re.compile(r"\b\d+ s left"), "N s left"), (re.compile(r"\((\d+) s\)"), "(N s)"),
            (re.compile(r"in \d+ h \d+ min|in \d+ min"), "in <t>")]

    def norm(t):
        for rx, rp in NORM:
            t = rx.sub(rp, t)
        return t

    def set_value(data):
        try:
            d = json.loads(data)
        except Exception:
            return data
        return d.get("0") if isinstance(d, dict) and "0" in d else d

    def sets_of(cmds):
        return sorted((sel, norm(str(set_value(data)))) for typ, sel, text, data in cmds if "append" not in typ.lower())

    def appends_of(cmds):
        return [(None if sel is None else sel.lstrip("#"), text) for typ, sel, text, data in cmds if "append" in typ.lower()]

    def ids_of(aps):
        return set(i for _p, t in aps for i in re.findall(r"#([A-Za-z0-9_]+)\s*\{", t))

    def texts_of(aps):
        return sorted(norm(t) for _p, mk in aps for t in TEXT_RE.findall(mk) if t)

    ALLOWED = set(SUI.allowed_colors()) | set(SUI.norm_color(c) for c in K["UI_DATA_COLORS"].values())
    BODY_H, IW, IH = K["IS_BODY_H"], K["IS_SH"].inner_w, K["IS_SH"].inner_h
    SEEN_TEXT = {}                                  # label / button id -> texts seen (for E)
    BODY_USED = {}

    def layout(tag, aps, setv):
        """the 0.5.4 layout of one build: the frame body column filled exactly, #SkyyIsBody holds its tab, every Left row its
        children's widths (and heights), every fixed-height column its children's heights; collects texts for E"""
        info, kids = {}, {}
        for p, mk in aps:
            typ, ident = top_of(mk)
            vals = SUI._anchor_vals(mk)
            own = SUI._own_props(mk)
            lay = SUI._top_prop(own, "LayoutMode")
            if ident:
                info[ident] = {"parent": p, "layout": lay, "w": vals.get("Width"), "h": vals.get("Height"), "pad": pad_of(SUI, mk),
                               "type": typ}
            if p is not None:
                kids.setdefault(p, []).append(mk)

        def inner_w(ident):
            if ident == "SkyyIsRoot":
                return IW
            e = info.get(ident)
            if e is None:
                return None
            w = e["w"] if e["w"] is not None else (inner_w(e["parent"]) if e["parent"] else None)
            return None if w is None else w - e["pad"]["Left"] - e["pad"]["Right"]

        def inner_h(ident):
            if ident == "SkyyIsRoot":
                return IH
            e = info.get(ident)
            if e is None or e["h"] is None:
                return None
            return e["h"] - e["pad"]["Top"] - e["pad"]["Bottom"]

        for cid, ch in kids.items():
            e = info.get(cid)
            lay = "Top" if cid == "SkyyIsRoot" else (e["layout"] if e else None)
            if lay == "Top":
                hs = [SUI.outer_size(mk)[1] for mk in ch]
                if not check(None not in hs, "C. %s: a child of #%s without a Height" % (tag, cid)):
                    continue
                room = inner_h(cid)
                if cid == "SkyyIsRoot":
                    check(sum(hs) == IH, "C. %s: the frame body column is %d px, not %d" % (tag, sum(hs), IH))
                elif room is not None:
                    check(sum(hs) <= room, "C. %s: #%s holds %d px in %d px" % (tag, cid, sum(hs), room))
                if cid == "SkyyIsBody":
                    BODY_USED[tag] = sum(hs)
                tally("C columns")
            elif lay == "Left":
                sz = [SUI.outer_size(mk) for mk in ch]
                ws = [z[0] for z in sz]
                if not check(None not in ws, "C. %s: a child of row #%s without a Width" % (tag, cid)):
                    continue
                room = inner_w(cid)
                check(room is not None and sum(ws) <= room, "C. %s: row #%s holds %s px in %s px" % (tag, cid, sum(ws), room))
                hr = inner_h(cid)
                if hr is not None:
                    check(all(z[1] is None or z[1] <= hr for z in sz), "C. %s: a child of row #%s is taller than %d px" % (tag, cid, hr))
                tally("C rows")
        # texts for E: every label / button with its box
        for p, mk in aps:
            typ, ident = top_of(mk)
            if typ not in ("Label", "TextButton"):
                continue
            vals = SUI._anchor_vals(mk)
            txt = TEXT_RE.search(mk)
            t = txt.group(1) if txt and txt.group(1) else setv.get("#%s.Text" % ident)
            if not t:
                continue
            w = vals.get("Width")
            if w is None:
                w = inner_w(p) if typ == "Label" else None
            if typ == "Label" and ident == "SkyyIsL0":
                w = K["IS_W"]                  # the title label fills the title bar
            SEEN_TEXT.setdefault((typ, ident if not re.match(r"SkyyIsL\d+$", ident or "") else "L", mk.split("Text:")[0][-200:], w,
                                  vals.get("Height"), mk[mk.find("Style"):mk.find("Style") + 400]), set()).add(t)

    ALIGN_TOL = 1.0 if SUI.font_table("Default") else 3.0

    def lead_px(mk, text):
        """the width of text's leading spaces in label markup mk's own style"""
        stl = mk[mk.find("Style"):]
        n = len(text) - len(text.lstrip(" "))
        if not n:
            return 0.0
        return SUI.text_width(" " * n, int(re.search(r"FontSize: (\d+)", stl).group(1)), "RenderBold: true" in stl,
                              "Secondary" if 'FontName: "Secondary"' in stl else "Default", "RenderUppercase: true" in stl)

    def heads_align(tag, aps, setv):
        """review fix: the permission / visitor / banned column heads start where their rows' names start (first glyph x)"""
        par, own, kids = {}, {}, {}
        for p, mk in aps:
            _t, ident = top_of(mk)
            if p is not None:
                kids.setdefault(p, []).append(mk)
            if ident:
                par[ident], own[ident] = p, mk

        def x_of(ident):
            x, cur = 0.0, ident
            while cur is not None and cur != "SkyyIsRoot":
                x += SUI._anchor_vals(own[cur]).get("Left") or 0
                p = par[cur]
                pm = own.get(p)
                if pm is not None:
                    x += pad_of(SUI, pm)["Left"]
                    if SUI._top_prop(SUI._own_props(pm), "LayoutMode") == "Left":
                        for mk in kids[p]:
                            if top_of(mk)[1] == cur:
                                break
                            x += SUI.outer_size(mk)[0]
                cur = p
            return x

        def glyph_x(ident):
            t = setv.get("#%s.Text" % ident, "")
            return x_of(ident) + lead_px(own[ident], t)

        def labels_in(row):
            return [top_of(mk)[1] for mk in kids.get(row, ()) if top_of(mk)[0] == "Label"]

        def head(row, start):
            for ident in labels_in(row):
                if setv.get("#%s.Text" % ident, "").startswith(start):
                    return ident
            return None

        pairs = []
        if "SkyyIsPHdr" in own:
            h = head("SkyyIsPHdr", "   What")
            names = [labels_in(r)[0] for r in sorted(i for i in own if re.fullmatch(r"SkyyIsPRow\d+", i))]
            pairs += [("What", h, n) for n in names]
        if "SkyyIsVHdr" in own:
            hv, hb = head("SkyyIsVHdr", "   On the island now"), head("SkyyIsVHdr", "Banned (")
            split = x_of(hb) if hb else 0          # the banned column starts where its head label starts
            for r in sorted(i for i in own if re.fullmatch(r"SkyyIsVRow\d+", i)):
                side = [i for i in labels_in(r) if x_of(i) < split]
                ban = [i for i in labels_in(r) if x_of(i) >= split]
                if side:                           # the visitor name: the first label of the row ("  " + name), then its role
                    check(setv.get("#%s.Text" % side[0], "").startswith("  "), "C. %s: %s: the visitor name label" % (tag, r))
                    pairs.append(("On the island now", hv, side[0]))
                if ban:
                    check(len(ban) == 1, "C. %s: %s: one banned name label" % (tag, r))
                    pairs.append(("Banned", hb, ban[0]))
        for what, h, n in pairs:
            if not check(h is not None and n is not None, "C. %s: the %s head / row name label was not found" % (tag, what)):
                continue
            d = glyph_x(n) - glyph_x(h)
            if check(abs(d) <= ALIGN_TOL, "C. %s: the %r head starts at %.1f px, the name %r at %.1f px (%+.1f)" % (
                    tag, setv.get("#%s.Text" % h, "")[:24], glyph_x(h), setv.get("#%s.Text" % n, "")[:24], glyph_x(n), d)):
                tally("C head alignment " + what)
                ALIGN_WORST[what] = max(ALIGN_WORST.get(what, 0.0), abs(d))

    ALIGN_WORST = {}

    def sanitized(mk):
        """the markup with 0.5.3's inline button labels that hold characters outside the kit's proven set ("Sure?", "Disband co-op
        (2)", "Friends (members + trusted)", "+") replaced by a proven sample - only for the syntax checks; the labels themselves
        are compared with 0.5.3's (identical inline texts)"""
        return TEXT_RE.sub(lambda m: m.group(0) if SUI.TEXT_OK.fullmatch(m.group(1)) else m.group(0).split('"', 1)[0] + '"x"', mk)

    def check_new(tag, cmds, evs):
        aps = appends_of(cmds)
        setv = dict((sel, str(set_value(data))) for typ, sel, text, data in cmds if "append" not in typ.lower())
        try:
            SUI.check_page([(p, sanitized(mk)) for p, mk in aps], prefix="SkyyIs")
            tally("C pages")
        except ValueError as e:
            check(False, "C. %s: check_page: %s" % (tag, e))
        for i, (p, mk) in enumerate(aps):
            if sanitized(mk) != mk:
                tally("C unproven inline labels")
            try:
                SUI.check_markup(sanitized(mk), prefix="SkyyIs", root=(p is None))
                tally("C markups")
            except ValueError as e:
                check(False, "C. %s: check_markup: %s: %s" % (tag, e, mk[:120]))
            check(i == 0 or p is not None, "C. %s: only the first append is a page root" % tag)
            for c in re.findall(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?(?:\([0-9.]+\))?", re.sub(r'"(?:[^"\\]|\\.)*"', '""', mk)):
                check(SUI.norm_color(c) in ALLOWED, "C. %s: colour %s is neither a kit colour nor a declared data colour" % (tag, c))
        try:
            SUI.assert_proven([mk for _p, mk in aps], what=tag)
            tally("C proven")
        except SUI.UnprovenError as e:
            check(False, "C. %s: %s" % (tag, e))
        check(aps and aps[0][0] is None and re.match(r"Group #SkyyIsF \{ Anchor: \(Width: 1240, Height: 980\); \}\Z", aps[0][1]),
              "C. %s: the page root is #SkyyIsF 1240 x 980 (Width / Height only)" % tag)
        layout(tag, aps, setv)
        heads_align(tag, aps, setv)

    # what each state must really draw on the 0.5.4 page (an id or a text; "!x" = must not) - proves the states cover the page
    COVER = {
        ("no island", 0): ["SkyyIsCreate", "You have no island yet", "!SkyyIsInvRow"],
        ("no island", 1): ["Create your island first (Overview tab), then invite"],
        ("no island + invite", 0): ["SkyyIsInvRow", "SkyyIsAcc", "SkyyIsDec", "Joining uses your current profile"],
        ("island gone", 0): ["not available right now"],
        ("file unreadable", 0): ["can't be read right now"],
        ("owner alone", 0): ["SkyyIsBox", "SkyyIsGo", "SkyyIsReset", "!SkyyIsDisb", "Commands"],
        ("owner alone", 1): ["SkyyIsNameBox", "SkyyIsInvBtn", "SkyyIsTrustBtn", "SkyyIsMr0", "Nobody yet. Trusted players may place"],
        ("owner alone", 2): ["SkyyIsPdef", "SkyyIsPc00v", "SkyyIsPc13a", "SkyyIsPRow13", "SkyyIsPList"],
        ("owner alone", 3): ["SkyyIsVm0", "SkyyIsVlm", "SkyyIsVn", "Nobody is on the island right now", "!SkyyIsVList"],
        ("owner alone", 4): ["SkyyIsIp", "SkyyIsIs", "!Only the owner and island admins can change these."],
        ("owner full", 0): ["SkyyIsDisb", "Disband co-op (4)", "Reset island: You can reset again", "!SkyyIsReset"],
        ("owner full", 1): ["SkyyIsMr4", "SkyyIsPr2", "SkyyIsDm1", "SkyyIsKk4", "SkyyIsTr1", "SkyyIsUt3", "SkyyIsTNav", "SkyyIsTp",
                            "Invited: Pam", "on another profile", "(profile 2)", "Page 2 / 2"],
        ("owner full", 3): ["SkyyIsVRow4", "SkyyIsVe3", "SkyyIsVt3", "SkyyIsVb4", "SkyyIsVu2", "SkyyIsBp", "SkyyIsBn", "Bans 2 / 2",
                            "Trusted", "Admin", "!SkyyIsVe0", "!SkyyIsVb1"],
        ("owner full page 1", 3): ["SkyyIsVRow7", "Averyverylongnam", "Bans 1 / 2"],
        ("owner 8 co-op slots", 1): ["and 3 more", "Co-op members  (8 / 8)"],
        ("owner no build grid", 1): ["The Permissions tab shows what Trusted players may do"],
        ("owner long denied list", 1): ["(the Permissions tab lists the rest)"],
        ("owner + invite it can't take", 0): ["SkyyIsInvRow", "SkyyIsDec", "!SkyyIsAcc", "you lead a co-op island"],
        ("admin", 0): ["SkyyIsLeave", "!SkyyIsOwnRow", "you are a co-op Admin here"],
        ("admin", 1): ["SkyyIsInvBtn", "Invite to co-op = they join the island", "SkyyIsUt0", "!SkyyIsKk1"],
        ("admin", 2): ["SkyyIsPc00v", "SkyyIsPdef"],
        ("admin, invites off", 1): ["!SkyyIsInvBtn", "SkyyIsTrustBtn"],
        ("admin, invites off", 2): ["can't drop items while on the wrong profile"],
        ("member", 0): ["SkyyIsLeave", "SkyyIsDec", "!SkyyIsAcc", "/island leave first"],
        ("member", 1): ["!SkyyIsNameBox", "!SkyyIsUt0"],
        ("member", 2): ["!SkyyIsPdef", "!SkyyIsPc00v", "Only the owner and island admins can change these.", "YES", "NO"],
        ("member", 3): ["!SkyyIsVm0", "Visits: "],
        ("member", 4): ["!SkyyIsIp", "Only the owner and island admins can change these."],
        ("owner arm disb", 0): ["Click again to DISBAND"],
        ("owner arm reset1", 0): ["Delete everything?"],
        ("owner arm reset2", 0): ["Really? Last click"],
        ("owner arm pdef", 2): ["Click again to reset"],
        ("owner arm kick", 1): ["Sure?"],
        ("owner arm ban", 3): ["Sure?"],
        ("member arm leave", 0): ["Click again to leave"]}

    # ---------------- C. differential builds
    MARKS = ["", "+Alex is now an island admin.", "-Nobody called Bob is online right now.",
             "=This DELETES every block and chest on your island, including your co-op members' things. Members, trusted players, "
             "bans and settings are kept. Click again within 20 s to continue.", "a line without a mark"]
    INFOS = set(MARKS)
    n_builds = 0
    for name in STATES:
        for tab in range(5):
            marks = MARKS if name in ("owner full",) and tab == 0 else MARKS[:2] if tab else MARKS[:3]
            for info in marks:
                res = {}
                for k in ("old", "new"):
                    setup(k, name)
                    res[k] = build(new_page(k, name, tab, info))
                    n_builds += 1
                tag = "%s / tab %d / %r" % (name, tab, info[:14])
                (co, eo), (cn, en) = res["old"], res["new"]
                check(eo == en, "C. %s: event bindings differ:\n   0.5.3 %s\n   0.5.4 %s" % (tag, eo[:6], en[:6]))
                tally("C bindings", len(en))
                so, sn = sets_of(co), sets_of(cn)
                check(so == sn, "C. %s: b.set lines differ:\n   only 0.5.3 %s\n   only 0.5.4 %s" % (
                    tag, sorted(set(so) - set(sn))[:4], sorted(set(sn) - set(so))[:4]))
                tally("C sets", len(sn))
                ao, an = appends_of(co), appends_of(cn)
                check(texts_of(ao) == texts_of(an), "C. %s: inline texts differ:\n   0.5.3 %s\n   0.5.4 %s" % (
                    tag, sorted(set(texts_of(ao)) - set(texts_of(an))), sorted(set(texts_of(an)) - set(texts_of(ao)))))
                miss = sorted(ids_of(ao) - ids_of(an))
                check(not miss, "C. %s: 0.5.3 element ids missing in 0.5.4: %s" % (tag, miss))
                tally("C old ids", len(ids_of(ao)))
                check_new(tag, cn, en)
                # a tab that throws shows the same fallback in both jars - it must never happen here
                check(not any("could not be drawn" in v for _s, v in sn), "C. %s: the tab failed to draw (fallback line)" % tag)
                have, txt = ids_of(an), " ".join(v for _s, v in sn) + " ".join(texts_of(an))
                for want in COVER.get((name, tab), ()):
                    ok = (want[1:] not in have and want[1:] not in txt) if want.startswith("!") else (want in have or want in txt)
                    if check(ok, "C. %s: coverage: %s" % (tag, want)):
                        tally("C coverage")
    COUNT["C builds"] = n_builds
    worst = sorted(BODY_USED.items(), key=lambda kv: -kv[1])[:3]
    check(COUNT.get("C coverage", 0) >= sum(len(v) for v in COVER.values()), "C. every coverage item was checked")
    print("C. %d page builds (%d states x 5 tabs x result marks x 2 jars; %d coverage checks): %d bindings, %d b.set lines, %d 0.5.3 ids compared; "
          "0.5.4: %d markups checked in %d pages (%d assert_proven), %d columns + %d rows laid out; #SkyyIsBody %d px, fullest %s"
          % (n_builds, len(STATES), COUNT.get("C coverage", 0), COUNT.get("C bindings", 0), COUNT.get("C sets", 0), COUNT.get("C old ids", 0),
             COUNT.get("C markups", 0), COUNT.get("C pages", 0), COUNT.get("C proven", 0), COUNT.get("C columns", 0),
             COUNT.get("C rows", 0), BODY_H, ", ".join("%s %d" % kv for kv in worst)))
    for what in ("What", "On the island now", "Banned"):
        check(COUNT.get("C head alignment " + what, 0) >= 10, "C. the %s head alignment was checked (%d rows)" % (
            what, COUNT.get("C head alignment " + what, 0)))
    print("   column heads over their rows (%s): %s" % ("client font tables" if SUI.font_table("Default") else "fallback widths", ", ".join(
        "%s %d rows (worst %.1f px)" % (w, COUNT.get("C head alignment " + w, 0), ALIGN_WORST.get(w, 0.0))
        for w in ("What", "On the island now", "Banned"))))

    # ---------------- D. clicks (handleDataEvent), identical on both jars
    def files_of(d):
        out = {}
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if not os.path.isfile(p) or f.endswith(".tmp"):
                continue
            props = {}
            for ln in open(p, encoding="latin-1").read().splitlines():
                if ln.startswith("#") or "=" not in ln:
                    continue
                kk, v = ln.split("=", 1)
                props[kk] = re.sub(r"\b\d{13}\b", "<t>", v)
            out[f] = props
        return out

    SCENARIOS = [
        ("owner full", [("tabmem", ""), ("name", "Bo b"), ("invite", ""), ("invite", "nobody"), ("invite", "Pam"), ("trust", "Finn"),
                        ("pr1", ""), ("pr3", ""), ("dm1", ""), ("kk2", ""), ("kk2", ""), ("ut0", ""), ("ut9", ""), ("tn", ""),
                        ("tp", ""), ("tp", ""), ("tabperm", ""), ("pc00v", ""), ("pc03m", ""), ("pc06a", ""), ("pc13t", ""),
                        ("pc99v", ""), ("pdef", ""), ("pdef", ""), ("tabvis", ""), ("vm2", ""), ("vm0", ""), ("vlm", ""), ("vlp", ""),
                        ("vlp", ""), ("vn", ""), ("ve3", ""), ("vt4", ""), ("vb3", ""), ("vb3", ""), ("vu0", ""), ("bn", ""),
                        ("bp", ""), ("vr", ""), ("tabisl", ""), ("ipvp", ""), ("ispawn", ""), ("ispawn", ""), ("tabov", ""),
                        ("reset", ""), ("disb", ""), ("disb", ""), ("refresh", ""), ("x9", ""), ("", ""), ("close", "")]),
        ("owner full page 1", [("tabov", ""), ("reset", ""), ("reset", ""), ("tabvis", ""), ("ve5", ""), ("vb6", ""), ("tabov", ""),
                               ("go", ""), ("create", "")]),
        ("member", [("tabov", ""), ("dec", ""), ("leave", ""), ("tabmem", ""), ("tabvis", ""), ("vm1", ""), ("tabov", ""),
                    ("leave", ""), ("leave", "")]),
        ("no island + invite", [("tabov", ""), ("acc", ""), ("tabmem", ""), ("tabov", ""), ("dec", "")]),
    ]
    n_clicks = 0
    for name, seq in SCENARIOS:
        trace = {}
        for k in ("old", "new"):
            Store, d = setup(k, name)
            pg = new_page(k, name)
            steps = []
            for a, t in seq:
                pg.handleDataEvent(None, None, json.dumps({"a": a, "@IsName": t}) if a else "{}")
                n_clicks += 1
                cmds, evs = build(pg)
                steps.append((a, t, norm(str(pg.info)), str(pg.confirm), str(pg.keepName), int(pg.tab), int(pg.trustPage), int(pg.banPage),
                              files_of(d), sorted(str(x) for x in Store.INVITES.keySet()), sets_of(cmds), evs))
                if k == "new":
                    INFOS.add(str(pg.info))
                    check_new("D. %s after %s %r" % (name, a, t), cmds, evs)
                check(not any("could not be drawn" in v for _s, v in sets_of(cmds)), "D. %s after %s: a tab failed to draw" % (name, a))
            trace[k] = steps
        for so, sn in zip(trace["old"], trace["new"]):
            FIELDS = ("click", "name", "result", "arm", "name box", "tab", "trust page", "ban page", "island files", "invites", "b.set lines",
                      "bindings")
            diff = [FIELDS[i] + (": only 0.5.3 %s / only 0.5.4 %s" % (sorted(set(so[i]) - set(sn[i]))[:3], sorted(set(sn[i]) - set(so[i]))[:3])
                                 if isinstance(so[i], list) else "") for i in range(len(so)) if so[i] != sn[i]]
            check(so == sn, "D. %s: after %s %r: 0.5.3 %s | 0.5.4 %s; differs: %s" % (name, so[0], so[1], so[2:8], sn[2:8], diff))
        tally("D results", len(set(s[2] for s in trace["new"])))
    COUNT["D clicks"] = n_clicks
    print("D. %d clicks (4 scenarios x 2 jars): identical result line, arm, name box, tab, pages, island files, invites and rebuilt page "
          "after every click (%d different result lines)" % (n_clicks, COUNT.get("D results", 0)))
    DONE = sorted(i for i in INFOS if i[:1] == "+")
    check(len(DONE) >= 10, "D. the clicks really changed things (%d '+' results)" % len(DONE))
    print("   e.g. " + " | ".join(i[:60] for i in DONE[:8]))

    # ---------------- E. text fit (the kit's text_width: the client's own font tables, or the fallback widths)
    n_fit, worst_fit = 0, []
    for (typ, ident, _head, w, h, style), texts in SEEN_TEXT.items():
        size = int(re.search(r"FontSize: (\d+)", style).group(1))
        bold = "RenderBold: true" in style.split("Hovered")[0]
        upper = "RenderUppercase: true" in style.split("Hovered")[0]
        wrap = "Wrap: true" in style.split("Hovered")[0]
        font = "Secondary" if 'FontName: "Secondary"' in style else "Default"
        for t in texts:
            n_fit += 1
            if typ == "TextButton":
                pad = int(re.search(r"Padding: \(Horizontal: (\d+)\)", _head).group(1)) if "Padding: (Horizontal:" in _head else 0
                room = (w or 0) - 2 * pad
                need = SUI.text_width(t, size, True, "Default", True)
                worst_fit.append((need - room, "button %s %r" % (ident, t)))
                check(need <= room + 0.5, "E. button #%s %r: %.0f px of label in %d px" % (ident, t, need, room))
            elif w is None:
                check(False, "E. label #%s %r: no box width" % (ident, t))
            elif wrap:
                lines = SUI.text_lines(t, w, size, bold, font, upper)
                need = lines * SUI.line_height(size, font, bold)
                worst_fit.append((need - (h or 0), "label %s (%d lines) %r" % (ident, lines, t[:50])))
                check(h is None or need <= h + 0.5, "E. label #%s %r: %d lines = %.1f px in %s px" % (ident, t[:60], lines, need, h))
            else:
                room = w - (2 * 19 if ident == "SkyyIsL0" else 0)
                need = SUI.text_width(t, size, bold, font, upper)
                worst_fit.append((need - room, "label %s %r" % (ident, t[:50])))
                check(need <= room + 0.5, "E. label #%s %r: %.0f px in %d px (%d px %s)" % (ident, t[:70], need, room, size,
                                                                                            "bold" if bold else "regular"))
    worst_fit.sort(reverse=True)
    COUNT["E texts"] = n_fit
    print("E. text fit: %d texts in %d boxes measured (%s); closest: %s" % (
        n_fit, len(SEEN_TEXT), "client font tables" if SUI.font_table("Default") else "fallback widths",
        "; ".join("%s (%+.0f px)" % (w_[1], w_[0]) for w_ in worst_fit[:3])))

    # ---------------- F. the page id
    pid, chk = K["IS_PAGE_ID"], K["IS_PAGE_CHECKED"]
    check("page %s)" % pid in LOG_NEW, "F. the jar's ready log line names the page the kit makes now (%s) - rebuild the jar" % pid)
    check(pid == chk, "F. the page the kit makes now (%s) is the checked page IS_PAGE_CHECKED (%s): if everything else passed, set "
                      "PAGE_CHECKED = %r in tools/islands_0_5_4_patch.py, regenerate and rebuild (without SKYY_UNCHECKED_PAGE)" % (pid, chk, pid))
    check(not os.path.basename(JAR).endswith("-UNCHECKED.jar"),
          "F. the jar under test is the harness-only -UNCHECKED build: once PAGE_CHECKED is set, rebuild without SKYY_UNCHECKED_PAGE "
          "and re-run on SkyyIslands-%s.jar" % VERSION)
    # the page gate (review fix): run the generated script's gate block on its own with a stub os
    import io, contextlib
    gsrc, full = gate_src()

    class StubOs(object):
        pass

    def gate(page_id, checked, env):
        so = StubOs()
        so.environ = env
        ns = {"os": so, "IS_PAGE_ID": page_id, "IS_PAGE_CHECKED": checked}
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(gsrc, SCRIPT + " (page gate)", "exec"), ns)
        except SystemExit:
            return "STOP"
        return ns.get("IS_JAR_TAG")

    for page_id, checked, env, want in (("a1", "a1", {}, ""), ("a1", "a1", {"SKYY_UNCHECKED_PAGE": "1"}, ""),
                                        ("a1", "b2", {}, "STOP"), ("a1", "b2", {"SKYY_UNCHECKED_PAGE": "0"}, "STOP"),
                                        ("a1", "b2", {"SKYY_UNCHECKED_PAGE": "yes"}, "STOP"),
                                        ("a1", "b2", {"SKYY_UNCHECKED_PAGE": "1"}, "-UNCHECKED")):
        got = gate(page_id, checked, env)
        if check(got == want, "F. page gate: page %s, checked %s, env %s -> %r, not %r" % (page_id, checked, env, got, want)):
            tally("F gate")
    jline = 'jar = os.path.join(HERE, "SkyyIslands-%s%s.jar" % (VERSION, IS_JAR_TAG))'
    check(full.count(jline) == 1 and full.index("# ---- end page gate") < full.index(jline) and full.count('"SkyyIslands-%s.jar"') == 0,
          "F. the build writes its jar only through the page gate's name (SkyyIslands-<v>.jar or SkyyIslands-<v>-UNCHECKED.jar)")
    check(K.get("IS_JAR_TAG") == ("" if pid == chk else "-UNCHECKED"), "F. the page code's gate picked %r" % K.get("IS_JAR_TAG"))
    COUNT["F"] = (pid, chk, SUI.kit_id(), SUI.kit_id() in LOG_NEW)
    print("F. page id %s, checked %s, kit %s%s; page gate: %d cases (a mismatch stops the build unless SKYY_UNCHECKED_PAGE=1 -> the "
          "-UNCHECKED jar name)" % (pid, chk, SUI.kit_id(), "" if SUI.kit_id() in LOG_NEW else " (the jar was built on another kit file)",
                                    COUNT.get("F gate", 0)))


def main():
    for j in (JAR, OLD):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first")
            return 1
    os.makedirs(SCRATCH, exist_ok=True)
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
    print("SkyyIslands %s page harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:40]:
        print("  FAIL", f[:400])
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
