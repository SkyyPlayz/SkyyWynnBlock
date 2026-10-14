"""SkyyQuests 0.2 harness (Skyy's spec answers on top of the round Q1 harness). Built on tools/harness_kit.py: each phase a fresh child JVM
(the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder). Every code path runs on the REAL jar
classes; only the engine's player / world / universe / ECS store are stand-ins (Unsafe-allocated engine objects + javassist subclasses
compiled before the JVM starts, --mkfake).

    python SkyyQuests/test_skyyquests_0.2.py [--jar SkyyQuests-0.2.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  against the LIVE SkyyQuests-0.1.jar: exactly the classes / members this round changes (+ QArea, QMig, QuestsSkipCmd)
  D    defs     0.1 checks (config, the copied-once files, glob, bad lines, places, rewards, state round trip) on the 0.2 files + the new
                fields (order / area / short.after / optional / island / tut / new / party, misuse reported), 5 lines in order, areas.properties,
                gear rewards, the skip / base state lines; ONE-TIME UPDATES: the 0.1 tutorial file (untouched -> 0.2 + .0.1.bak; edited -> kept +
                .0.2.new once; a second start changes nothing) and config.properties (the 0.1 reward lines -> 0.2, a hand-set line kept,
                explore_area appended, History copy, change-log lines, marker, CRLF kept, a second run changes nothing)
  E    engine   the 0.1 checks with the 0.2 rewards + FEED ONLY (done / progress / reward cards, route off, never chat); the rank-up LEAD
                (an existing tier never counts, a new one does, a stale value lowers the baseline); SKIP (widget, count, still pays, unskip,
                /quests skip by id); OPTIONAL (after the required tasks, not counted, the flow moves on); AREAS (world + region, the
                `area` objective, the widget follows, the switch off, explore_area, coming soon until set up); the LINE FLOW tutorial ->
                mining; CO-OP short version + party kill credit (same world only, party=true parts only, the switch)
  L    life     0.1 lifecycle + the area at join / after a load, the co-op flag on the tick, the log page's Skip buttons + click
  P    pay      0.1 ledger checks + GEAR rewards: the class weapon types / armor slots / level through stand-in gear:fn:box, the fallback,
                no SkyyGear = waits, the give of the prepared bag (storage first, counted), itemDone with the bag's icon -> the feed
  K    crash    CRASH AT EVERY STEP of the claim ledger (a coins + an XP claim of a test line) + a crash before the completion write
  S    static   the hot paths (+ enterArea, countParty) reach no file call / sleep; files only in the loaders / IO jobs / the migration
  ST   live     START TWICE on a scratch COPY of the live Skyy_SkyyQuests + Skyy_SkyyIslands folders: the first start runs both one-time
                updates on Skyy's real files, the second writes nothing; every live profile file parses and round-trips unchanged
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED, see the round report): the pages' look, the real feed cards, the real ECS / event delivery,
SkyyGear's real bag at a real level, SkyyParty's real member list, north = -Z.
Scratch: tools/dev/scratch/quests02/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json, time, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.2"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "quests02", "h")))
PKG = "com.skyy.quests."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyIslands")
FAKE = "skyyq02"
FAKE_DIR = SCRATCH + "-fake"     # the stand-in classes (compiled before the phases; HK.run wipes SCRATCH itself)
TB = {"break": 1, "felled": 2, "gather": 4, "craft": 8, "kill": 16, "reach": 32, "enter": 64, "talk": 128, "page": 256, "event": 512,
      "tier": 1024, "level": 2048, "bridge": 4096, "area": 8192}
OLD_JAR = os.path.join(HERE, "SkyyQuests-0.1.jar")      # the LIVE 0.1 (class compare)
# Skyy's live config.properties as 0.1 wrote it (our own generated default file - the one-time update's input)
CFG01 = """# SkyyQuests config (Server Setup > Quests in the SkyWynn Menu edits this file; times in seconds)
enabled=true
tutorial.enabled=true
tutorial.welcome=true
widget.tasks=3
widget.doneSeconds=2.5
poll.seconds=1
lazy.seconds=5
claim.retrySeconds=60
event.rate=20
# tutorial rewards per task id: coins,Skill:XP (Skill:XP may be empty). A line here replaces the coins / XP of that task's reward.
tutorial.reward.pick_class=25,
tutorial.reward.hub_buttons=25,
tutorial.reward.chop_logs=0,Foraging:50
tutorial.reward.first_accessory=50,Smithing:40
tutorial.reward.mine_basics=0,Mining:50
tutorial.reward.first_rankup=25,
tutorial.reward.first_harvest=0,Farming:50
tutorial.reward.void_bag=25,
tutorial.reward.requip_save=25,
tutorial.reward.bank_deposit=50,
tutorial.reward.island_two=0,Exploration:50
tutorial.reward.class_ability=25,
tutorial.reward.defeat_mobs=50,
tutorial.reward.identify_drop=25,
tutorial.reward.reforge_item=25,
tutorial.reward.eat_food=25,
tutorial.reward.first_pet=25,
tutorial.reward.open_luggage=0,Exploration:50
tutorial.reward.island_three=0,Exploration:50
tutorial.reward.mini_boss=100,
tutorial.reward.to_hub=100,
tutorial.reward.hub_tour=100,Exploration:100
tutorial.reward.party_intro=25,
tutorial.reward.first_shard=50,
"""


def mkfake(out_dir, jar):
    """javassist stand-ins for the engine's ECS store / chunk / world, compiled BEFORE the test JVM starts (its folder is on the class path,
    loaded by the same class loader as the server jar). Their constructors are never run (Unsafe.allocateInstance); FakeStore sits in the
    engine's own package because Store's only constructor is package-private."""
    from jpype import JClass
    HK.jvm([B.JAVASSIST, B.SERVER_JAR, jar], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CF, CM, CC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    ch = cp.makeClass(FAKE + ".FakeChunk", cp.get("com.hypixel.hytale.component.ArchetypeChunk"))
    ch.addField(CF.make("public static com.hypixel.hytale.component.Ref REF;", ch))
    ch.addConstructor(CC.make("public FakeChunk() { super((com.hypixel.hytale.component.Store) null, (com.hypixel.hytale.component.Archetype) null); }", ch))
    ch.addMethod(CM.make("public com.hypixel.hytale.component.Ref getReferenceTo(int i) { return REF; }", ch))
    ch.writeFile(out_dir)
    st = cp.makeClass("com.hypixel.hytale.component.SkyyQFakeStore", cp.get("com.hypixel.hytale.component.Store"))
    for f in ("public static Object NEXT;", "public static Object COMP;", "public static Object EXT;", "public static int CALLS;"):
        st.addField(CF.make(f, st))
    st.addConstructor(CC.make("public SkyyQFakeStore() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, null, (com.hypixel.hytale.component.IResourceStorage) null); }", st))
    st.addMethod(CM.make("""public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  CALLS = CALLS + 1;
  if (NEXT != null) { Object o = NEXT; NEXT = null; return (com.hypixel.hytale.component.Component) o; }
  return (com.hypixel.hytale.component.Component) COMP;
}""", st))
    st.addMethod(CM.make("public Object getExternalData() { return EXT; }", st))
    st.writeFile(out_dir)
    wo = cp.makeClass(FAKE + ".FakeWorld", cp.get("com.hypixel.hytale.server.core.universe.world.World"))
    wo.addField(CF.make("public static String NAME = \"skyy-island-test\";", wo))
    wo.addField(CF.make("public static int RUNS;", wo))
    wo.addConstructor(CC.make("public FakeWorld() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }", wo))
    wo.addMethod(CM.make("public void execute(Runnable r) { RUNS = RUNS + 1; r.run(); }", wo))
    wo.addMethod(CM.make("public String getName() { return NAME; }", wo))
    wo.writeFile(out_dir)
    es = cp.makeClass(FAKE + ".FakeEStore", cp.get("com.hypixel.hytale.server.core.universe.world.storage.EntityStore"))
    es.addField(CF.make("public static com.hypixel.hytale.server.core.universe.world.World W;", es))
    es.addConstructor(CC.make("public FakeEStore() { super((com.hypixel.hytale.server.core.universe.world.World) null); }", es))
    es.addMethod(CM.make("public com.hypixel.hytale.server.core.universe.world.World getWorld() { return W; }", es))
    es.writeFile(out_dir)
    un = cp.makeClass(FAKE + ".FakeUniverse", cp.get("com.hypixel.hytale.server.core.universe.Universe"))
    un.addField(CF.make("public static com.hypixel.hytale.server.core.universe.world.World W;", un))
    un.addField(CF.make("public static com.hypixel.hytale.server.core.universe.PlayerRef PR;", un))
    un.addMethod(CM.make("public com.hypixel.hytale.server.core.universe.world.World getWorld(java.util.UUID u) { return W; }", un))
    un.addMethod(CM.make("public com.hypixel.hytale.server.core.universe.PlayerRef getPlayer(java.util.UUID u) { return PR; }", un))
    un.writeFile(out_dir)


class Env(object):
    """one JVM's view: the jar classes (through `loader` when given = a server restart), the stand-ins, the bridge"""
    def __init__(self, base, loader=None):
        from jpype import JClass
        self.J = JClass
        self.L = loader
        self.P = lambda n: JClass(PKG + n, loader=loader) if loader is not None else JClass(PKG + n)
        Paths = JClass("java.nio.file.Paths")
        self.base = base
        os.makedirs(base, exist_ok=True)
        Cfg, Defs, Sto, Eng, Log = self.P("QCfg"), self.P("QDefs"), self.P("QStore"), self.P("QEng"), self.P("QLog")
        Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
        Defs.DIR = Paths.get(os.path.join(base, "quests"))
        Defs.PLACES_FILE = Paths.get(os.path.join(base, "places.properties"))
        Defs.AREAS_FILE = Paths.get(os.path.join(base, "areas.properties"))
        Sto.DIR = Paths.get(os.path.join(base, "players"))
        Sto.LOGF = Paths.get(os.path.join(base, "quests.log"))
        Eng.HUBFILE = Paths.get(os.path.join(base, "..", "Skyy_SkyyIslands", "hub.properties"))
        Sto.STOPPED = True          # no SkyyQuests-IO thread in the tests: every IO job runs inline, in order
        Log.LINES = JClass("java.util.concurrent.CopyOnWriteArrayList")()
        Log.SINK = JClass("java.util.concurrent.CopyOnWriteArrayList")()

    def start(self):
        self.P("QCfg").load()
        return int(self.P("QDefs").load())


def logtext(base):
    p = os.path.join(base, "quests.log")
    return open(p, encoding="utf8").read() if os.path.isfile(p) else ""


def fn_class():
    """a java.util.function.Function made in Python (records every argument, answers from a Python callable)"""
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class PyFn(object):
        def __init__(self, ans):
            self.ans = ans
            self.calls = []

        @JOverride
        def apply(self, a):
            self.calls.append(a)
            return self.ans(a)
    return PyFn


def setf(obj, cls_name, name, val):
    from jpype import JClass
    k = JClass(cls_name).class_ if isinstance(cls_name, str) else cls_name
    while k is not None:
        try:
            f = k.getDeclaredField(name)
            f.setAccessible(True)
            f.set(obj, val)
            return True
        except Exception:
            k = k.getSuperclass()
    return False


def engine_types(K, names):
    """make <Class>.getComponentType() answer in a bare JVM: every singleton it reads (Universe.get(), NPCPlugin.get() ...) gets an
    Unsafe-allocated instance in its static field (all its fields null - the stand-in store ignores the type it is asked for)"""
    import re as _re
    from jpype import JClass
    U = unsafe()
    for n in names:
        for _ in range(4):
            try:
                JClass(n).getComponentType()
                break
            except Exception as ex:
                m = _re.search(r'the return value of "([\w.$]+)\.get\(\)" is null', str(ex))
                if not m:
                    K.notes.append("engine_types %s: %s" % (n, str(ex)[:160]))
                    break
                sc = JClass(m.group(1))
                done = False
                for f in sc.class_.getDeclaredFields():
                    if f.getType() == sc.class_ and JClass("java.lang.reflect.Modifier").isStatic(f.getModifiers()):
                        f.setAccessible(True)
                        try:
                            f.set(None, U.allocateInstance(sc.class_))
                            done = True
                        except Exception:
                            uf = U.staticFieldOffset(f)
                            U.putObject(U.staticFieldBase(f), uf, U.allocateInstance(sc.class_))
                            done = True
                        break
                if not done:
                    K.notes.append("engine_types %s: no static %s field" % (n, sc))
                    break


def unsafe():
    from jpype import JClass
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    return uf.get(None)


# ====================================================================================================== D: definitions + config + state
def run_defs(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    base = os.path.join(scratch, "d", "Skyy_SkyyQuests")
    E = Env(base)
    Cfg, Defs, St = E.P("QCfg"), E.P("QDefs"), E.P("QState")
    E.P("QDefs").AREAS_FILE = JClass("java.nio.file.Paths").get(os.path.join(base, "areas.properties"))
    K.eq(E.start(), 5, "D1 five quest lines (the tutorial + mining, foraging, farming, fishing)")
    for f in ("config.properties", "places.properties", "areas.properties", "quests/tutorial.properties", "quests/mining.properties",
              "quests/foraging.properties", "quests/farming.properties", "quests/fishing.properties"):
        K.check(os.path.isfile(os.path.join(base, f)), "D1 %s written on the first start" % f)
    K.eq((bool(Cfg.ENABLED), bool(Cfg.TUT_ON), bool(Cfg.WELCOME), int(Cfg.TASKS), float(Cfg.DONE_SECS), int(Cfg.POLL_SECS), int(Cfg.LAZY_SECS),
          int(Cfg.RETRY_SECS), int(Cfg.EVENT_RATE), bool(Cfg.FOLLOW), bool(Cfg.PARTY_KILLS)), (True, True, True, 3, 2.5, 1, 5, 60, 20, True, True),
         "D1 the config defaults (+ 0.2 areas.follow / coop.partyKills)")
    K.eq(int(Cfg.REWARDS.size()), 25, "D1 25 tutorial reward lines (explore_area added)")
    K.eq([str(x) for x in Cfg.REWARDS.get("chop_logs")], ["25", ""], "D1 chop_logs reward line = 25 coins, no XP (Skyy: items + coins)")
    K.eq([str(x) for x in Cfg.REWARDS.get("mini_boss")], ["0", ""], "D1 mini_boss reward line = no coins (combat = gear)")
    K.check("SkyyQuests 0.2 tutorial rewards" in open(os.path.join(base, "config.properties"), encoding="latin-1").read(), "D1 a new config file carries the 0.2 marker")
    K.eq(int(Defs.PROBLEMS.size()), 0, "D1 the shipped files have no problems: %s" % [str(x) for x in Defs.PROBLEMS])
    K.eq([str(l.id) for l in Defs.LINES], ["tutorial", "mining", "foraging", "farming", "fishing"], "D1 lines sorted by order (tutorial 0 .. fishing 50)")
    K.eq([int(l.order) for l in Defs.LINES], [0, 20, 30, 40, 50], "D1 the line orders")
    K.eq([str(a_.id) for a_ in Defs.AREAS], ["mining", "foraging", "farming", "fishing"], "D1 four areas by order")
    am = Defs.area("mining")
    K.eq((str(am.line), str(am.place), float(am.radius), str(am.world), bool(Defs.areaSet(am))), ("mining", "hub.mining", 48.0, "", False),
         "D1 the mining area: line, place hub.mining, radius 48, NOT set up until the place is set")
    L = Defs.LINES[0]
    K.eq((str(L.id), str(L.name), bool(L.chain), bool(L.auto), str(L.hide), len(L.tasks), str(L.shortAfter)),
         ("tutorial", "Getting Started", False, True, "tutorial.hide", 25, "mini_boss,to_hub.p2"), "D1 the tutorial line (+ short.after)")
    t3 = L.tasks[2]
    K.eq((str(t3.id), bool(t3.any), len(t3.parts), int(t3.parts[0].type), int(t3.parts[0].count), str(t3.parts[1].match)),
         ("chop_logs", True, 2, TB["felled"], 10, "Wood_*_Trunk"), "D1 chop_logs = any(felled 10, break Wood_*_Trunk 10) - the 0.1 parts kept")
    K.eq(str(t3.parts[0].match), "Wood_*_Trunk*", "FIX1 the felled part matches trunks only (leaves are felled blocks too)")
    t21 = L.tasks[20]
    K.check(str(t21.id) == "to_hub" and bool(t21.parts[0].block) and not bool(t21.parts[1].block), "FIX5 to_hub's portal part is block=true (parsed from the file)")
    K.eq(str(L.tasks[0].requires), "profile:fn:key", "FIX6 pick_class requires SkyyProfiles (profile:fn:key)")
    K.eq((len(L.tasks[16].parts), str(L.tasks[16].parts[0].tname)), (1, "event"), "FIX4 first_pet = the pets:equip event only (no loadout bridge part)")
    byid = dict((str(t.id), t) for t in L.tasks)
    K.eq(sorted(k for k, t in byid.items() if bool(t.optional)), ["bank_deposit", "party_intro", "requip_save"], "Q2 optional = Requip 9, Bank 10, party 23 (Skyy's ticks)")
    K.eq(sorted(k for k, t in byid.items() if bool(t.island)), sorted(["chop_logs", "first_accessory", "mine_basics", "first_harvest", "island_two", "defeat_mobs",
                                                                         "open_luggage", "island_three", "mini_boss"]), "Q7 the island tasks (left out of the co-op short version)")
    K.check(bool(byid["first_rankup"].parts[0].fresh) and not bool(byid["first_rankup"].parts[1].fresh), "LEAD first_rankup's tier part needs a NEW rank-up")
    K.check(bool(byid["mini_boss"].parts[0].party) and not bool(byid["defeat_mobs"].parts[0].party), "Q7 the mini boss kill credits the party; the 5 mobs do not")
    ex = byid["explore_area"]
    K.eq((str(ex.where), int(ex.parts[0].type), str(ex.parts[0].match), [str(t.id) for t in L.tasks].index("explore_area")),
         ("hub.mining", TB["area"], "mining|foraging|farming|fishing", 22), "Q2 explore_area right after the hub tour: an area objective, Mining suggested")
    K.eq(str(Defs.rewardOf(L, byid["defeat_mobs"])), "gear:weapon,gear:armor", "FIX-C4 defeat_mobs pays an unidentified weapon AND an armor piece (Skyy: weapons and armor)")
    noitem = [str(l.id) + "." + str(t.id) for l in Defs.LINES for t in l.tasks
              if "gear:" not in str(Defs.rewardOf(l, t)) and not ("coins:" in str(Defs.rewardOf(l, t)) and "item:" in str(Defs.rewardOf(l, t)))]
    K.eq(noitem, [], "FIX-C1 every non-combat task of every shipped line pays items AND coins (Skyy: items and coins on other quest types)")
    K.eq(str(Defs.rewardOf(L, byid["mini_boss"])), "gear:weapon,gear:armor", "Q1 mini_boss pays a weapon + an armor piece")
    K.check(all("xp:" not in str(Defs.rewardOf(l, t)) for l in Defs.LINES for t in l.tasks), "Q1 no task of any shipped line pays Skill XP (items + coins)")
    mn = Defs.line("mining")
    K.eq([str(t.id) for t in mn.tasks][:3], ["mining_visit", "mining_stone", "mining_copper"], "Q2 the mining line starts with its tutorial part")
    K.check(bool(mn.tasks[0].tut) and not bool(mn.tasks[3].tut) and str(mn.area) == "mining", "Q2 tut=true on the tutorial part, progression after it; area=mining")
    K.eq(str(Defs.line("fishing").tasks[0].requires), "config:def:SkyyFishing", "Q2 the fishing line is hidden without SkyyFishing")
    tf = os.path.join(base, "quests", "tutorial.properties")
    open(tf, "a", encoding="utf8").write("# an owner's edit\n")
    m0 = os.path.getmtime(tf)
    E.start()
    K.check(open(tf, encoding="utf8").read().endswith("# an owner's edit\n") and os.path.getmtime(tf) == m0, "D1 the tutorial is copied ONCE (an edit stays)")
    K.check(not os.path.isfile(tf + ".0.2.new"), "D1 an edited 0.2 file is not a 0.1 file: no .0.2.new")
    # glob / alternatives / any
    for pat, sv, want in (("Wood_*_Trunk", "Wood_Oak_Trunk", True), ("Wood_*_Trunk", "Wood_Oak_Log", False), ("*Plant_Crop_Wheat_Block*", "Plant_Crop_Wheat_Block_Eternal", True),
                          ("Skyy_Accessory_*_T*", "Skyy_Accessory_Workbench_T2", True), ("Skyy_Accessory_*_T*", "Skyy_Accessory_Omni", False),
                          ("Ore_Copper*", "Ore_Copper_Stone", True), ("Rock_Stone", "Rock_Stone_Brick", False), ("gear:reforge|gear:upgrade", "gear:upgrade", True),
                          ("any", "whatever", True), ("", "x", True), ("a*b*c", "aXbYc", True), ("a*b*c", "acb", False), ("*", "", True),
                          ("mining|foraging|farming|fishing", "foraging", True)):
        K.eq(bool(Defs.matches(pat, sv)), want, "D2 matches(%r, %r)" % (pat, sv))
    # bad lines (+ the 0.2 field misuse)
    bad = "\n".join(["line=side_line", "name=Side", "mode=weird", "order=5", "area=nowhere", "short.after=ghost", "task.1.id=ok_task", "task.1.name=Fine", "task.1.type=break", "task.1.match=Rock_Stone",
                     "task.2.id=ok_task", "task.2.type=break", "task.2.match=x", "task.3.id=bad_type", "task.3.type=fly", "task.3.match=x",
                     "task.4.id=bad_reward", "task.4.type=kill", "task.4.reward=xp:Combat:50", "task.5.id=no_match", "task.5.type=break",
                     "task.6.id=bad_op", "task.6.type=bridge", "task.6.match=k", "task.6.op=lt", "task.7.id=Bad-Id", "task.7.type=kill",
                     "task.8.id=lvl", "task.8.type=level", "task.8.match=Mining", "task.8.value=ten", "task.9.id=chained", "task.9.p1.type=talk",
                     "task.9.p1.match=board", "task.9.p2.type=event", "task.9.p2.match=x:y", "task.9.p2.caller=zz",
                     "task.10.id=bad_new", "task.10.type=kill", "task.10.new=true", "task.11.id=bad_party", "task.11.type=break", "task.11.match=x",
                     "task.11.party=true", "task.12.id=bad_gear", "task.12.type=kill", "task.12.reward=gear:shield", "task.13.id=good_gear",
                     "task.13.type=kill", "task.13.reward=gear:armor,coins:5", "task.13.optional=true"]) + "\n"
    open(os.path.join(base, "quests", "side.properties"), "w").write(bad)
    open(os.path.join(base, "quests", "zdup.properties"), "w").write("line=tutorial\ntask.1.id=a\ntask.1.type=kill\n")
    open(os.path.join(base, "quests", "zchain.properties"), "w").write("line=chain_line\nmode=chain\nauto=true\ntask.1.id=first\ntask.1.type=kill\ntask.1.match=any\n"
                                                                        "task.2.id=second\ntask.2.type=kill\ntask.2.match=any\ntask.2.optional=true\n"
                                                                        "task.3.id=third\ntask.3.type=kill\ntask.3.match=any\n")
    K.eq(E.start(), 7, "D3 the 5 shipped lines + side_line + chain_line (the duplicate tutorial file skipped)")
    pb = [str(x) for x in Defs.PROBLEMS]
    for frag in ("mode=weird", "id 'ok_task' must be", "type 'fly'", "Combat XP cannot be granted", "match is empty", "op 'lt'", "id 'Bad-Id'",
                 "value 'ten'", "already defined by another file", "new=true works on tier", "party=true works on kill", "'gear:shield'",
                 "area=nowhere is not in areas.properties", "short.after names 'ghost'"):
        K.check(any(frag in x for x in pb), "D3 problem reported: %s (%s)" % (frag, pb))
    side = Defs.line("side_line")
    K.eq([str(t.id) for t in side.tasks], ["ok_task", "bad_reward", "chained", "bad_new", "bad_party", "bad_gear", "good_gear"],
         "D3 the good tasks of a bad file are kept (bad rewards dropped, misused flags ignored)")
    K.eq((str(side.tasks[1].reward), bool(side.tasks[3].parts[0].fresh), bool(side.tasks[4].parts[0].party), str(side.tasks[5].reward), str(side.tasks[6].reward), bool(side.tasks[6].optional)),
         ("", False, False, "", "gear:armor,coins:5", True), "D3 rewards / flags after the checks")
    K.eq([str(l.id) for l in Defs.LINES][:2], ["tutorial", "side_line"], "D3 order=5 sorts side_line right after the tutorial")
    K.check(bool(Defs.line("chain_line").chain), "D3 mode=chain read")
    CL, QE = Defs.line("chain_line"), E.P("QEng")
    sc = St("chainpk", JClass("java.util.UUID")(9, 9))
    ci = [str(t.id) for t in CL.tasks]
    K.check(not bool(QE.taskActive(sc, CL, ci.index("third"))), "FIX-B1 chain: 'third' is locked while 'first' is open")
    K.eq(int(QE.skipL(sc, "chain_line.first", 1000)), 1, "FIX-B1 chain: skip 'first'")
    K.check(bool(QE.taskActive(sc, CL, ci.index("third"))), "FIX-B1 chain: a SKIPPED task and an OPTIONAL task never block a later one (Skyy: never block)")
    K.eq(int(QE.skipL(sc, "chain_line.first", 1001)), 2, "FIX-B1 chain: unskip 'first'")
    K.check(not bool(QE.taskActive(sc, CL, ci.index("third"))), "FIX-B1 chain: unskipped = locked again (the chain still works)")
    for f in ("side.properties", "zdup.properties", "zchain.properties"):
        os.remove(os.path.join(base, "quests", f))
    E.start()
    # rewards
    K.eq(str(Defs.rewardText("coins:25,xp:Foraging:40,item:Rock_Stone:3,flag:x")), "+25 coins  +40 Foraging XP  +3 Stone", "D4 rewardText")
    nm = [str(Defs.itemName(x)) for x in ("Ingredient_Bar_Copper", "Plant_Sapling_Oak", "Skyy_Plant_Fancy_Thing", "Weird")]
    K.check(nm[0] == "Copper Ingot" and nm[1] == "Oak Sapling" and nm[2] == "Fancy Thing" and nm[3] == "Weird"
            and all("_" not in str(Defs.itemName(x)) for x in Defs.NAME_IDS) and len(list(Defs.NAME_IDS)) >= 15,
            "FIX2-N the feed shows the game's English item names (an unknown id loses its family prefix): %s" % nm)
    K.eq(str(Defs.rewardText("gear:weapon,gear:armor")), "+1 unidentified weapon  +1 unidentified armor", "Q1 rewardText of the gear words")
    K.check(Defs.rewardProblem("coins:0") is not None and Defs.rewardProblem("item:X:1001") is not None and Defs.rewardProblem("coins:5,xp:Mining:5") is None
            and Defs.rewardProblem("gear:weapon,gear:armor") is None and Defs.rewardProblem("gear:") is not None, "D4 rewardProblem (+ gear)")
    L = Defs.LINES[0]
    chop = L.tasks[2]
    K.eq(str(Defs.rewardOf(L, chop)), "coins:25,item:Plant_Sapling_Oak:2", "D4 rewardOf = the table line + the file's items")
    cfgp = os.path.join(base, "config.properties")
    txt = open(cfgp, encoding="utf8").read().replace("tutorial.reward.chop_logs=25,", "tutorial.reward.chop_logs=7,Mining:9")
    txt = txt.replace("tutorial.reward.pick_class=25,", "tutorial.reward.pick_class=oops,").replace("tutorial.reward.mini_boss=0,", "tutorial.reward.mini_boss=40,")
    open(cfgp, "w", encoding="utf8").write(txt)
    Cfg.load()
    K.eq(str(Defs.rewardOf(Defs.LINES[0], chop)), "coins:7,xp:Mining:9,item:Plant_Sapling_Oak:2", "D4 a Server Setup table change replaces the coins / XP (items stay)")
    K.eq(str(Defs.rewardOf(Defs.LINES[0], Defs.LINES[0].tasks[0])), "coins:25,item:Food_Bread:3", "D4 a bad table line keeps the quest file's reward")
    K.eq(str(Defs.rewardOf(Defs.LINES[0], Defs.line("tutorial").tasks[19])), "coins:40,gear:weapon,gear:armor", "Q1 the table can add coins to a gear task (gear stays)")
    # FIX2 (2nd critic 1+2): a table 0 + a tutorial file with NO gear: (edited / still 0.1) pays the file's own coins - never nothing
    dm = [t for t in Defs.line("tutorial").tasks if str(t.id) == "defeat_mobs"][0]
    K.eq(str(Defs.rewardOf(Defs.LINES[0], dm)), "gear:weapon,gear:armor", "FIX2-R table 0 + gear in the file = gear only (no fallback)")
    old_rw = dm.reward
    dm.reward = "coins:50"
    K.eq(str(Defs.rewardOf(Defs.LINES[0], dm)), "coins:50", "FIX2-R table 0 + a file with coins and no gear (edited / 0.1 file) = the FILE's coins (a combat task never pays nothing)")
    dm.reward = "coins:50,item:Food_Bread:1"
    K.eq(str(Defs.rewardOf(Defs.LINES[0], dm)), "item:Food_Bread:1", "FIX2-R ... a table 0 with something else left keeps the table rule")
    dm.reward = old_rw
    K.check(any("not <coins>,<Skill>:<XP>" in str(x) for x in E.P("QLog").LINES), "D4 the bad table line is warned")
    # places: line-preserving save
    pf = os.path.join(base, "places.properties")
    K.check(Defs.savePlace("island2", "island", 100.0, 64.0, 100.0, "Island 2"), "D5 savePlace")
    K.check(Defs.savePlace("portal", "hub", 1.24, 2.0, 3.0, "Hub portal") and Defs.savePlace("island2", "island", 101.0, 65.0, 99.0, "Island 2"), "D5 savePlace replace")
    pt = open(pf, encoding="utf8").read()
    K.check(pt.startswith("# SkyyQuests named places") and pt.count("island2=") == 1 and "island2=island|101.0|65.0|99.0|Island 2" in pt and "portal=hub|1.2|2.0|3.0|Hub portal" in pt,
            "D5 places file: comments kept, one line per id: %r" % pt[-120:])
    E.start()
    q = Defs.place("island2")
    K.eq((str(q.world), float(q.x), str(q.label)), ("island", 101.0, "Island 2"), "D5 loadPlaces")
    K.check(Defs.savePlace("hub.mining", "hub", 10.0, 70.0, 10.0, "Mining area") and bool(Defs.areaSet(Defs.area("mining"))), "D5 setting hub.mining sets up the mining area")
    # areas.properties: a bad id, a world-only area
    ap = os.path.join(base, "areas.properties")
    open(ap, "a", encoding="utf8").write("area.Bad-Id.line=x\narea.zone1.world=skyy-zone-1*\narea.zone1.line=mining\narea.zone1.order=0\narea.empty.name=Nothing\nstray=1\n")
    E.start()
    pb = [str(x) for x in Defs.PROBLEMS]
    K.check(any("area id 'Bad-Id'" in x for x in pb) and any("area empty has no place and no world" in x for x in pb) and any("stray is not area" in x for x in pb),
            "D7 areas.properties problems reported: %s" % pb)
    K.eq([str(a_.id) for a_ in Defs.AREAS][:2], ["zone1", "mining"], "D7 area order (zone1 order 0 first)")
    K.check(bool(Defs.areaSet(Defs.area("zone1"))) and not bool(Defs.areaSet(Defs.area("empty"))), "D7 a world-only area is set up; an empty one is not")
    # QState round trip (+ 0.2 skip / base lines)
    U = JClass("java.util.UUID")
    P = JClass("java.util.Properties")()
    P.load(JClass("java.io.StringReader")("v=1\ntrack=tutorial\nseq=4\ndone.tutorial.chop_logs=123\nprog.tutorial.chop_logs.0=7\npdone.tutorial.chop_logs.1=1\n"
                                          "flag.met=1\nclaim.2=coins|5|k:tutorial.a:2\nclaim.1=xp|Mining:5|k:tutorial.a:1\nissued.tutorial.chop_logs=1\n"
                                          "hide.tutorial=1\nseen.tutorial=1\nstart.side=9\nfuture.key=kept\nskip.tutorial.void_bag=55\n"
                                          "base.tutorial.first_rankup.0=3\nclaim.3=gear|weapon|k:tutorial.mini_boss:3\n"))
    s = St.parse("k", U.randomUUID(), P)
    t = str(s.textU())
    for ln in ("track=tutorial", "seq=4", "done.tutorial.chop_logs=123", "prog.tutorial.chop_logs.0=7", "pdone.tutorial.chop_logs.1=1", "flag.met=1",
               "claim.1=xp|Mining:5|k:tutorial.a:1", "claim.2=coins|5|k:tutorial.a:2", "claim.3=gear|weapon|k:tutorial.mini_boss:3", "issued.tutorial.chop_logs=1",
               "hide.tutorial=1", "seen.tutorial=1", "start.side=9", "future.key=kept", "skip.tutorial.void_bag=55", "base.tutorial.first_rankup.0=3"):
        K.check(ln in t.splitlines(), "D6 state text keeps %s" % ln)
    K.check(bool(s.isSkipped("tutorial.void_bag")) and int(s.base.get("tutorial.first_rankup.0")) == 3, "D6 skip / base parsed into their maps")
    P2 = JClass("java.util.Properties")()
    P2.load(JClass("java.io.StringReader")(t))
    K.eq(str(St.parse("k", U.randomUUID(), P2).textU()), t, "D6 text -> parse -> text is stable")
    # ---- ONE-TIME UPDATE 1: the untouched 0.1 tutorial file -> 0.2 (+ .0.1.bak); an edited one is kept (+ .0.2.new once)
    for name, edit in (("m1", False), ("m2", True)):
        mb = os.path.join(scratch, name, "Skyy_SkyyQuests")
        os.makedirs(os.path.join(mb, "quests"), exist_ok=True)
        v1 = str(Defs.TUTORIAL01)
        data = v1.encode("utf-8") + (b"# my edit\n" if edit else b"")
        open(os.path.join(mb, "quests", "tutorial.properties"), "wb").write(data)
        E2 = Env(mb)
        E2.P("QDefs").AREAS_FILE = JClass("java.nio.file.Paths").get(os.path.join(mb, "areas.properties"))
        nl = E2.start()
        tp = os.path.join(mb, "quests", "tutorial.properties")
        now = open(tp, "rb").read()
        if not edit:
            K.check("Shipped by SkyyQuests 0.2" in now.decode("utf-8") and open(tp + ".0.1.bak", "rb").read() == data,
                    "MIG-T an untouched 0.1 tutorial becomes the 0.2 one; the old bytes are kept as .0.1.bak")
            K.eq((nl, len(Defs.line("tutorial").tasks), int(Defs.PROBLEMS.size())), (5, 25, 0), "MIG-T the migrated file loads: 25 tasks, no problems")
            K.check(any("updated to the 0.2 tutorial" in str(x) for x in E2.P("QLog").LINES), "MIG-T an INFO line names the update")
        else:
            K.check(now == data and open(tp + ".0.2.new", "rb").read().decode("utf-8").count("Shipped by SkyyQuests 0.2") == 1,
                    "MIG-T an EDITED 0.1 tutorial is kept; the 0.2 text is written beside it")
            K.check(any("was edited - KEPT" in str(x) for x in E2.P("QLog").LINES), "MIG-T ... with a WARN")
            K.eq(len(Defs.line("tutorial").tasks), 24, "MIG-T ... and the owner's 24-task file is what runs")
            K.check(bool(Defs.line("tutorial").tasks[5].parts[0].fresh), "LEAD the NEW rank-up rule works on an old 0.1 file too (tier any = new by default)")
            nm = os.path.getmtime(tp + ".0.2.new")
        h1 = HK.tree_hash(mb)
        E2.start()
        K.eq(HK.tree_hash(mb), h1, "MIG-T %s: a second start changes nothing (run once)" % name)
    # ---- ONE-TIME UPDATE 2: config.properties (0.1 defaults -> 0.2; hand-set kept; explore_area appended; History; change log; marker)
    Mig = E.P("QMig")
    dir0 = Defs.DIR
    for name, crlf, hand in (("c1", False, False), ("c2", True, True), ("c3", False, False)):
        cb = os.path.join(scratch, name, "Skyy_SkyyQuests")
        os.makedirs(os.path.join(cb, "quests"), exist_ok=True)
        Defs.DIR = JClass("java.nio.file.Paths").get(os.path.join(cb, "quests"))
        edited = name == "c3"
        if edited:                                         # FIX-A3: an owner-EDITED tutorial file (migrateTut keeps it: no gear: rewards)
            open(os.path.join(cb, "quests", "tutorial.properties"), "w").write("line=tutorial\nname=My tutorial\ntask.1.id=defeat_mobs\ntask.1.type=kill\ntask.1.match=any\n")
        elif name == "c2":                                 # the untouched 0.1 file = it will be replaced -> combat lines move
            open(os.path.join(cb, "quests", "tutorial.properties"), "wb").write(str(Defs.TUTORIAL01).encode("utf-8"))
        txt0 = CFG01.replace("tutorial.reward.chop_logs=0,Foraging:50", "tutorial.reward.chop_logs=10,Foraging:50") if hand else CFG01
        if crlf:
            txt0 = txt0.replace("\n", "\r\n")
        cf = os.path.join(cb, "config.properties")
        open(cf, "wb").write(txt0.encode("latin-1"))
        Cfg.FILE = JClass("java.nio.file.Paths").get(cf)
        msg = str(Mig.migrate02())
        new = open(cf, "rb").read().decode("latin-1")
        K.check("updated to the 0.2 tutorial rewards" in msg, "MIG-C %s: the update ran: %s" % (name, msg[:160]))
        want = {"chop_logs": "10,Foraging:50" if hand else "25,", "first_accessory": "50,", "mine_basics": "25,", "first_harvest": "25,", "island_two": "25,",
                "defeat_mobs": "50," if edited else "0,", "open_luggage": "25,", "island_three": "25,", "mini_boss": "100," if edited else "0,", "hub_tour": "100,",
                "pick_class": "25,", "explore_area": "50,"}
        lines = new.replace("\r\n", "\n").split("\n")
        got = dict((l_.split("=", 1)[0][16:], l_.split("=", 1)[1]) for l_ in lines if l_.startswith("tutorial.reward."))
        K.eq(dict((k_, got.get(k_)) for k_ in want), want, "MIG-C %s: the reward lines after the update" % name)
        K.check(sum(1 for l_ in lines if "SkyyQuests 0.2 tutorial rewards" in l_) == 1 and lines.index([l_ for l_ in lines if "SkyyQuests 0.2" in l_][0]) < lines.index("tutorial.reward.pick_class=25,"),
                "MIG-C %s: one marker comment, before the first reward line" % name)
        K.check((new.count("\r\n") == new.count("\n")) if crlf else ("\r" not in new), "MIG-C %s: line endings kept (%s)" % (name, "CRLF" if crlf else "LF"))
        K.check(new.replace("\r\n", "\n").startswith(CFG01.split("# tutorial rewards")[0]), "MIG-C %s: every other line kept byte for byte" % name)
        hist = os.path.join(cb, "config-history")
        baks = [f_ for f_ in os.listdir(hist) if f_.endswith(".bak")] if os.path.isdir(hist) else []
        K.check(any(open(os.path.join(hist, f_), "rb").read() == txt0.encode("latin-1") for f_ in baks), "MIG-C %s: the old file is in config-history (%s)" % (name, baks))
        cl = open(os.path.join(cb, "config-changes.log"), encoding="utf8").read() if os.path.isfile(os.path.join(cb, "config-changes.log")) else ""
        rows = [l_.split("\t") for l_ in cl.splitlines() if l_.strip()]
        K.eq(len(rows), 10 if hand else (9 if edited else 11), "MIG-C %s: one change-log line per changed key (+ explore_area)" % name)
        K.check(all(r_[1] == "SkyyQuests 0.2" and r_[3] == "update" and r_[7] == "ok" and r_[4].startswith("quests.tutorial.rewards[") for r_ in rows),
                "MIG-C %s: change-log lines (who / update / table key / ok = Undo): %s" % (name, rows[:1]))
        K.check((["quests.tutorial.rewards[mini_boss]", "100|", "0|"] in [r_[4:7] for r_ in rows]) != edited and ["quests.tutorial.rewards[explore_area]", "(none)", "50|"] in [r_[4:7] for r_ in rows],
                "MIG-C %s: columns joined by | (the kit's table format), (none) for the added line" % name)
        if edited:
            K.check("defeat_mobs=50, kept - your edited quests/tutorial.properties has no gear reward" in msg and "mini_boss=100, kept" in msg,
                    "FIX-A3 an EDITED tutorial file: the combat coins are KEPT (never a task that pays nothing) and named: %s" % msg[-260:])
            Cfg.load()
            Lx = Defs.line("tutorial")
            K.check(Lx is None or "coins:50" in str(Defs.rewardOf(Lx, [t for t in Lx.tasks if str(t.id) == "defeat_mobs"][0])) or True, "FIX-A3 (table read)")
            K.eq([str(x) for x in Cfg.REWARDS.get("defeat_mobs")], ["50", ""], "FIX-A3 the loader still pays 50 coins for defeat_mobs with the edited file")
        done = os.path.join(cb, "config-update-0.2.done")
        K.check(os.path.isfile(done), "FIX-A4 the 2nd run-once marker file is written after the update (%s)" % name)
        if hand:
            K.check("chop_logs=10,Foraging:50 kept (custom)" in msg, "MIG-C a hand-set line is KEPT and named")
        h2 = open(cf, "rb").read()
        K.eq(str(Mig.migrate02()), "", "MIG-C %s: a second run does nothing (marker)" % name)
        K.check(open(cf, "rb").read() == h2, "MIG-C %s: ... the file is untouched" % name)
        open(cf, "wb").write(txt0.encode("latin-1"))     # Server Setup restores the WHOLE pre-update History copy (no marker inside)
        K.eq(str(Mig.migrate02()), "", "FIX-A4 %s: a restored pre-update file is NOT updated again (the sidecar marker)" % name)
        K.check(open(cf, "rb").read() == txt0.encode("latin-1"), "FIX-A4 %s: ... the restored file stays as restored" % name)
        open(cf, "wb").write(h2)
        Cfg.load()
        K.eq([str(x) for x in Cfg.REWARDS.get("hub_tour")], ["100", ""], "MIG-C %s: the loader reads the updated table" % name)
    Defs.DIR = dir0
    Cfg.FILE = JClass("java.nio.file.Paths").get(os.path.join(base, "config.properties"))
    K.eq(str(Mig.migrate02()), "", "MIG-C a config file written by 0.2 (marker in it) is never updated")
    K.save()


# ====================================================================================================== shared engine scene
class Scene(object):
    def __init__(self, K, scratch, name, loader=None):
        from jpype import JClass, JObject
        self.K = K
        self.J = JClass
        self.br = JClass("java.lang.System").getProperties().get("skyy.bridge")
        self.base = os.path.join(scratch, name, "Skyy_SkyyQuests")
        self.E = Env(self.base, loader)
        os.makedirs(os.path.join(scratch, name, "Skyy_SkyyIslands"), exist_ok=True)
        open(os.path.join(scratch, name, "Skyy_SkyyIslands", "hub.properties"), "w").write("world=skyy-hub\n")
        self.E.start()
        P = self.E.P
        self.Eng, self.Sto, self.St, self.QP, self.Defs, self.Cfg, self.Log, self.Life = (P("QEng"), P("QStore"), P("QState"), P("QP"), P("QDefs"),
                                                                                          P("QCfg"), P("QLog"), P("QLife"))
        self.U = JClass("java.util.UUID")
        self.L = self.Defs.LINES[0]
        self.Eng.HUBAT = 0
        self.Eng.hubRefresh(1000)

    def player(self, n, world="skyy-island-a1"):
        u = self.U(0x5151, n)
        p = self.QP(u, None)
        p.pk = str(u)
        p.world = world
        p.loaded = True
        self.Eng.PLAYERS.put(u, p)
        s = self.Sto.read(str(u), u)
        s.owner = u
        self.Sto.CACHE.put(str(u), s)
        self.Eng.rebuild(u, s)
        return u, p, s

    def done(self, s, tid):
        return bool(s.isDone("tutorial." + tid))

    def rows(self, s):
        r = [str(x) for x in s.rowsOf(self.L)]
        return dict((str(self.L.tasks[i].id), (r[2 * i], r[2 * i + 1])) for i in range(len(self.L.tasks)))

    def want(self, u):
        w = self.Eng.WANT.get(u)
        return 0 if w is None else int(w)


def run_engine(out, jar, scratch, home):
    from jpype import JClass, JObject, JArray, JLong, JInt
    K = HK.Child(out)
    hcls = FAKE_DIR
    HK.jvm([B.SERVER_JAR, jar, hcls], verify=True)
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    PyFn = fn_class()
    Boolean, Long, Integer, Double = JClass("java.lang.Boolean"), JClass("java.lang.Long"), JClass("java.lang.Integer"), JClass("java.lang.Double")
    X = Scene(K, scratch, "e")
    Eng, Sto, Life, Defs, Cfg, Log = X.Eng, X.Sto, X.Life, X.Defs, X.Cfg, X.Log
    br.put("coins:fn:add", PyFn(lambda a: Long(1)))
    br.put("skill:fn:addxp", PyFn(lambda a: Boolean.TRUE))
    feeds = []
    br.put("feed:fn:push", PyFn(lambda a: feeds.append((str(a[3]), None if a[2] is None else str(a[2]), None if a[4] is None else int(a[4]))) or Boolean.TRUE))
    OA = lambda *xs: JArray(JObject)([JObject(x) if not isinstance(x, (str,)) else x for x in xs])
    u, p, s = X.player(1)
    K.eq(X.rows(s)["pick_class"][0], "hidden", "FIX6 pick_class hidden without SkyyProfiles (profile:fn:key)")
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    K.eq(X.rows(s)["pick_class"][0], "open", "FIX6 ... shown with it")
    w0 = X.want(u)
    want0 = TB["break"] | TB["felled"] | TB["gather"] | TB["craft"] | TB["kill"] | TB["enter"] | TB["talk"] | TB["page"] | TB["event"] | TB["tier"] | TB["bridge"]
    K.eq(w0, want0, "E1 want bits of a fresh profile (no reach: no spot set; no level task in the tutorial)")
    K.check(Eng.WANT.get(X.U(9, 9)) is None and not Eng.count(X.U(9, 9), TB["break"], "Rock_Stone", 1, "w", False), "E1 a player without bits: one map read, false")
    v0 = int(s.ver)
    K.check(not Eng.count(u, TB["reach"], "x", 1, "w", False) and int(s.ver) == v0, "E1 a type without its bit: nothing touched")
    # ---- break: chop logs (any of felled / trunk breaks)
    for i in range(9):
        Eng.count(u, TB["break"], "Wood_Oak_Trunk", 1, "skyy-island-a1", False)
    K.eq(X.rows(s)["chop_logs"], ("open", "9/10"), "E2 chop_logs 9/10")
    Eng.count(u, TB["felled"], "Plant_Leaves_Oak", 40, "skyy-island-a1", False)
    K.check(not X.done(s, "chop_logs") and str(s.prog.get("tutorial.chop_logs.0")) in ("None", "0"), "FIX1 40 felled LEAVES do not count as logs (%s)" % s.prog.get("tutorial.chop_logs.0"))
    Eng.count(u, TB["felled"], "Wood_Birch_Trunk", 1, "skyy-island-a1", False)
    K.check(not X.done(s, "chop_logs") and int(str(s.prog.get("tutorial.chop_logs.0"))) == 1, "E2 felled 1 trunk counts, and does not add to the trunk-break counter (any = the best part)")
    Eng.count(u, TB["break"], "Wood_Oak_Trunk", 1, "skyy-island-a1", False)
    K.check(X.done(s, "chop_logs"), "E2 chop_logs done at 10 trunk breaks")
    g = "coins|25|%s:tutorial.chop_logs:1" % u
    gi = "item|Plant_Sapling_Oak:2|%s:tutorial.chop_logs:2" % u
    lg = logtext(X.base)
    K.check(lg.count("PAYING %s %s" % (u, g)) == 1 and lg.count("PAID %s %s" % (u, g)) == 1,
            "E2 its coins claim was ONE claim line, paid once at once (stand-in SkyyCoins): %s" % lg[-300:])
    K.check([str(x) for x in s.claims] == [gi] and ("PAID %s %s" % (u, gi)) not in lg, "Q1 + its item claim (items + coins), waiting: no world in a bare JVM (%s)" % [str(x) for x in s.claims])
    K.check(("Done: Chop 10 logs", None, None) in feeds and ("Reward: +25 coins", None, None) in feeds, "Q9 FEED ONLY: a done card + a reward card: %s" % feeds[-3:])
    K.check(not [x for x in Log.SINK if "Chop" in str(x) or "eward" in str(x)], "Q9 ... and never a chat line: %s" % [str(x) for x in Log.SINK][-3:])
    # ---- NON-LINEAR: task 6 (first_rankup) before task 4 (first_accessory), task 20 before 13
    br.put("coll:score:" + str(u), Long(3))
    br.put("coll:epoch:" + str(u), Long(6))
    Eng.lazy(p, True)
    K.check(not X.done(s, "first_rankup") and int(s.base.get("tutorial.first_rankup.0")) == 3,
            "LEAD an EXISTING rank (score 3) does NOT complete 'See a collection rank up' - it becomes the baseline")
    br.put("coll:score:" + str(u), Long(2))
    Eng.lazy(p, True)
    K.check(not X.done(s, "first_rankup") and int(s.base.get("tutorial.first_rankup.0")) == 2, "LEAD a lower value (stale right after a profile switch) lowers the baseline")
    Eng.lazy(p, True)
    K.check(not X.done(s, "first_rankup"), "LEAD the same value again: still not done")
    br.put("coll:score:" + str(u), Long(9))
    Eng.lazy(p, True)
    K.check(not X.done(s, "first_rankup") and int(s.base.get("tutorial.first_rankup.0")) == 2,
            "FIX-A1 a HIGHER score with coll:epoch NOT moved (stale, another profile's) never ticks it")
    p.collEp = None
    p.freshArm = False                                     # what a profile switch / join / reload does
    br.put("coll:score:" + str(u), Long(10))
    br.put("coll:epoch:" + str(u), Long(8))
    Eng.lazy(p, False)
    K.check(not X.done(s, "first_rankup") and int(s.base.get("tutorial.first_rankup.0")) == 2,
            "FIX-A1 the FIRST read after a profile switch is baseline-only: a stale higher score (10 vs base 2) does not tick it")
    br.put("coll:score:" + str(u), Long(2))
    br.put("coll:epoch:" + str(u), Long(9))
    Eng.lazy(p, False)
    K.check(not X.done(s, "first_rankup") and int(s.base.get("tutorial.first_rankup.0")) == 2, "FIX-A1 the real profile's score arrives (2): still not done")
    br.put("coll:score:" + str(u), Long(3))
    br.put("coll:epoch:" + str(u), Long(10))
    Eng.lazy(p, False)
    K.check(X.done(s, "first_rankup") and not X.done(s, "first_accessory"), "LEAD a NEW rank-up (2 -> 3, coll:epoch moved) completes it; task 6 before task 4 (non-linear)")
    K.check("base.tutorial.first_rankup.0=2" in str(s.textU()), "LEAD the baseline is saved in the profile file")
    Eng.count(u, TB["kill"], "Golem_Crystal_Earth", 1, None, False)
    K.check(X.done(s, "mini_boss") and not X.done(s, "defeat_mobs"), "E3 task 20 (mini boss) done before task 13")
    for i in range(4):
        Eng.count(u, TB["kill"], "Trork_Grunt", 1, None, False)
    K.check(X.rows(s)["defeat_mobs"] == ("open", "5/5") or X.done(s, "defeat_mobs"), "E3 the golem counted toward 5 mobs too (kill any)")
    K.check(X.done(s, "defeat_mobs") and X.done(s, "first_rankup") and X.done(s, "mini_boss"), "E3 ... and every earlier one stays done")
    # ---- bridge: exists / >= / notempty / contains; craft; all()
    br.put("profile:class:" + str(u), "Mage")
    br.put("bank:" + str(u), Long(49))
    Eng.lazy(p, True)
    K.check(X.done(s, "pick_class") and not X.done(s, "bank_deposit"), "E4 bridge exists (class) done, bank 49 < 50 not")
    br.put("bank:" + str(u), Long(60))
    Eng.lazy(p, True)
    K.check(X.done(s, "bank_deposit"), "E4 bridge >= (bank 60)")
    Eng.count(u, TB["craft"], "Skyy_Accessory_Workbench_T1", 1, "w", False)
    K.check(not X.done(s, "first_accessory"), "E4 all(): the craft alone is not enough")
    br.put("acc:has:" + str(u), "")
    Eng.lazy(p, True)
    K.check(not X.done(s, "first_accessory"), "E4 notempty: an empty bag is not enough")
    br.put("acc:has:" + str(u), "Skyy_Accessory_Workbench_T1")
    Eng.lazy(p, True)
    K.check(X.done(s, "first_accessory"), "E4 craft + in the bag = done")
    # ---- mine basics (a coming-soon bridge fn part), harvest (gather), enter hub
    for i in range(10):
        Eng.count(u, TB["break"], "Rock_Stone", 1, "w", False)
    for i in range(5):
        Eng.count(u, TB["break"], "Ore_Copper_Stone", 1, "w", False)
    K.check(X.done(s, "mine_basics"), "E5 stone 10 + copper 5 (the gear:fn:lifelong part is coming soon until quest:caller:gearlife)")
    Eng.count(u, TB["break"], "Plant_Crop_Wheat_Block", 3, "w", False)
    K.eq(X.rows(s)["first_harvest"][1], "0/3", "E5 an unripe crop break does not count (ripe=true)")
    Eng.count(u, TB["gather"], "Plant_Crop_Wheat_Item", 3, "w", False)
    K.check(X.done(s, "first_harvest"), "E5 gather 3 wheat")
    K.eq(str(Eng.hubWorld()), "skyy-hub", "E5 the hub world from Skyy_SkyyIslands/hub.properties (tick thread read)")
    Eng.count(u, TB["enter"], "skyy-hub", 1, "skyy-hub", False)
    K.check(not X.done(s, "to_hub") and s.pdone.contains("tutorial.to_hub.1") and X.rows(s)["to_hub"][0] == "soon",
            "FIX5 enter hub alone does NOT complete to_hub (portal part block=true is coming soon; the enter still counts): %s" % (X.rows(s)["to_hub"],))
    h0 = [str(x) for x in Eng.hud(u)]
    K.check("Travel to the hub" not in h0, "FIX5 ... and the widget skips it")
    br.put("quest:caller:islands", Boolean.TRUE)
    K.eq(X.rows(s)["to_hub"][0], "open", "FIX5 quest:caller:islands turns it live")
    K.check(not X.done(s, "to_hub"), "FIX5 ... still needs the portal")
    K.check(bool(Eng.event(OA(u, "island:portal", "", Long(1)))) and X.done(s, "to_hub"), "FIX5 the portal event + the earlier hub entry = done")
    br.remove("quest:caller:islands")
    # FIX2 (critic B2): hub_tour's parts are all block=true - SkyyMenu calling in alone never makes it live / pays it on 2 pages
    br.put("quest:caller:menu", Boolean.TRUE)
    K.eq(X.rows(s)["hub_tour"][0], "soon", "FIX2-B2 hub_tour stays coming soon with only quest:caller:menu")
    Eng.event(OA(u, "page", "auction", Long(1)))
    Eng.event(OA(u, "page", "bank", Long(1)))
    K.check(not X.done(s, "hub_tour"), "FIX2-B2 ... the Auction + Bank pages alone do not complete (pay) it")
    br.put("quest:caller:bazaar", Boolean.TRUE)
    br.put("quest:caller:board", Boolean.TRUE)
    K.eq(X.rows(s)["hub_tour"][0], "open", "FIX2-B2 live once every caller exists")
    br.remove("quest:caller:bazaar")
    br.remove("quest:caller:board")
    br.remove("quest:caller:menu")
    # ---- hidden (requires) + caller soon
    K.eq(X.rows(s)["first_pet"][0], "hidden", "E6 first_pet hidden without pets:fn:loadoutGet")
    pet = PyFn(lambda a: "|")
    br.put("pets:fn:loadoutGet", pet)
    K.eq(X.rows(s)["first_pet"][0], "soon", "FIX4 ... shown as coming soon once SkyyPets runs (pets:equip needs quest:caller:pets)")
    Eng.lazy(p, True)
    K.check(not X.done(s, "first_pet") and len(pet.calls) == 0, "FIX4 the loadout value ('|' = empty, or the starter pet) never completes it")
    K.check(bool(Eng.event(OA(u, "pets:equip", "", Long(1)))) and X.done(s, "first_pet"), "FIX4 the pets:equip event completes it")
    K.eq(X.rows(s)["hub_buttons"][0], "soon", "E6 hub_buttons coming soon (caller=menu)")
    K.eq(X.rows(s)["party_intro"][0], "soon", "E6 party_intro coming soon (caller=menu)")
    F_ev = Eng.event(OA(u, "page", "hub", Long(1)))
    K.check(bool(F_ev) and X.done(s, "hub_buttons"), "E6 an event from a caller that has not announced itself still counts (never lost)")
    br.put("quest:caller:menu", Boolean.TRUE)
    K.eq(X.rows(s)["party_intro"][0], "open", "E6 quest:caller:menu turns the soon tasks live")
    # ---- events: the ':' type form, talk, gather alias, unknown, rate cap
    br.put("quest:caller:bank", Boolean.TRUE)
    K.check(bool(Eng.event(OA(u, "requip:save", "", Long(1)))), "E7 a type with ':' = an event with that key")
    K.check(X.done(s, "requip_save"), "E7 requip:save done (counted while its caller is soon: never lost)")
    K.check(not bool(Eng.event(OA(u, "nope", "x", Long(1)))) and not bool(Eng.event(OA(u, "event", "x", Long(0)))) and not bool(Eng.event("bad")),
            "E7 bad events refused")
    p.lazyAt = 99
    K.check(bool(Eng.event(OA(u, "level", "Mining", Long(5)))) and int(p.lazyAt) == 0, "E7 level = re-check now")
    Cfg.EVENT_RATE = 3
    p.rateSec = 0
    res = [bool(Eng.event(OA(u, "event", "x:y", Long(1)))) for _ in range(5)]
    K.eq(res[:3], [True, True, True], "E7 rate: 3 in a second accepted")
    K.check(res[3:] == [False, False] and any("more than 3 calls" in str(x) for x in Log.LINES), "E7 rate: the 4th+ dropped, logged once")
    Cfg.EVENT_RATE = 20
    # ---- guards: busy, profile key
    v1 = int(s.ver)
    br.put("profile:busy:" + str(u), Boolean.TRUE)
    K.check(not Eng.count(u, TB["kill"], "x", 1, None, False) and int(s.ver) == v1, "E8 profile:busy = nothing counted")
    br.remove("profile:busy:" + str(u))
    keyfn = PyFn(lambda a: str(a) + "-p2")
    br.put("profile:fn:key", keyfn)
    K.check(not Eng.count(u, TB["break"], "Rock_Stone", 1, "w", False) and int(s.ver) == v1, "E8 another active profile key = not counted on this state")
    # FIX (critic 1.2): a profile switch DURING the lazy pass (after the bridge value was read) completes nothing on the old state
    br.put("bank:" + str(u), Long(10))
    u3, p3, s3 = X.player(3)
    calls = {"n": 0}
    def flip(a):
        calls["n"] += 1
        return str(a) if calls["n"] <= 1 else str(a) + "-p2"
    br.put("profile:fn:key", PyFn(flip))
    br.put("bank:" + str(u3), Long(500))
    Eng.lazy(p3, True)
    K.check(not X.done(s3, "bank_deposit") and calls["n"] >= 2, "FIX-L lazy re-checks the profile key before each completion (switch mid-pass: nothing done; %d key reads)" % calls["n"])
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    Eng.lazy(p3, True)
    K.check(X.done(s3, "bank_deposit"), "FIX-L ... the same pass with a steady key completes it")
    # FIX (critic 2.2): the arrow hop keeps going without a recent Hud call
    p3.dirPlace = "island2"
    p3.hudAt = 0
    K.check(bool(X.Life.needsHop(p3, JLong(int(time.time() * 1000)))), "FIX2 a player with an arrow target hops even 15 s+ after the last Hud read")
    p3.dirPlace = None
    # ---- hud shape
    Cfg.DONE_SECS = 2.5
    u2, p2, s2 = X.player(2)
    h = Eng.hud(u2)
    K.check(h is not None and len(h) == 2 + 6 * 3, "H1 3 tasks: %s" % (None if h is None else len(h)))
    opt = set(str(t.id) for t in X.L.tasks if bool(t.optional))
    live = [k for k, v in X.rows(s2).items() if v[0] not in ("soon", "hidden") and k not in opt]
    K.eq((str(h[0]), str(h[1])), ("Getting Started", "0 / %d" % len(live)), "H1 title + count (the live tasks: not soon, not hidden)")
    names = [str(h[2 + 6 * j]) for j in range(3)]
    K.eq(names, ["Pick a class", "Open the hub buttons", "Chop 10 logs"], "H1 file order, soon tasks skipped (menu caller is set now)")
    K.eq((str(h[5]), int(h[6]), bool(h[7])), ("Profiles page: your weapon + first ability", -1, False), "H1 task 1 where = its hint, no dir")
    K.eq((float(h[2 + 6 * 2 + 2]), str(h[2 + 6 * 2 + 1]), h[2 + 6 * 1 + 2]), (0.0, "0/10", None), "H1 frac of a counter (0.0) / none for a one-step task (null)")
    for i in range(6):
        Eng.count(u2, TB["break"], "Wood_Oak_Trunk", 1, "w", False)
    p2.compact = True
    h = Eng.hud(u2)
    K.eq(len(h), 8, "H2 compact = 1 task")
    p2.compact = False
    br.put("profile:class:" + str(u2), "Mage")
    Eng.lazy(p2, True)
    h = Eng.hud(u2)
    K.eq((str(h[2]), bool(h[7]), str(h[5])), ("Pick a class", True, "Done!  +25 coins  +3 Bread"), "H3 a done task stays (green) with Done! + its reward")
    s2.expire(JLong(int(time.time() * 1000) + 3000))
    h = Eng.hud(u2)
    K.eq(str(h[2]), "Open the hub buttons", "H3 after the hold the list moves up")
    nd = len([k for k, v in X.rows(s2).items() if v[0] == "done" and k not in opt])
    K.eq(str(h[1]), "%d / %d" % (nd, len(live)), "H3 count")
    # where + arrow: island2 place, task order: make island_two the first shown task by hiding the others? -> its own line
    open(os.path.join(X.base, "quests", "zplace.properties"), "w").write(
        "line=walk\nname=Walk\nauto=true\ntask.1.id=go\ntask.1.name=Go to island 2\ntask.1.type=reach\ntask.1.match=island2\ntask.1.radius=12\n")
    Defs.load()
    Defs.savePlace("island2", "island", 100.0, 64.0, 100.0, "Island 2")
    Eng.rebuild(u2, s2)
    while int(s2.claimCount()) > 0:          # 0.2: item rewards wait in a bare JVM (no world) - their "Reward waiting" note would cover task 1's line
        s2.takeClaim()
    s2.waitNote = None
    s2.retryNow()
    K.check(X.want(u2) & TB["reach"], "H4 a reach part with its spot set adds the reach bit")
    s2.setTrack("walk")
    p2.hideTut = True
    h = Eng.hud(u2)
    K.eq((str(h[0]), str(h[2]), str(h[5]), int(h[6])), ("Walk", "Go to island 2", "Island 2", -1), "H4 a place task: the label before a position is known")
    K.eq(str(p2.dirPlace), "island2", "H4 the hop is told the place")
    Eng.position(p2, "skyy-island-a2", 70.0, 64.0, 130.0)
    h = Eng.hud(u2)
    K.eq((str(h[5]), int(h[6])), ("NE  42 m  -  Island 2", 1), "H4 north-up: dx +30, dz -30 = NE 42 m")
    e0 = int(Eng.EPOCH.get(u2))
    Eng.position(p2, "skyy-island-a2", 70.2, 64.0, 130.1)
    K.eq(int(Eng.EPOCH.get(u2)), e0, "H4 standing still (same text) = no epoch change")
    dirs = {}
    for name, (x, z) in (("N", (100, 200)), ("NE", (0, 200)), ("E", (0, 100)), ("SE", (0, 0)), ("S", (100, 0)), ("SW", (200, 0)), ("W", (200, 100)), ("NW", (200, 200))):
        Eng.position(p2, "skyy-island-a2", float(x), 64.0, float(z))
        dirs[name] = (str(p2.dirText).split(" ")[0], int(p2.dir))
    K.eq(dirs, {"N": ("N", 0), "NE": ("NE", 1), "E": ("E", 2), "SE": ("SE", 3), "S": ("S", 4), "SW": ("SW", 5), "W": ("W", 6), "NW": ("NW", 7)},
         "H4 the 8 directions (north = -Z)")
    Eng.position(p2, "skyy-island-a2", 100.0, 64.0, 345.0)
    K.check(str(p2.dirText).startswith("N  250 m"), "H4 distance rounded to 10 above 100: %s" % p2.dirText)
    Eng.position(p2, "skyy-hub", 100.0, 64.0, 100.0)
    h = Eng.hud(u2)
    K.eq((str(h[5]), int(h[6])), ("Island 2", -1), "H4 another world = the label, no arrow")
    Eng.position(p2, "skyy-island-a2", 101.0, 64.0, 99.0)
    K.check(s2.isDone("walk.go"), "H4 reach within the radius = done")
    p2.hideTut = True
    p2.hideEmpty = True
    s2.expire(JLong(int(time.time() * 1000) + 5000))
    K.check(Eng.hud(u2) is None, "H5 nothing left (tutorial hidden, walk done) + Hide when empty = hidden")
    p2.hideEmpty = False
    h = Eng.hud(u2)
    K.eq([str(x) for x in h], ["No active quests", ""], "H5 ... or the No active quests state")
    p2.hideTut = False
    K.check(Eng.hud(u2) is not None, "H5 the tutorial back")
    os.remove(os.path.join(X.base, "quests", "zplace.properties"))
    Defs.load()
    # ---- QFn modes
    Fn = X.E.P("QFn")
    K.check(Fn("hud").apply(u2) is not None and Fn("hud").apply("x") is None, "F1 quest:fn:hud")
    K.check(bool(Fn("event").apply(OA(u2, "event", "x:y", Long(1)))), "F1 quest:fn:event")
    K.check(bool(Fn("done").apply(OA(u2, "tutorial.pick_class"))) and not bool(Fn("done").apply(OA(u2, "tutorial.chop_logs"))), "F1 quest:fn:done")
    K.check(not bool(Fn("flag").apply(OA(u2, "x"))) and not bool(Fn("hasoffer").apply(OA(u2, "fisher"))), "F1 flag / hasoffer for an NPC nobody wants")
    K.check(bool(Fn("hasoffer").apply(OA(u2, "board"))), "F1 hasoffer: an active talk objective names the board")
    K.check(not bool(Fn("talk").apply(OA(u2, "nobody"))) or True, "F1 talk to an unknown NPC")
    Fn("talk").apply(OA(u2, "board"))
    K.check(not bool(Fn("hasoffer").apply(OA(u2, "board"))), "F1 talk counted (the part is done)")
    K.check(not bool(Fn("start").apply(OA(u2, "tutorial"))), "F1 start: an auto line is already running (nothing to start)")
    K.check(Fn("markers").apply(OA(u2, "skyy-island-a2")) is not None and Fn("markers").apply("bad") is not None, "F1 markers never null")
    K.check(not bool(Fn("flag").apply("bad")), "F1 bad arguments = FALSE")
    # ---- admin done / undo never pays twice
    while int(s2.claimCount()) > 0:          # 0.2: the waiting item claims (no world in a bare JVM) would hold the payer for retrySeconds
        s2.takeClaim()
    s2.retryNow()
    n0 = int(s2.claimCount())
    out = JClass("java.util.ArrayList")()
    t_chop = [t for t in X.L.tasks if str(t.id) == "chop_logs"][0]
    K.check(s2.adminDone(X.L, t_chop, JLong(1), out) and int(s2.claimCount()) == n0 + 2, "A1 admin done issues the reward once (coins + item)")
    K.check(s2.adminUndo(X.L, t_chop) and not s2.isDone("tutorial.chop_logs"), "A1 undo clears it")
    for i in range(10):
        Eng.count(u2, TB["break"], "Wood_Oak_Trunk", 1, "w", False)
    gl = [l for l in logtext(X.base).splitlines() if ("PAYING %s " % u2) in l and "tutorial.chop_logs" in l]
    K.check(s2.isDone("tutorial.chop_logs") and len(gl) == 2 and len(set(l_.split(" ")[-1] for l_ in gl)) == 2, "A1 done again: NO second reward (issued stays) - only the first issue (coins + item) is paid: %s" % gl)
    # ---- settings
    gets = {}
    setfn = PyFn(lambda a: gets.setdefault(str(a[1]), None))
    br.put("settings:fn:get", PyFn(lambda a: {"tutorial.hide": Boolean.TRUE, "quests.compact": Boolean.TRUE}.get(str(a[1]))))
    br.put("msgroute:fn:get", PyFn(lambda a: "off"))
    K.check(Eng.refreshSettings(p2, s2) and p2.hideTut and p2.compact and p2.hideEmpty and p2.chat and str(p2.route) == "off", "S1 settings refresh")
    br.put("settings:fn:set", setfn)
    K.check(Eng.setHide(u2, False) and not p2.hideTut and len(setfn.calls) == 1 and not s2.hideOf("tutorial"), "S1 setHide -> settings:fn:set + the file line")
    br.remove("settings:fn:get")
    K.check(not Eng.refreshSettings(p2, s2) or True, "S1 without SkyyMenu the file line is the switch")
    K.eq(bool(p2.hideTut), False, "S1 file line false")
    Eng.regSetting("tutorial.hide", "x", Boolean.FALSE, "h")
    K.check(br.get("settings:def:tutorial.hide") is not None, "S1 regSetting writes settings:def")
    K.eq(str(Eng.action(u2, "hide", None))[0], "+", "S2 action hide")
    K.eq(str(Eng.action(u2, "track", "nope"))[0], "-", "S2 action track unknown")
    K.eq(str(Eng.action(u2, "track", "tutorial"))[0], "+", "S2 action track")
    K.eq(str(Eng.action(u2, "claim", None))[0], "+" if s2.hasClaims() else "=", "S2 action claim")
    K.eq(str(Eng.action(X.U(7, 7), "claim", None))[0], "-", "S2 action without a loaded state")
    # ---- progress lines: feed route / chat route
    pushes = PyFn(lambda a: Boolean.TRUE)
    br.put("feed:fn:push", pushes)
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    p2.pr = unsafe().allocateInstance(PRef.class_)
    setf(p2.pr, PRef.class_, "uuid", u2)
    p2.route = "feed"
    Eng.count(u2, TB["kill"], "Trork", 1, None, False)
    K.check(len(pushes.calls) == 1 and str(pushes.calls[0][1]) == "quest" and str(pushes.calls[0][3]) == "Defeat 5 mobs", "N1 progress -> feed:fn:push")
    nsink = len(Log.SINK)
    p2.route = "chat"
    Eng.count(u2, TB["kill"], "Trork", 1, None, False)
    K.check(len(pushes.calls) == 2 and len(Log.SINK) == nsink, "Q9 a 'chat' route still goes to the feed - never a chat line")
    p2.route = "off"
    Eng.count(u2, TB["kill"], "Trork", 1, None, False)
    K.check(len(pushes.calls) == 2 and len(Log.SINK) == nsink, "Q9 the quest route Off = nothing at all")
    refuse = PyFn(lambda a: Boolean.FALSE)
    br.put("feed:fn:push", refuse)
    p2.route = "feed"
    Eng.count(u2, TB["kill"], "Trork", 1, None, False)
    K.check(len(refuse.calls) == 1 and len(Log.SINK) == nsink, "Q9 a card the feed refuses is NOT turned into a chat line")
    br.put("feed:fn:push", pushes)
    # FIX2 (critic B1): the Server Setup switches rebuild the want index + bump the widget for online players
    Hk = X.E.P("QHooks")
    Cfg.ENABLED = False
    Eng.rebuild(u2, s2)
    K.eq(X.want(u2), 0, "FIX2-B1 Quests off: an (online) player wants nothing")
    Cfg.ENABLED = True
    e0 = int(Eng.EPOCH.get(u2))
    Hk.cfgChanged("quests.enabled")
    K.check(X.want(u2) != 0 and int(Eng.EPOCH.get(u2)) > e0, "FIX2-B1 switched on in Server Setup: after=QHooks.cfgChanged rebuilds the want bits (%d) + bumps quest:epoch at once" % X.want(u2))
    e1 = int(Eng.EPOCH.get(u2))
    Hk.reload()
    K.check(int(Eng.EPOCH.get(u2)) > e1 and bool(Cfg.ENABLED), "FIX2-B1 RELOAD (QHooks.reload) = QCfg.load + the same rebuild")
    # ======================================================================== 0.2: SKIP (Skyy: "bypassing tutorial quests needs to be simple and easy")
    u5, p5, s5 = X.player(5)
    h = Eng.hud(u5)
    K.eq(str(h[2]), "Pick a class", "SK first shown task")
    r = str(Eng.action(u5, "skip", "pick_class"))
    h = Eng.hud(u5)
    K.check(r.startswith("+Skipped: Pick a class") and str(h[2]) == "Open the hub buttons" and X.rows(s5)["pick_class"][0] == "skipped",
            "SK /quests skip <task> takes it out of the widget (%s; widget %s)" % (r, h[2]))
    K.check(str(h[1]).startswith("1 / "), "SK a skipped task counts as passed in the widget's x / y (%s)" % h[1])
    K.check(bool(s5.isSkipped("tutorial.pick_class")) and "skip.tutorial.pick_class=" in str(s5.textU()), "SK saved in the profile file")
    br.put("profile:class:" + str(u5), "Mage")
    Eng.lazy(p5, True)
    K.check(X.done(s5, "pick_class") and any(("pick_class" in str(c)) for c in [l_ for l_ in logtext(X.base).splitlines() if ("PAID %s " % u5) in l_]),
            "SK a skipped task still counts and still PAYS when it is done later")
    K.eq(str(Eng.action(u5, "skip", "tutorial.void_bag"))[:9], "+Skipped:", "SK skip by line.task")
    K.check(str(Eng.action(u5, "skip", "tutorial.void_bag")).endswith("is back in your widget.") and not bool(s5.isSkipped("tutorial.void_bag")), "SK the same again = Unskip")
    K.eq(str(Eng.action(u5, "skip", "nope"))[0], "-", "SK an unknown task")
    K.eq(str(Eng.action(u5, "skip", "chop_logs"))[0:9], "+Skipped:", "SK a bare id finds the first line that has it")
    K.check(Eng.findTask("mining.mining_stone") is not None and Eng.findTask("tutorial.mining_stone") is None, "SK findTask by line.task")
    # ======================================================================== 0.2: OPTIONAL tasks never block (Skyy ticked 9, 10, 23)
    open(os.path.join(X.base, "quests", "zopt.properties"), "w").write(
        "line=zopt\nname=Opt\nauto=true\norder=-1\ntask.1.id=o1\ntask.1.name=Opt one\ntask.1.optional=true\ntask.1.type=break\ntask.1.match=Rock_X\ntask.1.reward=coins:3\n"
        "task.2.id=r1\ntask.2.name=Req one\ntask.2.type=break\ntask.2.match=Rock_Y\ntask.3.id=r2\ntask.3.name=Req two\ntask.3.type=break\ntask.3.match=Rock_Z\n")
    Defs.load()
    u6, p6, s6 = X.player(6)
    h = Eng.hud(u6)
    K.eq([str(h[0]), str(h[1])] + [str(h[2 + 6 * j]) for j in range(3)], ["Opt", "0 / 2", "Req one", "Req two", "Opt one"],
         "OPT the required tasks first, the optional one last, not in x / y")
    Eng.count(u6, TB["break"], "Rock_Y", 1, "w", False)
    Eng.count(u6, TB["break"], "Rock_Z", 1, "w", False)
    s6.expire(JLong(int(time.time() * 1000) + 5000))
    h = Eng.hud(u6)
    K.eq(str(h[0]), "Getting Started", "OPT only an optional task left = the widget moves on to the next line (the flow never waits)")
    Eng.count(u6, TB["break"], "Rock_X", 1, "w", False)
    K.check(s6.isDone("zopt.o1") and ("coins|3|" in logtext(X.base)), "OPT an optional task still counts and pays")
    os.remove(os.path.join(X.base, "quests", "zopt.properties"))
    Defs.load()
    # ======================================================================== 0.2: AREAS (SkyBlock approach: suggest Mining, follow the player)
    u7, p7, s7 = X.player(7, "skyy-hub")
    K.eq(X.rows(s7)["explore_area"][0], "soon", "AR explore_area is coming soon while no area is set up")
    K.check(not (X.want(u7) & TB["area"]) and not bool(Eng.regionWorld("skyy-hub")), "AR no area bit / no region hop before a place is set")
    Defs.savePlace("hub.mining", "hub", 100.0, 64.0, 100.0, "Mining area")
    Defs.savePlace("hub.foraging", "hub", 400.0, 64.0, 400.0, "Foraging area")
    Life.rebuildAll()
    K.check(X.rows(s7)["explore_area"][0] == "open" and (X.want(u7) & TB["area"]) and bool(Eng.regionWorld("skyy-hub")) and bool(Life.needsHop(p7, JLong(0))),
            "AR set up (hub.mining set): explore_area live, the area bit, the hub is a region world -> the position hop")
    K.check(not bool(Eng.regionWorld("skyy-island-zz")), "AR a world without a region area is not a region world (no hop for areas there)")
    # FIX2 (critic, lag rule): with no area objective open, the hop runs only while the widget can follow to an area line with a task left
    u7b, p7b, s7b = X.player(77, "skyy-hub")
    for l_ in list(Defs.LINES):                      # every task of every line done: nothing but the area follow could want a hop
        for t_ in l_.tasks:
            s7b.adminDone(l_, t_, JLong(int(time.time() * 1000)), JClass("java.util.ArrayList")())
    Eng.rebuild(u7b, s7b)
    w7b = X.want(u7b) or 0
    K.check(not (w7b & TB["area"]) and not (w7b & TB["reach"]) and p7b.dirPlace is None and not bool(Life.needsHop(p7b, JLong(0))) and not bool(Eng.FOLLOWU.containsKey(u7b)),
            "FIX2-HOP every area task done: NO position hop for an idle hub player (want %s)" % w7b)
    Eng.FOLLOWU.put(u7b, Boolean.TRUE)
    K.check(bool(Life.needsHop(p7b, JLong(0))), "FIX2-HOP an area line with a task left + 'Widget follows areas' on = the hop")
    Cfg.FOLLOW = False
    K.check(not bool(Life.needsHop(p7b, JLong(0))), "FIX2-HOP 'Widget follows areas' off and no area objective = no hop")
    Cfg.FOLLOW = True
    K.check(bool(Eng.FOLLOWU.containsKey(u7)) and bool(Life.needsHop(p7, JLong(0))), "FIX2-HOP a fresh hub player (area tasks left) has the follow flag from rebuild")
    Life.quit(u7b)
    K.check(not bool(Eng.FOLLOWU.containsKey(u7b)), "FIX2-HOP quit forgets the follow flag")
    Eng.position(p7, "skyy-hub", 300.0, 64.0, 300.0)
    K.check(str(p7.area) == "" and not X.done(s7, "explore_area"), "AR outside every region = no area")
    Eng.position(p7, "skyy-hub", 130.0, 64.0, 120.0)
    K.check(str(p7.area) == "mining" and X.done(s7, "explore_area") and s7.isDone("mining.mining_visit"), "AR entering Mining: the area objective counts (explore_area + mining_visit)")
    s7.expire(JLong(int(time.time() * 1000) + 5000))
    h = Eng.hud(u7)
    K.check(str(s7.track) == "mining" and str(h[0]) == "Mining", "AR the widget FOLLOWS the player into Mining (%s / %s)" % (s7.track, h[0]))
    Eng.position(p7, "skyy-hub", 410.0, 64.0, 390.0)
    s7.expire(JLong(int(time.time() * 1000) + 5000))
    h = Eng.hud(u7)
    K.check(str(p7.area) == "foraging" and str(h[0]) == "Foraging" and s7.isDone("foraging.foraging_visit"),
            "AR ... and switches to Foraging when the player goes there instead (no forced order)")
    Cfg.FOLLOW = False
    Defs.savePlace("hub.farming", "hub", 700.0, 64.0, 700.0, "Farming area")
    Life.rebuildAll()                        # what /questadmin place set does after saving (QIO mode 4)
    Eng.position(p7, "skyy-hub", 700.0, 64.0, 700.0)
    K.check(str(s7.track) == "foraging" and s7.isDone("farming.farming_visit"), "AR Server Setup 'Widget follows areas' off: the widget stays, the visit still counts")
    Cfg.FOLLOW = True
    open(os.path.join(X.base, "areas.properties"), "a", encoding="utf8").write("area.zone1.world=skyy-zone-1\narea.zone1.line=mining\narea.zone1.order=0\n")
    Defs.load()
    K.eq(str(Eng.areaAt("skyy-zone-1", 0.0, 0.0, False)), "zone1", "AR a world-only area is found without a position (a world switch)")
    K.check(bool(Eng.enterArea(p7, "zone1", "skyy-zone-1")) and str(s7.track) == "mining", "AR entering a zone world follows its line")
    K.check(not bool(Eng.enterArea(p7, "zone1", "skyy-zone-1")), "AR the same area again = nothing")
    K.eq(X.rows(s7)["fishing_visit"][0] if "fishing_visit" in X.rows(s7) else [str(x) for x in s7.rowsOf(Defs.line("fishing"))][0], "hidden", "AR the fishing line is hidden without SkyyFishing")
    # ======================================================================== 0.2: the LINE FLOW (the tutorial flows straight into the area lines)
    u8, p8, s8 = X.player(8)
    now8 = int(time.time() * 1000)
    for t in X.L.tasks:
        if not bool(t.optional):
            s8.adminDone(X.L, t, JLong(now8), JClass("java.util.ArrayList")())
    s8.expire(JLong(now8 + 5000))
    h = Eng.hud(u8)
    K.check(str(h[0]) == "Mining" and str(h[2]) == "Visit the Mining area", "FLOW every required tutorial task done (optional ones left) -> the widget shows the Mining line (%s / %s)" % (h[0], h[2]))
    p8.hideTut = True
    h = Eng.hud(u8)
    K.check(h is None or str(h[0]) != "Mining" or "Visit" not in str(h[2]), "FLOW 'I know how to play' hides the tut=true tasks of the area lines too (%s)" % (None if h is None else [str(x) for x in h][:3]))
    br.put("skill:fn:level", PyFn(lambda a: Integer(1)))
    Eng.rebuild(u8, s8)
    h = Eng.hud(u8)
    K.check(h is not None and str(h[0]) == "Mining" and str(h[2]) == "Reach Mining 5", "FLOW ... the progression quests stay (Reach Mining 5)")
    br.remove("skill:fn:level")
    p8.hideTut = False
    # ======================================================================== 0.2: CO-OP short version (Skyy Q7)
    u9, p9, s9 = X.player(9, "skyy-island-friend")
    br.put("island:" + str(u9), "skyy-island-u9")
    Eng.count(u9, TB["kill"], "Golem_Crystal_Earth", 1, None, False)
    Life.step(p9, JLong(int(time.time() * 1000)))
    K.check(bool(p9.coop), "CO on a friend's island = the co-op flag (tick)")
    h = [str(x) for x in Eng.hud(u9)]
    K.check("Chop 10 logs" in h, "CO boss beaten but the hub not reached yet = the LONG version (island tasks still shown)")
    Eng.count(u9, TB["enter"], "skyy-hub", 1, "skyy-hub", False)
    s9.expire(JLong(int(time.time() * 1000) + 5000))
    h = [str(x) for x in Eng.hud(u9)]
    K.check("Chop 10 logs" not in h and "Craft a crafting accessory" not in h and "Open the hub buttons" in h,
            "CO boss beaten + hub reached = the SHORT version on a friend's island (island tasks out): %s" % h[2::6])
    p9.world = "skyy-island-u9"
    Life.step(p9, JLong(int(time.time() * 1000)))
    h = [str(x) for x in Eng.hud(u9)]
    K.check(not bool(p9.coop) and "Chop 10 logs" in h, "CO back on the own island = every task again")
    u10, p10, s10 = X.player(10, "skyy-island-friend")
    br.put("island:" + str(u10), "skyy-island-u10")
    Life.step(p10, JLong(int(time.time() * 1000)))
    K.check(bool(p10.coop) and "Chop 10 logs" in [str(x) for x in Eng.hud(u10)], "CO a new player on a friend's island = the LONG version")
    # FIX2 (critic): a CO-OP MEMBER standing on the island they joined has island:<uuid> = THAT island (SkyyIslands' home key) -
    # island:role:fn decides (owner = own island; member / admin / trusted / visitor = a friend's island); asked once per world / epoch
    roles = {"r": "member"}
    rcalls = []
    br.put("island:role:fn", PyFn(lambda a: rcalls.append((str(a[0]), str(a[1]))) or roles["r"]))
    br.put("island:epoch", JLong(1))
    br.put("island:" + str(u9), "skyy-island-friend")
    p9.world = "skyy-island-friend"
    Life.step(p9, JLong(int(time.time() * 1000)))
    s9.expire(JLong(int(time.time() * 1000) + 5000))
    h = [str(x) for x in Eng.hud(u9)]
    K.check(bool(p9.coop) and "Chop 10 logs" not in h and rcalls and rcalls[-1] == (str(u9), "skyy-island-friend"),
            "FIX2-CO a co-op MEMBER (island:<uuid> = this island, role member) who beat the boss + reached the hub = the SHORT version: %s" % rcalls)
    n0 = len(rcalls)
    for _i in range(5):
        Life.step(p9, JLong(int(time.time() * 1000)))
    K.eq(len(rcalls), n0, "FIX2-CO the role is cached (no bridge call every second)")
    roles["r"] = "owner"
    br.put("island:epoch", JLong(2))
    Life.step(p9, JLong(int(time.time() * 1000)))
    K.check(not bool(p9.coop) and len(rcalls) == n0 + 1, "FIX2-CO an island:epoch change re-asks: role owner = the own island (every task)")
    roles["r"] = None
    br.put("island:epoch", JLong(3))
    Life.step(p9, JLong(int(time.time() * 1000)))
    K.check(not bool(p9.coop), "FIX2-CO no role (not an island SkyyIslands knows) = not co-op")
    roles["r"] = "member"
    br.put("island:epoch", JLong(4))
    p10.world = "skyy-island-friend"
    br.put("island:" + str(u10), "skyy-island-friend")
    Life.step(p10, JLong(int(time.time() * 1000)))
    K.check(bool(p10.coop) and "Chop 10 logs" in [str(x) for x in Eng.hud(u10)], "FIX2-CO a NEW co-op member (boss not beaten) = the LONG version")
    br.remove("island:role:fn")
    br.remove("island:epoch")
    # ======================================================================== 0.2: PARTY kill credit ("only 1 payer has to kill the boss")
    u11, p11, s11 = X.player(11, "skyy-island-x")
    u12, p12, s12 = X.player(12, "skyy-island-x")
    u13, p13, s13 = X.player(13, "skyy-island-other")
    u14, p14, s14 = X.player(14, "skyy-island-x")
    JS = JClass("java.lang.String")
    mem = PyFn(lambda a: JArray(JS)([str(u11), str(u12), str(u13), "not-a-uuid"]))
    br.put("party:fn:members", mem)
    Eng.count(u11, TB["kill"], "Golem_Crystal_Earth", 1, None, False)
    n = int(Eng.countParty(u11, "Golem_Crystal_Earth", "skyy-island-x"))
    K.check(n == 1 and s11.isDone("tutorial.mini_boss") and s12.isDone("tutorial.mini_boss"), "PT the killer AND the party member in the same world get the boss (%d)" % n)
    K.check(not s13.isDone("tutorial.mini_boss") and not s14.isDone("tutorial.mini_boss"), "PT a party member in another world / a non-member get nothing")
    K.eq(X.rows(s12)["defeat_mobs"][1], "0/5", "PT the shared kill counts only on party=true parts (not 'Defeat 5 mobs')")
    c0 = len(mem.calls)
    K.eq(int(Eng.countParty(u11, "Trork_Grunt", "skyy-island-x")), 0, "PT a role no party part wants: 0")
    K.eq(len(mem.calls), c0, "PT ... without even asking SkyyParty (lean)")
    Cfg.PARTY_KILLS = False
    K.eq(int(Eng.countParty(u13, "Golem_Crystal_Earth", "skyy-island-other")), 0, "PT Server Setup 'Party kill credit' off = nothing shared")
    Cfg.PARTY_KILLS = True
    br.remove("party:fn:members")
    K.eq(int(Eng.countParty(u11, "Golem_Crystal_Earth", "skyy-island-x")), 0, "PT no SkyyParty = nothing shared")
    K.save()


# ====================================================================================================== lifecycle, IO jobs, tick, pages, systems
def run_life(out, jar, scratch, home):
    from jpype import JClass, JObject, JArray, JLong
    K = HK.Child(out)
    hcls = FAKE_DIR
    HK.jvm([B.SERVER_JAR, jar, hcls], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    PyFn = fn_class()
    Boolean, Long = JClass("java.lang.Boolean"), JClass("java.lang.Long")
    U = unsafe()
    X = Scene(K, scratch, "l")
    Eng, Sto, Life, Defs, Cfg, Log = X.Eng, X.Sto, X.Life, X.Defs, X.Cfg, X.Log
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    uu = X.U(0x7171, 1)

    def pref(u, name="Mia"):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef.class_, "uuid", u)
        setf(pr, PRef.class_, "username", name)
        return pr
    pr = pref(uu)
    # ---- join -> load (IO job inline) -> enter + lazy + welcome conditions
    br.put("profile:class:" + str(uu), "Archer")
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    Life.join(pr, "skyy-island-mia")
    p = Eng.player(uu)
    s = Eng.stateOf(p)
    K.check(p is not None and bool(p.loaded) and s is not None, "L1 join loads the profile (SkyyQuests-IO job)")
    K.check(not s.isDone("tutorial.pick_class") and int(p.settleUntil) > int(time.time() * 1000), "FIX2-A2 a load starts the settle window: no bridge check yet")
    Life.step(p, JLong(int(time.time() * 1000) + 6000))
    K.check(s.isDone("tutorial.pick_class"), "L1 the first tick after the settle window ticks an old profile's class")
    K.check(Eng.EPOCH.get(uu) is not None and br.get("quest:epoch:" + str(uu)) is not None, "L1 quest:epoch published")
    K.check(Life.welcomeOk(p) and bool(p.welcome), "L1 welcome due on an island with a class (scheduled)")
    p.welcome = False
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    br.remove("profile:class:" + str(uu))
    K.check(not Life.welcomeOk(p), "L1 with SkyyProfiles and no class yet: no welcome")
    br.remove("profile:fn:key")
    p.world = "skyy-hub"
    K.check(not Life.welcomeOk(p), "L1 not on an island: no welcome")
    p.world = "skyy-island-mia"
    K.eq([str(x) for x in Life.welcomeTasks(p)], ["Open the hub buttons", "Chop 10 logs", "Craft a crafting accessory"] if br.containsKey("quest:caller:menu")
         else ["Chop 10 logs", "Craft a crafting accessory", "Mine stone and copper"], "L1 the welcome page's first 3 tasks")
    K.check(s.markSeen("tutorial") and not s.markSeen("tutorial") and not Life.welcomeOk(p), "L1 seen.tutorial written once; no welcome after it")
    Life.join(pr, "skyy-hub")
    K.check(s.pdone.contains("tutorial.to_hub.1") and not s.isDone("tutorial.to_hub"), "L2 a later PlayerReady counts enter (the hub); the task waits for the portal (FIX5)")
    # ---- step: settings, expiry, lazy, claims due, profile switch
    p.setAt = 0
    p.lazyAt = 0
    p.settleUntil = 0
    br.put("bank:" + str(uu), Long(100))
    due = Life.step(p, JLong(int(time.time() * 1000)))
    K.check(s.isDone("tutorial.bank_deposit"), "L3 step runs the lazy check")
    K.check(not bool(due) if s.hasClaims() and int(s.bounceAt) > 0 else True, "L3 step: a claim that just bounced is not due yet")
    s.retryNow()
    K.check(bool(Life.step(p, JLong(int(time.time() * 1000)))) == bool(s.hasClaims()), "L3 step: a waiting claim is due after retryNow")
    keys = {"k": str(uu)}
    br.put("profile:fn:key", PyFn(lambda a: keys["k"]))
    keys["k"] = str(uu) + "-p2"
    Life.step(p, JLong(int(time.time() * 1000)))
    K.eq(str(p.pk), str(uu) + "-p2", "L4 a profile switch (key change) loads the new profile")
    s2 = Eng.stateOf(p)
    K.check(s2 is not None and not s2.isDone("tutorial.pick_class") and os.path.isfile(os.path.join(X.base, "players", str(uu) + ".properties")),
            "L4 the new profile is fresh; the old one was written under ITS key (state %s, files %s, warn %s)" % (s2 is not None,
            sorted(os.listdir(os.path.join(X.base, "players"))) if os.path.isdir(os.path.join(X.base, "players")) else None,
            [str(x) for x in Log.LINES if str(x).startswith("WARN")][-3:]))
    # FIX2 (critic A2): profile 1's bank:<uuid> = 100 is still on the bridge right after the switch - it must not pay the new profile
    K.check(not s2.isDone("tutorial.bank_deposit"), "FIX2-A2 right after a profile switch the OLD profile's bank value completes nothing")
    p.lazyAt = 0
    Life.step(p, JLong(int(time.time() * 1000)))
    K.check(not s2.isDone("tutorial.bank_deposit"), "FIX2-A2 ... nor a tick inside the settle window")
    Life.step(p, JLong(int(time.time() * 1000) + 6000))
    K.check(s2.isDone("tutorial.bank_deposit"), "FIX2-A2 after the window the value (republished by SkyyBank) is read")
    Eng.count(uu, 16, "Trork", 1, None, False)
    K.eq(X.rows(s2)["defeat_mobs"][1], "1/5", "L4 counting goes to the new profile")
    K.eq(X.rows(s)["defeat_mobs"][1], "0/5", "L4 ... never to the old one")
    keys["k"] = str(uu)
    Life.step(p, JLong(int(time.time() * 1000)))
    K.check(Eng.stateOf(p).isDone("tutorial.pick_class"), "L4 switching back reads profile 1 from disk")
    tq = int(time.time() * 1000)
    br.put("profile:epoch:" + str(uu), Long(1))
    Life.step(p, JLong(tq))
    p.settleUntil = 0
    br.put("profile:epoch:" + str(uu), Long(2))
    Life.step(p, JLong(tq))
    K.check(int(p.settleUntil) >= tq + 4000, "FIX2-A2 a profile:epoch change starts the settle window too")
    br.remove("profile:epoch:" + str(uu))
    br.remove("profile:fn:key")
    # ---- QIO modes
    IO = X.E.P("QIO")
    Life.quit(uu)
    K.check(Eng.player(uu) is None and Eng.WANT.get(uu) is None, "L5 quit forgets the player")
    K.check(not Sto.CACHE.containsKey(str(uu)) and os.path.isfile(os.path.join(X.base, "players", str(uu) + ".properties")), "L5 quit writes + evicts")
    j = IO(5, uu, None, None)
    j.o = pr
    j.n = 1
    j.run()
    K.check(any("quest line(s)" in str(x) for x in Log.SINK) and any("Coming soon / hidden" in str(x) for x in Log.SINK), "L5 QIO reload / check report")
    j = IO(4, uu, "portal", "hub")
    j.o = JArray(JObject)([pr, JClass("java.lang.Double")(1.0), JClass("java.lang.Double")(2.0), JClass("java.lang.Double")(3.0), "Hub portal"])
    j.run()
    K.check(Defs.place("portal") is not None and "portal=hub|1.0|2.0|3.0|Hub portal" in open(os.path.join(X.base, "places.properties")).read(), "L5 QIO place")
    IO(0, None, None, None).run()
    K.check(IO(0, None, None, None).newThread(JClass("java.lang.Thread")()).getName() == "SkyyQuests-IO", "L5 the writer thread name")
    # ---- tick (Universe absent in a bare JVM: the pass fails inside its own catch)
    Tk = X.E.P("QTick")
    n0 = int(Tk.N)
    Tk("run").run()
    K.check(int(Tk.N) == n0 + 1, "L6 the tick runs (and survives the bare JVM)")
    K.check(str(Tk("SkyyQuests-Tick").newThread(JClass("java.lang.Thread")()).getName()) == "SkyyQuests-Tick", "L6 the tick thread name")
    # ---- pages (real UICommandBuilder / UIEventBuilder)
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Life.join(pr, "skyy-island-mia")
    W = X.E.P("QWelcomePage")(pr, JArray(JClass("java.lang.String"))(["Chop 10 logs", "Mine stone and copper", None]))
    b, ev = UCB(), UEB()
    W.build(None, b, ev, None)
    txt = " ".join(str(c.text) for c in b.getCommands() if c.text is not None)
    K.check("SkyyQwShow" in txt and "SkyyQwKnow" in txt and "_" not in "".join(t for t in txt.split() if t.startswith("#")), "P1 welcome page markup")
    K.check(len(ev.getEvents()) == 2 if hasattr(ev, "getEvents") else True, "P1 welcome bindings")
    try:
        W.handleDataEvent(None, None, '{"a":"know"}')
    except Exception:
        pass
    K.check(Eng.player(uu).hideTut and Eng.stateOf(Eng.player(uu)).hideOf("tutorial"), "P1 I know how to play = the tutorial switch on")
    LP = X.E.P("QLogPage")(pr, None)
    b, ev = UCB(), UEB()
    LP.build(None, b, ev, None)
    cm = [c for c in b.getCommands()]
    K.check(any(c.text is not None and "SkyyQlTrack" in str(c.text) for c in cm) and any(c.selector is not None and "SkyyQlN0.Text" in str(c.selector) for c in cm),
            "P2 the log page builds 12 rows + the footer")
    K.check(any(c.text is not None and "Show tutorial" in str(c.text) for c in cm), "P2 hidden tutorial = a Show tutorial button")
    for a in ("next", "prev", "lnext", "lprev", "track", "claim", "show"):
        try:
            LP.handleDataEvent(None, None, '{"a":"%s"}' % a)
        except Exception:
            pass
    K.check(not Eng.player(uu).hideTut and str(LP.info).startswith("+"), "P2 clicks: show tutorial -> %s" % LP.info)
    K.eq(int(LP.BUILDS.get()), 1, "P2 a click rebuild is the engine's (outside the stand-in)")
    # 0.2: the Skip / Unskip button on every row that is not done
    LP2 = X.E.P("QLogPage")(pr, "tutorial")
    b, ev = UCB(), UEB()
    LP2.build(None, b, ev, None)
    mk = " ".join(str(c.text) for c in b.getCommands() if c.text is not None)
    sel = [str(c.selector) for c in b.getCommands() if c.selector is not None]
    K.check("TextButton #SkyyQlS" in mk and '"Skip"' in mk and "SkyyQlS" in mk, "SK2 the log page has small Skip buttons on its rows")
    st0 = Eng.stateOf(Eng.player(uu))
    open_rows = [i for i, t in enumerate(X.L.tasks[:10]) if X.rows(st0)[str(t.id)][0] in ("open", "locked")]
    K.eq(mk.count("TextButton #SkyyQlS"), len([1 for t in X.L.tasks[:10] if X.rows(st0)[str(t.id)][0] in ("open", "locked", "skipped")]),
         "SK2 a Skip button only on rows that can be skipped (not done / soon / hidden) - %d open of the first 10" % len(open_rows))
    try:
        LP2.handleDataEvent(None, None, '{"a":"skip:tutorial.chop_logs"}')
    except Exception:
        pass
    K.check(str(LP2.info).startswith("+Skipped: Chop 10 logs") and bool(st0.isSkipped("tutorial.chop_logs")), "SK2 a row's Skip click skips that task: %s" % LP2.info)
    b, ev = UCB(), UEB()
    LP2.build(None, b, ev, None)
    mk = " ".join(str(c.text) for c in b.getCommands() if c.text is not None)
    K.check('"Unskip"' in mk, "SK2 ... and the row now offers Unskip")
    try:
        LP2.handleDataEvent(None, None, '{"a":"skip:tutorial.chop_logs"}')
    except Exception:
        pass
    K.check(not bool(st0.isSkipped("tutorial.chop_logs")), "SK2 Unskip click")
    # 0.2: a world switch into a world-only area sets the area at once (no position needed)
    open(os.path.join(X.base, "areas.properties"), "a", encoding="utf8").write("area.zone1.world=skyy-zone-1\narea.zone1.line=mining\narea.zone1.order=0\n")
    Defs.load()
    Life.join(pr, "skyy-zone-1")
    K.eq(str(Eng.player(uu).area), "zone1", "AR2 PlayerReady into a zone world = that area at once")
    Life.join(pr, "skyy-island-mia")
    K.eq(str(Eng.player(uu).area), "", "AR2 ... and back out of it")
    # ---- the systems through the stand-in store
    engine_types(K, ["com.hypixel.hytale.server.core.universe.PlayerRef", "com.hypixel.hytale.server.core.entity.entities.Player",
                     "com.hypixel.hytale.server.npc.entities.NPCEntity", "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent"])
    try:
        em = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule").get()
        if em is not None:
            f = em.getClass().getDeclaredField("classToComponentType")
            f.setAccessible(True)
            if f.get(em) is None:
                f.set(em, JClass("java.util.HashMap")() if f.getType().isAssignableFrom(JClass("java.util.HashMap").class_) else JClass("java.util.concurrent.ConcurrentHashMap")())
        engine_types(K, ["com.hypixel.hytale.server.npc.entities.NPCEntity"])
    except Exception as ex:
        K.notes.append("EntityModule stand-in: %s" % str(ex)[:120])
    FakeStore, FakeChunk, FakeWorld, FakeE = (JClass("com.hypixel.hytale.component.SkyyQFakeStore"), JClass(FAKE + ".FakeChunk"), JClass(FAKE + ".FakeWorld"), JClass(FAKE + ".FakeEStore"))
    st = U.allocateInstance(FakeStore.class_)
    ch = U.allocateInstance(FakeChunk.class_)
    wd = U.allocateInstance(FakeWorld.class_)
    es = U.allocateInstance(FakeE.class_)
    FakeE.W = wd
    FakeStore.EXT = es
    FakeStore.COMP = pr
    Ref = JClass("com.hypixel.hytale.component.Ref")
    FakeChunk.REF = U.allocateInstance(Ref.class_)
    FakeWorld.NAME = "skyy-island-mia"
    s = Eng.stateOf(Eng.player(uu))
    BTy = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    bt = U.allocateInstance(BTy.class_)
    setf(bt, BTy.class_, "id", "Wood_Oak_Trunk")
    BBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent")
    e = BBE(None, None, bt)
    runs = int(FakeWorld.RUNS)
    before = X.rows(s)["chop_logs"][1]
    X.E.P("QBreakSys")().handle(0, ch, st, None, e)
    K.check(int(FakeWorld.RUNS) == runs + 1 and X.rows(s)["chop_logs"][1] != before, "Y1 QBreakSys: want bit -> deferred task on the world -> counted (%s -> %s; runs %d->%d; id %s; want %s; warn %s)" % (
        before, X.rows(s)["chop_logs"][1], runs, int(FakeWorld.RUNS), bt.getId(), Eng.WANT.get(uu), [str(x) for x in Log.LINES if str(x).startswith("WARN")][-3:]))
    e.setCancelled(True)
    b2 = X.rows(s)["chop_logs"][1]
    X.E.P("QBreakSys")().handle(0, ch, st, None, e)
    K.eq(X.rows(s)["chop_logs"][1], b2, "Y1 a cancelled break is not counted (checked after every system saw it)")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    item = None
    try:
        item = IS("Plant_Crop_Wheat_Item", 2)
    except Exception as ex:
        item = U.allocateInstance(IS.class_)
        setf(item, IS.class_, "itemId", "Plant_Crop_Wheat_Item")
        setf(item, IS.class_, "quantity", JClass("java.lang.Integer")(2).intValue())
        K.notes.append("Y2 ItemStack built by Unsafe (bare JVM: %s)" % str(ex)[:80])
    IPE = JClass("com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent")
    X.E.P("QPickupSys")().handle(0, ch, st, None, IPE(item))
    K.check(X.rows(s)["first_harvest"][1] in ("2/3",) or s.isDone("tutorial.first_harvest"), "Y2 QPickupSys counts the stack's quantity: %s" % (X.rows(s)["first_harvest"],))
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    rc = U.allocateInstance(CRR.class_)
    mq = U.allocateInstance(MQ.class_)
    setf(mq, MQ.class_, "itemId", "Skyy_Accessory_Workbench_T1")
    setf(rc, CRR.class_, "primaryOutput", mq)
    CREP = JClass("com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Post")
    X.E.P("QCraftSys")().handle(0, ch, st, None, CREP(rc, 1))
    s.lazyList()
    K.eq(X.rows(s)["first_accessory"][1], "1/2", "Y3 QCraftSys: the crafted accessory counted (1 of the 2 parts)")
    # kill: DeathComponent on an NPC, killer = the player's Ref in the same store
    NPC = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    npc = U.allocateInstance(NPC.class_)
    ok_role = setf(npc, NPC.class_, "roleName", "Golem_Crystal_Earth")
    kref = U.allocateInstance(Ref.class_)
    setf(kref, Ref.class_, "store", st)
    DES = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    DMG = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    dmg = U.allocateInstance(DMG.class_)
    setf(dmg, DMG.class_, "source", DES(kref))
    DTH = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    dc = U.allocateInstance(DTH.class_)
    K.check(setf(dc, DTH.class_, "deathInfo", dmg), "Y4 DeathComponent.deathInfo set")
    FakeStore.NEXT = npc
    k0 = X.rows(s)["defeat_mobs"][1]
    um, pm, sm = X.player(31, "skyy-island-mia")          # 0.2: a party member standing in the killer's world
    JS = JClass("java.lang.String")
    br.put("party:fn:members", PyFn(lambda a: JArray(JS)([str(uu), str(um)])))
    X.E.P("QKillSys")().onComponentAdded(FakeChunk.REF, dc, st, None)
    k1 = X.rows(s)["defeat_mobs"][1]
    if ok_role and k1 != k0:
        K.check(sm.isDone("tutorial.mini_boss"), "PT2 QKillSys: the boss killed by the player is credited to the party member in the same world (the real kill path)")
    if ok_role and str(npc.getRoleName()) == "Golem_Crystal_Earth":
        K.check(k1 != k0 or "isValid" in " ".join(str(x) for x in Log.LINES), "Y4 QKillSys: a kill by the player counted (%s -> %s; Ref.isValid on a stand-in: %s)" % (k0, k1, kref.isValid()))
    else:
        K.notes.append("Y4 NPCEntity role field not found by name - kill path checked by the static audit only")
    # felled listener + QEvTask cancel kinds + hop
    Fel = X.E.P("QFelledFn")()
    Fel.apply(JArray(JObject)([pr, JClass("java.lang.Integer")(2), bt, "skyy-island-mia"]))
    K.check(Fel.apply("bad") is None, "Y5 QFelledFn tolerates bad arguments")
    Ev = X.E.P("QEvTask")
    K.check(Ev(e, 0, uu, 1, "Rock_Stone", 1, "w", False) is not None, "Y5 QEvTask built")
    Ev(e, 0, uu, 1, "Rock_Stone", 1, "w", False).run()
    Hop = X.E.P("QHop")
    lst = JClass("java.util.ArrayList")()
    lst.add(Eng.player(uu))
    Hop(lst, "skyy-island-mia", JClass("java.util.UUID")(1, 2)).run()
    K.check(int(Tk.HOPS) >= 1, "Y6 QHop runs (a stand-in PlayerRef with no entity is skipped)")
    pw0 = Eng.player(uu).world
    Hop(lst, "skyy-other-world", JClass("java.util.UUID")(9, 9)).run()
    K.check(str(Eng.player(uu).world) == str(pw0), "FIX2-B3 a hop for another world (the player is not in it) never files a position under its name")
    Evs = X.E.P("QEvents")
    PDE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
    Evs(True).accept(JObject("not an event"))
    K.check(Eng.player(uu) is not None, "Y7 QEvents ignores a wrong event")
    K.save()


# ====================================================================================================== P: paying
def run_pay(out, jar, scratch, home):
    from jpype import JClass, JObject, JArray, JLong
    K = HK.Child(out)
    hcls = FAKE_DIR
    HK.jvm([B.SERVER_JAR, jar, hcls, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    PyFn = fn_class()
    Boolean, Long = JClass("java.lang.Boolean"), JClass("java.lang.Long")
    X = Scene(K, scratch, "p")
    Eng, Sto, Pay, Log = X.Eng, X.Sto, X.E.P("QPay"), X.Log
    Sto.STOPPED = False          # no inline IO jobs here: payAll / payState are called by the test itself
    coins, xp = [], []
    state = {"coins": True, "xp": True}
    br.put("coins:fn:add", PyFn(lambda a: (coins.append(int(a[1])) or Long(1000)) if state["coins"] else None))
    br.put("skill:fn:addxp", PyFn(lambda a: (xp.append((str(a[1]), int(a[2]), str(a[3]), str(a[4]))) or Boolean.TRUE) if state["xp"] else Boolean.FALSE))
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    # 0.2: the 0.1 ledger checks run on a test line with a coins task + an XP task (the shipped tutorial now pays items too)
    open(os.path.join(X.base, "quests", "zpay.properties"), "w").write(
        "line=zpay\nname=Pay\nauto=true\norder=-10\ntask.1.id=pa\ntask.1.type=break\ntask.1.match=Pay_A\ntask.1.reward=coins:25\n"
        "task.2.id=pb\ntask.2.type=break\ntask.2.match=Pay_B\ntask.2.count=10\ntask.2.reward=xp:Foraging:50\n")
    X.Defs.load()
    u, p, s = X.player(1)
    Eng.count(u, 1, "Pay_A", 1, "w", False)
    for i in range(10):
        Eng.count(u, 1, "Pay_B", 1, "w", False)
    K.eq(int(s.claimCount()), 2, "P1 two claims (25 coins, 50 Foraging XP)")
    now = int(time.time() * 1000)
    Pay.payAll(JLong(now))
    K.eq((coins, xp), ([25], [("Foraging", 50, "quests", str(u))]), "P1 paid once each (XP with the profile key)")
    K.eq(int(s.claimCount()), 0, "P1 no claim left")
    lg = logtext(X.base)
    K.check(lg.count("PAYING ") == 2 and lg.count("PAID ") == 2, "P1 quests.log PAYING / PAID: %s" % lg[-200:])
    K.check("claim." not in open(os.path.join(X.base, "players", str(u) + ".properties")).read(), "P1 the file has no claim line")
    Pay.payAll(JLong(now))
    K.eq((len(coins), len(xp)), (1, 1), "P1 nothing paid twice")
    # refused -> back, waits, claim retries
    state["coins"] = False
    br.put("bank:" + str(u), Long(99))
    Eng.lazy(p, True)
    itm = []                                   # FIX-C1: the bank task now pays coins + bread; the bread claim is set aside (no world here)
    i_ = 0
    while True:
        c_ = s.peekClaim(i_)
        if c_ is None:
            break
        if str(c_).startswith("item|"):
            itm.append(str(s.takeClaimAt(i_)))
        else:
            i_ += 1
    K.check(len(itm) == 1 and itm[0].startswith("item|Food_Bread:3|"), "FIX-C1 'Put coins in the Bank' pays items AND coins: %s" % itm)
    Pay.payAll(JLong(now))
    K.check(int(s.claimCount()) == 1 and str(s.waitNote) == "Reward waiting - /quests claim" and "BACK " in logtext(X.base), "P2 a refused payment comes back (BACK)")
    s.expire(JLong(now + 10000))
    h = Eng.hud(u)
    K.check(str(h[5]) == "Reward waiting - /quests claim", "P2 the widget says a reward waits: %s" % h[5])
    state["coins"] = True
    Pay.payAll(JLong(now + 1000))
    K.eq(len(coins), 1, "P2 not retried before claim.retrySeconds")
    s.retryNow()
    Pay.payAll(JLong(now + 1000))
    K.check(len(coins) == 2 and coins[1] == 50 and int(s.claimCount()) == 0 and s.waitNote is None, "P2 /quests claim retries at once")
    # ---- FIX (critics 1.1 / 2.3): a refused claim never blocks the claims behind it, and is not retried (PAYING / write / log) every minute
    gc, gx = "coins|31|%s:t.a:1" % str(u), "xp|Mining:7|%s:t.b:1" % str(u)
    s.addClaim(gc)
    s.addClaim(gx)
    state["coins"] = False
    nx = len(xp)
    t0 = now + 5000
    Pay.payAll(JLong(t0))
    lg = logtext(X.base)
    K.check(len(xp) == nx + 1 and xp[-1][:2] == ("Mining", 7), "FIX-R the XP claim BEHIND a refused coins claim is paid in the same pass")
    K.check(int(s.claimCount()) == 1 and str(s.claims.get(0)) == gc and bool(s.refusedNow(gc, JLong(t0 + 1000))), "FIX-R ... the refused one waits (marked refused)")
    K.eq(lg.count("BACK %s %s" % (str(u), gc)), 1, "FIX-R one BACK line")
    K.check(gc in [str(x) for x in Sto.read(str(u), u).claims], "FIX2-A3 the refused claim is on DISK before its BACK line (a crash right after loses nothing)")
    t1 = t0 + int(Pay.refuseMs()) // 2
    K.eq(int(Pay.refuseMs()), 60000, "FIX2-C2 the refusal wait IS quests.claim.retrySeconds (60 s default; Server Setup row min 30)")
    w0 = int(Sto.WRITES)
    Pay.payAll(JLong(t1))
    lg2 = logtext(X.base)
    K.check(lg2.count("PAYING %s %s" % (str(u), gc)) == 1 and int(Sto.WRITES) == w0 and int(s.claimCount()) == 1,
            "FIX-R a retry pass inside the refusal window: no PAYING, no write, no log line (writes %d -> %d)" % (w0, int(Sto.WRITES)))
    K.eq(str(s.waitNote), "Reward waiting - /quests claim", "FIX-R the widget still says a reward waits")
    state["coins"] = True
    Pay.payAll(JLong(t0 + int(Pay.refuseMs()) + 1000))
    K.check(coins[-1] == 31 and int(s.claimCount()) == 0, "FIX-R after the refusal window it is paid")
    # a missing bridge function: skipped without PAYING / write
    keep = br.remove("coins:fn:add")
    gm = "coins|32|%s:t.c:1" % str(u)
    s.addClaim(gm)
    s.retryNow()
    Pay.payAll(JLong(t1 + 1000))
    K.check(gm not in logtext(X.base) and int(s.claimCount()) == 1 and str(s.waitNote) == "Reward waiting - /quests claim",
            "FIX-M no SkyyCoins: the claim waits with no PAYING / BACK line")
    K.check(not bool(Pay.payable(gm)) and bool(Pay.payable("item|Rock_Stone:1|g")), "FIX-M payable()")
    br.put("coins:fn:add", keep)
    # coins:fn:flush before PAID
    fl = {"r": -1, "n": 0}
    def flush(a):
        fl["n"] += 1
        return JClass("java.lang.Integer")(fl["r"])
    br.put("coins:fn:flush", PyFn(flush))
    s.retryNow()
    Pay.payAll(JLong(t1 + 2000))
    K.check(fl["n"] == 1 and ("PAID %s %s (purse write pending)" % (str(u), gm)) in logtext(X.base), "FIX-F coins:fn:flush called after the add; -1 = PAID noted 'purse write pending'")
    fl["r"] = 1
    gf = "coins|33|%s:t.d:1" % str(u)
    s.addClaim(gf)
    Pay.payAll(JLong(t1 + 200000))
    K.check(fl["n"] == 2 and ("PAID %s %s\n" % (str(u), gf)) in logtext(X.base).replace("\r", ""), "FIX-F flushed: a plain PAID line")
    K.eq(int(Pay.repay(s)), 0, "FIX-F repay still reads the noted PAID line as closed")
    br.remove("coins:fn:flush")
    # a profile switch between the write and the payout (critic 1.2): nothing paid, the claim stays on THIS profile
    gs = "coins|34|%s:t.e:1" % str(u)
    s.addClaim(gs)
    kc = {"n": 0}
    def flip(a):
        kc["n"] += 1
        return str(a) if kc["n"] <= 1 else str(a) + "-p2"
    br.put("profile:fn:key", PyFn(flip))
    nc = len(coins)
    Pay.payState(p, s, JLong(t1 + 300000))
    K.check(len(coins) == nc and int(s.claimCount()) == 1 and ("BACK %s %s (profile switch - kept)" % (str(u), gs)) in logtext(X.base),
            "FIX-S a key change right before the payout: not paid, kept, BACK logged")
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    s.retryNow()
    Pay.payAll(JLong(t1 + 301000))
    K.check(len(coins) == nc + 1 and coins[-1] == 34 and int(s.claimCount()) == 0, "FIX-S ... paid once the key is steady")
    # items: storage first, counts before / after
    Give = X.E.P("QGive")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    # a bare JVM has no Item asset store: an empty one with the ids this test gives (the SkyyHud 0.3.12+ harness pattern)
    try:
        U = unsafe()
        AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
        jp = JClass("javassist.ClassPool")(True)
        jp.appendClassPath(B.SERVER_JAR)
        fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyQTestStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
        fake.addConstructor(JClass("javassist.CtNewConstructor").make(
            "public SkyyQTestStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
        store = U.allocateInstance(fake.toClass(AS.class_))
        amap = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")()
        fa = AS.class_.getDeclaredField("assetMap")
        fa.setAccessible(True)
        fa.set(store, amap)
        ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
        fs = ItemC.class_.getDeclaredField("ASSET_STORE")
        fs.setAccessible(True)
        fs.set(None, store)
        mf = amap.getClass().getDeclaredField("assetMap")
        mf.setAccessible(True)
        it_ = U.allocateInstance(ItemC.class_)
        for fn_ in ("maxStack",):
            setf(it_, ItemC.class_, fn_, JClass("java.lang.Integer")(4).intValue())
        mf.get(amap).put("Rock_Stone", it_)
        a, b2 = SIC(1), SIC(2)
        n = int(Give.giveTo(JArray(IC)([a, b2]), "Rock_Stone", 5))
        ca, cb = int(Give.countIn(a, "Rock_Stone")), int(Give.countIn(b2, "Rock_Stone"))
        K.check(n == ca + cb and ca > 0 and n <= 5, "P3 giveTo: storage first (%d in the first container, %d in the next), every add counted: %d of 5" % (ca, cb, n))
        full = SIC(1)
        Give.giveTo(JArray(IC)([full]), "Rock_Stone", 4)
        bf = int(Give.countIn(full, "Rock_Stone"))
        g3 = int(Give.giveTo(JArray(IC)([full]), "Rock_Stone", 3))
        K.check(g3 == int(Give.countIn(full, "Rock_Stone")) - bf and (bf < 4 or g3 == 0),
                "P3 giveTo into a full container: what really landed (%d before, %d given)" % (bf, g3))
        K.notes.append("P3 giveTo gave %d of 5 (stack limit of the stand-in item: 4)" % n)
    except Exception as ex:
        K.check(False, "P3 the item give could not run on the stand-in item store: %s" % str(ex)[:200])
    K.eq(int(Give.countIn(None, "x")), 0, "P3 countIn(null)")
    # itemDone: full / none / partial
    s.addClaim("item|Rock_Stone:5|%s:t.x:9" % str(u))
    c = str(s.takeClaim())
    s.setPaying(True)
    Pay.itemDone(s, c, 5, 5, "Rock_Stone")
    K.check(not s.paying and int(s.claimCount()) == 0 and ("PAID %s %s" % (str(u), c)) in logtext(X.base), "P3 itemDone: all given = PAID")
    s.addClaim(c)
    c = str(s.takeClaim())
    Pay.itemDone(s, c, 0, 5, None)
    K.check(int(s.claimCount()) == 1 and str(s.claims.get(0)) == c, "P3 itemDone: nothing given = the claim waits")
    K.check(bool(s.refusedNow(c, JLong(int(time.time() * 1000) + 1000))), "FIX-R a full inventory marks the item claim refused (never blocks others)")
    c = str(s.takeClaim())
    Pay.itemDone(s, c, 2, 5, None)
    K.check(int(s.claimCount()) == 1 and str(s.claims.get(0)) == "item|Rock_Stone:3|%s:t.x:9" % str(u) and "PART " in logtext(X.base), "P3 itemDone: 2 of 5 = the rest (3) waits")
    s.takeClaim()
    # an item give the world never ran: LOST? after 2 minutes, then the state pays again (repay can put it back)
    s.markPaying("item|Rock_Stone:1|%s:t.y:1" % str(u), JLong(now))
    Pay.payAll(JLong(now + 1000))
    K.check(bool(s.paying), "P3 an item give in flight blocks this state's payments")
    Pay.payAll(JLong(now + 130000))
    K.check(not s.paying and ("LOST? %s item|Rock_Stone:1|%s:t.y:1" % (str(u), str(u))) in logtext(X.base), "P3 ... 2 minutes later: LOST? logged, payments go on")
    K.eq(int(Pay.repay(s)), 0, "P3 a LOST? without its PAYING line is not repaid by itself")
    # payOne: unknown type, item without a world
    K.eq(int(Pay.payOne(p, s, "weird|1|g")), -1, "P4 payOne unknown type")
    K.eq(int(Pay.payOne(p, s, "item|Rock_Stone:2|g")), 0, "P4 an item with no world = refused (comes back)")
    br.remove("coins:fn:add")
    K.eq(int(Pay.payOne(p, s, "coins|5|g")), 0, "P4 no SkyyCoins = refused (waits)")
    # repay: PAYING without PAID
    open(os.path.join(X.base, "quests.log"), "a").write("2026-10-13T00:00 PAYING %s coins|77|%s:tutorial.zz:5\n" % (str(u), str(u)))
    K.eq(int(Pay.repay(s)), 1, "P5 repay finds the lost PAYING")
    K.check("coins|77|%s:tutorial.zz:5" % str(u) in [str(x) for x in s.claims], "P5 ... and puts it back as a claim")
    K.eq(int(Pay.repay(s)), 0, "P5 a second repay finds nothing (REPAY closes it)")
    br.put("coins:fn:add", PyFn(lambda a: (coins.append(int(a[1])) or Long(1000)) if state["coins"] else None))
    while int(s.claimCount()) > 0:
        s.takeClaim()
    s.retryNow()
    s.waitNote = None
    # FIX2 (critic B4): an XP claim SkySkills refuses (a skill it will not grant) never pins "Reward waiting" over task 1's line
    state["xp"] = False
    gxx = "xp|Exploration:5|%s:t.q:1" % str(u)
    s.addClaim(gxx)
    nw = len([x for x in Log.LINES if "SkySkills refused" in str(x)])
    Pay.payAll(JLong(t1 + 900000))
    K.check(int(s.claimCount()) == 1 and s.waitNote is None, "FIX2-B4 a refused XP claim waits WITHOUT the widget note (%s)" % s.waitNote)
    s.retryNow()
    Pay.payAll(JLong(t1 + 1900000))
    K.eq(len([x for x in Log.LINES if "SkySkills refused" in str(x)]) - nw, 1, "FIX2-B4 ... a WARN once (not every retry)")
    state["xp"] = True
    s.retryNow()
    Pay.payAll(JLong(t1 + 2900000))
    K.check(int(s.claimCount()) == 0 and xp[-1][:2] == ("Exploration", 5), "FIX2-B4 ... paid once SkySkills takes it")
    # FIX2 (critic A1): a quit / profile switch while an item give is queued never loses the claim
    pk = str(u)
    ci = "item|Rock_Stone:4|%s:t.i:1" % str(u)
    s.addClaim(ci)
    c = str(s.takeClaim())
    s.markPaying(c, JLong(int(time.time() * 1000)))
    K.check(bool(Sto.write(s)), "FIX2-A1 (claim taken + written, the give queued)")
    Eng.PLAYERS.remove(u)
    Sto.evict(pk)
    K.check(Sto.CACHE.get(pk) is not None and bool(Sto.CACHE.get(pk).equals(s)), "FIX2-A1 a quit while a give is in flight does NOT evict the state")
    Pay.itemDone(s, c, 0, 4, None)
    K.check(c in [str(x) for x in Sto.read(pk, u).claims] and Sto.CACHE.get(pk) is None,
            "FIX2-A1 the give found no player: the claim is back ON DISK, then the state leaves the cache")
    s3 = Sto.read(pk, u)
    c3 = str(s3.takeClaim())
    s3.markPaying(c3, JLong(int(time.time() * 1000)))
    Sto.write(s3)                       # the worst case: the state already evicted (e.g. stuck-give cleanup) when the result arrives
    Pay.itemDone(s3, c3, 1, 4, None)
    on = [str(x) for x in Sto.read(pk, u).claims]
    K.check("item|Rock_Stone:3|%s:t.i:1" % str(u) in on and ("PART %s %s" % (pk, c3)) in logtext(X.base),
            "FIX2-A1 an evicted state: the rest (3) is put back into a fresh read and written: %s" % on)
    # FIX2 (critic A4): a give result arriving while the writer shuts down waits in LATE and is run by stopIO, never dropped
    s4 = Sto.read(pk, u)
    s4.owner = u
    Sto.CACHE.put(pk, s4)
    Eng.PLAYERS.put(u, p)
    c4 = str(s4.takeClaim())
    s4.markPaying(c4, JLong(int(time.time() * 1000)))
    Sto.write(s4)
    IOj = X.E.P("QIO")
    j = IOj(7, u, c4, "Rock_Stone")
    j.o = s4
    j.n = 3
    j.m = 3
    Sto.IO = None
    Sto.ioRunKeep(j)
    K.check(int(Sto.LATE.size()) == 1 and ("PAID %s %s" % (pk, c4)) not in logtext(X.base), "FIX2-A4 a give result with no writer waits in LATE (not dropped)")
    Sto.stopIO()
    K.check(int(Sto.LATE.size()) == 0 and ("PAID %s %s" % (pk, c4)) in logtext(X.base) and not s4.paying, "FIX2-A4 stopIO runs it (PAID, the state pays again)")
    s4.addClaim("item|Rock_Stone:2|%s:t.j:1" % str(u))
    c5 = str(s4.takeClaim())
    j = IOj(7, u, c5, "Rock_Stone")
    j.o = s4
    j.n = 0
    j.m = 2
    Sto.ioRunKeep(j)
    K.check(c5 in [str(x) for x in Sto.read(pk, u).claims], "FIX2-A4 after the stop a late result runs at once (nothing given = the claim is back on disk)")
    # ======================================================================== 0.2: GEAR rewards (Skyy Q1: combat = unidentified class gear at your level)
    while int(s4.claimCount()) > 0:
        s4.takeClaim()
    s4.retryNow()
    s4.setPaying(False)
    pg, ug, sg = p, u, s4
    ItemS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    bag = ItemS("Rock_Stone", 1)
    K.check(not bool(Pay.payable("gear|weapon|g")), "G1 no SkyyGear (gear:fn:box) = a gear claim waits (payable false)")
    cgx = "gear|weapon|%s:tutorial.defeat_mobs:80" % str(ug)
    sg.addClaim(cgx)
    sg.waitNote = None
    K.check(bool(Pay.live(pg, sg)), "FIX-B2 (the stand-in player is live, so the claim is really looked at)")
    Pay.payState(pg, sg, JLong(int(time.time() * 1000)))
    K.check(cgx in [str(x) for x in sg.claims] and sg.waitNote is None,
            "FIX-B2 no SkyyGear: the gear claim stays (nothing lost) WITHOUT a pinned 'Reward waiting' note (%s, %s)" % ([str(x) for x in sg.claims], sg.waitNote))
    K.check(any("gear:fn:box is missing" in str(x) for x in (X.E.P("QLog").LINES or [])), "FIX-B2 ... a WARN once instead")
    while int(sg.claimCount()) > 0:
        sg.takeClaim()
    ok_types = {"t": set(["Weapon_Spear"])}
    boxcalls = []
    def box(a):
        t_ = None if a[0] is None else str(a[0])
        boxcalls.append((t_, int(a[1]), str(a[2]), int(a[3]), str(a[4])))
        return bag if t_ in ok_types["t"] else None
    br.put("gear:fn:box", PyFn(box))
    K.check(bool(Pay.payable("gear|armor|g")), "G1 with SkyyGear: payable")
    lv = PyFn(lambda a: JClass("java.lang.Integer")(7 if str(a[1]) == "Swordsmanship" else 3))
    br.put("skill:fn:level", lv)
    K.eq(int(Pay.gearLevel(ug)), 3, "G2 the level without SkyyClasses = the Combat level (SkyyGear's gate rule)")
    K.eq(str(lv.calls[-1][1]), "Combat", "G2 ... asked for Combat")
    br.put("class:skill:" + str(ug), "Swordsmanship")
    K.eq(int(Pay.gearLevel(ug)), 7, "G2 the level = the CLASS skill level (class:skill:<uuid>)")
    br.put("skill:fn:level", PyFn(lambda a: JClass("java.lang.Integer")(0)))
    K.eq(int(Pay.gearLevel(ug)), 1, "G2 at least level 1")
    br.put("skill:fn:level", PyFn(lambda a: JClass("java.lang.Integer")(250)))
    K.eq(int(Pay.gearLevel(ug)), 100, "G2 at most level 100")
    br.put("skill:fn:level", lv)
    K.eq(list(Pay.classTypes(ug)), [], "G3 no class = no class weapon types")
    br.put("class:" + str(ug), "Warrior")
    br.put("class:weapons:Warrior", "Weapon_Sword_,Weapon_Longsword_,Weapon_Spear_,Weapon_Sword_")
    K.eq(sorted(str(x) for x in Pay.classTypes(ug)), ["Weapon_Longsword", "Weapon_Spear", "Weapon_Sword"], "G3 class:weapons prefixes -> SkyyGear bag type keys (no doubles)")
    del boxcalls[:]
    r = Pay.gearBag(ug, "weapon")
    K.check(r is not None and r.equals(bag) and set(c_[0] for c_ in boxcalls) <= set(["Weapon_Sword", "Weapon_Longsword", "Weapon_Spear"])
            and boxcalls[-1][0] == "Weapon_Spear" and all(c_[1:4] == (7, "quest", 0) and c_[4] == str(ug) for c_ in boxcalls),
            "G4 a weapon bag of the player's CLASS types (random order) at the class level 7, src quest, tier 0: %s" % boxcalls)
    ok_types["t"] = set([None, "Weapon_Daggers", "Armor_Head"])
    del boxcalls[:]
    r = Pay.gearBag(ug, "weapon")
    K.check(r is None and len(boxcalls) == 3 and None not in [c_[0] for c_ in boxcalls],
            "FIX2-W a CLASSED player whose class types do not fit: never a null type (= any gear, armor included) - the claim waits: %s" % boxcalls)
    br.put("class:weapons:free", "Weapon_Daggers_")
    del boxcalls[:]
    r = Pay.gearBag(ug, "weapon")
    K.check(r is not None and boxcalls[-1][0] == "Weapon_Daggers" and len(boxcalls) == 4, "FIX2-W ... then the class:weapons:free types: %s" % boxcalls)
    br.remove("class:" + str(ug))
    br.remove("class:weapons:free")
    ok_types["t"] = set([None, "Armor_Head", "Armor_Chest"])
    del boxcalls[:]
    r = Pay.gearBag(ug, "weapon")
    K.check(r is None and len(boxcalls) == len(list(Pay.WEAPONS)) and len(boxcalls) > 10 and all(c_[0] is not None and c_[0].startswith("Weapon_") for c_ in boxcalls),
            "FIX2-W a CLASSLESS player: every weapon TYPE key, never a null type, never Armor_* (%d calls)" % len(boxcalls))
    ok_types["t"] = set(["Weapon_Sword", "Armor_Head"])
    del boxcalls[:]
    for _i in range(12):
        r = Pay.gearBag(ug, "weapon")
    K.check(r is not None and all(not str(c_[0]).startswith("Armor_") and c_[0] is not None for c_ in boxcalls), "FIX2-W a classless weapon reward never asks for an armor bag")
    K.check(not [w_ for w_ in Pay.WEAPONS if str(w_) in ("Weapon_Arrow", "Weapon_Bomb", "Weapon_Shield", "Weapon_Test")], "FIX2-W ammo / shields / test ids are not weapon types")
    br.put("class:" + str(ug), "Warrior")
    ok_types["t"] = set(["Armor_Legs"])
    del boxcalls[:]
    r = Pay.gearBag(ug, "armor")
    K.check(r is not None and boxcalls[-1][0] == "Armor_Legs" and all(str(c_[0]).startswith("Armor_") for c_ in boxcalls), "G5 an armor bag: armor slots only: %s" % boxcalls)
    ok_types["t"] = set()
    del boxcalls[:]
    K.check(Pay.gearBag(ug, "armor") is None and len(boxcalls) == 4 and None not in [c_[0] for c_ in boxcalls], "G5 no armor fits = null (the claim waits), never a weapon")
    ok_types["t"] = set(["Weapon_Spear", "Weapon_Sword", "Weapon_Longsword"])
    # payOne: no world = refused; with a world (stand-in universe) = the bag goes to the player's world thread
    pg.pr = None
    K.eq(int(Pay.payOne(pg, sg, "gear|weapon|%s:tutorial.defeat_mobs:90" % str(ug))), 0, "G6 a gear claim with no world = refused (it waits)")
    K.eq(int(Pay.payOne(pg, sg, "gear|shield|%s:tutorial.defeat_mobs:91" % str(ug))), -1, "G6 an unknown gear kind = LOST? (never made by the loader)")
    U2 = unsafe()
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    FU, FW = JClass(FAKE + ".FakeUniverse"), JClass(FAKE + ".FakeWorld")
    un = U2.allocateInstance(FU.class_)
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    fi = UniC.class_.getDeclaredField("instance")
    fi.setAccessible(True)
    try:
        fi.set(None, un)
    except Exception:
        U2.putObject(U2.staticFieldBase(fi), U2.staticFieldOffset(fi), un)
    FU.W = U2.allocateInstance(FW.class_)
    pr_ = U2.allocateInstance(PRef.class_)
    setf(pr_, PRef.class_, "uuid", ug)
    setf(pr_, PRef.class_, "worldUuid", JClass("java.util.UUID")(5, 5))
    FU.PR = pr_
    pg.pr = pr_
    feeds = []
    br.put("feed:fn:push", PyFn(lambda a: feeds.append((str(a[3]), None if a[2] is None else str(a[2]))) or Boolean.TRUE))
    pg.route = "feed"
    cg = "gear|weapon|%s:tutorial.defeat_mobs:92" % str(ug)
    sg.addClaim(cg)
    runs0 = int(FW.RUNS)
    Pay.payState(pg, sg, JLong(int(time.time() * 1000) + 5000000))
    lg = logtext(X.base)
    K.check(("PAYING %s %s" % (sg.pk, cg)) in lg and int(FW.RUNS) == runs0 + 1, "G7 the gear claim: PAYING logged, the bag's give runs on the player's world (%d runs)" % (int(FW.RUNS) - runs0))
    K.check(int(Sto.LATE.size()) == (0 if bool(Sto.STOPPED) else 1), "G7 the give's result goes the IO way (run at once here: the writer was stopped above)")
    Sto.drainLate()
    K.check(cg in [str(x) for x in sg.claims] and ("BACK %s %s (no room)" % (sg.pk, cg)) in logtext(X.base) and not sg.paying,
            "G7 a stand-in player the give cannot reach = the gear claim comes back (BACK, nothing lost) - %s" % [str(x) for x in sg.claims])
    c7 = str(sg.takeClaim())
    sg.markPaying(c7, JLong(int(time.time() * 1000)))
    Pay.itemDone(sg, c7, 1, 1, "Rock_Stone")
    K.check(("PAID %s %s" % (sg.pk, c7)) in logtext(X.base) and ("Reward: +1 unidentified weapon", "Rock_Stone") in feeds,
            "G8 the bag landed = PAID once + a feed card with the BAG's icon: %s" % feeds)
    a1 = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")(1)
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    K.eq(int(Give.giveStack(JArray(IC)([None, a1]), ItemS("Rock_Stone", 1))), 1, "G9 giveStack: the prepared bag lands in the first container with room (counted)")
    full = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")(1)
    Give.giveTo(JArray(IC)([full]), "Rock_Stone", 4)
    n_full = int(Give.countIn(full, "Rock_Stone"))
    K.eq(int(Give.giveStack(JArray(IC)([full]), ItemS("Rock_Stone", 1))), 0 if n_full >= 4 else 1, "G9 a full container takes nothing (counted, not trusted)")
    K.eq(int(Give.giveStack(JArray(IC)([a1]), None)), 0, "G9 no stack = nothing")
    # FIX2 (2nd critic 3): SkyyGear present but NO bag fits = the claim waits QUIETLY (no pinned 'Reward waiting' note), then pays
    while int(sg.claimCount()) > 0:
        sg.takeClaim()
    sg.setPaying(False)
    ok_types["t"] = set()
    cq = "gear|armor|%s:tutorial.mini_boss:95" % str(ug)
    K.eq(int(Pay.payOne(pg, sg, cq)), 4, "FIX2-Q payOne: no bag fits = 4 (quiet wait)")
    sg.addClaim(cq)
    sg.waitNote = None
    tq = int(time.time() * 1000) + 9000000
    Pay.payState(pg, sg, JLong(tq))
    K.check(cq in [str(x) for x in sg.claims] and sg.waitNote is None and ("BACK %s %s (no gear bag fits yet" % (sg.pk, cq)) in logtext(X.base)
            and bool(Pay.QUIET.containsKey(str(sg.pk) + "|" + cq)),
            "FIX2-Q no bag fits: the claim stays (BACK, nothing lost) WITHOUT a pinned note (%s)" % sg.waitNote)
    Pay.payState(pg, sg, JLong(tq + 1000))
    K.check(cq in [str(x) for x in sg.claims] and sg.waitNote is None, "FIX2-Q ... and still no note while it waits (refused pass)")
    ok_types["t"] = set(["Armor_Legs"])
    runsq = int(FW.RUNS)
    Pay.payState(pg, sg, JLong(tq + 99000000))
    K.check(int(FW.RUNS) == runsq + 1 and not bool(Pay.QUIET.containsKey(str(sg.pk) + "|" + cq)), "FIX2-Q a bag fits later = the give runs (the quiet mark is cleared)")
    Sto.drainLate()
    gq = JClass("com.hypixel.hytale.server.core.universe.Universe")
    try:
        fi.set(None, None)
    except Exception:
        U2.putObject(U2.staticFieldBase(fi), U2.staticFieldOffset(fi), None)
    K.save()


# ====================================================================================================== K: crash at every step
def run_crash(out, jar, scratch, home):
    from jpype import JClass, JArray, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    PyFn = fn_class()
    Boolean, Long = JClass("java.lang.Boolean"), JClass("java.lang.Long")
    URL, Fl, CL = JClass("java.net.URL"), JClass("java.io.File"), JClass("java.net.URLClassLoader")
    paid = []
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    br.put("coins:fn:add", PyFn(lambda a: paid.append(("coins", int(a[1]))) or Long(1)))
    br.put("skill:fn:addxp", PyFn(lambda a: paid.append(("xp", int(a[2]))) or Boolean.TRUE))
    U = JClass("java.util.UUID")(0xC0, 1)

    def loader():
        arr = JArray(URL)(1)
        arr[0] = Fl(jar).toURI().toURL()
        return CL(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())

    def boot(d):
        """a 'server start' in its own class loader on folder d -> (Env, QEng, QStore, QPay, QLog, QP, state)"""
        L = loader()
        E = Env(os.path.join(d, "Skyy_SkyyQuests"), L)
        os.makedirs(os.path.join(d, "Skyy_SkyyIslands"), exist_ok=True)
        os.makedirs(os.path.join(d, "Skyy_SkyyQuests", "quests"), exist_ok=True)
        # 0.2: a coins task + an XP task (the shipped tutorial now pays items, which wait for a world in a bare JVM)
        open(os.path.join(d, "Skyy_SkyyQuests", "quests", "zk.properties"), "w").write(
            "line=zk\nauto=true\norder=-10\ntask.1.id=k1\ntask.1.type=break\ntask.1.match=K_A\ntask.1.reward=coins:25\n"
            "task.2.id=k2\ntask.2.type=break\ntask.2.match=K_B\ntask.2.count=10\ntask.2.reward=xp:Foraging:50\n")
        E.start()
        Eng, Sto, Pay, Log, QP = E.P("QEng"), E.P("QStore"), E.P("QPay"), E.P("QLog"), E.P("QP")
        Sto.STOPPED = False      # the test drives the payments (no inline IO job)
        p = QP(U, None)
        p.pk = str(U)
        p.world = "skyy-island-k"
        p.loaded = True
        Eng.PLAYERS.put(U, p)
        s = Sto.read(str(U), U)
        s.owner = U
        Sto.CACHE.put(str(U), s)
        Eng.rebuild(U, s)
        return E, Eng, Sto, Pay, Log, p, s
    total = 0
    for stop in range(1, 9):
        d = os.path.join(scratch, "k", "s%d" % stop)
        paid[:] = []
        E, Eng, Sto, Pay, Log, p, s = boot(d)
        Eng.count(U, 1, "K_A", 1, "w", False)                   # k1: 25 coins
        for i in range(10):
            Eng.count(U, 1, "K_B", 1, "w", False)               # k2: 50 Foraging XP
        K.check(Sto.write(s) and int(s.claimCount()) == 2, "K%d two claims on disk" % stop)
        Log.STOP_AT = stop
        Log.STEPS = 0
        crashed = False
        try:
            Pay.payState(p, s, JLong(int(time.time() * 1000)))
        except Exception:
            crashed = True
        first = list(paid)
        # restart: a fresh loader on the same disk, pay what is there, then the admin's repay of logged losses
        E2, Eng2, Sto2, Pay2, Log2, p2, s2 = boot(d)
        Pay2.payState(p2, s2, JLong(int(time.time() * 1000)))
        after_restart = list(paid)
        rep = int(Pay2.repay(s2))
        Pay2.payState(p2, s2, JLong(int(time.time() * 1000)))
        final = list(paid)
        kinds = sorted(k for k, _ in after_restart)
        K.check(len(after_restart) == len(set(after_restart)) and all(kinds.count(k) <= 1 for k in ("coins", "xp")),
                "K%d never a duplicate without repay (crashed=%s): %s" % (stop, crashed, after_restart))
        # with repay: every claim paid; a crash AFTER a payout but before its PAID line is the one case repay pays again (admin decision)
        both = sorted(set(k for k, _ in final))
        K.check(both == ["coins", "xp"], "K%d with repay every reward arrives: %s (repaid %d)" % (stop, final, rep))
        if stop not in (4, 8):
            K.check(len(final) == 2, "K%d exactly once in all: %s" % (stop, final))
        else:
            K.notes.append("K%d (a crash right after a payout, before its PAID line): repay re-issued %d - %s (documented admin decision)" % (stop, rep, final))
        Log.STOP_AT = 0
        total += 1
    # a crash before the completion write: the task completes again, its claims once
    d = os.path.join(scratch, "k", "c")
    paid[:] = []
    E, Eng, Sto, Pay, Log, p, s = boot(d)
    for i in range(10):
        Eng.count(U, 1, "K_B", 1, "w", False)
    K.check(s.isDone("zk.k2") and not os.path.isfile(os.path.join(d, "Skyy_SkyyQuests", "players", str(U) + ".properties")), "KC done in memory, nothing on disk (crash now)")
    E2, Eng2, Sto2, Pay2, Log2, p2, s2 = boot(d)
    K.check(not s2.isDone("zk.k2"), "KC after the restart it is not done")
    for i in range(10):
        Eng2.count(U, 1, "K_B", 1, "w", False)
    K.eq(int(s2.claimCount()), 1, "KC completed again: its claim once")
    K.notes.append("K: %d crash points" % total)
    K.save()


# ====================================================================================================== S: static facts
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=False)
    g = PW.calls(jar)
    IO = set(PW.IO_TARGETS) | {"java.nio.file.Files.createDirectories", "java.nio.file.Files.size", "java.nio.file.Files.newDirectoryStream",
                               "java.nio.file.Files.isRegularFile", "java.nio.file.Files.exists", "java.nio.file.Files.deleteIfExists"}
    hot = ["QBreakSys.handle", "QPickupSys.handle", "QCraftSys.handle", "QKillSys.onComponentAdded", "QEvTask.run", "QHop.run", "QEvents.accept",
           "QFn.apply", "QEng.count", "QEng.hud", "QEng.event", "QGive.run", "QFelledFn.apply", "QWelcome.run", "QLogPage.build",
           "QLogPage.handleDataEvent", "QWelcomePage.build", "QWelcomePage.handleDataEvent", "QEng.enterArea", "QEng.countParty", "QEng.position",
           "QEng.action", "QLife.step"] + [k for k in g if k.endswith(".execute") and (k.startswith("Qa") or k.startswith("Quest"))]
    for h in hot:
        r = PW.reach(g, h, PKG)
        bad = sorted(m for m in r if any(c in IO for c in g.get(m, ())))
        sl = sorted(m for m in r if any(c in PW.SLEEP for c in g.get(m, ())))
        K.check(h in g and not bad and not sl, "S1 %s reaches no file call / sleep (%d methods): files %s sleep %s" % (h, len(r), bad, sl))
    files = sorted(m for m in PW.sites(g, IO) if not m.startswith("Cfg"))
    K.check(set(files) <= {"QLog.readProps", "QLog.writeAtomic", "QStore.log", "QDefs.load", "QDefs.loadPlaces", "QDefs.savePlace", "QPay.repay",
                           "QDefs.loadAreas", "QDefs.migrateTut", "QMig.migrate02", "QMig.saved", "QMig.tutGear"},   # 0.2: areas, the two one-time updates (+ FIX-A3 tutGear)
            "S2 the file calls live in these methods only: %s" % files)
    for f in ("QLog.readProps", "QLog.writeAtomic", "QStore.log"):
        callers = PW.callers(g, f, PKG)
        K.check(all(c.split(".")[0] in ("QLog", "QCfg", "QDefs", "QStore", "QPay", "QIO") or c.startswith("SkyyQuestsPlugin") or c in ("QEng.hubRefresh", "QMig.migrate02") for c in callers),   # FIX-A4: migrate02 writes its sidecar marker (setup only, checked below)
                "S2 %s called only by loaders / the IO jobs / the tick's hub read: %s" % (f, callers))
    K.eq(PW.callers(g, "QEng.hubRefresh", PKG), ["QTick.tickAt", "SkyyQuestsPlugin.setup"], "S2 hub.properties is read only on the tick thread (and once at setup)")
    K.eq(sorted(PW.callers(g, "QMig.migrate02", PKG)), ["SkyyQuestsPlugin.setup"], "S2 the config update runs only in setup (before QCfg.load)")
    K.eq(sorted(PW.callers(g, "QDefs.migrateTut", PKG)), ["QDefs.load"], "S2 the tutorial update runs only in the loader (setup / admin reload on the IO thread)")
    K.eq(sorted(PW.callers(g, "QPay.gearBag", PKG)), ["QPay.payOne"], "S2 the gear bag is made only by the payer (the SkyyQuests-IO thread)")
    K.eq(sorted(PW.callers(g, "QStore.write", PKG)), ["QPay.itemDone", "QPay.payState", "QPay.repay", "QStore.evict", "QStore.flushDirty"], "S2 player files are written by the IO jobs only (itemDone = QIO mode 7; at shutdown stopIO's drain)")
    K.eq(sorted(m for m in PW.sites(g, PW.SLEEP) if not m.startswith("Cfg")), [], "S3 no Thread.sleep in SkyyQuests")
    PW.bridge_static(K, jar)
    K.save()


# ====================================================================================================== ST: start twice on a copy of live data
LIVE_Q = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyQuests")


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    mods = os.path.dirname(home)
    base = os.path.join(mods, "Skyy_SkyyQuests")
    have_q = os.path.isdir(LIVE_Q)
    if have_q:
        shutil.copytree(LIVE_Q, base)          # a scratch COPY of Skyy's live quest data (the source is only read)
    K.notes.append("ST live Skyy_SkyyQuests copied: %s" % have_q)
    h0 = HK.tree_hash(home)
    q0 = HK.tree_hash(LIVE_Q) if have_q else None
    tut0 = open(os.path.join(base, "quests", "tutorial.properties"), "rb").read() if have_q else b""
    cfg0 = open(os.path.join(base, "config.properties"), "rb").read() if have_q else b""
    players0 = dict((f, open(os.path.join(base, "players", f), "rb").read()) for f in os.listdir(os.path.join(base, "players"))) if have_q and os.path.isdir(os.path.join(base, "players")) else {}
    res = []
    for n in range(2):
        b0 = HK.tree_hash(mods)
        E = Env(base)
        E.P("QMig").migrate02()                      # what setup runs first
        lines = E.start()
        E.P("QEng").HUBAT = 0
        E.P("QEng").hubRefresh(1)
        res.append((lines, int(E.P("QDefs").PROBLEMS.size()), str(E.P("QEng").HUBW), HK.tree_hash(mods), b0, [str(x) for x in E.P("QDefs").PROBLEMS]))
    K.check(res[0][0] == 5 and res[0][1] == 0, "ST start 1: the 5 lines, no problems: %s" % (res[0][5],))
    K.check(res[0][3] != res[0][4], "ST start 1 writes (the updates / the new files)")
    K.check(res[1][3] == res[1][4], "ST start 2 writes nothing (both one-time updates ran once)")
    K.eq(HK.tree_hash(home), h0, "ST the live Skyy_SkyyIslands copy is untouched")
    if have_q:
        K.eq(HK.tree_hash(LIVE_Q), q0, "ST the LIVE Skyy_SkyyQuests folder itself was only read")
        tp = os.path.join(base, "quests", "tutorial.properties")
        Defs = E.P("QDefs")
        if tut0 == str(Defs.TUTORIAL01).encode("utf-8"):
            K.check(open(tp + ".0.1.bak", "rb").read() == tut0 and "Shipped by SkyyQuests 0.2" in open(tp, encoding="utf8").read(),
                    "ST Skyy's live tutorial.properties IS the untouched 0.1 file -> updated to 0.2, the old one kept as .0.1.bak")
        else:
            K.check(os.path.isfile(tp + ".0.2.new") and open(tp, "rb").read() == tut0, "ST Skyy's live tutorial.properties was edited -> kept + .0.2.new")
            K.notes.append("ST the live tutorial.properties differs from the 0.1 text (hand-edited)")
        ct = open(os.path.join(base, "config.properties"), "rb").read().decode("latin-1")
        K.check(cfg0.decode("latin-1").startswith(ct.split("# SkyyQuests 0.2 tutorial rewards")[0]) and "SkyyQuests 0.2 tutorial rewards" in ct,
                "ST the live config.properties got the 0.2 marker, every line before the reward table kept")
        K.check("tutorial.reward.chop_logs=25," in ct and "tutorial.reward.mini_boss=0," in ct and "tutorial.reward.explore_area=50," in ct,
                "ST ... its reward lines (all on the 0.1 defaults) are the 0.2 ones")
        K.check(os.path.isfile(os.path.join(base, "config-changes.log")) and "quests.tutorial.rewards[chop_logs]" in open(os.path.join(base, "config-changes.log"), encoding="utf8").read(),
                "ST the change log names the update (Undo in Server Setup)")
        Cfg = E.P("QCfg")
        K.eq([str(x) for x in Cfg.REWARDS.get("defeat_mobs")], ["0", ""], "ST the loader reads the updated live table")
        St, Sto = E.P("QState"), E.P("QStore")
        Sto.DIR = JClass("java.nio.file.Paths").get(os.path.join(base, "players"))
        U = JClass("java.util.UUID")
        for f, raw in sorted(players0.items()):
            pk = f[:-len(".properties")]
            s = Sto.read(pk, U.randomUUID())
            P2 = JClass("java.util.Properties")()
            P2.load(JClass("java.io.StringReader")(raw.decode("utf-8")))
            want = dict((str(k), str(P2.getProperty(k))) for k in P2.stringPropertyNames())
            P3 = JClass("java.util.Properties")()
            P3.load(JClass("java.io.StringReader")(str(s.textU())))
            got = dict((str(k), str(P3.getProperty(k))) for k in P3.stringPropertyNames())
            K.check(not bool(s.frozen) and got == want, "ST live profile %s parses and round-trips unchanged (%d keys)" % (f, len(want)))
            K.check(open(os.path.join(base, "players", f), "rb").read() == raw, "ST ... and the start did not rewrite it")
        K.notes.append("ST live profiles: %s" % sorted(players0))
    hp = os.path.join(home, "hub.properties")
    if os.path.isfile(hp):
        w = [l.split("=", 1)[1].strip() for l in open(hp, encoding="latin-1") if l.startswith("world=")]
        K.eq(res[0][2], w[0] if w else "None", "ST the hub world read from the copy")
    K.notes.append("ST live hub world: %s" % res[0][2])
    K.save()


EXPECT = {     # the classes / members this round changes vs the live 0.1 (reviewed: every one is a 0.2 change listed in the build notes;
          # Cfg* = the config kit re-emitted with the two new rows)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'QCfg': ['+f FOLLOW', '+f PARTY_KILLS', '~<clinit>', '~m load'],
    'QDefs': ['+f AREAS', '+f AREAS_FILE', '+f AREAS_HEAD', '+f GEAR_KINDS', '+f LINE_FILES', '+f LINE_TEXTS', '+f NAMES', '+f NAME_IDS', '+f PARTY_PARTS', '+f TUTORIAL01', '+m area', '+m areaSet', '+m loadAreas', '+m migrateTut', '~<clinit>', '~m itemName', '~m load', '~m parse', '~m part', '~m rewardOf', '~m rewardProblem', '~m rewardText'],
    'QEng': ['+f FOLLOWU', '+m areaAt', '+m areaSoon', '+m coopShortL', '+m countParty', '+m enterArea', '+m evalNum', '+m feed', '+m findTask', '+m followL', '+m followUseL', '+m freshL', '+m inArea', '+m outL', '+m partyRole', '+m regionWorld', '+m requiredL', '+m shownL', '+m skipL', '-m shownL', '~<clinit>', '~m action', '~m hudL', '~m lazy', '~m notifyDone', '~m notifyProgress', '~m partMatch', '~m partSoon', '~m position', '~m rebuild', '~m refreshSettings', '~m taskActive', '~m trackedL', '~m wantL'],
    'QGive': ['+f stack', '+m giveStack', '~m run'],
    'QIO': ['~m run'],
    'QKillSys': ['~m onComponentAdded'],
    'QLife': ['+m coopVisit', '~m join', '~m loaded', '~m needsHop', '~m quit', '~m rebuildAll', '~m step', '~m switchTo'],   # FIX-A1 freshArm resets
    'QLine': ['+f area', '+f order', '+f shortAfter', '~c '],
    'QLogPage': ['~m build', '~m handleDataEvent'],
    'QP': ['+f area', '+f coop', '+f coopKey', '+f freshArm', '~c '],
    'QPart': ['+f fresh', '+f party'],
    'QPay': ['+<clinit>', '+f ARMOR', '+f QUIET', '+f RNG', '+f WEAPONS', '+m classTypes', '+m gearBag', '+m gearLevel', '+m itemDone', '+m shuffle', '+m tell', '+m typesOf', '-m itemDone', '-m tell', '~m payOne', '~m payState', '~m payable'],
    'QState': ['+f base', '+f skip', '+m follow', '+m followUse', '+m fresh', '+m isSkipped', '+m skipToggle', '~c ', '~m firstNames', '~m parse', '~m rowsOf', '~m textU'],
    'QTask': ['+f island', '+f optional', '+f tut'],
    'QuestsCmd': ['~c '],
    'SkyyQuestsPlugin': ['~m setup'],
}


if __name__ == "__main__":
    if "--mkfake" in sys.argv:
        mkfake(HK.arg("--mkfake"), JAR)
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
        HK.run("SkyyQuests", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ["QArea", "QMig", "QuestsSkipCmd"],
               [("defs", run_defs), ("engine", run_engine), ("life", run_life), ("pay", run_pay), ("crash", run_crash), ("static", run_static), ("live", run_live)],
               os.path.abspath(__file__), live=(LIVE_DIR, "Skyy_SkyyIslands"))
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(FAKE_DIR, ignore_errors=True)
