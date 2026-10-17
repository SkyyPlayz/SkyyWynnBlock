"""Bare-JVM check for SkyyEssentials 0.1.12 (MENU PATTERN sweep S4: the trade page, Trade settings, Teleport and message settings and the
/warpadmin warps editor on the kit 1.7 hub page; tools/essentials_0_1_12_patch.py). Build first:
    python tools/essentials_0_1_12_patch.py && python SkyyEssentials/build_skyyessentials_0.1.12.py

    python SkyyEssentials/test_skyyessentials_0.1.12.py [--jar <SkyyEssentials-0.1.12.jar>] [--dir <scratch folder>] [--keep]

The 0.1.11 harness (test_skyyessentials_0.1.11.py, loaded as a module, its globals pointed at 0.1.12) runs its phases main / trade / tpa /
chat / keep / compost / live1 / live2 against this jar, each in a fresh JVM; the checks that change ON PURPOSE (73 classes with HubBar; the
jar's kit art files) are listed in SUPERSEDED and re-checked here. Then:
  phase menu (a fresh JVM, -Xverify:all; stand-in Universe + two online players, a REAL PermissionsModule with one fake provider - Alice
  has skyyessentials.tradeadmin + skyyessentials.admin, Bob nothing - the real config kit on a scratch folder, real escrow containers):
    U1 EVERY PAGE BUILT through its real build(): the trade page (page-only and with an offer window, Alice admin / Bob not, locked in the
       countdown, coins off with / without an offer, ended), Trade settings (Alice; a danger-row question; Bob without permission),
       Teleport and message settings, the warps editor (no warps, 3, 230 = Show more, the remove confirm, warps still loading, Bob without
       permission): page rules (check_page, kit paths, every b.set / binding names an element) + SUI.assert_menu_page (1600 x 980, row 1 +
       row 2, one sub row, no back button / < Menu, no pager) + no Close / Back / Prev / Next text + the sub row + row 2's tabs
    U2 ITEM SAFETY - leaving the trade page through row 1 / row 2 / the X / the sub-tab: both escrows hold real items, the countdown is
       running; a row-2 click whose tab opens another page (a bridge Function that, like the engine, dismisses the open page) and a
       row-1 click to another hub run TStore.pageDismissed exactly like Esc / Close: countdown stopped, Ready cleared, the trade stays
       open, NOTHING moved (both players' items counted before and after); the X / Home answer "close" (the engine then dismisses the
       same way); afterwards Cancel trade gives everything back (inventories + what the trade owes = the totals before)
    U3 clicks: Bob's Trade settings sub-tab click is refused (not an admin); the Trade sub-tab of Trade settings with no open trade says
       so; the warps list Show more adds 200; every old click word still bound
    U4 bytecode: handleDataEvent asks hubClick first (TradePage / TCfgPage / WarpPage); hubClick calls route / goHub / close / hubAck;
       onDismiss still only calls TStore.pageDismissed; /warpadmin still opens WarpPage; no command registers /warp (vanilla's stays)
  Z  class byte-compare 0.1.11 -> 0.1.12: TradePage, TCfgPage, WarpPage changed on purpose, HubBar new, everything else = version text
NOT runnable in a bare JVM: where the client draws the offer window next to a 1600 x 980 page, the look, the real page manager - in-game steps.
Default scratch folder: tools/dev/scratch/menuS4/essentials/test (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, time, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "dev"))
import skyyui as SUI

_s11 = importlib.util.spec_from_file_location("test_skyyessentials_0_1_11", os.path.join(HERE, "test_skyyessentials_0.1.11.py"))
T11 = importlib.util.module_from_spec(_s11)
_s11.loader.exec_module(T11)

VERSION = "0.1.12"
PREV = "0.1.11"
PKG = "com.skyy.essentials."
SCRATCH = os.path.abspath(T11.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "menuS4", "essentials", "test")))
JAR = os.path.abspath(T11.arg("--jar", os.path.join(HERE, "SkyyEssentials-%s.jar" % VERSION)))
PREV_JAR = os.path.join(HERE, "SkyyEssentials-%s.jar" % PREV)
KEEP = "--keep" in sys.argv
# the 0.1.11 harness, pointed at this jar (its checks read these module globals)
T11.VERSION, T11.PREV10, T11.SCRATCH, T11.JAR, T11.PREV_JAR, T11.KEEP = VERSION, PREV, SCRATCH, JAR, PREV_JAR, KEEP

# 0.1.11 checks that change ON PURPOSE in 0.1.12 (each is re-checked below in its new form)
SUPERSEDED = [
    (re.compile(r"^72 classes in the jar"), "73 classes (+ HubBar) - checked in phase menu U0"),
    (re.compile(r"^P1: "), "the jar's non-class files = the two Compost_Soft files + the kit art - checked in phase menu U0"),
]
SKIPPED = []
FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def t11_check(cond, what):
    if not cond:
        for rx, why in SUPERSEDED:
            if rx.search(str(what)):
                SKIPPED.append("%s  -> %s" % (str(what)[:120], why))
                return
    check(cond, what)


T11.check = t11_check
T11.FAILS, T11.OKS = FAILS, OKS


# ============================================================================================================== helpers (SkyyMenu harness)
def jf(c, name):
    while c is not None:
        try:
            f = c.getDeclaredField(name)
            f.setAccessible(True)
            return f
        except Exception:
            c = c.getSuperclass()
    raise KeyError(name)


def cmds_of(b):
    out = []
    for c in list(b.getCommands()):
        g = lambda n: (lambda v: None if v is None else str(v))(jf(c.getClass(), n).get(c))
        out.append((g("type"), g("selector"), g("text"), g("data")))
    return out


def events_of(ev):
    from jpype import JClass
    out = []
    Coll = JClass("java.util.Collection")
    for f_ in ev.getClass().getDeclaredFields():
        f_.setAccessible(True)
        v_ = f_.get(ev)
        if v_ is None or not Coll.class_.isInstance(v_):
            continue
        for e in list(v_):
            sel, parts = None, []
            c = e.getClass()
            while c is not None and str(c.getName()) != "java.lang.Object":
                for g in c.getDeclaredFields():
                    try:
                        g.setAccessible(True)
                        x = g.get(e)
                        if x is None:
                            continue
                        if str(g.getName()) == "selector":
                            sel = str(x)
                        parts.append(str(x))
                        for h in x.getClass().getDeclaredFields():
                            try:
                                h.setAccessible(True)
                                y = h.get(x)
                                if y is not None:
                                    parts.append(str(y))
                            except Exception:
                                pass
                    except Exception:
                        pass
                c = c.getSuperclass()
            out.append((sel, " | ".join(parts)))
    return out


DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")


def unq(d):
    if d is None:
        return ""
    d = str(d)
    try:
        v = json.loads(d)
    except Exception:
        return d
    if isinstance(v, dict) and len(v) == 1:
        v = list(v.values())[0]
    return v if isinstance(v, str) else d


def built(page, what, hub, subs, need=(), forbid=()):
    """build the page for real, then the kit 1.7 checks on what it sent"""
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    try:
        page.build(None, b, ev, None)
    except Exception as e:
        check(False, "%s: build threw %s" % (what, e))
        return None
    cmds, evs = cmds_of(b), events_of(ev)
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, unq(d)) for ty, s, t, d in cmds if ty == "Set"]
    try:
        SUI.check_page(apps, "Skyy")
        check(True, "%s: check_page" % what)
    except Exception as e:
        check(False, "%s: check_page: %s" % (what, e))
    try:
        SUI.check_sky_paths(apps, tab_icons=True)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom" % what)
    except Exception as e:
        check(False, "%s: sky paths: %s" % (what, e))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s, _t in evs if s and s.lstrip("#") not in ids]
    check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(evs), bad[:4]))
    try:
        info = SUI.assert_menu_page(apps, hub=hub, what=what, sets=sets)
        check(info["rows"] == 2 and info["subs"] == 1, "%s: assert_menu_page (1600 x 980, rows 1 + 2, one sub row, no back / pager): %s" % (what, info))
    except Exception as e:
        check(False, "%s: assert_menu_page: %s" % (what, e))
    texts = [m.group(1) for _p, mk in apps for m in re.finditer(r'Text: "([^"]*)"', SUI.render(mk))] + [str(v) for s, v in sets if s.endswith(".Text")]
    old = [t for t in texts if t.strip().lower() in ("close", "back", "prev", "next", "< menu", "back to warps", "< back")]
    check(not old, "%s: no Close / Back / Prev / Next button text: %s" % (what, old))
    subl = [m.group(1) for _p, mk in apps for m in re.finditer(r'TextButton #\w+Sub\d+ \{[^}]*?Text: "([^"]*)"', SUI.render(mk))]
    check(subl == list(subs), "%s: the sub row = %s (got %s)" % (what, list(subs), subl))
    for n in need:
        check(n in ids or n in texts, "%s: has %s" % (what, n))
    for n in forbid:
        check(n not in ids, "%s: has no %s" % (what, n))
    acts = [e for _s, e in evs]
    return {"apps": apps, "sets": sets, "evs": evs, "ids": ids, "acts": acts, "texts": texts}


def bound(r, sel, act):
    return any(s == sel and ('"%s"' % act in e or "a | %s" % act in e or act in e.split(" | ")) for s, e in r["evs"])


# ============================================================================================================== phase menu
def run_menu(jar):
    B = T11.boot(jar)
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride, JShort, JInt
    J = JClass
    W = T11.World(B)
    ES, TC, Pub, TS = J(PKG + "EssStore"), J(PKG + "TCfg"), J(PKG + "CfgPub"), J(PKG + "TStore")
    Page, TCP, WP, HB, TCod = J(PKG + "TradePage"), J(PKG + "TCfgPage"), J(PKG + "WarpPage"), J(PKG + "HubBar"), J(PKG + "TCodec")
    UUID, Paths, Long, Boolean, Integer = J("java.util.UUID"), J("java.nio.file.Paths"), J("java.lang.Long"), J("java.lang.Boolean"), J("java.lang.Integer")
    HashSet, HashMap = J("java.util.HashSet"), J("java.util.HashMap")
    IS = J("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = J("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    W.item("Ingredient_Stick", stack=64)
    W.item("Ore_Copper", stack=64)
    W.item("Weapon_Sword_Iron", 100, 0.21, weapon=True, stack=1)

    # ---------------- U0 the jar
    z = zipfile.ZipFile(jar)
    names = z.namelist()
    cls = [n for n in names if n.endswith(".class")]
    other = sorted(n for n in names if not n.endswith(".class") and n != "manifest.json")
    kit = [n for n in other if n.startswith("Common/UI/Custom/SkyyKit/")]
    check(len(cls) == 73 and (PKG.replace(".", "/") + "HubBar.class") in cls, "U0: 73 classes in the jar (0.1.11's 72 + HubBar): %d" % len(cls))
    check(sorted(set(other) - set(kit)) == ["Server/Item/ResourceTypes/Compost_Soft.json", "Server/Languages/en-US/server.lang"]
          and len(kit) == len(SUI.SKY_FILES), "U0: non-class files = the two Compost_Soft files + %d kit art files (%d)" % (len(SUI.SKY_FILES), len(kit)))
    check(SUI.check_jar_kit(jar) == len(SUI.SKY_FILES), "U0: the kit art is byte-identical to the kit's pinned files")
    man = json.loads(z.read("manifest.json").decode("utf-8-sig"))
    check(man.get("IncludesAssetPack") is True and man.get("Version") == VERSION, "U0: manifest IncludesAssetPack true, version %s" % VERSION)
    check(z.read("Server/Item/ResourceTypes/Compost_Soft.json").decode() == "{}\n", "U0: Compost_Soft.json unchanged")

    # ---------------- stand-in Universe (two online players), SkyyCoins, permissions, the config kit, the trade thread
    Uni = J("com.hypixel.hytale.server.core.universe.Universe")
    PRc = J("com.hypixel.hytale.server.core.universe.PlayerRef")
    Holder = J("com.hypixel.hytale.component.Holder")
    CHM = J("java.util.concurrent.ConcurrentHashMap")
    uni = W.us.allocateInstance(Uni.class_)
    byu = CHM()
    W.fld(Uni, "playersByUuid").set(uni, byu)
    plist = J("java.util.concurrent.CopyOnWriteArrayList")()
    W.fld(Uni, "players").set(uni, plist)
    W.fld(Uni, "instance").set(None, uni)

    def player(name, uid):
        p_ = W.us.allocateInstance(PRc.class_)
        W.fld(PRc, "uuid").set(p_, UUID.fromString(uid))
        W.fld(PRc, "username").set(p_, name)
        W.fld(PRc, "holder").set(p_, W.us.allocateInstance(Holder.class_))
        byu.put(p_.getUuid(), p_)
        plist.add(p_)
        return p_

    pa = player("Alice", "00000000-0000-0000-0000-00000000a11c")
    pb = player("Bob", "00000000-0000-0000-0000-000000000b0b")
    bal = {str(pa.getUuid()): 1000, str(pb.getUuid()): 1000}

    @JImplements("java.util.function.Function")
    class CGet(object):
        @JOverride
        def apply(self, u):
            return Long.valueOf(bal.get(str(u), 0))

    @JImplements("java.util.function.Function")
    class CTake(object):
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(str(a[1]))
            if bal.get(u, 0) < n:
                return Boolean.FALSE
            bal[u] -= n
            return Boolean.TRUE

    @JImplements("java.util.function.Function")
    class CAdd(object):
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(str(a[1]))
            bal[u] = bal.get(u, 0) + n
            return Long.valueOf(bal[u])

    coinfns = [CGet(), CTake(), CAdd()]
    br = TC.bridge()
    br.put("coins:fn:get", coinfns[0])
    br.put("coins:fn:take", coinfns[1])
    br.put("coins:fn:add", coinfns[2])

    def jset(*xs):
        h_ = HashSet()
        for x_ in xs:
            h_.add(x_)
        return h_

    USERS = {str(pa.getUuid()): (["skyyessentials.tradeadmin", "skyyessentials.admin"], ["hytale:Adventurer"]),
             str(pb.getUuid()): ([], ["hytale:Adventurer"])}
    GROUPS = {"hytale:Adventurer": []}

    @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
    class Prov:
        @JOverride
        def getName(self): return "menu-test"
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

    PM = J("com.hypixel.hytale.server.core.permissions.PermissionsModule")
    pm = W.us.allocateInstance(PM.class_)
    provs = J("java.util.ArrayList")()
    provs.add(Prov())
    W.fld(PM, "providers").set(pm, provs)
    W.fld(PM, "virtualGroups").set(pm, HashMap())
    W.fld(PM, "instance").set(None, pm)
    check(bool(pa.hasPermission("skyyessentials.tradeadmin")) and not bool(pb.hasPermission("skyyessentials.tradeadmin")),
          "stand-in permissions: Alice is a trade admin, Bob is not")

    mods = os.path.join(SCRATCH, "menu", "mods")
    home = os.path.join(mods, "Skyy_SkyyEssentials")
    shutil.rmtree(os.path.join(SCRATCH, "menu"), ignore_errors=True)
    os.makedirs(home)
    T11.paths_for(TC, ES, Paths, home)
    TC.load()
    Pub.start(Paths.get(mods), None)
    TS.STOPPING = False
    TS.SAVER = J("java.util.concurrent.Executors").newSingleThreadScheduledExecutor(J(PKG + "TThreads")())
    TC.COUNTDOWN_S = 5

    # the hub contract entries other mods would publish (Object[] { mod, label, order, command, open Function, visible Function })
    opened = []
    dismiss_on_open = []

    @JImplements("java.util.function.Function")
    class Opener(object):
        def __init__(self, key):
            self.key = key

        @JOverride
        def apply(self, u):
            opened.append((self.key, str(u)))
            for pg in list(dismiss_on_open):      # what the engine does when another page opens: the open page is dismissed
                pg.onDismiss(None, None)
            return Boolean.TRUE

    def entry(mod, label, order, key):
        a = JArray(JObject)(6)
        a[0], a[1], a[2], a[3], a[4], a[5] = mod, label, Integer.valueOf(order), None, Opener(key), None
        return a
    for hub_, tab_, mod_, lab_, o_ in (("social", "players", "SkyyMenu", "Players", 10), ("social", "party", "SkyyParty", "Party", 20),
                                       ("social", "guild", "SkyyGuilds", "Guild", 30), ("world", "teleport", "SkyyMenu", "Teleport", 10),
                                       ("settings", "settings", "SkyyMenu", "Settings", 10), ("settings", "setup", "SkyyMenu", "Server Setup", 50)):
        br.put("hub:tab:%s:%s" % (hub_, tab_), entry(mod_, lab_, o_, "%s:%s" % (hub_, tab_)))

    def inv(n, stacks):
        c = SIC(JShort(n))
        for slot, (iid, q) in stacks.items():
            c.setItemStackForSlot(JShort(slot), IS(iid, JInt(q)))
        return c

    def count(*cs):
        tot = {}
        for c in cs:
            for k in range(int(c.getCapacity())):
                st = c.getItemStack(JShort(k))
                if st is None or st.isEmpty():
                    continue
                key = str(st.getItemId())
                tot[key] = tot.get(key, 0) + int(st.getQuantity())
        return tot

    def owed(rec, side):
        tot = {}
        for d in rec.oweCopy(side):
            key = str(TCod.strOf(d, "id"))
            tot[key] = tot.get(key, 0) + int(TCod.intOf(d, "qty", 0))
        return tot

    def add(*ds):
        out = {}
        for d in ds:
            for k, v in d.items():
                out[k] = out.get(k, 0) + v
        return dict((k, v) for k, v in out.items() if v)

    def drag(src, slot, qty, dst, to):
        return bool(src.moveItemStackFromSlotToSlot(JShort(slot), JInt(qty), dst, JShort(to)).succeeded())

    def wait_for(cond, secs=8.0):
        t0 = time.time()
        while not cond() and time.time() - t0 < secs:
            time.sleep(0.05)
        return bool(cond())

    def click(pg, a):
        pg.handleDataEvent(None, None, '{"a":"%s"}' % a)

    # ---------------- U1 the trade page, every view
    invA = inv(12, {0: ("Ingredient_Stick", 20), 1: ("Weapon_Sword_Iron", 1)})
    invB = inv(12, {0: ("Ore_Copper", 30), 1: ("Ingredient_Stick", 5)})
    s = TS.newSession(pa, pb)
    check(s is not None and bool(s.live()), "a live trade (TStore.newSession)")
    box0, box1 = s.box[0], s.box[1]
    total = count(invA, invB, box0, box1)
    check(drag(invA, 0, 12, box0, 0) and drag(invA, 1, 1, box0, 1) and drag(invB, 0, 30, box1, 0), "real items in both escrows")
    check(count(invA, invB, box0, box1) == total, "item totals after the offers")
    pgA, pgB = Page(pa, s, 0, 3), Page(pb, s, 1, 3)
    s.page[0], s.page[1] = pgA, pgB
    TRADE_NEED = ("SkyyTrTitle", "SkyyTrStatus", "SkyyTrMineGrid", "SkyyTrTheirsGrid", "SkyyTrCoinRow", "SkyyTrInfo", "SkyyTrChest",
                  "SkyyTrCancel", "SkyyTrReady", "SkyyTrPBigRow", "SkyyTrPBigTabs", "SkyyTrPHubClose", "SkyyTrPSub0")
    rA = built(pgA, "trade page (Alice, admin, page only)", "social", ["Trade", "Trade settings"], need=TRADE_NEED + ("SkyyTrPSub1", "Edit my offer"))
    if rA:
        check(any(s_ == "#SkyyTrTitle.Text" and v == "Trade with Bob" for s_, v in rA["sets"]), "trade page: the title names the other player")
        check(bound(rA, "#SkyyTrPSub1", "tsettings") and not [s_ for s_, _e in rA["evs"] if s_ == "#SkyyTrPSub0"],
              "trade page: Trade settings bound (tsettings), the selected Trade sub-tab drawn, not bound")
        for sel_, act_ in (("#SkyyTrReady", "ready"), ("#SkyyTrChest", "chest"), ("#SkyyTrCancel", "cancel"), ("#SkyyTrCoinSet", "coins"),
                           ("#SkyyTrPHubClose", "hub:close")):
            check(bound(rA, sel_, act_), "trade page: %s bound to %s" % (sel_, act_))
        tabs = sorted(i for i in rA["ids"] if re.fullmatch(r"SkyyTrPBigT\d+", i))
        check(len(tabs) == 3, "trade page row 2: the three Social tabs (Players, Party, Guild): %s" % tabs)
        check(any("Ready" in t for t in rA["texts"]) and "Open as chest" not in rA["texts"], "trade page: Ready + Edit my offer (no window)")
    rB = built(pgB, "trade page (Bob, not admin)", "social", ["Trade"], need=TRADE_NEED, forbid=("SkyyTrPSub1",))
    pgA.win = W.us.allocateInstance(J(PKG + "TWindow").class_)
    built(pgA, "trade page (Alice, with the offer window)", "social", ["Trade", "Trade settings"], need=TRADE_NEED + ("Open as chest",))
    pgA.win = None
    s.state = 1
    rL = built(pgA, "trade page (locked, countdown)", "social", ["Trade", "Trade settings"], need=TRADE_NEED + ("Not ready",))
    s.state = 0
    br.remove("coins:fn:get")
    built(pgA, "trade page (coins off, no coin offer)", "social", ["Trade", "Trade settings"], need=TRADE_NEED, forbid=("SkyyTrCoin",))
    s.coins[0] = 5
    rC = built(pgA, "trade page (coins off, a coin offer on the table)", "social", ["Trade", "Trade settings"], need=TRADE_NEED + ("SkyyTrCoinClear",))
    s.coins[0] = 0
    br.put("coins:fn:get", coinfns[0])
    pE = Page(pa, None, 0, 3)
    built(pE, "trade page (ended)", "social", ["Trade"], need=("SkyyTrTitle", "SkyyTrEnded", "SkyyTrInfo"), forbid=("SkyyTrReady", "SkyyTrCancel"))
    check(count(invA, invB, box0, box1) == total and bool(s.live()), "building the pages moved nothing")

    # ---------------- U2 ITEM SAFETY: leaving the page through row 1 / row 2 / the X while the countdown runs
    def put_ready():
        a_ = str(TS.clickReady(pgA))
        b_ = str(TS.clickReady(pgB))
        return a_, b_
    ra, rb = put_ready()
    check(ra.startswith("+You are ready") and rb.startswith("+Both ready") and int(s.state) == 1, "both Ready: the countdown runs (%s / %s)" % (ra, rb))
    snap = (count(box0), count(box1), count(invA), count(invB))
    dismiss_on_open[:] = [pgA]
    click(pgA, "hub:party")                       # row 2: another Social tab
    check(opened and opened[-1][0] == "social:party", "row 2 click: the Party tab's open Function ran (%s)" % opened[-1:])
    check(bool(pgA.dismissed) and s.page[0] is None, "row 2 click: the trade page went the dismiss way (TStore.pageDismissed)")
    check(int(s.state) == 0 and not s.ready[0] and bool(s.live()), "row 2 click: countdown stopped, Alice's Ready cleared, the trade stays open")
    check((count(box0), count(box1), count(invA), count(invB)) == snap, "row 2 click: NOTHING moved (both escrows + both inventories)")
    time.sleep(5.6)
    check(bool(s.live()) and str(s.rec.state) != "SETTLING" and (count(box0), count(box1)) == snap[:2], "the stopped countdown never settles the trade")
    # Bob leaves through row 1 (another hub) while Alice is ready again
    pgA2 = Page(pa, s, 0, 3)
    s.page[0] = pgA2
    ra2 = str(TS.clickReady(pgA2))
    rb2 = str(TS.clickReady(pgB))
    check(int(s.state) == 1, "Ready again x2: countdown (%s / %s)" % (ra2, rb2))
    dismiss_on_open[:] = [pgB]
    click(pgB, "hub:h:world")                     # row 1: the World hub (its Teleport tab)
    check(opened[-1][0] == "world:teleport" and bool(pgB.dismissed) and int(s.state) == 0 and not s.ready[1] and bool(s.live()),
          "row 1 click (World): the Teleport page opens, the trade page went the dismiss way, countdown stopped, trade open")
    check((count(box0), count(box1), count(invA), count(invB)) == snap, "row 1 click: NOTHING moved")
    dismiss_on_open[:] = []
    # the X and Home: route answers "close" (the page then closes; the engine runs onDismiss = the same pageDismissed)
    check(str(HB.route(pa, '{"a":"hub:close"}', "social", None)) == "close", "the X: HubBar.route says close")
    check(str(HB.goHub(pa, "home")) == "close", "row 1 Home without SkyyMenu: close")
    pgX = Page(pa, s, 0, 3)
    s.page[0] = pgX
    click(pgX, "hub:close")                       # close() needs the real page manager; the engine then calls onDismiss:
    pgX.onDismiss(None, None)
    check(bool(pgX.dismissed) and bool(s.live()) and (count(box0), count(box1), count(invA), count(invB)) == snap,
          "the X: dismissed the Esc way, the trade stays open, nothing moved")
    # a click the bar does not know leaves the page as it was
    pgY = Page(pb, s, 1, 3)
    s.page[1] = pgY
    br.remove("hub:tab:social:guild")
    click(pgY, "hub:guild")
    check(not bool(pgY.dismissed) and str(pgY.info).startswith("-That page could not open"), "a missing tab: the result line says so, the page stays (%s)" % pgY.info)
    click(pgY, "tsettings")
    check(str(pgY.info).startswith("-You do not have permission to change the trade settings"), "Bob's Trade settings click is refused: %s" % pgY.info)
    # finally Cancel trade: everything back to its owner
    TS.clickCancel(pgY)
    check(wait_for(lambda: str(s.rec.state) == "SETTLING") and str(s.rec.result) == "CANCELLED", "Cancel trade after all that: CANCELLED")
    check(count(box0, box1) == {} and add(count(invA, invB), owed(s.rec, 0), owed(s.rec, 1)) == total,
          "item totals conserved: inventories + what the trade owes = the totals before (%s)" % add(count(invA, invB), owed(s.rec, 0), owed(s.rec, 1)))
    check(owed(s.rec, 0) == {"Ingredient_Stick": 12, "Weapon_Sword_Iron": 1} and owed(s.rec, 1) == {"Ore_Copper": 30},
          "each player is owed exactly their own offer back")

    # ---------------- U1b Trade settings / Teleport and message settings
    tA = TCP(pa, 0)
    rT = built(tA, "Trade settings (Alice)", "social", ["Trade", "Trade settings"], need=("SkyyTcList", "SkyyTcRow0", "SkyyTcReload", "SkyyTcInfo"))
    if rT:
        nrows = len([i for i in rT["ids"] if re.fullmatch(r"SkyyTcRow\d+", i)])
        check(nrows == len(list(TCP.TRADE_KEYS)), "Trade settings: every row in ONE scroll list (%d)" % nrows)
        check(bound(rT, "#SkyyTcPSub0", "trade") and bound(rT, "#SkyyTcReload", "reload"), "Trade settings: the Trade sub-tab + Reload bound")
    tA.pendQ, tA.pendKey, tA.pendVal = "Turn trading off?", "part.trade", "false"
    built(tA, "Trade settings (a danger-row question)", "social", ["Trade", "Trade settings"], need=("SkyyTcYes", "SkyyTcNo"), forbid=("SkyyTcReload",))
    tA.pendQ = tA.pendKey = tA.pendVal = None
    built(TCP(pb, 0), "Trade settings (Bob, no permission)", "social", ["Trade", "Trade settings"], need=("SkyyTcInfo",))
    rS = built(TCP(pa, 1), "Teleport and message settings", "settings", ["Warps", "Teleport and messages"], need=("SkyyTcList", "SkyyTcRow0"))
    if rS:
        rh = [int(m.group(1)) for _p, mk in rS["apps"] for m in [re.search(r"#SkyyTcRow0 \{ Anchor: \(Height: (\d+)\)", SUI.render(mk))] if m]
        check(rh and rh[0] > 42, "Teleport and message settings: 6 rows grow to fill the list (rule 7): %s" % rh)
        check(bound(rS, "#SkyyTcPSub0", "warps"), "Teleport and message settings: the Warps sub-tab bound (warps)")
    click(tA, "trade")
    check(str(tA.info).startswith("=You have no trade open right now"), "the Trade sub-tab with no open trade says so: %s" % tA.info)

    # ---------------- U1c the warps editor
    TPP = J("com.hypixel.hytale.builtin.teleport.TeleportPlugin")
    Warp = J("com.hypixel.hytale.builtin.teleport.Warp")
    tp = W.us.allocateInstance(TPP.class_)
    fl = list(TPP.class_.getDeclaredFields())
    inst = [f for f in fl if J("java.lang.reflect.Modifier").isStatic(f.getModifiers()) and f.getType() == TPP.class_]
    wmap = [f for f in fl if not J("java.lang.reflect.Modifier").isStatic(f.getModifiers()) and J("java.util.Map").class_.isAssignableFrom(f.getType())]
    loadf = [f for f in fl if not J("java.lang.reflect.Modifier").isStatic(f.getModifiers()) and str(f.getType().getName()) in ("boolean", "java.util.concurrent.atomic.AtomicBoolean")]
    check(len(inst) == 1 and len(wmap) >= 1 and len(loadf) >= 1, "TeleportPlugin stand-in fields: %s" % [str(f.getName()) for f in fl])
    WARPS = CHM()
    for f in inst:
        f.setAccessible(True)
        f.set(None, tp)
    for f in wmap:
        f.setAccessible(True)
        f.set(tp, WARPS)

    def loaded(v):
        for f in loadf:
            f.setAccessible(True)
            if str(f.getType().getName()) == "boolean":
                f.setBoolean(tp, v)
            else:
                f.set(tp, J("java.util.concurrent.atomic.AtomicBoolean")(v))

    def mkwarp(name):
        w_ = Warp()
        for f in Warp.class_.getDeclaredFields():
            f.setAccessible(True)
            n_, t_ = str(f.getName()), str(f.getType().getName())
            if n_ == "id":
                f.set(w_, name)
            elif n_ == "world":
                f.set(w_, "default")
            elif n_ == "creator":
                f.set(w_, "Alice")
        WARPS.put(name.lower(), w_)

    wA = WP(pa)
    loaded(False)
    built(wA, "warps editor (warps still loading)", "settings", ["Warps", "Teleport and messages"], need=("SkyyWpEmpty", "SkyyWpAdd", "SkyyWpRefresh"))
    loaded(True)
    check(J(PKG + "EssWarp").tp() is not None, "the TeleportPlugin stand-in is loaded")
    built(wA, "warps editor (no warps)", "settings", ["Warps", "Teleport and messages"], need=("SkyyWpEmpty", "SkyyWpAdd"))
    for n_ in ("hub", "mine", "spawn2"):
        mkwarp(n_)
    rW = built(wA, "warps editor (3 warps)", "settings", ["Warps", "Teleport and messages"], need=("SkyyWpRow0", "SkyyWpRow2", "SkyyWpGo0", "SkyyWpRm2"),
               forbid=("SkyyWpRow3", "SkyyWpEmpty", "SkyyWpMore"))
    if rW:
        rh = [int(m.group(1)) for _p, mk in rW["apps"] for m in [re.search(r"#SkyyWpRow0 \{ Anchor: \(Height: (\d+)\)", SUI.render(mk))] if m]
        check(rh and rh[0] > 50, "warps editor: 3 rows grow (rule 7): %s" % rh)
        check(bound(rW, "#SkyyWpPSub1", "settings") and bound(rW, "#SkyyWpGo0", "go:0") and bound(rW, "#SkyyWpRm2", "rm:2")
              and bound(rW, "#SkyyWpAdd", "add") and bound(rW, "#SkyyWpRefresh", "refresh"), "warps editor: sub-tab + row + add + refresh bound")
        check(list(wA.ids) == ["hub", "mine", "spawn2"], "warps editor: the row ids the clicks read: %s" % list(wA.ids))
    for k_ in range(227):
        mkwarp("w%03d" % k_)
    rM = built(wA, "warps editor (230 warps)", "settings", ["Warps", "Teleport and messages"], need=("SkyyWpRow199", "SkyyWpMore"), forbid=("SkyyWpRow200",))
    click(wA, "more")
    check(int(wA.cap) == 400, "Show more adds 200 (%d)" % int(wA.cap))
    built(wA, "warps editor (all 230 warps)", "settings", ["Warps", "Teleport and messages"], need=("SkyyWpRow229",), forbid=("SkyyWpMore",))
    wA.cKind, wA.cId = "rm", "hub"
    built(wA, "warps editor (the remove confirm)", "settings", ["Warps", "Teleport and messages"], need=("SkyyWpQ", "SkyyWpYes", "SkyyWpNoBtn"),
          forbid=("SkyyWpList",))
    click(wA, "no")
    check(wA.cKind is None and str(wA.info) == "=Nothing was changed." and WARPS.get("hub") is not None, "the remove confirm's Cancel: nothing removed")
    built(WP(pb), "warps editor (Bob, no permission)", "settings", ["Warps", "Teleport and messages"], need=("SkyyWpNo",), forbid=("SkyyWpList",))

    # ---------------- U4 bytecode
    import skyybuild as _B
    pool = J("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    pool.appendClassPath(_B.SERVER_JAR)
    IP = J("javassist.bytecode.InstructionPrinter")
    PS, BOS = J("java.io.PrintStream"), J("java.io.ByteArrayOutputStream")

    def code(c, meth):
        out = []
        for mm in pool.get(PKG + c).getDeclaredMethods():
            if str(mm.getName()) == meth:
                bos = BOS()
                IP(PS(bos)).print_(mm)
                out += str(bos.toString()).splitlines()
        return out

    def calls(lines):
        return [m.group(1) for l in lines for m in [re.search(r"Method ([\w.$]+)\(", l)] if m]
    for c in ("TradePage", "TCfgPage", "WarpPage"):
        h = calls(code(c, "handleDataEvent"))
        check(h and h[0].endswith(c + ".hubClick"), "%s.handleDataEvent asks hubClick first: %s" % (c, h[:2]))
        hc = calls(code(c, "hubClick"))
        check(all(any(x.endswith(n) for x in hc) for n in ("HubBar.route", "HubBar.goHub", ".close", ".hubAck", ".rebuild")),
              "%s.hubClick: route / goHub / close / hubAck / rebuild: %s" % (c, hc))
    od = calls(code("TradePage", "onDismiss"))
    check(od == [PKG + "TStore.pageDismissed"], "TradePage.onDismiss still only calls TStore.pageDismissed: %s" % od)
    hd = calls(code("TradePage", "handleDataEvent"))
    check((PKG + "TCfgPage.<init>") in [x.replace("TCfgPage.<init>", "TCfgPage.<init>") for x in hd] or any("TCfgPage.<init>" in l for l in code("TradePage", "handleDataEvent")),
          "TradePage: the Trade settings sub-tab opens TCfgPage(0)")
    op_ = code("EssWarp", "open")
    check(any("WarpPage.<init>" in l for l in op_) and any("openCustomPage" in l for l in op_), "/warpadmin still opens the WarpPage (EssWarp.open)")
    allstr = b"".join(zipfile.ZipFile(jar).read(n) for n in zipfile.ZipFile(jar).namelist() if n.endswith("Cmd.class"))
    check(b"warpadmin" in allstr and not re.search(rb"\x00\x04warp", allstr), "no command class registers /warp (vanilla /warp <name> stays)")
    print("menu phase: pages built, item safety, clicks, bytecode done")


# ============================================================================================================== Z. class byte-compare
def compare_jars():
    from cpstrings import read_utf8_constants
    if not os.path.isfile(PREV_JAR):
        check(False, "Z: no %s to compare with" % PREV_JAR)
        return
    za, zb = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
    ca = dict((n, za.read(n)) for n in za.namelist() if n.endswith(".class"))
    cb = dict((n, zb.read(n)) for n in zb.namelist() if n.endswith(".class"))
    short = lambda n: n.rsplit("/", 1)[-1][:-6]
    gone = sorted(short(n) for n in set(ca) - set(cb))
    new = sorted(short(n) for n in set(cb) - set(ca))
    same = sorted(short(n) for n in set(ca) & set(cb) if ca[n] == cb[n])
    changed = sorted(n for n in set(ca) & set(cb) if ca[n] != cb[n])
    check(not gone, "Z: no class removed: %s" % gone)
    check(new == ["HubBar"], "Z: one new class, HubBar: %s" % new)
    expected = {"TradePage", "TCfgPage", "WarpPage"}
    ver_only = []
    for n in changed:
        if short(n) in expected:
            continue
        sa, sb = set(read_utf8_constants(ca[n])), set(read_utf8_constants(cb[n]))
        da, db = sorted(sa - sb), sorted(sb - sa)
        ok = sorted(x.replace(PREV, VERSION) for x in da) == db
        ver_only.append(short(n))
        check(ok, "Z: %s differs in more than the version text: %s -> %s" % (short(n), da[:4], db[:4]))
    cs = sorted(short(n) for n in changed)
    check(expected <= set(cs), "Z: the three page classes changed: %s" % sorted(expected & set(cs)))
    cmds = ["TpaCmd", "TpaHereCmd", "TpAcceptCmd", "TpAcceptNamedCmd", "TpDenyCmd", "TpDenyNamedCmd", "TpaCancelCmd", "MsgCmd", "ReplyCmd",
            "RCmd", "EssFn", "ChatMirror", "ChatMirrorF", "TStore", "TSession", "TCodec", "TWindow", "TBlock", "TBlockF", "EssWarp"]
    check(all(c_ in same for c_ in cmds), "Z: commands, the trade logic (TStore / TSession / TCodec / TWindow / TBlock; TRecord = version text) and EssWarp are "
          "byte-identical: %s" % [c_ for c_ in cmds if c_ not in same])
    print("Z. byte-compare %s -> %s: %d identical, new %s, changed on purpose %s, version text only %s" % (
        PREV, VERSION, len(same), new, sorted(expected & set(cs)), ver_only))


def main():
    ph = T11.arg("--phase")
    if "--run" in sys.argv:
        jar = T11.arg("--run")
        if ph == "menu":
            run_menu(jar)
        elif ph == "main":
            T11.run_main(jar)
        elif ph == "trade":
            T11.run_trade(jar)
        elif ph == "tpa":
            T11.run_tpa(jar)
        elif ph == "chat":
            T11.run_chat(jar)
        elif ph == "keep":
            T11.run_keep(jar)
        elif ph == "compost":
            T11.run_compost(jar)
        else:
            T11.run_live(jar, ph)
        for s_ in SKIPPED:
            print("  superseded:", s_)
        print("%s: %d checks passed, %d failed, %d superseded" % (ph, OKS[0], len(FAILS), len(SKIPPED)))
        for f in FAILS:
            print("  FAILED:", f)
        sys.stdout.flush()
        os._exit(1 if FAILS else 0)
    if not os.path.isfile(JAR):
        sys.exit("no jar at %s - build it first (python SkyyEssentials/build_skyyessentials_%s.py)" % (JAR, VERSION))
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    rc = 0
    only = T11.arg("--only")
    for ph in ("menu", "main", "trade", "tpa", "chat", "keep", "compost"):
        if only and ph not in only.split(","):
            continue
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--phase", ph, "--dir", SCRATCH], env=env)
        print("phase %s: %s" % (ph, "ok" if p.returncode == 0 else "FAIL"))
        rc |= p.returncode
    if not only:
        if os.path.isdir(T11.LIVE):
            dstl = os.path.join(SCRATCH, "live", "mods", "Skyy_SkyyEssentials")
            shutil.copytree(T11.LIVE, dstl)
            for ph in ("live1", "live2"):
                p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--phase", ph, "--dir", SCRATCH], env=env)
                print("phase %s: %s" % (ph, "ok" if p.returncode == 0 else "FAIL"))
                rc |= p.returncode
        else:
            print("FAIL no live folder at %s" % T11.LIVE)
            rc |= 1
    compare_jars()
    print("Z: %d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    rc |= 1 if FAILS else 0
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyEssentials %s bare-JVM check:" % VERSION, "PASS" if rc == 0 else "FAIL")
    sys.exit(rc)


if __name__ == "__main__":
    main()
