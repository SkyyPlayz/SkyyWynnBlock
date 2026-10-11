"""Derive SkyyMenu/build_skyymenu_0.3.17.py from the LIVE SkyyMenu 0.3.16 (python tools/menu_0_3_17_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_16_patch.py -> 0.3.16 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch, never re-build it) -> this patch -> 0.3.17. 0.3.16's files stay untouched. The harness
SkyyMenu/test_skyymenu_0.3.17.py is its own file (derived from test_skyymenu_0.3.16.py: it runs the 0.3.16 harness on the new jar next to
a control run = every old check carried forward, plus the new sections).

0.3.17 = THE MENU LAYOUT EDITOR. Skyy's own words (2026-10-10, docs/answered/ui.md):
  "another idea, can you make a menu editor that allows users to rearrange the menu? or is that too much work?"
  "make sure the flavor text of the edit button explains that it doesn't support dragging."
  1. An "Edit layout" tile on the main view, bottom-right slot 53 (row 5 = the control row; Close stays at 49). Its hover text says
     plainly that dragging does NOT work: click a tile, then click the slot you want it in, and the two swap; Reset puts everything back.
  2. EDIT MODE (main view only): the title, the hint line and the info box say "editing - no dragging"; every slot of rows 0 - 4 is
     clickable: the first click picks a tile up (its name gets "[Moving] ", the info box + status say what to do next), the second click
     on any slot (a tile or an empty slot) swaps them; clicking the picked-up tile again cancels. Empty slots show a glass marker
     ("Empty slot"); the slot of a tile this player cannot see (permission / unlock / mod missing) is NOT drawn (no marker, nothing
     named - restricted tiles stay fully hidden), not clickable and never a target - hidden tiles keep their saved slot. Row 5: Reset to
     default 45 (click twice), admins only: Save as server default 46 (click twice), Server default: standard 47 (click twice = back to
     layout D); Close 49 (unchanged); Done 52 (leaves edit mode; 53 stays empty so a double-click on Edit layout does not leave at once).
     Tiles do not run their action while editing. Teleport has no special lock. Hover Tooltips OFF: the first click on Edit layout shows
     its no-dragging text in the info box and asks again (the modcfg pattern), the second click starts editing.
  3. SAVED PER PLAYER (account UUID = PlayerRef.getUuid(), every profile shares it) in SkyyMenu's own data folder:
     Skyy_SkyyMenu/layouts/<uuid>.properties (_v=1, _name, <tile key>=<slot>), written off the world thread (300 ms LayoutSaveTask on the
     server scheduler, MenuUtil.atomicWrite: tmp + fsync + atomic rename), every move saved right away; Reset deletes the file. The
     server default: Skyy_SkyyMenu/layout-default.properties (same format; read at start; no file = the built-in layout D).
     Which layout a player gets: their own file, else the server default, else layout D. Resolving: a tile key unknown to this version
     is ignored; a saved slot outside 0 - 44 or already taken is dropped; a tile missing from the save (NEW tiles of later updates) goes
     to the first free slot (lowest index). A file without a usable layout (no _v=1, no usable tile line) = the default layout + ONE
     warning per file per session; it is not overwritten until that layout is changed in game, and then the old file is kept as
     <name>.bad (<name>.bad-<millis> if a .bad is already there). A READ ERROR (IO / a lock / a folder) = the default layout drawn + one
     warning, re-read after 30 s, editing refused meanwhile, the file never renamed. Players' files are preloaded off the world thread at
     PlayerReady (MenuLayout.preload -> LayoutSaveTask in load mode); the inline read on a first draw is only the fallback (as SetStore).
  4. Sub-views (Teleport, Players, Player, Mods) unchanged.
No migration (new files only), no command change, no other mod; ROUND_PINS = {}.
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.16 outside them, byte for byte.
"""
import os
import re
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.16.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.17.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
OLD = s
assert 'VERSION = "0.3.16"' in s and "0.3.16: LAYOUT D + OWN TILE ICONS" in s and "MenuLayout" not in s, "not the generated 0.3.16 script"
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
if _set is not None and _set.get("SkyyMenu") != "0.3.16":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.16" % _set.get("SkyyMenu"))

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.16: LAYOUT D''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.17: THE MENU LAYOUT EDITOR (notes: tools/menu_0_3_17_patch.py; Skyy 2026-10-10 "can you make a menu editor that allows users to
       rearrange the menu?", "make sure the flavor text of the edit button explains that it doesn't support dragging."): an Edit layout
       tile (main slot 53) - no dragging: click a tile, click its new slot, they swap; click it again = cancel; Reset to default; admins:
       Save as server default / back to layout D; Done. Saved per player (account uuid) in Skyy_SkyyMenu/layouts/<uuid>.properties, the
       server default in Skyy_SkyyMenu/layout-default.properties (MenuLayout + LayoutSaveTask). Hidden tiles keep their slot, unknown tile
       keys are ignored, new tiles go to the first free slot, an unreadable file = the default + one warning. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.17.py (every 0.3.16 check carried forward + CC 0.3.16 -> 0.3.17 + E the editor executed
  through the engine's PageManager: swap, cancel, reset, per-player files, server default, kept slots, unknown / new tiles, corrupt
  files, two starts on a copy of the live data + AA the engine-access audit).
0.3.16: LAYOUT D''')
rep('VERSION = "0.3.16"\n', 'VERSION = "0.3.17"\n')

# ================================================================================================ the editor's data (texts + icons)
EDIT_DATA = '''# 0.3.17: THE MENU LAYOUT EDITOR (Skyy 2026-10-10: "can you make a menu editor that allows users to rearrange the menu?" + "make sure the
# flavor text of the edit button explains that it doesn't support dragging."). The grid is click-only (AreItemsDraggable: false), so
# every text says it: click a tile, then click the slot you want it in - they swap. Main view only; rows 0 - 4 (slots 0 - 44) are the
# layout, row 5 holds the controls (Close stays at 49). Tile keys (E_KEY) = the tile name, lower case, letters / digits only - the saved
# files use them (Skyy_SkyyMenu/layouts/<uuid>.properties, Skyy_SkyyMenu/layout-default.properties).
LAY_GRID = 45                                 # slots 0 - 44 can hold a tile
EDIT_SLOT = 53                                # the Edit layout tile (bottom right); in edit mode 53 stays EMPTY (fix round: a
#                                               double-click on Edit layout must not land on Done), Done sits at 52
EDIT_CTRL = {"reset": 45, "srvsave": 46, "srvclear": 47, "done": 52}
EDIT_ICONS = {"EDIT": "Tool_Hammer_Iron", "DONE": "Tool_Hammer_Iron", "RESET": "Deco_Lever", "SRVSAVE": "Furniture_Human_Ruins_Banner",
              "SRVCLEAR": "Deco_Map", "EMPTY": "Editor_Empty"}
EDIT_TXT = {
    "EDIT_NAME": "Edit layout",
    "EDIT_BODY": "\\n".join(["Move the tiles of this menu around - your layout is saved for you.",
                             "Dragging does NOT work in this menu.",
                             "Instead: click a tile, then click the slot you want it in - the two swap.",
                             "Click a picked-up tile again to cancel.",
                             "Reset puts everything back the way it was."]),
    "EDIT_FOOT": "Click to edit the layout - no dragging, just click and click",
    "EDIT_TITLE": "Edit layout - SkyWynn Menu",
    "EDIT_HINT": "EDITING - no dragging: click a tile, then the slot you want it in (they swap). Done to finish.",
    "EDIT_INFO_NAME": "Editing your layout",
    "EDIT_INFO": "\\n".join(["No dragging here: click a tile, then click the slot you want it in. They swap.",
                             "Empty slots work too - the tile just moves there.",
                             "Click the picked-up tile again to cancel the move.",
                             "Every move is saved right away, for every profile of your account.",
                             "Reset to default (bottom left) puts every tile back.",
                             "Done (bottom row, right) goes back to the normal menu."]),
    "EDIT_INFO_ADMIN": "Admins: Save as server default gives YOUR layout to every player without one.",
    "EDIT_MOVING": "\\n".join(["Now click the slot where it should go - a tile there swaps places with it.",
                               "Empty slots work too.",
                               "Click it again to cancel. No dragging - just click, then click."]),
    "EDIT_TILE_BODY": "\\n".join(["Click to pick this tile up, then click the slot where it should go.",
                                  "No dragging - click, then click. The two tiles swap."]),
    "EDIT_PICK_FOOT": "Click to pick it up",
    "EDIT_SWAP_FOOT": "Click to swap it with the picked-up tile",
    "EDIT_SEL_BODY": "\\n".join(["Picked up - now click the slot where it should go.", "Click this tile again to cancel."]),
    "EDIT_SEL_FOOT": "Click again to cancel",
    "EMPTY_NAME": "Empty slot",
    "EMPTY_BODY": "\\n".join(["A free slot.", "Pick a tile up first, then click here to move it here."]),
    "EMPTY_FOOT_PICK": "Pick a tile up first",
    "EMPTY_FOOT_MOVE": "Click to move the picked-up tile here",
    # fix round: a hidden tile's slot is NOT marked in edit mode (no "Kept slot" - restricted tiles stay fully hidden, the 2026-09-25 rule);
    # it is simply not clickable. KEPT_MSG only answers a stale / forged click on it and names nothing.
    "KEPT_MSG": "That slot cannot be used - pick a tile or a slot with a glass marker.",
    # fix round: Hover Tooltips OFF = no hover text, so the first click on Edit layout shows EDIT_BODY in the info box and asks again
    "EDIT_ARM": "Click Edit layout again to start editing - no dragging, just click and click.",
    "EDIT_WAIT": "Your saved layout cannot be read right now - nothing changed. Try again soon.",
    "DONE_NAME": "Done",
    "DONE_BODY": "\\n".join(["Leave edit mode - your layout is already saved.", "The tiles work normally again."]),
    "DONE_FOOT": "Click to finish",
    "RESET_NAME": "Reset to default",
    "RESET_BODY": "\\n".join(["Put every tile back where it started.", "You get the server's default layout again."]),
    "RESET_FOOT": "Click twice to reset",
    "SRVSAVE_NAME": "Save as server default",
    "SRVSAVE_BODY": "\\n".join(["Admins: make YOUR current layout the default", "for every player who has not made their own.",
                                "Players with their own layout keep it."]),
    "SRVSAVE_FOOT": "Click twice to save it for everyone",
    "SRVCLEAR_NAME": "Server default: standard",
    "SRVCLEAR_BODY": "\\n".join(["Admins: make the built-in layout (layout D) the default again",
                                 "for every player who has not made their own."]),
    "SRVCLEAR_FOOT": "Click twice to go back to the standard layout",
}
for _k, _v in EDIT_TXT.items():
    for _ln in _v.split("\\n"):
        assert txt(_ln) == _ln and len(_ln) <= (96 if _k == "EDIT_HINT" else 80), "0.3.17: editor text %s line too long / not safe: %s" % (_k, _ln)
for _ic in EDIT_ICONS.values():
    need_item(_ic)
    need_icon(_ic)
_eb = EDIT_TXT["EDIT_BODY"].lower()
assert "dragging does not work" in _eb and "click a tile, then click the slot" in _eb and "swap" in _eb and "reset" in _eb, \\
    "0.3.17 (Skyy LOCKED 2026-10-10): the Edit layout text says plainly that dragging does not work, click + click swaps, Reset"
assert "no dragging" in EDIT_TXT["EDIT_FOOT"] and "no dragging" in EDIT_TXT["EDIT_HINT"].lower() and "No dragging" in EDIT_TXT["EDIT_INFO"] \\
    and "no dragging" in EDIT_TXT["EDIT_ARM"]
assert sorted(EDIT_CTRL.values()) == [45, 46, 47, 52] and 49 not in EDIT_CTRL.values() and EDIT_SLOT not in EDIT_CTRL.values(), \\
    "0.3.17: Close stays at 49; Done is not on the Edit layout slot (a double-click must not leave edit mode)"
_ekey = lambda n: re.sub(r"[^a-z0-9]", "", n.lower())
E_KEY = [_ekey(e[3]) if e[0] == "main" else "" for e in ENTRIES]
_mk = [k for k in E_KEY if k]
assert len(_mk) == len(set(_mk)) == len([e for e in ENTRIES if e[0] == "main"]) and all(re.match(r"^[a-z][a-z0-9]{2,31}$", k) for k in _mk), \\
    "0.3.17: every main tile has a unique saved-file key: %s" % _mk
assert all(e[1] < LAY_GRID for e in ENTRIES if e[0] == "main") and not [e for e in ENTRIES if e[0] == "main" and e[1] in EDIT_CTRL.values()], \\
    "0.3.17: the layout lives in rows 0 - 4, row 5 is the control row"
print("0.3.17 layout editor: tile keys", ", ".join(_mk), "- controls", EDIT_CTRL, "- icons", EDIT_ICONS)
'''
rep('''E_VIEW = [e[0] for e in ENTRIES]; E_SLOT = [e[1] for e in ENTRIES]; E_ICON = [e[2] for e in ENTRIES]
''', '''E_VIEW = [e[0] for e in ENTRIES]; E_SLOT = [e[1] for e in ENTRIES]; E_ICON = [e[2] for e in ENTRIES]
''' + EDIT_DATA)

# ================================================================================================ MenuData: the editor's arrays / texts
rep('''F(dat, "public static final java.util.concurrent.ConcurrentHashMap TILE_WARNED = new java.util.concurrent.ConcurrentHashMap();")
''', '''F(dat, "public static final java.util.concurrent.ConcurrentHashMap TILE_WARNED = new java.util.concurrent.ConcurrentHashMap();")
# 0.3.17: the layout editor - tile keys of the saved files ("" = not a main tile), the grid size, the control slots, icons, texts
F(dat, "public static final String[] E_KEY = %s;" % jarr(E_KEY))
F(dat, "public static final int LAY_GRID = %d;" % LAY_GRID)
F(dat, "public static final int EDIT_SLOT = %d;" % EDIT_SLOT)
for _k, _v in sorted(EDIT_CTRL.items()):
    F(dat, "public static final int CTRL_%s = %d;" % (_k.upper(), _v))
for _k, _v in sorted(EDIT_ICONS.items()):
    F(dat, "public static final String ICON_%s = %s;" % (_k, jstr(_v)))
for _k, _v in sorted(EDIT_TXT.items()):
    F(dat, "public static final String %s = %s;" % (_k, jstr(_v)))
''')

# ================================================================================================ the classes
rep('''pet  = mk("PetTile")        # 0.3.14: the Pets tile's name / text / icon from the active profile's SkyyPets record (read only)
''', '''pet  = mk("PetTile")        # 0.3.14: the Pets tile's name / text / icon from the active profile's SkyyPets record (read only)
lay  = mk("MenuLayout")     # 0.3.17: the per-player menu layouts + the server default (files, cache, resolving)
lsv  = mk("LayoutSaveTask") # 0.3.17: the 300 ms delayed layout save on the server scheduler (never on the world thread)
''')
rep('''         scl, stp, sta, stc, pet, pl)
''', '''         scl, stp, sta, stc, pet, lay, lsv, pl)
''')

# ================================================================================================ MenuLayout + LayoutSaveTask
LAYOUT_JAVA = r'''# ================= 0.3.17 MenuLayout: who gets which main-view layout (Skyy 2026-10-10, the menu layout editor) =================
# A layout = int[E_VIEW.length]: the slot (0 - 44) of every main tile, -1 for the other entries. OWN: uuid text -> the player's own
# layout (int[], never changed after it is published - copy-on-write) or NONE (no own layout / file unreadable). DEF = the server default
# (null = the built-in layout D = E_SLOT). Files: DIR/<uuid>.properties and DEF_FILE, written by saveNow (synchronized, off the world
# thread via LayoutSaveTask; atomicWrite); an unreadable file is warned once per file (WARNED) and kept as <name>.bad before the first
# write over it (BROKEN / DEF_BROKEN). DIRTY = keys whose write is pending or failed (retried by SeenTick every 30 s and at shutdown).
# Fix round: only a file that READS but holds no layout is BROKEN (renamed to .bad on the next change). A READ ERROR (IO, a lock held by
# an antivirus / backup tool, a folder in its place) is ERR: never cached as "no layout", never renamed; the default is drawn, editing is
# refused until it reads (ERRAT = uuid -> the time of the failed read; re-read after 30 s). The file is preloaded off the world thread at
# PlayerReady (preload -> LayoutSaveTask in load mode), like the settings' SetLoadTask; the inline read in own() is only the fallback.
F(lay, "public static volatile java.nio.file.Path DIR;")
F(lay, "public static volatile java.nio.file.Path DEF_FILE;")
F(lay, 'public static final String NONE = "none";')
F(lay, 'public static final String BAD = "bad";')
F(lay, 'public static final String ERR = "err";')
F(lay, 'public static final String DEF_KEY = "_default";')
F(lay, "public static volatile int[] DEF;")
F(lay, "public static volatile boolean DEF_BROKEN;")
F(lay, "public static volatile long READS;")
F(lay, "public static volatile long WRITES;")
F(lay, "public static volatile int WARNS;")
for _f in ("OWN", "NAMES", "DIRTY", "WARNED", "BROKEN", "ERRAT"):
    F(lay, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
M(lay, r"""
public static boolean isMain(int i) {
  return i >= 0 && i < @PKG@.MenuData.E_VIEW.length && "main".equals(@PKG@.MenuData.E_VIEW[i]);
}""")
M(lay, r"""
public static int[] builtin() {
  int n = @PKG@.MenuData.E_VIEW.length;
  int[] out = new int[n];
  for (int i = 0; i < n; i++) out[i] = isMain(i) ? @PKG@.MenuData.E_SLOT[i] : -1;
  return out;
}""")
M(lay, r"""
public static void warnOnce(String what, String msg) {
  if (WARNED.putIfAbsent(what, Boolean.TRUE) != null) return;
  WARNS = WARNS + 1;
  @PKG@.MenuUtil.warn(msg);
}""")
# tile=slot lines of a properties file -> a raw layout (-1 = not in the file); null = not a layout (no _v=1 or no usable tile line).
# Unknown keys (a tile of another version) and slots outside 0 - 44 are skipped.
M(lay, r"""
public static int[] parse(java.util.Properties p) {
  if (p == null || !"1".equals(p.getProperty("_v", "").trim())) return null;
  int n = @PKG@.MenuData.E_VIEW.length;
  int[] out = new int[n];
  int got = 0;
  for (int i = 0; i < n; i++) {
    out[i] = -1;
    if (!isMain(i)) continue;
    String v = p.getProperty(@PKG@.MenuData.E_KEY[i]);
    if (v == null) continue;
    int sl = -1;
    try { sl = Integer.parseInt(v.trim()); } catch (Throwable t) { sl = -1; }
    if (sl >= 0 && sl < @PKG@.MenuData.LAY_GRID) { out[i] = sl; got = got + 1; }
  }
  if (got == 0) return null;
  return out;
}""")
# null = no file; int[] = a layout; BAD = the file reads but holds no layout; ERR = a read error (both warned once per file)
M(lay, r"""
public static Object readFile(java.nio.file.Path f, String what) {
  if (f == null) return null;
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    READS = READS + 1L;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(new java.io.InputStreamReader(in, "UTF-8")); } finally { in.close(); }
    int[] r = parse(p);
    if (r != null) return r;
    warnOnce(what, "the menu layout file " + what + " holds no usable layout (it needs _v=1 and tile=slot lines) - the default layout is used; the file stays as it is until that layout is changed in game (then it is kept as " + what + ".bad)");
    return BAD;
  } catch (Throwable t) {
    warnOnce(what, "the menu layout file " + what + " cannot be read (" + t + ") - the default layout is shown and that layout cannot be edited until the file reads again (tried again every 30 s); the file is NOT changed");
  }
  return ERR;
}""")
# base (own / server default / built-in) -> the layout drawn: every saved slot that is valid and still free is kept (the first tile
# wins a doubled slot), every main tile without one (new in this version, dropped, or not in the file) takes the first free slot
M(lay, r"""
public static int[] resolve(int[] base) {
  int n = @PKG@.MenuData.E_VIEW.length;
  int g = @PKG@.MenuData.LAY_GRID;
  int[] out = new int[n];
  boolean[] used = new boolean[g];
  for (int i = 0; i < n; i++) {
    out[i] = -1;
    if (!isMain(i) || base == null || i >= base.length) continue;
    int sl = base[i];
    if (sl >= 0 && sl < g && !used[sl]) { out[i] = sl; used[sl] = true; }
  }
  for (int i = 0; i < n; i++) {
    if (!isMain(i) || out[i] >= 0) continue;
    int f = -1;
    for (int k = 0; k < g; k++) { if (!used[k]) { f = k; break; } }
    if (f < 0) continue;
    out[i] = f;
    used[f] = true;
  }
  return out;
}""")
M(lay, r"""
public static Object own(String k) {
  Object o = OWN.get(k);
  if (o != null) return o;
  if (DIR == null) return NONE;
  Object at = ERRAT.get(k);
  if (at != null && System.currentTimeMillis() - ((Long) at).longValue() < 30000L) return ERR;
  Object r = readFile(DIR.resolve(k + ".properties"), "layouts/" + k + ".properties");
  if (ERR.equals(r)) { ERRAT.put(k, Long.valueOf(System.currentTimeMillis())); return ERR; }
  ERRAT.remove(k);
  if (r == null) r = NONE;
  else if (BAD.equals(r)) { BROKEN.put(k, Boolean.TRUE); r = NONE; }
  Object prev = OWN.putIfAbsent(k, r);
  return prev != null ? prev : r;
}""")
M(lay, r"""
public static boolean unreadable(java.util.UUID u) {
  return u != null && ERR.equals(own(u.toString()));
}""")
M(lay, r"""
public static int[] of(java.util.UUID u) {
  int[] base = null;
  if (u != null) {
    Object o = own(u.toString());
    if (o instanceof int[]) base = (int[]) o;
  }
  if (base == null) base = DEF;
  if (base == null) base = builtin();
  return resolve(base);
}""")
M(lay, r"""
public static boolean hasOwn(java.util.UUID u) {
  return u != null && own(u.toString()) instanceof int[];
}""")
M(lay, r"""
public static String sourceOf(java.util.UUID u) {
  if (hasOwn(u)) return "your own layout";
  return DEF != null ? "the server's default layout" : "the standard layout";
}""")
M(lay, r"""
public static String text(int[] lay, String head) {
  StringBuilder sb = new StringBuilder();
  sb.append(head);
  sb.append("_v=1\n");
  for (int i = 0; i < lay.length; i++) {
    if (!isMain(i) || lay[i] < 0) continue;
    sb.append(@PKG@.MenuData.E_KEY[i]).append('=').append(lay[i]).append('\n');
  }
  return sb.toString();
}""")
M(lay, r"""
public static void keepBad(java.nio.file.Path f) throws java.io.IOException {
  if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
  java.nio.file.Path b = f.resolveSibling(f.getFileName().toString() + ".bad");
  if (java.nio.file.Files.exists(b, new java.nio.file.LinkOption[0])) b = f.resolveSibling(f.getFileName().toString() + ".bad-" + System.currentTimeMillis());
  java.nio.file.Files.move(f, b, new java.nio.file.CopyOption[0]);
}""")
M(lay, r"""
public static void writeOwn(String k) throws java.io.IOException {
  Object o = OWN.get(k);
  if (o == null || DIR == null) return;
  java.nio.file.Path f = DIR.resolve(k + ".properties");
  if (BROKEN.remove(k) != null) keepBad(f);
  if (o instanceof int[]) {
    Object nm = NAMES.get(k);
    String head = "# SkyyMenu: the SkyWynn Menu layout of one player (account uuid " + k + ", the same for every profile).\n"
      + "# tile=slot, slot = row * 9 + column (0 - 44). Change it in game: SkyWynn Menu - Edit layout. Delete this file = the default layout.\n"
      + "_name=" + @PKG@.MenuUtil.cleanName(nm == null ? "" : String.valueOf(nm)) + "\n";
    @PKG@.MenuUtil.atomicWrite(f, text((int[]) o, head).getBytes("UTF-8"));
  } else java.nio.file.Files.deleteIfExists(f);
}""")
M(lay, r"""
public static void writeDef() throws java.io.IOException {
  java.nio.file.Path f = DEF_FILE;
  if (f == null) return;
  if (DEF_BROKEN) { DEF_BROKEN = false; keepBad(f); }
  int[] d = DEF;
  if (d == null) { java.nio.file.Files.deleteIfExists(f); return; }
  String head = "# SkyyMenu: the SERVER DEFAULT SkyWynn Menu layout - every player without their own layout gets it. tile=slot (0 - 44).\n"
    + "# Set in game by an admin: SkyWynn Menu - Edit layout - Save as server default. Delete this file = the standard layout (layout D).\n";
  @PKG@.MenuUtil.atomicWrite(f, text(d, head).getBytes("UTF-8"));
}""")
M(lay, r"""
public static synchronized void saveNow(String k) {
  DIRTY.remove(k);
  try {
    if (DEF_KEY.equals(k)) writeDef(); else writeOwn(k);
    WRITES = WRITES + 1L;
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("could not save the menu layout " + (DEF_KEY.equals(k) ? "layout-default.properties" : "layouts/" + k + ".properties") + " (kept in memory, retried every 30 s and at shutdown): " + t);
    DIRTY.put(k, Boolean.TRUE);
  }
}""")
# ---- LayoutSaveTask: the delayed save (saveNow writes the NEWEST state, so quick clicks give few writes); load = the join preload
lsv.addInterface(pool.get("java.lang.Runnable"))
F(lsv, "public String k;")
F(lsv, "public boolean load;")
C(lsv, "public LayoutSaveTask(String k) { this.k = k; this.load = false; }")
C(lsv, "public LayoutSaveTask(String k, boolean load) { this.k = k; this.load = load; }")
M(lsv, r"""
public void run() {
  try {
    if (this.load) @PKG@.MenuLayout.own(this.k);
    else @PKG@.MenuLayout.saveNow(this.k);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu layout " + (this.load ? "preload" : "save") + " failed: " + t); }
}""")
# PlayerReady (MenuReady, every world switch): read the player's layout file off the world thread unless it is cached already
M(lay, r"""
public static void preload(java.util.UUID u) {
  try {
    if (u == null || DIR == null) return;
    String k = u.toString();
    if (OWN.containsKey(k)) return;
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.LayoutSaveTask(k, true), 0L, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule the menu layout preload: " + t); }
}""")
# ---- MenuLayout (cont.): the changes (world thread: memory only + a scheduled save; the inline fallback only when the executor refuses)
M(lay, r"""
public static void saveSoon(String k) {
  DIRTY.put(k, Boolean.TRUE);
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.LayoutSaveTask(k), 300L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { saveNow(k); }
}""")
# cur = the layout the player sees (of(u)); the tile on `from` goes to `to`, a tile on `to` goes to `from`. 1 = done, 0 = refused.
M(lay, r"""
public static int swap(java.util.UUID u, String name, int[] cur, int from, int to) {
  int g = @PKG@.MenuData.LAY_GRID;
  if (u == null || cur == null || cur.length != @PKG@.MenuData.E_VIEW.length || from == to || from < 0 || to < 0 || from >= g || to >= g) return 0;
  int a = -1;
  int b = -1;
  for (int i = 0; i < cur.length; i++) {
    if (!isMain(i)) continue;
    if (cur[i] == from) a = i;
    else if (cur[i] == to) b = i;
  }
  if (a < 0) return 0;
  int[] nx = new int[cur.length];
  System.arraycopy(cur, 0, nx, 0, cur.length);
  nx[a] = to;
  if (b >= 0) nx[b] = from;
  String k = u.toString();
  if (name != null) NAMES.put(k, name);
  DIRTY.put(k, Boolean.TRUE);
  OWN.put(k, nx);
  saveSoon(k);
  return 1;
}""")
M(lay, r"""
public static int reset(java.util.UUID u) {
  if (u == null) return 0;
  String k = u.toString();
  DIRTY.put(k, Boolean.TRUE);
  OWN.put(k, NONE);
  saveSoon(k);
  return 1;
}""")
M(lay, r"""
public static int saveDefault(int[] cur) {
  if (cur == null || cur.length != @PKG@.MenuData.E_VIEW.length) return 0;
  int[] c = new int[cur.length];
  System.arraycopy(cur, 0, c, 0, cur.length);
  DEF = c;
  saveSoon(DEF_KEY);
  return 1;
}""")
M(lay, r"""
public static int clearDefault() {
  DEF = null;
  saveSoon(DEF_KEY);
  return 1;
}""")
# at start (setup): the server default file -> DEF (no file / unreadable = the built-in layout D)
M(lay, r"""
public static void loadDefault() {
  Object r = readFile(DEF_FILE, "layout-default.properties");
  DEF_BROKEN = BAD.equals(r);
  if (r instanceof int[]) DEF = (int[]) r;
  else DEF = null;
  @PKG@.MenuUtil.info("menu layout editor: " + (DEF != null ? "the server default layout from layout-default.properties" : "the standard layout (layout D) is the server default") + "; players' own layouts in layouts/");
}""")
M(lay, r"""
public static void flushAll() {
  java.util.ArrayList ks = new java.util.ArrayList(DIRTY.keySet());
  for (int i = 0; i < ks.size(); i++) saveNow((String) ks.get(i));
}""")
# SeenTick (every 30 s): forget the cached layouts of players who left (never one with a save pending). Fix round: synchronized like
# saveNow (so a save's DIRTY.remove -> OWN.get never loses its entry), removes only the exact value it checked, and puts it back if a
# change marked DIRTY meanwhile (swap / reset mark DIRTY BEFORE they publish OWN).
M(lay, r"""
public static synchronized void pruneOffline(java.util.Set onlineK) {
  java.util.ArrayList ks = new java.util.ArrayList(OWN.keySet());
  for (int i = 0; i < ks.size(); i++) {
    String k = (String) ks.get(i);
    if (onlineK.contains(k) || DIRTY.containsKey(k)) continue;
    Object v = OWN.get(k);
    if (v == null || !OWN.remove(k, v)) continue;
    if (DIRTY.containsKey(k)) { OWN.putIfAbsent(k, v); continue; }
    NAMES.remove(k);
  }
  java.util.ArrayList es = new java.util.ArrayList(ERRAT.keySet());
  for (int i = 0; i < es.size(); i++) { if (!onlineK.contains(es.get(i))) ERRAT.remove(es.get(i)); }
}""")

'''
rep('''# ================= MenuPage (inline page; views switched with rebuild()) =================
''', LAYOUT_JAVA + '''# ================= MenuPage (inline page; views switched with rebuild()) =================
''')

# ================================================================================================ MenuPage: fields + constructor
rep('''F(page, "public static final int HEAL_ANSWERS = 3;")
''', '''F(page, "public static final int HEAL_ANSWERS = 3;")
# 0.3.17: the layout editor - editing (main view only), editSel = the slot of the picked-up tile (-1 = none), lay = the layout drawn
# (MenuLayout.of), occ = slot -> entry index of the tile there (hidden tiles too, -1 = empty), hid = the slot of a tile this player
# cannot see (a Kept slot in edit mode). lay / occ / hid are made by fillStatic on every draw of the main view.
for f in ("public boolean editing;", "public int editSel;", "public int[] lay;", "public int[] occ;", "public boolean[] hid;"):
    F(page, f)
''')
rep('''  this.view = view == null ? "main" : view;
  this.pageNo = 0;
  this.status = "";
  this.pages = 1;
}""")''', '''  this.view = view == null ? "main" : view;
  this.pageNo = 0;
  this.status = "";
  this.pages = 1;
  this.editing = false;
  this.editSel = -1;
}""")''')

# ================================================================================================ MenuPage: drawing in edit mode
rep('''# 0.3.16: THE PER-TILE VISIBILITY RULE (TILE_RULES -> MenuData E_PERM''', '''# 0.3.17: a tile in edit mode - it never runs its action; the picked-up one is named "[Moving] ..."
M(page, r"""
public void editTile(java.util.ArrayList slots, int slot, String icon, String name) {
  boolean sel = slot == this.editSel;
  put(slots, slot, icon, sel ? "[Moving] " + name : name, sel ? @PKG@.MenuData.EDIT_SEL_BODY : @PKG@.MenuData.EDIT_TILE_BODY,
      sel ? @PKG@.MenuData.EDIT_SEL_FOOT : (this.editSel >= 0 ? @PKG@.MenuData.EDIT_SWAP_FOOT : @PKG@.MenuData.EDIT_PICK_FOOT), "eslot", false);
}""")
# 0.3.17: every free slot of rows 0 - 4 in edit mode = an Empty slot (a target). Fix round: the slot of a tile this player cannot see is
# NOT marked (restricted tiles stay fully hidden, no greyed / "kept" entry - 2026-09-25); it stays plain, is not clickable and never a target.
M(page, r"""
public void editMarks(java.util.ArrayList slots) {
  for (int sl = 0; sl < @PKG@.MenuData.LAY_GRID; sl++) {
    if (this.acts[sl] != null || this.hid[sl]) continue;
    put(slots, sl, @PKG@.MenuData.ICON_EMPTY, @PKG@.MenuData.EMPTY_NAME, @PKG@.MenuData.EMPTY_BODY,
        this.editSel >= 0 ? @PKG@.MenuData.EMPTY_FOOT_MOVE : @PKG@.MenuData.EMPTY_FOOT_PICK, "eslot", false);
  }
}""")
# 0.3.16: THE PER-TILE VISIBILITY RULE (TILE_RULES -> MenuData E_PERM''')
rep('''public void fillStatic(java.util.ArrayList slots) {
  java.util.UUID me = this.playerRef.getUuid();
  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);
  for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {
    if (!@PKG@.MenuData.E_VIEW[i].equals(this.view)) continue;
    String act = @PKG@.MenuData.E_ACT[i];
    if (!tileVisible(i, admin)) continue;
''', '''public void fillStatic(java.util.ArrayList slots) {
  java.util.UUID me = this.playerRef.getUuid();
  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);
  boolean main = "main".equals(this.view);
  boolean edit = main && this.editing;
  if (main) {
    this.lay = @PKG@.MenuLayout.of(me);
    this.occ = new int[54];
    this.hid = new boolean[54];
    for (int sl = 0; sl < 54; sl++) this.occ[sl] = -1;
    for (int i = 0; i < this.lay.length; i++) { if (this.lay[i] >= 0 && this.lay[i] < 54) this.occ[this.lay[i]] = i; }
  }
  for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {
    if (!@PKG@.MenuData.E_VIEW[i].equals(this.view)) continue;
    int slot = main ? this.lay[i] : @PKG@.MenuData.E_SLOT[i];
    if (slot < 0) continue;
    String act = @PKG@.MenuData.E_ACT[i];
    if (!tileVisible(i, admin)) { if (main) this.hid[slot] = true; continue; }
''')
rep('''      if (!@PKG@.PetTile.installed()) continue;
''', '''      if (!@PKG@.PetTile.installed()) { if (main) this.hid[slot] = true; continue; }
''')
rep('''    String need = dim ? null : @PKG@.MenuUtil.needOf(lineOf(act));
    if (need != null) {
      put(slots, @PKG@.MenuData.E_SLOT[i], icon, name + " (update needed)", body, "Needs " + need + " on this server", act, true);
      continue;
    }
    put(slots, @PKG@.MenuData.E_SLOT[i], icon, name + (dim ? " (not installed)" : ""), body,
        dim ? "Not installed on this server" : @PKG@.MenuData.E_FOOT[i], act, dim);
  }
}""")''', '''    String need = dim ? null : @PKG@.MenuUtil.needOf(lineOf(act));
    if (edit) { editTile(slots, slot, icon, name + (need != null ? " (update needed)" : (dim ? " (not installed)" : ""))); continue; }
    if (need != null) {
      put(slots, slot, icon, name + " (update needed)", body, "Needs " + need + " on this server", act, true);
      continue;
    }
    put(slots, slot, icon, name + (dim ? " (not installed)" : ""), body,
        dim ? "Not installed on this server" : @PKG@.MenuData.E_FOOT[i], act, dim);
  }
  if (edit) editMarks(slots);
}""")''')

# ================================================================================================ MenuPage.nav: the Edit layout tile + the edit-mode controls
rep('''  put(slots, 49, @PKG@.MenuData.ICON_CLOSE, "Close", "Close the menu.", "Click to close", "close", false);
''', '''  put(slots, 49, @PKG@.MenuData.ICON_CLOSE, "Close", "Close the menu.", "Click to close", "close", false);
  if (this.view.equals("main") && !this.editing) {
    put(slots, @PKG@.MenuData.EDIT_SLOT, @PKG@.MenuData.ICON_EDIT, @PKG@.MenuData.EDIT_NAME, @PKG@.MenuData.EDIT_BODY, @PKG@.MenuData.EDIT_FOOT, "edit", false);
  }
  if (this.view.equals("main") && this.editing) {
    put(slots, @PKG@.MenuData.CTRL_DONE, @PKG@.MenuData.ICON_DONE, @PKG@.MenuData.DONE_NAME, @PKG@.MenuData.DONE_BODY, @PKG@.MenuData.DONE_FOOT, "edone", false);
    put(slots, @PKG@.MenuData.CTRL_RESET, @PKG@.MenuData.ICON_RESET, @PKG@.MenuData.RESET_NAME, @PKG@.MenuData.RESET_BODY, @PKG@.MenuData.RESET_FOOT, "ereset", false);
    if (@PKG@.MenuUtil.isAdmin(this.playerRef)) {
      put(slots, @PKG@.MenuData.CTRL_SRVSAVE, @PKG@.MenuData.ICON_SRVSAVE, @PKG@.MenuData.SRVSAVE_NAME, @PKG@.MenuData.SRVSAVE_BODY, @PKG@.MenuData.SRVSAVE_FOOT, "esrvsave", false);
      put(slots, @PKG@.MenuData.CTRL_SRVCLEAR, @PKG@.MenuData.ICON_SRVCLEAR, @PKG@.MenuData.SRVCLEAR_NAME, @PKG@.MenuData.SRVCLEAR_BODY, @PKG@.MenuData.SRVCLEAR_FOOT, "esrvclear", false);
    }
  }
''')
rep('''  this.title = @PKG@.MenuData.V_TITLE[vi];
  this.pages = 1;
  fillStatic(slots);
''', '''  this.title = @PKG@.MenuData.V_TITLE[vi];
  if (this.editing && this.view.equals("main")) this.title = @PKG@.MenuData.EDIT_TITLE;
  this.pages = 1;
  fillStatic(slots);
''')
rep('''  b.set("#SkyyMHint.Text", tipsOff ? "Tooltips off - the speech bubble at the top right turns them on. Click an item to use it."
                                   : "Hover an item for details - click it to use it. Esc closes the menu.");
''', '''  b.set("#SkyyMHint.Text", this.editing && this.view.equals("main") ? @PKG@.MenuData.EDIT_HINT
                         : (tipsOff ? "Tooltips off - the speech bubble at the top right turns them on. Click an item to use it."
                                    : "Hover an item for details - click it to use it. Esc closes the menu."));
''')

# ================================================================================================ MenuPage: the edit-mode clicks
rep('''M(page, r"""
public void click(@REF@ ref, @ST@ st, int idx, String act) {''', '''# 0.3.17: THE LAYOUT EDITOR'S CLICKS (main view, world thread). First click on a tile = pick it up; a click on another slot (a tile or an
# Empty slot) = swap + save (MenuLayout.swap); the picked-up tile again = cancel; a hidden tile's slot (not drawn) is never a target
# (a stale / forged click on it gets KEPT_MSG); a layout file that cannot be read right now is never changed (EDIT_WAIT). Reset / the two admin buttons need a second click (cfgArm, the modcfg pattern); the admin node is re-checked on the click.
M(page, r"""
public void editInfo() {
  java.util.UUID me = this.playerRef.getUuid();
  this.infoName = @PKG@.MenuData.EDIT_INFO_NAME;
  this.infoBody = @PKG@.MenuData.EDIT_INFO + "\\nYou are using: " + @PKG@.MenuLayout.sourceOf(me) + "."
    + (@PKG@.MenuUtil.isAdmin(this.playerRef) ? "\\n" + @PKG@.MenuData.EDIT_INFO_ADMIN : "");
}""")
M(page, r"""
public void startEdit() {
  this.editing = true;
  this.editSel = -1;
  editInfo();
  this.status = "Edit mode - no dragging: click a tile, then click its new slot.";
}""")
M(page, r"""
public void editClick(int idx, String act, String armed) {
  java.util.UUID me = this.playerRef.getUuid();
  if (act.equals("edone")) {
    this.editing = false;
    this.editSel = -1;
    this.infoName = null;
    this.infoBody = null;
    this.status = "Layout saved - the menu works as normal again.";
    rebuild();
    return;
  }
  if ((act.equals("eslot") || act.equals("ereset")) && @PKG@.MenuLayout.unreadable(me)) { this.editSel = -1; this.status = @PKG@.MenuData.EDIT_WAIT; rebuild(); return; }
  if (act.equals("ereset")) {
    if (!act.equals(armed)) { this.cfgArm = act; this.status = "Click Reset to default again to put every tile back."; rebuild(); return; }
    this.editSel = -1;
    @PKG@.MenuLayout.reset(me);
    editInfo();
    this.status = "Every tile is back in its default slot.";
    rebuild();
    return;
  }
  if (act.equals("esrvsave") || act.equals("esrvclear")) {
    if (!@PKG@.MenuUtil.isAdmin(this.playerRef)) { this.status = "Only admins can change the server default layout."; rebuild(); return; }
    if (!act.equals(armed)) {
      this.cfgArm = act;
      this.status = act.equals("esrvsave") ? "Click again: YOUR layout becomes the default for every player without their own."
                                           : "Click again: the standard layout (layout D) becomes the server default again.";
      rebuild();
      return;
    }
    if (act.equals("esrvsave")) {
      if (@PKG@.MenuLayout.saveDefault(this.lay) == 1) this.status = "Saved - every player without their own layout now gets yours.";
      else this.status = "That did not work - open the menu again and try once more.";
    } else {
      @PKG@.MenuLayout.clearDefault();
      this.status = "The standard layout (layout D) is the server default again.";
    }
    editInfo();
    rebuild();
    return;
  }
  if (!act.equals("eslot") || idx < 0 || idx >= @PKG@.MenuData.LAY_GRID || this.occ == null || this.lay == null || this.hid == null) return;
  int t = this.occ[idx];
  if (this.editSel < 0) {
    if (this.hid[idx]) { this.status = @PKG@.MenuData.KEPT_MSG; rebuild(); return; }
    if (t < 0) { this.status = "That slot is empty. Click a tile first, then click where it should go."; rebuild(); return; }
    this.editSel = idx;
    this.infoName = "Moving: " + @PKG@.MenuData.E_NAME[t];
    this.infoBody = @PKG@.MenuData.EDIT_MOVING;
    this.status = "Picked up " + @PKG@.MenuData.E_NAME[t] + " - now click the slot where it should go.";
    rebuild();
    return;
  }
  if (idx == this.editSel) {
    this.editSel = -1;
    editInfo();
    this.status = "Cancelled - nothing moved.";
    rebuild();
    return;
  }
  if (this.hid[idx]) { this.status = @PKG@.MenuData.KEPT_MSG; rebuild(); return; }
  int from = this.editSel;
  int mv = this.occ[from];
  this.editSel = -1;
  editInfo();
  if (mv < 0 || this.hid[from] || @PKG@.MenuLayout.swap(me, this.playerRef.getUsername(), this.lay, from, idx) != 1) {
    this.status = "That move did not work - try again.";
    rebuild();
    return;
  }
  this.status = t >= 0 ? @PKG@.MenuData.E_NAME[mv] + " and " + @PKG@.MenuData.E_NAME[t] + " swapped places." : @PKG@.MenuData.E_NAME[mv] + " moved.";
  rebuild();
}""")
M(page, r"""
public void click(@REF@ ref, @ST@ st, int idx, String act) {''')
rep('''  String armed = this.cfgArm;
  this.cfgArm = null;
  if (act.equals("close")) { closePage(ref, st); return; }
''', '''  String armed = this.cfgArm;
  this.cfgArm = null;
  if (act.equals("close")) { closePage(ref, st); return; }
  if (this.editing && this.view.equals("main")) { editClick(idx, act, armed); return; }
  if (act.equals("edit") && this.view.equals("main")) {
    java.util.UUID me = this.playerRef.getUuid();
    if (@PKG@.MenuLayout.unreadable(me)) { this.status = @PKG@.MenuData.EDIT_WAIT; rebuild(); return; }
    if (@PKG@.Tips.isOff(me) && !act.equals(armed)) {
      this.cfgArm = act;
      this.infoName = @PKG@.MenuData.EDIT_NAME;
      this.infoBody = @PKG@.MenuData.EDIT_BODY;
      this.status = @PKG@.MenuData.EDIT_ARM;
      rebuild();
      return;
    }
    startEdit();
    rebuild();
    return;
  }
''')

# ================================================================================================ start / upkeep / shutdown
rep('''  @PKG@.SetStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("settings");
''', '''  @PKG@.SetStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("settings");
  @PKG@.MenuLayout.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("layouts");
  @PKG@.MenuLayout.DEF_FILE = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("layout-default.properties");
  @PKG@.MenuLayout.loadDefault();
''')
rep('''    @PKG@.SetLoadTask.preload(pr);
''', '''    @PKG@.SetLoadTask.preload(pr);
    @PKG@.MenuLayout.preload(pr.getUuid());
''')
rep('''    @PKG@.SetStore.pruneOffline(onlineK);
''', '''    @PKG@.SetStore.pruneOffline(onlineK);
    @PKG@.MenuLayout.flushAll();
    @PKG@.MenuLayout.pruneOffline(onlineK);
''')
rep('''  try { @PKG@.SetStore.flushAll(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings flush at shutdown failed: " + t); }
''', '''  try { @PKG@.SetStore.flushAll(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings flush at shutdown failed: " + t); }
  try { @PKG@.MenuLayout.flushAll(); } catch (Throwable t) { @PKG@.MenuUtil.warn("menu layout flush at shutdown failed: " + t); }
''')

# ================================================================================================ the post-build check: the editor's texts are in the class
rep('''print("inline UI strings verified in MenuData.class:", len(UI) + len(UI_INFO) + len(SET_UI_ALL) + len(ADM_UI_ALL))
''', '''print("inline UI strings verified in MenuData.class:", len(UI) + len(UI_INFO) + len(SET_UI_ALL) + len(ADM_UI_ALL))
# 0.3.17: the editor's texts (Skyy's no-dragging rule) are in the compiled MenuData class
for _k, _v in EDIT_TXT.items():
    assert _v in _consts, "0.3.17: editor text %s missing from MenuData.class" % _k
print("0.3.17 editor texts verified in MenuData.class:", len(EDIT_TXT))
''')

# ================================================================================================ ROUND_PINS + the patch name
rep('''# 0.3.16: EMPTY - layout D + icons + tile rules, no other mod needed (the Wardrobe tile waits for SkyyWardrobe's wardrobe:fn:open).
ROUND_PINS = {}
''', '''# 0.3.16: EMPTY - layout D + icons + tile rules, no other mod needed (the Wardrobe tile waits for SkyyWardrobe's wardrobe:fn:open).
# 0.3.17: EMPTY - the layout editor, SkyyMenu's own files only.
ROUND_PINS = {}
''')
rep('_PATCH = "tools/menu_0_3_16_patch.py"', '_PATCH = "tools/menu_0_3_17_patch.py"')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
# fix round: swap / reset mark DIRTY before they publish OWN (pruneOffline never drops a pending change)
for _m in ("public static int swap(", "public static int reset("):
    _b = s[s.index(_m):s.index('}"""', s.index(_m))]
    assert _b.index("DIRTY.put(k") < _b.index("OWN.put(k"), "fix round: %s marks DIRTY before OWN" % _m
assert s.index("public static boolean unreadable(") < s.index("public void editClick(")
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.16 outside the recorded changes"
assert s.index("EDIT_TXT = {") < s.index('lay  = mk("MenuLayout")') < s.index('F(dat, "public static final String[] E_KEY') \
    < s.index("public static int[] resolve(") < s.index("public static synchronized void saveNow(") < s.index("public LayoutSaveTask(") \
    < s.index("public static void preload(java.util.UUID") < s.rindex("public static void saveSoon(") < s.index("public static int swap(") < s.index("public void editTile(") \
    < s.index("public void editMarks(") < s.index("public void fillStatic(") < s.index("public void nav(") < s.index("public void editClick(") \
    < s.index("public void click(@REF@"), "definitions before use"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.16 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
