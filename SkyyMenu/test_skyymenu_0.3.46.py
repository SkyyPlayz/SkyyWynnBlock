"""Harness for SkyyMenu 0.3.46 (no more menu item in the hotbar - Left Alt opens the Menu; tools/menu_0_3_46_patch.py). Build first:
    python tools/menu_0_3_46_patch.py && python SkyyMenu/build_skyymenu_0.3.46.py
    python SkyyMenu/test_skyymenu_0.3.46.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the SkyyMenu 0.3.19 engine stand-ins, -Xverify:all):
  S    static   the patch re-runs to identical bytes; no new system / command; line endings kept; the item JSON byte-identical to 0.3.45's
               (the id stays defined, right-click still opens the Menu); the tooltip / intro / Mods / Server Setup texts
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.45 -> 0.3.46: exactly the listed members differ (MenuHotkey + HotkeyOpen = the Left-Alt path: NOT listed = identical)
  OFF  EXECUTED - the real GrantTask (IO step + world step) on stand-in players:
       NOGIVE  giveItem OFF by default (MenuCfg, the Server Setup row, the default file): a join with no item -> nothing given, no
               given-profile record, the player's marker written (0 taken)
       ONCE    a join holding 3 Skyy_Menu (hotbar slot 9 + storage) + Skyy_Menu_Icon_Back + bread -> exactly the 3 Skyy_Menu taken
               (every other stack kept), one chat line, the marker says 3; a SECOND join (session cleared, a new copy in the hotbar)
               takes nothing and never hops to the world thread; after a "restart" (memory cleared) the marker file still stops it;
               profile:busy -> planHeld waits (2), nothing taken
       ON      giveItem ON = 0.3.45: a fresh join gets ONE item, no removal
       CMD     /skymenu with giveItem OFF opens the Menu and gives nothing; ON gives a lost one (0.3.45)
       MIG     the one-time giveItem update: an old-default file (CRLF) -> only that line becomes giveItem=false (every other byte
               kept), a VERIFIED History copy = the old bytes, a Changes line menu.giveItem true -> false status ok, the marker; a
               second start changes nothing (even after an Undo back to true); hand-edited lines (false, on, " = true", two lines)
               kept; no file = marker only, init writes giveItem=false; MenuCfg.load reads them
       ALT     the Left-Alt path: walkStep fires on the press; the real MenuHotkey.tick with walking=true queues ONE HotkeyOpen (walk),
               the world task opens the SkyWynn Menu (main view) - also for a player whose item was just taken
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, subprocess, time, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "dev"))
import harness_kit as HK
import skyybuild as B

_s45 = importlib.util.spec_from_file_location("test_skyymenu_0_3_45", os.path.join(HERE, "test_skyymenu_0.3.45.py"))
T45 = importlib.util.module_from_spec(_s45)
_s45.loader.exec_module(T45)
T35 = T45.T35
T19 = T45.T19

VERSION = "0.3.46"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.45.jar")
GEN = os.path.join(HERE, "build_skyymenu_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.45.py")
PATCH = os.path.join(ROOT, "tools", "menu_0_3_46_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menu046", "menu")))
PKG = "com.skyy.menu."
ADDED = []
EXPECT = {
    "Given": ["+f OFF", "+f REMOVED", "+m isRemoved", "+m markRemoved", "+m removedLater", "~<clinit>", "~m planFiles", "~m planHeld"],
    "GivenSave": ["+f off", "+f n", "+c ", "~c ", "~m run"],
    "GrantTask": ["+m removeNow", "~m grantNow", "~m step"],
    "MenuUtil": ["+m removeIn", "+m removeAll"],
    "MenuCfg": ["+m migrateGive", "~<clinit>", "~m load", "~m init"],          # init: the inlined default file text (giveItem=false)
    "MenuCmd": ["~c ", "~m execute"],
    "MenuData": ["~<clinit>"], "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "OpsPage": ["~<clinit>"],
    "SkyyMenuPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
if HK.arg("--phase") == "compare":          # the 0.3.27 pattern: server.lang changes too (the Skyy_Menu tooltip; its one line is checked in S)
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            got = sorted(got)
            return self.check(got == ["Server/Languages/en-US/server.lang", "manifest.json"], "C: non-class entries changed = manifest + server.lang: %s" % got)
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq
ITEM_JSON = "Server/Item/Items/Utility/Skyy_Menu.json"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.3.46"') == 1, "S VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.check(zn.read(ITEM_JSON) == zo.read(ITEM_JSON), "S the Skyy_Menu item JSON is byte-identical to 0.3.45's (id defined, right-click opens the Menu)")
    K.check(b"OpenCustomUI" in zn.read(ITEM_JSON) or b"SkyyMenu" in zn.read(ITEM_JSON), "S ... and it still opens the page")
    lang = zn.read("Server/Languages/en-US/server.lang").decode("utf8")
    lo = zo.read("Server/Languages/en-US/server.lang").decode("utf8")
    dl = [(a, b) for a, b in zip(lo.splitlines(), lang.splitlines()) if a != b]
    K.check(len(lo.splitlines()) == len(lang.splitlines()) and sorted(a.split("=")[0] for a, b in dl) == ["items.Skyy_Menu.description", "server.items.Skyy_Menu.description"],
            "S server.lang: only the Skyy_Menu description lines differ (both key forms): %s" % [a.split("=")[0] for a, b in dl])
    K.check("Left Alt (your Walk key) or /skymenu opens the menu too" in lang and "Lost it anyway" not in lang, "S the item tooltip: Left Alt / /skymenu")
    K.check("Lost your menu item" not in g and "Press Left Alt (your Walk key) or type /skymenu to open this menu." in g, "S the main view intro")
    K.check('"/skymenu%ALIASES% - open the menu",' in g and "or get the item back" not in g, "S the Mods line no longer offers the item")
    K.check('"giveItem=false",' in g and '"giveItem=true",' not in g, "S the default config file says giveItem=false")
    K.save()


def run_off(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_o")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_o", "Skyy_SkyyMenu")
    for sub in ("layouts", "settings"):
        os.makedirs(os.path.join(home, sub), exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    SS = JV("SetStore")
    SS.DIR = Paths.get(os.path.join(home, "settings"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    JV("SetReg").registerOwn()
    GV, GT, MC, MU, MD = JV("Given"), JV("GrantTask"), JV("MenuCfg"), JV("MenuUtil"), JV("MenuData")
    GV.DIR = Paths.get(os.path.join(home, "given-profile"))
    GV.LEGACY = Paths.get(os.path.join(home, "given"))
    offd = os.path.join(home, "menuitem-off")
    GV.OFF = Paths.get(offd)
    JV("MenuIO").begin()
    MH = JV("MenuHub")
    BR = MU.bridge()
    E.br = BR
    MH.register()
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    JShort = jpype.JShort
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = E.jf(UniC.class_, "playersByUuid").get(UniC.get())
    uid = lambda n: E.UUID.fromString("00000000-0000-0000-0000-%012x" % (0x3460 + n))

    def mk(n, name):
        P = E.player(uid(n), name=name)
        byU.put(P.pr.getUuid(), P.pr)
        E.UniH.PL.add(P.pr)
        E.PLAYERS.add(P.pr)
        return P

    def ids(P):
        acc = []
        for k_, c_ in sorted(P.slots.items()):
            ic = c_.getInventory()
            for i in range(int(ic.getCapacity())):
                s_ = ic.getItemStack(JShort(i))
                if s_ is not None and not s_.isEmpty():
                    acc.append((k_, i, str(s_.getItemId()), int(s_.getQuantity())))
        return acc

    def wait_file(f, t=3.0):
        t0 = time.time()
        while time.time() - t0 < t and not os.path.exists(f):
            time.sleep(0.05)
        return os.path.exists(f)

    def join(P):
        """the grant path of one join: the IO step (GrantTask.run on this thread = SkyyMenu-IO's job), then the world thread's queue"""
        E.W1.tasks = None
        n0 = len(E.sent(P))
        GT(P.pr).run()
        hop = E.queued(E.W1)
        E.run_world(E.W1)
        return hop, E.strs_of(P, n0)

    # ------------------------------------------------------------------ NOGIVE
    K.check(not bool(MC.GIVE_ITEM), "NOGIVE: MenuCfg.GIVE_ITEM is OFF by default")
    JV("CfgPub").publish()
    rows_ = dict((str(rw[0]), [str(x) for x in rw]) for rw in BR.get("config:def:SkyyMenu")[7])
    K.eq(rows_["menu.giveItem"][3:5], ["bool", "false"], "NOGIVE: the Server Setup row menu.giveItem kept, default OFF")
    K.check("old copies taken once" in rows_["menu.giveItem"][10], "NOGIVE: its help names the one-time removal: %s" % rows_["menu.giveItem"][10])
    K.eq(rows_["menu.itemKeep"][3:5], ["bool", "true"], "NOGIVE: menu.itemKeep (lifelong rules) unchanged")
    P1 = mk(1, "SkyyNewbie")
    hop, txt = join(P1)
    K.eq(E.count(P1, "Skyy_Menu"), 0, "NOGIVE: a join with no item - nothing given")
    K.eq(hop, ["GrantTask"], "NOGIVE: (the IO step found no marker and hopped to the world thread once)")
    K.check(not os.path.isdir(os.path.join(home, "given-profile")) or not os.listdir(os.path.join(home, "given-profile")), "NOGIVE: no given-profile record")
    K.check("SkyWynn Menu" not in txt, "NOGIVE: no chat line for a player who had nothing: %r" % txt[:120])
    m1 = os.path.join(offd, str(P1.pr.getUuid()) + ".done")
    K.check(wait_file(m1) and open(m1).read().startswith("old SkyWynn Menu items taken: 0 "), "NOGIVE: the player's run-once marker (0 taken) on SkyyMenu-IO")
    K.check(not bool(GV.wants(P1.pr.getUuid())), "NOGIVE: the session mark set (no further grant this session)")

    # ------------------------------------------------------------------ ONCE
    P2 = mk(2, "SkyyVeteran")
    hb, sto = P2.slots["hotbar"].getInventory(), P2.slots["storage"].getInventory()
    hb.addItemStackToSlot(JShort(8), IS("Skyy_Menu", 1))
    hb.addItemStackToSlot(JShort(0), IS("Skyy_Menu_Icon_Back", 1))
    sto.addItemStackToSlot(JShort(3), IS("Skyy_Menu", 2))
    sto.addItemStackToSlot(JShort(4), IS("Food_Bread", 5))
    before = ids(P2)
    K.eq(E.count(P2, "Skyy_Menu"), 3, "ONCE: (3 old menu items: hotbar slot 9 + a stack of 2 in storage)")
    busy = "profile:busy:" + str(P2.pr.getUuid())
    BR.put(busy, True)
    K.eq(int(GV.planHeld(P2.pr.getUuid(), str(P2.pr.getUuid()), 3)), 2, "ONCE: profile:busy - planHeld waits (2), the inventory is not trusted")
    BR.remove(busy)
    hop, txt = join(P2)
    K.eq(hop, ["GrantTask"], "ONCE: the IO step hops to the world thread")
    K.eq(E.count(P2, "Skyy_Menu"), 0, "ONCE: every Skyy_Menu taken")
    K.eq(ids(P2), [x for x in before if x[2] != "Skyy_Menu"], "ONCE: every other stack kept (Skyy_Menu_Icon_Back, bread)")
    K.check("You don't need the SkyWynn Menu item any more" in txt and "Left Alt" in txt, "ONCE: one chat line tells the player: %r" % txt[:160])
    m2 = os.path.join(offd, str(P2.pr.getUuid()) + ".done")
    K.check(wait_file(m2) and open(m2).read().startswith("old SkyWynn Menu items taken: 3 "), "ONCE: the marker says 3")
    # the second join: disconnect clears the session mark; a copy the player got since stays
    GV.forget(P2.pr.getUuid())
    K.check(bool(GV.wants(P2.pr.getUuid())), "ONCE: (after a disconnect the session mark is gone)")
    hb.addItemStackToSlot(JShort(8), IS("Skyy_Menu", 1))
    hop, txt = join(P2)
    K.eq((hop, E.count(P2, "Skyy_Menu")), ([], 1), "ONCE: a SECOND join takes nothing (no world hop) - removed once")
    # a restart: memory gone, the marker file still stops it
    GV.forget(P2.pr.getUuid())
    GV.REMOVED.clear()
    hop, txt = join(P2)
    K.eq((hop, E.count(P2, "Skyy_Menu")), ([], 1), "ONCE: after a restart (memory cleared) the marker file stops it")
    K.eq(open(m2).read().split(" at ")[0], "old SkyWynn Menu items taken: 3", "ONCE: the marker is never rewritten")
    # a removal that leaves a copy = no marker (tried again next login)

    # ------------------------------------------------------------------ ON (= 0.3.45)
    MC.GIVE_ITEM = True
    P3 = mk(3, "SkyyGiven")
    hop, txt = join(P3)
    K.eq(E.count(P3, "Skyy_Menu"), 1, "ON: giveItem ON - a fresh join gets ONE item (0.3.45)")
    K.check(not os.path.exists(os.path.join(offd, str(P3.pr.getUuid()) + ".done")), "ON: no removal marker")
    P4 = mk(4, "SkyyHolder")
    P4.slots["hotbar"].getInventory().addItemStackToSlot(JShort(8), IS("Skyy_Menu", 1))
    join(P4)
    K.eq(E.count(P4, "Skyy_Menu"), 1, "ON: a held item is kept, no second one")
    MC.GIVE_ITEM = False

    # ------------------------------------------------------------------ CMD (/skymenu)
    CmdC = JV("MenuCmd")
    cmd_ = CmdC()
    ex = [m for m in CmdC.class_.getDeclaredMethods() if str(m.getName()) == "execute"][0]
    ex.setAccessible(True)
    P5 = mk(5, "SkyyLost")
    ex.invoke(cmd_, None, P5.st, P5.ref, P5.pr, E.W1)
    cp = P5.pm.getCustomPage()
    K.check(cp is not None and str(cp.getClass().getName()) == PKG + "MenuPage", "CMD: /skymenu opens the Menu")
    K.eq(E.count(P5, "Skyy_Menu"), 0, "CMD: /skymenu with giveItem OFF gives nothing")
    E.pump(P5)
    P5.pm.handleLegacyCustomPageEvent(P5.ref, P5.st, E.CPE(E.CPT.Dismiss, None))
    MC.GIVE_ITEM = True
    ex.invoke(cmd_, None, P5.st, P5.ref, P5.pr, E.W1)
    K.eq(E.count(P5, "Skyy_Menu"), 1, "CMD: giveItem ON - /skymenu gives a lost one back (0.3.45)")
    E.pump(P5)
    P5.pm.handleLegacyCustomPageEvent(P5.ref, P5.st, E.CPE(E.CPT.Dismiss, None))
    MC.GIVE_ITEM = False
    K.check("Left Alt" in str(cmd_.getDescription()) and "lost" not in str(cmd_.getDescription()), "CMD: the description: %s" % cmd_.getDescription())

    # ------------------------------------------------------------------ MIG (the one-time giveItem update)
    CL = JV("CfgLog")
    old_text = str(MD.MENU_CFG_TEXT).replace("giveItem=false", "giveItem=true")
    K.check(old_text.count("giveItem=true") == 1, "MIG: (the old default file stands in)")

    def mig(case, data):
        d = os.path.join(scratch, "mig", case, "Skyy_SkyyMenu")
        os.makedirs(d, exist_ok=True)
        f = os.path.join(d, "config.properties")
        if data is not None:
            open(f, "wb").write(data)
        MC.FILE = Paths.get(f)
        q0 = int(CL.Q.size())
        r = str(MC.migrateGive())
        logs = [str(CL.Q.get(i)) for i in range(q0, int(CL.Q.size()))]
        return d, f, r, logs
    old_b = old_text.replace("\n", "\r\n").encode("ISO-8859-1")
    d, f, r, logs = mig("old", old_b)
    new_b = open(f, "rb").read()
    K.eq(new_b, old_b.replace(b"\r\ngiveItem=true\r\n", b"\r\ngiveItem=false\r\n"), "MIG: only the old default line changed (CRLF + every other byte kept)")
    hd = os.path.join(d, "config-history")
    baks = [x for x in os.listdir(hd) if x.endswith(".bak")] if os.path.isdir(hd) else []
    K.check(len(baks) == 1 and baks[0].startswith("Skyy_SkyyMenu~config.properties.") and open(os.path.join(hd, baks[0]), "rb").read() == old_b,
            "MIG: a VERIFIED History copy of the old bytes in config-history/: %s" % baks)
    K.check(len(logs) == 1 and logs[0].split("\t")[3:] == ["update", "menu.giveItem", "true", "false", "ok"],
            "MIG: one Changes line menu.giveItem true -> false, status ok (= the Undo button): %s" % logs)
    mkf = os.path.join(d, "menuitem-off", "config-giveitem.done")
    K.check(os.path.exists(mkf) and "-> giveItem=false" in open(mkf).read(), "MIG: the run-once marker: %s" % r)
    MC.load()
    K.check(not bool(MC.GIVE_ITEM), "MIG: MenuCfg.load reads OFF")
    open(f, "wb").write(old_b)          # an Undo (or a hand edit) back to true after the update
    r2, logs2 = mig("old", None)[2:]
    K.check(r2 == "done before" and open(f, "rb").read() == old_b and logs2 == [], "MIG: a second start changes nothing (Undo back to true is kept)")
    MC.load()
    K.check(bool(MC.GIVE_ITEM), "MIG: ... and load reads ON again")
    for case, line, want in (("false", "giveItem=false", "kept"), ("on", "giveItem=on", "kept"), ("spaced", "giveItem = true", "kept"),
                             ("two", "giveItem=true\ngiveItem=true", "2 giveItem lines"), ("none", "", "no giveItem line")):
        txt_ = "# x\nmodsHelp=true\n" + (line + "\n" if line else "") + "walkKey=true\n"
        d, f, r, logs = mig(case, txt_.encode("ISO-8859-1"))
        K.check(open(f, "rb").read() == txt_.encode("ISO-8859-1") and logs == [] and want in r and os.path.exists(os.path.join(d, "menuitem-off", "config-giveitem.done")),
                "MIG: %r -> the file kept, no Changes line, marker (%s)" % (line, r))
        K.check(not os.path.isdir(os.path.join(d, "config-history")), "MIG: %r -> no History copy needed" % line)
    d, f, r, logs = mig("fresh", None)
    K.check(not os.path.exists(f) and "no config.properties yet" in r and os.path.exists(os.path.join(d, "menuitem-off", "config-giveitem.done")),
            "MIG: no file yet - marker only (%s)" % r)
    MC.init()
    K.check(os.path.exists(f) and "\ngiveItem=false\n" in open(f).read(), "MIG: init writes the new default file with giveItem=false")
    MC.GIVE_ITEM = True
    MC.load()
    K.check(not bool(MC.GIVE_ITEM), "MIG: ... and load reads it OFF")
    MC.FILE = Paths.get(os.path.join(scratch, "mig", "missing.properties"))
    MC.GIVE_ITEM = True
    MC.load()
    K.check(not bool(MC.GIVE_ITEM), "MIG: no config file at all = OFF (load's missing-file defaults)")

    # ------------------------------------------------------------------ ALT (the Left-Alt path, untouched)
    HK_, HO = JV("MenuHotkey"), JV("HotkeyOpen")
    s_ = JArray(jpype.JLong)(6)          # 0.3.43: the long[6] state
    K.eq([bool(HK_.walkStep(s_, w_, t_)) for w_, t_ in ((False, 900), (True, 1000), (True, 1033))], [False, True, False],
         "ALT: walkStep - the Walk (Left Alt) press fires once")
    MVS = JClass("com.hypixel.hytale.protocol.MovementStates")
    msc = E.MSCc()
    ms_ = MVS()
    ms_.onGround = True
    msc.setMovementStates(ms_)
    P2.st.row(P2.ref).put(E.CT_MSC, msc)
    ACH = JClass("com.hypixel.hytale.component.ArchetypeChunk")
    ch = E.U.allocateInstance(ACH.class_)
    E.jf(ACH.class_, "refs").set(ch, JArray(E.REFc)([P2.ref]))
    E.jf(ACH.class_, "entitiesSize").setInt(ch, 1)
    sysm = HK_()
    HK_.ST.clear()
    HK_.ON = True
    E.W1.tasks = None
    sysm.tick(0.033, 0, ch, P2.st, None)
    ms_.walking = True
    sysm.tick(0.033, 0, ch, P2.st, None)
    K.eq(E.queued(E.W1), ["HotkeyOpen"], "ALT: Left Alt (walking false -> true) queues ONE HotkeyOpen on the player's world")
    K.check(bool(E.W1.tasks.peek().walk), "ALT: ... the Walk variant")
    E.run_world(E.W1)
    cp = P2.pm.getCustomPage()
    K.check(cp is not None and str(cp.getClass().getName()) == PKG + "MenuPage" and str(cp.view) == "main",
            "ALT: the world task opens the SkyWynn Menu (main view) - for the player whose item was taken")
    E.pump(P2)
    MH.clearAll()
    JV("MenuIO").stop(2000)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("off", run_off), ("live", T35.run_live)], script=__file__, live=(T35.LIVE_DIR, "Skyy_SkyyMenu"))
