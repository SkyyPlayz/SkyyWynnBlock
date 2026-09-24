"""Derive SkyyMenu/build_skyymenu_0.1.2.py from 0.1.1.
0.1.2 (Skyy 2026-09-23):
 - FIX "Loading..." forever on every page opened FROM the menu (Sacks Craft tab, HUD editor edits, Craft page buttons, Bazaar
   buttons): 0.1.1 closed the menu (PageManager.setPage(None)) and THEN ran the command, which opened the next page at once.
   The client's close answer for the menu arrived after the new page was already set, so the server dismissed the NEW page
   (PageManager.handleEvent Dismiss -> customPage.onDismiss, customPage = null): the page stayed on screen but every click went
   nowhere (handleEvent Data with customPage == null -> AnchorActionModule only). Pages opened by typing the command worked.
   Now the command runs first with the menu still open; a page command simply replaces the menu (openCustomPage dismisses the old
   page server-side, no SetPage(None) is sent). Only if the menu is STILL the open page ~150 ms after the command finished
   (teleports, chat-only commands flagged close) is it closed - CloseTask, same world-thread pattern as RefreshTask.
 - Page scaled up 1.4x (Skyy: "scale it up a bigger"): 84 px slots with 62 px icons, bigger fonts, buttons and info box. The page is
   ~952 px tall (the tallest that fits a 1080-high UI with margin) and 800 px wide.
 - Info box moved ABOVE the icon grid (Skyy: a top-row tooltip went off the top of the screen; "lower the icons a little"). Tooltips
   open above the hovered icon; the grid now starts ~420 px below the top of a 1080-high screen instead of ~150.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.1.1.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.1.2.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
Q = chr(34)  # a double quote


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n >= 1, "anchor missing: " + old[:100]
    if count == 1:
        assert n == 1, "anchor not unique (%d): %s" % (n, old[:100])
        s = s.replace(old, new, 1)
    else:
        s = s.replace(old, new)


rep('VERSION = "0.1.1"', 'VERSION = "0.1.2"')
rep("0.1.1: menu commands switched to the short positional forms",
    "0.1.2: pages opened from the menu no longer hang on Loading... (the menu is not closed before a page command; CloseTask closes it" + LF +
    "       afterwards only if it is still open) and the page is 1.4x bigger. Notes: tools/menu_0_1_2_patch.py." + LF +
    "0.1.1: menu commands switched to the short positional forms")

# ---- 1.4x layout
rep("LabelStyle: (FontSize: 12, TextColor: #ffe9c9", "LabelStyle: (FontSize: 17, TextColor: #ffe9c9")
rep("LabelStyle: (FontSize: 12, TextColor: #ffffff", "LabelStyle: (FontSize: 17, TextColor: #ffffff", count=0)
rep("SLOT, COLS, ROWS = 60, 9, 6", "SLOT, COLS, ROWS = 84, 9, 6")
rep("PW = GW + 32" + LF + "PH = 680", "PW = GW + 44" + LF + "PH = 952")
rep("Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }" + Q + " % (PW, PH)",
    "Padding: (Horizontal: 22, Vertical: 14); LayoutMode: Top; }" + Q + " % (PW, PH)")
rep(Q + "ACCENT" + Q + ":   " + Q + "Group { Anchor: (Height: 2);", Q + "ACCENT" + Q + ":   " + Q + "Group { Anchor: (Height: 3);")
rep("Label #SkyyMTitle { Anchor: (Height: 26); Text: " + Q + Q + "; Style: (FontSize: 16,",
    "Label #SkyyMTitle { Anchor: (Height: 38); Text: " + Q + Q + "; Style: (FontSize: 23,")
rep("Label #SkyyMHint { Anchor: (Height: 16); Text: " + Q + Q + "; Style: (FontSize: 10,",
    "Label #SkyyMHint { Anchor: (Height: 22); Text: " + Q + Q + "; Style: (FontSize: 14,")
rep("Group #SkyyMGridWrap { Anchor: (Height: %d); }" + Q + " % (GH + 4)", "Group #SkyyMGridWrap { Anchor: (Height: %d); }" + Q + " % (GH + 6)")
rep("ItemGrid #SkyyMGrid { Anchor: (Horizontal: 0, Top: 2, Width: %d, Height: %d);", "ItemGrid #SkyyMGrid { Anchor: (Horizontal: 0, Top: 3, Width: %d, Height: %d);")
rep("SlotSize: %d, SlotIconSize: 44, SlotSpacing: 0", "SlotSize: %d, SlotIconSize: 62, SlotSpacing: 0")
rep(Q + "GAP" + Q + ":      " + Q + "Group { Anchor: (Height: 6); }" + Q, Q + "GAP" + Q + ":      " + Q + "Group { Anchor: (Height: 8); }" + Q)
rep("Group #SkyyMInfoBox { Anchor: (Height: 186); Background: #142030(0.9); Padding: (Horizontal: 10, Vertical: 6);",
    "Group #SkyyMInfoBox { Anchor: (Height: 266); Background: #142030(0.9); Padding: (Horizontal: 14, Vertical: 8);")
rep("Label #SkyyMInfoName { Anchor: (Height: 18); Text: " + Q + Q + "; Style: (FontSize: 13,",
    "Label #SkyyMInfoName { Anchor: (Height: 26); Text: " + Q + Q + "; Style: (FontSize: 18,")
rep("Label #SkyyMInfoDesc { Anchor: (Height: 30); Text: " + Q + Q + "; Style: (FontSize: 11,",
    "Label #SkyyMInfoDesc { Anchor: (Height: 42); Text: " + Q + Q + "; Style: (FontSize: 15,")
rep("Label #SkyyMStatus { Anchor: (Height: 20); Text: " + Q + Q + "; Style: (FontSize: 11,",
    "Label #SkyyMStatus { Anchor: (Height: 28); Text: " + Q + Q + "; Style: (FontSize: 15,")
rep("Group #SkyyMFoot { Anchor: (Height: 32); LayoutMode: Left; Padding: (Top: 2); }",
    "Group #SkyyMFoot { Anchor: (Height: 46); LayoutMode: Left; Padding: (Top: 3); }")
rep("Label { Anchor: (Width: 8, Height: 28); Text: " + Q + Q + "; }", "Label { Anchor: (Width: 11, Height: 40); Text: " + Q + Q + "; }")
rep("Label { Anchor: (Width: 20, Height: 28); Text: " + Q + Q + "; }", "Label { Anchor: (Width: 28, Height: 40); Text: " + Q + Q + "; }")
rep("TextButton #SkyyMBack { Anchor: (Width: 120, Height: 28);", "TextButton #SkyyMBack { Anchor: (Width: 168, Height: 40);")
rep("TextButton #SkyyMPrev { Anchor: (Width: 110, Height: 28);", "TextButton #SkyyMPrev { Anchor: (Width: 154, Height: 40);")
rep("TextButton #SkyyMNext { Anchor: (Width: 110, Height: 28);", "TextButton #SkyyMNext { Anchor: (Width: 154, Height: 40);")
rep("TextButton #SkyyMClose { Anchor: (Width: 120, Height: 28);", "TextButton #SkyyMClose { Anchor: (Width: 168, Height: 40);")
rep("Label #SkyyMInfo%d { Anchor: (Height: 14); Text: " + Q + Q + "; Style: (FontSize: 10,",
    "Label #SkyyMInfo%d { Anchor: (Height: 20); Text: " + Q + Q + "; Style: (FontSize: 14,")
rep("# label), about 520 px wide at FontSize 10.", "# label), about 730 px wide at FontSize 14 (0.1.2: everything 1.4x, so the same characters fit).")
# the page's parts must add up to no more than PH
rep('assert "Width" in UI["ROOT"]',
    "_tall = 2 * 14 + 3 + 38 + 22 + (GH + 6) + 8 + 266 + 28 + 46" + LF +
    "assert _tall <= PH, 'menu parts are %d px tall, page is %d' % (_tall, PH)" + LF +
    "assert 26 + 42 + 20 * INFO_LINES + 16 <= 266, 'info box too small for its lines'" + LF +
    'assert "Width" in UI["ROOT"]')

# ---- Skyy: the tooltip of a top-row icon went off the top of the screen ("lower the icons on the screen a little").
# Tooltips open ABOVE the hovered slot, so the info box moves above the grid: the icons sit ~270 px lower, the page height is unchanged.
rep(LF.join(['  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GRIDWRAP);',
             '  b.appendInline("#SkyyMGridWrap", @PKG@.MenuData.UI_GRID);',
             '  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GAP);',
             '  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_INFOBOX);',
             '  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFONAME);',
             '  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFODESC);',
             '  for (int i = 0; i < @PKG@.MenuData.UI_INFO.length; i++) b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFO[i]);']),
    LF.join(['  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_INFOBOX);',
             '  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFONAME);',
             '  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFODESC);',
             '  for (int i = 0; i < @PKG@.MenuData.UI_INFO.length; i++) b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFO[i]);',
             '  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GAP);',
             '  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GRIDWRAP);',
             '  b.appendInline("#SkyyMGridWrap", @PKG@.MenuData.UI_GRID);']))

# ---- FIX: never close the menu before a page command
rep('ref_ = pool.makeClass(PKG + ".RefreshTask")', 'ref_ = pool.makeClass(PKG + ".RefreshTask")' + LF + 'clo_ = pool.makeClass(PKG + ".CloseTask")')
rep("for c in (dat, utl, giv, page, ref_, fac, cmd, grt, rdy, seen, quit_, pl):",
    "for c in (dat, utl, giv, page, ref_, clo_, fac, cmd, grt, rdy, seen, quit_, pl):")
TQ = Q * 3
CLOSE_TASK = LF.join([
    "# ================= CloseTask (0.1.2): close the menu after a command ONLY if the menu is still the open page =================",
    "# (a page command replaces the menu by itself; closing first made the client's close answer dismiss the NEW page server-side)",
    'clo_.addInterface(pool.get("java.lang.Runnable"))',
    'clo_.addInterface(pool.get("java.util.function.BiConsumer"))',
    'F(clo_, "public @PKG@.MenuPage page;")',
    'F(clo_, "public @PR@ pr;")',
    'F(clo_, "public @WLD@ expected;")',
    "C(clo_, r" + TQ,
    "public CloseTask(@PKG@.MenuPage page, @PR@ pr) { this.page = page; this.pr = pr; this.expected = null; }" + TQ + ")",
    "M(clo_, r" + TQ,
    "public void accept(Object result, Object error) {",
    "  try { @HSV@.SCHEDULED_EXECUTOR.schedule(this, 150L, java.util.concurrent.TimeUnit.MILLISECONDS); }",
    '  catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule the menu close: " + t); }',
    "}" + TQ + ")",
    "M(clo_, r" + TQ,
    "public void run() {",
    "  try {",
    "    if (this.pr == null || !this.pr.isValid()) return;",
    "    if (this.expected == null) {",
    "      java.util.UUID wu = this.pr.getWorldUuid();",
    "      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);",
    "      if (w == null) return;",
    "      this.expected = w;",
    "      w.execute(this);",
    "      return;",
    "    }",
    "    java.util.UUID wu2 = this.pr.getWorldUuid();",
    "    if (wu2 == null || @UNI@.get().getWorld(wu2) != this.expected) return;",
    "    @REF@ r = this.pr.getReference();",
    "    if (r == null || !r.isValid()) return;",
    "    @ST@ st = r.getStore();",
    "    if (st == null) return;",
    "    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());",
    "    if (p == null || p.getPageManager().getCustomPage() != this.page) return;",
    "    this.page.closePage(r, st);",
    '  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu close failed: " + t); }',
    "}" + TQ + ")",
    "",
])
anchor = "# run a command AS THIS PLAYER (vanilla /su pattern)"
rep(anchor, CLOSE_TASK + anchor)
rep(LF.join(["  if (close) closePage(ref, st);",
             "  @CMGR@.get().handleCommand(this.playerRef, line);",
             "  if (!close) {"]),
    LF.join(["  java.util.concurrent.CompletableFuture fut = @CMGR@.get().handleCommand(this.playerRef, line);",
             "  if (close) {",
             "    @PKG@.CloseTask ct = new @PKG@.CloseTask(this, this.playerRef);",
             "    if (fut != null) fut.whenComplete(ct); else ct.accept(null, null);",
             "  }",
             "  if (!close) {"]))

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
