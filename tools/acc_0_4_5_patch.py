"""Derive SkyyAccessories/build_skyyaccessories_0.4.5.py from the LIVE 0.4.4 (build_skyyaccessories_0.4.4.py = the tools/deploy_set.py
SET pin; same style as acc_0_4_4_patch.py: rep(old, new) / cut(a, b, new) with asserted anchors; 0.4.4 stays untouched).
Run:  python tools/acc_0_4_5_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.4.5.py   (never --deploy from an agent)

0.4.5 = THE VANILLA UI PASS for the Accessory Bag page (Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them
to look and feel vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md section 7; research/Skyy-UI-Inventory.md 5.1).
LOOK-ONLY RESTYLE: every element id of 0.4.4 (#SkyyAcc, #SkyyAccBonus, #SkyyAccSlot<i>, #SkyyAccUn<i>, #SkyyAccInv<i>, #SkyyAccEq<i>,
#SkyyAccInfo), the two event bindings (un:<i> / eq:<i>, copied lines, asserted), the page id SkyyAccBag, /accessories + aliases, the
permissions, config keys, bag files, bridge keys, every text the page shows (bonusText / pretty / rarityName / campLine / info: the
same Java expressions), invIds and the profile-key check are 0.4.4's. handleDataEvent, carried / takeOne / giveOne / giveBack and
every other class are untouched (asserted: only the AccPage.build block + the new AccPage.infoColor before it, the ready log line,
the header, VERSION and the new kit import change). Not look-only by nature, but not from this patch either: the rebuild compiles
the CURRENT admin config kit tools/skyycfg.py 1.1, while the live 0.4.4 jar was built on 1.0 (CfgFile / CfgFn / CfgRows /
CfgSaveTask; every rebuild of any config-kit mod picks that up).

THE F-STRING PILOT (style guide 8c): 0.4.4's page code lives in non-raw f-strings (page.addMethod(CtNewMethod.make(f\"\"\"...{PKG}...)).
This patch uses recipe A: the old build() block is cut out and replaced through an @@ACCPAGE@@ token (no % / f-string template in this
patch) by Python code that calls the kit when the BUILD runs, gives each piece of emitted Java a name (ACC_TOP_JAVA, ACC_SLOT_JAVA,
ACC_FULL_JAVA, ACC_EMPTY_JAVA, ACC_NONE_JAVA, ACC_INV_JAVA) and interpolates it into the build() f-string as {ACC_..._JAVA}.
Interpolated text is never re-parsed by Python, so the kit's Java literals reach javassist exactly as java_expr / java_append wrote
them (no brace doubling, no backslash escaping); the generated script asserts each named piece is in the method source verbatim.

The new page (1210 x 780, fits 1080; was 640 x 630 flat):
  - the vanilla DECORATED window (page_shell: ContainerHeader title bar with runes, the gold ornaments, ACCESSORY BAG in the 15 px
    Secondary title style, ContainerPatch body, padding 17) - like ItemRepairPage, the vanilla "list of items + an action" page. The
    new root is #SkyyAccF (Anchor Width / Height only); 0.4.4's root #SkyyAcc is now the body.
  - a vanilla well (#SkyyAccTop, WorldEventPanelPage #Summary) with the hint (default label, b.set: it ends with a dot) and the
    live #SkyyAccBonus line (the vanilla property-value colour #b7cedd, 16 px; b.set) - both left-aligned like the #Summary text.
  - two list wells (#SkyyAccCols: #SkyyAccLeft | #SkyyAccRight, 580 + 16 + 580; each the vanilla list well #000000(0.15) with
    padding 4 - WorldEventPanelPage #ListContainer, non-scrolling), each with a vanilla section head (BAG SLOTS / ACCESSORIES AND
    TALISMANS IN YOUR INVENTORY) inside, as the vanilla section labels sit inside the list. At readable text sizes 15 rows no
    longer fit one 980 px column, and a pager would add bindings: two columns keep every row on screen and the bindings unchanged.
  - rows in the vanilla list-row look (WorldEventListRow: a #101925(0.55) row panel with the 4 px #4274a5 status bar, a 40 px item
    icon, the name 18 px bold + the rarity word 15 px in the item's quality colour, 56 px high + 3) and the action outside the panel
    as a small Secondary button (UNEQUIP / EQUIP, 112 x 56, the vanilla light click). Empty slots: a static row panel with a grey
    caption "Empty slot"; no inventory accessories: "None - craft bench accessories and talismans at a Workbench" (0.4.4's words
    without the leading spaces; a margin indents now).
  - a content separator, then #SkyyAccInfo = the kit's status line (16 px bold, centred, wraps to two lines; b.set, same text as
    0.4.4) in the vanilla result colours: green for done (equipped / unequipped / upgraded), red for refused (nothing moved, or an
    item could not be given back), info blue for notes (profile changed) and the Campfire line. 0.4.4's result texts carry no
    +/-/= marks and stay as they are, so AccPage.infoColor(text) picks the colour from the text; this patch asserts the full list
    of result texts handleDataEvent sets, so a changed text stops the next patch until its colour is decided.
  - texts reach the page through b.set (never parsed as markup): safe() now only guards the item ids written INTO the markup
    (ItemId: "..."), so names and results show their commas again (0.4.4 inlined them and had to blank , : ; " { }).
  Fixed widths + Anchor margins + LayoutMode Left / Top only (no FlexWeight, no LayoutMode Center / Right, no WrapMaxLines, nothing
  UNVERIFIED); heights budgeted to fill the body exactly (asserted). Icons are ItemIcon { ItemId } (metadata-free; no ItemGrid).
  No Close button (review fix1b: rejected here): a footer Close needs a new element id, a new binding and a close branch in
  handleDataEvent - not look-only; Esc closes the page as before (CanDismiss), like the Classes 0.1.8 / Profiles 0.1.3 restyles.
KIT-GAPs (composed here from kit calls, tools/skyyui.py unchanged): a fixed-width list row (panel_row / row_text need FlexWeight):
panel(kind "row") + group() + item_icon + Appends.text labels + row_action; the 4 px status bar alone: group(layout=None, extra=
"Background: " + SUI.COLOR["selected"]); a non-scrolling list well: panel(kind "well", pad=SUI.WELL_LIST_PAD); a result line for
texts without +/-/= marks: status_line(color_expr=) + the mod's own infoColor.
Render compare (re-runnable): SkyyAccessories/test_skyyaccessories_0.4.5.py compiles this build() source again with test state and
runs it through the engine's own UICommandBuilder / UIEventBuilder against acc_page_state().
"""
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.4.4.py")
dst = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.4.5.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.4"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


def cut(a, b, new=""):
    """replace everything from anchor a (included) up to anchor b (kept) with new; returns the text that was cut"""
    global s
    assert s.count(a) == 1, "cut start count %d: %s" % (s.count(a), a[:120])
    assert s.count(b) == 1, "cut end count %d: %s" % (s.count(b), b[:120])
    i, j = s.index(a), s.index(b)
    assert i < j, "cut anchors out of order: %s / %s" % (a[:60], b[:60])
    old = s[i:j]
    s = s[:i] + new + s[j:]
    return old


def block(a, b):
    """the text from anchor a (included) to anchor b (excluded) of the CURRENT source (for unchanged-block asserts)"""
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
assert len(BIND0) == 2, BIND0
REG0 = s.count("registerCommand(")
# blocks that must come out of this patch byte-identical (everything but the page look, the header, VERSION, the import and the log line)
KEEP = [block("JP  = \"com.hypixel.hytale.server.core.plugin.JavaPlugin\"", "PAGE_H = 630\n"),
        block("# ---- 0.4 stat talismans in 5 RARITIES", "# ================= AccPage ================="),
        block("# ================= AccPage =================", "page.addMethod(CtNewMethod.make(f\"\"\"\npublic void build("),
        block("# giveBack: 0 = back in the inventory", "  getLogger().at(java.util.logging.Level.INFO).log(\"[SkyyAccessories] {VERSION} ready"),
        block("  {PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());", "jar = os.path.join(HERE, \"SkyyAccessories-%s.jar\" % VERSION)")]

# ---------------------------------------------------------------- header / version
rep('''"""SkyyAccessories 0.4.4 - build script (derived from 0.4.3 by tools/acc_0_4_4_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.4.4.py            -> SkyyAccessories/SkyyAccessories-0.4.4.jar
       python build_skyyaccessories_0.4.4.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.4.4: ADMIN CONFIG IN GAME''', '''"""SkyyAccessories 0.4.5 - build script (derived from 0.4.4 by tools/acc_0_4_5_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.4.5.py            -> SkyyAccessories/SkyyAccessories-0.4.5.jar
       python build_skyyaccessories_0.4.5.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.4.5: THE VANILLA LOOK for the Accessory Bag page (Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them
     to look and feel vanilla"; research/Vanilla-UI-Style-Guide.md; full notes in tools/acc_0_4_5_patch.py). ONLY THE LOOK CHANGED:
     - the page is built from the shared kit tools/skyyui.py when this script runs (SUI.verify() first proves every style value,
       texture and sound against Assets.zip, read-only); the kit id is in the ready log line.
     - the vanilla decorated window (title bar with runes, the gold ornaments, ACCESSORY BAG in the title font), 1210 x 780 (was
       640 x 630): a well with the hint and the live Bonuses line (left-aligned, the vanilla value colour), then two vanilla list
       wells - BAG SLOTS (the slot rows) and the inventory list (up to 6 rows) - with vanilla list rows (row panel, blue status bar,
       40 px item icon, 18 px name + 15 px rarity word in the item's quality colour) and small Secondary UNEQUIP / EQUIP buttons,
       then the result line (the kit's status line: green done, red refused, info blue notes / the Campfire line; AccPage.infoColor
       reads 0.4.4's unchanged result texts).
     - every element id of 0.4.4 (#SkyyAcc is now the window body), the un:<i> / eq:<i> bindings, every text (the same Java
       expressions; b.set, so commas show again - safe() only guards the item ids inside the markup), invIds and the profile-key
       check are 0.4.4's; handleDataEvent and every other class are unchanged. This rebuild compiles the current admin config kit
       tools/skyycfg.py 1.1 (the live 0.4.4 jar was built on 1.0): CfgFile / CfgFn / CfgRows / CfgSaveTask carry 1.1's
       hand-edit table-line checks, reload order and monitor changes (the Talisman bonuses rows + /accessories reload use them).
0.4.4 notes:
0.4.4: ADMIN CONFIG IN GAME''')
rep('VERSION = "0.4.4"\n', 'VERSION = "0.4.5"\n')
rep('''import skyycfg as CFG   # 0.4.4: the admin config kit (research/Server-Setup-Spec.md 1.3-1.4, tools/CONFIG-CONTRACT.md)
''', '''import skyycfg as CFG   # 0.4.4: the admin config kit (research/Server-Setup-Spec.md 1.3-1.4, tools/CONFIG-CONTRACT.md)
import skyyui as SUI    # 0.4.5: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"
SUI.verify()            # proves every vanilla value / texture / sound the page uses against Assets.zip (read-only); stops the build on drift
KIT_ID = SUI.kit_id()   # "skyyui <version> <blob12>" - in the ready log line
''')
rep("PAGE_H = 630\n", "# 0.4.5: the page size is ACC_W x ACC_H (the AccPage look block, built from tools/skyyui.py)\n")
rep('log("[SkyyAccessories] {VERSION} ready - /accessories', 'log("[SkyyAccessories] {VERSION} ready ({KIT_ID}) - /accessories')

# ---------------------------------------------------------------- AccPage.build: keep the Java logic lines, replace the markup
OLD_BUILD = cut('page.addMethod(CtNewMethod.make(f"""\npublic void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{',
                "# giveBack: 0 = back in the inventory", "@@ACCPAGE@@")
# the Java lines of 0.4.4's build() that 0.4.5 keeps VERBATIM (state, profile key, cap rule, loops, bindings, invIds)
KEEP_LINES = [
    "  java.util.UUID u = this.playerRef.getUuid();",
    "  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());",
    "  this.key = {PKG}.AccStore.pkey(u);   // 0.4.1",
    "  String[] s = {PKG}.AccStore.snapshot(u);",
    "  int cap = {PKG}.AccStore.capOf(s);   // 0.4.4",
    "  for (int i = 0; i < s.length; i++) {{",
    "    if (i >= cap && s[i] == null) continue;   // 0.4.4: a slot above this server's limit shows only while something is still in it",
    "    if (s[i] != null) {{",
    '      ev.addEventBinding({BT}.Activating, "#SkyyAccUn" + i, {EVD}.of("a", "un:" + i));',
    "    }} else {{",
    "  java.util.ArrayList inv = player == null ? new java.util.ArrayList() : carried(player);",
    "  this.invIds = new String[inv.size()];",
    "  for (int i = 0; i < inv.size() && i < {INV_ROWS}; i++) {{",
    "    String id = (String) inv.get(i);",
    "    this.invIds[i] = id;",
    '    ev.addEventBinding({BT}.Activating, "#SkyyAccEq" + i, {EVD}.of("a", "eq:" + i));',
]
_old_lines = OLD_BUILD.split(LF)
for _ln in KEEP_LINES:
    assert _old_lines.count(_ln) == 1, "0.4.4 build() line not found exactly once: " + _ln
assert [ln for ln in _old_lines if "ev.addEventBinding(" in ln] == BIND0, "both bindings live in build()"
# the texts 0.4.4 put inline (as safe(...) Java expressions) - 0.4.5 b.sets the SAME expressions, spelled as kit J()s in Python
# ("{PKG}" = '" + PKG + "'). Review fix1b: b.set never parses markup, so safe() (which blanks , : ; " and turns { } into ( ))
# stays only on the two item ids written INTO the markup (ItemId: "..."); the six texts go to the page as they are.
OLD_TEXT_EXPRS = {
    "safe({PKG}.AccDefs.bonusText(s))": 'SUI.J(PKG + ".AccDefs.bonusText(s)"',
    "safe({PKG}.AccDefs.pretty(s[i]))": 'SUI.J(PKG + ".AccDefs.pretty(s[i])"',
    "safe({PKG}.AccDefs.rarityName(s[i]).toUpperCase())": 'SUI.J(PKG + ".AccDefs.rarityName(s[i]).toUpperCase()"',
    "safe({PKG}.AccDefs.pretty(id))": 'SUI.J(PKG + ".AccDefs.pretty(id)"',
    "safe({PKG}.AccDefs.rarityName(id).toUpperCase())": 'SUI.J(PKG + ".AccDefs.rarityName(id).toUpperCase()"',
    "safe(this.info != null && this.info.length() > 0 ? this.info : {PKG}.AccStore.campLine(s))":
        'SUI.J("this.info != null && this.info.length() > 0 ? this.info : " + PKG + ".AccStore.campLine(s)"',
    "{PKG}.AccDefs.rarityColor(s[i])": 'SUI.J(PKG + ".AccDefs.rarityColor(s[i])"',
    "{PKG}.AccDefs.rarityColor(id)": 'SUI.J(PKG + ".AccDefs.rarityColor(id)"',
    "safe(s[i])": 'SUI.J("safe(s[i])"',
    "safe(id)": 'SUI.J("safe(id)"'}
for _e in OLD_TEXT_EXPRS:
    assert _e in OLD_BUILD, "0.4.4 page expression not found: " + _e

NEW = r'''# ================= AccPage look (0.4.5): the vanilla UI kit tools/skyyui.py, called when THIS script runs =================
# research/Vanilla-UI-Style-Guide.md sections 7 + 8c. acc_page_*() build the markup from kit calls (every value proven by SUI.verify() at
# the top of this script). The Java the kit emits gets a name here (ACC_*_JAVA) and is interpolated into the build() f-string below as
# {ACC_..._JAVA}: interpolated text is never re-parsed by Python, so the kit's Java string literals (their escaped quotes, the markup
# braces, the #ids) reach javassist exactly as the kit wrote them - no brace doubling, no escaping (the non-raw f-string pilot).
# ---- ACC PAGE BLOCK START (SkyyAccessories/test_skyyaccessories_0.4.5.py execs this block and ACC_BUILD_SRC below, with SUI verified,
# PKG, CAP, INV_ROWS and the class-name constants defined, and compares the compiled build() with acc_page_state())
ACC_PREFIX = "SkyyAcc"                 # every element id starts with it (the 0.4.4 ids already did); 0.4.4's root #SkyyAcc = the body
ACC_COL_W, ACC_COL_GAP = 580, 16       # two list wells: the bag slots | the accessories in the inventory
ACC_LIST_PAD = SUI.WELL_LIST_PAD       # 4: the vanilla list well's padding (WorldEventPanelPage #ListContainer)
ACC_COL_IN = ACC_COL_W - 2 * ACC_LIST_PAD                                       # 572: the width of a row inside a well
ACC_W = 2 * ACC_COL_W + ACC_COL_GAP + 2 * SUI.CONTENT_PAD                     # 1210
ACC_ROW_H, ACC_ROW_GAP = SUI.ROW_H_READABLE, SUI.ROW_GAP                       # 56 + 3: two readable lines (18 px name, 15 px rarity)
ACC_ACT_W = 112                        # UNEQUIP / EQUIP: a small Secondary row action (vanilla 92; 112 keeps UNEQUIP at 14 px)
ACC_PANEL_W = ACC_COL_IN - 4 - ACC_ACT_W                                       # the row panel; the action sits 4 px right of it
ACC_BAR = 4 + 8                        # the status bar (4 px + 8 px gap, WorldEventListRow)
ACC_ICON, ACC_ICON_BOX = 40, 52        # 40 px item icon in a 52 px box (12 px to the text)
ACC_ROW_PAD = 8                        # row panel padding left / right (WorldEventListRow)
ACC_TEXT_W = ACC_PANEL_W - 2 * ACC_ROW_PAD - ACC_BAR - ACC_ICON_BOX            # 376 (the longest name, a legacy talisman, ~345 px)
ACC_NAME_H, ACC_SUB_H = SUI.fs(14) + 6, SUI.fs(12) + 5                          # 24 + 20 (the kit's row_text heights)
ACC_TEXT_TOP = (ACC_ROW_H - ACC_NAME_H - ACC_SUB_H) // 2                       # 6
ACC_LINE_H = 26                        # hint / bonus lines
ACC_TOP_PAD = 8
ACC_TOP_H = 2 * ACC_LINE_H + 2 * ACC_TOP_PAD                                   # 68: the well on top
ACC_SEC_H = SUI.fs(13) + 10 + 10 + 4   # section head 26 + its margins 10 / 4 (WorldEventSectionLabel)
ACC_COLS_H = 2 * ACC_LIST_PAD + ACC_SEC_H + CAP * (ACC_ROW_H + ACC_ROW_GAP)   # 579: a list well holds its head + CAP slot rows
ACC_SEP_H = 1 + 2 * SUI.SEP_MARGIN     # content separator 1 px, 8 px above and below
ACC_INFO_H = 44                        # the result line: 16 px bold, wraps to two lines
ACC_H = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + ACC_TOP_H + ACC_COLS_H + ACC_SEP_H + ACC_INFO_H     # 780
ACC_HINT = "Bench accessories unlock /craft recipes - talismans add a percent on top of your stats while they sit here."
ACC_EMPTY = "Empty slot"
ACC_NONE = "None - craft bench accessories and talismans at a Workbench"
ACC_INFO_COLOR = "infoColor(this.info)"   # the Java colour expression of the result line (AccPage.infoColor below)
UI_DATA_COLORS = ["#8a97a3"]           # AccDefs.RETIRED_COLOR (0.4.2): a retired accessory's name + rarity word - data, like the rarity colours
assert (ACC_W, ACC_H) == (1210, 780) and ACC_COL_IN == 572 and ACC_TEXT_W == 376 and ACC_TEXT_TOP == 6, (ACC_W, ACC_H, ACC_TEXT_W)
assert ACC_ACT_W - 2 * SUI.BTN_SMALL_PAD >= 64 + 8, "UNEQUIP (64 px at 14 px bold) fits the small button without shrinking"
assert CAP * (ACC_ROW_H + ACC_ROW_GAP) >= INV_ROWS * (ACC_ROW_H + ACC_ROW_GAP) + ACC_ROW_H, "the inventory column fits its rows + the none line"
# AccPage.infoColor: the result line's colour from the result text (0.4.4's texts carry no +/-/= marks and stay unchanged). Vanilla
# success green = done, error red = refused (nothing moved, or an item could not be given back), info blue = a note (the profile
# switched) and the Campfire line shown while no result is set. The patch (tools/acc_0_4_5_patch.py) asserts the full list of texts
# handleDataEvent sets; the harness runs this method on the real texts.
ACC_INFO_COLOR_SRC = """
public static String infoColor(String t) {
  if (t == null || t.length() == 0) return "%(eq)s";
  if (t.startsWith("upgraded to ")) return t.indexOf(" could not be returned") >= 0 ? "%(no)s" : "%(ok)s";
  if (t.startsWith("equipped ") || t.startsWith("unequipped ")) return "%(ok)s";
  if (t.startsWith("your profile changed")) return "%(eq)s";
  return "%(no)s";
}""" % {"ok": SUI.STATUS["+"], "no": SUI.STATUS["-"], "eq": SUI.STATUS["="]}


def acc_page_shell(bonus, info):
    """The window + everything static: the top well (hint, #SkyyAccBonus), the two list wells with their section heads, the separator
    and #SkyyAccInfo (colour = ACC_INFO_COLOR, a J() in the markup). bonus / info = the b.set values (J(java expr) in the build, plain
    text in checks). Returns the Shell; its appends' .sets = hint, bonus, info (in that order)."""
    sh = SUI.page_shell(ACC_PREFIX + "F", ACC_W, ACC_H, "Accessory Bag", body_id=ACC_PREFIX)
    ap, body = sh.appends, sh.body
    ap.append((body, SUI.panel("SkyyAccTop", "well", h=ACC_TOP_H, pad={"horizontal": 8, "vertical": ACC_TOP_PAD})))
    sh.text("SkyyAccTop", "SkyyAccHint", ACC_HINT, "default", h=ACC_LINE_H)             # left-aligned like the vanilla #Summary text
    ap.append(("SkyyAccTop", SUI.label("SkyyAccBonus", "", "propValue", h=ACC_LINE_H, wrap=False)))   # a value, not a result line
    ap.append((body, SUI.group("SkyyAccCols", "Left", h=ACC_COLS_H)))
    ap.append(("SkyyAccCols", SUI.panel("SkyyAccLeft", "well", w=ACC_COL_W, h=ACC_COLS_H, pad=ACC_LIST_PAD)))
    ap.append(("SkyyAccCols", SUI.panel("SkyyAccRight", "well", w=ACC_COL_W, h=ACC_COLS_H, pad=ACC_LIST_PAD, anchor={"left": ACC_COL_GAP})))
    ap.append(("SkyyAccLeft", SUI.section("SkyyAccSlotsH", "Bag slots")))
    ap.append(("SkyyAccRight", SUI.section("SkyyAccInvH", "Accessories and talismans in your inventory")))
    ap.append((body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN})))
    ap.append((body, SUI.status_line("SkyyAccInfo", ACC_INFO_COLOR, h=ACC_INFO_H, wrap=True)))
    ap.sets.append(("SkyyAccBonus", "Text", bonus))
    ap.sets.append(("SkyyAccInfo", "Text", info))
    SUI.fit([ACC_LINE_H, ACC_LINE_H], ACC_TOP_H - 2 * ACC_TOP_PAD, "top well")
    SUI.fit([ACC_COL_W, ACC_COL_GAP, ACC_COL_W], sh.inner_w, "columns")
    SUI.fit([ACC_SEC_H] + [ACC_ROW_H + ACC_ROW_GAP] * CAP, ACC_COLS_H - 2 * ACC_LIST_PAD, "list well")
    SUI.fit([ACC_PANEL_W, 4, ACC_ACT_W], ACC_COL_IN, "row in the well")
    SUI.fit([ACC_ROW_PAD, ACC_BAR, ACC_ICON_BOX, ACC_TEXT_W, ACC_ROW_PAD], ACC_PANEL_W, "row panel")
    left = sh.fit([ACC_TOP_H, ACC_COLS_H, ACC_SEP_H, ACC_INFO_H], "accessory page body")
    assert left == 0 and sh.inner_w == 2 * ACC_COL_W + ACC_COL_GAP, "the body must be filled exactly (no FlexWeight filler): %d px left" % left
    return sh


def acc_page_row_box(ap, col, rid):
    """The row container #<rid> (a bag slot or an inventory row: LayoutMode Left, 56 + 3) in the list well col."""
    ap.append((col, SUI.group(rid, "Left", h=ACC_ROW_H, anchor={"bottom": ACC_ROW_GAP})))


def acc_page_row_full(ap, rid, act_id, act_text, item, name, rarity, colr):
    """A filled row inside #<rid>: the WorldEventListRow look with fixed widths - the row panel #<rid>P (#101925(0.55), padding 8) with
    the status bar, the item icon #<rid>Ic (ItemIcon: the item id only, metadata-free), the name #<rid>Nm (18 px bold) + the rarity
    word #<rid>Rr (15 px), both in the quality colour colr and b.set - then the small Secondary action button act_id."""
    ap.append((rid, SUI.panel(rid + "P", "row", w=ACC_PANEL_W, h=ACC_ROW_H, layout="Left", pad={"left": ACC_ROW_PAD, "right": ACC_ROW_PAD})))
    ap.append((rid + "P", SUI.group(rid + "Bar", None, w=4, anchor={"right": 8}, extra="Background: " + SUI.COLOR["selected"])))
    ap.append((rid + "P", SUI.group(rid + "Ib", None, w=ACC_ICON_BOX, h=ACC_ROW_H)))
    ap.append((rid + "Ib", SUI.item_icon(rid + "Ic", item, ACC_ICON, anchor={"left": 0, "top": (ACC_ROW_H - ACC_ICON) // 2})))
    ap.append((rid + "P", SUI.group(rid + "T", "Top", w=ACC_TEXT_W, h=ACC_ROW_H, pad={"top": ACC_TEXT_TOP})))
    ap.text(rid + "T", rid + "Nm", name, "rowName", h=ACC_NAME_H, col=colr)
    ap.text(rid + "T", rid + "Rr", rarity, "rowSub", h=ACC_SUB_H, col=colr)
    ap.append((rid, SUI.row_action(act_id, act_text, w=ACC_ACT_W)))


def acc_page_row_empty(ap, rid):
    """An empty bag slot inside #<rid>: a static row panel across the well with the grey caption "Empty slot" at the name position."""
    ap.append((rid, SUI.panel(rid + "P", "row", w=ACC_COL_IN, h=ACC_ROW_H, layout="Left", pad={"left": ACC_ROW_PAD, "right": ACC_ROW_PAD})))
    ap.append((rid + "P", SUI.spacer(w=ACC_BAR + ACC_ICON_BOX)))
    ap.append((rid + "P", SUI.label(None, ACC_EMPTY, "caption", w=ACC_COL_IN - 2 * ACC_ROW_PAD - ACC_BAR - ACC_ICON_BOX, h=ACC_ROW_H)))


def acc_page_none():
    """The line under the inventory head when no accessory is carried."""
    return SUI.label(None, ACC_NONE, "caption", h=30, anchor={"left": 2})


def acc_page_state(bonus, info, slots, inv):
    """The whole page for ONE state, as the chunks build() emits in order (each an Appends: its appends, then its b.set lines):
    slots = [(i, None) for an empty shown slot | (i, (item, name, rarity, colour))], inv = [(item, name, rarity, colour), ...] (at
    most INV_ROWS are drawn). Values are plain strings or J(expr, sample); the result line's colour stays the J(ACC_INFO_COLOR).
    Used by the build-time check of sample states below and by SkyyAccessories/test_skyyaccessories_0.4.5.py, which compares these
    chunks with what the compiled build() sends through the engine's UICommandBuilder."""
    sh = acc_page_shell(bonus, info)
    chunks = [sh.appends]
    for i, v in slots:
        rid = "SkyyAccSlot" + str(i)
        box = SUI.Appends()
        acc_page_row_box(box, "SkyyAccLeft", rid)
        chunks.append(box)
        ap = SUI.Appends()
        if v is None:
            acc_page_row_empty(ap, rid)
        else:
            acc_page_row_full(ap, rid, "SkyyAccUn" + str(i), "Unequip", v[0], v[1], v[2], v[3])
        chunks.append(ap)
    if not inv:
        chunks.append(SUI.Appends([("SkyyAccRight", acc_page_none())]))
    for i, v in enumerate(inv[:INV_ROWS]):
        ap = SUI.Appends()
        acc_page_row_box(ap, "SkyyAccRight", "SkyyAccInv" + str(i))
        acc_page_row_full(ap, "SkyyAccInv" + str(i), "SkyyAccEq" + str(i), "Equip", v[0], v[1], v[2], v[3])
        chunks.append(ap)
    return chunks


def acc_page_check(chunks):
    """check_page on a whole state (ids, prefix, no duplicates, every parent created first, every b.set target exists)."""
    whole = SUI.Appends()
    for c in chunks:
        whole += c
    return SUI.check_page(whole, ACC_PREFIX)


def _acc_java(ap, indent, known=()):
    """The Java statements of one Appends (appends, then b.set lines), checked first, indented for the build() source."""
    SUI.check_page(ap, ACC_PREFIX, known_parents=[SUI.render(k) for k in known])
    return LF.join(indent + ln for ln in ap.java("b").split(LF))


LF = chr(10)
_I = SUI.J("i", "0")                   # the loop index of build(); ids like "SkyyAccSlot" + (i) + "Nm"
_SLOT, _INV = "SkyyAccSlot" + _I, "SkyyAccInv" + _I
_Q = SUI.QUALITY["Epic"]               # colour sample of the runtime quality colour (AccDefs.rarityColor)
# the texts: the same Java expressions as 0.4.4, without safe() (b.set never parses markup); safe() stays on the ItemIds (inline markup)
ACC_SH = acc_page_shell(SUI.J(PKG + ".AccDefs.bonusText(s)", "Bonuses - none yet - put talismans in this bag"),
                        SUI.J("this.info != null && this.info.length() > 0 ? this.info : " + PKG + ".AccStore.campLine(s)",
                              "equipped Epic Vitality Talisman"))
SUI.check_page(ACC_SH.appends, ACC_PREFIX)
ACC_TOP_JAVA = LF.join("  " + ln for ln in ACC_SH.java("b").split(LF))
_ap = SUI.Appends()
acc_page_row_box(_ap, "SkyyAccLeft", _SLOT)
ACC_SLOT_JAVA = _acc_java(_ap, "    ", known=["SkyyAccLeft"])
_ap = SUI.Appends()
acc_page_row_full(_ap, _SLOT, "SkyyAccUn" + _I, "Unequip", SUI.J("safe(s[i])", "Skyy_Talisman_Vitality_Epic"),
                  SUI.J(PKG + ".AccDefs.pretty(s[i])", "Epic Vitality Talisman"),
                  SUI.J(PKG + ".AccDefs.rarityName(s[i]).toUpperCase()", "EPIC"),
                  SUI.J(PKG + ".AccDefs.rarityColor(s[i])", _Q))
ACC_FULL_JAVA = _acc_java(_ap, "      ", known=[_SLOT])
_ap = SUI.Appends()
acc_page_row_empty(_ap, _SLOT)
ACC_EMPTY_JAVA = _acc_java(_ap, "      ", known=[_SLOT])
ACC_NONE_JAVA = SUI.java_append("SkyyAccRight", acc_page_none())
_ap = SUI.Appends()
acc_page_row_box(_ap, "SkyyAccRight", _INV)
acc_page_row_full(_ap, _INV, "SkyyAccEq" + _I, "Equip", SUI.J("safe(id)", "Skyy_Accessory_Workbench_T2"),
                  SUI.J(PKG + ".AccDefs.pretty(id)", "Workbench II"),
                  SUI.J(PKG + ".AccDefs.rarityName(id).toUpperCase()", "UNCOMMON"),
                  SUI.J(PKG + ".AccDefs.rarityColor(id)", SUI.QUALITY["Uncommon"]))
ACC_INV_JAVA = _acc_java(_ap, "    ", known=["SkyyAccRight"])
# build-time check of whole sample states: every slot full + 6 inventory rows, all slots empty + no inventory, a lowered cap
_full = ("Skyy_Talisman_Speed_Legendary", "Legendary Speed Talisman", "LEGENDARY", SUI.QUALITY["Legendary"])
_invr = ("Skyy_Accessory_Furnace_T1", "Furnace", "COMMON", SUI.QUALITY["Common"])
for _acc_st in (acc_page_state("Bonuses - +10% Speed", "", [(i, _full) for i in range(CAP)], [_invr] * INV_ROWS),
                acc_page_state("Bonuses - none yet - put talismans in this bag", "", [(i, None) for i in range(CAP)], []),
                acc_page_state("Bonuses - none yet", "bag is full, or the same or a better Speed talisman is already equipped",
                               [(0, _full), (1, None), (7, _full)], [_invr])):
    acc_page_check(_acc_st)
print("accessory page: %d x %d on %s, %d static appends + row templates checked" % (ACC_W, ACC_H, KIT_ID, len(ACC_SH.appends)))
# ---- ACC PAGE BLOCK END
ACC_BUILD_SRC = f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  this.key = {PKG}.AccStore.pkey(u);   // 0.4.1
  String[] s = {PKG}.AccStore.snapshot(u);
  // 0.4.5: the window, the top well (hint + bonuses), the two list wells + heads, the separator and the result line - kit markup
{ACC_TOP_JAVA}
  int cap = {PKG}.AccStore.capOf(s);   // 0.4.4
  for (int i = 0; i < s.length; i++) {{
    if (i >= cap && s[i] == null) continue;   // 0.4.4: a slot above this server's limit shows only while something is still in it
{ACC_SLOT_JAVA}
    if (s[i] != null) {{
{ACC_FULL_JAVA}
      ev.addEventBinding({BT}.Activating, "#SkyyAccUn" + i, {EVD}.of("a", "un:" + i));
    }} else {{
{ACC_EMPTY_JAVA}
    }}
  }}
  java.util.ArrayList inv = player == null ? new java.util.ArrayList() : carried(player);
  this.invIds = new String[inv.size()];
  if (inv.isEmpty()) {ACC_NONE_JAVA}
  for (int i = 0; i < inv.size() && i < {INV_ROWS}; i++) {{
    String id = (String) inv.get(i);
    this.invIds[i] = id;
{ACC_INV_JAVA}
    ev.addEventBinding({BT}.Activating, "#SkyyAccEq" + i, {EVD}.of("a", "eq:" + i));
  }}
}}"""
for _piece in (ACC_TOP_JAVA, ACC_SLOT_JAVA, ACC_FULL_JAVA, ACC_EMPTY_JAVA, ACC_NONE_JAVA, ACC_INV_JAVA):
    assert _piece in ACC_BUILD_SRC, "kit Java changed on its way into the build() source"   # the f-string pilot: verbatim
assert ACC_BUILD_SRC.count("infoColor(this.info)") == 1 and ACC_BUILD_SRC.count("safe(") == 2, "infoColor once; safe() on the 2 ItemIds only"
page.addMethod(CtNewMethod.make(ACC_INFO_COLOR_SRC, page))   # before build() (javassist: methods before their callers)
page.addMethod(CtNewMethod.make(ACC_BUILD_SRC, page))
'''
rep("@@ACCPAGE@@", NEW)

# ---------------------------------------------------------------- self-checks on the generated script
new_lines = s.split(LF)
for _ln in KEEP_LINES:
    assert new_lines.count(_ln) == 1, "0.4.5 build() lost a kept 0.4.4 line: " + _ln
for _e, _py in OLD_TEXT_EXPRS.items():     # the same Java expression, now spelled as a kit J() in Python
    assert s.count(_py) == 1, "0.4.5 dropped a 0.4.4 page expression: %s (%d x %s)" % (_e, s.count(_py), _py)
_blk = s.split("# ---- ACC PAGE BLOCK START")[1].split("page.addMethod(CtNewMethod.make(ACC_BUILD_SRC, page))")[0]
assert _blk.count('SUI.J("safe(') == 2, "safe() stays on the two ItemIds only (b.set texts are never parsed as markup)"
# the result line's colour (AccPage.infoColor) reads 0.4.4's result texts: EVERY text handleDataEvent can set is listed here with the
# colour infoColor gives it. A changed or added text stops this patch until its colour is decided (then update infoColor + this list).
HDE = block("public void handleDataEvent(", "fac.addInterface(")
INFO_SETS = [   # (the assignment as the source spells it, the colour infoColor picks: + green / - red / = info blue)
    ('this.info = "your profile changed - this is the bag of your current profile now";', "="),
    ("this.info = blk;", "-"),                                   # AccStore.moveBlock: "your profile is still loading / not loaded"
    ('this.info = "your inventory is full";', "-"),
    ('this.info = "unequipped " + {PKG}.AccDefs.pretty(give) + ', "+"),
    ("this.info = {PKG}.AccDefs.retiredWhy(id);", "-"),          # "Retired - ..."
    ("this.info = why;", "-"),                                   # "bag is full, or the same or a better ... is already equipped"
    ('this.info = "could not find " + {PKG}.AccDefs.pretty(id) + " in your inventory";', "-"),
    ('this.info = g == 0 ? why : (g == 1 ? why + " - it was kept in a free bag slot" : "could not give " + ', "-"),
    ('this.info = "upgraded to " + {PKG}.AccDefs.pretty(id) + " - " + (g == 0 ? old + " returned" : (g == 1 ? old + " kept in the bag '
     '- inventory full" : old + " could not be returned - reported to the server log"));', "+ (- when the old one could not be returned)"),
    ('this.info = "equipped " + {PKG}.AccDefs.pretty(put) + ', "+"),
]
assert HDE.count("this.info = ") == len(INFO_SETS), "handleDataEvent sets %d result texts, INFO_SETS lists %d" % (HDE.count("this.info = "), len(INFO_SETS))
for _a, _c in INFO_SETS:
    assert HDE.count(_a) == 1, "result text changed - decide its colour in AccPage.infoColor: " + _a
assert HDE.count('String why = "bag is full, or the same or a better "') == 1
_mb = block("public static String moveBlock(java.util.UUID u) {", "# 0.4.1 PROFILES-CONTRACT rule 3")
assert re.findall(r'return "([^"]*)"', _mb) == ["your profile is still loading - try again in a moment",
                                                "your profile is not loaded - try again in a moment - tell an admin if this stays"], _mb
_rw = block("public static String retiredWhy(String id) {", "public static String retiredChat(String id) {")
assert [t[:10] for t in re.findall(r'return "([^"]*)"', _rw)] == ["Retired - "] * 3, _rw
for _t in ["your profile changed", "your profile is", "your inventory is full", "Retired - ", "bag is full", "could not "]:
    assert not any(_t.startswith(p) for p in ("equipped ", "unequipped ", "upgraded to ")), _t
assert [ln for ln in new_lines if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
assert s.count("registerCommand(") == REG0, "command registrations changed"
for k in KEEP:
    assert k in s, "a block that must stay 0.4.4's changed: %s" % k[:80]
for c in ("#0b1524", "#8fd0ff", "#e6f4ff", "#9fb8cc", "#9be89b", "#142030", "#5f7a90", "#c9dff0", "#c9b89a", "#5a4420", "#8a6a30",
          "#3a2a10", "#ffe9c9", "TextButtonStyle(Default: (Background: #", "String bs = ", "PAGE_H"):
    assert c not in s.split("# ================= AccPage =================")[1].split("# giveBack: 0")[0], "0.4.4 custom look left: " + c
assert "import skyyui as SUI" in s and s.index("SUI.verify()") < s.index("J = B.start()"), "verify() must run before the build"
assert s.index("# ---- ACC PAGE BLOCK START") < s.index("# ---- ACC PAGE BLOCK END") < s.index("page.addMethod(CtNewMethod.make(ACC_BUILD_SRC, page))")
assert s.index("public static String safe(String t)") < s.index("ACC_BUILD_SRC = f") < s.index("public static int giveBack("), \
    "javassist: build() keeps its place (after safe / carried, before giveBack / handleDataEvent)"
assert "{KIT_ID}" in s and 'VERSION = "0.4.5"' in s and "@@" not in s
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.4.4
print("wrote", dst, "(%d lines; 0.4.4 had %d)" % (s.count(LF), OLD.count(LF)))
