"""Derive SkyyUiProbe/build_skyyuiprobe_0.10.py + test_skyyuiprobe_0.10.py from the 0.9 SET pin (0.9 is left untouched; CRLF kept).
Run:  python tools/uiprobe_0_10_patch.py   then   python SkyyUiProbe/build_skyyuiprobe_0.10.py   (never --deploy)
Check: python SkyyUiProbe/test_skyyuiprobe_0.10.py [--keep] [--old-jar <the 0.9 jar>]

0.10 = phase P0 of research/Inventory-Screen-Plan.md (sections 2, 5, 6, 7): a probe proving our own Tab-replacing inventory page can show
and move REAL inventory items. Skyy's words (docs/answered/ui.md): "lets do our own version of that. but before we do, we need a full plan
on how to work everything in right."; popup 'Should the Tab key open the new SkyWynn screen instead of the vanilla inventory?' ->
"Yes, with off switch"; wrap-up 'Start step 1: check the CORE mod and build the test page?' -> "Yes, start step 1".

EVERY 0.9 case stays as it is. New, op only (the same skyyuiprobe.admin node, no permission groups):
  /uiprobe inv          I1 the probe inventory page: storage 9 x 4 + hotbar 9 + armour 4 + utility 4 with your REAL items (server-drawn
                        Slots, metadata stripped), a tab row [Inventory][Probe Bag], Sort, Close, a key-hint line, a full-screen drop
                        zone behind the window (drag outside = drop). Every action logs ONE line '[SkyyUiProbe] inv <action> <from> -> <to>
                        ok/fail' (drag, merge, swap, split, shift, drop-outside, sort, bag-return) + the raw client event data.
  /uiprobe tab on|off   I2 per player, in memory only, default OFF, never saved: while ON, Tab (ClientOpenWindow PocketCrafting) opens
                        the I1 page instead of the vanilla screen; Tab again / Esc close it; the orphan CloseWindow 0 is absorbed; the
                        log names the hook that caught it (subhandler / adapter). OFF = vanilla Tab untouched. Only for the op who set it.
  Probe Bag tab         I3 an 18-slot in-memory SimpleItemContainer drawn by the server; drag / shift-click in and out. ITEM SAFETY: on page
                        close (Esc, Tab, Close, another page), disconnect, world change, plugin shutdown and probe off, every item in the
                        bag goes back to the player's inventory (storage first, then hotbar; overflow dropped at the feet; if even that
                        fails it is kept in memory and given back at the next join / world change / page open), each one logged.
                        A click that arrives after the page closed is ignored; the same move reported twice is done once.
  I4 metadata safety    rolled gear (ItemDisplayMetadata) shows its name + description from the metadata on a metadata-free grid copy.
No Server Setup rows, no saved data, no migrations (a probe).

METHOD (learnt from CORE - Custom Inventory by SupremoSama, source CC0 1.0 = public domain; credited in the Java comments; nothing of
theirs is shipped - no texture, no .ui, no file):
  * Tab = ClientOpenWindow(WindowType.PocketCrafting). PacketAdapters inbound filters run on the dedicated (Netty) transport only, so the
    primary catch is a SubPacketHandler registered with ServerManager.registerSubPacketHandlers(Function): its registerHandlers() runs at
    the END of GamePacketHandler.registerHandlers (after the native handlers), reads the game's own Consumer for ClientOpenWindow /
    CloseWindow from GenericPacketHandler.handlers (reflection: handleClientOpenWindow is protected, so CORE re-implemented it - reading
    the native consumer keeps the game's exact world-thread hop + checks) and wraps it; DropItemStack / SmartMoveItemStack / MoveItemStack
    are wrapped the same way (observed, then passed to the consumer that was there - the game's InventoryPacketHandler or another mod's
    wrapper, never cut off; fixer 2026-11-14). Hooks apply to connections made after setup(); the inbound
    PlayerPacketFilter covers the others (skipped for hooked connections so nothing routes twice). Route = packet thread, no ECS: the
    work is queued on the player's world (World.execute).
  * After our page replaces the vanilla window the client may send CloseWindow id 0 - absorbed (the server's window 0 is closed if one
    exists), never used to dismiss our page.
  * FIXER 2026-11-14 (critics): CloseWindow 0 absorbed only while the page is open or within 5 s of the Tab redirect; the game's drop is
    count-checked on the next world tick ('inv drop-check'); bag returns at disconnect / shutdown run inline when already on the world
    thread, and the bag is logged first ('inv bag-hold') so a lost return shows; the drop zone gets CORE's RenderItemQualityBackground
    false + Padding 0; a SkyyProfiles epoch change while the bag holds items is WARNed (items go to the current profile - probe limit).
  * FIXER 2 2026-11-14: a native Move / SmartMove that arrives within 1.5 s AFTER our server move is WARNed 'AFTER a server move -
    possible undo' and counted as a fail (shows the client's order; no behaviour change). The disconnect bag return is proven to run
    before the engine removes the player: Universe.removePlayer dispatches PlayerDisconnectEvent synchronously, THEN queues the removal
    with CompletableFuture.runAsync(.., world); World.execute = Deque.offer, consumeTaskQueue = poll (FIFO); World.onShutdown drains the
    queue before PlayerRef.removeFromStore (bytecode-checked in the harness). Death: the engine opens RespawnPage (openCustomPage ->
    our onDismiss returns the bag); no item is made or deleted either way, but bag items may escape the death drop (probe limit, steps).
  * Grids: ItemGrid + InventorySectionId (InventoryComponent.STORAGE / HOTBAR / ARMOR / UTILITY_SECTION_ID) + AreItemsDraggable, and the
    server sends every grid's Slots: ItemGridSlot of stack.withMetadata((BsonDocument) null) (metadata stripped, durability kept - CORE's
    InventoryDisplay; HANDOFF section 2: no metadata in a grid slot) + setName / setDescription from ItemDisplayMetadata (children joined)
    + setActivatable(true). The bag grid has no section id (server-drawn).
  * Moves: SlotClicking (pick up) / Dropped (drop: the client adds SlotIndex + SourceInventorySectionId / SourceSlotId / ItemStackId /
    ItemStackQuantity to our EventData {"a","g"}) / SlotClickReleaseWhileDragging (shift release = quick move; a release on another slot =
    the drop, as CORE) / SlotDoubleClicking / DragCancelled, all bound with locksInterface false; the move runs on the world thread
    through ItemContainer.moveItemStackFromSlotToSlot (the engine's own move: merge, swap, part stacks; harness-checked) or
    moveItemStackFromSlot(slot, containers[]) for shift; every move counts the item totals before / after (a mismatch logs COUNT
    CHANGED). Drag outside onto the drop zone: inventory sections are handed to the game's own drop (new InventoryPacketHandler(handler)
    .handle(new DropItemStack(...)) - CORE's InventoryOperations.drop), the bag drops through ItemUtils.dropItem (null = refused = the
    stack goes back). Container change events (registerChangeEvent, off-thread / batched) queue ONE refresh on the world thread, which
    re-sends the grids only when their contents differ from the last packet. No hover event is bound (no hover updates).
  * One answer per event (HANDOFF section 2): a rebuild (tab switch), one sendUpdate (grids + caption), the close, or the safety net.

ENGINE FACTS read for this round (HytaleServer.jar 0.7.6, tools/dev/reflect.py + bcfull.py, 2026-11-14; build-time asserted):
  GenericPacketHandler.handlers (Consumer[]) / registerHandler / getSubPacketHandler; GamePacketHandler.registerHandlers registers the
  natives then packetHandlers.forEach(registerHandlers); ServerManager.registerSubPacketHandlers adds to subPacketHandlers (no removal:
  the wrappers pass through once InvState.ACTIVE is false); WindowType.PocketCrafting; CloseWindow.id; ItemContainer
  moveItemStackFromSlotToSlot = merge (stack cap), swap (whole stack onto another item), refuses a part stack onto another item;
  removeItemStackFromSlot(slot) succeeds on an empty slot too (so the bag claims a stack by getOutput(), never by succeeded());
  ItemUtils.dropItem -> throwItem returns null when the DropItemEvent is cancelled or the stack invalid; PageManager.setPage /
  openCustomPage tear the old page down (onDismiss); PlayerDisconnectEvent.getPlayerRef (network thread, before the entity leaves);
  PlayerReadyEvent (every world switch, world thread).
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D = os.path.join(ROOT, "SkyyUiProbe")


def load(name):
    b = open(os.path.join(D, name), "rb").read()
    assert b.count(b"\r\n") == b.count(b"\n"), name + ": expected CRLF only"
    return b.decode("utf-8").replace("\r\n", "\n")


def save(name, s):
    assert "\r" not in s
    with open(os.path.join(D, name), "wb") as f:
        f.write(s.replace("\n", "\r\n").encode("utf-8"))
    print("wrote", os.path.join("SkyyUiProbe", name))


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, "anchor found %d times (want %d): %r" % (c, n, old[:120])
    return s.replace(old, new)


# ===================================================================================================== the build script
S = load("build_skyyuiprobe_0.9.py")
S = rep(S, '"""SkyyUiProbe 0.9 - build script', '"""SkyyUiProbe 0.10 - build script')
S = rep(S, "Run:   python SkyyUiProbe/build_skyyuiprobe_0.9.py    -> SkyyUiProbe/SkyyUiProbe-0.9.jar (no --deploy on purpose)",
        "Run:   python SkyyUiProbe/build_skyyuiprobe_0.10.py   -> SkyyUiProbe/SkyyUiProbe-0.10.jar (no --deploy on purpose)")
S = rep(S, "Check: python SkyyUiProbe/test_skyyuiprobe_0.9.py   (J jar,", "Check: python SkyyUiProbe/test_skyyuiprobe_0.10.py  (J jar,")
S = rep(S, "0.9 (tools/uiprobe_0_9_patch.py - read its header for the engine facts): + the PRICE-TOOLTIP",
        """0.10 (tools/uiprobe_0_10_patch.py - read its header for the method + engine facts): + the INVENTORY PROBE P0 of
research/Inventory-Screen-Plan.md, every 0.9 case kept. Op only: /uiprobe inv (I1: the probe inventory page with your REAL items - storage,
hotbar, armour, utility grids filled by the server, metadata stripped; drag / merge / swap / split / shift / drag outside = drop / Sort;
a Probe Bag tab = an 18-slot in-memory bag, I3), /uiprobe tab on|off (I2: Tab opens that page instead of the vanilla inventory, for you
only, in memory). Every action logs '[SkyyUiProbe] inv <action> <from> -> <to> ok/fail'. Method after SupremoSama CustomInventory (CC0).

0.9 (tools/uiprobe_0_9_patch.py - read its header for the engine facts): + the PRICE-TOOLTIP""")
S = rep(S, 'VERSION = "0.9"', 'VERSION = "0.10"')

# ---- 3b. the two inventory page data files (built with the kit; inserted after the case pages, before the dev-preview dump)
INV_PY = r'''
# ================================================================= 3b. 0.10 INVENTORY PROBE PAGES (research/Inventory-Screen-Plan.md P0)
# Two page data files: inv (storage + hotbar + armour + utility) and invbag (+ the 18-slot Probe Bag above storage). The root is a
# TRANSPARENT 1600 x 980 Group (the D1 pattern) holding a full-size drop zone ItemGrid behind the window (drag an item outside the window
# = drop it; method after SupremoSama CustomInventory (CC0)) and the decorated window placed at Left / Top. Grids are filled at run time
# (InvPage.build: InventorySectionId + Slots), never here. The page bindings below are the 4 buttons; the grid events are bound in Java.
INV_W, INV_H = 960, 880
INV_L, INV_T = (PAGE_W - INV_W) // 2, (PAGE_H - INV_H) // 2
INV_CLEAR = ship("Clear", SM.Pic(8, 8), folder="SkyyUiProbe/Inv/")      # a transparent slot background for the drop zone
INV_GRIDS = [("s", P + "Is", -2, 9, 4, "Storage"), ("h", P + "Ih", -1, 9, 1, "Hotbar 1-9"), ("a", P + "Ia", -3, 1, 4, "Armour"),
             ("u", P + "Iu", -5, 1, 4, "Utility"), ("b", P + "Ib", None, 9, 2, "Probe Bag")]
INV_COL_W = SUI.GRID_SLOT + 2 * SUI.GRID_WELL_PAD
INV_MAIN_H = 616
INV_BAG_TEXT = "Probe Bag - 18 slots in server memory - every item goes back to your inventory when this page closes"
INV_HINTS = ["Drag = move or swap  -  drop on the same item = merge  -  Shift + click = quick move  -  right-drag = half a stack",
             "1-9 over an item = to that hotbar slot  -  Q over an item = drop it  -  drag outside the window = drop it  -  Sort = sort storage"]
INV_BINDS = [("#" + P + "ItI", "tinv"), ("#" + P + "ItB", "tbag"), ("#" + P + "ISo", "sort"), ("#" + P + "Close", "close")]
# the unproven tokens these pages may carry: the drop zone's own probe question (InfoDisplay / the inline SlotBackground)
INV_PROBE_TOKENS = {"SlotBackground", "InfoDisplay", "Visible", "Border", "TexturePath", "RenderItemQualityBackground", "Padding"}  # + CORE drop-zone tokens


def inv_page(bag):
    ap = SUI.Appends()
    ap.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); }" % (P, PAGE_W, PAGE_H)))
    ap.append(("#" + P, 'ItemGrid #%sDz { Anchor: (Left: 0, Top: 0, Width: %d, Height: %d); SlotsPerRow: 1; AreItemsDraggable: false; '
                        'InfoDisplay: None; RenderItemQualityBackground: false; Padding: 0; '
                        'Style: (SlotSize: %d, SlotIconSize: 1, SlotSpacing: 0, SlotBackground: "%s"); }'
               % (P, PAGE_W, PAGE_H, PAGE_W, INV_CLEAR)))
    sh = SUI.page_shell(P + "Iv", INV_W, INV_H, "SkyyUiProbe %s - inventory probe P0" % VERSION, kind="decorated")
    root0 = sh.appends[0]
    assert root0[0] is None and root0[1] == "Group #%sIv { Anchor: (Width: %d, Height: %d); }" % (P, INV_W, INV_H), root0
    sh.appends[0] = ("#" + P, "Group #%sIv { Anchor: (Left: %d, Top: %d, Width: %d, Height: %d); }" % (P, INV_L, INV_T, INV_W, INV_H))
    for item_ in sh.appends:
        ap.append(item_)
    ap.sets.extend(sh.appends.sets)
    ap.sets.extend(sh.sets)
    body, iw = "#" + sh.body, sh.inner_w
    tr = P + "Tr"
    ap.append((body, SUI.group(tr, layout="Left", w=iw, h=NAV_H)))
    ap.append(("#" + tr, SUI.button(P + "ItI", "Inventory", "secondary" if bag else "primary", "small", w=180, anchor={"right": 8})))
    ap.append(("#" + tr, SUI.button(P + "ItB", "Probe Bag", "primary" if bag else "secondary", "small", w=180, anchor={"right": 16})))
    ap.text("#" + tr, P + "TrL", "Your real items - op only - inventory probe P0", "gold", size=14, h=SUI.BTN_SMALL_H, w=iw - 180 - 8 - 180 - 16)
    ap.text(body, P + "TCap", "Waiting for your move", "caption", size=15, h=26, w=iw)
    mr = P + "Mr"
    ap.append((body, SUI.group(mr, layout="Left", w=iw, h=INV_MAIN_H)))
    for _g, gid, _sec, cols, rows, lab in INV_GRIDS[2:4]:
        col = gid + "C"
        ap.append(("#" + mr, SUI.group(col, layout="Top", w=INV_COL_W, h=INV_MAIN_H, anchor={"right": 12})))
        ap.text("#" + col, gid + "L", lab, "strong", size=14, h=22, w=INV_COL_W)
        ap.append(("#" + col, SUI.item_grid(gid, cols, rows, drag=True)))
    rw = iw - 2 * (INV_COL_W + 12) - 12
    rc = P + "Rc"
    ap.append(("#" + mr, SUI.spacer(w=12)))
    ap.append(("#" + mr, SUI.group(rc, layout="Top", w=rw, h=INV_MAIN_H)))
    gd = dict((x[0], x) for x in INV_GRIDS)
    for g in (["b"] if bag else []) + ["s", "h"]:
        _g, gid, _sec, cols, rows, lab = gd[g]
        ap.text("#" + rc, gid + "L", INV_BAG_TEXT if g == "b" else lab, "gold" if g == "b" else "strong", size=14, h=22, w=rw)
        ap.append(("#" + rc, SUI.item_grid(gid, cols, rows, drag=True)))
    for i, h_ in enumerate(INV_HINTS):
        ap.text(body, P + "Hk%d" % i, h_, "caption", size=14, h=22, w=iw)
    br = P + "Br"
    ap.append((body, SUI.group(br, layout="Left", w=iw, h=NAV_H)))
    ap.append(("#" + br, SUI.button(P + "ISo", "Sort", "secondary", "small", w=140, anchor={"right": 8})))
    ap.append(("#" + br, SUI.button(P + "Close", "Close", "secondary", "small", w=140, sound="cancel")))
    used = NAV_H + 26 + INV_MAIN_H + 22 * len(INV_HINTS) + NAV_H
    assert used <= sh.inner_h, (used, sh.inner_h)
    well = lambda r: r * SUI.GRID_SLOT + (r - 1) * SUI.GRID_SPACING + 2 * SUI.GRID_WELL_PAD
    need = (22 + well(2) if bag else 0) + 22 + well(4) + 22 + well(1)
    assert need <= INV_MAIN_H and 22 + well(4) <= INV_MAIN_H, need
    assert 9 * SUI.GRID_SLOT + 8 * SUI.GRID_SPACING + 2 * SUI.GRID_WELL_PAD <= rw, rw
    return ap


INV_PAGES = {}
for _key, _bag in (("inv", False), ("invbag", True)):
    ap = inv_page(_bag)
    for _p, mk in ap:
        SUI.check_markup(mk, prefix=P, root=(_p is None), kit_paths=False)
    SUI.check_page(ap, P)
    SUI.assert_page_size(PAGE_W, PAGE_H)
    toks = SUI.proven_tokens(ap)
    unproven = sorted(k for k, g in toks.items() if g == "unknown" or (g is not None and "base" not in g and not all(x in SUI.PROBED for x in g)))
    assert set(unproven) <= INV_PROBE_TOKENS, (_key, unproven)
    ids = set(i for _p, mk in ap for i in SUI._static_ids(mk))
    for sel, act in INV_BINDS:
        assert sel[1:] in ids, (_key, sel)
    for _g, gid, _sec, _c, _r, _l in INV_GRIDS:
        assert (gid in ids) == (_g != "b" or _bag), (_key, gid)
    assert P + "Dz" in ids and P + "TCap" in ids
    for _p, mk in ap:                                              # every texture path = a kit texture or one this jar ships
        for m in re.finditer(r'(?:Background|TexturePath|SlotBackground): *"([^"]+\.png)"', mk):
            pth = m.group(1)
            assert pth in set(SUI.TEX.values()) or (pth.startswith("SkyyUiProbe/") and TEX_ROOT + pth[:-4] + "@2x.png" in ASSETS), (_key, pth)
    lines = []
    for _p, mk in ap:
        mk_ = SUI.render(mk)
        assert "\t" not in mk_ and "\n" not in mk_
        lines.append("A\t%s\t%s" % ("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p), mk_))
    for ident, prop, val in ap.sets:
        assert isinstance(val, str) and not SUI.has_j(val) and "\t" not in val and "\n" not in val, (ident, prop, val)
        lines.append("S\t#%s.%s\t%s" % (SUI.render(ident).lstrip("#"), prop, val))
    for sel, act in INV_BINDS:
        lines.append("E\t%s\t%s" % (sel, act))
    text = "\n".join(lines) + "\n"
    INV_PAGES[_key] = dict(elements=count_elements(ap), appends=len(ap), sets=len(ap.sets), binds=len(INV_BINDS), ids=sorted(ids),
                           unproven=unproven, bytes=len(text.encode("utf-8")))
    assert INV_PAGES[_key]["elements"] <= 1600, (_key, INV_PAGES[_key]["elements"])
    ASSETS[RES_DIR + _key + ".txt"] = text.encode("utf-8")
    print("page %-6s inventory probe   %5d elements, %4d appends, %3d b.set, %3d bindings (+ the grid events in Java)%s" % (
        _key, INV_PAGES[_key]["elements"], INV_PAGES[_key]["appends"], INV_PAGES[_key]["sets"], INV_PAGES[_key]["binds"],
        ("  unproven: " + ", ".join(unproven)) if unproven else ""))
DUMP["inv"] = {"pages": INV_PAGES, "grids": [list(x) for x in INV_GRIDS], "binds": [a for _s, a in INV_BINDS], "clear": INV_CLEAR,
               "assets": sorted(ASSETS)}
DUMP["assets"] = sorted(ASSETS)
'''
S = rep(S, '\nif "--assets-out" in sys.argv:               # dev preview', INV_PY + '\nif "--assets-out" in sys.argv:               # dev preview')

# ---- tokens + build-time engine checks for the inventory probe
INV_T = r'''
# 0.10 inventory probe: the engine classes (tools/uiprobe_0_10_patch.py header) - every member is probed below
T.update({
    "SM2": "com.hypixel.hytale.server.core.io.ServerManager",
    "SPH": "com.hypixel.hytale.server.core.io.handlers.SubPacketHandler",
    "IPH": "com.hypixel.hytale.server.core.io.handlers.IPacketHandler",
    "GPH": "com.hypixel.hytale.server.core.io.handlers.game.GamePacketHandler",
    "GEN": "com.hypixel.hytale.server.core.io.handlers.GenericPacketHandler",
    "INVPH": "com.hypixel.hytale.server.core.io.handlers.game.InventoryPacketHandler",
    "PAD": "com.hypixel.hytale.server.core.io.adapter.PacketAdapters",
    "PPF": "com.hypixel.hytale.server.core.io.adapter.PlayerPacketFilter",
    "PFI": "com.hypixel.hytale.server.core.io.adapter.PacketFilter",
    "PKT": "com.hypixel.hytale.protocol.Packet",
    "COW": "com.hypixel.hytale.protocol.packets.window.ClientOpenWindow",
    "CW": "com.hypixel.hytale.protocol.packets.window.CloseWindow",
    "WT": "com.hypixel.hytale.protocol.packets.window.WindowType",
    "DIS": "com.hypixel.hytale.protocol.packets.inventory.DropItemStack",
    "SMIS": "com.hypixel.hytale.protocol.packets.inventory.SmartMoveItemStack",
    "MIS": "com.hypixel.hytale.protocol.packets.inventory.MoveItemStack",
    "WM": "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager",
    "PMG": "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager",
    "SIC": "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
    "SRT": "com.hypixel.hytale.server.core.inventory.container.SortType",
    "IGS": "com.hypixel.hytale.server.core.ui.ItemGridSlot",
    "EVR": "com.hypixel.hytale.event.EventRegistration",
    "EREG": "com.hypixel.hytale.event.EventRegistry",
    "PDE": "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "PRE": "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "IU": "com.hypixel.hytale.server.core.entity.ItemUtils",
    "STX": "com.hypixel.hytale.server.core.inventory.transaction.SlotTransaction",
    "MTX": "com.hypixel.hytale.server.core.inventory.transaction.MoveTransaction",
    "LTX": "com.hypixel.hytale.server.core.inventory.transaction.ListTransaction",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "BSON": "org.bson.BsonDocument",
})
'''
S = rep(S, '\nfor c, m in ((T["JP"], "getLogger"),', INV_T + '\nfor c, m in ((T["JP"], "getLogger"),')

INV_PROBES = r'''
# 0.10 inventory probe: every engine member it calls (B.probe = public, inherited included) + the facts it stands on (patch header)
for c, m in ((T["SM2"], "get"), (T["SM2"], "registerSubPacketHandlers"), (T["SPH"], "registerHandlers"), (T["IPH"], "getPlayerRef"),
             (T["GEN"], "registerHandler"), (T["GEN"], "getSubPacketHandler"), (T["GPH"], "getPlayerRef"), (T["INVPH"], "handle"),
             (T["PAD"], "registerInbound"), (T["PAD"], "deregisterInbound"), (T["PPF"], "test"),
             (T["COW"], "PACKET_ID"), (T["COW"], "type"), (T["CW"], "PACKET_ID"), (T["CW"], "id"), (T["WT"], "PocketCrafting"),
             (T["DIS"], "PACKET_ID"), (T["DIS"], "inventorySectionId"), (T["DIS"], "slotId"), (T["DIS"], "quantity"),
             (T["SMIS"], "PACKET_ID"), (T["SMIS"], "fromSectionId"), (T["SMIS"], "fromSlotId"), (T["SMIS"], "quantity"), (T["SMIS"], "moveType"),
             (T["MIS"], "PACKET_ID"), (T["MIS"], "fromSectionId"), (T["MIS"], "fromSlotId"), (T["MIS"], "toSectionId"), (T["MIS"], "toSlotId"),
             (T["MIS"], "quantity"), (T["PLA"], "getWindowManager"), (T["PLA"], "getInventory"), (T["WM"], "getWindow"), (T["WM"], "closeWindow"),
             (T["PMG"], "getCustomPage"), (T["PMG"], "openCustomPage"), (T["PR"], "getPacketHandler"),
             (T["IC"], "moveItemStackFromSlotToSlot"), (T["IC"], "moveItemStackFromSlot"), (T["IC"], "removeItemStackFromSlot"),
             (T["IC"], "sortItems"), (T["IC"], "registerChangeEvent"), (T["IC"], "addItemStack"), (T["INV"], "getSectionById"),
             (T["SRT"], "TYPE"), (T["IGS"], "setItemStack"), (T["IGS"], "setName"), (T["IGS"], "setDescription"), (T["IGS"], "setActivatable"),
             (T["IS"], "withQuantity"), (T["IS"], "getFromMetadataOrNull"), (T["IS"], "getMetadata"), (T["IDM"], "getName"), (T["IDM"], "getDescription"),
             (T["MSG"], "getRawText"), (T["MSG"], "getChildren"), (T["MSG"], "getMessageId"), (T["EVR"], "unregister"),
             (T["PDE"], "getPlayerRef"), (T["PRE"], "getPlayerRef"), (T["IU"], "dropItem"), (T["STX"], "getOutput"), (T["MTX"], "succeeded"),
             (T["LTX"], "succeeded"), (T["INVC"], "STORAGE_SECTION_ID"), (T["INVC"], "HOTBAR_SECTION_ID"), (T["INVC"], "ARMOR_SECTION_ID"),
             (T["INVC"], "UTILITY_SECTION_ID"), (T["BT"], "SlotClicking"), (T["BT"], "Dropped"), (T["BT"], "SlotClickReleaseWhileDragging"),
             (T["BT"], "SlotDoubleClicking"), (T["BT"], "DragCancelled"), (T["EVD"], "append"), (T["JP"], "getEventRegistry"),
             (T["EREG"], "registerGlobal"), (T["PAGE"], "rebuild"), (T["REF"], "isValid"), (T["WLD"], "isInThread")):
    B.probe(pool, c, m)
_gen_handlers = [f_ for f_ in pool.get(T["GEN"]).getDeclaredFields() if str(f_.getName()) == "handlers"]
assert len(_gen_handlers) == 1 and str(_gen_handlers[0].getType().getName()) == "java.util.function.Consumer[]", "GenericPacketHandler.handlers (Consumer[]) changed"
_hcow = [m_ for m_ in pool.get(T["GPH"]).getDeclaredMethods() if str(m_.getName()) == "handleClientOpenWindow"]
from jpype import JClass as _JC
assert len(_hcow) == 1 and _JC("javassist.Modifier").isProtected(_hcow[0].getModifiers()), "GamePacketHandler.handleClientOpenWindow is no longer protected (the hook could call it directly now)"
assert "(SILcom/hypixel/hytale/server/core/inventory/container/ItemContainer;S)Lcom/hypixel/hytale/server/core/inventory/transaction/MoveTransaction;" in _sig(T["IC"], "moveItemStackFromSlotToSlot"), "ItemContainer.moveItemStackFromSlotToSlot(short, int, ItemContainer, short) changed"
assert "(S[Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;)Lcom/hypixel/hytale/server/core/inventory/transaction/ListTransaction;" in _sig(T["IC"], "moveItemStackFromSlot"), "ItemContainer.moveItemStackFromSlot(short, ItemContainer[]) changed"
assert "(SI)Lcom/hypixel/hytale/server/core/inventory/transaction/ItemStackSlotTransaction;" in _sig(T["IC"], "removeItemStackFromSlot"), "removeItemStackFromSlot(short, int) changed"
assert "(S)Lcom/hypixel/hytale/server/core/inventory/transaction/SlotTransaction;" in _sig(T["IC"], "removeItemStackFromSlot"), "removeItemStackFromSlot(short) changed"
assert "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/inventory/ItemStack;Lcom/hypixel/hytale/component/ComponentAccessor;)Lcom/hypixel/hytale/component/Ref;" in _sig(T["IU"], "dropItem"), "ItemUtils.dropItem changed"
assert "(Ljava/util/function/Function;)V" in _sig(T["SM2"], "registerSubPacketHandlers"), "ServerManager.registerSubPacketHandlers(Function) changed"
assert "(Lcom/hypixel/hytale/server/core/io/adapter/PlayerPacketFilter;)Lcom/hypixel/hytale/server/core/io/adapter/PacketFilter;" in _sig(T["PAD"], "registerInbound"), "PacketAdapters.registerInbound(PlayerPacketFilter) changed"
assert "(Lcom/hypixel/hytale/component/Ref;ILcom/hypixel/hytale/component/ComponentAccessor;)Lcom/hypixel/hytale/server/core/entity/entities/player/windows/Window;" in _sig(T["WM"], "closeWindow"), "WindowManager.closeWindow changed"
assert "(Lcom/hypixel/hytale/server/core/io/handlers/IPacketHandler;)V" in _ctors(T["INVPH"]), "InventoryPacketHandler(IPacketHandler) changed"
assert "(III)V" in _ctors(T["DIS"]), "DropItemStack(int, int, int) changed"
assert "(S)V" in _ctors(T["SIC"]), "SimpleItemContainer(short) changed"
assert sorted(str(x.getName()) for x in pool.get(T["COW"]).getFields() if str(x.getName()) == "type") == ["type"], "ClientOpenWindow.type changed"
'''
S = rep(S, "\n\ndef _cp_strings(cls):", INV_PROBES + "\n\ndef _cp_strings(cls):")

# ---- the Java classes (before ProbeCmds, which calls InvCmds)
INV_JAVA = r'''
# ================================================================= 0.10 INVENTORY PROBE (research/Inventory-Screen-Plan.md P0) - Java
# Method after SupremoSama CustomInventory (CC0 1.0, public domain): Tab = ClientOpenWindow(PocketCrafting) caught by a transport-
# independent sub-packet handler (the game's own consumer for that packet id, wrapped) + a PacketAdapters inbound filter for connections
# the hook missed; the orphan CloseWindow 0 is absorbed; ItemGrids carry InventorySectionId and the server sends every grid's Slots
# (metadata stripped); a drag answers with a server-side move through the container API. Learnt, not copied: no file of theirs.
ist = mk("InvState")
ipg = mk("InvPage", T["PAGE"])
itk = mk("InvTask", None, "java.lang.Runnable")
irf = mk("InvRefresh", None, "java.lang.Runnable")
icl = mk("InvClose", None, "java.lang.Runnable")
ich = mk("InvChange", None, "java.util.function.Consumer")
ihk = mk("InvHooks", None, T["SPH"])
ihf = mk("InvHookFactory", None, "java.util.function.Function")
iwr = mk("InvWrap", None, "java.util.function.Consumer")
ifl = mk("InvFilter", None, T["PPF"])
ibye = mk("InvBye", None, "java.util.function.Consumer")
irdy = mk("InvReady", None, "java.util.function.Consumer")
icm = mk("InvCmds")
INV_CLASSES = [ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, icm]

# ---- InvState: per-player switches + the open pages (memory only), the hook bookkeeping, the safe give / drop helpers
for _f in ("public static java.util.concurrent.ConcurrentHashMap TAB = new java.util.concurrent.ConcurrentHashMap();",       # uuid -> TRUE: Tab on
           "public static java.util.concurrent.ConcurrentHashMap REDIR = new java.util.concurrent.ConcurrentHashMap();",     # uuid -> Long: when the last Tab redirect happened
           "public static java.util.concurrent.ConcurrentHashMap PAGES = new java.util.concurrent.ConcurrentHashMap();",     # uuid -> the open InvPage
           "public static java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();",   # uuid -> ArrayList of stacks to give back
           "public static java.util.concurrent.ConcurrentHashMap LASTNATIVE = new java.util.concurrent.ConcurrentHashMap();",  # uuid -> Long: last native move packet
           "public static java.util.Map HOOKED = java.util.Collections.synchronizedMap(new java.util.WeakHashMap());",       # hooked packet handlers
           "public static volatile boolean ACTIVE = false;", "public static volatile boolean INSTALLED = false;",
           "public static Object FILTER = null;", "public static volatile int SUB = 0;", "public static volatile int ADP = 0;",
           "public static volatile int ORPH = 0;", "public static volatile int NATIVE = 0;", "public static volatile int INSTALLS = 0;",
           "public static java.util.function.Function DROPPER = null;",                                                      # harness only: records drops
           "public static java.util.List DROPPED = java.util.Collections.synchronizedList(new java.util.ArrayList());"):
    F(ist, _f)
for _f in ("public String view;", "public @SIC@ bag;", "public volatile boolean closed;", "public boolean answered;", "public int answers;",
           "public int nets;", "public int builds;", "public int refreshes;", "public java.util.ArrayList regs;", "public @REF@ pref;",
           "public @ST@ pst;", "public String dg;", "public int ds;", "public String di;", "public boolean dshift;", "public String via;",
           "public int moves;", "public int fails;", "public String lastSig;", "public java.util.concurrent.atomic.AtomicBoolean queued;",
           "public String tcap;", "public String lastMove;", "public long lastMoveAt;", "public String epoch0;"):
    F(ipg, _f)
F(itk, "public int kind;")
F(itk, "public @PR@ pr;")
F(itk, "public String via;")
F(itk, "public @PKG@.InvPage pg;")
F(itk, "public String sid;")
F(itk, "public int n0;")
F(irf, "public @PKG@.InvPage pg;")
F(icl, "public @PKG@.InvPage pg;")
F(icl, "public String why;")
F(ich, "public @PKG@.InvPage pg;")
F(ihk, "public @IPH@ ph;")
F(iwr, "public @GPH@ g;")
F(iwr, "public java.util.function.Consumer nat;")
F(iwr, "public @INVPH@ ih;")
F(iwr, "public int kind;")
C(itk, "public InvTask(int kind, @PR@ pr, String via) { this.kind = kind; this.pr = pr; this.via = via; }")
C(irf, "public InvRefresh(@PKG@.InvPage pg) { this.pg = pg; }")
C(icl, "public InvClose(@PKG@.InvPage pg, String why) { this.pg = pg; this.why = why; }")
C(ich, "public InvChange(@PKG@.InvPage pg) { this.pg = pg; }")
C(ihk, "public InvHooks(@IPH@ ph) { this.ph = ph; }")
C(ihf, "public InvHookFactory() { }")
C(iwr, "public InvWrap(@GPH@ g, java.util.function.Consumer nat, @INVPH@ ih, int kind) { this.g = g; this.nat = nat; this.ih = ih; this.kind = kind; }")
C(ifl, "public InvFilter() { }")
C(ibye, "public InvBye() { }")
C(irdy, "public InvReady() { }")
C(ipg, r"""
public InvPage(@PR@ pr, String via) {
  super(pr, @LIFE@.CanDismiss);
  this.via = via;
  this.view = "inv";
  this.bag = new @SIC@((short) 18);
  this.closed = false;
  this.regs = new java.util.ArrayList();
  this.dg = null;
  this.ds = -1;
  this.di = null;
  this.lastSig = "";
  this.tcap = "";
  this.queued = new java.util.concurrent.atomic.AtomicBoolean(false);
  this.lastMove = "";
  this.lastMoveAt = 0L;
}""")

M(ist, r"""
public static boolean on(java.util.UUID u) { return u != null && TAB.containsKey(u); }""")
M(ist, r"""
public static String pkt(Object p) {
  if (p instanceof @COW@) return "ClientOpenWindow " + ((@COW@) p).type;
  if (p instanceof @CW@) return "CloseWindow " + ((@CW@) p).id;
  if (p instanceof @DIS@) { @DIS@ d = (@DIS@) p; return "DropItemStack section " + d.inventorySectionId + " slot " + d.slotId + " x" + d.quantity; }
  if (p instanceof @SMIS@) { @SMIS@ s = (@SMIS@) p; return "SmartMoveItemStack section " + s.fromSectionId + " slot " + s.fromSlotId + " x" + s.quantity + " " + s.moveType; }
  if (p instanceof @MIS@) { @MIS@ m = (@MIS@) p; return "MoveItemStack " + m.fromSectionId + ":" + m.fromSlotId + " -> " + m.toSectionId + ":" + m.toSlotId + " x" + m.quantity; }
  return p == null ? "null" : p.getClass().getSimpleName();
}""")
M(ist, r"""
public static boolean queue(@PR@ pr, Runnable r) {
  try {
    if (pr == null) return false;
    @REF@ ref = pr.getReference();
    if (ref == null || !ref.isValid()) return false;
    @ST@ st = ref.getStore();
    @WLD@ w = ((@ES@) st.getExternalData()).getWorld();
    if (w == null) return false;
    w.execute(r);
    return true;
  } catch (Throwable t) { @PKG@.ProbeLog.warn("inv: could not queue on the world thread: " + t); return false; }
}""")
M(ist, r"""
public static boolean now(@PR@ pr, Runnable r) {
  try {
    if (pr == null) return false;
    @REF@ ref = pr.getReference();
    if (ref == null || !ref.isValid()) return false;
    @WLD@ w = ((@ES@) ref.getStore().getExternalData()).getWorld();
    if (w != null && w.isInThread()) { r.run(); return true; }
  } catch (Throwable t) { @PKG@.ProbeLog.warn("inv: the world-thread check failed: " + t); }
  return queue(pr, r);
}""")
M(ist, r"""
public static void hooked(Object h) { if (h != null) HOOKED.put(h, Boolean.TRUE); }""")
M(ist, r"""
public static boolean isHooked(Object h) { return h != null && HOOKED.containsKey(h); }""")
# the game's own consumer for a packet id (GenericPacketHandler.handlers, private): our wrapper calls it for every packet it does not take
M(ist, r"""
public static java.util.function.Consumer nativeOf(@GEN@ g, int id) {
  try {
    java.lang.reflect.Field f = @GEN@.class.getDeclaredField("handlers");
    f.setAccessible(true);
    java.util.function.Consumer[] a = (java.util.function.Consumer[]) f.get(g);
    if (a == null || id < 0 || id >= a.length) return null;
    return a[id];
  } catch (Throwable t) { @PKG@.ProbeLog.warn("inv hooks: cannot read the game's packet handler table: " + t); return null; }
}""")
M(ist, r"""
public static synchronized void pend(java.util.UUID u, @IS@ s) {
  if (u == null || s == null || s.isEmpty()) return;
  java.util.ArrayList l = (java.util.ArrayList) PENDING.get(u);
  if (l == null) { l = new java.util.ArrayList(); PENDING.put(u, l); }
  l.add(s);
}""")
M(ist, r"""
public static synchronized java.util.ArrayList takePending(java.util.UUID u) {
  if (u == null) return null;
  return (java.util.ArrayList) PENDING.remove(u);
}""")
M(ist, r"""
public static String epoch(java.util.UUID u) {
  try {
    Object b = System.getProperties().get("skyy.bridge");
    if (u == null || !(b instanceof java.util.Map)) return "";
    Object v = ((java.util.Map) b).get("profile:epoch:" + u.toString());
    return v == null ? "" : String.valueOf(v);
  } catch (Throwable t) { return ""; }
}""")
M(ist, r"""
public static String it(@IS@ s) { return (s == null || s.isEmpty()) ? "empty" : s.getItemId() + " x" + s.getQuantity(); }""")
# add a stack to a container; returns what did NOT fit (null = all of it). Counted before / after, whatever the transaction says.
M(ist, r"""
public static @IS@ addTo(@IC@ c, @IS@ s) {
  if (c == null || s == null || s.isEmpty()) return s;
  String id = s.getItemId();
  int q = s.getQuantity();
  int before = @PKG@.Tips.count(c, id);
  try { c.addItemStack(s); } catch (Throwable t) { }
  int added = @PKG@.Tips.count(c, id) - before;
  if (added <= 0) return s;
  if (added >= q) return null;
  return s.withQuantity(q - added);
}""")
M(ist, r"""
public static boolean drop(@REF@ ref, @ST@ st, @IS@ s) {
  if (s == null || s.isEmpty()) return true;
  try {
    boolean ok = false;
    if (DROPPER != null) { Object r = DROPPER.apply(s); ok = (r instanceof Boolean) && ((Boolean) r).booleanValue(); }
    else ok = @IU@.dropItem(ref, s, (@CAC@) st) != null;
    if (ok) DROPPED.add(it(s));
    return ok;
  } catch (Throwable t) { @PKG@.ProbeLog.warn("inv: dropping " + it(s) + " at your feet failed: " + t); return false; }
}""")
# give a stack back: storage first, then hotbar, then the feet; if even that fails it is KEPT in memory for the next join / world / open
M(ist, r"""
public static String give(@REF@ ref, @ST@ st, @PR@ pr, @IS@ s) {
  if (s == null || s.isEmpty()) return "nothing";
  @IS@ rem = s;
  String where = "";
  try {
    @PLA@ p = (ref == null || st == null) ? null : (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    @INV@ inv = p == null ? null : p.getInventory();
    if (inv != null) {
      @IS@ r1 = addTo(inv.getStorage(), rem);
      if (r1 == null || r1.getQuantity() < rem.getQuantity()) where = "storage";
      rem = r1;
      if (rem != null && !rem.isEmpty()) {
        @IS@ r2 = addTo(inv.getHotbar(), rem);
        if (r2 == null || r2.getQuantity() < rem.getQuantity()) where = where.length() == 0 ? "hotbar" : where + " + hotbar";
        rem = r2;
      }
    }
  } catch (Throwable t) { @PKG@.ProbeLog.warn("inv: giving " + it(s) + " back failed: " + t); }
  if (rem != null && !rem.isEmpty()) {
    if (ref != null && st != null && drop(ref, st, rem)) where = where.length() == 0 ? "your feet (inventory full)" : where + " + your feet (inventory full)";
    else {
      pend(pr == null ? null : pr.getUuid(), rem);
      where = (where.length() == 0 ? "" : where + " + ") + "KEPT in memory for your next join (" + it(rem) + ")";
    }
  }
  return where;
}""")
M(ist, r"""
public static int deliver(@REF@ ref, @ST@ st, @PR@ pr) {
  if (pr == null) return 0;
  java.util.ArrayList l = takePending(pr.getUuid());
  if (l == null || l.isEmpty()) return 0;
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    @IS@ s = (@IS@) l.get(i);
    String w = give(ref, st, pr, s);
    @PKG@.ProbeLog.info("inv bag-return kept " + it(s) + " -> " + w + " ok (kept items delivered)");
    n = n + 1;
  }
  @PKG@.ProbeLog.chat(pr, "Probe Bag: " + n + " kept stack(s) went back to you now.");
  return n;
}""")

# ---- InvPage: the probe inventory page (I1 / I3 / I4)
M(ipg, r"""
public @PR@ who() { return this.playerRef; }""")
M(ipg, r"""
public static String sel(String g) {
  if ("s".equals(g)) return "#@PFX@Is";
  if ("h".equals(g)) return "#@PFX@Ih";
  if ("a".equals(g)) return "#@PFX@Ia";
  if ("u".equals(g)) return "#@PFX@Iu";
  if ("b".equals(g)) return "#@PFX@Ib";
  return null;
}""")
M(ipg, r"""
public static int sectionOf(String g) {
  if ("s".equals(g)) return @INVC@.STORAGE_SECTION_ID;
  if ("h".equals(g)) return @INVC@.HOTBAR_SECTION_ID;
  if ("a".equals(g)) return @INVC@.ARMOR_SECTION_ID;
  if ("u".equals(g)) return @INVC@.UTILITY_SECTION_ID;
  return 0;
}""")
M(ipg, r"""
public static String gridOf(int sec) {
  if (sec == @INVC@.STORAGE_SECTION_ID) return "s";
  if (sec == @INVC@.HOTBAR_SECTION_ID) return "h";
  if (sec == @INVC@.ARMOR_SECTION_ID) return "a";
  if (sec == @INVC@.UTILITY_SECTION_ID) return "u";
  return null;
}""")
M(ipg, r"""
public static String gname(String g) {
  if ("s".equals(g)) return "storage";
  if ("h".equals(g)) return "hotbar";
  if ("a".equals(g)) return "armour";
  if ("u".equals(g)) return "utility";
  if ("b".equals(g)) return "Probe Bag";
  return "?";
}""")
M(ipg, r"""
public String[] shown() {
  if ("bag".equals(this.view)) return new String[] { "s", "h", "a", "u", "b" };
  return new String[] { "s", "h", "a", "u" };
}""")
M(ipg, r"""
public @IC@ cont(String g) {
  if (g == null) return null;
  if (g.equals("b")) return this.bag;
  int sec = sectionOf(g);
  if (sec == 0 || this.pref == null || this.pst == null) return null;
  @PLA@ p = (@PLA@) this.pst.getComponent(this.pref, @PLA@.getComponentType());
  if (p == null || p.getInventory() == null) return null;
  return p.getInventory().getSectionById(sec);
}""")
M(ipg, r"""
public static String flat(@MSG@ m) {
  if (m == null) return "";
  StringBuilder sb = new StringBuilder();
  java.util.ArrayList stack = new java.util.ArrayList();
  stack.add(m);
  int guard = 0;
  while (!stack.isEmpty() && guard < 400) {
    guard = guard + 1;
    @MSG@ x = (@MSG@) stack.remove(stack.size() - 1);
    if (x == null) continue;
    String r = x.getRawText();
    java.util.List c = x.getChildren();
    if (r != null) sb.append(r);
    else if (x.getMessageId() != null && (c == null || c.isEmpty())) sb.append("[").append(x.getMessageId()).append("]");
    if (c != null) for (int i = c.size() - 1; i >= 0; i--) stack.add(c.get(i));
  }
  return sb.toString();
}""")
# I4: the grid copy carries NO metadata (CORE InventoryDisplay: withMetadata(null)); the name / description come from ItemDisplayMetadata
M(ipg, r"""
public static @IGS@ slot(@IS@ s) {
  @IGS@ g = new @IGS@();
  g.setActivatable(true);
  if (s == null || s.isEmpty()) return g;
  g.setItemStack(s.withMetadata((@BSON@) null));
  try {
    Object o = s.getFromMetadataOrNull(@IDM@.KEYED_CODEC);
    if (o != null) {
      @IDM@ d = (@IDM@) o;
      String n = flat(d.getName());
      String de = flat(d.getDescription());
      if (n.length() > 0) g.setName(n);
      if (de.length() > 0) g.setDescription(de);
    }
  } catch (Throwable t) { }
  return g;
}""")
M(ipg, r"""
public java.util.ArrayList slots(String g) {
  java.util.ArrayList l = new java.util.ArrayList();
  @IC@ c = cont(g);
  if (c == null) return l;
  int n = c.getCapacity();
  for (int i = 0; i < n; i++) l.add(slot(c.getItemStack((short) i)));
  return l;
}""")
M(ipg, r"""
public String sig() {
  StringBuilder sb = new StringBuilder();
  String[] gs = shown();
  for (int k = 0; k < gs.length; k++) {
    @IC@ c = cont(gs[k]);
    sb.append(gs[k]).append(':');
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s == null || s.isEmpty()) sb.append('-');
      else sb.append(s.getItemId()).append('x').append(s.getQuantity()).append(s.getMetadata() == null ? "" : "m" + s.getMetadata().hashCode());
      sb.append(',');
    }
  }
  return sb.toString();
}""")
M(ipg, r"""
public void putAll(@UCB@ b) {
  String[] gs = shown();
  for (int k = 0; k < gs.length; k++) b.set(sel(gs[k]) + ".Slots", slots(gs[k]));
  this.lastSig = sig();
}""")
M(ipg, r"""
public int total(String id) {
  if (id == null) return 0;
  int n = 0;
  String[] gs = new String[] { "s", "h", "a", "u" };
  for (int k = 0; k < gs.length; k++) n = n + @PKG@.Tips.count(cont(gs[k]), id);
  return n + @PKG@.Tips.count(this.bag, id);
}""")
M(ipg, r"""
public int bagCount() {
  int n = 0;
  for (int i = 0; i < this.bag.getCapacity(); i++) { @IS@ s = this.bag.getItemStack((short) i); if (s != null && !s.isEmpty()) n = n + 1; }
  return n;
}""")
# the raw client event data: {"a":..,"g":..} + what the client adds (SlotIndex, SourceInventorySectionId, SourceSlotId, ItemStackId, ...)
M(ipg, r"""
public static String val(String d, String k) {
  if (d == null || k == null) return null;
  String q = "\"" + k + "\"";
  int i = d.indexOf(q);
  if (i < 0) return null;
  int c = d.indexOf(':', i + q.length());
  if (c < 0) return null;
  int j = c + 1;
  while (j < d.length() && (d.charAt(j) == ' ' || d.charAt(j) == '\t' || d.charAt(j) == '\n' || d.charAt(j) == '\r')) j = j + 1;
  if (j >= d.length()) return null;
  if (d.charAt(j) == '"') {
    StringBuilder sb = new StringBuilder();
    int e = j + 1;
    while (e < d.length() && d.charAt(e) != '"') {
      if (d.charAt(e) == '\\' && e + 1 < d.length()) e = e + 1;
      sb.append(d.charAt(e));
      e = e + 1;
    }
    return sb.toString();
  }
  int e2 = j;
  while (e2 < d.length() && d.charAt(e2) != ',' && d.charAt(e2) != '}') e2 = e2 + 1;
  String v = d.substring(j, e2).trim();
  if (v.length() == 0 || v.equals("null")) return null;
  return v;
}""")
M(ipg, r"""
public static int ival(String d, String k, int def) {
  String v = val(d, k);
  if (v == null) return def;
  try { return Integer.parseInt(v); } catch (Throwable t) { }
  try { return (int) Double.parseDouble(v); } catch (Throwable t) { }
  return def;
}""")
M(ipg, r"""
public static boolean bval(String d, String k) { return "true".equalsIgnoreCase(val(d, k)); }""")
M(ipg, r"""
public static String cut(String d) { return d == null ? "" : (d.length() > 400 ? d.substring(0, 400) + "..." : d); }""")
M(ipg, r"""
public String logmv(String act, String from, String to, boolean ok, String why) {
  if (ok) this.moves = this.moves + 1; else this.fails = this.fails + 1;
  String w = why == null ? "" : why;
  @PKG@.ProbeLog.info("inv " + act + " " + from + " -> " + to + " " + (ok ? "ok" : "fail") + w);
  return (ok ? "OK - " : "FAIL - ") + act + " " + from + " -> " + to + w;
}""")
M(ipg, r"""
public String move(String sg, int ss, String tg, int ts, int q, String expect) {
  @IC@ sc = cont(sg);
  @IC@ tc = cont(tg);
  String from = sg + ":" + ss;
  String to = tg + ":" + ts;
  if (sc == null || tc == null) return logmv("drag", from, to, false, " (that grid is not on this page)");
  if (ss < 0 || ss >= sc.getCapacity() || ts < 0 || ts >= tc.getCapacity()) return logmv("drag", from, to, false, " (slot out of range)");
  @IS@ s = sc.getItemStack((short) ss);
  if (s == null || s.isEmpty()) return logmv("drag", from, to, false, " (the source slot is empty now - nothing moved)");
  String sid = s.getItemId();
  if (expect != null && expect.length() > 0 && !expect.equals(sid)) return logmv("drag", from + " " + sid, to, false, " (the client held " + expect + " - the slot changed, nothing moved)");
  int have = s.getQuantity();
  if (q <= 0 || q > have) q = have;
  if (sc == tc && ss == ts) return logmv("drag", from + " " + sid + " x" + q, to, true, " (same slot - nothing to do)");
  @IS@ t = tc.getItemStack((short) ts);
  String tid = (t == null || t.isEmpty()) ? null : t.getItemId();
  String act = tid == null ? (q < have ? "split" : "drag") : (tid.equals(sid) ? "merge" : "swap");
  int a0 = total(sid);
  int b0 = tid == null ? 0 : total(tid);
  boolean ok = false;
  String why = "";
  try {
    @MTX@ tx = sc.moveItemStackFromSlotToSlot((short) ss, q, tc, (short) ts);
    ok = tx != null && tx.succeeded();
  } catch (Throwable e) { ok = false; why = " (" + e + ")"; }
  if (!ok && why.length() == 0) why = (act.equals("swap") && q < have) ? " (part of a stack cannot swap with another item - nothing moved)" : " (the game refused the move - a slot rule? nothing moved)";
  int a1 = total(sid);
  int b1 = tid == null ? 0 : total(tid);
  if (a0 != a1 || b0 != b1) {
    @PKG@.ProbeLog.warn("inv COUNT CHANGED on " + act + " " + from + " -> " + to + ": " + sid + " " + a0 + " -> " + a1 + (tid == null ? "" : ", " + tid + " " + b0 + " -> " + b1));
    ok = false;
    why = why + " COUNT CHANGED";
  }
  if (ok) why = " (" + gname(tg) + " slot " + (ts + 1) + " now " + @PKG@.InvState.it(tc.getItemStack((short) ts)) + ")";
  return logmv(act, from + " " + sid + " x" + q, to, ok, why);
}""")
M(ipg, r"""
public @IC@[] quickTargets(String g) {
  if (g.equals("b")) return new @IC@[] { cont("s"), cont("h") };
  if ("bag".equals(this.view)) return new @IC@[] { this.bag };
  if (g.equals("s")) return new @IC@[] { cont("h") };
  if (g.equals("h")) return new @IC@[] { cont("s") };
  return new @IC@[] { cont("s"), cont("h") };
}""")
M(ipg, r"""
public String quick(String g, int si) {
  @IC@ sc = cont(g);
  String from = g + ":" + si;
  String to = g.equals("b") ? "s+h" : ("bag".equals(this.view) ? "b" : (g.equals("s") ? "h" : (g.equals("h") ? "s" : "s+h")));
  if (sc == null || si < 0 || si >= sc.getCapacity()) return logmv("shift", from, to, false, " (no such slot)");
  @IS@ s = sc.getItemStack((short) si);
  if (s == null || s.isEmpty()) return logmv("shift", from, to, false, " (the slot is empty - nothing moved)");
  @IC@[] tg = quickTargets(g);
  for (int i = 0; i < tg.length; i++) if (tg[i] == null) return logmv("shift", from, to, false, " (no target grid)");
  String sid = s.getItemId();
  int q = s.getQuantity();
  int a0 = total(sid);
  boolean ok = false;
  String why = "";
  try {
    @LTX@ tx = sc.moveItemStackFromSlot((short) si, tg);
    ok = tx != null && tx.succeeded();
  } catch (Throwable e) { why = " (" + e + ")"; }
  @IS@ left = sc.getItemStack((short) si);
  int moved = q - ((left == null || left.isEmpty() || !sid.equals(left.getItemId())) ? 0 : left.getQuantity());
  if (moved <= 0) ok = false;
  if (!ok && why.length() == 0) why = " (no room - nothing moved)";
  int a1 = total(sid);
  if (a0 != a1) {
    @PKG@.ProbeLog.warn("inv COUNT CHANGED on shift " + from + ": " + sid + " " + a0 + " -> " + a1);
    ok = false;
    why = why + " COUNT CHANGED";
  }
  if (ok) why = " (" + moved + " of " + q + " moved)";
  return logmv("shift", from + " " + sid + " x" + q, to, ok, why);
}""")
M(ipg, r"""
public void dropCheck(String sid, int n0, String from) {
  int n1 = total(sid);
  if (n1 < n0) @PKG@.ProbeLog.info("inv drop-check " + from + " " + sid + ": " + (n0 - n1) + " left your inventory - the game's drop ok");
  else {
    this.fails = this.fails + 1;
    @PKG@.ProbeLog.warn("inv drop-check " + from + " " + sid + ": nothing left your inventory - the game's own drop did NOT drop it (fail; no item lost)");
  }
}""")
M(ipg, r"""
public String dropOut(String sg, int ss, int q, String expect, @REF@ ref, @ST@ st) {
  @IC@ sc = cont(sg);
  String from = sg + ":" + ss;
  if (sc == null || ss < 0 || ss >= sc.getCapacity()) return logmv("drop-outside", from, "world", false, " (no such slot)");
  @IS@ s = sc.getItemStack((short) ss);
  if (s == null || s.isEmpty()) return logmv("drop-outside", from, "world", false, " (the slot is empty now - nothing dropped)");
  String sid = s.getItemId();
  if (expect != null && expect.length() > 0 && !expect.equals(sid)) return logmv("drop-outside", from + " " + sid, "world", false, " (the slot changed - nothing dropped)");
  int have = s.getQuantity();
  if (q <= 0 || q > have) q = have;
  int sec = sectionOf(sg);
  if (sec != 0) {
    Object h = this.playerRef.getPacketHandler();
    if (h instanceof @IPH@) {
      try {
        int n0 = total(sid);
        new @INVPH@((@IPH@) h).handle(new @DIS@(sec, ss, q));
        @PKG@.InvTask ck = new @PKG@.InvTask(3, this.playerRef, from);
        ck.pg = this;
        ck.sid = sid;
        ck.n0 = n0;
        if (!@PKG@.InvState.queue(this.playerRef, ck)) @PKG@.ProbeLog.info("inv drop-check could not be queued - look at the ground");
        return logmv("drop-outside", from + " " + sid + " x" + q, "world", true, " (handed to the game's own drop, like the Q key - CORE's way; an 'inv drop-check' line follows)");
      } catch (Throwable e) { @PKG@.ProbeLog.info("inv drop-outside: the game's own drop refused (" + e + ") - the probe drops it itself"); }
    }
  }
  int a0 = total(sid);
  @IS@ got = null;
  try {
    @STX@ tx = sc.removeItemStackFromSlot((short) ss, q);
    got = tx == null ? null : tx.getOutput();
  } catch (Throwable e) { got = null; }
  int a1 = total(sid);
  if (a1 == a0) return logmv("drop-outside", from + " " + sid + " x" + q, "world", false, " (the game would not take it out of the slot - nothing dropped)");
  if (got == null || got.isEmpty()) got = s.withQuantity(a0 - a1);
  if (a0 - a1 != got.getQuantity()) @PKG@.ProbeLog.warn("inv COUNT odd on drop-outside " + from + ": took " + (a0 - a1) + ", the transaction says " + got.getQuantity());
  if (@PKG@.InvState.drop(ref, st, got)) return logmv("drop-outside", from + " " + sid + " x" + got.getQuantity(), "world", true, " (dropped at your feet)");
  @IS@ back = @PKG@.InvState.addTo(sc, got);
  String w = (back == null || back.isEmpty()) ? gname(sg) : gname(sg) + " + " + @PKG@.InvState.give(ref, st, this.playerRef, back);
  return logmv("drop-outside", from + " " + sid + " x" + got.getQuantity(), "world", false, " (the drop failed - put back into " + w + ")");
}""")
M(ipg, r"""
public String sort() {
  @IC@ c = cont("s");
  if (c == null) return logmv("sort", "storage", "storage", false, " (no storage)");
  boolean ok = false;
  try { @LTX@ tx = c.sortItems(@SRT@.TYPE); ok = tx != null && tx.succeeded(); } catch (Throwable e) { ok = false; }
  return logmv("sort", "storage", "storage", ok, ok ? " (by type)" : " (the game refused)");
}""")
M(ipg, r"""
public void say(String cap) {
  @UCB@ ub = new @UCB@();
  this.tcap = cap == null ? "" : cap;
  ub.set("#@PFX@TCap.Text", this.tcap);
  this.answered = true;
  this.answers = this.answers + 1;
  this.sendUpdate(ub);
}""")
M(ipg, r"""
public void answer(String cap) {
  @UCB@ ub = new @UCB@();
  putAll(ub);
  this.tcap = cap == null ? "" : cap;
  ub.set("#@PFX@TCap.Text", this.tcap);
  this.answered = true;
  this.answers = this.answers + 1;
  this.sendUpdate(ub);
}""")
M(ipg, r"""
public void clearDrag() { this.dg = null; this.ds = -1; this.di = null; this.dshift = false; }""")
M(ipg, r"""
public boolean dup(String key) { return key.equals(this.lastMove) && System.currentTimeMillis() - this.lastMoveAt < 1500L; }""")
M(ipg, r"""
public void moved(String key) { this.lastMove = key; this.lastMoveAt = System.currentTimeMillis(); }""")
# a native Move / SmartMove packet the client sent a moment ago (InvState.route keeps its time): the game already moved the item
M(ipg, r"""
public boolean nativeRecent() {
  Long ln = (Long) @PKG@.InvState.LASTNATIVE.get(this.playerRef.getUuid());
  return ln != null && System.currentTimeMillis() - ln.longValue() < 1500L;
}""")
M(ipg, r"""
public void listen() {
  if (!this.regs.isEmpty()) return;
  String[] gs = new String[] { "s", "h", "a", "u", "b" };
  for (int k = 0; k < gs.length; k++) {
    @IC@ c = cont(gs[k]);
    if (c != null) { try { this.regs.add(c.registerChangeEvent(new @PKG@.InvChange(this))); } catch (Throwable t) { @PKG@.ProbeLog.warn("inv: no change listener on " + gname(gs[k]) + ": " + t); } }
  }
}""")
M(ipg, r"""
public void unlisten() {
  for (int i = 0; i < this.regs.size(); i++) { try { ((@EVR@) this.regs.get(i)).unregister(); } catch (Throwable t) { } }
  this.regs.clear();
}""")
# change events arrive off the world thread / batched: ONE refresh is queued; it sends only when the grids differ from the last packet
M(ipg, r"""
public void changed() {
  if (this.closed) return;
  if (!this.queued.compareAndSet(false, true)) return;
  if (!@PKG@.InvState.queue(this.playerRef, new @PKG@.InvRefresh(this))) this.queued.set(false);
}""")
M(ipg, r"""
public void refresh() {
  this.queued.set(false);
  if (this.closed || this.pref == null || this.pst == null) return;
  try {
    @PLA@ p = (@PLA@) this.pst.getComponent(this.pref, @PLA@.getComponentType());
    if (p == null || p.getPageManager().getCustomPage() != this) return;
    String s = sig();
    if (s.equals(this.lastSig)) return;
    @UCB@ ub = new @UCB@();
    putAll(ub);
    this.refreshes = this.refreshes + 1;
    this.sendUpdate(ub);
    @PKG@.ProbeLog.info("inv refresh: the items changed outside a click (pickup, Q key, a native move) - ONE update re-sent the grids");
  } catch (Throwable t) { @PKG@.ProbeLog.warn("inv refresh failed: " + t); }
}""")
# ITEM SAFETY: a bag slot is claimed by the stack the removal hands out (never by succeeded() - it is true on an empty slot too)
M(ipg, r"""
public synchronized @IS@ takeSlot(int i) {
  @IS@ s = this.bag.getItemStack((short) i);
  if (s == null || s.isEmpty()) return null;
  @STX@ t = this.bag.removeItemStackFromSlot((short) i);
  @IS@ out = t == null ? null : t.getOutput();
  if (out == null || out.isEmpty()) return null;
  @IS@ left = this.bag.getItemStack((short) i);
  if (left != null && !left.isEmpty()) @PKG@.ProbeLog.warn("inv bag slot " + i + " still holds " + @PKG@.InvState.it(left) + " after taking " + @PKG@.InvState.it(out));
  return out;
}""")
M(ipg, r"""
public String bagList() {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < this.bag.getCapacity(); i++) {
    @IS@ s = this.bag.getItemStack((short) i);
    if (s == null || s.isEmpty()) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append("b:").append(i).append(" ").append(@PKG@.InvState.it(s));
  }
  return sb.toString();
}""")
M(ipg, r"""
public int returnBag(@REF@ ref, @ST@ st, String why) {
  int n = 0;
  String e1 = @PKG@.InvState.epoch(this.playerRef.getUuid());
  if (this.epoch0 != null && this.epoch0.length() > 0 && e1.length() > 0 && !e1.equals(this.epoch0) && bagList().length() > 0)
    @PKG@.ProbeLog.warn("inv bag-return: the SkyyProfiles profile changed (epoch " + this.epoch0 + " -> " + e1 + ") while the Probe Bag held " + bagList() + " - they go to the profile you are on now (probe limit: close the probe page before switching profile)");
  for (int i = 0; i < this.bag.getCapacity(); i++) {
    @IS@ s = takeSlot(i);
    if (s == null) continue;
    String w = @PKG@.InvState.give(ref, st, this.playerRef, s);
    @PKG@.ProbeLog.info("inv bag-return b:" + i + " " + @PKG@.InvState.it(s) + " -> " + w + " ok (" + why + ")");
    n = n + 1;
  }
  if (n > 0) @PKG@.ProbeLog.chat(this.playerRef, "Probe Bag: " + n + " stack(s) went back to your inventory (" + why + ").");
  return n;
}""")
M(ipg, r"""
public void finish(String why) {
  this.closed = true;
  unlisten();
  clearDrag();
  try { @PKG@.InvState.PAGES.remove(this.playerRef.getUuid(), this); } catch (Throwable t) { }
}""")
M(ipg, r"""
public int toPending(String why) {
  this.closed = true;
  int n = 0;
  java.util.UUID u = this.playerRef.getUuid();
  for (int i = 0; i < this.bag.getCapacity(); i++) {
    @IS@ s = takeSlot(i);
    if (s == null) continue;
    @PKG@.InvState.pend(u, s);
    @PKG@.ProbeLog.info("inv bag-return b:" + i + " " + @PKG@.InvState.it(s) + " -> kept in memory for your next join / world / page ok (" + why + ")");
    n = n + 1;
  }
  finish(why);
  return n;
}""")
M(ipg, r"""
public void shut() { this.close(); }""")
M(ipg, r"""
public void forceClose(String why) {
  if (this.closed) { finish(why); return; }
  this.closed = true;
  @REF@ r = this.playerRef.getReference();
  @ST@ s = r == null ? null : r.getStore();
  @PLA@ p = null;
  try { if (r != null && r.isValid()) p = (@PLA@) s.getComponent(r, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p != null) returnBag(r, s, why); else toPending(why);
  finish(why);
  try { if (p != null && p.getPageManager().getCustomPage() == this) this.close(); } catch (Throwable t) { }
  @PKG@.ProbeLog.info("inv page force-closed (" + why + ") after " + this.moves + " moves, " + this.fails + " fails");
}""")
M(ipg, r"""
public void bindGrid(@UEB@ ev, String g) {
  String s = sel(g);
  ev.addEventBinding(@BT@.SlotClicking, s, @EVD@.of("a", "sc").append("g", g), false);
  ev.addEventBinding(@BT@.Dropped, s, @EVD@.of("a", "dr").append("g", g), false);
  ev.addEventBinding(@BT@.SlotClickReleaseWhileDragging, s, @EVD@.of("a", "rl").append("g", g), false);
  ev.addEventBinding(@BT@.SlotDoubleClicking, s, @EVD@.of("a", "dc").append("g", g), false);
  ev.addEventBinding(@BT@.DragCancelled, s, @EVD@.of("a", "cx").append("g", g), false);
}""")
M(ipg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  long t0 = System.nanoTime();
  this.pref = ref;
  this.pst = st;
  String[] l = @PKG@.ProbeData.lines("bag".equals(this.view) ? "invbag" : "inv");
  int binds = 0;
  for (int i = 0; i < l.length; i++) {
    String s = l[i];
    char k = s.charAt(0);
    int a = s.indexOf('\t', 2);
    String x = s.substring(2, a);
    String y = s.substring(a + 1);
    if (k == 'A') b.appendInline(x.length() == 0 ? (String) null : x, y);
    else if (k == 'S') b.set(x, y);
    else if (k == 'E') { ev.addEventBinding(@BT@.Activating, x, @EVD@.of("a", y)); binds = binds + 1; }
  }
  b.set("#@PFX@Is.InventorySectionId", @INVC@.STORAGE_SECTION_ID);
  b.set("#@PFX@Ih.InventorySectionId", @INVC@.HOTBAR_SECTION_ID);
  b.set("#@PFX@Ia.InventorySectionId", @INVC@.ARMOR_SECTION_ID);
  b.set("#@PFX@Iu.InventorySectionId", @INVC@.UTILITY_SECTION_ID);
  putAll(b);
  java.util.ArrayList dz = new java.util.ArrayList();
  dz.add(new @IGS@());
  b.set("#@PFX@Dz.Slots", dz);
  b.set("#@PFX@TCap.Text", this.tcap.length() == 0 ? "Waiting for your move - opened by " + this.via : this.tcap);
  String[] gs = shown();
  for (int k = 0; k < gs.length; k++) { bindGrid(ev, gs[k]); binds = binds + 5; }
  ev.addEventBinding(@BT@.Dropped, "#@PFX@Dz", @EVD@.of("a", "dz"), false);
  binds = binds + 1;
  listen();
  this.builds = this.builds + 1;
  try { @PKG@.InvState.PAGES.put(this.playerRef.getUuid(), this); } catch (Throwable t) { }
  @PKG@.ProbeLog.info("inv build #" + this.builds + " (" + this.view + " view): " + gs.length + " grids, " + binds + " bindings, built in " + ((System.nanoTime() - t0) / 1000000L) + " ms");
}""")
M(ipg, r"""
public String doMove(String d, String g, int si, boolean out) {
  int csec = ival(d, "SourceInventorySectionId", 999);
  int cslot = ival(d, "SourceSlotId", -1);
  String sg = this.dg;
  int ss = this.ds;
  String cg = gridOf(csec);
  if (cg != null && cslot >= 0) {
    if (sg != null && (!sg.equals(cg) || ss != cslot)) @PKG@.ProbeLog.info("inv note: the client names " + cg + ":" + cslot + " as the source, the server tracked " + sg + ":" + ss + " - using the client's");
    sg = cg;
    ss = cslot;
  }
  String expect = val(d, "ItemStackId");
  if (expect == null) expect = this.di;
  int q = ival(d, "ItemStackQuantity", -1);
  String to = out ? "world" : (g + ":" + si);
  if (sg == null) { clearDrag(); return logmv(out ? "drop-outside" : "drag", "?", to, false, " (the event names no source and nothing was picked up - nothing moved)"); }
  String key = sg + ":" + ss + ">" + to;
  if (dup(key)) {
    clearDrag();
    @PKG@.ProbeLog.info("inv duplicate callback for " + key + " (release + drop of ONE gesture) - ignored, nothing moved twice");
    return "Same move reported twice - done once";
  }
  if (!out && nativeRecent()) {
    clearDrag();
    return logmv("drag", sg + ":" + ss, to, false, " (skipped: the client sent its own native move a moment ago - the game moved it)");
  }
  String r = out ? dropOut(sg, ss, q, expect, this.pref, this.pst) : move(sg, ss, g, si, q, expect);
  moved(key);
  clearDrag();
  return r;
}""")
M(ipg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {
  @PR@ pr = this.playerRef;
  String a = @PKG@.ProbeData.act(d);
  this.answered = false;
  try {
    if (this.closed) { this.answered = true; @PKG@.ProbeLog.info("inv click '" + a + "' arrived after the page closed - ignored, nothing moved"); return; }
    this.pref = ref;
    this.pst = st;
    @PKG@.ProbeLog.info("inv event " + cut(d));
    if (a.equals("close")) { this.answered = true; close(); return; }
    if (a.equals("tinv") || a.equals("tbag")) {
      String v = a.equals("tbag") ? "bag" : "inv";
      if (v.equals(this.view)) { say(("bag".equals(v) ? "The Probe Bag" : "The inventory") + " is already open"); return; }
      this.view = v;
      clearDrag();
      this.tcap = "bag".equals(v) ? "Probe Bag open - drag or shift-click items in and out" : "Inventory open";
      this.answered = true;
      this.answers = this.answers + 1;
      rebuild();
      @PKG@.ProbeLog.info("inv view " + v + ": ONE rebuild");
      return;
    }
    if (a.equals("sort")) { clearDrag(); answer(sort()); return; }
    String g = val(d, "g");
    int si = ival(d, "SlotIndex", -1);
    if (a.equals("sc")) {
      @IC@ c = cont(g);
      @IS@ s = (c != null && si >= 0 && si < c.getCapacity()) ? c.getItemStack((short) si) : null;
      boolean sh = bval(d, "ShiftHeld");
      if (s != null && !s.isEmpty() && this.dg == null) { this.dg = g; this.ds = si; this.di = s.getItemId(); this.dshift = sh; }
      if (this.dg != null) say("Holding " + this.di + " from " + gname(this.dg) + " slot " + (this.ds + 1) + (this.dshift ? " (shift held - release to quick-move)" : ""));
      else say("Empty slot " + (si + 1) + " in " + gname(g));
      return;
    }
    if (a.equals("rl")) {
      if (this.dg != null && this.dg.equals(g) && this.ds == si) {
        if (this.dshift || bval(d, "ShiftHeld")) {
          String r = nativeRecent() ? logmv("shift", g + ":" + si, "?", false, " (skipped: the client sent its own native SmartMove a moment ago - the game moved it)") : quick(g, si);
          clearDrag();
          moved("shift " + g + ":" + si);
          answer(r);
          return;
        }
        clearDrag();
        say("Put back in " + gname(g) + " slot " + (si + 1));
        return;
      }
      if (this.dg != null && g != null && si >= 0) { answer(doMove(d, g, si, false)); return; }
      say("Release on " + gname(g) + " slot " + (si + 1) + " - nothing held");
      return;
    }
    if (a.equals("dr") || a.equals("dz")) { answer(doMove(d, g, si, a.equals("dz"))); return; }
    if (a.equals("cx")) {
      String was = this.dg == null ? "nothing" : this.di + " from " + gname(this.dg) + " slot " + (this.ds + 1);
      clearDrag();
      @PKG@.ProbeLog.info("inv cancel " + was + " -> back ok");
      answer("Drag cancelled (" + was + ") - the grids are re-sent");
      return;
    }
    if (a.equals("dc")) { say("Double-click on " + gname(g) + " slot " + (si + 1) + " seen (the probe does nothing with it)"); return; }
    @PKG@.ProbeLog.warn("inv unknown event: " + cut(d));
    say("Unknown event - nothing changed");
  } catch (Throwable t) {
    @PKG@.ProbeLog.warn("inv event '" + a + "' failed: " + t);
    @PKG@.ProbeLog.chat(pr, "INV FAIL - the event failed: " + t);
  } finally {
    if (!this.answered && !this.closed) {
      this.answered = true;
      this.nets = this.nets + 1;
      this.answers = this.answers + 1;
      try { this.sendUpdate(); } catch (Throwable t2) { @PKG@.ProbeLog.warn("inv: the empty answer failed: " + t2); }
    }
  }
}""")
M(ipg, r"""
public void onDismiss(@REF@ ref, @ST@ st) {
  if (!this.closed) {
    this.closed = true;
    try { returnBag(ref, st, "page closed"); }
    catch (Throwable t) { @PKG@.ProbeLog.warn("inv bag-return on close failed: " + t + " - the rest is kept for your next join"); toPending("page closed, after an error"); }
    finish("page closed");
  }
  @PKG@.ProbeLog.info("inv page closed (Esc, Tab, Close or another page) for " + this.playerRef.getUsername() + " after " + this.moves + " moves, " + this.fails + " fails, " + this.answers + " answers");
}""")
M(irf, "public void run() { this.pg.refresh(); }")
M(icl, "public void run() { try { this.pg.forceClose(this.why); } catch (Throwable t) { @PKG@.ProbeLog.warn(\"inv force-close failed: \" + t); } }")
M(ich, "public void accept(Object e) { try { this.pg.changed(); } catch (Throwable t) { } }")

# ---- InvCmds: /uiprobe inv, the Tab redirect (world thread), /uiprobe tab on|off, the help lines
M(icm, r"""
public static void help(@PR@ pr) {
  @PKG@.ProbeLog.chat(pr, "INVENTORY PROBE (P0, research/Inventory-Screen-Plan.md): /uiprobe inv = the probe inventory page with your REAL items (drag, merge, shift-click, right-drag half, 1-9, Q, drag outside = drop, Sort) and a Probe Bag tab.");
  @PKG@.ProbeLog.chat(pr, "/uiprobe tab on = the Tab key opens that page instead of the vanilla inventory (you only, in memory, never saved); /uiprobe tab off = vanilla Tab back.");
}""")
M(icm, r"""
public static @PKG@.InvPage openInv(@REF@ ref, @ST@ st, @PR@ pr, String via) {
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) { @PKG@.ProbeLog.tell(pr, "INV FAIL - the page could not be opened (no player component)"); return null; }
  @PKG@.InvState.deliver(ref, st, pr);
  @PKG@.InvPage pg = new @PKG@.InvPage(pr, via);
  pg.epoch0 = @PKG@.InvState.epoch(pr.getUuid());
  try { p.getPageManager().openCustomPage(ref, st, pg); }
  catch (Throwable t) {
    @PKG@.ProbeLog.warn("inv page could not open: " + t);
    @PKG@.ProbeLog.chat(pr, "INV FAIL - the page could not be opened: " + t);
    pg.toPending("open failed");
    return null;
  }
  @PKG@.ProbeLog.tell(pr, "INV page opened (" + via + ") - PASS (server) if it shows. Skyy: look - do you see YOUR items in storage, hotbar, armour and utility? Try every move on the key line; each prints 'inv <move> ... ok' in the log.");
  return pg;
}""")
M(icm, r"""
public static void tab(@REF@ ref, @ST@ st, @PR@ pr, @PLA@ p, String via) {
  @PKG@.InvPage cur = (@PKG@.InvPage) @PKG@.InvState.PAGES.get(pr.getUuid());
  if (cur != null && !cur.closed && p.getPageManager().getCustomPage() == cur) {
    @PKG@.ProbeLog.info("inv tab: Tab pressed with the probe page open (" + via + ") - the page closes");
    cur.shut();
    return;
  }
  @WM@ wm = p.getWindowManager();
  if (wm != null && wm.getWindow(0) != null) {
    wm.closeWindow(ref, 0, (@CAC@) st);
    @PKG@.ProbeLog.info("inv tab: the server had window 0 open - closed it first (the CORE redirect step)");
  }
  openInv(ref, st, pr, "Tab key, caught by " + via);
}""")
M(icm, r"""
public static void tabCmd(@REF@ ref, @ST@ st, @PR@ pr, String w) {
  String t = w == null ? "" : w.trim().toLowerCase();
  java.util.UUID u = pr.getUuid();
  if (t.equals("on")) {
    @PKG@.InvState.TAB.put(u, Boolean.TRUE);
    boolean hk = @PKG@.InvState.isHooked(pr.getPacketHandler());
    @PKG@.ProbeLog.tell(pr, "TAB ON for you only (in memory, never saved; off with /uiprobe tab off or when you leave). Press Tab: the probe page should open instead of the vanilla inventory, with no vanilla flash. Your connection: " + (hk ? "hooked by the sub-packet handler" : "NOT hooked - the adapter filter has to catch it (a dedicated server; on your own world rejoin once)") + ". Hooked connections so far: " + @PKG@.InvState.INSTALLS + ".");
    return;
  }
  if (t.equals("off")) {
    boolean was = @PKG@.InvState.TAB.remove(u) != null;
    @PKG@.InvState.REDIR.remove(u);
    @PKG@.InvPage cur = (@PKG@.InvPage) @PKG@.InvState.PAGES.get(u);
    if (cur != null && !cur.closed) cur.forceClose("probe off");
    @PKG@.ProbeLog.tell(pr, (was ? "TAB OFF - the Tab key opens the vanilla inventory again." : "Tab was already off (vanilla).") + " Tab routes seen: " + @PKG@.InvState.SUB + " by the sub-packet handler, " + @PKG@.InvState.ADP + " by the adapter, " + @PKG@.InvState.ORPH + " orphan CloseWindow 0 absorbed, " + @PKG@.InvState.NATIVE + " native inventory packets while the page was open.");
    return;
  }
  @PKG@.ProbeLog.chat(pr, "Usage: /uiprobe tab on  or  /uiprobe tab off");
}""")
M(itk, r"""
public void run() {
  try {
    @REF@ ref = this.pr.getReference();
    if (ref == null || !ref.isValid()) return;
    @ST@ st = ref.getStore();
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return;
    if (this.kind == 1) { @PKG@.InvCmds.tab(ref, st, this.pr, p, this.via); return; }
    if (this.kind == 3) { if (this.pg != null) this.pg.dropCheck(this.sid, this.n0, this.via); return; }
    if (this.kind == 2) {
      @WM@ wm = p.getWindowManager();
      if (wm != null && wm.getWindow(0) != null) {
        wm.closeWindow(ref, 0, (@CAC@) st);
        @PKG@.ProbeLog.info("inv tab: the server's window 0 closed for the orphan CloseWindow - the probe page untouched");
      }
    }
  } catch (Throwable t) { @PKG@.ProbeLog.warn("inv task " + this.kind + " failed: " + t); }
}""")

# ---- the router (packet thread: no ECS, no page; the work is queued on the player's world) + install / shutdown
M(ist, r"""
public static boolean route(@PR@ pr, Object p, String via) {
  if (!ACTIVE || pr == null || p == null) return false;
  java.util.UUID u = pr.getUuid();
  if (p instanceof @COW@) {
    if (!on(u)) return false;
    @COW@ o = (@COW@) p;
    if (o.type != @WT@.PocketCrafting) { @PKG@.ProbeLog.info("inv tab: ClientOpenWindow " + o.type + " caught by " + via + " - not the inventory key, left to the game"); return false; }
    if (!queue(pr, new @PKG@.InvTask(1, pr, via))) { @PKG@.ProbeLog.warn("inv tab: Tab caught by " + via + " but the world queue refused - the vanilla screen opens"); return false; }
    REDIR.put(u, Long.valueOf(System.currentTimeMillis()));
    if (via.equals("adapter")) ADP = ADP + 1; else SUB = SUB + 1;
    @PKG@.ProbeLog.info("inv tab: Tab (ClientOpenWindow PocketCrafting) caught by " + via + " for " + pr.getUsername() + " - the vanilla window is swallowed, the probe page opens on the world thread");
    return true;
  }
  if (p instanceof @CW@) {
    @CW@ c = (@CW@) p;
    Object rt = REDIR.get(u);
    if (c.id != 0 || !on(u) || rt == null) return false;
    if (!PAGES.containsKey(u) && System.currentTimeMillis() - ((Long) rt).longValue() > 5000L) {
      REDIR.remove(u);
      @PKG@.ProbeLog.info("inv tab: CloseWindow 0 with no probe page open, 5 s after the redirect - left to the game");
      return false;
    }
    if (!queue(pr, new @PKG@.InvTask(2, pr, via))) return false;
    ORPH = ORPH + 1;
    @PKG@.ProbeLog.info("inv tab: CloseWindow 0 absorbed (" + via + ") - it never dismisses the probe page");
    return true;
  }
  if ((p instanceof @DIS@ || p instanceof @SMIS@ || p instanceof @MIS@) && PAGES.containsKey(u)) {
    NATIVE = NATIVE + 1;
    if (!(p instanceof @DIS@)) {
      long nw = System.currentTimeMillis();
      LASTNATIVE.put(u, Long.valueOf(nw));
      @PKG@.InvPage lp = (@PKG@.InvPage) PAGES.get(u);
      String lm = lp == null || lp.lastMove == null ? "" : lp.lastMove;
      if (lp != null && lp.lastMoveAt > 0L && nw - lp.lastMoveAt >= 0L && nw - lp.lastMoveAt < 1500L && !lm.endsWith(">world")) {
        lp.fails = lp.fails + 1;
        @PKG@.ProbeLog.warn("inv native " + pkt(p) + " AFTER a server move (" + lm + ", " + (nw - lp.lastMoveAt) + " ms ago) - possible undo (a swap may swap back); fail - this shows the client's order");
      }
    }
    @PKG@.ProbeLog.info("inv native " + pkt(p) + " while the probe page is open (" + via + ") - left to the game");
  }
  return false;
}""")
M(ist, r"""
public static void install() {
  ACTIVE = true;
  if (!INSTALLED) {
    try {
      @SM2@ sm = @SM2@.get();
      if (sm == null) @PKG@.ProbeLog.info("inv hooks: no ServerManager here - Tab is caught by the adapter filter only");
      else {
        sm.registerSubPacketHandlers(new @PKG@.InvHookFactory());
        INSTALLED = true;
        @PKG@.ProbeLog.info("inv hooks: sub-packet handler registered (every connection made from now on)");
      }
    } catch (Throwable t) { @PKG@.ProbeLog.warn("inv hooks: the sub-packet handler could not be registered: " + t); }
  } else @PKG@.ProbeLog.info("inv hooks: already registered in this server run (they pass through while the probe is stopped)");
  try { if (FILTER == null) FILTER = @PAD@.registerInbound((@PPF@) new @PKG@.InvFilter()); }
  catch (Throwable t) { @PKG@.ProbeLog.warn("inv: the adapter filter could not be registered: " + t); }
}""")
M(ist, r"""
public static void hold(@PKG@.InvPage pg, String why) {
  String l = pg.bagList();
  if (l.length() > 0) @PKG@.ProbeLog.warn("inv bag-hold (" + why + ") for " + pg.who().getUsername() + ": " + l + " - their return runs on the world thread; no 'inv bag-return' line for them = NOT returned");
}""")
M(ist, r"""
public static void shutdown() {
  ACTIVE = false;
  try { if (FILTER != null) @PAD@.deregisterInbound((@PFI@) FILTER); } catch (Throwable t) { }
  FILTER = null;
  java.util.ArrayList open = new java.util.ArrayList(PAGES.values());
  for (int i = 0; i < open.size(); i++) {
    @PKG@.InvPage pg = (@PKG@.InvPage) open.get(i);
    hold(pg, "server stopping");
    if (!now(pg.who(), new @PKG@.InvClose(pg, "server stopping"))) pg.toPending("server stopping");
  }
  TAB.clear();
  REDIR.clear();
  java.util.Iterator ki = PENDING.keySet().iterator();
  while (ki.hasNext()) {
    Object k = ki.next();
    java.util.ArrayList l = (java.util.ArrayList) PENDING.get(k);
    if (l == null) continue;
    StringBuilder sb = new StringBuilder();
    for (int j = 0; j < l.size(); j++) sb.append(j > 0 ? ", " : "").append(it((@IS@) l.get(j)));
    @PKG@.ProbeLog.warn("inv: NOT RETURNED (the server stopped; the probe keeps no data) for player " + k + ": " + sb.toString());
  }
}""")

# ---- the hooks: one SubPacketHandler per connection (the CORE method), the wrapper, the adapter fallback, the events
M(iwr, r"""
public void accept(Object p) {
  boolean taken = false;
  try { taken = @PKG@.InvState.route(this.g.getPlayerRef(), p, "subhandler"); } catch (Throwable t) { taken = false; }
  if (taken) return;
  this.nat.accept(p);
}""")
M(ihk, r"""
public void registerHandlers() {
  try {
    if (!(this.ph instanceof @GPH@)) return;
    @GPH@ g = (@GPH@) this.ph;
    int n = 0;
    java.util.function.Consumer c1 = @PKG@.InvState.nativeOf(g, @COW@.PACKET_ID);
    if (c1 != null) { g.registerHandler(@COW@.PACKET_ID, new @PKG@.InvWrap(g, c1, null, 0)); n = n + 1; }
    java.util.function.Consumer c2 = @PKG@.InvState.nativeOf(g, @CW@.PACKET_ID);
    if (c2 != null) { g.registerHandler(@CW@.PACKET_ID, new @PKG@.InvWrap(g, c2, null, 0)); n = n + 1; }
    java.util.function.Consumer c3 = @PKG@.InvState.nativeOf(g, @DIS@.PACKET_ID);
    if (c3 != null) { g.registerHandler(@DIS@.PACKET_ID, new @PKG@.InvWrap(g, c3, null, 1)); n = n + 1; }
    java.util.function.Consumer c4 = @PKG@.InvState.nativeOf(g, @SMIS@.PACKET_ID);
    if (c4 != null) { g.registerHandler(@SMIS@.PACKET_ID, new @PKG@.InvWrap(g, c4, null, 2)); n = n + 1; }
    java.util.function.Consumer c5 = @PKG@.InvState.nativeOf(g, @MIS@.PACKET_ID);
    if (c5 != null) { g.registerHandler(@MIS@.PACKET_ID, new @PKG@.InvWrap(g, c5, null, 3)); n = n + 1; }
    if (c1 != null && c2 != null) @PKG@.InvState.hooked(g);
    @PKG@.InvState.INSTALLS = @PKG@.InvState.INSTALLS + 1;
    @PKG@.ProbeLog.info("inv hooks: " + n + " packet handlers wrapped on a new connection" + ((c1 != null && c2 != null) ? "" : " - the Tab hook is MISSING here (the adapter filter covers a dedicated server)"));
  } catch (Throwable t) { @PKG@.ProbeLog.warn("inv hooks: install failed on a connection: " + t); }
}""")
M(ihf, r"""
public Object apply(Object o) { return new @PKG@.InvHooks((o instanceof @IPH@) ? (@IPH@) o : null); }""")
M(ifl, r"""
public boolean test(@PR@ pr, @PKT@ p) {
  try {
    if (pr == null || p == null) return false;
    if (!(p instanceof @COW@ || p instanceof @CW@ || p instanceof @DIS@ || p instanceof @SMIS@ || p instanceof @MIS@)) return false;
    if (@PKG@.InvState.isHooked(pr.getPacketHandler())) return false;
    return @PKG@.InvState.route(pr, p, "adapter");
  } catch (Throwable t) { return false; }
}""")
M(ifl, r"""
public boolean test(Object a, Object b) { return test((@PR@) a, (@PKT@) b); }""")
M(ibye, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDE@) ev).getPlayerRef();
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    boolean was = @PKG@.InvState.TAB.remove(u) != null;
    @PKG@.InvState.REDIR.remove(u);
    @PKG@.InvState.LASTNATIVE.remove(u);
    @PKG@.InvPage pg = (@PKG@.InvPage) @PKG@.InvState.PAGES.get(u);
    if (pg != null) {
      @PKG@.InvState.hold(pg, "disconnect");
      if (!@PKG@.InvState.now(pr, new @PKG@.InvClose(pg, "disconnect"))) pg.toPending("disconnect, no world thread");
    }
    if (was) @PKG@.ProbeLog.info("inv tab: switched OFF for " + pr.getUsername() + " (left the game)");
  } catch (Throwable t) { @PKG@.ProbeLog.warn("inv: disconnect handling failed: " + t); }
}""")
M(irdy, r"""
public void accept(Object ev) {
  try {
    @REF@ r = ((@PRE@) ev).getPlayerRef();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.InvPage pg = (@PKG@.InvPage) @PKG@.InvState.PAGES.get(pr.getUuid());
    if (pg != null && !pg.closed && (pg.pref != r || pg.pst != st)) pg.toPending("world change");
    @PKG@.InvState.deliver(r, st, pr);
  } catch (Throwable t) { @PKG@.ProbeLog.warn("inv: world-change handling failed: " + t); }
}""")
'''
S = rep(S, "\n# ---- ProbeCmds: help, tour, next, open a case", INV_JAVA + "\n# ---- ProbeCmds: help, tour, next, open a case")

S = rep(S, '''  @PKG@.ProbeLog.info("help listed for " + (pr == null ? "?" : pr.getUsername()));''',
        '''  @PKG@.InvCmds.help(pr);
  @PKG@.ProbeLog.info("help listed for " + (pr == null ? "?" : pr.getUsername()));''')
S = rep(S, '''  if (t.equals("tipgear")) { @PKG@.Tips.gear(ref, store, pr); return; }''',
        '''  if (t.equals("tipgear")) { @PKG@.Tips.gear(ref, store, pr); return; }
  if (t.equals("inv")) { @PKG@.InvCmds.openInv(ref, store, pr, "/uiprobe inv"); return; }''')
S = rep(S, '''  super("(admin) /skyprobe tour | next | <case> - the UI queue probe; /skyprobe help lists the cases");''',
        '''  super("(admin) /skyprobe tour | next | inv | <case> - the UI queue probe + the inventory probe; /skyprobe help lists the cases");''')
S = rep(S, '''withRequiredArg("what", "tour, next, help, tipgear, or a case:''', '''withRequiredArg("what", "tour, next, help, tipgear, inv, or a case:''')

TAB_CMD = r'''cmdTab = mk("SkyProbeTabCmd", T["APC"])
# 0.10 I2: /uiprobe tab on|off - a SUB-command (2 words; usage variants are picked by the exact token count)
F(cmdTab, "public @RA@ stateArg;")
C(cmdTab, r"""
public SkyProbeTabCmd() {
  super("tab", "(admin) /uiprobe tab on|off - the inventory probe: Tab opens the probe page instead of the vanilla inventory (you only, in memory)");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.stateArg = withRequiredArg("state", "on or off", @ATY@.STRING);
}""")
M(cmdTab, EXEC + r""" {
  try { @PKG@.InvCmds.tabCmd(ref, store, pr, String.valueOf(ctx.get(this.stateArg))); }
  catch (Throwable t) { @PKG@.ProbeLog.warn("/uiprobe tab failed: " + t); @PKG@.ProbeLog.chat(pr, "Usage: /uiprobe tab on  or  /uiprobe tab off"); }
}""")
'''
S = rep(S, 'cmd = mk("SkyProbeCmd", T["APC"])', TAB_CMD + 'cmd = mk("SkyProbeCmd", T["APC"])')
S = rep(S, '''  super("skyprobe", "(admin) PROBE: the UI queue test pages (15 cases) + the price-tooltip probe (tip / tiplater / tipgear) - /skyprobe help lists them");''',
        '''  super("skyprobe", "(admin) PROBE: the UI queue test pages (15 cases) + the price-tooltip probe (tip / tiplater / tipgear) + the inventory probe (inv / tab on|off) - /skyprobe help lists them");''')
S = rep(S, '''  addSubCommand(new @PKG@.SkyProbeTipCmd("tiplater"));''', '''  addSubCommand(new @PKG@.SkyProbeTipCmd("tiplater"));
  addSubCommand(new @PKG@.SkyProbeTabCmd());''')
S = rep(S, '''  getCommandRegistry().registerCommand(new @PKG@.SkyProbeCmd());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyUiProbe] @VERSION@ ready - PROBE (op only): /skyprobe tour (alias /uiprobe) walks through the @NCASE@ UI queue cases + /uiprobe tip / tiplater / tipgear (price-tooltip probe P1-P5); no data, no HUD, nothing for players");''',
        '''  getCommandRegistry().registerCommand(new @PKG@.SkyProbeCmd());
  try {
    if (getEventRegistry() == null) @PKG@.ProbeLog.info("inv: no event registry here - the bag returns on disconnect / world change are off");
    else {
      getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.InvBye());
      getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.InvReady());
    }
  } catch (Throwable t) { @PKG@.ProbeLog.warn("inv: the event listeners could not be registered: " + t); }
  @PKG@.InvState.install();
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyUiProbe] @VERSION@ ready - PROBE (op only): /skyprobe tour (alias /uiprobe) walks through the @NCASE@ UI queue cases + /uiprobe tip / tiplater / tipgear (price-tooltip probe P1-P5) + /uiprobe inv, /uiprobe tab on|off (inventory probe P0); no data, no HUD, nothing for players");''')
S = rep(S, 'M(pl, "protected void shutdown() { @PKG@.ProbeTimer.stop(); super.shutdown(); }")',
        'M(pl, "protected void shutdown() { @PKG@.InvState.shutdown(); @PKG@.ProbeTimer.stop(); super.shutdown(); }")')
S = rep(S, "CLASSES = [log, data, thr, tim, rta, rtp, hres, heads, later, page_c, cmds, tips, tsend, cmdA, cmdT, cmd, pl]",
        "CLASSES = [log, data, thr, tim, rta, rtp, hres, heads, later, page_c, cmds, tips, tsend] + INV_CLASSES + [cmdA, cmdT, cmdTab, cmd, pl]")
S = rep(S, "+ the price-tooltip probe (/uiprobe tip, tiplater, tipgear: P1-P5) for one test session",
        "+ the price-tooltip probe (/uiprobe tip, tiplater, tipgear: P1-P5) + the inventory probe (/uiprobe inv, /uiprobe tab on|off: P0 of the inventory screen plan, real items, a Probe Bag) for one test session")
save("build_skyyuiprobe_0.10.py", S)

# ===================================================================================================== the harness
H = load("test_skyyuiprobe_0.9.py")
H = rep(H, '''"""Harness for SkyyUiProbe 0.9 (the UI queue probe, 15 cases + the price-tooltip probe R0; SkyyUiProbe/build_skyyuiprobe_0.9.py,
made by tools/uiprobe_0_9_patch.py). Build first: python SkyyUiProbe/build_skyyuiprobe_0.9.py

    python SkyyUiProbe/test_skyyuiprobe_0.9.py [--keep] [--old-jar <the 0.8 jar>] [--dir <folder inside tools/dev/scratch/>]''',
        '''"""Harness for SkyyUiProbe 0.10 (the UI queue probe, 15 cases + the price-tooltip probe R0 + the INVENTORY PROBE P0;
SkyyUiProbe/build_skyyuiprobe_0.10.py, made by tools/uiprobe_0_10_patch.py). Build first: python SkyyUiProbe/build_skyyuiprobe_0.10.py

    python SkyyUiProbe/test_skyyuiprobe_0.10.py [--keep] [--old-jar <the 0.9 jar>] [--dir <folder inside tools/dev/scratch/>]''')
H = rep(H, '''       CMDS    the command classes construct (admin: requirePermission skyyuiprobe.admin + no permission groups; alias uiprobe)''',
        '''       INV     (0.10) the inventory probe on a fresh player (storage / hotbar / armour / utility stand-ins, a rolled sword with
               ItemDisplayMetadata): /uiprobe inv = ONE page packet (InventorySectionId -2 / -1 / -3 / -5, every grid's Slots, the
               sword's slot WITHOUT metadata but with its name + description, the drop zone, 25 bindings); every move as the client
               sends it (pick up + drop, the client's source fields or the tracked one): drag, merge (cap 100), swap, split, a part
               stack onto another item refused, release-on-another-slot + its duplicate Dropped (moved ONCE), two drops of one slot
               (the second fails), shift both ways, put back, cancel, double-click, Sort, drag outside (the probe's own drop: ok /
               refused = put back / the real ItemUtils call; the game's own drop through InventoryPacketHandler), native Move / Drop /
               SmartMove observed (left to the game, a drag right after a native move skipped), a change event = ONE refresh, none
               when nothing changed; each = exactly ONE page packet and item totals unchanged. The Probe Bag: tab = ONE rebuild (30
               bindings), drag / shift in and out, drag out of the bag onto the drop zone; EVERY close path gives the bag back:
               Esc, Tab, probe off, disconnect (queued + no world), world change (to the new world's inventory), shutdown, a full
               inventory (feet / kept in memory, given back at the next ready / open); a click after close moves nothing. Tab
               routing: off = untouched, on = PocketCrafting caught by the subhandler / the adapter (never both), CloseWindow 0
               absorbed, other windows left alone, Tab again closes; the sub-packet hooks on a GamePacketHandler stand-in (the
               game's own consumers wrapped, Inventory packets to InventoryPacketHandler, the factory, a connection without the
               natives); /skyprobe inv + /skyprobe tab on|off through the engine's parser
       CMDS    the command classes construct (admin: requirePermission skyyuiprobe.admin + no permission groups; alias uiprobe)''')
H = rep(H, "Scratch: tools/dev/scratch/tip0/harness (deleted unless --keep). C = class compare vs the 0.8 jar.",
        "Scratch: tools/dev/scratch/uip010/harness (deleted unless --keep). C = class compare vs the 0.9 jar.")
H = rep(H, 'VERSION = "0.9"', 'VERSION = "0.10"')
H = rep(H, 'OLD_JAR = os.path.abspath(HK.arg("--old-jar", os.path.join(HERE, "SkyyUiProbe-0.8.jar")))',
        'OLD_JAR = os.path.abspath(HK.arg("--old-jar", os.path.join(HERE, "SkyyUiProbe-0.9.jar")))')
H = rep(H, 'os.path.join(ROOT, "tools", "dev", "scratch", "tip0", "harness")', 'os.path.join(ROOT, "tools", "dev", "scratch", "uip010", "harness")')
H = rep(H, '''           "Tips", "TipSend", "SkyProbeArgCmd", "SkyProbeTipCmd", "SkyProbeCmd", "SkyyUiProbePlugin"]''',
        '''           "Tips", "TipSend", "SkyProbeArgCmd", "SkyProbeTipCmd", "SkyProbeCmd", "SkyyUiProbePlugin",
           "InvState", "InvPage", "InvTask", "InvRefresh", "InvClose", "InvChange", "InvHooks", "InvHookFactory", "InvWrap", "InvFilter",
           "InvBye", "InvReady", "InvCmds", "SkyProbeTabCmd"]''')
_cmp_old = H[H.index("# class compare vs 0.8"):H.index('CMP_ADDED = ["Tips", "TipSend", "SkyProbeTipCmd"]') + len('CMP_ADDED = ["Tips", "TipSend", "SkyProbeTipCmd"]')]
H = rep(H, _cmp_old, '''# class compare vs 0.9: only these classes / members may differ (everything else byte-identical)
CMP_EXPECT = {"ProbeCmds": ["~m arg", "~m help"], "SkyProbeArgCmd": ["~c "], "SkyProbeCmd": ["~c "],
              "SkyyUiProbePlugin": ["~m setup", "~m shutdown"]}
CMP_ADDED = ["InvState", "InvPage", "InvTask", "InvRefresh", "InvClose", "InvChange", "InvHooks", "InvHookFactory", "InvWrap", "InvFilter",
             "InvBye", "InvReady", "InvCmds", "SkyProbeTabCmd"]''')
# the 0.9 parser / command checks: + tab
H = rep(H, '''    for line in ("skyprobe tip Wood_Oak_Trunk Test 1", 'skyprobe tip Wood_Oak_Trunk "Test 1"', "skyprobe tiplater Wood_Oak_Trunk Test 2",
                 "skyprobe tip gear Test 3", "skyprobe tipgear", "skyprobe tour", "skyprobe"):''',
        '''    for line in ("skyprobe tip Wood_Oak_Trunk Test 1", 'skyprobe tip Wood_Oak_Trunk "Test 1"', "skyprobe tiplater Wood_Oak_Trunk Test 2",
                 "skyprobe tip gear Test 3", "skyprobe tipgear", "skyprobe tour", "skyprobe", "skyprobe inv", "skyprobe tab on",
                 "skyprobe tab off", "uiprobe tab on"):''')
H = rep(H, '''    for line in ("skyprobe tip Wood_Oak_Trunk", "skyprobe tip", "skyprobe tiplater Wood_Oak_Trunk", "skyprobe tour extra"):''',
        '''    for line in ("skyprobe tip Wood_Oak_Trunk", "skyprobe tip", "skyprobe tiplater Wood_Oak_Trunk", "skyprobe tour extra", "skyprobe tab",
                 "skyprobe tab on extra"):''')
H = rep(H, '''    K.eq(sorted(subs), ["tip", "tiplater"], "CMDS: the sub-commands tip + tiplater")
    for nm_, tc_ in sorted(subs.items()):
        K.check(str(tc_.getClass().getSimpleName()) == "SkyProbeTipCmd" and str(tc_.getName()) == nm_, "CMDS: /skyprobe %s = SkyProbeTipCmd" % nm_)''',
        '''    K.eq(sorted(subs), ["tab", "tip", "tiplater"], "CMDS: the sub-commands tab + tip + tiplater")
    for nm_, tc_ in sorted(subs.items()):
        want_ = "SkyProbeTabCmd" if nm_ == "tab" else "SkyProbeTipCmd"
        K.check(str(tc_.getClass().getSimpleName()) == want_ and str(tc_.getName()) == nm_, "CMDS: /skyprobe %s = %s" % (nm_, want_))''')

INV_TEST = r'''
    # ================================================================= INV (0.10): the inventory probe P0, every new path executed
    from jpype import JArray as _JA
    INVST, INVPG, INVCM = JV("InvState"), JV("InvPage"), JV("InvCmds")
    ISc = JClass(PH + "server.core.inventory.ItemStack")
    MSGc = JClass(PH + "server.core.Message")
    COWc, CWc = JClass(PH + "protocol.packets.window.ClientOpenWindow"), JClass(PH + "protocol.packets.window.CloseWindow")
    WTc = JClass(PH + "protocol.packets.window.WindowType")
    DISc, SMISc, MISc = (JClass(PH + "protocol.packets.inventory.DropItemStack"), JClass(PH + "protocol.packets.inventory.SmartMoveItemStack"),
                         JClass(PH + "protocol.packets.inventory.MoveItemStack"))
    SMTc = JClass(PH + "protocol.SmartMoveType")
    UUIDc = JClass("java.util.UUID")
    TTc = JClass(PH + "server.core.util.thread.TickingThread")
    ARc = JClass("java.util.concurrent.atomic.AtomicReference")
    for w_ in (E.W1, E.W2):
        E.jf(TTc.class_, "currentRun").set(w_, ARc())
    for iid_, ms_ in (("Rock_Stone", 100), ("Weapon_Sword_Iron", 1), ("Plant_Fruit_Apple", 100)):
        fake_item(iid_, None, ms_)
    INVST.install()                                    # no ServerManager in this JVM: the adapter-only path; ACTIVE = true
    K.check(bool(INVST.ACTIVE) and INVST.FILTER is not None and not bool(INVST.INSTALLED), "INV: install() without a ServerManager = adapter filter only, active")
    K.check(any("no ServerManager here" in l for l in tail()), "INV: install() says the sub-packet handler is not there")

    def inv(PP, f):
        return PP.slots[f].getInventory()

    def put(PP, f, slot, stack):
        inv(PP, f).addItemStackToSlot(JShort(slot), stack)

    def at(PP, f, slot):
        s_ = inv(PP, f).getItemStack(JShort(slot))
        return None if s_ is None or s_.isEmpty() else (str(s_.getItemId()), int(s_.getQuantity()))

    def bag_of(pg_):
        out_ = {}
        for i_ in range(int(pg_.bag.getCapacity())):
            s_ = pg_.bag.getItemStack(JShort(i_))
            if s_ is not None and not s_.isEmpty():
                out_[i_] = (str(s_.getItemId()), int(s_.getQuantity()))
        return out_

    def tot(PP, iid, pg_=None):
        n_ = E.count(PP, iid)
        if pg_ is not None:
            n_ += sum(q for i_, q in bag_of(pg_).values() if i_ == iid)
        return n_
    IDS = ("Wood_Oak_Trunk", "Rock_Stone", "Weapon_Sword_Iron", "Plant_Fruit_Apple")

    def totals(PP, pg_=None):
        return dict((i_, tot(PP, i_, pg_)) for i_ in IDS)

    def sword():
        nm_ = MSGc.raw("Rolled Iron Sword").color("#ff5555")
        ds_ = MSGc.join(_JA(MSGc)([MSGc.raw("T3 Iron - Sword\n"), MSGc.raw("Damage +5").color("#7ee08a")]))
        return ISc("Weapon_Sword_Iron", 1).withMetadata(IDMc.KEYED_CODEC, IDMc(nm_, ds_))

    def ev(PP, obj):
        E.pump(PP)
        f_ = len(E.sent(PP))
        PP.pm.handleLegacyCustomPageEvent(PP.ref, PP.st, E.CPE(E.CPT.Data, json.dumps(obj)))
        return [p_ for p_ in E.sent(PP)[f_:] if str(p_.getClass().getSimpleName()) == "CustomPage"]

    def cmap(pk_):
        d_ = {}
        for c_ in cmds_of(pk_):
            d_[str(c_.selector)] = (str(c_.data) if c_.data is not None else "") + (str(c_.text) if c_.text is not None else "")
        return d_

    def binds_of(pk_):
        b_ = pk_.eventBindings if hasattr(pk_, "eventBindings") else None
        return [] if b_ is None else [(str(x.type), str(x.selector), str(x.data)) for x in b_]

    def mark():
        LOG.TAIL.clear()                               # the log keeps 400 lines: each check reads the lines since its own mark
        return 0

    def lines_since(n_):
        return tail()

    def pchats(PP, f_):
        return E.strs_of(PP, f_)

    def drag(PP, sg, ss, tg, ts, q=None, client=True, iid=None):
        """the client's two events: pick up (SlotClicking) + drop (Dropped on the target grid) - returns both packet lists"""
        a_ = ev(PP, {"a": "sc", "g": sg, "SlotIndex": ss})
        o_ = {"a": "dr", "g": tg, "SlotIndex": ts}
        if client:
            o_.update({"SourceInventorySectionId": {"s": -2, "h": -1, "a": -3, "u": -5}[sg], "SourceSlotId": ss})
            if iid:
                o_["ItemStackId"] = iid
            if q:
                o_["ItemStackQuantity"] = q
        b_ = ev(PP, o_)
        return a_, b_

    PI = E.player(uid=UUIDc(0x51, 0x51), name="SkyyInv")
    put(PI, "storage", 0, ISc("Wood_Oak_Trunk", 10))
    put(PI, "storage", 1, ISc("Wood_Oak_Trunk", 95))
    put(PI, "storage", 2, ISc("Rock_Stone", 5))
    put(PI, "storage", 5, sword())
    put(PI, "storage", 7, ISc("Plant_Fruit_Apple", 30))
    put(PI, "hotbar", 0, ISc("Plant_Fruit_Apple", 3))
    T0 = totals(PI)
    K.eq(T0, {"Wood_Oak_Trunk": 105, "Rock_Stone": 5, "Weapon_Sword_Iron": 1, "Plant_Fruit_Apple": 33}, "INV SETUP: the test inventory")
    # I4 straight on the slot copy: no metadata, the name + description from ItemDisplayMetadata, the real stack keeps its metadata
    IGSc = JClass(PH + "server.core.ui.ItemGridSlot")
    sl = INVPG.slot(inv(PI, "storage").getItemStack(JShort(5)))
    sst = E.jf(IGSc.class_, "itemStack").get(sl)
    K.check(sst is not None and sst.getMetadata() is None and str(sst.getItemId()) == "Weapon_Sword_Iron", "I4: the grid copy of the rolled sword carries NO metadata")
    K.eq(str(E.jf(IGSc.class_, "name").get(sl)), "Rolled Iron Sword", "I4: the slot name comes from ItemDisplayMetadata")
    K.check("T3 Iron - Sword" in str(E.jf(IGSc.class_, "description").get(sl)) and "Damage +5" in str(E.jf(IGSc.class_, "description").get(sl)),
            "I4: the slot description = the metadata description, children joined")
    K.check(inv(PI, "storage").getItemStack(JShort(5)).getMetadata() is not None, "I4: the REAL sword keeps its metadata (only the copy is stripped)")
    pl_ = INVPG.slot(inv(PI, "storage").getItemStack(JShort(0)))
    K.check(E.jf(IGSc.class_, "name").get(pl_) is None and bool(E.jf(IGSc.class_, "isActivatable").get(pl_)), "I4: a plain item gets no name override, slots are activatable")
    K.check(E.jf(IGSc.class_, "itemStack").get(INVPG.slot(None)) is None, "I4: an empty slot = an empty ItemGridSlot")
    K.eq(str(INVPG.flat(MSGc.join(_JA(MSGc)([MSGc.raw("a"), MSGc.translation("server.x.y"), MSGc.join(_JA(MSGc)([MSGc.raw("b")]))])))), "a[server.x.y]b",
         "I4: flat() joins children in order, a translation key shows as [key]")
    for js_, k_, want_ in (('{"a":"dr","SlotIndex":3,"g":"s"}', "SlotIndex", "3"), ('{"g": "b", "ShiftHeld" : true}', "ShiftHeld", "true"),
                           ('{"ItemStackId":"Wood_Oak_Trunk","DragItemStackId":"X"}', "ItemStackId", "Wood_Oak_Trunk"),
                           ('{"DragSourceSlotId":4,"SourceSlotId":7}', "SourceSlotId", "7"), ('{"SourceSlotId":null}', "SourceSlotId", None),
                           ('{"a":"x"}', "SlotIndex", None)):
        got_ = INVPG.val(js_, k_)
        K.eq(None if got_ is None else str(got_), want_, "INV: val(%s, %s)" % (js_, k_))
    K.eq(int(INVPG.ival('{"SlotIndex":2.0}', "SlotIndex", -1)), 2, "INV: ival reads 2.0 as 2")
    K.eq(int(INVPG.ival('{"SlotIndex":"x"}', "SlotIndex", -1)), -1, "INV: ival of junk = the default")

    # ---- I1: open
    f0, n0 = len(E.sent(PI)), mark()
    CMDS.arg(PI.ref, PI.st, PI.pr, "inv")
    pg = PI.pm.getCustomPage()
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "InvPage", "I1: /uiprobe inv opens the InvPage")
    pk = [p_ for p_ in E.sent(PI)[f0:] if str(p_.getClass().getSimpleName()) == "CustomPage"]
    K.eq(len(pk), 1, "I1: ONE CustomPage packet")
    cm = cmap(pk[0]) if pk else {}
    K.eq([json.loads(cm.get("#SkyyPrI%s.InventorySectionId" % g_, "{}")).get("0") for g_ in "shau"], [-2, -1, -3, -5], "I1: InventorySectionId -2 / -1 / -3 / -5 (the InventoryComponent ids)")
    K.check(all(("#SkyyPrI%s.Slots" % g_) in cm for g_ in "shau") and "#SkyyPrIb.Slots" not in cm and "#SkyyPrDz.Slots" in cm,
            "I1: the server sends every grid's Slots (+ the drop zone; no bag in the inventory view)")
    sd = cm.get("#SkyyPrIs.Slots", "")
    K.check("Wood_Oak_Trunk" in sd and "Rolled Iron Sword" in sd and "Damage +5" in sd and "ItemDisplay" not in sd,
            "I1 / I4: the storage Slots hold the real items; the sword's name + description travel, its metadata does not")
    K.check("Plant_Fruit_Apple" in cm.get("#SkyyPrIh.Slots", ""), "I1: the hotbar Slots hold the hotbar apples")
    bl = binds_of(pk[0]) if pk else []
    K.eq(len(bl), 25, "I1: 25 bindings (4 buttons + 4 grids x 5 slot events + the drop zone)")
    K.check(("SlotClicking", "#SkyyPrIs") in [(t_, s_) for t_, s_, _d in bl] and ("Dropped", "#SkyyPrDz") in [(t_, s_) for t_, s_, _d in bl]
            and not any("MouseEntered" in t_ or "MouseExited" in t_ for t_, _s, _d in bl), "I1: slot events bound, the drop zone bound, NO hover event")
    K.check(any('"g":"s"' in d_.replace(" ", "") and '"a":"dr"' in d_.replace(" ", "") for t_, s_, d_ in bl if s_ == "#SkyyPrIs"), "I1: the grid events carry {a, g}")
    K.check("INV page opened (/uiprobe inv)" in pchats(PI, f0), "I1: the opened line in chat")
    K.check(INVST.PAGES.get(PI.pr.getUuid()) == pg, "I1: the open page is known by uuid")

    def one(pks, what):
        K.eq(len(pks), 1, what + ": exactly ONE page packet")
        return pks[0] if pks else None

    def ok_line(n_, frag):
        return any(frag in l for l in lines_since(n_))
    # ---- moves
    n0 = mark()
    a_, b_ = drag(PI, "s", 0, "h", 1, q=10, iid="Wood_Oak_Trunk")
    p_ = one(a_, "MOVE pick up")
    if p_ is not None:
        K.eq(list(cmap(p_)), ["#SkyyPrTCap.Text"], "MOVE pick up: only the caption (the grids are untouched while the client holds the stack)")
    p_ = one(b_, "MOVE drag")
    K.eq((at(PI, "storage", 0), at(PI, "hotbar", 1)), (None, ("Wood_Oak_Trunk", 10)), "MOVE drag: s:0 -> h:1")
    if p_ is not None:
        K.check(not is_clear(p_) and all(("#SkyyPrI%s.Slots" % g_) in cmap(p_) for g_ in "shau"), "MOVE drag: ONE update re-sends the grids")
    K.check(ok_line(n0, "inv drag s:0 Wood_Oak_Trunk x10 -> h:1 ok"), "MOVE drag: the log line")
    n0 = mark()
    one(drag(PI, "h", 1, "s", 1, q=10, iid="Wood_Oak_Trunk")[1], "MOVE merge")
    K.eq((at(PI, "hotbar", 1), at(PI, "storage", 1)), (("Wood_Oak_Trunk", 5), ("Wood_Oak_Trunk", 100)), "MOVE merge: onto 95 -> 100, 5 stay")
    K.check(ok_line(n0, "inv merge h:1 Wood_Oak_Trunk x10 -> s:1 ok"), "MOVE merge: the log line")
    n0 = mark()
    one(drag(PI, "s", 2, "s", 1, q=5, iid="Rock_Stone")[1], "MOVE swap")
    K.eq((at(PI, "storage", 1), at(PI, "storage", 2)), (("Rock_Stone", 5), ("Wood_Oak_Trunk", 100)), "MOVE swap: rock <-> wood")
    K.check(ok_line(n0, "inv swap s:2 Rock_Stone x5 -> s:1 ok"), "MOVE swap: the log line")
    n0 = mark()
    one(drag(PI, "s", 1, "s", 10, q=2, iid="Rock_Stone")[1], "MOVE split")
    K.eq((at(PI, "storage", 1), at(PI, "storage", 10)), (("Rock_Stone", 3), ("Rock_Stone", 2)), "MOVE split (right-drag half): 2 of 5")
    K.check(ok_line(n0, "inv split s:1 Rock_Stone x2 -> s:10 ok"), "MOVE split: the log line")
    n0 = mark()
    one(drag(PI, "s", 10, "s", 2, q=1, iid="Rock_Stone")[1], "MOVE part onto another item")
    K.eq((at(PI, "storage", 10), at(PI, "storage", 2)), (("Rock_Stone", 2), ("Wood_Oak_Trunk", 100)), "MOVE part onto another item: refused, nothing moved")
    K.check(ok_line(n0, "inv swap s:10 Rock_Stone x1 -> s:2 fail (part of a stack cannot swap"), "MOVE part onto another item: the fail line")
    n0 = mark()
    one(drag(PI, "h", 0, "s", 20, client=False)[1], "MOVE tracked source")
    K.eq((at(PI, "hotbar", 0), at(PI, "storage", 20)), (None, ("Plant_Fruit_Apple", 3)), "MOVE without the client's source fields = the tracked pick-up")
    K.check(ok_line(n0, "inv drag h:0 Plant_Fruit_Apple x3 -> s:20 ok"), "MOVE tracked source: the log line")
    # a release on another slot = the drop (CORE); the Dropped of the same gesture moves nothing twice
    n0 = mark()
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": 20}), "MOVE release pick up")
    one(ev(PI, {"a": "rl", "g": "h", "SlotIndex": 2}), "MOVE release on another slot")
    one(ev(PI, {"a": "dr", "g": "h", "SlotIndex": 2, "SourceInventorySectionId": -2, "SourceSlotId": 20, "ItemStackId": "Plant_Fruit_Apple"}), "MOVE its Dropped")
    K.eq((at(PI, "storage", 20), at(PI, "hotbar", 2)), (None, ("Plant_Fruit_Apple", 3)), "MOVE release + Dropped = moved ONCE")
    K.check(ok_line(n0, "inv drag s:20 Plant_Fruit_Apple x3 -> h:2 ok") and ok_line(n0, "duplicate callback for s:20>h:2"), "MOVE release + Dropped: one move, the duplicate logged")
    # two drops of the same slot (outside the 1.5 s duplicate window): the second finds the slot empty
    n0 = mark()
    one(drag(PI, "h", 2, "h", 3, iid="Plant_Fruit_Apple")[1], "MOVE first click")
    pg.lastMoveAt = 0
    one(ev(PI, {"a": "dr", "g": "h", "SlotIndex": 3, "SourceInventorySectionId": -1, "SourceSlotId": 2, "ItemStackId": "Plant_Fruit_Apple"}), "MOVE second click")
    K.eq((at(PI, "hotbar", 2), at(PI, "hotbar", 3)), (None, ("Plant_Fruit_Apple", 3)), "MOVE two drops of one slot: moved once")
    K.check(ok_line(n0, "inv drag h:2 -> h:3 fail (the source slot is empty now"), "MOVE two drops: the second fails, nothing duplicated")
    K.eq(totals(PI), T0, "MOVE: every item total unchanged after the drags")
    # shift both ways
    n0 = mark()
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": 7, "ShiftHeld": True}), "SHIFT pick up")
    one(ev(PI, {"a": "rl", "g": "s", "SlotIndex": 7, "ShiftHeld": True}), "SHIFT release")
    K.check(at(PI, "storage", 7) is None and E.count(PI, "Plant_Fruit_Apple") == 33 and sum(at(PI, "hotbar", i_)[1] for i_ in range(9)
            if at(PI, "hotbar", i_) and at(PI, "hotbar", i_)[0] == "Plant_Fruit_Apple") == 33, "SHIFT storage -> hotbar: all 30 apples to the hotbar")
    K.check(ok_line(n0, "inv shift s:7 Plant_Fruit_Apple x30 -> h ok (30 of 30 moved)"), "SHIFT: the log line")
    hs_ = [i_ for i_ in range(9) if at(PI, "hotbar", i_) == ("Wood_Oak_Trunk", 5)][0]
    n0 = mark()
    one(ev(PI, {"a": "sc", "g": "h", "SlotIndex": hs_}), "SHIFT2 pick up")
    one(ev(PI, {"a": "rl", "g": "h", "SlotIndex": hs_, "ShiftHeld": True}), "SHIFT2 release (shift pressed late)")
    K.check(at(PI, "hotbar", hs_) is None and ok_line(n0, "inv shift h:%d Wood_Oak_Trunk x5 -> s ok" % hs_), "SHIFT hotbar -> storage")
    n0 = mark()
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": 2}), "PUTBACK pick up")
    p_ = one(ev(PI, {"a": "rl", "g": "s", "SlotIndex": 2}), "PUTBACK release on the same slot")
    K.check(p_ is not None and list(cmap(p_)) == ["#SkyyPrTCap.Text"], "PUTBACK: a caption only (no slot re-send while the client may still hold the stack)")
    K.eq(at(PI, "storage", 2), ("Wood_Oak_Trunk", 100), "PUTBACK: nothing moved")
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": 2}), "CANCEL pick up")
    one(ev(PI, {"a": "cx", "g": "s"}), "CANCEL")
    K.check(pg.dg is None and ok_line(n0, "inv cancel Wood_Oak_Trunk from storage slot 3 -> back ok"), "CANCEL: the drag is forgotten, logged")
    p_ = one(ev(PI, {"a": "dc", "g": "s", "SlotIndex": 2}), "DOUBLE-CLICK")
    K.check(p_ is not None and list(cmap(p_)) == ["#SkyyPrTCap.Text"], "DOUBLE-CLICK: a caption only")
    one(ev(PI, {"a": "rl", "g": "s", "SlotIndex": 4}), "RELEASE with nothing held")
    one(ev(PI, {"a": "dr", "g": "s", "SlotIndex": 4}), "DROP with no source anywhere")
    K.check(ok_line(n0, "the event names no source and nothing was picked up"), "DROP with no source: nothing moved, logged")
    n0 = mark()
    one(ev(PI, {"a": "sort"}), "SORT")
    K.check(ok_line(n0, "inv sort storage -> storage ok") and totals(PI) == T0, "SORT: storage sorted, totals unchanged")
    one(ev(PI, {"a": "zz"}), "UNKNOWN event (the safety net / say)")
    K.eq(totals(PI), T0, "MOVES: every item total unchanged")
    # drag outside the window = drop (the probe's own path: this player's packet handler is not the game's)
    DROPS = []

    @JImplements("java.util.function.Function")
    class Dropper(object):
        def __init__(self, ok):
            self.ok = ok

        @JOverride
        def apply(self, s):
            DROPS.append((str(s.getItemId()), int(s.getQuantity())))
            return JClass("java.lang.Boolean")(self.ok)
    hap = [i_ for i_ in range(9) if at(PI, "hotbar", i_) and at(PI, "hotbar", i_)[0] == "Plant_Fruit_Apple"][0]
    INVST.DROPPER = Dropper(True)
    n0 = mark()
    one(ev(PI, {"a": "sc", "g": "h", "SlotIndex": hap}), "DROP OUT pick up")
    one(ev(PI, {"a": "dz", "SourceInventorySectionId": -1, "SourceSlotId": hap, "ItemStackId": "Plant_Fruit_Apple", "ItemStackQuantity": 2}), "DROP OUT")
    K.eq((DROPS, tot(PI, "Plant_Fruit_Apple")), ([("Plant_Fruit_Apple", 2)], 31), "DROP OUT: 2 apples dropped at the feet, 2 fewer in the inventory")
    K.check(ok_line(n0, "inv drop-outside h:%d Plant_Fruit_Apple x2 -> world ok (dropped at your feet)" % hap), "DROP OUT: the log line")
    INVST.DROPPER = Dropper(False)
    one(ev(PI, {"a": "sc", "g": "h", "SlotIndex": hap}), "DROP REFUSED pick up")
    pg.lastMoveAt = 0
    one(ev(PI, {"a": "dz", "SourceInventorySectionId": -1, "SourceSlotId": hap, "ItemStackId": "Plant_Fruit_Apple", "ItemStackQuantity": 1}), "DROP REFUSED")
    K.check(tot(PI, "Plant_Fruit_Apple") == 31 and ok_line(n0, "(the drop failed - put back into hotbar)"), "DROP REFUSED: the stack goes back, nothing lost")
    INVST.DROPPER = None
    pg.lastMoveAt = 0
    one(ev(PI, {"a": "dz", "SourceInventorySectionId": -1, "SourceSlotId": hap, "ItemStackId": "Plant_Fruit_Apple", "ItemStackQuantity": 1}), "DROP REAL CALL")
    K.check(tot(PI, "Plant_Fruit_Apple") in (30, 31), "DROP REAL CALL: ItemUtils.dropItem on the stand-in store (dropped or put back - never lost: %d)" % tot(PI, "Plant_Fruit_Apple"))
    T0 = totals(PI)
    # the game's own drop (CORE): the player's packet handler IS an IPacketHandler -> InventoryPacketHandler.handle(DropItemStack) queues the
    # game's world task (not run here: that is the engine's own drop)
    GPHc, GENc = JClass(PH + "server.core.io.handlers.game.GamePacketHandler"), JClass(PH + "server.core.io.handlers.GenericPacketHandler")
    INVPHc = JClass(PH + "server.core.io.handlers.game.InventoryPacketHandler")
    PHc = JClass(PH + "server.core.io.PacketHandler")
    # a GamePacketHandler that forwards its writes to the recording handler (the page / chat packets stay recorded)
    CPx = JClass("javassist.ClassPool").getDefault()
    CPx.appendClassPath(B.SERVER_JAR)
    rg_ = CPx.makeClass("uiprobeharness.RecGame", CPx.get(PH + "server.core.io.handlers.game.GamePacketHandler"))
    rg_.addField(JClass("javassist.CtField").make("public static " + PH + "server.core.io.PacketHandler D;", rg_))
    _pt = [str(x.getName()) for x in list(GPHc.class_.getDeclaredConstructors())[0].getParameterTypes()]
    rg_.addConstructor(JClass("javassist.CtNewConstructor").make("public RecGame() { super(%s); }" % ", ".join("(%s) null" % x for x in _pt), rg_))
    for _m in ("public boolean writePacket(" + PH + "protocol.ToClientPacket p, boolean c) { D.writePacket(p, c); return true; }",
               "public void write(" + PH + "protocol.ToClientPacket p) { D.write(p); }",
               "public void write(" + PH + "protocol.ToClientPacket[] ps) { D.write(ps); }",
               "public void write(" + PH + "protocol.ToClientPacket[] ps, " + PH + "protocol.ToClientPacket p) { D.write(ps, p); }",
               "public void writeNoCache(" + PH + "protocol.ToClientPacket p) { D.writeNoCache(p); }"):
        rg_.addMethod(JClass("javassist.CtNewMethod").make(_m, rg_))
    rg_.writeFile(hcls)
    RGc = JClass("uiprobeharness.RecGame")
    old_ph = PI.pr.getPacketHandler()
    RGc.D = old_ph
    G = Ucls.allocateInstance(RGc.class_)
    E.jf(GPHc.class_, "playerRef").set(G, PI.pr)
    E.run_world(E.W1)
    E.jf(JClass(PH + "server.core.universe.PlayerRef").class_, "packetHandler").set(PI.pr, G)
    n0 = mark()
    pg.lastMoveAt = 0
    pg.handleDataEvent(PI.ref, PI.st, json.dumps({"a": "dz", "SourceInventorySectionId": -1, "SourceSlotId": hap, "ItemStackId": "Plant_Fruit_Apple", "ItemStackQuantity": 1}))
    q_ = E.queued(E.W1)
    K.check(len(q_) == 2 and "InventoryPacketHandler" in q_[0] and q_[1] == "InvTask", "DROP NATIVE: handed to InventoryPacketHandler -> the game's world task queued, then our drop-check (%s)" % q_)
    K.check(ok_line(n0, "(handed to the game's own drop, like the Q key"), "DROP NATIVE: the log line")
    tk_ = list(E.W1.tasks)
    E.W1.tasks.clear()
    f1_ = int(pg.fails)
    n0 = mark()
    tk_[1].run()                                           # the game's task NOT run: nothing left the inventory
    K.check(ok_line(n0, "the game's own drop did NOT drop it (fail; no item lost)") and int(pg.fails) == f1_ + 1, "DROP CHECK: a drop the game did not do is logged as a fail")
    ck_ = JV("InvTask")(3, PI.pr, "h:%d" % hap)
    ck_.pg, ck_.sid, ck_.n0 = pg, "Plant_Fruit_Apple", tot(PI, "Plant_Fruit_Apple") + 1
    n0 = mark()
    ck_.run()
    K.check(ok_line(n0, "Plant_Fruit_Apple: 1 left your inventory - the game's drop ok"), "DROP CHECK: a drop the game did is logged ok")
    E.jf(JClass(PH + "server.core.universe.PlayerRef").class_, "packetHandler").set(PI.pr, old_ph)
    K.eq(totals(PI), T0, "DROP NATIVE: the probe itself took nothing")
    # native packets while the page is open: observed + left to the game; a drag right after a native move is skipped
    E.run_world(E.W1)
    n0 = mark()
    K.check(not bool(INVST.route(PI.pr, MISc(-2, 2, 1, -1, 6), "subhandler")) and not bool(INVST.route(PI.pr, DISc(-1, hap, 1), "adapter"))
            and not bool(INVST.route(PI.pr, SMISc(-2, 2, 1, SMTc.PutInHotbarOrWindow), "subhandler")), "NATIVE: Move / Drop / SmartMove are left to the game")
    K.check(ok_line(n0, "inv native MoveItemStack -2:2 -> -1:6 x1") and ok_line(n0, "inv native DropItemStack section -1") and ok_line(n0, "inv native SmartMoveItemStack"),
            "NATIVE: each one logged")
    K.check(INVST.LASTNATIVE.get(PI.pr.getUuid()) is not None, "NATIVE: the time of the last native move is kept")
    one(drag(PI, "s", 2, "s", 30, iid="Wood_Oak_Trunk")[1], "NATIVE then a drag")
    K.check(at(PI, "storage", 2) == ("Wood_Oak_Trunk", 100) and ok_line(n0, "(skipped: the client sent its own native move"), "NATIVE: a drag right after it is skipped (no double move)")
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": 2, "ShiftHeld": True}), "NATIVE then a shift pick up")
    one(ev(PI, {"a": "rl", "g": "s", "SlotIndex": 2, "ShiftHeld": True}), "NATIVE then a shift release")
    K.check(at(PI, "storage", 2) == ("Wood_Oak_Trunk", 100) and ok_line(n0, "(skipped: the client sent its own native SmartMove"), "NATIVE: a shift-click right after a native SmartMove is skipped")
    INVST.LASTNATIVE.remove(PI.pr.getUuid())
    # fixer 2: a native Move / SmartMove that arrives AFTER our server move (within 1.5 s) is logged as a possible undo + counted as a fail
    sv_ = totals(PI)
    pg.moved("s:1>s:5")
    f1_ = int(pg.fails)
    n0 = mark()
    K.check(not bool(INVST.route(PI.pr, MISc(-2, 1, 1, -2, 5), "subhandler")), "LATE NATIVE: still left to the game")
    K.check(ok_line(n0, "inv native MoveItemStack -2:1 -> -2:5 x1 AFTER a server move (s:1>s:5,") and ok_line(n0, "possible undo") and int(pg.fails) == f1_ + 1,
            "LATE NATIVE: a native Move right after a server move is WARNed as a possible undo and counted as a fail")
    pg.moved("s:1>world")
    n0 = mark()
    INVST.route(PI.pr, SMISc(-2, 2, 1, SMTc.PutInHotbarOrWindow), "subhandler")
    K.check(not ok_line(n0, "AFTER a server move") and int(pg.fails) == f1_ + 1, "LATE NATIVE: not after a drop-outside")
    pg.lastMoveAt = 0
    n0 = mark()
    INVST.route(PI.pr, MISc(-2, 1, 1, -2, 5), "subhandler")
    K.check(not ok_line(n0, "AFTER a server move") and int(pg.fails) == f1_ + 1 and totals(PI) == sv_, "LATE NATIVE: no warning with no recent server move; the probe moved nothing")
    INVST.LASTNATIVE.remove(PI.pr.getUuid())
    # change events: ONE refresh when the items changed outside a click, none when nothing changed
    E.run_world(E.W1)
    E.pump(PI)
    f0 = len(E.sent(PI))
    E.run_world(E.W1)
    K.eq(len([p_ for p_ in E.sent(PI)[f0:] if str(p_.getClass().getSimpleName()) == "CustomPage"]), 0, "REFRESH: our own moves queue no extra packet")
    inv(PI, "storage").addItemStack(ISc("Rock_Stone", 1))
    K.check("InvRefresh" in E.queued(E.W1), "REFRESH: a change event queues ONE refresh on the world thread (%s)" % E.queued(E.W1))
    inv(PI, "hotbar").addItemStack(ISc("Rock_Stone", 1))
    K.eq(E.queued(E.W1).count("InvRefresh"), 1, "REFRESH: a second change before it runs queues nothing more")
    n0 = mark()
    E.run_world(E.W1)
    rp = [p_ for p_ in E.sent(PI)[f0:] if str(p_.getClass().getSimpleName()) == "CustomPage"]
    K.check(len(rp) == 1 and "#SkyyPrIs.Slots" in cmap(rp[0]) and ok_line(n0, "inv refresh: the items changed"), "REFRESH: ONE update re-sent the grids")
    pg.changed()
    E.run_world(E.W1)
    K.eq(len([p_ for p_ in E.sent(PI)[f0:] if str(p_.getClass().getSimpleName()) == "CustomPage"]), 1, "REFRESH: nothing changed = no packet")
    T0 = totals(PI)

    # ---- I3: the Probe Bag
    pk_ = one(ev(PI, {"a": "tbag"}), "BAG tab")
    if pk_ is not None:
        K.check(bool(is_clear(pk_)) and "#SkyyPrIb.Slots" in cmap(pk_) and len(binds_of(pk_)) == 30, "BAG tab: ONE rebuild with the bag grid (30 bindings)")
    K.eq(str(pg.view), "bag", "BAG: the bag view")
    one(ev(PI, {"a": "tbag"}), "BAG tab again (already open)")
    ws_ = [i_ for i_ in range(36) if at(PI, "storage", i_) and at(PI, "storage", i_)[0] == "Wood_Oak_Trunk"][0]
    n0 = mark()
    one(drag(PI, "s", ws_, "b", 3, iid="Wood_Oak_Trunk")[1], "BAG drag in")
    K.check(bag_of(pg).get(3, (None,))[0] == "Wood_Oak_Trunk" and ok_line(n0, "-> b:3 ok"), "BAG: storage -> bag slot 4")
    rs_ = [i_ for i_ in range(36) if at(PI, "storage", i_) and at(PI, "storage", i_)[0] == "Rock_Stone"][0]
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": rs_, "ShiftHeld": True}), "BAG shift pick up")
    one(ev(PI, {"a": "rl", "g": "s", "SlotIndex": rs_, "ShiftHeld": True}), "BAG shift in")
    K.check(any(v_[0] == "Rock_Stone" for v_ in bag_of(pg).values()) and ok_line(n0, "inv shift s:%d Rock_Stone" % rs_), "BAG: shift-click storage -> bag")
    K.eq(totals(PI, pg), T0, "BAG: totals (inventory + bag) unchanged")
    one(ev(PI, {"a": "sc", "g": "b", "SlotIndex": 3}), "BAG out pick up")
    one(ev(PI, {"a": "dr", "g": "s", "SlotIndex": 35}), "BAG out drop (no client source - the bag has no section)")
    K.check(at(PI, "storage", 35) is not None and at(PI, "storage", 35)[0] == "Wood_Oak_Trunk" and 3 not in bag_of(pg), "BAG: bag -> storage by the tracked pick-up")
    rb_ = [i_ for i_, v_ in bag_of(pg).items() if v_[0] == "Rock_Stone"][0]
    one(ev(PI, {"a": "sc", "g": "b", "SlotIndex": rb_, "ShiftHeld": True}), "BAG shift out pick up")
    one(ev(PI, {"a": "rl", "g": "b", "SlotIndex": rb_, "ShiftHeld": True}), "BAG shift out")
    K.check(bag_of(pg) == {} and ok_line(n0, "inv shift b:%d Rock_Stone" % rb_), "BAG: shift-click bag -> storage / hotbar")
    K.eq(totals(PI, pg), T0, "BAG: totals unchanged after in / out")
    # drag from the bag onto the drop zone (the bag has no section: the probe's own drop)
    wz_ = [i_ for i_ in range(36) if at(PI, "storage", i_) and at(PI, "storage", i_)[0] == "Wood_Oak_Trunk"][0]
    one(drag(PI, "s", wz_, "b", 0, iid="Wood_Oak_Trunk")[1], "BAG in again")
    K.check(bag_of(pg).get(0, (None,))[0] == "Wood_Oak_Trunk", "BAG: wood in bag slot 1 again")
    INVST.DROPPER = Dropper(True)
    del DROPS[:]
    one(ev(PI, {"a": "sc", "g": "b", "SlotIndex": 0}), "BAG drop-out pick up")
    one(ev(PI, {"a": "dz", "ItemStackQuantity": 4}), "BAG drop-out")
    K.check(DROPS == [("Wood_Oak_Trunk", 4)] and tot(PI, "Wood_Oak_Trunk", pg) == T0["Wood_Oak_Trunk"] - 4, "BAG: 4 dragged out of the bag = dropped at the feet")
    T0 = totals(PI, pg)
    # every close path returns the bag
    def fill_bag(pg_, PP, n_):
        """n_ stacks into the bag the way the player does it (drag from storage)"""
        moved_ = 0
        for i_ in range(36):
            if moved_ >= n_:
                break
            s_ = at(PP, "storage", i_)
            if s_ is None:
                continue
            pg_.lastMoveAt = 0
            drag(PP, "s", i_, "b", 10 + moved_, iid=s_[0])
            moved_ += 1
        return dict(bag_of(pg_))
    before_ = totals(PI, pg)
    pre_ = len(bag_of(pg))                             # the rest of the wood stack dragged out above is still in the bag
    filled = fill_bag(pg, PI, 3)
    NB = pre_ + 3
    K.eq(len(filled), NB, "BAG: %d stacks in the bag before Esc" % NB)
    n0, f0 = mark(), len(E.sent(PI))
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    K.check(PI.pm.getCustomPage() is None and bool(pg.closed) and bag_of(pg) == {}, "CLOSE Esc: the page is gone, the bag is empty")
    K.eq(totals(PI), before_, "CLOSE Esc: every bag item is back in the inventory (totals equal)")
    K.eq(sum(1 for l in lines_since(n0) if l.startswith("I inv bag-return b:") and "(page closed)" in l), NB, "CLOSE Esc: one bag-return line per stack")
    K.check(("Probe Bag: %d stack(s) went back to your inventory (page closed)." % NB) in pchats(PI, f0), "CLOSE Esc: the chat line")
    K.check(INVST.PAGES.get(PI.pr.getUuid()) is None and pg.regs.isEmpty(), "CLOSE Esc: the page is forgotten, its listeners unregistered")
    n0, f0 = mark(), len(E.sent(PI))
    pg.handleDataEvent(PI.ref, PI.st, json.dumps({"a": "dr", "g": "b", "SlotIndex": 0, "SourceInventorySectionId": -2, "SourceSlotId": 2}))
    K.check(len(E.sent(PI)) == f0 and ok_line(n0, "arrived after the page closed - ignored") and totals(PI) == before_, "AFTER CLOSE: a late click sends nothing, moves nothing")
    # probe off with the page open
    INVCM.tabCmd(PI.ref, PI.st, PI.pr, "on")
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    f0 = len(E.sent(PI))
    INVCM.tabCmd(PI.ref, PI.st, PI.pr, "off")
    K.check(bool(pg.closed) and bag_of(pg) == {} and totals(PI) == before_ and PI.pm.getCustomPage() is None, "CLOSE probe off: the page closes, the bag comes back")
    K.check("TAB OFF" in pchats(PI, f0) and not INVST.TAB.containsKey(PI.pr.getUuid()), "CLOSE probe off: Tab is vanilla again")
    # disconnect (queued on the world) + disconnect with no world reference (kept, given back at the next open)
    PDEc, PREc = JClass(PH + "server.core.event.events.player.PlayerDisconnectEvent"), JClass(PH + "server.core.event.events.player.PlayerReadyEvent")
    INVCM.tabCmd(PI.ref, PI.st, PI.pr, "on")
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    E.run_world(E.W1)
    n0 = mark()
    JV("InvBye")().accept(PDEc(PI.pr))
    K.check(not INVST.TAB.containsKey(PI.pr.getUuid()) and E.queued(E.W1) == ["InvClose"], "CLOSE disconnect: Tab switched off, the bag return queued on the world")
    K.check(ok_line(n0, "inv bag-hold (disconnect) for") and ok_line(n0, "b:10 ") and ok_line(n0, "b:11 "), "CLOSE disconnect: the bag contents are logged before the queued return")
    n0 = mark()
    E.run_world(E.W1)
    K.check(bool(pg.closed) and bag_of(pg) == {} and totals(PI) == before_ and ok_line(n0, "force-closed (disconnect)"), "CLOSE disconnect: the bag comes back")
    # fixer 2 (safety re-check #1): the engine's own removal task is queued AFTER the disconnect event (Universe.removePlayer: dispatch
    # PlayerDisconnectEvent, THEN CompletableFuture.runAsync(remove, world)); the world queue is FIFO - our bag return runs first
    _pool = JClass("javassist.ClassPool")(False)
    _pool.insertClassPath(B.SERVER_JAR)
    _IPc, _PSc, _BOSc = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    def _code(cls_, m_):
        for mm_ in _pool.get(cls_).getDeclaredMethods():
            if str(mm_.getName()) == m_:
                b_ = _BOSc()
                _IPc(_PSc(b_)).print_(mm_)
                return str(b_.toString())
        return ""
    def _order(src_, *needles_):
        at_ = [src_.find(nd_) for nd_ in needles_]
        return all(a_ >= 0 for a_ in at_) and at_ == sorted(at_)
    _rp = _code(PH + "server.core.universe.Universe", "removePlayer")
    K.check(_order(_rp, "PlayerDisconnectEvent.<init>", "IEventDispatcher.dispatch", "World.isInThread", "CompletableFuture.runAsync"),
            "ENGINE ORDER: Universe.removePlayer dispatches PlayerDisconnectEvent BEFORE it queues the player's removal on the world")
    _wx = _code(PH + "server.core.universe.world.World", "execute")
    _wq = _code(PH + "server.core.universe.world.World", "consumeTaskQueue")
    K.check("World.acceptingTasks" in _wx and "Deque.offer" in _wx and "Deque.poll" in _wq, "ENGINE ORDER: World.execute offers to the tail, consumeTaskQueue polls the head (FIFO)")
    _ws = _code(PH + "server.core.universe.world.World", "onShutdown")
    K.check(_order(_ws, "World.consumeTaskQueue", "PlayerRef.removeFromStore"), "ENGINE ORDER: World.onShutdown runs the queued tasks BEFORE it removes the players")
    @JImplements("java.lang.Runnable")
    class EngineRemove(object):
        @JOverride
        def run(self):
            E.jf(JClass(PH + "server.core.universe.PlayerRef").class_, "entity").set(PI.pr, None)
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    E.run_world(E.W1)
    n0 = mark()
    JV("InvBye")().accept(PDEc(PI.pr))
    K.check(E.queued(E.W1) == ["InvClose"], "DISCONNECT ORDER: our bag return is queued during the event, ahead of the engine's removal")
    E.W1.tasks.add(EngineRemove())                             # what Universe.removePlayer queues right after the event
    E.run_world(E.W1)
    E.jf(JClass(PH + "server.core.universe.PlayerRef").class_, "entity").set(PI.pr, PI.ref)
    K.check(bool(pg.closed) and bag_of(pg) == {} and totals(PI) == before_ and INVST.PENDING.get(PI.pr.getUuid()) is None
            and ok_line(n0, "inv bag-return b:10") and not ok_line(n0, "kept in memory"),
            "DISCONNECT ORDER: the bag is back in the inventory before the engine removes (and saves) the player - nothing left in memory")
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    E.run_world(E.W1)
    RUNc = JClass(PH + "server.core.util.thread.TickingThread$Run")
    run_ = Ucls.allocateInstance(RUNc.class_)
    E.jf(RUNc.class_, "thread").set(run_, JClass("java.lang.Thread").currentThread())
    E.jf(TTc.class_, "currentRun").get(E.W1).set(run_)
    n0 = mark()
    JV("InvBye")().accept(PDEc(PI.pr))
    E.jf(TTc.class_, "currentRun").get(E.W1).set(None)
    K.check(E.queued(E.W1) == [] and bool(pg.closed) and bag_of(pg) == {} and totals(PI) == before_ and ok_line(n0, "force-closed (disconnect)"),
            "CLOSE disconnect on the world thread: the bag comes back at once, nothing queued")
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    PRc = JClass(PH + "server.core.universe.PlayerRef")
    E.jf(PRc.class_, "entity").set(PI.pr, None)
    n0 = mark()
    JV("InvBye")().accept(PDEc(PI.pr))
    E.jf(PRc.class_, "entity").set(PI.pr, PI.ref)
    K.check(bag_of(pg) == {} and INVST.PENDING.get(PI.pr.getUuid()) is not None and int(INVST.PENDING.get(PI.pr.getUuid()).size()) == 2
            and ok_line(n0, "kept in memory for your next join"), "CLOSE disconnect without a world: the 2 stacks are kept in memory")
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    K.check(INVST.PENDING.get(PI.pr.getUuid()) is None and totals(PI) == before_, "KEPT: given back when the page opens again (totals equal)")
    # world change: the old world's page hands its bag to the new world's inventory
    ev(PI, {"a": "tbag"})
    fill_bag(pg, PI, 2)
    old_tot = totals(PI, pg)
    PW = E.player(uid=PI.pr.getUuid(), name="SkyyInv", world=E.W2, world_u=E.W2U)
    n0 = mark()
    JV("InvReady")().accept(PREc(PW.ref, PW.pl, 0))
    K.check(bool(pg.closed) and bag_of(pg) == {} and INVST.PAGES.get(PI.pr.getUuid()) is None, "CLOSE world change: the old page closes, its bag empties")
    K.eq(sum(totals(PW).values()) + sum(totals(PI).values()), sum(old_tot.values()), "CLOSE world change: the bag items are in the NEW world's inventory (nothing lost, nothing doubled)")
    K.check(sum(totals(PW).values()) > 0 and ok_line(n0, "(world change)") and ok_line(n0, "kept items delivered"), "CLOSE world change: logged")
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    # a full inventory: overflow at the feet; if the drop is refused, kept in memory and given back at the next ready
    PF2 = E.player(uid=UUIDc(0x52, 0x52), name="SkyyFull")
    put(PF2, "storage", 0, ISc("Plant_Fruit_Apple", 50))
    pgf = INVCM.openInv(PF2.ref, PF2.st, PF2.pr, "test")
    E.pump(PF2)
    ev(PF2, {"a": "tbag"})
    drag(PF2, "s", 0, "b", 0, iid="Plant_Fruit_Apple")
    for f_ in ("storage", "hotbar"):
        ic_ = inv(PF2, f_)
        for i_ in range(int(ic_.getCapacity())):
            ic_.addItemStackToSlot(JShort(i_), ISc("Rock_Stone", 100))
    rocks = E.count(PF2, "Rock_Stone")
    INVST.DROPPER = Dropper(True)
    del DROPS[:]
    PF2.pm.handleLegacyCustomPageEvent(PF2.ref, PF2.st, E.CPE(E.CPT.Dismiss, None))
    K.check(DROPS == [("Plant_Fruit_Apple", 50)] and bag_of(pgf) == {} and E.count(PF2, "Rock_Stone") == rocks, "FULL: the bag stack goes to the feet (inventory full)")
    pgf = INVCM.openInv(PF2.ref, PF2.st, PF2.pr, "test")
    E.pump(PF2)
    ev(PF2, {"a": "tbag"})
    pgf.bag.addItemStack(ISc("Plant_Fruit_Apple", 7))      # (a stack already in the bag - the full inventory leaves no slot to drag from)
    INVST.DROPPER = Dropper(False)
    PF2.pm.handleLegacyCustomPageEvent(PF2.ref, PF2.st, E.CPE(E.CPT.Dismiss, None))
    kept = INVST.PENDING.get(PF2.pr.getUuid())
    K.check(kept is not None and int(kept.size()) == 1 and bag_of(pgf) == {}, "FULL + drop refused: KEPT in memory, not lost")
    inv(PF2, "storage").removeItemStackFromSlot(JShort(4))
    n0 = mark()
    JV("InvReady")().accept(PREc(PF2.ref, PF2.pl, 0))
    K.check(INVST.PENDING.get(PF2.pr.getUuid()) is None and E.count(PF2, "Plant_Fruit_Apple") == 7 and ok_line(n0, "kept items delivered"), "FULL: given back at the next ready, into the freed slot")
    INVST.DROPPER = None
    # shutdown with the page open: the bag return is queued; leftovers in memory are named in the log
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    INVST.pend(UUIDc(9, 9), ISc("Rock_Stone", 3))
    E.run_world(E.W1)
    n0 = mark()
    INVST.shutdown()
    K.check(not bool(INVST.ACTIVE) and INVST.FILTER is None and E.queued(E.W1) == ["InvClose"], "SHUTDOWN: inactive, the adapter filter removed, the bag return queued")
    K.check(ok_line(n0, "inv bag-hold (server stopping) for"), "SHUTDOWN: the bag contents are named before the queued return (a loss would show)")
    K.check(ok_line(n0, "NOT RETURNED (the server stopped; the probe keeps no data) for player 00000000-0000-0009-0000-000000000009: Rock_Stone x3"), "SHUTDOWN: memory-only leftovers are named in the log")
    E.run_world(E.W1)
    K.check(bool(pg.closed) and bag_of(pg) == {} and totals(PI) == before_ and PI.pm.getCustomPage() is None, "SHUTDOWN: the bag comes back, the page closes")
    K.check(not bool(INVST.route(PI.pr, COWc(WTc.PocketCrafting), "subhandler")), "SHUTDOWN: the hooks pass every packet through")
    INVST.PENDING.clear()
    INVST.install()
    SPx = JClass("java.lang.System").getProperties()
    br_ = SPx.get("skyy.bridge")
    made_ = br_ is None
    if made_:
        br_ = JClass("java.util.concurrent.ConcurrentHashMap")()
        SPx.put("skyy.bridge", br_)
    ek_ = "profile:epoch:" + str(PI.pr.getUuid())
    br_.put(ek_, JClass("java.lang.Long").valueOf(3))
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    br_.put(ek_, JClass("java.lang.Long").valueOf(4))
    n0 = mark()
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    K.check(str(pg.epoch0) == "3" and bag_of(pg) == {} and totals(PI) == before_ and ok_line(n0, "profile changed (epoch 3 -> 4)"),
            "PROFILE: a profile switch with items in the bag is WARNed and the items still come back (nothing lost)")
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    fill_bag(pg, PI, 1)
    n0 = mark()
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    K.check(str(pg.epoch0) == "4" and not ok_line(n0, "profile changed"), "PROFILE: same epoch = no warning")
    br_.remove(ek_)
    if made_:
        SPx.remove("skyy.bridge")

    # ---- I2: Tab routing
    E.run_world(E.W1)
    K.check(not bool(INVST.route(PI.pr, COWc(WTc.PocketCrafting), "subhandler")) and E.queued(E.W1) == [], "TAB off: PocketCrafting is left to the game")
    f0 = len(E.sent(PI))
    INVCM.tabCmd(PI.ref, PI.st, PI.pr, "on")
    K.check(INVST.TAB.containsKey(PI.pr.getUuid()) and "TAB ON for you only" in pchats(PI, f0) and "NOT hooked" in pchats(PI, f0), "TAB on: switched on for this player (memory)")
    K.check(not bool(INVST.on(UUIDc(5, 5))), "TAB on: only for the op who switched it on")
    INVCM.tabCmd(PI.ref, PI.st, PI.pr, "maybe")
    K.check("Usage: /uiprobe tab on" in pchats(PI, f0), "TAB: a wrong word = usage")
    s0, n0 = int(INVST.SUB), mark()
    K.check(bool(INVST.route(PI.pr, COWc(WTc.PocketCrafting), "subhandler")), "TAB: PocketCrafting taken by the subhandler")
    K.check(E.queued(E.W1) == ["InvTask"] and int(INVST.SUB) == s0 + 1 and INVST.REDIR.containsKey(PI.pr.getUuid()), "TAB: the redirect is queued on the world thread")
    E.run_world(E.W1)
    pg = PI.pm.getCustomPage()
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "InvPage" and "caught by subhandler" in str(pg.via), "TAB: the probe page opened from the Tab key")
    K.check(ok_line(n0, "Tab (ClientOpenWindow PocketCrafting) caught by subhandler"), "TAB: the log names the hook")
    E.pump(PI)
    o0 = int(INVST.ORPH)
    K.check(bool(INVST.route(PI.pr, CWc(0), "subhandler")) and int(INVST.ORPH) == o0 + 1, "TAB: the orphan CloseWindow 0 is absorbed")
    E.run_world(E.W1)
    K.check(PI.pm.getCustomPage() == pg and not bool(pg.closed), "TAB: ... and the probe page stays open")
    K.check(not bool(INVST.route(PI.pr, CWc(5), "subhandler")) and not bool(INVST.route(PI.pr, COWc(WTc.Container), "subhandler")), "TAB: other windows are left to the game")
    K.check(ok_line(n0, "ClientOpenWindow Container caught by subhandler - not the inventory key"), "TAB: the other window logged")
    INVST.route(PI.pr, COWc(WTc.PocketCrafting), "subhandler")
    n0 = mark()
    E.run_world(E.W1)
    K.check(PI.pm.getCustomPage() is None and bool(pg.closed) and ok_line(n0, "Tab pressed with the probe page open"), "TAB again: the page closes")
    K.check(bool(INVST.route(PI.pr, CWc(0), "subhandler")), "TAB: within 5 s of the redirect a CloseWindow 0 is still absorbed (the page just closed)")
    E.run_world(E.W1)
    INVST.REDIR.put(PI.pr.getUuid(), JClass("java.lang.Long").valueOf(0))
    n0 = mark()
    K.check(not bool(INVST.route(PI.pr, CWc(0), "subhandler")) and not INVST.REDIR.containsKey(PI.pr.getUuid()) and E.queued(E.W1) == []
            and ok_line(n0, "5 s after the redirect - left to the game"), "TAB: a CloseWindow 0 long after the redirect, no page open = the game's (REDIR cleared)")
    # the adapter (a connection the hook missed) - never both
    FL = JV("InvFilter")()
    a0, n0 = int(INVST.ADP), mark()
    K.check(bool(FL.test(PI.pr, COWc(WTc.PocketCrafting))) and int(INVST.ADP) == a0 + 1, "TAB adapter: an unhooked connection is caught by the adapter")
    E.run_world(E.W1)
    K.check(PI.pm.getCustomPage() is not None and ok_line(n0, "caught by adapter"), "TAB adapter: the page opens, logged")
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    INVST.hooked(PI.pr.getPacketHandler())
    K.check(not bool(FL.test(PI.pr, COWc(WTc.PocketCrafting))) and int(INVST.ADP) == a0 + 1 and E.queued(E.W1) == [], "TAB adapter: a hooked connection is NOT routed twice")
    K.check(not bool(FL.test(PI.pr, DISc(-1, 0, 1))), "TAB adapter: inventory packets with no page = left to the game")
    INVST.HOOKED.remove(PI.pr.getPacketHandler())
    # the sub-packet hooks on a GamePacketHandler stand-in (the game's own consumers for ClientOpenWindow / CloseWindow are wrapped)
    REC_N = {"cow": 0, "cw": 0, "mv": 0}

    @JImplements("java.util.function.Consumer")
    class Native(object):
        def __init__(self, k):
            self.k = k

        @JOverride
        def accept(self, p):
            REC_N[self.k] += 1
    G = Ucls.allocateInstance(RGc.class_)
    CONS = JClass("java.util.function.Consumer")
    arr = _JA(CONS)(int(PHc.MAX_PACKET_ID) + 1)
    arr[int(COWc.PACKET_ID)] = Native("cow")
    arr[int(CWc.PACKET_ID)] = Native("cw")
    E.jf(GENc.class_, "handlers").set(G, arr)
    E.jf(GENc.class_, "packetHandlers").set(G, E.ArrayList())
    E.jf(GPHc.class_, "playerRef").set(G, PI.pr)
    IH = INVPHc(G)
    G.registerSubPacketHandler(IH)
    IH.registerHandlers()                                  # the game's own Drop / SmartMove / Move consumers in the table
    arr[int(COWc.PACKET_ID)] = Native("cow")
    arr[int(CWc.PACKET_ID)] = Native("cw")
    K.check(arr[int(DISc.PACKET_ID)] is not None and arr[int(SMISc.PACKET_ID)] is not None, "HOOKS: the game's inventory consumers are in the stand-in's table")
    arr[int(MISc.PACKET_ID)] = Native("mv")                # another mod's wrapper already on Move: ours must chain to it, not cut it off
    i0, n0 = int(INVST.INSTALLS), mark()
    hk = JV("InvHookFactory")().apply(G)
    K.check(str(hk.getClass().getSimpleName()) == "InvHooks", "HOOKS: the factory makes one InvHooks per connection")
    hk.registerHandlers()
    arr2 = E.jf(GENc.class_, "handlers").get(G)
    K.check(all(str(arr2[int(c_.PACKET_ID)].getClass().getSimpleName()) == "InvWrap" for c_ in (COWc, CWc, DISc, SMISc, MISc)),
            "HOOKS: ClientOpenWindow / CloseWindow / Drop / SmartMove / Move are wrapped")
    K.check(bool(INVST.isHooked(G)) and int(INVST.INSTALLS) == i0 + 1 and ok_line(n0, "inv hooks: 5 packet handlers wrapped on a new connection"), "HOOKS: the connection is marked hooked, logged")
    E.run_world(E.W1)
    arr2[int(COWc.PACKET_ID)].accept(COWc(WTc.PocketCrafting))
    K.check(REC_N["cow"] == 0 and E.queued(E.W1) == ["InvTask"], "HOOKS tab on: Tab is taken, the game's own handler NOT called")
    E.run_world(E.W1)
    K.check(PI.pm.getCustomPage() is not None, "HOOKS: the probe page opened through the wrapped handler")
    E.pump(PI)
    arr2[int(CWc.PACKET_ID)].accept(CWc(0))
    arr2[int(CWc.PACKET_ID)].accept(CWc(3))
    K.check(REC_N["cw"] == 1, "HOOKS: CloseWindow 0 absorbed, CloseWindow 3 goes to the game")
    E.run_world(E.W1)
    n0 = mark()
    arr2[int(DISc.PACKET_ID)].accept(DISc(-2, 0, 1))
    q_ = E.queued(E.W1)
    K.check(len(q_) == 1 and "InventoryPacketHandler" in q_[0] and ok_line(n0, "inv native DropItemStack section -2 slot 0 x1 while the probe page is open (subhandler)"),
            "HOOKS: a Drop is observed, then handed to InventoryPacketHandler (%s)" % q_)
    E.W1.tasks.clear()
    arr2[int(SMISc.PACKET_ID)].accept(SMISc(-2, 0, 1, SMTc.PutInHotbarOrWindow))
    K.check(len(E.queued(E.W1)) == 1, "HOOKS: SmartMoveItemStack handed to the game's own consumer (InventoryPacketHandler)")
    E.W1.tasks.clear()
    arr2[int(MISc.PACKET_ID)].accept(MISc(-2, 0, 1, -1, 0))
    K.check(REC_N["mv"] == 1 and E.queued(E.W1) == [], "HOOKS: Move goes to the consumer that was there before (another mod's wrapper is kept)")
    INVST.LASTNATIVE.remove(PI.pr.getUuid())
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    INVCM.tabCmd(PI.ref, PI.st, PI.pr, "off")
    arr2[int(COWc.PACKET_ID)].accept(COWc(WTc.PocketCrafting))
    K.check(REC_N["cow"] == 1 and E.queued(E.W1) == [], "HOOKS tab off: Tab goes to the game's own handler")
    E.jf(GPHc.class_, "playerRef").set(G, None)
    arr2[int(CWc.PACKET_ID)].accept(CWc(0))
    K.check(REC_N["cw"] == 2, "HOOKS: no player ref = the game's own handler")
    G2 = Ucls.allocateInstance(GPHc.class_)
    E.jf(GENc.class_, "handlers").set(G2, _JA(CONS)(int(PHc.MAX_PACKET_ID) + 1))
    E.jf(GENc.class_, "packetHandlers").set(G2, E.ArrayList())
    n0 = mark()
    JV("InvHooks")(G2).registerHandlers()
    K.check(not bool(INVST.isHooked(G2)) and ok_line(n0, "inv hooks: 0 packet handlers wrapped on a new connection - the Tab hook is MISSING"), "HOOKS: a connection without the natives is not marked hooked (the adapter covers it)")
    JV("InvHookFactory")().apply(MSGc.raw("not a handler")).registerHandlers()
    K.check(True, "HOOKS: a non-game handler = an InvHooks that does nothing")
    K.notes.append("INV: moves %d, fails %d; SUB %d ADP %d ORPH %d NATIVE %d INSTALLS %d; dropped %s" % (
        int(pg.moves), int(pg.fails), int(INVST.SUB), int(INVST.ADP), int(INVST.ORPH), int(INVST.NATIVE), int(INVST.INSTALLS), list(INVST.DROPPED)[:6]))
'''
H = rep(H, '''    K.notes.append("X: %d log lines; asset sends %d" % (len(tail()), int(RTP.SENT)))''',
        INV_TEST + '''    K.notes.append("X: %d log lines; asset sends %d" % (len(tail()), int(RTP.SENT)))''')

# C: the non-class entries: manifest + the 14 case pages (title line 0.9 -> 0.10) + the 2 new page data files + the drop zone picture
_cmpbody_old = H[H.index('def run_cmp(out):'):H.index("WORLD = \"NewBetaTest\"")]
H = rep(H, _cmpbody_old, '''def run_cmp(out):
    """C: HK.run_compare (byte code of every class vs the 0.9 jar) - its non-class rule allows manifest.json only; here: the 14 case pages
    differ by exactly ONE line each (the title 'SkyyUiProbe 0.9 - ...' -> '0.10 - ...'), and the jar ADDS the two inventory page data files
    + the drop zone's transparent picture. Checked here, line by line, then that one expected FAIL is cleared."""
    HK.run_compare(out, JAR, OLD_JAR, PKG, CMP_EXPECT, CMP_ADDED)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    na = [n for n in za.namelist() if not n.endswith(".class")]
    nb = [n for n in zb.namelist() if not n.endswith(".class")]
    ch = sorted(n for n in set(na) | set(nb) if n not in na or n not in nb or za.read(n) != zb.read(n))
    added = sorted(n for n in ch if n not in na)
    pages = [n for n in ch if n != "manifest.json" and n in na]
    good = ("manifest.json" in ch and len(pages) == 14 and all(n.startswith("com/skyy/uiprobe/pages/") and n in nb for n in pages)
            and added == ["Common/UI/Custom/SkyyUiProbe/Inv/Clear@2x.png", "com/skyy/uiprobe/pages/inv.txt", "com/skyy/uiprobe/pages/invbag.txt"]
            and not [n for n in na if n not in nb])
    for n in pages if good else []:
        a_, b_ = za.read(n).decode("utf-8").split("\\n"), zb.read(n).decode("utf-8").split("\\n")
        dl = [(x, y) for x, y in zip(a_, b_) if x != y]
        good = good and len(a_) == len(b_) and dl == [("S\\t#SkyyPrTitle.Text\\tSkyyUiProbe 0.9 - UI queue probe", "S\\t#SkyyPrTitle.Text\\tSkyyUiProbe 0.10 - UI queue probe")]
    fl = [f for f in d["fails"] if f.startswith("C: non-class entries changed")]
    if good and len(fl) == 1:
        d["fails"].remove(fl[0])
        d["ok"] += 1
        d["notes"].append("C: non-class entries: manifest.json + the 14 case pages (ONLY their title line 0.9 -> 0.10) + added %s" % added)
    else:
        d["fails"].append("C: the non-class entries differ from the expected (changed %s, added %s)" % (pages[:4], added))
    json.dump(d, open(out, "w"), indent=1)


''')
# LIVE: + the event registry capture, the ServerManager stand-in, the adapter list
H = rep(H, '''    sub-commands); shutdown() between; the copy is byte + time identical after both starts and no data folder appears."""''',
        '''    sub-commands); shutdown() between; the copy is byte + time identical after both starts and no data folder appears.
    0.10: + a capturing EventRegistry (the disconnect + ready listeners registered each start), a ServerManager stand-in (the sub-packet
    handler factory registered ONCE per server run), the PacketAdapters inbound list (our filter added at setup, removed at shutdown)."""''')
H = rep(H, '''    CAPC = JClass("uiprobeharness.CaptureCmds")''', '''    re_ = CPj.makeClass("uiprobeharness.CaptureEvents", CPj.get("com.hypixel.hytale.event.EventRegistry"))
    re_.addField(JClass("javassist.CtField").make("public static java.util.List CAP = new java.util.ArrayList();", re_))
    re_.addConstructor(JClass("javassist.CtNewConstructor").make("public CaptureEvents() { super((java.util.List) null, (java.util.function.BooleanSupplier) null, "
                                                                   "(String) null, (com.hypixel.hytale.event.IEventRegistry) null); }", re_))
    re_.addMethod(JClass("javassist.CtNewMethod").make("public com.hypixel.hytale.event.EventRegistration registerGlobal(Class c, java.util.function.Consumer k) {"
                                                       " CAP.add(c.getName() + \\" \\" + k.getClass().getName()); return null; }", re_))
    re_.writeFile(hcls)
    CAPC = JClass("uiprobeharness.CaptureCmds")
    CAPE = JClass("uiprobeharness.CaptureEvents")
    SMc = JClass("com.hypixel.hytale.server.core.io.ServerManager")
    PADc = JClass("com.hypixel.hytale.server.core.io.adapter.PacketAdapters")''')
H = rep(H, '''    s0 = snap()
    roots = []
    for n_ in range(2):
        CAPC.CAP.clear()''', '''    s0 = snap()
    roots = []
    sm_ = U.allocateInstance(SMc.class_)
    fsub = SMc.class_.getDeclaredField("subPacketHandlers")
    fsub.setAccessible(True)
    fsub.set(sm_, JClass("java.util.concurrent.CopyOnWriteArrayList")())
    fins = SMc.class_.getDeclaredField("instance")
    fins.setAccessible(True)
    fins.set(None, sm_)
    finb = PADc.class_.getDeclaredField("inboundHandlers")
    finb.setAccessible(True)
    inb0 = int(finb.get(None).size())
    evs, inbs = [], []
    for n_ in range(2):
        CAPC.CAP.clear()
        CAPE.CAP.clear()''')
H = rep(H, '''        setf(p_, "shutdownTasks", JClass("java.util.concurrent.CopyOnWriteArrayList")())''',
        '''        setf(p_, "shutdownTasks", JClass("java.util.concurrent.CopyOnWriteArrayList")())
        setf(p_, "eventRegistry", U.allocateInstance(CAPE.class_))''')
H = rep(H, '''        roots.append(list(CAPC.CAP))''', '''        roots.append(list(CAPC.CAP))
        evs.append([str(x) for x in CAPE.CAP])
        inbs.append(int(finb.get(None).size()))''')
H = rep(H, '''    ready = [m_ for m_ in records() if "[SkyyUiProbe] %s ready" % VERSION in m_]''',
        '''    K.eq(int(finb.get(None).size()), inb0, "LIVE: shutdown removed our adapter filter each time (inbound list back to %d)" % inb0)
    K.eq(inbs, [inb0 + 1, inb0 + 1], "LIVE: each start adds ONE inbound filter")
    K.eq(int(fsub.get(sm_).size()), 1, "LIVE: the sub-packet handler factory is registered ONCE per server run (2 starts)")
    if int(fsub.get(sm_).size()) == 1:
        K.eq(str(fsub.get(sm_).get(0).getClass().getSimpleName()), "InvHookFactory", "LIVE: ... it is ours")
    for n_, ev_ in enumerate(evs):
        K.eq(sorted(e_.split(" ")[0].rsplit(".", 1)[-1] + " " + e_.split(" ")[1].rsplit(".", 1)[-1] for e_ in ev_),
             ["PlayerDisconnectEvent InvBye", "PlayerReadyEvent InvReady"], "LIVE: start %d registers the disconnect + world-change listeners" % (n_ + 1))
    ready = [m_ for m_ in records() if "[SkyyUiProbe] %s ready" % VERSION in m_]''')
H = rep(H, '''    K.check(bool(ready) and "/uiprobe tip / tiplater / tipgear" in ready[0], "LIVE: the ready line names the tip probe: %s" % (ready[:1] or [None])[0])''',
        '''    K.check(bool(ready) and "/uiprobe tip / tiplater / tipgear" in ready[0] and "/uiprobe inv, /uiprobe tab on|off" in ready[0],
            "LIVE: the ready line names the tip probe + the inventory probe: %s" % (ready[:1] or [None])[0])''')
H = rep(H, '''            K.eq(sorted(str(k) for k in r_.getSubCommands().keySet()), ["tip", "tiplater"], "LIVE: start %d sub-commands" % (n_ + 1))''',
        '''            K.eq(sorted(str(k) for k in r_.getSubCommands().keySet()), ["tab", "tip", "tiplater"], "LIVE: start %d sub-commands" % (n_ + 1))''')
# J: + the inventory page data files and the build's second withMetadata (the grid copy, metadata stripped)
H = rep(H, '''    K.eq(len(re.findall(r"\\.withMetadata\\(", _src)), 1, "J: ONE withMetadata in the build (the fresh probe stack only)")''',
        '''    K.eq(len(re.findall(r"\\.withMetadata\\(", _src)), 2, "J: TWO withMetadata in the build: the fresh probe stack + the grid copy")
    K.check("g.setItemStack(s.withMetadata((@BSON@) null));" in _src, "J: ... the grid copy STRIPS the metadata (I4)")''')
H = rep(H, '''         sorted("com/skyy/uiprobe/pages/%s.txt" % c for c in [c[0] for c in D["cases"]] + ["nodes"]), "J: page data files")''',
        '''         sorted("com/skyy/uiprobe/pages/%s.txt" % c for c in [c[0] for c in D["cases"]] + ["nodes", "inv", "invbag"]), "J: page data files")
    for k_ in ("inv", "invbag"):
        K.check("_" not in "".join(D["inv"]["pages"][k_]["ids"]) and D["inv"]["pages"][k_]["elements"] <= 1600, "J: %s ids hold no underscore, <= 1600 elements" % k_)
        t_ = z.read("com/skyy/uiprobe/pages/%s.txt" % k_).decode("utf-8")
        K.check("InventorySectionId" not in t_ and "SkyyUiProbe/Inv/Clear.png" in t_ and ("#SkyyPrIb" in t_) == (k_ == "invbag"), "J: %s markup (section ids set at run time, the drop zone, the bag only in invbag)" % k_)''')
save("test_skyyuiprobe_0.10.py", H)
