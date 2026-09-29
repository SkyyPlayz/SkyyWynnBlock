"""Bare-JVM check for SkyyMenu 0.3.3 (kept next to the build so the build report's JVM claim can be re-run).

    python SkyyMenu/test_skyymenu_0.3.3.py [--jar <SkyyMenu-0.3.3.jar>] [--dir <scratch folder>] [--keep]

Build the jar first (python tools/menu_0_3_3_patch.py, then python SkyyMenu/build_skyymenu_0.3.3.py). One JVM (the game's own JRE,
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
  F  the Mods list texts (MenuData + MenuUtil.modBodyFor for a player and an admin): SkyyGear replaces SkyyRolls, the round versions,
     Essentials without world spawn + the Warps page, privacy.staffBypass in Party + Essentials, /class arrows + hotbar at once, rarity
     bags + Omni, the bag ladder, no "type it twice"; the Identify tile (slot 26, cmdc:identify; no /identify command = the
     "not installed" path), Settings at slot 39, main slot 51 empty
Not testable without the game (UNVERIFIED in the build report): the pages on a client, a real server's permission lookups (ops,
SkyyRanks grants), the Identify tile with SkyyGear loaded, clicks through the real PageManager.
Nothing is deployed. Default scratch folder: tools/dev/scratch/gc-menu (deleted at the end unless --keep); TEMP / TMP and java.io.tmpdir
point into it. Exit code 1 on any failure.
"""
import os, sys, re, ast, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.3.3"
PKG = "com.skyy.menu."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "gc-menu")))
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

    # ---------------- E. this round's rows in their tabs + paging on the real page
    SetReg.DEFS.clear()
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
    for m, v in (("SkyyParty", "0.1.5"), ("SkyyEssentials", "0.1.5"), ("SkyySkills", "0.4.6"), ("SkyySacks", "0.7.7"),
                 ("SkyyCollections", "0.2.3"), ("SkyyGuilds", "0.1.3")):
        check(ver.get(m) == v, "F. %s version %s (round 8 pin)" % (m, v))

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
