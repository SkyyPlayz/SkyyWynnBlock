"""Derive SkyyMenu/build_skyymenu_0.3.29.py from the LIVE SkyyMenu 0.3.28 (python tools/menu_0_3_29_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_28_patch.py -> 0.3.28 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.29. The harness SkyyMenu/test_skyymenu_0.3.29.py is its own file.

0.3.29 (2026-10-15) = UNIFIED MENU round U1 (research/Unified-Menu-Plan.md section 0 + 1 + 2 + 4 + 5 + 6; kit skyyui 1.6 = the hub row,
tools/HUBS-CONTRACT.md "Kit 1.6"). Skyy 2026-10-15 (docs/answered/ui.md): "so the menu item in my hand opens to an overview page. and all
the pages and menus are all tied together in there, so we have 1 unified menu for everything", then (UNIFIED MENU LAYOUT) "combined D and
A ... lets use a customizable grid in the center for the shortcuts. and build the overview around it, with the bub row up top. (so i can
still place the teleports at the center so i open it, click teleport, then make island the center of that so i can open it, click twice,
and be at my island without moving the mouse." + tabs "Icon first, themed later" + "have a way to remove and add them" + "add ones for the
overall menu that replace them by default. so instead of identify and reforge, you have smithing" + "id do skills as the default one".
  1. HOME (the menu item, the double-tap crouch hotkey, /skymenu): row 1 = the hubs (kit 1.6 HubBar.build2, Home active) + YOU (name,
     class, profile, Overall Level + bar, coins, bank, health, mana - missing ones left out; click = Character > Stats) + a 7 x 5
     SHORTCUT GRID whose centre slot sits on the screen spot slot 13 of the old 9 x 6 grid had (page centre + 4 px down: the same
     geometry, asserted) + RIGHT NOW (home:alert:<mod> Functions -> up to 3 'text|hub:tab' lines each; hidden when empty; SkyyMenu
     publishes home:alert:SkyyMenu: "your menu changed" after the one-time update, settings that cannot be read) + the foot row (the info
     line, Edit shortcuts, Close). Default grid: the 7 hubs one step around the centre, the centre = Teleport (World > Teleport).
  2. EDIT SHORTCUTS (Home and Teleport): click a tile = pick it up; another slot = swap / move; Remove; an empty slot = the + Add list
     (paged: every hub, every hub tab, every 0.3.28 tile, every teleport target); Reset; admins: Set default / Clear default (the server default); Old tiles back
     (after the update). No dragging - every text says so. Saved at once per account (Skyy_SkyyMenu/layouts/<uuid>.properties, extended
     backward-compatibly: _v=1 + the 0.3.28 tile lines stay, so a rollback reads the old layout).
  3. ONE-TIME UPDATE of saved layouts (players' + layout-default.properties): hubs replace the old tiles they cover (Hubs-Spec 1.3 table;
     a hub takes the slot of its first covered tile in reading order that maps inside the 7 x 5 grid), the other tiles keep their offset
     from the centre (9 x 6 -> 7 x 5; outside = waits in + Add, never lost), Hover Tooltips goes (Settings > General has it). Run-once
     marker _home, the old line kept as _old, a verified History copy in config-history/ before the first write, a config-changes.log line
     (status done; Undo = Edit shortcuts > Old tiles back). A removed tile never comes back by itself.
     Fix round (critics): a hub replaces a tile ONLY when that tile's own page is published as the hub's tab on this server right now
     (else the tile stays itself - no working tile becomes a "coming soon" stub); the server default's update waits for the first join
     (at setup no other mod has published its tabs); the update APPENDS its lines to the old file's exact bytes in its own line ending
     (PROJECT-RULES 4); one History copy per file even when the write is retried, and a History copy that fails 3 times no longer blocks
     saving; the History index line goes to config-history/SkyyMenu-layouts-index.log (the kit's index.log compaction drops foreign ids);
     a file written for a player with no 0.3.28 layout carries the full 0.3.28 layout D (a rollback shows layout D). DEVIATION (kept,
     recorded here): Server Setup shows the change-log line without an Undo button - a layout is not a settings row; the in-game Undo is
     Edit shortcuts > Old tiles back (a player) / Old default (admins: the server default), and the old lines stay in the file. Info
     line: 2 wrapped lines, every text width-checked.
     Fix round 2 (critics): a hub whose covered tiles ALL sat outside the 7 x 5 grid goes on the free slot nearest its first covered tile
     (Skyy's layout: Social + Settings no longer vanish); admins get "Old default" (the server default's Undo); a player with no 0.3.28
     file on a server with a custom 0.3.28 default gets the DEFAULT's tile lines as rollback lines (not layout D); a 0.3.28 file read
     again in the same session (a hand-restored .bak) gets its own History copy again; + Add lists a page once (an old tile and the hub
     tab it is are the same page, either one on the grid counts as placed); a hub's DEFAULT tab now beats its last tab (Skyy 2026-10-15
     "id do skills as the default one": Character always opens on Skills; hubs without a default keep the last-tab memory); the
     tooltips-off hint names Settings, General.
  4. TELEPORT (World > Teleport): the same 7 x 5 grid geometry, so its centre slot is the same screen spot; its layout is customizable the
     same way (My Island / Hub / Spawn / each warp; default My Island | Hub (centre) | Spawn); unplaced warps fill rows 4-5 (paged).
  5. Every Menu page (Stats, Teleport, Players, Settings, Mods, Server Setup) uses the kit 1.6 row shell (row 1 in place of "< Menu" + the
     title: no page grows); hub:def:<hub> carries the default tab (Character -> skills) + hub:def:home; Settings > "Edit shortcuts"
     (was Menu layout) opens Home in edit mode. The 0.3.28 9 x 6 main view is retired (Home replaces it).
Saved data: layouts/<uuid>.properties + layout-default.properties (format above; one-time update). ROUND_PINS = {}.
Rollback to 0.3.28: safe - it reads the kept 0.3.28 tile lines (a migrated player sees the old layout; g./t. lines are ignored).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.28.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.29.py")
CR, LF = chr(13), chr(10)
raw = open(src, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.28"' in s and "0.3.28: HUBS H2 (notes" in s and "0.3.29" not in s, "not the generated 0.3.28 script"
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    assert new, "a change never deletes outright (the undo check needs the new text)"
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


def block(start, end):
    """the unique text from `start` up to and including `end` (both must be unique, in that order)"""
    assert s.count(start) == 1, "block start count %d: %s" % (s.count(start), start[:120])
    i = s.index(start)
    j = s.index(end, i)
    return s[i:j + len(end)]


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.28: HUBS H2 (notes''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.29: UNIFIED MENU U1 (notes: tools/menu_0_3_29_patch.py; research/Unified-Menu-Plan.md; kit skyyui 1.6 tools/HUBS-CONTRACT.md; Skyy
       2026-10-15 "1 unified menu for everything" + "combined D and A ... a customizable grid in the center for the shortcuts ... with the
       bub row up top"): Home (row 1 hubs, You, the 7 x 5 shortcut grid whose centre is the old slot 13 screen spot, Right now, Edit
       shortcuts / Close) replaces the 9 x 6 main view; Edit shortcuts (pick up / swap / Remove / + Add / Reset / server default / Old tiles
       back); the one-time layout update (hubs replace covered tiles, History copy, _old, run-once _home); the Teleport page on the same
       grid geometry with its own customizable layout; every Menu page in the kit 1.6 row shell; hub:def default tabs + hub:def:home;
       home:alert:SkyyMenu. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.29.py.
0.3.28: HUBS H2 (notes''')
rep('VERSION = "0.3.28"\n', 'VERSION = "0.3.29"\n')

# ---------------------------------------------------------------------------------------------------------------- MENU DATA: Home + shortcuts
DATA29 = r'''
# ---- 0.3.29: UNIFIED MENU U1 (research/Unified-Menu-Plan.md section 0; Skyy 2026-10-15 "combined D and A"). The Home page's 7 x 5 SHORTCUT
# GRID (centre slot 17 = the old 9 x 6 slot 13's screen spot) and the Teleport page's grid. A shortcut is a KEY (saved as text):
#   hub:<hub>            a hub (opens its default tab, else its last tab, else its first tab: kit 1.6 HubBar.pickTab)
#   tab:<hub>:<tab>      one hub tab (= one page: "every page keeps its own shortcut, hidden by default")
#   tile:<0.3.28 key>    an old menu tile (its 0.3.28 action, visibility rule and text)
#   tp:island|hub|spawn  a teleport target;  warp:<name>  a warp
HG_COLS, HG_ROWS = 7, 5
HG_N = HG_COLS * HG_ROWS
HG_CR, HG_CC = 2, 3                          # the centre: row 2, column 3 = slot 17
HG_CENTRE = HG_CR * HG_COLS + HG_CC
OLD_COLS, OLD_CR, OLD_CC = 9, 1, 4            # the 0.3.28 main view: 9 wide, its centre (the mouse spot) row 1 column 4 = slot 13
assert HG_CENTRE == 17 and OLD_CR * OLD_COLS + OLD_CC == 13
HUB_DEFTAB = {"character": "skills"}          # Skyy 2026-10-15 "id do skills as the default one for this" (hub:def element 3)
HOME_TITLE, HOME_ICON = "Home", MENU_ITEM_ID  # hub:def:home - row 1's first button wears the SkyWynn Menu item itself
OWN_LABEL = {"layout": "Edit shortcuts"}      # Settings > Menu layout is now Edit shortcuts (it opens Home in edit mode)
HUB_BLURB = {"character": "Character hub: your stats, skills, trees, class, pets, accessories, collections and profiles.",
             "storage": "Storage hub: the Void, Requip, your Vault and the Bank.",
             "market": "Market hub: the Bazaar, the Auction House and Merchants.",
             "smithing": "Smithing hub: gear, recipes, reforge, upgrade and identify.",
             "world": "World hub: teleports, your island, exploring and quests.",
             "social": "Social hub: players online, your party and your guild.",
             "settings": "Settings hub: your settings, the HUD, Edit shortcuts and (admins) Server Setup."}
assert sorted(HUB_BLURB) == sorted(SUI.HUBS) and all(len(v) <= 96 for v in HUB_BLURB.values())
# THE ONE-TIME UPDATE (Hubs-Spec 1.3 table): each 0.3.28 tile -> the hub that covers it ("" = not covered: keeps its place; "-" = retired;
# "=<key>" = becomes exactly that shortcut). Skyy 2026-10-15: "so instead of identify and reforge, you have smithing".
MIG = {"yourprofile": "character", "pets": "character", "skills": "character", "accessorybag": "character", "collections": "character",
       "islandmenu": "world", "crafting": "smithing", "reforge": "smithing", "identify": "smithing",
       "bank": "storage", "vault": "storage", "pocketdimension": "storage", "wardrobe": "storage",
       "bazaar": "market", "auctionhouse": "market", "players": "social", "party": "social", "guild": "social",
       "settings": "settings", "hudeditor": "settings", "teleport": "=tab:world:teleport", "hovertooltips": "-",
       "mods": "", "serversetup": ""}
# the tab each old tile IS (Hubs-Spec 1.3): a tab shortcut wears that tile's icon; other tabs wear their hub's icon
TILE_TAB = {"yourprofile": "character:stats", "pets": "character:pets", "skills": "character:skills", "accessorybag": "character:accessories",
            "collections": "character:collections", "islandmenu": "world:island", "crafting": "smithing:recipes", "reforge": "smithing:reforge",
            "identify": "smithing:identify", "bank": "storage:bank", "vault": "storage:vault", "pocketdimension": "storage:pocket",
            "wardrobe": "storage:requip", "bazaar": "market:bazaar", "auctionhouse": "market:auctions", "players": "social:players",
            "party": "social:party", "guild": "social:guild", "settings": "settings:settings", "hudeditor": "settings:hud",
            "mods": "settings:mods", "serversetup": "settings:setup", "teleport": "world:teleport"}
# the default Home grid: the centre = Teleport (World > Teleport), the 7 hubs one step around it (Skyy: "the hub row" + "plus shape")
BUILTIN_HOME = {17: "tab:world:teleport", 10: "hub:character", 24: "hub:market", 16: "hub:storage", 18: "hub:smithing",
                9: "hub:social", 11: "hub:settings", 23: "hub:world"}
BUILTIN_TP = {16: "tp:island", 17: "tp:hub", 18: "tp:spawn"}        # the Teleport page: My Island | Hub (centre, as today) | Spawn
TP_KEYS = {"tp:island": "cmdc:island", "tp:hub": "cmdc:hub", "tp:spawn": "spawn"}   # -> the 0.3.28 Teleport view entry with that action
TP_AUTO = list(range(3 * HG_COLS, HG_N))      # warps nobody placed fill the free slots of rows 4 and 5 (paged)
HOME_TXT = {
    "HT_HINT": "Hover a shortcut to read it, click to use it. Edit shortcuts adds, moves and removes them (no dragging).",
    # fix round 2: the Hover Tooltips tile is gone, so the tooltips-off hint names where the switch is (Settings > General)
    "HT_HINT_OFF": "Tooltips are off - turn them on in Settings, General. Click a shortcut to use it. Edit shortcuts: no dragging.",
    "HT_EDIT": "EDITING - no dragging: click a tile, then a slot (they swap), or Remove. Click an empty slot to add one.",
    "HT_EDIT_START": "Edit mode - no dragging: click a tile, then click a slot (they swap). Empty slot = add. Done to finish.",
    "HT_ADD": "Pick what goes in this slot: any hub, page, old tile or teleport. Cancel goes back.",
    "HT_TP_HINT": "Click a place to go there. Edit puts your favourite in the middle, under your mouse (no dragging).",
    "HT_MID": "Shortcuts", "HT_MID_EDIT": "Editing shortcuts - no dragging", "HT_MID_ADD": "Add a shortcut",
    "HT_TILE_BODY": "Click to pick it up, then click the slot where it should go (the two swap).\nNo dragging - click, then click. Remove takes it off.",
    "HT_PICK_FOOT": "Click to pick it up",
    "HT_SWAP_FOOT": "Click to swap it with the picked-up tile",
    "HT_SEL_BODY": "Picked up - now click the slot where it should go.\nClick it again to cancel, or press Remove.",
    "HT_SEL_FOOT": "Click again to cancel",
    "HT_EMPTY_NAME": "Empty slot",
    "HT_EMPTY_ADD": "A free slot. Click it to add a shortcut here:\nany hub, any page, an old tile or a teleport.",
    "HT_EMPTY_MOVE": "A free slot. Click it to move the picked-up tile here.",
    "HT_EMPTY_FOOT_ADD": "Click to add a shortcut",
    "HT_EMPTY_FOOT_MOVE": "Click to move it here",
    "HT_NONE_LEFT": "Every shortcut is on your grid already.",
    "HT_YOU_TITLE": "You", "HT_YOU_HINT": "Click for all your stats", "HT_NOW_TITLE": "Right now",
    "AL_MIG": "Menu updated: hubs replaced old tiles", "AL_SET": "Your settings could not be read",
}
assert "no dragging" in HOME_TXT["HT_EDIT"].lower() and "no dragging" in HOME_TXT["HT_TILE_BODY"].lower() \
    and "no dragging" in HOME_TXT["HT_EDIT_START"].lower() and "no dragging" in HOME_TXT["HT_MID_EDIT"].lower() \
    and all("no dragging" in HOME_TXT[_k].lower() for _k in ("HT_HINT", "HT_HINT_OFF", "HT_TP_HINT")), \
    "0.3.29 (Skyy LOCKED 2026-10-10): every edit text - and the hint beside the Edit button, before it is clicked - says dragging does not work"
AL_MAX, AL_SHOW = 40, 8                      # an alert line: at most 40 characters (fits its 252 px button at 11 px); at most 8 lines (3 per mod)
'''
rep('''assert all(len(HUB_SOON[_h]) <= 100 for _h in SUI.HUBS), "0.3.28: the coming-soon lines stay short"
''', '''assert all(len(HUB_SOON[_h]) <= 100 for _h in SUI.HUBS), "0.3.28: the coming-soon lines stay short"
''' + DATA29)

# the build-time checks of the 0.3.29 tables (after ENTRIES / E_KEY exist: right after the layout-editor block)
CHECK29 = r'''
# ---- 0.3.29: the shortcut tables against the 0.3.28 tiles (every main tile has its update rule; the defaults are valid keys)
for _k, _v in HOME_TXT.items():
    for _ln in _v.split("\n"):
        assert txt(_ln) == _ln and len(_ln) <= 110, "0.3.29: Home text %s not safe / too long: %s" % (_k, _ln)
assert all(txt(v) == v for v in HUB_BLURB.values())
_mk29 = [k for k in E_KEY if k]
assert sorted(MIG) == sorted(_mk29), "0.3.29: every 0.3.28 tile has an update rule: %s" % sorted(set(MIG) ^ set(_mk29))
assert all(v in ("", "-") or v.startswith("=") or v in SUI.HUBS for v in MIG.values())
assert sorted(set(v for v in MIG.values() if v in SUI.HUBS)) == sorted(h for h in SUI.HUBS), "0.3.29: every hub covers at least one tile"
assert sorted(TILE_TAB) == sorted(k for k in _mk29 if k != "hovertooltips")
_tabs29 = set("%s:%s" % (h, t) for h, t, _o, _m, _l, _c in SUI.HUB_TABS)
assert all(v in _tabs29 for v in TILE_TAB.values()), "0.3.29: TILE_TAB names contract tabs only"
assert BUILTIN_HOME[HG_CENTRE] == "tab:world:teleport" and sorted(v[4:] for v in BUILTIN_HOME.values() if v.startswith("hub:")) == sorted(SUI.HUBS), \
    "0.3.29: the default Home = Teleport in the centre + the 7 hubs"
assert all(abs(s_ // HG_COLS - HG_CR) <= 1 and abs(s_ % HG_COLS - HG_CC) <= 1 for s_ in BUILTIN_HOME), "0.3.29: the hubs sit one step around the centre"
assert BUILTIN_TP[HG_CENTRE] == "tp:hub" and sorted(BUILTIN_TP.values()) == sorted(TP_KEYS)
TPK_E = [[i for i, e in enumerate(ENTRIES) if e[0] == "tp" and e[6] == TP_KEYS[k]] for k in sorted(TP_KEYS)]
assert all(len(x) == 1 for x in TPK_E), "0.3.29: each teleport key is one Teleport-view entry"
print("0.3.29 shortcuts: home default", BUILTIN_HOME, "- teleport default", BUILTIN_TP, "- update rules", len(MIG))
'''
# simplify pass 1: the retired 0.3.17 9 x 6 layout editor's controls, icons and texts go (Home's Edit shortcuts replaced it; nothing reads
# them any more) - kept: the tile keys (E_KEY: the saved files), LAY_GRID (the 0.3.28 tile lines), ICON_EMPTY (the empty-slot marker),
# KEPT_MSG + EDIT_WAIT (the new editor's answers)
rep(block('''# 0.3.17: THE MENU LAYOUT EDITOR (Skyy 2026-10-10: "can you make a menu editor''',
          '''print("0.3.17 layout editor: tile keys", ", ".join(_mk), "- controls", EDIT_CTRL, "- icons", EDIT_ICONS)
'''), '''# 0.3.17: THE MENU LAYOUT EDITOR's saved files (0.3.29: the 9 x 6 editor is retired - Home's Edit shortcuts replaces it). Tile keys (E_KEY) =
# the tile name, lower case, letters / digits only - the 0.3.28 tile lines of Skyy_SkyyMenu/layouts/<uuid>.properties and
# Skyy_SkyyMenu/layout-default.properties use them; rows 0 - 4 (slots 0 - 44) held the layout.
LAY_GRID = 45                                 # slots 0 - 44 can hold a tile
ICON_EMPTY = "Editor_Empty"                   # an empty slot in edit mode
EDIT_TXT = {
    # fix round: a hidden tile's slot is NOT marked in edit mode (no "Kept slot" - restricted tiles stay fully hidden, the 2026-09-25 rule);
    # it is simply not clickable. KEPT_MSG only answers a stale / forged click on it and names nothing.
    "KEPT_MSG": "That slot cannot be used - pick a tile or a slot with a glass marker.",
    "EDIT_WAIT": "Your saved layout cannot be read right now - nothing changed. Try again soon.",
}
for _k, _v in EDIT_TXT.items():
    for _ln in _v.split("\\n"):
        assert txt(_ln) == _ln and len(_ln) <= 80, "0.3.17: editor text %s line too long / not safe: %s" % (_k, _ln)
need_item(ICON_EMPTY)
need_icon(ICON_EMPTY)
_ekey = lambda n: re.sub(r"[^a-z0-9]", "", n.lower())
E_KEY = [_ekey(e[3]) if e[0] == "main" else "" for e in ENTRIES]
_mk = [k for k in E_KEY if k]
assert len(_mk) == len(set(_mk)) == len([e for e in ENTRIES if e[0] == "main"]) and all(re.match(r"^[a-z][a-z0-9]{2,31}$", k) for k in _mk), \\
    "0.3.17: every main tile has a unique saved-file key: %s" % _mk
assert all(e[1] < LAY_GRID for e in ENTRIES if e[0] == "main"), "0.3.17: the layout lives in rows 0 - 4"
print("0.3.17 layout tile keys", ", ".join(_mk))
''' + CHECK29)
rep('''F(dat, "public static final int EDIT_SLOT = %d;" % EDIT_SLOT)
for _k, _v in sorted(EDIT_CTRL.items()):
    F(dat, "public static final int CTRL_%s = %d;" % (_k.upper(), _v))
for _k, _v in sorted(EDIT_ICONS.items()):
    F(dat, "public static final String ICON_%s = %s;" % (_k, jstr(_v)))
''', '''F(dat, "public static final String ICON_EMPTY = %s;" % jstr(ICON_EMPTY))   # simplify pass 1: the 9 x 6 editor's slots + icons went
''')

# ---------------------------------------------------------------------------------------------------------------- the Stats shell: row 1
rep('''    sh = SUI.hub_shell("SkyyStatF", ST_W, ST_H, "character", body_id="SkyyStat")    # 0.3.28: Character > Stats (was page_shell "Your Stats")
''', '''    sh = SUI.hub_shell("SkyyStatF", ST_W, ST_H, "character", body_id="SkyyStat", row=True)    # 0.3.29: kit 1.6 row 1 (0.3.28: Character > Stats)
''')

# ---------------------------------------------------------------------------------------------------------------- the page shells + Home + Teleport
_hb = block('''# ================= 0.3.28 HUBS H2: the hub page shells (kit skyyui 1.5 hub_shell in the Sky Window theme) =================
''', '''assert "SkyyStatF" in ST_HUB_JAVA and '"character", "stats", 1066,' in ST_HUB_JAVA and ST_HUB_JAVA.endswith(", 3);")
''')
SHELLS29 = r'''# ================= 0.3.29 UNIFIED MENU: every Menu page in the kit 1.6 ROW SHELL + the Home page + the Teleport page =================
# kit 1.6 (tools/HUBS-CONTRACT.md "Kit 1.6"): row 1 = Home + the hubs in the 38 px title bar where "< Menu" + the title were, so no page
# grows (assert_hub_page as in 0.3.28); the tab strip stays row 2. Clicks: HubBar.route (MenuHub.click) - "hub:h:home" = Home in place.
assert SUI.HUB_THEME == "sky" and SUI.THEME_PAD["sky"] == 24 and SUI.KIT_VERSION == "1.5" and SUI.KIT_HUB_VERSION == "1.6", \
    "0.3.29: kit skyyui 1.6 (KIT_VERSION stays 1.5), hub pages in the sky theme"
HUB_PAD = SUI.THEME_PAD["sky"]
MH_W, MH_H = GW + 2 * HUB_PAD, SUI.MAX_PAGE_H        # the classic menu views (Players, a player, Mods): 804 x 980 (the 756 px grid)
MENU_HUB_SH = dict((h, SUI.hub_shell("SkyyMenuH", MH_W, MH_H, h, body_id="SkyyMenu", row=True)) for h in ("social", "settings"))
STG_HUB_SH = SUI.hub_shell("SkyyStgH", SPW, SPH, "settings", body_id="SkyyStg", row=True)
ADM_HUB_SH = SUI.hub_shell("SkyyAdmH", APW, APH, "settings", body_id="SkyyAdm", row=True)
for _h, _sh in MENU_HUB_SH.items():
    assert _sh.inner_w == GW and _sh.inner_h == 22 + 256 + 8 + (GH + 6) + 46, "0.3.29: the %s menu view fits its row shell" % _h
    assert _sh.tabs_w == GW and _sh.parts == SUI.HUB_PART_ROW | SUI.HUB_PART_CLOSE and _sh.row_w == MH_W - 50
assert STG_HUB_SH.inner_w == SPI and STG_HUB_SH.inner_h == 26 + SFIND_H + 58 + 58 + 8 + 40 + SET_ROWS * 64 + 26 + 62, "0.3.29: settings fit"
assert ADM_HUB_SH.inner_w == A_INNER and ADM_HUB_SH.inner_h == 26 + A_BODY + 30 + 62, "0.3.29: server setup fits"

# ---- HOME (the overview page): row 1 | YOU | the 7 x 5 shortcut grid | RIGHT NOW | the foot row. Ids start with SkyyM (the grid keeps
# the id #SkyyMGrid of every menu view: the same slot binding, clearGrid and click path).
HG_W, HG_H = SLOT * HG_COLS, SLOT * HG_ROWS          # 588 x 420 (84 px slots, as the 0.3.28 grid)
HOME_SIDE, HOME_GAP, HOME_MAIN_H = 300, 16, 460
HOME_MIDT_H, HOME_MIDGAP, HOME_GRID_TOP = 32, 5, 3
HOME_FOOT_H, HOME_FOOTGAP = 46, 8
HINFO_FS = 14                                        # the Home info line: 14 px, wraps to TWO lines in its 40 px (the kit status_line pattern)
HOME_W = 2 * HOME_SIDE + 2 * HOME_GAP + HG_W + 2 * HUB_PAD
HOME_H = 616
HOME_SH = SUI.hub_shell("SkyyMHm", HOME_W, HOME_H, "home", row=True, body_id="SkyyMHome")
HOME_FOOT_W = HOME_SH.inner_w
assert (HOME_W, HOME_SH.inner_w) == (1268, 1220) and HOME_MAIN_H + HOME_FOOTGAP + HOME_FOOT_H <= HOME_SH.inner_h
# ---- TELEPORT (World > Teleport): the tab strip, a status line, the same grid (centred by an 84 px lead), a two-line info box, the foot
TP_W, TP_H = GW + 2 * HUB_PAD, 704
TP_HINT_H, TP_GAP_H, TP_LEAD, TP_INFO_H = 26, 3, (GW - HG_W) // 2, 50
TP_SH = SUI.hub_shell("SkyyMTp", TP_W, TP_H, "world", row=True, body_id="SkyyMTpB")
TP_FOOT_W = TP_SH.inner_w
assert TP_LEAD == 84 and TP_SH.tabs_w == GW and SUI.HUB_BAR_H + TP_HINT_H + TP_GAP_H + (HG_H + HOME_GRID_TOP) + 8 + TP_INFO_H + 8 + HOME_FOOT_H <= TP_SH.inner_h + SUI.HUB_BAR_H
# THE CENTRE SLOT UNDER THE MOUSE (Skyy: "open it, click twice, and be at my island without moving the mouse"). A page opens centred
# on the screen with the mouse at the screen centre; 0.3.28's slot 13 (row 1, col 4 of the 9 x 6 grid) sat at the page centre + (0, +4)
# - computed here from the 0.3.28 markup itself. Home's and Teleport's centre slot 17 must land on exactly that offset.
_hpx = lambda mk: int(re.search(r"Height: (\d+)", mk).group(1))
OLD_SLOT13 = (22 + OLD_CC * SLOT + SLOT // 2 - PW // 2,
              14 + _hpx(UI["ACCENT"]) + _hpx(UI["TITLE"]) + _hpx(UI["HINT"]) + _hpx(UI["INFOBOX"]) + _hpx(UI["GAP"]) + 3 + OLD_CR * SLOT + SLOT // 2 - PH // 2)
assert "Top: 3" in UI["GRID"] and "Padding: (Horizontal: 22, Vertical: 14)" in UI["ROOT"]
HOME_C = (HUB_PAD + HOME_SIDE + HOME_GAP + HG_CC * SLOT + SLOT // 2 - HOME_W // 2,
          SUI.TITLE_H + HUB_PAD + HOME_MIDT_H + HOME_MIDGAP + HOME_GRID_TOP + HG_CR * SLOT + SLOT // 2 - HOME_H // 2)
TP_C = (HUB_PAD + TP_LEAD + HG_CC * SLOT + SLOT // 2 - TP_W // 2,
        SUI.TITLE_H + HUB_PAD + SUI.HUB_BAR_H + TP_HINT_H + TP_GAP_H + HOME_GRID_TOP + HG_CR * SLOT + SLOT // 2 - TP_H // 2)
assert OLD_SLOT13 == (0, 4) and HOME_C == OLD_SLOT13 and TP_C == OLD_SLOT13, "0.3.29: the centre slot keeps slot 13's screen spot %s / %s / %s" % (
    OLD_SLOT13, HOME_C, TP_C)
_K = SUI.THEME["sky"]
_gridmk = lambda tips: ("ItemGrid #SkyyMGrid { Anchor: (Horizontal: 0, Top: %d, Width: %d, Height: %d); SlotsPerRow: %d; AreItemsDraggable: false; %s"
                        "Style: (SlotSize: %d, SlotIconSize: 62, SlotSpacing: 0); }" % (HOME_GRID_TOP, HG_W, HG_H, HG_COLS, "" if tips else "InfoDisplay: None; ", SLOT))
_ALAB = ("(FontSize: 14, TextColor: %s, RenderBold: true, HorizontalAlignment: Start, VerticalAlignment: Center, ShrinkTextToFit: true, "
         "MinShrinkTextToFitFontSize: 11)" % SUI.color("rowName"))
UI29 = {
    "HMAIN": SUI.group("SkyyMHmMain", "Left", h=HOME_MAIN_H),
    "HYOU": "Button #SkyyMHmYou { Anchor: (Width: %d, Height: %d); LayoutMode: Top; Padding: (Full: 14); Style: ButtonStyle(Default: (Background: %s), "
            "Hovered: (Background: %s), Pressed: (Background: %s), Sounds: %s); }" % (HOME_SIDE, HOME_MAIN_H, _K["panel"], _K["card"], _K["inset"], SUI.sounds("light")),
    "HYT": SUI.label("SkyyMHmYT", HOME_TXT["HT_YOU_TITLE"], "panelTitle", h=26),
    "HYN": SUI.label("SkyyMHmYN", "", "heading", h=30, size=20, wrap=False),
    "HYBAR0": "Group #SkyyMHmYBar { Anchor: (Width: %d, Height: 10, Bottom: 6); Background: %s; Group #SkyyMHmYFill { Anchor: (Left: 0, Width: " % (
        HOME_SIDE - 28, SUI.color("progressTrack")),
    "HYBAR1": ", Height: 10); Background: %s; } }" % SUI.color("progressFill"),
    "HYH": SUI.label("SkyyMHmYH", HOME_TXT["HT_YOU_HINT"], "caption", h=24, size=14),
    "HSP16": SUI.spacer(w=HOME_GAP),
    "HMID": SUI.group("SkyyMHmMid", "Top", w=HG_W, h=HOME_MAIN_H),
    "HMIDT": SUI.label("SkyyMHmMidT", "", "heading", h=HOME_MIDT_H, size=18, align="Center", wrap=False),
    "HGAP5": SUI.spacer(h=HOME_MIDGAP),
    "HGW": "Group #SkyyMGW { Anchor: (Width: %d, Height: %d); }" % (HG_W, HG_H + HOME_GRID_TOP),
    "HGRID": _gridmk(True),
    "HGRIDNT": _gridmk(False),
    "HNOW": "Group #SkyyMHmNow { Anchor: (Width: %d, Height: %d); LayoutMode: Top; Padding: (Full: 14); Background: %s; }" % (HOME_SIDE, HOME_MAIN_H, _K["panel"]),
    "HNOWE": "Group #SkyyMHmNow { Anchor: (Width: %d, Height: %d); }" % (HOME_SIDE, HOME_MAIN_H),
    "HNOWT": SUI.label("SkyyMHmNowT", HOME_TXT["HT_NOW_TITLE"], "panelTitle", h=26),
    "HGAP8": SUI.spacer(h=HOME_FOOTGAP),
    "HFOOT": "Group #SkyyMHmFoot { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: 3); }" % HOME_FOOT_H,
    "HINFO0": "Label #SkyyMHmInfo { Anchor: (Width: ",
    "HINFO1": ', Height: 40); Padding: (Horizontal: 8); Text: ""; Style: %s; }' % SUI.text_style(HINFO_FS, "rowName", wrap=True),
    "FSP": SUI.spacer(w=10),
    "THINT": 'Label #SkyyMTpHint { Anchor: (Height: %d); Text: ""; Style: (FontSize: 15, RenderBold: true, TextColor: #ffd27f, HorizontalAlignment: Center, '
             'VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }' % TP_HINT_H,
    "TGAP3": SUI.spacer(h=TP_GAP_H),
    "TROW": SUI.group("SkyyMTpRow", "Left", h=HG_H + HOME_GRID_TOP),
    "TLEAD": SUI.spacer(w=TP_LEAD),
    "TINFO": "Group #SkyyMTpInfo { Anchor: (Height: %d); LayoutMode: Top; Padding: (Horizontal: 14, Vertical: 4); Background: %s; }" % (TP_INFO_H, _K["inset"]),
    "TIN": SUI.label("SkyyMTpIN", "", "rowName", h=22, size=16, wrap=False),
    "TID": SUI.label("SkyyMTpID", "", "default", h=20, size=14, wrap=False),
    "TFOOT": "Group #SkyyMTpFoot { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: 3); }" % HOME_FOOT_H,
}
UI29_HYL = [SUI.label("SkyyMHmYL%d" % i, "", "default", h=26, size=16, col="rowName", wrap=False) for i in range(7)]
UI29_HA = ['TextButton #SkyyMHmA%d { Anchor: (Height: 44, Bottom: 6); Padding: (Horizontal: 10); Text: ""; Style: TextButtonStyle(Default: (Background: %s, '
           'LabelStyle: %s), Hovered: (Background: %s, LabelStyle: %s), Pressed: (Background: %s, LabelStyle: %s), Sounds: %s); }' % (
               i, _K["row"], _ALAB, _K["rowHovered"], _ALAB, _K["rowSelected"], _ALAB, SUI.sounds("light")) for i in range(AL_SHOW)]
# the foot buttons (one table, both pages): word -> (label, width, kind, sound). The event is a = "f<word>".
FB = [("hedit", "Edit shortcuts", 190, "secondary", None), ("close", "Close", 130, "secondary", "cancel"),
      ("prev", "< Prev", 110, "secondary", None), ("next", "Next >", 110, "secondary", None),
      ("eremove", "Remove", 100, "destructive", None), ("ereset", "Reset", 90, "secondary", None),
      ("esrv", "Set default", 120, "secondary", None), ("estd", "Clear default", 135, "secondary", None),
      ("eold", "Old tiles back", 135, "secondary", None), ("edone", "Done", 90, "primary", None),
      # fix round 2: an admin's in-game Undo of the SERVER DEFAULT's one-time update (PROJECT-RULES 4): the old default's tiles back
      # (shown on Home edit while the server default keeps an _old line and no tile is picked up)
      ("edold", "Old default", 120, "secondary", None),
      ("aprev", "< Prev", 110, "secondary", None), ("anext", "Next >", 110, "secondary", None), ("acancel", "Cancel", 120, "secondary", "cancel")]
FB_GAP = 10
_fbmk = lambda pre, w_, lab, wid, kind, snd: 'TextButton #%sF%s { Anchor: (Width: %d, Height: 40); Padding: (Horizontal: 8); Text: "%s"; %s }' % (
    pre, w_, wid, lab, SUI.theme_button_style(kind, "small", theme="sky", sound=snd))
UI29_FBH = [_fbmk("SkyyMHm", w_, lab, wid, kind, snd) for w_, lab, wid, kind, snd in FB]
FB_TW = [110 if w_ == "hedit" else wid for w_, _l, wid, _k, _s in FB]
UI29_FBT = [_fbmk("SkyyMTp", w_, "Edit" if w_ == "hedit" else lab, tw, kind, snd) for (w_, lab, _wid, kind, snd), tw in zip(FB, FB_TW)]
for _w, _l, _wid, _k, _s in FB:
    assert SUI.text_width(_l, 14, bold=True, upper=True) <= _wid - 16, "0.3.29: foot button %s fits" % _l
_mode_words = {"home": [["hedit", "close"], ["eremove", "ereset", "esrv", "estd", "eold", "edone"], ["ereset", "esrv", "estd", "eold", "edold", "edone"],
                        ["aprev", "anext", "acancel"]],
               "tp": [["hedit", "prev", "next", "close"], ["eremove", "ereset", "esrv", "estd", "edone"], ["aprev", "anext", "acancel"]]}
_fbw = dict((w_, wid) for w_, _l, wid, _k, _s in FB)
for _ws in _mode_words["home"]:
    assert HOME_FOOT_W - sum(_fbw[w_] + FB_GAP for w_ in _ws) >= 300, "0.3.29: the Home info line keeps 300 px in every foot row"
# fix round: EVERY text the Home info line can show fits its TWO wrapped lines (14 px) in the NARROWEST foot row (an admin in edit mode
# with Old tiles back and Old default - fix round 2: Old default only shows while no tile is picked up, so Remove and it never share a row) - the hints, the edit texts, every status literal of the page code below (a name in it counted
# as the longest tile or hub name; the literals of both ternary branches added up, so this over-counts), the coming-soon / fail / wait lines. 0.85 = the
# room a word wrap may waste. The Teleport hint line (one line, shrinks to 11 px bold) takes the same texts.
HINFO_ROOM = HOME_FOOT_W - max(sum(_fbw[w_] + FB_GAP for w_ in _ws) for _ws in _mode_words["home"]) - 16
TP_HINT_ROOM = TP_SH.inner_w
_name24 = max([_n for _k, _n in zip(E_KEY, E_NAME) if _k] + [SUI.HUB_DEFS[_h][0] for _h in SUI.HUBS], key=len)   # the longest tile / hub name
_src29 = open(os.path.abspath(__file__), encoding="utf8").read()
_msgs29 = [HOME_TXT[k] for k in ("HT_HINT", "HT_HINT_OFF", "HT_EDIT", "HT_EDIT_START", "HT_ADD", "HT_TP_HINT")]
_msgs29 += [EDIT_TXT["KEPT_MSG"], EDIT_TXT["EDIT_WAIT"], HUB_TXT_FAIL] + ["[%s] %s" % (SUI.HUB_DEFS[_h][0], HUB_SOON[_h]) for _h in SUI.HUBS]
_stl29 = re.findall(r'this\.status = ([^;\n]*);', _src29)
assert len(_stl29) >= 30, "0.3.29: the status lines are found (%d)" % len(_stl29)
for _st in _stl29:
    _lits = re.findall(r'"((?:[^"\\]|\\.)*)"', _st)
    if _lits:
        _msgs29.append(_name24.join([_x for _x in _lits if _x]))
for _m in _msgs29:
    assert SUI.text_width(_m, HINFO_FS) <= 2 * HINFO_ROOM * 0.85, "0.3.29: the Home info line fits 2 lines of %d px: %s (%d px)" % (
        HINFO_ROOM, _m, SUI.text_width(_m, HINFO_FS))
    assert SUI.text_width(_m, 11, bold=True) <= TP_HINT_ROOM, "0.3.29: the Teleport hint line fits at 11 px: %s" % _m
# the Right now lines: an AL_MAX-character line in capitals + "  >" fits its button (300 - 2 x 14 panel - 2 x 10 padding) at 11 px
assert SUI.text_width(("Abcd Efgh " * 6)[:AL_MAX] + "  >", 11, bold=True) <= HOME_SIDE - 28 - 20, "0.3.29: an alert line fits its button"
assert all(SUI.text_width(HOME_TXT[_k] + "  >", 11, bold=True) <= HOME_SIDE - 48 and len(HOME_TXT[_k]) <= AL_MAX for _k in ("AL_MIG", "AL_SET")), "0.3.29: SkyyMenu's own alerts fit"
print("0.3.29 info line: %d px (2 lines of %d px), %d texts checked; Teleport hint %d px" % (HINFO_ROOM, HINFO_FS, len(_msgs29), TP_HINT_ROOM))
_fbtw = dict(zip([f[0] for f in FB], FB_TW))
for _ws in _mode_words["tp"]:
    assert sum(_fbtw[w_] for w_ in _ws) + FB_GAP * (len(_ws) - 1) <= TP_FOOT_W, "0.3.29: the Teleport foot fits"
# every look of both pages, checked as pages (markup rules, parents, no duplicate id, proven properties only, kit textures only)
_hp = SUI.Appends(list(HOME_SH.appends))
_hp.append(("SkyyMHome", UI29["HMAIN"]))
_hp.append(("SkyyMHmMain", UI29["HYOU"]))
for _k in ("HYT", "HYN"):
    _hp.append(("SkyyMHmYou", UI29[_k]))
for _mk in UI29_HYL:
    _hp.append(("SkyyMHmYou", _mk))
_hp.append(("SkyyMHmYou", UI29["HYBAR0"] + "136" + UI29["HYBAR1"]))
_hp.append(("SkyyMHmYou", UI29["HYH"]))
_hp.append(("SkyyMHmMain", UI29["HSP16"]))
_hp.append(("SkyyMHmMain", UI29["HMID"]))
for _k in ("HMIDT", "HGAP5", "HGW"):
    _hp.append(("SkyyMHmMid", UI29[_k]))
_hp.append(("SkyyMGW", UI29["HGRID"]))
_hp.append(("SkyyMHmMain", UI29["HSP16"]))
_hp.append(("SkyyMHmMain", UI29["HNOW"]))
_hp.append(("SkyyMHmNow", UI29["HNOWT"]))
for _mk in UI29_HA:
    _hp.append(("SkyyMHmNow", _mk))
_hp.append(("SkyyMHome", UI29["HGAP8"]))
_hp.append(("SkyyMHome", UI29["HFOOT"]))
_hp.append(("SkyyMHmFoot", UI29["HINFO0"] + "400" + UI29["HINFO1"]))
for _mk in UI29_FBH:
    _hp.append(("SkyyMHmFoot", UI29["FSP"]))
    _hp.append(("SkyyMHmFoot", _mk))
_hp.extend(SUI.hub_row_preview("SkyyMHm", [(i, t, "Skyy_Menu") for i, t in zip(SUI.HUB_ROW_IDS, SUI.HUB_ROW_TITLES)], "home", HOME_SH.row_w))
SUI.check_page(_hp, "SkyyM")
SUI.assert_proven(_hp, what="Home page")
_hels = SUI.check_sky_paths(_hp)
assert {"Frame", "Header", "Panel", "CardFrame", "PanelInset", "Row", "Close", "Primary", "Tertiary"} <= set(_hels), "0.3.29: Home uses the sky kit: %s" % _hels
assert SUI.used_height(SUI.Appends([(p_, mk) for p_, mk in _hp if p_ == "SkyyMHome"]), "SkyyMHome") <= HOME_SH.inner_h, "0.3.29: the Home body fits"
_hp2 = SUI.Appends(list(HOME_SH.appends) + [("SkyyMHome", UI29["HMAIN"]), ("SkyyMHmMain", UI29["HNOWE"]), ("SkyyMHmMain", UI29["HMID"]),
                                            ("SkyyMHmMid", UI29["HGW"]), ("SkyyMGW", UI29["HGRIDNT"])])
SUI.check_page(_hp2, "SkyyM")
SUI.assert_proven(_hp2, what="Home page (no alerts, tooltips off)")
_tp = SUI.Appends(list(TP_SH.appends))
for _k in ("THINT", "TGAP3", "TROW"):
    _tp.append(("SkyyMTpB", UI29[_k]))
_tp.append(("SkyyMTpRow", UI29["TLEAD"]))
_tp.append(("SkyyMTpRow", UI29["HGW"]))
_tp.append(("SkyyMGW", UI29["HGRID"]))
_tp.append(("SkyyMTpB", UI29["HGAP8"]))
_tp.append(("SkyyMTpB", UI29["TINFO"]))
_tp.append(("SkyyMTpInfo", UI29["TIN"]))
_tp.append(("SkyyMTpInfo", UI29["TID"]))
_tp.append(("SkyyMTpB", UI29["HGAP8"]))
_tp.append(("SkyyMTpB", UI29["TFOOT"]))
for _mk in UI29_FBT:
    _tp.append(("SkyyMTpFoot", _mk))
_tp.extend(SUI.hub_row_preview("SkyyMTp", [(i, t, "Skyy_Menu") for i, t in zip(SUI.HUB_ROW_IDS, SUI.HUB_ROW_TITLES)], "world", TP_SH.row_w))
_tp.extend(SUI.hub_bar_preview2("SkyyMTp", [(t, l, o) for t, o, _m, l, _c in SUI.hub_tabs("world")], "teleport", TP_SH.tabs_w))
SUI.check_page(_tp, "SkyyM")
SUI.assert_proven(_tp, what="Teleport page")
assert {"Frame_World", "Header", "PanelInset", "Tab_Selected", "Close"} <= set(SUI.check_sky_paths(_tp))
assert SUI.used_height(SUI.Appends([(p_, mk) for p_, mk in _tp if p_ == "SkyyMTpB"]), "SkyyMTpB") <= TP_SH.h - SUI.TITLE_H - 2 * HUB_PAD, "0.3.29: Teleport fits"
for _mk in list(UI29.values()) + UI29_HYL + UI29_HA + UI29_FBH + UI29_FBT:
    assert not re.search(r"(Vertical|Horizontal)Alignment\s*:\s*(Top|Bottom|Left|Right)\b", _mk), "0.3.29: Start / Center / End alignments only"
    for _eid in re.findall(r"#([A-Za-z0-9_]+)\s*\{", _mk):
        assert "_" not in _eid
# every hub page: the bar-less height + the 52 px strip fits 1080p and the hub's FULL contract tab list fits (row 1 is in the title bar)
HUB_PAGES = [("stats", ST_SH, "character", "stats"), ("teleport", TP_SH, "world", "teleport"),
             ("players", MENU_HUB_SH["social"], "social", "players"), ("mods", MENU_HUB_SH["settings"], "settings", "mods"),
             ("settings", STG_HUB_SH, "settings", "settings"), ("setup", ADM_HUB_SH, "settings", "setup")]
HUB_LABEL_FIT = {}
for _t, _sh, _h, _my in HUB_PAGES:
    assert _sh.row and SUI.assert_hub_page(_sh.w, _sh.h - SUI.HUB_BAR_H, old_title_h=0, hub=_h, pad=_sh.pad) == (_sh.w, _sh.h), "0.3.29: %s fits 1080p" % _t
    _tw = SUI.assert_hub_fits(_h, _sh.tabs_w)
    _pp = os.path.commonprefix([_sh.prefix, _sh.body])
    SUI.check_page(_sh.appends, _pp)
    SUI.assert_proven(_sh.appends, what="row shell " + _t)
    _els = SUI.check_sky_paths(_sh.appends)
    assert {"Header", SUI.HUB_FRAME[_h], "Close"} <= set(_els) and not any("HubMenu" in mk for _p, mk in _sh.appends), "0.3.29: %s row shell: %s" % (_t, _els)
    assert any(_sh.prefix + "HubRow" in mk for _p, mk in _sh.appends if _p == _sh.bar), "0.3.29: row 1 sits in the %s title bar" % _t
    assert SUI.assert_hub_row_fits(_sh.row_w)[1], "0.3.29: row 1 shows its icons on %s" % _t
    for _rows in (SUI.hub_tabs(_h), [r for r in SUI.hub_tabs(_h) if r[2] == "SkyyMenu"]):
        _lab = [(t, OWN_LABEL.get(t, l) if m == "SkyyMenu" else l, o) for t, o, m, l, _c in _rows]
        _bar = SUI.hub_bar_preview2(_sh.prefix, _lab, _my, _sh.tabs_w)
        SUI.check_page(SUI.Appends(list(_sh.appends) + list(_bar)), _pp)
        SUI.check_sky_paths(_bar)
        _w1 = SUI.hub_tab_width(_sh.tabs_w, len(_rows))
        for _r in _lab:
            assert SUI.text_width(_r[1], 12, bold=True) <= _w1 - 2 * SUI.HUB_TAB_PAD, "0.3.29: tab %s fits %d px at 12 px" % (_r[1], _w1)
    HUB_LABEL_FIT[_t] = _tw
MH_JAVA = dict((h, MENU_HUB_SH[h].java("b")) for h in MENU_HUB_SH)
HOME_JAVA = HOME_SH.java("b")
TP_JAVA = TP_SH.java("b")
STG_HUB_JAVA = STG_HUB_SH.java("b")
ADM_HUB_JAVA = ADM_HUB_SH.java("b")
ST_HUB_JAVA = SUI.java_hub_build(ST_SH, "stats", cls="@PKG@.HubBar")
STG_HUB_BUILD = SUI.java_hub_build(STG_HUB_SH, "settings", cls="@PKG@.HubBar", uuid="u")
ADM_HUB_BUILD = SUI.java_hub_build(ADM_HUB_SH, "setup", cls="@PKG@.HubBar", uuid="me()")
HOME_BUILD = SUI.java_hub_build(HOME_SH, None, cls="@PKG@.HubBar", uuid="me")
TP_BUILD = SUI.java_hub_build(TP_SH, "teleport", cls="@PKG@.HubBar", uuid="me")
MH_BUILD = '@PKG@.HubBar.build2(b, ev, "SkyyMenuH", hubName(), hubTab(), %d, this.playerRef.getUuid(), %d, %d);' % (
    GW, SUI.HUB_PART_ROW | SUI.HUB_PART_CLOSE, MENU_HUB_SH["social"].row_w)
assert ST_HUB_JAVA.startswith('@PKG@.HubBar.build2(b, ev, "SkyyStatF", "character", "stats", 1066,') and ST_HUB_JAVA.endswith(", 6, %d);" % (ST_W - 50))
assert HOME_BUILD == '@PKG@.HubBar.build2(b, ev, "SkyyMHm", "home", null, 0, me, 6, 1218);', HOME_BUILD
assert TP_BUILD == '@PKG@.HubBar.build2(b, ev, "SkyyMTp", "world", "teleport", 756, me, 6, 754);', TP_BUILD
print("0.3.29 pages (kit %s row 1): Home %d x %d (grid %d x %d, centre slot at page centre %+d / %+d = 0.3.28 slot 13), Teleport %d x %d, %s" % (
    SUI.kit_id(), HOME_W, HOME_H, HG_W, HG_H, HOME_C[0], HOME_C[1], TP_W, TP_H, ", ".join("%s %d px tabs" % (t, HUB_LABEL_FIT[t]) for t, _s, _h, _m in HUB_PAGES)))
'''
rep(_hb, SHELLS29)

# ---------------------------------------------------------------------------------------------------------------- MenuData: the 0.3.29 tables
rep('''F(dat, "public static final String[] HT_LABEL = %s;" % jarr([r[3] for r in HUB_OWN]))
''', '''F(dat, "public static final String[] HT_LABEL = %s;" % jarr([OWN_LABEL.get(r[1], r[3]) for r in HUB_OWN]))   # 0.3.29: layout -> Edit shortcuts
# 0.3.29: UNIFIED MENU U1 - the shortcut grids, the one-time update table, Home / Teleport markup, the foot buttons, the texts
for _n, _v in (("HG_N", HG_N), ("HG_COLS", HG_COLS), ("HG_ROWS", HG_ROWS), ("HG_CR", HG_CR), ("HG_CC", HG_CC), ("OLD_COLS", OLD_COLS),
               ("OLD_CR", OLD_CR), ("OLD_CC", OLD_CC), ("HOME_FOOT_W", HOME_FOOT_W), ("TP_FOOT_W", TP_FOOT_W), ("FB_GAP", FB_GAP),
               ("AL_MAX", AL_MAX), ("AL_SHOW", AL_SHOW), ("YOU_BAR_W", HOME_SIDE - 28)):
    F(dat, "public static final int %s = %d;" % (_n, _v))
F(dat, "public static final String[] MIG = %s;" % jarr([MIG.get(k, "") if k else "" for k in E_KEY]))
F(dat, "public static final String[] MIG_TAB = %s;" % jarr([TILE_TAB.get(k, "") if k else "" for k in E_KEY]))   # fix round: the tile's own tab
F(dat, "public static final String[] BH_KEY = %s;" % jarr([BUILTIN_HOME[k] for k in sorted(BUILTIN_HOME)]))
F(dat, "public static final int[] BH_SLOT = %s;" % jints(sorted(BUILTIN_HOME)))
F(dat, "public static final String[] BT_KEY = %s;" % jarr([BUILTIN_TP[k] for k in sorted(BUILTIN_TP)]))
F(dat, "public static final int[] BT_SLOT = %s;" % jints(sorted(BUILTIN_TP)))
F(dat, "public static final int[] TP_AUTO = %s;" % jints(TP_AUTO))
F(dat, "public static final String[] TPK_KEY = %s;" % jarr(sorted(TP_KEYS)))
F(dat, "public static final int[] TPK_E = %s;" % jints([x[0] for x in TPK_E]))
F(dat, "public static final String[] HUB_DEFTAB = %s;" % jarr([HUB_DEFTAB.get(_h, "") for _h in SUI.HUBS]))
F(dat, "public static final String[] HUB_BLURB = %s;" % jarr([HUB_BLURB[_h] for _h in SUI.HUBS]))
F(dat, "public static final String HOME_TITLE = %s;" % jstr(HOME_TITLE))
F(dat, "public static final String HOME_ICON = %s;" % jstr(HOME_ICON))
for _k, _v in sorted(HOME_TXT.items()):
    if _k in ("HT_YOU_TITLE", "HT_YOU_HINT", "HT_NOW_TITLE"):   # baked into the UI29 markup at build time; never read at runtime
        continue
    F(dat,"public static final String %s = %s;" % (_k, jstr(_v)))
for _k, _v in sorted(UI29.items()):
    F(dat, "public static final String UI_%s = %s;" % (_k, jstr(_v)))
F(dat, "public static final String[] UI_HYL = %s;" % jarr(UI29_HYL))
F(dat, "public static final String[] UI_HA = %s;" % jarr(UI29_HA))
F(dat, "public static final String[] UI_FBH = %s;" % jarr(UI29_FBH))
F(dat, "public static final String[] UI_FBT = %s;" % jarr(UI29_FBT))
F(dat, "public static final String[] FB_WORD = %s;" % jarr([f[0] for f in FB]))
F(dat, "public static final int[] FB_W = %s;" % jints([f[2] for f in FB]))
F(dat, "public static final int[] FB_TW = %s;" % jints(FB_TW))
''')

# ---------------------------------------------------------------------------------------------------------------- classes: HubBar (kit 1.6) + MenuAlert
rep('''hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod)
MADE.append(hubb)
''', '''hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True)   # 0.3.29: kit 1.6 (row 1, tab icons, default tab)
MADE.append(hubb)
mal  = mk("MenuAlert")      # 0.3.29: home:alert:SkyyMenu - what SkyyMenu itself knows for the Home page's Right now panel
''')
rep('''         hubb, mhub, mho, mhv, hcch, hcst, hcmk, hctr, hcso, pl)   # 0.3.28: the hub classes''',
    '''         hubb, mhub, mho, mhv, hcch, hcst, hcmk, hctr, hcso, mal, pl)   # 0.3.28: the hub classes; 0.3.29: MenuAlert''')

# ---------------------------------------------------------------------------------------------------------------- MenuLayout: the new model
_lb = block('''# ================= 0.3.17 MenuLayout: who gets which main-view layout (Skyy 2026-10-10, the menu layout editor) =================
''', '''    NAMES.remove(k);
  }
  java.util.ArrayList es = new java.util.ArrayList(ERRAT.keySet());
  for (int i = 0; i < es.size(); i++) { if (!onlineK.contains(es.get(i))) ERRAT.remove(es.get(i)); }
}""")
''')
LAYOUT29 = r'''# ================= 0.3.29 MenuLayout: every player's HOME shortcut grid + TELEPORT grid (Skyy 2026-10-15, the unified menu) =================
# A grid = String[HG_N] of shortcut keys (null = an empty slot; MenuData.HG_N = 35, 7 x 5). A RECORD (one per account, also the server
# default DEF) = Object[]{ String[] home or null (= the default), String[] tp or null, String old line (_old) or null, String 0.3.28 tile
# lines or null, Boolean "one-time update not yet written", String _name from the file }. OWN: uuid text -> its record (never changed
# after it is published - copy-on-write), NONE (no file) or ERR (a read error: the default is drawn, editing is refused, re-read after
# 30 s). Files (Skyy_SkyyMenu/layouts/<uuid>.properties, layout-default.properties), extended backward-compatibly:
#   _v=1  _home=1|0  _tp=1|0  [_old=<0.3.28 tile=slot,...>]  <the 0.3.28 tile=slot lines, kept for a rollback>  g.<slot>=<key>  t.<slot>=<key>
# THE ONE-TIME UPDATE (PROJECT-RULES 4): a file with _v=1 and 0.3.28 tile lines but no _home is a 0.3.28 layout: migrate() in memory at
# the first read (hubs replace the tiles they cover, the rest keep their offset from the centre, outside = + Add), then the first write
# (SkyyMenu-IO) keeps a VERIFIED History copy of the exact old bytes in config-history/ first (read back + compared; a failure = no write,
# retried), writes _home (the run-once marker) + _old (the old line) + the old tile lines + the new grid, and queues one config-changes.log
# line (status done; Undo = Edit shortcuts > Old tiles back). A removed tile never comes back by itself (no "new tile -> first free slot").
F(lay, "public static volatile java.nio.file.Path DIR;")
F(lay, "public static volatile java.nio.file.Path DEF_FILE;")
F(lay, 'public static final String NONE = "none";')
F(lay, 'public static final String BAD = "bad";')
F(lay, 'public static final String ERR = "err";')
F(lay, 'public static final String DEF_KEY = "_default";')
F(lay, "public static volatile Object[] DEF;")
F(lay, "public static volatile boolean DEF_BROKEN;")
F(lay, "public static volatile int MIGRATIONS;")
F(lay, 'public static final java.time.format.DateTimeFormatter STAMP = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");')
F(lay, 'public static final java.time.format.DateTimeFormatter HUMAN = java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");')
# SNAPPED: file key -> FALSE = its History copy is made (a failed write then never makes a second one), TRUE = the update is written + logged.
# HFAIL: file key -> Integer, failed History copies in a row (HIST_TRIES = write anyway: the old layout stays in the file itself).
for _f in ("OWN", "NAMES", "DIRTY", "WARNED", "BROKEN", "ERRAT", "MIGRATED", "SNAPPED", "HFAIL"):
    F(lay, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
F(lay, "public static final int HIST_TRIES = 3;")
# fix round: the server default's one-time update waits for the first player (DEF_PENDING): at setup no other mod has published its hub
# tabs yet, so the hub check of migrate() could not see them
F(lay, "public static final java.util.concurrent.atomic.AtomicBoolean DEF_PENDING = new java.util.concurrent.atomic.AtomicBoolean(false);")
F(lay, 'public static final String HIST_INDEX = "SkyyMenu-layouts-index.log";')
# LayoutSaveTask's fields + constructors first (saveSoon / preload construct it); its run() after saveNow
lsv.addInterface(pool.get("java.lang.Runnable"))
F(lsv, "public String k;")
F(lsv, "public boolean load;")
C(lsv, "public LayoutSaveTask(String k) { this.k = k; this.load = false; }")
C(lsv, "public LayoutSaveTask(String k, boolean load) { this.k = k; this.load = load; }")
M(lay, r"""
public static boolean isMain(int i) {
  return i >= 0 && i < @PKG@.MenuData.E_VIEW.length && "main".equals(@PKG@.MenuData.E_VIEW[i]);
}""")
# the 0.3.28 built-in layout (layout D) - only the retired 9 x 6 code path still reads it
M(lay, r"""
public static int[] builtinOld() {
  int n = @PKG@.MenuData.E_VIEW.length;
  int[] out = new int[n];
  for (int i = 0; i < n; i++) out[i] = isMain(i) ? @PKG@.MenuData.E_SLOT[i] : -1;
  return out;
}""")
M(lay, r"""
public static int keyIndex(String k) {
  if (k == null) return -1;
  for (int i = 0; i < @PKG@.MenuData.E_KEY.length; i++) { if (isMain(i) && @PKG@.MenuData.E_KEY[i].equals(k)) return i; }
  return -1;
}""")
M(lay, r"""
public static int hubIdx(String h) {
  if (h == null) return -1;
  for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) { if (@PKG@.MenuData.HUB_ID[i].equals(h)) return i; }
  return -1;
}""")
M(lay, r"""
public static boolean okWarp(String n) {
  if (n == null || n.length() < 1 || n.length() > 32) return false;
  for (int i = 0; i < n.length(); i++) {
    char c = n.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-')) return false;
  }
  return true;
}""")
M(lay, r"""
public static boolean okTp(String k) {
  if (k == null) return false;
  for (int i = 0; i < @PKG@.MenuData.TPK_KEY.length; i++) { if (@PKG@.MenuData.TPK_KEY[i].equals(k)) return true; }
  return k.startsWith("warp:") && okWarp(k.substring(5));
}""")
# a key that may sit on a grid (tp = the Teleport grid: teleport targets only; Home takes every kind)
M(lay, r"""
public static boolean okKey(String k, boolean tp) {
  if (k == null || k.length() < 4 || k.length() > 80) return false;
  if (okTp(k)) return true;
  if (tp) return false;
  if (k.startsWith("hub:")) return hubIdx(k.substring(4)) >= 0;
  if (k.startsWith("tab:")) {
    int c = k.indexOf(':', 4);
    return c > 4 && hubIdx(k.substring(4, c)) >= 0 && @PKG@.HubBar.okId(k.substring(c + 1));
  }
  if (k.startsWith("tile:")) {
    int i = keyIndex(k.substring(5));
    return i >= 0 && !"-".equals(@PKG@.MenuData.MIG[i]);
  }
  return false;
}""")
M(lay, r"""
public static boolean has(String[] g, String k) {
  if (g == null || k == null) return false;
  for (int i = 0; i < g.length; i++) { if (k.equals(g[i])) return true; }
  return false;
}""")
M(lay, "public static String[] blank() { return new String[@PKG@.MenuData.HG_N]; }")
M(lay, r"""
public static String[] copy(String[] g) {
  String[] o = blank();
  if (g == null) return o;
  for (int i = 0; i < o.length && i < g.length; i++) o[i] = g[i];
  return o;
}""")
# part 0 = Home, 1 = Teleport: the built-in default grid
M(lay, r"""
public static String[] builtin(int part) {
  String[] g = blank();
  String[] ks = @PKG@.MenuData.BH_KEY;
  int[] ss = @PKG@.MenuData.BH_SLOT;
  if (part == 1) { ks = @PKG@.MenuData.BT_KEY; ss = @PKG@.MenuData.BT_SLOT; }
  for (int i = 0; i < ks.length; i++) g[ss[i]] = ks[i];
  return g;
}""")
M(lay, r"""
public static void warnOnce(String what, String msg) {
  if (WARNED.putIfAbsent(what, Boolean.TRUE) != null) return;
  @PKG@.MenuUtil.warn(msg);
}""")
# g.<slot> / t.<slot> lines -> a grid; a bad key, a slot outside 0 - 34 or a key already on the grid is skipped
M(lay, r"""
public static String[] slotLines(java.util.Properties p, String pre, boolean tp) {
  String[] g = blank();
  for (int s = 0; s < g.length; s++) {
    String v = p.getProperty(pre + s);
    if (v == null) continue;
    v = v.trim();
    if (okKey(v, tp) && !has(g, v)) g[s] = v;
  }
  return g;
}""")
# the 0.3.28 tile=slot lines (slots 0 - 44) -> int[entry] = slot (-1 = none); null = no usable line
# a 0.3.28 tile line's slot: 0 - 44, else -1
M(lay, r"""
public static int slotOf(String v) {
  int sl = -1;
  try { sl = Integer.parseInt(v.trim()); } catch (Throwable t) { sl = -1; }
  return sl >= 0 && sl < @PKG@.MenuData.LAY_GRID ? sl : -1;
}""")
M(lay, r"""
public static int[] parseOld(java.util.Properties p) {
  int n = @PKG@.MenuData.E_VIEW.length;
  int[] out = new int[n];
  int got = 0;
  for (int i = 0; i < n; i++) {
    out[i] = -1;
    if (!isMain(i)) continue;
    String v = p.getProperty(@PKG@.MenuData.E_KEY[i]);
    if (v == null) continue;
    int sl = slotOf(v);
    if (sl >= 0) { out[i] = sl; got = got + 1; }
  }
  if (got == 0) return null;
  return out;
}""")
M(lay, r"""
public static String oldLine(int[] old) {
  StringBuilder sb = new StringBuilder();
  for (int s = 0; s < @PKG@.MenuData.LAY_GRID; s++) {
    for (int i = 0; i < old.length; i++) {
      if (!isMain(i) || old[i] != s) continue;
      if (sb.length() > 0) sb.append(',');
      sb.append(@PKG@.MenuData.E_KEY[i]).append('=').append(s);
    }
  }
  return sb.toString();
}""")
M(lay, r"""
public static String compatText(int[] old) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < old.length; i++) {
    if (!isMain(i) || old[i] < 0) continue;
    sb.append(@PKG@.MenuData.E_KEY[i]).append('=').append(old[i]).append('\n');
  }
  return sb.toString();
}""")
# 9 x 6 slot -> 7 x 5 slot keeping its offset from the centre (13 -> 17); -1 = outside the new grid
M(lay, r"""
public static int mapSlot(int s) {
  if (s < 0 || s >= @PKG@.MenuData.LAY_GRID) return -1;
  int r = s / @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CR + @PKG@.MenuData.HG_CR;
  int c = s % @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CC + @PKG@.MenuData.HG_CC;
  if (r < 0 || r >= @PKG@.MenuData.HG_ROWS || c < 0 || c >= @PKG@.MenuData.HG_COLS) return -1;
  return r * @PKG@.MenuData.HG_COLS + c;
}""")
# fix round: is the page an old tile IS (MenuData.MIG_TAB, "<hub>:<tab>") on this server right now (its hub:tab:<hub>:<tab> published)?
M(lay, r"""
public static boolean tabHere(String t) {
  if (t == null || t.length() == 0) return false;
  try { return @PKG@.HubBar.get("hub:tab:" + t) instanceof Object[]; } catch (Throwable x) { return false; }
}""")
# fix round 2: a hub whose covered tiles ALL sat outside the 7 x 5 grid (Skyy's own layout: Social on the left edge, Settings on the right)
# still replaces them - it goes on the free slot nearest to its first covered tile's spot pulled inside the grid (ties: reading order).
# Only hubs that replace a tile (its page is published right now); uncovered tiles outside still wait in + Add. Runs after every tile
# inside the grid has its place, so it only fills empty slots.
M(lay, r"""
public static void placeOutside(String[] g, int[] old) {
  for (int s = 0; s < @PKG@.MenuData.LAY_GRID; s++) {
    int i = -1;
    for (int k = 0; k < old.length; k++) { if (isMain(k) && old[k] == s) { i = k; break; } }
    if (i < 0) continue;
    String m = @PKG@.MenuData.MIG[i];
    if (m.length() == 0 || m.equals("-") || m.startsWith("=")) continue;
    if (!tabHere(@PKG@.MenuData.MIG_TAB[i])) continue;
    String key = "hub:" + m;
    if (has(g, key)) continue;
    int r = s / @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CR + @PKG@.MenuData.HG_CR;
    int c = s % @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CC + @PKG@.MenuData.HG_CC;
    if (r < 0) r = 0;
    if (r > @PKG@.MenuData.HG_ROWS - 1) r = @PKG@.MenuData.HG_ROWS - 1;
    if (c < 0) c = 0;
    if (c > @PKG@.MenuData.HG_COLS - 1) c = @PKG@.MenuData.HG_COLS - 1;
    int best = -1;
    int bd = 0;
    for (int x = 0; x < g.length; x++) {
      if (g[x] != null) continue;
      int dr = x / @PKG@.MenuData.HG_COLS - r;
      int dc = x % @PKG@.MenuData.HG_COLS - c;
      int d = dr * dr + dc * dc;
      if (best < 0 || d < bd) { best = x; bd = d; }
    }
    if (best >= 0) g[best] = key;
  }
}""")
# THE MIGRATION (hubs = true; false = "Old tiles back": every old tile as itself). The old tiles in reading order: Hover Tooltips is
# retired; a covered tile -> its hub, on the first covered tile's new slot that is inside the grid (once per hub) - but ONLY when the
# tile's own page is published as that hub's tab right now (fix round: a hub without the page would turn a working tile into a
# "coming soon" stub for good; such a tile stays itself); Teleport -> the Teleport shortcut; any other tile -> itself; a slot outside the
# 7 x 5 grid = not placed (it waits in + Add). Runs at a player's first read (join: every mod has published its tabs).
M(lay, r"""
public static String[] migrate(int[] old, boolean hubs) {
  String[] g = blank();
  if (old == null) return g;
  for (int s = 0; s < @PKG@.MenuData.LAY_GRID; s++) {
    int i = -1;
    for (int k = 0; k < old.length; k++) { if (isMain(k) && old[k] == s) { i = k; break; } }
    if (i < 0) continue;
    String m = @PKG@.MenuData.MIG[i];
    if (m.equals("-")) continue;
    int ns = mapSlot(s);
    if (ns < 0 || g[ns] != null) continue;
    String key = null;
    if (m.startsWith("=")) key = m.substring(1);
    else if (hubs && m.length() > 0 && tabHere(@PKG@.MenuData.MIG_TAB[i])) key = "hub:" + m;
    else key = "tile:" + @PKG@.MenuData.E_KEY[i];
    if (has(g, key)) continue;
    g[ns] = key;
  }
  if (hubs) placeOutside(g, old);
  return g;
}""")
# fix round 2: an old tile and the hub tab it IS (MenuData.MIG_TAB) are the SAME page - its twin key (tile:<key> <-> tab:<hub>:<tab>), null =
# none. + Add lists such a page once, and a page already on the grid under either key is "placed" (no second Teleport / Pets).
M(lay, r"""
public static String twin(String k) {
  if (k == null) return null;
  for (int i = 0; i < @PKG@.MenuData.E_KEY.length; i++) {
    if (!isMain(i) || @PKG@.MenuData.MIG_TAB[i].length() == 0) continue;
    if (k.equals("tile:" + @PKG@.MenuData.E_KEY[i])) return "tab:" + @PKG@.MenuData.MIG_TAB[i];
    if (k.equals("tab:" + @PKG@.MenuData.MIG_TAB[i])) return "tile:" + @PKG@.MenuData.E_KEY[i];
  }
  return null;
}""")
M(lay, r"""
public static boolean hasSame(String[] g, String k) {
  return has(g, k) || has(g, twin(k));
}""")
# properties -> a record; null = not a layout (no _v=1, or neither _home nor 0.3.28 tile lines)
M(lay, r"""
public static Object[] parse(java.util.Properties p) {
  if (p == null || !"1".equals(p.getProperty("_v", "").trim())) return null;
  String hm = p.getProperty("_home");
  int[] old = parseOld(p);
  String nm = p.getProperty("_name");
  if (hm == null) {
    if (old == null) return null;
    return new Object[] { migrate(old, true), null, oldLine(old), compatText(old), Boolean.TRUE, nm };
  }
  String[] home = null;
  if ("1".equals(hm.trim())) home = slotLines(p, "g.", false);
  String[] tp = null;
  if ("1".equals(p.getProperty("_tp", "").trim())) tp = slotLines(p, "t.", true);
  String ol = p.getProperty("_old");
  if (ol != null) ol = ol.trim();
  if (ol != null && ol.length() == 0) ol = null;
  String ct = null;
  if (old != null) ct = compatText(old);
  return new Object[] { home, tp, ol, ct, Boolean.FALSE, nm };
}""")
# null = no file; Object[] = a record; BAD = the file reads but holds no layout; ERR = a read error (both warned once per file)
M(lay, r"""
public static Object readFile(java.nio.file.Path f, String what) {
  if (f == null) return null;
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(new java.io.InputStreamReader(in, "UTF-8")); } finally { in.close(); }
    Object[] r = parse(p);
    if (r != null) return r;
    warnOnce(what, "the menu layout file " + what + " holds no usable layout (it needs _v=1 and _home or tile=slot lines) - the default shortcuts are used; the file stays as it is until the shortcuts are changed in game (then it is kept as " + what + ".bad)");
    return BAD;
  } catch (Throwable t) {
    warnOnce(what, "the menu layout file " + what + " cannot be read (" + t + ") - the default shortcuts are shown and cannot be edited until the file reads again (tried again every 30 s); the file is NOT changed");
  }
  return ERR;
}""")
M(lay, r"""
public static void lines(StringBuilder sb, String pre, String[] g) {
  if (g == null) return;
  for (int s = 0; s < g.length; s++) { if (g[s] != null) sb.append(pre).append(s).append('=').append(g[s]).append('\n'); }
}""")
# the 0.3.29 lines of a record (_home / _tp / _old / g. / t.): text() writes them after the 0.3.28 lines, the one-time update appends them
M(lay, r"""
public static String tail(Object[] r) {
  StringBuilder sb = new StringBuilder();
  sb.append("_home=").append(r[0] != null ? "1" : "0").append('\n');
  sb.append("_tp=").append(r[1] != null ? "1" : "0").append('\n');
  if (r[2] != null) sb.append("_old=").append((String) r[2]).append('\n');
  lines(sb, "g.", (String[]) r[0]);
  lines(sb, "t.", (String[]) r[1]);
  return sb.toString();
}""")
# the 0.3.28 tile lines: the file's own, else (fix round) the 0.3.28 built-in layout D in full - a rollback to 0.3.28 then shows layout D
# exactly (one lone teleport=13 line made 0.3.28 put the other tiles in the first free slots). Fix round 2: a player with no 0.3.28 file
# on a server whose default holds 0.3.28 tile lines (a custom 0.3.28 server default) gets THOSE lines - a rollback then shows them the
# server's default, as 0.3.28 did, not layout D
M(lay, r"""
public static String text(Object[] r, String head) {
  StringBuilder sb = new StringBuilder();
  sb.append(head);
  sb.append("_v=1\n");
  String ct = (String) r[3];
  Object[] d = DEF;
  if (ct == null && d != null && d != r && d.length > 3 && d[3] != null) ct = (String) d[3];   // fix round 2: a custom server default's lines
  sb.append(ct != null ? ct : compatText(builtinOld()));
  sb.append(tail(r));
  return sb.toString();
}""")
# a file that already holds 0.3.29 lines (hand-made: g. / t. / _home / _tp / _old) is rewritten in full, never appended to
M(lay, r"""
public static boolean hasNewLines(String t) {
  String[] ls = t.split("\n");
  for (int i = 0; i < ls.length; i++) {
    String l = ls[i].trim();
    if (l.startsWith("g.") || l.startsWith("t.") || l.startsWith("_home") || l.startsWith("_tp") || l.startsWith("_old")) return true;
  }
  return false;
}""")
# the bytes to write. THE ONE-TIME UPDATE (PROJECT-RULES 4 "keep the file's bytes and line endings"): the old file's EXACT bytes + the
# 0.3.29 lines appended in its own line ending (a later _key wins in a properties file; a 0.3.28 SkyyMenu reads the untouched old lines).
# Any later save: the whole file in the file's own line ending (CRLF stays CRLF).
M(lay, r"""
public static byte[] bytesFor(byte[] was, boolean mig, Object[] r, String head) throws java.io.IOException {
  String old = null;
  if (was != null) old = new String(was, "UTF-8");
  String nl = (old != null && old.indexOf("\r\n") >= 0) ? "\r\n" : "\n";
  if (mig && old != null && !hasNewLines(old)) {
    String add = "# 0.3.29: the Home shortcuts (the one-time update - every line above is the 0.3.28 layout exactly as it was)\n" + tail(r);
    if (was.length > 0 && was[was.length - 1] != (byte) 10) add = "\n" + add;
    if (!nl.equals("\n")) add = add.replace("\n", nl);
    byte[] tb = add.getBytes("UTF-8");
    byte[] out = new byte[was.length + tb.length];
    System.arraycopy(was, 0, out, 0, was.length);
    System.arraycopy(tb, 0, out, was.length, tb.length);
    return out;
  }
  String t = text(r, head);
  if (!nl.equals("\n")) t = t.replace("\n", nl);
  return t.getBytes("UTF-8");
}""")
M(lay, r"""
public static boolean empty(Object[] r) {
  return r == null || (r[0] == null && r[1] == null && r[2] == null && r[3] == null);
}""")
M(lay, r"""
public static String summary(Object g) {
  if (!(g instanceof String[])) return "the default shortcuts";
  String[] a = (String[]) g;
  StringBuilder sb = new StringBuilder();
  for (int s = 0; s < a.length; s++) { if (a[s] != null) { if (sb.length() > 0) sb.append(' '); sb.append(s).append('=').append(a[s]); } }
  return sb.length() == 0 ? "no shortcuts" : sb.toString();
}""")
M(lay, r"""
public static void keepBad(java.nio.file.Path f) throws java.io.IOException {
  if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
  java.nio.file.Path b = f.resolveSibling(f.getFileName().toString() + ".bad");
  if (java.nio.file.Files.exists(b, new java.nio.file.LinkOption[0])) b = f.resolveSibling(f.getFileName().toString() + ".bad-" + System.currentTimeMillis());
  java.nio.file.Files.move(f, b, new java.nio.file.CopyOption[0]);
}""")
M(lay, r"""
public static String fileId(String what) { return "Skyy_SkyyMenu~" + what.replace('/', '~'); }""")
# THE VERIFIED HISTORY COPY (PROJECT-RULES 4, before the one-time update's first write): the file's exact bytes -> config-history/
# <fileId>.<yyyyMMdd-HHmmss-SSS>.bak (the config kit's folder and naming), read back and compared byte for byte; any difference throws
# (the file is then NOT written; saveNow keeps it DIRTY and retries every 30 s). One index line in the kit's format (best effort) - in its OWN file
# config-history/SkyyMenu-layouts-index.log (fix round: the kit's index.log compaction drops ids that are not settings files).
M(lay, r"""
public static java.nio.file.Path history(java.nio.file.Path f, String what, String sum) throws java.io.IOException {
  byte[] cur = java.nio.file.Files.readAllBytes(f);
  java.nio.file.Path dir = f.toAbsolutePath().getParent();
  if (dir.getFileName() != null && "layouts".equals(dir.getFileName().toString())) dir = dir.getParent();
  dir = dir.resolve("config-history");
  java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
  String id = fileId(what);
  java.time.LocalDateTime now = java.time.LocalDateTime.now();
  java.nio.file.Path b = null;
  String st = null;
  for (int g = 0; g < 1000; g++) {
    java.time.LocalDateTime t = now.plusNanos(1000000L * g);
    st = STAMP.format(t);
    b = dir.resolve(id + "." + st + ".bak");
    if (!java.nio.file.Files.exists(b, new java.nio.file.LinkOption[0])) { now = t; break; }
  }
  @PKG@.MenuUtil.atomicWrite(b, cur);
  byte[] back = java.nio.file.Files.readAllBytes(b);
  if (!java.util.Arrays.equals(back, cur)) throw new java.io.IOException("the History copy " + b.getFileName() + " does not match " + what + " - the file is not changed");
  String line = id + "#" + st + "\tSkyy_SkyyMenu/" + what + "\t" + HUMAN.format(now) + "\tSkyyMenu update\t" + sum + "\n";
  try { java.nio.file.Files.write(dir.resolve(HIST_INDEX), line.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND }); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not add the History line of " + what + " to config-history/" + HIST_INDEX + " (the copy " + b.getFileName() + " is kept): " + t); }
  return b;
}""")
# one config-changes.log line per updated file (the config kit's queue: written by its save task / at shutdown); status done (a layout is
# not a setting row, so Server Setup offers no Undo button - Edit shortcuts > Old tiles back undoes it)
M(lay, r"""
public static void logMigration(String k, Object[] r) {
  try {
    @PKG@.CfgLog.add(null, "SkyyMenu update", "update", "menu.layout[" + k + "]", r[2] == null ? "" : (String) r[2],
      "(0.3.29 Home shortcuts: " + summary(r[0]) + " - Edit shortcuts, " + (DEF_KEY.equals(k) ? "Old default" : "Old tiles back") + " undoes it)", "done");
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not log the menu layout update of " + k + " in config-changes.log: " + t); }
}""")
# the History copy before the update's first write - ONCE per file (fix round): SNAPPED FALSE right after the copy is verified, so a
# failed write retried every 30 s never makes another copy; a copy that fails HIST_TRIES times in a row (config-history not writable)
# no longer blocks the player's shortcuts for good: written anyway with a warning (the old layout stays in the file itself: its exact
# bytes + _old)
M(lay, r"""
public static void snapFirst(String k, java.nio.file.Path f, String what) throws java.io.IOException {
  if (SNAPPED.containsKey(k) || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
  try {
    history(f, what, "before the 0.3.29 Home shortcuts update (the old layout also stays in the file)");
    SNAPPED.put(k, Boolean.FALSE);
    HFAIL.remove(k);
  } catch (Throwable t) {
    Object n = HFAIL.get(k);
    int c = (n instanceof Integer) ? ((Integer) n).intValue() + 1 : 1;
    HFAIL.put(k, Integer.valueOf(c));
    if (c < HIST_TRIES) throw new java.io.IOException("the History copy of " + what + " failed (" + t + ") - the file is not changed yet (try " + c + " of " + HIST_TRIES + ")");
    @PKG@.MenuUtil.warn("the History copy of " + what + " failed " + c + " times (" + t + ") - the update is written without it; the old layout stays in the file (its old lines are kept as they were, + _old)");
    SNAPPED.put(k, Boolean.FALSE);
  }
}""")
M(lay, r"""
public static byte[] readWas(java.nio.file.Path f) throws java.io.IOException {
  if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
  return java.nio.file.Files.readAllBytes(f);
}""")
M(lay, r"""
public static void finishMig(String k, Object[] r) {
  SNAPPED.put(k, Boolean.TRUE);
  HFAIL.remove(k);
  logMigration(k, r);
}""")
M(lay, r"""
public static void writeOwn(String k) throws java.io.IOException {
  Object o = OWN.get(k);
  if (o == null || DIR == null) return;
  java.nio.file.Path f = DIR.resolve(k + ".properties");
  String what = "layouts/" + k + ".properties";
  if (BROKEN.remove(k) != null) keepBad(f);
  if (!(o instanceof Object[])) { java.nio.file.Files.deleteIfExists(f); return; }
  Object[] r = (Object[]) o;
  boolean mig = Boolean.TRUE.equals(r[4]) && !Boolean.TRUE.equals(SNAPPED.get(k));
  if (mig) snapFirst(k, f, what);
  byte[] was = readWas(f);
  if (empty(r)) java.nio.file.Files.deleteIfExists(f);
  else {
    Object nm = NAMES.get(k);
    if (nm == null) nm = r[5];
    String head = "# SkyyMenu: the SkyWynn Menu shortcuts of one player (account uuid " + k + ", the same for every profile).\n"
      + "# g.<slot> = the Home grid, t.<slot> = the Teleport grid (7 x 5, slot = row * 7 + column, 17 = the centre). _home / _tp 0 = the default.\n"
      + "# _old and the tile=slot lines are the 0.3.28 layout (kept for a rollback). Change it in game: Home - Edit shortcuts. Delete this file = the defaults.\n"
      + "_name=" + @PKG@.MenuUtil.cleanName(nm == null ? "" : String.valueOf(nm)) + "\n";
    @PKG@.MenuUtil.atomicWrite(f, bytesFor(was, mig, r, head));
  }
  if (mig) finishMig(k, r);
}""")
M(lay, r"""
public static void writeDef() throws java.io.IOException {
  java.nio.file.Path f = DEF_FILE;
  if (f == null) return;
  if (DEF_BROKEN) { DEF_BROKEN = false; keepBad(f); }
  Object[] d = DEF;
  if (d == null || (empty(d) && !Boolean.TRUE.equals(d[4]))) { java.nio.file.Files.deleteIfExists(f); return; }
  boolean mig = Boolean.TRUE.equals(d[4]) && !Boolean.TRUE.equals(SNAPPED.get(DEF_KEY));
  if (mig) snapFirst(DEF_KEY, f, "layout-default.properties");
  byte[] was = readWas(f);
  String head = "# SkyyMenu: the SERVER DEFAULT shortcuts - every player without their own gets them. g.<slot> = Home, t.<slot> = Teleport (7 x 5).\n"
    + "# Set in game by an admin: Home - Edit shortcuts - Set default. Delete this file = the standard shortcuts.\n";
  @PKG@.MenuUtil.atomicWrite(f, bytesFor(was, mig, d, head));
  if (mig) finishMig(DEF_KEY, d);
}""")
M(lay, r"""
public static synchronized void saveNow(String k) {
  DIRTY.remove(k);
  try {
    if (DEF_KEY.equals(k)) writeDef(); else writeOwn(k);
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("could not save the menu shortcuts " + (DEF_KEY.equals(k) ? "layout-default.properties" : "layouts/" + k + ".properties") + " (kept in memory, retried every 30 s and at shutdown): " + t);
    DIRTY.put(k, Boolean.TRUE);
  }
}""")
# ---- LayoutSaveTask: the delayed save (saveNow writes the NEWEST state, so quick clicks give few writes); load = the join preload
M(lay, r"""
public static void saveSoon(String k) {
  DIRTY.put(k, Boolean.TRUE);
  if (!@PKG@.MenuIO.schedule(new @PKG@.LayoutSaveTask(k), 300L)) saveNow(k);
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
  if (prev != null) return prev;
  if ((r instanceof Object[]) && Boolean.TRUE.equals(((Object[]) r)[4])) {
    SNAPPED.remove(k);    // fix round 2: a 0.3.28 file read again (an admin restored a .bak by hand) = a NEW update: History copy + append again
    HFAIL.remove(k);
    MIGRATED.put(k, Boolean.TRUE);
    MIGRATIONS = MIGRATIONS + 1;
    @PKG@.MenuUtil.info("menu layout layouts/" + k + ".properties: the 0.3.29 one-time update - hubs replace the old tiles they cover, the other tiles keep their place, Hover Tooltips goes (Settings has it); the old layout stays in the file (_old + the 0.3.28 lines) and a History copy goes to config-history first");
    saveSoon(k);
  }
  return r;
}""")
M(lay, r"""
public static boolean unreadable(java.util.UUID u) {
  return u != null && ERR.equals(own(u.toString()));
}""")
M(lay, r"""
public static Object[] rec(java.util.UUID u) {
  if (u == null) return null;
  Object o = own(u.toString());
  if (o instanceof Object[]) return (Object[]) o;
  return null;
}""")
# the _old line (tile=slot,...) -> int[entry] = 0.3.28 slot (-1 = none)
M(lay, r"""
public static int[] parseOldLine(String ol) {
  int[] old = new int[@PKG@.MenuData.E_VIEW.length];
  for (int i = 0; i < old.length; i++) old[i] = -1;
  if (ol == null) return old;
  String[] ps = ol.split(",");
  for (int j = 0; j < ps.length; j++) {
    int e = ps[j].indexOf('=');
    if (e <= 0) continue;
    int i = keyIndex(ps[j].substring(0, e).trim());
    int sl = slotOf(ps[j].substring(e + 1));
    if (i >= 0 && sl >= 0) old[i] = sl;
  }
  return old;
}""")
# fix round: the server default's one-time update, deferred from setup (loadDefault) to the first use after every mod published its hub
# tabs (a player's join / a page draw / an admin change): migrate() again with the hub check, then written (History copy first) once
M(lay, r"""
public static void settleDef() {
  if (!DEF_PENDING.compareAndSet(true, false)) return;
  Object[] d = DEF;
  if (d == null || d[2] == null || !Boolean.TRUE.equals(d[4])) return;
  Object[] nx = new Object[] { migrate(parseOldLine((String) d[2]), true), d[1], d[2], d[3], d[4], d[5] };
  DEF = nx;
  @PKG@.MenuUtil.info("menu layout layout-default.properties: the 0.3.29 one-time update of the server default (hubs whose pages are on this server replace the old tiles they cover; the old layout stays in the file; a History copy goes to config-history first): " + summary(nx[0]));
  saveSoon(DEF_KEY);
}""")
# the grid a player sees: their own, else the server default, else the built-in one (a copy - change it freely)
M(lay, r"""
public static String[] grid(java.util.UUID u, int part) {
  settleDef();
  Object[] r = rec(u);
  if (r != null && r[part] != null) return copy((String[]) r[part]);
  Object[] d = DEF;
  if (d != null && d[part] != null) return copy((String[]) d[part]);
  return builtin(part);
}""")
M(lay, r"""
public static String oldOf(java.util.UUID u) {
  Object[] r = rec(u);
  return r == null ? null : (String) r[2];
}""")
# "Old tiles back" (the in-game Undo of the one-time update): the _old line as tiles, each on its own mapped slot (no hubs)
M(lay, r"""
public static String[] oldTilesBack(java.util.UUID u) {
  String ol = oldOf(u);
  if (ol == null) return null;
  return migrate(parseOldLine(ol), false);
}""")
# fix round 2 (PROJECT-RULES 4 "a change-log line with Undo"): the SERVER DEFAULT's in-game Undo - admins, Home - Edit shortcuts - Old default:
# the server default's _old line as tiles on their mapped slots (no hubs); null = the server default has no 0.3.28 layout to bring back
M(lay, r"""
public static boolean hasOldDefault() {
  Object[] d = DEF;
  return d != null && d.length > 2 && d[2] != null;
}""")
M(lay, r"""
public static String[] oldDefaultBack() {
  settleDef();
  Object[] d = DEF;
  if (d == null || d[2] == null) return null;
  return migrate(parseOldLine((String) d[2]), false);
}""")
M(lsv, r"""
public void run() {
  try {
    if (this.load) @PKG@.MenuLayout.own(this.k);
    else @PKG@.MenuLayout.saveNow(this.k);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu shortcuts " + (this.load ? "preload" : "save") + " failed: " + t); }
}""")
M(lay, r"""
public static void preload(java.util.UUID u) {
  try {
    settleDef();
    if (u == null || DIR == null) return;
    String k = u.toString();
    if (OWN.containsKey(k)) return;
    if (!@PKG@.MenuIO.schedule(new @PKG@.LayoutSaveTask(k, true), 0L)) @PKG@.MenuUtil.warn("could not schedule the menu shortcuts preload (SkyyMenu-IO stopped)");
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule the menu shortcuts preload: " + t); }
}""")
# a change (world thread: memory + a scheduled save): part 0 Home / 1 Teleport; g = the new grid, null = back to the default. 1 = done.
M(lay, r"""
public static int put(java.util.UUID u, String name, int part, String[] g) {
  if (u == null || part < 0 || part > 1) return 0;
  String k = u.toString();
  Object o = own(k);
  if (ERR.equals(o)) return 0;
  Object[] nx = new Object[] { null, null, null, null, Boolean.FALSE, null };
  if (o instanceof Object[]) {
    Object[] r = (Object[]) o;
    for (int i = 0; i < nx.length && i < r.length; i++) nx[i] = r[i];
  }
  nx[part] = null;
  if (g != null) nx[part] = copy(g);
  if (name != null) NAMES.put(k, name);
  DIRTY.put(k, Boolean.TRUE);
  OWN.put(k, nx);
  saveSoon(k);
  return 1;
}""")
M(lay, r"""
public static int saveDefault(int part, String[] g) {
  if (part < 0 || part > 1 || g == null) return 0;
  settleDef();
  Object[] d = DEF;
  Object[] nx = new Object[] { null, null, null, null, Boolean.FALSE, null };
  if (d != null) { for (int i = 0; i < 5 && i < d.length; i++) nx[i] = d[i]; }
  nx[part] = copy(g);
  DEF = nx;
  saveSoon(DEF_KEY);
  return 1;
}""")
M(lay, r"""
public static int clearDefault(int part) {
  if (part < 0 || part > 1) return 0;
  settleDef();
  Object[] d = DEF;
  if (d == null) { saveSoon(DEF_KEY); return 1; }
  Object[] nx = new Object[] { d[0], d[1], d[2], d[3], d[4], null };
  nx[part] = null;
  if (empty(nx) && !Boolean.TRUE.equals(nx[4])) DEF = null;
  else DEF = nx;
  saveSoon(DEF_KEY);
  return 1;
}""")
# at start (setup, after MenuIO.begin): the server default file -> DEF (a 0.3.28 file is updated once: settleDef at the first join)
M(lay, r"""
public static void loadDefault() {
  DEF_PENDING.set(false);
  Object r = readFile(DEF_FILE, "layout-default.properties");
  DEF_BROKEN = BAD.equals(r);
  if (r instanceof Object[]) {
    DEF = (Object[]) r;
    if (Boolean.TRUE.equals(DEF[4])) {
      SNAPPED.remove(DEF_KEY);    // fix round 2: a 0.3.28 default (again) = a new update with its own History copy
      HFAIL.remove(DEF_KEY);
      MIGRATIONS = MIGRATIONS + 1;
      DEF_PENDING.set(true);
      @PKG@.MenuUtil.info("menu layout layout-default.properties: a 0.3.28 server default - its 0.3.29 one-time update runs when the first player joins (every mod has published its hub tabs by then)");
    }
  } else DEF = null;
  @PKG@.MenuUtil.info("menu shortcuts: " + (DEF != null ? "the server default from layout-default.properties" : "the standard shortcuts are the server default") + "; players' own shortcuts in layouts/");
}""")
M(lay, r"""
public static void flushAll() {
  java.util.ArrayList ks = new java.util.ArrayList(DIRTY.keySet());
  for (int i = 0; i < ks.size(); i++) saveNow((String) ks.get(i));
}""")
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
  java.util.ArrayList ms = new java.util.ArrayList(MIGRATED.keySet());
  for (int i = 0; i < ms.size(); i++) { if (!onlineK.contains(ms.get(i))) MIGRATED.remove(ms.get(i)); }
}""")
'''
rep(_lb, LAYOUT29)

# ---------------------------------------------------------------------------------------------------------------- MenuHub: route + pickTab
rep('''public static String click(@PR@ pr, String data, String hub, String tab) {
  if (data == null || data.indexOf("\\"hub:") < 0) return null;
  String a = @PKG@.HubBar.jsonStr(data, "a");
  if (!a.startsWith("hub:")) return null;
  if (a.equals("hub:back")) return "menu";
  return @PKG@.HubBar.handle(pr, data, hub, tab);
}""")''', '''public static String click(@PR@ pr, String data, String hub, String tab) {
  if (data == null || data.indexOf("\\"hub:") < 0) return null;
  String a = @PKG@.HubBar.jsonStr(data, "a");
  if (!a.startsWith("hub:")) return null;
  if (a.equals("hub:back") || a.equals("hub:h:home")) return "menu";   // 0.3.29: row 1's Home = the Home page (never /skymenu)
  return @PKG@.HubBar.route(pr, data, hub, tab);                      // 0.3.29: kit 1.6 - row 1 (hub:h:<hub>), then the tabs / the X
}""")''')
rep('''public static String pick(String hub, java.util.UUID u) {
  java.util.ArrayList t = @PKG@.HubBar.tabs(hub, u);
  if (t.isEmpty()) return null;
  Object m = u == null ? null : @PKG@.HubBar.get("hub:last:" + u.toString());
  if (m instanceof java.util.Map) {
    Object l = ((java.util.Map) m).get(hub);
    for (int i = 0; i < t.size(); i++) {
      Object[] e = (Object[]) t.get(i);
      if (e[0].equals(l)) return (String) e[0];
    }
  }
  return (String) ((Object[]) t.get(0))[0];
}""")''', '''public static String pick(String hub, java.util.UUID u) {
  return @PKG@.HubBar.pickTab(hub, u);   // 0.3.29: the hub's default tab (Character -> Skills), else the last tab, else the first
}""")''')
rep('''public static int register() {
  for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) {
    @PKG@.HubBar.def(@PKG@.MenuData.HUB_ID[i], @PKG@.MenuData.HUB_TITLE[i], @PKG@.MenuData.HUB_CMD[i], @PKG@.MenuData.HUB_ICON[i]);
  }''', '''public static int register() {
  // 0.3.29 (kit 1.6): hub:def:<hub> = {title, command, icon, default tab}; hub:def:home = row 1's Home button; home:alert:SkyyMenu
  for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) {
    String dt = @PKG@.MenuData.HUB_DEFTAB[i];
    @PKG@.HubBar.def4(@PKG@.MenuData.HUB_ID[i], @PKG@.MenuData.HUB_TITLE[i], @PKG@.MenuData.HUB_CMD[i], @PKG@.MenuData.HUB_ICON[i], dt.length() == 0 ? null : dt);
  }
  @PKG@.HubBar.def4("home", @PKG@.MenuData.HOME_TITLE, "skymenu", @PKG@.MenuData.HOME_ICON, null);
  java.util.Map am = @PKG@.HubBar.map();
  if (am != null) {
    Object al = new @PKG@.MenuAlert();
    am.put("home:alert:SkyyMenu", al);
    @PKG@.HubBar.mine().put("home:alert:SkyyMenu", al);
  }''')
# MenuAlert: home:alert:<mod> = a java.util.function.Function: apply(UUID) -> null or up to 3 lines "text|target" (target = "<hub>:<tab>",
# "<hub>" or "edit"). SkyyMenu's own lines: the one-time update happened this session (until Done in Edit shortcuts), settings unreadable.
rep('''# setup(): hub:def:<hub> for the 7 hubs + Menu's own 7 tabs''', r'''mal.addInterface(pool.get("java.util.function.Function"))
C(mal, "public MenuAlert() { }")
M(mal, r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return null;
  java.util.UUID u = (java.util.UUID) o;
  StringBuilder sb = new StringBuilder();
  try {
    if (@PKG@.MenuLayout.MIGRATED.containsKey(u.toString())) sb.append(@PKG@.MenuData.AL_MIG).append("|edit");
    if (@PKG@.SetStore.isBroken(u)) { if (sb.length() > 0) sb.append('\n'); sb.append(@PKG@.MenuData.AL_SET).append("|settings:settings"); }
  } catch (Throwable t) { return null; }
  return sb.length() == 0 ? null : sb.toString();
}""")
# setup(): hub:def:<hub> for the 7 hubs + Menu's own 7 tabs''')

# ---------------------------------------------------------------------------------------------------------------- MenuPage: fields + guards
rep('''for f in ("public boolean editing;", "public int editSel;", "public int[] lay;", "public int[] occ;", "public boolean[] hid;"):
    F(page, f)''', '''for f in ("public boolean editing;", "public int editSel;", "public boolean[] hid;"):   # 0.3.29: lay / occ went with the 9 x 6 main view
    F(page, f)
# 0.3.29: Home / Teleport - grid = the keys drawn (35), gridN = the slots of the grid on screen (35 on Home / Teleport, 54 in the classic
# views), addSlot = the empty slot the + Add list fills (-1 = no list), addPage / addPages / addKeys = that list, alertT = Right now's targets
for f in ("public String[] grid;", "public int gridN;", "public int addSlot;", "public int addPage;", "public int addPages;",
          "public String[] addKeys;", "public String[] alertT;"):
    F(page, f)''')
rep('''  this.editing = false;
  this.editSel = -1;
}""")
# 0.2 SettingsPage fields + constructor right here''', '''  this.editing = false;
  this.editSel = -1;
  this.addSlot = -1;
  this.gridN = 54;
}""")
# 0.2 SettingsPage fields + constructor right here''')
rep('''public void put(java.util.ArrayList slots, int idx, String icon, String name, String body, String foot, String act, boolean dim) {
  if (idx < 0 || idx >= 54) return;''', '''public void put(java.util.ArrayList slots, int idx, String icon, String name, String body, String foot, String act, boolean dim) {
  if (idx < 0 || idx >= 54 || idx >= slots.size()) return;   // 0.3.29: Home / Teleport have 35 slots''')
rep('''    for (int i = 0; i < 54; i++) empty.add(new @IGS@());''', '''    for (int i = 0; i < this.gridN; i++) empty.add(new @IGS@());   // 0.3.29: the grid on screen (35 on Home / Teleport)''')
rep('''    if (idx < 0 || idx >= 54 || this.acts == null) { @PKG@.MenuUtil.info("unexpected slot payload: " + data); return; }''',
    '''    if (idx < 0 || idx >= 54 || idx >= this.gridN || this.acts == null) { @PKG@.MenuUtil.info("unexpected slot payload: " + data); return; }''')
# simplify pass 1: the retired 9 x 6 main view's code goes - the 0.3.17 edit-mode tiles + marks, the 0.3.28 warp filler (Teleport is a
# 7 x 5 grid page: fillAutoWarps), the main-view fillStatic (moved below tileLook: the classic views only) and nav's main-view controls
rep(block('''# 0.3.17: a tile in edit mode - it never runs its action; the picked-up one is named "[Moving] ..."''',
          '''        this.editSel >= 0 ? @PKG@.MenuData.EMPTY_FOOT_MOVE : @PKG@.MenuData.EMPTY_FOOT_PICK, "eslot", false);
  }
}""")
'''), '''# 0.3.29: the 0.3.17 edit-mode tiles of the 9 x 6 main view are retired (Home: editTile2 / emptyMark)
''')
rep(block('''M(page, r"""
public void fillStatic(java.util.ArrayList slots) {''', '''  if (edit) editMarks(slots);
}""")
'''), '''# 0.3.29: fillStatic (the classic views' fixed entries) is defined after tileLook
''')
rep(block('''M(page, r"""
public void fillWarps(java.util.ArrayList slots) {''', '''        null, "info", true);
  }
}""")
'''), '''# 0.3.29: the 0.3.28 warp filler is retired (the Teleport grid page fills its warps: fillAutoWarps)
''')
rep(block('''M(page, r"""
public void nav(java.util.ArrayList slots) {''', '''"esrvclear", false);
    }
  }
'''), '''M(page, r"""
public void nav(java.util.ArrayList slots) {
  String back = this.view.equals("player") ? "Players Online" : "Home";   // 0.3.29: the classic views only (Home is a grid page)
  put(slots, 45, @PKG@.MenuData.ICON_BACK, "Go Back", "Back to " + back + ".", "Click to go back", "back", false);
  put(slots, 49, @PKG@.MenuData.ICON_CLOSE, "Close", "Close the menu.", "Click to close", "close", false);
''')

# ---------------------------------------------------------------------------------------------------------------- MenuPage: Home + Teleport (before fill)
_fb = block('''M(page, r"""
public void fill(java.util.ArrayList slots) {''', '''  if (this.pages > 1) this.title = this.title + "  (page " + (this.pageNo + 1) + " of " + this.pages + ")";
}""")
''')
DASH29 = r'''# ================= 0.3.29 MenuPage: HOME + TELEPORT (the 7 x 5 grid pages) - the shortcut keys, the grid, the editor's grid, + Add =================
M(page, r"""
public static String pageOf(int page, int pages) { return pages > 1 ? "  (page " + (page + 1) + " of " + pages + ")" : ""; }""")
M(page, r"""
public boolean isDash() {
  String v = this.view == null ? "main" : this.view;
  return v.equals("main") || v.equals("tp");
}""")
M(page, "public int part() { return \"tp\".equals(this.view) ? 1 : 0; }")
M(page, r"""
public static String[] gone(String icon, String name) {
  return new String[] { icon, name, "That is not on this server right now.", "Not on this server", null, "gone" };
}""")
# an old 0.3.28 tile as a shortcut: its rule, text, icon and action exactly as the 0.3.28 main view drew it (fillStatic)
M(page, r"""
public String[] tileLook(int i, boolean admin) {
  java.util.UUID me = this.playerRef.getUuid();
  String act = @PKG@.MenuData.E_ACT[i];
  String name = @PKG@.MenuData.E_NAME[i];
  String body = @PKG@.MenuData.E_BODY[i];
  String icon = @PKG@.MenuData.E_ICON[i];
  if (!tileVisible(i, admin)) return new String[] { icon, name, "", "", null, "perm" };
  if ("profile".equals(act)) body = profileBody();
  if ("cmdc:pets".equals(act)) {
    if (!@PKG@.PetTile.installed()) return gone(icon, name);
    String[] pi = @PKG@.PetTile.of(me);
    name = @PKG@.PetTile.title(pi);
    body = @PKG@.PetTile.body(me, pi);
    icon = @PKG@.PetTile.icon(pi);
  }
  if (body.indexOf("%PURSE%") >= 0) body = body.replace("%PURSE%", purseText());
  if (body.indexOf("%BANK%") >= 0) body = body.replace("%BANK%", bankText());
  String c = cmdOf(act);
  boolean dim = c != null && @PKG@.MenuUtil.cmd(c) == null;
  String need = dim ? null : @PKG@.MenuUtil.needOf(lineOf(act));
  if (need != null) return new String[] { icon, name + " (update needed)", body, "Needs " + need + " on this server", act, "dim" };
  String foot = dim ? "Not installed on this server" : @PKG@.MenuData.E_FOOT[i];
  return new String[] { icon, name + (dim ? " (not installed)" : ""), body, foot == null ? "Click to open!" : foot, act, dim ? "dim" : "ok" };
}""")
# the classic views' fixed entries (Players: Accept / Deny) - drawn the way a tile shortcut is ("perm" / "gone" = not drawn)
M(page, r"""
public void fillStatic(java.util.ArrayList slots) {
  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);
  for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {
    if (!@PKG@.MenuData.E_VIEW[i].equals(this.view)) continue;
    String[] l = tileLook(i, admin);
    if (l[5].equals("ok") || l[5].equals("dim")) put(slots, @PKG@.MenuData.E_SLOT[i], l[0], l[1], l[2], l[3], l[4], l[5].equals("dim"));
  }
}""")
M(page, r"""
public static String tabIcon(String h, String t) {
  String k = h + ":" + t;
  for (int i = 0; i < @PKG@.MenuData.E_KEY.length; i++) { if (@PKG@.MenuData.MIG_TAB[i].equals(k)) return @PKG@.MenuData.E_ICON[i]; }
  int hi = @PKG@.MenuHub.hubIndex(h);
  return hi < 0 ? @PKG@.MenuData.ICON_EMPTY : @PKG@.MenuData.HUB_ICON[hi];
}""")
M(page, r"""
public static int tpEntry(String k) {
  for (int i = 0; i < @PKG@.MenuData.TPK_KEY.length; i++) { if (@PKG@.MenuData.TPK_KEY[i].equals(k)) return @PKG@.MenuData.TPK_E[i]; }
  return -1;
}""")
# what a shortcut key draws: { icon, name, hover text, foot, action (null = none), state } - state "ok", "dim" (not installed / locked),
# "gone" (not on this server: hidden; the editor shows it so it can be removed) or "perm" (not for this player: fully hidden, the
# 2026-09-25 rule). Runs on the world thread while the page is drawn.
# a warp tile { icon, name, hover text (+ pos), foot, action, state } - open or locked (look() and fillAutoWarps)
M(page, r"""
public String[] warpTile(String n, @WRP@ w, String pos) {
  String id = @PKG@.MenuUtil.safe(w.getId());
  boolean open = @PKG@.MenuUtil.isWarpUnlocked(this.playerRef, w.getId());
  return new String[] { open ? @PKG@.MenuData.ICON_WARP : @PKG@.MenuData.ICON_WARP_LOCKED, open ? id : id + " (locked)",
                        "Warp " + id + ".\nWorld: " + @PKG@.MenuUtil.safe(w.getWorld()) + pos,
                        open ? "Click to warp!" : "Locked - you have not unlocked this warp yet", open ? "warp:" + n : "locked:" + n, open ? "ok" : "dim" };
}""")
M(page, r"""
public String[] look(String k, boolean admin) {
  java.util.UUID me = this.playerRef.getUuid();
  if (k == null) return null;
  if (k.startsWith("hub:")) {
    String h = k.substring(4);
    int hi = @PKG@.MenuHub.hubIndex(h);
    if (hi < 0) return gone(@PKG@.MenuData.ICON_EMPTY, k);
    java.util.ArrayList t = @PKG@.HubBar.tabs(h, me);
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < t.size() && i < 9; i++) { if (i > 0) sb.append(", "); sb.append((String) ((Object[]) t.get(i))[1]); }
    String body = @PKG@.MenuData.HUB_BLURB[hi] + "\n" + (t.isEmpty() ? @PKG@.MenuData.HUB_SOON[hi] : "Tabs: " + sb.toString()) + "\nCommand: /" + @PKG@.MenuData.HUB_CMD[hi];
    return new String[] { @PKG@.MenuData.HUB_ICON[hi], @PKG@.MenuData.HUB_TITLE[hi], body, "Click to open!", "sc:" + k, "ok" };
  }
  if (k.startsWith("tab:")) {
    int c = k.indexOf(':', 4);
    if (c < 0) return gone(@PKG@.MenuData.ICON_EMPTY, k);
    String h = k.substring(4, c);
    String tb = k.substring(c + 1);
    int hi = @PKG@.MenuHub.hubIndex(h);
    String icon = tabIcon(h, tb);
    Object o = @PKG@.HubBar.get("hub:tab:" + h + ":" + tb);
    if (hi < 0 || !(o instanceof Object[]) || ((Object[]) o).length < 6) return gone(icon, (hi < 0 ? h : @PKG@.MenuData.HUB_TITLE[hi]) + " > " + tb);
    Object[] e = (Object[]) o;
    String lab = (e[1] instanceof String) ? @PKG@.HubBar.clean((String) e[1]) : tb;
    if (!@PKG@.HubBar.visible(e, me)) return new String[] { icon, lab, "", "", null, "perm" };
    String cmd = (e[3] instanceof String) ? (String) e[3] : "";
    String body = @PKG@.MenuData.HUB_TITLE[hi] + " > " + lab + " - a page of the " + @PKG@.MenuData.HUB_TITLE[hi] + " hub." + (cmd.length() > 0 ? "\nCommand: /" + cmd : "");
    return new String[] { icon, lab, body, "Click to open!", "sc:" + k, "ok" };
  }
  if (k.startsWith("tile:")) {
    int i = @PKG@.MenuLayout.keyIndex(k.substring(5));
    if (i < 0) return gone(@PKG@.MenuData.ICON_EMPTY, k);
    return tileLook(i, admin);
  }
  if (k.startsWith("tp:")) {
    int i = tpEntry(k);
    if (i < 0) return gone(@PKG@.MenuData.ICON_EMPTY, k);
    String act = @PKG@.MenuData.E_ACT[i];
    String c = cmdOf(act);
    boolean dim = c != null && @PKG@.MenuUtil.cmd(c) == null;
    return new String[] { @PKG@.MenuData.E_ICON[i], @PKG@.MenuData.E_NAME[i] + (dim ? " (not installed)" : ""), @PKG@.MenuData.E_BODY[i],
                          dim ? "Not installed on this server" : @PKG@.MenuData.E_FOOT[i], act, dim ? "dim" : "ok" };
  }
  if (k.startsWith("warp:")) {
    String n = k.substring(5);
    @TPP@ tp = null;
    try { tp = @TPP@.get(); } catch (Throwable t) { tp = null; }
    if (tp == null || !tp.isWarpsLoaded()) return new String[] { @PKG@.MenuData.ICON_WARP, n, "Warp " + n + ".\nThe warp list is still loading.", "Click to warp!", "warp:" + n, "ok" };
    @WRP@ w = (@WRP@) tp.getWarps().get(n);
    if (w == null) return gone(@PKG@.MenuData.ICON_WARP_LOCKED, n);
    return warpTile(n, w, "");
  }
  return gone(@PKG@.MenuData.ICON_EMPTY, k);
}""")
M(page, r"""
public String nameOf(String k) {
  String[] l = look(k, true);
  return l == null ? "That shortcut" : l[1];
}""")
M(page, r"""
public void editTile2(java.util.ArrayList slots, int s, String icon, String name) {
  boolean sel = s == this.editSel;
  put(slots, s, icon, sel ? "[Moving] " + name : name, sel ? @PKG@.MenuData.HT_SEL_BODY : @PKG@.MenuData.HT_TILE_BODY,
      sel ? @PKG@.MenuData.HT_SEL_FOOT : (this.editSel >= 0 ? @PKG@.MenuData.HT_SWAP_FOOT : @PKG@.MenuData.HT_PICK_FOOT), "eslot", false);
}""")
M(page, r"""
public void drawKey(java.util.ArrayList slots, int s, String k, boolean admin) {
  String[] l = look(k, admin);
  if (l == null) return;
  String st = l[5];
  if (this.editing) {
    if (st.equals("perm")) { this.hid[s] = true; return; }
    editTile2(slots, s, l[0], l[1] + (st.equals("gone") ? " (not on this server)" : ""));
    return;
  }
  if (st.equals("perm") || st.equals("gone")) return;
  put(slots, s, l[0], l[1], l[2], l[3], l[4], st.equals("dim"));
}""")
M(page, r"""
public void emptyMark(java.util.ArrayList slots, int s) {
  boolean mv = this.editSel >= 0;
  put(slots, s, @PKG@.MenuData.ICON_EMPTY, @PKG@.MenuData.HT_EMPTY_NAME, mv ? @PKG@.MenuData.HT_EMPTY_MOVE : @PKG@.MenuData.HT_EMPTY_ADD,
      mv ? @PKG@.MenuData.HT_EMPTY_FOOT_MOVE : @PKG@.MenuData.HT_EMPTY_FOOT_ADD, "eslot", false);
}""")
# + Add: every hub, every hub tab this player can see (from the registry - other mods' tabs appear when they are loaded), every 0.3.28
# tile this player can see (not Hover Tooltips), every teleport target; on the Teleport grid: the teleport targets only
M(page, r"""
public java.util.ArrayList candidates(boolean home, boolean admin) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.UUID me = this.playerRef.getUuid();
  if (home) {
    for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) out.add("hub:" + @PKG@.MenuData.HUB_ID[i]);
    for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) {
      java.util.ArrayList t = @PKG@.HubBar.tabs(@PKG@.MenuData.HUB_ID[i], me);
      for (int j = 0; j < t.size(); j++) out.add("tab:" + @PKG@.MenuData.HUB_ID[i] + ":" + (String) ((Object[]) t.get(j))[0]);
    }
    for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {
      if (!@PKG@.MenuLayout.isMain(i) || "-".equals(@PKG@.MenuData.MIG[i])) continue;
      if (@PKG@.MenuData.MIG_TAB[i].length() > 0 && out.contains("tab:" + @PKG@.MenuData.MIG_TAB[i])) continue;   // fix round 2: listed once (as its tab)
      String[] l = tileLook(i, admin);
      if (l[5].equals("ok") || l[5].equals("dim")) out.add("tile:" + @PKG@.MenuData.E_KEY[i]);
    }
  }
  for (int i = 0; i < @PKG@.MenuData.TPK_KEY.length; i++) out.add(@PKG@.MenuData.TPK_KEY[i]);
  try {
    @TPP@ tp = @TPP@.get();
    if (tp != null && tp.isWarpsLoaded()) {
      java.util.ArrayList ws = new java.util.ArrayList();
      java.util.Iterator it = tp.getWarps().keySet().iterator();
      while (it.hasNext()) { String w = String.valueOf(it.next()); if (@PKG@.MenuLayout.okWarp(w)) ws.add(w); }
      java.util.Collections.sort(ws);
      for (int i = 0; i < ws.size(); i++) out.add("warp:" + (String) ws.get(i));
    }
  } catch (Throwable t) { }
  return out;
}""")
M(page, r"""
public static String kindOf(String k) {
  if (k.startsWith("hub:")) return "A hub.";
  if (k.startsWith("tab:")) return "One page of a hub.";
  if (k.startsWith("tile:")) return "A tile of the old menu.";
  return "A teleport.";
}""")
M(page, r"""
public void fillAdd(java.util.ArrayList slots, boolean home, boolean admin) {
  java.util.UUID me = this.playerRef.getUuid();
  this.grid = @PKG@.MenuLayout.grid(me, part());
  java.util.ArrayList c = candidates(home, admin);
  java.util.ArrayList left = new java.util.ArrayList();
  for (int i = 0; i < c.size(); i++) { if (!@PKG@.MenuLayout.hasSame(this.grid, (String) c.get(i))) left.add(c.get(i)); }
  int per = @PKG@.MenuData.HG_N;
  this.addPages = left.isEmpty() ? 1 : (left.size() + per - 1) / per;
  if (this.addPage >= this.addPages) this.addPage = this.addPages - 1;
  if (this.addPage < 0) this.addPage = 0;
  this.addKeys = new String[per];
  for (int s = 0; s < per; s++) {
    int k = this.addPage * per + s;
    if (k >= left.size()) break;
    String key = (String) left.get(k);
    String[] l = look(key, admin);
    if (l == null || l[5].equals("perm") || l[5].equals("gone")) continue;
    this.addKeys[s] = key;
    put(slots, s, l[0], l[1], kindOf(key) + "\n" + l[2], "Click to put it in the empty slot", "eadd", false);
  }
  if (left.isEmpty()) put(slots, @PKG@.MenuData.HG_CR * @PKG@.MenuData.HG_COLS + @PKG@.MenuData.HG_CC, @PKG@.MenuData.ICON_NO_WARPS, "Nothing left to add",
                          @PKG@.MenuData.HT_NONE_LEFT, null, "info", true);
}""")
# the Teleport page: warps nobody placed fill the free slots of rows 4 and 5 (Prev / Next page through them)
M(page, r"""
public void fillAutoWarps(java.util.ArrayList slots) {
  @TPP@ tp = null;
  try { tp = @TPP@.get(); } catch (Throwable t) { }
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.Map warps = null;
  boolean placed = false;
  for (int s = 0; s < this.grid.length; s++) { if (this.grid[s] != null && this.grid[s].startsWith("warp:")) placed = true; }
  if (tp != null && tp.isWarpsLoaded()) {
    warps = tp.getWarps();
    java.util.Iterator it = warps.keySet().iterator();
    while (it.hasNext()) { String k = String.valueOf(it.next()); if (!@PKG@.MenuLayout.has(this.grid, "warp:" + k)) keys.add(k); }
    java.util.Collections.sort(keys);
  }
  java.util.ArrayList free = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.MenuData.TP_AUTO.length; i++) {
    int s = @PKG@.MenuData.TP_AUTO[i];
    if (this.grid[s] == null) free.add(Integer.valueOf(s));
  }
  int per = free.size();
  if (per == 0) return;
  this.pages = paging(keys.size(), per);
  for (int i = 0; i < per; i++) {
    int k = this.pageNo * per + i;
    if (k >= keys.size()) break;
    String key = (String) keys.get(k);
    @WRP@ w = (@WRP@) warps.get(key);
    if (w == null) continue;
    String pos = "";
    try {
      @V3D@ p = w.getTransform().getPosition();
      pos = "\nX " + (long) Math.floor(p.x) + "   Y " + (long) Math.floor(p.y) + "   Z " + (long) Math.floor(p.z);
    } catch (Throwable t) { }
    String[] l = warpTile(key, w, pos);
    put(slots, ((Integer) free.get(i)).intValue(), l[0], l[1], l[2], l[3], l[4], l[5].equals("dim"));
  }
  if (keys.isEmpty() && !placed) {
    put(slots, ((Integer) free.get(per > 3 ? 3 : 0)).intValue(), @PKG@.MenuData.ICON_NO_WARPS, "No warps yet",
        tp == null || warps != null ? "No warps have been set on this server yet.\nAn admin can stand somewhere and type /warp set [name]." : "The warp list is still loading.\nOpen this menu again in a moment.",
        null, "info", true);
  }
}""")
M(page, r"""
public void fillDash(java.util.ArrayList slots) {
  boolean home = this.view.equals("main");
  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);
  if (this.editing && this.addSlot >= 0) { fillAdd(slots, home, admin); return; }
  this.grid = @PKG@.MenuLayout.grid(this.playerRef.getUuid(), part());
  for (int s = 0; s < this.grid.length && s < slots.size(); s++) {
    String k = this.grid[s];
    if (k == null) { if (this.editing) emptyMark(slots, s); continue; }
    drawKey(slots, s, k, admin);
  }
  if (!home && !this.editing) fillAutoWarps(slots);
}""")
M(page, r"""
public void fill(java.util.ArrayList slots) {
  int vi = @PKG@.MenuData.viewIndex(this.view);
  this.view = @PKG@.MenuData.V_KEY[vi];
  this.title = @PKG@.MenuData.V_TITLE[vi];
  this.pages = 1;
  if (isDash()) {
    fillDash(slots);
    if (this.pages <= 1) this.pageNo = 0;
    return;
  }
  fillStatic(slots);
  if (this.view.equals("players")) fillPlayers(slots);
  else if (this.view.equals("player")) fillPlayer(slots);
  else if (this.view.equals("mods")) fillMods(slots);
  if (this.pages <= 1) this.pageNo = 0;
  nav(slots);
  this.title = this.title + pageOf(this.pageNo, this.pages);
}""")
'''
rep(_fb, DASH29)

# ---------------------------------------------------------------------------------------------------------------- MenuPage: hub names + build
_bb = block('''# 0.3.28: the views that are hub tabs draw in the hub shell: tp = World > Teleport, players / player = Social > Players, mods = Settings >
''', '''  ev.addEventBinding(@BT@.Dismissing, hub ? "#SkyyMenuH" : "#SkyyMenu", @EVD@.of("a", "mesc"), false);
  if (hub) """ + MH_BUILD + r"""
}""")
''')
BUILD29 = r'''# 0.3.29: every view is a hub page: main = Home (row 1, Home active), tp = World > Teleport, players / player = Social > Players, mods =
# Settings > Mods (the classic 9 x 6 views keep the 0.3.28 body in the kit 1.6 row shell)
M(page, r"""
public String hubName() {
  String v = this.view == null ? "main" : this.view;
  if (v.equals("main")) return "home";
  if (v.equals("tp")) return "world";
  if (v.equals("players") || v.equals("player")) return "social";
  return "settings";
}""")
M(page, r"""
public String hubTab() {
  String v = this.view == null ? "main" : this.view;
  if (v.equals("tp")) return "teleport";
  if (v.equals("players") || v.equals("player")) return "players";
  if (v.equals("mods")) return "mods";
  return null;
}""")
# Right now: every bridge key home:alert:<mod> (sorted) holding a java.util.function.Function; apply(UUID) -> up to 3 lines "text|target"
# (a throw = skipped + one warning per key). At most AL_SHOW lines in all; each text clipped to AL_MAX characters.
M(page, r"""
public java.util.ArrayList alerts() {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Map br = @PKG@.MenuUtil.bridge();
  java.util.ArrayList ks = new java.util.ArrayList();
  try {
    java.util.Iterator it = br.keySet().iterator();
    while (it.hasNext()) { Object k = it.next(); if ((k instanceof String) && ((String) k).startsWith("home:alert:")) ks.add(k); }
  } catch (Throwable t) { }
  java.util.Collections.sort(ks);
  for (int i = 0; i < ks.size(); i++) {
    String key = (String) ks.get(i);
    Object f = br.get(key);
    if (!(f instanceof java.util.function.Function)) continue;
    Object r = null;
    try { r = ((java.util.function.Function) f).apply(this.playerRef.getUuid()); }
    catch (Throwable t) {
      r = null;
      if (@PKG@.MenuData.TILE_WARNED.putIfAbsent(key, key) == null) @PKG@.MenuUtil.warn("the Home alert " + key + " failed (skipped): " + t);
    }
    if (!(r instanceof String)) continue;
    String[] ls = ((String) r).split("\n");
    int n = 0;
    for (int j = 0; j < ls.length && n < 3; j++) {
      String ln = ls[j].trim();
      if (ln.length() == 0) continue;
      int bar = ln.lastIndexOf('|');
      String tx = bar >= 0 ? ln.substring(0, bar) : ln;
      String tg = bar >= 0 ? ln.substring(bar + 1).trim() : "";
      tx = @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(tx).trim(), @PKG@.MenuData.AL_MAX);
      if (tx.length() == 0) continue;
      out.add(new String[] { tx, tg });
      n = n + 1;
      if (out.size() >= @PKG@.MenuData.AL_SHOW) return out;
    }
  }
  return out;
}""")
M(page, r"""
public int youLine(@UCB@ b, int n, String text) {
  if (n >= @PKG@.MenuData.UI_HYL.length) return n;
  b.appendInline("#SkyyMHmYou", @PKG@.MenuData.UI_HYL[n]);
  b.set("#SkyyMHmYL" + n + ".Text", text);
  return n + 1;
}""")
M(page, r"""
public static String vitMax(Object[] vit, int i) {
  if (vit == null || i >= vit.length || !(vit[i] instanceof String[])) return null;
  String[] e = (String[]) vit[i];
  return e.length > 0 ? e[0] : null;
}""")
# YOU: the numbers players check most, from the existing bridge keys / the stat map (missing ones are left out); a click = Character > Stats
M(page, r"""
public void youPanel(@UCB@ b, @UEB@ ev, @REF@ ref, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HYOU);
  b.appendInline("#SkyyMHmYou", @PKG@.MenuData.UI_HYT);
  b.appendInline("#SkyyMHmYou", @PKG@.MenuData.UI_HYN);
  b.set("#SkyyMHmYN.Text", @PKG@.MenuUtil.safe(this.playerRef.getUsername()));
  int n = 0;
  String cls = @PKG@.StatsCalc.className(u);
  if (cls != null) n = youLine(b, n, "Class: " + cls);
  String pn = @PKG@.StatsCalc.profileName(u);
  if (pn != null) n = youLine(b, n, "Profile: " + pn);
  int lv = @PKG@.StatsCalc.overall(u);
  if (lv >= 0) {
    n = youLine(b, n, "Overall Level " + lv);
    Object[] ov = @PKG@.StatsCalc.overallInfo(u);
    int fill = 0;
    if (ov != null && ov.length > 1 && (ov[1] instanceof Number)) {
      int t = ((Number) ov[1]).intValue() % 10;
      if (t < 0) t = 0;
      fill = (@PKG@.MenuData.YOU_BAR_W * t) / 10;
    }
    b.appendInline("#SkyyMHmYou", @PKG@.MenuData.UI_HYBAR0 + fill + @PKG@.MenuData.UI_HYBAR1);
  }
  long pu = @PKG@.MenuUtil.purse(u);
  if (pu >= 0L) n = youLine(b, n, "Coins: " + @PKG@.MenuUtil.fmt(pu));
  long bk = @PKG@.MenuUtil.bank(u);
  if (bk >= 0L) n = youLine(b, n, "Bank: " + @PKG@.MenuUtil.fmt(bk));
  Object[] vit = null;
  try { vit = @PKG@.StatsCalc.vitals(st, ref); } catch (Throwable t) { vit = null; }
  String hp = vitMax(vit, 0);
  if (hp != null) n = youLine(b, n, "Health: " + hp);
  String mp = vitMax(vit, 1);
  if (mp != null) n = youLine(b, n, "Mana: " + mp);
  b.appendInline("#SkyyMHmYou", @PKG@.MenuData.UI_HYH);
  ev.addEventBinding(@BT@.Activating, "#SkyyMHmYou", @EVD@.of("a", "hyou"));
}""")
M(page, r"""
public void nowPanel(@UCB@ b, @UEB@ ev) {
  java.util.ArrayList al = alerts();
  this.alertT = new String[al.size()];
  if (al.isEmpty()) { b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HNOWE); return; }
  b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HNOW);
  b.appendInline("#SkyyMHmNow", @PKG@.MenuData.UI_HNOWT);
  for (int i = 0; i < al.size() && i < @PKG@.MenuData.UI_HA.length; i++) {
    String[] a = (String[]) al.get(i);
    this.alertT[i] = a[1];
    b.appendInline("#SkyyMHmNow", @PKG@.MenuData.UI_HA[i]);
    b.set("#SkyyMHmA" + i + ".Text", a[0] + (a[1].length() > 0 ? "  >" : ""));
    ev.addEventBinding(@BT@.Activating, "#SkyyMHmA" + i, @EVD@.of("a", "halert" + i));
  }
}""")
M(page, r"""
public static int fbIndex(String w) {
  for (int i = 0; i < @PKG@.MenuData.FB_WORD.length; i++) { if (@PKG@.MenuData.FB_WORD[i].equals(w)) return i; }
  return -1;
}""")
# the foot row: Home = the info line (the status, else what to do) + the buttons; Teleport = the buttons, centred. Each sends a = "f<word>".
M(page, r"""
public void foot(@UCB@ b, @UEB@ ev, boolean home, String info) {
  java.util.ArrayList ws = new java.util.ArrayList();
  boolean add = this.editing && this.addSlot >= 0;
  if (add) {
    if (this.addPage > 0) ws.add("aprev");
    if (this.addPage < this.addPages - 1) ws.add("anext");
    ws.add("acancel");
  } else if (this.editing) {
    if (this.editSel >= 0) ws.add("eremove");
    ws.add("ereset");
    if (@PKG@.MenuUtil.isAdmin(this.playerRef)) { ws.add("esrv"); ws.add("estd"); }
    if (home && @PKG@.MenuLayout.oldOf(this.playerRef.getUuid()) != null) ws.add("eold");
    if (home && this.editSel < 0 && @PKG@.MenuLayout.hasOldDefault() && @PKG@.MenuUtil.isAdmin(this.playerRef)) ws.add("edold");
    ws.add("edone");
  } else {
    ws.add("hedit");
    if (!home && this.pageNo > 0) ws.add("prev");
    if (!home && this.pageNo < this.pages - 1) ws.add("next");
    ws.add("close");
  }
  String par = home ? "#SkyyMHmFoot" : "#SkyyMTpFoot";
  int used = 0;
  for (int k = 0; k < ws.size(); k++) {
    int fi = fbIndex((String) ws.get(k));
    used = used + (home ? @PKG@.MenuData.FB_W[fi] : @PKG@.MenuData.FB_TW[fi]) + @PKG@.MenuData.FB_GAP;
  }
  if (home) {
    b.appendInline(par, @PKG@.MenuData.UI_HINFO0 + (@PKG@.MenuData.HOME_FOOT_W - used) + @PKG@.MenuData.UI_HINFO1);
    b.set("#SkyyMHmInfo.Text", info == null ? "" : info);
  } else {
    int lead = (@PKG@.MenuData.TP_FOOT_W - used + @PKG@.MenuData.FB_GAP) / 2;
    if (lead > 0) b.appendInline(par, "Group { Anchor: (Width: " + lead + "); }");
  }
  for (int k = 0; k < ws.size(); k++) {
    String w = (String) ws.get(k);
    int fi = fbIndex(w);
    if (home || k > 0) b.appendInline(par, @PKG@.MenuData.UI_FSP);
    b.appendInline(par, home ? @PKG@.MenuData.UI_FBH[fi] : @PKG@.MenuData.UI_FBT[fi]);
    ev.addEventBinding(@BT@.Activating, (home ? "#SkyyMHmF" : "#SkyyMTpF") + w, @EVD@.of("a", "f" + w));
  }
}""")
M(page, r"""
public void buildDash(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st, java.util.ArrayList slots, boolean tipsOff) {
  boolean home = this.view.equals("main");
  java.util.UUID me = this.playerRef.getUuid();
  String stx = this.status == null ? "" : this.status;
  boolean add = this.editing && this.addSlot >= 0;
  @PKG@.MenuHub.ensure(me);
  if (home) {
""" + "\n".join("    " + ln for ln in HOME_JAVA.split("\n")) + r"""
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HMAIN);
    youPanel(b, ev, ref, st);
    b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HSP16);
    b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HMID);
    b.appendInline("#SkyyMHmMid", @PKG@.MenuData.UI_HMIDT);
    b.appendInline("#SkyyMHmMid", @PKG@.MenuData.UI_HGAP5);
    b.appendInline("#SkyyMHmMid", @PKG@.MenuData.UI_HGW);
    b.appendInline("#SkyyMGW", tipsOff ? @PKG@.MenuData.UI_HGRIDNT : @PKG@.MenuData.UI_HGRID);
    b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HSP16);
    nowPanel(b, ev);
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HGAP8);
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HFOOT);
    String info = stx.length() > 0 ? stx : (add ? @PKG@.MenuData.HT_ADD : (this.editing ? @PKG@.MenuData.HT_EDIT : (tipsOff ? @PKG@.MenuData.HT_HINT_OFF : @PKG@.MenuData.HT_HINT)));
    foot(b, ev, true, info);
    b.set("#SkyyMHmMidT.Text", add ? @PKG@.MenuData.HT_MID_ADD + pageOf(this.addPage, this.addPages)
                                   : (this.editing ? @PKG@.MenuData.HT_MID_EDIT : @PKG@.MenuData.HT_MID));
    ev.addEventBinding(@BT@.Dismissing, "#SkyyMHm", @EVD@.of("a", "mesc"), false);
    """ + HOME_BUILD + r"""
  } else {
""" + "\n".join("    " + ln for ln in TP_JAVA.split("\n")) + r"""
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_THINT);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TGAP3);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TROW);
    b.appendInline("#SkyyMTpRow", @PKG@.MenuData.UI_TLEAD);
    b.appendInline("#SkyyMTpRow", @PKG@.MenuData.UI_HGW);
    b.appendInline("#SkyyMGW", tipsOff ? @PKG@.MenuData.UI_HGRIDNT : @PKG@.MenuData.UI_HGRID);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_HGAP8);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TINFO);
    b.appendInline("#SkyyMTpInfo", @PKG@.MenuData.UI_TIN);
    b.appendInline("#SkyyMTpInfo", @PKG@.MenuData.UI_TID);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_HGAP8);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TFOOT);
    foot(b, ev, false, null);
    b.set("#SkyyMTpHint.Text", stx.length() > 0 ? stx : (add ? @PKG@.MenuData.HT_ADD : (this.editing ? @PKG@.MenuData.HT_EDIT : @PKG@.MenuData.HT_TP_HINT)));
    String iname = this.infoName;
    String ibody = this.infoBody;
    if (iname == null) {
      iname = add ? "Add a teleport" + pageOf(this.addPage, this.addPages)
                  : (this.editing ? "Editing the Teleport page - no dragging" : "Teleport" + pageOf(this.pageNo, this.pages));
      ibody = this.editing ? @PKG@.MenuData.HT_EDIT_START : @PKG@.MenuData.V_INTRO[@PKG@.MenuData.viewIndex("tp")];
    }
    String[] lines = (ibody == null ? "" : ibody).split("\n");
    b.set("#SkyyMTpIN.Text", iname);
    b.set("#SkyyMTpID.Text", lines.length > 0 ? lines[0] : "");
    ev.addEventBinding(@BT@.Dismissing, "#SkyyMTp", @EVD@.of("a", "mesc"), false);
    """ + TP_BUILD + r"""
  }
  b.set("#SkyyMGrid.Slots", slots);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyMGrid", @EVD@.of("a", "mslot"), false);
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.cleared = false;
  this.lastSend = System.currentTimeMillis();
  if (!this.watching && ref != null && st != null) {
    this.watching = true;
    try {
      Object ex = st.getExternalData();
      if (ex instanceof @EST@) this.world = ((@EST@) ex).getWorld();
    } catch (Throwable tw) { this.world = null; }
    this.joinSeen = @PKG@.PageGuard.joins(this.playerRef.getUuid());
    @PKG@.MenuWatch.schedule(this);
  }
  boolean tipsOff = @PKG@.Tips.isOff(this.playerRef.getUuid());
  boolean dash = isDash();
  int gn = dash ? @PKG@.MenuData.HG_N : 54;
  this.gridN = gn;
  this.acts = new String[54];
  this.names = new String[54];
  this.bodies = new String[54];
  this.hid = new boolean[54];
  java.util.ArrayList slots = new java.util.ArrayList();
  for (int i = 0; i < gn; i++) slots.add(filler());
  try { fill(slots); } catch (Throwable t) { @PKG@.MenuUtil.warn("menu view " + this.view + " failed: " + t); }
  if (dash) { buildDash(ref, b, ev, st, slots, tipsOff); return; }
  String stx = this.status == null ? "" : this.status;
  int nInfo = @PKG@.MenuData.HUB_INFO_LINES;
  @PKG@.MenuHub.ensure(this.playerRef.getUuid());
  if (hubName().equals("social")) {
""" + "\n".join("    " + ln for ln in MH_JAVA["social"].split("\n")) + r"""
  } else {
""" + "\n".join("    " + ln for ln in MH_JAVA["settings"].split("\n")) + r"""
  }
  b.appendInline("#SkyyMenu", stx.length() > 0 ? @PKG@.MenuData.UI_HINTST : @PKG@.MenuData.UI_HINT);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_INFOBOXH);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFONAME);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFODESC);
  for (int i = 0; i < nInfo; i++) b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFO[i]);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GAP);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GRIDWRAP);
  b.appendInline("#SkyyMGridWrap", tipsOff ? @PKG@.MenuData.UI_GRIDNOTIPS : @PKG@.MenuData.UI_GRID);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_FOOT);
  b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_LEAD);
  b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_BTNBACK);
  b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_SPACER);
  ev.addEventBinding(@BT@.Activating, "#SkyyMBack", @EVD@.of("a", "mback"));
  if (this.pages > 1) {
    b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_BTNPREV);
    b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_SPACER);
    b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_BTNNEXT);
    b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_SPACER);
    ev.addEventBinding(@BT@.Activating, "#SkyyMPrev", @EVD@.of("a", "mprev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyMNext", @EVD@.of("a", "mnext"));
  }
  b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_BTNCLOSE);
  ev.addEventBinding(@BT@.Activating, "#SkyyMClose", @EVD@.of("a", "mclose"));
  String hint = tipsOff ? "Tooltips off - the speech bubble at the top right turns them on. Click an item to use it."
                        : "Hover an item for details - click it to use it. Esc closes the menu.";
  b.set("#SkyyMHint.Text", stx.length() > 0 ? stx : hint);
  String iname = this.infoName;
  String ibody = this.infoBody;
  if (iname == null) {
    int vi = @PKG@.MenuData.viewIndex(this.view);
    iname = this.title;
    ibody = @PKG@.MenuData.V_INTRO[vi];
  }
  String[] lines = (ibody == null ? "" : ibody).split("\n");
  b.set("#SkyyMInfoName.Text", iname == null ? "" : iname);
  b.set("#SkyyMInfoDesc.Text", lines.length > 0 ? lines[0] : "");
  for (int i = 0; i < nInfo; i++) {
    String t = i + 1 < lines.length ? lines[i + 1] : "";
    if (i == nInfo - 1 && lines.length > nInfo + 1) t = t + "   ...";
    b.set("#SkyyMInfo" + i + ".Text", t);
  }
  b.set("#SkyyMGrid.Slots", slots);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyMGrid", @EVD@.of("a", "mslot"), false);
  ev.addEventBinding(@BT@.Dismissing, "#SkyyMenuH", @EVD@.of("a", "mesc"), false);
  """ + MH_BUILD + r"""
}""")
'''
rep(_bb, BUILD29)

# ---------------------------------------------------------------------------------------------------------------- MenuPage: the editor + shortcuts
_eb = block('''M(page, r"""
public void editInfo() {''', '''  this.status = t >= 0 ? @PKG@.MenuData.E_NAME[mv] + " and " + @PKG@.MenuData.E_NAME[t] + " swapped places." : @PKG@.MenuData.E_NAME[mv] + " moved.";
  rebuild();
}""")
''')
EDIT29 = r'''# ================= 0.3.29 EDIT SHORTCUTS (Home + Teleport; Skyy 2026-10-15 "have a way to remove and add them. so you can pick what shows up.
# and how its organized"). No dragging (AreItemsDraggable: false - every text says so): a tile click picks it up, another slot swaps / moves,
# Remove takes it off, an empty slot opens + Add. Saved at once per account (MenuLayout.put). Reset / Set default / Clear default / Old tiles
# back need a second click (cfgArm); the admin node is re-checked on the click. A layout file that cannot be read is never changed.
M(page, r"""
public void leaveEdit() {
  this.editing = false;
  this.editSel = -1;
  this.addSlot = -1;
}""")
M(page, r"""
public void startEdit() {
  this.editing = true;
  this.editSel = -1;
  this.addSlot = -1;
  this.addPage = 0;
  this.infoName = null;
  this.infoBody = null;
  this.status = @PKG@.MenuData.HT_EDIT_START;
}""")
# a changed grid saved (part 0 Home / 1 Teleport); false = it failed (the page already says so)
M(page, r"""
public boolean saveGrid(int p, String[] g) {
  if (@PKG@.MenuLayout.put(this.playerRef.getUuid(), this.playerRef.getUsername(), p, g) == 1) return true;
  this.status = "That did not work - try again.";
  rebuild();
  return false;
}""")
M(page, r"""
public void dashEditClick(int idx, String act) {
  java.util.UUID me = this.playerRef.getUuid();
  if (@PKG@.MenuLayout.unreadable(me)) { this.editSel = -1; this.addSlot = -1; this.status = @PKG@.MenuData.EDIT_WAIT; rebuild(); return; }
  int p = part();
  if (act.equals("eadd")) {
    if (this.addSlot < 0 || this.addKeys == null || idx < 0 || idx >= this.addKeys.length || this.addKeys[idx] == null) { this.status = "Pick a shortcut from the list."; rebuild(); return; }
    String k = this.addKeys[idx];
    String[] g = @PKG@.MenuLayout.grid(me, p);
    int at = this.addSlot;
    this.addSlot = -1;
    if (at < 0 || at >= g.length || g[at] != null) { this.status = "That slot is not free any more - nothing was added."; rebuild(); return; }
    if (@PKG@.MenuLayout.hasSame(g, k)) { this.status = nameOf(k) + " is on your grid already."; rebuild(); return; }
    g[at] = k;
    if (!saveGrid(p, g)) return;
    this.status = nameOf(k) + " added.";
    rebuild();
    return;
  }
  if (!act.equals("eslot") || this.grid == null || idx < 0 || idx >= this.grid.length) { rebuild(); return; }
  if (this.editSel < 0) {
    if (this.hid[idx]) { this.status = @PKG@.MenuData.KEPT_MSG; rebuild(); return; }
    if (this.grid[idx] == null) { this.addSlot = idx; this.addPage = 0; this.status = ""; rebuild(); return; }
    this.editSel = idx;
    this.status = "Picked up " + nameOf(this.grid[idx]) + " - click another slot to move it there, or press Remove.";
    rebuild();
    return;
  }
  if (idx == this.editSel) { this.editSel = -1; this.status = "Cancelled - nothing moved."; rebuild(); return; }
  int from = this.editSel;
  this.editSel = -1;
  if (this.hid[idx] || this.hid[from]) { this.status = @PKG@.MenuData.KEPT_MSG; rebuild(); return; }
  String[] g = @PKG@.MenuLayout.copy(this.grid);
  String a = g[from];
  String bb = g[idx];
  if (a == null) { this.status = "That move did not work - try again."; rebuild(); return; }
  g[idx] = a;
  g[from] = bb;
  if (!saveGrid(p, g)) return;
  this.status = bb != null ? nameOf(a) + " and " + nameOf(bb) + " swapped places." : nameOf(a) + " moved.";
  rebuild();
}""")
M(page, r"""
public void footClick(@REF@ ref, @ST@ st, String w) {
  String armed = this.cfgArm;
  this.cfgArm = null;
  this.status = "";
  java.util.UUID me = this.playerRef.getUuid();
  if (w.equals("close")) { closePage(ref, st); return; }
  if (w.equals("hedit")) {
    if (@PKG@.MenuLayout.unreadable(me)) { this.status = @PKG@.MenuData.EDIT_WAIT; rebuild(); return; }
    startEdit();
    rebuild();
    return;
  }
  if (w.equals("prev")) { if (this.pageNo > 0) this.pageNo = this.pageNo - 1; rebuild(); return; }
  if (w.equals("next")) { this.pageNo = this.pageNo + 1; rebuild(); return; }
  if (!this.editing) { rebuild(); return; }
  if (w.equals("acancel")) { this.addSlot = -1; this.status = "Nothing was added."; rebuild(); return; }
  if (w.equals("aprev")) { if (this.addPage > 0) this.addPage = this.addPage - 1; rebuild(); return; }
  if (w.equals("anext")) { this.addPage = this.addPage + 1; rebuild(); return; }
  if (w.equals("edone")) {
    leaveEdit();
    @PKG@.MenuLayout.MIGRATED.remove(me.toString());
    this.status = "Saved - your shortcuts work as normal again.";
    rebuild();
    return;
  }
  if (@PKG@.MenuLayout.unreadable(me)) { this.editSel = -1; this.status = @PKG@.MenuData.EDIT_WAIT; rebuild(); return; }
  int p = part();
  if (w.equals("eremove")) {
    if (this.editSel < 0 || this.grid == null || this.editSel >= this.grid.length || this.grid[this.editSel] == null) { this.editSel = -1; this.status = "Pick a tile up first, then press Remove."; rebuild(); return; }
    String[] g = @PKG@.MenuLayout.copy(this.grid);
    String gone = g[this.editSel];
    g[this.editSel] = null;
    this.editSel = -1;
    if (!saveGrid(p, g)) return;
    this.status = nameOf(gone) + " removed - it waits in + Add (click an empty slot).";
    rebuild();
    return;
  }
  if (w.equals("esrv") || w.equals("estd") || w.equals("edold")) {
    if (!@PKG@.MenuUtil.isAdmin(this.playerRef)) { this.status = "Only admins can change the server default shortcuts."; rebuild(); return; }
  }
  if (w.equals("edold") && p != 0) { this.status = "Old default works on the Home page."; rebuild(); return; }
  if (!w.equals(armed) && (w.equals("ereset") || w.equals("esrv") || w.equals("estd") || w.equals("eold") || w.equals("edold"))) {
    this.cfgArm = w;
    if (w.equals("ereset")) this.status = "Click Reset again: this page goes back to the default shortcuts.";
    else if (w.equals("esrv")) this.status = "Click Set default again: YOUR shortcuts become the server default (for players without their own).";
    else if (w.equals("estd")) this.status = "Click Clear default again: the standard shortcuts become the server default again.";
    else if (w.equals("edold")) this.status = "Click Old default again: the server default gets its old tiles back (as before the update).";
    else this.status = "Click Old tiles back again: your old menu tiles come back in place of the hubs.";
    rebuild();
    return;
  }
  this.editSel = -1;
  if (w.equals("ereset")) {
    @PKG@.MenuLayout.put(me, this.playerRef.getUsername(), p, null);
    this.status = "Back to the default shortcuts.";
  } else if (w.equals("esrv")) {
    if (@PKG@.MenuLayout.saveDefault(p, @PKG@.MenuLayout.grid(me, p)) == 1) this.status = "Saved - every player without their own shortcuts now gets yours.";
    else this.status = "That did not work - try again.";
  } else if (w.equals("estd")) {
    @PKG@.MenuLayout.clearDefault(p);
    this.status = "The standard shortcuts are the server default again.";
  } else if (w.equals("eold")) {
    String[] g = @PKG@.MenuLayout.oldTilesBack(me);
    if (g == null || @PKG@.MenuLayout.put(me, this.playerRef.getUsername(), 0, g) != 1) this.status = "There is no old layout to bring back.";
    else this.status = "Your old tiles are back where they were (the ones that did not fit wait in + Add).";
  } else if (w.equals("edold")) {
    String[] g = @PKG@.MenuLayout.oldDefaultBack();
    if (g == null || @PKG@.MenuLayout.saveDefault(0, g) != 1) this.status = "The server default has no old layout to bring back.";
    else this.status = "The server default has its old tiles back (for players without their own shortcuts).";
  }
  rebuild();
}""")
# a shortcut / a row-1 hub / an alert opens a tab: SkyyMenu's own views switch IN PLACE (the page stays, the mouse spot stays), its own pages
# open straight from the menu (the grid emptied first), any other tab through its bridge Function, else its command (HubBar.open)
M(page, r"""
public void openTab(@REF@ ref, @ST@ st, String h, String tb) {
  if (h == null || tb == null || @PKG@.MenuHub.hubIndex(h) < 0 || !@PKG@.HubBar.okId(tb)) { this.status = @PKG@.MenuData.HUB_TXT_FAIL; rebuild(); return; }
  if (h.equals("world") && tb.equals("teleport")) { leaveEdit(); open("tp"); rebuild(); return; }
  if (h.equals("social") && tb.equals("players")) { leaveEdit(); open("players"); rebuild(); return; }
  if (h.equals("settings") && tb.equals("mods")) {
    if (!@PKG@.MenuHub.visible("mods", this.playerRef)) { this.status = @PKG@.MenuData.HUB_TXT_FAIL; rebuild(); return; }
    leaveEdit();
    open("mods");
    rebuild();
    return;
  }
  if (h.equals("settings") && tb.equals("layout")) {
    if (@PKG@.MenuLayout.unreadable(this.playerRef.getUuid())) { this.status = @PKG@.MenuData.EDIT_WAIT; rebuild(); return; }
    open("main");
    startEdit();
    rebuild();
    return;
  }
  if (h.equals("character") && tb.equals("stats")) { openStats(ref, st); return; }
  if (h.equals("settings") && tb.equals("settings")) { openSettings(ref, st); return; }
  if (h.equals("settings") && tb.equals("setup")) { openAdmin(ref, st, null); return; }
  clearGrid();
  String r = @PKG@.HubBar.open(this.playerRef, this.playerRef.getUuid(), h, tb);
  if ("command".equals(r)) { @PKG@.RefreshTask.schedule(this, this.playerRef, 900L); return; }
  if (@PKG@.MenuHub.opened(r)) return;
  this.status = "missing".equals(r) ? "That page is not on this server right now." : @PKG@.MenuData.HUB_TXT_FAIL;
  rebuild();
}""")
M(page, r"""
public void openHub(@REF@ ref, @ST@ st, String h) {
  int hi = @PKG@.MenuHub.hubIndex(h);
  if (hi < 0) { this.status = @PKG@.MenuData.HUB_TXT_FAIL; rebuild(); return; }
  String tab = @PKG@.HubBar.pickTab(h, this.playerRef.getUuid());
  if (tab == null) { this.status = "[" + @PKG@.MenuData.HUB_TITLE[hi] + "] " + @PKG@.MenuData.HUB_SOON[hi]; rebuild(); return; }
  openTab(ref, st, h, tab);
}""")
M(page, r"""
public void shortcut(@REF@ ref, @ST@ st, String k) {
  if (k.startsWith("hub:")) { openHub(ref, st, k.substring(4)); return; }
  if (k.startsWith("tab:")) {
    int c = k.indexOf(':', 4);
    if (c > 4) { openTab(ref, st, k.substring(4, c), k.substring(c + 1)); return; }
  }
  this.status = "That shortcut does not work any more - Edit shortcuts can remove it.";
  rebuild();
}""")
M(page, r"""
public void youClick(@REF@ ref, @ST@ st) {
  leaveEdit();
  openStats(ref, st);
}""")
M(page, r"""
public void alertClick(@REF@ ref, @ST@ st, String n) {
  int i = -1;
  try { i = Integer.parseInt(n); } catch (Throwable t) { i = -1; }
  this.status = "";
  if (this.alertT == null || i < 0 || i >= this.alertT.length) { rebuild(); return; }
  String t = this.alertT[i] == null ? "" : this.alertT[i];
  if (t.equals("edit")) { openTab(ref, st, "settings", "layout"); return; }
  int c = t.indexOf(':');
  if (c > 0) { openTab(ref, st, t.substring(0, c), t.substring(c + 1)); return; }
  if (@PKG@.MenuHub.hubIndex(t) >= 0) { openHub(ref, st, t); return; }
  this.status = "That note has no page to open.";
  rebuild();
}""")
'''
rep(_eb, EDIT29)
rep(block('''  if (this.editing && this.view.equals("main")) { editClick(idx, act, armed); return; }''', '''    startEdit();
    rebuild();
    return;
  }
'''),
    '''  if (this.editing && isDash()) { dashEditClick(idx, act); return; }   // 0.3.29: Edit shortcuts (Home + Teleport)
  if (act.startsWith("sc:")) { shortcut(ref, st, act.substring(3)); return; }   // 0.3.29: a hub / tab shortcut
''')

rep(block('''  this.infoBody = this.bodies[idx];
  if (act.equals("tips")) {''', '''"Hover tooltips are on again.";
    rebuild();
    return;
  }
'''), '''  this.infoBody = this.bodies[idx];   // 0.3.29: no Hover Tooltips tile (Settings > General has the switch)
''')
# simplify: Tips.setOff had one caller - the Hover Tooltips tile above - so it goes too
rep('''# 1 = saved (memory now, file 500 ms later), 0 = the player's settings file is unreadable (nothing changed)
M(tip, r"""
public static int setOff(java.util.UUID u, boolean off) {
  if (u == null) return 0;
  return @PKG@.SetStore.set(u, @PKG@.MenuData.TIPS_KEY, !off, false);
}""")
''', '''# 0.3.29: Tips.setOff is gone (its only caller was the retired Hover Tooltips tile; Settings > General switches tooltips)
''')

# ---------------------------------------------------------------------------------------------------------------- MenuPage: row 1 / tab clicks
_hc = block('''M(page, r"""
public void hubClick(@REF@ ref, @ST@ st, String data) {''', '''  if (@PKG@.MenuHub.opened(r)) return;
  this.status = @PKG@.MenuData.HUB_TXT_FAIL;
  rebuild();
}""")
''')
HUBCLICK29 = r'''M(page, r"""
public void hubClick(@REF@ ref, @ST@ st, String data) {
  String a = @PKG@.HubBar.jsonStr(data, "a");
  if (!a.startsWith("hub:")) return;
  this.status = "";
  this.cfgArm = null;
  if (a.equals("hub:close")) { closePage(ref, st); return; }
  String myHub = hubName();
  String myTab = hubTab();
  if (a.startsWith("hub:h:")) {
    String h = a.substring(6);
    if (h.equals("home")) { leaveEdit(); open("main"); rebuild(); return; }
    if (h.equals(myHub)) { if (this.view.equals("player")) open("players"); rebuild(); return; }
    leaveEdit();
    openHub(ref, st, h);
    return;
  }
  if (a.equals("hub:back")) { leaveEdit(); open("main"); rebuild(); return; }
  String id = a.substring(4);
  if (myTab != null && id.equals(myTab)) { if (this.view.equals("player")) open("players"); rebuild(); return; }
  if (myHub.equals("home") || !@PKG@.HubBar.okId(id)) { this.status = @PKG@.MenuData.HUB_TXT_FAIL; rebuild(); return; }
  leaveEdit();
  openTab(ref, st, myHub, id);
}""")
'''
rep(_hc, HUBCLICK29)
rep('''    if (data.indexOf("\\"hub:") >= 0) { hubClick(ref, st, data); return; }   // 0.3.28: the hub bar of a menu view
''', '''    if (data.indexOf("\\"hub:") >= 0) { hubClick(ref, st, data); return; }   // 0.3.28: the hub bar of a menu view (0.3.29: + row 1)
    if (data.indexOf("\\"hyou\\"") >= 0 || data.indexOf("\\"halert") >= 0 || data.indexOf("\\"f") >= 0) {   // 0.3.29: Home / Teleport
      String fa = @PKG@.HubBar.jsonStr(data, "a");
      if (fa.equals("hyou")) { youClick(ref, st); return; }
      if (fa.startsWith("halert")) { alertClick(ref, st, fa.substring(6)); return; }
      if (fa.startsWith("f") && fbIndex(fa.substring(1)) >= 0) { footClick(ref, st, fa.substring(1)); return; }
    }
''')

# ---------------------------------------------------------------------------------------------------------------- the ready line
rep('''hubs: " + hubTabs + " own tabs, " + hubCmds + " of 5 hub commands (/character /char /storage /market /travel /social), Sky Window kit textures shipped; page guard on''',
    '''hubs: " + hubTabs + " own tabs, " + hubCmds + " of 5 hub commands (/character /char /storage /market /travel /social), Sky Window kit textures shipped; Home + Edit shortcuts (kit 1.6 row 1, 7 x 5 grid, " + @PKG@.MenuLayout.MIGRATIONS + " layout update(s) at start); page guard on''')

# ---------------------------------------------------------------------------------------------------------------- done
for _w in ("UI_SROOT", "UI_SACCENT", "UI_STITLE", "UI_SSTATUS", "UI_SGAP6", "#SkyyStgStatus", "#SkyyStgTitle", "UI_AROOT", "UI_AACCENT",
           "UI_ATITLE", "#SkyyAdmTitle", "MenuLayout.of(", "editClick(", 'MH_JAVA["world"]', "MenuLayout.swap(", "MenuLayout.reset(",
           "HubBar.handle(this.playerRef, data, hn, my)", "HubBar.build(b, ev"):
    assert _w not in s, "0.3.29: %s is still used" % _w
assert s.count("install_hub_bar(pool, PKG + \".HubBar\", CtField, CtNewMethod, row=True)") == 1
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:100]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.28 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.28 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
