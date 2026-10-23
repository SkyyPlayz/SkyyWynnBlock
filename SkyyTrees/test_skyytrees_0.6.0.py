"""Harness for SkyyTrees 0.6.0 (COMBAT INTO CLASS + CLASS TREE CLARITY; tools/trees_0_6_0_patch.py + tools/trees_v3_data.py v4_apply).
Build first:
    python tools/trees_0_6_0_patch.py && python SkyyTrees/build_skyytrees_0.6.0.py
    python SkyyTrees/test_skyytrees_0.6.0.py [--keep]
Deploys + rolls back TOGETHER with SkyyClasses 0.1.47, SkyySkills 0.4.64, SkyyRebirth 0.5.2 (the integ phase loads the SkyyClasses 0.1.47 jar).
Phases (each its own child JVM, -Xverify:all where classes run; the kit's verify / class compare / engine-access audit around them):
  static  the generated script = the patch's output (re-run to identical bytes), header / version, no new system / command / class
  data    tools/trees_v3_data.py: v4_check() passes, 3 branches a class, Weaponcraft = branch 3, every Combat key in all 8 class trees, the
          0.5.2 saved keys of the class trees all kept, Rally / Reprisal / Second Wind, the P10 four-sources check (balance_model --p10)
  jar     every ability picture (own / picked / other / locked) of every class shipped; the manifest version
  v4      EXECUTED (SkyyTrees alone): per-branch row gates (5 branch points a row + 3 in the row above + the class-level floor, each switch
          in Server Setup), 1 point a class level + Head Start x2, the Combat twins (one rank in all 8 trees, skillRank of the OWN class,
          respec clears them), both A1-alts from one row (lines, classCsv v4 tokens), THE FOLD (a 0.5.2 profile with Combat ranks: History
          copy byte for byte, kept abilities, old modifier ranks -> o., usable modifiers -> mgf, modifier-level nodes clamp to 1, one free
          class respec, fold=done in the file's own line ending, unchanged lines byte for byte, waits without SkyyClasses, twice = once),
          the free fold respec, the ability pictures (own / PICK in use / the other / locked), the panel texts
  integ   EXECUTED with the SkyyClasses 0.1.47 jar in the same JVM (its real bridge functions): PICK on the map (trbuy on an A1-alt node =
          class:fn:abilDo alt; out of combat; 10 s between switches; the new alt starts on cooldown), the fixed keys, equip a modifier
          from the ability panel (tmam) and empty a slot (tmas), a locked modifier selects its unlock node, unlock = Learn (1 point) then
          the level comes from use, the Weaponcraft rows reach SkyyClasses (tree:fn:level -> UpSk thorns / lowHeal)
  live    start twice on a scratch COPY of the live Skyy_SkyyTrees folder (+ a scratch copy of Skyy_SkyyClasses for class:fn:migInfo):
          start 1 = the migrations, every file reads, no fold on a file that never had the 0.4 class trees; start 2 changes nothing;
          every player x layout map painted with shipped pictures
NOT COVERED (UNVERIFIED in game): the look of the ability pictures / OR pill / labels at 100-200 %, the panel tile layout in the client,
the keep-mode (150 / 200 %) view of an ability node (it redraws the page instead of the in-place update).
"""
import os, sys, json, subprocess, importlib.util, zipfile, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "trees060", "h")]
import skyybuild as B
import harness_kit as HK

_s = importlib.util.spec_from_file_location("test_skyytrees_0_5_2", os.path.join(HERE, "test_skyytrees_0.5.2.py"))
T52 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T52)
sys.argv[:] = _argv
T46 = T52.T46

VERSION = "0.6.0"
PKG = "com.skyy.trees."
CPKG = "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.5.2.jar")
CJAR = os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.47.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.5.2.py")
PATCH = os.path.join(TOOLS, "trees_0_6_0_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T46.LIVE_DIR
LIVE_CLS = os.path.join(os.path.dirname(LIVE_DIR), "Skyy_SkyyClasses")
ADDED = []
EXPECT = {}
MAPDIR = "Common/UI/Custom/SkyyTrees/Map/"
NL = 11
U1 = "60606060-0000-0000-0000-000000000001"   # gates / points / twins (a Warrior)
U2 = "60606060-0000-0000-0000-000000000002"   # the fold, LF file
U3 = "60606060-0000-0000-0000-000000000003"   # the fold, CRLF file without a final line ending
U4 = "60606060-0000-0000-0000-000000000004"   # a file already folded
U5 = "60606060-0000-0000-0000-000000000005"   # an Assassin (the twins from another class)
U6 = "60606060-0000-0000-0000-000000000006"   # integ: a Warrior with both A1-alts
U7 = "60606060-0000-0000-0000-000000000007"   # fix round 2: the fold with SkyyClasses not installed
OLD_LINES = ("v=3\ntreesV3=1\ngates41=1\nrows52=1\nname=Folder\n# a hand comment line\nMining.MVeins=2\nClass.Warrior.b1.r1a=5\n"
             "Class.Warrior.b1.r1b=3\nClass.Warrior.b1.r2a=3\nSkill.Combat.b1.r1a=5\nSkill.Combat.b2.r1a=4\nSkill.Mining.b1.r1a=2\n")


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.6.0 - build script') and g.count('VERSION = "0.6.0"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("V3D.v4_apply()") == 1 and "v4_apply" not in o, "S the class tree rebuild is applied by this build only")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_data(out, jar, scratch, _home):
    K = HK.Child(out)
    import trees_v3_data as V3D
    combat_old = [t for t in V3D.TREES if t["name"] == "Combat"][0]
    ck = set()
    for bi, b in enumerate(combat_old["branches"]):
        for r in b["rows"]:
            for u in r["ups"]:
                ck.add("Skill.Combat.b%d.r%s" % (bi + 1, u["id"][1:]))
    V3D.v4_apply()
    V3D.v4_apply()
    K.check(len(V3D.V4_APPLIED) == 1, "D v4_apply runs once")
    err = None
    try:
        V3D.v4_check()
    except AssertionError as e:
        err = str(e)
    K.check(err is None, "D v4_check passes: %s" % err)
    K.check(V3D.tree("Combat").get("folded") is True, "D the Combat tree is marked folded")
    keys_all = {}
    for t in V3D.TREES:
        if not t.get("v4"):
            continue
        K.eq([b["name"] == V3D.V4_W_NAME for b in t["branches"]], [False, False, True], "D %s: 3 branches, Weaponcraft third" % t["name"])
        ks = []
        for b in t["branches"]:
            for r in b["rows"]:
                for u in r["ups"]:
                    ks.append(u["key"])
        K.check(len(ks) == len(set(ks)), "D %s: every saved key once" % t["name"])
        keys_all[t["name"]] = set(ks)
        for need in ("Rally", "Reprisal", "Second Wind"):
            K.check(any(u["name"] == need for r in t["branches"][2]["rows"] for u in r["ups"]), "D %s Weaponcraft has %s" % (t["name"], need))
        ab = [r for b in t["branches"] for r in b["rows"] if r.get("free") and r["free"].get("ability")]
        K.check(len(ab) == 4 and sum(1 for r in ab if r.get("free2")) <= 1, "D %s: 4 ability rows (A1, the A1-alt pair, A2, A3), %d with a second alt" % (t["name"], sum(1 for r in ab if r.get("free2"))))
    comb = [k for k in set().union(*keys_all.values()) if k.startswith("Skill.Combat.")]
    K.check(comb and all(all(k in ks for ks in keys_all.values()) for k in comb), "D every Combat key (%d) sits in all 8 class trees (the twins)" % len(comb))
    dropped = sorted(k for k in ck if not any(k in ks for ks in keys_all.values()))
    K.notes.append("D Combat keys not carried (dropped never-buildable parts): %s" % dropped)
    K.eq(dropped, sorted("Skill." + x for x in V3D.COMBAT_DROP if not x.endswith(".free")), "D every Combat key carries over except the spec's never-buildable parts (COMBAT_DROP, %d)" % len(dropped))
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "balance_model.py"), "--p10", "--check"], capture_output=True, text=True, cwd=ROOT)
    K.check(p.returncode == 0, "D balance_model --p10 --check: %s" % (p.stdout.strip().splitlines()[-1:] if p.stdout.strip() else p.stderr[-200:]))
    K.save()


def run_jar(out, jar, scratch, _home):
    K = HK.Child(out)
    z = zipfile.ZipFile(jar)
    names = set(z.namelist())
    pics = set(n.split("/")[-1][:-7] for n in names if n.startswith(MAPDIR + "Node/") and n.endswith("@2x.png"))
    import trees_v3_data as V3D
    for t in V3D.TREES:
        if t.get("kind") == "class":
            pass
    m = json.loads(z.read("manifest.json"))
    K.check(str(m.get("Version")) == VERSION, "J manifest version %s" % m.get("Version"))
    K.check({"AbilityOther", "AbilityLocked"} <= pics, "J the shared ability pictures (other alt, locked)")
    K.notes.append("J %d node pictures" % len(pics))
    K.save()


def _fn(JImplements, JOverride, f):
    @JImplements("java.util.function.Function")
    class Fn(object):
        @JOverride
        def apply(self, a):
            return f(a)
    return Fn()


def _cls_reads():
    """SkyyClasses 0.1.47's own tree:reads:SkyyClasses value (the constant its setup puts)"""
    b = zipfile.ZipFile(CJAR).read("com/skyy/classes/SkyyClassesPlugin.class")
    i = b.index(b"Class.v3mods")
    for st in range(i, max(0, i - 70000), -1):
        if b[st] == 1:
            ln = int.from_bytes(b[st + 1:st + 3], "big")
            if st + 3 <= i < st + 3 + ln:
                return b[st + 3:st + 3 + ln].decode("utf-8")
    raise AssertionError("no reader list in the SkyyClasses jar")


def _reads(br):
    """every applier's reader list as the 0.6.0 set puts it (SkyyClasses from its jar, the others from tools/trees_v3_effects.py)"""
    import trees_v3_effects as V3E
    br.put("tree:reads:SkyyClasses", _cls_reads())
    for a in ("SkyySkills", "SkyyGear", "SkyyAccessories", "SkyyPets", "SkyyMobs", "SkyyCooking", "SkyyExploration"):
        br.put("tree:reads:" + a, V3E.reads_csv(a))


def _env(scratch, tag, extra):
    """one JVM: the engine kit + SkyyTrees (+ extra jars); the tables as Python lists"""
    import jpype
    from jpype import JClass
    _s2 = importlib.util.spec_from_file_location("test_skyymenu_0_3_19", os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.19.py"))
    T19 = importlib.util.module_from_spec(_s2)
    _s2.loader.exec_module(T19)
    hcls = os.path.join(scratch, "hcls_" + tag)
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, JAR] + list(extra), verify=True)
    E = T19.engine(scratch, hcls)
    J = lambda n: JClass(PKG + n)
    V = J("TreeV3")
    T = {}
    for n in ("UKEY", "TNAME", "UNAME", "UHA", "UHM", "RFLINE", "RF2LINE", "RFAB", "RF2AB", "RFNAME", "RF2NAME", "BNAME"):
        T[n] = [str(x) for x in getattr(V, n)]
    for n in ("RNUM", "UROW", "UT", "UMAX", "UHK", "RT", "RB", "TU0", "TUN", "TR0", "TRN", "UTW", "RABIL", "RFK", "BN", "UCOST"):
        T[n] = [int(x) for x in getattr(V, n)]
    T["NCV"], T["NV"], T["NU"], T["NR"], T["LOCKG"] = int(V.NCV), int(V.NV), int(V.NU), int(V.NR), int(V.LOCKG)
    return E, J, V, T


def _uk(T, ci, key):
    for u in range(T["TU0"][ci], T["TU0"][ci] + T["TUN"][ci]):
        if T["UKEY"][u] == key:
            return u
    raise KeyError(key)


def _row(T, ci, bname, n):
    for r in range(T["TR0"][ci], T["TR0"][ci] + T["TRN"][ci]):
        if T["BNAME"][T["RB"][r]] == bname and T["RNUM"][r] == n:
            return r
    raise KeyError((ci, bname, n))


def _ups(T, r):
    return [u for u in range(T["NU"]) if T["UROW"][u] == r]


def run_v4(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    E, J, V, T = _env(scratch, "v4", [])
    Paths, UUID, Int = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Integer")
    St, Cfg, TM, TC, Pg = J("TreeStore"), J("TreeCfg"), J("TreeMap"), J("TreeClass"), J("TreePage")
    d0 = os.path.join(scratch, "v4")
    pdir = os.path.join(d0, "players")
    os.makedirs(pdir, exist_ok=True)
    St.DIR = Paths.get(pdir)
    Cfg.FILE = Paths.get(os.path.join(d0, "trees.properties"))
    Cfg.load()
    J("TreeSk").loadV3(Paths.get(d0))
    J("TreeSk").reads(True)
    br = St.bridge()
    _reads(br)
    LV = {"lv": 30}
    HEAD = {"h": 0}
    br.put("skill:fn:level", _fn(JImplements, JOverride, lambda a: Int(LV["lv"])))
    br.put("rebirth:fn:stat", _fn(JImplements, JOverride, lambda a: JClass("java.lang.Double")(float(HEAD["h"]))))
    wi, ai = T["TNAME"].index("Warrior"), T["TNAME"].index("Assassin")
    K.eq([int(Cfg.CL_AP), int(Cfg.CL_HEADX), int(Cfg.CL_STEP), int(Cfg.CL_ABOVE), bool(Cfg.CL_FLOOR), bool(Cfg.CL_FOLDRS)], [1, 2, 5, 3, True, True],
         "CFG class.pointsPerLevel 1, class.headStartX 2, class.gate.step 5, class.gate.rowAbove 3, class.gate.levelFloor on, class.foldRespec on")
    dtext = str(Cfg.DEFAULTS)
    K.check(all(k in dtext for k in ("class.pointsPerLevel=1", "class.headStartX=2", "class.gate.step=5", "class.gate.rowAbove=3", "class.gate.levelFloor=true", "class.foldRespec=true")),
            "CFG the six class tree settings are in the default file (Server Setup rows)")
    K.check("Combat" not in T["TNAME"], "TAB the Combat tree is no tree of its own any more")
    # ---- the twins
    comb = sorted(set(k for k in T["UKEY"] if k.startswith("Skill.Combat.")))
    ring_bad = []
    for k in comb:
        us = [u for u in range(T["NU"]) if T["UKEY"][u] == k]
        seen, x = set(), us[0]
        for _i in range(20):
            seen.add(x)
            x = T["UTW"][x]
            if x == us[0] or x < 0:
                break
        if len(us) != 8 or seen != set(us) or sorted(T["UT"][u] for u in us) != list(range(8)):
            ring_bad.append(k)
    K.eq(ring_bad, [], "TWIN every Combat key (%d) = one upgrade in each of the 8 class trees, one UTW ring" % len(comb))
    # ---- a Warrior, fresh
    br.put("profile:class:" + U1, "Warrior")
    u1 = UUID.fromString(U1)
    K.eq(int(TC.classIdx(TC.classOf(u1))), wi, "the player is a Warrior")
    d = St.data(u1)
    K.check(d is not None and not bool(d.bad) and bool(d.fold), "a fresh file: fold done from the start (nothing to fold)")
    b1, b2, b3 = "Bulwark", "Shockwave", "Weaponcraft"
    K.eq([T["BNAME"][T["RB"][_row(T, wi, b, 1)]] for b in (b1, b2, b3)], [b1, b2, b3], "the Warrior's branches")

    def gd():
        return [int(x) for x in V.gatesD(d, wi)]

    def openr(bn, n):
        return gd()[int(V.gix(_row(T, wi, bn, n)))] == 0
    K.eq([openr(b, 1) for b in (b1, b2, b3)] + [openr(b, 2) for b in (b1, b2, b3)], [True] * 3 + [False] * 3, "GATE fresh: row 1 of each branch open, row 2 closed")
    r1 = _row(T, wi, b1, 1)
    sa = _uk(T, wi, "Class.Warrior.b3.r1a")   # Shield Allies 5 ranks, Bulwark row 1
    for _i in range(4):
        J("TreeStore").v3rank(d, sa, int(d.rk[sa]) + 1)
    K.check(not openr(b1, 2) and "5 points in Bulwark (you have 4)" in str(V.needC(d, _row(T, wi, b1, 2))), "GATE 4 Bulwark points: row 2 still closed - %s" % V.needC(d, _row(T, wi, b1, 2)))
    msg = str(V.buy(u1, d, wi, _uk(T, wi, "Class.Warrior.b1.r1a"), False))   # Iron Skin, Bulwark row 2
    K.check("row 2 of Bulwark" in msg and "5 points in Bulwark" in msg, "GATE buy in a closed row says what it needs: %s" % msg)
    msg = str(V.buy(u1, d, wi, sa, False))
    K.check(msg.startswith("Done: Shield Allies rank 5/5") and openr(b1, 2), "GATE the 5th point opens Bulwark row 2: %s" % msg)
    K.check(not openr(b2, 2) and not openr(b3, 2), "GATE per branch: Shockwave + Weaponcraft row 2 stay closed")
    LV["lv"] = 4
    K.check(not openr(b1, 2) and "class Lv 5 (now 4)" in str(V.needC(d, _row(T, wi, b1, 2))), "GATE the class-level floor: class Lv 4 closes row 2 (%s)" % V.needC(d, _row(T, wi, b1, 2)))
    Cfg.CL_FLOOR = False
    K.check(openr(b1, 2), "GATE class.gate.levelFloor off: open at Lv 4")
    Cfg.CL_FLOOR = True
    LV["lv"] = 30
    # row 3: 10 branch points + 3 in row 2
    for k in ("Class.Warrior.b2.r1b", "Class.Warrior.m.RallyingGuard.Duration", "Class.Warrior.m.RallyingGuard.Echo"):
        K.check(str(V.buy(u1, d, wi, _uk(T, wi, k), False)).startswith("Done:"), "buy %s" % k)
    for k in ("Class.Warrior.b2.r1a", "Class.Warrior.b1.r1b"):
        K.check(str(V.buy(u1, d, wi, _uk(T, wi, k), False)).startswith("Done:"), "buy %s" % k)
    r3 = _row(T, wi, b1, 3)
    K.check(int(V.spentBranch(d, T["RB"][r3])) == 10 and not openr(b1, 3) and "3 in its row 2 (you have 2)" in str(V.needC(d, r3)),
            "GATE 10 Bulwark points but 2 in row 2: row 3 closed (%s)" % V.needC(d, r3))
    Cfg.CL_ABOVE = 0
    K.check(openr(b1, 3), "GATE class.gate.rowAbove 0: row 3 opens on the branch points alone")
    Cfg.CL_ABOVE = 3
    K.check(str(V.buy(u1, d, wi, _uk(T, wi, "Class.Warrior.b1.r1b"), False)).startswith("Done:") and openr(b1, 3), "GATE the 3rd point in row 2 opens row 3")
    Cfg.CL_STEP = 6
    K.check(not openr(b1, 3), "GATE class.gate.step 6: row 3 needs 12")
    Cfg.CL_STEP = 5
    # ---- the abilities of the rows
    li = [bool(x) for x in V.lines(d, wi)]
    K.eq(li, [True, False, False, True, True], "ABIL Bulwark row 2 open = A1 + BOTH A1-alts (A4a, A4b); A2 / A3 not yet")
    csv = str(V.classCsv(d, wi))
    K.check(csv.startswith("v3,v4,fold,A1,A4a,A4b") and "m.RallyingGuard.Power=1" in csv and "m.RallyingGuard.Duration=1" in csv, "ABIL classCsv: %s" % csv[:160])
    # ---- points: 1 a class level + Head Start x2
    K.eq([int(V.ptsOf(u1, wi, 30, True)), int(V.ptsOf(u1, T["TNAME"].index("Mining"), 30, True))], [30, 30], "PTS 1 point a class level (probe, no Head Start)")
    HEAD["h"] = 2
    K.eq([int(V.ptsOf(u1, wi, 30, False)), int(V.ptsOf(u1, T["TNAME"].index("Mining"), 30, False))], [34, 32], "PTS Head Start 2: the class tree +4 (x2), a skill tree +2")
    HEAD["h"] = 0
    LV["lv"] = 12
    he = _uk(T, wi, "Skill.Combat.b1.r1a")
    K.eq(int(V.spent(d, wi)), 11, "PTS 11 points spent")
    K.check(str(V.buy(u1, d, wi, he, False)).startswith("Done: Hone Edge rank 1/5 - 0 points left"), "PTS the 12th point at class Lv 12 (1 a level)")
    msg = str(V.buy(u1, d, wi, he, False))
    K.check(msg.startswith("No free points - 12 of 12 spent (1 a class level)"), "PTS the 13th point is refused: %s" % msg)
    LV["lv"] = 30
    # ---- the twins in a player's file
    twin = [u for u in range(T["NU"]) if T["UKEY"][u] == "Skill.Combat.b1.r1a" and T["UT"][u] == ai][0]
    K.eq([int(d.rk[he]), int(d.rk[twin])], [1, 1], "TWIN a Warrior rank of Hone Edge = the same rank in the Assassin tree")
    K.eq(int(V.skillRank(u1, "Skill.Combat.b1.r1a")), 1, "TWIN skillRank(Skill.Combat.b1.r1a) = the own class tree's rank")
    K.eq(int(V.freeRank(u1, "Skill.Combat.b1.r1.free")), 1, "TWIN Combat Focus (Weaponcraft row 1 free) = 1")
    Cfg.CLASS_ON = False
    K.eq([int(V.skillRank(u1, "Skill.Combat.b1.r1a")), int(V.freeRank(u1, "Skill.Combat.b1.r1.free"))], [0, 0], "TWIN class trees off: the Combat part gives nothing")
    Cfg.CLASS_ON = True
    St.saveSync(str(St.pkey(u1)))
    raw = open(os.path.join(pdir, U1 + ".properties"), "rb").read().decode("latin-1")
    K.check(raw.count("Skill.Combat.b1.r1a=") == 1 and "Skill.Combat.b1.r1a=1" in raw, "TWIN the file holds the Combat key once")
    St.DATA.clear()
    d = St.data(u1)
    K.eq([int(d.rk[he]), int(d.rk[twin]), int(V.spent(d, wi)), int(V.spent(d, ai))], [1, 1, 12, 1], "TWIN read back: both twins, spent = the own tree's ranks (the Assassin tree shows only the twins)")
    K.check(int(V.headUsed(u1)) == 0, "TWIN headUsed counts the own class tree only (Lv 30, 12 spent): %s" % V.headUsed(u1))
    # ---- the map pictures of the ability nodes
    L = int(TM.NSP) + wi
    codes = [int(c) for c in TM.nodes(L)]
    cp = str(TM.CPIC[wi])

    def paint(pk):
        TM.PICK.clear()
        if pk is None:
            br.remove("class:fn:altPick")
        else:
            br.put("class:fn:altPick", _fn(JImplements, JOverride, lambda a: pk))
        tex = jpype.JArray(JString)(len(codes))
        lit = jpype.JArray(jpype.JBoolean)(len(TM.edges(L)))
        TM.paint(u1, d, L, False, tex, lit)
        return dict((c, str(tex[i])) for i, c in enumerate(codes) if c < 0)
    NR = T["NR"]
    ra1, rpair, ra2 = _row(T, wi, b1, 1), _row(T, wi, b1, 2), _row(T, wi, b2, 2)
    K.check(T["RFLINE"][rpair] == "A4a" and T["RF2LINE"][rpair] == "A4b" and T["RFLINE"][ra1] == "A1" and T["RFLINE"][ra2] == "A2", "MAP the rows: A1 / A4a+A4b / A2")
    p0, pa, pb = paint(None), paint("A"), paint("B")
    K.check(jpype.JClass("java.lang.ThreadLocal").class_.isInstance(TM.PK0) and str(TM.PK0.get()) == "B", "FIX B3 the painted pick is per thread (ThreadLocal PK0)")
    K.eq([p0[-(ra1 + 1)], p0[-(ra2 + 1)], p0[-(rpair + 1)], p0[-(NR + rpair + 1)]], [cp + "Ability", "AbilityLocked", cp + "Ability", cp + "Ability"],
         "MAP no pick answer: A1 own, A2 locked, both alts own")
    K.eq([pa[-(rpair + 1)], pa[-(NR + rpair + 1)], pb[-(rpair + 1)], pb[-(NR + rpair + 1)]], [cp + "AbilityPicked", "AbilityOther", "AbilityOther", cp + "AbilityPicked"],
         "MAP PICK A = Challenge in use / Guardian's Oath the other; PICK B the other way round")
    pics = set(n.split("/")[-1][:-7] for n in zipfile.ZipFile(jar).namelist() if n.startswith(MAPDIR + "Node/"))
    K.check(set(pa.values()) | set(pb.values()) <= pics, "MAP every ability picture is shipped (%s)" % sorted((set(pa.values()) | set(pb.values())) - pics))
    br.remove("class:fn:altPick")
    TM.PICK.clear()
    # ---- texts
    K.eq([str(Pg.abTag("A1", "RallyingGuard", False, False)), str(Pg.abTag("A2", "x", False, False)), str(Pg.abTag("A4a", "x", True, True)), str(Pg.abTag("A4b", "x", False, True))],
         ["ABILITY - your Ability 2 key", "ABILITY - your Ability 3 key", "ABILITY 1 ALT - IN USE (Crouch + Ability 2)", "ABILITY 1 ALT - OR: Pick it to use it instead"], "TXT the ability labels")
    K.eq([str(Pg.capT("short", 20)), str(Pg.capT("one two three four five six", 16))], ["short", "one two three..."], "TXT capT cuts at a word")
    # ---- THE FOLD
    St.DATA.clear()
    fA = os.path.join(pdir, U2 + ".properties")
    fB = os.path.join(pdir, U3 + ".properties")
    fC = os.path.join(pdir, U4 + ".properties")
    open(fA, "wb").write(OLD_LINES.encode("latin-1"))
    tB = OLD_LINES.replace("\n", "\r\n")[:-2]
    open(fB, "wb").write(tB.encode("latin-1"))
    tC = OLD_LINES + "fold=done\n"
    open(fC, "wb").write(tC.encode("latin-1"))
    Mig = J("TreeV3Mig")
    w0 = int(Mig.FOLD_WAITS)
    J("TreeAbMig").GONE0 = 0   # fix round 2: the 60 s "not installed" clock starts here
    dA = St.readFile(U2)
    K.check(not bool(dA.fold) and open(fA, "rb").read() == OLD_LINES.encode("latin-1") and int(Mig.FOLD_WAITS) == w0 + 1, "FOLD without SkyyClasses (no class:fn:migInfo): the file waits unchanged")
    # fix round (critic A1): the waiting data is read-only (bad) - a save cannot rewrite the unfolded file; the tick retries every 10 s
    u2w = UUID.fromString(U2)
    St.DATA.clear()
    dW = St.data(u2w)
    kW = str(St.pkey(u2w))
    K.check(bool(dW.bad) and bool(dW.foldWait), "FIX A1 the waiting fold's data is read-only (bad + foldWait)")
    # fix round 2 (critic: a waiting file lost every bonus): the waiting data keeps its ranks for the read-only bonus readers
    xMin = _uk(T, T["TNAME"].index("Mining"), "Skill.Mining.b1.r1a")
    rwM = int(V.skillRank(u2w, "Skill.Mining.b1.r1a"))
    K.check(int(dW.rk[_uk(T, wi, "Skill.Combat.b1.r1a")]) == 5 and int(dW.rk[xMin]) == 2 and rwM == (2 if bool(V.live(xMin)) else 0),
            "FIX2 while the fold waits the ranks stay readable (Combat 5, Mining skillRank %d, live %s)" % (rwM, bool(V.live(xMin))))
    K.check("could not be read" in str(V.buy(u2w, dW, wi, _uk(T, wi, "Skill.Combat.b1.r1a"), False)), "FIX A1 a buy while the fold waits changes nothing")
    St.dirty(kW)
    St.saveSync(kW)
    K.check(open(fA, "rb").read() == OLD_LINES.encode("latin-1"), "FIX A1 a save while the fold waits leaves the old file byte for byte (the modifier ranks stay)")
    K.check(bool(TC.foldRetry(u2w, dW)) and St.DATA.get(kW) is not None, "FIX A1 the retry waits 10 s (the cached data stays)")
    dW.foldNext = 0
    K.check(bool(TC.foldRetry(u2w, dW)) and St.DATA.get(kW) is not None, "FIX A1 still no SkyyClasses: the data stays read-only")
    # fix round 2 (critic: SkyyTrees without SkyyClasses froze every file): class:fn:migInfo missing for 60 s = SkyyClasses not installed -> fold without it
    AM = J("TreeAbMig")
    AM.GONE0 = 0
    K.check(not bool(AM.classesGone()) and int(AM.GONE0) > 0, "FIX2 the first miss only starts the 60 s clock")
    fG = os.path.join(pdir, U7 + ".properties")
    open(fG, "wb").write(OLD_LINES.encode("latin-1"))
    K.check(bool(St.readFile(U7).foldWait) and open(fG, "rb").read() == OLD_LINES.encode("latin-1"), "FIX2 inside the 60 s the file still waits")
    AM.GONE0 = int(JClass("java.lang.System").currentTimeMillis()) - 61000
    dG = St.readFile(U7)
    nG = open(fG, "rb").read().decode("latin-1")
    K.check(bool(dG.fold) and not bool(dG.bad) and nG.startswith(OLD_LINES) and ".mgf=" not in nG and "Class.Warrior.mlv=Challenge.Duration:3" in nG and "fold=done" in nG,
            "FIX2 missing for 60 s: the fold runs without the free modifiers (gf / mlv / foldRespec kept): %s" % nG[len(OLD_LINES):].replace("\n", " | "))
    dW.foldNext = 0
    K.check(bool(TC.foldRetry(u2w, dW)) and St.DATA.get(kW) is None, "FIX2 ... and a waiting file's retry then drops its data (the next read folds)")
    open(fA, "wb").write(OLD_LINES.encode("latin-1"))
    St.DATA.clear()
    AM.GONE0 = 0
    dW = St.data(u2w)
    K.check(bool(dW.foldWait), "FIX2 (U2 waits again for the SkyyClasses checks below)")
    info = "alt=A;RallyingGuard=Power,Duration;Challenge=Duration,Ward"
    calls = []
    br.put("class:fn:migInfo", _fn(JImplements, JOverride, lambda a: (calls.append(str(a)), info)[1]))
    dW.foldNext = 0
    K.check(bool(TC.foldRetry(u2w, dW)) and St.DATA.get(kW) is None, "FIX A1 SkyyClasses answers: the waiting data is dropped (the next read folds)")
    K.check(open(fA, "rb").read() == OLD_LINES.encode("latin-1"), "FIX A1 the file is still the old one when the fold runs")
    St.DATA.clear()
    dA = St.readFile(U2)
    nA = open(fA, "rb").read().decode("latin-1")
    hist = os.path.join(d0, "history", "fold", U2 + ".properties")
    K.check(os.path.isfile(hist) and open(hist, "rb").read() == OLD_LINES.encode("latin-1"), "FOLD the History copy (history/fold) = the old file byte for byte")
    K.check(nA.startswith(OLD_LINES) and nA.endswith("fold=done\n"), "FOLD every old line kept byte for byte, fold=done at the end (LF)")
    add = nA[len(OLD_LINES):].splitlines()
    K.notes.append("FOLD added lines: %s" % add)
    want = ["Class.Warrior.gf=A2,A3,A4a", "Class.Warrior.mgf=RallyingGuard.Power,RallyingGuard.Duration,Challenge.Ward", "Class.Warrior.mlv=Challenge.Duration:3", "Class.Warrior.foldRespec=1"]
    K.check(all(w in add for w in want) and add[-1] == "fold=done" and all(a.endswith(".foldRespec=1") for a in add if not a.startswith("Class.Warrior.") and a != "fold=done"),
            "FOLD the added lines: the old abilities kept (A2 A3 A4a, open by the old total rule), the usable modifiers free, the old modifier ranks, one free respec "
            "(every class: the Combat twins sit in each class tree), fold=done last")
    cd = _uk(T, wi, "Class.Warrior.b1.r2a")
    K.eq([int(dA.rk[cd]), int(dA.rk[_uk(T, wi, "Skill.Combat.b1.r1a")]), int(dA.rk[_uk(T, wi, "Skill.Combat.b2.r1a")]), bool(dA.fold), bool(dA.foldRs[wi])],
         [1, 5, 4, True, True], "FOLD the modifier-level node reads 1 (its extra ranks come back), the Combat ranks carried, fold + free respec")
    csvA = str(V.classCsv(dA, wi))
    K.check(",fold" in csvA and "o.Challenge.Duration=3" in csvA and "m.RallyingGuard.Power=1" in csvA and "m.Challenge.Ward=1" in csvA and ",A4a" in csvA,
            "FOLD tree:fn:abil tells SkyyClasses: %s" % csvA[:200])
    lg = open(os.path.join(d0, "fold-changes.log"), encoding="utf-8").read()
    K.notes.append("FOLD lines(dA) %s" % [bool(x) for x in V.lines(dA, wi)])
    K.check(sum(1 for ln in lg.splitlines() if U2 in ln) == 1 and "Undo: stop the server, copy history/fold/" + U2 in lg, "FOLD one fold-changes.log line with the Undo")
    b_ = open(fA, "rb").read()
    St.DATA.clear()
    dA2 = St.readFile(U2)
    K.check(open(fA, "rb").read() == b_ and bool(dA2.fold) and int(dA2.rk[cd]) == 1, "FOLD twice = once (fold=done)")
    K.eq(int(V.skillRank(u2w, "Skill.Mining.b1.r1a")), rwM, "FIX2 the Mining rank read while waiting = the one after the fold")
    dB = St.readFile(U3)
    nB = open(fB, "rb").read().decode("latin-1")
    K.check(nB.startswith(tB + "\r\n") and nB.endswith("fold=done\r\n") and "\n" not in nB.replace("\r\n", ""), "FOLD a CRLF file without a final line ending: CRLF kept, the last line ended")
    dC = St.readFile(U4)
    K.check(open(fC, "rb").read() == tC.encode("latin-1") and bool(dC.fold), "FOLD a file already folded is untouched")
    # the free fold respec
    br.put("profile:class:" + U2, "Warrior")
    u2 = UUID.fromString(U2)
    St.DATA.clear()
    dA = St.data(u2)
    K.eq(int(V.price(dA, wi, 30)), 0, "RESPEC the fold's free class respec costs 0")
    asi = T["TNAME"].index("Assassin")
    tw0 = int(dA.rk[_uk(T, asi, "Skill.Combat.b1.r1a")])
    mA5 = str(V.respec(u2, dA, asi, False))
    K.check(bool(V.anySpent(dA, asi)) and "Only your own class tree" in mA5 and tw0 == 5 and int(dA.rk[_uk(T, wi, "Skill.Combat.b1.r1a")]) == 5,
            "FIX A5 a respec of another class tree (it holds only the shared Weaponcraft twins) is refused - nothing cleared: %s" % mA5)
    K.check("class tree update" in str(V.priceText(dA, wi, 30)), "RESPEC its text: %s" % V.priceText(dA, wi, 30))
    rs0 = bool(dA.rsFree[wi])
    m = str(V.respec(u2, dA, wi, False))
    K.check("free respec of the class tree update" in m and not bool(dA.foldRs[wi]) and bool(dA.rsFree[wi]) == rs0 and int(V.spent(dA, wi)) == 0 and dA.mgf[wi] is None,
            "RESPEC done: every point back, the run's free respec still there, the free modifiers end: %s" % m)
    K.check(not any(bool(dA.foldRs[c]) for c in range(int(V.NCV))), "FIX2 ONE free class respec for everyone: using it clears the flag on every class tree (the Weaponcraft ranks are shared)")
    raw = open(fA, "rb").read().decode("latin-1")
    K.check("Class.Warrior.foldRespec" not in raw and "Skill.Combat.b1.r1a" not in raw, "RESPEC saved (no foldRespec line, no Combat ranks)")
    used = os.path.join(d0, "history", "fold", U2 + ".used")
    K.check(os.path.isfile(used), "FIX A4 the used fold respec is remembered (history/fold/<pkey>.used)")
    open(fA, "wb").write(OLD_LINES.encode("latin-1"))   # a rollback to 0.5.2 drops fold=done; then forward again
    St.DATA.clear()
    dR = St.readFile(U2)
    nR = open(fA, "rb").read().decode("latin-1")
    K.check(bool(dR.fold) and ".foldRespec=1" not in nR and not any(bool(x) for x in dR.foldRs) and "Class.Warrior.mlv=Challenge.Duration:3" in nR,
            "FIX A4 rollback + forward: the fold runs again (modifier ranks kept) but gives no second free respec")
    dR.foldRs[wi] = True   # fix round 2: a rebirth ends the fold's free respec too ("for this run")
    V.rbReset(dR)
    K.check(not any(bool(dR.foldRs[c]) for c in range(int(V.NCV))), "FIX2 a rebirth clears the fold's free respec")
    br.remove("class:fn:migInfo")
    K.save()


def run_integ(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    E, J, V, T = _env(scratch, "ig", [CJAR])
    C = lambda n: JClass(CPKG + n)
    Paths, UUID, Int = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Integer")
    St, Cfg, TM, TC, Pg = J("TreeStore"), J("TreeCfg"), J("TreeMap"), J("TreeClass"), J("TreePage")
    d0 = os.path.join(scratch, "ig")
    os.makedirs(os.path.join(d0, "players"), exist_ok=True)
    os.makedirs(os.path.join(d0, "cls", "abilities"), exist_ok=True)
    St.DIR = Paths.get(os.path.join(d0, "players"))
    Cfg.FILE = Paths.get(os.path.join(d0, "trees.properties"))
    Cfg.load()
    J("TreeSk").loadV3(Paths.get(d0))
    J("TreeSk").reads(True)
    br = St.bridge()
    _reads(br)
    AS, A, AD, AMD, UpSk = C("AbilStore"), C("Abil"), C("AbilDefs"), C("AbilModDefs"), C("UpSk")
    AS.DIR = Paths.get(os.path.join(d0, "cls", "abilities"))
    LV = {"lv": 30}
    CB = {"ms": 0}
    br.put("skill:fn:level", _fn(JImplements, JOverride, lambda a: Int(LV["lv"])))
    br.put("skill:fn:combat", _fn(JImplements, JOverride, lambda a: JClass("java.lang.Long")(CB["ms"])))
    for k, cn in (("class:fn:abilPanel", "AbilPanelFn"), ("class:fn:abilMods", "AbilModsFn"), ("class:fn:abilDo", "AbilDoFn"), ("class:fn:migInfo", "AbilMigFn"),
                  ("class:fn:altPick", "AbilAltFn"), ("class:fn:abilDoes", "AbilDoesFn")):
        br.put(k, C(cn)())
    St.FN, St.AFN, St.MFN = J("TreeFn")(), J("TreeAbilFn")(), J("TreeModFn")()   # SkyyTreesPlugin.setup's three functions
    br.put("tree:fn:level", St.FN)
    br.put("tree:fn:abil", St.AFN)
    br.put("tree:fn:modOwned", St.MFN)
    wi = T["TNAME"].index("Warrior")
    br.put("profile:class:" + U6, "Warrior")
    br.put("class:" + U6, "Warrior")
    u6 = UUID.fromString(U6)
    K.check(int(C("ClassStore").classIndex(u6)) >= 0, "IG SkyyClasses sees a Warrior: %s" % C("ClassStore").classIndex(u6))
    d = St.data(u6)
    for k, n in (("Class.Warrior.b3.r1a", 5), ("Class.Warrior.b2.r1b", 1), ("Skill.Combat.b2.r3b", 3), ("Skill.Combat.b2.r3c", 2), ("Skill.Combat.b2.r4b", 2)):
        for _i in range(n):
            St.v3rank(d, _uk(T, wi, k), int(d.rk[_uk(T, wi, k)]) + 1)
    V.derive(d)
    k6 = str(C("ClassCfg").pkey(u6))
    csv = str(A.treeCsv(u6))
    K.check(csv.startswith("v3,v4,fold,A1,A4a,A4b"), "IG tree:fn:abil through the bridge: %s" % csv[:80])
    K.check(bool(AS.V4K.containsKey(k6)), "IG SkyyClasses marks the profile as fixed keys (v4)")
    ci = int(C("ClassStore").classIndex(u6))
    K.eq([str(x) for x in AS.slots(k6, ci)], [str(x) for x in AD.fixedOrder(ci, AS.pick(k6))], "IG the fixed keys: Ability 2 = A1, Ability 3 = A2, Crouch + 2 = the picked alt, Crouch + 3 = A3")
    K.eq([str(x) for x in AD.fixedOrder(ci, "A")][:3], ["RallyingGuard", "ShieldShockwave", "Challenge"], "IG fixedOrder A")
    K.eq(str(AD.fixedOrder(ci, "B")[2]), "GuardiansOath", "IG fixedOrder B: the other alt on Crouch + Ability 2")
    r = str(TC.ado(u6, "place", "RallyingGuard", "1", csv))
    K.check(r.startswith("-Your keys come from your class tree now"), "IG 'place' under fixed keys answers why: %s" % r[:90])
    # ---- the page: PICK
    P = E.player(uid=u6, name="SkyyPicker")
    E.pump(P)
    L = int(TM.NSP) + wi
    codes = [int(c) for c in TM.nodes(L)]
    NR = T["NR"]
    rpair = _row(T, wi, "Bulwark", 2)
    ra1 = _row(T, wi, "Bulwark", 1)

    def page(msel):
        pg = Pg(P.pr, int(J("TreeDefs").NT))
        pg.msel = msel
        pg.mselL = L
        P.pm.openCustomPage(P.ref, P.st, pg)
        E.pump(P)
        return pg

    def click(a):
        E.pump(P)
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, '{"a":"%s"}' % a))
        E.pump(P)
    kB = codes.index(-(NR + rpair + 1))
    pg = page(kB)
    K.eq(str(TM.pick(u6)), "A", "PICK starts on alt A (Challenge)")
    CB["ms"] = 5000
    click("trbuy")
    K.check("Leave combat first" in str(pg.msg) and str(AS.pick(k6)) == "A", "PICK in combat refused: %s" % pg.msg)
    CB["ms"] = 0
    click("trbuy")
    K.check("Guardian's Oath" in str(pg.msg) and str(AS.pick(k6)) == "B" and str(TM.pick(u6)) == "B", "PICK out of combat: B now (%s) - FIX B2: the map's pick cache follows at once" % pg.msg)
    gid = [str(x) for x in AD.IDS].index("GuardiansOath")
    K.check(int(AS.left(k6, "GuardiansOath", JClass("java.lang.System").currentTimeMillis())) > 0, "PICK the new alt starts on its cooldown")
    pg.msel = codes.index(-(rpair + 1))
    click("trbuy")
    K.check("Wait" in str(pg.msg) and "before switching" in str(pg.msg) and str(AS.pick(k6)) == "B", "PICK 10 s between switches: %s" % pg.msg)
    AS.ALTSW.put(k6, JClass("java.lang.Long")(JClass("java.lang.System").currentTimeMillis() - 11000))
    click("trbuy")
    K.check(str(AS.pick(k6)) == "A" and str(TM.pick(u6)) == "A", "PICK after the wait: back to A (%s); FIX B2 the map reads A at once" % pg.msg)
    K.eq([str(x) for x in AS.slots(k6, ci)][2], "Challenge", "PICK the picked alt sits on Crouch + Ability 2")
    pg.msel = codes.index(-(ra1 + 1))
    click("trbuy")
    K.check("is free - it comes with its row" in str(pg.msg), "PICK Learn on a plain ability node: %s" % pg.msg)
    # ---- the ability panel: modifiers
    pg = page(codes.index(-(ra1 + 1)))
    info = [str(x) for x in Pg.abInfo(u6, St.data(u6), wi, ra1, False, True)]
    K.check(info[1].startswith("Ability 2 key") or "Ability 2" in info[1], "PANEL the key line: %s" % info[1])
    K.eq(info[3], "2", "PANEL 2 modifier slots")
    nm = int(info[4])
    mods = [(info[14 + j], info[9 + j]) for j in range(nm)]
    K.check(("Power", "Power 1") in [(a, b.replace("Power", "Power", 1)) for a, b in mods] or any(a == "Power" and not b.endswith("unlock") for a, b in mods),
            "PANEL Power (its node bought) is owned at Lv 1: %s" % mods)
    lk = [j for j, (a, b) in enumerate(mods) if b.endswith("- unlock")]
    K.check(len(lk) >= 1, "PANEL the modifiers not bought show 'unlock': %s" % mods)
    jP = [j for j, (a, b) in enumerate(mods) if a == "Power"][0]
    click("tmam%d" % jP)
    ab = AS.load(k6)
    eqs = [str(ab.getProperty(x)) for x in ("m1.RallyingGuard", "m2.RallyingGuard")]
    K.check("put" in str(pg.msg).lower() or "Power" in str(pg.msg), "PANEL equip Power from the panel: %s / %s" % (pg.msg, eqs))
    ap = TC.apanel(u6, A.treeCsv(u6))
    row = int(TC.rowOf(ap, "RallyingGuard"))
    K.check(str(TC.modName(ap, row, 0)).startswith("Power"), "PANEL slot 1 = Power (SkyyClasses' panel): %s" % TC.modName(ap, row, 0))
    j2 = lk[0]
    sel0 = int(pg.msel)
    click("tmam%d" % j2)
    up = codes[int(pg.msel)] if int(pg.msel) >= 0 else -1
    K.check("is locked - its unlock node is selected now" in str(pg.msg) and up >= 0 and T["UHA"][up] == "RallyingGuard" and T["UHM"][up] == mods[j2][0],
            "PANEL a locked modifier selects its unlock node: %s" % pg.msg)
    click("trbuy")
    K.check(str(pg.msg).startswith("Done:") and "unlocked" in str(pg.msg), "PANEL Learn = 1 point: %s" % pg.msg)
    mods2 = TC.amods(u6, "RallyingGuard", V.classCsv(St.data(u6), wi))   # the page's own list (SkyyClasses caches tree:fn:abil 1 s)
    f = [str(x).split("|") for x in list(mods2)[1:] if str(x).split("|")[0] == mods[j2][0]][0]
    K.eq([f[3], f[4]], ["1", "1"], "PANEL unlocked at Lv 1 (the level comes from use)")
    mi = int(AMD.find(mods[j2][0]))
    import time as _t
    C("AbilStore").set(k6, jpype.JArray(jpype.JString)(["m.RallyingGuard." + mods[j2][0]]), jpype.JArray(jpype.JString)([str(int(C("AbilFold").usesFor(3)))]))
    mods3 = TC.amods(u6, "RallyingGuard", V.classCsv(St.data(u6), wi))
    f = [str(x).split("|") for x in list(mods3)[1:] if str(x).split("|")[0] == mods[j2][0]][0]
    K.eq(f[4], "3", "PANEL its uses give Lv 3 (level by use)")
    pg.msel = sel0
    click("tmas0")
    ap = TC.apanel(u6, V.classCsv(St.data(u6), wi))
    K.eq(str(TC.modName(ap, row, 0)), "", "PANEL click a full slot = empty it (%s)" % pg.msg)
    # ---- Weaponcraft rows reach SkyyClasses through tree:fn:level
    UpSk.C.clear()
    v = [float(x) for x in UpSk.compute(u6, JClass("java.lang.System").currentTimeMillis())]
    K.eq([round(v[6], 6), round(v[7], 6)], [9.0, 10.0], "IG Reprisal 3 = 9 % thorns, Second Wind 2 = 10 % (UpSk vals [6] / [7])")
    K.eq(int(V.skillRank(u6, "Skill.Combat.b2.r4b")), 2, "IG Rally 2 (tree.rally for SkyySkills' out-of-combat regen)")
    K.save()


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, CJAR], verify=True)
    import jpype
    from jpype import JClass, JString
    J = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    cls = os.path.join(os.path.dirname(home), "Skyy_SkyyClasses")
    if os.path.isdir(LIVE_CLS):
        shutil.copytree(LIVE_CLS, cls)
        JClass(CPKG + "AbilStore").DIR = Paths.get(os.path.join(cls, "abilities"))
        J("TreeStore").bridge().put("class:fn:migInfo", JClass(CPKG + "AbilMigFn")())

    def start():
        J("TreeStore").DIR = Paths.get(os.path.join(home, "players"))
        J("TreeCfg").FILE = Paths.get(os.path.join(home, "trees.properties"))
        J("TreeStore").DATA.clear()
        J("TreeCfg").load()
        bp = Paths.get(home)
        msgs = [str(J(m).run(bp)) for m in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317", "TreeMig321", "TreeMig323", "TreeMig324", "TreeMigP5", "TreeMigP7", "TreeMig052")]
        J("TreeSk").loadV3(bp)
        bad, ds = [], {}
        for f in sorted(os.listdir(os.path.join(home, "players"))):
            if f.endswith(".properties"):
                dd = J("TreeStore").readFile(f[:-11])
                if bool(dd.bad):
                    bad.append(f)
                ds[f[:-11]] = dd
        return msgs, bad, ds
    msgs, bad, ds = start()
    K.eq(bad, [], "LIVE every player file reads")
    K.check(all(bool(dd.fold) for dd in ds.values()), "LIVE every file is folded (or had nothing to fold)")
    K.notes.append("LIVE fold applied %d, waits %d, last %s" % (int(J("TreeV3Mig").FOLD_APPLIED), int(J("TreeV3Mig").FOLD_WAITS), str(J("TreeV3Mig").FOLD_LAST)[:160]))
    h1 = T46.tree_hash(home)
    msgs2, bad2, _ds = start()
    K.check(T46.tree_hash(home) == h1 and bad2 == [] and all(m == "" for m in msgs2), "LIVE start 2 changes nothing")
    TM, St = J("TreeMap"), J("TreeStore")
    z = zipfile.ZipFile(jar)
    pics = set(n.split("/")[-1][:-7] for n in z.namelist() if n.startswith(MAPDIR + "Node/"))
    names, painted = set(), 0
    for k in ds:
        dd = St.readFile(k)
        for L in range(NL):
            codes = TM.nodes(L)
            tex = jpype.JArray(JString)(len(codes))
            lit = jpype.JArray(jpype.JBoolean)(len(TM.edges(L)))
            TM.paint(None, dd, L, False, tex, lit)
            names |= set(str(x) for x in tex)
            painted += 1
    K.check(painted > 0 and names <= pics, "LIVE %d live player x layout maps painted, every picture shipped (%s)" % (painted, sorted(names - pics)[:4]))
    K.save()
    sys.stdout.flush()
    os._exit(0)


EXPECT.update({   # checked 2026-10-23 (the class compare vs 0.5.2 of the first harness run; every member is a change of tools/trees_0_6_0_patch.py)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'SkyyTreesPlugin': ['~m setup'],
    'TreeCfg': ['+f CL_ABOVE', '+f CL_AP', '+f CL_FLOOR', '+f CL_FOLDRS', '+f CL_HEADX', '+f CL_STEP', '~<clinit>', '~m apply', '~m load'],
    'TreeClassOps': ['~m buy', '~m probeData'],   # fix round 2: buy's text (no "under Abilities")
    'TreeClass': ['+m foldRetry', '~m maint'],   # fix round (critic A1)
    'TreeData': ['+f fold', '+f foldNext', '+f foldRs', '+f foldWait', '+f lvlFix', '+f mgf', '+f mlv', '~c '],
    'TreeMap': ['+f ALTA', '+f ALTB', '+f PICK', '+f PK0', '+m abTex', '+m alt2', '+m altLabels', '+m frow', '+m pick', '~<clinit>', '~m cand', '~m nextRow', '~m nextRowD', '~m nodeRow', '~m nodeTv', '~m paint', '~m stat', '~m tex', '~m texRespec'],
    'TreePage': ['+m abClick', '+m abInfo', '+m abTag', '+m capT', '+m pickAlt', '~m abilEv', '~m build', '~m buildK', '~m handleIn', '~m kSets', '~m kUpd'],
    'TreeSk': ['~<clinit>', '~m rank'],
    'TreeSkillCmd': ['~m execute'],
    'TreeStore': ['+m v3foldUsed', '~m namesPut', '~m readFile', '~m v3clear', '~m v3rank'],
    'TreeV3': ['+f BLINE', '+f GN', '+f OLDC', '+f OLDK', '+f OLDROW', '+f OMAB', '+f OMC', '+f OMK', '+f OMMD', '+f RABIL', '+f RF2AB', '+f RF2IC', '+f RF2LINE', '+f RF2NAME', '+f RF2TEXT', '+f RFFXV', '+f UCOMB', '+f UMODN', '+f UTW', '+m clv', '+m gatesL', '+m gfRow2', '+m gix', '+m needC', '+m needOfC', '+m ptsOf', '+m rowCapR', '+m rowOpenC', '+m rowSpentR', '+m rowWhere', '~<clinit>', '~m anySpent', '~m buy', '~m buyText', '~m cellSub', '~m classCsv', '~m count', '~m derive', '~m detCost', '~m detHow', '~m detName', '~m detNeed', '~m detNext', '~m detNow', '~m detState', '~m effText', '~m freeLive', '~m freeNow', '~m freeRank', '~m freeSub', '~m fxCsv', '~m fxLive', '~m fxNow', '~m fxSum', '~m gates', '~m gatesD', '~m gfRow', '~m headUsed', '~m level', '~m lines', '~m live', '~m needRow', '~m needShort', '~m note', '~m opened', '~m openedD', '~m pageOfName', '~m pointsAll', '~m price', '~m priceText', '~m r3bLive', '~m rbReset', '~m respec', '~m rowCapLive', '~m rowGf', '~m rowHead', '~m rowNeed', '~m rowNeedMig', '~m rowSpent', '~m selRow', '~m skillRank', '~m spent', '~m spentBranch', '~m tvOfOld', '~m tvOfPage', '~m ustate'],
    'TreeAbMig': ['+f GONE0', '+m classesGone', '~<clinit>'],   # fix round 2
    'TreeV3Mig': ['+f FOLD_APPLIED', '+f FOLD_GONE_TOLD', '+f FOLD_LAST', '+f FOLD_LOG', '+f FOLD_TOLD', '+f FOLD_WAITS', '+m foldIn', '+m foldKeep', '+m foldLocked', '+m foldText', '+m foldTry', '+m foldUsedMark', '+m foldUsedPath', '+m foldUsedSeen', '~<clinit>', '~m fresh', '~m journal', '~m migrate', '~m readV3', '~m rowsCsv', '~m rowsKeep', '~m writeV3'],
})
_ORIG_COMPARE = T52._ORIG_COMPARE
SKIP = T52.SKIP


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit compare on copies WITHOUT the map / icon / lang entries (run_jar checks them)"""
    cps = []
    for j_, tag_ in ((jar, VERSION), (old_jar, "old")):
        cp = os.path.join(SCRATCH, "compare-%s.jar" % tag_)
        with zipfile.ZipFile(j_) as zi, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
            for n in zi.namelist():
                if not SKIP.match(n):
                    zo.writestr(n, zi.read(n))
        cps.append(cp)
    _ORIG_COMPARE(out, cps[0], cps[1], pkg, expect, added, removed)


HK.run_compare = _compare

if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("data", run_data), ("jar", run_jar), ("v4", run_v4), ("integ", run_integ), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyTrees"))
