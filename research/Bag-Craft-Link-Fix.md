# Bags in crafting - diagnosis + fix recipe (2026-10-02)

Skyy, in game with SkyySacks 0.7.10: "neither inventory or bench crafting pull from the bags." Read-only diagnosis by a local agent from the
live HytaleServer.jar bytecode + bare-JVM experiments E1-E5 (all passed). Build it as **SkyySacks 0.7.12 on top of 0.7.11** (0.7.11 = withdraw
amount kept, stack auto-refill, bags add up). Full round (item loss / duplication risk).

## Verdict

- **Benches:** 0.7.10 attaches the bag mirror on the server but never tells the client. It marks the bench's materials section VALID and then
  calls `WindowManager.updateWindow` - the engine only puts the extra-materials list (`ExtraResources`) into that packet when the section is
  INVALID, and the client learns extra materials only from that list. So the client shows inventory-only counts ("Stick 0/4"), greys CRAFT and
  never sends the craft request.
- **Pocket crafting:** a plain `Window` (`FieldCraftingWindow`) - no materials section, no list, crafts from the inventory only
  (`CraftingWindow.craftSimpleItem`). 0.7.10 skips it (no "fed" log line).

## 1. What 0.7.10 does (`SkyySacks/build_skyysacks_0.7.10.py`)

- No event hook: `CraftTick` (lines 3091-3107) every 300 ms queues `CraftLinkTask` (3104).
- `CraftLinkTask.run` (3025-3089): settled key (`SackPool.settledKey`) or `BagMirror.park` while a switch settles; for each open
  `MaterialContainerWindow`: `BagMirror.of(k).sync()`, `rebuild(caps, wantedFor(w))` (36-slot mirror, bench ingredients first, max 4 stacks per
  item), `m.combined = CombinedItemContainer{existing, m.cont}`, `setItemContainer`, `setExtraMaterials(m.quantities())` (drops the vanilla
  chest list), `setValid(true)`, `wm.updateWindow(w)`, log "fed N".
- `BagMirror.sync` (2806-2816) books `slotQty - actual` to the pool once (idempotent); increases are wiped by the next `rebuild`.
- `park` (2962-2991) has the same valid-then-update bug.

## 2. How the engine feeds a bench window and the client

- `BenchWindow.onOpen0` -> `CraftingManager.feedExtraResourcesSection` -> `getContainersAroundBench` (chests in the `CraftingConfig` radius,
  output-only `DelegateItemContainer` wrappers) + a per-item list; section marked valid. `windowData` carries only chest counts / radii.
- `BenchWindow.getExtraResourcesSection()` re-runs the vanilla feed whenever the section is invalid (overwrites container + list - an attached
  mirror is gone). Invalidated after every craft (`SimpleCraftingWindow.handleAction`), each timed-craft unit start, and a tier change.
- The client learns amounts ONLY through `ExtraResources` (item id + quantity list): always in `WindowManager.openWindow`; in
  `clientOpenWindow` (window id 0) for any `MaterialContainerWindow`; in `updateWindow` ONLY if the section is invalid (the 0.7.10 bug). Dirty
  windows are sent by `PlayerSendInventorySystem.tick` on the world thread.
- Craft path: client `SendWindowAction{id, CraftRecipeAction}` -> world thread -> `SimpleCraftingWindow.handleAction` crafts from
  `CombinedItemContainer{inventory, getExtraResourcesSection().getItemContainer()}`. Pocket: `FieldCraftingWindow` (registered in
  `CraftingPlugin.setup` as `Window.CLIENT_REQUESTABLE_WINDOW_TYPES.put(WindowType.PocketCrafting, FieldCraftingWindow::new)`) crafts from the
  inventory only.

## 3. Fix recipe

**A. Bench display - outbound packet filter.** `CraftPacketFilter implements PlayerPacketFilter`
(`com.hypixel.hytale.server.core.io.adapter.PlayerPacketFilter`, `boolean test(PlayerRef, Packet)`): for an `UpdateWindow` / `OpenWindow` with
`extraResources != null` call `BenchLink.onExtras(pr, id, extraResources)`; try/catch Throwable; ALWAYS return false (true blocks the packet).
`onExtras` (world thread only - `World.isInThread()`, else skip + log once): window by id from the player's WindowManager; act only for
`SimpleCraftingWindow` / `ProcessingBenchWindow` (skip `DiagramCraftingWindow` / `StructuralCraftingWindow`); key = `SackPool.settledKey`
(null -> vanilla only); no carried bags -> just `sync()`; else `sec = getExtraResourcesSection()` (valid, no re-feed), `merged =
BagMirror.of(k).attach(sec, er.resources, wantedFor(win), caps)`, `er.resources = merged` (vanilla list + mirror list summed by id, zeros
skipped; when no packet is at hand use `sec.toPacket().resources`). Register in `start()` with `PacketAdapters.registerOutbound(...)` (patch the
`WB.start_java(PKG)` string inside the sacks patch - `tools/skyywbtab.py` is shared with SkyyAccessories); `deregisterOutbound` in `shutdown()`.
Filters run synchronously in `PacketHandler.writePacket` before caching / serializing (E3); the edited list survives a serialize round trip
(E4); every vanilla re-feed passes through at send time. DynamicTooltipsLib uses the same technique on these packets.

**B. BagMirror:** `guard = new DelegateItemContainer(cont); guard.setGlobalFilter(FilterType.ALLOW_OUTPUT_ONLY)` - attach `guard`, never raw
`cont` (E5: crafts still remove through `Combined{inventory, guard}`, inserts are refused; raw `cont` would accept inserts that the next
rebuild wipes = item loss). Add `owns(c)`, static `merge()`, `attach()` (sync -> rebuild -> combined `{vanilla, guard}` (just `guard` if
vanilla is `EmptyItemContainer.INSTANCE`) -> setItemContainer -> setExtraMaterials(merged) -> setValid(true)). One instance per key; `cont`
reused in place. New `park`: `sync()`, `empty()`, `invalidateExtraResources()` on each open window using this mirror.

**C. CraftLinkTask (keep the 300 ms task; drop `setValid(true)` + `updateWindow`):** for each open bench window (and the pocket window): if
the section is valid but not ours, or the pool / carried bags changed since the last attach (a per-key change counter bumped in `SackPool.add`
- every pool writer goes through `add`) -> `((MaterialContainerWindow) w).invalidateExtraResources()` (vanilla re-feeds + sends next tick; the
filter re-attaches); at most once a second per window. No crafting window open -> `sync()`; never drop a mirror a window still holds.

**D. Pocket crafting - swap the window class:** `PocketCraftWindow extends FieldCraftingWindow implements MaterialContainerWindow` with its own
`MaterialExtraResourcesSection` (starts invalid) and `BagMirror mirror`: `getExtraResourcesSection()` refills when invalid (settled key + caps,
else empty; `mirror.sync()`, `rebuild(caps, fieldcraftWanted)` from `CraftingPlugin.getBenchRecipes(BenchType.Crafting, "Fieldcraft")`,
`setItemContainer(mirror.guard)`, `setExtraMaterials(mirror.quantities())`, valid); `invalidateExtraResources()` = `sec.setValid(false);
invalidate();`; `isValid()` = `sec.isValid()`; `handleAction`: non-craft or null recipe -> `super`; else `CraftingManager.craftItem(ref,
store, recipe, qty, new CombinedItemContainer(new ItemContainer[]{ InventoryComponent.getCombined(store, ref, BACKPACK_STORAGE_HOTBAR),
getExtraResourcesSection().getItemContainer() }))`, the vanilla craft sound (`SFX_Player_Craft_Item_Inventory`), `invalidateExtraResources()`;
`onClose0` -> super + `mirror.sync()`. `PocketSupplier implements Supplier` returns a new `PocketCraftWindow`; in `start()`
`prev = Window.CLIENT_REQUESTABLE_WINDOW_TYPES.put(WindowType.PocketCrafting, sup)`, restore `prev` in `shutdown()`; warn if `prev` is null or
the entry is later not ours.

**E. Optional hardening (second click in the same tick):** inbound `PlayerPacketFilter` - for `SendWindowAction` with `CraftRecipeAction` /
`TierUpgradeAction` queue `PreCraftTask` (re-feed + attach if the section is invalid or not ours) before the vanilla handler's task (FIFO).
Without it a second click in the same tick can fail silently (no item loss).

**0.7.11 interplay:** 0.7.11's stack auto-refill pauses while `BagMirror.MIRRORS.containsKey(k)` - with mirrors living longer (pocket
crafting too) that must become an explicit "live" flag; withdraws and refills must sync / rebuild a live mirror (or pause while it is live),
so a bench can never use the same items twice. Mirror contents must never exceed the pool.

## Invariants (exactly-once booking)

1. All mirror removals go through `CraftingManager` on the world thread (instant crafts, timed units, tier upgrades).
2. `sync()` before every `rebuild` / `empty` / `clear`; idempotent.
3. The `guard` refuses inserts.
4. Cancelling a timed craft refunds the started unit to the inventory (a bag-to-inventory move, not a dupe).
5. Queued timed jobs keep the old combined container, which still points at the same `cont`; queues are cancelled on window close.
6. One live mirror per key, only for the settled key; on a key change the old mirror is synced and emptied first.
7. Mirror contents never exceed the pool.

## Other mods (ideas only, licences unknown)

SmartBenches 1.3.1 (ticks the old `ProcessingBenchState`, gone from this server jar - likely broken); UnifiedWorkbench 0.9 (overrides the
Simple_Crafting interaction, `SortedSimpleCraftingWindow extends SimpleCraftingWindow` - confirms window subclassing works); DynamicTooltipsLib
1.6.2 (outbound filter editing the extra-materials list of every OpenWindow/UpdateWindow - same technique, compatible); Clay Factoria (uses
`feedExtraResourcesSection` as a chest finder); ChestRangeMod (tunes the chest search); AutoSort (packet watchers).

## Risks / UNVERIFIED

1. Whether the client applies the list to pocket crafting (window 0) - DynamicTooltipsLib suggests yes; `/craft` stays the fallback.
2. The client might ignore the list when `nearbyChestCount` is 0 - fallback: set it to at least 1 in `windowData` (the chest counter shows 1).
3. The ingredient row shows the "nearby chests" icon - cosmetic.
4. If `/craft` rebuilds the shared mirror with a different wanted set while a bench is open, the display goes stale - track who rebuilt it,
   invalidate the bench window when it differs.
5. Counts show only what the mirror holds (36 slots, max 4 stacks per item); it refills after every craft.
6. A future server moving `PlayerSendInventorySystem` off the world thread -> the filter skips (bags just don't show) and logs once.

## Test plan

Bare JVM (extend the sacks harness): load + `-Xverify:all`; packet mechanics (a recording `PacketHandler`; valid + updateWindow sends no
list, invalidate sends one; the filter via `PacketAdapters.__handleOutbound` merges totals, leaves a null list alone, returns false;
serialize round trip); accounting (pool {Stick 100, Rubble 50} -> attach -> remove [Stick 4, Rubble 2] through `Combined{inv, section}` ->
sync {96, 48}, second sync no change, insert through guard refused, old combined container across a rebuild still books, park syncs then
empties); pocket supplier swap + restore; pocket refill + craft via a test seam.

In game (Skyy): (1) sticks, rubble, logs, cotton scraps only in bags (Omni is fine); (2) Workbench -> Survival -> Campfire shows bag amounts,
CRAFT lit; (3) one craft = exactly -4 sticks, -2 rubble in `/pd`; (4) 5 quick crafts + Craft All - exact totals; (5) Cooking + Alchemy bench;
(6) pick up sticks with a bench open -> count rises within ~1 s; drop the bag -> bag counts vanish; pick it up -> back; (7) inventory
crafting, Accessory Bag recipe uses bag logs + scraps (if still 0/4 -> fallback needed); (8) a second player at the same bench does not see
your bags; (9) profile switch with a bench open -> counts vanish ~6 s, then the new profile's bags; (10) close the bench mid timed craft -> the
started unit returns to the inventory, totals correct; (11) server log: "craft link: attached ..." lines, no "craft link failed".
