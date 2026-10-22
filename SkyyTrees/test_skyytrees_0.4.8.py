"""Harness for SkyyTrees 0.4.8 (Balance P8d: the useful + light skill trees row by row - 10 node aliases, 13 own TreeSk rows, 9 dead aliases
dropped; tools/trees_0_4_8_patch.py + tools/trees_v3_data.py + tools/trees_v3_effects.py). Build first:
    python tools/trees_0_4_8_patch.py && python SkyyTrees/build_skyytrees_0.4.8.py
    python SkyyTrees/test_skyytrees_0.4.8.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S    static   the patch re-runs to identical bytes; line endings kept; no class / system / command added; the new texts in the jar
  A    verify   every class loads + initialises
  C    compare  0.4.7 -> 0.4.8: exactly the planned members (EXPECT)
  OLD  the 0.4.7 jar's TreeV3 / TreeSk tables (dumped in its own JVM)
  DATA vs 0.4.7: no upgrade max / cost / key / name / row / free perk changed; UHK 0 -> 2 on the 10 P8D_OLD upgrades and 2 -> 0 on the 9
       P8D_DROP ones, nothing else; the texts change exactly on P8D_OLD + P8D_TEXT; only the seven P8d trees' gates move, to the planned
       table; TreeSk = the 16 P8b rows unchanged + 13 P8d rows; the budgets (check())
  X    exec     a bare JVM with scratch players: every new own effect EXECUTED at max (TreeSk.sum: spd, fall, hpp, stam, dodge.acrobatics,
       xp.smithing, dd.farming; the TreeFx late bodies skSta / skHp; skBonus merges dodge / dd / xp; movePost); derive() turns the 10 aliases
       into their node levels; live(): own rows with tree:reads:SkyyTrees, Fishing aliases only with SkyyFishing's tree:reads, the 9 dropped
       upgrades coming soon (state 4); the Alchemy row 2 gate (0.4.7: 3 dead ranks below = never open) opens at 5 really spent points
  LIVE START TWICE on a scratch COPY of the live Skyy_SkyyTrees folder: 0.4.8 adds no one-time update; the old tree-effects.properties (16
       rows) reads, the 13 new rows keep their built-in numbers; every player file reads; start 2 changes nothing
  AA   engine-access audit
NOT COVERED (UNVERIFIED in game): the page look of the seven trees; SkyySkills applying dodge.acrobatics / dd.farming from the "trees"
source and skyytree_stamina on the stamina bar (unchanged paths, read by SkyySkills since 0.4.1 / 0.4.26).
"""
import os, sys, json, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "balp8d", "trees")]
import skyybuild as B
import harness_kit as HK
import trees_v3_data as V3D
import trees_v3_effects as V3E

_s = importlib.util.spec_from_file_location("test_skyytrees_0_4_6", os.path.join(HERE, "test_skyytrees_0.4.6.py"))
T46 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T46)
sys.argv[:] = _argv

VERSION = "0.4.8"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.4.7.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.4.7.py")
PATCH = os.path.join(TOOLS, "trees_0_4_8_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T46.LIVE_DIR
ADDED = []
EXPECT = {}
P8D_ROWS = [e for e in V3E.EFFECTS if e[3] == "SkyyTrees" and e[0] in V3E.P8D_TREES]
P8D_KEYS = [V3E.key(e[0], e[1], e[2]) for e in P8D_ROWS]
OLDK = sorted("Skill." + k for k in V3D.P8D_OLD)
DROPK = sorted("Skill." + k for k in V3D.P8D_DROP)
TEXTK = sorted(set("Skill." + k for k in V3D.P8D_TEXT) | set(OLDK))
GATES = {"Farming": [0, 5, 10, 15, 20, 25], "Cooking": [0, 5, 10, 15, 20, 25], "Alchemy": [0, 5, 9, 14, 14, 19], "Fishing": [0, 5, 7, 15],
         "Smithing": [0, 5, 7, 10], "Acrobatics": [0, 5, 10, 15], "Exploration": [0, 3, 5, 11]}
U1 = "55555555-5555-5555-5555-555555555555"   # every P8d row + alias at max
U2 = "66666666-6666-6666-6666-666666666666"   # Alchemy: 4 / 5 points spent in row 1
TABLES = T46.TABLES


def dump_all(JClass):
    o = T46.dump(JClass(PKG + "TreeV3"))
    S = JClass(PKG + "TreeSk")
    o["SKEY"] = [str(x) for x in S.KEY]
    o["SEFF"] = [str(x) for x in S.EFF]
    o["SPER"] = [round(float(S.v3per(i)), 9) for i in range(len(S.KEY))]
    return o


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.4.8 - build script') and g.count('VERSION = "0.4.8"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    import zipfile as _zf
    _jb = b"".join(_zf.ZipFile(jar).read(_n) for _n in _zf.ZipFile(jar).namelist() if _n.endswith((".class", ".properties", ".json")))
    for t in ("+2% dodge push/rank (Hytale has no dodge chance)", "one mid-air jump at 75% of your jump height (100% at rank 2)", "Acrobatics Combat Flip Dodge a rank",
              "Exploration Trail Mix Stamina a rank", "Farming Bumper Crop Fortune a rank"):
        K.check(t.encode() in _jb, "S in the jar: %s" % t)
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
    o = dump_all(JClass)
    json.dump(o, open(os.path.join(scratch, "old047.json"), "w"))
    K.check(len(o["UKEY"]) > 0 and len(o["SKEY"]) == 16, "OLD the 0.4.7 tables read (%d upgrades, %d own rows)" % (len(o["UKEY"]), len(o["SKEY"])))
    K.save()


def run_data(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    V = JClass(PKG + "TreeV3")
    o, n = json.load(open(os.path.join(scratch, "old047.json"))), dump_all(JClass)
    for t in ("UMAX", "UCOST", "UKEY", "UNAME", "UROW", "TU0", "TUN", "TNAME", "RNUM", "RFK", "RFNAME", "RFTEXT", "R3B"):
        K.eq(n[t], o[t], "DATA %s unchanged" % t)
    hk = sorted((n["UKEY"][i], o["UHK"][i], n["UHK"][i]) for i in range(len(n["UKEY"])) if n["UHK"][i] != o["UHK"][i])
    K.eq(hk, sorted([(k, 0, 2) for k in OLDK] + [(k, 2, 0) for k in DROPK]), "DATA UHK: 10 new node aliases (0 -> 2), 9 dead aliases dropped (2 -> 0)")
    txt = sorted(n["UKEY"][i] for i in range(len(n["UKEY"])) if n["UTEXT"][i] != o["UTEXT"][i])
    K.eq(txt, TEXTK, "DATA the texts change exactly on P8D_OLD + P8D_TEXT (%d)" % len(TEXTK))
    dt = {}
    for _t in V3D.TREES:
        for _bn, _b in enumerate(_t["branches"]):
            for _r in _b["rows"]:
                for _u in _r["ups"]:
                    dt["%s.%s.b%d.%s" % ("Class" if _t["kind"] == "class" else "Skill", _t["name"], _bn + 1, _u["id"])] = _u["text"]
    K.check(all(n["UTEXT"][n["UKEY"].index(k)] == dt[k] for k in TEXTK), "DATA every P8d text in the jar = tools/trees_v3_data.py")
    K.check(all(n["UTEXT"][n["UKEY"].index(k)] == o["UTEXT"][o["UKEY"].index(k)] for k in DROPK if k != "Skill.Smithing.b1.r1a"),
            "DATA the 8 dropped (now coming soon) upgrades keep their plan text")
    moved, got = [], {}
    for tv in range(len(n["TNAME"])):
        nm = n["TNAME"][tv]
        for r in range(8):
            if o["GATES"][tv * 8 + r] != n["GATES"][tv * 8 + r]:
                moved.append(nm)
        if nm in GATES:
            got[nm] = [n["GATES"][tv * 8 + r] for r in range(1, len(GATES[nm]) + 1)]
    K.check(set(moved) == set(V3E.P8D_TREES) - {"Cooking"}, "DATA only the P8d trees' gates move: %s" % sorted(set(moved)))
    K.eq(got, GATES, "DATA the P8d gate table (Alchemy / Smithing / Fishing reachable now)")
    K.eq(n["SKEY"][:16], o["SKEY"], "DATA TreeSk: the 16 P8b rows unchanged (same index = same Server Setup field)")
    K.eq((n["SEFF"][:16], n["SPER"][:16]), (o["SEFF"], o["SPER"]), "DATA TreeSk: the P8b effects / numbers unchanged")
    K.eq((n["SKEY"][16:], n["SEFF"][16:], n["SPER"][16:]), (P8D_KEYS, [e[4] for e in P8D_ROWS], [round(e[5], 9) for e in P8D_ROWS]), "DATA TreeSk: + the 13 P8d rows")
    K.check(str(JClass(PKG + "TreeSk").READS) == V3E.reads_csv("SkyyTrees"), "DATA tree:reads:SkyyTrees = the 29 keys")
    K.check(bool(V3E.check()), "DATA trees_v3_effects.check(): " + "; ".join("%s %.1f / %.1f / %g / %.1f" % (t, 100 * V3E.tree_fort(t.lower()), 100 * V3E.tree_xp(t),
            V3E.tree_move(t), 100 * V3E.tree_hp(t)) for t in V3E.P8D_TREES))
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString, JImplements, JOverride
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
    K.check(open(ef, encoding="latin-1").read() == V3E.cfg_text("SkyyTrees") and "read" in r0, "X loadV3 seeds tree-effects.properties with the 29 rows: %s" % r0)
    br = St.bridge()

    @JImplements("java.util.function.Function")
    class Lv(object):
        @JOverride
        def apply(self, a):
            return JClass("java.lang.Integer")(60)
    br.put("skill:fn:level", Lv())
    ui = dict((str(V.UKEY[i]), i) for i in range(len(V.UKEY)))
    lk = lambda k: bool(V.live(ui[k]))
    K.check(not any(lk(k) for k in P8D_KEYS), "X without tree:reads:SkyyTrees the 13 own rows are not live")
    S.reads(True)
    K.check(all(lk(k) for k in P8D_KEYS), "X with tree:reads:SkyyTrees the 13 own rows are live")
    fish = [k for k in OLDK if k.startswith("Skill.Fishing.")]
    K.check(all(lk(k) for k in OLDK if k not in fish) and not any(lk(k) for k in fish),
            "X the Farming / Cooking / Alchemy aliases are live (SkyyTrees / SkyyCooking nodes); the Fishing ones wait for SkyyFishing")
    br.put("tree:reads:SkyyFishing", JString(V3E.reads_csv("SkyyFishing")))
    K.check(all(lk(k) for k in fish), "X with SkyyFishing 0.1.12's tree:reads (NBite / NFortune / NTreasure) Rod Tempering + Gear Resonance are live")
    br.put("tree:reads:SkyySkills", JString(V3E.reads_csv("SkyySkills")))
    br.put("tree:reads:SkyyGear", JString(V3E.reads_csv("SkyyGear")))
    K.check(not any(lk(k) for k in DROPK if k not in P8D_KEYS) and lk("Skill.Smithing.b1.r1a"),
            "X the 8 dropped aliases are coming soon even with SkyySkills / SkyyGear / SkyyFishing listed; Steady Strikes is live (Smithing XP)")
    full = {}
    for k in P8D_KEYS + OLDK:
        t, b, i = k.split(".")[1:]
        full[k] = V3E.maxrank(t, int(b[1:]), i)
    T46._pfile(d, U1, full)
    u1 = UUID.fromString(U1)
    data = St.data(u1)
    K.check(not bool(data.bad), "X the full P8d player file reads")
    V.derive(data)
    exp = {"spd": 9.0, "fall": 0.06 + 0.06 + 0.10, "hpp": 0.03 + 0.03, "stam": 0.9, "dodge.acrobatics": 0.12, "xp.smithing": 0.08, "dd.farming": 0.027}
    got = dict((k, round(float(S.sum(u1, k)), 9)) for k in exp)
    K.eq(got, dict((k, round(v, 9)) for k, v in exp.items()), "X every P8d own effect at max EXECUTED (TreeSk.sum)")
    K.eq((round(float(Fx.skSta(u1)), 9), round(float(Fx.skHp(u1)), 9)), (0.9, 6.0), "X TreeFx.skSta (new late body) = +0.9 Stamina, skHp = +6 % max Health")
    m = JClass("java.util.HashMap")()
    m.put("dd.farming", JClass("java.lang.Double")(0.1))
    Fx.skBonus(u1, m)
    K.eq((round(float(m.get("dd.farming")), 9), round(float(m.get("xp.smithing")), 9), round(float(m.get("dodge.acrobatics")), 9)), (0.127, 0.08, 0.12),
         "X skBonus merges Bumper Crop into dd.farming (0.1 + 0.027), Steady Strikes xp.smithing, Combat Flip + Evade Master dodge.acrobatics")
    lv = lambda n: int(data.lv[int(D.idx(n))])
    K.eq(dict((n, lv(n)) for n in ("Farming.ASeeds", "Cooking.CGourmet", "Cooking.CGourmet2", "Cooking.CSig", "Farming.AHerbs", "Fishing.NBite", "Fishing.NFortune")),
         {"Farming.ASeeds": 7, "Cooking.CGourmet": 9, "Cooking.CGourmet2": 6, "Cooking.CSig": 3, "Farming.AHerbs": 12, "Fishing.NBite": 8, "Fishing.NFortune": 6},
         "X derive: the 10 aliases -> their node levels (Auto-Seed 4 + Rare Seed 3, Long Simmer 6 + Fresh Catch 3, Spice Rack 6, Chef's Kiss 3, Herb Eye + Trained Hands 12, Rod Tempering 8, Gear Resonance 6)")
    S.movePost(u1)
    mv = br.get("move:" + U1)
    e = mv.get("trees.skills") if mv is not None else None
    K.check(e is not None and abs(float(e.get("speed")) - 0.09) < 1e-6 and abs(float(e.get("fallDamage")) + 0.22) < 1e-6,
            "X movePost: trees.skills speed +0.09 (Quick Scythe 3 + Gear Resonance 3 + Adrenaline 3), fallDamage -0.22 (Steady Land 6 + Fearless 6 + Safe Landing 10): %s" % e)
    sr = lambda k: int(V.skillRank(u1, k))
    K.eq((sr("Skill.Acrobatics.b1.r3b"), sr("Skill.Exploration.b1.r1b"), sr("Skill.Farming.b1.r4b")), (3, 3, 3), "X tree:fn:level answers the own rows")
    # Alchemy: row 2 opens at 5 points really spent (0.4.7: gate 3 behind 3 never-buyable Extended Vial ranks)
    tva = [t for t in range(len(V.TNAME)) if str(V.TNAME[t]) == "Alchemy"][0]
    g = V.gates(tva)
    th = ui["Skill.Alchemy.b2.r2a"]
    T46._pfile(d, U2, {"Skill.Alchemy.b2.r1a": 3, "Skill.Alchemy.b3.r1a": 1})
    u2 = UUID.fromString(U2)
    d2 = St.data(u2)
    K.eq((int(V.spent(d2, tva)), int(g[2]), int(V.ustate(d2, th, 60, int(V.spent(d2, tva)), g))), (4, 5, 0), "X Alchemy 4 points spent: Trained Hands (row 2, gate 5) locked")
    T46._pfile(d, U2, {"Skill.Alchemy.b2.r1a": 3, "Skill.Alchemy.b3.r1a": 2})
    St.DATA.remove(St.pkey(u2))
    d2 = St.data(u2)
    K.eq(int(V.ustate(d2, th, 60, int(V.spent(d2, tva)), g)), 1, "X Alchemy 5 points spent (Herb Eye 3 + Resist Tonic 2): Trained Hands buyable")
    K.eq(int(V.ustate(d2, ui["Skill.Alchemy.b1.r1b"], 60, 5, g)), 4, "X Extended Vial (the dropped dead alias) shows coming soon (state 4)")
    K.eq(round(float(S.sum(u2, "hpp")), 9), 0.02, "X Resist Tonic 2 = +2 % max Health")
    # Server Setup numbers: Trail Mix's per rank / ceiling fields apply at once
    i_t = [i for i in range(len(S.EFF)) if str(S.KEY[i]) == "Skill.Exploration.b1.r1b"][0]
    setattr(S, "V3X%d" % i_t, 100.0)
    setattr(S, "V3P%d" % i_t, 0.5)
    K.eq(round(float(S.sum(u1, "stam")), 6), 1.5, "X Trail Mix per rank 0.3 -> 0.5 + ceiling 100 (Server Setup fields) -> 1.5 Stamina")
    setattr(S, "V3X%d" % i_t, 1.0)
    K.eq(round(float(S.sum(u1, "stam")), 6), 1.0, "X its ceiling 1 -> 1.0")
    S.loadV3(Paths.get(d))
    K.eq(round(float(S.sum(u1, "stam")), 6), 0.9, "X loadV3 of the file puts the built-in numbers back")
    K.save()


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    from jpype import JClass
    fp = os.path.join(home, "trees.properties")
    ef = os.path.join(home, "tree-effects.properties")
    t0 = open(fp, "rb").read()
    e0 = open(ef, "rb").read() if os.path.exists(ef) else None
    msgs, bad = T46.live_start(home)
    print("   live start 1:", [m[:80] for m in msgs if m])
    po, pn = T46._props(t0), T46._props(open(fp, "rb").read())
    dk = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    K.check(dk in ([], ["Mining.MFortune.per"]), "LIVE start 1: trees.properties changes at most 0.4.5's own TreeMigP5 line: %s" % dk)
    K.check(e0 is None or open(ef, "rb").read() == e0, "LIVE the live tree-effects.properties is read, never rewritten")
    S = JClass(PKG + "TreeSk")
    K.check(all(abs(float(S.v3per(16 + i)) - P8D_ROWS[i][5]) < 1e-9 for i in range(len(P8D_ROWS))),
            "LIVE the 13 P8d rows (not in the live file) keep their built-in numbers")
    K.eq(bad, [], "LIVE every player file reads")
    h1 = T46.tree_hash(home)
    msgs2, bad2 = T46.live_start(home)
    K.check(T46.tree_hash(home) == h1 and bad2 == [], "LIVE start 2 changes nothing")
    K.save()


EXPECT.update({   # checked by hand 2026-10-22: the version texts (CfgFn / CfgRows / setup's ready line / TreeCfg.load's header), CfgFile's default
                 # tree-effects.properties text, TreeV3's tables (gates, hooks, texts in <clinit>), TreeFx's new skSta + its call in stats(), TreeSk's
                 # 13 new rows (fields, tables, v3per / v3most / loadV3 branches, the READS constant inlined in reads(), addBonus + dodge.)
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup"], "TreeCfg": ["~m load"],
    "TreeFx": ["+m skSta", "~m stats"], "TreeV3": ["~<clinit>"],
    "TreeSk": ["+f V3P16", "+f V3P17", "+f V3P18", "+f V3P19", "+f V3P20", "+f V3P21", "+f V3P22", "+f V3P23", "+f V3P24", "+f V3P25", "+f V3P26", "+f V3P27", "+f V3P28", "+f V3X16", "+f V3X17", "+f V3X18", "+f V3X19", "+f V3X20", "+f V3X21", "+f V3X22", "+f V3X23", "+f V3X24", "+f V3X25", "+f V3X26", "+f V3X27", "+f V3X28", "~<clinit>", "~m addBonus", "~m loadV3", "~m reads", "~m v3most", "~m v3per"]})

if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("old", run_old), ("data", run_data), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyTrees"))
