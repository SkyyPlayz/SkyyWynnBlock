"""Derive SkyyMenu/build_skyymenu_0.3.38.py from the LIVE SkyyMenu 0.3.37 (python tools/menu_0_3_38_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_37_patch.py -> 0.3.37 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.38. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.37 (nothing else changed). Line endings kept. The harness SkyyMenu/test_skyymenu_0.3.38.py is its own file.

0.3.38 (2026-10-17) = THE VOID CHARMS NAME + the Supplies tab icon + two Teleport Arrange fixes.
  1. VOID CHARMS (the SkyyAccessories 0.5.24 rename; Skyy 2026-10-17: "i noticed they are still called accessory's in the settings"):
     the Mods list entry of SkyyAccessories: its Server Setup page title "Accessories" -> "Void Charms" (= SkyyAccessories 0.5.24's kit
     TITLE, which menu_check compares), its setup blurb "bag slots" -> "charm slots", its description "that work in the bag" -> "that
     work while they sit in Void Charms" and "Craft them in the Workbench tab Accessories and Bags" -> "Craft them in the Craft tab of
     Void Charms" (SkyyAccessories 0.5.21+ crafts accessories only there); MENU_ICONS' tile label of the bag icon -> "Void Charms" (the
     icon item, its id and saved shortcuts unchanged; the art manifest keeps its old "Accessory Bag" tile name - the build maps it).
  2. SUPPLIES TAB ICON (RESUME NEXT 2; the kit's Storage > Supplies tab, SkyyCooking 0.1.11): TAB_ICON["storage:supplies"] = a new
     icon-only item Skyy_Menu_Icon_Supplies (hidden, never held, Farming_Collar look like the other icon items) showing the APPROVED
     black-leather satchel art/accessory-bag-icon (Skyy 2026-10-08 "Yes, the bag icon looks good, commit it"; free since 0.3.37 gave the
     Void Charms tile the amulet) - a pouch for the Potion Flask + Food Pouch, no new art. The tab row has no 72 px picture pair for it
     yet (none approved): the tab shows its label only, as today (TAB_NO_ART); a Home shortcut to the tab wears the satchel.
  3. TELEPORT ARRANGE - WARP NAMES WITH '.': MenuLayout.okWarp refused '.', which SkyyEssentials' warp name rule allows, so a warp like
     mine.deep was drawn but could not be pinned (the layout dropped the key). okWarp now takes letters, digits, _ - . and up to 64
     characters (vanilla /warp set names can be longer than /warpadmin's 32; okKey's 80 cap unchanged). An auto tile whose name still breaks
     the rule (a space ...) is no longer "picked up" in Arrange: the click says it can't be arranged and nothing is saved.
  4. TELEPORT ARRANGE - PREV / NEXT: Arrange had no page buttons, so auto tiles on page 2+ could not be reached; the Arrange foot row now
     shows < Prev / Next > like the normal Teleport foot (research/Menu-Pattern.md: one pager in the foot; the row still fits TP_FOOT_W).
  No new command, permission, setting or bridge key. Saved data: unchanged format (the Teleport grid may now hold warp:<name.with.dots>).
  ROLLBACK to 0.3.37: safe (0.3.37 drops a dotted warp key from the grid - that warp shows as an auto tile again; the Supplies shortcut
  shows the Storage hub icon).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import skyyui as SUI

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.37.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.38.py"))
assert P.has('VERSION = "0.3.37"\n') and P.has("MENU_ICONS_W") and P.has("tools/menu_0_3_37_patch.py"), "not the generated SkyyMenu 0.3.37 script"
assert ("storage", "supplies") in [(r[0], r[1]) for r in SUI.HUB_TABS], "the kit's Supplies tab"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.38: the Void Charms rename (notes: tools/menu_0_3_38_patch.py): the SkyyAccessories Mods entry (Server Setup title, blurb, text);
       the Supplies tab icon item (the approved satchel, art/accessory-bag-icon); Teleport Arrange takes warp names with '.' and pages
       with < Prev / Next >.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.38.py.
''')
P.rep('VERSION = "0.3.37"\n', 'VERSION = "0.3.38"\n')

# =================================================================================================== 1. Void Charms texts
P.rep("('AccessoryBag', 'Accessory Bag')", "('AccessoryBag', 'Void Charms')")
P.rep('''     "setup": ("0.4.4", "Accessories", "bag slots, booster lines, notices, Lantern"),''',
      '''     "setup": ("0.4.4", "Void Charms", "charm slots, booster lines, notices, Lantern"),   # 0.3.38: = SkyyAccessories 0.5.24's TITLE''')
P.rep(''' and more - that work in the bag. Only the best rarity of each line counts. Craft them in the Workbench tab Accessories and Bags.",''',
      ''' and more - that work while they sit in Void Charms. Only the best rarity of each line counts. Craft them in the Craft tab of Void Charms.",''')
P.rep('''assert "Accessories and Bags" in _bym["SkyyAccessories"]["desc"] and''',
      '''assert "Craft tab of Void Charms" in _bym["SkyyAccessories"]["desc"] and''')   # 0.3.38: accessories are crafted only in Void Charms
P.rep('''    all(t["item_id"] == "Skyy_Menu_Icon_" + t["name"] and dict(MENU_ICONS)[t["name"]] == t["tile"] for t in _mman["tiles"]), "0.3.16: the 23 approved icons"''',
      '''    all(t["item_id"] == "Skyy_Menu_Icon_" + t["name"] and dict(MENU_ICONS)[t["name"]] == {"Accessory Bag": "Void Charms"}.get(t["tile"], t["tile"])
        for t in _mman["tiles"]), "0.3.16: the 23 approved icons (0.3.38: the bag tile is called Void Charms)"''')

# =================================================================================================== 2. the Supplies tab icon
P.rep('''ICON_BAG = "Skyy_Menu_Icon_AccessoryBag"      # 0.3.11''', '''# 0.3.38: the Supplies tab (Storage > Supplies, SkyyCooking 0.1.11) wears the approved satchel (art/accessory-bag-icon, free since 0.3.37)
ICON_ITEMS["Skyy_Menu_Icon_Supplies"] = ("art/accessory-bag-icon/Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png",
                                         "Icons/ItemsGenerated/Skyy_Menu_Icon_Supplies.png", "art/accessory-bag-icon/manifest.json",
                                         "Supplies", "Farming_Collar")
ICON_BAG = "Skyy_Menu_Icon_AccessoryBag"      # 0.3.11''')
P.rep('''    len(ICON_ITEMS) == 1 + len(PET_ART) + len(MENU_ICONS) - 1 + len(MENU_ICONS_2) + len(MENU_ICONS_3) + len(MENU_ICONS_W), \\''',
      '''    len(ICON_ITEMS) == 1 + len(PET_ART) + len(MENU_ICONS) - 1 + len(MENU_ICONS_2) + len(MENU_ICONS_3) + len(MENU_ICONS_W) + 1, \\''')   # 0.3.38: + Supplies
P.rep('''"market:merchants": "Skyy_Menu_Icon_Merchants", "settings:layout": "Skyy_Menu_Icon_Layout"})''',
      '''"market:merchants": "Skyy_Menu_Icon_Merchants", "settings:layout": "Skyy_Menu_Icon_Layout",
                 "storage:supplies": "Skyy_Menu_Icon_Supplies"})   # 0.3.38''')
P.rep('''assert TAB_ART == sorted(_t.replace(":", "_") for _t in TAB_ICON), "0.3.30: one tab icon picture per contract tab (no Multitool)"''',
      '''TAB_NO_ART = ("storage:supplies",)   # 0.3.38: no approved 72 px tab picture pair yet - the tab shows its label only (as in 0.3.37)
assert TAB_ART == sorted(_t.replace(":", "_") for _t in TAB_ICON if _t not in TAB_NO_ART), "0.3.30: one tab icon picture per contract tab (no Multitool)"''')

# =================================================================================================== 3. warp names with '.'
P.rep('''public static boolean okWarp(String n) {
  if (n == null || n.length() < 1 || n.length() > 32) return false;
  for (int i = 0; i < n.length(); i++) {
    char c = n.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-')) return false;''',
      '''public static boolean okWarp(String n) {
  if (n == null || n.length() < 1 || n.length() > 64) return false;   // 0.3.38: 64 (vanilla /warp set names may be longer than 32)
  for (int i = 0; i < n.length(); i++) {
    char c = n.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-' || c == '.')) return false;   // 0.3.38: + '.' (SkyyEssentials' warp name rule)''')
P.rep('''      String ak = this.autoAt[idx];
      String[] g = @PKG@.MenuLayout.copy(this.grid);''', '''      String ak = this.autoAt[idx];
      if (!@PKG@.MenuLayout.okKey(ak, p == 1)) { this.status = nameOf(ak) + " can't be arranged (its name has characters a layout can't save) - it stays in the free slots."; rebuild(); return; }   // 0.3.38
      String[] g = @PKG@.MenuLayout.copy(this.grid);''')

# =================================================================================================== 4. Arrange pages
P.rep('''    if (home && this.editSel < 0 && @PKG@.MenuLayout.hasOldDefault() && @PKG@.MenuUtil.isAdmin(this.playerRef)) ws.add("edold");
    ws.add("edone");''', '''    if (home && this.editSel < 0 && @PKG@.MenuLayout.hasOldDefault() && @PKG@.MenuUtil.isAdmin(this.playerRef)) ws.add("edold");
    if (!home && this.pageNo > 0) ws.add("prev");                   // 0.3.38: Arrange pages through the auto tiles too
    if (!home && this.pageNo < this.pages - 1) ws.add("next");
    ws.add("edone");''')
P.rep('''               "tp": [["hedit", "prev", "next", "close"], ["eremove", "ereset", "esrv", "estd", "edone"], ["aprev", "anext", "acancel"]]}''',
      '''               "tp": [["hedit", "prev", "next", "close"], ["eremove", "ereset", "esrv", "estd", "prev", "next", "edone"], ["aprev", "anext", "acancel"]]}   # 0.3.38: Arrange + prev / next''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.38 adds no system / command"
P.finish()
