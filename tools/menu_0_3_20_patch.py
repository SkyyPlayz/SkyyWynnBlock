"""Derive SkyyMenu/build_skyymenu_0.3.20.py from the LIVE SkyyMenu 0.3.19 (python tools/menu_0_3_20_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_19_patch.py -> 0.3.19 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch, never re-build it) -> this patch -> 0.3.20. The harness SkyyMenu/test_skyymenu_0.3.20.py is its own
file.

0.3.20 = THE PROFILE NAME FOLLOW-UP (Skyy 2026-10-13: "have the name show (Class) (profile name."). SkyyProfiles 0.1.12 made bridge
profile:name:<uuid> the display text "<Class> <name>" (up to 10 + 1 + 16 = 27 characters: "Spellblade" + a 16-letter name) and added
profile:pname:<uuid> = the bare name (tools/PROFILES-CONTRACT.md):
 A. THE PETS TILE (PetTile.body): 0.3.19 cut the profile name at 24 characters, so "Spellblade <16 letters>" lost its end. Now the whole
    27 characters are shown; a longer text (never from SkyyProfiles today) is cut to 24 + "..." = 27. The line "Your pets on this
    profile (<27>). Click to see them all." is exactly StatsCalc.LINE_MAX (79) characters, and it is the tile's FIRST line, which the
    menu's info box wraps (#SkyyMInfoDesc) - nothing overflows.
 B. THE STATS PAGE (StatsCalc.profileName: the Profile tab's "Profile" row + the page header "<player> - <Class> - profile <name>"):
    both already show the class next to the name, and the Profile row's value column is 192 px (18 px bold: "Spellblade
    Abcdefghijklmnop" is ~254 px = overflow). profileName now reads profile:pname (the bare name) and falls back to profile:name (an
    older SkyyProfiles, where profile:name IS the bare name) - so the page shows "Priest" + "Banana", never "Priest ... Priest Banana".
No saved-data change. ROUND_PINS = {}.
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.19.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.20.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
OLD = s
assert 'VERSION = "0.3.19"' in s and "0.3.19: LAG FIXES + THE HUB HOTKEY" in s and "profile:pname:" not in s, "not the generated 0.3.19 script"
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
if _set is not None and _set.get("SkyyMenu") != "0.3.19":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.19" % _set.get("SkyyMenu"))

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.19: LAG FIXES + THE HUB HOTKEY''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.20: THE PROFILE NAME FOLLOW-UP (notes: tools/menu_0_3_20_patch.py; Skyy 2026-10-13 "have the name show (Class) (profile name."; for
       SkyyProfiles 0.1.12's profile:name = "<Class> <name>" + profile:pname = the bare name): the Pets tile shows the whole "<Class>
       <name>" (cut at 27 instead of 24; longer = 24 + "..."); the Stats page's Profile row + header show the bare name (profile:pname,
       else profile:name) next to the class. No saved-data change. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.20.py.
0.3.19: LAG FIXES + THE HUB HOTKEY''')
rep('VERSION = "0.3.19"\n', 'VERSION = "0.3.20"\n')

# ================================================================================================ A: the Pets tile
PN_MAX = 27         # "Spellblade" (the longest class, 10) + " " + a 16-letter profile name (SkyyProfiles NAME_MAX)
rep('''  if (pn.length() > 24) pn = pn.substring(0, 24).trim();
  StringBuilder sb = new StringBuilder();
  sb.append(@PKG@.MenuUtil.clip("Your pets on this profile"''', '''  if (pn.length() > %d) pn = pn.substring(0, %d).trim() + "...";
  StringBuilder sb = new StringBuilder();
  sb.append(@PKG@.MenuUtil.clip("Your pets on this profile"''' % (PN_MAX, PN_MAX - 3))
_line = "Your pets on this profile (" + "W" * PN_MAX + "). Click to see them all."
_lm = int(s[s.index("ST_LINE_MAX = ") + len("ST_LINE_MAX = "):].split()[0])
assert len(_line) <= _lm, "0.3.20 A: the pets line with a %d-character name is %d > LINE_MAX %d" % (PN_MAX, len(_line), _lm)

# ================================================================================================ B: the Stats page's bare name
rep('''public static String profileName(java.util.UUID u) { return text("profile:name:" + u.toString()); }''',
    '''public static String profileName(java.util.UUID u) {
  String p = text("profile:pname:" + u.toString());
  return p != null ? p : text("profile:name:" + u.toString());
}''')

# ================================================================================================ checks on the result
assert s.count("pn.substring(0, 24).trim();") == 0 and s.count('text("profile:pname:"') == 1, "0.3.20: the two changes"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.19 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.19 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
