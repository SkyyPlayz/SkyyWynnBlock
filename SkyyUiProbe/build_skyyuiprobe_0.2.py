"""SkyyUiProbe 0.2 - build script (javassist via jpype). A small DEV / TEST mod: it opens the vanilla-look kit's probe pages in game.
Run:   python SkyyUiProbe/build_skyyuiprobe_0.2.py            -> SkyyUiProbe/SkyyUiProbe-0.2.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
       --dump <file.json> also writes what every view sends (appends + b.set lines + extra Java lines, the index bindings) for the
       harness; nothing else changes. --dump-only <file.json> writes it and stops before the Java (no JVM, no class / jar written).
Check: python SkyyUiProbe/test_skyyuiprobe_0.2.py   (bare JVM, -Xverify:all; re-run it after every build and whenever the kit id
       changes - it refuses a jar built with another kit).

WHY 0.2 (made by copy + edit of build_skyyuiprobe_0.1.py): the kit tools/skyyui.py is 1.4 now. It keeps probe pages 1-18 (same
numbers, names and content) and adds 19 base4 (the kit 1.4 builders), 20 button-text, 21 flex-rows, 22 layout-right. 0.1 no
longer builds on kit 1.4 (its one-column index needs 1067 px, the body has 928), and Skyy has to SEE pages 19-22 before the 12
held restyles ship. Same purpose as 0.1 (Skyy 2026-09-28: every UI must look and feel vanilla): one property the client cannot
parse in an inline page disconnects the client the moment the page opens, so every kit look is proven page by page first. When a
page works, its key goes into skyyui.PROBED (tools/skyyui.py; "base" once base1, base2 and base3 all work; "base4" for page 19).

COMMANDS (unchanged from 0.1; ADMIN ONLY: requirePermission("skyyuiprobe.admin") AND setPermissionGroups(new String[0]) on the
command and its usage variant - ops pass through "*", plain hytale:Adventurer players are refused; lint rule perm_group_leaks):
  /skyprobe  (alias /uiprobe)     -> the INDEX page (every probe page: number, name, what it proves, an Open button)
  /skyprobe <n>  or <name>        -> probe page n directly (1-22, or its stable name: base1, checkbox, ..., base3, base4, flex-rows)
  /skyprobe list                  -> the same list in chat (number, name, key, one-line purpose), in the order to open them
Any other token count gets the engine's usage error.

PAGES (inline only, HANDOFF section 2): ONE CustomUIPage (ProbePage) with a view number, switched with rebuild() after a click (the
SkyyCollections CollPage pattern, seen in game) - never closed right before another opens, never updated on a timer.
  - INDEX (view 0): built ONLY from markup already proven in game - the OLD flat style of the live SkyyBank 0.1.3 page (as in
    0.1): plain Group roots / rows with a Background colour, Padding, LayoutMode Top / Left, the 3 px stripe, Labels, spacer Groups
    (SkyyCollections sp()), TextButtons with flat colour TextButtonStyle triples (the BankPage style() output, character for
    character). No textures, no sounds, no kit trial features, no FlexWeight / Wrap / WrapMaxLines / LetterSpacing / LayoutMode
    Center / Right / Full, no Anchor margins (the build asserts each, plus SUI.assert_proven on the whole index), so the index itself
    cannot be what fails. 22 entries in TWO columns of 11 (a LayoutMode Left group holding two fixed-width LayoutMode Top
    columns), in the order to open them: SUI.PROBE_OPEN_FIRST (base1, base2, base3, then base4 = pages 1, 2, 18, 19; green Open
    buttons), then the rest by number (blue). Each entry: number, name, Open on its first line, the page's Probe.summary on the
    second (the kit cuts base2's PROBE_SUMMARY line at 95 characters with "..."; the row has room for the kit's whole line, so the
    index and /skyprobe list show that one). The line "Open base1, base2, base3 first, then base4" heads the page. Every index
    text is measured with SUI.text_width against its label (FIT_MARGIN px kept free): the title, both top lines, both column
    heads, every name and summary, the kit line, and every runtime Info text (lastText of each page, the failure line of each
    page). The FLAT colours are that old page's own values (module constant FLAT, listed in UI_DATA_COLORS for the lint colour
    rule: they are the old proven look on purpose, not a restyle).
  - PROBE n (views 1-22): the kit's page exactly as SUI.probe_page(name) builds it (its numbered "what to see" list included; the
    kit buttons on it are not bound: they only play their sounds) plus ONE flat footer: [Back to the list] (rebuild to the index)
    and [Close], placed by the kit's public footer hook Probe.with_footer(footer, 56, foot_w=426, slack=4) (0.1's private
    height helpers / regex parsing are gone): at the end of the page body with the root 56 (+ up to 4) px taller while the page
    stays <= 980 px, else at the bottom of a fixed-height LayoutMode Top column with room (page 18). The footer uses the same proven
    flat markup as the index, so Back / Close keep working even if a kit look is wrong. The build asserts the page Java equals
    the kit's Java except the root height line and the footer lines.
    base2 (probe 2): its body is ONE FlexWeight: 1 column group + the footer. SUI.used_height counts a flex child as 0, so the
    "px slack" the build prints for it means nothing (the build says so), and base2's own layout - the footer position included
    - rests on FlexWeight, which the client has not been seen to honour yet: if base2 shows only the footer (no columns),
    FlexWeight failed.
  - Control events (checkbox ValueChanged, dropdown, number / search field) are NOT echoed: the kit has no binding helper for them,
    no deployed Skyy page binds ValueChanged yet, and a binding on a not-yet-proven element would make a disconnect on that page
    ambiguous (element or binding?). The element pages stay binding-free, exactly as the kit builds them. So pages 3, 4, 10 and 11
    (checkbox, number-field, dropdown, search-field) prove RENDERING only, not events: a restyle that needs ValueChanged bindings
    needs a separate event probe first.
LOGS (server log, INFO): "[SkyyUiProbe] opening probe <n> (<name>) for <player>" right before the open call (openCustomPage or
rebuild) and "[SkyyUiProbe] sent probe <n>" after it returned. A client disconnect right after "sent probe n" names the failing page
from the server log alone. The index logs "opening the index for <player>" / "sent the index" the same way.
A probe page whose own Java throws while it is built (server side, e.g. an item id the asset store lacks): /skyprobe n says so in
chat; a click on the index logs a WARNING "probe page click failed (probe n): ...", puts the page back on the index view (the client
keeps showing the index - nothing was sent) and says "Probe n (name) could not be built - see the server log." in chat.
After Back, the index line under the columns says which page was opened last and which one comes next in the list. A stale or
double Back (the page is already on the index) re-sends the index and keeps that line (0.2 review: it used to reset it to
"Nothing opened yet").
No data files, no config kit rows, no bridge keys, no player switches, no event systems. Ready line:
  "[SkyyUiProbe] 0.2 ready - /skyprobe (admin): 22 probe pages (kit skyyui 1.4 <blob12>)".
BUILD CHECKS: SUI.verify() (every vanilla value against Assets.zip, read-only), Probe.with_footer (check_page with every b.set
target, the height proofs, assert_page_size) on every probe page, SUI.check_page + SUI.assert_proven + the flat-only asserts +
SUI.used_height / used_width budgets + SUI.text_width fits for every index text, item_grid_java_is_safe on all the Java, no .ui
file in the jar. UNVERIFIED (needs the game): every probe page itself (that is the point of this mod).
CHECKED in a bare JVM by the kept harness SkyyUiProbe/test_skyyuiprobe_0.2.py (see its header).
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

VERSION = "0.2"
HERE = os.path.dirname(os.path.abspath(__file__))
SUI.verify()                       # every vanilla value the kit emits, proven against Assets.zip (read-only) - never caught
KIT_ID = SUI.kit_id()
assert SUI.KIT_VERSION == "1.4", "SkyyUiProbe 0.2 is made for kit 1.4 (Probe.summary, Probe.with_footer, PROBE_OPEN_FIRST)"
PREFIX = "SkyyPb"                  # the kit's default probe prefix; the index / footer ids (SkyyPbIx..., SkyyPbNav...) share it
PAGES = SUI.probe_pages(PREFIX)    # number order
BY_N = dict((p.n, p) for p in PAGES)
BY_NAME = dict((p.name, p) for p in PAGES)
assert sorted(BY_N) == list(range(1, len(PAGES) + 1)) and len(BY_NAME) == len(PAGES), "probe numbers 1..n, names unique"
for p in PAGES:
    assert re.fullmatch(r"[a-z0-9-]+", p.name), "probe name %r (a command argument): a-z 0-9 -" % p.name

# the order to open them: SUI.PROBE_OPEN_FIRST (base1, base2, base3, base4), then the rest in number order
FIRST = list(SUI.PROBE_OPEN_FIRST)
assert all(x in BY_NAME for x in FIRST), "PROBE_OPEN_FIRST names a page the kit does not build: %s" % FIRST
ORDER = [p.n for p in sorted(PAGES, key=lambda p: (0, FIRST.index(p.name)) if p.name in FIRST else (1, p.n))]
assert sorted(ORDER) == sorted(BY_N) and [BY_N[n].name for n in ORDER[:len(FIRST)]] == FIRST

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
IX_W, IX_H, IX_PADH, IX_PADV = 1600, 960, 20, 14
IX_IN_W = IX_W - 2 * IX_PADH                    # 1560
COL_GAP = 16
COL_W = (IX_IN_W - COL_GAP) // 2                # 772: two columns of entries
PER_COL = (len(ORDER) + 1) // 2                 # 11 + 11
ENT_H, ENT_GAP, ENT_TOP = 60, 4, 2              # entry: 2 px, line one 32, line two 24, 2 px
L1_H, L2_H = 32, 24
EDGE, NUM_W, GAP_W, OPEN_W = 10, 46, 8, 130
NAME_W = COL_W - EDGE - NUM_W - GAP_W - OPEN_W - EDGE    # line one: 10 | number | name | 8 | Open | 10
WHAT_X = EDGE + NUM_W                                    # line two: the summary starts under the name
WHAT_W = COL_W - WHAT_X - GAP_W
WHAT_FS, NAME_FS, NUM_FS = 15, 18, 20
FIT_MARGIN = 8                                   # px kept free after the widest text (the client's glyph advances vary a little)


def summary(pg):
    """The one-line purpose of a probe page: the kit's Probe.summary. Kit 1.4 cuts a PROBE_SUMMARY line longer than 95 characters
    to 92 + "..." (base2); when the kit's whole line still fits the index row, that whole line is shown instead."""
    s = pg.summary
    full = SUI.PROBE_SUMMARY.get(pg.name, "")
    if s.endswith("...") and full.startswith(s[:-3]) and SUI.text_width(full, WHAT_FS) <= WHAT_W - FIT_MARGIN:
        return full
    return s


WHAT = dict((p.n, summary(p)) for p in PAGES)
for p in PAGES:
    if WHAT[p.n] != p.summary:
        print("note: probe %d (%s): the index shows the kit's whole PROBE_SUMMARY line (Probe.summary is cut at 95 characters)"
              % (p.n, p.name))


# ================= the probe pages + their flat footer (the kit's public footer hook) =================
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

# ================= the index (flat, proven markup only) =================
FIRST_LINE = "Open %s first, then %s - then the other pages, left column first, top to bottom. Back returns here, Esc or Close " \
             "leaves." % (", ".join(FIRST[:-1]), FIRST[-1])
FIRST_TXT = "Nothing opened yet - start with %s, then %s (probes %s)." % (
    ", ".join(FIRST[:-1]), FIRST[-1], ", ".join(str(BY_NAME[x].n) for x in FIRST))
TITLE = "SkyyUiProbe - kit probe pages"
SUB2 = "A disconnect right after you click Open means that page failed - note its number (the server log names it too)."
HEADS = ("Start here - the base pages first (green Open)", "Then continue here, top to bottom")
KIT_LINE = "Kit %s  |  %d pages  |  chat: /skyprobe list, /skyprobe number or name" % (KIT_ID, len(PAGES))
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
            rows.append(entry(ap, col, n, "g" if BY_N[n].name in FIRST else "b"))
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
assert len(IX_ROWS) == len(PAGES) and PER_COL == 11 and len(ORDER) - PER_COL == 11, "22 entries in two columns of 11"
# every text fits its label (the client's font tables, SUI.text_width)
for n in ORDER:
    SUI.fit([SUI.text_width(WHAT[n], WHAT_FS), FIT_MARGIN], WHAT_W, "probe %d summary line" % n)
    SUI.fit([SUI.text_width(BY_N[n].name, NAME_FS, bold=True), FIT_MARGIN], NAME_W, "probe %d name" % n)
IX_TEXTS = [(TITLE, TITLE_FS, True, IX_IN_W), (FIRST_LINE, SUB_FS, False, IX_IN_W), (SUB2, SUB_FS, False, IX_IN_W),
            (HEADS[0], HEAD_FS, True, COL_W), (HEADS[1], HEAD_FS, True, COL_W), (KIT_LINE, KIT_FS, False, KIT_W),
            (FIRST_TXT, INFO_FS, True, IX_IN_W)]
IX_TEXTS += [(last_text(n), INFO_FS, True, IX_IN_W) for n in ORDER] + [(fail_text(n), INFO_FS, True, IX_IN_W) for n in ORDER]
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
for _t in [FIRST_TXT] + [last_text(n) for n in ORDER] + [fail_text(n) for n in ORDER]:
    assert not re.search(r"[<>]", _t), "runtime Info text (b.set) with < or >: %r" % _t
IX_JAVA = IXA.java("b") + "\n" + SUI.java_set(*INFO_SET)
IX_BINDS = [("#" + IX + "Open" + str(n), "open:" + str(n)) for n in ORDER] + [("#" + IX + "Close", "close")]
IX_BIND = ["ev.addEventBinding(@BT@.Activating, %s, @EVD@.of(\"a\", %s));" % (SUI.java_lit(sel), SUI.java_lit(act))
           for sel, act in IX_BINDS]
print("index: %d appends, %d b.set lines, %d / %d px high (%d free), two columns %s | %s" % (
    len(IXA), len(IXA.sets) + 1, IX_USED, IX_H - 2 * IX_PADV, IX_FREE, ORDER[:PER_COL], ORDER[PER_COL:]))

if DUMP:
    out = {"kit": KIT_ID, "order": ORDER, "names": dict((str(p.n), p.name) for p in PAGES),
           "keys": dict((str(p.n), p.key) for p in PAGES), "whats": dict((str(n), WHAT[n]) for n in ORDER),
           "open_first": FIRST, "first_txt": FIRST_TXT, "per_col": PER_COL,
           "what_w": WHAT_W, "what_fs": WHAT_FS, "name_w": NAME_W, "name_fs": NAME_FS, "fit_margin": FIT_MARGIN,
           "info_w": IX_IN_W, "info_fs": INFO_FS, "last_txts": dict((str(n), last_text(n)) for n in ORDER),
           "foot": ["#" + NAV_BACK, "#" + NAV_CLOSE],
           "index": {"appends": [[p, SUI.render(m)] for p, m in IXA], "sets": [[i, pr, v] for i, pr, v in IXA.sets],
                     "info": ["#" + IX + "Info", "Text"], "info_set": list(INFO_SET), "binds": [list(x) for x in IX_BINDS],
                     "w": IX_W, "h": IX_H}}
    for n, (ap, sets, _java, how, h, extra) in VIEWS.items():
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
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
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
    "NAVB": NAV_BACK, "NAVC": NAV_CLOSE,
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
for c, m in ((T["AC"], "requirePermission"), (T["AC"], "setPermissionGroups"), (T["AC"], "addAliases"), (T["AC"], "addUsageVariant"),
             (T["AC"], "withRequiredArg"), (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["MSG"], "raw"), (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"),
             (T["BT"], "Activating"), (T["PAGE"], "rebuild"), (T["PAGE"], "handleDataEvent"), (T["PAGE"], "close"), (T["PAGE"], "build"),
             (T["PGM"], "openCustomPage"), (T["PLA"], "getPageManager"), (T["PLA"], "getComponentType"), (T["LIFE"], "CanDismiss"),
             (PB, "getCommandRegistry"), (PB, "getLogger"), (PB, "shutdown"), (T["VAL"], "ref")):
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


# ---- ProbeLog: the server log lines
log = mk("ProbeLog")
F(log, "public static @LOG@ LOG;")
M(log, 'public static String kit() { return %s; }' % jl(KIT_ID))
M(log, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyUiProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyUiProbe] " + msg); } catch (Throwable t) { }
}""")

# ---- ProbeViews: every view's statements (one static method per probe page) + the page list
views = mk("ProbeViews")
MAXN = max(BY_N)
NAMES = [""] * (MAXN + 1)
KEYS = [""] * (MAXN + 1)
WHATS = [""] * (MAXN + 1)
for p in PAGES:
    NAMES[p.n], KEYS[p.n], WHATS[p.n] = p.name, p.key, WHAT[p.n]
M(views, "public static int count() { return %d; }" % len(PAGES))
M(views, "public static int[] order() { return new int[] { %s }; }" % ", ".join(str(n) for n in ORDER))
M(views, "public static String[] names() { return new String[] { %s }; }" % ", ".join(jl(x) for x in NAMES))
M(views, "public static String[] keys() { return new String[] { %s }; }" % ", ".join(jl(x) for x in KEYS))
M(views, "public static String[] whats() { return new String[] { %s }; }" % ", ".join(jl(x) for x in WHATS))
M(views, r"""
public static boolean has(int n) {
  String[] a = names();
  return n > 0 && n < a.length && a[n].length() > 0;
}""")
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
# a page number (1-22) or a stable name (base1, checkbox, number-field, ...); -1 = none. Locale.ROOT: under a Turkish / Azeri
# default locale toLowerCase() turns "TILE" into a dotless-i "tile" that matches nothing.
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
for n in sorted(VIEWS):
    MR(views, "public static void p%d(%s b) {\n%s\n}" % (n, T["UCB"], VIEWS[n][2]))
M(views, "public static boolean render(@UCB@ b, int n) {\n%s\n  return false;\n}" % "\n".join(
    "  if (n == %d) { p%d(b); return true; }" % (n, n) for n in sorted(VIEWS)))
MR(views, "public static void index(%s b, %s ev, String info) {\n%s\n%s\n}" % (T["UCB"], T["UEB"], IX_JAVA, jv("\n".join(IX_BIND))))

# ---- ProbePage: the one inline page (view 0 = index, n = probe page n), switched by rebuild() after a click
page = mk("ProbePage", T["PAGE"])
F(page, "public int view;")
F(page, "public String info;")
M(page, r"""
public static String lastText(int n) {
  if (!@PKG@.ProbeViews.has(n)) return %s;
  int nx = @PKG@.ProbeViews.nextOf(n);
  return "Last opened: probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + "). Did it look right? "
    + (nx > 0 ? "Next: probe " + nx + " (" + @PKG@.ProbeViews.nameOf(nx) + ")." : "That was the last one.");
}""" % jl(FIRST_TXT))
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
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  if (this.view > 0 && @PKG@.ProbeViews.render(b, this.view)) {
    ev.addEventBinding(@BT@.Activating, "#@NAVB@", @EVD@.of("a", "back"));
    ev.addEventBinding(@BT@.Activating, "#@NAVC@", @EVD@.of("a", "close"));
    return;
  }
  @PKG@.ProbeViews.index(b, ev, this.info);
}""")
# one chat line to the admin (ProbeCmds.tell is made after this class, so the page has its own copy)
M(page, r"""
public static void say(@PR@ pr, String s) {
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[SkyyUiProbe] " + s)); } catch (Throwable t) { }
}""")
# clicks run on the player's world thread. open:<n> = the index Open buttons; back = the probe footer; close = both Close buttons.
# A probe whose build() throws inside rebuild() (the engine sends nothing then, the client keeps the index): the page goes back to
# the index view and the admin gets one chat line - never a rebuild() from the catch (review 2026-09-29).
# back only sets the Info line when it leaves a probe page: a stale or double back (view already 0) keeps "Last opened ..." or the
# failure line instead of resetting it to lastText(0) (0.2 review); it still re-sends the index.
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  int tried = -1;
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("close")) { close(); return; }
    if (a.equals("back")) {
      if (this.view > 0) {
        this.info = lastText(this.view);
        this.view = 0;
      }
      rebuild();
      return;
    }
    if (a.startsWith("open:")) {
      int n = -1;
      try { n = Integer.parseInt(a.substring(5)); } catch (Throwable t) { n = -1; }
      if (!@PKG@.ProbeViews.has(n)) return;
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

# ---- ProbeCmds: what the two command classes do
cmds = mk("ProbeCmds")
M(cmds, r"""
public static void tell(@PR@ pr, String s) {
  try { pr.sendMessage(@MSG@.raw("[SkyyUiProbe] " + s)); } catch (Throwable t) { }
}""")
M(cmds, r"""
public static void open(@REF@ ref, @ST@ store, @PR@ pr, int n) {
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
public static void arg(@REF@ ref, @ST@ store, @PR@ pr, String a) {
  String t = a == null ? "" : a.trim();
  if (t.equalsIgnoreCase("list")) { list(pr); return; }
  int n = @PKG@.ProbeViews.find(t);
  if (n < 0) {
    tell(pr, "No probe page '" + t + "'. Use a number 1-" + @PKG@.ProbeViews.count() + ", a name like base1 or checkbox, or list.");
    return;
  }
  open(ref, store, pr, n);
}""")

EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
# ---- usage variant /skyprobe <n | name | list>   (admin: requirePermission + no permission groups, like its parent)
cmdA = mk("SkyProbeArgCmd", T["APC"])
F(cmdA, "public @RA@ pageArg;")
C(cmdA, r"""
public SkyProbeArgCmd() {
  super("(admin) /skyprobe <n or name> opens that kit probe page; /skyprobe list prints every page in chat");
  requirePermission("skyyuiprobe.admin");
  setPermissionGroups(new String[0]);
  this.pageArg = withRequiredArg("page", "probe page number, its name (base1, checkbox, ...) or list", @ATY@.STRING);
}""")
M(cmdA, EXEC + r""" {
  String a = null;
  try { a = String.valueOf(ctx.get(this.pageArg)); }
  catch (Throwable t) { @PKG@.ProbeLog.warn("/skyprobe failed: " + t); @PKG@.ProbeCmds.tell(pr, "Usage: /skyprobe, /skyprobe <n or name>, /skyprobe list"); return; }
  @PKG@.ProbeCmds.arg(ref, store, pr, a);
}""")
# ---- /skyprobe (alias /uiprobe): the index page
cmd = mk("SkyProbeCmd", T["APC"])
C(cmd, r"""
public SkyProbeCmd() {
  super("skyprobe", "(admin) Kit probe pages: /skyprobe opens the list page, /skyprobe <n or name> opens one page, /skyprobe list prints them");
  requirePermission("skyyuiprobe.admin");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "uiprobe" });
  addUsageVariant(new @PKG@.SkyProbeArgCmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.ProbeCmds.open(ref, store, pr, 0);
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
  super.shutdown();
}""")

ALL = [log, views, page, cmds, cmdA, cmd, pl]
for c in ALL:
    c.writeFile(OUT)
print("classes written:", len(ALL))

jar = os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)
man = B.manifest("SkyyUiProbe", VERSION, "SkyWynn dev / test tool: /skyprobe (admin only) opens the vanilla-look kit's probe pages one by one, so Skyy can see which vanilla UI properties work in inline pages before the restyle uses them. No data, no config, zero dependencies.", PKG + ".SkyyUiProbePlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
with zipfile.ZipFile(jar) as _jz:
    _bad = [n for n in _jz.namelist() if n.lower().endswith(".ui")]
    if _bad:
        raise SystemExit("SkyyUiProbe jar must not ship .ui files (inline pages only): %s" % _bad)
