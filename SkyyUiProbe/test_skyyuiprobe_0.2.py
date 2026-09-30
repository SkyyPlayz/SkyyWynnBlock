"""Bare-JVM check for SkyyUiProbe 0.2 (made from test_skyyuiprobe_0.1.py; kept next to the build so the build report's JVM claims
can be re-run).

    python SkyyUiProbe/test_skyyuiprobe_0.2.py [--jar <SkyyUiProbe-0.2.jar>] [--dir <scratch folder>] [--keep]

Build the jar first (python SkyyUiProbe/build_skyyuiprobe_0.2.py). Re-run this after every build AND whenever tools/skyyui.py changes
(its kit id): the probe pages come from the kit, so a kit change can change what the pages send.
  D  the expected page commands: runs the build script with --dump-only <scratch>/dump.json (a subprocess: SUI.verify() + the page
     proofs, no JVM, no class / jar written) and refuses a jar built with another kit id (ProbeLog.kit())
  A  every class of the jar loads and verifies (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the jar)
  S  the dump itself: 22 views = pages 1-22; every probe page (with its footer) and the index (with its runtime Info line) pass
     SUI.check_page (markup rules, parents, no duplicate id, every b.set target exists); the index passes SUI.assert_proven with
     nothing allowed and carries no texture / sound / FontName / FlexWeight / Wrap / LetterSpacing / LayoutMode other than Top /
     Left / Anchor margin; every probe page passes SUI.assert_proven with only its own key allowed (a disconnect names its key);
     no underscore ids, every page root <= 980 px high (Width / Height only), the flat Back / Close footer is the last 4 appends of
     every probe page; the index: two columns of 11 in the list order, SUI.PROBE_OPEN_FIRST first with green Open buttons, the
     "Open base1, base2, base3 first, then base4" line at the top; its b.set texts hold no < or > (proven inline only) and no
     builder names
  B  ProbeViews: count / order / names / keys / summaries match the build (Probe.summary, or the kit's whole PROBE_SUMMARY line
     where the kit cut it) and fit their index label (SUI.text_width); nextOf(); find() for numbers, names, "#3", junk, null - and
     the upper-case names ("TILE", "LAYOUT-RIGHT") under a Turkish default locale (where "TILE".toLowerCase() is "t\u0131le")
  C  every view through the ENGINE's UICommandBuilder / UIEventBuilder (ProbeViews.render / index): exactly the dumped appends +
     b.set lines + extra Java lines (page 17: its Value.ref line), the index: + its runtime Info line and the 22 Open bindings
     (open:<n>, in the list order) + Close. Page 18: every append + b.set line up to its grid fill; the grid fill needs the item asset
     store (a bare JVM has none: new ItemStack throws) - its item ids are checked in Assets.zip (read-only) instead
  E  ProbePage.build: views 1-22 send their page + bind only Back / Close; 0 / unknown views send the index; lastText() = the
     build's text for every page, and every lastText / failure Info text fits the Info label (SUI.text_width)
  K  clicks through ProbePage.handleDataEvent on a harness subclass whose rebuild() does what the engine's does (build into fresh
     builders, an exception passes through, nothing "sent" then) and whose close() is counted; the chat goes to a recording packet
     handler: open / back / close, the Info line after Back, a stale / double Back (already on the index: the index is re-sent and
     the Info line is KEPT, also after a failed build), malformed input (never a state change, never a throw), and a probe whose
     build throws (18 here) -> back on the index view, the Info text, ONE chat line, no rebuild from the catch
  L  the server log order (bytecode): "opening probe" before rebuild / openCustomPage, "sent probe" after
  P  permissions with the engine's own code: /skyprobe and its usage variant hold skyyuiprobe.admin with empty permission-group lists,
     getPermissionGroupsRecursive() gives the node to no group; a real PermissionsModule object (never set up) with one fake provider
     + those virtual groups answers AbstractCommand.hasPermission: plain Adventurer, skyy.*, hytale.*, hytale.command.* refused; op
     ("*") and a node holder pass; control: a command listing hytale:Adventurer IS granted to the same plain player
  M  the jar: manifest (Main, Version 0.2, IncludesAssetPack false), exactly the 7 classes, no .ui file, the ready line's text
Not testable without the game (UNVERIFIED): how the client draws each page (that is what the mod is for), probe 18's grid, the real
PageManager / CommandManager dispatch. Nothing is deployed. Default scratch folder: tools/dev/scratch/uiprobe02-test (deleted at the
end unless --keep); TEMP / TMP and java.io.tmpdir point into it. --dir must name a folder INSIDE tools/dev/scratch that is new,
empty or an earlier run's (it carries the harness's marker file): anything else is refused before the run, so the end-of-run
delete can only remove a folder this harness made. Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.2"
PAGE_COUNT = 22
PKG = "com.skyy.uiprobe."
BUILD = os.path.join(HERE, "build_skyyuiprobe_%s.py" % VERSION)
NODE = "skyyuiprobe.admin"
CLASSES = ["ProbeLog", "ProbeViews", "ProbePage", "ProbeCmds", "SkyProbeArgCmd", "SkyProbeCmd", "SkyyUiProbePlugin"]


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.join(TOOLS, "dev", "scratch")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "uiprobe02-test")))
MARK = os.path.join(SCRATCH, ".skyyuiprobe-harness")    # marks a scratch folder this harness made (the only kind it deletes)
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]


def under_scratch(path):
    """True when path is a folder strictly inside tools/dev/scratch (not the scratch root itself, not elsewhere)."""
    p, r = os.path.normcase(os.path.realpath(path)), os.path.normcase(os.path.realpath(SCRATCH_ROOT))
    try:
        return p != r and os.path.commonpath([p, r]) == r
    except ValueError:              # another drive
        return False


def claim_scratch():
    """Refuse a --dir the end-of-run delete must not touch (0.2 review: --dir <any real folder> used to be deleted); else make
    the folder and mark it as the harness's."""
    if not under_scratch(SCRATCH):
        raise SystemExit("--dir must be a folder inside %s (the harness deletes it at the end): %s" % (SCRATCH_ROOT, SCRATCH))
    if os.path.exists(SCRATCH) and not os.path.isdir(SCRATCH):
        raise SystemExit("--dir %s is a file, not a folder" % SCRATCH)
    if os.path.isdir(SCRATCH) and os.listdir(SCRATCH) and not os.path.isfile(MARK):
        raise SystemExit("--dir %s already holds files this harness did not make - pick a new folder name" % SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    with open(MARK, "w") as f:
        f.write("SkyyUiProbe %s harness scratch - deleted at the end of the run unless --keep\n" % VERSION)


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ------------------------------------------------------------------------------------------------ D. the expected commands
def make_dump(tmp):
    dump = os.path.join(SCRATCH, "dump.json")
    env = dict(os.environ, TEMP=tmp, TMP=tmp)
    r = subprocess.run([sys.executable, BUILD, "--dump-only", dump], cwd=ROOT, env=env, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.isfile(dump):
        print(r.stdout[-3000:], r.stderr[-3000:])
        raise SystemExit("D. the build script's --dump-only failed (exit %d)" % r.returncode)
    with open(dump, encoding="utf-8") as f:
        return json.load(f)


def expected(view, sui, info=None):
    """[(type, selector, data value or markup)] a view must send: appends, b.set lines (+ the index Info line)."""
    out = []
    for p, mk in view["appends"]:
        out.append(("AppendInline", None if p is None else "#" + sui.render(p).lstrip("#"), mk))
    for ident, prop, val in view["sets"]:
        out.append(("Set", "#" + sui.render(ident).lstrip("#") + "." + prop, sui.render(val) if isinstance(val, str) else val))
    if info is not None:
        out.append(("Set", view["info"][0] + "." + view["info"][1], info))
    return out


ELEM_ID = re.compile(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*\s+#([A-Za-z0-9_]+)\s*\{")
REF_LINE = re.compile(r'^\s*b\.set\("([^"]+)",\s*com\.hypixel\.hytale\.server\.core\.ui\.Value\.ref\("([^"]+)",\s*"([^"]+)"\)\);\s*$')
GRID_SET = re.compile(r'^\s*b\.set\("([^"]+\.Slots)",\s*\(\w+\)\);\s*$')
GRID_ITEM = re.compile(r'new com\.hypixel\.hytale\.server\.core\.inventory\.ItemStack\("([^"]+)",\s*(\d+)\)')


def extras(view):
    """(expected extra commands, grid item ids or None, unknown lines) from a view's extra Java lines."""
    exp, grid, unknown = [], None, []
    for l in view.get("extra", []):
        m = REF_LINE.match(l)
        if m:
            exp.append(("Set", m.group(1), {"$Document": m.group(2), "@Value": m.group(3)}))
            continue
        g = GRID_SET.match(l)
        if g:
            exp.append(("Set", g.group(1), "<grid slots>"))
            continue
        if "ItemGridSlot" in l or re.match(r"^\s*java\.util\.ArrayList \w+ = new java\.util\.ArrayList\(\);\s*$", l):
            grid = (grid or []) + GRID_ITEM.findall(l)
            continue
        unknown.append(l)
    return exp, grid, unknown


def same(got, exp):
    """one engine command (type, selector, data, text) against one expected entry."""
    t, sel, data, text = got
    et, esel, ev = exp
    if t != et or sel != esel:
        return False
    if t == "AppendInline":
        return text == ev and data is None
    try:
        v = json.loads(data)["0"]
    except Exception:
        return False
    if ev == "<grid slots>":
        return isinstance(v, list)
    if isinstance(ev, float) and not isinstance(ev, bool):
        return isinstance(v, (int, float)) and abs(v - ev) < 1e-6
    return v == ev


def run():
    tmp = os.path.join(SCRATCH, "tmp")
    hcls = os.path.join(SCRATCH, "hclasses")
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(hcls, exist_ok=True)
    import skyyui as SUI
    SUI.verify(quiet=True)             # read-only Assets.zip check; the kit's probe pages (page 17's Value.ref Java) need it
    dump = make_dump(tmp)
    print("D. dump: kit %s, %d views + the index" % (dump["kit"], len(dump["order"])))

    import jpype
    from jpype import JClass, JImplements, JOverride, JInt, JString
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, JAR, B.JAVASSIST, hcls], convertStrings=True)

    # ---------------- A. load + verify
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = sorted(n[:-6].replace("/", ".") for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class"))
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("A. load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    check(names == sorted(PKG + c for c in CLASSES), "A. the jar holds exactly the 7 classes: %s" % names)
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return
    PV, PL = JClass(PKG + "ProbeViews"), JClass(PKG + "ProbeLog")
    check(str(PL.kit()) == dump["kit"], "D. the jar was built with this kit (%s, jar %s) - rebuild the jar" % (dump["kit"], PL.kit()))
    if FAILS:
        return

    # ---------------- S. the dump itself
    order = [int(x) for x in dump["order"]]
    views = dict((n, dump[str(n)]) for n in order)
    foot = dump["foot"]
    check(sorted(order) == list(range(1, PAGE_COUNT + 1)), "S. %d views = probe pages 1-%d: %s" % (PAGE_COUNT, PAGE_COUNT, sorted(order)))
    kit_pages = SUI.probe_pages("SkyyPb")
    check([(p.n, p.name, p.key) for p in kit_pages] == [(n, dump["names"][str(n)], dump["keys"][str(n)]) for n in sorted(order)],
          "S. the views are the kit's probe pages (numbers, names, keys)")
    first = list(SUI.PROBE_OPEN_FIRST)
    check(dump["open_first"] == first and [dump["names"][str(n)] for n in order[:len(first)]] == first
          and order[len(first):] == sorted(order[len(first):]), "S. list order: %s first, then by number: %s" % (first, order))

    def appends_of(v, more_sets=()):
        ap = SUI.Appends([(p, m) for p, m in v["appends"]])
        ap.sets = [tuple(x) for x in v["sets"]] + [tuple(x) for x in more_sets]
        return ap

    for n in order:
        v = views[n]
        mks = [m for _p, m in v["appends"]]
        ids = [i for m in mks for i in ELEM_ID.findall(re.sub(r'"(?:[^"\\]|\\.)*"', '""', m))]
        check(len(ids) > 0 and not any("_" in i for i in ids) and len(set(ids)) == len(ids),
              "S. probe %d: %d element ids, no underscore, no duplicate" % (n, len(ids)))
        r = re.match(r"Group #\w+ \{ Anchor: \(Width: (\d+), Height: (\d+)\); \}$", mks[0])
        check(v["appends"][0][0] is None and r is not None and int(r.group(2)) <= 980 and int(r.group(2)) == v["h"],
              "S. probe %d: root Width / Height only, <= 980 px (%s): %s" % (n, v["how"], mks[0][:80]))
        last = v["appends"][-4:]
        check(len(last) == 4 and last[0][1].startswith("Group #SkyyPbNav {") and foot[0][1:] in last[1][1] and foot[1][1:] in last[3][1]
              and last[1][0] == "SkyyPbNav" and last[3][0] == "SkyyPbNav", "S. probe %d: the Back / Close footer is the last 4 appends" % n)
        body_kids = [p for p, _m in v["appends"] if p == last[0][0]]
        check(last[0][0] is not None, "S. probe %d: the footer sits in #%s (%d children)" % (n, last[0][0], len(body_kids)))
        try:
            SUI.check_page(appends_of(v), "SkyyPb")
            ok = True
        except ValueError as ex:
            ok = ex
        check(ok is True, "S. probe %d (+ footer): SUI.check_page (%s)" % (n, ok))
        key = dump["keys"][str(n)]
        try:
            SUI.assert_proven(appends_of(v), allow=(key,), what="probe %d" % n)
            ok = True
        except ValueError as ex:
            ok = ex
        check(ok is True, "S. probe %d: SUI.assert_proven with only its own key %r allowed (%s)" % (n, key, ok))
    ix = dump["index"]
    ixa = appends_of(ix, [ix["info_set"]])
    try:
        SUI.check_page(ixa, "SkyyPb")
        ok = True
    except ValueError as ex:
        ok = ex
    check(ok is True, "S. index (+ its runtime Info line): SUI.check_page (%s)" % ok)
    try:
        toks = SUI.assert_proven(ixa, allow=(), what="index")
        ok = True
    except ValueError as ex:
        ok, toks = ex, {}
    check(ok is True and all(g is None for g in toks.values()), "S. index: SUI.assert_proven, nothing allowed, every token proven (%s)" % ok)
    unflat = []
    for p, m in ix["appends"]:
        bad = [x for x in ("Common/", "Sounds/", "FontName", "LetterSpacing", "FlexWeight", "Wrap", "TexturePath", "Disabled") if x in m]
        lms = [x for x in re.findall(r"LayoutMode:\s*([A-Za-z]+)", m) if x not in ("Top", "Left")]
        marg = re.search(r"Anchor: \([^)]*\b(Top|Bottom|Left|Right|Horizontal|Vertical|Full):", m)
        if bad or lms or marg or not re.match(r"(Group|Label|TextButton)\b", m):
            unflat.append("%s %s %s in %s" % (bad, lms, marg and marg.group(0), m[:90]))
    check(not unflat, "S. index flat only (Group / Label / TextButton, LayoutMode Top / Left, no texture / sound / FontName / "
                      "FlexWeight / Wrap / LetterSpacing / Anchor margin): %s" % unflat[:3])
    r = re.match(r"Group #SkyyPbIx \{ Anchor: \(Width: (\d+), Height: (\d+)\);", ix["appends"][0][1])
    check(ix["appends"][0][0] is None and r is not None and int(r.group(1)) <= 1600 and int(r.group(2)) <= 980,
          "S. index root Width / Height only, <= 1600 x 980: %s" % ix["appends"][0][1][:80])
    per = int(dump["per_col"])
    cols = {}
    for p, m in ix["appends"]:
        g = re.match(r"Group #SkyyPbIxRow(\d+) \{", m)
        if g:
            cols.setdefault(p, []).append(int(g.group(1)))
    check(cols.get("SkyyPbIxColA") == order[:per] and cols.get("SkyyPbIxColB") == order[per:] and per == 11
          and len(order) - per == 11, "S. index: two columns of 11 entries in the list order: %s" % cols)
    opens = dict((int(g.group(1)), m) for _p, m in ix["appends"] for g in [re.match(r"TextButton #SkyyPbIxOpen(\d+) \{", m)] if g)
    check(sorted(opens) == sorted(order) and all(("#1f5a34" in opens[n]) == (dump["names"][str(n)] in first) for n in order),
          "S. index: one Open per page, green for %s, blue for the rest" % first)
    for n in order:
        kids = [m for p, m in ix["appends"] if p in ("SkyyPbIxTop%d" % n, "SkyyPbIxLow%d" % n)]
        has = [any(re.match(r"%s #SkyyPbIx%s%d \{" % (t, w, n), m) for m in kids) for t, w in
               (("Label", "Num"), ("Label", "Name"), ("TextButton", "Open"), ("Label", "What"))]
        what_set = [s[2] for s in ix["sets"] if s[0] == "SkyyPbIxWhat%d" % n]
        inline = [m for m in kids if m.startswith("Label #SkyyPbIxWhat%d " % n)]
        shown = what_set[0] if what_set else (re.search(r'Text: "([^"]*)"', inline[0]).group(1) if inline else None)
        check(all(has) and shown == dump["whats"][str(n)] and ('Text: "%s"' % dump["names"][str(n)]) in "".join(kids)
              and ('Text: "%d"' % n) in "".join(kids), "S. index entry %d: number, name, Open, summary %r" % (n, shown))
    sub1 = [s[2] for s in ix["sets"] if s[0] == "SkyyPbIxSub1"]
    check(len(sub1) == 1 and sub1[0].startswith("Open base1, base2, base3 first, then base4"),
          "S. index top line: %r" % (sub1[:1],))
    for ident, prop, val in ix["sets"]:
        t = SUI.render(val) if isinstance(val, str) else str(val)
        check("<" not in t and ">" not in t, "S. index b.set %s: no < or > (%r)" % (ident, t))
        check("Fable" not in t, "S. index b.set %s: no builder name (%r)" % (ident, t))
    check(not any("Fable" in m for _p, m in ix["appends"]), "S. index markup: no builder name")
    print("S. dump checks done (22 pages + the index through SUI.check_page, assert_proven)")

    # ---------------- B. ProbeViews data + find()
    nm = [str(x) for x in PV.names()]
    check(int(PV.count()) == len(order) and [int(x) for x in PV.order()] == order, "B. count / order = the build's")
    check(all(nm[n] == dump["names"][str(n)] for n in order) and nm[0] == "", "B. names() = the build's")
    ks = [str(x) for x in PV.keys()]
    check(all(ks[n] == dump["keys"][str(n)] for n in order), "B. keys() = the build's")
    # the summaries: the kit's Probe.summary, or its whole PROBE_SUMMARY line where the kit cut it at 95 characters (base2)
    kit_by_n = dict((p.n, p) for p in kit_pages)
    for n in order:
        w, kp = str(PV.whatOf(n)), kit_by_n[n]
        full = SUI.PROBE_SUMMARY.get(kp.name, "")
        check(w == dump["whats"][str(n)] and (w == kp.summary or (kp.summary.endswith("...") and w == full)),
              "B. probe %d: whatOf = the kit's summary line: %r" % (n, w))
        tw = SUI.text_width(w, int(dump["what_fs"]))
        check(len(w) > 0 and tw + int(dump["fit_margin"]) <= int(dump["what_w"]),
              "B. probe %d: the summary fits its index label (%.0f + %s <= %s px at %s px)" % (n, tw, dump["fit_margin"], dump["what_w"],
                                                                                          dump["what_fs"]))
        nw = SUI.text_width(nm[n], int(dump["name_fs"]), bold=True)
        check(nw + int(dump["fit_margin"]) <= int(dump["name_w"]), "B. probe %d: the name fits its label (%.0f px)" % (n, nw))
    check(str(PV.nameOf(99)) == "?" and str(PV.keyOf(-1)) == "?" and str(PV.whatOf(0)) == "", "B. nameOf / keyOf / whatOf of a missing page")
    nx = [int(PV.nextOf(n)) for n in order]
    check(nx == order[1:] + [-1] and int(PV.nextOf(0)) == -1 and int(PV.nextOf(99)) == -1, "B. nextOf() follows the list order: %s" % nx)
    idx = dict((dump["names"][str(n)], n) for n in order)
    cases = [("18", 18), ("22", 22), ("19", 19), ("base3", idx.get("base3")), ("base4", 19), ("CHECKBOX", idx.get("checkbox")),
             ("#3", 3), (" 7 ", 7), ("003", 3), ("022", 22), ("0", -1), ("23", -1), ("1234", -1), ("abc", -1), ("", -1), ("#", -1),
             ("  ", -1), (None, -1), ("base5", -1), ("TILE", idx.get("tile")), ("Disabled-Prop", idx.get("disabled-prop")),
             ("layout-right", 22), ("Flex-Rows", 21), ("#button-text", 20)]
    for s, want in cases:
        check(int(PV.find(s)) == want, "B. find(%r) = %s (got %s)" % (s, want, PV.find(s)))
    Locale = JClass("java.util.Locale")
    old = Locale.getDefault()
    try:
        Locale.setDefault(Locale.forLanguageTag("tr-TR"))
        check(str(JString("TILE").toLowerCase()) != "tile", "B. control: under tr-TR the plain toLowerCase() of TILE is not 'tile'")
        for s in ("TILE", "DISABLED-PROP", "ITEMSLOT", "BASE1", "QUALITY-FRAME", "LAYOUT-RIGHT", "BASE4", "BUTTON-TEXT"):
            want = idx.get(s.lower())
            check(want is not None and int(PV.find(s)) == want, "B. tr-TR default locale: find(%r) = %s (got %s)" % (s, want, PV.find(s)))
    finally:
        Locale.setDefault(old)
    print("B. ProbeViews data + find() done")

    # ---------------- C. every view through the engine's builders
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def cmds(b):
        return [(str(c.type), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)) for c in b.getCommands()]

    def evs(ev):
        out = []
        for e in ev.getEvents():
            d = json.loads(str(e.data)) if e.data is not None else None
            out.append((str(e.type), str(e.selector), d))
        return out

    def compare(got, exp, what):
        ok = len(got) == len(exp) and all(same(g, e) for g, e in zip(got, exp))
        if not ok:
            for i, (g, e) in enumerate(zip(got, exp)):
                if not same(g, e):
                    print("   first difference at %d:\n     got %r\n     exp %r" % (i, g, e))
                    break
            else:
                print("   length: got %d, expected %d" % (len(got), len(exp)))
        check(ok, what)
        return ok

    def grid_throw(ex):
        s = str(ex) + " " + " ".join(str(f) for f in ex.getStackTrace()) if hasattr(ex, "getStackTrace") else str(ex)
        return "ItemStack" in s or "ItemGridSlot" in s

    az = zipfile.ZipFile(os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Assets.zip"))
    items = set(os.path.basename(n)[:-5] for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    az.close()
    rendered = {}
    grid_views = []
    for n in order:
        v = views[n]
        base = expected(v, SUI)
        ex_cmds, grid, unknown = extras(v)
        check(not unknown, "C. probe %d: every extra Java line is understood by the harness: %s" % (n, unknown))
        b = UCB()
        thrown = None
        try:
            r = PV.render(b, n)
            check(bool(r), "C. render(b, %d) answers true" % n)
        except Exception as ex:
            thrown = ex
        got = cmds(b)
        if grid is not None:
            grid_views.append(n)
            check(len(grid) > 0 and all(i in items for i, _q in grid), "C. probe %d grid item ids are in Assets.zip: %s" % (n, grid))
            if thrown is not None:
                check(grid_throw(thrown), "C. probe %d throws only at its grid fill (ItemStack needs the asset store): %s" % (n, thrown))
                compare(got, base, "C. probe %d: every append + b.set line before the grid fill (%d commands)" % (n, len(base)))
            else:
                compare(got, base + ex_cmds, "C. probe %d: appends + b.set lines + the grid Slots line" % n)
        else:
            check(thrown is None, "C. probe %d renders without an exception (%s)" % (n, thrown))
            compare(got, base + ex_cmds, "C. probe %d: exactly the dumped %d appends + %d b.set lines + %d extra line(s)" % (
                n, len(v["appends"]), len(v["sets"]), len(ex_cmds)))
        rendered[n] = (got, thrown)
    check(not bool(PV.render(UCB(), 0)) and not bool(PV.render(UCB(), 99)) and not bool(PV.render(UCB(), -1)), "C. render() of 0 / 99 / -1 = false")
    b, ev = UCB(), UEB()
    PV.index(b, ev, "Harness info, line")
    ix_exp = expected(ix, SUI, "Harness info, line")
    compare(cmds(b), ix_exp, "C. index: exactly the dumped %d appends + %d b.set lines + the Info line" % (len(ix["appends"]), len(ix["sets"])))
    want_ev = [("Activating", sel, {"a": act}) for sel, act in ix["binds"]]
    check(evs(ev) == want_ev and len(want_ev) == len(order) + 1, "C. index bindings: %d Open (open:<n>, list order) + Close" % len(order))
    check([a["a"] for _t, _s, a in want_ev][:-1] == ["open:%d" % n for n in order], "C. the Open bindings follow the list order")
    print("C. %d views + the index rendered through the engine builders (grid views: %s)" % (len(order), grid_views))

    # ---------------- E. ProbePage.build
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def field(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UUID = JClass("java.util.UUID")
    PAGE = JClass(PKG + "ProbePage")
    foot_ev = [("Activating", foot[0], {"a": "back"}), ("Activating", foot[1], {"a": "close"})]

    # harness classes (javassist, written to the scratch class folder; never in the jar)
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(JAR)
    CtNewMethod, CtNewConstructor, CtField = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")
    hp = CP.makeClass("skyyuiprobeharness.HarnessPage", CP.get(PKG + "ProbePage"))
    for fsrc in ("public int rebuilds;", "public int built;", "public int closes;", "public java.lang.Object lastCmds;",
                 "public java.lang.Object lastEvents;"):
        hp.addField(CtField.make(fsrc, hp))
    hp.addConstructor(CtNewConstructor.make(
        "public HarnessPage(com.hypixel.hytale.server.core.universe.PlayerRef pr, int v) { super(pr, v); }", hp))
    hp.addMethod(CtNewMethod.make(
        "public void rebuild() {\n"
        "  com.hypixel.hytale.server.core.ui.builder.UICommandBuilder b = new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder();\n"
        "  com.hypixel.hytale.server.core.ui.builder.UIEventBuilder ev = new com.hypixel.hytale.server.core.ui.builder.UIEventBuilder();\n"
        "  this.rebuilds++;\n"
        "  build((com.hypixel.hytale.component.Ref) null, b, ev, (com.hypixel.hytale.component.Store) null);\n"
        "  this.built++;\n"
        "  this.lastCmds = b.getCommands();\n"
        "  this.lastEvents = ev.getEvents();\n}", hp))
    hp.addMethod(CtNewMethod.make("public void close() { this.closes++; }", hp))
    hp.writeFile(hcls)
    net = CP.makeClass("skyyuiprobeharness.HarnessNet", CP.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    net.addField(CtField.make("public java.util.ArrayList sent;", net))
    net.addConstructor(CtNewConstructor.make(
        "public HarnessNet() { super((com.hypixel.hytale.protocol.io.ChannelConnection) null, (com.hypixel.hytale.server.core.io.ProtocolVersion) null); }", net))
    net.addMethod(CtNewMethod.make(
        "public boolean writePacket(com.hypixel.hytale.protocol.ToClientPacket p, boolean c) {\n"
        "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  this.sent.add(p);\n  return true;\n}", net))
    net.addMethod(CtNewMethod.make("public void accept(com.hypixel.hytale.protocol.ToServerPacket p) { }", net))
    net.addMethod(CtNewMethod.make("public String getIdentifier() { return \"harness\"; }", net))
    net.writeFile(hcls)
    ctl = CP.makeClass("skyyuiprobeharness.HarnessCtl", CP.get("com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"))
    ctl.addConstructor(CtNewConstructor.make(
        "public HarnessCtl() { super(\"harnessctl\", \"control\"); requirePermission(\"harness.ctl\"); "
        "setPermissionGroups(new String[] { \"hytale:Adventurer\" }); }", ctl))
    ctl.addMethod(CtNewMethod.make(
        "protected void execute(com.hypixel.hytale.server.core.command.system.CommandContext ctx, com.hypixel.hytale.component.Store s, "
        "com.hypixel.hytale.component.Ref r, com.hypixel.hytale.server.core.universe.PlayerRef p, "
        "com.hypixel.hytale.server.core.universe.world.World w) { }", ctl))
    ctl.writeFile(hcls)
    HP, NET = JClass("skyyuiprobeharness.HarnessPage"), JClass("skyyuiprobeharness.HarnessNet")

    def pref(name, u):
        p = U.allocateInstance(PR.class_)
        field(PR, "uuid").set(p, u)
        field(PR, "username").set(p, name)
        h = U.allocateInstance(NET.class_)
        field(PR, "packetHandler").set(p, h)
        return p, h

    ME, MYNET = pref("ProbeTester", UUID.fromString("00000000-0000-0000-0000-0000000000a1"))

    def chats(h):
        out = []
        if h.sent is not None:
            for i in range(h.sent.size()):
                pk = h.sent.get(i)
                msg = getattr(pk, "message", None)
                out.append(str(msg.rawText) if msg is not None and msg.rawText is not None else str(pk))
        return out

    for n in order:
        pg = PAGE(ME, n)
        b, ev = UCB(), UEB()
        thrown = None
        try:
            pg.build(None, b, ev, None)
        except Exception as ex:
            thrown = ex
        got_r, thr_r = rendered[n]
        if n in grid_views and thrown is not None:
            check(grid_throw(thrown) and cmds(b) == got_r, "E. ProbePage(%d).build = the view up to its grid fill" % n)
        else:
            check(thrown is None and cmds(b) == got_r, "E. ProbePage(%d).build sends exactly probe %d (%s)" % (n, n, thrown))
            check(evs(ev) == foot_ev, "E. ProbePage(%d).build binds only Back / Close: %s" % (n, evs(ev)))
    for v in (0, 99, -1, PAGE_COUNT + 1):
        pg = PAGE(ME, v)
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        compare(cmds(b), expected(ix, SUI, str(PAGE.lastText(v))), "E. ProbePage(%d).build falls back to the index (Info = lastText)" % v)
        check(evs(ev) == want_ev, "E. ProbePage(%d) index bindings" % v)
    check(str(PAGE.lastText(0)) == dump["first_txt"] and str(PAGE.lastText(0)).startswith("Nothing opened yet - start with base1, base2, "
                                                                                           "base3, then base4"),
          "E. lastText(0) = %r" % str(PAGE.lastText(0)))
    for n in order:
        t, nxt = str(PAGE.lastText(n)), (order + [-1])[order.index(n) + 1]
        want = "Last opened: probe %d (%s). Did it look right? " % (n, dump["names"][str(n)]) + (
            "Next: probe %d (%s)." % (nxt, dump["names"][str(nxt)]) if nxt > 0 else "That was the last one.")
        check(t == want and "<" not in t and ">" not in t, "E. lastText(%d) = %r (got %r)" % (n, want, t))
        check(t == dump["last_txts"][str(n)], "E. lastText(%d) = the build's last_text (the text the build measured)" % n)
    # every runtime Info text fits the Info label (bold, info_fs px, the index inner width, fit_margin px kept free)
    iw, ifs, fm = int(dump["info_w"]), int(dump["info_fs"]), int(dump["fit_margin"])
    infos = [str(PAGE.lastText(0))] + [str(PAGE.lastText(n)) for n in order] + [
        "Probe %d could not be built - see the server log." % n for n in order]
    widest = max(SUI.text_width(t, ifs, bold=True) for t in infos)
    check(widest + fm <= iw, "E. every Info text (%d: lastText of 0 and each page, each failure line) fits the Info label "
                             "(widest %.0f + %d <= %d px at %d px bold)" % (len(infos), widest, fm, iw, ifs))
    print("E. ProbePage.build done (widest Info text %.0f of %d px)" % (widest, iw))

    # ---------------- K. clicks (engine-like rebuild; chat recorded)
    def state(p):
        return (int(p.view), str(p.info), int(p.rebuilds), int(p.closes), len(chats(MYNET)))

    def click(p, data):
        try:
            p.handleDataEvent(None, None, data)
            return None
        except Exception as ex:
            return ex

    pg = HP(ME, 0)
    check(int(pg.view) == 0 and str(pg.info) == str(PAGE.lastText(0)), "K. a new page: view 0, Info = lastText(0)")
    n5 = 5 if 5 in views and 5 not in grid_views else [n for n in order if n not in grid_views][2]
    check(click(pg, '{"a":"open:%d"}' % n5) is None, "K. open:%d does not throw" % n5)
    check(int(pg.view) == n5 and int(pg.rebuilds) == 1 and str(pg.info) == str(PAGE.lastText(n5)), "K. open:%d -> view %d, one rebuild" % (n5, n5))
    check(pg.lastCmds is not None and [(str(c.type), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                                        None if c.text is None else str(c.text)) for c in pg.lastCmds] == rendered[n5][0],
          "K. the rebuild sent probe %d" % n5)
    check([(str(e.type), str(e.selector), json.loads(str(e.data))) for e in pg.lastEvents] == foot_ev, "K. ... with only Back / Close bound")
    check(click(pg, '{"a": "back"}') is None and int(pg.view) == 0 and int(pg.rebuilds) == 2, "K. back -> the index, one rebuild")
    ixc = [(str(c.type), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
            None if c.text is None else str(c.text)) for c in pg.lastCmds]
    info_lines = [json.loads(d)["0"] for t, s, d, x in ixc if s == ix["info"][0] + ".Text"]
    check(info_lines == [str(PAGE.lastText(n5))] and ("Last opened: probe %d (%s)" % (n5, dump["names"][str(n5)])) in info_lines[0],
          "K. the index after Back shows 'Last opened: probe %d (...)': %s" % (n5, info_lines))
    compare(ixc, expected(ix, SUI, str(PAGE.lastText(n5))), "K. the index after Back = the dumped index")
    # a stale / double back (the page is already on the index; 0.2 review): the index is re-sent, the Info line is KEPT
    before = state(pg)
    check(click(pg, '{"a":"back"}') is None and int(pg.view) == 0 and str(pg.info) == str(PAGE.lastText(n5))
          and int(pg.rebuilds) == before[2] + 1 and int(pg.closes) == before[3],
          "K. a second (stale) back: still the index view, Info kept %r, one rebuild (got view %d, %r)" % (
              str(PAGE.lastText(n5)), int(pg.view), str(pg.info)))
    check([(str(c.type), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
            None if c.text is None else str(c.text)) for c in pg.lastCmds] == ixc,
          "K. ... it re-sent exactly the same index (Info 'Last opened: probe %d ...')" % n5)
    check(len(chats(MYNET)) == 0, "K. no chat line so far")
    # a probe whose build throws inside rebuild (18 in a bare JVM: its grid fill)
    for gv in grid_views:
        before = state(pg)
        built0 = int(pg.built)
        ex = click(pg, '{"a":"open:%d"}' % gv)
        check(ex is None, "K. open:%d never throws out of handleDataEvent (%s)" % (gv, ex))
        if int(pg.built) == built0 + 1:
            print("   note: probe %d built in this JVM (asset store present?) - the failure path is not exercised" % gv)
            check(int(pg.view) == gv, "K. open:%d built -> view %d" % (gv, gv))
            check(int(pg.rebuilds) == before[2] + 1, "K. open:%d rebuilt once" % gv)
            click(pg, '{"a":"back"}')
            continue
        c = chats(MYNET)
        want = "[SkyyUiProbe] Probe %d (%s) could not be built - see the server log." % (gv, dump["names"][str(gv)])
        check(int(pg.view) == 0, "K. open:%d fails to build -> the page is back on the index view" % gv)
        check(str(pg.info) == "Probe %d could not be built - see the server log." % gv, "K. ... Info = %r" % str(pg.info))
        check(int(pg.rebuilds) == before[2] + 1, "K. ... exactly one rebuild (the failed one), none from the catch (%d)" % (int(pg.rebuilds) - before[2]))
        check(len(c) == before[4] + 1 and c[-1] == want, "K. ... one chat line %r (got %s)" % (want, c[before[4]:]))
        check([(str(x.type), None if x.selector is None else str(x.selector), None if x.data is None else str(x.data),
                None if x.text is None else str(x.text)) for x in pg.lastCmds] == ixc, "K. ... nothing new was sent (the last page stays the index)")
        fail_info = "Probe %d could not be built - see the server log." % gv
        check(click(pg, '{"a":"back"}') is None and int(pg.view) == 0 and str(pg.info) == fail_info and len(chats(MYNET)) == before[4] + 1,
              "K. ... a stale back after the failure keeps the failure Info line, no chat (got %r)" % str(pg.info))
        sent_info = [json.loads(str(x.data))["0"] for x in pg.lastCmds
                     if x.selector is not None and str(x.selector) == ix["info"][0] + ".Text"]
        check(sent_info == [fail_info], "K. ... and the re-sent index shows it: %s" % sent_info)
        check(click(pg, '{"a":"open:%d"}' % n5) is None and int(pg.view) == n5, "K. ... and the next Open works (open:%d)" % n5)
        click(pg, '{"a":"back"}')
        check(int(pg.view) == 0 and len(chats(MYNET)) == before[4] + 1, "K. ... back, no further chat line")
    # malformed input: never a state change, never a throw
    for bad in ['{"a":"open:abc"}', '{"a":"open:99"}', '{"a":"open:"}', '{"a":"open:-3"}', '{"a":"open:0"}', '{"a":"open: 3"}',
                '{"b":"open:3"}', '{"a":5}', '{"a":"nonsense"}', '}{', '', '{"a":"', '"a"', None, '{"a":"open:99999999999"}']:
        before = state(pg)
        ex = click(pg, bad)
        check(ex is None and state(pg) == before, "K. malformed %r: no throw, no state change" % (bad,))
    check(click(pg, '{"a":"open:\\u0032"}') is None and int(pg.view) == 2, "K. an escaped \\u0032 opens probe 2 (jsonStr decodes it)")
    check(click(pg, '{"a":"close"}') is None and int(pg.closes) == 1 and int(pg.view) == 2, "K. close on a probe page -> close(), view kept")
    click(pg, '{"a":"back"}')
    check(click(pg, '{"a":"close"}') is None and int(pg.closes) == 2 and int(pg.view) == 0, "K. close on the index -> close()")
    print("K. clicks done (%d chat line(s): %s)" % (len(chats(MYNET)), chats(MYNET)))

    # ---------------- L. the log order (bytecode)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cls, meth):
        for mm in CP.get(PKG + cls).getDeclaredMethods():
            if str(mm.getName()) == meth:
                bos = BOS()
                IP(PS(bos)).print_(mm)
                return str(bos.toString())
        return ""

    def pos(txt, needle):
        return txt.find(needle)

    h = code("ProbePage", "handleDataEvent")
    op = pos(h, "opening probe ")
    check(0 <= op < h.find(".rebuild(", op) < pos(h, "sent probe "),
          "L. click: 'opening probe' logged before the open's rebuild(), 'sent probe' after")
    check(h.count(".rebuild(") == 2, "L. handleDataEvent calls rebuild() exactly twice (back, open) - none in the catch")
    o = code("ProbeCmds", "open")
    check(0 <= pos(o, "opening probe ") < pos(o, "openCustomPage") < pos(o, "sent probe "),
          "L. /skyprobe n: 'opening probe' logged before openCustomPage, 'sent probe' after")
    f = code("ProbeViews", "find")
    check("java.util.Locale.ROOT" in f and "toLowerCase(()" not in f, "L. find() lower-cases with Locale.ROOT only")
    print("L. log order done")

    # ---------------- P. permissions (the engine's own code)
    PM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
    HashSet, HashMap, ArrayList = JClass("java.util.HashSet"), JClass("java.util.HashMap"), JClass("java.util.ArrayList")

    def jset(*xs):
        s = HashSet()
        for x in xs:
            s.add(x)
        return s

    try:
        own = U.allocateInstance(JClass("com.hypixel.hytale.server.core.command.system.CommandManager").class_)
    except Exception as ex:
        own = None
        print("   no CommandManager owner (%s)" % ex)
    cmd, cc = JClass(PKG + "SkyProbeCmd")(), JClass("skyyuiprobeharness.HarnessCtl")()
    vf = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand").class_.getDeclaredField("variantCommands")
    vf.setAccessible(True)
    vm = vf.get(cmd)
    var = vm.get(JInt(1)) if vm is not None else None
    for c_ in (cmd, var, cc):
        if c_ is not None and own is not None:
            c_.setOwner(own)
    check(var is not None and str(var.getClass().getSimpleName()) == "SkyProbeArgCmd", "P. /skyprobe <page> is the usage variant SkyProbeArgCmd: %s" % vm)
    subs = cmd.getSubCommands()
    check(subs is None or subs.size() == 0, "P. /skyprobe has no sub-commands (only the variant)")
    for c_, what in ((cmd, "/skyprobe"), (var, "/skyprobe <page>")):
        if c_ is None:
            continue
        g = c_.getPermissionGroups()
        check(str(c_.getPermission()) == NODE and g is not None and len(g) == 0, "P. %s: requirePermission %s + setPermissionGroups(new String[0])" % (what, NODE))
    try:
        al = sorted(str(x) for x in cmd.getAliases()) if cmd.getAliases() is not None else []
    except Exception as ex:
        al = ["? %s" % ex]
    check(str(cmd.getName()) == "skyprobe" and al == ["uiprobe"], "P. /skyprobe, alias /uiprobe: %s" % al)
    m = cmd.getPermissionGroupsRecursive()
    check(m.size() == 0, "P. /skyprobe + its variant put %s into NO permission group: %s" % (NODE, m))
    mc = cc.getPermissionGroupsRecursive()
    check(mc.size() == 1 and "harness.ctl" in [str(x) for x in mc.get("hytale:Adventurer")], "P. control: HarnessCtl gives harness.ctl to hytale:Adventurer: %s" % mc)
    USERS = {"plain": ([], ["hytale:Adventurer"]), "op": ([], ["hytale:Admin"]), "holder": ([NODE], ["hytale:Adventurer"]),
             "skyystar": (["skyy.*"], ["hytale:Adventurer"]), "hytalestar": (["hytale.*"], ["hytale:Adventurer"]),
             "cmdstar": (["hytale.command.*"], ["hytale:Adventurer"])}
    IDS = dict((k, UUID.fromString("00000000-0000-0000-0000-%012d" % (i + 1))) for i, k in enumerate(sorted(USERS)))
    BY_ID = dict((str(v), k) for k, v in IDS.items())
    GROUPS = {"hytale:Admin": ["*"], "hytale:Adventurer": []}

    @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
    class Prov:
        @JOverride
        def getName(self): return "uiprobe-test"
        @JOverride
        def getUserPermissions(self, u): return jset(*USERS.get(BY_ID.get(str(u)), ([], []))[0])
        @JOverride
        def getGroupsForUser(self, u): return jset(*USERS.get(BY_ID.get(str(u)), ([], []))[1])
        @JOverride
        def getGroupPermissions(self, g): return jset(*GROUPS.get(str(g), []))
        @JOverride
        def getEffectiveGroupPermissions(self, g): return jset(*GROUPS.get(str(g), []))
        @JOverride
        def getGroupParent(self, g): return None
        @JOverride
        def getAllRegisteredGroups(self): return jset(*GROUPS.keys())
        @JOverride
        def getUsersWithPermission(self, n): return HashSet()
        @JOverride
        def addUserPermissions(self, *a): return None
        @JOverride
        def removeUserPermissions(self, *a): return None
        @JOverride
        def addUserToGroup(self, *a): return None
        @JOverride
        def addGroupPermissions(self, *a): return None
        @JOverride
        def removeGroupPermissions(self, *a): return None
        @JOverride
        def removeUserFromGroup(self, *a): return None
        @JOverride
        def setUserGroup(self, *a): return None

    pm = U.allocateInstance(PM.class_)
    provs = ArrayList()
    provs.add(Prov())
    field(PM, "providers").set(pm, provs)
    virt = HashMap()
    for mp in (m, mc):
        for k in mp.keySet():
            s = virt.get(k)
            if s is None:
                s = HashSet()
                virt.put(k, s)
            s.addAll(mp.get(k))
    field(PM, "virtualGroups").set(pm, virt)
    f_inst = field(PM, "instance")
    old_pm = f_inst.get(None)
    f_inst.set(None, pm)

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
    class Sender(object):
        def __init__(self, who):
            self.who = who

        @JOverride
        def hasPermission(self, *a):
            q = a[0]
            n = str(q) if isinstance(q, str) else str(q.getId())
            return bool(PM.get().hasPermission(IDS[self.who], n))

        @JOverride
        def getUsername(self):
            return self.who

        @JOverride
        def getUuid(self):
            return IDS[self.who]

        @JOverride
        def sendMessage(self, msg):
            pass

    try:
        for who, may in (("plain", False), ("skyystar", False), ("hytalestar", False), ("cmdstar", False), ("op", True), ("holder", True)):
            check(bool(PM.get().hasPermission(IDS[who], NODE)) == may, "P. PermissionsModule.hasPermission(%s, %s) = %s" % (who, NODE, may))
            s = Sender(who)
            check(bool(cmd.hasPermission(s)) == may and (var is None or bool(var.hasPermission(s)) == may),
                  "P. AbstractCommand.hasPermission: /skyprobe and /skyprobe <page> %s for %s" % ("allowed" if may else "refused", who))
        check(bool(cc.hasPermission(Sender("plain"))) and bool(PM.get().hasPermission(IDS["plain"], "harness.ctl")),
              "P. control: the plain player IS granted a node a command gives to hytale:Adventurer (the check can see a leak)")
    finally:
        f_inst.set(None, old_pm)
    print("P. permissions done")

    # ---------------- M. the jar
    z = zipfile.ZipFile(JAR)
    man = json.loads(z.read("manifest.json").decode("utf-8"))
    check(man.get("Main") == PKG + "SkyyUiProbePlugin" and man.get("IncludesAssetPack") is False and str(man.get("Version")) == VERSION,
          "M. manifest: Main, Version %s, IncludesAssetPack false: %s" % (VERSION, dict((k, man.get(k)) for k in ("Main", "Version", "IncludesAssetPack"))))
    check(not any(n.lower().endswith(".ui") for n in z.namelist()), "M. no .ui file in the jar")
    plug = z.read("com/skyy/uiprobe/SkyyUiProbePlugin.class")
    z.close()
    ready = "[SkyyUiProbe] %s ready - /skyprobe (admin): " % VERSION
    check(ready.encode() in plug and b" probe pages (kit " in plug and int(PV.count()) == PAGE_COUNT,
          "M. the ready line text is in SkyyUiProbePlugin (%d probe pages)" % int(PV.count()))
    print("M. ready line: %s%d probe pages (kit %s)" % (ready, int(PV.count()), PL.kit()))


def main():
    if not os.path.isfile(JAR):
        raise SystemExit("no jar at %s - build first: python SkyyUiProbe/build_skyyuiprobe_%s.py" % (JAR, VERSION))
    claim_scratch()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    os.environ["TEMP"] = tmp
    os.environ["TMP"] = tmp
    try:
        run()
    except SystemExit as e:
        FAILS.append(str(e))
    finally:
        print("SkyyUiProbe %s harness: %d ok, %d fail" % (VERSION, OKS[0], len(FAILS)))
        for f in FAILS:
            print("  FAIL", f)
        if not KEEP:
            try:
                import jpype
                if jpype.isJVMStarted():
                    jpype.shutdownJVM()
            except Exception as e:
                print("JVM shutdown: %s" % e)
            if under_scratch(SCRATCH) and os.path.isfile(MARK):      # claim_scratch() made and marked it
                shutil.rmtree(SCRATCH, ignore_errors=True)
            print("scratch folder %s" % ("removed" if not os.path.exists(SCRATCH) else "NOT fully removed - delete it by hand"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
