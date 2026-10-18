"""Harness for SkyyTrees 0.3.23 (round fortune, builder F1: Mining Fortune + Smelting Fortune +10% a level, max 10, the one-time
trees.properties update TreeMig323 and the one-time Dust refund TreeFortMig; tools/trees_0_3_23_patch.py; with SkyySkills 0.4.50 +
SkyySacks 0.8.21). Extends the 0.3.22 harness (its emblem phase runs again here). Build first:
    python tools/trees_0_3_23_patch.py && python SkyyTrees/build_skyytrees_0.3.23.py
    python SkyyTrees/test_skyytrees_0.3.23.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in tools/dev/scratch/fort-f1/tr):
  A    verify   every class loads + initialises
  C    compare  0.3.22 -> 0.3.23: exactly the planned members (EXPECT) + TreeMig323 + TreeFortMig
  OLD  the 0.3.22 jar's node tables (D_MAX / D_PER / D_B / D_TOK / NAME / NOW / HOW / READERS / KIND) and DEFAULTS, saved for F23
  X    (0.3.22's emblem phase, unchanged)
  F23  EXECUTED: N  the two nodes' numbers + texts, every other node field for field as 0.3.22, DEFAULTS = 0.3.22's with only the 4 value
                    lines + the marker comment line changed; valueText / value at levels 0-10 (and 15 = the max); the bridges
                    (skill:bonus dd.mining = level x 0.1 posted map, tree:fn:bonus "Smithing.SSmelt" / "Mining.MFortune" on a stand-in
                    profile file, capped at the max; READERS of SSmelt)
                 MG TreeMig323's text step (old defaults LF / CRLF / spaced numbers, missing final newline, one node hand-edited
                    keeps BOTH its lines, the other node still moves, doubled / continued line, missing lines, already new, marker =
                    runs once, marker inside a value does not count, sameAfter refuses an added key)
                 RF TreeFortMig on scratch player files: CFGOK false = waits; above the max = the Dust of the levels above it as that
                    tree's credit (exact B x n^3 sums, an existing credit kept), levels kept saved, eff = the max, History copy = the
                    old bytes, one log line with Undo, marker; re-read of the saved file = no second refund; at / below the max =
                    marker only, nothing else; a missing file = marked; an admin max of 20 = no refund; a History copy that cannot be
                    made = nothing changes; balance (spent - credit) = what a max-level node costs; bytecode wiring
  RB/RU  (critic L1) the 0.3.22 jar reads + saves a refunded file (fort.r323 dropped, credit + Class.SkyyFortune.paid323 kept), then
       0.3.23 reads it again: no second refund; a ledger 1000 short pays exactly 1000
  ST1/ST2  start twice on a scratch COPY of the live Skyy_SkyyTrees folder (setup's order: TreeCfg.load, the one-time updates): start 1
       writes ONLY the 0.3.23 Fortune update (4 values + marker, a History version, 4 Undo lines) when the live lines hold the old
       defaults, then reads EVERY live player file through readFile (the refund report; nothing above 10 expected); start 2 writes
       nothing; the live folder is only read
  AA   engine-access audit
"""
import os, sys, re, json, shutil, hashlib, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import deploy_set as DS

VERSION = "0.3.23"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.3.22.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "fort-f1", "tr")))
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyTrees")
MK323 = "skyytrees-0.3.23-fortune"
ADDED = ["TreeFortMig", "TreeMig323"]
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],     # the version texts
          "SkyyTreesPlugin": ["~m setup"],                                     # TreeMig323.run + the version text
          "TreeCfg": ["~m load"],                                              # DEFAULTS (4 lines, a comment name, the marker line) + the version text
          "TreeMig": ["~<clinit>"],                                            # the 0.3 trees block for a pre-0.3 file carries the new Smithing numbers
          "TreeData": ["+f fort323", "+f fortPaid", "~c "],   # the constructor fills the new long[] fortPaid
          "TreeDefs": ["~<clinit>"],                                           # D_MAX / D_PER / NAME / NOW / HOW of the two nodes
          "TreeStore": ["~m readFile", "~m snap"]}                             # the refund + fort.r323=done
ADDED_NOTE = "TreeFortMig = the per-profile refund, TreeMig323 = the trees.properties update"
KEYS = {"Mining.MFortune.per": ("0.01", "0.1"), "Mining.MFortune.max": ("20", "10"),
        "Smithing.SSmelt.per": ("0.01", "0.1"), "Smithing.SSmelt.max": ("20", "10")}
B5 = 5   # both nodes' Dust B (slot 2 of the template)


def _load_prev():
    spec = importlib.util.spec_from_file_location("test_skyytrees_0_3_22", os.path.join(HERE, "test_skyytrees_0.3.22.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def tables(J):
    D, Cfg = J("TreeDefs"), J("TreeCfg")
    o = {}
    for f in ("D_MAX", "D_TOK", "KIND", "TIER"):
        o[f] = [int(x) for x in getattr(D, f)]
    o["D_B"] = [int(x) for x in D.D_B]
    o["D_PER"] = [float(x) for x in D.D_PER]
    for f in ("ID", "NAME", "ICON", "NOW", "HOW", "READERS", "KEY"):
        o[f] = [str(x) for x in getattr(D, f)]
    o["DEFAULTS"] = str(Cfg.DEFAULTS)
    return o


def run_old(out, _jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=True)
    t = tables(lambda n: JClass(PKG + n))
    json.dump(t, open(os.path.join(scratch, "old-tables.json"), "w"))
    K.check(t["NAME"][t["ID"].index("SSmelt")] == "Smelter's Luck", "OLD: the 0.3.22 tables were read (%d nodes)" % len(t["ID"]))
    K.save()


def _rb_snap(Sto, k):
    d = Sto.readFile(k)
    Sto.DATA.put(k, d)
    p = Sto.snap(k)
    Sto.DATA.remove(k)
    return dict((str(x), str(p.getProperty(x))) for x in p.stringPropertyNames())


# RB (critic L1): ROLL BACK - the 0.3.22 jar reads + saves the file 0.3.23 saved after a refund (fort.r323 dropped, the credit and the paid
# line kept); RU: RE-UPGRADE - 0.3.23 reads that file: no second refund
def run_rb(out, _jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=True)
    Sto = JClass(PKG + "TreeStore")
    pd = os.path.join(scratch, "rb", "players")
    shutil.rmtree(os.path.join(scratch, "rb"), ignore_errors=True)
    os.makedirs(pd)
    shutil.copy(os.path.join(scratch, "rf-pa-0323.properties"), os.path.join(pd, "pa.properties"))
    Sto.DIR = JClass("java.nio.file.Paths").get(pd)
    o = _rb_snap(Sto, "pa")
    K.check("fort.r323" not in o and o.get("Class.SkyyFortune.paid323") and o.get("Mining.dustCredit") and o.get("Mining.MFortune") == "15",
            "RB: 0.3.22 saves the file without fort.r323 but KEEPS Class.SkyyFortune.paid323 + the credit + the levels (%s)" % sorted(o.items())[:12])
    open(os.path.join(pd, "pa.properties"), "w", encoding="latin-1", newline="\n").write("".join("%s=%s\n" % kv for kv in sorted(o.items())))
    shutil.copy(os.path.join(pd, "pa.properties"), os.path.join(scratch, "rb-pa-0322.properties"))
    K.save()


def run_ru(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Sto, FM, Defs = JClass(PKG + "TreeStore"), JClass(PKG + "TreeFortMig"), JClass(PKG + "TreeDefs")
    ids = [str(x) for x in Defs.ID]
    TM, TS = ids.index("MFortune") // 12, ids.index("SSmelt") // 12
    pd = os.path.join(scratch, "ru", "players")
    shutil.rmtree(os.path.join(scratch, "ru"), ignore_errors=True)
    os.makedirs(pd)
    shutil.copy(os.path.join(scratch, "rb-pa-0322.properties"), os.path.join(pd, "pa.properties"))
    Sto.DIR = JClass("java.nio.file.Paths").get(pd)
    FM.CFGOK = True
    before = open(os.path.join(pd, "pa.properties"), encoding="latin-1").read()
    cr = dict(l.split("=", 1) for l in before.split("\n") if "=" in l)
    d = Sto.readFile("pa")
    K.check(bool(d.fort323) and str(int(d.credit[TM])) == cr["Mining.dustCredit"] and str(int(d.credit[TS])) == cr["Smithing.dustCredit"]
            and not os.path.exists(os.path.join(scratch, "ru", "fortune323-changes.log")),
            "RU: re-upgrade after the rollback - no second refund (credits stay %s / %s), the marker comes back, no refund log line" % (int(d.credit[TM]), int(d.credit[TS])))
    o = _rb_snap(Sto, "pa")
    K.check(o.get("fort.r323") == "done" and o.get("Class.SkyyFortune.paid323") == cr["Class.SkyyFortune.paid323"], "RU: the next save has the marker + the same paid line")
    # a partial ledger (paid less than owed): only the difference is paid
    lines = [l for l in before.split("\n") if l and not l.startswith("Class.SkyyFortune.paid323=")]
    paid = [int(x) for x in cr["Class.SkyyFortune.paid323"].split(",")]
    part = list(paid)
    part[TM] = paid[TM] - 1000
    open(os.path.join(pd, "pq.properties"), "w", encoding="latin-1", newline="\n").write("\n".join(lines + ["Class.SkyyFortune.paid323=" + ",".join(str(x) for x in part)]) + "\n")
    d = Sto.readFile("pq")
    K.check(int(d.credit[TM]) == int(cr["Mining.dustCredit"]) + 1000 and int(d.credit[TS]) == int(cr["Smithing.dustCredit"]) and int(d.fortPaid[TM]) == paid[TM],
            "RU: a ledger 1000 short pays exactly the 1000 still owed (Mining), nothing on Smithing")
    K.save()


def run_x(out, jar, scratch, home):
    _load_prev().run_exec(out, jar, scratch, home)


def run_f23(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JString, JDouble
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, Defs, Fx, Sto, Calc, FM, Mig, Dat = (J("TreeCfg"), J("TreeDefs"), J("TreeFx"), J("TreeStore"), J("TreeCalc"), J("TreeFortMig"),
                                              J("TreeMig323"), J("TreeData"))
    UUID = JClass("java.util.UUID")
    ids = [str(x) for x in Defs.ID]
    IM, IS = ids.index("MFortune"), ids.index("SSmelt")
    TM, TS = IM // 12, IS // 12
    trees = [str(x) for x in Defs.TREES]
    K.eq((trees[TM], trees[TS]), ("Mining", "Smithing"), "F23 N: MFortune is a Mining node, SSmelt a Smithing node")
    # ---- N. numbers + texts; nothing else changed
    new = tables(J)
    old = json.load(open(os.path.join(scratch, "old-tables.json")))
    K.eq([(new["D_MAX"][i], new["D_PER"][i]) for i in (IM, IS)], [(10, 0.1), (10, 0.1)], "F23 N: both nodes +10% a level, max 10")
    K.eq([(int(Cfg.MAX[i]), float(Cfg.PER[i])) for i in (IM, IS)], [(10, 0.1), (10, 0.1)], "F23 N: TreeCfg's built-in MAX / PER")
    K.eq([(new["D_TOK"][i], new["D_B"][i], new["TIER"][i], new["KIND"][i], new["ICON"][i]) for i in (IM, IS)],
         [(old["D_TOK"][i], old["D_B"][i], old["TIER"][i], old["KIND"][i], old["ICON"][i]) for i in (IM, IS)], "F23 N: tokens / B / tier / kind / icon unchanged")
    K.eq([new["D_B"][i] for i in (IM, IS)], [B5, B5], "F23 N: B = 5 for both (the refund maths below)")
    K.eq([new["NAME"][IM], new["NAME"][IS]], ["Mining Fortune", "Smelting Fortune"], "F23 N: names (Smelter's Luck -> Smelting Fortune)")
    K.eq([new["NOW"][IM], new["NOW"][IS]], ["+%V Mining Fortune (100% = one sure extra drop)", "+%V Smelting Fortune - extra bars when you smelt in /craft Furnace"],
         "F23 N: the Now texts")
    K.check("no total cap" in new["HOW"][IM] and "SkyySkills 0.4.50" in new["HOW"][IM] and "/craft Furnace" in new["HOW"][IS] and "SkyySacks" in new["HOW"][IS],
            "F23 N: the How texts (%s | %s)" % (new["HOW"][IM], new["HOW"][IS]))
    diff = [(f, i) for f in ("D_MAX", "D_TOK", "D_B", "D_PER", "KIND", "TIER", "ID", "NAME", "ICON", "NOW", "HOW", "READERS", "KEY")
            for i in range(len(new["ID"])) if new[f][i] != old[f][i] and not (i in (IM, IS) and f in ("D_MAX", "D_PER", "NAME", "NOW", "HOW"))]
    K.check(len(new["ID"]) == len(old["ID"]) == 108 and not diff, "F23 N: every other node field for field as 0.3.22 (%s)" % diff[:6])
    K.eq(new["READERS"][IS], "SkyySkills,SkyySacks", "F23 N: SSmelt is still lit by SkyySacks (or SkyySkills) listing it in tree:reads")
    ol, nl = old["DEFAULTS"].split("\n"), new["DEFAULTS"].split("\n")
    mk = [l for l in nl if MK323 in l]
    nl2 = [l for l in nl if MK323 not in l]
    chg = [(a, b) for a, b in zip(ol, nl2) if a != b]
    want = [("# Smithing S2 Smelter's Luck (tier I)", "# Smithing S2 Smelting Fortune (tier I)")]
    for k_, (o_, n_) in KEYS.items():
        want.append((k_ + "=" + o_, k_ + "=" + n_))
    hd = [(a, b) for a, b in chg if a.startswith("# SkyyTrees 0.3.22 - ")]
    K.check(len(hd) == 1 and hd[0][1] == hd[0][0].replace("0.3.22", "0.3.23"), "F23 N: the default file's version header line")
    chg = [x for x in chg if x not in hd]
    K.check(len(mk) == 1 and mk[0].startswith("# ") and len(ol) == len(nl2) and sorted(chg) == sorted(want)
            ,
            "F23 N: DEFAULTS = 0.3.22's with only the 4 value lines + the SSmelt comment name changed + 1 marker comment line (%s)" % (chg[:7],))
    # valueText / value
    K.eq([str(Defs.valueText(IM, Fx.value(IM, lv))) for lv in (0, 1, 3, 5, 10)], ["0%", "10%", "30%", "50%", "100%"], "F23 N: Mining Fortune shows 0 / 10 / 30 / 50 / 100%")
    K.eq([str(Defs.valueText(IS, Fx.value(IS, lv))) for lv in (1, 7, 10)], ["10%", "70%", "100%"], "F23 N: Smelting Fortune shows 10 / 70 / 100%")
    # the posted skill:bonus map (dd.mining = MFortune's value; the trees source)
    v = JArray(JDouble)([0.0] * len(ids))
    v[IM] = float(Fx.value(IM, 10))
    m = Fx.bonusMap(v)
    K.check(abs(float(m.get("dd.mining")) - 1.0) < 1e-9 and m.size() == 1, "F23 N: skill:bonus dd.mining at level 10 = 1.0 (+100%%, one sure extra drop): %s" % m)
    v[IM] = float(Fx.value(IM, 3))
    K.check(abs(float(Fx.bonusMap(v).get("dd.mining")) - 0.3) < 1e-9, "F23 N: dd.mining at level 3 = 0.3")
    K.eq(str(Fx.SRC), "trees", "F23 N: the skill:bonus source stays \"trees\"")
    # ---- scratch player store
    pd = os.path.join(scratch, "rf", "players")
    shutil.rmtree(os.path.join(scratch, "rf"), ignore_errors=True)
    os.makedirs(pd)
    Paths = JClass("java.nio.file.Paths")
    Sto.DIR = Paths.get(pd)

    def wr(k, lines):
        b = ("\n".join(lines) + "\n").encode("latin-1")
        open(os.path.join(pd, k + ".properties"), "wb").write(b)
        return b

    def props(k):
        t = open(os.path.join(pd, k + ".properties"), "rb").read().decode("latin-1")
        return dict(l.split("=", 1) for l in t.replace("\r\n", "\n").split("\n") if l and not l.startswith("#") and "=" in l)

    def save(k, d):
        Sto.DATA.put(k, d)
        p = Sto.snap(k)
        Sto.DATA.remove(k)
        lines = ["%s=%s" % (str(x), str(p.getProperty(x))) for x in sorted(str(y) for y in p.stringPropertyNames())]
        wr(k, lines)

    hist = os.path.join(scratch, "rf", "history", "fortune323")
    logf = os.path.join(scratch, "rf", "fortune323-changes.log")
    cube = lambda a, b: sum(B5 * n ** 3 for n in range(a, b))
    # ---- RF a: CFGOK false = waits
    FM.CFGOK = False
    wr("pa", ["v=2", "Mining.MFortune=15", "Mining.MWisdom=3", "Smithing.SSmelt=12", "Mining.dustCredit=100"])
    d = Sto.readFile("pa")
    K.check(not bool(d.fort323) and int(d.credit[TM]) == 100 and int(d.credit[TS]) == 0 and not bool(d.mig) and not os.path.exists(hist),
            "F23 RF: before this start's trees.properties update ran (CFGOK false) nothing happens - no credit, no marker, no copy")
    # ---- RF b: the refund
    FM.CFGOK = True
    oldb = open(os.path.join(pd, "pa.properties"), "rb").read()
    d = Sto.readFile("pa")
    rm, rs = cube(10, 15), cube(10, 12)
    K.eq((int(d.credit[TM]), int(d.credit[TS])), (100 + rm, rs), "F23 RF: Mining credit 100 + %d (levels 11-15), Smithing credit %d (levels 11-12)" % (rm, rs))
    K.eq((int(d.lv[IM]), int(d.lv[IS]), int(Calc.eff(d, IM)), int(Calc.eff(d, IS))), (15, 12, 10, 10), "F23 RF: the levels stay saved (15 / 12), only the max works (eff 10)")
    K.check(bool(d.fort323) and bool(d.mig), "F23 RF: marker set + the file is saved soon (mig)")
    hp = os.path.join(hist, "pa.properties")
    K.check(os.path.isfile(hp) and open(hp, "rb").read() == oldb, "F23 RF: the History copy holds the old bytes")
    log = open(logf, encoding="utf8").read().strip().split("\n") if os.path.isfile(logf) else []
    K.check(len(log) == 1 and "\tpa\trefund\t" in log[0] and "Mining.MFortune 15 (max 10)" in log[0] and "Smithing.SSmelt 12 (max 10)" in log[0]
            and "Undo:" in log[0], "F23 RF: one fortune323-changes.log line with both nodes + Undo (%s)" % (log[:1],))
    K.check(str(FM.LAST).startswith("pa: ") and int(FM.APPLIED) >= 1, "F23 RF: LAST / APPLIED")
    # balance: spent - credit (this node) = what a level-10 node costs
    sp_m = int(Calc.dustSpent(d, TM))
    K.eq(sp_m - (int(d.credit[TM]) - 100), cube(1, 10) + sum(int(Calc.cost(ids.index("MWisdom"), n)) for n in range(1, 3)),
         "F23 RF: Mining Dust spent minus the refund = a max-level Mining Fortune + the other node (the balance is as if bought to 10)")
    # save + re-read = no second refund
    save("pa", d)
    pr = props("pa")
    K.check(pr.get("fort.r323") == "done" and pr.get("Mining.dustCredit") == str(100 + rm) and pr.get("Smithing.dustCredit") == str(rs)
            and pr.get("Mining.MFortune") == "15" and pr.get("Smithing.SSmelt") == "12", "F23 RF: the saved file: marker + credits + levels (%s)" % pr)
    paid = ",".join(str(rm if t_ == TM else (rs if t_ == TS else 0)) for t_ in range(len(trees)))
    K.eq(pr.get("Class.SkyyFortune.paid323"), paid, "F23 RF: the saved file records the Dust refunded per tree (Class.SkyyFortune.paid323)")
    shutil.copy(os.path.join(pd, "pa.properties"), os.path.join(scratch, "rf-pa-0323.properties"))   # for the RB / RU phases
    d2 = Sto.readFile("pa")
    K.check(int(d2.credit[TM]) == 100 + rm and int(d2.credit[TS]) == rs and bool(d2.fort323) and not bool(d2.mig) and len(open(logf, encoding="utf8").read().strip().split("\n")) == 1,
            "F23 RF: re-reading the saved file refunds nothing again (runs once)")
    # ---- RF c: at / below the max = marker only
    wr("pb", ["v=2", "Mining.MFortune=10", "Smithing.SSmelt=4"])
    d = Sto.readFile("pb")
    K.check(bool(d.fort323) and not bool(d.mig) and int(d.credit[TM]) == 0 and int(d.credit[TS]) == 0 and not os.path.exists(os.path.join(hist, "pb.properties")),
            "F23 RF: at / below the max = the marker only (with the next save) - no credit, no copy, no forced save")
    save("pb", d)
    K.eq(props("pb").get("fort.r323"), "done", "F23 RF: ... and the next save writes fort.r323=done")
    # ---- RF d: missing file
    d = Sto.readFile("nobody")
    K.check(bool(d.fort323) and not bool(d.bad), "F23 RF: a new profile (no file) is marked - nothing to refund ever")
    # ---- RF e: marked file
    wr("pc", ["v=2", "Mining.MFortune=18", "fort.r323=done"])
    d = Sto.readFile("pc")
    K.check(bool(d.fort323) and int(d.credit[TM]) == 0 and not bool(d.mig), "F23 RF: a file with fort.r323=done is never refunded (an admin max raised later is the admin's call)")
    # ---- RF f: an admin max of 20
    mx = Cfg.MAX
    keep = int(mx[IM])
    mx[IM] = 20
    wr("pd", ["v=2", "Mining.MFortune=15"])
    d = Sto.readFile("pd")
    mx[IM] = keep
    K.check(bool(d.fort323) and int(d.credit[TM]) == 0 and not bool(d.mig), "F23 RF: an admin-kept max 20 = level 15 is not above it: marker, no refund")
    # ---- RF g: the History copy cannot be made
    os.makedirs(hist, exist_ok=True)
    os.makedirs(os.path.join(hist, "pe.properties"))   # a FOLDER where the copy goes
    wr("pe", ["v=2", "Smithing.SSmelt=20"])
    d = Sto.readFile("pe")
    K.check(not bool(d.fort323) and int(d.credit[TS]) == 0 and not bool(d.mig) and int(FM.SNAPFAILS) >= 1,
            "F23 RF: no History copy = nothing changes, the next read tries again (SNAPFAILS %d)" % int(FM.SNAPFAILS))
    shutil.rmtree(os.path.join(hist, "pe.properties"))
    d = Sto.readFile("pe")
    K.eq((int(d.credit[TS]), bool(d.fort323)), (cube(10, 20), True), "F23 RF: ... the next read (copy possible) refunds levels 11-20 = %d" % cube(10, 20))
    # ---- the pure pieces
    K.eq([int(FM.above(IM, lv)) for lv in (0, 9, 10, 11, 12, 20)], [0, 0, 0, B5 * 1000, B5 * (1000 + 1331), cube(10, 20)], "F23 RF: above() = B x n^3 for n = max .. lv - 1")
    # ---- bridges on a stand-in profile file (tree:fn:bonus; TreeStore.data -> readFile)
    u = UUID.fromString("00000000-0000-4000-8000-0000000000f1")
    Sto.bridge().remove("profile:fn:key")
    wr(str(u), ["v=2", "Smithing.SSmelt=7", "Mining.MFortune=15", "fort.r323=done"])
    Sto.DATA.remove(str(u))
    fn = J("TreeBonusFn")()
    a = lambda key: float(fn.apply(JArray(JObject)([u, JString(key)])))
    K.check(abs(a("Smithing.SSmelt") - 0.7) < 1e-9 and abs(a("Mining.MFortune") - 1.0) < 1e-9 and a("Smithing.SNope") == 0.0,
            "F23 BR: tree:fn:bonus {UUID, \"Smithing.SSmelt\"} = 0.7 at level 7; \"Mining.MFortune\" at saved 15 = 1.0 (the max); unknown = 0")
    Sto.DATA.remove(str(u))
    # ---- bytecode
    g = PW.calls(jar)
    K.check(PKG + "TreeFortMig.run" in g.get("TreeStore.readFile", set()), "F23 RF: readFile runs the refund (bytecode)")
    K.check(PKG + "TreeMig323.run" in g.get("SkyyTreesPlugin.setup", set()), "F23 MG: setup runs the trees.properties update (bytecode)")
    K.check({PKG + "TreeFortMig.snap", PKG + "TreeFortMig.plan"} <= g.get("TreeFortMig.run", set()) and PKG + "TreeAbMig.copyOnce" in g.get("TreeFortMig.snap", set()),
            "F23 RF: run -> plan + snap -> TreeAbMig.copyOnce (bytecode)")
    # ---- MG. TreeMig323's text step
    mk = str(Mig.MARK_LINE)

    def upd(t):
        r = Mig.m323Update(t)
        return None if r is None else [str(r[0]), [str(x) for x in r[1]], [str(x) for x in r[2]], [str(x) for x in r[3]]]
    base_t = ("# SkyyTrees\nMining.MSpeed.max=25\nMining.MFortune.max=20\nMining.MFortune.per=0.01\nMining.MFortune.B=5\n"
              "Smithing.SSmelt.max=20\nSmithing.SSmelt.per=0.01\nSmithing.SSmelt.tokens=1\n")
    want_t = base_t.replace("MFortune.max=20", "MFortune.max=10").replace("MFortune.per=0.01", "MFortune.per=0.1").replace(
        "SSmelt.max=20", "SSmelt.max=10").replace("SSmelt.per=0.01", "SSmelt.per=0.1")
    r = upd(base_t)
    K.check(r is not None and r[0] == want_t + mk + "\n" and len(r[1]) == 12 and sorted(r[3]) == sorted(KEYS) and r[2] == []
            and r[1][0:3] == ["nodes.Mining[MFortune.per]", "0.01", "0.1"], "MG323 LF: the 4 old defaults -> 0.1 / 10, the marker appended, every other byte kept (%s)" % (r[1] if r else r,))
    crlf = base_t.replace("\n", "\r\n")
    r = upd(crlf)
    K.check(r is not None and r[0] == want_t.replace("\n", "\r\n") + mk + "\r\n", "MG323 CRLF: line endings kept")
    sp = base_t.replace("MFortune.per=0.01", "MFortune.per=0.010").replace("SSmelt.max=20", "SSmelt.max=20.0")
    r = upd(sp)
    K.check(r is not None and len(r[3]) == 4 and "Mining.MFortune.per=0.1\n" in r[0] and "Smithing.SSmelt.max=10\n" in r[0], "MG323: the same number written differently counts as untouched")
    nofl = base_t.rstrip("\n")
    r = upd(nofl)
    K.check(r is not None and r[0] == want_t.rstrip("\n") + "\n" + mk + "\n", "MG323: a missing final newline is added first")
    ed = base_t.replace("MFortune.per=0.01", "MFortune.per=0.02")
    r = upd(ed)
    K.check(r is not None and "Mining.MFortune.per=0.02\n" in r[0] and "Mining.MFortune.max=20\n" in r[0] and "Smithing.SSmelt.per=0.1\n" in r[0]
            and "Smithing.SSmelt.max=10\n" in r[0] and sorted(r[3]) == ["Smithing.SSmelt.max", "Smithing.SSmelt.per"]
            and len(r[2]) == 2 and "an admin changed it" in r[2][0] and "another line of the same node" in r[2][1],
            "MG323: a hand-edited MFortune.per keeps BOTH MFortune lines (never 0.02 with max 10), SSmelt still moves, 2 notes (%s)" % (r[2] if r else r,))
    ed2 = base_t.replace("SSmelt.max=20", "SSmelt.max=15")
    r = upd(ed2)
    K.check(r is not None and "Smithing.SSmelt.max=15\n" in r[0] and "Smithing.SSmelt.per=0.01\n" in r[0] and sorted(r[3]) == ["Mining.MFortune.max", "Mining.MFortune.per"],
            "MG323: a hand-edited SSmelt.max keeps both SSmelt lines, MFortune moves")
    db = base_t + "Mining.MFortune.max=20\n"
    r = upd(db)
    K.check(r is not None and "Mining.MFortune.per=0.01\n" in r[0] and "Mining.MFortune.max" not in r[3] and "Mining.MFortune.per" not in r[3]
            and any("doubled" in x for x in r[2]), "MG323: a doubled line keeps its node and is noted")
    cont = base_t.replace("Mining.MFortune.per=0.01", "Mining.MFortune.per=0.0\\\n  1")
    r = upd(cont)
    K.check(r is not None and "Mining.MFortune.per" not in r[3] and any("continues" in x for x in r[2]), "MG323: a continued line keeps its node and is noted")
    miss = "# SkyyTrees\nMining.MSpeed.max=25\n"
    r = upd(miss)
    K.check(r is not None and r[0] == miss + mk + "\n" and r[1] == [] and r[2] == [], "MG323: no Fortune lines (the new built-in values) - the marker only")
    nw = want_t
    r = upd(nw)
    K.check(r is not None and r[0] == nw + mk + "\n" and r[1] == [] and r[2] == [], "MG323: already the new values - the marker only")
    half = base_t.replace("MFortune.per=0.01", "MFortune.per=0.1")
    r = upd(half)
    K.check(r is not None and "Mining.MFortune.max=10\n" in r[0] and r[2] == [], "MG323: one line already new + the other the old default = the node moves")
    K.check(upd(base_t + mk + "\n") is None and upd("# x " + MK323 + "\n" + base_t) is None, "MG323: the marker in a comment line = nothing to do (runs once)")
    K.check(upd(base_t + "x.y=" + MK323 + "\n") is not None, "MG323: the marker id inside a VALUE does not count")
    mv = JArray(JString)(list(KEYS))
    K.check(bool(Mig.sameAfter(base_t.encode("latin-1"), upd(base_t)[0].encode("latin-1"), mv))
            and not bool(Mig.sameAfter(base_t.encode("latin-1"), (upd(base_t)[0] + "extra=1\n").encode("latin-1"), mv))
            and not bool(Mig.sameAfter(base_t.encode("latin-1"), upd(base_t)[0].replace("MSpeed.max=25", "MSpeed.max=24").encode("latin-1"), mv)),
            "MG323: sameAfter - only the 4 keys may change (an added key / another changed value is refused)")
    K.eq([str(x) for x in Mig.TKEY], ["nodes.Mining[MFortune.per]", "nodes.Mining[MFortune.max]", "nodes.Smithing[SSmelt.per]", "nodes.Smithing[SSmelt.max]"],
         "MG323: the Undo keys are the Server Setup table cells")
    K.save()


def live_vals():
    f = os.path.join(LIVE, "trees.properties")
    if not os.path.isfile(f):
        return None
    t = open(f, "rb").read().decode("latin-1")
    if MK323 in t:
        return "marked"
    o = {}
    for l in t.replace("\r\n", "\n").split("\n"):
        k = l.split("=", 1)[0]
        if k in KEYS:
            o[k] = o.get(k, []) + [l.split("=", 1)[1].strip()]
    return o


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Sto, FM, Defs, Calc = JClass(PKG + "TreeCfg"), JClass(PKG + "TreeStore"), JClass(PKG + "TreeFortMig"), JClass(PKG + "TreeDefs"), JClass(PKG + "TreeCalc")
    Paths = JClass("java.nio.file.Paths")
    base = os.path.join(scratch, "st", "mods", "Skyy_SkyyTrees")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = tree_hash(base)
    f = [x for x in Cfg.class_.getDeclaredFields() if str(x.getName()) == "FILE"]
    if f:
        Cfg.FILE = Paths.get(os.path.join(base, "trees.properties"))
    Sto.DIR = Paths.get(os.path.join(base, "players"))
    lo, mg = None, {}
    try:
        lo = str(Cfg.load())
        bp = Paths.get(base)
        for m_ in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317", "TreeMig321", "TreeMig323"):   # setup()'s order
            mg[m_] = str(JClass(PKG + m_).run(bp))
    except Exception as e:
        lo = "load: %s" % e
    ids = [str(x) for x in Defs.ID]
    IM, IS = ids.index("MFortune"), ids.index("SSmelt")
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    lv = live_vals()
    K.check(bool(FM.CFGOK), "ST start %s: TreeMig323 ran / found its marker = the refunds may run (CFGOK)" % step)
    K.eq([(int(Cfg.MAX[i]), float(Cfg.PER[i])) for i in (IM, IS)], [(10, 0.1), (10, 0.1)], "ST start %s: the loaded numbers are 0.1 / 10 for both nodes" % step)
    if step == "1":
        okset = all(k in ("trees.properties", "config-changes.log") or k.startswith("config-history/") for k in ch)
        others = dict((k, v) for k, v in mg.items() if k != "TreeMig323" and v)
        if isinstance(lv, dict) and all(v == [KEYS[k][0]] for k, v in lv.items()) and len(lv) == 4:
            t = open(os.path.join(base, "trees.properties"), "rb").read().decode("latin-1")
            log = open(os.path.join(base, "config-changes.log"), encoding="utf8").read().split("\n")
            rows = [l.split("\t") for l in log if "\tSkyyTrees 0.3.23\t" in l]
            K.check(okset and "trees.properties" in ch and any(k.startswith("config-history/") for k in ch) and not others,
                    "ST start 1 on a scratch COPY of the live data: only the 0.3.23 Fortune update is written %s (others %s)" % (ch, others))
            tn = t.replace("\r\n", "\n")
            K.check(all(("\n%s=%s\n" % (k, n_)) in tn for k, (o_, n_) in KEYS.items()) and t.count(MK323) == 1,
                    "ST start 1: the 4 lines hold 0.1 / 10 + the marker")
            K.check(len(rows) == 4 and all(r_[2:4] == ["-", "update"] and r_[7] == "ok" for r_ in rows), "ST start 1: 4 Undo lines: %s" % [r_[4:7] for r_ in rows])
            ol = open(os.path.join(LIVE, "trees.properties"), "rb").read()
            nb = open(os.path.join(base, "trees.properties"), "rb").read()
            exp = ol
            for k, (o_, n_) in KEYS.items():
                assert exp.count(b"\n" + (k + "=" + o_).encode()) == 1
                exp = exp.replace(b"\n" + (k + "=" + o_).encode(), b"\n" + (k + "=" + n_).encode(), 1)
            eol = b"\r\n" if b"\r\n" in ol else b"\n"
            if not exp.endswith(b"\n"):
                exp += eol
            mline = [l for l in tn.split("\n") if MK323 in l][0].encode("latin-1")
            K.check(nb == exp + mline + eol, "ST start 1: the new file = the old bytes with only the 4 values changed + the marker line (the file's own line ending)")
            K.check("nodes.Mining[MFortune.per] 0.01 -> 0.1" in mg["TreeMig323"], "ST start 1: the INFO line (%s)" % mg["TreeMig323"][:200])
        else:
            K.check(okset and not others, "ST start 1: the live Fortune lines are %s (not all the old default) - only those + the marker may be written %s" % (lv, ch))
        # every live player file through readFile: the refund report
        pdir = os.path.join(base, "players")
        rep = []
        for fn in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
            if not fn.endswith(".properties"):
                continue
            k = fn[:-len(".properties")]
            d = Sto.readFile(k)
            rep.append((k[:8], int(d.lv[IM]), int(d.lv[IS]), bool(d.fort323), bool(d.bad), [int(x) for x in d.credit]))
        above = [r_ for r_ in rep if r_[1] > 10 or r_[2] > 10]
        K.check(rep and all(r_[3] and not r_[4] for r_ in rep), "ST start 1: every live player file reads + is marked: %s" % rep)
        K.check(not os.path.exists(os.path.join(base, "history", "fortune323")) if not above else os.path.isdir(os.path.join(base, "history", "fortune323")),
                "ST start 1: refunds on the live copy: %s (none expected - 2026-10-17 MFortune 2)" % (above or "none"))
        json.dump(rep, open(os.path.join(scratch, "st-players.json"), "w"))
        print("LIVE-COPY players (key, MFortune, SSmelt, marked, bad, credits): %s" % rep)
    else:
        K.check(bool(f) and not ch and mg.get("TreeMig323") == "", "ST start 2: nothing written %s (load %s)" % (ch, (lo or "")[:60]))
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
           phases=[("old", run_old), ("x", run_x), ("f23", run_f23), ("rb", run_rb), ("ru", run_ru), ("st1", run_st1), ("st2", run_st2)], script=__file__)
