"""Harness for SkyyUiProbe 0.7 (the radial tree map probe M1-M7; SkyyUiProbe/build_skyyuiprobe_0.7.py).
Build first: python SkyyUiProbe/build_skyyuiprobe_0.7.py

    python SkyyUiProbe/test_skyyuiprobe_0.7.py [--keep] [--dir <folder inside tools/dev/scratch/>]

Phases (fresh child JVMs: the game's JRE, the cached HytaleServer.jar, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  J   jar      manifest (op-only probe text, asset pack), every picture under Common/UI/Custom/SkyyUiProbe/ with even (2x) sizes, no
               .ui file, the 10 page data files, the build's page counts (dump.json written by the build run below)
  A   verify   every class loads + initialises with -Xverify:all
  X   exec     -Xverify:all, the SkyyMenu 0.3.19 harness's 0.7 engine stand-ins (a player with the REAL PageManager / WindowManager and
               a recording packet handler) - EVERY case's server path:
       HELP    /skyprobe help (ProbeCmds.arg "help" / "" / "list" / "map") = the 9 cases in chat; an unknown case = a chat line, no page
       OPEN    each case m1 ... m7 (and by name, and "map <case>") opens through the real PageManager.openCustomPage: one CustomPage
               packet whose commands hold every element of the case (the element count the build printed), the page's bindings,
               the server log line "build #1: N elements"
       CLICK   through the REAL PageManager.handleLegacyCustomPageEvent (Data events): 10 node clicks on M1 = 10 chat lines + the
               PASS line; Rebuild 10x = 10 more CustomPage packets + the PASS line; M2 3 node clicks = PASS, both controls answer;
               M4 Next state x5 = 5 UPDATE packets carrying ONLY the 2 AssetPath sets + the text (no rebuild), the 5 paths in order;
               M5 a node click = one update packet with #SkyyPrSel.Anchor + 2 texts; M6 the tooltip discs answer + Esc (Dismiss) logs;
               M7 a node click = PASS; the nav row switches case in place (a rebuild, same page object, no close); Close closes;
               a stub button and unknown data answer without a page change; NO WARNING line except the deliberate unknown data
       CMDS    the three command classes construct (admin: requirePermission skyyuiprobe.admin + no permission groups; alias uiprobe)
  AA  audit    every class / member reference the JVM's access rules would refuse (MethodHandles.privateLookupIn) + the control
Scratch: tools/dev/scratch/uiprobe07/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, importlib.util, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.7"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "uiprobe07", "harness")))
PKG = "com.skyy.uiprobe."
CLASSES = ["ProbeLog", "ProbeData", "MapPage", "ProbeCmds", "SkyProbeMapCmd", "SkyProbeArgCmd", "SkyProbeCmd", "SkyyUiProbePlugin"]


def load_dump():
    return json.load(open(os.path.join(SCRATCH, "assets", "dump.json"), encoding="utf-8"))


def run_exec(out):
    import jpype
    from jpype import JClass
    K = HK.Child(out)
    _s = importlib.util.spec_from_file_location("test_skyymenu_0_3_19", os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.19.py"))
    T19 = importlib.util.module_from_spec(_s)
    _s.loader.exec_module(T19)
    hcls = os.path.join(SCRATCH, "hcls_x")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(SCRATCH)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, JAR], verify=True)
    E = T19.engine(SCRATCH, hcls)
    D = load_dump()
    JV = lambda n: JClass(PKG + n)
    LOG, DATA, CMDS, PAGE = JV("ProbeLog"), JV("ProbeData"), JV("ProbeCmds"), JV("MapPage")
    P = E.player(uid=E.OP, name="SkyyProbe")

    def tail():
        return [str(x) for x in LOG.TAIL.toArray()]

    def new_lines(n0):
        return tail()[n0:]

    def chats(frm):
        return E.strs_of(P, frm)

    def data(js):
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, js))

    def click(a):
        E.pump(P)
        data('{"a":"%s"}' % a)

    def cmds_of(pkt):
        cs = pkt.commands if hasattr(pkt, "commands") else None
        return [] if cs is None else list(cs)

    def cmd_txt(pkt):
        return "\n".join("%s | %s | %s | %s" % (c.type, c.selector, c.data, c.text) for c in cmds_of(pkt)).replace("\\/", "/")

    # ---- pure helpers
    K.eq([str(x) for x in DATA.KEYS], [c[0] for c in D["cases"]], "DATA: the 9 case keys")
    for i, c in enumerate(D["cases"]):
        K.eq(int(DATA.index(c[0])), i, "DATA: index(%s)" % c[0])
        K.eq(int(DATA.index(c[1].upper())), i, "DATA: index(name %s)" % c[1])
        K.eq(int(DATA.ELEMENTS[i]), D["pages"][c[0]]["elements"], "DATA: element count of %s" % c[0])
    K.eq(int(DATA.index("m9")), -1, "DATA: unknown case")
    for js, want in (('{"a":"n12"}', "n12"), ('{ "a" : "case:m4" }', "case:m4"), ('{"b":"x"}', ""), (None, ""), ('{"a":', "")):
        K.eq(str(DATA.act(js)), want, "DATA: act(%r)" % (js,))
    DATA.nodes()
    K.eq(len(DATA.LABEL), D["nodes"], "DATA: node labels")
    K.eq([(int(DATA.NX[k]), int(DATA.NY[k])) for k in range(D["nodes"])], [tuple(x) for x in D["node_xy"]], "DATA: node centres")

    # ---- HELP
    for w in ("help", "", "list", "map", "HELP"):
        f0 = len(E.sent(P))
        CMDS.arg(P.ref, P.st, P.pr, w)
        s = chats(f0)
        K.check(all(c[0] + " (" + c[1] in s for c in D["cases"]) and "Start with /skyprobe m1" in s, "HELP: '%s' lists the 9 cases" % w)
        K.check(P.pm.getCustomPage() is None, "HELP: '%s' opens no page" % w)
    f0 = len(E.sent(P))
    CMDS.arg(P.ref, P.st, P.pr, "m9")
    K.check("No case 'm9'" in chats(f0) and P.pm.getCustomPage() is None, "HELP: an unknown case says so, no page")
    CMDS.two(P.ref, P.st, P.pr, "kit", "m1")
    K.check(P.pm.getCustomPage() is None, "HELP: /skyprobe kit m1 = usage line, no page")

    # ---- OPEN every case (fresh page each), check the packet
    pages = {}
    for i, c in enumerate(D["cases"]):
        key = c[0]
        f0, n0 = len(E.sent(P)), len(tail())
        if i % 3 == 0:
            CMDS.arg(P.ref, P.st, P.pr, key)
        elif i % 3 == 1:
            CMDS.arg(P.ref, P.st, P.pr, c[1])
        else:
            CMDS.two(P.ref, P.st, P.pr, "map", key)
        pg = P.pm.getCustomPage()
        K.check(pg is not None and str(pg.cs) == key, "OPEN %s: the page is open" % key)
        if pg is None:
            continue
        pages[key] = pg
        pk = [p for p in E.sent(P)[f0:] if str(p.getClass().getSimpleName()) == "CustomPage"]
        K.eq(len(pk), 1, "OPEN %s: one CustomPage packet" % key)
        if pk:
            cm = cmds_of(pk[0])
            want = D["pages"][key]["appends"] + D["pages"][key]["sets"] + {"m4": 3, "m5": 1}.get(key, 0)
            K.eq(len(cm), want, "OPEN %s: commands = appends + b.set (+ M4's 3 dyn sets, M5's halo Anchor)" % key)
            txt = "\n".join(E.strs_of(P, f0).split("\n"))
            K.check("#SkyyPrN0B" in txt and "SkyyUiProbe/Map/Base.png" in txt, "OPEN %s: the map markup is in the packet" % key)
            evs = pk[0].eventBindings if hasattr(pk[0], "eventBindings") else None
            K.eq(0 if evs is None else len(list(evs)), D["pages"][key]["binds"], "OPEN %s: the click bindings" % key)
        K.eq(int(pg.lastElements), D["pages"][key]["elements"], "OPEN %s: elements counted at run time" % key)
        lines = new_lines(n0)
        K.check(any("build #1: %d elements" % D["pages"][key]["elements"] in l for l in lines), "OPEN %s: the build log line" % key)
        K.check(any("opened (" in l and "PASS (server)" in l and "Skyy: look" in l for l in lines), "OPEN %s: the opened line" % key)
        K.check("opened (" in chats(f0), "OPEN %s: the chat line" % key)
        if key == "m4":
            K.check(D["m4_2x"][0] in txt and D["m4_1x"][0] in txt, "OPEN m4: both AssetPaths in the packet")
        E.pump(P)

    # ---- CLICKS (on the page that is open now = the last case opened: re-open each case and click through the real PageManager)
    def open_case(key):
        CMDS.arg(P.ref, P.st, P.pr, key)
        E.pump(P)
        return P.pm.getCustomPage()
    pg = open_case("m1")
    n0, f0 = len(tail()), len(E.sent(P))
    for k in (0, 5, 17, 30, 44, 60, 77, 99, 120, 142):
        click("n%d" % k)
    l_ = new_lines(n0)
    K.eq(sum(1 for l in l_ if "click" in l and "reached the server: node" in l), 10, "CLICK m1: 10 node clicks = 10 lines")
    K.check(any("PASS (server) - 10 node clicks" in l for l in l_), "CLICK m1: the 10-click PASS line")
    K.check(D["node_labels"][44] in chats(f0), "CLICK m1: the chat line names the node")
    K.eq(len([p for p in E.sent(P)[f0:] if str(p.getClass().getSimpleName()) == "CustomPage"]), 0, "CLICK m1: a node click redraws nothing")
    n0, f0 = len(tail()), len(E.sent(P))
    click("rebuild10")
    K.eq(len([p for p in E.sent(P)[f0:] if str(p.getClass().getSimpleName()) == "CustomPage"]), 10, "CLICK m1: Rebuild 10x = 10 pages")
    K.check(any("PASS (server) - Rebuild 10x: 10 full pages of %d elements" % D["pages"]["m1"]["elements"] in l for l in new_lines(n0)),
            "CLICK m1: the Rebuild 10x PASS line")
    K.check(P.pm.getCustomPage() == pg and int(pg.builds) == 11, "CLICK m1: same page, 11 builds")
    for key in ("m1b", "m1c"):
        pgx = open_case(key)
        n0, f0 = len(tail()), len(E.sent(P))
        click("rebuild10")
        K.check(any("PASS (server) - Rebuild 10x: 10 full pages of %d elements" % D["pages"][key]["elements"] in l for l in new_lines(n0)),
                "CLICK %s: Rebuild 10x PASS at %d elements" % (key, D["pages"][key]["elements"]))
    pg = open_case("m2")
    n0 = len(tail())
    for k in (3, 4, 5):
        click("n%d" % k)
    click("ctlunder")
    click("ctlover")
    l_ = new_lines(n0)
    K.check(any("M2 map-order PASS (server)" in l for l in l_), "CLICK m2: the 3-click PASS line")
    K.check(any("UNDER a picture got the click" in l for l in l_) and any("OVER a picture got the click" in l for l in l_), "CLICK m2: controls")
    pg = open_case("m4")
    seen = []
    for i in range(5):
        f0 = len(E.sent(P))
        click("m4next")
        pk = [p for p in E.sent(P)[f0:] if str(p.getClass().getSimpleName()) == "CustomPage"]
        K.eq(len(pk), 1, "CLICK m4 #%d: one packet" % (i + 1))
        if pk:
            cm = cmds_of(pk[0])
            K.eq(len(cm), 3, "CLICK m4 #%d: ONLY 3 commands (2 AssetPath + 1 text, no rebuild)" % (i + 1))
            K.check(not bool(pk[0].clear) if hasattr(pk[0], "clear") else True, "CLICK m4 #%d: an update, not a clear" % (i + 1))
            s = cmd_txt(pk[0])
            if i == 0:
                K.notes.append("M4 update commands: " + s[:600])
            j = (i + 1) % 5
            K.check(D["m4_2x"][j] in s and D["m4_1x"][j] in s and "#SkyyPrA1.AssetPath" in s, "CLICK m4 #%d: the state %d paths" % (i + 1, j))
            seen.append(j)
    K.eq(seen, [1, 2, 3, 4, 0], "CLICK m4: states cycle")
    K.eq(int(pg.builds), 1, "CLICK m4: never rebuilt")
    pg = open_case("m5")
    f0, n0 = len(E.sent(P)), len(tail())
    click("n7")
    pk = [p for p in E.sent(P)[f0:] if str(p.getClass().getSimpleName()) == "CustomPage"]
    K.eq(len(pk), 1, "CLICK m5: one update packet")
    if pk:
        K.eq(len(cmds_of(pk[0])), 3, "CLICK m5: 3 commands (the Anchor + 2 texts)")
        K.notes.append("M5 update commands: " + cmd_txt(pk[0])[:600])
        K.check("#SkyyPrSel.Anchor" in cmd_txt(pk[0]), "CLICK m5: the halo Anchor set")
    K.check(int(pg.sel) == 7 and int(pg.builds) == 1, "CLICK m5: selected 7, never rebuilt")
    K.check(any("M5 sent: ONE Anchor update moved the halo to node 7" in l for l in new_lines(n0)), "CLICK m5: the line")
    pg = open_case("m6")
    n0 = len(tail())
    for i in range(3):
        click("tip%d" % i)
    P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Dismiss, None))
    l_ = new_lines(n0)
    K.eq(sum(1 for l in l_ if "M6 click on tooltip disc" in l), 3, "CLICK m6: 3 tooltip discs answer")
    K.check(any("page closed (Esc or Close)" in l and "M6: Skyy: look" in l for l in l_), "CLICK m6: Esc logged")
    K.check(P.pm.getCustomPage() is None, "CLICK m6: Esc closed the page")
    pg = open_case("m7")
    n0 = len(tail())
    click("n100")
    K.check(any("M7 map-scroll PASS (server)" in l for l in new_lines(n0)), "CLICK m7: a node click in the scroll box")
    # nav: switch case in place
    f0, n0 = len(E.sent(P)), len(tail())
    click("case:m3")
    K.check(P.pm.getCustomPage() == pg and str(pg.cs) == "m3", "NAV: case switch = the same page, case m3")
    kinds = [str(p.getClass().getSimpleName()) for p in E.sent(P)[f0:]]
    K.check("CustomPage" in kinds and "SetPage" not in kinds, "NAV: a rebuild (CustomPage), no close / SetPage")
    K.check(any("M3 map-crisp opened" in l for l in new_lines(n0)), "NAV: the opened line for m3")
    n0 = len(tail())
    click("stub:Learn")
    click("zzz")
    l_ = new_lines(n0)
    K.check(any("only a stub" in l for l in l_) and any(l.startswith("W ") and "unknown click data" in l for l in l_), "NAV: stub + unknown")
    click("case:m99")
    K.check(str(pg.cs) == "m3", "NAV: an unknown case changes nothing")
    click("close")
    K.check(P.pm.getCustomPage() is None, "NAV: Close closes the page")
    warns = [l for l in tail() if l.startswith("W ") and "unknown click data" not in l]
    K.eq(warns, [], "no WARNING lines")
    # ---- commands
    for cn in ("SkyProbeCmd", "SkyProbeArgCmd", "SkyProbeMapCmd"):
        try:
            c_ = JV(cn)()
            K.check(True, "CMDS: %s constructs" % cn)
        except Exception as ex:
            K.check(False, "CMDS: %s constructs: %s" % (cn, ex))
    root = JV("SkyProbeCmd")()
    K.check("uiprobe" in [str(a) for a in root.getAliases()], "CMDS: alias uiprobe")
    pgs = root.getPermissionGroups() if hasattr(root, "getPermissionGroups") else None
    K.check(pgs is None or len(list(pgs)) == 0, "CMDS: no permission groups")
    K.notes.append("X: %d log lines; last: %s" % (len(tail()), tail()[-1] if tail() else ""))
    K.save()


def run_jar(out):
    K = HK.Child(out)
    D = load_dump()
    z = zipfile.ZipFile(JAR)
    names = z.namelist()
    man = json.loads(z.read("manifest.json"))
    K.eq((man["Name"], man["Version"], man["Main"], man["IncludesAssetPack"]), ("0.7 SkyyUiProbe", "0.7", "com.skyy.uiprobe.SkyyUiProbePlugin", True),
         "J: manifest")
    K.check("op only" in man["Description"] and "no data" in man["Description"], "J: the description says op only, no data")
    K.eq(sorted(n[:-6].split("/")[-1] for n in names if n.endswith(".class")), sorted(CLASSES), "J: classes")
    K.check(not any(n.lower().endswith(".ui") for n in names), "J: no .ui files")
    pngs = [n for n in names if n.endswith(".png")]
    K.check(all(n.startswith("Common/UI/Custom/SkyyUiProbe/Map/") and "_" not in n for n in pngs), "J: pictures under the custom root")
    bad = [n for n in pngs if n.endswith("@2x.png") and any(v % 2 for v in struct.unpack(">II", z.read(n)[16:24]))]
    K.eq(bad, [], "J: every @2x picture has even sizes")
    K.eq(sorted(n for n in names if n.startswith("com/skyy/uiprobe/pages/")),
         sorted("com/skyy/uiprobe/pages/%s.txt" % c for c in [c[0] for c in D["cases"]] + ["nodes"]), "J: page data files")
    K.eq(sorted(n for n in names if not n.endswith(".class") and n != "manifest.json"), sorted(D["assets"]), "J: assets = the build's")
    for c in D["cases"]:
        t = z.read("com/skyy/uiprobe/pages/%s.txt" % c[0]).decode("utf-8")
        K.check("@2x" not in "".join(l for l in t.split("\n") if "Background" in l), "J: %s markup names no @2x file" % c[0])
        for l in t.split("\n"):
            if 'Background: "SkyyUiProbe/' in l:
                p = l.split('Background: "', 1)[1].split('"', 1)[0]
                if ("Common/UI/Custom/" + p[:-4] + "@2x.png") not in names:
                    K.check(False, "J: %s texture %s shipped" % (c[0], p))
    K.save()


if "--phase" in sys.argv:
    ph = HK.arg("--phase")
    if ph == "mkfake":
        HK.run_mkfake(os.path.join(SCRATCH, "fake"), JAR)
    elif ph == "verify":
        HK.run_verify(HK.arg("--out"), JAR)
    elif ph == "audit":
        HK.run_audit(HK.arg("--out"), JAR, os.path.join(SCRATCH, "fake"))
    elif ph == "exec":
        run_exec(HK.arg("--out"))
    elif ph == "jar":
        run_jar(HK.arg("--out"))
    sys.exit(0)

assert os.path.isfile(JAR), JAR
sc = os.path.realpath(SCRATCH)
assert sc.startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep), "scratch must be inside tools/dev/scratch/"
shutil.rmtree(SCRATCH, ignore_errors=True)
os.makedirs(os.path.join(SCRATCH, "tmp"))
os.makedirs(os.path.join(SCRATCH, "fake"))
env = dict(os.environ)
env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
try:
    # the build's own data (dump-only: no JVM) - the counts the jar must hold
    p = subprocess.run([sys.executable, os.path.join(HERE, "build_skyyuiprobe_0.7.py"), "--dump-only", "--assets-out",
                        os.path.join(SCRATCH, "assets")], env=env, capture_output=True, text=True)
    HK.check(p.returncode == 0, "the build's dump-only run: %s" % p.stderr[-800:])
    for label in ("jar", "mkfake", "verify", "exec", "audit"):
        out = os.path.join(SCRATCH, "%s.json" % label)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--phase", label, "--out", out, "--dir", SCRATCH, "--jar", JAR], env=env)
        HK.check(r.returncode == 0, "%s: the child exited cleanly (%s)" % (label, r.returncode))
        if label == "audit":
            if os.path.isfile(out):
                a = json.load(open(out))
                HK.check(not a["refused"] and a["refs"] > 100, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
                HK.check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
                print("AA. engine-access audit: %d references in %d classes, %d refused, control refused" % (a["refs"], a["classes"], len(a["refused"])))
        elif label != "mkfake":
            HK.take(out, label)
finally:
    if "--keep" not in sys.argv:
        shutil.rmtree(SCRATCH, ignore_errors=True)
print("SkyyUiProbe %s harness: %d ok, %d fail(s)" % (VERSION, HK.OKS[0], len(HK.FAILS)))
for f in HK.FAILS:
    print("FAIL:", f)
sys.exit(1 if HK.FAILS else 0)
