"""Derive SkyyCollections/build_skyycollections_0.2.4.py from the LIVE 0.2.3 (build_skyycollections_0.2.3.py = the tools/deploy_set.py
SET pin; 0.2.3 stays untouched; same style as coll_0_2_3_patch.py: rep() / cut() with asserted anchors).
Run:  python tools/coll_0_2_4_patch.py   then   python SkyyCollections/build_skyycollections_0.2.4.py   (never --deploy: coordinated deploy)
Edit THIS file, never the generated build script (it is overwritten on every run of this patch).

0.2.4 = THE VANILLA UI PASS for the /collections page (Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them
to look and feel vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md sections 7, 8c, 12, 13; research/Skyy-UI-Inventory.md
5.7). LOOK-ONLY RESTYLE on the shared kit tools/skyyui.py (1.4), recipe A of the guide (8c): the generated script calls the kit when
the BUILD runs (SUI.verify() first proves every vanilla value / texture / sound against Assets.zip, read-only), and the kit's Java is
filled into CollPage's method templates through /*=NAME=*/ tokens.
  KEPT (asserted below): every 0.2.3 element id, the 17 bind(ev, ...) calls (EventData "a": ccat<cat>, ccard<n>, crecipes, crefresh,
  cclose, cback, chome, cprev, cnext, cbuy) in their order, every EventData payload, the page (CollPage, CanDismiss), every data /
  text / b.set statement of the page methods word for word (the patch checks each 0.2.3 line against the new templates), the view
  logic (view / cat / pageNo / coll / status / cards[12]), handleDataEvent, closePage, openFor, the commands /collections + /coll +
  aliases, permissions, config keys, rewards / counts files, coll:fn:where and every bridge key, the bag ladder, the rewards data and
  its migration markers ("(0.2.3)" in rewards.properties stays - data), CollBypass (the coin path), every other class.
  CHANGED: only the CollPage look (bs / btn / lab / sp / bar / icon are gone; the kit builds the markup), the new CollPage.statusColor
  (the result line colour from 0.2.3's unchanged texts), the static CollPage.CATOPEN / CATBACK markups (the "Open <category>" /
  "< Back to <category>" buttons: a TextButton label cannot be b.set yet, so one static markup per category), VERSION, the kit
  import + UI_DATA_COLORS, the ready log line (kit id + page id) and this header. A few texts 0.2.3 wrote inline (after safe()) are
  b.set now (the card / detail names, the category names, the tier state words and roman numerals, "???", the hint, the error line,
  the Buy text); the text itself is the same (names without safe(): b.set never parses markup).
  Deploy rule (round 8) is unchanged: SkyySacks 0.7.7 + SkyyCollections 0.2.3 go together - 0.2.4 is look-only, so it pairs with
  SkyySacks 0.7.7 the same way (same recipe ids, coll:fn:where, bag ladder, rewards file).
The new page, the vanilla DECORATED window (like the vanilla collection page, Memories: 1070 x 825) 1120 x 826, fits 1080:
  - page_shell: the ContainerHeader title bar with runes, the two gold ornaments, COLLECTIONS in the 15 px Secondary title style, the
    ContainerPatch body (padding 17). New root #SkyyCollF (Anchor Width / Height only); 0.2.3's root #SkyyColl is the body. Gone:
    the dark-blue root, the purple accent stripe, the big custom titles, the solid colour buttons, the empty Label spacers.
    Why DECORATED although guide section 13 step 1 gives list pages the plain window: this page is a picker (Home), a list
    (Category) and a table (Detail) in one window, and its vanilla model is the collection page itself (Memories, 1070 x 825, a
    decorated container) - the picker / collection look wins; see the note at COLL_SHELL.
  - every view ends with the same bottom block: the result line #SkyyCStatus (kit result_line: 16 px bold, centred, two lines;
    statusColor: success green for "Bought the tier ...", the info blue for "Click Buy again ...", error red for every refusal),
    the content separator and a footer row of Secondary buttons (Close / Back with the vanilla cancel sound on the right / left, a
    fixed spacer between them - WorldEventPanelPage #Footer). Every view fills the body exactly (no FlexWeight; asserted at build time).
  - HOME: a well with the hint and #SkyyCSum (18 px bold), then 2 x 2 category cards (vanilla wells): the category icon in the
    vanilla slot border, the name in the category accent (a data colour), "n of m found", the tier bar (stat_bar: the vanilla progress
    track, the fill in the accent, no fill Group at 0), "Tiers a / b  Maxed c" and OPEN <CATEGORY> (Secondary); "Fishing - coming
    later" as a caption; footer UNLOCKED RECIPES, REFRESH ... CLOSE. The detail view sets the body height (754 px), so Home spends
    its spare height on air instead of one blank band (review fix2): taller summary well (padding 12), 20 px under it and under
    each card row, cards with 18 px top / bottom padding and 24 px between their three parts - a 24 px fill spacer is left.
  - CATEGORY: the title "<Category> Collections" (18 px bold, accent), then ONE vanilla list well of 12 collection rows in 2 columns
    x 6 lines (0.2.3: 3 x 4 cards; the same 12 per page, the same cards[] / ccard<n> numbering in reading order): a WorldEventListRow
    style row panel with the blue status bar, the 40 px item icon, the name (18 px bold), a progress bar (accent; success green when
    maxed), the tier / progress line and the "Next:" line, and a small Secondary OPEN button (#SkyyCCard<n>, bound ccard<n> - 0.2.3
    bound the name button with that id). Undiscovered = the row without bar colour or icon, "???" + "Gather one to discover it" in
    the grey caption colours, no button (0.2.3: no binding either). The kit pager (< PREV / Page n / m / NEXT >, the ends greyed in
    the vanilla Disabled look but still bound as in 0.2.3) when there is more than one page, else only the page caption; footer
    < BACK, HOME ... CLOSE.
  - COLLECTION: a well with the item in the slot border, the name (18 px bold, accent), the tier line, "Total collected" (bold white)
    and the curve line; the progress bar with its text; the tier table = vanilla section-label column heads (STATE / TIER / NEEDED /
    REWARDS) over a scrolling list on the vanilla list well (TopScrolling + the vanilla scrollbar: 10 rows show, a custom curve of
    up to 20 tiers scrolls - 0.2.3's fixed rows ran past the page bottom beyond about 12): one row panel per tier with the state word in the vanilla colours
    (DONE success green, BOUGHT the info blue, NEXT the confirm yellow, LOCKED the disabled grey), the roman tier, the threshold, the
    rewards (0.2.3's texts). "From:" as a caption; a well with the Primary BUY button (#SkyyCBuy, bound cbuy) next to 0.2.3's Buy
    text ("Buy tier III unlocks - 1500 coins", now a label in the kit's cost colour) over the unlock info - or 0.2.3's refusal line
    across the well; footer < BACK TO <CATEGORY>, HOME ... CLOSE (the row is 0.2.3's #SkyyCHead, which held those buttons before).
    Columns (review fix2): STATE 90 / TIER 56 / NEEDED 110 px (widest cell texts BOUGHT 70, XVIII 37, 999,999,999 94 px) leave the
    one-line rewards column 802 px (0.2.3: 740). The rewards text cannot wrap (one 32 px row) or be clipped (it is 0.2.3's text
    statement, word for word), so an admin-edited rewards.properties line wider than 802 px (about 90 characters at 16 px) runs
    past the row's right edge; the shipped registry's widest reachable text is 738 px (harness F measures it). The list scrolls
    for curves over 10 tiers, and every click rebuilds the page, which puts the scroll back at the top (0.2.3's fixed rows ran off
    the page there instead): after BUY the result line and the tier line say which tier is next.
  Two 0.2.3 ids keep their binding but hold another text (declared, checked per id by the harness): #SkyyCCard<n> was the
    collection-name button and is the small OPEN button now (the name is #SkyyCCd<n>Nm, not clickable: open a collection with
    OPEN), and #SkyyCBuy said "Buy tier III unlocks - 1500 coins" and says BUY now (that text is #SkyyCBuyLbl beside it).
  - UNLOCKED RECIPES: the heading, #SkyyCRSub, two vanilla wells of 20 lines (0.2.3's #SkyyCRCol0 / 1, #SkyyCRn<i>, #SkyyCRMore);
    footer < BACK ... CLOSE.  ERROR (counts or registry unreadable): 0.2.3's line in the vanilla error red, footer CLOSE.
  Only properties the deployed pages already use (LayoutMode Left / Top / TopScrolling, fixed sizes, Anchor margins, Padding, colour
  backgrounds, ItemIcon with an inline ItemId, Wrap) and the kit 1.4 blocks (probe page base4): no FlexWeight, WrapMaxLines,
  LetterSpacing, LayoutMode Center / Right / Full, nothing UNVERIFIED (SUI.assert_proven on every sample state at build time).
KIT-GAPs (composed here from kit calls; tools/skyyui.py unchanged): (1) static_row has no progress bar / third line, so the collection
row is composed from group + panel("row") + status_bar + item_icon + label + stat_bar; (2) column_row names its cells <id>C<i>, so the
tier row (0.2.3's #SkyyCThr<t> / #SkyyCRew<t>) is panel("row") + label() at the column_spec widths, nested with a local copy of the
kit's private _inside; (3) java_append takes a selector id, not a Java variable (catCard's / card()'s `parent`), so coll_java() emits
that one append itself (check_markup first); (4) no runtime pick among more than two markups (choose() takes two): CATOPEN / CATBACK
are static String[] fields indexed by the category; (5) SUI.assert_proven checks property names, not enum values: the column heads'
HorizontalAlignment: Start (the kit's "section" label kind) passes although no deployed page has used that value (probe base4 shows
it; UNVERIFIED below); (6) no kit footer block (fill spacer, result line, separator, footer row of left / right buttons): coll_bottom
re-derives it, as the Bank and Party pilots do; (7) no kit card for a well with icon frame, coloured name, found line, stat_bar and an
action row (the Home cards); (8) no fit-safe label for a runtime text column (the tier rewards: fit=False, width budget above);
(9) nothing outside this mod's harness enforces the checked page id - the build refuses an unchecked page only when the environment
sets SKYY_REQUIRE_CHECKED_PAGE=1 (for a deploy / SET-bump procedure; otherwise it warns, like the pilots).
UNVERIFIED (needs the game; the build docstring repeats it): the whole new look - probe pages base1 / base2 / base3 and base4
(stat_bar, list wells, the fixed rows and the column heads with HorizontalAlignment: Start), a TopScrolling list inside a kit window.
Harness (re-runnable, commit-ready): SkyyCollections/test_skyycollections_0.2.4.py - both jars side by side in one bare JVM.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.3.py")
dst = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.4.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.2.3"' in s and "tools/coll_0_2_3_patch.py" in s, "build_skyycollections_0.2.3.py is not the live 0.2.3"
assert "@@" not in s and "/*=" not in s, "0.2.3 already holds a token"
REG0 = s.count("registerCommand(")
BIND_LINES0 = [ln for ln in s.split(LF) if ln.lstrip().startswith("bind(ev, ")]
assert len(BIND_LINES0) == 17, "0.2.3 has 17 bind(ev, ...) calls in CollPage, found %d" % len(BIND_LINES0)
EVB0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
assert len(EVB0) == 1, "0.2.3 binds only through CollPage.bind(): %s" % EVB0


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


TOKEN_RE = re.compile(r"@@[A-Z0-9]+@@")


def fill(template, values):
    """@@NAME@@ replacement (research/Vanilla-UI-Style-Guide.md 8c): every token occurs exactly once, no value holds '@@', none left."""
    for name, value in values.items():
        tok = "@@%s@@" % name
        assert template.count(tok) == 1, "token %s occurs %d times" % (tok, template.count(tok))
        assert "@@" not in value, "the value for %s holds '@@'" % tok
        template = template.replace(tok, value)
    left = TOKEN_RE.findall(template)
    assert not left, "tokens left unfilled: %s" % left
    return template


READY_OLD = 'log("[SkyyCollections] 0.2.3 ready - item collections'
PAGE_A = 'M(page, r"""\npublic static String bs(int fs, String bg, String hv) {'
PAGE_B = 'M(page, r"""\npublic void closePage(@REF@ ref, @ST@ st) {'
# blocks that must come out of this patch byte-identical (everything but the header, VERSION, the kit import, the page look and
# the ready log line)
KEEP = [block("\nHERE = os.path.dirname(os.path.abspath(__file__))", "# ================= CollPage: one inline page"),
        block('F(page, "public int view;")', PAGE_A),
        block(PAGE_B, "  getLogger().at(java.util.logging.Level.INFO).log(\"[SkyyCollections] 0.2.3 ready"),
        s[s.index(READY_OLD) + len(READY_OLD):]]


# ================================================================================================ the page block (goes into the
# generated script at the old page's place; the kit calls in it run when the BUILD runs)
NEW_PAGE = r'''# ================= CollPage look (0.2.4): the vanilla UI kit tools/skyyui.py, called when THIS script runs =================
# research/Vanilla-UI-Style-Guide.md sections 7, 8c, 12 and 13. The coll_* functions build every markup from kit calls (every value
# proven by SUI.verify() at the top of this script); called with no arguments they hold J() runtime values (the Java locals of the
# page methods), called with concrete values they give one sample state (coll_views() below: check_page, assert_proven, the height
# budget). The Java the kit emits is filled into the page method templates through /*=NAME=*/ tokens (coll_fill: each token
# exactly once, none left over). Every data / text / binding statement of the templates is 0.2.3's, word for word
# (tools/coll_0_2_4_patch.py asserts it against the 0.2.3 methods); only the appends changed and a few texts moved to b.set.
# ---- COLL PAGE BLOCK START (SkyyCollections/test_skyycollections_0.2.4.py execs this block with SUI verified; needs UI_DATA_COLORS)
import hashlib
import os
COLL_PREFIX = "SkyyC"                  # every element id starts with it (the 0.2.3 ids already did)
COLL_W = 1120                          # the page root = the vanilla decorated window (0.2.3's root was 1120 x 840 without a frame)
COLL_IW = COLL_W - 2 * SUI.CONTENT_PAD  # 1086: the body's inner width (padding 17 = the container default)
COLL_BTN = SUI.BTN_MIN_W               # 172: a normal button (@DefaultButtonMinWidth)
COLL_GAP = 12                          # between the category cards / the recipe columns
COLL_ACCENT = tuple(UI_DATA_COLORS[:5])  # = CollReg.ACCENT (the category accents: data colours; the patch checks both lists)
COLL_CATS = ("Farming", "Mining", "Foraging", "Combat", "Fishing")          # = CollReg.CATS (checked by the patch)
COLL_PARENT = "=parent"                # the first append of catCard / card goes into their `parent` argument (a Java variable)


def coll_fill(tpl, values):
    """/*=NAME=*/ replacement: every value's token occurs exactly once in the template and no token is left over."""
    for name, value in values.items():
        tok = "/*=" + name + "=*/"
        assert tpl.count(tok) == 1, "token %s occurs %d times" % (tok, tpl.count(tok))
        assert "/*=" not in value, "the value for %s holds a token" % tok
        tpl = tpl.replace(tok, value)
    assert "/*=" not in tpl, "tokens left unfilled: " + tpl[tpl.index("/*="):tpl.index("/*=") + 40]
    return tpl


def coll_inside(outer, kids):
    """KIT-GAP: kit markup `outer` with the markups `kids` placed inside it (the kit's own _inside is private)."""
    assert outer.endswith("}"), outer[:60]
    return outer[:-1] + " ".join(kids) + " }"


def coll_java(ap, indent):
    """The Java statements of one part: every append (the kit's java_append; the "=parent" one into the method's `parent`
    variable, check_markup first), then its b.set lines (the kit's java_set) - indented for the method template."""
    lines = []
    for p, mk in ap:
        if p == COLL_PARENT:
            SUI.check_markup(mk)
            lines.append("b.appendInline(parent, %s);" % SUI.java_value(mk))
        else:
            lines.append(SUI.java_append(p, mk))
    lines += [SUI.java_set(i, pr, v) for i, pr, v in ap.sets]
    return "\n".join(" " * indent + ln for ln in lines)


def coll_btn_w(texts, minimum=COLL_BTN):
    """The width a normal button needs so every label in `texts` fits without ShrinkTextToFit (text_width = the client's own
    NunitoSans ExtraBold advances, 17 px uppercase): the widest label + 2 x 24 px padding + 4 px, rounded up to 4 px."""
    need = max(SUI.text_width(t, 17, bold=True, upper=True) for t in texts) + 2 * SUI.BTN_PAD + 4
    return max(minimum, int(need + 3) // 4 * 4)


def _J(v, expr, sample):
    return SUI.J(expr, sample) if v is None else v


# ---------------------------------------------------------------- the bottom block every view ends with
# the result line (0.2.3 #SkyyCStatus: CollBypass.click's texts, which carry no + / - / = mark -> statusColor() picks the vanilla
# colour from the words), the content separator (8 above / below, WorldEventPanelPage), then a footer row of Secondary buttons
COLL_STATUS = SUI.result_line("SkyyCStatus", SUI.J("statusColor(this.status)", SUI.COLOR["success"]), h=44, anchor={"top": 8})
COLL_SEP = SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN})
COLL_BOTTOM_H = (44 + 8) + (1 + 2 * SUI.SEP_MARGIN) + SUI.BTN_H           # 113
# "Bought the tier ..." = done (success green), "Click Buy again within 10 s ..." = a note (info blue), every other text
# CollBypass.click / offer returns = refused (error red); the patch asserts that list of texts
COLL_STATUS_SRC = SUI.java_color_by_text("statusColor", [("startsWith", "Bought the tier ", "+"),
                                                         ("startsWith", "Click Buy again ", "=")], empty="=", default="-")
COLL_RECIPES_W = coll_btn_w(["Unlocked recipes"])
COLL_OPEN_W = coll_btn_w(["Open " + c for c in COLL_CATS])
COLL_BACKTO_W = coll_btn_w(["< Back to " + c for c in COLL_CATS])


def coll_foot_btn(ident, text, w, sound=None, left=False):
    return SUI.button(ident, text, "secondary", w=w, sound=sound, anchor={"left": 6} if left else None)


COLL_CLOSE = coll_foot_btn("SkyyCClose", "Close", COLL_BTN, sound="cancel")
COLL_HOMEB = coll_foot_btn("SkyyCHome", "Home", COLL_BTN, left=True)
COLL_BACK = coll_foot_btn("SkyyCBack", "< Back", COLL_BTN, sound="cancel")
# "< Back to <category>" / "Open <category>" were runtime texts in 0.2.3 buttons; a TextButton label cannot be b.set yet (kit
# "button-text" is UNVERIFIED), so one static markup per category, picked by index in the Java: CollPage.CATBACK / CATOPEN
COLL_CATBACK = [coll_foot_btn("SkyyCBack", "< Back to " + c, COLL_BACKTO_W, sound="cancel") for c in COLL_CATS]
COLL_CATOPEN = [SUI.button("SkyyCCat" + str(i), "Open " + c, "secondary", w=COLL_OPEN_W, anchor={"left": 8})
                for i, c in enumerate(COLL_CATS)]


def coll_bottom(foot_id, left, right, used):
    """The spacer that fills the body (every view fills it exactly: no FlexWeight), the result line, the separator and the footer row
    #foot_id (LayoutMode Left): the `left` buttons, an empty Group as wide as what is left (WorldEventPanelPage #Footer's flex
    spacer as a fixed width), the `right` buttons. `left` may start with None = a button the Java appends itself (CATBACK)."""
    ap = SUI.Appends()
    if COLL_IH - used > 0:
        ap.add("SkyyColl", SUI.spacer(w=COLL_IW, h=COLL_IH - used))
    ap.add("SkyyColl", COLL_STATUS)
    ap.add("SkyyColl", COLL_SEP)
    ap.add("SkyyColl", SUI.group(foot_id, "Left", h=SUI.BTN_H))
    btn_w = sum(SUI.outer_size(m)[0] for m in left + right if m is not None) + (COLL_BACKTO_W if None in left else 0)
    gap = COLL_IW - btn_w
    assert gap >= 0, "footer %s: buttons %d px, %d px room" % (foot_id, btn_w, COLL_IW)
    for m in [m for m in left if m is not None] + [SUI.spacer(w=gap, h=SUI.BTN_H)] + right:
        ap.add(foot_id, m)
    return ap


# ---------------------------------------------------------------- HOME: summary well + 2 x 2 category cards
# the detail view sets the body height (COLL_IH); Home spends its spare height on air (the well padding, the gaps under the well and
# the card rows, the cards' own padding and inner gaps) rather than on one blank band above the result line (review fix2: 112 px)
COLL_HTOP_PADV = 12                                                        # the summary well's top / bottom padding
COLL_HTOP_H = 2 * COLL_HTOP_PADV + 26 + 30                                 # 80
COLL_HROW_GAP = 20                                                         # under the summary well and under each card row
COLL_CAT_W = (COLL_IW - COLL_GAP) // 2                                     # 537
COLL_CAT_PAD = 12                                                          # left / right (sets the bar width COLL_CAT_IN)
COLL_CAT_PADV = 18                                                         # top / bottom
COLL_CAT_VGAP = 24                                                         # between the icon row, the bar and the action row
COLL_CAT_IN = COLL_CAT_W - 2 * COLL_CAT_PAD                                # 513
COLL_CAT_FRAME = 84                                                        # the slot border (icon 80)
COLL_CAT_TXT = COLL_CAT_IN - COLL_CAT_FRAME - 16                           # 413
COLL_CAT_BAR = 14
COLL_CAT_H = 2 * COLL_CAT_PADV + COLL_CAT_FRAME + COLL_CAT_VGAP + COLL_CAT_BAR + COLL_CAT_VGAP + SUI.BTN_H   # 226
COLL_HINT = "Gather items yourself to raise collections. Every tier unlocks rewards."
COLL_HGAP = SUI.spacer(w=COLL_GAP, h=COLL_CAT_H)                           # between the two cards of a row (0.2.3: sp(40, 230))


def coll_home_top():
    """#SkyyCHTop: a vanilla well (WorldEventPanelPage #Summary) with 0.2.3's hint (b.set: it has dots) and #SkyyCSum."""
    ap = SUI.Appends()
    ap.add("SkyyColl", SUI.panel("SkyyCHTop", "well", h=COLL_HTOP_H, pad={"horizontal": 12, "vertical": COLL_HTOP_PADV},
                                 anchor={"bottom": COLL_HROW_GAP}))
    ap.text("SkyyCHTop", "SkyyCHint", COLL_HINT, "default", h=26, align="Center")
    ap.add("SkyyCHTop", SUI.label("SkyyCSum", "", "heading", h=30, align="Center", wrap=False))
    return ap


def coll_home_row(row=None):
    row = _J(row, "row", "0")
    return SUI.Appends([("SkyyColl", SUI.group("SkyyCHRow" + row, "Left", h=COLL_CAT_H, anchor={"bottom": COLL_HROW_GAP}))])


def coll_cat_card(cat=None, acc=None, fill=None):
    """One category card (catCard): the well #SkyyCCatBox<cat>, the top row #SkyyCCatTop<cat> (the category icon in the vanilla slot
    border #SkyyCCatIco<cat> - CollReg.CATICON - and the text column #SkyyCCatTxt<cat>: the name #SkyyCCatNm<cat> 18 px bold in
    the category accent, a data colour, and #SkyyCCatFound<cat>), the tier bar #SkyyCCatBar<cat> (stat_bar: the fill Group only
    when it is > 0, as 0.2.3's bar()) and the row #SkyyCCatAct<cat> with #SkyyCCatTiers<cat>; the OPEN button #SkyyCCat<cat> is
    appended into it by the Java (CATOPEN[cat])."""
    cat, acc, fill = _J(cat, "cat", "0"), _J(acc, "acc", COLL_ACCENT[0]), _J(fill, "fill", "300")
    box = "SkyyCCatBox" + cat
    ap = SUI.Appends()
    ap.add(COLL_PARENT, SUI.panel(box, "well", w=COLL_CAT_W, h=COLL_CAT_H, pad={"horizontal": COLL_CAT_PAD, "vertical": COLL_CAT_PADV}))
    ap.add(box, SUI.group("SkyyCCatTop" + cat, "Left", h=COLL_CAT_FRAME, anchor={"bottom": COLL_CAT_VGAP}))
    ap.add("SkyyCCatTop" + cat, SUI.item_frame("SkyyCCatIco" + cat, size=COLL_CAT_FRAME,
                                               item=SUI.J("@PKG@.CollReg.CATICON[cat]", "Plant_Crop_Wheat_Item")))
    ap.add("SkyyCCatTop" + cat, SUI.group("SkyyCCatTxt" + cat, "Top", w=COLL_CAT_TXT, h=COLL_CAT_FRAME, anchor={"left": 16},
                                          pad={"top": (COLL_CAT_FRAME - 28 - 26) // 2}))
    ap.add("SkyyCCatTxt" + cat, SUI.label("SkyyCCatNm" + cat, "", "heading", h=28, wrap=False, col=acc))
    ap.add("SkyyCCatTxt" + cat, SUI.label("SkyyCCatFound" + cat, "", "default", h=26))
    ap.add(box, SUI.stat_bar("SkyyCCatBar" + cat, COLL_CAT_IN, COLL_CAT_BAR, fill, col=acc, anchor={"bottom": COLL_CAT_VGAP}).choose("fill > 0"))
    ap.add(box, SUI.group("SkyyCCatAct" + cat, "Left", h=SUI.BTN_H))
    ap.add("SkyyCCatAct" + cat, SUI.label("SkyyCCatTiers" + cat, "", "default", w=COLL_CAT_IN - COLL_OPEN_W - 8, h=SUI.BTN_H))
    return ap


def coll_home_bottom():
    ap = SUI.Appends([("SkyyColl", SUI.label(None, "Fishing - coming later", "caption", h=25, align="Center"))])
    ap += coll_bottom("SkyyCFoot", [coll_foot_btn("SkyyCRecipes", "Unlocked recipes", COLL_RECIPES_W),
                                    coll_foot_btn("SkyyCRefresh", "Refresh", COLL_BTN, left=True)], [COLL_CLOSE], COLL_HOME_USED)
    return ap


# ---------------------------------------------------------------- CATEGORY: head + list well of 6 x 2 collection rows + pager
COLL_GRID_ROWS, COLL_GRID_COLS = 6, 2                                      # 12 per page (0.2.3's cards[12] / pageNo arrays)
COLL_RH = 88                                                               # a collection row: name, bar, progress, next reward
COLL_GRID_IN = COLL_IW - 2 * SUI.WELL_LIST_PAD                             # 1078
COLL_CD_GAP = 8
COLL_CD_W = (COLL_GRID_IN - COLL_CD_GAP) // 2                              # 535
COLL_CD_ACT = SUI.ROW_ACTION_W                                             # 92: the small row action (WorldEventListRow)
COLL_CD_PANEL = COLL_CD_W - 4 - COLL_CD_ACT                                # 439
COLL_CD_ICONBOX, COLL_CD_ICON = 52, 40                                     # the 40 px item icon in a 52 px box (static_row)
COLL_CD_TEXT = COLL_CD_PANEL - 2 * 8 - (4 + 8) - COLL_CD_ICONBOX           # 359
COLL_CD_BAR = 10
COLL_CD_TOP = (COLL_RH - (24 + (3 + COLL_CD_BAR + 5) + 20 + 20)) // 2       # 3
COLL_GRID_H = SUI.list_well_h(COLL_GRID_ROWS, COLL_RH)                     # 554
COLL_CGAP = SUI.spacer(w=COLL_CD_GAP, h=COLL_RH)                           # between the two rows of a line (0.2.3: sp(10, 170))
COLL_PG_BTN, COLL_PG_CAP, COLL_PG_GAP = 150, 260, 12                       # the kit pager's defaults
COLL_PG_CAP_X = SUI.centre_margin(COLL_IW, 2 * COLL_PG_BTN + 2 * COLL_PG_GAP + COLL_PG_CAP) + COLL_PG_BTN + COLL_PG_GAP


def coll_cat_head(acc=None):
    """#SkyyCHead: the category title #SkyyCCatTitle (18 px bold, the category accent) over the list well #SkyyCGrid."""
    acc = _J(acc, "acc", COLL_ACCENT[0])
    ap = SUI.Appends()
    ap.add("SkyyColl", SUI.group("SkyyCHead", "Left", h=30, anchor={"bottom": 8}))
    ap.add("SkyyCHead", SUI.label("SkyyCCatTitle", "", "heading", w=COLL_IW, h=30, wrap=False, col=acc))
    ap.add("SkyyColl", SUI.list_well("SkyyCGrid", w=COLL_IW, h=COLL_GRID_H))
    return ap


def coll_cat_grow(row=None):
    row = _J(row, "row", "0")
    return SUI.Appends([("SkyyCGrid", SUI.group("SkyyCGRow" + row, "Left", h=COLL_RH, anchor={"bottom": SUI.ROW_GAP}))])


def coll_cd_top(n=None, bar=True):
    """The row #SkyyCCd<n> (LayoutMode Left, fixed width) with the row panel #SkyyCCd<n>P (the list row colour, padding 8), the status bar
    (blue; bar=False keeps its 12 px) and the icon box #SkyyCCdTop<n> (an empty 52 px Group for an undiscovered one)."""
    n = _J(n, "n", "0")
    ap = SUI.Appends()
    ap.add(COLL_PARENT, SUI.group("SkyyCCd" + n, "Left", w=COLL_CD_W, h=COLL_RH))
    ap.add("SkyyCCd" + n, SUI.panel("SkyyCCd" + n + "P", "row", w=COLL_CD_PANEL, h=COLL_RH, layout="Left", pad={"left": 8, "right": 8}))
    ap.add("SkyyCCd" + n + "P", SUI.status_bar(None, bar))
    if bar:
        ap.add("SkyyCCd" + n + "P", SUI.group("SkyyCCdTop" + n, None, w=COLL_CD_ICONBOX, h=COLL_RH))
    else:
        ap.add("SkyyCCd" + n + "P", SUI.spacer(w=COLL_CD_ICONBOX, h=COLL_RH))
    return ap


def coll_cd_icon(n=None, item=None):
    """The collection's 40 px icon in #SkyyCCdTop<n> (0.2.3: only when R.iconOk[c])."""
    n, item = _J(n, "n", "0"), _J(item, "R.icon[c]", "Ore_Copper")
    return SUI.Appends([("SkyyCCdTop" + n, SUI.item_icon(None, item, COLL_CD_ICON,
                                                         anchor={"left": 0, "top": (COLL_RH - COLL_CD_ICON) // 2}))])


def coll_cd_text(n=None, fill=None, fc=None):
    """The text column #SkyyCCd<n>T (name #SkyyCCd<n>Nm 18 px bold, the progress bar #SkyyCCdBar<n>, #SkyyCCdProg<n>, #SkyyCCdNext<n>)
    and the action column with the small Secondary OPEN button #SkyyCCard<n> (0.2.3's card button, bound ccard<n> as before; it
    held the collection name in 0.2.3 and says OPEN now - the name is #SkyyCCd<n>Nm: a declared id-text move)."""
    n, fill, fc = _J(n, "n", "0"), _J(fill, "fill", "150"), _J(fc, "fc", COLL_ACCENT[0])
    t = "SkyyCCd" + n + "T"
    ap = SUI.Appends()
    ap.add("SkyyCCd" + n + "P", SUI.group(t, "Top", w=COLL_CD_TEXT, h=COLL_RH, pad={"top": COLL_CD_TOP}))
    ap.add(t, SUI.label("SkyyCCd" + n + "Nm", "", "rowName", h=24))
    ap.add(t, SUI.stat_bar("SkyyCCdBar" + n, COLL_CD_TEXT, COLL_CD_BAR, fill, col=fc, anchor={"top": 3, "bottom": 5}).choose("fill > 0"))
    ap.add(t, SUI.label("SkyyCCdProg" + n, "", "rowSub", h=20, col="value"))
    ap.add(t, SUI.label("SkyyCCdNext" + n, "", "rowSub", h=20))
    ap.add("SkyyCCd" + n, SUI.group("SkyyCCd" + n + "A", "Top", w=COLL_CD_ACT, h=COLL_RH, anchor={"left": 4},
                                    pad={"top": (COLL_RH - SUI.BTN_SMALL_H) // 2}))
    ap.add("SkyyCCd" + n + "A", SUI.button("SkyyCCard" + n, "Open", "secondary", "small", w=COLL_CD_ACT))
    return ap


def coll_cd_undisc(n=None):
    """An undiscovered collection (0.2.3: "???" + "Gather one to discover it", not clickable): the row with the status bar's space
    kept and an empty icon box, the two lines in the grey caption colours."""
    n = _J(n, "n", "0")
    ap = coll_cd_top(n, bar=False)
    t = "SkyyCCd" + n + "T"
    ap.add("SkyyCCd" + n + "P", SUI.group(t, "Top", w=COLL_CD_TEXT, h=COLL_RH, pad={"top": (COLL_RH - 24 - 20) // 2}))
    ap.text(t, "SkyyCCd" + n + "Q", "???", "rowName", h=24, col="caption")             # b.set: "?" is no inline text
    ap.add(t, SUI.label(None, "Gather one to discover it", "rowSub", h=20))
    return ap


def coll_cat_pager():
    """pages > 1: the kit pager - Prev / Page n / m / Next (Prev greyed on the first page, Next on the last: the vanilla Disabled look,
    still bound as in 0.2.3, whose clicks there did nothing) with 0.2.3's ids #SkyyCPrev / #SkyyCPage / #SkyyCNext."""
    return SUI.pager("SkyyColl", "SkyyCPager", COLL_IW, prev_on=SUI.J("this.pageNo > 0"), next_on=SUI.J("this.pageNo < pages - 1"),
                     btn_w=COLL_PG_BTN, caption_w=COLL_PG_CAP, gap=COLL_PG_GAP,
                     ids={"row": "SkyyCPager", "prev": "SkyyCPrev", "page": "SkyyCPage", "next": "SkyyCNext"})


def coll_cat_page1():
    """pages == 1: the same row with only the caption #SkyyCPage where the pager puts it (0.2.3 had no Prev / Next then)."""
    ap = SUI.Appends()
    ap.add("SkyyColl", SUI.group("SkyyCPager", "Left", h=SUI.BTN_SMALL_H, anchor={"top": 8}))
    ap.add("SkyyCPager", SUI.label("SkyyCPage", "", "default", w=COLL_PG_CAP, h=SUI.BTN_SMALL_H, align="Center",
                                   anchor={"left": COLL_PG_CAP_X}))
    return ap


def coll_cat_bottom():
    return coll_bottom("SkyyCFoot", [COLL_BACK, COLL_HOMEB], [COLL_CLOSE], COLL_CAT_USED)


# ---------------------------------------------------------------- COLLECTION (detail): summary well, bar, tier table, buy well
COLL_DTOP_IN = 68                                                          # the slot border (icon 64)
COLL_DTOP_H = COLL_DTOP_IN + 2 * SUI.WELL_PAD                              # 84
COLL_D_TXT_W = 600
COLL_D_TXT2_W = COLL_IW - 2 * SUI.WELL_PAD - COLL_DTOP_IN - 12 - COLL_D_TXT_W - 12   # 378
COLL_DBAR_W = 700
COLL_TR_H = 32                                                             # one tier row: one 16 px line
COLL_TR_SHOW = 10                                                          # rows visible without scrolling (Bulk = 10 tiers)
COLL_TLIST_H = SUI.list_well_h(COLL_TR_SHOW, COLL_TR_H)                    # 358
# the three short columns as narrow as their widest cell + about 16 px (review fix2: more room for the one-line rewards text):
# STATE "BOUGHT" 70 px bold, TIER "XVIII" 37 px bold (a custom curve has up to 20 tiers), NEEDED "999,999,999" 94 px; the heads
# (16 px bold uppercase) are narrower still - asserted below with the client's font tables when they are there
COLL_TR_COLS = [("State", 90), ("Tier", 56), ("Needed", 110)]
COLL_TR_REW = COLL_GRID_IN - 8 - sum(w for _t, w in COLL_TR_COLS) - (SUI.SCROLL_SIZE + SUI.SCROLL_SPACING)   # 802: scrollbar room
if os.path.isdir(SUI.FONT_DIR):
    for (_head, _cw), _cells, _bold in zip(COLL_TR_COLS, (["DONE", "BOUGHT", "NEXT", "LOCKED"], ["XVIII"], ["999,999,999"]),
                                           (True, True, False)):
        _tw = max([SUI.text_width(x, 16, bold=_bold) for x in _cells] + [SUI.text_width(_head, SUI.fs(13), bold=True, upper=True)])
        assert _tw + 12 <= _cw, "tier column %s (%d px): its widest text is %.0f px" % (_head, _cw, _tw)
COLL_TR_SPEC = SUI.column_spec(COLL_TR_COLS + [("Rewards", COLL_TR_REW)], avail=COLL_GRID_IN, pad_left=8)
COLL_BUY_IN = 26 + 46                                                      # the cost line + two wrapped 16 px lines (43.7 px)
COLL_BUY_H = COLL_BUY_IN + 2 * SUI.WELL_PAD                                # 88
COLL_BUY_TXT_W = COLL_IW - 2 * SUI.WELL_PAD - COLL_BTN - 16                # 882
# the tier row look by state (0.2.3's coloured chips): DONE the vanilla success green, BOUGHT the info blue, NEXT the confirm
# yellow, LOCKED the disabled grey; the reward text bright for DONE / BOUGHT / NEXT, the plain label colour for LOCKED
COLL_TIER_LOOK = (("LOCKED", "disabled", "text"), ("DONE", "success", "rowName"), ("BOUGHT", "info", "rowName"),
                  ("NEXT", "warning", "rowName"))


def coll_det_top(acc=None, icon=True):
    """#SkyyCDTop: a well (Left): the icon in the slot border #SkyyCDIcon (empty when the id is no game item: 0.2.3 drew none),
    #SkyyCDTxt (#SkyyCDName 18 px bold in the category accent, #SkyyCDTier) and #SkyyCDTxt2 (#SkyyCDTotal, #SkyyCDCurve); then
    #SkyyCDBarRow: the progress bar #SkyyCDBar and #SkyyCDProg."""
    acc = _J(acc, "acc", COLL_ACCENT[0])
    ap = SUI.Appends()
    ap.add("SkyyColl", SUI.panel("SkyyCDTop", "well", h=COLL_DTOP_H, layout="Left", anchor={"bottom": 8}))
    full = SUI.item_frame("SkyyCDIcon", size=COLL_DTOP_IN, item=SUI.J("R.icon[c]", "Ore_Copper"))
    empty = SUI.item_frame("SkyyCDIcon", size=COLL_DTOP_IN)
    ap.add("SkyyCDTop", SUI.choose(SUI.J("R.iconOk[c]"), full, empty) if icon is None else (full if icon else empty))
    pt = {"top": (COLL_DTOP_IN - 28 - 26) // 2}
    ap.add("SkyyCDTop", SUI.group("SkyyCDTxt", "Top", w=COLL_D_TXT_W, h=COLL_DTOP_IN, anchor={"left": 12}, pad=pt))
    ap.add("SkyyCDTxt", SUI.label("SkyyCDName", "", "heading", h=28, wrap=False, col=acc))
    ap.add("SkyyCDTxt", SUI.label("SkyyCDTier", "", "default", h=26))
    ap.add("SkyyCDTop", SUI.group("SkyyCDTxt2", "Top", w=COLL_D_TXT2_W, h=COLL_DTOP_IN, anchor={"left": 12}, pad=pt))
    ap.add("SkyyCDTxt2", SUI.label("SkyyCDTotal", "", "strong", h=28))
    ap.add("SkyyCDTxt2", SUI.label("SkyyCDCurve", "", "caption", h=26))
    return ap


def coll_det_bar(fill=None, fc=None):
    fill, fc = _J(fill, "fill", "350"), _J(fc, "fc", COLL_ACCENT[0])
    ap = SUI.Appends()
    ap.add("SkyyColl", SUI.group("SkyyCDBarRow", "Left", h=26, anchor={"bottom": 8}))
    ap.add("SkyyCDBarRow", SUI.stat_bar("SkyyCDBar", COLL_DBAR_W, 12, fill, col=fc, anchor={"top": 7}).choose("fill > 0"))
    ap.add("SkyyCDBarRow", SUI.label("SkyyCDProg", "", "default", w=COLL_IW - COLL_DBAR_W - 16, h=26, anchor={"left": 16}))
    return ap


def coll_det_table():
    """The tier table: the column heads #SkyyCTHead (vanilla section labels over the cells) and the scrolling list #SkyyCTiers on the
    vanilla list well (TopScrolling + the vanilla scrollbar: a custom curve may have up to 20 tiers; 10 rows show at once). Every
    click rebuilds the page, so the scroll position goes back to the top (0.2.3's fixed rows ran off the page there instead).
    The heads are the kit's "section" labels: HorizontalAlignment: Start, a value no deployed page has used yet (probe base4
    shows it; UNVERIFIED in the build docstring)."""
    ap = SUI.Appends()
    ap.add("SkyyColl", COLL_TR_SPEC.heads("SkyyCTHead", outside=SUI.WELL_LIST_PAD))
    ap.add("SkyyColl", SUI.scroll_list("SkyyCTiers", h=COLL_TLIST_H, well=True))
    return ap


def coll_det_tier(t=None, col=None, tc=None):
    """One tier row #SkyyCTr<t> (the list row panel, one line) with the state #SkyyCTr<t>S, the tier #SkyyCTr<t>T, the
    threshold #SkyyCThr<t> and the rewards #SkyyCRew<t> (0.2.3's ids), at the column heads' widths. KIT-GAP: column_row names its
    cells <id>C<i>, so 0.2.3's #SkyyCThr<t> / #SkyyCRew<t> need this composition of panel() + label()."""
    t, col, tc = _J(t, "t", "1"), _J(col, "col", SUI.COLOR["success"]), _J(tc, "tc", SUI.COLOR["rowName"])
    w = COLL_TR_SPEC.widths
    # the rewards cell: one line, COLL_TR_REW (802) px, runtime text (fit=False: the build cannot measure it). It cannot wrap (one
    # 32 px row) or be clipped (0.2.3's text statement, word for word): the shipped registry's widest reachable text is 738 px
    # (harness F); an admin-edited rewards.properties line wider than 802 px runs past the row's right edge (KIT-GAP 8)
    cells = [SUI.label("SkyyCTr" + t + "S", "", "bold", w=w[0], h=COLL_TR_H, col=col),
             SUI.label("SkyyCTr" + t + "T", "", "bold", w=w[1], h=COLL_TR_H, col="rowName"),
             SUI.label("SkyyCThr" + t, "", "default", w=w[2], h=COLL_TR_H, col="value"),
             SUI.label("SkyyCRew" + t, "", "default", w=w[3], h=COLL_TR_H, col=tc, fit=False)]
    row = SUI.panel("SkyyCTr" + t, "row", h=COLL_TR_H, layout="Left", pad={"left": COLL_TR_SPEC.pad_left}, anchor={"bottom": SUI.ROW_GAP})
    return SUI.Appends([("SkyyCTiers", coll_inside(row, cells))])


def coll_det_buyrow():
    ap = SUI.Appends()
    ap.add("SkyyColl", SUI.label("SkyyCFrom", "", "caption", h=25, anchor={"top": 6}))
    ap.add("SkyyColl", SUI.panel("SkyyCBuyRow", "well", h=COLL_BUY_H, layout="Left", anchor={"top": 8}))
    return ap


def coll_det_buyok():
    """A tier coins can unlock: the Primary BUY button #SkyyCBuy (bound cbuy as in 0.2.3) next to the cost line #SkyyCBuyLbl (0.2.3's
    button text "Buy tier III unlocks - 1500 coins", now b.set, in the kit's cost colour) over #SkyyCBuyInfo (wraps to 2 lines).
    #SkyyCBuy held that text in 0.2.3 and says BUY now: a declared id-text move."""
    ap = SUI.Appends()
    ap.add("SkyyCBuyRow", SUI.button("SkyyCBuy", "Buy", "primary", w=COLL_BTN, anchor={"top": (COLL_BUY_IN - SUI.BTN_H) // 2}))
    ap.add("SkyyCBuyRow", SUI.group("SkyyCBuyTxt", "Top", w=COLL_BUY_TXT_W, h=COLL_BUY_IN, anchor={"left": 16}))
    ap.add("SkyyCBuyTxt", SUI.label("SkyyCBuyLbl", "", "bold", h=26, col="gold"))
    ap.add("SkyyCBuyTxt", SUI.label("SkyyCBuyInfo", "", "default", h=46, wrap=True))
    return ap


def coll_det_buyno():
    """Nothing to buy: 0.2.3's refusal text in #SkyyCBuyInfo across the well."""
    return SUI.Appends([("SkyyCBuyRow", SUI.label("SkyyCBuyInfo", "", "default", w=COLL_IW - 2 * SUI.WELL_PAD, h=COLL_BUY_IN,
                                                 align="Center", wrap=True))])


def coll_det_bottom():
    """The footer row is 0.2.3's #SkyyCHead (it held Back / Home / Close then as well): < BACK TO <CATEGORY> (the Java appends
    CATBACK[cat] first), HOME, the spacer, CLOSE."""
    return coll_bottom("SkyyCHead", [None, COLL_HOMEB], [COLL_CLOSE], COLL_DET_USED)


# ---------------------------------------------------------------- UNLOCKED RECIPES: heading + two list columns
COLL_RC_LINES = 20
COLL_RC_LINE = 26
COLL_RC_W = (COLL_IW - COLL_GAP) // 2                                      # 537
COLL_RC_H = 2 * SUI.WELL_PAD + COLL_RC_LINES * COLL_RC_LINE                # 536


def coll_rc_head():
    """The heading, #SkyyCRSub and #SkyyCRCols: two vanilla wells #SkyyCRCol0 / #SkyyCRCol1 of 20 lines each."""
    ap = SUI.Appends()
    ap.add("SkyyColl", SUI.label(None, "Unlocked recipes", "heading", h=28, wrap=False))
    ap.add("SkyyColl", SUI.label("SkyyCRSub", "", "default", h=26, anchor={"bottom": 8}))
    ap.add("SkyyColl", SUI.group("SkyyCRCols", "Left", h=COLL_RC_H))
    ap.add("SkyyCRCols", SUI.panel("SkyyCRCol0", "well", w=COLL_RC_W, h=COLL_RC_H))
    ap.add("SkyyCRCols", SUI.panel("SkyyCRCol1", "well", w=COLL_RC_W, h=COLL_RC_H, anchor={"left": COLL_GAP}))
    return ap


def coll_rc_line(i=None, col=None):
    i, col = _J(i, "i", "0"), _J(col, "i / 20", "0")
    return SUI.Appends([("SkyyCRCol" + col, SUI.label("SkyyCRn" + i, "", "default", h=COLL_RC_LINE, col="rowName"))])


def coll_rc_more():
    return SUI.Appends([("SkyyCRCol1", SUI.label("SkyyCRMore", "", "bold", h=COLL_RC_LINE, col="info"))])


def coll_rc_bottom():
    return coll_bottom("SkyyCFoot", [COLL_BACK], [COLL_CLOSE], COLL_RC_USED)


# ---------------------------------------------------------------- ERROR (the counts file or the registry cannot be read)
COLL_ERR = "Your collections could not be read right now - try again in a moment."


def coll_err():
    ap = SUI.Appends()
    ap.text("SkyyColl", "SkyyCErr", COLL_ERR, "error", h=52, align="Center", wrap=True, anchor={"top": 40})
    used = (40 + 52) + (1 + 2 * SUI.SEP_MARGIN) + SUI.BTN_H
    if COLL_IH - used > 0:
        ap.add("SkyyColl", SUI.spacer(w=COLL_IW, h=COLL_IH - used))
    ap.add("SkyyColl", COLL_SEP)
    ap.add("SkyyColl", SUI.group("SkyyCFoot", "Left", h=SUI.BTN_H))
    ap.add("SkyyCFoot", SUI.spacer(w=COLL_IW - COLL_BTN, h=SUI.BTN_H))
    ap.add("SkyyCFoot", COLL_CLOSE)
    return ap


# ---------------------------------------------------------------- the height budget: every view fills the body exactly
COLL_DET_USED = (COLL_DTOP_H + 8) + (26 + 8) + 30 + COLL_TLIST_H + (25 + 6) + (COLL_BUY_H + 8) + COLL_BOTTOM_H
COLL_IH = COLL_DET_USED                                                    # the tallest view sets the page height
COLL_H = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + COLL_IH
COLL_HOME_USED = (COLL_HTOP_H + COLL_HROW_GAP) + 2 * (COLL_CAT_H + COLL_HROW_GAP) + 25 + COLL_BOTTOM_H
COLL_CAT_USED = (30 + 8) + COLL_GRID_H + (SUI.BTN_SMALL_H + 8) + COLL_BOTTOM_H
COLL_RC_USED = 28 + (26 + 8) + COLL_RC_H + COLL_BOTTOM_H
SUI.assert_page_size(COLL_W, COLL_H)
assert COLL_GRID_ROWS * COLL_GRID_COLS == 12, "0.2.3's cards[12]: 12 per page"
assert max(COLL_HOME_USED, COLL_CAT_USED, COLL_RC_USED) <= COLL_IH, (COLL_HOME_USED, COLL_CAT_USED, COLL_RC_USED, COLL_IH)
assert COLL_IH - COLL_HOME_USED <= 48, "Home would show a %d px blank band above its result line" % (COLL_IH - COLL_HOME_USED)
# The DECORATED window (title bar with runes + gold ornaments), not the plain one guide section 13 step 1 gives list pages: this page
# is a picker (Home), a list (Category) and a table (Detail) in one window, and its vanilla model is the collection page itself
# (Memories, 1070 x 825, a decorated container), so the picker / collection look wins over the list recipe (reviewed: keep it).
COLL_SHELL = SUI.page_shell("SkyyCollF", COLL_W, COLL_H, "Collections", body_id="SkyyColl")   # 0.2.3's root #SkyyColl = the body
assert COLL_SHELL.inner_w == COLL_IW and COLL_SHELL.inner_h == COLL_IH


# ---------------------------------------------------------------- the page methods (templates; the statements are 0.2.3's)
COLL_CATCARD_TPL = r"""
public void catCard(@UCB@ b, @UEB@ ev, String parent, int cat, @PKG@.CollData d, @PKG@.RegData R) {
  int found = 0; int total = 0; int maxed = 0; long td = 0L; long tt = 0L;
  for (int c = 0; c < R.n; c++) {
    if (R.cat[c] != cat || R.hidden[c]) continue;
    total++;
    long sm = @PKG@.CollStore.sum(d, R, c);
    if (sm > 0L) found++;
    int ct = @PKG@.CollReg.tierOf(R, c, sm);
    int mx = @PKG@.CollReg.maxTier(R, c);
    td += ct; tt += mx;
    if (ct >= mx) maxed++;
  }
  String box = "SkyyCCatBox" + cat;
  String acc = @PKG@.CollReg.ACCENT[cat];
  int fill = tt > 0L ? (int) (/*=BARW=*/L * td / tt) : 0;
/*=CARD=*/
  b.appendInline("#SkyyCCatAct" + cat, CATOPEN[cat]);
  b.set("#SkyyCCatNm" + cat + ".Text", @PKG@.CollReg.CATS[cat]);
  b.set("#SkyyCCatFound" + cat + ".Text", found + " of " + total + " found");
  b.set("#SkyyCCatTiers" + cat + ".Text", "Tiers " + td + " / " + tt + "     Maxed " + maxed);
  bind(ev, "SkyyCCat" + cat, "ccat" + cat);
}"""
COLL_HOME_TPL = r"""
public void buildHome(@UCB@ b, @UEB@ ev, @PKG@.CollData d, @PKG@.RegData R) {
  long[] s = @PKG@.CollStore.stats(d, R);
  int rec = @PKG@.CollUnlocks.compute(d).size();
/*=TOP=*/
  b.set("#SkyyCSum.Text", "Tiers " + s[0] + " / " + s[4] + "      Maxed " + s[2] + "      Recipes unlocked " + rec + "      Score " + s[0]);
  for (int row = 0; row < 2; row++) {
/*=ROW=*/
    catCard(b, ev, "#SkyyCHRow" + row, row * 2, d, R);
/*=GAP=*/
    catCard(b, ev, "#SkyyCHRow" + row, row * 2 + 1, d, R);
  }
/*=BOTTOM=*/
  bind(ev, "SkyyCRecipes", "crecipes");
  bind(ev, "SkyyCRefresh", "crefresh");
  bind(ev, "SkyyCClose", "cclose");
}"""
COLL_CARD_TPL = r"""
public void card(@UCB@ b, @UEB@ ev, String parent, int n, int c, @PKG@.CollData d, @PKG@.RegData R) {
  long sm = @PKG@.CollStore.sum(d, R, c);
  String box = "SkyyCCd" + n;
  if (sm <= 0L) {
/*=UNDISC=*/
    return;
  }
  this.cards[n] = c;
  int ct = @PKG@.CollReg.tierOf(R, c, sm);
  int mx = @PKG@.CollReg.maxTier(R, c);
  long next = ct < mx ? @PKG@.CollReg.threshold(R, c, ct + 1) : 0L;
  int fill = ct >= mx ? /*=BARW1=*/ : (int) (/*=BARW2=*/L * sm / (next < 1L ? 1L : next));
  if (fill < 0) fill = 0;
  if (fill > /*=BARW3=*/) fill = /*=BARW4=*/;
  String fc = ct >= mx ? "/*=MAXCOL=*/" : @PKG@.CollReg.ACCENT[R.cat[c]];
/*=TOP=*/
  if (R.iconOk[c]) /*=ICON=*/
/*=TEXT=*/
  b.set("#SkyyCCd" + n + "Nm.Text", R.name[c]);
  bind(ev, "SkyyCCard" + n, "ccard" + n);
  b.set("#SkyyCCdProg" + n + ".Text", @PKG@.CollUtil.tierName(ct) + "    " + (ct >= mx ? "MAXED" : @PKG@.CollUtil.fmt(sm) + " / " + @PKG@.CollUtil.fmt(next)));
  java.util.ArrayList nx = ct >= mx ? null : @PKG@.CollReg.rewardLines(R, c, ct + 1);
  String[] nr = ct >= mx ? new String[0] : @PKG@.CollReg.recipesAt(c, ct + 1);
  String n1 = nr.length > 0 ? @PKG@.CollUtil.prettyRecipe(nr[0]) + " recipe" : (nx == null || nx.isEmpty() ? "" : (String) nx.get(0));
  b.set("#SkyyCCdNext" + n + ".Text", nx == null ? "All tiers done" : (nx.isEmpty() ? "Next: tier " + @PKG@.CollUtil.roman(ct + 1) : "Next: " + @PKG@.CollUtil.clip(n1, 32)));
}"""
COLL_CAT_TPL = r"""
public void buildCat(@UCB@ b, @UEB@ ev, @PKG@.CollData d, @PKG@.RegData R) {
  java.util.ArrayList list = new java.util.ArrayList();
  java.util.ArrayList un = new java.util.ArrayList();
  for (int c = 0; c < R.n; c++) {
    if (R.cat[c] != this.cat || R.hidden[c]) continue;
    if (@PKG@.CollStore.sum(d, R, c) > 0L) list.add(Integer.valueOf(c)); else un.add(Integer.valueOf(c));
  }
  list.addAll(un);
  int pages = (list.size() + 11) / 12;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  for (int i = 0; i < 12; i++) this.cards[i] = -1;
  String acc = @PKG@.CollReg.ACCENT[this.cat];
/*=HEAD=*/
  b.set("#SkyyCCatTitle.Text", @PKG@.CollReg.CATS[this.cat] + " Collections");
  bind(ev, "SkyyCBack", "cback");
  for (int row = 0; row < /*=ROWS=*/; row++) {
/*=ROW=*/
    for (int col = 0; col < /*=COLS1=*/; col++) {
      int n = row * /*=COLS2=*/ + col;
      int k = this.pageNo * 12 + n;
      if (k >= list.size()) break;
      if (col > 0) /*=GAP=*/
      card(b, ev, "#SkyyCGRow" + row, n, ((Integer) list.get(k)).intValue(), d, R);
    }
  }
  if (pages > 1) {
/*=PAGER=*/
    bind(ev, "SkyyCPrev", "cprev");
    bind(ev, "SkyyCNext", "cnext");
  } else {
/*=PAGE1=*/
  }
  b.set("#SkyyCPage.Text", "Page " + (this.pageNo + 1) + " / " + pages);
/*=BOTTOM=*/
  bind(ev, "SkyyCHome", "chome");
  bind(ev, "SkyyCClose", "cclose");
}"""
COLL_DET_TPL = r"""
public void buildDetail(@UCB@ b, @UEB@ ev, @PKG@.CollData d, @PKG@.RegData R) {
  int c = this.coll;
  this.cat = R.cat[c];
  long sm = @PKG@.CollStore.sum(d, R, c);
  int ct = @PKG@.CollReg.tierOf(R, c, sm);
  int bt = @PKG@.CollStore.boughtTier(d, R, c);
  int mx = @PKG@.CollReg.maxTier(R, c);
  int eff = ct > bt ? ct : bt;
  long next = ct < mx ? @PKG@.CollReg.threshold(R, c, ct + 1) : 0L;
  String acc = @PKG@.CollReg.ACCENT[R.cat[c]];
  int fill = ct >= mx ? /*=BARW1=*/ : (int) (/*=BARW2=*/L * sm / (next < 1L ? 1L : next));
  if (fill < 0) fill = 0;
  if (fill > /*=BARW3=*/) fill = /*=BARW4=*/;
  String fc = ct >= mx ? "/*=MAXCOL=*/" : acc;
  bind(ev, "SkyyCBack", "cback");
  bind(ev, "SkyyCHome", "chome");
  bind(ev, "SkyyCClose", "cclose");
/*=TOP=*/
  b.set("#SkyyCDName.Text", R.name[c]);
  b.set("#SkyyCDTier.Text", (ct <= 0 ? "No tier yet" : "Tier " + @PKG@.CollUtil.roman(ct) + " of " + @PKG@.CollUtil.roman(mx)) + (bt > ct ? "   (recipes bought up to tier " + @PKG@.CollUtil.roman(bt) + ")" : ""));
  b.set("#SkyyCDTotal.Text", "Total collected: " + @PKG@.CollUtil.fmt(sm));
  b.set("#SkyyCDCurve.Text", @PKG@.CollReg.CATS[R.cat[c]] + " - " + @PKG@.CollReg.CURVENAMES[R.curve[c]] + " collection");
/*=BAR=*/
  b.set("#SkyyCDProg.Text", ct >= mx ? "MAXED" : @PKG@.CollUtil.fmt(sm) + " / " + @PKG@.CollUtil.fmt(next) + " to tier " + @PKG@.CollUtil.roman(ct + 1));
/*=TABLE=*/
  for (int t = 1; t <= mx; t++) {
/*=LOOK=*/
/*=TIER=*/
    b.set("#SkyyCTr" + t + "S.Text", st);
    b.set("#SkyyCTr" + t + "T.Text", @PKG@.CollUtil.roman(t));
    b.set("#SkyyCThr" + t + ".Text", @PKG@.CollUtil.fmt(@PKG@.CollReg.threshold(R, c, t)));
    b.set("#SkyyCRew" + t + ".Text", @PKG@.CollReg.rewardTextB(R, c, t, t > ct && t <= bt) + (t > ct && t <= bt ? "  (paid when reached)" : ""));
  }
/*=BUYROW=*/
  b.set("#SkyyCFrom.Text", "From: " + R.from[c]);
  Object[] o = @PKG@.CollBypass.offer(d, R, c);
  if (o[2] == null) {
    int nt = ((Integer) o[0]).intValue();
    long price = ((Long) o[1]).longValue();
/*=BUYOK=*/
    b.set("#SkyyCBuyLbl.Text", "Buy tier " + @PKG@.CollUtil.roman(nt) + " unlocks - " + price + " coins");
    bind(ev, "SkyyCBuy", "cbuy");
    b.set("#SkyyCBuyInfo.Text", @PKG@.CollBypass.unlockText(c, nt));
  } else {
/*=BUYNO=*/
    b.set("#SkyyCBuyInfo.Text", (String) o[2]);
  }
/*=BOTTOM=*/
  b.appendInline("#SkyyCHead", CATBACK[R.cat[c]]);
/*=BOTTOM2=*/
}"""
COLL_RC_TPL = r"""
public void buildRecipes(@UCB@ b, @UEB@ ev, @PKG@.CollData d, @PKG@.RegData R) {
  java.util.ArrayList lines = new java.util.ArrayList();
  java.util.HashSet seen = new java.util.HashSet();
  for (int c = 0; c < R.n; c++) {
    if (R.hidden[c]) continue;
    int ct = @PKG@.CollStore.countTier(d, R, c);
    int eff = @PKG@.CollStore.effTier(d, R, c);
    for (int t = 1; t <= eff; t++) {
      String[] rs = @PKG@.CollReg.recipesAt(c, t);
      for (int i = 0; i < rs.length; i++) {
        if (t > ct && @PKG@.CollUtil.bagRank(rs[i]) > @PKG@.CollReg.BYP_BAGMAX) continue;
        if (!seen.add(rs[i])) continue;
        lines.add(@PKG@.CollUtil.prettyRecipe(rs[i]) + "    (" + R.name[c] + " " + @PKG@.CollUtil.roman(t) + (t > ct ? " - bought" : "") + ")");
      }
    }
  }
  java.util.Iterator it = @PKG@.CollUnlocks.compute(d).iterator();
  while (it.hasNext()) { String rid = (String) it.next(); if (seen.add(rid)) lines.add(@PKG@.CollUtil.prettyRecipe(rid) + "    (auto rule)"); }
/*=HEAD=*/
  b.set("#SkyyCRSub.Text", lines.isEmpty() ? "No recipes yet - reach tier I of Wheat, Oak Log or Cobblestone for the first ones." : lines.size() + " recipe(s). Craft them in /craft - Collections tab (materials still needed, no bench).");
  int shown = lines.size() > 40 ? 39 : lines.size();
  for (int i = 0; i < shown; i++) {
/*=LINE=*/
    b.set("#SkyyCRn" + i + ".Text", (String) lines.get(i));
  }
  if (lines.size() > 40) {
/*=MORE=*/
    b.set("#SkyyCRMore.Text", "... and " + (lines.size() - 39) + " more (/collections unlocks)");
  }
/*=BOTTOM=*/
  bind(ev, "SkyyCBack", "cback");
  bind(ev, "SkyyCClose", "cclose");
}"""
COLL_BUILD_TPL = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.RegData R = @PKG@.CollReg.D;
  @PKG@.CollData d = @PKG@.CollStore.data(u);
/*=SHELL=*/
  if (R == null || d == null) {
/*=ERR=*/
    bind(ev, "SkyyCClose", "cclose");
    return;
  }
  if (this.view == 2 && this.coll >= 0 && this.coll < R.n && !R.hidden[this.coll]) buildDetail(b, ev, d, R);
  else if (this.view == 1 && this.cat >= 0 && this.cat < 4) buildCat(b, ev, d, R);
  else if (this.view == 3) buildRecipes(b, ev, d, R);
  else { this.view = 0; buildHome(b, ev, d, R); }
  b.set("#SkyyCStatus.Text", this.status == null ? "" : this.status);
}"""


def coll_look_java():
    """The tier row look chain (0.2.3's st / col / tc if chain, its state words unchanged; the colours from the kit)."""
    c = dict((st, (SUI.COLOR[a], SUI.COLOR[b])) for st, a, b in COLL_TIER_LOOK)
    return ('    String st = "LOCKED"; String col = "%s"; String tc = "%s";\n'
            '    if (t <= ct) { st = "DONE"; col = "%s"; tc = "%s"; }\n'
            '    else if (t <= bt) { st = "BOUGHT"; col = "%s"; tc = "%s"; }\n'
            '    else if (t == eff + 1) { st = "NEXT"; col = "%s"; tc = "%s"; }'
            % (c["LOCKED"] + c["DONE"] + c["BOUGHT"] + c["NEXT"]))


def _coll_bars(w):
    return {"BARW1": str(w), "BARW2": str(w), "BARW3": str(w), "BARW4": str(w), "MAXCOL": SUI.COLOR["success"]}


def _coll_split(ap, k):
    a, b = SUI.Appends(ap[:k]), SUI.Appends(ap[k:])
    b.sets = list(ap.sets)
    return a, b


for _m in COLL_CATOPEN + COLL_CATBACK:
    SUI.check_markup(_m, COLL_PREFIX)
COLL_FIELDS = ["public static final String[] CATOPEN = new String[] { %s };" % ", ".join(SUI.java_lit(m) for m in COLL_CATOPEN),
               "public static final String[] CATBACK = new String[] { %s };" % ", ".join(SUI.java_lit(m) for m in COLL_CATBACK)]
_coll_db = coll_det_bottom()           # (spacer,) result line, separator, #SkyyCHead | then HOME, spacer, CLOSE in #SkyyCHead
_coll_db = _coll_split(_coll_db, [p for p, _m in _coll_db].index("SkyyCHead"))
assert all(p == "SkyyColl" for p, _m in _coll_db[0]) and all(p == "SkyyCHead" for p, _m in _coll_db[1])
COLL_SRC = {}                          # method name -> Java source (before the @TOKEN@ replacement of M())
COLL_SRC["statusColor"] = COLL_STATUS_SRC
COLL_SRC["catCard"] = coll_fill(COLL_CATCARD_TPL, {"BARW": str(COLL_CAT_IN), "CARD": coll_java(coll_cat_card(), 2)})
COLL_SRC["buildHome"] = coll_fill(COLL_HOME_TPL, {
    "TOP": coll_java(coll_home_top(), 2), "ROW": coll_java(coll_home_row(), 4),
    "GAP": coll_java(SUI.Appends([("SkyyCHRow" + SUI.J("row", "0"), COLL_HGAP)]), 4), "BOTTOM": coll_java(coll_home_bottom(), 2)})
COLL_SRC["card"] = coll_fill(COLL_CARD_TPL, dict(_coll_bars(COLL_CD_TEXT), **{
    "UNDISC": coll_java(coll_cd_undisc(), 4), "TOP": coll_java(coll_cd_top(), 2), "ICON": coll_java(coll_cd_icon(), 0),
    "TEXT": coll_java(coll_cd_text(), 2)}))
COLL_SRC["buildCat"] = coll_fill(COLL_CAT_TPL, {
    "HEAD": coll_java(coll_cat_head(), 2), "ROWS": str(COLL_GRID_ROWS), "COLS1": str(COLL_GRID_COLS), "COLS2": str(COLL_GRID_COLS),
    "ROW": coll_java(coll_cat_grow(), 4), "GAP": coll_java(SUI.Appends([("SkyyCGRow" + SUI.J("row", "0"), COLL_CGAP)]), 0),
    "PAGER": coll_java(coll_cat_pager(), 4), "PAGE1": coll_java(coll_cat_page1(), 4), "BOTTOM": coll_java(coll_cat_bottom(), 2)})
COLL_SRC["buildDetail"] = coll_fill(COLL_DET_TPL, dict(_coll_bars(COLL_DBAR_W), **{
    "TOP": coll_java(coll_det_top(icon=None), 2), "BAR": coll_java(coll_det_bar(), 2), "TABLE": coll_java(coll_det_table(), 2),
    "LOOK": coll_look_java(), "TIER": coll_java(coll_det_tier(), 4), "BUYROW": coll_java(coll_det_buyrow(), 2),
    "BUYOK": coll_java(coll_det_buyok(), 4), "BUYNO": coll_java(coll_det_buyno(), 4),
    "BOTTOM": coll_java(_coll_db[0], 2), "BOTTOM2": coll_java(_coll_db[1], 2)}))
COLL_SRC["buildRecipes"] = coll_fill(COLL_RC_TPL, {
    "HEAD": coll_java(coll_rc_head(), 2), "LINE": coll_java(coll_rc_line(), 4), "MORE": coll_java(coll_rc_more(), 4),
    "BOTTOM": coll_java(coll_rc_bottom(), 2)})
COLL_SRC["build"] = coll_fill(COLL_BUILD_TPL, {"SHELL": coll_java(COLL_SHELL.appends, 2), "ERR": coll_java(coll_err(), 4)})


# ---------------------------------------------------------------- build-time proof on sample states (the Java's append order)
def coll_state(view, **kw):
    """One page state as the Appends the Java sends, in its order (frame first), with concrete ids and values:
    view "home" (kw: none), "cat" (kw: cells = [None = no card | "disc" | "undisc" | "disc-noicon"] x 12, pages), "detail" (kw: tiers,
    icon, buy), "recipes" (kw: lines), "error". Used for check_page / assert_proven / the height budget below and by the harness."""
    ap = SUI.Appends(COLL_SHELL.appends)

    def put(part, parent=None):
        for p, mk in part:
            ap.add(parent if p == COLL_PARENT else p, mk)
        ap.sets.extend(part.sets)
    if view == "error":
        put(coll_err())
        return ap
    if view == "home":
        put(coll_home_top())
        for row in range(2):
            put(coll_home_row(str(row)))
            for k in range(2):
                cat = str(row * 2 + k)
                if k:
                    ap.add("SkyyCHRow" + str(row), COLL_HGAP)
                put(coll_cat_card(cat, COLL_ACCENT[int(cat)], 200), "SkyyCHRow" + str(row))
                ap.add("SkyyCCatAct" + cat, COLL_CATOPEN[int(cat)])
        put(coll_home_bottom())
    elif view == "cat":
        cells, pages = kw.get("cells", ["disc"] * 12), kw.get("pages", 2)
        put(coll_cat_head(COLL_ACCENT[0]))
        for row in range(COLL_GRID_ROWS):
            put(coll_cat_grow(str(row)))
            for col in range(COLL_GRID_COLS):
                n = row * COLL_GRID_COLS + col
                if cells[n] is None:
                    break
                if col > 0:
                    ap.add("SkyyCGRow" + str(row), COLL_CGAP)
                par = "SkyyCGRow" + str(row)
                if cells[n] == "undisc":
                    put(coll_cd_undisc(str(n)), par)
                    continue
                put(coll_cd_top(str(n)), par)
                if cells[n] == "disc":
                    put(coll_cd_icon(str(n), "Ore_Copper"))
                put(coll_cd_text(str(n), 120, COLL_ACCENT[1]))
        put(coll_cat_pager() if pages > 1 else coll_cat_page1())
        put(coll_cat_bottom())
    elif view == "detail":
        put(coll_det_top(COLL_ACCENT[2], icon=kw.get("icon", True)))
        put(coll_det_bar(350, COLL_ACCENT[2]))
        put(coll_det_table())
        for t in range(1, kw.get("tiers", 10) + 1):
            put(coll_det_tier(str(t), SUI.COLOR["success"], SUI.COLOR["rowName"]))
        put(coll_det_buyrow())
        put(coll_det_buyok() if kw.get("buy", True) else coll_det_buyno())
        put(_coll_db[0])
        ap.add("SkyyCHead", COLL_CATBACK[2])
        put(_coll_db[1])
    elif view == "recipes":
        lines = kw.get("lines", 40)
        put(coll_rc_head())
        shown = 39 if lines > 40 else lines
        for i in range(shown):
            put(coll_rc_line(str(i), str(i // 20)))
        if lines > 40:
            put(coll_rc_more())
        put(coll_rc_bottom())
    return ap


def coll_views():
    """Every view on sample states: check_page (ids, prefix, no duplicates, parents first, b.set targets exist, markup rules),
    assert_proven (only what the deployed pages use, minus PROBED), the body filled exactly and every Left row / Top column fitting
    its parent (read back out of the markup: used_height / used_width). Returns the states it checked."""
    states = [("error", {}), ("home", {}), ("cat", {"pages": 2}), ("cat", {"pages": 1, "cells": ["disc", "undisc"] * 3 + [None] * 6}),
              ("cat", {"pages": 3, "cells": ["disc-noicon"] * 5 + ["undisc"] * 7}), ("detail", {"tiers": 10}),
              ("detail", {"tiers": 7, "icon": False, "buy": False}), ("detail", {"tiers": 20}), ("recipes", {"lines": 0}),
              ("recipes", {"lines": 40}), ("recipes", {"lines": 57})]
    for view, kw in states:
        ap = coll_state(view, **kw)
        SUI.check_page(ap, COLL_PREFIX)
        SUI.assert_proven(ap, what="collections %s %s" % (view, kw))
        used = SUI.used_height(ap, "SkyyColl")
        assert used == COLL_IH, "%s %s: the body holds %d px of %d" % (view, kw, used, COLL_IH)
        for p, mk in ap:
            for v in (mk.variants() if isinstance(mk, SUI.Choice) else (mk,)):
                r = SUI.render(v)
                m = re.match(r"Group #([A-Za-z0-9]+) \{([^{}]*)", r)
                if not m or not any(q is not None and SUI.render(q) == m.group(1) for q, _m in ap):
                    continue
                ident, own = m.group(1), m.group(2)
                lay = re.search(r"LayoutMode: (Left|Top);", own)
                anc = re.search(r"Anchor: \(([^)]*)\)", own)
                if not lay or not anc or lay.group(1) == "TopScrolling":
                    continue
                a = dict((k, int(x)) for k, x in re.findall(r"(Width|Height): (\d+)", anc.group(1)))
                pad = re.search(r"Padding: \(([^)]*)\)", own)
                pv = dict((k, int(x)) for k, x in re.findall(r"(Left|Right|Top|Bottom|Horizontal|Vertical|Full): (\d+)",
                                                            pad.group(1))) if pad else {}
                if lay.group(1) == "Left" and "Width" in a:
                    room = a["Width"] - pv.get("Left", 0) - pv.get("Right", 0) - 2 * (pv.get("Horizontal", 0) + pv.get("Full", 0))
                    got = SUI.used_width(ap, ident)
                    assert got <= room, "%s %s: row #%s holds %d px of %d" % (view, kw, ident, got, room)
                if lay.group(1) == "Top" and "Height" in a:
                    room = a["Height"] - pv.get("Top", 0) - pv.get("Bottom", 0) - 2 * (pv.get("Vertical", 0) + pv.get("Full", 0))
                    got = SUI.used_height(ap, ident)
                    assert got <= room, "%s %s: column #%s holds %d px of %d" % (view, kw, ident, got, room)
    return states


COLL_VIEWS = coll_views()
# the page id: a hash of every piece of CollPage this build makes from the kit (the static button fields and every page method
# source) - a later kit change that alters the page changes it; it is in the ready log line. COLL_PAGE_CHECKED = the page the
# harness SkyyCollections/test_skyycollections_0.2.4.py last passed on (tools/coll_0_2_4_patch.py PAGE_CHECKED)
COLL_PAGE_ID = hashlib.sha256("\n".join(COLL_FIELDS + [COLL_SRC[k] for k in sorted(COLL_SRC)]).encode("utf8")).hexdigest()[:12]
COLL_PAGE_CHECKED = "@@PAGECHECKED@@"
print("collections page: %d x %d on %s, page %s, %d sample states checked" % (COLL_W, COLL_H, KIT_ID, COLL_PAGE_ID, len(COLL_VIEWS)))
# ---- COLL PAGE BLOCK END
'''


# ================================================================================================ docstring of the generated script
HEAD_OLD = '''"""SkyyCollections 0.2.3 - build script (derived from 0.2.2 by tools/coll_0_2_3_patch.py - edit the patch, not this file; 0.2.2 was
derived from 0.2.1 by tools/coll_0_2_2_patch.py; 0.2.1 from 0.2 by tools/coll_0_2_1_patch.py; 0.2 was written fresh: the 0.1.5
per-profile code, the coll:recipes bridge contract and the page command rules are carried over, everything else follows
research/Collections-Spec.md).
'''
HEAD_NEW = '''"""SkyyCollections 0.2.4 - build script (javassist via jpype). GENERATED by tools/coll_0_2_4_patch.py from the LIVE 0.2.3
(build_skyycollections_0.2.3.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.3 was derived from 0.2.2 by
tools/coll_0_2_3_patch.py; 0.2.2 from 0.2.1 by tools/coll_0_2_2_patch.py; 0.2.1 from 0.2 by tools/coll_0_2_1_patch.py; 0.2 was written
fresh: the 0.1.5 per-profile code, the coll:recipes bridge contract and the page command rules are carried over, everything else
follows research/Collections-Spec.md).

0.2.4 (2026-09-29, the vanilla UI pass - Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them to look and
feel vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md): ONLY THE LOOK OF THE /collections PAGE CHANGED, on the
shared kit tools/skyyui.py (full notes: tools/coll_0_2_4_patch.py). Commands, permissions, config keys, the counts / rewards files and
their migrations, coll:fn:where and every bridge key, the bag ladder, the coin path (CollBypass), every element id of 0.2.3, the 17
event bindings (bind calls) and their EventData, the view logic (view / cat / pageNo / coll / status / cards[12]) and every page text are
0.2.3's (the patch asserts it). Deploy rule unchanged: SkyySacks 0.7.7 + SkyyCollections 0.2.3/0.2.4 go together.
  - The build calls SUI.verify() first (every vanilla value / texture / sound the page uses is proven against Assets.zip, read-only;
    a game update that changes one stops the build); KIT_ID and COLL_PAGE_ID (a hash of the kit-emitted page code) are in the ready
    log line. The page code (the COLL PAGE block below) runs the kit when this script runs.
  - Window: the vanilla decorated container (title bar with runes, the gold ornaments, COLLECTIONS in the vanilla title style), 1120 x
    826 (fits 1080); 0.2.3's root #SkyyColl is the body now. Every view: content, the result line (vanilla green / info blue / red),
    the content separator, a footer of Secondary buttons (Close / Back with the vanilla cancel sound).
  - Home: a summary well, 2 x 2 category cards (vanilla wells: icon in the slot border, name in the category accent, found line,
    tier bar, tiers line, OPEN <CATEGORY>), spaced to fill the body (no blank band). Category: one list well of 12 collection rows
    (2 x 6, vanilla list-row panels with the status bar, icon, name, progress bar, tier and next-reward lines, a small OPEN button =
    0.2.3's #SkyyCCard<n>), the kit pager. Collection: a summary well, the progress bar, the tier table (section-label heads
    STATE 90 / TIER 56 / NEEDED 110 / REWARDS 802 px over a scrolling list well; state words in the vanilla colours), "From:", a buy
    well (Primary BUY + 0.2.3's Buy text as a label + the unlock info). Unlocked recipes: two vanilla wells of 20 lines. Error:
    0.2.3's line in the vanilla error red.
  - Two 0.2.3 ids hold another text (declared; the harness compares every id's text and allows only these two): #SkyyCCard<n> was
    the collection-name button and is the small OPEN button (the name is #SkyyCCd<n>Nm and is not clickable), #SkyyCBuy said
    "Buy tier III unlocks - 1500 coins" and says BUY (that text is #SkyyCBuyLbl beside it). Both keep their binding and EventData.
  - Known limits (not regressions): the tier list scrolls for curves over 10 tiers and every click rebuilds the page, so the scroll
    goes back to the top; the rewards cell is one 802 px line (0.2.3: 740) that cannot wrap or be clipped - an admin-edited
    rewards.properties line wider than that (about 90 characters) runs past the row; the shipped registry's widest is 738 px.
  - A kit change that alters the page makes the build print a WARNING (the page id is not the checked one); with the environment
    variable SKYY_REQUIRE_CHECKED_PAGE=1 the build stops instead, before the jar is written (for a deploy / SET-bump procedure).
@@CHECKED@@
  UNVERIFIED (needs the game): the whole new look - the kit's "base" look (skyyui probe pages base1 / base2 / base3) and its 1.4 blocks
    (probe page base4: stat_bar, list_well, the fixed rows, and the column heads = the kit's section labels with
    HorizontalAlignment: Start, a value no deployed page has used yet - the tier table heads here) have not been seen in game yet,
    nor a TopScrolling list inside a kit window on this client. This page has no runtime fallback: a parse error disconnects on
    /collections, /coll <name>, every OPEN click and the SkyyMenu Collections tile. It goes into a test deploy only after Skyy has
    opened base1, base2, base3 and base4 cleanly (base4 must show its column heads); keep the SET pin at 0.2.3 until Skyy has seen
    this page in game.
'''
# what 0.2.4 was checked with: every claim is what the COMMITTED harness SkyyCollections/test_skyycollections_0.2.4.py checks - re-run it
CHECKED = '''  CHECKED with SkyyCollections/test_skyycollections_0.2.4.py (committed; re-run it: python SkyyCollections/test_skyycollections_0.2.4.py) -
    2026-09-29 (review fix2), kit skyyui 1.4 ac93356c4c60, page 0b8c336ae94b; one JVM with -Xverify:all, HytaleServer.jar, 0.2.3 and 0.2.4 each in
    its own class loader: A all 47 classes of both jars load, verify and initialise. B 43 classes byte-identical to 0.2.3; CfgFn /
    CfgRows identical but their version string, SkyyCollectionsPlugin identical but its ready line; CollPage: 0.2.3's fields +
    CATOPEN / CATBACK, the constructor, bind, closePage, handleDataEvent and openFor instruction-identical (constants compared by
    value), bs / btn / lab / sp / bar / icon gone, statusColor new. C statusColor on every CollBypass result text, "" and null.
    D 177 page states x 2 jars through the engine's UICommandBuilder / UIEventBuilder on the real registry (both error views, home x
    3 data profiles, every category page + a page past the end, collection views incl. coin unlocks off, free bags, bagMax none /
    legendary, a bazaar price, a 20-tier curve, hidden / out-of-range fallbacks, recipes none / some / exactly 40 / 41 / 57+, every
    result text): identical bindings (type, selector, EventData, order) and page state (view, cat, pageNo, coll, status, cards[12]),
    every 0.2.3 element id and text still there (0.2.4 adds only Open, Buy, the four column heads and the window title), and per
    element id the same text in the same id: 10168 id texts compared with the clicks' rebuilt pages, the only differences the two
    declared moves (426: #SkyyCCard<n> says Open and its name is in #SkyyCCd<n>Nm, #SkyyCBuy says Buy and its text is in
    #SkyyCBuyLbl), 10725 appends through check_markup, 177 pages through check_page + assert_proven, only kit / data colours, 2114
    layout checks (every body filled exactly, every fixed row / column holds its children). E 76 clicks in 3 sequences (browsing +
    the pager ends, a two-click coin buy, a refused buy): identical page state, purse, counts file, bypass.log and rebuilt page.
    F 862 button labels and shown texts measured with the client's font tables: all fit; the widest tier rewards text is 738 px of
    its 802 px cell. G the page id in the jar = the kit's page now = COLL_PAGE_CHECKED.'''
# the page id (COLL_PAGE_ID, a hash of the kit-emitted CollPage code) the harness last passed on
PAGE_CHECKED = "0b8c336ae94b"
rep(HEAD_OLD, fill(HEAD_NEW, {"CHECKED": CHECKED}))
# the 0.2.3 docstring's page paragraph described the 0.2.3 look (card grid, chips, 1120 x 840 root): rewrite it for 0.2.4
rep("  Page (/collections, /coll, /coll <name>): one inline page, three views switched with rebuild() (HOME categories -> CATEGORY grid of\n"
    "    12 cards -> COLLECTION tier list with DONE / NEXT / LOCKED / BOUGHT chips and the Buy button) plus an Unlocked recipes view.\n"
    "    1120 x 840 root with only Width/Height, no underscores in ids, TextButton + EventData matched with a trailing quote, dynamic\n"
    "    text via b.set, no periodic updates, the page never closes itself before opening something else.\n",
    "  Page (/collections, /coll, /coll <name>): one inline page, three views switched with rebuild() (HOME 2 x 2 category cards ->\n"
    "    CATEGORY list well of 12 collection rows, 2 x 6, each with a small OPEN button -> COLLECTION tier table with the DONE / NEXT /\n"
    "    LOCKED / BOUGHT state words in the vanilla colours and the buy well) plus an Unlocked recipes view. 0.2.4 look: the vanilla\n"
    "    decorated window, 1120 x 826 root with only Width/Height (0.2.3: 1120 x 840, no frame), no underscores in ids, TextButton +\n"
    "    EventData matched with a trailing quote, dynamic text via b.set, no periodic updates, the page never closes itself before\n"
    "    opening something else.\n")
rep("Run:   python build_skyycollections_0.2.3.py          -> SkyyCollections/SkyyCollections-0.2.3.jar\n"
    "       (--deploy copies to Mods/SkyyCollections.jar - Skyy's OK needed first)",
    "Run:   python build_skyycollections_0.2.4.py          -> SkyyCollections/SkyyCollections-0.2.4.jar\n"
    "       (never --deploy from a build: tools/deploy_set.py installs the whole set once Skyy says deploy)")

# ================================================================================================ version, kit import, data colours
rep('VERSION = "0.2.3"', 'VERSION = "0.2.4"')
UI_DATA = ["#e0c060", "#9fb8cc", "#7fcf7a", "#e07a6a", "#7fb8e0", "#ffc800", "#c8f0a0", "#e8d8a0", "#7fdcff", "#c8b070", "#ffe08a",
           "#e6f0ff"]
rep("import skyybuild as B\n", '''import skyybuild as B
import skyyui as SUI       # 0.2.4: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"
SUI.verify()               # proves every vanilla value / texture / sound the page uses against Assets.zip (read-only); stops the build on drift
KIT_ID = SUI.kit_id()      # "skyyui <version> <blob12>" - in the ready log line
# 0.2.4: DATA colours for the vanilla UI kit's lint (research/Vanilla-UI-Style-Guide.md section 5): the category accents (CollReg.ACCENT:
# category names, cards and bars on /collections; the page's COLL_ACCENT reads them from here) + the chat line colours (Message.color)
UI_DATA_COLORS = [%s,
                  %s]
''' % (", ".join('"%s"' % c for c in UI_DATA[:5]), ", ".join('"%s"' % c for c in UI_DATA[5:])))

# ================================================================================================ CollPage: the look only
rep("# ================= CollPage: one inline page, views switched with rebuild() =================",
    "# ================= CollPage: one inline page, views switched with rebuild() (0.2.3 logic; 0.2.4 look = the vanilla UI kit tools/skyyui.py) =================")
OLD_PAGE = cut(PAGE_A, PAGE_B, "@@COLLPAGE@@")
_bi = OLD_PAGE.index('M(page, r"""\npublic static void bind(')
BIND_SRC = OLD_PAGE[_bi:OLD_PAGE.index('M(page, r"""\npublic void catCard(')]
assert BIND_SRC == ('M(page, r"""\npublic static void bind(@UEB@ ev, String id, String payload) {\n'
                    '  ev.addEventBinding(@BT@.Activating, "#" + id, @EVD@.of("a", payload));\n}""")\n'), BIND_SRC
for _gone in ("bs", "btn", "lab", "sp", "bar", "icon"):
    assert ("public static String %s(" % _gone in OLD_PAGE) or ("public static void %s(" % _gone in OLD_PAGE), _gone
METHODS = ("catCard", "buildHome", "card", "buildCat", "buildDetail", "buildRecipes", "build")


def old_method(name):
    i = OLD_PAGE.index("public void %s(" % name)
    return OLD_PAGE[i:OLD_PAGE.index('}"""', i) + 1]


def new_template(name):
    tpl = {"catCard": "COLL_CATCARD_TPL", "buildHome": "COLL_HOME_TPL", "card": "COLL_CARD_TPL", "buildCat": "COLL_CAT_TPL",
           "buildDetail": "COLL_DET_TPL", "buildRecipes": "COLL_RC_TPL", "build": "COLL_BUILD_TPL"}[name]
    i = NEW_PAGE.index(tpl + ' = r"""\n') + len(tpl + ' = r"""\n')
    return NEW_PAGE[i:NEW_PAGE.index('}"""', i) + 1]


def is_markup(ln):
    return "b.appendInline(" in ln or "icon(b, " in ln or "bar(b, " in ln


# 0.2.3 lines that are look, not logic, and changed: the grid loops (3 x 4 cards -> 2 columns x 6 lines, the same 12 per page and
# the same n order) and the tier chip colours (the state words stay; checked below with the colours taken out)
LOOK_LINES = {"buildCat": ["  for (int row = 0; row < 3; row++) {", "    for (int col = 0; col < 4; col++) {",
                           "      int n = row * 4 + col;"],
              "buildDetail": ['    String st = "LOCKED"; String col = "#8a3a36"; String tc = "#9aa8b6";',
                              '    if (t <= ct) { st = "DONE"; col = "#3aa655"; tc = "#dcf5e0"; }',
                              '    else if (t <= bt) { st = "BOUGHT"; col = "#d98a2b"; tc = "#f5e0c0"; }',
                              '    else if (t == eff + 1) { st = "NEXT"; col = "#d9b038"; tc = "#fff0c0"; }']}
# the lines the new templates add besides the kit's appends (/*=NAME=*/ tokens): locals for the look, the static button pick, and
# the b.set lines of texts 0.2.3 wrote inline (TEXT_MOVES below proves each one shows the same Java expression)
NEW_LINES = {"catCard": ["  String acc = @PKG@.CollReg.ACCENT[cat];", "  int fill = tt > 0L ? (int) (/*=BARW=*/L * td / tt) : 0;",
                         '  b.appendInline("#SkyyCCatAct" + cat, CATOPEN[cat]);',
                         '  b.set("#SkyyCCatNm" + cat + ".Text", @PKG@.CollReg.CATS[cat]);'],
             "buildHome": [],
             "card": ["  int fill = ct >= mx ? /*=BARW1=*/ : (int) (/*=BARW2=*/L * sm / (next < 1L ? 1L : next));",
                      "  if (fill < 0) fill = 0;", "  if (fill > /*=BARW3=*/) fill = /*=BARW4=*/;",
                      '  String fc = ct >= mx ? "/*=MAXCOL=*/" : @PKG@.CollReg.ACCENT[R.cat[c]];', "  if (R.iconOk[c]) /*=ICON=*/",
                      '  b.set("#SkyyCCd" + n + "Nm.Text", R.name[c]);'],
             "buildCat": ["  for (int row = 0; row < /*=ROWS=*/; row++) {", "    for (int col = 0; col < /*=COLS1=*/; col++) {",
                          "      int n = row * /*=COLS2=*/ + col;", "      if (col > 0) /*=GAP=*/",
                          '  b.set("#SkyyCCatTitle.Text", @PKG@.CollReg.CATS[this.cat] + " Collections");'],
             "buildDetail": ["  int fill = ct >= mx ? /*=BARW1=*/ : (int) (/*=BARW2=*/L * sm / (next < 1L ? 1L : next));",
                             "  if (fill < 0) fill = 0;", "  if (fill > /*=BARW3=*/) fill = /*=BARW4=*/;",
                             '  String fc = ct >= mx ? "/*=MAXCOL=*/" : acc;', '    b.set("#SkyyCTr" + t + "S.Text", st);',
                             '    b.set("#SkyyCTr" + t + "T.Text", @PKG@.CollUtil.roman(t));',
                             '    b.set("#SkyyCBuyLbl.Text", "Buy tier " + @PKG@.CollUtil.roman(nt) + " unlocks - " + price + " coins");',
                             '  b.appendInline("#SkyyCHead", CATBACK[R.cat[c]]);'],
             "buildRecipes": [], "build": []}
# texts 0.2.3 wrote INLINE (through safe()) that 0.2.4 b.sets: (method, the 0.2.3 Java expression, the 0.2.4 line that sets it)
TEXT_MOVES = [("catCard", "@PKG@.CollReg.CATS[cat]", '  b.set("#SkyyCCatNm" + cat + ".Text", @PKG@.CollReg.CATS[cat]);'),
              ("card", "R.name[c]", '  b.set("#SkyyCCd" + n + "Nm.Text", R.name[c]);'),
              ("buildCat", '@PKG@.CollReg.CATS[this.cat] + " Collections"',
               '  b.set("#SkyyCCatTitle.Text", @PKG@.CollReg.CATS[this.cat] + " Collections");'),
              ("buildDetail", "lab(null, \"Full: 0\", st, ", '    b.set("#SkyyCTr" + t + "S.Text", st);'),
              ("buildDetail", "@PKG@.CollUtil.roman(t), 20, true", '    b.set("#SkyyCTr" + t + "T.Text", @PKG@.CollUtil.roman(t));'),
              ("buildDetail", '"Buy tier " + @PKG@.CollUtil.roman(nt) + " unlocks - " + price + " coins"',
               '    b.set("#SkyyCBuyLbl.Text", "Buy tier " + @PKG@.CollUtil.roman(nt) + " unlocks - " + price + " coins");')]
for _m in METHODS:
    _old = old_method(_m).split(LF)
    _new = new_template(_m).split(LF)
    _logic = [ln for ln in _old if ln.strip() and not is_markup(ln) and ln not in LOOK_LINES.get(_m, [])]
    for ln in _logic:
        assert _new.count(ln) == _old.count(ln), "%s: the 0.2.3 line is not kept word for word in 0.2.4: %s" % (_m, ln)
    for ln in LOOK_LINES.get(_m, []):
        assert _old.count(ln) == 1, "%s: 0.2.3 look line not found: %s" % (_m, ln)
    _extra = [ln for ln in _new if ln.strip() and not re.fullmatch(r"\s*/\*=[A-Z0-9]+=\*/", ln) and ln not in _logic]
    assert sorted(_extra) == sorted(NEW_LINES[_m]), "%s: lines the template adds: %s" % (_m, sorted(set(_extra) ^ set(NEW_LINES[_m])))
    assert [ln for ln in _old if "bind(ev, " in ln] == [ln for ln in _new if "bind(ev, " in ln], "%s: bindings changed" % _m
for _m, _expr, _line in TEXT_MOVES:
    assert _expr in old_method(_m), "%s: 0.2.3 inline text expression not found: %s" % (_m, _expr)
    assert _line in new_template(_m).split(LF), "%s: 0.2.4 b.set line missing: %s" % (_m, _line)
# the tier state words: the same chain with the colours taken out (0.2.4 fills in the kit's colours: COLL_TIER_LOOK)
for ln in LOOK_LINES["buildDetail"]:
    assert re.sub(r'"#[0-9a-f]{6}"', '"%s"', ln) in NEW_PAGE, "the tier look chain changed beyond its colours: " + ln
# the static texts 0.2.4 b.sets (they hold a dot or "?") are 0.2.3's inline texts
for _t in ("Gather items yourself to raise collections. Every tier unlocks rewards.", "???",
           "Your collections could not be read right now - try again in a moment."):
    assert ('"%s"' % _t) in OLD_PAGE and ('"%s"' % _t) in NEW_PAGE, _t
for _t in ("Fishing - coming later", "Gather one to discover it", "Unlocked recipes", "Refresh", "Close", "< Back", "Home", "< Prev",
           "Next >", "Collections"):
    assert ('"%s"' % _t) in OLD_PAGE, _t
# the old grid: 12 cards per page in 3 x 4, the new: 2 x 6 (asserted in the block: COLL_GRID_ROWS * COLL_GRID_COLS == 12)
assert "int pages = (list.size() + 11) / 12;" in old_method("buildCat") and "this.cards = new int[12];" in s

# CollPage.statusColor: the result line colour from CollBypass.click's texts (unchanged, no + / - / = marks). EVERY text click() /
# offer() can return is listed with its colour; a changed or new text stops this patch until its colour is decided.
_byp = block("# ================= CollBypass: coins buy the NEXT tier's recipe unlocks only =================",
             "# ================= PlacedStore")
_click = _byp[_byp.index("public static String click("):]
_offer = _byp[_byp.index("public static Object[] offer("):_byp.index("public static String unlockText(")]
_texts = []
for _st in re.findall(r"return (.*?);\n", _click) + re.findall(r"err = (.*?);", _offer):
    _texts += [t for t in re.findall(r'"((?:[^"\\]|\\.)*)"', _st) if t[:1].isupper()]
STATUS_TEXTS = [("Your collections could not be read right now.", "-"), ("Click Buy again within 10 s to pay ", "="),
                ("Coin unlocks need SkyyCoins, which is not loaded.", "-"), ("You need ", "-"),
                ("Could not save the purchase - your coins were refunded.", "-"),
                ("Could not save the purchase and the refund failed - tell an admin (bypass.log).", "-"), ("Bought the tier ", "+"),
                ("Coin unlocks are turned off on this server.", "-"), ("Collections are not loaded.", "-"),
                ("Coin unlocks are not available for this collection.", "-"),
                ("Collect one first - coin unlocks need a discovered collection.", "-"), ("Every tier is unlocked.", "-"),
                ("Coin unlocks are not available for ", "-"), ("Tier ", "-"), ("Nothing more here can be bought with coins - gather it.", "-")]
assert _texts == [t for t, _c in STATUS_TEXTS], "CollBypass status texts changed - decide their colours: %s" % _texts
for _t, _c in STATUS_TEXTS:
    assert ("+" if _t.startswith("Bought the tier ") else ("=" if _t.startswith("Click Buy again ") else "-")) == _c, _t
assert 'COLL_STATUS_SRC = SUI.java_color_by_text("statusColor", [("startsWith", "Bought the tier ", "+"),' in NEW_PAGE
assert '("startsWith", "Click Buy again ", "=")], empty="=", default="-")' in NEW_PAGE
# handleDataEvent sets status only from CollBypass.click (and clears it); the page shows nothing else there
_hde = block('M(page, r"""\npublic void handleDataEvent(', 'M(page, r"""\npublic static void openFor(')
assert re.findall(r"this\.status = (.*?);", _hde) == ["@PKG@.CollBypass.click(this.playerRef, this.playerRef.getUuid(), this.coll)", '""'], _hde

# the page code of the generated script: the COLL PAGE block (kit calls at build time), then the fields and the methods in order
# (javassist: methods before their callers; bind() is 0.2.3's, verbatim), then the page-id check
PAGE_CODE = fill(NEW_PAGE, {"PAGECHECKED": PAGE_CHECKED}) + '''
# the CollPage fields and methods built above (javassist: a method before its callers; bind() is 0.2.3's, verbatim)
for _f in COLL_FIELDS:
    F(page, _f)
''' + BIND_SRC + '''M(page, COLL_SRC["statusColor"])
for _name in ("catCard", "buildHome", "card", "buildCat", "buildDetail", "buildRecipes", "build"):
    M(page, COLL_SRC[_name])
if COLL_PAGE_ID == COLL_PAGE_CHECKED:
    print("collections page %s = the page SkyyCollections/test_skyycollections_0.2.4.py last passed on" % COLL_PAGE_ID)
elif os.environ.get("SKYY_REQUIRE_CHECKED_PAGE") == "1":
    # a deploy / SET-bump procedure builds with SKYY_REQUIRE_CHECKED_PAGE=1: an unchecked page stops the build before the jar exists
    raise SystemExit("collections page %s is NOT the page SkyyCollections/test_skyycollections_0.2.4.py last passed on (%s) and "
                     "SKYY_REQUIRE_CHECKED_PAGE=1: no jar assembled. Build without the flag, run the harness, then set PAGE_CHECKED "
                     "in tools/coll_0_2_4_patch.py and regenerate" % (COLL_PAGE_ID, COLL_PAGE_CHECKED))
else:
    print("WARNING: collections page %s is NOT the page SkyyCollections/test_skyycollections_0.2.4.py last passed on (%s): the kit "
          "output changed the page. Run the harness, then set PAGE_CHECKED in tools/coll_0_2_4_patch.py and regenerate; never deploy "
          "an unchecked page (SKYY_REQUIRE_CHECKED_PAGE=1 makes this an error)" % (COLL_PAGE_ID, COLL_PAGE_CHECKED))
'''
rep("@@COLLPAGE@@", PAGE_CODE)

# ================================================================================================ the ready log line
rep(READY_OLD, 'log("[SkyyCollections] 0.2.4 ready (""" + KIT_ID + ", page " + COLL_PAGE_ID + r""") - item collections')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert [ln for ln in s.split(LF) if ln.lstrip().startswith("bind(ev, ")] == BIND_LINES0, "the bind(ev, ...) calls changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == EVB0, "event bindings changed"
for k in KEEP:
    assert k in s, "a block that must stay 0.2.3's changed: %s" % k[:80]
assert s.index("public static String safe(String t)") < s.index("COLL PAGE BLOCK START") < s.index("public void closePage(")
assert s.index("SUI.verify()") < s.index("J = B.start()"), "verify() must run before the build"
assert s.index("COLL_PAGE_ID = hashlib") < s.index('ready (""" + KIT_ID'), "COLL_PAGE_ID before the ready log line"
# data colours: CollReg.ACCENT is exactly UI_DATA_COLORS[:5] (the page reads COLL_ACCENT from there), CATS = the page's COLL_CATS,
# and every literal colour left in the script is a data colour (the kit gives the page its colours at build time)
_acc = re.search(r'public static final String\[\] ACCENT = new String\[\] \{ (.*?) \};', s).group(1)
assert re.findall(r'(#[0-9a-f]{6})', _acc) == UI_DATA[:5], _acc
assert 'COLL_CATS = ("Farming", "Mining", "Foraging", "Combat", "Fishing")' in s and 'CATS_PY = ("Farming", "Mining", "Foraging", "Combat", "Fishing")' in s
_code = LF.join(ln.split("#", 1)[0] if ln.lstrip().startswith("#") else ln for ln in s.split(LF))
_lits = set(c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}\b", _code))
assert _lits <= set(UI_DATA), "colour literals that are no data colour: %s" % sorted(_lits - set(UI_DATA))
assert set(re.findall(r"#[0-9a-fA-F]{6}\b", LF.join(ln for ln in OLD.split(LF)[:2872] + OLD.split(LF)[3225:]))) == set(UI_DATA), \
    "the 0.2.3 colours outside the page are the data colours listed in UI_DATA_COLORS"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.2.3 had %d)" % (s.count(LF), OLD.count(LF)))
