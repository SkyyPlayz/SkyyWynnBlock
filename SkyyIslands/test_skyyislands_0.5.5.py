"""Bare-JVM harness for SkyyIslands 0.5.5 - DORMANT ISLANDS (the island of a deleted / archived SkyyProfiles profile), derived from the
0.5.4 page harness. Committed next to the build so the build docstring's CHECKED claims can be re-run instead of trusted; copy it to the
next version and keep it passing.

    python SkyyIslands/test_skyyislands_0.5.5.py [--jar <SkyyIslands-0.5.5.jar>] [--old <SkyyIslands-0.5.4.jar>] [--dir <scratch>]
                                                 [--live <a save's mods folder>] [--keep]

Build first (python tools/islands_0_5_5_patch.py, then python SkyyIslands/build_skyyislands_0.5.5.py). One JVM (the game's JRE,
-Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath; EACH SkyyIslands jar in its own class loader,
so 0.5.4 - the live SET pin - and 0.5.5 run side by side; online players / island worlds are an Unsafe-allocated Universe + Worlds +
PlayerRefs, no server, no client). It checks:
  A  every class of both jars loads, verifies and initialises (-Xverify:all)
  B  the 0.5.5 contract in bytes (0.5.4 vs 0.5.5): the same classes + JoinNote; every class byte-identical (IslandMenuPage included) or
     different only in version-string constants, except exactly IslandStore, IslandCmd, SweepTask, ArrivalTask, IslandCoop, PermFn,
     IslandReady, SeenTick and IslandMenuCmd, whose changed / new methods are exactly the planned ones (javassist, constant-pool indices
     resolved; IslandStore's 5 new fields); JoinNote.schedule waits 6 s; SkyyIslandsPlugin = 0.5.4's bytes once its ready-log constant is swapped back (setup() is
     untouched)
  C  the menu page, 0.5.4 vs 0.5.5, in 21 island states x 5 tabs x result marks (the 0.5.4 harness' states and checks, kept): the WHOLE
     command list and every event binding identical - without profile:fn:state and with one that answers every key as a live profile -
     plus the 0.5.4 layout / proven-markup / colour / coverage checks on the 0.5.5 output
  D  clicks through handleDataEvent, 4 scenarios x 2 jars, without and with that profile:fn:state: identical result line, arm, name box,
     tab, pages, island files, invites and rebuilt page after every click
  E  text fit (as 0.5.4)        F  the page id = 0.5.4's checked page (the page gate passes without a new page check)
  G  dormant islands on a SCRATCH COPY of the live Skyy_SkyyIslands + Skyy_SkyyProfiles data (found under the game's Saves, read only;
     the scenario's co-op lines are written into the copy) with a stubbed profile:fn:state that reads the copied players files the way
     SkyyProfiles 0.1.5's ProfDel.state does (p.<id>.deleted = pending, gone.<id> = archived). Chat lines are captured through a
     javassist PacketHandler fake, hub teleports through a Store fake (Teleport component), server admins through a PlayerRef fake;
     world-thread tasks are drained from the fake worlds' task queues:
     G0 open = 0.5.4; G1 owner pending: every entry path refused with the closed line and no teleport (/island = home = the
     SkyyProfiles switch, the menu's Go to island, /island visit, IslandCmd.go itself, a member without an island, the owner on another
     profile), accept + the menu's invite row + invite refused, 10 edits refused (trust, untrust, ban, unban, lock, visit mode, PvP,
     permission cell, reset permissions, limit), island:perm:fn, /island info, the menu's closed line, a server admin enters; arrival:
     member with an island -> their own island, member without one + trusted -> hub, admin stays; the sweep (+ the 4 s no-double-send)
     and SeenTick's world-thread dispatch; join line; one state call per sweep; the island folder untouched; G2 restore: open again,
     membership + files byte-identical; G2b leaving works while closed; G3 owner archived: released on both sides (file lines +
     MEMBER_OF, island:<uuid>), every other line / file kept, told once online, once at next join (notices.properties), a second scan
     does nothing; G4 a member's own profile pending (nothing) / archived (removed, owner told once - online and at next join);
     G5 no SkyyProfiles, SkyyProfiles 0.1.4 (no profile:fn:state), null and unknown answers: identical to 0.5.4 side by side (results,
     chat lines, teleports, island files, MEMBER_OF), no notices file; G6 start twice: no file written (bytes + times), a restart after
     a release releases nothing; unknown / null keys are open.
     Review fixes: G1 IslandCmd.go(own=true) to someone else's closed island refused; "profile #N" for a deleted profile, the name for
     a listed one; SeenTick's archive scan asks only after the island sweeps are queued; G3b / G4 an offline player's line saved before
     the island file write, dropped when that write fails, not saved twice by the 30 s retry (which really reads the island back),
     released once writable; G7 a corrupt notices.properties left untouched, read again after a minute, memory lines merged.
Not testable without the game: real teleports (the hub / own-island teleport is seen as a Teleport component / the "Teleporting..."
line), the real SkyyProfiles 0.1.5 next to it, chat on a real client.
Nothing is deployed and nothing outside the scratch folder is written (default tools/dev/scratch/islands055, deleted at the end unless
--keep; TEMP / TMP and java.io.tmpdir point into it). The live save is only read (copied). Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.5.5", "0.5.4"
PKG = "com.skyy.islands."
SCRIPT = os.path.join(HERE, "build_skyyislands_%s.py" % VERSION)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "islands055")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyIslands-%s.jar" % OLD_VERSION)))
KEEP = "--keep" in sys.argv
ONLY_G = "--only-g" in sys.argv     # development: A, B and G only
if "--hang" in sys.argv:              # development: dump the Python stack after N s
    import faulthandler
    faulthandler.dump_traceback_later(int(arg("--hang", "120")), exit=True)
VERBOSE = "-v" in sys.argv
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
    """Run the generated script's page code (the 0.5.5 look block and the tab builders) on the CURRENT kit with a stub M() - no
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
    print("A. loaded + verified + initialised: 0.5.4 %d, 0.5.5 %d classes (-Xverify:all)" % (COUNT.get("A classes old", 0),
                                                                                         COUNT.get("A classes new", 0)))
    if FAILS:
        return

    # ---------------- B. the 0.5.5 contract in bytes (class byte-compare 0.5.4 vs 0.5.5)
    old, new = CB["old"], CB["new"]
    page_c, plug_c = PKG + "IslandMenuPage", PKG + "SkyyIslandsPlugin"
    check(sorted(set(old) - set(new)) == [] and sorted(set(new) - set(old)) == [PKG + "JoinNote"],
          "B. the same classes + JoinNote: gone %s, new %s" % (sorted(set(old) - set(new)), sorted(set(new) - set(old))))
    # class -> (methods allowed to change, methods that must be new); every other class byte-identical or version-string only
    EXPECT = {
        "IslandStore": ({"<clinit>"}, {"profState", "closedState", "profWord", "closedText", "closedEdit", "closedNote", "noteFile", "notes0",
                                       "noteSave0", "noticeAdd0", "noticeTake0", "noticeAdd", "noticeTake", "tellOnce", "releaseCoop0",
                                       "releaseCoop", "releaseAll", "releaseMember", "archiveScan",
                                       "noticeDrop0", "noticeDrop", "relText"}),   # review fixes: + noticeDrop0 / noticeDrop / relText
        "IslandCmd": ({"go", "info", "visit"}, set()),
        "SweepTask": ({"run"}, {"sendOffClosed"}),
        "ArrivalTask": ({"run"}, set()),
        "IslandCoop": ({"acceptProblem", "invite", "trust", "untrustByKey", "ban", "unbanByKey", "editRefusal"}, set()),
        "PermFn": ({"apply"}, set()),
        "IslandReady": ({"accept"}, set()),
        "SeenTick": ({"run"}, set()),
        "IslandMenuCmd": ({"execute"}, set()),
    }
    vonly, changed_cls = [], []
    for n in sorted(old):
        if n == plug_c or n not in new:
            continue
        if old[n] == new[n]:
            tally("B identical")
            OKS[0] += 1
        elif version_only(old[n], new[n]):
            vonly.append(n.split(".")[-1])
            OKS[0] += 1
        else:
            changed_cls.append(n.split(".")[-1])
    COUNT["B version only"] = vonly
    check(sorted(changed_cls) == sorted(EXPECT), "B. the changed classes are exactly %s: %s" % (sorted(EXPECT), sorted(changed_cls)))
    check(old[page_c] == new[page_c], "B. IslandMenuPage is byte-identical to 0.5.4 (the page did not change)")
    uo, _ro = cp_split(old[plug_c])
    un, _rn = cp_split(new[plug_c])
    ready_old = [e for e in uo if b"] 0.5.4 ready" in e[2]]
    ready_new = [e for e in un if b"] 0.5.5 ready" in e[2]]
    LOG_NEW = ""
    if check(len(ready_old) == 1 and len(ready_new) == 1, "B. one ready-log constant in each SkyyIslandsPlugin"):
        s0, e0, t0 = ready_old[0]
        s1, e1, t1 = ready_new[0]
        swapped = new[plug_c][:s1] + old[plug_c][s0:e0] + new[plug_c][e1:]
        check(swapped == old[plug_c], "B. SkyyIslandsPlugin = 0.5.4's bytes once the ready-log constant is swapped back (setup unchanged)")
        LOG_NEW = t1.decode("utf8")
        check(LOG_NEW == t0.decode("utf8").replace("] 0.5.4 ready", "] 0.5.5 ready"), "B. the ready constant only changes its version: %r" % LOG_NEW[:120])
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
        try:
            ci = c.getClassInitializer()
            if ci is not None:
                out["<clinit>()V"] = code_of(ci)
        except Exception:
            pass
        return out

    BDET = []
    for cn in sorted(EXPECT):
        if cn not in changed_cls:
            continue
        co, cnw = ct(old[PKG + cn]), ct(new[PKG + cn])
        fo = set((str(f.getName()), str(f.getSignature())) for f in co.getDeclaredFields())
        fn_ = set((str(f.getName()), str(f.getSignature())) for f in cnw.getDeclaredFields())
        mo, mn = methods(co), methods(cnw)
        gone = sorted(k.split("(")[0] for k in mo if k not in mn)
        added = set(k.split("(")[0] for k in mn if k not in mo)
        changed = set(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k])
        same = [k for k in mo if k in mn and mo[k] == mn[k]]
        allow, want = EXPECT[cn]
        check(not gone, "B. %s: no method is gone: %s" % (cn, gone))
        check(changed <= allow, "B. %s: only %s changed: %s" % (cn, sorted(allow), sorted(changed)))
        check(added == want, "B. %s: the new methods are %s: %s" % (cn, sorted(want), sorted(added)))
        newf = sorted(n for n, _sg in fn_ - fo)
        check(not (fo - fn_) and newf == (["NOTES", "NOTES_AT", "NOTES_RO", "NOTE_LOCK", "REL_FAIL"] if cn == "IslandStore" else []),
              "B. %s fields: gone %s, new %s" % (cn, sorted(fo - fn_), newf))
        BDET.append("%s %d same / %s changed%s" % (cn, len(same), ",".join(sorted(changed)) or "-", (" / +" + str(len(added))) if added else ""))
        tally("B methods compared", len(mo))
    COUNT["B detail"] = BDET
    # review 7: JoinNote waits 6 s (after the login hub teleport at +1.5 s), not 3 s
    jn_s = [v for k_, v in methods(ct(new[PKG + "JoinNote"])).items() if k_.startswith("schedule(")]
    check(len(jn_s) == 1 and any(re.search(r"\b6000\b", ln) for ln in jn_s[0]) and not any(re.search(r"\b3000\b", ln) for ln in jn_s[0]),
          "B. JoinNote.schedule waits 6000 ms: %s" % [ln for ln in (jn_s[0] if jn_s else []) if "000" in ln])
    print("B. %d classes byte-identical (IslandMenuPage included), %d differ only by the version string (%s), SkyyIslandsPlugin = 0.5.4 "
          "but its ready constant, + JoinNote; changed exactly as planned (%d methods compared): %s"
          % (COUNT.get("B identical", 0), len(vonly), ", ".join(vonly), COUNT.get("B methods compared", 0), "; ".join(BDET)))

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

    @JImplements("java.util.function.Function")
    class StateOpen:
        """a SkyyProfiles 0.1.5 profile:fn:state that answers every key as a live profile (C / D: "state key present, nothing deleted")"""
        @JOverride
        def apply(self, k):
            k = str(k)
            if len(k) < 36:
                return None
            return "active" if k == PROFILE.get(k[:36], k[:36]) else "inactive"

    STATE_FN = [None]

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
        if STATE_FN[0] is not None:
            BR.put("profile:fn:state", STATE_FN[0])
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

    def cnorm(r):
        """a build's whole command list + bindings with the invite countdowns normalised (they tick between two builds)"""
        cm, ev = r
        return ([tuple(None if x is None else norm(x) for x in c) for c in cm], [tuple(norm(x) if isinstance(x, str) else x for x in e) for e in ev])

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
        """the 0.5.5 layout of one build: the frame body column filled exactly, #SkyyIsBody holds its tab, every Left row its
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
        """the markup with 0.5.4's inline button labels that hold characters outside the kit's proven set ("Sure?", "Disband co-op
        (2)", "Friends (members + trusted)", "+") replaced by a proven sample - only for the syntax checks; the labels themselves
        are compared with 0.5.4's (identical inline texts)"""
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

    # ---------------- G. dormant islands (0.5.5): scratch copies of the live Skyy_SkyyIslands + Skyy_SkyyProfiles data, a stubbed
    # profile:fn:state that reads the copied players files the way SkyyProfiles 0.1.5's ProfDel.state does
    import uuid as _uuid
    Ref_ = JClass("com.hypixel.hytale.component.Ref")
    Store_ = JClass("com.hypixel.hytale.component.Store")
    EntStore = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    EntMod = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    CompType = JClass("com.hypixel.hytale.component.ComponentType")
    CLDeque = JClass("java.util.concurrent.ConcurrentLinkedDeque")
    # the fakes, made with javassist into the scratch folder: chat capture (PacketHandler.writeNoCache), teleport capture
    # (Store.addComponent = what HubCmd.sendToHub does) and server admins (PlayerRef.hasPermission)
    fdir = os.path.join(SCRATCH, "fakes")
    os.makedirs(fdir, exist_ok=True)
    jcp = CP(True)
    CtF_, CtM_ = JClass("javassist.CtField"), JClass("javassist.CtNewMethod")

    def fake(name, sup, fields, meths):
        c = jcp.makeClass("skyyfake." + name, jcp.get(sup))
        # no constructor at all (instances come from Unsafe.allocateInstance; Store's constructor is not inheritable): add javassist's
        # default constructor and remove it again, so the class is written without one
        k0 = JClass("javassist.CtNewConstructor").defaultConstructor(c)
        c.addConstructor(k0)
        c.removeConstructor(k0)
        for f in fields:
            c.addField(CtF_.make(f, c))
        for m in meths:
            c.addMethod(CtM_.make(m, c))
        c.writeFile(fdir)

    fake("ChatCap", "com.hypixel.hytale.server.core.io.PacketHandler",
         ["public static java.util.concurrent.ConcurrentLinkedQueue Q = new java.util.concurrent.ConcurrentLinkedQueue();", "public java.util.UUID who;"],
         ["public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { Q.add(new Object[] { this.who, p }); }"])
    fake("FakeStore", "com.hypixel.hytale.component.Store",
         ["public static java.util.concurrent.ConcurrentLinkedQueue Q = new java.util.concurrent.ConcurrentLinkedQueue();"],
         ["public void addComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) { Q.add(new Object[] { r, c }); }"])
    fake("FakePR", "com.hypixel.hytale.server.core.universe.PlayerRef",
         ["public static java.util.Set ADMINS = java.util.Collections.synchronizedSet(new java.util.HashSet());"],
         ["public boolean hasPermission(String perm) { return ADMINS.contains(getUuid()); }"])
    FL = loader(fdir)
    ChatCap, FakeStore, FakePR = [Cls.forName("skyyfake." + n, True, FL) for n in ("ChatCap", "FakeStore", "FakePR")]
    CHATQ = ChatCap.getField("Q").get(None)
    TPQ = FakeStore.getField("Q").get(None)
    ADMINS = FakePR.getField("ADMINS").get(None)
    em = U.allocateInstance(EntMod.class_)
    setf(em, EntMod, "teleportComponentType", U.allocateInstance(CompType.class_))
    setf(None, EntMod, "instance", em)
    WBU = CHM()
    setf(uni, Universe, "worldsByUuid", WBU)
    setf(uni, Universe, "players", PLAYERS.values())      # Universe.getPlayers() (SeenTick, /island reload)
    FSTORE = U.allocateInstance(FakeStore)
    ESTORE = U.allocateInstance(EntStore.class_)
    setf(FSTORE, Store_, "externalData", ESTORE)

    # ---- the live data (read only) -> scratch
    saves = os.path.join(B.HYTALE, "UserData", "Saves")
    LIVE = arg("--live")
    if not LIVE:
        for w_ in (sorted(os.listdir(saves)) if os.path.isdir(saves) else []):
            if os.path.isdir(os.path.join(saves, w_, "mods", "Skyy_SkyyIslands", "islands")):
                LIVE = os.path.join(saves, w_, "mods")
                break
    if not check(bool(LIVE) and os.path.isdir(os.path.join(LIVE, "Skyy_SkyyIslands")), "G. live Skyy_SkyyIslands data found (%s)" % LIVE):
        return
    GROOT = os.path.join(SCRATCH, "G")

    def pread(path):
        d = {}
        if os.path.isfile(path):
            for ln in open(path, encoding="latin-1").read().splitlines():
                if ln.startswith("#") or "=" not in ln:
                    continue
                k_, v_ = ln.split("=", 1)
                d[k_.strip().replace("\\:", ":")] = v_.strip()
        return d

    def pwrite(path, d):
        with open(path, "w", encoding="latin-1") as fh:
            fh.write("#harness edit\n" + "".join("%s=%s\n" % kv for kv in d.items()))

    # the stub = SkyyProfiles 0.1.5 ProfDel.state / ProfStore.keyOf over the scratch players files (re-read on every call)
    def pfile(u):
        return pread(os.path.join(GROOT, "Skyy_SkyyProfiles", "players", u + ".properties"))

    def p_exists(d, i):
        return ("p.%s.name" % i) in d or ("p.%s.class" % i) in d

    def p_live(d, i):
        return p_exists(d, i) and ("p.%s.deleted" % i) not in d

    def key_id(d):
        if not d:
            return None
        a = d.get("active")
        if a is not None and p_live(d, a.strip()):
            return a.strip()
        for i in range(1, 257):
            if p_live(d, str(i)):
                return str(i)
        return None

    OVERRIDE = {}

    def state_of(k):
        if k in OVERRIDE:
            return OVERRIDE[k]
        if k is None or len(k) < 36:
            return None
        try:
            if str(_uuid.UUID(k[:36])) != k[:36]:
                return None
        except ValueError:
            return None
        rest = k[36:]
        if rest == "":
            i = "1"
        elif rest.startswith("-p") and rest[2:].isdigit() and str(int(rest[2:])) == rest[2:] and int(rest[2:]) >= 2:
            i = rest[2:]
        else:
            return None
        d = pfile(k[:36])
        if p_live(d, i):
            return "active" if i == key_id(d) else "inactive"
        if p_exists(d, i) and ("p.%s.deleted" % i) in d:
            return "pending"
        if ("gone.%s" % i) in d:
            return "archived"
        if i == "1" and key_id(d) is None:
            return "active"
        return None

    def key_of(u):
        i = key_id(pfile(u))
        return u if i in (None, "1") else u + "-p" + i

    STATE_CALLS = [0]
    STATE_KEYS = []          # every key asked (review 8: the failed release is really retried)
    STATE_HOOK = [None]      # called at every state call (review 3: what SeenTick had queued when the archive scan asked)

    @JImplements("java.util.function.Function")
    class GState:
        @JOverride
        def apply(self, k):
            STATE_CALLS[0] += 1
            STATE_KEYS.append(str(k))
            if STATE_HOOK[0] is not None:
                STATE_HOOK[0]()
            return state_of(k) if isinstance(k, str) else None

    @JImplements("java.util.function.Function")
    class GKey:
        @JOverride
        def apply(self, u):
            return key_of(str(u))

    def ikey(u, i):
        return u if str(i) == "1" else "%s-p%s" % (u, i)

    def island_file(k):
        return os.path.join(GROOT, "Skyy_SkyyIslands", "islands", k + ".properties")

    # who is who: OWNER = a players file with 2+ live profiles that have islands (the island of a NON-active one goes dormant), MEMBER =
    # another player with an island of their own (their co-op home becomes OWNER's island); Moe (a member without an island), Tess
    # (trusted), Ada (server admin) and Nia (2 profiles, her profile 2 in the co-op of OWNER's ACTIVE island) are harness players
    def pick():
        src_p = os.path.join(LIVE, "Skyy_SkyyProfiles", "players")
        owner = member = None
        for f in (sorted(os.listdir(src_p)) if os.path.isdir(src_p) else []):
            u = f[:-11]
            d = pread(os.path.join(src_p, f))
            ids = [str(i) for i in range(1, 257) if p_live(d, str(i)) and os.path.isfile(os.path.join(LIVE, "Skyy_SkyyIslands", "islands", ikey(u, i) + ".properties"))]
            act = key_id(d)
            if owner is None and len(ids) >= 2 and act in ids:
                owner = (u, d.get("username", "Owner"), [i for i in ids if i != act][0], act)
            elif member is None and act and os.path.isfile(os.path.join(LIVE, "Skyy_SkyyIslands", "islands", ikey(u, act) + ".properties")):
                member = (u, d.get("username", "Member"), act)
        return owner, member

    OWN_INFO, MEM_INFO = pick()
    SYNTH = OWN_INFO is None or MEM_INFO is None
    if SYNTH:      # the live data no longer has the shapes this test needs: the same shapes, written into the scratch copy
        OWN_INFO = ("d8ddde89-98b2-4739-983e-a39773d582b6", "SkyLordPlayz", "2", "3")
        MEM_INFO = ("b942734e-90b8-4e4b-986c-cd725d975b9e", "WesleyPlayz", "1")
    OWN_U, OWN_N, OWN_ID, OWN_ACT = OWN_INFO
    MEM_U, MEM_N, MEM_ID = MEM_INFO
    OWNER_KEY, OWNER_ACT_KEY, MEM_KEY = ikey(OWN_U, OWN_ID), ikey(OWN_U, OWN_ACT), ikey(MEM_U, MEM_ID)
    MOE_U, TESS_U, ADA_U, NIA_U = [str(uid(n)) for n in (701, 702, 703, 704)]
    NIA2 = NIA_U + "-p2"
    W_DORM = "skyy-island-" + OWNER_KEY
    GW, GP = {}, {}

    def gworld(name):
        w = U.allocateInstance(World.class_)
        setf(w, World, "alive", AtomicBoolean(True))
        setf(w, World, "acceptingTasks", AtomicBoolean(True))
        setf(w, World, "name", name)
        setf(w, World, "taskQueue", CLDeque())
        setf(w, World, "playerRefs", COWAL())
        # the harness thread is this world's thread (World.isInThread): getChunkIfLoaded & co. never wait for a world thread
        for f_ in JClass("com.hypixel.hytale.server.core.util.thread.TickingThread").class_.getDeclaredFields():
            if str(f_.getType().getName()) == "java.lang.Thread":
                f_.setAccessible(True)
                f_.set(w, JClass("java.lang.Thread").currentThread())
        wu = UUID.nameUUIDFromBytes(JArray(JClass("byte"))(name.encode("utf8")))
        WORLDS.put(name.lower(), w)
        WBU.put(wu, w)
        return w

    def wuuid(w):
        for e in WBU.entrySet():
            if System.identityHashCode(e.getValue()) == System.identityHashCode(w):
                return e.getKey()
        return None

    def gplayer(u, name):
        p = U.allocateInstance(FakePR)
        setf(p, PR, "uuid", UUID.fromString(u))
        setf(p, PR, "username", name)
        setf(p, PR, "holder", holder)
        ph = U.allocateInstance(ChatCap)
        ChatCap.getField("who").set(ph, UUID.fromString(u))
        setf(p, PR, "packetHandler", ph)
        r = U.allocateInstance(Ref_.class_)
        setf(r, Ref_, "index", Integer(1))
        setf(r, Ref_, "store", FSTORE)
        setf(p, PR, "entity", r)
        return p

    def online(p, on=True):
        if on:
            PLAYERS.put(p.getUuid(), p)
        else:
            PLAYERS.remove(p.getUuid())

    def place(p, w):
        for w2 in list(WBU.values()):
            lst = w2.getPlayerRefs()
            if lst.contains(p):
                lst.remove(p)
        w.getPlayerRefs().add(p)
        setf(p, PR, "worldUuid", wuuid(w))

    def fresh(owner_members=True, nia=False):
        """a new scratch copy of the live data + the scenario lines, and a clean in-memory state of both jars"""
        shutil.rmtree(GROOT, ignore_errors=True)
        os.makedirs(GROOT)
        for d_ in ("Skyy_SkyyIslands", "Skyy_SkyyProfiles"):
            if os.path.isdir(os.path.join(LIVE, d_)):
                shutil.copytree(os.path.join(LIVE, d_), os.path.join(GROOT, d_))
        isl = os.path.join(GROOT, "Skyy_SkyyIslands", "islands")
        pl_ = os.path.join(GROOT, "Skyy_SkyyProfiles", "players")
        os.makedirs(isl, exist_ok=True)
        os.makedirs(pl_, exist_ok=True)
        if SYNTH:
            pwrite(os.path.join(pl_, OWN_U + ".properties"), {"active": OWN_ACT, "p.1.name": "Strawberry", "p.1.class": "Archer", "p.2.name": "Zucchini",
                                                             "p.2.class": "Warrior", "p.3.name": "Banana", "p.3.class": "Priest", "username": OWN_N})
            pwrite(os.path.join(pl_, MEM_U + ".properties"), {"active": "1", "p.1.name": "Pear", "p.1.class": "Warrior", "username": MEM_N})
            for k_ in (OWNER_KEY, OWNER_ACT_KEY, MEM_KEY):
                pwrite(island_file(k_), {"v": "5", "world": "skyy-island-" + k_, "members": "", "trusted": "", "kit": "1",
                                         "ownerName": OWN_N if k_ != MEM_KEY else MEM_N})
        p = pread(island_file(OWNER_KEY))
        if owner_members:
            p.update({"members": ",".join([MEM_KEY, MOE_U]), "admins": MEM_KEY, "name." + MEM_KEY: MEM_N, "name." + MOE_U: "Moe",
                      "coopSince." + MEM_KEY: "1790000000000", "coopSince." + MOE_U: "1790000000001",
                      "trusted": ",".join([x for x in p.get("trusted", "").split(",") if x and x != MEM_KEY] + [TESS_U]), "name." + TESS_U: "Tess"})
        pwrite(island_file(OWNER_KEY), p)
        if nia:
            pwrite(os.path.join(pl_, NIA_U + ".properties"), {"active": "1", "p.1.name": "Fig", "p.1.class": "Mage", "p.2.name": "Kiwi",
                                                             "p.2.class": "Archer", "username": "Nia"})
            q = pread(island_file(OWNER_ACT_KEY))
            q.update({"members": NIA2, "name." + NIA2: "Nia", "coopSince." + NIA2: "1790000000002"})
            pwrite(island_file(OWNER_ACT_KEY), q)
        PLAYERS.clear()
        WORLDS.clear()
        WBU.clear()
        BR.clear()
        OVERRIDE.clear()
        CHATQ.clear()
        TPQ.clear()
        ADMINS.clear()
        ADMINS.add(UUID.fromString(ADA_U))
        for k in ("old", "new"):
            S_ = jc(k, "IslandStore")
            for m in ("SETTINGS", "MEMBER_OF", "INVITES", "CONFIRM", "EXPELLED", "PINGED", "EXPELLING", "RESETTING", "LOCKS", "BAD",
                      "KITDONE", "CREATING", "WORLD_OWNER", "SEEN", "EPOCH", "WARNED"):
                getattr(S_, m).clear()
            S_.ISLAND_WORLDS.clear()
            S_.DIR = Paths.get(isl)
            S_.HUB_FILE = Paths.get(os.path.join(GROOT, "Skyy_SkyyIslands", "hub.properties"))
            S_.HUB_WORLD = None
            S_.loadHub()
            if S_.HUB_WORLD is None:
                S_.HUB_WORLD, S_.HUB_POS, S_.HUB_ROT = "default", JArray(JClass("double"))([0.0, 100.0, 0.0]), JArray(JClass("float"))([0.0, 0.0, 0.0])
            if k == "new":
                S_.NOTES = None
                S_.NOTES_RO = False
                S_.NOTES_AT = 0
                S_.REL_FAIL.clear()
            Cf = jc(k, "IslandCfg")
            Cf.COOP_MAX, Cf.ADMINS_INVITE, Cf.STRICT_OTHER, Cf.TRUSTED_MAX, Cf.BANS_MAX = 5, True, True, 20, 100
            Cf.INVITE_SECONDS, Cf.EXPEL_SECONDS = 60, 60
        GW.clear()
        GW["hub"] = gworld(str(jc("new", "IslandStore").HUB_WORLD))
        setf(ESTORE, EntStore, "world", GW["hub"])
        GW["dorm"] = gworld(W_DORM)
        GW["memown"] = gworld("skyy-island-" + MEM_KEY)
        GW["ownact"] = gworld("skyy-island-" + OWNER_ACT_KEY)
        GP.clear()
        for nm, u, un_ in (("owner", OWN_U, OWN_N), ("member", MEM_U, MEM_N), ("moe", MOE_U, "Moe"), ("tess", TESS_U, "Tess"),
                           ("ada", ADA_U, "Ada"), ("nia", NIA_U, "Nia")):
            GP[nm] = gplayer(u, un_)
            place(GP[nm], GW["hub"])
        return isl

    def chat():
        out = {}
        while not CHATQ.isEmpty():
            o = CHATQ.poll()
            msg = o[1].message
            out.setdefault(str(o[0]), []).append("" if msg is None or msg.rawText is None else str(msg.rawText))
        return out

    def tps():
        out = []
        while not TPQ.isEmpty():
            o = TPQ.poll()
            who = [n for n, p in GP.items() if System.identityHashCode(p.getReference()) == System.identityHashCode(o[0])]
            wn = None
            try:
                wn = str(o[1].getWorld().getName())
            except Exception:
                pass
            out.append((who[0] if who else "?", wn))
        return out

    def snap(d):
        out = {}
        for root, _ds, fs in os.walk(d):
            for f in fs:
                p = os.path.join(root, f)
                out[os.path.relpath(p, d)] = (open(p, "rb").read(), os.path.getmtime(p))
        return out

    def props_of(b):
        d = {}
        for ln in b.decode("latin-1").splitlines():
            if ln.startswith("#") or "=" not in ln:
                continue
            k_, v_ = ln.split("=", 1)
            d[k_] = v_
        return d

    def isl_same(a, b):
        """two island-folder snapshots are the same - except that a member sent to their OWN island gets their ownerName stamped
        into their own island file (IslandCmd.go(own), 0.5.4's kick / disband destination behaviour)"""
        if sorted(a) != sorted(b):
            return False
        for f in a:
            if f == MEM_KEY + ".properties":
                pa, pb = props_of(a[f][0]), props_of(b[f][0])
                pa.pop("ownerName", None)
                pb.pop("ownerName", None)
                if pa != pb:
                    return False
            elif a[f] != b[f]:
                return False
        return True

    def drain(w):
        q = World.class_.getDeclaredField("taskQueue")
        q.setAccessible(True)
        dq = q.get(w)
        n = 0
        while not dq.isEmpty():
            dq.poll().run()
            n += 1
        return n

    def qlen(w):
        q = World.class_.getDeclaredField("taskQueue")
        q.setAccessible(True)
        return int(q.get(w).size())

    def arr(*a):
        x = JArray(JObject)(len(a))
        for i, v in enumerate(a):
            x[i] = v
        return x

    CLOSED_P = "'s island is closed - its profile was deleted. It comes back if they restore it within the undo window; otherwise you can make your own island."
    CLOSED_A = "'s island is closed - its profile was deleted for good."
    G_STEPS = []

    def gcheck(cond, what):
        G_STEPS.append(what)
        return check(cond, "G. " + what)

    def pedit(u, fn):
        f = os.path.join(GROOT, "Skyy_SkyyProfiles", "players", u + ".properties")
        pwrite(f, fn(pread(f)))

    def set_pending(u, i):
        def f(d):
            d["p.%s.deleted" % i] = str(NOW)
            d["p.%s.until" % i] = str(NOW + 6 * 3600000)
            d["p.%s.slots" % i] = "4"
            return d
        pedit(u, f)

    def set_restored(u, i):
        pedit(u, lambda d: dict((k_, v_) for k_, v_ in d.items() if k_ not in ("p.%s.deleted" % i, "p.%s.until" % i, "p.%s.slots" % i)))

    def set_archived(u, i):
        def f(d):
            d = dict((k_, v_) for k_, v_ in d.items() if not k_.startswith("p.%s." % i))
            d["gone.%s" % i] = str(NOW)
            return d
        pedit(u, f)

    def with_profiles(state=True, key=True):
        BR.remove("profile:fn:state")
        BR.remove("profile:fn:key")
        if key:
            BR.put("profile:fn:key", GKey())
        if state:
            BR.put("profile:fn:state", GState())

    NS, NC = jc("new", "IslandStore"), jc("new", "IslandCmd")
    NCo, NSw, NAr, NJn = jc("new", "IslandCoop"), jc("new", "SweepTask"), jc("new", "ArrivalTask"), jc("new", "JoinNote")

    def hubW():
        return GW["hub"]

    def U_(n):
        return GP[n].getUuid()

    def said(c, n, part):
        return any(part in t for t in c.get(str(U_(n)), []))

    def notices():
        return pread(os.path.join(GROOT, "Skyy_SkyyIslands", "notices.properties"))

    # ===== G0: the scenario on the live copy, nobody deleted: open (= 0.5.4)
    if VERBOSE:
        print('   G0 ...', flush=True)
    isl = fresh()
    with_profiles()
    for n in ("owner", "member", "tess", "ada"):
        online(GP[n])
    NS.loadIslandWorlds()
    BASE = snap(isl)
    gcheck(state_of(OWNER_KEY) == "inactive" and state_of(MEM_KEY) == "active", "G0 the stub reads the copied players files: owner island %s = %s, member %s = %s%s"
           % (OWNER_KEY[-8:], state_of(OWNER_KEY), MEM_KEY[-8:], state_of(MEM_KEY), " (synthetic shapes: the live data changed)" if SYNTH else ""))
    gcheck(str(NS.homeKey(U_("member"))) == OWNER_KEY and NS.closedState(OWNER_KEY) == 0, "G0 the member's home = the owner's island, open")
    NC.goHome(FSTORE, GP["member"].getReference(), GP["member"], hubW())
    c = chat()
    gcheck(said(c, "member", "Teleporting...") and not said(c, "member", "closed"), "G0 open island: the member's /island goes there (%s)" % c.get(str(U_("member"))))

    # ===== G1: the owner's profile is deleted (pending) = closed
    if VERBOSE:
        print('   G1 ...', flush=True)
    set_pending(OWN_U, OWN_ID)
    gcheck(state_of(OWNER_KEY) == "pending" and NS.closedState(OWNER_KEY) == 1, "G1 pending owner profile -> closedState 1")
    paths = [0]

    def refused(n, what, part=CLOSED_P, extra=None):
        c_ = chat()
        t_ = tps()
        ok = said(c_, n, part) and not said(c_, n, "Teleporting...") and not said(c_, n, "Loading the island") and not [x for x in t_ if x[0] == n]
        if extra:
            ok = ok and said(c_, n, extra)
        gcheck(ok, "G1 refused: %s (%s)" % (what, c_.get(str(U_(n)), [])[:2]))
        paths[0] += 1
        return c_

    NC.goHome(FSTORE, GP["member"].getReference(), GP["member"], hubW())
    refused("member", "/island = /island home|go = the SkyyProfiles switch teleport (member)", extra="/island leave ends your co-op membership now.")
    pg = jc("new", "IslandMenuPage")(GP["member"])
    pg.handleDataEvent(GP["member"].getReference(), FSTORE, '{"a":"go"}')
    refused("member", "the island menu's Go to island")
    NC.visit(FSTORE, GP["tess"].getReference(), GP["tess"], hubW(), GP["member"])
    c = refused("tess", "/island visit|warp <member> (a trusted player)")
    gcheck(not said(c, "tess", "Visiting"), "G1 no visiting line after the refusal")
    NC.go(FSTORE, GP["member"].getReference(), GP["member"], hubW(), OWNER_KEY, False)
    refused("member", "IslandCmd.go(owner's island) - the one teleport every entry path goes through")
    NC.go(FSTORE, GP["member"].getReference(), GP["member"], hubW(), OWNER_KEY, True)
    refused("member", "IslandCmd.go(owner's island, own=true) - review 4: the check keys on the player's own profile, not the caller's flag")
    online(GP["moe"])
    NC.goHome(FSTORE, GP["moe"].getReference(), GP["moe"], hubW())
    refused("moe", "/island (a member without an island of their own)")
    NC.visit(FSTORE, GP["owner"].getReference(), GP["owner"], hubW(), GP["member"])
    refused("owner", "the owner (on another profile) visiting it", part="This island belongs to your deleted profile #%s - " % OWN_ID)
    BR.put("profile:list:" + OWN_U, OWN_ACT + ":Kiwi:Mage")
    pw_ = (str(NS.profWord(OWNER_ACT_KEY)), str(NS.profWord(OWNER_KEY)))
    BR.remove("profile:list:" + OWN_U)
    gcheck(pw_ == ("profile Kiwi", "profile #" + OWN_ID), "G1 review 5: a listed profile reads by its name, a deleted one (not in profile:list) "
           "as profile #<the number /profiles list shows> %s" % (pw_,))
    _t, inv = invite(702, OWNER_KEY, 1, OWN_N, 50)
    NS.INVITES.put(UUID.fromString(TESS_U), inv)
    r_ = str(NCo.accept(GP["tess"]))
    gcheck(r_.startswith("-You can't accept: that island is closed - its owner's profile was deleted"), "G1 refused: /island accept of an invite to it (%s)" % r_)
    r_ = str(NCo.acceptProblem(GP["tess"]))
    gcheck(r_.startswith("that island is closed"), "G1 the menu's invite row shows why it can't be accepted (%s)" % r_)
    NS.INVITES.clear()
    r_ = str(NCo.invite(GP["member"], GP["tess"]))
    gcheck(r_.startswith("-") and "No co-op invites" in r_ and NS.INVITES.isEmpty(), "G1 refused: an island admin's co-op invite (%s)" % r_)
    online(GP["nia"])
    for what, call in (("trust", lambda: NCo.trust(GP["member"], GP["ada"])), ("untrust", lambda: NCo.untrust(GP["member"], "Tess")),
                       ("ban", lambda: NCo.ban(GP["member"], GP["nia"])), ("unban", lambda: NCo.unbanByKey(GP["member"], str(uid(999)))),
                       ("lock", lambda: NCo.lock(GP["member"], True)), ("visit mode", lambda: NCo.setMode(GP["member"], 2)),
                       ("PvP", lambda: NCo.togglePvp(GP["member"])), ("permission cell", lambda: NCo.clickPerm(GP["member"], 0, 0)),
                       ("reset permissions", lambda: NCo.resetPerms(GP["member"])), ("visitor limit", lambda: NCo.changeLimit(GP["member"], -1))):
        r_ = str(call())
        gcheck(r_.startswith("-") and "is closed" in r_, "G1 refused while closed: %s by the island admin (%s)" % (what, r_[:70]))
    online(GP["nia"], False)
    chat()
    pf = jc("new", "PermFn")()
    pv = lambda n, f: str(pf.apply(arr(U_(n), W_DORM, f))).lower()
    gcheck((pv("member", "enter"), pv("tess", "enter"), pv("ada", "enter"), pv("member", "settings"), pv("member", "build"))
           == ("false", "false", "true", "false", "true"), "G1 island:perm:fn %s enter = false (member, trusted), true (server admin); settings false; flags unchanged" % [pv(n_, f_) for n_, f_ in (("member", "enter"), ("tess", "enter"), ("ada", "enter"), ("member", "settings"), ("member", "build"))])
    NC.info(GP["member"], hubW())
    c = chat()
    gcheck(said(c, "member", CLOSED_P), "G1 /island info names the closed island")
    note = NS.closedNote(U_("member"))
    gcheck(note is not None and CLOSED_P in str(note) and NS.closedNote(U_("tess")) is None, "G1 /island menu opens with the closed line (IslandMenuCmd sets the page's result line)")
    NC.visit(FSTORE, GP["ada"].getReference(), GP["ada"], hubW(), GP["member"])
    c = chat()
    gcheck(said(c, "ada", "Teleporting...") and not said(c, "ada", "closed"), "G1 a server admin may still enter (/island visit goes there)")
    gcheck(snap(isl) == BASE, "G1 nothing in the island folder changed while closed")
    # sent away: arrival (every world switch: /tp, /tpa, warps, respawns) + the 5 s sweep
    for n in ("member", "moe", "tess", "ada"):
        place(GP[n], GW["dorm"])
    for n in ("member", "moe", "tess", "ada"):
        if VERBOSE:
            print("   arrival", n, flush=True)
        NAr(GP[n], W_DORM, 1).run()
    c, t = chat(), tps()
    hub_name = str(NS.HUB_WORLD)
    gcheck(said(c, "member", CLOSED_P) and said(c, "member", "Teleporting...") and not [x for x in t if x[0] == "member"],
           "G1 arrival: a member with an island of their own -> their own island (the kick destination) (%s)" % c.get(str(U_("member")), [])[:3])
    gcheck(said(c, "moe", CLOSED_P) and ("moe", hub_name) in t, "G1 arrival: a member without an island -> the hub (%s)" % t)
    gcheck(said(c, "tess", CLOSED_P) and ("tess", hub_name) in t, "G1 arrival: a trusted player -> the hub")
    gcheck(said(c, "ada", "Server admin:") and not [x for x in t if x[0] == "ada"], "G1 arrival: the server admin stays (inspection line)")
    NS.EXPELLING.clear()
    NSw(GW["dorm"], False).run()
    c, t = chat(), tps()
    gcheck(said(c, "member", "Teleporting...") and ("moe", hub_name) in t and ("tess", hub_name) in t and not [x for x in t if x[0] == "ada"]
           and not c.get(str(U_("ada"))), "G1 the 5 s sweep sends everyone but the server admin away (%s)" % t)
    NSw(GW["dorm"], False).run()
    c, t = chat(), tps()
    gcheck(not c and not t, "G1 a second sweep within 4 s sends nobody twice")
    NS.EXPELLING.clear()
    jc("new", "SeenTick")().run()
    n_q = drain(GW["dorm"])
    c, t = chat(), tps()
    gcheck(n_q >= 1 and ("moe", hub_name) in t, "G1 SeenTick queues the sweep on the island's world thread (%d task(s))" % n_q)
    for w_ in GW.values():
        drain(w_)
    chat()
    tps()
    NS.EXPELLING.clear()
    tick = jc("new", "SeenTick")()
    tick.runs = 2
    qseen = []
    STATE_HOOK[0] = lambda: qseen.append(qlen(GW["dorm"]))
    tick.run()
    STATE_HOOK[0] = None
    gcheck(len(qseen) >= 1 and qseen[0] >= 1, "G1 review 3: SeenTick's archive check (every 6th run) asks profile:fn:state only after this tick's "
           "island sweeps are queued (dorm queue at its first call: %s)" % qseen[:3])
    for w_ in GW.values():
        drain(w_)
    chat()
    tps()
    for n in ("member", "moe", "tess", "ada"):
        place(GP[n], hubW())
    NJn(GP["member"]).run()
    NJn(GP["tess"]).run()
    c = chat()
    gcheck(said(c, "member", CLOSED_P) and not c.get(str(U_("tess"))), "G1 join: the member hears the island is closed, the trusted player nothing")
    gcheck(isl_same(snap(isl), BASE) and snap(isl)[OWNER_KEY + ".properties"] == BASE[OWNER_KEY + ".properties"],
           "G1 still nothing in the island folder changed (the closed island's file byte-identical: membership, settings)")
    calls0 = STATE_CALLS[0]
    NSw(GW["ownact"], False).run()
    gcheck(STATE_CALLS[0] - calls0 == 1, "G1 the sweep asks profile:fn:state once per island world (%d)" % (STATE_CALLS[0] - calls0))

    # ===== G2: restored = open again, nothing changed
    if VERBOSE:
        print('   G2 ...', flush=True)
    set_restored(OWN_U, OWN_ID)
    gcheck(state_of(OWNER_KEY) == "inactive" and NS.closedState(OWNER_KEY) == 0, "G2 restored -> open")
    NC.goHome(FSTORE, GP["member"].getReference(), GP["member"], hubW())
    NC.visit(FSTORE, GP["tess"].getReference(), GP["tess"], hubW(), GP["member"])
    c = chat()
    gcheck(said(c, "member", "Teleporting...") and said(c, "tess", "Teleporting...") and not said(c, "member", "closed") and not said(c, "tess", "closed"),
           "G2 the member's /island and the trusted player's visit go there again")
    gcheck(pv("member", "enter") == "true", "G2 island:perm:fn enter = true again")
    for n in ("member", "moe", "tess"):
        place(GP[n], GW["dorm"])
    NS.EXPELLING.clear()
    NSw(GW["dorm"], False).run()
    c, t = chat(), tps()
    gcheck(not t and not any("closed" in x for v in c.values() for x in v), "G2 the sweep leaves them there")
    for n in ("member", "moe", "tess"):
        place(GP[n], hubW())
    gcheck(isl_same(snap(isl), BASE) and snap(isl)[OWNER_KEY + ".properties"] == BASE[OWNER_KEY + ".properties"] and str(NS.MEMBER_OF.get(MEM_KEY)) == OWNER_KEY and str(NS.MEMBER_OF.get(MOE_U)) == OWNER_KEY,
           "G2 membership and settings unchanged (island files byte-identical, MEMBER_OF kept)")

    # ===== G2b: leaving always works, even while closed
    if VERBOSE:
        print('   G2b ...', flush=True)
    set_pending(OWN_U, OWN_ID)
    r_ = str(NCo.leave(None, None, GP["moe"], None))
    gcheck(r_.startswith("+You left") and MOE_U not in pread(island_file(OWNER_KEY)).get("members", ""), "G2b a member can leave a closed island (%s)" % r_[:40])
    chat()

    # ===== G3: the owner's profile is archived = members released (both sides), told once (online now, next join)
    if VERBOSE:
        print('   G3 ...', flush=True)
    isl = fresh()
    with_profiles()
    for n in ("owner", "member", "tess"):
        online(GP[n])
    NS.loadIslandWorlds()
    PRE = snap(isl)
    pre_p = pread(island_file(OWNER_KEY))
    set_archived(OWN_U, OWN_ID)
    gcheck(state_of(OWNER_KEY) == "archived" and NS.closedState(OWNER_KEY) == 2, "G3 archived owner profile -> closedState 2")
    NC.goHome(FSTORE, GP["member"].getReference(), GP["member"], hubW())
    c = chat()
    gcheck(said(c, "member", CLOSED_A), "G3 still closed before the release (%s)" % c.get(str(U_("member")), [])[:1])
    n_rel = NS.archiveScan()
    c = chat()
    post_p = pread(island_file(OWNER_KEY))
    gcheck(n_rel == 2, "G3 the archive scan released 2 members (%d)" % n_rel)
    gcheck(post_p.get("members") == "" and post_p.get("admins") == "" and not [k_ for k_ in post_p if k_.startswith("coopSince.")],
           "G3 island file: members, admins, coopSince cleared")

    def keep(d):
        return dict((k_, v_) for k_, v_ in d.items() if k_ not in ("members", "admins") and not k_.startswith("coopSince."))

    gcheck(keep(pre_p) == keep(post_p), "G3 island file: every other line kept (%s)" % sorted(set(keep(pre_p).items()) ^ set(keep(post_p).items()))[:4])
    POST = snap(isl)
    gcheck(sorted(POST) == sorted(PRE) and all(POST[f] == PRE[f] for f in PRE if f != OWNER_KEY + ".properties"),
           "G3 every other island file (and the .v4bak copies) byte-identical, nothing deleted (%d files)" % len(PRE))
    gcheck(NS.MEMBER_OF.get(MEM_KEY) is None and NS.MEMBER_OF.get(MOE_U) is None and str(NS.homeKey(U_("member"))) == MEM_KEY,
           "G3 MEMBER_OF released too: the member's home is their own island again")
    gcheck(str(BR.get("island:" + MEM_U)) == "skyy-island-" + MEM_KEY, "G3 the online member's island:<uuid> = their own island again")
    gcheck(sum(1 for x in c.get(str(U_("member")), []) if "no longer in its co-op" in x) == 1, "G3 the online member is told once (%s)" % c.get(str(U_("member"))))
    nt = notices()
    gcheck(MOE_U in nt and "no longer in its co-op" in nt[MOE_U] and MEM_U not in nt, "G3 the offline member's line waits in notices.properties")
    NOTE_SNAP = snap(os.path.join(GROOT, "Skyy_SkyyIslands"))
    gcheck(NS.archiveScan() == 0 and not chat() and snap(os.path.join(GROOT, "Skyy_SkyyIslands")) == NOTE_SNAP, "G3 a second scan: nothing (no write, no line)")
    online(GP["moe"])
    NJn(GP["moe"]).run()
    c = chat()
    gcheck(sum(1 for x in c.get(str(U_("moe")), []) if "no longer in its co-op" in x) == 1, "G3 next join: the member hears it once")
    NJn(GP["moe"]).run()
    NJn(GP["member"]).run()
    gcheck(not chat() and MOE_U not in notices(), "G3 ... and never again")
    NC.go(FSTORE, GP["tess"].getReference(), GP["tess"], hubW(), OWNER_KEY, False)
    c = chat()
    gcheck(said(c, "tess", CLOSED_A), "G3 the archived island stays closed to visitors")
    NC.goHome(FSTORE, GP["member"].getReference(), GP["member"], hubW())
    c = chat()
    gcheck(said(c, "member", "Teleporting...") and not said(c, "member", "closed"), "G3 the released member's /island goes to their own island")

    # ===== G3b (review 8): an offline member's line is saved BEFORE the island file write; a failed write drops it again, the 30 s retry
    # (the island read back into the cache after write0 dropped it) saves nothing twice; once the file can be written both are released
    if VERBOSE:
        print('   G3b ...', flush=True)
    isl = fresh()
    with_profiles()
    for n in ("owner", "member", "tess"):
        online(GP[n])
    NS.loadIslandWorlds()
    set_archived(OWN_U, OWN_ID)
    nf = os.path.join(GROOT, "Skyy_SkyyIslands", "notices.properties")
    blk = island_file(OWNER_KEY) + ".tmp"
    os.makedirs(blk)
    pre_b = open(island_file(OWNER_KEY), "rb").read()
    r1 = NS.archiveScan()
    c = chat()
    gcheck(r1 == 0 and open(island_file(OWNER_KEY), "rb").read() == pre_b and str(NS.MEMBER_OF.get(MOE_U)) == OWNER_KEY
           and not said(c, "member", "no longer"), "G3b the island file can't be written: nobody released, nobody told (%d)" % r1)
    gcheck(os.path.exists(nf) and MOE_U not in notices(), "G3b ... the offline member's line was saved before the write (notices.properties "
           "written) and dropped again (%s)" % (sorted(notices()) if os.path.exists(nf) else "no notices file"))
    n1 = (open(nf, "rb").read(), os.path.getmtime(nf)) if os.path.exists(nf) else None
    del STATE_KEYS[:]
    r2 = NS.archiveScan()
    gcheck(r2 == 0 and OWNER_KEY in STATE_KEYS and n1 is not None and (open(nf, "rb").read(), os.path.getmtime(nf)) == n1 and not chat(),
           "G3b the 30 s retry asks again (the island read back after the failed write) and saves no notice twice")
    os.rmdir(blk)
    r3 = NS.archiveScan()
    c = chat()
    nt = notices()
    gcheck(r3 == 2 and pread(island_file(OWNER_KEY)).get("members") == "" and NS.MEMBER_OF.get(MOE_U) is None and NS.REL_FAIL.isEmpty(),
           "G3b the file writable again: both released (%d)" % r3)
    gcheck(sum(1 for x in c.get(str(U_("member")), []) if "no longer in its co-op" in x) == 1 and nt.get(MOE_U, "").count("no longer in its co-op") == 1,
           "G3b ... each told once (the online member now, the offline member's line waits once)")

    # ===== G4: a member's OWN profile archived = removed from the host island, the owner told once
    if VERBOSE:
        print('   G4 ...', flush=True)
    for owner_on in (True, False):
        isl = fresh(owner_members=False, nia=True)
        with_profiles()
        if owner_on:
            online(GP["owner"])
        online(GP["nia"])
        NS.loadIslandWorlds()
        PRE = snap(isl)
        set_pending(NIA_U, "2")
        tag = "owner " + ("online" if owner_on else "offline")
        gcheck(NS.archiveScan() == 0 and not chat() and snap(isl) == PRE and str(NS.MEMBER_OF.get(NIA2)) == OWNER_ACT_KEY,
               "G4 a member's pending profile changes nothing (%s)" % tag)
        set_archived(NIA_U, "2")
        if not owner_on:   # review 8: the offline owner's line is saved before the island file write and dropped again when it fails
            blk = island_file(OWNER_ACT_KEY) + ".tmp"
            os.makedirs(blk)
            nf = os.path.join(GROOT, "Skyy_SkyyIslands", "notices.properties")
            gcheck(NS.archiveScan() == 0 and not chat() and NIA2 in pread(island_file(OWNER_ACT_KEY)).get("members", "") and os.path.exists(nf)
                   and OWN_U not in notices(), "G4 the host island file can't be written: the member stays, the offline owner's pre-saved line is dropped again")
            os.rmdir(blk)
        n_rel = NS.archiveScan()
        c = chat()
        q = pread(island_file(OWNER_ACT_KEY))
        gcheck(n_rel == 1 and NIA2 not in q.get("members", "") and NS.MEMBER_OF.get(NIA2) is None and ("coopSince." + NIA2) not in q,
               "G4 the archived member left the host island (file + MEMBER_OF; %s)" % tag)
        if owner_on:
            gcheck(sum(1 for x in c.get(OWN_U, []) if "deleted the profile they had in your island co-op" in x) == 1, "G4 the online owner is told once (%s)" % c.get(OWN_U))
        else:
            gcheck(not c and OWN_U in notices(), "G4 the offline owner's line waits")
            online(GP["owner"])
            NJn(GP["owner"]).run()
            NJn(GP["owner"]).run()
            c = chat()
            gcheck(sum(1 for x in c.get(OWN_U, []) if "deleted the profile they had in your island co-op" in x) == 1, "G4 next join: the owner hears it once")
        gcheck(NS.archiveScan() == 0 and not chat(), "G4 a second scan: nothing (%s)" % tag)

    # ===== G5: no SkyyProfiles / SkyyProfiles 0.1.4 (no profile:fn:state) / null + unknown answers = 0.5.4, side by side
    if VERBOSE:
        print('   G5 ...', flush=True)
    def g5_run(k, mode):
        isl_ = fresh()
        set_pending(OWN_U, OWN_ID)
        if mode == "0.1.4":
            with_profiles(state=False)
        elif mode == "null":
            with_profiles()
            OVERRIDE[OWNER_KEY] = None
        elif mode == "unknown":
            with_profiles()
            OVERRIDE[OWNER_KEY] = "frozen"
        for n in ("owner", "member", "tess", "ada", "moe"):
            online(GP[n])
        S_, C_, Co_ = jc(k, "IslandStore"), jc(k, "IslandCmd"), jc(k, "IslandCoop")
        S_.loadIslandWorlds()
        out = []
        C_.goHome(FSTORE, GP["member"].getReference(), GP["member"], hubW())
        C_.visit(FSTORE, GP["tess"].getReference(), GP["tess"], hubW(), GP["member"])
        C_.info(GP["member"], hubW())
        _t, inv_ = invite(702, OWNER_KEY, 1, OWN_N, 50)
        S_.INVITES.put(UUID.fromString(TESS_U), inv_)
        out.append(str(Co_.acceptProblem(GP["tess"])))
        out.append(str(Co_.trust(GP["member"], GP["ada"])))
        out.append(str(Co_.setMode(GP["member"], 1)))
        out.append(str(jc(k, "PermFn")().apply(arr(U_("tess"), W_DORM, "enter"))))
        for n in ("member", "moe", "tess"):
            place(GP[n], GW["dorm"])
        for n in ("member", "moe", "tess"):
            jc(k, "ArrivalTask")(GP[n], W_DORM, 1).run()
        S_.EXPELLING.clear()
        jc(k, "SweepTask")(GW["dorm"], False).run()
        if k == "new":
            out.append(int(S_.archiveScan()))
            jc(k, "JoinNote")(GP["member"]).run()
        c_ = chat()
        files = dict((f, re.sub(rb"#[^\n]*\n", b"", v[0])) for f, v in snap(isl_).items())
        return out, sorted((u, tuple(v)) for u, v in c_.items()), tps(), files, sorted(str(x) for x in S_.MEMBER_OF.keySet())

    for mode in ("no SkyyProfiles", "0.1.4", "null", "unknown"):
        ro, rn = g5_run("old", mode), g5_run("new", mode)
        on_ = rn[0][:-1]
        same = ro[0] == on_ and ro[1:] == rn[1:]
        gcheck(same and rn[0][-1] == 0, "G5 %s: identical to 0.5.4 (results, chat lines, teleports, island files, MEMBER_OF; the archive scan does nothing)%s"
               % (mode, "" if same else ": 0.5.4 %s | 0.5.5 %s" % (str((ro[0], ro[1], ro[2]))[:400], str((on_, rn[1], rn[2]))[:400])))
        gcheck(not os.path.exists(os.path.join(GROOT, "Skyy_SkyyIslands", "notices.properties")), "G5 %s: no notices file" % mode)

    # ===== G6: start twice (no churn): the start-up scan + the archive check, twice
    if VERBOSE:
        print('   G6 ...', flush=True)
    isl = fresh()
    with_profiles()
    NS.loadIslandWorlds()
    S0 = snap(GROOT)
    NS.loadIslandWorlds()
    gcheck(snap(GROOT) == S0, "G6 an open world started twice: no file written (bytes + times)")
    set_archived(OWN_U, OWN_ID)
    S0 = snap(GROOT)
    NS.archiveScan()
    S1 = snap(GROOT)
    chat()
    for m in ("SETTINGS", "MEMBER_OF", "LOCKS", "BAD", "WORLD_OWNER", "EXPELLING"):
        getattr(NS, m).clear()
    NS.ISLAND_WORLDS.clear()
    NS.NOTES = None
    NS.loadIslandWorlds()
    gcheck(NS.archiveScan() == 0 and not chat() and snap(GROOT) == S1 and S1 != S0, "G6 after the release a restart releases nothing and writes nothing")
    gcheck(NS.closedState(OWNER_KEY + "x") == 0 and NS.closedState(None) == 0 and NS.closedState(OWN_U + "-p9") == 0, "G6 unknown / null keys are open")
    # ===== G7 (review 9): an unreadable notices.properties is left untouched, read again after a minute (not only at the next restart), and
    # the notices kept in memory meanwhile are merged in - nothing lost
    if VERBOSE:
        print('   G7 ...', flush=True)
    nf = os.path.join(GROOT, "Skyy_SkyyIslands", "notices.properties")
    bad = ("%s=waiting line\nbroken=\\u00zz\n" % MOE_U).encode("latin-1")
    open(nf, "wb").write(bad)
    NS.NOTES = None
    NS.NOTES_RO = False
    NS.NOTES_AT = 0
    NS.noticeAdd(U_("tess"), "memory line")
    gcheck(bool(NS.NOTES_RO) and open(nf, "rb").read() == bad, "G7 a corrupt notices.properties: left untouched, the new line kept in memory")
    open(nf, "wb").write(("%s=waiting line\n" % MOE_U).encode("latin-1"))
    gcheck(NS.noticeTake(U_("ada")) is None and bool(NS.NOTES_RO), "G7 ... not read again within the minute (no file read per notice)")
    NS.NOTES_AT = int(NS.NOTES_AT) - 61000
    t_ = NS.noticeTake(U_("ada"))
    nt = notices()
    gcheck(t_ is None and not bool(NS.NOTES_RO) and nt.get(MOE_U) == "waiting line" and nt.get(TESS_U) == "memory line",
           "G7 a minute later it reads again: the memory line merged in and saved, the waiting line kept (%s)" % nt)
    gcheck(str(NS.noticeTake(U_("tess"))) == "memory line" and str(NS.noticeTake(UUID.fromString(MOE_U))) == "waiting line" and not notices(),
           "G7 ... and each is delivered once")
    COUNT["G"] = (len(G_STEPS), paths[0], SYNTH, OWNER_KEY, MEM_KEY)
    print("G. dormant islands on a scratch copy of the live data (%s): %d checks; owner island ...%s (%s), member ...%s (%s); refused entry "
          "paths %d + accept / invite / 10 edits / perm:fn / info / menu line; arrival + sweep + SeenTick send-offs; restore; release (both "
          "sides, once, next join); archived member; 4 no-state modes = 0.5.4; start twice; review fixes: go(own) keyed on the profile, archive "
          "scan after the sweeps, profile #N, lines saved before the write (failed write + retry), notices re-read"
          % ("synthetic shapes" if SYNTH else LIVE, len(G_STEPS), OWNER_KEY[-12:], OWN_N, MEM_KEY[-12:], MEM_N, paths[0]))

    if ONLY_G:
        return

    # what each state must really draw on the 0.5.5 page (an id or a text; "!x" = must not) - proves the states cover the page
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
                # 0.5.5: the page is 0.5.4's - the whole command list and every binding are identical, with no profile:fn:state and with one
                # that answers every key as live (nothing deleted)
                check(cnorm(res["old"]) == cnorm(res["new"]), "C. %s: the 0.5.5 page differs from 0.5.4's (no profile:fn:state)" % tag)
                tally("C identical builds")
                STATE_FN[0] = StateOpen()
                try:
                    res2 = {}
                    for k in ("old", "new"):
                        setup(k, name)
                        res2[k] = build(new_page(k, name, tab, info))
                        n_builds += 1
                finally:
                    STATE_FN[0] = None
                check(cnorm(res2["old"]) == cnorm(res2["new"]) == cnorm(res["new"]), "C. %s: with a profile:fn:state that answers live the page differs" % tag)
                tally("C identical builds")
                (co, eo), (cn, en) = res["old"], res["new"]
                check(eo == en, "C. %s: event bindings differ:\n   0.5.4 %s\n   0.5.5 %s" % (tag, eo[:6], en[:6]))
                tally("C bindings", len(en))
                so, sn = sets_of(co), sets_of(cn)
                check(so == sn, "C. %s: b.set lines differ:\n   only 0.5.4 %s\n   only 0.5.5 %s" % (
                    tag, sorted(set(so) - set(sn))[:4], sorted(set(sn) - set(so))[:4]))
                tally("C sets", len(sn))
                ao, an = appends_of(co), appends_of(cn)
                check(texts_of(ao) == texts_of(an), "C. %s: inline texts differ:\n   0.5.4 %s\n   0.5.5 %s" % (
                    tag, sorted(set(texts_of(ao)) - set(texts_of(an))), sorted(set(texts_of(an)) - set(texts_of(ao)))))
                miss = sorted(ids_of(ao) - ids_of(an))
                check(not miss, "C. %s: 0.5.4 element ids missing in 0.5.5: %s" % (tag, miss))
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
    print("C. %d page builds identical to 0.5.4 (whole command list + bindings; without and with a live-answering profile:fn:state)" % COUNT.get("C identical builds", 0))
    print("C. %d page builds (%d states x 5 tabs x result marks x 2 jars x 2 modes; %d coverage checks): %d bindings, %d b.set lines, %d 0.5.4 ids compared; "
          "0.5.5: %d markups checked in %d pages (%d assert_proven), %d columns + %d rows laid out; #SkyyIsBody %d px, fullest %s"
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
    for mode, name, seq in [(None, n_, q_) for n_, q_ in SCENARIOS] + [("open", n_, q_) for n_, q_ in SCENARIOS]:
        trace = {}
        STATE_FN[0] = StateOpen() if mode else None
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
        STATE_FN[0] = None
        name = name + (" (profile:fn:state present)" if mode else "")
        for so, sn in zip(trace["old"], trace["new"]):
            FIELDS = ("click", "name", "result", "arm", "name box", "tab", "trust page", "ban page", "island files", "invites", "b.set lines",
                      "bindings")
            diff = [FIELDS[i] + (": only 0.5.4 %s / only 0.5.5 %s" % (sorted(set(so[i]) - set(sn[i]))[:3], sorted(set(sn[i]) - set(so[i]))[:3])
                                 if isinstance(so[i], list) else "") for i in range(len(so)) if so[i] != sn[i]]
            check(so == sn, "D. %s: after %s %r: 0.5.4 %s | 0.5.5 %s; differs: %s" % (name, so[0], so[1], so[2:8], sn[2:8], diff))
        tally("D results", len(set(s[2] for s in trace["new"])))
    COUNT["D clicks"] = n_clicks
    print("D. %d clicks (4 scenarios x 2 jars, without and with a profile:fn:state that answers live): identical result line, arm, name box, tab, pages, island files, invites and rebuilt page "
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
                      "PAGE_CHECKED = %r? No: 0.5.5 must keep 0.5.4's page (tools/islands_0_5_5_patch.py)" % (pid, chk, pid))
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
    print("SkyyIslands %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:40]:
        print("  FAIL", f[:400])
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
