"""SkyyClasses 0.1.30 - harness for MODIFIERS OUT OF THE TREE + EVERY ABILITY SAYS WHAT IT DOES (tools/classes_0_1_30_patch.py). Build first:
python tools/classes_0_1_30_patch.py && python SkyyClasses/build_skyyclasses_0.1.30.py

    python SkyyClasses/test_skyyclasses_0.1.30.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch. Live save data (the test world's
Skyy_SkyyClasses) is only READ - copied into scratch first. (The page side - SkyyTrees 0.3.18 calling class:fn:abilDoes / abilMods - is
EXECUTED by SkyyTrees/test_skyytrees_0.3.18.py with both jars in one JVM.)
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.29 -> 0.1.30: exactly the members of EXPECT differ; + AbilDoes, AbilDoesFn, AbilMig3
  X    EXECUTED (bare JVM, the real config / stores in scratch, bridge stand-ins for SkyySkills / SkyyProfiles):
       DOES  every ability's AbilDoes.info: what it does = the DOES template of the build script with the LIVE AbilCfg / AbilNum values
             (read from the JVM) put in, the walking cost line, the level line; a changed Server Setup number shows at once; the bridge
             Function (String / Object[] / unknown / null)
       MOD   modifiers unlock by ability level with class trees on: Abil.modOk ignores modifier node ids, modRows answers the unlock
             level + "unlocks at <Ability> Lv N", equipMod / holdText / the rebirth pick refuse a locked one with the level, newMods
             names the new modifier again; tree:reads:SkyyClasses lists no modifier node
       MIG3  the one-time slot check: a profile file with modifiers above / below their unlock level (slots 1-4) -> a verified History
             copy (byte-identical), ONE write (only the dropped slots + abil.tree3=done), the change-log line (Undo), the chat text naming
             each modifier + its level; run again = nothing; nothing to drop = nothing written; a blocked History copy = nothing changes
             (null, retried); consider(): the player's chat line once (SEEN), a loading profile (profile:busy) waits
  LIVE start twice on a scratch COPY of the live Skyy_SkyyClasses: ClassCfg.load + both config migrations twice = no byte changes; the slot
       check over every live ability file twice: the second run changes nothing; every modifier the level allows stays slotted
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, ast, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import deploy_set as DS

VERSION = "0.1.30"
PKG = "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-0.1.29.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "cls0130", "hc")))
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyClasses")
SCRIPT = os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION)
ADDED = ["AbilDoes", "AbilDoesFn", "AbilMig3"]
EXPECT = {}   # filled from the first compare run (see the bottom)


def does_table():
    """the DOES dict literal of the build script (ast - nothing of the build runs)"""
    t = ast.parse(open(SCRIPT, encoding="utf8").read())
    for n in t.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "DOES":
            return ast.literal_eval(n.value)
    raise SystemExit("no DOES table in " + SCRIPT)


# ======================================================================================================== X
def run_x(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JObject, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    C = lambda n: JClass(PKG + n)
    Cfg, Store, AS, A, AD, AMD, Doc, Mig3 = C("ClassCfg"), C("ClassStore"), C("AbilStore"), C("Abil"), C("AbilDefs"), C("AbilModDefs"), C("AbilDoes"), C("AbilMig3")
    Paths, Integer, Long, UUID, ArrayList = JClass("java.nio.file.Paths"), JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.util.UUID"), JClass("java.util.ArrayList")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyClasses")
    home = os.path.join(scratch, "x-home")
    os.makedirs(os.path.join(home, "players"), exist_ok=True)
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    K.notes.append("config: " + str(Cfg.load())[:100])
    Store.DIR = Paths.get(os.path.join(home, "players"))
    AS.DIR = Paths.get(os.path.join(home, "abilities"))
    AS.SYNC = True
    SAID = ArrayList()
    A.SAID = SAID
    br = Cfg.bridge()

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    LV = {"lvl": 30}
    br.put("skill:fn:level", Fn(lambda o: Integer.valueOf(LV["lvl"])))
    br.put("skill:fn:combat", Fn(lambda o: Long.valueOf(0)))
    me = UUID(0x7ee5, 3130)
    km = str(me)

    def setcls(cn):
        br.put("profile:" + km, "1")
        br.put("profile:class:" + km, cn)
        br.put("class:" + km, cn)
    setcls("Mage")
    IDS = [str(x) for x in AD.IDS]
    NAMES = [str(x) for x in AD.NAMES]

    # ------------------------------------------------------------------ DOES
    tab = does_table()
    K.eq(sorted(tab), sorted(IDS), "DOES: one text per ability")
    Num, Cfa, Mth = C("AbilNum"), C("AbilCfg"), C("AbilMath")
    Num.sync()

    def want(tx):
        def sub(m):
            f, k = m.group(1), m.group(2)
            hold = Num if hasattr(Num, f) else Cfa
            v = float(getattr(hold, f)) * (float(k) if k else 1.0)
            return str(Doc.n(v))
        return re.sub(r"\{([A-Z0-9_]+)(?:\*([0-9.]+))?\}", sub, tx)
    bad = []
    for ai, aid in enumerate(IDS):
        inf = Doc.info(aid)
        if inf is None or len(inf) != 4:
            bad.append((aid, "no info"))
            continue
        nm, dz, cost, grow = [str(x) for x in inf]
        if nm != NAMES[ai] or dz != want(tab[aid]) or "{" in dz or not re.search(r"\d", dz):
            bad.append((aid, dz[:80], want(tab[aid])[:80]))
        if not (("Mana" in cost and "cooldown" in cost) or cost.startswith("Passive")):
            bad.append((aid, "cost", cost))
        if not grow.startswith("Levels by use: +") or str(AD.NOUN[ai]) not in grow:
            bad.append((aid, "grow", grow))
    K.check(not bad, "DOES: every ability (%d): its sentence = the template with the live AbilCfg / AbilNum numbers, a cost line, a level line: %s" % (len(IDS), bad[:3]))
    m0 = [str(x) for x in Doc.info("Meteor")]
    K.notes.append("DOES Meteor: " + " | ".join(m0))
    K.check(m0[1] == "A meteor falls where you look (up to 25 blocks) 1 s later and hits every enemy within 4 blocks for 3x one staff hit."
            and m0[2] == "23 Mana + 2 Stamina - cooldown 14 s" and m0[3] == "Levels by use: +2 % damage a level (half after Lv 10, a quarter after Lv 20; top Lv 25).",
            "DOES: Meteor at the defaults: %s" % m0)
    old_r = float(Cfa.M_RADIUS)
    Cfa.M_RADIUS = 6.5
    K.check("within 6.5 blocks" in str(Doc.info("Meteor")[1]), "DOES: a changed Server Setup number (ab.Meteor.radius 6.5) shows at once")
    Cfa.M_RADIUS = old_r
    sa = [str(x) for x in Doc.info("ShieldShockwave")]
    ab = [str(x) for x in Doc.info("ArcaneBreach")]
    K.check(sa[1].startswith("A 90-degree cone 6 blocks") and ab[1].startswith("A 180-degree arc 5 blocks") and "+3 Momentum" in ab[1],
            "DOES: angles are the full cone / arc (2 x the half angle the code compares with): %s / %s" % (sa[1][:40], ab[1][:40]))
    gs = [str(x) for x in Doc.info("GuardianSpirit")]
    K.check(gs[2].startswith("Passive - always on - 15 Mana + 1 Stamina a save") and gs[1].startswith("Passive, always on"), "DOES: the passive's cost line: %s" % gs[2])
    fn = C("AbilDoesFn")()
    r1, r2 = fn.apply("Toxin"), fn.apply(JArray(JObject)([JString("Toxin")]))
    K.check(r1 is not None and r2 is not None and str(r1[1]) == str(r2[1]) and fn.apply("Nope") is None and fn.apply(None) is None,
            "DOES: class:fn:abilDoes takes the id as a String or Object[]{id}; unknown / null -> null")
    for ai, aid in enumerate(IDS):
        K.notes.append("DOES %s: %s || %s || %s" % ((aid,) + tuple(str(x) for x in Doc.info(aid))[1:]))

    # ------------------------------------------------------------------ MOD
    met = IDS.index("Meteor")
    K.check(not bool(A.modOk("A1,A1.Power,A1.Radius", met, 0, 1)) and bool(A.modOk("A1", met, 0, 2)) and not bool(A.modOk("A1", met, 1, 3))
            and bool(A.modOk("A1", met, 1, 4)) and bool(A.modOk(None, met, 1, 4)), "MOD: modOk = the ability level (2 / 4 ...), modifier node ids in the tree list do nothing")
    K.check(str(A.newMods(met, 1, 2)) == "Power+" and str(A.newMods(met, 3, 6)) == "Radius+, Split", "MOD: newMods names the modifiers a level-up unlocks")
    AS.set(km, JArray(JString)(["u.Meteor", "p1", "alt"]), JArray(JString)(["30", "Meteor", "A"]))   # 30 uses = Lv 2 (AbilMath.levelOf)
    lvl = int(A.alvlk(km, 30))
    csv = "ROOT,A1"
    rows = [str(x) for x in A.modRows(me, "Meteor", csv)]
    f = [r.split("|") for r in rows[1:]]
    K.check(lvl == 2 and [x[0] for x in f] == ["Power", "Radius", "Split", "Lingering", "Echo"] and [x[2] for x in f] == ["2", "4", "6", "8", "10"]
            and [x[3] for x in f] == ["1", "0", "0", "0", "0"], "MOD: modRows (Lv %d): unlock levels 2/4/6/8/10, Power+ unlocked only: %s" % (lvl, [(x[0], x[2], x[3]) for x in f]))
    K.check(f[1][9] == "unlocks at Meteor Lv 4" and f[1][10] != "" and "class tree" not in rows[2], "MOD: a locked modifier says where it unlocks: %s / %s" % (f[1][9], f[1][10]))
    r = str(A.equipMod(me, "Meteor", 1, "Radius", csv, True))
    K.check(r == "-Radius+ unlocks at Meteor Lv 4 (Lv 2 now) - use Meteor to level it.", "MOD: equipMod refuses a locked modifier with its level: %s" % r)
    r = str(A.equipMod(me, "Meteor", 0, "Power", csv, True))
    K.check(r.startswith("+Meteor: slot 1 Power+") and str(AS.load(km).getProperty("e.Meteor")) == "Power,", "MOD: an unlocked one equips (no node needed): %s" % r)
    ci = int(Store.classIndex(me))
    r = str(A.holdText(me, ci, "Meteor", "Split", csv))
    K.check(r == "-Split unlocks at Meteor Lv 6 (Lv 2 now) - use Meteor to level it.", "MOD: holdText refuses a locked modifier with its level: %s" % r)
    r = str(A.holdText(me, ci, "Meteor", "Power", csv))
    K.check(r.startswith("Ability: holding Power+"), "MOD: holdText holds an unlocked one: %s" % r)
    AS.set(km, JArray(JString)(["rb.pick.Meteor"]), JArray(JString)(["1"]))
    r = str(A.rbPick(me, "Meteor", "Split"))
    K.check(r == "-That modifier is still locked - it unlocks at Meteor Lv 6.", "MOD: the rebirth pick refuses a locked modifier with its level: %s" % r)
    import zipfile
    m_ = re.search(rb"Class\.Mage\.A1[ -~]*", zipfile.ZipFile(jar).read("com/skyy/classes/SkyyClassesPlugin.class"))
    reads = m_.group(0).decode() if m_ else ""
    K.check("Class.Mage.A1" in reads and "Class.Mage.A4b" in reads and ".Power" not in reads and ".Echo" not in reads,
            "MOD: tree:reads:SkyyClasses lists the ability nodes, no modifier node: %s..." % reads[:80])
    pan = A.panel(me, csv, True)
    K.check(len(pan) == 129 and str(pan[0]) == "ok", "MOD: the panel keeps its 129 fields (SkyyTrees / SkyyMenu)")

    # ------------------------------------------------------------------ MIG3
    adir = os.path.join(home, "abilities")
    k2 = "mig3-a"
    body = ("#SkyyClasses abilities\r\nu.Meteor=20\r\ne.Meteor=Power,Radius\r\ne2.Meteor=Split\r\nu.ManaBarrier=0\r\ne.ManaBarrier=Power\r\n"
            "e.FrostNova=,Power\r\nu.FrostNova=500\r\nm.Meteor.Radius=7\r\nrb.pick.Meteor=1\r\np1=Meteor\r\n")
    open(os.path.join(adir, k2 + ".properties"), "wb").write(body.encode("latin-1"))
    AS.DATA.remove(k2)
    r = Mig3.check(k2)
    hist = os.path.join(home, "history", "abiltree3", k2 + ".properties")
    p = AS.load(k2)
    disk = open(os.path.join(adir, k2 + ".properties"), "rb").read().decode("latin-1")
    K.check(r is not None and "Radius+ on Meteor (Lv 4)" in str(r) and "Split on Meteor (Lv 6)" in str(r) and "Power+ on Mana Barrier (Lv 2)" in str(r)
            and "Power+ on Meteor" not in str(r) and "Frost Nova" not in str(r), "MIG3: the chat text names each dropped modifier + its level: %s" % r)
    K.check(str(p.getProperty("e.Meteor")) == "Power," and p.getProperty("e2.Meteor") is None and p.getProperty("e.ManaBarrier") is None
            and str(p.getProperty("e.FrostNova")) == ",Power" and str(p.getProperty("m.Meteor.Radius")) == "7" and str(p.getProperty("rb.pick.Meteor")) == "1"
            and str(p.getProperty("abil.tree3")) == "done", "MIG3: only the locked slots left (Power+ Lv 2 stays; use levels + rebirth picks untouched); the marker")
    K.check("abil.tree3=done" in disk and "e.Meteor=Power," in disk, "MIG3: written to disk (one write)")
    K.check(os.path.isfile(hist) and open(hist, "rb").read() == body.encode("latin-1"), "MIG3: the History copy is the untouched file, byte for byte")
    log = open(os.path.join(home, "abiltree3-changes.log"), encoding="utf8").read()
    K.check(log.count("\n") == 1 and "\tmig3-a\tslots\t3 modifier(s) back to the list" in log and "Undo: stop the server, copy history/abiltree3/mig3-a.properties" in log,
            "MIG3: one change-log line with the Undo: %s" % log.strip()[:160])
    K.check(str(Mig3.check(k2)) == "" and open(os.path.join(adir, k2 + ".properties"), "rb").read().decode("latin-1") == disk, "MIG3: a second run = nothing (the marker)")
    k3 = "mig3-b"
    K.notes.append("MIG3: ability levels by uses: %s" % [(u_, int(A.alvlk("x", u_))) for u_ in (13, 30, 100, 300, 1000, 3000, 5000)])
    b3 = "u.Meteor=5000\ne.Meteor=Radius,Echo\n"
    open(os.path.join(adir, k3 + ".properties"), "wb").write(b3.encode("latin-1"))
    AS.DATA.remove(k3)
    r3 = Mig3.check(k3)
    AS.save(k3)
    d3 = open(os.path.join(adir, k3 + ".properties"), "rb").read().decode("latin-1")
    h3 = os.path.join(home, "history", "abiltree3", k3 + ".properties")
    K.check(str(r3) == "" and "abil.tree3=done" in d3 and "e.Meteor=Radius,Echo" in d3 and "u.Meteor=5000" in d3
            and os.path.isfile(h3) and open(h3, "rb").read() == b3.encode("latin-1"),
            "FIX2: nothing to drop (Lv %d) = the run-once marker alone (slots + uses kept), after a byte-exact History copy" % int(A.alvlk(k3, 5000)))
    log3 = open(os.path.join(home, "abiltree3-changes.log"), encoding="utf8").read()
    K.check(log3.count("\n") == 2 and "\tmig3-b\tslots\tnothing to move back" in log3, "FIX2: ... one change-log line with the Undo for it")
    AS.DATA.remove(k3)
    K.check(str(Mig3.check(k3)) == "" and open(os.path.join(adir, k3 + ".properties"), "rb").read().decode("latin-1") == d3
            and open(os.path.join(home, "abiltree3-changes.log"), encoding="utf8").read() == log3, "FIX2: ... a second run = nothing (the marker)")
    k7 = "mig3-nofile"
    AS.DATA.remove(k7)
    K.check(str(Mig3.check(k7)) == "" and not os.path.exists(os.path.join(adir, k7 + ".properties")), "FIX2: no ability file yet = nothing written (no empty file made)")
    k4 = "mig3-c"
    b4 = "u.Meteor=0\ne.Meteor=Power\n"
    open(os.path.join(adir, k4 + ".properties"), "wb").write(b4.encode("latin-1"))
    os.makedirs(os.path.join(home, "history", "abiltree3", k4 + ".properties"))   # a blocked History copy
    AS.DATA.remove(k4)
    K.check(Mig3.check(k4) is None and open(os.path.join(adir, k4 + ".properties"), "rb").read().decode() == b4 and AS.load(k4).getProperty("abil.tree3") is None,
            "MIG3: a blocked History copy = nothing changes (null: tried again)")
    os.rmdir(os.path.join(home, "history", "abiltree3", k4 + ".properties"))
    K.check("Power+ on Meteor (Lv 2)" in str(Mig3.check(k4)), "MIG3: ... the next try updates it")
    # fix round checks
    K.check("AP" not in str(r) and "Ability Point" in str(r) and "gave back" not in str(r), "FIX: the slot check's chat line no longer claims AP came back (SkyyTrees says it): %s" % r)
    ACfg = C("AbilCfg")
    k6 = "mig3-lvloff"
    b6 = "u.Meteor=0\ne.Meteor=Power,Radius\ne2.Meteor=Echo\n"
    open(os.path.join(adir, k6 + ".properties"), "wb").write(b6.encode("latin-1"))
    AS.DATA.remove(k6)
    ACfg.LEVELS = False
    try:
        lo_ok = bool(A.modOk(None, met, 4, 1)) and bool(A.modOk("A1", met, 1, 1))
        lo_r = Mig3.check(k6)
        lo_disk = open(os.path.join(adir, k6 + ".properties"), "rb").read().decode()
        lo_p = AS.load(k6)
    finally:
        ACfg.LEVELS = True
    K.check(lo_ok and str(lo_r) == "" and lo_disk == b6 and lo_p.getProperty("abil.tree3") is None
            and not os.path.exists(os.path.join(home, "history", "abiltree3", k6 + ".properties")),
            "FIX: abil.levels OFF = every modifier open (modOk) and the slot check keeps every slotted one, writes nothing, no marker (%r)" % (str(lo_r),))
    K.check(not bool(A.modOk(None, met, 4, 1)), "FIX: ... levels back ON = the level rule again")
    p_old = AS.load(k3)
    K.check(bool(AS.set(k3, ["x.click"], ["1"])) and not bool(AS.setIf(k3, p_old, ["x.mig"], ["1"])) and AS.load(k3).getProperty("x.mig") is None
            and bool(AS.setIf(k3, AS.load(k3), ["x.mig"], ["1"])) and str(AS.load(k3).getProperty("x.click")) == "1",
            "FIX: AbilStore.setIf refuses lines changed since they were read (a loadout click in between) and writes onto fresh ones")
    sb_ = str(Doc.info("ShieldBubble")[1])
    ff_ = str(Doc.info("FlowingForm")[1])
    K.check("When it drops to 75, 50 and 25 % and when it breaks, everyone inside heals 8 % of max Health." in sb_
            and "Awed: they take more damage the higher your combo. Awe lasts 10 s after they leave." in ff_,
            "FIX: the two hard sentences are split: %s || %s" % (sb_, ff_))
    # consider(): the player's chat line once; profile:busy waits
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    pr = U.allocateInstance(PRef.class_)
    fu = PRef.class_.getDeclaredField("uuid")
    fu.setAccessible(True)
    p5 = UUID(0x7ee5, 3131)
    fu.set(pr, p5)
    open(os.path.join(adir, str(p5) + ".properties"), "w").write("u.Toxin=0\ne.Toxin=Radius\n")
    br.put("profile:busy:" + str(p5), "1")
    SAID.clear()
    K.check(int(Mig3.consider(pr)) == -1 and SAID.size() == 0, "MIG3: a loading profile (profile:busy) waits")
    br.remove("profile:busy:" + str(p5))
    a1 = int(Mig3.consider(pr))
    said = [str(x) for x in SAID]
    a2 = int(Mig3.consider(pr))
    K.check(a1 == 1 and a2 == -1 and len(said) == 1 and said[0].startswith("Modifiers now unlock by themselves") and "Radius+ on Toxin (Lv 2)" in said[0],
            "MIG3: consider() sends the chat line once (%s / %s): %s" % (a1, a2, said))
    K.save()
    sys.stdout.flush()
    os._exit(0)


# ======================================================================================================== LIVE: start twice on a copy
def run_live(out, jar, scratch, home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    C = lambda n: JClass(PKG + n)
    Cfg, Store, AS, Mig3, A = C("ClassCfg"), C("ClassStore"), C("AbilStore"), C("AbilMig3"), C("Abil")
    Paths = JClass("java.nio.file.Paths")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyClasses")

    def snap(d):
        o = {}
        for r, _ds, fs in os.walk(d):
            for f in fs:
                p = os.path.join(r, f)
                o[os.path.relpath(p, d)] = open(p, "rb").read()
        return o
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    Store.DIR = Paths.get(os.path.join(home, "players"))
    AS.DIR = Paths.get(os.path.join(home, "abilities"))
    AS.SYNC = True
    s0 = snap(home)
    for i in range(2):
        Cfg.load()
        for mname in ("migrate0110", "migrate0129"):
            if hasattr(Cfg, mname):
                try:
                    getattr(Cfg, mname)()
                except Exception as e:
                    K.notes.append("%s: %s" % (mname, str(e)[:120]))
        Cfg.load()
        s1 = snap(home)
        K.check(sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k)) == [], "LIVE: config start %d on the copy changes nothing" % (i + 1))
    files = sorted(f[:-11] for f in os.listdir(os.path.join(home, "abilities")) if f.endswith(".properties")) if os.path.isdir(os.path.join(home, "abilities")) else []
    for k in files:
        raw = open(os.path.join(home, "abilities", k + ".properties"), "rb").read().decode("latin-1")
        AS.DATA.remove(k)
        r1 = Mig3.check(k)
        after = open(os.path.join(home, "abilities", k + ".properties"), "rb").read().decode("latin-1")
        AS.DATA.remove(k)
        r2 = Mig3.check(k)
        after2 = open(os.path.join(home, "abilities", k + ".properties"), "rb").read().decode("latin-1")
        K.check(r1 is not None and str(r2) == "" and after2 == after, "LIVE %s: the slot check runs, the second run changes nothing (%s)" % (k[:13], str(r1)[:200]))
        eq0 = sorted(l for l in raw.splitlines() if re.match(r"e2?\.", l))
        eq1 = sorted(l for l in after.splitlines() if re.match(r"e2?\.", l))
        K.notes.append("LIVE %s: slots before %s after %s; %s" % (k[:13], eq0, eq1, str(r1)[:160]))
    K.check(len(files) >= 1, "LIVE: %d live ability file(s) checked on the copy" % len(files))
    K.save()
    sys.stdout.flush()
    os._exit(0)


EXPECT = {
    "Abil": ["~m holdText", "~m equipMod", "~m modOk", "~m modRows", "~m rbPick", "~m used"],
    "AbilSave": ["+m histCopyIn", "~m histCopy", "-m histCopy0", "+m histCopy0"],
    "ClassTick": ["~m run"],
    "AbilStore": ["+m setIf"],   # fix round: the slot check's compare-and-set
    "SkyyClassesPlugin": ["~m setup", "~m shutdown"],
    "CfgRows2": ["~<clinit>"],   # the abil.treeGate / mods.unlock help texts
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"],
}

if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("x", run_x), ("live", run_live)], script=__file__, live=(LIVE, "Skyy_SkyyClasses"))
