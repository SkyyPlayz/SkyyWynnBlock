"""Derive SkyyMenu/build_skyymenu_0.3.32.py from the LIVE SkyyMenu 0.3.31 (python tools/menu_0_3_32_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_31_patch.py -> 0.3.31 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.32. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.31 (nothing else changed). The harness SkyyMenu/test_skyymenu_0.3.32.py is its own file.

0.3.32 (2026-10-16) = round life01, THE LIFELONG SKYWYNN MENU ITEM (with SkyyAccessories 0.5.20, SkyySacks 0.8.12, SkyyIslands 0.5.17).
Skyy 2026-10-16 (docs/answered/gear.md, after /island reset gave a 2nd Accessory Bag): "when island reset, it came with a 2nd accessory
bag.   (yk how you cant loose the tools, and can bring them back with a command. lets do the same to the accessory bag, the pocket
dimension, and the menu item.)"
  1. THE MENU ITEM (Skyy_Menu, only the opener) IS LIFELONG (tools/skyyonce.py, classes MenuOnce*): never dropped (Drop key / drag out
     refused), never on the ground (a death drop / full-inventory overflow is stopped and it comes back into the inventory), never stored
     (put into a chest / container / trade offer / the Vault it goes straight back; a second one there is removed), never sold (market:veto;
     the Auction House refused it already), never in a starter kit (once:item:Skyy_Menu = TRUE for SkyyIslands 0.5.17). SkyyProfiles keeps
     it across profile switches (keepItems) and Requip never moves it (swap.keepIds) - unchanged.
  2. ONE PER PROFILE: extra copies in the inventory are removed (history line first: Skyy_SkyyMenu/lifelong/history.log, fsynced, with its
     UNDO); the first pass of each profile = the one-time cleanup (marker lifelong/once/<pkey>.done).
  3. RECALL: /menuitem (NEW alias of /skymenu, like /menu and /sbmenu, when no other build script takes it) - /skymenu already gives a new
     menu item when the inventory holds none (hotbar slot 9 first), then opens the menu.
  4. SERVER SETUP -> Menu -> "Menu item stays with you" (menu.itemKeep -> config.properties itemKeep, default on; a missing key = on, an
     existing file keeps its bytes). Off = 0.3.31 behaviour.
  FIX ROUND (critic life01): a WORLD chest's copies are touched only when the viewer just put theirs in (their inventory dropped below
  what the last sweep left) - a copy already in someone's chest is never moved or removed; personal windows (Vault, trade offer) as
  before; pkey cached per profile epoch. A refused Drop key on an own-inventory section is re-sent by the engine itself
  (InventoryPacketHandler marks the InventoryComponent dirty - VERIFIED bytecode); a container window is marked changed here.
  Item tooltip: it stays with you, /menuitem. No saved-data format change.
  ROLLBACK to 0.3.31: safe (the lifelong/ folder is ignored; /menuitem is gone, /skymenu still gives the item).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.31.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.32.py"))
assert P.has('VERSION = "0.3.31"\n') and P.has("HubCraftCmd") and not P.has("MenuOnce"), "not the generated SkyyMenu 0.3.31 script"
CMD0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.32: LIFE01 (notes: tools/menu_0_3_32_patch.py; docs/answered/gear.md 2026-10-16 LIFELONG BAG / POCKET / MENU ITEM): the SkyWynn Menu item
       is lifelong (tools/skyyonce.py MenuOnce*: never dropped / stored / sold, one per profile, extra copies removed with a history line
       first, never in a starter kit); /menuitem (alias of /skymenu) brings it back; Server Setup -> Menu -> Menu item stays with you.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.32.py.
''')
P.rep('VERSION = "0.3.31"\n', 'VERSION = "0.3.32"\n')
P.rep('''import serverjar as _SJ      # 0.3.26: the CACHED Assets.zip (tools/serverjar.py) - never the installed game file
''', '''import serverjar as _SJ      # 0.3.26: the CACHED Assets.zip (tools/serverjar.py) - never the installed game file
import skyyonce as ONCE      # 0.3.32: the lifelong SkyWynn Menu item (one shared generator with SkyyAccessories 0.5.20 / SkyySacks 0.8.12)
''')

# ---- the alias (only when no other build script takes it - the same takes() rule as /menu and /sbmenu)
P.rep('''ALIASES = [a for a in ("menu", "sbmenu") if a not in TAKEN]''', '''ALIASES = [a for a in ("menu", "sbmenu", "menuitem") if a not in TAKEN]   # 0.3.32: + /menuitem (the lifelong recall)''')
P.rep('''                  "\\\\n\\\\nLost it? Type /skymenu to get a new one.")''',
      '''                  "\\\\n\\\\nIt stays with you: it can't be dropped, stored or sold. Lost it anyway? Type /menuitem (or /skymenu) to get a new one.")''')

# ---- the setting: menu.itemKeep -> config.properties itemKeep (default on; a missing key = on)
P.rep('''     "field:MenuCfg.MODS_HELP@config.properties:modsHelp"),
''', '''     "field:MenuCfg.MODS_HELP@config.properties:modsHelp"),
    # 0.3.32: the lifelong menu item (MenuOnce reads it live)
    ("menu.itemKeep", "Menu item stays with you", "menu", "bool", "true", "", "", "", "", "live",
     "Never dropped, stored or sold; one per profile (extras removed); /menuitem brings it back.",
     "field:MenuCfg.KEEP_ITEM@config.properties:itemKeep"),
''')
P.rep('''    "# modsHelp = show players the Mods tile (every mod and its commands). Admins always see it.",
    "modsHelp=true",
''', '''    "# modsHelp = show players the Mods tile (every mod and its commands). Admins always see it.",
    "modsHelp=true",
    "",
    "# itemKeep = the SkyWynn Menu item stays with you: it can't be dropped, stored in a container or sold, one per profile (extra copies",
    "# are removed) and /menuitem gives it back (true or false).",
    "itemKeep=true",
''')
P.rep('''F(mcfg, "public static volatile boolean MODS_HELP = true;")
''', '''F(mcfg, "public static volatile boolean MODS_HELP = true;")
F(mcfg, "public static volatile boolean KEEP_ITEM = true;")       # 0.3.32: Server Setup (menu.itemKeep) - the lifelong menu item
''')
P.rep('''{ GIVE_ITEM = true; MODS_HELP = true; HOTKEY_GAP_MS = 400L; HOTKEY_COOLDOWN_MS = 1500L; return; }''',
      '''{ GIVE_ITEM = true; MODS_HELP = true; KEEP_ITEM = true; HOTKEY_GAP_MS = 400L; HOTKEY_COOLDOWN_MS = 1500L; return; }''')
P.rep('''    MODS_HELP = flag(p, "modsHelp", true);
''', '''    MODS_HELP = flag(p, "modsHelp", true);
    KEEP_ITEM = flag(p, "itemKeep", true);   // 0.3.32
''')

# ---- the lifelong classes (before /skymenu)
P.rep('''# ================= /skymenu =================
''', '''# ================= 0.3.32 THE LIFELONG MENU ITEM (tools/skyyonce.py): MenuOnce (rules), MenuOnceTask, MenuOnceDropSys, MenuOnceThrowSys,
# MenuOnceInvSys, MenuOnceReady, MenuOnceFn (once:item:Skyy_Menu + the market:veto entry). ON = MenuCfg.KEEP_ITEM (row menu.itemKeep).
assert "menuitem" in ALIASES, "0.3.32: /menuitem is taken by another build script - pick another recall word"
LIFE = ONCE.emit(pool, PKG, "MenuOnce", item=MENU_ITEM_ID, name="SkyWynn Menu item", tag="[Menu]", recall="/menuitem", mod="SkyyMenu",
                 on_expr=PKG + ".MenuCfg.KEEP_ITEM", info_col=SUI.STATUS["="], warn_col=SUI.STATUS_INFO["gold"])

# ================= /skymenu =================
''')
P.rep('''  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register the hub hotkey (double-tap crouch) - the menu item and /skymenu still work: " + t); }
''', '''  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register the hub hotkey (double-tap crouch) - the menu item and /skymenu still work: " + t); }
""" + LIFE["setup"] + r"""''')
P.rep('''page guard on (a page left open across a world change is forgotten at the join, no packet; the menu heals stuck page clicks)");''',
      '''page guard on (a page left open across a world change is forgotten at the join, no packet; the menu heals stuck page clicks); " + @PKG@.MenuOnce.statusText());''')
P.rep('''  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { @PKG@.MenuUtil.warn("config kit flush at shutdown failed: " + t); }
  super.shutdown();''', '''  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { @PKG@.MenuUtil.warn("config kit flush at shutdown failed: " + t); }
""" + LIFE["shutdown"] + r"""  super.shutdown();''')
P.rep('''for c in WRITE:
    c.writeFile(OUT)
''', '''for c in WRITE:
    c.writeFile(OUT)
for c in LIFE["classes"]:   # 0.3.32: the lifelong menu item (tools/skyyonce.py)
    c.writeFile(OUT)
''')

P.rep('''     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item",''',
      '''     "commands": ["/skymenu%ALIASES% - open the menu or get the item back",   # 0.3.32: shorter (+ /menuitem fits 80)''')
assert P.s.count("registerCommand(") == CMD0 and P.s.count("registerSystem(") == SYS0, "no command / system added in the script text"
P.finish()
