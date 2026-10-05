"""Bare-JVM check for SkyyMenu 0.3.8 - data / text only: the Mods list = SET of 2026-10-05 evening + this round (ROUND_PINS: SkyyTrees
0.3.2, class trees ON by default) - Collections 0.2.6, Party 0.1.7, Bazaar 0.1.4, Gear 0.2.3, Skills 0.4.16, Essentials 0.1.8 (26 mods).
COPIED FORWARD from test_skyymenu_0.3.7.py with every check (B - J, P, X, K against 0.3.5, F + F2 with the 0.3.8 versions). NEW for 0.3.8:
  F3 the 0.3.8 texts: SkyyGear crafting Smithing XP (description + Server Setup line), SkyySkills 'own XP list per skill' (Server Setup
     line), SkyyParty TPA / Accept TPA buttons + SkyyEssentials 'also from the party page', SkyyBazaar progression prices, SkyyTrees
     Alchemy / Smithing + the class tree, /tree class for players, /tree probe for admins only
  K3 class compare 0.3.7 (the live pin, --prev) -> 0.3.8: only MenuData's static data initialiser; CfgRows / CfgFn / manifest.json the
     version string only; SkyyMenuPlugin the version + the config kit blob id in its ready line (tools/skyycfg.py changed since 0.3.7 -
     kit 1.1 still, its emitted classes byte-identical); every other entry byte-identical, none added or removed.
The 0.3.7 text below describes the carried-forward parts (read "0.3.7" as the new jar).

    python SkyyMenu/test_skyymenu_0.3.8.py [--jar <SkyyMenu-0.3.8.jar>] [--old <SkyyMenu-0.3.5.jar>] [--prev <SkyyMenu-0.3.7.jar>]
                                           [--dir <scratch folder>] [--keep]

=== 0.3.7 harness notes ===
Build the jar first (python tools/menu_0_3_8_patch.py, then python SkyyMenu/build_skyymenu_0.3.8.py). Carried forward from
test_skyymenu_0.3.6.py with every check: B - J on the 0.3.7 jar; P / X / K keep SkyyMenu 0.3.5 as the "old" jar (the stuck-page bug
reference: 0.3.5 must still reproduce it and 0.3.7 must still fix it; K = 0.3.5 -> 0.3.7, the same class changes 0.3.6 made); the "SET"
of F = tools/deploy_set.py SET with this round's ROUND_PINS versions. NEW for 0.3.7:
  F2 the 0.3.7 texts: the Accessories entry names the Lantern (description + Server Setup line), NO Mods / menu text says Night Vision;
     SkyyArmory 0.1 right after SkyyGear (no command, Server Setup Armory since 0.1, its file); SkyyUiProbe 0.4 /skyprobe map for
     admins only; SkyyBazaar's Server Setup page (Bazaar since 0.1.3); the gear.critFx switch known (Combat tab, after gear.notices)
  K2 class compare 0.3.6 (the live pin, --prev) -> 0.3.7: MenuData / SetReg / CfgRows differ only in their static data initialiser,
     SkyyMenuPlugin / CfgFn / manifest.json only by the version string, every other entry byte-identical, none added or removed.
The 0.3.6 text below describes the carried-forward parts (read "0.3.6" as the new jar).
One JVM: the game's own JRE, -Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar + the harness's stand-in classes on
the class path, SkyyMenu 0.3.6 and SkyyMenu 0.3.5 (the live SET pin) each in its OWN class loader (same package, separate statics; the
engine classes are shared, so both run on the same engine PageManager class).
  A  every class of both jars loads, verifies and initialises
  B  - J  as in 0.3.5 (permissions stand-in, the settings registry, the Settings page, the round's rows, the review fixes, seconds in
     Server Setup, the menu item per profile, TWO STARTS on scratch COPIES of the live Skyy_SkyyMenu data) - on the 0.3.6 jar
  F  the Mods list = tools/deploy_set.py SET when the harness runs (25 mods), the build's MODS_VERSIONS table = SET, the 0.3.5 texts
     still there, the 0.3.6 texts (the NEW SkyyWorldGen entry: /zone lines admins only, Server Setup World Gen, its file; Hud combat
     indicator, Gear damage / armor by level, Skills kill XP by mob level + early gathering, Accessories Night Vision, Cooking +32% per
     Grade, Mobs difficulty + health floor), no info line over 80 characters, no description over 390
  P  THE STUCK-PAGE FLOWS on the engine's PageManager (init(playerRef, windowManager) as the engine does) with a stand-in player
     (a Store answering getComponent from a map, recording packet handler, stand-in Universe / EntityModule, recording worlds - the
     SkyyBank 0.1.6 harness's stand-ins), a stand-in CommandManager (/island, /hub, /tpaccept resolve; handleCommand returns a future
     that keeps what the menu chains on it) and a model client that acknowledges what the real one does (inferred from the engine,
     the bank round's model): every CustomPage for the page it shows, a SetPage that closes the page it shows, nothing while it shows
     no page; it drops its page at a world change. A world change runs the engine's order: PlayerRef.removeFromStore (old ref invalid,
     holder kept) -> World.addPlayer = the new world id + AddPlayerToWorldEvent (0.3.6: PageGuard.accept, the registered listener) ->
     onSetupPlayerJoining = clearCustomPageAcknowledgements + the client's JoinWorld (drops its page) -> onFinishPlayerJoining =
     addToStore (a new ref in the new world's store). Clicks are the binding's own EventData from the last page packet the client
     applied (a grid click adds "SlotIndex"), through PageManager.handleEvent.
       P1 THE ISLAND TILE: menu (Teleport view) -> click My Island -> the real MenuPage.click / runCmd (grid emptied, /island run, its
          CloseTask chained on the command's future) -> world change -> the CloseTask the menu made runs (scheduler hop -> World.execute
          -> its world part, as the engine threads would): 0.3.5 = setPage(None) on the new world, 1 pending acknowledgement, the next
          page's clicks (a new SkyWynn Menu, a stand-in Bank page) are DROPPED; 0.3.6 = no packet, 0 pending, the next clicks work.
          The CloseTask's other timings (hop before the change, hop between worlds) are safe on both jars.
       P2 the keep-open command redraw (RefreshTask) after a world change: 0.3.5 stuck, 0.3.6 no packet + healthy
       P3 a bench (setPage Bench, what setPageWithWindows does first) after a world change with the menu left open: 0.3.5 stuck, 0.3.6 ok
       P4 the normal same-world paths still work on both jars: the Close button, a CloseTask after a command that stays in the world,
          a RefreshTask redraw, Esc (the "mesc" CloseTask does nothing after the Dismiss) - every packet acknowledged, page closed
       P5 no packet to a player with no page: CloseTask / RefreshTask after Esc, PageGuard / MenuWatch / StaleTask with no page
       P6 (0.3.6) PageGuard on every kind of page: the menu, Settings, Server Setup and a stand-in page with the engine's empty onDismiss
          are forgotten AT the event (no packet, counter untouched); a stand-in with its own onDismiss is left to StaleTask, which
          forgets it on the new world's thread with the NEW world's ref / store, only while it is still that page; a throwing
          onDismiss is logged and nothing breaks; plainDismiss of each page class; JOINS counts joins, MenuQuit drops them
       P7 (0.3.6) MenuWatch.watchTick: healthy = no packet; a stray page packet the client never acknowledges -> the dropped click is
          healed (one WARNING, reset, one answer) and the next click works; at most 3 answers per menu, later heals silent; a world
          change -> forget (no packet), also without the event; between worlds -> wait; Esc -> done
       P8 (0.3.6) the real timer chains with a scheduler built like HytaleServer.SCHEDULED_EXECUTOR handed over as setup() does:
          MenuWatch (hop -> World.execute -> check, follows the player into the new world, ends on Esc / STOP), StaleTask (polls while
          the player is between worlds, hands the forget to the new world), no scheduler = the menu still works, said once
  K  class compare 0.3.5 -> 0.3.6: added exactly PageGuard / StaleTask / MenuWatch; MenuData only <clinit>; MenuPage 0.3.5's fields +
     the new ones, changed only build / clearGrid / handleDataEvent, new who / changedWorld / watchFail / watchTick, every other method
     instruction-identical; CloseTask / RefreshTask only run; MenuQuit only accept; SkyyMenuPlugin only setup / shutdown; CfgRows /
     CfgFn / manifest only the version string; every other class + the item JSON + server.lang byte-identical
  X  engine-access audit with the JVM's own rules: every class / field / method / constructor reference of the 0.3.6 jar looked up with
     MethodHandles.Lookup in its referencing class (a protected engine member only from a subclass) - 0 refused; control: a class calling
     MenuPage.rebuild from outside is refused AND throws IllegalAccessError when run
Not testable without the game (UNVERIFIED in the build docstring): the client's own acknowledgement code (modelled), the real thread /
scheduler timing, the pages on a client. Not in this harness: the whole SET in one JVM (the cross-check's job).
Nothing is deployed. Default scratch folder tools/dev/scratch/menu036/harness (deleted at the end unless --keep); TEMP / TMP and
java.io.tmpdir point into it and the JVM's working directory is it. --dir must name a folder INSIDE tools/dev/scratch that is new,
empty or an earlier run's (it carries this harness's marker file): anything else is refused, so the end-of-run delete can only remove a
folder this harness made. Live data is only READ (copied). Exit code 1 on any failure.
"""
import os, sys, re, ast, shutil, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.3.8"
OLDVER = "0.3.5"             # the stuck-page bug reference for P / X / K
PREVVER = "0.3.7"            # the live SET pin: K3
PKG = "com.skyy.menu."
MARK = ".skyymenu-0.3.8-harness"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.realpath(os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "menu038", "harness"))))
OLDJAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyMenu-%s.jar" % OLDVER)))
PREVJAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyMenu-%s.jar" % PREVVER)))
LIVE_MODS = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Hytale", "UserData", "Saves", "HUD mod", "mods")   # READ ONLY
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
COUNT = {}


PART_OK = {}


def check(cond, what):
    part = what.split(".", 1)[0].strip()[:4]
    if cond:
        OKS[0] += 1
        PART_OK[part] = PART_OK.get(part, 0) + 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def tally(key, n=1):
    COUNT[key] = COUNT.get(key, 0) + n


def claim_scratch():
    """the scratch folder must sit inside tools/dev/scratch and be new, empty or this harness's own (marker file)"""
    if os.path.commonpath([SCRATCH, SCRATCH_ROOT]) != SCRATCH_ROOT or SCRATCH == SCRATCH_ROOT:
        raise SystemExit("--dir must be a folder inside %s (got %s)" % (SCRATCH_ROOT, SCRATCH))
    if os.path.isdir(SCRATCH) and os.listdir(SCRATCH) and not os.path.isfile(os.path.join(SCRATCH, MARK)):
        raise SystemExit("refusing %s: not empty and not made by this harness (no %s)" % (SCRATCH, MARK))
    if os.path.isdir(SCRATCH):            # an earlier run's folder (--keep): start empty, the parts expect fresh folders
        for n in os.listdir(SCRATCH):
            q = os.path.join(SCRATCH, n)
            if os.path.isdir(q):
                shutil.rmtree(q, ignore_errors=True)
            elif n != MARK:
                os.remove(q)
    os.makedirs(SCRATCH, exist_ok=True)
    open(os.path.join(SCRATCH, MARK), "w").write("SkyyMenu 0.3.8 harness scratch - safe to delete\n")


# ------------------------------------------------------------------------------------------------ the round's set (no JVM needed)
def live_set():
    tree = ast.parse(open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8").read())
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SET" for t in n.targets):
            return ast.literal_eval(n.value)
    return []


def round_set():
    """0.3.7: tools/deploy_set.py SET with this round's ROUND_PINS versions (the build's "this round's set"; mods the round adds
    appended) - the versions MODS names"""
    btree = ast.parse(open(os.path.join(HERE, "build_skyymenu_%s.py" % VERSION), encoding="utf-8").read())
    rp = {}
    for n in btree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ROUND_PINS" for t in n.targets):
            rp = ast.literal_eval(n.value)
    out = [(m, rp[m][1] if m in rp and rp[m][0] == v else v) for m, v in live_set()]
    out += [(m, to) for m, (frm, to) in sorted(rp.items()) if frm is None and m not in dict(out)]
    return out


# 0.3.4: the build's "seconds rows" rule read off the live build scripts (kit rows: 11 / 12-element tuples, helper calls like crow(...))
KIT_TYPES = {"bool", "int", "dec", "text", "choice", "items", "range", "table", "link", "action", "color"}


def ms_rows():
    rows = []
    for mod, ver in live_set():
        p = os.path.join(ROOT, mod, "build_%s_%s.py" % (mod.lower(), ver))
        if mod == "SkyyMenu" or not os.path.isfile(p):
            continue
        for node in ast.walk(ast.parse(open(p, encoding="utf-8", errors="ignore").read())):
            if isinstance(node, ast.Tuple) and len(node.elts) in (11, 12):
                a = [e.value if isinstance(e, ast.Constant) else None for e in node.elts]
                if isinstance(a[0], str) and a[3] in KIT_TYPES and a[8] == "ms":
                    rows.append((mod, a[0], a[3], a[4], a[5], a[6]))
            elif isinstance(node, ast.Call) and len(node.args) >= 4:
                a = [e.value if isinstance(e, ast.Constant) else None for e in node.args]
                if isinstance(a[0], str) and a[3] in KIT_TYPES and " " not in a[0] and "ms" in a[4:]:
                    nums = [x for x in a[4:] if isinstance(x, str) and re.match(r"^-?\d+$", x)]
                    rows.append((mod, a[0], a[3], None, nums[0] if nums else None, nums[1] if len(nums) > 1 else None))
    return rows


def round_scripts():
    """(mod, script path) of every mod in THIS round's set - the same rule as the build's ROUND_SET"""
    tree = ast.parse(open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8").read())
    live = None
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SET" for t in n.targets):
            live = ast.literal_eval(n.value)
    btree = ast.parse(open(os.path.join(HERE, "build_skyymenu_%s.py" % VERSION), encoding="utf-8").read())
    rp, rr = {}, {}
    for n in btree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ROUND_PINS" for t in n.targets):
            rp = ast.literal_eval(n.value)
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ROUND_RETIRED" for t in n.targets):
            rr = ast.literal_eval(n.value)
    out = []
    for mod, ver in live:
        if mod in rr or mod == "SkyyMenu":
            continue
        cands = [ver]
        if mod in rp and rp[mod][0] == ver:
            cands = [rp[mod][1], ver]          # the round's script, else the replaced version's (SkyyAuctions 0.1.2 while it is built)
        for v in cands:
            p = os.path.join(ROOT, mod, "build_%s_%s.py" % (mod.lower(), v))
            if os.path.isfile(p):
                out.append((mod, p))
                break
    for mod, (frm, to) in rp.items():
        if frm is None and mod not in dict(live):
            out.append((mod, os.path.join(ROOT, mod, "build_%s_%s.py" % (mod.lower(), to))))
    return out, rp, rr


def build_table():
    """0.3.5: the build script's ONE version table (MODS_VERSIONS in its MENU DATA section) - {} when it has none"""
    btree = ast.parse(open(os.path.join(HERE, "build_skyymenu_%s.py" % VERSION), encoding="utf-8").read())
    for n in btree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MODS_VERSIONS" for t in n.targets):
            return ast.literal_eval(n.value)
    return {}


REG = re.compile(r'regSetting\(\s*"([^"]+)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*(true|false|True|False)\s*,\s*"([^"]*)"\s*(?:,\s*"([^"]*)"\s*)?\)')
NODE_LIT = re.compile(r'(?:requirePermission\(\s*|hasPermission\([^;"]*?)"([^"]+)"\s*\)')


def real_nodes(scripts):
    """the permission nodes the round's mods use today: every regSetting node (7th registration element - none yet) and every literal
    requirePermission / hasPermission node of their newest scripts (what a mod would gate a switch with) -> {node: script names}"""
    out = {}
    for mod, p in scripts:
        t = open(p, encoding="utf-8", errors="ignore").read()
        found = [r[5] for r in REG.findall(t) if r[5]]          # registration nodes: all of them, whatever they look like
        found += [n for n in NODE_LIT.findall(t) if "." in n and not n.endswith(".") and not re.search(r"[{}@%\s]", n)]
        for n in found:
            out.setdefault(n, set()).add(os.path.basename(p))
    return out


def run():
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride, JByte
    import zipfile, json
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    hcls = os.path.join(SCRATCH, "hclasses")
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(hcls, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    os.chdir(SCRATCH)                     # any relative path the engine might touch lands in the scratch folder
    # 0.3.6: the two SkyyMenu jars each in their own class loader (same package); tools/javassist.jar for K / X and the stand-ins
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST, hcls], convertStrings=True)

    # ---------------- A. load + verify (both jars)
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")

    def mkloader(jar):
        urls = JArray(URL)(1)
        urls[0] = File(jar).toURI().toURL()
        return URLCL(urls, sysl)
    LDR = {"new": mkloader(JAR), "old": mkloader(OLDJAR)}
    loader = LDR["new"]
    CBY = {}
    for k, jp in (("new", JAR), ("old", OLDJAR)):
        z_ = zipfile.ZipFile(jp)
        CBY[k] = dict((n[:-6].replace("/", "."), z_.read(n)) for n in z_.namelist() if n.endswith(".class"))
        z_.close()
        for n in sorted(CBY[k]):
            try:
                Cls.forName(n, True, LDR[k])
                OKS[0] += 1
                tally("A " + k)
            except Exception as e:
                FAILS.append("load %s %s: %s" % (k, n, e))
                print("LOAD FAIL", k, n, e)
    print("A. loaded + verified + initialised (-Xverify:all): SkyyMenu %s %d classes, SkyyMenu %s %d classes" % (
        VERSION, COUNT.get("A new", 0), OLDVER, COUNT.get("A old", 0)))
    if FAILS:
        return

    def JN(name):
        return JClass(PKG + name, loader=LDR["new"])

    def JV(k, name):
        return JClass(PKG + name, loader=LDR[k])

    UUID, Paths, Boolean, Integer = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Boolean"), JClass("java.lang.Integer")
    HashSet, HashMap, ArrayList = JClass("java.util.HashSet"), JClass("java.util.HashMap"), JClass("java.util.ArrayList")
    MD, MU, SetReg, SetStore = JN("MenuData"), JN("MenuUtil"), JN("SetReg"), JN("SetStore")
    SetRegFn, SetSetFn, SettingsPage = JN("SetRegFn"), JN("SetSetFn"), JN("SettingsPage")
    PM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def jarr(*xs):
        a = JArray(JObject)(len(xs))
        for i, x in enumerate(xs):
            a[i] = x
        return a

    def jset(*xs):
        s = HashSet()
        for x in xs:
            s.add(x)
        return s

    # ---------------- B. a real PermissionsModule object behind PermissionsModule.get(), one fake provider
    A_ = UUID.fromString("00000000-0000-0000-0000-00000000000a")     # holds skyytest.staff
    B_ = UUID.fromString("00000000-0000-0000-0000-00000000000b")     # plain player (hytale:Adventurer, no nodes)
    C_ = UUID.fromString("00000000-0000-0000-0000-00000000000c")     # op: hytale:Admin = "*"
    D_ = UUID.fromString("00000000-0000-0000-0000-00000000000d")     # op with a personal deny -skyytest.staff
    USERS = {str(A_): (["skyytest.staff"], ["hytale:Adventurer"]), str(B_): ([], ["hytale:Adventurer"]),
             str(C_): ([], ["hytale:Admin"]), str(D_): (["-skyytest.staff"], ["hytale:Admin"])}
    GROUPS = {"hytale:Admin": ["*"], "hytale:Adventurer": []}

    @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
    class Prov:
        @JOverride
        def getName(self): return "gc-menu-test"
        @JOverride
        def getUserPermissions(self, u): return jset(*USERS.get(str(u), ([], []))[0])
        @JOverride
        def getGroupsForUser(self, u): return jset(*USERS.get(str(u), ([], []))[1])
        @JOverride
        def getGroupPermissions(self, g): return jset(*GROUPS.get(str(g), []))
        @JOverride
        def getEffectiveGroupPermissions(self, g): return jset(*GROUPS.get(str(g), []))
        @JOverride
        def getGroupParent(self, g): return None
        @JOverride
        def getAllRegisteredGroups(self): return jset(*GROUPS.keys())
        @JOverride
        def getUsersWithPermission(self, n): return HashSet()
        @JOverride
        def addUserPermissions(self, *a): return None
        @JOverride
        def removeUserPermissions(self, *a): return None
        @JOverride
        def addUserToGroup(self, *a): return None
        @JOverride
        def addGroupPermissions(self, *a): return None
        @JOverride
        def removeGroupPermissions(self, *a): return None
        @JOverride
        def removeUserFromGroup(self, *a): return None
        @JOverride
        def setUserGroup(self, *a): return None

    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def field(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    pm = U.allocateInstance(PM.class_)
    provs = ArrayList()
    provs.add(Prov())
    field(PM, "providers").set(pm, provs)
    field(PM, "virtualGroups").set(pm, HashMap())
    f_inst = field(PM, "instance")
    f_inst.set(None, pm)
    check(PM.get() is not None, "B. PermissionsModule.get() answers")
    check(bool(PM.get().hasPermission(A_, "skyytest.staff")) and not bool(PM.get().hasPermission(B_, "skyytest.staff"))
          and bool(PM.get().hasPermission(C_, "skyytest.staff")) and not bool(PM.get().hasPermission(D_, "skyytest.staff")),
          "B. engine hasPermission: holder yes, plain no, op (*) yes, op with a personal deny no")

    # ---------------- C. the registry
    work = os.path.join(SCRATCH, "world", "mods", "Skyy_SkyyMenu")
    os.makedirs(os.path.join(work, "settings"), exist_ok=True)
    SetStore.DIR = Paths.get(os.path.join(work, "settings"))
    br = MU.bridge()
    reg = SetRegFn()
    GEN = list(MD.SET_CAT_ID).index("general")
    COINS = list(MD.SET_CAT_ID).index("coins")
    T = Boolean.TRUE
    check(bool(reg.apply(jarr("TestMod", "test.open", "Open row", "general", T, "every player"))), "C. 6 elements register")
    check(bool(reg.apply(jarr("TestMod", "test.staff", "Staff row", "coins", T, "holders only", "skyytest.staff"))), "C. 7 elements (node) register")
    check(bool(reg.apply(jarr("TestMod", "test.nul", "Null node", "general", T, "h", None))), "C. 7th element null registers")
    check(bool(reg.apply(jarr("TestMod", "test.empty", "Empty node", "general", T, "h", "  "))), "C. 7th element blank registers")
    for bad in (Integer.valueOf(5), "bad node!", "skyy.*", "x" * 101, "a b"):
        check(not bool(reg.apply(jarr("TestMod", "test.bad", "Bad", "general", T, "h", bad))), "C. bad node %r refused" % (str(bad)[:20],))
    check(SetReg.DEFS.get("test.bad") is None, "C. a refused registration is not in DEFS")
    d_staff = SetReg.info("test.staff")
    check(d_staff is not None and len(d_staff) == 7 and str(d_staff[6]) == "skyytest.staff", "C. DEFS entry = Object[7] with the node")
    check(SetReg.info("test.open")[6] is None and SetReg.info("test.nul")[6] is None and SetReg.info("test.empty")[6] is None,
          "C. no node for 6 elements, null and blank")
    check(str(SetReg.permOf("test.staff")) == "skyytest.staff" and SetReg.permOf("test.open") is None and SetReg.permOf("no.such") is None,
          "C. permOf")
    br.put("settings:def:test.def7", jarr("DefMod", "test.def7", "Def7 row", "coins", T, "via settings:def", "skyytest.staff"))
    SetReg.drain()
    check(SetReg.info("test.def7") is not None and str(SetReg.permOf("test.def7")) == "skyytest.staff", "C. settings:def: fallback keeps the 7th element")
    check(bool(reg.apply(jarr("OtherMod", "test.staff", "Other", "coins", T, "h"))) and str(SetReg.permOf("test.staff")) == "skyytest.staff"
          and str(SetReg.info("test.staff")[0]) == "TestMod", "C. a different mod keeps the FIRST registration (its node too)")
    check(bool(reg.apply(jarr("TestMod", "test.staff", "Staff row", "coins", T, "holders only", "skyytest.staff"))), "C. re-register (same mod)")
    for u, sees, who in ((A_, True, "holder"), (B_, False, "plain"), (C_, True, "op"), (D_, False, "op with a deny")):
        v = [str(x) for x in SetReg.visible(COINS, u)]
        check(("test.staff" in v) == sees and ("test.def7" in v) == sees, "C. visible(coins) for the %s: %s" % (who, v))
        check(bool(SetReg.may(u, "test.staff")) == sees and bool(SetReg.may(u, "test.open")), "C. may() for the %s" % who)
        g = [str(x) for x in SetReg.visible(GEN, u)]
        check("test.open" in g and "test.nul" in g and "test.empty" in g, "C. rows without a node visible to the %s" % who)
    check(len(SetReg.keysOf(COINS)) == 2, "C. keysOf still lists every registered row")
    check(bool(SetReg.may(B_, "no.such.key")) and not bool(SetReg.allowed(None, "skyytest.staff")) and bool(SetReg.allowed(None, None)),
          "C. unknown key = no node; no player + a node = refused")
    sset = SetSetFn()
    check(not bool(sset.apply(jarr(B_, "test.staff", Boolean.FALSE))), "C. settings:fn:set refuses a key the player lacks")
    check(SetStore.own(B_, "test.staff") is None, "C. ... and stores nothing")
    check(bool(sset.apply(jarr(A_, "test.staff", Boolean.FALSE))) and bool(sset.apply(jarr(A_, "test.open", Boolean.FALSE))),
          "C. settings:fn:set works for the holder")
    _v = SetStore.get(A_, "test.staff")
    check(_v is not None and not bool(_v), "C. the holder's value is stored (%r)" % (_v,))
    check(bool(sset.apply(jarr(B_, "test.open", Boolean.FALSE))) and not bool(sset.apply(jarr(D_, "test.staff", Boolean.TRUE))),
          "C. settings:fn:set: the plain player sets a node-free key; the denied op is refused")
    # Reset all keeps the choices of keys the player may not change: E_ had test.staff=false saved while they held the node
    E_ = UUID.fromString("00000000-0000-0000-0000-00000000000e")
    open(os.path.join(work, "settings", str(E_) + ".properties"), "w").write("_v=1\ntest.staff=false\ntest.open=false\n")
    check(int(SetStore.resetAll(E_)) == 1, "C. resetAll (player without the node) saved")
    _v = SetStore.own(E_, "test.staff")
    check(_v is not None and not bool(_v) and SetStore.own(E_, "test.open") is None,
          "C. Reset all keeps the hidden row's choice, resets the visible one")
    check(int(SetStore.resetAll(A_)) == 1 and SetStore.own(A_, "test.staff") is None and SetStore.own(A_, "test.open") is None,
          "C. Reset all resets every row the holder can change")
    SetStore.saveNow(str(E_))
    txt = open(os.path.join(work, "settings", str(E_) + ".properties")).read()
    check("test.staff=false" in txt and "test.open" not in txt, "C. the reset file on disk")
    f_inst.set(None, None)
    check(not bool(SetReg.may(A_, "test.staff")) and bool(SetReg.may(A_, "test.open")) and len(SetReg.visible(COINS, C_)) == 0,
          "C. no PermissionsModule = node rows hidden for everyone (fail closed), node-free rows stay")
    f_inst.set(None, pm)

    # ---------------- D. the Settings page (engine UICommandBuilder / UIEventBuilder)
    def pref(u):
        p = U.allocateInstance(PR.class_)
        field(PR, "uuid").set(p, u)
        return p

    def build(page):
        b, ev = UCB(), UEB()
        page.build(None, b, ev, None)
        cmds = list(b.getCommands())
        out = []
        for c in cmds:
            out.append((str(c.selector) if c.selector is not None else "", str(c.text) if c.text is not None else "",
                        str(c.data) if c.data is not None else ""))
        return out

    def tabs_of(cmds):
        return [int(re.search(r"#SkyyStgTab(\d+) ", t).group(1)) for s, t, d in cmds if s.startswith("#SkyyStgTabs") and "#SkyyStgTab" in t
                and re.search(r"#SkyyStgTab(\d+) ", t)]

    def rows_of(cmds):
        return len([1 for s, t, d in cmds if s == "#SkyyStgRows" and t.startswith("Group #SkyyStgRow")])

    def head_of(cmds):
        h = [d for s, t, d in cmds if s == "#SkyyStgHead.Text"]
        return h[0] if h else ""

    def parent_of(cmds, i):
        p = [s for s, t, d in cmds if s.startswith("#SkyyStgTabs") and ("#SkyyStgTab%d " % i) in t]
        return p[0] if p else None

    pgB = SettingsPage(pref(B_), -1)
    cB = build(pgB)
    check(tabs_of(cB) == [GEN], "D. plain player: only the General tab is drawn (Coins holds only node rows): %s" % tabs_of(cB))
    check(int(pgB.cat) == GEN and parent_of(cB, GEN) == "#SkyyStgTabs0", "D. the page opens on the first visible tab, buttons close up")
    check("3 settings" in head_of(cB) and rows_of(cB) == 3, "D. header + rows count visible rows only: %r" % head_of(cB))
    pgB.cat = COINS
    cB2 = build(pgB)
    check(int(pgB.cat) == GEN and tabs_of(cB2) == [GEN], "D. a tab the player cannot see moves the page to the first visible tab")
    pgA = SettingsPage(pref(A_), COINS)
    cA = build(pgA)
    check(tabs_of(cA) == [COINS, GEN] and int(pgA.cat) == COINS, "D. holder: Coins + General drawn, Coins open: %s" % tabs_of(cA))
    check("2 settings" in head_of(cA) and rows_of(cA) == 2 and parent_of(cA, GEN) == "#SkyyStgTabs0", "D. holder's Coins rows")
    staff_names = [d for s, t, d in cA if s.startswith("#SkyyStgName")]
    check(any("Staff row" in d for d in staff_names) and not any("Staff row" in d for s, t, d in cB), "D. the node row is drawn for the holder only")
    # a stale click: the page still has the node row, the player lost the node meanwhile
    pgA.rowKeys = JArray(JClass("java.lang.String"))(list(pgA.rowKeys))
    idx = [str(k) for k in pgA.rowKeys].index("test.staff")
    before = SetStore.own(B_, "test.staff")
    pgB.rowKeys[0] = "test.staff"
    pgB.handleDataEvent(None, None, '{"a":"son%d"}' % 0)
    check(str(pgB.status) == str(MD.SET_TXT_GONE) and SetStore.own(B_, "test.staff") == before,
          "D. stale click on a row the player lost: refused, nothing stored (%r)" % str(pgB.status))
    check(idx >= 0, "D. the holder's page kept the node row key")

    # ---------------- G. review fixes: a refused key fails closed, plain nodes only, the stricter node wins
    sget = JN("SetGetFn")()
    FA = Boolean.FALSE
    F_ = UUID.fromString("00000000-0000-0000-0000-00000000000f")     # plain player with choices stored for the keys refused below
    open(os.path.join(work, "settings", str(F_) + ".properties"), "w").write("_v=1\ntest.inv=true\ntest.weak=false\n")
    # an invalid node (skyy.*) -> the key is refused: set refused, get = the registered default, row hidden - for everyone
    check(not bool(reg.apply(jarr("TestMod", "test.inv", "Invalid node", "coins", FA, "h", "skyy.*"))), "G. node skyy.* refused")
    check(SetReg.DEFS.get("test.inv") is None and SetReg.REFUSED.get("test.inv") is not None, "G. the key is REFUSED, not in DEFS")
    for u, who in ((A_, "holder"), (B_, "plain player"), (C_, "op"), (F_, "player with a stored choice")):
        check(not bool(SetReg.may(u, "test.inv")), "G. refused key: may() false for the %s" % who)
        check("test.inv" not in [str(x) for x in SetReg.visible(COINS, u)], "G. refused key: row hidden for the %s" % who)
        check(not bool(sset.apply(jarr(u, "test.inv", T))), "G. refused key: settings:fn:set refused for the %s" % who)
    check(SetStore.own(A_, "test.inv") is None and SetStore.own(C_, "test.inv") is None, "G. refused key: nothing stored")
    _g = sget.apply(jarr(F_, "test.inv"))
    check(_g is not None and not bool(_g), "G. refused key: settings:fn:get = the registered default FALSE, not the stored TRUE (%r)" % (_g,))
    _g = sget.apply(jarr(B_, "test.inv"))
    check(_g is not None and not bool(_g), "G. refused key: settings:fn:get = the registered default for a player without a choice (%r)" % (_g,))
    pgG = SettingsPage(pref(C_), COINS)
    cG = build(pgG)
    check(not any("Invalid node" in d for s, t, d in cG) and "2 settings" in head_of(cG), "G. refused key: no row on the op's page (%r)" % head_of(cG))
    # the same mod: a weaker registration first, then an invalid node -> the earlier registration goes too
    check(bool(reg.apply(jarr("TestMod", "test.weak", "Weak row", "general", T, "every player"))) and
          "test.weak" in [str(x) for x in SetReg.visible(GEN, B_)], "G. test.weak registers for every player")
    check(not bool(reg.apply(jarr("TestMod", "test.weak", "Weak row", "general", T, "h", "a..b"))), "G. the same mod again with node a..b: refused")
    check(SetReg.DEFS.get("test.weak") is None and "test.weak" not in [str(x) for x in SetReg.visible(GEN, B_)]
          and not bool(SetReg.may(B_, "test.weak")) and not bool(sset.apply(jarr(B_, "test.weak", FA))),
          "G. ... the earlier weaker registration is gone: hidden, may() false, set refused")
    _g = sget.apply(jarr(F_, "test.weak"))
    check(_g is not None and bool(_g), "G. ... settings:fn:get = the registered default TRUE, not the stored FALSE (%r)" % (_g,))
    check(not bool(reg.apply(jarr("TestMod", "test.weak", "Weak row", "general", T, "every player")))
          and not bool(reg.apply(jarr("OtherMod", "test.weak", "W", "general", T, "h", "skyytest.staff"))) and SetReg.DEFS.get("test.weak") is None,
          "G. a refused key stays refused (a later valid registration of any mod)")
    # an undrained settings:def: with a bad node fails closed on the very first get / may / set; the drain never brings it back
    br.put("settings:def:test.lazy", jarr("LazyMod", "test.lazy", "Lazy", "general", FA, "h", "-skyytest.staff"))
    _g = sget.apply(jarr(B_, "test.lazy"))
    check(_g is not None and not bool(_g) and not bool(SetReg.may(D_, "test.lazy")) and not bool(sset.apply(jarr(B_, "test.lazy", T))),
          "G. settings:def: with a bad node, never drained: get = default, may() false, set refused (%r)" % (_g,))
    SetReg.drain()
    check(SetReg.DEFS.get("test.lazy") is None and SetReg.REFUSED.get("test.lazy") is not None, "G. ... the drain keeps it refused")
    # plain nodes only
    check(not bool(reg.apply(jarr("TestMod", "test.deny", "Deny", "coins", T, "h", "-skyytest.staff"))) and not bool(SetReg.may(D_, "test.deny"))
          and not bool(SetReg.may(A_, "test.deny")), "G. -skyytest.staff (the engine's deny syntax) refuses the key")
    for bad in ("-skyytest.staff", "-", ":", ".", "..", "a..b", "skyy.", "skyy:", "skyy-", "skyy.admin.", "skyy.admin-", "skyy.admin:",
                ".skyy.admin", "skyy.*", "*", "skyy.ad*min", "skyy:admin", "skyy-x.admin", "Skyy.admin", "skyy_x.admin", "skyy",
                "a b.c", "1skyy.admin", "x" * 98 + ".ab"):
        check(not bool(SetReg.validPerm(bad)), "G. validPerm refuses %r" % bad[:24])
    for good in ("skyytest.staff", "a.b", "skyy0.admin2", "skyy.2fa", "skyyranks.rank.vip", "x" * 97 + ".ab"):
        check(bool(SetReg.validPerm(good)), "G. validPerm accepts %r" % good[:24])
    scripts_g, _rp, _rr = round_scripts()
    scripts_g = scripts_g + [(m, p) for m, p in (("SkyyGear", os.path.join(ROOT, "SkyyGear", "build_skyygear_0.1.py")),)
                             if (m, p) not in scripts_g and os.path.isfile(p)]
    real = real_nodes(scripts_g)
    print("G. %d permission nodes the round's mods use today (registration nodes: %d)" %
          (len(real), len([1 for m, p in scripts_g for r in REG.findall(open(p, encoding="utf-8", errors="ignore").read()) if r[5]])))
    check(len(real) >= 15, "G. real nodes found in the round's scripts: %d" % len(real))
    for n in sorted(real):
        check(bool(SetReg.validPerm(n)), "G. validPerm accepts the real node %s (%s)" % (n, ", ".join(sorted(real[n]))))
    # two mods on one key: the stricter node wins
    check(bool(reg.apply(jarr("ModA", "test.conf", "Conflict row", "general", T, "first, no node"))), "G. conflict: ModA registers without a node")
    check(bool(reg.apply(jarr("ModB", "test.conf", "Other text", "general", T, "second, a node", "skyytest.staff"))),
          "G. conflict: ModB registers the same key with a node")
    _d = SetReg.info("test.conf")
    check(str(SetReg.permOf("test.conf")) == "skyytest.staff" and str(_d[0]) == "ModA" and str(_d[2]) == "Conflict row" and len(_d) == 7,
          "G. null then node: the key is gated by the node, ModA's texts kept")
    check(not bool(SetReg.may(B_, "test.conf")) and bool(SetReg.may(A_, "test.conf")) and bool(SetReg.may(C_, "test.conf"))
          and "test.conf" not in [str(x) for x in SetReg.visible(GEN, B_)] and "test.conf" in [str(x) for x in SetReg.visible(GEN, A_)],
          "G. ... hidden for the plain player, shown to the holder and the op")
    check(not bool(sset.apply(jarr(B_, "test.conf", FA))) and bool(sset.apply(jarr(A_, "test.conf", FA))), "G. ... set: plain refused, holder ok")
    check(bool(reg.apply(jarr("ModA", "test.conf", "Conflict row", "general", T, "first, no node"))) and str(SetReg.permOf("test.conf")) == "skyytest.staff",
          "G. ModA registering again (the settings:def: drain) keeps ModB's node")
    check(bool(reg.apply(jarr("ModA", "test.conf2", "Two nodes", "general", T, "h", "skyytest.staff"))), "G. test.conf2: ModA with a node")
    check(not bool(reg.apply(jarr("ModB", "test.conf2", "Two nodes", "general", T, "h", "skyytest.other"))) and SetReg.DEFS.get("test.conf2") is None
          and not bool(SetReg.may(A_, "test.conf2")) and not bool(SetReg.may(C_, "test.conf2")),
          "G. two mods, two different nodes: the key is refused (hidden even for holders and ops)")
    check(bool(reg.apply(jarr("ModA", "test.own", "Own", "general", T, "h", "skyytest.staff")))
          and bool(reg.apply(jarr("ModA", "test.own", "Own", "general", T, "h", "skyytest.other"))) and str(SetReg.permOf("test.own")) == "skyytest.other",
          "G. a mod may change its own node")
    check(bool(reg.apply(jarr("ModA", "test.own", "Own", "general", T, "h"))) and str(SetReg.permOf("test.own")) == "skyytest.other",
          "G. ... but never drops it by registering without one")

    # ---------------- E. this round's rows in their tabs + paging on the real page
    SetReg.DEFS.clear()
    SetReg.REFUSED.clear()
    SetReg.PERM_MOD.clear()
    for k in list(br.keySet()):
        if str(k).startswith("settings:def:test."):
            br.remove(k)
    scripts, rp, rr = round_scripts()
    nreg = 0
    for mod, p in scripts:
        t = open(p, encoding="utf-8", errors="ignore").read()
        for k, lab, cat, df, hlp, perm in REG.findall(t):
            a = [mod, k, lab, cat, Boolean.valueOf(df.lower() == "true"), hlp] + ([perm] if perm else [])
            check(bool(reg.apply(jarr(*a))), "E. register %s (%s)" % (k, mod))
            nreg += 1
    SetReg.registerOwn()
    print("E. registered %d switches from %d scripts of this round's set + SkyyMenu's own" % (nreg, len(scripts)))
    check("SkyyRolls" not in [m for m, p in scripts] and "SkyyGear" in [m for m, p in scripts], "E. the round set: SkyyGear in, SkyyRolls out")
    cat = dict((str(c), i) for i, c in enumerate(MD.SET_CAT_ID))
    gen = [str(x) for x in SetReg.visible(cat["general"], B_)]
    com = [str(x) for x in SetReg.visible(cat["combat"], B_)]
    ski = [str(x) for x in SetReg.visible(cat["skills"], B_)]
    check(gen == ["party.invites", "party.members", "party.chat", "guild.online", "guild.members", "guild.chat", "tpa.requests",
                  "tpa.updates", "msg.private", "menu.tooltips"], "E. General rows in Settings-Spec 2.2 order: %s" % gen)
    check(com == ["classes.blockedChat", "classes.blockedPopup", "classes.healGiven", "classes.healTaken", "gear.blockedPopup",
                  "gear.armorWarn", "gear.notices", "gear.critFx", "skills.xbowMeter", "skills.xbowSound", "skills.xbowHint"], "E. Combat rows (0.3.7: + gear.critFx): %s" % com)
    check(len(ski) == 8 and ski[7] == "skills.overallUp", "E. Skills: skills.overallUp is row 8: %s" % ski)
    for k in ("party.invites", "tpa.requests", "msg.private", "skills.overallUp", "skills.xbowMeter", "gear.notices"):
        check(k in list(MD.SET_ORDER) and ("#%s=true" % k) in str(MD.SET_TEMPLATE), "E. %s in SET_ORDER and the defaults template" % k)
    rows = int(MD.SET_ROWS)
    check(rows == 8, "E. 8 rows per page")
    for tab, n in (("general", 10), ("combat", 11)):
        pg = SettingsPage(pref(B_), cat[tab])
        c1 = build(pg)
        check(rows_of(c1) == 8 and ("%d settings" % n) in head_of(c1) and "page 1 of 2" in head_of(c1), "E. %s page 1: 8 rows, %r" % (tab, head_of(c1)))
        check(any(s == "#SkyyStgFoot" and "#SkyyStgPrev" in t for s, t, d in c1) and any(s == "#SkyyStgFoot" and "#SkyyStgNext" in t for s, t, d in c1),
              "E. %s: Prev / Next drawn" % tab)
        pg.pageNo = 1
        c2 = build(pg)
        check(rows_of(c2) == n - 8 and "page 2 of 2" in head_of(c2), "E. %s page 2: %d rows, %r" % (tab, n - 8, head_of(c2)))
        names2 = [d for s, t, d in c2 if s.startswith("#SkyyStgName")]
        last2 = gen[8:] if tab == "general" else com[8:]
        check(len(names2) == n - 8, "E. %s page 2 row names %s (keys %s)" % (tab, names2, last2))
        pg.pageNo = 5
        c3 = build(pg)
        check(int(pg.pageNo) == 1 and rows_of(c3) == n - 8, "E. %s: a page past the end clamps to the last" % tab)
    pgS = SettingsPage(pref(B_), cat["skills"])
    cS = build(pgS)
    check(rows_of(cS) == 8 and "page" not in head_of(cS) and not any("#SkyyStgPrev" in t for s, t, d in cS), "E. Skills: 8 rows, one page")
    check(sorted(tabs_of(cS)) == list(range(len(MD.SET_CAT_ID))), "E. every tab has rows in this round's set, all 8 drawn: %s" % tabs_of(cS))
    check(parent_of(cS, 4) == "#SkyyStgTabs1" and parent_of(cS, 3) == "#SkyyStgTabs0", "E. 4 + 4 tab rows when all tabs are visible")

    # ---------------- F. Mods list texts + menu entries
    mods = [str(x) for x in MD.MOD_NAME]
    ver = dict(zip(mods, [str(x) for x in MD.MOD_VER]))
    check("SkyyGear" in mods and "SkyyRolls" not in mods, "F. SkyyGear replaces SkyyRolls in the Mods list")
    for m, v in rp.items():
        check(ver.get(m) == v[1], "F. %s version %s" % (m, v[1]))
    # 0.3.4: every MODS version = what tools/deploy_set.py SET pins (SkyyMenu's own entry = VERSION); 0.3.7: + this round's ROUND_PINS
    _set = round_set()
    for m, v in _set:
        check(ver.get(m) == (VERSION if m == "SkyyMenu" else v), "F. %s version %s (SET)" % (m, v))
    check(sorted(mods) == sorted(m for m, v in _set), "F. MODS lists exactly the SET mods: %s" % sorted(set(mods) ^ set(m for m, v in _set)))

    def body(m, admin):
        return str(MU.modBodyFor(mods.index(m), admin))
    g_pl, g_ad = body("SkyyGear", False), body("SkyyGear", True)
    check("/identify" in g_pl and "/reforge" in g_pl and "/gear -" in g_pl and "/gear give" not in g_pl, "F. SkyyGear for players: commands, no admin lines")
    check("Admin only:" in g_ad and "/gear give" in g_ad and "/gear migrate" in g_ad and "/gear level" in g_ad, "F. SkyyGear for admins: the /gear admin lines")
    check("unidentified" in g_pl and "Rarity, level and modifiers" in g_pl, "F. SkyyGear description")
    e_ad = body("SkyyEssentials", True)
    check("spawn" not in e_ad and "Warps page" in e_ad and "privacy.staffBypass" in e_ad and "/settings" in e_ad,
          "F. Essentials: no world spawn, the Warps page, privacy.staffBypass")
    p_ad = body("SkyyParty", True)
    check("privacy.staffBypass" in p_ad and "party invites" in p_ad.lower(), "F. Party: party invites switch + privacy.staffBypass")
    c_pl = body("SkyyClasses", False)
    check("/class arrows" in c_pl and "hotbar at once" in c_pl, "F. Classes: /class arrows, kits in the hotbar at once")
    check("Omni" in body("SkyySacks", False) and "Rare" in body("SkyySacks", False), "F. Sacks: rarity bags + the Mythic Omni Bag")
    check("tiers I, III, V and VII" in body("SkyyCollections", False), "F. Collections: the bag ladder")
    check("type it twice" not in body("SkyyVault", False) and "window" in body("SkyyVault", False), "F. Vault: the confirm window")
    check("overall" in body("SkyySkills", False) and "Overall Level" in body("SkyySkills", False), "F. Skills: Overall Level")
    check("Owner" in body("SkyyRanks", False), "F. Ranks: the Owner rank")
    pr_pl, pr_ad = body("SkyyProfiles", False), body("SkyyProfiles", True)
    check("/profiles delete" in pr_pl and "/profiles restore" in pr_pl and "/profileadmin" not in pr_pl and "restored" in pr_pl,
          "F. Profiles 0.1.5: /profiles delete + restore for players")
    check("/profileadmin archive list" in pr_ad and "/profileadmin archive restore" in pr_ad and "reload" in pr_ad, "F. Profiles: the archive lines for admins")
    ac_pl, ac_ad = body("SkyyAccessories", False), body("SkyyAccessories", True)
    check("/accessories lines" in ac_pl and "18 slots" in ac_pl and "/accessories give" not in ac_pl and "/accessories givetier" in ac_ad,
          "F. Accessories 0.5.1: lines, 18 slots, give lines admin only")
    check("/gear charged" in body("SkyyGear", True) and "/gear charged" not in body("SkyyGear", False), "F. /gear charged: admins only")
    up_pl, up_ad = body("SkyyUiProbe", False), body("SkyyUiProbe", True)
    check("Developer test mod" in up_pl and "/skyprobe" not in up_pl and "/skyprobe" in up_ad, "F. SkyyUiProbe: a dev mod, /skyprobe admins only")
    check("by what each put in" in body("SkyyGuilds", False), "F. Guilds 0.1.5: disband pays back by contribution")
    allb = " ".join(body(m, True) for m in mods)
    check("SkyyRolls" not in allb and "/rolls" not in allb and "world spawn" not in allb, "F. no stale SkyyRolls / world spawn text")
    fl = [str(x) for x in MD.MOD_FLINE][mods.index("SkyyGear")]
    check("Skyy_SkyyGear/config.properties" in fl, "F. SkyyGear file-only line: %r" % fl)
    ev_, es_, ei_, ea_, en_ = [list(MD.E_VIEW), list(MD.E_SLOT), list(MD.E_ICON), list(MD.E_ACT), list(MD.E_NAME)]
    main = dict((int(es_[i]), (str(ei_[i]), str(ea_[i]), str(en_[i]), str(list(MD.E_BODY)[i]))) for i in range(len(ev_)) if str(ev_[i]) == "main")
    check(main.get(26, ("",))[0] == "Ingredient_Crystal_Purple" and main[26][1] == "cmdc:identify" and main[26][2] == "Identify",
          "F. Identify tile at main slot 26")
    check(main.get(25, ("", "", "", ""))[1] == "cmdc:reforge" and "modifiers" in main[25][3] and "tool" not in main[25][3], "F. Reforge text")
    check(main.get(39, ("", ""))[1] == "settings" and main.get(40, ("", "", ""))[2] == "Mods" and 51 not in main, "F. Settings at 39 left of Mods, 51 empty")
    check(MU.cmd("identify") is None and str(JN("MenuPage").cmdOf("cmdc:identify")) == "identify",
          "F. no /identify command loaded -> MenuUtil.cmd null = the greyed 'not installed' path of fillStatic")
    check("identifying gear" in str(MD.MOD_BODY[mods.index("SkyyMenu")]), "F. SkyyMenu's own Mods text names identifying")
    # review fix: Commands lines marked (admin) / (staff) only in the admins' Mods text (MOD_AONLY = the MOD_ADMIN lines)
    madm = [str(x) for x in MD.MOD_ADMIN]
    for i, m in enumerate(mods):
        pl, ad = body(m, False), body(m, True)
        st = str(MD.MOD_BODY[i]) + str(MD.MOD_OLD_BODY[i])
        check("(admin)" not in pl and "(staff)" not in pl and "(admin)" not in st and "(staff)" not in st,
              "F. %s: no (admin) / (staff) line in the players' Mods text" % m)
        for l in [x for x in madm[i].split("\n") if x]:
            check(l.replace("<", "[").replace(">", "]") in ad, "F. %s: the admin sees %r" % (m, l[:50]))
    c_pl2, c_ad2 = body("SkyyClasses", False), body("SkyyClasses", True)
    check("/classadmin" not in c_pl2 and "/class arrows" in c_pl2 and all(("/classadmin " + s) in c_ad2 for s in ("set", "reset", "info", "reload", "kit")),
          "F. /classadmin set|reset|info|reload|kit: admins only")
    check("/classadmin set" in madm[mods.index("SkyyClasses")], "F. ... and on the Server Setup page (MOD_ADMIN)")
    a_pl, a_ad = body("SkyyAuctions", False), body("SkyyAuctions", True)
    check("/ahadmin" not in a_pl and "/ah sell" in a_pl and "regrant" in a_ad and "Admin only:" in a_ad, "F. /ahadmin ... regrant: admins only")
    check("/fly" not in body("SkyyEssentials", False) and "/fly - (staff)" in body("SkyyEssentials", True), "F. /fly (staff): admins only")
    r_pl, r_ad = body("SkyyRanks", False), body("SkyyRanks", True)
    check("/rank set [player] [rank] | clear [player] - (admin)" in r_ad and "/rank" not in r_pl, "F. SkyyRanks: /rank set <player> <rank> | clear <player>, admins only")

    # ---------------- F (0.3.5): the ONE version table + the help texts of the 2026-10-01 / 2026-10-02 builds
    _tbl = build_table()
    _setv = dict((m, v) for m, v in _set if m != "SkyyMenu")
    check(_tbl == _setv, "F. the build script's MODS_VERSIONS table = tools/deploy_set.py SET: differs %s" % sorted(set(_tbl.items()) ^ set(_setv.items())))
    check(len(mods) == len(_set) and len(set(mods)) == len(mods), "F. %d mods, each listed once (SET has %d)" % (len(mods), len(_set)))
    if "SkyyMobs" not in mods:
        check(False, "F. SkyyMobs is not in the jar's Mods list - its 0.3.5 checks are skipped")
    else:
        check(mods.index("SkyyMobs") == mods.index("SkyyGear") + 2 and mods[mods.index("SkyyGear") + 1] == "SkyyArmory" and mods[-1] == "SkyyUiProbe",
              "F. SkyyMobs right after SkyyGear + SkyyArmory (0.3.7), the dev mod last")
        mb_pl, mb_ad = body("SkyyMobs", False), body("SkyyMobs", True)
        check("/mobs (or /mobs info) - the mob level band where you stand" in mb_pl and "Zone 1 1-20" in mb_pl and "[Lv 9] Trork Warrior" in mb_pl
              and "bosses never" in mb_pl, "F. SkyyMobs for players: /mobs, the zone bands, the plate, who never gets a level")
        for sub in ("inspect", "set [level]", "platetest", "reload"):
            check(("/mobs " + sub) not in mb_pl and ("/mobs " + sub + " - (admin)") in mb_ad, "F. SkyyMobs: /mobs %s for admins only" % sub)
        i_mobs = mods.index("SkyyMobs")
        check(str(MD.MOD_STITLE[i_mobs]) == "Mobs" and str(MD.MOD_CHECK[i_mobs]) == "mobs" and str(MD.MOD_SINCE[i_mobs]) == "0.1"
              and ver.get("SkyyMobs") == dict(_set).get("SkyyMobs"), "F. SkyyMobs: Server Setup title Mobs since 0.1, installed check /mobs, version = SET")
        _flm = str(MD.MOD_FLINE[i_mobs])
        check("Skyy_SkyyMobs/config.properties and 1 more" in _flm and "/mobs reload" in _flm, "F. SkyyMobs file-only line: %r" % _flm)
    check("/skyprobe win | secgrid - (admin)" in up_ad and "secgrid" not in up_pl and "vault window probes" in up_pl
          and ver.get("SkyyUiProbe") == dict(_set).get("SkyyUiProbe"), "F. SkyyUiProbe 0.3+: /skyprobe win | secgrid for admins only")
    g5_pl, g5_ad = body("SkyyGear", False), body("SkyyGear", True)
    check("/gear relevel [player] - (admin)" in g5_ad and "relevel" not in g5_pl and "its own level" in g5_pl, "F. SkyyGear 0.2: item levels; /gear relevel admins only")
    sk_pl, sk_ad = body("SkyySkills", False), body("SkyySkills", True)
    check("/skills mana - (admin)" in sk_ad and "/skills mana" not in sk_pl and "own XP curve" in sk_pl and "Mana refills in combat" in sk_pl,
          "F. SkyySkills 0.4.12: class curve, Mana in combat; /skills mana admins only")
    sa_pl = body("SkyySacks", False)
    check("Stack refill (on the /sacks page): Hotbar only, Full inventory or Off" in sa_pl and "Bags of one type add up" in sa_pl
          and "Benches, inventory crafting and /craft use the bags you carry" in sa_pl, "F. SkyySacks 0.7.11 - 0.7.12: stack refill, bags add up, benches")
    check("Coins never buy a tier, recipe or bag" in body("SkyyCollections", False), "F. SkyyCollections 0.2.5: coins never buy tiers")
    es_pl = body("SkyyEssentials", False)
    check("can't be traded" in es_pl and "trade items and coins safely (no Magic Bags)" in es_pl, "F. SkyyEssentials 0.1.7: no Magic Bags in /trade")
    check("party, guild, skills (your Overall Level" in body("SkyyHud", False), "F. SkyyHud 0.3.11: the Skills widget (0.3.6 wording)")
    check("Workbench tab Accessories and Bags" in ac_pl, "F. SkyyAccessories 0.5.2: the Workbench tab")
    gu_pl = body("SkyyGuilds", False)
    check("leaves or is kicked" in gu_pl and "35%" in gu_pl, "F. SkyyGuilds 0.1.6: the leave refund")
    check("Pick it on that page" in main[11][3] or "pick it on that page" in main[11][3], "F. main menu Pocket Dimension: the stack refill line")
    check("Vanilla benches and inventory crafting use the bags you carry too." in main[14][3], "F. main menu Crafting: benches use the bags")
    check("booster accessories" in main[12][3] and "talisman" not in main[12][3], "F. main menu Accessory Bag: booster accessories")
    _all5 = " ".join(body(m, True) for m in mods) + " " + " ".join(str(x) for x in MD.E_BODY)
    check("&" not in _all5 and "stat talismans" not in _all5, "F. no raw & in any tooltip text, no 'stat talismans' (boosters since 0.5)")
    for i, m in enumerate(mods):
        for l in body(m, True).split("\n")[1:]:
            if len(l) > 80:
                check(False, "F. %s: an info line longer than 80 characters: %r" % (m, l))

    # ---------------- F (0.3.6): the 2026-10-03 SET - the NEW SkyyWorldGen entry and the help texts of the 2026-10-02 / 10-03 builds
    check(ver.get("SkyyMenu") == VERSION and len(mods) == 26, "F. 0.3.7: 26 mods (SkyyMenu %s): %d" % (ver.get("SkyyMenu"), len(mods)))
    if "SkyyWorldGen" not in mods:
        check(False, "F. SkyyWorldGen is not in the jar's Mods list - its 0.3.6 checks are skipped")
    else:
        i_wg = mods.index("SkyyWorldGen")
        wg_pl, wg_ad = body("SkyyWorldGen", False), body("SkyyWorldGen", True)
        check(i_wg == mods.index("SkyyMobs") + 1 and mods[-1] == "SkyyUiProbe", "F. SkyyWorldGen right after SkyyMobs, the dev mod still last")
        check(ver.get("SkyyWorldGen") == dict(_set).get("SkyyWorldGen") and str(MD.MOD_STITLE[i_wg]) == "World Gen"
              and str(MD.MOD_CHECK[i_wg]) == "zone" and str(MD.MOD_SINCE[i_wg]) == "0.1",
              "F. SkyyWorldGen: version = SET, Server Setup title World Gen since 0.1, installed check /zone")
        check("/zone" not in wg_pl and "No commands for players yet" in wg_pl and "World Gen V2" in wg_pl and "only admins" in wg_pl,
              "F. SkyyWorldGen for players: no /zone line (every /zone command is admin-only), what it is")
        for a_ in ("/zone - (admin)", "/zone 1 - (admin)", "/zone info | leave - (admin)", "/zone setlanding - (admin)", "/zone reload - (admin)"):
            check(a_ in wg_ad, "F. SkyyWorldGen admin line %r" % a_)
        _flw = str(MD.MOD_FLINE[i_wg])
        check("Skyy_SkyyWorldGen/config.properties" in _flw and "/zone reload" in _flw, "F. SkyyWorldGen file-only line: %r" % _flw)
        check(str(MD.MOD_ICON[i_wg]) == "Plant_Sapling_Azure", "F. SkyyWorldGen icon (the azure core)")
    check("combat indicator (red with a countdown" in body("SkyyHud", False), "F. SkyyHud 0.3.12: the combat indicator")
    g6 = body("SkyyGear", False)
    check("its damage or armor grows with that level" in g6 and "its own level" in g6, "F. SkyyGear 0.2.1: damage and armor by level")
    sk6 = body("SkyySkills", False)
    check("Stronger mobs pay more kill XP and early gathering is faster" in sk6 and "own XP curve" in sk6 and "Mana refills in combat" in sk6,
          "F. SkyySkills 0.4.14: kill XP by mob level, early gathering (0.4.12 texts kept)")
    check("the Lantern (you glow like a torch)" in body("SkyyAccessories", False) and "18 slots" in body("SkyyAccessories", False),
          "F. SkyyAccessories 0.5.4+: the Lantern (0.3.7; 0.3.6 said Night Vision)")
    check("32% stronger" in body("SkyyCooking", False), "F. SkyyCooking 0.1.4: +32% per Grade")
    mb6 = body("SkyyMobs", False)
    check("Difficulty Easy, Normal or Hard in Server Setup" in mb6 and "weak mobs get a health floor" in mb6 and "[Lv 9] Trork Warrior" in mb6,
          "F. SkyyMobs 0.1.1 - 0.1.2: difficulty ladder, health floor")
    for i, m in enumerate(mods):
        d_ = str(MD.MOD_BODY[i]).split("\n")[0]
        check(len(d_) <= 390, "F. %s: description %d characters (<= 390)" % (m, len(d_)))
    _all6 = " ".join(body(m, True) for m in mods)
    check("&" not in _all6 and "SkyyRolls" not in _all6, "F. 0.3.6: no raw & and no SkyyRolls in any Mods text")

    # ---------------- F2 (0.3.7): the Lantern texts, SkyyArmory, SkyyUiProbe 0.4, SkyyBazaar's Server Setup page, gear.critFx
    _all7 = (" ".join(body(m, True) + " " + body(m, False) for m in mods) + " " + " ".join(str(x) for x in MD.E_BODY) + " " +
             " ".join(str(x) for x in MD.MOD_SWHAT) + " " + " ".join(str(x) for x in MD.MOD_STITLE))
    check("night vision" not in _all7.lower(), "F2. 0.3.7: no Mods or menu text names Night Vision (retired by SkyyAccessories 0.5.4)")
    i_ac = mods.index("SkyyAccessories")
    check("Lantern" in str(MD.MOD_SWHAT[i_ac]) and str(MD.MOD_STITLE[i_ac]) == "Accessories",
          "F2. SkyyAccessories Server Setup line names the Lantern: %r" % str(MD.MOD_SWHAT[i_ac]))
    for m_, v_ in (("SkyyExploration", "0.2.3"), ("SkyyAccessories", "0.5.5"), ("SkyyCooking", "0.1.6"), ("SkyyArmory", "0.1"), ("SkyyUiProbe", "0.4"),
                   ("SkyyHud", "0.3.13"), ("SkyyMobs", "0.1.3"), ("SkyyGear", "0.2.3"), ("SkyySkills", "0.4.16"), ("SkyyTrees", "0.3.2"),
                   ("SkyyCollections", "0.2.6"), ("SkyyParty", "0.1.7"), ("SkyyBazaar", "0.1.4"), ("SkyyEssentials", "0.1.8")):   # 0.3.8 versions
        check(ver.get(m_) == v_, "F2. %s %s in the Mods list (got %s)" % (m_, v_, ver.get(m_)))
    if "SkyyArmory" not in mods:
        check(False, "F2. SkyyArmory is not in the jar's Mods list")
    else:
        i_ar = mods.index("SkyyArmory")
        ar_pl, ar_ad = body("SkyyArmory", False), body("SkyyArmory", True)
        check(i_ar == mods.index("SkyyGear") + 1, "F2. SkyyArmory right after SkyyGear")
        check(str(MD.MOD_STITLE[i_ar]) == "Armory" and str(MD.MOD_SINCE[i_ar]) == "0.1" and str(MD.MOD_CHECK[i_ar]) == ""
              and str(MD.MOD_ICON[i_ar]) == "Weapon_Wand_Wood", "F2. SkyyArmory: Server Setup Armory since 0.1, no command check, the wand icon")
        check("Tap for a quick shot, hold for a charged shot" in ar_pl and "No commands" in ar_pl and "Weapon Bench (Bow tab)" in ar_pl
              and "/" not in ar_pl, "F2. SkyyArmory for players: what it is, no command line: %r" % ar_pl[:200])
        check("Admin only:" not in ar_ad, "F2. SkyyArmory: no admin lines (it has no commands)")
        _fla = str(MD.MOD_FLINE[i_ar])
        check("Skyy_SkyyArmory/config.properties" in _fla and "Server Setup -> Armory" in _fla, "F2. SkyyArmory file-only line: %r" % _fla)
        check(not JN("AdminPage").installed(i_ar), "F2. SkyyArmory with no plugin loaded: not installed (no command to find; in game its plugin name decides)")
    up7_pl, up7_ad = body("SkyyUiProbe", False), body("SkyyUiProbe", True)
    check("/skyprobe map [step] - (admin)" in up7_ad and "/skyprobe map" not in up7_pl, "F2. SkyyUiProbe 0.4: /skyprobe map for admins only")
    i_bz = mods.index("SkyyBazaar")
    check(str(MD.MOD_STITLE[i_bz]) == "Bazaar" and str(MD.MOD_SINCE[i_bz]) == "0.1.3" and "/bazaaradmin reload" in str(MD.MOD_FLINE[i_bz]),
          "F2. SkyyBazaar: Server Setup Bazaar since 0.1.3, the file line keeps /bazaaradmin reload: %r" % str(MD.MOD_FLINE[i_bz]))
    _keys7 = [str(x) for x in MD.SET_ORDER]
    check("gear.critFx" in _keys7 and _keys7.index("gear.critFx") == _keys7.index("gear.notices") + 1, "F2. gear.critFx known, right after gear.notices")

    # ---------------- F3 (0.3.8): the texts of Gear 0.2.3, Skills 0.4.16, Party 0.1.7 + Essentials 0.1.8, Bazaar 0.1.4, Trees 0.3 - 0.3.2
    g8_pl = body("SkyyGear", False)
    i_g = mods.index("SkyyGear")
    check("rolls and pays Smithing XP" in g8_pl and "crafting Smithing XP" in str(MD.MOD_SWHAT[i_g]) and "damage and armor by level" in str(MD.MOD_SWHAT[i_g]),
          "F3. SkyyGear 0.2.3: crafted gear pays Smithing XP (description + Server Setup line): %r" % str(MD.MOD_SWHAT[i_g]))
    i_s = mods.index("SkyySkills")
    check("own XP list per skill" in str(MD.MOD_SWHAT[i_s]) and str(MD.MOD_STITLE[i_s]) == "Skills", "F3. SkyySkills 0.4.16: own XP list per skill in the Server Setup line")
    check("TPA and Accept TPA buttons" in body("SkyyParty", False), "F3. SkyyParty 0.1.7: the TPA buttons named")
    check("teleport requests between players (also from the party page)" in body("SkyyEssentials", False), "F3. SkyyEssentials 0.1.8: TPA from the party page")
    check("about twice the one before" in body("SkyyBazaar", False), "F3. SkyyBazaar 0.1.4: progression prices")
    tr_pl, tr_ad = body("SkyyTrees", False), body("SkyyTrees", True)
    i_t = mods.index("SkyyTrees")
    check("Alchemy, Smithing, Acrobatics and Exploration" in tr_pl and "a class tree that spends the Ability Points" in tr_pl, "F3. SkyyTrees: Alchemy / Smithing + the class tree")
    check("/tree class - your class tree" in tr_pl and "/tree probe" not in tr_pl and "/tree probe - (admin)" in tr_ad and "/tree reload" not in tr_pl,
          "F3. SkyyTrees: /tree class for players, /tree probe + reload for admins only")
    check("class trees" in str(MD.MOD_SWHAT[i_t]) and str(MD.MOD_STITLE[i_t]) == "Trees", "F3. SkyyTrees Server Setup line names class trees: %r" % str(MD.MOD_SWHAT[i_t]))
    for i_, m_ in enumerate(mods):
        check(len(str(MD.MOD_SWHAT[i_])) <= 60, "F3. %s: Server Setup line <= 60 characters" % m_)

    # ================================================================================================ 0.3.4
    # ---------------- H. seconds in Server Setup
    AP = JN("AdminPage")
    JS = JClass("java.lang.String")

    def S(x):
        return None if x is None else str(x)

    def krow(key, label, typ, d, lo, hi, unit, opts=""):
        return jarr(key, label, "c", typ, d, lo, hi, opts, unit, "live", "Help text of " + key)

    R_MS = krow("regen.periodMs", "Regen tick", "int", "2000", "250", "60000", "ms")
    R_MS0 = krow("fell.memoryMs", "Remember who felled a tree", "int", "60000", "0", "600000", "ms")
    R_OPEN = krow("x.openMs", "No bounds", "int", "1000", "", "", "ms")
    R_DEC = krow("x.decMs", "Dec ms", "dec", "1.5", "0", "100", "ms")
    R_RNG = krow("x.rangeMs", "Range ms", "range", "100-200", "0", "1000", "ms")
    R_S = krow("x.sec", "Seconds row", "int", "5", "1", "60", "s")
    R_PCT = krow("x.pct", "Percent row", "int", "3", "0", "100", "%")
    R_BLK = krow("x.blocks", "Blocks row", "int", "8", "1", "64", "blocks")
    R_TXT = krow("x.txtMs", "Text ms", "text", "", "", "", "ms")
    # review 2026-10-01: the mods' own help texts of the millisecond rows (SkySkills feedbackMs "...per this many ms.", the jump / dodge
    # cooldowns with NO help text at all)
    R_HMS = jarr("x.fbMs", "XP line at most every", "c", "int", "2000", "500", "600000", "", "ms", "live,adv",
                 "One combined +XP chat line per player per this many ms.")
    R_HNO = jarr("x.jumpMs", "Paid jump cooldown", "c", "int", "800", "200", "600000", "", "ms", "live,adv", "")
    R_HNUM = jarr("x.numMs", "Help with numbers", "c", "int", "1500", "250", "60000", "", "ms", "live",
                  "Waits 250 ms at least; 12 items, 5 msgs, Millis and milliseconds count.")
    check(bool(AP.msRow(R_MS)) and bool(AP.msRow(R_DEC)) and not bool(AP.msRow(R_RNG)) and not bool(AP.msRow(R_S))
          and not bool(AP.msRow(R_TXT)) and not bool(AP.msRow(R_PCT)) and not bool(AP.msRow(None)), "H. msRow: int / dec rows with unit ms only")
    for ms, sec in (("240", "0.24"), ("1", "0.001"), ("1500", "1.5"), ("30000", "30"), ("0", "0"), ("250", "0.25"), ("60000", "60"),
                    ("600000", "600"), ("3600000", "3600"), ("100", "0.1"), ("2000", "2"), ("86400000", "86400"), ("1.5", "0.0015")):
        check(S(AP.secText(ms)) == sec, "H. secText(%s) = %s (got %s)" % (ms, sec, S(AP.secText(ms))))
    check(S(AP.secText("abc")) == "abc" and AP.secText(None) is None and S(AP.secText("")) == "", "H. secText leaves non-numbers alone")
    for typed, ms in (("0.24", "240"), ("0.001", "1"), ("1.5", "1500"), ("30", "30000"), ("0", "0"), ("0.25", "250"), ("60", "60000"),
                      (" 0.24 ", "240"), ("0.240", "240"), ("00.24", "240"), (".5", "500"), ("5.", "5000"), ("1.5s", "1500"),
                      ("1.5 s", "1500"), ("2 sec", "2000"), ("2secs", "2000"), ("2 second", "2000"), ("2 seconds", "2000"),
                      ("240ms", "240"), ("240 ms", "240"), ("0.2405", "241"), ("0.2404", "240"), ("0.0005", "1"), ("0.0004", "0"),
                      ("+1", "1000"), ("-1", "-1000"), ("3600", "3600000"), ("1_000", "1000000"), ("0.1", "100"), ("0.3", "300"),
                      ("0.7", "700"), ("1.1", "1100"), ("2.675", "2675"), ("1.005", "1005"), ("0.29", "290"), ("0.57", "570")):
        check(S(AP.msOf(typed, True)) == ms, "H. msOf(%r) = %s ms (got %s)" % (typed, ms, S(AP.msOf(typed, True))))
    check(S(AP.msOf("0.0005", False)) == "0.5" and S(AP.msOf("0.24", False)) == "240", "H. msOf on a dec row keeps parts of a ms")
    for bad in ("", "   ", "abc", "1,5", "1,000", "0.2.4", ".", "-", "+", "1e3", "5m", "5 min", "s", "ms", "0x10", "--1", "1-", "2 ms s",
                "seconds", "1.5h", "12:30", "%5"):
        check(AP.msOf(bad, True) is None, "H. msOf refuses %r (got %s)" % (bad, S(AP.msOf(bad, True))))
    check(AP.msOf(None, True) is None, "H. msOf(null)")
    drift = []
    for i in range(0, 3001):
        if S(AP.msOf(S(AP.secText(str(i))), True)) != str(i):
            drift.append(i)
    for i in range(0, 2001):
        t = "%d.%03d" % (i // 1000, i % 1000)
        if S(AP.msOf(t, True)) != str(i):
            drift.append(("typed", t))
    for i in (59999, 60000, 60001, 599999, 600000, 3599999, 3600000, 86400000, 9007199254740993):
        if S(AP.msOf(S(AP.secText(str(i))), True)) != str(i):
            drift.append(i)
    check(not drift, "H. round trips: every whole ms 0-3000, every 0.000-2.000 s step and big values convert both ways exactly: %s" % drift[:5])

    def tv(r, v):
        a = AP.typedValue(r, v)
        return (S(a[0]), S(a[1]))
    check(tv(R_MS, "0.25") == ("250", None) and tv(R_MS, "60") == ("60000", None), "H. typedValue: min 0.25 s and max 60 s accepted")
    _lo, _hi = tv(R_MS, "0.249"), tv(R_MS, "60.001")
    check(_lo[0] is None and "0.25 to 60 seconds" in _lo[1] and "Regen tick" in _lo[1] and "0.249" in _lo[1], "H. below the min refused in seconds: %r" % (_lo[1],))
    check(_hi[0] is None and "0.25 to 60 seconds" in _hi[1] and "60.001" in _hi[1], "H. above the max refused in seconds: %r" % (_hi[1],))
    check(tv(R_MS, "0.2495") == ("250", None) and tv(R_MS, "0.2494")[0] is None and tv(R_MS, "60.0004") == ("60000", None),
          "H. rounding to whole ms happens before the bounds check (0.2495 -> 250 ok, 0.2494 -> 249 refused)")
    _bad = tv(R_MS, "abc")
    check(_bad[0] is None and "seconds" in _bad[1] and "0.25" in _bad[1], "H. not a time refused: %r" % (_bad[1],))
    check(tv(R_MS, "1,5")[0] is None and tv(R_MS, "")[0] is None, "H. a comma / empty refused")
    check(tv(R_MS0, "0") == ("0", None) and tv(R_MS0, "-0.001")[0] is None and tv(R_MS0, "600") == ("600000", None) and tv(R_MS0, "600.001")[0] is None,
          "H. min 0 / max 600 s edges")
    check(tv(R_MS, "240ms")[0] is None and tv(R_MS, "250ms") == ("250", None), "H. 240ms typed as milliseconds, checked against the min")
    check(tv(R_OPEN, "123.456") == ("123456", None) and tv(R_OPEN, "0") == ("0", None), "H. a row without bounds")
    check(tv(R_DEC, "0.0015") == ("1.5", None), "H. a dec ms row keeps parts of a ms")
    check(tv(R_S, "abc") == ("abc", None) and tv(R_PCT, "3%") == ("3%", None) and tv(R_RNG, "100-200") == ("100-200", None),
          "H. other rows are sent as typed (the mod checks them)")
    check(S(AP.disp(R_MS, "240")) == "0.24 s" and S(AP.disp(R_MS, "60000")) == "60 s" and S(AP.disp(R_MS, "")) == "(empty)"
          and S(AP.disp(R_MS, None)) == "(unknown)", "H. disp: a ms value in seconds")
    check(S(AP.disp(R_S, "5")) == "5 s" and S(AP.disp(R_PCT, "3")) == "3%" and S(AP.disp(R_BLK, "8")) == "8 blocks"
          and S(AP.disp(R_RNG, "100-200")) == "100-200 ms", "H. disp of the other units unchanged (a range ms row keeps ms)")
    check(S(AP.secHint(R_MS)) == "0.25 to 60 seconds, default 2" and S(AP.secHint(R_OPEN)) == "In seconds, default 1",
          "H. secHint: %r / %r" % (S(AP.secHint(R_MS)), S(AP.secHint(R_OPEN))))
    for msg, want in (("Regen tick: 240 ms - saved (applies now).", "Regen tick: 0.24 s - saved (applies now)."),
                      ("Must be a whole number from 250 to 60000 ms.", "Must be a whole number from 0.25 to 60 s."),
                      ("Must be a whole number of at least 250 ms.", "Must be a whole number of at least 0.25 s."),
                      ("Change Regen tick from 2000 ms to 240 ms?", "Change Regen tick from 2 s to 0.24 s?"),
                      ("Regen tick: 2000 ms -> 3000 ms\nXP line at most every: 500 ms -> 1500 ms", "Regen tick: 2 s -> 3 s\nXP line at most every: 0.5 s -> 1.5 s"),
                      ("Regen tick is already 1 ms.", "Regen tick is already 0.001 s."),
                      ("Interest per payout: 3% - saved.", "Interest per payout: 3% - saved."),
                      ("12 items, 5 msgs, v1.2 ms", "12 items, 5 msgs, v1.2 ms"), ("", ""), ("no numbers ms", "no numbers ms")):
        check(S(AP.msWords(msg)) == want, "H. msWords(%r) = %r (got %r)" % (msg, want, S(AP.msWords(msg))))
    check(AP.msWords(None) is None, "H. msWords(null)")
    check(S(AP.rMsg(jarr("ok", "240", "Regen tick: 240 ms - saved (applies now)."))) == "Regen tick: 0.24 s - saved (applies now).",
          "H. rMsg (status line, confirm question, previews) reads the kit's ms in seconds")
    # drawRow with a fake mod on the bridge (config:def:SkyyTestms + config:fn:SkyyTestms)
    VALS = {"regen.periodMs": "2000", "x.blocks": "8", "x.decMs": "1.5", "x.fbMs": "2000", "x.jumpMs": "800", "x.numMs": "1500"}

    @JImplements("java.util.function.Function")
    class FakeCfg:
        @JOverride
        def apply(self, a):
            if a is not None and len(a) >= 2 and str(a[0]) == "get":
                return VALS.get(str(a[1]))
            return None
    rows = JArray(JObject)(6)
    rows[0], rows[1], rows[2], rows[3], rows[4], rows[5] = R_MS, R_BLK, R_DEC, R_HMS, R_HNO, R_HNUM
    hdrv = jarr("1", "SkyyTestms", "Test ms", "0.1", "skyytest.admin", JArray(JS)(["c"]), JArray(JS)(["Cat"]), rows,
                "Skyy_SkyyTestms/config.properties", "")
    br.put("config:def:SkyyTestms", hdrv)
    br.put("config:fn:SkyyTestms", FakeCfg())
    h = AP.hdr("SkyyTestms")
    check(h is not None and int(AP.rowIdx(h, "regen.periodMs")) == 0, "H. the fake mod's header reads")
    page = AP(pref(C_), "mod", "SkyyTestms")

    def draw_row(i):
        b, ev = UCB(), UEB()
        page.drawRow(b, ev, h, i, 0, True, True, "")
        out = {}
        for c in list(b.getCommands()):
            sel = str(c.selector) if c.selector is not None else ""
            out.setdefault(sel, []).append(str(c.data) if c.data is not None else "")
        return out

    def val_of(out, sel):
        return " ".join(out.get(sel, []))
    d0 = draw_row(0)
    check('"2"' in val_of(d0, "#SkyyAdmVal0.Value") and "2000" not in val_of(d0, "#SkyyAdmVal0.Value"),
          "H. drawRow: the value box shows 2 (seconds), not 2000: %r" % val_of(d0, "#SkyyAdmVal0.Value"))
    check("Regen tick (s)" in val_of(d0, "#SkyyAdmName0.Text") and "(ms)" not in val_of(d0, "#SkyyAdmName0.Text"),
          "H. drawRow: the name says (s): %r" % val_of(d0, "#SkyyAdmName0.Text"))
    check("0.25 to 60 seconds, default 2 - Help text" in val_of(d0, "#SkyyAdmDesc0.Text"), "H. drawRow: help starts with the bounds in seconds: %r" % val_of(d0, "#SkyyAdmDesc0.Text"))
    page.drafts.put("regen.periodMs", "0.24")
    d1 = draw_row(0)
    check('"0.24"' in val_of(d1, "#SkyyAdmVal0.Value") and "Regen tick (s) *" in val_of(d1, "#SkyyAdmName0.Text"), "H. a typed draft stays as typed (seconds) and is marked *")
    page.drafts.put("regen.periodMs", "2.000")
    draw_row(0)
    check(page.drafts.get("regen.periodMs") is None, "H. a draft equal to the value (2.000 s = 2000 ms) is dropped")
    d2 = draw_row(1)
    check('"8"' in val_of(d2, "#SkyyAdmVal0.Value") and "Blocks row (blocks)" in val_of(d2, "#SkyyAdmName0.Text")
          and val_of(d2, "#SkyyAdmDesc0.Text").count("seconds") == 0, "H. a blocks row is drawn as before")
    d3 = draw_row(2)
    check('"0.0015"' in val_of(d3, "#SkyyAdmVal0.Value"), "H. a dec ms row: 1.5 ms shows 0.0015 s")
    # the row's own help line is in seconds too, and a row without help text has no dangling " - "
    d4, d5, d6 = draw_row(3), draw_row(4), draw_row(5)
    def txt(out, sel):      # the builder's data for a .Text is a JSON string: {"0": "<text>"} - give the text itself
        import json
        return json.loads(val_of(out, sel))["0"]
    _h4, _h5, _h6 = txt(d4, "#SkyyAdmDesc0.Text"), txt(d5, "#SkyyAdmDesc0.Text"), txt(d6, "#SkyyAdmDesc0.Text")
    check(_h4 == "0.5 to 600 seconds, default 2 - One combined +XP chat line per player per this many seconds.",
          "H. help of a ms row says seconds, not 'this many ms': %r" % _h4)
    check(_h5 == "0.2 to 600 seconds, default 0.8" and not _h5.rstrip().endswith("-"),
          "H. a row without help text: the help line is just the bounds (no dangling dash): %r" % _h5)
    check(_h6 == "0.25 to 60 seconds, default 1.5 - Waits 0.25 s at least; 12 items, 5 msgs, seconds and seconds count.",
          "H. help with a number + ms, whole words only (items / msgs stay): %r" % _h6)
    for raw, want in (("per this many ms.", "per this many seconds."), ("Ms", "seconds"), ("ms", "seconds"), ("in MS", "in seconds"),
                      ("a 5 ms gap", "a 0.005 s gap"), ("items, msgs, forms, Arms", "items, msgs, forms, Arms"), ("", ""), ("no unit", "no unit")):
        check(S(AP.secHelp(raw)) == want, "H. secHelp(%r) = %r (got %r)" % (raw, want, S(AP.secHelp(raw))))
    check(S(AP.secHelp(None)) == "", "H. secHelp(null) is empty")
    check("Paid jump cooldown (s)" in val_of(d5, "#SkyyAdmName0.Text") and "(ms)" not in val_of(d4, "#SkyyAdmName0.Text"),
          "H. the names of the new rows say (s)")
    _lt = S(AP.logText(h, "SkyyTestms", JArray(JS)(["2026-10-01T10:00:00", "Skyy", str(C_), "menu", "regen.periodMs", "2000", "240", "ok"])))
    check("Regen tick  2 s -> 0.24 s" in _lt, "H. the Changes log line in seconds: %r" % _lt)
    br.remove("config:def:SkyyTestms")
    br.remove("config:fn:SkyyTestms")
    # every millisecond row of the live set: the build's rule finds them, each one is a msRow and its literal numbers round-trip
    found = ms_rows()
    EXPECT = {("SkyyGear", "regen.periodMs"), ("SkyySkills", "feedbackMs"), ("SkyySkills", "harvestCooldownMs"), ("SkyySkills", "fell.pollMs"),
              ("SkyySkills", "fell.quietMs"), ("SkyySkills", "fell.maxWatchMs"), ("SkyySkills", "fell.memoryMs"),
              ("SkyySkills", "acro.jumpCooldownMs"), ("SkyySkills", "acro.dodgeCooldownMs"), ("SkyySkills", "acro.feedbackMs"),
              ("SkyySkills", "acro.doubleJump.cooldownMs"), ("SkyySkills", "acro.doubleJump.minAirMs"), ("SkyyClasses", "openDelayMillis"),
              ("SkyyClasses", "priestHeal.feedbackMs"), ("SkyyEssentials", "tradeSaveDelayMillis"), ("SkyyProfiles", "openDelayMillis"),
              ("SkyyTrees", "feedbackMs"), ("SkyyExploration", "chests.pollMs"), ("SkyyExploration", "chests.pollMaxMs"),
              ("SkyyExploration", "chunks.feedbackMs"), ("SkyyExploration", "spots.checkMs"), ("SkyyExploration", "spots.bannerGapMs"),
              ("SkyyExploration", "bridge.retryMs"), ("SkyyVault", "saveDelayMillis")}
    got = set((m, k) for m, k, t, d, lo, hi in found)
    print("H. millisecond rows of the live set: %d (%s)" % (len(found), ", ".join("%s %s" % x for x in sorted(got))))
    check(got >= EXPECT and len(found) == len(got), "H. every millisecond row found: missing %s, extra %s" % (sorted(EXPECT - got), sorted(got - EXPECT)))
    for m, k, t, d, lo, hi in found:
        r = krow(k, k, t, d or "", lo or "", hi or "", "ms")
        check(bool(AP.msRow(r)), "H. %s %s is a seconds row" % (m, k))
        for v in (d, lo, hi):
            if isinstance(v, str) and re.match(r"^\d+$", v):
                check(S(AP.msOf(S(AP.secText(v)), t == "int")) == v, "H. %s %s: %s ms -> %s s -> back" % (m, k, v, S(AP.secText(v))))
        if lo and hi:
            check(tv(r, S(AP.secText(lo)))[0] == lo and tv(r, S(AP.secText(hi)))[0] == hi, "H. %s %s: min / max typed in seconds accepted" % (m, k))

    # ---------------- I. the menu item per profile
    Gv, MC, GT = JN("Given"), JN("MenuCfg"), JN("GrantTask")
    idir = os.path.join(SCRATCH, "item")
    os.makedirs(os.path.join(idir, "given"), exist_ok=True)
    Gv.DIR = Paths.get(os.path.join(idir, "given-profile"))
    Gv.LEGACY = Paths.get(os.path.join(idir, "given"))
    MC.GIVE_ITEM = True
    KEYS = {}

    @JImplements("java.util.function.Function")
    class PKey:
        @JOverride
        def apply(self, u):
            return KEYS.get(str(u), str(u))
    br.put("profile:fn:key", PKey())

    def recs():
        d = os.path.join(idir, "given-profile")
        return sorted(os.listdir(d)) if os.path.isdir(d) else []

    def plan(u, held):
        return int(Gv.plan(u, Gv.key(u), held))

    def give(u):
        """what GrantTask.grantNow does after plan() == 4 and a successful giveMenuItem"""
        Gv.markGiven(Gv.key(u))
    N = UUID.fromString("00000000-0000-0000-0000-0000000000a1")      # a brand-new player
    n = str(N)
    check(bool(Gv.wants(N)) and plan(N, 0) == 4, "I. new player, profile 1 (key = uuid): give one")
    give(N)
    check(recs() == [n + ".txt"] and plan(N, 0) == 1 and not bool(Gv.wants(N)), "I. ... recorded as %s.txt, nothing more this session" % n)
    check(not bool(Gv.wants(N)), "I. a world switch (PlayerReadyEvent) wants nothing: the session mark")
    Gv.forget(N)
    check(bool(Gv.wants(N)) and plan(N, 0) == 1, "I. after a reconnect (forget): the record says done - no second item")
    KEYS[n] = n + "-p2"
    check(bool(Gv.wants(N)) and plan(N, 0) == 4, "I. switched to a NEW profile 2 (key uuid-p2): give one")
    give(N)
    check((n + "-p2.txt") in recs() and plan(N, 0) == 1, "I. ... recorded per profile")
    KEYS[n] = n
    check(not bool(Gv.wants(N)) and plan(N, 0) == 1, "I. back on profile 1: nothing")
    KEYS[n] = n + "-p3"
    check(plan(N, 1) == 1 and (n + "-p3.txt") in recs(), "I. profile 3 already holds the item (anywhere): recorded, none given")
    KEYS[n] = n + "-p4"
    br.put("profile:busy:" + n, Boolean.TRUE)
    check(plan(N, 0) == 2 and plan(N, 1) == 2 and (n + "-p4.txt") not in recs() and bool(Gv.wants(N)),
          "I. profile:busy: wait - nothing recorded, the held count is not trusted, still wanted")
    br.remove("profile:busy:" + n)
    check(plan(N, 0) == 4, "I. busy over: give one")
    give(N)
    check(plan(N, -1) == 1, "I. ... then nothing (even without a player entity)")
    KEYS[n] = n + "-p5"
    check(plan(N, -1) == 2 and (n + "-p5.txt") not in recs(), "I. no player entity yet: retry later, nothing recorded")
    # an old (0.1 - 0.3.3) per-player flag: the profile active at the first 0.3.4 sight counts as given, the others get it
    E = UUID.fromString("00000000-0000-0000-0000-0000000000e2")
    e = str(E)
    open(os.path.join(idir, "given", e + ".txt"), "w").write("menu item given 1790000000000\n")
    KEYS[e] = e + "-p2"
    check(plan(E, 0) == 1 and (e + "-p2.txt") in recs() and (e + ".txt") not in recs(),
          "I. old flag + currently on profile 2: profile 2 counts as given (no item even if they lost it)")
    KEYS[e] = e
    check(plan(E, 0) == 4, "I. ... their profile 1 gets the item when first used")
    give(E)
    E2 = UUID.fromString("00000000-0000-0000-0000-0000000000e3")
    e2 = str(E2)
    open(os.path.join(idir, "given", e2 + ".txt"), "w").write("menu item given 1790000000000\n")
    check(plan(E2, 1) == 1 and (e2 + ".txt") in recs(), "I. old flag + on profile 1, holding it: recorded, nothing given")
    KEYS[e2] = e2 + "-p2"
    check(plan(E2, 0) == 4, "I. ... a new profile 2 gets one")
    # a second server run: the migration looks again but finds a record - writes nothing
    Gv.SESSION.clear()
    Gv.CHECKED.clear()
    before = recs()
    KEYS[e] = e + "-p3"
    check(not bool(Gv.migrate(E, e + "-p3")) and recs() == before, "I. next run: an old flag with a per-profile record migrates nothing")
    check(plan(E, 0) == 4, "I. ... so a later profile 3 gets its item")
    # bad keys from the bridge fall back to the UUID
    B9 = UUID.fromString("00000000-0000-0000-0000-0000000000b9")
    for badk in ("../evil", "a b", "x" * 81, "", "c:\\x"):
        KEYS[str(B9)] = badk
        check(str(Gv.key(B9)) == str(B9), "I. a bad storage key %r falls back to the UUID" % badk[:12])
    KEYS.pop(str(B9))
    br.remove("profile:fn:key")
    check(str(Gv.key(B9)) == str(B9), "I. without SkyyProfiles the key is the UUID")
    br.put("profile:fn:key", PKey())
    # the item switched off (Server Setup "Give the menu item")
    O = UUID.fromString("00000000-0000-0000-0000-0000000000f0")
    MC.GIVE_ITEM = False
    check(plan(O, 0) == 1 and (str(O) + ".txt") not in recs(), "I. giveItem off: nothing given, nothing recorded")
    MC.GIVE_ITEM = True
    # one pending GrantTask per player
    P = UUID.fromString("00000000-0000-0000-0000-0000000000c1")
    check(bool(Gv.claim(P, 1000)) and not bool(Gv.claim(P, 2000)) and bool(Gv.claim(P, 92000)), "I. claim: one pending task, stale after 90 s")
    Gv.PENDING.remove(P)
    check(bool(Gv.claim(P, 92001)), "I. claim again after the task released it")
    # forget / retainOnline keep other players' marks
    Gv.SESSION.clear()
    Gv.SESSION.put(n, Boolean.TRUE)
    Gv.SESSION.put(n + "-p2", Boolean.TRUE)
    Gv.SESSION.put(e, Boolean.TRUE)
    Gv.READY.put(N, Boolean.TRUE)
    Gv.forget(N)
    check(not bool(Gv.SESSION.containsKey(n)) and not bool(Gv.SESSION.containsKey(n + "-p2")) and bool(Gv.SESSION.containsKey(e))
          and not bool(Gv.READY.containsKey(N)), "I. forget drops only that player's marks")
    Gv.SESSION.put(n + "-p2", Boolean.TRUE)
    Gv.READY.put(N, Boolean.TRUE)
    Gv.READY.put(E, Boolean.TRUE)
    Gv.retainOnline(jset(E), jset(e))
    check(not bool(Gv.SESSION.containsKey(n + "-p2")) and bool(Gv.SESSION.containsKey(e)) and not bool(Gv.READY.containsKey(N))
          and bool(Gv.READY.containsKey(E)), "I. retainOnline keeps online players' marks only")
    # GrantTask.grantNow without a player entity (bare JVM): retry, nothing written; an already recorded profile: nothing to do
    Gv.SESSION.clear()
    Q = UUID.fromString("00000000-0000-0000-0000-0000000000d4")
    gt = GT(pref(Q))
    check(int(gt.grantNow(Q)) == 2 and (str(Q) + ".txt") not in recs(), "I. GrantTask.grantNow without a player entity: retry, nothing recorded")
    Gv.markGiven(str(Q))
    check(int(gt.grantNow(Q)) == 1, "I. GrantTask.grantNow for a recorded profile: nothing to do")
    _mt = os.path.getmtime(os.path.join(idir, "given-profile", str(Q) + ".txt"))
    _by = open(os.path.join(idir, "given-profile", str(Q) + ".txt"), "rb").read()
    check(bool(Gv.markGiven(str(Q))) and os.path.getmtime(os.path.join(idir, "given-profile", str(Q) + ".txt")) == _mt
          and open(os.path.join(idir, "given-profile", str(Q) + ".txt"), "rb").read() == _by, "I. markGiven never rewrites a record")
    check(not [f for f in recs() if f.endswith(".tmp")], "I. no temp files left")

    # ---------------- J. two starts on scratch COPIES of the live Skyy_SkyyMenu data: J1 as it is today, J2 as 0.3.3 left it
    # 0.3.5: the 0.3.4 check assumed data no SkyyMenu 0.3.4 had seen yet (it expected the given-profile folder and a record for EVERY old
    # flag to be new), so it failed once 0.3.4 had run on the live world. What a start must do is now derived from the copy itself.
    live_menu = os.path.join(LIVE_MODS, "Skyy_SkyyMenu")
    if not os.path.isdir(live_menu):
        print("J. no live Skyy_SkyyMenu folder at %s - skipped" % live_menu)
    else:
        JST = {"players": None}

        def active_key(us):
            """SkyyProfiles' storage key of the profile active in the copy (tools/PROFILES-CONTRACT.md: <uuid> = profile 1)"""
            f = os.path.join(JST["players"], us + ".properties")
            act = "1"
            if os.path.isfile(f):
                for line in open(f, encoding="utf-8", errors="ignore"):
                    if line.startswith("active="):
                        act = line.split("=", 1)[1].strip()
            return us if act in ("", "1") else us + "-p" + act

        @JImplements("java.util.function.Function")
        class ProfKey:
            @JOverride
            def apply(self, u):
                return active_key(str(u))
        AST = JN("AdmSaveTask")
        live_prof = os.path.join(LIVE_MODS, "Skyy_SkyyProfiles", "players")
        GPK = os.path.join("Skyy_SkyyMenu", "given-profile")
        for jn, strip in (("J1", False), ("J2", True)):
            jw = os.path.join(SCRATCH, "livecopy-" + jn.lower())
            shutil.copytree(live_menu, os.path.join(jw, "Skyy_SkyyMenu"))
            if os.path.isdir(live_prof):
                shutil.copytree(live_prof, os.path.join(jw, "Skyy_SkyyProfiles", "players"))
            menu = os.path.join(jw, "Skyy_SkyyMenu")
            players = os.path.join(jw, "Skyy_SkyyProfiles", "players")
            gp = os.path.join(menu, "given-profile")
            if strip:
                shutil.rmtree(gp, ignore_errors=True)      # J2: no per-profile record yet = the folder as SkyyMenu 0.3.3 left it
            JST["players"] = players
            br.put("profile:fn:key", ProfKey())

            def tree():
                out = {}
                for dp, dn, fn in os.walk(jw):
                    for f in fn:
                        p = os.path.join(dp, f)
                        out[os.path.relpath(p, jw)] = (open(p, "rb").read(), os.path.getmtime(p))
                    for d in dn:
                        out[os.path.relpath(os.path.join(dp, d), jw) + os.sep] = None
                return out

            def start():
                for mp in (Gv.SESSION, Gv.CHECKED, Gv.READY, Gv.PENDING, Gv.INFLIGHT):
                    mp.clear()
                MC.FILE = Paths.get(os.path.join(menu, "config.properties"))
                MC.init()
                SetReg.ADMIN_FILE = Paths.get(os.path.join(menu, "settings-defaults.properties"))
                SetReg.loadAdmin(True)
                AST.BASE = Paths.get(menu)
                AST.ensureDirs()
                Gv.DIR = Paths.get(gp)
                Gv.LEGACY = Paths.get(os.path.join(menu, "given"))
                uu = set()
                for d in (os.path.join(menu, "given"), players):
                    if os.path.isdir(d):
                        for f in os.listdir(d):
                            if re.match(r"^[0-9a-f-]{36}\.", f):
                                uu.add(f[:36])
                res = {}
                for us in sorted(uu):
                    u = UUID.fromString(us)
                    res[us] = (str(Gv.key(u)), plan(u, 0))      # held 0 = the worst case: they lost the item
                return res
            gdir = os.path.join(menu, "given")
            legacy = sorted(f[:36] for f in os.listdir(gdir) if re.match(r"^[0-9a-f-]{36}\.txt$", f)) if os.path.isdir(gdir) else []
            recs0 = set(f for f in os.listdir(gp) if f.endswith(".txt")) if os.path.isdir(gp) else set()

            def has_any(us):        # = Given.hasAnyFor: a record of ANY profile of that player (<uuid>.txt or <uuid>-p<N>.txt)
                return (us + ".txt") in recs0 or any(r.startswith(us + "-p") for r in recs0)
            t0 = tree()
            r1 = start()
            t1 = tree()
            give_on = bool(MC.GIVE_ITEM)
            # the one-time migration still owed (0.3.4 rule): an old flag + no record of any profile -> ONE record for the profile active now
            mig = [us for us in legacy if not has_any(us)] if give_on else []

            def want_plan(us):
                if not give_on or (active_key(us) + ".txt") in recs0 or us in mig:
                    return 1        # the current profile already got the item (record, or the old flag migrated now): nothing to give
                return 4            # a profile that never got it (0.3.4: every other profile gets the item the first time it is used)
            want_new = sorted([os.path.join(GPK, active_key(us) + ".txt") for us in mig] + ([GPK + os.sep] if mig and (GPK + os.sep) not in t0 else []))
            print("%s. live copy%s: %d old flag(s) %s, records before %s, giveItem %s, migrations owed %s, start 1: %s" %
                  (jn, " without given-profile/" if strip else "", len(legacy), legacy, sorted(recs0), give_on, mig, r1))
            check(set(r1) >= set(legacy), "%s. every player with an old flag was looked at" % jn)
            check(all(r1[us][0] == active_key(us) for us in r1), "%s. Given.key = the active profile's storage key for every player" % jn)
            bad = dict((us, (r1[us][1], want_plan(us))) for us in r1 if r1[us][1] != want_plan(us))
            check(not bad, "%s. start 1: what each player gets = the 0.3.4 rule (got, want): %s" % (jn, bad))
            check(all(r1[us][1] == 1 for us in legacy if us in mig or (active_key(us) + ".txt") in recs0),
                  "%s. start 1: no player with an old flag gets a second item on a profile that already got one" % jn)
            new_files = sorted(k for k in t1 if k not in t0)
            changed = sorted(k for k in t0 if k in t1 and t0[k] != t1[k])
            check(new_files == want_new and not changed and not [k for k in t0 if k not in t1],
                  "%s. start 1 writes exactly the owed records (the CURRENT profile's key) and nothing else: new %s, want %s, changed %s" %
                  (jn, new_files, want_new, changed))
            if strip:
                check(bool(legacy) and sorted(mig) == legacy and all(r1[us][1] == 1 for us in legacy),
                      "J2. the 0.3.3 data: every old flag migrates once, nobody with an old flag gets a second item")
            r2 = start()
            t2 = tree()
            check(r2 == r1, "%s. start 2: every player gets the same answer, no new grant: %s" % (jn, r2))
            check(t2 == t1, "%s. start 2: no file churn (every byte and modification time unchanged)" % jn)
        br.put("profile:fn:key", PKey())

    # ---------------- K. class compare 0.3.5 -> 0.3.6 (the stuck-page fix + the menu data)
    CPc = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IPc = JClass("javassist.bytecode.InstructionPrinter")
    BR_RE = re.compile(r"^(if\w*|goto(?:_w)?|jsr(?:_w)?) (\d+)$")

    def ct(b):
        return CPc(False).makeClass(BAIS(JArray(JByte)(b)))

    def code_of(m):
        """a method's instructions, constants resolved, byte offsets read as instruction numbers (a bigger constant pool turns a few
        ldc into ldc_w and moves every later branch offset - an encoding difference, not a code difference; the SkyyBank 0.1.6 rule)"""
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        cp = mi.getConstPool()
        if ca is None:
            return ["<no code>"]
        it, raw = ca.iterator(), []
        while it.hasNext():
            pos = it.next()
            raw.append((pos, str(IPc.instructionString(it, pos, cp))))
        at = dict((pos, i) for i, (pos, _t) in enumerate(raw))
        at[int(ca.getCodeLength())] = len(raw)
        out = []
        for pos, t in raw:
            t = re.sub(r"#\d+ = ", "", t).replace("ldc_w ", "ldc ")
            mm = BR_RE.match(t)
            if mm:
                t = "%s @%d" % (mm.group(1), at.get(int(mm.group(2)), -1))
            elif t.startswith("tableswitch") or t.startswith("lookupswitch"):
                t = re.sub(r"(default|-?\d+): (\d+)", lambda x: "%s: @%d" % (x.group(1), at.get(int(x.group(2)), -1)), t)
            out.append(t)
        et = ca.getExceptionTable()
        for i in range(et.size()):
            ctp = et.catchType(i)
            out.append("try @%d @%d @%d %s" % (at.get(et.startPc(i), -1), at.get(et.endPc(i), -1), at.get(et.handlerPc(i), -1),
                                              cp.getClassInfo(ctp) if ctp else "any"))
        return out

    def methods(c):
        return dict((str(m.getMethodInfo().getName()) + str(m.getSignature()), code_of(m))
                    for m in list(c.getDeclaredMethods()) + list(c.getDeclaredConstructors()) +
                    ([c.getClassInitializer()] if c.getClassInitializer() is not None else []))

    def fields_of(c):
        return set((str(f.getName()), str(f.getSignature()), int(f.getModifiers())) for f in c.getDeclaredFields())

    def diff(cn):
        mo, mn = methods(ct(CBY["old"][PKG + cn])), methods(ct(CBY["new"][PKG + cn]))
        return (sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k]), sorted(k.split("(")[0] for k in mn if k not in mo),
                sorted(k.split("(")[0] for k in mo if k not in mn), sorted(k.split("(")[0] for k in mo if k in mn and mo[k] == mn[k]))
    STR_RE = re.compile(r'".*"', re.S)
    ARR_OPS = re.compile(r"^(dup|bipush|sipush|iconst_\w+|ldc|ldc_w|aastore|iastore|anewarray|newarray)\b")

    def data_only(a, b):
        """two class files with the same fields + methods whose code differs only in string constants -> (True, methods that differ)"""
        ca_, cb_ = ct(a), ct(b)
        ma_, mb_ = methods(ca_), methods(cb_)
        if fields_of(ca_) != fields_of(cb_) or set(ma_) != set(mb_):
            return False, "fields / methods differ"
        dif = sorted(k for k in ma_ if ma_[k] != mb_[k])
        def norm(k, ls):
            ls = [STR_RE.sub('"S"', l) for l in ls]
            # a static data initialiser: only the array-literal stores may differ (more / fewer elements); every other instruction
            # (the fields it sets, the calls it makes) must be the same, in the same order
            return [l for l in ls if not ARR_OPS.match(l)] if k.startswith("<clinit>") else ls
        bad = [k for k in dif if norm(k, ma_[k]) != norm(k, mb_[k])]
        return not bad, ("code differs beyond strings in %s" % bad) if bad else [k.split("(")[0] for k in dif]
    if not os.path.isfile(OLDJAR):
        check(False, "K. no %s to compare with" % OLDJAR)
    else:
        za, zb = zipfile.ZipFile(OLDJAR), zipfile.ZipFile(JAR)
        na, nb = set(za.namelist()), set(zb.namelist())
        ch = sorted(x for x in na & nb if za.read(x) != zb.read(x))
        print("K. %s -> %s: changed %s; added %s; removed %s" % (OLDVER, VERSION, [x.split("/")[-1] for x in ch],
                                                              sorted(x.split("/")[-1] for x in nb - na), sorted(na - nb)))
        P_ = "com/skyy/menu/"
        NEWC = sorted(P_ + c + ".class" for c in ("PageGuard", "StaleTask", "MenuWatch"))
        CODEC = [P_ + c + ".class" for c in ("MenuData", "MenuPage", "CloseTask", "RefreshTask", "MenuQuit", "SkyyMenuPlugin")]
        vonly = [P_ + "CfgFn.class", "manifest.json"]
        DATAK = [P_ + "CfgRows.class", P_ + "SetReg.class"]       # 0.3.7: the defaults template text (gear.critFx) - string constants only
        check(sorted(nb - na) == NEWC and not (na - nb), "K. added exactly PageGuard, StaleTask, MenuWatch; nothing removed: %s / %s" % (
            sorted(nb - na), sorted(na - nb)))
        for x in DATAK:
            ok_, why_ = data_only(za.read(x), zb.read(x))
            check(ok_, "K. %s: only string constants differ from 0.3.5: %s" % (x.split("/")[-1], why_))
        check(sorted(ch) == sorted(CODEC + vonly + DATAK), "K. changed exactly %s: %s" % (sorted(x.split("/")[-1] for x in CODEC + vonly + DATAK),
                                                                             sorted(x.split("/")[-1] for x in ch)))
        for x in vonly:
            check(x in na and x in nb and za.read(x).replace(OLDVER.encode(), VERSION.encode()) == zb.read(x),
                  "K. %s differs from %s only by %s -> %s" % (x.split("/")[-1], OLDVER, OLDVER, VERSION))
        same = sorted(x for x in na & nb if x not in vonly and x not in CODEC and x not in DATAK)
        for x in same:
            check(za.read(x) == zb.read(x), "K. %s byte-identical to %s" % (x.split("/")[-1], OLDVER))
        ncls = len([x for x in na if x.endswith(".class")])
        nsame = len([x for x in same if x.endswith(".class")])
        print("K. %d of %d 0.3.5 classes byte-identical (+ the item JSON and server.lang); %d changed, %d new" % (
            nsame, ncls, len([x for x in ch if x.endswith(".class")]), len(NEWC)))
        check(nsame == ncls - 9, "K. every other class byte-identical (%d of %d)" % (nsame, ncls))
        check("Server/Item/Items/Utility/Skyy_Menu.json" in same and "Server/Languages/en-US/server.lang" in same, "K. the item JSON and server.lang unchanged")
        cmd_ = ct(CBY["old"][PKG + "MenuData"])
        check(fields_of(cmd_) == fields_of(ct(CBY["new"][PKG + "MenuData"])), "K. MenuData: the same fields")
        dchg, dadd, dgone, dsame = diff("MenuData")
        check(dchg == ["<clinit>"] and not dadd and not dgone, "K. MenuData: only the static data initialiser <clinit> differs: %s %s %s" % (dchg, dadd, dgone))
        fo, fn_ = fields_of(ct(CBY["old"][PKG + "MenuPage"])), fields_of(ct(CBY["new"][PKG + "MenuPage"]))
        NEWF = {"world", "joinSeen", "lastSend", "watching", "probeNonce", "probeSeen", "heals", "watchFails", "SETTLE", "HEAL_ANSWERS"}
        check(fo <= fn_ and set(n for n, _s, _m in fn_ - fo) == NEWF, "K. MenuPage: 0.3.5's fields + %s: %s" % (sorted(NEWF), sorted(fn_ - fo)))
        pchg, padd, pgone, psame = diff("MenuPage")
        check(pchg == ["build", "clearGrid", "handleDataEvent"] and padd == ["changedWorld", "watchFail", "watchTick", "who"] and not pgone,
              "K. MenuPage: changed build / clearGrid / handleDataEvent, new who / changedWorld / watchFail / watchTick: %s %s %s" % (pchg, padd, pgone))
        _mo = methods(ct(CBY["old"][PKG + "MenuPage"]))
        check(len(psame) == len(_mo) - 3 and "click()" not in psame and "runCmd" in psame and "closePage" in psame and "click" in psame,
              "K. MenuPage: every other method (%d of %d, incl. click, runCmd, closePage, teleport, fill) instruction-identical to 0.3.5" % (
                  len(psame), len(_mo)))
        for cn, want in (("CloseTask", ["run"]), ("RefreshTask", ["run"]), ("MenuQuit", ["accept"]), ("SkyyMenuPlugin", ["setup", "shutdown"])):
            c_, a_, g_, s_ = diff(cn)
            check(c_ == want and not a_ and not g_, "K. %s: only %s changed: %s (added %s, gone %s)" % (cn, want, c_, a_, g_))
        # what the changed methods gained, read back from the bytecode
        cn_new = methods(ct(CBY["new"][PKG + "CloseTask"]))
        crun = [v for k, v in cn_new.items() if k.startswith("run(")][0]
        check(any("PageGuard.forget" in l for l in crun) and any("MenuPage.changedWorld" in l for l in crun)
              and any("MenuPage.closePage" in l for l in crun), "K. CloseTask.run: changedWorld -> PageGuard.forget, else closePage")
        rn_new = methods(ct(CBY["new"][PKG + "RefreshTask"]))
        rrun = [v for k, v in rn_new.items() if k.startswith("run(")][0]
        check(any("PageGuard.forget" in l for l in rrun) and any("MenuPage.refresh" in l for l in rrun), "K. RefreshTask.run: forget, else refresh")
        pl_new = methods(ct(CBY["new"][PKG + "SkyyMenuPlugin"]))
        psetup = [v for k, v in pl_new.items() if k.startswith("setup(")][0]
        _ex = [i for i in range(1, len(psetup)) if "putstatic" in psetup[i] and "PageGuard.EXEC" in psetup[i]
               and "HytaleServer.SCHEDULED_EXECUTOR" in psetup[i - 1]]
        check(len(_ex) == 1 and any("AddPlayerToWorldEvent" in l for l in psetup) and any("PageGuard.STOP" in l for l in psetup),
              "K. SkyyMenuPlugin.setup: PageGuard.STOP, EXEC = HytaleServer.SCHEDULED_EXECUTOR, registerGlobal(AddPlayerToWorldEvent, PageGuard)")
        psd = [v for k, v in pl_new.items() if k.startswith("shutdown(")][0]
        check(any("putstatic" in l and "PageGuard.STOP" in l for l in psd), "K. SkyyMenuPlugin.shutdown: PageGuard.STOP")
        mf = json.loads(zb.read("manifest.json").decode("utf-8"))
        check(VERSION in json.dumps(mf) and OLDVER not in json.dumps(mf), "K. manifest.json names %s" % VERSION)
        za.close()
        zb.close()
    # ---------------- K3 (0.3.8). class compare 0.3.7 (the live pin) -> 0.3.8: data / text only
    if not os.path.isfile(PREVJAR):
        check(False, "K3. no %s to compare with" % PREVJAR)
    else:
        zp, zb = zipfile.ZipFile(PREVJAR), zipfile.ZipFile(JAR)
        np_, nb = set(zp.namelist()), set(zb.namelist())
        ch2 = sorted(x for x in np_ & nb if zp.read(x) != zb.read(x))
        P_ = "com/skyy/menu/"
        DATA2 = [P_ + "MenuData.class"]
        VER2 = [P_ + c + ".class" for c in ("CfgRows", "CfgFn")] + ["manifest.json"]
        PLG = P_ + "SkyyMenuPlugin.class"
        check(np_ == nb, "K3. the same entries as 0.3.7: %s" % sorted(np_ ^ nb))
        check(ch2 == sorted(DATA2 + VER2 + [PLG]), "K3. changed exactly %s: %s" % (sorted(x.split("/")[-1] for x in DATA2 + VER2 + [PLG]), [x.split("/")[-1] for x in ch2]))
        for x in VER2:
            check(zp.read(x).replace(PREVVER.encode(), VERSION.encode()) == zb.read(x), "K3. %s differs from %s only by the version" % (x.split("/")[-1], PREVVER))
        kitre = re.compile(rb"config kit 1\.1 [0-9a-f]{12}")
        check(kitre.sub(b"KIT", zp.read(PLG).replace(PREVVER.encode(), VERSION.encode())) == kitre.sub(b"KIT", zb.read(PLG)),
              "K3. SkyyMenuPlugin differs only by the version and the config kit blob id of its ready line")
        cp_, cn_ = ct(zp.read(DATA2[0])), ct(zb.read(DATA2[0]))
        mo2, mn2 = methods(cp_), methods(cn_)
        chg = sorted(k.split("(")[0] for k in mo2 if k in mn2 and mo2[k] != mn2[k])
        ok_, why_ = data_only(zp.read(DATA2[0]), zb.read(DATA2[0]))
        check(ok_ and chg == ["<clinit>"] and set(mo2) == set(mn2) and fields_of(cp_) == fields_of(cn_),
              "K3. MenuData: the same fields and methods, only the static data initialiser differs: %s %s" % (chg, why_))
        same2 = [x for x in np_ & nb if x not in ch2]
        print("K3. %s -> %s: %d entries byte-identical; data only: MenuData; version string only: %s; SkyyMenuPlugin: version + kit blob id" % (
            PREVVER, VERSION, len(same2), ", ".join(x.split("/")[-1] for x in VER2)))
        zp.close()
        zb.close()

    # ================================================================================================ P. the stuck-page flows (engine PageManager)
    def jf(c, name):
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    HP = CPc(False)
    HP.appendSystemPath()
    HP.appendClassPath(B.SERVER_JAR)
    HP.appendClassPath(JAR)
    CtNewMethod, CtNewConstructor, CtField = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")

    def hclass(name, sup, ctor, fields=(), meths=(), ifaces=(), out=None):
        c = HP.makeClass(name, HP.get(sup)) if sup else HP.makeClass(name)
        for i_ in ifaces:
            c.addInterface(HP.get(i_))
        for s_ in fields:
            c.addField(CtField.make(s_, c))
        if ctor:
            c.addConstructor(CtNewConstructor.make(ctor, c))
        for s_ in meths:
            c.addMethod(CtNewMethod.make(s_, c))
        c.writeFile(out or hcls)

    PGE = "com.hypixel.hytale.server.core.entity.entities.player.pages"
    hclass("skyymenuharness.Net", "com.hypixel.hytale.server.core.io.PacketHandler",
           "public Net() { super((com.hypixel.hytale.protocol.io.ChannelConnection) null, (com.hypixel.hytale.server.core.io.ProtocolVersion) null); }",
           ["public java.util.ArrayList sent;"],
           ["public boolean writePacket(com.hypixel.hytale.protocol.ToClientPacket p, boolean c) {\n"
            "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  this.sent.add(p);\n  return true;\n}",
            "public void accept(com.hypixel.hytale.protocol.ToServerPacket p) { }",
            "public String getIdentifier() { return \"skyymenuharness\"; }"])
    hclass("com.hypixel.hytale.component.SkyyMenuTestStore", "com.hypixel.hytale.component.Store",
           "public SkyyMenuTestStore() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
           "(com.hypixel.hytale.component.IResourceStorage) null); }",
           ["public java.util.IdentityHashMap comps;"],
           ["public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, "
            "com.hypixel.hytale.component.ComponentType t) {\n  if (this.comps == null) return null;\n"
            "  java.util.Map m = (java.util.Map) this.comps.get(r);\n  if (m == null) return null;\n"
            "  return (com.hypixel.hytale.component.Component) m.get(t);\n}"])
    # the player's components between worlds (what PlayerRef.removeFromStore keeps and AddPlayerToWorldEvent carries)
    hclass("com.hypixel.hytale.component.SkyyMenuTestHolder", "com.hypixel.hytale.component.Holder", "public SkyyMenuTestHolder() { super(); }",
           ["public java.util.IdentityHashMap comps;"],
           ["public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.ComponentType t) {\n"
            "  if (this.comps == null) return null;\n  return (com.hypixel.hytale.component.Component) this.comps.get(t);\n}"])
    hclass("skyymenuharness.World", "com.hypixel.hytale.server.core.universe.world.World",
           "public World() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }",
           ["public java.util.concurrent.ConcurrentLinkedQueue tasks;"],
           ["public void execute(java.lang.Runnable r) {\n  if (this.tasks == null) this.tasks = new java.util.concurrent.ConcurrentLinkedQueue();\n"
            "  this.tasks.add(r);\n}"])
    PAGE_BUILD = ("public void build(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.server.core.ui.builder.UICommandBuilder b, "
                  "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder e, com.hypixel.hytale.component.Store s) { "
                  "b.appendInline((String) null, \"Group #SkyyPStandIn { Anchor: (Width: 100, Height: 100); }\"); "
                  "e.addEventBinding(com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType.Activating, \"#SkyyPStandIn\", "
                  "com.hypixel.hytale.server.core.ui.builder.EventData.of(\"m\", \"tile\")); }")
    PAGE_CLICK = ("public void handleDataEvent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s, String d) { "
                  "this.clicks = this.clicks + 1; }")
    # the stand-in Bank page answers a click like a real page does (a redraw - the client stops waiting)
    PAGE_ANSWER = ("public void handleDataEvent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s, String d) { "
                   "this.clicks = this.clicks + 1; rebuild(); }")
    PAGE_CTOR = ("public %s(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr, "
                 "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime.CanDismiss); }")
    # a page with the engine's empty onDismiss (a stand-in for the Bank / Vault / any mod's page), one with its own onDismiss (records what
    # the engine passes), one whose onDismiss throws
    hclass("skyymenuharness.PlainPage", PGE + ".CustomUIPage", PAGE_CTOR % "PlainPage", ["public int clicks;"], [PAGE_BUILD, PAGE_ANSWER])
    hclass("skyymenuharness.OwnPage", PGE + ".CustomUIPage", PAGE_CTOR % "OwnPage",
           ["public int clicks;", "public int dCount;", "public Object dRef;", "public Object dStore;"],
           [PAGE_BUILD, PAGE_CLICK, "public void onDismiss(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s) { "
                                    "this.dCount = this.dCount + 1; this.dRef = r; this.dStore = s; }"])
    hclass("skyymenuharness.ThrowPage", PGE + ".CustomUIPage", PAGE_CTOR % "ThrowPage", ["public int clicks;"],
           [PAGE_BUILD, PAGE_CLICK, "public void onDismiss(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s) { "
                                    "throw new java.lang.IllegalStateException(\"harness onDismiss failure\"); }"])
    # the command system the menu talks to: resolveCommand + handleCommand (the future keeps what the menu chains on it: the CloseTask)
    hclass("skyymenuharness.RecFuture", "java.util.concurrent.CompletableFuture", "public RecFuture() { super(); }",
           ["public java.util.function.BiConsumer act;"],
           ["public java.util.concurrent.CompletableFuture whenComplete(java.util.function.BiConsumer a) { this.act = a; return this; }"])
    hclass("skyymenuharness.Cmd", "com.hypixel.hytale.server.core.command.system.AbstractCommand", "public Cmd() { super(\"x\", \"y\"); }", [],
           ["public boolean hasPermission(com.hypixel.hytale.server.core.command.system.CommandSender s) { return true; }",
            "protected java.util.concurrent.CompletableFuture execute(com.hypixel.hytale.server.core.command.system.CommandContext c) { return null; }"])
    hclass("skyymenuharness.Cmds", "com.hypixel.hytale.server.core.command.system.CommandManager", "public Cmds() { super(); }",
           ["public java.util.HashMap cmds;", "public java.util.ArrayList lines;", "public skyymenuharness.RecFuture last;"],
           ["public com.hypixel.hytale.server.core.command.system.AbstractCommand resolveCommand(String n) {\n"
            "  return this.cmds == null ? null : (com.hypixel.hytale.server.core.command.system.AbstractCommand) this.cmds.get(n);\n}",
            "public java.util.concurrent.CompletableFuture handleCommand(com.hypixel.hytale.server.core.command.system.CommandSender s, String line) {\n"
            "  if (this.lines == null) this.lines = new java.util.ArrayList();\n  this.lines.add(line);\n"
            "  this.last = new skyymenuharness.RecFuture();\n  return this.last;\n}"])
    # the item assets a menu slot needs (new ItemStack(icon, 1) -> Item.getAssetMap().getAsset(id) -> max durability / quality index):
    # a stand-in AssetStore whose map answers every id with one plain Item (the menu only draws icons; nothing else reads the item)
    hclass("skyymenuharness.ItemMap", "com.hypixel.hytale.assetstore.map.DefaultAssetMap", "public ItemMap() { super(); }",
           ["public com.hypixel.hytale.assetstore.JsonAsset item;", "public java.util.HashSet asked;"],
           ["public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object k) {\n"
            "  if (this.asked == null) this.asked = new java.util.HashSet();\n  this.asked.add(k);\n  return this.item;\n}"])
    hclass("skyymenuharness.Items", "com.hypixel.hytale.assetstore.AssetStore",
           "public Items() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }",
           ["public com.hypixel.hytale.assetstore.AssetMap map;"],
           ["public com.hypixel.hytale.assetstore.AssetMap getAssetMap() { return this.map; }"])
    hclass("skyymenuharness.LookupIn", None, None, [],
           ["public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
            "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}"])
    # X control: the SkyyUiProbe 0.3 mistake - a class that is no page calling a page's protected rebuild(); its own folder, loaded
    # under the 0.3.6 jar's loader so it resolves MenuPage like the mod's classes do
    hcls2 = os.path.join(SCRATCH, "hclasses2")
    os.makedirs(hcls2, exist_ok=True)
    hclass("skyymenuharness.BadCaller", None, None, [], ["public static void poke(com.skyy.menu.MenuPage p) { p.rebuild(); }"], out=hcls2)

    NET, TSC, THL, HW = (JClass("skyymenuharness.Net"), JClass("com.hypixel.hytale.component.SkyyMenuTestStore"),
                         JClass("com.hypixel.hytale.component.SkyyMenuTestHolder"), JClass("skyymenuharness.World"))
    PLAIN, OWN, THROW = JClass("skyymenuharness.PlainPage"), JClass("skyymenuharness.OwnPage"), JClass("skyymenuharness.ThrowPage")
    PMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    WMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
    Uni = JClass("com.hypixel.hytale.server.core.universe.Universe")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    STc = JClass("com.hypixel.hytale.component.Store")
    CTc = JClass("com.hypixel.hytale.component.ComponentType")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    CPE = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageEvent")
    CPT = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageEventType")
    PAGE_E = JClass("com.hypixel.hytale.protocol.packets.interface_.Page")
    CPK = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPage")
    ATW = JClass("com.hypixel.hytale.server.core.event.events.player.AddPlayerToWorldEvent")
    PDE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
    CMGRc = JClass("com.hypixel.hytale.server.core.command.system.CommandManager")
    IdMap = JClass("java.util.IdentityHashMap")
    System = JClass("java.lang.System")
    nxt = [900]

    def ctype():
        c = CTc()
        nxt[0] += 1
        jf(CTc.class_, "index").setInt(c, nxt[0])
        jf(CTc.class_, "hashCode").setInt(c, nxt[0])
        return c

    CT_PR, CT_PLA = ctype(), ctype()
    uni = U.allocateInstance(Uni.class_)
    jf(Uni.class_, "playerRefComponentType").set(uni, CT_PR)
    WORLDS = JClass("java.util.concurrent.ConcurrentHashMap")()
    jf(Uni.class_, "worldsByUuid").set(uni, WORLDS)
    jf(Uni.class_, "players").set(uni, ArrayList())
    jf(Uni.class_, "instance").set(None, uni)
    em = U.allocateInstance(EMc.class_)
    jf(EMc.class_, "playerComponentType").set(em, CT_PLA)
    jf(EMc.class_, "instance").set(None, em)

    def world():
        w = U.allocateInstance(HW.class_)
        u = UUID.randomUUID()
        WORLDS.put(u, w)
        return w, u
    W1, W1U = world()
    W2, W2U = world()
    W3, W3U = world()
    # the command system: /island and /hub resolve (the teleport itself is the harness's world change), /tpaccept too
    CM = U.allocateInstance(JClass("skyymenuharness.Cmds").class_)
    CM.cmds = HashMap()
    CM.lines = ArrayList()
    for cn_ in ("island", "hub", "tpaccept", "tpdeny", "sacks"):
        CM.cmds.put(cn_, U.allocateInstance(JClass("skyymenuharness.Cmd").class_))
    jf(CMGRc.class_, "instance").set(None, CM)
    ITc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    IMAP = U.allocateInstance(JClass("skyymenuharness.ItemMap").class_)
    IMAP.item = U.allocateInstance(ITc.class_)
    ISTORE = U.allocateInstance(JClass("skyymenuharness.Items").class_)
    ISTORE.map = IMAP
    jf(ITc.class_, "ASSET_STORE").set(None, ISTORE)
    # the log lines of both jars (MenuUtil.LOG of each loader -> one subscriber)
    HLB, HL = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend"), JClass("com.hypixel.hytale.logger.HytaleLogger")
    RECS = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    HLB.subscribe(RECS)
    for k in ("old", "new"):
        JV(k, "MenuUtil").LOG = HL.get("SkyyMenuHarness" + k)

    def logs():
        out = []
        for i in range(int(RECS.size())):
            r = RECS.get(i)
            try:
                out.append("%s %s" % (r.getLevel(), r.getMessage()))
            except Exception:
                out.append(str(r))
        return [x for x in out if "[SkyyMenu]" in x]

    PG = JN("PageGuard")
    PG.STOP = False
    PG.EXEC = None
    SKP = UUID.fromString("00000000-0000-0000-0000-0000000000a7")      # the flows' player (a plain player: no admin nodes)

    class Pl:
        pass

    def store_for(P, w):
        st = U.allocateInstance(TSC.class_)
        ref = U.allocateInstance(REFc.class_)
        jf(REFc.class_, "store").set(ref, st)
        jf(REFc.class_, "index").setInt(ref, 7)
        comps = IdMap()
        comps.put(CT_PR, P.pr)
        comps.put(CT_PLA, P.pl)
        allc = IdMap()
        allc.put(ref, comps)
        st.comps = allc
        es = U.allocateInstance(ESc.class_)
        jf(ESc.class_, "world").set(es, w)
        jf(STc.class_, "externalData").set(st, es)
        return ref, st

    def player(w=None, wu=None, u=SKP):
        """a stand-in player in world w: Store + Ref + PlayerRef + Player holding the engine's own PageManager / WindowManager"""
        P = Pl()
        P.pr = U.allocateInstance(PR.class_)
        jf(PR.class_, "uuid").set(P.pr, u)
        jf(PR.class_, "username").set(P.pr, "SkyyHarness")
        P.net = U.allocateInstance(NET.class_)
        jf(PR.class_, "packetHandler").set(P.pr, P.net)
        jf(PR.class_, "worldUuid").set(P.pr, wu if wu is not None else W1U)
        P.pl = U.allocateInstance(PLAc.class_)
        P.wm = WMc()
        P.wm.init(P.pr)
        P.pm = PMc()
        P.pm.init(P.pr, P.wm)
        jf(PLAc.class_, "windowManager").set(P.pl, P.wm)
        jf(PLAc.class_, "pageManager").set(P.pl, P.pm)
        P.ref, P.st = store_for(P, w if w is not None else W1)
        jf(PR.class_, "entity").set(P.pr, P.ref)
        P.world = w if w is not None else W1
        P.cl = Client(P)
        return P

    def acks(pm):
        return int(jf(PMc.class_, "customPageRequiredAcknowledgments").get(pm).get())

    def sent(net):
        return [] if net.sent is None else [net.sent.get(i) for i in range(int(net.sent.size()))]

    def kinds(ps):
        return [str(p.getClass().getSimpleName()) + ("(%s)" % str(p.key).rsplit(".", 1)[-1] if str(p.getClass().getSimpleName()) == "CustomPage" else
                                                     ("(%s)" % p.page if str(p.getClass().getSimpleName()) == "SetPage" else "")) for p in ps]

    class Client:
        """the game client as far as the engine's acknowledgement rule needs it (inferred - the SkyyBank 0.1.6 harness's model)"""

        def __init__(s, P):
            s.P = P
            s.page, s.seen, s.waiting, s.binds, s.errors = None, 0, False, {}, []

        def ack(s):
            try:
                s.P.pm.handleEvent(s.P.ref, s.P.st, CPE(CPT.Acknowledge, None))
            except Exception as e:
                s.errors.append(str(e))

        def pump(s):
            ps = sent(s.P.net)
            for p in ps[s.seen:]:
                kind = str(p.getClass().getSimpleName())
                if kind == "CustomPage":
                    if bool(p.isInitial) or (s.page is not None and str(p.key) == s.page):
                        s.page, s.waiting = str(p.key), False
                        if bool(p.clear) or bool(p.isInitial):
                            s.binds = dict((str(e.selector), (str(e.type), None if e.data is None else str(e.data), bool(e.locksInterface)))
                                           for e in p.eventBindings)
                        s.ack()
                elif kind == "SetPage":
                    if s.page is not None:
                        s.page, s.waiting = None, False
                        s.ack()
            s.seen = len(ps)

        def press(s, sel, slot=None):
            """click `sel` as the client does: the binding's EventData (+ SlotIndex for a grid slot)"""
            b = s.binds.get(sel)
            if b is None:
                raise KeyError("no binding for %s (%s)" % (sel, sorted(s.binds)))
            d = json.loads(b[1]) if b[1] else {}
            if slot is not None:
                d["SlotIndex"] = slot
            s.waiting = b[2]
            s.P.pm.handleEvent(s.P.ref, s.P.st, CPE(CPT.Data, json.dumps(d, separators=(",", ":"))))
            s.pump()

        def esc(s):
            if s.page is not None:
                b = [v for v in s.binds.values() if v[0] == "Dismissing"]
                s.page, s.waiting = None, False
                for v in b:
                    s.P.pm.handleEvent(s.P.ref, s.P.st, CPE(CPT.Data, v[1]))
                s.P.pm.handleEvent(s.P.ref, s.P.st, CPE(CPT.Dismiss, None))

    def leave(P, w, wu, k, guard=True):
        """the first half of a world change in the engine's order: PlayerRef.removeFromStore (the old ref invalid, the holder kept), then
        World.addPlayer = the new world id + AddPlayerToWorldEvent (0.3.6: the registered PageGuard listener runs here)"""
        jf(REFc.class_, "index").setInt(P.ref, -2147483648)
        jf(PR.class_, "entity").set(P.pr, None)
        h = U.allocateInstance(THL.class_)
        hc = IdMap()
        hc.put(CT_PR, P.pr)
        hc.put(CT_PLA, P.pl)
        h.comps = hc
        jf(PR.class_, "holder").set(P.pr, h)
        jf(PR.class_, "worldUuid").set(P.pr, wu)
        P.ev_counter = acks(P.pm)
        P.ev_sent = len(sent(P.net))
        if k == "new" and guard:
            JN("PageGuard")().accept(ATW(h, w, None))
        P.ev_after = acks(P.pm)
        P.ev_sent_after = len(sent(P.net))
        P.ev_page = P.pm.getCustomPage()

    def arrive(P, w):
        """the second half: onSetupPlayerJoining (clearCustomPageAcknowledgements; the client's JoinWorld drops its page), then
        onFinishPlayerJoining (addToStore: a new ref in the new world's store)"""
        P.pm.clearCustomPageAcknowledgements()
        P.cl.page, P.cl.waiting = None, False
        P.ref, P.st = store_for(P, w)
        jf(PR.class_, "entity").set(P.pr, P.ref)
        jf(PR.class_, "holder").set(P.pr, None)
        P.world = w

    def world_change(P, w, wu, k, guard=True):
        leave(P, w, wu, k, guard)
        arrive(P, w)

    def drain(*ws):
        for w in ws:
            if w.tasks is not None:
                w.tasks.clear()

    def run_world(w):
        """run what was handed to the world's thread (World.execute), in order, as the world thread would"""
        n = 0
        while w.tasks is not None and not w.tasks.isEmpty():
            t = w.tasks.poll()
            t.run()
            n += 1
        return n

    def open_page(P, pg):
        P.pm.openCustomPage(P.ref, P.st, pg)
        P.cl.pump()
        return pg

    def slot_of(menu, act):
        a = [None if x is None else str(x) for x in menu.acts]
        return a.index(act) if act in a else -1

    def next_page_works(P, k):
        """after a flow: a new SkyWynn Menu (/skymenu) - its Your Profile tile - and a stand-in page (e.g. the Bank) - its button"""
        m2 = open_page(P, JV(k, "MenuPage")(P.pr, "main"))
        sp = slot_of(m2, "profile")
        P.cl.press("#SkyyMGrid", slot=sp)
        menu_ok = str(m2.infoName) == "Your Profile"
        bk = open_page(P, PLAIN(P.pr))
        P.cl.press("#SkyyPStandIn")
        bank_ok = int(bk.clicks) == 1 and not P.cl.waiting
        P.cl.esc()
        return menu_ok, bank_ok

    RES = {}
    drain(W1, W2, W3)
    for k in ("old", "new"):
        V = OLDVER if k == "old" else VERSION
        MP = JV(k, "MenuPage")
        R = RES.setdefault(k, {})
        # ---- P1 THE ISLAND TILE: menu (Teleport) -> My Island -> /island = a world change -> the CloseTask the menu chained on it
        P = player()
        menu = open_page(P, MP(P.pr, "tp"))
        check(P.cl.page == PKG + "MenuPage" and acks(P.pm) == 0, "P1. %s: the menu (Teleport view) is open, every packet acknowledged" % V)
        si = slot_of(menu, "cmdc:island")
        CM.lines.clear()
        CM.last = None
        P.cl.press("#SkyyMGrid", slot=si)
        ct_ = CM.last.act if CM.last is not None else None
        check(si >= 0 and [str(x) for x in CM.lines] == ["island"] and ct_ is not None and str(ct_.getClass().getName()) == PKG + "CloseTask"
              and acks(P.pm) == 0, "P1. %s: the My Island tile ran /island (as the player) and chained its CloseTask on the command (grid "
              "emptied and acknowledged)" % V)
        world_change(P, W2, W2U, k)
        R["p1_event_forgot"] = P.ev_page is None
        n0 = len(sent(P.net))
        ct_.run()                                  # the scheduler-thread hop ~150 ms later: the player's world is W2 now
        hopped = W2.tasks is not None and W2.tasks.size() == 1
        run_world(W2)                              # its world part, on W2's thread
        P.cl.pump()
        new_pk = kinds(sent(P.net)[n0:])
        R["p1_pending"] = acks(P.pm)
        R["p1_packets"] = new_pk
        if k == "old":
            check(hopped and new_pk == ["SetPage(None)"] and R["p1_pending"] == 1,
                  "P1. %s (the live pin) REPRODUCES THE BUG: its CloseTask closed the stale menu on the new world with setPage(None) - 1 "
                  "acknowledgement the client never sends (%s, %d pending)" % (V, new_pk, R["p1_pending"]))
        else:
            check(R["p1_event_forgot"] and P.ev_after == P.ev_counter and P.ev_sent_after == P.ev_sent,
                  "P1. %s: PageGuard forgot the menu AT the world join (no packet, the counter untouched: %d -> %d)" % (V, P.ev_counter, P.ev_after))
            check(hopped and new_pk == [] and R["p1_pending"] == 0, "P1. %s: the CloseTask sends nothing on the new world, 0 pending (%s, %d)" % (
                V, new_pk, R["p1_pending"]))
        mok, bok = next_page_works(P, k)
        R["p1_next"] = (mok, bok)
        if k == "old":
            check(not mok and not bok, "P1. %s: ... and the NEXT pages ignore every click (a new SkyWynn Menu, a stand-in Bank page) - "
                  "Skyy's 'Loading...' (menu %s, bank %s)" % (V, mok, bok))
        else:
            check(mok and bok and acks(P.pm) == 0 and not P.cl.errors, "P1. %s: the next pages' clicks WORK (a new menu's Your Profile tile, "
                  "the stand-in Bank button), 0 pending (%s)" % (V, P.cl.errors))
        # P1b (0.3.6): the same flow WITHOUT the world-join event - the CloseTask's own world check forgets the menu
        if k == "new":
            P = player()
            menu = open_page(P, MP(P.pr, "tp"))
            CM.last = None
            P.cl.press("#SkyyMGrid", slot=slot_of(menu, "cmdc:island"))
            ct_ = CM.last.act
            world_change(P, W2, W2U, k, guard=False)
            check(P.pm.getCustomPage() is not None and P.pm.getCustomPage().equals(menu), "P1b. %s: without the event the stale menu is still "
                  "the server's page" % V)
            n0 = len(sent(P.net))
            RECS.clear()
            ct_.run()
            run_world(W2)
            P.cl.pump()
            check(sent(P.net)[n0:] == [] and acks(P.pm) == 0 and P.pm.getCustomPage() is None
                  and any("menu close after a command" in l and "forgot" in l for l in logs()),
                  "P1b. %s: the CloseTask's own check (changedWorld: W1 -> W2) forgets it - no packet, 0 pending, one INFO line" % V)
            mok, bok = next_page_works(P, k)
            check(mok and bok, "P1b. %s: the next pages' clicks work" % V)
            # P1c: a re-join of the SAME world (World.addPlayer on W1 again) with the event: forgotten at the join
            P = player()
            menu = open_page(P, MP(P.pr, "tp"))
            CM.last = None
            P.cl.press("#SkyyMGrid", slot=slot_of(menu, "cmdc:island"))
            ct_ = CM.last.act
            world_change(P, W1, W1U, k)
            n0 = len(sent(P.net))
            ct_.run()
            run_world(W1)
            P.cl.pump()
            check(P.ev_page is None and sent(P.net)[n0:] == [] and acks(P.pm) == 0, "P1c. %s: a re-join of the same world: the menu forgotten "
                  "at the join, the CloseTask sends nothing" % V)
            check(next_page_works(P, k) == (True, True), "P1c. %s: the next pages' clicks work" % V)
        # P1d: the CloseTask's other timings are safe on both jars - hop BEFORE the change (old world) / hop while between worlds
        P = player()
        menu = open_page(P, MP(P.pr, "tp"))
        CM.last = None
        P.cl.press("#SkyyMGrid", slot=slot_of(menu, "cmdc:island"))
        ct_ = CM.last.act
        drain(W1, W2)
        ct_.run()                                  # hop on W1 (still there)
        world_change(P, W2, W2U, k)
        n0 = len(sent(P.net))
        run_world(W1)                              # its world part runs on W1's thread after the player left
        check(sent(P.net)[n0:] == [], "P1d. %s: a CloseTask that hopped before the world change does nothing after it (the world differs)" % V)
        P = player()
        menu = open_page(P, MP(P.pr, "tp"))
        CM.last = None
        P.cl.press("#SkyyMGrid", slot=slot_of(menu, "cmdc:island"))
        ct_ = CM.last.act
        leave(P, W2, W2U, k)
        ct_.run()                                  # hop while between worlds: the player's world id is W2, no ref yet
        n0 = len(sent(P.net))
        run_world(W2)
        check(sent(P.net)[n0:] == [], "P1d. %s: a CloseTask that runs while the player is between worlds does nothing (no ref)" % V)
        arrive(P, W2)

        # ---- P2 the keep-open command redraw (RefreshTask) after a world change
        P = player()
        menu = open_page(P, MP(P.pr, "main"))
        rt = JV(k, "RefreshTask")(menu, P.pr)
        world_change(P, W2, W2U, k)
        n0 = len(sent(P.net))
        rt.run()
        run_world(W2)
        P.cl.pump()
        pk = kinds(sent(P.net)[n0:])
        R["p2"] = (pk, acks(P.pm))
        if k == "old":
            check(pk == ["CustomPage(MenuPage)"] and acks(P.pm) == 1, "P2. %s REPRODUCES: its RefreshTask redrew the stale menu on the new "
                  "world (a page update the client ignores: 1 pending) %s" % (V, pk))
            check(next_page_works(P, k) == (False, False), "P2. %s: ... the next pages ignore clicks" % V)
        else:
            check(pk == [] and acks(P.pm) == 0, "P2. %s: the RefreshTask sends nothing after the world change, 0 pending %s" % (V, pk))
            check(next_page_works(P, k) == (True, True), "P2. %s: the next pages' clicks work" % V)
            P = player()
            menu = open_page(P, MP(P.pr, "main"))
            rt = JV(k, "RefreshTask")(menu, P.pr)
            world_change(P, W2, W2U, k, guard=False)
            n0 = len(sent(P.net))
            rt.run()
            run_world(W2)
            check(sent(P.net)[n0:] == [] and P.pm.getCustomPage() is None and acks(P.pm) == 0,
                  "P2b. %s: without the event the RefreshTask's own check forgets the menu (no packet)" % V)

        # ---- P3 a bench after a world change with the menu left open (setPageWithWindows runs setPage first)
        P = player()
        open_page(P, MP(P.pr, "main"))
        world_change(P, W2, W2U, k)
        n0 = len(sent(P.net))
        P.pm.setPage(P.ref, P.st, PAGE_E.Bench, True)
        P.cl.pump()
        R["p3"] = acks(P.pm)
        if k == "old":
            check(R["p3"] == 1 and kinds(sent(P.net)[n0:]) == ["SetPage(Bench)"], "P3. %s REPRODUCES: the bench after the world change "
                  "leaves 1 acknowledgement the client never sends (the stale menu was still open on the server)" % V)
            check(next_page_works(P, k) == (False, False), "P3. %s: ... the next pages ignore clicks" % V)
        else:
            check(R["p3"] == 0, "P3. %s: the bench after the world change leaves 0 pending (the menu was forgotten at the join)" % V)
            check(next_page_works(P, k) == (True, True), "P3. %s: the next pages' clicks work" % V)

        # ---- P4 the normal same-world paths still work
        P = player()
        menu = open_page(P, MP(P.pr, "main"))
        n0 = len(sent(P.net))
        P.cl.press("#SkyyMClose")
        check(kinds(sent(P.net)[n0:]) == ["CustomPage(MenuPage)", "SetPage(None)"] and acks(P.pm) == 0 and P.pm.getCustomPage() is None
              and P.cl.page is None and not P.cl.waiting, "P4. %s: the Close button: grid emptied + setPage(None), both acknowledged, "
              "closed on both sides" % V)
        menu = open_page(P, MP(P.pr, "tp"))
        CM.last = None
        P.cl.press("#SkyyMGrid", slot=slot_of(menu, "cmdc:hub"))
        ct_ = CM.last.act
        n0 = len(sent(P.net))
        ct_.run()
        run_world(W1)
        P.cl.pump()
        check(kinds(sent(P.net)[n0:]) == ["SetPage(None)"] and acks(P.pm) == 0 and P.pm.getCustomPage() is None and P.cl.page is None,
              "P4. %s: a command that stays in the world: the CloseTask closes the menu (acknowledged, closed on both sides)" % V)
        menu = open_page(P, MP(P.pr, "main"))
        rt = JV(k, "RefreshTask")(menu, P.pr)
        n0 = len(sent(P.net))
        rt.run()
        run_world(W1)
        P.cl.pump()
        check(kinds(sent(P.net)[n0:]) == ["CustomPage(MenuPage)"] and acks(P.pm) == 0 and P.cl.page == PKG + "MenuPage",
              "P4. %s: the RefreshTask redraw in the same world (acknowledged, the menu stays)" % V)
        P.cl.press("#SkyyMGrid", slot=slot_of(menu, "profile"))
        check(str(menu.infoName) == "Your Profile", "P4. %s: ... and the menu's next click works" % V)
        P.cl.esc()
        check(P.pm.getCustomPage() is None and acks(P.pm) == 0, "P4. %s: Esc ('mesc' then Dismiss) closes the menu on the server" % V)

        # ---- P5 no packet to a player with no page
        P = player()
        menu = open_page(P, MP(P.pr, "tp"))
        P.cl.esc()
        n0 = len(sent(P.net))
        ct2 = JV(k, "CloseTask")(menu, P.pr)
        ct2.run()
        run_world(W1)
        rt2 = JV(k, "RefreshTask")(menu, P.pr)
        rt2.run()
        run_world(W1)
        check(sent(P.net)[n0:] == [] and acks(P.pm) == 0, "P5. %s: CloseTask / RefreshTask after Esc send nothing" % V)
        if k == "new":
            RECS.clear()
            leave(P, W2, W2U, k)
            check(len(sent(P.net)) == n0 and P.ev_page is None and not [l for l in logs() if "changed world" in l],
                  "P5. %s: PageGuard at a world join with no page open: nothing sent, nothing logged" % V)
            arrive(P, W2)
            check(not bool(menu.watchTick(W2)) and len(sent(P.net)) == n0, "P5. %s: MenuWatch with no page: done, nothing sent" % V)
        print("P1-P5. %s: island tile pending %s packets %s, next pages %s; RefreshTask %s; bench %s" % (
            V, R.get("p1_pending"), R.get("p1_packets"), R.get("p1_next"), R.get("p2"), R.get("p3")))
    check(RES["old"]["p1_pending"] == 1 and RES["new"]["p1_pending"] == 0 and RES["old"]["p1_next"] == (False, False)
          and RES["new"]["p1_next"] == (True, True), "P. THE CHECK: the Island-tile flow leaves 0 pending and working pages on %s; the same "
          "check FAILS on %s (1 pending, every click dropped)" % (VERSION, OLDVER))

    # ---- P6 (0.3.6) PageGuard on every kind of page
    MPn, SPn, APn = JN("MenuPage"), JN("SettingsPage"), JN("AdminPage")
    for nm, mkp in (("SkyWynn Menu", lambda pr: MPn(pr, "main")), ("Settings", lambda pr: SPn(pr, -1)), ("Server Setup", lambda pr: APn(pr, "list", None)),
                    ("a stand-in page with the engine's onDismiss", lambda pr: PLAIN(pr))):
        P = player()
        pg = open_page(P, mkp(P.pr))
        check(bool(PG.plainDismiss(pg)), "P6. plainDismiss(%s) = true (the engine's empty onDismiss)" % nm)
        RECS.clear()
        leave(P, W2, W2U, "new")
        check(P.ev_page is None and P.ev_after == P.ev_counter and P.ev_sent_after == P.ev_sent
              and any("changed world with the page" in l and "forgot it" in l for l in logs()),
              "P6. %s: forgotten AT the world join - no packet, the counter untouched (%d), one INFO line" % (nm, P.ev_after))
        arrive(P, W2)
        P.pm.setPage(P.ref, P.st, PAGE_E.Bench, True)
        P.cl.pump()
        check(acks(P.pm) == 0, "P6. %s: a bench after the join leaves 0 pending" % nm)
    check(not bool(PG.plainDismiss(OWN(None))) and not bool(PG.plainDismiss(THROW(None))) and not bool(PG.plainDismiss(None))
          and not bool(PG.plainDismiss("not a page")), "P6. plainDismiss: false for a page with its own onDismiss, null, a non-page")
    # a page with its own onDismiss: left alone at the join, forgotten by StaleTask on the new world's thread with the NEW ref / store
    try:
        TF = JClass("com.hypixel.hytale.server.core.util.concurrent.ThreadUtil").daemon("Scheduler")
        EXEC = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor(TF)
    except Exception as e:
        print("   (ThreadUtil.daemon unavailable: %s - plain scheduler)" % e)
        EXEC = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor()

    def wait_task(w, secs=3.0, cls=None):
        t_end = time.time() + secs
        while time.time() < t_end:
            if w.tasks is not None and not w.tasks.isEmpty():
                t = w.tasks.peek()
                if cls is None or str(t.getClass().getName()) == PKG + cls:
                    return w.tasks.poll()
                w.tasks.poll()
            time.sleep(0.02)
        return None
    PG.EXEC = EXEC
    try:
        drain(W1, W2, W3)
        P = player()
        own = open_page(P, OWN(P.pr))
        RECS.clear()
        leave(P, W2, W2U, "new")
        check(P.ev_page is not None and P.ev_page.equals(own) and int(own.dCount) == 0 and P.ev_sent_after == P.ev_sent
              and int(PG.DEFERRED) >= 1 and any("its own close code" in l for l in logs()),
              "P6. a page with its OWN onDismiss: left alone at the join (still the page, onDismiss not run, nothing sent), StaleTask started")
        time.sleep(0.3)
        check(W2.tasks is None or W2.tasks.isEmpty(), "P6. ... while the player is between worlds nothing is handed to the new world (it polls)")
        arrive(P, W2)
        task = wait_task(W2, 2.0, "StaleTask")
        check(task is not None, "P6. ... once the player is in the new world's store, StaleTask hands itself to that world's thread")
        n0 = len(sent(P.net))
        if task is not None:
            task.run()
        check(P.pm.getCustomPage() is None and int(own.dCount) == 1 and own.dRef is not None and own.dRef.equals(P.ref)
              and own.dStore is not None and own.dStore.equals(P.st) and len(sent(P.net)) == n0 and acks(P.pm) == 0,
              "P6. ... which forgets it with the NEW world's ref / store (its onDismiss ran once with them), no packet, 0 pending")
        P.pm.setPage(P.ref, P.st, PAGE_E.Bench, True)
        P.cl.pump()
        check(acks(P.pm) == 0, "P6. ... and a bench after it leaves 0 pending")
        # replaced before the deferred forget: left alone
        P = player()
        own = open_page(P, OWN(P.pr))
        leave(P, W2, W2U, "new")
        arrive(P, W2)
        task = wait_task(W2, 2.0, "StaleTask")
        other = open_page(P, PLAIN(P.pr))                 # the engine's openCustomPage dismisses `own` itself (dCount 1)
        n0 = len(sent(P.net))
        if task is not None:
            task.run()
        check(task is not None and P.pm.getCustomPage() is not None and P.pm.getCustomPage().equals(other) and int(own.dCount) == 1
              and len(sent(P.net)) == n0, "P6. a page replaced before the deferred forget: StaleTask leaves the new page alone")
        # a throwing onDismiss: logged once, nothing breaks (the page stays the engine's page - its own problem at the next page action)
        P = player()
        thr = open_page(P, THROW(P.pr))
        PG.WARNED = 0
        RECS.clear()
        leave(P, W2, W2U, "new")
        arrive(P, W2)
        task = wait_task(W2, 2.0, "StaleTask")
        n0 = len(sent(P.net))
        if task is not None:
            task.run()
        check(task is not None and len(sent(P.net)) == n0 and any("page check failed" in l for l in logs()),
              "P6. a page whose onDismiss throws: StaleTask logs it once, sends nothing, nothing else breaks")
        # the player leaves while the StaleTask polls: it ends
        P = player()
        own = open_page(P, OWN(P.pr))
        leave(P, W2, W2U, "new")
        jf(PR.class_, "holder").set(P.pr, None)          # disconnected: no entity, no holder -> PlayerRef.isValid() false
        time.sleep(0.3)
        check(W2.tasks is None or W2.tasks.isEmpty(), "P6. a player who leaves while StaleTask polls: it ends, nothing handed to a world")
    finally:
        pass
    # JOINS: one per world join; MenuQuit drops them
    PG.JOINS.clear()
    P = player()
    for (w, wu) in ((W2, W2U), (W1, W1U), (W3, W3U)):
        world_change(P, w, wu, "new")
    check(int(PG.joins(SKP)) == 3, "P6. PageGuard counts world joins per player (%d)" % int(PG.joins(SKP)))
    JN("MenuQuit")().accept(PDE(P.pr))
    check(int(PG.joins(SKP)) == 0 and not bool(PG.JOINS.containsKey(SKP)), "P6. MenuQuit (disconnect) drops the player's join count")
    # PageGuard ignores odd events
    try:
        JN("PageGuard")().accept("not an event")
        JN("PageGuard")().accept(ATW(None, W1, None))
        h0 = U.allocateInstance(THL.class_)
        JN("PageGuard")().accept(ATW(h0, W1, None))       # a holder without components
        ok_odd = True
    except Exception as e:
        ok_odd = False
    check(ok_odd, "P6. PageGuard ignores a wrong event, a null holder and a holder without a Player (nothing thrown)")

    # ---- P7 (0.3.6) MenuWatch.watchTick
    PG.EXEC = None
    P = player()
    menu = open_page(P, MPn(P.pr, "main"))

    def settle(pg):
        pg.lastSend = int(System.currentTimeMillis()) - 1500
    settle(menu)
    n0 = len(sent(P.net))
    check(bool(menu.watchTick(W1)) and len(sent(P.net)) == n0 and int(menu.heals) == 0, "P7. a healthy menu: the check's test click arrives, nothing is sent")
    stray = CPK("skyymenuharness.Elsewhere", False, True, menu.getLifetime(),
                JArray(JClass("com.hypixel.hytale.protocol.packets.interface_.CustomUICommand"))(0),
                JArray(JClass("com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBinding"))(0))
    P.pm.updateCustomPage(stray)
    P.cl.pump()
    check(acks(P.pm) == 1, "P7. a stray page packet (another page's update the client never acknowledges): 1 pending")
    info0 = str(menu.infoName) if menu.infoName is not None else None
    P.cl.press("#SkyyMGrid", slot=slot_of(menu, "profile"))
    check((None if menu.infoName is None else str(menu.infoName)) == info0, "P7. ... so the engine drops the menu's next click")
    settle(menu)
    RECS.clear()
    n0 = len(sent(P.net))
    again = bool(menu.watchTick(W1))
    P.cl.pump()
    lw = [l for l in logs() if "WARNING" in l and "dropping" in l]
    HEAL = "Clicks were stuck (a game hiccup after a teleport) - fixed. Click again."
    check(again and int(menu.heals) == 1 and len(lw) == 1 and kinds(sent(P.net)[n0:]) == ["CustomPage(MenuPage)"] and acks(P.pm) == 0
          and str(menu.status) == HEAL, "P7. the check heals it: one WARNING, the acknowledgements reset, ONE answer (the menu with %r), 0 "
          "pending" % HEAL)
    P.cl.press("#SkyyMGrid", slot=slot_of(menu, "profile"))
    check(str(menu.infoName) == "Your Profile", "P7. ... and the next click works")
    answers = []
    for i in range(5):
        P.pm.updateCustomPage(stray)
        P.cl.pump()
        settle(menu)
        n0 = len(sent(P.net))
        menu.watchTick(W1)
        P.cl.pump()
        answers.append(len(sent(P.net)) - n0)
        check(acks(P.pm) == 0, "P7. heal %d: 0 pending after it" % (i + 2))
    check(answers == [1, 1, 0, 0, 0] and int(menu.heals) == 6, "P7. at most 3 answers per menu, later heals reset silently: %s" % answers)
    check(len([l for l in logs() if "WARNING" in l and "dropping" in l]) == 3, "P7. WARNING lines for heals 1-3 only")
    # a world change without the event: the check forgets the menu (no packet)
    P = player()
    menu = open_page(P, MPn(P.pr, "main"))
    leave(P, W2, W2U, "new", guard=False)
    settle(menu)
    n0 = len(sent(P.net))
    check(bool(menu.watchTick(W2)) and len(sent(P.net)) == n0, "P7. between worlds (no ref yet): the check waits, nothing sent")
    arrive(P, W2)
    check(not bool(menu.watchTick(W2)) and len(sent(P.net)) == n0 and P.pm.getCustomPage() is None,
          "P7. after a world change without the event: the check forgets the menu (no packet) and ends")
    P.pm.setPage(P.ref, P.st, PAGE_E.Bench, True)
    P.cl.pump()
    check(acks(P.pm) == 0, "P7. ... a bench after it leaves 0 pending")
    P = player()
    menu = open_page(P, MPn(P.pr, "main"))
    P.cl.esc()
    check(not bool(menu.watchTick(W1)), "P7. after Esc the check ends")
    P = player()
    menu = open_page(P, MPn(P.pr, "main"))
    jf(PR.class_, "entity").set(P.pr, None)
    check(not bool(menu.watchTick(W1)), "P7. the player gone (no entity, no holder): the check ends")

    # ---- P8 (0.3.6) the real timer chains (a scheduler built like HytaleServer.SCHEDULED_EXECUTOR, handed over as setup() does)
    MW = JN("MenuWatch")
    PG.EXEC = None
    PG.WARNED = 0
    RECS.clear()
    P = player()
    menu = open_page(P, MPn(P.pr, "main"))
    P.cl.press("#SkyyMGrid", slot=slot_of(menu, "profile"))
    check(str(menu.infoName) == "Your Profile" and any("could not be scheduled" in l for l in logs()),
          "P8. no scheduler (SkyyMenu not set up): the menu still works and the missing check is logged once")
    PG.EXEC = EXEC
    try:
        drain(W1, W2, W3)
        P = player()
        menu = open_page(P, MPn(P.pr, "main"))
        t0 = time.time()
        task = wait_task(W1, 3.0, "MenuWatch")
        check(task is not None and task.target is not None and task.target.equals(W1) and time.time() - t0 >= 0.8,
              "P8. ~1 s after the open the scheduler-thread hop handed a MenuWatch for the player's world to World.execute (%.2f s)" % (time.time() - t0))
        n0 = len(sent(P.net))
        settle(menu)
        if task is not None:
            task.run()
        check(len(sent(P.net)) == n0 and int(menu.heals) == 0, "P8. healthy: the check sent nothing")
        task = wait_task(W1, 3.0, "MenuWatch")
        check(task is not None, "P8. ... and it checks again a second later")
        P.pm.updateCustomPage(stray)
        P.cl.pump()
        settle(menu)
        if task is not None:
            task.run()
        P.cl.pump()
        check(int(menu.heals) == 1 and acks(P.pm) == 0, "P8. a stray packet is healed by the next timer check")
        drain(W1, W2, W3)
        world_change(P, W2, W2U, "new")
        task = wait_task(W2, 3.0, "MenuWatch")
        n0 = len(sent(P.net))
        if task is not None:
            task.run()
        check(task is not None and len(sent(P.net)) == n0 and (W1.tasks is None or W1.tasks.isEmpty()),
              "P8. after a world change the hop hands the check to the NEW world, which finds the menu gone (forgotten at the join) - nothing sent")
        check(wait_task(W2, 2.2) is None and wait_task(W1, 0.1) is None, "P8. ... and the check ends")
        P = player()
        menu = open_page(P, MPn(P.pr, "main"))
        task = wait_task(W1, 3.0, "MenuWatch")
        P.cl.esc()
        if task is not None:
            task.run()
        check(task is not None and wait_task(W1, 2.2) is None, "P8. Esc: the next check ends it")
        P = player()
        menu = open_page(P, MPn(P.pr, "main"))
        PG.STOP = True
        check(wait_task(W1, 2.2) is None, "P8. STOP (plugin shutdown): no check runs")
        PG.STOP = False
    finally:
        PG.EXEC = None
        try:
            EXEC.shutdownNow()
        except Exception:
            pass

    # ---------------- X. engine-access audit (MethodHandles.Lookup in each referencing class)
    LIN = JClass("skyymenuharness.LookupIn")
    MTc = JClass("java.lang.invoke.MethodType")
    CPool = JClass("javassist.bytecode.ConstPool")
    JMod_ = JClass("java.lang.reflect.Modifier")
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def audit(cn, ldr, pool):
        def jvm_class(name):
            return Cls.forName(name.replace("/", "."), False, ldr)
        D = jvm_class(cn)
        lk = LIN.lookupIn(D)
        cc = pool.get(cn)
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
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", ldr).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)),
                                                 str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)),
                                                 str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, ldr)
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
                    # MethodHandles refuses caller-sensitive JDK methods (Field.get, Method.invoke - the config kit's reflection) to a
                    # privateLookupIn lookup whatever their access; for those the JVM's own rule is checked directly: a public member
                    # of a public class is accessible from anywhere
                    if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb9, 0xb8):
                        try:
                            m_ = C_.getMethod(name, mt.parameterArray())
                            if JMod_.isPublic(int(m_.getModifiers())) and JMod_.isPublic(int(m_.getDeclaringClass().getModifiers())):
                                tally("X caller-sensitive public")
                                continue
                        except Exception:
                            pass
                    refused.append("%s: %s" % (where, ex_))
        return refused, n

    xp = CPc(False)
    xp.appendSystemPath()
    xp.appendClassPath(B.SERVER_JAR)
    xp.appendClassPath(JAR)
    xref, xn = [], 0
    COUNT.pop("X caller-sensitive public", None)
    for cn_ in sorted(CBY["new"]):
        r_, n_ = audit(cn_, LDR["new"], xp)
        xref += r_
        xn += n_
    check(not xref and xn > 1000, "X. all %d references in the %d classes of the %s jar pass MethodHandles.Lookup in their own class "
          "(the JVM's access rules): refused %s" % (xn, len(CBY["new"]), VERSION, xref[:5]))
    xcs = COUNT.get("X caller-sensitive public", 0)
    nn = [c for c in CBY["new"] if c.rsplit(".", 1)[-1] in ("PageGuard", "StaleTask", "MenuWatch", "MenuPage", "CloseTask", "RefreshTask")]
    xr2, xn2 = [], 0
    for cn_ in sorted(nn):
        r_, n_ = audit(cn_, LDR["new"], xp)
        xr2 += r_
        xn2 += n_
    check(not xr2 and xn2 > 500, "X. the classes the fix touches (PageGuard, StaleTask, MenuWatch, MenuPage, CloseTask, RefreshTask): %d "
          "references, 0 refused (%s)" % (xn2, xr2[:3]))
    print("X. %d references audited (%d caller-sensitive JDK reflection calls - the config kit's, PageGuard.plainDismiss's getMethod - "
          "checked as public members of public classes), %d of them in the classes the fix touches" % (xn, xcs, xn2))
    xb = CPc(False)
    xb.appendSystemPath()
    xb.appendClassPath(B.SERVER_JAR)
    xb.appendClassPath(JAR)
    xb.appendClassPath(hcls2)
    u2 = JArray(URL)(1)
    u2[0] = File(hcls2).toURI().toURL()
    BADL = URLCL(u2, LDR["new"])
    br_, bn_ = audit("skyymenuharness.BadCaller", BADL, xb)
    check(len(br_) == 1 and "rebuild" in br_[0], "X. control: a class calling MenuPage.rebuild from outside is refused by the audit: %s" % br_)
    try:
        jpbad = JClass("skyymenuharness.BadCaller", loader=BADL)
        jpbad.poke(MPn(player().pr, "main"))
        check(False, "X. control: the outside rebuild call ran - the JVM did not refuse it")
    except Exception as e:
        check("IllegalAccessError" in str(e) or "IllegalAccess" in str(e.__class__.__name__) or "IllegalAccessError" in repr(e),
              "X. control: running it throws IllegalAccessError (%s)" % str(e)[:120])


def main():
    if not os.path.isfile(JAR):
        print("no jar at", JAR, "- build it first")
        return 1
    if not os.path.isfile(OLDJAR):
        print("no 0.3.5 jar at", OLDJAR, "- the stuck-page bug reference is needed for P and K")
        return 1
    claim_scratch()
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
    print("checks passed per part: " + ", ".join("%s %d" % (k, PART_OK[k]) for k in sorted(PART_OK)))
    print("SkyyMenu %s bare-JVM check: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP and os.path.isfile(os.path.join(SCRATCH, MARK)):
        os.chdir(ROOT)                    # the JVM's working directory was the scratch folder
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
