"""Derive SkyyMenu/build_skyymenu_0.3.21.py from the LIVE SkyyMenu 0.3.20 (python tools/menu_0_3_21_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_20_patch.py -> 0.3.20 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch, never re-build it) -> this patch -> 0.3.21. The harness SkyyMenu/test_skyymenu_0.3.21.py is its own
file.

0.3.21 = THE MESSAGES TAB (Skyy 2026-10-12, docs/answered/ui.md CHAT OVERFLOW: "figure out ways to reduce the chat overflow while still
giving players the info they need"). SkyyHud 0.3.20+ registers two player switches per message kind through settings:fn:register (11 kinds
in 0.3.22 = 22 rows: msg.<kind> "shown or not" + msg.<kind>.feed "feed or chat"), with the category "messages". SkyyMenu 0.3.20 has no
such tab, so SetReg.catIndex sent every one of them to the LAST tab, General (12 rows -> 34 = 5 pages).
 A. A NINTH TAB "Messages" (category id "messages", before General, which stays last and keeps catching unknown ids). SkyyHud's
    registration already names "messages", so no SkyyHud change and no new bridge argument: the register call is unchanged (backward
    compatible both ways - an older SkyyMenu still files them under General). General is back to its 0.3.19 length.
 B. ROW ORDER inside the tab: SkyyHud's kinds in its own order, each "shown" switch followed by its "feed" switch (MenuData.SET_ORDER_MSG,
    ranked after SET_ORDER; 0.3.20 had no rank for them = alphabetical). The 22 rows are 3 pages of 8. The build checks the list against
    SkyyHud/build_skyyhud_0.3.22.py's MSG_KINDS when that script exists. These keys are NOT added to SET_KNOWN (their defaults follow
    SkyyHud's Server Setup -> Messages rows, not the true / false template of settings-defaults.properties).
 C. THE TAB STRIP STILL FITS: 0.3.20 draws 4 tab buttons of 252 px per row in two rows (1044 of the page's 1080 px). With 9 visible tabs
    the page draws 5 per row at 206 px (5 x 206 + 4 x 12 = 1078 px; the longest name "Collections" is checked to fit); with 8 or fewer
    visible tabs it is 0.3.20's strip exactly (same buttons, same 4 per row). Same two rows, same page height (930), same button styles as
    the other settings buttons (this page keeps its 0.2 look, like 0.3.20; tools/skyyui.py is used by the Stats page only).
No saved-data change, no new key, no command. ROUND_PINS = {} (deploys on its own; SkyyHud 0.3.22 is already the SET pin).
"""
import os
import re
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.20.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.21.py")
HUD = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.22.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
OLD = s
assert 'VERSION = "0.3.20"' in s and "0.3.20: THE PROFILE NAME FOLLOW-UP" in s and "SET_ORDER_MSG" not in s, "not the generated 0.3.20 script"
CHANGES = []            # (new text, old text) of every change, in order: undone at the end


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyMenu") != "0.3.20":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.20" % _set.get("SkyyMenu"))

# SkyyHud 0.3.22's message kinds, in its order (MSG_KINDS of SkyyHud/build_skyyhud_0.3.22.py)
MSG_KINDS = ["pickup", "drop", "skillxp", "levelup", "coins", "collection", "rankup", "quest", "heal", "petxp", "ability"]
if os.path.isfile(HUD):
    _h = open(HUD, encoding="utf-8", errors="ignore").read()
    _blk = _h[_h.index("MSG_KINDS = ["):]
    _blk = _blk[:_blk.index("\n]")]
    _hk = re.findall(r"^\s*\('([a-z]+)', 'R_", _blk, re.M)
    assert _hk == MSG_KINDS, "0.3.21: SkyyHud 0.3.22's MSG_KINDS changed: %s" % _hk
    assert '"messages", Boolean.valueOf(!"off".equals(d))' in _h and '"messages", Boolean.valueOf("feed".equals(d))' in _h, \
        "0.3.21: SkyyHud 0.3.22 registers its rows with the category messages"

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.20: THE PROFILE NAME FOLLOW-UP''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.21: THE MESSAGES TAB (notes: tools/menu_0_3_21_patch.py; Skyy 2026-10-12 CHAT OVERFLOW): a ninth /settings tab "Messages" (category
       messages, before General) for SkyyHud's 22 Chat / Feed / Off switches (msg.<kind> + msg.<kind>.feed), in SkyyHud's kind order
       (SET_ORDER_MSG); General is back to its own rows. With 9 visible tabs the strip draws 5 per row at 206 px (else 0.3.20's 4 x 252).
       No saved-data change. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.21.py.
0.3.20: THE PROFILE NAME FOLLOW-UP''')
rep('VERSION = "0.3.20"\n', 'VERSION = "0.3.21"\n')

# ================================================================================================ A: the Messages tab
rep('''    ("cooking",     "Cooking",     "Cooking & Trees",    "Everything on this tab can be switched off."),
    ("general",''', '''    ("cooking",     "Cooking",     "Cooking & Trees",    "Everything on this tab can be switched off."),
    # 0.3.21: SkyyHud's message routes (category "messages", registered by SkyyHud 0.3.20+; SET_ORDER_MSG gives their order)
    ("messages",    "Messages",    "Messages (chat, feed or off)",
     "Each message type: the first switch shows or hides it, the second puts it in the feed above chat. Errors stay in chat."),
    ("general",''')
rep('''assert len(SET_TABS) == 8 and len(set(SET_CAT_ID)) == 8 and SET_CAT_ID[-1] == "general", "8 tabs, general last (unknown ids go there)"''',
    '''assert len(SET_TABS) == 9 and len(set(SET_CAT_ID)) == 9 and SET_CAT_ID[-1] == "general", "9 tabs, general last (unknown ids go there)"
assert SET_CAT_ID[-2] == "messages", "0.3.21: Messages right before General"''')

# ================================================================================================ B: the row order of the Messages tab
rep('''SET_TAB_ROWS = [(t[0], len([k for k in SET_KNOWN if k[1] == t[0]])) for t in SET_TABS]''',
    '''# 0.3.21: SkyyHud's message-route switches, ranked after SET_ORDER (SetReg.rank): per kind the "shown" switch, then its "feed" switch
MSG_KINDS = %r
SET_ORDER_MSG = [k for _mk in MSG_KINDS for k in ("msg." + _mk, "msg." + _mk + ".feed")]
assert len(SET_ORDER_MSG) == 22 and not (set(SET_ORDER_MSG) & set(SET_ORDER)) and all(KEY_RE.match(_k) for _k in SET_ORDER_MSG)
assert not [k for k in SET_KNOWN if k[1] == "messages"], "0.3.21: SkyyHud's rows are not SET_KNOWN entries"
SET_TAB_ROWS = [(t[0], len([k for k in SET_KNOWN if k[1] == t[0]]) + (len(SET_ORDER_MSG) if t[0] == "messages" else 0)) for t in SET_TABS]''' % MSG_KINDS)
rep('''F(dat, "public static final String[] SET_ORDER = %s;" % jarr(SET_ORDER))''',
    '''F(dat, "public static final String[] SET_ORDER = %s;" % jarr(SET_ORDER))
F(dat, "public static final String[] SET_ORDER_MSG = %s;" % jarr(SET_ORDER_MSG))      # 0.3.21''')
rep('''  for (int i = 0; i < @PKG@.MenuData.SET_ORDER.length; i++) if (@PKG@.MenuData.SET_ORDER[i].equals(key)) return i;
  return 9000;''', '''  for (int i = 0; i < @PKG@.MenuData.SET_ORDER.length; i++) if (@PKG@.MenuData.SET_ORDER[i].equals(key)) return i;
  for (int j = 0; j < @PKG@.MenuData.SET_ORDER_MSG.length; j++) if (@PKG@.MenuData.SET_ORDER_MSG[j].equals(key)) return @PKG@.MenuData.SET_ORDER.length + j;
  return 9000;''')

# ================================================================================================ C: the tab strip (5 per row when 9 show)
STABN_W = 206
rep('''    "SROW":    ["Group #SkyyStgRow%d { Anchor: (Height: 61); Background: #142030(0.92); LayoutMode: Left; Padding: (Top: 4); }" % r for r in range(SET_ROWS)],''',
    '''    # 0.3.21: the same tab buttons %d px wide - 5 per row when more than 8 tabs show (5 x %d + 4 x 12 <= the page's 1080 px inside)
    "STABN":    ['TextButton #SkyyStgTab%%d { Anchor: (Width: %d, Height: 48); Text: "%%s"; ' %% (i, t[1]) + SBS + " }" for i, t in enumerate(SET_TABS)],
    "STABSELN": ['TextButton #SkyyStgTab%%d { Anchor: (Width: %d, Height: 48); Text: "%%s"; ' %% (i, t[1]) + TAB_SEL + " }" for i, t in enumerate(SET_TABS)],
    "SROW":    ["Group #SkyyStgRow%%d { Anchor: (Height: 61); Background: #142030(0.92); LayoutMode: Left; Padding: (Top: 4); }" %% r for r in range(SET_ROWS)],''' % (STABN_W, STABN_W, STABN_W, STABN_W))
rep('''SET_UI_ALL = list(UI_S.values()) + [x for v in UI_SARR.values() for x in v]''',
    '''SET_UI_ALL = list(UI_S.values()) + [x for v in UI_SARR.values() for x in v]
# 0.3.21: the strip fits - 4 x 252 + 3 x 12 (0.3.20) and 5 x %d + 4 x 12 inside the 1120 - 2 x 20 px page; every tab name fits its button
assert 4 * 252 + 3 * 12 <= SPW - 40 and 5 * %d + 4 * 12 <= SPW - 40, "0.3.21: the tab strip is wider than the Settings page"
assert len(SET_TABS) <= 10, "0.3.21: two rows of 5 tab buttons at most"
for _t in SET_TABS:
    assert SUI.text_width(_t[1], 18, bold=True) + 16 <= %d, "0.3.21: the tab name %%s does not fit a %d px button" %% _t[1]''' % (STABN_W, STABN_W, STABN_W, STABN_W))
rep('''  int shown = 0;
  for (int i = 0; i < nCat; i++) {
    if (((String[]) vis[i]).length == 0) continue;
    String par = shown < 4 ? "#SkyyStgTabs0" : "#SkyyStgTabs1";
    if (shown % 4 != 0) b.appendInline(par, @PKG@.MenuData.UI_SSP12);
    b.appendInline(par, i == this.cat ? @PKG@.MenuData.UI_STABSEL[i] : @PKG@.MenuData.UI_STAB[i]);''', '''  int tabsN = 0;
  for (int i = 0; i < nCat; i++) if (((String[]) vis[i]).length > 0) tabsN++;
  boolean narrow = tabsN > 8;
  int perRow = narrow ? 5 : 4;
  int shown = 0;
  for (int i = 0; i < nCat; i++) {
    if (((String[]) vis[i]).length == 0) continue;
    String par = shown < perRow ? "#SkyyStgTabs0" : "#SkyyStgTabs1";
    if (shown % perRow != 0) b.appendInline(par, @PKG@.MenuData.UI_SSP12);
    if (narrow) b.appendInline(par, i == this.cat ? @PKG@.MenuData.UI_STABSELN[i] : @PKG@.MenuData.UI_STABN[i]);
    else b.appendInline(par, i == this.cat ? @PKG@.MenuData.UI_STABSEL[i] : @PKG@.MenuData.UI_STAB[i]);''')

# ================================================================================================ checks on the result
assert s.count("UI_STABSELN[i]") == 1 and s.count("MenuData.SET_ORDER_MSG") == 2 and s.count('("messages",') == 1, "0.3.21: the changes"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.20 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.20 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
