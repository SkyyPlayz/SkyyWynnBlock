"""Derive SkyyMenu/build_skyymenu_0.3.31.py from the LIVE SkyyMenu 0.3.30 (python tools/menu_0_3_31_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_30_patch.py -> 0.3.30 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.31. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.30 (nothing else changed). The harness SkyyMenu/test_skyymenu_0.3.31.py is its own file.

0.3.31 (2026-10-16) = round craft01, THE CRAFTING HUB (with SkyySacks 0.8.11). Skyy (screenshot: SkyWynn Menu hub row Home / Character /
Storage / Market / Smithing / World / Social / Settings, no crafting): "we need a crafting tab at the top. unless we want to roll crafting and
smithing into 1 page called crafting with separate crafting and smithing pages. (and upgrade the look of the crafter while were at it.)"
(docs/answered/ui.md 2026-10-16 CRAFTING HUB; the LOCKED 2026-10-10 hubs line: "the hub is CRAFTING (/crafting; /craft + /smithing + ...
are shortcuts)").
  1. The hub row's "Smithing" is now CRAFTING (hub:def:smithing title; the hub ID STAYS "smithing", so every saved shortcut - hub:smithing,
     tab:smithing:recipes / gear / reforge / upgrade / identify, the old tiles that became them - keeps working; no saved data changes).
  2. Its row-2 pages: CRAFTING first (the /craft crafter - SkyySacks 0.8.11 puts the real tab hub:tab:smithing:recipes, order 5; Menu's
     stand-in for it, still put while SkyySacks has none, now has the same label + order) and SMITHING (the stand-in that opens SkyyGear's
     /smithing page through gear:fn:smithing - was labelled "Gear"). Reforge / Upgrade / Identify stay as before (they open the matching
     /smithing tab).
  3. /crafting (new hub command, everyone - hytale:Adventurer) opens the Crafting hub (its last tab, else Crafting); hub:def command =
     "crafting". /smithing stays SkyyGear's own command.
  4. Texts: the hub tooltip / blurb ("Crafting hub: the crafter and Smithing - gear, anvil, identify, upgrade."), the "no pages" line, the
     Mods page help line lists /crafting, the ready line counts 6 hub commands.
Rollback to 0.3.30: safe - the same files; the hub is called Smithing again.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.30.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.31.py"))
assert P.has('VERSION = "0.3.30"\n') and P.has("MenuVtOpen") and not P.has("HubCraftCmd"), "not the generated SkyyMenu 0.3.30 script"
CMD0 = P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.31 (2026-10-16)"):].rstrip()

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.31: CRAFT01 (notes: tools/menu_0_3_31_patch.py; docs/answered/ui.md 2026-10-16 CRAFTING HUB): the hub row's Smithing is CRAFTING (id
       "smithing" kept), its tabs Crafting (/craft, SkyySacks 0.8.11) + Smithing (/smithing) + Reforge / Upgrade / Identify; /crafting.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.31.py.
''')
P.rep('VERSION = "0.3.30"\n', 'VERSION = "0.3.31"\n')

# ---- 1 + 3. the hub's title and command (the id stays "smithing")
P.rep('''HUB_SOON = dict((_h, "No %s pages are on this server right now." % SUI.HUB_DEFS[_h][0]) for _h in SUI.HUBS)
''', '''# 0.3.31 (Skyy 2026-10-16 "we need a crafting tab at the top ... roll crafting and smithing into 1 page called crafting"): the hub with the id
# "smithing" is titled CRAFTING and opens with /crafting (the id stays: saved shortcuts hub:smithing / tab:smithing:<tab> keep working)
HUB_TITLE31 = {"smithing": "Crafting"}
HUB_CMD31 = {"smithing": "crafting"}
hub_title = lambda h: HUB_TITLE31.get(h, SUI.HUB_DEFS[h][0])
hub_cmd = lambda h: HUB_CMD31.get(h, SUI.HUB_DEFS[h][1])
assert all(len(hub_title(_h)) <= len(max(SUI.HUB_ROW_TITLES, key=len)) for _h in SUI.HUBS), "0.3.31: every hub title fits row 1 like the kit's"
HUB_SOON = dict((_h, "No %s pages are on this server right now." % hub_title(_h)) for _h in SUI.HUBS)
''')
P.rep('''HUB_CMDS = [("character", ("char",), "character"), ("storage", (), "storage"), ("market", (), "market"), ("travel", (), "world"),''',
      '''HUB_CMDS = [("character", ("char",), "character"), ("storage", (), "storage"), ("market", (), "market"), ("crafting", (), "smithing"), ("travel", (), "world"),''')
P.rep('''assert all(SUI.HUB_DEFS[h][1] == w for w, _a, h in HUB_CMDS), "0.3.28: each hub command is the contract's command (SUI.HUB_DEFS)"''',
      '''assert all(hub_cmd(h) == w for w, _a, h in HUB_CMDS), "0.3.28 / 0.3.31: each hub command is the hub's command (SUI.HUB_DEFS; Crafting = /crafting)"''')
P.rep('''             "smithing": "Smithing hub: gear, recipes, reforge, upgrade and identify.",''',
      '''             "smithing": "Crafting hub: the crafter and Smithing - gear, anvil, identify, upgrade.",   # 0.3.31''')
P.rep('''F(dat, "public static final String[] HUB_TITLE = %s;" % jarr([SUI.HUB_DEFS[_h][0] for _h in SUI.HUBS]))
F(dat, "public static final String[] HUB_CMD = %s;" % jarr([SUI.HUB_DEFS[_h][1] for _h in SUI.HUBS]))''',
      '''F(dat, "public static final String[] HUB_TITLE = %s;" % jarr([hub_title(_h) for _h in SUI.HUBS]))   # 0.3.31: smithing = Crafting
F(dat, "public static final String[] HUB_CMD = %s;" % jarr([hub_cmd(_h) for _h in SUI.HUBS]))''')

# ---- 2. the stand-in tabs: Crafting first (= SkyySacks 0.8.11's own tab), Gear -> Smithing
P.rep('''assert all(_k in ["%s:%s" % (_r[0], _r[1]) for _r in VT] for _k in VT_FN) and ("smithing", "gear", 10, "Gear", "smithing") in VT, \\
    "0.3.30: the Smithing hub's first stand-in tab runs /smithing (SkyyGear's Craft / Anvil / Upgrade / Identify page)"
''', '''assert all(_k in ["%s:%s" % (_r[0], _r[1]) for _r in VT] for _k in VT_FN) and ("smithing", "gear", 10, "Gear", "smithing") in VT, \\
    "0.3.30: the Smithing hub's first stand-in tab runs /smithing (SkyyGear's Craft / Anvil / Upgrade / Identify page)"
# 0.3.31: the Crafting hub's row 2 = Crafting (the /craft crafter; SkyySacks 0.8.11 puts the real tab with this label + order) + Smithing
VT_LABEL31 = {"smithing:recipes": "Crafting", "smithing:gear": "Smithing"}
VT_ORDER31 = {"smithing:recipes": 5}
VT = [(_h, _t, VT_ORDER31.get("%s:%s" % (_h, _t), _o), VT_LABEL31.get("%s:%s" % (_h, _t), _l), _c) for _h, _t, _o, _l, _c in VT]
assert ("smithing", "recipes", 5, "Crafting", "craft") in VT and ("smithing", "gear", 10, "Smithing", "smithing") in VT
assert len(set((_h, _o) for _h, _t, _o, _l, _c in VT)) == len(VT), "0.3.31: no two stand-in tabs of one hub share an order"
''')

# ---- 3. /crafting
P.rep('''hcso = mk("HubSocialCmd", T["APC"])
''', '''hcso = mk("HubSocialCmd", T["APC"])
hccr = mk("HubCraftCmd", T["APC"])   # 0.3.31: /crafting
''')
P.rep('''M(hcso, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "social");
}""")
''', '''M(hcso, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "social");
}""")
# 0.3.31: /crafting = the Crafting hub (id "smithing"): its last tab, else Crafting (the first by order)
C(hccr, r"""
public HubCraftCmd() {
  super("crafting", "Open the Crafting hub - the crafter (/craft) and Smithing (/smithing) in one place");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hccr, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "smithing");
}""")
''')
P.rep('''  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /social (another mod may own it): " + t); }
''', '''  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /social (another mod may own it): " + t); }
  try { getCommandRegistry().registerCommand(new @PKG@.HubCraftCmd()); hubCmds = hubCmds + 1; }   // 0.3.31
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /crafting (another mod may own it): " + t); }
''')
P.rep('''of 5 hub commands (/character /char /storage /market /travel /social)''', '''of 6 hub commands (/character /char /storage /market /crafting /travel /social)''')
P.rep('''hubb, mhub, mho, mhv, hcch, hcst, hcmk, hctr, hcso, mal, mvo, mvv, pl)''', '''hubb, mhub, mho, mhv, hcch, hcst, hcmk, hctr, hcso, hccr, mal, mvo, mvv, pl)''')
P.rep('''                  "/character (/char), /travel, /social, /storage, /market - open a hub",   # 0.3.28''',
      '''                  "/character (/char), /crafting, /travel, /social, /storage, /market - open a hub",   # 0.3.28; 0.3.31: /crafting''')

# ---- the build checks measure the titles that are shown (Crafting)
P.rep('''_ROWHUBS = [(i, t, "Skyy_Menu" if i == "home" else HUB_ICON_ITEM[i]) for i, t in zip(SUI.HUB_ROW_IDS, SUI.HUB_ROW_TITLES)]''',
      '''_ROWHUBS = [(i, t if i == "home" else hub_title(i), "Skyy_Menu" if i == "home" else HUB_ICON_ITEM[i]) for i, t in zip(SUI.HUB_ROW_IDS, SUI.HUB_ROW_TITLES)]   # 0.3.31''')
P.rep('''["[%s] %s" % (SUI.HUB_DEFS[_h][0], HUB_SOON[_h]) for _h in SUI.HUBS]''', '''["[%s] %s" % (hub_title(_h), HUB_SOON[_h]) for _h in SUI.HUBS]''')
P.rep('''+ [SUI.HUB_DEFS[_h][0] for _h in SUI.HUBS], key=len)   # the longest tile / hub name''', '''+ [hub_title(_h) for _h in SUI.HUBS], key=len)   # the longest tile / hub name''')

assert P.s.count("registerCommand(") == CMD0 + 1
P.finish()
