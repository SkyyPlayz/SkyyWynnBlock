"""Bare-JVM check for SkyyUiProbe 0.3 (made from test_skyyuiprobe_0.2.py; kept next to the build so the build report's JVM claims
can be re-run).

    python SkyyUiProbe/test_skyyuiprobe_0.3.py [--jar <SkyyUiProbe-0.3.jar>] [--dir <scratch folder>] [--keep]

Build the jar first (python SkyyUiProbe/build_skyyuiprobe_0.3.py). Re-run this after every build AND whenever tools/skyyui.py changes
(its kit id): the probe pages come from the kit, so a kit change can change what the pages send.
  D  the expected page commands: runs the build script with --dump-only <scratch>/dump.json (a subprocess: SUI.verify() + the page
     proofs, no JVM, no class / jar written) and refuses a jar built with another kit id (ProbeLog.kit())
  A  every class of the jar loads and verifies (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the jar)
  S  the dump itself: 24 views = kit pages 1-22 + window probes 23 / 24; every page (with its footer) and the index (with its runtime
     Info line) pass SUI.check_page; the index passes SUI.assert_proven with nothing allowed and carries no texture / sound / FontName /
     FlexWeight / Wrap / LetterSpacing / LayoutMode other than Top / Left / Anchor margin; kit pages pass SUI.assert_proven with only
     their own key allowed, window pages with NOTHING allowed and no InventorySectionId in any markup; no underscore ids, every page
     root <= 980 px high (Width / Height only), the flat Back / Close footer is the last 4 appends of every probe page; the index: two
     columns of 12 in the list order, win + secgrid first with green Open buttons, the "New in 0.3: open win (23), then secgrid (24)"
     line at the top; its b.set texts hold no < or > (proven inline only) and no builder names
  B  ProbeViews: count / order / names / keys / summaries match the build and fit their index label (SUI.text_width); nextOf();
     isWin(); find() for numbers, names (win, secgrid), "#3", junk, null - and upper-case names under a Turkish default locale
  C  every view through the ENGINE's UICommandBuilder / UIEventBuilder (ProbeViews.render / renderWin / index): exactly the dumped
     appends + b.set lines + extra Java lines; grid fills run for real (a stand-in item asset store: every id is Item.UNKNOWN, as the
     SkyyVault / SkyyGear harnesses do) - page 18's 4 items, probe 23's 3 arrow slots (the vanilla stand-in ids, since the stand-in
     store knows no SkyyVault item; name, description, activatable checked in the Slots JSON); probe 24 sends NO Slots; every grid
     item id is in Assets.zip (read-only) or in the SkyyVault 0.1.5 jar's asset pack
  E  ProbePage.build: views 1-22 send their page + bind only Back / Close; 23 / 24 WITH an open session send their page + Back /
     Close (+ the arrow SlotClicking on 23); 23 / 24 WITHOUT a session fall back to the index with "Probe 23 needs its window ..."; 0 /
     unknown views send the index; lastText() / noWinText() = the build's texts, every Info text fits the Info label
  K  clicks through ProbePage.handleDataEvent on a harness subclass whose rebuild() does what the engine's does: 0.2's open / back /
     close / stale back / malformed input / failed build cases, plus: arrow clicks on 23 (one chat line each, SlotIndex 0-2; a bad
     index one hint line; arrows on other views ignored), Back on a window view (the list first, then the session ends with the
     admin's items kept in the box - no player component in a bare JVM), open:23 / open:24 from the index (no player component:
     one chat line, the index view stays, nothing rebuilt)
  W  THE WINDOW PROBE LOGIC with the engine's own container code: ProbeBox.make (3 probe items in slots 0-2, armed); every gesture the
     client can send for a window slot, as InventoryPacketHandler calls it - drag (moveItemStackFromSlotToSlot) in every direction,
     onto / off a probe item, swap, inside the box; shift-click (whole-slot moveItemStackFromSlot, single target and the ListTransaction
     form - a refused probe slot answers a failed transaction, never null / an NPE); the Drop key (removeItemStackFromSlot); Take All
     (whole-slot moves into the inventory); Put All (moveAllItemStacksTo); Quick Stack (quickStackTo); double-click merge
     (combineItemStacksIntoSlot both ways); Sort (NAME, TYPE - RARITY needs the quality asset store); a stack with a probe item's
     id from outside - after EVERY gesture:
     item totals per id (box + stand-in inventory) unchanged, the 3 probe items still in the box, none outside. returnTo (all fits /
     inventory full / nothing own / inventory unreadable), counts / diff / total / countLine, the box change listener (ProbeChange ->
     noteChange: the transaction name, no count queued without a world), the client packet log (describe() for all 8 packet types +
     the engine's own PacketAdapters.__handleInbound with a stand-in GamePacketHandler: logged for an open session, silent without
     one or 5 s after the close, never blocks the packet; ensureNet / stopNet register and remove exactly one inbound filter), the
     session life cycle (windowClosed: once, listener removed, return skipped while the next probe shows the box; dismissed / lateClose
     without a world; closeNow without a player ends the session and keeps the items), the re-send after client packets
     (ProbeWindow.validate always true, nothing queued without a world / for a closed session; syncNow without a player reference
     does nothing), ProbeWin.shutdown lists a box's leftovers
  L  bytecode order: "opening probe" before rebuild / openCustomPage(WithWindows), "sent probe" after; ProbeWin.open: the
     InventorySectionId update after openCustomPageWithWindows, the previous window closed only after the new page; closeNow asks
     getWindow before closeWindow; syncNow re-sends the window before marking the inventory; ProbeWindow.resend calls invalidate and
     ProbeWindow is a ValidatedWindow; ProbeBox overrides the 5 container checks with the engine's signatures
  P  permissions with the engine's own code: /skyprobe and its usage variant hold skyyuiprobe.admin with empty permission-group lists,
     getPermissionGroupsRecursive() gives the node to no group; a real PermissionsModule object (never set up) with one fake provider
     + those virtual groups answers AbstractCommand.hasPermission: plain Adventurer, skyy.*, hytale.*, hytale.command.* refused; op
     ("*") and a node holder pass; control: a command listing hytale:Adventurer IS granted to the same plain player
  M  the jar: manifest (Main, Version 0.3, IncludesAssetPack false), exactly the 16 classes, no .ui file, the ready line's text
  REVIEW FIXES (2026-10-02 review of 0.3) - checks that fail on the first 0.3 jar / build:
  1  the re-send gate, with a recording stand-in World (HarnessWorld: execute / scheduleAfter are recorded, run by hand): 100
     validate() calls without a client packet for the window (movement ticks) queue NOTHING; a MoveItemStack into the window through the
     engine's PacketAdapters stamps the session and 30 validate() calls then queue exactly ONE ProbeSyncTask, 100 ms later; the stamp is
     used up; a second / third packet while one waits; a move between the player's own sections; a stale stamp (> 1.5 s); a world that
     refuses tasks; the no-watcher fallback (one per 250 ms); wantsResend() for 16 packet shapes; wantSync() edge cases; bytecode:
     touched() = wantSync + World.scheduleAfter, never World.execute; packet() stamps before it logs
  3  Close on a window view: the page closes once, the session is detached and the window closed in the same click ("Close button"),
     the onDismiss that follows schedules NO 1.5 s check (control: Esc / onDismiss with the session DOES); bytecode order close() ->
     ProbeWin.closeNow
  4  windowClosed / endQuiet / the same-box path / ProbeWindow.onClose0 let go of window / player / listener / world / store (box, owner,
     id, name, closedAt stay), release() on an open session is a no-op; a session past the 5 s grace leaves SESS on the next packet;
     bytecode: closedAt written before the volatile closed flag
  5 / 7 / 8  the page texts: bread or stone (not an iron mace, helmet or shovel), "No inventory showing? Say so.", "if the buttons do
     nothing, press Esc"; every check still <= 2 lines, the note one caption line
  6  the count-changed chat line names a bag sweep / refill
  A crash (e.g. a jar without a member a check reads) is reported as a FAIL.
Not testable without the game (UNVERIFIED): how the client draws each page (that is what the mod is for), whether it draws the window
next to a custom page, InventorySectionId on a window section, the real PageManager / WindowManager / CommandManager dispatch.
Nothing is deployed. Default scratch folder: tools/dev/scratch/uiprobe03-test (deleted at the end unless --keep); TEMP / TMP and
java.io.tmpdir point into it. --dir must name a folder INSIDE tools/dev/scratch that is new, empty or an earlier run's (it carries the
harness's marker file): anything else is refused before the run, so the end-of-run delete can only remove a folder this harness made.
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.3"
PAGE_COUNT = 24
KIT_COUNT = 22
WIN_VIEWS = [23, 24]
PKG = "com.skyy.uiprobe."
BUILD = os.path.join(HERE, "build_skyyuiprobe_%s.py" % VERSION)
NODE = "skyyuiprobe.admin"
CLASSES = ["ProbeLog", "ProbeViews", "ProbeSession", "ProbeBox", "ProbeWindow", "ProbeChange", "ProbeCountTask", "ProbeCloseTask",
           "ProbeSyncTask", "ProbeNet", "ProbePage", "ProbeWin", "ProbeCmds", "SkyProbeArgCmd", "SkyProbeCmd", "SkyyUiProbePlugin"]
VAULT_JAR = os.path.join(ROOT, "SkyyVault", "SkyyVault-0.1.5.jar")     # the SET pin: its asset pack ships the Skyy_Vault_* arrow items


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.join(TOOLS, "dev", "scratch")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "uiprobe03-test")))
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
WIN_SLOTS_SET = re.compile(r'^\s*b\.set\("(#[^"]+\.Slots)",\s*pbArrowSlots\);\s*$')


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


def win_extras(view):
    """(expected extra commands, unknown lines) of a window probe view: probe 23's arrow fill (the exact lines the build writes),
    probe 24: none."""
    exp, unknown = [], []
    for l in view.get("extra", []):
        m = WIN_SLOTS_SET.match(l)
        if m:
            exp.append(("Set", m.group(1), "<grid slots>"))
            continue
        if re.match(r"^\s*(java\.util\.ArrayList pbArrowSlots = new java\.util\.ArrayList\(\);|String\[\] pbAid = @PKG@\.ProbeViews\."
                    r"arrowIds\(\);|String\[\] pbAnm = @PKG@\.ProbeViews\.arrowNames\(\);|for \(int i = 0; i < pbAid\.length; i\+\+\) \{|"
                    r"@IGS@ pbG = new @IGS@\(new @IS@\(pbAid\[i\], 1\)\);|pbG\.setName\(pbAnm\[i\]\);|pbG\.setDescription\(\"[^\"]*\"\);|"
                    r"pbG\.setActivatable\(true\);|pbArrowSlots\.add\(pbG\);|\})\s*$", l):
            continue
        unknown.append(l)
    return exp, unknown


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
    from jpype import JClass, JImplements, JOverride, JInt, JString, JShort, JArray, JByte
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
    check(names == sorted(PKG + c for c in CLASSES), "A. the jar holds exactly the %d classes: %s" % (len(CLASSES), names))
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return
    PV, PL = JClass(PKG + "ProbeViews"), JClass(PKG + "ProbeLog")
    check(str(PL.kit()) == dump["kit"], "D. the jar was built with this kit (%s, jar %s) - rebuild the jar" % (dump["kit"], PL.kit()))
    if FAILS:
        return

    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def jf(jcls, name):
        c = jcls
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    def field(cls, name):
        return jf(cls.class_, name)

    # harness classes (javassist, written to / defined next to their engine class; never in the jar)
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(JAR)
    CtNewMethod, CtNewConstructor, CtField = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")

    def fake(name, sup, ctor, neighbor):
        """a stand-in subclass of an engine class, defined next to it; never constructed (Unsafe.allocateInstance)"""
        c = CP.makeClass(name, CP.get(sup))
        c.addConstructor(CtNewConstructor.make(ctor, c))
        return c.toClass(neighbor)

    # the item asset store: an empty map (Item.UNKNOWN for every id) so ItemStack constructors run (the SkyyVault / SkyyGear pattern)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    FS = fake("com.hypixel.hytale.assetstore.SkyyUiProbeTestAssets", "com.hypixel.hytale.assetstore.AssetStore",
              "public SkyyUiProbeTestAssets() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", AS.class_)
    st0 = U.allocateInstance(FS)
    jf(AS.class_, "assetMap").set(st0, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())
    jf(JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_, "ASSET_STORE").set(None, st0)
    ISC = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    check(str(ISC("Food_Bread", 3).getItemId()) == "Food_Bread", "A. the stand-in item asset store lets new ItemStack(id, qty) run")

    # ---------------- S. the dump itself
    order = [int(x) for x in dump["order"]]
    views = dict((n, dump[str(n)]) for n in order)
    foot = dump["foot"]
    check(sorted(order) == list(range(1, PAGE_COUNT + 1)), "S. %d views = probe pages 1-%d: %s" % (PAGE_COUNT, PAGE_COUNT, sorted(order)))
    kit_pages = SUI.probe_pages("SkyyPb")
    check([(p.n, p.name, p.key) for p in kit_pages] == [(n, dump["names"][str(n)], dump["keys"][str(n)]) for n in range(1, KIT_COUNT + 1)],
          "S. views 1-22 are the kit's probe pages (numbers, names, keys)")
    check([dump["names"][str(n)] for n in WIN_VIEWS] == ["win", "secgrid"] and dump["win"]["views"] == WIN_VIEWS,
          "S. views 23 / 24 are the window probes win / secgrid")
    first = list(SUI.PROBE_OPEN_FIRST)
    new = dump["new"]
    check(new == ["win", "secgrid"] and dump["open_first"] == new + first and
          [dump["names"][str(n)] for n in order[:len(new) + len(first)]] == new + first
          and order[len(new) + len(first):] == sorted(order[len(new) + len(first):]),
          "S. list order: win, secgrid, %s first, then by number: %s" % (first, order))

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
        allow = () if n in WIN_VIEWS else (key,)
        try:
            toks = SUI.assert_proven(appends_of(v), allow=allow, what="probe %d" % n)
            ok = True
        except ValueError as ex:
            ok, toks = ex, {}
        check(ok is True, "S. probe %d: SUI.assert_proven with %s allowed (%s)" % (n, list(allow) or "nothing", ok))
        if n in WIN_VIEWS:
            check(all(g is None for g in toks.values()) and toks, "S. window probe %d: every token proven (no probe key needed)" % n)
            check(not any("InventorySectionId" in m for m in mks), "S. window probe %d: no InventorySectionId in the markup" % n)
            check(int(r.group(1)) == dump["win"]["page_w"] if r else False, "S. window probe %d: %s px wide" % (n, dump["win"]["page_w"]))
    w23, w24 = views[23], views[24]
    g23 = [m for _p, m in w23["appends"] if "ItemGrid #SkyyPbWinArrows" in m]
    g24 = [m for _p, m in w24["appends"] if "ItemGrid #SkyyPbSgGrid" in m]
    check(len(g23) == 1 and "SlotsPerRow: 3; AreItemsDraggable: false; InfoDisplay: None;" in g23[0],
          "S. probe 23: one 3-slot arrow grid, not draggable, no tooltips: %s" % (g23[:1],))
    check(len(g24) == 1 and "SlotsPerRow: 9; AreItemsDraggable: true; InfoDisplay: None;" in g24[0],
          "S. probe 24: one 9-slot DRAGGABLE grid (the window section is set after the open): %s" % (g24[:1],))
    check(not any("ItemGrid" in m for _p, m in w24["appends"] if "SkyyPbSgGrid" not in m) and not any(
        "ItemGrid" in m for _p, m in w23["appends"] if "SkyyPbWinArrows" not in m), "S. each window probe has exactly its one grid")
    for n in WIN_VIEWS:
        tx = dump["win"]["texts"][str(n)]
        sets = dict((s[0], s[2]) for s in views[n]["sets"])
        one = [v_ for k, v_ in sets.items() if k.endswith("One")]
        check(len(one) == 1 and one[0] == tx["one"] and "Tell Claude" in one[0], "S. window probe %d: the one line %r" % (n, one[:1]))
        check(SUI.text_width(tx["one"], 16, bold=True) + int(dump["fit_margin"]) <= dump["win"]["page_w"] - 2 * SUI.CONTENT_PAD,
              "S. window probe %d: the one line fits ONE line (%.0f px)" % (n, SUI.text_width(tx["one"], 16, bold=True)))
        checks = [sets.get("SkyyPb%sC%d" % ("Win" if n == 23 else "Sg", i)) for i in range(1, 5)]
        check(checks == tx["checks"] and all(c.startswith("%d. " % (i + 1)) for i, c in enumerate(checks)),
              "S. window probe %d: four numbered checks" % n)
        note = [v_ for k, v_ in sets.items() if k.endswith("Note")]
        check(note == [dump["win"]["note"]], "S. window probe %d: the note line" % n)
    # review fixes 5 / 7 / 8 (the page texts) + the re-send timing of fix 1
    c23, c24 = dump["win"]["texts"]["23"]["checks"], dump["win"]["texts"]["24"]["checks"]
    check("bread or stone (not an iron mace, helmet or shovel - those 3 are locked)" in c23[1],
          "S. review fix 5: probe 23 check 2 names what to drag (bread or stone, not the admin's own iron mace / helmet / shovel, which "
          "share the probe item ids): %r" % c23[1])
    check("bread or stone (not an iron mace, helmet or shovel)" in c24[2], "S. review fix 5: probe 24 check 3 names what to drag: %r" % c24[2])
    check(not any("YOUR items" in c for c in c23 + c24), "S. review fix 5: no check asks for 'one of YOUR items' any more")
    check(c24[2].endswith("No inventory showing? Say so."), "S. review fix 7: probe 24 check 3 asks to say so when no inventory shows: %r" % c24[2])
    check("if the buttons do nothing, press Esc" in dump["win"]["note"],
          "S. review fix 8: the note on both window pages says to press Esc when the buttons do nothing: %r" % dump["win"]["note"])
    for n in WIN_VIEWS:
        tx_ = dump["win"]["texts"][str(n)]["checks"]
        check(all(SUI.text_lines(t, dump["win"]["page_w"] - 2 * SUI.CONTENT_PAD - 4, 16) <= 2 for t in tx_),
              "S. window probe %d: every check line still takes at most 2 lines" % n)
    check(SUI.text_width(dump["win"]["note"], SUI.fs(12)) + int(dump["fit_margin"]) <= dump["win"]["page_w"] - 2 * SUI.CONTENT_PAD,
          "S. the note still fits one caption line (%.0f px)" % SUI.text_width(dump["win"]["note"], SUI.fs(12)))
    SYNC_MS, SAW_MS, RATE_MS = int(dump["win"]["sync_delay_ms"]), int(dump["win"]["saw_ms"]), int(dump["win"]["sync_rate_ms"])
    check((SYNC_MS, SAW_MS, RATE_MS) == (100, 1500, 250), "S. review fix 1: re-send 100 ms after the packet, stamps kept 1.5 s, "
                                                          "fallback one per 250 ms: %s" % ((SYNC_MS, SAW_MS, RATE_MS),))
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
    check(cols.get("SkyyPbIxColA") == order[:per] and cols.get("SkyyPbIxColB") == order[per:] and per == 12
          and len(order) - per == 12, "S. index: two columns of 12 entries in the list order: %s" % cols)
    opens = dict((int(g.group(1)), m) for _p, m in ix["appends"] for g in [re.match(r"TextButton #SkyyPbIxOpen(\d+) \{", m)] if g)
    check(sorted(opens) == sorted(order) and all(("#1f5a34" in opens[n]) == (dump["names"][str(n)] in new) for n in order),
          "S. index: one Open per page, green for %s, blue for the rest" % new)
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
    check(len(sub1) == 1 and sub1[0].startswith("New in 0.3: open win (23), then secgrid (24)"),
          "S. index top line: %r" % (sub1[:1],))
    for ident, prop, val in ix["sets"]:
        t = SUI.render(val) if isinstance(val, str) else str(val)
        check("<" not in t and ">" not in t, "S. index b.set %s: no < or > (%r)" % (ident, t))
        check("Fable" not in t, "S. index b.set %s: no builder name (%r)" % (ident, t))
    check(not any("Fable" in m for _p, m in ix["appends"]), "S. index markup: no builder name")
    for n in WIN_VIEWS:
        for ident, prop, val in views[n]["sets"]:
            check("<" not in val and ">" not in val and "Fable" not in val, "S. window probe %d b.set %s: no < > or builder name" % (n, ident))
    print("S. dump checks done (24 pages + the index through SUI.check_page, assert_proven)")

    # ---------------- B. ProbeViews data + find()
    nm = [str(x) for x in PV.names()]
    check(int(PV.count()) == len(order) and [int(x) for x in PV.order()] == order, "B. count / order = the build's")
    check(all(nm[n] == dump["names"][str(n)] for n in order) and nm[0] == "", "B. names() = the build's")
    ks = [str(x) for x in PV.keys()]
    check(all(ks[n] == dump["keys"][str(n)] for n in order), "B. keys() = the build's")
    kit_by_n = dict((p.n, p) for p in kit_pages)
    for n in order:
        w = str(PV.whatOf(n))
        if n in kit_by_n:
            kp = kit_by_n[n]
            full = SUI.PROBE_SUMMARY.get(kp.name, "")
            ok = w == dump["whats"][str(n)] and (w == kp.summary or (kp.summary.endswith("...") and w == full))
        else:
            ok = w == dump["whats"][str(n)] and len(w) <= 95
        check(ok, "B. probe %d: whatOf = the build's summary line: %r" % (n, w))
        tw = SUI.text_width(w, int(dump["what_fs"]))
        check(len(w) > 0 and tw + int(dump["fit_margin"]) <= int(dump["what_w"]),
              "B. probe %d: the summary fits its index label (%.0f + %s <= %s px at %s px)" % (n, tw, dump["fit_margin"], dump["what_w"],
                                                                                          dump["what_fs"]))
        nw = SUI.text_width(nm[n], int(dump["name_fs"]), bold=True)
        check(nw + int(dump["fit_margin"]) <= int(dump["name_w"]), "B. probe %d: the name fits its label (%.0f px)" % (n, nw))
        check(bool(PV.isWin(n)) == (n in WIN_VIEWS), "B. isWin(%d) = %s" % (n, n in WIN_VIEWS))
    check(not bool(PV.isWin(0)) and not bool(PV.isWin(25)) and not bool(PV.isWin(-23)), "B. isWin of 0 / 25 / -23 = false")
    check(str(PV.nameOf(99)) == "?" and str(PV.keyOf(-1)) == "?" and str(PV.whatOf(0)) == "", "B. nameOf / keyOf / whatOf of a missing page")
    nx = [int(PV.nextOf(n)) for n in order]
    check(nx == order[1:] + [-1] and int(PV.nextOf(0)) == -1 and int(PV.nextOf(99)) == -1, "B. nextOf() follows the list order: %s" % nx)
    idx = dict((dump["names"][str(n)], n) for n in order)
    cases = [("18", 18), ("22", 22), ("19", 19), ("base3", idx.get("base3")), ("base4", 19), ("CHECKBOX", idx.get("checkbox")),
             ("#3", 3), (" 7 ", 7), ("003", 3), ("022", 22), ("0", -1), ("23", 23), ("24", 24), ("25", -1), ("1234", -1), ("abc", -1),
             ("", -1), ("#", -1), ("  ", -1), (None, -1), ("base5", -1), ("TILE", idx.get("tile")), ("Disabled-Prop", idx.get("disabled-prop")),
             ("layout-right", 22), ("Flex-Rows", 21), ("#button-text", 20), ("win", 23), ("secgrid", 24), ("Win", 23), ("#secgrid", 24),
             ("wins", -1), ("sec-grid", -1), (" SecGrid ", 24), ("024", 24)]
    for s, want in cases:
        check(int(PV.find(s)) == want, "B. find(%r) = %s (got %s)" % (s, want, PV.find(s)))
    Locale = JClass("java.util.Locale")
    old = Locale.getDefault()
    try:
        Locale.setDefault(Locale.forLanguageTag("tr-TR"))
        check(str(JString("TILE").toLowerCase()) != "tile", "B. control: under tr-TR the plain toLowerCase() of TILE is not 'tile'")
        for s in ("TILE", "DISABLED-PROP", "ITEMSLOT", "BASE1", "QUALITY-FRAME", "LAYOUT-RIGHT", "BASE4", "BUTTON-TEXT", "WIN", "SECGRID"):
            want = idx.get(s.lower())
            check(want is not None and int(PV.find(s)) == want, "B. tr-TR default locale: find(%r) = %s (got %s)" % (s, want, PV.find(s)))
    finally:
        Locale.setDefault(old)
    av, an = [str(x) for x in PV.arrowIds()], [str(x) for x in PV.arrowNames()]
    check(av == dump["win"]["arrow_ids_vanilla"] and an == dump["win"]["arrow_names"],
          "B. arrowIds(): the vanilla stand-ins when the item store does not know the SkyyVault arrows: %s %s" % (av, an))
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

    def locks(ev):
        return [bool(e.locksInterface) for e in ev.getEvents()]

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

    az = zipfile.ZipFile(os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Assets.zip"))
    items = set(os.path.basename(n)[:-5] for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    az.close()
    vault_items = set()
    if os.path.isfile(VAULT_JAR):
        with zipfile.ZipFile(VAULT_JAR) as vz:
            vault_items = set(os.path.basename(n)[:-5] for n in vz.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    wd = dump["win"]
    check(all(i in items for i in wd["probe_items"]) and all(i in items for i in wd["arrow_ids_vanilla"]),
          "C. the probe items %s and the vanilla arrow stand-ins %s are in Assets.zip" % (wd["probe_items"], wd["arrow_ids_vanilla"]))
    check(all(i in vault_items for i in wd["arrow_ids_vault"]), "C. the SkyyVault arrows %s are in the SkyyVault 0.1.5 jar's asset pack (%s)"
          % (wd["arrow_ids_vault"], VAULT_JAR))
    rendered = {}
    grid_views = []
    for n in order:
        v = views[n]
        base = expected(v, SUI)
        b = UCB()
        thrown = None
        if n in WIN_VIEWS:
            ex_cmds, unknown = win_extras(v)
            check(not unknown, "C. probe %d: every extra Java line is the build's arrow fill: %s" % (n, unknown))
            try:
                r_ = PV.renderWin(b, n)
                check(bool(r_), "C. renderWin(b, %d) answers true" % n)
            except Exception as ex:
                thrown = ex
            got = cmds(b)
            check(thrown is None, "C. window probe %d renders without an exception (%s)" % (n, thrown))
            compare(got, base + ex_cmds, "C. window probe %d: exactly the dumped %d appends + %d b.set lines + %d grid line(s)" % (
                n, len(v["appends"]), len(v["sets"]), len(ex_cmds)))
            if n == 23:
                slots = [json.loads(d)["0"] for t, s, d, x in got if s == "#SkyyPbWinArrows.Slots"]
                txt = json.dumps(slots)
                check(len(slots) == 1 and len(slots[0]) == 3, "C. probe 23: one Slots line with 3 arrow slots: %s" % txt[:300])
                if len(slots) == 1 and len(slots[0]) == 3:
                    for i, sl in enumerate(slots[0]):
                        st_ = json.dumps(sl)
                        check(wd["arrow_ids_vanilla"][i] in st_ and wd["arrow_names"][i] in st_ and wd["arrow_desc"] in st_,
                              "C. probe 23 slot %d: item %s, name %r, the description: %s" % (i, wd["arrow_ids_vanilla"][i], wd["arrow_names"][i], st_[:200]))
                        check("etadata" not in st_ or '"Metadata": null' in st_ or '"metadata": null' in st_,
                              "C. probe 23 slot %d: no item metadata in the grid slot: %s" % (i, st_[:200]))
                    print("   probe 23 arrow slot JSON: %s" % json.dumps(slots[0][0])[:300])
            else:
                check(not any(s and s.endswith(".Slots") for t, s, d, x in got), "C. probe 24 sends no Slots (the client fills it from the section)")
                check(not any(s and "InventorySectionId" in s for t, s, d, x in got), "C. probe 24's build sends no InventorySectionId (set after the open)")
            rendered[n] = (got, thrown)
            continue
        ex_cmds, grid, unknown = extras(v)
        check(not unknown, "C. probe %d: every extra Java line is understood by the harness: %s" % (n, unknown))
        try:
            r_ = PV.render(b, n)
            check(bool(r_), "C. render(b, %d) answers true" % n)
        except Exception as ex:
            thrown = ex
        got = cmds(b)
        if grid is not None:
            grid_views.append(n)
            check(len(grid) > 0 and all(i in items for i, _q in grid), "C. probe %d grid item ids are in Assets.zip: %s" % (n, grid))
            check(thrown is None, "C. probe %d renders with the stand-in item store (%s)" % (n, thrown))
            compare(got, base + ex_cmds, "C. probe %d: appends + b.set lines + the grid Slots line" % n)
        else:
            check(thrown is None, "C. probe %d renders without an exception (%s)" % (n, thrown))
            compare(got, base + ex_cmds, "C. probe %d: exactly the dumped %d appends + %d b.set lines + %d extra line(s)" % (
                n, len(v["appends"]), len(v["sets"]), len(ex_cmds)))
        rendered[n] = (got, thrown)
    check(not bool(PV.render(UCB(), 0)) and not bool(PV.render(UCB(), 99)) and not bool(PV.render(UCB(), -1)) and not bool(PV.render(UCB(), 23)),
          "C. render() of 0 / 99 / -1 / 23 = false")
    check(not bool(PV.renderWin(UCB(), 5)) and not bool(PV.renderWin(UCB(), 0)), "C. renderWin() of 5 / 0 = false")
    b, ev = UCB(), UEB()
    PV.index(b, ev, "Harness info, line")
    ix_exp = expected(ix, SUI, "Harness info, line")
    compare(cmds(b), ix_exp, "C. index: exactly the dumped %d appends + %d b.set lines + the Info line" % (len(ix["appends"]), len(ix["sets"])))
    want_ev = [("Activating", sel, {"a": act}) for sel, act in ix["binds"]]
    check(evs(ev) == want_ev and len(want_ev) == len(order) + 1, "C. index bindings: %d Open (open:<n>, list order) + Close" % len(order))
    check([a["a"] for _t, _s, a in want_ev][:-1] == ["open:%d" % n for n in order], "C. the Open bindings follow the list order")
    print("C. %d views + the index rendered through the engine builders (grid views: %s + window probes)" % (len(order), grid_views))

    # ---------------- E. ProbePage.build
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UUID = JClass("java.util.UUID")
    PAGE = JClass(PKG + "ProbePage")
    SES, BOX, WINC, PW = JClass(PKG + "ProbeSession"), JClass(PKG + "ProbeBox"), JClass(PKG + "ProbeWindow"), JClass(PKG + "ProbeWin")
    foot_ev = [("Activating", foot[0], {"a": "back"}), ("Activating", foot[1], {"a": "close"})]
    arrow_ev = foot_ev + [("SlotClicking", dump["win"]["arrows"], {"a": "arrow"})]

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
    net_ = CP.makeClass("skyyuiprobeharness.HarnessNet", CP.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    net_.addField(CtField.make("public java.util.ArrayList sent;", net_))
    net_.addConstructor(CtNewConstructor.make(
        "public HarnessNet() { super((com.hypixel.hytale.protocol.io.ChannelConnection) null, (com.hypixel.hytale.server.core.io.ProtocolVersion) null); }", net_))
    net_.addMethod(CtNewMethod.make(
        "public boolean writePacket(com.hypixel.hytale.protocol.ToClientPacket p, boolean c) {\n"
        "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  this.sent.add(p);\n  return true;\n}", net_))
    net_.addMethod(CtNewMethod.make("public void accept(com.hypixel.hytale.protocol.ToServerPacket p) { }", net_))
    net_.addMethod(CtNewMethod.make("public String getIdentifier() { return \"harness\"; }", net_))
    net_.writeFile(hcls)
    ctl = CP.makeClass("skyyuiprobeharness.HarnessCtl", CP.get("com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"))
    ctl.addConstructor(CtNewConstructor.make(
        "public HarnessCtl() { super(\"harnessctl\", \"control\"); requirePermission(\"harness.ctl\"); "
        "setPermissionGroups(new String[] { \"hytale:Adventurer\" }); }", ctl))
    ctl.addMethod(CtNewMethod.make(
        "protected void execute(com.hypixel.hytale.server.core.command.system.CommandContext ctx, com.hypixel.hytale.component.Store s, "
        "com.hypixel.hytale.component.Ref r, com.hypixel.hytale.server.core.universe.PlayerRef p, "
        "com.hypixel.hytale.server.core.universe.world.World w) { }", ctl))
    ctl.writeFile(hcls)
    # review fixes 1 + 3: a stand-in World (never constructed: Unsafe.allocateInstance) that RECORDS what the mod queues on the world
    # thread instead of running it - execute (delay -1) and scheduleAfter (its delay in ms); refuse = a world that stopped taking tasks
    hw = CP.makeClass("skyyuiprobeharness.HarnessWorld", CP.get("com.hypixel.hytale.server.core.universe.world.World"))
    for fsrc in ("public java.util.ArrayList tasks;", "public java.util.ArrayList delays;", "public int count;", "public boolean refuse;"):
        hw.addField(CtField.make(fsrc, hw))
    hw.addConstructor(CtNewConstructor.make(
        "public HarnessWorld() { super((String) null, (java.nio.file.Path) null, "
        "(com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }", hw))
    hw.addMethod(CtNewMethod.make(
        "public void keep(java.lang.Runnable r, long ms) {\n"
        "  if (this.tasks == null) { this.tasks = new java.util.ArrayList(); this.delays = new java.util.ArrayList(); }\n"
        "  this.tasks.add(r);\n  this.delays.add(java.lang.Long.valueOf(ms));\n  this.count++;\n}", hw))
    hw.addMethod(CtNewMethod.make(
        "public void execute(java.lang.Runnable r) {\n"
        "  if (this.refuse) throw new java.lang.IllegalStateException(\"harness world takes no tasks\");\n  keep(r, -1L);\n}", hw))
    hw.addMethod(CtNewMethod.make(
        "public java.util.concurrent.ScheduledFuture scheduleAfter(java.lang.Runnable r, long d, java.util.concurrent.TimeUnit u) {\n"
        "  if (this.refuse) throw new java.util.concurrent.RejectedExecutionException(\"harness world takes no tasks\");\n"
        "  keep(r, u.toMillis(d));\n  return null;\n}", hw))
    hw.writeFile(hcls)
    HP, NET, HW = JClass("skyyuiprobeharness.HarnessPage"), JClass("skyyuiprobeharness.HarnessNet"), JClass("skyyuiprobeharness.HarnessWorld")

    def world():
        """a recording stand-in World (fields zero: no tasks yet)"""
        return U.allocateInstance(HW.class_)

    def queued(w):
        """[(task class, delay ms or -1 for execute)] still waiting on the stand-in world"""
        if w.tasks is None:
            return []
        return [(str(w.tasks.get(i).getClass().getSimpleName()), int(w.delays.get(i))) for i in range(int(w.tasks.size()))]

    def run_all(w):
        """run what waits on the stand-in world, in order (what the world thread would do); returns how many ran"""
        if w.tasks is None:
            return 0
        ts = [w.tasks.get(i) for i in range(int(w.tasks.size()))]
        w.tasks.clear()
        w.delays.clear()
        for t in ts:
            t.run()
        return len(ts)

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

    def session(n, win_id=7, owner=None, pr=ME):
        """a ProbeSession as ProbeWin.open fills it (no world, no store: the bare JVM has none) with a fresh box + window"""
        s = SES()
        s.pr = pr
        s.owner = owner or pr.getUuid()
        s.who = str(pr.getUsername())
        s.probe = n
        s.box = BOX.make()
        s.win = WINC(s.box, s)
        s.win.setId(win_id)
        s.winId = win_id
        return s

    for n in order:
        pg = PAGE(ME, n)
        if n in WIN_VIEWS:
            pg.sess = session(n)
        b, ev = UCB(), UEB()
        thrown = None
        try:
            pg.build(None, b, ev, None)
        except Exception as ex:
            thrown = ex
        got_r, thr_r = rendered[n]
        check(thrown is None and cmds(b) == got_r, "E. ProbePage(%d).build sends exactly probe %d (%s)" % (n, n, thrown))
        want = arrow_ev if n == 23 else foot_ev
        check(evs(ev) == want, "E. ProbePage(%d).build binds %s: %s" % (n, "Back / Close + the arrow SlotClicking" if n == 23 else "only Back / Close",
                                                                      evs(ev)))
        if n == 23:
            check(len(locks(ev)) == 3 and locks(ev)[-1] is False, "E. the arrow SlotClicking does not lock the interface: %s" % locks(ev))
        check(int(pg.view) == n, "E. ProbePage(%d) keeps its view after build" % n)
    for n in WIN_VIEWS:
        for how in ("no session", "closed session"):
            pg = PAGE(ME, n)
            if how == "closed session":
                s_ = session(n)
                s_.closed = True
                pg.sess = s_
            b, ev = UCB(), UEB()
            pg.build(None, b, ev, None)
            nw = str(PAGE.noWinText(n))
            check(nw == dump["nowin_txts"][str(n)], "E. noWinText(%d) = the build's text %r" % (n, nw))
            compare(cmds(b), expected(ix, SUI, nw), "E. ProbePage(%d) with %s falls back to the index (Info = noWinText)" % (n, how))
            check(evs(ev) == want_ev and int(pg.view) == 0 and str(pg.info) == nw, "E. ... index bindings, view 0, info kept (%s)" % how)
    for v in (0, 99, -1, PAGE_COUNT + 1):
        pg = PAGE(ME, v)
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        compare(cmds(b), expected(ix, SUI, str(PAGE.lastText(v))), "E. ProbePage(%d).build falls back to the index (Info = lastText)" % v)
        check(evs(ev) == want_ev, "E. ProbePage(%d) index bindings" % v)
    check(str(PAGE.lastText(0)) == dump["first_txt"] and str(PAGE.lastText(0)).startswith("Nothing opened yet - start with win, then secgrid"),
          "E. lastText(0) = %r" % str(PAGE.lastText(0)))
    for n in order:
        t, nxt = str(PAGE.lastText(n)), (order + [-1])[order.index(n) + 1]
        want = "Last opened: probe %d (%s). Did it look right? " % (n, dump["names"][str(n)]) + (
            "Next: probe %d (%s)." % (nxt, dump["names"][str(nxt)]) if nxt > 0 else "That was the last one.")
        check(t == want and "<" not in t and ">" not in t, "E. lastText(%d) = %r (got %r)" % (n, want, t))
        check(t == dump["last_txts"][str(n)], "E. lastText(%d) = the build's last_text (the text the build measured)" % n)
    iw, ifs, fm = int(dump["info_w"]), int(dump["info_fs"]), int(dump["fit_margin"])
    infos = [str(PAGE.lastText(0))] + [str(PAGE.lastText(n)) for n in order] + [
        "Probe %d could not be built - see the server log." % n for n in order] + [str(PAGE.noWinText(n)) for n in WIN_VIEWS]
    widest = max(SUI.text_width(t, ifs, bold=True) for t in infos)
    check(widest + fm <= iw, "E. every Info text (%d: lastText of 0 and each page, each failure line, the no-window lines) fits the Info "
                             "label (widest %.0f + %d <= %d px at %d px bold)" % (len(infos), widest, fm, iw, ifs))
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

    def lastcmds(p):
        return [(str(c.type), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)) for c in p.lastCmds]

    pg = HP(ME, 0)
    check(int(pg.view) == 0 and str(pg.info) == str(PAGE.lastText(0)), "K. a new page: view 0, Info = lastText(0)")
    n5 = 5
    check(click(pg, '{"a":"open:%d"}' % n5) is None, "K. open:%d does not throw" % n5)
    check(int(pg.view) == n5 and int(pg.rebuilds) == 1 and str(pg.info) == str(PAGE.lastText(n5)), "K. open:%d -> view %d, one rebuild" % (n5, n5))
    check(pg.lastCmds is not None and lastcmds(pg) == rendered[n5][0], "K. the rebuild sent probe %d" % n5)
    check([(str(e.type), str(e.selector), json.loads(str(e.data))) for e in pg.lastEvents] == foot_ev, "K. ... with only Back / Close bound")
    check(click(pg, '{"a": "back"}') is None and int(pg.view) == 0 and int(pg.rebuilds) == 2, "K. back -> the index, one rebuild")
    ixc = lastcmds(pg)
    info_lines = [json.loads(d)["0"] for t, s, d, x in ixc if s == ix["info"][0] + ".Text"]
    check(info_lines == [str(PAGE.lastText(n5))] and ("Last opened: probe %d (%s)" % (n5, dump["names"][str(n5)])) in info_lines[0],
          "K. the index after Back shows 'Last opened: probe %d (...)': %s" % (n5, info_lines))
    compare(ixc, expected(ix, SUI, str(PAGE.lastText(n5))), "K. the index after Back = the dumped index")
    before = state(pg)
    check(click(pg, '{"a":"back"}') is None and int(pg.view) == 0 and str(pg.info) == str(PAGE.lastText(n5))
          and int(pg.rebuilds) == before[2] + 1 and int(pg.closes) == before[3],
          "K. a second (stale) back: still the index view, Info kept %r, one rebuild (got view %d, %r)" % (
              str(PAGE.lastText(n5)), int(pg.view), str(pg.info)))
    check(lastcmds(pg) == ixc, "K. ... it re-sent exactly the same index (Info 'Last opened: probe %d ...')" % n5)
    check(len(chats(MYNET)) == 0, "K. no chat line so far")
    # a probe whose build throws inside rebuild: a harness page subclass whose render throws is not needed - force it with a view whose
    # grid fill throws: drop the stand-in item store for one click (new ItemStack then fails in the engine)
    item_cls = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_
    gv = 18
    jf(item_cls, "ASSET_STORE").set(None, None)
    before = state(pg)
    built0 = int(pg.built)
    ex = click(pg, '{"a":"open:%d"}' % gv)
    jf(item_cls, "ASSET_STORE").set(None, st0)
    check(ex is None, "K. open:%d never throws out of handleDataEvent (%s)" % (gv, ex))
    if int(pg.built) == built0 + 1:
        print("   note: probe %d built without an item store - the failure path is not exercised" % gv)
        click(pg, '{"a":"back"}')
    else:
        c = chats(MYNET)
        want = "[SkyyUiProbe] Probe %d (%s) could not be built - see the server log." % (gv, dump["names"][str(gv)])
        check(int(pg.view) == 0, "K. open:%d fails to build -> the page is back on the index view" % gv)
        check(str(pg.info) == "Probe %d could not be built - see the server log." % gv, "K. ... Info = %r" % str(pg.info))
        check(int(pg.rebuilds) == before[2] + 1, "K. ... exactly one rebuild (the failed one), none from the catch (%d)" % (int(pg.rebuilds) - before[2]))
        check(len(c) == before[4] + 1 and c[-1] == want, "K. ... one chat line %r (got %s)" % (want, c[before[4]:]))
        check(lastcmds(pg) == ixc, "K. ... nothing new was sent (the last page stays the index)")
        fail_info = "Probe %d could not be built - see the server log." % gv
        check(click(pg, '{"a":"back"}') is None and int(pg.view) == 0 and str(pg.info) == fail_info and len(chats(MYNET)) == before[4] + 1,
              "K. ... a stale back after the failure keeps the failure Info line, no chat (got %r)" % str(pg.info))
        check(click(pg, '{"a":"open:%d"}' % n5) is None and int(pg.view) == n5, "K. ... and the next Open works (open:%d)" % n5)
        click(pg, '{"a":"back"}')
        check(int(pg.view) == 0 and len(chats(MYNET)) == before[4] + 1, "K. ... back, no further chat line")
    for bad in ['{"a":"open:abc"}', '{"a":"open:99"}', '{"a":"open:"}', '{"a":"open:-3"}', '{"a":"open:0"}', '{"a":"open: 3"}',
                '{"b":"open:3"}', '{"a":5}', '{"a":"nonsense"}', '}{', '', '{"a":"', '"a"', None, '{"a":"open:99999999999"}',
                '{"a":"arrow","SlotIndex":1}', '{"a":"open:25"}']:
        before = state(pg)
        ex = click(pg, bad)
        check(ex is None and state(pg) == before, "K. malformed / out of place %r: no throw, no state change" % (bad,))
    check(click(pg, '{"a":"open:\\u0032"}') is None and int(pg.view) == 2, "K. an escaped \\u0032 opens probe 2 (jsonStr decodes it)")
    check(click(pg, '{"a":"close"}') is None and int(pg.closes) == 1 and int(pg.view) == 2, "K. close on a probe page -> close(), view kept")
    click(pg, '{"a":"back"}')
    check(click(pg, '{"a":"close"}') is None and int(pg.closes) == 2 and int(pg.view) == 0, "K. close on the index -> close()")
    # window probes from the index: no player component in a bare JVM -> one chat line, the index stays, nothing rebuilt
    for wv in WIN_VIEWS:
        before = state(pg)
        ex = click(pg, '{"a":"open:%d"}' % wv)
        c = chats(MYNET)
        want = "[SkyyUiProbe] Probe %d (%s) could not be opened (no player component)." % (wv, dump["names"][str(wv)])
        check(ex is None and int(pg.view) == 0 and int(pg.rebuilds) == before[2] and len(c) == before[4] + 1 and c[-1] == want,
              "K. open:%d from the index without a player: index kept, no rebuild, one chat line %r (got %s)" % (wv, want, c[before[4]:]))
    # arrow clicks on probe 23 (with its session)
    wp = HP(ME, 23)
    s23 = session(23, 11)
    wp.sess = s23
    for i in range(3):
        before = state(wp)
        ex = click(wp, '{"a":"arrow","SlotIndex":%d}' % i)
        c = chats(MYNET)
        want = "[SkyyUiProbe] Arrow %d (%s) pressed - the server got it on the first click. Did anything stick to your cursor?" % (
            i + 1, dump["win"]["arrow_names"][i])
        check(ex is None and len(c) == before[4] + 1 and c[-1] == want and state(wp)[:4] == before[:4],
              "K. probe 23 arrow %d: one chat line, no page change (%s)" % (i, c[before[4]:]))
        lt = [str(x) for x in PL.tail()]
        check(lt and lt[-1] == "probe 23 ProbeTester: arrow %d (%s, %s) pressed" % (i + 1, dump["win"]["arrow_names"][i],
                                                                                    dump["win"]["arrow_ids_vanilla"][i]),
              "K. ... and one log line: %s" % (lt[-1:],))
    for data in ('{"a":"arrow","SlotIndex":7}', '{"a":"arrow"}', '{"a":"arrow","SlotIndex":"2"}'):
        before = state(wp)
        click(wp, data)
        c = chats(MYNET)
        if '"2"' in data:
            check(len(c) == before[4] + 1 and c[-1].startswith("[SkyyUiProbe] Arrow 3 (Next page) pressed"), "K. a quoted SlotIndex \"2\" is read: %s" % c[-1:])
        else:
            check(len(c) == before[4] + 1 and "without a slot" in c[-1], "K. %s: one hint line (%s)" % (data, c[-1:]))
    check(int(wp.rebuilds) == 0 and int(wp.view) == 23, "K. arrow clicks never rebuild the page")
    # Back on a window view: the list first, then the session ends (no player component here: the admin's items stay in the box)
    s23.box.setItemStackForSlot(JShort(5), ISC("Food_Bread", 4))
    before = state(wp)
    ex = click(wp, '{"a":"back"}')
    check(ex is None and int(wp.view) == 0 and wp.sess is None and int(wp.rebuilds) == before[2] + 1,
          "K. Back on probe 23: view 0, session detached, one rebuild (the list)")
    compare(lastcmds(wp), expected(ix, SUI, str(PAGE.lastText(23))), "K. ... the list shows 'Last opened: probe 23 (win)'")
    check(bool(s23.closed) and str(s23.closedBy).startswith("window not open any more (Back to the list)"),
          "K. ... the session ended (%s)" % s23.closedBy)
    check(int(PW.ownIn(s23.box)) == 4 and int(PW.probesIn(s23.box)) == 3, "K. ... the admin's 4 bread stay in the box, the probe items too")
    check(s23.win is None and s23.pr is None and s23.world is None and s23.store is None and s23.reg is None and s23.box is not None
          and s23.owner is not None, "K. review fix 4: ... the ended session let go of its window / player / world refs (the box stays)")
    check(click(wp, '{"a":"arrow","SlotIndex":0}') is None and len(chats(MYNET)) == before[4], "K. an arrow click after Back does nothing")
    # review fix 3: Close on a window view closes the window AT ONCE - no 1.5 s check through onDismiss, no draggable panel without a page
    wc = HP(ME, 23)
    sc3 = session(23, 13)
    wcw = world()
    sc3.world = wcw
    wc.sess = sc3
    sc3.box.setItemStackForSlot(JShort(5), ISC("Food_Bread", 2))
    before = state(wc)
    ex = click(wc, '{"a":"close"}')
    lt = [str(x) for x in PL.tail()]
    check(ex is None and int(wc.closes) == 1 and wc.sess is None and int(wc.rebuilds) == 0,
          "K. review fix 3: Close on probe 23: the page closes once (close()), its session is detached, nothing rebuilt")
    check(bool(sc3.closed) and str(sc3.closedBy) == "window not open any more (Close button)" and int(sc3.dismissedAt) > 0,
          "K. ... and the window is closed in the same click (closeNow 'Close button'; no player component in a bare JVM -> the session "
          "ends): %s" % sc3.closedBy)
    check(any(x.startswith("probe 23 ProbeTester: session ended (window not open any more (Close button)); 2 own item(s) stay in the "
                           "probe box: Food_Bread x2") for x in lt[-3:]), "K. ... logged as the Close button: %s" % lt[-2:])
    wc.onDismiss(None, None)               # what close() -> PageManager.setPage(None) calls next in the engine
    check(int(wcw.count) == 0 and queued(wcw) == [], "K. ... the onDismiss that follows schedules NO 1.5 s window check: %s" % queued(wcw))
    check(int(PW.ownIn(sc3.box)) == 2 and int(PW.probesIn(sc3.box)) == 3, "K. ... the admin's 2 bread stay in the box (no inventory here)")
    check(len(chats(MYNET)) == before[4], "K. ... no chat line from the Close itself")
    # control: Esc (onDismiss with the session still attached) DOES schedule the 1.5 s check on the world thread
    we = HP(ME, 24)
    se = session(24, 14)
    wew = world()
    se.world = wew
    we.sess = se
    we.onDismiss(None, None)
    check(queued(wew) == [("ProbeCloseTask", int(dump["win"]["late_ms"]))] and bool(se.lateQueued) and not bool(se.closed),
          "K. control: Esc (onDismiss) schedules one ProbeCloseTask %d ms later and keeps the window open until then: %s" % (
              int(dump["win"]["late_ms"]), queued(wew)))
    print("K. clicks done (%d chat line(s))" % len(chats(MYNET)))

    # ---------------- W. the window probe logic (the engine's own container code)
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    SortType = JClass("com.hypixel.hytale.server.core.inventory.container.SortType")
    probe_ids = list(dump["win"]["probe_items"])

    def snap(*cs):
        out = {}
        for c in cs:
            for i in range(int(c.getCapacity())):
                s = c.getItemStack(JShort(i))
                if s is not None and not s.isEmpty():
                    out[str(s.getItemId())] = out.get(str(s.getItemId()), 0) + int(s.getQuantity())
        return out

    def where(c):
        return [(i, str(c.getItemStack(JShort(i)).getItemId()), int(c.getItemStack(JShort(i)).getQuantity()))
                for i in range(int(c.getCapacity())) if c.getItemStack(JShort(i)) is not None and not c.getItemStack(JShort(i)).isEmpty()]

    def arr(*cs):
        a = JArray(IC)(len(cs))
        for i, c in enumerate(cs):
            a[i] = c
        return a

    box = BOX.make()
    check(bool(box.armed) and int(box.getCapacity()) == dump["win"]["slots"] and
          [x[1] for x in where(box)] == probe_ids and all(x[2] == 1 for x in where(box)),
          "W. ProbeBox.make: %d slots, the 3 probe items in slots 0-2 (qty 1), armed: %s" % (dump["win"]["slots"], where(box)))
    check([str(x) for x in BOX.probeIds()] == probe_ids and all(bool(BOX.isProbeId(x)) for x in probe_ids) and not bool(BOX.isProbeId("Food_Bread"))
          and not bool(BOX.isProbeId(None)), "W. probeIds / isProbeId")
    inv = SIC(JShort(36))
    for i, (iid, q) in enumerate((("Food_Bread", 10), ("Weapon_Sword_Iron", 1), ("Ingredient_Bar_Iron", 30), ("Plant_Fruit_Apple", 5),
                                  ("Weapon_Mace_Iron", 1))):
        inv.setItemStackForSlot(JShort(i), ISC(iid, q))
    t0 = snap(box, inv)

    def invariant(what):
        t = snap(box, inv)
        outside = [x for x in where(inv) if x[1] in probe_ids and x[1] != "Weapon_Mace_Iron"] + \
                  [x for x in where(inv) if x[1] == "Weapon_Mace_Iron" and x[2] != 1]
        ok = t == t0 and int(PW.probesIn(box)) == 3 and not outside and snap(box).get("Weapon_Mace_Iron") == 1
        check(ok, "W. %s: totals unchanged %s, 3 probe items still in the box (%s), none outside" % (
            what, "" if t == t0 else "(%s -> %s)" % (t0, t), where(box)))

    def moved(tx):
        try:
            return bool(tx.succeeded())
        except Exception:
            return None

    # drag (MoveItemStack = moveItemStackFromSlotToSlot) - every direction
    for slot in range(3):
        tx = box.moveItemStackFromSlotToSlot(JShort(slot), JInt(1), inv, JShort(20))
        check(moved(tx) is False, "W. drag probe item %d out of the box to an empty inventory slot: refused" % slot)
        invariant("drag probe %d out" % slot)
        tx = box.moveItemStackFromSlotToSlot(JShort(slot), JInt(1), box, JShort(6))
        check(moved(tx) is False, "W. drag probe item %d inside the box: refused (locked)" % slot)
        invariant("drag probe %d inside" % slot)
        tx = box.moveItemStackFromSlotToSlot(JShort(slot), JInt(1), inv, JShort(0))
        check(moved(tx) is False, "W. drag probe item %d onto an occupied inventory slot (swap): refused" % slot)
        invariant("swap probe %d out" % slot)
    tx = inv.moveItemStackFromSlotToSlot(JShort(0), JInt(10), box, JShort(1))
    check(moved(tx) is False, "W. drag bread ONTO a probe item (the engine's swap asks only the target): refused")
    invariant("swap onto a probe item")
    tx = inv.moveItemStackFromSlotToSlot(JShort(4), JInt(1), box, JShort(5))
    check(moved(tx) is False and int(box.getItemStack(JShort(5)).getQuantity() if box.getItemStack(JShort(5)) is not None else 0) == 0,
          "W. drag the player's OWN iron mace (a probe item's id) into a free box slot: refused")
    invariant("a probe id from outside")
    tx = inv.moveItemStackFromSlotToSlot(JShort(0), JInt(6), box, JShort(4))
    check(moved(tx) is True and snap(box).get("Food_Bread") == 6, "W. drag 6 of the player's bread into a free box slot: moves")
    invariant("own bread in")
    tx = box.moveItemStackFromSlotToSlot(JShort(4), JInt(6), box, JShort(7))
    check(moved(tx) is True and str(box.getItemStack(JShort(7)).getItemId()) == "Food_Bread", "W. move the bread inside the box: moves")
    invariant("own bread inside")
    tx = box.moveItemStackFromSlotToSlot(JShort(7), JInt(6), box, JShort(2))
    check(moved(tx) is False, "W. drop the bread onto a probe item inside the box: refused")
    invariant("own bread onto a probe item")
    tx = box.moveItemStackFromSlotToSlot(JShort(7), JInt(6), inv, JShort(1))
    check(moved(tx) is True and str(box.getItemStack(JShort(7)).getItemId()) == "Weapon_Sword_Iron", "W. drop the box bread onto the inventory sword: they swap")
    invariant("own swap")
    tx = box.moveItemStackFromSlotToSlot(JShort(7), JInt(1), inv, JShort(1))
    check(moved(tx) is True, "W. and swap them back")
    invariant("own swap back")
    # shift-click (SmartMoveItemStack: whole-slot moves) - a refused probe slot answers a failed transaction, never null / an NPE
    for slot in range(3):
        try:
            tx = box.moveItemStackFromSlot(JShort(slot), inv)
            ok = tx is not None and not bool(tx.succeeded())
            err = None
        except Exception as ex_:
            ok, err = False, ex_
        check(ok, "W. shift-click probe item %d (single target): a failed MoveTransaction, no exception (%s)" % (slot, err))
        invariant("shift-click probe %d" % slot)
        try:
            lt_ = box.moveItemStackFromSlot(JShort(slot), arr(inv))
            ok, err = lt_ is not None, None
        except Exception as ex_:
            ok, err = False, ex_
        check(ok, "W. shift-click probe item %d (ListTransaction form): no exception (%s)" % (slot, err))
        invariant("shift-click list probe %d" % slot)
        try:
            lt_ = box.moveItemStackFromSlot(JShort(slot), JInt(1), arr(inv))
            ok, err = lt_ is not None, None
        except Exception as ex_:
            ok, err = False, ex_
        check(ok, "W. shift-click probe item %d (quantity + ListTransaction form): no exception (%s)" % (slot, err))
        invariant("shift-click qty list probe %d" % slot)
    tx = box.moveItemStackFromSlot(JShort(6), inv)
    check(tx is not None, "W. shift-click an empty box slot: a transaction (%s)" % tx)
    invariant("shift-click empty")
    # the Drop key (DropItemStack -> removeItemStackFromSlot(slot, qty))
    for slot in range(3):
        try:
            r_ = box.removeItemStackFromSlot(JShort(slot), JInt(1))
            ok = not bool(r_.succeeded()) or r_.getOutput() is None or r_.getOutput().isEmpty()
            err = None
        except Exception as ex_:
            ok, err = False, ex_
        check(ok, "W. Drop key on probe item %d: nothing removed (%s)" % (slot, err))
        invariant("drop probe %d" % slot)
        try:
            r_ = box.removeItemStackFromSlot(JShort(slot))
            ok = not bool(r_.succeeded())
            err = None
        except Exception as ex_:
            ok, err = False, ex_
        check(ok, "W. removeItemStackFromSlot(slot) on probe item %d: refused (%s)" % (slot, err))
        invariant("remove probe %d" % slot)
    # Put All / Quick Stack (player -> window), Take All (window -> player), merge, Sort
    try:
        inv.moveAllItemStacksTo(arr(box))
        err = None
    except Exception as ex_:
        err = ex_
    check(err is None, "W. Put All (moveAllItemStacksTo the box): no exception (%s)" % err)
    invariant("put all")
    check("Weapon_Mace_Iron" not in [x[1] for x in where(box) if x[0] >= 3], "W. ... the player's own mace never entered the box: %s" % where(box))
    check(int(PW.ownIn(box)) > 0, "W. ... the player's other items did (%d own items in the box)" % int(PW.ownIn(box)))
    try:
        inv.quickStackTo(arr(box))
        err = None
    except Exception as ex_:
        err = ex_
    check(err is None, "W. Quick Stack into the box: no exception (%s)" % err)
    invariant("quick stack")
    for st in (SortType.NAME, SortType.TYPE):       # RARITY needs the item QUALITY asset store (none in a bare JVM): same internal_sortItems
                                                    # path, which skips slots that refuse removal (offset 23) whatever the comparator
        try:
            box.sortItems(st)
            err = None
        except Exception as ex_:
            err = ex_
        check(err is None and [x[1] for x in where(box)][:3] == probe_ids, "W. Sort %s on the box: the probe items stay in slots 0-2 (%s, %s)" % (
            st, where(box)[:4], err))
        invariant("sort %s" % st)
    for slot in range(int(box.getCapacity())):           # Take All: every slot as a whole-slot move into the inventory
        try:
            box.moveItemStackFromSlot(JShort(slot), inv)
        except Exception as ex_:
            check(False, "W. Take All slot %d threw: %s" % (slot, ex_))
    invariant("take all")
    check(int(PW.ownIn(box)) == 0 and int(PW.probesIn(box)) == 3, "W. ... Take All emptied the admin's items, the 3 probe items stayed")
    # double-click merge: A.combineItemStacksIntoSlot(B, slot) pulls A's stackable stacks into B's (non-empty) slot - skipping A's slots
    # that refuse removal (offset 81); the move into B asks B.cantAddToSlot. Targets: every non-empty inventory slot (one is the
    # player's OWN iron mace: the box's probe mace must not be pulled) and every non-empty box slot (the probe items + own bread)
    bslot = [x[0] for x in where(inv) if x[1] == "Food_Bread"]
    tx = inv.moveItemStackFromSlotToSlot(JShort(bslot[0] if bslot else 0), JInt(3), box, JShort(5))
    check(bool(bslot) and moved(tx) is True, "W. 3 bread into the box for the merge tests (bread at inventory slot %s)" % bslot)
    invariant("bread for merge")
    for a_, b_, what in ((box, inv, "box -> inventory"), (inv, box, "inventory -> box")):
        for slot in [x[0] for x in where(b_)]:
            try:
                a_.combineItemStacksIntoSlot(b_, JShort(slot))
                err = None
            except Exception as ex_:
                err = ex_
            check(err is None, "W. double-click merge %s slot %d: no exception (%s)" % (what, slot, err))
            invariant("merge %s %d" % (what, slot))
    check(snap(box).get("Weapon_Mace_Iron") == 1 and snap(inv).get("Weapon_Mace_Iron") == 1,
          "W. ... the player's own mace and the probe mace stay apart (%s / %s)" % (where(box)[:3], where(inv)))
    # ---- returnTo (the return on close)
    inv2 = SIC(JShort(36))
    inv2.setItemStackForSlot(JShort(0), ISC("Food_Bread", 3))
    box.setItemStackForSlot(JShort(4), ISC("Food_Bread", 5))
    box.setItemStackForSlot(JShort(6), ISC("Weapon_Sword_Iron", 1))
    t1 = snap(box, inv2)
    r_ = [None if x is None else str(x) for x in PW.returnTo(box, inv2, inv2)]
    check(snap(box, inv2) == t1 and int(PW.ownIn(box)) == 0 and int(PW.probesIn(box)) == 3 and snap(inv2).get("Food_Bread") == 8
          and snap(inv2).get("Weapon_Sword_Iron") == 1 and not any(i in snap(inv2) for i in probe_ids),
          "W. returnTo, room: the 6 own items moved, the probe items stayed, totals equal: %s" % where(inv2))
    check(r_[0].startswith("returned 6 item(s) from the probe box to the inventory; counted ") and r_[0].endswith("- nothing created or lost")
          and r_[1] == "Your 6 item(s) from the probe window are back in your inventory (counted before and after: nothing lost).",
          "W. returnTo log + chat: %s" % r_)
    full = SIC(JShort(2))
    full.setItemStackForSlot(JShort(0), ISC("Rock_Stone", 7))
    full.setItemStackForSlot(JShort(1), ISC("Plant_Fruit_Apple", 2))
    box.setItemStackForSlot(JShort(4), ISC("Food_Bread", 5))
    t2 = snap(box, full)
    r_ = [None if x is None else str(x) for x in PW.returnTo(box, full, full)]
    check(snap(box, full) == t2 and int(PW.ownIn(box)) == 5 and "stayed in the box (inventory full: Food_Bread x5)" in r_[0]
          and r_[1].startswith("5 of your items stayed in the probe window (inventory full)"),
          "W. returnTo, inventory full: the bread stays in the box, totals equal: %s" % r_)
    r_ = [None if x is None else str(x) for x in PW.returnTo(box, None, None)]
    check(int(PW.ownIn(box)) == 5 and "could not be read" in r_[0] and r_[1].startswith("5 of your items stayed in the probe window"),
          "W. returnTo, inventory unreadable: nothing moves: %s" % r_)
    box.removeItemStackFromSlot(JShort(4))
    r_ = [None if x is None else str(x) for x in PW.returnTo(box, inv2, inv2)]
    check(r_ == ["nothing of the player's was in the probe box", None], "W. returnTo with only the probe items: nothing to do: %s" % r_)
    r_ = [None if x is None else str(x) for x in PW.returnTo(None, inv2, inv2)]
    check(r_[0] == "nothing of the player's was in the probe box", "W. returnTo(null box): no throw")
    # ---- counting helpers + countLine
    HashMap = JClass("java.util.HashMap")
    m1 = PW.counts(box, inv2)
    check(int(PW.total(m1)) == sum(snap(box, inv2).values()) and int(PW.val(m1, "Food_Bread")) == snap(box, inv2).get("Food_Bread")
          and int(PW.val(m1, "Nope")) == 0 and int(PW.total(None)) == 0, "W. counts / total / val")
    m2 = PW.counts(box, inv2)
    check(str(PW.diff(m1, m2)) == "", "W. diff of equal counts = ''")
    inv2.addItemStack(ISC("Food_Bread", 2))
    m3 = PW.counts(box, inv2)
    check(str(PW.diff(m2, m3)) == "Food_Bread 8 -> 10", "W. diff shows the change: %r" % str(PW.diff(m2, m3)))
    s = session(24, 9)
    s.last = PW.counts(s.box, inv2)
    s.lastTx = "MoveTransaction"
    r_ = [str(x) for x in PW.countLine(s, PW.counts(s.box, inv2))]
    check(r_[2] == "0" and r_[0].startswith("probe 24 ProbeTester: move 1 seen (MoveTransaction): counted ") and r_[0].endswith(
        "- nothing created or lost; probe items in the box: 3 of 3") and r_[1].startswith("Move seen - ") and int(s.moves) == 1,
          "W. countLine, nothing changed: %s" % r_)
    inv2.addItemStack(ISC("Food_Bread", 1))
    r_ = [str(x) for x in PW.countLine(s, PW.counts(s.box, inv2))]
    check(r_[2] == "1" and "COUNT CHANGED: Food_Bread 10 -> 11" in r_[0] and "did you drop or pick something up" in r_[1],
          "W. countLine, a count change is a WARNING + chat: %s" % r_)
    check("did you drop or pick something up, or did a bag sweep or refill a stack? Tell Claude." in r_[1],
          "W. review fix 6: the count-changed chat line also names a bag sweep / refill (it compares with the previous move): %s" % r_[1])
    s.box.armed = False
    s.box.removeItemStackFromSlot(JShort(1))
    s.box.armed = True
    r_ = [str(x) for x in PW.countLine(s, PW.counts(s.box, inv2))]
    check(r_[2] == "1" and "probe items in the box: 2 of 3" in r_[0] and r_[1].startswith("A locked probe item left the probe window"),
          "W. countLine, a probe item missing from the box: WARNING + chat: %s" % r_)
    # ---- the box change listener (ProbeChange -> noteChange): the transaction name; no world -> nothing queued
    s = session(23, 12)
    CHG = JClass(PKG + "ProbeChange")
    s.reg = s.box.registerChangeEvent(CHG(s))
    s.box.setItemStackForSlot(JShort(5), ISC("Food_Bread", 2))
    check(str(s.lastTx) != "" and not bool(s.countQueued), "W. a box change reaches noteChange (transaction %s), no count queued without a world" % s.lastTx)
    s.box.moveItemStackFromSlotToSlot(JShort(5), JInt(2), s.box, JShort(6))
    check(str(s.lastTx) == "MoveTransaction", "W. ... a drag inside the box is a MoveTransaction (%s)" % s.lastTx)
    s.reg.unregister()
    s.lastTx = ""
    s.box.moveItemStackFromSlotToSlot(JShort(6), JInt(2), s.box, JShort(5))
    check(str(s.lastTx) == "", "W. ... after unregister the listener is gone")
    # ---- the client packet log: describe() + the engine's own PacketAdapters with a stand-in GamePacketHandler
    MIS = JClass("com.hypixel.hytale.protocol.packets.inventory.MoveItemStack")
    SMIS = JClass("com.hypixel.hytale.protocol.packets.inventory.SmartMoveItemStack")
    DIS = JClass("com.hypixel.hytale.protocol.packets.inventory.DropItemStack")
    IAC = JClass("com.hypixel.hytale.protocol.packets.inventory.InventoryAction")
    CLW = JClass("com.hypixel.hytale.protocol.packets.window.CloseWindow")
    SWA = JClass("com.hypixel.hytale.protocol.packets.window.SendWindowAction")
    COW = JClass("com.hypixel.hytale.protocol.packets.window.ClientOpenWindow")
    CPE = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageEvent")
    SMT = JClass("com.hypixel.hytale.protocol.SmartMoveType")
    IAT = JClass("com.hypixel.hytale.protocol.InventoryActionType")
    CPT = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageEventType")
    WT = JClass("com.hypixel.hytale.protocol.packets.window.WindowType")
    pk = [(MIS(7, 3, 1, -2, 5), "MoveItemStack x1 from the probe window (7) slot 3 to storage slot 5"),
          (MIS(-1, 0, 4, 7, 8), "MoveItemStack x4 from hotbar slot 0 to the probe window (7) slot 8"),
          (MIS(-9, 2, 1, 3, 0), "MoveItemStack x1 from backpack slot 2 to window 3 slot 0"),
          (SMIS(7, 4, 2, SMT.PutInHotbarOrWindow), "SmartMoveItemStack (shift-click) x2 from the probe window (7) slot 4 (PutInHotbarOrWindow)"),
          (DIS(7, 0, 1), "DropItemStack x1 from the probe window (7) slot 0"),
          (IAC(7, IAT.TakeAll, JByte(0)), "InventoryAction TakeAll on the probe window (7)"),
          (CLW(7), "CloseWindow for the probe window (7)"), (CLW(2), "CloseWindow for window 2"),
          (SWA(7, None), "SendWindowAction on the probe window (7): ?"),
          (COW(WT.values()[0]), "ClientOpenWindow %s" % WT.values()[0]),
          (CPE(CPT.Dismiss, None), "CustomPageEvent Dismiss"),
          (CPE(CPT.Data, '{"a":"arrow","SlotIndex":1}'), 'CustomPageEvent Data {"a":"arrow","SlotIndex":1}')]
    for p_, want in pk:
        check(str(PW.describe(p_, 7)) == want, "W. describe(%s) = %r (got %r)" % (p_.getClass().getSimpleName(), want, str(PW.describe(p_, 7))))
    check(PW.describe(ISC("Food_Bread", 1), 7) is None and PW.describe(None, 7) is None, "W. describe of anything else = null")
    check(str(PW.describe(CPE(CPT.Data, "x" * 300), 7)).endswith("x" * 120 + "..."), "W. a long page event is cut at 120 characters")
    check([str(PW.sec(x, 7)) for x in (-1, -2, -3, -5, -8, -9, -10, 7, 0)] == ["hotbar", "storage", "armor", "utility", "tools", "backpack",
                                                                             "section -10", "the probe window (7)", "window 0"],
          "W. section names")
    PA = JClass("com.hypixel.hytale.server.core.io.adapter.PacketAdapters")
    inbound = jf(PA.class_, "inboundHandlers").get(None)
    handle_in = getattr(PA, "__handleInbound")
    n0 = int(inbound.size())
    PW.ensureNet()
    PW.ensureNet()
    check(int(inbound.size()) == n0 + 1 and PW.NET is not None, "W. ensureNet registers exactly ONE inbound filter (twice called): %d -> %d" % (n0, int(inbound.size())))
    GPH = JClass("com.hypixel.hytale.server.core.io.handlers.game.GamePacketHandler")
    gph = U.allocateInstance(GPH.class_)
    field(GPH, "playerRef").set(gph, ME)
    PW.SESS.clear()
    lines0 = len(list(PL.tail()))
    blocked = bool(handle_in(gph, MIS(7, 3, 1, -2, 5)))
    check(not blocked and len(list(PL.tail())) == lines0, "W. no probe session: the packet passes, nothing logged")
    s = session(24, 7)
    PW.SESS.put(ME.getUuid(), s)
    SYS = JClass("java.lang.System")
    # review fix 1: what the watcher stamps (wantsResend), first as a table, then through the engine's own PacketAdapters
    wr = [(MIS(7, 3, 1, -2, 5), True, "MoveItemStack out of the window"), (MIS(-1, 0, 4, 7, 8), True, "MoveItemStack into the window"),
          (MIS(-1, 0, 1, -2, 3), False, "MoveItemStack hotbar -> storage"), (MIS(-9, 2, 1, 3, 0), False, "MoveItemStack into window 3"),
          (SMIS(7, 4, 2, SMT.PutInHotbarOrWindow), True, "shift-click in the window"),
          (SMIS(-2, 4, 2, SMT.PutInHotbarOrWindow), True, "shift-click in storage (its target may be the window)"),
          (DIS(7, 0, 1), True, "Drop from the window"), (DIS(-1, 0, 1), False, "Drop from the hotbar"),
          (IAC(7, IAT.TakeAll, JByte(0)), True, "Take All on the window"), (IAC(0, IAT.TakeAll, JByte(0)), False, "an action on section 0"),
          (SWA(7, None), True, "SendWindowAction for the window"), (SWA(2, None), False, "SendWindowAction for window 2"),
          (CLW(7), False, "CloseWindow"), (COW(WT.values()[0]), False, "ClientOpenWindow"), (CPE(CPT.Dismiss, None), False, "page Dismiss"),
          (CPE(CPT.Data, '{"a":"close"}'), False, "page Data")]
    for p_, want, what in wr:
        check(bool(PW.wantsResend(p_, 7)) == want, "W. review fix 1: wantsResend(%s) = %s" % (what, want))
    check(not bool(PW.wantsResend(None, 7)) and not bool(PW.wantsResend(MIS(-1, 0, 1, -1, 2), -1)), "W. wantsResend: no packet / no window id -> false")
    s.sawAt = 0
    for p_ in (MIS(-1, 0, 1, -2, 3), CPE(CPT.Data, '{"a":"back"}'), CLW(2)):
        handle_in(gph, p_)
    check(int(s.sawAt) == 0, "W. review fix 1: a move between the player's own sections, a page event, another window's close: no stamp")
    t_stamp = int(SYS.currentTimeMillis())
    blocked = bool(handle_in(gph, MIS(7, 3, 1, -2, 5)))
    lt = [str(x) for x in PL.tail()]
    check(not blocked and lt[-1] == "probe 24 ProbeTester: the client sent MoveItemStack x1 from the probe window (7) slot 3 to storage slot 5",
          "W. an open session: the engine's PacketAdapters passes the packet on and the watcher logs it: %s" % lt[-1:])
    check(int(s.sawAt) >= t_stamp, "W. review fix 1: ... and stamps the session (sawAt) on the network thread, before the engine's handler")
    blocked = bool(handle_in(gph, CLW(7)))
    lt = [str(x) for x in PL.tail()]
    check(not blocked and lt[-1] == "probe 24 ProbeTester: the client sent CloseWindow for the probe window (7)", "W. ... CloseWindow logged: %s" % lt[-1:])
    s.closed = True
    s.closedAt = JClass("java.lang.System").currentTimeMillis()
    s.sawAt = 0
    handle_in(gph, DIS(7, 0, 1))
    lt = [str(x) for x in PL.tail()]
    check(lt[-1].endswith("DropItemStack x1 from the probe window (7) slot 0 (after the window closed)"), "W. ... within 5 s after the close it is still logged: %s" % lt[-1:])
    check(int(s.sawAt) == 0 and PW.SESS.get(ME.getUuid()) == s, "W. review fixes 1 + 4: ... a closed session is never stamped, and stays in SESS during the grace")
    s.closedAt = JClass("java.lang.System").currentTimeMillis() - 6000
    n_before = len(list(PL.tail()))
    handle_in(gph, DIS(7, 0, 1))
    check(len(list(PL.tail())) == n_before or [str(x) for x in PL.tail()][-1] == lt[-1], "W. ... 6 s after the close: silent")
    check(PW.SESS.get(ME.getUuid()) is None, "W. review fix 4: ... and the closed session left SESS (no closed session kept per admin)")
    PW.SESS.put(ME.getUuid(), s)
    other, _onet = pref("Someone", UUID.fromString("00000000-0000-0000-0000-0000000000b2"))
    gph2 = U.allocateInstance(GPH.class_)
    field(GPH, "playerRef").set(gph2, other)
    s.closed = False
    tail_before = [str(x) for x in PL.tail()]
    handle_in(gph2, MIS(7, 3, 1, -2, 5))
    check([str(x) for x in PL.tail()] == tail_before, "W. another player's packets are never logged")
    NETC = JClass(PKG + "ProbeNet")
    try:
        NETC().accept(None, None)
        NETC().accept(ME, None)
        err = None
    except Exception as ex_:
        err = ex_
    check(err is None, "W. ProbeNet.accept never throws (null player / packet): %s" % err)
    PW.stopNet()
    check(int(inbound.size()) == n0 and PW.NET is None, "W. stopNet removes the filter again (%d)" % int(inbound.size()))
    PW.stopNet()
    check(int(inbound.size()) == n0, "W. a second stopNet is harmless")
    PW.SESS.clear()
    # ---- the session life cycle without a world / player (the bare JVM has neither)
    s = session(23, 21)
    s.reg = s.box.registerChangeEvent(CHG(s))
    s.box.setItemStackForSlot(JShort(5), ISC("Food_Bread", 3))
    PW.dismissed(s)
    check(int(s.dismissedAt) > 0 and not bool(s.lateQueued) and not bool(s.closed), "W. dismissed without a world: noted, nothing scheduled, still open")
    PW.lateClose(s)
    check(not bool(s.closed), "W. lateClose without a player reference: no close, no throw")
    chat0 = len(chats(MYNET))
    PW.windowClosed(s, None, None)
    c = chats(MYNET)
    lt = [str(x) for x in PL.tail()]
    check(bool(s.closed) and str(s.closedBy) == "the client or the engine" and any("window 21 closed by the client or the engine" in x for x in lt[-3:]),
          "W. windowClosed: closed once, by the client / engine, logged: %s" % lt[-2:])
    check(len(c) == chat0 + 1 and c[-1].startswith("[SkyyUiProbe] 3 of your items stayed in the probe window (your inventory could not be read)")
          and int(PW.ownIn(s.box)) == 3, "W. ... without an inventory the 3 bread stay in the box, one chat line: %s" % c[chat0:])
    check(s.win is None and s.pr is None and s.reg is None and s.world is None and s.store is None and s.last is None
          and s.box is not None and s.owner is not None and int(s.winId) == 21 and str(s.who) == "ProbeTester" and int(s.closedAt) > 0,
          "W. review fix 4: windowClosed let go of the window / player / listener / world / store refs (box, owner, window id, name, "
          "closedAt stay for the grace and the late-close log)")
    s.box.setItemStackForSlot(JShort(6), ISC("Food_Bread", 1))
    PW.windowClosed(s, None, None)
    check(len(chats(MYNET)) == chat0 + 1, "W. a second windowClosed does nothing")
    PW.lateClose(s)
    lt = [str(x) for x in PL.tail()]
    check(lt[-1].endswith("1.5 s after the page closed the window was already closed (by the client or the engine)"), "W. lateClose after the close: logged only: %s" % lt[-1:])
    # the next probe already shows the same box: the old window returns nothing
    sa = session(23, 30)
    sb = session(24, 31)
    sb.box = sa.box
    PW.SESS.put(ME.getUuid(), sb)
    sa.box.setItemStackForSlot(JShort(5), ISC("Food_Bread", 2))
    chat0 = len(chats(MYNET))
    PW.windowClosed(sa, None, None)
    lt = [str(x) for x in PL.tail()]
    check(bool(sa.closed) and len(chats(MYNET)) == chat0 and int(PW.ownIn(sa.box)) == 2 and "stays open in probe 24" in lt[-1],
          "W. the old window closes while probe 24 shows the same box: nothing returned, no chat: %s" % lt[-1:])
    check(sa.win is None and sa.pr is None and sa.box is not None and sb.win is not None and sb.pr is not None,
          "W. review fix 4: ... the old session lets go of its refs too, the new one keeps its own")
    PW.SESS.clear()
    sc = session(24, 40)
    PW.closeNow(sc, None, None, "test")
    check(bool(sc.closed) and str(sc.closedBy) == "window not open any more (test)", "W. closeNow without a player: the session ends quietly (%s)" % sc.closedBy)
    check(sc.win is None and sc.pr is None and sc.box is not None, "W. review fix 4: endQuiet lets go of the refs too")
    PW.closeNow(sc, None, None, "again")
    check(str(sc.closedBy) == "window not open any more (test)", "W. closeNow on a closed session does nothing")
    so = session(23, 41)
    PW.release(so)
    check(so.win is not None and so.pr is not None and not bool(so.closed), "W. review fix 4: release() on an OPEN session changes nothing")
    so.box.setItemStackForSlot(JShort(5), ISC("Food_Bread", 1))
    try:
        so.win.onClose0(None, None)        # the engine's close of the window object itself (closeAllWindows / closeWindow)
        err = None
    except Exception as ex_:
        err = ex_
    check(err is None and bool(so.closed) and so.win is None and so.pr is None and int(PW.ownIn(so.box)) == 1,
          "W. ProbeWindow.onClose0: the session closes, lets go of its refs, the bread stays in the box without an inventory (%s)" % err)
    check(bool(PW.open(None, None, ME, None, 5)) is False and bool(PW.open(None, None, ME, None, 23)) is False,
          "W. ProbeWin.open: a non-window probe or no player component -> false")
    # the re-send after client packets: validate() is always true; without a world nothing is queued; syncNow without a reference: no-op
    sv = session(23, 50)
    check(bool(sv.win.validate(None, None)) is True and not bool(sv.syncQueued), "W. ProbeWindow.validate: true, nothing queued without a world")
    sv.closed = True
    check(bool(sv.win.validate(None, None)) is True and not bool(sv.syncQueued), "W. ProbeWindow.validate on a closed session: still true (never closes)")
    sv.closed = False
    PW.syncNow(sv)
    check(int(sv.syncs) == 0 and not bool(sv.syncQueued), "W. syncNow without a player reference: nothing sent, no throw")
    try:
        sv.win.resend()
        err = None
    except Exception as ex_:
        err = ex_
    check(err is None, "W. ProbeWindow.resend (the protected invalidate through the window itself): no IllegalAccessError (%s)" % err)
    check(PW.invType(6) is None and PW.invType(-1) is None, "W. invType: nothing outside the six sections (0-5 need the game's component "
                                                           "registry: InventoryComponent$Hotbar.getComponentType() is null in a bare JVM)")
    try:
        PW.markInv(None, None)
        err = None
    except Exception as ex_:
        err = ex_
    check(err is None, "W. markInv without a store: no throw (%s)" % err)
    # ---- review fix 1: the re-send gate. The engine calls validate() for every inventory packet that names the window AND on every
    # movement tick (Player.moveTo -> WindowManager.validateWindows), so validate() alone must never re-send; one re-send per watcher
    # stamp, SYNC_MS later (World.scheduleAfter). A stand-in World records what is queued; the tasks are run by hand.
    now = int(SYS.currentTimeMillis())
    sw_ = session(23, 51)
    check(not bool(PW.wantSync(sw_, now, True)), "W. review fix 1: wantSync without a stamp -> false")
    sw_.sawAt = now - 10
    check(bool(PW.wantSync(sw_, now, True)) and int(sw_.syncFor) == int(sw_.sawAt), "W. ... a fresh stamp -> true, and it is used up")
    check(not bool(PW.wantSync(sw_, now, True)), "W. ... the same stamp again -> false")
    sw_.sawAt = now - 1
    sw_.syncQueued = True
    check(not bool(PW.wantSync(sw_, now, True)) and int(sw_.syncFor) != int(sw_.sawAt),
          "W. ... while a re-send is queued -> false, the newer stamp is kept for later")
    sw_.syncQueued = False
    check(bool(PW.wantSync(sw_, now, True)), "W. ... once it ran -> true for the newer stamp")
    sw_.sawAt = now - SAW_MS
    check(bool(PW.wantSync(sw_, now, True)), "W. ... a stamp exactly %d ms old still counts" % SAW_MS)
    sw_.sawAt = now - SAW_MS - 1
    check(not bool(PW.wantSync(sw_, now, True)) and int(sw_.syncFor) == int(sw_.sawAt), "W. ... an older stamp is dropped (used up, no re-send)")
    sw_.sawAt = now
    sw_.closed = True
    check(not bool(PW.wantSync(sw_, now, True)), "W. ... a closed session -> false")
    sw_.closed = False
    PW.SESS.clear()
    n0 = int(inbound.size())
    PW.ensureNet()                         # the packet watcher is running: the stamp gate (not the fallback)
    w = world()
    sg = session(23, 70)
    sg.world = w
    PW.SESS.put(ME.getUuid(), sg)
    answers = set()
    for rnd in range(5):                   # 5 x 20 movement ticks (validateWindows), the world thread running its tasks in between
        for i in range(20):
            answers.add(bool(sg.win.validate(None, None)))
        run_all(w)
    check(answers == {True}, "W. validate() always answers true (it never closes the window): %s" % answers)
    check(int(w.count) == 0, "W. review fix 1: 100 validate() calls without a client packet for the window (movement, knockback, teleports) "
                             "queue NO re-send (got %d)" % int(w.count))
    blocked = bool(handle_in(gph, MIS(-1, 0, 1, 70, 5)))    # the client drags into the box: the watcher stamps, the engine's handler follows
    check(not blocked and int(sg.sawAt) > 0, "W. ... a MoveItemStack into the window passes and stamps the session")
    for i in range(30):                    # the packet's own two getSectionById validates + movement ticks
        sg.win.validate(None, None)
    check(queued(w) == [("ProbeSyncTask", SYNC_MS)] and bool(sg.syncQueued),
          "W. review fix 1: one window packet + 30 validate() calls queue exactly ONE re-send, %d ms later (World.scheduleAfter): %s" % (
              SYNC_MS, queued(w)))
    run_all(w)
    check(not bool(sg.syncQueued) and int(sg.syncs) == 0, "W. ... it ran (no player reference in a bare JVM: nothing sent) and cleared the flag")
    for rnd in range(3):
        for i in range(20):
            sg.win.validate(None, None)
        run_all(w)
    check(int(w.count) == 1, "W. review fix 1: the stamp is used up - 60 more validate() calls queue nothing (%d queued in all)" % int(w.count))
    time.sleep(0.005)                       # a later millisecond than the first stamp (two packets in one ms share one re-send)
    handle_in(gph, DIS(70, 4, 1))           # a second packet ...
    sg.win.validate(None, None)
    sg.sawAt = int(sg.sawAt) + 1            # ... and a third one ms later, while the re-send for the second still waits
    sg.win.validate(None, None)
    check(int(w.count) == 2 and len(queued(w)) == 1, "W. ... two packets while one re-send waits: still one queued (it covers the first)")
    run_all(w)
    sg.win.validate(None, None)
    check(int(w.count) == 3 and queued(w) == [("ProbeSyncTask", SYNC_MS)], "W. ... after it ran, the next validate() queues one for the newer packet")
    run_all(w)
    for i in range(20):
        sg.win.validate(None, None)
    check(int(w.count) == 3 and queued(w) == [], "W. ... and then nothing more")
    handle_in(gph, MIS(-1, 0, 1, -2, 3))    # a move between the player's own sections while the window is open
    for i in range(20):
        sg.win.validate(None, None)
    check(int(w.count) == 3, "W. review fix 1: a move between the player's own sections re-sends nothing")
    sg.sawAt = int(SYS.currentTimeMillis()) - SAW_MS - 500
    sg.win.validate(None, None)
    check(int(w.count) == 3 and int(sg.syncFor) == int(sg.sawAt), "W. review fix 1: a stamp older than %d ms is dropped, never re-sent for" % SAW_MS)
    w.refuse = True                        # a world that stopped taking tasks (shutting down)
    sg.sawAt = int(SYS.currentTimeMillis())
    sg.win.validate(None, None)
    w.refuse = False
    check(not bool(sg.syncQueued) and int(w.count) == 3, "W. ... a world that refuses the task: the flag is cleared again, no throw")
    PW.stopNet()                           # no packet watcher (registerInbound failed): the fallback, at most one per RATE_MS
    check(PW.NET is None and int(inbound.size()) == n0, "W. ... the watcher is removed for the fallback test")
    sg.lastSyncAt = 0
    for i in range(20):
        sg.win.validate(None, None)
    check(int(w.count) == 4, "W. review fix 1: without the watcher, 20 validate() calls queue one re-send (got %d)" % (int(w.count) - 3))
    run_all(w)
    for i in range(20):
        sg.win.validate(None, None)
    check(int(w.count) == 4, "W. ... and nothing more within %d ms" % RATE_MS)
    sg.lastSyncAt = int(sg.lastSyncAt) - RATE_MS - 50
    sg.win.validate(None, None)
    check(int(w.count) == 5 and queued(w) == [("ProbeSyncTask", SYNC_MS)], "W. ... one more after %d ms" % RATE_MS)
    run_all(w)
    sg.closed = True
    sg.lastSyncAt = 0
    sg.win.validate(None, None)
    check(int(w.count) == 5, "W. ... never for a closed session")
    PW.SESS.clear()
    # ProbeWin.shutdown lists a box that still holds an admin's items
    PW.BOXES.clear()
    bx = BOX.make()
    bx.setItemStackForSlot(JShort(4), ISC("Food_Bread", 2))
    PW.BOXES.put(UUID.fromString("00000000-0000-0000-0000-0000000000c3"), bx)
    PW.BOXES.put(UUID.fromString("00000000-0000-0000-0000-0000000000c4"), BOX.make())
    PW.shutdown()
    lt = [str(x) for x in PL.tail()]
    check(any(x.startswith("WARNING server stop: the probe box of 00000000-0000-0000-0000-0000000000c3 still holds 2 of the admin's own item(s): Food_Bread x2") for x in lt[-3:])
          and not any("0000000000c4" in x for x in lt[-3:]), "W. shutdown warns about a box with leftovers only: %s" % lt[-2:])
    bf = PW.boxFor(UUID.fromString("00000000-0000-0000-0000-0000000000c5"))
    check(PW.boxFor(UUID.fromString("00000000-0000-0000-0000-0000000000c5")) == bf and int(PW.probesIn(bf)) == 3,
          "W. boxFor makes one box per admin and keeps it")
    PW.BOXES.clear()
    print("W. window probe logic done")

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
    check(0 <= pos(h, "ProbeWin.open(") < op, "L. a window probe click goes to ProbeWin.open (before the rebuild path)")
    bk = pos(h, '"back"')
    check(0 <= bk < h.find(".rebuild(", bk) < h.find("ProbeWin.closeNow(", bk), "L. Back on a window view: the list (rebuild) first, then closeNow")
    o = code("ProbeCmds", "open")
    check(0 <= pos(o, "ProbeWin.open(") < pos(o, "opening probe ") < pos(o, "openCustomPage") < pos(o, "sent probe "),
          "L. /skyprobe n: window probes go to ProbeWin.open; others: 'opening probe' before openCustomPage, 'sent probe' after")
    w_ = code("ProbeWin", "open")
    check(0 <= pos(w_, "opening probe ") < pos(w_, "openCustomPageWithWindows") < pos(w_, "InventorySectionId") < pos(w_, "sendUpdate")
          < pos(w_, "registerChangeEvent") < pos(w_, "sent probe "),
          "L. ProbeWin.open: log, openCustomPageWithWindows, the InventorySectionId update, the change listener, 'sent probe'")
    last_close = w_.rfind("closeNow(")
    check(last_close > pos(w_, "sent probe ") > pos(w_, "openCustomPageWithWindows"), "L. ... the previous probe window closes only after the new page")
    cn = code("ProbeWin", "closeNow")
    check(0 <= pos(cn, "getWindow(") < pos(cn, "closeWindow("), "L. closeNow asks getWindow (its own window?) before closeWindow")
    sn = code("ProbeWin", "syncNow")
    check(0 <= pos(sn, "getReference(") < pos(sn, ".resend(") < pos(sn, "markInv("), "L. syncNow: the reference check, then resend, then markInv")
    rs = code("ProbeWindow", "resend")
    check(".invalidate(" in rs, "L. ProbeWindow.resend calls invalidate()")
    vd = code("ProbeWindow", "validate")
    check("ProbeWin.touched(" in vd and "iconst_1" in vd and "iconst_0" not in vd, "L. ProbeWindow.validate: touched(), then always true")
    tc = code("ProbeWin", "touched")
    check(0 <= pos(tc, "ProbeWin.wantSync(") < pos(tc, "World.scheduleAfter(") and "World.execute(" not in tc,
          "L. review fix 1: touched() asks wantSync, then queues the re-send with World.scheduleAfter (delayed) - never World.execute")
    pk_ = code("ProbeWin", "packet")
    check(0 <= pos(pk_, "ProbeWin.wantsResend(") < pos(pk_, "ProbeWin.describe(") and "ConcurrentHashMap.remove(" in pk_,
          "L. review fixes 1 + 4: packet() stamps (wantsResend) before it logs, and drops a session past the grace from SESS")
    ci = pos(h, '"close"')
    check(0 <= ci < h.find(".close(", ci) < h.find("ProbeWin.closeNow(", ci) < pos(h, '"back"'),
          "L. review fix 3: the Close branch closes the page, then the window (ProbeWin.closeNow), before the Back branch")

    def first_line(txt, *needles):
        for i_, l_ in enumerate(txt.splitlines()):
            if all(nd in l_ for nd in needles):
                return i_
        return -1

    for meth, rel in (("windowClosed", 2), ("endQuiet", 1)):
        cw_ = code("ProbeWin", meth)
        a_, b_ = first_line(cw_, "putfield", "ProbeSession.closedAt(J)"), first_line(cw_, "putfield", "ProbeSession.closed(Z)")
        check(0 <= a_ < b_, "L. review fix 4: %s writes closedAt before the volatile closed flag (the netty thread reads closed, then "
                            "closedAt): lines %d / %d" % (meth, a_, b_))
        check(cw_.count("ProbeWin.release(") == rel, "L. review fix 4: %s lets go of the session's refs (release x%d)" % (meth, rel))
    oc_ = code("ProbeWindow", "onClose0")
    check(0 <= pos(oc_, "ProbeWin.windowClosed(") < pos(oc_, "ProbeWin.release("), "L. review fix 4: ProbeWindow.onClose0 releases after windowClosed")
    check(JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ValidatedWindow").class_.isAssignableFrom(WINC.class_),
          "L. ProbeWindow is a ValidatedWindow")
    f_ = code("ProbeViews", "find")
    check("java.util.Locale.ROOT" in f_ and "toLowerCase(()" not in f_, "L. find() lower-cases with Locale.ROOT only")
    BOXC = BOX.class_
    sigs = {}
    for mm in BOXC.getDeclaredMethods():
        sigs.setdefault(str(mm.getName()), []).append(([str(p.getName()) for p in mm.getParameterTypes()], int(mm.getModifiers())))
    Mod = JClass("java.lang.reflect.Modifier")
    want_sigs = [("cantRemoveFromSlot", ["short"]), ("cantDropFromSlot", ["short"]),
                 ("cantAddToSlot", ["short", "com.hypixel.hytale.server.core.inventory.ItemStack", "com.hypixel.hytale.server.core.inventory.ItemStack"]),
                 ("internal_moveItemStackFromSlot", ["short", "com.hypixel.hytale.server.core.inventory.container.ItemContainer", "boolean", "boolean"]),
                 ("internal_moveItemStackFromSlot", ["short", "int", "com.hypixel.hytale.server.core.inventory.container.ItemContainer", "boolean", "boolean"])]
    for nm_, ps in want_sigs:
        got_ = [m_ for p_, m_ in sigs.get(nm_, []) if p_ == ps]
        check(len(got_) == 1 and Mod.isProtected(got_[0]) and not Mod.isStatic(got_[0]), "L. ProbeBox overrides %s(%s) (protected)" % (nm_, ", ".join(ps)))
    check(JClass("java.lang.reflect.Modifier").isVolatile(SES.class_.getDeclaredField("closed").getModifiers()), "L. ProbeSession.closed is volatile")
    check(JClass("com.hypixel.hytale.server.core.io.adapter.PlayerPacketWatcher").class_.isAssignableFrom(NETC.class_),
          "L. ProbeNet is a PlayerPacketWatcher")
    check(JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow").class_.isAssignableFrom(WINC.class_)
          and SIC.class_.isAssignableFrom(BOXC), "L. ProbeWindow is a ContainerWindow, ProbeBox a SimpleItemContainer")
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
    except Exception as e:                  # a crash (e.g. a jar without a member a check reads) is a FAIL, never "0 fail"
        traceback.print_exc()
        FAILS.append("the harness stopped on an exception: %s: %s" % (type(e).__name__, e))
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
