"""Harness for SkyyTrees 0.4.2 (Skill Trees 3 + Rebirth follow-ups: the dead 0.3 nodes dropped, Salvage Hook's text, the raised skill gates,
Head Start; tools/trees_0_4_2_patch.py). Build first:
    python tools/trees_0_4_2_patch.py && python SkyyTrees/build_skyytrees_0.4.2.py
    python SkyyTrees/test_skyytrees_0.4.2.py [--dir <empty folder inside tools/dev/scratch/>]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A    verify   every class loads + initialises
  C    compare  0.4.1 -> 0.4.2: exactly the planned members (EXPECT)
  OLDG the 0.4.1 jar's GATES (dumped in its own JVM)
  GATE the class gates did not move; every skill gate only rose, to the build's numbers; no skill row whose free ability does something moved
       (nothing to grandfather); Salvage Hook's text; the dropped READ_BY entries
  DEAD every v3 rank of every tree maxed + derive: every one of the 57 dead 0.3 nodes is 0, the live aliases are not; bonusMap has no
       xp.smithing / xp.fishing / dodge.acrobatics key and dd.foraging = FFortune alone; healthOf = the class extra; toolSpeed = 0; the
       Acrobatics move source carries jump / fall only (speed 0)
  HEAD Head Start on fake bridges: head() reads rebirth:fn:stat live, keeps the last answer on null, 0 without SkyyRebirth, clamped; buy()
       spends Head Start points (skill + class tree), the refusal text names them; tree:<uuid> carries them; the respec price stays
       level-based; the raised Combat row-2 gate; rebirth:reads:SkyyTrees put + removed (only our value); fix round: tree:fn:headUsed
       (TreeV3.headUsed / TreeHeadFn) = the most Head Start points one tree uses (spent - level), null when SkyySkills does not answer
  LIVE START TWICE on a scratch COPY of the live Skyy_SkyyTrees folder: no file changes at all (no saved-data change in 0.4.2)
  AA   engine-access audit
NOT COVERED (UNVERIFIED in game): the pages' "Points X of Y" with Head Start on a real client; the gather rolls (only removals).
"""
import os, sys, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import deploy_set as DS
import trees_v3_data as V3D

VERSION = "0.4.2"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.4.1.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "st3fix", "th")))
LIVE_DIR = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyTrees")
ADDED = ["TreeHeadFn"]   # fix round: tree:fn:headUsed
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup", "~m shutdown"], "TreeCfg": ["~m load"],   # the version text
    "TreeDefs": ["~<clinit>"],                                                   # READERS / COMING_* of the dead nodes
    "TreeFx": ["~m acroPost", "~m bonusMap", "~m dmgBonus", "~m healthOf", "~m postTree", "~m stats", "~m toolSpeed"],
    "TreeGather": ["~m felled", "~m run"], "TreeSwing": ["~m notice"],
    "TreeStore": ["~m namesPut", "~m namesRemove"],
    "TreeV3": ["+f HEAD", "+f HEAD_MAX", "+f HFN", "+m head", "+m headOf", "+m headUsed", "+m pointsAll", "~<clinit>", "~m buy"],
    "TreePage": ["~m build", "~m buildClass"],
}
DEAD = ["Acrobatics.RDodge", "Acrobatics.RDodge2", "Acrobatics.RFall2", "Acrobatics.RJump2", "Acrobatics.RSpeed", "Acrobatics.RSpeed3",
        "Acrobatics.RStamina", "Acrobatics.RStamina2", "Acrobatics.RStamina3", "Alchemy.PDur2", "Alchemy.PExtra", "Alchemy.PHealth",
        "Alchemy.PMana", "Alchemy.PSeed", "Alchemy.PSig", "Alchemy.PStam", "Cooking.CBaker", "Cooking.CFed", "Cooking.CGrill", "Cooking.CIngr",
        "Cooking.CMaster", "Cooking.CPrep", "Exploration.EHeart", "Exploration.EHeart2", "Exploration.EScav", "Farming.AEssence",
        "Farming.AGarden", "Farming.AGrain", "Farming.AHearty", "Farming.ARoots", "Farming.ARunner", "Fishing.NBait", "Fishing.NDouble",
        "Fishing.NFortune2", "Fishing.NHunter", "Fishing.NReel", "Fishing.NSea", "Fishing.NWisdom", "Foraging.FCoins", "Foraging.FFortune2",
        "Foraging.FSpeed2", "Foraging.FSpread", "Foraging.FStride", "Foraging.FVigor", "Mining.MCoins", "Mining.MHeavy", "Mining.MRunner",
        "Mining.MSpread", "Mining.MStamina", "Smithing.SAppraise", "Smithing.SFuel", "Smithing.SHaggle", "Smithing.SHealth", "Smithing.SIdent",
        "Smithing.SMaster", "Smithing.SRarity2", "Smithing.SWisdom"]
WANT_SKILL = {"Mining": [0, 5, 10, 15, 20, 25], "Foraging": [0, 5, 10, 15, 20, 25], "Combat": [0, 5, 8, 13, 20, 25], "Beastmastery": [0, 0, 0, 0, 0, 0],
              "Farming": [0, 5, 8, 15, 20, 25], "Fishing": [0, 5, 10, 15], "Alchemy": [0, 3, 3, 14, 17, 22], "Smithing": [0, 5, 10, 15],
              "Cooking": [0, 5, 10, 15, 20, 25], "Acrobatics": [0, 3, 5, 9], "Exploration": [0, 0, 0, 3]}


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


class World(object):
    """fake bridges: skill levels per UUID + skill name, classes, coins, reader lists, SkyyRebirth's rebirth:fn:stat"""

    def __init__(self):
        from jpype import JClass, JImplements, JOverride
        self.J = lambda n: JClass(PKG + n)
        self.Int, self.Long, self.Bool, self.Dbl = JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Boolean"), JClass("java.lang.Double")
        self.UUID = JClass("java.util.UUID")
        self.levels, self.purse, self.head = {}, {}, {}
        W_ = self

        @JImplements("java.util.function.Function")
        class Fn(object):
            def __init__(self, f):
                self.f = f

            @JOverride
            def apply(self, a):
                return self.f(a)
        self.Fn = Fn
        br = self.J("TreeStore").bridge()
        self.br = br

        def lvl(a):
            return W_.Int.valueOf(int(W_.levels.get((str(a[0]), str(a[1]).lower()), 0)))

        def take(a):
            u, n = str(a[0]), int(a[1])
            if W_.purse.get(u, 0) < n:
                return W_.Bool.FALSE
            W_.purse[u] = W_.purse.get(u, 0) - n
            return W_.Bool.TRUE

        def stat(a):
            if str(a[1]) != "headstart":
                return W_.Dbl.valueOf(0.0)
            v = W_.head.get(str(a[0]))
            return None if v is None else W_.Dbl.valueOf(float(v))
        self.statfn = Fn(stat)
        for k, f in (("skill:fn:level", lvl), ("coins:fn:take", take), ("skill:fn:combat", lambda a: W_.Long.valueOf(0)),
                     ("skill:fn:xp", lambda a: W_.Long.valueOf(0))):
            br.put(k, Fn(f))
        br.put("rebirth:fn:stat", self.statfn)

    def uuid(self, s):
        return self.UUID.fromString(s)

    def set_class(self, u, cls):
        self.br.put("profile:class:" + str(u), cls)

    def readers(self, mod, keys):
        self.br.put("tree:reads:" + mod, ",".join(keys))


def setup_dirs(J, base):
    from jpype import JClass
    Paths = JClass("java.nio.file.Paths")
    os.makedirs(os.path.join(base, "players"), exist_ok=True)
    J("TreeStore").DIR = Paths.get(os.path.join(base, "players"))
    J("TreeCfg").FILE = Paths.get(os.path.join(base, "trees.properties"))
    J("TreeStore").DATA.clear()
    J("TreeStore").DIRTY.clear()


# ============================================================================================ OLDG: the 0.4.1 gates (in their own JVM)
def run_oldg(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=False)
    V = JClass(PKG + "TreeV3")
    g = [int(x) for x in V.GATES]
    json.dump({"g": g, "readers": [str(x) for x in JClass(PKG + "TreeDefs").READERS]}, open(os.path.join(scratch, "gates041.json"), "w"))
    K.check(len(g) == 19 * 8, "OLDG the 0.4.1 GATES table read (%d)" % len(g))
    K.save()


# ============================================================================================ GATE: the raised skill gates, texts, readers
def run_gate(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    V, D = JClass(PKG + "TreeV3"), JClass(PKG + "TreeDefs")
    o = json.load(open(os.path.join(scratch, "gates041.json")))
    g041, g = o["g"], [int(x) for x in V.GATES]
    names = [str(x) for x in V.TNAME]
    K.eq(g[:64], g041[:64], "GATE the 8 class gates did not move")
    K.check(all(g[i] >= g041[i] for i in range(len(g))), "GATE every gate only rose")
    for tv in range(8, 19):
        K.eq([g[tv * 8 + r] for r in range(1, len(WANT_SKILL[names[tv]]) + 1)], WANT_SKILL[names[tv]], "GATE %s gates" % names[tv])
    moved = []
    for r in range(int(V.NR)):
        tv = [t for t in range(19) if int(V.TR0[t]) <= r < int(V.TR0[t]) + int(V.TRN[t])][0]
        if tv >= 8 and int(V.RFK[r]) != 0 and g[tv * 8 + int(V.RNUM[r])] != g041[tv * 8 + int(V.RNUM[r])]:
            moved.append(str(V.RFNAME[r]))
    K.check(not moved, "GATE no skill row whose free ability does something moved its gate (nothing to grandfather): %s" % moved)
    sal = [x for x in range(int(V.NU)) if str(V.UKEY[x]) == "Skill.Fishing.b2.r3a"][0]
    K.eq(str(V.UNAME[sal]) + " | " + str(V.UTEXT[sal]), "Salvage Hook | +1.5% chance to reel in sunken loot/rank", "GATE Salvage Hook's text = its alias (3 x 0.5 %)")
    K.eq(int(V.UHL[sal]), 3, "GATE Salvage Hook still feeds 3 Treasure Hunter levels a rank")
    ids = ["%s.%s" % (str(D.TREES[i // 12]), str(D.ID[i])) for i in range(int(D.N))]
    rd = [str(x) for x in D.READERS]
    dropped = [ids[i] for i in range(len(ids)) if o["readers"][i] and not rd[i]]
    K.check(all(x in DEAD for x in dropped) and len(dropped) == 19, "GATE READ_BY dropped for 19 dead nodes only: %s" % dropped)
    K.check(all(rd[i] == o["readers"][i] for i in range(len(ids)) if ids[i] not in DEAD), "GATE every live node keeps its readers")
    K.save()


# ============================================================================================ DEAD: the 57 dead nodes read nowhere
def run_dead(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    setup_dirs(J, os.path.join(scratch, "dead"))
    Cfg, V, St, Fx, D, C = J("TreeCfg"), J("TreeV3"), J("TreeStore"), J("TreeFx"), J("TreeDefs"), J("TreeCalc")
    Cfg.load()
    w = World()
    u = w.uuid("22222222-2222-3333-4444-555555555555")
    d = St.data(u)
    for x in range(int(V.NU)):
        d.rk[x] = int(V.UMAX[x])
    V.derive(d)
    ids = ["%s.%s" % (str(D.TREES[i // 12]), str(D.ID[i])) for i in range(int(D.N))]
    v = Fx.compute(u)
    nz_dead = [ids[i] for i in range(len(ids)) if ids[i] in DEAD and (int(C.eff(d, i)) != 0 or float(v[i]) != 0.0)]
    live = [ids[i] for i in range(len(ids)) if ids[i] not in DEAD and float(v[i]) != 0.0]
    K.check(not nz_dead and len([x for x in ids if x in DEAD]) == 57, "DEAD every v3 rank maxed: the 57 dead nodes stay 0: %s" % nz_dead)
    K.check(len(live) >= 30, "DEAD the aliased nodes are fed (%d non-zero, e.g. %s)" % (len(live), live[:6]))
    m = Fx.bonusMap(v)
    keys = sorted(str(k) for k in m.keySet())
    K.check(not [k for k in keys if k in ("xp.smithing", "xp.fishing", "dodge.acrobatics")], "DEAD bonusMap: no xp.smithing / xp.fishing / dodge.acrobatics: %s" % keys)
    ff = ids.index("Foraging.FFortune")
    K.eq(round(float(m.get(JString("dd.foraging"))), 6), round(float(v[ff]), 6), "DEAD dd.foraging = FFortune alone (FFortune2 dropped)")
    K.check("dd.mining" in keys and "xp.mining" in keys and "doublejump.acrobatics" in keys, "DEAD the live keys stay: %s" % keys)
    K.eq(float(Fx.healthOf(u, v)), float(Fx.extraStat(u, 0)), "DEAD healthOf = the class tree's extra only")
    K.eq(float(Fx.toolSpeed(v, "Tool_Pickaxe_Iron")) + float(Fx.toolSpeed(v, "Tool_Hatchet_Iron")) + float(Fx.toolSpeed(v, "Tool_Hoe_Iron")), 0.0, "DEAD toolSpeed = 0")
    Fx.acroPost(u, v)
    mv = w.br.get("move:" + str(u))
    e = None if mv is None else mv.get("trees.acrobatics")
    rj, rf = ids.index("Acrobatics.RJump"), ids.index("Acrobatics.RFall")
    if e is not None:
        K.check(float(e.get("speed")) == 0.0 and abs(float(e.get("jump")) - float(v[rj])) < 1e-5 and abs(float(e.get("fallDamage")) + float(v[rf])) < 1e-5,
                "DEAD the Acrobatics move source: speed 0, jump = RJump, fall = RFall: %s" % e)
    else:
        K.check(float(v[rj]) == 0.0 and float(v[rf]) == 0.0, "DEAD no Acrobatics move source (RJump / RFall 0)")
    K.save()


# ============================================================================================ HEAD: Head Start
def run_head(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    setup_dirs(J, os.path.join(scratch, "head"))
    Cfg, V, St, Fx = J("TreeCfg"), J("TreeV3"), J("TreeStore"), J("TreeFx")
    Cfg.load()
    w = World()
    u = w.uuid("33333333-2222-3333-4444-555555555555")
    us = str(u)
    tvx = dict((str(V.TNAME[i]), i) for i in range(19))

    def up(tn, b, rid):
        t = tvx[tn]
        for x in range(int(V.TU0[t]), int(V.TU0[t]) + int(V.TUN[t])):
            if str(V.UKEY[x]) == "%s.%s.b%d.%s" % ("Class" if t < 8 else "Skill", tn, b, rid):
                return x
        raise KeyError((tn, b, rid))
    # head(): live read, clamp, null keeps the last answer, no SkyyRebirth = 0
    K.eq(int(V.head(u)), 0, "HEAD no answer yet (null) and nothing cached = 0")
    w.head[us] = 3
    K.eq(int(V.head(u)), 3, "HEAD rebirth:fn:stat headstart 3 -> 3")
    w.head[us] = None
    K.eq(int(V.head(u)), 3, "HEAD SkyyRebirth still loading (null) -> the last answer 3")
    w.head[us] = 2.9999999
    K.eq(int(V.head(u)), 3, "HEAD 2.9999999 -> 3 (rounding guard)")
    w.head[us] = 250
    K.eq(int(V.head(u)), 100, "HEAD clamped at 100")
    w.head[us] = -4
    K.eq(int(V.head(u)), 0, "HEAD a negative answer -> 0")
    K.eq(int(V.headOf(JClass("java.lang.Double").valueOf(float("nan")))), -1, "HEAD NaN is no answer")
    w.br.remove("rebirth:fn:stat")
    K.eq(int(V.head(u)), 0, "HEAD SkyyRebirth not loaded -> 0")
    w.br.put("rebirth:fn:stat", w.statfn)
    w.head[us] = 3
    # a skill tree at level 0: Head Start alone pays three ranks (Mining Prospector row 1, an alias upgrade)
    d = St.data(u)
    MIN = tvx["Mining"]
    w.levels[(us, "mining")] = 0
    r1 = up("Mining", 1, "r1a")
    msgs = [str(V.buy(u, d, MIN, r1, False)) for _ in range(3)]
    K.check(all(m.startswith("Done:") for m in msgs) and int(d.rk[r1]) == 3, "HEAD level 0 + Head Start 3 buys 3 ranks: %s" % msgs[-1])
    r = str(V.buy(u, d, MIN, r1, False))
    K.check(r.startswith("No free points - 3 of 3 spent (1 point a level + 3 Head Start)"), "HEAD the 4th is refused and names Head Start: %s" % r)
    K.eq(int(V.pointsAll(u, MIN)), 3, "HEAD pointsAll = level 0 + 3")
    K.eq(int(V.points(u, MIN)), 0, "HEAD points (the respec price's level) stays 0")
    w.levels[(us, "mining")] = 2
    K.eq(int(V.pointsAll(u, MIN)), 5, "HEAD level 2 + 3 = 5")
    K.eq(str(V.priceText(d, MIN, 2)), str(V.priceText(d, MIN, int(V.points(u, MIN)))), "HEAD the respec price text is level-based")
    Fx.postTree(u, d)
    tr = str(w.br.get("tree:" + us))
    K.check("Mining:3/5" in tr, "HEAD tree:<uuid> carries spent / level + Head Start: %s" % tr)
    # the raised Combat gate (0 -> 5 at row 2): 4 points in Combat row 1 do not open row 2; the 5th does
    COM = tvx["Combat"]
    w.readers("SkyyGear", ["Skill.Combat.b1.r1a", "Skill.Combat.b1.r1b", "Skill.Combat.b1.r4a", "Skill.Combat.b1.r4b"])
    w.head[us] = 0
    w.set_class(u, "Warrior")
    w.levels[(us, "combat")] = 10   # SkyySkills' "Combat" = the current class skill
    hone = up("Combat", 1, "r1a")
    for _ in range(4):
        V.buy(u, d, COM, hone, False)
    r2 = [x for x in range(int(V.TU0[COM]), int(V.TU0[COM]) + int(V.TUN[COM])) if int(V.RNUM[int(V.UROW[x])]) == 2][0]
    w.readers("SkyySkills", [str(V.UKEY[r2])])
    lvc = int(V.level(u, COM))
    K.check(lvc >= 5, "HEAD Combat has %d points (the class level)" % lvc)
    r = str(V.buy(u, d, COM, r2, False))
    K.check("needs 5 points in this tree - you have 4" in r, "HEAD Combat row 2 needs 5 now (was 0): %s" % r)
    V.buy(u, d, COM, hone, False)
    r = str(V.buy(u, d, COM, r2, False))
    K.check(r.startswith("Done:"), "HEAD the 5th point opens Combat row 2: %s" % r)
    # the class tree: Head Start on top of the class level
    WAR = tvx["Warrior"]
    w.head[us] = 2
    w.levels[(us, "swordsmanship")] = 0
    iron = up("Warrior", 1, "r1b")   # Last Stand (SkyyTrees' own hp code - always live)
    msgs = [str(V.buy(u, d, WAR, iron, False)) for _ in range(3)]
    K.check(msgs[0].startswith("Done:") and msgs[1].startswith("Done:") and msgs[2].startswith("No free points - 2 of 2 spent (1 point a level + 2 Head Start)"),
            "HEAD class tree at level 0: Head Start 2 buys 2 ranks, the 3rd waits: %s" % msgs)
    # fix round: tree:fn:headUsed - Mining 3 spent at level 2 (1 Head Start point), Combat 5 at 10 (0), Warrior 2 at 0 (2) -> the most = 2
    HF = J("TreeHeadFn")()
    K.eq(int(V.headUsed(u)), 2, "HEAD headUsed = the most Head Start points one tree uses (Warrior 2 at level 0; Mining 1; Combat 0)")
    K.eq(int(HF.apply(u)), 2, "HEAD TreeHeadFn (tree:fn:headUsed) answers the same")
    w.levels[(us, "swordsmanship")] = 5
    K.eq(int(HF.apply(u)), 1, "HEAD Warrior level 5 covers its 2 points -> Mining's 1 is the most")
    w.levels[(us, "mining")] = 9
    K.eq(int(HF.apply(u)), 0, "HEAD every tree covered by its level -> 0 (a Nexus respec may go on)")
    w.levels[(us, "mining")] = 2
    lvf = w.br.remove("skill:fn:level")
    K.check(HF.apply(u) is None, "HEAD SkyySkills not answering -> null (unknown: SkyyRebirth refuses, try again)")
    w.br.put("skill:fn:level", lvf)
    K.check(HF.apply(JClass("java.lang.String")("x")) is None, "HEAD a non-UUID argument -> null")
    # rebirth:reads:SkyyTrees (SkyyRebirth's reader gate)
    St.namesPut()
    K.eq(str(w.br.get("rebirth:reads:SkyyTrees")), "headstart", "HEAD namesPut lists headstart in rebirth:reads:SkyyTrees")
    St.namesRemove()
    K.check(w.br.get("rebirth:reads:SkyyTrees") is None, "HEAD namesRemove takes it back")
    w.br.put("rebirth:reads:SkyyTrees", "other")
    St.namesRemove()
    K.eq(str(w.br.get("rebirth:reads:SkyyTrees")), "other", "HEAD namesRemove never removes another value")
    K.save()


# ============================================================================================ LIVE: start twice on a copy of the live data
def live_start(jar_, home, K):
    from jpype import JClass
    J = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    J("TreeStore").DIR = Paths.get(os.path.join(home, "players"))
    J("TreeCfg").FILE = Paths.get(os.path.join(home, "trees.properties"))
    J("TreeStore").DATA.clear()
    J("TreeCfg").load()
    bp = Paths.get(home)
    for m in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317", "TreeMig321", "TreeMig323", "TreeMig324"):
        J(m).run(bp)
    datas = []
    for f in sorted(os.listdir(os.path.join(home, "players"))):
        if f.endswith(".properties"):
            datas.append((f, J("TreeStore").readFile(f[:-11])))
    return datas


def players_text(home):
    o = {}
    for f in sorted(os.listdir(os.path.join(home, "players"))):
        t = open(os.path.join(home, "players", f), "rb").read().decode("latin-1")
        o[f] = [l for l in t.splitlines() if not l.startswith("#")]
    return o


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    before = tree_hash(home)
    d1 = live_start(jar, home, K)
    after1 = tree_hash(home)
    new = sorted(k for k in after1 if k not in before)
    changed = sorted(k for k in before if after1.get(k) != before[k])
    K.check(all(c.startswith("players/") for c in changed) and all(n.startswith(("history/treesv3/", "history/gates041/")) or n == "trees-v3-changes.log" for n in new),
            "LIVE start 1: only the existing one-time updates (0.4.0 v3 + 0.4.1 gates41) touch files - nothing new in 0.4.2: changed %s new %d" % (changed, len(new)))
    K.check(d1 and not [f for f, d in d1 if bool(d.bad)] and all(bool(d.g41) and bool(d.v3) for f, d in d1), "LIVE every player file reads as v3 + gates41 (%d files)" % len(d1))
    V = JClass(PKG + "TreeV3")
    for f, d in d1:
        K.notes.append("LIVE %s: spent %s" % (f, ["%s %d" % (str(V.TNAME[tv]), int(V.spent(d, tv))) for tv in range(19) if int(V.spent(d, tv)) > 0]))
    json.dump(players_text(home), open(os.path.join(scratch, "live042.json"), "w"))
    live_start(jar, home, K)
    K.check(tree_hash(home) == after1, "LIVE start 2 changes nothing")
    K.save()


def run_live2(out, jar, scratch, home):
    """the same live copy under the PINNED 0.4.1: its player files must equal 0.4.2's (0.4.2 changes no saved data)"""
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=False)
    live_start(OLD_JAR, home, K)
    a = players_text(home)
    b = json.load(open(os.path.join(scratch, "live042.json")))
    K.check(a == b and len(a) > 0, "LIVE2 0.4.1 and 0.4.2 write the same player files from the live copy (%d files; comments ignored)" % len(a))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("oldg", run_oldg), ("gate", run_gate), ("dead", run_dead), ("head", run_head), ("live", run_live), ("live2", run_live2)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyTrees"))
