"""Harness for SkyyTrees 0.6.2 (Beastmastery hatching nodes, Beastmastery in tree:<uuid>, Pet Fang x1.5 text; tools/trees_0_6_2_patch.py +
tools/trees_v3_data.py / trees_v3_effects.py r062_apply). Build first:
    python tools/trees_0_6_2_patch.py && python SkyyTrees/build_skyytrees_0.6.2.py
    python SkyyTrees/test_skyytrees_0.6.2.py [--keep] [--expect-dump]
Phases (each its own child JVM, -Xverify:all where classes run; the kit's verify / class compare 0.6.1 -> 0.6.2 / engine-access audit around them):
  static  the generated script = the patch's output (re-run to identical bytes), 0.6.1's patch still regenerates 0.6.1 byte for byte, header /
          version, no new system / command / class, line endings kept
  data    the opt-in rule: WITHOUT r062_apply the two tables dump exactly like the committed (git HEAD) modules - every other build is
          unchanged; WITH it: Warm Nest / Burrow Nursery in their rows (3 upgrades a row, new keys), the two SkyyPets rows appended (every
          older row keeps its index), Pet Fang 2.6 / 1.5 a rank + its text in all 8 class trees' Weaponcraft, the budgets (class XP 29.5 %,
          hatch cut 20 % <= 25 %, Hatchery slots 5 <= 10); r062_apply twice = once; after v4_apply it refuses (order)
  jar     the two node icons: own 64 x 64 PNGs (not the Gentle Hand picture, not each other), their item JSONs + lang names; the keys and
          names in TreeV3's tables; the manifest version
  bm      EXECUTED (SkyyTrees in a JVM with the engine kit): buy Warm Nest x4 / Burrow Nursery x2 in the Beastmastery tree (points = the
          Beastmastery level), tree:fn:level-style skillRank answers the ranks while tree:reads:SkyyPets lists the keys and 0 when it does
          not (an older SkyyPets: coming soon, buy refused); postTree -> tree:<uuid> holds ",Beastmastery:<spent>/<points>" before ",Class:";
          SkyyMenu 0.3.47's REAL MenuPage.treeRows (its jar in the same JVM) shows "N unspent points in Beastmastery" -> /tree beastmastery;
          every layout map painted with the new ranks uses shipped pictures
  live    start twice on a scratch COPY of the live Skyy_SkyyTrees folder (0.6.0's phase: migrations, every file reads, start 2 changes nothing,
          every player x layout map painted with shipped pictures)
NOT COVERED (UNVERIFIED in game): the look of the two composited icons and of the 3-node rows on the radial map at 100-200 %.
"""
import os, sys, json, subprocess, importlib.util, zipfile, re, shutil, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "bm1", "trees")]
import skyybuild as B
import harness_kit as HK

_s = importlib.util.spec_from_file_location("test_skyytrees_0_6_0", os.path.join(HERE, "test_skyytrees_0.6.0.py"))
T60 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T60)
sys.argv[:] = _argv

VERSION = "0.6.2"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.6.1.jar")
MJAR = os.path.join(ROOT, "SkyyMenu", "SkyyMenu-0.3.47.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.6.1.py")
PATCH = os.path.join(TOOLS, "trees_0_6_2_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T60.JAR = JAR
ADDED = []
EXPECT = {   # checked 2026-10-24 against the harness's class compare 0.6.1 -> 0.6.2 (tools/dev/scratch method diffs: every ~m below except postTree /
    # the version strings is the upgrade count NU 818 -> 820 inlined as a constant - the two new Beastmastery upgrades)
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup"], "TreeCfg": ["~m load"],   # VERSION strings
    "TreeData": ["~c "], "TreePage": ["~m abClick"], "TreeSk": ["~<clinit>"], "TreeV3Mig": ["~m readV3", "~m writeV3"],         # NU / the tables
    "TreeFx": ["~m postTree"],                                                                                                  # + Beastmastery
    "TreeMap": ["~<clinit>", "~m cand", "~m nodeRow", "~m nodeTv", "~m paint", "~m tex", "~m texRespec"],
    "TreeV3": ["~<clinit>", "~m buyText", "~m cellSub", "~m count", "~m detCost", "~m detHow", "~m detName", "~m detNeed", "~m detNext", "~m detNow",
               "~m detState", "~m effText", "~m fxLive", "~m fxNow", "~m live", "~m r3bLive", "~m ustate"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
NEW_ICONS = {"Skyy_NodeIcon_Beastmastery_B3R2c": ("Warm Nest", "Skill.Beastmastery.b3.r2c"), "Skyy_NodeIcon_Beastmastery_B2R4c": ("Burrow Nursery", "Skill.Beastmastery.b2.r4c")}
U9 = "62626262-0000-0000-0000-000000000009"

DUMP = r'''
import sys, json
sys.path.insert(0, sys.argv[1])
import trees_v3_data as D
import trees_v3_effects as E
out = {"effects": [list(e) for e in E.EFFECTS], "bm": D.tree("Beastmastery"), "combat": D.tree("Combat"), "pets": E.cfg_text("SkyyPets"),
       "reads": E.reads_csv("SkyyPets"), "trees": E.cfg_text("SkyyTrees")}
print(json.dumps(out, sort_keys=True))
'''


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.6.2 - build script') and g.count('VERSION = "0.6.2"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("V3D.r062_apply()") == 1 and g.count("V3E.r062_apply()") == 1 and "r062_apply" not in o, "S r062 is applied by this build only")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "trees_0_6_1_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_data(out, jar, scratch, _home):
    K = HK.Child(out)
    # the opt-in rule: the tables WITHOUT r062 dump exactly like the committed modules (git HEAD)
    hd = os.path.join(scratch, "head")
    os.makedirs(hd, exist_ok=True)
    for m in ("trees_v3_data.py", "trees_v3_effects.py"):
        p = subprocess.run(["git", "show", "HEAD:tools/" + m], capture_output=True, cwd=ROOT)
        K.check(p.returncode == 0, "D git show HEAD:tools/%s" % m)
        open(os.path.join(hd, m), "wb").write(p.stdout)
    d1 = subprocess.run([sys.executable, "-c", DUMP, TOOLS], capture_output=True, text=True)
    d0 = subprocess.run([sys.executable, "-c", DUMP, hd], capture_output=True, text=True)
    K.check(d1.returncode == 0 and d0.returncode == 0 and d1.stdout == d0.stdout and len(d1.stdout) > 10000,
            "D without r062_apply the tables are byte-equal to git HEAD (every other build unchanged): %s %s" % (d1.stderr[-200:], d0.stderr[-200:]))
    import trees_v3_data as V3D
    import trees_v3_effects as V3E
    n0 = len(V3E.EFFECTS)
    old_rows = [tuple(e) for e in V3E.rows("SkyyPets")]
    V3E.r062_apply()
    V3E.r062_apply()
    K.check(len(V3D.R062_APPLIED) == 1 and len(V3E.R062_APPLIED) == 1 and len(V3E.EFFECTS) == n0 + 2, "D r062_apply twice = once (+2 rows)")
    new_rows = [tuple(e) for e in V3E.rows("SkyyPets")]
    K.eq([r[:5] for r in new_rows[:len(old_rows)]], [r[:5] for r in old_rows], "D every older SkyyPets row keeps its index (V3P<i> / V3X<i>)")
    K.eq([r for r in new_rows[len(old_rows):]], [("Beastmastery", 3, "r2c", "SkyyPets", "hatchspd", 0.05, None, 0), ("Beastmastery", 2, "r4c", "SkyyPets", "hatch", 1.0, None, 0)],
         "D the two hatching rows appended")
    fang = dict((r[4], r[5]) for r in new_rows if r[:3] == ("Combat", 3, "r3a"))
    K.eq(fang, {"xp.combat": 0.026, "dmg": 1.5}, "D Pet Fang 2.6 % class XP / 1.5 % damage a rank (was 2 / 1)")
    bm = V3D.tree("Beastmastery")
    r2 = bm["branches"][2]["rows"][1]
    r4 = bm["branches"][1]["rows"][3]
    K.check([u["id"] for u in r2["ups"]] == ["r2a", "r2b", "r2c"] and r2["ups"][2]["name"] == "Warm Nest" and r2["ups"][2]["max"] == 4, "D Warm Nest = Wild Roots row 2, 3rd upgrade, 4 ranks")
    K.check([u["id"] for u in r4["ups"]] == ["r4a", "r4b", "r4c"] and r4["ups"][2]["name"] == "Burrow Nursery" and r4["ups"][2]["max"] == 2, "D Burrow Nursery = Deep Burrow row 4, 3rd upgrade, 2 ranks")
    K.check(abs(V3E.tree_xp("Combat") - 0.295) < 1e-9, "D class (Combat) tree XP 29.5 %% <= 30 %% (%.3f)" % V3E.tree_xp("Combat"))
    K.check(abs(sum(V3E.vmax(e) for e in V3E.EFFECTS if e[4] == "hatchspd") - 0.20) < 1e-9 and sum(V3E.vmax(e) for e in V3E.EFFECTS if e[4] == "hatch") == 5.0,
            "D hatch cut 20 % (budget 25 %), Hatchery slots 3 + 2 = 5 (clamp 10)")
    t = V3E.cfg_text("SkyyPets")
    K.check("tree.Combat.b3.r3a.xp.per=2.6\ntree.Combat.b3.r3a.xp.max=19.5\n" in t and "tree.Combat.b3.r3a.dmg.per=1.5\ntree.Combat.b3.r3a.dmg.max=11.25\n" in t
            and "tree.Beastmastery.b3.r2c.hatchspd.per=5\ntree.Beastmastery.b3.r2c.hatchspd.max=20\n" in t and "tree.Beastmastery.b2.r4c.hatch.per=1\ntree.Beastmastery.b2.r4c.hatch.max=2\n" in t,
            "D SkyyPets' trees.properties defaults (Pet Fang 2.6 / 19.5, 1.5 / 11.25; Warm Nest 5 / 20; Burrow Nursery 1 / 2)")
    V3D.V4_MODNAME_SUFFIX = True
    V3D.v4_apply()
    txt = set()
    for tr in V3D.TREES:
        if tr.get("v4"):
            for b in tr["branches"]:
                for r in b["rows"]:
                    for u in r["ups"]:
                        if u.get("key") == "Skill.Combat.b3.r3a":
                            txt.add((tr["name"], u["text"]))
    K.check(len(txt) == 8 and all(x[1] == "+2.6% class XP and +1.5% damage/rank, x your Combat pet's rarity bonus" for x in txt), "D Pet Fang's new text in all 8 Weaponcraft branches: %s" % sorted(txt)[:2])
    ok = False
    V3D.R062_APPLIED[:] = []
    try:
        V3D.r062_apply()
    except AssertionError:
        ok = True
    V3D.R062_APPLIED.append(1)
    K.check(ok, "D r062_apply after v4_apply is refused (Weaponcraft copies Pet Fang's text)")
    K.save()


def run_jar(out, jar, scratch, _home):
    import skyyart as SA
    K = HK.Child(out)
    z = zipfile.ZipFile(jar)
    names = set(z.namelist())
    m = json.loads(z.read("manifest.json"))
    K.check(str(m.get("Version")) == VERSION, "J manifest version %s" % m.get("Version"))
    gh = z.read("Common/Icons/ItemsGenerated/Skyy_NodeIcon_Beastmastery_B3R1b.png")
    pngs = []
    lang = z.read("Server/Languages/en-US/server.lang").decode("utf-8")
    for iid, (nm, key) in NEW_ICONS.items():
        p = "Common/Icons/ItemsGenerated/%s.png" % iid
        K.check(p in names, "J %s icon shipped" % iid)
        b = z.read(p)
        im = SA.png_decode(b)
        cov = sum(1 for y in range(64) for x in range(64) if im.get(x, y)[3] > 128)
        K.check((im.w, im.h) == (64, 64) and 600 < cov < 3000 and b != gh, "J %s: 64 x 64, %d opaque pixels, not the Gentle Hand picture" % (iid, cov))
        pngs.append(b)
        js = json.loads(z.read("Server/Item/Items/Utility/%s.json" % iid))
        K.check(js.get("Icon") == "Icons/ItemsGenerated/%s.png" % iid and "Recipe" not in js and "Categories" not in js, "J %s item JSON (icon-only)" % iid)
        K.check(("server.items.%s.name=%s" % (iid, nm)) in lang, "J %s lang name %s" % (iid, nm))
    K.check(pngs[0] != pngs[1], "J the two icons differ")
    blob = z.read("com/skyy/trees/TreeV3.class")
    K.check(all(k.encode() in blob for _n, k in NEW_ICONS.values()) and b"Warm Nest" in blob and b"Burrow Nursery" in blob, "J TreeV3 knows the two keys + names")
    K.save()


def run_bm(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    import trees_v3_data as V3D
    import trees_v3_effects as V3E
    V3E.r062_apply()                     # the reader lists below = SkyyPets 0.4.17's (its tree:reads:SkyyPets)
    E, J, V, T = T60._env(scratch, "bm", [MJAR])
    Paths, UUID, Int = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Integer")
    St, Cfg, TM = J("TreeStore"), J("TreeCfg"), J("TreeMap")
    d0 = os.path.join(scratch, "bm")
    os.makedirs(os.path.join(d0, "players"), exist_ok=True)
    St.DIR = Paths.get(os.path.join(d0, "players"))
    Cfg.FILE = Paths.get(os.path.join(d0, "trees.properties"))
    Cfg.load()
    J("TreeSk").loadV3(Paths.get(d0))
    J("TreeSk").reads(True)
    br = St.bridge()
    T60._reads(br)
    K.check("Skill.Beastmastery.b3.r2c" in str(br.get("tree:reads:SkyyPets")) and "Skill.Beastmastery.b2.r4c" in str(br.get("tree:reads:SkyyPets")), "BM the 0.4.17 reader list names both keys")
    LV = {"Beastmastery": 12}
    br.put("skill:fn:level", T60._fn(JImplements, JOverride, lambda a: Int(LV.get(str(a[1]), 0))))
    br.put("profile:class:" + U9, "Warrior")
    u = UUID.fromString(U9)
    d = St.data(u)
    bv = T["TNAME"].index("Beastmastery")
    wn, bn = T60._uk(T, bv, "Skill.Beastmastery.b3.r2c"), T60._uk(T, bv, "Skill.Beastmastery.b2.r4c")
    K.eq([T["UNAME"][wn], T["UMAX"][wn], T["UNAME"][bn], T["UMAX"][bn]], ["Warm Nest", 4, "Burrow Nursery", 2], "BM the two upgrades in the Beastmastery tree")
    # row 2 / row 4 open the usual way: 5 / 15 points spent below (Green Companion 5, Whistle Training 5, Fang Familiar 3, Digger's Calling 5)
    LV["Beastmastery"] = 40
    for k, n in (("Skill.Beastmastery.b3.r1a", 5), ("Skill.Beastmastery.b1.r1a", 5), ("Skill.Beastmastery.b1.r1b", 3), ("Skill.Beastmastery.b2.r1a", 5)):
        for _i in range(n):
            msg = str(V.buy(u, d, bv, T60._uk(T, bv, k), False))
            K.check(msg.startswith("Done:"), "BM buy %s: %s" % (k, msg[:90]))
    for _i in range(4):
        msg = str(V.buy(u, d, bv, wn, False))
        K.check(msg.startswith("Done: Warm Nest rank %d/4" % (_i + 1)), "BM buy Warm Nest %d: %s" % (_i + 1, msg[:90]))
    K.check(not str(V.buy(u, d, bv, wn, False)).startswith("Done:"), "BM Warm Nest stops at 4")
    for k, n in (("Skill.Beastmastery.b3.r3a", 4), ("Skill.Beastmastery.b3.r3b", 1)):
        for _i in range(n):
            K.check(str(V.buy(u, d, bv, T60._uk(T, bv, k), False)).startswith("Done:"), "BM buy %s" % k)
    for _i in range(2):
        msg = str(V.buy(u, d, bv, bn, False))
        K.check(msg.startswith("Done: Burrow Nursery rank %d/2" % (_i + 1)), "BM buy Burrow Nursery %d: %s" % (_i + 1, msg[:120]))
    K.eq([int(V.skillRank(u, "Skill.Beastmastery.b3.r2c")), int(V.skillRank(u, "Skill.Beastmastery.b2.r4c"))], [4, 2], "BM skillRank (tree:fn:level) = 4 / 2 while SkyyPets lists the keys")
    spent = int(V.spent(d, bv))
    K.eq(spent, 5 + 5 + 3 + 5 + 4 + 4 + 1 + 2, "BM points spent in Beastmastery")
    # tree:<uuid>
    J("TreeFx").postTree(u, d)
    s = str(br.get("tree:" + U9))
    K.check((",Beastmastery:%d/40" % spent) in s and s.index(",Beastmastery:") < s.index(",Class:") and s.count("Beastmastery") == 1, "BM tree:<uuid> lists Beastmastery before Class: %s" % s)
    K.check(s.startswith("Mining:") and len(s.split(",")) == 9 + 1 + 1, "BM tree:<uuid>: 9 old trees + Beastmastery + Class (%d entries)" % len(s.split(",")))
    # SkyyMenu 0.3.47's REAL parser
    rows = [list(map(str, r)) for r in JClass("com.skyy.menu.MenuPage").treeRows(u)]
    K.check(["%d unspent points in Beastmastery" % (40 - spent), "tree:beastmastery"] in rows, "BM SkyyMenu 0.3.47 Right now: %s" % rows)
    K.check(int(V.pageOfName("beastmastery")) >= 0, "BM /tree beastmastery opens a page")
    # paint every layout with the new ranks: shipped pictures only
    z = zipfile.ZipFile(jar)
    pics = set(n.split("/")[-1][:-7] for n in z.namelist() if n.startswith(T60.MAPDIR + "Node/"))
    names = set()
    for L in range(T60.NL):
        codes = TM.nodes(L)
        tex = jpype.JArray(jpype.JString)(len(codes))
        lit = jpype.JArray(jpype.JBoolean)(len(TM.edges(L)))
        TM.paint(None, d, L, False, tex, lit)
        names |= set(str(x) for x in tex)
    K.check(names and names <= pics, "BM every layout painted with the new ranks uses shipped pictures (%s)" % sorted(names - pics)[:4])
    # an older SkyyPets (0.4.16): its list lacks the two keys -> coming soon, rank 0, no buy
    old = ",".join(k for k in str(br.get("tree:reads:SkyyPets")).split(",") if k not in ("Skill.Beastmastery.b3.r2c", "Skill.Beastmastery.b2.r4c"))
    br.put("tree:reads:SkyyPets", old)
    J("TreeSk").reads(True)
    u2 = UUID.fromString(U9.replace("09", "10"))
    br.put("profile:class:" + str(u2), "Warrior")
    d2 = St.data(u2)
    msg = str(V.buy(u2, d2, bv, T60._uk(T, bv, "Skill.Beastmastery.b3.r1b"), False))
    msg2 = str(V.buy(u2, d2, bv, wn, False))
    K.check(not msg2.startswith("Done:") and int(V.skillRank(u, "Skill.Beastmastery.b3.r2c")) == 0, "BM with an older SkyyPets: Warm Nest cannot be bought, rank reads 0: %s" % msg2[:120])
    K.save()
    sys.stdout.flush()
    os._exit(0)


HK.run_compare = T60._compare

if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("data", run_data), ("jar", run_jar), ("bm", run_bm), ("live", T60.run_live)],
           script=__file__, live=(T60.LIVE_DIR, "Skyy_SkyyTrees"))
