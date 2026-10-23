"""Harness for SkyyTrees 0.5.2 (MOTHERLODE JACKPOT, ROW GATES, HARVEST SWING SPEED, OWN NODE ICONS + THE PLAN TEXT SWEEP; tools/trees_0_5_2_patch.py
+ tools/trees_v3_data.py P052_TEXT). Build first:
    python tools/trees_0_5_2_patch.py && python SkyyTrees/build_skyytrees_0.5.2.py
    python SkyyTrees/test_skyytrees_0.5.2.py [--keep]
Phases (each its own child JVM, -Xverify:all where classes run; the kit's verify / class compare / engine-access audit around them):
  static  the generated script = the patch's output (re-run to identical bytes), its header / version, no new system or command, one new class
  jar     vs 0.5.1: every map picture byte-identical, only the manifest + the page data changed; the NEW files are exactly the 684 icon items
          (JSON shape + PNG = the art files byte for byte), server.lang, the 40 harvest tier effects, the harvest steps and the 2 sickle selector
          overrides (= vanilla but Next); the harvest tree walked for every tier on a crop / not on a crop; every map node shows an own icon
  old / data  the TreeV3 tables vs 0.5.1: only UTEXT (exactly the P052 texts), UIC / RFIC (own icons) change
  exec51  the whole 0.5.1 EXEC phase on the 0.5.2 jar (GOLD pictures + lines, every bound event = ONE page packet, the KEEP mode: a zoomed
          talent click / Learn / Respec = ONE sendUpdate)
  new     EXECUTED: Motherlode (TreeFx value 3 % at 3 ranks, jackpot() = 2 fresh rolls + the "Motherlode jackpot" word, the panel texts, the
          TreeMig052 text step); ROW GATES (locked by the row above / opened by one more point / rows.needAbove 0 / a small row above / class
          trees untouched / the one-time rows52 update: kept rows, bytes + line endings kept, History copy, run once / respec + rebirth end
          it / the respec History keeps it); HARVEST (Quick Scythe = swing.farming not move speed, the tier sum with SkyyGear's
          gear:swing:harvest + accessories, gear:perk:readers, the .swing / .spd config keys); ICONS (every upgrade / free perk its own id,
          the map page data = UIC / RFIC node by node)
  live    start twice on a scratch COPY of the live Skyy_SkyyTrees folder: start 1 = the MVeins line (+ marker) and rows52 per player file,
          nothing else; start 2 changes nothing; every player x layout map painted with shipped pictures
NOT COVERED (UNVERIFIED in game): the shortened sickle pad in the client (animation / prediction), the BlockCondition latest target while a
sickle sweeps, the icons' look at 18 / 12 px, SkyyGear 0.3.42's gear:swing:harvest key in a live server (stubbed here).
"""
import os, sys, json, subprocess, importlib.util, zipfile, re, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "trees052", "h")]
import skyybuild as B
import harness_kit as HK

_s = importlib.util.spec_from_file_location("test_skyytrees_0_5_1", os.path.join(HERE, "test_skyytrees_0.5.1.py"))
T51 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T51)
sys.argv[:] = _argv
T46 = T51.T46

VERSION = "0.5.2"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.5.1.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.5.1.py")
PATCH = os.path.join(TOOLS, "trees_0_5_2_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T46.LIVE_DIR
ADDED = ["TreeMig052"]
EXPECT = {}
TABLES = tuple(T46.TABLES) + ("UIC", "RFIC")
MAPRES = "com/skyy/trees/map/"
MAPDIR = "Common/UI/Custom/SkyyTrees/Map/"
NL, ZN = 11, 3
SEL = ["Server/Item/Interactions/Weapons/Sickle/Attacks/Swing_%s/Sickle_Swing_%s_Selector.json" % (s, s) for s in ("Left", "Right")]
U5 = "52525252-0000-0000-0000-000000000005"   # Motherlode 3
U6 = "52525252-0000-0000-0000-000000000006"   # Mining: 8 points in row 1, 2 in row 2 (row 3: total met, row above not)
U7 = "52525252-0000-0000-0000-000000000007"   # the same, a v=3 file without rows52 (the one-time update keeps row 3)
U8 = "52525252-0000-0000-0000-000000000008"   # the same with CRLF line endings
U9 = "52525252-0000-0000-0000-000000000009"   # rows that already meet the rule (only rows52=1 is appended)
U10 = "52525252-0000-0000-0000-000000000010"  # Quick Scythe 3
U11 = "52525252-0000-0000-0000-000000000011"  # fix round: rows52 while rows.needAbove = 0 still keeps the open row
U12 = "52525252-0000-0000-0000-000000000012"  # fix round: rows52 on a CRLF file with no final line ending


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.5.2 - build script') and g.count('VERSION = "0.5.2"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("makeClass(") - o.count("makeClass("), 1, "S one class added (TreeMig052)")
    K.check(g.count("V3D.p052_apply()") == 1 and "p052_apply" not in o, "S the 0.5.2 texts are applied by this build only")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    import trees_v3_data as V3D
    n0 = dict((k, v) for k, v in V3D.P052_TEXT_OLD.items())
    V3D.p052_apply()
    V3D.p052_apply()   # once only
    K.check(len(V3D.P052_TEXT) == 43 and len(V3D.P052_APPLIED) == 1 and set(n0) == set(V3D.P052_TEXT), "S P052: 2 decision texts + 41 sweep texts, applied once")
    K.save()


def _icon_art():
    """icon id -> the art file bytes (art/tree-node-icons + the row abilities' art/ability-icons pictures)"""
    m = json.load(open(os.path.join(ROOT, "art", "tree-node-icons", "manifest.json"), encoding="utf8"))
    c = json.load(open(os.path.join(ROOT, "art", "tree-node-icons", "manifest-classes.json"), encoding="utf8"))
    out = {}
    for tn, tt in m["trees"].items():
        for n in tt["nodes"]:
            out[n["icon_id"]] = (open(os.path.join(ROOT, "art", "tree-node-icons", *n["file"].split("/")), "rb").read(), n["key"], n["name"])
    for cn, cc in c["classes"].items():
        for n in cc["nodes"]:
            if n.get("icon_id"):
                out[n["icon_id"]] = (open(os.path.join(ROOT, "art", "tree-node-icons", *n["file"].split("/")), "rb").read(), n["key"], n["name"])
            else:
                b_, r_ = re.match(r"^%s\.b(\d)\.r(\d)\.free$" % cn, n["key"]).groups()
                out["Skyy_NodeIcon_%s_B%sR%sFree" % (cn, b_, r_)] = (open(os.path.join(ROOT, *n["reused_ability_icon"].split("/")), "rb").read(), n["key"], n["name"])
    return out


def run_jar(out, jar, scratch, _home):
    K = HK.Child(out)
    z = zipfile.ZipFile(jar)
    zo = zipfile.ZipFile(OLD_JAR)
    names, on = set(z.namelist()), set(zo.namelist())
    K.check(not [n for n in names if n.lower().endswith(".ui")], "J no .ui file (inline pages only)")
    pics = sorted(n for n in on if n.startswith(MAPDIR))
    K.check(pics and all(n in names and z.read(n) == zo.read(n) for n in pics) and sorted(n for n in names if n.startswith(MAPDIR)) == pics,
            "J every 0.5.1 map picture is in the jar byte for byte (%d), none added" % len(pics))
    K.eq(sorted(n for n in names if n.startswith(MAPRES)), sorted(n for n in on if n.startswith(MAPRES)), "J the same 66 page data files")
    removed = sorted(n for n in on - names if not n.endswith(".class"))
    K.eq(removed, [], "J no file removed")
    changed = sorted(n for n in on & names if not n.endswith(".class") and z.read(n) != zo.read(n))
    K.check(set(changed) - set(n for n in changed if n.startswith(MAPRES)) == {"manifest.json"}, "J vs 0.5.1: only the manifest + page data changed: %s" % [n for n in changed if not n.startswith(MAPRES)][:5])
    added = sorted(n for n in names - on if not n.endswith(".class"))
    art = _icon_art()
    want = set()
    for iid in art:
        want |= {"Server/Item/Items/Utility/%s.json" % iid, "Common/Icons/ItemsGenerated/%s.png" % iid}
    want.add("Server/Languages/en-US/server.lang")
    want |= set("Server/Entity/Effects/SkyyTrees/Skyy_Tree_Swing_Harv_%02d.json" % k for k in range(1, 41))
    harv = sorted(n for n in added if n.startswith("Server/Item/Interactions/SkyyTrees/Skyy_Tree_Harv"))
    want |= set(harv) | set(SEL)
    K.eq(sorted(set(added) ^ want), [], "J the new files = 684 icon items x 2 + server.lang + 40 harvest effects + %d harvest steps + the 2 selector overrides" % len(harv))
    K.eq(len(art), 684, "J 684 node icons (361 skill, 283 class, 40 row abilities)")
    bad = []
    for iid, (png, key, nm) in art.items():
        js = json.loads(z.read("Server/Item/Items/Utility/%s.json" % iid))
        if z.read("Common/Icons/ItemsGenerated/%s.png" % iid) != png:
            bad.append((iid, "png"))
        if js.get("Icon") != "Icons/ItemsGenerated/%s.png" % iid or js.get("Variant") is not True or js.get("MaxStack") != 1 or \
                [k for k in ("Categories", "Recipe", "Interactions") if k in js] or "Model" not in js or "Texture" not in js or \
                js.get("TranslationProperties", {}).get("Name") != "server.items.%s.name" % iid:
            bad.append((iid, "json"))
    K.eq(bad[:5], [], "J every icon item: the art file byte for byte, Name / Icon / Variant / MaxStack 1 + the held look, no Categories / Recipe / Interactions")
    lang = z.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines()
    keys = [l.split("=", 1)[0] for l in lang]
    K.check(len(lang) == 2 * 684 and len(set(keys)) == len(keys) and all(("server.items.%s.name=%s" % (i, art[i][2])) in lang for i in art), "J server.lang: both name keys of every icon item, unique")
    # the harvest assets: the overrides = vanilla but Next; the tier tree on a crop / not on a crop
    import serverjar as SJ
    za = zipfile.ZipFile(SJ.assets_zip())
    for p in SEL:
        a, b = json.loads(za.read(p).decode("utf-8-sig")), json.loads(z.read(p))
        K.check(b["Next"] == "Skyy_Tree_Harv" and dict((k, v) for k, v in a.items() if k not in ("Next", "HitBlock", "HitEntity")) == dict((k, v) for k, v in b.items() if k not in ("Next", "HitBlock", "HitEntity")),
                "J %s = vanilla but its Next (the harvest tier) and its inline steps named" % p.split("/")[-1])
        for fld in ("HitBlock", "HitEntity"):
            nm = b[fld]["Interactions"][0]
            body = json.loads(z.read("Server/Item/Interactions/SkyyTrees/%s.json" % nm))
            if "Next" in body and isinstance(body["Next"], str) and body["Next"].startswith("Skyy_Tree_"):
                body["Next"] = json.loads(z.read("Server/Item/Interactions/SkyyTrees/%s.json" % body["Next"]))
            K.eq(body, a[fld]["Interactions"][0], "J %s %s re-inlined = vanilla's" % (p.split("/")[-1], fld))
    H = dict((n.split("/")[-1][:-5], json.loads(z.read(n))) for n in harv)
    ids = ["Skyy_Tree_Swing_Harv_%02d" % k for k in range(1, 41)]

    def walk(have, crop):
        n, steps = "Skyy_Tree_Harv", 0
        while True:
            b_ = H[n]
            steps += 1
            if b_["Type"] == "EffectCondition":
                n = b_["Failed"] if any(e in have for e in b_["EntityEffectIds"]) else b_["Next"]
            elif b_["Type"] == "BlockCondition":
                assert b_["UseLatestTarget"] is True and [m["Block"]["Tag"] for m in b_["Matchers"]] == ["Family=Crop", "Family=Bush"]
                n = b_["Next"] if crop else b_["Failed"]
            else:
                return b_, steps
    t0 = 0.56
    okc, okn = 0, 0
    for k in range(0, 41):
        have = set([ids[k - 1]]) if k else set()
        b_, _st = walk(have, True)
        want_ = 0.2 if k == 0 else round(0.2 - (t0 - t0 / (1 + k / 100.0)), 4)
        okc += 1 if (b_ == {"Type": "Simple", "$Comment": "Pad the interaction length", "RunTime": want_}) else 0
        b2, _st = walk(have, False)
        okn += 1 if b2 == {"Type": "Simple", "$Comment": "Pad the interaction length", "RunTime": 0.2} else 0
    K.check(okc == 41 and okn == 41, "J harvest tiers 0-40 aimed at a crop -> the pad 0.2 - (0.56 - 0.56 / (1 + k%%)) (k 40: 0.04 s); not a crop -> the vanilla 0.2 s pad (%d / %d)" % (okc, okn))
    K.check(all(json.loads(z.read("Server/Entity/Effects/SkyyTrees/%s.json" % i)) == {"Duration": 3, "OverlapBehavior": "Overwrite"} for i in ids), "J the 40 harvest tier effects = the swing markers")
    # every node of every map shows an own icon, one per node, unique within its layout
    icons = {}
    for L in range(NL):
        t = z.read(MAPRES + "L%dZ0.txt" % L).decode("utf-8")
        got = []
        for ln in t.split("\n"):
            f = ln.split("\t")
            if f[0] == "N":
                m = re.search(r'ItemIcon #SkyyTrMN\d+I \{[^}]*ItemId: "([^"]+)"', ln)
                got.append(m.group(1) if m else None)
        icons[L] = got
        K.check(got and all(g and g.startswith("Skyy_NodeIcon_") for g in got) and len(set(got)) == len(got), "J L%d: every node (%d) its own Skyy_NodeIcon_ icon, free diamonds too" % (L, len(got)))
    json.dump(icons, open(os.path.join(scratch, "icons.json"), "w"))
    nodepics = set(n[len(MAPDIR) + 5:-7] for n in names if n.startswith(MAPDIR + "Node/"))
    json.dump(sorted(nodepics), open(os.path.join(scratch, "nodepics.json"), "w"))
    worst = 0
    for L in range(NL):
        for zi in range(ZN):
            worst = max(worst, sum(T51.SMAP_count(x) for x in z.read(MAPRES + "L%dZ%d.txt" % (L, zi)).decode("utf-8").split("\n")))
    K.check(worst + 184 + 3 <= 1000, "J the worst map page data %d elements + the page's 184 + 3 <= 1,000" % worst)
    K.save()


def run_old(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=False)
    V = JClass(PKG + "TreeV3")
    o = dict((n, [int(y) if isinstance(y, int) else str(y) for y in getattr(V, n)]) for n in TABLES)
    json.dump(o, open(os.path.join(scratch, "old051.json"), "w"))
    K.check(len(o["UKEY"]) > 0, "OLD the 0.5.1 tables read (%d upgrades)" % len(o["UKEY"]))
    K.save()


def run_data(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    V = JClass(PKG + "TreeV3")
    o = json.load(open(os.path.join(scratch, "old051.json")))
    n = dict((t, [int(y) if isinstance(y, int) else str(y) for y in getattr(V, t)]) for t in TABLES)
    for t in TABLES:
        if t not in ("UTEXT", "UIC", "RFIC"):
            K.eq(n[t], o[t], "DATA %s unchanged" % t)
    import trees_v3_data as V3D
    V3D.p052_apply()
    ch = dict((n["UKEY"][i], n["UTEXT"][i]) for i in range(len(n["UKEY"])) if n["UTEXT"][i] != o["UTEXT"][i])
    K.eq(sorted(ch), sorted("Skill." + k for k in V3D.P052_TEXT), "DATA UTEXT: exactly the 43 P052 upgrades changed")
    K.check(all(ch["Skill." + k] == v and o["UTEXT"][n["UKEY"].index("Skill." + k)] == V3D.P052_TEXT_OLD[k] for k, v in V3D.P052_TEXT.items()), "DATA UTEXT: old -> new as the table says")
    K.check(all(x.startswith("Skyy_NodeIcon_") for x in n["UIC"]) and len(set(n["UIC"])) == len(n["UIC"]), "DATA UIC: every upgrade (%d) its own icon" % len(n["UIC"]))
    rf = [(n["RFIC"][r], n["RFNAME"][r]) for r in range(len(n["RFIC"]))]
    K.check(all(i.startswith("Skyy_NodeIcon_") for i, nm in rf if nm) and all(i == "" for i, nm in rf if not nm) and len(set(i for i, nm in rf if nm)) == len([1 for i, nm in rf if nm]),
            "DATA RFIC: every free perk / row ability its own icon")
    K.check(not set(n["UIC"]) & set(i for i, nm in rf if nm), "DATA no icon shared between an upgrade and a free perk")
    K.save()


def run_exec51(out, jar, scratch, home):
    T51.run_exec(out, jar, scratch, home)


def _fn(JImplements, JOverride, f):
    @JImplements("java.util.function.Function")
    class Fn(object):
        @JOverride
        def apply(self, a):
            return f(a)
    return Fn()


def run_new(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    _s2 = importlib.util.spec_from_file_location("test_skyymenu_0_3_19", os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.19.py"))
    T19 = importlib.util.module_from_spec(_s2)
    _s2.loader.exec_module(T19)
    hcls = os.path.join(scratch, "hcls_n")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    J = lambda n: JClass(PKG + n)
    Paths, UUID, Int, Dbl = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Integer"), JClass("java.lang.Double")
    St, Cfg, V, TM, Fx, Sk, Gat, Msg, Sw, Ab, Mig = (J("TreeStore"), J("TreeCfg"), J("TreeV3"), J("TreeMap"), J("TreeFx"), J("TreeSk"), J("TreeGather"),
                                                    J("TreeMsg"), J("TreeSwing"), J("TreeAbil"), J("TreeV3Mig"))
    d = os.path.join(scratch, "new")
    os.makedirs(os.path.join(d, "players"), exist_ok=True)
    St.DIR = Paths.get(os.path.join(d, "players"))
    Cfg.FILE = Paths.get(os.path.join(d, "trees.properties"))
    Cfg.load()
    Sk.loadV3(Paths.get(d))
    Sk.reads(True)
    br = St.bridge()
    br.put("skill:fn:level", _fn(JImplements, JOverride, lambda a: Int(30)))
    UKEY = [str(x) for x in V.UKEY]
    TNAME = [str(x) for x in V.TNAME]
    RNUM, UROW, UT, UMAX, UHO = ([int(x) for x in getattr(V, n)] for n in ("RNUM", "UROW", "UT", "UMAX", "UHO"))
    mt = TNAME.index("Mining")
    LOCKG = int(V.LOCKG)

    def ui(k):
        return UKEY.index(k)

    def pfile(uid, ranks, extra="", crlf=False, r52=True):
        t = "v=3\ntreesV3=1\ngates41=1\n" + ("rows52=1\n" if r52 else "") + "name=Test\n" + extra + "".join("%s=%d\n" % (k, v) for k, v in ranks.items())
        if crlf:
            t = t.replace("\n", "\r\n")
        open(os.path.join(d, "players", uid + ".properties"), "wb").write(t.encode("latin-1"))
        St.DATA.remove(UUID.fromString(uid)) if False else None
        return os.path.join(d, "players", uid + ".properties")

    # ================= MOTHERLODE: 1 % a rank, x3 (two fresh rolls), its own "jackpot" word
    pfile(U5, {"Skill.Mining.b1.r4a": 3})
    u5 = UUID.fromString(U5)
    ml = ui("Skill.Mining.b1.r4a")
    v5 = Fx.compute(u5)
    K.check(abs(float(v5[UHO[ml]]) - 0.03) < 1e-9, "ML Motherlode 3 ranks = a 3 %% jackpot chance (TreeFx %.4f)" % float(v5[UHO[ml]]))
    K.check(abs(float(Cfg.PER[UHO[ml]]) - 0.01) < 1e-12 and "Mining.MVeins.per=0.01" in str(Cfg.DEFAULTS), "ML nodes.Mining[MVeins.per] built-in 0.01 (the new default file too)")
    t1, t3, how = str(V.effText(ml, 1)), str(V.effText(ml, 3)), str(V.detHow(UROW[ml], ml))
    K.check(t1 == "Jackpot: 1% chance an ore drops x3 - its own roll, separate from Fortune" and "Jackpot: 3% chance an ore drops x3" in t3,
            "ML the panel: '%s' / rank 3 '%s'" % (t1, t3))
    K.check(how.startswith("Plan: Jackpot: 1% chance/rank an ore drops x3 - its own roll, separate from Fortune.") and "Fortune rolls separately" in how, "ML the Plan line: %s" % how[:140])
    calls = []
    br.put("skill:fn:drops", _fn(JImplements, JOverride, lambda a: (calls.append(1), JClass("java.util.ArrayList")())[1]))
    P5 = E.player(uid=u5, name="SkyyJackpot")
    E.pump(P5)
    Msg.PEND.remove(u5)
    Gat.jackpot(P5.pr, "harness_home", None)
    line = str(Msg.take(u5, 10 ** 13))
    K.check(len(calls) == 2 and "Motherlode jackpot x1" in line, "ML jackpot() = TWO fresh rolls of the ore's drops (x3 in all) + 'Motherlode jackpot x1' in the Tree bonus line: %d calls, %r" % (len(calls), line))
    calls[:] = []
    Gat.jackpot(P5.pr, "another_world", None)
    K.eq(len(calls), 0, "ML jackpot() in another world than the player's: no roll")
    br.remove("skill:fn:drops")
    M52 = J("TreeMig052")
    r = M52.m052Update("# a file\nMining.MVeins.per=0.02\nMining.MVeins.max=15\n")
    K.check(r is not None and "Mining.MVeins.per=0.01\n" in str(r[0]) and str(M52.MK) in str(r[0]) and list(r[3]) == ["Mining.MVeins.per"], "ML TreeMig052: an untouched 0.02 line -> 0.01 + the marker")
    r = M52.m052Update("Mining.MVeins.per=0.05\r\n")
    K.check(r is not None and "Mining.MVeins.per=0.05\r\n" in str(r[0]) and len(r[3]) == 0 and "kept" in " ".join(str(x) for x in r[2]) and str(r[0]).endswith("\r\n"),
            "ML TreeMig052: a hand-edited value is kept and named; the file's CRLF kept")
    K.check(M52.m052Update(str(r[0])) is None, "ML TreeMig052: runs once (the marker)")
    # ================= ROW GATES
    K.eq(int(Cfg.ROW_NEED), 3, "ROW rows.needAbove defaults to 3")
    row = dict((n, [u for u in range(int(V.TU0[mt]), int(V.TU0[mt]) + int(V.TUN[mt])) if RNUM[UROW[u]] == n]) for n in range(1, 7))
    r1 = {"Skill.Mining.b1.r1a": 5, "Skill.Mining.b1.r1b": 3}
    six = dict(r1, **{"Skill.Mining.b1.r2a": 2})
    pfile(U6, six)
    u6 = UUID.fromString(U6)
    d6 = St.data(u6)
    g6, gs = [int(x) for x in V.gatesD(d6, mt)], [int(x) for x in V.gates(mt)]
    K.check(int(V.spent(d6, mt)) == 10 and gs[3] == 10 and g6[3] == LOCKG and g6[2] == gs[2] and int(V.rowSpent(d6, mt, 2)) == 2,
            "ROW 10 points (8 in row 1, 2 in row 2): row 3's total gate (10) is met but the row above holds 2 < 3 -> row 3 locked (%s)" % g6[1:7])
    gem = ui("Skill.Mining.b1.r3a")
    pts = 30
    K.eq(int(V.ustate(d6, gem, pts, 10, V.gatesD(d6, mt))), 0, "ROW a row-3 talent is Locked")
    need = str(V.detNeed(d6, UROW[gem], gem, 0, V.gatesD(d6, mt), 10, pts, 30))
    st = str(V.detState(d6, UROW[gem], gem, 0, V.gatesD(d6, mt), 10, pts))
    K.check("10 points in this tree (you have 10)" in need and "and 3 in row 2 (you have 2)" in need and "in row 2" in st, "ROW the panel names both conditions: %r / %r" % (need, st))
    import skyyui as SUI
    _sw = (424 - SUI.SLOT_FRAME - 12) * 0.95
    st_free = str(V.detState(d6, UROW[gem], -1, 0, V.gatesD(d6, mt), 10, pts))
    K.check(st == "Locked - needs 10 points in this tree and 3 in row 2" and SUI.text_lines(st, _sw, 16, True) <= 2 and SUI.text_lines(st_free, _sw, 16, True) <= 2,
            "FIX the 344 px state label gets the short form (the counts stay in the Needs line) and fits 2 lines: %r / %r" % (st, st_free))
    nr = str(TM.nextRowD(d6, mt, V.gatesD(d6, mt), 10))
    K.check("row 3 needs 3 in row 2" in nr, "ROW the points line: %r" % nr)
    m = str(V.buy(u6, d6, mt, gem, False))
    K.check(int(d6.rk[gem]) == 0 and "in row 2 (you have 2)" in m, "ROW Learn on it is refused, naming the row above: %r" % m)
    tex = jpype.JArray(JString)(len(TM.nodes(0)))
    lit = jpype.JArray(jpype.JBoolean)(len(TM.edges(0)))
    TM.paint(u6, d6, 0, False, tex, lit)
    codes = [int(x) for x in TM.nodes(0)]
    k_gem = codes.index(gem)
    K.check(str(tex[k_gem]).endswith("Locked"), "ROW the map shows it locked (%s)" % str(tex[k_gem]))
    m = str(V.buy(u6, d6, mt, ui("Skill.Mining.b1.r2c"), False))
    g6b = [int(x) for x in V.gatesD(d6, mt)]
    K.check(m.startswith("Done:") and g6b[3] == 10 and int(V.ustate(d6, gem, pts, 11, V.gatesD(d6, mt))) == 1, "ROW one more point in row 2 (3) opens row 3: %r" % m)
    TM.paint(u6, d6, 0, False, tex, lit)
    K.check(str(tex[k_gem]).endswith("Ready"), "ROW ... and the map shows it Ready (%s)" % str(tex[k_gem]))
    pfile(U6, six)
    St.DATA.clear()
    d6 = St.data(u6)
    Cfg.ROW_NEED = 0
    K.check(all([int(x) for x in V.gatesD(d6, tv)] == [int(x) for x in V.gates(tv)] for tv in range(int(V.NV))), "ROW rows.needAbove 0 = the 0.5.1 rule (every tree)")
    Cfg.ROW_NEED = 3
    K.check(all([int(x) for x in V.gatesD(d6, tv)] == [int(x) for x in V.gates(tv)] for tv in range(int(V.NCV))), "ROW class trees are untouched (0.6.0 rebuilds them)")
    small = [(tv, n) for tv in range(int(V.NCV), int(V.NV)) for n in range(2, 7) if 0 < int(V.ROWCAP[tv * 8 + n - 1]) < 3]
    K.check(small and all(int(V.rowNeed(tv, n)) == int(V.ROWCAP[tv * 8 + n - 1]) for tv, n in small) and all(int(V.rowNeed(tv, 1)) == 0 for tv in range(int(V.NV))),
            "ROW a row above with fewer buyable points asks only those (%s); row 1 asks nothing" % [(TNAME[t], n, int(V.ROWCAP[t * 8 + n - 1])) for t, n in small][:4])
    # fix round: an admin switching nodes of the row above off never locks the row below for good (rowNeed uses the LIVE capacity)
    UHK, UCOST = [int(x) for x in V.UHK], [int(x) for x in V.UCOST]
    en0 = [bool(x) for x in Cfg.EN]
    hit = None
    for tv_ in range(int(V.NCV), int(V.NV)):
        us = list(range(int(V.TU0[tv_]), int(V.TU0[tv_]) + int(V.TUN[tv_])))
        for n_ in range(2, 7):
            cap = int(V.ROWCAP[tv_ * 8 + n_ - 1])
            offs = [u for u in us if UHK[u] == 2 and RNUM[UROW[u]] == n_ - 1 and bool(V.live(u))]
            if cap <= 0 or not offs:
                continue
            for u in offs:
                Cfg.EN[UHO[u]] = False
            lc = sum(UMAX[u] * UCOST[u] for u in us if RNUM[UROW[u]] == n_ - 1 and bool(V.live(u)))
            got = int(V.rowNeed(tv_, n_))
            for i_, e_ in enumerate(en0):
                Cfg.EN[i_] = e_
            if lc < min(3, cap):
                hit = (TNAME[tv_], n_, cap, lc, got, int(V.rowNeed(tv_, n_)))
                break
        if hit:
            break
    K.check(hit is not None and hit[4] == hit[3] and hit[5] == min(3, hit[2]),
            "FIX nodes of the row above switched off in Server Setup: the row below asks only what is still buyable, back to normal once on again (tree, row, cap, live cap, need off, need on) = %s" % (hit,))
    # the one-time update rows52: a v=3 file without the marker keeps the rows it has open
    f7 = pfile(U7, six, extra="# a comment line\n", r52=False)
    b7 = open(f7, "rb").read()
    St.DATA.clear()
    d7 = St.readFile(U7)
    a7 = open(f7, "rb").read()
    hist = os.path.join(d, "history", "rows052", U7 + ".properties")
    K.check(not bool(d7.bad) and bool(d7.r52) and bool(d7.rgf[mt * 8 + 3]) and [int(x) for x in V.gatesD(d7, mt)][3] == 10, "ROW rows52: the open Mining row 3 is KEPT (rgf), its gate stays 10")
    K.check(a7.startswith(b7) and a7[len(b7):] == b"Skill.Mining.rowgf=3\nrows52=1\n", "ROW rows52: every line kept byte for byte, 'Skill.Mining.rowgf=3' + 'rows52=1' appended: %r" % a7[len(b7):])
    K.check(os.path.isfile(hist) and open(hist, "rb").read() == b7, "ROW rows52: the old file in history/rows052 first")
    St.DATA.clear()
    St.readFile(U7)
    K.check(open(f7, "rb").read() == a7, "ROW rows52 runs once (a second read changes nothing)")
    f8 = pfile(U8, six, crlf=True, r52=False)
    b8 = open(f8, "rb").read()
    St.readFile(U8)
    K.check(open(f8, "rb").read() == b8 + b"Skill.Mining.rowgf=3\r\nrows52=1\r\n", "ROW rows52: a CRLF file gets CRLF lines")
    f9 = pfile(U9, {"Skill.Mining.b1.r1a": 5, "Skill.Mining.b1.r2a": 3, "Skill.Mining.b1.r2c": 2}, r52=False)
    b9 = open(f9, "rb").read()
    d9 = St.readFile(U9)
    K.check(open(f9, "rb").read() == b9 + b"rows52=1\n" and not any(bool(d9.rgf[i]) for i in range(len(d9.rgf))), "ROW rows52: nothing to keep -> only rows52=1")
    K.check(bool(St.readFile("52525252-0000-0000-0000-00000000ffff").r52), "ROW a new profile is born with rows52 (nothing to keep)")
    # fix round: the one-time update keeps by the shipped rule even while rows.needAbove is 0, so raising it later closes nothing
    f11 = pfile(U11, six, r52=False)
    St.DATA.clear()
    Cfg.ROW_NEED = 0
    d11 = St.readFile(U11)
    Cfg.ROW_NEED = 3
    K.check(bool(d11.r52) and bool(d11.rgf[mt * 8 + 3]) and b"Skill.Mining.rowgf=3\n" in open(f11, "rb").read() and [int(x) for x in V.gatesD(d11, mt)][3] == 10,
            "FIX rows52 run while rows.needAbove = 0 still keeps the open Mining row 3; raised back to 3 the row stays open")
    # fix round: a CRLF file without a final line ending: the last line gets CRLF, never a bare LF
    f12 = pfile(U12, six, crlf=True, r52=False)
    b12 = open(f12, "rb").read()
    assert b12.endswith(b"\r\n")
    b12 = b12[:-2]
    open(f12, "wb").write(b12)
    St.DATA.clear()
    St.readFile(U12)
    a12 = open(f12, "rb").read()
    K.check(a12 == b12 + b"\r\nSkill.Mining.rowgf=3\r\nrows52=1\r\n" and b"\n" not in a12.replace(b"\r\n", b""),
            "FIX rows52 on a CRLF file with no final line ending: CRLF only (%r)" % a12[-50:])
    # the kept row ends with the respec (its History keeps it) and with a rebirth
    St.DATA.clear()
    u7 = UUID.fromString(U7)
    d7 = St.data(u7)
    rs = str(V.respec(u7, d7, mt, False))
    rdir = os.path.join(d, "history", "respec", U7)
    jf = [os.path.join(rdir, x) for x in os.listdir(rdir)] if os.path.isdir(rdir) else []
    K.check("Respec done" in rs and int(V.spent(d7, mt)) == 0 and not bool(d7.rgf[mt * 8 + 3]), "ROW a respec ends the kept row: %r" % rs)
    K.check(len(jf) == 1 and "Skill.Mining.rowgf=3" in open(jf[0], encoding="latin-1").read(), "ROW the respec History keeps Skill.Mining.rowgf (Undo)")
    snap = JClass("java.util.Properties")()
    Mig.writeV3(d7, snap)
    K.check(snap.getProperty("Skill.Mining.rowgf") is None and str(snap.getProperty("rows52")) == "1", "ROW the saved file after the respec: no rowgf, rows52 stays")
    d7.rgf[mt * 8 + 3] = True
    V.rbReset(d7)
    K.check(not bool(d7.rgf[mt * 8 + 3]), "ROW a rebirth ends a kept row too")
    # ================= HARVEST SWING SPEED
    pfile(U10, {"Skill.Farming.b1.r1b": 3})
    u10 = UUID.fromString(U10)
    St.DATA.clear()
    K.check(abs(float(Fx.sk(u10, "swing.farming")) - 3.0) < 1e-9 and float(Sk.sum(u10, "spd")) == 0.0, "HV Quick Scythe 3 = +3 %% harvester swing (TreeSk swing.farming), no move speed any more")
    v10 = Fx.compute(u10)
    K.check(abs(float(Sw.total(u10, v10, 2)) - 0.03) < 1e-9 and int(Sw.tier(Sw.total(u10, v10, 2))) == 3, "HV the harvest tier = Quick Scythe alone: 3")
    br.put("gear:swing:harvest:" + U10, Dbl(10.0))
    br.put("gear:swing:" + U10, Dbl(50.0))
    hm = JClass("java.util.HashMap")()
    acc = JClass("java.util.HashMap")()
    acc.put("swing.farming", Dbl(0.05))
    hm.put("accessories", acc)
    br.put("skill:bonus:" + U10, hm)
    K.check(abs(float(Sw.total(u10, v10, 2)) - 0.18) < 1e-9 and int(Sw.tier(Sw.total(u10, v10, 2))) == 18,
            "HV + SkyyGear's gear:swing:harvest 10 %% + accessories swing.farming 5 %% = tier 18 (the pickaxe key gear:swing never counts here)")
    K.check(abs(float(Sw.total(u10, v10, 0)) - 0.5) < 1e-9, "HV the pickaxe family still reads gear:swing (50 %%)")
    br.put("gear:swing:harvest:" + U10, JString("junk"))
    K.check(abs(float(Sw.gearHarv(u10))) == 0.0, "HV a junk / absent gear:swing:harvest reads 0, never throws")
    for k_ in ("gear:swing:harvest:", "gear:swing:", "skill:bonus:"):
        br.remove(k_ + U10)
    K.check(len(Sw.HARV_IDS) == 41 and str(Sw.HARV_IDS[40]) == "Skyy_Tree_Swing_Harv_40", "HV 40 harvest tier ids")
    K.eq(str(Ab.readersWith(None, True)), "vein,fell,swing,swing.harvest", "HV gear:perk:readers lists swing.harvest (SkyyGear 0.3.42 sells the line)")
    K.eq(str(Ab.readersWith("a,swing.harvest,b,swing", False)), "a,b", "HV ... and removes only its own words")
    open(os.path.join(d, "tree-effects.properties"), "w").write("tree.Farming.b1.r1b.spd.per=5\n")
    Sk.loadV3(Paths.get(d))
    K.check(abs(float(Fx.sk(u10, "swing.farming")) - 3.0) < 1e-9, "HV an old tree.Farming.b1.r1b.spd line is ignored (the built-in 1 a rank)")
    open(os.path.join(d, "tree-effects.properties"), "w").write("tree.Farming.b1.r1b.swing.per=2\ntree.Farming.b1.r1b.swing.max=6\n")
    Sk.loadV3(Paths.get(d))
    K.check(abs(float(Fx.sk(u10, "swing.farming")) - 6.0) < 1e-9, "HV the Server Setup keys tree.Farming.b1.r1b.swing.per / .max set it (2 a rank, most 6 -> 6)")
    os.remove(os.path.join(d, "tree-effects.properties"))
    Sk.loadV3(Paths.get(d))
    qs = ui("Skill.Farming.b1.r1b")
    K.eq(str(V.UTEXT[qs]), "+1% harvester swing speed on crops/rank (the full % on the Harvester, a little less on slower sickles; not hoes)", "HV Quick Scythe's text")
    _swc = zipfile.ZipFile(jar).read(PKG.replace(".", "/") + "TreeSwing.class")
    K.check(b"hoes keep the vanilla swing" in _swc and b"a little less on slower sickles" in _swc, "FIX /tree swing names the hoe exclusion and the slower-sickle number")
    # ================= ICONS: the map page data = the node's own icon (UIC / RFIC), node by node, every layout
    icons = json.load(open(os.path.join(scratch, "icons.json")))
    UIC, RFIC = [str(x) for x in V.UIC], [str(x) for x in V.RFIC]
    bad = []
    for L in range(NL):
        codes = [int(x) for x in TM.nodes(L)]
        for k, c in enumerate(codes):
            want = UIC[c] if c >= 0 else RFIC[-c - 1]
            if icons[str(L)][k] != want:
                bad.append((L, k, c, icons[str(L)][k], want))
    K.eq(bad[:4], [], "IC every map node of every layout shows its node's own icon (UIC / RFIC)")
    K.save()


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    import jpype
    from jpype import JClass, JString
    J = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")

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
    fp = os.path.join(home, "trees.properties")
    t0 = open(fp, "rb").read()
    p0 = dict((f, open(os.path.join(home, "players", f), "rb").read()) for f in os.listdir(os.path.join(home, "players")) if f.endswith(".properties"))
    msgs, bad, ds = start()
    K.eq(bad, [], "LIVE every player file reads")
    po, pn = T46._props(t0), T46._props(open(fp, "rb").read())
    dk = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    K.check(dk in ([], ["Mining.MVeins.per"], ["Mining.MVeins.per", "respec.curve"], ["respec.curve"]) and (po.get("Mining.MVeins.per") != "0.02" or pn.get("Mining.MVeins.per") == "0.01"),
            "LIVE start 1: trees.properties = the MVeins line 0.02 -> 0.01 (+ 0.4.9's own respec line if it never ran): %s" % dk)
    K.check("Motherlode jackpot (SkyyTrees 0.5.2)" in open(fp, encoding="latin-1").read() and any("SkyyTrees 0.5.2" in m for m in msgs), "LIVE start 1: TreeMig052 ran once (marker): %s" % [m[:80] for m in msgs if "0.5.2" in m])
    V = J("TreeV3")
    kept, closed = [], []
    for k, dd in ds.items():
        raw = open(os.path.join(home, "players", k + ".properties"), "rb").read()
        props = T46._props(raw)
        K.check(props.get("rows52") == "1", "LIVE %s: rows52=1 after start 1" % k)
        for tv in range(int(V.NCV), int(V.NV)):
            sp = int(V.spent(dd, tv))
            g = [int(x) for x in V.gates(tv)]
            gd = [int(x) for x in V.gatesD(dd, tv)]
            for n in range(2, 7):
                if sp >= g[n] and gd[n] > sp:
                    closed.append((k, str(V.TNAME[tv]), n))
                if bool(dd.rgf[tv * 8 + n]):
                    kept.append((k[:8], str(V.TNAME[tv]), n))
    K.eq(closed, [], "LIVE no row a live player had open closes (kept rows: %s)" % kept)
    K.notes.append("LIVE kept rows: %s" % kept)
    h1 = T46.tree_hash(home)
    msgs2, bad2, _ds = start()
    K.check(T46.tree_hash(home) == h1 and bad2 == [] and all(m == "" for m in msgs2), "LIVE start 2 changes nothing")
    changed = sorted(f for f in p0 if open(os.path.join(home, "players", f), "rb").read() != p0[f])
    K.notes.append("LIVE player files changed by start 1: %d of %d" % (len(changed), len(p0)))
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


EXPECT.update({   # checked 2026-10-23 (the class compare of the first harness run, every member named by the patch)
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup"],   # version, rows, TreeMig052
    "TreeAbil": ["~m readersWith"],                                                     # + swing.harvest
    "TreeCfg": ["+f ROW_NEED", "~<clinit>", "~m apply", "~m load"],                     # rows.needAbove (+ the default file)
    "TreeData": ["+f r52", "+f rgf", "~c "],                                            # the kept rows + the marker
    "TreeDefs": ["~<clinit>"],                                                          # MVeins per 0.01 + its jackpot texts
    "TreeGather": ["+m jackpot", "~m run"], "TreeMsg": ["~m take"],                    # Motherlode x3 + its word
    "TreeMap": ["+m nextRowD", "~<clinit>", "~m cand", "~m paint"],                     # the player's gates; BUD (free-diamond icons)
    "TreePage": ["~m build", "~m buildK", "~m kSets"],                                  # gatesD + nextRowD in the page
    "TreeSk": ["~<clinit>", "~m loadV3", "~m rank"],                                    # Quick Scythe swing.farming + .swing key; gatesD
    "TreeStore": ["~m readFile", "~m v3clear"],                                         # the rows52 update; a respec ends kept rows
    "TreeSwing": ["+f HARV_IDS", "+f HARV_IDX", "+m gearHarv", "+m treeHarv", "~<clinit>", "~m apply", "~m clear", "~m init", "~m report", "~m total"],
    "TreeV3": ["+f LOCKG", "+f ROWCAP", "+m gatesD", "+m needRow", "+m needShort", "+m openedD", "+m rowAbove", "+m rowAboveMig", "+m rowCapLive", "+m rowGf", "+m rowNeed",
               "+m rowNeedMig", "+m rowSpent", "~<clinit>",
               "~m buy", "~m derive", "~m detHow", "~m detNeed", "~m detState", "~m freeRank", "~m note", "~m rbReset"],
    "TreeV3Mig": ["+f R52_APPLIED", "+f R52_KEPT", "+f R52_LAST", "+m rowsCsv", "+m rowsIn", "+m rowsKeep", "+m rowsLocked", "+m rowsText", "~<clinit>",
                  "~m fresh", "~m journal", "~m migrate", "~m readV3", "~m writeV3"]})
SKIP = re.compile(r"\A(?:Common/UI/Custom/SkyyTrees/Map/|com/skyy/trees/map/|Common/Icons/ItemsGenerated/Skyy_NodeIcon_|Server/Item/Items/Utility/Skyy_NodeIcon_|"
                  r"Server/Languages/|Server/Item/Interactions/SkyyTrees/Skyy_Tree_Harv|Server/Entity/Effects/SkyyTrees/Skyy_Tree_Swing_Harv_|"
                  r"Server/Item/Interactions/Weapons/Sickle/)")
_ORIG_COMPARE = T51._ORIG_COMPARE


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit compare on copies WITHOUT the map / icon / harvest entries (run_jar checks them)"""
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
           phases=[("static", run_static), ("jar", run_jar), ("old", run_old), ("data", run_data), ("exec51", run_exec51), ("new", run_new),
                   ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyTrees"))
