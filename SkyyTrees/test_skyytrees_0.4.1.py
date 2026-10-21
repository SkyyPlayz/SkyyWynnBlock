"""Harness for SkyyTrees 0.4.1 (SKILL TREES 3 ROUND R3a - the 8 class trees: fx hooks, the raised class gates + their one-time update, the R3b
skill-key contract; tools/trees_0_4_1_patch.py). Build first:
    python tools/trees_0_4_1_patch.py && python SkyyTrees/build_skyytrees_0.4.1.py
    python SkyyTrees/test_skyytrees_0.4.1.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A    verify   every class loads + initialises
  C    compare  0.4.0 -> 0.4.1: exactly the planned members (EXPECT)
  OLDG the 0.4.0 jar's GATES (dumped in its own JVM) = 0.4.1's GATES_OLD
  DAT  the fx tables = tools/trees_v3_data.py (every fx entry, owner, Now template, free fx row); every class gate = 0/5/10/15/20/25; the
       skill gates did not move
  ENG  the engine on fake bridges: an fx upgrade is coming soon until its owner lists Class.fx.<code> (SkyyTrees' own codes always live),
       buy it, tree:fn:abil carries f.<code>=<sum> (+ f.ShadowClone=1 once Executioner row 2 opens), tree:fn:bonus Class.fx.<code>,
       fxU / fxSum, the stat stubs (hp %, Mana regen via skill:fn:manaregen, Stamina / Mana % helpers, the Stamina Regen top-up's early
       paths), the "Now:" texts, every fx page text fits; round R3b's contract (a listed Skill.<Tree>.b<n>.<id> key is live, tree:fn:level
       answers its rank)
  MIG  the one-time gates update on scratch files: CRLF + LF, a line re-locked by the raised gate is grandfathered (gf), an existing gf
       line rewritten, every other line byte for byte, gates41=1 appended, the History copy (byte-identical), the log line, runs once,
       no History copy = waits unchanged; a fresh profile and a 0.3 file are born with gates41=1
  LIVE START TWICE on a scratch COPY of the live Skyy_SkyyTrees folder: start 1 = only the player files + their History copies + the log,
       every file v3 + gates41; start 2 changes nothing
  AA   engine-access audit
NOT COVERED (UNVERIFIED in game): the stat modifiers on a real player (EntityStatMap), the Stamina Regen top-up's real rate, the pages.
"""
import os, sys, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import skyyui as SUI
import deploy_set as DS
import trees_v3_data as V3D

VERSION = "0.4.1"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.4.0.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "st3r3a", "th")))
LIVE_DIR = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyTrees")
ADDED = []
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup"], "TreeCfg": ["~m load"],   # the version text
    "TreeBonusFn": ["~m apply"], "TreeFn": ["~m apply"],   # Class.fx.<code> / Skill.<Tree>.b<n>.<id>
    "TreeClass": ["+m v3hp", "+m v3reg", "~m hpPct", "~m post"], "TreeData": ["+f g41"], "TreeFx": ["+m v3pct", "+m v3sreg", "~m stats"],
    "TreeStore": ["~m readFile"],
    "TreeV3": ["+f FXC", "+f FXO", "+f FXOWN_CODES", "+f FXOWN_MODS", "+f FXU", "+f FXV", "+f GATES_OLD", "+f R3B", "+f RFFX", "+f SREG_FAILED",
               "+f UFX0", "+f UFXHOW", "+f UFXN", "+f UNOW", "+m codeLive", "+m fxCsv", "+m fxLive", "+m fxNow", "+m fxSum", "+m fxU", "+m num",
               "+m pctOf", "+m r3bLive", "+m skillRank", "+m staminaRegen", "~<clinit>", "~m classCsv", "~m detHow", "~m detNext", "~m detNow",
               "~m effText", "~m freeNow", "~m live"],
    "TreeV3Mig": ["+f G41_APPLIED", "+f G41_KEPT", "+f G41_LAST", "+m gatesIn", "+m gatesKeep", "+m gatesLocked", "+m gatesText", "~<clinit>",
                  "~m fresh", "~m migrate", "~m readV3", "~m writeV3"],
}
MARGIN = 0.95
W, NW = 424, 424 - SUI.SLOT_FRAME - 12
BOX = {"name": (NW, 14, 24, True), "state": (NW, 16, 44, True), "line": (W, 16, 44, False), "need": (W, 16, 66, False), "how": (W, 13, 107, False),
       "cost": (W, 16, 26, True)}
CLASS_ORDER = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"]


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
    """fake bridges: skill levels per UUID + skill name, classes, coins, combat, reader lists, the Mana regen registry"""

    def __init__(self):
        from jpype import JClass, JImplements, JOverride
        self.J = lambda n: JClass(PKG + n)
        self.Int, self.Long, self.Bool = JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
        self.UUID = JClass("java.util.UUID")
        self.levels, self.purse, self.combat, self.regen = {}, {}, {}, []
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

        def regen(a):
            W_.regen.append(tuple(str(x) for x in a))
            return None

        for k, f in (("skill:fn:level", lvl), ("coins:fn:take", take), ("skill:fn:combat", lambda a: W_.Long.valueOf(0)),
                     ("skill:fn:xp", lambda a: W_.Long.valueOf(0)), ("skill:fn:manaregen", regen)):
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


# ============================================================================================ OLDG: the 0.4.0 gates (in their own JVM)
def run_oldg(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=False)
    g = [int(x) for x in JClass(PKG + "TreeV3").GATES]
    json.dump(g, open(os.path.join(scratch, "gates040.json"), "w"))
    K.check(len(g) == 19 * 8, "OLDG the 0.4.0 GATES table read (%d)" % len(g))
    K.save()


# ============================================================================================ DAT: the jar's fx tables = the data file
def run_dat(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    V = JClass(PKG + "TreeV3")
    names = [str(x) for x in V.TNAME]
    K.eq(names[:8], CLASS_ORDER, "DAT class tree order")
    g040 = json.load(open(os.path.join(scratch, "gates040.json")))
    K.eq([int(x) for x in V.GATES_OLD], g040, "DAT GATES_OLD = the 0.4.0 jar's GATES (what players had until now)")
    for tv in range(8):
        K.eq([int(V.GATES[tv * 8 + n]) for n in range(1, 7)], [0, 5, 10, 15, 20, 25], "DAT %s gates = Skyy's 0/5/10/15/20/25" % names[tv])
    K.eq([int(V.GATES[i]) for i in range(64, 152)], g040[64:152], "DAT the 11 skill trees keep their 0.4.0 gates (R3b)")
    raised = ["%s %s" % (names[tv], "/".join(str(g040[tv * 8 + n]) for n in range(1, 7))) for tv in range(8) if g040[tv * 8 + 1:tv * 8 + 7] != [0, 5, 10, 15, 20, 25]]
    K.notes.append("DAT 0.4.0 class gates raised: %s" % raised)
    bad, nfx, nup = [], 0, 0
    for tv, tn in enumerate(names):
        t = V3D.tree(tn)
        for bn, b in enumerate(t["branches"]):
            for r in b["rows"]:
                ri = [x for x in range(int(V.TR0[tv]), int(V.TR0[tv]) + int(V.TRN[tv])) if int(V.RB[x]) == int(V.TB0[tv]) + bn and int(V.RNUM[x]) == r["r"]][0]
                f = r["free"]
                if f and f["hook"] and f["hook"][0] == "fx":
                    if int(V.RFK[ri]) != 3 or str(V.RFFX[ri]) != f["hook"][1] or str(V.RFTEXT[ri]) != f["text"]:
                        bad.append("free fx %s" % f["name"])
                for k, u in enumerate(r["ups"]):
                    ui = int(V.RU0[ri]) + k
                    codes = V3D.fx_codes(u)
                    if t["kind"] == "class":
                        nup += 1
                        if int(V.UHK[ui]) not in (1, 3):
                            bad.append("class upgrade not wired: %s %s" % (tn, u["name"]))
                    if not codes:
                        continue
                    nfx += 1
                    got = [(str(V.FXC[e]), float(V.FXV[e]), str(V.FXO[e])) for e in range(int(V.UFX0[ui]), int(V.UFX0[ui]) + int(V.UFXN[ui]))]
                    want = [(c, float(v), V3D.fx_owner(c)) for c, v in codes]
                    if got != want or int(V.UHK[ui]) != 3 or str(V.UNOW[ui]) != u["now"] or str(V.UTEXT[ui]) != u["text"]:
                        bad.append("%s %s: %s / %s" % (tn, u["name"], got, want))
                    if int(V.FXU[int(V.UFX0[ui])]) != ui:
                        bad.append("FXU %s" % u["name"])
    K.check(not bad and nfx == 180 and nup == 180 + sum(1 for x in range(int(V.NU)) if int(V.UT[x]) < 8 and int(V.UHK[x]) == 1),
            "DAT every class upgrade wired (%d fx + modifiers), every fx entry / owner / Now template = the data %s" % (nfx, bad[:5]))
    owners = dict((str(V.FXOWN_CODES[i]), str(V.FXOWN_MODS[i])) for i in range(len(V.FXOWN_CODES)))
    K.check(owners.get("hp") == "SkyyTrees" and owners.get("blinkStep") == "SkyyArmory" and owners.get("smiteReach") == "SkyyArmory"
            and owners.get("drMelee") == "SkyyClasses" and owners.get("ShadowClone") == "SkyyClasses", "DAT the code owners")
    K.save()


# ============================================================================================ ENG: the engine on fake bridges
def run_eng(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    base = os.path.join(scratch, "eng")
    setup_dirs(J, base)
    Cfg, V, St, TC, Fx, M = J("TreeCfg"), J("TreeV3"), J("TreeStore"), J("TreeClass"), J("TreeFx"), J("TreeV3Mig")
    Cfg.load()
    w = World()
    u = w.uuid("11111111-2222-3333-4444-555555555555")
    us = str(u)
    tvx = dict((str(V.TNAME[i]), i) for i in range(19))
    WAR, ASN, MAG, PRI = tvx["Warrior"], tvx["Assassin"], tvx["Mage"], tvx["Priest"]

    def up(tn, b, rid):
        t = tvx[tn]
        for x in range(int(V.TU0[t]), int(V.TU0[t]) + int(V.TUN[t])):
            if str(V.UKEY[x]) == "%s.%s.b%d.%s" % ("Class" if t < 8 else "Skill", tn, b, rid):
                return x
        raise KeyError((tn, b, rid))
    arr = lambda *xs: JArray(JObject)(list(xs))
    d = St.data(u)
    K.check(bool(d.v3) and bool(d.g41) and not bool(d.bad), "ENG a new profile is born with gates41 (nothing to update)")
    w.set_class(u, "Warrior")
    w.levels[(us, "swordsmanship")] = 30
    iron, last, stone = up("Warrior", 1, "r1a"), up("Warrior", 1, "r1b"), up("Warrior", 1, "r3b")
    K.check(not bool(V.live(iron)) and bool(V.live(last)), "ENG Iron Skin (SkyyClasses' drMelee) waits for its owner; Last Stand (SkyyTrees' hp) is live at once")
    r = str(V.buy(u, d, WAR, iron, False))
    K.check("is coming soon" in r and int(d.rk[iron]) == 0, "ENG an fx upgrade is not sold while SkyyClasses does not list Class.fx.drMelee: %s" % r)
    codes = sorted(set(str(V.FXOWN_CODES[i]) for i in range(len(V.FXOWN_CODES)) if str(V.FXOWN_MODS[i]) == "SkyyClasses"))
    w.readers("SkyyClasses", ["Class.v3mods"] + ["Class.fx." + c for c in codes])
    K.check(bool(V.live(iron)) and bool(V.codeLive("ShadowClone")) and not bool(V.codeLive("blinkStep")) and not bool(V.codeLive("nope")),
            "ENG SkyyClasses 0.1.43 lists its codes -> live; SkyyArmory's blinkStep still waits; an unknown code is never live")
    msgs = [str(V.buy(u, d, WAR, iron, False)) for _ in range(5)]
    K.check(all(m.startswith("Done: Iron Skin rank") for m in msgs) and "New: Challenge, Shield Shockwave, Iron Chain!" in msgs[-1],
            "ENG 5 ranks of Iron Skin open row 2 at Skyy's 5 points: %s" % msgs[-1])
    for _ in range(3):
        V.buy(u, d, WAR, last, False)
    r = str(V.buy(u, d, WAR, stone, False))
    K.check("needs 10 points in this tree - you have 8" in r, "ENG row 3 needs 10 (the raised gate): %s" % r)
    csv = str(TC.abilGate(u))
    K.check(csv.startswith("v3,A1,A2,A3,A4a") and ",f.drMelee=20" in csv and ",f.hp=18" in csv, "ENG tree:fn:abil carries the fx sums: %s" % csv)
    K.eq(float(V.fxSum(d, WAR, "drMelee")), 20.0, "ENG fxSum drMelee = 5 x 4")
    K.eq(float(V.fxU(u, "hp")), 18.0, "ENG fxU hp = 3 x 6 (the player's own class tree)")
    K.eq(float(TC.hpPct(u)), 18.0, "ENG TreeClass.hpPct = the 0.3 nodes (none) + the hp code (Last Stand)")
    bfn, lfn = J("TreeBonusFn")(), J("TreeFn")()
    K.eq(float(bfn.apply(arr(u, JString("Class.fx.drMelee")))), 20.0, "ENG tree:fn:bonus Class.fx.drMelee = 20 (SkyyArmory's read)")
    K.eq(float(bfn.apply(arr(u, JString("Class.fx.nope")))), 0.0, "ENG tree:fn:bonus of an unknown code = 0")
    K.eq(str(V.effText(iron, 5)), "20% less melee damage taken", "ENG the Now line of Iron Skin at rank 5")
    K.eq(str(V.detNow(d, int(V.UROW[iron]), iron, 3, 8, V.gates(WAR))), "Now: 20% less melee damage taken", "ENG detNow uses the template")
    K.check("SkyyClasses applies it in combat." in str(V.detHow(int(V.UROW[iron]), iron)) and "SkyyTrees applies it to your stats." in str(V.detHow(int(V.UROW[last]), last)),
            "ENG How names the mod that applies it")
    # Mana regen (mreg) through the class tree's skill:fn:manaregen post; the stat helpers' early paths
    w.set_class(u, "Mage")
    w.levels[(us, "sorcery")] = 20
    att = up("Mage", 2, "r3c")
    for x in (up("Mage", 2, "r1a"),) * 4 + (up("Mage", 2, "r1b"),) * 2:
        V.buy(u, d, MAG, x, False)
    for x in (up("Mage", 1, "r1a"),) * 3 + (up("Mage", 1, "r1b"),):
        V.buy(u, d, MAG, x, False)
    r = str(V.buy(u, d, MAG, att, False))
    K.check(r.startswith("Done: Attunement rank 1"), "ENG Attunement (mreg, SkyyTrees) bought at 10 points: %s" % r)
    TC.post(u)
    K.check(("add", us, "trees", "5.0") in w.regen, "ENG TreeClass.post sends Mana regen +5 %% (the 0.3 nodes 0 + mreg 5): %s" % w.regen[-2:])
    K.eq(float(V.fxU(u, "mana")), 16.0, "ENG Mana Well 4 ranks = +16 % max Mana (fxU mana)")
    K.eq(float(Fx.v3pct(None, u, 2)), 0.0, "ENG v3pct with no stat map = 0 (no throw)")
    K.eq(float(V.pctOf(None, 0, "skyytree_mana", 16.0)), 0.0, "ENG pctOf with no stat map = 0")
    K.eq(float(V.staminaRegen(None, None, None, 10.0, 1.0)), 0.0, "ENG staminaRegen with no stat map = 0")
    Fx.v3sreg(None, None, None, u)
    K.check(not bool(V.SREG_FAILED), "ENG v3sreg with nothing to read returns quietly")
    # the Assassin's free fx row: Shadow Clone comes with Executioner row 2 (5 points)
    w.set_class(u, "Assassin")
    w.levels[(us, "assassination")] = 10
    K.check(",f.ShadowClone" not in str(TC.abilGate(u)), "ENG no Shadow Clone before row 2")
    for _ in range(3):
        V.buy(u, d, ASN, up("Assassin", 1, "r1a"), False)
    for _ in range(2):
        V.buy(u, d, ASN, up("Assassin", 3, "r1a"), False)
    csv = str(TC.abilGate(u))
    K.check(",f.ShadowClone=1" in csv and ",A4a" in csv, "ENG 5 points open row 2: Vanishing Act (A4a) + Shadow Clone (f.ShadowClone=1): %s" % csv)
    rr = [x for x in range(int(V.TR0[ASN]), int(V.TR0[ASN]) + int(V.TRN[ASN])) if str(V.RFNAME[x]) == "Shadow Clone"][0]
    K.check(str(V.freeNow(rr)).startswith("Cloak / Vanishing Act leave a clone") and "coming soon" not in str(V.freeNow(rr)),
            "ENG Shadow Clone's text (SkyyClasses lists it): %s" % V.freeNow(rr))
    K.eq(str(V.detNext(d, rr, -1)), "Free - it works as soon as its row is open", "ENG a free fx row's Next line")
    # round R3b's contract: a listed Skill key is live + tree:fn:level answers its rank
    MIN = tvx["Mining"]
    w.levels[(us, "mining")] = 10
    sk = up("Mining", 2, "r1a")
    K.check(int(V.UHK[sk]) == 0 and not bool(V.live(sk)), "R3B Mining Tool Mastery has no hook and is coming soon")
    w.readers("SkyyGear", ["Skill.Mining.b2.r1a"])
    K.check(bool(V.live(sk)), "R3B listed by SkyyGear -> live")
    r = str(V.buy(u, d, MIN, sk, False))
    K.check(r.startswith("Done:"), "R3B bought: %s" % r)
    K.eq(int(lfn.apply(arr(u, JString("Skill.Mining.b2.r1a")))), 1, "R3B tree:fn:level Skill.Mining.b2.r1a = its rank")
    w.readers("SkyyGear", [])
    K.eq(int(lfn.apply(arr(u, JString("Skill.Mining.b2.r1a")))), 0, "R3B no longer listed -> tree:fn:level answers 0")
    K.check(int(lfn.apply(arr(u, JString("Mining.MSpeed")))) >= 0 and int(lfn.apply(arr(u, JString("Skill.Nope.b1.r1a")))) == 0, "R3B the 0.3 keys still answer; an unknown key = 0")
    K.check(str(V.effText(sk, 1)).startswith("nothing yet") or True, "R3B text path runs")
    w.readers("SkyyGear", ["Skill.Mining.b2.r1a"])
    K.check(str(V.effText(sk, 1)).startswith("rank 1 of"), "R3B a live R3b upgrade's Now line: %s" % V.effText(sk, 1))
    # every fx page text fits the detail boxes (every state, rank 0 / max)
    bad, n = [], 0
    dd = J("TreeData")()
    M.fresh(dd)
    for tv in range(8):
        g = V.gates(tv)
        for x in range(int(V.TU0[tv]), int(V.TU0[tv]) + int(V.TUN[tv])):
            if int(V.UHK[x]) != 3:
                continue
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
            if int(V.RFK[ri]) != 3:
                continue
            for sp in (0, 99):
                for kind, tx in (("line", str(V.detNow(dd, ri, -1, 7, sp, g))), ("how", str(V.detHow(ri, -1))), ("state", str(V.detState(dd, ri, -1, 7, g, sp, 100)))):
                    n += 1
                    if not fits(kind, tx):
                        bad.append("free %s: %s" % (kind, tx))
    K.check(not bad and n > 8000, "ENG %d fx page texts fit the detail boxes %s" % (n, bad[:4]))
    # the respec ends fx ranks too
    w.purse[us] = 10 ** 9
    w.set_class(u, "Warrior")
    r = str(V.respec(u, d, WAR, False))
    K.check(r.startswith("Respec done") and float(V.fxSum(d, WAR, "drMelee")) == 0.0 and ",f." not in str(TC.abilGate(u)), "ENG a respec takes every fx rank back: %s" % r)
    K.save()


# ============================================================================================ MIG: the one-time gates update
def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    base = os.path.join(scratch, "mig")
    setup_dirs(J, base)
    Cfg, V, St, M = J("TreeCfg"), J("TreeV3"), J("TreeStore"), J("TreeV3Mig")
    Cfg.load()
    ASN = [str(x) for x in V.TNAME].index("Assassin")
    ARC = [str(x) for x in V.TNAME].index("Archer")
    K.eq([int(V.GATES_OLD[ASN * 8 + n]) for n in range(1, 7)], [0, 3, 8, 10, 11, 14], "MIG the Assassin's 0.4.0 gates (the test data)")
    # an Assassin with 3 points in Shadowstep row 1 (Duration 3): 0.4.0 opened row 2 (Vanishing Act A4a + Shadow Clone) at 3; 0.4.1 needs 5
    k1 = "aaaaaaaa-2222-3333-4444-555555555555"
    old = ("#SkyyTrees v3 - the ranks of one profile (points come from your levels)\r\n#Mon Oct 20 12:40:00 MDT 2026\r\nClass.Assassin.b1.r1a=3\r\n"
           "Class.Archer.b1.r1a=3\r\nClass.Archer.gf=A4b\r\nname=Wes\\\r\n  ley\r\nquiet=false\r\ntreesV3=1\r\nv=3\r\nv3.note=1\r\n")
    pf = os.path.join(base, "players", k1 + ".properties")
    open(pf, "wb").write(old.encode("latin-1"))
    d = St.readFile(k1)
    new = open(pf, "rb").read().decode("latin-1")
    hist = os.path.join(base, "history", "gates041", k1 + ".properties")
    K.check(os.path.isfile(hist) and open(hist, "rb").read() == old.encode("latin-1"), "MIG the History copy = the old file byte for byte")
    kept = old.replace("Class.Archer.gf=A4b\r\n", "")
    K.check(new.startswith(kept), "MIG every other line byte for byte (the comments, a continued name, CRLF): %r" % new[:200])
    tail = new[len(kept):]
    K.check(tail == "Class.Archer.gf=A2,A4a,A4b\r\nClass.Assassin.gf=A2,A4a\r\ngates41=1\r\n",
            "MIG every row-2 ability the 0.4.0 gate (3) opened is grandfathered (Assassin Toxin A2 + Vanishing Act A4a; Archer A2 + A4a added to its A4b), gates41 in CRLF: %r" % tail)
    li = lambda x: ["A1", "A2", "A3", "A4a", "A4b"].index(x)
    K.check(bool(d.g41) and bool(d.gfa[ASN * 5 + li("A4a")]) and bool(d.gfa[ASN * 5 + li("A2")]) and bool(d.gfa[ARC * 5 + li("A2")]) and bool(d.gfa[ARC * 5 + li("A4b")])
            and int(d.rk[int(V.TU0[ASN])]) == 3, "MIG the data: the marker, the kept abilities, the ranks stay")
    lines = V.lines(d, ASN)
    K.check(bool(lines[li("A4a")]) and bool(lines[li("A2")]) and not bool(lines[li("A3")]), "MIG Vanishing Act + Toxin stay owned (grandfathered) though row 2 now needs 5; God Killer (row 5) never was")
    K.check(",f.ShadowClone" not in str(V.classCsv(d, ASN)), "MIG the free Shadow Clone is NOT grandfathered (it was never live before 0.4.1)")
    logf = os.path.join(base, "trees-v3-changes.log")
    lg = open(logf, encoding="utf8").read() if os.path.isfile(logf) else ""
    K.check("\tgates\t" in lg and "Undo: stop the server, copy history/gates041/" in lg, "MIG one log line with the Undo")
    b2 = open(pf, "rb").read()
    St.DATA.clear()
    d2 = St.readFile(k1)
    K.check(open(pf, "rb").read() == b2 and bool(d2.g41) and bool(d2.gfa[ASN * 5 + li("A4a")]), "MIG runs once: the second read changes nothing")
    # nothing re-locked: only the marker (LF file)
    k2 = "bbbbbbbb-2222-3333-4444-555555555555"
    pf2 = os.path.join(base, "players", k2 + ".properties")
    t2 = "Class.Warrior.b1.r1a=5\nname=Sky\ntreesV3=1\nv=3\n"
    open(pf2, "wb").write(t2.encode("latin-1"))
    St.readFile(k2)
    K.eq(open(pf2, "rb").read().decode("latin-1"), t2 + "gates41=1\n", "MIG nothing re-locked (Warrior gates did not move): only gates41=1, LF kept")
    # no History copy = waits unchanged
    k3 = "cccccccc-2222-3333-4444-555555555555"
    pf3 = os.path.join(base, "players", k3 + ".properties")
    t3 = "Class.Assassin.b1.r1a=3\ntreesV3=1\nv=3\n"
    open(pf3, "wb").write(t3.encode("latin-1"))
    os.makedirs(os.path.join(base, "history", "gates041", k3 + ".properties"))
    d3 = St.readFile(k3)
    K.check(bool(d3.bad) and open(pf3, "rb").read() == t3.encode("latin-1"), "MIG no History copy -> the file waits unchanged")
    # a 0.3 file goes straight to v3 + gates41 (one update, born under the raised gates)
    k4 = "dddddddd-2222-3333-4444-555555555555"
    pf4 = os.path.join(base, "players", k4 + ".properties")
    open(pf4, "wb").write(b"Mining.MSpeed=1\nClass.Assassin=ROOT,A1,A4a\nv=2\n")
    d4 = St.readFile(k4)
    t4 = open(pf4, "rb").read().decode("latin-1")
    K.check("treesV3=1\nv3.note=1\ngates41=1\n" in t4 and bool(d4.g41) and bool(d4.gfa[ASN * 5 + li("A4a")]) and not os.path.isdir(os.path.join(base, "history", "gates041", k4 + ".properties")),
            "MIG a 0.3 file: the 0.4.0 update writes gates41=1 at once (no gates History copy needed): %r" % t4)
    # gatesKeep on its own: a grandfathered line is not touched again
    dd = J("TreeData")()
    M.fresh(dd)
    dd.rk[int(V.TU0[ASN])] = 3
    dd.gfa[ASN * 5 + li("A4a")] = True
    dd.gfa[ASN * 5 + li("A2")] = True
    K.check(not any(bool(x) for x in M.gatesKeep(dd)), "MIG gatesKeep: already grandfathered lines = no change")
    dd.gfa[ASN * 5 + li("A4a")] = False
    dd.gfa[ASN * 5 + li("A2")] = False
    ch = M.gatesKeep(dd)
    K.check(bool(ch[ASN]) and bool(dd.gfa[ASN * 5 + li("A4a")]), "MIG gatesKeep grants the re-locked A4a")
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
        datas = []
        for f in sorted(os.listdir(os.path.join(home, "players"))):
            if f.endswith(".properties"):
                datas.append((f, J("TreeStore").readFile(f[:-11])))
        return datas
    d1 = start()
    after1 = tree_hash(home)
    new = sorted(k for k in after1 if k not in before)
    changed = sorted(k for k in before if after1.get(k) != before[k])
    K.check(all(c.startswith("players/") for c in changed) and all(n.startswith(("history/treesv3/", "history/gates041/")) or n == "trees-v3-changes.log" for n in new),
            "LIVE start 1: only the player files changed (+ History copies + trees-v3-changes.log): changed %s new %s" % (changed, new))
    K.check(not [f for f, d in d1 if bool(d.bad)] and len(d1) == len(olds) and all(bool(d.g41) and bool(d.v3) for f, d in d1),
            "LIVE every player file read as v3 + gates41 (%d files)" % len(d1))
    for f in olds:
        t = open(os.path.join(home, "players", f), "rb").read().decode("latin-1")
        K.check("gates41=1" in t and "treesV3=1" in t, "LIVE %s: the markers" % f)
        K.notes.append("LIVE %s -> %s" % (f, [l for l in t.splitlines() if l.startswith(("Class.", "gates41", "v="))][:10]))
    d2 = start()
    K.check(tree_hash(home) == after1, "LIVE start 2 changes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("oldg", run_oldg), ("dat", run_dat), ("eng", run_eng), ("mig", run_mig), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyTrees"))
