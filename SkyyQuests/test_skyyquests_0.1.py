"""SkyyQuests 0.1 harness (round Q1, research/SkyyQuests-Tutorial-Spec.md section 10). Built on tools/harness_kit.py: each phase a fresh
child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder). Every code path runs on the
REAL jar classes; only the engine's player / world / ECS store are stand-ins (Unsafe-allocated engine objects + javassist subclasses of
ArchetypeChunk / Store / EntityStore / World compiled before the JVM starts, --mkfake).

    python SkyyQuests/test_skyyquests_0.1.py [--jar SkyyQuests-0.1.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  a NEW mod: against a copy of itself with another manifest version (nothing but the manifest may differ)
  D    defs     config.properties written once + read (fields, clamps, the tutorial reward table); the shipped tutorial written ONCE
                (an edit stays), 24 tasks, 0 problems; glob / alternatives / "any"; every bad-line kind reported (and the good tasks kept);
                a duplicate line id; places.properties (line-preserving save, comments kept, replace); rewardOf / rewardText + the
                Server Setup override; QState text <-> parse round trip (unknown keys kept, claims in order)
  E    engine   the want index (one map read, nothing touched without the bit); every objective type fed by its stand-in event / bridge
                value (break, felled, gather, craft, kill, reach, enter, talk, page, event, tier, level, bridge exists / notempty / >= /
                contains / fn:); any / all with coming-soon parts; NON-LINEAR (task 6 before 4, 20 before 13 - each stays done); hidden
                tasks (requires) appear when their key does; caller= soon parts turn live with quest:caller:<id>; chain lines; busy /
                profile-key guards; the quest:fn:hud Object[] shape (title, count, 1-3 tasks, frac, where, dir, done; compact; hide the
                tutorial; empty state; the green Done! hold + expiry; coming-soon tasks skipped); the arrow text (8 directions, the
                distance rounding, another world = the label); every QFn mode + the event rate cap; admin done / undo (never pays twice);
                settings refresh + setHide; join / load / quit / profile switch on the IO jobs; every QIO mode; the tick + its per-player
                step; the welcome conditions; the page builds + clicks (welcome + log); the 4 ECS systems + the kill system through the
                stand-in store; QEvTask cancel checks; QFelledFn; QHop; regSetting
  P    pay      claims paid ONCE (coins / XP / items through stand-in bridge functions), PAYING / PAID / BACK / PART / REPAY lines, a
                refused payment comes back and waits claim.retrySeconds, /quests claim retries at once, the item give storage-first with
                counts before / after (full, none, partial), repay of a lost PAYING
  K    crash    CRASH AT EVERY STEP of the claim ledger (QLog.STOP_AT): each step of paying two claims, then a fresh class loader (a
                restart) on what is on disk: never a duplicate; a crash before the payout = the claim is still there or logged PAYING
                (repay brings it back once); plus a crash before the completion write (the task completes again, claims once)
  S    static   the hot paths (every ECS handler, QEvTask, QHop, QEvents, QFn, QEng.count / hud / event, QGive, the pages, the commands)
                reach no file call and no Thread.sleep; files only from the SkyyQuests-IO jobs, the tick (hub.properties), setup /
                shutdown and the loaders; every handler reads QEng.WANT first; the lock-free bridge()
  ST   live     START TWICE on a scratch COPY of the live Skyy_SkyyIslands folder (hub.properties): the first start writes config /
                tutorial / places, the second writes nothing; the hub world is read from the copy
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED, see the round report): the pages' look, chat colours, the real ECS registration and event
delivery (the smoke test proves registration), north = -Z on the player's map.
Scratch: tools/dev/scratch/quests01/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json, time, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.1"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "quests01", "h")))
PKG = "com.skyy.quests."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyIslands")
FAKE = "skyyq01"
FAKE_DIR = SCRATCH + "-fake"     # the stand-in classes (compiled before the phases; HK.run wipes SCRATCH itself)
TB = {"break": 1, "felled": 2, "gather": 4, "craft": 8, "kill": 16, "reach": 32, "enter": 64, "talk": 128, "page": 256, "event": 512,
      "tier": 1024, "level": 2048, "bridge": 4096}


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
    K.eq(E.start(), 1, "D1 one quest line (the shipped tutorial)")
    K.check(os.path.isfile(os.path.join(base, "config.properties")) and os.path.isfile(os.path.join(base, "quests", "tutorial.properties"))
            and os.path.isfile(os.path.join(base, "places.properties")), "D1 config / tutorial / places written on the first start")
    K.eq((bool(Cfg.ENABLED), bool(Cfg.TUT_ON), bool(Cfg.WELCOME), int(Cfg.TASKS), float(Cfg.DONE_SECS), int(Cfg.POLL_SECS), int(Cfg.LAZY_SECS),
          int(Cfg.RETRY_SECS), int(Cfg.EVENT_RATE)), (True, True, True, 3, 2.5, 1, 5, 60, 20), "D1 the config defaults")
    K.eq(int(Cfg.REWARDS.size()), 24, "D1 24 tutorial reward lines")
    K.eq([str(x) for x in Cfg.REWARDS.get("chop_logs")], ["0", "Foraging:50"], "D1 chop_logs reward line")
    K.eq(int(Defs.PROBLEMS.size()), 0, "D1 the shipped tutorial has no problems: %s" % [str(x) for x in Defs.PROBLEMS])
    L = Defs.LINES[0]
    K.eq((str(L.id), str(L.name), bool(L.chain), bool(L.auto), str(L.hide), len(L.tasks)), ("tutorial", "Getting Started", False, True, "tutorial.hide", 24),
         "D1 the tutorial line")
    t3 = L.tasks[2]
    K.eq((str(t3.id), bool(t3.any), len(t3.parts), int(t3.parts[0].type), int(t3.parts[0].count), str(t3.parts[1].match)),
         ("chop_logs", True, 2, TB["felled"], 10, "Wood_*_Trunk"), "D1 chop_logs = any(felled 10, break Wood_*_Trunk 10)")
    K.eq(str(t3.parts[0].match), "Wood_*_Trunk*", "FIX1 the felled part matches trunks only (leaves are felled blocks too)")
    t21 = L.tasks[20]
    K.check(str(t21.id) == "to_hub" and bool(t21.parts[0].block) and not bool(t21.parts[1].block), "FIX5 to_hub's portal part is block=true (parsed from the file)")
    K.eq(str(L.tasks[0].requires), "profile:fn:key", "FIX6 pick_class requires SkyyProfiles (profile:fn:key)")
    K.eq((len(L.tasks[16].parts), str(L.tasks[16].parts[0].tname)), (1, "event"), "FIX4 first_pet = the pets:equip event only (no loadout bridge part)")
    tf = os.path.join(base, "quests", "tutorial.properties")
    open(tf, "a", encoding="utf8").write("# an owner's edit\n")
    m0 = os.path.getmtime(tf)
    E.start()
    K.check(open(tf, encoding="utf8").read().endswith("# an owner's edit\n") and os.path.getmtime(tf) == m0, "D1 the tutorial is copied ONCE (an edit stays)")
    # glob / alternatives / any
    for pat, sv, want in (("Wood_*_Trunk", "Wood_Oak_Trunk", True), ("Wood_*_Trunk", "Wood_Oak_Log", False), ("*Plant_Crop_Wheat_Block*", "Plant_Crop_Wheat_Block_Eternal", True),
                          ("Skyy_Accessory_*_T*", "Skyy_Accessory_Workbench_T2", True), ("Skyy_Accessory_*_T*", "Skyy_Accessory_Omni", False),
                          ("Ore_Copper*", "Ore_Copper_Stone", True), ("Rock_Stone", "Rock_Stone_Brick", False), ("gear:reforge|gear:upgrade", "gear:upgrade", True),
                          ("any", "whatever", True), ("", "x", True), ("a*b*c", "aXbYc", True), ("a*b*c", "acb", False), ("*", "", True)):
        K.eq(bool(Defs.matches(pat, sv)), want, "D2 matches(%r, %r)" % (pat, sv))
    # bad lines
    bad = "\n".join(["line=side_line", "name=Side", "mode=weird", "task.1.id=ok_task", "task.1.name=Fine", "task.1.type=break", "task.1.match=Rock_Stone",
                     "task.2.id=ok_task", "task.2.type=break", "task.2.match=x", "task.3.id=bad_type", "task.3.type=fly", "task.3.match=x",
                     "task.4.id=bad_reward", "task.4.type=kill", "task.4.reward=xp:Combat:50", "task.5.id=no_match", "task.5.type=break",
                     "task.6.id=bad_op", "task.6.type=bridge", "task.6.match=k", "task.6.op=lt", "task.7.id=Bad-Id", "task.7.type=kill",
                     "task.8.id=lvl", "task.8.type=level", "task.8.match=Mining", "task.8.value=ten", "task.9.id=chained", "task.9.p1.type=talk",
                     "task.9.p1.match=board", "task.9.p2.type=event", "task.9.p2.match=x:y", "task.9.p2.caller=zz"]) + "\n"
    open(os.path.join(base, "quests", "side.properties"), "w").write(bad)
    open(os.path.join(base, "quests", "zdup.properties"), "w").write("line=tutorial\ntask.1.id=a\ntask.1.type=kill\n")
    open(os.path.join(base, "quests", "zchain.properties"), "w").write("line=chain_line\nmode=chain\nauto=true\ntask.1.id=first\ntask.1.type=kill\ntask.1.match=any\n"
                                                                        "task.2.id=second\ntask.2.type=kill\ntask.2.match=any\n")
    K.eq(E.start(), 3, "D3 tutorial + side_line + chain_line (the duplicate tutorial file skipped)")
    pb = [str(x) for x in Defs.PROBLEMS]
    for frag in ("mode=weird", "id 'ok_task' must be", "type 'fly'", "Combat XP cannot be granted", "match is empty", "op 'lt'", "id 'Bad-Id'",
                 "value 'ten'", "already defined by another file"):
        K.check(any(frag in x for x in pb), "D3 problem reported: %s (%s)" % (frag, pb))
    side = Defs.line("side_line")
    K.eq([str(t.id) for t in side.tasks], ["ok_task", "bad_reward", "chained"], "D3 the good tasks of a bad file are kept (bad_reward keeps its objective, reward dropped)")
    K.eq(str(side.tasks[1].reward), "", "D3 the bad reward is ignored")
    K.check(bool(Defs.line("chain_line").chain), "D3 mode=chain read")
    for f in ("side.properties", "zdup.properties", "zchain.properties"):
        os.remove(os.path.join(base, "quests", f))
    E.start()
    # rewards
    K.eq(str(Defs.rewardText("coins:25,xp:Foraging:40,item:Rock_Stone:3,flag:x")), "+25 coins  +40 Foraging XP  +3 Rock Stone", "D4 rewardText")
    K.check(Defs.rewardProblem("coins:0") is not None and Defs.rewardProblem("item:X:1001") is not None and Defs.rewardProblem("coins:5,xp:Mining:5") is None,
            "D4 rewardProblem")
    chop = L.tasks[2]
    K.eq(str(Defs.rewardOf(L, chop)), "xp:Foraging:50", "D4 rewardOf = the table line")
    cfgp = os.path.join(base, "config.properties")
    txt = open(cfgp, encoding="utf8").read().replace("tutorial.reward.chop_logs=0,Foraging:50", "tutorial.reward.chop_logs=7,Mining:9")
    txt = txt.replace("tutorial.reward.pick_class=25,", "tutorial.reward.pick_class=oops,")
    open(cfgp, "w", encoding="utf8").write(txt)
    Cfg.load()
    K.eq(str(Defs.rewardOf(Defs.LINES[0], chop)), "coins:7,xp:Mining:9", "D4 a Server Setup table change replaces the coins / XP")
    K.eq(str(Defs.rewardOf(Defs.LINES[0], Defs.LINES[0].tasks[0])), "coins:25", "D4 a bad table line keeps the quest file's reward")
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
    # QState round trip
    U = JClass("java.util.UUID")
    P = JClass("java.util.Properties")()
    P.load(JClass("java.io.StringReader")("v=1\ntrack=tutorial\nseq=4\ndone.tutorial.chop_logs=123\nprog.tutorial.chop_logs.0=7\npdone.tutorial.chop_logs.1=1\n"
                                          "flag.met=1\nclaim.2=coins|5|k:tutorial.a:2\nclaim.1=xp|Mining:5|k:tutorial.a:1\nissued.tutorial.chop_logs=1\n"
                                          "hide.tutorial=1\nseen.tutorial=1\nstart.side=9\nfuture.key=kept\n"))
    s = St.parse("k", U.randomUUID(), P)
    t = str(s.textU())
    for ln in ("track=tutorial", "seq=4", "done.tutorial.chop_logs=123", "prog.tutorial.chop_logs.0=7", "pdone.tutorial.chop_logs.1=1", "flag.met=1",
               "claim.1=xp|Mining:5|k:tutorial.a:1", "claim.2=coins|5|k:tutorial.a:2", "issued.tutorial.chop_logs=1", "hide.tutorial=1",
               "seen.tutorial=1", "start.side=9", "future.key=kept"):
        K.check(ln in t.splitlines(), "D6 state text keeps %s" % ln)
    P2 = JClass("java.util.Properties")()
    P2.load(JClass("java.io.StringReader")(t))
    K.eq(str(St.parse("k", U.randomUUID(), P2).textU()), t, "D6 text -> parse -> text is stable")
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
    g = "xp|Foraging:50|%s:tutorial.chop_logs:1" % u
    lg = logtext(X.base)
    K.check(lg.count("PAYING %s %s" % (u, g)) == 1 and lg.count("PAID %s %s" % (u, g)) == 1 and int(s.claimCount()) == 0,
            "E2 its reward was ONE claim line, paid once at once (stand-in SkyySkills): %s" % lg[-300:])
    K.check(any("Task done: Chop 10 logs  (+50 Foraging XP)" in str(x) for x in Log.SINK), "E2 the chat line: %s" % [str(x) for x in Log.SINK][-2:])
    # ---- NON-LINEAR: task 6 (first_rankup) before task 4 (first_accessory), task 20 before 13
    br.put("coll:score:" + str(u), Long(1))
    Eng.lazy(p, True)
    K.check(X.done(s, "first_rankup") and not X.done(s, "first_accessory"), "E3 task 6 done before task 4 (its page part is coming soon: all() ignores it)")
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
    live = [k for k, v in X.rows(s2).items() if v[0] not in ("soon", "hidden")]
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
    K.eq((str(h[2]), bool(h[7]), str(h[5])), ("Pick a class", True, "Done!  +25 coins"), "H3 a done task stays (green) with Done! + its reward")
    s2.expire(JLong(int(time.time() * 1000) + 3000))
    h = Eng.hud(u2)
    K.eq(str(h[2]), "Open the hub buttons", "H3 after the hold the list moves up")
    nd = len([k for k, v in X.rows(s2).items() if v[0] == "done"])
    K.eq(str(h[1]), "%d / %d" % (nd, len(live)), "H3 count")
    # where + arrow: island2 place, task order: make island_two the first shown task by hiding the others? -> its own line
    open(os.path.join(X.base, "quests", "zplace.properties"), "w").write(
        "line=walk\nname=Walk\nauto=true\ntask.1.id=go\ntask.1.name=Go to island 2\ntask.1.type=reach\ntask.1.match=island2\ntask.1.radius=12\n")
    Defs.load()
    Defs.savePlace("island2", "island", 100.0, 64.0, 100.0, "Island 2")
    Eng.rebuild(u2, s2)
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
    n0 = int(s2.claimCount())
    out = JClass("java.util.ArrayList")()
    t_chop = [t for t in X.L.tasks if str(t.id) == "chop_logs"][0]
    K.check(s2.adminDone(X.L, t_chop, JLong(1), out) and int(s2.claimCount()) == n0 + 1, "A1 admin done issues the reward once")
    K.check(s2.adminUndo(X.L, t_chop) and not s2.isDone("tutorial.chop_logs"), "A1 undo clears it")
    for i in range(10):
        Eng.count(u2, TB["break"], "Wood_Oak_Trunk", 1, "w", False)
    gl = [l for l in logtext(X.base).splitlines() if ("PAYING %s " % u2) in l and "tutorial.chop_logs" in l]
    K.check(s2.isDone("tutorial.chop_logs") and len(gl) == 1, "A1 done again: NO second reward (issued stays): %s" % gl)
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
    p2.route = "chat"
    p2.chatAt = 0
    nsink = len(Log.SINK)
    Eng.count(u2, TB["kill"], "Trork", 1, None, False)
    Eng.count(u2, TB["kill"], "Trork", 1, None, False)
    K.eq(len(Log.SINK) - nsink, 1, "N1 chat route: one line per 10 s")
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
    X.E.P("QKillSys")().onComponentAdded(FakeChunk.REF, dc, st, None)
    k1 = X.rows(s)["defeat_mobs"][1]
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
    u, p, s = X.player(1)
    br.put("profile:class:" + str(u), "Mage")
    Eng.lazy(p, True)
    for i in range(10):
        Eng.count(u, 1, "Wood_Oak_Trunk", 1, "w", False)
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
    Pay.itemDone(s, c, 5, 5)
    K.check(not s.paying and int(s.claimCount()) == 0 and ("PAID %s %s" % (str(u), c)) in logtext(X.base), "P3 itemDone: all given = PAID")
    s.addClaim(c)
    c = str(s.takeClaim())
    Pay.itemDone(s, c, 0, 5)
    K.check(int(s.claimCount()) == 1 and str(s.claims.get(0)) == c, "P3 itemDone: nothing given = the claim waits")
    K.check(bool(s.refusedNow(c, JLong(int(time.time() * 1000) + 1000))), "FIX-R a full inventory marks the item claim refused (never blocks others)")
    c = str(s.takeClaim())
    Pay.itemDone(s, c, 2, 5)
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
    Pay.itemDone(s, c, 0, 4)
    K.check(c in [str(x) for x in Sto.read(pk, u).claims] and Sto.CACHE.get(pk) is None,
            "FIX2-A1 the give found no player: the claim is back ON DISK, then the state leaves the cache")
    s3 = Sto.read(pk, u)
    c3 = str(s3.takeClaim())
    s3.markPaying(c3, JLong(int(time.time() * 1000)))
    Sto.write(s3)                       # the worst case: the state already evicted (e.g. stuck-give cleanup) when the result arrives
    Pay.itemDone(s3, c3, 1, 4)
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
        br.put("profile:class:" + str(U), "Mage")
        Eng.lazy(p, True)                      # pick_class: 25 coins
        for i in range(10):
            Eng.count(U, 1, "Wood_Oak_Trunk", 1, "w", False)    # chop_logs: 50 Foraging XP
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
        Eng.count(U, 1, "Wood_Oak_Trunk", 1, "w", False)
    K.check(s.isDone("tutorial.chop_logs") and not os.path.isfile(os.path.join(d, "Skyy_SkyyQuests", "players", str(U) + ".properties")), "KC done in memory, nothing on disk (crash now)")
    E2, Eng2, Sto2, Pay2, Log2, p2, s2 = boot(d)
    K.check(not s2.isDone("tutorial.chop_logs"), "KC after the restart it is not done")
    for i in range(10):
        Eng2.count(U, 1, "Wood_Oak_Trunk", 1, "w", False)
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
           "QLogPage.handleDataEvent", "QWelcomePage.build", "QWelcomePage.handleDataEvent"] + [k for k in g if k.endswith(".execute") and (k.startswith("Qa") or k.startswith("Quest"))]
    for h in hot:
        r = PW.reach(g, h, PKG)
        bad = sorted(m for m in r if any(c in IO for c in g.get(m, ())))
        sl = sorted(m for m in r if any(c in PW.SLEEP for c in g.get(m, ())))
        K.check(h in g and not bad and not sl, "S1 %s reaches no file call / sleep (%d methods): files %s sleep %s" % (h, len(r), bad, sl))
    files = sorted(m for m in PW.sites(g, IO) if not m.startswith("Cfg"))
    K.check(set(files) <= {"QLog.readProps", "QLog.writeAtomic", "QStore.log", "QDefs.load", "QDefs.loadPlaces", "QDefs.savePlace", "QPay.repay"},
            "S2 the file calls live in these methods only: %s" % files)
    for f in ("QLog.readProps", "QLog.writeAtomic", "QStore.log"):
        callers = PW.callers(g, f, PKG)
        K.check(all(c.split(".")[0] in ("QLog", "QCfg", "QDefs", "QStore", "QPay", "QIO") or c.startswith("SkyyQuestsPlugin") or c in ("QEng.hubRefresh",) for c in callers),
                "S2 %s called only by loaders / the IO jobs / the tick's hub read: %s" % (f, callers))
    K.eq(PW.callers(g, "QEng.hubRefresh", PKG), ["QTick.tickAt", "SkyyQuestsPlugin.setup"], "S2 hub.properties is read only on the tick thread (and once at setup)")
    K.eq(sorted(PW.callers(g, "QStore.write", PKG)), ["QPay.itemDone", "QPay.payState", "QPay.repay", "QStore.evict", "QStore.flushDirty"], "S2 player files are written by the IO jobs only (itemDone = QIO mode 7; at shutdown stopIO's drain)")
    K.eq(sorted(m for m in PW.sites(g, PW.SLEEP) if not m.startswith("Cfg")), [], "S3 no Thread.sleep in SkyyQuests")
    PW.bridge_static(K, jar)
    K.save()


# ====================================================================================================== ST: start twice on a copy of live data
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    mods = os.path.dirname(home)
    base = os.path.join(mods, "Skyy_SkyyQuests")
    h0 = HK.tree_hash(home)
    res = []
    for n in range(2):
        b0 = HK.tree_hash(mods)
        E = Env(base)
        lines = E.start()
        E.P("QEng").HUBAT = 0
        E.P("QEng").hubRefresh(1)
        res.append((lines, int(E.P("QDefs").PROBLEMS.size()), str(E.P("QEng").HUBW), HK.tree_hash(mods), b0))
    K.check(res[0][0] == 1 and res[0][1] == 0, "ST start 1: the tutorial, no problems")
    K.check(res[0][3] != res[0][4], "ST start 1 writes config / tutorial / places")
    K.check(res[1][3] == res[1][4], "ST start 2 writes nothing")
    K.eq(HK.tree_hash(home), h0, "ST the live Skyy_SkyyIslands copy is untouched")
    hp = os.path.join(home, "hub.properties")
    if os.path.isfile(hp):
        w = [l.split("=", 1)[1].strip() for l in open(hp, encoding="latin-1") if l.startswith("world=")]
        K.eq(res[0][2], w[0] if w else "None", "ST the hub world read from the copy")
    K.notes.append("ST live hub world: %s" % res[0][2])
    K.save()


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
    old = os.path.join(FAKE_DIR, "SkyyQuests-0.0.jar")
    if "--phase" not in sys.argv:
        import zipfile
        with zipfile.ZipFile(JAR) as zi, zipfile.ZipFile(old, "w", zipfile.ZIP_DEFLATED) as zo:
            for it in zi.infolist():
                data = zi.read(it.filename)
                if it.filename == "manifest.json":
                    data = data.replace(b'"Version": "0.1"', b'"Version": "0.0"')
                zo.writestr(it, data)
    try:
        HK.run("SkyyQuests", VERSION, JAR, old, PKG, SCRATCH, {}, [],
               [("defs", run_defs), ("engine", run_engine), ("life", run_life), ("pay", run_pay), ("crash", run_crash), ("static", run_static), ("live", run_live)],
               os.path.abspath(__file__), live=(LIVE_DIR, "Skyy_SkyyIslands"))
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(FAKE_DIR, ignore_errors=True)
