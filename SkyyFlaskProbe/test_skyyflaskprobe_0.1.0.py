"""Harness for SkyyFlaskProbe 0.1.0. Build first: python SkyyFlaskProbe/build_skyyflaskprobe_0.1.0.py

    python SkyyFlaskProbe/test_skyyflaskprobe_0.1.0.py [--jar <SkyyFlaskProbe-0.1.0.jar>] [--keep]

Parent (plain Python, Assets.zip + the SET's SkyyCooking jar + installed mods read-only):
  J  the jar: stable manifest (Name SkyyFlaskProbe, Version 0.1.0, Main, IncludesAssetPack), exactly the 12 expected classes, no .ui
  N  NO OVERRIDE: no asset path / item / interaction / effect id of ours is in Assets.zip, in any SET jar or in any installed mod
     (UserData/Mods, read-only); no lang key of ours is written by another SET jar
  A  every item: no Parent / BlockType / Recipe / Tags / Categories, MaxStack 1, DropOnDeath false, one shared name key per kind, the
     shared look (model / texture / icon exist in Assets.zip); loaded ids: Secondary = our root (flask) or the source's vanilla food
     root (pouch); InteractionVars = the source's (re-flattened here independently) except the Consume_Charge Parent -> our charge
     copy; every charge copy = its source with exactly ONE ModifyInventory replaced by ApplyEffect Skyy_Probe_Supply_Used + the same
     Next (compared node by node), nothing else changed; the condition copy keeps CooldownCondition Potion_Consume_Health
Child (fresh JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, java.io.tmpdir in scratch):
  V  every class loads, verifies and initialises against HytaleServer.jar
  L  FpLogic / FpStore on plain data: kindOf, srcOf (loaded / Empty / foreign / malformed), loadedId round trip for every source,
     known, testFill (alternating), wrongSrc (never a test source, never the head), summary; store fill / head / take / giveBack /
     nextId / busy
Not testable without the game (in-game steps in the build report): the chain running on the client, the effect + timing, the hand
keeping the item, the cancel packet, the held-id swap.
Scratch: tools/dev/scratch/fp0/test (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, copy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.1.0"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyFlaskProbe-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "fp0", "test")))
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
SERVER_JAR = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Server", "HytaleServer.jar")
PKG = "com.skyy.flaskprobe."
CLASSES = sorted(PKG + c for c in ["FpLog", "FpLogic", "FpStore", "FpEng", "FpSyncTask", "FpCore", "FpCmds", "FpStartSys", "FpTick",
                                   "FlaskProbeArgCmd", "FlaskProbeCmd", "SkyyFlaskProbePlugin"])
MARK = "Skyy_Probe_Supply_Used"
OKS, FAILS = [0], []


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("  FAIL:", what)


def set_pins():
    src = open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8").read()
    body = src[src.index("SET = ["):src.index("]\n", src.index("SET = ["))]
    return re.findall(r'\("(Skyy\w+)",\s*"([0-9.]+)"\)', body)


def jmap(z, prefix):
    return dict((n.rsplit("/", 1)[1][:-5], n) for n in z.namelist() if n.startswith(prefix) and n.endswith(".json"))


def part_static():
    jz = zipfile.ZipFile(JAR)
    names = set(jz.namelist())
    man = json.loads(jz.read("manifest.json"))
    check(man.get("Name") == "SkyyFlaskProbe" and man.get("Version") == VERSION and man.get("Group") == "Skyy"
          and man.get("Main") == PKG + "SkyyFlaskProbePlugin" and man.get("IncludesAssetPack") is True and "Dependencies" not in man,
          "J: stable manifest %s" % {k: man.get(k) for k in ("Group", "Name", "Version", "Main")})
    cls = sorted(n[:-6].replace("/", ".") for n in names if n.endswith(".class"))
    check(cls == CLASSES, "J: exactly the 12 classes (%s)" % [c for c in cls if c not in CLASSES][:5])
    check(not [n for n in names if n.endswith(".ui")], "J: no .ui file")
    az = zipfile.ZipFile(ASSETS)
    pins = set_pins()
    cook = [v for m, v in pins if m == "SkyyCooking"]
    check(len(cook) == 1, "N: SkyyCooking pinned once in the SET")
    cz = zipfile.ZipFile(os.path.join(ROOT, "SkyyCooking", "SkyyCooking-%s.jar" % cook[0]))
    check(("SkyyCooking %s" % cook[0]) in man.get("Description", ""), "J: built against the SET's SkyyCooking %s" % cook[0])
    ours = [n for n in names if n.startswith("Server/") and not n.endswith("server.lang")]
    our_ids = set(n.rsplit("/", 1)[1][:-5] for n in ours if n.endswith(".json"))
    check(all(i.startswith("Skyy_Probe_") for i in our_ids), "N: every asset id starts with Skyy_Probe_")
    # ---- no clash with vanilla, the SET jars, installed mods
    others = [("Assets.zip", az)]
    for m, v in pins:
        p = os.path.join(ROOT, m, "%s-%s.jar" % (m, v))
        if os.path.isfile(p) and m != "SkyyFlaskProbe":
            others.append((m, zipfile.ZipFile(p)))
    mods = os.path.join(B.USERDATA, "Mods")
    if os.path.isdir(mods):
        for f in sorted(os.listdir(mods)):
            if f.lower().endswith((".jar", ".zip")) and "flaskprobe" not in f.lower():
                try:
                    others.append(("Mods/" + f, zipfile.ZipFile(os.path.join(mods, f))))
                except Exception:
                    pass
    our_lang = set(l.split("=", 1)[0] for l in jz.read("Server/Languages/en-US/server.lang").decode().splitlines() if "=" in l)
    clash, lclash = [], []
    for label, z in others:
        zn = z.namelist()
        for n in zn:
            if n in names and not n.endswith(("manifest.json", "server.lang")) and not n.endswith("/"):
                clash.append((label, n))
            elif n.endswith(".json") and n.startswith("Server/") and n.rsplit("/", 1)[1][:-5] in our_ids:
                clash.append((label, n))
            elif n.endswith("server.lang") and label != "Assets.zip":
                for l in z.read(n).decode("utf-8", "replace").splitlines():
                    if "=" in l and l.split("=", 1)[0] in our_lang:
                        lclash.append((label, l.split("=", 1)[0]))
    check(not clash, "N: no path / id clash with Assets.zip, %d SET jars, the installed mods: %s" % (len(pins), clash[:5]))
    check(not lclash, "N: no lang key of ours in another jar: %s" % lclash[:5])
    print("N. %d asset ids checked against %d archives" % (len(our_ids), len(others)))
    return jz, az, cz


def part_assets(jz, az, cz):
    I = jmap(jz, "Server/Item/Items/SkyyFlaskProbe/")
    INT = jmap(jz, "Server/Item/Interactions/SkyyFlaskProbe/")
    RT = jmap(jz, "Server/Item/RootInteractions/SkyyFlaskProbe/")
    rdj = lambda z, n: json.loads(z.read(n).decode("utf-8-sig"))
    VI, CI = jmap(az, "Server/Item/Items/"), jmap(cz, "Server/Item/Items/")
    VINT, CINT = jmap(az, "Server/Item/Interactions/"), jmap(cz, "Server/Item/Interactions/")
    AZN = set(az.namelist())

    def src_item(i):
        return rdj(cz, CI[i]) if i in CI else rdj(az, VI[i])

    def flat(i):
        d = src_item(i)
        p = d.pop("Parent", None)
        if not p:
            return d
        b = flat(p)
        for k, v in d.items():
            if k in ("Interactions", "InteractionVars", "TranslationProperties") and isinstance(v, dict) and isinstance(b.get(k), dict):
                m = dict(b[k]); m.update(v); b[k] = m
            else:
                b[k] = v
        return b
    flask = [i for i in I if i.startswith("Skyy_Probe_Flask_V_")]
    pouch = [i for i in I if i.startswith("Skyy_Probe_Pouch_V_")]
    check(len(flask) == 5 and len(pouch) >= 300, "A: 5 flask + %d pouch loaded ids (>= 300, the R4 load test)" % len(pouch))
    check("Skyy_Probe_Flask_Empty" in I and "Skyy_Probe_Pouch_Empty" in I, "A: both Empty ids")
    bad = []
    for i, n in I.items():
        d = rdj(jz, n)
        kind = "Flask" if "_Flask_" in i else "Pouch"
        if any(k in d for k in ("Parent", "BlockType", "Recipe", "Tags", "Categories")) or d.get("MaxStack") != 1 or d.get("DropOnDeath") is not False:
            bad.append((i, "shape"))
        if d["TranslationProperties"] != {"Name": "server.items.Skyy_Probe_%s.name" % kind, "Description": "server.items.Skyy_Probe_%s.description" % kind}:
            bad.append((i, "name key"))
        for k in ("Model", "Texture", "Icon"):
            if "Common/" + d[k] not in AZN:
                bad.append((i, k))
        if i.endswith("_Empty"):
            if "Interactions" in d or "InteractionVars" in d:
                bad.append((i, "empty has interactions"))
            continue
        src = i.split("_V_", 1)[1]
        f = flat(src)
        want = copy.deepcopy(f.get("InteractionVars") or {})
        if kind == "Flask":
            if d["Interactions"] != {"Secondary": "Skyy_Probe_Root_Potion_Health"} or f["Interactions"]["Secondary"] != "Root_Secondary_Consume_Potion_Health":
                bad.append((i, "flask root"))
        else:
            if d["Interactions"] != {"Secondary": f["Interactions"]["Secondary"]} or not re.match(r"^Root_Secondary_Consume_Food_T[123]$", d["Interactions"]["Secondary"]):
                bad.append((i, "pouch root"))
            for e in want["Consume_Charge"]["Interactions"]:
                e["Parent"] = "Skyy_Probe_Charge_" + e["Parent"]
        if json.dumps(d.get("InteractionVars"), sort_keys=True) != json.dumps(want, sort_keys=True):
            bad.append((i, "vars"))
    check(not bad, "A: every item's shape / name / look / root / vars: %s" % bad[:5])

    # ---- charge copies: the source with exactly the one swap
    def swap_ok(src, our, n):
        if isinstance(src, dict):
            if src.get("Type") == "ModifyInventory":
                n[0] += 1
                return isinstance(our, dict) and sorted(our) == ["EffectId", "Next", "Type"] and our["Type"] == "ApplyEffect" \
                    and our["EffectId"] == MARK and json.dumps(our["Next"], sort_keys=True) == json.dumps(src["Next"], sort_keys=True)
            return isinstance(our, dict) and sorted(src) == sorted(our) and all(swap_ok(src[k], our[k], n) for k in src)
        if isinstance(src, list):
            return isinstance(our, list) and len(src) == len(our) and all(swap_ok(a, b, n) for a, b in zip(src, our))
        return src == our
    charges = [i for i in INT if i.startswith("Skyy_Probe_Charge_")]
    check(len(charges) >= 2, "A: charge copies %s" % charges)
    for c in charges:
        s = c[len("Skyy_Probe_Charge_"):]
        srcj = rdj(cz, CINT[s]) if s in CINT else rdj(az, VINT[s])
        n = [0]
        check(swap_ok(srcj, rdj(jz, INT[c]), n) and n[0] == 1, "A: %s = %s with exactly one ModifyInventory -> ApplyEffect %s (same Next)" % (c, s, MARK))
    cond = rdj(jz, INT["Skyy_Probe_Cond_Potion_Health"])
    vc = rdj(az, VINT["Condition_Consume_Potion_Health"])
    vc["Next"]["Next"] = "Skyy_Probe_Charge_Consume_Charge_Potion_Fast"
    check(cond == vc and cond["Next"]["Id"] == "Potion_Consume_Health", "A: the condition copy = vanilla + our charge, same cooldown id")
    check(rdj(jz, RT["Skyy_Probe_Root_Potion_Health"]) == {"RequireNewClick": True, "Interactions": ["Skyy_Probe_Cond_Potion_Health"]},
          "A: the root copy keeps RequireNewClick")
    check(rdj(jz, "Server/Entity/Effects/SkyyFlaskProbe/%s.json" % MARK) == {"Duration": 0.5, "OverlapBehavior": "Overwrite"}, "A: the marker effect")
    print("A. %d items, %d charge copies checked" % (len(I), len(charges)))


# ====================================================================================================== child
def run_child(out):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[SERVER_JAR, JAR], convertStrings=True)
    from jpype import JClass
    res = {"ok": 0, "fails": []}

    def ck(c, w):
        if c:
            res["ok"] += 1
        else:
            res["fails"].append(w)
    CL = JClass("java.lang.ClassLoader").getSystemClassLoader()
    Cls = JClass("java.lang.Class")
    for c in CLASSES:
        try:
            Cls.forName(c, True, CL)
            ck(True, c)
        except Exception as e:
            ck(False, "V: %s does not load / verify: %s" % (c, str(e)[:300]))
    L = JClass(PKG + "FpLogic")
    S = JClass(PKG + "FpStore")
    ck(L.kindOf("Skyy_Probe_Flask_V_Potion_Health_Small") == 0 and L.kindOf("Skyy_Probe_Pouch_Empty") == 1 and L.kindOf("Food_Bread") == -1
       and L.kindOf(None) == -1, "L: kindOf")
    ck(L.srcOf("Skyy_Probe_Flask_V_Potion_Health_Small") == "Potion_Health_Small" and L.srcOf("Skyy_Probe_Pouch_Empty") == ""
       and L.srcOf("Skyy_Probe_Pouch_X") is None and L.srcOf("Skyy_Probe_Pouch_V_") is None and L.srcOf("Potion_Health_Small") is None, "L: srcOf")
    rt = [(k, s) for k, arr in ((0, L.FLASK_SRC), (1, L.POUCH_SRC)) for s in arr if L.srcOf(L.loadedId(k, s)) != s or L.kindOf(L.loadedId(k, s)) != k or not L.known(k, s)]
    ck(not rt and len(L.FLASK_SRC) == 5 and L.NLOADED == len(L.FLASK_SRC) + len(L.POUCH_SRC), "L: loadedId round trip for every source: %s" % rt[:3])
    ck(L.loadedId(0, None) == "Skyy_Probe_Flask_Empty" and L.loadedId(1, "") == "Skyy_Probe_Pouch_Empty" and not L.known(0, "Food_Bread"), "L: Empty ids, known")
    f = [str(x) for x in L.testFill(1, 10)]
    ck(len(f) == 10 and f[0] == L.POUCH_TEST[0] and f[1] == L.POUCH_TEST[1] and f[2] == L.POUCH_TEST[0] and L.POUCH_TEST[0] != L.POUCH_TEST[1],
       "L: testFill alternates two different sources %s" % f[:3])
    for k, t in ((0, L.FLASK_TEST), (1, L.POUCH_TEST)):
        w = L.wrongSrc(k, t[0])
        ck(w is not None and w not in [str(x) for x in t] and L.known(k, w), "L: wrongSrc(%d) = %s (known, not a test source)" % (k, w))
    ck(L.summary(None) == "empty" and L.summary(L.testFill(0, 3)) == "3 (next %s): %s x2, %s x1" % (L.FLASK_TEST[0], L.FLASK_TEST[0], L.FLASK_TEST[1]),
       "L: summary = %s" % L.summary(L.testFill(0, 3)))
    U = JClass("java.util.UUID").randomUUID()
    ck(S.head(U, 0) is None and S.nextId(U, 0) == "Skyy_Probe_Flask_Empty" and not S.busy(U), "L: an empty store")
    S.fill(U, 0, L.testFill(0, 4))
    a = S.take(U, 0)
    ck(a == L.FLASK_TEST[0] and S.head(U, 0) == L.FLASK_TEST[1] and S.nextId(U, 0) == "Skyy_Probe_Flask_V_" + L.FLASK_TEST[1], "L: take -> next head")
    S.giveBack(U, 0, a)
    ck(S.head(U, 0) == L.FLASK_TEST[0] and S.list(U, 0).size() == 4 and S.list(U, 1).size() == 0, "L: giveBack puts it back at the head")
    S.SYNC.put(U, JClass("java.lang.Boolean").TRUE)
    ck(S.busy(U) and S.STRICT, "L: busy with a pending sync; strict defaults ON")
    json.dump(res, open(out, "w"))


def main():
    if "--child" in sys.argv:
        run_child(arg("--child"))
        return
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    try:
        jz, az, cz = part_static()
        part_assets(jz, az, cz)
        out = os.path.join(SCRATCH, "child.json")
        subprocess.run([sys.executable, os.path.abspath(__file__), "--child", out, "--dir", SCRATCH, "--jar", JAR], env=env)
        if os.path.isfile(out):
            d = json.load(open(out))
            OKS[0] += d["ok"]
            for f in d["fails"]:
                check(False, "child: " + f)
            print("V/L. child JVM: %d ok, %d fail(s)" % (d["ok"], len(d["fails"])))
        else:
            check(False, "child: no result")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
            try:
                os.rmdir(os.path.dirname(SCRATCH))
            except OSError:
                pass
    print("%d ok, %d fail(s)" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
