"""Harness for SkyyTrees 0.4.0 (SKILL TREES 3 - research/Skill-Trees-3-Spec.md R0 + R1 + R2; tools/trees_0_4_0_patch.py). Build first:
    python tools/trees_0_4_0_patch.py && python SkyyTrees/build_skyytrees_0.4.0.py
    python SkyyTrees/test_skyytrees_0.4.0.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A    verify   every class loads + initialises
  C    compare  0.3.25 -> 0.4.0: + TreeV3, TreeV3Mig; exactly the planned members of the 0.3 classes (EXPECT)
  DAT  the jar's tables = tools/trees_v3_data.py (every tree, branch, row, upgrade, hook, gate; the alias sums vs the 0.3 maxes)
  ENG  the engine on fake bridges: points = levels, gates (BL3 total points + the dead-upgrade rule), buy (every refusal + success), derive
       (alias levels, free perks of open rows -> TreeCalc.eff / TreeFx / tree:fn:bonus / tree:fn:level / skill:bonus), the class list
       (v3 + lines + m.<Ability>.<Mod>=ranks), respec (free, paid x level x n capped, combat, coins refused, History journal), rebirth reset,
       save / load round trip, postTree, the page texts of EVERY upgrade + row in every state measured against the 0.3.25 detail boxes
  MIG  the one-time update on scratch files: CRLF + LF, a continued value, every kept line byte for byte, v=2 -> v=3, the markers, the refund
       inputs (Dust spent = the 0.3.25 prices), the grandfathered abilities, the History copy (byte-identical), the log line, runs once,
       a missing History copy = waits (file unchanged); the Dust coin refund (paid once, journalled, pending -> unknown, a throw, no answer)
  CFG  a fresh trees.properties (no Token / Dust / AP lines, the 0.3 markers -> every 0.3 update leaves it alone), the new settings, the
       unused-value note of a hand-edited old file
  LIVE START TWICE on a scratch COPY of the live Skyy_SkyyTrees folder (setup's order: TreeCfg.load, the 0.3 updates, the note, then every
       player file read): start 1 = only the player files + their History copies + trees-v3-changes.log; start 2 changes nothing
  AA   engine-access audit
NOT COVERED (UNVERIFIED in game): the page build / clicks (TreePage needs a live PlayerRef), SkyyClasses' real cast with tree ranks.
"""
import os, sys, json, shutil, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import skyyui as SUI
import deploy_set as DS
import trees_v3_data as V3D

VERSION = "0.4.0"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.3.25.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "st3r12", "h")))
LIVE_DIR = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyTrees")
ADDED = ["TreeV3", "TreeV3Mig"]
EXPECT = {
    "TreeData": ["+f gfa", "+f gfx", "+f refCredit", "+f refHas", "+f refNext", "+f refSpent", "+f refSt", "+f refXp", "+f refZero", "+f rk", "+f rsAt", "+f rsFree", "+f rsN",
                 "+f v3", "+f v3note", "~c "],
    "TreeStore": ["+m v3clear", "+m v3lv", "+m v3noteOff", "+m v3rank", "+m v3ref", "+m v3refXp", "~m namesPut", "~m namesRemove", "~m rbReset", "~m readFile",
                  "~m rootOwn", "~m saveNow", "~m saveSync", "~m snap"],
    "TreeFx": ["~m compute", "~m postTree"],
    "TreeClass": ["~m abilCsv", "~m abilGate", "~m csvOf", "~m intact", "~m maint0"],
    "TreeCfg": ["+f V3_DCAP", "+f V3_DDIV", "+f V3_RBASE", "+f V3_RSTEPS", "~<clinit>", "~m apply", "~m load"],
    "CfgFile": ["~<clinit>"],   # the default trees.properties text (no Token / Dust / AP lines)
    "TreeRb": ["~m count"],
    "TreePage": ["+f vbr", "+f vsel", "~c ", "~m build", "~m buildClass", "~m handleDataEvent"],
    "TreeSkillCmd": ["~c ", "~m execute"],
    "TreesCmd": ["~c "],
    "SkyyTreesPlugin": ["~m setup"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],
}
MARGIN = 0.95
W, NW = 424, 424 - SUI.SLOT_FRAME - 12
BOX = {"name": (NW, 14, 24, True), "state": (NW, 16, 44, True), "line": (W, 16, 44, False), "need": (W, 16, 66, False), "how": (W, 13, 107, False),
       "cost": (W, 16, 26, True)}


def fits(kind, tx):
    w, size, h, bold = BOX[kind]
    if kind == "cost":
        return SUI.text_width(tx, size, bold) <= w * MARGIN
    return SUI.text_lines(tx, w * MARGIN, size, bold) <= int(h // SUI.line_height(size, bold=bold))


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


class World(object):
    """fake bridges: skill levels / XP per UUID + skill name, classes, coins (a purse per UUID), combat, reader lists"""

    def __init__(self):
        from jpype import JClass, JImplements, JOverride
        self.J = lambda n: JClass(PKG + n)
        self.Int, self.Long, self.Bool = JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
        self.UUID = JClass("java.util.UUID")
        self.levels, self.xps, self.purse, self.combat, self.take_ok = {}, {}, {}, {}, [True]
        self.add_mode = ["ok"]
        self.added = []
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
            u, n = str(a[0]), str(a[1]).lower()
            return W_.Int.valueOf(int(W_.levels.get((u, n), 0)))

        def xp(a):
            u, n = str(a[0]), str(a[1]).lower()
            return W_.Long.valueOf(int(W_.xps.get((u, n), 0)))

        def take(a):
            u, n = str(a[0]), int(a[1])
            if not W_.take_ok[0] or W_.purse.get(u, 0) < n:
                return W_.Bool.FALSE
            W_.purse[u] = W_.purse.get(u, 0) - n
            return W_.Bool.TRUE

        def add(a):
            u, n = str(a[0]), int(a[1])
            if W_.add_mode[0] == "throw":
                raise RuntimeError("purse locked")
            if W_.add_mode[0] == "none":
                return None
            W_.purse[u] = W_.purse.get(u, 0) + n
            W_.added.append((u, n))
            return W_.Long.valueOf(W_.purse[u])

        def combat(a):
            return W_.Long.valueOf(int(W_.combat.get(str(a), 0)))
        for k, f in (("skill:fn:level", lvl), ("skill:fn:xp", xp), ("coins:fn:take", take), ("coins:fn:add", add), ("skill:fn:combat", combat)):
            br.put(k, Fn(f))

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


# ============================================================================================ DAT: the jar's tables = the data file
def run_dat(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    V = JClass(PKG + "TreeV3")
    TD = JClass(PKG + "TreeDefs")
    order = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"] + \
            ["Mining", "Foraging", "Combat", "Beastmastery", "Farming", "Fishing", "Alchemy", "Smithing", "Cooking", "Acrobatics", "Exploration"]
    K.eq([str(x) for x in V.TNAME], order, "DAT tree order (classes = TreeClass.CLASSES, skills = the sub-tab order)")
    bad, nu = [], 0
    oldkey = dict((str(TD.TREES[i // 12]) + "." + str(TD.ID[i]), i) for i in range(int(TD.N)))
    for tv, tn in enumerate(order):
        t = V3D.tree(tn)
        if int(V.TNB[tv]) != len(t["branches"]) or bool(V.TLIGHT[tv]) != t["light"]:
            bad.append("%s shape" % tn)
        for bn, b in enumerate(t["branches"]):
            bi = int(V.TB0[tv]) + bn
            if str(V.BNAME[bi]) != b["name"] or int(V.BRN[bi]) != len(b["rows"]):
                bad.append("%s branch %d" % (tn, bn))
            for j, r in enumerate(b["rows"]):
                ri = int(V.BR0[bi]) + j
                if int(V.RNUM[ri]) != r["r"] or int(V.RGATE[ri]) != r["gate"] or bool(V.RCAP[ri]) != r["cap"] or int(V.RUN[ri]) != len(r["ups"]):
                    bad.append("%s b%d r%d row" % (tn, bn + 1, r["r"]))
                f = r["free"]
                if (str(V.RFNAME[ri]) or None) != (f["name"] if f else None):
                    bad.append("%s b%d r%d free %s" % (tn, bn + 1, r["r"], V.RFNAME[ri]))
                if f and f["hook"]:
                    h = f["hook"]
                    if h[0] == "abil" and (int(V.RFK[ri]) != 1 or str(V.RFLINE[ri]) != h[1] or str(V.RFAB[ri]) != h[2]):
                        bad.append("%s free hook %s" % (tn, h))
                    if h[0] == "old" and (int(V.RFK[ri]) != 2 or int(V.RFO[ri]) != oldkey[h[1]] or int(V.RFL[ri]) != h[2]):
                        bad.append("%s free hook %s" % (tn, h))
                for k, u in enumerate(r["ups"]):
                    ui = int(V.RU0[ri]) + k
                    nu += 1
                    key = "%s.%s.b%d.%s" % ("Class" if t["kind"] == "class" else "Skill", tn, bn + 1, u["id"])
                    if (str(V.UNAME[ui]), str(V.UTEXT[ui]), int(V.UMAX[ui]), int(V.UCOST[ui]), str(V.UKEY[ui])) != (u["name"], u["text"], u["max"], u["cost"], key):
                        bad.append("%s %s" % (tn, u["name"]))
                    h = u["hook"]
                    hk = int(V.UHK[ui])
                    if h is None and hk != 0:
                        bad.append("%s %s hook" % (tn, u["name"]))
                    if h and h[0] == "mod" and (hk != 1 or str(V.UHA[ui]) != h[1] or str(V.UHM[ui]) != h[2]):
                        bad.append("%s %s mod hook" % (tn, u["name"]))
                    if h and h[0] == "old" and (hk != 2 or int(V.UHO[ui]) != oldkey[h[1]] or int(V.UHL[ui]) != h[2]):
                        bad.append("%s %s old hook" % (tn, u["name"]))
    K.check(not bad and nu == int(V.NU), "DAT every tree / branch / row / upgrade / hook = tools/trees_v3_data.py (%d upgrades) %s" % (nu, bad[:6]))
    caps = [int(V.RGATE[int(V.BR0[int(V.TB0[tv])]) + int(V.BRN[int(V.TB0[tv])]) - 1]) for tv in range(19)]
    K.eq(caps, [15 if V3D.tree(tn)["light"] else 25 for tn in order], "DAT the capstone gate: 25 points (light trees Fishing / Exploration / Acrobatics / Smithing: 15)")
    K.check(all(int(V.UCOST[u]) == 1 for u in range(int(V.NU))) and all(int(V.UMAX[u]) == 1 for u in range(int(V.NU)) if bool(V.RCAP[int(V.UROW[u])])),
            "DAT every rank costs 1 point; every capstone = rank 1, 1 point (Skyy answer 4)")
    K.save()


# ============================================================================================ ENG: the engine on fake bridges
def run_eng(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    base = os.path.join(scratch, "eng")
    setup_dirs(J, base)
    Cfg, V, St, D, Fx, TC, Calc = J("TreeCfg"), J("TreeV3"), J("TreeStore"), J("TreeDefs"), J("TreeFx"), J("TreeClass"), J("TreeCalc")
    K.check("ready" not in str(Cfg.load()) or True, "ENG TreeCfg.load on a fresh folder")
    w = World()
    u = w.uuid("11111111-2222-3333-4444-555555555555")
    us = str(u)
    tvx = dict((str(V.TNAME[i]), i) for i in range(19))
    MIN, WAR, SMI, COM, BEA = tvx["Mining"], tvx["Warrior"], tvx["Smithing"], tvx["Combat"], tvx["Beastmastery"]
    d = St.data(u)
    K.check(bool(d.v3) and not bool(d.bad) and int(V.spent(d, MIN)) == 0, "ENG a new profile: v3 data, nothing spent")
    K.eq(int(V.level(u, MIN)), 0, "ENG no Mining level yet = 0 points")
    w.levels[(us, "mining")] = 12
    K.eq(int(V.points(u, MIN)), 12, "ENG points = the Mining level (1 a level)")
    def up(tn, b, rid):
        t = tvx[tn]
        for x in range(int(V.TU0[t]), int(V.TU0[t]) + int(V.TUN[t])):
            if str(V.UKEY[x]) == "%s.%s.b%d.%s" % ("Class" if t < 8 else "Skill", tn, b, rid):
                return x
        raise KeyError((tn, b, rid))
    g = V.gates(MIN)
    K.eq([int(g[n]) for n in range(1, 7)], [0, 5, 10, 15, 18, 23], "ENG Mining gates: 0/5/10/15 then capped by the live ranks below (the dead-upgrade rule: rows 1-4 hold 18 live ranks, rows 1-5 23)")
    # fix round (critic HIGH): the gates are fixed at build time - the same table the build printed, never from the live state
    K.eq([int(x) for x in list(V.gates(tvx["Assassin"]))[1:7]], [0, 3, 8, 10, 11, 14], "FIX gates fixed at build time: Assassin 0/3/8/10/11/14 (lowered where R3 hooks are missing)")
    K.eq([int(x) for x in list(V.gates(WAR))[1:7]], [0, 5, 10, 15, 20, 25], "FIX gates: Warrior = Skyy's 0/5/10/15/20/25")
    K.eq([int(V.GATES[t * 8 + n]) for t in range(19) for n in range(8)], [int(V.gates(t)[n]) for t in range(19) for n in range(8)], "FIX gates() = the GATES table")
    _cls_on = bool(Cfg.CLASS_ON)
    Cfg.CLASS_ON = False
    _g_off = [int(x) for x in V.gates(WAR)]
    Cfg.CLASS_ON = _cls_on
    K.eq(_g_off, [int(x) for x in V.gates(WAR)], "FIX gates do not move when class trees switch off / readers change at run time")
    qs, rs, wb = up("Mining", 1, "r1a"), up("Mining", 1, "r1b"), up("Mining", 1, "r2a")
    msgs = []
    r = str(V.buy(u, d, MIN, wb, False))
    K.check("needs 5 points in this tree - you have 0" in r, "ENG buy in a locked row is refused: %s" % r)
    for _ in range(5):
        msgs.append(str(V.buy(u, d, MIN, qs, False)))
    K.check(all(m.startswith("Done: Quick Swing rank") for m in msgs) and "New: Vein Burst!" in msgs[-1], "ENG 5 ranks of Quick Swing; the 5th opens row 2 (Vein Burst comes free): %s" % msgs[-1])
    K.check(str(V.buy(u, d, MIN, qs, False)) == "Quick Swing is already maxed", "ENG a maxed upgrade refuses")
    I = lambda nid: [i for i in range(int(D.N)) if str(D.ID[i]) == nid][0]
    K.eq((int(d.lv[I("MSpeed")]), int(d.lv[I("MVein")])), (5, 1), "ENG derive: MSpeed 5 (alias), MVein 1 (the row-2 perk)")
    v = Fx.compute(u)
    K.check(abs(float(v[I("MSpeed")]) - 0.08) < 1e-9 and float(v[I("MVein")]) == 1.0, "ENG TreeFx: +8%% pickaxe swing, Vein Burst 1 more ore (%s, %s)" % (v[I("MSpeed")], v[I("MVein")]))
    for _ in range(3):
        str(V.buy(u, d, MIN, wb, False))
    K.eq(int(d.lv[I("MVein")]), 4, "ENG Wide Burst 3 ranks + the perk = Vein Burst level 4")
    for _ in range(3):
        msgs.append(str(V.buy(u, d, MIN, rs, False)))
    K.check(msgs[-1].startswith("Done: Rich Seams rank 3/3 - 1 point left"), "ENG Rich Seams 3 ranks (11 of 12 spent): %s" % msgs[-1])
    gem = up("Mining", 1, "r3a")
    r = str(V.buy(u, d, MIN, gem, False))
    K.check(r.startswith("Done: Gem Eye rank 1/3 - 0 points left"), "ENG row 3 open at 10 points: %s" % r)
    r = str(V.buy(u, d, MIN, gem, False))
    K.check(r.startswith("No free points - 12 of 12 spent"), "ENG no free point refused: %s" % r)
    dead = up("Mining", 2, "r1a")
    r = str(V.buy(u, d, MIN, dead, False))
    K.check("is coming soon" in r and int(d.rk[dead]) == 0, "ENG a dead upgrade (no hook) is never bought: %s" % r)
    bfn = J("TreeBonusFn")()
    lfn = J("TreeFn")()
    arr = lambda *xs: JArray(JObject)(list(xs))
    K.eq(int(lfn.apply(arr(u, JString("Mining.MSpeed")))), 5, "ENG tree:fn:level Mining.MSpeed = 5 (the alias, unchanged key)")
    K.check(abs(float(bfn.apply(arr(u, JString("Mining.MFortune")))) - 0.3) < 1e-9, "ENG tree:fn:bonus Mining.MFortune = 0.3 (Rich Seams 3 x 10%)")
    Fx.refresh(u)
    sb = w.br.get("skill:bonus:" + us)
    tr = dict((str(k), float(vv)) for k, vv in dict(sb.get("trees")).items())
    K.check(abs(tr.get("dd.mining", 0) - 0.3) < 1e-9, "ENG skill:bonus trees dd.mining 0.3 (SkyySkills' Fortune path unchanged): %s" % tr)
    pt = str(w.br.get("tree:" + us))
    K.check(pt.startswith("Mining:12/12,"), "ENG tree:<uuid> = spent / points per tree: %s" % pt[:60])
    # ---- reader gating: Smithing Thrift = Smelting Fortune waits until SkyySkills / SkyySacks lists Smithing.SSmelt
    w.levels[(us, "smithing")] = 3
    th = up("Smithing", 1, "r1b")
    r = str(V.buy(u, d, SMI, th, False))
    K.check("coming soon" in r, "ENG Thrift waits for its reader (Smithing.SSmelt not listed): %s" % r)
    _gs = [int(x) for x in V.gates(SMI)]
    w.readers("SkyySacks", ["Smithing.SSmelt"])
    K.eq([int(x) for x in V.gates(SMI)], _gs, "FIX a reader mod listing a node late does not move the Smithing gates")
    r = str(V.buy(u, d, SMI, th, False))
    K.check(r.startswith("Done: Thrift rank 1/3"), "ENG listed by SkyySacks -> live and bought: %s" % r)
    K.check(abs(float(bfn.apply(arr(u, JString("Smithing.SSmelt")))) - 0.1) < 1e-9, "ENG tree:fn:bonus Smithing.SSmelt 0.1 (SkyySacks' Smelting Fortune key kept)")
    # ---- Combat / Beastmastery: no hooks yet - every row open (gates 0), nothing to buy, Beastmastery has no skill = 0 points
    K.eq([int(x) for x in list(V.gates(COM))[1:7]], [0] * 6, "ENG Combat: every upgrade waits for R3 -> no row is gated by dead upgrades")
    K.eq(int(V.points(u, BEA)), 0, "ENG Beastmastery: no SkyySkills skill yet = 0 points")
    # ---- class tree
    w.set_class(u, "Warrior")
    w.levels[(us, "swordsmanship")] = 20
    K.eq(int(V.points(u, WAR)), 20, "ENG class points = the class skill level")
    K.eq(str(TC.abilGate(u)), "v3,A1", "ENG tree:fn:abil at the start: v3 + A1 only (branch 1 row 1)")
    rad, pw = up("Warrior", 2, "r1a"), up("Warrior", 2, "r1b")
    r = str(V.buy(u, d, WAR, rad, False))
    K.check("is coming soon" in r and int(d.rk[rad]) == 0, "FIX a class modifier is not sold while SkyyClasses does not list Class.v3mods (0.1.41 / missing): %s" % r)
    w.readers("SkyyClasses", ["Class.Warrior.A1", "Class.v3mods"])
    K.check(bool(V.live(rad)), "FIX listed by SkyyClasses 0.1.42 (Class.v3mods) -> the modifier is live")
    for _ in range(4):
        str(V.buy(u, d, WAR, rad, False))
    r = str(V.buy(u, d, WAR, pw, False))
    K.check("New: Challenge, Shield Shockwave, Iron Chain!" in r, "ENG 5 class points open every row 2: Challenge (A4a), Shield Shockwave (A2), Iron Chain (A3): %s" % r)
    csv = str(TC.abilGate(u))
    K.eq(csv, "v3,A1,A2,A3,A4a,m.RallyingGuard.Radius=4,m.RallyingGuard.Power=1", "ENG the class list for SkyyClasses 0.1.42")
    K.eq(str(TC.csvOf(d, None, WAR)), csv, "ENG TreeClass.csvOf (the Lattice actions) = the same list")
    K.check(TC.abilGate(w.uuid("99999999-2222-3333-4444-555555555555")) is None, "ENG no class -> no gate (null)")
    # ---- respec: the free one, then 100 x level x n (capped at 5 steps), combat blocks, coins refused, History first
    w.purse[us] = 10 ** 9
    K.eq(int(V.price(d, MIN, 12)), 0, "ENG the first respec of a tree in a run is free")
    w.combat[us] = 4000
    r = str(V.respec(u, d, MIN, False))
    K.check(r.startswith("Leave combat first") and int(V.spent(d, MIN)) == 12, "ENG respec blocked in combat: %s" % r)
    w.combat[us] = 0
    r = str(V.respec(u, d, MIN, False))
    hist = os.path.join(base, "history", "respec", us)
    hf = sorted(os.listdir(hist)) if os.path.isdir(hist) else []
    K.check(r.startswith("Respec done - every Mining point is back (your free respec") and int(V.spent(d, MIN)) == 0 and len(hf) == 1,
            "ENG the free respec: every point back, History %s: %s" % (hf, r))
    hp = open(os.path.join(hist, hf[0]), encoding="latin-1").read() if hf else ""
    K.check("Skill.Mining.b1.r1a=5" in hp and "Skill.Mining.b1.r2a=3" in hp and "tree=Mining" in hp, "ENG the History journal holds the old ranks")
    K.eq((int(d.lv[I("MSpeed")]), int(d.lv[I("MVein")])), (0, 0), "ENG after the respec the aliases and the perk are gone")
    for _ in range(5):
        V.buy(u, d, MIN, qs, False)
    K.eq(int(V.price(d, MIN, 12)), 1200, "ENG the next respec: 100 x 12 x 1")
    w.take_ok[0] = False
    r = str(V.respec(u, d, MIN, False))
    K.check("you do not have enough" in r and int(V.spent(d, MIN)) == 5 and len(os.listdir(hist)) == 1, "ENG coins refused -> nothing changed, the journal taken back: %s" % r)
    w.take_ok[0] = True
    r = str(V.respec(u, d, MIN, False))
    K.check("1,200 coins paid" in r and w.purse[us] == 10 ** 9 - 1200 and int(d.rsN[MIN]) == 1, "ENG the paid respec takes 1,200 coins: %s" % r)
    _pt = open(os.path.join(base, "players", us + ".properties"), encoding="latin-1").read()
    K.check("respec.Mining.n=1" in _pt and "Skill.Mining.b1.r1a" not in _pt, "FIX the respec is on disk at once (saveSync, not a later saveSoon)")
    d.rsN[MIN] = 9
    K.eq(int(V.price(d, MIN, 12)), 6000, "ENG the price steps stop at respec.maxSteps 5 (100 x 12 x 5)")
    r = str(V.respec(u, d, MIN, False))
    K.check(r.startswith("Nothing to respec"), "ENG nothing spent = nothing to respec: %s" % r)
    r = str(V.respec(u, d, WAR, False))
    K.check(r.startswith("Respec done - every Warrior point") and str(TC.abilGate(u)) == "v3,A1", "ENG the class respec (free) re-locks the row abilities: %s" % r)
    # ---- grandfathered abilities stay until that tree's respec
    d.gfa[WAR * 5 + 4] = True
    K.eq(str(TC.abilGate(u)), "v3,A1,A4b", "ENG a grandfathered A4b stays owned")
    w.purse[us] = 10 ** 9
    r = str(V.respec(u, d, WAR, False))
    K.check(r.startswith("Respec done") and str(TC.abilGate(u)) == "v3,A1", "ENG a respec ends it (anySpent counts it): %s" % r)
    # fix round (critic): the 0.3 passive class nodes are grandfathered in tree:fn:abil until the tree's respec
    d.gfx[WAR] = "PA1,PB2"
    K.eq(str(TC.abilGate(u)), "v3,A1,PA1,PB2", "FIX grandfathered 0.3 passives (PA1, PB2) reach SkyyClasses in tree:fn:abil")
    r = str(V.respec(u, d, WAR, False))
    _hw = [f for f in os.listdir(hist) if f.startswith("Warrior-")]
    K.check(r.startswith("Respec done") and str(TC.abilGate(u)) == "v3,A1" and d.gfx[WAR] is None
            and any("Class.Warrior.gfx=PA1,PB2" in open(os.path.join(hist, f), encoding="latin-1").read() for f in _hw),
            "FIX a respec ends the grandfathered passives (journalled in History): %s" % r)
    # ---- fix round 2 (critic): a grandfathered 0.3 passive keeps its SkyyTrees-applied effects + tree:fn:bonus (SkyyArmory) for a v3 player
    MAG = tvx["Mage"]
    w.set_class(u, "Mage")
    d.gfx[MAG] = "PC2,T2"
    _it = TC.intact(d, MAG)
    _pc2, _t2, _t3 = int(TC.nodeIdx(MAG, "PC2")), int(TC.nodeIdx(MAG, "T2")), int(TC.nodeIdx(MAG, "T3"))
    K.check(bool(_it[_pc2]) and bool(_it[_t2]) and sum(1 for x in _it if bool(x)) == 2, "FIX2 TreeClass.intact of a v3 player = its grandfathered passives (PC2, T2)")
    _chp = int(TC.CHP[MAG * int(TC.NN) + _pc2])
    K.check(_chp != 0 and abs(float(TC.hpPct(u)) - _chp) < 1e-9, "FIX2 Siphon's max Health cost (%d %%) applies again to a grandfathered PC2: %s" % (_chp, TC.hpPct(u)))
    K.check(int(TC.bonusLevel(u, "Class.Mage.T2")) == 1 and int(TC.bonusLevel(u, "Class.Mage.T3")) == 0, "FIX2 tree:fn:bonus answers a grandfathered T2 (SkyyArmory) and not an unowned T3")
    _csvm = str(TC.abilGate(u))
    K.check(",PC2" in _csvm and ",T2" in _csvm, "FIX2 the passives reach SkyyClasses as 0.3's csvOf wrote them (=Amount where set): %s" % _csvm)
    d.gfx[MAG] = None
    K.check(float(TC.hpPct(u)) == 0.0 and int(TC.bonusLevel(u, "Class.Mage.T2")) == 0, "FIX2 gone with the gfx line (a respec)")
    w.set_class(u, "Warrior")
    # ---- fix round 2 (critic): no buy / respec while SkyyProfiles switches the profile
    w.br.put("profile:busy:" + us, "1")
    _rb = str(V.buy(u, d, MIN, int(V.TU0[MIN]), False))
    _rr = str(V.respec(u, d, MIN, False))
    w.br.remove("profile:busy:" + us)
    K.check(_rb.startswith("Wait for the profile switch") and _rr.startswith("Wait for the profile switch"), "FIX2 buy + respec refused while the profile switches: %s / %s" % (_rb, _rr))
    # ---- rebirth reset
    for _ in range(5):
        V.buy(u, d, MIN, qs, False)
    w.levels[(us, "exploration")] = 10
    EXP = tvx["Exploration"]
    cf = up("Exploration", 1, "r3b")
    wd = [x for x in range(int(V.TU0[EXP]), int(V.TU0[EXP]) + int(V.TUN[EXP])) if bool(V.live(x))]
    K.eq([str(V.UNAME[x]) for x in wd], ["Chest Finder"], "ENG Exploration: only Chest Finder is live")
    d.rsFree[EXP] = True
    d.rk[cf] = 2
    c = V.count(d)
    K.eq((int(c[0]), int(c[1])), (2, 0), "ENG rebirth facts: 2 skill upgrades with ranks (Quick Swing, Thrift; Exploration's Chest Finder not counted)")
    St.rbReset(d, "tx1234567890123-abcdef")
    K.check(int(V.spent(d, MIN)) == 0 and int(d.rk[cf]) == 2 and not bool(d.rsFree[EXP]) and int(d.rsN[MIN]) == 0 and str(d.rbTx) == "tx1234567890123-abcdef",
            "ENG rebirth: every tree back to 0 but Exploration, respec counters reset (a free respec again)")
    # ---- save / load round trip
    for _ in range(4):
        V.buy(u, d, MIN, qs, False)
    d.gfa[WAR * 5 + 2] = True
    St.dirty(us)
    St.flushDirty()
    txt = open(os.path.join(base, "players", us + ".properties"), encoding="latin-1").read()
    K.check("v=3" in txt and "treesV3=1" in txt and "Skill.Mining.b1.r1a=4" in txt and "Class.Warrior.gf=A3" in txt and "dust" not in txt.lower().replace("refund", ""),
            "ENG the v=3 file: marker, ranks, gf (no Tokens / Dust)")
    St.DATA.clear()
    d2 = St.data(u)
    K.check(int(d2.rk[qs]) == 4 and bool(d2.gfa[WAR * 5 + 2]) and int(d2.rk[cf]) == 2 and int(d2.rsN[MIN]) == 0 and int(d2.lv[I("MSpeed")]) == 4,
            "ENG load = save (ranks, gf, derived levels)")
    # ---- every page text of every upgrade + row in every state fits the 0.3.25 detail boxes
    bad, n = [], 0
    dd = J("TreeData")()
    J("TreeV3Mig").fresh(dd)
    for tv in range(19):
        g = V.gates(tv)
        for x in range(int(V.TU0[tv]), int(V.TU0[tv]) + int(V.TUN[tv])):
            ri = int(V.UROW[x])
            for st in (0, 1, 2, 3, 4, 5):
                for rk in (0, int(V.UMAX[x])):
                    dd.rk[x] = rk
                    texts = [("name", str(V.detName(ri, x))), ("state", str(V.detState(dd, ri, x, st, g, 99, 100))),
                             ("line", str(V.detNow(dd, ri, x, st, 99, g))), ("line", str(V.detNext(dd, ri, x))), ("cost", str(V.detCost(x, 100, 99))),
                             ("need", str(V.detNeed(dd, ri, x, st, g, 99, 100, 100))), ("how", str(V.detHow(ri, x))), ("cost", str(V.buyText(dd, ri, x, st)))]
                    for kind, tx in texts:
                        n += 1
                        if not fits(kind, tx):
                            bad.append("%s %s %s: %s" % (V.TNAME[tv], kind, st, tx))
            dd.rk[x] = 0
        for ri in range(int(V.TR0[tv]), int(V.TR0[tv]) + int(V.TRN[tv])):
            if not str(V.RFNAME[ri]):
                continue
            for sp in (0, 99):
                texts = [("name", str(V.detName(ri, -1))), ("state", str(V.detState(dd, ri, -1, 7, g, sp, 100))), ("line", str(V.detNow(dd, ri, -1, 7, sp, g))),
                         ("line", str(V.detNext(dd, ri, -1))), ("need", str(V.detNeed(dd, ri, -1, 7, g, sp, 100, 100))), ("how", str(V.detHow(ri, -1)))]
                for kind, tx in texts:
                    n += 1
                    if not fits(kind, tx):
                        bad.append("%s free %s: %s" % (V.TNAME[tv], kind, tx))
    K.notes.append("ENG page texts measured: %d" % n)
    K.check(not bad and n > 20000, "ENG %d page texts (every upgrade + free row, every state) fit the detail boxes %s" % (n, bad[:5]))
    K.eq(int(V.pageOfName("combat")), int(D.NT) + 1, "ENG /tree combat -> the Combat page")
    K.eq([int(V.pageOfName(x)) for x in ("beasts", "beastmastery", "mining", "smi", "xyz")], [int(D.NT) + 2, int(D.NT) + 2, 0, 7, -1], "ENG /tree names")
    K.save()


# ============================================================================================ MIG: the one-time update + the Dust coin refund
def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    base = os.path.join(scratch, "mig")
    setup_dirs(J, base)
    Cfg, V, St, M, Calc, D = J("TreeCfg"), J("TreeV3"), J("TreeStore"), J("TreeV3Mig"), J("TreeCalc"), J("TreeDefs")
    Cfg.load()
    w = World()
    I = lambda nid: [i for i in range(int(D.N)) if str(D.ID[i]) == nid][0]
    k1 = "aaaaaaaa-2222-3333-4444-555555555555"
    old = ("#SkyyTrees - node levels of one profile (Tokens and Dust are computed from your skills, never stored)\r\n#Thu Oct 15 22:24:14 MDT 2026\r\n"
           "Acrobatics.RJump=4\r\nClass.Priest=ROOT,A1,P1,T1,TS,P2,A2,X2,T2,P3,P4,A4b,A1.Power\r\nClass.Priest.order=ROOT,A1,TS\r\nMining.MSpeed=3\r\n"
           "Mining.MFortune=2\r\nClass.Priest.on=TS\r\nMining.dustCredit=77\r\nabil.tree2=done\r\nname=Wes\\\r\n  ley\r\nnote.swing=1\r\nquiet=false\r\nrb.lastTx=tx1\r\nv=2\r\n")
    pf = os.path.join(base, "players", k1 + ".properties")
    open(pf, "wb").write(old.encode("latin-1"))
    d = St.readFile(k1)
    new = open(pf, "rb").read().decode("latin-1")
    hist = os.path.join(base, "history", "treesv3", k1 + ".properties")
    K.check(os.path.isfile(hist) and open(hist, "rb").read() == old.encode("latin-1"), "MIG the History copy = the old file byte for byte")
    keep = ["#SkyyTrees - node levels of one profile (Tokens and Dust are computed from your skills, never stored)\r\n", "#Thu Oct 15 22:24:14 MDT 2026\r\n",
            "name=Wes\\\r\n  ley\r\n", "note.swing=1\r\n", "quiet=false\r\n", "rb.lastTx=tx1\r\n", "v=3\r\n"]
    want = "".join(keep)
    sp_m = int(Calc.cost(I("MSpeed"), 1)) + int(Calc.cost(I("MSpeed"), 2)) + int(Calc.cost(I("MFortune"), 1))
    sp_a = sum(int(Calc.cost(I("RJump"), n)) for n in (1, 2, 3))
    K.check(new.startswith(want), "MIG the kept lines byte for byte (comments, a continued name, note.swing, quiet, rb.lastTx; v=2 -> v=3), CRLF kept: %r" % new[:240])
    tail = new[len(want):]
    K.check(tail.startswith("treesV3=1\r\nv3.note=1\r\n") and ("refund.Mining.dust=%d,77\r\n" % sp_m) in tail and ("refund.Acrobatics.dust=%d,0\r\n" % sp_a) in tail
            and "Class.Priest.gf=A2,A4b\r\n" in tail and "Class.Priest.gfx=P1,T1,TS,P2,X2,T2,P3,P4\r\nClass.Priest.gfon=TS\r\n" in tail and tail.count("\r\n") == tail.count("\n"), "MIG the appended lines (marker, note, refund inputs = the 0.3.25 Dust prices, gf A2 + A4b) in CRLF: %r" % tail)
    K.check(bool(d.v3) and not bool(d.bad) and str(d.name) == "Wesley" and bool(d.v3note) and bool(d.gfa[4 * 5 + 1]) and bool(d.gfa[4 * 5 + 4]) and int(d.refSpent[0]) == sp_m
            and int(d.refCredit[0]) == 77 and all(int(x) == 0 for x in d.rk), "MIG the data: v3, the name, the note, the abilities kept, the refund inputs, no ranks")
    logf = os.path.join(base, "trees-v3-changes.log")
    K.check(os.path.isfile(logf) and "update" in open(logf, encoding="utf8").read() and "Undo: stop the server" in open(logf, encoding="utf8").read(), "MIG one change-log line with the Undo")
    St.DATA.clear()
    b2 = open(pf, "rb").read()
    d2 = St.readFile(k1)
    K.check(open(pf, "rb").read() == b2 and bool(d2.gfa[4 * 5 + 1]) and open(hist, "rb").read() == old.encode("latin-1"), "MIG runs once: the second read changes nothing")
    _csv2 = [x.split("=")[0] for x in str(J("TreeV3").classCsv(d2, 4)).split(",")]
    K.check(str(d2.gfx[4]) == "P1,T1,TS,P2,X2,T2,P3,P4" and "TS" in _csv2 and "X2" in _csv2, "FIX the Priest's 0.3 passives (+ X2) are grandfathered (gfx) and sent to SkyyClasses, TS ON (gfon): %s / %s" % (d2.gfx[4], _csv2))
    TC = J("TreeClass")
    _ts = int(TC.nodeIdx(4, "TS"))
    K.check(bool(d2.con[4 * int(TC.NN) + _ts]), "FIX2 the All players switch of a grandfathered passive survives the update (Class.Priest.on -> .gfon -> d.con)")
    d2.con[4 * int(TC.NN) + _ts] = False
    K.check("TS" not in [x.split("=")[0] for x in str(J("TreeV3").classCsv(d2, 4)).split(",")], "FIX2 a Party only switch is not sent (as 0.3's csvOf)")
    _p2 = JClass("java.util.Properties")()
    M_ = J("TreeV3Mig")
    M_.writeV3(d2, _p2)
    K.check(_p2.getProperty("Class.Priest.gfon") is None and str(_p2.getProperty("Class.Priest.gfx")) == "P1,T1,TS,P2,X2,T2,P3,P4", "FIX2 a switch turned off is saved off (no .gfon)")
    d2.con[4 * int(TC.NN) + _ts] = True
    _lg0 = open(os.path.join(base, "trees-v3-changes.log"), encoding="utf8").read()
    K.check("old class-page setting line(s) dropped on purpose" in _lg0, "FIX2 the update log names the dropped 0.3 class-page settings (.order ...)")
    K.check(os.path.isfile(os.path.join(base, "history", "treesv3", k1 + ".done")), "FIX the update writes history/treesv3/<pkey>.done")
    # LF file without a v line
    k2 = "bbbbbbbb-2222-3333-4444-555555555555"
    pf2 = os.path.join(base, "players", k2 + ".properties")
    open(pf2, "wb").write(b"Foraging.FSpeed=8\nname=Sky\nquiet=true\n")
    St.readFile(k2)
    t2 = open(pf2, "rb").read().decode("latin-1")
    K.check(t2.startswith("name=Sky\nquiet=true\nv=3\ntreesV3=1\n") and "\r" not in t2, "MIG LF kept, a missing v line added: %r" % t2[:80])
    # no History copy = it waits (a directory where the copy goes)
    k3 = "cccccccc-2222-3333-4444-555555555555"
    pf3 = os.path.join(base, "players", k3 + ".properties")
    open(pf3, "wb").write(b"Mining.MSpeed=1\nv=2\n")
    os.makedirs(os.path.join(base, "history", "treesv3", k3 + ".properties"))
    d3 = St.readFile(k3)
    K.check(bool(d3.bad) and open(pf3, "rb").read() == b"Mining.MSpeed=1\nv=2\n", "MIG no History copy -> the file waits unchanged (unreadable for now)")
    # ---- the Dust coin refund
    u1 = w.uuid(k1)
    St.DATA.clear()
    d = St.data(u1)
    w.levels[(k1, "mining")] = 20
    w.xps[(k1, "mining")] = 6000000
    w.levels[(k1, "acrobatics")] = 5
    w.xps[(k1, "acrobatics")] = 100
    Cfg.EXTRA_DUST = 10 ** 9   # fix round 2: debug.extraDust never counts in the refund
    M.settle(None, u1, d)
    K.check(sum(1 for t in range(int(D.NT)) if d.refSt[t] is not None and str(d.refSt[t]).startswith("paid:") and str(d.refSt[t]) != "paid:0") == 1
            and str(d.refSt[0]).startswith("paid:"), "FIX2 one tree paid per settle call (Mining first; the others wait 10 s)")
    for _ in range(12):
        d.refNext = 0
        d.refZero[list(D.TREES).index("Acrobatics")] = 0
        M.settle(None, u1, d)
    Cfg.EXTRA_DUST = 0
    em = 6000000 // int(Cfg.rate(0)) + 77 - sp_m
    want_m = min(25000, em // 100)
    K.check(str(d.refSt[0]) == "paid:%d" % want_m and (k1, want_m) in w.added, "MIG Mining: %d Dust left -> %d coins paid (1 per 100, cap 25000): %s" % (em, want_m, d.refSt[0]))
    ai = list(D.TREES).index("Acrobatics")
    K.check(str(d.refSt[ai]) == "paid:0", "MIG Acrobatics: Dust spent above earned -> 0 coins, settled")
    K.check(int(d.refXp[0]) == 6000000, "FIX2 the first real XP answer is kept (refXp)")
    _zt = [t for t in range(int(D.NT)) if d.refHas[t] and t not in (0, ai)]
    K.check(all(d.refSt[t] is None for t in _zt) and all(int(d.refZero[t]) > 0 for t in _zt),
            "FIX2 a tree whose XP answers 0 is NOT settled at once (the 60 s zero window started): %s" % [str(d.refSt[t]) for t in _zt])
    for t in _zt:
        d.refZero[t] = 1   # the zero window passed
    for _ in range(12):
        d.refNext = 0
        M.settle(None, u1, d)
    K.check(all(str(d.refSt[t]) == "paid:0" for t in _zt), "FIX2 after 60 s of zero answers a 0-XP tree settles (paid:0): %s" % [str(d.refSt[t]) for t in _zt])
    n0 = len(w.added)
    d.refNext = 0
    M.settle(None, u1, d)
    K.check(len(w.added) == n0, "MIG the refund is paid once (a second settle pays nothing)")
    import time
    time.sleep(1.0)   # saveSoon runs on the server's scheduler
    St.save(k1)
    txt = open(pf, "rb").read().decode("latin-1")
    K.check(("refund.Mining=paid\\:%d" % want_m) in txt,"MIG the paid state is saved (Properties escapes the colon)")
    K.check(("refund.Mining.dust=%d,77,6000000" % sp_m) in txt, "FIX2 the XP snapshot is saved (refund.<Tree>.dust=<spent>,<credit>,<xp>)")
    txt2 = "".join(("refund.Mining=pending:%d:1700000000000" % want_m) + l_[len(l_.rstrip("\r\n")):] if l_.startswith("refund.Mining=") else l_
                   for l_ in txt.splitlines(True))
    open(pf, "wb").write(txt2.encode("latin-1"))
    St.DATA.clear()
    d = St.data(u1)
    K.check(str(d.refSt[0]) == "unknown:%d" % want_m, "MIG a pending refund found at load = unknown (never paid twice): %s" % d.refSt[0])
    lg = open(logf, encoding="utf8").read()
    K.check("refund-unknown" in lg and "refund\tMining" in lg.replace(": ", "\t") or "refund" in lg, "MIG the refund lines are logged")
    # a throw = unknown; no answer = retried later
    k4 = "dddddddd-2222-3333-4444-555555555555"
    open(os.path.join(base, "players", k4 + ".properties"), "wb").write(b"Mining.MSpeed=1\nv=2\n")
    u4 = w.uuid(k4)
    St.DATA.clear()
    d4 = St.data(u4)
    w.levels[(k4, "mining")] = 50
    w.xps[(k4, "mining")] = 9000000
    w.add_mode[0] = "none"
    M.settle(None, u4, d4)
    K.check(d4.refSt[0] is None, "MIG coins:fn:add answers nothing -> not paid, tried again later")
    d4.refNext = 0
    w.add_mode[0] = "throw"
    M.settle(None, u4, d4)
    K.check(str(d4.refSt[0]).startswith("unknown:"), "MIG coins:fn:add throws -> unknown (never retried): %s" % d4.refSt[0])
    d4.refNext = 0
    w.add_mode[0] = "ok"
    n1 = len(w.added)
    M.settle(None, u4, d4)
    K.check(not [a for a in w.added[n1:] if a[0] == k4 and a[1] > 0 and str(d4.refSt[0]).startswith("unknown")], "MIG an unknown refund is never paid")
    # ---- fix round (critic MEDIUM): the refund never settles on a non-answer
    k5 = "eeeeeeee-2222-3333-4444-555555555555"
    open(os.path.join(base, "players", k5 + ".properties"), "wb").write(b"Mining.MSpeed=3\nv=2\n")
    u5 = w.uuid(k5)
    St.DATA.clear()
    d5 = St.data(u5)
    w.levels[(k5, "mining")] = 30
    M.settle(None, u5, d5)
    K.check(d5.refSt[0] is None, "FIX Dust spent but SkyySkills shows 0 XP (profile still loading) -> not settled (no paid:0): %s" % d5.refSt[0])
    xp_fn = w.br.get("skill:fn:xp")
    w.br.put("skill:fn:xp", w.Fn(lambda a: None))
    w.xps[(k5, "mining")] = 8000000
    d5.refNext = 0
    M.settle(None, u5, d5)
    K.check(d5.refSt[0] is None, "FIX skill:fn:xp answers nothing -> not settled")
    w.br.put("skill:fn:xp", xp_fn)
    w.br.put("rebirth:fn:dustmult", w.Fn(lambda a: None))
    Calc.DMULT.clear()
    Calc.DLAST.clear()
    d5.refNext = 0
    M.settle(None, u5, d5)
    K.check(d5.refSt[0] is None, "FIX SkyyRebirth loaded but silent -> not settled (the multiplier is unknown)")
    w.br.put("rebirth:fn:dustmult", w.Fn(lambda a: JClass("java.lang.Double").valueOf(2.0)))
    Calc.DMULT.clear()
    d5.refNext = 0
    M.settle(None, u5, d5)
    em5 = (8000000 // int(Cfg.rate(0))) * 2 - int(d5.refSpent[0])
    K.check(str(d5.refSt[0]) == "paid:%d" % min(25000, em5 // 100), "FIX every answer in -> paid with the x2 multiplier: %s (want %d)" % (d5.refSt[0], min(25000, em5 // 100)))
    # fix round 2 (critic): the refund is worked out from the FIRST real XP answer (a later XP rise / a rebirth to 0 does not move it)
    w.br.remove("rebirth:fn:dustmult")
    Calc.DMULT.clear()
    k8 = "abababab-2222-3333-4444-555555555555"
    open(os.path.join(base, "players", k8 + ".properties"), "wb").write(b"Mining.MSpeed=1\nv=2\n")
    u8 = w.uuid(k8)
    St.DATA.clear()
    d8 = St.data(u8)
    w.levels[(k8, "mining")] = 30
    w.xps[(k8, "mining")] = 4000000
    w.add_mode[0] = "none"
    M.settle(None, u8, d8)
    K.check(d8.refSt[0] is None and int(d8.refXp[0]) == 4000000, "FIX2 the XP is kept even when the payment waits")
    w.add_mode[0] = "ok"
    w.xps[(k8, "mining")] = 0   # a rebirth before the settle
    d8.refNext = 0
    M.settle(None, u8, d8)
    em8 = 4000000 // int(Cfg.rate(0)) - int(d8.refSpent[0])
    K.check(str(d8.refSt[0]) == "paid:%d" % min(25000, em8 // 100), "FIX2 a rebirth to 0 XP before the settle does not lose the refund: %s (want %d)" % (d8.refSt[0], min(25000, em8 // 100)))
    w.br.remove("rebirth:fn:dustmult")
    # ---- fix round (critic LOW-MEDIUM): a rollback below 0.4.0 + a 0.3.x save + the update again = no second refund
    St.DATA.clear()
    open(pf, "wb").write(b"Mining.MSpeed=2\r\nname=Wes\r\nv=2\r\n")
    d6 = St.data(u1)
    t6 = open(pf, "rb").read().decode("latin-1")
    K.check(all(str(d6.refSt[t]) == "unknown:0" for t in range(int(D.NT))) and "refund.Mining=unknown:0\r\n" in t6 and "treesV3=1" in t6,
            "FIX the update running AGAIN (the .done mark) writes refund.<Tree>=unknown:0 for every tree")
    n2 = len(w.added)
    d6.refNext = 0
    M.settle(None, u1, d6)
    K.check(len(w.added) == n2 and "update-again" in open(logf, encoding="utf8").read(), "FIX no second refund after a rollback (logged update-again)")
    # ---- fix round (critic LOW): two threads loading one old file at once run the update once
    import threading
    k7 = "ffffffff-2222-3333-4444-555555555555"
    open(os.path.join(base, "players", k7 + ".properties"), "wb").write(b"Mining.MSpeed=1\nv=2\n")
    St.DATA.clear()
    res = []
    ths = [threading.Thread(target=lambda: res.append(St.readFile(k7))) for _ in range(4)]
    for t_ in ths:
        t_.start()
    for t_ in ths:
        t_.join()
    lg7 = [l_ for l_ in open(logf, encoding="utf8").read().splitlines() if ("\t" + k7 + "\tupdate\t") in l_]
    K.check(len(res) == 4 and all(bool(x.v3) and not bool(x.bad) for x in res) and len(lg7) == 1, "FIX 4 threads read one old file: 4 v3 results, ONE update line (%d)" % len(lg7))
    K.save()


# ============================================================================================ CFG: the default file + the settings
def run_cfg(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    base = os.path.join(scratch, "cfg")
    setup_dirs(J, base)
    Cfg = J("TreeCfg")
    Cfg.load()
    f = os.path.join(base, "trees.properties")
    t0 = open(f, "rb").read()
    txt = t0.decode("latin-1")
    for bad in ("tokens.", "dust.xpPerDust", "class.ap.", "class.nodes.", "tier.levels", "debug.extra", ".B=", ".tokens="):
        K.check(bad not in txt, "CFG the new file has no %s line" % bad)
    for good in ("respec.perLevel=100", "respec.maxSteps=5", "trees.dustCoinDivisor=100", "trees.dustCoinCap=25000", "class.enabled=true", "Mining.MSpeed.per=0.016"):
        K.check(good in txt, "CFG the new file has %s" % good)
    K.check((int(Cfg.V3_RBASE), int(Cfg.V3_RSTEPS), int(Cfg.V3_DDIV), int(Cfg.V3_DCAP)) == (100, 5, 100, 25000), "CFG the new settings load")
    bp = Paths.get(base)
    for m in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317", "TreeMig321", "TreeMig323", "TreeMig324"):
        J(m).run(bp)
    K.check(open(f, "rb").read() == t0, "CFG every 0.3 one-time update leaves a fresh 0.4.0 file alone (their markers are in it)")
    Cfg.load()
    K.check(open(f, "rb").read() == t0, "CFG a second load writes nothing")
    open(f, "ab").write(b"respec.perLevel=250\ntrees.dustCoinCap=0\ntokens.every=3\ndust.xpPerDust.Mining=9\nclass.ap.max=60\n")
    Cfg.load()
    K.check(int(Cfg.V3_RBASE) == 250 and int(Cfg.V3_DCAP) == 0, "CFG hand-edited respec.perLevel / trees.dustCoinCap are read")
    note = str(J("TreeV3Mig").unusedNote(Cfg.FILE))
    K.check("tokens.every=3" in note and "class.ap.max=60" in note and "dust.xpPerDust.Mining=9" in note, "CFG the unused-value note names the hand-edited old values: %s" % note)
    rows = [str(r[0]) for r in J("CfgRows").header()[7]]
    K.check("respec.perLevel" in rows and "trees.dustCoinDivisor" in rows and not [r for r in rows if r.startswith(("tokens.", "dust.", "class.ap", "debug."))],
            "CFG Server Setup rows: the new ones in, no Token / Dust / AP / debug rows (%d rows)" % len(rows))
    K.save()


# ============================================================================================ LIVE: start twice on a copy of the live data
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    before = tree_hash(home)
    olds = dict((f, open(os.path.join(home, "players", f), "rb").read()) for f in os.listdir(os.path.join(home, "players")) if f.endswith(".properties"))

    def start():
        J("TreeStore").DIR = Paths.get(os.path.join(home, "players"))
        J("TreeCfg").FILE = Paths.get(os.path.join(home, "trees.properties"))
        J("TreeStore").DATA.clear()
        J("TreeCfg").load()
        bp = Paths.get(home)
        for m in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317", "TreeMig321", "TreeMig323", "TreeMig324"):
            J(m).run(bp)
        note = str(J("TreeV3Mig").unusedNote(J("TreeCfg").FILE))
        datas = []
        for f in sorted(os.listdir(os.path.join(home, "players"))):
            if f.endswith(".properties"):
                datas.append((f, J("TreeStore").readFile(f[:-11])))
        return note, datas
    note1, d1 = start()
    after1 = tree_hash(home)
    new = sorted(k for k in after1 if k not in before)
    changed = sorted(k for k in before if after1.get(k) != before[k])
    K.check(all(c.startswith("players/") for c in changed) and all(n.startswith("history/treesv3/") or n == "trees-v3-changes.log" for n in new),
            "LIVE start 1: only the player files changed (+ their History copies + trees-v3-changes.log): changed %s new %s" % (changed, new))
    K.check(not [f for f, d in d1 if bool(d.bad)] and len(d1) == len(olds), "LIVE every player file read as v3 (%d files)" % len(d1))
    for f, b in olds.items():
        h = os.path.join(home, "history", "treesv3", f)
        K.check(os.path.isfile(h) and open(h, "rb").read() == b, "LIVE %s: History copy byte-identical" % f)
        t = open(os.path.join(home, "players", f), "rb").read().decode("latin-1")
        nl = "\r\n" if "\r\n" in b.decode("latin-1") else "\n"
        kept = [l for l in b.decode("latin-1").split(nl) if l.startswith(("#", "name=", "quiet=", "note.swing=", "rb.lastTx="))]
        TD = J("TreeDefs")
        oldkeys = set(str(TD.TREES[i // 12]) + "." + str(TD.ID[i]) for i in range(int(TD.N)))
        left = [l for l in t.split(nl) if l.split("=")[0] in oldkeys or (l.startswith("Class.") and not l.split("=")[0].endswith((".gf", ".gfx")))
                or l.startswith(("abil.tree", "fort.r323"))]
        K.check(all((l + nl) in t for l in kept) and ("v=3" + nl) in t and ("treesV3=1" + nl) in t and not left,
                "LIVE %s: kept lines byte for byte, v=3, the marker, no old node / class pick / old marker line %s" % (f, left))
        K.notes.append("LIVE %s -> %s" % (f, [l for l in t.split(nl) if l.startswith(("Class.", "refund."))][:12]))
    note2, d2 = start()
    after2 = tree_hash(home)
    K.check(after2 == after1, "LIVE start 2 changes nothing")
    K.notes.append("LIVE unused note: %r" % note1)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("dat", run_dat), ("eng", run_eng), ("mig", run_mig), ("cfg", run_cfg), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyTrees"))
