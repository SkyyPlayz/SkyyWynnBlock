"""Derive SkyyClasses/build_skyyclasses_0.1.8.py from the LIVE 0.1.7 (build_skyyclasses_0.1.7.py = the tools/deploy_set.py SET pin).
Run:  python tools/classes_0_1_8_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.8.py   (never --deploy: coordinated deploy)
EDITED-SCRIPTS RULE (commit ab75b6c): the lineage is Skyy's EDITED 0.1.6 -> tools/classes_0_1_7_patch.py -> the generated 0.1.7 read
here; tools/classes_0_1_6_patch.py is NEVER re-run. Edit THIS file, never the generated build script.

0.1.8 = the vanilla UI pass (Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them to look and feel
vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md section 7; research/Skyy-UI-Inventory.md 5.5 + section 6
"Class cards"). ONLY THE LOOK OF ClassPage (/class) CHANGES - a look-only restyle on the shared kit tools/skyyui.py (1.3):
  - the generated script imports skyyui as SUI and calls SUI.verify() before anything else (every vanilla value the page uses is
    proven against Assets.zip at every build) and puts SUI.kit_id() into the ready log line;
  - a SKYY CARD block (the ONE shared card component, identical in SkyyProfiles 0.1.3 - tools/profiles_0_1_3_patch.py; both patches
    assert the same hash, CARD_SHA) builds the class cards from kit calls;
  - ClassPage.build() is generated at build time by class_page_java(): 0.1.7's statements (profile lock / no-profile gates, cur,
    the sub / title / question / footer texts, the action chain Selected / Coming soon / Locked / Choose-Switch, the pending state,
    the 3 event bindings clspick<i> / clsyes / clsno with their EventData) are kept word for word - asserted below against the
    0.1.7 method; only the appends changed, and the texts go in with b.set (0.1.7 wrote them inline after safe(); the same safe()
    text is b.set now). The inline confirm row is the kit's confirm_view(compact=True) with 0.1.7's ids #SkyyClsConfirm /
    #SkyyClsYes / #SkyyClsNo.
  - UI_DATA_COLORS lists the class colours (ClassDefs.COLORS = data colours, research/Vanilla-UI-Style-Guide.md section 5) and the
    chat line colours (Message.color, not page chrome) for the kit lint.
  - review fixes (second pass, 2026-09-29): CARD_LOOKS["selected"] = the row pressed step (contrast), the description box 40 px;
    the CARD block hash moved with it (CARD_SHA, the same in both patches). Harness: SkyyClasses/test_skyyclasses_0.1.8.py part Y.
Everything else (commands, permissions, config keys + rows, files, bridge keys, the first-join OpenTask gates, ClassPage's fields,
constructor, safe(), handleDataEvent, every other class) is byte-identical to 0.1.7 - asserted below (KEEP blocks).
"""
import collections
import hashlib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.7.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.8.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
# the source must be the generated 0.1.7 of the EDITED lineage (Skyy's ab75b6c edits carried through classes_0_1_7_patch.py)
assert 'VERSION = "0.1.7"' in s and "DEF_HEAL_MSG_MS = 10000   # LOCKED Skyy 2026-09-25" in s, "build_skyyclasses_0.1.7.py is not the live 0.1.7"
assert "derived from the EDITED 0.1.6 script by tools/classes_0_1_7_patch.py" in s, "0.1.7 is not the edited-lineage script"
REG0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
assert len(BIND0) == 3, "0.1.7 has 3 event bindings (all in ClassPage), found %d" % len(BIND0)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)


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


# blocks that must come out of this patch byte-identical (everything but the docstring head, VERSION, the kit import, the data
# colour list, ClassPage's look and the ready log line)
KEEP = [block("\nHERE = os.path.dirname(os.path.abspath(__file__))", "# usable by every class (and by classless players)"),
        block("# usable by every class (and by classless players)", "# ================= ClassPage: /class ================="),
        block('F(page, "public int pending;")', 'M(page, (r"""\npublic void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {'),
        block('M(page, r"""\npublic void handleDataEvent(', 'getLogger().at(java.util.logging.Level.INFO).log("[SkyyClasses] __VER__ ready'),
        block('M(pl, r"""\nprotected void shutdown() {', "if \"--deploy\" in sys.argv:")]

# ================================================================================================ docstring
rep('''"""SkyyClasses 0.1.7 - build script (javassist via jpype; derived from the EDITED 0.1.6 script by tools/classes_0_1_7_patch.py - edit the
patch, not this file; classes_0_1_6_patch.py is never re-run). Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.8 - build script (javassist via jpype). GENERATED by tools/classes_0_1_8_patch.py from the LIVE 0.1.7 (the EDITED
lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7) - edit the patch, not this file; classes_0_1_6_patch.py is never re-run.
Wynncraft-style classes for SkyWynn.
0.1.8 (2026-09-29, the vanilla UI pass - Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them to look and
  feel vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md): ONLY THE LOOK OF THE /class PAGE CHANGED, on the
  shared kit tools/skyyui.py. Commands, permissions, config, files, bridge keys, the first-join page gates, every element id of 0.1.7,
  the 3 event bindings (clspick<i>, clsyes, clsno), the pending / info state and every text are 0.1.7's (the patch asserts it).
  - The build calls SUI.verify() first (every vanilla style value / texture / sound the page uses is proven against Assets.zip,
    read-only; a game update that changes one stops the build); KIT_ID (kit version + file hash) is in the ready log line.
  - Window: the vanilla decorated container (ContainerHeader title bar with runes + the two gold ornaments, title CLASSES in the
    15 px Secondary title style, the ContainerPatch body, padding 17), 1100 x 854; 0.1.7's root #SkyyCls is the body now. Gone: the
    dark-blue root, the copper accent stripe, the custom title, the empty Label spacers.
  - Class cards = the SKYY CARD component (the same code as SkyyProfiles 0.1.3's cards) in a vanilla list well (#000000(0.15),
    padding 4): a 4 px status bar, weapon icons in vanilla item slot borders (BarterTradeRow #1a2530), the class name in the class
    colour (data colour), the combat skill line in the property value colour, the description in the list row caption colour
    (wraps to two lines), the action column. Looks: your class = the list row's pressed step #182a40(0.9) + the selected blue bar;
    waiting for Confirm = the hovered row + a yellow bar (the confirm question colour); open = the list row panel; coming soon =
    BarterTradeRow's disabled card, grey text and the sold-out cover over the icons.
  - Buttons: Choose / Switch = vanilla Secondary (Primary while that class waits for Confirm, like 0.1.7's green); state words
    Selected (vanilla success green) and Coming soon / Locked (vanilla disabled grey).
  - Confirm: the kit's in-page confirm_view(compact=True) - the question in the vanilla confirm yellow, Confirm = Primary with the
    save sound, Cancel = Secondary with the cancel sound - on a list well. Info line = the vanilla info blue, bold; footer = the
    vanilla caption grey. Esc closes the page as before (no new button, no new binding).
  - Texts are b.set now (0.1.7 put them inline); the text itself is unchanged (still passed through safe()).
  - Review fixes (2026-09-29, second pass): the selected card background is the WorldEventListRow pressed step #182a40(0.9), not
    the active tint #7a9cc6(0.25) (Berserker red 2.6:1 -> 3.4:1; a profile locked to Assassin / Shaman: disabled grey 2.7:1 ->
    3.5:1); the two-line description box is 40 px (was 38 + 2 spare). The page-state harness (SkyyClasses/test_skyyclasses_0.1.8.py
    part Y) builds ClassPage in both jars and checks bindings, ids, texts, markup and layout.
  UNVERIFIED (needs the game): the kit's "base" look has not been seen in game yet (skyyui probe pages base1 / base2 / base3).
''')
rep("Run:   python build_skyyclasses_0.1.7.py            -> SkyyClasses/SkyyClasses-0.1.7.jar",
    "Run:   python build_skyyclasses_0.1.8.py            -> SkyyClasses/SkyyClasses-0.1.8.jar")

# ================================================================================================ version, kit import, data colours
rep('VERSION = "0.1.7"', 'VERSION = "0.1.8"')
rep("import skyybuild as B\n", """import skyybuild as B
import skyyui as SUI       # 0.1.8: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"
SUI.verify()               # proves every vanilla value / texture / sound the page uses against Assets.zip (read-only); stops the build on drift
KIT_ID = SUI.kit_id()      # "skyyui <version> <blob12>" - in the ready log line
""")
rep("""# usable by every class (and by classless players)
FREE_WEAPONS = """, """# 0.1.8: DATA colours for the vanilla UI kit's lint (research/Vanilla-UI-Style-Guide.md section 5): the class colours
# (ClassDefs.COLORS - class names on the /class cards; checked against CLASSES right below) + the chat line colours (Message.color,
# not page chrome)
UI_DATA_COLORS = ["#8fd67a", "#e0b060", "#7fb0e0", "#d9443f", "#f2e6a0", "#b58cff", "#ff7a5c"] + ["#8fe39a", "#ffc800", "#ff9d6b"]
assert sorted(set(UI_DATA_COLORS[:len(CLASSES)])) == sorted(set(c["color"] for c in CLASSES)), "UI_DATA_COLORS must start with the CLASSES colours"
# usable by every class (and by classless players)
FREE_WEAPONS = """)

# ================================================================================================ ClassPage: the look only
OLD_LOOK = cut("# 0.1.6: 15 pt buttons, 1000 x 900 root (7 cards, fits 1080)", 'F(page, "public int pending;")', "@@CARD_AND_PAGE@@")
assert "BTN_GO = " in OLD_LOOK and "PAGE_W, PAGE_H = 1000, 900" in OLD_LOOK
OLD_BUILD = cut('M(page, (r"""\npublic void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {', 'M(page, r"""\npublic void handleDataEvent(',
                "@@BUILD@@")
CARD_BLOCK = r'''# =====================================================================================================================
# SKYY CARD - the ONE shared card component (research/Skyy-UI-Inventory.md 5.5, 5.17 and section 6 "Class cards"): the class
# cards of SkyyClasses' ClassPage and of SkyyProfiles' Create Profile page, SkyyProfiles' profile cards and its empty-slot card.
# Built from kit calls only (tools/skyyui.py). THE SAME BLOCK is in SkyyClasses 0.1.8 and SkyyProfiles 0.1.3: both patches
# (tools/classes_0_1_8_patch.py, tools/profiles_0_1_3_patch.py) insert it and assert its hash - change it in both together.
# A card is one row of a list well (the vanilla #000000(0.15) list inset, padding 4): Group <card> (LayoutMode Left) = a 4 px status
# bar <card>Bar + the card body <card>In (the state background; side by side, so a look without a bar is one plain colour) holding
# the item cells (the vanilla BarterTradeRow slot border with an ItemIcon) | the text column (up to three label lines, their Text
# is b.set) | the action column (a vanilla button or a state word, appended by the page). Only
# properties the deployed pages already use: LayoutMode Left / Top, fixed widths / heights, Anchor margins, Padding, colour
# backgrounds, ItemIcon with an inline ItemId, Wrap (no FlexWeight, no WrapMaxLines, no LayoutMode Center / Full).
# =====================================================================================================================
CARD_H = 84                 # card height: name 24 + line two 20 + line three 40 (two wrapped lines; review fix: was 38 + 2 spare,
                            # a two-line 15 px text needs ~41 px at the game's Nunito Sans line height)
CARD_GAP = 4                # space under each card (the OverrideRespawnPointButton option rows: 50 + 4)
CARD_BAR = 4                # status bar at the left edge (WorldEventListRow #StatusBar: 4 px)
CARD_FRAME = 64             # item cell border (BarterTradeRow slot border #1a2530, padding 2) around a 60 px ItemIcon
CARD_CELL = CARD_FRAME + 8  # one icon cell: an 8 px gap + the frame
CARD_ACT_W = 200            # action column: a vanilla normal button (172 = @DefaultButtonMinWidth) centred in it
CARD_BTN_W = SUI.BTN_MIN_W
CARD_PAD_R = 12             # space right of the action column
CARD_LIST_PAD = SUI.WELL_LIST_PAD   # the list well's padding (WorldEventPanelPage #ListContainer: 4)
# card looks: (background, status bar), kit colour names
CARD_LOOKS = {
    "selected": ("rowPressed", "selected"),    # your class / the picked class / the active profile: the WorldEventListRow pressed
                                               # step #182a40(0.9) + its selected blue #4274a5 as the bar (review fix: the active
                                               # tint #7a9cc6(0.25) put the Berserker red at 2.6:1 and the disabled grey at 2.7:1;
                                               # on the pressed step every card text is >= 3.4:1; vanilla's solid #4274a5 row
                                               # would drop the class colours to 1.1-2:1)
    "pending": ("rowHover", "warning"),        # waiting for Confirm: the hovered row #132033(0.8) + the confirm question yellow bar
    "normal": ("row", "row"),                  # the WorldEventListRow panel #101925(0.55); the bar in the card colour = no bar
    "off": ("cardDisabled", "cardDisabled"),   # coming later: BarterTradeRow's disabled card #1a1e24 (+ grey text, covered icons)
    "empty": ("well", "well"),                 # an empty slot: one more step of the list well tone
}


def card_list_h(rows):
    """The height of a list well holding `rows` cards (padding 4 + rows x (card + gap))."""
    return 2 * CARD_LIST_PAD + rows * (CARD_H + CARD_GAP)


def card_list(ident, h, anchor=None):
    """The list well the cards go into (a vanilla panel "well", LayoutMode Top, padding 4)."""
    return SUI.panel(ident, "well", h=h, pad=CARD_LIST_PAD, anchor=anchor)


def card_text_w(w, icon_max):
    """The text column width of a w px card with icon_max item cells."""
    tw = w - CARD_BAR - icon_max * CARD_CELL - CARD_ACT_W - CARD_PAD_R
    SUI.fit([CARD_BAR, icon_max * CARD_CELL, tw, CARD_ACT_W, CARD_PAD_R], w, "card width")
    assert tw >= 240, "card text column too narrow: %d px" % tw
    return tw


def _card_in(outer, *kids):
    """kit markup `outer` with the kit markups `kids` placed inside it (before its closing brace)."""
    assert outer.endswith("}") and kids, outer[:60]
    return outer[:-1] + " ".join(kids) + " }"


def _card_col(col, on):
    """A line colour: a kit colour name or a J(java expr, sample) data colour; with on (a Java boolean expression) the vanilla
    disabled grey when it is false."""
    c = SUI.color(col)
    if on is None:
        return c
    sample = SUI.render(c) if SUI.has_j(c) else c
    return SUI.J("(%s) ? (%s) : %s" % (on, SUI.java_value(c), SUI.java_lit(SUI.COLOR["disabled"])), sample)


def _card_look(look, var):
    """(java declarations, background, bar) for a static look name or [(look, java boolean), ..., last look]."""
    if isinstance(look, str):
        bg, bar = CARD_LOOKS[look]
        return [], SUI.color(bg), SUI.color(bar)
    conds, last = list(look[:-1]), look[-1]
    assert conds and isinstance(last, str), look
    e_bg, e_bar = SUI.java_lit(SUI.color(CARD_LOOKS[last][0])), SUI.java_lit(SUI.color(CARD_LOOKS[last][1]))
    for name, cond in reversed(conds):
        e_bg = "(%s) ? %s : (%s)" % (cond, SUI.java_lit(SUI.color(CARD_LOOKS[name][0])), e_bg)
        e_bar = "(%s) ? %s : (%s)" % (cond, SUI.java_lit(SUI.color(CARD_LOOKS[name][1])), e_bar)
    first = CARD_LOOKS[conds[0][0]]
    decl = ["String %sBg = %s;" % (var, e_bg), "String %sBar = %s;" % (var, e_bar)]
    return decl, SUI.J(var + "Bg", SUI.color(first[0])), SUI.J(var + "Bar", SUI.color(first[1]))


def _card_cell(fid, item, on):
    """One item cell: an 8 px gap + the slot border (padding 2) with the ItemIcon; the coming-later look lays the vanilla
    sold-out cover (BarterTradeRow #0a0e12(0.75)) over it. With on: both looks, picked in the Java (choose)."""
    cell = SUI.group(None, None, w=CARD_CELL, h=CARD_H)
    frame = SUI.item_frame(fid, CARD_FRAME, anchor={"left": CARD_CELL - CARD_FRAME, "top": (CARD_H - CARD_FRAME) // 2})
    icon = SUI.item_icon(None, item, CARD_FRAME - 4, anchor={"left": 0, "top": 0})
    live = _card_in(cell, _card_in(frame, icon))
    if on is None:
        return live
    cover = SUI.group(None, None, anchor={"full": 0}, extra="Background: %s" % SUI.COLOR["cardOverlay"])
    return SUI.choose(SUI.J(on), live, _card_in(cell, _card_in(frame, icon, cover)))


def card_java(ids, w, look, lines, icons=None, icon_item=None, icon_max=1, on=None, var="card", k="k", b="b"):
    """Java statements that append ONE card (they go inside the page's Java loop; ids / texts / colours may be J() values):
      ids       {"list": the list well, "card", "icons" (None = <card>Ics), "text", "act"} - the page's OLD element ids
      w         the card width (the list well's inner width)
      look      a CARD_LOOKS name, or [(look, java boolean), ..., last look name]: the first true condition wins
      lines     [{"id": suffix, "text": java String expression, "kind": label kind, "h": px, "col": kit colour name or
                J(java expr, sample), "wrap": bool, "tag": {"id", "text", "col", "w", "kind"}}] - the label is <card><suffix>; a tag
                is a second, right-aligned label on the same row (<card><tag id>, the row <card><suffix>Row)
      icons     a Java String[] expression (one cell per entry, at most icon_max; icon_item = J(item id of entry k)), or
                icons=None and icon_item = J(one item id): one cell
      on        a Java boolean: false = the coming-later look (grey text, covered icons); None = always on
    The page appends the action column content (card_button / card_state) into ids["act"] afterwards."""
    card, text, act = ids["card"], ids["text"], ids["act"]
    icons_id = ids.get("icons") or card + "Ics"
    tw = card_text_w(w, icon_max)
    decl, bg, bar = _card_look(look, var)
    out = list(decl)
    body = card + "In"
    out.append(SUI.java_append(ids["list"], SUI.group(card, "Left", h=CARD_H, anchor={"bottom": CARD_GAP}), b))
    out.append(SUI.java_append(card, SUI.group(card + "Bar", None, w=CARD_BAR, h=CARD_H, extra="Background: %s" % bar), b))
    out.append(SUI.java_append(card, SUI.group(body, "Left", w=w - CARD_BAR, h=CARD_H, extra="Background: %s" % bg), b))
    out.append(SUI.java_append(body, SUI.group(icons_id, "Left", w=icon_max * CARD_CELL, h=CARD_H), b))
    if icons is None:
        out.append(SUI.java_append(icons_id, _card_cell(card + "F0", icon_item, on), b))
    else:
        out.append("for (int %s = 0; %s < %s.length && %s < %d; %s++) {" % (k, k, icons, k, icon_max, k))
        out.append("  " + SUI.java_append(icons_id, _card_cell(card + "F" + SUI.J(k), icon_item, on), b))
        out.append("}")
    top = SUI.fit([ln["h"] for ln in lines], CARD_H, "card text lines") // 2
    out.append(SUI.java_append(body, SUI.group(text, "Top", w=tw, h=CARD_H, pad={"top": top} if top else None), b))
    sets = []
    for ln in lines:
        lid, col = card + ln["id"], _card_col(ln["col"], on)
        tag = ln.get("tag")
        if tag is None:
            out.append(SUI.java_append(text, SUI.label(lid, "", ln["kind"], h=ln["h"], col=col, wrap=ln.get("wrap", False)), b))
        else:
            row, tid = card + ln["id"] + "Row", card + tag["id"]
            out.append(SUI.java_append(text, SUI.group(row, "Left", h=ln["h"]), b))
            out.append(SUI.java_append(row, SUI.label(lid, "", ln["kind"], w=tw - tag["w"], h=ln["h"], col=col, wrap=False), b))
            out.append(SUI.java_append(row, SUI.label(tid, "", tag.get("kind", "default"), w=tag["w"], h=ln["h"],
                                                      col=_card_col(tag["col"], on), align="End", wrap=False), b))
        sets.append(SUI.java_set(lid, "Text", SUI.J(ln["text"]), b))
        if tag is not None:
            sets.append(SUI.java_set(tid, "Text", SUI.J(tag["text"]), b))
    out.extend(sets)
    out.append(SUI.java_append(body, SUI.group(act, "Top", w=CARD_ACT_W, h=CARD_H, pad={"top": (CARD_H - SUI.BTN_H) // 2,
                                                                                            "left": (CARD_ACT_W - CARD_BTN_W) // 2}), b))
    return "\n".join(out)


def card_button(ident, text, kind="secondary", sound=None):
    """The card's action button: a vanilla normal text button (172 x 44) - append it into the card's action column."""
    return SUI.button(ident, text, kind, w=CARD_BTN_W, sound=sound)


def card_state(text, kind):
    """A state word in the action column instead of a button: Selected / Active = the vanilla success green, Locked / Coming
    soon / Coming later = the vanilla disabled grey (both bold, centred where the button would be)."""
    return SUI.label(None, text, kind, w=CARD_BTN_W, h=SUI.BTN_H, align="Center", bold=True)


def java_block(src, indent):
    """Java statements re-indented by `indent` spaces (for pasting kit output into a method template)."""
    return "\n".join((" " * indent + ln) if ln.strip() else ln for ln in src.split("\n"))


def java_fill(tpl, parts):
    """A Java method template with {{NAME}} placeholders filled with the kit-built Java in parts (each placeholder used at least
    once, none left over)."""
    out = tpl
    for name, java in parts.items():
        tok = "{{" + name + "}}"
        assert tok in out, "unused Java part " + name
        out = out.replace(tok, java)
    left = re.findall(r"\{\{[A-Z0-9]+\}\}", out)
    assert not left, "unfilled Java placeholder: %s" % left
    return out
# ======================================================================= (end of the shared SKYY CARD block)'''
PAGE_BLOCK = r'''# 0.1.8 (the vanilla UI pass): ClassPage's look = the vanilla UI kit + the shared SKYY CARD above. class_page_java() builds the
# markup with kit calls at BUILD time (every value proven by SUI.verify()) and returns build()'s Java: 0.1.7's statements (state,
# texts, the action chain, the 3 event bindings) are kept word for word (the patch asserts it); only the appends changed and the
# texts now go in with b.set (0.1.7 wrote them inline). Page: the decorated window (1100 wide; the body is 0.1.7's root #SkyyCls),
# the sub line, the class cards in a list well, the info line, then the in-page confirm (kit confirm_view, compact) or the footer.
CLS_W = 1100
CLS_PREFIX = "SkyyCls"
CLS_SUB_H, CLS_INFO_H, CLS_END_H = 44, 28, SUI.BTN_H + 16      # sub line (two lines), info line, confirm row / footer (+ margins)
CLS_IDS_017 = ["SkyyCls", "SkyyClsSub", "SkyyClsCard0", "SkyyClsIco0", "SkyyClsTxt0", "SkyyClsAct0", "SkyyClsPick0", "SkyyClsInfo",
               "SkyyClsConfirm", "SkyyClsYes", "SkyyClsNo", "SkyyClsFoot"]      # every element id of the 0.1.7 page (kept)
CLS_BUILD = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  int pi = @PKG@.ClassStore.profileIndex(u);
  boolean lockp = pi >= 0;
  boolean np = !lockp && @PKG@.ClassCfg.needsProfile(u);
  int cur = lockp ? pi : @PKG@.ClassStore.classIndex(u);
{{SHELL}}
  String sub = cur < 0 ? "You have no class yet - your first choice is free. Your class decides your weapons and your combat skill."
    : "You are " + @PKG@.ClassDefs.article(@PKG@.ClassDefs.NAMES[cur]) + " - combat skill " + @PKG@.ClassDefs.SKILLS[cur] + ". Only " + @PKG@.ClassDefs.NAMES[cur] + " weapons deal damage for you.";
  if (lockp) sub = "Your class is locked to this profile - you are " + @PKG@.ClassDefs.article(@PKG@.ClassDefs.NAMES[cur]) + " with combat skill " + @PKG@.ClassDefs.SKILLS[cur] + ". A new class means a new profile.";
  if (lockp && !@PKG@.ClassDefs.ENABLED[cur]) sub = "This profile is locked to " + @PKG@.ClassDefs.NAMES[cur] + " - not playable yet. Its weapons deal no damage until it is released.";
  if (np) sub = "You have no profile yet. Type /profiles to create one - you pick your class there and it is locked to that profile.";
{{SUB}}
{{LIST}}
  for (int i = 0; i < @PKG@.ClassDefs.NAMES.length; i++) {
    boolean on = @PKG@.ClassDefs.ENABLED[i];
    boolean sel = i == cur;
    boolean pend = i == this.pending;
    String[] ic = @PKG@.ClassDefs.ICONS[i].split(",");
    String title = @PKG@.ClassDefs.NAMES[i] + (sel ? " - your class" : (on ? " - " + @PKG@.ClassDefs.ROLES[i] : " - coming soon"));
{{CARD}}
    if (lockp && sel) {
{{SELECTED}}
    } else if (!on) {
{{SOON}}
    } else if (sel) {
{{SELECTED}}
    } else if (lockp || np) {
{{LOCKED}}
    } else {
{{PICK}}
      ev.addEventBinding(@BT@.Activating, "#SkyyClsPick" + i, @EVD@.of("a", "clspick" + i));
    }
  }
{{INFO}}
  long cost = @PKG@.ClassCfg.SWITCH_COST;
  if (!lockp && !np && this.pending >= 0 && this.pending < @PKG@.ClassDefs.NAMES.length) {
    String pn = @PKG@.ClassDefs.NAMES[this.pending];
    String q = cur < 0 ? "Become " + @PKG@.ClassDefs.article(pn) + "? Your first choice is free."
      : "Switch to " + pn + " for " + cost + " coins? Your " + @PKG@.ClassDefs.NAMES[cur] + " progress is kept.";
{{CONFIRM}}
    ev.addEventBinding(@BT@.Activating, "#SkyyClsYes", @EVD@.of("a", "clsyes"));
    ev.addEventBinding(@BT@.Activating, "#SkyyClsNo", @EVD@.of("a", "clsno"));
  } else if (np) {
    String nf = "Your class comes from your profile - type /profiles to create it. Shields and tools work for every class. Hatchets are tools.";
{{FOOTNF}}
  } else if (lockp) {
    String pt = @PKG@.ClassCfg.profileText(u);
    String lf = "Class locked to " + (pt.length() > 0 ? pt : "this profile") + ". To play another class create a new profile. Shields and tools work for every class. Hatchets are tools.";
{{FOOTLF}}
  } else {
    String foot = "Switching costs " + cost + " coins (first choice free) - cooldown " + @PKG@.ClassCfg.COOLDOWN_MIN + " min"
      + (@PKG@.ClassStore.coinsReady() ? " - purse " + @PKG@.ClassStore.purse(u) + " coins" : "") + ". Shields and tools work for every class. Hatchets are tools.";
{{FOOT}}
  }
}"""


def class_page_java():
    """ClassPage.build(): CLS_BUILD with its {{parts}} built from kit calls. Heights fill the window body exactly (asserted)."""
    heights = [CLS_SUB_H + 10, card_list_h(len(CLASSES)), 8 + CLS_INFO_H, 8 + CLS_END_H]
    sh = SUI.page_shell("SkyyClsF", CLS_W, SUI.TITLE_H + 2 * SUI.CONTENT_PAD + sum(heights), "Classes", body_id="SkyyCls")
    assert sh.fit(heights) == 0, "the class page body must be filled exactly"
    body, W = sh.body, sh.inner_w
    i = SUI.J("i")
    act = "SkyyClsAct" + i
    ids = {"list": "SkyyClsList", "card": "SkyyClsCard" + i, "icons": "SkyyClsIco" + i, "text": "SkyyClsTxt" + i, "act": act}
    lines = [{"id": "Nm", "text": "safe(title)", "kind": "rowName", "h": 24, "col": SUI.J("@PKG@.ClassDefs.COLORS[i]", CLASSES[0]["color"])},
             {"id": "Sk", "text": 'safe("Combat skill " + @PKG@.ClassDefs.SKILLS[i] + " - " + @PKG@.ClassDefs.WTEXT[i])', "kind": "fieldLabel",
              "h": 20, "col": "value"},
             {"id": "Ds", "text": "safe(@PKG@.ClassDefs.DESCS[i])", "kind": "rowSub", "h": 40, "col": "rowSub", "wrap": True}]
    pick = "SkyyClsPick" + i
    foot = SUI.label("SkyyClsFoot", "", "caption", h=CLS_END_H, align="Center", wrap=True, anchor={"top": 8})
    confirm = SUI.confirm_view(body, "SkyyClsConfirm", W, question=SUI.J("safe(q)"), compact=True, top=8,
                               ids={"box": "SkyyClsConfirm", "yes": "SkyyClsYes", "no": "SkyyClsNo"})
    assert confirm.h == 8 + CLS_END_H
    parts = {
        "SHELL": sh.java("b"),
        "SUB": "\n".join([SUI.java_append(body, SUI.label("SkyyClsSub", "", "default", h=CLS_SUB_H, align="Center", wrap=True,
                                                           anchor={"bottom": 10})),
                          SUI.java_set("SkyyClsSub", "Text", SUI.J("safe(sub)"))]),
        "LIST": SUI.java_append(body, card_list("SkyyClsList", card_list_h(len(CLASSES)))),
        "CARD": card_java(ids, W - 2 * CARD_LIST_PAD, [("selected", "sel"), ("pending", "pend"), ("normal", "on"), "off"], lines,
                          icons="ic", icon_item=SUI.J("safe(ic[k])", CLASSES[0]["icons"][0]), icon_max=max(len(c["icons"]) for c in CLASSES),
                          on="on"),
        "SELECTED": SUI.java_append(act, card_state("Selected", "success")),
        "SOON": SUI.java_append(act, card_state("Coming soon", "disabled")),
        "LOCKED": SUI.java_append(act, card_state("Locked", "disabled")),
        "PICK": "if (pend) %s\nelse %s" % (
            SUI.java_append(act, SUI.choose(SUI.J("cur < 0"), card_button(pick, "Choose", "primary"), card_button(pick, "Switch", "primary"))),
            SUI.java_append(act, SUI.choose(SUI.J("cur < 0"), card_button(pick, "Choose"), card_button(pick, "Switch")))),
        "INFO": "\n".join([SUI.java_append(body, SUI.label("SkyyClsInfo", "", "info", h=CLS_INFO_H, bold=True, align="Center",
                                                            anchor={"top": 8})),
                           SUI.java_set("SkyyClsInfo", "Text", SUI.J("safe(this.info)"))]),
        "CONFIRM": confirm.java("b"),
    }
    for tok, var in (("FOOTNF", "nf"), ("FOOTLF", "lf"), ("FOOT", "foot")):
        parts[tok] = "\n".join([SUI.java_append(body, foot), SUI.java_set("SkyyClsFoot", "Text", SUI.J("safe(%s)" % var))])
    sh.appends.check(CLS_PREFIX)          # the window frame: ids, prefix, parents, markup rules (every runtime append: java_append)
    indent = {"SHELL": 2, "SUB": 2, "LIST": 2, "CARD": 4, "SELECTED": 6, "SOON": 6, "LOCKED": 6, "PICK": 6, "INFO": 2, "CONFIRM": 4,
              "FOOTNF": 4, "FOOTLF": 4, "FOOT": 4}
    java = java_fill(CLS_BUILD, dict((k, java_block(v, indent[k])) for k, v in parts.items()))
    for ident in CLS_IDS_017:             # every 0.1.7 element id is still created (runtime ids: "#<id>" + (i))
        assert ("#%s {" % ident) in java or ('#%s" + (i)' % ident[:-1]) in java, "0.1.8 dropped the 0.1.7 element id #" + ident
    return java, sh


CLS_BUILD_JAVA, CLS_SHELL = class_page_java()
print("class page %dx%d (body %dx%d): %d class cards, kit %s" % (CLS_SHELL.w, CLS_SHELL.h, CLS_SHELL.inner_w, CLS_SHELL.inner_h,
                                                                 len(CLASSES), SUI.kit_id()))'''
CARD_SHA = "85a047857ef2762641fb7045aee6f5ce9acd4e1ded05f55ba4a2a7496445f7d5"     # the SAME value in tools/profiles_0_1_3_patch.py: the card block is one component in both mods
assert hashlib.sha256(CARD_BLOCK.encode("utf8")).hexdigest() == CARD_SHA, "the SKYY CARD block differs from SkyyProfiles 0.1.3's"
rep("@@CARD_AND_PAGE@@", CARD_BLOCK + "\n" + PAGE_BLOCK + "\n")
rep("@@BUILD@@", "M(page, CLS_BUILD_JAVA)\n")

# 0.1.7's build() statements that are not markup must all be in the 0.1.8 template, word for word (multiset of whole lines)
_old_lines = OLD_BUILD.split(LF)[1:]
_drop = ("b.appendInline(", 'String bs = "__BTN__";', 'String go = "__BTNGO__";', "String bg = ", "String nameColor = ",
         "String textColor = ", '}""").replace("__BTN__"')
KEPT = [ln for ln in _old_lines if ln.strip() and not any(d in ln for d in _drop)]
# the weapon icon loop is markup now (the card component emits it): its header and its closing brace go with it
KEPT.remove("    for (int k = 0; k < ic.length && k < 4; k++) {")
KEPT.remove("    }")
_tpl = PAGE_BLOCK[PAGE_BLOCK.index('CLS_BUILD = r"""'):PAGE_BLOCK.index('"""\n\n\ndef class_page_java')].split(LF)
_missing = collections.Counter(KEPT) - collections.Counter(_tpl)
assert not _missing, "0.1.7 build() lines missing from the 0.1.8 template: %s" % list(_missing)
assert len(KEPT) >= 40, len(KEPT)
for ln in BIND0:                                            # the 3 bindings, word for word and in their order
    assert ln in _tpl, ln
assert [ln for ln in _tpl if "ev.addEventBinding(" in ln] == BIND0, "binding order changed"

# ================================================================================================ ready log line: the kit id
rep('log("[SkyyClasses] __VER__ ready - /class, /class kit, /class arrows, /classadmin; classes "',
    'log("[SkyyClasses] __VER__ ready (__KIT__) - /class, /class kit, /class arrows, /classadmin; classes "')
rep('''config also in game: SkyWynn Menu -> Server Setup -> Classes)");
}""".replace("__VER__", VERSION))''', '''config also in game: SkyWynn Menu -> Server Setup -> Classes)");
}""".replace("__VER__", VERSION).replace("__KIT__", KIT_ID))''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
for k in KEEP:
    assert k in s, "a block that must stay 0.1.7's changed: %s" % k[:80]
_page = s[s.index("# ================= ClassPage: /class ================="):s.index('M(page, r"""\npublic void handleDataEvent(')]
for c in ("#0b1524", "#d08a4a", "#ffe9c9", "#9fb8cc", "#173524", "#3a2f1a", "#142030", "#0d1219", "#5f6b78", "#9fd8a2", "#c9d6e2",
          "#8fa4b8", "#ffd27a", "#5a4420", "#8a6a30", "#3a2a10", "#2f6a3a", "#3f8a4a", "#1f4a2a", "#e9ffe9", "TextButtonStyle(Default: (Background: #"):
    assert c not in _page, "0.1.7 custom look left in the 0.1.8 page: " + c
assert "import skyyui as SUI" in s and s.index("SUI.verify()") < s.index("J = B.start()"), "verify() must run before the build"
assert s.index("def card_java(") < s.index("CLS_BUILD_JAVA, CLS_SHELL = class_page_java()") < s.index("M(page, CLS_BUILD_JAVA)")
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.1.7 had %d)" % (s.count(LF), OLD.count(LF)))
