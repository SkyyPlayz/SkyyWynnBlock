"""SkyyProfiles 0.1.4 - bare-JVM harness: the automatic profile limit (Skyy 2026-09-30: "lets make the default profile cap match the
number of classes, and we can get more profiles later with ranks.") + the taller shared SKYY CARD. Copied from the 0.1.3 page-state
harness; parts B-F compare 0.1.3 and 0.1.4 side by side with the expected 0.1.4 differences, parts G and M are new.

    python SkyyProfiles/test_skyyprofiles_0.1.4.py [--jar <SkyyProfiles-0.1.4.jar>] [--old <SkyyProfiles-0.1.3.jar>]
                                                   [--classes <SkyyClasses-0.1.9.jar>] [--live <Skyy_SkyyProfiles folder>] [--dir <scratch>] [--keep]

Build the jars first (python tools/profiles_0_1_4_patch.py + python SkyyProfiles/build_skyyprofiles_0.1.4.py; the SkyyClasses 0.1.9 jar
for part G). Child processes start fresh JVMs (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the mod jar(s);
javassist only for the bytecode step) and check:
  A  every class of the 0.1.4 jar AND of the 0.1.3 jar loads and initializes under -Xverify:all
  B  33 page states built by the REAL ProfilePage.buildList / buildCreate of both jars with the engine's own UICommandBuilder /
     UIEventBuilder (the page from its own constructor with an Unsafe-allocated PlayerRef; the player's profile Properties built here -
     one state reads the players file of the scratch COPY of the live world; bridge class:list / class:fn:kitnew / rank:fn:profileSlots;
     0.1.4: ProfCfg.MAX_SETTING auto or a number, 0.1.3: ProfCfg.MAX_PROFILES = the limit 0.1.4 must reach): the 0.1.3 states + auto
     with the real 5-class list, a player above the automatic limit, 7 / 8 profiles, rank extras, Create Profile N of M / full while open
  C  per state: 0.1.3's event bindings (type, selector, EventData, lock flag, order) - only the pfcls binding of a class card past the
     7th is gone (0.1.4 draws 7 cards); no 0.1.3 element id missing (cards past the 7th aside); every 0.1.3 text still shown except the
     list footer (0.1.4 adds where the limit comes from: checked word for word) and the texts of cards past the 7th
  D  per state, the 0.1.4 markup as the client gets it: SUI.check_markup / check_page, binding targets exist, only kit / data colours,
     no Width 0 / FlexWeight / WrapMaxLines / LetterSpacing / LayoutMode Right, Center, Full / ItemGrid; the page root 1100 x 980; the
     layout model (every child inside its parent, the body children fill 908 px exactly); every label's text fits (SUI.text_width:
     the client's own Nunito Sans advances, read-only); contrast >= 3.0:1. 0.1.4 only: every card 92 px high; one profile card per profile (none
     hidden), the Create new card only below the limit, the list footer and the Create Profile limit line (#SkyyPfSlots) word for word
  E  the SKYY CARD block: byte-identical in SkyyClasses/build_skyyclasses_0.1.9.py and here, = CARD_SHA of both patches; every look
     renders through the kit; CARD_H 92
  F  class bytes 0.1.3 vs 0.1.4: only ProfCfg, ProfStore.describe, ProfSwitch.createAndSwitch, ProfilePage (buildList, buildCreate,
     handleDataEvent, open, + warnHidden), SkyyProfilesPlugin.setup, CfgFn / CfgRows and manifest.json differ; ProfCfg gains exactly the
     limit + migration methods and fields
  G  the limit with the REAL SkyyClasses 0.1.9 jar on the classpath (its ClassDefs.listText() = what its setup() puts on class:list): 5
     playable -> 5; a 6th class enabled (Assassin) -> 6, Shaman too -> 7; fixed 1 / 3 / 6 / 8 override; no SkyyClasses (no / empty
     class:list) -> 6; duplicate names count once; rank hook +2 -> 7, +10 -> 8 (CAP_MAX), negative / not a number / throwing -> +0 (one
     WARN); a player with 6 profiles over the automatic 5 keeps all 6 (listed, switchable, nothing deleted) and is refused a 7th
     (createAndSwitch, pfnew, the players file byte for byte unchanged); a player with 4 passes the limit check; the config kit row
     (choice auto + 1-8, live, danger) through config:def / config:fn / CfgFn.cmdSetConsole (auto, 4, 9 refused, 0 refused,
     "5 profiles", AUTO), the file line after the save, hand edits through the kit's reload op (12 -> 8, junk keeps the value)
  M  the one-time migration (ProfCfg.upgradeDefault + capMigrate + load) on scratch COPIES of the live Skyy_SkyyProfiles folder (read
     only; default: the HUD mod world): the live file (the untouched 0.1.1 default) -> the 0.1.4 default + marker, second start no-op;
     another setting changed -> only the maxProfiles line (+ its comment); 4 kept; 6 changed in game before (config-changes.log, also a
     rotated one) kept; CRLF kept; no file; the untouched 0.1 file (4) -> the 0.1.4 default; two maxProfiles lines kept; marker present
     = nothing; unreadable (a folder) = nothing + no marker; "maxProfiles = 6"; owner comments with a Latin-1 byte and a UTF-8
     word kept byte for byte (the line path is an ISO-8859-1 round trip); players / inventories / switches.log byte for byte
     unchanged in every case; the live SkyLordPlayz file lists 3 of 5 after the migration
Not testable without the game (UNVERIFIED in the build report): the pages on a client, a real SkyyClasses / SkyyProfiles load order
(the limit is read at every use, so order cannot matter), the SkyyMenu cycling widget for the choice row. Nothing is deployed and the
live world is only read (copied into the scratch folder). Default scratch folder: tools/dev/scratch/prof014/profiles-014 (git-ignored),
deleted at the end unless --keep; TEMP/TMP and java.io.tmpdir point into it. Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, hashlib, struct, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.4", "0.1.3"
PKG = "com.skyy.profiles."
PREFIX = "SkyyPf"
PAGE_W, PAGE_H = 1100, 980
BODY_ID, BODY_INNER_H = "SkyyPf", 980 - 38 - 2 * 17       # 908
MIN_CONTRAST = 3.0
CARD_H_NEW = 92
CAP_MAX, CAP_FALLBACK, MAX_CARDS_NEW = 8, 6, 7
REAL_LIST = "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity"   # SkyyClasses 0.1.9 class:list
CAP_OPTS = ("auto|Auto - one per class,1|1 profile,2|2 profiles,3|3 profiles,4|4 profiles,5|5 profiles,6|6 profiles,7|7 profiles,"
            "8|8 profiles")
EXPECTED_DIFF = {"com/skyy/profiles/ProfCfg.class", "com/skyy/profiles/ProfStore.class", "com/skyy/profiles/ProfSwitch.class",
                 "com/skyy/profiles/ProfilePage.class", "com/skyy/profiles/SkyyProfilesPlugin.class", "com/skyy/profiles/CfgFn.class",
                 "com/skyy/profiles/CfgRows.class", "manifest.json"}
SCRIPT = os.path.join(HERE, "build_skyyprofiles_%s.py" % VERSION)
TWIN = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.9.py")          # the other script with the SKYY CARD block
PATCHES = [os.path.join(TOOLS, "profiles_0_1_4_patch.py"), os.path.join(TOOLS, "classes_0_1_9_patch.py")]
LIVE_DEFAULT = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Hytale", "UserData", "Saves", "HUD mod", "mods",
                            "Skyy_SkyyProfiles")
LIVE_UUID = "d8ddde89-98b2-4739-983e-a39773d582b6"      # SkyLordPlayz in the live world (3 profiles on 2026-09-30)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "prof014", "profiles-014")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyProfiles-%s.jar" % OLD_VERSION)))
CLS_JAR = os.path.abspath(arg("--classes", os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.9.jar")))
LIVE = os.path.abspath(arg("--live", LIVE_DEFAULT))
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


# ============================================================================================ the limit 0.1.4 must show (the rules)
def class_count(clist):
    """ProfCfg.classCount: the distinct names of a class:list (-1 = no / empty list)."""
    if not clist or not clist.strip():
        return -1
    names = set(p.split(":")[0].strip().lower() for p in clist.split(","))
    names.discard("")
    return len(names) if names else -1


def expected_cap(mx, clist, rank):
    """ProfCfg.capFor: the fixed number or auto (the class count; 6 without a list), 1..8, + the rank extra (still at most 8)."""
    if mx != "auto":
        base = max(1, min(CAP_MAX, int(mx)))
    else:
        n = class_count(clist)
        base = max(1, min(CAP_MAX, n if n > 0 else CAP_FALLBACK))
    extra = max(0, min(CAP_MAX, rank or 0)) if isinstance(rank, int) else 0
    return min(CAP_MAX, base + extra)


def expected_why(mx, clist, rank):
    w = "the limit on this server" if mx != "auto" else ("one per class you can play" if class_count(clist) > 0 else "the default limit")
    if isinstance(rank, int) and rank > 0:
        w += " + %d from your rank" % min(CAP_MAX, rank)
    return w


# ============================================================================================ child: build every page state of one jar
DAY, HOUR = 86400000, 3600000
CREATED = 1700000000000          # 2023-11-14 (a fixed date: the text is identical in both child JVMs)
LONG = "Abcdefghijklmnopqrstuvwxyzabcdef"     # 32 letters (ProfNames / admin names are cut to 32)
SIX = [(str(i), "Profile %d" % i, c, i * DAY) for i, c in zip(range(1, 7), ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Warrior"])]
EIGHT = [(str(i), "Slot %d" % i, c, i * HOUR) for i, c in zip(range(1, 9), ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Mage",
                                                                             "Archer", "Priest"])]
STATES = [
    # (name, view, first, profiles [(id, name, class, lastPlayed-ago-ms or 0 = never)] or "LIVE", active, pending, pickName, pickClass,
    #  info, max (0.1.4 MAX_SETTING: "auto" or a number), class:list, kits, rank extra (None = no hook, int = the hook's answer))
    ("list one", 0, False, [("1", "Profile 1", "Warrior", 3 * DAY + HOUR)], "1", None, "", None, "", "auto", None, False, None),
    ("list two pending", 0, False, [("1", "Main", "Archer", 5 * HOUR + 1800000), ("2", "Alt", "Priest", 0)], "1", "2", "", None, "", "6",
     None, False, None),
    ("list three active 2", 0, False, [("1", "Apple", "Mage", 30 * DAY), ("2", "Berry", "Berserker", 2 * HOUR), ("3", "Cherry", "Priest",
                                                                                                                 0)], "2", None, "", None,
     "Switched to Berry.", "auto", None, False, None),
    ("list six full", 0, False, SIX, "4", None, "", None, "All 6 profile slots are used.", "6", None, False, None),
    ("list over max", 0, False, [(str(i), "P%d" % i, "Mage", i * HOUR * 50) for i in range(1, 8)], "3", "5", "", None, "", "3", None, False,
     None),
    ("list no class", 0, False, [("1", "Old save", "", 4 * DAY), ("2", "New", "Warrior", HOUR * 3)], "2", None, "", None, "", "auto", None,
     False, None),
    ("list extra class", 0, False, [("1", "Dark", "Necromancer", DAY * 2), ("2", "Light", "Priest", HOUR * 5)], "1", "2", "", None, "",
     "auto", "Archer,Warrior:Blades,Mage,Berserker,Priest,Necromancer:Death", True, None),
    ("list long names", 0, False, [("1", LONG, "Berserker", DAY), ("2", LONG[::-1], "Archer", 3 * DAY), ("12", "Twelve", "Mage", 9 * DAY)],
     "12", "1", "", None, "Your profile file was repaired.", "auto", None, False, None),
    ("list pending is active", 0, False, [("1", "Solo", "Priest", DAY)], "1", "1", "", None, "", "1", None, False, None),
    ("list one of one", 0, False, [("1", "Only", "Archer", 7 * DAY)], "1", None, "", None, "", "1", None, False, None),
    ("create first", 1, True, [], None, None, "Profile 1", None, "", "auto", None, False, None),
    ("create first pick kits", 1, True, [], None, None, "Mango", "Archer", "Your current class Archer is pre-selected.", "auto", None,
     True, None),
    ("create new", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Kiwi", None, "", "auto", None, True, None),
    ("create new pick", 1, False, [("1", "Main", "Warrior", DAY), ("2", "Alt", "Mage", HOUR * 9)], "2", None, "Lychee", "Priest", "", "6",
     None, False, None),
    ("create two classes", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Papaya", "Mage", "", "auto", "Warrior,Mage", True, None),
    ("create eight classes", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Guava", None, "", "auto",
     "Archer,Warrior,Mage,Berserker,Priest,Assassin:Stealth,Shaman:Totems,Necromancer:Death", True, None),
    ("create nine classes", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Fig", "Necromancer", "", "auto",
     "Archer,Warrior,Mage,Berserker,Priest,Necromancer:Death,Druid:Nature,Monk:Fists,Bard:Songs", True, None),
    ("create info later", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Plum", None, "Assassin is coming later.", "auto", None,
     False, None),
    ("create long name", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, LONG, "Berserker", "", "auto", None, True, None),
    ("create first later pick", 1, True, [], None, None, "Pear", "Assassin", "", "auto", None, False, None),
    ("create first berserker", 1, True, [], None, None, "Grape", "Berserker", "", "auto", None, True, None),
    ("create after make error", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Lime", "Warrior",
     "You are in combat - try again in a few seconds.", "auto", None, False, None),
    # 0.1.4: the automatic limit (the real SkyyClasses list = 5), players above it, 7 / 8 profiles, rank extras, N of M on Create Profile
    ("list auto five", 0, False, [("1", "Strawberry", "Archer", 8 * DAY), ("2", "Zucchini", "Warrior", 6 * DAY), ("3", "Banana", "Priest", 0)],
     "3", None, "", None, "", "auto", REAL_LIST, True, None),
    ("list above auto", 0, False, SIX, "2", "5", "", None, "", "auto", REAL_LIST, True, None),
    ("list eight fixed", 0, False, EIGHT, "8", None, "", None, "", "8", REAL_LIST, True, None),
    ("list seven of eight", 0, False, EIGHT[:7], "1", "7", "", None, "", "8", REAL_LIST, True, None),
    ("list rank extra", 0, False, [("1", "Main", "Mage", DAY), ("2", "Alt", "Archer", HOUR)], "1", None, "", None, "", "auto", REAL_LIST,
     True, 2),
    ("list live skyy", 0, False, "LIVE", None, None, "", None, "", "auto", REAL_LIST, True, None),
    ("create auto five", 1, False, [("1", "Strawberry", "Archer", 8 * DAY), ("2", "Zucchini", "Warrior", 6 * DAY),
                                    ("3", "Banana", "Priest", 0)], "3", None, "Kiwi", "Mage", "", "auto", REAL_LIST, True, None),
    ("create full while open", 1, False, SIX[:5], "1", None, "Lemon", "Archer", "", "auto", REAL_LIST, True, None),
    ("create first auto", 1, True, [], None, None, "Mango", None, "", "auto", REAL_LIST, True, None),
    ("create fixed four", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Pear", "Priest", "", "4", REAL_LIST, True, None),
    ("create rank three", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Plum", None, "", "auto", REAL_LIST, True, 3),
]


def live_players():
    """The live-copy players file of SkyLordPlayz as [(id, name, class, lastPlayed)] + its active id (read from the scratch copy)."""
    p = {}
    f = os.path.join(SCRATCH, "live", "Skyy_SkyyProfiles", "players", LIVE_UUID + ".properties")
    for ln in open(f, encoding="latin-1").read().splitlines():
        if ln and ln[0] not in "#!" and "=" in ln:
            k, v = ln.split("=", 1)
            p[k.strip()] = v.strip()
    ids = sorted(set(k.split(".")[1] for k in p if k.startswith("p.") and k.endswith(".name")), key=int)
    return [(i, p["p.%s.name" % i], p.get("p.%s.class" % i, ""), int(p.get("p.%s.lastPlayed" % i, "0"))) for i in ids], p.get("active"), p


def run_states(jar, out, tag):
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
    UUID, Props, System, Integer = JClass("java.util.UUID"), JClass("java.util.Properties"), JClass("java.lang.System"), JClass("java.lang.Integer")
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

    @JImplements("java.util.function.Function")
    class Rank(object):
        def __init__(self, n):
            self.n = n

        @JOverride
        def apply(self, o):
            return Integer(self.n)

    new = tag == "new"
    bridge = Cfg.bridge()
    me = UUID(0x9f014, 1)
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    for (name, view, first, profs, active, pending, pick_name, pick_class, info, mx, clist, kits, rank) in STATES:
        for k in ("class:list", "class:fn:kitnew", "rank:fn:profileSlots"):
            bridge.remove(k)
        if clist is not None:
            bridge.put("class:list", clist)
        if kits:
            bridge.put("class:fn:kitnew", KitNew())
        if new:
            Cfg.MAX_SETTING = mx
            if rank is not None:
                bridge.put("rank:fn:profileSlots", Rank(rank))
        else:
            Cfg.MAX_PROFILES = expected_cap(mx, clist, rank)      # 0.1.3 has no automatic limit: it gets the number 0.1.4 must reach
        now = int(System.currentTimeMillis())
        p = Props()
        if profs == "LIVE":
            profs, active, _raw = live_players()
            for pid, pname, pcls, lp in profs:
                p.setProperty("p.%s.name" % pid, pname)
                p.setProperty("p.%s.class" % pid, pcls)
                p.setProperty("p.%s.created" % pid, str(CREATED + int(pid) * DAY))
                p.setProperty("p.%s.lastPlayed" % pid, str(now - 5 * DAY))
        else:
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
        res["states"][name] = {"error": err, "commands": cmds, "events": evs, "profiles": len(profs)}
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: parts M + G (the limit, the migration)
def _tree_hashes(root, skip=("config.properties", "cap-auto.properties", "config-changes.log")):
    """{relative path: sha1} of every file under root except the config file, the marker and the kit's files (players, inventories,
    switches.log, switching markers - what a migration must never touch)."""
    out = {}
    for dp, dn, fn in os.walk(root):
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), root).replace("\\", "/")
            if rel in skip or rel.startswith("config-history/") or rel.startswith("config-changes.log"):
                continue
            out[rel] = hashlib.sha1(open(os.path.join(dp, f), "rb").read()).hexdigest()
    return out


def run_caps(jar, cls_jar, live_copy):
    """Parts M then G in ONE child JVM (SkyyProfiles 0.1.4 + SkyyClasses 0.1.9 on the classpath); prints its checks, exit 1 on a fail."""
    import time
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    _jvm_start([jar, cls_jar])
    Cfg, Store, Sw, Page = JClass(PKG + "ProfCfg"), JClass(PKG + "ProfStore"), JClass(PKG + "ProfSwitch"), JClass(PKG + "ProfilePage")
    Pub, Fn = JClass(PKG + "CfgPub"), JClass(PKG + "CfgFn")
    Defs = JClass("com.skyy.classes.ClassDefs")
    UUID, Paths, Integer, Props = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Integer"), JClass("java.util.Properties")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    def jarr(*xs):
        a = JArray(JObject)(len(xs))
        for i, x in enumerate(xs):
            a[i] = x
        return a

    bridge = Cfg.bridge()
    base = os.path.join(SCRATCH, "caps")
    live_cfg = open(os.path.join(live_copy, "config.properties"), "rb").read()
    DEFAULT = ("\n".join(str(x) for x in Cfg.DEFAULT_LINES) + "\n").encode("utf8")
    OLD011 = ("\n".join(str(x) for x in Cfg.OLD011_LINES) + "\n").encode("utf8")
    OLD01 = ("\n".join(str(x) for x in Cfg.OLD_LINES) + "\n").encode("utf8")
    check(live_cfg == OLD011, "M: the live config.properties is byte for byte the untouched 0.1.1-0.1.3 default (maxProfiles=6)")
    check(b"\nmaxProfiles=auto\n" in DEFAULT and DEFAULT.count(b"maxProfiles=") == 1, "M: the 0.1.4 default file says maxProfiles=auto")

    # ------------------------------------------------------------------------------------------------ M: the one-time migration
    def variant(name, cfg=None, logs=None, marker=False, cfg_dir=False):
        home = os.path.join(base, "m-" + name, "Skyy_SkyyProfiles")
        shutil.copytree(live_copy, home)
        cp = os.path.join(home, "config.properties")
        if cfg_dir:
            os.remove(cp)
            os.makedirs(cp)
        elif cfg is None:
            os.remove(cp)
        else:
            open(cp, "wb").write(cfg)
        for fn_, text in (logs or {}).items():
            open(os.path.join(home, fn_), "w", newline="\n").write(text)
        if marker:
            open(os.path.join(home, "cap-auto.properties"), "w").write("result=kept\n")
        return home, cp

    def migrate(home, cp):
        Cfg.FILE = Paths.get(cp)
        Cfg.MAX_SETTING = "auto"
        before = _tree_hashes(home)
        up = Cfg.upgradeDefault()
        note = Cfg.capMigrate()
        after = _tree_hashes(home)
        check(before == after and len(before) >= 4, "M %s: players / inventories / switches.log byte for byte unchanged (%d files)"
              % (os.path.basename(os.path.dirname(home)), len(before)))
        mk = os.path.join(home, "cap-auto.properties")
        marker = {}
        if os.path.isfile(mk):
            for ln in open(mk, encoding="latin-1").read().splitlines():
                if ln and ln[0] != "#" and "=" in ln:
                    k, v = ln.split("=", 1)
                    marker[k] = v.replace("\\:", ":").replace("\\=", "=")
        return (None if up is None else str(up)), (None if note is None else str(note)), marker

    live_txt = live_cfg.decode("utf8")
    # a: the live file = the untouched default -> the 0.1.4 default, once
    home_a, cp_a = variant("live", live_cfg)
    up, note, mk = migrate(home_a, cp_a)
    check(up is None and note is not None and "untouched default" in note and "6 -> auto" in note, "M live: %s" % note)
    check(open(cp_a, "rb").read() == DEFAULT, "M live: config.properties is now the 0.1.4 default file")
    check(mk.get("result") == "default" and mk.get("version") == VERSION and "migratedAt" in mk, "M live: marker %s" % mk)
    Cfg.load()
    check(str(Cfg.MAX_SETTING) == "auto", "M live: load reads maxProfiles=auto (%s)" % Cfg.MAX_SETTING)
    t0, m0 = open(cp_a, "rb").read(), open(os.path.join(home_a, "cap-auto.properties"), "rb").read()
    check(Cfg.capMigrate() is None and open(cp_a, "rb").read() == t0
          and open(os.path.join(home_a, "cap-auto.properties"), "rb").read() == m0, "M live: a second start changes nothing (marker)")
    # b: another setting changed (in game) -> only the maxProfiles line + its comment
    b_txt = live_txt.replace("combatSeconds=10", "combatSeconds=5")
    home_b, cp_b = variant("other-setting", b_txt.encode("utf8"))
    up, note, mk = migrate(home_b, cp_b)
    want_b = b_txt.replace("maxProfiles=6", "maxProfiles=auto").replace(str(Cfg.OLD_CAP_COMMENT), "\n".join(str(x) for x in Cfg.NEW_CAP_COMMENT))
    check(mk.get("result") == "line" and open(cp_b, "rb").read().decode("utf8") == want_b and "combatSeconds=5\n" in want_b,
          "M other-setting: only maxProfiles (+ its comment) changed: %s" % note)
    Cfg.load()
    check(str(Cfg.MAX_SETTING) == "auto" and int(Cfg.COMBAT_MS) == 5000, "M other-setting: auto + combatSeconds 5 kept")
    # c: 4 kept
    c_txt = live_txt.replace("maxProfiles=6", "maxProfiles=4")
    home_c, cp_c = variant("kept4", c_txt.encode("utf8"))
    up, note, mk = migrate(home_c, cp_c)
    check(mk.get("result") == "kept" and mk.get("kept") == "4" and "kept maxProfiles=4" in (note or "")
          and open(cp_c, "rb").read().decode("utf8") == c_txt, "M kept4: the owner's 4 is kept and logged: %s" % note)
    Cfg.load()
    check(str(Cfg.MAX_SETTING) == "4" and int(Cfg.capFor(UUID(1, 2))) == 4, "M kept4: the limit is 4")
    # d / e / m: a 6 changed in game before (config-changes.log, also rotated) kept; another key in the log = line
    d_txt = b_txt
    lg_max = "2026-09-26T10:00:00\tSkyLordPlayz\t%s\tmenu\tmaxProfiles\t6\t4\tok\n2026-09-26T10:01:00\tSkyLordPlayz\t%s\tmenu\tmaxProfiles\t4\t6\tok\n" % (LIVE_UUID, LIVE_UUID)
    lg_other = "2026-09-26T10:00:00\tSkyLordPlayz\t%s\tmenu\tcombatSeconds\t10\t5\tok\n" % LIVE_UUID
    for vname, logs, want in (("log-max", {"config-changes.log": lg_other + lg_max}, "kept"),
                              ("log-rotated", {"config-changes.log": lg_other, "config-changes.log.2": lg_max}, "kept"),
                              ("log-other", {"config-changes.log": lg_other}, "line")):
        home_x, cp_x = variant(vname, d_txt.encode("utf8"), logs=logs)
        up, note, mk = migrate(home_x, cp_x)
        check(mk.get("result") == want, "M %s: %s (%s)" % (vname, want, note))
        if want == "kept":
            check(open(cp_x, "rb").read().decode("utf8") == d_txt and "config-changes.log" in (note or ""), "M %s: file unchanged" % vname)
    # f: CRLF kept
    f_txt = b_txt.replace("\n", "\r\n")
    home_f, cp_f = variant("crlf", f_txt.encode("utf8"))
    up, note, mk = migrate(home_f, cp_f)
    got_f = open(cp_f, "rb").read().decode("utf8")
    check(mk.get("result") == "line" and got_f == want_b.replace("\n", "\r\n") and "\n" not in got_f.replace("\r\n", ""),
          "M crlf: CRLF on every line, maxProfiles=auto (%r)" % got_f[:60])
    # g: no file
    home_g, cp_g = variant("nofile", None)
    up, note, mk = migrate(home_g, cp_g)
    check(mk.get("result") == "new" and not os.path.exists(cp_g), "M nofile: marker new, nothing written yet (%s)" % note)
    Cfg.load()
    check(open(cp_g, "rb").read() == DEFAULT and str(Cfg.MAX_SETTING) == "auto", "M nofile: load writes the 0.1.4 default (auto)")
    # h: the untouched 0.1 file (maxProfiles=4) -> upgradeDefault -> the 0.1.4 default -> auto
    home_h, cp_h = variant("old01", OLD01)
    up, note, mk = migrate(home_h, cp_h)
    check(up is not None and "4 -> auto" in up and open(cp_h, "rb").read() == DEFAULT and mk.get("result") == "auto",
          "M old01: %s / %s" % (up, note))
    # i: two maxProfiles lines kept
    i_txt = b_txt + "maxProfiles=6\n"
    home_i, cp_i = variant("dup", i_txt.encode("utf8"))
    up, note, mk = migrate(home_i, cp_i)
    check(mk.get("result") == "kept" and open(cp_i, "rb").read().decode("utf8") == i_txt, "M dup: two lines kept (%s)" % note)
    # j: marker present = nothing
    home_j, cp_j = variant("marker", b_txt.encode("utf8"), marker=True)
    up, note, mk = migrate(home_j, cp_j)
    check(note is None and open(cp_j, "rb").read().decode("utf8") == b_txt and mk == {"result": "kept"}, "M marker: nothing done")
    # k: unreadable (a folder named config.properties) = nothing, no marker (runs again next start)
    home_k, cp_k = variant("unreadable", cfg_dir=True)
    up, note, mk = migrate(home_k, cp_k)
    check(note is None and not mk and os.path.isdir(cp_k), "M unreadable: no change, no marker")
    # l: "maxProfiles = 6" untouched -> line
    l_txt = b_txt.replace("maxProfiles=6", "maxProfiles = 6")
    home_l, cp_l = variant("spaced", l_txt.encode("utf8"))
    up, note, mk = migrate(home_l, cp_l)
    check(mk.get("result") == "line" and "\nmaxProfiles=auto\n" in open(cp_l, "rb").read().decode("utf8"), "M spaced: %s" % note)
    # n: owner comments in other encodings (a Latin-1 byte on top, a UTF-8 word at the end) -> every byte but the maxProfiles line +
    # its comment kept (review fix: the line path is an ISO-8859-1 round trip; UTF-8 turned the Latin-1 byte into U+FFFD)
    n_top, n_end = b"# owner note: caf\xe9 (Latin-1)\n", b"# owner note: caf\xc3\xa9 (UTF-8)\n"
    home_n, cp_n = variant("encodings", n_top + b_txt.encode("utf8") + n_end)
    up, note, mk = migrate(home_n, cp_n)
    check(mk.get("result") == "line" and open(cp_n, "rb").read() == n_top + want_b.encode("utf8") + n_end,
          "M encodings: a Latin-1 byte and a UTF-8 word kept byte for byte, only maxProfiles (+ its comment) changed: %s" % note)
    Cfg.load()
    check(str(Cfg.MAX_SETTING) == "auto" and int(Cfg.COMBAT_MS) == 5000, "M encodings: load reads auto + combatSeconds 5")
    print("M. migration: 14 variants on copies of %s" % live_copy)

    # ------------------------------------------------------------------------------------------------ G: the limit
    me = UUID(0x9f014, 7)
    real = str(Defs.listText())
    check(real == REAL_LIST, "G: SkyyClasses 0.1.9 class:list = the 5 playable classes (%s)" % real)
    bridge.put("class:list", real)                          # what SkyyClassesPlugin.setup() puts on the bridge
    Cfg.MAX_SETTING = "auto"
    check(int(Cfg.classCount()) == 5 and int(Cfg.baseCap()) == 5 and int(Cfg.capFor(me)) == 5, "G: 5 playable classes -> 5")
    check(str(Cfg.capWhy(me)) == "one per class you can play" and "auto = 5" in str(Cfg.summary()), "G: why / summary: %s" % Cfg.summary())
    names = [str(x) for x in Defs.NAMES]
    en0 = [bool(x) for x in Defs.ENABLED]
    Defs.ENABLED[names.index("Assassin")] = True
    bridge.put("class:list", Defs.listText())
    check(int(Cfg.capFor(me)) == 6, "G: a 6th class enabled (Assassin) -> 6 (%s)" % bridge.get("class:list"))
    Defs.ENABLED[names.index("Shaman")] = True
    bridge.put("class:list", Defs.listText())
    check(int(Cfg.capFor(me)) == 7, "G: Shaman too -> 7")
    for i, v in enumerate(en0):
        Defs.ENABLED[i] = v
    bridge.put("class:list", Defs.listText())
    check(int(Cfg.capFor(me)) == 5, "G: back to 5")
    for v, want in (("3", 3), ("1", 1), ("8", 8), ("6", 6)):
        Cfg.MAX_SETTING = v
        check(int(Cfg.capFor(me)) == want and str(Cfg.capWhy(me)) == "the limit on this server", "G: fixed %s overrides auto" % v)
    Cfg.MAX_SETTING = "auto"
    bridge.remove("class:list")
    check(int(Cfg.capFor(me)) == 6 and str(Cfg.capWhy(me)) == "the default limit" and int(Cfg.classCount()) == -1,
          "G: no SkyyClasses (no class:list) -> 6")
    bridge.put("class:list", "  ")
    check(int(Cfg.capFor(me)) == 6, "G: an empty class:list -> 6")
    bridge.put("class:list", "Archer,archer:Bows,Mage:Sorcery, ,Mage")
    check(int(Cfg.capFor(me)) == 2, "G: duplicate names count once -> 2")
    bridge.put("class:list", real)

    @JImplements("java.util.function.Function")
    class Hook(object):
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, o):
            if self.ans == "boom":
                raise JClass("java.lang.IllegalStateException")("boom")
            return Integer(self.ans) if isinstance(self.ans, int) else self.ans

    for ans, want in ((2, 7), (10, 8), (0, 5), (-3, 5), ("x", 5), ("boom", 5)):
        bridge.put("rank:fn:profileSlots", Hook(ans))
        check(int(Cfg.capFor(me)) == want, "G: rank hook answers %r -> %d (got %d)" % (ans, want, int(Cfg.capFor(me))))
    check(bool(Cfg.RANK_WARNED), "G: a bad rank hook logs one WARN")
    bridge.put("rank:fn:profileSlots", Hook(2))
    check(str(Cfg.capWhy(me)) == "one per class you can play + 2 from your rank", "G: why with a rank: %s" % Cfg.capWhy(me))
    bridge.remove("rank:fn:profileSlots")

    # a player above the automatic limit keeps every profile and is refused a new one
    gdir = os.path.join(base, "g")
    for d in ("players", "switching", "inventories"):
        os.makedirs(os.path.join(gdir, d), exist_ok=True)
    Store.DIR, Store.SWDIR, Store.INVDIR = Paths.get(os.path.join(gdir, "players")), Paths.get(os.path.join(gdir, "switching")), \
        Paths.get(os.path.join(gdir, "inventories"))
    Store.LOGF = Paths.get(os.path.join(gdir, "switches.log"))
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    pf = os.path.join(gdir, "players", str(me) + ".properties")
    lines = ["active=1", "epoch=6", "username=Skyy"]
    for i, c in enumerate(["Archer", "Warrior", "Mage", "Berserker", "Priest", "Warrior"], 1):
        lines += ["p.%d.name=Fruit%d" % (i, i), "p.%d.class=%s" % (i, c), "p.%d.created=1790252693719" % i, "p.%d.lastPlayed=1790252693719" % i]
        if i > 1:
            lines.append("p.%d.inv=1" % i)
    open(pf, "w", newline="\n").write("\n".join(lines) + "\n")
    raw0 = open(pf, "rb").read()
    Store.DATA.clear()
    p = Store.load(me)
    check(int(Store.count(p)) == 6 and int(Cfg.capFor(me)) == 5, "G above: 6 profiles, the automatic limit 5")
    r = Sw.createAndSwitch(None, None, pr, None, "Mage", "Kiwi")
    check(str(r) == "All 5 profile slots are used.", "G above: a 7th profile is refused (%s)" % r)
    check(open(pf, "rb").read() == raw0 and int(Store.count(Store.load(me))) == 6, "G above: the players file byte for byte unchanged, 6 kept")
    d = str(Store.describe(me))
    check("slots 6/5" in d and all(("Fruit%d" % i) in d for i in range(1, 7)), "G above: /profiles list names all 6: %s" % d)
    page = Page(pr, 0, False)
    page.handleDataEvent(None, None, '{"a":"pfnew"}')
    check(str(page.info) == "All 5 profile slots are used." and int(page.view) == 0, "G above: Create new -> refused (%s)" % page.info)
    b, ev = UCB(), UEB()
    page.info = ""
    page.buildList(b, ev, me, Store.load(me))
    txt = " ".join(str(c.text) for c in b.getCommands() if c.text is not None)
    sets = dict((str(c.selector), str(c.data)) for c in b.getCommands() if str(c.type.name()) == "Set")
    cards = sorted(set(re.findall(r"#(SkyyPfCard\d+) \{", txt)))
    evs = [str(e.data) for e in ev.getEvents()]
    check(cards == ["SkyyPfCard%d" % i for i in range(1, 7)], "G above: 6 profile cards shown: %s" % cards)
    check(sorted(e for e in evs if "pfsw" in e) == sorted('{"a": "pfsw%d"}' % i for i in range(2, 7)) and not any("pfnew" in e for e in evs),
          "G above: every other profile switchable, no Create new: %s" % evs)
    foot = js(sets.get("#SkyyPfFoot.Text", ""))
    check(foot.startswith("6 profiles - this server now allows 5. You keep them all but cannot create more."), "G above: footer %r" % foot)
    # a player below the limit passes the limit check (4 of 5): the profile is created (5 of 5); the switch after it needs a live
    # player (no EntityModule in a bare JVM), so it fails there and the new profile simply stays inactive - then back to 4
    four = "\n".join(l for l in lines if not re.match(r"p\.[56]\.", l)) + "\n"
    open(pf, "w", newline="\n").write(four)
    Store.DATA.clear()
    check(int(Store.count(Store.load(me))) == 4, "G below: 4 profiles")
    try:
        r2 = Sw.createAndSwitch(None, None, pr, None, "Mage", "Kiwi")
        r2 = str(r2)
    except Exception as e:
        r2 = "threw after the limit check: %s" % type(e).__name__
    p5 = Store.load(me)
    check("profile slots are used" not in r2 and int(Store.count(p5)) == 5 and str(p5.getProperty("p.5.name")) == "Kiwi"
          and str(p5.getProperty("p.5.class")) == "Mage" and str(p5.getProperty("active")) == "1",
          "G below: past the limit check - profile 5 Kiwi (Mage) created, active still 1 (%s)" % r2)
    r3 = str(Sw.createAndSwitch(None, None, pr, None, "Priest", "Lemon"))
    check(r3 == "All 5 profile slots are used." and int(Store.count(Store.load(me))) == 5, "G below: now at 5 of 5 a 6th is refused (%s)" % r3)
    open(pf, "w", newline="\n").write(four)
    Store.DATA.clear()
    check(int(Store.count(Store.load(me))) == 4, "G below: back to 4 profiles")
    page2 = Page(pr, 0, False)
    page2.handleDataEvent(None, None, '{"a":"pfnew"}')
    check(int(page2.view) == 1, "G below: Create new opens the Create Profile view (view %s, info %r)" % (page2.view, page2.info))
    print("G. limit: real class list, +Assassin / +Shaman, fixed, no SkyyClasses, rank hook, above / below the limit")

    # the config kit row on the migrated live copy (variant a)
    mods_a = os.path.dirname(home_a)
    Cfg.FILE = Paths.get(cp_a)
    Cfg.MAX_SETTING = "auto"
    Cfg.load()
    Pub.start(Paths.get(mods_a), None)
    fn = bridge.get("config:fn:SkyyProfiles")
    hdr = bridge.get("config:def:SkyyProfiles")
    check(fn is not None and hdr is not None and str(hdr[3]) == VERSION, "G kit: config:def / config:fn published (%s)" % (hdr[3] if hdr else None))
    rows = [[str(x) for x in row] for row in hdr[7]]
    mrow = [r_ for r_ in rows if r_[0] == "maxProfiles"]
    check(len(mrow) == 1 and mrow[0][1] == "Profile limit per player" and mrow[0][2:5] == ["profiles", "choice", "auto"]
          and mrow[0][5:10] == ["", "", CAP_OPTS, "", "live,danger"] and len(mrow[0][10]) <= 100, "G kit: the maxProfiles row %s" % mrow)
    check(len(str(hdr[9])) <= 100 and "Auto" in str(hdr[9]), "G kit: note %r" % str(hdr[9]))

    def op(*args):
        return fn.apply(jarr(*args))

    def R(r_):
        return (str(r_[0]), None if r_[1] is None else str(r_[1]), str(r_[2])) if r_ is not None else None

    def settle():
        Pub.flush()
        time.sleep(0.4)
        Pub.flush()

    check(str(op("get", "maxProfiles")) == "auto", "G kit: get maxProfiles = auto (the migrated live file)")
    for typed, status, want in (("4", "ok", "4"), ("9", "bad", "4"), ("0", "bad", "4"), ("5 profiles", "ok", "5"), ("AUTO", "ok", "auto"),
                                ("8", "ok", "8")):
        r_ = R(op("set", "maxProfiles", typed, None, None, "yes", "console"))
        check(r_ is not None and r_[0] == status and str(Cfg.MAX_SETTING) == want, "G kit: set %r -> %s, MAX_SETTING %s (%s / %s)"
              % (typed, status, want, r_, Cfg.MAX_SETTING))
    r_ = R(op("set", "maxProfiles", "3", None, None, "", "console"))
    check(r_[0] == "confirm" and str(Cfg.MAX_SETTING) == "8", "G kit: a danger row asks first (%s)" % (r_,))
    check(int(Cfg.capFor(me)) == 8, "G kit: the limit follows the row (8)")
    msg = str(Fn.cmdSetConsole("maxProfiles", "auto"))
    check(str(Cfg.MAX_SETTING) == "auto" and int(Cfg.capFor(me)) == 5, "G kit: /profileadmin set maxProfiles auto (console): %s" % msg)
    settle()
    t = open(cp_a, "rb").read().decode("utf8")
    check(t.count("\nmaxProfiles=auto\n") == 1 and "profile slots per player: auto" in t, "G kit: the file line after the save")
    check(bool(Cfg.changedBefore(Paths.get(os.path.dirname(cp_a)))), "G kit: changes are now in config-changes.log (a later migration keeps them)")
    for hand, want in (("maxProfiles=12", "8"), ("maxProfiles=junk", "8"), ("maxProfiles=2", "2"), ("maxProfiles=auto", "auto")):
        cur = open(cp_a, encoding="utf8").read()           # read BEFORE opening for write (open(..., "w") truncates at once)
        check(len(re.findall(r"(?m)^maxProfiles=.*$", cur)) == 1, "G kit: one maxProfiles line before the hand edit %s" % hand)
        open(cp_a, "w", newline="\n").write(re.sub(r"(?m)^maxProfiles=.*$", hand, cur))
        R(op("reload", None, None, "console"))
        settle()
        check(str(Cfg.MAX_SETTING) == want, "G kit: hand edit %s + reload -> %s (%s)" % (hand, want, Cfg.MAX_SETTING))
    # the live SkyLordPlayz file after the migration: 3 of 5
    Store.DIR = Paths.get(os.path.join(os.path.dirname(cp_a), "players"))
    Store.DATA.clear()
    lu = UUID.fromString(LIVE_UUID)
    d = str(Store.describe(lu))
    check("slots 3/5" in d and "Strawberry" in d and "Zucchini" in d and "Banana" in d, "G live: SkyLordPlayz lists 3 of 5: %s" % d)
    Pub.shutdown()
    print("G. kit row + live profile file done")
    print("caps child: %d checks passed, %d failed" % (OKS[0], len(FAILS)))
    sys.exit(1 if FAILS else 0)


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
                  "fields_gone": sorted(set(fo) - set(fn)), "fields_new": sorted(set(fn) - set(fo)), "consts": consts,
                  "listing": dict((k, mn[k]) for k in changed + sorted(set(mn) - set(mo))),
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
def font_table(bold, secondary=False):
    """({codepoint: advance (em)}, line height (em)) of the client's glyph JSON through the kit (SUI.font_table, read-only); None
    when the client folder is absent."""
    import skyyui as SUI
    return SUI.font_table("Secondary" if secondary else "Default", bold)


def text_w(text, size, bold, upper, secondary=False):
    """The px width of one line - the kit's own measure (SUI.text_width: the client's Nunito Sans / Lexend advances)."""
    import skyyui as SUI
    if font_table(bold, secondary) is None:
        return None
    return SUI.text_width(text, size, bold=bold, font="Secondary" if secondary else "Default", upper=upper)


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


def compare_state(name, old, new, SUI, counts, data_colors, page_w, page_h, body_id, body_h, expect=None):
    """expect (0.1.4): {"event_gone": a predicate for old bindings that may be missing (the rest keep their order), "ids_ok": a predicate
    for old ids that may be gone, "text_ok": a predicate for old texts that may be gone}; returns (root, ids, sets) of the new page."""
    ex = expect or {}
    check(old["error"] is None and new["error"] is None, "%s: the page built in both jars (%s / %s)" % (name, old["error"], new["error"]))
    if old["error"] or new["error"]:
        return None
    # C1 bindings: the old ones in their order (minus the expected gone ones)
    gone = ex.get("event_gone") or (lambda e: False)
    want = [e for e in old["events"] if not gone(e)]
    check(new["events"] == want, "%s: event bindings = 0.1.3's (%d, %d expected gone; got %d)" % (name, len(old["events"]),
                                                                                              len(old["events"]) - len(want), len(new["events"])))
    counts["bindings"] += len(new["events"])
    # C2 ids
    oi, ni = ids_of(old), ids_of(new)
    idok = ex.get("ids_ok") or (lambda i: False)
    miss = sorted(i for i in set(oi) - set(ni) if not idok(i))
    check(not miss, "%s: no old id missing: %s" % (name, miss))
    counts["ids"] += len(set(oi))
    # C3 texts
    ot, nt = texts_of(old), texts_of(new)
    tok = ex.get("text_ok") or (lambda t: False)
    lost = sorted((t for t in ot - nt if not tok(t)), key=str)
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
    return root, ids, dict((i, v) for i, p, v in ap.sets if p == "Text")


PREFIX_OF = [PREFIX]


def new_counts():
    return dict(states=0, bindings=0, ids=0, texts=0, colours=0, check_page=0, appends=0, placed=0, min_row_slack=10 ** 6, wrapped=0,
                lines=0, buttons=0, max_lines_fill=0.0, max_line_fill=0.0, widest=(0.0, ""), shrunk=set(), text_skipped=False,
                contrasts=0, min_contrast=(99.0, ""), max_payload=0)


def report_counts(counts):
    print("B-D. %(states)d states: %(bindings)d bindings as expected, %(ids)d old ids kept, %(texts)d old texts shown (expected changes aside); "
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
    check(ns["CARD_H"] == CARD_H_NEW and ns["card_list_h"](8) == 8 + 8 * (CARD_H_NEW + 4)
          and ns["card_text_w"](1058, 3) == 1058 - 4 - 216 - 200 - 12, "E: card sizes (CARD_H %s)" % ns["CARD_H"])
    print("E. SKYY CARD block: identical in both scripts + both patches (sha %s), %d look x cell variants, %d markups checked"
          % (sha[:12], n, n_mk))


# ============================================================================================ main
KNOWN = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Shaman"]      # the fallback roster = SkyyClasses' 7 classes
FOOT_TAIL = " Switching saves your inventory and takes you to the island of the other profile. Not while in combat."


def roster_extras(clist):
    """ProfRoster.roster(): the 7 known classes first, then every class:list name it does not know, in list order."""
    names = [x.split(":")[0].strip() for x in (clist or "").split(",") if x.strip()]
    return [x for x in names if x.lower() not in [k.lower() for k in KNOWN]]


def roster_size(clist):
    return len(KNOWN) + len(roster_extras(clist))


def roster_index(clist, name):
    order = [k.lower() for k in KNOWN + roster_extras(clist)]
    return order.index(name.lower()) if name.lower() in order else -1


def all_hashes(root):
    out = {}
    for dp, dn, fn in os.walk(root):
        for f in fn:
            out[os.path.relpath(os.path.join(dp, f), root)] = hashlib.sha1(open(os.path.join(dp, f), "rb").read()).hexdigest()
    return out


def main():
    if "--run" in sys.argv:
        run_states(arg("--run"), arg("--out"), arg("--tag"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    if "--caps" in sys.argv:
        run_caps(arg("--caps"), arg("--classes"), arg("--livecopy"))
        return
    for j in (JAR, OLD_JAR, CLS_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not SCRATCH.replace("\\", "/").lower().startswith(os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower()):
        sys.exit("--dir must be inside tools/dev/scratch/ (it is deleted afterwards): " + SCRATCH)
    if not (os.path.isfile(os.path.join(LIVE, "config.properties")) and os.path.isfile(os.path.join(LIVE, "players", LIVE_UUID + ".properties"))):
        sys.exit("no live Skyy_SkyyProfiles folder at %s (--live)" % LIVE)
    if os.path.isdir(SCRATCH):
        shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    # the live world is only READ: one copy into the scratch folder; every test works on copies of the copy
    live_before = all_hashes(LIVE)
    copy = os.path.join(SCRATCH, "live", "Skyy_SkyyProfiles")
    shutil.copytree(LIVE, copy)
    check(all_hashes(copy) == live_before, "the scratch copy of the live folder is byte for byte the live folder (%d files)" % len(live_before))
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    me = os.path.abspath(__file__)
    outs = {}
    for tag, j in (("new", JAR), ("old", OLD_JAR)):
        outs[tag] = os.path.join(SCRATCH, "states-%s.json" % tag)
        p = subprocess.run([sys.executable, me, "--run", j, "--out", outs[tag], "--tag", tag, "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(outs[tag]), "child JVM for %s ran" % j)
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "bytecode child ran")
    p = subprocess.run([sys.executable, me, "--caps", JAR, "--classes", CLS_JAR, "--livecopy", copy, "--dir", SCRATCH], env=env)
    check(p.returncode == 0, "M + G child (the migration on live copies, the limit with SkyyClasses 0.1.9): see its lines above")
    if not (os.path.isfile(outs["new"]) and os.path.isfile(outs["old"]) and os.path.isfile(bco)):
        return finish()
    new, old = json.load(open(outs["new"])), json.load(open(outs["old"]))
    # A
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                            os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    # B-D (+ the 0.1.4 page checks)
    import skyyui as SUI
    SUI.verify(quiet=True)
    src = open(SCRIPT, encoding="utf8").read()
    data_colors = eval(re.search(r"^UI_DATA_COLORS = (\[.*?\](?:\s*\+\s*\[.*?\])?)\n", src, re.M | re.S).group(1))
    counts = new_counts()
    extra = {"cards": 0, "footers": 0, "slots": 0, "profiles": 0}
    for st in STATES:
        nm, view, first, profs, active, pending, pick_name, pick_class, info, mx, clist, kits, rank = st
        check(nm in new["states"] and nm in old["states"], "B: state %s built by both jars" % nm)
        if not (nm in new["states"] and nm in old["states"]):
            continue
        ns_, os_ = new["states"][nm], old["states"][nm]
        cap, why, n = expected_cap(mx, clist, rank), expected_why(mx, clist, rank), ns_["profiles"]
        oset = sets_of(os_)
        foot_old = oset.get("SkyyPfFoot")
        hidden = set(v for k, v in oset.items() if re.match(r"SkyyPfCls[7-9]", k))      # texts of class cards past the 7th (0.1.3 drew 8)
        if view == 1 and pick_class and roster_index(clist, pick_class) >= MAX_CARDS_NEW:
            hidden.add("Selected")          # the picked class's card is the 8th: 0.1.3 showed its "Selected" state word, 0.1.4 draws 7
        expect = {"event_gone": (lambda e: re.search(r'"pfcls[7-9]"', e[2] or "") is not None),
                  "ids_ok": (lambda i: re.match(r"SkyyPf(Cls|Ico|CTx|CAct|Pick)[7-9]", i) is not None),
                  "text_ok": (lambda t, f=foot_old, h=hidden: t == f or t in h)}
        got = compare_state(nm, os_, ns_, SUI, counts, data_colors, PAGE_W, PAGE_H, BODY_ID, BODY_INNER_H, expect)
        if got is None:
            continue
        root, ids, sets = got
        cards = [i for i in ids if re.fullmatch(r"SkyyPf(Card\d+|Cls\d+|NewCard)", i)]
        check(cards and all(_pairs(ids[c]["props"].get("Anchor")).get("Height") == CARD_H_NEW for c in cards),
              "D %s: every card %d px high (%d cards)" % (nm, CARD_H_NEW, len(cards)))
        extra["cards"] += len(cards)
        if view == 0:
            pcards = [c for c in cards if c.startswith("SkyyPfCard")]
            check(len(pcards) == n and (("SkyyPfNewCard" in ids) == (n < cap)), "D %s: %d profile cards (all of them), Create new %s"
                  % (nm, n, "shown" if n < cap else "hidden"))
            extra["profiles"] += len(pcards)
            confirm = any(e[1] == "#SkyyPfYes" for e in ns_["events"])
            if not confirm:
                used = ("%d of %d profile slots used (%s)." % (n, cap, why)) if n <= cap else \
                    ("%d profiles - this server now allows %d. You keep them all but cannot create more." % (n, cap))
                check(sets.get("SkyyPfFoot") == used + FOOT_TAIL, "D %s: footer %r" % (nm, sets.get("SkyyPfFoot")))
                if n <= cap:
                    check(foot_old == ("%d of %d profile slots used." % (n, cap)) + FOOT_TAIL, "C %s: 0.1.3 said %r" % (nm, foot_old))
                else:
                    check(foot_old == sets.get("SkyyPfFoot"), "C %s: the over-the-limit footer is 0.1.3's" % nm)
                extra["footers"] += 1
        else:
            have = n
            want = ("All %d profile slots are used - you cannot create another profile." % cap) if (not first and have >= cap) else \
                ("This is profile %d of %d - %s." % (have + 1, cap, why))
            check(sets.get("SkyyPfSlots") == want, "D %s: limit line %r (want %r)" % (nm, sets.get("SkyyPfSlots"), want))
            ccards = [c for c in cards if c.startswith("SkyyPfCls")]
            check(len(ccards) == min(roster_size(clist), MAX_CARDS_NEW), "D %s: %d class cards" % (nm, len(ccards)))
            extra["slots"] += 1
    report_counts(counts)
    print("D (0.1.4). %(cards)d cards 92 px high, %(profiles)d profile cards (none hidden), %(footers)d list footers, %(slots)d Create "
          "Profile limit lines word for word" % extra)
    # E
    check_card_block(SUI, data_colors)
    # F
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    check(sorted(zo.namelist()) == sorted(zn.namelist()), "F: same entries in both jars")
    diff = set(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    same = len(set(zo.namelist()) & set(zn.namelist())) - len(diff)
    check(diff == EXPECTED_DIFF, "F: exactly %s differ, got %s" % (sorted(EXPECTED_DIFF), sorted(diff)))
    check(not [n for n in zn.namelist() if n.endswith(".ui")], "F: no .ui files in the jar (inline pages only)")
    mo, mn = json.loads(zo.read("manifest.json")), json.loads(zn.read("manifest.json"))
    check(set(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k)) <= {"Version", "Name", "Description"} and mn.get("Version") == VERSION,
          "F: manifest: only the version differs: %s" % sorted(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k)))
    bc = json.load(open(bco))
    sig = "(Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;" \
          "Ljava/util/UUID;Ljava/util/Properties;)V"
    pg = bc.get("com/skyy/profiles/ProfilePage.class", {})
    check(sorted(m.split("(")[0] for m in pg.get("changed", [])) == ["buildCreate", "buildList", "handleDataEvent", "open"]
          and "buildList" + sig in pg["changed"] and pg.get("new") == ["<clinit>()V", "warnHidden(I)V"] and not pg.get("gone")
          and pg.get("fields_gone") == [] and pg.get("fields_new") == ["HIDDEN_WARNED Z"] and pg.get("consts") == {"MAX_CARDS": ["8", "7"]}
          and "HIDDEN_WARNED" in pg["listing"]["<clinit>()V"] and "ProfCfg.capFor" in pg["listing"]["handleDataEvent(Lcom/hypixel/hytale/"
                                                                                                   "component/Ref;Lcom/hypixel/hytale/"
                                                                                                   "component/Store;Ljava/lang/String;)V"],
          "F: ProfilePage (+ warnHidden, the HIDDEN_WARNED initializer, MAX_CARDS 8 -> 7, the pfnew limit = capFor): %s" % dict(
              (k, pg.get(k)) for k in ("changed", "new", "gone", "fields_gone", "fields_new", "consts")))
    cfgc = bc.get("com/skyy/profiles/ProfCfg.class", {})
    want_new = ["baseCap()I", "capFor(Ljava/util/UUID;)I", "capMigrate()Ljava/lang/String;", "capNote()Ljava/lang/String;",
                "capWhy(Ljava/util/UUID;)Ljava/lang/String;", "changedBefore(Ljava/nio/file/Path;)Z", "clampCap(J)I", "classCount()I",
                "extraSlots(Ljava/util/UUID;)I", "isAuto()Z", "linesBytes([Ljava/lang/String;)[B", "rankWarn(Ljava/lang/String;)V"]
    check(sorted(cfgc.get("new", [])) == want_new and not cfgc.get("gone")
          and set(m.split("(")[0] for m in cfgc.get("changed", [])) <= {"summary", "upgradeDefault", "load", "<clinit>"}
          and cfgc.get("fields_gone") == ["MAX_PROFILES I"]
          and sorted(f.split()[0] for f in cfgc.get("fields_new", [])) == ["CAP_FALLBACK", "CAP_MAX", "MAX_SETTING", "NEW_CAP_COMMENT",
                                                                          "OLD011_LINES", "OLD_CAP_COMMENT", "RANK_FN", "RANK_WARNED"],
          "F: ProfCfg: the limit + migration methods / fields only: %s" % dict(
              (k, cfgc.get(k)) for k in ("changed", "new", "gone", "fields_gone", "fields_new")))
    stc = bc.get("com/skyy/profiles/ProfStore.class", {})
    check(stc.get("changed") == ["describe(Ljava/util/UUID;)Ljava/lang/String;"] and not stc.get("new") and not stc.get("gone")
          and stc.get("fields_same"), "F: ProfStore: only describe() (slots n/limit): %s" % stc.get("changed"))
    swc = bc.get("com/skyy/profiles/ProfSwitch.class", {})
    cas = [m for m in swc.get("changed", []) if m.startswith("createAndSwitch(")]
    check(len(cas) == 1 and len(swc.get("changed", [])) == 1 and not swc.get("new") and not swc.get("gone") and swc.get("fields_same")
          and "ProfCfg.capFor" in swc["listing"][cas[0]], "F: ProfSwitch: only createAndSwitch (its limit check = capFor); switchTo "
                                                          "unchanged: %s" % swc.get("changed"))
    sp = bc.get("com/skyy/profiles/SkyyProfilesPlugin.class", {})
    lst = sp.get("listing", {}).get("setup()V", "")
    check(sp.get("changed") == ["setup()V"] and not sp.get("new") and not sp.get("gone") and sp.get("fields_same")
          and "ProfCfg.capMigrate" in lst, "F: SkyyProfilesPlugin: only setup() (+ capMigrate): %s" % sp.get("changed"))
    check(0 <= lst.find("ProfCfg.upgradeDefault") < lst.find("ProfCfg.capMigrate") < lst.find("ProfCfg.load") < lst.find("CfgPub.start"),
          "F: setup order upgradeDefault -> capMigrate -> load -> ... -> CfgPub.start")
    fnc = bc.get("com/skyy/profiles/CfgFn.class", {})
    check(not fnc or (not fnc.get("new") and not fnc.get("gone") and fnc.get("fields_same") and fnc.get("version_only")),
          "F: CfgFn: only the version string differs: %s" % fnc.get("changed"))
    print("F. class bytes: %d entries identical, differ: %s; methods: %s" % (
        same, ", ".join(sorted(n.split("/")[-1] for n in diff)),
        "; ".join("%s %s" % (n.split("/")[-1][:-6], dict((x, bc[n][x]) for x in ("changed", "new", "gone") if bc[n][x]))
                  for n in sorted(bc))))
    check(all_hashes(LIVE) == live_before, "the live Skyy_SkyyProfiles folder was only read (byte for byte unchanged)")
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
