"""Bare-JVM check for SkyyEssentials 0.1.14 (warp icons; tools/essentials_0_1_14_patch.py). Build first:
    python tools/essentials_0_1_14_patch.py && python SkyyEssentials/build_skyyessentials_0.1.14.py

    python SkyyEssentials/test_skyyessentials_0.1.14.py [--jar <SkyyEssentials-0.1.14.jar>] [--dir <scratch folder>] [--keep] [--only wicon,...]

The 0.1.13 harness (test_skyyessentials_0.1.13.py, loaded as a module; it loads 0.1.12's and 0.1.11's) runs its phases back / menu / main /
trade / tpa / chat / keep / compost / live1 / live2 against this jar, each in a fresh JVM; the checks that change ON PURPOSE (the class
count) are listed in SUPERSEDED and re-checked here. Then:
  phase wicon (a fresh JVM, -Xverify:all; stand-in Universe with an admin (Alice) and a player (Bob), stand-in TeleportPlugin with warps,
  stand-in item map holding two of SkyyMenu's icon items):
    I1 the theme table = art/warp-icons/manifest.json (warp first = the signpost), EssWIcon.get / label / item defaults
    I2 a pick saved: set -> warpicons.properties (atomic: no .tmp left, our header, one 'id=theme' line, warp = no line); load reads it
       back after a "restart"; a bad line / unknown theme is skipped; rename carries the icon, remove drops it
    I3 the bridge essentials:fn:warps -> '<id>|<theme>' for every warp A-Z (published by EssBack.publish with the homes functions, removed
       by EssBack.stop)
    I4 the /warpadmin page: every row has an Icon button bound to ic:<row> with the theme's name; ic:<row> opens the PICK view (kit 1.7
       rules + assert_menu_page): one button per theme bound pk:<k>, the current one Primary, a picture only where the icon item exists,
       Cancel (pno); pk:<k> saves (file + EssWIcon) and writes a config-changes.log line; Cancel changes nothing; Add warp here opens the
       pick for the new warp; Bob (no admin) gets the no-permission page and pk: changes nothing
  Z  class byte-compare 0.1.13 -> 0.1.14: only the listed classes differ, EssWIcon is the one new class
NOT runnable in a bare JVM: the pictures on the client, a real vanilla warp file. Default scratch: tools/dev/scratch/tp37/ess (deleted unless --keep).
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "dev"))
import skyyui as SUI

_s13 = importlib.util.spec_from_file_location("test_skyyessentials_0_1_13", os.path.join(HERE, "test_skyyessentials_0.1.13.py"))
T13 = importlib.util.module_from_spec(_s13)
_s13.loader.exec_module(T13)
T12, T11 = T13.T12, T13.T11

VERSION = "0.1.14"
PREV = "0.1.13"
PKG = "com.skyy.essentials."
SCRATCH = os.path.abspath(T11.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "tp37", "ess")))
JAR = os.path.abspath(T11.arg("--jar", os.path.join(HERE, "SkyyEssentials-%s.jar" % VERSION)))
PREV_JAR = os.path.join(HERE, "SkyyEssentials-%s.jar" % PREV)
KEEP = "--keep" in sys.argv
for _m in (T11, T12, T13):
    _m.VERSION, _m.SCRATCH, _m.JAR, _m.KEEP = VERSION, SCRATCH, JAR, KEEP
T13.PREV, T13.PREV_JAR = PREV, PREV_JAR

SUPERSEDED = list(T13.SUPERSEDED) + [
    (re.compile(r"^S0: 89 classes in the jar"), "90 classes (+ EssWIcon) - checked in phase wicon Z / compare"),
    (re.compile(r"^U0: 89 classes"), "90 classes (+ EssWIcon)"),
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


def old_check(cond, what):
    if not cond:
        for rx, why in SUPERSEDED:
            if rx.search(str(what)):
                SKIPPED.append("%s  -> %s" % (str(what)[:120], why))
                return
    check(cond, what)


T11.check = old_check
T12.check = old_check
T13.check = old_check
T13.SUPERSEDED = SUPERSEDED
WIM = json.load(open(os.path.join(ROOT, "art", "warp-icons", "manifest.json"), encoding="utf8"))
THEMES = [r["theme"] for r in WIM["reused"]] + [i["theme"] for i in WIM["icons"]]


# ============================================================================================================== phase wicon
def run_wicon(jar):
    B = T11.boot(jar)
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    J = JClass
    W = T11.World(B)
    ES, TC, Pub, WI, WP = J(PKG + "EssStore"), J(PKG + "TCfg"), J(PKG + "CfgPub"), J(PKG + "EssWIcon"), J(PKG + "WarpPage")
    BK, EW = J(PKG + "EssBack"), J(PKG + "EssWarp")
    UUID, Paths, Integer, Boolean = J("java.util.UUID"), J("java.nio.file.Paths"), J("java.lang.Integer"), J("java.lang.Boolean")
    HashSet, HashMap, CHM = J("java.util.HashSet"), J("java.util.HashMap"), J("java.util.concurrent.ConcurrentHashMap")
    W.item("Skyy_Menu_Icon_Warp", stack=1)          # two of SkyyMenu's icon items exist on this "server"
    W.item("Skyy_Menu_Icon_WarpMining", stack=1)

    # ---------------- I1 the table
    check([str(x) for x in WI.THEME] == THEMES and str(WI.THEME[0]) == "warp", "I1: EssWIcon.THEME = art/warp-icons (warp first): %s" % [str(x) for x in WI.THEME])
    check(str(WI.ITEM[THEMES.index("mining")]) == "Skyy_Menu_Icon_WarpMining" and str(WI.item("nope")) == "Skyy_Menu_Icon_Warp"
          and str(WI.label("fishing")) == "Fishing" and str(WI.get("anything")) == "warp", "I1: item / label / default theme")
    check(bool(WI.has("Skyy_Menu_Icon_WarpMining")) and not bool(WI.has("Skyy_Menu_Icon_WarpBoss")), "I1: has() = the item map (SkyyMenu's items)")

    # ---------------- stand-in Universe, permissions, paths (the 0.1.12 menu phase's fixture)
    Uni = J("com.hypixel.hytale.server.core.universe.Universe")
    PRc = J("com.hypixel.hytale.server.core.universe.PlayerRef")
    Holder = J("com.hypixel.hytale.component.Holder")
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

    def jset(*xs):
        h_ = HashSet()
        for x_ in xs:
            h_.add(x_)
        return h_
    USERS = {str(pa.getUuid()): (["skyyessentials.admin"], ["hytale:Adventurer"]), str(pb.getUuid()): ([], ["hytale:Adventurer"])}

    @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
    class Prov:
        @JOverride
        def getName(self): return "wicon-test"
        @JOverride
        def getUserPermissions(self, u): return jset(*USERS.get(str(u), ([], []))[0])
        @JOverride
        def getGroupsForUser(self, u): return jset(*USERS.get(str(u), ([], []))[1])
        @JOverride
        def getGroupPermissions(self, g): return HashSet()
        @JOverride
        def getEffectiveGroupPermissions(self, g): return HashSet()
        @JOverride
        def getGroupParent(self, g): return None
        @JOverride
        def getAllRegisteredGroups(self): return jset("hytale:Adventurer")
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
    mods = os.path.join(SCRATCH, "wicon", "mods")
    home = os.path.join(mods, "Skyy_SkyyEssentials")
    shutil.rmtree(os.path.join(SCRATCH, "wicon"), ignore_errors=True)
    os.makedirs(home)
    T11.paths_for(TC, ES, Paths, home)
    TC.load()
    Pub.start(Paths.get(mods), None)
    br = TC.bridge()

    def entry(mod, label, order):
        a = JArray(JObject)(6)
        a[0], a[1], a[2], a[3], a[4], a[5] = mod, label, Integer.valueOf(order), None, None, None
        return a
    for hub_, tab_, mod_, lab_, o_ in (("world", "teleport", "SkyyMenu", "Teleport", 10), ("settings", "settings", "SkyyMenu", "Settings", 10),
                                       ("settings", "setup", "SkyyMenu", "Server Setup", 50)):
        br.put("hub:tab:%s:%s" % (hub_, tab_), entry(mod_, lab_, o_))

    # ---------------- the stand-in TeleportPlugin
    TPP = J("com.hypixel.hytale.builtin.teleport.TeleportPlugin")
    Warp = J("com.hypixel.hytale.builtin.teleport.Warp")
    Mod = J("java.lang.reflect.Modifier")
    tp = W.us.allocateInstance(TPP.class_)
    fl = list(TPP.class_.getDeclaredFields())
    WARPS = CHM()
    for f in fl:
        f.setAccessible(True)
        if Mod.isStatic(f.getModifiers()) and f.getType() == TPP.class_:
            f.set(None, tp)
        elif not Mod.isStatic(f.getModifiers()) and J("java.util.Map").class_.isAssignableFrom(f.getType()):
            f.set(tp, WARPS)
        elif not Mod.isStatic(f.getModifiers()) and str(f.getType().getName()) == "boolean":
            f.setBoolean(tp, True)
        elif not Mod.isStatic(f.getModifiers()) and str(f.getType().getName()) == "java.util.concurrent.atomic.AtomicBoolean":
            f.set(tp, J("java.util.concurrent.atomic.AtomicBoolean")(True))

    def mkwarp(name):
        w_ = Warp()
        for f in Warp.class_.getDeclaredFields():
            f.setAccessible(True)
            n_ = str(f.getName())
            if n_ == "id":
                f.set(w_, name)
            elif n_ == "world":
                f.set(w_, "default")
            elif n_ == "creator":
                f.set(w_, "Alice")
        WARPS.put(name.lower(), w_)
    for n_ in ("Mines", "dock", "hub"):
        mkwarp(n_)
    check(EW.tp() is not None and [str(x) for x in EW.ids()] == ["dock", "hub", "Mines"], "SETUP: 3 warps A-Z: %s" % [str(x) for x in EW.ids()])

    # ---------------- I2 the store
    f = os.path.join(home, "warpicons.properties")
    check(str(WI.load(Paths.get(f))) == "no warp icons yet", "I2: no file yet")
    check(bool(WI.set("Mines", "mining")) and str(WI.get("mines")) == "mining", "I2: set Mines = mining (any case)")
    txt = open(f, encoding="utf8").read()
    check(txt.startswith("# SkyyEssentials warp icons") and "mines=mining\n" in txt and not os.path.exists(f + ".tmp"),
          "I2: warpicons.properties written (header + 'mines=mining', no .tmp left)")
    check(bool(WI.set("dock", "fishing")) and bool(WI.set("dock", "warp")) and "dock=" not in open(f, encoding="utf8").read(),
          "I2: picking the signpost (warp) removes the line")
    check(not bool(WI.set("dock", "nosuch")) and str(WI.get("dock")) == "warp", "I2: an unknown theme is refused")
    open(f, "a", encoding="utf8").write("bad line\nhub=nosuch\nhub=hub\n")
    WI.MAP.clear()
    r_ = str(WI.load(Paths.get(f)))
    check(r_ == "2 warp icons" and str(WI.get("hub")) == "hub" and str(WI.get("mines")) == "mining", "I2: load after a restart: %s; bad lines skipped" % r_)
    WI.rename("Mines", "Quarry")
    check(str(WI.get("quarry")) == "mining" and str(WI.get("mines")) == "warp" and "quarry=mining" in open(f, encoding="utf8").read(), "I2: rename carries the icon")
    WI.remove("quarry")
    check(str(WI.get("quarry")) == "warp" and "quarry" not in open(f, encoding="utf8").read(), "I2: remove drops it")
    WI.set("Mines", "mining")

    # ---------------- I3 the bridge
    BK.publish()
    fw = br.get("essentials:fn:warps")
    got = [str(x) for x in fw.apply(None)] if fw is not None else None
    check(got == ["dock|warp", "hub|hub", "Mines|mining"], "I3: essentials:fn:warps -> '<id>|<theme>' A-Z: %s" % got)
    check([str(x) for x in BK.FN_KEYS] == ["essentials:fn:homes", "essentials:fn:gohome", "essentials:fn:back", "essentials:fn:warps"],
          "I3: FN_KEYS = the 0.1.13 three + warps")

    # ---------------- I4 the page
    def click(pg, a):
        pg.handleDataEvent(None, None, '{"a":"%s"}' % a)
    T12.click = click
    wA = WP(pa)
    rL = T12.built(wA, "warps editor (with Icon column)", "settings", ["Warps", "Teleport and messages"], need=("SkyyWpIc0", "SkyyWpIc2", "SkyyWpGo0"))
    if rL:
        check(T12.bound(rL, "#SkyyWpIc0", "ic:0") and T12.bound(rL, "#SkyyWpIc2", "ic:2"), "I4: every row's Icon button is bound to ic:<row>")
        sets = dict(rL["sets"])
        check(sets.get("#SkyyWpIc0.Text") == "Signpost" and sets.get("#SkyyWpIc2.Text") == "Mining", "I4: the Icon button shows the theme's name (%s / %s)" % (sets.get("#SkyyWpIc0.Text"), sets.get("#SkyyWpIc2.Text")))
    T12.click(wA, "ic:2")
    check(str(wA.pickId) == "Mines", "I4: ic:2 opens the pick for Mines")
    rP = T12.built(wA, "warps editor (icon pick)", "settings", ["Warps", "Teleport and messages"], need=("SkyyWpPkQ", "SkyyWpPkB0", "SkyyWpPkNo"), forbid=("SkyyWpList",))
    if rP:
        n = len(THEMES)
        check(all(T12.bound(rP, "#SkyyWpPkB%d" % k, "pk:%d" % k) for k in range(n)), "I4: one pick button per theme (%d), bound pk:<k>" % n)
        check(T12.bound(rP, "#SkyyWpPkNo", "pno"), "I4: Cancel bound (pno)")
        mi = THEMES.index("mining")
        ren = [SUI.render(mk) for _p, mk in rP["apps"]]
        prim = [k for k in range(n) if any(re.search(r"TextButton #SkyyWpPkB%d \{" % k, t) and "Primary" in t for t in ren)]
        check(prim == [mi], "I4: the current theme (Mining) is the Primary button: %s" % prim)
        pics = sorted(int(m.group(1)) for t in ren for m in [re.search(r"ItemIcon #SkyyWpPkI(\d+) ", t)] if m)
        check(pics == sorted([0, mi]), "I4: a picture only where the icon item exists (warp + mining): %s" % pics)
    fi = THEMES.index("fishing")
    T12.click(wA, "pk:%d" % fi)
    check(wA.pickId is None and str(WI.get("mines")) == "fishing" and "mines=fishing" in open(f, encoding="utf8").read()
          and str(wA.info).startswith("+Warp Mines now shows the Fishing icon"), "I4: pk:<k> saves the pick (%s)" % str(wA.info))
    T12.click(wA, "ic:0")
    T12.click(wA, "pno")
    check(wA.pickId is None and str(WI.get("dock")) == "warp" and "No icon" in str(wA.info), "I4: Cancel changes nothing")
    wB = WP(pb)
    T12.built(wB, "warps editor (Bob, no permission)", "settings", ["Warps", "Teleport and messages"], need=("SkyyWpNo",), forbid=("SkyyWpList", "SkyyWpPkQ"))
    wB.pickId = "Mines"
    T12.click(wB, "pk:0")
    check(str(WI.get("mines")) == "fishing", "I4: Bob's forged pk: changes nothing (guard first)")
    BK.stop()
    check(br.get("essentials:fn:warps") is None, "I3: EssBack.stop removes essentials:fn:warps")
    Pub.shutdown()                # the kit flushes config-changes.log
    clog = ""
    for root_, _d, fs_ in os.walk(mods):
        for fn_ in fs_:
            if "change" in fn_:
                clog += open(os.path.join(root_, fn_), encoding="utf8", errors="replace").read()
    check("warpicon[Mines]" in clog, "I4: the pick is a config-changes.log line (warpicon[Mines]): %s" % clog[-300:])
    print("wicon phase done")


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
    changed = sorted(short(n) for n in set(ca) & set(cb) if ca[n] != cb[n])
    check(not gone and new == ["EssWIcon"], "Z: no class removed, EssWIcon new: %s / %s" % (gone, new))
    expected = {"SkyyEssentialsPlugin", "WarpPage", "EssWarp", "EssHFn", "EssBack"}
    other = [c for c in changed if c not in expected]
    bad = []
    for c in other:
        n = PKG.replace(".", "/") + c + ".class"
        sa, sb = set(read_utf8_constants(ca[n])), set(read_utf8_constants(cb[n]))
        if sorted(x.replace(PREV, VERSION) for x in sa - sb) != sorted(sb - sa):
            bad.append(c)
    check(not bad, "Z: every other changed class differs only in the version text: %s" % bad)
    check({"WarpPage", "EssWarp", "SkyyEssentialsPlugin"} <= set(changed), "Z: WarpPage + EssWarp + the plugin changed: %s" % changed)
    keep = ["TpaCmd", "MsgCmd", "TStore", "TradePage", "HubBar", "EssDur", "EssHome", "EssBackSys"]   # (TCfgPage: its version text only)
    check(all(short_ not in changed for short_ in keep), "Z: tpa / msg / trade / homes / hook byte-identical: %s" % [c for c in keep if c in changed])
    print("Z. byte-compare %s -> %s: new %s, changed %s (version text only: %s)" % (PREV, VERSION, new, changed, [c for c in other if c not in bad]))


def main():
    ph = T11.arg("--phase")
    if "--run" in sys.argv:
        jar = T11.arg("--run")
        if ph == "wicon":
            run_wicon(jar)
        elif ph == "back":
            T13.run_back(jar)
        elif ph == "menu":
            T12.run_menu(jar)
        elif ph in ("main", "trade", "tpa", "chat", "keep", "compost"):
            getattr(T11, "run_" + ph)(jar)
        else:
            T11.run_live(jar, ph)
        tf = list(T13.FAILS)
        for s_ in SKIPPED:
            print("  superseded:", s_)
        print("%s: %d checks passed, %d failed, %d superseded" % (ph, OKS[0], len(FAILS) + len(tf), len(SKIPPED)))
        for f in FAILS + tf:
            print("  FAILED:", f)
        sys.stdout.flush()
        os._exit(1 if FAILS or tf else 0)
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
    for ph in ("wicon", "back", "menu", "main", "trade", "tpa", "chat", "keep", "compost"):
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
