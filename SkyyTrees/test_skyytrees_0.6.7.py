"""Harness for SkyyTrees 0.6.7 (Accessory Plates text +0.75 %, the wc15 numbers folded into tools/trees_v3_effects.py; tools/trees_0_6_7_patch.py).
Build first:
    python tools/trees_0_6_7_patch.py && python SkyyTrees/build_skyytrees_0.6.7.py
    python SkyyTrees/test_skyytrees_0.6.7.py [--keep] [--expect-dump] [--base <folder holding the older jars>]
--base: the checkout whose SkyyTrees / SkyyClasses / SkyyPets folders hold the built jars (0.6.4 / 0.6.6 Trees, Classes 0.1.50, Pets 0.4.20);
        default = this checkout, then the main checkout above .claude/worktrees (jars are git-ignored, so a worktree has none).
Phases (each its own child JVM, -Xverify:all where classes run; the kit's verify / class compare 0.6.6 -> 0.6.7 / engine-access audit around them):
  static   the generated script = the patch's output (re-run to identical bytes), 0.6.6's patch still regenerates 0.6.6 byte for byte, header /
           version, no new class / system / command / method, line endings kept
  effects  (python) tools/trees_v3_effects.py EFFECTS holds every tools/wc15.py ROWS NEW number; for EVERY applier the outputs its build reads
           (rows, keys, reader list, trees.properties text, Server Setup rows, cfg fields / methods, wc15 mig_rows / java()) equal the
           pre-fold table (commit 1b4c6c9c) + wc15.apply - i.e. no behaviour change for any mod or saved rank; wc15.apply now swaps 0 rows; check()
  old66    dumps the 0.6.6 jar's TreeV3 UKEY / UNAME / UTEXT (the text phase compares)
  text     EXECUTED in the 0.6.7 jar: every Accessory Plates node (Weaponcraft branch 2 row 4 of each class tree) says +0.75 % in UTEXT,
           detHow (the node's "Plan:" line) and effText (the live "rank 2 of 3 - ..." line, tree:reads:SkyyAccessories listing it); every
           other UTEXT equals 0.6.6's (only the Accessory Plates entries changed)
  bridge   EXECUTED TreeFx.postTree: tree:<uuid> holds ",Beastmastery:<spent>/<points>" (a bought Warm Nest rank counts) before ",Class:";
           Warm Nest (Skill.Beastmastery.b3.r2c) + Burrow Nursery (b2.r4c) are live (buyable) with SkyyPets 0.4.20's own tree:reads:SkyyPets
           list (read from its jar) and coming soon without it
  creative / g64 / data / sow / jar65 / path / mig / integ / farm / sap / live   the older EXEC phases on the 0.6.7 jar (unchanged behaviour;
           live = start twice on a scratch COPY of the live Skyy_SkyyTrees folder). Left out: 0.6.4's jar phase (it needs the 0.6.3 jar, no
           longer kept) - the zip entry compare 0.6.6 -> 0.6.7 is in 'static'.
"""
import os, sys, json, subprocess, importlib.util, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.6.7"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "trees067", "trees")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)]
import skyybuild as B
import harness_kit as HK


def _base():
    if "--base" in sys.argv:
        return os.path.abspath(sys.argv[sys.argv.index("--base") + 1])
    if os.path.isfile(os.path.join(HERE, "SkyyTrees-0.6.6.jar")):
        return ROOT
    p = os.path.abspath(ROOT)
    parts = p.split(os.sep)
    if ".claude" in parts:
        return os.sep.join(parts[:parts.index(".claude")])
    return ROOT


BASE = _base()
_s = importlib.util.spec_from_file_location("test_skyytrees_0_6_6", os.path.join(HERE, "test_skyytrees_0.6.6.py"))
T66 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T66)
sys.argv[:] = _argv
T65, T64, T63, T60 = T66.T65, T66.T64, T66.T63, T66.T60

PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(BASE, "SkyyTrees", "SkyyTrees-0.6.6.jar")
CJAR = os.path.join(BASE, "SkyyClasses", "SkyyClasses-0.1.50.jar")
PJAR = os.path.join(BASE, "SkyyPets", "SkyyPets-0.4.20.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.6.6.py")
PATCH = os.path.join(TOOLS, "trees_0_6_7_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
for _m in (T60, T63, T64, T65, T66):
    _m.JAR = JAR
    _m.SCRATCH = SCRATCH
for _m in (T60, T63, T64):
    _m.CJAR = CJAR                       # the SET pin's reader list (SkyyClasses 0.1.50) - jars are not in a worktree
T65.OLD_JAR = os.path.join(BASE, "SkyyTrees", "SkyyTrees-0.6.4.jar")   # run_g64 / run_jar compare against 0.6.4 (kept)
T60.VERSION = VERSION
AP_NEW = "+0.75% max Health/rank per counting accessory (max 5)"
AP_OLD = "+0.5% max Health/rank per counting accessory (max 5)"
EXPECT = {   # checked 2026-10-30 (the class compare 0.6.6 -> 0.6.7): the version strings (CfgFn / CfgRows / SkyyTreesPlugin / TreeCfg) and
    # TreeV3's UTEXT constant (the Accessory Plates text) - nothing else
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'SkyyTreesPlugin': ['~m setup'],
    'TreeCfg': ['~m load'],
    'TreeV3': ['~<clinit>'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U1 = T65.U1


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.6.7 - build script') and g.count('VERSION = "0.6.7"') == 1 and 'VERSION = "0.6.6"' not in g, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(")
            and g.count("makeClass(") == o.count("makeClass(") and g.count("\nM(") == o.count("\nM("), "S no new command / system / class / method")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "trees_0_6_6_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq(sorted(nb - na) + sorted(na - nb), [], "S the same jar entries as 0.6.6")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(chg, ["manifest.json"], "S only the manifest (version) differs among the non-class entries")
    K.save()


PRE_FOLD = "1b4c6c9c"   # the last commit of tools/trees_v3_effects.py before the 0.6.7 fold (pin: SkyyAccessories 0.5.33)


def _old_v3e(scratch):
    """the pre-fold tools/trees_v3_effects.py + trees_v3_data.py (commit PRE_FOLD) in a folder of their own"""
    d = os.path.join(scratch, "headv3")
    os.makedirs(d, exist_ok=True)
    for f in ("trees_v3_effects.py", "trees_v3_data.py"):
        p = subprocess.run(["git", "-C", ROOT, "show", PRE_FOLD + ":tools/" + f], capture_output=True)
        assert p.returncode == 0, p.stderr
        open(os.path.join(d, f), "wb").write(p.stdout)
    return d


EQ_SRC = r'''
import sys, os, json
which, mod, r062, old, tools = sys.argv[1], sys.argv[2], sys.argv[3] == "1", sys.argv[4], sys.argv[5]
sys.path.insert(0, tools)
if which == "old":
    sys.path.insert(0, old)
import trees_v3_effects as V3E
assert os.path.dirname(os.path.abspath(V3E.__file__)) == os.path.abspath(old if which == "old" else tools), V3E.__file__
if r062:
    V3E.r062_apply()
import wc15
out = {}
if mod in wc15.ROWS:
    out["n"] = wc15.apply(V3E, mod)
    out["own"] = repr(V3E.rows(mod))
    out["mig"] = repr(wc15.mig_rows(V3E, mod))
    out["java"] = repr(wc15.java(V3E, mod, "L", "@PKG@.L.info", "@PKG@.L.warn"))
out["rows"] = repr(V3E.rows(mod))
out["keys"] = repr(V3E.keys(mod))
out["reads"] = repr(V3E.reads_csv(mod))
out["desc"] = repr([V3E.describe(e) for e in V3E.rows(mod)])
if mod in V3E.WHERE or mod in V3E.FILE_OF:
    out["text"] = V3E.cfg_text(mod)
    out["fields"] = repr(V3E.cfg_fields(mod))
    out["methods"] = repr(V3E.cfg_methods(mod, "W.warn"))
    out["tf"] = repr(V3E.cfg_text_field(mod))
    out["cfgrows"] = repr(V3E.cfg_rows(mod, "C", "Skyy_X/trees.properties", "cat"))
if mod == "ALL4":
    for m in wc15.ROWS:
        wc15.apply(V3E, m)
    out["all"] = repr(V3E.EFFECTS)
V3E.check()
print(json.dumps(out))
'''


def run_effects(out, jar, scratch, _home):
    K = HK.Child(out)
    import trees_v3_effects as V3E
    import wc15 as WC
    for m, rs in WC.ROWS.items():
        for r in rs:
            h = [e for e in V3E.EFFECTS if (e[0], e[1], e[2], e[4]) == r[:4]]
            K.check(len(h) == 1 and h[0][3] == m and repr(h[0][5]) == repr(r[5]), "E %s %s.b%d.%s %s = %s (wc15 NEW, the table itself): %s" % (m, r[0], r[1], r[2], r[3], r[5], h))
    K.eq(sum(len(rs) for rs in WC.ROWS.values()), 14, "E the 14 wc15 rows")
    for m, rs in WC.HELD.items():
        for r in rs:
            h = [e for e in V3E.EFFECTS if (e[0], e[1], e[2], e[4]) == r[:4]]
            K.check(len(h) == 1 and abs(h[0][5] - r[4]) < 1e-12, "E HELD row stays on its old number: %s %s" % (m, r))
    V3E.check()
    K.check(abs(V3E.tree_hp("Combat") - 0.1375) < 1e-12 and V3E.tree_hp("Combat") <= V3E.tree_hp_max("Combat") + 1e-12,
            "E the Weaponcraft max Health budget = 13.75 %% exactly (Toughness 2.5 + Accessory Plates 11.25): %.4f" % V3E.tree_hp("Combat"))
    old = _old_v3e(scratch)
    src = os.path.join(scratch, "eq_child.py")
    open(src, "w").write(EQ_SRC)
    mods = list(WC.ROWS) + ["SkyyPets", "SkyyExploration", "SkyySkills", "SkyyCooking", "SkyyFishing", "SkyyTrees", "ALL4"]
    for mod in mods:
        for r062 in (0, 1):
            res = {}
            for w in ("old", "new"):
                p = subprocess.run([sys.executable, "-I", src, w, mod, str(r062), old, TOOLS], capture_output=True, text=True, cwd=scratch)
                K.check(p.returncode == 0, "E %s %s r062=%d runs: %s" % (w, mod, r062, p.stderr[-400:]))
                res[w] = json.loads(p.stdout.strip().splitlines()[-1]) if p.returncode == 0 else {}
            diff = sorted(k for k in set(res["old"]) | set(res["new"]) if k != "n" and res["old"].get(k) != res["new"].get(k))
            K.eq(diff, [], "E %s (r062_apply %s): every output its build reads = the pre-fold table + wc15.apply" % (mod, bool(r062)))
            if mod in WC.ROWS:
                K.check(res["new"].get("n") == 0 and res["old"].get("n") == len(WC.ROWS[mod]),
                        "E %s: wc15.apply swapped %s rows before, %s now (the table holds them)" % (mod, res["old"].get("n"), res["new"].get("n")))
    K.save()


def run_old66(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=True)
    from jpype import JClass
    V = JClass(PKG + "TreeV3")
    d = dict((n, [str(x) for x in getattr(V, n)]) for n in ("UKEY", "UNAME", "UTEXT"))
    json.dump(d, open(os.path.join(scratch, "old66-dump.json"), "w"))
    K.check(len(d["UTEXT"]) == len(d["UKEY"]) and AP_OLD in d["UTEXT"], "O the 0.6.6 jar says the old Accessory Plates text")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_text(out, jar, scratch, _home):
    K = HK.Child(out)
    E, J, V, T, br, d0 = T65._env(scratch, "tx")
    from jpype import JClass
    old = json.load(open(os.path.join(scratch, "old66-dump.json")))
    ut = [str(x) for x in V.UTEXT]
    K.eq([str(x) for x in V.UKEY], old["UKEY"], "T the same upgrade keys as 0.6.6")
    ch = [i for i in range(len(ut)) if ut[i] != old["UTEXT"][i]]
    ap = [i for i in range(len(ut)) if T["UNAME"][i] == "Accessory Plates"]
    K.check(len(ap) >= 8 and ch == ap, "T only the Accessory Plates texts changed (%d changed, %d Accessory Plates nodes)" % (len(ch), len(ap)))
    K.check(all(ut[i] == AP_NEW and old["UTEXT"][i] == AP_OLD for i in ap), "T every Accessory Plates node: %r -> %r" % (AP_OLD, AP_NEW))
    K.check(AP_OLD not in ut, "T no old Accessory Plates text left")
    K.notes.append("T Accessory Plates keys: %s" % ", ".join(T["UKEY"][i] for i in ap))
    for i in ap:
        h = str(V.detHow(int(T["UROW"][i]), i))
        K.check(h.startswith("Plan: " + AP_NEW + "."), "T detHow renders the new text for %s: %s" % (T["UKEY"][i], h[:120]))
        K.check(bool(V.r3bLive(i)), "T %s is live (tree:reads:SkyyAccessories lists it)" % T["UKEY"][i])
        e = str(V.effText(i, 2))
        K.eq(e, "rank 2 of 3 - " + AP_NEW, "T effText renders the new text for %s" % T["UKEY"][i])
    K.save()
    sys.stdout.flush()
    os._exit(0)


def _pets_reads():
    """SkyyPets 0.4.20's own tree:reads:SkyyPets value (PetV3.READS, a class constant)"""
    b = zipfile.ZipFile(PJAR).read("com/skyy/pets/PetV3.class")
    i = b.index(b"Skill.Beastmastery.b3.r2c")
    for st in range(i, max(0, i - 70000), -1):
        if b[st] == 1:
            ln = int.from_bytes(b[st + 1:st + 3], "big")
            if st + 3 <= i < st + 3 + ln:
                return b[st + 3:st + 3 + ln].decode("utf-8")
    raise AssertionError("no reader list in the SkyyPets jar")


def run_bridge(out, jar, scratch, _home):
    K = HK.Child(out)
    E, J, V, T, br, d0 = T65._env(scratch, "br")
    from jpype import JClass
    UUID = JClass("java.util.UUID")
    St, Fx = J("TreeStore"), J("TreeFx")
    u = UUID.fromString(U1)
    d = St.data(u)
    wn, bn = T["UKEY"].index("Skill.Beastmastery.b3.r2c"), T["UKEY"].index("Skill.Beastmastery.b2.r4c")
    K.check(T["UNAME"][wn] == "Warm Nest" and T["UNAME"][bn] == "Burrow Nursery", "B the hatching nodes are in the tree (Warm Nest, Burrow Nursery)")
    pr = _pets_reads()
    K.check("Skill.Beastmastery.b3.r2c" in pr.split(",") and "Skill.Beastmastery.b2.r4c" in pr.split(","), "B SkyyPets 0.4.20 lists both in tree:reads:SkyyPets")
    br.put("tree:reads:SkyyPets", "")
    K.check(not bool(V.live(wn)) and not bool(V.live(bn)), "B without SkyyPets' list they are coming soon")
    br.put("tree:reads:SkyyPets", pr)
    K.check(bool(V.live(wn)) and bool(V.live(bn)), "B with SkyyPets 0.4.20's list both are live (buyable)")
    bv = T["TNAME"].index("Beastmastery")
    s0 = int(V.spent(d, bv))
    Fx.postTree(u, d)
    k = "tree:" + U1
    s = str(br.get(k))
    K.check(",Beastmastery:%d/" % s0 in s, "B tree:<uuid> lists Beastmastery: %s" % s)
    d.rk[wn] = 1
    s1 = int(V.spent(d, bv))
    Fx.postTree(u, d)
    s = str(br.get(k))
    pts = int(V.pointsAll(u, bv))
    K.check(s1 == s0 + 1 and (",Beastmastery:%d/%d" % (s1, pts)) in s, "B a bought Warm Nest rank counts: %s (points %d)" % (s, pts))
    K.check(s.index(",Beastmastery:") < s.index(",Class:") if ",Class:" in s else True, "B Beastmastery before Class")
    K.check(s.count("Beastmastery:") == 1 and not s.startswith(","), "B listed once")
    d.rk[wn] = 0
    K.save()
    sys.stdout.flush()
    os._exit(0)


HK.run_compare = T60._compare

if __name__ == "__main__":
    for _p in (OLD_JAR, CJAR, PJAR, T65.OLD_JAR):
        assert os.path.isfile(_p), "missing %s (pass --base <the checkout with the built jars>)" % _p
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("effects", run_effects), ("old66", run_old66), ("text", run_text), ("bridge", run_bridge),
                   ("creative", T66.run_creative), ("g64", T65.run_g64), ("data", T65.run_data), ("sow", T65.run_sow), ("jar65", T65.run_jar),
                   ("path", T64.run_path), ("mig", T64.run_mig), ("integ", T64.run_integ),
                   ("farm", T63.run_farm), ("sap", T63.run_sap), ("live", T63.run_live)],
           script=__file__, live=(T60.LIVE_DIR, "Skyy_SkyyTrees"))
