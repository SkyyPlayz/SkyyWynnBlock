"""Derive SkyyTrees/build_skyytrees_0.2.5.py from the LIVE SkyyTrees/build_skyytrees_0.2.4.py (the tools/deploy_set.py SET pin).
Run:  python tools/trees_0_2_5_patch.py   then   python SkyyTrees/build_skyytrees_0.2.5.py   (never --deploy: coordinated deploy)
EDITED-SCRIPTS RULE (commit ab75b6c): the lineage is Skyy's EDITED 0.2.3 -> tools/trees_0_2_4_patch.py -> the generated 0.2.4 read
here; tools/trees_0_2_3_patch.py and older are NEVER re-run. Edit THIS file, never the generated build script. Same style as
trees_0_2_4_patch.py (rep() with asserted single anchors, newline-agnostic; 0.2.4 stays untouched, its CRLF line endings are kept).

0.2.5 = the vanilla UI pass (Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them to look and feel
vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md sections 7, 12 and 14; research/Skyy-UI-Inventory.md 5.21).
ONLY THE LOOK OF TreePage (/tree) CHANGES - a look-only restyle on the shared kit tools/skyyui.py (1.4):
  - the generated script imports skyyui as SUI and calls SUI.verify() before anything else (every vanilla value the page uses is
    proven against Assets.zip at every build) and puts SUI.kit_id() into the ready log line;
  - TreePage.build() is generated at build time by tree_page_java(): 0.2.4's statements (tree / node clamps, the data, level and
    balance reads, every text expression, the tier / node loops, the 11 event bindings trtab<i> / trnode<s> / trbuy / trtoggle /
    trback / trrespec with their EventData and order, the armed-respec rule) are kept word for word - asserted below against the
    0.2.4 method; only the appends changed. Texts 0.2.4 wrote inline after safe() are b.set now (the same safe() text); the Buy
    button's runtime label becomes a b.set line above a button with a static label (a b.set TextButton label is UNVERIFIED:
    kit probe page 20 button-text), the per-tree Tab / Respec labels are static per tree index.
  - the old-look page fields BG / HV / FG / SOON_BG / SOON_HV / SOON_FG and the old line() helper go (only build() used them); a
    result-colour helper infoColor() comes in (SUI.java_color_by_text: 0.2.4's result texts carry no + / - / = mark).
  - UI_DATA_COLORS lists the tree colours (TreeDefs.TCOLOR, data colours) and the chat line colours (Message.color, not page chrome).
  - review fixes (2026-09-29, still 0.2.5 - never deployed): the node grid sits on the vanilla list well (0.2.4's #SkyyTrGrid is
    SUI.list_well now: padding 4, the cells 4 apart both ways, the tier column 204; the page is 1440 x 892), and the UNVERIFIED gate
    in the generated docstring names all four base probe pages (base4 = the kit 1.4 blocks).
  - second review fixes (2026-09-29, still 0.2.5 - never deployed): the node name / state lines are 168 px wide (TR_TEXT_W; the
    cell's right margin 8 -> 2) so "Wanderer's Heart" (154 px in the client glyph tables, 95% of the old 162) keeps room if the
    client renders a little wider than the table model; the draft-slot cell look is one constant (TR_DRAFT_CELL: "disabled" = the
    kit's sold-out cover cell; "normal" = the fallback if the cover swallows the click in game); the generated docstring's
    UNVERIFIED notes say that base4 (probe page 19) needs a SkyyUiProbe 0.2 on kit 1.4 (the deployed 0.1 opens pages 1-18 only),
    name the draft-slot click-through, the greyed buttons that must still fire, the SkyyAuctions 0.1.2 precedent for b.set on
    Labels inside a Button, and the rebuild on the final committed kit (the harness now fails on a kit id mismatch).
Everything else (the swing-speed interaction assets, Tree Feller, Double Jump, the player-file migration, commands, permissions,
config keys + rows, files, bridge keys, TreePage's other fields, constructor, text helpers and handleDataEvent, every other class)
is byte-identical to 0.2.4 - asserted below (KEEP blocks); the harness SkyyTrees/test_skyytrees_0.2.5.py compares the jars.
"""
import collections
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.2.4.py")
dst = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.2.5.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2.4"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
OLD = s
# the source must be the generated 0.2.4 of the EDITED lineage (Skyy's ab75b6c edits carried through trees_0_2_4_patch.py)
assert 'VERSION = "0.2.4"' in s and "DERIVED from the EDITED build_skyytrees_0.2.3.py by tools/trees_0_2_4_patch.py" in s, \
    "build_skyytrees_0.2.4.py is not the live 0.2.4 of the edited lineage"
for _a in ('"feller.cooldownSec", "Tree Feller cooldown", "abilities", "int", "3"', 'feller.logs', 'Skyy_Tree_Chop_Wood',
           'p.setProperty("v", "2");'):
    assert _a in s, "not the live 0.2.4: missing %r" % _a
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
assert len(BIND0) == 6, "0.2.4 has 6 event binding lines (all in TreePage.build), found %d" % len(BIND0)


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
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


# blocks that must come out of this patch byte-identical (everything but the docstring, VERSION, the kit import, the data colour
# list, TreePage's look (the tbs styles, the old-look fields, line() and build()) and the ready log line)
KEEP = [block("\nHERE = os.path.dirname(os.path.abspath(__file__))", 'TCOLOR = ["#8fc8ff"'),
        block("for n, tn in enumerate(TREES): T[\"T_\" + tn.upper()] = str(n)", "# ================= TreePage: the inline tree page ================="),
        block('F(page, "public int tree;")', "F(page, 'public static final String[] BG = "),
        block('F(page, "public static final java.util.concurrent.ConcurrentHashMap LASTTREE', "F(page, 'public static final String SOON_BG = "),
        block('C(page, r"""\npublic TreePage(', 'M(page, r"""\npublic static void line('),
        block('M(page, r"""\npublic void handleDataEvent(', 'getLogger().at(java.util.logging.Level.INFO).log("[SkyyTrees] @VERSION@ ready'),
        block("  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());\n}\"\"\".replace(\"@VERSION@\", VERSION))",
              'if "--deploy" in sys.argv:')]

# ================================================================================================ docstring
rep('''"""SkyyTrees 0.2.4 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
DERIVED from the EDITED build_skyytrees_0.2.3.py by tools/trees_0_2_4_patch.py - edit the patch, not this file. 0.2.3 was derived from
0.2.2 by tools/trees_0_2_3_patch.py and then edited by Skyy in commit ab75b6c (locked defaults) - never re-run that patch; 0.2.2 was
derived from 0.2.1 by tools/trees_0_2_2_patch.py, 0.2.1 from 0.2 by tools/trees_0_2_1_patch.py, 0.2 from 0.1 by tools/trees_0_2_patch.py.
''', '''"""SkyyTrees 0.2.5 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_2_5_patch.py from the LIVE build_skyytrees_0.2.4.py (the EDITED lineage: Skyy's edited 0.2.3 ->
trees_0_2_4_patch.py -> 0.2.4) - edit the patch, not this file; trees_0_2_3_patch.py and older are never re-run. 0.2.4 was DERIVED
from the EDITED build_skyytrees_0.2.3.py by tools/trees_0_2_4_patch.py. 0.2.3 was derived from
0.2.2 by tools/trees_0_2_3_patch.py and then edited by Skyy in commit ab75b6c (locked defaults) - never re-run that patch; 0.2.2 was
derived from 0.2.1 by tools/trees_0_2_2_patch.py, 0.2.1 from 0.2 by tools/trees_0_2_1_patch.py, 0.2 from 0.1 by tools/trees_0_2_patch.py.
0.2.5 (2026-09-29, the vanilla UI pass - Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them to look and
  feel vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md sections 12 + 14): ONLY THE LOOK OF THE /tree PAGE
  CHANGED, on the shared kit tools/skyyui.py (1.4). Commands, permissions, config, files, bridge keys, the swing-speed interaction
  assets, Tree Feller, Double Jump, the player-file migration, every element id of 0.2.4, the 11 event bindings (trtab<i>, trnode<s>,
  trbuy, trtoggle, trback, trrespec - same EventData, same order), the tree / node / message / respec-arm state and every text are
  0.2.4's (the patch asserts it; SkyyTrees/test_skyytrees_0.2.5.py builds the page in both jars and compares).
  - The build calls SUI.verify() first (every vanilla style value / texture / sound the page uses is proven against Assets.zip,
    read-only; a game update that changes one stops the build); KIT_ID (kit version + file hash) is in the ready log line.
  - Window: the vanilla plain container (@Container: the ContainerHeaderNoRunes title bar, no ornaments - the same window as the
    SkyySkills 0.4.7 pages, so Skills -> Tree -> < Skills reads as one family), title SKILL TREES in the 15 px Secondary title style,
    the ContainerPatch body, padding 17; 1440 x 892 (was 1000 x 660); 0.2.4's root #SkyyTrRoot is the body now. Gone: the dark-blue
    root, the tree-colour rule, the custom button colours, the empty Label spacers.
  - Tabs: the vanilla server tab row (EntitySpawnPage): six 172 px buttons 5 apart, the open tree Primary, the others Secondary;
    the level "<Tree> n" right of them in the tree colour (data colour, 18 px bold). Under them Tokens (vanilla gold), Dust (property
    value colour) and the one-line note (the default label), then the vanilla content separator.
  - Node grid: on the vanilla list well (#000000(0.15), padding 4 - WorldEventPanelPage #ListContainer; 0.2.4's #SkyyTrGrid is the
    well now, so the node cells sit on the well like vanilla list rows and the grid and the detail well read as one family), six
    tier rows (VI on top), the tier head in the vanilla section-head style (16 px bold uppercase; the section colour
    once your level opens the tier, the disabled grey before), the nodes centred under each other like a tree (1 / 2 / 3 per tier),
    the cells 4 apart both ways.
    Node = the kit's icon_cell (242 x 96, the WorldEventListRow palette: row #101925(0.55), hover #132033(0.8), pressed
    #182a40(0.9) + the light click; the selected node = the vanilla selected row #4274a5) with a 52 px item icon, the node name
    (18 px bold) and its state line (15 px), both 168 px wide: Locked = disabled grey, Unlockable = success green, Owned = info blue,
    Maxed = gold;
    the selected node white / row-name. The Exploration draft slots ("Coming later") use the kit's disabled cell (the vanilla
    sold-out cover over it, grey text, no click sound).
  - Detail panel: a vanilla well (#000000(0.15), padding 8, 440 x 608): the item icon in the vanilla slot border, the name (18 px
    bold) and state line in the state colour, then three vanilla section heads (WorldEventSectionLabel: EFFECT / COST / HOW IT
    WORKS) over Now (property value colour) + Next level (default text), the cost (gold, bold) + what is missing (the vanilla error
    red), and how it triggers (the summary colour); at the bottom the Buy line (the old Buy button text, now a label: gold when you
    can buy, green at MAX, grey otherwise) and the buttons: Unlock / Level up = Primary (the vanilla Disabled look while you cannot
    buy - still clickable, the reason is shown as before), Maxed / Coming later = Disabled; Turn off / Turn on = Secondary.
  - Result line: 0.2.4's message (#SkyyTrMsg) in the vanilla result colours by its words (infoColor: done green, refused red, the
    "Click Respec again" arm in the confirm yellow, "coming later" info blue), two lines, above the footer separator.
  - Footer: "< Skills" (Secondary, cancel sound - the SkyySkills 0.4.7 nav buttons) left; Respec <Tree> right (Secondary); armed
    ("Click again to respec <Tree>", within 10 s, as before) = Destructive.
  - Fonts 15-18 px (0.2.4: 10-16); every static label is proven text, every other text b.set.
  UNVERIFIED (needs the game): the kit's "base" look has not been seen in game yet - skyyui probe pages base1, base2, base3 AND
  base4 (the icon cell and the disabled cell are on base3; the kit 1.4 blocks this page uses - list_well, result_line,
  item_frame(item=, cover=), the runtime colours of java_color_by_text / color_by and the right_margin footer offset - are on
  base4, probe page 19). Hold this version until Skyy has seen all four work. base4 CANNOT be opened yet: the deployed
  SkyyUiProbe 0.1 (kit 1.3) bakes in probe pages 1-18 only, so a SkyyUiProbe 0.2 on kit 1.4 (pages 1-22) has to be built and
  seen first. If none is built, base4's pieces reduce to properties base1-base3 already carry (a colour Background + Padding
  well, a runtime TextColor, an Anchor Left margin, the slot-border texture) and the gate falls back to base1-base3 - Skyy's
  call; the deploy notes name base4 either way.
  Also unseen in game: (a) the Exploration draft slots S5-S12 are bound Buttons with the kit's full-size sold-out cover Group
  (#SkyyTrN<s>Out, Anchor Full 0) inside them - no deployed page has a background Group over a bound Button, so the first click
  on an unselected draft slot may be swallowed by the cover (the selected slot has no cover; fallback: TR_DRAFT_CELL = "normal"
  in tools/trees_0_2_5_patch.py, the row cell with grey text and no cover); (b) the greyed buttons - Unlock / Level up while you
  cannot buy, Maxed, Coming later: the vanilla Disabled style without a Disabled: true property - must still fire their event
  (the refusal text shows as before); (c) b.set on the Labels inside a Button (the node name / state lines): SkyyAuctions 0.1.2
  (in the SET) already does it (#SkyyAhInvQty<i>), but that has not been seen in game either.
  KIT_ID is the kit on disk at build time (tools/skyyui.py is not committed yet): rebuild on the final committed kit before the
  deploy round (build only, never --deploy) and rerun SkyyTrees/test_skyytrees_0.2.5.py - it fails when the jar's kit id is not
  the id of tools/skyyui.py.
''')
rep('''Run:   python build_skyytrees_0.2.4.py            -> SkyyTrees/SkyyTrees-0.2.4.jar
       python build_skyytrees_0.2.4.py --deploy   -> also Mods/SkyyTrees.jar''', '''Run:   python build_skyytrees_0.2.5.py            -> SkyyTrees/SkyyTrees-0.2.5.jar
       python build_skyytrees_0.2.5.py --deploy   -> also Mods/SkyyTrees.jar''')
# the old page's colour words in the history notes (the 0.1 / 0.2 page look; replaced by 0.2.5 - see above)
rep("the page shows \"Coming later\" (card #1a1a24 / #8890a0, no Turn off button)",
    "the page shows \"Coming later\" (a greyed card, no Turn off button)")
rep('''  no MouseEntered handlers, no periodic updates, dynamic label text through b.set. 1000 x 660: tabs Mining | Foraging | Farming |
  Cooking + level / Tokens / Dust, 6 tier rows (VI on top) of node cards in 4 states (Locked #1c1414/#b07a68, Unlockable
  #16301f/#9adf86, Owned #10243d/#9cd8ff, Maxed #3a3010/#ffc300; the selected card uses its state's hover colour), a detail panel''',
    '''  no MouseEntered handlers, no periodic updates, dynamic label text through b.set. 1000 x 660 (0.1-0.2.4; the 0.2.5 vanilla look is
  described at the top): tabs Mining | Foraging | Farming | Cooking + level / Tokens / Dust, 6 tier rows (VI on top) of node cards in
  4 states (Locked, Unlockable, Owned, Maxed; the selected card uses its state's hover colour), a detail panel''')

# ================================================================================================ version, kit import, data colours
rep('VERSION = "0.2.4"', 'VERSION = "0.2.5"')
rep("import skyycfg as CFG   # 0.2.2: the admin config kit (tools/CONFIG-CONTRACT.md)\n",
    """import skyycfg as CFG   # 0.2.2: the admin config kit (tools/CONFIG-CONTRACT.md)
import skyyui as SUI       # 0.2.5: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"
SUI.verify()               # proves every vanilla value / texture / sound the page uses against Assets.zip (read-only); stops the build on drift
KIT_ID = SUI.kit_id()      # "skyyui <version> <blob12>" - in the ready log line
""")
rep('TCOLOR = ["#8fc8ff", "#8fe08a", "#f0d060", "#ffb070", "#c8a0ff", "#e0a040"]\n',
    '''TCOLOR = ["#8fc8ff", "#8fe08a", "#f0d060", "#ffb070", "#c8a0ff", "#e0a040"]
# 0.2.5: DATA colours for the vanilla UI kit's lint (research/Vanilla-UI-Style-Guide.md section 5): the tree colours (TreeDefs.TCOLOR -
# the level line on /tree) + the chat line colours (Message.color: the notice, the Tree bonus line, Vein Burst / Tree Feller, the
# unknown-tree answer - not page chrome)
UI_DATA_COLORS = TCOLOR + ["#b8f0a0", "#9cd8ff", "#ffc300", "#ff9090"]
''')

# ================================================================================================ TreePage: the look only
OLD_LOOK = cut("# ================= TreePage: the inline tree page =================\ndef tbs(", 'F(page, "public int tree;")', "@@PAGE_KIT@@")
assert 'T["BSG"] = tbs(' in OLD_LOOK and 'T["BTOFF"] = T["BSOFF"]' in OLD_LOOK
OLD_FIELDS = []
for _f in ("F(page, 'public static final String[] BG = new String[] { \"#1c1414\", \"#16301f\", \"#10243d\", \"#3a3010\" };')\n",
           "F(page, 'public static final String[] HV = new String[] { \"#2c2020\", \"#22462e\", \"#1a3a5e\", \"#54461a\" };')\n",
           "F(page, 'public static final String[] FG = new String[] { \"#b07a68\", \"#9adf86\", \"#9cd8ff\", \"#ffc300\" };')\n",
           "F(page, 'public static final String SOON_BG = \"#1a1a24\";')\n",
           "F(page, 'public static final String SOON_HV = \"#262634\";')\n",
           "F(page, 'public static final String SOON_FG = \"#8890a0\";')\n"):
    rep(_f, "")
    OLD_FIELDS.append(_f)
OLD_BUILD = cut('M(page, r"""\npublic static void line(', 'M(page, r"""\npublic void handleDataEvent(', "@@PAGE_BUILD@@")
assert OLD_BUILD.count("public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {") == 1 and OLD_BUILD.count("M(page, r\"\"\"") == 2
OLD_BUILD_SRC = OLD_BUILD[OLD_BUILD.index("public void build("):OLD_BUILD.rindex('}""")') + 1]

PAGE_KIT = r'''# ================= TreePage: the inline tree page (0.2.5: the vanilla UI kit, tools/skyyui.py) =================
# 0.2.5 (the vanilla UI pass): TreePage's look = kit calls only. tree_page_java() builds build()'s Java at BUILD time (every value
# proven by SUI.verify()); 0.2.4's statements (the clamps, the data / level / balance reads, every text expression, the tier and node
# loops, the event bindings and their order, the armed-respec rule) are kept word for word (tools/trees_0_2_5_patch.py asserts it);
# only the appends changed and the texts 0.2.4 wrote inline (after safe()) are b.set now. Only properties the deployed pages already
# use (LayoutMode Left / Top, fixed widths / heights, Anchor margins, Padding, colour backgrounds, Button + ItemIcon cells, Wrap):
# no FlexWeight, no WrapMaxLines, no LetterSpacing, no LayoutMode Center / Right / Full (SUI.assert_proven below).
# Page 1440 x 892 (the plain window of the SkyySkills 0.4.7 pages; the old root #SkyyTrRoot is its body): tab row + level | Tokens,
# Dust, note | separator | the node grid on the list well (tier heads + icon cells, centred per tier) beside the detail well
# (section heads Effect / Cost / How it works) | result line | separator | footer (< Skills ... Respec).
TR_PREFIX = "SkyyTr"
TR_TAB_W, TR_TAB_GAP = SUI.BTN_MIN_W, 5          # six vanilla tab buttons (EntitySpawnPage row: 5 px apart), 172 = @DefaultButtonMinWidth
TR_TIER_W = 204                                  # the tier head column: every tier I head on one line (TIER I - EXPLORATION 1 = 191 px)
TR_CELL_W, TR_CELL_H, TR_CELL_GAP = 242, 96, 4   # a node cell (kit icon_cell, row palette) + the gap right of it
TR_ROW_GAP = 4                                   # under each tier row: the cells sit 4 apart both ways on the list well
TR_PER_ROW = 3                                   # the most nodes one tier holds (SLOT_TIER, asserted below)
TR_ICON, TR_ICON_L = 52, 10                      # the node icon and its left margin in the cell
TR_TEXT_L = TR_ICON_L + TR_ICON + 10             # the name / state lines start here (72)
TR_TEXT_R = 2                                    # the cell's right margin after the name / state lines (was 8: 154 of 162 px was tight)
TR_TEXT_W = TR_CELL_W - TR_TEXT_L - TR_TEXT_R    # 168 px: "Wanderer's Heart", the widest name, is 154 px at 18 px bold (92%)
# the Exploration draft slots ("Coming later"): the kit's disabled cell (the sold-out cover inside the bound Button, grey text,
# silent). UNVERIFIED that the cover lets the click through (no deployed page has a background Group over a bound Button): if the
# first click on a draft slot does nothing in game, set this to "normal" (the row cell, grey text, no cover) and rebuild.
TR_DRAFT_CELL = "disabled"
assert TR_DRAFT_CELL in ("disabled", "normal"), TR_DRAFT_CELL
TR_NAME_H, TR_SUB_H = 28, 24                     # rowName 18 px + rowSub 15 px (the readable WorldEventListRow lines)
TR_DET_W, TR_DET_GAP = 440, 16                   # the detail well and the gap left of it
# the grid = the vanilla list well (review fix 2026-09-29: the row-coloured cells sat straight on the ContainerPatch body, 1.04:1 -
# vanilla puts rows on the #000000(0.15) well, style guide section 6); its padding 4 comes out of the tier column (was 200 + 3 x 250)
TR_GRID_W = 2 * SUI.WELL_LIST_PAD + TR_TIER_W + TR_PER_ROW * (TR_CELL_W + TR_CELL_GAP)      # 950 (the width budget is unchanged)
TR_GRID_H = SUI.list_well_h(6, TR_CELL_H, TR_ROW_GAP)                                         # 608: six tier rows + the padding
assert (TR_CELL_W + TR_CELL_GAP) % 2 == 0, "the centring step (half a cell) must be a whole pixel count"
TR_HEAD_H, TR_HEAD_GAP, TR_INFO_H = SUI.BTN_H, 10, 28
TR_MSG_H, TR_FOOT_H = 44, SUI.BTN_H
TR_SEP = 1 + 8 + 8                               # separator("content") with its top / bottom 8 (WorldEventPanelPage)
TR_PARTS = [TR_HEAD_H + TR_HEAD_GAP, TR_INFO_H, TR_SEP, TR_GRID_H, 8 + TR_MSG_H, TR_SEP, TR_FOOT_H]
TR_W = TR_GRID_W + TR_DET_GAP + TR_DET_W + 2 * SUI.CONTENT_PAD
TR_H = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + sum(TR_PARTS)
TR_LVL_W = TR_W - 2 * SUI.CONTENT_PAD - len(TREES) * TR_TAB_W - (len(TREES) - 1) * TR_TAB_GAP
TR_TOK_W, TR_DUST_W = 190, 230
TR_NOTE_W = TR_W - 2 * SUI.CONTENT_PAD - TR_TOK_W - TR_DUST_W
TR_BACK_W = SUI.BTN_MIN_W
TR_DET_IN_W = TR_DET_W - 2 * SUI.WELL_PAD
TR_BUY_W = (TR_DET_IN_W - 8) // 2                # Buy + Turn off side by side, 8 apart
TR_OLD_IDS = ["SkyyTrRoot", "SkyyTrHead", "SkyyTrTab0", "SkyyTrLvl", "SkyyTrTok", "SkyyTrDust", "SkyyTrNote", "SkyyTrBody",
              "SkyyTrGrid", "SkyyTrRow0", "SkyyTrTier0", "SkyyTrN0", "SkyyTrDet", "SkyyTrDetTop", "SkyyTrDetIcon", "SkyyTrDetName",
              "SkyyTrDetState", "SkyyTrDetNow", "SkyyTrDetNext", "SkyyTrDetCost", "SkyyTrDetNeed", "SkyyTrDetHow", "SkyyTrBuy",
              "SkyyTrToggle", "SkyyTrFoot", "SkyyTrBack", "SkyyTrRespec", "SkyyTrMsg"]      # every element id of the 0.2.4 page (kept)
assert max(SLOT_TIER.count(_k) for _k in set(SLOT_TIER)) <= TR_PER_ROW, "a tier holds more nodes than one grid row"
assert all(SUI.text_width(r["name"], 18, True) <= TR_TEXT_W for r in ROWS), "a node name does not fit its cell at 18 px bold"
TR_RESPEC_ON_W = max(-(-int(SUI.text_width("Click again to respec " + tn, 17, True, upper=True) + 2 * 24) // 10) * 10 for tn in TREES)
TR_RESPEC_OFF_W = max(-(-int(SUI.text_width("Respec " + tn, 17, True, upper=True) + 2 * 24) // 10) * 10 for tn in TREES)
# the result colours by the words of 0.2.4's messages (TreeOps.buy / toggle / respec, handleDataEvent): done = green, refused = red
TR_INFO_COLOR = SUI.java_color_by_text("infoColor", [
    ("startsWith", "Unlocked ", "+"), ("contains", " is now level ", "+"), ("endsWith", " turned off - its level is kept", "+"),
    ("endsWith", " turned on", "+"), ("startsWith", "Respec done", "+"), ("startsWith", "Click Respec again", "warning"),
    ("contains", " is coming later", "=")], empty="=", default="-")
TR_BUILD = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  int t = this.tree;
  if (t < 0 || t >= @PKG@.TreeDefs.NT) t = 0;
  int sl = this.sel;
  if (sl < 1 || sl > 12) sl = 1;
  @PKG@.TreeData d = @PKG@.TreeStore.data(u);
  int lvl = @PKG@.TreeCalc.level(u, t);
  long[] bal = @PKG@.TreeCalc.balance(u, d, t, lvl);
  long tokA = bal[0] - bal[1];
  long dustA = bal[2] - bal[3];
  String tn = @PKG@.TreeDefs.TREES[t];
  String col = @PKG@.TreeDefs.TCOLOR[t];
{{SHELL}}
{{HEAD}}
  for (int i = 0; i < @PKG@.TreeDefs.NT; i++) {
{{TAB}}
    ev.addEventBinding(@BT@.Activating, "#SkyyTrTab" + i, @EVD@.of("a", "trtab" + i));
  }
{{INFO}}
  b.set("#SkyyTrLvl.Text", lvl < 0 ? "SkyySkills missing" : tn + " " + lvl);
  b.set("#SkyyTrTok.Text", "Tokens " + tokA + " of " + bal[0]);
  b.set("#SkyyTrDust.Text", "Dust " + @PKG@.TreeDefs.grp(dustA));
  b.set("#SkyyTrNote.Text", note(u, d, t, lvl, tokA, dustA));
{{GRID}}
  for (int k = 6; k >= 1; k--) {
    int gate = @PKG@.TreeCfg.TIER_LV[k - 1];
    int nk = 0;
    for (int s2 = 1; s2 <= 12; s2++) if (@PKG@.TreeDefs.TIER[t * 12 + s2 - 1] == k) nk++;
    int rp = nk >= __PER_ROW__ ? 0 : (__PER_ROW__ - nk) * __HALF_CELL__;
{{ROW}}
    b.set("#SkyyTrTier" + k + ".Text", "Tier " + @PKG@.TreeDefs.roman(k) + " - " + tn + " " + gate);
    for (int s = 1; s <= 12; s++) {
      int i = t * 12 + s - 1;
      if (@PKG@.TreeDefs.TIER[i] != k) continue;
      int stt = @PKG@.TreeCalc.state(d, i, lvl, tokA);
      boolean so = @PKG@.TreeDefs.soon(i);
{{CELL}}
      b.set("#SkyyTrN" + s + "Nm.Text", safe(@PKG@.TreeDefs.NAME[i]));
      b.set("#SkyyTrN" + s + "Sb.Text", safe(cardSub(d, i, stt, lvl, tokA)));
      ev.addEventBinding(@BT@.Activating, "#SkyyTrN" + s, @EVD@.of("a", "trnode" + s));
    }
  }
  int i0 = t * 12 + sl - 1;
  int st0 = @PKG@.TreeCalc.state(d, i0, lvl, tokA);
  boolean so0 = @PKG@.TreeDefs.soon(i0);
  boolean mx0 = d.lv[i0] >= @PKG@.TreeCfg.MAX[i0];
{{DET}}
  b.set("#SkyyTrDetName.Text", @PKG@.TreeDefs.NAME[i0] + "  (S" + sl + ")");
  b.set("#SkyyTrDetState.Text", stateLine(d, i0, st0));
  b.set("#SkyyTrDetNow.Text", nowLine(d, i0));
  b.set("#SkyyTrDetNext.Text", nextLine(d, i0));
  b.set("#SkyyTrDetCost.Text", costLine(d, i0));
  b.set("#SkyyTrDetNeed.Text", needLine(d, i0, lvl, tokA, dustA));
  b.set("#SkyyTrDetHow.Text", @PKG@.TreeDefs.HOW[i0].replace("%C", cd(i0)).replace("%K", @PKG@.TreeFx.djKey()));
  boolean can = canAct(d, i0, st0, tokA, dustA);
{{BUY}}
  b.set("#SkyyTrBuyTx.Text", safe(buyText(d, i0, st0, lvl, tokA, dustA)));
  ev.addEventBinding(@BT@.Activating, "#SkyyTrBuy", @EVD@.of("a", "trbuy"));
  if (d.lv[i0] >= 1 && !@PKG@.TreeDefs.soon(i0)) {
{{TOGGLE}}
    ev.addEventBinding(@BT@.Activating, "#SkyyTrToggle", @EVD@.of("a", "trtoggle"));
  }
{{FOOT}}
  b.set("#SkyyTrMsg.Text", this.msg == null ? "" : this.msg);
  ev.addEventBinding(@BT@.Activating, "#SkyyTrBack", @EVD@.of("a", "trback"));
  boolean armed = this.armT == t && System.currentTimeMillis() - this.armAt <= 10000L;
{{RESPEC}}
  ev.addEventBinding(@BT@.Activating, "#SkyyTrRespec", @EVD@.of("a", "trrespec"));
}""".replace("__PER_ROW__", str(TR_PER_ROW)).replace("__HALF_CELL__", str((TR_CELL_W + TR_CELL_GAP) // 2))


def _tr_in(outer, *kids):
    """kit markup `outer` with the kit markups `kids` placed inside it (before its closing brace) - the 0.2.4 card pattern: a
    Button holding its ItemIcon and Labels, children placed by Anchor."""
    assert outer.endswith("}") and kids, outer[:60]
    return outer[:-1] + " ".join(kids) + " }"


def tree_page_java():
    """TreePage.build(): TR_BUILD with its {{parts}} built from kit calls, every markup recorded for assert_proven. Heights fill the
    window body exactly and every row / column is budgeted (asserted)."""
    sh = SUI.page_shell("SkyyTrF", TR_W, TR_H, "Skill Trees", kind="plain", body_id="SkyyTrRoot")   # the SkyySkills 0.4.7 window
    assert sh.fit(TR_PARTS) == 0, "the tree page body must be filled exactly"
    body, W = sh.body, sh.inner_w
    assert SUI.fit([TR_GRID_W, TR_DET_GAP, TR_DET_W], W, "grid + detail") == 0
    assert SUI.fit([len(TREES) * TR_TAB_W, (len(TREES) - 1) * TR_TAB_GAP, TR_LVL_W], W, "tab row") == 0 and TR_LVL_W >= 240
    assert SUI.fit([TR_TOK_W, TR_DUST_W, TR_NOTE_W], W, "info row") == 0
    marks = list(sh.appends.markups())

    def app(parent, markup):
        marks.append(markup)
        return SUI.java_append(parent, markup)

    def chain(conds, parent, markups):
        """if (c0) append m0; else if (c1) append m1; ...; else append the last (len(markups) == len(conds) + 1, or == len(conds))"""
        out = []
        for n, mk in enumerate(markups):
            head = ("if (%s) " % conds[n]) if n == 0 else (("else if (%s) " % conds[n]) if n < len(conds) else "else ")
            out.append(head + app(parent, mk))
        return "\n".join(out)

    i, s, k = SUI.J("i", "0"), SUI.J("s", "1"), SUI.J("k", "6")
    # ---- tab row: the open tree Primary, the others Secondary (one static label per tree index) + the level line
    tabs = []
    for n, name in enumerate(TREES):
        anc = {"left": TR_TAB_GAP} if n else None
        tabs.append(SUI.choose(SUI.J("i == t"), SUI.button("SkyyTrTab%d" % n, name, "primary", w=TR_TAB_W, anchor=anc),
                               SUI.button("SkyyTrTab%d" % n, name, "secondary", w=TR_TAB_W, anchor=anc)))
    info = [app(body, SUI.group("SkyyTrInfo", "Left", h=TR_INFO_H)),
            app("SkyyTrHead", SUI.label("SkyyTrLvl", "", "rowName", w=TR_LVL_W, h=TR_HEAD_H, align="End",
                                        col=SUI.J("col", TCOLOR[0]))),
            app("SkyyTrInfo", SUI.label("SkyyTrTok", "", "bold", w=TR_TOK_W, h=TR_INFO_H, col="gold")),
            app("SkyyTrInfo", SUI.label("SkyyTrDust", "", "bold", w=TR_DUST_W, h=TR_INFO_H, col="value")),
            app("SkyyTrInfo", SUI.label("SkyyTrNote", "", "default", w=TR_NOTE_W, h=TR_INFO_H))]
    # ---- the grid: tier rows (VI on top), the nodes of a tier centred (rp = the left room of a row with fewer than 3 nodes)
    well = SUI.list_well("SkyyTrGrid", TR_GRID_W, rows=6, row_h=TR_CELL_H, gap=TR_ROW_GAP)      # 0.2.4's #SkyyTrGrid, on the well
    assert well.h == TR_GRID_H and well.inner_w == TR_TIER_W + TR_PER_ROW * (TR_CELL_W + TR_CELL_GAP) \
        and well.inner_h == 6 * (TR_CELL_H + TR_ROW_GAP), "the node grid must fill its list well exactly"
    grid = [app(body, SUI.separator("content", anchor={"top": 8, "bottom": 8})),
            app(body, SUI.group("SkyyTrBody", "Left", h=TR_GRID_H)),
            app("SkyyTrBody", well)]
    tier_col = SUI.color_by([("lvl >= gate", "section")], "disabled")
    row = [app("SkyyTrGrid", SUI.group("SkyyTrRow" + k, "Left", h=TR_CELL_H, anchor={"bottom": TR_ROW_GAP})),
           app("SkyyTrRow" + k, SUI.label("SkyyTrTier" + k, "", "section", w=SUI.J("%d + rp" % TR_TIER_W, str(TR_TIER_W)), h=TR_CELL_H,
                                          wrap=True, col=tier_col))]
    node_col = SUI.color_by([("stt == 1", "success"), ("stt == 2", "info"), ("stt == 3", "gold")], "disabled")
    top = (TR_CELL_H - TR_NAME_H - TR_SUB_H) // 2
    assert SUI.fit([top, TR_NAME_H, TR_SUB_H], TR_CELL_H, "node cell lines") >= 0
    assert SUI.fit([TR_TEXT_L, TR_TEXT_W, TR_TEXT_R], TR_CELL_W, "node cell text columns") == 0

    def cell(state, name_col, sub_col):
        c = SUI.icon_cell("SkyyTrN" + s, SUI.J("@PKG@.TreeDefs.ICON[i]", "Tool_Pickaxe_Iron"), state=state, icon=TR_ICON,
                          w=TR_CELL_W, h=TR_CELL_H, icon_left=TR_ICON_L, anchor={"right": TR_CELL_GAP})
        nm = SUI.label("SkyyTrN" + s + "Nm", "", "rowName", w=TR_TEXT_W, h=TR_NAME_H, col=name_col, anchor={"left": TR_TEXT_L, "top": top})
        sb = SUI.label("SkyyTrN" + s + "Sb", "", "rowSub", w=TR_TEXT_W, h=TR_SUB_H, col=sub_col,
                       anchor={"left": TR_TEXT_L, "top": top + TR_NAME_H})
        return _tr_in(c, nm, sb)
    cells = chain(["s == sl", "so"], "SkyyTrRow" + k,
                  [cell("selected", "white", "rowName"), cell(TR_DRAFT_CELL, "disabled", "disabled"), cell("normal", node_col, node_col)])
    # ---- the detail well: icon + name, state, separator, now, next, cost, need, how; the Buy line + buttons at its bottom
    fg0 = SUI.color_by([("so0", "disabled"), ("st0 == 1", "success"), ("st0 == 2", "info"), ("st0 == 3", "gold")], "disabled")
    frame = SUI.SLOT_FRAME
    name_w = TR_DET_IN_W - frame - 12
    sec_h = SUI.outer_size(SUI.section(None, "Effect"))[1]           # a vanilla section head with its margins (40)
    det_parts = [frame + 10, 26 + 4, sec_h, 44 + 6, 44 + 6, sec_h, 26 + 6, 44 + 6, sec_h, 66]
    buy_parts = [26 + 6, SUI.BTN_H]
    slack = SUI.fit(det_parts + buy_parts, TR_GRID_H - 2 * SUI.WELL_PAD, "detail well")
    det = [app("SkyyTrBody", SUI.panel("SkyyTrDet", "well", w=TR_DET_W, h=TR_GRID_H, anchor={"left": TR_DET_GAP})),
           app("SkyyTrDet", SUI.group("SkyyTrDetTop", "Left", h=frame, anchor={"bottom": 10})),
           app("SkyyTrDetTop", SUI.item_frame("SkyyTrDetFrame", frame, icon_id="SkyyTrDetIcon",
                                              item=SUI.J("@PKG@.TreeDefs.ICON[i0]", "Tool_Pickaxe_Iron"))),
           app("SkyyTrDetTop", SUI.label("SkyyTrDetName", "", "rowName", w=name_w, h=frame, wrap=True, col=fg0, anchor={"left": 12})),
           app("SkyyTrDet", SUI.label("SkyyTrDetState", "", "bold", h=26, col=fg0, anchor={"bottom": 4})),
           app("SkyyTrDet", SUI.section(None, "Effect")),
           app("SkyyTrDet", SUI.label("SkyyTrDetNow", "", "default", h=44, wrap=True, col="value", anchor={"bottom": 6})),
           app("SkyyTrDet", SUI.label("SkyyTrDetNext", "", "default", h=44, wrap=True, anchor={"bottom": 6})),
           app("SkyyTrDet", SUI.section(None, "Cost")),
           app("SkyyTrDet", SUI.label("SkyyTrDetCost", "", "bold", h=26, col="gold", anchor={"bottom": 6})),
           app("SkyyTrDet", SUI.label("SkyyTrDetNeed", "", "default", h=44, wrap=True, col="error", anchor={"bottom": 6})),
           app("SkyyTrDet", SUI.section(None, "How it works")),
           app("SkyyTrDet", SUI.label("SkyyTrDetHow", "", "summary", h=66, wrap=True, max_lines=False))]
    buy_col = SUI.color_by([("can", "gold"), ("so0", "disabled"), ("mx0", "success")], "disabled")
    buy = [app("SkyyTrDet", SUI.label("SkyyTrBuyTx", "", "bold", h=26, col=buy_col, anchor={"top": slack, "bottom": 6})),
           app("SkyyTrDet", SUI.group("SkyyTrBuyRow", "Left", h=SUI.BTN_H)),
           chain(["so0", "mx0", "d.lv[i0] == 0"], "SkyyTrBuyRow", [
               SUI.button("SkyyTrBuy", "Coming later", "secondary", w=TR_BUY_W, disabled=True),
               SUI.button("SkyyTrBuy", "Maxed", "secondary", w=TR_BUY_W, disabled=True),
               SUI.choose(SUI.J("can"), SUI.button("SkyyTrBuy", "Unlock", "primary", w=TR_BUY_W),
                          SUI.button("SkyyTrBuy", "Unlock", "primary", w=TR_BUY_W, disabled=True)),
               SUI.choose(SUI.J("can"), SUI.button("SkyyTrBuy", "Level up", "primary", w=TR_BUY_W),
                          SUI.button("SkyyTrBuy", "Level up", "primary", w=TR_BUY_W, disabled=True))])]
    toggle = app("SkyyTrBuyRow", SUI.choose(SUI.J("d.off[i0]"),
                                            SUI.button("SkyyTrToggle", "Turn on", "secondary", w=TR_BUY_W, anchor={"left": 8}),
                                            SUI.button("SkyyTrToggle", "Turn off", "secondary", w=TR_BUY_W, anchor={"left": 8})))
    # ---- result line, separator, footer: < Skills left, Respec right (armed = Destructive, one static label per tree)
    foot = [app(body, SUI.result_line("SkyyTrMsg", SUI.J("infoColor(this.msg)", SUI.COLOR["success"]), h=TR_MSG_H, anchor={"top": 8})),
            app(body, SUI.separator("content", anchor={"top": 8, "bottom": 8})),
            app(body, SUI.group("SkyyTrFoot", "Left", h=TR_FOOT_H)),
            app("SkyyTrFoot", SUI.button("SkyyTrBack", "< Skills", "secondary", w=TR_BACK_W, sound="cancel"))]
    respec = []
    for n, name in enumerate(TREES):
        on = SUI.button("SkyyTrRespec", "Click again to respec " + name, "destructive", w=TR_RESPEC_ON_W,
                        anchor={"left": SUI.right_margin(W - TR_BACK_W, TR_RESPEC_ON_W)})
        off = SUI.button("SkyyTrRespec", "Respec " + name, "secondary", w=TR_RESPEC_OFF_W,
                         anchor={"left": SUI.right_margin(W - TR_BACK_W, TR_RESPEC_OFF_W)})
        respec.append(("if (t == %d) " % n if n == 0 else "else if (t == %d) " % n) + app("SkyyTrFoot", SUI.choose(SUI.J("armed"), on, off)))
    parts = {
        "SHELL": sh.java("b"),
        "HEAD": app(body, SUI.group("SkyyTrHead", "Left", h=TR_HEAD_H, anchor={"bottom": TR_HEAD_GAP})),
        "TAB": chain(["i == %d" % n for n in range(len(TREES))], "SkyyTrHead", tabs),
        "INFO": "\n".join(info), "GRID": "\n".join(grid), "ROW": "\n".join(row), "CELL": cells, "DET": "\n".join(det),
        "BUY": "\n".join(buy), "TOGGLE": toggle, "FOOT": "\n".join(foot), "RESPEC": "\n".join(respec),
    }
    sh.appends.check(TR_PREFIX)           # the window frame: ids, prefix, parents, markup rules (every runtime append: java_append)
    SUI.assert_proven(marks, what="TreePage")      # proven properties only (minus skyyui.PROBED): every branch of every state
    indent = {"SHELL": 2, "HEAD": 2, "TAB": 4, "INFO": 2, "GRID": 2, "ROW": 4, "CELL": 6, "DET": 2, "BUY": 2, "TOGGLE": 4, "FOOT": 2,
              "RESPEC": 2}
    java = TR_BUILD
    for name, part in parts.items():
        tok = "{{" + name + "}}"
        assert java.count(tok) == 1, "unused / doubled Java part " + name
        java = java.replace(tok, "\n".join((" " * indent[name] + ln) if ln.strip() else ln for ln in part.split("\n")))
    assert not re.findall(r"\{\{[A-Z]+\}\}", java), "unfilled Java placeholder"
    for ident in TR_OLD_IDS:              # every 0.2.4 element id is still created (runtime ids: "#<id>" + (k) / (s))
        assert ("#%s {" % ident) in java or ('#%s" + (' % ident[:-1]) in java, "0.2.5 dropped the 0.2.4 element id #" + ident
    return java, sh, marks


TR_BUILD_JAVA, TR_SHELL, TR_MARKUPS = tree_page_java()
print("tree page %dx%d (body %dx%d): grid %d + detail %d, %d markups proven, kit %s" % (
    TR_SHELL.w, TR_SHELL.h, TR_SHELL.inner_w, TR_SHELL.inner_h, TR_GRID_W, TR_DET_W, len(TR_MARKUPS), SUI.kit_id()))

'''
rep("@@PAGE_KIT@@", PAGE_KIT)
rep("@@PAGE_BUILD@@", "M(page, TR_INFO_COLOR)\nM(page, TR_BUILD_JAVA)\n")

# 0.2.4's build() statements that are not markup must all be in the 0.2.5 template, word for word (multiset of whole lines)
_old_lines = OLD_BUILD_SRC.split(LF)[1:]
_drop = ("b.appendInline(", "String hv = ", "String bg = ", "String fg = ", "String fg0 = ", "  line(b, ")
KEPT = [ln for ln in _old_lines if ln.strip() and not any(x in ln for x in _drop)]
_tpl = PAGE_KIT[PAGE_KIT.index('TR_BUILD = r"""'):PAGE_KIT.index('""".replace("__PER_ROW__"')].split(LF)
_missing = collections.Counter(KEPT) - collections.Counter(_tpl)
assert not _missing, "0.2.4 build() lines missing from the 0.2.5 template: %s" % list(_missing)
assert len(KEPT) >= 40, len(KEPT)
assert [ln for ln in _tpl if "ev.addEventBinding(" in ln] == BIND0, "event bindings / their order changed"
# the texts 0.2.4 appended inline (after safe()) or through line() are the same expressions b.set now
for old_frag, new_line in (
        ('line(b, "SkyyTrDetState", stateLine(d, i0, st0), ', 'b.set("#SkyyTrDetState.Text", stateLine(d, i0, st0));'),
        ('line(b, "SkyyTrDetNow", nowLine(d, i0), ', 'b.set("#SkyyTrDetNow.Text", nowLine(d, i0));'),
        ('line(b, "SkyyTrDetNext", nextLine(d, i0), ', 'b.set("#SkyyTrDetNext.Text", nextLine(d, i0));'),
        ('line(b, "SkyyTrDetCost", costLine(d, i0), ', 'b.set("#SkyyTrDetCost.Text", costLine(d, i0));'),
        ('line(b, "SkyyTrDetNeed", needLine(d, i0, lvl, tokA, dustA), ', 'b.set("#SkyyTrDetNeed.Text", needLine(d, i0, lvl, tokA, dustA));'),
        ('line(b, "SkyyTrDetHow", @PKG@.TreeDefs.HOW[i0].replace("%C", cd(i0)).replace("%K", @PKG@.TreeFx.djKey()), ',
         'b.set("#SkyyTrDetHow.Text", @PKG@.TreeDefs.HOW[i0].replace("%C", cd(i0)).replace("%K", @PKG@.TreeFx.djKey()));'),
        ('Text: \\"" + safe(buyText(d, i0, st0, lvl, tokA, dustA)) + "\\"; ', 'b.set("#SkyyTrBuyTx.Text", safe(buyText(d, i0, st0, lvl, tokA, dustA)));'),
        ('Text: \\"" + safe(@PKG@.TreeDefs.NAME[i]) + "\\"; ', 'b.set("#SkyyTrN" + s + "Nm.Text", safe(@PKG@.TreeDefs.NAME[i]));'),
        ('Text: \\"" + safe(cardSub(d, i, stt, lvl, tokA)) + "\\"; ', 'b.set("#SkyyTrN" + s + "Sb.Text", safe(cardSub(d, i, stt, lvl, tokA)));'),
        ('safe(armed ? "Click again to respec " + tn : "Respec " + tn)', 'boolean armed = this.armT == t && System.currentTimeMillis() - this.armAt <= 10000L;'),
        ('(d.off[i0] ? "Turn on" : "Turn off")', 'if (d.lv[i0] >= 1 && !@PKG@.TreeDefs.soon(i0)) {'),
        ('Text: \\"< Skills\\"; ', 'ev.addEventBinding(@BT@.Activating, "#SkyyTrBack", @EVD@.of("a", "trback"));')):
    assert OLD_BUILD_SRC.count(old_frag) == 1, "0.2.4 build() text source not found once: " + old_frag
    assert sum(1 for ln in _tpl if ln.strip() == new_line) == 1, "0.2.5 template line missing: " + new_line

# ================================================================================================ ready log line: the kit id
rep('log("[SkyyTrees] @VERSION@ ready - /tree; " + sum', 'log("[SkyyTrees] @VERSION@ ready (__KIT__) - /tree; " + sum')
rep('''  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""".replace("@VERSION@", VERSION))''', '''  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""".replace("@VERSION@", VERSION).replace("__KIT__", KIT_ID))''')

# ================================================================================================ checks on the result
assert s.count("registerSystem(") == REG0, "0.2.5 adds no system (one registerSystem per class)"
assert s.count("registerCommand(") == CMD0, "command registrations changed"
for kb in KEEP:
    fixed = kb.replace('}""".replace("@VERSION@", VERSION))', '}""".replace("@VERSION@", VERSION).replace("__KIT__", KIT_ID))')
    assert kb in s or fixed in s, "a block that must stay 0.2.4's changed: %s" % kb[:80]
_page = s[s.index("# ================= TreePage: the inline tree page (0.2.5"):s.index('M(page, r"""\npublic void handleDataEvent(')]
for c in ("#0b1524", "#101d30", "#27463a", "#3b6b54", "#172a22", "#dcffe8", "#262626", "#1d2c3c", "#5a1e1e", "#ffe08a", "#c8a0ff",
          "#9fb8cc", "#1c1414", "#16301f", "#10243d", "#3a3010", "#141414", "#dfe8f0", "#bfe8c8", "#ffb080", "#8fa6ba", "TextButtonStyle(Default: (Background: #",
          "def tbs(", "@BSG@", "@BSX@", "@BSOFF@", "@BSRED@", "@BTON@", "@BTOFF@", "SOON_FG", "FG[st"):
    assert c not in _page, "0.2.4 custom look left in the 0.2.5 page: " + c
assert "public static void line(" not in s and 'T["BSG"]' not in s
assert "import skyyui as SUI" in s and s.index("SUI.verify()") < s.index("J = B.start()"), "verify() must run before the build"
assert s.index("def tree_page_java(") < s.index("TR_BUILD_JAVA, TR_SHELL, TR_MARKUPS = tree_page_java()") < s.index("M(page, TR_BUILD_JAVA)")
assert s.index("M(page, TR_INFO_COLOR)") < s.index("M(page, TR_BUILD_JAVA)"), "javassist: infoColor before its caller build()"
# the rest of the script outside the page region and the changed lines is 0.2.4's, line for line
_a0, _a1 = OLD.index("\nHERE = os.path.dirname"), OLD.index("# ================= TreePage: the inline tree page =================")
_b0, _b1 = s.index("\nHERE = os.path.dirname"), s.index("# ================= TreePage: the inline tree page (0.2.5")
_old_mid = OLD[_a0:_a1].replace('VERSION = "0.2.4"', 'VERSION = "0.2.5"')
_new_mid = s[_b0:_b1]
_ins = [ln for ln in _new_mid.split(LF)]
_diff = collections.Counter(_ins) - collections.Counter(_old_mid.split(LF))
assert all(("UI_DATA_COLORS" in ln or ln.startswith("# ") or "skyyui" in ln or "SUI." in ln) for ln in _diff), \
    "unexpected new lines before the page: %s" % list(_diff)[:5]
assert not (collections.Counter(_old_mid.split(LF)) - collections.Counter(_ins)), "a 0.2.4 line before the page went missing"
_c0 = OLD.index('M(page, r"""\npublic void handleDataEvent(')
_d0 = s.index('M(page, r"""\npublic void handleDataEvent(')
assert OLD[_c0:].replace('ready - /tree; " + sum', 'ready (__KIT__) - /tree; " + sum').replace(
    '}""".replace("@VERSION@", VERSION))', '}""".replace("@VERSION@", VERSION).replace("__KIT__", KIT_ID))') == s[_d0:], \
    "the script after TreePage.build differs from 0.2.4 beyond the ready line"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.2.4
print("wrote", dst, "(%d lines; 0.2.4 had %d)" % (s.count(LF), OLD.count(LF)))
