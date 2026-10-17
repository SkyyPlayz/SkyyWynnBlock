"""Derive SkyyMenu/build_skyymenu_0.3.37.py from the LIVE SkyyMenu 0.3.36 (python tools/menu_0_3_37_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_36_patch.py -> 0.3.36 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.37. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.36 (nothing else changed). The harness SkyyMenu/test_skyymenu_0.3.37.py is its own file.

0.3.37 (2026-10-17) = round tp37: WARPS, ISLAND HOMES AND HOMES ON THE TELEPORT PAGE + warp icons + the Void Charms icon.
Skyy (docs/answered/world.md + ui.md 2026-10-17): "give players warp. put it in the teleports page (only admin can set warps. but players
can see them, and rearrange them in their teleport menu. (if posible i want a bunch of custom icons we can set to a warp when making it. for
mining fishing foraging farming and what not. probably 1 per zone.)" + "warps, island homes, and homes should all show up in, and be
organizable in the teleport page" + the Void Charms icon popup: "A - gold chain + glow" and "Also use the new amulet on the Character hub
Void Charms tab?" -> "Yes".
  1. WORLD > TELEPORT (kit 1.7 hub page, its 5 x 5 grid): the fixed spots (My Island | Hub | Spawn) as before, then every ISLAND HOME
     (SkyyIslands 0.5.19 island:fn:homes; tile = the My Island picture, "Island home <name>"), every HOME (SkyyEssentials 0.1.13
     essentials:fn:homes; tile = the warp-icons Home picture, "Home <name>") and every WARP (vanilla TeleportPlugin, as before) that the
     player has not placed, in that order, in the free slots of rows 4 + 5 (Prev / Next page through them) - so new warps / homes appear
     at the end. A click = that mod's own teleport: island:fn:gohome (the page closes first, like My Island; /island's rules and chat
     lines), essentials:fn:gohome ("ok" = queued -> the page closes; else the reason in the status line), a warp = vanilla tryGo as before.
     A bridge that is missing (mod not installed / older) = those tiles are simply not there; a home that is gone = its pinned tile hides.
  2. ARRANGE (the Teleport page's Edit button is now "Arrange"; Home keeps "Edit shortcuts"): the 0.3.29 editor (click a tile, then a
     slot - they swap; no dragging), and now the AUTO tiles (homes / warps nobody placed) are drawn in Arrange too: a click on one pins it
     where it is and picks it up, the next click puts it where it goes. Saved per player at once (MenuLayout, the Teleport grid). New keys
     ihome:<name> / zhome:<name> (MenuLayout.okTp: the warp name rule); + Add lists island homes and homes too.
  3. WARP ICONS: art/warp-icons (DRAFT, tools/art/make_warp_icons.py) ships as the icon-only items Skyy_Menu_Icon_Warp<Name> (11; the
     manifest sha256 + bytes checked); a warp tile wears the icon SkyyEssentials 0.1.14 saved for it (essentials:fn:warps '<id>|<theme>';
     theme -> item: MenuData.WI_THEME / WI_ICON; no bridge / no pick / unknown theme = the signpost as before).
  4. VOID CHARMS ICON: the icon item Skyy_Menu_Icon_AccessoryBag (same id - saved shortcuts keep working) now shows the approved void
     amulet art/void-charms-icon (A); the Character hub's Void Charms tab pair (SkyyHubTabs/character_accessories(_on)@2x.png) comes from
     art/void-charms-icon/hub-tab (its manifest sha256 + bytes checked) instead of art/hub-tab-icons.
  No new command, permission or setting. Saved data: the Teleport grid file may now hold ihome: / zhome: keys. ROLLBACK to 0.3.36: safe
  (0.3.36's okKey refuses those keys, so a pinned home is not drawn there; warps / fixed spots unchanged).
  Requirements (research/Menu-Pattern.md rule 9): none on these pages (no costs / levels; a locked warp keeps its red foot line).
"""
import os, sys, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import skyyui as SUI

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.36.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.37.py"))
assert P.has('VERSION = "0.3.36"\n') and P.has("OPS_SUBTABS") and not P.has("MENU_ICONS_W"), "not the generated SkyyMenu 0.3.36 script"
assert SUI.KIT_PAGE_VERSION == "1.7", "kit skyyui 1.7 (hub_page)"

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.37: round tp37 (notes: tools/menu_0_3_37_patch.py): World > Teleport lists island homes (island:fn:homes), homes (essentials:fn:homes)
       and warps (with their SkyyEssentials 0.1.14 icons, essentials:fn:warps) after the fixed spots; Arrange (was Edit) also picks up the
       auto tiles; the art/warp-icons icon items; the Void Charms icon item + Character tab pair = art/void-charms-icon.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.37.py.
''')
P.rep('VERSION = "0.3.36"\n', 'VERSION = "0.3.37"\n')

# =================================================================================================== 4. the Void Charms icon item + tab
P.rep('''    "Skyy_Menu_Icon_AccessoryBag": ("art/accessory-bag-icon/Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png",
                                    "Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png", "art/accessory-bag-icon/manifest.json",''',
      '''    # 0.3.37: the same id (saved shortcuts keep working), the approved void amulet (art/void-charms-icon A, Skyy 2026-10-17)
    "Skyy_Menu_Icon_AccessoryBag": ("art/void-charms-icon/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png",
                                    "Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png", "art/void-charms-icon/manifest.json",''')
P.rep('''MENU_ICON_OF["Void Charms"] = "Skyy_Menu_Icon_AccessoryBag"   # 0.3.36: the renamed tile keeps the bag icon (art manifest: Accessory Bag)
''', '''MENU_ICON_OF["Void Charms"] = "Skyy_Menu_Icon_AccessoryBag"   # 0.3.36: the renamed tile keeps the bag icon (art manifest: Accessory Bag)
# ---- 0.3.37: THE WARP ICONS (round tp37; art/warp-icons, tools/art/make_warp_icons.py, DRAFT until Skyy approves the sheet): one icon-only
# item per new theme (Skyy_Menu_Icon_Warp<Name>, checked against the manifest's sha256 + bytes like menu-icons-2); the theme table =
# the manifest's reused themes (warp = the signpost default, hub, spawn) + the new ones. SkyyEssentials 0.1.14 saves a theme per warp.
MENU_ICON_DIR_W = "art/warp-icons"
_WIM = json.load(open(os.path.join(HERE, "..", *(MENU_ICON_DIR_W + "/manifest.json").split("/")), encoding="utf8"))
MENU_ICONS_W = [(_i["name"], _i["label"], _i["theme"]) for _i in _WIM["icons"]]
for _nm, _lab, _th in MENU_ICONS_W:
    assert "Skyy_Menu_Icon_" + _nm not in ICON_ITEMS and _nm.startswith("Warp"), "0.3.37: %s clashes with an icon item we already ship" % _nm
    ICON_ITEMS["Skyy_Menu_Icon_" + _nm] = ("%s/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % (MENU_ICON_DIR_W, _nm),
                                         "Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % _nm, MENU_ICON_DIR_W + "/manifest.json",
                                         "%s (warp icon)" % _lab, "Farming_Collar")
WI_THEME = [_r["theme"] for _r in _WIM["reused"]] + [_t for _n, _l, _t in MENU_ICONS_W]
WI_ICON = [_r["id"] for _r in _WIM["reused"]] + ["Skyy_Menu_Icon_" + _n for _n, _l, _t in MENU_ICONS_W]
ICON_ZHOME = "Skyy_Menu_Icon_WarpHome"       # 0.3.37: a home (/sethome) tile
ICON_IHOME = "Skyy_Menu_Icon_MyIsland"       # 0.3.37: an island home tile (the My Island picture)
assert WI_THEME[0] == "warp" and WI_ICON[0] == "Skyy_Menu_Icon_Warp" and len(set(WI_THEME)) == len(WI_THEME) and all(_i in ICON_ITEMS for _i in WI_ICON) \\
    and ICON_ZHOME in ICON_ITEMS and ICON_IHOME in ICON_ITEMS, "0.3.37: every warp theme has a shipped icon item"
''')
P.rep('''    len(ICON_ITEMS) == 1 + len(PET_ART) + len(MENU_ICONS) - 1 + len(MENU_ICONS_2) + len(MENU_ICONS_3), \\''',
      '''    len(ICON_ITEMS) == 1 + len(PET_ART) + len(MENU_ICONS) - 1 + len(MENU_ICONS_2) + len(MENU_ICONS_3) + len(MENU_ICONS_W), \\''')
P.rep('''TAB_ART = sorted("%s_%s" % (_i["hub"], _i["tab"]) for _i in _TAM["icons"] if _i["hub"] != "hubrow")
''', '''TAB_ART = sorted("%s_%s" % (_i["hub"], _i["tab"]) for _i in _TAM["icons"] if _i["hub"] != "hubrow")
# 0.3.37: tab pictures drawn elsewhere (Skyy 2026-10-17 "Also use the new amulet on the Character hub Void Charms tab?" -> "Yes"):
# tab -> (art folder, its manifest); the pair is <folder>/hub-tab/<hub>_<tab>(_on).png
TAB_ART_OVER = {"character_accessories": ("art/void-charms-icon", json.load(open(os.path.join(HERE, "..", "art", "void-charms-icon", "manifest.json"), encoding="utf8")))}
assert all(_k in TAB_ART for _k in TAB_ART_OVER)
''')
P.rep('''        _data = open(os.path.join(HERE, "..", *(TAB_ART_DIR + "/" + _fn).split("/")), "rb").read()
        _me = [f for f in _TAM["files"] if f["path"] == _fn]''', '''        if _st in TAB_ART_OVER:      # 0.3.37: the Void Charms amulet pair
            _odir, _om = TAB_ART_OVER[_st]
            _data = open(os.path.join(HERE, "..", *(_odir + "/hub-tab/" + _fn).split("/")), "rb").read()
            _me = [f for f in _om["files"] if f["path"] == "hub-tab/" + _fn]
        else:
            _data = open(os.path.join(HERE, "..", *(TAB_ART_DIR + "/" + _fn).split("/")), "rb").read()
            _me = [f for f in _TAM["files"] if f["path"] == _fn]''')

# =================================================================================================== texts
P.rep('''    ("tp",      "Teleport",       ["Your island, the hub, the server spawn and every warp that has been set.",
                                   "Admins add warps with /warp set <name>."]),''',
      '''    ("tp",      "Teleport",       ["Your island, your island homes, your homes, the hub, the server spawn and every warp.",
                                   "Admins add warps (and pick their icons) on /warpadmin."]),''')
P.rep('''    "HT_TP_HINT": "Click a place to go there. Edit puts your favourite in the middle, under your mouse (no dragging).",''',
      '''    "HT_TP_HINT": "Click a place to go there. Arrange moves your tiles: click one, then the slot it goes to (no dragging).",''')
P.rep('''UI29_FBT = [_fbmk("SkyyMTp", w_, "Edit" if w_ == "hedit" else lab, tw, kind, snd) for (w_, lab, _wid, kind, snd), tw in zip(FB, FB_TW)]''',
      '''UI29_FBT = [_fbmk("SkyyMTp", w_, "Arrange" if w_ == "hedit" else lab, tw, kind, snd) for (w_, lab, _wid, kind, snd), tw in zip(FB, FB_TW)]   # 0.3.37: Arrange''')

# =================================================================================================== MenuData
P.rep('''F(dat, "public static final String[] TPK_KEY = %s;" % jarr(sorted(TP_KEYS)))
''', '''F(dat, "public static final String[] TPK_KEY = %s;" % jarr(sorted(TP_KEYS)))
F(dat, "public static final String[] WI_THEME = %s;" % jarr(WI_THEME))      # 0.3.37: warp icon themes (SkyyEssentials 0.1.14) -> icon items
F(dat, "public static final String[] WI_ICON = %s;" % jarr(WI_ICON))
F(dat, "public static final String ICON_ZHOME = %s;" % jstr(ICON_ZHOME))
F(dat, "public static final String ICON_IHOME = %s;" % jstr(ICON_IHOME))
''')

# =================================================================================================== MenuLayout: the new keys
P.rep('''  return k.startsWith("warp:") && okWarp(k.substring(5));
''', '''  if (k.startsWith("ihome:") || k.startsWith("zhome:")) return okWarp(k.substring(6));   // 0.3.37: an island home / a home (names: the warp rule)
  return k.startsWith("warp:") && okWarp(k.substring(5));
''')

# =================================================================================================== MenuPage
P.rep('''for f in ("public boolean editing;", "public int editSel;", "public boolean[] hid;"):''',
      '''for f in ("public boolean editing;", "public int editSel;", "public boolean[] hid;",
          "public String[] ihs;", "public String[] zhs;", "public java.util.HashMap wth;", "public String[] autoAt;"):   # 0.3.37: island homes, homes, warp themes, the auto tile of each slot (Arrange)''')
# the helpers (before warpTile / look / fillAutoWarps)
P.rep('''# a warp tile { icon, name, hover text (+ pos), foot, action, state } - open or locked (look() and fillAutoWarps)
M(page, r"""
public String[] warpTile(String n, @WRP@ w, String pos) {''', '''# 0.3.37: a bridge's home list (String[] names; null = the bridge is not there; names that break the key rule are left out)
M(page, r"""
public String[] homesOf(String key) {
  Object f = @PKG@.MenuUtil.bridge().get(key);
  if (!(f instanceof java.util.function.Function)) return null;
  try {
    Object r = ((java.util.function.Function) f).apply(this.playerRef.getUuid());
    if (r instanceof String[]) {
      String[] a = (String[]) r;
      java.util.ArrayList ok = new java.util.ArrayList();
      for (int i = 0; i < a.length; i++) { if (a[i] != null && @PKG@.MenuLayout.okWarp(a[i]) && !ok.contains(a[i])) ok.add(a[i]); }
      return (String[]) ok.toArray(new String[0]);
    }
  } catch (Throwable t) { @PKG@.PageGuard.warnOnce("the bridge " + key + " failed: " + t); }
  return new String[0];
}""")
# 0.3.37: essentials:fn:warps -> { lower warp id -> theme }; empty = no bridge (every warp the signpost)
M(page, r"""
public static java.util.HashMap warpThemes() {
  java.util.HashMap m = new java.util.HashMap();
  Object f = @PKG@.MenuUtil.bridge().get("essentials:fn:warps");
  if (!(f instanceof java.util.function.Function)) return m;
  try {
    Object r = ((java.util.function.Function) f).apply((Object) null);
    if (r instanceof String[]) {
      String[] a = (String[]) r;
      for (int i = 0; i < a.length; i++) {
        if (a[i] == null) continue;
        int p = a[i].lastIndexOf('|');
        if (p > 0) m.put(a[i].substring(0, p).toLowerCase(java.util.Locale.ROOT), a[i].substring(p + 1));
      }
    }
  } catch (Throwable t) { @PKG@.PageGuard.warnOnce("the bridge essentials:fn:warps failed: " + t); }
  return m;
}""")
M(page, r"""
public static String themeIcon(java.util.HashMap th, String warp) {
  Object t = th == null || warp == null ? null : th.get(warp.toLowerCase(java.util.Locale.ROOT));
  if (t instanceof String) {
    for (int i = 0; i < @PKG@.MenuData.WI_THEME.length; i++) { if (@PKG@.MenuData.WI_THEME[i].equals(t)) return @PKG@.MenuData.WI_ICON[i]; }
  }
  return @PKG@.MenuData.ICON_WARP;
}""")
# the name as the bridge spells it (any case), null = not in the list
M(page, r"""
public static String nameIn(String[] a, String n) {
  if (a == null || n == null) return null;
  for (int i = 0; i < a.length; i++) { if (a[i] != null && a[i].equalsIgnoreCase(n)) return a[i]; }
  return null;
}""")
# the lists one draw uses (world thread): island homes, homes, the warp icons
M(page, r"""
public void loadTp() {
  this.ihs = homesOf("island:fn:homes");
  this.zhs = homesOf("essentials:fn:homes");
  this.wth = warpThemes();
}""")
# a warp tile { icon, name, hover text (+ pos), foot, action, state } - open or locked (look() and fillAutoWarps)
M(page, r"""
public String[] warpTile(String n, @WRP@ w, String pos) {''')
P.rep('''  return new String[] { open ? @PKG@.MenuData.ICON_WARP : @PKG@.MenuData.ICON_WARP_LOCKED, open ? id : id + " (locked)",''',
      '''  return new String[] { open ? themeIcon(this.wth, n) : @PKG@.MenuData.ICON_WARP_LOCKED, open ? id : id + " (locked)",   // 0.3.37: its icon''')
P.rep('''    @WRP@ w = (@WRP@) tp.getWarps().get(n);
    if (w == null) return gone(@PKG@.MenuData.ICON_WARP_LOCKED, n);
    return warpTile(n, w, "");
  }
  return gone(@PKG@.MenuData.ICON_EMPTY, k);
}""")''', '''    @WRP@ w = (@WRP@) tp.getWarps().get(n);
    if (w == null) return gone(@PKG@.MenuData.ICON_WARP_LOCKED, n);
    return warpTile(n, w, "");
  }
  if (k.startsWith("ihome:") || k.startsWith("zhome:")) {   // 0.3.37: an island home (SkyyIslands) / a home (SkyyEssentials)
    boolean isl = k.startsWith("ihome:");
    String n = k.substring(6);
    String ic = isl ? @PKG@.MenuData.ICON_IHOME : @PKG@.MenuData.ICON_ZHOME;
    String nm = nameIn(isl ? this.ihs : this.zhs, n);
    if (nm == null) return gone(ic, (isl ? "Island home " : "Home ") + n);
    if (isl) return new String[] { ic, "Island home " + nm, "Your island home " + nm + " (set with /island sethome " + nm + ").\\nCommand: /island " + nm, "Click to teleport!", "ihome:" + nm, "ok" };
    return new String[] { ic, "Home " + nm, "Your home " + nm + " (set with /sethome " + nm + ").\\nCommand: /home " + nm, "Click to teleport!", "zhome:" + nm, "ok" };
  }
  return gone(@PKG@.MenuData.ICON_EMPTY, k);
}""")''')
P.rep('''  for (int i = 0; i < @PKG@.MenuData.TPK_KEY.length; i++) out.add(@PKG@.MenuData.TPK_KEY[i]);
''', '''  for (int i = 0; i < @PKG@.MenuData.TPK_KEY.length; i++) out.add(@PKG@.MenuData.TPK_KEY[i]);
  if (this.ihs != null) { for (int i = 0; i < this.ihs.length; i++) out.add("ihome:" + this.ihs[i]); }   // 0.3.37: island homes, homes
  if (this.zhs != null) { for (int i = 0; i < this.zhs.length; i++) out.add("zhome:" + this.zhs[i]); }
''')
# fillAutoWarps: island homes, homes, then warps; drawn in Arrange too (autoAt)
_old_auto = P.s[P.s.index('''# the Teleport page: warps nobody placed fill the free slots of rows 4 and 5 (Prev / Next page through them)
M(page, r"""
public void fillAutoWarps('''):]
_old_auto = _old_auto[:_old_auto.index('}""")\n') + len('}""")\n')]
assert _old_auto.count("public void fillAutoWarps(") == 1 and "No warps yet" in _old_auto
P.rep(_old_auto, '''# the Teleport page: warps nobody placed fill the free slots of rows 4 and 5 (Prev / Next page through them)
# 0.3.37: island homes, then homes, then warps - every one the player has not placed (new ones land at the end); in Arrange they are
# drawn as pick-up tiles (autoAt[slot] = the key; a click pins it there - dashEditClick)
M(page, r"""
public static void addAuto(java.util.ArrayList keys, String[] grid, String pfx, String[] names) {
  if (names == null) return;
  for (int i = 0; i < names.length; i++) {
    String k = pfx + names[i];
    boolean on = false;
    for (int s = 0; s < grid.length; s++) { if (grid[s] != null && grid[s].equalsIgnoreCase(k)) on = true; }
    if (!on) keys.add(k);
  }
}""")
M(page, r"""
public void fillAutoWarps(java.util.ArrayList slots) {
  @TPP@ tp = null;
  try { tp = @TPP@.get(); } catch (Throwable t) { }
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.Map warps = null;
  boolean placed = false;
  for (int s = 0; s < this.grid.length; s++) { if (this.grid[s] != null && this.grid[s].startsWith("warp:")) placed = true; }
  addAuto(keys, this.grid, "ihome:", this.ihs);
  addAuto(keys, this.grid, "zhome:", this.zhs);
  int nw = 0;
  if (tp != null && tp.isWarpsLoaded()) {
    warps = tp.getWarps();
    java.util.ArrayList ws = new java.util.ArrayList();
    java.util.Iterator it = warps.keySet().iterator();
    while (it.hasNext()) { String k = String.valueOf(it.next()); if (!@PKG@.MenuLayout.has(this.grid, "warp:" + k)) ws.add(k); }
    java.util.Collections.sort(ws);
    nw = ws.size();
    for (int i = 0; i < ws.size(); i++) keys.add("warp:" + (String) ws.get(i));
  }
  java.util.ArrayList free = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.MenuData.TP_AUTO.length; i++) {
    int s = @PKG@.MenuData.TP_AUTO[i];
    if (this.grid[s] == null) free.add(Integer.valueOf(s));
  }
  int per = free.size();
  if (per == 0) return;
  this.pages = paging(keys.size(), per);
  if (this.pageNo >= this.pages) this.pageNo = this.pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  for (int i = 0; i < per; i++) {
    int k = this.pageNo * per + i;
    if (k >= keys.size()) break;
    String key = (String) keys.get(k);
    int s = ((Integer) free.get(i)).intValue();
    String[] l = null;
    if (key.startsWith("warp:")) {
      @WRP@ w = (@WRP@) warps.get(key.substring(5));
      if (w == null) continue;
      String pos = "";
      try {
        @V3D@ p = w.getTransform().getPosition();
        pos = "\\nX " + (long) Math.floor(p.x) + "   Y " + (long) Math.floor(p.y) + "   Z " + (long) Math.floor(p.z);
      } catch (Throwable t) { }
      l = warpTile(key.substring(5), w, pos);
    } else {
      l = look(key, false);
    }
    if (l == null || l[5].equals("perm") || l[5].equals("gone")) continue;
    if (this.editing) {
      if (this.autoAt != null && s < this.autoAt.length) this.autoAt[s] = key;
      editTile2(slots, s, l[0], l[1]);
    } else {
      put(slots, s, l[0], l[1], l[2], l[3], l[4], l[5].equals("dim"));
    }
  }
  if (nw == 0 && !placed && !this.editing) {
    int at = keys.isEmpty() ? (per > 3 ? 3 : 0) : keys.size() - this.pageNo * per;
    if (at >= 0 && at < per) {
      put(slots, ((Integer) free.get(at)).intValue(), @PKG@.MenuData.ICON_NO_WARPS, "No warps yet",
          tp == null || warps != null ? "No warps have been set on this server yet.\\nAn admin adds them on /warpadmin (Add warp here)." : "The warp list is still loading.\\nOpen this menu again in a moment.",
          null, "info", true);
    }
  }
}""")
''')
P.rep('''  if (this.editing && this.addSlot >= 0) { fillAdd(slots, home, admin); return; }
  this.grid = @PKG@.MenuLayout.grid(this.playerRef.getUuid(), part());''', '''  loadTp();                                                         // 0.3.37: island homes, homes, warp icons
  this.autoAt = new String[@PKG@.MenuData.HG_N];
  if (this.editing && this.addSlot >= 0) { fillAdd(slots, home, admin); return; }
  this.grid = @PKG@.MenuLayout.grid(this.playerRef.getUuid(), part());''')
P.rep('''  if (!home && !this.editing) fillAutoWarps(slots);''', '''  if (!home) fillAutoWarps(slots);   // 0.3.37: in Arrange too (pick-up tiles)''')
P.rep('''    if (this.grid[idx] == null) { this.addSlot = idx; this.addPage = 0; this.status = ""; rebuild(); return; }''',
      '''    if (this.grid[idx] == null && this.autoAt != null && idx < this.autoAt.length && this.autoAt[idx] != null) {   // 0.3.37: an auto tile: pinned here + picked up
      String ak = this.autoAt[idx];
      String[] g = @PKG@.MenuLayout.copy(this.grid);
      if (@PKG@.MenuLayout.has(g, ak)) { rebuild(); return; }
      g[idx] = ak;
      if (!saveGrid(p, g)) return;
      this.editSel = idx;
      this.status = "Picked up " + nameOf(ak) + " - click the slot where it should go (no dragging).";
      rebuild();
      return;
    }
    if (this.grid[idx] == null) { this.addSlot = idx; this.addPage = 0; this.status = ""; rebuild(); return; }''')
# the home teleports (before click)
P.rep('''M(page, r"""
public void doWarp(@REF@ ref, @ST@ st, String key) {''', '''# 0.3.37: an island home / a home tile: the owner mod's bridge does the teleport with its own rules. Island: the page closes first (the
# /island teleport may change worlds - the My Island tile's order); /island's chat line says what happened. Home: "ok" = queued on the
# player's world thread -> the page closes; else the reason stays in the status line.
M(page, r"""
public void goHome(@REF@ ref, @ST@ st, String name, boolean island) {
  String key = island ? "island:fn:gohome" : "essentials:fn:gohome";
  Object f = @PKG@.MenuUtil.bridge().get(key);
  if (!(f instanceof java.util.function.Function)) { this.status = island ? "Island homes are not on this server right now." : "Homes are not on this server right now."; rebuild(); return; }
  Object[] a = new Object[] { this.playerRef.getUuid(), name };
  if (island) {
    closePage(ref, st);
    try { ((java.util.function.Function) f).apply(a); } catch (Throwable t) { @PKG@.MenuUtil.warn("the bridge " + key + " failed: " + t); }
    return;
  }
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(a); } catch (Throwable t) { @PKG@.MenuUtil.warn("the bridge " + key + " failed: " + t); r = null; }
  String s = r == null ? "" : String.valueOf(r);
  if (s.equals("ok")) { closePage(ref, st); return; }
  this.status = s.length() == 0 ? "That did not work - try again." : "Could not go home: " + s;
  rebuild();
}""")
M(page, r"""
public void doWarp(@REF@ ref, @ST@ st, String key) {''')
P.rep('''  if (act.startsWith("warp:")) { doWarp(ref, st, act.substring(5)); return; }
''', '''  if (act.startsWith("warp:")) { doWarp(ref, st, act.substring(5)); return; }
  if (act.startsWith("ihome:")) { goHome(ref, st, act.substring(6), true); return; }    // 0.3.37
  if (act.startsWith("zhome:")) { goHome(ref, st, act.substring(6), false); return; }
''')
P.rep('''for _nm, _tile in MENU_ICONS:
    _iid = "Skyy_Menu_Icon_" + _nm
    _png = files["Common/" + ICON_ITEMS[_iid][1]]
''', '''for _nm, _tile in MENU_ICONS:
    _iid = "Skyy_Menu_Icon_" + _nm
    if _nm == "AccessoryBag":   # 0.3.37: the Void Charms item shows the approved amulet (art/void-charms-icon, checked by icon_item_png)
        continue
    _png = files["Common/" + ICON_ITEMS[_iid][1]]
''')
assert P.s.count("loadTp()") == 2 and "Arrange" in P.s
P.finish()
