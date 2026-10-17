"""Derive SkyyMenu/build_skyymenu_0.3.36.py from the LIVE SkyyMenu 0.3.35 (python tools/menu_0_3_36_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_35_patch.py -> 0.3.35 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.36. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.35 (nothing else changed). The harness SkyyMenu/test_skyymenu_0.3.36.py is its own file.

0.3.36 (2026-10-16) = round menu36, the MENU PATTERN sweep leftovers of SkyyMenu (research/Menu-Pattern.md rules 7-8, M8, M16). Skyy
(docs/answered/ui.md 2026-10-16): "I never want to have to use a back button. The menus at the top should always be there for easy
navigation." + "work through the small things and the next up list" + "i dont mind scrolling, but if there are only a few items try to scale
them to all fit."
  1. THE ADMIN PAGE (OpsPage) ON THE KIT 1.7 HUB PAGE under Settings (1600 x 980; row 2 shows Server Setup selected - it is a sub view of
     Server Setup, admins only): the sub-tab row = All mods (Server Setup's mod list) + its 4 tabs; ONE scroll list of the buttons (no
     pages; a short tab gets bigger buttons - Skyy rule 7, HubBar.growSize); the footer = the result line + Close. Its old back button to the
     menu and its page buttons went; rows 1 + 2 lead away (hub clicks routed like Server Setup's).
  2. SERVER SETUP: every row page (the mod list, a mod, a table, the change log, the history, the import files) is ONE scroll list with
     grow rows (rule 7) on the kit row look; the two in-body tab rows went: a mod's categories join the sub-tab row after the crumbs
     (All mods | <mod> | <category ...>), the change log's mod filter and the history's file filter are one in-page picker each (< name >).
     The list view's Admin button is the Admin crumb now. Crumbs stay All mods | <mod> | <view>; every crumb / category / picker click
     carries the view's text boxes (no typed value is lost); the confirm flow is unchanged (nothing bound but Confirm / Cancel).
     An editable table draws at most ADM_TFIELDS boxes (the filter finds the rest), the change log the newest ADM_GMAX lines.
  3. LONG CRUMB NAMES: every crumb / category text is fitted to its button (AdminPage.fit: the client's own glyph widths at the 12 px the
     label shrinks to, cut with ... when even that is too wide) and set with b.set, so nothing clips at 150 px (or the narrower category tabs).
  4. FIX: the crumb ids were SkyyAdmCr<i> - the same ids as a choice row's > button (SkyyAdmCr<row>): a mod page with a long choice row on
     row 0 / 1 drew two elements with one id. The crumbs are SkyyAdmCrumb<i> now.
  No saved data, no command, no setting. ROLLBACK to 0.3.35: safe (the old pages come back).
"""
import os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import skyyui as SUI

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.35.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.36.py"))
assert P.has('VERSION = "0.3.35"\n') and P.has("SUI.hub_page(") and not P.has("OPS_SUBTABS"), "not the generated SkyyMenu 0.3.35 script"
CMD0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
assert SUI.KIT_PAGE_VERSION == "1.7", "kit skyyui 1.7 (hub_page)"


def cut(start, end):
    """the exact text of P.s from start up to and including end (each unique)"""
    assert P.s.count(start) == 1, "start anchor count %d: %s" % (P.s.count(start), start[:120])
    i = P.s.index(start)
    j = P.s.index(end, i)
    return P.s[i:j + len(end)]


P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.36: MENU PATTERN leftovers (notes: tools/menu_0_3_36_patch.py; research/Menu-Pattern.md rules 7-8, M8, M16): the Admin page on the kit
       1.7 hub page under Settings (sub-tabs, one scroll list), Server Setup's row pages as scroll lists with grow rows, a mod's categories
       in the sub-tab row, in-page pickers for the change log / history filters, crumb texts fitted to their buttons (SkyyAdmCrumb ids).
  CHECKED: see SkyyMenu/test_skyymenu_0.3.36.py.
''')
P.rep('VERSION = "0.3.35"\n', 'VERSION = "0.3.36"\n')

# =================================================================================================== 1. THE ADMIN PAGE (Python markup)
P.rep('''OPS_W, OPS_H = 1160, 960
OPS_ROWS = 12                          # button rows per page; 2 buttons per row
OPS_PER = OPS_ROWS * 2
OPS_BTN_W = 252''', '''OPS_W, OPS_H = SUI.HUB_PAGE_W, SUI.HUB_PAGE_H    # 0.3.36: the kit 1.7 hub page under Settings (0.3.23 - 0.3.35: a 1160 x 960 window)
OPS_SUBTABS = ["All mods"] + OPS_TABS          # 0.3.36: the ONE sub-tab row: Server Setup's mod list, then the Admin page's 4 tabs
OPS_BTN_PAD = 10
OPS_BTN_W = 252''')
P.rep(cut('''def ops_page():
    """the Admin page's markup pieces: shell (the frame), parts (body pieces by name, each (parent, markup)), the per-button markups"""''',
          '''      % (OPS_W, OPS_H, len(OPS), ", ".join("%s %d" % (t, len([o for o in OPS if o[0] == i])) for i, t in enumerate(OPS_TABS)), OPS_PER, OPS_LEFT, SUI_KIT_ID))
'''), '''def ops_btn(ident, h, kind):
    """0.3.36: one Admin page button (the sky button art), its label set with b.set (OpsPage.build)"""
    return 'TextButton #%s { Anchor: (Width: %d, Height: %s); Padding: (Horizontal: %d); Text: ""; %s }' % (
        ident, OPS_BTN_W, h, OPS_BTN_PAD, SUI.theme_button_style(kind, "normal", theme="sky"))


def ops_page():
    """0.3.36 (research/Menu-Pattern.md rule 8 + M16): the Admin page on the kit 1.7 hub_page under Settings - row 1, row 2 (Server Setup
    selected: the page is its sub view), the ONE sub-tab row (All mods = Server Setup's mod list, then Server / Economy / Players /
    Diagnostics), the content (the caption, the Player / Text picker row, ONE scroll list of the buttons, two a row, each with the command
    it runs; Diagnostics' info lines under them) and the footer (the result line, Close). No back button, no pages. Returns the pieces."""
    J = SUI.J
    sh = SUI.hub_page("SkyyOpsF", "settings", body_id="SkyyOpsFB", content_id="SkyyOps", sub=True, footer=True)
    IW, BH, LP = sh.content_w, SUI.BTN_H, SUI.WELL_LIST_PAD
    P = {}
    P["sub"] = ("SkyyOps", SUI.label("SkyyOpsSub", "", "caption", h=24, size=OPS_HELP_FS))
    P["pick"] = ("SkyyOps", SUI.group("SkyyOpsPick", "Left", h=BH, anchor={"top": 6, "bottom": 8}))
    list_h = sh.content_h - 24 - (6 + BH + 8)
    P["list"] = ("SkyyOps", SUI.scroll_list("SkyyOpsList", h=list_h, well=True))
    left = sh.content_h - sum(SUI.outer_size(P[k][1])[1] for k in ("sub", "pick", "list"))
    assert left == 0 and list_h >= 500, "admin page parts do not fill the content (%d left, list %d)" % (left, list_h)
    # the sub-tab row: All mods + the 4 tabs (kit small buttons, 150 px), the active tab Primary
    SUI.assert_sub_tabs_fit(OPS_SUBTABS)
    subn = [SUI.sub_tab_markup("SkyyOpsF", k, t, False) for k, t in enumerate(OPS_SUBTABS)]
    subs = [SUI.sub_tab_markup("SkyyOpsF", k, t, True) for k, t in enumerate(OPS_SUBTABS)]
    subgap = "Group { Anchor: (Width: %d); }" % SUI.SUB_TAB_GAP
    # the picker row: Player < name > | Text [box] Clear - filled exactly
    g = 6
    pw = {"plab": 80, "pprev": 72, "pname": 268, "pnext": 72, "gap": 24, "tlab": 56, "clr": 120}
    field_w = IW - (pw["plab"] + pw["pprev"] + g + pw["pname"] + g + pw["pnext"] + pw["gap"] + pw["tlab"] + pw["clr"] + g)
    assert field_w >= 600, "the Text box is too narrow: %d" % field_w
    sb = lambda i, t, w, anc=None: 'TextButton #%s { Anchor: (Width: %d, Height: %d%s); Padding: (Horizontal: %d); Text: "%s"; %s }' % (
        i, w, BH, "".join(", %s: %d" % (k.capitalize(), v) for k, v in sorted((anc or {}).items())), OPS_BTN_PAD, t,
        SUI.theme_button_style("secondary", "normal", theme="sky"))
    pick = [("SkyyOpsPick", SUI.label(None, "Player", "bold", w=pw["plab"], h=BH)),
            ("SkyyOpsPick", sb("SkyyOpsPPrev", "<", pw["pprev"], {"right": g})),
            ("SkyyOpsPick", SUI.label("SkyyOpsPName", "", "bold", w=pw["pname"], h=BH, align="Center")),
            ("SkyyOpsPick", sb("SkyyOpsPNext", ">", pw["pnext"], {"left": g})),
            ("SkyyOpsPick", SUI.spacer(w=pw["gap"], h=BH)),
            ("SkyyOpsPick", SUI.label(None, "Text", "bold", w=pw["tlab"], h=BH)),
            ("SkyyOpsPick", SUI.text_field("SkyyOpsArgBox", "SkyyOpsArg", w=field_w, h=BH, placeholder=OPS_TEXT_HINT, max_length=OPS_TEXT_MAX)),
            ("SkyyOpsPick", sb("SkyyOpsClr", "Clear", pw["clr"], {"left": g}))]
    assert sum(SUI.outer_size(mk)[0] for _p, mk in pick) == IW, "the picker row is not filled exactly"
    # the button list: rows of two cells (button | gap | help text); the row height bh = a grow tier (rule 7), the buttons as high as it
    row_w = IW - 2 * LP - 24
    cell_w = (row_w - OPS_CELL_GAP) // 2
    help_w = cell_w - OPS_BTN_W - 10
    rid, cid, bh = J("r", "0"), J("c", "0"), J("bh", str(BH))
    grid = {
        "row": ("SkyyOpsList", SUI.group("SkyyOpsR" + rid, "Left", h=bh, anchor={"bottom": OPS_ROW_GAP})),
        "cell": ("SkyyOpsR" + rid, SUI.choose(J("c % 2 == 0"), SUI.group("SkyyOpsC" + cid, "Left", w=cell_w, h=bh, anchor={"right": OPS_CELL_GAP}),
                                              SUI.group("SkyyOpsC" + cid, "Left", w=cell_w, h=bh))),
        "btn": ("SkyyOpsC" + cid, SUI.choose(J("dng"), ops_btn("SkyyOpsA" + J("i", "0"), bh, "destructive"), ops_btn("SkyyOpsA" + J("i", "0"), bh, "secondary"))),
        "gap": ("SkyyOpsC" + cid, SUI.spacer(w=10, h=bh)),
        "help": ("SkyyOpsC" + cid, SUI.label("SkyyOpsH" + cid, "", "caption", w=help_w, h=bh, size=OPS_HELP_FS)),
        "line": ("SkyyOpsList", SUI.label("SkyyOpsI" + J("k", "0"), "", "default", w=row_w, h=OPS_LINE_H, size=OPS_HELP_FS + 1,
                                          anchor={"bottom": OPS_LINE_GAP})),
    }
    # the footer: the result line (its colour by the result mark), Close - filled exactly
    fg = SUI.FOOT_GAP
    msg_w = IW - fg - SUI.BTN_MIN_W
    foot = [("SkyyOpsFFoot", SUI.label("SkyyOpsMsg", "", "default", w=msg_w, h=SUI.FOOT_BTN_H, size=16, bold=True,
                                       col=J("colorOf(this.info)", SUI.COLOR["success"]), wrap=True, padding={"horizontal": 8})),
            ("SkyyOpsFFoot", SUI.spacer(w=fg)),
            ("SkyyOpsFFoot", SUI.foot_button("SkyyOpsClose", "Close", sound="cancel"))]
    assert sum(SUI.outer_size(mk)[0] for _p, mk in foot) == IW, "the admin footer is not filled exactly"
    # every look this page can show, checked as one page (ids, parents, markup rules, proven properties only, the menu pattern)
    chk = SUI.hub_page_preview(sh, tabs=[(r[0], SUI.hub_tab_label("settings", r[0])) for r in SUI.hub_page_tabs("settings")], my_tab="setup")
    for k in range(len(OPS_SUBTABS)):
        if k > 0:
            chk.append(("SkyyOpsFSub", subgap))
        chk.append(("SkyyOpsFSub", subs[k] if k == 1 else subn[k]))
    for k in ("sub", "pick", "list"):
        chk.append(P[k])
    chk.extend(pick)
    for k in ("row", "cell", "btn", "gap", "help", "line"):
        chk.append(grid[k])
    chk.extend(foot)
    chk.check("SkyyOps")
    SUI.assert_proven(chk, what="admin page")
    SUI.assert_proven(subs + subn, what="admin page sub-tabs")
    SUI.check_sky_paths(chk, tab_icons=True)
    for _v in (0, 1):     # SUI.assert_menu_page renders each markup: one pass per variant of the choose() pieces (kit 1.7 takes no Choice)
        SUI.assert_menu_page(SUI.Appends([(p_, mk.variants()[_v] if isinstance(mk, SUI.Choice) else mk) for p_, mk in chk]), sh)
    # every fixed text fits: help lines (with the widest status), the sub line, the info lines
    for o in OPS:
        h_ = ops_help(o) + ((" - 99,999 open" if o[7] == "auction:count" else " - 9,999 items") if o[7] else "")
        assert SUI.text_width(h_, OPS_HELP_FS) <= help_w, "help text too wide for its cell: " + h_
        assert SUI.text_width(o[1], 12, bold=True, upper=True) <= OPS_BTN_W - 2 * OPS_BTN_PAD, "button label too wide: " + o[1]
    assert SUI.text_width("Press again", 12, bold=True, upper=True) <= OPS_BTN_W - 2 * OPS_BTN_PAD
    assert SUI.text_width(OPS_SUB, OPS_HELP_FS) <= IW, "sub line too wide"
    assert SUI.text_width("Not running: SkyyAccessories, SkyyCollections, SkyyExploration, SkyyMerchants, SkyyWardrobe,", OPS_HELP_FS + 1) <= row_w
    rows_h = SUI.grow_row_sizes(list_h - 2 * LP, BH, gap=OPS_ROW_GAP)
    return sh, P, (subn, subs, subgap), pick, grid, foot, list_h, rows_h, cell_w, help_w


OPS_SH, OPS_P, OPS_SUBMK, OPS_PICK_MK, OPS_GRID, OPS_FOOT, OPS_LIST_H, OPS_ROW_H, OPS_CELL_W, OPS_HELP_W = ops_page()
OPS_LIST_IN = OPS_LIST_H - 2 * SUI.WELL_LIST_PAD                           # the list well's inner height (growSize's room)
OPS_SHELL_JAVA = OPS_SH.java("b")
OPS_HUB_JAVA = SUI.java_hub_page(OPS_SH, "setup", cls="@PKG@.HubBar", uuid="me()")
assert OPS_HUB_JAVA == '@PKG@.HubBar.page17(b, ev, "SkyyOpsF", "settings", "setup", 1552, me(), 2);', OPS_HUB_JAVA
OPS_PART_JAVA = dict((k, SUI.java_append(p, mk)) for k, (p, mk) in OPS_P.items())
OPS_PICK_JAVA = "\\n".join(SUI.java_append(p, mk) for p, mk in OPS_PICK_MK)
OPS_GRID_JAVA = dict((k, SUI.java_append(p, mk)) for k, (p, mk) in OPS_GRID.items())
OPS_FOOT_JAVA = "\\n".join(SUI.java_append(p, mk) for p, mk in OPS_FOOT)
# the SET this menu is built with (Diagnostics compares the running versions with it; SkyyMenu = this build)
OPS_SET = [(m, (VERSION if m == "SkyyMenu" else v)) for m, v in _LIVE]
print("admin page: %d x %d (kit 1.7 hub page), %d buttons (%s), one scroll list (row sizes %s), kit %s"
      % (OPS_W, OPS_H, len(OPS), ", ".join("%s %d" % (t, len([o for o in OPS if o[0] == i])) for i, t in enumerate(OPS_TABS)), OPS_ROW_H, SUI_KIT_ID))
''')
# ---- the Admin page's Java data
P.rep('''F(ops, "public static final String[] O_MK = %s;" % jarr([SUI.render(m) for m in OPS_BTN]))
F(ops, "public static final String[] O_MKA = %s;" % jarr([SUI.render(m) for m in OPS_ARMED]))''',
      '''F(ops, "public static final String[] O_SUBN = %s;" % jarr([SUI.render(m) for m in OPS_SUBMK[0]]))   # 0.3.36: the sub-tab row
F(ops, "public static final String[] O_SUBS = %s;" % jarr([SUI.render(m) for m in OPS_SUBMK[1]]))
F(ops, "public static final String O_SUBGAP = %s;" % jstr(OPS_SUBMK[2]))''')
P.rep('''F(ops, "public static final int PER = %d;" % OPS_PER)
F(ops, "public static final int WELL_H = %d;" % OPS_ROWS_FIT)
F(ops, "public static final int ROW_H = %d;" % (SUI.BTN_H + OPS_ROW_GAP))''',
      '''F(ops, "public static final int LIST_IN = %d;" % OPS_LIST_IN)            # 0.3.36: one scroll list - its room + the row sizes (rule 7)
F(ops, "public static final int[] O_ROWH = %s;" % jints(OPS_ROW_H))
F(ops, "public static final int ROW_GAP = %d;" % OPS_ROW_GAP)''')

# ---- the Admin page's Java: me(), the hub click answer, build, handleDataEvent
P.rep('''M(ops, r"""
public String who() {''', '''M(ops, r"""
public java.util.UUID me() {
  try { return this.playerRef == null ? null : this.playerRef.getUuid(); } catch (Throwable t) { return null; }
}""")
M(ops, r"""
public String who() {''')
P.rep('''M(ops, r"""
public void openSetup(@REF@ ref, @ST@ st) {''', '''# 0.3.36: after a hub click (MenuHub.click's answer; the page is tab "ops" of Settings, so row 2's Server Setup leads to Server Setup): the X
# closes, Home opens the SkyWynn Menu, an opened tab owns the screen, a tab that could not open says so
M(ops, r"""
public void hubAfter(@REF@ ref, @ST@ st, String hr) {
  if (hr.equals("close")) { closeNow(ref, st); return; }
  if (hr.equals("menu")) { openMenu(ref, st); return; }
  if (@PKG@.MenuHub.opened(hr) || hr.equals("self")) return;
  this.info = "-" + @MD@.HUB_TXT_FAIL;
  redraw();
}""")
M(ops, r"""
public void openSetup(@REF@ ref, @ST@ st) {''')
P.rep(cut('''M(ops, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  boolean ok = pageOk();''', '''  } catch (Throwable t) { @MU@.warn("admin page click failed: " + t); }
}""")'''), '''# 0.3.36: the kit 1.7 hub page - rows 1 + 2 (HubBar.page17), the sub-tabs (their clicks carry the Text box), the picker row, ONE scroll list
# of the visible buttons (a short tab grows its rows: HubBar.growSize over O_ROWH; Diagnostics' info lines below), the footer
M(ops, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  boolean ok = pageOk();
  if (this.tab < 0 || this.tab >= O_TABS.length) this.tab = 0;
  int[] vis = ok ? visibleOn(this.tab) : new int[0];
  this.pg = 0;
  this.field = ok;
""" + "\\n".join("  " + ln for ln in OPS_SHELL_JAVA.split("\\n")) + r"""
  @PKG@.MenuHub.ensure(me());
  """ + OPS_HUB_JAVA + r"""
  if (ok) {
    for (int k = 0; k < O_SUBN.length; k++) {
      if (k > 0) b.appendInline("#SkyyOpsFSub", O_SUBGAP);
      b.appendInline("#SkyyOpsFSub", k == this.tab + 1 ? O_SUBS[k] : O_SUBN[k]);
      ev.addEventBinding(@BT@.Activating, "#SkyyOpsFSub" + k, evd(k == 0 ? "setup" : "ot" + (k - 1)));
    }
  }
  """ + OPS_PART_JAVA["sub"] + r"""
  b.set("#SkyyOpsSub.Text", ok ? SUB : textOf(NOACCESS));
  if (ok) {
    """ + OPS_PART_JAVA["pick"] + r"""
""" + "\\n".join("    " + ln for ln in OPS_PICK_JAVA.split("\\n")) + r"""
    String[] on = online();
    int pj = pickIndex(on);
    b.set("#SkyyOpsPName.Text", pj < 0 ? (on.length == 0 ? "nobody online" : "nobody picked") : on[pj] + "  (" + (pj + 1) + " of " + on.length + ")");
    if (this.arg != null && this.arg.length() > 0) b.set("#SkyyOpsArg.Value", this.arg);
    ev.addEventBinding(@BT@.Activating, "#SkyyOpsPPrev", evd("pprev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyOpsPNext", evd("pnext"));
    ev.addEventBinding(@BT@.Activating, "#SkyyOpsClr", evd("clr"));
  }
  """ + OPS_PART_JAVA["list"] + r"""
  int n = vis.length;
  String[] dl = new String[0];
  if (ok && this.tab == O_DIAG) dl = diagLines();
  else if (ok && n == 0) dl = new String[] { "No button on this tab for you: none of its commands is on this server, or your permissions do not include them." };
  int nr = (n + 1) / 2;
  int sz = nr > 0 ? @PKG@.HubBar.growSize(nr, LIST_IN - dl.length * LINE_H, O_ROWH, ROW_GAP) : 0;
  int bh = O_ROWH[sz];
  for (int c = 0; c < n; c++) {
    int r = c / 2;
    int i = vis[c];
    boolean arm = armedNow(i);
    boolean dng = O_CONF[i] || arm;
    if (c % 2 == 0) {
      """ + OPS_GRID_JAVA["row"] + r"""
    }
    """ + OPS_GRID_JAVA["cell"] + r"""
    """ + OPS_GRID_JAVA["btn"] + r"""
    b.set("#SkyyOpsA" + i + ".Text", arm ? "Press again" : O_LABEL[i]);
    """ + OPS_GRID_JAVA["gap"] + r"""
    """ + OPS_GRID_JAVA["help"] + r"""
    b.set("#SkyyOpsH" + c + ".Text", helpOf(i));
    ev.addEventBinding(@BT@.Activating, "#SkyyOpsA" + i, evd("op" + i));
  }
  for (int k = 0; k < dl.length; k++) {
    """ + OPS_GRID_JAVA["line"] + r"""
    b.set("#SkyyOpsI" + k + ".Text", dl[k]);
  }
""" + "\\n".join("  " + ln for ln in OPS_FOOT_JAVA.split("\\n")) + r"""
  b.set("#SkyyOpsMsg.Text", textOf(ok ? this.info : NOACCESS));
  ev.addEventBinding(@BT@.Activating, "#SkyyOpsClose", evd("close"));
}""")
M(ops, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String hr = @PKG@.MenuHub.click(this.playerRef, data, "settings", "ops");   // 0.3.36: rows 1 + 2 (the bar's click carries no Text box)
    if (hr != null) { hubAfter(ref, st, hr); return; }
    String a = @MU@.jstr(data, "a", 40);
    if (data.indexOf("\\"" + argKey() + "\\"") >= 0) this.arg = @MU@.jstr(data, argKey(), TEXT_MAX);
    if (a.equals("close")) { closeNow(ref, st); return; }
    if (!pageOk()) { this.info = NOACCESS; this.armed = -1; redraw(); return; }
    if (a.equals("setup")) { openSetup(ref, st); return; }
    if (a.startsWith("ot")) {
      int t = num(a.substring(2));
      if (t >= 0 && t < O_TABS.length) { this.tab = t; this.pg = 0; this.armed = -1; this.info = ""; }
    }
    else if (a.equals("pprev")) cyclePick(-1);
    else if (a.equals("pnext")) cyclePick(1);
    else if (a.equals("clr")) this.arg = "";
    else if (a.startsWith("op")) run(num(a.substring(2)));
    redraw();
  } catch (Throwable t) { @MU@.warn("admin page click failed: " + t); }
}""")''')

# =================================================================================================== 2. SERVER SETUP (Python markup)
P.rep(cut('''UI_A = {
    # 0.3.28: the page root, accent and title row are the kit's hub shell now''',
          '''assert 120 + 120 + 150 + 150 + 130 + 200 + 120 + 6 * 8 <= A_INNER, "the list footer is wider than the page"
'''), '''# 0.3.36 (research/Menu-Pattern.md M8 + rule 7): every row page is ONE scroll list (SUI.scroll_list, the well) of kit rows; a short list
# grows its rows (SUI.grow_row_sizes -> HubBar.growSize: the row taller, its content centred). A row's pieces are built at run time as
# <head> + <row number> + <tail> (UI_<NAME>A / UI_<NAME>B below, validated here with a sample number); a row group takes its tier's tail
# UI_<NAME>B[size]. The rows lose 24 px of width to the scrollbar (ADM_LW).
_ROWBG = SUI.THEME["sky"]["row"]                      # the kit row (the Settings rows' look; 0.3.35: #142030)
_BOXBG = SUI.THEME["sky"]["inset"]                    # the info / message / preview boxes
ADM_LW = A_INNER - 2 * SUI.WELL_LIST_PAD - 24         # 1048: what a scroll-list row may use
ADM_LH = {"list": A_BODY - 58, "mod": A_BODY - 26 - 40, "modp": A_BODY - 58 - 40, "tableadd": A_BODY - 58 - 40 - 30 - 62, "table": A_BODY - 58 - 40 - 30,
          "log": A_BODY - 58 - 40, "hist": A_BODY - 58 - 40, "histprev": A_BODY - 58 - 40 - 282, "files": ADM_FROWS * 48}
ADM_IN = dict((k, v - 2 * SUI.WELL_LIST_PAD) for k, v in ADM_LH.items())    # growSize's room
ADM_RH = {"L": SUI.grow_row_sizes(ADM_IN["list"], 70, gap=6), "M": SUI.grow_row_sizes(ADM_IN["mod"], 70, gap=6),
          "T": SUI.grow_row_sizes(ADM_IN["tableadd"], 70, gap=6), "G": SUI.grow_row_sizes(ADM_IN["log"], 46, gap=6),
          "H": SUI.grow_row_sizes(ADM_IN["hist"], 52, gap=6)}
ADM_TFIELDS, ADM_TMAX, ADM_GMAX, ADM_FMAX = 40, 200, 200, 50
ADM_MFIELDS, ADM_CATMIN = 40, 60   # critic fixes: a mod view's crumbs / footer carry at most 40 boxes; a category tab is >= 60 px   # an editable table: at most 40 text boxes; at most 200 table / log rows, 50 files
UI_A = {
    # 0.3.28: the page root, accent and title row are the kit's hub shell now (ADM_HUB_SH below: root SkyyAdmH, body = #SkyyAdm); the
    # view's title and subtitle share ONE line ("<title>   -   <subtitle>", cut at ADM_SUBMAX characters); 0.3.36: on a mod with
    # categories (they fill the sub-tab row) that line is the first line of the body (ASUB)
    "ASUB":     _TXT("SkyyAdmSub", 26, 16, "#ffe9c9", True, True),
    "ABODY":    "Group #SkyyAdmBody { Anchor: (Height: %d); LayoutMode: Top; }" % A_BODY,
    "AGAP6":    "Group { Anchor: (Height: 6); }",
    "AGAP8":    "Group { Anchor: (Height: 8); }",
    "AGAP12":   "Group { Anchor: (Height: 12); }",
    "AGAP20":   "Group { Anchor: (Height: 20); }",
    "AHEAD":    _TXT("SkyyAdmHead", 40, 24, "#e0b060", True),
    "AEMPTY":   _TXT("SkyyAdmEmpty", 80, 19, "#c9dff0", False, True),
    # list
    "ALSEARCH": "Group #SkyyAdmSearch { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "ALROWS":   SUI.scroll_list("SkyyAdmLRows", h=ADM_LH["list"], well=True),
    # mod
    "AROWS":    SUI.scroll_list("SkyyAdmRows", h=ADM_LH["mod"], well=True),
    "AROWSP":   SUI.scroll_list("SkyyAdmRows", h=ADM_LH["modp"], well=True),   # under the category picker
    "AINFO":    "Group #SkyyAdmInfo { Anchor: (Height: 670); Background: %s; Padding: (Horizontal: 24, Vertical: 12); LayoutMode: Top; }" % _BOXBG,
    # table
    "ATFIND":   "Group #SkyyAdmTFindRow { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "ATCOLS":   "Group #SkyyAdmCols { Anchor: (Height: 30); LayoutMode: Left; }",
    "ATROWSA":  SUI.scroll_list("SkyyAdmTRows", h=ADM_LH["tableadd"], well=True),
    "ATROWSB":  SUI.scroll_list("SkyyAdmTRows", h=ADM_LH["table"], well=True),
    "ATADD":    "Group #SkyyAdmTAdd { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 6); }",
    # confirm
    "AMSGBOX":  "Group #SkyyAdmMsgBox { Anchor: (Height: 560); Background: %s; Padding: (Horizontal: 24, Vertical: 12); LayoutMode: Top; }" % _BOXBG,
    "ACONF":    "Group #SkyyAdmConf { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 3); }",
    # log + history (the in-page picker: label, <, the picked name, >) + io
    "APICK":    "Group #SkyyAdmPick { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "APICKL":   _TXT("SkyyAdmPickL", 50, 18, "#e0b060", True, False, 240),
    "APICKV":   _TXT("SkyyAdmPickV", 50, 19, "#ffffff", True, True, 420),
    "AGROWS":   SUI.scroll_list("SkyyAdmGRows", h=ADM_LH["log"], well=True),
    "AHROWS":   SUI.scroll_list("SkyyAdmHRows", h=ADM_LH["hist"], well=True),
    "AHROWSP":  SUI.scroll_list("SkyyAdmHRows", h=ADM_LH["histprev"], well=True),
    "APREV":    "Group #SkyyAdmPrev { Anchor: (Height: 282); Background: %s; Padding: (Horizontal: 16, Vertical: 8); LayoutMode: Top; }" % _BOXBG,
    "APREVHEAD": _TXT("SkyyAdmPrevHead", 26, 17, "#e0b060", True),
    "AIOL1":    _TXT("SkyyAdmIoL1", 34, 18, "#e0b060", True),
    "AIOL2":    _TXT("SkyyAdmIoL2", 34, 18, "#e0b060", True),
    "AIOR1":    "Group #SkyyAdmIoR1 { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "AIOR2":    "Group #SkyyAdmIoR2 { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "AIOF":     _TXT("SkyyAdmIoF", 30, 17, "#9fb8cc"),
    "AIOFROWS": SUI.scroll_list("SkyyAdmIoFRows", h=ADM_LH["files"], well=True),
}
UI_AARR = {      # the fixed-count pieces (info / message / preview lines)
    "AINFOL":   [_TXT("SkyyAdmInfo%d" % i, 27, 18, "#e6f2ff") for i in range(ADM_INFOLINES)],
    "AINFOB":   [_TXT("SkyyAdmInfo%d" % i, 27, 19, "#e0b060", True) for i in range(ADM_INFOLINES)],
    "AMSGQ":    [_TXT("SkyyAdmMsg%d" % i, 33, 21, "#ffe9c9", True) for i in range(ADM_MSGLINES)],
    "AMSGL":    [_TXT("SkyyAdmMsg%d" % i, 33, 18, "#c9dff0") for i in range(ADM_MSGLINES)],
    "APL":      [_TXT("SkyyAdmPL%d" % i, 20, 15, "#c9dff0") for i in range(ADM_PLINES)],
}
# a row group per grow tier: " { Anchor: (Height: h); Background: <kit row>; LayoutMode: ...; Padding: (Top: content centred); }"
_rowb = lambda tiers, lay, content: [" { Anchor: (Height: %d); Background: %s; LayoutMode: %s; Padding: (Top: %d); }" % (h_, _ROWBG, lay, (h_ - content) // 2)
                                    for h_ in tiers]
UI_AROWB = {
    "ALROWB": _rowb(ADM_RH["L"], "Left", 52),       # Group #SkyyAdmLRow<r>: name + line 2 (52), Open, Reload
    "AROWB":  _rowb(ADM_RH["M"], "Top", 64),        # Group #SkyyAdmRow<r>: the line (42) + the help line (22)
    "ATROWB": _rowb(ADM_RH["T"], "Left", 52),       # Group #SkyyAdmTRow<r>: entry, its boxes, Set, Remove
    "AGROWB": _rowb(ADM_RH["G"], "Left", 40),       # Group #SkyyAdmGRow<r>: a change line + Undo
    "AHROWB": _rowb(ADM_RH["H"], "Left", 44),       # Group #SkyyAdmHRow<r>: a version + Preview + Restore
}
ADM_ROWHEAD = {"ALROWB": "Group #SkyyAdmLRow", "AROWB": "Group #SkyyAdmRow", "ATROWB": "Group #SkyyAdmTRow", "AGROWB": "Group #SkyyAdmGRow",
               "AHROWB": "Group #SkyyAdmHRow"}
# the per-row pieces: <head> + r + <tail> (the sample number 7777 marks the split)
_PIECE = {
    "ALTXT":    "Group #SkyyAdmLTxt%s { Anchor: (Width: 712, Height: 52); LayoutMode: Top; }",
    "ALNAME":   _TXT("SkyyAdmLName%s", 28, 21, "#ffffff", True),
    "ALDESC":   _TXT("SkyyAdmLDesc%s", 24, 16, "#b8c8d8"),
    "ALDESCRED": _TXT("SkyyAdmLDesc%s", 24, 16, "#ff8a8a", True),
    "ALINE":    "Group #SkyyAdmLine%s { Anchor: (Height: 42); LayoutMode: Left; }",
    "ANAME":    _TXT("SkyyAdmName%s", 42, 20, "#ffffff", True, False, 524),
    "AW":       "Group #SkyyAdmW%s { Anchor: (Width: 380, Height: 42); LayoutMode: Left; }",
    "AHELP":    "Group #SkyyAdmHelpRow%s { Anchor: (Height: 22); LayoutMode: Left; }",
    "ADESC":    _TXT("SkyyAdmDesc%s", 22, 15, "#b8c8d8", False, False, 1034),
    "ARO":      _TXT("SkyyAdmRo%s", 42, 19, "#ffe9a0", True, False, 380),
    "ACHV":     _TXT("SkyyAdmChv%s", 42, 18, "#ffe9a0", True, True, 268),
    "ATKEY":    _TXT("SkyyAdmTKey%s", 52, 18, "#ffffff", True, False, 300),
    "ATCELLS":  "Group #SkyyAdmTCols%s { Anchor: (Width: 450, Height: 52); LayoutMode: Left; }",
    "AGTXT":    _TXT("SkyyAdmGTxt%s", 40, 16, "#e6f2ff", False, False, 890),
    "AHTXT":    _TXT("SkyyAdmHTxt%s", 44, 16, "#e6f2ff", False, False, 776),
    "AFROW":    "Group #SkyyAdmFRow%s { Anchor: (Height: 42); LayoutMode: Left; }",
    "AFTXT":    _TXT("SkyyAdmFTxt%s", 42, 17, "#e6f2ff", False, False, 890),
}
UI_APIECE = {}
for _n, _t in _PIECE.items():
    _s = _t % "7777"
    assert _s.count("7777") == 1, _n
    UI_APIECE[_n + "A"], UI_APIECE[_n + "B"] = _s.split("7777")
ADM_ROW_SAMPLES = [_t % "7777" for _t in _PIECE.values()] + [ADM_ROWHEAD[_k] + "7777" + _b for _k, _v in UI_AROWB.items() for _b in _v]
# 0.3.36: the crumbs / categories (AdminPage.crumbBtn: the kit small button, its text fitted and set with b.set) + the title label beside them
ADM_CRUMB_PAD = SUI.SUB_TAB_PAD
# the client's glyph widths (x 100, rounded up) at the 12 px a small button label shrinks to, capitals (RenderUppercase): AdminPage.fit
ADM_CW = [int(-(-SUI.text_width(chr(_c), 12, bold=True, upper=True) * 100 // 1)) for _c in range(32, 127)]
ADM_CWMAX = max(ADM_CW)
# the run-time patterns (AdminPage.btn / spc / lab / field / crumbBtn) with sample values, so the validation below also covers them
def adm_btn(i, w, h, text, style):
    return 'TextButton #%s { Anchor: (Width: %d, Height: %d); Text: "%s"; %s }' % (i, w, h, text, style)
def adm_field(i, w, h, mx, ph):
    p = (' PlaceholderText: "%s"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 17);' % ph) if ph else ""
    return ["Group #%sBox { Anchor: (Width: %d, Height: %d); Background: #16263a; }" % (i, w, h),
            "TextField #%s { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: %d;%s Style: (TextColor: #ffffff, FontSize: 19); }" % (i, mx, p)]
def adm_crumb(i, w, sel):
    return 'TextButton #%s { Anchor: (Width: %d, Height: %d); Padding: (Horizontal: %d); Text: ""; %s }' % (
        i, w, SUI.SUB_TAB_H, ADM_CRUMB_PAD, ADM_STYLE["SUBSEL"] if sel else ADM_STYLE["SUBN"])
ADM_SAMPLES = ([adm_btn("SkyyAdmF0", 150, 48, "Changes", ADM_STYLE["BS"]), adm_btn("SkyyAdmPickPrev", 60, 50, "<", ADM_STYLE["BS"]),
                adm_crumb("SkyyAdmCrumb0", 150, True), adm_crumb("SkyyAdmCrumb1", 72, False),
                'Label { Anchor: (Width: 14, Height: 42); Text: ""; }', _TXT("SkyyAdmColv0x1", 52, 18, "#ffffff", False, False, 222)]
               + adm_field("SkyyAdmVal3", 196, 42, 2000, "") + adm_field("SkyyAdmFind", 660, 50, 60, "search settings and editors") + ADM_ROW_SAMPLES)
ADM_UI_ALL = (list(UI_A.values()) + [x for v in UI_AARR.values() for x in v] + list(ADM_STYLE.values()) + [x for v in UI_AROWB.values() for x in v]
              + list(UI_APIECE.values()))
for s_ in list(UI_A.values()) + [x for v in UI_AARR.values() for x in v] + ADM_SAMPLES:
    assert s_.count("{") == s_.count("}") and s_.count("(") == s_.count(")"), "unbalanced inline UI: " + s_
    for eid in re.findall(r"#([A-Za-z0-9_]+)\\s*\\{", s_):
        assert "_" not in eid, "underscore in element id #" + eid
        assert eid.startswith("SkyyAdm"), "server setup ids start with SkyyAdm: #" + eid
    assert "Anchow" not in s_ and ";;" not in s_
    for txt_ in re.findall(r'Text: "([^"]*)"', s_):
        assert re.match(r"^[A-Za-z0-9 <>/-]*$", txt_), "inline text with unproven characters (use b.set): " + txt_
for s_ in ADM_STYLE.values():
    assert s_.count("(") == s_.count(")") and "{" not in s_
# the scroll lists, the rows and the samples: the kit's markup rules + proven properties only (the kit row texture, the scrollbar)
_adm_chk = SUI.Appends([(None, "Group #SkyyAdmT { Anchor: (Width: 1080, Height: 676); LayoutMode: Top; }")])
for _k in ("ALROWS", "AROWS", "AGROWS", "AINFO", "APICK"):
    _adm_chk.append(("SkyyAdmT", UI_A[_k]))
_adm_chk.append(("SkyyAdmLRows", ADM_ROWHEAD["ALROWB"] + "0" + UI_AROWB["ALROWB"][-1]))
_adm_chk.append(("SkyyAdmLRow0", UI_APIECE["ALTXTA"] + "0" + UI_APIECE["ALTXTB"]))
_adm_chk.append(("SkyyAdmRows", ADM_ROWHEAD["AROWB"] + "0" + UI_AROWB["AROWB"][0]))
_adm_chk.append(("SkyyAdmRow0", UI_APIECE["ALINEA"] + "0" + UI_APIECE["ALINEB"]))
_adm_chk.append(("SkyyAdmGRows", ADM_ROWHEAD["AGROWB"] + "0" + UI_AROWB["AGROWB"][1]))
_adm_chk.append(("SkyyAdmPick", UI_A["APICKL"]))
_adm_chk.append(("SkyyAdmPick", UI_A["APICKV"]))
_adm_chk.check("SkyyAdm")
SUI.assert_proven(_adm_chk, what="server setup rows")
SUI.check_sky_paths(_adm_chk)
assert SUI.text_width("Show the versions of", 18, bold=True) <= 240 and SUI.text_width("Show the changes of", 18, bold=True) <= 240
# 0.3.28: the root is the kit's hub shell (its root anchor is checked by the kit: Width / Height only)
# height budgets (spec 2.4 / 2.5 asserts, like the menu's _tall): the body of every view fits the fixed body group
assert SUI.TITLE_H + 2 * 24 + SUI.HUB_BIG_ROW_H + SUI.HUB_BIG_TABS_H + SUI.SUB_ROW_H + A_BODY + SUI.FOOT_H == SUI.HUB_PAGE_H == 980 and A_BODY == 676, \\
    "0.3.35: the server setup page is the 1600 x 980 hub page"
_abody = {"list": 58 + ADM_LH["list"], "mod": 26 + 40 + ADM_LH["mod"], "modp": 58 + 40 + ADM_LH["modp"], "file": 670, "table": 58 + 40 + 30 + ADM_LH["tableadd"] + 62,
          "tablero": 58 + 40 + 30 + ADM_LH["table"], "confirm": 560 + 20 + 62, "log": 58 + 40 + ADM_LH["log"], "hist": 58 + 40 + ADM_LH["hist"],
          "histprev": 58 + 40 + ADM_LH["histprev"] + 282, "io": 34 + 58 + 12 + 34 + 58 + 282 + 30 + ADM_LH["files"]}
for _v, _h in _abody.items():
    assert _h <= A_BODY, "server setup view %s needs %d px, the body has %d" % (_v, _h, A_BODY)
assert 24 + ADM_INFOLINES * 27 <= 670 and 24 + ADM_MSGLINES * 33 <= 560 and 16 + 26 + ADM_PLINES * 20 <= 282
assert ADM_LH["histprev"] >= 2 * 58 and all(len(v) == 3 and v[0] < v[1] < v[2] for v in ADM_RH.values()), "0.3.36: the row tiers"
# width budgets (a scroll-list row: ADM_LW = 1048)
assert 14 + 712 + 10 + 150 + 10 + 150 <= ADM_LW, "a list row is wider than its scroll list"
assert 14 + 524 + 10 + 380 + 10 + 110 <= ADM_LW and 14 + 1034 <= ADM_LW and 156 + 6 + 84 + 6 + 60 + 6 + 60 <= 380 and 270 + 6 + 104 <= 380, "a mod row is wider than its list"
assert 14 + 300 + 10 + 450 + 10 + 100 + 6 + 150 <= ADM_LW and 3 * 146 + 2 * 6 <= 450 and 2 * 222 + 6 <= 450, "a table row is wider than its list"
assert 14 + 890 + 10 + 120 <= ADM_LW and 14 + 776 + 10 + 120 + 6 + 120 <= ADM_LW and 14 + 890 + 10 + 130 <= ADM_LW and 830 + 10 + 200 <= A_INNER
assert 660 + 10 + 130 + 10 + 130 <= A_INNER and 14 + 240 + 60 + 6 + 420 + 6 + 60 <= A_INNER, "the search / picker rows fit"
assert 120 + 180 + 140 + 160 + 100 + 4 * 8 <= SUI.HUB_PAGE_IW - 200 and 150 + 150 + 130 + 120 + 3 * 8 <= SUI.HUB_PAGE_IW - 200, "the footers leave the status line room"
''')
# ---- MenuData: the 0.3.36 row tiers, rooms, pieces, caps, glyph widths
P.rep('''for _n, _t in UI_A.items():
    F(dat, "public static final String UI_%s = %s;" % (_n, jstr(_t)))
for _n, _v in UI_AARR.items():
    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))''', '''for _n, _t in UI_A.items():
    F(dat, "public static final String UI_%s = %s;" % (_n, jstr(_t)))
for _n, _v in UI_AARR.items():
    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))
for _n, _v in UI_AROWB.items():            # 0.3.36: the row group tails per grow tier, the per-row piece heads / tails
    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))
for _n, _t in UI_APIECE.items():
    F(dat, "public static final String UI_%s = %s;" % (_n, jstr(_t)))
for _k, _v in ADM_IN.items():
    F(dat, "public static final int ADM_IN_%s = %d;" % (_k.upper(), _v))
for _k, _v in ADM_RH.items():
    F(dat, "public static final int[] ADM_RH_%s = %s;" % (_k, jints(_v)))
for _n, _v in (("ADM_MFIELDS", ADM_MFIELDS), ("ADM_CATMIN", ADM_CATMIN), ("ADM_TFIELDS", ADM_TFIELDS), ("ADM_TMAX", ADM_TMAX), ("ADM_GMAX", ADM_GMAX), ("ADM_FMAX", ADM_FMAX), ("ADM_CWMAX", ADM_CWMAX),
               ("ADM_CRPAD", ADM_CRUMB_PAD), ("ADM_SUBH", SUI.SUB_TAB_H)):
    F(dat, "public static final int %s = %d;" % (_n, _v))
F(dat, "public static final int[] ADM_CW = %s;" % jints(ADM_CW))''')

# =================================================================================================== 2 + 3. SERVER SETUP (Java)
P.rep('''          "public java.util.ArrayList fT;", "public java.util.ArrayList fA;", "public java.util.ArrayList fW;"):''',
      '''          "public java.util.ArrayList fT;", "public java.util.ArrayList fA;", "public java.util.ArrayList fW;",
          "public int rowSz;", "public java.util.HashSet boxRows;"):   # 0.3.36: the mod view's grow tier + its rows with a text box''')
# ---- 0.3.36 (critic 1): a mod row's own buttons carry ONLY that row's box (not every box of the view: the payload grew rows x boxes);
# crumbs / categories / footer / picker carry the first ADM_MFIELDS boxes (drawMod)
P.rep('''public void bindEnter(@UEB@ ev, String id, String a) {
  ev.addEventBinding(@BT@.Validating, "#" + id, evd(a), false);
}""")''', '''public void bindEnter(@UEB@ ev, String id, String a) {
  ev.addEventBinding(@BT@.Validating, "#" + id, evd(a), false);
}""")
M(apg, r"""
public @EVD@ evdRow(String a, int r) {
  @EVD@ d = @EVD@.of("a", a);
  if (this.boxRows != null && this.boxRows.contains(Integer.valueOf(r))) d = d.append(at("V" + r), "#SkyyAdmVal" + r + ".Value");
  return d;
}""")
M(apg, r"""
public void bindR(@UEB@ ev, int r, String id, String a) {
  ev.addEventBinding(@BT@.Activating, "#" + id, evdRow(a, r));
}""")
M(apg, r"""
public void bindEnterR(@UEB@ ev, int r, String id, String a) {
  ev.addEventBinding(@BT@.Validating, "#" + id, evdRow(a, r), false);
}""")
M(apg, r"""
public static int catFit() {
  return (@MD@.ADM_ROWW - 150 - 5 - 150 - 16 + 5) / (@MD@.ADM_CATMIN + 5);
}""")''')
# ---- the crumbs (+ a mod's categories), fit, the frame, the tail; tabRow went (no in-body tab rows)
P.rep(cut('''M(apg, r"""
public java.util.ArrayList crumbs() {''', '''  bind(ev, "SkyyAdmTab" + i, act + i);
}""")'''), r'''M(apg, r"""
public java.util.ArrayList crumbs() {
  java.util.ArrayList c = new java.util.ArrayList();
  String v = this.view == null ? "list" : this.view;
  boolean conf = v.equals("confirm");
  boolean lst = v.equals("list") || this.locked;
  c.add(new String[] { "All mods", lst || conf ? null : "amods", lst ? "1" : "0", "150", "0" });
  if (lst) {
    if (!this.locked) c.add(new String[] { "Admin", "aops", "0", "150", "5" });   // 0.3.36: the Admin page (was a button in the search row)
    return c;
  }
  if (this.mod != null && !v.equals("log") && !(v.equals("io") && this.ioAll)) {
    boolean here = v.equals("mod");
    String nm = this.mod.startsWith("Skyy") && this.mod.length() > 4 ? this.mod.substring(4) : this.mod;
    c.add(new String[] { nm, here || conf ? null : "aback", here ? "1" : "0", "150", "5" });
    if (here) {
      Object[] h = hdr(this.mod);
      int nc = catIds(h).length;
      if (nc > 1 && nc <= catFit()) {                 // more than fit at ADM_CATMIN px: the in-page category picker (drawMod)
        int tw = (@MD@.ADM_ROWW - 150 - 5 - 150 - 16 - 5 * (nc - 1)) / nc;
        if (tw > 150) tw = 150;
        if (tw < @MD@.ADM_CATMIN) tw = @MD@.ADM_CATMIN;
        for (int i = 0; i < nc; i++) {
          boolean sel = i == this.cat;
          c.add(new String[] { catLabel(h, i), sel ? null : "atab" + i, sel ? "1" : "0", String.valueOf(tw), i == 0 ? "16" : "5", "cat" });
        }
      }
    }
  }
  String w = null;
  if (v.equals("table")) w = "Table";
  else if (v.equals("hist")) w = "History";
  else if (v.equals("io")) w = "Export";
  else if (v.equals("log")) w = "Changes";
  else if (conf) w = "Confirm";
  if (w != null) c.add(new String[] { w, null, "1", "150", "5" });
  return c;
}""")
M(apg, r"""
public static boolean crumbAct(String a) {
  return "amods".equals(a) || "aback".equals(a) || "amenu".equals(a);
}""")
# 0.3.36 (task 3, long crumb names): a text fitted to room px - whole when the label can shrink it to fit (12 px, the kit small button's
# MinShrinkTextToFitFontSize; ADM_CW = the client's glyph widths x 100 at 12 px, capitals), else cut with ... (b.set: the dots are not an
# inline character)
M(apg, r"""
public static int cw(char c) {
  char u = Character.toUpperCase(c);
  int k = u - 32;
  if (k < 0 || k >= @MD@.ADM_CW.length) return @MD@.ADM_CWMAX;
  return @MD@.ADM_CW[k];
}""")
M(apg, r"""
public static String fit(String s, int room) {
  if (s == null) return "";
  int lim = room * 100;
  int tot = 0;
  for (int i = 0; i < s.length(); i++) tot = tot + cw(s.charAt(i));
  if (tot <= lim) return s;
  int dots = 3 * cw('.');
  StringBuilder sb = new StringBuilder();
  int acc = 0;
  for (int i = 0; i < s.length(); i++) {
    int x = cw(s.charAt(i));
    if (acc + x + dots > lim) break;
    acc = acc + x;
    sb.append(s.charAt(i));
  }
  return sb.toString().trim() + "...";
}""")
M(apg, r"""
public static String crumbBtn(String id, int w, boolean sel) {
  return "TextButton #" + id + " { Anchor: (Width: " + w + ", Height: " + @MD@.ADM_SUBH + "); Padding: (Horizontal: " + @MD@.ADM_CRPAD + "); Text: \"\"; " + (sel ? @MD@.ADM_SUBSEL : @MD@.ADM_SUBN) + " }";
}""")
# the frame: the hub page, the crumbs (+ categories) in the sub-tab row (SkyyAdmCrumb<i>: 0.3.35's SkyyAdmCr<i> were the ids of a choice
# row's > button too), the title line beside them - or, when a mod's categories fill the row, the body's first line - and the body group
M(apg, r"""
public void frame(@UCB@ b, String title, String sub) {
""" + "\n".join("  " + ln for ln in ADM_HUB_JAVA.split("\n")) + r"""
  java.util.ArrayList cr = crumbs();
  int used = 0;
  boolean cats = false;
  for (int i = 0; i < cr.size(); i++) {
    String[] c = (String[]) cr.get(i);
    int w = Integer.parseInt(c[3]);
    int g = i > 0 ? Integer.parseInt(c[4]) : 0;
    if (g > 0) { b.appendInline("#SkyyAdmHSub", spc(g, @MD@.ADM_SUBH)); used = used + g; }
    b.appendInline("#SkyyAdmHSub", crumbBtn("SkyyAdmCrumb" + i, w, "1".equals(c[2])));
    b.set("#SkyyAdmCrumb" + i + ".Text", fit(c[0], w - 2 * @MD@.ADM_CRPAD - 2));
    used = used + w;
    if (c.length > 5) cats = true;
  }
  if (!cats) b.appendInline("#SkyyAdmHSub", "Label #SkyyAdmSub { Anchor: (Width: " + (@MD@.ADM_ROWW - used - 12) + ", Height: 32, Left: 12); Text: \"\"; Style: " + @MD@.ADM_SUBSTYLE + "; }");
  b.appendInline("#SkyyAdm", @MD@.UI_ABODY);
  if (cats) b.appendInline("#SkyyAdmBody", @MD@.UI_ASUB);
  String t = title == null ? "" : title;
  if (t.startsWith(@MD@.ADM_PREFIX)) t = t.substring(@MD@.ADM_PREFIX.length());   // the Server Setup tab already names the page
  String s = sub == null ? "" : sub;
  b.set("#SkyyAdmSub.Text", @MU@.clip(s.length() == 0 ? t : t + "   -   " + s, @MD@.ADM_SUBMAX));
}""")
M(apg, r"""
public void fReset() {
  this.fT = new java.util.ArrayList();
  this.fA = new java.util.ArrayList();
  this.fW = new java.util.ArrayList();
}""")
M(apg, r"""
public void foot(String text, String act, int w) {
  this.fT.add(text);
  this.fA.add(act);
  this.fW.add(Integer.valueOf(w));
}""")
M(apg, r"""
public void tail(@UCB@ b, @UEB@ ev) {
  int k = this.statusKind;
  if (k < 0 || k > 3) k = 0;
  java.util.ArrayList cr = crumbs();
  for (int i = 0; i < cr.size(); i++) {
    String[] c = (String[]) cr.get(i);
    if (c[1] != null) bind(ev, "SkyyAdmCrumb" + i, c[1]);      // with every text box of the view (bind = evd): no typed value is lost
  }
  int total = 0;
  int nb = 0;
  for (int i = 0; i < this.fW.size(); i++) {
    if (crumbAct((String) this.fA.get(i))) continue;
    total = total + ((Integer) this.fW.get(i)).intValue() + (nb > 0 ? 8 : 0);
    nb++;
  }
  int sw = @MD@.ADM_ROWW - total - 10;
  if (sw < 200) { @MU@.warn("server setup footer is " + total + " px wide"); sw = 200; }
  String sst = k == 1 ? @MD@.ADM_ST1 : (k == 2 ? @MD@.ADM_ST2 : (k == 3 ? @MD@.ADM_ST3 : @MD@.ADM_ST0));
  b.appendInline("#SkyyAdmHFoot", "Label #SkyyAdmStatus { Anchor: (Width: " + sw + ", Height: 48); Text: \"\"; Style: " + sst + "; }");
  b.set("#SkyyAdmStatus.Text", firstLine(this.status));
  b.appendInline("#SkyyAdmHFoot", spc(10, 48));
  int j = 0;
  for (int i = 0; i < this.fT.size(); i++) {
    if (crumbAct((String) this.fA.get(i))) continue;
    if (j > 0) b.appendInline("#SkyyAdmHFoot", spc(8, 48));
    String id = "SkyyAdmF" + i;
    b.appendInline("#SkyyAdmHFoot", btn(id, ((Integer) this.fW.get(i)).intValue(), 48, (String) this.fT.get(i), @MD@.ADM_BS));
    bind(ev, id, (String) this.fA.get(i));
    j++;
  }
  @PKG@.MenuHub.ensure(me());   // 0.3.28: every view ends here (tail) - the hub tab strip of Settings > Server Setup
  """ + ADM_HUB_BUILD + r"""
}""")
# 0.3.36: the in-page picker (the change log's mod filter, the history's file filter): <label>  <  <the picked name (k of n)>  >
M(apg, r"""
public void picker(@UCB@ b, @UEB@ ev, String label, String shown, String prevAct, String nextAct) {
  b.appendInline("#SkyyAdmBody", @MD@.UI_APICK);
  b.appendInline("#SkyyAdmPick", spc(14, 50));
  b.appendInline("#SkyyAdmPick", @MD@.UI_APICKL);
  b.set("#SkyyAdmPickL.Text", label);
  b.appendInline("#SkyyAdmPick", btn("SkyyAdmPickPrev", 60, 50, "<", @MD@.ADM_BS));
  b.appendInline("#SkyyAdmPick", spc(6, 50));
  b.appendInline("#SkyyAdmPick", @MD@.UI_APICKV);
  b.set("#SkyyAdmPickV.Text", shown);
  b.appendInline("#SkyyAdmPick", spc(6, 50));
  b.appendInline("#SkyyAdmPick", btn("SkyyAdmPickNext", 60, 50, ">", @MD@.ADM_BS));
  bind(ev, "SkyyAdmPickPrev", prevAct);
  bind(ev, "SkyyAdmPickNext", nextAct);
}""")''')


def edit_block(start, end, pairs, what):
    """cut [start .. end], apply the (old, new) pairs (each old exactly once) and rep it"""
    old = cut(start, end)
    new = old
    for o_, n_ in pairs:
        assert new.count(o_) == 1, "%s: %s" % (what, o_[:90])
        new = new.replace(o_, n_)
    P.rep(old, new)


# ---- the mod list: one scroll list, grow rows; the Admin button is the Admin crumb now
edit_block('''public void drawList(@UCB@ b, @UEB@ ev) {''', '''  foot("Close", "aclose", 120);
  tail(b, ev);
}""")''', (
    ('''  int per = @MD@.ADM_LROWS;
  int pages = lr.size() <= 0 ? 1 : (lr.size() + per - 1) / per;
  if (this.listPage >= pages) this.listPage = pages - 1;
  if (this.listPage < 0) this.listPage = 0;
''', '''  this.listPage = 0;                                     // 0.3.36: one scroll list (no pages)
'''),
    ('''  b.appendInline("#SkyyAdmSearch", btn("SkyyAdmOps", 130, 50, "Admin", @MD@.ADM_BS));
  bind(ev, "SkyyAdmOps", "aops");
  b.appendInline("#SkyyAdmSearch", spc(10, 50));
  field(b, "#SkyyAdmSearch", "SkyyAdmFind", 520, 50, 60, q, "search settings and editors");''',
     '''  field(b, "#SkyyAdmSearch", "SkyyAdmFind", 660, 50, 60, q, "search settings and editors");   // 0.3.36: Admin = a crumb now'''),
    ('''  this.listMods = new String[per];
  this.listReload = new String[per];
  this.listJump = new String[per];
  for (int r = 0; r < per; r++) {
    int k = this.listPage * per + r;
    if (k >= lr.size()) break;
    String[] e = (String[]) lr.get(k);''', '''  int nl = lr.size();
  this.listMods = new String[nl];
  this.listReload = new String[nl];
  this.listJump = new String[nl];
  int sz = @PKG@.HubBar.growSize(nl, @MD@.ADM_IN_LIST, @MD@.ADM_RH_L, 6);   // Skyy rule 7: a short list fills its room
  for (int r = 0; r < nl; r++) {
    String[] e = (String[]) lr.get(r);'''),
    ('''    b.appendInline("#SkyyAdmLRows", @MD@.UI_ALROW[r]);
    b.appendInline(rsel, spc(14, 52));
    b.appendInline(rsel, @MD@.UI_ALTXT[r]);
    b.appendInline("#SkyyAdmLTxt" + r, @MD@.UI_ALNAME[r]);
    b.appendInline("#SkyyAdmLTxt" + r, "1".equals(e[5]) ? @MD@.UI_ALDESCRED[r] : @MD@.UI_ALDESC[r]);''',
     '''    b.appendInline("#SkyyAdmLRows", "Group #SkyyAdmLRow" + r + @MD@.UI_ALROWB[sz]);
    b.appendInline(rsel, spc(14, 52));
    b.appendInline(rsel, @MD@.UI_ALTXTA + r + @MD@.UI_ALTXTB);
    b.appendInline("#SkyyAdmLTxt" + r, @MD@.UI_ALNAMEA + r + @MD@.UI_ALNAMEB);
    b.appendInline("#SkyyAdmLTxt" + r, "1".equals(e[5]) ? @MD@.UI_ALDESCREDA + r + @MD@.UI_ALDESCREDB : @MD@.UI_ALDESCA + r + @MD@.UI_ALDESCB);'''),
    ('''  fReset();
  if (pages > 1) { foot("< Prev", "aprev", 120); foot("Next >", "anext", 120); }
  foot("Changes", "achanges", 150);''', '''  fReset();
  foot("Changes", "achanges", 150);''')), "drawList")

# ---- a mod's row: the pieces as <head> + r + <tail>, the row group at the view's grow tier
_dr = cut('''public void drawRow(@UCB@ b, @UEB@ ev, Object[] h, int i, int r, boolean edit, boolean ok, String q) {''', '''  b.appendInline("#SkyyAdmRows", @MD@.UI_AGAP6);
}""")''')
_dr2 = _dr.replace('''  b.appendInline("#SkyyAdmRows", @MD@.UI_AROW[r]);''',
                   '''  b.appendInline("#SkyyAdmRows", "Group #SkyyAdmRow" + r + @MD@.UI_AROWB[this.rowSz]);   // 0.3.36: the grow tier (drawMod)''')
_dr2 = _dr2.replace("bind(ev, ", "bindR(ev, r, ").replace("bindEnter(ev, ", "bindEnterR(ev, r, ")
assert _dr2.count("bindR(ev, r, ") >= 10 and "bind(ev" not in _dr2
for _nm in ("ALINE", "ANAME", "AW", "ARO", "ACHV", "AHELP", "ADESC"):
    assert ("@MD@.UI_%s[r]" % _nm) in _dr2, _nm
    _dr2 = _dr2.replace("@MD@.UI_%s[r]" % _nm, "@MD@.UI_%sA + r + @MD@.UI_%sB" % (_nm, _nm))
assert "@MD@.UI_" not in "".join(re.findall(r"@MD@\.UI_\w+\[r\]", _dr2))
P.rep(_dr, _dr2)

# ---- a mod: one scroll list of the category's rows (grow rows), the categories in the sub-tab row (crumbs), no pages
edit_block('''public void drawMod(@UCB@ b, @UEB@ ev) {''', '''  foot("Close", "aclose", 100);
  tail(b, ev);
}""")''', (
    ('''  int[] vis = visible(h);
  int per = @MD@.ADM_ROWS;
  int pages = vis.length <= 0 ? 1 : (vis.length + per - 1) / per;
  if (this.modPage >= pages) this.modPage = pages - 1;
  if (this.modPage < 0) this.modPage = 0;
  evReset();
  this.rowKeys = new String[per];
  for (int r = 0; r < per; r++) {
    int k = this.modPage * per + r;
    if (k >= vis.length) break;
    Object[] w = rowAt(h, vis[k]);''', '''  int[] vis = visible(h);
  int nv = vis.length;
  this.modPage = 0;                                      // 0.3.36: one scroll list of the category (no pages)
  evReset();
  this.rowKeys = new String[nv];
  this.boxRows = new java.util.HashSet();
  int nbox = 0;
  for (int r = 0; r < nv; r++) {
    Object[] w = rowAt(h, vis[r]);'''),
    ('''    if (ok && edit && !hasFlag(w, "ro") && typed(rv(w, 3))) evField("V" + r, "SkyyAdmVal" + r);
  }''', '''    if (ok && edit && !hasFlag(w, "ro") && typed(rv(w, 3))) {
      this.boxRows.add(Integer.valueOf(r));                // its own buttons carry its box (bindR)
      if (nbox < @MD@.ADM_MFIELDS) evField("V" + r, "SkyyAdmVal" + r);   // crumbs / footer: the first ADM_MFIELDS boxes
      nbox++;
    }
  }'''),
    ('''  b.appendInline("#SkyyAdmBody", @MD@.UI_ATABS0);
  if (nCat > 8) b.appendInline("#SkyyAdmBody", @MD@.UI_ATABS1);
  for (int i = 0; i < nCat && i < 16; i++) tabRow(b, ev, i, catLabel(h, i), i == this.cat, "atab");
  b.appendInline("#SkyyAdmBody", @MD@.UI_AGAP8);
  b.appendInline("#SkyyAdmBody", @MD@.UI_AHEAD);
  b.appendInline("#SkyyAdmBody", @MD@.UI_AROWS);
  String q = this.search == null ? "" : this.search.trim();
  for (int r = 0; r < per; r++) {
    int k = this.modPage * per + r;
    if (k >= vis.length) break;
    drawRow(b, ev, h, vis[k], r, edit, ok, q);
  }''', '''  // 0.3.36: the categories are in the sub-tab row (crumbs(): All mods | <mod> | <category ...>) - no in-body tab rows
  boolean catPick = nCat > catFit();                     // critic 2: too many categories for the sub row -> the in-page picker
  if (catPick) picker(b, ev, "Category", catLabel(h, this.cat) + "  (" + (this.cat + 1) + " of " + nCat + ")", "cfprev", "cfnext");
  b.appendInline("#SkyyAdmBody", @MD@.UI_AHEAD);
  b.appendInline("#SkyyAdmBody", catPick ? @MD@.UI_AROWSP : @MD@.UI_AROWS);
  String q = this.search == null ? "" : this.search.trim();
  this.rowSz = @PKG@.HubBar.growSize(nv, catPick ? @MD@.ADM_IN_MODP : @MD@.ADM_IN_MOD, @MD@.ADM_RH_M, 6);   // Skyy rule 7: a short category fills its room
  for (int r = 0; r < nv; r++) drawRow(b, ev, h, vis[r], r, edit, ok, q);'''),
    ('''  b.set("#SkyyAdmHead.Text", catLabel(h, this.cat) + "   -   " + n + (n == 1 ? " setting" : " settings")
      + (pages > 1 ? "   -   page " + (this.modPage + 1) + " of " + pages : "") + (adv > 0 ? "   -   " + adv + " advanced hidden" : ""));''',
     '''  b.set("#SkyyAdmHead.Text", catLabel(h, this.cat) + "   -   " + n + (n == 1 ? " setting" : " settings")
      + (adv > 0 ? "   -   " + adv + " advanced hidden" : "") + (nbox > @MD@.ADM_MFIELDS ? "   -   past box " + @MD@.ADM_MFIELDS + ", press its Set" : ""));'''),
    ('''  fReset();
  if (pages > 1) { foot("< Prev", "aprev", 90); foot("Next >", "anext", 90); }
  foot("History", "ahist", 120);''', '''  fReset();
  foot("History", "ahist", 120);''')), "drawMod")

# ---- a table: one scroll list (grow rows); an editable one draws at most ADM_TFIELDS boxes (every click carries every box), the rest by
# the filter; a view-only one at most ADM_TMAX rows
edit_block('''public void drawTable(@UCB@ b, @UEB@ ev) {''', '''  foot("Close", "aclose", 110);
  tail(b, ev);
}""")''', (
    ('''  int per = @MD@.ADM_ROWS;
  int pages = eks.size() <= 0 ? 1 : (eks.size() + per - 1) / per;
  if (this.tPage >= pages) this.tPage = pages - 1;
  if (this.tPage < 0) this.tPage = 0;
  boolean typeAdd''', '''  int per = eks.size();                                  // 0.3.36: one scroll list (no pages), capped:
  if (edit && cols.length > 0) { if (per > @MD@.ADM_TFIELDS / cols.length) per = @MD@.ADM_TFIELDS / cols.length; }
  else if (per > @MD@.ADM_TMAX) per = @MD@.ADM_TMAX;
  this.tPage = 0;
  boolean typeAdd'''),
    ('''  for (int r = 0; r < per; r++) {
    int k = this.tPage * per + r;
    if (k >= eks.size()) break;
    this.tKeys[r] = (String) eks.get(k);
    this.tVals[r] = (String) evs.get(k);''', '''  for (int r = 0; r < per; r++) {
    this.tKeys[r] = (String) eks.get(r);
    this.tVals[r] = (String) evs.get(r);'''),
    ('''      + (flt.length() > 0 ? " match" : "") + (pages > 1 ? "   -   page " + (this.tPage + 1) + " of " + pages : ""));''',
     '''      + (flt.length() > 0 ? " match" : "") + (per < n ? "   -   " + per + " shown, the filter finds the rest" : ""));
  if (per < n && this.status.length() == 0) setStatus("Showing " + per + " of " + n + " - type in the filter to find the rest.", 2);   // critic 3'''),
    ('''  b.appendInline("#SkyyAdmBody", @MD@.UI_ATROWS);
  boolean canRemove = edit && (itemsMode || !mode.equals("none"));''', '''  b.appendInline("#SkyyAdmBody", typeAdd || heldAdd ? @MD@.UI_ATROWSA : @MD@.UI_ATROWSB);
  boolean canRemove = edit && (itemsMode || !mode.equals("none"));
  int sz = @PKG@.HubBar.growSize(per, typeAdd || heldAdd ? @MD@.ADM_IN_TABLEADD : @MD@.ADM_IN_TABLE, @MD@.ADM_RH_T, 6);'''),
    ('''    b.appendInline("#SkyyAdmTRows", @MD@.UI_ATROW[r]);
    b.appendInline(rsel, spc(14, 52));
    b.appendInline(rsel, @MD@.UI_ATKEY[r]);''', '''    b.appendInline("#SkyyAdmTRows", "Group #SkyyAdmTRow" + r + @MD@.UI_ATROWB[sz]);
    b.appendInline(rsel, spc(14, 52));
    b.appendInline(rsel, @MD@.UI_ATKEYA + r + @MD@.UI_ATKEYB);'''),
    ('''    b.appendInline(rsel, @MD@.UI_ATCELLS[r]);''', '''    b.appendInline(rsel, @MD@.UI_ATCELLSA + r + @MD@.UI_ATCELLSB);'''),
    ('''  fReset();
  if (pages > 1) { foot("< Prev", "aprev", 120); foot("Next >", "anext", 120); }
  if (itemsMode && edit)''', '''  fReset();
  if (itemsMode && edit)''')), "drawTable")

# ---- the change log: the mod filter = the in-page picker (no tab rows), one scroll list of the newest ADM_GMAX changes (grow rows)
edit_block('''public void drawLog(@UCB@ b, @UEB@ ev) {''', '''  foot("Close", "aclose", 120);
  tail(b, ev);
}""")''', (
    ('''  int per = @MD@.ADM_GROWS;
  int pages = all.size() <= 0 ? 1 : (all.size() + per - 1) / per;
  if (this.logPage >= pages) this.logPage = pages - 1;
  if (this.logPage < 0) this.logPage = 0;
''', '''  int per = all.size() > @MD@.ADM_GMAX ? @MD@.ADM_GMAX : all.size();   // 0.3.36: one scroll list, the newest ADM_GMAX (no pages)
  this.logPage = 0;
  int ti = 0;
  for (int i = 0; i < tabs.length; i++) if (tabs[i].equals(this.logMod)) ti = i;
'''),
    ('''  b.appendInline("#SkyyAdmBody", @MD@.UI_ATABS0);
  if (tabs.length > 8) b.appendInline("#SkyyAdmBody", @MD@.UI_ATABS1);
  for (int i = 0; i < tabs.length && i < 16; i++) {
    String lbl = i == 0 ? "All" : hs((Object[]) hdrs.get(tabs[i]), 2);
    tabRow(b, ev, i, lbl, tabs[i].equals(this.logMod), "ltab");
  }
  b.appendInline("#SkyyAdmBody", @MD@.UI_AHEAD);
  String scope = this.logMod.length() == 0 ? "All mods" : hs((Object[]) hdrs.get(this.logMod), 2);
  b.set("#SkyyAdmHead.Text", scope + "   -   " + all.size() + (all.size() == 1 ? " change" : " changes") + (pages > 1 ? "   -   page " + (this.logPage + 1) + " of " + pages : ""));
  b.appendInline("#SkyyAdmBody", @MD@.UI_AGROWS);
  this.logShown = new java.util.ArrayList();
  for (int r = 0; r < per; r++) {
    int k = this.logPage * per + r;
    if (k >= all.size()) break;
    String s = (String) all.get(k);''', '''  String scope = this.logMod.length() == 0 ? "All mods" : hs((Object[]) hdrs.get(this.logMod), 2);
  picker(b, ev, "Show the changes of", scope + "  (" + (ti + 1) + " of " + tabs.length + ")", "lfprev", "lfnext");   // 0.3.36: no tab rows
  b.appendInline("#SkyyAdmBody", @MD@.UI_AHEAD);
  b.set("#SkyyAdmHead.Text", scope + "   -   " + all.size() + (all.size() == 1 ? " change" : " changes") + (per < all.size() ? "   -   the newest " + per + " shown" : ""));
  b.appendInline("#SkyyAdmBody", @MD@.UI_AGROWS);
  this.logShown = new java.util.ArrayList();
  int sz = @PKG@.HubBar.growSize(per, @MD@.ADM_IN_LOG, @MD@.ADM_RH_G, 6);
  for (int r = 0; r < per; r++) {
    String s = (String) all.get(r);'''),
    ('''    b.appendInline("#SkyyAdmGRows", @MD@.UI_AGROW[r]);
    b.appendInline(rsel, spc(14, 40));
    b.appendInline(rsel, @MD@.UI_AGTXT[r]);''', '''    b.appendInline("#SkyyAdmGRows", "Group #SkyyAdmGRow" + r + @MD@.UI_AGROWB[sz]);
    b.appendInline(rsel, spc(14, 40));
    b.appendInline(rsel, @MD@.UI_AGTXTA + r + @MD@.UI_AGTXTB);'''),
    ('''  fReset();
  if (pages > 1) { foot("< Prev", "aprev", 120); foot("Next >", "anext", 120); }
  foot("Refresh", "arefresh", 130);''', '''  fReset();
  foot("Refresh", "arefresh", 130);''')), "drawLog")

# ---- the history: the file filter = the in-page picker (files > 1), one scroll list of the versions (grow rows), the preview below
edit_block('''public void drawHist(@UCB@ b, @UEB@ ev) {''', '''  foot("Close", "aclose", 120);
  tail(b, ev);
}""")''', (
    ('''  boolean prev = this.histPreview != null;
  int per = prev ? 4 : @MD@.ADM_HROWS;
  int pages = lines.size() <= 0 ? 1 : (lines.size() + per - 1) / per;
  if (this.histPage >= pages) this.histPage = pages - 1;
  if (this.histPage < 0) this.histPage = 0;''', '''  boolean prev = this.histPreview != null;
  int per = lines.size();                                // 0.3.36: one scroll list (no pages)
  this.histPage = 0;'''),
    ('''  if (fs.length > 1) {
    b.appendInline("#SkyyAdmBody", @MD@.UI_ATABS0);
    tabRow(b, ev, 0, "All files", this.histFile.length() == 0, "htab");
    for (int i = 0; i < fs.length && i < 7; i++) tabRow(b, ev, i + 1, baseName(fs[i]), fs[i].equals(this.histFile), "htab");
  }''', '''  if (fs.length > 1) {                                   // 0.3.36: the in-page picker (no tab row)
    int fi = 0;
    for (int i = 0; i < fs.length; i++) if (fs[i].equals(this.histFile)) fi = i + 1;
    picker(b, ev, "Show the versions of", (fi == 0 ? "All files" : baseName(this.histFile)) + "  (" + (fi + 1) + " of " + (fs.length + 1) + ")", "hfprev", "hfnext");
  }'''),
    ('''      + (pages > 1 ? "   -   page " + (this.histPage + 1) + " of " + pages : ""));
  b.appendInline("#SkyyAdmBody", prev ? @MD@.UI_AHROWS4 : @MD@.UI_AHROWS8);
  this.histIds = new String[@MD@.ADM_HROWS];
  for (int r = 0; r < per; r++) {
    int k = this.histPage * per + r;
    if (k >= lines.size()) break;
    String[] f = (String[]) lines.get(k);''', '''      );
  b.appendInline("#SkyyAdmBody", prev ? @MD@.UI_AHROWSP : @MD@.UI_AHROWS);
  this.histIds = new String[per];
  int sz = @PKG@.HubBar.growSize(per, prev ? @MD@.ADM_IN_HISTPREV : @MD@.ADM_IN_HIST, @MD@.ADM_RH_H, 6);
  for (int r = 0; r < per; r++) {
    String[] f = (String[]) lines.get(r);'''),
    ('''    b.appendInline("#SkyyAdmHRows", @MD@.UI_AHROW[r]);
    b.appendInline(rsel, spc(14, 44));
    b.appendInline(rsel, @MD@.UI_AHTXT[r]);''', '''    b.appendInline("#SkyyAdmHRows", "Group #SkyyAdmHRow" + r + @MD@.UI_AHROWB[sz]);
    b.appendInline(rsel, spc(14, 44));
    b.appendInline(rsel, @MD@.UI_AHTXTA + r + @MD@.UI_AHTXTB);'''),
    ('''  fReset();
  if (pages > 1) { foot("< Prev", "aprev", 120); foot("Next >", "anext", 120); }
  foot("Refresh", "arefresh", 130);''', '''  fReset();
  foot("Refresh", "arefresh", 130);''')), "drawHist")

# ---- export / import: the import files are one scroll list (every file, ADM_FMAX at most)
P.rep('''      : "Files in Skyy_SkyyMenu/imports (" + files.length + ")" + (files.length > @MD@.ADM_FROWS ? " - the first " + @MD@.ADM_FROWS + " by name:" : ":"));
  b.appendInline("#SkyyAdmBody", @MD@.UI_AIOFROWS);
  for (int r = 0; r < files.length && r < @MD@.ADM_FROWS; r++) {
    b.appendInline("#SkyyAdmIoFRows", @MD@.UI_AFROW[r]);
    b.appendInline("#SkyyAdmFRow" + r, spc(14, 42));
    b.appendInline("#SkyyAdmFRow" + r, @MD@.UI_AFTXT[r]);''', '''      : "Files in Skyy_SkyyMenu/imports (" + files.length + ")" + (files.length > @MD@.ADM_FMAX ? " - the first " + @MD@.ADM_FMAX + " by name:" : ":"));
  b.appendInline("#SkyyAdmBody", @MD@.UI_AIOFROWS);    // 0.3.36: one scroll list (every file)
  for (int r = 0; r < files.length && r < @MD@.ADM_FMAX; r++) {
    b.appendInline("#SkyyAdmIoFRows", @MD@.UI_AFROWA + r + @MD@.UI_AFROWB);
    b.appendInline("#SkyyAdmFRow" + r, spc(14, 42));
    b.appendInline("#SkyyAdmFRow" + r, @MD@.UI_AFTXTA + r + @MD@.UI_AFTXTB);''')

# ---- the pickers' clicks (a mod's categories past the sub row, the change log's mod, the history's file); the old tab clicks went
P.rep('''  int t = tailNum(a, "atab");
  if (t >= 0) { this.cat = t; this.modPage = 0; return false; }''', '''  if (a.equals("cfprev") || a.equals("cfnext")) {         // 0.3.36: the category picker (more categories than the sub row holds)
    int nc = catIds(h).length;
    if (nc > 0) this.cat = a.equals("cfnext") ? (this.cat + 1) % nc : (this.cat + nc - 1) % nc;
    return false;
  }
  int t = tailNum(a, "atab");
  if (t >= 0) { this.cat = t; this.modPage = 0; return false; }''')
P.rep('''  int t = tailNum(a, "ltab");
  if (t >= 0) { if (t < this.logTabs.length) this.logMod = this.logTabs[t]; this.logPage = 0; return; }''',
      '''  if (a.equals("lfprev") || a.equals("lfnext")) {         // 0.3.36: the mod picker (All mods, then every mod with changes)
    int nt = this.logTabs == null ? 0 : this.logTabs.length;
    if (nt > 0) {
      int at0 = 0;
      for (int k = 0; k < nt; k++) if (this.logTabs[k].equals(this.logMod)) at0 = k;
      this.logMod = this.logTabs[a.equals("lfnext") ? (at0 + 1) % nt : (at0 + nt - 1) % nt];
    }
    this.logPage = 0;
    return;
  }''')
P.rep('''  int t = tailNum(a, "htab");
  if (t >= 0) { this.histFile = t == 0 || t > this.histFiles.length ? "" : this.histFiles[t - 1]; this.histPage = 0; this.histPreview = null; return; }''',
      '''  if (a.equals("hfprev") || a.equals("hfnext")) {         // 0.3.36: the file picker (All files, then each file)
    int nf = this.histFiles == null ? 0 : this.histFiles.length;
    int at0 = 0;
    for (int k = 0; k < nf; k++) if (this.histFiles[k].equals(this.histFile)) at0 = k + 1;
    int m = nf + 1;
    int nx = a.equals("hfnext") ? (at0 + 1) % m : (at0 + m - 1) % m;
    this.histFile = nx == 0 ? "" : this.histFiles[nx - 1];
    this.histPage = 0;
    this.histPreview = null;
    return;
  }''')

assert P.s.count("registerCommand(") == CMD0 and P.s.count("registerSystem(") == SYS0, "no command / system added in the script text"
# =================================================================================================== 5. VOID CHARMS (coordinator add-on)
# SkyyAccessories 0.5.22 (AP1) replaced /accessories /acc /accbag with /charms (/charm, /ch); its tab is Void Charms. The menu's texts,
# the old tile, the Mods / admin lines and the Admin page's reload row follow. The old tile's saved key stays "accessorybag" (a saved
# tile:accessorybag shortcut keeps working: _tilekey).
P.rep("""ROUND_PINS = {}
# mods a round RETIRES""", """ROUND_PINS = {"SkyyAccessories": ("0.5.21", "0.5.22")}   # 0.3.36: /charms (Void Charms) - deploy together
# mods a round RETIRES""")
P.rep(""""SkyyAccessories": "0.5.5", "SkyyClasses": "0.1.15",""", """"SkyyAccessories": "0.5.22", "SkyyClasses": "0.1.15",""")
P.rep(""""Accessory Bag", "Utility_Bag_Seed"),""", """"Void Charms", "Utility_Bag_Seed"),     # 0.3.36: the icon item's name (was Accessory Bag)""")
P.rep("""    ("main", 5, "Skyy_Menu_Icon_AccessoryBag", "Accessory Bag",                  # 0.3.11: our own icon (was the vanilla Utility_Bag_Seed)
        ["Equip bench accessories and booster accessories - they work while they sit in the bag.", "Command: /accessories (or /acc)"],
        "Click to open!", "cmdc:accessories"),""", """    ("main", 5, "Skyy_Menu_Icon_AccessoryBag", "Void Charms",                    # 0.3.11: our own icon; 0.3.36: Void Charms (/charms)
        ["Equip bench accessories and booster accessories - they work while they sit in Void Charms.", "Command: /charms (or /charm, /ch)"],
        "Click to open!", "cmdc:charms"),""")
P.rep(""""Bench accessories in your Accessory Bag unlock that bench's recipes.",""", """"Bench accessories in your Void Charms unlock that bench's recipes.",""")
P.rep("""{"mod": "SkyyAccessories", "version": MODS_VERSIONS["SkyyAccessories"], "icon": "Utility_Bag_Seed", "check": "accessories",
     "config": "Skyy_SkyyAccessories/config.properties", "reload": "accessories reload", "note": "",""",
      """{"mod": "SkyyAccessories", "version": MODS_VERSIONS["SkyyAccessories"], "icon": "Utility_Bag_Seed", "check": "charms",
     "config": "Skyy_SkyyAccessories/config.properties", "reload": "charms reload", "note": "",   # 0.3.36: /charms (SkyyAccessories 0.5.22)""")
P.rep("""     "admin": ["/accessories reload - (admin) re-read config.properties after hand edits",
               "/accessories give <player> <item> [amount] - (admin) give an accessory",
               "/accessories givetier <player> <line> <rarity> [amount] - (admin)"],""",
      """     "admin": ["/charms reload - (admin) re-read config.properties after hand edits",
               "/charms give <player> <item> [amount] - (admin) give an accessory",
               "/charms givetier <player> <line> <rarity> [amount] - (admin)"],""")
P.rep(""""desc": "Your Accessory Bag: 18 slots""", """"desc": "Void Charms: 18 slots""")
P.rep("""     "commands": ["/accessories (or /acc, /accbag) - open your Accessory Bag",
                  "/accessories lines - every accessory line, its rarities and numbers"]},""",
      """     "commands": ["/charms (or /charm, /ch) - open Void Charms",
                  "/charms lines - every accessory line, its rarities and numbers",
                  "/charms power [name] - your Accessory Power, or pick a Power"]},""")
P.rep("""    (0, "Reload accessories", "accessories reload", "skyyaccessories.admin", "SkyyAccessories", False, "", ""),""",
      """    (0, "Reload charms", "charms reload", "skyyaccessories.admin", "SkyyAccessories", False, "", ""),   # 0.3.36: /charms""")
P.rep("""_set_live = dict(_LIVE)
for _o in OPS:""", """_set_live = dict(ROUND_SET)          # 0.3.36: this round's set (the /charms row needs SkyyAccessories 0.5.22)
for _o in OPS:""")
P.rep("""'Accessory Bag': (0, 5)""", """'Void Charms': (0, 5)""")
P.rep("""Pocket Dimension, Vault, Accessory Bag, the HUD editor,""", """Pocket Dimension, Vault, Void Charms, the HUD editor,""")
P.rep("""(Magic Bags and the Accessory Bag can't be traded)""", """(Magic Bags and Void Charms can't be traded)""")
P.rep("""Pocket Dimension, Vault, Accessory Bag, HUD editor,""", """Pocket Dimension, Vault, Void Charms, HUD editor,""")
P.rep("""MENU_ICON_OF["Shards"] = "Skyy_Menu_Icon_Shards" """, """MENU_ICON_OF["Void Charms"] = "Skyy_Menu_Icon_AccessoryBag"   # 0.3.36: the renamed tile keeps the bag icon (art manifest: Accessory Bag)
MENU_ICON_OF["Shards"] = "Skyy_Menu_Icon_Shards" """)
P.rep("""TILE_TAB = {"yourprofile": "character:stats",""", """_EKEY_KEEP = {"Void Charms": "accessorybag"}   # 0.3.36: a renamed tile keeps its saved key (tile:accessorybag shortcuts stay valid)
_tilekey = lambda n: _EKEY_KEEP.get(n) or re.sub(r"[^a-z0-9]", "", n.lower())
TILE_TAB = {"yourprofile": "character:stats",""")
P.rep("""e[0] == "main" and re.sub(r"[^a-z0-9]", "", e[3].lower()) == _k][0]""", """e[0] == "main" and _tilekey(e[3]) == _k][0]""")
P.rep("""_ekey = lambda n: re.sub(r"[^a-z0-9]", "", n.lower())
E_KEY =""", """_ekey = _tilekey                     # 0.3.36: the saved keys stay (Void Charms = accessorybag)
E_KEY =""")
P.rep("""  add(rows, "Accessory Bag", String.valueOf(""", """  add(rows, "Void Charms", String.valueOf(""")
P.rep("""@PKG@.MenuUtil.clip("Accessory Bag: " + @PKG@.MenuUtil.csvCount(br.get("acc:has:" """, """@PKG@.MenuUtil.clip("Void Charms: " + @PKG@.MenuUtil.csvCount(br.get("acc:has:" """)
P.rep("""skills, trees, class, pets, accessories, collections and profiles.",""", """skills, trees, class, pets, Void Charms, collections and profiles.",""")
assert "tabRow(" not in P.s and "UI_ATABS" not in P.s and "SkyyAdmCr\" + i" not in P.s, "0.3.36: no in-body tab rows, the crumbs renamed"
P.finish()
