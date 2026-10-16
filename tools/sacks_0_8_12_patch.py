"""Derive SkyySacks/build_skyysacks_0.8.12.py from the SET pin 0.8.11 (the GENERATED build_skyysacks_0.8.11.py; edit THIS file, then
regenerate: python tools/sacks_0_8_12_patch.py; never re-run sacks_0_8_11_patch.py on top of it). Every anchor is asserted; at the end every
change is undone on a copy and compared with 0.8.11 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_12_patch.py   then   python SkyySacks/build_skyysacks_0.8.12.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.12.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.12 = THE LIFELONG POCKET DIMENSION ITEM (round life01, 2026-10-16, with SkyyAccessories 0.5.20, SkyyMenu 0.3.32, SkyyIslands 0.5.17).
Skyy 2026-10-16 (docs/answered/gear.md, after /island reset gave a 2nd Accessory Bag): "when island reset, it came with a 2nd accessory
bag.   (yk how you cant loose the tools, and can bring them back with a command. lets do the same to the accessory bag, the pocket
dimension, and the menu item.)"
  1. THE POCKET DIMENSION ITEM (Skyy_Sack_Pocket, only the opener - the Void lives in the profile's pool) IS LIFELONG (tools/skyyonce.py,
     classes PdOnce*): never dropped (Drop key / drag out refused), never on the ground (a death drop / full-inventory overflow is stopped
     and it comes back into the inventory), never stored (put into a chest / container / trade offer / the Vault it goes straight back;
     a second one there is removed), never sold (market:veto; Magic Bag ids were already walled), never in a starter kit
     (once:item:Skyy_Sack_Pocket = TRUE for SkyyIslands 0.5.17).
  2. ONE PER PROFILE: extra copies in the inventory are removed (history line first: Skyy_SkyySacks/lifelong/history.log, fsynced, with
     its UNDO); the first pass of each profile = the one-time cleanup (marker lifelong/once/<pkey>.done).
  3. RECALL: /pocket (NEW alias of /sacks, like /pd and /bags) and /pd give a new Pocket Dimension when the inventory holds none (storage,
     hotbar, backpack - never dropped; full = one chat line), then open the Void as before.
  4. SERVER SETUP -> SkyyVoid -> "Pocket Dimension stays with you" (bags.pocketKeep, default on; a missing key = on, an existing file
     keeps its bytes). Off = 0.8.11 behaviour. While /pdadmin legacybags all is on (HOLDALL) the rules are off too (that mode strips the
     item on purpose for a rollback).
  FIX ROUND (critic life01): a WORLD chest's copies are touched only when the viewer just put theirs in (their inventory dropped below
  what the last sweep left) - a copy already in someone's chest is never moved or removed; personal windows (Vault, trade offer) as
  before; pkey cached per profile epoch. A refused Drop key on an own-inventory section is re-sent by the engine itself
  (InventoryPacketHandler marks the InventoryComponent dirty - VERIFIED bytecode); a container window is marked changed here.
  Built against the committed tools/skyyench.py + tools/tier_tags.py (52298ac): the Enchanted Stick (Skyy_Ench_Stick) homes in Foraging
  (SackDefs.enchCat) and RecipeCmp's tier table has the egg rows - those two classes differ from 0.8.11 for that reason only.
  Item tooltip: it stays with you, /pocket. No saved-data format change.
  ROLLBACK to 0.8.11: safe (the lifelong/ folder is ignored; /pocket is gone, /pd still gives the item).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.11.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.12.py"))
assert P.has('VERSION = "0.8.11"\n') and P.has("AccLink") and not P.has("PdOnce"), "not the live generated SkyySacks 0.8.11"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.12 = THE LIFELONG POCKET"):].rstrip() + "\n"

# ================================================================================================ header, version, imports
P.rep('''SAVED DATA: none new (crafts.log gets ACCBAG lines; the Accessory Bag files change only through SkyyAccessories' own take / put).
ROLLBACK to 0.8.10: safe (no file format change); the Crafting tab then comes back as SkyyMenu's stand-in.
"""
''', '''SAVED DATA: none new (crafts.log gets ACCBAG lines; the Accessory Bag files change only through SkyyAccessories' own take / put).
ROLLBACK to 0.8.10: safe (no file format change); the Crafting tab then comes back as SkyyMenu's stand-in.
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.11"\n', 'VERSION = "0.8.12"\n')
P.rep('''import tier_tags as TT   # 0.8.11: THE tier table (sort by tier, PROJECT-RULES 4) - read only
''', '''import tier_tags as TT   # 0.8.11: THE tier table (sort by tier, PROJECT-RULES 4) - read only
import skyyonce as ONCE  # 0.8.12: the lifelong Pocket Dimension item (one shared generator with SkyyAccessories 0.5.20 / SkyyMenu 0.3.32)
''')

# ================================================================================================ the setting
P.rep('''    "#bags.pocketCraft=true",
''', '''    "#bags.pocketCraft=true",
    "# Pocket Dimension stays with you (true or false): the Pocket Dimension item can't be dropped, stored in a container or sold,",
    "# one per profile (extra copies are removed - the Void lives with the profile) and /pocket gives it back. false: the old rules.",
    "#bags.pocketKeep=true",
''')
P.rep('''scfg.addField(CtField.make("public static volatile boolean POCKET_CRAFT = true;", scfg))
''', '''scfg.addField(CtField.make("public static volatile boolean POCKET_CRAFT = true;", scfg))
# 0.8.12: bags.pocketKeep (Server Setup "Pocket Dimension stays with you", default ON) - the lifelong Pocket Dimension item (PdOnce)
scfg.addField(CtField.make("public static volatile boolean POCKET_KEEP = true;", scfg))
''')
P.rep('''  FISH_SWEEP = boolKey(p, "bags.fishSweep", true);   // 0.8.10 review fix
''', '''  FISH_SWEEP = boolKey(p, "bags.fishSweep", true);   // 0.8.10 review fix
  POCKET_KEEP = boolKey(p, "bags.pocketKeep", true);   // 0.8.12: the lifelong Pocket Dimension item
''')
P.rep('''     "field:SackCfg.POCKET_CRAFT@config.properties:bags.pocketCraft;after=SackCfg.pocketChanged"),
] + [(k, _CAP_ROW[k][0]''', '''     "field:SackCfg.POCKET_CRAFT@config.properties:bags.pocketCraft;after=SackCfg.pocketChanged"),
    # 0.8.12: live - every PdOnce rule reads it (tools/skyyonce.py)
    ("bags.pocketKeep", "Pocket Dimension stays with you", "bags", "bool", "true", "", "", "", "", "live",
     "Never dropped, stored or sold; one per profile (extras removed); /pocket brings it back.",
     "field:SackCfg.POCKET_KEEP@config.properties:bags.pocketKeep"),
] + [(k, _CAP_ROW[k][0]''')

# ================================================================================================ the lifelong classes + /pocket
P.rep('''# ================= SacksCmd =================
''', '''# ================= 0.8.12 THE LIFELONG POCKET DIMENSION ITEM (tools/skyyonce.py): PdOnce (rules), PdOnceTask, PdOnceDropSys, PdOnceThrowSys,
# PdOnceInvSys, PdOnceReady, PdOnceFn (once:item:Skyy_Sack_Pocket + the market:veto entry). ON = bags.pocketKeep and not /pdadmin legacybags all.
LIFE = ONCE.emit(pool, PKG, "PdOnce", item=POCKET, name="Pocket Dimension", tag="[SkyyVoid]", recall="/pocket", mod="SkyySacks",
                 on_expr=PKG + ".SackCfg.POCKET_KEEP && !" + PKG + ".VoidStore.HOLDALL", info_col="#cc66cc", warn_col=SUI.STATUS_INFO["gold"])

# ================= SacksCmd =================
''')
P.rep('''  super("sacks", "Open the Void - your SkyyVoid Pocket Dimension (also /pd, /bags)");
  addAliases(new String[] { "pd", "bags" });''', '''  super("sacks", "Open the Void - your SkyyVoid Pocket Dimension (also /pd, /bags; /pocket gives a new one if yours is missing)");
  addAliases(new String[] { "pd", "bags", "pocket" });''')
P.rep('''    // 0.8.0: the Pocket Dimension item is only the opener - /pd gives one when you have none (dropping it never loses anything)
    try {{
      if (!{PKG}.VoidStore.HOLDALL && {PKG}.VoidStore.countIn(player.getInventory(), {PKG}.SackDefs.POCKET, false) <= 0) {{   // fix round 2: not under legacybags all
        if ({PKG}.VoidStore.givePocket(player.getInventory())) pr.sendMessage({MSG}.raw("[SkyyVoid] Here is your Pocket Dimension - right-click it to open the Void").color("#cc66cc"));
      }}
    }} catch (Throwable tp) {{ }}''', '''    // 0.8.0: the Pocket Dimension item is only the opener - /pd gives one when you have none (dropping it never loses anything)
    // 0.8.12: /pocket (and /pd, /bags, /sacks) = the lifelong recall: one into storage, hotbar or backpack (never dropped), counted
    try {{
      if (!{PKG}.VoidStore.HOLDALL) {{   // fix round 2: not under legacybags all
        String rr = {PKG}.PdOnce.recall(pr, {PKG}.PdOnce.secs(player.getInventory()));
        if ("+given".equals(rr)) pr.sendMessage({MSG}.raw("[SkyyVoid] Here is your Pocket Dimension - right-click it to open the Void. It stays with you: it can't be dropped, stored or sold.").color("#cc66cc"));
        else {{ String rt = {PKG}.PdOnce.recallText(rr); if (rt != null) pr.sendMessage({MSG}.raw(rt).color("{GOLD}")); }}
      }}
    }} catch (Throwable tp) {{ }}'''.replace("{GOLD}", __import__("skyyui").STATUS_INFO["gold"]))

# ================================================================================================ plugin: setup / shutdown / ready / write
P.rep('''  catch (Throwable te) {{ {PKG}.SweepTask.EVENTS_OK = false; {PKG}.SackPool.warn("inventory-change listener not registered - every player is swept every 2 s (0.7.17): " + te); }}
''', '''  catch (Throwable te) {{ {PKG}.SweepTask.EVENTS_OK = false; {PKG}.SackPool.warn("inventory-change listener not registered - every player is swept every 2 s (0.7.17): " + te); }}
""" + LIFE["setup"] + f"""''')
P.rep('''the Void's Deposit all fills every bag");''', '''the Void's Deposit all fills every bag; " + {PKG}.PdOnce.statusText());''')
P.rep('''  try {{ {PKG}.PickHarv.HPEND.clear(); {PKG}.PickHarv.HPT.clear(); {PKG}.PickHarv.HCUR.clear(); }} catch (Throwable t) {{ }}   // 0.8.4
  super.shutdown();''', '''  try {{ {PKG}.PickHarv.HPEND.clear(); {PKG}.PickHarv.HPT.clear(); {PKG}.PickHarv.HCUR.clear(); }} catch (Throwable t) {{ }}   // 0.8.4
""" + LIFE["shutdown"] + f"""  super.shutdown();''')
P.rep('''for c in WB_CLASSES:   # 0.7.10: WbRank, WbTab, WbAssetL
    c.writeFile(OUT)
''', '''for c in WB_CLASSES:   # 0.7.10: WbRank, WbTab, WbAssetL
    c.writeFile(OUT)
for c in LIFE["classes"]:   # 0.8.12: the lifelong Pocket Dimension item (tools/skyyonce.py)
    c.writeFile(OUT)
''')
P.rep('''          "you collect. This is only the opener - losing it loses nothing, /pd gives a new one.")''',
      '''          "you collect. This is only the opener and it stays with you: it can't be dropped, stored or sold - /pocket gives a new one if it is ever missing.")''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "no system / command added in the script text (the 3 come from LIFE['setup'])"
P.finish()
