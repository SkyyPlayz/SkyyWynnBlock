"""SkyyUiProbe 0.3 - build script (javassist via jpype). A small DEV / TEST mod: it opens the vanilla-look kit's probe pages in game,
and (new in 0.3) the two VAULT WINDOW probes of research/Vault-Arrow-Click-Research.md section 8 step 1.
Run:   python SkyyUiProbe/build_skyyuiprobe_0.3.py            -> SkyyUiProbe/SkyyUiProbe-0.3.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
       --dump <file.json> also writes what every view sends (appends + b.set lines + extra Java lines, the index bindings) for the
       harness; nothing else changes. --dump-only <file.json> writes it and stops before the Java (no JVM, no class / jar written).
Check: python SkyyUiProbe/test_skyyuiprobe_0.3.py   (bare JVM, -Xverify:all; re-run it after every build and whenever the kit id
       changes - it refuses a jar built with another kit).

WHY 0.3 (made by copy + edit of build_skyyuiprobe_0.2.py, the SET pin; Skyy 2026-10-02, OPEN-QUESTIONS "Q&A with Skyy 2026-10-02" R2
LOCKED: "try the one-click vault arrow row on our own vanilla-look page next to the vault slots (one probe first; the in-chest arrows
stay as a fallback)"). The vanilla chest never tells the server when an item is LIFTED, so a one-click arrow needs our own page next to
the vault window - and nobody has seen the client draw a window next to a CUSTOM page yet. Two probes answer that, ~30 s each:
  P1 /skyprobe win      (probe 23) a small custom page opened with PageManager.openCustomPageWithWindows(page, ProbeWindow), a
                        ContainerWindow over a SCRATCH 9-slot container (the "probe box"): does the client draw the chest panel and the
                        player's inventory next to the page, can you drag between them, where does the panel sit? Folded in (research
                        P3): a 3-slot non-draggable arrow grid (AreItemsDraggable false, InfoDisplay None, SlotClicking with
                        locksInterface=false - the SkyyMenu launcher pattern, the vault 0.1.6 plan): one press = one chat line, nothing
                        lifts. The arrows are SkyyVault's own Skyy_Vault_Prev / Info / Next items when the server knows them (so this
                        also shows the 0.1.6 icons), else the vanilla stand-ins Weapon_Arrow_Crude / Ingredient_Bar_Iron /
                        Weapon_Arrow_Iron - each slot is new ItemGridSlot(new ItemStack(id, 1)) + setName / setDescription /
                        setActivatable(true), never a stack that can carry metadata.
  P2 /skyprobe secgrid  (probe 24) the same window + page, plus a 9-slot DRAGGABLE ItemGrid on the page bound to the window's section:
                        b.set("#SkyyPbSgGrid.InventorySectionId", <window id>) - does it show and drag the window's real slots? Every
                        move is handled by the ENGINE (MoveItemStack -> InventoryUtils.moveItem -> the probe box); the mod logs each
                        inventory packet the client sends while a probe window is open (section ids, slots, quantity) and its move
                        handler counts the items (probe box + the player's whole inventory, per item id) before and after every
                        change: a chat line + a log line per move, a WARNING when the count changes or a probe item leaves the box.
  Kept from 0.2 unchanged: kit probe pages 1-22 (same numbers, names, content, footer), /skyprobe list, the flat index (now 24
  entries in two columns of 12; the two window probes first, green).

DECISIONS (where the spec left room):
  * InventorySectionId is SET (b.set, int), not written inline: the two libraries that use it (HyUI ItemGridBuilder, ktaleui
    ItemGridRef, installed mods read-only) both set it through "#Id.InventorySectionId". It is sent as ONE page update right after
    openCustomPageWithWindows returned, i.e. after the OpenWindow packet (the engine writes CustomPage first, then OpenWindow), so the
    client never gets a grid bound to a window it does not have yet. The page markup itself is proven properties only (assert_proven
    passes with nothing allowed), so a disconnect on P2 names the binding.
  * P2 binds ONLY the window's section - no grid on the player's storage (-2) as the research suggested: the task says scratch
    containers only, never real player storage. P2 has no arrow grid (P3 is in P1) so P2 tests one thing.
  * The probe box (com.skyy.uiprobe.ProbeBox, a SimpleItemContainer subclass, 9 slots) holds 3 LOCKED probe items - Weapon_Mace_Iron,
    Armor_Iron_Head, Tool_Shovel_Iron: weapon / armor / tool = MaxStack 1 (Item.processConfig), so nothing can ever merge with them -
    plus 6 free slots for the admin's OWN items. ProbeBox refuses (by item id, wherever the probe item sits, so Sort cannot unlock
    one): removing or dropping a probe item (cantRemoveFromSlot / cantDropFromSlot), adding anything onto a probe item or adding a
    stack with a probe item's id (cantAddToSlot - this also blocks the engine's swap path, which never asks the TARGET slot
    cantRemoveFromSlot), and answers a refused whole-slot move (shift-click / Take All) with the engine's own failed MoveTransaction
    instead of null (SkyyVault VView, live since 0.1.2: no "Failed to run task!" NPE). The probe items are made once per admin and
    never leave the box, so the probe creates nothing.
  * One probe box per admin for the server's life (never shared). When its window closes - Esc, Close, Back, a world change or a
    disconnect (the engine's closeAllWindows) - ProbeWindow.onClose0 returns the admin's own items exactly like vanilla's crafting
    windows do (StructuralCraftingWindow.onClose0), but storage first (InventoryComponent.STORAGE_HOTBAR_BACKPACK) and counted before
    and after; what does not fit STAYS in the box (nothing is dropped in the world) and the admin is told to make room and reopen.
    A box that still holds an admin's items at plugin shutdown is logged item by item (WARNING). Kept on purpose after the 2026-10-02
    review (finding 2, the safe option): closeAllWindows also runs on a WORLD CHANGE, where vanilla's addOrDropItemStacks would drop
    the leftovers into the world the admin is leaving (an instance world may unload) - the box keeps them for /skyprobe win in any
    world; the only loss left is a server stop / crash while the box holds items (it lives in RAM), which the test steps rule out
    (bread or stone only, 6+ free inventory slots).
  * A refused move (a locked probe item) changes nothing, so the engine sends nothing back and the client could keep its own guess (an
    item shown moved, a ghost in the inventory). So after every client packet for the probe window the server re-sends the truth: the
    window (Window.invalidate through ProbeWindow.resend) and the player's six inventory sections (markDirty) - SkyyVault 0.1.5's
    resync. ProbeWindow is a ValidatedWindow and validate() always answers true (it never closes the window), but the engine calls it
    far more often than once per packet: InventoryUtils.getSectionById (every inventory packet that names the window) AND
    Player.moveTo -> WindowManager.validateWindows (every movement tick, knockback, teleport). So validate() alone never re-sends
    (review 2026-10-02, finding 1): the packet watcher (netty thread, PlayerChannelHandler.channelRead runs the inbound filters BEFORE
    the engine's handler queues its world task) stamps ProbeSession.sawAt when a packet names the probe window (MoveItemStack either
    end, DropItemStack, InventoryAction, SendWindowAction) or is a shift-click (SmartMoveItemStack: its target may be the window), and
    validate() queues ONE re-send per stamp, SYNC_DELAY_MS later on the world thread (World.scheduleAfter: it lands after that
    packet's handler even when a movement validate saw the stamp first); a stamp older than SAW_MS is dropped. Without the watcher
    (registerInbound failed - logged) the fallback is at most one re-send per SYNC_RATE_MS.
  * Esc on a window page: PageManager only calls onDismiss (it never closes windows), so the page schedules a check 1.5 s later on
    the world thread (World.scheduleAfter): still open -> the server closes it; already closed -> the log says the client did it.
    WindowManager.closeWindow throws when the id is gone, so the server only closes its OWN registered window (getWindow(id) == ours).
    Back: the page rebuilds to the list first, then closes the window. Close (review finding 3): the page detaches its session, closes
    itself, then the server closes the window AT ONCE (no 1.5 s with a draggable chest panel and no page; the log says "Close button"
    instead of the Esc line). A second window probe replaces the first: new page + window first, then the old window closes (the
    SkyyVault askBuy order); the old window returns nothing while the new one shows the box.
  * A closed session lets go of its World / Store / PlayerRef / window / listener (review finding 4: SESS keeps the newest session per
    admin, and a kept World would keep an unloaded SkyyIslands instance alive) and leaves SESS on that admin's first client packet
    after the 5 s grace.
  * Client packets are watched with PacketAdapters.registerInbound(PlayerPacketWatcher) - registered once at the first window probe,
    removed at plugin shutdown, log only (netty thread: no inventory / component access), and silent unless that player has a probe
    window open (or closed less than 5 s ago): MoveItemStack, SmartMoveItemStack, DropItemStack, InventoryAction, CloseWindow,
    SendWindowAction, ClientOpenWindow, CustomPageEvent.
  * The window pages use the kit (page_shell decorated frame, label kinds, item_grid) + the same flat Back / Close footer as pages
    1-22; each says in ONE line what to look for and how to report it, then four numbered checks.

REVIEW FIXES (2026-10-02 review of 0.3, verdict PASS - same version, same 16 classes; every fix has harness checks that fail on the
first 0.3 build):
  1 (MEDIUM) the window re-send is gated by the packet watcher's stamp (above) - movement / knockback / teleports never re-send.
  2 (LOW)    leftovers stay in the box (above, the safe option); the test steps ask for bread or stone and 6+ free inventory slots.
  3 (LOW)    the Close button closes the window at once (above).
  4 (LOW)    a closed session lets go of its world refs and leaves SESS after the grace (above); closedAt is written before the volatile
             closed flag, so the netty thread's grace check never reads a stale 0.
  5 (LOW)    the checks name the items to use: "bread or stone (not an iron mace, helmet or shovel ...)" - the admin's own iron gear
             shares the probe item ids and is refused without a chat line.
  6 (INFO)   "Move seen, but the count changed" also names a bag sweep (the count compares with the previous move's count).
  7 (INFO)   P2 check 3 ends "No inventory showing? Say so." (no grid on the player's storage - scratch containers only).
  8 (INFO)   the note on both window pages says "if the buttons do nothing, press Esc" (a pending page acknowledgement drops clicks).
  9 (INFO)   no change: a profile switch inside the 1.5 s Esc gap cannot be reached by hand, and Close now closes at once.

COMMANDS (unchanged from 0.2 - no new command classes; ADMIN ONLY: requirePermission("skyyuiprobe.admin") AND setPermissionGroups(new
String[0]) on the command and its usage variant - ops pass through "*", plain hytale:Adventurer players are refused; lint rule
perm_group_leaks):
  /skyprobe  (alias /uiprobe)     -> the INDEX page (every probe page: number, name, what it proves, an Open button)
  /skyprobe <n>  or <name>        -> probe page n directly (1-24, or its stable name: base1, checkbox, ..., layout-right, win, secgrid)
  /skyprobe list                  -> the same list in chat, in the order to open them
Any other token count gets the engine's usage error.

PAGES (inline only, HANDOFF section 2): ONE CustomUIPage class (ProbePage) with a view number. Views 1-22 + the index switch with
rebuild() after a click (0.2); views 23 / 24 are opened as a NEW ProbePage through ProbeWin.open -> openCustomPageWithWindows (never a
page closed right before another opens, never a timer update; P2's one InventorySectionId update is sent once, right after the open).
A window view without its open window (built any other way) shows the index with the line "Probe 23 needs its window ...".
LOGS (server log, INFO): 0.2's "opening probe <n> (<name>) for <player>" / "sent probe <n>"; window probes add the window id, the box
contents and the count at open, every client packet (above), every counted move, who closed the window and how long after the page,
and the return line ("returned N item(s) ...; counted X items before and X after - nothing created or lost").
No data files, no config kit rows, no bridge keys, no player switches, no event systems (one packet watcher, see above). Ready line:
  "[SkyyUiProbe] 0.3 ready - /skyprobe (admin): 24 probe pages (kit skyyui 1.4 <blob12>)".
BUILD CHECKS: everything 0.2 checks (SUI.verify, Probe.with_footer + check_page on pages 1-22, the index: check_page, assert_proven,
flat-only asserts, used_height / used_width budgets, text_width fits), plus for pages 23 / 24: check_page with every b.set target,
assert_proven with NOTHING allowed, used_height == the body, every text measured (the one line fits ONE line), item_grid_java_is_safe on
all Java, no .ui file in the jar.
UNVERIFIED (needs the game - that is what the probes are for): (V5) the client draws a ContainerWindow next to a custom page; (V6) an
ItemGrid with InventorySectionId shows / drags a window's slots; whether the client closes the window itself on Esc; where the chest
panel sits; the vault arrow icons in an ItemGridSlot; that the client sends MoveItemStack (not something else) for the bound grid; that
the re-send after a refused move corrects the chest panel and the custom grid (SkyyVault 0.1.5's pattern for its chest); the return on a
DISCONNECT rests on the same engine path as vanilla's crafting windows (PlayerAddedSystem.onEntityRemove -> closeAllWindows -> onClose0);
the re-send timing in a live world (review fix 1: the decision logic is harness-checked with a recording stand-in World; that the
100 ms World.scheduleAfter lands after the packet's own world task rests on the bytecode - channelRead runs the inbound filters, then
the handler queues World.execute - and on SCHEDULED_EXECUTOR offering the task to the same world task queue 100 ms later; the log's
"N window re-send(s)" count shows it in game).
CHECKED in a bare JVM by the kept harness SkyyUiProbe/test_skyyuiprobe_0.3.py (see its header).
"""
import sys, os, re, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyyui as SUI

if "--deploy" in sys.argv:
    raise SystemExit("SkyyUiProbe: --deploy is not supported here - deploys go through tools/deploy_set.py")
DUMP, DUMP_ONLY = None, False
for _flag in ("--dump", "--dump-only"):
    if _flag in sys.argv:
        i = sys.argv.index(_flag)
        if i + 1 >= len(sys.argv) or sys.argv[i + 1].startswith("--"):
            raise SystemExit("%s needs a file path" % _flag)
        if DUMP is not None:
            raise SystemExit("use --dump or --dump-only, not both")
        DUMP, DUMP_ONLY = sys.argv[i + 1], _flag == "--dump-only"

VERSION = "0.3"
HERE = os.path.dirname(os.path.abspath(__file__))
SUI.verify()                       # every vanilla value the kit emits, proven against Assets.zip (read-only) - never caught
KIT_ID = SUI.kit_id()
assert SUI.KIT_VERSION == "1.4", "SkyyUiProbe 0.3 is made for kit 1.4 (Probe.summary, Probe.with_footer, PROBE_OPEN_FIRST)"
PREFIX = "SkyyPb"                  # the kit's default probe prefix; the index / footer / window page ids (SkyyPbIx..., SkyyPbNav...,
                                   # SkyyPbWin..., SkyyPbSg...) share it
PAGES = SUI.probe_pages(PREFIX)    # the kit pages 1-22, number order (0.2's pages, unchanged)
assert [p.n for p in PAGES] == list(range(1, 23)), "kit 1.4 builds probe pages 1-22"


class WinProbe(object):
    """A vault WINDOW probe (0.3): a page of this mod (not a kit page) opened with openCustomPageWithWindows."""

    def __init__(self, n, name, title, summary):
        self.n, self.name, self.key, self.title, self.summary = n, name, name, title, summary


WINP = [WinProbe(23, "win", "Probe 23 - window", "Chest window next to a custom page, plus a one-click arrow grid (vault idea)"),
        WinProbe(24, "secgrid", "Probe 24 - section grid", "Item grid bound to the window slots (InventorySectionId): show, drag, count")]
WIN_N = [w.n for w in WINP]
PROBES = list(PAGES) + list(WINP)
BY_N = dict((p.n, p) for p in PROBES)
BY_NAME = dict((p.name, p) for p in PROBES)
assert sorted(BY_N) == list(range(1, len(PROBES) + 1)) and len(BY_NAME) == len(PROBES), "probe numbers 1..n, names unique"
for p in PROBES:
    assert re.fullmatch(r"[a-z0-9-]+", p.name), "probe name %r (a command argument): a-z 0-9 -" % p.name
    assert len(p.summary) <= 95, "probe %d summary over 95 characters" % p.n

# the order to open them: the two window probes (new in 0.3), then SUI.PROBE_OPEN_FIRST (base1..base4), then the rest by number
NEW = [w.name for w in WINP]
FIRST = list(SUI.PROBE_OPEN_FIRST)
assert all(x in BY_NAME for x in FIRST), "PROBE_OPEN_FIRST names a page the kit does not build: %s" % FIRST
ORDER = [BY_NAME[x].n for x in NEW] + [p.n for p in sorted(PAGES, key=lambda p: (0, FIRST.index(p.name)) if p.name in FIRST
                                                             else (1, p.n))]
assert sorted(ORDER) == sorted(BY_N) and [BY_N[n].name for n in ORDER[:len(NEW) + len(FIRST)]] == NEW + FIRST

# ================= the old flat look (live SkyyBank 0.1.3 BankPage + SkyyCollections 0.2 CollPage, both seen in game) =================
FLAT = {
    "root": "#0b1524(0.96)", "stripe": "#ffd070", "title": "#ffe08a", "sub": "#cfe3ff", "caption": "#9fb8d0",
    "row": "#142030(0.92)", "name": "#e6f2ff", "num": "#ffe08a",
    "gBg": "#1f5a34", "gHov": "#2c7a48", "gPress": "#133a22", "gFg": "#e6ffe8",      # BankPage green (Deposit)
    "bBg": "#1d3a5f", "bHov": "#2f5a8f", "bPress": "#0f2038", "bFg": "#e6f2ff",      # BankPage blue (Withdraw)
    "nBg": "#2a3444", "nHov": "#3a475c", "nPress": "#1a2230", "nFg": "#e6f2ff",      # BankPage grey (Refresh / Close)
}
UI_DATA_COLORS = list(FLAT.values())    # the proven OLD look, used on purpose by the index and the probe footer only


def f_style(kind, fs):
    """BankPage.style(bg, hov, press, fg, fs) of SkyyBank 0.1.3, character for character."""
    bg, hov, press, fg = FLAT[kind + "Bg"], FLAT[kind + "Hov"], FLAT[kind + "Press"], FLAT[kind + "Fg"]
    ls = "LabelStyle: (FontSize: %d, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)" % (fs, fg)
    return "Style: TextButtonStyle(Default: (Background: %s, %s), Hovered: (Background: %s, %s), Pressed: (Background: %s, %s));" % (
        bg, ls, hov, ls, press, ls)


def f_button(ident, text, w, h, kind, fs=18):
    SUI.check_text(text, "button text")
    return 'TextButton #%s { Anchor: (Width: %d, Height: %d); Text: "%s"; %s }' % (ident, w, h, text, f_style(kind, fs))


def f_label(ident, text, h, fs, col, bold=False, center=False, w=None):
    """A BankPage / CollPage label (lab()): Anchor (Width,) Height; Style FontSize (RenderBold) TextColor (HorizontalAlignment Center)
    VerticalAlignment Center. text must be proven inline text ("" for a b.set label)."""
    SUI.check_text(text, "label text")
    anc = ("Width: %d, " % w if w else "") + "Height: %d" % h
    return 'Label%s { Anchor: (%s); Text: "%s"; Style: (FontSize: %d%s, TextColor: %s%s, VerticalAlignment: Center); }' % (
        " #" + ident if ident else "", anc, text, fs, ", RenderBold: true" if bold else "", FLAT.get(col, col),
        ", HorizontalAlignment: Center" if center else "")


def f_spacer(w, h):
    return "Group { Anchor: (Width: %d, Height: %d); }" % (w, h)                   # CollPage sp(w, h)


def f_group(ident, layout, h, w=None, bg=None):
    """A plain Group row / column (BankPage / CollPage): Anchor (Width,) Height, an optional flat Background, LayoutMode Top / Left."""
    assert layout in ("Top", "Left"), "flat groups use the proven LayoutMode Top / Left only"
    anc = ("Width: %d, " % w if w else "") + "Height: %d" % h
    return "Group #%s { Anchor: (%s);%s LayoutMode: %s; }" % (ident, anc, " Background: %s;" % FLAT[bg] if bg else "", layout)


def f_text(ap, parent, ident, text, h, fs, col, bold=False, center=False, w=None):
    """A flat label with any text: proven text inline, anything else as an empty label + a b.set line (the #SkyyBCapMid pattern)."""
    if SUI.TEXT_OK.fullmatch(text) and not SUI.has_j(text):
        ap.append((parent, f_label(ident, text, h, fs, col, bold, center, w)))
    else:
        ap.append((parent, f_label(ident, "", h, fs, col, bold, center, w)))
        ap.sets.append((ident, "Text", text))


# ================= the index geometry (proven below with SUI.used_height / used_width / fit / text_width) =================
IX = PREFIX + "Ix"
IX_W, IX_H, IX_PADH, IX_PADV = 1600, 980, 20, 14         # 0.3: 980 high (was 960) for 2 x 12 entries; MAX_PAGE_H, flat root (no
                                                         # ornaments: the 980 ceiling keeps the kit's 18 px for them anyway)
IX_IN_W = IX_W - 2 * IX_PADH                    # 1560
COL_GAP = 16
COL_W = (IX_IN_W - COL_GAP) // 2                # 772: two columns of entries
PER_COL = (len(ORDER) + 1) // 2                 # 12 + 12
ENT_H, ENT_GAP, ENT_TOP = 56, 4, 2              # entry: 2 px, line one 30, line two 24 (0.2: 60 = 2 + 32 + 24 + 2)
L1_H, L2_H = 30, 24
EDGE, NUM_W, GAP_W, OPEN_W = 10, 46, 8, 130
NAME_W = COL_W - EDGE - NUM_W - GAP_W - OPEN_W - EDGE    # line one: 10 | number | name | 8 | Open | 10
WHAT_X = EDGE + NUM_W                                    # line two: the summary starts under the name
WHAT_W = COL_W - WHAT_X - GAP_W
WHAT_FS, NAME_FS, NUM_FS = 15, 18, 20
FIT_MARGIN = 8                                   # px kept free after the widest text (the client's glyph advances vary a little)


def summary(pg):
    """The one-line purpose of a probe page: the kit's Probe.summary (a window probe: its own). Kit 1.4 cuts a PROBE_SUMMARY line longer
    than 95 characters to 92 + "..." (base2); when the kit's whole line still fits the index row, that whole line is shown instead."""
    s = pg.summary
    full = SUI.PROBE_SUMMARY.get(pg.name, "")
    if s.endswith("...") and full.startswith(s[:-3]) and SUI.text_width(full, WHAT_FS) <= WHAT_W - FIT_MARGIN:
        return full
    return s


WHAT = dict((p.n, summary(p)) for p in PROBES)
for p in PAGES:
    if WHAT[p.n] != p.summary:
        print("note: probe %d (%s): the index shows the kit's whole PROBE_SUMMARY line (Probe.summary is cut at 95 characters)"
              % (p.n, p.name))


# ================= the kit probe pages + their flat footer (the kit's public footer hook) =================
FOOT_H = 56                      # BankPage bottom row: Group Height 56, LayoutMode Left, Padding Top 8; 46 px buttons
FOOT_SLACK = 4                   # px kept free under the footer's container end (0.1 review: a clipped footer would still leave
                                 # Esc, but Back / Close must stay whole)
FOOT_W = 240 + 16 + 170
NAV, NAV_BACK, NAV_CLOSE = PREFIX + "Nav", PREFIX + "NavBack", PREFIX + "NavClose"


def footer(container):
    return [(container, "Group #%s { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: 8); }" % (NAV, FOOT_H)),
            (NAV, f_button(NAV_BACK, "Back to the list", 240, 46, "b")),
            (NAV, f_spacer(16, 46)),
            (NAV, f_button(NAV_CLOSE, "Close", 170, 46, "n"))]


def probe_view(pg):
    """(appends with the footer, sets, java statements, how the footer was placed, page height, extra Java lines) for one page:
    SUI.probe_page(name) (the kit's lookup by stable name - what /skyprobe <name> means) + Probe.with_footer."""
    kp = SUI.probe_page(pg.name, PREFIX)
    assert kp.n == pg.n and kp.key == pg.key and kp.name == pg.name, "probe_page(%r) is not probe %d" % (pg.name, pg.n)
    view = kp.with_footer(footer, FOOT_H, foot_w=FOOT_W, slack=FOOT_SLACK, prefix=PREFIX)
    ap = view.appends
    assert all(isinstance(mk, str) and not isinstance(mk, SUI.Choice) for _p, mk in ap), "probe %d: a runtime choice" % pg.n
    assert [x for x in ap[-4:]] == footer(view.container), "probe %d: the footer is the last 4 appends" % pg.n
    assert view.h <= SUI.MAX_PAGE_H, "probe %d: %d px high" % (pg.n, view.h)
    java = view.java("b")
    kit_java, shell_java = kp.java("b"), kp.shell.java("b")
    assert kit_java.startswith(shell_java), "probe %d: Probe.java must start with the shell's Java" % pg.n
    extra = [l for l in kit_java[len(shell_java):].strip("\n").splitlines() if l.strip()]
    # nothing of the kit markup changed except the root height line and the footer lines
    mine = [l for l in java.splitlines() if not (NAV in l and "appendInline" in l)]
    kit_lines = kit_java.splitlines()
    assert len(java.splitlines()) - len(mine) == 4, "probe %d: exactly 4 footer appends" % pg.n
    assert len(mine) == len(kit_lines) and mine[1:] == kit_lines[1:] and "appendInline((String) null" in mine[0], \
        "probe %d: the page Java differs from the kit's in more than the root height + footer" % pg.n
    assert SUI.item_grid_java_is_safe(java), "probe %d fills a grid slot with a held stack" % pg.n
    return ap, list(view.sets), java, view.how, view.h, extra


def flex_kids(ap):
    """The FlexWeight children of the footer's container (not the footer itself): SUI.used_height counts them as 0 px."""
    cont = ap[-4][0]
    return [m for p, m in ap[:-4] if p == cont and "FlexWeight" in SUI.render(m)]


VIEWS = {}
for pg in PAGES:
    VIEWS[pg.n] = probe_view(pg)
    how = VIEWS[pg.n][3]
    if flex_kids(VIEWS[pg.n][0]):
        # base2: the body is one FlexWeight column + the footer - the kit's slack figure counts that column as 0 px (0.2 review)
        how += " (slack NOT meaningful: the body holds a FlexWeight child, counted as 0 px; if the page shows only the footer, " \
               "FlexWeight failed)"
    print("probe %2d %-16s key %-16s footer: %s" % (pg.n, pg.name, pg.key, how))
FLEX_VIEWS = [n for n in sorted(VIEWS) if flex_kids(VIEWS[n][0])]
assert FLEX_VIEWS == [BY_NAME["base2"].n], "only base2 has a FlexWeight child next to the footer (the header's base2 note): %s" % (
    FLEX_VIEWS,)

# ================= 0.3: the two vault WINDOW probe pages (kit look; markup = proven properties only) =================
WIN_PAGE_W = 800
WP_ARROWS = PREFIX + "WinArrows"                        # P1: the 3-slot arrow grid (SlotClicking)
WP_GRID = PREFIX + "SgGrid"                             # P2: the 9-slot grid bound to the window's section (InventorySectionId)
PROBE_ITEMS = ["Weapon_Mace_Iron", "Armor_Iron_Head", "Tool_Shovel_Iron"]   # the 3 LOCKED probe items (MaxStack 1: weapon / armor /
                                                                            # tool - Item.processConfig), slots 0-2 of the box
BOX_SLOTS = 9
ARROW_IDS_VAULT = ["Skyy_Vault_Prev", "Skyy_Vault_Info", "Skyy_Vault_Next"]  # SkyyVault's own items (its asset pack), when loaded
ARROW_IDS_VANILLA = ["Weapon_Arrow_Crude", "Ingredient_Bar_Iron", "Weapon_Arrow_Iron"]   # stand-ins when SkyyVault is not loaded
ARROW_NAMES = ["Previous page", "Page 1 of 3", "Next page"]
ARROW_DESC = "Probe arrow: one click prints one chat line, and nothing sticks to your cursor."
LATE_CLOSE_MS = 1500                                    # Esc: the server closes a window the client left open after this long
NET_GRACE_MS = 5000                                     # client packets are still logged this long after the window closed
SYNC_DELAY_MS = 100                                     # review fix 1: the re-send runs this long after the stamp (behind the
                                                        # packet's own handler, which the netty thread queues right after the stamp)
SAW_MS = 1500                                           # a watcher stamp older than this is dropped (never re-sent for)
SYNC_RATE_MS = 250                                      # fallback without the packet watcher: at most one re-send per this long
assert 0 < SYNC_DELAY_MS < SAW_MS and SYNC_RATE_MS > 0
WIN_TEXT = {
    23: {"one": "Look for a chest panel with 3 iron items and your inventory. Tell Claude 1-4 + a screenshot.",
         "checks": ["1. Do you see the 9-slot chest panel with the 3 iron items, and your own inventory?",
                    "2. Drag bread or stone (not an iron mace, helmet or shovel - those 3 are locked) into a free slot of "
                    "that panel and back out: does it move?",
                    "3. Where does the panel sit: left, right, below, above or on top of this page?",
                    "4. Click each arrow below once: one chat line per click, and nothing sticks to your cursor?"],
         "head": "Vault arrow test - click each one once:"},
    24: {"one": "The 9 slots below should copy the chest panel (3 iron items). Tell Claude 1-4 + a screenshot.",
         "checks": ["1. Do the 9 slots below show the 3 iron items (the same as the chest panel, if one shows)?",
                    "2. Drag an iron item inside the 9 slots: it must snap back (the probe items are locked).",
                    "3. Drag bread or stone (not an iron mace, helmet or shovel) into the 9 slots, on to another slot, then "
                    "back: does each move stick? No inventory showing? Say so.",
                    "4. After each move, does chat say Move seen, with the same count before and after?"],
         "head": "The window's 9 slots, drawn by this page:"},
}
# review fix 5: the check that asks for the admin's OWN item names what to use - their own iron mace / helmet / shovel share the probe
# item ids and are refused with no chat line (a refused drag must not read as "the grid does not work"); fix 7: P2 asks to say so when
# no inventory shows (P2 binds only the window section)
for _n, _c in ((23, 1), (24, 2)):
    assert "bread or stone (not an iron mace, helmet or shovel" in WIN_TEXT[_n]["checks"][_c], "window probe %d: fix 5 text" % _n
assert WIN_TEXT[24]["checks"][2].endswith("No inventory showing? Say so."), "window probe 24: fix 7 text"
WIN_NOTE = "Esc, Close or Back ends the probe; if the buttons do nothing, press Esc. Your items go back to your inventory."
assert "if the buttons do nothing, press Esc" in WIN_NOTE        # review fix 8: a pending page acknowledgement drops button clicks
LINE_PX = 21                                            # a 16 px line (the kit's look-list figure); + 4 px per label


def text_h(text, w, size=16, bold=False):
    """Height of a wrapped default label holding `text` in w px (the kit's look-list rule: 21 px per line + 4)."""
    return SUI.text_lines(text, w - 4, size, bold=bold) * LINE_PX + 4


def win_page(wp, page_h=None):
    """(shell, appends + b.set lines, extra Java lines, body height used) of window probe page wp at page height page_h (None = a tall
    first pass; the caller rebuilds it at the exact height)."""
    n = wp.n
    P = PREFIX + ("Win" if n == 23 else "Sg")
    sh = SUI.page_shell(P, WIN_PAGE_W, page_h or SUI.MAX_PAGE_H, wp.title, kind="decorated")
    ap = sh.appends
    body, w = sh.body, sh.inner_w
    tx = WIN_TEXT[n]
    # the ONE line: what to look for + how to report it (it must fit one line - asserted below)
    ap.text(body, P + "One", tx["one"], "strong", h=26, w=w)
    ap.append((body, SUI.spacer(h=6)))
    for i, t in enumerate(tx["checks"]):
        ap.text(body, P + "C" + str(i + 1), t, "default", h=text_h(t, w), w=w, wrap=True)
    ap.append((body, SUI.spacer(h=10)))
    ap.text(body, P + "Hd", tx["head"], "bold", h=26, w=w)
    extra = []
    if n == 23:
        ap.append((body, SUI.item_grid(WP_ARROWS, len(ARROW_IDS_VAULT), 1, drag=False, tooltips=False)))
        extra = [
            "java.util.ArrayList pbArrowSlots = new java.util.ArrayList();",
            "String[] pbAid = @PKG@.ProbeViews.arrowIds();",
            "String[] pbAnm = @PKG@.ProbeViews.arrowNames();",
            "for (int i = 0; i < pbAid.length; i++) {",
            "  @IGS@ pbG = new @IGS@(new @IS@(pbAid[i], 1));",
            "  pbG.setName(pbAnm[i]);",
            "  pbG.setDescription(%s);" % SUI.java_lit(ARROW_DESC),
            "  pbG.setActivatable(true);",
            "  pbArrowSlots.add(pbG);",
            "}",
            'b.set("#%s.Slots", pbArrowSlots);' % WP_ARROWS,
        ]
    else:
        ap.append((body, SUI.item_grid(WP_GRID, BOX_SLOTS, 1, drag=True, tooltips=False)))
    ap.append((body, SUI.spacer(h=10)))
    ap.text(body, P + "Note", WIN_NOTE, "caption", h=22, w=w)
    ap.extend(footer(body))
    used = SUI.used_height(ap, body)
    return sh, ap, extra, used


WVIEWS = {}
for wp in WINP:
    _sh, _ap, _extra, _used = win_page(wp)
    _h = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + _used + FOOT_SLACK
    sh, ap, extra, used = win_page(wp, _h)
    assert used == _used and sh.h == _h <= SUI.MAX_PAGE_H, "window probe %d: the height pass changed the body" % wp.n
    left = SUI.fit([used], sh.inner_h, "window probe %d body" % wp.n)
    assert left == FOOT_SLACK, "window probe %d: %d px left under the footer" % (wp.n, left)
    chk = SUI.Appends(ap)
    chk.sets = list(ap.sets) + list(sh.sets)
    SUI.check_page(chk, PREFIX)                       # markup rules, parents, no duplicate id, every b.set target exists
    SUI.assert_page_size(sh.w, sh.h)
    toks = SUI.assert_proven(chk, allow=(), what="window probe %d" % wp.n)    # proven properties only (InventorySectionId is a b.set
    assert all(g is None for g in toks.values()), "window probe %d: an unproven token %s" % (wp.n, toks)   # after the open, not markup)
    assert [x for x in ap[-4:]] == footer(sh.body), "window probe %d: the footer is the last 4 appends" % wp.n
    for _p, mk in ap:
        assert "InventorySectionId" not in mk, "window probe %d: InventorySectionId is set after the open, never inline" % wp.n
    tx = WIN_TEXT[wp.n]
    SUI.fit([SUI.text_width(tx["one"], 16, bold=True), FIT_MARGIN], sh.inner_w, "window probe %d one line" % wp.n)
    for t in [tx["head"]]:
        SUI.fit([SUI.text_width(t, 16, bold=True), FIT_MARGIN], sh.inner_w, "window probe %d heading" % wp.n)
    SUI.fit([SUI.text_width(WIN_NOTE, SUI.fs(12)), FIT_MARGIN], sh.inner_w, "window probe %d note" % wp.n)   # caption = fs(12)
    for t in tx["checks"]:
        assert SUI.text_lines(t, sh.inner_w - 4, 16) <= 2, "window probe %d: a check line takes 3+ lines: %r" % (wp.n, t)
    java = (sh.appends.java("b", sets=list(sh.sets)) + ("\n" + "\n".join(extra) if extra else ""))
    assert SUI.item_grid_java_is_safe(java.replace("@IGS@", SUI.GRID_SLOT_CLASS).replace("@IS@", SUI.ITEM_STACK_CLASS)), \
        "window probe %d fills a grid slot with a held stack" % wp.n
    WVIEWS[wp.n] = (ap, list(ap.sets) + list(sh.sets), java, "body end, page %d px high, %d px slack" % (sh.h, left), sh.h, extra)
    print("probe %2d %-16s key %-16s footer: %s (window probe, %d appends, %d b.set lines)" % (
        wp.n, wp.name, wp.key, WVIEWS[wp.n][3], len(ap), len(WVIEWS[wp.n][1])))
assert SUI.item_grid(WP_GRID, BOX_SLOTS, 1, drag=True, tooltips=False).count("AreItemsDraggable: true") == 1
assert SUI.item_grid(WP_ARROWS, 3, 1, drag=False, tooltips=False).count("AreItemsDraggable: false; InfoDisplay: None;") == 1
assert len(PROBE_ITEMS) == 3 and len(set(PROBE_ITEMS)) == 3 and BOX_SLOTS - len(PROBE_ITEMS) == 6
assert len(ARROW_IDS_VAULT) == len(ARROW_IDS_VANILLA) == len(ARROW_NAMES) == 3

# ================= the index (flat, proven markup only) =================
FIRST_LINE = "New in 0.3: open %s (23), then %s (24) - the vault window probes. Pages 1-22 are the 0.2 kit probes. Back returns " \
             "here, Esc or Close leaves." % (NEW[0], NEW[1])
FIRST_TXT = "Nothing opened yet - start with %s, then %s (probes %s)." % (
    NEW[0], NEW[1], ", ".join(str(BY_NAME[x].n) for x in NEW))
TITLE = "SkyyUiProbe - kit and window probe pages"
SUB2 = "A disconnect right after you click Open means that page failed - note its number (the server log names it too)."
HEADS = ("Start here - the two window probes first (green Open)", "Then continue here, top to bottom")
KIT_LINE = "Kit %s  |  %d pages  |  chat: /skyprobe list, /skyprobe number or name" % (KIT_ID, len(PROBES))
KIT_W = IX_IN_W - 16 - 170                      # the bottom row: kit line | 16 | Close 170
TITLE_FS, SUB_FS, HEAD_FS, INFO_FS, KIT_FS = 30, 16, 17, 17, 15


def last_text(n):
    """What ProbePage.lastText(n) returns (the Java below builds the same string; the harness compares them)."""
    if n not in BY_N:
        return FIRST_TXT
    nx = ORDER[ORDER.index(n) + 1] if ORDER.index(n) + 1 < len(ORDER) else -1
    return "Last opened: probe %d (%s). Did it look right? " % (n, BY_N[n].name) + (
        "Next: probe %d (%s)." % (nx, BY_N[nx].name) if nx > 0 else "That was the last one.")


def fail_text(n):
    """The Info text after probe n could not be built (ProbePage.handleDataEvent's catch)."""
    return "Probe %d could not be built - see the server log." % n


def nowin_text(n):
    """The Info text when a window probe view is built without its open window (ProbePage.build)."""
    return "Probe %d needs its window - open it with its Open button or /skyprobe %s." % (n, BY_N[n].name)


def entry(ap, col, n, kind):
    """One index entry in column col: line one = number, name, Open; line two = the summary (a b.set label: it has punctuation)."""
    pg = BY_N[n]
    row, top, low = IX + "Row" + str(n), IX + "Top" + str(n), IX + "Low" + str(n)
    ap.append((col, f_group(row, "Top", ENT_H, bg="row")))
    ap.append((row, f_spacer(EDGE, ENT_TOP)))
    ap.append((row, f_group(top, "Left", L1_H)))
    ap.append((top, f_spacer(EDGE, L1_H)))
    ap.append((top, f_label(IX + "Num" + str(n), str(n), L1_H, NUM_FS, "num", bold=True, center=True, w=NUM_W)))
    ap.append((top, f_label(IX + "Name" + str(n), pg.name, L1_H, NAME_FS, "name", bold=True, w=NAME_W)))
    ap.append((top, f_spacer(GAP_W, L1_H)))
    ap.append((top, f_button(IX + "Open" + str(n), "Open", OPEN_W, L1_H, kind)))
    ap.append((row, f_group(low, "Left", L2_H)))
    ap.append((low, f_spacer(WHAT_X, L2_H)))
    f_text(ap, low, IX + "What" + str(n), WHAT[n], L2_H, WHAT_FS, "sub", w=WHAT_W)
    return row, top, low


def build_index():
    ap = SUI.Appends()
    ap.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); Background: %s; Padding: (Horizontal: %d, Vertical: %d); LayoutMode: Top; }"
               % (IX, IX_W, IX_H, FLAT["root"], IX_PADH, IX_PADV)))
    ap.append((IX, "Group { Anchor: (Height: 3); Background: %s; }" % FLAT["stripe"]))
    ap.append((IX, f_label(None, TITLE, 44, TITLE_FS, "title", bold=True, center=True)))
    f_text(ap, IX, IX + "Sub1", FIRST_LINE, 26, SUB_FS, "sub", center=True)
    f_text(ap, IX, IX + "Sub2", SUB2, 26, SUB_FS, "sub", center=True)
    ap.append((IX, f_spacer(10, 8)))
    cols_h = 28 + 4 + PER_COL * ENT_H + (PER_COL - 1) * ENT_GAP
    ap.append((IX, f_group(IX + "Cols", "Left", cols_h)))
    rows = []
    for ci, chunk in enumerate((ORDER[:PER_COL], ORDER[PER_COL:])):
        col = IX + "Col" + "AB"[ci]
        if ci:
            ap.append((IX + "Cols", f_spacer(COL_GAP, cols_h)))
        ap.append((IX + "Cols", f_group(col, "Top", cols_h, w=COL_W)))
        f_text(ap, col, IX + "Head" + "AB"[ci], HEADS[ci], 28, HEAD_FS, "caption", bold=True)
        ap.append((col, f_spacer(10, 4)))
        for j, n in enumerate(chunk):
            if j:
                ap.append((col, f_spacer(10, ENT_GAP)))
            rows.append(entry(ap, col, n, "g" if BY_N[n].name in NEW else "b"))
    ap.append((IX, f_spacer(10, 8)))
    ap.append((IX, f_label(IX + "Info", "", 28, INFO_FS, "title", bold=True, center=True)))  # b.set from ProbePage.info at runtime
    ap.append((IX, "Group #%sBottom { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }" % IX))
    f_text(ap, IX + "Bottom", IX + "Kit", KIT_LINE, 46, KIT_FS, "caption", w=KIT_W)
    ap.append((IX + "Bottom", f_spacer(16, 46)))
    ap.append((IX + "Bottom", f_button(IX + "Close", "Close", 170, 46, "n")))
    return ap, rows, cols_h


IXA, IX_ROWS, COLS_H = build_index()
INFO_SET = (IX + "Info", "Text", SUI.J("info", "Nothing opened yet"))     # the runtime line under the columns (ProbePage.info)
_ixchk = SUI.Appends(IXA)
_ixchk.sets.append(INFO_SET)
SUI.check_page(_ixchk, PREFIX)          # markup rules, every parent exists, no duplicate id, every b.set target exists
SUI.assert_page_size(IX_W, IX_H)
IX_USED = SUI.used_height(IXA, IX)
IX_FREE = SUI.fit([IX_USED], IX_H - 2 * IX_PADV, "index body")
SUI.fit([SUI.used_width(IXA, IX + "Cols")], IX_IN_W, "index columns")
SUI.fit([SUI.used_width(IXA, IX + "Bottom")], IX_IN_W, "index bottom row")
for _c in ("A", "B"):
    SUI.fit([SUI.used_height(IXA, IX + "Col" + _c)], COLS_H, "index column " + _c)
for _row, _top, _low in IX_ROWS:
    SUI.fit([SUI.used_height(IXA, _row)], ENT_H, "index entry " + _row)
    SUI.fit([SUI.used_width(IXA, _top)], COL_W, "index entry line one " + _top)
    SUI.fit([SUI.used_width(IXA, _low)], COL_W, "index entry line two " + _low)
assert len(IX_ROWS) == len(PROBES) == 24 and PER_COL == 12 and len(ORDER) - PER_COL == 12, "24 entries in two columns of 12"
# every text fits its label (the client's font tables, SUI.text_width)
for n in ORDER:
    SUI.fit([SUI.text_width(WHAT[n], WHAT_FS), FIT_MARGIN], WHAT_W, "probe %d summary line" % n)
    SUI.fit([SUI.text_width(BY_N[n].name, NAME_FS, bold=True), FIT_MARGIN], NAME_W, "probe %d name" % n)
IX_TEXTS = [(TITLE, TITLE_FS, True, IX_IN_W), (FIRST_LINE, SUB_FS, False, IX_IN_W), (SUB2, SUB_FS, False, IX_IN_W),
            (HEADS[0], HEAD_FS, True, COL_W), (HEADS[1], HEAD_FS, True, COL_W), (KIT_LINE, KIT_FS, False, KIT_W),
            (FIRST_TXT, INFO_FS, True, IX_IN_W)]
IX_TEXTS += [(last_text(n), INFO_FS, True, IX_IN_W) for n in ORDER] + [(fail_text(n), INFO_FS, True, IX_IN_W) for n in ORDER]
IX_TEXTS += [(nowin_text(n), INFO_FS, True, IX_IN_W) for n in WIN_N]
IX_WIDEST = {}
for _t, _fs, _b, _w in IX_TEXTS:
    _tw = SUI.text_width(_t, _fs, bold=_b)
    SUI.fit([_tw, FIT_MARGIN], _w, "index text %r" % _t[:40])
    if _tw > IX_WIDEST.get(_w, (0, ""))[0]:
        IX_WIDEST[_w] = (_tw, _t)
print("index texts: %d measured, widest per label width: %s" % (len(IX_TEXTS), ", ".join(
    "%.0f / %d px" % (IX_WIDEST[w][0], w) for w in sorted(IX_WIDEST))))
# flat only: the proven table (independent of PROBED: the index never uses a base / trial property, even after it is probed)
IX_TOKENS = SUI.assert_proven(IXA, what="SkyyUiProbe index")
for _p, mk in IXA:
    for bad in ("Common/", "Sounds/", "FontName", "LetterSpacing", "FlexWeight", "Wrap", "TexturePath", "Disabled", "Visible"):
        assert bad not in mk, "index: flat only (%s): %s" % (bad, mk[:100])
    for lm in re.findall(r"LayoutMode:\s*([A-Za-z]+)", mk):
        assert lm in ("Top", "Left"), "index: LayoutMode Top / Left only, not %s" % lm
    assert not re.search(r"Anchor: \([^)]*\b(Top|Bottom|Left|Right|Horizontal|Vertical|Full):", SUI.render(mk)), \
        "index: no Anchor margins (only Width / Height, like the proven flat pages): %s" % mk[:100]
    assert re.match(r"(Group|Label|TextButton)\b", mk), "index: Group / Label / TextButton only: %s" % mk[:60]
for _i, _pr, _v in IXA.sets:
    # < and > are proven only as INLINE text ("< Back"), not through b.set (review 2026-09-29): keep them out of b.set texts
    assert not (isinstance(_v, str) and re.search(r"[<>]", SUI.render(_v))), "index b.set text with < or >: %r" % _v
for _t in [FIRST_TXT] + [last_text(n) for n in ORDER] + [fail_text(n) for n in ORDER] + [nowin_text(n) for n in WIN_N]:
    assert not re.search(r"[<>]", _t), "runtime Info text (b.set) with < or >: %r" % _t
for _n in WIN_N:
    for _i, _pr, _v in WVIEWS[_n][1]:
        assert not (isinstance(_v, str) and re.search(r"[<>]", SUI.render(_v))), "window probe b.set text with < or >: %r" % _v
IX_JAVA = IXA.java("b") + "\n" + SUI.java_set(*INFO_SET)
IX_BINDS = [("#" + IX + "Open" + str(n), "open:" + str(n)) for n in ORDER] + [("#" + IX + "Close", "close")]
IX_BIND = ["ev.addEventBinding(@BT@.Activating, %s, @EVD@.of(\"a\", %s));" % (SUI.java_lit(sel), SUI.java_lit(act))
           for sel, act in IX_BINDS]
print("index: %d appends, %d b.set lines, %d / %d px high (%d free), two columns %s | %s" % (
    len(IXA), len(IXA.sets) + 1, IX_USED, IX_H - 2 * IX_PADV, IX_FREE, ORDER[:PER_COL], ORDER[PER_COL:]))

if DUMP:
    out = {"kit": KIT_ID, "order": ORDER, "names": dict((str(p.n), p.name) for p in PROBES),
           "keys": dict((str(p.n), p.key) for p in PROBES), "whats": dict((str(n), WHAT[n]) for n in ORDER),
           "open_first": NEW + FIRST, "new": NEW, "first_txt": FIRST_TXT, "per_col": PER_COL,
           "what_w": WHAT_W, "what_fs": WHAT_FS, "name_w": NAME_W, "name_fs": NAME_FS, "fit_margin": FIT_MARGIN,
           "info_w": IX_IN_W, "info_fs": INFO_FS, "last_txts": dict((str(n), last_text(n)) for n in ORDER),
           "nowin_txts": dict((str(n), nowin_text(n)) for n in WIN_N),
           "foot": ["#" + NAV_BACK, "#" + NAV_CLOSE],
           "win": {"views": WIN_N, "arrows": "#" + WP_ARROWS, "grid": "#" + WP_GRID, "probe_items": PROBE_ITEMS, "slots": BOX_SLOTS,
                   "arrow_ids_vault": ARROW_IDS_VAULT, "arrow_ids_vanilla": ARROW_IDS_VANILLA, "arrow_names": ARROW_NAMES,
                   "arrow_desc": ARROW_DESC, "late_ms": LATE_CLOSE_MS, "grace_ms": NET_GRACE_MS,
                   "sync_delay_ms": SYNC_DELAY_MS, "saw_ms": SAW_MS, "sync_rate_ms": SYNC_RATE_MS, "texts": dict(
                       (str(k), v) for k, v in WIN_TEXT.items()), "note": WIN_NOTE, "page_w": WIN_PAGE_W},
           "index": {"appends": [[p, SUI.render(m)] for p, m in IXA], "sets": [[i, pr, v] for i, pr, v in IXA.sets],
                     "info": ["#" + IX + "Info", "Text"], "info_set": list(INFO_SET), "binds": [list(x) for x in IX_BINDS],
                     "w": IX_W, "h": IX_H}}
    for n, (ap, sets, _java, how, h, extra) in list(VIEWS.items()) + list(WVIEWS.items()):
        out[str(n)] = {"appends": [[p, SUI.render(m)] for p, m in ap],
                       "sets": [[i, pr, v] for i, pr, v in sets], "extra": extra, "how": how, "h": h}
    with open(DUMP, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("dumped the expected page commands to", DUMP)
    if DUMP_ONLY:
        raise SystemExit(0)

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.uiprobe"
T = {
    "PKG": PKG, "VERSION": VERSION,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "CA": "com.hypixel.hytale.component.ComponentAccessor",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "ES": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "AC": "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "PGM": "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "IGS": "com.hypixel.hytale.server.core.ui.ItemGridSlot",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "VAL": "com.hypixel.hytale.server.core.ui.Value",
    # 0.3: the window probes
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "SIC": "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
    "ICCE": "com.hypixel.hytale.server.core.inventory.container.ItemContainer$ItemContainerChangeEvent",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "MT": "com.hypixel.hytale.server.core.inventory.transaction.MoveTransaction",
    "STX": "com.hypixel.hytale.server.core.inventory.transaction.SlotTransaction",
    "ISX": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "MVT": "com.hypixel.hytale.server.core.inventory.transaction.MoveType",
    "ACT": "com.hypixel.hytale.server.core.inventory.transaction.ActionType",
    "WIN": "com.hypixel.hytale.server.core.entity.entities.player.windows.Window",
    "CW": "com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow",
    "VWIN": "com.hypixel.hytale.server.core.entity.entities.player.windows.ValidatedWindow",
    "CT": "com.hypixel.hytale.component.ComponentType",
    "HOT": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar",
    "STO": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage",
    "BAK": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Backpack",
    "ARM": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Armor",
    "UTI": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility",
    "TOO": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Tool",
    "WM": "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager",
    "EREG": "com.hypixel.hytale.event.EventRegistration",
    "ITEM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "PAD": "com.hypixel.hytale.server.core.io.adapter.PacketAdapters",
    "PPW": "com.hypixel.hytale.server.core.io.adapter.PlayerPacketWatcher",
    "PF": "com.hypixel.hytale.server.core.io.adapter.PacketFilter",
    "PKT": "com.hypixel.hytale.protocol.Packet",
    "MIS": "com.hypixel.hytale.protocol.packets.inventory.MoveItemStack",
    "SMIS": "com.hypixel.hytale.protocol.packets.inventory.SmartMoveItemStack",
    "DIS": "com.hypixel.hytale.protocol.packets.inventory.DropItemStack",
    "IAC": "com.hypixel.hytale.protocol.packets.inventory.InventoryAction",
    "CLW": "com.hypixel.hytale.protocol.packets.window.CloseWindow",
    "SWA": "com.hypixel.hytale.protocol.packets.window.SendWindowAction",
    "COW": "com.hypixel.hytale.protocol.packets.window.ClientOpenWindow",
    "CPE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageEvent",
    "NAVB": NAV_BACK, "NAVC": NAV_CLOSE, "ARROWS": WP_ARROWS, "GRID": WP_GRID,
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
for c, m in ((T["AC"], "requirePermission"), (T["AC"], "setPermissionGroups"), (T["AC"], "addAliases"), (T["AC"], "addUsageVariant"),
             (T["AC"], "withRequiredArg"), (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["MSG"], "raw"), (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"),
             (T["BT"], "Activating"), (T["PAGE"], "rebuild"), (T["PAGE"], "handleDataEvent"), (T["PAGE"], "close"), (T["PAGE"], "build"),
             (T["PGM"], "openCustomPage"), (T["PLA"], "getPageManager"), (T["PLA"], "getComponentType"), (T["LIFE"], "CanDismiss"),
             (PB, "getCommandRegistry"), (PB, "getLogger"), (PB, "shutdown"), (T["VAL"], "ref"),
             # 0.3: the window probes (every engine member the new classes call - API drift fails the build here)
             (T["PGM"], "openCustomPageWithWindows"), (T["PAGE"], "onDismiss"), (T["PAGE"], "sendUpdate"), (T["BT"], "SlotClicking"),
             (T["PLA"], "getWindowManager"), (T["WM"], "getWindow"), (T["WM"], "closeWindow"), (T["WIN"], "getId"),
             (T["CW"], "onClose0"), (T["VWIN"], "validate"), (T["WIN"], "invalidate"), (T["INVC"], "markDirty"),
             (T["HOT"], "getComponentType"), (T["STO"], "getComponentType"), (T["BAK"], "getComponentType"),
             (T["ARM"], "getComponentType"), (T["UTI"], "getComponentType"), (T["TOO"], "getComponentType"),
             (T["SIC"], "cantRemoveFromSlot"), (T["SIC"], "cantAddToSlot"), (T["SIC"], "cantDropFromSlot"),
             (T["SIC"], "internal_getSlot"), (T["IC"], "internal_moveItemStackFromSlot"), (T["IC"], "moveItemStackFromSlot"),
             (T["IC"], "getItemStack"), (T["IC"], "getCapacity"), (T["IC"], "setItemStackForSlot"), (T["IC"], "registerChangeEvent"),
             (T["ICCE"], "transaction"), (T["INVC"], "getCombined"), (T["INVC"], "EVERYTHING"), (T["INVC"], "STORAGE_HOTBAR_BACKPACK"),
             (T["MVT"], "MOVE_FROM_SELF"), (T["ACT"], "REMOVE"), (T["ISX"], "FAILED_ADD"), (T["EREG"], "unregister"),
             (T["IS"], "isEmpty"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IGS"], "setName"), (T["IGS"], "setDescription"),
             (T["IGS"], "setActivatable"), (T["ITEM"], "getAssetMap"), ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset"),
             (T["PAD"], "registerInbound"), (T["PAD"], "deregisterInbound"), (T["PPW"], "accept"), (T["PR"], "getUuid"),
             (T["PR"], "getReference"), (T["REF"], "isValid"), (T["REF"], "getStore"), (T["ST"], "getExternalData"),
             (T["ST"], "getComponent"), (T["ES"], "getWorld"), (T["WLD"], "execute"), (T["WLD"], "scheduleAfter"),
             (T["MIS"], "fromSectionId"), (T["MIS"], "fromSlotId"), (T["MIS"], "quantity"), (T["MIS"], "toSectionId"),
             (T["MIS"], "toSlotId"), (T["SMIS"], "moveType"), (T["DIS"], "inventorySectionId"), (T["DIS"], "slotId"),
             (T["IAC"], "inventoryActionType"), (T["CLW"], "id"), (T["SWA"], "action"), (T["COW"], "type"), (T["CPE"], "type"),
             (T["CPE"], "data")):
    B.probe(pool, c, m)

TOKEN = re.compile(r"@([A-Z]{2,7})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def MR(cls, src):
    """A method whose text holds kit output: added exactly as written (no @TOKEN@ replacement - the tokens are filled in first)."""
    try:
        cls.addMethod(CtNewMethod.make(src, cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, src[:2500]))


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def mk(name, sup=None):
    return pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)


def jl(s):
    return SUI.java_lit(s)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(jl(x) for x in xs)


# every class first (javassist resolves a type by name once it exists in the pool), then the members in dependency order
log = mk("ProbeLog")
views = mk("ProbeViews")
ses = mk("ProbeSession")
box = mk("ProbeBox", T["SIC"])
win = mk("ProbeWindow", T["CW"])
chg = mk("ProbeChange")
ctk = mk("ProbeCountTask")
ltk = mk("ProbeCloseTask")
stk = mk("ProbeSyncTask")
net = mk("ProbeNet")
page = mk("ProbePage", T["PAGE"])
pw = mk("ProbeWin")

# ---- ProbeLog: the server log lines (0.3: + the last 64 lines in memory - the harness reads them; nothing is written anywhere)
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.LinkedList TAIL = new java.util.LinkedList();")
M(log, 'public static String kit() { return %s; }' % jl(KIT_ID))
M(log, r"""
public static synchronized void remember(String s) {
  TAIL.add(s);
  while (TAIL.size() > 64) TAIL.removeFirst();
}""")
M(log, "public static synchronized String[] tail() { return (String[]) TAIL.toArray(new String[0]); }")
M(log, r"""
public static void info(String msg) {
  try { remember(msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyUiProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { remember("WARNING " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyUiProbe] " + msg); } catch (Throwable t) { }
}""")

# ---- ProbeViews: every view's statements (one static method per probe page) + the page list
MAXN = max(BY_N)
NAMES = [""] * (MAXN + 1)
KEYS = [""] * (MAXN + 1)
WHATS = [""] * (MAXN + 1)
for p in PROBES:
    NAMES[p.n], KEYS[p.n], WHATS[p.n] = p.name, p.key, WHAT[p.n]
M(views, "public static int count() { return %d; }" % len(PROBES))
M(views, "public static int[] order() { return new int[] { %s }; }" % ", ".join(str(n) for n in ORDER))
M(views, "public static String[] names() { return new String[] { %s }; }" % ", ".join(jl(x) for x in NAMES))
M(views, "public static String[] keys() { return new String[] { %s }; }" % ", ".join(jl(x) for x in KEYS))
M(views, "public static String[] whats() { return new String[] { %s }; }" % ", ".join(jl(x) for x in WHATS))
M(views, r"""
public static boolean has(int n) {
  String[] a = names();
  return n > 0 && n < a.length && a[n].length() > 0;
}""")
M(views, "public static boolean isWin(int n) { return %s; }" % " || ".join("n == %d" % n for n in WIN_N))
M(views, "public static String nameOf(int n) { return has(n) ? names()[n] : \"?\"; }")
M(views, "public static String keyOf(int n) { return has(n) ? keys()[n] : \"?\"; }")
M(views, "public static String whatOf(int n) { return has(n) ? whats()[n] : \"\"; }")
# the page after n in the list order (-1 after the last one or for a missing page)
M(views, r"""
public static int nextOf(int n) {
  int[] o = order();
  for (int i = 0; i + 1 < o.length; i++) { if (o[i] == n) return o[i + 1]; }
  return -1;
}""")
# a page number (1-24) or a stable name (base1, checkbox, number-field, ..., win, secgrid); -1 = none. Locale.ROOT: under a Turkish /
# Azeri default locale toLowerCase() turns "TILE" into a dotless-i "tile" that matches nothing.
M(views, r"""
public static int find(String s) {
  if (s == null) return -1;
  String t = s.trim().toLowerCase(java.util.Locale.ROOT);
  if (t.startsWith("#")) t = t.substring(1);
  if (t.length() == 0) return -1;
  boolean digits = t.length() <= 3;
  for (int i = 0; i < t.length() && digits; i++) { char c = t.charAt(i); if (c < '0' || c > '9') digits = false; }
  if (digits) {
    int n = Integer.parseInt(t);
    return has(n) ? n : -1;
  }
  String[] a = names();
  for (int i = 1; i < a.length; i++) { if (a[i].length() > 0 && a[i].equals(t)) return i; }
  return -1;
}""")
# P1's arrow items: SkyyVault's own when the server's item asset map knows all three (SkyyVault loaded), else vanilla stand-ins.
# Item.getAssetMap().getAsset(id) is null for an unknown id (ItemStack.getItem() then falls back to Item.UNKNOWN by itself).
M(views, r"""
public static String[] arrowIds() {
  String[] v = %s;
  boolean ok = true;
  try {
    for (int i = 0; i < v.length; i++) { if (@ITEM@.getAssetMap().getAsset(v[i]) == null) ok = false; }
  } catch (Throwable t) { ok = false; }
  if (ok) return v;
  return %s;
}""" % (jarr(ARROW_IDS_VAULT), jarr(ARROW_IDS_VANILLA)))
M(views, "public static String[] arrowNames() { return %s; }" % jarr(ARROW_NAMES))
for n in sorted(VIEWS):
    MR(views, "public static void p%d(%s b) {\n%s\n}" % (n, T["UCB"], VIEWS[n][2]))
M(views, "public static boolean render(@UCB@ b, int n) {\n%s\n  return false;\n}" % "\n".join(
    "  if (n == %d) { p%d(b); return true; }" % (n, n) for n in sorted(VIEWS)))
for n in WIN_N:
    MR(views, "public static void p%d(%s b) {\n%s\n}" % (n, T["UCB"], jv(WVIEWS[n][2])))
M(views, "public static boolean renderWin(@UCB@ b, int n) {\n%s\n  return false;\n}" % "\n".join(
    "  if (n == %d) { p%d(b); return true; }" % (n, n) for n in WIN_N))
MR(views, "public static void index(%s b, %s ev, String info) {\n%s\n%s\n}" % (T["UCB"], T["UEB"], IX_JAVA, jv("\n".join(IX_BIND))))

# ---- ProbeSession: one open (or recently closed) probe window of one admin
for f in ("public @PR@ pr;", "public java.util.UUID owner;", "public String who;", "public int probe;", "public @PKG@.ProbeBox box;",
          "public @PKG@.ProbeWindow win;", "public int winId;", "public @WLD@ world;", "public @ST@ store;", "public @EREG@ reg;",
          "public volatile boolean closed;", "public boolean countQueued;", "public boolean lateQueued;", "public java.util.HashMap last;",
          "public String lastTx;", "public String closingBy;", "public String closedBy;", "public long openedAt;",
          "public long dismissedAt;", "public long closedAt;", "public int moves;", "public boolean syncQueued;", "public int syncs;",
          # review fix 1: sawAt = the packet watcher's stamp (netty thread) of the last client packet for this window; syncFor = the
          # stamp the last queued re-send covered; lastSyncAt = the fallback's rate limit (no watcher) - the last two world thread only
          "public volatile long sawAt;", "public long syncFor;", "public long lastSyncAt;"):
    F(ses, f)
C(ses, "public ProbeSession() { this.winId = -1; this.lastTx = \"\"; this.closedBy = \"\"; }")

# ---- ProbeBox: the scratch container behind a window probe (9 slots: 3 locked probe items + 6 free). Every refusal is by ITEM ID
# wherever the item sits (slot reads are raw internal_getSlot: the engine calls these checks inside the container's write lock).
F(box, "public boolean armed;")
C(box, "public ProbeBox(short cap) { super(cap); this.armed = false; }")
M(box, "public static String[] probeIds() { return %s; }" % jarr(PROBE_ITEMS))
M(box, r"""
public static boolean isProbeId(String id) {
  if (id == null) return false;
  String[] d = probeIds();
  for (int i = 0; i < d.length; i++) { if (d[i].equals(id)) return true; }
  return false;
}""")
M(box, r"""
public static boolean isProbe(@IS@ s) {
  if (s == null || s.isEmpty()) return false;
  return isProbeId(s.getItemId());
}""")
M(box, r"""
public boolean probeAt(short slot) {
  if (slot < 0 || slot >= getCapacity()) return false;
  try { return isProbe(internal_getSlot(slot)); } catch (Throwable t) { return false; }
}""")
M(box, r"""
protected boolean cantRemoveFromSlot(short slot) {
  if (this.armed && probeAt(slot)) return true;
  return super.cantRemoveFromSlot(slot);
}""")
M(box, r"""
protected boolean cantDropFromSlot(short slot) {
  if (this.armed && probeAt(slot)) return true;
  return super.cantDropFromSlot(slot);
}""")
# also refuses a stack with a probe item's id from outside (no copy can enter, so a probe item can never merge or be mistaken) and
# anything onto a probe item: the engine's swap (MoveItemStack onto an occupied slot) asks only the TARGET's cantAddToSlot, never
# its cantRemoveFromSlot (ItemContainer.lambda$internal_moveItemStackFromSlot$5, offsets 196-290)
M(box, r"""
protected boolean cantAddToSlot(short slot, @IS@ add, @IS@ existing) {
  if (this.armed && (isProbe(add) || isProbe(existing) || probeAt(slot))) return true;
  return super.cantAddToSlot(slot, add, existing);
}""")
# SkyyVault VView (live since 0.1.2): the whole-slot move primitive (shift-click, Take All) returns NULL for a slot that refuses
# removal and the engine then NPEs - answer with the engine's own failed MoveTransaction instead
M(box, r"""
public @MT@ refused(short slot, @IC@ to, boolean filter) {
  @IS@ cur = getItemStack(slot);
  @STX@ rm = new @STX@(false, @ACT@.REMOVE, slot, cur, cur, (@IS@) null, false, false, filter);
  return new @MT@(false, rm, @MVT@.MOVE_FROM_SELF, to, @ISX@.FAILED_ADD);
}""")
M(box, r"""
protected @MT@ internal_moveItemStackFromSlot(short slot, @IC@ to, boolean allOrNothing, boolean filter) {
  if (filter && slot >= 0 && slot < getCapacity() && cantRemoveFromSlot(slot)) return refused(slot, to, filter);
  return super.internal_moveItemStackFromSlot(slot, to, allOrNothing, filter);
}""")
M(box, r"""
protected @MT@ internal_moveItemStackFromSlot(short slot, int qty, @IC@ to, boolean allOrNothing, boolean filter) {
  if (filter && slot >= 0 && slot < getCapacity() && cantRemoveFromSlot(slot)) return refused(slot, to, filter);
  return super.internal_moveItemStackFromSlot(slot, qty, to, allOrNothing, filter);
}""")
# a new box: the probe items written in BEFORE the box is armed, then read back (count) - only ever called on the world thread
M(box, r"""
public static @PKG@.ProbeBox make() {
  @PKG@.ProbeBox b = new @PKG@.ProbeBox((short) %d);
  String[] d = probeIds();
  for (int i = 0; i < d.length; i++) b.setItemStackForSlot((short) i, new @IS@(d[i], 1));
  b.armed = true;
  return b;
}""" % BOX_SLOTS)

# ---- ProbeWindow / ProbeChange / ProbeCountTask / ProbeCloseTask / ProbeNet: fields + constructors (bodies after ProbeWin)
win.addInterface(pool.get(T["VWIN"]))
F(win, "public @PKG@.ProbeSession sess;")
C(win, "public ProbeWindow(@IC@ c, @PKG@.ProbeSession s) { super(c); this.sess = s; }")
# Window.invalidate() is PROTECTED: only the window itself may call it (SkyyVault 0.1.5 VWindow.resend - the engine then sends one
# UpdateWindow on its next window tick)
M(win, "public void resend() { invalidate(); }")
chg.addInterface(pool.get("java.util.function.Consumer"))
F(chg, "public @PKG@.ProbeSession sess;")
C(chg, "public ProbeChange(@PKG@.ProbeSession s) { this.sess = s; }")
for k in (ctk, ltk, stk):
    k.addInterface(pool.get("java.lang.Runnable"))
    F(k, "public @PKG@.ProbeSession sess;")
C(ctk, "public ProbeCountTask(@PKG@.ProbeSession s) { this.sess = s; }")
C(ltk, "public ProbeCloseTask(@PKG@.ProbeSession s) { this.sess = s; }")
C(stk, "public ProbeSyncTask(@PKG@.ProbeSession s) { this.sess = s; }")
net.addInterface(pool.get(T["PPW"]))
C(net, "public ProbeNet() { }")

# ---- ProbePage: the one inline page (view 0 = index, n = probe page n), switched by rebuild() after a click; window views (23 / 24)
# carry their ProbeSession (set by ProbeWin.open before openCustomPageWithWindows)
F(page, "public int view;")
F(page, "public String info;")
F(page, "public @PKG@.ProbeSession sess;")
M(page, r"""
public static String lastText(int n) {
  if (!@PKG@.ProbeViews.has(n)) return %s;
  int nx = @PKG@.ProbeViews.nextOf(n);
  return "Last opened: probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + "). Did it look right? "
    + (nx > 0 ? "Next: probe " + nx + " (" + @PKG@.ProbeViews.nameOf(nx) + ")." : "That was the last one.");
}""" % jl(FIRST_TXT))
M(page, r"""
public static String noWinText(int n) {
  return "Probe " + n + " needs its window - open it with its Open button or /skyprobe " + @PKG@.ProbeViews.nameOf(n) + ".";
}""")
C(page, r"""
public ProbePage(@PR@ pr, int view) {
  super(pr, @LIFE@.CanDismiss);
  this.view = view;
  this.info = lastText(view);
}""")
# one string value out of the page event JSON (SkyyBank 0.1.3 BankPage.jsonStr, verbatim)
M(page, r"""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) {
      char n = data.charAt(i + 1);
      if (n == 'u' && i + 5 < data.length()) {
        try { sb.append((char) Integer.parseInt(data.substring(i + 2, i + 6), 16)); } catch (Throwable t) { }
        i += 6;
        continue;
      }
      if (n == 'n' || n == 'r' || n == 't' || n == 'b' || n == 'f') sb.append(' '); else sb.append(n);
      i += 2;
      continue;
    }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
# SlotClicking payload: {"a":"arrow","SlotIndex":2} (the value may be quoted) - SkyyMenu 0.3.4 MenuUtil.jsonInt, verbatim
M(page, r"""
public static int jsonInt(String data, String key) {
  if (data == null || key == null) return -1;
  int p = data.indexOf("\"" + key + "\"");
  if (p < 0) return -1;
  int c = data.indexOf(':', p);
  if (c < 0) return -1;
  int i = c + 1;
  while (i < data.length() && (data.charAt(i) == ' ' || data.charAt(i) == '"')) i++;
  int j = i;
  while (j < data.length() && (Character.isDigit(data.charAt(j)) || data.charAt(j) == '-')) j++;
  if (j == i) return -1;
  try { return Integer.parseInt(data.substring(i, j)); } catch (Throwable t) { return -1; }
}""")
# one chat line to the admin (ProbeCmds.tell is made after this class, so the page has its own copy)
M(page, r"""
public static void say(@PR@ pr, String s) {
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[SkyyUiProbe] " + s)); } catch (Throwable t) { }
}""")

# ---- ProbeWin: the window probes (all inventory work on the world thread; the packet watcher only logs)
F(pw, "public static java.util.concurrent.ConcurrentHashMap BOXES = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> box
F(pw, "public static java.util.concurrent.ConcurrentHashMap SESS = new java.util.concurrent.ConcurrentHashMap();")   # uuid -> newest
F(pw, "public static volatile @PF@ NET;")      # written under ensureNet / stopNet (synchronized), read by touched() on world threads
M(pw, r"""
public static void say(@PR@ pr, String s) {
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[SkyyUiProbe] " + s)); } catch (Throwable t) { }
}""")
M(pw, r"""
public static String cut(String s, int n) {
  if (s == null) return "";
  return s.length() <= n ? s : s.substring(0, n) + "...";
}""")
# ---- counting: item id -> long[1] quantity, over one or more containers
M(pw, r"""
public static void addCounts(java.util.HashMap m, @IC@ c) {
  if (c == null) return;
  int n = c.getCapacity();
  for (int i = 0; i < n; i++) {
    @IS@ s = c.getItemStack((short) i);
    if (s == null || s.isEmpty()) continue;
    String id = s.getItemId();
    long[] v = (long[]) m.get(id);
    if (v == null) { v = new long[1]; m.put(id, v); }
    v[0] += (long) s.getQuantity();
  }
}""")
M(pw, r"""
public static java.util.HashMap counts(@IC@ a, @IC@ b) {
  java.util.HashMap m = new java.util.HashMap();
  addCounts(m, a);
  addCounts(m, b);
  return m;
}""")
M(pw, r"""
public static long val(java.util.HashMap m, String k) {
  if (m == null) return 0L;
  long[] v = (long[]) m.get(k);
  return v == null ? 0L : v[0];
}""")
M(pw, r"""
public static long total(java.util.HashMap m) {
  long t = 0L;
  if (m == null) return 0L;
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) t += ((long[]) it.next())[0];
  return t;
}""")
# "" = the same; else "id a -> b, ..." (sorted, so the line is stable)
M(pw, r"""
public static String diff(java.util.HashMap a, java.util.HashMap b) {
  java.util.TreeSet keys = new java.util.TreeSet();
  if (a != null) keys.addAll(a.keySet());
  if (b != null) keys.addAll(b.keySet());
  StringBuilder sb = new StringBuilder();
  java.util.Iterator it = keys.iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    long x = val(a, k);
    long y = val(b, k);
    if (x != y) {
      if (sb.length() > 0) sb.append(", ");
      sb.append(k).append(' ').append(x).append(" -> ").append(y);
    }
  }
  return sb.toString();
}""")
# how many of the 3 probe items are in the box (each exactly once)
M(pw, r"""
public static int probesIn(@PKG@.ProbeBox box) {
  if (box == null) return 0;
  String[] d = @PKG@.ProbeBox.probeIds();
  java.util.HashMap m = new java.util.HashMap();
  addCounts(m, box);
  int k = 0;
  for (int i = 0; i < d.length; i++) { if (val(m, d[i]) == 1L) k++; }
  return k;
}""")
# the admin's OWN items in the box (everything but the probe items)
M(pw, r"""
public static int ownIn(@PKG@.ProbeBox box) {
  if (box == null) return 0;
  int n = box.getCapacity();
  int k = 0;
  for (int i = 0; i < n; i++) {
    @IS@ s = box.getItemStack((short) i);
    if (s == null || s.isEmpty() || @PKG@.ProbeBox.isProbe(s)) continue;
    k += s.getQuantity();
  }
  return k;
}""")
M(pw, r"""
public static String ownList(@PKG@.ProbeBox box) {
  StringBuilder sb = new StringBuilder();
  if (box == null) return "";
  int n = box.getCapacity();
  for (int i = 0; i < n; i++) {
    @IS@ s = box.getItemStack((short) i);
    if (s == null || s.isEmpty() || @PKG@.ProbeBox.isProbe(s)) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append(s.getItemId()).append(" x").append(s.getQuantity());
  }
  return sb.toString();
}""")
M(pw, r"""
public static @IC@ playerAll(@CA@ a, @REF@ ref) {
  try { return @INVC@.getCombined(a, ref, @INVC@.EVERYTHING); } catch (Throwable t) { return null; }
}""")
M(pw, r"""
public static @IC@ playerReturn(@CA@ a, @REF@ ref) {
  try { return @INVC@.getCombined(a, ref, @INVC@.STORAGE_HOTBAR_BACKPACK); } catch (Throwable t) { return null; }
}""")
M(pw, r"""
public static @PKG@.ProbeBox boxFor(java.util.UUID u) {
  @PKG@.ProbeBox b = (@PKG@.ProbeBox) BOXES.get(u);
  if (b != null) return b;
  b = @PKG@.ProbeBox.make();
  BOXES.put(u, b);
  return b;
}""")
# the return on close (vanilla StructuralCraftingWindow.onClose0 pattern, storage first): every own stack moves with the engine's
# own whole-slot move (what does not fit stays in its slot), counted before and after (box + the player's whole inventory, per id).
# Returns { log line, chat line or null }. Pure container work: the harness drives it with stand-in containers.
M(pw, r"""
public static String[] returnTo(@PKG@.ProbeBox box, @IC@ inv, @IC@ all) {
  String[] out = new String[2];
  int own = ownIn(box);
  if (box == null || own == 0) { out[0] = "nothing of the player's was in the probe box"; return out; }
  if (inv == null || all == null) {
    out[0] = "the player's inventory could not be read - " + own + " item(s) stay in the probe box (" + ownList(box) + ")";
    out[1] = own + " of your items stayed in the probe window (your inventory could not be read) - open /skyprobe win to take them.";
    return out;
  }
  java.util.HashMap before = counts(box, all);
  int n = box.getCapacity();
  for (int i = 0; i < n; i++) {
    @IS@ s = box.getItemStack((short) i);
    if (s == null || s.isEmpty() || @PKG@.ProbeBox.isProbe(s)) continue;
    try { box.moveItemStackFromSlot((short) i, inv); } catch (Throwable t) { @PKG@.ProbeLog.warn("returning probe box slot " + i + " failed: " + t); }
  }
  java.util.HashMap after = counts(box, all);
  int left = ownIn(box);
  String d = diff(before, after);
  out[0] = "returned " + (own - left) + " item(s) from the probe box to the inventory"
    + (left > 0 ? ", " + left + " stayed in the box (inventory full: " + ownList(box) + ")" : "")
    + "; counted " + total(before) + " items before and " + total(after) + " after"
    + (d.length() == 0 ? " - nothing created or lost" : " - COUNT CHANGED: " + d);
  if (d.length() > 0) out[1] = "The item count changed while your probe items were returned (" + d + ") - tell Claude.";
  else if (left > 0) out[1] = left + " of your items stayed in the probe window (inventory full) - make room, then open /skyprobe win to take them.";
  else out[1] = "Your " + own + " item(s) from the probe window are back in your inventory (counted before and after: nothing lost).";
  return out;
}""")
# ---- the client packets of a probe window (log only; PlayerPacketWatcher runs on the network thread)
M(pw, r"""
public static String sec(int s, int win) {
  if (win >= 0 && s == win) return "the probe window (" + s + ")";
  if (s == -1) return "hotbar";
  if (s == -2) return "storage";
  if (s == -3) return "armor";
  if (s == -5) return "utility";
  if (s == -8) return "tools";
  if (s == -9) return "backpack";
  if (s >= 0) return "window " + s;
  return "section " + s;
}""")
M(pw, r"""
public static String describe(Object p, int win) {
  if (p == null) return null;
  if (p instanceof @MIS@) {
    @MIS@ m = (@MIS@) p;
    return "MoveItemStack x" + m.quantity + " from " + sec(m.fromSectionId, win) + " slot " + m.fromSlotId + " to " + sec(m.toSectionId, win) + " slot " + m.toSlotId;
  }
  if (p instanceof @SMIS@) {
    @SMIS@ m = (@SMIS@) p;
    return "SmartMoveItemStack (shift-click) x" + m.quantity + " from " + sec(m.fromSectionId, win) + " slot " + m.fromSlotId + " (" + m.moveType + ")";
  }
  if (p instanceof @DIS@) {
    @DIS@ m = (@DIS@) p;
    return "DropItemStack x" + m.quantity + " from " + sec(m.inventorySectionId, win) + " slot " + m.slotId;
  }
  if (p instanceof @IAC@) {
    @IAC@ m = (@IAC@) p;
    return "InventoryAction " + m.inventoryActionType + " on " + sec(m.inventorySectionId, win);
  }
  if (p instanceof @CLW@) {
    @CLW@ m = (@CLW@) p;
    return "CloseWindow " + (win >= 0 && m.id == win ? "for the probe window (" + m.id + ")" : "for window " + m.id);
  }
  if (p instanceof @SWA@) {
    @SWA@ m = (@SWA@) p;
    return "SendWindowAction on " + sec(m.id, win) + ": " + (m.action == null ? "?" : m.action.getClass().getSimpleName());
  }
  if (p instanceof @COW@) {
    @COW@ m = (@COW@) p;
    return "ClientOpenWindow " + m.type;
  }
  if (p instanceof @CPE@) {
    @CPE@ m = (@CPE@) p;
    return "CustomPageEvent " + m.type + (m.data == null ? "" : " " + cut(m.data, 120));
  }
  return null;
}""")
# review fix 1: the client packets whose result the client may have guessed for the probe window, so the server re-sends the truth
# after them: a MoveItemStack with either end on the window, every shift-click (SmartMoveItemStack has no destination - the engine may
# put the stack into the window), a DropItemStack / InventoryAction on the window, a SendWindowAction for it. Never CloseWindow,
# ClientOpenWindow or page events.
M(pw, r"""
public static boolean wantsResend(Object p, int win) {
  if (p == null || win < 0) return false;
  if (p instanceof @MIS@) {
    @MIS@ m = (@MIS@) p;
    return m.fromSectionId == win || m.toSectionId == win;
  }
  if (p instanceof @SMIS@) return true;
  if (p instanceof @DIS@) return ((@DIS@) p).inventorySectionId == win;
  if (p instanceof @IAC@) return ((@IAC@) p).inventorySectionId == win;
  if (p instanceof @SWA@) return ((@SWA@) p).id == win;
  return false;
}""")
# the watcher (netty thread, before the engine's handler queues its world task): stamp sawAt for a packet the window needs a re-send
# after, log the packet; a session closed longer than the grace leaves SESS here (review fix 4: no closed session kept per admin)
M(pw, r"""
public static void packet(@PR@ pr, Object p) {
  if (pr == null || p == null || SESS.isEmpty()) return;
  java.util.UUID u = pr.getUuid();
  @PKG@.ProbeSession s = (@PKG@.ProbeSession) SESS.get(u);
  if (s == null) return;
  long now = System.currentTimeMillis();
  boolean shut = s.closed;
  if (shut && now - s.closedAt > %dL) { SESS.remove(u, s); return; }
  if (!shut && wantsResend(p, s.winId)) s.sawAt = now;
  String d = describe(p, s.winId);
  if (d == null) return;
  @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": the client sent " + d + (shut ? " (after the window closed)" : ""));
}""" % NET_GRACE_MS)
M(pw, r"""
public static synchronized void ensureNet() {
  if (NET != null) return;
  try {
    NET = @PAD@.registerInbound((@PPW@) new @PKG@.ProbeNet());
    @PKG@.ProbeLog.info("watching the client's inventory / window / page packets while a probe window is open (log only)");
  } catch (Throwable t) { NET = null; @PKG@.ProbeLog.warn("could not watch the client's packets (the probes still work, the log just has less): " + t); }
}""")
M(pw, r"""
public static synchronized void stopNet() {
  if (NET == null) return;
  try { @PAD@.deregisterInbound(NET); } catch (Throwable t) { }
  NET = null;
}""")
# ---- the truth after every client packet for the probe window (ProbeWindow.validate, world thread): a REFUSED move (a locked probe
# item) changes nothing, fires no change event and the engine re-sends nothing, so the client could keep its own guess (an item shown
# moved / a ghost in the inventory). One task re-sends the window (resend -> UpdateWindow) and the player's six inventory sections
# (markDirty -> PlayerSendInventorySystem) - SkyyVault 0.1.5 resync - once per watcher stamp (review fix 1, wantSync below).
M(pw, r"""
public static @CT@ invType(int i) {
  if (i == 0) return @HOT@.getComponentType();
  if (i == 1) return @STO@.getComponentType();
  if (i == 2) return @BAK@.getComponentType();
  if (i == 3) return @ARM@.getComponentType();
  if (i == 4) return @UTI@.getComponentType();
  if (i == 5) return @TOO@.getComponentType();
  return null;
}""")
M(pw, r"""
public static void markInv(@ST@ st, @REF@ ref) {
  for (int i = 0; i < 6; i++) {
    try {
      @INVC@ c = (@INVC@) st.getComponent(ref, invType(i));
      if (c != null) c.markDirty();
    } catch (Throwable t) { }
  }
}""")
# review fix 1: validate() runs for every inventory packet that names the window AND on every movement tick (Player.moveTo ->
# WindowManager.validateWindows; knockback, teleports), so a re-send needs a NEW watcher stamp: one re-send per stamp (the two validate
# calls of one MoveItemStack, or a movement validate that runs before the packet's own handler, share it - the re-send is delayed, so it
# still lands after that handler); while one is queued a newer stamp is left for the next validate (the queued one covers every packet
# handled before it runs); a stamp older than SAW_MS is dropped. watched = false (no packet watcher): at most one per SYNC_RATE_MS.
M(pw, r"""
public static boolean wantSync(@PKG@.ProbeSession s, long now, boolean watched) {
  if (s == null || s.closed || s.syncQueued) return false;
  if (!watched) {
    if (s.lastSyncAt > 0L && now - s.lastSyncAt < %dL) return false;
    s.lastSyncAt = now;
    return true;
  }
  long seen = s.sawAt;
  if (seen == 0L || seen == s.syncFor) return false;
  s.syncFor = seen;
  return now - seen <= %dL;
}""" % (SYNC_RATE_MS, SAW_MS))
M(pw, r"""
public static void touched(@PKG@.ProbeSession s) {
  if (s == null || s.world == null) return;
  if (!wantSync(s, System.currentTimeMillis(), NET != null)) return;
  s.syncQueued = true;
  try { s.world.scheduleAfter(new @PKG@.ProbeSyncTask(s), %dL, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { s.syncQueued = false; }
}""" % SYNC_DELAY_MS)
M(pw, r"""
public static void syncNow(@PKG@.ProbeSession s) {
  if (s == null) return;
  s.syncQueued = false;
  if (s.closed) return;
  try {
    @REF@ ref = s.pr.getReference();
    if (ref == null || !ref.isValid() || ref.getStore() != s.store) return;
    s.win.resend();
    markInv(s.store, ref);
    s.syncs++;
  } catch (Throwable t) { @PKG@.ProbeLog.warn("probe " + s.probe + ": re-sending the window failed: " + t); }
}""")
# ---- the move handler: every successful change of the box (MoveItemStack / shift-click / drop / Take All ... handled by the engine)
# queues ONE count on the world thread (after the whole packet handler); countLine compares it with the last count
M(pw, r"""
public static void noteChange(@PKG@.ProbeSession s, Object ev) {
  if (s == null || s.closed) return;
  try { s.lastTx = ((@ICCE@) ev).transaction().getClass().getSimpleName(); } catch (Throwable t) { }
  if (s.countQueued || s.world == null) return;
  s.countQueued = true;
  try { s.world.execute(new @PKG@.ProbeCountTask(s)); } catch (Throwable t) { s.countQueued = false; }
}""")
# { log line, chat line, "1" when it is a WARNING } for a count `now` after a move; s.last becomes `now`
M(pw, r"""
public static String[] countLine(@PKG@.ProbeSession s, java.util.HashMap now) {
  String[] out = new String[3];
  String d = diff(s.last, now);
  int pi = probesIn(s.box);
  s.moves++;
  out[0] = "probe " + s.probe + " " + s.who + ": move " + s.moves + " seen" + (s.lastTx == null || s.lastTx.length() == 0 ? "" : " (" + s.lastTx + ")")
    + ": counted " + total(s.last) + " items before and " + total(now) + " after (probe box + inventory)"
    + (d.length() == 0 ? " - nothing created or lost" : " - COUNT CHANGED: " + d) + "; probe items in the box: " + pi + " of 3";
  if (pi != 3) out[1] = "A locked probe item left the probe window - tell Claude (that is a bug).";
  else if (d.length() > 0) out[1] = "Move seen, but the count changed (" + d + ") - did you drop or pick something up, or did a bag sweep or refill a stack? Tell Claude.";
  else out[1] = "Move seen - " + total(now) + " items counted before and after: nothing created or lost.";
  out[2] = (pi != 3 || d.length() > 0) ? "1" : "0";
  s.last = now;
  return out;
}""")
M(pw, r"""
public static void countNow(@PKG@.ProbeSession s) {
  if (s == null) return;
  s.countQueued = false;
  if (s.closed) return;
  try {
    @REF@ ref = s.pr.getReference();
    if (ref == null || !ref.isValid() || ref.getStore() != s.store) return;
    String[] r = countLine(s, counts(s.box, playerAll(s.store, ref)));
    if ("1".equals(r[2])) @PKG@.ProbeLog.warn(r[0]); else @PKG@.ProbeLog.info(r[0]);
    say(s.pr, r[1]);
  } catch (Throwable t) { @PKG@.ProbeLog.warn("probe " + s.probe + ": counting after a move failed: " + t); }
}""")
# review fix 4: a CLOSED session lets go of everything heavy - SESS keeps the newest session per admin, and a kept World / Store would
# keep an unloaded instance world alive. What stays: owner, who, probe, winId, closed / closedAt / closedBy (the 5 s packet grace and the
# late-close log read them) and the box (kept per admin in BOXES anyway). Only ever called once closed is set.
M(pw, r"""
public static void release(@PKG@.ProbeSession s) {
  if (s == null || !s.closed) return;
  s.reg = null;
  s.win = null;
  s.world = null;
  s.store = null;
  s.pr = null;
  s.last = null;
}""")
# the window closed (ProbeWindow.onClose0 - every path: CloseWindow from the client, the server's close, the engine's closeAllWindows on a
# world change / disconnect): stop counting, then return the admin's own items unless the NEXT window probe already shows the same box.
# closedAt is written BEFORE the volatile closed flag (the netty thread's grace check reads closed, then closedAt).
M(pw, r"""
public static void windowClosed(@PKG@.ProbeSession s, @REF@ ref, @CA@ a) {
  if (s == null || s.closed) return;
  s.closedAt = System.currentTimeMillis();
  s.closed = true;
  s.closedBy = s.closingBy != null ? "the server (" + s.closingBy + ")" : "the client or the engine";
  try { if (s.reg != null) s.reg.unregister(); } catch (Throwable t) { }
  @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": window " + s.winId + " closed by " + s.closedBy
    + (s.dismissedAt > 0L ? ", " + (s.closedAt - s.dismissedAt) + " ms after the page closed" : " (the page was still open)")
    + "; " + s.moves + " counted move(s), " + s.syncs + " window re-send(s) after client packets");
  @PKG@.ProbeSession cur = (@PKG@.ProbeSession) SESS.get(s.owner);
  if (cur != null && cur != s && !cur.closed && cur.box == s.box) {
    @PKG@.ProbeLog.info("probe " + s.probe + ": the probe box stays open in probe " + cur.probe + " - its items are returned when that window closes");
    release(s);
    return;
  }
  String[] r = returnTo(s.box, playerReturn(a, ref), playerAll(a, ref));
  if (r[0].indexOf("COUNT CHANGED") >= 0) @PKG@.ProbeLog.warn("probe " + s.probe + " " + s.who + ": " + r[0]);
  else @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": " + r[0]);
  if (r[1] != null) say(s.pr, r[1]);
  release(s);
}""")
# end a session whose window is not registered any more (or could not be closed): the admin's items stay in the box (kept per admin)
M(pw, r"""
public static void endQuiet(@PKG@.ProbeSession s, String why) {
  if (s == null || s.closed) return;
  s.closedAt = System.currentTimeMillis();
  s.closed = true;
  s.closedBy = why;
  try { if (s.reg != null) s.reg.unregister(); } catch (Throwable t) { }
  int own = ownIn(s.box);
  @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": session ended (" + why + ")" + (own > 0 ? "; " + own + " own item(s) stay in the probe box: " + ownList(s.box) : ""));
  release(s);
}""")
# the server closes ITS OWN window only (WindowManager.closeWindow throws for a gone id and would close another window under a reused id)
M(pw, r"""
public static void closeNow(@PKG@.ProbeSession s, @REF@ ref, @ST@ st, String why) {
  if (s == null || s.closed) return;
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) {
      @WM@ wm = p.getWindowManager();
      if (wm != null && s.winId >= 0 && wm.getWindow(s.winId) == s.win) {
        s.closingBy = why;
        wm.closeWindow(ref, s.winId, st);
      }
    }
  } catch (Throwable t) { @PKG@.ProbeLog.warn("probe " + s.probe + ": closing the probe window failed (" + why + "): " + t); }
  if (!s.closed) endQuiet(s, "window not open any more (" + why + ")");
}""")
# the page was closed or replaced (onDismiss): the engine never closes windows here - check again in 1.5 s on the world thread
M(pw, r"""
public static void dismissed(@PKG@.ProbeSession s) {
  if (s == null || s.closed) return;
  if (s.dismissedAt == 0L) s.dismissedAt = System.currentTimeMillis();
  if (s.lateQueued || s.world == null) return;
  s.lateQueued = true;
  try { s.world.scheduleAfter(new @PKG@.ProbeCloseTask(s), %dL, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { s.lateQueued = false; @PKG@.ProbeLog.warn("probe " + s.probe + ": could not schedule the window check: " + t); }
}""" % LATE_CLOSE_MS)
M(pw, r"""
public static void lateClose(@PKG@.ProbeSession s) {
  if (s == null) return;
  if (s.closed) {
    @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": 1.5 s after the page closed the window was already closed (by " + s.closedBy + ")");
    return;
  }
  try {
    @REF@ ref = s.pr.getReference();
    if (ref == null || !ref.isValid() || ref.getStore() != s.store) {
      @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": the player left this world - the engine closes the window");
      return;
    }
    @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": the window was still open 1.5 s after the page closed (Esc or another page) - the client did NOT close it with the page; the server closes it now");
    closeNow(s, ref, s.store, "page closed 1.5 s ago");
  } catch (Throwable t) { @PKG@.ProbeLog.warn("probe " + s.probe + ": the window check failed: " + t); }
}""")
# P1's arrow grid: one press = one chat line (+ a log line)
M(pw, r"""
public static void arrow(@PR@ pr, int idx) {
  String[] nm = @PKG@.ProbeViews.arrowNames();
  String[] id = @PKG@.ProbeViews.arrowIds();
  if (idx < 0 || idx >= nm.length) { say(pr, "A click on the arrow grid without a slot (SlotIndex " + idx + ") - tell Claude."); return; }
  @PKG@.ProbeLog.info("probe 23 " + (pr == null ? "?" : pr.getUsername()) + ": arrow " + (idx + 1) + " (" + nm[idx] + ", " + id[idx] + ") pressed");
  say(pr, "Arrow " + (idx + 1) + " (" + nm[idx] + ") pressed - the server got it on the first click. Did anything stick to your cursor?");
}""")
# open window probe n: a NEW ProbePage + a ProbeWindow over the admin's probe box, through openCustomPageWithWindows (world thread:
# the command or a page click). Order: a new session first, the page + window, then (P2) the one InventorySectionId update, the
# counting baseline, and only then the previous probe window closes (new page first - the SkyyVault askBuy order).
M(pw, r"""
public static boolean open(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ w, int n) {
  String who = pr == null ? "?" : pr.getUsername();
  if (!@PKG@.ProbeViews.isWin(n)) return false;
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) { say(pr, "Probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + ") could not be opened (no player component)."); return false; }
  java.util.UUID u = pr.getUuid();
  @PKG@.ProbeSession old = (@PKG@.ProbeSession) SESS.get(u);
  @PKG@.ProbeSession s = new @PKG@.ProbeSession();
  s.pr = pr;
  s.owner = u;
  s.who = who;
  s.probe = n;
  s.world = w;
  s.store = st;
  s.openedAt = System.currentTimeMillis();
  boolean ok = false;
  try {
    s.box = boxFor(u);
    s.win = new @PKG@.ProbeWindow(s.box, s);
    @PKG@.ProbePage pg = new @PKG@.ProbePage(pr, n);
    pg.sess = s;
    ensureNet();
    SESS.put(u, s);
    @PKG@.ProbeLog.info("opening probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + ") for " + who + ": openCustomPageWithWindows with a ContainerWindow over the " + s.box.getCapacity() + "-slot probe box");
    ok = p.getPageManager().openCustomPageWithWindows(ref, st, pg, new @WIN@[] { s.win });
    if (ok) {
      s.winId = s.win.getId();
      if (n == 24) {
        @UCB@ ub = new @UCB@();
        ub.set("#@GRID@.InventorySectionId", s.winId);
        pg.sendUpdate(ub);
        @PKG@.ProbeLog.info("probe 24 " + who + ": sent #@GRID@.InventorySectionId = " + s.winId + " (one page update, after the window opened)");
      }
      s.reg = s.box.registerChangeEvent(new @PKG@.ProbeChange(s));
      s.last = counts(s.box, playerAll(st, ref));
      @PKG@.ProbeLog.info("sent probe " + n + ": window id " + s.winId + ", probe items in the box " + probesIn(s.box) + " of 3, own items in the box "
        + ownIn(s.box) + ", counted " + total(s.last) + " items (probe box + inventory)");
    }
  } catch (Throwable t) {
    ok = false;
    @PKG@.ProbeLog.warn("could not open probe " + n + ": " + t);
  }
  if (!ok) {
    if (s.win != null && s.win.getId() >= 0) { s.winId = s.win.getId(); closeNow(s, ref, st, "open failed"); }
    endQuiet(s, "open failed");
    say(pr, "Probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + ") could not be opened - see the server log.");
    return false;
  }
  if (old != null && !old.closed && old != s) closeNow(old, ref, st, "replaced by probe " + n);
  return true;
}""")
M(pw, r"""
public static void shutdown() {
  stopNet();
  try {
    java.util.Iterator it = BOXES.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      @PKG@.ProbeBox b = (@PKG@.ProbeBox) e.getValue();
      int own = ownIn(b);
      if (own > 0) @PKG@.ProbeLog.warn("server stop: the probe box of " + e.getKey() + " still holds " + own + " of the admin's own item(s): " + ownList(b) + " - give them back by hand");
    }
  } catch (Throwable t) { }
}""")

# ---- bodies that call ProbeWin
# release after windowClosed: a no-op when windowClosed already let go (or the session is still open), the cleanup when it threw
M(win, r"""
public void onClose0(@REF@ ref, @CA@ a) {
  try { super.onClose0(ref, a); } catch (Throwable t) { }
  try { @PKG@.ProbeWin.windowClosed(this.sess, ref, a); } catch (Throwable t) { @PKG@.ProbeLog.warn("probe window close handling failed: " + t); }
  try { @PKG@.ProbeWin.release(this.sess); } catch (Throwable t) { }
}""")
M(win, r"""
public boolean validate(@REF@ ref, @CA@ a) {
  try { @PKG@.ProbeWin.touched(this.sess); } catch (Throwable t) { }
  return true;
}""")
M(stk, r"""
public void run() {
  try { @PKG@.ProbeWin.syncNow(this.sess); } catch (Throwable t) { }
}""")
M(chg, r"""
public void accept(Object ev) {
  try { @PKG@.ProbeWin.noteChange(this.sess, ev); } catch (Throwable t) { }
}""")
M(ctk, r"""
public void run() {
  try { @PKG@.ProbeWin.countNow(this.sess); } catch (Throwable t) { }
}""")
M(ltk, r"""
public void run() {
  try { @PKG@.ProbeWin.lateClose(this.sess); } catch (Throwable t) { }
}""")
M(net, r"""
public void accept(@PR@ pr, @PKT@ p) {
  try { @PKG@.ProbeWin.packet(pr, p); } catch (Throwable t) { }
}""")

# ---- ProbePage: build / clicks / dismiss
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  if (@PKG@.ProbeViews.isWin(this.view)) {
    if (this.sess != null && !this.sess.closed && @PKG@.ProbeViews.renderWin(b, this.view)) {
      ev.addEventBinding(@BT@.Activating, "#@NAVB@", @EVD@.of("a", "back"));
      ev.addEventBinding(@BT@.Activating, "#@NAVC@", @EVD@.of("a", "close"));
      if (this.view == 23) ev.addEventBinding(@BT@.SlotClicking, "#@ARROWS@", @EVD@.of("a", "arrow"), false);
      return;
    }
    this.info = noWinText(this.view);
    this.view = 0;
  } else if (this.view > 0 && @PKG@.ProbeViews.render(b, this.view)) {
    ev.addEventBinding(@BT@.Activating, "#@NAVB@", @EVD@.of("a", "back"));
    ev.addEventBinding(@BT@.Activating, "#@NAVC@", @EVD@.of("a", "close"));
    return;
  }
  @PKG@.ProbeViews.index(b, ev, this.info);
}""")
# clicks run on the player's world thread. open:<n> = the index Open buttons (23 / 24: ProbeWin.open - a new page with its window);
# back = the probe footer (a window view: the list first, then the window closes); close = both Close buttons; arrow = P1's grid.
# A probe whose build() throws inside rebuild() (the engine sends nothing then, the client keeps the index): the page goes back to
# the index view and the admin gets one chat line - never a rebuild() from the catch (review 2026-09-29).
# back only sets the Info line when it leaves a probe page: a stale or double back (view already 0) keeps "Last opened ..." or the
# failure line instead of resetting it to lastText(0) (0.2 review); it still re-sends the index.
# close on a window view (review fix 3): the session is detached first (so the onDismiss that close() triggers schedules no 1.5 s
# check), the page closes, then the server closes the window AT ONCE - even when close() threw.
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  int tried = -1;
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("close")) {
      @PKG@.ProbeSession cs = this.sess;
      this.sess = null;
      if (cs != null && !cs.closed && cs.dismissedAt == 0L) cs.dismissedAt = System.currentTimeMillis();
      try { close(); } catch (Throwable t) { @PKG@.ProbeLog.warn("closing the probe page failed: " + t); }
      if (cs != null) @PKG@.ProbeWin.closeNow(cs, ref, st, "Close button");
      return;
    }
    if (a.equals("back")) {
      @PKG@.ProbeSession s = this.sess;
      this.sess = null;
      if (this.view > 0) {
        this.info = lastText(this.view);
        this.view = 0;
      }
      rebuild();
      if (s != null) @PKG@.ProbeWin.closeNow(s, ref, st, "Back to the list");
      return;
    }
    if (a.equals("arrow")) {
      if (this.view == 23 && this.sess != null) @PKG@.ProbeWin.arrow(this.playerRef, jsonInt(data, "SlotIndex"));
      return;
    }
    if (a.startsWith("open:")) {
      int n = -1;
      try { n = Integer.parseInt(a.substring(5)); } catch (Throwable t) { n = -1; }
      if (!@PKG@.ProbeViews.has(n)) return;
      if (@PKG@.ProbeViews.isWin(n)) {
        @WLD@ w = null;
        try { w = ((@ES@) st.getExternalData()).getWorld(); } catch (Throwable t) { w = null; }
        @PKG@.ProbeWin.open(ref, st, this.playerRef, w, n);
        return;
      }
      @PKG@.ProbeLog.info("opening probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + ") for " + this.playerRef.getUsername());
      tried = n;
      this.view = n;
      this.info = lastText(n);
      rebuild();
      @PKG@.ProbeLog.info("sent probe " + n);
    }
  } catch (Throwable ex) {
    @PKG@.ProbeLog.warn("probe page click failed" + (tried > 0 ? " (probe " + tried + ")" : "") + ": " + ex);
    if (tried > 0) {
      this.view = 0;
      this.info = "Probe " + tried + " could not be built - see the server log.";
      say(this.playerRef, "Probe " + tried + " (" + @PKG@.ProbeViews.nameOf(tried) + ") could not be built - see the server log.");
    }
  }
}""")
M(page, r"""
public void onDismiss(@REF@ ref, @ST@ store) {
  try { if (this.sess != null) @PKG@.ProbeWin.dismissed(this.sess); } catch (Throwable t) { }
}""")

# ---- ProbeCmds: what the two command classes do
cmds = mk("ProbeCmds")
M(cmds, r"""
public static void tell(@PR@ pr, String s) {
  try { pr.sendMessage(@MSG@.raw("[SkyyUiProbe] " + s)); } catch (Throwable t) { }
}""")
M(cmds, r"""
public static void open(@REF@ ref, @ST@ store, @PR@ pr, @WLD@ world, int n) {
  if (n > 0 && @PKG@.ProbeViews.isWin(n)) { @PKG@.ProbeWin.open(ref, store, pr, world, n); return; }
  @PLA@ p = null;
  try { p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) { tell(pr, "The page could not be opened (no player component)."); return; }
  String who = pr.getUsername();
  if (n > 0) @PKG@.ProbeLog.info("opening probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + ") for " + who);
  else @PKG@.ProbeLog.info("opening the index for " + who);
  try {
    p.getPageManager().openCustomPage(ref, store, new @PKG@.ProbePage(pr, n));
  } catch (Throwable t) {
    @PKG@.ProbeLog.warn("could not open " + (n > 0 ? "probe " + n : "the index") + ": " + t);
    tell(pr, (n > 0 ? "Probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + ")" : "The list page") + " could not be opened - see the server log.");
    return;
  }
  if (n > 0) @PKG@.ProbeLog.info("sent probe " + n); else @PKG@.ProbeLog.info("sent the index");
}""")
M(cmds, r"""
public static void list(@PR@ pr) {
  int[] o = @PKG@.ProbeViews.order();
  tell(pr, "" + o.length + " probe pages (kit " + @PKG@.ProbeLog.kit() + "). Open them in this order: /skyprobe <n>, or /skyprobe for the list page.");
  for (int i = 0; i < o.length; i++) {
    int n = o[i];
    String k = @PKG@.ProbeViews.keyOf(n);
    String nm = @PKG@.ProbeViews.nameOf(n);
    tell(pr, "" + n + "  " + nm + (k.equals(nm) ? "" : "  (key " + k + ")") + "  -  " + @PKG@.ProbeViews.whatOf(n));
  }
}""")
M(cmds, r"""
public static void arg(@REF@ ref, @ST@ store, @PR@ pr, @WLD@ world, String a) {
  String t = a == null ? "" : a.trim();
  if (t.equalsIgnoreCase("list")) { list(pr); return; }
  int n = @PKG@.ProbeViews.find(t);
  if (n < 0) {
    tell(pr, "No probe page '" + t + "'. Use a number 1-" + @PKG@.ProbeViews.count() + ", a name like base1, win or secgrid, or list.");
    return;
  }
  open(ref, store, pr, world, n);
}""")

EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
# ---- usage variant /skyprobe <n | name | list>   (admin: requirePermission + no permission groups, like its parent)
cmdA = mk("SkyProbeArgCmd", T["APC"])
F(cmdA, "public @RA@ pageArg;")
C(cmdA, r"""
public SkyProbeArgCmd() {
  super("(admin) /skyprobe <n or name> opens that probe page (win and secgrid: the vault window probes); /skyprobe list prints every page in chat");
  requirePermission("skyyuiprobe.admin");
  setPermissionGroups(new String[0]);
  this.pageArg = withRequiredArg("page", "probe page number, its name (base1, checkbox, ..., win, secgrid) or list", @ATY@.STRING);
}""")
M(cmdA, EXEC + r""" {
  String a = null;
  try { a = String.valueOf(ctx.get(this.pageArg)); }
  catch (Throwable t) { @PKG@.ProbeLog.warn("/skyprobe failed: " + t); @PKG@.ProbeCmds.tell(pr, "Usage: /skyprobe, /skyprobe <n or name>, /skyprobe list"); return; }
  @PKG@.ProbeCmds.arg(ref, store, pr, world, a);
}""")
# ---- /skyprobe (alias /uiprobe): the index page
cmd = mk("SkyProbeCmd", T["APC"])
C(cmd, r"""
public SkyProbeCmd() {
  super("skyprobe", "(admin) Probe pages: /skyprobe opens the list page, /skyprobe <n or name> opens one page, /skyprobe list prints them");
  requirePermission("skyyuiprobe.admin");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "uiprobe" });
  addUsageVariant(new @PKG@.SkyProbeArgCmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.ProbeCmds.open(ref, store, pr, world, 0);
}""")

# ---- plugin
pl = mk("SkyyUiProbePlugin", T["JP"])
C(pl, "public SkyyUiProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.ProbeLog.LOG = getLogger();
  getCommandRegistry().registerCommand(new @PKG@.SkyProbeCmd());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyUiProbe] @VERSION@ ready - /skyprobe (admin): " + @PKG@.ProbeViews.count() + " probe pages (kit " + @PKG@.ProbeLog.kit() + ")");
}""")
M(pl, r"""
protected void shutdown() {
  try { @PKG@.ProbeWin.shutdown(); } catch (Throwable t) { }
  super.shutdown();
}""")

CLASSES = [log, views, ses, box, win, chg, ctk, ltk, stk, net, page, pw, cmds, cmdA, cmd, pl]
for c in CLASSES:
    c.writeFile(OUT)
print("classes written:", len(CLASSES))

jar = os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)
man = B.manifest("SkyyUiProbe", VERSION, "SkyWynn dev / test tool: /skyprobe (admin only) opens the vanilla-look kit's probe pages and the vault window probes (win, secgrid) one by one, so Skyy can see which UI properties and window tricks work before a build uses them. No data, no config, zero dependencies.", PKG + ".SkyyUiProbePlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
with zipfile.ZipFile(jar) as _jz:
    _bad = [n for n in _jz.namelist() if n.lower().endswith(".ui")]
    if _bad:
        raise SystemExit("SkyyUiProbe jar must not ship .ui files (inline pages only): %s" % _bad)
