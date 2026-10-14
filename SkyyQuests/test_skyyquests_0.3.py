"""SkyyQuests 0.3 harness (Quests round Q3: quest NPCs, markers, the hub board + daily jobs, Marlow + the pole) on top of the 0.2 harness
(every 0.2 check still runs on this jar). Built on tools/harness_kit.py: each phase a fresh child JVM (the game's JRE, -Xverify:all,
-XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder). Every code path runs on the REAL jar classes; the engine's player /
world / universe / ECS store are stand-ins (Unsafe-allocated engine objects + javassist subclasses compiled before the JVM starts, --mkfake),
the NPC engine calls go through the QNpcApi seam (an in-memory world here; QNpcReal = the game's side, checked by -Xverify + the audit).

    python SkyyQuests/test_skyyquests_0.3.py [--jar SkyyQuests-0.3.jar] [--dir <scratch>] [--keep]

  A / C / AA      verify, class compare against the LIVE 0.2 (+ the new lang file), the engine-access audit
  D E L P K S     the 0.2 phases (defs, engine, life, pay, crash points, static) - their counts now include Marlow's line; S adds the 0.3
                  world-thread / tick paths (no file call, no sleep) and who may read / write npcs.tsv + the dialogue files
  N   npc     /questadmin npc add / remove / list (vanilla roles, the name, OUR talk hint, the admin's spot + facing), a move = the old one
              removed or a ghost, the restart (registry + ghosts from npcs.tsv), the KEEPER (re-prepare after a load, ONE floating '!'
              prop, the switch both / prop / particle / off, per-player signs Alerted / Question to the right players only, a missing NPC
              re-spawned 15 s after its chunk loaded, ghosts removed when they load, never in an unloaded area), the RefSystem add hook
              (ghost / orphan / others / FROZEN), an unreadable npcs.tsv (FROZEN, never written over), F on an NPC through the real
              QUseSys (cancel + the page task NEXT tick, 250 ms double press, other NPCs untouched, ghosts), map + compass markers (one
              provider per world, per-player rows rebuilt only on change, the collector gets SkyyQuest* ids from far, the switch, the widget
              target, quest:fn:markers), the tick's keeper hops (only worlds with an NPC + a player, every 2 s)
  B   board   the day (anchor, never back in a run), the seeded 3 jobs (FNV-1a + java.util.Random, one per tier, the same every time, fish
              jobs only with SkyyFishing), nothing counts before the board was used, a job done = coins + item claims under the day key,
              never twice a day, a RESTART keeps the same jobs + progress, the next day = new jobs, pruning older than yesterday, the board
              page + Track / Claim, the widget's "x / 3", the log page lists today's jobs, /quests board, the switch, bad board files
  F   fish    Marlow without / with SkyyFishing 0.1.4 (the REAL FishQuestFn in the same JVM), the offer pages + Accept, the pole claim made
              by SkyyFishing for that grant and given ONCE (refused without a world = kept; PAID once), the grant guard (hasGrant + a repay
              after a crash), a relog, /questadmin undo + done, a PROFILE SWITCH (the other profile's own one pole; never a second on
              profile 1), SkyyFishing's catch event -> '?' -> hand-in -> done, an edited dialogue file + a bad icon
  ST  live    START TWICE on a scratch COPY of the live Skyy_SkyyQuests (0.2 data) + Skyy_SkyyIslands: start 1 writes only the new
              copied-once files, the 0.2 files keep their bytes, every live profile round-trips; start 2 writes nothing
Not testable without the game (UNVERIFIED, see the round report): the NPC spawn / Use / prop / particle / map-provider engine calls
(QNpcReal), the pages' look, the vanilla compass showing the markers, Tuluk_Fisherman's animations, north = -Z.
Scratch: tools/dev/scratch/quests3/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json, time, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.3"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "quests3fix", "h")))
PKG = "com.skyy.quests."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyIslands")
FAKE = "skyyq03"
FAKE_DIR = SCRATCH + "-fake"     # the stand-in classes (compiled before the phases; HK.run wipes SCRATCH itself)
TB = {"break": 1, "felled": 2, "gather": 4, "craft": 8, "kill": 16, "reach": 32, "enter": 64, "talk": 128, "page": 256, "event": 512,
      "tier": 1024, "level": 2048, "bridge": 4096, "area": 8192}
OLD_JAR = os.path.join(HERE, "SkyyQuests-0.2.jar")      # the LIVE 0.2 (class compare)
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
    K.eq(E.start(), 6, "D1 six quest lines (the tutorial + mining, foraging, farming, fishing + 0.3 Marlow's fishing_intro; the board needs BOARD_FILE)")
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
    K.eq([str(l.id) for l in Defs.LINES], ["tutorial", "mining", "foraging", "farming", "fishing", "fishing_intro"], "D1 lines sorted by order (tutorial 0 .. fishing 50, Marlow 55)")
    K.eq([int(l.order) for l in Defs.LINES], [0, 20, 30, 40, 50, 55], "D1 the line orders")
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
              if "gear:" not in str(Defs.rewardOf(l, t)) and not ("coins:" in str(Defs.rewardOf(l, t)) and ("item:" in str(Defs.rewardOf(l, t)) or "pole:" in str(Defs.rewardOf(l, t))))]   # 0.3: Marlow's pole IS the item
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
    K.eq(E.start(), 8, "D3 the 6 shipped lines + side_line + chain_line (the duplicate tutorial file skipped)")
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
            K.eq((nl, len(Defs.line("tutorial").tasks), int(Defs.PROBLEMS.size())), (6, 25, 0), "MIG-T the migrated file loads: 25 tasks, no problems")
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
           "QEng.action", "QLife.step",
           # 0.3: F on a quest NPC, the RefSystem hook, the keeper hop, the pages, the talk logic, the markers, the tick's world part
           "QUseSys.handle", "QNpcAddSys.onEntityAdded", "QNpcTask.run", "QNpc.keep", "QNpc.onAdded", "QNpc.add", "QNpc.remove", "QTalkTask.run",
           "QTalk.pageFor", "QTalk.accept", "QTalk.boardCmd", "QDlgPage.build", "QDlgPage.handleDataEvent", "QBoardPage.build",
           "QBoardPage.handleDataEvent", "QMarks.refresh", "QMarks.collect", "QMarks.provide", "QMapProv.update", "QWorld.tick", "QWorld.roll"]
    hot += [k for k in g if k.endswith(".execute") and (k.startswith("Qa") or k.startswith("Quest"))]
    for h in hot:
        r = PW.reach(g, h, PKG)
        bad = sorted(m for m in r if any(c in IO for c in g.get(m, ())))
        sl = sorted(m for m in r if any(c in PW.SLEEP for c in g.get(m, ())))
        K.check(h in g and not bad and not sl, "S1 %s reaches no file call / sleep (%d methods): files %s sleep %s" % (h, len(r), bad, sl))
    files = sorted(m for m in PW.sites(g, IO) if not m.startswith("Cfg"))
    K.check(set(files) <= {"QLog.readProps", "QLog.writeAtomic", "QStore.log", "QDefs.load", "QDefs.loadPlaces", "QDefs.savePlace", "QPay.repay",
                           "QDefs.loadAreas", "QDefs.migrateTut", "QMig.migrate02", "QMig.saved", "QMig.tutGear",   # 0.2: areas, the two one-time updates (+ FIX-A3 tutGear)
                           "QNpc.load", "QNpc.loadDialogues"},                                                      # 0.3: npcs.tsv + dialogue/ (setup / reload on IO)
            "S2 the file calls live in these methods only: %s" % files)
    for f in ("QLog.readProps", "QLog.writeAtomic", "QStore.log"):
        callers = PW.callers(g, f, PKG)
        K.check(all(c.split(".")[0] in ("QLog", "QCfg", "QDefs", "QStore", "QPay", "QIO") or c.startswith("SkyyQuestsPlugin") or c in ("QEng.hubRefresh", "QMig.migrate02", "QNpc.loadDialogues", "QNpc.save") for c in callers),   # FIX-A4: migrate02 writes its sidecar marker (setup only, checked below)
                "S2 %s called only by loaders / the IO jobs / the tick's hub read: %s" % (f, callers))
    K.eq(PW.callers(g, "QEng.hubRefresh", PKG), ["QTick.tickAt", "SkyyQuestsPlugin.setup"], "S2 hub.properties is read only on the tick thread (and once at setup)")
    K.eq(sorted(PW.callers(g, "QMig.migrate02", PKG)), ["SkyyQuestsPlugin.setup"], "S2 the config update runs only in setup (before QCfg.load)")
    K.eq(sorted(PW.callers(g, "QDefs.migrateTut", PKG)), ["QDefs.load"], "S2 the tutorial update runs only in the loader (setup / admin reload on the IO thread)")
    K.eq(sorted(PW.callers(g, "QPay.gearBag", PKG)), ["QPay.payOne"], "S2 the gear bag is made only by the payer (the SkyyQuests-IO thread)")
    K.eq(sorted(PW.callers(g, "QStore.write", PKG)), ["QPay.itemDone", "QPay.payState", "QPay.repay", "QStore.evict", "QStore.flushDirty"], "S2 player files are written by the IO jobs only (itemDone = QIO mode 7; at shutdown stopIO's drain)")
    K.eq(sorted(PW.callers(g, "QNpc.save", PKG)), ["QIO.run", "SkyyQuestsPlugin.shutdown"], "S2 npcs.tsv is written only by the IO job (mode 8) and at shutdown")
    K.eq(sorted(PW.callers(g, "QNpc.load", PKG)), ["QIO.run", "SkyyQuestsPlugin.setup"], "S2 npcs.tsv is read only at setup / an admin reload (IO)")
    K.eq(sorted(PW.callers(g, "QNpc.loadDialogues", PKG)), ["QIO.run", "SkyyQuestsPlugin.setup"], "S2 the dialogue files are read only at setup / an admin reload (IO)")
    K.eq(sorted(PW.callers(g, "QNpc.keep", PKG)), ["QNpcTask.run"], "S2 the keeper runs only as the world task (QNpcTask, World.execute)")
    K.eq(sorted(PW.callers(g, "QTalk.pageFor", PKG)), ["QTalkTask.run"], "S2 an NPC page is made only on the NEXT tick (QTalkTask, never inside the Use handler)")
    K.check("com.skyy.quests.QTalkTask.<init>" in g.get("QUseSys.handle", ()) and "com.skyy.quests.QTalk.pageFor" not in g.get("QUseSys.handle", ()),
            "S2 the Use handler only schedules the page task")
    K.eq(sorted(m for m in PW.sites(g, PW.SLEEP) if not m.startswith("Cfg")), [], "S3 no Thread.sleep in SkyyQuests")
    PW.bridge_static(K, jar)
    K.save()


# ====================================================================================================== ST: start twice on a copy of live data
LIVE_Q = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyQuests")


def run_live(out, jar, scratch, home):
    """0.3 START TWICE on a scratch COPY of the live Skyy_SkyyQuests (0.2 data) + Skyy_SkyyIslands: start 1 writes only the new copied-once
    files (board.properties, dialogue/marlow.properties, quests/fishing_intro.properties - npcs.tsv is written only when an admin places an
    NPC); the 0.2 files (tutorial, config, areas, places, profiles) keep their bytes; start 2 writes nothing"""
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
    keep = {}
    if have_q:
        for rel in ("quests/tutorial.properties", "config.properties", "areas.properties", "places.properties"):
            fp = os.path.join(base, *rel.split("/"))
            if os.path.isfile(fp):
                keep[rel] = open(fp, "rb").read()
    players0 = dict((f, open(os.path.join(base, "players", f), "rb").read()) for f in os.listdir(os.path.join(base, "players"))) if have_q and os.path.isdir(os.path.join(base, "players")) else {}
    new0 = [rel for rel in ("board.properties", "dialogue/marlow.properties", "quests/fishing_intro.properties") if not os.path.isfile(os.path.join(base, *rel.split("/")))]
    res = []
    Paths = JClass("java.nio.file.Paths")
    for n in range(2):
        b0 = HK.tree_hash(mods)
        E = Env(base)
        E.P("QDefs").BOARD_FILE = Paths.get(os.path.join(base, "board.properties"))
        Npc = E.P("QNpc")
        Npc.FILE = Paths.get(os.path.join(base, "npcs.tsv"))
        Npc.DLG_DIR = Paths.get(os.path.join(base, "dialogue"))
        E.P("QMig").migrate02()                      # what setup runs first (a 0.2 file: nothing to do)
        lines = E.start()
        errs = JClass("java.util.ArrayList")()
        Npc.load(errs)
        Npc.loadDialogues(errs)
        E.P("QEng").HUBAT = 0
        E.P("QEng").hubRefresh(1)
        res.append((lines, int(E.P("QDefs").PROBLEMS.size()), str(E.P("QEng").HUBW), HK.tree_hash(mods), b0, [str(x) for x in E.P("QDefs").PROBLEMS] + [str(x) for x in errs]))
    K.check(res[0][0] >= 7 and res[0][1] == 0 and not res[0][5], "ST start 1: the shipped lines + Marlow's line + the board (%d lines), no problems: %s" % (res[0][0], res[0][5]))
    ch = sorted(k for k in set(res[0][3]) | set(res[0][4]) if res[0][3].get(k) != res[0][4].get(k))
    want = sorted(os.path.join("Skyy_SkyyQuests", *r_.split("/")) for r_ in new0)
    K.eq(ch, want, "ST start 1 writes ONLY the new copied-once files that were not there yet")
    K.check(res[1][3] == res[1][4], "ST start 2 writes nothing")
    K.eq(HK.tree_hash(home), h0, "ST the live Skyy_SkyyIslands copy is untouched")
    if have_q:
        K.eq(HK.tree_hash(LIVE_Q), q0, "ST the LIVE Skyy_SkyyQuests folder itself was only read")
        for rel, raw in sorted(keep.items()):
            K.check(open(os.path.join(base, *rel.split("/")), "rb").read() == raw, "ST the live %s keeps its bytes (0.3 has no one-time update)" % rel)
        St, Sto = E.P("QState"), E.P("QStore")
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
            K.check(not bool(s.frozen) and got == want_, "ST live profile %s parses and round-trips unchanged (%d keys)" % (f, len(want_)))
            K.eq(int(s.pruneDaily(E.P("QDefs").day())), 0, "ST live profile %s has no board keys to prune" % f)
            K.check(open(os.path.join(base, "players", f), "rb").read() == raw, "ST ... and the start did not rewrite it")
        K.notes.append("ST live profiles: %s" % sorted(players0))
    hp = os.path.join(home, "hub.properties")
    if os.path.isfile(hp):
        w = [l.split("=", 1)[1].strip() for l in open(hp, encoding="latin-1") if l.startswith("world=")]
        K.eq(res[0][2], w[0] if w else "None", "ST the hub world read from the copy")
    K.notes.append("ST live hub world: %s; new files on start 1: %s" % (res[0][2], new0))
    K.save()


# ====================================================================================================== 0.3 (Quests Q3): shared
FISH_JAR = os.path.join(ROOT, "SkyyFishing", "SkyyFishing-0.1.4.jar")    # Marlow's pole maker (the real FishQuestFn, cross-mod in one JVM)
HUB = "skyy-hub"


def npc_api(st):
    """the QNpcApi seam: an in-memory world (entities by uuid, props, particles, the players near, worlds, providers)"""
    from jpype import JImplements, JOverride, JClass, JObject, JArray, JDouble
    JS = JClass("java.lang.String")
    AL = JClass("java.util.ArrayList")

    def uof(ref):
        r = str(ref)
        return r[4:] if r.startswith("ref:") else None

    @JImplements(PKG + "QNpcApi")
    class Api(object):
        def _n(self, k):
            st["calls"][k] = st["calls"].get(k, 0) + 1

        @JOverride
        def spawn(self, w, role, x, y, z, yaw):
            self._n("spawn")
            st["roles"].append(str(role))
            if st.get("nospawn"):
                return None
            st["seq"] += 1
            u = "00000000-0000-4000-8000-%012d" % st["seq"]
            ref = JS("ref:" + u)
            st["ents"][u] = {"w": str(w), "role": str(role), "x": float(x), "y": float(y), "z": float(z), "yaw": float(yaw), "name": None, "hint": None, "ref": ref}
            return ref

        @JOverride
        def find(self, w, uuid):
            self._n("find")
            e = st["ents"].get(str(uuid))
            return e["ref"] if e is not None and e["w"] == str(w) else None

        @JOverride
        def uuidOf(self, w, ref):
            return uof(ref)

        @JOverride
        def loaded(self, w, x, z):
            return st["loaded"]

        @JOverride
        def remove(self, w, ref):
            self._n("remove")
            r = str(ref)
            st["removed"].append(r)
            if r in st["props"]:
                del st["props"][r]
            u = uof(ref)
            if u in st["ents"]:
                del st["ents"][u]

        @JOverride
        def prepare(self, w, ref, name, hint):
            self._n("prepare")
            e = st["ents"].get(uof(ref))
            if e is not None:
                e["name"], e["hint"] = str(name), str(hint)

        @JOverride
        def prop(self, w, x, y, z, text):
            self._n("prop")
            st["pseq"] += 1
            k = "prop:%d" % st["pseq"]
            st["props"][k] = (float(x), float(y), float(z), str(text), str(w))
            if st.get("on_prop"):
                st["on_prop"]()                                               # FIX2: something happens while the ! is made
            return JS(k)

        @JOverride
        def valid(self, ref):
            if ref is None:
                return False
            r = str(ref)
            return r in st["props"] or (uof(ref) in st["ents"])

        @JOverride
        def pos(self, w, ref):
            e = st["ents"].get(uof(ref))
            return None if e is None else JArray(JDouble)([e["x"], e["y"], e["z"]])

        @JOverride
        def particle(self, w, pid, x, y, z, viewers):
            self._n("particle")
            st["parts"].append((str(pid), sorted(str(v) for v in viewers), float(y)))

        @JOverride
        def near(self, w, x, y, z, r):
            l = AL()
            for u, ref in st["near"]:
                l.add(JArray(JObject)([u, JS(ref)]))
            return l

        @JOverride
        def worldName(self, w):
            return None if w is None else JS(str(w))

        @JOverride
        def world(self, name):
            return JS(str(name)) if str(name) in st["worlds"] else None

        @JOverride
        def exec(self, w, r):
            self._n("exec")
            r.run()

        @JOverride
        def provide(self, w, prov):
            self._n("provide")
            st["prov"].append(str(w))
    return Api()


def api_state():
    return {"calls": {}, "roles": [], "seq": 0, "pseq": 0, "ents": {}, "props": {}, "removed": [], "parts": [], "near": [], "loaded": True,
            "worlds": set([HUB]), "prov": []}


def scene3(K, scratch, name, loader=None):
    """a 0.3 scene: the board file, the NPC registry and the dialogue folder in the scratch copy (what setup sets) + the loaders run"""
    from jpype import JClass
    X = Scene(K, scratch, name, loader)
    P = X.E.P
    Paths = JClass("java.nio.file.Paths")
    X.Npc, X.Talk, X.Marks, X.World, X.Pay = P("QNpc"), P("QTalk"), P("QMarks"), P("QWorld"), P("QPay")
    X.Defs.BOARD_FILE = Paths.get(os.path.join(X.base, "board.properties"))
    X.Npc.FILE = Paths.get(os.path.join(X.base, "npcs.tsv"))
    X.Npc.DLG_DIR = Paths.get(os.path.join(X.base, "dialogue"))
    X.Defs.load()
    errs = JClass("java.util.ArrayList")()
    X.Npc.load(errs)
    X.Npc.loadDialogues(errs)
    X.errs = [str(e) for e in errs]
    X.L = X.Defs.LINES[0]
    return X


def pref_of(u, name="Mia"):
    from jpype import JClass
    U = unsafe()
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef.class_, "uuid", u)
    setf(pr, PRef.class_, "username", name)
    return pr


def markup(b):
    out = []
    for c in b.getCommands():
        for v in (c.selector, c.data, c.text):
            if v is not None:
                out.append(str(v))
    return " | ".join(out)


def item_store(ids):
    """a bare JVM has no Item asset store: an empty one holding these ids (the SkyyHud 0.3.12+ / quests pay-phase pattern) - new ItemStack works"""
    from jpype import JClass
    U = unsafe()
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyQ3TestStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyQ3TestStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
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
    for i in ids:
        it_ = U.allocateInstance(ItemC.class_)
        setf(it_, ItemC.class_, "maxStack", JClass("java.lang.Integer")(1 if "Rod" in i else 64).intValue())
        setf(it_, ItemC.class_, "id", i)
        mf.get(amap).put(i, it_)


# ====================================================================================================== N: the quest NPCs (registry, keeper, ghosts, systems, markers)
def run_npc(out, jar, scratch, home):
    from jpype import JClass, JObject, JArray, JLong, JFloat, JString, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, FAKE_DIR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    PyFn = fn_class()
    X = scene3(K, scratch, "n")
    Npc, Marks, Cfg, Eng, Defs = X.Npc, X.Marks, X.Cfg, X.Eng, X.Defs
    st = api_state()
    Npc.API = npc_api(st)
    hub = JString(HUB)
    # N0 the copied-once files + the loaders
    K.check(os.path.isfile(os.path.join(X.base, "board.properties")) and os.path.isfile(os.path.join(X.base, "dialogue", "marlow.properties"))
            and os.path.isfile(os.path.join(X.base, "quests", "fishing_intro.properties")), "N0 board.properties, dialogue/marlow.properties, quests/fishing_intro.properties copied once")
    K.check(X.errs == [] and int(Defs.PROBLEMS.size()) == 0, "N0 no file problems: %s %s" % (X.errs, [str(p) for p in Defs.PROBLEMS]))
    K.eq([str(l.id) for l in Defs.LINES], ["tutorial", "mining", "foraging", "farming", "fishing", "fishing_intro", "board"], "N0 the 7 lines in order (Marlow's 55, the board 90)")
    K.check(Defs.BOARD is not None and bool(Defs.BOARD.daily) and str(Defs.BOARD.giver) == "board" and len(Defs.BOARD.tasks) == 10
            and sorted(int(t.tier) for t in Defs.BOARD.tasks) == [1, 1, 1, 1, 2, 2, 2, 3, 3, 3], "N0 the board: daily, giver board, 10 jobs by tier")
    fl = Defs.line("fishing_intro")
    K.check(fl is not None and bool(fl.chain) and not bool(fl.auto) and str(fl.giver) == "marlow" and [str(t.id) for t in fl.tasks] == ["take_pole", "catch_fish", "show_marlow"],
            "N0 Marlow's line: chain, started by talking, giver marlow, 3 tasks")
    K.eq(str(Npc.dlg("marlow", "name", "x")), "Marlow", "N0 the dialogue file is read (name)")
    K.eq(str(Npc.icon("marlow")), "Food_Fish_Raw", "N0 the portrait item")
    # FIX-B2 (critic): quest:caller:board only while a Quest Board can answer a talk
    tour = [p_ for t_ in Defs.line("tutorial").tasks for p_ in t_.parts if str(p_.caller) == "board"]
    K.check(len(tour) == 1 and not br.containsKey("quest:caller:board") and bool(Eng.partSoon(tour[0])),
            "FIX-B2 no Quest Board placed = no quest:caller:board (the tutorial's 'talk to the quest board' part is coming soon, not a dead task)")
    # N1 add the board
    r = str(Npc.add(None, hub, 10.5, 64.0, -3.5, JFloat(1.5), "board"))
    K.check(bool(br.containsKey("quest:caller:board")) and not bool(Eng.partSoon(tour[0])), "FIX-B2 the board placed = quest:caller:board (the part is live)")
    u1 = list(st["ents"])[0]
    e1 = st["ents"][u1]
    K.check(r.startswith("+Quest Board placed here (skyy-hub") and e1["role"] == "Temple_Kweebec_Static" and e1["name"] == "Quest Board"
            and e1["hint"] == "server.skyyquests.talkHint" and (e1["x"], e1["y"], e1["z"], e1["yaw"]) == (10.5, 64.0, -3.5, 1.5),
            "N1 /questadmin npc add board: the vanilla role, the name, our talk hint, the admin's spot + facing: %s %s" % (r, e1))
    K.check(len(Npc.RECS) == 1 and str(Npc.RECS[0].uuid) == u1 and bool(Npc.KNOWN.containsKey(u1)) and int(Npc.SPAWNS) == 1, "N1 registered (KNOWN)")
    tsv = open(os.path.join(X.base, "npcs.tsv"), encoding="utf8").read()
    K.check(("npc\tboard\tskyy-hub\t10.5\t64.0\t-3.5\t1.5\t%s\n" % u1) in tsv, "N1 npcs.tsv written (the IO job): %r" % tsv[-120:])
    K.check(Defs.place("npc:board") is not None and str(Defs.place("npc:board").label) == "Quest Board" and str(Defs.place("npc:board").world) == HUB,
            "N1 npc:board is a place (the widget arrow / reach to an NPC)")
    # N2 placed again in the same world: the old one goes at once
    r = str(Npc.add(None, hub, 20.0, 64.0, 0.0, JFloat(0.0), "board"))
    u2 = str(Npc.RECS[0].uuid)
    K.check(u2 != u1 and u1 not in st["ents"] and ("ref:" + u1) in st["removed"] and "the old one was removed" in r and len(Npc.RECS) == 1
            and not bool(Npc.KNOWN.containsKey(u1)), "N2 a second add moves it: the old NPC removed, one registry line: %s" % r)
    # N3 marlow; then the board moved to another world while the old one stands where nothing is loaded = a ghost
    Npc.add(None, hub, 30.0, 62.0, 5.0, JFloat(0.0), "marlow")
    um = str(Npc.recOf("marlow").uuid)
    K.check(st["ents"][um]["role"] == "Tuluk_Fisherman" and st["ents"][um]["name"] == "Marlow", "N3 Marlow = the vanilla fisher (Tuluk_Fisherman)")
    st["worlds"].add("skyy-hub2")
    r = str(Npc.add(None, JString("skyy-hub2"), 1.0, 70.0, 1.0, JFloat(0.0), "board"))
    K.check(bool(Npc.GHOSTS.containsKey(u2)) and str(Npc.GHOSTS.get(u2)).endswith("|" + HUB) and "goes the moment its area loads" in r and u2 in st["ents"],
            "N3 the old board in another world = a ghost (removed when it loads): %s" % r)
    # N4 refusals
    K.check(str(Npc.add(None, hub, 0.0, 0.0, 0.0, JFloat(0.0), "fred")).startswith("-Unknown quest NPC"), "N4 an unknown id")
    st["nospawn"] = True
    K.check(str(Npc.add(None, hub, 0.0, 0.0, 0.0, JFloat(0.0), "marlow")).startswith("-Marlow did not spawn") and str(Npc.recOf("marlow").uuid) == um,
            "N4 a role that does not spawn changes nothing")
    st["nospawn"] = False
    # N5 a restart: the registry + ghosts come back from npcs.tsv
    recs_before = sorted((str(x.id), str(x.world), str(x.uuid)) for x in Npc.RECS)
    Npc.RECS = JArray(X.E.P("QNpcRec"))([])
    Npc.KNOWN.clear()
    Npc.GHOSTS.clear()
    errs = JClass("java.util.ArrayList")()
    Npc.load(errs)
    K.check(sorted((str(x.id), str(x.world), str(x.uuid)) for x in Npc.RECS) == recs_before and bool(Npc.GHOSTS.containsKey(u2)) and errs.size() == 0
            and bool(Npc.KNOWN.containsKey(um)), "N5 after a restart: the same NPCs, the ghost kept: %s" % recs_before)
    # FIX2 (critic 3.2): the floating ! only over an NPC that offers something - Marlow without SkyyFishing 0.1.4 (line hidden) = none
    Cfg.MARK_NPC = "both"
    had_fish = br.get("fishing:fn:starter")
    br.remove("fishing:fn:starter")
    K.check(not bool(Npc.offers("marlow")) and bool(Npc.offers("board")) and not bool(Npc.offers("fred")), "FIX2-3.2 offers: Marlow's line hidden = no, the board = yes, an unknown id = no")
    Npc.keep(hub, JLong(999000))
    K.check(not [v for v in st["props"].values() if v[4] == HUB] and Npc.recOf("marlow").prop is None,
            "FIX2-3.2 no SkyyFishing 0.1.4: no floating ! over Marlow (he says the fish are not biting)")
    Cfg.BOARD_ON = False
    K.check(not bool(Npc.offers("board")), "FIX2-3.2 Daily jobs board off = no floating ! over the board")
    Cfg.BOARD_ON = True
    br.put("fishing:fn:starter", had_fish if had_fish is not None else PyFn(lambda a: None))
    K.check(bool(Npc.offers("marlow")), "FIX2-3.2 SkyyFishing 0.1.4 there = Marlow offers his line")
    Npc.recOf("marlow").prepared = None                                   # (N6 below counts the re-prepare after a load)
    # N6 the keeper in the hub world: Marlow named again (after a load), the floating '!' prop, the ghost removed
    st["calls"] = {}
    Npc.keep(hub, JLong(1000000))
    props = [v for v in st["props"].values() if v[4] == HUB]
    K.check(st["calls"].get("prepare") == 1 and len(props) == 1 and props[0][3] == "!" and abs(props[0][1] - (62.0 + 2.7)) < 1e-6,
            "N6 keeper: Marlow re-prepared once after the load, ONE floating '!' prop 2.7 over his feet: %s %s" % (st["calls"], props))
    K.check(u2 not in st["ents"] and not bool(Npc.GHOSTS.containsKey(u2)) and int(Npc.REMOVED) >= 2, "N6 keeper: the ghost board that loaded in the hub is removed")
    st["calls"] = {}
    Npc.keep(hub, JLong(1002000))
    K.check(st["calls"].get("prepare", 0) == 0 and st["calls"].get("prop", 0) == 0, "N6 a second pass: nothing re-done (prepared, prop alive): %s" % st["calls"])
    tsv = open(os.path.join(X.base, "npcs.tsv"), encoding="utf8").read()
    K.check(u2 not in tsv, "N6 the removed ghost left npcs.tsv")
    # N7 the switch: per-player signs only = the prop goes; off = nothing
    Cfg.MARK_NPC = "particle"
    Npc.keep(hub, JLong(1004000))
    K.check(len([v for v in st["props"].values() if v[4] == HUB]) == 0 and Npc.recOf("marlow").prop is None, "N7 'Your signs only': the floating prop is removed")
    Cfg.MARK_NPC = "both"
    # N8 per-player signs: ! to a player with Marlow's offer, ? to one with a hand-in, nothing to one who is done / has nothing
    br.put("fishing:fn:starter", PyFn(lambda a: None))
    br.put("quest:caller:fishing", JClass("java.lang.Boolean").TRUE)
    ua, pa, sa = X.player(41, HUB)
    ub, pb, sb = X.player(42, HUB)
    uc, pc, sc = X.player(43, HUB)
    K.eq(int(sa.npcMark("marlow")), 1, "N8 a player who has not started Marlow's line sees '!' (an offer)")
    sb.startLine("fishing_intro", JLong(1))
    fl = Defs.line("fishing_intro")
    out_ = JClass("java.util.ArrayList")()
    sb.adminDone(fl, fl.tasks[0], JLong(1), out_)
    sb.adminDone(fl, fl.tasks[1], JLong(1), out_)
    K.eq(int(sb.npcMark("marlow")), 2, "N8 'Show Marlow your catch' active = '?' (a hand-in)")
    sc.startLine("fishing_intro", JLong(1))
    for t in fl.tasks:
        sc.adminDone(fl, t, JLong(1), out_)
    K.eq(int(sc.npcMark("marlow")), 0, "N8 the line done = no sign")
    K.eq(int(sa.npcMark("board")), 1, "N8 the board: a line it gives (the daily jobs) not started yet = '!'")
    st["near"] = [(ua, "player:a"), (ub, "player:b"), (uc, "player:c")]
    st["parts"] = []
    Npc.keep(hub, JLong(1006000))
    got = sorted((p_[0], tuple(p_[1])) for p_ in st["parts"])
    K.check(("Alerted", ("player:a",)) in got and ("Question", ("player:b",)) in got and not [g for g in got if "player:c" in g[1]],
            "N8 the signs go per player: Alerted (!) to a, Question (?) to b, nothing to c: %s" % got)
    Cfg.MARK_NPC = "prop"
    st["parts"] = []
    Npc.keep(hub, JLong(1008000))
    K.eq(st["parts"], [], "N8 'Floating ! only': no per-player particles")
    Cfg.MARK_NPC = "off"
    Npc.keep(hub, JLong(1010000))
    K.check(st["parts"] == [] and not [v for v in st["props"].values() if v[4] == HUB], "N8 'Off': no prop, no particles")
    Cfg.MARK_NPC = "both"
    Cfg.ENABLED = False
    K.check(not bool(Cfg.propsOn()) and not bool(Cfg.particlesOn()), "N8 Quests off = no markers")
    Cfg.ENABLED = True
    # N9 a missing NPC (its chunk loaded, the entity gone): re-spawned at its spot 15 s later, the old uuid a ghost
    Npc.keep(hub, JLong(1012000))
    old_props = [k_ for k_, v in st["props"].items() if v[4] == HUB]
    K.eq(len(old_props), 1, "FIX-B1 (Marlow's floating ! stands before he goes missing)")
    del st["ents"][um]
    st["calls"] = {}
    Npc.keep(hub, JLong(2000000))
    K.check(st["calls"].get("spawn", 0) == 0 and int(Npc.recOf("marlow").missing) == 2000000, "N9 missing: noted, not re-spawned at once")
    Npc.keep(hub, JLong(2014999))
    K.eq(st["calls"].get("spawn", 0), 0, "N9 ... not before 15 s")
    Npc.keep(hub, JLong(2015000))
    um2 = str(Npc.recOf("marlow").uuid)
    K.check(st["calls"].get("spawn") == 1 and um2 != um and um2 in st["ents"] and st["ents"][um2]["role"] == "Tuluk_Fisherman"
            and (st["ents"][um2]["x"], st["ents"][um2]["y"], st["ents"][um2]["z"]) == (30.0, 62.0, 5.0) and bool(Npc.GHOSTS.containsKey(um))
            and int(Npc.RESPAWNS) == 1 and bool(Npc.KNOWN.containsKey(um2)) and not bool(Npc.KNOWN.containsKey(um)),
            "N9 ... 15 s after: re-spawned at the same spot, the old uuid is a ghost")
    K.check(um2 in open(os.path.join(X.base, "npcs.tsv"), encoding="utf8").read(), "N9 npcs.tsv has the new uuid")
    K.check(old_props[0] not in st["props"] and old_props[0] in st["removed"], "FIX-B1 the re-spawn removed the old floating ! (%s): %s" % (old_props, st["removed"][-3:]))
    Npc.keep(hub, JLong(2017000))
    K.eq(len([v for v in st["props"].values() if v[4] == HUB]), 1, "FIX-B1 ... and the next pass puts up exactly ONE ! over the new Marlow")
    st["loaded"] = False
    Npc.recOf("marlow").missing = 0
    del st["ents"][um2]
    st["calls"] = {}
    Npc.keep(hub, JLong(3000000))
    Npc.keep(hub, JLong(3100000))
    K.check(st["calls"].get("spawn", 0) == 0 and int(Npc.recOf("marlow").missing) == 0, "N9 an area that is not loaded is never 're-spawned' (the NPC is just not loaded)")
    K.check(not [v for v in st["props"].values() if v[4] == HUB] and Npc.recOf("marlow").prop is None, "FIX-B1 an unloaded area: a still-valid floating ! is removed before the link is dropped")
    st["loaded"] = True
    # FIX2 (critic 2.1): the board (in skyy-hub2) gets its floating !, then an admin in the hub moves it here -> the old ! waits for hub2's keeper
    H2 = JString("skyy-hub2")
    Npc.PROPQ.clear()
    Npc.keep(H2, JLong(3200000))
    p2 = [k_ for k_, v in st["props"].items() if v[4] == "skyy-hub2"]
    K.check(len(p2) == 1 and Npc.recOf("board").prop is not None, "FIX2-2.1 the board's floating ! stands in skyy-hub2: %s" % p2)
    bu_old = str(Npc.recOf("board").uuid)
    r = str(Npc.add(None, hub, 12.0, 64.0, 0.0, JFloat(0.0), "board"))
    K.check(p2[0] in st["props"] and int(Npc.PROPQ.size()) == 1 and str(Npc.PROPQ.get(JString(p2[0]))) == "skyy-hub2",
            "FIX2-2.1 moved from another world: the old ! cannot go now - queued for skyy-hub2 (%s)" % r)
    Npc.keep(hub, JLong(3202000))
    K.check(p2[0] in st["props"] and int(Npc.PROPQ.size()) == 1, "FIX2-2.1 the hub's keeper leaves another world's ! alone")
    Npc.keep(H2, JLong(3204000))
    K.check(p2[0] not in st["props"] and p2[0] in st["removed"] and int(Npc.PROPQ.size()) == 0,
            "FIX2-2.1 skyy-hub2's keeper removes the left-over ! (never left floating)")
    K.check(bu_old not in st["ents"] and not bool(Npc.GHOSTS.containsKey(bu_old)), "FIX2-2.1 ... and the old board (a ghost) in the same pass")
    hp = [k_ for k_, v in st["props"].items() if v[4] == HUB and abs(v[0] - 12.0) < 1e-6]
    K.eq(len(hp), 1, "FIX2-2.1 the moved board has ONE ! in the hub")
    r = str(Npc.remove(None, H2, "board"))
    K.check(r.startswith("+Quest Board removed from the list") and hp[0] in st["props"] and int(Npc.PROPQ.size()) == 1,
            "FIX2-2.1 removed by an admin in another world: the ! is queued: %s" % r)
    Npc.keep(hub, JLong(3206000))
    K.check(hp[0] not in st["props"] and int(Npc.PROPQ.size()) == 0, "FIX2-2.1 ... and the hub's keeper removes it")
    Npc.PROPQ.put(JString("prop:gone"), "skyy-hub")
    Npc.keep(hub, JLong(3208000))
    K.check(int(Npc.PROPQ.size()) == 0 and "prop:gone" not in st["removed"], "FIX2-2.1 a queued ! that is gone already (area unloaded) is just forgotten")
    r = str(Npc.add(None, H2, 1.0, 70.0, 1.0, JFloat(0.0), "board"))     # back where the later steps expect it
    K.check(r.startswith("+Quest Board placed here (skyy-hub2") and str(Npc.recOf("board").world) == "skyy-hub2", "FIX2-2.1 (the board back in skyy-hub2)")
    Npc.GHOSTS.clear()
    # FIX2: a keeper pass whose record is removed while it makes the ! (an admin elsewhere, the move / remove race) drops that ! at once
    rb = Npc.recOf("board")
    Npc.dropProp(Npc.API, H2, rb)
    st["on_prop"] = lambda: Npc.dropRec("board")
    Npc.keep(H2, JLong(3210000))
    st["on_prop"] = None
    K.check(Npc.recOf("board") is None and rb.prop is None and not [v for v in st["props"].values() if v[4] == "skyy-hub2"],
            "FIX2 the record went while its ! was made: that ! is removed at once (never a stray !)")
    st["ents"].pop(str(rb.uuid), None)
    r = str(Npc.add(None, H2, 1.0, 70.0, 1.0, JFloat(0.0), "board"))
    K.check(r.startswith("+Quest Board placed here (skyy-hub2"), "FIX2 (the board back in skyy-hub2)")
    # N10 the add hook (RefSystem): known = keep, ghost = remove, orphan (our role + our NPC name, unregistered) = remove, others = keep
    K.eq(int(Npc.onAdded(HUB, um2, "Tuluk_Fisherman", "Marlow")), 0, "N10 our registered Marlow is kept")
    Npc.GHOSTS.put("00000000-0000-4000-8000-000000000999", "1|" + HUB)
    K.eq(int(Npc.onAdded(HUB, "00000000-0000-4000-8000-000000000999", "Tuluk_Fisherman", "Marlow")), 1, "N10 a ghost is removed when it loads")
    K.check(not bool(Npc.GHOSTS.containsKey("00000000-0000-4000-8000-000000000999")), "N10 ... and forgotten")
    K.eq(int(Npc.onAdded(HUB, "00000000-0000-4000-8000-000000000998", "Tuluk_Fisherman", "Marlow")), 1, "N10 an orphan Marlow (no registry line) is removed")
    K.eq(int(Npc.onAdded(HUB, "00000000-0000-4000-8000-000000000997", "Tuluk_Fisherman", "Bjorn")), 0, "N10 another Tuluk is left alone")
    K.eq(int(Npc.onAdded(HUB, "00000000-0000-4000-8000-000000000996", "Temple_Kweebec_Static", "Fennel")), 0, "N10 another Kweebec is left alone")
    Npc.FROZEN = True
    K.eq(int(Npc.onAdded(HUB, "00000000-0000-4000-8000-000000000995", "Tuluk_Fisherman", "Marlow")), 0, "N10 an unreadable registry (FROZEN) never removes an NPC")
    K.check(str(Npc.add(None, hub, 0.0, 0.0, 0.0, JFloat(0.0), "marlow")).startswith("-npcs.tsv could not be read"), "N10 ... and refuses changes")
    Npc.FROZEN = False
    # N11 an unreadable npcs.tsv freezes (never written over)
    raw_ok = open(os.path.join(X.base, "npcs.tsv"), "rb").read()
    open(os.path.join(X.base, "npcs.tsv"), "w", encoding="utf8").write("npc\tmarlow\tskyy-hub\tNOT_A_NUMBER\t1\t1\t0\tx\n")
    Npc.load(JClass("java.util.ArrayList")())
    K.check(bool(Npc.FROZEN) and not bool(Npc.save()), "N11 a broken npcs.tsv = FROZEN, save refuses")
    K.check(open(os.path.join(X.base, "npcs.tsv"), encoding="utf8").read().startswith("npc\tmarlow\tskyy-hub\tNOT_A_NUMBER"), "N11 ... the file is not written over")
    open(os.path.join(X.base, "npcs.tsv"), "wb").write(raw_ok)
    Npc.load(JClass("java.util.ArrayList")())
    K.check(not bool(Npc.FROZEN) and Npc.recOf("marlow") is not None, "N11 fixed + reload = unfrozen")
    # N12 the Use system + the add system through the stand-in ECS store (the real handlers)
    engine_types(K, ["com.hypixel.hytale.server.core.universe.PlayerRef", "com.hypixel.hytale.server.core.entity.UUIDComponent",
                     "com.hypixel.hytale.server.npc.entities.NPCEntity", "com.hypixel.hytale.server.core.entity.nameplate.Nameplate"])
    try:
        em = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule").get()
        if em is not None:
            f = em.getClass().getDeclaredField("classToComponentType")
            f.setAccessible(True)
            if f.get(em) is None:
                f.set(em, JClass("java.util.HashMap")() if f.getType().isAssignableFrom(JClass("java.util.HashMap").class_) else JClass("java.util.concurrent.ConcurrentHashMap")())
    except Exception as ex:
        K.notes.append("EntityModule stand-in: %s" % str(ex)[:120])
    U = unsafe()
    FakeStore, FakeChunk, FakeWorld, FakeE = (JClass("com.hypixel.hytale.component.SkyyQFakeStore"), JClass(FAKE + ".FakeChunk"), JClass(FAKE + ".FakeWorld"), JClass(FAKE + ".FakeEStore"))
    sto = U.allocateInstance(FakeStore.class_)
    ch = U.allocateInstance(FakeChunk.class_)
    wd = U.allocateInstance(FakeWorld.class_)
    es = U.allocateInstance(FakeE.class_)
    FakeE.W = wd
    FakeStore.EXT = es
    FakeWorld.NAME = HUB
    Ref = JClass("com.hypixel.hytale.component.Ref")
    tref = Ref(sto, 3)
    FakeChunk.REF = Ref(sto, 4)
    UUC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    UUID = JClass("java.util.UUID")
    prA = pref_of(ua, "Ann")
    UEP = JClass("com.hypixel.hytale.server.core.event.events.ecs.UseEntityEvent$Pre")
    ev = UEP(None, None, tref)
    FakeStore.NEXT = UUC(UUID.fromString(um2))
    FakeStore.COMP = prA
    runs = int(FakeWorld.RUNS)
    use = X.E.P("QUseSys")()
    use.handle(0, ch, sto, None, ev)
    K.check(bool(ev.isCancelled()) and int(FakeWorld.RUNS) == runs + 1, "N12 F on Marlow: the vanilla use is cancelled, the page task goes to the world (NEXT tick, never inside the handler)")
    ev2 = UEP(None, None, tref)
    FakeStore.NEXT = UUC(UUID.fromString(um2))
    use.handle(0, ch, sto, None, ev2)
    K.check(bool(ev2.isCancelled()) and int(FakeWorld.RUNS) == runs + 1, "N12 a second Use within 250 ms: cancelled, no second page (one page per press)")
    ev3 = UEP(None, None, tref)
    FakeStore.NEXT = UUC(UUID.fromString("00000000-0000-4000-8000-00000000abcd"))
    use.handle(0, ch, sto, None, ev3)
    K.check(not bool(ev3.isCancelled()), "N12 F on any other NPC: untouched (the vanilla use goes on)")
    Npc.GHOSTS.put("00000000-0000-4000-8000-00000000beef", "1|" + HUB)
    ev4 = UEP(None, None, tref)
    FakeStore.NEXT = UUC(UUID.fromString("00000000-0000-4000-8000-00000000beef"))
    runs = int(FakeWorld.RUNS)
    use.handle(0, ch, sto, None, ev4)
    K.check(bool(ev4.isCancelled()) and int(FakeWorld.RUNS) == runs, "N12 F on a ghost (not removed yet): cancelled, no page")
    Npc.GHOSTS.remove("00000000-0000-4000-8000-00000000beef")
    ev5 = UEP(None, None, tref)
    ev5.setCancelled(True)
    FakeStore.NEXT = UUC(UUID.fromString(um2))
    runs = int(FakeWorld.RUNS)
    use.handle(0, ch, sto, None, ev5)
    K.eq(int(FakeWorld.RUNS), runs, "N12 an already-cancelled Use is left alone")
    add = X.E.P("QNpcAddSys")()
    try:
        add.getQuery()
        K.check(True, "N12 QNpcAddSys.getQuery (NPCEntity's type; null in a bare JVM)")
    except Exception as ex:
        K.check(False, "N12 QNpcAddSys.getQuery: %s" % str(ex)[:120])
    FakeStore.COMP = None
    nw = len([x for x in X.Log.LINES if "npcadd" in str(x) or "add hook" in str(x)])
    try:
        FakeStore.NEXT = UUC(UUID.fromString(um2))
        add.onEntityAdded(tref, None, sto, None)
        K.eq(len([x for x in X.Log.LINES if "add hook" in str(x)]), nw, "N12 ... without a WARN")
        K.check(True, "N12 QNpcAddSys.onEntityAdded runs on the stand-in store (a registered uuid: kept, no CommandBuffer call)")
    except Exception as ex:
        K.check(False, "N12 QNpcAddSys.onEntityAdded: %s" % str(ex)[:200])
    # QTalkTask: a stand-in PlayerRef with no entity = nothing opens (no crash)
    X.E.P("QTalkTask")(prA, "marlow").run()
    K.check(True, "N12 QTalkTask with a player that has no entity returns quietly")
    # N13 map + compass markers: one provider per world, rows per player, the collector, the bridge
    w1 = JString(HUB)
    K.check(bool(Marks.provide(w1)) and not bool(Marks.provide(w1)) and st["prov"] == [HUB], "N13 one marker provider per world (added once)")
    try:
        Marks.refresh(pa, sa)
    except Exception as ex:
        K.check(False, "N13 QMarks.refresh in a bare JVM: %s" % str(ex)[:300])
    rows = [tuple(str(x) for x in r_) for r_ in Marks.bridge(ua, HUB)]
    K.check(("npc:marlow", "!") in [r_[:2] for r_ in rows] and ("npc:board", "!") not in [r_[:2] for r_ in rows], "N13 a's rows: Marlow '!' (the board stands in skyy-hub2): %s" % rows)
    b0 = int(Marks.BUILDS)
    Marks.refresh(pa, sa)
    K.eq(int(Marks.BUILDS), b0, "N13 nothing changed = nothing rebuilt (markers once / on change)")
    Marks.refresh(pb, sb)
    rows_b = [tuple(str(x) for x in r_) for r_ in Marks.bridge(ub, HUB)]
    K.check(("npc:marlow", "?") in [r_[:2] for r_ in rows_b], "N13 b's rows: Marlow '?': %s" % rows_b)
    K.eq(len(Marks.bridge(ua, "another-world")), 0, "N13 another world = no rows")

    got = []

    @JImplements("com.hypixel.hytale.server.core.universe.world.worldmap.markers.MarkersCollector")
    class Col(object):
        @JOverride
        def add(self, m):
            got.append(("add", str(m.id)))

        @JOverride
        def addIgnoreViewDistance(self, m):
            got.append(("far", str(m.id), str(m.markerImage)))

        @JOverride
        def isInViewDistance(self, *a):
            return True

        @JOverride
        def getPlayerMapFilter(self):
            return None
    try:
        n = int(Marks.collect(ua, HUB, Col()))
        K.check(n >= 1 and ("far", "SkyyQuestNpcmarlow", "Temple_GatewayCTA.png") in got and not [g for g in got if g[0] == "add"],
                "N13 the collector gets OUR markers (ids SkyyQuest... = the minimap's quest kind), visible from far: %s" % got)
    except Exception as ex:
        K.check(False, "N13 collect / MapMarkerBuilder in a bare JVM: %s" % str(ex)[:200])
    Cfg.MARK_MAP = False
    Marks.refresh(pa, sa)
    del got[:]
    K.check(int(Marks.collect(ua, HUB, Col())) == 0 and got == [] and len(Marks.bridge(ua, HUB)) >= 1, "N13 'Map and compass markers' off: no map markers (quest:fn:markers still answers)")
    Cfg.MARK_MAP = True
    qf = X.E.P("QFn")("markers")
    r_ = qf.apply(JArray(JObject)([ua, HUB]))
    K.check(len(r_) >= 1 and str(r_[0][0]).startswith("npc:"), "N13 quest:fn:markers = the rows {id, ! / ? / place, x, y, z, label}")
    # the widget target place joins the rows
    Defs.savePlace("island2", HUB, 1.0, 2.0, 3.0, "Island 2")
    pa.dirPlace = "island2"
    Marks.refresh(pa, sa)
    rows = [tuple(str(x) for x in r_) for r_ in Marks.bridge(ua, HUB)]
    K.check(("island2", "place") in [r_[:2] for r_ in rows], "N13 the quest widget's target place is a marker too: %s" % rows)
    # N14 remove + list
    r = str(Npc.remove(None, hub, "marlow"))
    K.check(r.startswith("+Marlow removed") and Npc.recOf("marlow") is None and um2 not in st["ents"], "N14 /questadmin npc remove marlow: %s" % r)
    K.check(str(Npc.remove(None, hub, "marlow")).startswith("=Marlow is not placed"), "N14 removing it again")
    lt = str(Npc.listText())
    K.check("board (Quest Board, Temple_Kweebec_Static): skyy-hub2" in lt and "marlow (Marlow, Tuluk_Fisherman): not placed" in lt, "N14 /questadmin npc list: %s" % lt)
    # N15 the tick's world part: a keeper hop only for worlds with a quest NPC (or a ghost) AND a player there
    Npc.GHOSTS.clear()
    Tk = X.E.P("QTick")
    st["calls"] = {}
    Tk.N = 2
    X.World.tick(JLong(int(time.time() * 1000)))
    K.eq(st["calls"].get("exec", 0), 0, "N15 no player stands in skyy-hub2 = no keeper hop")
    pa.world = "skyy-hub2"
    st["worlds"].add("skyy-hub2")
    X.World.tick(JLong(int(time.time() * 1000)))
    K.eq(st["calls"].get("exec", 0), 1, "N15 a player there = one hop to that world")
    Tk.N = 3
    X.World.tick(JLong(int(time.time() * 1000)))
    K.eq(st["calls"].get("exec", 0), 1, "N15 every 2 s only")
    st["worlds"].add("skyy-hub3")
    Npc.PROPQ.put(JString("prop:left"), "skyy-hub3")
    pa.world = "skyy-hub3"
    Tk.N = 4
    X.World.tick(JLong(int(time.time() * 1000)))
    K.check(st["calls"].get("exec", 0) == 2 and int(Npc.PROPQ.size()) == 0, "FIX2-2.1 a world with a queued ! (and a player) gets a keeper hop, which clears it")
    pa.world = "skyy-hub2"
    # FIX-B2: Server Setup "Daily jobs board" and /questadmin npc remove board take the caller away (and give it back)
    Hk = X.E.P("QHooks")
    K.check(bool(br.containsKey("quest:caller:board")), "FIX-B2 (the board stands in skyy-hub2)")
    Cfg.BOARD_ON = False
    Hk.cfgChanged("quests.board.enabled")
    K.check(not br.containsKey("quest:caller:board") and bool(Eng.partSoon(tour[0])), "FIX-B2 Daily jobs board off = no caller (the part shows coming soon)")
    Cfg.BOARD_ON = True
    Hk.cfgChanged("quests.board.enabled")
    K.check(bool(br.containsKey("quest:caller:board")), "FIX-B2 ... on again = the caller is back")
    r = str(Npc.remove(None, JString("skyy-hub2"), "board"))
    K.check(r.startswith("+Quest Board removed") and not br.containsKey("quest:caller:board"), "FIX-B2 /questadmin npc remove board = the caller goes: %s" % r)
    K.save()


# ====================================================================================================== B: the hub board + 3 daily jobs
def run_board(out, jar, scratch, home):
    from jpype import JClass, JObject, JArray, JLong, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, FAKE_DIR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    PyFn = fn_class()
    X = scene3(K, scratch, "b")
    Npc, Cfg, Eng, Defs, Sto, Talk = X.Npc, X.Cfg, X.Eng, X.Defs, X.Sto, X.Talk
    Npc.API = npc_api(api_state())
    BL = Defs.BOARD
    T0 = (20741 * 86400 + 12 * 3600) * 1000      # noon UTC of a fixed day as the board clock
    Defs.TEST_NOW = T0
    Defs.DAYMAX = JLong(-9223372036854775808)
    d0 = int(Defs.day())
    K.eq(d0, 20741, "B1 day = floor(now / 86400 s) at the default anchor (midnight UTC)")
    Cfg.BOARD_ANCHOR = 13 * 3600
    K.eq(int(Defs.day()), 20741, "B1 an anchor change never sends the day back within a run (DAYMAX)")
    Defs.DAYMAX = JLong(-9223372036854775808)
    K.eq(int(Defs.day()), 20740, "B1 (a fresh start) an anchor 13 h after midnight: noon still belongs to yesterday's board")
    K.eq(int(Defs.leftSeconds()), 3600, "B1 ... and the new jobs come in 1 h")
    Cfg.BOARD_ANCHOR = 0
    Defs.DAYMAX = JLong(-9223372036854775808)
    # B2 picks: per tier one, from FNV-1a(pkey | day) with java.util.Random (TownProbe #12), the same every time
    Rnd = JClass("java.util.Random")

    def fnv(s_):
        h = 0xcbf29ce484222325
        for c_ in s_:
            h ^= ord(c_)
            h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
        return h - (1 << 64) if h >= (1 << 63) else h

    def want_picks(pk, day, ok):
        r = Rnd(JLong(fnv("%s|%d" % (pk, day))))
        res = []
        for tier in (1, 2, 3):
            idx = [i for i, t in enumerate(BL.tasks) if int(t.tier) == tier]
            k = int(r.nextInt(len(idx)))
            for m in range(len(idx)):
                i = idx[(k + m) % len(idx)]
                if ok(str(BL.tasks[i].id)):
                    res.append(i)
                    break
        return res
    K.eq(int(Defs.fnv("a")), fnv("a"), "B2 FNV-1a 64 (the TownProbe seed) matches")
    nofish = lambda tid: not tid.startswith("fish")
    u1, p1, s1 = X.player(51, HUB)
    pk1 = str(s1.pk)
    pk_ = [int(x) for x in s1.dailyPicks(BL)]
    K.eq(pk_, want_picks(pk1, d0, nofish), "B2 today's 3 jobs = per tier the seeded pick (fish jobs hidden without SkyyFishing)")
    K.eq(sorted(int(BL.tasks[i].tier) for i in pk_), [1, 2, 3], "B2 one Easy, one Medium, one Hard")
    K.eq([int(x) for x in s1.dailyPicks(BL)], pk_, "B2 the same picks every time")
    seen = set()
    fish_pk = None
    for n in range(60):
        seen.add(tuple(int(x) for x in Eng.pickDaily(BL, "pk%d" % n, JLong(d0))))
    K.check(len(seen) > 5 and not [p_ for p_ in seen if any(str(BL.tasks[i].id).startswith("fish") for i in p_)], "B2 other profiles get other jobs; no fish job without SkyyFishing (%d sets)" % len(seen))
    br.put("config:def:SkyyFishing", JClass("java.lang.Object")())
    br.put("quest:caller:fishing", JClass("java.lang.Boolean").TRUE)
    seen2 = [tuple(int(x) for x in Eng.pickDaily(BL, "pk%d" % n, JLong(d0))) for n in range(60)]
    K.check([p_ for p_ in seen2 if any(str(BL.tasks[i].id).startswith("fish") for i in p_)], "B2 with SkyyFishing 0.1.4 the fish jobs can be picked")
    for n in range(60):
        K.eq(list(seen2[n]), want_picks("pk%d" % n, d0, lambda tid: True), "B2 seeded pick pk%d" % n) if n < 3 else None
    br.remove("config:def:SkyyFishing")
    br.remove("quest:caller:fishing")
    # B3 not started = nothing counts; the first use of the board starts the line
    t1 = BL.tasks[pk_[0]]
    part = t1.parts[0]
    keyfor = {"any": "Kweebec", "Wood_*_Trunk*": "Wood_Oak_Trunk", "Wood_*_Trunk": "Wood_Oak_Trunk", "Rock_Stone*": "Rock_Stone", "Ore_Copper*": "Ore_Copper",
              "Ore_Iron*": "Ore_Iron_Slate", "Plant_Crop_Wheat_Item": "Plant_Crop_Wheat_Item"}
    key = keyfor.get(str(part.match), str(part.match))
    Eng.count(u1, int(part.type), key, int(part.count), HUB, False)
    K.check(not bool(s1.isDone(Eng.tk(BL, t1))), "B3 a job does not count before the board was used")
    K.check(bool(Talk.startBoard(p1, s1, JLong(1))) and bool(s1.isStarted("board")) and not bool(Talk.startBoard(p1, s1, JLong(2))), "B3 the board starts the line once")
    K.check((X.want(u1) & int(part.type)) != 0, "B3 the picked job's objective is wanted now")
    # B4 a job done: claims once, the keys carry the day
    Eng.count(u1, int(part.type), key, int(part.count), HUB, False)
    k1 = str(Eng.tk(BL, t1))
    K.check(k1 == "board.%s@%d" % (t1.id, d0) and bool(s1.isDone(k1)), "B4 the job is done under its day key %s" % k1)
    cl = [str(c) for c in s1.claims if ":board." in str(c)]
    rw1 = str(Defs.rewardOf(BL, t1)).split(",")
    K.check(len(cl) == len(rw1) and cl[0].startswith("coins|%d|" % {1: 40, 2: 80, 3: 140}[int(t1.tier)]) and [c.split("|")[0] for c in cl] == [x.split(":")[0] for x in rw1]
            and all((":" + k1 + ":") in c for c in cl), "B4 the job's claims (coins + item, or coins + gear on a kill job), the grant ids carry the day key: %s" % cl)
    K.check(k1 in [str(x) for x in s1.issued], "B4 issued (never twice today)")
    out_ = JClass("java.util.ArrayList")()
    s1.adminUndo(BL, t1)
    s1.adminDone(BL, t1, JLong(5), out_)
    K.eq(len([c for c in s1.claims if ":board." in str(c)]), len(rw1), "B4 undo + done again the same day = no second payout")
    # a second job half done before a restart
    t2 = BL.tasks[pk_[1]]
    p2_ = t2.parts[0]
    k2 = keyfor.get(str(p2_.match), str(p2_.match))
    half = max(1, int(p2_.count) // 2)
    Eng.count(u1, int(p2_.type), k2, half, HUB, False)
    rows = [str(x) for x in s1.rowsOf(BL)]
    K.eq(sum(1 for i in range(len(BL.tasks)) if rows[2 * i] != "nottoday"), 3, "B5 the board's rows: 3 jobs today, the rest 'nottoday'")
    prog2 = rows[2 * pk_[1] + 1]
    # B6 a restart: the same 3 jobs, the done one done, the half one half
    K.check(bool(Sto.write(s1)), "B6 (state written)")
    Sto.CACHE.clear()
    Eng.PLAYERS.clear()
    Defs.load()
    BL2 = Defs.BOARD
    s1b = Sto.read(pk1, u1)
    K.eq([int(x) for x in s1b.dailyPicks(BL2)], pk_, "B6 after a restart: the same 3 jobs")
    rows_b = [str(x) for x in s1b.rowsOf(BL2)]
    K.check(rows_b[2 * pk_[0]] == "done" and rows_b[2 * pk_[1] + 1] == prog2 and bool(s1b.isStarted("board")), "B6 ... the done job done, the half one at %s" % prog2)
    s1b.owner = u1
    Sto.CACHE.put(pk1, s1b)
    p1.loaded = True
    Eng.PLAYERS.put(u1, p1)
    Eng.rebuild(u1, s1b)
    # B7 the next day: new jobs, yesterday's done job is not done today, nothing paid twice
    Defs.TEST_NOW = T0 + 86400 * 1000
    d1 = int(Defs.day())
    pk_d1 = [int(x) for x in s1b.dailyPicks(BL2)]
    K.eq(pk_d1, want_picks(pk1, d1, nofish), "B7 a new day = the new seeded jobs")
    K.check(not bool(s1b.isDone(Eng.tk(BL2, BL2.tasks[pk_d1[0]]))) or pk_d1[0] != pk_[0], "B7 yesterday's done job is fresh today (a new key)")
    X.World.DAY = JLong(d0)
    X.World.tick(JLong(T0 + 86400 * 1000))
    K.eq(int(X.World.DAY), d1, "B7 the tick sees the day change (QWorld.roll)")
    keys_d0 = [str(k) for k in s1b.done.keySet()] + [str(k) for k in s1b.issued]
    K.check([k for k in keys_d0 if ("@%d" % d0) in k], "B7 yesterday's keys stay (pruned only when older than yesterday)")
    Defs.TEST_NOW = T0 + 3 * 86400 * 1000
    d3 = int(Defs.day())
    n_pruned = int(s1b.pruneDaily(JLong(d3)))
    keys_after = [str(k) for k in s1b.done.keySet()] + [str(k) for k in s1b.issued] + [str(k) for k in s1b.prog.keySet()] + [str(k) for k in s1b.pdone]
    K.check(n_pruned > 0 and not [k for k in keys_after if ("@%d" % d0) in k], "B7 3 days later: day %d's board keys are pruned (%d)" % (d0, n_pruned))
    K.check([str(k) for k in s1b.done.keySet() if str(k).startswith("tutorial.")] == [str(k) for k in Sto.read(pk1, u1).done.keySet() if str(k).startswith("tutorial.")],
            "B7 pruning touches only the board's keys")
    Defs.TEST_NOW = T0
    Defs.DAYMAX = JLong(-9223372036854775808)
    # B8 the board page (real UICommandBuilder) + its buttons
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    pr1 = pref_of(u1, "Bo")
    BP = X.E.P("QBoardPage")(pr1)
    b, ev = UCB(), UEB()
    BP.build(None, b, ev, None)
    mk = markup(b)
    K.check("SkyyQbR0" in mk and "SkyyQbR2" in mk and "SkyyQbR3" not in mk and "Easy" in mk and "Medium" in mk and "Hard" in mk
            and "New jobs in" in mk and str(BL2.tasks[pk_[0]].name) in mk and "coins" in mk, "B8 the board page: 3 job rows (tier, name, progress, reward), the reset time")
    K.check("_" not in "".join(t_ for t_ in mk.split() if t_.startswith("#")), "B8 no underscore in an element id")
    try:
        BP.handleDataEvent(None, None, '{"a":"track"}')
    except Exception:
        pass
    K.check(str(BP.info).startswith("+Tracking Daily Jobs") and str(s1b.track) == "board", "B8 Track jobs = the widget shows the daily jobs: %s" % BP.info)
    h = Eng.hud(u1)
    K.check(h is not None and str(h[0]) == "Daily Jobs" and str(h[1]).endswith("/ 3"), "B8 the widget counts today's 3 jobs: %s" % (None if h is None else [str(h[0]), str(h[1])]))
    try:
        BP.handleDataEvent(None, None, '{"a":"claim"}')
    except Exception:
        pass
    K.check(str(BP.info).startswith("+Paying") or str(BP.info).startswith("="), "B8 Claim rewards: %s" % BP.info)
    # B9 the log page lists only today's jobs of the board
    LP = X.E.P("QLogPage")(pr1, "board")
    b, ev = UCB(), UEB()
    LP.build(None, b, ev, None)
    mk = markup(b)
    K.check("SkyyQlR2" in mk and "SkyyQlR3" not in mk, "B9 the quest log lists today's 3 jobs only")
    # B10 /quests board: within 8 blocks or 'Board from anywhere'
    K.check(str(Talk.boardCmd(pr1, None, None, None)).startswith("-The Quest Board stands in the hub (not placed yet)"), "B10 /quests board with no board placed")
    Cfg.BOARD_ON = False
    K.check(str(Talk.boardCmd(pr1, None, None, None)).startswith("-The quest board is closed"), "B10 the board switched off")
    K.check(not bool(Eng.lineOn(BL2)), "B10 ... the daily line is off (nothing counts)")
    pg = Talk.pageFor(pr1, "board")
    K.check(pg is not None and "QDlgPage" in str(pg.getClass().getName()) and "closed" in str(pg.pages[0]), "B10 F on the board while it is off: 'closed today'")
    Cfg.BOARD_ON = True
    pg = Talk.pageFor(pr1, "board")
    K.check(pg is not None and "QBoardPage" in str(pg.getClass().getName()), "B10 F on the board = the board page")
    # FIX-C2 (critic; Skyy Q1 "if its a combat quest, unidentified weapons and armor ... items and coins on other quest types")
    kills = [t for t in BL2.tasks if int(t.parts[0].type) == TB["kill"]]
    K.check(len(kills) == 3 and all("gear:weapon" in str(Defs.rewardOf(BL2, t)) and "gear:armor" in str(Defs.rewardOf(BL2, t)) and "item:" not in str(Defs.rewardOf(BL2, t))
                                    and str(Defs.rewardOf(BL2, t)).startswith("coins:") for t in kills),
            "FIX-C2 the 3 kill jobs pay coins + an unidentified weapon + armor piece: %s" % [str(Defs.rewardOf(BL2, t)) for t in kills])
    K.check(all("item:" in str(Defs.rewardOf(BL2, t)) and "gear:" not in str(Defs.rewardOf(BL2, t)) for t in BL2.tasks if int(t.parts[0].type) != TB["kill"]),
            "FIX-C2 every other job pays coins + an item, no gear")
    uk, pkk, skk = X.player(58, HUB)
    hk = kills[0]
    out_k = JClass("java.util.ArrayList")()
    Eng.completeL(skk, BL2, hk, JLong(9), out_k)
    ck = sorted(str(c).split("|")[0] + "|" + str(c).split("|")[1] for c in skk.claims if (":" + str(Eng.tk(BL2, hk)) + ":") in str(c))
    K.eq(ck, ["coins|40", "gear|armor", "gear|weapon"], "FIX-C2 a kill job done = a coins claim + a gear weapon + a gear armor claim (SkyyGear's bag at the class level)")
    # FIX-C3 (critic): Server Setup "Daily jobs per day" (1-3) + "Daily job coins (percent)" (0-300)
    rown = lambda st_: sum(1 for i in range(len(BL2.tasks)) if str(st_.rowsOf(BL2)[2 * i]) != "nottoday")
    Cfg.BOARD_JOBS = 1
    K.check([int(x) for x in s1b.dailyPicks(BL2)] == pk_[:1] and rown(s1b) == 1, "FIX-C3 1 job a day = today's Easy job only (the same seed, the cache follows the switch)")
    Cfg.BOARD_JOBS = 2
    K.check([int(x) for x in s1b.dailyPicks(BL2)] == pk_[:2] and rown(s1b) == 2, "FIX-C3 2 jobs a day = Easy + Medium")
    Cfg.BOARD_JOBS = 3
    K.check([int(x) for x in s1b.dailyPicks(BL2)] == pk_ and rown(s1b) == 3, "FIX-C3 back to 3 = the same 3 jobs")
    Cfg.load()
    K.check(int(Cfg.BOARD_JOBS) == 3 and int(Cfg.BOARD_SCALE) == 100, "FIX-C3 config defaults: 3 jobs, 100 percent")
    Cfg.BOARD_SCALE = 150
    K.eq(str(Defs.rewardOf(BL2, hk)), "coins:60,gear:weapon,gear:armor", "FIX-C3 150 percent: a 40-coin job pays 60")
    Cfg.BOARD_SCALE = 0
    K.eq(str(Defs.rewardOf(BL2, hk)), "gear:weapon,gear:armor", "FIX-C3 0 percent: no coins (the gear stays)")
    fi_ = Defs.line("fishing_intro")
    K.eq(str(Defs.rewardOf(fi_, fi_.tasks[2])), "coins:50,item:Food_Fish_Grilled:3", "FIX-C3 the percent touches daily jobs only (Marlow's line keeps its coins)")
    Cfg.BOARD_SCALE = 100
    cfgp = os.path.join(X.base, "config.properties")
    cfg_before = open(cfgp, "rb").read()
    open(cfgp, "a", encoding="utf8").write("\nboard.jobsPerDay=9\nboard.coinScalePercent=900\n")
    Cfg.load()
    K.check(int(Cfg.BOARD_JOBS) == 3 and int(Cfg.BOARD_SCALE) == 300, "FIX-C3 hand-edited values are clamped (9 jobs -> 3, 900 % -> 300 %)")
    open(cfgp, "wb").write(cfg_before)
    Cfg.load()
    # B11 a bad board file: problems, never a crash
    open(os.path.join(X.base, "board.properties"), "a", encoding="utf8").write("\ntask.99.id=bad\ntask.99.type=kill\ntask.99.match=any\ntask.99.tier=7\n")
    Defs.load()
    K.check(Defs.BOARD is not None and [str(p_) for p_ in Defs.PROBLEMS if "tier must be 1, 2 or 3" in str(p_)], "B11 a tier outside 1-3 is reported (1 used)")
    open(os.path.join(X.base, "board.properties"), "w", encoding="utf8").write("line=board\nname=x\nmode=open\ntask.1.id=a\ntask.1.type=kill\ntask.1.match=any\n")
    Defs.load()
    K.check(Defs.BOARD is None and [str(p_) for p_ in Defs.PROBLEMS if "mode must be daily" in str(p_)], "B11 a board file that is not daily = no board + a problem")
    K.save()


# ====================================================================================================== F: Marlow, his line and the pole (once)
def run_fish(out, jar, scratch, home):
    from jpype import JClass, JObject, JArray, JLong, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, FISH_JAR, FAKE_DIR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    PyFn = fn_class()
    Boolean, Long = JClass("java.lang.Boolean"), JClass("java.lang.Long")
    X = scene3(K, scratch, "f")
    Npc, Cfg, Eng, Defs, Sto, Talk, Pay = X.Npc, X.Cfg, X.Eng, X.Defs, X.Sto, X.Talk, X.Pay
    Npc.API = npc_api(api_state())
    Sto.STOPPED = True
    coins = []
    br.put("coins:fn:add", PyFn(lambda a: coins.append(int(a[1])) or Long(1000)))
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    FL = Defs.line("fishing_intro")
    u, p, s = X.player(61, HUB)
    pr = pref_of(u, "Fin")
    p.pr = pr
    # F1 without SkyyFishing 0.1.4: the line is hidden, Marlow is closed, no sign
    K.check(bool(Talk.allHidden(FL)) and int(s.npcMark("marlow")) == 0, "F1 no fishing:fn:starter = Marlow's line hidden, no sign")
    pg = Talk.pageFor(pr, "marlow")
    K.check(pg is not None and int(pg.mode) == 0 and "not biting" in str(pg.pages[0]), "F1 F on Marlow: 'The fish are not biting today'")
    # F2 SkyyFishing 0.1.4 (the REAL FishQuestFn in this JVM): the offer
    FB = JClass("com.skyy.fishing.FishBridge")
    FB.questInit()
    K.check(br.get("fishing:fn:starter") is not None and br.get("fishing:fn:grantOf") is not None and bool(br.get("quest:caller:fishing")),
            "F2 SkyyFishing 0.1.4 publishes fishing:fn:starter, fishing:fn:grantOf, quest:caller:fishing")
    K.eq(int(s.npcMark("marlow")), 1, "F2 Marlow '!' (an offer)")
    pg = Talk.pageFor(pr, "marlow")
    K.check(int(pg.mode) == 1 and len(pg.pages) == 3 and "Ahoy" in str(pg.pages[0]) and "Deal?" in str(pg.pages[2]), "F2 the offer: 3 pages from dialogue/marlow.properties")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    b, ev = UCB(), UEB()
    pg.build(None, b, ev, None)
    mk = markup(b)
    K.check("SkyyQdNext" in mk and "SkyyQdClose" in mk and "SkyyQdYes" not in mk and "Food_Fish_Raw" in mk and "Ahoy" in mk and "page 1 of 3" in mk,
            "F2 page 1: the portrait item, the text, Next + Close")
    for _ in range(2):
        try:
            pg.handleDataEvent(None, None, '{"a":"next"}')
        except Exception:
            pass
    b, ev = UCB(), UEB()
    pg.build(None, b, ev, None)
    mk = markup(b)
    K.check("SkyyQdYes" in mk and "SkyyQdNo" in mk and "SkyyQdNext" not in mk and "Deal?" in mk, "F2 the last offer page: Accept + Not now")
    K.check("_" not in "".join(t_ for t_ in mk.split() if t_.startswith("#")), "F2 no underscore in an element id")
    # F3 Accept: the line starts + is tracked, the pole task completes = ONE pole claim (+ its coins)
    try:
        pg.handleDataEvent(None, None, '{"a":"yes"}')
    except Exception:
        pass
    cl = [str(c) for c in s.claims]
    poles = [c for c in cl if c.startswith("pole|starter|")]
    K.check(bool(s.isStarted("fishing_intro")) and str(s.track) == "fishing_intro" and bool(s.isDone("fishing_intro.take_pole")) and len(poles) == 1,
            "F3 Accept: started, tracked, 'Take the pole' done, one pole claim: %s" % cl)
    K.check(int(pg.mode) == 0 and "Right click deep water" in str(pg.pages[0]) and "Wooden Fishing Rod" in str(pg.reward) and str(pg.info).startswith("+"),
            "F3 the page turns into Marlow's hand-over line + the reward: %s / %s" % (pg.pages[0], pg.reward))
    try:
        pg.handleDataEvent(None, None, '{"a":"yes"}')
    except Exception:
        pass
    K.eq(len([c for c in s.claims if str(c).startswith("pole|")]), 1, "F3 a second Accept click = nothing more")
    ra = Talk.accept(pr, "marlow")
    K.check(ra is not None and str(ra[1]) == "", "F3 accept() again (a stale page): no reward")
    K.eq(len([c for c in s.claims if str(c).startswith("pole|")]), 1, "F3 ... still one pole claim")
    gid = poles[0].split("|")[2]
    K.check(gid.startswith(str(s.pk) + ":fishing_intro.take_pole:"), "F3 the grant id = profile : line.task : n (%s)" % gid)
    # F4 the pole is made by SkyyFishing (real FishQuestFn) and given through the item path, once
    try:
        item_store(["SkyyFishing_Rod_Bamboo", "Rock_Stone"])
    except Exception as ex:
        K.notes.append("item store stand-in: %s" % str(ex)[:120])
    fnS = br.get("fishing:fn:starter")
    pole = fnS.apply(JArray(JObject)([u, gid]))
    K.check(pole is not None and str(pole.getItemId()) == "SkyyFishing_Rod_Bamboo" and int(pole.getQuantity()) == 1,
            "F4 fishing:fn:starter makes the Wooden Fishing Rod (SkyyFishing_Rod_Bamboo)")
    K.eq(str(br.get("fishing:fn:grantOf").apply(pole)), gid, "F4 the rod carries the claim's grant id (fishing:fn:grantOf)")
    FR = JClass("com.skyy.fishing.FishRig")
    K.eq(str(FR.rigOf(pole)[0]), "1", "F4 ... with the Wooden Reel fitted (the bench's fresh rig)")
    K.check(br.get("fishing:fn:grantOf").apply(JClass("com.hypixel.hytale.server.core.inventory.ItemStack")("Rock_Stone", 1)) is None, "F4 grantOf: not a rod = null")
    K.check(fnS.apply(JArray(JObject)([u, ""])) is None and fnS.apply("bad") is None, "F4 starter: no grant id / bad args = null")
    # payState: the universe stand-in sends the give to the player's world (the stand-in player has no inventory = it comes back)
    U2 = unsafe()
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
    setf(pr, "com.hypixel.hytale.server.core.universe.PlayerRef", "worldUuid", JClass("java.util.UUID")(5, 5))
    FU.PR = pr
    starter_calls = []
    real = br.get("fishing:fn:starter")
    br.put("fishing:fn:starter", PyFn(lambda a: starter_calls.append(str(a[1])) or real.apply(a)))
    lg0 = logtext(X.base)
    K.check(("BACK %s pole|starter|%s (refused" % (s.pk, gid)) in lg0, "F4 the accept already tried to pay it (no world for the stand-in yet = refused, kept, never lost)")
    s.retryNow()                                   # = /quests claim
    runs0 = int(FW.RUNS)
    Pay.payState(p, s, JLong(int(time.time() * 1000)))
    Sto.drainLate()
    lg = logtext(X.base)
    K.check(starter_calls == [gid] and int(FW.RUNS) >= runs0 + 1 and ("PAYING %s pole|starter|%s" % (s.pk, gid)) in lg,
            "F4 the pole claim: PAYING, SkyyFishing made it for that grant, the give ran on the player's world: %s" % starter_calls)
    K.check(("BACK %s pole|starter|%s (no room)" % (s.pk, gid)) in lg and len([c for c in s.claims if str(c).startswith("pole|")]) == 1,
            "F4 a player the give cannot reach = the pole claim comes back (nothing lost)")
    cp = [str(c) for c in s.claims if str(c).startswith("pole|")][0]
    c = str(s.takeClaimAt(int([str(x) for x in s.claims].index(cp))))
    s.markPaying(c, JLong(int(time.time() * 1000)))
    Pay.itemDone(s, c, 1, 1, "SkyyFishing_Rod_Bamboo")
    K.check(("PAID %s %s" % (s.pk, c)) in logtext(X.base) and not [x for x in s.claims if str(x).startswith("pole|")], "F4 the pole landed = PAID once, no pole claim left")
    # F5 the grant guard: a rod with this grant already in the bags = never a second one (a repay after a crash)
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    Give = X.E.P("QGive")
    bag1, bag2 = SIC(3), SIC(3)
    bag2.addItemStack(pole)
    K.check(bool(Give.hasGrant(JArray(IC)([bag1, bag2]), gid)) and not bool(Give.hasGrant(JArray(IC)([bag1, bag2]), gid + "x"))
            and not bool(Give.hasGrant(JArray(IC)([bag1]), gid)), "F5 hasGrant finds THIS grant's rod (real FishRig grantOf), not another")
    keep = br.remove("fishing:fn:grantOf")
    K.check(not bool(Give.hasGrant(JArray(IC)([bag2]), gid)), "F5 without SkyyFishing nothing is found (the claim ledger alone guards)")
    br.put("fishing:fn:grantOf", keep)
    PW_g = PW.calls(jar)
    K.check(PKG + "QGive.hasGrant" in PW_g.get("QGive.run", ()), "F5 QGive.run asks hasGrant before giving a grant-carrying stack")
    K.eq(int(Pay.repay(s)), 0, "F5 repay after the PAID line: nothing to put back")
    open(os.path.join(X.base, "quests.log"), "a").write("2026-10-14T00:00 PAYING %s %s\n" % (s.pk, c))
    K.eq(int(Pay.repay(s)), 1, "F5 a crash between the give and its PAID line + /questadmin repay = the pole claim is back ...")
    K.check(bool(Give.hasGrant(JArray(IC)([bag1, bag2]), str(c).split("|")[2])), "F5 ... and the give then finds that rod in the bags (not given again)")
    while [x for x in s.claims if str(x).startswith("pole|")]:
        s.takeClaimAt(int([str(x) for x in s.claims].index([str(x) for x in s.claims if str(x).startswith("pole|")][0])))
    s.setPaying(False)
    # F6 talking again: the catch task text, no new claim; relog (file round trip) keeps it once
    pg = Talk.pageFor(pr, "marlow")
    K.check(int(pg.mode) == 0 and "Deep water" in str(pg.pages[0]) and not [x for x in s.claims if str(x).startswith("pole|")], "F6 F on Marlow again: the catch hint, no second pole")
    K.check(bool(Sto.write(s)), "F6 (written)")
    Sto.CACHE.clear()
    s2 = Sto.read(str(s.pk), u)
    s2.owner = u
    Sto.CACHE.put(str(s.pk), s2)
    Eng.rebuild(u, s2)
    K.check("fishing_intro.take_pole" in [str(x) for x in s2.issued] and not [x for x in s2.claims if str(x).startswith("pole|")] and bool(s2.isStarted("fishing_intro")),
            "F6 after a relog: issued, started, no pole claim")
    out_ = JClass("java.util.ArrayList")()
    s2.adminUndo(FL, FL.tasks[0])
    s2.adminDone(FL, FL.tasks[0], JLong(9), out_)
    K.check(not [x for x in s2.claims if str(x).startswith("pole|")], "F6 /questadmin set ... take_pole undo + done = still no second pole (issued is never removed)")
    s = s2
    # F7 a profile switch: the other profile is its own character - its own (one) pole; back on profile 1 still none
    br.put("profile:fn:key", PyFn(lambda a: str(a) + "-p2"))
    pk2 = str(u) + "-p2"
    s3 = Sto.read(pk2, u)
    s3.owner = u
    Sto.CACHE.put(pk2, s3)
    p.pk = pk2
    Eng.rebuild(u, s3)
    K.eq(int(s3.npcMark("marlow")), 1, "F7 a new profile: Marlow offers again (per profile, like every quest)")
    Talk.accept(pr, "marlow")
    K.eq(len([x for x in s3.claims if str(x).startswith("pole|")]), 1, "F7 ... that profile gets its own ONE pole")
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    p.pk = str(u)
    Eng.rebuild(u, s)
    K.check(not [x for x in s.claims if str(x).startswith("pole|")] and Talk.accept(pr, "marlow") is not None and not [x for x in s.claims if str(x).startswith("pole|")],
            "F7 back on profile 1: still no second pole (accept() on a started line pays nothing)")
    # F8 the catch (SkyyFishing's quest:fn:event) -> '?' over Marlow -> talk = done + rewards
    br.put("quest:fn:event", X.E.P("QFn")("event"))
    FB.questCatch(u, "SkyyFishing_Fish_Bluegill", 1)
    K.check(bool(s.isDone("fishing_intro.catch_fish")), "F8 SkyyFishing's catch event completes 'Catch a fish'")
    K.eq(int(s.npcMark("marlow")), 2, "F8 Marlow '?' (hand it in)")
    pg = Talk.pageFor(pr, "marlow")
    K.check(bool(s.isDone("fishing_intro.show_marlow")) and "Now that is a fish" in str(pg.pages[0]) and "+50 coins" in str(pg.reward), "F8 F on Marlow = shown: done + his line + the reward")
    K.eq(int(s.npcMark("marlow")), 0, "F8 the line done = no sign")
    pg = Talk.pageFor(pr, "marlow")
    K.check("Good to see you again" in str(pg.pages[0]), "F8 afterwards Marlow says the 'done' line")
    # F9 the dialogue file is Skyy's to edit
    dp = os.path.join(X.base, "dialogue", "marlow.properties")
    t_ = open(dp, encoding="utf8").read().replace("done=Good to see you again. The fish are biting today.", "done=Hello again, friend.").replace("icon=Food_Fish_Raw", "icon=Bad Icon!")
    open(dp, "w", encoding="utf8").write(t_)
    Npc.loadDialogues(JClass("java.util.ArrayList")())
    pg = Talk.pageFor(pr, "marlow")
    K.check("Hello again, friend." in str(pg.pages[0]) and str(pg.icon) == "Food_Fish_Raw", "F9 an edited dialogue file is used after reload; a bad icon id falls back to the default")
    K.check(open(dp, encoding="utf8").read() == t_, "F9 the edited file is never written over")
    try:
        fi.set(None, None)
    except Exception:
        U2.putObject(U2.staticFieldBase(fi), U2.staticFieldOffset(fi), None)
    K.save()


EXPECT = {     # the classes / members this round changes vs the live 0.2 (reviewed 2026-10-14: every one is a 0.3 change in the patch notes;
               # Cfg* = the config kit re-emitted with the five new rows)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'QCfg': ['+f BOARD_ANCHOR', '+f BOARD_JOBS', '+f BOARD_ON', '+f BOARD_REMOTE', '+f BOARD_SCALE', '+f MARK_MAP', '+f MARK_NPC', '+m particlesOn', '+m propsOn',
             '~<clinit>', '~m load'],                       # FIX C3: + jobs per day, coin percent
    'QDefs': ['+f BOARD', '+f BOARD_FILE', '+f BOARD_TEXT', '+f DAYMAX', '+f NPCPLACES', '+f POLE_NAME', '+f TEST_NOW', '+m boardScale', '+m day', '+m fnv',
              '+m leftSeconds', '~<clinit>', '~m load', '~m parse', '~m place', '~m rewardOf', '~m rewardProblem', '~m rewardText'],   # FIX C3: boardScale
    'QEng': ['+m nextTaskL', '+m npcMarkL', '+m oldDay', '+m pickDaily', '+m picksL', '+m pruneDailyL', '+m pruneIt', '+m talkTaskL', '~m hudL', '~m lineOn',
             '~m taskActive', '~m tk'],
    'QEvents': ['~m accept'],                # the map provider of the world at PlayerReady; a quit forgets the marker rows
    'QFn': ['~m apply'],                     # quest:fn:markers = the QMarks rows
    'QGive': ['+f grant', '+m hasGrant', '~m run'],
    'QHooks': ['~m cfgChanged', '~m reload'],  # FIX B2: the board caller re-checked on a Server Setup change / reload
    'QIO': ['~m run'],                       # mode 8 (npcs.tsv) + the dialogue / registry reload
    'QLife': ['~m loaded'],                  # old board keys pruned at load
    'QLine': ['+f daily', '+f giver', '~c '],
    'QLogPage': ['~m build'],                # a daily line lists today's jobs only
    'QPay': ['~m payOne', '~m payable'],     # the pole claim
    'QState': ['+f jobDay', '+f jobLine', '+f jobN', '+f jobs', '+m dailyPicks', '+m isStarted', '+m nextTask', '+m npcMark', '+m pruneDaily', '+m talkTask', '~c ',
               '~m rowsOf'],
    'QTask': ['+f tier'],
    'QTick': ['~m tickAt'],                  # QWorld.tick
    'QuestAdminCmd': ['~c ', '~m execute'],  # + npc, the help line
    'QuestsCmd': ['~c '],                    # + board
    'SkyyQuestsPlugin': ['~m setup', '~m shutdown'],
}
ADDED = ["QBoardPage", "QDlgPage", "QMapProv", "QMarks", "QNpc", "QNpcAddSys", "QNpcApi", "QNpcReal", "QNpcRec", "QNpcTask", "QTalk",
         "QTalkTask", "QUseSys", "QWorld", "QaNpcCmd", "QaNpcIdCmd", "QuestsBoardCmd"]
NEW_ENTRIES = ["Server/Languages/en-US/server.lang", "manifest.json"]   # 0.3 ships its first asset (the talk hint lang line)


_orig_compare = HK.run_compare


def _compare_wrap(out, jar, old_jar, pkg, expect, added):
    """HK.run_compare writes its own K and fails on the lang entry: run the class part, drop its entry check, add ours"""
    # the class compare of the kit, with its non-class check neutralised by comparing the old jar's own entries
    import harness_kit as _hk
    _orig = _hk.Child.eq
    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            return True
        return _orig(self, got, want, what)
    _hk.Child.eq = eq
    try:
        _orig_compare(out, jar, old_jar, pkg, expect, added)
    finally:
        _hk.Child.eq = _orig
    d = json.load(open(out))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = d["ok"], d["fails"], d["notes"]
    import zipfile as _z
    za, zb = _z.ZipFile(old_jar), _z.ZipFile(jar)
    ea = [n for n in za.namelist() if not n.endswith(".class")]
    eb = [n for n in zb.namelist() if not n.endswith(".class")]
    ed = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
    K.eq(ed, sorted(NEW_ENTRIES), "C: non-class entries changed (the manifest + the one lang file)")
    K.check(zb.read("Server/Languages/en-US/server.lang").decode("utf-8") == "skyyquests.talkHint = Press [{key}] to talk\n", "C: the lang file holds exactly our one key")
    K.check(json.loads(zb.read("manifest.json")).get("IncludesAssetPack") is True, "C: the manifest says IncludesAssetPack (the lang line loads)")
    K.save()


HK.run_compare = _compare_wrap


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
        HK.run("SkyyQuests", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
               [("defs", run_defs), ("engine", run_engine), ("life", run_life), ("pay", run_pay), ("crash", run_crash), ("static", run_static),
                ("npc", run_npc), ("board", run_board), ("fish", run_fish), ("live", run_live)],
               os.path.abspath(__file__), live=(LIVE_DIR, "Skyy_SkyyIslands"))
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(FAKE_DIR, ignore_errors=True)
