"""Harness for SkyyProfiles 0.1.12 (admins have no profile cap, rename a profile, "<Class> <name>" everywhere + bridge profile:name;
tools/profiles_0_1_12_patch.py). Build first: python tools/profiles_0_1_12_patch.py && python SkyyProfiles/build_skyyprofiles_0.1.12.py

    python SkyyProfiles/test_skyyprofiles_0.1.12.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.11 -> 0.1.12: exactly the listed members differ; ProfRenameCmd is the one class added
  X  exec     EXECUTED on the compiled classes (0.1.11 side by side as the control), the engine's REAL PermissionsModule.hasPermission
              code with a stand-in permission provider (op = hytale:Admin with "*", a player with the skyyprofiles.admin node, a plain
              Adventurer, an unknown uuid, a provider that throws, no module at all):
              ADMIN  isAdmin / capFor (256 for admins, the normal limit + bonus for players), capWhy, describe; the page's Create new
                     (pfnew) at 8 profiles: refused for a player, the create view for an admin; createAndSwitch passes the limit for an
                     admin (0.1.11: refused); a player restore over the limit refused, an admin's restored; buildList / buildCreate texts
              NAMES  ProfNames.clean / check / staffLike on a table of names (length, characters, letters, duplicates any case, itself,
                     deleted profiles, staff words for a player vs an admin); every fruit name passes
              RENAME renameProfile: the file holds only the new p.<id>.name (every other key byte-equal), the key / epoch / active never
                     change, publish puts profile:name = "<Class> <name>" + profile:pname; refused: duplicate, deleted, bad name, unknown
                     id, unreadable file; "=" for the same name; a RENAME line in switches.log; 2 x 8 threads racing to give two
                     profiles the same name - exactly one wins per race, no file ever holds a duplicate
              DISPLAY dispName (class, no class, the old Shaman = Monk), resolveId by the display text, describe / listText, the bridge keys
              PAGE   ProfilePage events on a page stand-in: pfren<id> opens the row with the current name, pfrnok + @PfName renames (also
                     Enter = the same payload), a refused name keeps the row + the typed text, pfrnno closes it, any other click closes it,
                     a TYPED "pfclose" / "pfdelyes" / "pfsw2" is a name and never another button; buildList with the row open (ids, the
                     16-letter field, the bindings), the active card's Rename button + its binding, the switch / delete questions
  D  live     start twice on a scratch COPY of the live Skyy_SkyyProfiles with 0.1.11 and 0.1.12 (setup()'s data steps): no file changed
              by either start, the same storage keys; the published keys = 0.1.11's + profile:pname:<uuid>, profile:name = "<Class> <name>"
  AA engine-access audit
Scratch: tools/dev/scratch/prof012/profiles (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, shutil, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.12"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyProfiles-0.1.11.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "prof012", "profiles")))
PKG = "com.skyy.profiles."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyProfiles")
EXPECT = {
    "ProfCfg": ["+f ADMIN_NODE", "+f ADMIN_LIMIT", "+m isAdmin", "~m capFor", "~m capWhy", "~m capMigrate"],   # capMigrate: version text
    "ProfNames": ["+f NAME_MIN", "+f NAME_MAX", "+f STAFF_WORDS", "+f STAFF_LEAD", "+f STAFF_PREFIX", "+m clean", "+m staffLike", "+m check", "~<clinit>"],
    "ProfStore": ["+m dispName", "+m rename0", "+m rename", "+m renameProfile", "~m resolveId", "~m describe"],
    "ProfPub": ["~m publishLocked"],
    "ProfSwitch": ["~m createFirst", "~m switchLocked"],
    "ReadyTask": ["~m run"],
    "ProfilePage": ["+f renId", "+f renText", "+m jsonStr", "+m renameEvent", "~m shownIds", "~m buildList", "~m buildCreate", "~m handleDataEvent", "~c "],
    "ProfilesCmd": ["~c "],
    "ProfDel": ["~m archiveLocked"],                                               # archive.version = the version text
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],                            # the config kit's version text
    "SkyyProfilesPlugin": ["~m setup"],                                            # the ready line's version + the setting's example
}
ADDED = ["ProfRenameCmd"]
FRUITS = ["Apple", "Banana", "Blueberry", "Coconut", "Cucumber", "Grapes", "Kiwi", "Lemon", "Lime", "Mango", "Orange",
          "Papaya", "Pear", "Pineapple", "Pomegranate", "Raspberry", "Strawberry", "Tomato", "Watermelon", "Zucchini"]


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)([JClass("java.io.File")(jar).toURI().toURL()])
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


class Jar(object):
    """one jar in its own loader with its own players folder"""

    def __init__(self, jar, home):
        from jpype import JClass
        self.L = loader_for(jar)
        self.c = lambda n: JClass(PKG + n, loader=self.L)
        self.Store, self.Cfg, self.Del, self.Names, self.Sw = (self.c("ProfStore"), self.c("ProfCfg"), self.c("ProfDel"), self.c("ProfNames"),
                                                                self.c("ProfSwitch"))
        P = JClass("java.nio.file.Paths")
        os.makedirs(os.path.join(home, "players"), exist_ok=True)
        self.home = home
        self.Store.DIR = P.get(os.path.join(home, "players"))
        self.Store.SWDIR = P.get(os.path.join(home, "switching"))
        self.Store.INVDIR = P.get(os.path.join(home, "inventories"))
        self.Store.LOGF = P.get(os.path.join(home, "switches.log"))
        self.Del.ARCDIR = P.get(os.path.join(home, "archive"))

    def file(self, u):
        return os.path.join(self.home, "players", str(u) + ".properties")


def props(path):
    from jpype import JClass
    p = JClass("java.util.Properties")()
    if os.path.isfile(path):
        s_ = JClass("java.io.FileInputStream")(path)
        try:
            p.load(s_)
        finally:
            s_.close()
    return dict((str(k), str(p.getProperty(k))) for k in p.stringPropertyNames())


def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    UUID, HashSet, HashMap, ArrayList = JClass("java.util.UUID"), JClass("java.util.HashSet"), JClass("java.util.HashMap"), JClass("java.util.ArrayList")
    System = JClass("java.lang.System")
    bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", bridge)
    new = Jar(jar, os.path.join(scratch, "x_new"))
    old = Jar(OLD_JAR, os.path.join(scratch, "x_old"))
    S, Cfg, N = new.Store, new.Cfg, new.Names
    for J in (new, old):
        try:
            J.Cfg.BRIDGE = None
        except Exception:
            pass

    # ------------------------------------------------------------------ the engine's PermissionsModule with a stand-in provider
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    PM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")

    def pm_field(n):
        f = PM.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f
    U_OP, U_NODE, U_PLAIN, U_GHOST = (UUID(0x0A00000000000000, 1), UUID(0x0A00000000000000, 2), UUID(0x0A00000000000000, 3),
                                      UUID(0x0A00000000000000, 4))
    STATE = {"boom": False}

    def jset(*xs):
        h = HashSet()
        for x in xs:
            h.add(JString(x))
        return h

    @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
    class Prov(object):
        @JOverride
        def getName(self): return "skyy-test"

        @JOverride
        def getUserPermissions(self, u):
            if STATE["boom"]:
                raise RuntimeError("provider down")
            return jset("skyyprofiles.admin") if str(u) == str(U_NODE) else jset()

        @JOverride
        def getGroupsForUser(self, u):
            if str(u) == str(U_OP):
                return jset("hytale:Admin")
            return jset("hytale:Adventurer") if str(u) in (str(U_NODE), str(U_PLAIN)) else jset()

        @JOverride
        def getGroupPermissions(self, g): return jset("*") if str(g) == "hytale:Admin" else jset()

        @JOverride
        def getGroupParent(self, g): return None

        @JOverride
        def getEffectiveGroupPermissions(self, g): return self.getGroupPermissions(g)

        @JOverride
        def getAllRegisteredGroups(self): return jset("hytale:Admin", "hytale:Adventurer")

        @JOverride
        def getUsersWithPermission(self, p): return jset()

        @JOverride
        def addUserPermissions(self, *a): return None

        @JOverride
        def removeUserPermissions(self, *a): return None

        @JOverride
        def removeGroupPermissions(self, *a): return None

        @JOverride
        def addGroupPermissions(self, *a): return None

        @JOverride
        def addUserToGroup(self, *a): return None

        @JOverride
        def removeUserFromGroup(self, *a): return None

        @JOverride
        def setUserGroup(self, *a): return None
    pm = us.allocateInstance(PM.class_)
    lst = ArrayList()
    lst.add(Prov())
    pm_field("providers").set(pm, lst)
    pm_field("virtualGroups").set(pm, HashMap())
    inst = pm_field("instance")
    inst.set(None, None)
    K.check(not Cfg.isAdmin(U_OP), "ADMIN: no PermissionsModule at all -> not an admin (no exception)")
    inst.set(None, pm)
    K.check(PM.get() is not None, "ADMIN: the stand-in module is PermissionsModule.get()")

    # PlayerRef stand-ins (the uuid fields set) for the page and the switch path
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Mod = JClass("java.lang.reflect.Modifier")
    uuid_fs = [f_ for f_ in PRc.class_.getDeclaredFields() if f_.getType() == UUID.class_ and not Mod.isStatic(f_.getModifiers())]
    for f_ in uuid_fs:
        f_.setAccessible(True)

    def pref(u):
        r_ = us.allocateInstance(PRc.class_)
        for f_ in uuid_fs:
            f_.set(r_, u)
        return r_
    K.check(bool(pref(U_OP).hasPermission("skyyprofiles.admin")) and not pref(U_PLAIN).hasPermission("skyyprofiles.admin"),
            "ADMIN: control - PlayerRef.hasPermission through the same module (op yes, plain no)")

    # ------------------------------------------------------------------ ADMIN
    K.eq([bool(Cfg.isAdmin(x)) for x in (U_OP, U_NODE, U_PLAIN, U_GHOST, None)], [True, True, False, False, False],
         "ADMIN: isAdmin op (hytale:Admin *) / skyyprofiles.admin node / plain / unknown / null")
    STATE["boom"] = True
    K.check(not Cfg.isAdmin(U_NODE), "ADMIN: a provider that throws -> not an admin (no exception)")
    STATE["boom"] = False
    K.eq((int(Cfg.capFor(U_OP)), int(Cfg.capFor(U_NODE)), int(Cfg.capFor(U_PLAIN))), (256, 256, 8), "ADMIN: capFor admin 256 (every id), player 8 (auto)")
    K.eq(int(Cfg.ADMIN_LIMIT), 256, "ADMIN: ADMIN_LIMIT = MAX_ID")
    K.eq(int(old.Cfg.capFor(U_OP)), 8, "ADMIN CONTROL: 0.1.11 gives the op 8")
    K.eq(str(Cfg.capWhy(U_OP)), "admins have no profile limit", "ADMIN: capWhy for an admin")
    K.eq(str(Cfg.capWhy(U_PLAIN)), "one per class", "ADMIN: capWhy for a player")
    Cfg.MAX_SETTING = "3"
    K.eq((int(Cfg.capFor(U_OP)), int(Cfg.capFor(U_PLAIN))), (256, 3), "ADMIN: maxProfiles=3 - the admin still 256, the player 3")
    Cfg.MAX_SETTING = "auto"
    for u_ in (U_OP, U_PLAIN):
        for i in range(1, 9):
            S.create(u_, str(i), FRUITS[i], ["Archer", "Mage", "Priest", "Monk"][i % 4], i == 1)
    d_op, d_pl = str(S.describe(U_OP)), str(S.describe(U_PLAIN))
    K.check(d_op.endswith("| 8 profiles (admin - no profile limit)") and "1 Mage Banana - ACTIVE" in d_op, "ADMIN: describe for an admin: %s" % d_op[-80:])
    K.check(d_pl.endswith("| slots 8/8"), "ADMIN: describe for a player: %s" % d_pl[-40:])
    # the page's Create new at 8 profiles
    PP = new.c("ProfilePage")

    def page_for(u, view=0):
        pg = us.allocateInstance(PP.class_)
        c_ = PP.class_
        while c_ is not None:
            try:
                f_ = c_.getDeclaredField("playerRef")
                f_.setAccessible(True)
                f_.set(pg, pref(u))
                break
            except Exception:
                c_ = c_.getSuperclass()
        pg.view, pg.first, pg.info, pg.pickName, pg.renText = view, False, "", "", ""
        return pg
    pgp, pgo = page_for(U_PLAIN), page_for(U_OP)
    pgp.handleDataEvent(None, None, '{"a":"pfnew"}')
    pgo.handleDataEvent(None, None, '{"a":"pfnew"}')
    K.check(str(pgp.info) == "All 8 profile slots are used." and int(pgp.view) == 0, "ADMIN: page Create new at 8 - a player is refused (%s)" % pgp.info)
    K.check(int(pgo.view) == 1 and str(pgo.info) == "", "ADMIN: page Create new at 8 - an admin gets the Create Profile view (info %r)" % str(pgo.info))
    # createAndSwitch: the limit check (the world parts after it cannot run here: an exception or another answer = the limit passed)

    def cas(J, u):
        try:
            return str(J.Sw.createAndSwitch(None, None, pref(u), None, "Mage", "Zucchini"))
        except Exception as e:
            return "EXC " + str(e)[:80]
    r_pl, r_op, r_old = cas(new, U_PLAIN), cas(new, U_OP), None
    for i in range(1, 9):
        old.Store.create(U_OP, str(i), FRUITS[i], "Mage", i == 1)
    r_old = cas(old, U_OP)
    K.eq(r_pl, "All 8 profile slots are used.", "ADMIN: createAndSwitch - a player at 8 is refused")
    K.eq(int(S.count(S.load(U_PLAIN))), 8, "ADMIN: ... and nothing was created for the player")
    # the admin's create runs for real (profile 9 = Mage Zucchini); only the switch afterwards cannot run without a world
    K.check(r_op.startswith("Profile Zucchini was created but the switch did not happen"), "ADMIN: createAndSwitch - an admin at 8 creates a 9th (%s)" % r_op)
    K.eq((int(S.count(S.load(U_OP))), str(S.dispName(S.load(U_OP), "9"))), (9, "Mage Zucchini"), "ADMIN: the admin has 9 live profiles")
    K.eq(r_old, "All 8 profile slots are used.", "ADMIN CONTROL: 0.1.11 refuses the op at 8")
    K.eq(int(old.Store.count(old.Store.load(U_OP))), 8, "ADMIN CONTROL: 0.1.11 created nothing")
    # admin creates past the limit (the store path the create uses) + restore over the limit
    for i in range(10, 12):
        K.check(bool(S.create(U_OP, str(i), "Extra%s" % chr(64 + i), "Mage", False)), "ADMIN: profile %d created" % i)
    K.eq(int(S.count(S.load(U_OP))), 11, "ADMIN: 11 live profiles")
    for u_ in (U_OP, U_PLAIN):
        S.markDeleted(u_, "3", int(System.currentTimeMillis()), int(System.currentTimeMillis()) + 3600000)
        S.create(u_, "12", "Fill", "Mage", False)
    rp, ro = new.Del.restore(U_PLAIN, "pl", "3"), new.Del.restore(U_OP, "op", "3")
    K.check(rp is not None and str(rp).startswith("No free slot"), "ADMIN: a player's restore over the limit is refused (%s)" % rp)
    K.check(ro is None and S.live(S.load(U_OP), "3"), "ADMIN: an admin's restore over any limit works (%s)" % ro)
    # page texts (buildList / buildCreate on the real builders)
    UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def ucb_text(b_):
        out_ = []
        for c_ in b_.getCommands():
            k_ = c_.getClass()
            while k_ is not None:
                for f_ in k_.getDeclaredFields():
                    if Mod.isStatic(f_.getModifiers()):
                        continue
                    f_.setAccessible(True)
                    v_ = f_.get(c_)
                    if v_ is not None:
                        out_.append(str(v_))
                k_ = k_.getSuperclass()
        return "\n".join(out_)

    def ev_text(e_):
        out_ = []
        for c_ in e_.getEvents():
            k_ = c_.getClass()
            while k_ is not None:
                for f_ in k_.getDeclaredFields():
                    if Mod.isStatic(f_.getModifiers()):
                        continue
                    f_.setAccessible(True)
                    v_ = f_.get(c_)
                    if v_ is not None:
                        out_.append(str(v_))
                k_ = k_.getSuperclass()
        return "\n".join(out_)

    def build(pg, u, create=False):
        b_, e_ = UCB(), UEB()
        if create:
            pg.buildCreate(b_, e_, u, S.load(u))
        else:
            pg.buildList(b_, e_, u, S.load(u))
        return ucb_text(b_), ev_text(e_)
    t_op, _e = build(page_for(U_OP), U_OP)
    t_pl, e_pl = build(page_for(U_PLAIN), U_PLAIN)
    K.check("12 profiles - admins have no profile limit." in t_op, "ADMIN: list footer for an admin")
    K.check("8 of 8 profile slots used (one per class)." in t_pl, "ADMIN: list footer for a player")
    pgc = page_for(U_OP, 1)
    pgc.pickName = "Kiwi"
    t_c, _e = build(pgc, U_OP, create=True)
    K.check("This is profile 13 - admins have no profile limit." in t_c, "ADMIN: Create Profile line for an admin")
    pgc2 = page_for(U_PLAIN, 1)
    pgc2.pickName = "Kiwi"
    t_c2, _e = build(pgc2, U_PLAIN, create=True)
    K.check("All 8 profile slots are used" in t_c2, "ADMIN: Create Profile line for a player at the limit")
    K.check("(admins have no limit)" in t_op and "free)" not in t_op, "ADMIN: the empty-slot card for an admin")
    K.check("Create new" not in t_pl, "ADMIN: no empty-slot card for a player at the limit")
    K.notes.append("ADMIN: op / node admins 256, player 8; page + switch + restore paths executed")
    # fix round (critic: "no cap" stopped at 16 on the page): an admin with 20 live profiles, active = 18 -> the page still has Create new
    # (a 17th card) and draws the active card (its Rename); ids 1-15 + 18 drawn, 16 / 17 / 19 / 20 named in the footer
    for i in range(13, 21):
        K.check(bool(S.create(U_OP, str(i), "Extra%s" % chr(64 + i), "Mage", False)), "ADMIN 16+: profile %d created" % i)
    q_ = S.load(U_OP).clone()
    q_.setProperty("active", "18")
    K.check(bool(S.commit(U_OP, q_)) and str(S.activeOf(S.load(U_OP))) == "18", "ADMIN 16+: profile 18 active")
    K.eq([str(x) for x in PP.shownIds(S.load(U_OP))], [str(i) for i in range(1, 16)] + ["18"], "ADMIN 16+: shownIds keeps the active profile")
    t_o2, e_o2 = build(page_for(U_OP), U_OP)
    K.check("#SkyyPfNew" in t_o2 and "pfnew" in e_o2, "ADMIN 16+: the Create new card stays for an admin at 20 profiles")
    K.check("#SkyyPfRen18" in t_o2 and "pfren18" in e_o2 and "SkyyPfCard16" not in t_o2 and "SkyyPfCard15" in t_o2,
            "ADMIN 16+: the active card 18 (Rename) is drawn in the 16th place")
    K.check("4 more profiles - /profiles list shows them." in t_o2, "ADMIN 16+: the footer names the 4 not drawn")
    pgo2 = page_for(U_OP)
    pgo2.handleDataEvent(None, None, '{"a":"pfnew"}')
    K.check(int(pgo2.view) == 1, "ADMIN 16+: Create new at 20 opens the Create Profile view")
    K.eq([str(x) for x in old.c("ProfilePage").shownIds(S.load(U_OP))], [str(i) for i in range(1, 17)], "ADMIN 16+ CONTROL: 0.1.11 drops the active 18")
    q_ = S.load(U_OP).clone()
    q_.setProperty("active", "1")
    S.commit(U_OP, q_)
    # a player is still capped at 16 cards with no Create card (unchanged)
    t_pl3, _e = build(page_for(U_PLAIN), U_PLAIN)
    K.check("#SkyyPfNew" not in t_pl3, "ADMIN 16+: a player at the limit still has no Create new")

    # ------------------------------------------------------------------ NAMES
    P0 = JClass("java.util.Properties")()
    P0.setProperty("p.1.name", "Banana")
    P0.setProperty("p.1.class", "Mage")
    P0.setProperty("p.2.name", "Kiwi")
    P0.setProperty("p.2.class", "Priest")
    P0.setProperty("p.2.deleted", "1")
    cases = [  # (id, name, admin, ok?)
        ("1", "Banana", False, True), ("1", "banana", False, True), ("1", "Big Banana", False, True), ("1", "Kiwi", False, False),
        ("1", "KIWI", False, False), ("2", "Banana", False, False), ("1", "A", False, False), ("1", "AB", False, True),
        ("1", "Sixteen Letters!", False, False), ("1", "SixteenLettersXY", False, True), ("1", "SeventeenLettersX", False, False),
        ("1", "12345", False, False), ("1", "Team 7", False, True), ("1", "Neo-Tokyo", False, True), ("1", "Bad_Name", False, False),
        ("1", "Na:me", False, False), ("1", "Na,me", False, False), ("1", "Ünï", False, False), ("1", "Admin", False, False),
        ("1", "Admin", True, True), ("1", "The Mod", False, False), ("1", "Modern", False, True), ("1", "xXAdminXx", False, True),
        ("1", "Server", False, False), ("1", "Owner-Bob", False, False), ("1", "Staffy", False, True), ("1", "Op", False, False),
        ("1", "Opal", False, True), ("1", "Dev", False, False), ("1", "Devon", False, True), ("1", "Official", False, False),
        # fix round: the staff filter no longer over-blocks ordinary words; it still blocks titles
        ("1", "Fire Staff", False, True), ("1", "Badminton", False, True), ("1", "Stafford", False, True), ("1", "Downer", False, True),
        ("1", "Staff Bob", False, False), ("1", "Server Bot", False, False), ("1", "Admin123", False, False), ("1", "A-d-m-i-n", False, False),
        ("1", "Ad Min", False, False), ("1", "Big Owner", False, False), ("1", "Mod Squad", False, False), ("1", "Moderators", False, False),
        ("1", "Server Bot", True, True), ("1", "Pod Racer", False, True), ("1", "Systems Go", False, True),
        # fix round: never two profiles that READ the same ("<Class> <name>"): 1 = Mage Banana, 2 = Priest Kiwi (deleted), 3 = Mage "Priest Lime"
        ("1", "Priest Kiwi", False, False), ("3", "Banana", False, False), ("1", "Lime", False, True), ("2", "Lime", False, False),
        ("4", "Mage Banana", False, False), ("1", "Mage Banana", False, True), ("1", "Kiwi Priest", False, True)]
    P0.setProperty("p.3.name", "Priest Lime")
    P0.setProperty("p.3.class", "Mage")
    P0.setProperty("p.4.name", "Plum")
    P0.setProperty("p.4.class", "")
    bad_ = []
    for id_, nm, adm, ok in cases:
        r_ = N.check(P0, id_, nm, adm)
        if (r_ is None) != ok:
            bad_.append((id_, nm, adm, None if r_ is None else str(r_)))
    K.eq(bad_, [], "NAMES: the rule table (%d cases)" % len(cases))
    K.eq([str(N.clean(x)) for x in ("  Big   Red  Apple ", "\tKiwi\n", "", None)], ["Big Red Apple", "Kiwi", "", ""], "NAMES: clean")
    K.eq([f for f in FRUITS if N.check(JClass("java.util.Properties")(), "1", f, False) is not None], [], "NAMES: every fruit name passes")
    K.eq(list(str(x) for x in N.FRUITS), FRUITS, "NAMES: the fruit table")

    # ------------------------------------------------------------------ RENAME
    UR = UUID(0x0C00000000000000, 7)
    S.create(UR, "1", "Banana", "Priest", True)
    S.create(UR, "2", "Kiwi", "Mage", False)
    S.create(UR, "3", "Lime", "", False)
    S.publish(UR)
    f0 = props(new.file(UR))
    key0, ep0 = str(S.keyOf(UR)), int(S.num(S.load(UR), "epoch"))
    r_ = str(S.renameProfile(UR, "Tester", "1", "  Sunny   Day ", False))
    f1 = props(new.file(UR))
    K.eq(r_, "+Banana is now called Priest Sunny Day.", "RENAME: answer")
    K.eq(dict((k, v) for k, v in f1.items() if k != "p.1.name"), dict((k, v) for k, v in f0.items() if k != "p.1.name"),
         "RENAME: every other key of the players file is unchanged (epoch, active, created, lastPlayed ...)")
    K.eq(f1.get("p.1.name"), "Sunny Day", "RENAME: p.1.name in the file")
    K.eq((str(S.keyOf(UR)), int(S.num(S.load(UR), "epoch"))), (key0, ep0), "RENAME: storage key + epoch unchanged")
    K.eq((str(bridge.get("profile:name:" + str(UR))), str(bridge.get("profile:pname:" + str(UR))), str(bridge.get("profile:list:" + str(UR)))),
         ("Priest Sunny Day", "Sunny Day", "1:Sunny Day:Priest,2:Kiwi:Mage,3:Lime:"), "RENAME: published name / pname / list")
    K.eq(int(bridge.get("profile:epoch:" + str(UR))), ep0, "RENAME: the published epoch did not move")
    rr = [str(S.renameProfile(UR, "T", "2", x, False)) for x in ("sunny day", "Bad_Name", "Admin")]
    K.check(rr[0].startswith("-You already have a profile called Sunny Day") and rr[1].startswith("-Use only") and rr[2].startswith("-That name looks like a staff"),
            "RENAME: refused duplicate (any case) / bad characters / staff word: %s" % rr)
    K.eq(str(S.renameProfile(UR, "T", "2", "Admin", True)), "+Kiwi is now called Mage Admin.", "RENAME: an admin may use a staff word")
    K.eq(str(S.renameProfile(UR, "T", "2", "Admin", True)), "=Mage Admin already has that name.", "RENAME: the same name -> '=' nothing to do")
    K.eq(str(S.renameProfile(UR, "T", "3", "Plain", False)), "+Lime is now called Plain.", "RENAME: a profile without a class")
    S.markDeleted(UR, "3", 1000, int(System.currentTimeMillis()) + 3600000)
    K.check(str(S.renameProfile(UR, "T", "3", "Ghost", False)).startswith("-Plain is deleted - restore it first"), "RENAME: a deleted profile is refused")
    K.check(str(S.renameProfile(UR, "T", "9", "Ghost", False)).startswith("-You have no such profile"), "RENAME: unknown id")
    K.check(str(S.renameProfile(UR, "T", None, "Ghost", False)).startswith("-You have no such profile"), "RENAME: null id")
    K.check(str(S.renameProfile(UR, "T", "1", "Plain", False)).startswith("-You already have a profile called Plain"), "RENAME: a DELETED profile's name stays taken")
    S.BROKEN.put(UR, True)
    K.check(str(S.renameProfile(UR, "T", "1", "Other", False)).startswith("-Your profile file could not be read"), "RENAME: unreadable file -> refused")
    S.BROKEN.remove(UR)
    K.check(S.rename(UR, "1", "Kiwi Two", False) is None, "RENAME: rename() direct")
    K.check(str(S.rename(UR, "2", "kiwi two", False)).startswith("You already have"), "RENAME: rename() re-checks inside the stripe")
    log_ = open(os.path.join(new.home, "switches.log"), encoding="utf8").read()
    K.check("RENAME %s Tester profile 1 Banana -> Sunny Day" % UR in log_, "RENAME: switches.log line")
    # the race: two profiles, 8 threads each trying to give one of them the same name at once (fresh name per round)
    UQ = UUID(0x0D00000000000000, 5)
    S.create(UQ, "1", "Apple", "Mage", True)
    S.create(UQ, "2", "Pear", "Mage", False)
    lost = []
    for rnd in range(25):
        nm = "Race %d" % rnd
        res = []
        lk = threading.Lock()

        def go(i):
            pid = "1" if i % 2 == 0 else "2"
            r2 = S.renameProfile(UQ, "racer", pid, nm, False)
            with lk:
                res.append((pid, str(r2)))
        ths = [threading.Thread(target=go, args=(i,), daemon=True) for i in range(16)]
        for t in ths:
            t.start()
        for t in ths:
            t.join(30)
        fq = props(new.file(UQ))
        wins = set(pid for pid, x in res if x.startswith("+"))
        holder = [pid for pid in ("1", "2") if fq.get("p.%s.name" % pid) == nm]
        if len(wins) != 1 or holder != sorted(wins) or S.load(UQ).getProperty("p.%s.name" % holder[0]) != nm:
            lost.append((rnd, res[:4], fq.get("p.1.name"), fq.get("p.2.name")))
    K.eq(lost, [], "RENAME: 25 races x 16 threads (8 per profile) - one profile gets the name each time (the one every '+' answer names), never both")

    # ------------------------------------------------------------------ DISPLAY
    PD = JClass("java.util.Properties")()
    PD.setProperty("p.1.name", "Mango")
    PD.setProperty("p.1.class", "Shaman")
    PD.setProperty("p.2.name", "Pear")
    PD.setProperty("p.2.class", "")
    PD.setProperty("p.3.class", "Archer")
    K.eq([str(S.dispName(PD, i)) for i in ("1", "2", "3", "4")], ["Monk Mango", "Pear", "Archer Profile 3", "Profile 4"],
         "DISPLAY: dispName (the old Shaman = Monk, no class, no name, nothing)")
    K.eq(str(S.dispName(None, "1")), "Profile 1", "DISPLAY: dispName(null)")
    K.eq(str(S.resolveId(UR, "Priest Kiwi Two")), "1", "DISPLAY: resolveId by the display text")
    K.eq(str(S.resolveId(UR, "kiwi two")), "1", "DISPLAY: resolveId by the bare name")
    K.eq(str(S.resolveId(UR, "2")), "2", "DISPLAY: resolveId by the number")
    K.check(S.resolveId(UR, "Mage Nothing") is None, "DISPLAY: resolveId unknown -> null")
    # fix round (critic: "/profiles delete Priest Banana" hit the wrong profile): a file where a Mage is NAMED "Priest Banana" next to the
    # Priest "Banana" (written directly - rename now refuses it) -> resolveId of the shared text picks nothing; the number / unique text work
    UA = UUID(0x0E00000000000000, 9)
    S.create(UA, "1", "Priest Banana", "Mage", True)
    S.create(UA, "2", "Banana", "Priest", False)
    K.check(S.resolveId(UA, "Priest Banana") is None and S.resolveId(UA, "priest banana") is None, "DISPLAY: an ambiguous name resolves to nothing")
    K.eq([str(S.resolveId(UA, x)) for x in ("Banana", "Mage Priest Banana", "1", "2")], ["2", "1", "1", "2"], "DISPLAY: unique names / numbers still resolve")
    UA2 = UUID(0x0E00000000000000, 10)
    S.create(UA2, "1", "Apple", "Mage", True)
    S.create(UA2, "2", "Banana", "Priest", False)
    r_a = [str(S.renameProfile(UA2, "T", "1", x, False)) for x in ("Priest Banana", "priest banana")]
    K.check(all(x.startswith("-That would look the same as your profile Priest Banana") for x in r_a), "RENAME: a name reading like another profile is refused: %s" % r_a)
    K.eq(str(S.renameProfile(UA2, "T", "2", "Mage Apple", False)), "-That would look the same as your profile Mage Apple - pick another name.", "RENAME: the reverse case")
    K.eq(props(new.file(UA2)).get("p.1.name"), "Apple", "RENAME: nothing written when refused")
    d_ = str(S.describe(UR))
    K.check(d_.startswith("1 Priest Kiwi Two - ACTIVE | 2 Mage Admin - last played") and "3 Plain - no class - DELETED" in d_, "DISPLAY: describe: %s" % d_[:120])
    # a profile with no name -> profile:name / pname removed
    UN = UUID(0x0E00000000000000, 1)
    q = JClass("java.util.Properties")()
    q.setProperty("p.1.class", "Mage")
    q.setProperty("active", "1")
    S.commit(UN, q)
    bridge.put("profile:name:" + str(UN), "stale")
    bridge.put("profile:pname:" + str(UN), "stale")
    S.publish(UN)
    K.check(bridge.get("profile:name:" + str(UN)) is None and bridge.get("profile:pname:" + str(UN)) is None, "DISPLAY: no name -> both keys removed")

    # ------------------------------------------------------------------ PAGE
    UPG = UUID(0x0F00000000000000, 3)
    S.create(UPG, "1", "Banana", "Priest", True)
    S.create(UPG, "2", "Kiwi", "Mage", False)
    pg = page_for(UPG)
    pg.handleDataEvent(None, None, '{"a":"pfren1"}')
    K.eq((str(pg.renId), str(pg.renText)), ("1", "Banana"), "PAGE: pfren1 opens the row with the current name")
    t_, e_ = build(pg, UPG)
    for need in ("SkyyPfRenRow", "SkyyPfRenQ", "SkyyPfRenBox", "SkyyPfRenF", "MaxLength: 16;", "SkyyPfRenOk", "SkyyPfRenNo",
                 "New name for Priest Banana - 2 to 16 letters", "#SkyyPfRen1", "Priest Banana - ACTIVE", "Mage Kiwi"):
        K.check(need in t_, "PAGE: buildList with the row open has %r" % need)
    K.check("SkyyPfFootRow" not in t_, "PAGE: the row replaces the footer")
    K.check("#SkyyPfRenF.Value" in t_ and "Banana" in t_, "PAGE: the field is filled with the name")
    for need in ("pfrnok", "@PfName", "#SkyyPfRenF.Value", "pfrnno", "pfren1", "Validating"):
        K.check(need in e_, "PAGE: event bindings have %r" % need)
    pg.handleDataEvent(None, None, '{"a":"pfrnok","@PfName":"Bad_Name"}')
    K.check(str(pg.renId) == "1" and str(pg.renText) == "Bad_Name" and str(pg.info).startswith("Use only"), "PAGE: a refused name keeps the row + the text")
    pg.handleDataEvent(None, None, '{"@PfName":"Golden Pear","a":"pfrnok"}')
    K.check(pg.renId is None and str(pg.info) == "Banana is now called Priest Golden Pear.", "PAGE: Save renames (%s)" % pg.info)
    K.eq(props(new.file(UPG)).get("p.1.name"), "Golden Pear", "PAGE: the file")
    # typed payload names: never another button
    for typed in ("pfclose", "pfdelyes", "pfsw2", "pfyes"):
        pg.handleDataEvent(None, None, '{"a":"pfren2"}')
        pg.handleDataEvent(None, None, '{"a":"pfrnok","@PfName":"%s"}' % typed)
        K.check(pg.pending is None and pg.delAsk is None and pg.renId is None and str(pg.info) == "Kiwi is now called Mage %s." % typed,
                "PAGE: a typed %r is a name, not a button (%s)" % (typed, pg.info))
        S.renameProfile(UPG, "t", "2", "Kiwi", False)
    pg.handleDataEvent(None, None, '{"a":"pfrnok","@PfName":"pf\\"sw2\\" x"}')
    K.check(pg.pending is None, "PAGE: an escaped quote in the field is not a payload")
    pg.handleDataEvent(None, None, '{"a":"pfren2"}')
    pg.handleDataEvent(None, None, '{"a":"pfrnno"}')
    K.check(pg.renId is None and str(pg.renText) == "", "PAGE: Cancel closes the row")
    pg.handleDataEvent(None, None, '{"a":"pfren2"}')
    pg.handleDataEvent(None, None, '{"a":"pfsw2"}')
    K.check(pg.renId is None and str(pg.pending) == "2", "PAGE: another click (Switch) closes the row and works as before")
    t_, e_ = build(pg, UPG)
    K.check("Switch to Mage Kiwi? Your inventory is saved" in t_, "PAGE: the switch question names <Class> <name>")
    pg.handleDataEvent(None, None, '{"a":"pfno"}')
    pg.handleDataEvent(None, None, '{"a":"pfdel2"}')
    t_, e_ = build(pg, UPG)
    K.check("Delete profile Mage Kiwi? Its island" in t_, "PAGE: the delete question names <Class> <name>")
    pg.handleDataEvent(None, None, '{"a":"pfdelno"}')
    pg.handleDataEvent(None, None, '{"a":"pfren9"}')
    K.check(pg.renId is None and str(pg.info) == "That profile cannot be renamed right now.", "PAGE: pfren of a missing profile")
    pg.handleDataEvent(None, None, '{"a":"pfren2"}')
    pg.renId = "2"
    S.markDeleted(UPG, "2", 1000, int(System.currentTimeMillis()) + 3600000)
    t_, e_ = build(pg, UPG)
    K.check("SkyyPfRenRow" not in t_ and "SkyyPfFootRow" in t_, "PAGE: a row for a profile deleted meanwhile is not drawn (footer instead)")
    K.eq(str(PP.jsonStr('{"a" : "x\\u0041y", "b":"q"}', "a")), "xAy", "PAGE: jsonStr unicode escape")
    K.eq(str(PP.jsonStr('{"a":5}', "a")), "", "PAGE: jsonStr non-string")
    K.eq(str(PP.jsonStr(None, "a")), "", "PAGE: jsonStr null")
    t_pl2, e_pl2 = build(page_for(U_PLAIN), U_PLAIN)
    K.check("pfren1" in e_pl2 and "#SkyyPfRen1" in t_pl2 and "SkyyPfRen2" not in t_pl2, "PAGE: only the ACTIVE card has Rename")

    # ------------------------------------------------------------------ CMD: /profiles rename executed (a CommandContext stand-in holding
    # the parsed arguments; the chat reply itself needs a connection - the effect is read from the players file)
    CC = JClass("com.hypixel.hytale.server.core.command.system.CommandContext")
    av = CC.class_.getDeclaredField("argValues")
    av.setAccessible(True)
    RC = new.c("ProfRenameCmd")
    cmd = RC()
    K.eq((str(cmd.getName()), [str(x) for x in (cmd.getPermissionGroups() or [])]), ("rename", ["hytale:Adventurer"]), "CMD: /profiles rename = Adventurer")
    ex = RC.class_.getDeclaredMethod("execute", CC.class_, JClass("com.hypixel.hytale.component.Store").class_,
                                     JClass("com.hypixel.hytale.component.Ref").class_, PRc.class_,
                                     JClass("com.hypixel.hytale.server.core.universe.world.World").class_)
    ex.setAccessible(True)

    def run_cmd(u, slot, name):
        ctx = us.allocateInstance(CC.class_)
        m_ = HashMap()
        m_.put(cmd.profArg, JString(slot))
        m_.put(cmd.nameArg, JString(name))
        av.set(ctx, m_)
        try:
            ex.invoke(cmd, ctx, None, None, pref(u), None)
        except Exception:
            pass        # the reply (pr.sendMessage) has no connection here
    UC = U_PLAIN
    run_cmd(UC, "2", "Big Blue Sky")
    K.eq(props(new.file(UC)).get("p.2.name"), "Big Blue Sky", "CMD: /profiles rename 2 Big Blue Sky (a name with spaces)")
    run_cmd(UC, "Big", "x")
    K.eq(props(new.file(UC)).get("p.2.name"), "Big Blue Sky", "CMD: an unknown profile argument changes nothing")
    run_cmd(UC, "Big Blue Sky", "Admin")
    K.eq(props(new.file(UC)).get("p.2.name"), "Big Blue Sky", "CMD: a player cannot take a staff word")
    run_cmd(U_OP, "1", "Admin Main")
    K.eq(props(new.file(U_OP)).get("p.1.name"), "Admin Main", "CMD: an op can (PlayerRef.hasPermission through the module)")
    pc = new.c("ProfilesCmd")()
    K.check("rename" in [str(x) for x in pc.getSubCommands().keySet()], "CMD: /profiles has the rename sub-command")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Paths, Files, Attr = JClass("java.nio.file.Paths"), JClass("java.nio.file.Files"), JClass("java.nio.file.attribute.FileAttribute")
    d11 = os.path.join(os.path.dirname(home), "live11", "Skyy_SkyyProfiles")
    shutil.copytree(home, d11)
    pubs = {}
    for start in (1, 2):
        for tag, j, d in (("old", OLD_JAR, d11), ("new", jar, home)):
            b0 = HK.tree_hash(d)
            L = loader_for(j)
            c = lambda n: JClass(PKG + n, loader=L)
            Cfg, Store, Del, Pub, KeyFn = c("ProfCfg"), c("ProfStore"), c("ProfDel"), c("CfgPub"), c("KeyFn")
            Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
            Store.DIR, Store.SWDIR = Paths.get(os.path.join(d, "players")), Paths.get(os.path.join(d, "switching"))
            Store.INVDIR, Store.LOGF = Paths.get(os.path.join(d, "inventories")), Paths.get(os.path.join(d, "switches.log"))
            Del.ARCDIR = Paths.get(os.path.join(d, "archive"))
            up, capm, summ = Cfg.upgradeDefault(), Cfg.capMigrate(), str(Cfg.load())
            for dd in (Store.DIR, Store.SWDIR, Store.INVDIR):
                Files.createDirectories(dd, JArray(Attr)(0))
            waiting = int(Del.scanIndex())
            br = JClass("java.util.concurrent.ConcurrentHashMap")()
            JClass("java.lang.System").getProperties().put("skyy.bridge", br)
            Cfg.BRIDGE = None
            Cfg.bridge().put("profile:fn:key", KeyFn())
            Pub.start(Paths.get(os.path.dirname(d)), None)
            Pub.flush()
            time.sleep(0.3)
            Pub.flush()
            keys = {}
            pdir = os.path.join(d, "players")
            for fn in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
                if fn.endswith(".properties"):
                    u = JClass("java.util.UUID").fromString(fn[:-11])
                    keys[fn] = str(KeyFn().apply(u))
                    Store.publish(u)
            vals = dict((str(k), str(br.get(k))) for k in br.keySet() if not str(k).startswith("config:") and not str(k).startswith("profile:fn:"))
            pubs[(start, tag)] = (vals, keys, waiting, up is None, capm is None)
            if tag == "new":
                # the display text = "<Class> <name>" of that player's active profile, read independently from the file
                bad = []
                for fn in keys:
                    u = fn[:-11]
                    p = Store.load(JClass("java.util.UUID").fromString(u))
                    a = Store.keyId(p)
                    if a is None:
                        continue
                    nm, cl = str(p.getProperty("p.%s.name" % a, "")), str(c("ProfRoster").canon(p.getProperty("p.%s.class" % a, "")))
                    want = (cl + " " + nm) if cl else nm
                    if nm and (vals.get("profile:name:" + u) != want or vals.get("profile:pname:" + u) != nm):
                        bad.append((u, vals.get("profile:name:" + u), want))
                K.eq(bad, [], "D%d: profile:name = '<Class> <name>', profile:pname = the name, for every live player" % start)
            Pub.shutdown()
            a0 = HK.tree_hash(d)
            ch = sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k))
            K.eq(ch, [], "D%d %s: no file changed by the start" % (start, tag))
        vo, vn = pubs[(start, "old")][0], pubs[(start, "new")][0]
        K.eq(pubs[(start, "new")][1:], pubs[(start, "old")][1:], "D%d: the same storage keys / waiting / migrations as 0.1.11" % start)
        K.eq(sorted(set(vn) - set(vo)), sorted("profile:pname:" + k[len("profile:name:"):] for k in vo if k.startswith("profile:name:")),
             "D%d: the only new bridge keys are profile:pname:<uuid>" % start)
        K.eq(dict((k, v) for k, v in vn.items() if not k.startswith(("profile:name:", "profile:pname:"))),
             dict((k, v) for k, v in vo.items() if not k.startswith("profile:name:")), "D%d: every other bridge value = 0.1.11's" % start)
    K.notes.append("D: %d player files, names %s" % (len(pubs[(1, "new")][1]), sorted(v for k, v in pubs[(1, "new")][0].items() if k.startswith("profile:name:"))[:6]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyProfiles", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyProfiles"))
