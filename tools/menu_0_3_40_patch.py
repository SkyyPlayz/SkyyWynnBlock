"""Derive SkyyMenu/build_skyymenu_0.3.40.py from the LIVE SkyyMenu 0.3.39 (python tools/menu_0_3_40_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_39_patch.py -> 0.3.39 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.40. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.39 (nothing else changed). Line endings kept. The harness SkyyMenu/test_skyymenu_0.3.40.py is its own file.

0.3.40 (2026-10-18) = THE SKYWYNN MENU ITEM IS ONE-HANDED.
  Skyy (2026-10-18), after "and soul orb should be a 1 handed weapon, not 2": "same with the menu item".
  CAUSE: the engine reads one-handedness from the item's "Utility" block: Item.utility defaults to ItemUtility.DEFAULT, whose Compatible
     is false (the no-arg constructor sets nothing), and Utility.Compatible = "this main-hand item works next to an off-hand item"
     (InteractionContext.forInteraction routes to the off-hand only when the main-hand item isCompatible(); StatModifiersManager
     applies off-hand stats the same way; the flag goes to the client in protocol ItemUtility). The menu item never had a "Utility" key
     (it borrowed the look of Ingredient_Voidheart, an ingredient with no Utility block either), so it counted as two-handed - like the
     vanilla Battleaxe (no Utility) or Debug_Bow_Two_Handed (Compatible false). The borrowed look keys (VISUAL_KEYS: PlayerAnimationsId
     "Item", Scale, IconProperties, Light ...) play no part - vanilla food uses the same "Item" pose and is one-handed.
  FIX (the vanilla one-handed Tools item, Tool_Hoe_Crude - same Items.Tools category - and Template_Food, same "Item" pose):
     "Utility": {"Compatible": true}                                     -> one-handed, the off-hand stays usable;
     "InteractionConfig": {"Priorities": {"Secondary": {"MainHand": 1}}} -> right-click still opens the menu while the off-hand holds
        something with its own right-click (a shield): with equal priorities a Compatible main-hand item hands Secondary to the
        off-hand; MainHand 1 > the off-hand item's default 0 keeps it on the menu (the hoe's / food's exact setting).
     Both values are checked against the vanilla Tool_Hoe_Crude JSON at build (keys + values; nothing copied). Look, icon, art files,
     the OpenCustomUI interaction, lang: unchanged.
  No new command, permission, setting or bridge key; no class change beyond the version texts. Saved data: unchanged.
  ROLLBACK to 0.3.39: safe (the menu item is two-handed again - the off-hand is blocked while it is held; nothing saved changes).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.39.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.40.py"))
assert P.has('VERSION = "0.3.39"\n') and P.has("tools/menu_0_3_39_patch.py") and not P.has('"Utility": {"Compatible"'), \
    "not the generated SkyyMenu 0.3.39 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.40: the SkyWynn Menu item is ONE-HANDED (notes: tools/menu_0_3_40_patch.py): "Utility": {"Compatible": true} + right-click priority
       Secondary MainHand 1 (the vanilla Tool_Hoe_Crude's settings) - the off-hand stays usable, right-click still opens the menu.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.40.py.
''')
P.rep('VERSION = "0.3.39"\n', 'VERSION = "0.3.40"\n')

# =================================================================================================== the one-handed settings
P.rep('''MENU_ITEM_KEYS_FROM = "Ingredient_Voidheart"   # 0.3.15:''',
      '''# 0.3.40: ONE-HANDED (Skyy "same with the menu item" - like the Soul Orb). The engine's rule: a main-hand item is one-handed only with
# Utility.Compatible true (no Utility block = ItemUtility.DEFAULT = Compatible false = two-handed, which the Voidheart-look item was).
# The right-click priority keeps Secondary on the menu while the off-hand holds a shield. Both = the vanilla Tool_Hoe_Crude's (checked).
MENU_ITEM_ONE_HAND = {"Utility": {"Compatible": True}, "InteractionConfig": {"Priorities": {"Secondary": {"MainHand": 1}}}}
MENU_ITEM_ONE_HAND_FROM = "Tool_Hoe_Crude"     # 0.3.40: the vanilla one-handed Items.Tools item the two keys are checked against
MENU_ITEM_KEYS_FROM = "Ingredient_Voidheart"   # 0.3.15:''')
P.rep('''    "0.3.15: the glow colour is written like the Voidheart's (#rgb)"

VISUAL_KEYS = (''', '''    "0.3.15: the glow colour is written like the Voidheart's (#rgb)"
# 0.3.40: the one-handed keys = the vanilla hoe's (one-handed Tools item with its own right-click), and vanilla food (the same "Item"
# pose) is one-handed the same way - so the borrowed pose stays
_oh = json.loads(ASSETS.read(ITEMS[MENU_ITEM_ONE_HAND_FROM]).decode("utf-8-sig"))
for _k in MENU_ITEM_ONE_HAND:
    assert _oh.get(_k) == MENU_ITEM_ONE_HAND[_k], "0.3.40: the menu item's %s = the vanilla %s's: %r" % (_k, MENU_ITEM_ONE_HAND_FROM, _oh.get(_k))
assert _oh.get("Categories") == ["Items.Tools"], "0.3.40: %s is a Tools item like the menu" % MENU_ITEM_ONE_HAND_FROM
_tf = json.loads(ASSETS.read(ITEMS["Template_Food"]).decode("utf-8-sig"))
assert _tf.get("PlayerAnimationsId") == MENU_ITEM_FIELDS["PlayerAnimationsId"] and _tf.get("Utility") == {"Compatible": True}, \\
    "0.3.40: vanilla food wears the same Item pose one-handed"
assert not set(MENU_ITEM_ONE_HAND) & set(_vh), "0.3.40: the Voidheart has no Utility / InteractionConfig of its own (the two-handed cause)"

VISUAL_KEYS = (''')
P.rep('''    "Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": PAGE_ID}}]}},
}
for k in VISUAL_KEYS:''', '''    "Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": PAGE_ID}}]}},
}
item.update(MENU_ITEM_ONE_HAND)                      # 0.3.40: one-handed (Utility.Compatible) + right-click stays on the menu
for k in VISUAL_KEYS:''')
P.rep('''assert set(item) == set(["TranslationProperties", "Categories", "Quality", "Tags", "MaxStack", "Interactions"]) | set(MENU_ITEM_FIELDS) \\''',
      '''assert set(item) == set(["TranslationProperties", "Categories", "Quality", "Tags", "MaxStack", "Interactions"]) | set(MENU_ITEM_FIELDS) \\
    | set(MENU_ITEM_ONE_HAND) \\''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.40 adds no system / command"
P.finish()
