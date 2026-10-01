"""SkyyProfiles 0.1.5 - bare-JVM harness: DELETE A PROFILE (Skyy 2026-10-01: "add a way to delete a profile. (make sure there is a
confirm question. then a 6 hour undo window.") + the footer Close. Built on the 0.1.4 harness (its markup model, layout, text and
contrast checks are copied unchanged); parts B-F compare 0.1.4 and 0.1.5 side by side, parts G, R and S are new.

    python SkyyProfiles/test_skyyprofiles_0.1.5.py [--jar <SkyyProfiles-0.1.5.jar>] [--old <SkyyProfiles-0.1.4.jar>]
                                                   [--classes <SkyyClasses-0.1.9.jar>] [--live <Skyy_SkyyProfiles folder>] [--dir <scratch>] [--keep]

Build first (python tools/profiles_0_1_5_patch.py + python SkyyProfiles/build_skyyprofiles_0.1.5.py). Child processes start fresh JVMs
(the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the mod jar(s); javassist only for the bytecode step):
  A  every class of the 0.1.5 jar AND of the 0.1.4 jar loads and initializes under -Xverify:all
  B  page states built by the REAL ProfilePage.buildList / buildCreate with the engine's UICommandBuilder / UIEventBuilder: the 0.1.4
     harness's 33 states in both jars (compat) + 13 delete states in 0.1.5 only (deleted cards, the delete question, restore, over the
     limit, more cards than the well holds, a deadline already past, the live copy of Skyy's world with a deleted profile)
  C  compat: the create view is byte for byte 0.1.4's; the list view keeps every 0.1.4 binding in its order (the only new ones:
     pfdel<id> after its card's pfsw<id>, pfclose with the footer), every 0.1.4 element id and every 0.1.4 text
  D  every 0.1.5 state as the client gets it: SUI.check_markup / check_page, binding targets exist, only kit / data colours, no
     Width 0 / FlexWeight / WrapMaxLines / LetterSpacing / LayoutMode Right, Center, Full / ItemGrid, root 1100 x 980, the layout
     model (children inside parents, the body fills 908 px), every text fits (the client's own glyph tables), contrast >= 3.0:1;
     0.1.5: the exact bindings of every state (computed here from the rules), cards = live then deleted (max 8 with Create new), each
     card's look (active / question / deleted / normal background), Delete only on live non-active cards (Destructive texture),
     Restore on deleted cards, the delete question word for word (Destructive Delete + Secondary Cancel), the footer word for word,
     Close (Secondary + the cancel sound) exactly when the footer shows
  E  the SKYY CARD block: byte-identical in SkyyClasses/build_skyyclasses_0.1.9.py and here, = CARD_SHA of both 0.1.4 patches + the
     0.1.5 patch (unchanged)
  F  class bytes 0.1.4 vs 0.1.5: the expected classes / methods differ, the rest is byte-identical; 8 new classes
  G  the logic on a scratch COPY of the live Skyy_SkyyProfiles folder (SkyLordPlayz's real files): delete refused for the active /
     last profile (+ unknown name, a running switch, a failed marker; the players file byte for byte unchanged), the confirm question
     required (page: pfdel -> pfdelno / pfdelyes; command: first run asks, the same again within 10 s deletes, a stale repeat asks
     again), what a delete writes (p.<id>.deleted / until = +6 h, nothing else), the key / epoch / profile:list / profile:fn:state,
     switching to a deleted profile refused, a NEW profile while one is pending (a new id; the deleted id never reused), restore within
     the window (exactly as it was), restore over the limit, expiry after the window with a simulated clock (files MOVED to
     archive/, nothing deleted), a late Restore, a failed marker keeps it pending, the admin archive list / restore (name taken ->
     renamed; a pending one; unknown), no item duplication (every inventory snapshot exists exactly once, slot totals constant) and
     other mods' files untouched across delete / restore / switch / archive, the config kit row deleteUndoHours (12 ok, 0 / 169 refused)
     Review fixes: G5b the limit holds (p.<id>.slots; delete -> create -> restore refused on the page / command / restore(), the
     review's 6-round loop stays at the limit, a LOWERED limit still restores every deleted profile in any order); G6 a profile past
     its deadline kept pending by a FAILED marker (player Restore refused, /profiles list + login line + archive list wording, admin
     restore ignores the deadline); G6b archive write failures (no junk folder left, one WARN per profile, a folder that already
     exists is left alone); the BUSY wording; profile:fn:state(UUID) = null. D: the overdue card = Expired (no Restore).
  R  restart keeps the timer: a FRESH JVM reads the files G left (scanIndex finds the waiting deletion, the time left is the stored
     deadline's), a simulated clock 5 h later archives nothing, at the deadline it archives; the join path (ProfJoin.prepare) archives
     a window that ended while the server was down and repairs a player left with only deleted profiles
  S  start twice on a scratch COPY of the live data (the setup order: upgradeDefault, capMigrate, load, folders, scanIndex, a sweep,
     the config kit): nothing in the folder changes, no archive folder appears, Skyy's live profiles read back (describe), the window
     is 6 h
Not testable without the game (UNVERIFIED in the build report): the pages on a client, the small Switch + Delete pair, the sweep thread
of a real server. Nothing is deployed; the live world is only read (copied into the scratch folder). Default scratch folder:
tools/dev/scratch/prof015/profiles-015 (git-ignored), deleted at the end unless --keep; TEMP/TMP and java.io.tmpdir point into it.
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, hashlib, struct, zlib, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.5", "0.1.4"
PKG = "com.skyy.profiles."
PREFIX = "SkyyPf"
PAGE_W, PAGE_H = 1100, 980
BODY_ID, BODY_INNER_H = "SkyyPf", 980 - 38 - 2 * 17       # 908
MIN_CONTRAST = 3.0
CARD_H_NEW = 92
CAP_MAX, CAP_FALLBACK, MAX_CARDS_NEW = 8, 6, 7
MAX_ID = 256                     # 0.1.5 review: 64 -> 256
HOUR, DAY, MIN = 3600000, 86400000, 60000
UNDO_MS = 6 * HOUR
BUSY_TEXT = "Your profiles are busy for a moment (a switch or a clean-up is running) - try again in a few seconds."
EXPIRED_L3 = "Deleted - the undo time is over. Ask an admin."
REAL_LIST = "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity"   # SkyyClasses 0.1.9 class:list
NEW_CLASSES = ["ProfDel", "ProfSweep", "StateFn", "ProfDeleteCmd", "ProfRestoreCmd", "AdmArchListCmd", "AdmArchResCmd", "AdmArchiveCmd"]
EXPECTED_DIFF = set("com/skyy/profiles/%s.class" % c for c in (
    "ProfCfg", "ProfStore", "ProfSwitch", "ProfilePage", "ProfJoin", "ReadyTask", "ProfilesCmd", "AdmInfoCmd", "ProfileAdminCmd",
    "SkyyProfilesPlugin", "CfgFn", "CfgRows", "CfgFile", "ProfNames")) | {"manifest.json"}     # CfgFile: its per-row arrays (one row
# more); ProfNames: javassist inlines ProfCfg.MAX_ID (64 -> 256, review) into its loop
SCRIPT = os.path.join(HERE, "build_skyyprofiles_%s.py" % VERSION)
TWIN = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.9.py")          # the other script with the SKYY CARD block
PATCHES = [os.path.join(TOOLS, "profiles_0_1_4_patch.py"), os.path.join(TOOLS, "classes_0_1_9_patch.py")]
PATCH_015 = os.path.join(TOOLS, "profiles_0_1_5_patch.py")
LIVE_DEFAULT = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Hytale", "UserData", "Saves", "HUD mod", "mods",
                            "Skyy_SkyyProfiles")
LIVE_UUID = "d8ddde89-98b2-4739-983e-a39773d582b6"      # SkyLordPlayz in the live world


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "prof015", "profiles-015")))
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


# ============================================================================================ the rules (what 0.1.4 / 0.1.5 must show)
def class_count(clist):
    if not clist or not clist.strip():
        return -1
    names = set(p.split(":")[0].strip().lower() for p in clist.split(","))
    names.discard("")
    return len(names) if names else -1


def expected_cap(mx, clist, rank):
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


def fmt_left(ms):
    """ProfStore.fmtLeft"""
    if ms < 60000:
        return "less than a minute"
    m = ms // 60000
    h = m // 60
    m -= h * 60
    if h == 0:
        return "%d min" % m
    return "%d h" % h + (" %d min" % m if m > 0 else "")


def safe(t):
    """ProfilePage.safe"""
    return (t or "").replace(":", " ").replace(";", " ").replace(",", " ").replace("{", "(").replace("}", ")").replace('"', " ") \
        .replace("'", " ").replace("\\", " ")


# ============================================================================================ child: build every page state of one jar
CREATED = 1700000000000          # 2023-11-14 (a fixed date: the text is identical in both child JVMs)
LONG = "Abcdefghijklmnopqrstuvwxyzabcdef"     # 32 letters
SIX = [(str(i), "Profile %d" % i, c, i * DAY) for i, c in zip(range(1, 7), ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Warrior"])]
EIGHT = [(str(i), "Slot %d" % i, c, i * HOUR) for i, c in zip(range(1, 9), ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Mage",
                                                                             "Archer", "Priest"])]
FOUR = [("1", "Strawberry", "Archer", 8 * DAY), ("2", "Zucchini", "Warrior", 6 * DAY), ("3", "Banana", "Priest", 2 * HOUR),
        ("4", "Watermelon", "Warrior", 0)]
LEFT = 5 * HOUR + 12 * MIN + 30000          # a deleted profile's time left in the states (prints "5 h 12 min")
# (name, view, first, profiles [(id, name, class, lastPlayed-ago-ms or 0 = never)] or "LIVE", active, pending, pickName, pickClass,
#  info, max, class:list, kits, rank, deleted {id: ms left until the deadline}, delAsk)   - the 0.1.4 states get deleted {} / None
STATES_014 = [
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
STATES_COMPAT = [st + ({}, None) for st in STATES_014]
STATES_DEL = [
    ("del pending one", 0, False, FOUR, "4", None, "", None, "", "auto", REAL_LIST, True, None, {"3": LEFT}, None),
    ("del ask", 0, False, FOUR, "4", None, "", None, "", "auto", REAL_LIST, True, None, {}, "2"),
    ("del ask with a deleted", 0, False, FOUR, "1", None, "", None, "", "auto", REAL_LIST, True, None, {"2": LEFT}, "3"),
    ("del ask long", 0, False, [("1", LONG, "Berserker", DAY), ("2", LONG[::-1], "Archer", 3 * DAY)], "1", None, "", None, "", "auto",
     REAL_LIST, True, None, {}, "2"),
    ("del after restore", 0, False, FOUR, "4", None, "", None, "Banana is back - exactly as it was.", "auto", REAL_LIST, True, None, {},
     None),
    ("del restore over limit", 0, False, SIX, "1", None, "",
     None, "Profile 6 is back - exactly as it was. You now have 6 profiles - more than the 5 allowed - so you cannot create more.", "auto",
     REAL_LIST, True, None, {}, None),
    ("del only active live", 0, False, FOUR[:3], "1", None, "", None, "Zucchini is deleted. Restore it within 6 hours - after that it is gone.",
     "auto", REAL_LIST, True, None, {"2": LEFT, "3": 30 * MIN + 30000}, None),
    ("del seven plus two", 0, False, EIGHT[:7] + [("9", "Late", "Mage", DAY), ("10", "Later", "Priest", DAY)], "1", None, "", None, "", "8",
     REAL_LIST, True, None, {"9": LEFT, "10": 2 * HOUR + 30000}, None),
    ("del eight live plus one", 0, False, EIGHT + [("11", "Gone soon", "Mage", DAY)], "8", None, "", None, "", "8", REAL_LIST, True, None,
     {"11": HOUR + 30000}, None),
    ("del deadline passed", 0, False, FOUR, "4", None, "", None, "", "auto", REAL_LIST, True, None, {"1": -30000}, None),
    ("del switch question", 0, False, FOUR, "4", "2", "", None, "", "auto", REAL_LIST, True, None, {"3": LEFT}, None),
    ("del stale ask", 0, False, FOUR, "4", None, "", None, "", "auto", REAL_LIST, True, None, {"2": LEFT}, "2"),
    ("del live skyy", 0, False, "LIVE", None, None, "", None, "", "auto", REAL_LIST, True, None, {"LIVE2": LEFT}, None),
    # review fixes: Restore refused for want of a slot (the longest name), an overdue card beside a live delete question
    ("del restore no slot", 0, False, FOUR + [("5", "Kiwi", "Mage", DAY), ("6", LONG, "Priest", 2 * DAY)], "1", None, "", None,
     "No free slot for %s - you have 5 profiles and the limit is 5. Delete another profile first." % LONG, "auto", REAL_LIST, True,
     None, {"6": LEFT}, None),
    ("del expired and ask", 0, False, FOUR, "4", None, "", None, "", "auto", REAL_LIST, True, None, {"2": -HOUR}, "3"),
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


def resolve_state(st):
    """(profiles, active, deleted {id: ms left}) with LIVE read from the live copy (LIVE2 = the live player's lowest non-active id)."""
    nm, view, first, profs, active, pending, pick_name, pick_class, info, mx, clist, kits, rank, deleted, ask = st
    if profs == "LIVE":
        lp, active, _raw = live_players()
        profs = [(pid, pname, pcls, 5 * DAY) for pid, pname, pcls, _lp in lp]
        if "LIVE2" in deleted:
            victim = [x[0] for x in profs if x[0] != active][0]
            deleted = {victim: deleted["LIVE2"]}
    return profs, active, deleted


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
    me = UUID(0x9f015, 1)
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    for st in (STATES_COMPAT + (STATES_DEL if new else [])):
        name, view, first, _profs, _active, pending, pick_name, pick_class, info, mx, clist, kits, rank, _deleted, ask = st
        profs, active, deleted = resolve_state(st)
        for k in ("class:list", "class:fn:kitnew", "rank:fn:profileSlots"):
            bridge.remove(k)
        if clist is not None:
            bridge.put("class:list", clist)
        if kits:
            bridge.put("class:fn:kitnew", KitNew())
        Cfg.MAX_SETTING = mx
        if rank is not None:
            bridge.put("rank:fn:profileSlots", Rank(rank))
        now = int(System.currentTimeMillis())
        p = Props()
        for pid, pname, pcls, ago in profs:
            p.setProperty("p.%s.name" % pid, pname)
            p.setProperty("p.%s.class" % pid, pcls)
            p.setProperty("p.%s.created" % pid, str(CREATED + int(pid) * DAY))
            p.setProperty("p.%s.lastPlayed" % pid, str(now - ago) if ago else "0")
        dl = {}
        for pid, left in deleted.items():
            until = now + left
            p.setProperty("p.%s.deleted" % pid, str(until - UNDO_MS))
            p.setProperty("p.%s.until" % pid, str(until))
            dl[pid] = left
        if active:
            p.setProperty("active", active)
        page = Page(pr, 0, first)                   # view 0 in the constructor: no prepareCreate (no player file needed)
        page.view, page.pending, page.pickName, page.pickClass, page.info = view, pending, pick_name, pick_class, info
        if new:
            page.delAsk = ask
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
        res["states"][name] = {"error": err, "commands": cmds, "events": evs, "profiles": [list(x) for x in profs], "active": active,
                               "deleted": dl, "now": now}
    json.dump(res, open(out, "w"), indent=1)


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


# ============================================================================================ child: part G (delete / restore / archive)
def _props(path):
    """a players / record file as a dict (java.util.Properties text: key=value, \\: and \\= unescaped)"""
    out = {}
    if not os.path.isfile(path):
        return out
    for ln in open(path, encoding="latin-1").read().splitlines():
        if ln and ln[0] not in "#!" and "=" in ln:
            k, v = ln.split("=", 1)
            out[k.strip().replace("\\:", ":").replace("\\=", "=")] = v.strip().replace("\\:", ":").replace("\\=", "=")
    return out


def _sha(path):
    return hashlib.sha1(open(path, "rb").read()).hexdigest()


def _slots(path):
    """the saved slot count of one inventory snapshot (its "count", extended JSON)"""
    try:
        c = json.loads(open(path, encoding="utf8").read()).get("count", 0)
        if isinstance(c, dict):
            c = c.get("$numberInt", c.get("$numberLong", 0))
        return int(c)
    except Exception:
        return -1


def _inv_census(home):
    """{content sha1: [paths]} of every inventory snapshot under inventories/ and archive/ + the total saved slot count"""
    out, slots = {}, 0
    for sub in ("inventories", "archive"):
        for dp, dn, fn in os.walk(os.path.join(home, sub)):
            for f in fn:
                if f.endswith(".json"):
                    p = os.path.join(dp, f)
                    out.setdefault(_sha(p), []).append(os.path.relpath(p, home).replace("\\", "/"))
                    slots += _slots(p)
    return out, slots


def _tree(root, skip_dirs=()):
    out = {}
    for dp, dn, fn in os.walk(root):
        rel_dir = os.path.relpath(dp, root).replace("\\", "/")
        if any(rel_dir == d or rel_dir.startswith(d + "/") for d in skip_dirs):
            continue
        for f in fn:
            out[os.path.relpath(os.path.join(dp, f), root).replace("\\", "/")] = _sha(os.path.join(dp, f))
    return out


def run_logic(jar, cls_jar, live_copy):
    from jpype import JClass, JArray, JObject
    _jvm_start([jar, cls_jar])
    Cfg, Store, Sw, Page = JClass(PKG + "ProfCfg"), JClass(PKG + "ProfStore"), JClass(PKG + "ProfSwitch"), JClass(PKG + "ProfilePage")
    Del, KeyFn, StateFn, Pub = JClass(PKG + "ProfDel"), JClass(PKG + "KeyFn"), JClass(PKG + "StateFn"), JClass(PKG + "CfgPub")
    Defs = JClass("com.skyy.classes.ClassDefs")
    UUID, Paths, Long = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    Uns = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    def player(u, name):
        pr = Uns.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", u)
        setf(pr, PRef, "username", name)
        return pr

    def jarr(*xs):
        a = JArray(JObject)(len(xs))
        for i, x in enumerate(xs):
            a[i] = x
        return a

    base = os.path.join(SCRATCH, "logic")
    mods = os.path.join(base, "mods")
    home = os.path.join(mods, "Skyy_SkyyProfiles")
    shutil.copytree(live_copy, home)
    # stand-ins for OTHER mods' per-profile files (SkyyProfiles must never touch them: they stay with the deleted / archived key)
    for rel, text in (("Skyy_SkyyBank/accounts/%s-p2.properties", "balance=12345\n"), ("Skyy_SkyyCoins/players/%s-p2.properties", "purse=777\n"),
                      ("Skyy_SkyySacks/pools/%s-p3.properties", "Ore_Iron=64\n"), ("Skyy_SkyyIslands/islands/%s-p2.properties", "world=x\n"),
                      ("Skyy_SkyyAuctions/claims/%s-p2.properties", "owed=1\n")):
        p = os.path.join(mods, rel % LIVE_UUID)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", newline="\n").write(text)
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    Store.DIR, Store.SWDIR = Paths.get(os.path.join(home, "players")), Paths.get(os.path.join(home, "switching"))
    Store.INVDIR, Store.LOGF = Paths.get(os.path.join(home, "inventories")), Paths.get(os.path.join(home, "switches.log"))
    Del.ARCDIR = Paths.get(os.path.join(home, "archive"))
    for d in ("players", "switching", "inventories"):
        os.makedirs(os.path.join(home, d), exist_ok=True)
    Cfg.load()
    check(int(Cfg.UNDO_MS) == UNDO_MS and str(Cfg.windowText()) == "6 hours", "G: the undo window is 6 h (%s)" % Cfg.windowText())
    bridge = Cfg.bridge()
    bridge.put("class:list", Defs.listText())
    Cfg.MAX_SETTING = "auto"
    U = UUID.fromString(LIVE_UUID)
    pr = player(U, "SkyLordPlayz")
    pf = os.path.join(home, "players", LIVE_UUID + ".properties")
    Store.DATA.clear()
    P0 = _props(pf)
    A = P0["active"]
    ids0 = sorted(set(k.split(".")[1] for k in P0 if re.match(r"p\.\d+\.name$", k)), key=int)
    inact = [i for i in ids0 if i != A]
    # the live copy must offer three inactive profiles; add made-up ones (empty, never played) if Skyy has fewer by now
    extra = 0
    while len(inact) < 3:
        nid = str(max(int(i) for i in ids0 + inact) + 1)
        Store.create(U, nid, "Extra%s" % nid, "Mage", False)
        inact.append(nid)
        extra += 1
    Store.DATA.clear()
    P0 = _props(pf)
    X, Y, Z = inact[0], inact[1], inact[2]
    NAME = dict((i, P0["p.%s.name" % i]) for i in ids0 + inact[len(inact) - extra:] if "p.%s.name" % i in P0)
    CLS = dict((i, P0.get("p.%s.class" % i, "")) for i in NAME)
    keyof = lambda i: LIVE_UUID if i == "1" else "%s-p%s" % (LIVE_UUID, i)
    entries = lambda pp, i: dict((k, v) for k, v in pp.items() if k.startswith("p.%s." % i))
    others0 = _tree(mods, skip_dirs=("Skyy_SkyyProfiles",))
    census0, slots0 = _inv_census(home)
    SHA0 = dict((i, _sha(os.path.join(home, "inventories", keyof(i) + ".json"))) for i in NAME
                if os.path.isfile(os.path.join(home, "inventories", keyof(i) + ".json")))
    key0, epoch0 = str(KeyFn().apply(U)), P0.get("epoch")
    print("G: live copy %s: active %s, inactive %s, %d inventory snapshots (%d saved slots)" % (LIVE_UUID, A, inact, len(census0), slots0))

    def key_ok(what):
        k = str(KeyFn().apply(U))
        check(k == key0, "G %s: profile:fn:key still the active profile's key (%s)" % (what, k))

    def items_ok(what):
        c, sl = _inv_census(home)
        check(sorted(c) == sorted(census0) and all(len(v) == 1 for v in c.values()) and sl == slots0,
              "G %s: every inventory snapshot exists exactly once, %d saved slots (no duplicate, none lost): %s" % (what, sl, c if sorted(c) != sorted(census0) else ""))
        check(_tree(mods, skip_dirs=("Skyy_SkyyProfiles",)) == others0, "G %s: other mods' files untouched" % what)

    # ---------------------------------------------------------------------------------------- G1 refusals
    raw0 = open(pf, "rb").read()
    r = str(Del.delete(U, "SkyLordPlayz", A))
    check(r == "You are playing %s right now - switch to another profile first and then delete it." % NAME[A], "G1 active refused: %s" % r)
    r = str(Del.cmdDelete(U, "SkyLordPlayz", NAME[A]))
    check(r.startswith("-You are playing %s right now" % NAME[A]), "G1 /profiles delete <active> refused: %s" % r)
    r = str(Del.cmdDelete(U, "SkyLordPlayz", "Nope"))
    check(r.startswith("-No profile 'Nope'"), "G1 unknown name: %s" % r)
    Store.BUSY.put(U, JClass("java.lang.Boolean").TRUE)
    r = str(Del.delete(U, "SkyLordPlayz", X))
    Store.BUSY.remove(U)
    check(r == BUSY_TEXT, "G1 during a switch / clean-up (the BUSY guard): %s" % r)
    mk = os.path.join(home, "switching", LIVE_UUID + ".properties")
    open(mk, "w", newline="\n").write("stage=failed\nfrom=%s\nto=%s\n" % (A, X))
    r = str(Del.delete(U, "SkyLordPlayz", X))
    os.remove(mk)
    check("needs an admin first" in r, "G1 a failed switch marker refuses it: %s" % r)
    check(open(pf, "rb").read() == raw0, "G1 the players file is byte for byte unchanged after every refusal")
    # the last profile: a player with one profile, and one with one live profile + a deleted one
    lp = {}
    for nm_, lines in (("one", ["active=1", "epoch=1", "p.1.name=Only", "p.1.class=Archer", "p.1.created=1", "p.1.lastPlayed=1"]),
                       ("onelive", ["active=1", "epoch=3", "p.1.name=Left", "p.1.class=Mage", "p.1.created=1", "p.1.lastPlayed=1",
                                    "p.2.name=Gone", "p.2.class=Priest", "p.2.created=1", "p.2.lastPlayed=1", "p.2.inv=1",
                                    "p.2.deleted=%d" % (int(time.time() * 1000)), "p.2.until=%d" % (int(time.time() * 1000) + UNDO_MS)])):
        u_ = UUID(0x9f0150, len(lp) + 1)
        f_ = os.path.join(home, "players", str(u_) + ".properties")
        open(f_, "w", newline="\n").write("\n".join(lines) + "\n")
        lp[nm_] = (u_, f_, open(f_, "rb").read())
    for nm_, (u_, f_, raw_) in lp.items():
        r = str(Del.delete(u_, "x", "1"))
        check(r.startswith("You are playing") and open(f_, "rb").read() == raw_, "G1 last profile (%s) refused: %s" % (nm_, r))
        pg = Page(player(u_, "x"), 0, False)
        pg.handleDataEvent(None, None, '{"a":"pfdel1"}')
        check(pg.delAsk is None and str(pg.info).startswith("You are playing") and open(f_, "rb").read() == raw_,
              "G1 last profile (%s): the page's Delete does not even ask (%s)" % (nm_, pg.info))
    r = str(Del.delete(lp["onelive"][0], "x", "2"))
    check(r == "Gone is already deleted - /profiles restore Gone brings it back.", "G1 a deleted profile is not deleted twice: %s" % r)

    # ---------------------------------------------------------------------------------------- G2 the confirm question
    page = Page(pr, 0, False)
    page.handleDataEvent(None, None, '{"a":"pfdel%s"}' % X)
    check(str(page.delAsk) == X and open(pf, "rb").read() == raw0, "G2 page: Delete only ASKS (delAsk %s, players file unchanged)" % page.delAsk)
    b, ev = UCB(), UEB()
    page.buildList(b, ev, U, Store.load(U))
    q = [str(c.data) for c in b.getCommands() if str(c.type.name()) == "Set" and str(c.selector) == "#SkyyPfDelQ.Text"]
    want_q = "Delete profile %s? Its island, coins, skills, bags and items will be gone. You have 6 hours to undo this." % NAME[X]
    check(len(q) == 1 and js(q[0]) == want_q, "G2 page: the confirm question %r" % (js(q[0]) if q else None))
    page.handleDataEvent(None, None, '{"a":"pfdelno"}')
    check(page.delAsk is None and open(pf, "rb").read() == raw0, "G2 page: Cancel - nothing deleted")
    page.handleDataEvent(None, None, '{"a":"pfdelyes"}')
    check(open(pf, "rb").read() == raw0, "G2 page: a stale Delete click (no question open) deletes nothing")
    page.handleDataEvent(None, None, '{"a":"pfdel%s"}' % X)
    t_before = int(time.time() * 1000)
    page.handleDataEvent(None, None, '{"a":"pfdelyes"}')
    t_after = int(time.time() * 1000)
    P1 = _props(pf)
    check("p.%s.deleted" % X in P1 and str(page.info) == "%s is deleted. Restore it within 6 hours - after that it is gone." % NAME[X],
          "G2 page: Delete -> deleted (%s)" % page.info)
    dx, ux = int(P1.get("p.%s.deleted" % X, 0)), int(P1.get("p.%s.until" % X, 0))
    check(t_before <= dx <= t_after and ux == dx + UNDO_MS, "G3 p.%s.deleted = now, until = deleted + 6 h exactly (%d / %d)" % (X, dx, ux))
    live0 = len([i for i in NAME if "p.%s.deleted" % i not in P0])
    check(P1.get("p.%s.slots" % X) == str(live0), "G3 p.%s.slots = the live count before the delete (%s, want %d)" % (X, P1.get("p.%s.slots" % X), live0))
    e0, e1 = entries(P0, X), entries(P1, X)
    for k_ in ("deleted", "until", "slots"):
        e1.pop("p.%s.%s" % (X, k_), None)
    check(e0 == e1 and dict((k, v) for k, v in P0.items() if not k.startswith("p.%s." % X)) ==
          dict((k, v) for k, v in P1.items() if not k.startswith("p.%s." % X)), "G3 a delete writes the three keys and nothing else")
    # the command: first run asks, the same again within 10 s deletes, a stale repeat asks again
    raw1 = open(pf, "rb").read()
    r1 = str(Del.cmdDelete(U, "SkyLordPlayz", NAME[Y]))
    want1 = ("=Delete profile %s%s? Its island, coins, skills, bags and items will be gone. You have 6 hours to undo this (/profiles restore %s)."
             " Type /profiles delete %s again within 10 s to confirm." % (NAME[Y], " (%s)" % CLS[Y] if CLS[Y] else "", NAME[Y], NAME[Y]))
    check(r1 == want1 and open(pf, "rb").read() == raw1, "G2 command: the first run asks (%s)" % r1)
    r2 = str(Del.cmdDelete(U, "SkyLordPlayz", Y))          # the same profile by number counts as the repeat
    check(r2 == "+Profile %s is deleted. /profiles restore %s brings it back within 6 hours - after that it is gone." % (NAME[Y], NAME[Y])
          and "p.%s.deleted" % Y in _props(pf), "G2 command: the repeat within 10 s deletes (%s)" % r2)
    check(_props(pf).get("p.%s.slots" % Y) == str(live0), "G3 the second delete keeps the first one's higher mark: p.%s.slots = %s (live %d -> %d)"
          % (Y, _props(pf).get("p.%s.slots" % Y), live0 - 1, live0 - 2))
    raw2 = open(pf, "rb").read()
    r3 = str(Del.cmdDelete(U, "SkyLordPlayz", NAME[Z]))
    Del.ASK.put("%s:%s" % (LIVE_UUID, Z), Long(int(time.time() * 1000) - 1))
    r4 = str(Del.cmdDelete(U, "SkyLordPlayz", NAME[Z]))
    check(r3.startswith("=Delete profile") and r4.startswith("=Delete profile") and open(pf, "rb").read() == raw2,
          "G2 command: a repeat after 10 s asks again (nothing deleted)")
    Del.ASK.clear()

    # ---------------------------------------------------------------------------------------- G3 what the others see
    key_ok("after two deletes")
    Store.publish(U)
    P2 = _props(pf)
    live2 = [i for i in sorted(set(k.split(".")[1] for k in P2 if re.match(r"p\.\d+\.name$", k)), key=int) if "p.%s.deleted" % i not in P2]
    check(P2.get("epoch") == epoch0 and str(bridge.get("profile:epoch:" + LIVE_UUID)) == epoch0, "G3 delete never bumps the epoch (%s)" % epoch0)
    want_list = ",".join("%s:%s:%s" % (i, P2["p.%s.name" % i], P2.get("p.%s.class" % i, "")) for i in live2)
    check(str(bridge.get("profile:list:" + LIVE_UUID)) == want_list and str(bridge.get("profile:key:" + LIVE_UUID)) == key0
          and str(bridge.get("profile:" + LIVE_UUID)) == A, "G3 profile:list lists live profiles only: %s" % bridge.get("profile:list:" + LIVE_UUID))
    sf = StateFn()
    for k, want in ((keyof(X), "pending"), (keyof(Y), "pending"), (keyof(A), "active"), (keyof(Z), "inactive"),
                    (LIVE_UUID + "-p63", None), ("junk", None), (LIVE_UUID + "-p02", None), (LIVE_UUID + "-p1", None)):
        got = sf.apply(k)
        check((None if got is None else str(got)) == want, "G3 profile:fn:state(%s) = %s (got %s)" % (k[-6:], want, got))
    check(sf.apply(U) is None and sf.apply(None) is None, "G3 profile:fn:state of a UUID (not a storage key) / null = null (%s)" % sf.apply(U))
    r = str(Sw.switchTo(None, None, pr, None, X))
    check(r == "%s is deleted - restore it first (/profiles restore %s)." % (NAME[X], NAME[X]), "G3 switching to a deleted profile is refused: %s" % r)
    check(str(Store.resolveId(U, NAME[X])) == X, "G3 /profiles switch <name> finds it (and switchTo refuses it)")
    d = str(Store.describe(U))
    check(("%s %s - %s - DELETED (restore within 5 h 59 min: /profiles restore %s)" % (X, NAME[X], CLS[X] or "no class", NAME[X])) in d
          and ("slots %d/5" % len(live2)) in d, "G3 /profiles list: %s" % d)
    items_ok("after two deletes")

    # ---------------------------------------------------------------------------------------- G4 a new profile while one is pending
    creates = 0
    r = str(Sw.createAndSwitch(None, None, pr, None, "Mage", "Kiwi"))
    P3 = _props(pf)
    nid = [i for i in set(k.split(".")[1] for k in P3 if re.match(r"p\.\d+\.name$", k)) if P3["p.%s.name" % i] == "Kiwi"]
    allids = sorted(set(int(k.split(".")[1]) for k in P0 if re.match(r"p\.\d+\.name$", k)))
    check(len(nid) == 1 and nid[0] not in (X, Y) and int(nid[0]) == max(allids) + 1 and P3["active"] == A
          and "profile slots are used" not in r, "G4 a new profile while two are pending: id %s (never a deleted id), still on %s (%s)" % (nid, A, r))
    N = nid[0]
    creates += 1
    NAME[N], CLS[N] = "Kiwi", "Mage"
    key_ok("after a create")
    u_gap = UUID(0x9f0150, 9)
    f_gap = os.path.join(home, "players", str(u_gap) + ".properties")
    open(f_gap, "w", newline="\n").write("active=1\np.1.name=A\np.1.class=Mage\np.2.name=B\np.2.class=Mage\np.2.deleted=5\np.2.until=9\ngone.3=7\ngone.3.dir=3-7\n")
    check(str(Store.nextId(Store.load(u_gap))) == "4", "G4 nextId skips a deleted id and an archived one (got %s)" % Store.nextId(Store.load(u_gap)))

    # ---------------------------------------------------------------------------------------- G5 restore within the window
    Store.BUSY.put(U, JClass("java.lang.Boolean").TRUE)
    r = str(Del.restore(U, "SkyLordPlayz", X))
    Store.BUSY.remove(U)
    check(r == BUSY_TEXT and "p.%s.deleted" % X in _props(pf), "G5 restore while the BUSY guard is held: %s" % r)
    check(Del.restore(U, "SkyLordPlayz", X) is None, "G5 restore %s within the window" % X)
    P4 = _props(pf)
    check(entries(P4, X) == entries(P0, X), "G5 %s is back exactly as it was (every p.%s.* key = before the delete)" % (X, X))
    page2 = Page(pr, 0, False)
    page2.handleDataEvent(None, None, '{"a":"pfres%s"}' % Y)
    check(str(page2.info) == "%s is back - exactly as it was." % NAME[Y] and entries(_props(pf), Y) == entries(P0, Y),
          "G5 page Restore: %s" % page2.info)
    items_ok("after restore")
    # over the limit: fixed 3, delete one, restore it -> above 3, allowed; a new profile refused
    Cfg.MAX_SETTING = "3"
    Del.cmdDelete(U, "SkyLordPlayz", X)
    Del.cmdDelete(U, "SkyLordPlayz", X)
    c_live = int(Store.count(Store.load(U)))
    r = str(Del.cmdRestore(U, "SkyLordPlayz", NAME[X]))
    c2 = int(Store.count(Store.load(U)))
    check(c2 == c_live + 1 > 3 and r == ("+Profile %s is back - exactly as it was. /profiles switch %s plays it. You now have %d profiles - more than the 3"
                                          " this server allows - so you cannot create another one." % (NAME[X], NAME[X], c2)),
          "G5 restore over the limit is allowed: %s" % r)
    r = str(Sw.createAndSwitch(None, None, pr, None, "Mage", "Lime"))
    check(r == "All 3 profile slots are used.", "G5 ... and a new profile is refused (%s)" % r)
    Cfg.MAX_SETTING = "auto"

    # ---------------------------------------------------------------------------------------- G5b the limit holds (review finding 1)
    # delete -> create -> restore used to grow past the limit (review: 9, 13, 17 ... 29 live profiles on a limit of 5); a player
    # restore now needs live < max(limit, p.<id>.slots). Synthetic players (not in the live copy), a fixed limit of 3.
    def synth(n_, names, extra=()):
        u_ = UUID(0x9f0150, n_)
        f_ = os.path.join(home, "players", str(u_) + ".properties")
        ls = ["active=1", "epoch=%d" % len(names), "username=Syn%d" % n_]
        for i_, nm_ in enumerate(names, 1):
            ls += ["p.%d.name=%s" % (i_, nm_), "p.%d.class=Mage" % i_, "p.%d.created=1" % i_, "p.%d.lastPlayed=1" % i_]
        open(f_, "w", newline="\n").write("\n".join(ls + list(extra)) + "\n")
        return u_, f_
    Cfg.MAX_SETTING = "3"
    u_l, f_l = synth(20, ["Apple", "Banana", "Cherry"])
    pr_l = player(u_l, "Syn20")
    L0 = _props(f_l)
    lcount = lambda: int(Store.count(Store.load(u_l)))
    check(Del.delete(u_l, "Syn20", "2") is None and _props(f_l).get("p.2.slots") == "3", "G5b a delete stores the live count before it: p.2.slots = %s"
          % _props(f_l).get("p.2.slots"))
    r = str(Sw.createAndSwitch(None, None, pr_l, None, "Mage", "Date"))
    check(lcount() == 3 and "profile slots are used" not in r and _props(f_l).get("p.4.name") == "Date",
          "G5b the freed slot takes a new profile (id 4, 3 live): %s" % r)
    want_full = "No free slot for Banana - you have 3 profiles and the limit is 3. Delete another profile first."
    raw_l = open(f_l, "rb").read()
    r = Del.restore(u_l, "Syn20", "2")
    check(str(r) == want_full and open(f_l, "rb").read() == raw_l, "G5b ... then Banana cannot come back on top of the limit: %s" % r)
    r = str(Del.cmdRestore(u_l, "Syn20", "Banana"))
    check(r == "-" + want_full, "G5b /profiles restore says the same: %s" % r)
    pg = Page(pr_l, 0, False)
    pg.handleDataEvent(None, None, '{"a":"pfres2"}')
    check(str(pg.info) == want_full and open(f_l, "rb").read() == raw_l, "G5b the page's Restore says the same: %s" % pg.info)
    check(Del.delete(u_l, "Syn20", "4") is None and Del.restore(u_l, "Syn20", "2") is None and lcount() == 3
          and entries(_props(f_l), "2") == entries(L0, "2"), "G5b deleting the new profile frees the slot: Banana is back exactly as it was")
    check(str(Del.restore(u_l, "Syn20", "4")) == want_full.replace("Banana", "Date"), "G5b ... and now Date cannot come back on top")
    tops, rounds_ok = [], True
    for rnd in range(6):          # the review's loop: delete every non-active profile, create up to the limit, restore every deleted one
        Pl = Store.load(u_l)
        for i_ in range(1, MAX_ID + 1):
            if bool(Store.live(Pl, str(i_))) and str(i_) != str(Store.activeOf(Pl)):
                rounds_ok = rounds_ok and Del.delete(u_l, "Syn20", str(i_)) is None
        for _k in range(4):
            if "profile slots are used" in str(Sw.createAndSwitch(None, None, pr_l, None, "Mage", None)):
                break
        Pl = Store.load(u_l)
        for i_ in range(1, MAX_ID + 1):
            if bool(Store.isDel(Pl, str(i_))):
                Del.restore(u_l, "Syn20", str(i_))
        tops.append(lcount())
    check(rounds_ok and tops == [3] * 6, "G5b the review's delete / create / restore loop, 6 rounds: live profiles %s (the limit is 3)" % tops)
    # a LOWERED limit: 5 profiles on a limit of 3 - two deleted come back, in either order (the second delete keeps the mark 5)
    u_w5, f_w5 = synth(21, ["Apple", "Banana", "Cherry", "Date", "Elder"])
    check(Del.delete(u_w5, "Syn21", "2") is None and Del.delete(u_w5, "Syn21", "3") is None and _props(f_w5).get("p.3.slots") == "5"
          and Del.restore(u_w5, "Syn21", "2") is None and Del.restore(u_w5, "Syn21", "3") is None and int(Store.count(Store.load(u_w5))) == 5,
          "G5b a lowered limit: 5 profiles on a limit of 3, delete two, restore both (first-deleted first) -> 5 live")
    r = str(Sw.createAndSwitch(None, None, player(u_w5, "Syn21"), None, "Mage", "Fig"))
    check(r == "All 3 profile slots are used.", "G5b ... and still no new profile (%s)" % r)
    for u_ in (u_l, u_w5):
        Del.INDEX.remove(u_)       # their remaining deleted profiles must not reach the G6 sweeps (other players' tests)
    Cfg.MAX_SETTING = "auto"

    # ---------------------------------------------------------------------------------------- G6 expiry (simulated clock)
    inv_x = os.path.join(home, "inventories", keyof(X) + ".json")
    had_x = os.path.isfile(inv_x)
    sha_x = _sha(inv_x) if had_x else None
    check(Del.delete(U, "SkyLordPlayz", X) is None, "G6 delete %s again" % X)
    px = _props(pf)
    ux = int(px["p.%s.until" % X])
    check(int(Del.expireDue(ux - 1)) == 0 and "p.%s.deleted" % X in _props(pf), "G6 one ms before the deadline: still pending")
    check(int(Del.expireDue(ux)) == 1, "G6 at the deadline: archived")
    P5 = _props(pf)
    adir = os.path.join(home, "archive", LIVE_UUID, "%s-%d" % (X, ux))
    rec = _props(os.path.join(adir, "profile.properties"))
    check(not entries(P5, X) and P5.get("gone.%s" % X) == str(ux) and P5.get("gone.%s.dir" % X) == "%s-%d" % (X, ux),
          "G6 the players file: no p.%s.* left, tombstone gone.%s" % (X, X))
    want_rec = dict(entries(P0, X))
    want_rec.update({"p.%s.deleted" % X: px["p.%s.deleted" % X], "p.%s.until" % X: str(ux), "p.%s.slots" % X: px["p.%s.slots" % X]})
    check(entries(rec, X) == want_rec and rec.get("archive.id") == X and rec.get("archive.key") == keyof(X) and rec.get("archive.version") == VERSION
          and rec.get("archive.inventory") == ("inventory.json" if had_x else "none"), "G6 the archive record holds the profile's entries: %s" % sorted(rec))
    check((not had_x) or (not os.path.exists(inv_x) and _sha(os.path.join(adir, "inventory.json")) == sha_x),
          "G6 inventories/%s.json MOVED into the archive (same bytes), not deleted" % keyof(X))
    items_ok("after the archive")
    check(Store.resolveId(U, NAME[X]) is None and str(Del.restore(U, "SkyLordPlayz", X)) == "You have no such profile. /profiles list shows yours."
          and str(sf.apply(keyof(X))) == "archived", "G6 an archived profile is gone for the player; profile:fn:state = archived")
    key_ok("after the archive")
    # a late Restore (deadline passed, the sweep has not run yet) is refused and archives it at once
    check(Del.delete(U, "SkyLordPlayz", Y) is None, "G6 delete %s" % Y)
    qy = Store.load(U).clone()
    qy.setProperty("p.%s.until" % Y, str(int(time.time() * 1000) - 1000))
    check(bool(Store.commit(U, qy)), "G6 (test) the deadline of %s moved into the past" % Y)
    r = str(Del.restore(U, "SkyLordPlayz", Y))
    check(r == "Too late - the undo time of %s is over. Only an admin can bring it back now." % NAME[Y] and "gone.%s" % Y in _props(pf),
          "G6 a late Restore: %s (archived at once)" % r)
    # a FAILED switch marker that names the key keeps the profile pending
    en_before = entries(_props(pf), N)
    check(Del.delete(U, "SkyLordPlayz", N) is None, "G6 delete %s (never played: no inventory file)" % N)
    open(mk, "w", newline="\n").write("stage=failed\nfrom=%s\nto=%s\nfromKey=%s\ntoKey=%s\n" % (A, N, keyof(A), keyof(N)))
    far = int(time.time() * 1000) + 10 * DAY
    check(int(Del.expireDue(far)) == 0 and "p.%s.deleted" % N in _props(pf) and bool(Del.MARKER_WARNED.get()),
          "G6 a failed switch marker naming its key keeps it pending (one WARN)")
    # review finding 3: past its deadline but kept pending by the marker - the player cannot restore it, the card / list / login line
    # stop offering it, the admin restore brings it back (the deadline does not apply to an admin)
    qn = Store.load(U).clone()
    qn.setProperty("p.%s.until" % N, str(int(time.time() * 1000) - 1000))
    check(bool(Store.commit(U, qn)), "G6 (test) the deadline of %s moved into the past" % N)
    r = str(Del.restore(U, "SkyLordPlayz", N))
    Pn = _props(pf)
    check(r == "Too late - the undo time of %s is over. Only an admin can bring it back now." % NAME[N] and "p.%s.deleted" % N in Pn
          and "gone.%s" % N not in Pn, "G6 overdue + failed marker: the late Restore is refused and it stays pending (%s)" % r)
    d = str(Store.describe(U))
    check(("%s %s - %s - DELETED (the undo time is over - only an admin can bring it back)" % (N, NAME[N], CLS[N])) in d, "G6 /profiles list: %s" % d)
    check(Del.pendingNote(Store.load(U)) is None, "G6 the login line does not offer an overdue profile (%s)" % Del.pendingNote(Store.load(U)))
    lines = [str(x) for x in Del.archiveText(U)]
    check(lines[0].startswith("SkyLordPlayz: 0 deleted profile(s) in their undo window, 1 past it (not archived yet), 2 archived")
          and any(x.startswith("  %s %s (" % (N, NAME[N])) and "undo window ENDED" in x and "/profileadmin archive restore can" in x for x in lines),
          "G6 /profileadmin archive list names the overdue profile:\n    " + "\n    ".join(lines))
    r = str(Del.adminRestore(U, NAME[N], "Admin"))
    check(r == "+Restored %s - its undo window had ended but it was not archived yet. It is not active - the player switches to it in /profiles." % NAME[N]
          and entries(_props(pf), N) == en_before, "G6 the admin restores the overdue profile, exactly as it was: %s" % r)
    os.remove(mk)
    check(Del.delete(U, "SkyLordPlayz", N) is None, "G6 delete %s again (the marker is gone)" % N)
    check(int(Del.expireDue(far)) == 1 and "gone.%s" % N in _props(pf), "G6 ... archived at the end of its window")
    recs = [d_ for d_ in os.listdir(os.path.join(home, "archive", LIVE_UUID)) if d_.startswith(N + "-")]
    check(len(recs) == 1 and _props(os.path.join(home, "archive", LIVE_UUID, recs[0], "profile.properties")).get("archive.inventory") == "none",
          "G6 a never-played profile is archived without an inventory")
    # ---------------------------------------------------------------------------------------- G6b archive write failures (review finding 6)
    # the players file cannot be saved (its .tmp name is taken by a folder) AFTER the record was written into the fresh archive folder:
    # the attempt removes its record + folder again and warns once per profile (it used to leave one folder + one WARN per minute)
    T = int(time.time() * 1000) - HOUR
    u_f, f_f = synth(22, ["Apple", "Pear"], ["p.2.deleted=%d" % (T - UNDO_MS), "p.2.until=%d" % T, "p.2.slots=2"])
    raw_f = open(f_f, "rb").read()
    Del.reindex(u_f)
    fdir = os.path.join(home, "archive", str(u_f))
    w0 = int(Del.ARC_WARNS.get())
    block_ = f_f + ".tmp"
    os.makedirs(block_)
    for k_ in (1, 2):                                   # two sweeps (a different folder name each time, like a minute apart)
        n_ = int(Del.expireDue(T + k_))
        check(n_ == 0 and open(f_f, "rb").read() == raw_f and not os.path.exists(os.path.join(fdir, "2-%d" % (T + k_))),
              "G6b the players file cannot be saved (sweep %d): still pending (file unchanged), the fresh archive folder removed again" % k_)
    check(int(Del.ARC_WARNS.get()) == w0 + 1 and bool(Del.ARC_WARNED.containsKey("%s:2" % u_f)),
          "G6b ... one WARN for both failures (%d)" % (int(Del.ARC_WARNS.get()) - w0))
    os.rmdir(block_)
    # cleanDir removes only what an attempt writes (the record, its .tmp, the then empty folder)
    for nm_, files_ in (("ours", ["profile.properties", "profile.properties.tmp"]), ("mixed", ["profile.properties", "other.txt"])):
        d_ = os.path.join(SCRATCH, "cleandir", nm_)
        os.makedirs(d_)
        for f_ in files_:
            open(os.path.join(d_, f_), "w").write("x\n")
        Del.cleanDir(Paths.get(d_))
    check(not os.path.exists(os.path.join(SCRATCH, "cleandir", "ours")) and os.listdir(os.path.join(SCRATCH, "cleandir", "mixed")) == ["other.txt"],
          "G6b cleanDir: its own files + the empty folder go, a folder with anything else keeps that")
    os.makedirs(os.path.join(fdir, "2-%d" % (T + 3)))
    open(os.path.join(fdir, "2-%d" % (T + 3), "keep.txt"), "w", newline="\n").write("not ours\n")
    check(int(Del.expireDue(T + 3)) == 0 and open(os.path.join(fdir, "2-%d" % (T + 3), "keep.txt")).read() == "not ours\n"
          and sorted(os.listdir(os.path.join(fdir, "2-%d" % (T + 3)))) == ["keep.txt"] and "p.2.deleted" in _props(f_f),
          "G6b an archive folder of that name that already exists is left alone (still pending)")
    check(int(Del.expireDue(T + 4)) == 1 and "gone.2" in _props(f_f) and os.path.isfile(os.path.join(fdir, "2-%d" % (T + 4), "profile.properties"))
          and not bool(Del.ARC_WARNED.containsKey("%s:2" % u_f)) and int(Del.ARC_WARNS.get()) == w0 + 1
          and sorted(os.listdir(fdir)) == sorted(["2-%d" % (T + 3), "2-%d" % (T + 4)]) and not bool(Del.INDEX.containsKey(u_f)),
          "G6b ... the next sweep archives it, the warning resets: %s" % sorted(os.listdir(fdir)))
    items_ok("after three archives")
    key_ok("after three archives")

    # ---------------------------------------------------------------------------------------- G7 the admin archive
    lines = [str(x) for x in Del.archiveText(U)]
    check(lines[0].startswith("SkyLordPlayz: 0 deleted profile(s) in their undo window, 3 archived") and
          sum(1 for x in lines if NAME[X] in x and "folder %s-" % X in x) == 1 and any("Kiwi" in x and "no inventory (never played)" in x for x in lines),
          "G7 /profileadmin archive list:\n    " + "\n    ".join(lines))
    # a name taken meanwhile: a new profile takes the archived Y's name, then the admin restores Y -> Y gets a new fruit name
    r = str(Sw.createAndSwitch(None, None, pr, None, "Priest", NAME[Y]))
    P6 = _props(pf)
    taken = [i for i in set(k.split(".")[1] for k in P6 if re.match(r"p\.\d+\.name$", k)) if P6["p.%s.name" % i] == NAME[Y]]
    check(len(taken) == 1 and taken[0] != Y, "G7 a new profile took the archived name %s (id %s)" % (NAME[Y], taken))
    creates += len(taken)
    inv_y = os.path.join(home, "inventories", keyof(Y) + ".json")
    r = str(Del.adminRestore(U, NAME[Y], "Admin"))
    P7 = _props(pf)
    ny = P7.get("p.%s.name" % Y)
    check(r.startswith("+Restored profile %s (it was called %s - another profile has that name now) (number %s)." % (ny, NAME[Y], Y))
          and ny != NAME[Y] and "gone.%s" % Y not in P7 and "p.%s.deleted" % Y not in P7, "G7 admin restore of a renamed name: %s" % r)
    ey = dict(entries(P0, Y))
    ey["p.%s.name" % Y] = ny
    check(entries(P7, Y) == ey, "G7 ... every other p.%s.* key as it was before the delete" % Y)
    check((Y not in SHA0 and not os.path.isfile(inv_y)) or (Y in SHA0 and os.path.isfile(inv_y) and _sha(inv_y) == SHA0[Y]),
          "G7 ... its inventory is back in inventories/ (same bytes)")
    check(any(d_.startswith(Y + "-") and d_.endswith("-restored") for d_ in os.listdir(os.path.join(home, "archive", LIVE_UUID))),
          "G7 ... its archive folder is renamed <folder>-restored (history, never deleted)")
    r = str(Del.adminRestore(U, X, "Admin"))
    check(r.startswith("+Restored profile %s (number %s)." % (NAME[X], X)) and entries(_props(pf), X) == entries(P0, X)
          and ((X not in SHA0) or _sha(inv_x) == SHA0[X]), "G7 admin restore by number: %s (inventory back, same bytes)" % r)
    check(Del.delete(U, "SkyLordPlayz", Z) is None, "G7 delete %s" % Z)
    r = str(Del.adminRestore(U, NAME[Z], "Admin"))
    check(r.startswith("+Restored %s - it was still in its undo window." % NAME[Z]) and entries(_props(pf), Z) == entries(P0, Z),
          "G7 admin restore of a profile still in its window: %s" % r)
    r = str(Del.adminRestore(U, "Nope", "Admin"))
    check(r.startswith("-No deleted or archived profile 'Nope'"), "G7 admin restore of an unknown name: %s" % r)
    items_ok("after the admin restores")
    key_ok("after the admin restores")
    Pf = _props(pf)
    check(all(entries(Pf, i) == entries(P0, i) for i in ids0 if i not in (Y,)) and Pf["active"] == A and int(Pf.get("epoch")) == int(epoch0) + creates,
          "G every original profile is live again with its original entries (%s renamed); the epoch rose only for the %d creates (%s -> %s)"
          % (Y, creates, epoch0, Pf.get("epoch")))

    # ---------------------------------------------------------------------------------------- G8 the config kit row
    Pub.start(Paths.get(mods), None)
    fn = bridge.get("config:fn:SkyyProfiles")
    hdr = bridge.get("config:def:SkyyProfiles")
    rows = [[str(x) for x in row] for row in hdr[7]]
    urow = [r_ for r_ in rows if r_[0] == "deleteUndoHours"]
    check(len(urow) == 1 and urow[0][1:10] == ["Undo window after deleting a profile", "profiles", "int", "6", "1", "168", "step=1", "h", "live"],
          "G8 the Server Setup row deleteUndoHours: %s" % urow)
    for typed, status, want in (("12", "ok", 12), ("0", "bad", 12), ("169", "bad", 12), ("6", "ok", 6)):
        r_ = fn.apply(jarr("set", "deleteUndoHours", typed, None, None, "yes", "console"))
        check(r_ is not None and str(r_[0]) == status and int(Cfg.UNDO_MS) == want * HOUR, "G8 set deleteUndoHours %s -> %s (%s h)" % (typed, status, int(Cfg.UNDO_MS) // HOUR))
    Pub.flush()
    time.sleep(0.4)
    Pub.flush()
    t = open(os.path.join(home, "config.properties"), encoding="utf8").read()
    check(len(re.findall(r"(?m)^deleteUndoHours=6$", t)) == 1, "G8 the kit wrote deleteUndoHours=6 into config.properties")
    Pub.shutdown()

    # ---------------------------------------------------------------------------------------- prepare part R (a fresh JVM reads these)
    rhome = os.path.join(SCRATCH, "restart", "mods", "Skyy_SkyyProfiles")
    for d in ("players", "inventories", "switching"):
        os.makedirs(os.path.join(rhome, d), exist_ok=True)
    now = int(time.time() * 1000)
    src_inv = [os.path.join(home, "inventories", f) for f in os.listdir(os.path.join(home, "inventories")) if f.endswith(".json")]
    plan = {"t0": now}
    for tag, n_, lines in (("Y", 1, ["active=1", "epoch=2", "username=Ypp", "p.1.name=Apple", "p.1.class=Mage", "p.2.name=Pear", "p.2.class=Archer",
                                      "p.2.inv=1", "p.2.deleted=%d" % now, "p.2.until=%d" % (now + UNDO_MS)]),
                           ("Z", 2, ["active=1", "epoch=2", "username=Zpp", "p.1.name=Apple", "p.1.class=Mage", "p.2.name=Plum", "p.2.class=Priest",
                                     "p.2.inv=1", "p.2.deleted=%d" % (now - 7 * HOUR), "p.2.until=%d" % (now - HOUR)]),
                           ("Q", 3, ["active=1", "epoch=4", "username=Qpp", "p.1.name=Lime", "p.1.class=Mage", "p.1.inv=1", "p.1.deleted=%d" % (now - 2 * HOUR),
                                     "p.1.until=%d" % (now + 10 * HOUR), "p.2.name=Fig", "p.2.class=Archer", "p.2.inv=1",
                                     "p.2.deleted=%d" % (now - HOUR), "p.2.until=%d" % (now + 10 * HOUR)])):
        u_ = UUID(0x9f015, 100 + n_)
        open(os.path.join(rhome, "players", str(u_) + ".properties"), "w", newline="\n").write("\n".join(lines) + "\n")
        for pid in ("1", "2"):
            if "p.%s.inv=1" % pid in lines:
                shutil.copyfile(src_inv[0], os.path.join(rhome, "inventories", (str(u_) if pid == "1" else "%s-p%s" % (u_, pid)) + ".json"))
        plan[tag] = str(u_)
    json.dump(plan, open(os.path.join(SCRATCH, "restart", "plan.json"), "w"))
    print("G. delete / restore / archive: %d checks so far" % OKS[0])
    print("logic child: %d checks passed, %d failed" % (OKS[0], len(FAILS)))
    sys.exit(1 if FAILS else 0)


# ============================================================================================ child: part R (restart keeps the timer)
def run_restart(jar):
    from jpype import JClass
    _jvm_start([jar])
    Cfg, Store, Del, Join = JClass(PKG + "ProfCfg"), JClass(PKG + "ProfStore"), JClass(PKG + "ProfDel"), JClass(PKG + "ProfJoin")
    KeyFn = JClass(PKG + "KeyFn")
    UUID, Paths = JClass("java.util.UUID"), JClass("java.nio.file.Paths")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    Uns = uf.get(None)

    def player(u, name):
        pr = Uns.allocateInstance(PRef.class_)
        for fld, val in (("uuid", u), ("username", name)):
            f = PRef.class_.getDeclaredField(fld)
            f.setAccessible(True)
            f.set(pr, val)
        return pr

    plan = json.load(open(os.path.join(SCRATCH, "restart", "plan.json")))
    rhome = os.path.join(SCRATCH, "restart", "mods", "Skyy_SkyyProfiles")
    Cfg.FILE = Paths.get(os.path.join(rhome, "config.properties"))
    Store.DIR, Store.SWDIR = Paths.get(os.path.join(rhome, "players")), Paths.get(os.path.join(rhome, "switching"))
    Store.INVDIR, Store.LOGF = Paths.get(os.path.join(rhome, "inventories")), Paths.get(os.path.join(rhome, "switches.log"))
    Del.ARCDIR = Paths.get(os.path.join(rhome, "archive"))
    Cfg.load()
    yu, zu, qu = UUID.fromString(plan["Y"]), UUID.fromString(plan["Z"]), UUID.fromString(plan["Q"])
    t0 = int(plan["t0"])
    check(int(Del.scanIndex()) == 3 and all(bool(Del.INDEX.containsKey(u)) for u in (yu, zu, qu)), "R: a fresh JVM finds the 3 players with a waiting deletion")
    now = int(time.time() * 1000)
    d = str(Store.describe(yu))
    lefts = set(fmt_left(t0 + UNDO_MS - x) for x in (now - 2000, now, now + 2000))
    check(any(("2 Pear - Archer - DELETED (restore within %s: /profiles restore Pear)" % l_) in d for l_ in lefts),
          "R: the time left comes from the stored deadline: %s" % d)
    # the join path: Z's window ended while the server was down -> archived at join; Q has only deleted profiles -> the newest back
    zinv = os.path.join(rhome, "inventories", plan["Z"] + "-p2.json")
    zsha = _sha(zinv)
    Join.prepare(player(zu, "Zpp"))
    pz = _props(os.path.join(rhome, "players", plan["Z"] + ".properties"))
    zdirs = os.listdir(os.path.join(rhome, "archive", plan["Z"])) if os.path.isdir(os.path.join(rhome, "archive", plan["Z"])) else []
    check("gone.2" in pz and not os.path.exists(zinv) and len(zdirs) == 1 and _sha(os.path.join(rhome, "archive", plan["Z"], zdirs[0], "inventory.json")) == zsha,
          "R: at join an ended window is archived (inventory moved, same bytes)")
    Join.prepare(player(qu, "Qpp"))
    pq = _props(os.path.join(rhome, "players", plan["Q"] + ".properties"))
    check("p.2.deleted" not in pq and "p.1.deleted" in pq and pq.get("active") == "2" and str(KeyFn().apply(qu)) == plan["Q"] + "-p2",
          "R: only deleted profiles left (hand edit) -> the newest (2) is back and active; the key is never a deleted one's (%s)" % KeyFn().apply(qu))
    ypf = os.path.join(rhome, "players", plan["Y"] + ".properties")
    yraw = open(ypf, "rb").read()
    check(int(Del.expireDue(t0 + 5 * HOUR)) == 0 and open(ypf, "rb").read() == yraw, "R: simulated clock +5 h: nothing archived (Y has an hour left)")
    yinv = os.path.join(rhome, "inventories", plan["Y"] + "-p2.json")
    ysha = _sha(yinv)
    check(int(Del.expireDue(t0 + UNDO_MS)) == 1, "R: simulated clock +6 h (the stored deadline): Y archived")
    py = _props(ypf)
    ydirs = os.listdir(os.path.join(rhome, "archive", plan["Y"]))
    check("gone.2" in py and not os.path.exists(yinv) and len(ydirs) == 1 and ydirs[0] == "2-%d" % (t0 + UNDO_MS)
          and _sha(os.path.join(rhome, "archive", plan["Y"], ydirs[0], "inventory.json")) == ysha, "R: ... its inventory moved, never deleted")
    check(int(Del.expireDue(t0 + 11 * HOUR)) == 1 and "gone.1" in _props(os.path.join(rhome, "players", plan["Q"] + ".properties"))
          and not bool(Del.INDEX.containsKey(qu)) and not bool(Del.INDEX.containsKey(yu)), "R: Q's other deleted profile at its own deadline; the index empties")
    print("R. restart: %d checks" % OKS[0])
    sys.exit(1 if FAILS else 0)


# ============================================================================================ child: part S (one server start)
def run_start(jar, home, out):
    from jpype import JClass
    _jvm_start([jar])
    Cfg, Store, Del, Pub, KeyFn = JClass(PKG + "ProfCfg"), JClass(PKG + "ProfStore"), JClass(PKG + "ProfDel"), JClass(PKG + "CfgPub"), JClass(PKG + "KeyFn")
    UUID, Paths, Files = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.nio.file.Files")
    Attr = JClass("java.nio.file.attribute.FileAttribute")
    from jpype import JArray
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    Store.DIR, Store.SWDIR = Paths.get(os.path.join(home, "players")), Paths.get(os.path.join(home, "switching"))
    Store.INVDIR, Store.LOGF = Paths.get(os.path.join(home, "inventories")), Paths.get(os.path.join(home, "switches.log"))
    Del.ARCDIR = Paths.get(os.path.join(home, "archive"))
    # SkyyProfilesPlugin.setup() order
    up = Cfg.upgradeDefault()
    capm = Cfg.capMigrate()
    summary = str(Cfg.load())
    for d in (Store.DIR, Store.SWDIR, Store.INVDIR):
        Files.createDirectories(d, JArray(Attr)(0))
    waiting = int(Del.scanIndex())
    Cfg.bridge().put("profile:fn:key", KeyFn())
    Pub.start(Paths.get(os.path.dirname(home)), None)
    archived = int(Del.expireDue(int(time.time() * 1000)))      # the first sweep
    Pub.flush()
    time.sleep(0.4)
    Pub.flush()
    u = UUID.fromString(LIVE_UUID)
    res = {"up": None if up is None else str(up), "capm": None if capm is None else str(capm), "summary": summary, "waiting": waiting,
           "archived": archived, "describe": str(Store.describe(u)), "key": str(KeyFn().apply(u)), "undo": int(Cfg.UNDO_MS)}
    Pub.shutdown()
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


# ============================================================================================ 0.1.5: the markup of one state (part D)
def markup_checks(name, new, SUI, counts, data_colors):
    """D for one 0.1.5 state (the 0.1.4 compare_state's D half): returns (root, ids, sets, nodes by id with their markup)."""
    check(new["error"] is None, "%s: the page built (%s)" % (name, new["error"]))
    if new["error"]:
        return None
    ap = SUI.Appends()
    allowed = SUI.allowed_colors() | set(SUI.norm_color(c) for c in data_colors)
    size = 0
    raw = {}
    for idx, (t, sel, data, text) in enumerate(new["commands"]):
        if t == "AppendInline":
            parent = None if sel is None else sel.lstrip("#")
            check(idx != 0 or parent is None, "%s: the first append is the page root" % name)
            try:
                SUI.check_markup(text, prefix=PREFIX, root=(parent is None))
            except ValueError as e:
                check(False, "%s: check_markup: %s" % (name, e))
            ap.append((parent, text))
            size += len(text)
            for i in _ID_RE.findall(text):
                raw.setdefault(i, text)
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
        SUI.check_page(ap, PREFIX)
        counts["check_page"] += 1
    except ValueError as e:
        check(False, "%s: check_page: %s" % (name, e))
    counts["appends"] += len(ap)
    root, ids = build_tree(ap)
    a0 = _pairs(root["props"].get("Anchor"))
    check((a0.get("Width"), a0.get("Height")) == (PAGE_W, PAGE_H), "%s: page root %s x %s" % (name, a0.get("Width"), a0.get("Height")))
    for e in new["events"]:
        check(e[1] and e[1].lstrip("#") in ids, "%s: binding target %s exists" % (name, e[1]))
    issues = []
    order = layout(root, issues)
    check(not issues, "%s: layout: %s" % (name, issues[:4]))
    counts["placed"] += len(order)
    tot, inner = body_fill(ids, BODY_ID)
    check(inner == BODY_INNER_H and tot == BODY_INNER_H, "%s: the body children fill %d px exactly (got %d of %d)" % (name, BODY_INNER_H, tot, inner))
    for nd in order:
        if nd["props"].get("LayoutMode") == "Left" and nd["kids"]:
            counts["min_row_slack"] = min(counts["min_row_slack"], nd["inner"][2] - nd["used"])
    sets = dict((i, v) for i, p, v in ap.sets if p == "Text")
    check_texts(name, order, sets, counts)
    check_contrast(name, root, counts)
    counts["states"] += 1
    return root, ids, sets, raw


def ev_a(e):
    try:
        return json.loads(e[2]).get("a")
    except Exception:
        return None


def expect_list(st, built):
    """What the 0.1.5 list view must show for one state: the card ids (in order), each card's role, whether Create new shows, the
    bindings ("a" values in order), the bottom row (switch / delete / foot) and its text."""
    nm, view, first, _p, _a, pending, pick_name, pick_class, info, mx, clist, kits, rank, _d, ask = st
    profs, act = built["profiles"], built["active"]
    dels = built["deleted"]
    names = dict((p[0], p[1]) for p in profs)
    ordered = sorted(names, key=int)
    live = [i for i in ordered if i not in dels]
    dl = [i for i in ordered if i in dels]
    n, cap = len(live), expected_cap(mx, clist, rank)
    shown = live[:CAP_MAX]
    for i in dl:
        if len(shown) < CAP_MAX:
            shown.append(i)
    room = n < cap and len(shown) < CAP_MAX
    evs, roles = [], {}
    for i in shown:
        on, d, pend = i == act, i in dels, i == pending
        over = d and dels[i] <= 0          # past its deadline, not archived yet: Expired, no Restore (review finding 3)
        can = (not on) and (not d) and (not pend) and act is not None and n > 1
        roles[i] = "active" if on else ("expired" if over else ("deleted" if d else ("switch" if not can else "swdel")))
        if on or over:
            pass
        elif d:
            evs.append("pfres" + i)
        elif not can:
            evs.append("pfsw" + i)
        else:
            evs += ["pfsw" + i, "pfdel" + i]
    if room:
        evs.append("pfnew")
    if pending and pending in live and pending != act:
        evs += ["pfyes", "pfno"]
        mode, text = "switch", None
    elif ask and ask in live and ask != act:
        evs += ["pfdelyes", "pfdelno"]
        mode = "delete"
        text = "Delete profile %s? Its island, coins, skills, bags and items will be gone. You have 6 hours to undo this." % safe(names[ask])
    else:
        evs.append("pfclose")
        mode = "foot"
        why = expected_why(mx, clist, rank)
        used = ("%d of %d profile slots used (%s)." % (n, cap, why)) if n <= cap else \
            ("%d profiles - this server now allows %d. You keep them all but cannot create more." % (n, cap))
        foot = used + FOOT_TAIL
        live_sh, del_sh = len([i for i in shown if i not in dels]), len([i for i in shown if i in dels])
        if dl:
            foot += " A deleted profile does not use a slot."
        if n > live_sh:
            foot += " %d more profiles - /profiles list shows them." % (n - live_sh)
        if len(dl) > del_sh:
            foot += " %d more deleted - /profiles list shows them." % (len(dl) - del_sh)
        if n < cap and not room:
            foot += " New profile - /profiles create."
        text = safe(foot)
    return {"shown": shown, "roles": roles, "room": room, "events": evs, "mode": mode, "text": text, "dels": dels, "names": names, "act": act,
            "pending": pending, "ask": ask}


def check_list_015(nm, st, built, got, SUI):
    """D (0.1.5 rules) for one list state: bindings, cards, looks, buttons, the bottom row, word for word."""
    root, ids, sets, raw = got
    ex = expect_list(st, built)
    check([ev_a(e) for e in built["events"]] == ex["events"], "D %s: bindings %s (want %s)" % (nm, [ev_a(e) for e in built["events"]], ex["events"]))
    cards = [i[len("SkyyPfCard"):] for i in ids if re.fullmatch(r"SkyyPfCard\d+", i)]
    check(cards == ex["shown"] and (("SkyyPfNewCard" in ids) == ex["room"]) and len(cards) + int(ex["room"]) <= CAP_MAX,
          "D %s: cards %s + Create new %s (want %s + %s)" % (nm, cards, "SkyyPfNewCard" in ids, ex["shown"], ex["room"]))
    looks = {"active": SUI.COLOR["rowPressed"], "question": SUI.COLOR["rowHover"], "deleted": SUI.COLOR["cardDisabled"], "normal": SUI.COLOR["row"]}
    for i in ex["shown"]:
        role = ex["roles"][i]
        inner = ids.get("SkyyPfCard%sIn" % i)
        look = "active" if role == "active" else ("question" if i in (ex["pending"], ex["ask"]) else
                                                  ("deleted" if role in ("deleted", "expired") else "normal"))
        bg = inner["props"].get("Background", "") if inner else ""
        check(SUI.norm_color(bg) == SUI.norm_color(looks[look]), "D %s: card %s look %s (background %s)" % (nm, i, look, bg))
        has = lambda k: ("SkyyPf%s%s" % (k, i)) in ids
        nm_text = sets.get("SkyyPfCard%sNm" % i, "")
        if role == "expired":
            acts = [c[3] for c in built["commands"] if c[0] == "AppendInline" and c[1] == "#SkyyPfAct%s" % i]
            check(not has("Res") and not has("Sw") and not has("Del") and len(acts) == 1 and '"Expired"' in acts[0]
                  and SUI.COLOR["disabled"].lower() in acts[0].lower(), "D %s: overdue card %s = the state word Expired (disabled grey), no Restore: %s"
                  % (nm, i, acts))
            check(sets.get("SkyyPfCard%sL3" % i) == EXPIRED_L3 and nm_text == safe(ex["names"][i] + " - DELETED"),
                  "D %s: overdue card %s texts %r / %r" % (nm, i, nm_text, sets.get("SkyyPfCard%sL3" % i)))
            ico = [k for k in ids["SkyyPfCard%sF0" % i]["kids"] if not k["id"]]
            check(any(SUI.norm_color(k["props"].get("Background", "")) == SUI.norm_color(SUI.COLOR["cardOverlay"]) for k in ico),
                  "D %s: overdue card %s icon covered" % (nm, i))
        elif role == "deleted":
            left = st[13].get(i, st[13].get("LIVE2"))
            want3 = "Deleted - restore it within %s. Then it is gone." % fmt_left(left)
            check(has("Res") and not has("Sw") and not has("Del") and SUI.TEX["btnPrimary"] in raw.get("SkyyPfRes" + i, ""),
                  "D %s: deleted card %s = Restore (Primary) only" % (nm, i))
            check(sets.get("SkyyPfCard%sL3" % i) == want3 and nm_text == safe(ex["names"][i] + " - DELETED"),
                  "D %s: deleted card %s texts %r / %r" % (nm, i, nm_text, sets.get("SkyyPfCard%sL3" % i)))
            ico = [k for k in ids["SkyyPfCard%sF0" % i]["kids"] if not k["id"]]
            check(any(SUI.norm_color(k["props"].get("Background", "")) == SUI.norm_color(SUI.COLOR["cardOverlay"]) for k in ico),
                  "D %s: deleted card %s icon covered (the sold-out cover)" % (nm, i))
        elif role == "swdel":
            check(has("Sw") and has("Del") and has("SwRow") and not has("Res") and SUI.TEX["btnDestructive"] in raw.get("SkyyPfDel" + i, "")
                  and SUI.TEX["btnSecondary"] in raw.get("SkyyPfSw" + i, ""), "D %s: card %s = small Switch + Destructive Delete" % (nm, i))
        elif role == "switch":
            check(has("Sw") and not has("Del") and not has("Res"), "D %s: card %s = Switch only (no Delete)" % (nm, i))
        else:
            check(not has("Sw") and not has("Del") and not has("Res"), "D %s: active card %s has no Switch / Delete / Restore" % (nm, i))
    if ex["mode"] == "delete":
        check(sets.get("SkyyPfDelQ") == ex["text"], "D %s: the delete question %r" % (nm, sets.get("SkyyPfDelQ")))
        check(SUI.TEX["btnDestructive"] in raw.get("SkyyPfDelYes", "") and SUI.TEX["btnSecondary"] in raw.get("SkyyPfDelNo", "")
              and SUI.sounds("cancel") in raw.get("SkyyPfDelNo", "") and SUI.sounds("cancel") in raw.get("SkyyPfDelYes", ""),
              "D %s: Delete = Destructive, Cancel = Secondary (both the cancel sound)" % nm)
        check("SkyyPfClose" not in ids and "SkyyPfFoot" not in ids and "SkyyPfConfirm" not in ids, "D %s: the question replaces the footer" % nm)
    elif ex["mode"] == "foot":
        check(sets.get("SkyyPfFoot") == ex["text"], "D %s: footer %r (want %r)" % (nm, sets.get("SkyyPfFoot"), ex["text"]))
        check("SkyyPfClose" in ids and SUI.TEX["btnSecondary"] in raw.get("SkyyPfClose", "") and SUI.sounds("cancel") in raw.get("SkyyPfClose", ""),
              "D %s: footer Close = Secondary + the cancel sound" % nm)
    else:
        check("SkyyPfConfirm" in ids and "SkyyPfClose" not in ids and "SkyyPfDelRow" not in ids, "D %s: the switch question row" % nm)
    return ex


# ============================================================================================ main
KNOWN = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Shaman"]
FOOT_TAIL = " Switching saves your inventory and takes you to the island of the other profile. Not while in combat."


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
    if "--logic" in sys.argv:
        run_logic(arg("--logic"), arg("--classes"), arg("--livecopy"))
        return
    if "--restart" in sys.argv:
        run_restart(arg("--restart"))
        return
    if "--start" in sys.argv:
        run_start(arg("--start"), arg("--home"), arg("--out"))
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
    p = subprocess.run([sys.executable, me, "--logic", JAR, "--classes", CLS_JAR, "--livecopy", copy, "--dir", SCRATCH], env=env)
    check(p.returncode == 0, "G child (delete / restore / archive on a copy of the live data): see its lines above")
    p = subprocess.run([sys.executable, me, "--restart", JAR, "--dir", SCRATCH], env=env)
    check(p.returncode == 0, "R child (a fresh JVM: restart keeps the timer, the join path): see its lines above")
    # S: two server starts on another copy of the live folder (two JVMs, like two real starts)
    shome = os.path.join(SCRATCH, "start", "mods", "Skyy_SkyyProfiles")
    shutil.copytree(LIVE, shome)
    trees, starts = [all_hashes(shome)], []
    for k in (1, 2):
        sout = os.path.join(SCRATCH, "start-%d.json" % k)
        p = subprocess.run([sys.executable, me, "--start", JAR, "--home", shome, "--out", sout, "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(sout), "S start %d ran" % k)
        starts.append(json.load(open(sout)) if os.path.isfile(sout) else {})
        trees.append(all_hashes(shome))
    check(trees[1] == trees[0], "S start 1 on the live copy changes nothing in Skyy_SkyyProfiles: %s" % sorted(
        set(trees[1].items()) ^ set(trees[0].items()))[:6])
    check(trees[2] == trees[1], "S start 2 changes nothing either")
    check(not os.path.exists(os.path.join(shome, "archive")), "S no archive folder (nothing was deleted on the live data)")
    lp, lact, _raw = live_players()
    for k, st in enumerate(starts, 1):
        d = st.get("describe", "")
        check(all(("%s %s - " % (pid, pnm)) in d for pid, pnm, _c, _l in lp) and ("slots %d/%d" % (len(lp), CAP_FALLBACK)) in d and "DELETED" not in d
              and st.get("undo") == UNDO_MS and st.get("waiting") == 0 and st.get("archived") == 0 and st.get("up") is None and st.get("capm") is None
              and "deleteUndoHours=6" in st.get("summary", "") and st.get("key") == (LIVE_UUID if lact == "1" else "%s-p%s" % (LIVE_UUID, lact)),
              "S start %d: %s | %s" % (k, d, st.get("summary")))
    print("S. two starts on a copy of the live folder: unchanged; %s" % starts[-1].get("describe"))
    if not (os.path.isfile(outs["new"]) and os.path.isfile(outs["old"]) and os.path.isfile(bco)):
        return finish()
    new, old = json.load(open(outs["new"])), json.load(open(outs["old"]))
    # A
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                            os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    # B-D
    import skyyui as SUI
    SUI.verify(quiet=True)
    src = open(SCRIPT, encoding="utf8").read()
    data_colors = eval(re.search(r"^UI_DATA_COLORS = (\[.*?\](?:\s*\+\s*\[.*?\])?)\n", src, re.M | re.S).group(1))
    counts = new_counts()
    extra = {"compat": 0, "same_create": 0, "del": 0, "cards": 0, "deleted_cards": 0, "questions": 0, "footers": 0}
    for st in STATES_COMPAT:
        nm, view = st[0], st[1]
        check(nm in new["states"] and nm in old["states"], "B: state %s built by both jars" % nm)
        if not (nm in new["states"] and nm in old["states"]):
            continue
        ns_, os_ = new["states"][nm], old["states"][nm]
        if view == 1:
            check(ns_["commands"] == os_["commands"] and ns_["events"] == os_["events"], "C %s: the Create Profile view is byte for byte 0.1.4's" % nm)
            extra["same_create"] += 1
        else:
            fil = [e for e in ns_["events"] if not re.fullmatch(r"pfdel\d+|pfclose", ev_a(e) or "")]
            check(fil == os_["events"], "C %s: every 0.1.4 binding, same order (the new ones aside)" % nm)
            na = [ev_a(e) for e in ns_["events"]]
            check(all(na[k - 1] == "pfsw" + a[5:] for k, a in enumerate(na) if a.startswith("pfdel")), "C %s: each pfdel<id> follows its pfsw<id>" % nm)
            oi, ni = set(ids_of(os_)), set(ids_of(ns_))
            check(not (oi - ni), "C %s: no 0.1.4 id missing: %s" % (nm, sorted(oi - ni)))
            ot, nt = texts_of(os_), texts_of(ns_)
            check(not (ot - nt), "C %s: every 0.1.4 text still shown: %s" % (nm, sorted(ot - nt)))
            counts["bindings"] += len(ns_["events"])
            counts["ids"] += len(oi)
            counts["texts"] += len(ot)
        got = markup_checks(nm, ns_, SUI, counts, data_colors)
        if got is None:
            continue
        root, ids, sets, raw = got
        cards = [i for i in ids if re.fullmatch(r"SkyyPf(Card\d+|Cls\d+|NewCard)", i)]
        check(cards and all(_pairs(ids[c]["props"].get("Anchor")).get("Height") == CARD_H_NEW for c in cards), "D %s: every card %d px" % (nm, CARD_H_NEW))
        if view == 0:
            ex = check_list_015(nm, st, ns_, got, SUI)
            extra["cards"] += len(ex["shown"])
            extra["footers"] += ex["mode"] == "foot"
        extra["compat"] += 1
    for st in STATES_DEL:
        nm = st[0]
        check(nm in new["states"], "B: state %s built" % nm)
        if nm not in new["states"]:
            continue
        ns_ = new["states"][nm]
        got = markup_checks(nm, ns_, SUI, counts, data_colors)
        if got is None:
            continue
        ex = check_list_015(nm, st, ns_, got, SUI)
        extra["del"] += 1
        extra["cards"] += len(ex["shown"])
        extra["deleted_cards"] += len([i for i in ex["shown"] if i in ex["dels"]])
        extra["questions"] += ex["mode"] == "delete"
        extra["footers"] += ex["mode"] == "foot"
        counts["bindings"] += len(ns_["events"])
    report_counts(counts)
    print("C-D (0.1.5). %(compat)d compat states (%(same_create)d Create Profile views byte for byte 0.1.4's), %(del)d delete states; %(cards)d "
          "profile cards (%(deleted_cards)d deleted), %(questions)d delete questions and %(footers)d footers word for word" % extra)
    # E
    check_card_block(SUI, data_colors)
    sha = hashlib.sha256(card_block(SCRIPT).encode("utf8")).hexdigest()
    check(re.search(r'^CARD_SHA = "%s"' % sha, open(PATCH_015, encoding="utf8").read(), re.M) is not None,
          "E: tools/profiles_0_1_5_patch.py asserts the same CARD_SHA (the block is unchanged)")
    # F
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    added = sorted(set(zn.namelist()) - set(zo.namelist()))
    check(added == sorted("com/skyy/profiles/%s.class" % c for c in NEW_CLASSES) and not (set(zo.namelist()) - set(zn.namelist())),
          "F: new classes %s, none gone" % [a.split("/")[-1] for a in added])
    diff = set(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    same = len(set(zo.namelist()) & set(zn.namelist())) - len(diff)
    check(diff == EXPECTED_DIFF, "F: exactly %s differ, got %s" % (sorted(EXPECTED_DIFF), sorted(diff)))
    check(not [n for n in zn.namelist() if n.endswith(".ui")], "F: no .ui files in the jar (inline pages only)")
    mo, mn = json.loads(zo.read("manifest.json")), json.loads(zn.read("manifest.json"))
    check(set(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k)) <= {"Version", "Name", "Description"} and mn.get("Version") == VERSION,
          "F: manifest: only version / name / description differ")
    bc = json.load(open(bco))

    def meth(cls, kind):
        return sorted(m.split("(")[0] for m in bc.get("com/skyy/profiles/%s.class" % cls, {}).get(kind, []))
    want = {
        "ProfCfg": ({"summary", "load", "<clinit>", "capMigrate"}, ["windowText"], ["UNDO_MS J"]),      # capMigrate: the version in its marker
        "ProfStore": ({"count", "nextId", "lowestId", "activeOf", "create", "setActive", "listText", "describe", "resolveId"},   # resolveId: MAX_ID
                      sorted(["isDel", "live", "gone", "pendingCount", "goneCount", "slotsMark", "markDeleted", "unDelete", "archiveCommit",
                              "restoreCommit", "untilOf", "fmtLeft"]), []),
        "ProfNames": ({"used"}, [], []),
        "ProfSwitch": ({"switchTo", "createFirst"}, [], []),
        "ProfilePage": ({"buildList", "handleDataEvent", "open", "ProfilePage"}, ["deleteEvent", "shownIds"], ["delAsk Ljava/lang/String;"]),
        "ProfJoin": ({"prepare"}, [], []), "ReadyTask": ({"run"}, [], []), "ProfilesCmd": ({"ProfilesCmd"}, [], []), "AdmInfoCmd": ({"execute"}, [], []),
        "ProfileAdminCmd": ({"ProfileAdminCmd", "execute"}, [], []),
        "CfgFile": ({"<clinit>"}, [], []),
        "SkyyProfilesPlugin": ({"setup", "shutdown"}, [], ["sweeper Ljava/util/concurrent/ScheduledFuture;"]),
    }
    for cls, (chg, nw, fnew) in want.items():
        c = bc.get("com/skyy/profiles/%s.class" % cls, {})
        check(set(meth(cls, "changed")) == chg and meth(cls, "new") == nw and not c.get("gone") and c.get("fields_gone") == [] and
              c.get("fields_new") == fnew, "F: %s: changed %s, new %s, fields %s" % (cls, meth(cls, "changed"), meth(cls, "new"), c.get("fields_new")))
    cm = bc.get("com/skyy/profiles/ProfCfg.class", {}).get("listing", {}).get("capMigrate()Ljava/lang/String;", "")
    check('ldc "%s"' % VERSION in cm and "deleteUndo" not in cm, "F: ProfCfg.capMigrate changed only by the version it writes into its marker")
    rows_ = bc.get("com/skyy/profiles/CfgRows.class", {})
    check(set(m.split("(")[0] for m in rows_.get("changed", [])) <= {"<clinit>", "header"} and not rows_.get("new") and not rows_.get("gone")
          and rows_.get("consts") == {"VERSION": [OLD_VERSION, VERSION]} and "deleteUndoHours" in rows_.get("listing", {}).get("<clinit>()V", ""),
          "F: CfgRows: the new row deleteUndoHours + the version")
    fnc = bc.get("com/skyy/profiles/CfgFn.class", {})
    check(fnc.get("version_only"), "F: CfgFn: only the version string differs: %s" % fnc.get("changed"))
    lst = bc.get("com/skyy/profiles/SkyyProfilesPlugin.class", {}).get("listing", {}).get("setup()V", "")
    check(0 <= lst.find("ProfCfg.capMigrate") < lst.find("ProfCfg.load") < lst.find("ProfDel.scanIndex") < lst.find("profile:fn:state")
          < lst.find("CfgPub.start"), "F: setup order capMigrate -> load -> folders -> scanIndex -> bridge -> ... -> CfgPub.start")
    print("F. class bytes: %d entries identical, differ: %s; new: %s" % (same, ", ".join(sorted(n.split("/")[-1] for n in diff)),
                                                                      ", ".join(NEW_CLASSES)))
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
