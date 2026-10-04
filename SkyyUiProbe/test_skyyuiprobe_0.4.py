"""Bare-JVM check for SkyyUiProbe 0.4 (made from test_skyyuiprobe_0.3.1.py, which came from 0.3's / 0.2's; kept next to the build
so the build report's JVM claims can be re-run).

    python SkyyUiProbe/test_skyyuiprobe_0.4.py [--jar <SkyyUiProbe-0.4.jar>] [--old <SkyyUiProbe-0.3.1.jar>] [--dir <scratch>]
                                               [--live <world mods folder>] [--keep]

Build the jar first (python SkyyUiProbe/build_skyyuiprobe_0.4.py). Re-run this after every build AND whenever tools/skyyui.py changes
(its kit id): the probe pages come from the kit, so a kit change can change what the pages send.
EVERY 0.3.1 CHECK STILL RUNS (sections D A S B C E K W O X L P M below, unchanged except the version / class count / the map variant
in P and M); 0.4 ADDS the map probe sections (they EXECUTE every new code path in the jar):
  N  the PNG encoder: MapImages packed with the ENGINE's own BitFieldArr (4 / 8 / 12 / 16 bits, palettes with alpha, 8 / 16 / 32 px)
     through MapPng.fromMapImage at scales 1 / 2 / 4, decoded back in pure Python (chunk CRCs, IHDR, PLTE / tRNS, zlib, the 5 PNG
     filters, 1 / 2 / 4 / 8-bit indices, RGBA) and compared pixel by pixel with the palette; MapPng.pack / unpack = BitFieldArr both
     ways; every refused MapImage (sizes, bits, short data, an index outside the palette, scale) -> null; every generated picture
     (mask, ring, 8 arrows, the 3 pictures, 2 test tiles) redrawn in Python from the same integer geometry and compared, plus what it
     must look like (disc, ring band, north tick, each arrow's heading); the byte sizes; the encode time per tile
  G  the pan / ring-buffer math: chunkOf / slot / key / inGroup / base / tilePos / groupPos / bucket against a Python model (yaw sweep
     incl. NaN / inf, negative coordinates); MapProbe.assign + move driven along random walks (single, diagonal and 2+ chunk steps,
     teleports, negative coordinates): after every step the commands applied to a model of the client keep all 81 window chunks on
     screen exactly where they belong (the player's block at the clip centre), one chunk step = 9 Anchor + 9 AssetPath sets, a
     diagonal 17, a re-base 81 Anchors, never a tile outside the grid Group's 544 px
  T  the outbound tap through the engine's own PacketAdapters.__handleOutbound with a stand-in GamePacketHandler: tapOn twice = one
     handler, tapOff removes it; nothing kept without a session or with nothing on (one volatile read); real UpdateWorldMap / MapChunk /
     MapImage / MapMarker / ClearWorldMap objects: null chunks, null entries, null arrays, markers, clears, other packet kinds ignored;
     a 25,000-packet burst (bounded at 20,000, the rest counted as dropped, the write never blocked); 4 threads storming while the tick
     drains (every packet counted once); the tap's time per packet; the analyzer's counts, bytes (computeSize), sizes, the summary
     line, P2's captured pieces (null chunk removes, Clear clears, prune), P5's segments at ClearWorldMap (named by the ready event)
  Q  the asset packets: names (content hash = CommonAsset.hash = sha256), one asset per picture, the mask under UI/Custom/, getBlob;
     send = ONE write of [AssetInitialize(name, hash, size), AssetPart, AssetFinalize] to that player only, once per connection, force
     re-sends, RequestCommonAssetsRebuild alone; a 6 MB asset split in 2,621,440-byte parts; the byte counts = computeSize
  H  the HUD command lists of every probe (P1a, P1b, P3 armed / re-sent / not re-sent, P2, P2 sharp, the pan updates) through the
     engine's UICommandBuilder: the page checks of the build (check_markup for the HUD root, check_page, no underscore id, every token
     proven or one of the 3 map trial tokens), the dumped templates, every b.set / setObject target exists in the document
  U  the HUD SLOT through the real HudManager: a SkyyHud stand-in (key skyyhud_main, shown with show() as SkyyHud does, and also
     registered) and the probe HUD side by side; a model of the client's HUD documents (CustomHud by hudId, ResetUserInterfaceState)
     after every step: no packet of the probe ever names skyyhud_main, SkyyHud's document is never cleared by the probe, and after
     off / a mode switch / a world change (the engine's resetHud) / a disconnect / shutdown the client holds exactly SkyyHud's document
  Y  every flow end to end through the tick (a recording scheduler, stand-in worlds / stores / player, the real HudManager): the
     command lines, p1a, p1b, p2 (the shared-cache tiles, tap pieces upgrading the tiles, the walk, the reads on the world thread),
     p2sharp, p3 / p3resend across a world change and a reconnect, p4 (60 s summary, a world change stops it), p5 (3 worlds), off,
     status, disconnect, shutdown; the tick stops when nothing runs
  R  start twice on a scratch COPY of the live world data (the live folder is only read): the plugin's start() twice = one tap, a
     shutdown removes it, a full session run, nothing written anywhere in the copy
  Z  class compare 0.3.1 vs 0.4: which old classes are byte-identical, the 3 changed ones (and which methods), the 17 new ones
NEW IN 0.3.1 (Skyy's /skyprobe secgrid threw java.lang.IllegalAccessError in game: ProbeWin called the protected
CustomUIPage.sendUpdate; javassist compiled it, -Xverify:all loads it, the JVM refuses it only when the line RUNS - and 0.3's harness
never ran it): section O EXECUTES the open paths of probes 23 / 24 through the engine's REAL PageManager / WindowManager /
ContainerWindow / CustomUIPage code, and section X checks every reference in the jar's bytecode with the JVM's own access rules. Run
against the 0.3 jar (--jar SkyyUiProbe/SkyyUiProbe-0.3.jar), O fails with the game's exact IllegalAccessError line and X names
ProbeWin.open -> CustomUIPage.sendUpdate.
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
  O  (0.3.1) THE OPEN PATHS THROUGH THE REAL ENGINE: a stand-in admin whose Player component holds the engine's own PageManager +
     WindowManager (wired with init(playerRef, ...) as the engine does), a stand-in Store that answers getComponent from a map
     (PlayerRef, Player, the six inventory components + the Combined one - real engine classes holding real containers), the
     Universe / EntityModule instances carrying only those component types, the store's external data an EntityStore on a recording
     World. Then, every step through the mod's bytecode and the engine's code, each followed by: no Java exception, no WARNING /
     error line in the mod log (an IllegalAccessError is caught by ProbeWin.open and logged - the 0.3 failure - so it FAILS here),
     and the exact packets: /skyprobe secgrid (ProbeCmds.arg -> ProbeWin.open -> openCustomPageWithWindows -> WindowManager
     openWindow -> ItemContainer.toPacket, PageManager.openCustomPage -> ProbePage.build, then ProbePage.sendSection ->
     CustomUIPage.sendUpdate): CustomPage (probe 24's page = section C's commands, Back / Close bound) -> OpenWindow (the window id,
     Container, 9 slots, the 3 probe items) -> CustomPage update (exactly one Set #SkyyPbSgGrid.InventorySectionId = the window id),
     the window registered in the WindowManager, the session open, counted with the real getCombined; /skyprobe win replaces it (new
     page + window first, then CloseWindow for the old one; the box stays open); the page acknowledgements (PageManager.handleEvent
     Acknowledge) and a Data click per step as the client sends them: the arrow grid (one chat line), a drag into the box (the box
     listener counts with the real inventory: chat "Move seen"), the watcher stamp + WindowManager.validateWindows -> the re-send ->
     WindowManager.updateWindows sends UpdateWindow and markInv marks all six inventory components; Back (CustomUIPage.rebuild sends
     the index, then CloseWindow, the bread back in storage, counted); the list's Open button for 24 (the world from
     Store.getExternalData); Close (CustomUIPage.close -> SetPage None, then CloseWindow at once, nothing queued); /skyprobe (the list
     through openCustomPage) and its Open button for 23; Esc (handleEvent Dismiss -> onDismiss -> the 1.5 s task -> CloseWindow, the
     bread back); a client close (WindowManager.closeWindow) and a world change / disconnect (WindowManager.closeAllWindows) - both
     return the admin's items, counted. The inventory ends exactly as it started, the box holds only the 3 probe items
  X  (0.3.1) ACCESS AUDIT with the JVM's own rules: every class / field / method / constructor reference in the jar's bytecode is looked
     up with MethodHandles.Lookup IN its referencing class (privateLookupIn: findVirtual / findStatic / findSpecial / findConstructor /
     findGetter / accessClass) - a protected engine member from a non-subclass, a package-private one, a non-public class all throw;
     0 refused. Controls: a harness class that calls a page's sendUpdate the 0.3 way is refused by the same audit AND throws
     java.lang.IllegalAccessError when run (this JVM enforces exactly the game's rule); ProbePage.sendSection (sendUpdate from the
     page itself, on this) passes
  L  bytecode order: "opening probe" before rebuild / openCustomPage(WithWindows), "sent probe" after; ProbeWin.open: the
     InventorySectionId update (0.3.1: ProbePage.sendSection - ProbeWin.open itself never names sendUpdate) after
     openCustomPageWithWindows, the previous window closed only after the new page; ProbePage.sendSection calls sendUpdate on this
     (aload_0); closeNow asks getWindow before closeWindow; syncNow re-sends the window before marking the inventory;
     ProbeWindow.resend calls invalidate and ProbeWindow is a ValidatedWindow; ProbeBox overrides the 5 container checks with the
     engine's signatures
  P  permissions with the engine's own code: /skyprobe and its usage variant hold skyyuiprobe.admin with empty permission-group lists,
     getPermissionGroupsRecursive() gives the node to no group; a real PermissionsModule object (never set up) with one fake provider
     + those virtual groups answers AbstractCommand.hasPermission: plain Adventurer, skyy.*, hytale.*, hytale.command.* refused; op
     ("*") and a node holder pass; control: a command listing hytale:Adventurer IS granted to the same plain player
  M  the jar: manifest (Main, Version 0.3.1, IncludesAssetPack false), exactly the 16 classes, no .ui file, the ready line's text
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
next to a custom page, InventorySectionId on a window section, the engine's packet handlers / world thread / CommandManager dispatch
around the calls (O runs the real PageManager / WindowManager code, called the way those handlers call it).
Nothing is deployed. Default scratch folder: tools/dev/scratch/uiprobe031-test (deleted at the end unless --keep); TEMP / TMP and
java.io.tmpdir point into it. --dir must name a folder INSIDE tools/dev/scratch that is new, empty or an earlier run's (it carries the
harness's marker file): anything else is refused before the run, so the end-of-run delete can only remove a folder this harness made.
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.4"
PAGE_COUNT = 24
KIT_COUNT = 22
WIN_VIEWS = [23, 24]
PKG = "com.skyy.uiprobe."
BUILD = os.path.join(HERE, "build_skyyuiprobe_%s.py" % VERSION)
NODE = "skyyuiprobe.admin"
OLD_CLASSES = ["ProbeLog", "ProbeViews", "ProbeSession", "ProbeBox", "ProbeWindow", "ProbeChange", "ProbeCountTask", "ProbeCloseTask",
               "ProbeSyncTask", "ProbeNet", "ProbePage", "ProbeWin", "ProbeCmds", "SkyProbeArgCmd", "SkyProbeCmd", "SkyyUiProbePlugin"]
MAP_CLASSES = ["MapPng", "MapGeo", "MapAsset", "MapReq", "MapP3", "MapSess", "MapHud", "MapUi", "MapProbe", "MapTick", "MapRead",
               "MapAttach", "MapDetach", "MapReady", "MapQuit", "MapTap", "SkyProbeMapCmd"]
CLASSES = OLD_CLASSES + MAP_CLASSES
CHANGED_OLD = ["ProbeCmds", "SkyProbeCmd", "SkyyUiProbePlugin"]     # 0.4 touched only these 0.3.1 classes
VAULT_JAR = os.path.join(ROOT, "SkyyVault", "SkyyVault-0.1.5.jar")     # the SET pin: its asset pack ships the Skyy_Vault_* arrow items


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.join(TOOLS, "dev", "scratch")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "uiprobe04-test")))
MARK = os.path.join(SCRATCH, ".skyyuiprobe-harness")    # marks a scratch folder this harness made (the only kind it deletes)
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyUiProbe-0.3.1.jar")))     # the SET pin (class compare Z)
LIVE = os.path.abspath(arg("--live", os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData",
                                                  "Saves", "HUD mod", "mods")))   # read only: copied into the scratch folder (R)
SKIPS = []
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
    if os.path.isfile(MARK):                                         # 0.4: an earlier run's folder (it is marked): start it empty
        shutil.rmtree(SCRATCH, ignore_errors=True)
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

    def fake(name, sup, ctor, neighbor, fields=(), methods=()):
        """a stand-in subclass of an engine class, defined next to it; never constructed (Unsafe.allocateInstance)"""
        c = CP.makeClass(name, CP.get(sup))
        for fsrc in fields:
            c.addField(CtField.make(fsrc, c))
        c.addConstructor(CtNewConstructor.make(ctor, c))
        for msrc in methods:
            c.addMethod(CtNewMethod.make(msrc, c))
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
    net_.addField(CtField.make("public java.util.ArrayList batches;", net_))      # 0.4: each write(ToClientPacket[]) as one list
    net_.addMethod(CtNewMethod.make(
        "public void write(com.hypixel.hytale.protocol.ToClientPacket[] ps) {\n"
        "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  if (this.batches == null) this.batches = new java.util.ArrayList();\n"
        "  java.util.ArrayList one = new java.util.ArrayList();\n"
        "  for (int i = 0; i < ps.length; i++) { this.sent.add(ps[i]); one.add(ps[i]); }\n  this.batches.add(one);\n}", net_))
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

    # ---------------- O. (0.3.1) THE OPEN PATHS THROUGH THE REAL ENGINE
    # 0.3's IllegalAccessError came from a line no bare-JVM check had ever RUN (the JVM checks member access when an instruction first
    # executes). Here the open paths run for real: the mod's bytecode + the engine's own PageManager / WindowManager / ContainerWindow /
    # CustomUIPage code. Stand-ins only where the engine needs a live server: the Store (getComponent from a map), the PlayerRef /
    # Player / Ref objects (Unsafe, fields set as the engine sets them), the Universe / EntityModule instances (only the component
    # types), the World (recording). The components themselves are real engine classes: the six InventoryComponents (real
    # containers) and the Combined component, so ProbeWin's playerAll / playerReturn go through the REAL InventoryComponent.getCombined.
    PMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    WMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
    Uni = JClass("com.hypixel.hytale.server.core.universe.Universe")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    INVN = "com.hypixel.hytale.server.core.inventory.InventoryComponent"
    INVc = JClass(INVN)
    CTc = JClass("com.hypixel.hytale.component.ComponentType")
    REFc, STOREc = JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.component.Store")
    ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    CICc = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
    CMDS = JClass(PKG + "ProbeCmds")
    JMod_ = JClass("java.lang.reflect.Modifier")
    LATE_MS = int(dump["win"]["late_ms"])
    TSC = fake("com.hypixel.hytale.component.SkyyUiProbeTestStore", "com.hypixel.hytale.component.Store",
               "public SkyyUiProbeTestStore() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
               "(com.hypixel.hytale.component.IResourceStorage) null); }", STOREc.class_,
               fields=["public java.util.IdentityHashMap comps;"],
               methods=["public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, "
                        "com.hypixel.hytale.component.ComponentType t) {\n  if (this.comps == null) return null;\n"
                        "  java.util.Map m = (java.util.Map) this.comps.get(r);\n  if (m == null) return null;\n"
                        "  return (com.hypixel.hytale.component.Component) m.get(t);\n}"])
    o_old = [(jf(Uni.class_, "instance"), jf(Uni.class_, "instance").get(None)),
             (jf(EMc.class_, "instance"), jf(EMc.class_, "instance").get(None))]
    for f_ in INVc.class_.getDeclaredFields():          # setupCombined writes these static ComponentType[] fields: put them back after O
        if JMod_.isStatic(f_.getModifiers()) and not JMod_.isFinal(f_.getModifiers()) and str(f_.getType().getName()).startswith("[L"):
            f_.setAccessible(True)
            o_old.append((f_, f_.get(None)))
    o_log = []
    try:
        ct_next = [900]

        def ctype():
            """a ComponentType with its own index (ComponentType.equals / hashCode compare the index the registry gives it)"""
            c_ = CTc()
            ct_next[0] += 1
            field(CTc, "index").setInt(c_, ct_next[0])
            field(CTc, "hashCode").setInt(c_, ct_next[0])
            return c_

        CT_PR, CT_PLA, CT_COMB = ctype(), ctype(), ctype()
        KINDS = [("Hotbar", "hotbarInventoryComponentType", 9), ("Storage", "storageInventoryComponentType", 36),
                 ("Backpack", "backpackInventoryComponentType", 0), ("Armor", "armorInventoryComponentType", 4),
                 ("Utility", "utilityInventoryComponentType", 4), ("Tool", "toolInventoryComponentType", 4)]
        CT_INV = dict((k, ctype()) for k, _f, _n in KINDS)
        uni = U.allocateInstance(Uni.class_)
        field(Uni, "playerRefComponentType").set(uni, CT_PR)
        jf(Uni.class_, "instance").set(None, uni)
        em = U.allocateInstance(EMc.class_)
        field(EMc, "playerComponentType").set(em, CT_PLA)
        field(EMc, "combinedInventoryComponentType").set(em, CT_COMB)
        for k, fname, _n in KINDS:
            field(EMc, fname).set(em, CT_INV[k])
        jf(EMc.class_, "instance").set(None, em)
        INVc.setupCombined(CT_INV["Storage"], CT_INV["Armor"], CT_INV["Hotbar"], CT_INV["Utility"], CT_INV["Backpack"], CT_INV["Tool"])
        invs = dict((k, JClass(INVN + "$" + k)(JShort(n))) for k, _f, n in KINDS)

        def kind_of(ct):
            return [k for k in CT_INV if CT_INV[k] == ct][0]

        def combined(cts):
            """the CombinedItemContainer getCombined builds for these component types (their containers, in that order)"""
            a = JArray(IC)(len(cts))
            for i, ct in enumerate(cts):
                a[i] = invs[kind_of(ct)].getInventory()
            return CICc(a)

        comb = JClass(INVN + "$Combined")()
        for key in (INVc.EVERYTHING, INVc.STORAGE_HOTBAR_BACKPACK):
            comb.getInventories().put(key, combined(list(key)))
        ostore = U.allocateInstance(TSC)
        oref = U.allocateInstance(REFc.class_)
        field(REFc, "store").set(oref, ostore)
        OU = UUID.fromString("00000000-0000-0000-0000-0000000000e1")
        opr = U.allocateInstance(PR.class_)
        field(PR, "uuid").set(opr, OU)
        field(PR, "username").set(opr, "OpenTester")
        onet = U.allocateInstance(NET.class_)
        field(PR, "packetHandler").set(opr, onet)
        field(PR, "entity").set(opr, oref)
        oplayer = U.allocateInstance(PLAc.class_)
        owm = WMc()
        owm.init(opr)                                   # what the engine does when the player joins (Player.init)
        opm = PMc()
        opm.init(opr, owm)
        field(PLAc, "windowManager").set(oplayer, owm)
        field(PLAc, "pageManager").set(oplayer, opm)
        comps = JClass("java.util.IdentityHashMap")()
        for ct_, c_ in [(CT_PR, opr), (CT_PLA, oplayer), (CT_COMB, comb)] + [(CT_INV[k], invs[k]) for k in invs]:
            comps.put(ct_, c_)
        allc = JClass("java.util.IdentityHashMap")()
        allc.put(oref, comps)
        ostore.comps = allc
        oworld = world()
        oes = U.allocateInstance(ESc.class_)
        field(ESc, "world").set(oes, oworld)
        field(STOREc, "externalData").set(ostore, oes)
        storage = invs["Storage"].getInventory()
        storage.setItemStackForSlot(JShort(0), ISC("Food_Bread", 10))
        storage.setItemStackForSlot(JShort(1), ISC("Rock_Stone", 20))
        invs["Hotbar"].getInventory().setItemStackForSlot(JShort(0), ISC("Weapon_Sword_Iron", 1))
        everything = comb.getInventories().get(INVc.EVERYTHING)
        INV0 = snap(everything)
        INV_TOTAL = sum(INV0.values())
        check(INV0 == {"Food_Bread": 10, "Rock_Stone": 20, "Weapon_Sword_Iron": 1} and bool(oref.isValid()) and opr.getReference() == oref
              and PLAc.getComponentType() == CT_PLA and ostore.getComponent(oref, PLAc.getComponentType()) == oplayer,
              "O. the stand-in admin: Player.getComponentType + Store.getComponent find the Player, PlayerRef.getReference the Ref, the "
              "real getCombined containers hold 10 bread, 20 stone, 1 sword: %s" % INV0)
        ogph = U.allocateInstance(GPH.class_)
        field(GPH, "playerRef").set(ogph, opr)
        PW.SESS.clear()
        PW.BOXES.clear()

        def osent():
            return [] if onet.sent is None else [onet.sent.get(i) for i in range(int(onet.sent.size()))]

        def kinds(ps):
            return [str(p.getClass().getSimpleName()) for p in ps]

        def pcmds(p):
            return [(str(c.type), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                     None if c.text is None else str(c.text)) for c in p.commands]

        def pevs(p):
            return [(str(e.type), str(e.selector), json.loads(str(e.data)) if e.data is not None else None) for e in p.eventBindings]

        def ochat(ps):
            return [str(p.message.rawText) for p in ps if str(p.getClass().getSimpleName()) == "ServerMessage"]

        def section(sec):
            """an InventorySection packet -> {slot: (item id, quantity)}"""
            out = {}
            it_ = sec.items.entrySet().iterator()
            while it_.hasNext():
                e_ = it_.next()
                out[int(e_.getKey())] = (str(e_.getValue().itemId), int(e_.getValue().quantity))
            return out

        def acks():
            return int(jf(PMc.class_, "customPageRequiredAcknowledgments").get(opm).get())

        def ack_all():
            """the client acknowledges every page packet it got (PageManager.handleEvent Acknowledge); a Data click is dropped by the
            engine while one is pending (the window pages' note: 'if the buttons do nothing, press Esc')"""
            n_ = acks()
            for _i in range(n_):
                opm.handleEvent(oref, ostore, CPE(CPT.Acknowledge, None))
            return n_

        def click(data):
            return lambda: opm.handleEvent(oref, ostore, CPE(CPT.Data, data))

        def ostep(what, fn):
            """one call into the mod / engine -> (the packets it sent, the mod's log lines). A Java exception thrown out of it, a WARNING
            line or a line naming an error FAILS: ProbeWin.open catches a throw (0.3: the IllegalAccessError) and logs it as a WARNING"""
            i0 = len(osent())
            PL.TAIL.clear()
            err = None
            try:
                fn()
            except Exception as ex_:
                err = ex_
            lines = [str(x) for x in PL.tail()]
            o_log.extend(lines)
            bad = [l for l in lines if l.startswith("WARNING") or re.search(r"Error|Exception|could not", l)]
            check(err is None and not bad, "O. %s: runs through the engine without an exception or an error line (%s %s)" % (
                what, err, bad))
            return osent()[i0:], lines

        def opened(n, ps, lines, how):
            """the checks of one window probe open (its session, window, page, packets) -> (session, page, window id)"""
            s_ = PW.SESS.get(OU)
            pg_ = opm.getCustomPage()
            wid = int(s_.winId) if s_ is not None else -1
            check(s_ is not None and not bool(s_.closed) and int(s_.probe) == n and wid > 0 and s_.store == ostore and s_.world == oworld,
                  "O. %s: probe %d is open - a live session, window id %d, the world + store it was opened in" % (how, n, wid))
            check(wid > 0 and s_.win is not None and owm.getWindow(JInt(wid)) == s_.win and int(s_.win.getId()) == wid,
                  "O. ... the ProbeWindow is registered in the engine's WindowManager under that id")
            check(pg_ is not None and str(pg_.getClass().getName()) == PKG + "ProbePage" and int(pg_.view) == n and pg_.sess == s_,
                  "O. ... the PageManager's page is a ProbePage, view %d, holding that session" % n)
            want = ["CustomPage", "OpenWindow"] + (["CustomPage"] if n == 24 else [])
            check(kinds(ps)[:len(want)] == want, "O. ... packets: %s (got %s)" % (want, kinds(ps)))
            if kinds(ps)[:len(want)] == want:
                p0, ow = ps[0], ps[1]
                check(bool(p0.isInitial) and bool(p0.clear) and str(p0.lifetime) == "CanDismiss" and str(p0.key) == PKG + "ProbePage",
                      "O. ... the page packet: initial, clear, CanDismiss, key ProbePage")
                check(pcmds(p0) == rendered[n][0], "O. ... the page = exactly probe %d's commands (section C, %d)" % (n, len(rendered[n][0])))
                check(pevs(p0) == (arrow_ev if n == 23 else foot_ev), "O. ... bindings: %s" % pevs(p0))
                check(int(ow.id) == wid and str(ow.windowType) == "Container" and int(ow.inventory.capacity) == 9
                      and dict((k_, v_) for k_, v_ in section(ow.inventory).items() if k_ < 3) == dict((i, (probe_ids[i], 1)) for i in range(3)),
                      "O. ... OpenWindow: window %d, Container, 9 slots, the 3 probe items in slots 0-2: %s" % (wid, section(ow.inventory)))
                if n == 24:
                    up = ps[2]
                    uc = pcmds(up)
                    check(not bool(up.isInitial) and not bool(up.clear) and len(uc) == 1 and uc[0][0] == "Set"
                          and uc[0][1] == "#SkyyPbSgGrid.InventorySectionId" and json.loads(uc[0][2])["0"] == wid
                          and len(list(up.eventBindings)) == 0,
                          "O. ... after the OpenWindow: ONE page update (not initial, not clear) = Set #SkyyPbSgGrid.InventorySectionId "
                          "= %d - ProbePage.sendSection -> CustomUIPage.sendUpdate (0.3: IllegalAccessError here): %s" % (wid, uc))
            sent_line = "sent probe %d: window id %d, probe items in the box 3 of 3, own items in the box %d, counted %d items (probe box + " \
                        "inventory)" % (n, wid, int(PW.ownIn(s_.box)) if s_ is not None else -1, 3 + INV_TOTAL)
            check(lines[-1:] == [sent_line] and (n == 23 or lines[-2:-1] == ["probe 24 OpenTester: sent #SkyyPbSgGrid.InventorySectionId = "
                                                                          "%d (one page update, after the window opened)" % wid]),
                  "O. ... logged%s 'sent probe %d', counted with the REAL getCombined (3 probe items + %d): %s" % (
                      " the InventorySectionId update, then" if n == 24 else "", n, INV_TOTAL, lines[-2:]))
            return s_, pg_, wid

        # O1 the command Skyy ran: /skyprobe secgrid (0.3: "could not open probe 24: java.lang.IllegalAccessError ...")
        ps, lines = ostep("/skyprobe secgrid (ProbeCmds.arg -> ProbeWin.open, probe 24)", lambda: CMDS.arg(oref, ostore, opr, oworld, "secgrid"))
        s24, pg24, w24 = opened(24, ps, lines, "/skyprobe secgrid")
        check(len(ps) == 3 and not ochat(ps) and acks() == 2, "O. ... nothing else sent (no 'could not be opened' chat), 2 page packets "
                                                               "to acknowledge (the page + its update)")
        # O2 /skyprobe win replaces it: the new page + window first, then the old window closes (the box stays open)
        ps, lines = ostep("/skyprobe win (probe 23 replaces 24)", lambda: CMDS.arg(oref, ostore, opr, oworld, "win"))
        s23, pg23, w23 = opened(23, ps, lines[:-2] if len(lines) >= 2 else lines, "/skyprobe win")
        check(s23 is not None and s24 is not None and s23 != s24 and s23.box == s24.box and w23 != w24 and pg23 != pg24,
              "O. ... a new session + page + window over the SAME probe box")
        check(bool(s24.closed) and str(s24.closedBy) == "the server (replaced by probe 23)" and owm.getWindow(JInt(w24)) is None,
              "O. ... probe 24's window was closed by the server (%s) and left the WindowManager" % s24.closedBy)
        check(kinds(ps) == ["CustomPage", "OpenWindow", "CloseWindow"] and int(ps[2].id) == w24,
              "O. ... CloseWindow for the old window comes AFTER the new page + window: %s" % kinds(ps))
        check(lines[-1:] == ["probe 24: the probe box stays open in probe 23 - its items are returned when that window closes"]
              and not ochat(ps), "O. ... nothing returned while probe 23 shows the box, no chat: %s" % lines[-1:])
        check(queued(oworld) == [("ProbeCloseTask", LATE_MS)],
              "O. ... the engine dismissed probe 24's page (openCustomPage -> onDismiss): its 1.5 s check is queued: %s" % queued(oworld))
        ps, lines = ostep("probe 24's 1.5 s check (world thread)", lambda: run_all(oworld))
        check(not ps and lines == ["probe 24 OpenTester: 1.5 s after the page closed the window was already closed (by the server "
                                   "(replaced by probe 23))"], "O. ... it finds the window closed and only logs: %s" % lines)
        # O3 the arrow grid, as the client sends it: dropped while a page acknowledgement is pending, then one chat line per click
        pend = acks()
        ps, lines = ostep("an arrow click while %d page acknowledgement(s) are pending" % pend, click('{"a":"arrow","SlotIndex":1}'))
        check(pend > 0 and not ps and not lines, "O. ... the engine drops it (nothing sent, nothing logged) - why the note says 'if the "
                                                 "buttons do nothing, press Esc'")
        check(ack_all() == pend and acks() == 0, "O. ... the client acknowledges the %d page packet(s)" % pend)
        ps, lines = ostep("a click on arrow 2 (PageManager.handleEvent Data -> ProbePage.handleDataEvent)", click('{"a":"arrow","SlotIndex":1}'))
        an, ai = dump["win"]["arrow_names"], dump["win"]["arrow_ids_vanilla"]
        check(kinds(ps) == ["ServerMessage"] and ochat(ps) == ["[SkyyUiProbe] Arrow 2 (%s) pressed - the server got it on the first click. "
                                                               "Did anything stick to your cursor?" % an[1]],
              "O. ... one chat line, nothing else: %s" % ochat(ps))
        check(lines == ["probe 23 OpenTester: arrow 2 (%s, %s) pressed" % (an[1], ai[1])], "O. ... one log line: %s" % lines)
        # O4 a drag into the box (the engine's own container move), the count, the watcher stamp -> validateWindows -> the re-send
        ps, lines = ostep("6 bread dragged from storage into box slot 5 (the engine's move)",
                          lambda: storage.moveItemStackFromSlotToSlot(JShort(0), JInt(6), s23.box, JShort(5)))
        check(int(PW.ownIn(s23.box)) == 6 and queued(oworld) == [("ProbeCountTask", -1)],
              "O. ... the bread is in the box and the box listener queued ONE count: %s" % queued(oworld))
        ps, lines = ostep("the world thread runs the count", lambda: run_all(oworld))
        check(ochat(ps) == ["[SkyyUiProbe] Move seen - %d items counted before and after: nothing created or lost." % (3 + INV_TOTAL)]
              and len(lines) == 1 and lines[0].startswith("probe 23 OpenTester: move 1 seen (") and lines[0].endswith(
                  "counted %d items before and %d after (probe box + inventory) - nothing created or lost; probe items in the box: 3 of 3"
                  % (3 + INV_TOTAL, 3 + INV_TOTAL)), "O. ... chat 'Move seen', counted with the real getCombined: %s %s" % (ochat(ps), lines))
        ps, lines = ostep("WindowManager.updateWindows (the move's own window update)", lambda: owm.updateWindows())
        check(kinds(ps) == ["UpdateWindow"] and int(ps[0].id) == w23 and section(ps[0].inventory).get(5) == ("Food_Bread", 6),
              "O. ... the engine sends the box with the bread in slot 5 (UpdateWindow): %s" % kinds(ps))
        for k in invs:
            invs[k].consumeIsDirty()                     # clean inventory flags: what follows must come from the re-send
        handle_in(ogph, MIS(-2, 0, 6, w23, 5))         # the client's MoveItemStack through the engine's PacketAdapters: the watcher stamps
        check(int(s23.sawAt) > 0, "O. ... the client's MoveItemStack (through PacketAdapters) stamped the session")
        ps, lines = ostep("5 x WindowManager.validateWindows (the packet's validate + movement ticks)",
                          lambda: [owm.validateWindows(oref, ostore) for _i in range(5)])
        check(not ps and queued(oworld) == [("ProbeSyncTask", SYNC_MS)] and owm.getWindow(JInt(w23)) == s23.win,
              "O. ... ProbeWindow.validate answers true (the window stays) and ONE re-send is queued %d ms later: %s" % (SYNC_MS, queued(oworld)))
        ps, lines = ostep("the world thread runs the re-send", lambda: run_all(oworld))
        check(int(s23.syncs) == 1 and all(bool(invs[k].consumeIsDirty()) for k in invs),
              "O. ... syncNow ran: markInv marked all six inventory components (InventoryComponent.markDirty)")
        ps, lines = ostep("WindowManager.updateWindows (the next window tick)", lambda: owm.updateWindows())
        check(kinds(ps) == ["UpdateWindow"] and int(ps[0].id) == w23, "O. ... ProbeWindow.resend -> Window.invalidate: the engine "
                                                                       "re-sends the window (one UpdateWindow): %s" % kinds(ps))
        # O5 Back: CustomUIPage.rebuild sends the list, then the window closes and the bread goes back to storage, counted
        ps, lines = ostep("Back on probe 23 (handleEvent Data back -> rebuild() -> closeNow)", click('{"a":"back"}'))
        check(kinds(ps) == ["CustomPage", "CloseWindow", "ServerMessage"] and int(ps[1].id) == w23,
              "O. ... packets: the list, CloseWindow, one chat line: %s" % kinds(ps))
        if kinds(ps)[:1] == ["CustomPage"]:
            check(not bool(ps[0].isInitial) and bool(ps[0].clear), "O. ... the list is a rebuild (not initial, clear)")
            compare(pcmds(ps[0]), expected(ix, SUI, str(PAGE.lastText(23))), "O. ... CustomUIPage.rebuild sent the list: 'Last opened: "
                                                                              "probe 23 (win)'")
            check(pevs(ps[0]) == want_ev, "O. ... with the index bindings")
        check(ochat(ps) == ["[SkyyUiProbe] Your 6 item(s) from the probe window are back in your inventory (counted before and after: "
                            "nothing lost)."], "O. ... chat: the 6 bread are back: %s" % ochat(ps))
        check(bool(s23.closed) and str(s23.closedBy) == "the server (Back to the list)" and owm.getWindow(JInt(w23)) is None
              and int(pg23.view) == 0 and pg23.sess is None and opm.getCustomPage() == pg23,
              "O. ... the window left the WindowManager, the session ended (%s), the page shows the list" % s23.closedBy)
        check(snap(everything) == INV0 and int(PW.ownIn(s23.box)) == 0 and int(PW.probesIn(s23.box)) == 3,
              "O. ... the inventory holds exactly what it held before the probe (%s), the probe items stay in the box" % snap(everything))
        check(any(l == "probe 23 OpenTester: returned 6 item(s) from the probe box to the inventory; counted %d items before and %d after "
                       "- nothing created or lost" % (3 + INV_TOTAL, 3 + INV_TOTAL) for l in lines), "O. ... the return is logged, counted")
        # O6 the list's Open button for probe 24 (the click path: the world comes from Store.getExternalData)
        ack_all()
        ps, lines = ostep("the list's Open button for probe 24 (handleEvent Data open:24 -> ProbeWin.open)", click('{"a":"open:24"}'))
        s24b, pg24b, w24b = opened(24, ps, lines, "the Open button")
        check(len(ps) == 3 and queued(oworld) == [], "O. ... nothing else sent; the dismissed list page queued nothing (no session)")
        # O7 Close: CustomUIPage.close -> PageManager.setPage(None), then the window closes AT ONCE (no 1.5 s check)
        ack_all()
        ps, lines = ostep("Close on probe 24 (handleEvent Data close -> close() -> closeNow)", click('{"a":"close"}'))
        check(kinds(ps) == ["SetPage", "CloseWindow"] and str(ps[0].page) == "None" and int(ps[1].id) == w24b,
              "O. ... packets: SetPage None (CustomUIPage.close), then CloseWindow: %s" % kinds(ps))
        check(opm.getCustomPage() is None and bool(s24b.closed) and str(s24b.closedBy) == "the server (Close button)"
              and owm.getWindow(JInt(w24b)) is None and queued(oworld) == [] and pg24b.sess is None,
              "O. ... no page, the window closed by the Close button (%s), nothing queued" % s24b.closedBy)
        # O8 /skyprobe (the list, PageManager.openCustomPage), its Open button for probe 23, then Esc: handleEvent Dismiss ->
        # onDismiss -> the 1.5 s check closes the window and returns the bread
        ack_all()
        ps, lines = ostep("/skyprobe (ProbeCmds.open -> PageManager.openCustomPage, the list)", lambda: CMDS.open(oref, ostore, opr, oworld, 0))
        check(kinds(ps) == ["CustomPage"] and bool(ps[0].isInitial) and lines == ["opening the index for OpenTester", "sent the index"],
              "O. ... one page packet, logged: %s %s" % (kinds(ps), lines))
        if kinds(ps) == ["CustomPage"]:
            compare(pcmds(ps[0]), expected(ix, SUI, str(PAGE.lastText(0))), "O. ... the list as dumped (Info: %r)" % str(PAGE.lastText(0)))
            check(pevs(ps[0]) == want_ev, "O. ... with the index bindings")
        ack_all()
        ps, lines = ostep("the list's Open button for probe 23 (handleEvent Data open:23 -> ProbeWin.open)", click('{"a":"open:23"}'))
        s23b, pg23b, w23b = opened(23, ps, lines, "the Open button for 23")
        check(len(ps) == 2 and queued(oworld) == [], "O. ... nothing else sent; the dismissed list page queued nothing")
        ostep("2 bread into the box", lambda: storage.moveItemStackFromSlotToSlot(JShort(0), JInt(2), s23b.box, JShort(6)))
        ps, lines = ostep("the count", lambda: run_all(oworld))
        check(len(ochat(ps)) == 1 and ochat(ps)[0].startswith("[SkyyUiProbe] Move seen - "), "O. ... counted: %s" % ochat(ps))
        ps, lines = ostep("Esc (handleEvent Dismiss -> ProbePage.onDismiss)", lambda: opm.handleEvent(oref, ostore, CPE(CPT.Dismiss, None)))
        check(not ps and opm.getCustomPage() is None and queued(oworld) == [("ProbeCloseTask", LATE_MS)] and not bool(s23b.closed)
              and owm.getWindow(JInt(w23b)) == s23b.win, "O. ... the page is gone, the window still open, its 1.5 s check queued: %s"
              % queued(oworld))
        ps, lines = ostep("the 1.5 s check (world thread)", lambda: run_all(oworld))
        check(kinds(ps) == ["CloseWindow", "ServerMessage"] and int(ps[0].id) == w23b and ochat(ps) == [
            "[SkyyUiProbe] Your 2 item(s) from the probe window are back in your inventory (counted before and after: nothing lost)."],
            "O. ... the server closes the window, the 2 bread come back: %s %s" % (kinds(ps), ochat(ps)))
        check(bool(s23b.closed) and str(s23b.closedBy) == "the server (page closed 1.5 s ago)" and any(
            "the window was still open 1.5 s after the page closed (Esc or another page)" in l for l in lines),
            "O. ... closed by the late check (%s), logged" % s23b.closedBy)
        # O9 the client closes the window itself (the engine's CloseWindow handler), then a world change / disconnect (closeAllWindows)
        for how, name_, n_, closer in (("the client's CloseWindow (WindowManager.closeWindow)", "secgrid", 24, "close"),
                                       ("a world change / disconnect (WindowManager.closeAllWindows)", "win", 23, "all")):
            ps, lines = ostep("/skyprobe " + name_, lambda: CMDS.arg(oref, ostore, opr, oworld, name_))
            s_, pg_, w_ = opened(n_, ps, lines, "/skyprobe %s (again)" % name_)
            ostep("3 bread into the box", lambda: storage.moveItemStackFromSlotToSlot(JShort(0), JInt(3), s_.box, JShort(7)))
            ps, lines = ostep("the count", lambda: run_all(oworld))
            check(len(ochat(ps)) == 1 and ochat(ps)[0].startswith("[SkyyUiProbe] Move seen - "), "O. ... counted: %s" % ochat(ps))
            if closer == "close":
                ps, lines = ostep(how, lambda: owm.closeWindow(oref, JInt(w_), ostore))
            else:
                ps, lines = ostep(how, lambda: owm.closeAllWindows(oref, ostore))
            check(kinds(ps) == ["CloseWindow", "ServerMessage"] and int(ps[0].id) == w_ and ochat(ps) == [
                "[SkyyUiProbe] Your 3 item(s) from the probe window are back in your inventory (counted before and after: nothing lost)."]
                and bool(s_.closed) and str(s_.closedBy) == "the client or the engine" and owm.getWindow(JInt(w_)) is None,
                "O. %s: ProbeWindow.onClose0 returns the 3 bread, closed by the client or the engine: %s %s" % (how, kinds(ps), ochat(ps)))
            ack_all()
            ostep("Esc after the window closed", lambda: opm.handleEvent(oref, ostore, CPE(CPT.Dismiss, None)))
            check(queued(oworld) == [], "O. ... Esc after that queues nothing (the session is closed)")
        check(owm.getWindows().size() == 0 and snap(everything) == INV0 and snap(PW.boxFor(OU)) == dict((i_, 1) for i_ in probe_ids),
              "O. end: no window left, the inventory holds exactly what it started with (%s), the box only the 3 probe items" % snap(everything))
        check(len(o_log) > 30 and not any(re.search(r"IllegalAccess|Error|Exception|WARNING", l) for l in o_log),
              "O. none of the %d mod log lines written during O names an IllegalAccessError, another error or a WARNING" % len(o_log))
    except Exception as ex_:                            # a step that failed above leaves nothing to drive: report it, go on with X
        traceback.print_exc()
        check(False, "O. the open-path run stopped after a failed step (%s: %s) - mod log lines so far: %s" % (
            type(ex_).__name__, ex_, [l for l in o_log if re.search(r"IllegalAccess|Error|Exception|WARNING", l)][:3]))
    finally:
        PW.stopNet()
        PW.SESS.clear()
        PW.BOXES.clear()
        for f_, v_ in o_old:
            f_.set(None, v_)
    print("O. open paths through the real PageManager / WindowManager done (%d mod log lines, 0 errors expected)" % len(o_log))

    # ---------------- X. (0.3.1) ACCESS AUDIT with the JVM's own rules (MethodHandles.Lookup in each referencing class)
    hx = CP.makeClass("skyyuiprobeharness.LookupIn")
    hx.addMethod(CtNewMethod.make(
        "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
        "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", hx))
    hx.writeFile(hcls)
    bs = CP.makeClass("skyyuiprobeharness.BadSender")           # the 0.3 call, from a class that is no page: javassist compiles it
    bs.addMethod(CtNewMethod.make(
        "public static void send(com.skyy.uiprobe.ProbePage p, int id) {\n"
        "  com.hypixel.hytale.server.core.ui.builder.UICommandBuilder b = new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder();\n"
        "  b.set(\"#SkyyPbSgGrid.InventorySectionId\", id);\n  p.sendUpdate(b);\n}", bs))
    bs.writeFile(hcls)
    LIN = JClass("skyyuiprobeharness.LookupIn")
    MTc = JClass("java.lang.invoke.MethodType")
    CPool = JClass("javassist.bytecode.ConstPool")
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, loader)

    def lookup_audit(cn):
        """(refused references, references checked) of class cn: each class / field / method / constructor reference in its bytecode
        looked up with a MethodHandles.Lookup IN that class - the JVM's own access rules (a protected member only from a subclass, no
        package-private / private member of another class, public classes only)"""
        D = jvm_class(cn)
        lk = LIN.lookupIn(D)
        cc = CP.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n = [], 0
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it_ = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it_.hasNext():
                p_ = it_.next()
                op = it_.byteAt(p_)
                if op not in XOPS:
                    continue
                where = "%s.%s @%d %s" % (cn.rsplit(".", 1)[-1], mi.getName(), p_, XOPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        nm_ = str(cp.getClassInfo(idx))
                        lk.accessClass(jvm_class(nm_))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", loader).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)),
                                                 str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)),
                                                 str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, loader)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            # super(...) / this(...): any public or protected constructor of the superclass, a package one at home
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn
                                    or (not JMod_.isPrivate(md) and str(C_.getPackageName()) == str(D.getPackageName()))):
                                raise ValueError("constructor %s %s%s is not accessible from %s" % (JMod_.toString(md), cname, desc, cn))
                        elif name == "<init>":
                            lk.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lk.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lk.findSpecial(C_, name, mt, D)
                        else:
                            lk.findVirtual(C_, name, mt)
                except Exception as ex_:
                    refused.append("%s: %s" % (where, ex_))
        return refused, n

    xref, xn = [], 0
    for cn in names:
        r_, n_ = lookup_audit(cn)
        xref += r_
        xn += n_
    check(not xref and xn > 1000, "X. all %d class / field / method / constructor references in the jar's %d classes pass "
                                  "MethodHandles.Lookup in their own class (the JVM's access rules): refused %s" % (xn, len(names), xref[:5]))
    br, bn = lookup_audit("skyyuiprobeharness.BadSender")
    check(len(br) == 1 and "sendUpdate" in br[0] and "invokevirtual" in br[0],
          "X. control: the 0.3 call (a class that is no page calling a page's sendUpdate) is refused by the same audit: %s" % br)
    pgx = PAGE(ME, 24)
    try:
        JClass("skyyuiprobeharness.BadSender").send(pgx, 7)
        err, msg = None, ""
    except Exception as ex_:
        err = ex_
        try:
            msg = "%s: %s" % (ex_.getClass().getName(), ex_.getMessage())
        except Exception:
            msg = str(ex_)
    check(err is not None and msg.startswith("java.lang.IllegalAccessError: ") and "tried to access protected method" in msg
          and "CustomUIPage.sendUpdate" in msg, "X. control: running that call throws the game's exact error - this JVM enforces the "
                                                 "rule the harness relies on: %s" % msg[:200])
    try:
        pgx.sendSection(7)                               # the 0.3.1 way: the page itself, on this (no live player here: sends nothing)
        err = None
    except Exception as ex_:
        err = ex_
    check(err is None, "X. control: ProbePage.sendSection (sendUpdate from the page itself, on this) passes the same JVM check (%s)" % err)
    print("X. access audit: %d references, %d refused (control refused %d)" % (xn, len(xref), len(br)))

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
    check(0 <= pos(w_, "opening probe ") < pos(w_, "openCustomPageWithWindows") < pos(w_, "ProbePage.sendSection(")
          < pos(w_, "InventorySectionId") < pos(w_, "registerChangeEvent") < pos(w_, "sent probe "),
          "L. ProbeWin.open: log, openCustomPageWithWindows, the InventorySectionId update (0.3.1: ProbePage.sendSection, then its log "
          "line), the change listener, 'sent probe'")
    check("sendUpdate" not in w_, "L. 0.3.1: ProbeWin.open never names sendUpdate (protected - only the page may call it, on itself)")
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

    ss_ = code("ProbePage", "sendSection")
    ssl = ss_.splitlines()
    iu = first_line(ss_, "invokevirtual", "CustomUIPage.sendUpdate(")
    check(0 <= pos(ss_, '"#SkyyPbSgGrid.InventorySectionId"') < pos(ss_, "UICommandBuilder.set(") < pos(ss_, "CustomUIPage.sendUpdate(")
          and iu >= 2 and ssl[iu - 2].strip().endswith("aload_0") and ss_.count("sendUpdate(") == 1,
          "L. 0.3.1: ProbePage.sendSection sets #SkyyPbSgGrid.InventorySectionId and calls sendUpdate once, on this (aload_0)")
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
    var2 = vm.get(JInt(2)) if vm is not None else None          # 0.4: /skyprobe map <step>
    for c_ in (cmd, var, var2, cc):
        if c_ is not None and own is not None:
            c_.setOwner(own)
    check(var is not None and str(var.getClass().getSimpleName()) == "SkyProbeArgCmd", "P. /skyprobe <page> is the usage variant SkyProbeArgCmd: %s" % vm)
    check(var2 is not None and str(var2.getClass().getSimpleName()) == "SkyProbeMapCmd" and vm.size() == 2,
          "P. 0.4: /skyprobe map <step> is the 2-word usage variant SkyProbeMapCmd (exactly 2 variants): %s" % vm)
    check(var2 is not None and int(var2.getRequiredArguments().size()) == 2 and int(var.getRequiredArguments().size()) == 1,
          "P. 0.4: the variants take 1 and 2 required words")
    subs = cmd.getSubCommands()
    check(subs is None or subs.size() == 0, "P. /skyprobe has no sub-commands (only the variant)")
    for c_, what in ((cmd, "/skyprobe"), (var, "/skyprobe <page>"), (var2, "/skyprobe map <step>")):
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
            check(var2 is not None and bool(var2.hasPermission(s)) == may,
                  "P. 0.4: AbstractCommand.hasPermission: /skyprobe map <step> %s for %s" % ("allowed" if may else "refused", who))
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
    check(b"/skyprobe map: " in plug and b" minimap probes, each off until an op starts it" in plug,
          "M. 0.4: the ready line names the map probes (off until an op starts one)")
    run_map(locals())


# ======================================================================================================== 0.4: the map probe sections
def run_map(L):
    """0.4: the map probe sections N G T Q H U Y R Z (every new code path in the jar runs here; see the header)."""
    import struct
    import zlib as _zlib
    import hashlib
    import random
    import math
    import jpype
    from jpype import JClass, JInt, JShort, JArray, JByte, JLong, JDouble, JFloat, JString, JObject
    import skyyui as SUI
    dump, U, jf, field, CP = L["dump"], L["U"], L["jf"], L["field"], L["CP"]
    CtNewMethod, CtNewConstructor, CtField = L["CtNewMethod"], L["CtNewConstructor"], L["CtField"]
    hcls, world, queued, run_all, pref, chats = L["hcls"], L["world"], L["queued"], L["run_all"], L["pref"], L["chats"]
    NET, UCB, Cls, loader, PL, names = L["NET"], L["UCB"], L["Cls"], L["loader"], L["PL"], L["names"]
    cmds = L["cmds"]
    md = dump["map"]
    KEY, SKEY, Z, T = md["key"], md["skyyhud_key"], int(md["z"]), int(md["tile"])
    ids = md["ids"]
    MPROBE, MPNG, MGEO = JClass(PKG + "MapProbe"), JClass(PKG + "MapPng"), JClass(PKG + "MapGeo")
    MSESS, MHUD, MUI, MASSET = JClass(PKG + "MapSess"), JClass(PKG + "MapHud"), JClass(PKG + "MapUi"), JClass(PKG + "MapAsset")
    MREQ, MP3C = JClass(PKG + "MapReq"), JClass(PKG + "MapP3")
    MIMc = JClass("com.hypixel.hytale.protocol.packets.worldmap.MapImage")
    MCHc = JClass("com.hypixel.hytale.protocol.packets.worldmap.MapChunk")
    UWMc = JClass("com.hypixel.hytale.protocol.packets.worldmap.UpdateWorldMap")
    CWMc = JClass("com.hypixel.hytale.protocol.packets.worldmap.ClearWorldMap")
    MMKc = JClass("com.hypixel.hytale.protocol.packets.worldmap.MapMarker")
    BFA = JClass("com.hypixel.hytale.server.core.universe.world.chunk.palette.BitFieldArr")
    CMAc = JClass("com.hypixel.hytale.server.core.asset.common.CommonAsset")
    HMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.hud.HudManager")
    UUID = JClass("java.util.UUID")
    SYS = JClass("java.lang.System")
    rnd = random.Random(20261003)

    def pyb(arr):
        if arr is None:
            return None
        try:
            return bytes(memoryview(arr))
        except Exception:
            return bytes((int(x) & 255) for x in arr)

    def s32(v):
        v &= 0xffffffff
        return v - (1 << 32) if v >= (1 << 31) else v

    def rgba(c):
        c &= 0xffffffff
        return (c >> 24) & 255, (c >> 16) & 255, (c >> 8) & 255, c & 255

    def jb(b):
        return JArray(JByte)(bytes(b))

    def tail():
        return [str(x) for x in PL.tail()]

    # ================================================================================================ N. the PNG encoder
    def png_decode(b):
        if b[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError("PNG signature")
        pos, chunks = 8, []
        while pos < len(b):
            ln = struct.unpack(">I", b[pos:pos + 4])[0]
            typ, data = b[pos + 4:pos + 8], b[pos + 8:pos + 8 + ln]
            crc = struct.unpack(">I", b[pos + 8 + ln:pos + 12 + ln])[0]
            if _zlib.crc32(typ + data) & 0xffffffff != crc:
                raise ValueError("CRC of %s" % typ)
            chunks.append((typ.decode("ascii"), data))
            pos += 12 + ln
        if pos != len(b):
            raise ValueError("bytes after IEND")
        kinds = [c[0] for c in chunks]
        if kinds[0] != "IHDR" or kinds[-1] != "IEND" or kinds.count("IHDR") != 1:
            raise ValueError("chunk order %s" % kinds)
        w, h, depth, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", chunks[0][1])
        if (comp, filt, inter) != (0, 0, 0):
            raise ValueError("IHDR methods %s" % ((comp, filt, inter),))
        plte = b"".join(d for t, d in chunks if t == "PLTE") or None
        trns = b"".join(d for t, d in chunks if t == "tRNS") or None
        raw = _zlib.decompress(b"".join(d for t, d in chunks if t == "IDAT"))
        chans = {3: 1, 6: 4}[ctype]
        bpp = max(1, (depth * chans) // 8)
        stride = (w * depth * chans + 7) // 8
        if len(raw) != h * (stride + 1):
            raise ValueError("raw size %d, expected %d" % (len(raw), h * (stride + 1)))
        rows, prev, p, filters = [], bytearray(stride), 0, set()
        for y in range(h):
            ft = raw[p]
            line = bytearray(raw[p + 1:p + 1 + stride])
            p += 1 + stride
            filters.add(ft)
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                up, c = prev[i], (prev[i - bpp] if i >= bpp else 0)
                if ft == 1:
                    line[i] = (line[i] + a) & 255
                elif ft == 2:
                    line[i] = (line[i] + up) & 255
                elif ft == 3:
                    line[i] = (line[i] + ((a + up) >> 1)) & 255
                elif ft == 4:
                    pp = a + up - c
                    pa, pb, pc = abs(pp - a), abs(pp - up), abs(pp - c)
                    line[i] = (line[i] + (a if pa <= pb and pa <= pc else (up if pb <= pc else c))) & 255
                elif ft != 0:
                    raise ValueError("filter %d" % ft)
            rows.append(line)
            prev = line
        px = []
        for y in range(h):
            row = rows[y]
            for x in range(w):
                if ctype == 3:
                    bit = x * depth
                    v = (row[bit >> 3] >> (8 - depth - (bit & 7))) & ((1 << depth) - 1)
                    if plte is None or 3 * v + 2 >= len(plte):
                        raise ValueError("index %d outside PLTE" % v)
                    px.append((plte[3 * v], plte[3 * v + 1], plte[3 * v + 2], trns[v] if trns is not None and v < len(trns) else 255))
                else:
                    px.append(tuple(row[4 * x:4 * x + 4]))
        return {"w": w, "h": h, "depth": depth, "ctype": ctype, "kinds": kinds, "px": px, "plte": plte, "trns": trns,
                "filters": filters}

    def py_unpack(packed, bits, n):
        out = []
        for i in range(n):
            bit, v, got = i * bits, 0, 0
            while got < bits:
                p = bit + got
                bi, off = p >> 3, p & 7
                take = min(8 - off, bits - got)
                v |= (((packed[bi] if bi < len(packed) else 0) >> off) & ((1 << take) - 1)) << got
                got += take
            out.append(v)
        return out

    def engine_image(w, h, ncol, alpha=True, bits=None, idx=None):
        """a MapImage packed with the ENGINE's BitFieldArr (what ImageBuilder.encodeToPalette does)"""
        pal = [s32((rnd.randrange(1 << 24) << 8) | (rnd.choice([0, 64, 128, 255, 255, 255]) if alpha else 255)) for _k in range(ncol)]
        if bits is None:
            bits = 4 if ncol <= 16 else (8 if ncol <= 256 else (12 if ncol <= 4096 else 16))
        if idx is None:
            idx = [rnd.randrange(ncol) for _i in range(w * h)]
        bf = BFA(JInt(bits), JInt(w * h))
        for i, v in enumerate(idx):
            bf.set(JInt(i), JInt(v))
        packed = bf.get()
        return MIMc(JInt(w), JInt(h), JArray(JInt)(pal), JByte(bits), packed), pal, idx, bits, pyb(packed)

    def want_png(w, h, pal, idx, scale):
        n = len(pal)
        ct = 3 if n <= 256 else 6
        depth = (1 if n <= 2 else 2 if n <= 4 else 4 if n <= 16 else 8) if n <= 256 else 8
        return ct, depth, [rgba(pal[idx[(y // scale) * w + x // scale]]) for y in range(h * scale) for x in range(w * scale)]

    def check_png(png, w, h, pal, idx, scale, what):
        try:
            d = png_decode(png)
        except Exception as ex:
            check(False, "N. %s: decodes as a PNG (%s)" % (what, ex))
            return None
        ct, depth, exp = want_png(w, h, pal, idx, scale)
        kinds_ok = d["kinds"][:2] == ["IHDR", "PLTE"] if ct == 3 else d["kinds"][1] == "IDAT"
        check(d["w"] == w * scale and d["h"] == h * scale and d["ctype"] == ct and d["depth"] == depth and kinds_ok
              and d["px"] == exp, "N. %s: %dx%d %s %d-bit PNG, every pixel = the palette colour of its index%s" % (
                  what, w * scale, h * scale, "indexed" if ct == 3 else "RGBA", depth,
                  "" if d["px"] == exp else " (first difference at %d)" % next(i for i, (a, b) in enumerate(zip(d["px"], exp)) if a != b)))
        return d

    cases = [(16, 16, 3, True), (16, 16, 16, True), (16, 16, 17, False), (16, 16, 200, True), (8, 8, 2, False), (32, 32, 300, True),
             (32, 32, 1024, True), (16, 16, 256, True), (16, 16, 5000, False), (1, 1, 1, True), (17, 5, 9, True), (24, 24, 4, True)]
    for (w, h, ncol, alpha) in cases:
        m, pal, idx, bits, packed = engine_image(w, h, ncol, alpha)
        check([int(x) for x in MPNG.unpack(jb(packed), JInt(bits), JInt(w * h))] == idx == py_unpack(packed, bits, w * h),
              "N. MapPng.unpack = the engine's BitFieldArr layout (= the Python reader), %d colours, %d-bit, %dx%d" % (ncol, bits, w, h))
        check(pyb(MPNG.pack(JArray(JInt)(idx), JInt(bits))) == packed,
              "N. MapPng.pack writes the engine's BitFieldArr bytes (%d-bit, %d values)" % (bits, w * h))
        for sc in (1, 2, 4):
            if w * sc > 1024:
                continue
            check_png(pyb(MPNG.fromMapImage(m, JInt(sc))), w, h, pal, idx, sc, "%dx%d %d colours (%d-bit) x%d" % (w, h, ncol, bits, sc))
    # a value split over two bytes (12 bits) and the image() helper (bits by palette size, like ImageBuilder.calculateBitsRequired)
    for ncol, want_bits in ((2, 4), (16, 4), (17, 8), (256, 8), (257, 12), (4096, 12), (4097, 16)):
        idx = [rnd.randrange(ncol) for _i in range(64)]
        im = MPNG.image(JInt(8), JInt(8), JArray(JInt)([s32(rnd.randrange(1 << 32)) for _k in range(ncol)]), JArray(JInt)(idx))
        check((int(im.bitsPerIndex) & 255) == want_bits == int(MPNG.bitsFor(JInt(ncol)))
              and py_unpack(pyb(im.packedIndices), want_bits, 64) == idx,
              "N. MapPng.image: %d colours -> %d bits (the engine's rule), indices read back" % (ncol, want_bits))
    # every MapImage the encoder refuses -> null (the slot then shows the test pattern; the server never throws)
    m0, pal0, idx0, bits0, packed0 = engine_image(16, 16, 3)

    def mim(w, h, pal, bits, packed):
        return MIMc(JInt(w), JInt(h), None if pal is None else JArray(JInt)(pal), JByte(bits), None if packed is None else jb(packed))

    bad_idx = list(idx0)
    bad_idx[37] = 7                                                   # 3 colours, an index 7 in the 4-bit data
    refused = [("no image", None, 1), ("scale 0", m0, 0), ("scale 9", m0, 9), ("width 0", mim(0, 16, pal0, 4, packed0), 1),
               ("width 513", mim(513, 1, pal0, 4, bytes(300)), 1), ("1025 px after scaling", mim(342, 1, pal0, 4, bytes(200)), 3),
               ("no palette", mim(16, 16, None, 4, packed0), 1), ("an empty palette", mim(16, 16, [], 4, packed0), 1),
               ("0 bits", mim(16, 16, pal0, 0, packed0), 1), ("17 bits", mim(16, 16, pal0, 17, packed0), 1),
               ("no packed data", mim(16, 16, pal0, 4, None), 1), ("packed data too short", mim(16, 16, pal0, 4, packed0[:100]), 1),
               ("an index outside the palette", mim(16, 16, pal0, 4, pyb(MPNG.pack(JArray(JInt)(bad_idx), JInt(4)))), 1)]
    for what, mm, sc in refused:
        try:
            r_ = MPNG.fromMapImage(mm, JInt(sc))
            err = None
        except Exception as ex:
            r_, err = "threw", ex
        check(r_ is None and err is None, "N. a MapImage with %s is refused (null, no exception): %s" % (what, err or r_))

    # ---- the generated pictures: redrawn in Python from the same integer geometry, then the PNG round trip
    def py_mask(d):
        return [1 if (2 * x + 1 - d) ** 2 + (2 * y + 1 - d) ** 2 <= d * d else 0 for y in range(d) for x in range(d)]

    def py_ring(d):
        b0, b1, b2, b3 = md["ring_bands"]
        tk = md["north_tick"]
        out = []
        for y in range(d):
            for x in range(d):
                dx, dy = 2 * x + 1 - d, 2 * y + 1 - d
                r2 = dx * dx + dy * dy
                v = 1 if b0 <= r2 < b1 else (2 if b1 <= r2 < b2 else (1 if b2 <= r2 < b3 else 0))
                if y < tk and abs(dx) <= 2 * (tk - y):
                    v = 3
                out.append(v)
        return out

    def py_tri(ax, ay, bx, by, cx, cy, px, py):
        d1 = (bx - ax) * (py - ay) - (by - ay) * (px - ax)
        d2 = (cx - bx) * (py - by) - (cy - by) * (px - bx)
        d3 = (ax - cx) * (py - cy) - (ay - cy) * (px - cx)
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))

    def py_arrow(b, s=24):
        v = md["arrow_v"][8 * b:8 * b + 8]
        idx = [2 if (py_tri(v[0], v[1], v[2], v[3], v[4], v[5], 2 * x + 1, 2 * y + 1) or
                     py_tri(v[0], v[1], v[4], v[5], v[6], v[7], 2 * x + 1, 2 * y + 1)) else 0 for y in range(s) for x in range(s)]
        out = list(idx)
        for y in range(s):
            for x in range(s):
                if idx[y * s + x] == 0 and ((x > 0 and idx[y * s + x - 1] == 2) or (x + 1 < s and idx[y * s + x + 1] == 2) or
                                            (y > 0 and idx[(y - 1) * s + x] == 2) or (y + 1 < s and idx[(y + 1) * s + x] == 2)):
                    out[y * s + x] = 1
        return out

    def py_picture(s=128):
        out = []
        for y in range(s):
            for x in range(s):
                v = (1 if x >= s // 2 else 0) + (2 if y >= s // 2 else 0)
                dx, dy = 2 * x + 1 - s, 2 * y + 1 - s
                r2 = dx * dx + dy * dy
                if 88 * 88 <= r2 <= 100 * 100:
                    v = 5
                if (x == y or x == y + 1) and r2 < 88 * 88:
                    v = 5
                if 8 <= y < 30 and abs(dx) <= 2 * (y - 8):
                    v = 6
                if x < 3 or y < 3 or x >= s - 3 or y >= s - 3:
                    v = 4
                out.append(v)
        return out

    def py_test(s=16):
        return [1 if (x == 0 or y == 0 or x == s - 1 or y == s - 1) else (2 if x == y else 0) for y in range(s) for x in range(s)]

    gens = [("mask", MPNG.mask(JInt(md["clip"])), py_mask(md["clip"]), md["pal_mask"], md["clip"]),
            ("ring", MPNG.ring(JInt(md["ring"])), py_ring(md["ring"]), md["pal_ring"], md["ring"])]
    gens += [("arrow %d" % b, MPNG.arrow(JInt(b)), py_arrow(b), md["pal_arrow"], md["arrow"]) for b in range(8)]
    gens += [("picture %d" % v, MPNG.picture(JInt(v)), py_picture(), md["pal_pic"][v], md["p1_pic"]) for v in range(3)]
    gens += [("test tile %d" % k, MPNG.testTile(JInt(k)), py_test(), md["pal_test"][k], 16) for k in range(2)]
    SIZES = {}
    for what, m, exp_idx, pal, size in gens:
        bits = int(m.bitsPerIndex) & 255
        got = py_unpack(pyb(m.packedIndices), bits, size * size)
        check(int(m.width) == size == int(m.height) and [int(x) for x in m.palette] == pal and got == exp_idx,
              "N. %s: the MapImage = the Python redraw (%dx%d, palette from the kit colours, %d-bit)" % (what, size, size, bits))
        png = pyb(MPNG.fromMapImage(m, JInt(1)))
        SIZES[what] = len(png)
        check_png(png, size, size, pal, exp_idx, 1, what)
    mi = py_mask(md["clip"])
    r = md["clip"] // 2
    check(abs(sum(mi) - math.pi * r * r) / (math.pi * r * r) < 0.01 and mi[r * md["clip"] + r] == 1 and mi[0] == 0 and mi[-1] == 0,
          "N. the mask is an opaque disc of radius %d (%d px) with clear corners" % (r, sum(mi)))
    ri, d = py_ring(md["ring"]), md["ring"]
    check(ri[(d // 2) * d + d // 2] == 0 and ri[(d // 2) * d + d // 2 + 81] == 2 and ri[(d // 2) * d + d // 2 + 79] == 1
          and ri[2 * d + d // 2] == 3, "N. the ring: clear centre, dark edge at 79 px, light band at 81 px, the gold north tick on top")
    def rot_px(idx, s=24):                                        # a picture turned 90 degrees clockwise (pixel (x, y) -> (23 - y, x))
        out = [0] * (s * s)
        for y in range(s):
            for x in range(s):
                out[x * s + (s - 1 - y)] = idx[y * s + x]
        return out

    arr = [py_arrow(b) for b in range(8)]
    n_ = arr[0]
    rows = [y for y in range(24) if any(n_[y * 24 + x] == 2 for x in range(24))]
    top = [x for x in range(24) if n_[rows[0] * 24 + x] == 2]
    low = [x for x in range(24) if n_[rows[-1] * 24 + x] == 2]
    check(min(top) >= 10 and max(top) <= 13 and min(low) < 8 and max(low) > 15 and sum(1 for v in n_ if v == 1) > 20,
          "N. the north arrow: its tip at the top centre (row %d, x %s), its two feet at the bottom (row %d), outlined" % (rows[0], top, rows[-1]))
    ne = arr[1]
    tipne = max(((x, y) for y in range(24) for x in range(24) if ne[y * 24 + x] == 2), key=lambda p: p[0] - p[1])
    check(tipne[0] - tipne[1] > 10, "N. the north-east arrow's tip is at the top right (%s)" % (tipne,))
    for b in range(2, 8):
        check(arr[b] == rot_px(arr[b - 2]), "N. arrow %d = arrow %d turned 90 degrees clockwise (exact)" % (b, b - 2))
    check(len(set(SIZES[k] for k in ("picture 0", "picture 1", "picture 2"))) >= 1 and
          len(set(pyb(MPNG.fromMapImage(MPNG.picture(JInt(v)), JInt(1))) for v in range(3))) == 3,
          "N. the three P1 / P3 pictures are three different PNGs (a new asset each)")
    # sizes of real-looking map pieces (the in-game log reports the real ones)
    terrain = [((x + y) // 3 + (x * y) % 2) % 10 for y in range(16) for x in range(16)]
    flat = [0 if (x * 7 + y * 3) % 11 else 1 for y in range(16) for x in range(16)]
    for what, w, ncol, idx in (("terrain-like 16 px, 10 colours", 16, 10, terrain), ("flat 16 px, 2 colours", 16, 2, flat),
                               ("random 16 px, 16 colours", 16, 16, None), ("random 16 px, 256 colours", 16, 256, None),
                               ("random 32 px (HIGH), 300 colours", 32, 300, None)):
        m, pal, idx_, bits, packed = engine_image(w, w, ncol, False, idx=idx)
        SIZES[what] = len(pyb(MPNG.fromMapImage(m, JInt(1))))
        SIZES[what + " x2"] = len(pyb(MPNG.fromMapImage(m, JInt(2)))) if w * 2 <= 1024 else 0
        SIZES[what + " (protocol MapImage)"] = int(m.computeSize())
    print("   PNG sizes (bytes): " + ", ".join("%s %d" % (k, v) for k, v in SIZES.items()))
    # encode time per tile, inside the JVM (no Python call per tile)
    eb = CP.makeClass("skyyuiprobeharness.EncBench")
    eb.addMethod(CtNewMethod.make(
        "public static long run(com.hypixel.hytale.protocol.packets.worldmap.MapImage m, int scale, int n) {\n"
        "  long t0 = System.nanoTime();\n  for (int i = 0; i < n; i++) com.skyy.uiprobe.MapPng.fromMapImage(m, scale);\n"
        "  return System.nanoTime() - t0;\n}", eb))
    eb.writeFile(hcls)
    EB = JClass("skyyuiprobeharness.EncBench")
    mt = engine_image(16, 16, 10, False, idx=terrain)[0]
    EB.run(mt, JInt(1), JInt(2000))                                  # warm up
    ns1 = int(EB.run(mt, JInt(1), JInt(5000))) / 5000.0
    ns2 = int(EB.run(mt, JInt(2), JInt(5000))) / 5000.0
    check(ns1 < 2000000, "N. a 16 px tile encodes in %.1f us (x2: %.1f us) on this PC - 81 tiles = %.2f ms" % (ns1 / 1000, ns2 / 1000,
                                                                                                         81 * ns1 / 1e6))
    print("N. PNG encoder done (%d cases, %d generated pictures, %.1f us per 16 px tile)" % (len(cases), len(gens), ns1 / 1000))

    # ================================================================================================ G. the pan / ring-buffer math
    def f32(v):
        return struct.unpack("f", struct.pack("f", v))[0]

    def py_chunk(v):
        return int(math.floor(v / 32.0))

    def py_slot(cx, cz):
        return (cx % 9) + 9 * (cz % 9)

    def py_round(x):
        return int(math.floor(x + 0.5))                               # Java Math.round(double)

    def py_group(p, b):
        return py_round(md["clip"] // 2 - (p - b * 32.0) * T / 32.0)

    def py_bucket(y):
        if math.isnan(y) or math.isinf(y):
            return 0
        deg = -y * 180.0 / math.pi
        b = math.fmod(deg, 360.0)
        if b < 0.0:
            b += 360.0
        return int(math.floor((b + 22.5) / 45.0)) % 8

    for v in (0.0, 31.999, 32.0, -0.001, -32.0, -32.001, 1e6 + 0.5, -1e6 - 0.5, 15.5, -15.5):
        check(int(MGEO.chunkOf(JDouble(v))) == py_chunk(v), "G. chunkOf(%r) = %d" % (v, py_chunk(v)))
    bad = [(cx, cz) for cx in range(-20, 21, 3) for cz in range(-20, 21, 5) if int(MGEO.slot(JInt(cx), JInt(cz))) != py_slot(cx, cz)]
    check(not bad, "G. slot(cx, cz) = cx mod 9 + 9 (cz mod 9) with floor-mod for negatives: %s" % bad[:3])
    for cx, cz in ((0, 0), (-1, -1), (2147483647, -2147483648), (-2147483648, 2147483647), (123456, -654321)):
        k = int(MGEO.key(JInt(cx), JInt(cz)))
        check(int(MGEO.keyX(JLong(k))) == cx and int(MGEO.keyZ(JLong(k))) == cz, "G. key / keyX / keyZ round trip (%d, %d)" % (cx, cz))
    check(all(bool(MGEO.inGroup(JInt(c), JInt(MGEO.base(JInt(c))))) for c in range(-30, 30)) and
          [bool(MGEO.inGroup(JInt(c), JInt(0))) for c in (3, 4, 12, 13)] == [False, True, True, False],
          "G. inGroup: the window (centre +- 4) fits the 17 positions from base = centre - 8; centre 4-12 fit base 0")
    check(all(int(MGEO.groupPos(JDouble(p), JInt(b))) == py_group(p, b) for p in (0.0, 16.4, 16.5, -0.5, -1000.25, 4096.75)
              for b in (-40, 0, 3)), "G. groupPos = round(80 - (p - 32 b)): the player's block at the clip centre")
    yaws = [i * 0.01 for i in range(-1000, 1001)] + [k * math.pi / 8 for k in range(-20, 21)] + [math.pi / 8 + 1e-6, -math.pi / 8 - 1e-6]
    badb = [(y, int(MGEO.bucket(JFloat(y))), py_bucket(f32(y))) for y in yaws if int(MGEO.bucket(JFloat(y))) != py_bucket(f32(y))]
    check(not badb, "G. bucket(yaw) over %d yaws = the Python model: %s" % (len(yaws), badb[:3]))
    check([int(MGEO.bucket(JFloat(f32(v)))) for v in (0.0, -math.pi / 2, math.pi, math.pi / 2, -math.pi / 4)] == [0, 2, 4, 6, 1]
          and int(MGEO.bucket(JFloat(float("nan")))) == 0 and int(MGEO.bucket(JFloat(float("inf")))) == 0,
          "G. headings: yaw 0 = N, -pi/2 = E (Transform.getDirection: x = -sin yaw), pi = S, +pi/2 = W, -pi/4 = NE; NaN / inf -> N")

    gpr, gnet = pref("GeoTester", UUID.fromString("00000000-0000-0000-0000-0000000000f1"))

    def anchor_of(data):
        o = json.loads(data)["0"]

        def num(v):
            return v if isinstance(v, (int, float)) else (v.get("Value", v.get("value")) if isinstance(v, dict) else None)
        return dict((k, num(v)) for k, v in o.items())

    first_anchor = []

    def geo_session(px, pz, yaw, sharp=False):
        s = MSESS()
        s.pr = gpr
        s.uuid = gpr.getUuid()
        s.who = "GeoTester"
        s.sharp = sharp
        s.capture = True
        s.px, s.pz, s.yaw = px, pz, yaw
        s.ccx, s.ccz = int(MGEO.chunkOf(JDouble(px))), int(MGEO.chunkOf(JDouble(pz)))
        s.bx, s.bz = int(MGEO.base(JInt(s.ccx))), int(MGEO.base(JInt(s.ccz)))
        s.arrows = JArray(JString)(["arrow-%d" % i for i in range(8)])
        MPROBE.assign(s, None, True, JArray(JInt)([10000]))
        s.gl, s.gt = int(MGEO.groupPos(JDouble(px), JInt(s.bx))), int(MGEO.groupPos(JDouble(pz), JInt(s.bz)))
        s.arrow = int(MGEO.bucket(JFloat(yaw)))
        s.capText = MPROBE.capText(s)
        model = {"tiles": {}, "grid": (int(s.gl), int(s.gt)), "me": "arrow-%d" % int(s.arrow), "cap": str(s.capText)}
        for sl in range(81):
            k = int(s.slotKey[sl])
            model["tiles"][sl] = [(int(MGEO.keyX(JLong(k))) - int(s.bx)) * T, (int(MGEO.keyZ(JLong(k))) - int(s.bz)) * T, str(s.slotPath[sl])]
        return s, model

    def geo_apply(model, cm):
        cnt = {"tanchor": 0, "tpath": 0, "grid": 0, "me": 0, "cap": 0, "other": 0}
        for t, sel, data, text in cm:
            m_ = re.match(r"#%s(\d+)\.(Anchor|AssetPath)$" % re.escape(ids["tile"]), sel or "")
            if m_ and t == "Set":
                sl = int(m_.group(1))
                if m_.group(2) == "Anchor":
                    a_ = anchor_of(data)
                    if not first_anchor:
                        first_anchor.append(data)
                    model["tiles"][sl][0], model["tiles"][sl][1] = a_["Left"], a_["Top"]
                    cnt["tanchor"] += 1
                    if (a_.get("Width"), a_.get("Height")) != (T, T):
                        cnt["other"] += 1
                else:
                    model["tiles"][sl][2] = json.loads(data)["0"]
                    cnt["tpath"] += 1
            elif t == "Set" and sel == "#%s.Anchor" % ids["grid"]:
                a_ = anchor_of(data)
                model["grid"] = (a_["Left"], a_["Top"])
                cnt["grid"] += 1
                if (a_.get("Width"), a_.get("Height")) != (17 * T, 17 * T):
                    cnt["other"] += 1
            elif t == "Set" and sel == "#%s.AssetPath" % ids["me"]:
                model["me"] = json.loads(data)["0"]
                cnt["me"] += 1
            elif t == "Set" and sel == "#%s.Text" % ids["cap"]:
                model["cap"] = json.loads(data)["0"]
                cnt["cap"] += 1
            else:
                cnt["other"] += 1
        return cnt

    def geo_verify(s, model, px, pz, what):
        ccx, ccz, bx, bz = int(s.ccx), int(s.ccz), int(s.bx), int(s.bz)
        ok = ccx == py_chunk(px) and ccz == py_chunk(pz) and bx + 4 <= ccx <= bx + 12 and bz + 4 <= ccz <= bz + 12
        window = set((cx, cz) for cx in range(ccx - 4, ccx + 5) for cz in range(ccz - 4, ccz + 5))
        seen, worst = set(), 0.0
        gl, gt = model["grid"]
        for sl in range(81):
            k = int(s.slotKey[sl])
            cx, cz = int(MGEO.keyX(JLong(k))), int(MGEO.keyZ(JLong(k)))
            l_, t_, p_ = model["tiles"][sl]
            ok = ok and (cx, cz) in window and py_slot(cx, cz) == sl and l_ == (cx - bx) * T and t_ == (cz - bz) * T
            ok = ok and 0 <= l_ <= 16 * T and 0 <= t_ <= 16 * T and p_ == str(s.slotPath[sl])
            seen.add((cx, cz))
            worst = max(worst, abs(gl + l_ - (md["clip"] // 2 + cx * 32 - px)), abs(gt + t_ - (md["clip"] // 2 + cz * 32 - pz)))
        ok = ok and seen == window and worst <= 0.5 + 1e-9 and model["me"] == "arrow-%d" % int(s.arrow)
        return ok, worst

    walks = [((-40.0, 1500.5), 7, 1500), ((10.25, -10.75), 11, 800), ((100000.5, -100000.5), 13, 400)]
    totals = {"steps": 0, "swaps": 0, "diag": 0, "jumps": 0, "rebases": 0, "bad": [], "worst": 0.0}
    for (sx, sz), seed, steps in walks:
        wr = random.Random(seed)
        px, pz, yaw = sx, sz, 0.0
        s, model = geo_session(px, pz, yaw)
        ok0, w0 = geo_verify(s, model, px, pz, "start")
        check(ok0, "G. walk from (%s, %s): the first build puts the 81 window chunks in place (worst %.2f px)" % (sx, sz, w0))
        for i in range(steps):
            r_ = wr.random()
            if r_ < 0.55:
                px += wr.uniform(-6, 6)
                pz += wr.uniform(-6, 6)
            elif r_ < 0.80:                                            # exactly across one border (x or z)
                if wr.random() < 0.5:
                    px = (py_chunk(px) + (1 if wr.random() < 0.5 else 0)) * 32.0 + wr.choice([0.01, -0.01])
                else:
                    pz = (py_chunk(pz) + (1 if wr.random() < 0.5 else 0)) * 32.0 + wr.choice([0.01, -0.01])
            elif r_ < 0.90:                                            # a diagonal step over a corner
                px = (py_chunk(px) + 1) * 32.0 + 0.3
                pz = (py_chunk(pz) + 1) * 32.0 + 0.3
            elif r_ < 0.97:                                            # 2-8 chunks (a sprint / a jump)
                px += wr.choice([-1, 1]) * wr.uniform(64, 260)
            else:                                                      # a teleport
                px += wr.choice([-1, 1]) * wr.uniform(500, 5000)
                pz += wr.choice([-1, 1]) * wr.uniform(500, 5000)
            yaw = f32(wr.uniform(-7, 7))
            before = [int(s.slotKey[sl]) for sl in range(81)]
            b0, oc, oz = int(s.rebases), int(s.ccx), int(s.ccz)
            b = UCB()
            MPROBE.move(s, b, JDouble(px), JDouble(pz), JFloat(yaw), JArray(JInt)([10000]))
            cnt = geo_apply(model, cmds(b))
            changed = sum(1 for sl in range(81) if int(s.slotKey[sl]) != before[sl])
            reb = int(s.rebases) != b0
            dx, dz = abs(int(s.ccx) - oc), abs(int(s.ccz) - oz)
            want = 81 if reb else changed
            if dx + dz == 1 and dx <= 1 and dz <= 1:
                totals["swaps"] += 1
                want_changed = 9
            elif dx == 1 and dz == 1:
                totals["diag"] += 1
                want_changed = 17
            elif dx or dz:
                totals["jumps"] += 1
                want_changed = 81 if max(dx, dz) >= 9 else 81 - (9 - dx) * (9 - dz)
            else:
                want_changed = 0
            totals["rebases"] += 1 if reb else 0
            ok, worst = geo_verify(s, model, px, pz, "step")
            totals["worst"] = max(totals["worst"], worst)
            if not (ok and changed == want_changed and cnt["tanchor"] == want and cnt["tpath"] >= changed and cnt["other"] == 0
                    and cnt["grid"] <= 1 and (cnt["grid"] == 1 or not reb)):
                totals["bad"].append((i, px, pz, ok, worst, changed, want_changed, cnt, reb))
            totals["steps"] += 1
    check(not totals["bad"], "G. %d steps on 3 random walks (negative and far coordinates): every step keeps the 81 window chunks on "
                             "screen where they belong (worst %.2f px), a 1-chunk step changes 9 tiles, a diagonal 17, a jump the "
                             "entering chunks, a re-base re-anchors 81, one grid Anchor at most, no stray command: %s" % (
                                 totals["steps"], totals["worst"], totals["bad"][:2]))
    check(totals["swaps"] > 200 and totals["diag"] > 50 and totals["jumps"] > 50 and totals["rebases"] > 50,
          "G. the walks crossed borders %d times, %d diagonals, %d jumps, %d re-bases" % (totals["swaps"], totals["diag"],
                                                                                          totals["jumps"], totals["rebases"]))
    print("   the first tile Anchor command: %s" % (first_anchor[:1],))
    # a still player: no command at all; a turn: only the arrow; new map pieces: only their AssetPaths (+ the caption)
    s, model = geo_session(5.5, 5.5, 0.0)
    b = UCB()
    MPROBE.move(s, b, JDouble(5.5), JDouble(5.5), JFloat(0.0), JArray(JInt)([10000]))
    check(len(cmds(b)) == 0, "G. a player standing still: no command (no periodic re-send)")
    b = UCB()
    MPROBE.move(s, b, JDouble(5.5), JDouble(5.5), JFloat(f32(-math.pi / 2)), JArray(JInt)([10000]))
    c_ = cmds(b)
    check([(t, sel) for t, sel, _d, _x in c_] == [("Set", "#%s.AssetPath" % ids["me"])] and json.loads(c_[0][2])["0"] == "arrow-2",
          "G. turning east: exactly one command, the arrow picture (arrow-2): %s" % c_)
    ims = {}
    for cx in range(-1, 2):
        ims[(cx, 0)] = engine_image(16, 16, 5, False)[0]
        s.tiles.put(JLong(int(MGEO.key(JInt(cx), JInt(0)))), ims[(cx, 0)])
    b = UCB()
    gnet.batches = None
    MPROBE.move(s, b, JDouble(5.5), JDouble(5.5), JFloat(f32(-math.pi / 2)), JArray(JInt)([10000]))
    c_ = cmds(b)
    paths = [(sel, json.loads(d)["0"]) for t, sel, d, x in c_ if sel.endswith(".AssetPath")]
    check(len(paths) == 3 and int(s.srcMap) == 3 and all(p.startswith(md["asset_dir"] + "t-") for _s, p in paths)
          and any(sel == "#%s.Text" % ids["cap"] for t, sel, d, x in c_) and gnet.batches is not None and int(gnet.batches.size()) == 3,
          "G. 3 map pieces from the stream: their 3 slots get new pictures (t-<hash>), sent first (3 asset writes), the caption "
          "changes: %s" % paths)
    b = UCB()
    MPROBE.move(s, b, JDouble(5.5), JDouble(5.5), JFloat(f32(-math.pi / 2)), JArray(JInt)([10000]))
    check(len(cmds(b)) == 0, "G. ... the same pieces again: nothing re-sent, no command")
    # the encode budget: 81 new pictures with a budget of 5 -> 5 encoded now, the rest keep the test pattern and s.more asks for more
    s2, model2 = geo_session(-300.5, 77.5, 0.0)
    for sl in range(81):
        k = int(s2.slotKey[sl])
        s2.tiles.put(JLong(k), engine_image(8, 8, 3, False)[0])
    b = UCB()
    MPROBE.move(s2, b, JDouble(-300.5), JDouble(77.5), JFloat(0.0), JArray(JInt)([5]))
    check(int(s2.srcMap) == 5 and bool(s2.more), "G. the encode budget: 5 of 81 new pieces encoded in one tick, s.more set (%d, %s)" % (
        int(s2.srcMap), bool(s2.more)))
    for _i in range(20):
        if not bool(s2.more):
            break
        s2.more = False
        MPROBE.move(s2, UCB(), JDouble(-300.5), JDouble(77.5), JFloat(0.0), JArray(JInt)([40]))
    check(int(s2.srcMap) == 81 and not bool(s2.more), "G. ... the next ticks finish the rest (81 map pieces, s.more cleared)")
    print("G. pan math done (%d walk steps, worst offset %.2f px)" % (totals["steps"], totals["worst"]))

    # ================================================================================================ T. the outbound tap
    JLongC = JClass("java.lang.Long")
    PA = JClass("com.hypixel.hytale.server.core.io.adapter.PacketAdapters")
    GPH = JClass("com.hypixel.hytale.server.core.io.handlers.game.GamePacketHandler")
    outbound = jf(PA.class_, "outboundHandlers").get(None)
    handle_out = getattr(PA, "__handleOutbound")
    tpr, tnet = pref("TapTester", UUID.fromString("00000000-0000-0000-0000-0000000000f2"))
    tgph = U.allocateInstance(GPH.class_)
    field(GPH, "playerRef").set(tgph, tpr)
    MPROBE.SESS.clear()
    MPROBE.recountTaps()
    n0 = int(outbound.size())
    MPROBE.tapOn()
    MPROBE.tapOn()
    check(int(outbound.size()) == n0 + 1 and MPROBE.TAPF is not None, "T. tapOn twice (a second plugin start) = ONE outbound handler (%d -> %d)"
          % (n0, int(outbound.size())))

    def mk_upd(chunks, added=0, removed=0, null_arrays=False):
        if null_arrays:
            return UWMc(None, None, None)
        arr = JArray(MCHc)(len(chunks))
        for i, c in enumerate(chunks):
            arr[i] = None if c is None else MCHc(JInt(c[0]), JInt(c[1]), c[2])
        am = None
        if added:
            am = JArray(MMKc)(added)
            for i in range(added):
                am[i] = MMKc()
        rm = JArray(JString)(["marker%d" % i for i in range(removed)]) if removed else None
        return UWMc(arr, am, rm)

    imgA, imgB = engine_image(16, 16, 6, False)[0], engine_image(16, 16, 12, False)[0]
    p1 = mk_upd([(0, 0, imgA), (1, 0, imgB), (2, 0, None)], added=2, removed=1)
    blocked = bool(handle_out(tgph, p1))
    check(not blocked, "T. no map probe on: the engine's PacketAdapters passes the packet on (the tap does one volatile read)")
    ts = MSESS()
    ts.uuid = tpr.getUuid()
    ts.pr = tpr
    ts.who = "TapTester"
    MPROBE.SESS.put(ts.uuid, ts)
    MPROBE.recountTaps()
    handle_out(tgph, p1)
    check(int(ts.qn.get()) == 0 and int(ts.seen.get()) == 0 and int(MPROBE.TAPS) == 0,
          "T. a session that asked for nothing (no p2 / p4 / p5): nothing kept")
    ts.wants = True
    MPROBE.recountTaps()
    check(int(MPROBE.TAPS) == 1, "T. p2 / p4 / p5 on: TAPS = 1")
    others = [CWMc(), MMKc(), JClass("com.hypixel.hytale.protocol.packets.setup.AssetFinalize")(),
              JClass("com.hypixel.hytale.protocol.packets.interface_.CustomHud")(JString(KEY), JInt(0), True, None),
              JClass("com.hypixel.hytale.protocol.packets.inventory.MoveItemStack")(JInt(1), JInt(2), JInt(3), JInt(4), JInt(5))]
    stream = [p1, mk_upd([(3, 0, imgA)]), mk_upd([None, (4, 0, None), None]), mk_upd([], 3, 0), mk_upd(None, null_arrays=True), others[0],
              mk_upd([(5, 0, imgB), (6, 0, imgA)], removed=2)]
    want_q = 0
    for p_ in stream + others[2:]:
        try:
            r_ = bool(handle_out(tgph, p_)) if not isinstance(p_, MMKc) else False
            err = None
        except Exception as ex:
            r_, err = None, ex
        check(r_ is False and err is None, "T. %s through the engine's outbound adapters: passed on, no exception" % p_.getClass().getSimpleName())
    want_q = len(stream)
    check(int(ts.qn.get()) == want_q and int(ts.seen.get()) == want_q and int(ts.q.size()) == want_q,
          "T. the tap kept exactly the %d map packets (UpdateWorldMap + ClearWorldMap), nothing else: %d" % (want_q, int(ts.q.size())))
    NETW = JClass(PKG + "MapTap")()
    try:
        NETW.accept(None, None)
        NETW.accept(tpr, None)
        NETW.accept(None, p1)
        err = None
    except Exception as ex:
        err = ex
    check(err is None and int(MPROBE.TAPERR.get()) == 0, "T. MapTap.accept never throws (null player / packet) and counts no error: %s" % err)
    ts.tapMode = 4
    ts.tapInfo = "world 'tap test'"
    now = int(SYS.currentTimeMillis())
    MPROBE.resetStats(ts, JLong(now - 12000))
    def size_or_none(p_):
        try:
            return int(p_.computeSize())
        except Exception:
            return None                                               # null MapChunk entries: the engine's own computeSize NPEs
    sizes_ = [size_or_none(p_) for p_ in stream if isinstance(p_, UWMc)]
    want_bytes = sum(x for x in sizes_ if x is not None)
    check(sizes_.count(None) == 1, "T. (a packet with null MapChunk entries cannot even be sized by the engine - the real stream never "
                                   "has them; drain counts its chunks and skips its bytes without failing)")
    MPROBE.drain(ts, JLong(now))
    check((int(ts.upd), int(ts.chunks), int(ts.nulls), int(ts.imgs), int(ts.mAdd), int(ts.mRem), int(ts.clears), int(ts.bytes), int(ts.qn.get()))
          == (6, 7, 2, 5, 5, 3, 1, want_bytes, 0) and int(ts.tickMax) == 6,
          "T. drain counts: 6 UpdateWorldMap, 7 chunks (2 null = unloads, null entries skipped), 5 pictures, 5 markers added / 3 removed, "
          "1 ClearWorldMap, %d bytes (computeSize), max 6 in one tick: %s" % (want_bytes, (int(ts.upd), int(ts.chunks), int(ts.nulls),
                                                                                        int(ts.imgs), int(ts.mAdd), int(ts.mRem),
                                                                                        int(ts.clears), int(ts.bytes))))
    check((int(ts.minW), int(ts.maxW), int(ts.minPal), int(ts.maxPal), str(MPROBE.bitsText(JInt(ts.bitsMask)))) == (16, 16, 6, 12, "4"),
          "T. picture sizes seen: 16 px, 6-12 colours, 4-bit")
    line = str(MPROBE.tapLine(ts, "test", JLong(now)))
    check(line.startswith("P4 (world 'tap test') 12.0 s: 6 UpdateWorldMap (max 6 in one 0.25 s), 7 chunks (2 null = unloads), 5 markers added "
                          "/ 3 removed, 1 ClearWorldMap, %d bytes; pictures 16 px, 6-12 colours, 4 bit - test" % want_bytes),
          "T. the summary line: %s" % line)
    MPROBE.resetStats(ts, JLong(now))
    check("NO map stream" in str(MPROBE.tapLine(ts, None, JLong(now))), "T. 0 UpdateWorldMap -> the line says NO map stream (map off or nothing new)")
    # P2's captured pieces: an image is kept per chunk, a null chunk removes it, a Clear clears, far pieces are pruned
    ts.capture = True
    ts.ccx, ts.ccz = 0, 0
    handle_out(tgph, mk_upd([(0, 0, imgA), (1, 1, imgB)]))
    MPROBE.drain(ts, JLong(now))
    check(int(ts.tiles.size()) == 2 and ts.tiles.get(JLongC.valueOf(int(MGEO.key(JInt(1), JInt(1))))) == imgB and bool(ts.tilesDirty),
          "T. capture: the map pieces are kept per chunk (the same MapImage object), tilesDirty asks for a pan")
    handle_out(tgph, mk_upd([(1, 1, None)]))
    MPROBE.drain(ts, JLong(now))
    check(int(ts.tiles.size()) == 1, "T. ... a null chunk (an unload) removes its piece")
    handle_out(tgph, CWMc())
    MPROBE.drain(ts, JLong(now))
    check(int(ts.tiles.size()) == 0, "T. ... ClearWorldMap clears them all")
    for i in range(5000):
        ts.tiles.put(JLongC.valueOf(int(MGEO.key(JInt(100 + i), JInt(0)))), imgA)
    ts.tiles.put(JLongC.valueOf(int(MGEO.key(JInt(3), JInt(-3)))), imgB)
    handle_out(tgph, mk_upd([(2, 2, imgA)]))
    MPROBE.drain(ts, JLong(now))
    check(int(ts.tiles.size()) == 2, "T. ... more than 4096 pieces: everything farther than 16 chunks is pruned (%d left)" % int(ts.tiles.size()))
    ts.capture = False
    ts.tiles.clear()
    # a burst far beyond the bound: the tap never blocks; 20,000 kept, the rest counted as dropped
    tb = CP.makeClass("skyyuiprobeharness.TapBench")
    tb.addMethod(CtNewMethod.make(
        "public static long run(com.hypixel.hytale.server.core.universe.PlayerRef pr, Object p, int n) {\n"
        "  long t0 = System.nanoTime();\n  for (int i = 0; i < n; i++) com.skyy.uiprobe.MapProbe.tap(pr, p);\n  return System.nanoTime() - t0;\n}", tb))
    tb.writeFile(hcls)
    TB = JClass("skyyuiprobeharness.TapBench")
    one = mk_upd([(9, 9, imgA)])
    ts.seen.set(0)
    ts.dropped.set(0)
    ns = int(TB.run(tpr, one, JInt(25000)))
    check(int(ts.qn.get()) == md["qmax"] and int(ts.dropped.get()) == 25000 - md["qmax"] and int(ts.seen.get()) == 25000,
          "T. a 25,000-packet burst: %d kept (the bound), %d counted as dropped, every packet seen, no block (%.0f ns per packet)" % (
              int(ts.qn.get()), int(ts.dropped.get()), ns / 25000.0))
    MPROBE.drain(ts, JLong(now))
    check(int(ts.qn.get()) == 0 and int(ts.q.size()) == 0, "T. ... the next tick drains all of it")
    ts.wants = False
    MPROBE.recountTaps()
    TB.run(tpr, one, JInt(100000))
    ns_off = int(TB.run(tpr, one, JInt(1000000))) / 1e6
    ts.wants = True
    MPROBE.recountTaps()
    TB.run(tpr, one, JInt(1000))
    MPROBE.drain(ts, JLong(now))
    ns_on = int(TB.run(tpr, one, JInt(10000))) / 1e4
    MPROBE.drain(ts, JLong(now))
    check(ns_off < 2000 and ns_on < 20000, "T. the tap costs %.0f ns per packet with nothing on and %.0f ns while a probe counts (the "
                                           "writer's thread is never held)" % (ns_off, ns_on))
    # 4 writer threads storm the tap while the tick thread drains: every packet counted exactly once
    st_ = CP.makeClass("skyyuiprobeharness.TapStorm")
    st_.addInterface(CP.get("java.lang.Runnable"))
    for f_ in ("public com.hypixel.hytale.server.core.universe.PlayerRef pr;", "public Object p;", "public int n;"):
        st_.addField(CtField.make(f_, st_))
    st_.addConstructor(CtNewConstructor.make(
        "public TapStorm(com.hypixel.hytale.server.core.universe.PlayerRef pr, Object p, int n) { this.pr = pr; this.p = p; this.n = n; }", st_))
    st_.addMethod(CtNewMethod.make("public void run() { for (int i = 0; i < this.n; i++) com.skyy.uiprobe.MapProbe.tap(this.pr, this.p); }", st_))
    st_.addMethod(CtNewMethod.make(
        "public static long storm(com.hypixel.hytale.server.core.universe.PlayerRef pr, Object p, int n, int k, com.skyy.uiprobe.MapSess s) throws Exception {\n"
        "  Thread[] ts = new Thread[k];\n  for (int i = 0; i < k; i++) { ts[i] = new Thread(new skyyuiprobeharness.TapStorm(pr, p, n)); ts[i].start(); }\n"
        "  long drains = 0L;\n  boolean alive = true;\n  while (alive) {\n    com.skyy.uiprobe.MapProbe.drain(s, System.currentTimeMillis());\n"
        "    drains = drains + 1L;\n    alive = false;\n    for (int i = 0; i < k; i++) { if (ts[i].isAlive()) alive = true; }\n  }\n"
        "  for (int i = 0; i < k; i++) ts[i].join();\n  com.skyy.uiprobe.MapProbe.drain(s, System.currentTimeMillis());\n  return drains;\n}", st_))
    st_.writeFile(hcls)
    STORM = JClass("skyyuiprobeharness.TapStorm")
    MPROBE.resetStats(ts, JLong(now))
    ts.seen.set(0)
    ts.dropped.set(0)
    drains = int(STORM.storm(tpr, one, JInt(20000), JInt(4), ts))
    check(int(ts.seen.get()) == 80000 and int(ts.upd) + int(ts.dropped.get()) == 80000 and int(ts.qn.get()) == 0 and int(ts.chunks) == int(ts.upd),
          "T. 4 threads x 20,000 packets while the tick drains (%d drains): seen 80,000 = counted %d + dropped %d, nothing lost or "
          "doubled" % (drains, int(ts.upd), int(ts.dropped.get())))
    # P5: the engine's ClearWorldMap (every world change) closes a world's count; the ready event names the next; 3 worlds at most
    ts.tapMode = 5
    ts.seg = 1
    ts.p5done = False
    ts.infoOpen = False
    ts.nextInfo = None
    ts.tapInfo = "world 'one'"
    MPROBE.resetStats(ts, JLong(now))
    tnet.sent = None
    for k in range(3):
        handle_out(tgph, mk_upd([(k, k, imgA), (k, k + 1, None)]))
        handle_out(tgph, CWMc())
        if k == 0:
            MPROBE.drain(ts, JLong(now))
            check(int(ts.seg) == 2 and str(ts.tapInfo) == "the next world" and bool(ts.infoOpen),
                  "T. P5: the first ClearWorldMap closes world 1 and opens world 2 (named when the ready event comes)")
            ts.tapInfo = "world 'two'"                                 # what handle('ready') does with infoOpen
            ts.infoOpen = False
            ts.nextInfo = "world 'three'"                              # a ready event that came BEFORE the next ClearWorldMap
    MPROBE.drain(ts, JLong(now))
    c_ = [x for x in chats(tnet) if x.startswith("[SkyyUiProbe] P5 world")]
    check(len(c_) == 3 and c_[0].startswith("[SkyyUiProbe] P5 world 1 of 3 (world 'one')") and c_[1].startswith(
        "[SkyyUiProbe] P5 world 2 of 3 (world 'two')") and c_[2].startswith("[SkyyUiProbe] P5 world 3 of 3 (world 'three')")
          and all("1 UpdateWorldMap" in x and "2 chunks (1 null = unloads)" in x and "1 ClearWorldMap" in x for x in c_)
          and bool(ts.p5done) and int(ts.tapEnd) <= now, "T. P5: three worlds, three summary lines (named by the ready event, also when "
                                                         "it came first), then it stops: %s" % c_)
    ts.tapMode = 0
    ts.wants = False
    MPROBE.SESS.clear()
    MPROBE.recountTaps()
    MPROBE.tapOff()
    check(int(outbound.size()) == n0 and MPROBE.TAPF is None, "T. tapOff removes the handler again")
    MPROBE.tapOff()
    check(int(outbound.size()) == n0, "T. a second tapOff is harmless")
    print("T. tap done (%.0f / %.0f ns per packet off / on)" % (ns_off, ns_on))

    # ================================================================================================ Q. the asset packets
    qpr, qnet = pref("AssetTester", UUID.fromString("00000000-0000-0000-0000-0000000000f3"))
    qs = MSESS()
    qs.pr = qpr
    qs.uuid = qpr.getUuid()
    qs.who = "AssetTester"
    MPROBE.DELIVERED.clear()
    png = pyb(MPNG.fromMapImage(engine_image(16, 16, 5, False)[0], JInt(1)))
    a = MPROBE.asset("t", jb(png))
    name, hsh = str(a.getName()), str(a.getHash())
    check(hsh == hashlib.sha256(png).hexdigest() == str(CMAc.hash(jb(png))) and name == md["asset_dir"] + "t-" + hsh[:16] + ".png"
          and pyb(a.bytes) == png, "Q. asset: name %s = the content hash (sha256 = CommonAsset.hash)" % name)
    check(MPROBE.asset("t", jb(png)) == a and MPROBE.asset("t", jb(png + b"")) == a, "Q. the same PNG = the same MapAsset object (one per picture)")
    am = MPROBE.asset("mask", jb(png))
    check(str(am.getName()) == md["mask_dir"] + md["mask_prefix"] + hsh[:16] + ".png" and str(MPROBE.maskRel(am)) == md["mask_prefix"] + hsh[:16] + ".png",
          "Q. the mask lives under UI/Custom/ and the markup names it relative to it: %s" % MPROBE.maskRel(am))
    check(pyb(a.getBlob().join()) == png, "Q. CommonAsset.getBlob (MapAsset.getBlob0) gives the bytes")
    qnet.sent = None
    qnet.batches = None
    nb = int(MPROBE.send(qs, a, False))
    bt = [qnet.batches.get(0).get(i) for i in range(int(qnet.batches.get(0).size()))] if qnet.batches is not None else []
    kinds_ = [str(p_.getClass().getSimpleName()) for p_ in bt]
    check(kinds_ == ["AssetInitialize", "AssetPart", "AssetFinalize"] and int(qnet.batches.size()) == 1,
          "Q. send: ONE write of AssetInitialize + AssetPart + AssetFinalize to that player: %s" % kinds_)
    if len(bt) == 3:
        check(str(bt[0].asset.name) == name and str(bt[0].asset.hash) == hsh and int(bt[0].size) == len(png) and pyb(bt[1].part) == png
              and nb == sum(int(p_.computeSize()) for p_ in bt),
              "Q. ... AssetInitialize(name, hash, %d bytes), the part = the PNG, %d bytes counted = computeSize" % (len(png), nb))
    check(qs.uuid is not None and MPROBE.delivered(qs.uuid).contains(name), "Q. ... the name is in this connection's 'already sent' list")
    nb2 = int(MPROBE.send(qs, a, False))
    check(nb2 == 0 and int(qnet.batches.size()) == 1 and int(qs.cachedHits) == 1, "Q. the same picture again: NOT sent (0 bytes, no packet)")
    nb3 = int(MPROBE.send(qs, a, True))
    check(nb3 == nb and int(qnet.batches.size()) == 2, "Q. force (P3 re-send): sent again")
    rb_ = int(MPROBE.rebuild(qs))
    last = qnet.sent.get(int(qnet.sent.size()) - 1)
    check(str(last.getClass().getSimpleName()) == "RequestCommonAssetsRebuild" and int(qnet.batches.size()) == 2 and rb_ == int(last.computeSize()),
          "Q. rebuild = ONE RequestCommonAssetsRebuild on its own (writeNoCache, %d bytes)" % rb_)
    big = MASSET(JString("UI/SkyyUiProbe/big-test.png"), JString("0" * 64), JArray(JByte)(6000000))
    MPROBE.send(qs, big, False)
    bb = qnet.batches.get(2)
    parts = [int(len(bb.get(i).part)) for i in range(1, int(bb.size()) - 1)]
    check(str(bb.get(0).getClass().getSimpleName()) == "AssetInitialize" and int(bb.get(0).size) == 6000000 and parts == [2621440, 2621440, 757120]
          and str(bb.get(int(bb.size()) - 1).getClass().getSimpleName()) == "AssetFinalize",
          "Q. a 6 MB picture goes in 2,621,440-byte parts like the engine's: %s" % parts)
    MPROBE.ASSETS.clear()
    print("Q. asset packets done")

    # ================================================================================================ H. the HUD command lists
    MAP_TRIAL = set(md["trial"])
    SAMPLE_PIC = md["asset_dir"] + "p1a-0123456789abcdef.png"
    SAMPLE_T = md["asset_dir"] + "t-0123456789abcdef.png"
    SAMPLE_MASK = md["mask_prefix"] + "0123456789abcdef.png"
    SAMPLE_RING = md["asset_dir"] + "ring-0123456789abcdef.png"
    SAMPLE_ME = md["asset_dir"] + "arrow0-0123456789abcdef.png"

    def as4(c):
        return (str(c.type), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                None if c.text is None else str(c.text))

    def doc_parts(cm):
        aps, sets_, other = [], [], []
        for t, sel, data, text in cm:
            if t == "AppendInline":
                aps.append((None if sel is None else sel.lstrip("#"), text))
            elif t == "Set" and sel.endswith((".Text", ".AssetPath")):
                sets_.append((sel, json.loads(data)["0"]))
            else:
                other.append((t, sel))
        return aps, sets_, other

    def doc_ids(aps):
        return set(i for _p, mk in aps for i in re.findall(r"#([A-Za-z0-9_]+)\s*\{", mk))

    def check_doc(cm, what):
        aps, sets_, other = doc_parts(cm)
        try:
            assert aps and aps[0][0] is None and all(p is not None for p, _m in aps[1:]), "one root first"
            SUI.check_markup(aps[0][1], prefix="SkyyPb", root=False)
            rest = SUI.Appends(aps[1:])
            rest.sets = [(sel[1:].split(".")[0], sel.split(".")[1], v) for sel, v in sets_]
            SUI.check_page(rest, "SkyyPb", known_parents=[ids["root"]])
            toks = SUI.proven_tokens(SUI.Appends(aps))
            bad = sorted(t for t, g in toks.items() if g is not None and t not in MAP_TRIAL)
            assert not bad, "tokens neither proven nor map trial: %s" % bad
            assert not any("_" in i for i in doc_ids(aps)), "underscore id"
            assert not other, "other commands in a document: %s" % other
            ok = True
        except Exception as ex:
            ok = "%s: %s" % (type(ex).__name__, ex)
        check(ok is True, "H. %s: the page checks pass (HUD root Anchor Full 0, rules, parents, no duplicate / underscore id, every "
                          "b.set target, only proven + the 3 map trial tokens): %s" % (what, ok))
        return aps, sets_

    G0, G1 = MPROBE.gen(JInt(0)), MPROBE.gen(JInt(1))
    GA = [str(MPROBE.gen(JInt(2 + i)).getName()) for i in range(8)]
    pics = [str(MPROBE.gen(JInt(10 + v)).getName()) for v in range(3)]
    check(all(re.fullmatch(re.escape(md["asset_dir"]) + r"(p1a|p1b|p3|ring|arrow[0-7])-[0-9a-f]{16}\.png", n_) for n_ in pics + GA + [str(G1.getName())])
          and re.fullmatch(re.escape(md["mask_dir"] + md["mask_prefix"]) + r"[0-9a-f]{16}\.png", str(G0.getName())),
          "H. the generated pictures' names: %s ..." % (pics[:1],))
    for pic, cap, what in ((pics[0], md["caps"]["p1a"], "P1a"), (pics[1], md["caps"]["p1b"], "P1b"), (pics[2], md["caps"]["p3"], "P3 armed"),
                           (pics[2], md["caps"]["p3re"], "P3 re-sent"), (pics[2], md["caps"]["p3no"], "P3 not re-sent")):
        b = UCB()
        MUI.p1(b, JString(pic), JString(cap))
        aps, sets_ = check_doc(cmds(b), "%s box" % what)
        exp = [(p, mk.replace(SAMPLE_PIC, pic)) for p, mk in md["p1"]["appends"]]
        check(aps == [(p, m) for p, m in exp] and sets_ == [("#%s.Text" % ids["cap"], cap)],
              "H. %s box = the build's validated template with the real picture %s and caption %r" % (what, pic, cap))
        check(SUI.text_width(cap, md["cap_fs"]) + md["fit_margin"] <= md["p1_pic"], "H. the %s caption fits its label" % what)
    # P2: a document as startP2 makes it (81 tiles from a session)
    s, model = geo_session(-77.25, 1999.5, 0.0)
    hud = MHUD(gpr, s, JInt(3))
    for sl in range(81):
        hud.tl[sl] = model["tiles"][sl][0]
        hud.tt[sl] = model["tiles"][sl][1]
        hud.tp[sl] = model["tiles"][sl][2]
    hud.mask, hud.ring, hud.me = MPROBE.maskRel(G0), G1.getName(), GA[0]
    hud.gl, hud.gt = model["grid"]
    hud.cap = MPROBE.capText(s)
    b = UCB()
    MUI.p2(b, hud)
    aps, sets_ = check_doc(cmds(b), "P2 minimap (81 tiles)")
    exp = []
    for p, mk in md["p2"]["appends"]:
        if mk.startswith("AssetImage #%s40 " % ids["tile"]):
            for i in range(81):
                exp.append((p, 'AssetImage #%s%d { Anchor: (Left: %d, Top: %d, Width: %d, Height: %d); AssetPath: "%s"; }' % (
                    ids["tile"], i, model["tiles"][i][0], model["tiles"][i][1], T, T, model["tiles"][i][2])))
        else:
            exp.append((p, mk.replace(SAMPLE_MASK, str(MPROBE.maskRel(G0))).replace(SAMPLE_RING, str(G1.getName()))
                        .replace(SAMPLE_ME, GA[0]).replace("Left: -176, Top: -176", "Left: %d, Top: %d" % model["grid"])))
    check(aps == exp and sets_ == [("#%s.Text" % ids["cap"], str(hud.cap))],
          "H. P2 document = the build's validated template, the tile line written 81 times with each slot's place and picture")
    p2_ids = doc_ids(aps)
    check(set("%s%d" % (ids["tile"], i) for i in range(81)) <= p2_ids and set(ids[k] for k in ("root", "box", "clip", "back", "grid", "ring", "me", "capbox", "cap")) <= p2_ids,
          "H. the P2 document creates the 81 tile ids + root / box / clip / back / grid / ring / me / caption")
    for t_ in md["p2_cap_samples"]:
        check(SUI.text_width(t_, md["cap_fs"]) + md["fit_margin"] <= md["p2_box"][0] - 12, "H. P2 caption %r fits (widest the tick writes)" % t_)
    # every command a pan sends targets an element of that document (from a short walk)
    sels = set()
    px_, pz_ = -77.25, 1999.5
    for k in range(60):
        px_ += 7.3
        pz_ -= 5.1
        b = UCB()
        MPROBE.move(s, b, JDouble(px_), JDouble(pz_), JFloat(f32(k * 0.4)), JArray(JInt)([10000]))
        for t, sel, data, text in cmds(b):
            sels.add(sel)
    bad = sorted(x for x in sels if x.lstrip("#").split(".")[0] not in p2_ids or x.split(".")[1] not in ("Anchor", "AssetPath", "Text"))
    check(sels and not bad, "H. every pan command (%d selectors) targets an element of the P2 document: Anchor / AssetPath / Text only: %s" % (
        len(sels), bad[:3]))
    print("H. HUD documents done")

    # ================================================================================================ U + Y: the HUD slot and every flow
    TSC = L["TSC"]
    Uni = JClass("com.hypixel.hytale.server.core.universe.Universe")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    CTc = JClass("com.hypixel.hytale.component.ComponentType")
    REFc, STOREc = JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.component.Store")
    ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    TRCc = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    HRTc = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    WMMc = JClass("com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapManager")
    WMSc = JClass("com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapSettings")
    UWMSc = JClass("com.hypixel.hytale.protocol.packets.worldmap.UpdateWorldMapSettings")
    IEc = JClass("com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapManager$ImageEntry")
    L2O = JClass("com.hypixel.fastutil.longs.Long2ObjectConcurrentHashMap")
    WORLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    Vec3d, Rot3 = JClass("org.joml.Vector3d"), JClass("com.hypixel.hytale.math.vector.Rotation3f")
    CHU = JClass("com.hypixel.hytale.math.util.ChunkUtil")
    PREc = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent")
    PDEc = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
    IHM = JClass("java.util.IdentityHashMap")
    MRDY, MQUIT = JClass(PKG + "MapReady"), JClass(PKG + "MapQuit")
    rx = CP.makeClass("skyyuiprobeharness.RecExec", CP.get("java.util.concurrent.ScheduledThreadPoolExecutor"))
    rx.addField(CtField.make("public java.util.ArrayList fixed;", rx))
    rx.addField(CtField.make("public java.util.ArrayList periods;", rx))
    rx.addConstructor(CtNewConstructor.make("public RecExec() { super(1); this.fixed = new java.util.ArrayList(); this.periods = new java.util.ArrayList(); }", rx))
    rx.addMethod(CtNewMethod.make(
        "public java.util.concurrent.ScheduledFuture scheduleAtFixedRate(Runnable r, long d, long p, java.util.concurrent.TimeUnit u) {\n"
        "  this.fixed.add(r);\n  this.periods.add(Long.valueOf(u.toMillis(p)));\n  return super.schedule(r, 1L, java.util.concurrent.TimeUnit.DAYS);\n}", rx))
    rx.writeFile(hcls)
    sk = CP.makeClass("skyyuiprobeharness.HarnessSkyyHud", CP.get("com.hypixel.hytale.server.core.entity.entities.player.hud.CustomUIHud"))
    sk.addConstructor(CtNewConstructor.make("public HarnessSkyyHud(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr, \"%s\"); }" % SKEY, sk))
    sk.addMethod(CtNewMethod.make(
        "protected void build(com.hypixel.hytale.server.core.ui.builder.UICommandBuilder b) {\n"
        "  b.appendInline((String) null, \"Group #SkyyWRoot { Anchor: (Full: 0); }\");\n"
        "  b.appendInline(\"#SkyyWRoot\", \"Label #SkyyWClock { Anchor: (Top: 8, Left: 8, Width: 120, Height: 26); Text: \\\"12 00\\\"; }\");\n}", sk))
    sk.writeFile(hcls)
    REC, SKY = JClass("skyyuiprobeharness.RecExec"), JClass("skyyuiprobeharness.HarnessSkyyHud")
    saved = [(jf(Uni.class_, "instance"), jf(Uni.class_, "instance").get(None)), (jf(EMc.class_, "instance"), jf(EMc.class_, "instance").get(None))]
    old_exec = MPROBE.EXEC
    rec = REC()
    y_log = []
    nxt = [2000]

    def ctype():
        c_ = CTc()
        nxt[0] += 1
        field(CTc, "index").setInt(c_, nxt[0])
        field(CTc, "hashCode").setInt(c_, nxt[0])
        return c_

    try:
        CT_PR, CT_PLA, CT_TR, CT_HR = ctype(), ctype(), ctype(), ctype()
        uni = U.allocateInstance(Uni.class_)
        field(Uni, "playerRefComponentType").set(uni, CT_PR)
        jf(Uni.class_, "instance").set(None, uni)
        em = U.allocateInstance(EMc.class_)
        field(EMc, "playerComponentType").set(em, CT_PLA)
        field(EMc, "transformComponentType").set(em, CT_TR)
        field(EMc, "headRotationComponentType").set(em, CT_HR)
        jf(EMc.class_, "instance").set(None, em)

        def map_manager(enabled, scale, images):
            m_ = U.allocateInstance(WMMc.class_)
            imgs = L2O()
            for (cx, cz), im in images.items():
                imgs.put(JLong(int(CHU.indexChunk(JInt(cx), JInt(cz)))), IEc(im))
            field(WMMc, "images").set(m_, imgs)
            sp = UWMSc()
            sp.enabled = enabled
            field(WMMc, "worldMapSettings").set(m_, WMSc(None, JFloat(scale), JFloat(1.0), JInt(1), JInt(64), sp))
            return m_

        def place(base, wname, x, z, yaw, mm, tail_="e7", who="MapTester"):
            """the player (base's PlayerRef / Player / HudManager / network, or new ones) in a world of its own: a stand-in Store
            answering getComponent, a Ref, a recording World with a map manager"""
            st = U.allocateInstance(TSC)
            ref = U.allocateInstance(REFc.class_)
            field(REFc, "store").set(ref, st)
            if base is None:
                pr = U.allocateInstance(PRc.class_)
                field(PRc, "uuid").set(pr, UUID.fromString("00000000-0000-0000-0000-0000000000" + tail_))
                field(PRc, "username").set(pr, who)
                net = U.allocateInstance(NET.class_)
                field(PRc, "packetHandler").set(pr, net)
                pl = U.allocateInstance(PLAc.class_)
                hm = HMc()
                field(PLAc, "hudManager").set(pl, hm)
            else:
                pr, net, pl, hm = base["pr"], base["net"], base["pl"], base["hm"]
            tc = TRCc(Vec3d(JDouble(x), JDouble(64.0), JDouble(z)), Rot3(JFloat(0.0), JFloat(yaw), JFloat(0.0)))
            hr = HRTc(Rot3(JFloat(0.0), JFloat(yaw), JFloat(0.0)))
            comps = IHM()
            for ct_, c_ in ((CT_PR, pr), (CT_PLA, pl), (CT_TR, tc), (CT_HR, hr)):
                comps.put(ct_, c_)
            allc = IHM()
            allc.put(ref, comps)
            st.comps = allc
            w = world()
            jf(WORLDc.class_, "worldMapManager").set(w, mm)
            jf(WORLDc.class_, "name").set(w, wname)
            es = U.allocateInstance(ESc.class_)
            field(ESc, "world").set(es, w)
            field(STOREc, "externalData").set(st, es)
            if base is None:
                field(PRc, "entity").set(pr, ref)
            return {"st": st, "ref": ref, "pr": pr, "net": net, "pl": pl, "hm": hm, "tc": tc, "hr": hr, "w": w, "name": wname}

        def mark(st_):
            return 0 if st_["net"].sent is None else int(st_["net"].sent.size())

        def pk(st_, i0):
            n_ = st_["net"]
            return [] if n_.sent is None else [n_.sent.get(i) for i in range(i0, int(n_.sent.size()))]

        def kinds(ps):
            return [str(p_.getClass().getSimpleName()) for p_ in ps]

        def chat_of(ps):
            return [str(p_.message.rawText) for p_ in ps if str(p_.getClass().getSimpleName()) == "ServerMessage"]

        def huds(ps):
            return [p_ for p_ in ps if str(p_.getClass().getSimpleName()) == "CustomHud"]

        def assets_in(ps):
            return [str(p_.asset.name) for p_ in ps if str(p_.getClass().getSimpleName()) == "AssetInitialize"]

        def ytick():
            PL.TAIL.clear()
            MPROBE.tick()
            ln = tail()
            y_log.extend(ln)
            return ln

        client = {}

        def apply(ps):
            for p_ in ps:
                k = str(p_.getClass().getSimpleName())
                if k == "ResetUserInterfaceState":
                    client.clear()
                elif k == "CustomHud":
                    hid = str(p_.hudId)
                    cm = [] if p_.commands is None else [as4(c) for c in p_.commands]
                    if bool(p_.clear):
                        if p_.commands is None:
                            client.pop(hid, None)
                        else:
                            client[hid] = list(cm)
                    else:
                        client.setdefault(hid, []).extend(cm)

        sky_sent = [0]

        def sky_show(sky):
            sky.show()
            sky_sent[0] += 1

        def probe_never_skyy(ps, what):
            bad = [p_ for p_ in huds(ps) if str(p_.hudId) == SKEY]
            check(not bad, "U. %s: the probe sent no packet for SkyyHud's key %s" % (what, SKEY))

        def sess():
            return MPROBE.SESS.get(UUID.fromString("00000000-0000-0000-0000-0000000000e7"))

        for f_ in ("SESS", "P3ARM", "DELIVERED", "LASTWORLD"):
            getattr(MPROBE, f_).clear()
        MPROBE.REQ.clear()
        MPROBE.ASSETS.clear()
        MPROBE.ENC.clear()
        MPROBE.TICKER = None
        MPROBE.EXEC = rec
        n0 = int(outbound.size())
        MPROBE.tapOn()
        rnd2 = random.Random(5)
        cacheA = {}
        for cx in range(0, 6):
            for cz in range(-9, -4):
                cacheA[(cx, cz)] = engine_image(16, 16, rnd2.randrange(2, 14), False)[0]
        mmA = map_manager(True, 0.5, cacheA)
        A = place(None, "harness_overworld", 100.5, -200.25, 0.0, mmA)
        B = place(A, "harness_island", 7.5, 9.5, 0.0, map_manager(False, 0.5, {}))
        ygph = U.allocateInstance(GPH.class_)
        field(GPH, "playerRef").set(ygph, A["pr"])
        uid = A["pr"].getUuid()
        sky = SKY(A["pr"])
        i0 = mark(A)
        sky_show(sky)
        apply(pk(A, i0))
        SKY_DOC = list(client.get(SKEY, []))
        check(list(client) == [SKEY] and len(SKY_DOC) == 2, "U. SkyyHud's own HUD (show(), key %s, never registered) is on the client" % SKEY)

        # ---- Y1 /skyprobe map p1a
        i0 = mark(A)
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("p1a"))
        ps = pk(A, i0)
        check(chat_of(ps) == ["[SkyyUiProbe] " + md["lines"][0]] and int(MPROBE.REQ.size()) == 1 and MPROBE.TICKER is not None
              and int(rec.fixed.size()) == 1 and int(rec.periods.get(0)) == 250,
              "Y. /skyprobe map p1a: its ONE chat line at once, one request queued, the 0.25 s tick started (it was off): %s" % chat_of(ps))
        ln = ytick()
        ps = pk(A, i0 + 1)
        check(kinds(ps)[:3] == ["AssetInitialize", "AssetPart", "AssetFinalize"] and assets_in(ps) == [pics[0]] and
              not any(k == "RequestCommonAssetsRebuild" for k in kinds(ps)) and queued(A["w"]) == [("MapAttach", -1)] and not huds(ps),
              "Y. the tick sends the P1a picture (3 packets, no rebuild) and hands the HUD to the world thread: %s %s" % (kinds(ps), queued(A["w"])))
        check(any(l_.startswith("P1a MapTester: picture %s (128 x 128, " % pics[0]) and "sent in 3 packets" in l_ and ", no rebuild" in l_
                  and "to the world thread" in l_ for l_ in ln), "Y. ... logged with bytes, packets and ms: %s" % ln[-1:])
        i1 = mark(A)
        run_all(A["w"])
        ps = pk(A, i1)
        hp = huds(ps)
        check(len(hp) == 1 and str(hp[0].hudId) == KEY and int(hp[0].zOrder) == Z and bool(hp[0].clear),
              "Y. the world thread: HudManager.addCustomHud -> ONE CustomHud (hudId %s, zOrder %d, clear) - the probe's own key" % (KEY, Z))
        if hp:
            check_doc([as4(c) for c in hp[0].commands], "P1a as sent")
        apply(ps)
        s_ = sess()
        check(s_ is not None and s_.hud is not None and bool(s_.hud.attached) and A["hm"].getCustomHud(KEY) == s_.hud
              and A["hm"].getCustomHud(SKEY) is None and sorted(client) == sorted([KEY, SKEY]) and client[SKEY] == SKY_DOC,
              "U. P1a shown: the HudManager holds the probe HUD under its key, SkyyHud's document on the client is untouched (both shown)")
        probe_never_skyy(ps, "P1a")
        # ---- Y2 p1b: a NEW picture + ONE rebuild; the same key replaces the P1a box
        i0 = mark(A)
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("p1b"))
        ytick()
        run_all(A["w"])
        ps = pk(A, i0)
        hp = huds(ps)
        check(assets_in(ps) == [pics[1]] and kinds(ps).count("RequestCommonAssetsRebuild") == 1 and
              kinds(ps).index("RequestCommonAssetsRebuild") > kinds(ps).index("AssetFinalize") and len(hp) == 2
              and hp[0].commands is None and bool(hp[0].clear) and str(hp[0].hudId) == KEY and hp[1].commands is not None,
              "Y. p1b: the new picture, then ONE RequestCommonAssetsRebuild, then the same key replaces the box (clear the old, show the new): %s" % kinds(ps))
        apply(ps)
        probe_never_skyy(ps, "P1b")
        check(client[SKEY] == SKY_DOC, "U. ... SkyyHud's document unchanged")
        i0 = mark(A)
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("p1a"))
        ln = ytick()
        run_all(A["w"])
        ps = pk(A, i0)
        check(assets_in(ps) == [] and len(huds(ps)) == 2 and any("NOT sent again (this connection has it)" in l_ for l_ in ln),
              "Y. p1a again: the picture is NOT sent again (this connection has it), only the box")
        apply(ps)
        # ---- Y3 p2: mask + ring + 8 arrows + the tiles (30 from the shared cache), ONE rebuild, the 81-tile document
        i0 = mark(A)
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("p2"))
        ln = ytick()
        ps = pk(A, i0)
        sent = assets_in(ps)
        tiles_sent = [n_ for n_ in sent if re.match(re.escape(md["asset_dir"]) + r"t-", n_)]
        check(sent[:10] == [str(G0.getName()), str(G1.getName())] + GA and len(tiles_sent) == len(set(tiles_sent)) and
              len([n_ for n_ in sent if "/x-" in n_]) == 2 and kinds(ps).count("RequestCommonAssetsRebuild") == 1
              and kinds(ps)[-1] == "RequestCommonAssetsRebuild" and queued(A["w"]) == [("MapAttach", -1)],
              "Y. p2: mask, ring, 8 arrows, %d cache tiles, 2 test patterns, then ONE rebuild (the first mask of this connection): %d "
              "pictures" % (len(tiles_sent), len(sent)))
        s_ = sess()
        check(int(s_.srcCache) == 30 and int(s_.srcMap) == 0 and int(s_.srcTest) == 51 and int(s_.ccx) == 3 and int(s_.ccz) == -7,
              "Y. ... chunk 3 -7: 30 tiles from the shared map cache (getImageIfInMemory), 51 test pattern, 0 map stream yet")
        check(any(l_.startswith("P2 MapTester: chunk 3 -7, 81 tiles (0 from the map stream, 30 from the shared map cache, 51 test pattern)")
                  for l_ in ln), "Y. ... logged: %s" % [l_ for l_ in ln if l_.startswith("P2 ")][:1])
        i1 = mark(A)
        run_all(A["w"])
        ps = pk(A, i1)
        hp = huds(ps)
        check(len(hp) == 2 and hp[0].commands is None and hp[1].commands is not None, "Y. ... the P2 HUD replaces the box on the world thread")
        if len(hp) == 2:
            aps, sets_ = check_doc([as4(c) for c in hp[1].commands], "P2 as sent")
            tps = [re.search(r'AssetPath: "([^"]+)"', mk).group(1) for p, mk in aps if mk.startswith("AssetImage #%s" % ids["tile"])]
            check(len(tps) == 81 and sum(1 for t_ in tps if "/t-" in t_) == 30 and set(t_ for t_ in tps) <= set(sent),
                  "Y. ... the document's 81 tiles name pictures sent before it (30 map pictures)")
        apply(ps)
        probe_never_skyy(ps, "P2")
        # the world-thread read, the tap's map pieces upgrading tiles, a walk across a chunk border, a turn
        ln = ytick()
        check(queued(A["w"]) == [("MapRead", -1)] and bool(s_.readPending), "Y. the next tick posts ONE world-thread read (positions only)")
        run_all(A["w"])
        check(not bool(s_.readPending) and int(s_.posAt) > 0, "Y. ... the read ran on the world thread")
        i0 = mark(A)
        handle_out(ygph, mk_upd([(cx, cz, engine_image(16, 16, 7, False)[0]) for cx in (2, 3, 4) for cz in (-8, -7, -6)]))
        ytick()
        ps = pk(A, i0)
        hp = huds(ps)
        check(int(s_.srcMap) == 9 and len(assets_in(ps)) == 9 and len(hp) == 1 and not bool(hp[0].clear) if hp else False,
              "Y. 9 map pieces from the stream (the tap): 9 new pictures, then ONE HUD update (not a re-send): map %d" % int(s_.srcMap))
        if hp:
            u_ = [as4(c) for c in hp[0].commands]
            check(sum(1 for c in u_ if c[1].endswith(".AssetPath")) == 9 and any(c[1] == "#%s.Text" % ids["cap"] for c in u_)
                  and kinds(ps).index("CustomHud") > max(i for i, k in enumerate(kinds(ps)) if k == "AssetFinalize"),
                  "Y. ... the update swaps exactly 9 tile pictures + the caption, after the pictures were sent")
        apply(ps)
        run_all(A["w"])
        A["tc"].setPosition(Vec3d(JDouble(140.5), JDouble(64.0), JDouble(-200.25)))
        ytick()
        run_all(A["w"])
        i0 = mark(A)
        ytick()
        ps = pk(A, i0)
        hp = huds(ps)
        if hp:
            u_ = [as4(c) for c in hp[0].commands]
            ta = sum(1 for c in u_ if re.match(r"#%s\d+\.Anchor$" % ids["tile"], c[1]))
            check(ta == 9 and any(c[1] == "#%s.Anchor" % ids["grid"] for c in u_) and int(s_.ccx) == 4 and int(s_.swaps) == 1,
                  "Y. a walk across a chunk border: ONE update with 9 tile Anchors (the entering column) + the grid Anchor: %d" % ta)
        else:
            check(False, "Y. a walk across a chunk border sends an update")
        apply(ps)
        A["hr"].getRotation().setYaw(JFloat(f32(-math.pi / 2)))
        run_all(A["w"])
        i0 = mark(A)
        ytick()
        hp = huds(pk(A, i0))
        check(len(hp) == 1 and [as4(c)[1] for c in hp[0].commands] == ["#%s.AssetPath" % ids["me"]] and
              json.loads(as4(hp[0].commands[0])[2])["0"] == GA[2], "Y. turning east (HeadRotation yaw -pi/2): one command, the east arrow")
        apply(pk(A, i0))
        check(client[SKEY] == SKY_DOC and len(client) == 2, "U. after the walk SkyyHud's document is still untouched")
        # ---- Y4 p2sharp: tiles enlarged on the server (32 px pictures), no second rebuild
        i0 = mark(A)
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("p2sharp"))
        ytick()
        ps = pk(A, i0)
        ts_ = [n_ for n_ in assets_in(ps) if "/ts-" in n_]
        check(len(ts_) == 30 and kinds(ps).count("RequestCommonAssetsRebuild") == 0 and len([n_ for n_ in assets_in(ps) if "/xs-" in n_]) == 2,
              "Y. p2sharp: %d tile pictures made at 32 px on the server (ts-), 2 sharp test patterns, NO rebuild (the mask was sent)" % len(ts_))
        if ts_:
            d_ = png_decode(pyb(MPROBE.ASSETS.get(ts_[0]).bytes))
            check(d_["w"] == 32 and d_["h"] == 32, "Y. ... a sharp tile is a 32 x 32 PNG (the 16 px piece x2, nearest neighbour)")
        run_all(A["w"])
        apply(pk(A, i0))
        # ---- Y5 status
        i0 = mark(A)
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("status"))
        check(chat_of(pk(A, i0)) == [], "Y. /skyprobe map status prints nothing at once (the line comes from the tick)")
        ytick()
        c_ = chat_of(pk(A, i0))
        check(len(c_) == 1 and c_[0].startswith("[SkyyUiProbe] Map probes: HUD P2 sharp - map ") and "pictures sent" in c_[0]
              and "P3 off" in c_[0], "Y. status: one line from the tick: %s" % c_)
        # ---- Y6 p4 next to the minimap: 60 s of counts, the summary
        i0 = mark(A)
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("p4"))
        check(chat_of(pk(A, i0)) == ["[SkyyUiProbe] " + md["lines"][6]], "Y. p4: its ONE chat line")
        ytick()
        feed = [mk_upd([(20, 20, imgA), (21, 20, None)], added=1), mk_upd([(22, 20, imgB)], removed=1), mk_upd([(23, 20, imgA)])]
        for p_ in feed:
            handle_out(ygph, p_)
        handle_out(ygph, CWMc())
        ytick()
        s_.tapEnd = int(SYS.currentTimeMillis()) - 1
        i1 = mark(A)
        ytick()
        c_ = chat_of(pk(A, i1))
        wb = sum(int(p_.computeSize()) for p_ in feed)
        check(len(c_) == 1 and c_[0].startswith("[SkyyUiProbe] P4 (world 'harness_overworld', map on, no generator, image scale 0.5) ")
              and (": 3 UpdateWorldMap (max 3 in one 0.25 s), 4 chunks (1 null = unloads), 1 markers added / 1 removed, 1 ClearWorldMap, %d "
                   "bytes; pictures 16 px" % wb) in c_[0], "Y. p4 after 60 s: the summary line in chat (and the log): %s" % c_)
        check(int(s_.tapMode) == 0 and s_.hud is not None, "Y. ... counting stopped, the minimap still runs")
        # ---- Y7 p3 across a world change and a reconnect (re-send off, then on)
        i0 = mark(A)
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("p3"))
        check(chat_of(pk(A, i0)) == ["[SkyyUiProbe] " + md["lines"][4]], "Y. p3: its ONE chat line")
        ytick()
        run_all(A["w"])
        apply(pk(A, i0))
        check(MPROBE.P3ARM.containsKey(uid) and assets_in(pk(A, i0)) == [pics[2]], "Y. p3 armed: the P3 picture sent and shown now")

        def world_change(src, dst):
            j0 = mark(src)
            src["hm"].resetUserInterface(src["pr"])                   # Universe.resetPlayer -> Player.resetManagers
            src["hm"].resetHud(src["pr"])
            handle_out(ygph, CWMc())                                  # WorldMapTracker.clear
            field(PRc, "entity").set(src["pr"], dst["ref"])
            MRDY().accept(PREc(dst["ref"], dst["pl"], JInt(7)))
            sky_show(sky)                                             # SkyyHud shows its HUD again on PlayerReadyEvent
            apply(pk(src, j0))
            return j0

        j0 = world_change(A, B)
        check(int(MPROBE.REQ.size()) == 1 and (bool(s_.hud.gone) if s_.hud is not None else False),
              "Y. world change: the engine's resetHud removed the probe HUD (MapHud.onRemove), the ready event queued a request")
        jt = mark(A)
        ln = ytick()
        ps = pk(A, jt)
        check(MPROBE.SESS.get(uid) is None and any("HUD ended (world change)" in l_ or "HUD ended (the engine removed it" in l_ for l_ in ln)
              and not huds(ps) and not assets_in(ps) and not MPROBE.DELIVERED.containsKey(uid),
              "Y. ... the tick ends the session without a packet (the client already dropped it), the 'already sent' list is cleared")
        p3 = MPROBE.P3ARM.get(uid)
        check(p3 is not None and int(p3.dueAt) > int(SYS.currentTimeMillis()) and p3.world == B["w"], "Y. ... P3 is due 1.5 s after the ready event")
        p3.dueAt = 1
        j1 = mark(A)
        ln = ytick()
        ps = pk(A, j1)
        check(assets_in(ps) == [] and chat_of(ps) == ["[SkyyUiProbe] P3: after your world change the picture was NOT sent again - do you see it "
                                                      "in the box top-right? Tell Claude, then /skyprobe map off."] and queued(B["w"]) == [("MapAttach", -1)],
              "Y. P3 after the world change: the box comes back WITHOUT sending the picture again: %s" % chat_of(ps))
        run_all(B["w"])
        ps = pk(A, j1)
        hp = [p_ for p_ in huds(ps) if str(p_.hudId) == KEY]
        if hp:
            aps, sets_ = check_doc([as4(c) for c in hp[-1].commands], "P3 after a world change")
            check(sets_ == [("#%s.Text" % ids["cap"], md["caps"]["p3no"])] and SAMPLE_PIC not in str(aps) and pics[2] in str(aps),
                  "Y. ... the same picture path, caption %r" % md["caps"]["p3no"])
        apply(ps)
        check(client[SKEY] == SKY_DOC and KEY in client, "U. ... SkyyHud's document is back (its own re-show) and the probe's P3 box beside it")
        j0 = mark(A)
        MPROBE.command(B["ref"], B["st"], B["pr"], B["w"], JString("p3resend"))
        ytick()
        run_all(B["w"])
        apply(pk(A, j0))
        check(bool(MPROBE.P3ARM.get(uid).resend), "Y. p3resend armed (in the island world)")
        j0 = world_change(B, A)
        ytick()
        MPROBE.P3ARM.get(uid).dueAt = 1
        j1 = mark(A)
        ytick()
        ps = pk(A, j1)
        check(assets_in(ps) == [pics[2]] and chat_of(ps)[-1:] == ["[SkyyUiProbe] P3: after your world change the picture was SENT AGAIN "
                                                                  "first - do you see it in the box top-right? Tell Claude, then /skyprobe map off."],
              "Y. P3 re-send after the world change back: the picture is sent again first: %s" % chat_of(ps))
        run_all(A["w"])
        apply(pk(A, j1))
        j0 = mark(A)
        MQUIT().accept(PDEc(A["pr"]))
        ytick()
        ps = pk(A, j0)
        check(not huds(ps) and not assets_in(ps) and MPROBE.SESS.get(uid) is None and not MPROBE.DELIVERED.containsKey(uid)
              and bool(MPROBE.P3ARM.get(uid).sawQuit), "Y. disconnect: the session ends without a packet, the per-connection list is "
                                                      "cleared, P3 stays armed (it is the reconnect test)")
        client.clear()                                                # a new client
        j0 = mark(A)
        MRDY().accept(PREc(A["ref"], A["pl"], JInt(1)))
        sky_show(sky)
        ytick()
        MPROBE.P3ARM.get(uid).dueAt = 1
        ytick()
        ps = pk(A, j0)
        check(assets_in(ps) == [pics[2]] and any("after your reconnect the picture was SENT AGAIN" in c for c in chat_of(ps)),
              "Y. reconnect: P3 shows again 1.5 s after the join (re-send on: sent first): %s" % chat_of(ps)[-1:])
        run_all(A["w"])
        apply(pk(A, j0))
        check(client[SKEY] == SKY_DOC and KEY in client, "U. after the reconnect: SkyyHud's document + the probe's P3 box")
        # ---- Y8 p5 through 3 worlds (segments at the engine's ClearWorldMap, named by the ready event); P3 off first
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("off"))
        ytick()
        run_all(A["w"])
        j0 = mark(A)
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("p5"))
        check(chat_of(pk(A, j0)) == ["[SkyyUiProbe] " + md["lines"][7]], "Y. p5: its ONE chat line")
        ytick()
        handle_out(ygph, mk_upd([(1, 1, imgA)]))
        world_change(A, B)
        ytick()
        handle_out(ygph, mk_upd([(2, 2, imgB), (3, 3, None)]))
        world_change(B, A)
        ytick()
        handle_out(ygph, mk_upd([(4, 4, imgA)]))
        s_ = sess()
        s_.tapEnd = int(SYS.currentTimeMillis()) - 1
        ytick()
        c_ = [x for x in chat_of(pk(A, j0)) if x.startswith("[SkyyUiProbe] P5 world")]
        check(len(c_) == 3 and "(world 'harness_overworld', map on, no generator, image scale 0.5)" in c_[0] and
              "(world 'harness_island', map OFF, no generator, image scale 0.5)" in c_[1] and "(world 'harness_overworld'" in c_[2]
              and ": 1 UpdateWorldMap" in c_[0] and "2 chunks (1 null = unloads)" in c_[1] and "the world changed (ClearWorldMap)" in c_[0],
              "Y. p5: one summary per world (overworld, island with the map OFF, overworld), named by the ready events: %s" % c_)
        check(MPROBE.SESS.get(uid) is None or int(sess().tapMode) == 0, "Y. ... then P5 stops")
        # ---- Y9 off: the HUD removed through the world thread, the count printed, P3 disarmed, the tick stops
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("p2"))
        ytick()
        run_all(A["w"])
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("p4"))
        ytick()
        run_all(A["w"])                                               # the read the minimap asked for
        j0 = mark(A)
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("off"))
        check(chat_of(pk(A, j0)) == ["[SkyyUiProbe] " + md["lines"][8]], "Y. off: its ONE chat line")
        ytick()
        c_ = chat_of(pk(A, j0))
        check(len(c_) == 2 and c_[1].startswith("[SkyyUiProbe] P4 (world 'harness_overworld'") and c_[1].endswith(" - off")
              and queued(A["w"]) == [("MapDetach", -1)] and not MPROBE.P3ARM.containsKey(uid) and MPROBE.SESS.get(uid) is None,
              "Y. ... the tick prints P4's summary, removes the HUD through the world thread, disarms P3: %s" % c_[1:])
        run_all(A["w"])
        ps = pk(A, j0)
        hp = [p_ for p_ in huds(ps) if str(p_.hudId) == KEY]
        check(len(hp) == 1 and hp[0].commands is None and bool(hp[0].clear) and A["hm"].getCustomHud(KEY) is None,
              "Y. ... HudManager.removeCustomHud(%s): one clear for the probe's key only" % KEY)
        client.clear()
        apply(pk(A, 0))                                               # the whole session replayed on a fresh client model
        check(list(client) == [SKEY] and client[SKEY] == SKY_DOC, "U. replaying every packet of the session: the client ends with exactly "
                                                                  "SkyyHud's document - nothing borrowed, nothing left behind")
        ytick()
        check(MPROBE.TICKER is None and bool(MPROBE.idle()), "Y. nothing runs any more: the tick stopped itself (off by default again)")
        skp = [p_ for p_ in huds(pk(A, 0)) if str(p_.hudId) == SKEY]
        check(len(skp) == sky_sent[0], "U. every %s packet of the whole run came from SkyyHud's own show() (%d), none from the probe" % (SKEY, len(skp)))
        # ---- U: SkyyHud REGISTERED in the HudManager too: the probe's add / remove leave its entry alone
        C = place(None, "harness_other", 5.0, 5.0, 0.0, map_manager(True, 0.5, {}), "e8", "SlotTester")
        sky2 = SKY(C["pr"])
        C["hm"].addCustomHud(C["pr"], sky2)                           # SkyyHud registered (its own show packet)
        c0 = mark(C)
        MPROBE.command(C["ref"], C["st"], C["pr"], C["w"], JString("p1a"))
        ytick()
        run_all(C["w"])
        check(C["hm"].getCustomHud(SKEY) == sky2 and C["hm"].getCustomHud(KEY) is not None and int(C["hm"].getCustomHuds().size()) == 2,
              "U. a registered SkyyHud: the HudManager holds both keys side by side")
        MPROBE.command(C["ref"], C["st"], C["pr"], C["w"], JString("p2"))
        ytick()
        run_all(C["w"])
        check(C["hm"].getCustomHud(SKEY) == sky2, "U. ... the probe's mode switch (same key) leaves SkyyHud's entry alone")
        MPROBE.command(C["ref"], C["st"], C["pr"], C["w"], JString("off"))
        ytick()
        run_all(C["w"])
        check(C["hm"].getCustomHud(SKEY) == sky2 and C["hm"].getCustomHud(KEY) is None and int(C["hm"].getCustomHuds().size()) == 1,
              "U. ... off removes only the probe's key")
        probe_never_skyy([p_ for p_ in pk(C, c0)], "the registered-SkyyHud run")
        ytick()
        # ---- Y10 shutdown with a live minimap: tap removed, tick cancelled, the HUD removed through the world thread
        MPROBE.command(A["ref"], A["st"], A["pr"], A["w"], JString("p2"))
        ytick()
        run_all(A["w"])
        j0 = mark(A)
        MPROBE.shutdown()
        check(int(outbound.size()) == n0 and MPROBE.TICKER is None and int(MPROBE.SESS.size()) == 0 and queued(A["w"]) == [("MapDetach", -1)],
              "Y. shutdown: the tap deregistered, the tick cancelled, every session ended, the HUD removal handed to the world thread")
        run_all(A["w"])
        check(A["hm"].getCustomHud(KEY) is None and len([p_ for p_ in huds(pk(A, j0)) if str(p_.hudId) == KEY]) == 1,
              "Y. ... the probe HUD is removed (one clear)")
        bad_log = [l_ for l_ in y_log if l_.startswith("WARNING") or re.search(r"Exception|IllegalAccess|Error", l_)]
        check(not bad_log, "Y. none of the %d map probe log lines of the flows is a WARNING or names an error: %s" % (len(y_log), bad_log[:3]))
    except Exception as ex_:
        import traceback as _tb
        _tb.print_exc()
        check(False, "Y. the map flow run stopped on %s: %s" % (type(ex_).__name__, ex_))
    finally:
        try:
            MPROBE.shutdown()
        except Exception:
            pass
        MPROBE.EXEC = old_exec
        for f_, v_ in saved:
            f_.set(None, v_)
        try:
            rec.shutdownNow()
        except Exception:
            pass
    for l_ in y_log:                                                  # what the server log says (bytes, packets, ms) - for the report
        if re.match(r"(P1a|P1b|P2|P2 sharp|P3|P4|P5) ", l_):
            print("   map log: " + l_[:400])
    print("U / Y. HUD slot + flows done (%d log lines)" % len(y_log))

    # ================================================================================================ R. start twice on a copy of the live data
    import time as _time
    if os.path.isdir(LIVE):
        live = os.path.join(SCRATCH, "live", "mods")
        if os.path.isdir(os.path.join(SCRATCH, "live")) and under_scratch(os.path.join(SCRATCH, "live")):
            shutil.rmtree(os.path.join(SCRATCH, "live"), ignore_errors=True)
        shutil.copytree(LIVE, live)                                   # read only from the live folder: everything below runs on the copy

        def tree():
            o = {}
            for dp, dn, fn in os.walk(os.path.join(SCRATCH, "live")):
                for f_ in fn:
                    p_ = os.path.join(dp, f_)
                    o[os.path.relpath(p_, SCRATCH)] = (open(p_, "rb").read(), os.path.getmtime(p_))
                for d_ in dn:
                    o[os.path.relpath(os.path.join(dp, d_), SCRATCH) + os.sep] = None
            return o

        t0 = tree()
        _time.sleep(1.1)
        PLUG = JClass(PKG + "SkyyUiProbePlugin")
        plugin = U.allocateInstance(PLUG.class_)
        m_start = PLUG.class_.getDeclaredMethod("start")
        m_start.setAccessible(True)
        m_stop = PLUG.class_.getDeclaredMethod("shutdown")
        m_stop.setAccessible(True)
        jf(JClass("com.hypixel.hytale.server.core.plugin.PluginBase").class_, "dataDirectory").set(
            plugin, JClass("java.nio.file.Paths").get(os.path.join(live, "Skyy_SkyyUiProbe"), JArray(JString)(0)))
        n0 = int(outbound.size())
        m_start.invoke(plugin, JArray(JObject)(0))
        m_start.invoke(plugin, JArray(JObject)(0))
        check(int(outbound.size()) == n0 + 1 and MPROBE.TAPF is not None, "R. the plugin's start() twice: ONE outbound tap (%d -> %d)" % (
            n0, int(outbound.size())))
        rpr, rnet = pref("LiveCopyTester", UUID.fromString("00000000-0000-0000-0000-0000000000f9"))
        rs = MSESS()
        rs.pr, rs.uuid, rs.who = rpr, rpr.getUuid(), "LiveCopyTester"
        rs.wants = True
        rs.capture = True
        rs.tapMode = 4
        MPROBE.SESS.put(rs.uuid, rs)
        MPROBE.recountTaps()
        rg = U.allocateInstance(GPH.class_)
        field(GPH, "playerRef").set(rg, rpr)
        for k in range(50):
            handle_out(rg, mk_upd([(k, -k, imgA), (k, k, None)], added=1))
        MPROBE.drain(rs, JLong(int(SYS.currentTimeMillis())))
        a_ = MPROBE.asset("t", MPNG.fromMapImage(imgA, JInt(2)))
        MPROBE.send(rs, a_, False)
        check(int(rs.upd) == 50 and int(rs.chunks) == 100, "R. a session runs on top of the started plugin (50 packets counted)")
        m_stop.invoke(plugin, JArray(JObject)(0))
        check(int(outbound.size()) == n0 and MPROBE.TAPF is None and int(MPROBE.SESS.size()) == 0, "R. shutdown(): the tap removed, the sessions ended")
        m_start.invoke(plugin, JArray(JObject)(0))
        check(int(outbound.size()) == n0 + 1, "R. start() again after the shutdown: one tap again")
        m_stop.invoke(plugin, JArray(JObject)(0))
        check(int(outbound.size()) == n0, "R. ... and shutdown() removes it again")
        t1 = tree()
        check(t1 == t0 and len(t0) > 3, "R. start twice + a session + shutdown on the copy of the live data wrote NOTHING (%d entries, every byte and "
                                        "modification time; new %s changed %s)" % (len(t0), sorted(k for k in t1 if k not in t0)[:3],
                                                                                   sorted(k for k in t0 if k in t1 and t0[k] != t1[k])[:3]))
        check(not os.path.exists(os.path.join(live, "Skyy_SkyyUiProbe")), "R. ... not even a data folder (SkyyUiProbe keeps no data)")
    else:
        SKIPS.append("R (start twice on a copy of the live data): no live world mods folder at %s" % LIVE)
        print("   R skipped: no live data at %s" % LIVE)
    print("R. start twice on the live copy done")

    # ================================================================================================ Z. class compare 0.3.1 vs 0.4
    if os.path.isfile(OLD_JAR):
        zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
        old = dict((n_, zo.read(n_)) for n_ in zo.namelist() if n_.endswith(".class"))
        new = dict((n_, zn.read(n_)) for n_ in zn.namelist() if n_.endswith(".class"))
        zo.close()
        zn.close()

        def short(n_):
            return n_.rsplit("/", 1)[-1][:-6]

        same = sorted(short(c) for c in old if new.get(c) == old[c])
        changed = sorted(short(c) for c in old if c in new and new[c] != old[c])
        gone = sorted(short(c) for c in old if c not in new)
        added = sorted(short(c) for c in new if c not in old)
        JCF = JClass("javassist.bytecode.ClassFile")
        JDI, JBI = JClass("java.io.DataInputStream"), JClass("java.io.ByteArrayInputStream")
        IPz = JClass("javassist.bytecode.InstructionPrinter")

        def methods(data):
            cf = JCF(JDI(JBI(jb(data))))
            out = {}
            for mi in cf.getMethods():
                ca = mi.getCodeAttribute()
                txt = []
                if ca is not None:
                    it_ = ca.iterator()
                    cp_ = mi.getConstPool()
                    while it_.hasNext():
                        p_ = it_.next()
                        txt.append(re.sub(r"#\d+ = ", "", str(IPz.instructionString(it_, p_, cp_))))
                out[str(mi.getName()) + str(mi.getDescriptor())] = "\n".join(txt)
            return out

        diff = {}
        for c in changed:
            mo, mn = methods(old["com/skyy/uiprobe/%s.class" % c]), methods(new["com/skyy/uiprobe/%s.class" % c])
            diff[c] = sorted(k.split("(")[0] for k in set(mo) | set(mn) if mo.get(k) != mn.get(k))
        check(not gone and changed == sorted(CHANGED_OLD) and len(same) == len(OLD_CLASSES) - len(CHANGED_OLD) and added == sorted(MAP_CLASSES),
              "Z. 0.3.1 -> 0.4: %d classes byte-identical, changed only %s, new %d (the map probe classes), none gone" % (
                  len(same), changed, len(added)))
        check(diff.get("ProbeCmds") == ["arg", "list"] and diff.get("SkyProbeCmd") == ["<init>"] and diff.get("SkyyUiProbePlugin") == ["setup", "shutdown", "start"],
              "Z. the changed methods: ProbeCmds.arg + list (the map word / line), SkyProbeCmd.<init> (the map variant), "
              "SkyyUiProbePlugin.setup / start / shutdown (scheduler + events, the tap, the map shutdown): %s" % diff)
        print("Z. class compare: same %s | changed %s | new %s" % (same, diff, added))
    else:
        SKIPS.append("Z (class compare): no 0.3.1 jar at %s" % OLD_JAR)
    print("map probe sections done")


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
        print("SkyyUiProbe %s harness: %d ok, %d fail, %d skipped" % (VERSION, OKS[0], len(FAILS), len(SKIPS)))
        for f in FAILS:
            print("  FAIL", f)
        for k in SKIPS:
            print("  SKIP", k)
        if not KEEP:
            try:
                import jpype
                if jpype.isJVMStarted():
                    jpype.shutdownJVM()
            except Exception as e:
                print("JVM shutdown: %s" % e)
            if under_scratch(SCRATCH) and os.path.isfile(MARK):      # claim_scratch() made and marked it
                shutil.rmtree(SCRATCH, ignore_errors=True)
                if os.path.isdir(SCRATCH):                           # 0.4: a native library the JVM keeps loaded until this process ends
                    with open(MARK, "w") as f:                       # (zstd-jni in tmp) - marked again, so the next run takes the folder
                        f.write("SkyyUiProbe %s harness scratch - deleted at the end of the run unless --keep\n" % VERSION)
            left = [os.path.relpath(os.path.join(d_, f_), SCRATCH) for d_, _n, fs in os.walk(SCRATCH) for f_ in fs] if os.path.isdir(SCRATCH) else []
            print("scratch folder %s" % ("removed" if not os.path.exists(SCRATCH) else "kept with %s (a native library this process still holds; "
                                                                                          "the next run clears it)" % [x for x in left if not x.endswith(".skyyuiprobe-harness")]))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
