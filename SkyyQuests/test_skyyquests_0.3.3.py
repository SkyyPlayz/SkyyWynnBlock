"""SkyyQuests 0.3.3 harness (STARTER-FLOW FIXES: early progress on chain lines + the cascade, logs + stone + copper merged into one tutorial
task with saved progress folded, progress cards with their count; tools/quests_0_3_3_patch.py) on top of the 0.3.2 harness
(test_skyyquests_0.3.2.py -> 0.3.1 -> 0.3: every older phase runs again on the 0.3.3 jar). tools/harness_kit.py phases, fresh child JVMs
(-Xverify:all).

    python SkyyQuests/test_skyyquests_0.3.3.py [--jar SkyyQuests-0.3.3.jar] [--dir <scratch>] [--keep]

  A / C / AA  verify, class compare 0.3.2 -> 0.3.3, engine-access audit
  M     merge   EXECUTED on the shipped 0.3.3 tutorial (written fresh by QDefs.load): 24 tasks, task 3 = "Gather logs, stone and copper"
                (before the crafting accessory; felled OR broken logs = the alt group, 10 stone, 5 copper, was=mine_basics:2); logs alone /
                stone alone / copper alone never finish it; the three finish it and pay BOTH old rewards once (coins paid, items waiting,
                issued.tutorial.chop_logs + issued.tutorial.mine_basics, grants under each old key); felled logs work as the log part; with
                SkyyGear's caller the lifelong-tools part is needed too; the log page reward text names both rewards; rows "k/n"
                FEED: a progress card carries "<task>: <label> n / goal" + the block id as its icon, ONE card per event (the widget's line
                first: the merged task while its stone part counts, then "Mine 64 stone 11 / 64"), a kill card has its count too
                FOLD (players/*.properties written the 0.3.2 way, read by QStore.read): both done -> done, nothing new; only chop_logs done
                -> REOPENED with the logs kept, stone + copper then pay ONLY mine_basics' reward; only mine_basics done -> the logs pay
                ONLY chop_logs' reward; counts in the middle carried (higher wins); a second fold changes nothing; /questadmin reload folds
                cached profiles (QIO mode 5); an edited tutorial file that still has mine_basics folds nothing (0.3.2 behaviour)
  CH    chain   EARLY PROGRESS + CASCADE on a chain line: a later break / kill step counts before it is active (want bits too), a talk
                step does NOT (no bit, nothing counted), finishing step 1 completes the already-met step 2 at once (both claims, both
                Done cards, in order), a skipped step does not block; an open line is unchanged; the daily board unchanged (phase B)
  FX    (in M / CH) the REVIEW FIXES: one talk never finishes two talk steps (A talk, B early-met, C talk: one talk = A + B, the 2nd
                talk = C); an early-counted step sends no card until it is active; an alt group's card shows its best member (felled 6 +
                broken 1 = "logs 6 / 10"); a card whose key is no item (kills) is sent at most once per task per 5 s, an item card every
                event; the fold runs once (folded.<line>.<task>; an admin undo stays undone after a reload); the reward help names the merge
  MT    migt    the ONE-TIME tutorial file update: the 0.2 shipped bytes -> 0.3.3 + tutorial.properties.0.2.bak (= the old bytes); the
                0.1 bytes -> 0.3.3 + .0.1.bak; an edited file KEPT + .0.3.3.new once (a 2nd start does not rewrite it); a 0.3.3 file
                (the marker) untouched; a backup that cannot be written = nothing changed
  ISL SND D E L P K S N B F   every 0.3.2 phase on the 0.3.3 jar with an EDITED 0.2 tutorial file in place (the "owner kept his
                file" path = 0.3.2 behaviour); the few checks that test what 0.3.3 changes on purpose are WAIVED by name (listed)
  ST    live    START TWICE on a scratch COPY of the live Skyy_SkyyQuests: start 1 updates quests/tutorial.properties (the live file IS
                the 0.2 shipped text) + writes tutorial.properties.0.2.bak = the old bytes, nothing else; start 2 writes nothing;
                every live profile loads, folds (both old tasks done -> the merged task done, nothing paid) and keeps every key
Scratch: tools/dev/scratch/start033fix/quests (deleted unless --keep). Exit 1 on any failure.
"""
import os, sys, shutil, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "start033fix", "quests")]
_spec = importlib.util.spec_from_file_location("test_skyyquests_0_3_2", os.path.join(HERE, "test_skyyquests_0.3.2.py"))
T032 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T032)
T031 = T032.T031
T03 = T032.T03

VERSION = "0.3.3"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyQuests-0.3.2.jar")
SCRATCH = T03.SCRATCH
FAKE_DIR = T03.FAKE_DIR
PKG = T03.PKG
TB = T03.TB
EXPECT = {
    "QDefs": ["+f TUTORIAL02", "+m rewardFor", "+m rewardWas", "+m rewardAll", "~<clinit>", "~m migrateTut", "~m part", "~m parse", "~m rewardOf"],
    "QPart": ["+f alt", "+f label", "~c "],
    "QTask": ["+f was", "+f wasAt", "+f wasReward", "~c "],
    "QState": ["+m fold", "+m foldMe", "+m cascade", "+m tracked"],
    "QStore": ["~m read"],
    "QIO": ["~m run"],
    "QEng": ["+m issueL", "+m completeOneL", "+m cascadeL", "+m cardText", "+m cardIcon", "+m cardItem", "+f CARD_LAST", "+f CARD_GAP_MS", "+f CARD_ITEMS", "~<clinit>", "~m completeL", "~m satisfied", "~m progL",
             "~m applyL", "~m reachL", "~m wantL", "+m notifyProgress", "-m notifyProgress", "~m after", "~m action"],
    "QLogPage": ["~m build"],
    "CfgRows": ["~<clinit>", "~m header"],      # 0.3.3 FIX: the reward table help text
    "CfgFn": ["~m opExport"],
    "SkyyQuestsPlugin": ["~m setup"],
}
ADDED = []

# ---------------------------------------------------------------------------------------------------- the older phases: legacy file + waivers
# The older phases ran on the shipped tutorial; 0.3.3 ships the merged one. They run here with an EDITED copy of the 0.2 tutorial in place
# (the "owner kept his file" path, which must behave exactly like 0.3.2). Checks that test what 0.3.3 changes ON PURPOSE are waived by name.
LEGACY = [False]
WAIVE = (
    "MIG-T the migrated file loads: 25 tasks",         # an untouched 0.1 file now becomes the 0.3.3 tutorial = 24 tasks (checked in M / MT)
    "MIG-T an INFO line names the update",             # its INFO line says "updated to the 0.3.3 tutorial" (checked in MT / ST)
    "N1 progress -> feed:fn:push",                     # the progress card now carries its count: "Defeat 5 mobs 1 / 5" (checked in M)
)
WAIVED = []
_orig_check = HK.Child.check


def _check(self, cond, what):
    if not cond and LEGACY[0] and str(what).startswith(WAIVE):
        WAIVED.append(str(what))
        self.notes.append("WAIVED (0.3.3 changed this on purpose): %s" % str(what)[:160])
        return cond
    return _orig_check(self, cond, what)


HK.Child.check = _check
_orig_start = T03.Env.start


def _start(self):
    if LEGACY[0]:
        tf = os.path.join(self.base, "quests", "tutorial.properties")
        if not os.path.isfile(tf):
            os.makedirs(os.path.dirname(tf), exist_ok=True)
            txt = str(self.P("QDefs").TUTORIAL02) + "# kept by the server owner (an edited 0.2 file - the 0.3.3 harness)\n"
            open(tf, "wb").write(txt.encode("utf-8"))
    return _orig_start(self)


T03.Env.start = _start


def _mapnew():
    """0.3.3 writes tutorial.properties.0.3.3.new beside an edited file where 0.2 wrote .0.2.new: the old MIG-T check reads the new name
    (its own test - "the text written beside it carries 'Shipped by SkyyQuests 0.2' once" - holds for the 0.3.3 text too)"""
    import builtins
    o_open, o_mt = builtins.open, os.path.getmtime

    def m(pth):
        ps = str(pth)
        if ps.endswith("tutorial.properties.0.2.new") and not os.path.exists(ps):
            return ps[:-len("0.2.new")] + "0.3.3.new"
        return pth
    builtins.open = lambda f, *a, **k: o_open(m(f), *a, **k)
    os.path.getmtime = lambda f: o_mt(m(f))


def legacy(fn):
    def w(out, jar, scratch, home):
        LEGACY[0] = True
        _mapnew()
        try:
            return fn(out, jar, scratch, home)
        finally:
            if WAIVED:
                print("waived in this phase (%d): %s" % (len(WAIVED), "; ".join(x[:90] for x in WAIVED)))
    return w


def claims(s):
    return [str(x) for x in s.claims]


# ---------------------------------------------------------------------------------------------------- M: the merged task + fold + cards
def run_merge(out, jar, scratch, home):
    from jpype import JClass, JObject, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, FAKE_DIR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    PyFn = T03.fn_class()
    Boolean, Long = JClass("java.lang.Boolean"), JClass("java.lang.Long")
    X = T03.scene3(K, scratch, "m")
    Eng, Defs, Sto, St = X.Eng, X.Defs, X.Sto, X.St
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    br.put("coins:fn:add", PyFn(lambda a: Long(1)))
    feeds = []
    br.put("feed:fn:push", PyFn(lambda a: feeds.append((str(a[3]), None if a[2] is None else str(a[2]))) or Boolean.TRUE))
    W = "skyy-island-a1"
    L = X.L
    tf = os.path.join(X.base, "quests", "tutorial.properties")
    txt = open(tf, "rb").read().decode("utf-8")
    K.check("updated by 0.3.3" in txt and txt == str(Defs.TUTORIAL), "M a fresh server writes the 0.3.3 tutorial")
    ids = [str(t.id) for t in L.tasks]
    K.check(str(L.id) == "tutorial" and len(ids) == 24 and "mine_basics" not in ids and ids.index("chop_logs") == 2 and ids.index("first_accessory") == 3,
            "M 24 tasks; chop_logs is task 3, BEFORE the crafting accessory; mine_basics gone: %s" % ids[:5])
    t3 = L.tasks[2]
    K.eq((str(t3.name), bool(t3.any), int(len(t3.parts)), str(t3.was), int(t3.wasAt)), ("Gather logs, stone and copper", False, 5, "mine_basics", 2),
         "M the merged task: name, all parts, 5 parts, was=mine_basics:2")
    K.eq([(str(p_.tname), str(p_.match), int(p_.count), str(p_.alt), str(p_.label)) for p_ in t3.parts],
         [("felled", "Wood_*_Trunk*", 10, "logs", "logs"), ("break", "Wood_*_Trunk", 10, "logs", "logs"), ("break", "Rock_Stone", 10, "", "stone"),
          ("break", "Ore_Copper*", 5, "", "copper ore"), ("bridge", "fn:gear:fn:lifelong", 1, "", "")], "M the parts (the old amounts)")
    K.eq(str(Defs.rewardAll(L, t3)), "coins:25,item:Plant_Sapling_Oak:2,coins:25,item:Ingredient_Bar_Copper:3", "M rewardAll = both old rewards (table rows chop_logs + mine_basics)")
    K.check(not list(Defs.PROBLEMS), "M no line problems: %s" % [str(x) for x in Defs.PROBLEMS])
    # ---- one requirement each: logs alone, stone alone, copper alone never finish it
    u, p, s = X.player(1)
    for i in range(10):
        Eng.count(u, TB["break"], "Wood_Oak_Trunk", 1, W, False)
    K.check(not X.done(s, "chop_logs") and X.rows(s)["chop_logs"] == ("open", "1/3"), "M 10 trunk breaks = the log group met, task 1/3: %s" % (X.rows(s)["chop_logs"],))
    c1 = [f for f in feeds if "Gather" in f[0]]
    K.check(("Gather logs, stone and copper: logs 9 / 10", "Wood_Oak_Trunk") in c1 and c1[-1] == ("Gather logs, stone and copper: logs 10 / 10", "Wood_Oak_Trunk") and len(c1) == 10,
            "M FEED: each trunk = ONE card with its count + the block icon (10 cards, not one per line that moved): %s" % c1[-2:])
    for i in range(10):
        Eng.count(u, TB["break"], "Rock_Stone", 1, W, False)
    K.check(not X.done(s, "chop_logs") and X.rows(s)["chop_logs"] == ("open", "2/3"), "M + 10 stone: 2/3, not done")
    st = [f for f in feeds if f[1] == "Rock_Stone"]
    K.check(("Gather logs, stone and copper: stone 4 / 10", "Rock_Stone") in st and not [f for f in st[:9] if "Mine 64" in f[0]],
            "M FEED: while the merged stone part counts, its card wins over the Mining line's 'Mine 64 stone' (ONE card per event): %s" % st[:3])
    n0 = len(feeds)
    Eng.count(u, TB["break"], "Rock_Stone", 1, W, False)
    K.eq(feeds[n0:], [("Mine 64 stone 11 / 64", "Rock_Stone")], "M FEED: the merged part met -> the next stone is the Mining line's card '11 / 64' (its count from the start)")
    K.check(not [f for f in feeds if " x" in f[0]], "M FEED: no xN in our texts")
    for i in range(4):
        Eng.count(u, TB["break"], "Ore_Copper_Stone", 1, W, False)
    K.check(not X.done(s, "chop_logs"), "M 4 copper: not yet")
    Eng.count(u, TB["break"], "Ore_Copper_Stone", 1, W, False)
    K.check(X.done(s, "chop_logs"), "M 5 copper: DONE (the lifelong-tools part is coming soon without SkyyGear's caller)")
    lg = T03.logtext(X.base)
    gc = "coins|25|%s:tutorial.chop_logs:1" % u
    gm = "coins|25|%s:tutorial.mine_basics:3" % u
    K.check(lg.count("PAID %s %s" % (u, gc)) == 1 and lg.count("PAID %s %s" % (u, gm)) == 1, "M BOTH coin rewards paid once, under each old key: %s" % lg[-400:])
    K.eq(claims(s), ["item|Plant_Sapling_Oak:2|%s:tutorial.chop_logs:2" % u, "item|Ingredient_Bar_Copper:3|%s:tutorial.mine_basics:4" % u],
         "M BOTH item rewards waiting (no world in a bare JVM)")
    K.check(bool(s.issued.contains("tutorial.chop_logs")) and bool(s.issued.contains("tutorial.mine_basics")), "M issued both old keys")
    K.check(("Done: Gather logs, stone and copper", None) in feeds, "M the Done card")
    rec = s.recent.get("tutorial.chop_logs")
    K.check(rec is not None and "Sapling" in str(rec[1]) and "Copper" in str(rec[1]), "M the widget's Done! text names both rewards: %s" % (None if rec is None else str(rec[1])))
    # ---- felled logs work as the log part; a kill card has its count
    u2, p2, s2 = X.player(2)
    Eng.count(u2, TB["felled"], "Wood_Birch_Trunk", 10, W, False)
    for i in range(10):
        Eng.count(u2, TB["break"], "Rock_Stone", 1, W, False)
    Eng.count(u2, TB["break"], "Ore_Copper_Stone", 5, W, False)
    K.check(X.done(s2, "chop_logs"), "M 10 FELLED logs + stone + copper = done (alt group: felled OR broken)")
    u4, p4, s4 = X.player(4)
    Eng.count(u4, TB["felled"], "Wood_Oak_Trunk", 6, W, False)
    n0 = len(feeds)
    Eng.count(u4, TB["break"], "Wood_Oak_Trunk", 1, W, False)
    K.eq(feeds[n0:], [("Gather logs, stone and copper: logs 6 / 10", "Wood_Oak_Trunk")],
         "M FIX alt group: 6 felled + 1 broken -> the card shows the BEST member (6 / 10, the tracker's number), not the broken part's 1")
    n0 = len(feeds)
    Eng.count(u2, TB["kill"], "Trork_Grunt", 1, W, False)
    K.eq(feeds[n0:], [("Defeat 5 mobs 1 / 5", "Trork_Grunt")], "M FEED: a kill card carries its count (a bare JVM has no item map: trusted)")
    HashSet = JClass("java.util.HashSet")
    its = HashSet()
    its.add("Rock_Stone")
    Eng.CARD_ITEMS = its                       # = the game: Rock_Stone is an item, Trork_Grunt is not
    n0 = len(feeds)
    Eng.count(u2, TB["kill"], "Trork_Grunt", 1, W, False)
    Eng.count(u2, TB["kill"], "Trork_Grunt", 1, W, False)
    K.eq(feeds[n0:], [("Defeat 5 mobs 2 / 5", None)], "M FIX a kill (no item icon): ONE card while it is on screen (the 2nd kill within 5 s sends none), no icon")
    ck_ = "%s|tutorial.%s" % (u2, [str(t_.id) for t_ in L.tasks if str(t_.name) == "Defeat 5 mobs"][0])
    K.check(Eng.CARD_LAST.get(ck_) is not None, "M FIX ... the throttle key is uuid|line.task")
    Eng.CARD_LAST.put(ck_, Long(Eng.CARD_LAST.get(ck_).longValue() - 6000))
    n0 = len(feeds)
    Eng.count(u2, TB["kill"], "Trork_Grunt", 1, W, False)
    K.eq(feeds[n0:], [("Defeat 5 mobs 4 / 5", None)], "M FIX ... 5 s later the next kill sends its card with the true count")
    u5, p5, s5 = X.player(5)
    n0 = len(feeds)
    for i in range(3):
        Eng.count(u5, TB["break"], "Rock_Stone", 1, W, False)
    K.eq([f for f in feeds[n0:] if f[1] == "Rock_Stone"], [("Gather logs, stone and copper: stone %d / 10" % i, "Rock_Stone") for i in (1, 2, 3)],
         "M FIX an item card (Rock_Stone) is sent on EVERY event (SkyyHud merges it on the icon)")
    Eng.CARD_ITEMS = None
    # ---- SkyyGear's caller: the lifelong part is needed too
    br.put("quest:caller:gearlife", Boolean.TRUE)
    u3, p3, s3 = X.player(3)
    Eng.count(u3, TB["break"], "Wood_Oak_Trunk", 10, W, False)
    Eng.count(u3, TB["break"], "Rock_Stone", 10, W, False)
    Eng.count(u3, TB["break"], "Ore_Copper_Stone", 5, W, False)
    K.check(not X.done(s3, "chop_logs") and X.rows(s3)["chop_logs"][1] == "3/4", "M with quest:caller:gearlife the lifelong part counts: 3/4, not done (%s)" % (X.rows(s3)["chop_logs"],))
    br.remove("quest:caller:gearlife")
    # ---- FOLD: profiles written the 0.3.2 way
    pdir = os.path.join(X.base, "players")
    os.makedirs(pdir, exist_ok=True)
    U = JClass("java.util.UUID")

    def load(n, body):
        uu = U(0x7777, n)
        open(os.path.join(pdir, "%s.properties" % uu), "w", newline="\n").write("v=1\nseq=4\n" + body)
        return uu, Sto.read(str(uu), uu)
    BOTH = ("done.tutorial.chop_logs=1\ndone.tutorial.mine_basics=2\nprog.tutorial.chop_logs.0=10\nprog.tutorial.chop_logs.1=3\npdone.tutorial.chop_logs.0=1\n"
            "prog.tutorial.mine_basics.0=10\nprog.tutorial.mine_basics.1=5\nprog.tutorial.mine_basics.2=1\npdone.tutorial.mine_basics.0=1\n"
            "pdone.tutorial.mine_basics.1=1\npdone.tutorial.mine_basics.2=1\nissued.tutorial.chop_logs=1\nissued.tutorial.mine_basics=1\n")
    ua, sa = load(1, BOTH)      # = Skyy's live p9 profile
    K.check(X.done(sa, "chop_logs") and [str(sa.prog.get("tutorial.chop_logs.%d" % i)) for i in range(5)] == ["10", "3", "10", "5", "1"]
            and all(bool(sa.pdone.contains("tutorial.chop_logs.%d" % i)) for i in (0, 2, 3, 4)) and claims(sa) == [],
            "FOLD both old tasks done: the merged task is done, the counts carried, nothing new to pay")
    K.check(bool(sa.done.containsKey("tutorial.mine_basics")) and str(sa.prog.get("tutorial.mine_basics.0")) == "10", "FOLD the old keys stay (a rollback finds them)")
    K.check(not bool(St.fold(sa)), "FOLD a second fold changes nothing")
    ub, sb = load(2, "done.tutorial.chop_logs=1\nprog.tutorial.chop_logs.1=10\npdone.tutorial.chop_logs.1=1\nissued.tutorial.chop_logs=1\nprog.tutorial.mine_basics.0=4\n")
    K.check(not X.done(sb, "chop_logs") and bool(sb.pdone.contains("tutorial.chop_logs.1")) and str(sb.prog.get("tutorial.chop_logs.2")) == "4" and bool(sb.issued.contains("tutorial.chop_logs")),
            "FOLD only 'Chop 10 logs' done: the merged task REOPENS (logs kept as met, the 4 stone carried, issued kept)")
    pb = X.QP(ub, None); pb.pk = str(ub); pb.world = W; pb.loaded = True
    Eng.PLAYERS.put(ub, pb)
    Sto.CACHE.put(str(ub), sb)
    Eng.rebuild(ub, sb)
    Eng.count(ub, TB["break"], "Rock_Stone", 6, W, False)
    Eng.count(ub, TB["break"], "Ore_Copper_Stone", 5, W, False)
    K.check(X.done(sb, "chop_logs"), "FOLD ... 6 more stone + 5 copper finish it")
    lg = T03.logtext(X.base)
    K.check(("%s:tutorial.mine_basics:" % ub) in lg and ("%s:tutorial.chop_logs:" % ub) not in lg and claims(sb) == ["item|Ingredient_Bar_Copper:3|%s:tutorial.mine_basics:6" % ub],
            "FOLD ... and pay ONLY mine_basics' reward (chop_logs was paid before): %s / %s" % (claims(sb), [l_ for l_ in lg.splitlines() if str(ub) in l_]))
    uc, sc = load(3, "done.tutorial.mine_basics=1\nissued.tutorial.mine_basics=1\nprog.tutorial.chop_logs.0=6\n")
    K.check(not X.done(sc, "chop_logs") and all(bool(sc.pdone.contains("tutorial.chop_logs.%d" % i)) for i in (2, 3, 4)) and str(sc.prog.get("tutorial.chop_logs.2")) == "10",
            "FOLD only 'Mine stone and copper' done: its parts count as met (even without part lines)")
    pc = X.QP(uc, None); pc.pk = str(uc); pc.world = W; pc.loaded = True
    Eng.PLAYERS.put(uc, pc)
    Sto.CACHE.put(str(uc), sc)
    Eng.rebuild(uc, sc)
    Eng.count(uc, TB["felled"], "Wood_Oak_Trunk", 4, W, False)
    K.check(X.done(sc, "chop_logs") and claims(sc) == ["item|Plant_Sapling_Oak:2|%s:tutorial.chop_logs:6" % uc] and ("%s:tutorial.mine_basics:" % uc) not in T03.logtext(X.base),
            "FOLD ... 4 more felled logs (6 + 4) finish it and pay ONLY chop_logs' reward: %s" % claims(sc))
    ud, sd = load(4, "prog.tutorial.chop_logs.0=3\nprog.tutorial.mine_basics.0=7\nprog.tutorial.mine_basics.1=2\nprog.tutorial.chop_logs.2=9\n")
    K.eq([str(sd.prog.get("tutorial.chop_logs.%d" % i)) for i in range(4)], ["3", "None", "9", "2"], "FOLD in the middle: counts carried, the higher one wins (9 > 7)")
    # /questadmin reload folds cached profiles (QIO mode 5): a profile cached before its file had was= is folded on reload
    ue, se = load(5, "prog.tutorial.mine_basics.0=8\n")
    K.check(str(se.prog.get("tutorial.chop_logs.2")) == "8", "FOLD at load")
    K.eq(str(se.extra.get("folded.tutorial.chop_logs")), "1", "FOLD FIX the run-once marker folded.tutorial.chop_logs=1 is set (a plain extra key)")
    K.check("folded.tutorial.chop_logs=1" in str(se.textU()), "FOLD FIX ... and written to the profile file")
    se.prog.remove("tutorial.chop_logs.2")
    se.extra.remove("folded.tutorial.chop_logs")      # = a profile cached before its line file had was=
    Sto.CACHE.put(str(ue), se)
    IO = JClass(PKG + "QIO")
    q = IO(5, None, None, None)
    q.o = None
    q.n = 0
    try:
        q.run()
    except Exception as ex_:
        K.notes.append("QIO 5 run: %s" % ex_)
    K.check(str(se.prog.get("tutorial.chop_logs.2")) == "8", "FOLD /questadmin reload (QIO mode 5) folds cached profiles again")
    # FIX (critic): /questadmin set <p> tutorial chop_logs undo stays undone through a reload / the next load (the fold runs once)
    ug, sg = load(7, BOTH)
    K.check(X.done(sg, "chop_logs"), "FOLD FIX undo: the folded profile starts done")
    K.check(bool(sg.adminUndo(L, t3)) and not X.done(sg, "chop_logs"), "FOLD FIX ... /questadmin undo clears the merged task")
    K.check(not bool(St.fold(sg)) and not X.done(sg, "chop_logs") and not any(bool(sg.pdone.contains("tutorial.chop_logs.%d" % i)) for i in range(5))
            and sg.prog.get("tutorial.chop_logs.2") is None, "FOLD FIX ... a second fold (reload / next load) does NOT bring the old parts back")
    open(os.path.join(pdir, "%s.properties" % ug), "w", newline="\n").write(str(sg.textU()))
    sg2 = Sto.read(str(ug), ug)
    K.check(not X.done(sg2, "chop_logs") and sg2.prog.get("tutorial.chop_logs.2") is None and bool(sg2.issued.contains("tutorial.mine_basics")),
            "FOLD FIX ... and the saved + re-read profile stays undone (issued kept: never paid twice)")
    # an EDITED tutorial file that still has mine_basics: nothing folded (0.3.2 behaviour)
    open(tf, "wb").write((str(Defs.TUTORIAL02) + "# edited\n").encode("utf-8"))
    Defs.load()
    K.check("mine_basics" in [str(t.id) for t in Defs.line("tutorial").tasks], "M the edited 0.2 file is KEPT (both old tasks)")
    uf, sf = load(6, "done.tutorial.chop_logs=1\nissued.tutorial.chop_logs=1\nprog.tutorial.mine_basics.0=4\n")
    K.check(X.done(sf, "chop_logs") and sf.prog.get("tutorial.chop_logs.2") is None, "FOLD with the kept 0.2 file: nothing folded, chop_logs stays done")
    K.check(os.path.isfile(tf + ".0.3.3.new"), "M ... and the 0.3.3 text is beside it as tutorial.properties.0.3.3.new")
    import zipfile as _zf
    _cr = _zf.ZipFile(jar).read(PKG.replace(".", "/") + "CfgRows.class")
    K.check(b"mine_basics now pays with chop_logs (merged)" in _cr, "M FIX the Server Setup tutorial reward help says mine_basics is paid with chop_logs")
    K.save()


# ---------------------------------------------------------------------------------------------------- CH: early progress + cascade (chain)
CHAIN = """line=zc
name=Chain test
mode=chain
auto=true
order=5

task.1.id=a
task.1.name=Break basalt
task.1.reward=coins:5
task.1.type=break
task.1.match=Rock_Basalt
task.1.count=2

task.2.id=b
task.2.name=Break slate
task.2.reward=coins:6
task.2.type=break
task.2.match=Rock_Slate
task.2.count=3

task.3.id=c
task.3.name=Talk to Bob
task.3.reward=coins:7
task.3.type=talk
task.3.match=bob

task.4.id=d
task.4.name=Kill one
task.4.reward=coins:8
task.4.type=kill
task.4.match=Trork_*
"""


CHAIN_T = """line=zt
name=Talk chain test
mode=chain
auto=true
order=6

task.1.id=ta
task.1.name=Talk to Dan
task.1.reward=coins:11
task.1.type=talk
task.1.match=dan

task.2.id=tb
task.2.name=Break marble
task.2.reward=coins:12
task.2.type=break
task.2.match=Rock_Marble
task.2.count=1

task.3.id=tc
task.3.name=Show Dan
task.3.reward=coins:13
task.3.type=talk
task.3.match=dan
"""


def run_chain(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, FAKE_DIR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    PyFn = T03.fn_class()
    Boolean, Long = JClass("java.lang.Boolean"), JClass("java.lang.Long")
    X = T03.scene3(K, scratch, "ch")
    Eng, Defs = X.Eng, X.Defs
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    br.put("coins:fn:add", PyFn(lambda a: Long(1)))
    feeds = []
    br.put("feed:fn:push", PyFn(lambda a: feeds.append(str(a[3])) or Boolean.TRUE))
    open(os.path.join(X.base, "quests", "zc.properties"), "w").write(CHAIN)
    open(os.path.join(X.base, "quests", "zt.properties"), "w").write(CHAIN_T)
    Defs.load()
    L = Defs.line("zc")
    K.check(L is not None and bool(L.chain), "CH the chain line loads")
    W = "w"
    u, p, s = X.player(1)
    k = lambda t: bool(s.isDone("zc." + t))
    w = X.want(u)
    K.check((w & TB["break"]) and (w & TB["kill"]), "CH want: break + kill bits (step 2 / 4 count early)")
    Eng.count(u, TB["break"], "Rock_Slate", 3, W, False)
    K.check(not k("b") and bool(s.pdone.contains("zc.b.0")) and str(s.prog.get("zc.b.0")) == "3", "CH step 2 (not active yet) COUNTS early: 3/3, not done")
    K.eq(str(Eng.progL(s, L, L.tasks[1])[0]), "3/3", "CH the log page shows the early count")
    K.check(not [f for f in feeds if f.startswith("Break slate")], "CH FIX an early step (not its turn yet) sends NO progress card: %s" % feeds[-2:])
    Eng.count(u, TB["kill"], "Trork_Grunt", 1, W, False)
    K.check(not k("d") and bool(s.pdone.contains("zc.d.0")), "CH step 4 kill counts early too")
    v0 = int(s.ver)
    K.check(not bool(Eng.count(u, TB["talk"], "bob", 1, W, False)) and not bool(s.pdone.contains("zc.c.0")) and int(s.ver) == v0,
            "CH a TALK step that is not active is NOT counted (a hand-in needs its turn)")
    n0 = len(feeds)
    Eng.count(u, TB["break"], "Rock_Basalt", 2, W, False)
    K.check(k("a") and k("b") and not k("c") and not k("d"), "CH step 1 done -> the already-met step 2 completes AT ONCE (the CASCADE); step 3 now active")
    K.check(feeds[n0:].count("Done: Break basalt") == 1 and feeds[n0:].count("Done: Break slate") == 1
            and feeds[n0:].index("Done: Break basalt") < feeds[n0:].index("Done: Break slate"), "CH ... one Done card each, in order: %s" % feeds[n0:])
    lg = T03.logtext(X.base)
    K.check(lg.count("PAID %s coins|5|" % u) == 1 and lg.count("PAID %s coins|6|" % u) == 1, "CH ... both rewards paid once")
    Eng.rebuild(u, s)
    K.check(X.want(u) & TB["talk"], "CH step 3 active: the talk bit is back")
    Eng.count(u, TB["talk"], "bob", 1, W, False)
    K.check(k("c") and k("d"), "CH the talk finishes step 3 and the early kill finishes step 4 at once")
    lg = T03.logtext(X.base)
    K.check(lg.count("PAID %s coins|7|" % u) == 1 and lg.count("PAID %s coins|8|" % u) == 1 and lg.count("PAID %s coins|5|" % u) == 1, "CH every reward exactly once")
    # a skipped step never blocks; an early-met step after it completes when it becomes active
    u2, p2, s2 = X.player(2)
    Eng.count(u2, TB["break"], "Rock_Slate", 3, W, False)
    K.check(not bool(s2.isDone("zc.b")), "CH player 2: step 2 met early, step 1 not done")
    r = str(Eng.action(u2, "skip", "zc.a"))
    K.check(bool(s2.isSkipped("zc.a")) and r.startswith("+Skipped"), "CH skip step 1 (/quests skip zc.a): %s" % r)
    K.check(bool(s2.isDone("zc.b")) and not bool(s2.isDone("zc.a")), "CH ... the skip makes the already-met step 2 active -> done AT ONCE")
    Eng.count(u2, TB["break"], "Rock_Basalt", 2, W, False)
    K.check(bool(s2.isDone("zc.a")), "CH ... the skipped step still counts and finishes later")
    lg = T03.logtext(X.base)
    K.check(lg.count("PAID %s coins|6|" % u2) == 1 and lg.count("PAID %s coins|5|" % u2) == 1, "CH ... each paid once")
    # FIX (critic): A talk dan, B break (met early), C talk dan (another NPC than zc's bob) - ONE talk finishes A (+ B by the cascade), NOT C
    LT = Defs.line("zt")
    K.check(LT is not None and bool(LT.chain), "CH FIX the talk chain line loads")
    u3, p3, s3 = X.player(3)
    kt = lambda t: bool(s3.isDone("zt." + t))
    Eng.count(u3, TB["break"], "Rock_Marble", 1, W, False)
    K.check(not kt("ta") and bool(s3.pdone.contains("zt.tb.0")), "CH FIX step B (break) met early")
    Eng.count(u3, TB["talk"], "dan", 1, W, False)
    K.check(kt("ta") and kt("tb") and not kt("tc") and not bool(s3.pdone.contains("zt.tc.0")),
            "CH FIX ONE talk: A done, B done by the cascade, C (made active by this same event) NOT ticked")
    lg = T03.logtext(X.base)
    K.check(lg.count("PAID %s coins|11|" % u3) == 1 and lg.count("PAID %s coins|12|" % u3) == 1 and ("PAID %s coins|13|" % u3) not in lg, "CH FIX ... A + B paid, C not")
    Eng.rebuild(u3, s3)
    Eng.count(u3, TB["talk"], "dan", 1, W, False)
    K.check(kt("tc"), "CH FIX the SECOND talk finishes C")
    K.check(T03.logtext(X.base).count("PAID %s coins|13|" % u3) == 1, "CH FIX ... paid once")
    K.save()


# ---------------------------------------------------------------------------------------------------- MT: the one-time tutorial file update
def run_migt(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, FAKE_DIR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Paths = JClass("java.nio.file.Paths")
    X = T03.scene3(K, scratch, "mt")
    Defs = X.Defs
    v1, v2, v3 = str(Defs.TUTORIAL01), str(Defs.TUTORIAL02), str(Defs.TUTORIAL)
    K.check("Shipped by SkyyQuests 0.2," in v2 and "updated by 0.3.3" in v3 and "updated by 0.3.3" not in v2, "MT the three shipped texts")
    for name, data, frm in (("v2", v2, "0.2"), ("v1", v1, "0.1")):
        d = os.path.join(scratch, "mt-" + name)
        os.makedirs(d, exist_ok=True)
        tp = os.path.join(d, "tutorial.properties")
        open(tp, "wb").write(data.encode("utf-8"))
        m = str(Defs.migrateTut(Paths.get(tp)))
        K.check(open(tp, "rb").read() == v3.encode("utf-8") and open(tp + "." + frm + ".bak", "rb").read() == data.encode("utf-8") and "0.3.3" in m,
                "MT the untouched %s file -> the 0.3.3 tutorial; the old bytes kept as tutorial.properties.%s.bak" % (frm, frm))
        K.eq(str(Defs.migrateTut(Paths.get(tp))), "", "MT ... a second start does nothing (the marker)")
        K.check(not os.path.isfile(tp + ".0.3.3.new"), "MT ... no .new beside an updated file")
    d = os.path.join(scratch, "mt-ed")
    os.makedirs(d, exist_ok=True)
    tp = os.path.join(d, "tutorial.properties")
    ed = (v2 + "# my own line\n").encode("utf-8")
    open(tp, "wb").write(ed)
    m = str(Defs.migrateTut(Paths.get(tp)))
    K.check(open(tp, "rb").read() == ed and open(tp + ".0.3.3.new", "rb").read() == v3.encode("utf-8") and "KEPT" in m, "MT an edited file is KEPT + the 0.3.3 text beside it")
    t0 = os.path.getmtime(tp + ".0.3.3.new")
    open(tp + ".0.3.3.new", "ab").write(b"# the owner's note\n")
    K.eq(str(Defs.migrateTut(Paths.get(tp))), "", "MT ... the .new is written ONCE (a second start leaves it)")
    K.check(open(tp + ".0.3.3.new", "rb").read().endswith(b"# the owner's note\n"), "MT ... and keeps the owner's change to it")
    # a backup that cannot be written: nothing changes
    d = os.path.join(scratch, "mt-nobak")
    os.makedirs(os.path.join(d, "tutorial.properties.0.2.bak"), exist_ok=True)     # a folder where the backup file should go
    tp = os.path.join(d, "tutorial.properties")
    open(tp, "wb").write(v2.encode("utf-8"))
    m = str(Defs.migrateTut(Paths.get(tp)))
    K.check(open(tp, "rb").read() == v2.encode("utf-8") and m == "", "MT a backup that cannot be written = the file is NOT changed (%s)" % m[:80])
    K.save()


# ---------------------------------------------------------------------------------------------------- ST: start twice on the live copy
def run_live033(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    mods = os.path.dirname(home)
    base = os.path.join(mods, "Skyy_SkyyQuests")
    LIVE_Q = T03.LIVE_Q
    if not os.path.isdir(LIVE_Q):
        K.check(False, "ST no live Skyy_SkyyQuests at %s" % LIVE_Q)
        K.save()
        return
    shutil.copytree(LIVE_Q, base)                  # a scratch COPY (the source is only read)
    q0 = HK.tree_hash(LIVE_Q)
    tp = os.path.join(base, "quests", "tutorial.properties")
    old = open(tp, "rb").read()
    players0 = dict((f, open(os.path.join(base, "players", f), "rb").read()) for f in os.listdir(os.path.join(base, "players")))
    Paths = JClass("java.nio.file.Paths")
    res = []
    E = None
    for n in range(2):
        b0 = HK.tree_hash(mods)
        E = T03.Env(base)
        E.P("QDefs").BOARD_FILE = Paths.get(os.path.join(base, "board.properties"))
        Npc = E.P("QNpc")
        Npc.FILE = Paths.get(os.path.join(base, "npcs.tsv"))
        Npc.DLG_DIR = Paths.get(os.path.join(base, "dialogue"))
        E.P("QMig").migrate02()
        lines = E.start()
        errs = JClass("java.util.ArrayList")()
        Npc.load(errs)
        Npc.loadDialogues(errs)
        res.append((lines, [str(x) for x in E.P("QDefs").PROBLEMS] + [str(x) for x in errs], HK.tree_hash(mods), b0))
    K.check(res[0][0] >= 7 and not res[0][1], "ST start 1: %d lines, no problems: %s" % (res[0][0], res[0][1]))
    ch = sorted(k for k in set(res[0][2]) | set(res[0][3]) if res[0][2].get(k) != res[0][3].get(k))
    K.eq(ch, sorted([os.path.join("Skyy_SkyyQuests", "quests", "tutorial.properties"), os.path.join("Skyy_SkyyQuests", "quests", "tutorial.properties.0.2.bak")]),
         "ST start 1 changes ONLY the tutorial file (the live file is the 0.2 shipped text) + writes its .0.2.bak")
    K.check(open(tp + ".0.2.bak", "rb").read() == old and open(tp, "rb").read() == str(E.P("QDefs").TUTORIAL).encode("utf-8"), "ST the .0.2.bak = the old bytes; the new file = the 0.3.3 tutorial")
    K.check(res[1][2] == res[1][3], "ST start 2 writes nothing")
    K.eq(HK.tree_hash(LIVE_Q), q0, "ST the LIVE folder itself was only read")
    Sto = E.P("QStore")
    Sto.DIR = Paths.get(os.path.join(base, "players"))
    U = JClass("java.util.UUID")
    for f, raw in sorted(players0.items()):
        pk = f[:-len(".properties")]
        s = Sto.read(pk, U.randomUUID())
        P2 = JClass("java.util.Properties")()
        P2.load(JClass("java.io.StringReader")(raw.decode("utf-8")))
        want_ = dict((str(k), str(P2.getProperty(k))) for k in P2.stringPropertyNames())
        P3 = JClass("java.util.Properties")()
        P3.load(JClass("java.io.StringReader")(str(s.textU())))
        got = dict((str(k), str(P3.getProperty(k))) for k in P3.stringPropertyNames())
        lost = sorted(k for k in want_ if k not in got and k != "done.tutorial.chop_logs")
        K.check(not bool(s.frozen) and not lost, "ST live profile %s loads, keeps every key (%d keys; lost %s)" % (f, len(want_), lost))
        if "done.tutorial.mine_basics" in want_ and "done.tutorial.chop_logs" in want_:
            K.check(bool(s.isDone("tutorial.chop_logs")) and int(s.claimCount()) == int(sum(1 for k in want_ if k.startswith("claim."))),
                    "ST live profile %s: both old tasks were done -> the merged task done, nothing new to pay" % f)
        K.check(open(os.path.join(base, "players", f), "rb").read() == raw, "ST ... and the start did not rewrite it")
    K.notes.append("ST live profiles: %s" % sorted(players0))
    K.save()


if __name__ == "__main__":
    if "--mkfake" in sys.argv:
        T03.mkfake(HK.arg("--mkfake"), JAR)
        sys.exit(0)
    if "--phase" not in sys.argv:
        shutil.rmtree(FAKE_DIR, ignore_errors=True)
        os.makedirs(FAKE_DIR, exist_ok=True)
        env = dict(os.environ)
        env["TEMP"] = env["TMP"] = os.path.join(FAKE_DIR, "tmp")
        os.makedirs(env["TEMP"], exist_ok=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mkfake", FAKE_DIR, "--jar", JAR, "--dir", SCRATCH], env=env)
        if r.returncode != 0:
            sys.exit("the stand-in classes were not compiled")
    try:
        HK.run("SkyyQuests", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
               [("merge", run_merge), ("chain", run_chain), ("migt", run_migt),
                ("isl", legacy(T032.run_isl)), ("snd", legacy(T031.run_snd)), ("defs", legacy(T03.run_defs)), ("engine", legacy(T03.run_engine)),
                ("life", legacy(T03.run_life)), ("pay", legacy(T03.run_pay)), ("crash", legacy(T03.run_crash)), ("static", legacy(T03.run_static)),
                ("npc", legacy(T03.run_npc)), ("board", legacy(T03.run_board)), ("fish", legacy(T03.run_fish)), ("live", run_live033)],
               os.path.abspath(__file__), live=(T03.LIVE_DIR, "Skyy_SkyyIslands"))
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(FAKE_DIR, ignore_errors=True)
