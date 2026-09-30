# Vault arrows: why a plain click only lifts the arrow, and how to fix it

*Written 2026-09-30. Research only. Nothing built, nothing deployed.*
*Trigger (Skyy in game, SkyyVault 0.1.4 live, verbatim): "arrow button works, but not when i click it, i have to set it back down".*
*Lock this must meet (OPEN-QUESTIONS, LOCKED 2026-09-25): "a plain click turns the vault page immediately, the same as shift-click."*
*Other lock in play (OPEN-QUESTIONS, APPROVED 2026-09-25): "cycle pages inside the vault GUI with the existing in-chest Prev/Next arrows.
Do not add a second page-switch UI."*

**How claims were checked.**
- **[E]**: read from `HytaleServer.jar` bytecode with javassist `InstructionPrinter` and reflection.
- **[C]**: read from the client's own files: `Client/Data/Game/Interface/**.ui`, `Client/Data/Shared/Language/en-US/client.lang`, and the
  string table of `HytaleClient.exe`. The exe is .NET native code, so it gives names but not logic.
- **[M]**: read from installed mods in `UserData/Mods` (253 jars scanned).
- **UNVERIFIED**: the real game still has to show it. All of these are collected in section 9.
- All game files were read-only. Scratch lived in `tools/dev/scratch/vaultclick/` and was deleted afterwards.

---

## 1. Verdict in plain words

1. **In the vanilla chest window, the server hears nothing when you pick an item up.** The client lifts the arrow onto the cursor on its
   own. It tells the server only when the arrow lands somewhere: a slot, the same slot, or outside the window. So a plain click can
   never turn the page at once in the chest window. This is how the engine is built. It is not a SkyyVault bug (section 2).
2. **The server also cannot tell the client "this item cannot be lifted" in a vanilla chest.** A slot on the wire carries only an item
   id, a quantity, durability, quality and metadata. An item definition has no "locked" or "unmovable" field either. Every slot lock in
   the modding scene (ours, CarryChest, UnstableRifts, EndgameAndQoL, TerrariaAddons) is a server-side filter that refuses the move
   after the client has already lifted the item. The only switch that stops lifting is the UI property `AreItemsDraggable: false` on an
   `ItemGrid`. The vanilla chest panel is a client file the server cannot change (section 5).
3. **Three gestures already turn the page at once today**, because their packets need no destination:
   - Transfer (shift-click);
   - the Drop key over the arrow;
   - the chest header buttons (bulk actions, which never turn a page by design).
4. **The only way to get "one plain click = page turns" is to draw the arrows ourselves on a custom page.** Use an `ItemGrid` with
   `AreItemsDraggable: false` plus a `SlotClicking` event binding. SkyyMenu's launcher grid has used exactly that pattern live since
   2026-09-23 ("menu WORKS"). It sends the click on the first press and nothing gets lifted. The open question is how the vault slots
   show next to such a page (probes P1/P2, section 8).

**Recommended fix:**
1. Ship the hint text now (fix c).
2. Run two UI probes.
3. If a probe passes, open the vault as our own vanilla-look chest page whose bottom arrow row is a non-draggable, click-bound grid
   (fix e1). The in-chest item arrows stay as the chest-mode fallback.
4. This needs Skyy's OK because of the "no second page-switch UI" lock. The arrows stay arrows in the vault GUI; only who draws them
   changes.

---

## 2. Everything the client can send about inventory [E]

`com.hypixel.hytale.protocol.packets` holds **139 client-to-server packet classes** (every class that implements `ToServerPacket`). The
ones that can touch an inventory or a window are listed below. Nothing else in the list (movement, chat, builder tools, asset editor,
voice, world map, camera) carries a slot.

| ID | Packet | Fields | Server handler -> engine call |
|---|---|---|---|
| 175 | `inventory.MoveItemStack` | fromSectionId, fromSlotId, quantity, **toSectionId, toSlotId** | `InventoryPacketHandler.handle(MoveItemStack)` -> world thread -> `InventoryUtils.moveItem` -> `ItemContainer.moveItemStackFromSlotToSlot` |
| 176 | `inventory.SmartMoveItemStack` | fromSectionId, fromSlotId, quantity, moveType (`EquipOrMergeStack`, `PutInHotbarOrWindow`, `PutInHotbarOrBackpack`) | `InventoryUtils.smartMoveItem`: `combineItemStacksIntoSlot` over every open window (merge), or `moveItemFromCheckToInventory` / `moveItemStackFromSlot` |
| 174 | `inventory.DropItemStack` | inventorySectionId, slotId, quantity | fires ECS event `DropItemEvent$PlayerRequest(section, slot)` (cancellable) **before** anything moves, then `getSectionById` -> `removeItemStackFromSlot(slot, qty)` -> `ItemUtils.throwItem` |
| 179 | `inventory.InventoryAction` | inventorySectionId, type (`TakeAll`, `PutAll`, `QuickStack`, `Sort`), actionData | `takeAllWithPriority` / `takeAll` / `putAll` / `quickStack` / `sortItems` on the window container (section id 0 = `sortStorage` of the player) |
| 177 | `inventory.SetActiveSlot` | inventorySectionId, activeSlot | hotbar / utility / tool selection |
| 171, 172, 173, 178 | `SetCreativeItem`, `DropCreativeItem`, `SmartGiveCreativeItem`, `SwitchHotbarBlockSet` | creative library | creative only |
| 203 | `window.SendWindowAction` | window id + `WindowAction`: `SortItemsAction`, `SelectSlotAction(slot)`, `SetActiveAction`, `CraftItemAction`, `CraftRecipeAction`, `CancelCraftingAction`, `ChangeBlockAction`, `TierUpgradeAction`, `UpdateCategoryAction` | `GamePacketHandler.handleSendWindowAction`: `ValidatedWindow.validate` (a failure closes the window), then `Window.handleAction(ref, store, action)` |
| 202, 204 | `window.CloseWindow`, `window.ClientOpenWindow` | window id / window type | close; the client asks for pocket-crafting-type windows |
| 219 | `interface_.CustomPageEvent` | type (`Acknowledge`, `Data`, `Dismiss`), data (JSON) | custom pages only: `CustomUIPage.handleDataEvent` |
| 111 | `player.MouseInteraction` | clientTimestamp, activeSlot, itemInHandId, screenPoint, mouseButton, mouseMotion, worldInteraction | `InteractionModule.doMouseInteraction` -> `PlayerMouseButtonEvent` (world input; see 4.8) |

**Proof that no "picked up" signal exists [E]:**
- **(1) No such packet.** None of the 139 packets means "item lifted onto the cursor" or "cursor holds X".
- **(2) No cursor on the server.** The only section ids are the `InventoryComponent` constants HOTBAR -1, STORAGE -2, ARMOR -3,
  UTILITY -5, TOOLS -8, BACKPACK -9, DUMMY -10, plus non-negative window ids. There is no cursor section, and no cursor field on
  `Player` or `InventoryComponent`.
- **(3) A move needs both ends.** `MoveItemStack` carries both ends of the move in one packet, so the client can only send it once it
  knows where the item lands.

**Client side [C].** The client's input actions (client.lang `settings.bindings.*`) are:
- UI actions: `UiPickItem`, `UiPickHalf`, `UiPickOne`, `UiSmartMove`, `UiPlaceOne`, `UiResizeStackUp/Down`;
- `DropItem`, `HotbarSlot1-9`;
- `ContainerTakeAll/PutAll/QuickStack/Sort`.

The item-tooltip action hints are "Take Half", "Take One", "Transfer", "Drop", "Place One" and "Resize". Pick / pick half / pick one /
resize are cursor states that only the client knows about.

---

## 3. Every gesture on a vault slot: what the server sees and when

"First press" = the server hears it on the first press, with no lift. Client behaviour is inferred from the packet shapes above.

| Gesture | Packet | Server hears it | SkyyVault 0.1.4 today |
|---|---|---|---|
| Plain left click on the arrow (`UiPickItem`) | none | **never on this click**: the client lifts the arrow | nothing (Skyy's report) |
| ... then click again anywhere, drag-release, or put it back on its own slot | `MoveItemStack(from arrow, to X)` | on the put-down | REMOVE refused on the arrow slot = 1 hit -> page turns, arrow snaps back |
| Take Half / Take One (right-click family), then put down | `MoveItemStack` with a smaller quantity | on the put-down | same as above |
| Resize Stack +/- while holding | none | never | nothing |
| Place One while holding | one `MoveItemStack` per target slot | per target | the arrow's REMOVE is refused -> turns |
| **Transfer / shift-click** (`UiSmartMove`) | `SmartMoveItemStack` (no destination) | **first press** (UNVERIFIED that the client sends it on press; it needs no destination, so nothing forces a wait) | REMOVE refused (via `VView`) -> turns |
| **Drop key** over the arrow (`DropItem`) | `DropItemStack` (section, slot, qty) | **first press** | REMOVE refused -> turns. The engine logs a WARNING "<name> attempted to drop an empty ItemStack!" every time (handler bytecode offsets 151-185) |
| Clicking outside the window while holding the arrow | most likely `DropItemStack` from the original slot (there is no cursor to drop from) | on that second click | turns (UNVERIFIED) |
| Hotbar number key over the arrow (`HotbarSlotN`) | if the client supports it: `MoveItemStack(arrow -> hotbar N)` | first press | turns (UNVERIFIED client support; already in Vault-Arrows-Spec section 5) |
| Double-click on some item (`SlotDoubleClicking` in the client grid) | likely `SmartMoveItemStack(EquipOrMergeStack)` -> `combineItemStacksIntoSlot` over every open window | on the second click | REMOVE tested on many slots -> 2+ hits -> no page action (by design) |
| Header: Take All / Put All / Quick Stack / Sort (buttons in client `ContainerPanel.ui`: `#TakeAllButton #PutAllButton #QuickStackButton #AutosortButton`, plus their keybinds) | `InventoryAction(window id, type)`; the client *might* send `SendWindowAction(SortItemsAction)` for Sort | first press | bulk: 2+ hits or ADD only -> no page action (by design) |
| Hover | none (the vanilla grid sends no hover) | never | - |
| Esc / close | `CloseWindow` | first press | `VWindow.onClose0` |

**So Skyy's observation is exactly what the engine predicts:** click = client-only lift; put-down = the first packet = the page turns.

---

## 4. Server hooks SkyyVault can use [E]

| # | Hook | Fires on | Use for the arrows |
|---|---|---|---|
| 4.1 | `ItemContainer.setSlotFilter(FilterActionType{ADD,REMOVE,DROP}, short, SlotFilter)` | every move / remove / add attempt that the global filter lets through, **before** anything moves | **used today** (`VBtnFilter`): the refused REMOVE is the click |
| 4.2 | `ItemContainer.registerChangeEvent(Consumer)` / `(short slot, Consumer)` | only **successful** transactions: `sendUpdate(tx)` starts `if (!tx.succeeded()) return;` | not a click signal (a refused move fires nothing) |
| 4.3 | `ValidatedWindow.validate(ref, accessor)` | before every inventory packet that names the window (`getSectionById`) and every `SendWindowAction` | used for the profile-switch gate; too coarse for clicks |
| 4.4 | `Window.handleAction(ref, store, WindowAction)` | `SendWindowAction` for this window id. `Window.handleAction` is empty; `ContainerWindow` (our `VWindow`'s parent) does **not** override it; `ContainerBlockWindow` handles only `SortItemsAction` (-> `sortItems` + `invalidate`) | side finding: if the chest's sort button sends `SortItemsAction`, the vault ignores it today. `VWindow` could override `handleAction` (UNVERIFIED which packet the button sends) |
| 4.5 | ECS `DropItemEvent$PlayerRequest` (cancellable; `getInventorySectionId()`, `getSlotId()`) | Drop key, before removal | could turn the page on Drop and cancel the event, which also removes the engine WARNING. Pattern: SkyyIslands `GuardDrop`, SimpleEnchantments `DropItemEventSystem` [M]. Needs one new ECS system class (rule: ONE registerSystem per class) |
| 4.6 | ECS `InventoryChangeEvent`, `InventoryActiveSlotRequestEvent`, `InventorySetActiveSlotEvent` | the player's own inventory components / hotbar selection | not the vault window |
| 4.7 | Custom page `CustomUIEventBindingType`: `Activating, RightClicking, DoubleClicking, MouseEntered, MouseExited, ValueChanged, ElementReordered, Validating, Dismissing, FocusGained, FocusLost, KeyDown, MouseButtonReleased, SlotClicking, SlotDoubleClicking, SlotMouseEntered, SlotMouseExited, DragCancelled, Dropped, SlotMouseDragCompleted, SlotMouseDragExited, SlotClickReleaseWhileDragging, SlotClickPressWhileDragging, SelectedTabChanged` | clicks on OUR page's elements (`CustomPageEvent`) | **the only first-click signal**: `SlotClicking` on a non-draggable `ItemGrid` (SkyyMenu payload `{"a":"mslot","SlotIndex":3}`), or `Activating` on a TextButton (the VaultPage `#SkyyVPrev` / `#SkyyVNext`, build lines 2203-2204) |
| 4.8 | `PlayerMouseButtonEvent` (event bus, from `MouseInteraction`) | world mouse input | almost surely not sent while a UI page has the mouse (UNVERIFIED; CarryChest / partypro use it for world clicks only [M]). Not a way in |

Payload fields of the custom grid events, from HyUI's event classes [M] (a third-party library, so the exact keys are UNVERIFIED on our
client):
- `Dropped` / `SlotMouseDragCompleted`: SlotIndex, SourceItemGridIndex, SourceSlotId, SourceInventorySectionId, ItemStackId,
  ItemStackQuantity, PressedMouseButton.
- `SlotClickPressWhileDragging`: DragItemStackId, DragSourceInventorySectionId, DragSourceSlotId, ClickMouseButton, ClickCount.

---

## 5. Can the client be told not to lift the arrow? (fix b)

**No, not inside the vanilla chest window.** Evidence:

| Candidate | Finding |
|---|---|
| Slot data on the wire [E] | `InventorySection` = `short capacity` + `Map items` only. Each item is `ItemWithAllMetadata` = itemId, quantity, durability, maxDurability, quality, overrideDroppedItemAnimation, metadata. No lock, filter or flag. Server `SlotFilter`s never leave the server. |
| Item definition [E] | `protocol.ItemBase` (49 fields: model, icon, maxStack, quality, tool/weapon/armor/utility, interactions, carryInteractions, ...) has no "unmovable", "locked" or "no drag" field. |
| Item quality [E] | `protocol.ItemQuality`: textures, textColor, localizationKey, visibleQualityLabel, renderSpecialSlot, hideFromSearch. Looks only. |
| Item metadata the client understands [C][E] | the client has `ClientItemMetadata`, `ItemDisplayMetadata` (per-stack name/description, used today) and `AdventureMetadata` (`Cursed` bool: portal items, a cursed icon overlay, deleted by `CursedItems`). Nothing that blocks lifting. |
| Window data keys [E] | the only key vanilla ever sends for a Container window is `blockItemId` (`ContainerBlockWindow`), plus the generic `needRebuild`. Bench windows use `processingSlots`, `processingFuelSlots`, `tierLevel`, ... No "read-only" or "locked" key exists. |
| `PreventInventoryAccess` component [E] | a whole-player flag: `blocksInventoryAccess` drops every inventory packet. The client learns it through `PreventInventoryAccessUpdate`. It is all or nothing, not per slot. |
| Client ItemGrid properties [C] | the property table next to the ItemGrid events in `HytaleClient.exe` lists: `SlotsPerRow, ShowScrollbar, RenderItemQualityBackground, InfoDisplay, AdjacentInfoPaneGridWidth, AreItemsDraggable, FastClickClearsSlot, InventorySectionId, Slots, RenderEmptySlots, AllowMaxStackDraggableItems, DisplayItemQuantity, IsCreativeSource`. **`AreItemsDraggable` is the switch.** It is UI markup. The vanilla `ContainerPanel.ui` chest grid does not set it (so it defaults to draggable). The vanilla `Hud/Hotbar.ui` and `Hud/CarriedBlockHotbar.ui` set it to `false`. The server cannot edit a vanilla client page. It sets it only on its own custom pages (SkyyMenu, SkyyAuctions and SkyyEssentials trade already do). |
| `InfoDisplay` [C] | client enum `ItemGridInfoDisplayMode` ("ItemGrid.SlotsPerRow cannot be less than 3 when using InfoDisplayMode.Adjacent"). It sets the tooltip / info pane mode. `InfoDisplay: None` is our fix for stuck tooltips (Auction-House-Spec line 43; vanilla `ItemQuantityPopup.ui`). It has nothing to do with dragging. |
| `ItemGridSlot` flags [E][C] | server `ItemGridSlot`: itemStack, background, overlay, icon, name, description, isItemIncompatible, isActivatable, skipItemQualityBackground, isItemUncraftable. The client adds InventorySlotIndex, ExtraOverlays, IsLabelSlot and LabelText. These exist only for a custom page grid's `Slots`, never for a window's contents. `IsActivatable` = the slot reacts to clicks (SkyyMenu sets it on tiles that have an action). `IsItemIncompatible` = the red "can't go here" look. None locks lifting. |
| Other mods [M] | every "slot lock" found is server-side: CarryChest (`InventorySetActiveSlotEvent` + `PlayerMouseButtonEvent` cancels), UnstableRifts `InventoryLockService` (`SlotFilter.DENY` + `ALLOW_OUTPUT_ONLY`), EndgameAndQoL / TerrariaAddons pouches (`setSlotFilter`), Lootr. None stops the client lift. No installed mod uses `openCustomPageWithWindows` except SkyyEssentials, SkyySacks and SkyyVault, and no `.ui` file anywhere (Assets.zip or mods) sets `InventorySectionId`. So there is nothing working to copy for P1/P2. |

**So fix (b) is only possible as fix (e1):** an arrow grid on a custom page.

---

## 6. How SkyyVault 0.1.4 works today (`SkyyVault/build_skyyvault_0.1.4.py`)

**Opening the vault.**
- `open2` (line 2836) opens the vault in one of two modes:
  - chest mode: `setPageWithWindows(Page.Bench, VWindow)`, line 2873;
  - page mode (the `openMode` default): `openCustomPageWithWindows(VaultPage, VWindow)`, line 2871.
- In both modes the window's container is a `VView`, capacity 45 (36 storage + a control row).
- Control row: Prev at 36, info at 40, Next / Buy at 44, fillers in between.

**Filters and click detection.**
- `newSession` (line 2717) registers one `VBtnFilter` for ADD, REMOVE and DROP on every control index (lines 2740-2742).
- `VBtnFilter.test` (line 3661) touches no container. It always refuses. On REMOVE it calls `VSession.noteHit(slot)` (line 1676),
  and the first hit of a batch queues one `VBtnTask` through `queueBtn` (line 2514), which runs on the viewer's world thread.
- `VView` (lines 1874-1899) turns the engine's null result for a refused whole-slot move into a failed `MoveTransaction`, so
  shift-click and Take All no longer throw.

**The batch task, `btnBatch` (line 3489):**
1. restores the canonical row;
2. `resync` (line 3200) re-sends the window and all six inventory sections (`invalidate` + `markDirty`);
3. sweeps strays;
4. turns the page only when exactly one control slot was hit and storage did not change in or 100 ms before the batch. It then calls
   `btnClick` (line 3429): Prev/Next -> `gate` + `swap`; Buy -> `VStore.intent`; info / first / last -> a chat line.

**Why the reported behaviour follows.** The design treats "the refused attempt is the click" (0.1.2). A plain click produces no attempt
until the put-down (sections 2-3). Everything else in the design is sound: no leaks, a correct batch decision, instant shift-click and
Drop.

**Page mode already has instant buttons.** `VaultPage` has `< Prev` / `Next >` TextButtons bound with `Activating` (lines 2203-2204),
and a TextButton click reaches the server at once. Whether the client draws the vault window's slots next to a custom page has been
UNVERIFIED since 0.1.1 (0.1.4 header, test step 2, and the "Vault slots not showing next to this page? Click Open as chest." hint). No
test result is recorded in HANDOFF or TEST-CHECKLIST (the SkyySacks `/pd` inventory-panel experiment in TEST-CHECKLIST line 41 is also
still unticked).

---

## 7. The fixes, ranked

| Rank | Fix | Meets "plain click turns at once"? | Proof status | Cost / risk | Lock conflict |
|---|---|---|---|---|---|
| **1 (target)** | **(e1) Arrow row drawn by OUR page**: the vault opens as a SkyyVault custom page in the vanilla look (kit `tools/skyyui.py`), with the vault window. The bottom row is an `ItemGrid` with `AreItemsDraggable: false; InfoDisplay: None`, slots = `new ItemStack("Skyy_Vault_Prev"/..., 1)` + `setName` / `setDescription` + `setActivatable(true)`, bound with `SlotClicking` (`locksInterface=false`) -> `btnClick` logic on the first press, no lift, no snap-back, no filter needed for the row. | **Yes** | event + no-lift proven live by SkyyMenu (HANDOFF 2026-09-23 "menu WORKS"); how the vault slots show beside the page = probes P1/P2 (UNVERIFIED) | medium: a new page + reuse of `swap` / `btnClick`; the window keeps `VView` + filters for storage; about 0.5-1 build round after the probes | the arrows stay arrows inside the vault GUI and no second switch is added, but it changes the approved look -> **ask Skyy** |
| **2 (do now)** | **(c) Teach the instant gestures**: the arrow tooltips + the chest opening line say "Shift-click (Transfer) or press your Drop key on an arrow to turn at once. A plain click lifts it; the page turns when you put it down." Optional: a `DropItemEvent$PlayerRequest` system turns the page on Drop and cancels the event (no engine WARNING spam). | No (a plain click stays two-step) | shift-click / Drop packets carry no destination [E]; that the client sends them on the first press is UNVERIFIED but expected | tiny: text only (+ optionally one ECS system class) | none |
| 3 | **(d) Page mode's existing Prev / Next / number buttons** (`Activating`) as the main switch; chest arrows as the fallback. Zero code: Server Setup -> Vault -> Open /vault as: Page view. | Yes (TextButtons are instant) | UNVERIFIED that the window shows next to the page (= probe P1) | none to try | yes: the buttons are the "second page-switch UI" the lock turned down, and they are not "arrows in the chest" -> Skyy decides |
| - | **(a) Turn on a first-click signal from the vanilla chest** | - | **impossible**: no such packet, no server cursor [E] (section 2) | - | - |
| - | **(b) Make the chest arrows un-liftable** | - | **impossible in `Page.Bench`**: no wire flag; the only switch is custom-page markup [E][C] (section 5); becomes (e1) | - | - |
| - | (e2) Reuse a chest header button (Sort / Quick Stack) as "Next page" | technically first press | the tooltip is client text ("Sort Items by Type"), it breaks sorting, and it is invisible as an arrow | - | rejected |
| - | (e3) Hover, world mouse events, timed window re-sends | no | the vanilla grid sends no hover; `MouseInteraction` is world input; a re-send is no signal | - | rejected |
| - | (e4) `arrowLayout=inside` or a second 1-slot window for the arrows | no | still a vanilla `ContainerPanel` grid: same client lift | - | rejected |

---

## 8. Recommended plan

### Step 1: SkyyVault 0.1.5 (copy + edit of 0.1.4, text only) and SkyyUiProbe 0.3 in the same round

**Vault 0.1.5 (fix c):**
- New arrow tooltip lines (`VBtn.row`, line ~1840): "Click, then click again (or put it back) to turn. Shift-click or your Drop key
  turns at once."
- Chest opening line (line 2880): "...the arrows in the bottom row turn pages (shift-click = instant), Esc saves."
- Optional: turn the page on the Drop key through `DropItemEvent$PlayerRequest` and cancel it, which ends the WARNING per Drop.
- Optional side finding: a `VWindow.handleAction` override that sorts on `SortItemsAction` (4.4). Only needed if Skyy reports that Sort
  does nothing in the vault.

**UiProbe 0.3 (Skyy opens each probe once; each takes about 30 s):**
- **P1 `/skyprobe win`**: a small custom page opened with `openCustomPageWithWindows(page, ContainerWindow(SimpleItemContainer 9, 3
  dummy items))`. Questions: does the client draw the 9 slots and the player's inventory? Can you drag between them? Where does the
  panel sit relative to the page? This answers the 0.1.1 UNVERIFIED (1), the SkyySacks `/pd` experiment and the TradePage question
  together.
- **P2 `/skyprobe secgrid`**: the same, plus an `ItemGrid` on the page with `InventorySectionId: <window id>` and a second one with
  `InventorySectionId: -2` (player storage). Questions: do they show the real items, and do drags between them move items (server log:
  `MoveItemStack` handled; count before and after)? The property exists in the client's ItemGrid table [C] and in HyUI's builder [M],
  but no one has seen it bound to a window.
- **P3**, folded into P1: a 3-slot non-draggable arrow grid with `SlotClicking`. A press prints a chat line, and nothing lifts. This is
  already proven by SkyyMenu; it only confirms the arrow icons.

### Step 2: SkyyVault 0.1.6, after Skyy's probe results and Skyy's OK on the lock

- **If P1 passes (the client draws the window beside the page):**
  - `/vault` opens our chest page (vanilla frame, kit) with the vault window.
  - The window gets `arrowLayout` none, so it holds just the 36 storage slots.
  - The page shows the arrow grid: [Prev][fillers][page info][fillers][Next / gold Buy], bound with `SlotClicking`.
  - `SlotIndex` -> the same decision as `btnClick` (Prev / Next / Buy with `buyConfirmCoins` / info / first / last).
  - The page label and row are redrawn with `b.set` / `sendUpdate` after a flip, never on a timer, never by closing and reopening.
- **If only P2 passes:** the same page draws the vault slots itself (grid bound to the window id) and the player inventory (grids bound
  to -1 / -2).
- **If neither passes:** keep 0.1.5. Tell Skyy plainly that a vanilla chest cannot do a one-click arrow; shift-click / Drop are the
  instant ways.
- **In every case, chest mode (`Page.Bench`) keeps today's item arrows, filters and sweep unchanged as the fallback.**

**Rules to carry into 0.1.6:**
- UI (HANDOFF section 2): inline page, no underscores in ids, root anchor Width/Height only, never close a page right before opening
  another, big readable page.
- Every colour, texture and sound comes from `tools/skyyui.py`.
- `ItemGridSlot` only ever gets `new ItemStack(id, 1)`: never the metadata-carrying control stacks (the 2026-09-25 AH disconnect).
- The vault storage keeps `VView` + change sync + counting before and after.
- `btnClick` runs on the world thread (a page event arrives on it already; keep the gate + swap order).
- Buy keeps `BUY_GUARD_MS` (a double press on the grid must not buy two pages).
- Profile-switch close and the stray sweep stay as in 0.1.4.

---

## 9. UNVERIFIED (needs the game) and in-game checks

| # | Question | Default if untested |
|---|---|---|
| V1 | Does the client send `SmartMoveItemStack` on the shift-click press (before release)? | expected yes: the packet has no destination |
| V2 | Does the Drop key over a window slot send `DropItemStack` at once, and does clicking outside the window with a lifted arrow send a Drop? | yes for the key, likely for outside |
| V3 | Does a hotbar number key over a window slot move it (instant `MoveItemStack`)? | unknown |
| V4 | Which packet the chest's Sort button sends for a non-block window (`InventoryAction Sort` works; `SortItemsAction` would be ignored by `ContainerWindow`) | InventoryAction |
| V5 | **P1**: a Container window opened with a custom page is drawn by the client (slots + player inventory) | unknown since 0.1.1 |
| V6 | **P2**: a custom-page `ItemGrid` with `InventorySectionId` shows and drags a window's real slots | unknown |
| V7 | `PlayerMouseButtonEvent` is not fired while a page is open | expected not fired |
| V8 | HyUI's event payload key names match our client (only needed if 0.1.6 uses Dropped / drag events; the arrow row needs only `SlotIndex`, proven by SkyyMenu) | - |

**Steps for Skyy with 0.1.4 (no new build needed):**
1. Open `/vault` (chest mode). Shift-click the Next arrow: does the page turn on the press, with no lift? (V1)
2. Hover the Next arrow and press your Drop key: the page turns, nothing is thrown. (V2)
3. Lift the arrow with a plain click, then click outside the chest window: does the page turn, and does the arrow come back? (V2)
4. Hover the arrow and press 1-9: does anything happen? (V3)
5. Press the chest's Sort button with a few mixed items in the vault: are they sorted? (V4)
6. Server Setup -> Vault -> Open /vault as: Page view, then `/vault`: do the vault slots show next to the page, and is your inventory
   there too? If yes, click the page's Next: the slots switch on one click. (V5, fix d preview.) Switch back to Chest window afterwards
   if you prefer.

---

## 10. Engine references (for the build pass)

- `InventoryPacketHandler`: `lambda$handle$5` (Move), `$6` (SmartMove), `$4` (Drop; `DropItemEvent$PlayerRequest` at 59-83, the
  empty-drop WARNING at 151-185), `$8` (InventoryAction; the Sort window branch at 397-435, section 0 = `sortStorage`),
  `blocksInventoryAccess` (`PreventInventoryAccess` archetype check).
- `GamePacketHandler.handleSendWindowAction` (validate, then `Window.handleAction`); `handleMouseInteraction` ->
  `InteractionModule.doMouseInteraction` -> `PlayerMouseButtonEvent`.
- `ItemContainer.lambda$internal_moveItemStackFromSlot$5`: `cantRemoveFromSlot` (offset 6) before `cantMoveToSlot` (66) and
  `cantAddToSlot` (206); `ItemContainer.sendUpdate`: `if (!succeeded) return` (offsets 1-9).
- `ContainerBlockWindow.handleAction`: `SortItemsAction` only; `Window.handleAction`: empty; `ContainerWindow`: no override.
- `PageManager.openCustomPageWithWindows` = `WindowManager.openWindows` + `openCustomPage` + one `OpenWindow` packet per window.
  `setPageWithWindows` = the same with `setPage` (`Page.Bench`). No vanilla code calls `openCustomPageWithWindows`.
- Client: `Interface/InGame/Pages/Inventory/ContainerPanel.ui` (a chest grid without `AreItemsDraggable`); `Interface/InGame/Hud/Hotbar.ui`
  line 69 and `CarriedBlockHotbar.ui` line 32 (`AreItemsDraggable: false`); `Shared/Language/en-US/client.lang` lines 2120-2223
  (inventory actions) and 3651-3661 (UI bindings).
