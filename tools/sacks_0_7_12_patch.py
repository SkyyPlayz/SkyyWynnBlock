"""Derive SkyySacks/build_skyysacks_0.7.12.py from the SET pin 0.7.11 (edit THIS file, then regenerate: python tools/sacks_0_7_12_patch.py).
0.7.12 = BAGS IN BENCH AND POCKET CRAFTING (Skyy in game with 0.7.10: "neither inventory or bench crafting pull from the bags").
Diagnosis + fix recipe: research/Bag-Craft-Link-Fix.md (proven against the live HytaleServer.jar). Every engine fact this build relies on is
re-checked at build time (_engine_facts in the generated script) and the build stops when one changed.
 A. BENCH DISPLAY - outbound packet filter. A bench learns extra materials ONLY from the ExtraResources list of an OpenWindow / UpdateWindow,
    and WindowManager.updateWindow sends that list only for an INVALID section (0.7.10 marked it valid, then updated: no list = "Stick 0/4",
    CRAFT greyed). CraftPacketFilter (PlayerPacketFilter, PacketAdapters.registerOutbound in start(), deregistered in shutdown()) hands
    every OpenWindow / UpdateWindow that carries a list to BenchLink.outbound -> onExtras (world thread only - Store.isInThread, else skipped
    and logged once): window by id; only SimpleCraftingWindow / ProcessingBenchWindow (Diagram / Structural benches use their own slots);
    key = SackPool.settledKey (null = vanilla only); no carried bag = vanilla only (a mirror it used is synced + emptied); else the section the
    vanilla code just fed (valid - no re-feed) gets the player's bag mirror ATTACHED: sync -> rebuild -> container Combined{vanilla chests,
    guard} (just the guard without chests) -> extra materials = vanilla list + mirror list summed by id -> valid; the packet's list becomes the
    merged one (new ItemQuantity objects, the vanilla array is never edited). The filter ALWAYS returns false (true would drop the packet).
 B. BagMirror - the GUARD: MirrorGuard extends DelegateItemContainer with FilterType.ALLOW_OUTPUT_ONLY wraps the mirror's container; only the
    guard is ever put on a section (crafts remove through it, inserts are refused - a raw container would accept inserts the next rebuild
    wipes = item loss). owns(c) (containsContainer), static merge(a, b), fit(id) (trim to the pool, never booked), rebuild keeps a content
    version (ver) that windows compare. One mirror per key, its container reused in place. park = sync, empty, invalidate each open window
    using it.
 C. CraftLinkTask keeps its 300 ms task but never marks a section valid or sends a window update itself: BenchLink.link books what benches
    took (sync), then for each open bench / pocket window asks for a vanilla refresh (invalidateExtraResources - the vanilla code re-feeds
    and sends, the filter re-attaches) only when it is stale: the pool changed AND the rebuilt mirror differs from what the window was given
    (a per-key change counter SackPool.CHG, bumped in SackPool.add - every pool writer goes through add), the carried bags changed, the key
    changed, an old mirror still hangs on it, or the filter never saw it; at most once a second per window. Windows that are invalid already
    are skipped (a refresh is on its way - and getExtraResourcesSection() is never called on an invalid bench section: that would re-feed
    without a packet). No crafting window open = synced, emptied, dropped. Every bench window with a mirror gets a close hook (Window.
    registerCloseEvent -> MirrorClose): at close (after the vanilla refund of a started timed unit) the mirror is synced at once.
 D. POCKET CRAFTING - PocketCraftWindow extends FieldCraftingWindow implements MaterialContainerWindow (own section, starts invalid):
    getExtraResourcesSection() refills when invalid (settled key + carried bags -> the shared mirror attached with the Fieldcraft recipes'
    inputs first; else an empty section), invalidateExtraResources() = section invalid + window dirty, handleAction crafts a known recipe
    through CraftingManager.craftItem from Combined{InventoryComponent.getCombined(BACKPACK_STORAGE_HOTBAR), the section's container} (the
    vanilla FieldCraftingWindow path + the section), plays the vanilla craft sound, invalidates. PocketSupplier is swapped into
    Window.CLIENT_REQUESTABLE_WINDOW_TYPES for WindowType.PocketCrafting in start() (warned when nothing was registered before) and the
    previous supplier restored in shutdown(); the 300 ms task warns once if another mod replaced ours later.
 E. PRE-CRAFT HARDENING - inbound CraftInFilter: a SendWindowAction with CraftRecipeAction / TierUpgradeAction for a bench window queues a
    PreCraftTask on the player's world BEFORE the vanilla handler's task (the inbound filter runs on the network thread before
    PacketHandler.handle queues the handler; World.execute is a FIFO deque) - it re-feeds + attaches when the section is invalid or not ours,
    so a second click in the same tick still sees the bags (else it would fail silently - never an item loss).
 LIVE-MIRROR RULE (replaces 0.7.11's refill pause while a bench window is open): the mirror never offers more than the pool holds. Every pool
    writer that takes items OUT of the pool (withdraw clicks / Pick up all, the stack refill) first books what a bench / pocket craft already
    took from the mirror (BagMirror.beforeTake = sync) and right after the move trims the mirror to the pool (BagMirror.afterTake = fit).
    So the refill now runs while a bench is open (the 0.7.11 PENDQ / benchFed pause is gone) and the same items can never be used twice.
 WORDING (0.7.11 removed it on purpose - now true): the refill help lines under the bag page row, the "no bag" view's hint and the ready log
    line say that benches and inventory crafting use the bags you carry; /craft stays the fallback (unchanged).
 SERVER SETUP: new row bags.benchChests "Bench chest count fallback" (default OFF) for the doc's client risk 2: ON = a bench whose bags are
    linked reports at least 1 nearby chest (window data + the packet), in case the client ignores the list when the count is 0.
Safety: SackPool.add logs a warning when a booking would drive a pool below zero (it was silently clamped) - an accounting error signal.
DECISIONS made while building (see the build report): one mirror per key is shared by every crafting window of the player (bench, pocket,
/craft) and rebuilt with the UNION of the open windows' recipe inputs, so two windows never rebuild it against each other; a refresh is
asked only when what a window shows really changed (the 300 ms task rebuilds after a pool change and compares the content version); a
declined window (no settled key / no bag) syncs and EMPTIES the mirror it used (bags only work while carried - an old combined container a
queued timed job holds then finds nothing); every attach first retires another key's mirror (a quick profile switch before the 300 ms task
ran); start() undoes an earlier start (a second registration would merge the bags twice into every list); the pocket "attached" log line is
written once per player and server start (the pocket window is made anew each time the inventory opens).
KNOWN EDGES (documented, not changed): a bench / pocket window shows what the mirror holds (36 slots, at most 4 stacks per item, recipe inputs
first; it refills after every craft - research doc risk 5); a tier upgrade that finishes right after a vanilla re-feed (rare) takes from the
inventory + chests only and may fail (never an item loss); if the client keeps window 0 registered while the inventory is closed, a shown bag
item that changes still sends at most one window-0 update a second (bandwidth only); UNVERIFIED client behaviour: research doc risks 1-3.
REVIEW FIXES (review of 0.7.12: PASS, no item loss / duplication found; these are its hardening findings):
 1. Server Setup row bags.pocketCraft "Bags in inventory crafting" (default ON, live) = the OFF SWITCH of the pocket crafting swap (every
    player's window-0 update now carries an extra-materials list - vanilla sends none - and no client has been seen handling that yet).
    SackCfg.reload reads it from config.properties in setup(), BEFORE start(), so an owner whose clients break on inventory open turns it
    off by editing the file (no join needed); pocketStart() checks it; a live change (the row's after= hook, a hand edit through reload,
    the 300 ms link as a backstop) swaps the vanilla window back / ours in (BenchLink.pocketApply: synchronized, only between start() and
    stop()); an open pocket window declines (empty section) on its next refresh. The texts follow the switch (off: "Benches use your bags").
 2. A DECLINED bench window (no settled key / no bag carried) gets its close hook too (onExtras hooks before its decline return, the 300 ms
    link hooks a bench it makes a record for): its LinkRec + Window no longer outlive a disconnect (prune only runs for online players).
    Not the KeptQuit alternative: the disconnect event's order against closeAllWindows is unverified, and a record dropped before the
    close hooks run would skip the close-time booking.
 3. (harness) the item-conservation fuzz books with DELAYED syncs (no syncAll after each step; conservation corrected by the unbooked use;
    a no-sync audit: container <= table per slot, tables per key <= the pool) + deterministic checks in which the syncs of preCraft's
    owns-branch, decline and park are the ones that book (the old V park check was vacuous).
 4. BagMirror.rebuild skips a pool entry whose item is no longer loaded (ProcBench.item = the Item asset map: null for an id of a removed
    pack mod) - it stays in the pool, it is never offered to a bench, pocket crafting or /craft (the client's answer to an unknown itemId
    in an extra-materials list is unknown).
 Review 5 (the wording ships before the in-game test): kept, as the task asks, and tied to switch 1; a failed bench test means rolling back
    to 0.7.11, whose jar carries the old wording. Review 6 (the client's "nearby chests" tooltip) / 7 (documented edges): nothing to change.
Unchanged: item classification, recipes, assets (only the manifest version), the Workbench tab, /craft (shares the mirror; a /craft rebuild
bumps the version, so an open bench refreshes), Furnace / Tannery, kept counts, bags add up.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.11.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.12.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:90]
    assert count != 1 or s.count(old) == 1, "anchor not unique: " + old[:90]
    s = s.replace(old, new, count)


assert 'VERSION = "0.7.11"' in s and "RefillPref" in s and "benchFed" in s and "BenchLink" not in s and "MirrorGuard" not in s, \
    "the source must be the generated 0.7.11 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")

# ================= docstring + version =================
rep('"""SkyySacks 0.7.11 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.11.py           -> SkyySacks/SkyySacks-0.7.11.jar' + LF
    + '       python build_skyysacks_0.7.11.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world' + LF,
    '"""SkyySacks 0.7.12 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.12.py           -> SkyySacks/SkyySacks-0.7.12.jar' + LF
    + '       python build_skyysacks_0.7.12.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world' + LF)
rep('SackPool.CLOSED (settledKey); an empty metadata document counts as none. Known edges: tools/sacks_0_7_11_patch.py docstring.' + LF + '"""' + LF,
    'SackPool.CLOSED (settledKey); an empty metadata document counts as none. Known edges: tools/sacks_0_7_11_patch.py docstring.' + LF
    + '0.7.12 (derived from 0.7.11 by tools/sacks_0_7_12_patch.py - edit the patch, not this file; research/Bag-Craft-Link-Fix.md): BENCHES AND' + LF
    + 'INVENTORY CRAFTING USE THE BAGS. (A) an outbound packet filter (CraftPacketFilter) merges the bag mirror into every bench OpenWindow /' + LF
    + 'UpdateWindow extra-materials list and attaches the mirror to the section the vanilla code just fed (world thread, always returns false);' + LF
    + '(B) the mirror is attached only through an output-only guard (MirrorGuard: crafts remove, inserts refused), one mirror per key, park' + LF
    + 'invalidates; (C) the 300 ms CraftLinkTask (BenchLink.link) books bench use and asks for a vanilla refresh only when a window is stale' + LF
    + '(pool counter SackPool.CHG + a changed mirror, carried bags, key, foreign mirror) at most once a second - it never marks a section valid' + LF
    + 'or sends updates itself; close hooks book at once; (D) PocketCraftWindow (pocket crafting with its own section, swapped into' + LF
    + 'Window.CLIENT_REQUESTABLE_WINDOW_TYPES, restored at shutdown); (E) an inbound filter queues a PreCraftTask before a bench craft click' + LF
    + 'so a second click in the same tick sees the bags. Live-mirror rule: withdraws and the stack refill book mirror use first and trim the' + LF
    + 'mirror to the pool after (the 0.7.11 refill pause is gone). Texts say benches and inventory crafting use the bags you carry. Server' + LF
    + 'Setup row bags.benchChests (bench chest count fallback, off). Engine facts re-checked at build time (_engine_facts). One mirror per' + LF
    + 'key shared by bench / pocket / /craft (rebuilt for the union of the open windows\' inputs); a declined window empties it; every attach' + LF
    + 'retires another key\'s mirror first; start() undoes an earlier start. Decisions + known edges: tools/sacks_0_7_12_patch.py docstring.' + LF
    + 'Review fixes: Server Setup bags.pocketCraft (default on, live) = the off switch of the pocket crafting swap, read from config.properties' + LF
    + 'before start(); a declined bench window gets its close hook too; rebuild never offers an id the Item asset map no longer knows.' + LF
    + '"""' + LF)
rep('VERSION = "0.7.11"', 'VERSION = "0.7.12"')

# ================= engine class names + jt tokens (0.7.12) =================
rep('PDE = "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent"   # 0.7.11: KeptQuit (relog resets the kept counts)' + LF,
    'PDE = "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent"   # 0.7.11: KeptQuit (relog resets the kept counts)' + LF
    + '# 0.7.12 (research/Bag-Craft-Link-Fix.md): the bench / pocket crafting link (VERIFIED against the live HytaleServer.jar; _engine_facts)' + LF
    + 'SCW = "com.hypixel.hytale.builtin.crafting.window.SimpleCraftingWindow"' + LF
    + 'PBW = "com.hypixel.hytale.builtin.crafting.window.ProcessingBenchWindow"' + LF
    + 'FCW = "com.hypixel.hytale.builtin.crafting.window.FieldCraftingWindow"' + LF
    + 'DIC = "com.hypixel.hytale.server.core.inventory.container.DelegateItemContainer"' + LF
    + 'FT  = "com.hypixel.hytale.server.core.inventory.container.filter.FilterType"' + LF
    + 'EIC = "com.hypixel.hytale.server.core.inventory.container.EmptyItemContainer"' + LF
    + 'PPF = "com.hypixel.hytale.server.core.io.adapter.PlayerPacketFilter"' + LF
    + 'PFI = "com.hypixel.hytale.server.core.io.adapter.PacketFilter"' + LF
    + 'PAD = "com.hypixel.hytale.server.core.io.adapter.PacketAdapters"' + LF
    + 'PKT = "com.hypixel.hytale.protocol.Packet"' + LF
    + 'UW  = "com.hypixel.hytale.protocol.packets.window.UpdateWindow"' + LF
    + 'OW  = "com.hypixel.hytale.protocol.packets.window.OpenWindow"' + LF
    + 'ER  = "com.hypixel.hytale.protocol.ExtraResources"' + LF
    + 'SWA = "com.hypixel.hytale.protocol.packets.window.SendWindowAction"' + LF
    + 'CRA = "com.hypixel.hytale.protocol.packets.window.CraftRecipeAction"' + LF
    + 'TUA = "com.hypixel.hytale.protocol.packets.window.TierUpgradeAction"' + LF
    + 'WA  = "com.hypixel.hytale.protocol.packets.window.WindowAction"' + LF
    + 'WT  = "com.hypixel.hytale.protocol.packets.window.WindowType"' + LF
    + 'INVC = "com.hypixel.hytale.server.core.inventory.InventoryComponent"' + LF
    + 'CAC = "com.hypixel.hytale.component.ComponentAccessor"' + LF
    + 'SNDU = "com.hypixel.hytale.server.core.universe.world.SoundUtil"' + LF
    + 'TAI = "com.hypixel.hytale.server.core.util.TempAssetIdUtil"' + LF
    + 'SCAT = "com.hypixel.hytale.protocol.SoundCategory"' + LF
    + 'EVR = "com.hypixel.hytale.event.EventRegistration"' + LF
    + 'JSO = "com.google.gson.JsonObject"' + LF
    + 'JPR = "com.google.gson.JsonParser"' + LF)
rep('''       "PDE": PDE, "WM": WM, "MCW": MCW}   # 0.7.11 (+ WM / MCW: SweepTask.benchFed, review fix 9)''',
    '''       "PDE": PDE, "WM": WM, "MCW": MCW,   # 0.7.11 (+ WM / MCW: SweepTask.benchFed, review fix 9)
       # 0.7.12: the bench / pocket crafting link (BenchLink, the packet filters, PocketCraftWindow, MirrorGuard)
       "SCW": SCW, "PBW": PBW, "FCW": FCW, "DIC": DIC, "FT": FT, "EIC": EIC, "PPF": PPF, "PFI": PFI, "PAD": PAD, "PKT": PKT, "UW": UW,
       "OW": OW, "ER": ER, "SWA": SWA, "CRA": CRA, "TUA": TUA, "WA": WA, "WT": WT, "INVC": INVC, "CAC": CAC, "SNDU": SNDU, "TAI": TAI,
       "SCAT": SCAT, "EVR": EVR, "JSO": JSO, "JPR": JPR, "IQ": IQ, "MERS": MERS, "WIN": WIN, "CIC": CIC, "CRM": CRM, "BTP": BTP,
       "UNI": UNI, "WLD": WLD}''')

# ================= API probes + the engine facts the link relies on (0.7.12) =================
rep('''             (INV, "getHotbar"), (INV, "getBackpack"), (PLA, "getWindowManager"), (WM, "getWindows"), ("org.bson.BsonDocument", "isEmpty")):
    B.probe(pool, c, m)
''', '''             (INV, "getHotbar"), (INV, "getBackpack"), (PLA, "getWindowManager"), (WM, "getWindows"), ("org.bson.BsonDocument", "isEmpty")):
    B.probe(pool, c, m)
# 0.7.12 (research/Bag-Craft-Link-Fix.md, VERIFIED bytecode 2026-10-02): the public members the bench / pocket link calls
for c, m in ((PAD, "registerOutbound"), (PAD, "deregisterOutbound"), (PAD, "registerInbound"), (PAD, "deregisterInbound"), (PPF, "test"),
             (UW, "extraResources"), (UW, "windowData"), (UW, "id"), (OW, "extraResources"), (OW, "windowData"), (OW, "id"), (ER, "resources"),
             (IQ, "itemId"), (IQ, "quantity"), (SWA, "action"), (SWA, "id"), (CRA, "recipeId"), (CRA, "quantity"), (MERS, "toPacket"),
             (MERS, "setValid"), (MERS, "isValid"), (MERS, "setItemContainer"), (MERS, "setExtraMaterials"), (MCW, "invalidateExtraResources"),
             (MCW, "getExtraResourcesSection"), (MCW, "isValid"), (WIN, "CLIENT_REQUESTABLE_WINDOW_TYPES"), (WIN, "registerCloseEvent"),
             (WIN, "getData"), (WIN, "getPlayerRef"), (WM, "getWindow"), (FCW, "handleAction"), (FCW, "onClose0"), (FCW, "onOpen0"),
             (DIC, "setGlobalFilter"), (FT, "ALLOW_OUTPUT_ONLY"), (EIC, "INSTANCE"), (IC, "containsContainer"), (CIC, "getContainersSize"),
             (CIC, "getContainer"), (CRM, "craftItem"), (CRM, "getComponentType"), (INVC, "getCombined"), (INVC, "BACKPACK_STORAGE_HOTBAR"),
             ("com.hypixel.hytale.component.Store", "isInThread"), (SNDU, "playSoundEvent2d"), (TAI, "getSoundEventIndex"),
             (WT, "PocketCrafting"), (JPR, "parseString"), (JSO, "addProperty"), (WLD, "execute"), (CRR, "getAssetMap")):
    B.probe(pool, c, m)


# 0.7.12: the ENGINE FACTS of research/Bag-Craft-Link-Fix.md, read from the server jar's bytecode at build time (in order); a server update
# that changes one of them stops the build instead of shipping a link that silently does nothing (or worse).
def _engine_facts():
    from jpype import JClass
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def code(cls, meth, sig=None):
        for mm in pool.get(cls).getDeclaredMethods():
            if str(mm.getName()) == meth and (sig is None or sig in str(mm.getSignature())):
                mi = mm.getMethodInfo()
                ca = mi.getCodeAttribute()
                cp = mi.getConstPool()
                it = ca.iterator()
                out = []
                while it.hasNext():
                    pos = it.next()
                    out.append(str(IP.instructionString(it, pos, cp)))
                return "\\n".join(out)
        raise SystemExit("0.7.12 engine check: %s.%s not found in the server jar" % (cls, meth))

    def in_order(txt, needles):
        i = 0
        for nd in needles:
            j = txt.find(nd, i)
            if j < 0:
                return nd
            i = j + len(nd)
        return None
    W = "com.hypixel.hytale.server.core.entity.entities.player.windows."
    facts = [
        ("PacketHandler.writePacket runs the outbound filters first (before caching / serializing)",
         "com.hypixel.hytale.server.core.io.PacketHandler", "writePacket", None, ["PacketAdapters.__handleOutbound", "ireturn", "getChannel"]),
        ("WindowManager.updateWindow sends the extra-materials list ONLY for an invalid section",
         WM, "updateWindow", None, ["MaterialContainerWindow.isValid", "ifne", "getExtraResourcesSection", "toPacket", "UpdateWindow.<init>", "writeNoCache"]),
        ("WindowManager.openWindow always sends the list", WM, "openWindow", None, ["getExtraResourcesSection", "toPacket", "OpenWindow.<init>"]),
        ("WindowManager.clientOpenWindow (window 0) sends the list of a MaterialContainerWindow",
         WM, "clientOpenWindow", None, ["CLIENT_REQUESTABLE_WINDOW_TYPES", "onOpen", "consumeIsDirty", "MaterialContainerWindow.getExtraResourcesSection", "toPacket"]),
        ("BenchWindow.getExtraResourcesSection re-feeds the vanilla chests only when the section is invalid",
         "com.hypixel.hytale.builtin.crafting.window.BenchWindow", "getExtraResourcesSection", None,
         ["MaterialExtraResourcesSection.isValid", "ifne", "feedExtraResourcesSection"]),
        ("CraftingManager.feedExtraResourcesSection replaces the container + list and marks the section valid",
         CRM, "feedExtraResourcesSection", None, ["setItemContainer", "setExtraMaterials", "setValid"]),
        ("SimpleCraftingWindow.handleAction crafts from Combined{inventory BACKPACK_STORAGE_HOTBAR, the section container}, then invalidates",
         SCW, "handleAction", None, ["CraftRecipeAction", "BACKPACK_STORAGE_HOTBAR", "getExtraResourcesSection", "getItemContainer",
                                     "CombinedItemContainer.<init>", "invalidateExtraResources"]),
        ("CraftingWindow.craftSimpleItem (the vanilla pocket path) crafts from the inventory only",
         "com.hypixel.hytale.builtin.crafting.window.CraftingWindow", "craftSimpleItem", None, ["BACKPACK_STORAGE_HOTBAR", "craftItem"]),
        ("FieldCraftingWindow.handleAction = craftSimpleItem + SFX_Player_Craft_Item_Inventory (PocketCraftWindow mirrors it)",
         FCW, "handleAction", None, ["CraftRecipeAction", "craftSimpleItem", "SFX_Player_Craft_Item_Inventory", "playSoundEvent2d"]),
        ("CraftingPlugin.setup registers the pocket crafting window supplier",
         CRP, "setup", None, ["CLIENT_REQUESTABLE_WINDOW_TYPES", "WindowType.PocketCrafting", "Map.put"]),
        ("a timed unit's inputs come out of the job's container and the window is invalidated after",
         CRM, "removeInputFromInventory", "CraftingManager$CraftingJob;I", ["inputItemContainer", "removeMaterials", "invalidateExtraResources"]),
        ("closing a bench cancels its queue and refunds the started unit into the inventory",
         CRM, "cancelAllCrafting", None, ["queuedCraftingJobs", "refundInputToInventory"]),
        ("the refund goes into the player's inventory (not the extra-materials container)",
         CRM, "refundInputToInventory", None, ["HOTBAR_FIRST", "getCombined", "addOrDropItemStacks"]),
        ("DelegateItemContainer refuses inserts when its filter does not allow input",
         DIC, "cantAddToSlot", None, ["FilterType.allowInput", "ifne", "iconst_1"]),
        ("DelegateItemContainer allows removals when its filter allows output",
         DIC, "cantRemoveFromSlot", None, ["FilterType.allowOutput"]),
        ("inbound filters run on the network thread BEFORE the packet handler queues its world task",
         "com.hypixel.hytale.server.core.io.netty.PlayerChannelHandler", "channelRead", None, ["PacketAdapters.__handleInbound", "PacketHandler.handle"]),
        ("world packet handlers run as World.execute tasks", "com.hypixel.hytale.server.core.io.handlers.IWorldPacketHandler",
         "lambda$registerHandler$0", None, ["World.execute"]),
        ("World.execute appends to a FIFO deque (a task queued earlier runs earlier)", WLD, "execute", None, ["Deque.offer"]),
        ("a player filter is called with the GamePacketHandler's PlayerRef",
         PAD, "lambda$registerOutbound$1", None, ["GamePacketHandler", "getPlayerRef", "PlayerPacketFilter.test"]),
        ("window close events fire after onClose0 (the close hook books after the vanilla refund)",
         WIN, "onClose", None, ["onClose0", "closeEventRegistry", "dispatch"]),
    ]
    bad = []
    for (what, cls, meth, sig, needles) in facts:
        miss = in_order(code(cls, meth, sig), needles)
        if miss is not None:
            bad.append("%s (%s.%s: no %r in order)" % (what, cls.rsplit(".", 1)[1], meth, miss))
    if bad:
        raise SystemExit("0.7.12 engine check FAILED - the bench / pocket link would not work as built:\\n  " + "\\n  ".join(bad))
    print("engine facts: %d verified (research/Bag-Craft-Link-Fix.md): %s" % (len(facts), "; ".join(f[0].split(" (")[0][:40] for f in facts[:4])) + " ...")


_engine_facts()
''')

# ================= new classes (0.7.12) =================
rep('''kq = pool.makeClass(PKG + ".KeptQuit")
''', '''kq = pool.makeClass(PKG + ".KeptQuit")
# 0.7.12 (research/Bag-Craft-Link-Fix.md): MirrorGuard = the mirror's output-only face; LinkRec = one crafting window's link state;
# BenchLink = the bench / pocket link logic (static); MirrorClose = a bench window's close hook; CraftPacketFilter (outbound) /
# CraftInFilter (inbound) = the packet filters; PreCraftTask = the pre-craft world task; PocketCraftWindow + PocketSupplier = pocket crafting
mgd = pool.makeClass(PKG + ".MirrorGuard", pool.get(DIC))
lrec = pool.makeClass(PKG + ".LinkRec")
blink = pool.makeClass(PKG + ".BenchLink")
mcl = pool.makeClass(PKG + ".MirrorClose")
cpf = pool.makeClass(PKG + ".CraftPacketFilter")
cif = pool.makeClass(PKG + ".CraftInFilter")
pct = pool.makeClass(PKG + ".PreCraftTask")
pcw = pool.makeClass(PKG + ".PocketCraftWindow", pool.get(FCW))
psu = pool.makeClass(PKG + ".PocketSupplier")
''')

# ================= SackPool: the change counter, the negative-clamp warning, no PENDQ =================
rep('''# KEPTKEY = player uuid -> the key whose kept counts that player used last (the quit listener forgets them). The stack refill's "stacks you
# are using" memory: SEENQ = uuid -> (item id -> Long carried at the end of the last sweep tick), PENDQ = uuid -> HashSet of item ids used
# while a bench was fed from the bags (refilled once it closes). All memory only: reset on relog (KeptQuit), on a profile switch
# (settledKey) and by a restart - like the exemption they replace.''',
    '''# KEPTKEY = player uuid -> the key whose kept counts that player used last (the quit listener forgets them). The stack refill's "stacks you
# are using" memory: SEENQ = uuid -> (item id -> Long carried at the end of the last sweep tick). 0.7.12: no PENDQ any more - the refill
# no longer waits while a bench is open (the live-mirror rule: BagMirror.beforeTake / afterTake). All memory only: reset on relog
# (KeptQuit), on a profile switch (settledKey) and by a restart - like the exemption they replace.''')
rep('''sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PENDQ = new java.util.concurrent.ConcurrentHashMap();", sp))
''', '')
rep('''sp.addField(CtField.make("public static volatile boolean CLOSED = false;", sp))
''', '''sp.addField(CtField.make("public static volatile boolean CLOSED = false;", sp))
# 0.7.12 (research/Bag-Craft-Link-Fix.md C): CHG = profile key -> Long change counter, bumped by EVERY pool change (add() is the one pool
# writer: sweep, withdraw, refill, mirror bookings). BenchLink compares it with what an open crafting window was last given.
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CHG = new java.util.concurrent.ConcurrentHashMap();", sp))
''')
rep("""  SEENQ.remove(u);
  PENDQ.remove(u);
}'''), sp))""", """  SEENQ.remove(u);
}'''), sp))""")
rep('''public static synchronized void add(String k, String item, long n) {
  java.util.Map m = pool(k);
  Long v = (Long) m.get(item);
  long nv = (v == null ? 0L : v.longValue()) + n;
  if (nv <= 0L) m.remove(item); else m.put(item, Long.valueOf(nv));
  DIRTY.put(k, Boolean.TRUE);
}""", sp))''', '''public static synchronized void add(String k, String item, long n) {
  java.util.Map m = pool(k);
  Long v = (Long) m.get(item);
  long nv = (v == null ? 0L : v.longValue()) + n;
  // 0.7.12: a booking below zero was silently clamped - it would mean items were used twice; say so (the clamp itself stays)
  if (nv < 0L) warn("pool for " + k + " would go below zero for " + item + " (by " + (-nv) + ") - clamped at 0; report this (accounting error)");
  if (nv <= 0L) m.remove(item); else m.put(item, Long.valueOf(nv));
  DIRTY.put(k, Boolean.TRUE);
  // 0.7.12: the per-key change counter (open crafting windows refresh their bag counts from it)
  if (n != 0L) {
    Long c = (Long) CHG.get(k);
    CHG.put(k, Long.valueOf(c == null ? 1L : c.longValue() + 1L));
  }
}""", sp))
# 0.7.12: the per-key change counter (0 = no change yet)
sp.addMethod(CtNewMethod.make("""
public static long chg(String k) {
  if (k == null) return 0L;
  Long c = (Long) CHG.get(k);
  return c == null ? 0L : c.longValue();
}""", sp))''')

# ================= the live-mirror rule: forward declarations (bodies set after the BagMirror section) + withdraw =================
rep('''# withdraw up to n of an item into STORAGE; returns how many actually left the pool
swp.addMethod(CtNewMethod.make(f"""
public static int withdraw({PLA} p, String k, String id, int n) {{
  long have = {PKG}.SackPool.get(k, id);''', '''# 0.7.12 THE LIVE-MIRROR RULE (research/Bag-Craft-Link-Fix.md invariant 7 - the mirror never offers more than the pool holds): every move
# that takes items OUT of a pool first books what a bench / pocket craft already took from that key's mirror (beforeTake = BagMirror.sync,
# else the pool would read too high and the same items could be taken out AND used by the bench) and right after the move trims the
# mirror to the pool (afterTake = BagMirror.fit, never booked). Declared here because SweepTask.withdraw (below) calls them; javassist
# compiles a call only against an existing method, so the real bodies are set with setBody after the BagMirror section ($1 = k, $2 = id).
_BEFORE_TAKE = CtNewMethod.make("public static int beforeTake(String k) { return 0; }", mir)
mir.addMethod(_BEFORE_TAKE)
_AFTER_TAKE = CtNewMethod.make("public static int afterTake(String k, String id) { return 0; }", mir)
mir.addMethod(_AFTER_TAKE)
# withdraw up to n of an item into STORAGE; returns how many actually left the pool
swp.addMethod(CtNewMethod.make(f"""
public static int withdraw({PLA} p, String k, String id, int n) {{
  // 0.7.12 live-mirror rule: book what a crafting window took from the bag mirror BEFORE the pool is read
  {PKG}.BagMirror.beforeTake(k);
  long have = {PKG}.SackPool.get(k, id);''')
rep('''    {PKG}.SackPool.add(k, id, -(long) added);
    {PKG}.SackPool.raiseKept(''', '''    {PKG}.SackPool.add(k, id, -(long) added);
    {PKG}.BagMirror.afterTake(k, id);   // 0.7.12 live-mirror rule: the mirror never offers more than the pool now holds
    {PKG}.SackPool.raiseKept(''')

# ================= MirrorGuard (before BagMirror: its constructor creates one) =================
rep('''# ================= BagMirror (per player: SimpleItemContainer mirroring the pool for bench crafting) =================
''', '''# ================= MirrorGuard (0.7.12, research/Bag-Craft-Link-Fix.md B): the bag mirror's OUTPUT-ONLY face =================
# A DelegateItemContainer over the mirror's container with FilterType.ALLOW_OUTPUT_ONLY (VERIFIED bytecode: cantAddToSlot refuses when
# the filter does not allow input, cantRemoveFromSlot allows output). Only the guard is ever put on a crafting section: crafts, timed units
# and tier upgrades remove through it; an insert (a stack shift-clicked or a refund aimed at the section) is refused - a raw container
# would accept it and the next rebuild would wipe it (item loss). Its own class marks it, so BenchLink.peel can always find the vanilla part.
mgd.addConstructor(CtNewConstructor.make(jt(r\'\'\'
public MirrorGuard(@IC@ c) {
  super(c);
  setGlobalFilter(@FT@.ALLOW_OUTPUT_ONLY);
}\'\'\'), mgd))

# ================= BagMirror (per player: SimpleItemContainer mirroring the pool for bench crafting) =================
''')
rep('''mir.addField(CtField.make(f"public {CIC} combined;", mir))
mir.addField(CtField.make("public Object vanilla;", mir))
''', '''# 0.7.12: guard = the output-only face that crafting sections get (never the raw container); ver = content version (bumped when a rebuild,
# fit or empty changes what the mirror offers - an open crafting window given an older version refreshes). The 0.7.10 combined / vanilla
# fields moved per window into LinkRec (a bench and the pocket window can share one mirror).
mir.addField(CtField.make(f"public {PKG}.MirrorGuard guard;", mir))
mir.addField(CtField.make("public int ver;", mir))
''')
rep('''  this.cont = new {SIC}((short) 36);
  this.slotIds = new String[36];
  this.slotQty = new int[36];
  this.sig = "";
}}""", mir))''', '''  this.cont = new {SIC}((short) 36);
  this.guard = new {PKG}.MirrorGuard(this.cont);
  this.slotIds = new String[36];
  this.slotQty = new int[36];
  this.sig = "";
  this.ver = 0;
}}""", mir))''')
# review fix 4: an id the Item asset map no longer knows (a pack mod removed while its items sat in a bag) is never offered - the client's
# answer to an unknown itemId in an extra-materials list is unknown; it stays in the pool (a separate statement: the 0.7.11 bytecode of the
# line above stays as it was)
rep('''    if (cat == null || !caps.containsKey(cat) || cnt <= 0L) continue;
    ids[e] = id;''', '''    if (cat == null || !caps.containsKey(cat) || cnt <= 0L) continue;
    if ({PKG}.ProcBench.item(id) == null) continue;   // 0.7.12 review fix 4: not a loaded item (a removed pack mod) - never offered
    ids[e] = id;''')
rep('''  return sb.toString();
}}""", mir))''', '''  // 0.7.12: the content version moves only when the offer really changed (same pool + same wanted set = same layout: no refresh loop)
  String nsig = sb.toString();
  if (!nsig.equals(this.sig)) {{ this.sig = nsig; this.ver++; }}
  return nsig;
}}""", mir))''')
# the 0.7.2 retireOther / park move into BenchLink (retire / park): they now detach + invalidate windows instead of feeding them
_old_retire = s[s.index("# 0.7.2: a bench mirror belongs to ONE profile key."):s.index("# 0.7.2 review fix: drop everything the mirror offers")]
assert "public static {PKG}.BagMirror retireOther(" in _old_retire and _old_retire.count("mir))") == 1
rep(_old_retire, '''# 0.7.12: the 0.7.2 retireOther moved to BenchLink.retire (sync + EMPTY + drop the old key's mirror, detach + invalidate its windows).
''')
rep('''public void empty() {{
  try {{ this.cont.clear(); }} catch (Throwable t) {{ }}
  for (int i = 0; i < 36; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}
  this.sig = "";
}}""", mir))''', '''public void empty() {{
  try {{ this.cont.clear(); }} catch (Throwable t) {{ }}
  for (int i = 0; i < 36; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}
  if (this.sig != null && this.sig.length() > 0) this.ver++;   // 0.7.12: what it offered changed
  this.sig = "";
}}""", mir))''')
_old_park = s[s.index("# 0.7.2 review fix (settle window): while SackPool.settledKey(u) is null CraftLinkTask calls only this."):s.index("mir.addMethod(CtNewMethod.make(f\"\"\"\npublic {IQ}[] quantities() {{")]
assert "public static int park(" in _old_park and _old_park.count("mir))") == 1
rep(_old_park, '''# 0.7.12: the 0.7.2 park moved to BenchLink.park (research/Bag-Craft-Link-Fix.md B: sync, empty, invalidateExtraResources on each open
# window using the mirror - the vanilla code re-feeds and sends; 0.7.10 marked the section valid and updated it, which sent no list).
''')

# ================= BagMirror: owns / merge / fit + the live-mirror bodies; then the link classes =================
LINK = r"""
# 0.7.12 (research/Bag-Craft-Link-Fix.md B) - owns: c is (or contains) this mirror's guard / container (CombinedItemContainer.containsContainer
# is recursive, VERIFIED); merge: the vanilla list + the mirror list summed by item id (vanilla order first, zeros / nulls skipped, NEW
# ItemQuantity objects - the arrays given are never edited); fit: trim what the mirror offers of one item to what the pool holds (after a
# sync, from the last slots; never booked - those items are still in the pool)
mir.addMethod(CtNewMethod.make(jt(r'''
public boolean owns(@IC@ c) {
  if (c == null) return false;
  return c.containsContainer(this.guard) || c.containsContainer(this.cont);
}'''), mir))
mir.addMethod(CtNewMethod.make(jt(r'''
public static void sumInto(java.util.LinkedHashMap sum, @IQ@[] l) {
  for (int i = 0; l != null && i < l.length; i++) {
    if (l[i] == null || l[i].itemId == null || l[i].quantity <= 0) continue;
    Long cur = (Long) sum.get(l[i].itemId);
    sum.put(l[i].itemId, Long.valueOf((cur == null ? 0L : cur.longValue()) + (long) l[i].quantity));
  }
}'''), mir))
mir.addMethod(CtNewMethod.make(jt(r'''
public static @IQ@[] merge(@IQ@[] a, @IQ@[] b) {
  java.util.LinkedHashMap sum = new java.util.LinkedHashMap();
  sumInto(sum, a);
  sumInto(sum, b);
  @IQ@[] out = new @IQ@[sum.size()];
  java.util.Iterator it = sum.entrySet().iterator();
  int k = 0;
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    long v = ((Long) e.getValue()).longValue();
    out[k++] = new @IQ@((String) e.getKey(), v > 2147483647L ? 2147483647 : (int) v);
  }
  return out;
}'''), mir))
mir.addMethod(CtNewMethod.make(jt(r'''
public int fit(String id) {
  if (id == null) return 0;
  sync();
  long inPool = @PKG@.SackPool.get(this.key, id);
  long held = 0L;
  for (int i = 0; i < 36; i++) if (id.equals(this.slotIds[i])) held += (long) this.slotQty[i];
  if (held <= inPool) return 0;
  long excess = held - inPool;
  int removed = 0;
  for (int j = 35; j >= 0 && excess > 0L; j--) {
    if (!id.equals(this.slotIds[j])) continue;
    @IS@ was = this.cont.getItemStack((short) j);
    int before = (was == null || was.isEmpty()) ? 0 : was.getQuantity();
    int take = (long) before < excess ? before : (int) excess;
    if (take > 0) this.cont.removeItemStackFromSlot((short) j, take);
    @IS@ after = this.cont.getItemStack((short) j);
    int left = (after == null || after.isEmpty()) ? 0 : after.getQuantity();
    int gone = before - left;
    if (gone < 0) gone = 0;
    this.slotQty[j] = left;
    if (left <= 0) this.slotIds[j] = null;
    excess -= (long) gone;
    removed += gone;
  }
  if (removed > 0) { this.ver++; this.sig = "fit:" + this.ver; }   // content changed: a new version, and the next rebuild differs from it
  return removed;
}'''), mir))
# the real bodies of the live-mirror rule (declared before SweepTask.withdraw): $1 = profile key, $2 = item id
_BEFORE_TAKE.setBody(jt(r'''{
  @PKG@.BagMirror m = (@PKG@.BagMirror) MIRRORS.get($1);
  if (m == null) return 0;
  return m.sync();
}'''))
_AFTER_TAKE.setBody(jt(r'''{
  @PKG@.BagMirror m = (@PKG@.BagMirror) MIRRORS.get($1);
  if (m == null) return 0;
  return m.fit($2);
}'''))

# ================= LinkRec (0.7.12): one open crafting window's link state (identity: the window object) =================
# key = the mirror key it is attached to (null = not attached), vanilla / vanillaList = the vanilla part of its section at the attach
# (nearby chests; none for the pocket window), combined = what was set on the section, chg / caps / ver = the pool counter, carried-bags
# signature and mirror version it was given, wanted = what that window can use (bench recipes / Fieldcraft), lastInval = the last refresh
# asked (rate limit), reg = the close hook, why = why it is not attached, logged = its "attached" log line was written
for _d in ("public Object win;", "public String key;", "public boolean attached;", "public @IC@ vanilla;", "public @IQ@[] vanillaList;",
           "public @IC@ combined;", "public long chg;", "public String caps;", "public int ver;", "public java.util.Set wanted;",
           "public long lastInval;", "public long seen;", "public @EVR@ reg;", "public String why;", "public boolean logged;"):
    lrec.addField(CtField.make(jt(_d), lrec))
lrec.addConstructor(CtNewConstructor.make("public LinkRec(Object w) { this.win = w; this.chg = -1L; this.ver = -1; }", lrec))

# ================= BenchLink (0.7.12, research/Bag-Craft-Link-Fix.md A / C / E): the bench + pocket crafting link =================
# Everything here runs on the player's world thread (the outbound filter checks Store.isInThread; the 300 ms task, the close hook, the
# pre-craft task and the pocket window's refill are world tasks). RECS = player uuid -> ArrayList of LinkRec (that player's world thread only).
# PLAYERS = the bare-JVM harness's PlayerRef -> Player lookup (always null in the game: the filter then reads the player's own store).
blink.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap RECS = new java.util.concurrent.ConcurrentHashMap();", blink))
blink.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();", blink))
blink.addField(CtField.make("public static volatile java.util.function.Function PLAYERS;", blink))
blink.addField(CtField.make(jt("public static volatile @PFI@ OUT;"), blink))
blink.addField(CtField.make(jt("public static volatile @PFI@ IN;"), blink))
blink.addField(CtField.make("public static volatile Object POCKET_SUP;", blink))
blink.addField(CtField.make("public static volatile Object POCKET_PREV;", blink))
blink.addField(CtField.make("public static volatile boolean POCKET_ON = false;", blink))
blink.addField(CtField.make("public static volatile boolean POCKET_WARNED = false;", blink))
# review fix 1: STARTED = between start() and stop() (the bags.pocketCraft switch swaps the pocket window only then)
blink.addField(CtField.make("public static volatile boolean STARTED = false;", blink))
blink.addField(CtField.make("public static volatile java.util.Set FIELD;", blink))
blink.addField(CtField.make("public static final long REFRESH_MS = 1000L;", blink))
blink.addMethod(CtNewMethod.make(jt(r'''
public static void warnOnce(String key, String msg) {
  if (key == null || WARNED.putIfAbsent(key, Boolean.TRUE) != null) return;
  @PKG@.SackPool.warn(msg);
}'''), blink))
blink.addMethod(CtNewMethod.make(jt(r'''
public static void info(String msg) {
  try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] " + msg); } catch (Throwable t) { }
}'''), blink))
blink.addMethod(CtNewMethod.make(jt(r'''
public static java.util.ArrayList recs(java.util.UUID u, boolean create) {
  if (u == null) return null;
  java.util.ArrayList l = (java.util.ArrayList) RECS.get(u);
  if (l == null && create) {
    l = new java.util.ArrayList();
    java.util.ArrayList prev = (java.util.ArrayList) RECS.putIfAbsent(u, l);
    if (prev != null) l = prev;
  }
  return l;
}'''), blink))
blink.addMethod(CtNewMethod.make(jt(r'''
public static @PKG@.LinkRec recOf(java.util.UUID u, Object w, boolean create) {
  if (u == null || w == null) return null;
  java.util.ArrayList l = recs(u, create);
  if (l == null) return null;
  for (int i = 0; i < l.size(); i++) {
    @PKG@.LinkRec r0 = (@PKG@.LinkRec) l.get(i);
    if (r0.win == w) return r0;
  }
  if (!create) return null;
  @PKG@.LinkRec r = new @PKG@.LinkRec(w);
  l.add(r);
  return r;
}'''), blink))
blink.addMethod(CtNewMethod.make(jt(r'''
public static @PKG@.LinkRec dropRec(java.util.UUID u, Object w) {
  java.util.ArrayList l = recs(u, false);
  if (l == null) return null;
  for (int i = 0; i < l.size(); i++) {
    @PKG@.LinkRec r = (@PKG@.LinkRec) l.get(i);
    if (r.win == w) {
      l.remove(i);
      if (l.isEmpty()) RECS.remove(u, l);
      return r;
    }
  }
  return null;
}'''), blink))
blink.addMethod(CtNewMethod.make(jt(r'''
public static boolean anyAttached(java.util.UUID u, String k) {
  java.util.ArrayList l = recs(u, false);
  if (l == null || k == null) return false;
  for (int i = 0; i < l.size(); i++) {
    @PKG@.LinkRec r = (@PKG@.LinkRec) l.get(i);
    if (r.attached && k.equals(r.key)) return true;
  }
  return false;
}'''), blink))
# the bench windows the link feeds: a SimpleCraftingWindow (Workbench, Cooking, Alchemy ...) or a ProcessingBenchWindow (its tier upgrade
# reads the section); Diagram / Structural crafting windows use their own input slots (research doc A)
blink.addMethod(CtNewMethod.make(jt(r'''
public static boolean isBench(Object w) {
  return w instanceof @SCW@ || w instanceof @PBW@;
}'''), blink))
blink.addMethod(CtNewMethod.make(jt(r'''
public static boolean isPocket(Object w) {
  return w instanceof @PKG@.PocketCraftWindow;
}'''), blink))
blink.addMethod(CtNewMethod.make(jt(r'''
public static String capsSig(java.util.HashMap caps) {
  if (caps == null || caps.isEmpty()) return "";
  return new java.util.TreeMap(caps).toString();
}'''), blink))
# the Fieldcraft (pocket crafting) recipes' inputs, cached once the recipe assets answer
blink.addMethod(CtNewMethod.make(jt(r'''
public static java.util.Set fieldWanted() {
  java.util.Set c = FIELD;
  if (c != null) return c;
  java.util.HashSet s = new java.util.HashSet();
  try {
    java.util.List l = @CRP@.getBenchRecipes(@BTP@.Crafting, "Fieldcraft");
    for (int i = 0; l != null && i < l.size(); i++) {
      Object o = l.get(i);
      if (o instanceof @CRR@) @PKG@.BagMirror.addInputs(s, ((@CRR@) o).getInput());
    }
  } catch (Throwable t) { }
  if (!s.isEmpty()) FIELD = s;
  return s;
}'''), blink))
blink.addMethod(CtNewMethod.make(jt(r'''
public static java.util.Set wantedOf(Object w) {
  if (isPocket(w)) return fieldWanted();
  java.util.Set s = @PKG@.BagMirror.wantedFor(w);
  return s == null ? new java.util.HashSet() : s;
}'''), blink))
# one mirror per key, shared by every crafting window of that player: it is rebuilt with the UNION of what those windows can use, so two
# windows never rebuild it against each other (a refresh ping-pong)
blink.addMethod(CtNewMethod.make(jt(r'''
public static java.util.HashSet union(java.util.UUID u, String k) {
  java.util.HashSet out = new java.util.HashSet();
  java.util.ArrayList l = recs(u, false);
  for (int i = 0; l != null && i < l.size(); i++) {
    @PKG@.LinkRec r = (@PKG@.LinkRec) l.get(i);
    if (r.attached && k != null && k.equals(r.key) && r.wanted != null) out.addAll(r.wanted);
  }
  return out;
}'''), blink))
# the vanilla part of a section container: a bare guard (pocket window) has none, Combined{x, guard} (what attach builds) has x
blink.addMethod(CtNewMethod.make(jt(r'''
public static @IC@ peel(@IC@ c) {
  if (c instanceof @PKG@.MirrorGuard) return null;
  if (c instanceof @CIC@) {
    @CIC@ cc = (@CIC@) c;
    if (cc.getContainersSize() == 2 && cc.getContainer(1) instanceof @PKG@.MirrorGuard) return cc.getContainer(0);
  }
  return c;
}'''), blink))
# RETIRE (invariant 6): the active key changed - the old key's mirror is synced, EMPTIED and dropped, its windows detached + refreshed.
# Called by the 300 ms link AND first thing in every attach (with no window list): a mirror the filter attached before the link ran
# is still retired on a quick profile switch (its windows are then refreshed by the link: their key differs)
blink.addMethod(CtNewMethod.make(jt(r'''
public static void retire(java.util.UUID u, String k, java.util.List wins) {
  if (u == null || k == null) return;
  String old = (String) @PKG@.BagMirror.LASTKEY.put(u, k);
  if (old == null || old.equals(k)) return;
  @PKG@.BagMirror m = (@PKG@.BagMirror) @PKG@.BagMirror.MIRRORS.remove(old);
  int c = 0;
  if (m != null) {
    c = m.sync();
    m.empty();
    @PKG@.SackPool.saveSoon(old);
  }
  int n = 0;
  long now = System.currentTimeMillis();
  for (int i = 0; wins != null && i < wins.size(); i++) {
    Object w = wins.get(i);
    if (!isBench(w) && !isPocket(w)) continue;
    @PKG@.LinkRec rec = recOf(u, w, false);
    if (rec == null || !old.equals(rec.key)) continue;
    rec.attached = false;
    rec.key = null;
    rec.why = "profile switched";
    rec.lastInval = now;
    ((@MCW@) w).invalidateExtraResources();
    n++;
  }
  if (m != null || n > 0) @PKG@.CraftLog.later(old, "PROFILE bench mirror retired - active key now " + k + " consumed=" + c + " windows=" + n);
}'''), blink))
# ATTACH (research doc B): sync (book what was taken) -> rebuild with the union of the key's windows -> section container = the guard
# (Combined{vanilla chests, guard} when there are chests) -> extra materials = vanilla list + mirror list -> valid. Returns the merged list.
blink.addMethod(CtNewMethod.make(jt(r'''
public static @IQ@[] attach(java.util.UUID u, @PKG@.LinkRec rec, @PKG@.BagMirror m, @MERS@ sec, @IC@ vanillaCont, @IQ@[] vanillaList, java.util.Set wanted, java.util.HashMap caps) {
  retire(u, m.key, (java.util.List) null);   // one live mirror per key: another key's mirror is synced, emptied and dropped first
  rec.wanted = wanted;
  rec.key = m.key;
  rec.attached = true;
  int c = m.sync();
  if (c > 0) @PKG@.SackPool.saveSoon(m.key);
  m.rebuild(caps, union(u, m.key));
  @IC@ comb = m.guard;
  if (vanillaCont != null && vanillaCont != @EIC@.INSTANCE) comb = new @CIC@(new @IC@[] { vanillaCont, m.guard });
  sec.setItemContainer(comb);
  @IQ@[] base = vanillaList == null ? new @IQ@[0] : vanillaList;
  @IQ@[] merged = @PKG@.BagMirror.merge(base, m.quantities());
  sec.setExtraMaterials(merged);
  sec.setValid(true);
  rec.vanilla = vanillaCont;
  rec.vanillaList = base;
  rec.combined = comb;
  rec.chg = @PKG@.SackPool.chg(m.key);
  rec.caps = capsSig(caps);
  rec.ver = m.ver;
  rec.why = null;
  rec.seen = System.currentTimeMillis();
  return merged;
}'''), blink))
# DECLINE: no settled key or no bag carried - vanilla only. A mirror the window used is synced (book what it took) and emptied (an old
# combined container a queued timed job still holds then finds nothing: bags are only usable while carried, never an unbooked removal).
blink.addMethod(CtNewMethod.make(jt(r'''
public static void decline(java.util.UUID u, @PKG@.LinkRec rec, String k, java.util.HashMap caps, String why) {
  if (rec == null) return;
  if (rec.attached && rec.key != null) {
    @PKG@.BagMirror om = (@PKG@.BagMirror) @PKG@.BagMirror.MIRRORS.get(rec.key);
    if (om != null) {
      int c = om.sync();
      if (c > 0) @PKG@.SackPool.saveSoon(rec.key);
      om.empty();
    }
  }
  rec.attached = false;
  rec.key = k;
  rec.combined = null;
  rec.chg = k == null ? -1L : @PKG@.SackPool.chg(k);
  rec.caps = capsSig(caps);
  rec.ver = -1;
  rec.why = why;
  rec.seen = System.currentTimeMillis();
}'''), blink))
# a crafting window closed (world thread; bench: after the vanilla refund of a started timed unit): book what it took at once; the last
# window of a key drops the mirror (synced + emptied first - nothing can reach its container afterwards)
blink.addMethod(CtNewMethod.make(jt(r'''
public static void closed(java.util.UUID u, Object w) {
  @PKG@.LinkRec rec = dropRec(u, w);
  if (rec == null || rec.key == null) return;
  String k = rec.key;
  @PKG@.BagMirror m = (@PKG@.BagMirror) @PKG@.BagMirror.MIRRORS.get(k);
  if (m == null) return;
  int c = m.sync();
  if (c > 0) @PKG@.SackPool.saveSoon(k);
  if (!anyAttached(u, k)) {
    m.empty();
    @PKG@.BagMirror.MIRRORS.remove(k, m);
  }
}'''), blink))
# ================= MirrorClose (0.7.12): a bench window's close hook -> BenchLink.closed =================
mcl.addInterface(pool.get("java.util.function.Consumer"))
mcl.addField(CtField.make("public java.util.UUID u;", mcl))
mcl.addField(CtField.make("public Object w;", mcl))
mcl.addConstructor(CtNewConstructor.make("public MirrorClose(java.util.UUID u, Object w) { this.u = u; this.w = w; }", mcl))
mcl.addMethod(CtNewMethod.make(jt(r'''
public void accept(Object ev) {
  try { @PKG@.BenchLink.closed(this.u, this.w); } catch (Throwable t) { }
}'''), mcl))
blink.addMethod(CtNewMethod.make(jt(r'''
public static void hook(@PKG@.LinkRec rec, Object w, java.util.UUID u) {
  if (rec == null || rec.reg != null || !(w instanceof @WIN@) || isPocket(w)) return;
  try { rec.reg = ((@WIN@) w).registerCloseEvent(new @PKG@.MirrorClose(u, w)); }
  catch (Throwable t) { warnOnce("hook", "craft link: no window close hook (" + t + ") - bench use is booked by the 300 ms task instead"); }
}'''), blink))
# the player of a filtered packet: only on that player's own world thread (else skipped, logged once - research doc risk 6)
blink.addMethod(CtNewMethod.make(jt(r'''
public static @PLA@ playerOf(@PR@ pr) {
  if (pr == null) return null;
  java.util.function.Function f = PLAYERS;
  if (f != null) return (@PLA@) f.apply(pr);
  @REF@ r = pr.getReference();
  if (r == null) return null;
  @ST@ st = r.getStore();
  if (st == null) return null;
  if (!st.isInThread()) {
    warnOnce("thread", "craft link: a bench window packet was sent off its world thread - bag counts skipped for it (logged once)");
    return null;
  }
  return (@PLA@) st.getComponent(r, @PLA@.getComponentType());
}'''), blink))
# Server Setup bags.benchChests (research doc risk 2, default off): a bench with bags linked reports at least 1 nearby chest - in the
# window's data (later updates) and in this packet's window data (the open packet was built before the filter ran)
blink.addMethod(CtNewMethod.make(jt(r'''
public static void chestFix(Object w, @PKT@ pkt) {
  if (!@PKG@.SackCfg.CHEST_FIX || !(w instanceof @WIN@)) return;
  try {
    @JSO@ d = ((@WIN@) w).getData();
    if (d != null && d.has("nearbyChestCount") && d.get("nearbyChestCount").getAsInt() < 1) d.addProperty("nearbyChestCount", Integer.valueOf(1));
    String wd = null;
    if (pkt instanceof @OW@) wd = ((@OW@) pkt).windowData;
    else if (pkt instanceof @UW@) wd = ((@UW@) pkt).windowData;
    if (wd == null || wd.indexOf("nearbyChestCount") < 0) return;
    @JSO@ o = @JPR@.parseString(wd).getAsJsonObject();
    if (!o.has("nearbyChestCount") || o.get("nearbyChestCount").getAsInt() >= 1) return;
    o.addProperty("nearbyChestCount", Integer.valueOf(1));
    if (pkt instanceof @OW@) ((@OW@) pkt).windowData = o.toString();
    else ((@UW@) pkt).windowData = o.toString();
  } catch (Throwable t) { warnOnce("chests", "craft link: bench chest count fallback failed (logged once): " + t); }
}'''), blink))
# ON EXTRAS (research doc A) - a bench OpenWindow / UpdateWindow carries a list: the section was just fed by the vanilla code (valid - no
# re-feed); attach the player's mirror to it and return the window (null = left vanilla). A section that still held a mirror (never the
# case for a packet with a list - defensive) gives its vanilla part back through peel + the window's own vanilla list.
blink.addMethod(CtNewMethod.make(jt(r'''
public static Object onExtras(@PLA@ p, java.util.UUID u, int id, @ER@ er) {
  if (p == null || u == null || er == null || id <= 0) return null;
  @WM@ wm = p.getWindowManager();
  if (wm == null) return null;
  @WIN@ w = wm.getWindow(id);
  if (w == null || !isBench(w)) return null;
  @MERS@ sec = ((@MCW@) w).getExtraResourcesSection();
  if (sec == null) return null;
  @PKG@.LinkRec rec = recOf(u, w, true);
  String k = @PKG@.SackPool.settledKey(u);
  java.util.HashMap caps = @PKG@.SweepTask.caps(p.getInventory());
  if (k == null || caps.isEmpty()) {
    decline(u, rec, k, caps, k == null ? "profile not settled" : "no bag carried");
    hook(rec, w, u);   // review fix 2: a declined bench gets its close hook too (else its record + window outlive a disconnect)
    return null;
  }
  @PKG@.BagMirror m = @PKG@.BagMirror.of(k);
  @IC@ cur = sec.getItemContainer();
  @IC@ vc = peel(cur);
  @IQ@[] vl = er.resources;
  if (vc != cur) vl = rec.vanillaList;
  @IQ@[] merged = attach(u, rec, m, sec, vc, vl, wantedOf(w), caps);
  er.resources = merged;
  hook(rec, w, u);
  if (!rec.logged) {
    rec.logged = true;
    info("craft link: attached " + m.quantities().length + " bag item types to " + w.getClass().getSimpleName() + " (key " + k + ", " + merged.length + " types shown)");
  }
  return w;
}'''), blink))
# the outbound filter's work: window packets with a list only (id 0 = the pocket window, which refills itself)
blink.addMethod(CtNewMethod.make(jt(r'''
public static void outbound(@PR@ pr, @PKT@ pkt) {
  int id = -1;
  @ER@ er = null;
  if (pkt instanceof @UW@) { id = ((@UW@) pkt).id; er = ((@UW@) pkt).extraResources; }
  else if (pkt instanceof @OW@) { id = ((@OW@) pkt).id; er = ((@OW@) pkt).extraResources; }
  if (er == null || id <= 0 || pr == null) return;
  @PLA@ p = playerOf(pr);
  if (p == null) return;
  Object w = onExtras(p, pr.getUuid(), id, er);
  if (w != null) chestFix(w, pkt);
}'''), blink))
# PRE-CRAFT (research doc E): runs before the vanilla handler of a bench craft / tier upgrade click. Not ours (re-fed by an earlier click
# in the same tick, or never attached) -> attach, so this click sees the bags; ours -> book what was taken and top the mirror up.
blink.addMethod(CtNewMethod.make(jt(r'''
public static boolean preCraft(@PLA@ p, java.util.UUID u, int id) {
  if (p == null || u == null || id <= 0) return false;
  @WM@ wm = p.getWindowManager();
  if (wm == null) return false;
  @WIN@ w = wm.getWindow(id);
  if (w == null || !isBench(w)) return false;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return false;
  java.util.HashMap caps = @PKG@.SweepTask.caps(p.getInventory());
  if (caps.isEmpty()) return false;
  @MERS@ sec = ((@MCW@) w).getExtraResourcesSection();
  if (sec == null) return false;
  @PKG@.BagMirror m = @PKG@.BagMirror.of(k);
  @IC@ cur = sec.getItemContainer();
  if (m.owns(cur)) {
    int c = m.sync();
    if (c > 0) @PKG@.SackPool.saveSoon(k);
    m.rebuild(caps, union(u, k));
    return false;
  }
  @PKG@.LinkRec rec = recOf(u, w, true);
  @IC@ vc = peel(cur);
  @IQ@[] vl = null;
  if (vc != cur) vl = rec.vanillaList;
  else {
    @ER@ pk = sec.toPacket();
    if (pk != null) vl = pk.resources;
  }
  attach(u, rec, m, sec, vc, vl, wantedOf(w), caps);
  hook(rec, w, u);
  return true;
}'''), blink))
# PARK (research doc B, profile switch settling): the player's last key's mirror is synced and emptied, every open crafting window using it
# is detached and asked to refresh (the vanilla code re-feeds the chests only; nothing is attached until the switch settles)
blink.addMethod(CtNewMethod.make(jt(r'''
public static int park(java.util.UUID u, java.util.List wins) {
  String lk = u == null ? null : (String) @PKG@.BagMirror.LASTKEY.get(u);
  if (lk == null) return 0;
  @PKG@.BagMirror m = (@PKG@.BagMirror) @PKG@.BagMirror.MIRRORS.get(lk);
  int consumed = 0;
  if (m != null) {
    consumed = m.sync();
    if (consumed > 0) @PKG@.SackPool.saveSoon(lk);
    if (m.holds()) m.empty();
  }
  int parked = 0;
  long now = System.currentTimeMillis();
  for (int i = 0; wins != null && i < wins.size(); i++) {
    Object w = wins.get(i);
    if (!isBench(w) && !isPocket(w)) continue;
    @PKG@.LinkRec rec = recOf(u, w, false);
    if (rec == null || !rec.attached || !lk.equals(rec.key)) continue;
    rec.attached = false;
    rec.key = null;
    rec.why = "profile switch settling";
    rec.lastInval = now;
    ((@MCW@) w).invalidateExtraResources();
    parked++;
  }
  if (parked > 0) {
    @PKG@.SackPool.warn("craft link: profile switch settling - bag materials taken off " + parked + " open crafting window(s) (key " + lk + ", consumed=" + consumed + ")");
    @PKG@.CraftLog.later(lk, "PROFILE switch settling - bag materials taken off " + parked + " open crafting window(s) consumed=" + consumed);
  }
  return consumed;
}'''), blink))
# REFRESH (research doc C) - one open crafting window, settled key k: ask the vanilla code to re-send (invalidateExtraResources; the filter
# or the pocket refill re-attaches) only when stale, at most once a second. An INVALID window is skipped (a refresh is already on its way;
# getExtraResourcesSection() on an invalid bench section would re-feed without a packet). Pool changed -> rebuild first, refresh only when
# the offer really changed (stone above the mirror's 4 stacks changes nothing on the screen).
blink.addMethod(CtNewMethod.make(jt(r'''
public static boolean refresh(java.util.UUID u, Object w, String k, @PKG@.BagMirror m, java.util.HashMap caps, String cs, long now) {
  @MCW@ mw = (@MCW@) w;
  if (!mw.isValid()) return false;
  @PKG@.LinkRec rec = recOf(u, w, false);
  @MERS@ sec = mw.getExtraResourcesSection();
  @IC@ c = sec == null ? null : sec.getItemContainer();
  boolean guarded = c != null && peel(c) != c;
  boolean ours = m != null && m.owns(c);
  boolean stale = false;
  if (rec == null) {
    rec = recOf(u, w, true);
    rec.key = k;
    rec.caps = cs;
    rec.why = "waiting for the next window refresh";
    hook(rec, w, u);   // review fix 2: the record this task made goes at the window's close too (not only by prune)
    stale = true;
  } else if (guarded && !ours) {
    stale = true;
  } else if (rec.attached) {
    if (!ours || !k.equals(rec.key) || !cs.equals(rec.caps)) stale = true;
    else {
      long chg = @PKG@.SackPool.chg(k);
      if (rec.chg != chg) {
        int cc = m.sync();
        if (cc > 0) @PKG@.SackPool.saveSoon(k);
        m.rebuild(caps, union(u, k));
        rec.chg = @PKG@.SackPool.chg(k);
      }
      stale = rec.ver != m.ver;
    }
  } else {
    stale = !k.equals(rec.key) || !cs.equals(rec.caps);
  }
  // review fix 1: inventory crafting switched off (bags.pocketCraft) while a pocket window still shows the bags -> refresh (it declines)
  if (!stale && rec.attached && isPocket(w) && !@PKG@.SackCfg.POCKET_CRAFT) stale = true;
  if (!stale) return false;
  if (now - rec.lastInval < REFRESH_MS) return false;
  rec.lastInval = now;
  mw.invalidateExtraResources();
  return true;
}'''), blink))
blink.addMethod(CtNewMethod.make(jt(r'''
public static void prune(java.util.UUID u, java.util.List wins) {
  java.util.ArrayList l = recs(u, false);
  if (l == null) return;
  for (int i = l.size() - 1; i >= 0; i--) {
    @PKG@.LinkRec r = (@PKG@.LinkRec) l.get(i);
    boolean open = false;
    for (int j = 0; wins != null && j < wins.size(); j++) {
      if (wins.get(j) == r.win) { open = true; break; }
    }
    if (!open) l.remove(i);
  }
  if (l.isEmpty()) RECS.remove(u, l);
}'''), blink))
blink.addMethod(CtNewMethod.make(jt(r'''
public static void pocketCheck() {
  // review fix 1: the backstop of the bags.pocketCraft switch (the row's after= hook and SackCfg.reload apply it at once)
  if (STARTED && POCKET_ON != @PKG@.SackCfg.POCKET_CRAFT) pocketApply();
  if (!POCKET_ON || POCKET_WARNED) return;
  Object cur = @WIN@.CLIENT_REQUESTABLE_WINDOW_TYPES.get(@WT@.PocketCrafting);
  if (cur != POCKET_SUP) {
    POCKET_WARNED = true;
    @PKG@.SackPool.warn("craft link: another mod replaced the pocket crafting window after ours - inventory crafting does not use the bags (benches still do)");
  }
}'''), blink))
# LINK - the 300 ms CraftLinkTask (world thread): a settling switch parks; else retire an old key, book what benches took, refresh every
# open crafting window that is stale, forget closed windows; no crafting window open = the mirror is synced, emptied and dropped
blink.addMethod(CtNewMethod.make(jt(r'''
public static void link(@PLA@ p, java.util.UUID u, java.util.List wins, long now) {
  if (p == null || u == null) return;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) { park(u, wins); return; }
  retire(u, k, wins);
  @PKG@.BagMirror m = (@PKG@.BagMirror) @PKG@.BagMirror.MIRRORS.get(k);
  if (m != null) {
    int c = m.sync();
    if (c > 0) @PKG@.SackPool.saveSoon(k);
  }
  boolean any = false;
  java.util.HashMap caps = null;
  String cs = null;
  for (int i = 0; wins != null && i < wins.size(); i++) {
    Object w = wins.get(i);
    if (!isBench(w) && !isPocket(w)) continue;
    any = true;
    if (caps == null) { caps = @PKG@.SweepTask.caps(p.getInventory()); cs = capsSig(caps); }
    try { refresh(u, w, k, m, caps, cs, now); }
    catch (Throwable t) { warnOnce("refresh", "craft link: window refresh failed (logged once): " + t); }
  }
  prune(u, wins);
  if (m != null && !any) {
    int c2 = m.sync();
    if (c2 > 0) @PKG@.SackPool.saveSoon(k);
    m.empty();
    @PKG@.BagMirror.MIRRORS.remove(k, m);
  }
  pocketCheck();
}'''), blink))

# ================= CraftPacketFilter (0.7.12, research doc A): the outbound filter (ALWAYS returns false - true drops the packet) =================
cpf.addInterface(pool.get(PPF))
cpf.addConstructor(CtNewConstructor.make("public CraftPacketFilter() { }", cpf))
cpf.addMethod(CtNewMethod.make(jt(r'''
public boolean test(@PR@ pr, @PKT@ pkt) {
  try {
    if (pkt instanceof @UW@ || pkt instanceof @OW@) @PKG@.BenchLink.outbound(pr, pkt);
  } catch (Throwable t) { @PKG@.BenchLink.warnOnce("filter", "craft link failed (outbound filter, logged once): " + t); }
  return false;
}'''), cpf))

# ================= PreCraftTask (0.7.12, research doc E): the world task the inbound filter queues before the vanilla handler =================
pct.addInterface(pool.get("java.lang.Runnable"))
pct.addField(CtField.make(jt("public @PR@ pr;"), pct))
pct.addField(CtField.make("public java.util.UUID expectedWorld;", pct))
pct.addField(CtField.make("public int id;", pct))
pct.addConstructor(CtNewConstructor.make(jt("public PreCraftTask(@PR@ pr, java.util.UUID w, int id) { this.pr = pr; this.expectedWorld = w; this.id = id; }"), pct))
pct.addMethod(CtNewMethod.make(jt(r'''
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID nowWorld = pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;
    @REF@ r = pr.getReference();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    @PKG@.BenchLink.preCraft(p, pr.getUuid(), this.id);
  } catch (Throwable t) { @PKG@.BenchLink.warnOnce("precraft", "craft link: pre-craft check failed (logged once): " + t); }
}'''), pct))

# ================= CraftInFilter (0.7.12, research doc E): the inbound filter (network thread; only queues; ALWAYS returns false) =================
cif.addInterface(pool.get(PPF))
cif.addConstructor(CtNewConstructor.make("public CraftInFilter() { }", cif))
cif.addMethod(CtNewMethod.make(jt(r'''
public boolean test(@PR@ pr, @PKT@ pkt) {
  try {
    if (!(pkt instanceof @SWA@)) return false;
    @SWA@ a = (@SWA@) pkt;
    if (a.id <= 0 || a.action == null) return false;
    if (!(a.action instanceof @CRA@) && !(a.action instanceof @TUA@)) return false;
    if (pr == null) return false;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return false;
    @WLD@ w = @UNI@.get().getWorld(wu);
    if (w == null) return false;
    w.execute(new @PKG@.PreCraftTask(pr, wu, a.id));
  } catch (Throwable t) { }
  return false;
}'''), cif))

# ================= PocketCraftWindow (0.7.12, research doc D): pocket crafting that also crafts from the bags you carry =================
# FieldCraftingWindow (the vanilla pocket crafting window: Fieldcraft categories in its data) + MaterialContainerWindow with its own section
# (starts invalid). The section refills when invalid: settled key + carried bags -> the player's shared mirror attached (Fieldcraft inputs
# first); else an EMPTY section (inventory only). The engine reads the section for window 0 in clientOpenWindow / updateWindow (VERIFIED).
pcw.addInterface(pool.get(MCW))
pcw.addField(CtField.make(jt("public @MERS@ sec;"), pcw))
pcw.addConstructor(CtNewConstructor.make(jt("public PocketCraftWindow() { super(); this.sec = new @MERS@(); }"), pcw))
# refillFor = the refill with an explicit player (the bare-JVM test seam; refill() below finds the player on its world thread)
pcw.addMethod(CtNewMethod.make(jt(r'''
public void refillFor(@PLA@ p, java.util.UUID u) {
  @PKG@.LinkRec rec = @PKG@.BenchLink.recOf(u, this, true);
  String k = u == null ? null : @PKG@.SackPool.settledKey(u);
  java.util.HashMap caps = p == null ? new java.util.HashMap() : @PKG@.SweepTask.caps(p.getInventory());
  // review fix 1: Server Setup bags.pocketCraft off = an open pocket window declines too (inventory only) until the inventory is reopened
  boolean on = @PKG@.SackCfg.POCKET_CRAFT;
  if (p == null || rec == null || k == null || caps.isEmpty() || !on) {
    this.sec.setItemContainer(@EIC@.INSTANCE);
    this.sec.setExtraMaterials(new @IQ@[0]);
    this.sec.setValid(true);
    @PKG@.BenchLink.decline(u, rec, k, caps, !on ? "inventory crafting link off (bags.pocketCraft)" : (k == null ? "profile not settled" : "no bag carried"));
    return;
  }
  @PKG@.BagMirror m = @PKG@.BagMirror.of(k);
  @PKG@.BenchLink.attach(u, rec, m, this.sec, (@IC@) null, new @IQ@[0], @PKG@.BenchLink.fieldWanted(), caps);
  // the pocket window is made anew each time the inventory opens: one log line per player and server start
  if (!rec.logged && @PKG@.BenchLink.WARNED.putIfAbsent("pocketlog:" + u, Boolean.TRUE) == null) {
    @PKG@.BenchLink.info("craft link: pocket crafting shows " + m.quantities().length + " bag item types (key " + k + ")");
  }
  rec.logged = true;
}'''), pcw))
pcw.addMethod(CtNewMethod.make(jt(r'''
public void refill() {
  try {
    @PR@ pr = getPlayerRef();
    if (pr == null) return;
    @REF@ r = pr.getReference();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null || !st.isInThread()) return;
    refillFor((@PLA@) st.getComponent(r, @PLA@.getComponentType()), pr.getUuid());
  } catch (Throwable t) { @PKG@.BenchLink.warnOnce("pocket", "craft link: pocket crafting bag materials skipped (logged once): " + t); }
}'''), pcw))
pcw.addMethod(CtNewMethod.make(jt(r'''
public @MERS@ getExtraResourcesSection() {
  if (!this.sec.isValid()) refill();
  if (this.sec.getItemContainer() == null) {
    this.sec.setItemContainer(@EIC@.INSTANCE);
    this.sec.setExtraMaterials(new @IQ@[0]);
  }
  return this.sec;
}'''), pcw))
# what a pocket craft takes its materials from (handleAction below; the bare-JVM test seam): the inventory first, then the section
pcw.addMethod(CtNewMethod.make(jt(r'''
public @IC@ craftContainer(@IC@ inv) {
  return new @CIC@(new @IC@[] { inv, getExtraResourcesSection().getItemContainer() });
}'''), pcw))
pcw.addMethod(CtNewMethod.make(jt(r'''
public void invalidateExtraResources() {
  this.sec.setValid(false);
  invalidate();
}'''), pcw))
pcw.addMethod(CtNewMethod.make(jt(r'''
public boolean isValid() {
  return this.sec.isValid();
}'''), pcw))
# a known recipe crafts through CraftingManager.craftItem from Combined{the vanilla inventory, the section} (CraftingWindow.craftSimpleItem
# + the section), the vanilla sound, then a refresh (the next updateWindow refills: the craft is booked by its sync). Anything else is vanilla.
pcw.addMethod(CtNewMethod.make(jt(r'''
public void handleAction(@REF@ ref, @ST@ store, @WA@ action) {
  if (!(action instanceof @CRA@)) { super.handleAction(ref, store, action); return; }
  @CRA@ a = (@CRA@) action;
  @CRR@ recipe = a.recipeId == null ? null : (@CRR@) @CRR@.getAssetMap().getAsset(a.recipeId);
  if (recipe == null) { super.handleAction(ref, store, action); return; }
  @CRM@ cm = (@CRM@) store.getComponent(ref, @CRM@.getComponentType());
  if (cm == null) return;
  @IC@ inv = @INVC@.getCombined(store, ref, @INVC@.BACKPACK_STORAGE_HOTBAR);
  cm.craftItem(ref, store, recipe, a.quantity, craftContainer(inv));
  try { @SNDU@.playSoundEvent2d(ref, @TAI@.getSoundEventIndex("SFX_Player_Craft_Item_Inventory"), @SCAT@.UI, store); } catch (Throwable t) { }
  invalidateExtraResources();
}'''), pcw))
pcw.addMethod(CtNewMethod.make(jt(r'''
public void onClose0(@REF@ ref, @CAC@ acc) {
  super.onClose0(ref, acc);
  try {
    @PR@ pr = getPlayerRef();
    @PKG@.BenchLink.closed(pr == null ? null : pr.getUuid(), this);
  } catch (Throwable t) { }
}'''), pcw))
psu.addInterface(pool.get("java.util.function.Supplier"))
psu.addConstructor(CtNewConstructor.make("public PocketSupplier() { }", psu))
psu.addMethod(CtNewMethod.make(jt(r'''
public Object get() {
  return new @PKG@.PocketCraftWindow();
}'''), psu))

# ================= BenchLink start / stop (plugin start() / shutdown()) =================
# review fix 1: synchronized (the switch may arrive from the SackSaver, the kit's after= hook and the 300 ms link at once - two
# overlapping swaps would record OUR supplier as the one to restore); pocketStart checks Server Setup bags.pocketCraft (read from
# config.properties by SackCfg.reload in setup(), before start()) and never swaps twice
blink.addMethod(CtNewMethod.make(jt(r'''
public static synchronized void pocketStart() {
  if (POCKET_ON) return;
  if (!@PKG@.SackCfg.POCKET_CRAFT) {
    info("craft link: inventory crafting does not use the bags - Server Setup bags.pocketCraft is off (the vanilla pocket crafting window stays)");
    return;
  }
  java.util.Map map = @WIN@.CLIENT_REQUESTABLE_WINDOW_TYPES;
  @PKG@.PocketSupplier sup = new @PKG@.PocketSupplier();
  Object prev = map.put(@WT@.PocketCrafting, sup);
  POCKET_SUP = sup;
  POCKET_PREV = prev;
  POCKET_WARNED = false;
  POCKET_ON = true;
  if (prev == null) @PKG@.SackPool.warn("craft link: no pocket crafting window was registered before ours (crafting plugin missing?) - ours is used, nothing to restore at shutdown");
  else info("craft link: pocket crafting uses the bags you carry (" + prev.getClass().getName() + " -> PocketCraftWindow; restored at shutdown or by bags.pocketCraft off)");
}'''), blink))
blink.addMethod(CtNewMethod.make(jt(r'''
public static synchronized void pocketStop() {
  if (!POCKET_ON) return;
  POCKET_ON = false;
  java.util.Map map = @WIN@.CLIENT_REQUESTABLE_WINDOW_TYPES;
  Object cur = map.get(@WT@.PocketCrafting);
  if (cur != POCKET_SUP) { @PKG@.SackPool.warn("craft link: the pocket crafting window was replaced by another mod - left as it is"); return; }
  if (POCKET_PREV != null) map.put(@WT@.PocketCrafting, POCKET_PREV);
  else map.remove(@WT@.PocketCrafting);
}'''), blink))
# review fix 1: the bags.pocketCraft switch applied live (SackCfg.linkKeys after a reload, SackCfg.pocketChanged = the row's after= hook,
# pocketCheck in the 300 ms link): ours in when on, the vanilla supplier back when off - only between start() and stop(). New pocket
# windows (the inventory opened again) follow at once; an open one declines on its next refresh (PocketCraftWindow.refillFor)
_POCKET_APPLY.setBody(jt(r'''{
  if (!STARTED) return;
  boolean want = @PKG@.SackCfg.POCKET_CRAFT;
  if (want && !POCKET_ON) pocketStart();
  else if (!want && POCKET_ON) pocketStop();
}'''))
blink.addMethod(CtNewMethod.make(jt(r'''
public static synchronized void stop() {
  STARTED = false;
  try { if (OUT != null) @PAD@.deregisterOutbound(OUT); } catch (Throwable t) { }
  OUT = null;
  try { if (IN != null) @PAD@.deregisterInbound(IN); } catch (Throwable t) { }
  IN = null;
  try { pocketStop(); } catch (Throwable t) { }
}'''), blink))
# start() first undoes an earlier start (a second registration would merge the bags twice into every list)
blink.addMethod(CtNewMethod.make(jt(r'''
public static synchronized void start() {
  stop();
  WARNED.clear();
  FIELD = null;
  try { OUT = @PAD@.registerOutbound(new @PKG@.CraftPacketFilter()); }
  catch (Throwable t) { @PKG@.SackPool.warn("craft link: outbound filter not registered - benches show inventory materials only: " + t); }
  try { IN = @PAD@.registerInbound(new @PKG@.CraftInFilter()); }
  catch (Throwable t) { @PKG@.SackPool.warn("craft link: inbound filter not registered - a fast second craft click may miss the bags: " + t); }
  STARTED = true;
  try { pocketStart(); }
  catch (Throwable t) { @PKG@.SackPool.warn("craft link: pocket crafting window not replaced - inventory crafting uses the inventory only: " + t); }
  info("craft link: benches " + (POCKET_ON ? "and inventory crafting use" : "use") + " the bags you carry (outbound filter " + (OUT != null) + ", pre-craft filter " + (IN != null) + ", pocket window " + (POCKET_ON ? "ours" : (@PKG@.SackCfg.POCKET_CRAFT ? "not replaced" : "vanilla - Server Setup bags.pocketCraft is off")) + ")");
}'''), blink))

"""
assert '"""' not in LINK
rep('''# ================= 0.7.11 SweepTask (continued): STACK AUTO-REFILL + the 2 s item tick =================
''', LINK + '''
# ================= 0.7.11 SweepTask (continued): STACK AUTO-REFILL + the 2 s item tick =================
''')

# ================= SweepTask.refill / items: the live-mirror rule replaces the 0.7.11 bench pause =================
rep('''  java.util.HashMap caps = caps(inv);
  if (caps.isEmpty()) return 0;
  @IC@[] conts = mode == 1 ? new @IC@[] { inv.getHotbar(), inv.getStorage(), inv.getBackpack() } : new @IC@[] { inv.getHotbar() };''',
    '''  java.util.HashMap caps = caps(inv);
  if (caps.isEmpty()) return 0;
  @PKG@.BagMirror.beforeTake(k);   // 0.7.12 live-mirror rule: book what a crafting window took before the pool is read
  @IC@[] conts = mode == 1 ? new @IC@[] { inv.getHotbar(), inv.getStorage(), inv.getBackpack() } : new @IC@[] { inv.getHotbar() };''')
rep('''      @PKG@.SackPool.add(k, id, -(long) got);
      @PKG@.SackPool.keep(k, id, (long) got);''', '''      @PKG@.SackPool.add(k, id, -(long) got);
      @PKG@.BagMirror.afterTake(k, id);   // 0.7.12 live-mirror rule: the mirror never offers more than the pool now holds
      @PKG@.SackPool.keep(k, id, (long) got);''')
_old_fed = s[s.index("# Review fix 9: is a bench fed from the bags right now?"):s.index("# items(): the item work of one 2 s tick for a SETTLED key")]
assert "public static boolean benchFed(" in _old_fed and _old_fed.count("swp))") == 1
rep(_old_fed, '''# 0.7.12: the 0.7.11 benchFed pause is gone - the live-mirror rule (BagMirror.beforeTake / afterTake inside refill) keeps a bench and the
# refill from ever offering the same items twice, so the refill also runs while a bench or pocket crafting is open.
''')
rep('''# the last tick (SEENQ - our own moves happen before that snapshot, so they never count) + the items still pending; (2) kept drops to
# what the player carries; (3) the automatic sweep; (4) the stack refill of the used items (mode from RefillPref; off = nothing). While a
# bench is fed from the bags (benchFed: a mirror for the key AND an open bench window) the refill waits and the used items stay pending in
# PENDQ: the mirror offers pool items to that bench, so taking them out here could let the bench use them twice. (5) the new SEENQ
# snapshot. Returns {swept, refilled}.''', '''# the last tick (SEENQ - our own moves happen before that snapshot, so they never count); (2) kept drops to what the player carries; (3)
# the automatic sweep; (4) the stack refill of the used items (mode from RefillPref; off = nothing) - 0.7.12: also while a bench or pocket
# crafting uses the bags (the live-mirror rule inside refill, no pending set any more); (5) the new SEENQ snapshot. Returns {swept, refilled}.''')
rep('''  java.util.HashSet pend = u == null ? null : (java.util.HashSet) @PKG@.SackPool.PENDQ.remove(u);
  if (pend != null) used.addAll(pend);
''', '')
rep('''  if (mode != 2 && !used.isEmpty()) {
    try {
      if (benchFed(p, k)) { if (u != null) @PKG@.SackPool.PENDQ.put(u, used); }
      else out[1] = refill(p, k, mode, used, sweepLeft(inv, k, caps(inv)), (java.util.HashMap) null);
    } catch (Throwable t2) { @PKG@.KnowSync.warnOnce("stack refill failed: " + t2); }
  }''', '''  if (mode != 2 && !used.isEmpty()) {
    try { out[1] = refill(p, k, mode, used, sweepLeft(inv, k, caps(inv)), (java.util.HashMap) null); }
    catch (Throwable t2) { @PKG@.KnowSync.warnOnce("stack refill failed: " + t2); }
  }''')

# ================= CraftLinkTask: the 300 ms task hands its work to BenchLink.link =================
rep('''# 0.7.2 review fix: the key comes from SackPool.settledKey. While a profile switch settles (null) the task only parks the mirror
# (BagMirror.park) and returns: no retireOther, no rebuild, nothing fed to the bench for ANY key until the switch has settled.''',
    '''# 0.7.2 review fix: the key comes from SackPool.settledKey. While a profile switch settles (null) the task only parks the mirror and returns.
# 0.7.12 (research/Bag-Craft-Link-Fix.md C): BenchLink.link does the work - it books what crafting windows took and asks the vanilla code
# for a refresh when a window is stale; it never marks a section valid or sends a window update itself (0.7.10's valid + updateWindow sent
# no extra-materials list - the cause of "Stick 0/4").''')
rep('''clt.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DBG = new java.util.concurrent.ConcurrentHashMap();", clt))
''', '')
_old_run = s[s.index('''clt.addMethod(CtNewMethod.make(f"""
public void run() {{'''):s.index('''ctk.addInterface(pool.get("java.lang.Runnable"))''')]
assert "BagMirror.park(wm0, wins0, u)" in _old_run and _old_run.count("clt))") == 1
rep(_old_run, '''clt.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    java.util.UUID nowWorld = pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (p == null) return;
    {WM} wm = p.getWindowManager();
    java.util.List wins = null;
    if (wm != null) wins = wm.getWindows();
    {PKG}.BenchLink.link(p, pr.getUuid(), wins, System.currentTimeMillis());
  }} catch (Throwable t) {{ {PKG}.BenchLink.warnOnce("link", "craft link failed (logged once): " + t); }}
}}""", clt))

''')

# ================= wording: benches and inventory crafting use the bags you carry (0.7.11 removed it on purpose - now true) =================
rep('''# the one-line explanation under the row. Review fix 1: no bench claim - vanilla benches do NOT use the bags yet (research/Bag-Craft-Link-
# Fix.md, SkyySacks 0.7.12), and the refill itself waits while a bench window is open (SweepTask.benchFed), so FULL tops up after the bench
# closes (Skyy's FULL use case: brewing / cooking / crafting from the inventory)
RF_HELP = ("A hotbar stack you use tops back up from your bags every 2 seconds (paused while a bench is open).",
           "Any stack you use - hotbar, inventory or backpack - tops back up every 2 seconds (paused while a bench is open).",
           "Stacks never top up by themselves - take items out on this page when you need them.")
RF_OFFSRV = "Stack refill is turned off on this server - your choice is kept for when it is back on."
assert len(RF_WORDS) == len(RF_LABELS) == len(RF_HELP) == 3
assert not any("enches already" in h or "enches still" in h or "use your bags" in h for h in RF_HELP + (RF_OFFSRV,)), "review fix 1"''',
    '''# the one-line explanation under the row. 0.7.12: benches and inventory crafting DO use the bags now (research/Bag-Craft-Link-Fix.md) - every
# line says so (0.7.11 had removed that claim on purpose); the refill no longer pauses while a bench is open (the live-mirror rule)
RF_HELP = ("A hotbar stack you use tops back up from your bags every 2 seconds. Benches and inventory crafting use your bags too.",
           "Any stack you use - hotbar, inventory or backpack - tops back up every 2 seconds. Benches and inventory crafting use your bags too.",
           "Stacks never top up by themselves - take items out on this page. Benches and inventory crafting still use your bags.")
RF_OFFSRV = "Stack refill is turned off on this server - your choice is kept. Benches and inventory crafting still use your bags."
# 0.7.12 review fix 1: the same lines while Server Setup bags.pocketCraft is off (inventory crafting does not use the bags then)
RF_HELP_B = ("A hotbar stack you use tops back up from your bags every 2 seconds. Benches use your bags too.",
             "Any stack you use - hotbar, inventory or backpack - tops back up every 2 seconds. Benches use your bags too.",
             "Stacks never top up by themselves - take items out on this page. Benches still use your bags.")
RF_OFFSRV_B = "Stack refill is turned off on this server - your choice is kept. Benches still use your bags."
assert len(RF_WORDS) == len(RF_LABELS) == len(RF_HELP) == len(RF_HELP_B) == 3
assert all("Benches and inventory crafting" in h for h in RF_HELP + (RF_OFFSRV,)) and not any("paused" in h for h in RF_HELP), "0.7.12 wording"
assert not any("inventory crafting" in h or "paused" in h for h in RF_HELP_B + (RF_OFFSRV_B,)) and all("Benches" in h for h in RF_HELP_B + (RF_OFFSRV_B,))''')
rep('''rfp.addField(CtField.make("public static final String OFFSRV = " + jlit(RF_OFFSRV) + ";", rfp))   # review fix 8: bags.refill off
''', '''rfp.addField(CtField.make("public static final String OFFSRV = " + jlit(RF_OFFSRV) + ";", rfp))   # review fix 8: bags.refill off
# 0.7.12 review fix 1: the lines shown while Server Setup bags.pocketCraft is off (no inventory crafting claim)
rfp.addField(CtField.make("public static final String[] HELPB = new String[] { " + ", ".join(jlit(h) for h in RF_HELP_B) + " };", rfp))
rfp.addField(CtField.make("public static final String OFFSRVB = " + jlit(RF_OFFSRV_B) + ";", rfp))
''')
rep('''  b.set("#SkyySRefillHelp.Text", @PKG@.SackCfg.REFILL_ON ? @PKG@.RefillPref.HELP[m] : @PKG@.RefillPref.OFFSRV);''',
    '''  // 0.7.12 review fix 1: the inventory crafting claim only while Server Setup bags.pocketCraft is on
  boolean pc = @PKG@.SackCfg.POCKET_CRAFT;
  b.set("#SkyySRefillHelp.Text", @PKG@.SackCfg.REFILL_ON ? (pc ? @PKG@.RefillPref.HELP[m] : @PKG@.RefillPref.HELPB[m]) : (pc ? @PKG@.RefillPref.OFFSRV : @PKG@.RefillPref.OFFSRVB));''')
rep('''for _h in RF_HELP + (RF_OFFSRV,):
''', '''for _h in RF_HELP + (RF_OFFSRV,) + RF_HELP_B + (RF_OFFSRV_B,):   # 0.7.12 review fix 1: + the bags.pocketCraft-off lines
''')
rep('''  b.set("#SkyySNbHint.Text", "/craft can use the materials in the bags you carry. Unlocked bag recipes are also on the Collections tab of /craft.");''',
    '''  // 0.7.12 (review fix 1: the inventory crafting claim only while Server Setup bags.pocketCraft is on)
  b.set("#SkyySNbHint.Text", @PKG@.SackCfg.POCKET_CRAFT ? "Benches and inventory crafting use the materials in the bags you carry, and so does /craft. Unlocked bag recipes are also on the Collections tab of /craft." : "Benches use the materials in the bags you carry, and so does /craft. Unlocked bag recipes are also on the Collections tab of /craft.");''')
rep('''right-click a magic bag; /craft crafts from your bags (vanilla benches do not show bag materials yet); withdrawn items stay in your inventory''',
    '''right-click a magic bag; benches and inventory crafting use the bags you carry (bag items show at the bench; inventory crafting can be switched off with bags.pocketCraft; /craft too); withdrawn items stay in your inventory''')

# ================= Server Setup: bags.benchChests (research doc risk 2 fallback, default off) + review fix 1: bags.pocketCraft =================
CHEST_HELP = "On: a bench with your bags linked reports 1 nearby chest. Only if benches ignore bag items."
assert len(CHEST_HELP) <= 100, "the kit's help limit is 100 characters"
# review fix 1: the off switch of the pocket crafting swap (default on); the kit's limits: label 40, help 100 characters
POCKET_LABEL = "Bags in inventory crafting"
POCKET_HELP = "On: inventory crafting also uses the bags you carry. Off: inventory only (benches still use bags)."
assert len(POCKET_LABEL) <= 40 and len(POCKET_HELP) <= 100, "the kit's label / help limits"
rep('''scfg.addField(CtField.make('public static volatile String REFILL_DEF = "hotbar";', scfg))
''', '''scfg.addField(CtField.make('public static volatile String REFILL_DEF = "hotbar";', scfg))
# 0.7.12: bags.benchChests (Server Setup "Bench chest count fallback", default off; research/Bag-Craft-Link-Fix.md risk 2), bound field
scfg.addField(CtField.make("public static volatile boolean CHEST_FIX = false;", scfg))
# 0.7.12 review fix 1: bags.pocketCraft (Server Setup "Bags in inventory crafting", default ON) - the pocket crafting swap's off switch
scfg.addField(CtField.make("public static volatile boolean POCKET_CRAFT = true;", scfg))
''')
rep('''    "#bags.refillDefault=hotbar",
''', '''    "#bags.refillDefault=hotbar",
    "# Bench chest count fallback (true or false): true makes an open bench report at least 1 nearby chest while your bags are linked.",
    "# Turn it on only if benches ignore bag items (the game client may want a chest count first).",
    "#bags.benchChests=false",
    "# Bags in inventory crafting (true or false): true lets inventory (pocket) crafting use the bags you carry, like benches do.",
    "# Set it to false if inventory crafting misbehaves on clients - benches keep using the bags either way.",
    "#bags.pocketCraft=true",
''')
rep('''     "field:SackCfg.REFILL_DEF@config.properties:bags.refillDefault;after=SackCfg.refillChanged"),
''', '''     "field:SackCfg.REFILL_DEF@config.properties:bags.refillDefault;after=SackCfg.refillChanged"),
    # 0.7.12 (research/Bag-Craft-Link-Fix.md risk 2): live - BenchLink.chestFix reads it on every bench packet
    ("bags.benchChests", "Bench chest count fallback", "bags", "bool", "false", "", "", "", "", "live", "%s",
     "field:SackCfg.CHEST_FIX@config.properties:bags.benchChests"),
    # 0.7.12 review fix 1: live - SackCfg.pocketChanged swaps the vanilla pocket crafting window back / ours in (BenchLink.pocketApply)
    ("bags.pocketCraft", "%s", "bags", "bool", "true", "", "", "", "", "live", "%s",
     "field:SackCfg.POCKET_CRAFT@config.properties:bags.pocketCraft;after=SackCfg.pocketChanged"),
''' % (CHEST_HELP, POCKET_LABEL, POCKET_HELP))
rep('''scfg.addMethod(CtNewMethod.make("""
public static synchronized void reload() {''', '''# 0.7.12 review fix 1: BenchLink.pocketApply (the bags.pocketCraft switch applied live) is called by linkKeys / pocketChanged below; javassist
# compiles a call only against an existing method, so it is declared here and its real body is set after BenchLink.pocketStart / pocketStop
_POCKET_APPLY = CtNewMethod.make("public static synchronized void pocketApply() { }", blink)
blink.addMethod(_POCKET_APPLY)
# 0.7.12: bags.benchChests + review fix 1 bags.pocketCraft for reload() below (one log line when the value is not the default at the first
# load and on every change). A later load (a hand edit) applies bags.pocketCraft at once (BenchLink.pocketApply: no-op before start())
scfg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void linkKeys(java.util.Properties p, boolean first) {
  boolean v = boolKey(p, "bags.benchChests", false);
  boolean changed = (first && v) || (!first && v != CHEST_FIX);
  CHEST_FIX = v;
  boolean pc = boolKey(p, "bags.pocketCraft", true);
  boolean pcChanged = (first && !pc) || (!first && pc != POCKET_CRAFT);
  POCKET_CRAFT = pc;
  if (changed) {
    try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: bench chest count fallback " + (v ? "ON (a bench with bags linked reports at least 1 nearby chest)" : "OFF")); } catch (Throwable t) { }
  }
  if (pcChanged) {
    try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: bags in inventory crafting " + (pc ? "ON (pocket crafting uses the bags you carry)" : "OFF (bags.pocketCraft - inventory crafting uses the inventory only; benches still use the bags)")); } catch (Throwable t) { }
  }
  if (!first) {
    try { @PKG@.BenchLink.pocketApply(); } catch (Throwable t) { @PKG@.SackPool.warn("config: bags.pocketCraft could not be applied: " + t); }
  }
}\'\'\'), scfg))
# 0.7.12 review fix 1: after= hook of the bags.pocketCraft row (the kit set POCKET_CRAFT already): one log line + the swap applied at once
scfg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void pocketChanged(String key) {
  try {
    if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: bags in inventory crafting " + (POCKET_CRAFT ? "ON - pocket crafting uses the bags you carry (from the next time a player opens the inventory)" : "OFF - inventory crafting uses the inventory only (benches still use the bags)"));
  } catch (Throwable t) { }
  try { @PKG@.BenchLink.pocketApply(); } catch (Throwable t) { @PKG@.SackPool.warn("config: bags.pocketCraft could not be applied: " + t); }
}\'\'\'), scfg))
scfg.addMethod(CtNewMethod.make("""
public static synchronized void reload() {''')
rep('''    refillKeys(p, first);   // 0.7.11 review fix 8: the stack refill owner switches (Server Setup rows bags.refill / bags.refillDefault)
''', '''    refillKeys(p, first);   // 0.7.11 review fix 8: the stack refill owner switches (Server Setup rows bags.refill / bags.refillDefault)
    linkKeys(p, first);     // 0.7.12: bags.benchChests (bench chest count fallback)
''')

# ================= plugin: start() starts the link, shutdown() stops it; the classes are written =================
rep('''pl.addMethod(CtNewMethod.make(WB.start_java(PKG), pl))   # 0.7.10: the Workbench tab once every asset pack is loaded
''', '''# 0.7.10: the Workbench tab once every asset pack is loaded. 0.7.12: + the bench / pocket crafting link (research/Bag-Craft-Link-Fix.md):
# the packet filters and the pocket crafting window swap need every plugin set up (CraftingPlugin registers the vanilla pocket window in
# its setup) - the shared tools/skyywbtab.py start() text gets one more statement here (the module itself stays unchanged)
_START_JAVA = WB.start_java(PKG)
assert _START_JAVA.endswith(chr(10) + "}") and _START_JAVA.count("protected void start()") == 1
_START_JAVA = (_START_JAVA[:-1] + "  // 0.7.12: benches and inventory crafting use the bags you carry (BenchLink: packet filters + the pocket crafting window)" + chr(10)
               + "  try { %s.BenchLink.start(); } catch (Throwable t2) { %s.SackPool.warn(\\"craft link: could not start - benches and inventory crafting use the inventory only: \\" + t2); }" % (PKG, PKG)
               + chr(10) + "}")
pl.addMethod(CtNewMethod.make(_START_JAVA, pl))
''')
rep('''  {PKG}.SackPool.CLOSED = true;   // 0.7.11 review fix 10: the shutdown latch (SackPool.settledKey answers null from here on)
''', '''  {PKG}.SackPool.CLOSED = true;   // 0.7.11 review fix 10: the shutdown latch (SackPool.settledKey answers null from here on)
  try {{ {PKG}.BenchLink.stop(); }} catch (Throwable t) {{ }}   // 0.7.12: the packet filters off, the vanilla pocket window back
''')
rep('''for c in (defs, sp, scfg, ksync, snot, rfp, kq, pjob, pben, pst, swp, tick, sav, cmp, page, cmd, fac, mir, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, pl):
    c.writeFile(OUT)   # 0.7.11: + RefillPref, KeptQuit
''', '''for c in (defs, sp, scfg, ksync, snot, rfp, kq, pjob, pben, pst, swp, tick, sav, cmp, page, cmd, fac, mgd, mir, lrec, blink, mcl, cpf, pct, cif,
          pcw, psu, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, pl):
    c.writeFile(OUT)   # 0.7.11: + RefillPref, KeptQuit. 0.7.12: + MirrorGuard, LinkRec, BenchLink, MirrorClose, the two filters, PreCraftTask,
                       # PocketCraftWindow, PocketSupplier
''')

# ================= self-checks =================
assert 'VERSION = "0.7.12"' in s and s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "no new command or ECS system"
assert "PENDQ.remove" not in s and "PENDQ.put" not in s and "ConcurrentHashMap PENDQ" not in s and "benchFed(" not in s and "DBG" not in s and "BagMirror.park(" not in s and "retireOther(" not in s
assert "m.combined" not in s and "stale.vanilla" not in s and "(paused while a bench is open)" not in s
assert "/craft crafts from your bags (vanilla benches do not show bag materials yet)" not in s
assert s.count("{PKG}.BagMirror.beforeTake(k);") == 1 and s.count("@PKG@.BagMirror.beforeTake(k);") == 1 \
    and s.count("{PKG}.BagMirror.afterTake(k, id);") == 1 and s.count("@PKG@.BagMirror.afterTake(k, id);") == 1, "live-mirror rule in withdraw + refill"
assert s.count("BenchLink.start()") == 1 and s.count("BenchLink.stop()") == 1
for _a, _b in (("mgd = pool.makeClass(", "# ================= SackDefs ="),
               ("sp.addField(CtField.make(\"public static final java.util.concurrent.ConcurrentHashMap CHG", "public static synchronized void add("),
               ("public static long chg(String k)", "public static String settledKey("),
               ("_BEFORE_TAKE = CtNewMethod.make(", "public static int withdraw({PLA} p, String k, String id, int n) {{"),
               ("public MirrorGuard(@IC@ c) {", "public BagMirror(String key) {{"),
               ("public boolean owns(@IC@ c) {", "public static @IQ@[] attach("),
               ("public int fit(String id) {", "_BEFORE_TAKE.setBody("),
               ("public static @PKG@.LinkRec recOf(", "public static @IQ@[] attach("),
               ("public static void closed(java.util.UUID u, Object w) {", "public void accept(Object ev) {\n  try { @PKG@.BenchLink.closed("),
               ("public MirrorClose(java.util.UUID u, Object w)", "public static void hook("),
               ("public static void hook(", "public static Object onExtras("),
               ("public static void chestFix(", "public static void outbound("),
               ("public static Object onExtras(", "public static void outbound("),
               ("public static void outbound(", "public boolean test(@PR@ pr, @PKT@ pkt) {\n  try {\n    if (pkt instanceof @UW@"),
               ("public static boolean preCraft(", "    @PKG@.BenchLink.preCraft(p, pr.getUuid(), this.id);"),
               ("public PreCraftTask(@PR@ pr", "w.execute(new @PKG@.PreCraftTask("),
               ("public static int park(", "public static void link("),
               ("public static void retire(", "public static @IQ@[] attach("), ("public static boolean refresh(", "public static void link("),
               ("public static void prune(", "public static void link("), ("public static void pocketCheck()", "public static void link("),
               ("public void refillFor(", "public void refill() {"), ("public void refill() {", "public @MERS@ getExtraResourcesSection() {"),
               ("public @MERS@ getExtraResourcesSection() {", "public @IC@ craftContainer("), ("public @IC@ craftContainer(", "public void handleAction(@REF@ ref"),
               ("public void invalidateExtraResources() {", "public void handleAction(@REF@ ref"),
               ("public PocketCraftWindow() {", "return new @PKG@.PocketCraftWindow();"),
               ("public PocketSupplier() { }", "public static synchronized void pocketStart() {"),
               ("public CraftPacketFilter() { }", "public static synchronized void start() {"),
               ("public CraftInFilter() { }", "public static synchronized void start() {"),
               ("public static synchronized void pocketStop() {", "public static synchronized void stop() {"),
               ("public static synchronized void stop() {", "public static synchronized void start() {"),
               ("public static void link(", "{PKG}.BenchLink.link(p, pr.getUuid(), wins, System.currentTimeMillis());"),
               ("public static void linkKeys(", "public static synchronized void reload() {"),
               ("public static volatile boolean CHEST_FIX = false;", "public static void chestFix("),
               ("public static volatile boolean CHEST_FIX = false;", "kit = CFG.emit("),
               ("public static synchronized void start() {", "pl.addMethod(CtNewMethod.make(_START_JAVA, pl))"),
               ("public static synchronized void stop() {", "  try {{ {PKG}.BenchLink.stop(); }}"),
               # review fixes: the pocketApply stub before its callers (linkKeys, pocketChanged, pocketCheck), its body after the swap
               # methods; STARTED / POCKET_CRAFT before their readers; the two new hook calls after hook() exists; the rebuild skip after
               # ProcBench.item; the bags.pocketCraft-off help lines before their reader
               ("_POCKET_APPLY = CtNewMethod.make(", "public static void linkKeys("),
               ("_POCKET_APPLY = CtNewMethod.make(", "public static void pocketChanged(String key) {"),
               ("_POCKET_APPLY = CtNewMethod.make(", "public static void pocketCheck()"),
               ("public static synchronized void pocketStop() {", "_POCKET_APPLY.setBody("),
               ("_POCKET_APPLY.setBody(", "public static synchronized void stop() {"),
               ("public static volatile boolean STARTED = false;", "public static void pocketCheck()"),
               ("public static volatile boolean POCKET_CRAFT = true;", "public static void linkKeys("),
               ("public static volatile boolean POCKET_CRAFT = true;", "public void refillFor("),
               ("public static void hook(", "    hook(rec, w, u);   // review fix 2: a declined bench"),
               ("public static void hook(", "    hook(rec, w, u);   // review fix 2: the record this task made"),
               ("public static {ITM} item(String id) {{", "if ({PKG}.ProcBench.item(id) == null) continue;   // 0.7.12 review fix 4"),
               ("RF_HELP_B = (", "public static final String[] HELPB = new String[] { "),
               ("public static final String OFFSRVB = ", "@PKG@.RefillPref.OFFSRVB")):
    assert 0 <= s.find(_a) < s.find(_b), "order: %s before %s" % (_a[:60], _b[:60])
assert s.count('("bags.benchChests", "Bench chest count fallback"') == 1 and s.count('"#bags.benchChests=false",') == 1 \
    and s.count("    linkKeys(p, first);") == 1
# review fixes: each exactly once
assert s.count('("bags.pocketCraft", "Bags in inventory crafting"') == 1 and s.count('"#bags.pocketCraft=true",') == 1 \
    and s.count("after=SackCfg.pocketChanged") == 1 and s.count("_POCKET_APPLY.setBody(") == 1
assert s.count("hook(rec, w, u);   // review fix 2:") == 2 and s.count("if ({PKG}.ProcBench.item(id) == null) continue;") == 1
assert s.count('@PKG@.SackCfg.POCKET_CRAFT ? "Benches and inventory crafting use the materials') == 1 \
    and s.count("RefillPref.HELPB[m]") == 1 and s.count("RefillPref.OFFSRVB") == 1
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
