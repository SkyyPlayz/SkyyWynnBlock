"""Bare-JVM check for SkyyMenu 0.3.4 (kept next to the build so the build report's JVM claim can be re-run).

    python SkyyMenu/test_skyymenu_0.3.4.py [--jar <SkyyMenu-0.3.4.jar>] [--dir <scratch folder>] [--keep]

Build the jar first (python tools/menu_0_3_4_patch.py, then python SkyyMenu/build_skyymenu_0.3.4.py). One JVM (the game's own JRE,
-Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the jar on the classpath) checks:
  A  every class of the jar loads and verifies
  B  the permission stand-in: a real PermissionsModule object (allocated, never set up) with one fake PermissionProvider behind
     PermissionsModule.get() - so SetReg.allowed runs the ENGINE's own hasPermission code (user nodes first, a personal -node deny,
     groups, "*"): a node holder, a plain player, an op (hytale:Admin = "*") and an op with a personal deny
  C  the registry: 6-element registrations (every player), the optional 7th element (null / "" = every player, a node = holders only,
     anything else refused), the settings:def: fallback with 7 elements, the first registration wins (node too), visible() per player,
     may(), settings:fn:set refusing a key the player lacks, Reset all keeping the choices the player may not change, fail closed
     without a PermissionsModule
  D  the Settings page itself (SettingsPage.build with the engine's UICommandBuilder / UIEventBuilder): a hidden row is not drawn, a
     tab without a visible row is not drawn (the tab buttons close up), the page moves off a tab the player cannot see, the header
     counts visible rows, a stale click on a row the player lost is refused (SET_TXT_GONE) and changes nothing
  E  the new rows in their tabs: every regSetting of THIS ROUND's set (tools/deploy_set.py SET + the build's ROUND_PINS, ROUND_RETIRED
     out) registered -> General / Combat / Skills rows in SET_ORDER; paging on the real page: General and Combat = 10 rows = page 1 of 2
     with 8 rows + Prev / Next, page 2 of 2 with 2 rows; one-page tabs have no Prev / Next; the defaults template lists the new keys
  G  the review fixes (2026-09-29): a key registered with a node that is not plain is REFUSED for everyone (may false, row hidden, set
     refused, get = its registered default even over a stored choice; an earlier weaker registration of the same mod goes too; later
     registrations stay refused; an undrained settings:def: fails closed on the first call); validPerm refuses "-skyytest.staff" and
     the other non-plain forms and accepts every node the round's mods use today (scanned: regSetting nodes + literal
     requirePermission / hasPermission nodes); two mods on one key: no node then a node = gated (kept when the first mod registers
     again), two different nodes = refused, a mod may change (never drop) its own node
  F  the Mods list texts (MenuData + MenuUtil.modBodyFor for a player and an admin): SkyyGear replaces SkyyRolls, the round versions,
     Essentials without world spawn + the Warps page, privacy.staffBypass in Party + Essentials, /class arrows + hotbar at once, rarity
     bags + Omni, the bag ladder, no "type it twice"; the Identify tile (slot 26, cmdc:identify; no /identify command = the
     "not installed" path), Settings at slot 39, main slot 51 empty; review fix: no (admin) / (staff) line in any player's Mods text,
     every MOD_ADMIN line in the admin's (/classadmin, /ahadmin ... regrant, /fly, /rank set <player> <rank>)
     0.3.4: every MODS version = tools/deploy_set.py SET, SkyyUiProbe listed as a dev mod (admin line only), the SkyyProfiles 0.1.5
     delete / restore / archive lines, SkyyAccessories 0.5.1, /gear charged (admin)
  H  0.3.4 SECONDS: AdminPage.secText / msOf round trips (0.24 <-> 240, 0.001, 1.5, 30, every whole ms 0-3000 and every 0.000-2.000 s
     step, big values), rounding half up to whole ms, bad input refused, typedValue at the min / max edges (refusal text in seconds),
     msRow per type / unit, disp, msWords + rMsg on the kit's message shapes, secHint, the Changes log line, and drawRow with a fake
     config:def / config:fn (value box, "(s)", help with the bounds, drafts in seconds); every millisecond row of the live set found
     (24, the build's rule) and each one's literal min / max / default round-trips
  I  0.3.4 MENU ITEM PER PROFILE (Given with a fake profile:fn:key on the bridge): a new player gets it, a new profile gets it, the
     existing active profile of an old per-player flag does not (migration), the other profiles of that player do, an item already
     held = recorded and none given, profile:busy = wait (nothing recorded) then give, a world switch (PlayerReadyEvent) and a
     reconnect never re-give, a bad key from the bridge falls back to the UUID, item switched off, one pending task per player
     (claim), forget / retainOnline, GrantTask.grantNow without a player entity = retry and nothing written
  J  0.3.4 TWO STARTS on a scratch COPY of the live Skyy_SkyyMenu data (+ SkyyProfiles players files for the keys): the first start
     writes exactly one per-profile record per old flag (and nothing else), no grant; the second start changes no byte and no
     modification time and grants nothing
  K  0.3.4 class byte-compare against SkyyMenu-0.3.3.jar: only the expected classes changed, GivenTick added, the player Settings /
     main menu / Settings registry classes byte-identical
Not testable without the game (UNVERIFIED in the build report): the pages on a client, a real server's permission lookups (ops,
SkyyRanks grants), the Identify tile with SkyyGear loaded, clicks through the real PageManager.
Nothing is deployed. Default scratch folder: tools/dev/scratch/menu034/harness (deleted at the end unless --keep); TEMP / TMP and java.io.tmpdir
point into it. Exit code 1 on any failure.
"""
import os, sys, re, ast, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.3.4"
PKG = "com.skyy.menu."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "menu034", "harness")))
OLDJAR = os.path.join(HERE, "SkyyMenu-0.3.3.jar")
LIVE_MODS = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Hytale", "UserData", "Saves", "HUD mod", "mods")   # READ ONLY
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ------------------------------------------------------------------------------------------------ the round's set (no JVM needed)
def live_set():
    tree = ast.parse(open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8").read())
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SET" for t in n.targets):
            return ast.literal_eval(n.value)
    return []


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
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    import zipfile
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, JAR], convertStrings=True)

    # ---------------- A. load + verify
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return

    UUID, Paths, Boolean, Integer = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Boolean"), JClass("java.lang.Integer")
    HashSet, HashMap, ArrayList = JClass("java.util.HashSet"), JClass("java.util.HashMap"), JClass("java.util.ArrayList")
    MD, MU, SetReg, SetStore = JClass(PKG + "MenuData"), JClass(PKG + "MenuUtil"), JClass(PKG + "SetReg"), JClass(PKG + "SetStore")
    SetRegFn, SetSetFn, SettingsPage = JClass(PKG + "SetRegFn"), JClass(PKG + "SetSetFn"), JClass(PKG + "SettingsPage")
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
    sget = JClass(PKG + "SetGetFn")()
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
                  "gear.armorWarn", "gear.notices", "skills.xbowMeter", "skills.xbowSound", "skills.xbowHint"], "E. Combat rows: %s" % com)
    check(len(ski) == 8 and ski[7] == "skills.overallUp", "E. Skills: skills.overallUp is row 8: %s" % ski)
    for k in ("party.invites", "tpa.requests", "msg.private", "skills.overallUp", "skills.xbowMeter", "gear.notices"):
        check(k in list(MD.SET_ORDER) and ("#%s=true" % k) in str(MD.SET_TEMPLATE), "E. %s in SET_ORDER and the defaults template" % k)
    rows = int(MD.SET_ROWS)
    check(rows == 8, "E. 8 rows per page")
    for tab, n in (("general", 10), ("combat", 10)):
        pg = SettingsPage(pref(B_), cat[tab])
        c1 = build(pg)
        check(rows_of(c1) == 8 and "10 settings" in head_of(c1) and "page 1 of 2" in head_of(c1), "E. %s page 1: 8 rows, %r" % (tab, head_of(c1)))
        check(any(s == "#SkyyStgFoot" and "#SkyyStgPrev" in t for s, t, d in c1) and any(s == "#SkyyStgFoot" and "#SkyyStgNext" in t for s, t, d in c1),
              "E. %s: Prev / Next drawn" % tab)
        pg.pageNo = 1
        c2 = build(pg)
        check(rows_of(c2) == 2 and "page 2 of 2" in head_of(c2), "E. %s page 2: 2 rows, %r" % (tab, head_of(c2)))
        names2 = [d for s, t, d in c2 if s.startswith("#SkyyStgName")]
        last2 = gen[8:] if tab == "general" else com[8:]
        check(len(names2) == 2, "E. %s page 2 row names %s (keys %s)" % (tab, names2, last2))
        pg.pageNo = 5
        c3 = build(pg)
        check(int(pg.pageNo) == 1 and rows_of(c3) == 2, "E. %s: a page past the end clamps to the last" % tab)
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
    # 0.3.4: every MODS version = what tools/deploy_set.py SET pins (SkyyMenu's own entry = VERSION)
    _set = live_set()
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
    check(MU.cmd("identify") is None and str(JClass(PKG + "MenuPage").cmdOf("cmdc:identify")) == "identify",
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

    # ================================================================================================ 0.3.4
    # ---------------- H. seconds in Server Setup
    AP = JClass(PKG + "AdminPage")
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
    Gv, MC, GT = JClass(PKG + "Given"), JClass(PKG + "MenuCfg"), JClass(PKG + "GrantTask")
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

    # ---------------- J. two starts on a scratch COPY of the live Skyy_SkyyMenu data
    live_menu = os.path.join(LIVE_MODS, "Skyy_SkyyMenu")
    if not os.path.isdir(live_menu):
        print("J. no live Skyy_SkyyMenu folder at %s - skipped" % live_menu)
    else:
        jw = os.path.join(SCRATCH, "livecopy")
        shutil.copytree(live_menu, os.path.join(jw, "Skyy_SkyyMenu"))
        live_prof = os.path.join(LIVE_MODS, "Skyy_SkyyProfiles", "players")
        if os.path.isdir(live_prof):
            shutil.copytree(live_prof, os.path.join(jw, "Skyy_SkyyProfiles", "players"))
        menu = os.path.join(jw, "Skyy_SkyyMenu")
        players = os.path.join(jw, "Skyy_SkyyProfiles", "players")

        @JImplements("java.util.function.Function")
        class ProfKey:
            @JOverride
            def apply(self, u):
                f = os.path.join(players, str(u) + ".properties")
                act = "1"
                if os.path.isfile(f):
                    for line in open(f, encoding="utf-8", errors="ignore"):
                        if line.startswith("active="):
                            act = line.split("=", 1)[1].strip()
                return str(u) if act in ("", "1") else str(u) + "-p" + act
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

        AST = JClass(PKG + "AdmSaveTask")

        def start():
            for mp in (Gv.SESSION, Gv.CHECKED, Gv.READY, Gv.PENDING, Gv.INFLIGHT):
                mp.clear()
            MC.FILE = Paths.get(os.path.join(menu, "config.properties"))
            MC.init()
            SetReg.ADMIN_FILE = Paths.get(os.path.join(menu, "settings-defaults.properties"))
            SetReg.loadAdmin(True)
            AST.BASE = Paths.get(menu)
            AST.ensureDirs()
            Gv.DIR = Paths.get(os.path.join(menu, "given-profile"))
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
        legacy = sorted(f[:36] for f in os.listdir(os.path.join(menu, "given"))) if os.path.isdir(os.path.join(menu, "given")) else []
        t0 = tree()
        r1 = start()
        t1 = tree()
        print("J. live copy: %d old flag(s) %s, start 1: %s" % (len(legacy), legacy, r1))
        check(legacy and all(r1[us][1] == 1 for us in legacy), "J. start 1: no player with an old flag gets a second item (all 1)")
        new_files = sorted(k for k in t1 if k not in t0)
        changed = sorted(k for k in t0 if k in t1 and t0[k] != t1[k])
        want = sorted([os.path.join("Skyy_SkyyMenu", "given-profile") + os.sep] +
                      [os.path.join("Skyy_SkyyMenu", "given-profile", r1[us][0] + ".txt") for us in legacy])
        check(new_files == want and not changed and not [k for k in t0 if k not in t1],
              "J. start 1 writes exactly one record per old flag (the CURRENT profile's key) and nothing else: new %s changed %s" % (new_files, changed))
        r2 = start()
        t2 = tree()
        check(r2 == dict((k, (v[0], 1)) for k, v in r1.items()) and all(v[1] == 1 for v in r2.values()), "J. start 2: no grant: %s" % r2)
        check(t2 == t1, "J. start 2: no file churn (every byte and modification time unchanged)")
        br.put("profile:fn:key", PKey())

    # ---------------- K. class byte-compare 0.3.3 -> 0.3.4
    if not os.path.isfile(OLDJAR):
        check(False, "K. no %s to compare with" % OLDJAR)
    else:
        za, zb = zipfile.ZipFile(OLDJAR), zipfile.ZipFile(JAR)
        na, nb = set(za.namelist()), set(zb.namelist())
        ch = sorted(x for x in na & nb if za.read(x) != zb.read(x))
        print("K. 0.3.3 -> 0.3.4: changed %s; added %s; removed %s" % ([x.split("/")[-1] for x in ch], sorted(nb - na), sorted(na - nb)))
        P_ = "com/skyy/menu/"
        okch = set([P_ + c + ".class" for c in ("MenuData", "MenuUtil", "Given", "AdminPage", "MenuCmd", "GrantTask", "MenuReady", "SeenTick",
                                                 "MenuQuit", "SkyyMenuPlugin", "CfgRows", "CfgFn")] + ["manifest.json"])
        check(sorted(nb - na) == [P_ + "GivenTick.class"] and not (na - nb), "K. GivenTick added, nothing removed")
        check(set(ch) <= okch, "K. only the expected classes changed: unexpected %s" % sorted(set(ch) - okch))
        for c in ("SettingsPage", "SetReg", "SetStore", "SetSaveTask", "SetLoadTask", "SetGetFn", "SetRegFn", "SetSetFn", "SetDefCfg", "Tips",
                  "MenuPage", "MenuCfg", "AdmSaveTask", "RefreshTask", "CloseTask", "MenuPageFactory", "SettingsCmd", "AdminCmd", "AdminModCmd"):
            check(za.read(P_ + c + ".class") == zb.read(P_ + c + ".class"), "K. %s byte-identical to 0.3.3" % c)
        check(za.read("Server/Item/Items/Utility/Skyy_Menu.json") == zb.read("Server/Item/Items/Utility/Skyy_Menu.json"), "K. the menu item JSON unchanged")



def main():
    if not os.path.isfile(JAR):
        print("no jar at", JAR, "- build it first")
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
    print("SkyyMenu %s bare-JVM check: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
