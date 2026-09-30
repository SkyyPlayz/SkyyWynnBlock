"""SkyyUiProbe 0.1 - build script (javassist via jpype). A small DEV / TEST mod: it opens the vanilla-look kit's probe pages in game.
Run:   python SkyyUiProbe/build_skyyuiprobe_0.1.py            -> SkyyUiProbe/SkyyUiProbe-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
       --dump <file.json> also writes what every view sends (appends + b.set lines + extra Java lines, the index bindings) for the
       harness; nothing else changes. --dump-only <file.json> writes it and stops before the Java (no JVM, no class / jar written).
Check: python SkyyUiProbe/test_skyyuiprobe_0.1.py   (bare JVM, -Xverify:all; re-run it after every build and whenever the kit id
       changes - it refuses a jar built with another kit).

WHY (Skyy 2026-09-28: every UI must look and feel vanilla): no page built from the kit's vanilla textures (tools/skyyui.py, kit 1.3)
has been SEEN on Skyy's client yet, and one property the client cannot parse in an inline page disconnects the client the moment the
page opens. The kit ships one probe page per UNVERIFIED feature plus three "base" pages (SUI.probe_pages(); research/
Vanilla-UI-Style-Guide.md section 0). This mod lets Skyy open them one by one, so the restyle only uses what is proven. When a page
works, its key goes into skyyui.PROBED (tools/skyyui.py; "base" once base1, base2 and base3 all work).

COMMANDS (ADMIN ONLY: requirePermission("skyyuiprobe.admin") AND setPermissionGroups(new String[0]) on the command and its usage
variant - ops pass through "*", plain hytale:Adventurer players are refused; lint rule perm_group_leaks):
  /skyprobe  (alias /uiprobe)     -> the INDEX page (every probe page: number, name, what it proves, an Open button)
  /skyprobe <n>  or <name>        -> probe page n directly (1-18, or its stable name: base1, checkbox, number-field, ..., base3)
  /skyprobe list                  -> the same list in chat (number, name, key, one-line purpose)
Any other token count gets the engine's usage error.

PAGES (inline only, HANDOFF section 2): ONE CustomUIPage (ProbePage) with a view number, switched with rebuild() after a click (the
SkyyCollections CollPage pattern, seen in game) - never closed right before another opens, never updated on a timer.
  - INDEX (view 0): built ONLY from markup already proven in game - the OLD flat style of the live SkyyBank 0.1.3 page: a plain
    Group root with a Background colour, Padding and LayoutMode Top, the 3 px stripe, Labels, spacer Groups (SkyyCollections sp()),
    TextButtons with flat colour TextButtonStyle triples (the BankPage style() output, character for character). No textures, no
    sounds, no kit trial features, no Anchor margins, so the index itself cannot be what fails. Rows are listed in the order to open
    them: the base pages first (1, 2, 18), then 3-17. The FLAT colours are that page's own values (module constant FLAT, listed in
    UI_DATA_COLORS for the lint colour rule: they are the old proven look on purpose, not a restyle).
  - PROBE n (views 1-18): the kit's page exactly as SUI.probe_pages() builds it (its numbered "what to see" list included; the kit
    buttons on it are not bound: they only play their sounds) plus ONE flat footer: [Back to the list] (rebuild to the index) and
    [Close]. The footer uses the same proven flat markup as the index, so Back / Close keep working even if a kit look is wrong.
    Where the footer goes (proven at build time from the markup heights): at the bottom of the page body, the page root 56 px
    higher, plus up to FOOT_SLACK (4) px more when the body had less than 4 px free (base1: its 788 px columns fill the body, so
    860 -> 920, footer + 4 px slack) - every page whose new height stays <= 980, all but page 18; otherwise at the bottom of a
    LayoutMode Top column with a fixed height and >= 56 + 4 px free (page 18: its 900 px main column, 96 px free). Nothing else of
    the kit markup is changed: the build asserts the page Java equals the kit's Java except the root height line and the footer
    lines. The height proofs read the markup with the kit's PUBLIC render() + a local quoted-text blanker, and assert the kit's
    root markup form (a kit change there fails the build loudly, it never ships a wrong page).
LOGS (server log, INFO): "[SkyyUiProbe] opening probe <n> (<name>) for <player>" right before the open call (openCustomPage or
rebuild) and "[SkyyUiProbe] sent probe <n>" after it returned. A client disconnect right after "sent probe n" names the failing page
from the server log alone. The index logs "opening the index for <player>" / "sent the index" the same way.
A probe page whose own Java throws while it is built (server side, e.g. an item id the asset store lacks): /skyprobe n says so in
chat; a click on the index logs a WARNING "probe page click failed (probe n): ...", puts the page back on the index view (the client
keeps showing the index - nothing was sent) and says "Probe n (name) could not be built - see the server log." in chat.
No data files, no config kit rows, no bridge keys, no player switches, no event systems. Ready line:
  "[SkyyUiProbe] 0.1 ready - /skyprobe (admin): 18 probe pages (kit skyyui 1.3 <blob12>)".
BUILD CHECKS: SUI.verify() (every vanilla value against Assets.zip, read-only), SUI.check_page on every probe page (with its footer)
and on the index, SUI.assert_page_size, the footer height proofs, the index height budget, item_grid_java_is_safe on all the Java,
no .ui file in the jar. UNVERIFIED (needs the game): every probe page itself (that is the point of this mod).
CHECKED in a bare JVM by the kept harness SkyyUiProbe/test_skyyuiprobe_0.1.py (2026-09-29 fix round: 320 checks, 0 fail; the
pre-fix jar fails 16 of them - the locale, click-failure, index-text and base1-slack fixes): all 7 classes
load + initialise under -Xverify:all; every view rendered through the REAL UICommandBuilder / UIEventBuilder sends exactly the
appends + b.set lines + extra Java lines this build dumps (probe 18 up to its grid fill: new ItemStack(id, qty) needs the item asset
store, which a bare JVM does not load - the four item ids are in Assets.zip and SkyyMenu's launcher grid runs the same pattern in
game); the index binds its 18 Open buttons (open:<n>) + Close; ProbePage.build sends the probe view + binds only Back / Close for
views 1-18 and falls back to the index for 0 / unknown; clicks through handleDataEvent (engine-like rebuild: build, exceptions pass
through): open / back / close, malformed input never changes state, a probe whose build throws (18 in a bare JVM) puts the page back
on the index view + one chat line; find() incl. upper-case names under a Turkish default locale; /skyprobe and its variant hold
skyyuiprobe.admin with empty permission-group lists, no group gets the node, the engine's PermissionsModule + AbstractCommand refuse
a plain Adventurer and skyy.* / hytale.* / hytale.command.* holders and pass an op ("*") and a node holder; control: a command listing
hytale:Adventurer is granted to that same plain player (so the check can see a leak).
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

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
SUI.verify()                       # every vanilla value the kit emits, proven against Assets.zip (read-only) - never caught
KIT_ID = SUI.kit_id()
PREFIX = "SkyyPb"                  # the kit's default probe prefix; the index / footer ids (SkyyPbIx..., SkyyPbNav...) share it
PAGES = SUI.probe_pages(PREFIX)
BY_N = dict((p.n, p) for p in PAGES)

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


def f_text(ap, parent, ident, text, h, fs, col, bold=False, center=False, w=None):
    """A flat label with any text: proven text inline, anything else as an empty label + a b.set line (the #SkyyBCapMid pattern)."""
    if SUI.TEXT_OK.fullmatch(text) and not SUI.has_j(text):
        ap.append((parent, f_label(ident, text, h, fs, col, bold, center, w)))
    else:
        ap.append((parent, f_label(ident, "", h, fs, col, bold, center, w)))
        ap.sets.append((ident, "Text", text))


# ================= what each page proves (one line; the index, /skyprobe list) =================
PURPOSE = {
    "base1": "Window frame, gold ornaments, close X, all button kinds + sounds, tabs, big text, separators",
    "base2": "Plain window, list well + scrollbar, list rows, property box, cards, 3 text field looks, option / nav rows",
    "base3": "Kit 1.3 builders: pager, item grid, icon cells, confirm views, punctuated text, big number",
    "checkbox": "CheckBox element inline (tick / untick sound)",
    "number-field": "NumberField element inline (digits only)",
    "tooltip": "Hover tooltips on a button and a label; Esc with a tooltip open",
    "progress-element": "Vanilla ProgressBar element (its Value set from the server)",
    "memories-bar": "Textured Memories progress bar",
    "quality-frame": "Item quality slot frames + a quality tooltip frame (../ItemQualities paths)",
    "itemslot": "ItemSlot element with its quality background",
    "dropdown": "DropdownBox, plain and with a search box",
    "search-field": "Search box with the magnifier and the clear x",
    "spinner": "Loading spinner (animated sprite)",
    "tile": "Memories tile textures in their 4 states",
    "text-mask": "Gradient text mask on a label and on a nav button",
    "slot-background": "Slot backgrounds in an item grid",
    "disabled-prop": "Disabled: true on a button (grey look, no click)",
    "value-ref": "A button style set by reference to the vanilla style",
}


def purpose(pg):
    if pg.name in PURPOSE:
        return PURPOSE[pg.name]
    t = SUI.UNVERIFIED.get(pg.key, pg.look[-1] if pg.look else pg.name)     # a page added to the kit later: its own description
    print("note: probe %d (%s) has no short purpose line here - using the kit's description" % (pg.n, pg.name))
    return t if len(t) <= 95 else t[:92] + "..."


# the order to open them: the base pages (PROBE_BASE) first, then the rest in number order
ORDER = [p.n for p in sorted(PAGES, key=lambda p: (0, SUI.PROBE_BASE.index(p.name)) if p.name in SUI.PROBE_BASE else (1, p.n))]
assert sorted(ORDER) == sorted(BY_N) and len(set(p.name for p in PAGES)) == len(PAGES), "probe numbers / names must be unique"
for p in PAGES:
    assert re.fullmatch(r"[a-z0-9-]+", p.name), "probe name %r (a command argument): a-z 0-9 -" % p.name


# ================= layout proof helpers (heights read from the markup the page really sends) =================
# Only PUBLIC kit names are used here (SUI.render, SUI.fit, ...). The kit has no public "height of a child" helper yet (review
# kitGaps: SUI.used_height / a probe footer hook), so the few lines below read Anchor heights themselves and raise when they cannot.
def _blank_quoted(s):
    """s with every "..." body blanked (text never counts as syntax); raises on an unterminated quote."""
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c == '"':
            j = i + 1
            while j < n and s[j] != '"':
                j += 2 if s[j] == "\\" else 1
            if j >= n:
                raise ValueError("unterminated quote in markup: %s" % s[i:i + 60])
            out.append('""')
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


assert _blank_quoted('Label #A { Text: "a { b"; Style: (X: "q\\"r"); }') == 'Label #A { Text: ""; Style: (X: ""); }'


def _depth1(mk):
    """The outer element's own properties (brace depth 1) of one markup, quoted text blanked."""
    s = _blank_quoted(SUI.render(mk if isinstance(mk, str) else mk.variants()[0]))
    out, depth = [], 0
    for ch in s:
        if ch == "{":
            depth += 1
            if depth == 1:
                continue
        elif ch == "}":
            depth -= 1
        if depth == 1:
            out.append(ch)
    return "".join(out)


def _anchor(mk):
    d = _depth1(mk)
    m = re.search(r"Anchor:\s*\(([^)]*)\)", d)
    vals = {}
    if m:
        for part in m.group(1).split(","):
            k, _s, v = part.partition(":")
            vals[k.strip()] = v.strip()
    return vals, d


def outer_h(mk):
    """(height incl. Top / Bottom margins, is_flex) of a child in a LayoutMode Top parent; raises when it cannot be proven."""
    a, d = _anchor(mk)
    flex = re.search(r"\bFlexWeight:", d) is not None
    if "Height" not in a:
        if flex:
            return 0, True
        raise ValueError("cannot prove the height of: %s" % SUI.render(mk if isinstance(mk, str) else mk.variants()[0])[:120])
    return int(a["Height"]) + int(a.get("Top", 0)) + int(a.get("Bottom", 0)), flex


def ident_of(mk):
    m = re.match(r"\s*[A-Z][A-Za-z]*\s+#([A-Za-z0-9]+)", SUI.render(mk if isinstance(mk, str) else mk.variants()[0]))
    return m.group(1) if m else None


def used_in(ap, container):
    return sum(outer_h(mk)[0] for par, mk in ap if par is not None and SUI.render(par).lstrip("#") == container)


# ================= the probe pages + their flat footer =================
FOOT_H = 56                      # BankPage bottom row: Group Height 56, LayoutMode Left, Padding Top 8; 46 px buttons
FOOT_SLACK = 4                   # px kept free under the footer's container end (review: base1 had 0 px slack; a clipped footer
                                 # would still leave Esc, but Back / Close must stay whole)
FOOT_W = 240 + 16 + 170
NAV, NAV_BACK, NAV_CLOSE = PREFIX + "Nav", PREFIX + "NavBack", PREFIX + "NavClose"


def footer(container):
    return [(container, "Group #%s { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: 8); }" % (NAV, FOOT_H)),
            (NAV, f_button(NAV_BACK, "Back to the list", 240, 46, "b")),
            (NAV, f_spacer(16, 46)),
            (NAV, f_button(NAV_CLOSE, "Close", 170, 46, "n"))]


def probe_view(pg):
    """(appends with the footer, sets, java statements, how the footer was placed) for one kit probe page."""
    sh = pg.shell
    ap = SUI.Appends(sh.appends)            # a copy (items + .sets): the kit's own objects are never changed
    root_par, root_mk = ap[0]
    assert root_par is None
    m = re.fullmatch(r"Group #(%s) \{ Anchor: \(Width: (\d+), Height: (\d+)\); \}" % re.escape(sh.root), root_mk)
    assert m and int(m.group(2)) == sh.w and int(m.group(3)) == sh.h, "unexpected kit page root: %s" % root_mk
    used = used_in(ap, sh.body)
    grow = FOOT_H + max(0, FOOT_SLACK - (sh.inner_h - used))        # + up to 4 px when the body was (nearly) full: base1
    if sh.h + grow <= SUI.MAX_PAGE_H:
        # at the bottom of the body; the root grows by the footer (flex children shrink, fixed ones must fit)
        new_h = sh.h + grow
        SUI.assert_page_size(sh.w, new_h)
        ap[0] = (None, "Group #%s { Anchor: (Width: %d, Height: %d); }" % (sh.root, sh.w, new_h))
        slack = SUI.fit([used, FOOT_H, FOOT_SLACK], sh.inner_h + grow, "probe %d body + footer + slack" % pg.n) + FOOT_SLACK
        flex = any(outer_h(mk)[1] for par, mk in ap if par is not None and SUI.render(par).lstrip("#") == sh.body)
        container, how = sh.body, "body end, page %d -> %d px high, %s" % (
            sh.h, new_h, "a FlexWeight child takes the free height" if flex else "%d px slack" % slack)
    else:
        # the page is too high to grow: a LayoutMode Top column with a fixed height, no padding and room for the footer
        container, how = None, None
        for par, mk in ap:
            cid = ident_of(mk)
            a, d = _anchor(mk)
            if (par is None or not cid or cid.endswith("Look") or "LayoutMode: Top" not in d or "Height" not in a
                    or "Padding" in d or int(a.get("Width", sh.inner_w)) < FOOT_W):
                continue
            free = int(a["Height"]) - used_in(ap, cid)
            if free >= FOOT_H + FOOT_SLACK:
                container, how = cid, "bottom of #%s (%d px free, %d px slack), page stays %d px high" % (
                    cid, free, free - FOOT_H, sh.h)
                break
        if container is None:
            raise SystemExit("probe %d (%s): no place for the Back / Close footer (page %d px high, no column with %d px free)"
                             % (pg.n, pg.name, sh.h, FOOT_H + FOOT_SLACK))
    ap.extend(footer(container))
    chk = SUI.Appends(ap)
    chk.sets.extend(sh.sets)               # the shell's own b.set lines (a b.set title, a progress Value) must hit real elements too
    SUI.check_page(chk, PREFIX)            # every markup rule + every parent exists + no duplicate id + every b.set target exists
    kit_java = sh.java("b")
    full = pg.java("b")
    assert full.startswith(kit_java), "probe %d: Probe.java must start with the shell's Java" % pg.n
    extra = full[len(kit_java):].strip("\n")
    java = ap.java("b", sets=sh.sets) + ("\n" + extra if extra else "")
    # nothing of the kit markup changed except the root height line and the footer lines
    mine = [l for l in java.splitlines() if not (NAV in l and "appendInline" in l)]
    kit_lines = full.splitlines()
    assert len(mine) == len(kit_lines) and mine[1:] == kit_lines[1:] and "appendInline((String) null" in mine[0], \
        "probe %d: the page Java differs from the kit's in more than the root height + footer" % pg.n
    assert SUI.item_grid_java_is_safe(java), "probe %d fills a grid slot with a held stack" % pg.n
    sets = list(ap.sets) + list(sh.sets)
    return ap, sets, java, how


VIEWS = {}
for pg in PAGES:
    VIEWS[pg.n] = probe_view(pg)
    print("probe %2d %-16s key %-16s footer: %s" % (pg.n, pg.name, pg.key, VIEWS[pg.n][3]))

# ================= the index (flat, proven markup only) =================
IX = PREFIX + "Ix"
IX_W, IX_H, IX_PADH, IX_PADV = 1300, 960, 28, 16
ROW_H, ROW_GAP = 34, 3


def build_index():
    ap = SUI.Appends()
    ap.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); Background: %s; Padding: (Horizontal: %d, Vertical: %d); LayoutMode: Top; }"
               % (IX, IX_W, IX_H, FLAT["root"], IX_PADH, IX_PADV)))
    ap.append((IX, "Group { Anchor: (Height: 3); Background: %s; }" % FLAT["stripe"]))
    ap.append((IX, f_label(None, "SkyyUiProbe - kit probe pages", 46, 30, "title", bold=True, center=True)))
    f_text(ap, IX, IX + "Sub1", "Open the pages from the top: the three base pages first, then 3 to 17. Back returns here, Esc or "
                                "Close leaves.", 26, 16, "sub", center=True)
    f_text(ap, IX, IX + "Sub2", "A disconnect right after you click Open means that page failed - note its number (the server log "
                                "names it too).", 26, 16, "sub", center=True)
    ap.append((IX, f_spacer(10, 8)))
    base = [n for n in ORDER if BY_N[n].key == "base"]
    rest = [n for n in ORDER if BY_N[n].key != "base"]
    for hn, (head, group, kind) in enumerate((("Base pages - open these first", base, "g"),
                                              ("Feature pages - one UNVERIFIED feature each, in number order", rest, "b"))):
        if hn:
            ap.append((IX, f_spacer(10, 6)))
        f_text(ap, IX, IX + "Head" + str(hn), head, 26, 17, "caption", bold=True)
        for j, n in enumerate(group):
            pg = BY_N[n]
            row = IX + "Row" + str(n)
            if j:
                ap.append((IX, f_spacer(10, ROW_GAP)))
            ap.append((IX, "Group #%s { Anchor: (Height: %d); Background: %s; LayoutMode: Left; }" % (row, ROW_H, FLAT["row"])))
            ap.append((row, f_spacer(12, ROW_H)))
            ap.append((row, f_label(IX + "Num" + str(n), str(n), ROW_H, 18, "num", bold=True, center=True, w=60)))
            ap.append((row, f_label(IX + "Name" + str(n), pg.name, ROW_H, 18, "name", bold=True, w=200)))
            f_text(ap, row, IX + "What" + str(n), purpose(pg), ROW_H, 16, "sub", w=812)
            ap.append((row, f_spacer(10, ROW_H)))
            ap.append((row, f_button(IX + "Open" + str(n), "Open", 140, ROW_H, kind)))
    ap.append((IX, f_spacer(10, 8)))
    ap.append((IX, f_label(IX + "Info", "", 28, 17, "title", bold=True, center=True)))       # b.set from ProbePage.info at runtime
    ap.append((IX, "Group #%sBottom { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }" % IX))
    f_text(ap, IX + "Bottom", IX + "Kit", "Kit %s  |  %d pages  |  chat: /skyprobe list, /skyprobe number or name" % (
        KIT_ID, len(PAGES)), 46, 15, "caption", w=1000)
    ap.append((IX + "Bottom", f_spacer(16, 46)))
    ap.append((IX + "Bottom", f_button(IX + "Close", "Close", 170, 46, "n")))
    return ap


IXA = build_index()
INFO_SET = (IX + "Info", "Text", SUI.J("info", "Nothing opened yet"))     # the runtime line under the rows (ProbePage.info)
_ixchk = SUI.Appends(IXA)
_ixchk.sets.append(INFO_SET)
SUI.check_page(_ixchk, PREFIX)
SUI.fit([used_in(IXA, IX)], IX_H - 2 * IX_PADV, "index body")
SUI.assert_page_size(IX_W, IX_H)
assert all(outer_h(mk)[1] is False for _p, mk in IXA if _p is not None), "the index uses no FlexWeight"
for _p, mk in IXA:
    assert "Common/" not in mk and "Sounds/" not in mk and "FontName" not in mk and "LetterSpacing" not in mk, "index: flat only"
    assert not re.search(r"Anchor: \([^)]*\b(Top|Bottom|Left|Right|Horizontal|Vertical|Full):", SUI.render(mk)), \
        "index: no Anchor margins (only Width / Height, like the proven flat pages): %s" % mk[:100]
for _i, _pr, _v in IXA.sets:
    # < and > are proven only as INLINE text ("< Back"), not through b.set (review 2026-09-29): keep them out of b.set texts
    assert not (isinstance(_v, str) and re.search(r"[<>]", SUI.render(_v))), "index b.set text with < or >: %r" % _v
IX_JAVA =IXA.java("b") + "\n" + SUI.java_set(*INFO_SET)
IX_BINDS = [("#" + IX + "Open" + str(n), "open:" + str(n)) for n in ORDER] + [("#" + IX + "Close", "close")]
IX_BIND = ["ev.addEventBinding(@BT@.Activating, %s, @EVD@.of(\"a\", %s));" % (SUI.java_lit(sel), SUI.java_lit(act))
           for sel, act in IX_BINDS]
print("index: %d appends, %d b.set lines, %d / %d px high, rows in the order %s" % (
    len(IXA), len(IXA.sets) + 1, used_in(IXA, IX), IX_H - 2 * IX_PADV, ORDER))

if DUMP:
    out = {"kit": KIT_ID, "order": ORDER, "names": dict((str(p.n), p.name) for p in PAGES),
           "foot": ["#" + NAV_BACK, "#" + NAV_CLOSE],
           "index": {"appends": [[p, SUI.render(m)] for p, m in IXA], "sets": [[i, pr, v] for i, pr, v in IXA.sets],
                     "info": ["#" + IX + "Info", "Text"], "binds": [list(x) for x in IX_BINDS]}}
    for n, (ap, sets, _java, _how) in VIEWS.items():
        _kit, _full = BY_N[n].shell.java("b"), BY_N[n].java("b")
        out[str(n)] = {"appends": [[p, SUI.render(m if isinstance(m, str) else m.variants()[0])] for p, m in ap],
                       "sets": [[i, pr, v] for i, pr, v in sets],
                       "extra": [l for l in _full[len(_kit):].strip("\n").splitlines() if l.strip()]}
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
WHAT = [""] * (MAXN + 1)
for p in PAGES:
    NAMES[p.n], KEYS[p.n], WHAT[p.n] = p.name, p.key, purpose(p)
M(views, "public static int count() { return %d; }" % len(PAGES))
M(views, "public static int[] order() { return new int[] { %s }; }" % ", ".join(str(n) for n in ORDER))
M(views, "public static String[] names() { return new String[] { %s }; }" % ", ".join(jl(x) for x in NAMES))
M(views, "public static String[] keys() { return new String[] { %s }; }" % ", ".join(jl(x) for x in KEYS))
M(views, "public static String[] whats() { return new String[] { %s }; }" % ", ".join(jl(x) for x in WHAT))
M(views, r"""
public static boolean has(int n) {
  String[] a = names();
  return n > 0 && n < a.length && a[n].length() > 0;
}""")
M(views, "public static String nameOf(int n) { return has(n) ? names()[n] : \"?\"; }")
M(views, "public static String keyOf(int n) { return has(n) ? keys()[n] : \"?\"; }")
M(views, "public static String whatOf(int n) { return has(n) ? whats()[n] : \"\"; }")
# a page number (1-18) or a stable name (base1, checkbox, number-field, ...); -1 = none. Locale.ROOT: under a Turkish / Azeri
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
  if (!@PKG@.ProbeViews.has(n)) return "Nothing opened yet - start with probe 1 (base1), then 2, then 18.";
  return "Last opened: probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + "). Did it look right? Then open the next one.";
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
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  int tried = -1;
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("close")) { close(); return; }
    if (a.equals("back")) {
      this.info = lastText(this.view);
      this.view = 0;
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
