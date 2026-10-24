"""SkyyQuests 0.4.4 harness (the ARCHIPELAGO line + the have objective + first_shard -> "Open a shard door"; tools/quests_0_4_4_patch.py)
on top of the 0.4.3 harness (test_skyyquests_0.4.3.py -> 0.4.2 -> ... -> 0.3: every older phase runs again on the 0.4.4 jar).

    python SkyyQuests/test_skyyquests_0.4.4.py [--jar SkyyQuests-0.4.4.jar] [--keep] [--only archi44,...]

  A / C / AA  verify (-Xverify:all), class compare 0.4.3 -> 0.4.4, engine-access audit
  ARCHI44 archi44  a fresh folder: quests/archipelago.properties written ONCE (byte for byte the shipped text; an edited copy is kept), the
               line loads (30 tasks, order 10 after the tutorial, auto), every task HIDDEN without shard:fn:door and shown with it; the
               real quest:fn:event with SkyyShards 0.4.8's exact Object[] { UUID, "event", "shard:door:<kind>", 1 } completes that door
               task (+ the tutorial's first_shard, ONE claim pair, never twice), shard:seeds:<kind> the optional seed task; the visit
               tasks via the real position path with SkyyIslands 0.5.25's island:places (coming soon without them); level tasks via the
               lazy check (skill:fn:level stand-in, "Combat" = the class level); the want index carries the have bit; needsHop for a
               have-only player
  HAVE44 have44  QEng.haveCount on real SimpleItemContainers + real ItemStacks (ids, globs, a|b, meta=CapturedEntity on a stack made
               with withMetadata), haveDue (bit + 2 s throttle), QEng.have (progress rises only, done at count, stays done, claims once),
               havePl with a real Player whose Inventory is empty (null-safe), the parser: meta on a non-have part = a problem + ignored
  FS44  fs44   QDefs.shard044: the OLD shipped first_shard (0.4.3's tutorial file) loads as "Open a shard door" (match shard:door:*,
               requires shard:fn:door, no caller, new name + hint) in memory only (the file's bytes unchanged); an owner-edited copy
               (another match / name) keeps its own values
  LIVE44 live44 START TWICE on a scratch COPY of the live Skyy_SkyyQuests: start 1 writes exactly ONE new file (quests/archipelago.properties)
               and nothing else; start 2 writes nothing; every live profile loads and keeps every key; the archipelago line is active
               for each with no done / issued key of its own; no claim of an OLD task is added (nothing re-paid)
  OLD   every 0.4.3 phase (wid43 acc42 gear41 page40 claim40 mig34 fish34 merge chain migt isl snd defs engine life pay crash static npc
        board fish live40 live41) - live40's "start 1 writes nothing" is waived (0.4.4 copies the new line file once: LIVE44)
Scratch: tools/dev/scratch/quest044/q (deleted unless --keep). Exit 1 on any failure.
"""
import os, sys, shutil, subprocess, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.4.4"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "quest044", "q")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)]
import harness_kit as HK
import skyybuild as B

_spec = importlib.util.spec_from_file_location("test_skyyquests_0_4_3", os.path.join(HERE, "test_skyyquests_0.4.3.py"))
T043 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T043)
T042 = T043.T042
T041, T040, T034, T033, T03 = T042.T041, T042.T040, T042.T034, T042.T033, T042.T03

JAR = T043.JAR
OLD_JAR = os.path.join(HERE, "SkyyQuests-0.4.3.jar")
SCRATCH, FAKE_DIR, PKG = T03.SCRATCH, T03.FAKE_DIR, T03.PKG
EXPECT = {
    "QDefs": ["+m shard044", "~<clinit>", "~m parse", "~m part"],                  # first_shard in memory; the shipped texts; have parts' meta
    "QEng": ["+f HAVES", "+f HAVE_MS", "+m have", "+m haveCount", "+m haveDue", "+m haveListL", "+m havePl", "+m haveSetL", "+m haveWorld", "+f HAVE_OPT_MS", "+f RWC", "+f RW_MS", "+m reachWorld", "~<clinit>"],
    "QState": ["+m haveList", "+m haveSet"],
    "QHop": ["~m run"],                                                             # the have look on the world thread
    "QLife": ["~m needsHop"],                                                       # a have part = the hop
    "QP": ["+f haveAt"], "QPart": ["+f meta", "~c "],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyQuestsPlugin": ["~m setup"],    # the version texts
}
ADDED, REMOVED = [], []
TB = dict(T03.TB)
TB["have"] = 1 << 14
KINDS = ("farming", "foraging", "mining", "ranching", "orchard", "combat")
PLACES = ("farm=island|29.5|129.0|-25.5|The Farming island;forage=island|-18.5|131.0|-32.5|The Foraging island;"
          "minecave=island|-26.5|128.0|4.5|The copper cave;ranch=island|-19.5|128.0|45.5|The Ranching island;"
          "orchard=island|17.5|129.0|52.5|The Orchard island;island2=island|46.5|128.0|14.5|Island 2")

# ---------------------------------------------------------------------------------------------------- waivers: on purpose in 0.4.4
_LV44 = "LIVE44 (start 1 writes exactly quests/archipelago.properties, copied once; start 2 / pages write nothing)"
_D44 = "ARCHI44 (the new archipelago line, order 10, right after the tutorial)"
WAIVE44 = (("LV start 1 writes nothing", _LV44), ("LV start 2 writes nothing", _LV44), ("LV building the pages wrote nothing", _LV44),
           ("LV41 starting 0.4.1 on the live copy writes nothing", _LV44), ("LV41 nothing written", _LV44),
           ("D1 six quest lines", _D44), ("D1 lines sorted by order", _D44), ("D1 the line orders", _D44),
           ("D3 the 6 shipped lines + side_line", _D44), ("N0 the 7 lines in order", _D44))
_chk043 = HK.Child.check


def _check44(self, cond, what):
    if not cond:
        for w, why in WAIVE44:
            if str(what).startswith(w):
                self.notes.append("WAIVED (0.4.4, on purpose; covered by %s): %s" % (why, str(what)[:140]))
                return cond
    return _chk043(self, cond, what)


HK.Child.check = _check44
_eq043 = HK.Child.eq


def _eq44(self, got, want, what):
    if got != want:
        for w, why in WAIVE44:
            if str(what).startswith(w):
                self.notes.append("WAIVED (0.4.4, on purpose; covered by %s): %s (got %r)" % (why, str(what)[:120], got))
                return False
    return _eq043(self, got, want, what)


HK.Child.eq = _eq44


def _boot(K, scratch, name, pre=None):
    """a bare JVM with the jar + the stand-ins, the bridge, a Scene (QDefs.load ran on a fresh scratch folder; pre(base) writes files first)"""
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, JAR if "--jar" not in sys.argv else HK.arg("--jar"), FAKE_DIR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    if pre is not None:
        pre(os.path.join(scratch, name, "Skyy_SkyyQuests"))
    X = T03.Scene(K, scratch, name)
    return br, X


def rows_of(s, L):
    r = [str(x) for x in s.rowsOf(L)]
    return dict((str(L.tasks[i].id), (r[2 * i], r[2 * i + 1])) for i in range(len(L.tasks)))


def logtext(X):
    return T03.logtext(X.base)


def issued(X, s, u, claim):
    """how many times a claim line was issued: waiting in the state (the payer pays one pass per wake; an item claim with no world
    bounces) + PAYING lines in quests.log"""
    return len([c for c in s.claims if str(c).startswith(claim)]) + T03.logtext(X.base).count("PAYING %s %s" % (u, claim))


# ---------------------------------------------------------------------------------------------------- ARCHI44: the line end to end
def run_archi44(out, jar, scratch, home):
    from jpype import JClass, JObject, JArray, JString
    K = HK.Child(out)
    br, X = _boot(K, scratch, "a44")
    PyFn = T03.fn_class()
    Boolean, Long, Integer = JClass("java.lang.Boolean"), JClass("java.lang.Long"), JClass("java.lang.Integer")
    Eng, Defs, Sto, Life, P = X.Eng, X.Defs, X.Sto, X.Life, X.E.P
    qd = os.path.join(X.base, "quests")
    af = os.path.join(qd, "archipelago.properties")
    files, texts = [str(x) for x in Defs.LINE_FILES], [str(x) for x in Defs.LINE_TEXTS]
    K.check(files[-1] == "fishing_intro.properties" and "archipelago.properties" in files, "ARCHI the shipped line files: + archipelago, Marlow's line still last: %s" % files)
    shipped = texts[files.index("archipelago.properties")]
    K.check(os.path.isfile(af) and open(af, "rb").read() == shipped.encode("utf-8"), "ARCHI quests/archipelago.properties written on a fresh folder, byte for byte the shipped text")
    K.check("updated by 0.3.3" in open(os.path.join(qd, "tutorial.properties"), encoding="utf-8").read()
            and "match=shard:door:*\n" in open(os.path.join(qd, "tutorial.properties"), encoding="utf-8").read(),
            "FS the fresh tutorial file carries first_shard = shard:door:* (and the 0.3.3 marker - no tutorial update runs on it)")
    K.check(not [str(x) for x in Defs.PROBLEMS], "ARCHI no file problems: %s" % [str(x) for x in Defs.PROBLEMS])
    ids = [str(l.id) for l in Defs.LINES]
    K.eq(ids[:2], ["tutorial", "archipelago"], "ARCHI the line sits right after the tutorial (order 10)")
    L = Defs.line("archipelago")
    K.check(L is not None and len(L.tasks) == 30 and bool(L.auto) and not bool(L.chain) and int(L.order) == 10 and str(L.name) == "Your Islands",
            "ARCHI 30 tasks, open, auto, order 10, 'Your Islands'")
    K.check(all(str(t.requires) == "shard:fn:door" for t in L.tasks), "ARCHI every task requires shard:fn:door")
    K.eq(sorted(str(t.id) for t in L.tasks if bool(t.optional)), ["archi_egg", "archi_farmseeds", "archi_foragesap", "archi_orchardsap"], "ARCHI the 4 optional tasks")
    tut = Defs.line("tutorial")
    fs = [t for t in tut.tasks if str(t.id) == "first_shard"][0]
    K.check(str(fs.name) == "Open a shard door" and str(fs.requires) == "shard:fn:door" and len(fs.parts) == 1 and str(fs.parts[0].match) == "shard:door:*"
            and str(fs.parts[0].caller) == "" and str(fs.reward) == "coins:50,item:Ingredient_Bar_Iron:2", "FS first_shard: Open a shard door, shard:door:*, no caller, the same reward")
    # ---- hidden without SkyyShards 0.4.8
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    coins = []
    br.put("coins:fn:add", PyFn(lambda a: coins.append(int(a[1])) or Long(1000)))
    br.put("feed:fn:push", PyFn(lambda a: Boolean.TRUE))
    u, p, s = X.player(44)
    r0 = rows_of(s, L)
    K.check(all(v[0] == "hidden" for v in r0.values()), "ARCHI without shard:fn:door every task is hidden: %s" % sorted(set(v[0] for v in r0.values())))
    K.eq(rows_of(s, tut)["first_shard"][0], "hidden", "FS ... first_shard too")
    K.check(not (X.want(u) & TB["have"]), "ARCHI ... and no have bit (no inventory looks)")
    br.put("shard:fn:door", PyFn(lambda a: JString("+")))
    Eng.rebuild(u, s)
    r1 = rows_of(s, L)
    soon = sorted(k for k, v in r1.items() if v[0] == "soon")
    K.eq(soon, ["archi_farm", "archi_forage", "archi_mine", "archi_orchard", "archi_ranch"], "ARCHI with it: the 5 visits are coming soon (no island:places yet), the rest open")
    K.check(all(v[0] == "open" for k, v in r1.items() if k not in soon), "ARCHI ... every other task open")
    w = X.want(u)
    K.check(w & TB["have"] and w & TB["event"] and w & TB["level"] and not (w & TB["reach"]), "ARCHI the want index: have + event + level, no reach without places (%d)" % w)
    # ---- the visits: SkyyIslands 0.5.25's island:places
    br.put("island:places", JString(PLACES))
    Eng.rebuild(u, s)
    K.check(X.want(u) & TB["reach"], "ARCHI places published -> the reach bit")
    K.eq(rows_of(s, L)["archi_farm"][0], "open", "ARCHI ... the Farming visit is open")
    Eng.position(p, "skyy-island-a1", 29.0, 129.0, -20.0)
    K.check(bool(s.isDone("archipelago.archi_farm")), "ARCHI standing on the Farming island (5.5 blocks from its place) = Visit the Farming island done")
    Eng.position(p, "skyy-island-a1", 8.5, 129.0, 8.5)
    K.check(not bool(s.isDone("archipelago.archi_forage")) and not bool(s.isDone("archipelago.archi_ranch")), "ARCHI the spawn island counts for no other visit")
    Eng.position(p, "skyy-hub", -18.5, 131.0, -32.5)
    K.check(not bool(s.isDone("archipelago.archi_forage")), "ARCHI the same spot in another (non-island) world does not count")
    Eng.position(p, "skyy-island-zz", -26.5, 128.0, 6.0)
    K.check(bool(s.isDone("archipelago.archi_mine")), "ARCHI at the cave mouth = Find the copper cave done")
    # ---- shard events through the REAL quest:fn:event, SkyyShards 0.4.8's exact call
    Fn = P("QFn")("event")
    OA = lambda *xs: JArray(JObject)([JObject(x) for x in xs])
    n0 = len(coins)
    r = Fn.apply(OA(u, JString("event"), JString("shard:door:farming"), Long(1)))
    K.check(bool(r) and bool(s.isDone("archipelago.archi_farmingdoor")), "ARCHI shard:door:farming -> Open the Farming Shard done (%s)" % r)
    K.check(bool(s.isDone("tutorial.first_shard")), "FS ... and the tutorial's first_shard (any door)")
    K.eq(issued(X, s, u, "coins|110|%s:archipelago.archi_farmingdoor:" % u), 1, "ARCHI its coins (110 = 0.02 h at Lv 5 on the curve) issued once")
    K.eq(issued(X, s, u, "item|Plant_Seeds_Wheat:16|%s:archipelago.archi_farmingdoor:" % u), 1, "ARCHI ... and its item once")
    K.eq(issued(X, s, u, "coins|50|%s:tutorial.first_shard:" % u), 1, "FS first_shard's old 50 coins issued once")
    Fn.apply(OA(u, JString("event"), JString("shard:door:mining"), Long(1)))
    K.check(bool(s.isDone("archipelago.archi_miningdoor")) and issued(X, s, u, "coins|50|%s:tutorial.first_shard:" % u) == 1,
            "FS a second door: the Mining door task, first_shard NOT paid again")
    K.check(not bool(s.isDone("archipelago.archi_ranchingdoor")), "ARCHI the Ranching door still open")
    Fn.apply(OA(u, JString("event"), JString("shard:seeds:farming"), Long(1)))
    K.check(bool(s.isDone("archipelago.archi_farmseeds")), "ARCHI shard:seeds:farming -> the optional seed task done")
    Fn.apply(OA(u, JString("event"), JString("shard:auto:farming"), Long(1)))
    K.check(not bool(s.isDone("archipelago.archi_foragesap")), "ARCHI shard:auto:farming completes nothing else")
    # ---- level tasks (lazy, skill:fn:level; Combat = the class level)
    lv = {"Farming": 5, "Foraging": 4, "Mining": 9, "Orchard": 5, "Ranching": 0, "Combat": 5}
    br.put("skill:fn:level", PyFn(lambda a: Integer(lv.get(str(a[1]), 0))))
    Eng.lazy(p, True)
    dn = dict((k, bool(s.isDone("archipelago." + k))) for k in ("archi_farm5", "archi_forage5", "archi_mine5", "archi_orchard5", "archi_ranch5", "archi_class5"))
    K.eq(issued(X, s, u, "gear|weapon|%s:archipelago.archi_class5:" % u) + issued(X, s, u, "gear|armor|%s:archipelago.archi_class5:" % u), 2,
         "FIXC class level 5 (a combat quest, Skyy Q1) issued gear:weapon + gear:armor once each")
    K.check(not [c for c in [str(x) for x in s.claims] + T03.logtext(X.base).split("\n") if "archipelago.archi_class5:" in c and ("coins|" in c or "item|" in c)],
            "FIXC ... and no coins / item for it")
    K.eq(dn, {"archi_farm5": True, "archi_forage5": False, "archi_mine5": True, "archi_orchard5": True, "archi_ranch5": False, "archi_class5": True},
         "ARCHI the level-5 tasks tick from skill:fn:level (Mining 9 too; Foraging 4 / Ranching 0 not)")
    lv["Foraging"] = 5
    Eng.lazy(p, True)
    K.check(bool(s.isDone("archipelago.archi_forage5")), "ARCHI Foraging reaching 5 later ticks it")
    # ---- counters (harvest, logs, copper) still work on the new line
    for i in range(10):
        Eng.count(u, TB["break"], "Ore_Copper_Stone", 1, "skyy-island-a1", False)
    K.check(bool(s.isDone("archipelago.archi_copper")), "ARCHI 10 copper ore broken -> Mine 10 copper ore")
    Eng.count(u, TB["felled"], "Wood_Birch_Trunk", 10, "skyy-island-a1", False)
    K.check(bool(s.isDone("archipelago.archi_logs")), "ARCHI 10 birch trunks felled -> Chop 10 oak or birch logs")
    Eng.count(u, TB["gather"], "Plant_Crop_Wheat_Item", 12, "skyy-island-a1", False)
    K.check(bool(s.isDone("archipelago.archi_wheat")) and not bool(s.isDone("archipelago.archi_replant")) and rows_of(s, L)["archi_replant"][1] == "12/40",
            "ARCHI 12 wheat: Harvest 10 wheat done, Replant 12/40 (%s)" % (rows_of(s, L)["archi_replant"],))
    # ---- the hop decision for have parts (QLife.needsHop)
    q = X.QP(X.U(0x4444, 1), None)
    q.world = "skyy-island-a1"
    Eng.WANT.put(q.u, Integer(TB["have"]))
    K.check(bool(Life.needsHop(q, Long(0))), "HAVE a player whose only open objective is a have part gets the position hop (the inventory look runs there)")
    q.haveAt = 5000
    K.check(not bool(Life.needsHop(q, Long(4000))) and bool(Life.needsHop(q, Long(5000))), "FIXL a have part alone asks for the hop only when its look is due")
    q.haveAt = 0
    for w_ in ("skyy-hub", "skyy-shard-farming-1", None):
        q.world = w_
        K.check(not bool(Life.needsHop(q, Long(0))) and not bool(Eng.haveDue(q, Long(0))), "FIXL in %s: no hop and no inventory look for have parts" % w_)
    q.world = "skyy-island-a1"
    Eng.WANT.put(q.u, Integer(0))
    K.check(not bool(Life.needsHop(q, Long(0))), "HAVE ... nothing open = no hop")
    # ---- FIX2 lag rule: the reach bit asks for the hop only in a world holding some reach place (the archipelago places = island worlds)
    Eng.RWC.clear()
    Eng.WANT.put(q.u, Integer(TB["reach"]))
    for w_, want_ in (("skyy-island-a1", True), ("skyy-shard-farming-1", False), ("skyy-shard-combat-9", False), (None, False)):
        q.world = w_
        K.eq(bool(Life.needsHop(q, Long(1000))), want_, "FIX2R reach tasks open, standing in %s: hop %s" % (w_, want_))
    hubw_ = bool([1 for l_ in Defs.LINES for t_ in l_.tasks for p_ in t_.parts if int(p_.type) == TB["reach"] and Defs.place(p_.match) is not None and bool(Eng.worldMatch(Defs.place(p_.match).world, "skyy-hub"))])
    K.eq(bool(Eng.reachWorld("skyy-hub", Long(1000))), hubw_, "FIX2R the hub hops exactly when some reach place lies in the hub (%s)" % hubw_)
    br.remove("island:places")
    q.world = "skyy-island-b2"
    K.check(not bool(Life.needsHop(q, Long(1000))) and bool(Eng.RWC.containsKey("skyy-island-b2")), "FIX2R no island:places = no island reach place = no hop (cached)")
    br.put("island:places", JString(PLACES))
    K.check(not bool(Life.needsHop(q, Long(2000))) and bool(Life.needsHop(q, Long(1000 + int(Eng.RW_MS)))), "FIX2R the cache holds RW_MS, then the new places count")
    q.world = "skyy-island-a1"
    Eng.WANT.put(q.u, Integer(0))
    # ---- a second start: the copied file is kept as it is (an owner's edit stays)
    open(af, "a", encoding="utf-8").write("# my note\n")
    b1 = open(af, "rb").read()
    Defs.load()
    K.check(open(af, "rb").read() == b1, "ARCHI a later start never rewrites quests/archipelago.properties (copied once - edits stay)")
    os.remove(af)
    Defs.load()
    K.check(open(af, "rb").read() == shipped.encode("utf-8"), "ARCHI a deleted copy is written again from the shipped text")
    K.save()


# ---------------------------------------------------------------------------------------------------- HAVE44: the have objective
def run_have44(out, jar, scratch, home):
    from jpype import JClass, JObject, JArray, JString
    K = HK.Child(out)
    br, X = _boot(K, scratch, "h44")
    PyFn = T03.fn_class()
    Boolean, Long, Integer = JClass("java.lang.Boolean"), JClass("java.lang.Long"), JClass("java.lang.Integer")
    Eng, Defs = X.Eng, X.Defs
    ids = ["Tool_Capture_Crate", "Tool_Shears_Basic", "Ingredient_Fabric_Scrap_Wool", "*Container_Bucket_State_Filled_Milk", "Container_Bucket",
           "Food_Egg", "Plant_Fruit_Apple", "Rock_Stone"]
    T03.item_store(ids)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    BD = JClass("org.bson.BsonDocument")
    BS = JClass("org.bson.BsonString")
    st, hb, bp = SIC(9), SIC(9), SIC(4)
    cs = JArray(IC)([st, hb, bp])
    hc = lambda pat, meta="": int(Eng.haveCount(cs, pat, meta))
    K.eq(hc("Food_Egg"), 0, "HAVE empty bags: 0")
    st.addItemStack(IS("Food_Egg", 2))
    bp.addItemStack(IS("Food_Egg", 1))
    hb.addItemStack(IS("Plant_Fruit_Apple", 3))
    K.eq(hc("Food_Egg"), 3, "HAVE storage + backpack counted (2 + 1)")
    K.eq(hc("Food_*"), 3, "HAVE a glob")
    K.eq(hc("Food_Egg|Plant_Fruit_Apple"), 6, "HAVE a|b alternatives (hotbar too)")
    K.eq(hc("Rock_Stone"), 0, "HAVE an id not held: 0")
    K.eq(int(Eng.haveCount(JArray(IC)([None, st]), "Food_Egg", "")), 2, "HAVE a null container is skipped")
    hb.addItemStack(IS("Tool_Capture_Crate", 1))
    K.eq(hc("Tool_Capture_Crate"), 1, "HAVE an empty crate counts for the plain id")
    K.eq(hc("Tool_Capture_Crate", "CapturedEntity"), 0, "HAVE ... but not for meta=CapturedEntity (an empty crate has no captured animal)")
    md = BD()
    md.put("CapturedEntity", BD("NpcNameKey", BS("server.npc.Chicken_Chick")))
    full = IS("Tool_Capture_Crate", 1).withMetadata(md)
    st.addItemStack(full)
    K.eq(hc("Tool_Capture_Crate", "CapturedEntity"), 1, "HAVE a crate made with withMetadata(CapturedEntity) = a full crate counts")
    K.eq(hc("Tool_Capture_Crate"), 2, "HAVE ... and both crates count for the plain id")
    md2 = BD()
    md2.put("SkyyUnid", BD())
    st.addItemStack(IS("Tool_Capture_Crate", 1).withMetadata(md2))
    K.eq(hc("Tool_Capture_Crate", "CapturedEntity"), 1, "HAVE other metadata is not CapturedEntity")
    st.addItemStack(IS("*Container_Bucket_State_Filled_Milk", 1))
    K.eq(hc("*Container_Bucket_State_Filled_Milk|*Container_Bucket_State_Filled_Mosshorn_Milk"), 1, "HAVE the milk bucket state id (the shipped pattern)")
    # ---- the state side: haveDue throttle, have() progress rises only, done at count, claims once
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    coins = []
    br.put("coins:fn:add", PyFn(lambda a: coins.append(int(a[1])) or Long(1000)))
    br.put("feed:fn:push", PyFn(lambda a: Boolean.TRUE))
    br.put("shard:fn:door", PyFn(lambda a: JString("+")))
    u, p, s = X.player(45)
    L = Defs.line("archipelago")
    K.check(X.want(u) & TB["have"], "HAVE the archipelago gives the have bit")
    p.haveAt = 0
    K.check(bool(Eng.haveDue(p, Long(1000))), "HAVE haveDue: the first look is due")
    K.check(not bool(Eng.haveDue(p, Long(2500))), "HAVE ... not again within 2 s")
    K.check(bool(Eng.haveDue(p, Long(3000))), "HAVE ... due again 2 s later")
    hv = Eng.WANT.get(u)
    Eng.WANT.put(u, Integer(int(hv) & ~TB["have"]))
    p.haveAt = 0
    K.check(not bool(Eng.haveDue(p, Long(99000))), "HAVE no have bit = never due (no inventory look)")
    Eng.WANT.put(u, hv)
    st2, hb2 = SIC(9), SIC(9)
    cs2 = JArray(IC)([st2, hb2, SIC(1)])
    hb2.addItemStack(IS("Plant_Fruit_Apple", 3))
    K.check(bool(Eng.have(p, cs2)) and rows_of(s, L)["archi_apples"][1] == "3/5", "HAVE 3 apples held -> Pick 5 apples 3/5 (%s)" % (rows_of(s, L)["archi_apples"],))
    hb2.clear()
    hb2.addItemStack(IS("Plant_Fruit_Apple", 1))
    Eng.have(p, cs2)
    K.eq(rows_of(s, L)["archi_apples"][1], "3/5", "HAVE eating 2 does not lower the progress (the most held so far)")
    K.check(not bool(Eng.have(p, cs2)), "HAVE the same look again changes nothing")
    hb2.addItemStack(IS("Plant_Fruit_Apple", 4))
    Eng.have(p, cs2)
    K.check(bool(s.isDone("archipelago.archi_apples")), "HAVE 5 apples held -> done")
    hb2.clear()
    Eng.have(p, cs2)
    K.check(bool(s.isDone("archipelago.archi_apples")), "HAVE ... and stays done when they are gone")
    hb2.addItemStack(IS("Tool_Capture_Crate", 1))
    Eng.have(p, cs2)
    K.check(not bool(s.isDone("archipelago.archi_ranchkit")) and rows_of(s, L)["archi_ranchkit"][1] == "1/2", "HAVE the kit: a crate only = 1/2 (%s)" % (rows_of(s, L)["archi_ranchkit"],))
    st2.addItemStack(IS("Tool_Shears_Basic", 1))
    Eng.have(p, cs2)
    K.check(bool(s.isDone("archipelago.archi_ranchkit")) and not bool(s.isDone("archipelago.archi_capture")), "HAVE crate + shears = Take the ranch kit; the EMPTY crate is no capture")
    st2.addItemStack(full)
    Eng.have(p, cs2)
    K.check(bool(s.isDone("archipelago.archi_capture")), "HAVE a full crate (CapturedEntity) = Catch a baby animal in a crate")
    st2.addItemStack(IS("*Container_Bucket_State_Filled_Milk", 1))
    st2.addItemStack(IS("Ingredient_Fabric_Scrap_Wool", 2))
    p.haveAt = 0
    Eng.have(p, cs2)
    K.check(bool(s.isDone("archipelago.archi_milk")) and bool(s.isDone("archipelago.archi_wool")) and not bool(s.isDone("archipelago.archi_egg")),
            "FIXL milk + wool done, the optional egg still open")
    t0 = int(p.haveAt) - int(JClass("java.lang.System").currentTimeMillis())
    K.check(14000 <= t0 <= 15001, "FIXL only the optional egg left -> the next look waits 15 s (HAVE_OPT_MS), not 2 s (%d ms)" % t0)
    K.check(not bool(Eng.haveDue(p, Long(int(JClass("java.lang.System").currentTimeMillis()) + 3000))), "FIXL ... not due 3 s later")
    p.haveAt = 0
    st2.addItemStack(IS("Food_Egg", 1))
    Eng.have(p, cs2)
    K.check(bool(s.isDone("archipelago.archi_milk")) and bool(s.isDone("archipelago.archi_wool")) and bool(s.isDone("archipelago.archi_egg")),
            "HAVE milk bucket / wool / egg in one look -> Milk a cow, Shear a sheep, Collect an egg")
    for t_, c_ in (("archi_apples", 50), ("archi_capture", 50), ("archi_egg", 60)):
        K.eq(issued(X, s, u, "coins|%d|%s:archipelago.%s:" % (c_, u, t_)), 1, "HAVE %s issued its coins once" % t_)
    for i in range(3):
        Eng.have(p, cs2)
    K.eq(issued(X, s, u, "coins|50|%s:archipelago.archi_capture:" % u), 1, "HAVE more looks never pay again")
    K.check(not (X.want(u) & TB["have"]), "HAVE every have part done -> the have bit is gone (no more looks)")
    K.check(not bool(Eng.have(p, cs2)) and not bool(Eng.have(p, None)), "HAVE nothing open / no containers: false")
    s.frozen = True
    K.check(not bool(Eng.have(p, cs2)), "HAVE a frozen state: nothing")
    s.frozen = False
    # ---- havePl: a real Player (Unsafe), an empty Inventory -> no throw, false; null = false
    Player = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    Inv = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    U_ = T03.unsafe()
    pl = U_.allocateInstance(Player.class_)
    set_ = False
    k = Player.class_
    while k is not None and not set_:
        for f in k.getDeclaredFields():
            if f.getType() == Inv.class_:
                f.setAccessible(True)
                f.set(pl, Inv())
                set_ = True
                break
        k = k.getSuperclass()
    u2, p2, s2 = X.player(46)
    try:
        r = bool(Eng.havePl(p2, pl))
        K.check(set_ and not r, "HAVE havePl with a real Player + an empty Inventory: storage / hotbar / backpack read, nothing held -> false")
    except Exception as ex:
        K.check(False, "HAVE havePl threw on an empty Inventory: %s" % str(ex)[:200])
    K.check(not bool(Eng.havePl(p2, None)), "HAVE havePl(null) = false")
    # ---- the parser: meta on a non-have part is a problem + ignored; a have part keeps it
    PR = JClass("java.util.Properties")
    pr = PR()
    for k_, v_ in (("line", "zz"), ("task.1.id", "a"), ("task.1.type", "gather"), ("task.1.match", "Food_Egg"), ("task.1.meta", "X"),
                   ("task.2.id", "b"), ("task.2.type", "have"), ("task.2.match", "Tool_Capture_Crate"), ("task.2.meta", "CapturedEntity"), ("task.2.count", "2")):
        pr.setProperty(k_, v_)
    err = JClass("java.util.ArrayList")()
    ln = Defs.parse(pr, "zz.properties", err)
    es = [str(e) for e in err]
    K.check(ln is not None and str(ln.tasks[0].parts[0].meta) == "" and any("meta works on have parts only" in e for e in es),
            "HAVE meta on a gather part: a problem line + ignored (%s)" % es)
    K.check(str(ln.tasks[1].parts[0].meta) == "CapturedEntity" and int(ln.tasks[1].parts[0].count) == 2 and int(ln.tasks[1].parts[0].type) == TB["have"],
            "HAVE a have part: type bit 1<<14, count, meta kept")
    K.save()


# ---------------------------------------------------------------------------------------------------- FS44: the old shipped first_shard
def _old_tut(new_text):
    """0.4.3's shipped tutorial text = the 0.4.4 one with first_shard's old values (and without the 2 new header lines)"""
    t = new_text
    t = "\n".join(l for l in t.split("\n") if not l.startswith("# 0.4.4: first_shard") and not l.startswith("# (meta=<key>"))
    n = [l for l in t.split("\n") if l.endswith(".id=first_shard")][0].split(".")[1]
    p = "task.%s." % n
    t = t.replace(p + "name=Open a shard door\n", p + "name=Get your first shard\n")
    t = t.replace(p + "hint=Every island around your spawn has a shard door - reach that skill's level 5, right click the door and press Enter Shard\n", p + "hint=/island\n")
    t = t.replace(p + "requires=shard:fn:door\n", p + "requires=island:fn:shards\n")
    t = t.replace(p + "match=shard:door:*\n", p + "match=island:shard\n" + p + "caller=islands\n")
    return t, p


def run_fs44(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, FAKE_DIR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Defs = JClass(PKG + "QDefs")
    old, p = _old_tut(str(Defs.TUTORIAL))
    K.check(p + "match=island:shard\n" in old and p + "caller=islands\n" in old and "shard:door" not in old and "0.4.4:" not in old,
            "FS the 0.4.3 shipped tutorial rebuilt (old first_shard, no 0.4.4 header)")
    for name, txt, want in (("fsold", old, ("Open a shard door", "shard:door:*", "shard:fn:door", "")),
                            ("fsedit", old.replace(p + "match=island:shard\n", p + "match=island:shard|my:event\n").replace(p + "name=Get your first shard\n", p + "name=My shard task\n"),
                             ("My shard task", "island:shard|my:event", "island:fn:shards", "islands")),
                            ("fsname", old.replace(p + "name=Get your first shard\n", p + "name=My shard task\n"),
                             ("My shard task", "shard:door:*", "shard:fn:door", ""))):
        base = os.path.join(scratch, name, "Skyy_SkyyQuests")
        os.makedirs(os.path.join(base, "quests"), exist_ok=True)
        os.makedirs(os.path.join(scratch, name, "Skyy_SkyyIslands"), exist_ok=True)
        open(os.path.join(scratch, name, "Skyy_SkyyIslands", "hub.properties"), "w").write("world=skyy-hub\n")
        tf = os.path.join(base, "quests", "tutorial.properties")
        open(tf, "wb").write(txt.encode("utf-8"))
        E = T03.Env(base)
        E.start()
        fs = [t for t in E.P("QDefs").line("tutorial").tasks if str(t.id) == "first_shard"][0]
        got = (str(fs.name), str(fs.parts[0].match), str(fs.requires), str(fs.parts[0].caller))
        K.eq(got, want, "FS %s: first_shard loads as %s" % (name, (want,)))
        K.check(open(tf, "rb").read() == txt.encode("utf-8") and not os.path.exists(tf + ".0.3.3.new"), "FS %s: the file on disk is untouched (in memory only)" % name)
        K.check(str(fs.reward) == "coins:50,item:Ingredient_Bar_Iron:2" and str(fs.hint) != "" , "FS %s: the reward is unchanged (%s)" % (name, fs.reward))
    pr = JClass("java.util.Properties")()
    pr.setProperty("task.3.id", "first_shard")
    pr.setProperty("task.3.p1.type", "event")
    pr.setProperty("task.3.p1.match", "island:shard")
    K.check(not bool(Defs.shard044(pr)) and str(pr.getProperty("task.3.p1.match")) == "island:shard", "FS a first_shard with parts (an owner's) is left alone")
    K.check(not bool(Defs.shard044(JClass("java.util.Properties")())), "FS no first_shard = nothing")
    K.save()


# ---------------------------------------------------------------------------------------------------- LIVE44: start twice on the live copy
def run_live44(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    if home is None or not os.path.isdir(home):
        K.check(False, "LV44 no live copy")
        K.save()
        return
    mods = os.path.dirname(home)
    players0 = dict((f, open(os.path.join(home, "players", f), "rb").read()) for f in os.listdir(os.path.join(home, "players")))
    had = os.path.isfile(os.path.join(home, "quests", "archipelago.properties"))
    h0 = HK.tree_hash(mods)
    X = T040.QStage(K, scratch, "lv44", base=home)
    h1 = HK.tree_hash(mods)
    new = sorted(k for k in h1 if h0.get(k) != h1[k])
    K.check(not had and new == [os.path.join("Skyy_SkyyQuests", "quests", "archipelago.properties")] and not [k for k in h0 if k not in h1],
            "LV44 start 1 writes exactly ONE new file, quests/archipelago.properties: %s" % new)
    K.check(not [str(x) for x in X.Defs.PROBLEMS], "LV44 no file problems: %s" % [str(x) for x in X.Defs.PROBLEMS])
    X.Env.start()
    K.eq(HK.tree_hash(mods), h1, "LV44 start 2 writes nothing")
    L = X.Defs.line("archipelago")
    fs = [t for t in X.Defs.line("tutorial").tasks if str(t.id) == "first_shard"][0]
    K.check(L is not None and len(L.tasks) == 30, "LV44 the archipelago line loads on the live copy")
    K.notes.append("LV44 live first_shard loads as: %s / %s / %s" % (fs.name, fs.parts[0].match, fs.requires))
    K.check(str(fs.parts[0].match) == "shard:door:*", "LV44 the live tutorial's first_shard loads as shard:door:* (live file: %s)" % fs.parts[0].match)
    U = JClass("java.util.UUID")
    n = 0
    for f, raw in sorted(players0.items()):
        pk = f[:-len(".properties")]
        try:
            u = U.fromString(pk)
        except Exception:
            continue
        p = X.P("QP")(u, None)
        p.pk = pk
        p.world = "skyy-island-a1"
        p.loaded = True
        X.Eng.PLAYERS.put(u, p)
        s = X.Sto.read(pk, u)
        s.owner = u
        X.Sto.CACHE.put(pk, s)
        X.Eng.rebuild(u, s)
        P2 = JClass("java.util.Properties")()
        P2.load(JClass("java.io.StringReader")(raw.decode("utf-8")))
        P3 = JClass("java.util.Properties")()
        P3.load(JClass("java.io.StringReader")(str(s.textU())))
        lost = sorted(str(k) for k in P2.stringPropertyNames() if P3.getProperty(k) is None)
        claims0 = sorted(str(k) for k in P2.stringPropertyNames() if str(k).startswith("claim."))
        K.check(not bool(s.frozen) and not lost, "LV44 live profile %s loads, keeps every key (lost %s)" % (f, lost))
        K.check(bool(X.Eng.lineActive(s, L)) and not [k for k in P3.stringPropertyNames() if "archipelago." in str(k)],
                "LV44 ... the archipelago line is active for it, with no key of its own yet (a fresh start, nothing paid)")
        K.eq(len([str(c) for c in s.claims]), len(claims0), "LV44 ... no claim added (no old reward paid again)")
        n += 1
    K.check(n >= 1, "LV44 %d live profile(s) checked" % n)
    K.eq(HK.tree_hash(mods), h1, "LV44 loading every profile wrote nothing")
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
        env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
        os.makedirs(env["TEMP"], exist_ok=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mkfake", FAKE_DIR, "--jar", JAR, "--dir", SCRATCH], env=env)
        if r.returncode != 0:
            sys.exit("the stand-in classes were not compiled")
    lg = T033.legacy
    phases = [("archi44", run_archi44), ("have44", run_have44), ("fs44", run_fs44), ("live44", run_live44), ("wid43", T043.run_wid43), ("acc42", T042.run_acc42), ("gear41", T041.run_gear41), ("page40", T040.run_page40),
              ("claim40", T040.run_claim40), ("mig34", T034.run_mig34), ("fish34", T034.run_fish34),
              ("merge", T033.run_merge), ("chain", T033.run_chain), ("migt", T033.run_migt),
              ("isl", lg(T040.T032.run_isl)), ("snd", lg(T040.T031.run_snd)), ("defs", lg(T03.run_defs)), ("engine", lg(T03.run_engine)),
              ("life", lg(T03.run_life)), ("pay", lg(T03.run_pay)), ("crash", lg(T03.run_crash)), ("static", lg(T03.run_static)),
              ("npc", lg(T03.run_npc)), ("board", lg(T03.run_board)), ("fish", lg(T03.run_fish)), ("live40", T040.run_live40),
              ("live41", T041.run_live41)]
    if not os.path.isfile(T034.FISH17):
        print("NOTE: %s is not built here - phases fish34 + fish skipped (nothing in 0.4.4 touches fishing)" % T034.FISH17)
        phases = [ph for ph in phases if ph[0] not in ("fish34", "fish")]
    only = HK.arg("--only")
    if only:
        phases = [ph for ph in phases if ph[0] in only.split(",")]
    try:
        HK.run("SkyyQuests", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, phases, os.path.abspath(__file__), live=(T040.LIVE_Q, "Skyy_SkyyQuests"),
               removed=REMOVED)
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(FAKE_DIR, ignore_errors=True)
    sys.exit(1 if HK.FAILS else 0)
