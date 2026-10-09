"""SkyyProfiles 0.1.9 - bare-JVM harness for THE PROFILE CAP = THE NUMBER OF CLASSES (tools/profiles_0_1_9_patch.py; Skyy LOCKED 2026-10-08:
"profile cap should match the number of classes. ( upgrade: ranks and earn in game later)"). Child JVMs run the game's own JRE with
HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder. The live save data is
only ever READ and copied into scratch (checked afterwards). Built on the 0.1.5 / 0.1.7 harnesses and the SkyySkills 0.4.27 harness helpers
(imported, never edited).

    python SkyyProfiles/test_skyyprofiles_0.1.9.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyyProfiles-0.1.9.jar] [--prev SkyyProfiles-0.1.8.jar] [--live <Skyy_SkyyProfiles folder>]

SECTIONS
  A    every class of both jars loads, verifies (-Xverify:all) and initialises (own class loader each)
  CC   CLASS COMPARE 0.1.8 -> 0.1.9 (javassist text of every method / constructor / static initialiser): exactly the planned classes and
       methods changed or were added, nothing removed
  Z    engine-access audit (the 0.1.7 harness routine): every class / field / method reference passes MethodHandles.Lookup in its class
  CAP  EXECUTED (new jar; the old jar for the comparison): ProfCfg.classCount / listCount / knownName / baseCap / capFor / capWhy /
       capNote / bonusSlots / bonusWarn with no class:list, SkyyClasses 0.1.15's list, + Spellblade, + the Shaman alias, + a 9th and a
       20th class, fixed 6 / 3 / 8, rank extras, bonus, the LIMIT_MAX clamp, broken / garbage hooks; ProfRoster cards (Spellblade
       coming later; on when class:list lists it)
  BON  EXECUTED: the REAL BonusFn (bridge profile:fn:bonusSlots) get / set / clamp / remove / bad arguments / unreadable file,
       ProfStore.bonusOf / setBonus on a scratch players folder, AdmBonusCmd.run (the whole /profileadmin bonus logic), switches.log
  GATE EXECUTED: the REAL ProfSwitch.createAndSwitch limit gate: a player with 6 profiles can create #7 and #8 (store creates them), the
       9th is refused "All 8 profile slots are used."; 0.1.8 refuses the 8th; Skyy's live copy (7 profiles) may create #8 (0.1.8: no);
       + 1 bonus slot = a 9th; a deleted profile frees its slot; ProfilePage.shownIds draws up to 16 (0.1.8: 8)
  PG   PAGES (the REAL ProfilePage.buildList / buildCreate, 13 states): the 0.1.5 harness's markup model (check_markup, check_page,
       colours, layout, the body filled exactly, text fit with the client's font, contrast) with LayoutMode TopScrolling as a scrolling
       Top list: the window is 1100 x 980 (fits 1080), the Profiles list shows 8 cards and the Create Profile list 7 without scrolling,
       every card + the scrollbar room fits the list's width; texts (This is profile 7 of 8 - one per class., + N bonus, Spellblade -
       coming later, All 8 profile slots are used); 14 classes = the first 12 cards (MAX_CARDS)
  ST   START TWICE on a scratch COPY of Skyy's live Skyy_SkyyProfiles (the plugin's setup data steps, the 0.1.5 routine) for both jars:
       nothing in the folder changes; 0.1.9 reads the same 7 profiles, slots 7/8 (0.1.8: 7/7)
  KEEP a hand-edited cap is kept: maxProfiles=5 and an owner's maxProfiles=6 (cap-auto marker present) start twice unchanged byte for
       byte and run as fixed 5 / 6; maxProfiles=12 by hand reads as 8; a NEW server (no config) writes maxProfiles=auto and runs auto = 8
  FIX  (critic round) /profileadmin bonus: an unknown uuid with no players file is refused and NO file is written; the reply names the
       player ("for SkyLordPlayz", "Your ..." for yourself), never the raw uuid; MIG: capMigrate EXECUTED on the untouched 0.1.1 default
       file and on an edited maxProfiles=6 file - its notes say 8 / "one profile per class of the game", never "6 without SkyyClasses"
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.1.9", "0.1.8"
PKG = "com.skyy.profiles."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "prof019", "h")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyProfiles-%s.jar" % PREV_VERSION)))
SCRIPT = os.path.join(HERE, "build_skyyprofiles_%s.py" % VERSION)
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
MODS_LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods")
LIVE = os.path.abspath(arg("--live", os.path.join(MODS_LIVE, "Skyy_SkyyProfiles")))
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")
LIVE_UUID = "d8ddde89-98b2-4739-983e-a39773d582b6"
CL15 = "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity,Assassin:Assassination,Monk:Zen"
HOUR, DAY, MIN = 3600000, 86400000, 60000
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def sk():
    return _mod(SKILLS_HARNESS, "ts0427")


def t15():
    return _mod(os.path.join(HERE, "test_skyyprofiles_0.1.5.py"), "tp015")


def t17():
    return _mod(os.path.join(HERE, "test_skyyprofiles_0.1.7.py"), "tp017")


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs) if os.path.isdir(d) else {}


def props(path):
    out = {}
    if not os.path.isfile(path):
        return out
    for ln in open(path, encoding="latin-1").read().splitlines():
        if ln and ln[0] not in "#!" and "=" in ln:
            k, v = ln.split("=", 1)
            out[k.strip()] = v.strip()
    return out


# ============================================================================================ child: CAP + BON + GATE (one jar)
def run_cap(jar, home, out, tag):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    S = sk()
    S.jvm_start()
    ld = S.loader(jar)
    R = {"tag": tag}
    R["classes"], R["load_fails"] = S.load_all(jar, ld)
    C = lambda n: JClass(PKG + n, loader=ld)
    new = tag == "new"
    UUID, Paths, Integer, Long, Obj = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Object")
    Str = JClass("java.lang.String")
    try:
        Cfg, Store, Ros, Sw, Page = C("ProfCfg"), C("ProfStore"), C("ProfRoster"), C("ProfSwitch"), C("ProfilePage")
        P = lambda *a: Paths.get(os.path.join(home, *a), JArray(Str)(0))
        Cfg.FILE = P("config.properties")
        Store.DIR, Store.SWDIR, Store.INVDIR, Store.LOGF = P("players"), P("switching"), P("inventories"), P("switches.log")
        C("ProfDel").ARCDIR = P("archive")
        br = Cfg.bridge()

        @JImplements("java.util.function.Function")
        class Fixed(object):
            def __init__(self, v):
                self.v = v

            @JOverride
            def apply(self, o):
                if self.v == "throw":
                    raise ValueError("boom")
                return self.v

        def clear():
            for k in ("class:list", "rank:fn:profileSlots", "profile:fn:bonusSlots"):
                br.remove(k)
        u0 = UUID(0x19, 0x1)

        def cap_row(mx, clist, rank=None, bonus=None):
            clear()
            Cfg.MAX_SETTING = mx
            if clist is not None:
                br.put("class:list", clist)
            if rank is not None:
                br.put("rank:fn:profileSlots", Fixed(rank))
            if bonus is not None:
                br.put("profile:fn:bonusSlots", Fixed(bonus))
            row = {"base": int(Cfg.baseCap()), "cap": int(Cfg.capFor(u0)), "why": str(Cfg.capWhy(u0)), "note": str(Cfg.capNote()),
                   "count": int(Cfg.classCount())}
            if new:
                row["list"] = int(Cfg.listCount())
                row["bonus"] = int(Cfg.bonusSlots(u0))
            return row
        cases = {
            "none": ("auto", None), "c15": ("auto", CL15), "c15sb": ("auto", CL15 + ",Spellblade:Battlemagic"),
            "c15sham": ("auto", CL15 + ",Shaman:Totems,shamans"), "c15nine": ("auto", CL15 + ",Necromancer:Death"),
            "twenty": ("auto", ",".join("C%d:S" % i for i in range(20))), "empty": ("auto", "  "),
            "fix6": ("6", CL15), "fix8": ("8", None), "fix1": ("1", CL15),
        }
        R["cap"] = dict((k, cap_row(*v)) for k, v in cases.items())
        R["cap"]["fix3_rank2"] = cap_row("3", CL15, rank=Integer(2))
        R["cap"]["auto_rank8"] = cap_row("auto", CL15, rank=Integer(8))
        if new:
            R["cap"]["fix3_rank2_bonus1"] = cap_row("3", CL15, rank=Integer(2), bonus=Integer(1))
            R["cap"]["auto_bonus2"] = cap_row("auto", CL15, bonus=Integer(2))
            R["cap"]["auto_bonus0"] = cap_row("auto", CL15, bonus=Integer(0))
            R["cap"]["auto_bonus_neg"] = cap_row("auto", CL15, bonus=Integer(-4))
            R["cap"]["auto_bonusnull"] = cap_row("auto", CL15, bonus=None)
            R["cap"]["clamp16"] = cap_row("auto", CL15, rank=Integer(8), bonus=Integer(40))
            R["warned_before"] = bool(Cfg.BONUS_WARNED)
            R["cap"]["bonus_garbage"] = cap_row("auto", CL15, bonus=JObject("lots", Str))
            R["warned_after_garbage"] = bool(Cfg.BONUS_WARNED)
            Cfg.BONUS_WARNED = False
            R["cap"]["bonus_throw"] = cap_row("auto", CL15, bonus="throw")
            R["warned_after_throw"] = bool(Cfg.BONUS_WARNED)
            R["known"] = [str(x) for x in Cfg.KNOWN]
            R["knownName"] = [str(Cfg.knownName(x)) for x in (" Shaman ", "SHAMANS", "Monk", "spellblade", None, "Shaman skill")]
            R["limit_max"] = int(Cfg.LIMIT_MAX)
            R["page_max"] = [int(Page.MAX_CARDS), int(Page.LIST_MAX)]
        clear()
        Cfg.MAX_SETTING = "auto"
        # ---- roster cards
        R["roster"] = {}
        for k, lst in (("none", None), ("c15", CL15), ("c15sb", CL15 + ",Spellblade:Bladesong")):
            clear()
            if lst:
                br.put("class:list", lst)
            R["roster"][k] = [[str(x) for x in e] for e in Ros.roster()]
        clear()
        # ---- BON: the REAL BonusFn on a scratch players folder
        if new:
            Fn = C("BonusFn")()
            br.put("profile:fn:bonusSlots", Fn)
            br.put("class:list", CL15)
            u1, u2 = UUID(0x19, 0x2), UUID(0x19, 0x3)
            pf1 = os.path.join(home, "players", str(u1) + ".properties")
            b = {}
            b["get0"] = str(Fn.apply(u1))
            b["cap0"] = int(Cfg.capFor(u1))
            b["file_before"] = os.path.exists(pf1)
            b["set2"] = str(Fn.apply(JArray(Obj)([u1, Integer(2)])))
            b["file2"] = props(pf1).get("bonusSlots")
            b["get2"] = str(Fn.apply(u1))
            b["cap2"] = int(Cfg.capFor(u1))
            b["why2"] = str(Cfg.capWhy(u1))
            b["setneg"] = str(Fn.apply(JArray(Obj)([u1, Integer(-5)])))
            b["fileneg"] = props(pf1).get("bonusSlots", "<none>")
            b["set99"] = str(Fn.apply(JArray(Obj)([u1, Long(99)])))
            b["file99"] = props(pf1).get("bonusSlots")
            b["cap99"] = int(Cfg.capFor(u1))
            b["bad_str"] = str(Fn.apply(JArray(Obj)([u1, JObject("3", Str)])))
            b["bad_short"] = str(Fn.apply(JArray(Obj)([u1])))
            b["bad_key"] = str(Fn.apply(JObject("x", Str)))
            b["bad_null"] = str(Fn.apply(None))
            b["bad_uuid_pos"] = str(Fn.apply(JArray(Obj)([Integer(1), u1])))
            Store.BROKEN.put(u2, Long(int(time.time() * 1000)))
            b["broken"] = str(Fn.apply(JArray(Obj)([u2, Integer(1)])))
            b["broken_file"] = os.path.exists(os.path.join(home, "players", str(u2) + ".properties"))
            Store.BROKEN.remove(u2)
            Pr = JClass("java.util.Properties")
            pp = Pr()
            vals = {}
            for v in ("-3", "abc", "40", "7", " 2 "):
                pp.setProperty("bonusSlots", v)
                vals[v] = int(Store.bonusOf(pp))
            pp.remove("bonusSlots")
            vals["absent"] = int(Store.bonusOf(pp))
            b["bonusOf"] = vals
            # setBonus keeps every other key of a real players file (Skyy's live copy)
            ul = UUID.fromString(LIVE_UUID)
            pl = os.path.join(home, "players", LIVE_UUID + ".properties")
            before = props(pl)
            b["live_set"] = bool(Store.setBonus(ul, 1))
            after = props(pl)
            b["live_same_rest"] = dict((k, v) for k, v in after.items() if k != "bonusSlots") == before and after.get("bonusSlots") == "1"
            b["live_cap1"] = int(Cfg.capFor(ul))
            b["live_clear"] = bool(Store.setBonus(ul, 0))
            b["live_back"] = props(pl) == before
            # AdmBonusCmd.run = the whole /profileadmin bonus logic
            A = C("AdmBonusCmd")
            b["adm3"] = str(A.run(str(u1), "3", "Tester"))
            b["adm3_file"] = props(pf1).get("bonusSlots")
            b["adm_bad"] = str(A.run(str(u1), "x", "Tester"))
            b["adm_17"] = str(A.run(str(u1), "17", "Tester"))
            b["adm_neg"] = str(A.run(str(u1), "-1", "Tester"))
            b["adm_null"] = str(A.run(str(u1), None, "Tester"))
            b["adm_who"] = str(A.run("nobody-here-xyz", "1", "Tester"))
            b["adm0"] = str(A.run(str(u1), "0", "Tester"))
            b["adm0_file"] = props(pf1).get("bonusSlots", "<none>")
            b["adm_live_name"] = str(A.run("SkyLordPlayz", "0", "Tester"))
            # FIX: an unknown uuid (no players file, not online) is refused and leaves no orphan file
            uo = UUID(0x19, 0x77)
            pfo = os.path.join(home, "players", str(uo) + ".properties")
            b["adm_orphan"] = str(A.run(str(uo), "2", "Tester"))
            b["adm_orphan_file"] = os.path.exists(pfo)
            # FIX: an admin targeting themself reads "Your ..."
            b["adm_self"] = str(A.run("SkyLordPlayz", "1", "SkyLordPlayz"))
            b["adm_self_file"] = props(os.path.join(home, "players", LIVE_UUID + ".properties")).get("bonusSlots")
            b["adm_self0"] = str(A.run(LIVE_UUID, "0", "skylordplayz"))
            log = open(os.path.join(home, "switches.log"), encoding="utf8", errors="replace").read() if os.path.isfile(os.path.join(home, "switches.log")) else ""
            b["log_bonus"] = [ln.split(" ", 1)[1] if " " in ln else ln for ln in log.splitlines() if " BONUS " in ln or ln.startswith("BONUS")]
            R["bon"] = b
            clear()
        # ---- GATE: the REAL createAndSwitch limit gate (it returns before touching the world when the limit or BUSY refuses)
        PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        Unsafe = JClass("sun.misc.Unsafe")
        uf = Unsafe.class_.getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        U = uf.get(None)

        def pref(u, name):
            pr = U.allocateInstance(PRef.class_)
            for f, v in (("uuid", u), ("username", name)):
                fd = PRef.class_.getDeclaredField(f)
                fd.setAccessible(True)
                fd.set(pr, v)
            return pr
        br.put("class:list", CL15)
        Cfg.MAX_SETTING = "auto"
        g = {}
        u6 = UUID(0x19, 0x6)
        f6 = os.path.join(home, "players", str(u6) + ".properties")
        os.makedirs(os.path.dirname(f6), exist_ok=True)
        with open(f6, "w", encoding="latin-1") as fh:
            fh.write("active=1\nepoch=6\n")
            for i, c in enumerate(["Archer", "Warrior", "Mage", "Berserker", "Priest", "Monk"], 1):
                fh.write("p.%d.name=Fruit%d\np.%d.class=%s\np.%d.created=%d\n" % (i, i, i, c, i, 1700000000000 + i))
        Store.reload(u6)
        pr6 = pref(u6, "SixProfiles")
        BUSY = Long(1)

        def gate(u, pr):
            Store.BUSY.put(u, BUSY)
            try:
                return str(Sw.createAndSwitch(None, None, pr, None, "Mage", "Kiwi"))
            finally:
                Store.BUSY.remove(u)

        def create(u, cls):
            p = Store.load(u)
            nid = str(Store.nextId(p))
            return nid, bool(Store.create(u, nid, "Made" + nid, cls, False))
        g["six_count"] = int(Store.count(Store.load(u6)))
        g["six_cap"] = int(Cfg.capFor(u6))
        g["six_gate"] = gate(u6, pr6)
        g["make7"] = create(u6, "Assassin")
        g["seven_gate"] = gate(u6, pr6)
        if g["seven_gate"] == "A profile switch is already running.":
            g["make8"] = create(u6, "Archer")
            g["eight_count"] = int(Store.count(Store.load(u6)))
            g["eight_gate"] = gate(u6, pr6)
            if new:
                br.put("profile:fn:bonusSlots", C("BonusFn")())
                Store.setBonus(u6, 1)
                g["eight_bonus_gate"] = gate(u6, pr6)
                g["make9"] = create(u6, "Mage")
                g["nine_gate"] = gate(u6, pr6)
                g["nine_why"] = str(Cfg.capWhy(u6))
                # a deleted profile frees its slot (ProfStore.count = live only)
                now = int(time.time() * 1000)
                g["del"] = bool(Store.markDeleted(u6, "9", now, now + 6 * HOUR))
                g["after_del_gate"] = gate(u6, pr6)
                Store.setBonus(u6, 0)
                br.remove("profile:fn:bonusSlots")
        ul = UUID.fromString(LIVE_UUID)
        Store.reload(ul)
        g["live_count"] = int(Store.count(Store.load(ul)))
        g["live_cap"] = int(Cfg.capFor(ul))
        g["live_gate"] = gate(ul, pref(ul, "SkyLordPlayz"))
        # shownIds: 12 live + 3 deleted
        Pr = JClass("java.util.Properties")
        pp = Pr()
        for i in range(1, 16):
            pp.setProperty("p.%d.name" % i, "N%d" % i)
            pp.setProperty("p.%d.class" % i, "Mage")
            if i > 12:
                pp.setProperty("p.%d.deleted" % i, "1")
                pp.setProperty("p.%d.until" % i, str(int(time.time() * 1000) + HOUR))
        g["shown"] = [str(x) for x in Page.shownIds(pp)]
        R["gate"] = g
        clear()
        # ---- the command objects themselves (constructors: name, permission, arguments, sub-command wiring)
        if new:
            cm = {}
            try:
                ab = C("AdmBonusCmd")()
                cm["bonus_name"] = str(ab.getName())
                cm["bonus_perm"] = str(ab.getPermission())
                adm = C("ProfileAdminCmd")()
                sub = adm.getSubCommand("bonus")
                cm["admin_bonus"] = None if sub is None else str(sub.getClass().getSimpleName())
                cm["admin_setclass"] = None if adm.getSubCommand("setclass") is None else "ok"
            except Exception as e:
                cm["error"] = str(e)[:400]
            R["cmds"] = cm
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ child: PG (page states, new jar)
LONG = "Abcdefghijklmnopqrstuvwxyzabcdef"
SIX = [(str(i), n, c) for i, n, c in zip(range(1, 7), ["Apple", "Banana", "Kiwi", "Lemon", "Mango", "Pear"],
                                          ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Monk"])]
EIGHT = SIX + [("7", "Lime", "Assassin"), ("8", LONG, "Berserker")]
NINE = EIGHT + [("9", "Plum", "Mage")]
SIXTEEN = [(str(i), "Slot%d" % i, ["Archer", "Mage", "Priest", "Monk"][i % 4]) for i in range(1, 19)]
# (name, view, first, profiles or "LIVE", active, pending, pickName, pickClass, info, max, class:list, bonus, deleted {id: ms left}, delAsk)
PG_STATES = [
    ("list live skyy", 0, False, "LIVE", None, None, "", None, "", "auto", CL15, 0, {}, None),
    ("list six", 0, False, SIX, "1", None, "", None, "", "auto", CL15, 0, {}, None),
    ("list seven pending", 0, False, EIGHT[:7], "2", "7", "", None, "", "auto", CL15, 0, {}, None),
    ("list eight full", 0, False, EIGHT, "8", None, "", None, "", "auto", CL15, 0, {}, None),
    ("list eight ask", 0, False, EIGHT, "1", None, "", None, "", "auto", CL15, 0, {}, "8"),
    ("list nine bonus", 0, False, NINE, "9", None, "", None, "", "auto", CL15, 2, {}, None),
    ("list sixteen", 0, False, SIXTEEN, "1", None, "", None, "", "auto", CL15, 8, {"17": 5 * HOUR, "18": HOUR}, None),
    ("list fixed six of eight", 0, False, EIGHT, "3", None, "", None, "", "6", CL15, 0, {}, None),
    ("create eight classes", 1, False, SIX, "1", None, "Kiwi", None, "", "auto", CL15, 0, {}, None),
    ("create spellblade later", 1, False, SIX, "1", None, "Kiwi", None, "Spellblade is coming later.", "auto", CL15, 0, {}, None),
    ("create nine classes", 1, False, SIX, "1", None, "Fig", "Necromancer", "", "auto", CL15 + ",Necromancer:Death", 0, {}, None),
    ("create thirteen classes", 1, False, SIX, "1", None, "Fig", None, "", "auto", CL15 + "," + ",".join("Extra%s:Skill" % c for c in "ABCDEF"), 0, {}, None),
    ("create first", 1, True, [], None, None, "Mango", "Archer", "", "auto", CL15, 0, {}, None),
    ("create first no classes mod", 1, True, [], None, None, "Mango", None, "", "auto", None, 0, {}, None),
    ("create full", 1, False, EIGHT, "1", None, "Lemon", "Archer", "", "auto", CL15, 0, {}, None),
    ("create bonus ninth", 1, False, EIGHT, "1", None, "Plum", "Mage", "", "auto", CL15, 1, {}, None),
    ("create spellblade on", 1, False, SIX, "1", None, "Kiwi", "Spellblade", "", "auto", CL15 + ",Spellblade:Battlemagic", 0, {}, None),
]


def run_pg(jar, live_copy, out):
    from jpype import JClass, JImplements, JOverride
    T = t15()
    T._jvm_start([jar])
    Page, Cfg = JClass(PKG + "ProfilePage"), JClass(PKG + "ProfCfg")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UUID, Props, System, Integer = JClass("java.util.UUID"), JClass("java.util.Properties"), JClass("java.lang.System"), JClass("java.lang.Integer")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    @JImplements("java.util.function.Function")
    class Fixed(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            return self.v
    bridge = Cfg.bridge()
    me = UUID(0x9f019, 1)
    pr = U.allocateInstance(PRef.class_)
    for f, v in (("uuid", me), ("username", "Skyy")):
        fd = PRef.class_.getDeclaredField(f)
        fd.setAccessible(True)
        fd.set(pr, v)
    live = props(os.path.join(live_copy, "players", LIVE_UUID + ".properties"))
    res = {"states": {}}
    for st in PG_STATES:
        name, view, first, profs, active, pending, pick_name, pick_class, info, mx, clist, bonus, deleted, ask = st
        if profs == "LIVE":
            ids = sorted(set(k.split(".")[1] for k in live if k.startswith("p.") and k.endswith(".name")), key=int)
            profs = [(i, live["p.%s.name" % i], live.get("p.%s.class" % i, "")) for i in ids]
            active = live.get("active")
        for k in ("class:list", "class:fn:kitnew", "rank:fn:profileSlots", "profile:fn:bonusSlots"):
            bridge.remove(k)
        if clist is not None:
            bridge.put("class:list", clist)
        bridge.put("class:fn:kitnew", Fixed(JClass("java.lang.Boolean").TRUE))
        if bonus:
            bridge.put("profile:fn:bonusSlots", Fixed(Integer(bonus)))
        Cfg.MAX_SETTING = mx
        now = int(System.currentTimeMillis())
        p = Props()
        for pid, pname, pcls in profs:
            p.setProperty("p.%s.name" % pid, pname)
            p.setProperty("p.%s.class" % pid, pcls)
            p.setProperty("p.%s.created" % pid, str(1700000000000 + int(pid) * DAY))
            p.setProperty("p.%s.lastPlayed" % pid, str(now - int(pid) * HOUR))
        for pid, left in deleted.items():
            p.setProperty("p.%s.deleted" % pid, str(now + left - 6 * HOUR))
            p.setProperty("p.%s.until" % pid, str(now + left))
        if active:
            p.setProperty("active", active)
        page = Page(pr, 0, first)
        page.view, page.pending, page.pickName, page.pickClass, page.info, page.delAsk = view, pending, pick_name, pick_class, info, ask
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
        res["states"][name] = {"error": err, "commands": cmds, "events": evs, "nprofs": len(profs), "cap": int(Cfg.capFor(me))}
    json.dump(res, open(out, "w"), indent=1)
    os._exit(0)


def run_st(jar, home, out):
    t15().run_start(jar, home, out)
    os._exit(0)


def run_audit(jar, out):
    t17().run_audit(jar, out)
    os._exit(0)


# ============================================================================================ parent: page checks
def page_checks(pg):
    T = t15()
    import skyyui as SUI
    SUI.verify(quiet=True)
    src = open(SCRIPT, encoding="utf8").read()
    data_colors = eval(re.search(r"^UI_DATA_COLORS = (\[.*?\](?:\s*\+\s*\[.*?\])?)\n", src, re.M | re.S).group(1))
    scroll_w = SUI.SCROLL_SIZE + SUI.SCROLL_SPACING
    card_step = 92 + 4
    orig_layout = T.layout
    scroll_nodes = []

    def layout(root, issues):
        """TopScrolling = a Top list that may be taller than its box (it scrolls); everything else = the 0.1.5 model"""
        stack, sc = [root], []
        while stack:
            x = stack.pop()
            if x["props"].get("LayoutMode") == "TopScrolling":
                x["props"]["LayoutMode"] = "Top"
                x["scroll"] = True
                sc.append(x)
            stack.extend(x["kids"])
        mine = []
        order = orig_layout(root, mine)
        for i in mine:
            if any(("children of #%s need" % (n["id"])) in i for n in sc):
                continue
            issues.append(i)
        scroll_nodes[:] = sc
        return order
    T.layout = layout
    T.PAGE_W, T.PAGE_H = 1100, 980
    counts = T.new_counts()
    before = len(T.FAILS)
    out = {}
    for st in PG_STATES:
        nm, view = st[0], st[1]
        ns_ = pg["states"].get(nm)
        check(ns_ is not None and ns_["error"] is None, "PG %s: built (%s)" % (nm, (ns_ or {}).get("error")))
        if not ns_ or ns_["error"]:
            continue
        got = T.markup_checks(nm, ns_, SUI, counts, data_colors)
        if not got:
            continue
        root, ids, sets, _raw = got
        check(SUI.MAX_PAGE_H == 980 and root["props"] is not None, "PG %s: the window is at most 980 px high (fits 1080)" % nm)
        lst = ids.get("SkyyPfList")
        check(lst is not None and lst.get("scroll"), "PG %s: #SkyyPfList is a TopScrolling list" % nm)
        if lst is None:
            continue
        ix, iy, iw, ih = lst["inner"]
        cards = [k for k in lst["kids"]]
        visible = ih // card_step
        check(visible == (8 if view == 0 else 7), "PG %s: %d cards visible without scrolling (want %d)" % (nm, visible, 8 if view == 0 else 7))
        wide = [k["id"] for k in cards if k.get("used", 0) > iw - scroll_w]
        check(not wide and cards, "PG %s: every card (%d) + the 12 px scrollbar room fits the %d px list: %s" % (nm, len(cards), iw, wide))
        a = json.loads
        texts = dict((k, v) for k, v in sets.items())
        out[nm] = {"cards": len(cards), "texts": texts, "events": [e[2] for e in ns_["events"]]}
    T.layout = orig_layout
    for f in T.FAILS[before:]:
        check(False, "PG (0.1.5 markup model): " + f)
    print("PG: %d states, %d appends, %d placed, %d text lines, %d colours checked; tightest row slack %d px; widest text %.0f%%"
          % (counts["states"], counts["appends"], counts["placed"], counts["lines"], counts["colours"], counts["min_row_slack"],
             100.0 * counts["max_line_fill"]))
    return out


def txt(page, idpart):
    return [v for k, v in page["texts"].items() if idpart in k]


# ============================================================================================ parent
def main():
    if "--cap" in sys.argv:
        return run_cap(arg("--cap"), arg("--home"), arg("--out"), arg("--tag"))
    if "--pg" in sys.argv:
        return run_pg(arg("--pg"), arg("--home"), arg("--out"))
    if "--st" in sys.argv:
        return run_st(arg("--st"), arg("--home"), arg("--out"))
    if "--audit" in sys.argv:
        return run_audit(arg("--audit"), arg("--out"))
    if "--cc" in sys.argv:
        return sk().run_cc(arg("--cc"), arg("--prevjar"), arg("--out"), arg("--repl"))
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
    if not os.path.realpath(SCRATCH).startswith(sroot + os.sep):
        sys.exit("--dir must be inside tools/dev/scratch/ (deleted afterwards): %s" % SCRATCH)
    if os.path.exists(SCRATCH) and os.listdir(SCRATCH):
        sys.exit("%s is not empty - pass an empty --dir" % SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_before = snap(LIVE)
    me = os.path.abspath(__file__)

    def child(args_, out_):
        with open(out_ + ".log", "wb") as lf:
            subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        if not os.path.isfile(out_):
            print(open(out_ + ".log", encoding="utf8", errors="replace").read()[-3000:])
            return None
        return json.load(open(out_))
    try:
        # ---------------------------------------------------------------- CC
        cc = child(["--cc", JAR, "--prevjar", PREV_JAR, "--repl", json.dumps({"versions": [VERSION, PREV_VERSION], "rules": []})],
                   os.path.join(SCRATCH, "cc.json"))
        check(cc is not None, "CC: the compare child ran")
        if cc:
            plan = {
                "ProfCfg": {"structural": {"listCount(Ljava/lang/Object;)I", "classCount()I", "baseCap()I", "capFor(Ljava/util/UUID;)I",
                                           "capWhy(Ljava/util/UUID;)Ljava/lang/String;", "capNote()Ljava/lang/String;", "<clinit>",
                                           "listCount()I (new)", "knownName(Ljava/lang/String;)Ljava/lang/String; (new)",
                                           "bonusWarn(Ljava/lang/String;)V (new)", "bonusSlots(Ljava/util/UUID;)I (new)",
                                           # fixer: the one-time migration / upgrade log notes (8 / "one profile per class of the game")
                                           "capMigrate()Ljava/lang/String;", "upgradeDefault()Ljava/lang/String;"},
                            "fields_new": {"BONUS_FN:Ljava/lang/String;", "BONUS_WARNED:Z", "KNOWN:[Ljava/lang/String;",
                                           "KNOWN_ALIAS_FROM:[Ljava/lang/String;", "KNOWN_ALIAS_TO:[Ljava/lang/String;", "LIMIT_MAX:I"}},
                "ProfRoster": {"structural": {"<clinit>"}},
                "ProfStore": {"structural": {"bonusOf(Ljava/util/Properties;)I (new)", "setBonus(Ljava/util/UUID;I)Z (new)"}},
                "ProfilePage": {"structural": {"buildList(Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;Ljava/util/UUID;Ljava/util/Properties;)V",
                                               "buildCreate(Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;Ljava/util/UUID;Ljava/util/Properties;)V",
                                               "shownIds(Ljava/util/Properties;)[Ljava/lang/String;", "warnHidden(I)V",
                                               # MAX_CARDS 7 -> 12 is inlined in the pfcls<i> loop
                                               "handleDataEvent(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Ljava/lang/String;)V"},
                                "fields_new": {"LIST_MAX:I"}},
                "ProfileAdminCmd": {"structural": {"<init>()V", "execute(Lcom/hypixel/hytale/server/core/command/system/CommandContext;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/server/core/universe/world/World;)V"}},
                "SkyyProfilesPlugin": {"structural": {"setup()V"}},
                "CfgRows": {"structural": {"<clinit>", "header()[Ljava/lang/Object;"}},      # the row help + kit NOTE texts
                "CfgPub": None,   # the kit's note / version strings - checked loosely below
            }
            cls_ = cc["classes"]
            check(sorted(cc["added"]) == ["AdmBonusCmd", "BonusFn"] and not cc["gone"], "CC: added exactly AdmBonusCmd + BonusFn, none gone: %s %s" % (cc["added"], cc["gone"]))
            unexpected = sorted(c for c in cls_ if c not in plan)
            check(not unexpected, "CC: only planned classes changed - unexpected %s" % dict((c, cls_[c]["structural"] + cls_[c]["const_only"]) for c in unexpected))
            for c, want in plan.items():
                if want is None or c not in cls_:
                    if want is not None:
                        check(False, "CC: %s did not change at all (planned: %s)" % (c, sorted(want["structural"])[:3]))
                    continue
                v = cls_[c]
                got = set(v["structural"]) | set(v["const_only"])
                # the javassist signature of listCount was classCount's in 0.1.8 - accept the rename as new + changed
                extra = sorted(x for x in got - want["structural"] if not x.startswith("listCount("))
                check(not extra and v["same_shape"] and not v["fields_gone"] and set(v["fields_new"]) == want.get("fields_new", set()),
                      "CC %s: only the planned methods / fields changed: extra %s, fields new %s gone %s" % (c, extra, v["fields_new"], v["fields_gone"]))
            print("CC: " + "; ".join("%s %s" % (c, sorted(set(v["structural"]) | set(v["const_only"]))) for c, v in sorted(cls_.items()))[:3000])
        # ---------------------------------------------------------------- Z
        z = child(["--audit", JAR], os.path.join(SCRATCH, "z.json"))
        check(z is not None and not z["refused"] and z["refs"] > 1000, "Z: engine-access audit: %s refs in %s classes, refused %s" % (
            (z or {}).get("refs"), (z or {}).get("classes"), (z or {}).get("refused", [])[:5]))
        # ---------------------------------------------------------------- A + CAP + BON + GATE
        res = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            home = os.path.join(SCRATCH, "cap-" + tag, "Skyy_SkyyProfiles")
            shutil.copytree(LIVE, home)
            res[tag] = child(["--cap", j, "--home", home, "--tag", tag], os.path.join(SCRATCH, "cap-%s.json" % tag)) or {}
            r = res[tag]
            check(r and "error" not in r, "CAP (%s) ran: %s" % (tag, r.get("error", "")[-2500:]))
            check(r and not r.get("load_fails") and r.get("classes", 0) >= 40, "A (%s): %s classes load, verify (-Xverify:all), initialise %s"
                  % (tag, r.get("classes"), r.get("load_fails", [])[:3]))
        n, o = res["new"], res["prev"]
        if n and "error" not in n and o and "error" not in o:
            c = n["cap"]
            exp = {"none": (8, 8, "one per class"), "c15": (8, 8, "one per class"), "c15sb": (8, 8, "one per class"),
                   "c15sham": (8, 8, "one per class"), "c15nine": (9, 9, "one per class"), "twenty": (16, 16, "one per class"),
                   "empty": (8, 8, "one per class"), "fix6": (6, 6, "the limit on this server"), "fix8": (8, 8, "the limit on this server"),
                   "fix1": (1, 1, "the limit on this server"), "fix3_rank2": (3, 5, "the limit on this server + 2 from your rank"),
                   "auto_rank8": (8, 16, "one per class + 8 from your rank"),
                   "fix3_rank2_bonus1": (3, 6, "the limit on this server + 2 from your rank + 1 bonus"),
                   "auto_bonus2": (8, 10, "one per class + 2 bonus"), "auto_bonus0": (8, 8, "one per class"),
                   "auto_bonus_neg": (8, 8, "one per class"), "auto_bonusnull": (8, 8, "one per class"),
                   "clamp16": (8, 16, "one per class + 8 from your rank + 16 bonus"), "bonus_garbage": (8, 8, "one per class"),
                   "bonus_throw": (8, 8, "one per class")}
            for k, (base, cap, why) in exp.items():
                got = c.get(k, {})
                check((got.get("base"), got.get("cap"), got.get("why")) == (base, cap, why), "CAP %s: base %s cap %s why %r (want %s %s %r)" % (
                    k, got.get("base"), got.get("cap"), got.get("why"), base, cap, why))
            check([c[k]["count"] for k in ("none", "c15", "c15sb", "c15sham", "c15nine", "twenty", "empty")] == [8, 8, 8, 8, 9, 28, 8],
                  "CAP classCount = the fallback roster (8) united with class:list, aliases folded: %s" % [c[k]["count"] for k in ("none", "c15", "c15sb", "c15sham", "c15nine", "twenty", "empty")])
            check([c[k]["list"] for k in ("none", "c15", "c15sb", "c15sham", "empty")] == [-1, 7, 8, 9, -1],
                  "CAP listCount = 0.1.8's classCount (class:list only): %s" % [c[k]["list"] for k in ("none", "c15", "c15sb", "c15sham", "empty")])
            check(c["none"]["note"] == "auto = 8 - one per class (SkyyClasses not loaded)" and c["c15"]["note"] == "auto = 8 - one per class (7 playable in SkyyClasses)"
                  and c["fix6"]["note"] == "fixed 6", "CAP capNote: %r %r %r" % (c["none"]["note"], c["c15"]["note"], c["fix6"]["note"]))
            check(c["clamp16"]["bonus"] == 16 and c["auto_bonus_neg"]["bonus"] == 0 and c["auto_bonus2"]["bonus"] == 2, "CAP bonusSlots clamps 0..16")
            check(not n["warned_before"] and n["warned_after_garbage"] and n["warned_after_throw"], "CAP a garbage / throwing bonus hook warns once and counts 0")
            check(n["known"] == ["archer", "warrior", "mage", "berserker", "priest", "assassin", "monk", "spellblade"], "CAP KNOWN = the 8 classes: %s" % n["known"])
            check(n["knownName"] == ["monk", "monk", "monk", "spellblade", "", "monk"], "CAP knownName folds the Shaman aliases: %s" % n["knownName"])
            check(n["limit_max"] == 16 and n["page_max"] == [12, 16], "CAP LIMIT_MAX 16, MAX_CARDS 12, LIST_MAX 16: %s %s" % (n["limit_max"], n["page_max"]))
            oc = o["cap"]
            check(oc["c15"]["cap"] == 7 and oc["none"]["cap"] == 6 and oc["c15"]["why"] == "one per class you can play",
                  "CAP 0.1.8 for comparison: auto = 7 with SkyyClasses 0.1.15, 6 without: %s %s" % (oc["c15"], oc["none"]))
            # roster
            rn, ro = n["roster"], o["roster"]
            sb = lambda cards: [x for x in cards if x[0] == "Spellblade"]
            check(len(rn["none"]) == 8 and sb(rn["none"])[0][6] == "0" and sb(rn["c15"])[0][6] == "0" and sb(rn["c15sb"])[0][6] == "1"
                  and sb(rn["c15sb"])[0][1] == "Bladesong" and sb(rn["none"])[0][1] == "Battlemagic",
                  "ROSTER: the Spellblade card is 'coming later' (with and without SkyyClasses) and becomes pickable when class:list lists it: %s" % sb(rn["c15"]))
            check(rn["c15"][:7] == ro["c15"] and rn["none"][:7] == ro["none"] and rn["c15sb"][:7] == ro["c15sb"][:7],
                  "ROSTER: the other seven cards are 0.1.8's")
            check(len(ro["c15sb"]) == 8 and ro["c15sb"][7][2].startswith("Open /class"), "ROSTER: 0.1.8 showed a Spellblade from class:list only as an unknown extra class")
            # BON
            b = n.get("bon", {})
            str_u1, UUID_O = "00000000-0000-0019-0000-000000000002", "00000000-0000-0019-0000-000000000077"
            check(b.get("get0") == "0" and b.get("cap0") == 8 and not b.get("file_before"), "BON: no bonus = 0, cap 8, no players file written by a read")
            check(b.get("set2") == "2" and b.get("file2") == "2" and b.get("get2") == "2" and b.get("cap2") == 10 and b.get("why2") == "one per class + 2 bonus",
                  "BON: set 2 -> file bonusSlots=2, cap 10, 'one per class + 2 bonus': %s" % b)
            check(b.get("setneg") == "0" and b.get("fileneg") == "<none>" and b.get("set99") == "16" and b.get("file99") == "16" and b.get("cap99") == 16,
                  "BON: -5 clamps to 0 (key removed), 99 to 16 (cap 16)")
            check([b.get(k) for k in ("bad_str", "bad_short", "bad_key", "bad_null", "bad_uuid_pos")] == ["None"] * 5, "BON: bad arguments answer null")
            check(b.get("broken") == "None" and not b.get("broken_file"), "BON: an unreadable players file refuses the set (null, nothing written)")
            check(b.get("bonusOf") == {"-3": 0, "abc": 0, "40": 16, "7": 7, " 2 ": 2, "absent": 0}, "BON: bonusOf parses / clamps: %s" % b.get("bonusOf"))
            check(b.get("live_set") and b.get("live_same_rest") and b.get("live_cap1") == 9 and b.get("live_clear") and b.get("live_back"),
                  "BON: on Skyy's live copy setBonus touches only bonusSlots (cap 8 -> 9), 0 removes it again (file keys back to the original)")
            check(b.get("adm3", "").startswith("+Bonus profile slots for " + str_u1) and ": 16 -> 3. Their limit is now 11 (one per class + 3 bonus)." in b.get("adm3", "")
                  and b.get("adm3_file") == "3", "BON: /profileadmin bonus <uuid> 3: %s" % b.get("adm3"))
            bad = "Bonus slots must be a whole number 0-16 (0 removes them)."
            check([b.get(k) for k in ("adm_bad", "adm_17", "adm_neg", "adm_null")] == [bad] * 4, "BON: /profileadmin bonus refuses x / 17 / -1 / null")
            check(b.get("adm_who") == "Unknown player - use a name (online or seen before) or a uuid.", "BON: unknown player: %s" % b.get("adm_who"))
            check(b.get("adm0", "").startswith("+") and b.get("adm0_file") == "<none>", "BON: /profileadmin bonus <uuid> 0 removes the key")
            check(b.get("adm_live_name", "").startswith("+Bonus profile slots for SkyLordPlayz: ") and LIVE_UUID not in b.get("adm_live_name", "").split(".")[0],
                  "BON/FIX: a player NAME resolves and the reply names them, not the uuid (SkyLordPlayz): %s" % b.get("adm_live_name", "")[:120])
            check(b.get("adm_orphan") == "Unknown player - use a name (online or seen before) or a uuid." and b.get("adm_orphan_file") is False,
                  "FIX: /profileadmin bonus <unknown uuid> 2 is refused and writes no orphan players file: %s file %s" % (b.get("adm_orphan"), b.get("adm_orphan_file")))
            check(b.get("adm_self", "").startswith("+Your bonus profile slots: 0 -> 1. Your limit is now 9 (one per class + 1 bonus).") and b.get("adm_self_file") == "1"
                  and b.get("adm_self0", "").startswith("+Your bonus profile slots: 1 -> 0. Your limit is now 8 (one per class)."),
                  "FIX: in-game step 5 - an admin's own bonus reads 'Your limit is now 9' (and back to 8; a uuid + other-case name also counts as self): %s | %s" % (b.get("adm_self", "")[:90], b.get("adm_self0", "")[:90]))
            cm = n.get("cmds", {})
            check(cm.get("bonus_name") == "bonus" and cm.get("bonus_perm") == "skyyprofiles.admin" and cm.get("admin_bonus") == "AdmBonusCmd"
                  and cm.get("admin_setclass") == "ok", "BON: /profileadmin bonus is wired (name, skyyprofiles.admin, a sub-command of /profileadmin): %s" % cm)
            lb = b.get("log_bonus", [])
            check(len([x for x in lb if "(bridge)" in x]) == 3 and len([x for x in lb if "by Tester" in x]) == 3
                  and any("(SkyLordPlayz) " in x for x in lb) and not any(UUID_O in x for x in lb),
                  "BON: switches.log has a BONUS line per bridge change (3; an unchanged value is not logged) and per command (3; with the name; none for the refused unknown uuid): %s" % lb)
            # GATE
            g, go = n.get("gate", {}), o.get("gate", {})
            busy, full8, full7 = "A profile switch is already running.", "All 8 profile slots are used.", "All 7 profile slots are used."
            check(g.get("six_count") == 6 and g.get("six_cap") == 8 and g.get("six_gate") == busy and g.get("make7", [0, 0])[1]
                  and g.get("seven_gate") == busy and g.get("make8", [0, 0])[1] and g.get("eight_count") == 8 and g.get("eight_gate") == full8,
                  "GATE: 6 profiles -> #7 and #8 pass the limit, the 9th is refused (%s)" % dict((k, g.get(k)) for k in ("six_cap", "six_gate", "seven_gate", "eight_gate")))
            check(g.get("eight_bonus_gate") == busy and g.get("make9", [0, 0])[1] and g.get("nine_gate") == "All 9 profile slots are used."
                  and g.get("nine_why") == "one per class + 1 bonus" and g.get("del") and g.get("after_del_gate") == busy,
                  "GATE: 1 bonus slot lets the 9th through, the 10th is refused; a deleted profile frees its slot: %s" % dict((k, g.get(k)) for k in ("eight_bonus_gate", "nine_gate", "nine_why", "after_del_gate")))
            check(g.get("live_count") == 7 and g.get("live_cap") == 8 and g.get("live_gate") == busy and go.get("live_gate") == full7,
                  "GATE: Skyy's live copy (7 profiles): 0.1.9 lets #8 through, 0.1.8 refused it: %s / %s" % (g.get("live_gate"), go.get("live_gate")))
            check(go.get("seven_gate") == full7, "GATE: 0.1.8 refused the 8th (comparison): %s" % go.get("seven_gate"))
            check(g.get("shown") == [str(i) for i in range(1, 16)] and go.get("shown") == [str(i) for i in range(1, 9)],
                  "GATE: shownIds draws 12 live + 3 deleted (0.1.8: the first 8): %s" % g.get("shown"))
        # ---------------------------------------------------------------- PG
        pgh = os.path.join(SCRATCH, "pg-live")
        shutil.copytree(LIVE, pgh)
        pg = child(["--pg", JAR, "--home", pgh], os.path.join(SCRATCH, "pg.json"))
        check(pg is not None, "PG: the page child ran")
        if pg:
            pages = page_checks(pg)
            P = lambda k: pages.get(k, {"cards": -1, "texts": {}, "events": []})
            check(P("list live skyy")["cards"] == 8 and any("7 of 8 profile slots used (one per class)." in v for v in txt(P("list live skyy"), "SkyyPfFoot")),
                  "PG live: Skyy's 7 profiles + Create new; footer '7 of 8 profile slots used (one per class).': %s" % txt(P("list live skyy"), "SkyyPfFoot"))
            check(P("list six")["cards"] == 7 and P("list eight full")["cards"] == 8 and P("list seven pending")["cards"] == 8,
                  "PG: 6 profiles + Create new = 7 cards; 7 + Create new = 8; 8 profiles = 8 (no Create new)")
            check('"a":"pfnew"' in "".join(P("list seven pending")["events"]).replace(" ", "") and '"a":"pfnew"' not in "".join(P("list eight full")["events"]).replace(" ", ""),
                  "PG: Create new is offered at 7 of 8, not at 8 of 8")
            check(P("list nine bonus")["cards"] == 10 and any("9 of 10 profile slots used (one per class + 2 bonus)." in v for v in txt(P("list nine bonus"), "SkyyPfFoot")),
                  "PG: 9 profiles + 2 bonus = 9 cards + Create new (the list scrolls): %s" % txt(P("list nine bonus"), "SkyyPfFoot"))
            check(P("list sixteen")["cards"] == 16 and any("2 more deleted" in v for v in txt(P("list sixteen"), "SkyyPfFoot")),
                  "PG: 18 profiles (2 deleted), bonus 8 -> 16 cards drawn, the rest named in the footer: %s" % txt(P("list sixteen"), "SkyyPfFoot"))
            check(any("8 profiles - this server now allows 6." in v for v in txt(P("list fixed six of eight"), "SkyyPfFoot")),
                  "PG: a fixed 6 below 8 profiles keeps them all (footer)")
            ce = P("create eight classes")
            check(ce["cards"] == 8 and "Spellblade - coming later" in ce["texts"].values() and any("This is profile 7 of 8 - one per class." == v for v in txt(ce, "SkyyPfSlots")),
                  "PG create: 8 class cards (the Spellblade 'coming later'), 'This is profile 7 of 8 - one per class.': %s" % txt(ce, "SkyyPfSlots"))
            check(sum(1 for e in ce["events"] if '"pfcls' in e) == 7 and not any('"pfcls7"' in e for e in ce["events"]),
                  "PG create: 7 Select bindings (pfcls0-6), none for the Spellblade")
            check(P("create spellblade later")["texts"].get("SkyyPfInfo") == "Spellblade is coming later.", "PG create: the coming-later info line")
            c9 = P("create nine classes")
            check(c9["cards"] == 9 and any("This is profile 7 of 9 - one per class." == v for v in txt(c9, "SkyyPfSlots"))
                  and "Necromancer - selected" in c9["texts"].values() and sum(1 for e in c9["events"] if '"pfcls' in e) == 7,
                  "PG create: a 9th class from SkyyClasses = 9 cards (scrolls), limit 9, the 9th selectable (selected here): %s" % txt(c9, "SkyyPfSlots"))
            c13 = P("create thirteen classes")
            check(c13["cards"] == 12 and any("This is profile 7 of 14 - one per class." == v for v in txt(c13, "SkyyPfSlots")),
                  "PG create: 14 classes -> the first 12 cards drawn (MAX_CARDS; warnHidden), limit 14: %s %s" % (c13["cards"], txt(c13, "SkyyPfSlots")))
            check(P("create first")["cards"] == 8 and P("create first no classes mod")["cards"] == 8, "PG create first: 8 cards with and without SkyyClasses")
            check(any("All 8 profile slots are used - you cannot create another profile." == v for v in txt(P("create full"), "SkyyPfSlots")),
                  "PG create full: %s" % txt(P("create full"), "SkyyPfSlots"))
            check(any("This is profile 9 of 9 - one per class + 1 bonus." == v for v in txt(P("create bonus ninth"), "SkyyPfSlots")),
                  "PG create + 1 bonus: %s" % txt(P("create bonus ninth"), "SkyyPfSlots"))
            so = P("create spellblade on")
            check("Spellblade - selected" in so["texts"].values() and any('"pfcls7"' in e for e in so["events"]) is False,
                  "PG create: once SkyyClasses lists the Spellblade it can be selected (selected card shown)")
        # ---------------------------------------------------------------- ST (two starts on the live copy, both jars)
        T = t15()
        st = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            home = os.path.join(SCRATCH, "st-" + tag, "Skyy_SkyyProfiles")
            shutil.copytree(LIVE, home)
            h0 = T.all_hashes(home)
            runs = [child(["--st", j, "--home", home], os.path.join(SCRATCH, "st-%s-%d.json" % (tag, k))) for k in (1, 2)]
            st[tag] = runs
            check(all(runs) and h0 == T.all_hashes(home), "ST (%s): two starts on the live copy change nothing: %s" % (
                tag, sorted(set(h0.items()) ^ set(T.all_hashes(home).items()))[:4]))
        if all(st["new"]) and all(st["prev"]):
            a, b = st["new"], st["prev"]
            check(a[0] == a[1] and a[0]["describe"].endswith("| slots 7/8") and b[0]["describe"].endswith("| slots 7/6")
                  and a[0]["describe"].rsplit("|", 1)[0] == b[0]["describe"].rsplit("|", 1)[0] and a[0]["key"] == b[0]["key"],
                  "ST: both starts read Skyy's 7 profiles like 0.1.8; slots 7/8 (0.1.8 without SkyyClasses: 7/6): %s" % a[0]["describe"][-60:])
            check(a[0]["capm"] is None and a[0]["up"] is None and "maxProfiles=auto (auto = 8 - one per class (SkyyClasses not loaded))" in a[0]["summary"],
                  "ST: no migration runs (cap-auto marker present, the row stays auto): %s" % a[0]["summary"][:120])
        # ---------------------------------------------------------------- KEEP: hand-edited caps kept, a new server
        for nm_, edit, want in (("five", "maxProfiles=5", "maxProfiles=5 (fixed 5)"), ("six", "maxProfiles=6", "maxProfiles=6 (fixed 6)"),
                                ("twelve", "maxProfiles=12", "maxProfiles=8 (fixed 8)")):
            seen = {}
            for tag, j in (("new", JAR), ("prev", PREV_JAR)):
                home = os.path.join(SCRATCH, "keep-%s-%s" % (nm_, tag), "Skyy_SkyyProfiles")
                shutil.copytree(LIVE, home)
                cf = os.path.join(home, "config.properties")
                raw = open(cf, "rb").read()
                nl = b"\r\n" if b"\r\n" in raw else b"\n"
                raw2 = raw.replace(b"maxProfiles=auto" + nl, edit.encode() + nl)
                check(raw2 != raw, "KEEP %s: the live copy had maxProfiles=auto to edit" % nm_)
                open(cf, "wb").write(raw2)
                h0 = T.all_hashes(home)
                runs = [child(["--st", j, "--home", home], os.path.join(SCRATCH, "keep-%s-%s-%d.json" % (nm_, tag, k))) for k in (1, 2)]
                after = T.all_hashes(home)
                seen[tag] = (runs, open(cf, "rb").read(), sorted(k for k in set(h0) | set(after) if h0.get(k) != after.get(k)))
                if nm_ != "twelve":
                    check(all(runs) and h0 == after and open(cf, "rb").read() == raw2,
                          "KEEP %s (%s): two starts leave the hand-edited file byte for byte" % (nm_, tag))
                if tag == "new" and all(runs):
                    check(runs[0]["summary"].startswith(want) and runs[0]["capm"] is None, "KEEP %s: runs as %r: %s" % (nm_, want, runs[0]["summary"][:80]))
            if nm_ == "twelve":
                (rn_, fn_, dn_), (ro_, fo_, do_) = seen["new"], seen["prev"]
                check(all(rn_) and all(ro_) and fn_ == fo_ and dn_ == do_
                      and [r["summary"].split(" ", 1)[0] for r in rn_] == [r["summary"].split(" ", 1)[0] for r in ro_],
                      "KEEP twelve: an out-of-range hand edit is handled exactly like 0.1.8 (files touched %s, 0.1.8 %s)" % (dn_, do_))
                print("KEEP twelve: files touched (both versions): %s; config now %s" % (
                    dn_, [ln for ln in fn_.decode("latin-1").splitlines() if ln.startswith("maxProfiles")]))
        home = os.path.join(SCRATCH, "fresh", "Skyy_SkyyProfiles")
        os.makedirs(home)
        runs = [child(["--st", JAR, "--home", home], os.path.join(SCRATCH, "fresh-%d.json" % k)) for k in (1, 2)]
        cfg = props(os.path.join(home, "config.properties"))
        text = open(os.path.join(home, "config.properties"), encoding="utf8").read() if os.path.isfile(os.path.join(home, "config.properties")) else ""
        check(all(runs) and cfg.get("maxProfiles") == "auto" and "one per class in the game (8 with the Spellblade" in text and "6 without SkyyClasses" not in text,
              "NEW server: config.properties starts with maxProfiles=auto and the new comment")
        if all(runs):
            check("maxProfiles=auto (auto = 8 - one per class (SkyyClasses not loaded))" in runs[0]["summary"] and runs[0]["describe"] == "no profiles yet",
                  "NEW server: auto = 8: %s" % runs[0]["summary"][:100])
            mk = props(os.path.join(home, "cap-auto.properties"))
            check(mk.get("result") == "new" and mk.get("version") == VERSION, "NEW server: the 0.1.4 marker says new (no migration): %s" % mk)
        if all(runs):
            check("one profile per class of the game" in str(runs[0].get("capm")) and "a player can pick" not in str(runs[0].get("capm")),
                  "FIX/MIG new: the 'no config yet' migration note says one profile per class of the game: %s" % runs[0].get("capm"))
        # ---------------------------------------------------------------- MIG (fixer): capMigrate EXECUTED on the two rewrite paths
        import ast
        src_ = open(SCRIPT, encoding="utf8").read()
        m_ = re.search(r"^CFG_LINES_011 = (\[.*?\n\])\n", src_, re.M | re.S)
        check(m_ is not None, "MIG: CFG_LINES_011 found in the build script")
        if m_:
            old011 = ast.literal_eval(m_.group(1))
            for nm_, body in (("default", ("\n".join(old011) + "\n").encode("utf8")),
                              ("line", ("# an owner's own comment\n" + "\n".join(old011) + "\n").encode("utf8"))):
                home = os.path.join(SCRATCH, "mig-" + nm_, "Skyy_SkyyProfiles")
                os.makedirs(home)
                open(os.path.join(home, "config.properties"), "wb").write(body)
                rr = child(["--st", JAR, "--home", home], os.path.join(SCRATCH, "mig-%s.json" % nm_)) or {}
                note = str(rr.get("capm"))
                mk = props(os.path.join(home, "cap-auto.properties"))
                cfgm = props(os.path.join(home, "config.properties"))
                check(mk.get("result") == nm_ and cfgm.get("maxProfiles") == "auto"
                      and "8 with the Spellblade, also without SkyyClasses" in note and "6 without SkyyClasses" not in note
                      and "6 without SkyyClasses" not in mk.get("note", ""),
                      "FIX/MIG %s: maxProfiles 6 -> auto and the one-time note says 8 (not '6 without SkyyClasses'): %s | %s" % (nm_, mk.get("result"), note[:200]))
        check(snap(LIVE) == live_before, "the live Skyy_SkyyProfiles folder was never written (only read + copied)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyProfiles %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
