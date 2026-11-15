"""Derive SkyyMenu/build_skyymenu_0.3.52.py + SkyyMenu/test_skyymenu_0.3.52.py from the SET pin SkyyMenu 0.3.51 (generated - never re-run
its patch). Run:  python tools/menu_0_3_52_patch.py   then   python SkyyMenu/build_skyymenu_0.3.52.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.52.py
Edit THIS patch, never the generated files. Every anchor is asserted once; at the end every change is undone on a copy and compared with the
0.3.51 file (nothing else changed). Line endings kept. --out <build path> [--test-out <test path>] writes elsewhere (the harness re-run).

0.3.52 (2026-11-14, round inv3) = OUR OWN CRAFTING inside the inventory + the approved Inventory tab layout (research/ui-theme-art/
inventory-mockup.png v5). Skyy's words: TEST 285 "the goal is to use our own craft not the vanilla one."; TEST 284 "the top bar needs to
be at the top of the screen craft needs to be in, and work in the inventory, i dont see the pets the requip, the charms, the pockets, the
teleports."; popups "Is v5 the look to build?" -> "Yes, build it" and "Do the 7 tabs and the Pets screen look right?" -> "Yes, both".
  1. CRAFTING (the "Crafting - Tab" placeholder + its one-Tab vanilla pass button are gone): the craft panel above the inventory =
     a row of BENCH TABS (Crafting = hand / pocket + Workbench recipes, the default; one tab per other bench whose recipes the player may
     craft - SkyySacks' craft set = Fieldcraft + every bench charm equipped in the Void Charms; Furnace + Tanning tabs open the pack's own
     timed Furnace / Tannery page, PROCESSING STATIONS "furnace and tanning will have a custom look and work more like they do in our pack"),
     a SEARCH box (Enter or Search), a "Craftable only" toggle, a 7 x 3 recipe grid (paged; a recipe you cannot make now is drawn
     uncraftable), and the selected recipe's detail (output, tier, bench, NEEDS icons with have / need, Ready line, Craft / x10 / All).
     Recipes = the game's own recipe registry as SkyySacks allows them (sacks:fn:craftList "all" - the same rule as /craft and the
     benches; without SkyySacks: CraftingPlugin.getBenchRecipes(Crafting, "Fieldcraft") + the player's known recipes = the vanilla pocket
     set); charm / accessory and pet / egg recipes are left out (they stay on the Charms and Pets pages - Skyy 11-14); processing-bench
     recipes are left out (their own tabs). Sorted by tier (tools/tier_tags.py, baked at build time) then name.
     A CRAFT runs exactly like CraftingManager.craftItem: CraftRecipeEvent$Pre (cancel = nothing used) -> the payment through
     sacks:fn:craftPay (inventory FIRST, then the Void; all or nothing; a receipt) -> CraftRecipeEvent$Post (cancel = refunded) -> the
     outputs as giveOutput gives them (InventoryUtils.getContainerForItemPickup + SimpleItemContainer.addOrDropItemStack: a full
     inventory drops the rest at your feet, as vanilla) -> PlayerCraftEvent on the event bus -> sacks:fn:craftCommit. So SkyySkills /
     SkyyQuests / SkyyCooking / SkyyGear see the craft exactly as a vanilla one (no skill:fn:craftxp of ours - that would double).
     Without SkyySacks the craft IS CraftingManager.craftItem on the backpack + storage + hotbar (the vanilla pocket craft).
     Item safety: the click names no slot - the recipe id is the one drawn (the grid keeps the drawn ids); before paying the recipe must
     still be in the allowed list (else refused, nothing used); the pay is all or nothing; x10 / All take what the materials allow (All
     also what fits, at least 1); a refused Post refunds the receipt; a give that throws before anything was handed refunds.
  2. LAYOUT (v5): the 7 approved tabs at the top of a full-size window (Inventory, Skills, Pets, Market, World, Social, Settings - each
     opens today's page for that topic until its new screen is built), coins + X; LEFT: Requip (opens Requip - the one-click presets need
     a SkyyWardrobe bridge: next round), name / class / profile, armour + off-hand (read only, as 0.3.50), VOID CHARMS (acc:has + acc:tal,
     click = the Void Charms page), PET + MOUNT cards (pets:fn:hud: portrait, kind, level, rarity; click = the Pets tab), Health / Mana /
     Stamina / Defense; MIDDLE: the craft panel, the pocket row (Craft | Void - the pocket tabs inside the inventory are the next round),
     the inventory + hotbar (unchanged: the proven grids and server-side moves), the TELEPORT row (a mini hotbar of icons: Island + Hub;
     editing = next round); RIGHT: SKILLS (12 cells, skill + level) and RIGHT NOW (quest, mystery bags, unspent tree points; Go buttons).
  No saved data, no command, no setting, no lang key, no new system; one new class (InvCraft). The client-crash rules stand: the server
  never opens the vanilla screen; every grid copy is a NEW ItemStack without metadata; no Top / Bottom alignment; inline page only.
  CRITIC FIXES (inv3fix): the Salvagebench (Processing in vanilla, instant in SkyySacks) gets its own bench tab - its recipes were
  dropped from the grid; give() answers -1 when nothing was handed out (craftVoid refunds, never commits); no developer notes on the
  player's screen (pocket / teleport captions); the Tanning tab caption names the Tannery tab it lands next to.
  ROLLBACK to 0.3.51: safe (no data; Tab opens the 0.3.51 page with its vanilla-craft pass).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.51.py"), os.path.join(MOD, "build_skyymenu_0.3.52.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.51.py"), os.path.join(MOD, "test_skyymenu_0.3.52.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.51"\n') and P.has("tools/menu_0_3_51_patch.py") and P.has("InvMode")
assert not P.has("InvCraft"), "not the generated SkyyMenu 0.3.51 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")


def cut(t, start, end, keep_end=True):
    """the exact text from start up to end (end itself kept outside the cut when keep_end) - each marker must occur once"""
    assert t.count(start) == 1 and t.count(end) == 1, (start, end)
    a = t.index(start)
    return t[a:t.index(end) + (0 if keep_end else len(end))]


# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.52: OUR OWN CRAFTING inside the inventory (bench tabs, search, Craftable only, recipe grid, Craft / x10 / All; Pre -> pay inventory
       first then the Void -> Post -> giveOutput -> PlayerCraftEvent, as CraftingManager.craftItem) + the approved v5 layout (7 tabs on
       top, Requip, charms, pet + mount, teleport row, Skills, Right now) (notes: tools/menu_0_3_52_patch.py).
       CHECKED: see SkyyMenu/test_skyymenu_0.3.52.py.
''')
P.rep('VERSION = "0.3.51"\n', 'VERSION = "0.3.52"\n')

# ---------- engine classes for the crafting
P.rep('''    "CAC":  "com.hypixel.hytale.component.ComponentAccessor",
}''', '''    "CAC":  "com.hypixel.hytale.component.ComponentAccessor",
    # 0.3.52: our own crafting (CraftingManager.craftItem's steps, every member probed below)
    "CRR":  "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe",
    "MQ":   "com.hypixel.hytale.server.core.inventory.MaterialQuantity",
    "BRQ":  "com.hypixel.hytale.protocol.BenchRequirement",
    "BTY":  "com.hypixel.hytale.protocol.BenchType",
    "CRM":  "com.hypixel.hytale.builtin.crafting.component.CraftingManager",
    "CRP":  "com.hypixel.hytale.builtin.crafting.CraftingPlugin",
    "CREPRE": "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Pre",
    "CREPOST": "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Post",
    "PCE":  "com.hypixel.hytale.server.core.event.events.player.PlayerCraftEvent",
    "CEE":  "com.hypixel.hytale.component.system.CancellableEcsEvent",
    "ITEM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "IRT":  "com.hypixel.hytale.protocol.ItemResourceType",
    "SIC":  "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
    "IVU":  "com.hypixel.hytale.server.core.inventory.InventoryUtils",
    "PSET": "com.hypixel.hytale.server.core.modules.entity.player.PlayerSettings",
    "IEDP": "com.hypixel.hytale.event.IEventDispatcher",
    "I18N": "com.hypixel.hytale.server.core.modules.i18n.I18nModule",
}''')
P.rep('''print("0.3.51 inventory screen: every engine member probed (hooks, adapter, grids, drop, sort, the game-mode watch)")''',
      '''print("0.3.51 inventory screen: every engine member probed (hooks, adapter, grids, drop, sort, the game-mode watch)")
# 0.3.52: our own crafting - every member CraftingManager.craftItem's steps use (the Pre / Post events, the payment view, giveOutput's
# container pick + addOrDrop, the PlayerCraftEvent dispatch) and the vanilla pocket list (the fallback without SkyySacks)
for c, m in ((T["CRR"], "getAssetMap"), (T["CRR"], "getInput"), (T["CRR"], "getPrimaryOutput"), (T["CRR"], "getOutputs"),
             (T["CRR"], "getBenchRequirement"), (T["CRR"], "isKnowledgeRequired"), (T["CRR"], "getId"), (T["MQ"], "getItemId"),
             (T["MQ"], "getResourceTypeId"), (T["MQ"], "getQuantity"), (T["BRQ"], "type"), (T["BRQ"], "id"), (T["BTY"], "Processing"),
             (T["BTY"], "Crafting"), (T["CRM"], "getComponentType"), (T["CRM"], "craftItem"), (T["CRM"], "getOutputItemStacks"),
             (T["CRP"], "getBenchRecipes"), (T["CEE"], "isCancelled"), (T["ST"], "invoke"), (T["ITEM"], "getAssetMap"),
             (T["ITEM"], "getMaxStack"), (T["ITEM"], "getResourceTypes"), (T["ITEM"], "getTranslationKey"), (T["IRT"], "id"),
             (T["IRT"], "quantity"), (T["SIC"], "addOrDropItemStack"), (T["IVU"], "getContainerForItemPickup"), (T["PSET"], "getComponentType"),
             (T["PSET"], "defaults"), (T["INV"], "getCombinedBackpackStorageHotbar"), (T["INV"], "getCombinedHotbarFirst"),
             (T["IC"], "countRemovableMaterial"), (T["HSV"], "get"), (T["HSV"], "getEventBus"), ("com.hypixel.hytale.event.EventBus", "dispatchFor"),
             (T["IEDP"], "hasListener"), (T["IEDP"], "dispatch"), (T["I18N"], "get"), (T["I18N"], "getMessage"), (T["IGS"], "setItemUncraftable"),
             (T["PLA"], "getPlayerConfigData"), ("com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData", "getKnownRecipes"),
             (T["IS"], "getItem"), (T["IS"], "getMetadata")):
    B.probe(pool, c, m)
_CS = lambda n: "L" + n.replace(".", "/") + ";"
assert ("(%s%s%sI%s)Z" % (_CS(T["REF"]), _CS(T["CAC"]), _CS(T["CRR"]), _CS(T["IC"]))) in _isig(T["CRM"], "craftItem"), "0.3.52: CraftingManager.craftItem(Ref, ComponentAccessor, CraftingRecipe, int, ItemContainer)"
assert ("(%sI)Ljava/util/List;" % _CS(T["CRR"])) in _isig(T["CRM"], "getOutputItemStacks"), "0.3.52: CraftingManager.getOutputItemStacks(recipe, n)"
assert ("(%sLjava/lang/String;)Ljava/util/List;" % _CS(T["BTY"])) in _isig(T["CRP"], "getBenchRecipes"), "0.3.52: CraftingPlugin.getBenchRecipes(BenchType, String)"
assert ("(%s%s%s%s)Z" % (_CS(T["CAC"]), _CS(T["REF"]), _CS(T["IC"]), _CS(T["IS"]))) in _isig(T["SIC"], "addOrDropItemStack"), "0.3.52: addOrDropItemStack(accessor, ref, container, stack)"
assert ("(%s%s%s%s)%s" % (_CS(T["REF"]), _CS(T["ITEM"]), _CS(T["PSET"]), _CS(T["CAC"]), _CS(T["IC"]))) in _isig(T["IVU"], "getContainerForItemPickup"), "0.3.52: getContainerForItemPickup"
assert ("(%sI)V" % _CS(T["CRR"])) in _ictor(T["CREPRE"]) and ("(%sI)V" % _CS(T["CRR"])) in _ictor(T["CREPOST"]), "0.3.52: CraftRecipeEvent$Pre / $Post(recipe, n)"
assert pool.get(T["CREPRE"]).subclassOf(pool.get(T["CEE"])) and pool.get(T["CREPOST"]).subclassOf(pool.get(T["CEE"])), "0.3.52: Pre / Post are cancellable ECS events"
assert ("(%s%s%sI)V" % (_CS(T["REF"]), _CS(T["PLA"]), _CS(T["CRR"]))) in _ictor(T["PCE"]), "0.3.52: PlayerCraftEvent(ref, player, recipe, n)"
assert ("(%s%s)V" % (_CS(T["REF"]), _CS(T["EVT"]))) in _isig(T["ST"], "invoke"), "0.3.52: Store.invoke(Ref, EcsEvent)"
assert "(Ljava/lang/Class;Ljava/lang/Object;)Lcom/hypixel/hytale/event/IEventDispatcher;" in _isig("com.hypixel.hytale.event.EventBus", "dispatchFor"), "0.3.52: EventBus.dispatchFor"
print("0.3.52 crafting: every engine member probed (CraftingManager.craftItem's steps, the events, giveOutput's container pick)")''')

# ---------- THE PAGE: the v5 layout (the 0.3.50 / 0.3.51 page definition replaced as one block)
_OLD_PAGE = cut(P.s, 'IV = "SkyyInv"\n', "    return ap, binds, ivh\n", keep_end=False)
P.rep(_OLD_PAGE, r'''IV = "SkyyInv"
IV_PAGE_W, IV_PAGE_H = SUI.MAX_PAGE_W, SUI.MAX_PAGE_H
IV_W, IV_PAD = 1584, 14                            # 0.3.52: a full-size window (TEST 284 "the top bar needs to be at the top of the screen")
IV_IW = IV_W - 2 * IV_PAD                          # 1556
# 0.3.52: THE 7 APPROVED TABS (popup 2026-11-14 "Do the 7 tabs and the Pets screen look right?" -> "Yes, both"; research/ui-theme-art/
# tab-plan.png): each opens today's page for its topic until its new one-screen page is built. (label, hub, hub tab or "" = the hub's pick)
IV_TABS = [("Inventory", "", ""), ("Skills", "character", "skills"), ("Pets", "character", "pets"), ("Market", "market", ""),
           ("World", "world", "teleport"), ("Social", "social", ""), ("Settings", "settings", "settings")]
assert [t_[0] for t_ in IV_TABS] == ["Inventory", "Skills", "Pets", "Market", "World", "Social", "Settings"], "0.3.52: the 7 approved tabs"
for _l, _h, _t in IV_TABS[1:]:
    assert _h in SUI.HUBS and (not _t or any(r_[0] == _h and r_[1] == _t for r_ in SUI.HUB_TABS)), "0.3.50: tab %s -> %s:%s is a contract tab" % (_l, _h, _t)
IV_TAB_W, IV_TAB_H, IV_TAB_GAP = 150, 44, 2
IV_COIN_W, IV_X = 220, 40
IV_TOP_H = 48
IV_COL_L, IV_COL_M = 392, 724
IV_GAP = 10
IV_COL_R = IV_IW - IV_COL_L - IV_COL_M - 2 * IV_GAP   # 420
IV_HINT_H = 28
IV_WIN_H = IV_PAGE_H - 12
IV_BODY_H = IV_WIN_H - 2 * IV_PAD - IV_TOP_H - 14 - 6 - IV_HINT_H   # 844
IV_GW, IV_GH = SUI.glass_grid_size(9, 4)
IV_HW, IV_HH = SUI.glass_grid_size(9, 1)
IV_AW, IV_AH = SUI.glass_grid_size(1, 4)
# the craft panel: a 7 x 3 recipe grid (56 px slots), the NEEDS row (6 x 42 px), up to 8 bench tabs
IV_CS, IV_CI, IV_CC, IV_CR = 56, 46, 7, 3
IV_NS, IV_NI, IV_NMAX = 42, 34, 6
IV_BMAX = 8
IV_SKN, IV_NOWN, IV_TPN, IV_VCN = 12, 8, 8, 6
IV_TPS, IV_TPI = 40, 32
IV_HINTS = [("LMB", "Drag to move"), ("RMB", "Drag half"), ("Shift", "Quick move"), ("1-9", "To hotbar"), ("Q", "Drop"),
            ("Drag out", "Drop"), ("Tab / Esc", "Close")]
# the texts with punctuation go in as b.set lines (TEXT_OK = [A-Za-z0-9 <>/-] inline only)
IV_TXT = {
    "cap0": "Drag items to move them. Shift + click moves them fast.",
    "cfHint": "Pick a recipe on the left to see what it needs.",
    "pkNote": "Your Pocket Dimension bags. Void opens all of them.",
    "tpNote": "Teleport to your island or the hub.",
    "nowNone": "Nothing waiting right now.",
}
for _k, _v in IV_TXT.items():
    assert "later update" not in _v and "comes in" not in _v, "0.3.52 fix: no developer notes on the player's screen: " + _k
    assert all(32 <= ord(c_) < 127 for c_ in _v) and '"' not in _v and "\\" not in _v, "0.3.50: plain text: " + _k
# the teleport mini hotbar (Skyy 11-14: "make the teleport row like a mini hot bar, with icons instead of names"; default Island + Hub)
IV_TP = [("Skyy_Menu_Icon_MyIsland", "Island", "Teleport to your island", "island"), ("Skyy_Menu_Icon_Hub", "Hub", "Go back to the hub", "hub")]
assert all(t_[0] in ICON_ITEMS for t_ in IV_TP), "0.3.52: the teleport icons are items this jar ships"
# runtime markup (bench tabs, Right now rows): the style strings are the kit's; {I} {W} {S} filled in Java (digits / a kit style only)
IV_BENCH_BTN = "TextButton #SkyyInvBt{I} { Anchor: (Width: {W}, Height: 34, Right: 4); {S} }"
IV_ST_TAB = SUI.glass_button_style("tab", 14)
IV_ST_TABSEL = SUI.glass_button_style("tabSelected", 14)
IV_NOW_ROW = ("Group #SkyyInvNr{I} { Anchor: (Width: %d, Height: 40, Bottom: 4); LayoutMode: Left; Padding: (Horizontal: 10); Background: %s; "
              "Label #SkyyInvNrT{I} { Anchor: (Width: %d, Height: 40); Style: %s; } "
              "TextButton #SkyyInvNrB{I} { Anchor: (Width: 64, Height: 30, Top: 5); Text: \"Go\"; %s } }"
              % (IV_COL_R - 24, SUI.glass_bg("inset"), IV_COL_R - 24 - 20 - 64 - 6, SUI.glass_text_style(14, "text"), SUI.glass_button_style("secondary", 13)))
IV_NOW_EMPTY = ("Label #SkyyInvNrE { Anchor: (Width: %d, Height: 40); Style: %s; }" % (IV_COL_R - 24, SUI.glass_text_style(14, "dim")))
for _mk in (IV_BENCH_BTN.replace("{I}", "0").replace("{W}", "90").replace("{S}", IV_ST_TAB), IV_NOW_ROW.replace("{I}", "0"), IV_NOW_EMPTY):
    SUI.check_markup(_mk, prefix=IV, kit_paths=True)
    assert "@" not in _mk and "\n" not in _mk, "0.3.52: a runtime markup line Java can hold"


def _inv_page():
    ap = SUI.Appends()
    G_ = SUI
    lab = G_.glass_label
    ap.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); }" % (IV, IV_PAGE_W, IV_PAGE_H)))
    # the drop zone: a full-page transparent grid behind the window (one empty slot; Dropped on it = drag outside = drop)
    ap.append(("#" + IV, 'ItemGrid #%sDz { Anchor: (Left: 0, Top: 0, Width: %d, Height: %d); SlotsPerRow: 1; AreItemsDraggable: false; '
                         'InfoDisplay: None; Style: (SlotSize: %d, SlotIconSize: 1, SlotSpacing: 0, SlotBackground: "%s"); }'
               % (IV, IV_PAGE_W, IV_PAGE_H, IV_PAGE_W, G_.glass_path("Clear"))))
    used = IV_TOP_H + 14 + IV_BODY_H + 6 + IV_HINT_H
    ivh = used + 2 * IV_PAD
    assert ivh == IV_WIN_H and ivh <= IV_PAGE_H, ivh
    win = IV + "Win"
    ap.append(("#" + IV, G_.glass_group(win, IV_W, ivh, role="frame", layout="Top", pad=IV_PAD,
                                          anchor={"left": (IV_PAGE_W - IV_W) // 2, "top": (IV_PAGE_H - ivh) // 2})))
    # ---- row 1 (the TOP of the screen): the 7 tabs, coins, the X
    top = IV + "Top"
    ap.append(("#" + win, G_.glass_group(top, IV_IW, IV_TOP_H, layout="Left")))
    for i, (lb, _h, _t) in enumerate(IV_TABS):
        assert G_.text_width(lb, 16, bold=True) <= IV_TAB_W - 10, "0.3.50: tab label fits: " + lb
        ap.append(("#" + top, G_.glass_button("%sT%d" % (IV, i), lb, "tabSelected" if i == 0 else "tab", w=IV_TAB_W, h=IV_TAB_H, size=16,
                                              anchor={"right": IV_TAB_GAP, "top": 2})))
    tabs_w = len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP)
    sp = IV_IW - tabs_w - IV_COIN_W - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, lab(IV + "Coins", "", 15, "xp", bold=True, w=IV_COIN_W, h=IV_TOP_H, halign="End", anchor={"right": 8})))
    ap.append(("#" + top, G_.glass_button(IV + "Close", "X", "close", w=IV_X, h=IV_X, size=16, anchor={"top": 4})))
    ap.append(("#" + win, 'Group #%sSep { Anchor: (Width: %d, Height: 2, Top: 6, Bottom: 6); Background: "%s"; }'
               % (IV, IV_IW, G_.glass_path("Separator"))))
    # ---- row 2: the three columns
    body = IV + "Body"
    ap.append(("#" + win, G_.glass_group(body, IV_IW, IV_BODY_H, layout="Left")))
    # ======== LEFT: Requip, you, armour + off-hand, Void Charms, pet + mount, vitals
    ch = IV + "Char"
    ap.append(("#" + body, G_.glass_group(ch, IV_COL_L, IV_BODY_H, role="panel", layout="Top", pad=12)))
    ciw = IV_COL_L - 24
    rq = IV + "RqRow"
    ap.append(("#" + ch, G_.glass_group(rq, ciw, 34, layout="Left")))
    ap.append(("#" + rq, lab(IV + "RqH", "REQUIP", 15, "accentHi", bold=True, w=110, h=34)))
    ap.append(("#" + rq, G_.glass_button(IV + "RqBtn", "Open Requip", "secondary", w=160, h=32, size=14)))
    ap.append(("#" + ch, lab(IV + "Name", "", 20, "title", bold=True, w=ciw, h=26, anchor={"top": 8})))
    ap.append(("#" + ch, lab(IV + "Cls", "", 16, "gold", bold=True, w=ciw, h=22)))
    ap.append(("#" + ch, lab(IV + "Prof", "", 14, "dim", w=ciw, h=18)))
    gr = IV + "Gear"
    gear_h = 22 + IV_AH
    ap.append(("#" + ch, G_.glass_group(gr, ciw, gear_h, layout="Left", anchor={"top": 6})))
    mid_w = ciw - 2 * IV_AW - 2 * 8
    for side, gid, head in (("L", IV + "Ia", "Armour"), ("R", IV + "Iu", "Off-hand")):
        col = IV + "Gc" + side
        if side == "R":
            nm = IV + "GnL"
            ap.append(("#" + gr, G_.glass_group(nm, mid_w, gear_h, layout="Top", anchor={"left": 8, "right": 8})))
            ap.append(("#" + nm, "Group { Anchor: (Height: 22); }"))
            for k_, (a_, b_) in enumerate(zip(("Head", "Chest", "Hands", "Legs"), ("Off-hand", "Off-hand 2", "Off-hand 3", "Off-hand 4"))):
                rw = IV + "Gn%d" % k_
                ap.append(("#" + nm, G_.glass_group(rw, mid_w, SUI.GLASS_SLOT + (SUI.GRID_SPACING if k_ < 3 else 0), layout="Left")))
                ap.append(("#" + rw, lab(None, a_, 14, "text", w=mid_w // 2, h=SUI.GLASS_SLOT)))
                ap.append(("#" + rw, lab(None, b_, 14, "text", w=mid_w - mid_w // 2, h=SUI.GLASS_SLOT, halign="End")))
        ap.append(("#" + gr, G_.glass_group(col, IV_AW, gear_h, layout="Top")))
        ap.append(("#" + col, lab(None, head, 13, "dim", bold=True, w=IV_AW, h=22, halign="Center")))
        ap.append(("#" + col, G_.glass_grid(gid, 1, 4, drag=False)))
    # VOID CHARMS (acc:has + acc:tal; click = the Void Charms page)
    vh = IV + "VcRow"
    ap.append(("#" + ch, G_.glass_group(vh, ciw, 26, layout="Left", anchor={"top": 8})))
    ap.append(("#" + vh, lab(IV + "VcH", "VOID CHARMS", 14, "accentHi", bold=True, w=130, h=26)))
    ap.append(("#" + vh, lab(IV + "VcN", "", 13, "dim", w=ciw - 130 - 120, h=26)))
    ap.append(("#" + vh, G_.glass_button(IV + "VcAll", "All charms", "secondary", w=120, h=26, size=13)))
    ap.append(("#" + ch, G_.glass_grid(IV + "Vc", IV_VCN, 1, drag=False, slot=56, icon=46, anchor={"top": 4})))
    # PET + MOUNT cards (pets:fn:hud; click = the Pets tab)
    pm = IV + "PmRow"
    ap.append(("#" + ch, G_.glass_group(pm, ciw, 64, layout="Left", anchor={"top": 10})))
    cw = (ciw - 10) // 2
    for k_, head in (("Pet", "PET"), ("Mnt", "MOUNT")):
        cd = IV + k_ + "Card"
        ap.append(("#" + pm, G_.glass_group(cd, cw, 64, role="inset", layout="Left", pad=4, anchor={"right": 10} if k_ == "Pet" else None)))
        ap.append(("#" + cd, G_.glass_grid(IV + k_ + "I", 1, 1, drag=False, slot=56, icon=46)))
        tc = IV + k_ + "Tx"
        tw = cw - 8 - 56 - 8
        ap.append(("#" + cd, G_.glass_group(tc, tw, 56, layout="Top", anchor={"left": 8})))
        ap.append(("#" + tc, lab(None, head, 12, "dim", bold=True, w=tw, h=16)))
        ap.append(("#" + tc, lab(IV + k_ + "N", "", 15, "title", bold=True, w=tw, h=22)))
        ap.append(("#" + tc, lab(IV + k_ + "L", "", 13, "text", w=tw, h=18)))
    # vitals 2 x 2
    vit = IV + "Vit"
    ap.append(("#" + ch, G_.glass_group(vit, ciw, 2 * 38, layout="Top", anchor={"top": 10})))
    vw = (ciw - 8) // 2
    for r_ in range(2):
        rw = IV + "Vr%d" % r_
        ap.append(("#" + vit, G_.glass_group(rw, ciw, 34, layout="Left", anchor={"bottom": 4})))
        for c_ in range(2):
            k_ = 2 * r_ + c_
            nm_, col_ = (("Health", "health"), ("Mana", "mana"), ("Stamina", "stamina"), ("Defense", "defense"))[k_]
            cl = IV + "V%d" % k_
            ap.append(("#" + rw, G_.glass_group(cl, vw, 34, role="inset", layout="Left", pad={"horizontal": 10}, anchor={"right": 8} if c_ == 0 else None)))
            ap.append(("#" + cl, lab(None, nm_, 15, col_, bold=True, w=(vw - 20) // 2, h=34)))
            ap.append(("#" + cl, lab(IV + "Vv%d" % k_, "", 15, "title", bold=True, w=(vw - 20) - (vw - 20) // 2, h=34, halign="End")))
    left_used = 34 + 8 + 26 + 22 + 18 + 6 + gear_h + 8 + 26 + 4 + 56 + 10 + 64 + 10 + 76 + 24
    assert left_used <= IV_BODY_H, ("0.3.52: the left column fits", left_used)
    ap.append(("#" + body, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ======== MIDDLE: the craft panel, the pocket row, the inventory + hotbar + teleport row
    md = IV + "Mid"
    ap.append(("#" + body, G_.glass_group(md, IV_COL_M, IV_BODY_H, layout="Top")))
    cf = IV + "Craft"
    miw = IV_COL_M - 20
    cgw, cgh = SUI.glass_grid_size(IV_CC, IV_CR, IV_CS)
    ngw, _ngh = SUI.glass_grid_size(IV_NMAX, 1, IV_NS)
    left_w = cgw
    det_w = miw - left_w - 12
    body_h = max(32 + 6 + cgh + 4 + 22, 0)
    craft_h = 20 + 36 + 6 + body_h
    ap.append(("#" + md, G_.glass_group(cf, IV_COL_M, craft_h, role="panel", layout="Top", pad=10)))
    # row A: the bench tabs (drawn at run time into #SkyyInvCfB) + Craftable only
    ra = IV + "CfA"
    ap.append(("#" + cf, G_.glass_group(ra, miw, 36, layout="Left")))
    ap.append(("#" + ra, G_.glass_group(IV + "CfB", miw - 180 - 8, 36, layout="Left", anchor={"right": 8})))
    ap.append(("#" + ra, G_.glass_button(IV + "CfOnly", "Craftable only", "secondary", w=180, h=34, size=13)))
    rb = IV + "CfBody"
    ap.append(("#" + cf, G_.glass_group(rb, miw, body_h, layout="Left", anchor={"top": 6})))
    cl = IV + "CfL"
    ap.append(("#" + rb, G_.glass_group(cl, left_w, body_h, layout="Top")))
    sr = IV + "CfS"
    ap.append(("#" + cl, G_.glass_group(sr, left_w, 32, layout="Left")))
    ap.append(("#" + sr, G_.text_field(IV + "CqBox", IV + "Cq", w=166, h=32, placeholder="Search recipes", max_length=24, size=14)))
    ap.append(("#" + sr, G_.glass_button(IV + "CqGo", "Search", "secondary", w=66, h=32, size=13, anchor={"left": 4})))
    ap.append(("#" + sr, G_.glass_button(IV + "CqX", "Clear", "secondary", w=56, h=32, size=13, anchor={"left": 4})))
    spw = left_w - 166 - 4 - 66 - 4 - 56 - 32 - 42 - 32
    assert spw >= 0, ("0.3.52: the search row fits", spw)
    ap.append(("#" + sr, "Group { Anchor: (Width: %d); }" % spw))
    ap.append(("#" + sr, G_.glass_button(IV + "CpPrev", "<", "secondary", w=32, h=32, size=14)))
    ap.append(("#" + sr, lab(IV + "CpN", "", 13, "text", bold=True, w=42, h=32, halign="Center")))
    ap.append(("#" + sr, G_.glass_button(IV + "CpNext", ">", "secondary", w=32, h=32, size=14)))
    ap.append(("#" + cl, G_.glass_grid(IV + "Cg", IV_CC, IV_CR, drag=False, slot=IV_CS, icon=IV_CI, anchor={"top": 6})))
    ap.append(("#" + cl, lab(IV + "Ci", "", 13, "dim", w=left_w, h=22, anchor={"top": 4})))
    ap.append(("#" + rb, "Group { Anchor: (Width: 12); }"))
    dr = IV + "CfR"
    ap.append(("#" + rb, G_.glass_group(dr, det_w, body_h, role="inset", layout="Top", pad=8)))
    diw = det_w - 16
    assert ngw <= diw, ("0.3.52: the NEEDS row fits", ngw, diw)
    oh = IV + "CoRow"
    ap.append(("#" + dr, G_.glass_group(oh, diw, 56, layout="Left")))
    ap.append(("#" + oh, G_.glass_grid(IV + "Co", 1, 1, drag=False, slot=56, icon=46)))
    ot = IV + "CoTx"
    ap.append(("#" + oh, G_.glass_group(ot, diw - 56 - 8, 56, layout="Top", anchor={"left": 8})))
    ap.append(("#" + ot, lab(IV + "CoN", "", 16, "title", bold=True, w=diw - 64, h=28)))
    ap.append(("#" + ot, lab(IV + "CoS", "", 13, "dim", w=diw - 64, h=24)))
    ap.append(("#" + dr, lab(IV + "CnH", "NEEDS", 13, "dim", bold=True, w=diw, h=18, anchor={"top": 4})))
    ap.append(("#" + dr, G_.glass_grid(IV + "Cn", IV_NMAX, 1, drag=False, slot=IV_NS, icon=IV_NI)))
    nq = IV + "NqRow"
    ap.append(("#" + dr, G_.glass_group(nq, diw, 18, layout="Left")))
    for k_ in range(IV_NMAX):
        ap.append(("#" + nq, lab(IV + "Nq%d" % k_, "", 12, "text", bold=True, w=IV_NS, h=18, halign="Center",
                                 anchor={"right": SUI.GRID_SPACING} if k_ < IV_NMAX - 1 else None)))
    ap.append(("#" + dr, lab(IV + "Crd", "", 13, "green", w=diw, h=20, anchor={"top": 4})))
    bt = IV + "CxRow"
    ap.append(("#" + dr, G_.glass_group(bt, diw, 36, layout="Left", anchor={"top": 6})))
    ap.append(("#" + bt, G_.glass_button(IV + "Cx1", "Craft", "primary", w=112, h=36, size=15)))
    ap.append(("#" + bt, G_.glass_button(IV + "Cx10", "x10", "secondary", w=70, h=36, size=14, anchor={"left": 6})))
    ap.append(("#" + bt, G_.glass_button(IV + "CxA", "All", "secondary", w=70, h=36, size=14, anchor={"left": 6})))
    assert 112 + 6 + 70 + 6 + 70 <= diw and 56 + 4 + 18 + IV_NS + 18 + 4 + 20 + 6 + 36 + 16 <= body_h, "0.3.52: the recipe detail fits"
    # the pocket row (Craft | Void)
    pk = IV + "Pk"
    ap.append(("#" + md, G_.glass_group(pk, IV_COL_M, 40, layout="Left", anchor={"top": 6})))
    ap.append(("#" + pk, G_.glass_button(IV + "PkC", "Craft", "tabSelected", w=120, h=38, size=15, anchor={"right": 2})))
    ap.append(("#" + pk, G_.glass_button(IV + "PkV", "Void", "tab", w=120, h=38, size=15)))
    ap.append(("#" + pk, lab(IV + "PkNote", "", 13, "dim", w=IV_COL_M - 242 - 12, h=38, anchor={"left": 12})))
    ap.sets.append((IV + "PkNote", "Text", IV_TXT["pkNote"]))
    ivp = IV + "Inv"
    inv_h = IV_BODY_H - craft_h - 46 - 6
    ap.append(("#" + md, G_.glass_group(ivp, IV_COL_M, inv_h, role="panel", layout="Top", pad=12, anchor={"top": 6})))
    iiw = IV_COL_M - 24
    hr = IV + "InvHead"
    ap.append(("#" + ivp, G_.glass_group(hr, iiw, 30, layout="Left")))
    ap.append(("#" + hr, lab(IV + "InvH", "INVENTORY", 15, "accentHi", bold=True, w=150, h=30)))
    ap.append(("#" + hr, lab(IV + "Cap", "", 14, "dim", w=iiw - 150 - 130, h=30)))
    ap.append(("#" + hr, G_.glass_button(IV + "Sort", "Sort", "secondary", w=120, h=30, anchor={"left": 10})))
    gx = (iiw - IV_GW) // 2
    ap.append(("#" + ivp, G_.glass_grid(IV + "Is", 9, 4, drag=True, anchor={"left": gx, "top": 6})))
    ap.append(("#" + ivp, G_.glass_grid(IV + "Ih", 9, 1, drag=True, anchor={"left": gx, "top": 6})))
    tr = IV + "TpRow"
    ap.append(("#" + ivp, G_.glass_group(tr, iiw, IV_TPS, layout="Left", anchor={"top": 8, "left": gx})))
    ap.append(("#" + tr, lab(IV + "TpH", "TELEPORT", 13, "dim", bold=True, w=96, h=IV_TPS)))
    tpw, _tph = SUI.glass_grid_size(IV_TPN, 1, IV_TPS)
    ap.append(("#" + tr, G_.glass_grid(IV + "Tp", IV_TPN, 1, drag=False, slot=IV_TPS, icon=IV_TPI)))
    ap.append(("#" + tr, lab(IV + "TpNote", "", 12, "dim", w=iiw - gx - 96 - tpw - 10, h=IV_TPS, anchor={"left": 10})))
    ap.sets.append((IV + "TpNote", "Text", IV_TXT["tpNote"]))
    assert 24 + 30 + 6 + IV_GH + 6 + IV_HH + 8 + IV_TPS <= inv_h and iiw - gx - 96 - tpw - 10 > 40, ("0.3.52: the inventory panel fits", inv_h)
    ap.append(("#" + body, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ======== RIGHT: Skills + Right now
    rt = IV + "Right"
    ap.append(("#" + body, G_.glass_group(rt, IV_COL_R, IV_BODY_H, layout="Top")))
    riw = IV_COL_R - 24
    sk_h = 24 + 26 + 4 * 40 + 4
    sk = IV + "Sk"
    ap.append(("#" + rt, G_.glass_group(sk, IV_COL_R, sk_h, role="panel", layout="Top", pad=12, anchor={"bottom": 10})))
    sh = IV + "SkHead"
    ap.append(("#" + sk, G_.glass_group(sh, riw, 26, layout="Left")))
    ap.append(("#" + sh, lab(IV + "SkH", "SKILLS", 15, "accentHi", bold=True, w=riw - 90, h=26)))
    ap.append(("#" + sh, G_.glass_button(IV + "SkBtn", "Open", "secondary", w=90, h=26, size=13)))
    cw3 = (riw - 2 * 6) // 3
    for r_ in range(4):
        rw = IV + "SkR%d" % r_
        ap.append(("#" + sk, G_.glass_group(rw, riw, 36, layout="Left", anchor={"top": 4})))
        for c_ in range(3):
            k_ = 3 * r_ + c_
            cl_ = IV + "SkC%d" % k_
            ap.append(("#" + rw, G_.glass_group(cl_, cw3, 36, role="inset", layout="Left", pad={"horizontal": 6}, anchor={"right": 6} if c_ < 2 else None)))
            ap.append(("#" + cl_, lab(IV + "Sk%d" % k_, "", 13, "text", bold=True, w=cw3 - 12, h=36, halign="Center")))
    now_h = IV_BODY_H - sk_h - 10
    nw = IV + "Now"
    ap.append(("#" + rt, G_.glass_group(nw, IV_COL_R, now_h, role="panel", layout="Top", pad=12)))
    nh = IV + "NowHead"
    ap.append(("#" + nw, G_.glass_group(nh, riw, 26, layout="Left")))
    ap.append(("#" + nh, lab(IV + "NowH", "RIGHT NOW", 15, "accentHi", bold=True, w=riw - 90, h=26)))
    ap.append(("#" + nh, G_.glass_button(IV + "NowBtn", "Quests", "secondary", w=90, h=26, size=13)))
    assert 24 + 26 + 8 + IV_NOWN * 44 <= now_h, "0.3.52: the Right now rows fit"
    ap.append(("#" + nw, G_.glass_group(IV + "NowL", riw, now_h - 24 - 26 - 8, layout="Top", anchor={"top": 8})))
    # ---- row 3: the key hints
    hn = IV + "Hints"
    ap.append(("#" + win, G_.glass_group(hn, IV_IW, IV_HINT_H, layout="Left", anchor={"top": 6})))
    parts = [G_.glass_key_hint(IV + "K%d" % k_, k, t, h=IV_HINT_H) for k_, (k, t) in enumerate(IV_HINTS)]
    hw = sum(w_ for _m, w_ in parts)
    assert hw <= IV_IW, ("0.3.50: the key hints fit", hw)
    ap.append(("#" + hn, "Group { Anchor: (Width: %d); }" % ((IV_IW - hw) // 2)))
    for mk_, _w in parts:
        ap.append(("#" + hn, mk_))
    ap.sets.append((IV + "Cap", "Text", IV_TXT["cap0"]))
    binds = [("#%sT%d" % (IV, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [
        ("#" + IV + "Close", "close"), ("#" + IV + "Sort", "sort"), ("#" + IV + "RqBtn", "rq"), ("#" + IV + "VcAll", "vc"),
        ("#" + IV + "CfOnly", "conly"), ("#" + IV + "CqX", "cqx"), ("#" + IV + "CpPrev", "cpp"), ("#" + IV + "CpNext", "cpn"),
        ("#" + IV + "Cx1", "cx:1"), ("#" + IV + "Cx10", "cx:10"), ("#" + IV + "CxA", "cx:0"), ("#" + IV + "PkC", "pkc"),
        ("#" + IV + "PkV", "pkv"), ("#" + IV + "SkBtn", "tab:1"), ("#" + IV + "NowBtn", "nowq")]
    IV_BW_ALL[0] = miw - 180 - 8
    return ap, binds, ivh
''')
P.rep('''IV_AP, IV_BINDS, IV_H = _inv_page()''', '''IV_BW_ALL = [0]
IV_AP, IV_BINDS, IV_H = _inv_page()''')
P.rep('''for _g in ("Is", "Ih", "Ia", "Iu", "Dz", "Cap", "Name", "Cls", "Prof", "Coins", "Vv0", "Vv1", "Vv2", "Vv3"):''',
      '''for _g in ("Is", "Ih", "Ia", "Iu", "Dz", "Cap", "Name", "Cls", "Prof", "Coins", "Vv0", "Vv1", "Vv2", "Vv3",   # 0.3.52: + the craft panel,
           "CfB", "CfOnly", "Cq", "CqGo", "CpN", "Cg", "Ci", "Co", "CoN", "CoS", "Cn", "Crd", "Vc", "VcN", "PetI", "PetN", "PetL",   # charms, pets,
           "MntI", "MntN", "MntL", "NowL", "Tp") + tuple("Nq%d" % k_ for k_ in range(IV_NMAX)) + tuple("Sk%d" % k_ for k_ in range(IV_SKN)):   # skills, now, teleports''')
P.rep('''assert IV_ELEMENTS <= 400, "0.3.50: the inventory page stays far under the ~1,600 element budget (%d)" % IV_ELEMENTS''',
      '''assert IV_ELEMENTS <= 700, "0.3.52: the inventory page stays well under the ~1,600 element budget (%d + at most %d at run time)" % (IV_ELEMENTS, IV_BMAX + 4 * IV_NOWN)''')

# ---------- InvData: the tabs, the crafting constants, the tier table, the runtime markup
P.rep('''F(idat, "public static final String CAP0 = %s;" % jstr(IV_TXT["cap0"]))
''', '''F(idat, "public static final String CAP0 = %s;" % jstr(IV_TXT["cap0"]))
# 0.3.52: the crafting + side panel constants
for _n, _v in (("CC", IV_CC), ("CR", IV_CR), ("NMAX", IV_NMAX), ("BMAX", IV_BMAX), ("SKN", IV_SKN), ("NOWN", IV_NOWN), ("TPN", IV_TPN),
               ("VCN", IV_VCN), ("BW_ALL", IV_BW_ALL[0])):
    F(idat, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("ST_TAB", IV_ST_TAB), ("ST_TABSEL", IV_ST_TABSEL), ("BENCH_BTN", IV_BENCH_BTN), ("NOW_ROW", IV_NOW_ROW), ("NOW_EMPTY", IV_NOW_EMPTY),
               ("CF_HINT", IV_TXT["cfHint"]), ("NOW_NONE", IV_TXT["nowNone"])):
    F(idat, "public static final String %s = %s;" % (_n, jstr(_v)))
F(idat, "public static final String[] TP_ID = %s;" % jarr([t_[0] for t_ in IV_TP]))
F(idat, "public static final String[] TP_NAME = %s;" % jarr([t_[1] for t_ in IV_TP]))
F(idat, "public static final String[] TP_DESC = %s;" % jarr([t_[2] for t_ in IV_TP]))
F(idat, "public static final String[] TP_CMD = %s;" % jarr([t_[3] for t_ in IV_TP]))
# SORT BY TIER (PROJECT-RULES 4): the tier of an output id = tools/tier_tags.py (baked here, sorted for a binary search), else the tool metal
# word in the id (TOOL_METALS), else 0 (untiered first, as SkyySacks' /craft)
import tier_tags as _TT
_tt = sorted((i_, r_[0]) for i_, r_ in _TT.ROWS.items())
F(idat, "public static final String[] TT_IDS = %s;" % jarr([i_ for i_, _t in _tt]))
F(idat, "public static final int[] TT_T = %s;" % jints([t_ for _i, t_ in _tt]))
F(idat, "public static final String[] TM_W = %s;" % jarr([w_ for w_, _t in _TT.TOOL_METALS]))
F(idat, "public static final int[] TM_T = %s;" % jints([t_ for _w, t_ in _TT.TOOL_METALS]))
print("0.3.52 crafting: %d tier rows baked from tools/tier_tags.py (TT_VERSION %s), %d metal words" % (len(_tt), _TT.TT_VERSION, len(_TT.TOOL_METALS)))
''')

# ---------- the class list: InvCraft
P.rep('''imod = mk("InvMode", T["EES"])   # 0.3.51: ChangeGameModeEvent -> the creative flag (the vanilla Tab for creative players)
''', '''imod = mk("InvMode", T["EES"])   # 0.3.51: ChangeGameModeEvent -> the creative flag (the vanilla Tab for creative players)
icr  = mk("InvCraft")       # 0.3.52: our own crafting (the list, the stock, the craft as CraftingManager.craftItem does it) + side-panel reads
''')
P.rep('''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, pl)   # 0.3.50: the inventory screen (0.3.51: + InvMode)''',
      '''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, icr, pl)   # 0.3.50: the inventory screen (0.3.51: + InvMode; 0.3.52: + InvCraft)''')

# ---------- InvPage fields + constructor
P.rep('''           "public long lastMoveAt;"):
    F(ipg, _f)''', '''           "public long lastMoveAt;",
           # 0.3.52 crafting state: bench tab, search, Craftable only, page, the selected recipe, the recipe ids drawn, the last craft line,
           # the bench tabs drawn, the Right now targets drawn, crafts done on this page
           "public String cbench;", "public String cquery;", "public boolean conly;", "public int cpage;", "public String csel;",
           "public String[] cshown;", "public String cnote;", "public java.util.ArrayList cbenches;", "public String[] nowT;", "public int crafts;"):
    F(ipg, _f)''')
P.rep('''  this.lastMove = "";
  this.lastMoveAt = 0L;
}""")''', '''  this.lastMove = "";
  this.lastMoveAt = 0L;
  this.cbench = "Crafting";
  this.cquery = "";
  this.conly = false;
  this.cpage = 0;
  this.csel = null;
  this.cshown = new String[0];
  this.cnote = "";
  this.cbenches = new java.util.ArrayList();
  this.nowT = new String[0];
  this.crafts = 0;
}""")''')

# ---------- InvCraft (before InvPage part 1: its callers)
P.rep('''# ---- InvPage part 1: grids, slots, moves
''', r'''# ---- 0.3.52 InvCraft: OUR OWN CRAFTING (tools/menu_0_3_52_patch.py). The list = SkyySacks' allowed set (sacks:fn:craftList "all") or,
# without SkyySacks, the vanilla pocket set; the craft = CraftingManager.craftItem's steps with the payment through sacks:fn:craftPay
# (inventory first, then the Void). FIRE = harness only (records the events instead of the engine; TRUE = cancel).
for _f in ("public static java.util.function.Function FIRE = null;",
           "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile int CRAFTS = 0;", "public static volatile int REFUSED = 0;", "public static volatile int REFUNDS = 0;",
           "public static volatile int FALLBACK = 0;", "public static volatile int EVENTS = 0;", "public static volatile boolean WARNED = false;"):
    F(icr, _f)
M(icr, r"""
public static java.util.function.Function fn(String k) {
  Object o = null;
  try { o = @PKG@.MenuUtil.bridge().get(k); } catch (Throwable t) { o = null; }
  return (o instanceof java.util.function.Function) ? (java.util.function.Function) o : null;
}""")
M(icr, r"""
public static boolean voidMode() {
  return fn("sacks:fn:craftList") != null && fn("sacks:fn:craftHave") != null && fn("sacks:fn:craftPay") != null
      && fn("sacks:fn:craftRefund") != null && fn("sacks:fn:craftCommit") != null;
}""")
M(icr, r"""
public static void warnOnce(String s) {
  if (WARNED) return;
  WARNED = true;
  @PKG@.MenuUtil.warn("inventory crafting: " + s + " (logged once)");
}""")
M(icr, r"""
public static long num(Object o) { return (o instanceof Number) ? ((Number) o).longValue() : 0L; }""")
M(icr, r"""
public static String pretty(String id) {
  if (id == null) return "?";
  String s = id.startsWith("Skyy_") ? id.substring(5) : id;
  return s.replace('_', ' ').trim();
}""")
# the item's English name (the server's I18nModule, en-US - SkyySacks' /craft lookup), else its id made readable; cached
M(icr, r"""
public static String tr(String key) {
  if (key == null) return null;
  try {
    @I18N@ m = @I18N@.get();
    if (m == null) return null;
    String n = m.getMessage("en-US", key);
    if ((n == null || n.length() == 0) && key.startsWith("server.")) n = m.getMessage("en-US", key.substring(7));
    if (n == null) return null;
    n = n.trim();
    if (n.length() == 0 || (n.indexOf('.') > 0 && n.indexOf(' ') < 0)) return null;
    return n;
  } catch (Throwable t) { return null; }
}""")
M(icr, r"""
public static @ITEM@ item(String id) {
  if (id == null) return null;
  try { Object o = @ITEM@.getAssetMap().getAsset(id); return (o instanceof @ITEM@) ? (@ITEM@) o : null; } catch (Throwable t) { return null; }
}""")
# the pay view craftItem uses: backpack + storage + hotbar (Inventory's own combined container; built from the three when it has none)
M(icr, r"""
public static @IC@ bag(@PLA@ p) {
  @INV@ inv = p == null ? null : p.getInventory();
  if (inv == null) return null;
  @IC@ c = null;
  try { c = inv.getCombinedBackpackStorageHotbar(); } catch (Throwable t) { c = null; }
  if (c != null) return c;
  java.util.ArrayList l = new java.util.ArrayList();
  if (inv.getBackpack() != null) l.add(inv.getBackpack());
  if (inv.getStorage() != null) l.add(inv.getStorage());
  if (inv.getHotbar() != null) l.add(inv.getHotbar());
  return new com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer((@IC@[]) l.toArray(new @IC@[0]));
}""")
M(icr, r"""
public static @IC@ bagHotbarFirst(@PLA@ p) {
  @INV@ inv = p == null ? null : p.getInventory();
  if (inv == null) return null;
  @IC@ c = null;
  try { c = inv.getCombinedHotbarFirst(); } catch (Throwable t) { c = null; }
  if (c != null) return c;
  java.util.ArrayList l = new java.util.ArrayList();
  if (inv.getHotbar() != null) l.add(inv.getHotbar());
  if (inv.getStorage() != null) l.add(inv.getStorage());
  if (inv.getBackpack() != null) l.add(inv.getBackpack());
  return new com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer((@IC@[]) l.toArray(new @IC@[0]));
}""")
M(icr, r"""
public static String name(String id) {
  if (id == null) return "?";
  Object c = NAMES.get(id);
  if (c instanceof String) return (String) c;
  String n = null;
  @ITEM@ it = item(id);
  if (it != null) { try { n = tr(it.getTranslationKey()); } catch (Throwable t) { n = null; } }
  if (n == null) n = pretty(id);
  n = @PKG@.MenuUtil.safe(n);
  if (n.length() > 40) n = n.substring(0, 40);
  NAMES.put(id, n);
  return n;
}""")
M(icr, r"""
public static @CRR@ recipe(String rid) {
  if (rid == null) return null;
  try { Object o = @CRR@.getAssetMap().getAsset(rid); return (o instanceof @CRR@) ? (@CRR@) o : null; } catch (Throwable t) { return null; }
}""")
M(icr, r"""
public static String outId(@CRR@ r) {
  if (r == null) return null;
  @MQ@ po = r.getPrimaryOutput();
  if (po != null && po.getItemId() != null) return po.getItemId();
  @MQ@[] os = r.getOutputs();
  for (int i = 0; os != null && i < os.length; i++) { if (os[i] != null && os[i].getItemId() != null) return os[i].getItemId(); }
  return null;
}""")
M(icr, r"""
public static int outQty(@CRR@ r) {
  if (r == null) return 1;
  @MQ@ po = r.getPrimaryOutput();
  int q = po == null ? 1 : po.getQuantity();
  return q < 1 ? 1 : q;
}""")
# the bench tab of a recipe: "Crafting" = hand (Fieldcraft) + Workbench (Skyy 11-14: "the normal crafting bench adds to the default crafting
# section. but all the others get their own tab"); another bench = its id; a processing bench (Furnace, Tannery ...) = null (its own page)
# - except the Salvagebench, which SkyySacks crafts INSTANTLY (SackPool.instantProc): its own tab here (fixer: "nothing lost")
M(icr, r"""
public static String benchKey(@CRR@ r) {
  if (r == null) return null;
  @BRQ@[] b = r.getBenchRequirement();
  if (b == null || b.length == 0) return "Crafting";
  for (int i = 0; i < b.length; i++) {
    if (b[i] == null || b[i].type != @BTY@.Processing) continue;
    if (b[i].id != null && b[i].id.equalsIgnoreCase("Salvagebench")) return b[i].id;
    return null;
  }
  for (int i = 0; i < b.length; i++) {
    if (b[i] == null || b[i].id == null) continue;
    if (b[i].id.equals("Fieldcraft") || b[i].id.equals("Workbench")) return "Crafting";
  }
  for (int i = 0; i < b.length; i++) { if (b[i] != null && b[i].id != null && b[i].id.length() > 0) return b[i].id; }
  return "Crafting";
}""")
M(icr, r"""
public static boolean processing(String bk) { return "Furnace".equals(bk) || "Tannery".equals(bk); }""")
M(icr, r"""
public static String benchLabel(String bk) {
  if (bk == null) return "Bench";
  if (bk.equals("Tannery")) return "Tanning";
  String s = bk;
  String lo = s.toLowerCase();
  if (lo.endsWith("_bench")) s = s.substring(0, s.length() - 6);
  else if (lo.endsWith("bench") && s.length() > 5) s = s.substring(0, s.length() - 5);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < 14; i++) {
    char c = s.charAt(i);
    if (c == '_') sb.append(' ');
    else if (Character.isLetterOrDigit(c) && c < 128) sb.append(c);
  }
  String o = sb.toString().trim();
  return o.length() == 0 ? "Bench" : o;
}""")
# charm / accessory and pet / egg recipes stay on the Charms and Pets pages (Skyy 11-14: "lets keep the charm crafting in the charm page.
# same with the pets")
M(icr, r"""
public static boolean skip(@CRR@ r) {
  String o = outId(r);
  if (o == null) return true;
  return o.startsWith("Skyy_Talisman_") || o.startsWith("Skyy_Accessory_") || o.startsWith("Skyy_Acc_") || o.startsWith("Skyy_PetEgg")
      || o.startsWith("Skyy_Pet_");
}""")
M(icr, r"""
public static int tier(String id) {
  if (id == null) return 0;
  int k = java.util.Arrays.binarySearch(@PKG@.InvData.TT_IDS, id);
  if (k >= 0) return @PKG@.InvData.TT_T[k];
  for (int i = 0; i < @PKG@.InvData.TM_W.length; i++) {
    String w = @PKG@.InvData.TM_W[i];
    if (id.indexOf("_" + w + "_") >= 0 || id.endsWith("_" + w)) return @PKG@.InvData.TM_T[i];
  }
  return 0;
}""")
M(icr, r"""
public static String sortKey(@CRR@ r, String rid) {
  String o = outId(r);
  int t = tier(o);
  String p = t < 10 ? "00" + t : (t < 100 ? "0" + t : String.valueOf(t));
  return p + String.valueOf((char) 1) + name(o).toLowerCase() + String.valueOf((char) 1) + rid;
}""")
# the recipe ids this player may craft here, sorted by tier then name (world thread)
M(icr, r"""
public static java.util.ArrayList allowed(java.util.UUID u, @PLA@ p) {
  java.util.ArrayList ids = new java.util.ArrayList();
  if (voidMode()) {
    Object o = null;
    try { o = fn("sacks:fn:craftList").apply(new Object[] { u, "all" }); } catch (Throwable t) { o = null; warnOnce("sacks:fn:craftList failed: " + t); }
    if (o instanceof String[]) { String[] a = (String[]) o; for (int i = 0; i < a.length; i++) ids.add(a[i]); }
  } else if (p != null) {
    try {
      java.util.List l = @CRP@.getBenchRecipes(@BTY@.Crafting, "Fieldcraft");
      java.util.Set known = null;
      try { known = p.getPlayerConfigData() == null ? null : p.getPlayerConfigData().getKnownRecipes(); } catch (Throwable t) { known = null; }
      for (int i = 0; l != null && i < l.size(); i++) {
        Object x = l.get(i);
        if (!(x instanceof @CRR@)) continue;
        @CRR@ r = (@CRR@) x;
        if (r.isKnowledgeRequired() && (known == null || !(known.contains(r.getId()) || known.contains(outId(r))))) continue;
        ids.add(r.getId());
      }
    } catch (Throwable t) { warnOnce("the vanilla pocket recipe list could not be read: " + t); }
  }
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < ids.size(); i++) {
    String rid = (String) ids.get(i);
    if (rid == null || !seen.add(rid)) continue;
    @CRR@ r = recipe(rid);
    if (r == null || skip(r) || benchKey(r) == null) continue;
    keys.add(sortKey(r, rid));
  }
  java.util.Collections.sort(keys);
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < keys.size(); i++) { String k = (String) keys.get(i); out.add(k.substring(k.lastIndexOf((char) 1) + 1)); }
  return out;
}""")
M(icr, r"""
public static void add(java.util.HashMap m, String k, long n) {
  if (k == null || n <= 0L) return;
  Object o = m.get(k);
  m.put(k, Long.valueOf((o instanceof Long ? ((Long) o).longValue() : 0L) + n));
}""")
# what the player holds for the list's "can I make it" marks: plain stacks of backpack + storage + hotbar, + the Void (sacks:fn:all), + every
# resource type those items count as ("res:<type>"). The detail panel and the craft use SkyySacks' exact numbers (sacks:fn:craftHave).
M(icr, r"""
public static java.util.HashMap stock(java.util.UUID u, @PLA@ p) {
  java.util.HashMap m = new java.util.HashMap();
  try {
    @IC@ c = bag(p);
    int cap = c.getCapacity();
    for (int i = 0; i < cap; i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s == null || s.isEmpty() || s.getMetadata() != null) continue;
      add(m, s.getItemId(), (long) s.getQuantity());
    }
  } catch (Throwable t) { }
  java.util.function.Function f = fn("sacks:fn:all");
  if (f != null && u != null) {
    try {
      Object o = f.apply(u);
      if (o instanceof java.util.Map) {
        java.util.Iterator it = ((java.util.Map) o).entrySet().iterator();
        while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); if (e.getKey() instanceof String) add(m, (String) e.getKey(), num(e.getValue())); }
      }
    } catch (Throwable t) { }
  }
  java.util.HashMap res = new java.util.HashMap();
  java.util.Iterator it2 = m.entrySet().iterator();
  while (it2.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it2.next();
    @ITEM@ itm = item((String) e.getKey());
    if (itm == null) continue;
    @IRT@[] rts = null;
    try { rts = itm.getResourceTypes(); } catch (Throwable t) { rts = null; }
    for (int i = 0; rts != null && i < rts.length; i++) {
      if (rts[i] == null || rts[i].id == null) continue;
      add(res, "res:" + rts[i].id, ((Long) e.getValue()).longValue() * (long) (rts[i].quantity < 1 ? 1 : rts[i].quantity));
    }
  }
  m.putAll(res);
  return m;
}""")
M(icr, r"""
public static long can(@CRR@ r, java.util.HashMap m) {
  if (r == null) return 0L;
  @MQ@[] in = r.getInput();
  if (in == null || in.length == 0) return 0L;
  long best = Long.MAX_VALUE;
  for (int i = 0; i < in.length; i++) {
    if (in[i] == null) continue;
    String k = in[i].getItemId() != null ? in[i].getItemId() : "res:" + in[i].getResourceTypeId();
    Object o = m.get(k);
    long h = o instanceof Long ? ((Long) o).longValue() : 0L;
    int q = in[i].getQuantity() < 1 ? 1 : in[i].getQuantity();
    long c = h / (long) q;
    if (c < best) best = c;
  }
  return best == Long.MAX_VALUE ? 0L : best;
}""")
# the exact numbers: SkyySacks' craftHave {Long limit, String[] ids, Long[] have, Long[] need} (inventory + the Void, its own rules); without
# SkyySacks the same shape from the backpack + storage + hotbar (countRemovableMaterial, what craftItem pays from)
M(icr, r"""
public static Object[] have(java.util.UUID u, @PLA@ p, @CRR@ r) {
  if (r == null) return null;
  if (u != null && voidMode()) {
    try {
      Object o = fn("sacks:fn:craftHave").apply(new Object[] { u, String.valueOf(r.getId()) });
      if ((o instanceof Object[]) && ((Object[]) o).length >= 4) return (Object[]) o;
    } catch (Throwable t) { warnOnce("sacks:fn:craftHave failed: " + t); }
    return null;
  }
  if (p == null) return null;
  @MQ@[] in = r.getInput();
  int n = in == null ? 0 : in.length;
  @IC@ c = bag(p);
  String[] ids = new String[n];
  Long[] hv = new Long[n];
  Long[] nd = new Long[n];
  long lim = n == 0 ? 0L : Long.MAX_VALUE;
  for (int i = 0; i < n; i++) {
    if (in[i] == null) { ids[i] = "?"; hv[i] = Long.valueOf(0L); nd[i] = Long.valueOf(0L); continue; }
    ids[i] = in[i].getItemId() != null ? in[i].getItemId() : "res:" + in[i].getResourceTypeId();
    int h = c.countRemovableMaterial(in[i]);
    int q = in[i].getQuantity() < 1 ? 1 : in[i].getQuantity();
    hv[i] = Long.valueOf((long) h);
    nd[i] = Long.valueOf((long) q);
    long cc = (long) (h / q);
    if (cc < lim) lim = cc;
  }
  return new Object[] { Long.valueOf(lim == Long.MAX_VALUE ? 0L : lim), ids, hv, nd };
}""")
# an item of that resource type the player holds (the NEEDS icon of an "any Wood" input), else null
M(icr, r"""
public static String example(String rt, @PLA@ p) {
  if (rt == null || p == null) return null;
  try {
    @IC@ c = bag(p);
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s == null || s.isEmpty()) continue;
      @ITEM@ itm = item(s.getItemId());
      if (itm == null) continue;
      @IRT@[] rts = itm.getResourceTypes();
      for (int k = 0; rts != null && k < rts.length; k++) { if (rts[k] != null && rt.equals(rts[k].id)) return s.getItemId(); }
    }
  } catch (Throwable t) { }
  return null;
}""")
M(icr, r"""
public static String shortN(long v) {
  if (v >= 1000000L) return (v / 1000000L) + "m";
  if (v >= 10000L) return (v / 1000L) + "k";
  return String.valueOf(v);
}""")
M(icr, r"""
public static String clean(String q) {
  if (q == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < q.length() && sb.length() < 24; i++) {
    char c = q.charAt(i);
    if ((Character.isLetterOrDigit(c) && c < 128) || c == ' ') sb.append(c);
  }
  return sb.toString().trim();
}""")
M(icr, r"""
public static String rarity(String n) {
  if ("1".equals(n)) return "Common";
  if ("2".equals(n)) return "Uncommon";
  if ("3".equals(n)) return "Rare";
  if ("4".equals(n)) return "Epic";
  if ("5".equals(n)) return "Legendary";
  if ("6".equals(n)) return "Mythic";
  return "";
}""")
# pets:fn:hud (SkyyPets 0.4.20): String[2] { pet slot line, summon slot line }, 17 '|' fields each; null = cannot answer
M(icr, r"""
public static String[] pets(java.util.UUID u) {
  java.util.function.Function f = fn("pets:fn:hud");
  if (f == null || u == null) return null;
  try { Object o = f.apply(u); if ((o instanceof String[]) && ((String[]) o).length >= 2) return (String[]) o; } catch (Throwable t) { }
  return null;
}""")
# the equipped Void Charms: acc:has:<uuid> (bench charms) + acc:tal:<uuid> (talismans), "id,id"
M(icr, r"""
public static java.util.ArrayList charms(java.util.UUID u) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (u == null) return out;
  String[] ks = new String[] { "acc:has:" + u.toString(), "acc:tal:" + u.toString() };
  for (int k = 0; k < ks.length; k++) {
    Object o = null;
    try { o = @PKG@.MenuUtil.bridge().get(ks[k]); } catch (Throwable t) { o = null; }
    if (!(o instanceof String)) continue;
    String[] a = ((String) o).split(",");
    for (int i = 0; i < a.length; i++) { String id = a[i].trim(); if (id.length() > 0 && id.length() < 80 && !out.contains(id)) out.add(id); }
  }
  return out;
}""")
M(icr, r"""
public static int maxStack(String id) {
  @ITEM@ it = item(id);
  int m = 100;
  try { if (it != null) m = it.getMaxStack(); } catch (Throwable t) { m = 100; }
  return m < 1 ? 1 : m;
}""")
# how many crafts of r fit into backpack + storage + hotbar (All stops there; vanilla drops the rest of a click)
M(icr, r"""
public static int fits(@PLA@ p, @CRR@ r) {
  String id = outId(r);
  if (id == null) return 999;
  int per = outQty(r);
  int ms = maxStack(id);
  long room = 0L;
  try {
    @IC@ c = bag(p);
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s == null || s.isEmpty()) room = room + ms;
      else if (id.equals(s.getItemId()) && s.getMetadata() == null && s.getQuantity() < ms) room = room + (ms - s.getQuantity());
    }
  } catch (Throwable t) { return 999; }
  long n = room / (long) per;
  return (int) (n > 999L ? 999L : n);
}""")
# CraftRecipeEvent$Pre / $Post exactly as craftItem fires them (store.invoke(ref, event)); true = cancelled
M(icr, r"""
public static boolean cancelled(@REF@ ref, @ST@ st, Object e) {
  EVENTS = EVENTS + 1;
  if (FIRE != null) return Boolean.TRUE.equals(FIRE.apply(e));
  st.invoke(ref, (com.hypixel.hytale.component.system.EcsEvent) e);
  return ((@CEE@) e).isCancelled();
}""")
# PlayerCraftEvent on the event bus, keyed by the world name (craftItem's dispatchFor; only when someone listens)
M(icr, r"""
public static void told(@REF@ ref, @ST@ st, @PLA@ p, @CRR@ r, int k) {
  @PCE@ e = new @PCE@(ref, p, r, k);
  EVENTS = EVENTS + 1;
  if (FIRE != null) { FIRE.apply(e); return; }
  String wn = null;
  try { wn = ((@EST@) st.getExternalData()).getWorld().getName(); } catch (Throwable t) { wn = null; }
  @IEDP@ d = @HSV@.get().getEventBus().dispatchFor(@PCE@.class, wn);
  if (d != null && d.hasListener()) d.dispatch(e);
}""")
# the outputs as giveOutput gives them: each stack into InventoryUtils.getContainerForItemPickup (the player's pickup settings), addOrDrop
# (a full inventory drops the rest at the feet, never lost). Returns the items handed out; a throw mid-way stops (what was given stays given).
# Fixer: nothing handed out (no output stacks) = -1, so craftVoid refunds instead of committing a paid craft. addOrDropItemStack's boolean
# is "some of it was dropped at the feet" (bytecode: remainder not empty -> ItemUtils.dropItem, true), not a failure - so it is not checked.
M(icr, r"""
public static int give(@REF@ ref, @ST@ st, @PLA@ p, @CRR@ r, int k) {
  java.util.List outs = @CRM@.getOutputItemStacks(r, k);
  if (outs == null) return -1;
  @PSET@ ps = null;
  try { ps = (@PSET@) st.getComponent(ref, @PSET@.getComponentType()); } catch (Throwable t) { ps = null; }
  if (ps == null) { try { ps = @PSET@.defaults(); } catch (Throwable t) { ps = null; } }
  int n = 0;
  for (int i = 0; i < outs.size(); i++) {
    @IS@ s = (@IS@) outs.get(i);
    if (s == null || s.isEmpty()) continue;
    @IC@ c = null;
    try { if (ps != null) c = @IVU@.getContainerForItemPickup(ref, s.getItem(), ps, (@CAC@) st); } catch (Throwable t) { c = null; }
    if (c == null) { c = bagHotbarFirst(p); FALLBACK = FALLBACK + 1; }
    try { @SIC@.addOrDropItemStack((@CAC@) st, ref, c, s); }
    catch (Throwable t) { @PKG@.MenuUtil.warn("inventory crafting: handing out " + s.getItemId() + " x" + s.getQuantity() + " failed after " + n + " items: " + t); return n == 0 ? -1 : n; }
    n = n + s.getQuantity();
  }
  return n == 0 ? -1 : n;
}""")
M(icr, r"""
public static long refund(java.util.UUID u, String rc) {
  try { return num(fn("sacks:fn:craftRefund").apply(new Object[] { u, rc })); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory crafting: refund " + rc + " failed: " + t); return 0L; }
}""")
M(icr, r"""
public static boolean commit(java.util.UUID u, String rc) {
  try { return Boolean.TRUE.equals(fn("sacks:fn:craftCommit").apply(new Object[] { u, rc })); } catch (Throwable t) { return false; }
}""")
M(icr, r"""
public static int amount(@PLA@ p, @CRR@ r, long lim, int want) {
  int n = (int) (lim > 999L ? 999L : lim);
  if (want > 0 && want < n) n = want;
  if (want <= 0) { int fit = fits(p, r); if (fit < n) n = fit < 1 ? 1 : fit; }
  return n;
}""")
M(icr, r"""
public static String done(@CRR@ r, int k, int want) {
  String s = "Crafted " + (k * outQty(r)) + " x " + name(outId(r));
  if (want > 0 && k < want) s = s + " - only " + k + " of " + want + ", not enough materials";
  return s;
}""")
M(icr, r"""
public static String craftVoid(@REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, @CRR@ r, String rid, int want) {
  Object[] h = have(u, p, r);
  long lim = h == null ? 0L : num(h[0]);
  if (lim <= 0L) return "Not enough materials - nothing was used";
  int n = amount(p, r, lim, want);
  if (cancelled(ref, st, new @CREPRE@(r, n))) { REFUSED = REFUSED + 1; return "This craft was refused - nothing was used"; }
  Object o = null;
  try { o = fn("sacks:fn:craftPay").apply(new Object[] { u, rid, Long.valueOf((long) n) }); } catch (Throwable t) { o = null; @PKG@.MenuUtil.warn("inventory crafting: sacks:fn:craftPay failed: " + t); }
  Object[] pay = null;
  if (o instanceof Object[]) pay = (Object[]) o;
  long got = (pay == null || pay.length < 2) ? 0L : num(pay[0]);
  String rc = (pay != null && pay.length > 1 && (pay[1] instanceof String)) ? (String) pay[1] : null;
  if (got <= 0L || rc == null) {
    String why = (pay != null && pay.length > 2 && (pay[2] instanceof String)) ? (String) pay[2] : "not enough materials";
    if (why.indexOf('|') >= 0 || why.equals("table") || why.equals("know")) why = "this recipe is locked for you";
    return "Not crafted: " + @PKG@.MenuUtil.safe(why) + " - nothing was used";
  }
  int k = (int) got;
  boolean post = true;
  try { post = cancelled(ref, st, new @CREPOST@(r, k)); } catch (Throwable t) { post = true; @PKG@.MenuUtil.warn("inventory crafting: the Post event failed - refunded: " + t); }
  if (post) { refund(u, rc); REFUNDS = REFUNDS + 1; return "This craft was refused - your materials are back"; }
  int given = -1;
  try { given = give(ref, st, p, r, k); } catch (Throwable t) { given = -1; @PKG@.MenuUtil.warn("inventory crafting: the output of " + rid + " failed - refunded: " + t); }
  if (given < 0) { long b = refund(u, rc); REFUNDS = REFUNDS + 1; return b > 0L ? "The craft could not finish - your materials are back" : "The craft could not finish - an admin can check crafts.log"; }
  try { told(ref, st, p, r, k); } catch (Throwable t) { }
  commit(u, rc);
  CRAFTS = CRAFTS + 1;
  return done(r, k, want);
}""")
# without SkyySacks: the vanilla pocket craft itself (CraftingManager.craftItem on backpack + storage + hotbar: Pre, pay, Post, give, event)
M(icr, r"""
public static String craftPlain(@REF@ ref, @ST@ st, @PLA@ p, @CRR@ r, int want) {
  @CRM@ cm = null;
  try { cm = (@CRM@) st.getComponent(ref, @CRM@.getComponentType()); } catch (Throwable t) { cm = null; }
  if (cm == null) return "Crafting is not ready here - nothing was used";
  Object[] h = have(null, p, r);
  long lim = h == null ? 0L : num(h[0]);
  if (lim <= 0L) return "Not enough materials - nothing was used";
  int n = amount(p, r, lim, want);
  boolean ok = false;
  try { ok = cm.craftItem(ref, (@CAC@) st, r, n, bag(p)); } catch (Throwable t) { ok = false; @PKG@.MenuUtil.warn("inventory crafting: craftItem failed: " + t); }
  if (!ok) return "Not crafted - nothing was used";
  CRAFTS = CRAFTS + 1;
  return done(r, n, want);
}""")
# ONE craft click (world thread). The recipe id is the one drawn; it must still be allowed now (a recipe changed / locked between draw and
# click = refused, nothing used). want: 1, 10, 0 = All.
M(icr, r"""
public static String craft(@REF@ ref, @ST@ st, @PR@ pr, String rid, int want) {
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null || p.getInventory() == null) return "Your inventory could not be read - nothing was used";
  @CRR@ r = recipe(rid);
  if (r == null) return "That recipe is gone - nothing was used";
  java.util.UUID u = pr.getUuid();
  if (!allowed(u, p).contains(rid)) return "You cannot craft that here any more - nothing was used";
  if (voidMode()) return craftVoid(ref, st, p, u, r, rid, want);
  return craftPlain(ref, st, p, r, want);
}""")

# ---- InvPage part 1: grids, slots, moves
''')

# ---------- InvPage: the side panels, the craft panel, the build, the clicks
P.rep('''M(ipg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {''', r'''# 0.3.52: the side panels (pets / mount, Void Charms, Skills, teleports) - bridge reads only, world thread
M(ipg, r"""
public void petCard(@UCB@ b, String k, String line, String none) {
  java.util.ArrayList sl = new java.util.ArrayList();
  @IGS@ g = new @IGS@();
  String nm = none;
  String lv = "";
  if (line != null && line.length() > 0) {
    String[] f = line.split("\\|", -1);
    if (f.length >= 10) {
      nm = @PKG@.MenuUtil.safe(f[4]);
      String st = f.length > 15 ? f[15] : "";
      lv = "Lv " + @PKG@.MenuUtil.safe(f[5]) + "  " + @PKG@.InvCraft.rarity(f[3]) + ("riding".equals(st) ? "  riding" : ("down".equals(st) ? "  down" : ""));
      if (f[9].length() > 0 && f[9].length() < 80) { g.setItemStack(new @IS@(f[9], 1)); g.setName(nm); }
    }
  }
  sl.add(g);
  b.set("#SkyyInv" + k + "I.Slots", sl);
  b.set("#SkyyInv" + k + "N.Text", nm);
  b.set("#SkyyInv" + k + "L.Text", lv);
}""")
M(ipg, r"""
public void fillSide(@UCB@ b) {
  java.util.UUID u = this.playerRef.getUuid();
  String[] pl = @PKG@.InvCraft.pets(u);
  petCard(b, "Pet", pl == null ? "" : pl[0], "No pet");
  petCard(b, "Mnt", pl == null ? "" : pl[1], "No mount");
  java.util.ArrayList cs = @PKG@.InvCraft.charms(u);
  java.util.ArrayList vs = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.InvData.VCN; i++) {
    @IGS@ g = new @IGS@();
    if (i < cs.size()) g.setItemStack(new @IS@((String) cs.get(i), 1));
    vs.add(g);
  }
  b.set("#SkyyInvVc.Slots", vs);
  b.set("#SkyyInvVcN.Text", cs.size() == 0 ? "none equipped" : (cs.size() + " equipped"));
  java.util.ArrayList ps = new java.util.ArrayList();
  try { ps = @PKG@.StatsCalc.pairs(@PKG@.MenuUtil.bridge().get("skill:" + u.toString())); } catch (Throwable t) { ps = new java.util.ArrayList(); }
  for (int i = 0; i < @PKG@.InvData.SKN; i++) {
    String tx = "";
    if (i < ps.size()) { String[] e = (String[]) ps.get(i); tx = @PKG@.MenuUtil.safe(e[0]) + "  " + @PKG@.MenuUtil.safe(e[1]); }
    else if (i == 0) tx = "No skills yet";
    b.set("#SkyyInvSk" + i + ".Text", tx);
  }
  java.util.ArrayList tp = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.InvData.TPN; i++) {
    @IGS@ g = new @IGS@();
    if (i < @PKG@.InvData.TP_ID.length) { g.setItemStack(new @IS@(@PKG@.InvData.TP_ID[i], 1)); g.setName(@PKG@.InvData.TP_NAME[i]); g.setDescription(@PKG@.InvData.TP_DESC[i]); }
    tp.add(g);
  }
  b.set("#SkyyInvTp.Slots", tp);
}""")
# RIGHT NOW: the Home panel's rows from the same bridges (quest:fn:hud, SkyyGear's mystery bags, tree:<uuid> unspent points), Go buttons
M(ipg, r"""
public void fillNow(@UCB@ b, @UEB@ ev, @REF@ ref, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  java.util.ArrayList rows = new java.util.ArrayList();
  String q = null;
  try { q = @PKG@.MenuPage.questLine(u); } catch (Throwable t) { q = null; }
  if (q != null) rows.add(new String[] { q, "world:quests" });
  try {
    if (@PKG@.MenuUtil.bridge().get("gear:fn:smithing") instanceof java.util.function.Function) {
      int nb = @PKG@.MenuUtil.countPrefix((@PLA@) st.getComponent(ref, @PLA@.getComponentType()), "Skyy_Unid_Bag_");
      if (nb > 0) rows.add(new String[] { nb + (nb == 1 ? " mystery bag to identify" : " mystery bags to identify"), "smithing:identify" });
    }
  } catch (Throwable t) { }
  java.util.ArrayList tr = new java.util.ArrayList();
  try { tr = @PKG@.MenuPage.treeRows(u); } catch (Throwable t) { tr = new java.util.ArrayList(); }
  for (int i = 0; i < tr.size() && rows.size() < @PKG@.InvData.NOWN; i++) rows.add(tr.get(i));
  String[] tg = new String[rows.size()];
  if (rows.size() == 0) { b.appendInline("#SkyyInvNowL", @PKG@.InvData.NOW_EMPTY); b.set("#SkyyInvNrE.Text", @PKG@.InvData.NOW_NONE); }
  for (int i = 0; i < rows.size(); i++) {
    String[] r = (String[]) rows.get(i);
    tg[i] = r[1];
    b.appendInline("#SkyyInvNowL", @PKG@.InvData.NOW_ROW.replace("{I}", String.valueOf(i)));
    b.set("#SkyyInvNrT" + i + ".Text", @PKG@.MenuUtil.safe(r[0]));
    ev.addEventBinding(@BT@.Activating, "#SkyyInvNrB" + i, @EVD@.of("a", "now:" + i));
  }
  this.nowT = tg;
}""")
# the recipe detail (the selected recipe: output, tier, bench, NEEDS with have / need from the exact numbers, the Ready line)
M(ipg, r"""
public void fillDetail(@UCB@ b, java.util.UUID u, @PLA@ p, java.util.ArrayList all) {
  java.util.ArrayList os = new java.util.ArrayList();
  java.util.ArrayList ns = new java.util.ArrayList();
  @IGS@ og = new @IGS@();
  String nm = "Pick a recipe";
  String sub = "";
  String rd = this.cnote.length() > 0 ? this.cnote : @PKG@.InvData.CF_HINT;
  String[] qs = new String[@PKG@.InvData.NMAX];
  for (int i = 0; i < qs.length; i++) qs[i] = "";
  @CRR@ r = this.csel == null ? null : @PKG@.InvCraft.recipe(this.csel);
  if (r != null && !all.contains(this.csel)) r = null;
  if (r == null) this.csel = null;
  if (r != null) {
    String oid = @PKG@.InvCraft.outId(r);
    int oq = @PKG@.InvCraft.outQty(r);
    if (oid != null) og.setItemStack(new @IS@(oid, oq));
    nm = @PKG@.InvCraft.name(oid);
    int t = @PKG@.InvCraft.tier(oid);
    sub = (t > 0 ? "T" + t + "  -  " : "") + @PKG@.InvCraft.benchLabel(@PKG@.InvCraft.benchKey(r)) + (oq > 1 ? "  -  makes " + oq : "");
    Object[] h = @PKG@.InvCraft.have(u, p, r);
    long lim = 0L;
    if (h != null) {
      lim = @PKG@.InvCraft.num(h[0]);
      String[] ids = (String[]) h[1];
      Object[] hv = (Object[]) h[2];
      Object[] nd = (Object[]) h[3];
      for (int i = 0; ids != null && i < ids.length && i < @PKG@.InvData.NMAX; i++) {
        @IGS@ g = new @IGS@();
        String iid = ids[i];
        boolean res = iid != null && iid.startsWith("res:");
        String show = res ? @PKG@.InvCraft.example(iid.substring(4), p) : iid;
        if (show != null && show.length() > 0 && !show.equals("?")) {
          g.setItemStack(new @IS@(show, 1));
          g.setName(res ? "Any " + @PKG@.InvCraft.pretty(iid.substring(4)) : @PKG@.InvCraft.name(iid));
        }
        long a = @PKG@.InvCraft.num(hv[i]);
        long n = @PKG@.InvCraft.num(nd[i]);
        qs[i] = @PKG@.InvCraft.shortN(a) + " / " + n;
        ns.add(g);
      }
    }
    if (this.cnote.length() == 0) rd = lim > 0L ? "Ready - you can make " + lim : "Not enough materials yet";
  }
  while (ns.size() < @PKG@.InvData.NMAX) ns.add(new @IGS@());
  os.add(og);
  b.set("#SkyyInvCo.Slots", os);
  b.set("#SkyyInvCn.Slots", ns);
  b.set("#SkyyInvCoN.Text", nm);
  b.set("#SkyyInvCoS.Text", sub);
  for (int i = 0; i < qs.length; i++) b.set("#SkyyInvNq" + i + ".Text", qs[i]);
  b.set("#SkyyInvCrd.Text", rd);
  this.cnote = "";
}""")
# the craft panel: bench tabs (run time), the filtered recipe page (tier, then name), the page number, the info line, the toggle, the detail
M(ipg, r"""
public void fillCraft(@UCB@ b, @UEB@ ev, @REF@ ref, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  java.util.ArrayList all = p == null ? new java.util.ArrayList() : @PKG@.InvCraft.allowed(u, p);
  java.util.HashMap stock = p == null ? new java.util.HashMap() : @PKG@.InvCraft.stock(u, p);
  java.util.ArrayList bs = new java.util.ArrayList();
  bs.add("Crafting");
  for (int i = 0; i < all.size(); i++) {
    String bk = @PKG@.InvCraft.benchKey(@PKG@.InvCraft.recipe((String) all.get(i)));
    if (bk != null && !bs.contains(bk)) bs.add(bk);
  }
  if (@PKG@.InvCraft.voidMode()) { if (!bs.contains("Furnace")) bs.add("Furnace"); if (!bs.contains("Tannery")) bs.add("Tannery"); }
  while (bs.size() > @PKG@.InvData.BMAX) bs.remove(bs.size() - 1);
  if (!bs.contains(this.cbench) || @PKG@.InvCraft.processing(this.cbench)) this.cbench = "Crafting";
  this.cbenches = bs;
  int bw = (@PKG@.InvData.BW_ALL - 4 * bs.size()) / bs.size();
  if (bw > 120) bw = 120;
  for (int i = 0; i < bs.size(); i++) {
    String bk = (String) bs.get(i);
    b.appendInline("#SkyyInvCfB", @PKG@.InvData.BENCH_BTN.replace("{I}", String.valueOf(i)).replace("{W}", String.valueOf(bw)).replace("{S}", bk.equals(this.cbench) ? @PKG@.InvData.ST_TABSEL : @PKG@.InvData.ST_TAB));
    b.set("#SkyyInvBt" + i + ".Text", @PKG@.InvCraft.benchLabel(bk));
    ev.addEventBinding(@BT@.Activating, "#SkyyInvBt" + i, @EVD@.of("a", "cb:" + i));
  }
  String q = this.cquery.toLowerCase();
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.ArrayList cans = new java.util.ArrayList();
  for (int i = 0; i < all.size(); i++) {
    String rid = (String) all.get(i);
    @CRR@ r = @PKG@.InvCraft.recipe(rid);
    if (r == null || !this.cbench.equals(@PKG@.InvCraft.benchKey(r))) continue;
    String oid = @PKG@.InvCraft.outId(r);
    if (q.length() > 0 && @PKG@.InvCraft.name(oid).toLowerCase().indexOf(q) < 0 && (oid == null || oid.toLowerCase().indexOf(q) < 0)) continue;
    long c = @PKG@.InvCraft.can(r, stock);
    if (this.conly && c <= 0L) continue;
    rows.add(rid);
    cans.add(Long.valueOf(c));
  }
  int per = @PKG@.InvData.CC * @PKG@.InvData.CR;
  int np = rows.size() == 0 ? 1 : (rows.size() + per - 1) / per;
  if (this.cpage >= np) this.cpage = np - 1;
  if (this.cpage < 0) this.cpage = 0;
  int from = this.cpage * per;
  java.util.ArrayList sl = new java.util.ArrayList();
  String[] shown = new String[per];
  for (int k = 0; k < per; k++) {
    @IGS@ g = new @IGS@();
    int at = from + k;
    if (at < rows.size()) {
      String rid = (String) rows.get(at);
      @CRR@ r = @PKG@.InvCraft.recipe(rid);
      String oid = @PKG@.InvCraft.outId(r);
      shown[k] = rid;
      if (oid != null) {
        g.setItemStack(new @IS@(oid, @PKG@.InvCraft.outQty(r)));
        g.setItemUncraftable(((Long) cans.get(at)).longValue() <= 0L);
      }
    }
    sl.add(g);
  }
  this.cshown = shown;
  b.set("#SkyyInvCg.Slots", sl);
  b.set("#SkyyInvCpN.Text", (this.cpage + 1) + " / " + np);
  String info = rows.size() + (rows.size() == 1 ? " recipe" : " recipes") + " - " + @PKG@.InvCraft.benchLabel(this.cbench)
      + (this.cbench.equals("Crafting") ? " (hand + Workbench)" : "") + (q.length() > 0 ? " - search: " + this.cquery : "")
      + (@PKG@.InvCraft.voidMode() ? " - materials: inventory, then the Void" : "");
  b.set("#SkyyInvCi.Text", info);
  if (this.cquery.length() > 0) b.set("#SkyyInvCq.Value", this.cquery);
  b.set("#SkyyInvCfOnly.Text", this.conly ? "Craftable only - On" : "Craftable only - Off");
  fillDetail(b, u, p, all);
}""")
M(ipg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {''')
P.rep('''  fillChar(b, ref, st);
  if (this.tcap.length() > 0) b.set("#SkyyInvCap.Text", this.tcap);
  bindGrid(ev, "s");
  bindGrid(ev, "h");
  ev.addEventBinding(@BT@.Dropped, "#SkyyInvDz", @EVD@.of("a", "dz"), false);''', '''  fillChar(b, ref, st);
  if (this.tcap.length() > 0) b.set("#SkyyInvCap.Text", this.tcap);
  bindGrid(ev, "s");
  bindGrid(ev, "h");
  ev.addEventBinding(@BT@.Dropped, "#SkyyInvDz", @EVD@.of("a", "dz"), false);
  // 0.3.52: the side panels, Right now, the craft panel; the click-only grids; the search (Enter or Search carries the typed text)
  try { fillSide(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the side panels failed: " + t); }
  try { fillNow(b, ev, ref, st); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: Right now failed: " + t); }
  try { fillCraft(b, ev, ref, st); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the craft panel failed: " + t); }
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvCg", @EVD@.of("a", "cr"), false);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvTp", @EVD@.of("a", "tp"), false);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvVc", @EVD@.of("a", "vc"), false);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvPetI", @EVD@.of("a", "pet"), false);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvMntI", @EVD@.of("a", "pet"), false);
  String qk = String.valueOf((char) 64) + "Q";
  ev.addEventBinding(@BT@.Validating, "#SkyyInvCq", @EVD@.of("a", "cq").append(qk, "#SkyyInvCq.Value"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyInvCqGo", @EVD@.of("a", "cq").append(qk, "#SkyyInvCq.Value"));''')

# ---------- the clicks: craft() (0.3.51's close + vanilla pass) becomes our crafting
P.rep('''M(ipg, r"""
public void craft(@REF@ ref, @ST@ st) {
  this.answered = true;
  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.InvState.REDIR.remove(u);
  @PKG@.InvState.PASS.put(u, Long.valueOf(System.currentTimeMillis()));
  @PKG@.InvState.tell(this.playerRef, "Press Tab to open crafting (vanilla screen) - our own crafting comes in a later update.");
  shut();
}""")''', r'''M(ipg, r"""
public boolean still() {
  try {
    @PLA@ p = (@PLA@) this.pst.getComponent(this.pref, @PLA@.getComponentType());
    return p != null && p.getPageManager().getCustomPage() == this;
  } catch (Throwable t) { return false; }
}""")
# a state change on this page = ONE full redraw (no periodic updates; the inventory grids are re-sent with it)
M(ipg, r"""
public void redraw() {
  this.answered = true;
  if (!still()) { finish("replaced"); return; }
  this.rebuild();
}""")
# 0.3.52: Craft / x10 / All on the selected recipe (InvCraft.craft: Pre -> pay inventory then the Void -> Post -> give -> PlayerCraftEvent)
M(ipg, r"""
public void craft(@REF@ ref, @ST@ st, int want) {
  this.answered = true;
  if (this.csel == null) { say("Pick a recipe first"); return; }
  String r = null;
  try { r = @PKG@.InvCraft.craft(ref, st, this.playerRef, this.csel, want); }
  catch (Throwable t) { r = "Crafting failed - nothing was used"; @PKG@.MenuUtil.warn("inventory crafting: " + this.csel + " failed: " + t); }
  this.crafts = this.crafts + 1;
  this.cnote = r == null ? "" : r;
  redraw();
}""")
M(ipg, r"""
public void pick(int i) {
  if (i < 0 || this.cshown == null || i >= this.cshown.length || this.cshown[i] == null) { say("That slot is empty"); return; }
  this.csel = this.cshown[i];
  this.cnote = "";
  redraw();
}""")
M(ipg, r"""
public void openHub(String hub, String tab, String label) {
  this.answered = true;
  String r = null;
  try {
    r = @PKG@.HubBar.open(this.playerRef, this.playerRef.getUuid(), hub, tab);
    if (r == null || !@PKG@.MenuHub.opened(r)) r = @PKG@.MenuHub.run(this.playerRef, hub);
  } catch (Throwable t) { r = "failed"; @PKG@.MenuUtil.warn("inventory: opening " + label + " failed: " + t); }
  if (!still()) { finish("hub " + hub); return; }
  say(@PKG@.MenuHub.opened(r) ? "Opening " + label : label + " is not on this server right now");
}""")
M(ipg, r"""
public void openFn(String k1, String k2, String label) {
  this.answered = true;
  java.util.function.Function f = @PKG@.InvCraft.fn(k1);
  if (f == null) f = @PKG@.InvCraft.fn(k2);
  Object o = null;
  try { if (f != null) o = f.apply(this.playerRef.getUuid()); } catch (Throwable t) { o = null; @PKG@.MenuUtil.warn("inventory: opening " + label + " failed: " + t); }
  if (!still()) { finish("bridge " + label); return; }
  say(Boolean.TRUE.equals(o) ? "Opening " + label : label + " is not on this server right now");
}""")
# a bench tab: Crafting / a bench = its recipes here; Furnace / Tanning = the pack's own timed page (PROCESSING STATIONS)
M(ipg, r"""
public void bench(int i) {
  if (i < 0 || i >= this.cbenches.size()) { say("No such bench tab"); return; }
  String bk = (String) this.cbenches.get(i);
  if (bk.equals("Furnace")) { openFn("sacks:fn:openFurnace", "sacks:fn:openFurnace", "the Furnace"); return; }
  if (bk.equals("Tannery")) { openHub("smithing", "recipes", "the Crafting page - pick its Tannery tab"); return; }
  this.cbench = bk;
  this.cpage = 0;
  this.csel = null;
  this.cnote = "";
  redraw();
}""")
M(ipg, r"""
public void teleport(int i) {
  this.answered = true;
  if (i < 0 || i >= @PKG@.InvData.TP_CMD.length) { say("An empty teleport slot"); return; }
  String cmd = @PKG@.InvData.TP_CMD[i];
  shut();
  try { @CMGR@.get().handleCommand(this.playerRef, cmd); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: /" + cmd + " failed: " + t); }
}""")
M(ipg, r"""
public void nowGo(int i) {
  if (i < 0 || this.nowT == null || i >= this.nowT.length || this.nowT[i] == null) { say("Nothing there now"); return; }
  String t = this.nowT[i];
  int c = t.indexOf(':');
  String hub = c < 0 ? t : t.substring(0, c);
  String tab = c < 0 ? "" : t.substring(c + 1);
  if (hub.equals("tree")) { openHub("character", "trees", "your trees"); return; }
  openHub(hub, tab, hub.equals("world") ? "Quests" : "that page");
}""")''')
P.rep('''    if (a.equals("craft")) { craft(ref, st); return; }
    if (a.equals("sort")) { clearDrag(); answer(sort()); return; }''', '''    if (a.equals("sort")) { clearDrag(); answer(sort()); return; }
    // 0.3.52: our own crafting + the side panels
    if (a.equals("cr")) { pick(ival(d, "SlotIndex", -1)); return; }
    if (a.startsWith("cx:")) { int w = 1; try { w = Integer.parseInt(a.substring(3)); } catch (Throwable t) { w = 1; } craft(ref, st, w); return; }
    if (a.startsWith("cb:")) { int w = -1; try { w = Integer.parseInt(a.substring(3)); } catch (Throwable t) { w = -1; } bench(w); return; }
    if (a.equals("conly")) { this.conly = !this.conly; this.cpage = 0; redraw(); return; }
    if (a.equals("cq")) { this.cquery = @PKG@.InvCraft.clean(val(d, String.valueOf((char) 64) + "Q")); this.cpage = 0; redraw(); return; }
    if (a.equals("cqx")) { this.cquery = ""; this.cpage = 0; redraw(); return; }
    if (a.equals("cpp")) { this.cpage = this.cpage - 1; redraw(); return; }
    if (a.equals("cpn")) { this.cpage = this.cpage + 1; redraw(); return; }
    if (a.equals("pkc")) { say("You are on Craft"); return; }
    if (a.equals("pkv")) { openHub("storage", "pocket", "the Void"); return; }
    if (a.equals("rq")) { openFn("requip:fn:open", "wardrobe:fn:open", "Requip"); return; }
    if (a.equals("vc")) { openHub("character", "accessories", "Void Charms"); return; }
    if (a.equals("pet")) { goTab(2); return; }
    if (a.equals("tp")) { teleport(ival(d, "SlotIndex", -1)); return; }
    if (a.equals("nowq")) { openHub("world", "quests", "Quests"); return; }
    if (a.startsWith("now:")) { int w = -1; try { w = Integer.parseInt(a.substring(4)); } catch (Throwable t) { w = -1; } nowGo(w); return; }''')
# the read-only armour line no longer points at the vanilla screen
P.rep('''  if (!movable(sg) || !movable(tg)) return mv(false, "Armour and off-hand are read only here - Crafting - Tab, then Tab, for the vanilla screen");''',
      '''  if (!movable(sg) || !movable(tg)) return mv(false, "Armour and off-hand are read only here for now - Requip changes them");''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.52 adds no system, no command"
for _w in ("Crafting - Tab", "vanilla crafting screen (every recipe)", '"craftA"', "CraftBtn"):
    assert _w not in P.s[P.s.index('VERSION = "0.3.52"'):], "0.3.52: still in the build: " + _w
_i = P.s.index
assert _i("public static String craft(@REF@ ref, @ST@ st, @PR@ pr") < _i("# ---- InvPage part 1: grids, slots, moves") < _i("public void fillCraft(")
P.finish()

# ---- the harness texts (used below)
HARNESS_EXPECT = '''ADDED = ["InvCraft"]
EXPECT = {
    "InvPage": ["+f cbench", "+f cbenches", "+f cnote", "+f conly", "+f cpage", "+f cquery", "+f crafts", "+f cshown", "+f csel", "+f nowT",
                "+m bench", "+m fillCraft", "+m fillDetail", "+m fillNow", "+m fillSide", "+m nowGo", "+m openFn", "+m openHub", "+m petCard",
                "+m pick", "+m redraw", "+m still", "+m teleport", "+m craft", "-m craft", "~c ", "~m build", "~m handleDataEvent", "~m move"],   # craft(ref, st) -> craft(ref, st, want)
    "InvData": ["~<clinit>", "+f BENCH_BTN", "+f BMAX", "+f BW_ALL", "+f CC", "+f CF_HINT", "+f CR", "+f NMAX", "+f NOWN", "+f NOW_EMPTY",
                "+f NOW_NONE", "+f NOW_ROW", "+f SKN", "+f ST_TAB", "+f ST_TABSEL", "+f TM_T", "+f TM_W", "+f TPN", "+f TP_CMD", "+f TP_DESC",
                "+f TP_ID", "+f TP_NAME", "+f TT_IDS", "+f TT_T", "+f VCN"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text in the setup lines (as every version)
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string
}
'''
HARNESS_CRAFT = r'''    # ---- CRAFT (0.3.52; TEST 285 "the goal is to use our own craft not the vanilla one."): OUR crafting, EXECUTED on the stand-ins
    IC_ = JV("InvCraft")
    JS = JClass("java.lang.String")
    LONGc = JClass("java.lang.Long")
    OBJ = lambda xs: _JA(JClass("java.lang.Object"))(xs)
    CRRc = JClass(PH + "server.core.asset.type.item.config.CraftingRecipe")
    MQc = JClass(PH + "server.core.inventory.MaterialQuantity")
    BRQc = JClass(PH + "protocol.BenchRequirement")
    BTYc = JClass(PH + "protocol.BenchType")
    for iid_, ms_ in (("Ingredient_Stick", 100), ("Furniture_Torch", 25), ("Tool_Pickaxe_Iron", 1), ("Ingredient_Bar_Iron", 100),
                      ("Weapon_Sword_Copper", 1), ("Skyy_PetEgg_Wolf", 1), ("Skyy_Talisman_Speed_T1", 1), ("Skyy_Menu_Icon_MyIsland", 1),
                      ("Skyy_Menu_Icon_Hub", 1), ("Skyy_PetIcon_Wolf_Legendary", 1), ("Skyy_Accessory_Workbench_T1", 1)):
        it_ = Ucls.allocateInstance(ITc.class_)
        E.jf(ITc.class_, "id").set(it_, iid_)
        E.jf(ITc.class_, "translationProperties").set(it_, Ucls.allocateInstance(ITPc.class_))
        E.jf(ITc.class_, "maxStack").setInt(it_, ms_)
        amap.put(iid_, it_)
    rdam = DAMc()
    rast = Ucls.allocateInstance(JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore").class_)
    E.jf(AScls.class_, "assetMap").set(rast, rdam)
    ramap = E.jf(DAMc.class_, "assetMap").get(rdam)
    E.jf(CRRc.class_, "ASSET_STORE").set(None, rast)

    def mq(i_, q_):
        return MQc(i_, None, None, q_, None)

    def recipe(rid_, ins_, out_, oq_, bench_, btype_="Crafting"):
        r_ = Ucls.allocateInstance(CRRc.class_)
        E.jf(CRRc.class_, "id").set(r_, rid_)
        E.jf(CRRc.class_, "input").set(r_, _JA(MQc)([mq(a_, b_) for a_, b_ in ins_]))
        po_ = mq(out_, oq_)
        E.jf(CRRc.class_, "primaryOutput").set(r_, po_)
        E.jf(CRRc.class_, "outputs").set(r_, _JA(MQc)([po_]))
        E.jf(CRRc.class_, "primaryOutputQuantity").setInt(r_, oq_)
        E.jf(CRRc.class_, "benchRequirement").set(r_, _JA(BRQc)([BRQc(getattr(BTYc, btype_), bench_, None, 0, None)]))
        ramap.put(rid_, r_)
        return rid_
    R1 = recipe("Skyy_Test_Stick", [("Wood_Oak_Trunk", 1)], "Ingredient_Stick", 4, "Fieldcraft")
    R2 = recipe("Skyy_Test_Torch", [("Ingredient_Stick", 1), ("Rock_Stone", 1)], "Furniture_Torch", 2, "Fieldcraft")
    R3 = recipe("Skyy_Test_Pick", [("Ingredient_Bar_Iron", 3), ("Ingredient_Stick", 2)], "Tool_Pickaxe_Iron", 1, "Workbench")
    R4 = recipe("Skyy_Test_Sword", [("Ingredient_Bar_Iron", 2)], "Weapon_Sword_Copper", 1, "Weapon_Bench")
    R5 = recipe("Skyy_Test_Egg", [("Rock_Stone", 1)], "Skyy_PetEgg_Wolf", 1, "Fieldcraft")
    R6 = recipe("Skyy_Test_Charm", [("Rock_Stone", 1)], "Skyy_Talisman_Speed_T1", 1, "Fieldcraft")
    R7 = recipe("Skyy_Test_Ingot", [("Rock_Stone", 1)], "Ingredient_Bar_Iron", 1, "Furnace", "Processing")
    FILL = [recipe("Skyy_Test_F%02d" % k_, [("Rock_Stone", 1)], "Plant_Fruit_Apple", 1, "Fieldcraft") for k_ in range(22)]
    LIST = [R1, R2, R3, R4, R5, R6, R7] + FILL
    CRAFTING = set([R1, R2, R3] + FILL)
    PK = E.player(uid=UUIDc(0x53, 0x53), name="SkyyCraftA")
    byU.put(PK.pr.getUuid(), PK.pr)
    put(PK, "storage", 0, ISc("Wood_Oak_Trunk", 2))
    put(PK, "storage", 1, ISc("Rock_Stone", 3))
    put(PK, "storage", 2, ISc("Ingredient_Bar_Iron", 3))
    VOID = {"Wood_Oak_Trunk": 5}
    CALLS, REC, PAYFAIL = [], {}, [False]
    EVS, CANCEL = [], {"Pre": False, "Post": False}
    FALSE = JClass("java.lang.Boolean").FALSE

    def take_inv(PP, iid_, q_):
        got_ = 0
        for f_ in ("storage", "hotbar"):
            ic_ = inv(PP, f_)
            for i_ in range(int(ic_.getCapacity())):
                s_ = ic_.getItemStack(JShort(i_))
                if got_ >= q_ or s_ is None or s_.isEmpty() or str(s_.getItemId()) != iid_:
                    continue
                n_ = min(q_ - got_, int(s_.getQuantity()))
                rest_ = int(s_.getQuantity()) - n_
                ic_.removeItemStackFromSlot(JShort(i_))                  # the whole stack out, the rest back in the same slot
                if rest_:
                    ic_.addItemStackToSlot(JShort(i_), ISc(iid_, rest_))
                got_ += n_
        return got_

    def have_py(rid_):
        r_ = ramap.get(rid_)
        ids_, hv_, nd_, lim_ = [], [], [], None
        for m_ in r_.getInput():
            i_, q_ = str(m_.getItemId()), int(m_.getQuantity())
            h_ = E.count(PK, i_) + VOID.get(i_, 0)
            ids_.append(i_)
            hv_.append(h_)
            nd_.append(q_)
            lim_ = h_ // q_ if lim_ is None else min(lim_, h_ // q_)
        return lim_ or 0, ids_, hv_, nd_

    def f_list(o):
        CALLS.append(("list", str(o[1])))
        return _JA(JS)(LIST)

    def f_have(o):
        lim_, ids_, hv_, nd_ = have_py(str(o[1]))
        return OBJ([LONGc(lim_), _JA(JS)(ids_), _JA(LONGc)([LONGc(x_) for x_ in hv_]), _JA(LONGc)([LONGc(x_) for x_ in nd_])])

    def f_pay(o):
        rid_, n_ = str(o[1]), int(o[2])
        CALLS.append(("pay", rid_, n_))
        if PAYFAIL[0] or have_py(rid_)[0] < n_:
            return OBJ([LONGc(0), None, "not enough materials"])
        ti_, tv_ = [], {}
        for m_ in ramap.get(rid_).getInput():
            i_, need_ = str(m_.getItemId()), int(m_.getQuantity()) * n_
            g_ = take_inv(PK, i_, need_)                      # the inventory FIRST
            ti_.append((i_, g_))
            if need_ - g_:
                VOID[i_] = VOID.get(i_, 0) - (need_ - g_)     # then the Void
                tv_[i_] = need_ - g_
        rc_ = "rc%d" % len(REC)
        REC[rc_] = [ti_, tv_, "open"]
        return OBJ([LONGc(n_), rc_, None])

    def f_refund(o):
        e_ = REC.get(str(o[1]))
        CALLS.append(("refund", str(o[1])))
        if not e_ or e_[2] != "open":
            return LONGc(0)
        for i_, g_ in e_[0]:
            if g_:
                inv(PK, "storage").addItemStack(ISc(i_, g_))
        for i_, g_ in e_[1].items():
            VOID[i_] = VOID.get(i_, 0) + g_
        e_[2] = "refunded"
        return LONGc(1)

    def f_commit(o):
        e_ = REC.get(str(o[1]))
        CALLS.append(("commit", str(o[1])))
        if not e_ or e_[2] != "open":
            return FALSE
        e_[2] = "committed"
        return TRUE

    def f_all(o):
        m_ = JClass("java.util.HashMap")()
        for k_, v_ in VOID.items():
            m_.put(k_, LONGc(v_))
        return m_
    OPENED = []

    def f_furnace(o):
        OPENED.append(str(o))
        return TRUE

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            try:
                return self.f(o)
            except Exception as x_:
                import traceback as tb_
                K.notes.append("STUB FAILED: " + " | ".join(tb_.format_exc().splitlines()[-8:]))
                raise

    @JImplements("java.util.function.Function")
    class Fire(object):
        @JOverride
        def apply(self, e):
            nm_ = str(e.getClass().getSimpleName())
            EVS.append(nm_)
            return TRUE if CANCEL.get(nm_) else FALSE
    SACKS = {"sacks:fn:craftList": f_list, "sacks:fn:craftHave": f_have, "sacks:fn:craftPay": f_pay, "sacks:fn:craftRefund": f_refund,
             "sacks:fn:craftCommit": f_commit, "sacks:fn:all": f_all, "sacks:fn:openFurnace": f_furnace}
    for k_, f_ in SACKS.items():
        BR.put(k_, Fn(f_))
    uk = str(PK.pr.getUuid())
    BR.put("pets:fn:hud", Fn(lambda o: _JA(JS)(["1|p1|Wolf|5|Wolf|42|50|10|90|Skyy_PetIcon_Wolf_Legendary||||||", ""])))
    BR.put("acc:has:" + uk, "Skyy_Accessory_Workbench_T1")
    BR.put("acc:tal:" + uk, "Skyy_Talisman_Speed_T1,Skyy_Accessory_Workbench_T1")
    BR.put("skill:" + uk, "Mining:12,Farming:5")
    BR.put("quest:fn:hud", Fn(lambda o: OBJ(["The Farming Island", "1 / 3", "Talk to the Farmer", "0 / 1", JClass("java.lang.Double")(0.0), "", "", FALSE])))
    IC_.FIRE = Fire()
    K.check(bool(IC_.voidMode()), "CRAFT: SkyySacks' five craft bridges present = the Void mode")
    f0 = len(E.sent(PK))
    pg = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    pk = pages(PK, f0)
    cm = cmap(pk[-1]) if pk else {}
    K.eq([sval(cm, "#SkyyInvBt%d.Text" % k_) for k_ in range(5)], ["Crafting", "Weapon", "Furnace", "Tanning", None],
         "CRAFT tabs: Crafting (hand + Workbench), one tab per other bench (Weapon_Bench), the pack's Furnace + Tanning")
    K.check(pk and all(("#SkyyInvBt%d" % k_) in [b_[1] for b_ in binds_of(pk[-1])] for k_ in range(4)), "CRAFT tabs: each bench tab is bound")
    shown = [str(x_) for x_ in pg.cshown if x_ is not None]
    seen = set(shown)
    K.check(len(shown) == 21 and not [x_ for x_ in shown if x_ in (R4, R5, R6, R7)],
            "CRAFT list: a full page of 21; no charm, pet egg, processing (Furnace) or other-bench recipe on Crafting")
    tiers = [int(IC_.tier(IC_.outId(IC_.recipe(x_)))) for x_ in shown]
    K.check(tiers == sorted(tiers), "CRAFT order: tier first, then name (%s)" % tiers)
    K.eq(sval(cm, "#SkyyInvCpN.Text"), "1 / 2", "CRAFT pages: 25 Crafting recipes = 2 pages of 21")
    gs_ = cm.get("#SkyyInvCg.Slots", "")
    K.check("ItemDisplay" not in gs_ and "Skyy_Test" not in gs_ and "Ingredient_Stick" in gs_,
            "CRAFT grid: output icons only (new ItemStack(id, qty) - no metadata, no recipe ids sent)")
    one(ev(PK, {"a": "cpn"}), "CRAFT next page")
    seen |= set(str(x_) for x_ in pg.cshown if x_ is not None)
    K.eq(seen, CRAFTING, "CRAFT 'nothing lost': every allowed pocket + Workbench recipe is reachable over the pages")
    p_ = one(ev(PK, {"a": "cpn"}), "CRAFT next past the end")
    K.eq(sval(cmap(p_), "#SkyyInvCpN.Text") if p_ else None, "2 / 2", "CRAFT pages: clamped at the last page")
    one(ev(PK, {"a": "cpp"}), "CRAFT prev")
    p_ = one(ev(PK, {"a": "conly"}), "CRAFT Craftable only")
    co = [str(x_) for x_ in pg.cshown if x_ is not None]
    K.check(R1 in co and R2 not in co and R3 not in co and p_ is not None and "On" in (sval(cmap(p_), "#SkyyInvCfOnly.Text") or ""),
            "CRAFT Craftable only: the trunk recipe (inventory + Void) stays, Torch / Pickaxe (no sticks) go (%s)" % co[:4])
    one(ev(PK, {"a": "conly"}), "CRAFT Craftable only off")
    p_ = one(ev(PK, {"a": "cq", "@Q": "stick!!"}), "CRAFT search")
    K.check([str(x_) for x_ in pg.cshown if x_ is not None] == [R1] and str(pg.cquery) == "stick" and p_ is not None and sval(cmap(p_), "#SkyyInvCq.Value") == "stick",
            "CRAFT search: 'stick' (cleaned) finds the Stick recipe only, the box keeps the word")
    p_ = one(ev(PK, {"a": "cr", "SlotIndex": 0}), "CRAFT pick")
    cm = cmap(p_) if p_ else {}
    K.check(str(pg.csel) == R1 and sval(cm, "#SkyyInvCoN.Text") == "Ingredient Stick" and sval(cm, "#SkyyInvNq0.Text") == "7 / 1"
            and sval(cm, "#SkyyInvCrd.Text") == "Ready - you can make 7", "CRAFT detail: name, have / need (2 in the bag + 5 in the Void), Ready (%s %s %s)"
            % (sval(cm, "#SkyyInvCoN.Text"), sval(cm, "#SkyyInvNq0.Text"), sval(cm, "#SkyyInvCrd.Text")))
    one(ev(PK, {"a": "cqx"}), "CRAFT clear search")
    # x1: Pre -> pay -> Post -> give -> PlayerCraftEvent -> commit; the inventory pays first
    EVS[:] = []
    CALLS[:] = []
    p_ = one(ev(PK, {"a": "cx:1"}), "CRAFT x1")
    K.eq(EVS, ["Pre", "Post", "PlayerCraftEvent"], "CRAFT x1: the events in craftItem's order")
    K.eq([c_ for c_ in CALLS if c_[0] != "list"], [("pay", R1, 1), ("commit", "rc0")], "CRAFT x1: paid once, committed")
    K.check(E.count(PK, "Wood_Oak_Trunk") == 1 and VOID["Wood_Oak_Trunk"] == 5 and E.count(PK, "Ingredient_Stick") == 4,
            "CRAFT x1: the inventory paid first (trunk 2 -> 1, Void 5), 4 sticks given")
    K.eq(sval(cmap(p_), "#SkyyInvCrd.Text") if p_ else None, "Crafted 4 x Ingredient Stick", "CRAFT x1: the result line")
    CALLS[:] = []
    p_ = one(ev(PK, {"a": "cx:10"}), "CRAFT x10 with 6")
    K.check(("pay", R1, 6) in CALLS and E.count(PK, "Wood_Oak_Trunk") == 0 and VOID["Wood_Oak_Trunk"] == 0 and E.count(PK, "Ingredient_Stick") == 28
            and "only 6 of 10" in (sval(cmap(p_), "#SkyyInvCrd.Text") or ""), "CRAFT x10: 6 made (1 from the bag, 5 from the Void), says so")
    CALLS[:] = []
    EVS[:] = []
    p_ = one(ev(PK, {"a": "cx:1"}), "CRAFT nothing left")
    K.check(not [c_ for c_ in CALLS if c_[0] == "pay"] and EVS == [] and "Not enough materials" in (sval(cmap(p_), "#SkyyInvCrd.Text") or ""),
            "CRAFT nothing left: no event, no payment")
    put(PK, "storage", 3, ISc("Wood_Oak_Trunk", 1))
    CANCEL["Pre"] = True
    CALLS[:] = []
    p_ = one(ev(PK, {"a": "cx:1"}), "CRAFT Pre cancelled")
    K.check(not [c_ for c_ in CALLS if c_[0] == "pay"] and E.count(PK, "Wood_Oak_Trunk") == 1 and "refused - nothing was used" in (sval(cmap(p_), "#SkyyInvCrd.Text") or ""),
            "CRAFT Pre cancelled (SkyyGear's lifelong rule etc.): nothing paid, nothing given")
    CANCEL["Pre"], CANCEL["Post"] = False, True
    CALLS[:] = []
    p_ = one(ev(PK, {"a": "cx:1"}), "CRAFT Post cancelled")
    K.check([c_[0] for c_ in CALLS if c_[0] != "list"] == ["pay", "refund"] and E.count(PK, "Wood_Oak_Trunk") == 1 and E.count(PK, "Ingredient_Stick") == 28
            and "materials are back" in (sval(cmap(p_), "#SkyyInvCrd.Text") or ""), "CRAFT Post cancelled: paid, then refunded - nothing lost, nothing given")
    CANCEL["Post"] = False
    PAYFAIL[0] = True
    p_ = one(ev(PK, {"a": "cx:1"}), "CRAFT payment refused")
    K.check("Not crafted: not enough materials" in (sval(cmap(p_), "#SkyyInvCrd.Text") or "") and E.count(PK, "Ingredient_Stick") == 28,
            "CRAFT a refused payment: nothing given")
    PAYFAIL[0] = False
    put(PK, "storage", 4, ISc("Wood_Oak_Trunk", 2))
    CALLS[:] = []
    one(ev(PK, {"a": "cx:0"}), "CRAFT All")
    K.check(("pay", R1, 3) in CALLS and E.count(PK, "Wood_Oak_Trunk") == 0 and E.count(PK, "Ingredient_Stick") == 40, "CRAFT All: every craft the materials allow (3)")
    put(PK, "storage", 3, ISc("Wood_Oak_Trunk", 1))
    CALLS[:] = []
    one(ev(PK, {"a": "cx:1"}), "CRAFT double click 1")
    p_ = one(ev(PK, {"a": "cx:1"}), "CRAFT double click 2")
    K.check([c_[0] for c_ in CALLS if c_[0] == "pay"] == ["pay"] and E.count(PK, "Ingredient_Stick") == 44 and "Not enough" in (sval(cmap(p_), "#SkyyInvCrd.Text") or ""),
            "CRAFT double click: the second click finds nothing to pay with - no dupe")
    put(PK, "storage", 3, ISc("Wood_Oak_Trunk", 1))
    LIST.remove(R1)
    CALLS[:] = []
    p_ = one(ev(PK, {"a": "cx:1"}), "CRAFT recipe gone between draw and click")
    K.check(not [c_ for c_ in CALLS if c_[0] == "pay"] and E.count(PK, "Wood_Oak_Trunk") == 1 and pg.csel is None,
            "CRAFT a recipe that left the list: refused, nothing used, unselected (%s)" % (sval(cmap(p_), "#SkyyInvCrd.Text") if p_ else None))
    LIST.insert(0, R1)
    K.eq(int(IC_.amount(PK.pl, ramap.get(R1), 5, 1)), 1, "CRAFT amount: x1 = 1")
    K.eq(int(IC_.amount(PK.pl, ramap.get(R1), 5, 10)), 5, "CRAFT amount: x10 with 5 = 5")
    fit_ = int(IC_.fits(PK.pl, ramap.get(R1)))
    K.check(fit_ >= 1 and int(IC_.amount(PK.pl, ramap.get(R1), 5000, 0)) == min(999, fit_), "CRAFT All stops at what fits (%d)" % fit_)
    p_ = one(ev(PK, {"a": "cb:1"}), "CRAFT Weapon tab")
    K.check(str(pg.cbench) == "Weapon_Bench" and [str(x_) for x_ in pg.cshown if x_ is not None] == [R4], "CRAFT Weapon tab: its own recipes")
    p_ = one(ev(PK, {"a": "cb:2"}), "CRAFT Furnace tab")
    K.check(len(OPENED) == 1 and "Opening the Furnace" in cap_of(p_), "CRAFT Furnace tab: the pack's own Furnace page (sacks:fn:openFurnace)")
    p_ = one(ev(PK, {"a": "cb:3"}), "CRAFT Tanning tab")
    K.check("Tannery tab" in cap_of(p_), "CRAFT Tanning tab: the caption tells the player to pick the Tannery tab (%s)" % cap_of(p_))
    p_ = one(ev(PK, {"a": "cb:9"}), "CRAFT no such tab")
    K.check("No such bench" in cap_of(p_), "CRAFT a bench index out of range = a caption")
    # fixer: a Salvagebench recipe (Processing in vanilla, INSTANT in SkyySacks) gets its own tab; other Processing benches stay off
    R8 = recipe("Skyy_Test_Salvage", [("Rock_Stone", 1)], "Ingredient_Stick", 1, "Salvagebench", "Processing")
    K.eq(str(IC_.benchKey(ramap.get(R8))), "Salvagebench", "CRAFT benchKey: the Salvagebench (instant) = its own tab")
    K.check(IC_.benchKey(ramap.get(R7)) is None, "CRAFT benchKey: the Furnace (timed) = no grid tab (its own page)")
    K.eq(str(IC_.benchLabel("Salvagebench")), "Salvage", "CRAFT the Salvage tab label")
    LIST.append(R8)
    p_ = one(ev(PK, {"a": "cb:0"}), "CRAFT redraw with a Salvage recipe")
    bts_ = [sval(cmap(p_), "#SkyyInvBt%d.Text" % k_) for k_ in range(6)] if p_ else []
    K.check("Salvage" in bts_ and "Furnace" in bts_ and "Tanning" in bts_, "CRAFT tabs with a Salvage recipe: %s" % bts_)
    if "Salvage" in bts_:
        one(ev(PK, {"a": "cb:%d" % bts_.index("Salvage")}), "CRAFT Salvage tab")
        K.eq([str(x_) for x_ in pg.cshown if x_ is not None], [R8], "CRAFT Salvage tab: its recipe is reachable (nothing lost)")
    LIST.remove(R8)
    # fixer: a recipe with no output stacks hands out nothing = -1 (craftVoid refunds, never commits a paid craft with nothing given)
    R9 = recipe("Skyy_Test_Empty", [("Rock_Stone", 1)], "Ingredient_Stick", 1, "Fieldcraft")
    E.jf(CRRc.class_, "outputs").set(ramap.get(R9), _JA(MQc)([]))
    E.jf(CRRc.class_, "primaryOutput").set(ramap.get(R9), None)
    g_ = None
    try:
        g_ = int(IC_.give(PK.ref, PK.st, PK.pl, ramap.get(R9), 1))
    except Exception as x_:
        K.notes.append("give() on an empty recipe threw (craftVoid treats a throw as -1 too): %s" % x_)
        g_ = -1
    K.eq(g_, -1, "CRAFT give(): nothing handed out = -1 (refund, not commit)")
    ramap.remove(R9)
    # the side panels
    p_ = one(ev(PK, {"a": "cb:0"}), "CRAFT back to Crafting")
    cm = cmap(p_) if p_ else {}
    K.check(sval(cm, "#SkyyInvPetN.Text") == "Wolf" and sval(cm, "#SkyyInvPetL.Text") == "Lv 42  Legendary" and sval(cm, "#SkyyInvMntN.Text") == "No mount"
            and "Skyy_PetIcon_Wolf_Legendary" in cm.get("#SkyyInvPetI.Slots", ""), "SIDE pet + mount cards from pets:fn:hud")
    K.check(sval(cm, "#SkyyInvVcN.Text") == "2 equipped" and "Skyy_Talisman_Speed_T1" in cm.get("#SkyyInvVc.Slots", ""), "SIDE Void Charms (acc:has + acc:tal, no doubles)")
    K.check(sval(cm, "#SkyyInvSk0.Text") == "Mining  12" and sval(cm, "#SkyyInvSk1.Text") == "Farming  5" and sval(cm, "#SkyyInvSk2.Text") == "",
            "SIDE skills (%s %s)" % (sval(cm, "#SkyyInvSk0.Text"), sval(cm, "#SkyyInvSk1.Text")))
    K.check("Island" in cm.get("#SkyyInvTp.Slots", "") and "Hub" in cm.get("#SkyyInvTp.Slots", ""), "SIDE the teleport mini hotbar: Island + Hub")
    K.check((sval(cm, "#SkyyInvNrT0.Text") or "").startswith("Quest: Talk to the Farmer") and pg.nowT is not None and str(pg.nowT[0]) == "world:quests"
            and "#SkyyInvNrB0" in [b_[1] for b_ in binds_of(p_)], "SIDE Right now: the quest row with its Go button (%s)" % sval(cm, "#SkyyInvNrT0.Text"))
    ev(PK, {"a": "now:0"})
    K.notes.append("SIDE Right now Go -> page %s" % (None if PK.pm.getCustomPage() is None else PK.pm.getCustomPage().getClass().getSimpleName()))
    E.pump(PK)
    if PK.pm.getCustomPage() is not None and PK.pm.getCustomPage() != pg:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    if PK.pm.getCustomPage() != pg:
        pg = ST.openPage(PK.ref, PK.st, PK.pr, "test")
        E.pump(PK)
    l0 = int(E.CM.lines.size())
    pg.handleDataEvent(PK.ref, PK.st, json.dumps({"a": "tp", "SlotIndex": 0}))
    K.check(bool(pg.closed) and [str(E.CM.lines.get(i_)) for i_ in range(l0, int(E.CM.lines.size()))] == ["island"],
            "SIDE teleport Island: the page closes, /island runs as the player")
    # the totals: exactly what was crafted (11 trunks paid -> 44 sticks; 1 trunk left; nothing else moved)
    K.eq((E.count(PK, "Wood_Oak_Trunk"), VOID["Wood_Oak_Trunk"], E.count(PK, "Ingredient_Stick"), E.count(PK, "Rock_Stone"), E.count(PK, "Ingredient_Bar_Iron")),
         (1, 0, 44, 3, 3), "CRAFT totals: every trunk paid made exactly 4 sticks; nothing else moved")
    K.check(len([e_ for e_ in REC.values() if e_[2] == "open"]) == 0, "CRAFT every receipt was committed or refunded")
    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
    for k_ in SACKS:
        BR.remove(k_)
    IC_.WARNED = False
    K.check(not bool(IC_.voidMode()), "PLAIN: no craft bridges = the plain mode")
    al_ = IC_.allowed(PK.pr.getUuid(), PK.pl)
    K.check(al_ is not None, "PLAIN: the vanilla pocket list (CraftingPlugin.getBenchRecipes) read without a throw (%d here)" % int(al_.size()))
    h_ = IC_.have(None, PK.pl, ramap.get(R1))
    K.notes.append("PLAIN have(): %s" % (None if h_ is None else [str(x_) for x_ in h_]))
    K.eq(str(IC_.craftPlain(PK.ref, PK.st, PK.pl, ramap.get(R1), 1)), "Crafting is not ready here - nothing was used",
         "PLAIN: no CraftingManager on the stand-in = refused, nothing used (in game: craftItem)")
    IC_.FIRE = None
    K.notes.append("CRAFT counters: crafts %d refused %d refunds %d events %d give-fallback %d" % (int(IC_.CRAFTS), int(IC_.REFUSED), int(IC_.REFUNDS),
                   int(IC_.EVENTS), int(IC_.FALLBACK)))
    E.pump(PK)

'''

# ======================================================================= the HARNESS (derived from the 0.3.51 harness: every 0.3.51 check
# kept except the Craft-button pass (the button is gone; the PASS route itself is still checked on the real wrapper) -> CRAFT 0.3.52
assert T.has('VERSION = "0.3.51"\nJAR') and T.has("""pg.handleDataEvent(PI.ref, PI.st, '{"a":"craft"}')""")
T.rep('''"""Harness for SkyyMenu 0.3.51 (the Craft client-crash fix: the server never opens the vanilla screen; tools/menu_0_3_51_patch.py).
GENERATED by tools/menu_0_3_51_patch.py from the 0.3.50 harness (edit the patch, not this file): every 0.3.50 check runs again on the
0.3.51 jar except the server-opened vanilla screen ones (OFF race, CREATIVE, CRAFT), which are replaced by the 0.3.51 checks. Build first:
    python tools/menu_0_3_51_patch.py && python SkyyMenu/build_skyymenu_0.3.51.py
    python SkyyMenu/test_skyymenu_0.3.51.py [--dir <folder inside tools/dev/scratch/>] [--keep]
''', '''"""Harness for SkyyMenu 0.3.52 (OUR OWN CRAFTING inside the inventory + the v5 layout; tools/menu_0_3_52_patch.py).
GENERATED by tools/menu_0_3_52_patch.py from the 0.3.51 harness (edit the patch, not this file): every 0.3.51 check runs again on the
0.3.52 jar (the Tab hook, the client-crash rules, moves, drops, creative, the pass-through) except the Craft-button pass (the button is
gone), which becomes the 0.3.52 CRAFT phase below. Build first:
    python tools/menu_0_3_52_patch.py && python SkyyMenu/build_skyymenu_0.3.52.py
    python SkyyMenu/test_skyymenu_0.3.52.py [--dir <folder inside tools/dev/scratch/>] [--keep]
  0.3.52 CRAFT (EXECUTED on the stand-ins with SkyySacks' craft bridges as Python stubs that pay inventory FIRST, then the Void):
       the bench tabs (Crafting / Weapon / Furnace / Tanning), charm + pet egg + processing recipes left out, every pocket recipe reachable
       over the pages, tier-then-name order, Craftable only, search, the detail (have / need, Ready), Craft x1 (Pre -> pay -> Post -> give
       -> PlayerCraftEvent -> commit), x10 with fewer materials, nothing left, Pre cancelled (nothing paid), Post cancelled (refunded), a
       refused payment, All, a double click (no dupe), a recipe that left the list between draw and click, the Weapon / Furnace / Tanning
       tabs, the side panels (pet / mount, charms, skills, teleports, Right now + Go), the teleport click, the plain mode (no SkyySacks),
       every grid copy metadata-free, item totals exactly as crafted
''')
T.rep('VERSION = "0.3.51"\nJAR', 'VERSION = "0.3.52"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.50.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.51.jar")\nJAR50 = os.path.join(HERE, "SkyyMenu-0.3.50.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.50.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.51.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_51_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_52_patch.py")')
T.rep('"scratch", "inv2", "menu"', '"scratch", "inv3", "menu"')
T.rep(cut(T.s, 'ADDED = ["InvMode"]', 'if "--expect-dump" in sys.argv:'), HARNESS_EXPECT)
T.rep('''    K.check(g.count('VERSION = "0.3.51"') == 1, "S VERSION")
    K.check(g.count("registerSystem(") == o.count("registerSystem(") + 1 and g.count("registerSystem(new @PKG@.InvMode())") == 1,
            "S ONE new registerSystem: InvMode (one per class)")''', '''    K.check(g.count('VERSION = "0.3.52"') == 1, "S VERSION")
    K.check(g.count("registerSystem(") == o.count("registerSystem(") and g.count("registerSystem(new @PKG@.InvMode())") == 1,
            "S no new registerSystem (InvMode stays the only inventory system)")''')
T.rep('''    K.eq(_bad(zo), ["com/skyy/menu/InvState.class"], "S ... (the scan works: 0.3.50's InvState had both)")''',
      '''    K.eq(_bad(zipfile.ZipFile(JAR50)), ["com/skyy/menu/InvState.class"], "S ... (the scan works: 0.3.50's InvState had both)")
    # 0.3.52: our own crafting - the engine's craft steps are referenced, the server still never opens a crafting window
    _ic = zn.read("com/skyy/menu/InvCraft.class")
    K.check(all(x_ in _ic for x_ in (b"CraftRecipeEvent$Pre", b"CraftRecipeEvent$Post", b"PlayerCraftEvent", b"sacks:fn:craftPay", b"sacks:fn:craftRefund",
                                     b"sacks:fn:craftCommit", b"getContainerForItemPickup", b"addOrDropItemStack", b"craftItem", b"getBenchRecipes")),
            "S InvCraft references craftItem's steps (Pre / Post / PlayerCraftEvent, giveOutput's container pick + addOrDrop), the pay / refund / commit bridges")
    K.check(not [n for n in zn.namelist() if n.endswith(".class") and (b"CraftingWindow" in zn.read(n) or b"openWindow" in zn.read(n))],
            "S no crafting window is ever opened by the server")''')
T.rep('''    m = re.search(r'^IV_TABS = (\\[.*?\\])\\s+# \\(label', g, re.M | re.S)
    tabs = eval(m.group(1)) if m else []
    K.eq([t[0] for t in tabs], ["Inventory", "Skills", "Class", "Pets", "Collections", "Storage", "Upgrade", "Market", "Quests", "World",
                                "Social", "Settings"], "S the 12 top tabs (plan section 3 + v4 Upgrade)")''',
      '''    m = re.search(r'^IV_TABS = (\\[.*?\\])\\n', g, re.M | re.S)
    tabs = eval(m.group(1)) if m else []
    K.eq([t[0] for t in tabs], ["Inventory", "Skills", "Pets", "Market", "World", "Social", "Settings"], "S the 7 approved top tabs (popup 11-14 'Yes, both')")
    me = re.search(r"IV_ELEMENTS <= (\\d+)", g)
    K.check(me is not None and int(me.group(1)) <= 700, "S the page's element budget assert is <= 700 (the ~1,600 client budget)")''')
T.rep('''    K.check("#SkyyInvCfA.Text" in cm and "vanilla crafting screen" in (sval(cm, "#SkyyInvCfB.Text") or ""), "PAGE: the crafting placeholder texts")
    bl = binds_of(pk[0]) if pk else []
    K.eq(len(bl), 17 + 2 * 4 + 1, "PAGE: 26 bindings (12 tabs + X + Craft + Sort + 2 panel buttons, 2 grids x 4 slot events, the drop zone)")''',
      '''    K.check(all(k_ in cm for k_ in ("#SkyyInvCg.Slots", "#SkyyInvCo.Slots", "#SkyyInvCn.Slots", "#SkyyInvCfOnly.Text", "#SkyyInvCi.Text",
                                    "#SkyyInvVc.Slots", "#SkyyInvTp.Slots", "#SkyyInvPetI.Slots", "#SkyyInvMntI.Slots", "#SkyyInvSk0.Text")),
            "PAGE (0.3.52): the craft panel, charms, teleports, pet / mount and skills are filled")
    K.check("Crafting" == sval(cm, "#SkyyInvBt0.Text") and "#SkyyInvBt1.Text" not in cm, "PAGE (0.3.52): no SkyySacks here = the plain pocket mode, one bench tab (Crafting)")
    K.eq(sval(cm, "#SkyyInvCrd.Text"), "Pick a recipe on the left to see what it needs.", "PAGE (0.3.52): the detail asks for a pick")
    K.check("Crafting - Tab" not in "".join(str(c_.text or "") for c_ in cmds_of(pk[0])), "PAGE (0.3.52): the 'Crafting - Tab' placeholder is gone")
    bl = binds_of(pk[0]) if pk else []
    K.eq(len(bl), 7 + 15 + 2 * 4 + 1 + 5 + 2 + 1, "PAGE: 39 bindings (7 tabs + 15 buttons, 2 grids x 4 slot events, the drop zone, 5 click grids, "
                                                    "the search field + button, 1 bench tab)")''')
T.rep(cut(T.s, "    # ---- CRAFT (0.3.51; TEST 284", "    # ---- TABS: the other 11 open the hub pages\n", keep_end=False), HARNESS_CRAFT + "    # ---- TABS: the other 6 open the hub pages\n")
T.rep('''    pg.handleDataEvent(PI.ref, PI.st, '{"a":"tab:11"}')''', '''    pg.handleDataEvent(PI.ref, PI.st, '{"a":"tab:6"}')''')
T.rep('''    p_ = one(ev(PI, {"a": "tab:7"}), "TABS Market (no market mod here)")''', '''    p_ = one(ev(PI, {"a": "tab:3"}), "TABS Market (no market mod here)")''')
for _w in ('{"a":"craft"}', "Press Tab to open crafting", "0.3.49.jar"):
    assert _w not in T.s, "0.3.52 harness: still there: " + _w
if T.dst:
    T.finish()
