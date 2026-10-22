"""Harness for SkyyTrees 0.4.6 (Balance P8b: the essential skill trees Mining / Foraging / Combat row by row; tools/trees_0_4_6_patch.py +
tools/trees_v3_data.py + tools/trees_v3_effects.py). Build first:
    python tools/trees_0_4_6_patch.py && python SkyyTrees/build_skyytrees_0.4.6.py
    python SkyyTrees/test_skyytrees_0.4.6.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S    static   the patch re-runs to identical bytes; line endings kept; one class added (TreeSk); no new system / command
  A    verify   every class loads + initialises
  C    compare  0.4.5 -> 0.4.6: exactly the planned members (EXPECT)
  OLD  the 0.4.5 jar's TreeV3 tables (dumped in its own JVM)
  DATA vs 0.4.5: no upgrade max / cost / key / name changed (nothing to clamp); the texts change exactly on the P8b upgrades; 3 upgrades
       become 0.3 node aliases (UHK 0 -> 2); 2 free perks RFK 4 with their keys; the gates only rise and only Combat rows 3 / 4 move
       (8 -> 10, 13 -> 15); R3B + SkyyTrees / SkyyClasses / SkyyMobs; TreeSk's 16 rows = trees_v3_effects; the budgets (check())
  X    exec     a bare JVM with scratch players: every own effect EXECUTED through the jar (TreeSk.sum / TreeFx.sk / skHp / addBonus /
       movePost / clearOne), the old aliases through derive (Chain Fortune -> Mining Wisdom 4 levels = +4 % XP in skill:bonus), the
       free perks (Stoneskin opens with row 2, tree:fn:level of the free key 1 / 0, Combat Focus live only while SkyyClasses lists it),
       live() follows tree:reads (SkyyMobs' rows dead without its list), the Server Setup numbers (a changed per / ceiling applies at once,
       a seeded tree-effects.properties), THE GRANDFATHER RULE (a rank bought in Combat row 3 at 9 points - gate 8 in 0.4.5, 10 now - stays,
       counts, and the next row-3 buy is locked)
  LIVE START TWICE on a scratch COPY of the live Skyy_SkyyTrees folder (setup's update chain + TreeSk.loadV3 + every player file read +
       derived): trees.properties unchanged (no one-time update in 0.4.6), tree-effects.properties seeded once, start 2 changes nothing
  AA   engine-access audit
NOT COVERED (UNVERIFIED in game): Vein Burst / Tree Feller breaking the extra ore / logs on a real block break, the movement source applied by
SkyySkills, the page look of the RFK 4 perks. SkyyClasses 0.1.45 / SkyyMobs 0.1.15 apply their rows (their own harnesses).
"""
import os, sys, json, hashlib, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "balp8bfix", "trees")]
import skyybuild as B
import harness_kit as HK
import deploy_set as DS
import trees_v3_data as V3D
import trees_v3_effects as V3E

VERSION = "0.4.6"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.4.5.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.4.5.py")
PATCH = os.path.join(TOOLS, "trees_0_4_6_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyTrees")
ADDED = ["TreeSk"]
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["+f DL1", "~<clinit>", "~m defLines", "~m header"], "SkyyTreesPlugin": ["~m setup", "~m shutdown"], "TreeCfg": ["~m load"],
    "CfgFile": ["~<clinit>", "~m init"],                       # the new file (tree-effects.properties)
    "TreeV3": ["~<clinit>", "+f RFKEY", "+m freeLive", "+m freeRank", "~m freeNow", "~m detNext", "~m skillRank"],
    "TreeFx": ["+f SK_SRC", "+m sk", "+m skBonus", "+m skHp", "+m skMove", "~m clearOne", "~m postBonus", "~m stats"],
    "TreeGather": ["~m felled", "~m run"], "TreeTick": ["~m tick"], "TreeKit": ["~m reloadCmd"],
}
TABLES = ("GATES", "UMAX", "UCOST", "UKEY", "UTEXT", "UNAME", "UHK", "UROW", "TU0", "TUN", "TNAME", "RNUM", "RFK", "RFTEXT", "RFNAME", "R3B")
P8B_OLDK = sorted("Skill." + k for k in V3D.P8B_OLD)
P8B_TEXTK = sorted("Skill." + k for k in V3D.P8B_TEXT if not k.endswith(".free"))
U1 = "11111111-1111-1111-1111-111111111111"   # a full P8b build
U2 = "22222222-2222-2222-2222-222222222222"   # the grandfathered Combat row 3 rank
U3 = "33333333-3333-3333-3333-333333333333"   # Mining spent 4 (Stoneskin's row 2 not open)


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def dump(V):
    o = {}
    for n in TABLES:
        o[n] = [int(y) if isinstance(y, int) else str(y) for y in getattr(V, n)]
    return o


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.4.6 - build script') and g.count('VERSION = "0.4.6"') == 1, "S header + VERSION")
    import zipfile as _zf
    _jb = b"".join(_zf.ZipFile(jar).read(_n) for _n in _zf.ZipFile(jar).namelist() if _n.endswith((".class", ".properties", ".json")))
    # fixer (critics 2026-10-22): Steady Pick's text in real % (1 Mining Speed level = Mining.MSpeed.per 0.016, LOCKED 2026-09-25); the free
    # perk's Server Setup row says "(perk)", not "a rank"; tree rows' ceiling help is the tree's own sentence
    K.check(b"+1.6% pickaxe swing speed/rank (1 Mining Speed level)" in _jb and b"+1 Mining Speed level/rank" not in _jb, "S fixer: Steady Pick says +1.6% pickaxe swing speed/rank (in the jar)")
    K.check(b"Mining Stoneskin Fall (perk)" in _jb and b"Stoneskin Fall a rank" not in _jb, "S fixer: Server Setup row 'Mining Stoneskin Fall (perk)', not 'a rank'")
    K.check(b"whatever the rank, gear or pet" not in _jb and b"gives at its top rank" in _jb, "S fixer: tree-row ceiling help is the tree's own words")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("makeClass(") - o.count("makeClass("), 1, "S one class added (TreeSk)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_old(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=False)
    o = dump(JClass(PKG + "TreeV3"))
    json.dump(o, open(os.path.join(scratch, "old045.json"), "w"))
    K.check(len(o["UKEY"]) > 0, "OLD the 0.4.5 tables read (%d upgrades, %d rows)" % (len(o["UKEY"]), len(o["RFK"])))
    K.save()


def run_data(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    V, S = JClass(PKG + "TreeV3"), JClass(PKG + "TreeSk")
    o, n = json.load(open(os.path.join(scratch, "old045.json"))), dump(V)
    for t in ("UMAX", "UCOST", "UKEY", "UNAME", "UROW", "TU0", "TUN", "TNAME", "RNUM", "RFNAME"):
        K.eq(n[t], o[t], "DATA %s unchanged (no max moved: nothing to clamp)" % t)
    txt = sorted(n["UKEY"][i] for i in range(len(n["UKEY"])) if n["UTEXT"][i] != o["UTEXT"][i])
    want = sorted(set(P8B_TEXTK) | set(P8B_OLDK))
    K.check(set(txt) <= set(want) and len(txt) >= 25, "DATA only P8b upgrade texts change (%d of %d; the rest already said it): %s" % (len(txt), len(want), sorted(set(want) - set(txt))))
    dt = {}
    for _t in V3D.TREES:
        for _bn, _b in enumerate(_t["branches"]):
            for _r in _b["rows"]:
                for _u in _r["ups"]:
                    dt["%s.%s.b%d.%s" % ("Class" if _t["kind"] == "class" else "Skill", _t["name"], _bn + 1, _u["id"])] = _u["text"]
    K.check(all(n["UTEXT"][n["UKEY"].index(k)] == dt[k] for k in want), "DATA every P8b text in the jar = tools/trees_v3_data.py")
    hk = sorted((n["UKEY"][i], o["UHK"][i], n["UHK"][i]) for i in range(len(n["UKEY"])) if n["UHK"][i] != o["UHK"][i])
    K.eq(hk, [(k, 0, 2) for k in P8B_OLDK], "DATA 3 upgrades become 0.3 node aliases (UHK 0 -> 2)")
    fk = [(str(V.TNAME[int(V.RT[r])]), int(V.RNUM[r]), str(V.RFKEY[r])) for r in range(len(n["RFK"])) if n["RFK"][r] != o["RFK"][r]]
    K.eq(sorted(fk), [("Combat", 1, "Skill.Combat.b1.r1.free"), ("Mining", 2, "Skill.Mining.b2.r2.free")], "DATA 2 free perks RFK 0 -> 4 with their keys")
    K.check(all(n["RFK"][r] == 4 for r in range(len(n["RFK"])) if (str(V.TNAME[int(V.RT[r])]), int(V.RNUM[r])) in (("Combat", 1), ("Mining", 2)) and str(V.RFKEY[r]) != "-"), "DATA RFK 4 rows")
    moved = []
    for tv in range(len(n["TNAME"])):
        for r in range(8):
            a, b = o["GATES"][tv * 8 + r], n["GATES"][tv * 8 + r]
            if a != b:
                moved.append((n["TNAME"][tv], r, a, b))
    K.check(all(int(x[3]) > int(x[2]) for x in moved), "DATA a gate only rises")
    K.eq(sorted(moved), [("Combat", 3, 8, 10), ("Combat", 4, 13, 15)], "DATA the gate moves (spec 4.3): Combat row 3 8 -> 10, row 4 13 -> 15")
    K.eq(n["R3B"][-3:], ["SkyyTrees", "SkyyClasses", "SkyyMobs"], "DATA R3B + the three P8b appliers")
    rows = V3E.rows("SkyyTrees")
    K.eq([str(x) for x in S.KEY], [V3E.key(e[0], e[1], e[2]) for e in rows], "DATA TreeSk.KEY = trees_v3_effects' SkyyTrees rows")
    K.eq([str(x) for x in S.EFF], [e[4] for e in rows], "DATA TreeSk.EFF")
    K.eq([round(float(S.v3per(i)), 9) for i in range(len(rows))], [round(e[5], 9) for e in rows], "DATA TreeSk per rank (effect units) = the table")
    K.check(str(S.READS) == V3E.reads_csv("SkyyTrees"), "DATA tree:reads:SkyyTrees = the 16 keys")
    K.check(bool(V3E.check()), "DATA trees_v3_effects.check(): Fortune %.1f / %.1f, XP %.1f / %.1f / %.1f %%, move %g / %g / %g %%, Health %.1f / %.1f / %.1f %%" % (
        100 * V3E.tree_fort("mining"), 100 * V3E.tree_fort("foraging"), 100 * V3E.tree_xp("Mining"), 100 * V3E.tree_xp("Foraging"), 100 * V3E.tree_xp("Combat"),
        V3E.tree_move("Mining"), V3E.tree_move("Foraging"), V3E.tree_move("Combat"), 100 * V3E.tree_hp("Mining"), 100 * V3E.tree_hp("Foraging"), 100 * V3E.tree_hp("Combat")))
    K.save()


def _props(b):
    from jpype import JClass
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.ByteArrayInputStream")(b))
    return {str(k): str(p.getProperty(k)) for k in p.stringPropertyNames()}


def _pfile(d, uid, ranks):
    t = "v=3\ntreesV3=1\ngates41=1\nname=Test\n" + "".join("%s=%d\n" % (k, v) for k, v in ranks.items())
    open(os.path.join(d, "players", uid + ".properties"), "w").write(t)


FULL = {}
for _e in V3E.EFFECTS:
    if _e[3] in ("SkyyTrees", "SkyyClasses", "SkyyMobs") and not V3E.is_free(_e[2]):
        FULL[V3E.key(_e[0], _e[1], _e[2])] = V3E.maxrank(_e[0], _e[1], _e[2])
for _k in V3D.P8B_OLD:
    _t, _b, _i = _k.split(".")
    FULL["Skill." + _k] = V3E.maxrank(_t, int(_b[1:]), _i)


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    St, Cfg, V, S, Fx, D = (JClass(PKG + "TreeStore"), JClass(PKG + "TreeCfg"), JClass(PKG + "TreeV3"), JClass(PKG + "TreeSk"),
                            JClass(PKG + "TreeFx"), JClass(PKG + "TreeDefs"))
    d = os.path.join(scratch, "exec")
    os.makedirs(os.path.join(d, "players"), exist_ok=True)
    St.DIR = Paths.get(os.path.join(d, "players"))
    Cfg.FILE = Paths.get(os.path.join(d, "trees.properties"))
    Cfg.load()
    r0 = str(S.loadV3(Paths.get(d)))
    ef = os.path.join(d, "tree-effects.properties")
    K.check(os.path.isfile(ef) and open(ef, encoding="latin-1").read() == V3E.cfg_text("SkyyTrees") and "read" in r0,
            "X loadV3 seeds tree-effects.properties with the table's numbers: %s" % r0)
    br = St.bridge()
    S.reads(True)
    br.put("tree:reads:SkyyClasses", JString(V3E.reads_csv("SkyyClasses")))
    br.put("tree:reads:SkyyMobs", JString(V3E.reads_csv("SkyyMobs")))
    br.put("tree:reads:SkyyPets", JString(V3E.reads_csv("SkyyPets")))
    # the points: tree:fn:level of a skill = SkyySkills' skill:fn:level (Mining / Foraging / Combat 60)
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Lv(object):
        @JOverride
        def apply(self, a):
            return JClass("java.lang.Integer")(LEVEL[0])
    LEVEL = [60]
    br.put("skill:fn:level", Lv())
    _pfile(d, U1, FULL)
    u1 = UUID.fromString(U1)
    data = St.data(u1)
    K.check(not bool(data.bad), "X the full-build player file reads")
    V.derive(data)
    exp = {"vein": 1 * 3 + 2 * 2, "feller": 3.0, "gem.mining": 0.0018, "coins.mining": 0.06, "extra.foraging": 0.024, "xp.foraging": 0.045,
           "hpp": 0.06 + 0.06 + 0.025, "spd": 4.0 + 6.0 + 6.0 + 4.0, "fall": 0.10 + 0.10}
    got = dict((k, round(float(S.sum(u1, k)), 9)) for k in exp)
    K.eq(got, dict((k, round(v, 9)) for k, v in exp.items()), "X every own effect at max EXECUTED (TreeSk.sum; Stoneskin open)")
    K.eq((round(float(Fx.sk(u1, "vein")), 9), round(float(Fx.skHp(u1)), 9)), (7.0, 14.5), "X the TreeFx stubs got their late bodies (sk, skHp = % max Health)")
    m = JClass("java.util.HashMap")()
    m.put("xp.foraging", JClass("java.lang.Double")(0.1))
    Fx.skBonus(u1, m)
    K.eq(round(float(m.get("xp.foraging")), 9), 0.145, "X skBonus merges Forest Fortune into skill:bonus xp.foraging (0.1 + 0.045)")
    # Chain Fortune through derive: Mining Wisdom 10 (Overclock 0) + 4 levels; the skill:bonus map xp.mining
    v = Fx.compute(u1)
    mw, ms, fs = int(D.idx("Mining.MWisdom")), int(D.idx("Mining.MSpeed")), int(D.idx("Foraging.FSpeed"))
    K.eq((int(data.lv[mw]), int(data.lv[ms]), int(data.lv[fs])), (4, 4, 4), "X derive: Chain Fortune 2 x 2 -> Mining Wisdom 4; Steady Pick 4 -> Mining Speed 4; Steady Rhythm 4 -> Chopping Speed 4")
    bm = Fx.bonusMap(v)
    K.eq(round(float(bm.get("xp.mining")), 9), 0.04, "X skill:bonus xp.mining = +4 % (Chain Fortune at max)")
    # the movement source
    S.movePost(u1)
    mv = br.get("move:" + U1)
    e = mv.get("trees.skills") if mv is not None else None
    K.check(e is not None and abs(float(e.get("speed")) - 0.20) < 1e-6 and abs(float(e.get("fallDamage")) + 0.20) < 1e-6 and str(e.get("layer")) == "flat",
            "X movePost: source trees.skills, flat speed +0.20, fallDamage -0.20: %s" % e)
    Fx.clearOne(u1)
    K.check(br.get("move:" + U1) is None or br.get("move:" + U1).get("trees.skills") is None, "X clearOne removes trees.skills")
    # tree:fn:level of the P8b keys + the free keys; live() follows tree:reads
    sr = lambda k: int(V.skillRank(u1, k))
    K.eq((sr("Skill.Mining.b1.r2b"), sr("Skill.Combat.b3.r5a"), sr("Skill.Mining.b2.r2.free"), sr("Skill.Combat.b1.r1.free")), (3, 3, 1, 1),
         "X tree:fn:level: Burst Reach 3, Lucky Kill 3, Stoneskin 1, Combat Focus 1")
    br.remove("tree:reads:SkyyClasses")
    br.remove("tree:reads:SkyyMobs")
    rf = [r for r in range(len(V.RFK)) if str(V.RFKEY[r]) == "Skill.Combat.b1.r1.free"][0]
    K.eq((sr("Skill.Combat.b1.r1.free"), sr("Skill.Combat.b3.r5a"), bool(V.freeLive(rf))), (0, 0, False),
         "X without tree:reads:SkyyClasses / SkyyMobs: Combat Focus and Lucky Kill answer 0 (not live)")
    K.check(str(V.freeNow(rf)).endswith("- coming soon"), "X freeNow says coming soon while SkyyClasses does not list it: %s" % V.freeNow(rf))
    br.put("tree:reads:SkyyClasses", JString(V3E.reads_csv("SkyyClasses")))
    br.put("tree:reads:SkyyMobs", JString(V3E.reads_csv("SkyyMobs")))
    K.eq(str(V.freeNow(rf)), "+3% damage", "X freeNow: the Combat Focus text")
    rs = [r for r in range(len(V.RFK)) if str(V.RFKEY[r]) == "Skill.Mining.b2.r2.free"][0]
    K.eq(str(V.freeNow(rs)), "-10% fall damage", "X freeNow: the Stoneskin text")
    lk = lambda k: bool(V.live([i for i in range(len(V.UKEY)) if str(V.UKEY[i]) == k][0]))
    K.check(all(lk(k) for k in FULL), "X every P8b upgrade is live with its applier listed")
    # Stoneskin needs row 2: a Mining build with 4 points spent
    _pfile(d, U3, {"Skill.Mining.b1.r1a": 4})
    u3 = UUID.fromString(U3)
    K.eq((round(float(S.sum(u3, "fall")), 9), int(V.skillRank(u3, "Skill.Mining.b2.r2.free"))), (0.0, 0), "X Stoneskin closed at 4 Mining points (row 2 gate 5)")
    _pfile(d, U3, {"Skill.Mining.b1.r1a": 5})
    St.DATA.remove(St.pkey(u3))
    K.eq((round(float(S.sum(u3, "fall")), 9), int(V.skillRank(u3, "Skill.Mining.b2.r2.free"))), (0.1, 1), "X Stoneskin open at 5 Mining points")
    # Server Setup numbers: a changed per rank / ceiling applies at once (the kit sets the field)
    i_v = [i for i in range(len(S.EFF)) if str(S.EFF[i]) == "vein"][0]
    K.eq(i_v, 0, "X row 0 = Burst Reach")
    S.V3X0 = 100.0
    S.V3P0 = 2.0
    K.eq(round(float(S.sum(u1, "vein")), 6), 10.0, "X Burst Reach per rank 1 -> 2 (Server Setup field) -> vein 2 x 3 + 4 = 10")
    S.V3X0 = 1.0
    K.eq(round(float(S.sum(u1, "vein")), 6), 5.0, "X its ceiling 1 -> vein 1 + 4 = 5")
    S.loadV3(Paths.get(d))
    K.eq(round(float(S.sum(u1, "vein")), 6), 7.0, "X loadV3 of the file puts the built-in numbers back")
    # THE GRANDFATHER RULE: Combat Hone Edge 5 + Weak Spot 3 + Pet Fang 1 = 9 points (row 3 gate 8 in 0.4.5 -> 10 now)
    _pfile(d, U2, {"Skill.Combat.b1.r1a": 5, "Skill.Combat.b1.r1b": 3, "Skill.Combat.b3.r3a": 1})
    u2 = UUID.fromString(U2)
    d2 = St.data(u2)
    tvc = [t for t in range(len(V.TNAME)) if str(V.TNAME[t]) == "Combat"][0]
    pf = [i for i in range(len(V.UKEY)) if str(V.UKEY[i]) == "Skill.Combat.b3.r3a"][0]
    fi = [i for i in range(len(V.UKEY)) if str(V.UKEY[i]) == "Skill.Combat.b1.r3a"][0]
    g = V.gates(tvc)
    sp = int(V.spent(d2, tvc))
    K.eq((sp, int(g[3]), int(d2.rk[pf]), int(V.skillRank(u2, "Skill.Combat.b3.r3a"))), (9, 10, 1, 1),
         "X grandfather: 9 points < the new row-3 gate 10, the Pet Fang rank stays and tree:fn:level still answers it")
    K.eq((int(V.ustate(d2, pf, 60, sp, g)), int(V.ustate(d2, fi, 60, sp, g))), (2, 0),
         "X grandfather: Pet Fang shows owned (2), Finisher in the same row is locked (0) until 10 points")
    K.save()


def live_start(home):
    from jpype import JClass
    J = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    J("TreeStore").DIR = Paths.get(os.path.join(home, "players"))
    J("TreeCfg").FILE = Paths.get(os.path.join(home, "trees.properties"))
    J("TreeStore").DATA.clear()
    J("TreeCfg").load()
    bp = Paths.get(home)
    out = []
    for m in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317", "TreeMig321", "TreeMig323", "TreeMig324", "TreeMigP5"):
        out.append(str(J(m).run(bp)))
    out.append(str(J("TreeSk").loadV3(bp)))
    bad = []
    for f in sorted(os.listdir(os.path.join(home, "players"))):
        if f.endswith(".properties"):
            d = J("TreeStore").readFile(f[:-11])
            if bool(d.bad):
                bad.append(f)
            J("TreeV3").derive(d)
    return out, bad


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    fp = os.path.join(home, "trees.properties")
    t0 = open(fp, "rb").read()
    K.check(not os.path.exists(os.path.join(home, "tree-effects.properties")), "LIVE no tree-effects.properties yet (a new file)")
    msgs, bad = live_start(home)
    print("   live start 1:", [m[:80] for m in msgs if m])
    po, pn = _props(t0), _props(open(fp, "rb").read())
    dk = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    K.check(dk in ([], ["Mining.MFortune.per"]), "LIVE start 1: trees.properties changes at most 0.4.5's own TreeMigP5 line (the live world has not started 0.4.5 yet): %s" % dk)
    K.check(open(os.path.join(home, "tree-effects.properties"), encoding="latin-1").read() == V3E.cfg_text("SkyyTrees"), "LIVE tree-effects.properties seeded with the table")
    K.eq(bad, [], "LIVE every player file reads")
    K.check(all(m == "" for m in msgs[:-2]), "LIVE start 1: every update before 0.4.5's already ran: %s" % [m[:60] for m in msgs[:-2] if m])
    h1 = tree_hash(home)
    msgs2, bad2 = live_start(home)
    K.check(tree_hash(home) == h1 and bad2 == [], "LIVE start 2 changes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("old", run_old), ("data", run_data), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyTrees"))
