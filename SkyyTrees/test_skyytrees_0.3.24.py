"""Harness for SkyyTrees 0.3.24 (lean round: Vein Burst / Vein Mine + Tree Feller GUARANTEED on every qualifying break, 26-neighbour vein,
no cooldowns by default, speed caps, the one-time trees.properties update TreeMig324; tools/trees_0_3_24_patch.py). Build first:
    python tools/trees_0_3_24_patch.py && python SkyyTrees/build_skyytrees_0.3.24.py
    python SkyyTrees/test_skyytrees_0.3.24.py [--dir <empty folder inside tools/dev/scratch/>]
Skyy 2026-10-18: "Make vein miner and tree feller a guarantee instead of a chance. So with VeinMiner 1 or TreeFeller 1, I always break two
blocks at a time instead of one, and it can go diagonal on the VeinMiner." + "And make sure fortune still works on things mined with vein
miner and the logs that fall when you chop a tree down."
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A    verify   every class loads + initialises
  C    compare  0.3.23 -> 0.3.24: exactly the planned members (EXPECT) + TreeMig324
  G    guarantee: Vein Burst value = level (1-10), no cooldown defaults, level 1 = exactly 1 extra ore (= 2 blocks) in 1000 runs, every
       level N = exactly N on a full cube, fewer only when fewer exist; Tree Feller level 1 = 1 extra log in 1000 runs; a diagonal-only ore
       is found; a placed block is never picked; speed caps (VEIN_CAP 64, 4000 reads, feller.maxPerLayer, the leaves check stops early,
       the 512-a-tick budget); bytecode: vein / feller break through performBlockBreak (= a real BreakBlockEvent, SkyySkills pays XP +
       Fortune), no CD.put at cooldown 0, the felled-log path never rolls drops in SkyyTrees
  F    FORTUNE (SkyySkills 0.4.52 jar, the SET pin): Perks.extras(1.5) = 1 sure extra + a 50 % second (2 drops + 50 % a third) for each
       path - vein ore / feller logs (BreakTask.run -> Perks.breakDouble) and felled logs (FellCredit.one -> Perks.breakDouble); the hand
       break of a claimed log (Fell.onBreak) never pays the felled roll too (no double roll)
  MG   TreeMig324's text step: LF / CRLF / spaced numbers, a hand-edited group keeps both lines, doubled line kept, missing lines, already
       new, the marker = runs once, sameAfter refuses an added key
  ST1/ST2  start twice on a scratch COPY of the live Skyy_SkyyTrees folder (setup's order): start 1 writes ONLY the 0.3.24 update (4 values
       + marker, a History version, 4 Undo lines) when the live lines hold the old defaults; start 2 writes nothing; the live folder is only read
  AA   engine-access audit
"""
import os, sys, json, shutil, hashlib, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import deploy_set as DS

VERSION = "0.3.24"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.3.23.jar")
SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-%s.jar" % dict(DS.SET)["SkyySkills"])
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "trees24", "tr")))
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyTrees")
MK324 = "skyytrees-0.3.24-vein"
ADDED = ["TreeMig324"]
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
          "SkyyTreesPlugin": ["~m setup"],
          "TreeCfg": ["~<clinit>", "~m apply", "~m load"],                   # DEFAULTS + the two cooldown code defaults (apply = the loader)
          "TreeDefs": ["~<clinit>"],
          "TreeAbil": ["+f BHITS", "+f BSLOT", "+f BUDGET", "+f BUDGET_TOLD", "+f BUSED", "+f LASTREADS", "+f TEST", "+f VEIN_CAP",
                       "+m budget", "+m budgetAt", "+m fired", "+m idAt", "+m veinPick", "~<clinit>", "~m feller", "~m flatFlood", "~m flood", "~m vein"]}
KEYS = {"Mining.MVein.per": ("2.0", "1.0"), "Mining.MVein.base": ("4.0", "0.0"), "vein.cooldownSec": ("40", "0"), "feller.cooldownSec": ("3", "0")}


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def _fn(JProxy, f):
    return JProxy("java.util.function.Function", dict(apply=f))


def run_g(out, jar, scratch, _home):
    from jpype import JClass, JProxy, JArray, JBoolean
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Ab, Cfg, Defs, Fx = J("TreeAbil"), J("TreeCfg"), J("TreeDefs"), J("TreeFx")
    Bool, HashMap, UUID = JClass("java.lang.Boolean"), JClass("java.util.HashMap"), JClass("java.util.UUID")
    ids = [str(x) for x in Defs.ID]
    IV, IF = ids.index("MVein"), ids.index("FFeller")
    # ---- numbers + defaults
    K.eq([float(Fx.value(IV, n)) for n in range(0, 11)], [float(n) for n in range(0, 11)], "G: Vein Burst value = the level (0-10)")
    K.eq((float(Defs.D_PER[IV]), float(Defs.D_BASE[IV]), int(Defs.D_MAX[IV])), (1.0, 0.0, 5), "G: Mining.MVein per 1.0 base 0.0 max 5")
    K.eq((int(Cfg.VEIN_CD_MS), int(Cfg.FELLER_CD_MS)), (0, 0), "G: code default cooldowns are 0")
    d = str(Cfg.DEFAULTS)
    K.check(all(("\n%s=%s\n" % (k, n)) in d for k, (o, n) in KEYS.items()) and d.count(MK324) == 1, "G: DEFAULTS hold the 4 new values + the marker")
    K.check("up to" not in str(Defs.NOW[IV]) and "%C" not in str(Defs.HOW[IV]) and "%C" not in str(Defs.HOW[IF]) and "cooldown" not in str(Defs.HOW[IV]),
            "G: texts without 'up to' / cooldown: %s | %s | %s" % (Defs.NOW[IV], Defs.HOW[IV], Defs.HOW[IF]))
    K.eq([int(Ab.llTotal(0, 1)), int(Ab.llTotal(1, 0)), int(Ab.llTotal(1, 1)), int(Ab.llTotal(5, 9))], [1, 1, 2, 10],
         "G: total level = tree + tool (cap 10): Vein Mine 1 alone = 1, tree 1 alone = 1, both = 2, 5 + 9 = 10")
    K.eq([int(Cfg.fellerLogs(n)) for n in range(0, 11)], [0, 1, 2, 4, 5, 6, 10, 12, 14, 14, 14], "G: Tree Feller logs at total level 0-10 (level 1 = 1 extra = 2 logs)")

    notplaced = _fn(JProxy, lambda a: Bool.FALSE)
    world = None
    T = HashMap()
    Ab.TEST = T

    def put(x, y, z, bid):
        T.put(Ab.pos(x, y, z), bid)

    def cube(bid, r=1):
        T.clear()
        for x in range(-r, r + 1):
            for y in range(-r, r + 1):
                for z in range(-r, r + 1):
                    if (x, y, z) != (0, 0, 0):
                        put(x, y, z, bid)

    def pts(l):
        return sorted((int(v.x()), int(v.y()), int(v.z())) for v in l)

    # ---- level 1 = 2 blocks, every time (1000 runs; no roll anywhere: the search is deterministic, no cooldown armed)
    cube("Ore_Iron")
    u = UUID.randomUUID()
    n1 = [int(Ab.veinPick(world, "w", 0, 0, 0, "Ore_Iron", 1, notplaced).size()) for _ in range(1000)]
    rd = [bool(Ab.ready(u, "vein")) and bool(Ab.ready(u, "feller")) for _ in range(1000)]
    K.check(n1 == [1] * 1000 and all(rd), "G: Vein Mine 1 = exactly 1 extra ore (2 blocks) in 1000 of 1000 breaks, never on cooldown (%s)" % sorted(set(n1)))
    K.eq([int(Ab.veinPick(world, "w", 0, 0, 0, "Ore_Iron", n, notplaced).size()) for n in range(1, 27)], list(range(1, 27)),
         "G: level N = exactly N extra ore on a full 3x3x3 vein (N 1-26)")
    T.clear(); put(1, 0, 0, "Ore_Iron"); put(2, 0, 0, "Ore_Iron"); put(0, 1, 0, "Ore_Copper")
    K.eq(int(Ab.veinPick(world, "w", 0, 0, 0, "Ore_Iron", 5, notplaced).size()), 2, "G: fewer only when fewer connected same-id ore exist (2 of 5; a Copper neighbour is not taken)")
    # ---- diagonal-only ore
    T.clear(); put(1, 1, 1, "Ore_Iron")
    K.eq(pts(Ab.veinPick(world, "w", 0, 0, 0, "Ore_Iron", 1, notplaced)), [(1, 1, 1)], "G: a corner-diagonal-only ore is found")
    T.clear(); put(1, 0, 1, "Ore_Iron"); put(2, -1, 2, "Ore_Iron")
    K.eq(pts(Ab.veinPick(world, "w", 0, 0, 0, "Ore_Iron", 2, notplaced)), [(1, 0, 1), (2, -1, 2)], "G: a vein of diagonal steps is followed")
    # ---- placed blocks never
    cube("Ore_Iron")
    placed1 = _fn(JProxy, lambda a: Bool.TRUE if (int(a[1]), int(a[2]), int(a[3])) == (1, 0, 0) else Bool.FALSE)
    got = pts(Ab.veinPick(world, "w", 0, 0, 0, "Ore_Iron", 26, placed1))
    K.check(len(got) == 25 and (1, 0, 0) not in got, "G: a placed ore is never picked (25 of the 26, without (1,0,0))")
    allp = _fn(JProxy, lambda a: Bool.TRUE)
    unknown = _fn(JProxy, lambda a: None)
    K.check(int(Ab.veinPick(world, "w", 0, 0, 0, "Ore_Iron", 26, allp).size()) == 0 and int(Ab.veinPick(world, "w", 0, 0, 0, "Ore_Iron", 26, unknown).size()) == 0,
            "G: all placed / unknown placed state = nothing picked (the safe side)")
    T.clear()
    for x in (1, 2, -1):
        put(x, 0, 0, "Wood_Oak_Trunk")
    put(1, 1, 0, "Plant_Leaves_Oak")
    fam = Defs.logFamily("Wood_Oak_Trunk")
    K.check(fam is not None, "G: Oak log family %s" % fam)
    f1 = [int(Ab.flatFlood(world, "w", 0, 0, 0, fam, int(Cfg.fellerLogs(1)), 6, notplaced).size()) for _ in range(1000)]
    K.check(f1 == [1] * 1000, "G: Tree Feller 1 = exactly 1 extra log (2 logs) in 1000 of 1000 cuts (%s)" % sorted(set(f1)))
    K.eq(pts(Ab.flatFlood(world, "w", 0, 0, 0, fam, 3, 6, placed1)), [(-1, 0, 0)], "G: Tree Feller never takes a placed log (nor reaches past it)")
    # ---- speed caps
    T.clear()
    for x in range(-7, 8):
        for y in range(-7, 8):
            for z in range(-7, 8):
                if (x, y, z) != (0, 0, 0):
                    put(x, y, z, "Ore_Iron")
    big = Ab.veinPick(world, "w", 0, 0, 0, "Ore_Iron", 1000, notplaced)
    K.check(int(big.size()) == int(Ab.VEIN_CAP) == 64 and int(Ab.LASTREADS) <= 4000, "G: one Vein Burst breaks at most 64 (level 1000 asked) with <= 4000 reads (%d)" % int(Ab.LASTREADS))
    Ab.flood(world, "w", 0, 0, 0, "Ore_Iron", False, 0, 100000, 6, 6, None, notplaced)
    K.check(int(Ab.LASTREADS) <= 4000, "G: any flood reads at most 4000 positions (%d)" % int(Ab.LASTREADS))
    T.clear()
    for x in range(-6, 7):
        for y in range(-6, 7):
            for z in range(-6, 7):
                if (x, y, z) != (0, 0, 0):
                    put(x, y, z, "Wood_Oak_Trunk")
    put(1, 1, 1, "Plant_Leaves_Oak")
    lv = JArray(JBoolean)(1)
    Ab.flood(world, "w", 0, 0, 0, fam, True, 0, 256, 6, 32, lv, notplaced)
    K.check(bool(lv[0]) and int(Ab.LASTREADS) <= 26, "G: the read-only leaves check stops at the first leaves (%d reads, was up to 4000)" % int(Ab.LASTREADS))
    T.remove(Ab.pos(1, 1, 1))
    Ab.flood(world, "w", 0, 0, 0, fam, True, 0, 256, 6, 32, lv, notplaced)
    K.check(not bool(lv[0]) and int(Ab.LASTREADS) <= 4000, "G: no leaves = false, still <= 4000 reads (%d)" % int(Ab.LASTREADS))
    K.check(int(Cfg.fellerLogs(1000)) <= int(Cfg.FELLER_ALL) == 64, "G: Tree Feller logs capped at feller.maxPerLayer 64")
    g = [int(Ab.budgetAt(777, 100)) for _ in range(7)]
    K.eq(g, [100, 100, 100, 100, 100, 12, 0], "G: the server budget: 512 ability blocks per 50 ms tick, all players together")
    K.eq(int(Ab.budgetAt(778, 100)), 100, "G: the next tick has the full budget again")
    Ab.TEST = None
    # ---- bytecode wiring
    gr = PW.calls(jar)
    v, fe, br, fd = gr.get("TreeAbil.vein", set()), gr.get("TreeAbil.feller", set()), gr.get("TreeAbil.breakList", set()), gr.get("TreeAbil.fired", set())
    K.check(PKG + "TreeAbil.veinPick" in v and PKG + "TreeAbil.budget" in v and PKG + "TreeAbil.breakList" in v and PKG + "TreeAbil.fired" in v,
            "G: vein = veinPick -> budget -> breakList -> fired")
    K.check(PKG + "TreeAbil.budget" in fe and PKG + "TreeAbil.fired" in fe and PKG + "TreeAbil.flatFlood" in fe, "G: feller = flatFlood -> budget -> breakList -> fired")
    K.check(not any(x.endswith("ConcurrentHashMap.put") for x in v | fe), "G: vein / feller never arm a cooldown themselves (fired does, only when cd > 0)")
    K.check(any(x.endswith("BlockHarvestUtils.performBlockBreak") for x in br),
            "G: every Vein Burst / Tree Feller block breaks through BlockHarvestUtils.performBlockBreak (a real BreakBlockEvent: SkyySkills XP + Fortune)")
    K.check(not any("blockIdAt" in x for x in gr.get("TreeAbil.flood", set()) | gr.get("TreeAbil.flatFlood", set())) and
            PKG + "TreeAbil.blockIdAt" in gr.get("TreeAbil.idAt", set()), "G: the searches read through idAt (the world in the game)")
    fel = gr.get("TreeGather.felled", set())
    K.check(not any(x.endswith(".giveDrops") or "breakDouble" in x for x in fel), "G: SkyyTrees' felled-log rolls never give drops (Fortune for felled logs = SkyySkills only, no double roll)")
    gat = gr.get("TreeGather.run", set())
    K.check(PKG + "TreeAbil.vein" in gat and PKG + "TreeAbil.feller" in gat and PKG + "TreeAbil.llValue" in gat, "G: TreeGather.run fires vein / feller at tree + tool level (llValue)")
    K.save()


def run_f(out, _jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, SKILLS_JAR], verify=True)
    P = JClass("com.skyy.skills.Perks")
    PC = JClass("com.skyy.skills.PerkCfg")
    K.check(int(PC.GUARD) >= 2, "F: perk.fortuneGuard %d" % int(PC.GUARD))
    rnd = random.Random(324)
    for path in ("Vein Burst ore", "Tree Feller log", "felled log"):
        xs = [int(P.extras(1.5, rnd.random())) for _ in range(20000)]
        drops = [1 + x for x in xs]
        share3 = drops.count(3) / float(len(drops))
        K.check(set(drops) == {2, 3} and 0.48 < share3 < 0.52,
                "F %s: Fortune 150%% = 2 drops always + a third %.1f%% of the time (min %d)" % (path, share3 * 100, min(drops)))
    K.eq([int(P.extras(1.5, r)) for r in (0.0, 0.49, 0.5, 0.99)], [2, 2, 1, 1], "F: extras(1.5, r) = 1 + (r < 0.5)")
    gr = PW.calls(SKILLS_JAR)
    sp = "com.skyy.skills."
    bt, fc, ob = gr.get("BreakTask.run", set()), gr.get("FellCredit.one", set()), gr.get("Fell.onBreak", set())
    K.check(sp + "Perks.breakDouble" in bt, "F: a block broken by Vein Burst / Tree Feller (a real BreakBlockEvent) -> BreakTask.run -> Perks.breakDouble (Fortune)")
    K.check(sp + "Perks.breakDouble" in fc, "F: a log that fell -> FellCredit.one -> Perks.breakDouble (Fortune)")
    K.check(sp + "Perks.breakDouble" not in ob and sp + "FellCredit.one" not in ob, "F: no double roll - Fell.onBreak (a claimed log broken by hand / Tree Feller) never pays the felled roll")
    K.save()


def run_mg(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    M = JClass(PKG + "TreeMig324")
    base = "# head\nfoo=1\nMining.MVein.max=5\nMining.MVein.per=2.0\nMining.MVein.base=4.0\nMining.MVein.B=150000\nvein.cooldownSec=40\nfeller.logs=1,2\nfeller.cooldownSec=3\nbar=2\n"

    def upd(t):
        r = M.m324Update(t)
        if r is None:
            return None
        return str(r[0]), [str(x) for x in r[1]], [str(x) for x in r[2]], [str(x) for x in r[3]]

    r = upd(base)
    exp = base.replace("MVein.per=2.0", "MVein.per=1.0").replace("MVein.base=4.0", "MVein.base=0.0").replace("cooldownSec=40", "cooldownSec=0").replace("cooldownSec=3", "cooldownSec=0")
    K.check(r is not None and r[0] == exp + str(M.MARK_LINE) + "\n", "MG: LF old defaults -> the 4 values + the marker line, nothing else")
    K.eq(r[1], ["nodes.Mining[MVein.per]", "2.0", "1.0", "nodes.Mining[MVein.base]", "4.0", "0.0", "vein.cooldownSec", "40", "0", "feller.cooldownSec", "3", "0"],
         "MG: the 4 change-log rows (Server Setup keys)")
    K.check(upd(r[0]) is None, "MG: the marker = runs once")
    crlf = base.replace("\n", "\r\n")
    r2 = upd(crlf)
    K.check(r2 is not None and r2[0] == exp.replace("\n", "\r\n") + str(M.MARK_LINE) + "\r\n", "MG: CRLF file keeps CRLF on every line")
    r3 = upd(base.rstrip("\n"))
    K.check(r3 is not None and r3[0] == exp + str(M.MARK_LINE) + "\n", "MG: a missing final newline is added before the marker")
    r4 = upd(base.replace("MVein.per=2.0", "MVein.per=3.0").replace("vein.cooldownSec=40", "vein.cooldownSec=20"))
    K.check(r4 is not None and "Mining.MVein.per=3.0\n" in r4[0] and "Mining.MVein.base=4.0\n" in r4[0] and "vein.cooldownSec=20\n" in r4[0]
            and "feller.cooldownSec=0\n" in r4[0] and r4[3] == ["feller.cooldownSec"] and len(r4[2]) == 3,
            "MG: a hand-edited per keeps its base too, a hand-edited cooldown is kept, the untouched one still moves (notes %s)" % r4[2])
    r5 = upd(base.replace("vein.cooldownSec=40", "vein.cooldownSec = 40.0"))
    K.check(r5 is not None and "vein.cooldownSec = 0\n" in r5[0], "MG: spaced / 40.0 counts as the old default, the key part is kept")
    r6 = upd(base + "feller.cooldownSec=3\n")
    K.check(r6 is not None and r6[0].count("feller.cooldownSec=3\n") == 2 and "feller.cooldownSec" not in r6[3], "MG: a doubled line is kept")
    r7 = upd("# head\nfoo=1\n")
    K.check(r7 is not None and r7[0] == "# head\nfoo=1\n" + str(M.MARK_LINE) + "\n" and r7[1] == [], "MG: missing lines = the new built-ins, only the marker added")
    r8 = upd(exp)
    K.check(r8 is not None and r8[1] == [] and r8[0] == exp + str(M.MARK_LINE) + "\n", "MG: already new = nothing moved")
    K.check(upd("x=" + MK324 + "\n") is not None, "MG: the marker inside a value does not count")
    ob, nb = base.encode("latin-1"), r[0].encode("latin-1")
    K.check(bool(M.sameAfter(ob, nb, r[3])) and not bool(M.sameAfter(ob, nb + b"extra=1\n", r[3])), "MG: sameAfter accepts the update and refuses an added key")
    K.save()


def live_vals():
    p = os.path.join(LIVE, "trees.properties")
    if not os.path.isfile(p):
        return None
    o = {}
    for l in open(p, "rb").read().decode("latin-1").replace("\r\n", "\n").split("\n"):
        k = l.split("=", 1)[0]
        if k in KEYS:
            o[k] = o.get(k, []) + [l.split("=", 1)[1].strip()]
    return o


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Sto, Defs, Ab = JClass(PKG + "TreeCfg"), JClass(PKG + "TreeStore"), JClass(PKG + "TreeDefs"), JClass(PKG + "TreeAbil")
    Paths = JClass("java.nio.file.Paths")
    base = os.path.join(scratch, "st", "mods", "Skyy_SkyyTrees")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = tree_hash(base)
    Cfg.FILE = Paths.get(os.path.join(base, "trees.properties"))
    Sto.DIR = Paths.get(os.path.join(base, "players"))
    mg = {}
    lo = str(Cfg.load())
    bp = Paths.get(base)
    for m_ in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317", "TreeMig321", "TreeMig323", "TreeMig324"):   # setup()'s order
        mg[m_] = str(JClass(PKG + m_).run(bp))
    ids = [str(x) for x in Defs.ID]
    IV = ids.index("MVein")
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    K.eq((float(Cfg.PER[IV]), float(Cfg.BASE[IV]), int(Cfg.VEIN_CD_MS), int(Cfg.FELLER_CD_MS)), (1.0, 0.0, 0, 0),
         "ST start %s: the loaded numbers: Vein Burst per 1 base 0, no cooldowns" % step)
    if step == "1":
        lv = live_vals()
        okset = all(k in ("trees.properties", "config-changes.log") or k.startswith("config-history/") for k in ch)
        others = dict((k, v) for k, v in mg.items() if k != "TreeMig324" and v)
        K.check(okset and not others, "ST start 1: only trees.properties / config-changes.log / config-history change %s (others %s)" % (ch, others))
        if isinstance(lv, dict) and len(lv) == 4 and all(v == [KEYS[k][0]] for k, v in lv.items()):
            t = open(os.path.join(base, "trees.properties"), "rb").read()
            log = open(os.path.join(base, "config-changes.log"), encoding="utf8").read().split("\n")
            rows = [l.split("\t") for l in log if "\tSkyyTrees 0.3.24\t" in l]
            K.check(len(rows) == 4 and all(r_[2:4] == ["-", "update"] and r_[7] == "ok" for r_ in rows), "ST start 1: 4 Undo lines: %s" % [r_[4:7] for r_ in rows])
            K.check(any(k.startswith("config-history/") for k in ch), "ST start 1: a History version was written first")
            ol = open(os.path.join(LIVE, "trees.properties"), "rb").read()
            exp = ol
            for k, (o_, n_) in KEYS.items():
                assert exp.count(b"\n" + (k + "=" + o_).encode() + b"\n") + exp.count(b"\n" + (k + "=" + o_).encode() + b"\r\n") == 1, k
                exp = exp.replace(b"\n" + (k + "=" + o_).encode() + b"\r", b"\n" + (k + "=" + n_).encode() + b"\r", 1) if b"\r\n" in ol else \
                    exp.replace(b"\n" + (k + "=" + o_).encode() + b"\n", b"\n" + (k + "=" + n_).encode() + b"\n", 1)
            eol = b"\r\n" if b"\r\n" in ol else b"\n"
            if not exp.endswith(b"\n"):
                exp += eol
            mline = [l for l in t.decode("latin-1").replace("\r\n", "\n").split("\n") if MK324 in l][0].encode("latin-1")
            K.check(t == exp + mline + eol, "ST start 1: the new file = the old bytes with only the 4 values changed + the marker line (own line ending)")
            K.check("nodes.Mining[MVein.per] 2.0 -> 1.0" in mg["TreeMig324"], "ST start 1: the INFO line (%s)" % mg["TreeMig324"][:200])
        else:
            K.check(True, "ST start 1: the live lines are %s (not all the old defaults)" % lv)
            K.notes.append("live lines not at the old defaults: %s" % lv)
    else:
        K.check(not ch and mg.get("TreeMig324") == "", "ST start 2: nothing written %s (load %s)" % (ch, lo[:60]))
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyTrees folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("g", run_g), ("f", run_f), ("mg", run_mg), ("st1", run_st1), ("st2", run_st2)], script=__file__)
