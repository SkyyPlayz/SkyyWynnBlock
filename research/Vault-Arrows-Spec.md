# Vault page arrows: SkyyVault 0.1.2 spec (Wynncraft-style arrows inside the chest)

*Written 2026-09-25. Part A below is the SPEC for `SkyyVault/build_skyyvault_0.1.2.py`, to be copied from the LIVE
`build_skyyvault_0.1.1.py` and edited. Appendix R (after Part A) is the research map of 0.1.1 that two earlier passes wrote into
this file today. It stays for its line numbers. Where the appendix and Part A disagree, Part A wins.*
*Skyy's feedback (in game, 2026-09-25): "vault seems to work. if possible could you add arrows in the chest to switch between vaults
like Wynncraft so I don't have to go back to select vault 2". Their screenshots show 0.1.1 in CHEST mode: the vanilla chest window,
vault page 1 of 2, with no way to turn the page except typing `/vault next` or reopening.*
*Design lock kept: no custom UI on the vanilla inventory screen. The arrows are ITEMS inside OUR container, not buttons on the screen.*
*Engine facts marked [E] were checked read-only in this pass against `HytaleServer.jar` (javassist disassembly + `tools/dev/reflect.py`,
`cpgrep.py`), the client's own UI files (`Client/Data/Game/Interface/...`) and `Assets.zip`. Scratch files were deleted afterwards.
Anything the real game still has to confirm is marked UNVERIFIED and collected in section 12.*

---

## 1. Verdict in plain words

**Yes, this can be done cleanly, and without any item ever leaking out of the vault.**

When the vault opens as a chest, the chest gets **one extra row at the bottom**: 5 rows instead of 4. All 36 storage slots stay
yours. The bottom row is a control bar:

```
 row 1-4:  [ your 36 vault slots, exactly as today                                  ]
 row 5:    [ <  ][ ## ][ ## ][ ## ][ Page 2 of 4 ][ ## ][ ## ][ ## ][  > ]
            Prev   dark filler squares   page info    dark filler squares  Next
```

- **Left arrow**: previous page. On page 1 it is a grey "First page" arrow that does nothing.
- **Middle item**: a page icon. Hover it and it reads "Page 2 of 4" with "14 of 36 slots used".
- **Right arrow**: next page. On your last owned page it turns **gold: "Buy page 5 - 75,000 coins"**. Click it once and chat asks you
  to confirm. Click it again within 10 seconds to buy (coins taken once), and the new page opens in place. This is the same confirm
  that the page's Buy button and `/vault buy` already share. At the max page it becomes a grey "Last page" arrow.
- Click an arrow and the chest shows the other page **in place**: no typing, no reopening. The old page is saved first, as every page
  swap already does.

**Why the arrows can never be stolen:** the engine lets a container refuse, slot by slot, every attempt to take or place an item. It
refuses **before anything moves**, so the arrow never leaves its slot, not even for a moment. The refused attempt is exactly the
"click" we listen for. After every click the server re-sends the chest and your inventory to your screen, so a picture of the arrow
that your client drew under your mouse snaps back. A safety sweep also removes any stray vault button item it ever finds (on join,
when the vault closes, and every 30 s) and logs it. By design it should never find one.

**The one thing only the game can tell us (UNVERIFIED U2):** Hytale lifts an item under your mouse on YOUR screen before the server
hears anything. The server only hears when you put the item down, drag it somewhere, shift-click it or press the drop key. So a plain
click may only "lift" the arrow, and the page turns when you let go or click again. Shift-click is a single message to the server, so
it always turns the page at once. Either way the page turns the moment the server hears about it, and the arrow snaps back. The first
in-game test tells us which wording the chat hint should use.

**Admin switches (in game, SkyWynn Menu -> Server Setup -> Vault):** arrows on/off, and where they go ("Extra row", the default, or
"Inside the page", which is Wynncraft-exact: the arrows use 2 of the page's slots and any item stored there is moved out first, never
lost).

---

## 2. What the engine gives us (the facts this design stands on)

| # | Fact [E] | Where it was read |
|---|---|---|
| E1 | **Per-slot filters exist:** `ItemContainer.setSlotFilter(FilterActionType{ADD,REMOVE,DROP}, short slot, SlotFilter)`. `SlotFilter.test(action, container, slot, stack)` returning `false` = refused. `SimpleItemContainer.cantRemoveFromSlot` calls it only while the global filter allows output (`cantAddToSlot`: while it allows input). A DENY_ALL (closed) view therefore never calls our filter. | `SimpleItemContainer.testFilter/cantRemoveFromSlot/cantAddToSlot/cantDropFromSlot` bytecode |
| E2 | **Refused before anything moves.** Slot-to-slot move (`internal_moveItemStackFromSlot` lambda): `cantRemoveFromSlot(from)`, then `cantMoveToSlot`, then `cantAddToSlot(to)`, all before the first `internal_setSlot`. A refusal returns a failed transaction, and `sendUpdate` then does nothing (`if (!succeeded) return`), so no change event fires. Dropping an item ONTO a control slot only asks ADD on it, never REMOVE. | `ItemContainer.lambda$internal_moveItemStackFromSlot$5`, `sendUpdate` |
| E3 | **Our own writes skip the filters.** `setItemStackForSlot(slot, stack, false)`: the boolean is "filter" (false = no `cantAddToSlot`). `clear()` (`SimpleItemContainer.internal_clear`) checks no filter. So `fill`/restore never trigger our filter. | `InternalContainerUtilItemStack.lambda$internal_setItemStackForSlot$0`, `internal_clear` |
| E4 | **Every player gesture on a vault slot lands on REMOVE for that slot.** Drag/put-down = `MoveItemStack` -> `InventoryUtils.moveItem` -> `moveItemStackFromSlotToSlot` (REMOVE on the source). Shift-click = `SmartMoveItemStack` -> `smartMoveItem` -> `moveItemFromCheckToInventory` -> `moveItemStackFromSlot` (REMOVE; it may test the same slot more than once, once per target container). Drop key = `DropItemStack` -> `removeItemStackFromSlot(slot, qty)` with filter=true -> **REMOVE**. It never asks DROP, which only `dropAllItemStacks` asks. | `InventoryPacketHandler` handlers + `InventoryUtils` bytecode |
| E5 | **The chest's bulk buttons also test our slots, but always many at once.** Take All = `takeAllWithPriority`: REMOVE on every NON-EMPTY slot, in slot order. Sort (`InventoryAction` Sort on a window) = `container.sortItems`: REMOVE on EVERY slot before collecting (and again while placing back). It skips refused slots, so the arrows stay put. The "merge stack" smart move (`EquipOrMergeStack` -> `combineItemStacksIntoSlot` over every open window) does REMOVE per slot. Put All / Quick Stack / shift-click INTO the vault only ask ADD. | same |
| E6 | **No server-side cursor.** The server only sees whole from->to transfers. The item under the mouse is the client's own drawing. | `InventoryComponent` constants, packet fields (Appendix R16.1) |
| E7 | **Re-sending the truth to the client is built in.** `WindowManager` registers a change listener per window (`markWindowChanged` -> `Window.invalidate()`), and `PlayerSendInventorySystem` calls `updateWindows()` every tick, sending `UpdateWindow` with the whole container for each dirty window. For the player's own inventory it sends a full `UpdatePlayerInventory` when any `InventoryComponent` `consumeIsDirty()`. **So `s.window.invalidate()` + `InventoryComponent.markDirty()` = "send the chest and the inventory again next tick"** (the drop handler itself calls `markDirty()`). | `WindowManager.lambda$setWindow0$0/updateWindows/updateWindow`, `PlayerSendInventorySystem.tick` |
| E8 | **Filters are reentrant-safe.** The container lock is a `ReentrantReadWriteLock`, and the refusal branch never touches the container again (Appendix R16.3). We still keep `test()` free of container calls (section 4). | Appendix R16.3 |
| E9 | **The chest window draws any capacity in rows of 9.** The vanilla chest panel `ContainerPanel.ui` is one `ItemGrid #ItemGrid { SlotsPerRow: 9 }` (`@DefaultItemSlotsPerRow = 9`, slot 74 px) with no height or row limit. The server sends a bare `short capacity` (`InventorySection`). **45 slots = 5 rows of 9.** Vanilla chests are only 18 and 36 (Assets.zip `Capacity` values), so a 5-row chest is new ground: see U1. | client `Game/Interface/InGame/Pages/Inventory/ContainerPanel.ui`, `InGame/Common.ui`; Assets.zip |
| E10 | **Per-stack name + description:** `stack.withMetadata(ItemDisplayMetadata.KEYED_CODEC, new ItemDisplayMetadata(Message name, Message desc))` (key `ItemDisplay`) replaces the tooltip name/description of THAT stack. It is the SimpleEnchantments method (a working installed mod) and has been live in SkyyRolls since 0.1.3 (`withDisplay`, `Message.raw(..).color("#hex")`). | `ItemDisplayMetadata` reflect; `SkyyRolls/build_skyyrolls_0.1.5.py` ~549 |
| E11 | **Hiding items from the creative item library:** an item Quality with `"HideFromSearch": true` (vanilla `Debug` and `Template` use it). A mod can ship its own quality at `Server/Item/Qualities/<Id>.json` (18 installed mods do). | Assets.zip `Server/Item/Qualities/*.json`; `ItemQuality.HideFromSearch` |
| E12 | **Own item icons:** a PNG at `Common/Icons/ItemsGenerated/<Id>.png` in the jar, referenced as `"Icon": "Icons/ItemsGenerated/<Id>.png"` (117 installed mods do this; vanilla icons are 64x64). No Skyy mod has shipped its own PNG yet, so SkyyVault 0.1.2 is the first. | installed Mods scan; Assets.zip |
| E13 | `ItemStack(String id, int qty)`, `withMetadata(String, BsonValue)`, `getMetadata()`; `InventoryComponent.markDirty()`; `Window.invalidate()`; `InventoryComponent$Storage/$Hotbar/$Backpack/$Utility/$Tool/$Armor.getComponentType()` + `getInventory()`. | reflect |

**Wynncraft reference (research pass 2, own words):** page 1 is free and more pages are bought. A distinct arrow appears only on the
last owned page, and double-clicking it buys the next page from inside the bank. Navigation is strictly one page at a time (players
asked for a page picker for years; it was never shipped). The arrow item can never be picked up: the server keeps putting it back.
The bank is shared by all characters. Our design matches all of that, except that "double-click" becomes "click, then click again
within 10 s" (section 4.6).

**Nothing to copy locally:** no installed mod (251 scanned) puts a real clickable item in a real vanilla container slot. They all
build a custom page with buttons. The mechanism above comes straight from engine primitives.

---

## 3. Layout

`S` = the vault's storage size = `VData.cap` (normally `slotsPerPage`, 36; an old file can be bigger). Storage indices `0..S-1` are
exactly today's slots. **Nothing about storage, the file format or `VData` changes.** Control items are never written to a vault
file, so rolling back to 0.1.1 is safe.

### 3.1 Default: `arrowLayout=row` (an extra control row, every storage slot stays usable)

- `R = ((S + 8) / 9) * 9` (the next multiple of 9). Container capacity = `R + 9`.
- Indices `S..R-1` (only when S is not a multiple of 9) are **padding**, and `R..R+8` is the **control row**. All of them are
  non-storage slots.
- Control row: `R` = Prev / First-page, `R+4` = Page info, `R+8` = Next / Buy / Last-page. `R+1..R+3`, `R+5..R+7` and every padding
  slot hold a Filler.
- Default S=36: capacity 45. Prev = index 36, info = 40, next = 44 (0-based): the left, middle and right slots of row 5.
- `slotsPerPage` stays 9-90. A 10-row chest (90 slots) is already allowed today; the arrow row makes it 11 rows. See U1.

### 3.2 Fallback: `arrowLayout=inside` (Wynncraft-exact: the arrows use 2 page slots)

For when a 5-row chest does not show or fit on Skyy's screen (U1), or if Skyy prefers the Wynncraft look.

- Container capacity = `S` (unchanged). `L = ((S - 1) / 9) * 9`, and if `S - L < 2` then `L = S - 2`. Prev = `L` (first slot of the
  last row), Next = `S - 1` (last slot). Default S=36: indices 27 and 35, i.e. the bottom-left and bottom-right slots of row 4.
  Usable storage = S-2 = 34.
- No info item and no fillers: the page info goes into both arrows' tooltips ("Page 3 >" / "You are on page 2 of 4 - 12 of 34 slots
  used").
- **Items already stored in those two slots are never lost.** Before a page is shown (open and every swap), a new synchronized
  `VData.clearReserved(page, a, b)` runs:
  1. It moves the item to the **first free non-reserved slot of the same page**.
  2. If that page is full, it moves it to the first free non-reserved slot of **any other owned page**.
  3. Each move bumps `rev`, schedules `saveSoon`, writes `vault.log RESERVED-MOVE <page>:<slot> -> <page>:<slot> <id> x<qty>` and
     sends one chat line ("Moved 12 Iron Bar from slot 36 to page 3 slot 5 to make room for the page arrow.").
  4. If the whole vault is full, **the item stays where it is and wins**. That page shows the item instead of the arrow, the slot
     works as normal storage (the filter lets it through, section 4.2), and chat says "Your vault is full - free a slot on this page
     to get the arrow back. /vault next still works."
  5. It counts before and after: `total()` must be equal, or the move is undone and logged.
- Switching back to `row` needs no migration: the two slots simply become storage again.

### 3.3 When arrows are off (`pageArrows=false`)

The container is exactly 0.1.1 (capacity S, no filters, no items, 0.1.1 chat text).

The layout is captured per session at `newSession` (`s.layout` 0/1/2, `s.base` = first non-storage index, plus the
prev/info/next indices). A config change never reshapes an open window; it applies from the next window (`new` flag).

---

## 4. Click -> page flip, with zero leaks

### 4.1 The button items in the view

For each page shown, `VBtn.row(s, d)` builds the **canonical control stacks** (`s.ctrl[]`, one per non-storage index):
`new ItemStack(id, 1)` + `ItemDisplay` (per-stack name/description, E10) + marker `"SkyyVaultBtn"` =
`{k: <kind>, o: <owner uuid>, s: <session serial>}` (a `BsonDocument`; the serial comes from an `AtomicLong` in `VSessions`). They are
placed with `setItemStackForSlot(i, st, false)` (E3), then read back (item id + marker kind must match: count before and after).

| Kind | Item id | When | Tooltip name (ItemDisplay) | Description |
|---|---|---|---|---|
| PREV | `Skyy_Vault_Prev` | page > 1 | `< Page 1` | Click to turn to page 1 of 4. |
| PREV_OFF | `Skyy_Vault_PrevOff` | page 1 | `First page` | You are on page 1 of 4. |
| NEXT | `Skyy_Vault_Next` | page < owned | `Page 3 >` | Click to turn to page 3 of 4. |
| BUY | `Skyy_Vault_Buy` | page = owned < maxPages | `Buy page 5` (gold) | 75,000 coins from your active profile. Click, then click again within 10 s. (Price 0: "Unlock page 5 - free".) |
| NEXT_OFF | `Skyy_Vault_NextOff` | page = owned = maxPages | `Last page` | You own every vault page (10 of 10). |
| INFO | `Skyy_Vault_Info` | row layout, `R+4` | `Page 2 of 4` (gold) | 14 of 36 slots used / Shared by all your profiles / /vault <page> jumps to a page |
| FILLER | `Skyy_Vault_Filler` | the other control and padding slots | `Vault` | (no description) |

Multi-line descriptions are built the way `SkyyRolls.descMsg` builds its lines. Every stack is rebuilt on every page swap and after
every buy, so the text is always current.

### 4.2 The filter (new class `VBtnFilter implements SlotFilter`, one instance per session)

`newSession` registers it for **ADD, REMOVE and DROP on every non-storage index**. `test()` touches **no container** (E8), only the
session's small synchronized fields:

```java
public boolean test(FilterActionType a, ItemContainer c, short slot, ItemStack st) {
  if (s == null || s.closed) return false;
  if (!s.ctrlLive(slot)) return true;            // inside layout: this reserved slot holds a real item on this page (3.2 step 4)
  if (a == FilterActionType.REMOVE && s.noteHit(slot)) VSessions.queueBtn(s);   // first hit of a batch schedules ONE task
  return false;                                  // ADD, REMOVE and DROP are always refused
}
```

- `VSession.noteHit(int slot)` (synchronized) sets the bit `slot - s.base` in `hitMask` (at most 17 bits) and returns true only when no
  batch is queued yet (it then sets `batchQueued`). `VSessions.onChange` also calls `s.noteChanged()` (synchronized) while a batch is
  queued, so the batch knows storage moved in the same breath. *(Review fix R4, 13: a storage change in the 100 ms BEFORE the first
  hit also marks the batch, because a bulk move walks the slots in index order inside one server call.)*
- `queueBtn(s)`: `Universe.get().getWorld(s.pr.getWorldUuid()).execute(new VBtnTask(s))`, the `dispatchClose` pattern. If there is no
  world, clear `batchQueued`. The task runs after the packet's own task has finished (E8: even inline it would be safe).

### 4.3 The batch task (new class `VBtnTask implements Runnable`, world thread)

1. `packed = s.takeHits()` (synchronized: mask, changed flag, clears `batchQueued`). If `s.closed` or `s.swapping`, stop here: the
   next fill places a fresh canonical row.
2. **Restore (count before and after):**
   - For every live non-storage index, compare the view slot with `s.ctrl[i - base]` (id + marker kind). A button stack that is
     wrong or missing is put back with `setItemStackForSlot(i, want, false)`. A REAL item in a control slot (impossible while ADD is
     refused, but handled) goes to the rescue path (6.4) before the slot is reset.
   - For every storage index, a vault button item found there is removed (`removeItemStackFromSlot(i)`: storage slots carry no
     filter) and logged `STRAY view`.
   - Recount: the number of button items in the view must equal the number of live control slots, and every live control slot must
     match. If not, `closeAny` (storage is already in `VData` from the change events) and warn.
3. **Re-send the truth (E7):** `s.window.invalidate()` plus `markDirty()` on the viewer's Storage, Hotbar and Backpack components.
   Next tick the client gets the chest and the whole inventory again, so any arrow it drew under the mouse or in a slot snaps back.
4. **Sweep the viewer** (6.2), cheap, and it covers "it went somewhere after all".
5. **Decide:**
   - **Exactly one distinct control slot hit** and **no storage change in the batch** and the session still `current(u)`,
     `registered` and `visible` => a click on that slot's kind (4.5).
   - Anything else (2+ distinct slots = Take All, Sort or merge-stack, E5; or a storage move in the same batch) => no page action.
   - **Invariant that makes this safe:** the control area always holds at least 2 button items (row: 9; inside: 2, unless blocked), so
     a bulk button can never look like a single click. *(Review R4: that was not enough - see 13.)* For the blocked inside case
     (only 1 live control), a Take All that moves
     nothing is the only lookalike, and it just turns the page, harmlessly.
   - **Hit counts are never used**: one shift-click can test the same slot twice (E4). Two hits on one slot are still one click, and a
     buy needs two separate batches (4.6).

### 4.4 Flip = save the current page, load the next in place

For PREV/NEXT the task runs the same steps as `pageSwap`:
1. `gate(u)` (profile busy / after-switch wait; refusal => chat line, nothing moves).
2. `swap(s, target)`.
3. On failure: `closeAny` + the existing "closed to keep your items safe" line.
4. On success: page mode => `refreshPage(p, s)`; chat `=Vault page 3 of 4.`

`swap` itself (0.1.1 R3/R5) already does "`syncView` old page -> `fill` new page -> read back -> `noSync` close on any mismatch". In
0.1.2:
- `syncView` builds `now` from storage indices only, and treats a button item in storage as empty and flags it for step 2.
  `VData.copyIn` already copies only `a.length = S` elements.
- The inside layout runs `clearReserved` before `fill`.
- `fill` clears, places storage (`i < S`), then places the new canonical control row, then reads back BOTH: storage against `src`,
  control against `s.ctrl`.
- `newSession` does the same for the first page and registers the filters. `s.swapping` still shields `onChange` during the fill.

### 4.5 What each kind does on a click

- PREV / NEXT: flip (4.4).
- PREV_OFF / NEXT_OFF: chat `=This is your first page.` / `=This is your last page (10 of 10).`
- INFO: chat `=Vault page 2 of 4 - 14 of 36 slots used. /vault <page> jumps to a page.`
- FILLER: nothing (the restore and the re-send still happen).
- Any nav click disarms a pending buy (`VStore.disarm`, as the page's buttons do).

### 4.6 Buying from inside (BUY kind)

Reuse, do not duplicate: `VStore.buyKey(u, next)`, `VStore.confirm(key)` (the 10 s arm shared with the page's Buy button and
`/vault buy`), `VStore.buy(u, name)` (coins first, write + read back, relock + refund on failure) and the same result strings.

- **First click:** `confirm` arms. Chat: `=Buy vault page 5 for 75,000 coins? Click the gold arrow again within 10 s (or type /vault
  buy).` The item text stays static: no timers.
- **Second click in a LATER batch within 10 s:** `confirm` returns true, then `gate(u)`, then `VStore.buy`.
  - Success: `swap(s, next)`, chat `+Bought vault page 5 for 75,000 coins.`, and the row is rebuilt (Buy becomes Next, or NextOff at
    max).
  - Failure (no SkyyCoins, too few coins, write failed and refunded): the existing message, nothing else changes.
- A click after 10 s arms again. A double-click that lands in one batch only arms (the player clicks once more). That is on purpose:
  coins must never go on one gesture (E4).

### 4.7 Why nothing can leak (the checklist)

1. The engine refuses the move before anything moves (E1, E2). There is no server cursor to strand an item in (E6).
2. Our filter refuses ADD on every control slot, so no real item can be buried under a control and lost from the save.
3. Control items never enter `VData`, so they are never saved (4.4). A button in a vault file is dropped at load (6.3).
4. After every click, the chest and the inventory are re-sent (E7) and the viewer is swept (6.2).
5. A button item anywhere else is removed by the sweep on join, on vault close and every 30 s (6.1).
6. A closed or retired view is DENY_ALL (the 0.1.1 rule), so its filter is never even asked (E1).

---

## 5. Every gesture, and what happens

| Gesture | What the server sees [E] | Result |
|---|---|---|
| Click the arrow, then click/put it down anywhere | `MoveItemStack` from the arrow slot on put-down | REMOVE refused, 1 hit => page turns, arrow snaps back |
| Drag the arrow out (to your inventory, hotbar, armor, another vault slot) | same | same |
| Shift-click the arrow ("Transfer") | `SmartMoveItemStack` | REMOVE refused (maybe 2 hits on the same slot = still 1 click) => page turns |
| Drop key on the arrow | `DropItemStack` -> `removeItemStackFromSlot` | REMOVE refused => page turns, nothing is thrown |
| Take Half / Take One on the arrow | a `MoveItemStack` with a smaller quantity when placed | same as a drag |
| Number key over the arrow (if the client has it) | `MoveItemStack` window slot -> hotbar | same as a drag |
| Double-click / merge stack on some other item | `combineItemStacksIntoSlot` over every open window: REMOVE on all our slots | 2+ hits => no flip. Buttons are MaxStack 1, never "stackable with" anything, so they are never pulled |
| Take All button | REMOVE on every non-empty slot | storage empties as usual, controls stay, 2+ hits => no flip |
| Sort button | REMOVE on every slot, refused slots skipped | storage sorts inside 0..S-1, controls stay, 9+ hits => no flip |
| Put All / Quick Stack / shift-click from your inventory into the vault | ADD tests only | control and padding slots refuse, items land in storage or stay with you |
| Drag an item onto an arrow / filler | ADD on that slot | refused, the item stays where it was, no flip |
| Right-drag "Place One" across slots | one `MoveItemStack` per target | control targets refuse |
| Esc or close with the arrow still "held" by the client | nothing (it never left the server slot) | the next window update shows it in place |
| Disconnect mid-drag | nothing | nothing to repair |
| Spam-click Next | one batch per packet group | one flip per batch, never more than one per click, every flip gated |
| Creative item library | a creative player could spawn any item (`SetCreativeItem`) | hidden by the quality's `HideFromSearch` (E11, U5). A spawned one is useless (no interaction, not placeable, not craftable) and the sweep removes it |

---

## 6. Safety sweep

### 6.1 When

The sweep runs in four places. None of them adds an event listener or ECS system: 0.1.2 still registers none, and the existing 1 s
ticker does the timing.
- **Join:** `VTick` keeps a set of online UUIDs. A player seen for the first time (or again after being offline), once
  `pr.getWorldUuid()` is known, gets one sweep.
- **Vault close:** `finalizeWorld` (world-thread close) sweeps the viewer after the final sync. The offline and shutdown paths skip it.
- **Periodic:** every `straySweepSeconds` (default 30), one sweep per online player on that player's world.
- **After every button batch** (4.3 step 4).

### 6.2 What (new class `VSweepTask implements Runnable`, world thread)

- Skip while `profile:busy:<uuid>` is set (PROFILES-CONTRACT rule 5: crash recovery is about to replace the inventory). The next
  period retries.
- `ref = pr.getReference()`. For Hotbar, Storage, Backpack, Utility, Tool and Armor: every slot whose stack passes `VBtn.isButton`
  (`getItemId().startsWith("Skyy_Vault_")`) is removed with `removeItemStackFromSlot((short) i)`.
- The player's other open windows (`WindowManager.getWindows()`, any `ItemContainerWindow` that is not a live vault session's window)
  are swept too. For the player's own live vault window, only storage indices are checked.
- Count before and after: a rescan must find 0. If not, warn once per player. Each removal writes
  `vault.log STRAY <name> <uuid> <section>:<slot> <itemId> sid=<marker s>` plus one server WARN line per sweep that found anything.
- Cost: about 80 slot reads and a prefix compare per player per 30 s.

### 6.3 The file and the save path

- `VStore.fromDoc`: a stack with a `Skyy_Vault_` id is dropped with `vault.log STRAY-FILE` (it is a UI item with no value, so this
  loses nothing).
- `syncView`: a button in a storage index is saved as empty and flagged, and `queueBtn` removes it (4.3).

### 6.4 Rescue (defensive: a real item found in a live control slot)

Such an item is never cleared. In order, it goes to:
1. the first free storage slot of the current page (then `syncView`);
2. the player's Storage/Hotbar (`addItemStack`, remainder checked);
3. the first free slot of any owned page in `VData`;
4. last resort: thrown at the player's feet with the vanilla drop call (`ItemUtils.throwItem`, as the drop handler does).

Each step is logged (`RESCUE`), with a count before and after. *(Review fixes R2/R3, 13: a storage write that does not read back
is undone; a stack the rescue cannot move is never overwritten by the arrow, and the close moves it into the vault.)*

**Known limits:** item entities on the ground, real chest blocks and other mods' stores are not scanned. A stray can only reach them
from an inventory, which the sweep keeps clean, and the filters make strays impossible in the first place. A later cross-mod rule
could have SkyySacks/SkyyAuctions/trade refuse `Skyy_Vault_*` ids (not in 0.1.2).

---

## 7. Both open modes

- **Chest mode (`Page.Bench`):** the whole point. New opening line:
  `=Vault page 1 of 2 (shared by all your profiles): the arrows in the bottom row turn pages, Esc saves. /vault <page> jumps.`
  With arrows off, the 0.1.1 line.
- **Page mode (`openCustomPageWithWindows`):** the same view, so the same control row shows in the window. The page's own
  `< Prev` / `Next >` / number / Buy buttons keep working. An arrow click also calls `refreshPage` so the page's label follows. One
  code path, no mode branch in the filter. (Whether the client draws the window next to a custom page at all is still 0.1.1's
  UNVERIFIED (1).)
- **`/vault pages` in chest mode** (session-less `VaultPage`) and **`/vaultadmin open`** (a read-only DENY_ALL COPY of storage) are
  unchanged and show no arrows. *(Review fix R1, 13: the admin copy's container is now a `VView`, still DENY_ALL and without arrows,
  so an admin's shift-click / Take All no longer throws.)*
- `/vault next|prev|<page>` and the page buttons keep working exactly as before, and all go through `swap`, which now also rebuilds
  the control row.
- Page-mode label and `/vault info`: "of Y slots" uses the usable count (S, or S-2 in the inside layout).

---

## 8. Config (kit `tools/skyycfg.py`, contract `tools/CONFIG-CONTRACT.md`)

Three new rows are appended to `ROWS` (11 rows in total), in the 0.1.1 tuple format, with `F_ = "@config.properties:"`:

```python
("pageArrows", "Page arrows in the vault window", "vault", "bool", "true", "", "", "", "", "new",
 "Arrow items in the vault window turn pages. Applies to vault windows opened afterwards.",
 "field:VCfg.ARROWS" + F_ + "pageArrows"),
("arrowLayout", "Where the page arrows go", "vault", "choice", "row", "", "", "row|Extra row,inside|Inside the page", "", "new,danger",
 "Extra row: a control row under the slots. Inside: arrows use 2 page slots (items there move).",
 "field:VCfg.ARROW_LAYOUT" + F_ + "arrowLayout"),
("straySweepSeconds", "Stray arrow check every", "vault", "int", "30", "5", "600", "step=5", "s", "live,adv",
 "Online players are checked this often for stray vault arrow items, which are removed.",
 "field:VCfg.SWEEP_MS*1000" + F_ + "straySweepSeconds"),
```

- New `VCfg` fields (before `emit()`): `public static volatile boolean ARROWS = true;`,
  `public static volatile String ARROW_LAYOUT = "row";`, `public static volatile long SWEEP_MS = 30000L;`. The unit rule holds:
  `*_MS` + unit `s` + `*1000`.
- `VCfg.load` reads and clamps them the 0.1 way: bool words; layout `row`/`inside`, anything else => `row`; sweep 5-600 s. They are
  added to `CFG_LINES` (so `CONFIG_TEXT` / `DEFAULTS` carry them), each with a comment line:
  `pageArrows=true`, `arrowLayout=row`, `straySweepSeconds=30`. `pageArrows` is written as `true`/`false`, so no `01` opt.
- `arrowLayout` is `danger`: the kit asks before any change, because `inside` moves items. It is `new`: open windows keep their
  layout.
- 0.1.2 picks up whatever `KIT_VERSION` `tools/skyycfg.py` has at build time (1.1 per the contract; 0.1.1 was built with 1.0). No
  adopter code change is needed for 1.1.
- Player Settings (`settings:*`): none. Every chat line is a reply to the player's own click.

---

## 9. The asset pack (first Skyy mod with its own PNGs)

`B.manifest` already sets `IncludesAssetPack: true`. 0.1.2 passes a `files` dict to `B.assemble(jar, man, OUT, files)` (0.1.1 passes
none). `zipfile.writestr` accepts bytes, so PNGs go in the same dict.

- **7 item JSONs** at `Server/Item/Items/Utility/Skyy_Vault_<X>.json` (X = Prev, PrevOff, Next, NextOff, Buy, Info, Filler):
  ```json
  { "TranslationProperties": {"Name": "server.items.Skyy_Vault_Next.name", "Description": "server.items.Skyy_Vault_Next.description"},
    "Icon": "Icons/ItemsGenerated/Skyy_Vault_Next.png",
    "Model": "Items/Consumables/Scrolls/Map.blockymodel",
    "Texture": "Items/Consumables/Scrolls/Map_Wood.png",
    "PlayerAnimationsId": "Item",
    "Quality": "SkyyVaultButton",
    "MaxStack": 1 }
  ```
  - **Never usable anywhere else:** no `Categories` (not listed by category), no `Recipe` (not craftable), no `Interactions` (no
    right-click), no `BlockType` (not placeable), no `ResourceTypes` / `Consumable` / `Tool` / `Weapon` / `Armor` / `Utility`,
    `MaxStack 1` (never stackable, never merged).
  - The model and texture are the vanilla map scroll (both paths exist in Assets.zip), so a copy that somehow leaked still renders.
  - Build check: every Model/Texture path exists in Assets.zip, MaxStack is 1, and none of the forbidden keys is present.
- **1 quality** `Server/Item/Qualities/SkyyVaultButton.json`: a copy of vanilla `Technical.json`'s textures (`SlotTool.png` slot frame,
  so the control row looks different from storage), with `"HideFromSearch": true`, `"VisibleQualityLabel": false`,
  `"TextColor": "#d9b25c"`, `"LocalizationKey": "server.general.qualities.SkyyVaultButton"`, `QualityValue 8`, and no
  `ItemEntityConfig` (no drop sparkle).
- **7 icons** at `Common/Icons/ItemsGenerated/Skyy_Vault_<X>.png`, 64x64 RGBA, drawn by the build script with a ~20-line pure-Python
  PNG writer (`zlib` + `struct` + `zlib.crc32`; PIL is not installed here):
  - Prev/Next: light-blue chevron arrows (left/right);
  - PrevOff/NextOff: the same arrows in grey at about 40% alpha;
  - Buy: a gold right arrow with a small "+";
  - Info: a cream page with 3 lines;
  - Filler: a dark slate square at about 60% alpha.
  They are our own art, so there is no license question. Skyy can replace them later.
- **`Server/Languages/en-US/server.lang`**: `items.<Id>.name` / `server.items.<Id>.name` / `.description` for each of the 7 ids (the
  SkyySacks pattern), plus `server.general.qualities.SkyyVaultButton=Vault`. Names: Previous page, First page, Next page, Last page,
  Buy next page, Vault page, Vault. Per-stack ItemDisplay text overrides the name and description in the view.

---

## 10. Build notes for 0.1.2 (for the build pass)

**Touch list** (function names from 0.1.1, see Appendix R for line numbers):

| Area | Change |
|---|---|
| `VCfg` | 3 fields + load/clamp + `CFG_LINES` |
| `VData` | `clearReserved(page, a, b)` (synchronized, count before and after) |
| `VStore.fromDoc` | drop `Skyy_Vault_*` stacks + log |
| `VSession` | fields `layout, base, prevIdx, infoIdx, nextIdx, ctrl[], live[], hitMask, batchQueued, batchChanged, sid`; synchronized `noteHit`, `noteChanged`, `takeHits`; `ctrlLive(slot)` |
| `VSessions` | `newSession` (capacity by layout, filters, row), `fill` (control row + read back), `syncView` (storage only, stray flag), `swap` (`clearReserved`), `onChange` (`noteChanged`), `finalizeWorld` (sweep), `open` (chat text), new `queueBtn`, `restoreCtrl`, `resync`, `sweepPlayer`, `btnClick` |
| `VTick` | join set + periodic sweep dispatch |
| New classes | `VBtn` (ids, `isButton`, `same`, canonical stacks, texts), `VBtnFilter`, `VBtnTask`, `VSweepTask` (top-level classes, no inner classes) |
| `ROWS` | 3 rows |
| Assets | section 9 |
| Header | 0.1.2 notes + the UNVERIFIED list |

**javassist:**
- No lambdas, generics, varargs, autoboxing (`Integer.valueOf` / `Long.valueOf` by hand), enhanced-for, inner classes, String switch
  (the kind is an `int`) or try-with-resources.
- Methods before callers, also inside `VSessions` (`VBtn` compiled before `VSessions`; `VBtnFilter` / `VBtnTask` / `VSweepTask` after
  the `VSessions` methods they call).
- A synchronized block holds one call; use synchronized METHODS for the hit fields.
- f-string braces doubled.
- Nested engine classes are referenced with `$` (`InventoryComponent$Storage`, as SkyyIslands does).
- `SlotFilter` is an interface: `addInterface` on `VBtnFilter`.

**Engine rules:** no `registerSystem` (none added); containers only on the world thread (`VBtnTask` / `VSweepTask` run there;
`test()` touches no container); count before and after every move (restore, sweep, rescue, `clearReserved`).

**Bare-JVM checks** (scratch harness under `tools/dev/scratch/vault/`, deleted after; `TEMP`/`TMP` pointed there):
- (a) all classes load under `-Xverify:all`;
- (b) `SimpleItemContainer(45)` + filters on 36-44: `moveItemStackFromSlotToSlot(44, 1, other, 0)` fails, slot 44 and `other`
  unchanged, the hit mask shows only 44;
- (c) `other -> view slot 44` fails with no hit;
- (d) `removeItemStackFromSlot(44, 1)` (drop path) fails with a hit;
- (e) `sortItems` sorts 0-35, controls stay, 9 distinct hits;
- (f) a Take All loop (`moveItemStackFromSlot` for every non-empty slot) empties storage, controls stay, 3+ distinct hits;
- (g) `setItemStackForSlot(40, x)` (filter on) is refused;
- (h) `syncView` copies only 0-35, and a button placed at slot 3 (filter off) is saved as empty and flagged;
- (i) `fill` + control read-back; `swap` keeps both pages byte-equal;
- (j) inside layout: items at 27/35 move to the first free slot with `total()` equal; with a full vault they stay, `ctrlLive` is
  false and the filter allows;
- (k) the kit publishes 11 rows; get/set/file lines of the 3 new rows; `straySweepSeconds 20` gives `SWEEP_MS 20000`; `arrowLayout`
  asks confirm;
- (l) the jar holds 7 JSONs + the quality + 7 valid 64x64 PNGs + lang lines, and every JSON passes the section 9 checks;
- (m) `fromDoc` drops a `Skyy_Vault_Next` stack.

**Build:** plain `python build_skyyvault_0.1.2.py` must end with `assembled ...SkyyVault-0.1.2.jar`; `python tools/ci/lint.py` must
give 0 fails. Never pass `--deploy`, `tools/deploy_set.py --check` only, and do not commit.

---

## 11. Test plan (Skyy, in game)

**A. Look.**
1. Set chest mode (`/modconfig` Vault -> Open /vault as: Chest window), then `/vault`.
2. Expect 5 rows: 4 storage rows plus the bottom row [grey First page][3 fillers][page item][3 fillers][Next or gold Buy].
3. Check that everything fits your screen and your inventory is still visible below. Hover each item: the names and texts read
   right.

**B. Flip both ways.**
1. Click Next. Page 2 shows, the page item reads "Page 2 of N", chat says "Vault page 2 of N". Click Prev to go back.
2. Try every gesture on an arrow: plain click (does it turn at once, or only when you click again or let go?), drag it onto your
   inventory, shift-click, drop key, take half.
3. After each: the arrow is back in its slot, and after about 1 s your inventory shows no arrow. Close and reopen the inventory to be
   sure.

**C. Try to steal an arrow.**
1. Drag an arrow onto your hotbar, your armor and a vault slot.
2. Press Take All, Sort, Put All and Quick Stack.
3. Drag an item onto an arrow and onto a filler.
4. Shift-click items into a full page: nothing may land in the bottom row.
5. Spam-click Next 10 times fast.
6. Press Esc while the client shows the arrow on your cursor. Disconnect mid-drag and rejoin.
7. After all of that, search your whole inventory for "page" / "Vault" items. The server log and
   `mods/Skyy_SkyyVault/vault.log` should show no STRAY lines (a STRAY line means the safety net caught something: report it).

**D. Buy a page from inside.**
1. With coins, go to your last page. Click the gold arrow: chat asks you to confirm.
2. Click again within 10 s: the coins are taken ONCE and the new page opens.
3. Click, wait 11 s, click: it asks again and buys nothing.
4. Without enough coins: a refusal, nothing taken.
5. At max pages: a grey "Last page" arrow.

**E. Page mode.** Set Open /vault as: Page view, then `/vault`. The same bottom row appears in the window (if the window shows at all
next to the page), and the page's label follows arrow clicks.

**F. Profile switch.**
1. Switch profiles with the vault open: it closes as before.
2. Within 30 s after a switch, arrows are refused with the wait message.

**G. Config.**
1. Page arrows off, then reopen: 4 rows, no arrows.
2. Where the page arrows go: Inside the page (it asks to confirm), then reopen: the arrows sit in the bottom-left and bottom-right
   slots of row 4. An item that was in one of those slots moved to a free slot, and chat says where.
3. Fill every slot of the vault, then reopen with Inside: the item stays and that page shows it instead of the arrow.
4. Switch back to Extra row.

**H. Creative library.** Search "page" / "vault": the arrow items should not be listed (U5).

**I. Two players (if Wesley is on).** Both flip their own vaults at the same time: no cross-effects.

---

## 12. Open questions (with the default that ships if Skyy does not answer)

| # | Question for Skyy | Default in 0.1.2 |
|---|---|---|
| Q1 | Extra 5th row (all 36 slots stay usable) or Wynncraft-exact (arrows use 2 of the 36)? | Extra row (`arrowLayout=row`); Inside is one switch away |
| Q2 | Arrows also in page mode (where the page already has Prev/Next buttons)? | Yes (one code path) |
| Q3 | Buy from inside the chest with click + click again within 10 s (Wynncraft: double-click)? | Yes; the same confirm as the page button and `/vault buy` |
| Q4 | A chat line on every page turn ("Vault page 3 of 4.")? | Yes (the chest title cannot show the page) |
| Q5 | Dark filler items in the unused bottom-row slots? | Yes (the row reads as "not storage", and fillers keep bulk buttons from looking like a click) |
| Q6 | Icons: our generated simple arrows, or does Skyy want to draw/pick art? | Generated now, replaceable later |
| Q7 | Clicking the page item: nothing but a hint, or a jump-to-page picker (Wynncraft never had one)? | Hint only |
| Q8 | Arrows in the admin read-only view too? | No (`/vaultadmin open <player> <page>`) |
| Q9 | Stray check interval | 30 s (admin row, 5-600 s) |
| Q10 | Rename the chest title "Chest" to "Vault"? It might work through the window data key `blockItemId` (what real chest blocks use), but that is untested. | Not in 0.1.2 |

**UNVERIFIED (needs the real game):**

| # | Question | What we know so far |
|---|---|---|
| U1 | Does a 45-slot chest draw 5 rows and still fit the screen with the player inventory? | Client `ContainerPanel.ui` evidence (E9). If not: `arrowLayout=inside`. |
| U2 | Which gesture reaches the server first (plain click vs put-down / drag / shift-click / drop)? | Section 1. The chat hint wording follows the answer. |
| U3 | Does a refused pick-up snap back cleanly on the client? | `invalidate` + `markDirty` re-send next tick (E7). If a flicker remains, also call `WindowManager.updateWindow(window)` at once. |
| U4 | Does the ItemDisplay tooltip show on items in a container slot? | SimpleEnchantments / SkyyRolls method; SkyyRolls' tooltip is not yet in the verified list. |
| U5 | Does `HideFromSearch` in our own quality keep the items out of the creative library? | E11 |
| U6 | Do our own icon PNGs load from the jar? | E12; first Skyy mod to ship them |
| U7 | Take All / Sort on the arrow row. | The engine skips refused slots and 2+ hits never flip (E5); confirm by eye. |

## 13. Build pass notes (SkyyVault 0.1.2 built 2026-09-25; where the build differs from sections 1-12)

- **E4/E5 were incomplete: a refused whole-slot move throws.** `ItemContainer.internal_moveItemStackFromSlot(slot, [qty,] to,
  allOrNothing, filter)` (shift-click via `smartMoveItem`, Take All via `takeAllWithPriority -> moveItemFromCheckToInventory`) returns
  `null` when `cantRemoveFromSlot(slot)` is true, and the public wrapper then calls `sendUpdate(null)`: a NullPointerException, logged
  by the world as "Failed to run task!" (SEVERE). Take All stopped at the first arrow, so with empty storage it looked like a single
  click on Prev. Confirmed in a bare JVM. Fix in 0.1.2: windows with arrows use `VView extends SimpleItemContainer`, which answers a
  refused whole-slot move with the engine's own failed `MoveTransaction` (the one it builds for `cantMoveToSlot`). The filter still
  sees every attempt, and Take All now touches all 9 row slots. Drag / put-down and the drop key already returned a failed
  transaction. *(First build pass: the 0.1.1 DENY_ALL views, the `/vaultadmin open` copy and a retired view, still threw on
  shift-click / Take All. Fixed by review R1 below.)*
- **Drop key on an arrow:** nothing is thrown (the refused removal has no output), but the engine logs its own WARNING "<name>
  attempted to drop an empty ItemStack!".
- **Re-send:** the engine re-sends only the inventory sections whose component is dirty (`PlayerSendInventorySystem`), so all six
  sections are marked dirty, not three.
- **World check:** `VBtnTask` and `VSweepTask` carry the world they were queued on. A player who changed worlds meanwhile is never
  touched from the old world's thread (a sweep re-dispatches up to 3 times, the `VCloseTask` pattern).
- **Inside layout, freed arrow slot:** when a player empties an arrow slot that a stored stack had blocked, a batch puts the arrow back
  at once (`relive`), so "free a slot on this page to get the arrow back" is literal.
- **Filler item** has no lang description (its JSON names only `Name`), so no raw key can show. Its per-stack tooltip is the name only.
- **Stale row:** the slot's action follows the vault's current state (Prev slot, Next slot, info, filler), and non-flip clicks redraw
  the row. `/vault buy` redraws an open row too.

### 13.1 Review fixes (same 0.1.2, rebuilt 2026-09-25)

- **R1 No vault container throws any more.** `/vaultadmin open` builds its read-only copy as a `VView` (no slot filters, still
  DENY_ALL, no arrows): under DENY_ALL `cantRemoveFromSlot` is true for every slot, so the plain `SimpleItemContainer` of 0.1.1 hit the
  engine's null result on an admin's shift-click / Take All ("Failed to run task!"). Every session view is a `VView` too, also with
  `pageArrows=false`, so a retired DENY_ALL view still on screen is covered. `VView` changes nothing for an allowed move.
- **R2 Rescue into storage never places a stack twice.** A write into an empty storage slot that does not read back is undone before
  the next slot is tried. If the undo fails, the rescue stops there (`vault.log RESCUE-PARTIAL`, a WARN) and hands nothing on.
- **R3 A stack the rescue cannot move is never overwritten.** `rescue` returns whether the control slot is empty. If it is not,
  `restoreCtrl` leaves the stack, the recount fails and the batch closes the view. `finalizeWorld` then runs `keepCtrl` before the view
  is emptied: a real stack in a live control slot goes to the first free slot of any owned page (`RESCUE ... at close`), else it is
  thrown at the player's feet, else `RESCUE-LOST`. It does nothing in normal use. Engine note (bytecode): with `filter=false`,
  `removeItemStackFromSlot` and `setItemStackForSlot` always succeed, so R2 and R3 are defence in depth.
- **R4 A bulk move before the arrow no longer looks like a click.** `noteChanged` used to count a storage change only after a batch
  was queued. The engine's bulk actions walk slots in index order inside one server call, and change events are dispatched
  synchronously per successful transaction (failed ones fire none). So with `arrowLayout=inside` and one live arrow (the other
  blocked, vault full), a Take All that filled the player's inventory before it reached the arrow, or a merge-stack that pulled
  stacks from lower slots, produced storage moves first and then exactly one hit, and the page turned. Now the session keeps the time of
  the last storage change, and a batch whose first hit comes within 100 ms of it counts as changed. A person cannot move an item and
  then click an arrow within 100 ms. If two packets do arrive that close together, the click is only ignored (the arrow snaps back).
  The row layout was never exposed (a bulk action always touches all 9 row slots).

---

# Appendix R: research map of SkyyVault 0.1.1 (kept for its line numbers)

*Written earlier on 2026-09-25 by two read-only research passes (sections R1-R15, then the R16 addendum). Every line number is
`SkyyVault/build_skyyvault_0.1.1.py` (2355 lines). Inside this appendix, "section N" means RN. Superseded by Part A: R8's "buying
from the chest is out of scope" (Part A 4.6 builds it), R12's item notes (Part A 9: custom quality with HideFromSearch, own icons),
R13's open reentrancy risk (answered in R16.3; Part A 4.2 keeps test() free of container calls anyway), R14's touch list (Part A 10)
and R15's open questions (Part A 12).*


## R1. How chest mode and page mode open the container today

Both modes go through **one function, `VSessions.open(pr, ref, st, page, mode)`** (lines 1526–1572). `mode` is `1` = page, `2` = chest
(constants `VSessions.PAGE=1`, `CHEST=2`, line 1316). `VCfg.PAGE_MODE` (boolean, mirrors the `openMode` config choice) picks the default
mode for a bare `/vault` (`VSessions.openDefault`, line 1573).

- **Gate first** (line 1531): `VSessions.gate(u)` — refuses while `profile:busy:<uuid>` is set or within `afterSwitchSeconds` of a switch
  (section 8 below).
- **Load the vault** (line 1533): `VStore.load(u)` — the `VData` for this player (per-player, keyed by UUID, never by profile — vault is
  shared by every profile, contract rule 6).
- **Reuse or replace the session**: `VSessions.current(u)` (line 1541). If a live session already shows this exact mode and is visible,
  it just swaps pages in place (`swap`, line 1544); otherwise the old view is released (`release`, line 1550) before a new one is made
  (never two open at once — session locking, section 6).
- **Build the view**: `VSessions.newSession(pr, u, d, page, mode)` (line 1463) makes `s.view = new SimpleItemContainer((short) d.cap)` —
  **the same container class and the same size (`d.cap` = `VCfg.SLOTS`, default 36) for BOTH modes.** Mode only changes which vanilla
  UI wraps that container:
  - **mode 1 (page)**: `p.getPageManager().openCustomPageWithWindows(ref, st, vp, new Window[]{ s.window })` (line 1561) — OUR
    `VaultPage` (a `CustomUIPage`, Prev/Next/number buttons, section 11) is opened TOGETHER WITH the container window.
  - **mode 2 (chest)**: `p.getPageManager().setPageWithWindows(ref, st, Page.Bench, true, new Window[]{ s.window })` (line 1563) — the
    **vanilla chest page** (`Page.Bench`) is opened with only the container window, no custom page at all. This is exactly the screen
    in Skyy's screenshots and the one with no arrows today.
  - `s.window` is `new VWindow(s.view, s)` (line 1473) — `VWindow extends ContainerWindow` (line 299), overriding `onClose0` (closes the
    session, line 1819) and `validate` (line 1824, calls `VSessions.stillValid`).
  - Chest mode's chat line (`"...(shared by all your profiles): drag items in and out, Esc saves. /vault next or /vault <page>
    switches pages."`, line 1570) is exactly what Skyy's screenshot shows.
- `/vault pages` (`VSessions.openNav`, line 1584) is the only place that opens the button page in CHEST-mode servers without slots (a
  `VaultPage` with `sess = null`) — a *third*, session-less shape worth remembering when adding arrows: not every `VaultPage` has a
  live container to put arrow items into.

## R2. Slots per page

- `VCfg.SLOTS` (field, line 337; default `DEF_SLOTS = 36`, line 285) is the config-driven page size ("slotsPerPage", admin row at line
  466, flags `new,danger` — only applies to vaults loaded after a change, line 467).
- `VData.cap` (field, line 493) is the actual capacity of ONE loaded vault (set at construction, line 498; can be bigger than
  `VCfg.SLOTS` if a saved file already used a larger page — `VStore.fromDoc`, lines 762–764, raises `cap` to fit the largest saved
  slot index, `maxSlot + 1`). **`VData.cap` is what actually sizes the container** (`newSession`, line 1466: `new
  SimpleItemContainer((short) d.cap)`), not `VCfg.SLOTS` directly.
- `VData.pages` is an `ArrayList` of `ItemStack[]`, one array of length `cap` per unlocked page (`VData.page(n)`, line 504, grows the
  list lazily). **There is no spare slot today**: every index `0..cap-1` is a real storage slot, 1:1 with what the chest window shows.

## R3. Loading a page into / saving it from the container (lossless)

- **Load** = `VSessions.fill(s, src)` (line 1445): `s.view.clear()`, then `setItemStackForSlot((short) i, src[i], false)` for every
  non-null index, then **reads every slot back** and byte-compares id/qty/emptiness against `src` — returns `false` on any mismatch
  (caller then closes the session `noSync`, never losing or duplicating anything: `swap`, lines 1478–1500).
- **Save** = `VSessions.syncView(s)` (line 1386): reads every slot of `s.view` (`getItemStack`, `getCapacity`), builds an `ItemStack[]`
  `now`, and calls `VData.copyIn(page, now)` (line 536) which compares element-by-element into the stored page array and bumps `rev`
  only if something actually changed (then `VStore.saveSoon(owner, VCfg.SAVE_DELAY_MS)`, line 1397).
- **Lossless slot codec** = `VCodec` (lines 546–622): `slotDoc`/`stackOf` carry id, qty, durability, maxDurability, quality,
  overrideAnim, a raw `meta` BsonDocument, PLUS the engine's own `ItemStack.CODEC` encoding as a `"stack"` field (decoded first; the
  explicit fields are the fallback, line 580). A stack that cannot be rebuilt (item removed from the game) is kept byte-for-byte as an
  **orphan** (`VStore.place`, line 721) and retried at every load, on any page — never dropped.
- **File shape**: `VStore.toDoc`/`fromDoc` (lines 686–789) — `vaults/<uuid>.json`: format, mod, version, uuid, name, pages, capacity,
  savedAt, rev, count, `content:[{page, slots:[{slot,...}]}]`, `orphans:[...]`. Written with `VCfg.atomicWrite` (tmp + fsync +
  `ATOMIC_MOVE`, 5×20 ms retries, line 382) under a **per-vault IO lock** (`VData.ioLock`, `VStore.writeDoc`, line 868) that only ever
  writes a revision if it is newer than what is already on disk (`write0`, line 852: `if (r <= d.writtenRev) return true;`) — an older
  snapshot can never overwrite a newer file. Every write is read back and slot-counted (`VCodec.countSlots`) to catch silent
  corruption (line 858).

## R4. The change listener

- `VChange` (line 1114) implements `java.util.function.Consumer`; `accept(Object ev)` (line 1815) just calls `VSessions.onChange(sess)`
  — **the actual event object is never inspected** (no slot index, no old/new stack passed through today).
- `onChange` (line 1400) is a thin guard (`if (s == null || s.closed || s.swapping) return;`) around `syncView(s)` — i.e. **any**
  change anywhere in the container re-syncs the WHOLE page, not just the changed slot.
- Registered once per session, in `newSession` (line 1474): `s.reg = s.view.registerChangeEvent(new VChange(s));`. `s.reg` is an
  `EventRegistration`, unregistered on close (`finalizeWorld` line 1410, `retire` line 1427).
- **Engine fact confirmed by `reflect.py`**: `ItemContainer.registerChangeEvent` is overloaded as `(Consumer)`, `(EventPriority,
  Consumer)` and `(short, Consumer)` — **a per-slot change registration already exists on the engine side** (`(short slot, Consumer)`)
  that this mod has never used; it could tell the mod exactly which slot changed without diffing the whole container. Untested by us
  (not called anywhere in the codebase) — verify the `short` argument means "only this slot" before relying on it.

## R5. Session / viewer locking (one editable view per vault)

All in `VSessions` (lines 1310–1809), keyed by **owner UUID** in `SESSIONS` (a `ConcurrentHashMap`, line 1311) — never by viewer, so a
vault can only ever have ONE editable view, matching contract rule "never swap or touch the vanilla inventory for a profile switch" and
the mod's own "no dupes, no loss" design (0.1.1 header, lines 77–115).

- `current(u)` (line 1369): live session or `null`.
- `registered(p, s)` (line 1377): is `s.window` still the window the engine's `WindowManager` actually has open.
- `visible(p, s)` (line 1502): for mode 1, is `s.pageObj` the player's current custom page; for mode 2, is there NO custom page open
  (chest mode has none).
- `release(p, ref, st, s)` (line 1519) — the "make room for a new view" dispatcher: **retire** (line 1422, `DENY_ALL` first, then sync,
  then mark closed — used when the window is part of the page ON SCREEN and about to be replaced, so nothing is ever closed right
  before another opens) vs **closeRegistered** (line 1433, actually asks the engine to close the window) vs **finalizeWorld** directly
  (line 1521, when the window is already gone).
- `finalizeWorld(s)` (line 1407): the definitive close — `s.close1()` (a `synchronized` one-shot flag, line 1108) guards against double
  processing, syncs once more (unless `s.noSync`), unregisters the change listener, `DENY_ALL`, `clear()`s the view, removes from
  `SESSIONS`, remembers `LAST` page, schedules a save.
- The **admin view** (`adminView`, line 1778) never creates a session at all — a `DENY_ALL` **copy** in a fresh `SimpleItemContainer`
  (vanilla `/invsee` pattern) — so two viewers editing one vault is structurally impossible, and the admin path needs nothing from a
  page-arrow feature.

## R6. Retire-on-disconnect

**There is no `PlayerDisconnectEvent` listener anywhere in this mod** (confirmed: no `EREG`/event-registration import used for anything
but the container's own change event; grep for `PlayerDisconnectEvent` in this file returns nothing). Disconnect handling is two
separate, weaker mechanisms:

1. **The engine itself** closes every open window when a player entity leaves a world (`PlayerAddedSystem`, per the mod's own header
   note line 127 of `HANDOFF.md` / `VWindow.onClose0`, line 1819) — this fires `VSessions.windowClosed(s)` → `finalizeWorld(s)` in the
   *normal* disconnect case.
2. **`VTick` (1 s ticker, registered in `setup()`, line 2307) → `VSessions.tick()` (line 1750) → `tickOne(un, s, now)` (line 1729)** is
   the fallback for a session whose viewer object goes stale without the engine's own close firing: `pr == null || !pr.isValid()`
   increments `s.offline`; at `10` ticks (~10 s) `dispatchOffline(s)` (line 1678, closes the view from that world's own thread if the
   world still exists) runs; at `20` ticks (~20 s) `offlineFinalize(s)` (line 1670, retires it directly, logs `FINALIZE-OFFLINE`) runs
   as the absolute last resort.
3. **Plugin `shutdown()`** (line 2313) calls `VSessions.shutdownSync()` (line 1801: retires every live session) before `VStore.flushAll()`
   (line 926: writes every dirty vault) — this is the "normal stop / logout saves both sides" guarantee from the header (line 166).

A page-arrow feature that adds real ItemStacks to the container does **not** need new disconnect handling — it rides whichever of
these three paths already fires, since it is the same `s.view` object.

## R7. The profile-switch wait

- `VSessions.gate(u)` (line 1361), called at the very top of every `open()` (line 1531) and every `pageSwap` click (line 1620):
  1. `noteBusy(u)` (line 1346): `profile:busy:<uuid>` present → refuse now ("your profile is still loading").
  2. `noteEpoch(u)` (line 1336): first sight of an epoch is a baseline (contract section 4 rule 2); a **later, different** value marks
     `SWITCHED.put(u, now)`.
  3. `settleLeft(u)` (line 1353): seconds left of `VCfg.AFTER_SWITCH_MS` (default 30 000 ms, config row `afterSwitchSeconds`, line 480)
     since that switch — non-zero → refuse with a countdown message.
- An **already open** vault is also watched every tick: `tickOne` (line 1729–1748) checks `profile:busy` and the epoch on every live
  session and force-closes it (`dispatchClose`, line 1659) with a "your vault closed because your profile changed" message — so a
  chest window that is open WHEN a switch happens gets yanked, arrows and all, exactly like today's plain slots.
- **Nothing about this needs to change for arrows** — the gate runs before any window opens, and the tick-close runs on the whole
  session, not on individual slots.

## R8. Buy-page flow

- **Price**: `VStore.price(page)` (line 673): `0` at/under `FREE_PAGES`; else `PRICE + STEP * (page - FREE_PAGES - 1)`.
- **Confirm handshake**: `VStore.CONFIRM` (`ConcurrentHashMap`, line 632) keyed by `buyKey(u, page)` = `"buy:<uuid>:<page>"` (line 980)
  — **the SAME key for the page's Buy button and the `/vault buy` command** (so a click then a typed command, or the reverse, is the
  two-step confirm): `confirm(key)` (line 984) arms it for `CONFIRM_MS` (10 000 ms) on the first call, consumes-and-returns-true on a
  second call within the window; `armed(key)` (line 992) peeks without consuming (used to render "Sure? Buy page N"); `disarm(key)`
  (line 997) clears it (any nav click disarms — line 1855/1881).
- **The actual purchase**: `VStore.buy(u, name)` (line 1022) — **coins first** (`coins:fn:take` bridge function, must return `TRUE`,
  line 1029–1034; missing SkyyCoins or insufficient funds both refuse before anything else changes), THEN `VData.unlockTo(next)`
  (line 828: only succeeds if `unlocked == next - 1`, bumps `rev`), THEN `VStore.writeDoc` synchronously (line 1038) — **a failed write
  rolls the page count back (`VData.relock`, line 836) and refunds the exact coins (`VStore.refund`, line 1010)**, unless the page
  already holds items (`relock` refuses, the header calls this the "page kept" case, line 1042).
- **Callers**: the page's `"buy"` click (`VaultPage.handleDataEvent`, line 1888) and the `/vault buy` command (`VaultBuyCmd`, line
  2202) both do confirm → `VStore.buy` → refresh the page (`afterBuy`, line 1630, or `pageSwap` to jump straight to the new page,
  line 1900).
- A page-arrow feature reuses this untouched — an arrow only needs to call `VSessions.pageSwap`-equivalent logic for an **already
  unlocked** page; buying a locked page from inside the chest is out of scope unless Skyy asks for a "buy" arrow item too (open
  question, section 12).

## R9. Config rows (`config:def:SkyyVault`)

`ROWS` array, lines 459–486 (kit = `tools/skyycfg.py`, contract = `tools/CONFIG-CONTRACT.md`), emitted at line 487:

| key | type | default | binding |
|---|---|---|---|
| `freePages` | int | 2 | `field:VCfg.FREE_PAGES`; check `VHooks.checkFree`; after `VHooks.afterFree` |
| `maxPages` | int | 10 | `field:VCfg.MAX_PAGES`; check `VHooks.checkMax` (scans loaded vaults + a background `VScan`, line 305/1919) |
| `slotsPerPage` | int | 36 | `field:VCfg.SLOTS`; `new,danger` (only new vaults) |
| `pagePrice` / `pagePriceStep` | int | 50000 / 25000 | `field:VCfg.PRICE` / `VCfg.STEP` |
| `openMode` | choice | `page` | `field:VCfg.OPEN_MODE`; after `VHooks.afterOpenMode` (line 2142, flips `VCfg.PAGE_MODE`) |
| `afterSwitchSeconds` | int | 30 | `field:VCfg.AFTER_SWITCH_MS*1000` |
| `saveDelayMillis` | int | 1000 | `field:VCfg.SAVE_DELAY_MS` |

If arrows need their own admin-tunable knob (e.g. "show page arrows in chest mode: on/off", or which two slot indices they occupy),
a new row goes here (`ROWS`, after line 486) plus a matching `VCfg` field (after line 345) — the kit auto-adopts kit 1.1 fixes with
no code change (contract "Kit versions" table).

## R10. Commands

Built with the shared `cmd()` helper (line 2164) — every command is generated, so `tools/ci/lint.py` cannot see it directly; the script
self-checks permissions at build time (lines 2159–2162, 2328+). Full player tree (`VaultCmd`, line 2222, subcommands `buy`/`info`/
`pages`/`next`/`prev`, usage variant `<page>`) and admin tree (`VaultAdminCmd`, line 2282, subcommands `open`/`info`/`setpages`/
`config`/`reload`) are both listed in the header (lines 44–75) and match the code exactly. No command touches the container directly —
they all call into `VSessions`/`VStore` static methods, so a page-arrow feature does not need new commands (arrows are a click-only,
in-container affordance by design).

## R11. `VaultPage` (OUR custom page, page mode + `/vault pages`)

`VaultPage.build()` (line 1189) draws, purely with `UICommandBuilder.appendInline`/`set` (never a `.ui` file, per `HANDOFF.md` section
2): title, subtitle, **`< Prev` / page label / `Next >`** (lines 1217–1224), a row of page-number buttons (lines 1235–1243, current
green / owned blue / locked grey), the "Page N - X of Y slots used" line, **Open as chest** / **Buy page N** / **Close** buttons (lines
1256–1277), three help lines, one result line. Every button is bound with `UIEventBuilder.addEventBinding(BindingType.Activating, "#Id",
EventData.of("a", "<payload>"))`; clicks land in `handleDataEvent` (line 1836), which reads the payload with `jsonStr` (line 1141, the
same `"a":"..."` helper as SkyySacks/SkyyGuilds). **This is the page that ALREADY has working Prev/Next arrows — just not visible while
a chest window (mode 2 / `Page.Bench`) is open, which is exactly Skyy's complaint.**

## R12. How SkyySacks ships custom items (asset pack pattern to copy)

Source: `SkyySacks/build_skyysacks_0.7.6.py`, `sack_item()` (line 3676) and the assets block (lines 3673–3711).

- **Manifest**: `tools/skyybuild.py` `manifest()` (line 92) always sets `"IncludesAssetPack": True` — every Skyy mod jar already
  declares this; SkyyVault's own `manifest()` call (near the bottom of `build_skyyvault_0.1.1.py`, same pattern as every other mod)
  needs no change to ship new items.
- **Item JSON path**: `Server/Item/Items/<Category>/<Id>.json` inside the jar (SkyySacks uses `Utility/Skyy_Sack_<cat>_<tier>.json`,
  line 3700) — for the vault, something like `Server/Item/Items/Utility/Skyy_VaultArrow_Prev.json` / `..._Next.json`.
- **Item JSON fields actually used** (`sack_item`, lines 3676–3689):
  `TranslationProperties` (name/description keys into `server.lang`), `Categories` (`["Items.Tools"]`), `Icon` (a PNG path under
  `Icons/ItemsGenerated/...` — SkyySacks reuses a stock icon, `Utility_Bag_Seed.png`; a bespoke arrow icon would need its own PNG
  shipped the same way or a stock icon reused), `Quality`, `Recipe` (**omit this for a non-craftable decoration item** — the vault
  arrows are never crafted, only spawned in code via `VCodec.stackOf`/`new ItemStack(id, qty, ...)`, same as SkyyRolls' rolled items or
  SkyyCooking's graded dishes), `Model`/`Texture`/`IconProperties` (3D held-item look; can likely be omitted or copied from a simple
  vanilla item if the arrow is only ever seen sitting in a container slot, never held), `Tags` (`{"Family":[...], "Type":[...]}`),
  `MaxStack` (SkyySacks bags are `1`; arrows should also be `1` — never meant to stack or be moved as a stack), `Interactions`
  (`Secondary.Interactions[].Type: "OpenCustomUI"` — **not used for the vault arrow**, since the click must be caught at the
  container/slot level, not via a right-click-to-open-page interaction; section 13).
- **Language file**: `Server/Languages/en-US/server.lang`, one `items.<Id>.name=...` / `server.items.<Id>.name=...` / matching
  `.description=` line pair per item (lines 3701–3707).
- **No "cannot be dropped" item flag exists anywhere in this codebase or the engine.** Confirmed by `cpgrep.py` against
  `HytaleServer.jar` for `NoDrop`, `Undroppable`, `CantDrop`, `Soulbound`, `Unmovable`, `LockedSlot` — **zero hits**. "Cannot be picked
  up" for the vault arrows is not an item-level property; it is a **container-level** property, engine-verified in section 13:
  `ItemContainer.cantDropFromSlot(short)` / `cantRemoveFromSlot(short)` are backed by a per-slot `SlotFilter`, not by any field on the
  item's own JSON.

## R13. NEW engine finding: the mechanism a page-arrow feature actually needs

Nothing in SkyyVault (or any live Skyy mod) uses anything but `SimpleItemContainer.setGlobalFilter(FilterType.DENY_ALL/ALLOW_ALL)` —
an all-slots-or-nothing filter (grep across every `build_*.py` in the repo: only `DENY_ALL`/`ALLOW_ALL` global-filter calls exist,
never a per-slot one). Confirmed live against `HytaleServer.jar` with `tools/dev/reflect.py` and `tools/dev/bcfull2.py`
(`ItemContainer`/`SimpleItemContainer`/`FilterType`/`FilterActionType`/`SlotFilter`), a genuine **per-slot filter/click hook already
exists on the engine side and has never been used by any Skyy mod**:

- `ItemContainer.setSlotFilter(FilterActionType action, short slot, SlotFilter filter)` registers one filter per `(action, slot)` pair.
  `FilterActionType` has exactly three values: `ADD`, `REMOVE`, `DROP`.
- `SlotFilter` is a single-abstract-method interface: `boolean test(FilterActionType action, ItemContainer container, short slot,
  ItemStack stack)`, plus two built-in constants `SlotFilter.ALLOW` / `SlotFilter.DENY`.
- **Disassembly proof of the call chain** (`SimpleItemContainer` bytecode, via `bcfull2.py`):
  `cantRemoveFromSlot(short)` → if the container's `globalFilter.allowOutput()` is true, calls `testFilter(FilterActionType.REMOVE,
  slot, null)`; `cantAddToSlot(short, ItemStack, ItemStack)` → if `globalFilter.allowInput()` is true, calls
  `testFilter(FilterActionType.ADD, slot, stack)`. `testFilter` looks up the registered `SlotFilter` for that `(action, slot)` in a
  private `slotFilters` map and, if one is registered, **calls `filter.test(...)` and returns its negation** — i.e. `test()` returning
  `true` means "allowed", `false` means "denied". **`cantXxxFromSlot` is consulted by every real transaction method
  (`removeItemStackFromSlot`, `setItemStackForSlot`, `addItemStackToSlot`, `moveItemStackFromSlot`, ...) before it mutates the slot** —
  the same rule the codebase already knows ("inventory/containers only on the world thread").

**This is the mechanism for Wynncraft-style arrow items**: a custom class implementing `SlotFilter`, registered with
`container.setSlotFilter(FilterActionType.REMOVE, arrowSlot, arrowFilter)` (and probably `ADD` too, to refuse anything a player tries
to place over the arrow, and `DROP` to refuse dropping it out of the world) whose `test(...)` method:
1. treats being called at all as "the player just tried to interact with this slot" (the click signal Minecraft plugins normally get
   from a raw click event — Hytale's engine gives it via the filter callback instead, since the callback fires on the attempt
   regardless of outcome);
2. performs the page-swap side effect (equivalent to `VSessions.pageSwap`/`step`, but for a session whose `mode == 2`, i.e. chest
   mode, since page mode already has working buttons — section 1/11);
3. **always returns `false`** so the arrow item itself never actually leaves (or is buried under another item in) its slot.

**UNVERIFIED / open engineering risk (flag for the build pass, not resolved by this research pass)**: whether it is safe to mutate the
SAME container (`fill()`/`setItemStackForSlot` for the new page's items) from INSIDE a `SlotFilter.test()` callback that is itself
running in the middle of a transaction against that same container (reentrancy) — the codebase's own rule "a synchronized block holds
one call" suggests the safer shape is: `test()` only sets a lightweight flag / schedules a `world.execute(...)` task that performs the
actual page swap on the next tick, then returns `false`. This needs either a decompile of one transaction method
(`SimpleItemContainer#setItemStackForSlot`/`removeItemStackFromSlot`, with `bcfull2.py`) to see whether it holds a lock across the
`cantXxxFromSlot` check, or a real in-game test, before it is built.

## R14. The minimal set of places a page-arrow feature must touch

Everything below is inside `SkyyVault/build_skyyvault_0.1.2.py` (copied from the live `build_skyyvault_0.1.1.py`), following the
project rule "copy + edit, write the new version from the LIVE one":

1. **Reserve arrow slot indices.** Decide (Skyy decision, section 15 Q1) whether arrows live in 2 of the existing `cap` slots
   (reduces real storage by 2, and needs a migration rule for any already-saved vault that has real items sitting in those exact
   indices) or the container is enlarged by a fixed amount beyond `d.cap` for CHEST-mode windows only (page mode keeps `cap` exactly,
   since it already has button arrows — section 1/11). Either way this changes **`VSessions.newSession`** (line 1463, container size
   and where `fill()` writes the arrow icons) and likely **`VData`** (a new `displayCap`/`storageCap` distinction if the container is
   enlarged, since `VData.cap`/`page()`/`used()`/`copyIn()`, lines 493–544, currently treat every index as real storage).
2. **Never let arrow slots reach the vault file.** `VSessions.fill()` (line 1445) and `VSessions.syncView()`/`VData.copyIn()` (lines
   1386–1399, 536–544) must skip the reserved indices entirely (fill them with the arrow `ItemStack`, never read them back into
   `now`/`copyIn`) — otherwise the arrow item gets saved as if it were a real vault item, or a real item a player manages to place
   there (if the filter is ever bypassed) gets silently dropped from the save.
3. **Place the arrow items only for CHEST-mode sessions** (skip for `mode == 1`, since `VaultPage.build()` already draws working
   Prev/Next buttons — section 11): in `newSession` (line 1463) right after `fill()` succeeds, or in a new small helper called from
   there.
4. **Register the per-slot filters** (new engine mechanism, section 13) on `s.view` for each arrow slot: `setSlotFilter(ADD, slot,
   DENY-and-nothing-else)` and a custom `SlotFilter` for `REMOVE` (and `DROP`) that triggers the page swap. This is new code in
   `VSessions`/`VWindow` (near lines 1463–1476), and a new small class (parallel to `VChange`/`VWindow`, lines 1114–1121) implementing
   `SlotFilter`.
5. **Reuse the existing swap logic**, not duplicate it: `VSessions.swap(s, page)` (line 1478) already does "sync the old page, fill the
   new one, roll back to `noSync` on any mismatch" — the arrow's callback should call this (via a scheduled world-thread task per the
   reentrancy risk in section 13), then re-place the arrow icons into their reserved slots of the NEW page's view (since `fill()`
   cleared the whole container).
6. **Config**: if the feature should be toggleable or configurable (which two slots, or on/off in chest mode), add rows to `ROWS`
   (line 459) + fields to `VCfg` (line 334) — optional, not required for a first cut.
7. **Assets**: two new item JSONs (`Server/Item/Items/Utility/Skyy_VaultArrow_Prev.json` / `..._Next.json`, pattern from
   `SkyySacks.sack_item`, section 12) with no `Recipe` and no `Interactions.Secondary` (the click is caught by the container filter,
   not by a right-click page-open), added to the `files` dict passed to `B.assemble()` at the bottom of the build script, plus two
   language lines. Icons can reuse a stock arrow-looking icon under `Icons/ItemsGenerated/` (needs a quick look at `Assets.zip` for a
   suitable one, or Skyy provides one) or be genuinely decorative-only (no 3D held-item concern since these items are only ever meant
   to sit in a container slot).
8. **Nothing else needs to change**: config rows for `slotsPerPage`/`maxPages`/`freePages`/prices, the buy flow, the profile-switch
   gate, session locking, retire-on-disconnect, the admin commands and the admin read-only view are all orthogonal to this feature and
   were confirmed unaffected while reading them (sections 5–10).

## R15. Open questions for Skyy (do not guess these in code)

1. **Where do the two arrow slots live?** Reserve 2 of the existing `slotsPerPage` (default 36 → 34 usable) or add a fixed number of
   extra slots beyond `cap` just for chest-mode windows (visual row-of-9 alignment unverified — `Page.Bench`'s vanilla chest layout for
   a non-multiple-of-9 capacity is one of the pre-existing UNVERIFIED items in the 0.1.1 header, line 141, and adding slots makes that
   question sharper, not easier).
2. **Do arrows also render in page mode's window**, for visual consistency with chest mode, even though page mode already has working
   Prev/Next buttons on the custom page itself? (Skyy's ask only mentions chest mode.)
3. **Should a locked/unbought next page show a "Buy" arrow item** inside the chest (parallel to the page's own Buy button, section 8),
   or should the chest simply have no "next" arrow past the last owned page (matching "the arrow row itself doesn't scroll past what
   you own", the safer first cut)?
4. **Icon**: reuse a stock arrow-shaped icon from `Assets.zip`, or does Skyy want a custom one drawn/sourced?
5. **The reentrancy question in section 13** is an engineering decision for whoever builds this (defer the swap to a scheduled world
   task vs. doing it inline in `test()`), not a design question for Skyy — flagged here so it is not skipped.

## R16. Addendum (second read-only pass, same day): the packet path + the reentrancy answer

*This section fills the one gap the pass above left (the network/packet side of "how a click reaches the server", and whether a
server-side cursor slot exists) and resolves the reentrancy risk section 13 flagged as unverified. Same rules: nothing built, nothing
deployed, engine facts re-confirmed live against `HytaleServer.jar` with `tools/dev/reflect.py` and a small ad-hoc disassembler built on
`javassist.bytecode.InstructionPrinter` (same library `tools/dev/bcfull2.py` already uses), scratch files deleted after.*

### R16.1 The packets, and the handler that turns them into container calls

A vanilla chest window's clicks reach the server as one of four packets, all in `com.hypixel.hytale.protocol.packets.inventory`:

| Packet | Fields | Used for |
|---|---|---|
| `MoveItemStack` | `fromSectionId, fromSlotId, quantity, toSectionId, toSlotId` (all `int`) | a normal click-drag: pick up in one slot, place in another, in ONE packet |
| `SmartMoveItemStack` | `fromSectionId, fromSlotId, quantity, moveType` (`SmartMoveType`: `EquipOrMergeStack` / `PutInHotbarOrWindow` / `PutInHotbarOrBackpack`) | shift-click / quick-move — the SERVER picks the destination, no `to*` fields |
| `InventoryAction` | `inventorySectionId, inventoryActionType` (`InventoryActionType`: `TakeAll` / `PutAll` / `QuickStack` / `Sort`), `actionData` | the chest's bulk buttons |
| `DropItemStack` | `inventorySectionId, slotId, quantity` | the drop key on a slot |

All four are handled server-side by `com.hypixel.hytale.server.core.io.handlers.game.InventoryPacketHandler` (`handle(MoveItemStack)`,
`handle(SmartMoveItemStack)`, `handle(InventoryAction)`, `handle(DropItemStack)`) — each hops once to the owning `World.execute(Runnable)`
(so the actual work always runs on the world thread, matching the codebase's own rule) and then calls a matching static helper on
`com.hypixel.hytale.server.core.inventory.InventoryUtils`: `moveItem(Ref, fromSection, fromSlot, qty, toSection, toSlot, ComponentAccessor)`,
`smartMoveItem(...)`, `takeAllWithPriority`/`putAll`/`quickStack`/`sortStorage`, `dropAllItemStacks`. (`GamePacketHandler` separately owns
`handleSendWindowAction`/`handleCloseWindow` for the generic `WindowAction`/`CloseWindow` packets — window open/close plumbing, not slot
clicks.)

**Section-id resolution** (`InventoryUtils.getSectionById(Ref, int sectionId, ComponentAccessor)`, disassembled in full): a
**non-negative** id is a **window id** — `player.getWindowManager().getWindow(id)`. If that window is a `ValidatedWindow` (ours,
`VWindow`, already is), its `.validate(ref, ca)` runs FIRST and a `false` closes the window and aborts the whole action before the
container is even fetched — exactly the mechanism `VWindow.validate` / `VSessions.stillValid` already relies on for the profile-switch
gate (section 7), now confirmed to be the SAME gate the engine consults on every click, not just on player movement. If validation
passes and the window is an `ItemContainerWindow`, `.getItemContainer()` is returned. A **negative** id is one of the built-in
inventory components via `InventoryComponent.getComponentTypeById(id)`; the constants (read directly off the class,
`InventoryComponent.HOTBAR_SECTION_ID` etc.) are `HOTBAR=-1, STORAGE=-2, ARMOR=-3, UTILITY=-5, TOOLS=-8, BACKPACK=-9, DUMMY=-10`
(`INACTIVE_SLOT_INDEX=-1` is unrelated, a slot-index sentinel not a section id). `DEFAULT_STORAGE_ROWS=4` / `DEFAULT_STORAGE_COLUMNS=9`
/ `DEFAULT_STORAGE_CAPACITY=36` are also plain static fields on `InventoryComponent` — the vanilla PLAYER inventory's own shape, not a
limit on any other container (see 16.3).

**No server-side cursor/held-item container exists.** Every constant on `InventoryComponent` was read directly; there is no
`CURSOR_SECTION_ID` or equivalent, and `DUMMY_SECTION_ID=-10` is the closest thing to a "not a real container" sentinel. Every packet
above carries an explicit `fromSection/fromSlot` (and, for `MoveItemStack`, an explicit `toSection/toSlot`) — nothing carries a
"cursor" section. The item that visually follows the mouse mid-drag is purely a CLIENT-side prediction; the server only ever sees one
atomic transfer per packet (or, for the Smart variants, one atomic "take from here, server picks where" transfer). **This directly
answers "is there a server-side cursor slot": no.** Design the arrow feature around discrete from-slot/to-slot (or from-slot-only)
packets, never a cursor state machine.

### R16.2 The move primitive, proven zero-leak by construction, and what the client sees on a refusal

`ItemContainer.moveItemStackFromSlotToSlot` → `internal_moveItemStackFromSlot` (disassembled in full, all overloads and lambdas): for a
same-container "swap" it checks `cantRemoveFromSlot(fromSlot)` on the source, then (only if that passed) `cantMoveToSlot`/`cantAddToSlot`
on the destination, **before touching a single slot**, and returns a `MoveTransaction` built with `succeeded=false` the instant either
check denies — the method returns right there; it never reads or writes the container again. The one case that DOES mutate before a
check can fail (destination occupied by a non-stackable item, i.e. an actual swap) explicitly rolls back: it puts the just-removed stack
straight back with `internal_setSlot(fromSlot, ...)` BEFORE returning the failed transaction. This is disassembly-level proof, not
inference, that a `SlotFilter` `DENY` on the arrow slot's `REMOVE` (and `ADD`, so nothing can be dropped on top of it) makes the click a
true no-op at the engine level — there is no path for the arrow stack to actually leave its slot, so "zero item leaks" holds by
construction, not by care taken in our own code.

`removeAllItemStacks()` and `dropAllItemStacks()` were confirmed (by disassembly) to call `cantRemoveFromSlot`/`cantDropFromSlot` per
slot too, so a chest's "Take all" button also respects the filter and skips the arrow slot; `InventoryUtils.smartMoveItem` was not
individually re-disassembled this pass (see the belt-and-braces note in 16.3).

**What the client sees on a refusal**: `ItemContainer.sendUpdate(Transaction)` — called unconditionally by every move/remove/add
wrapper after the fact — itself does `if (!transaction.succeeded()) return;` before dispatching anything. So a denied move fires **no**
`ItemContainerChangeEvent` at all, to either the existing whole-container `registerChangeEvent(Consumer)` listener this mod already uses
(`VChange`) or the per-slot `registerChangeEvent(short, Consumer)` overload section 4 flagged as untried and worth checking — **neither
one fires on a filter-denied attempt**, because both sit behind the same `sendUpdate`/`succeeded()` gate. (The per-slot overload is
still worth adopting some day for the mod's OTHER, non-denied slots — a real change elsewhere in the vault would no longer force a
full-container `syncView` — but it is not an alternative path to "notice a denied click"; nothing is.) Since the container's real state
never changes on a denial, no packet write was observed anywhere in this call chain that would explicitly correct the client's
optimistic UI. **Flag as UNVERIFIED, needs an in-game check**: does a real client cleanly refuse to lift the arrow (most likely, since
Hytale's window UI already appears to be server-authoritative rather than doing local prediction — SkyyVault's own `FilterType.DENY_ALL`
admin view already ships on this exact mechanism and is reported working), or does repeated fast clicking on the same denied slot ever
show a visual glitch that needs a companion `Window.setNeedRebuild()` nudge? This was never specifically tested against click-spam.

### R16.3 The reentrancy question (section 13) is answered

`SimpleItemContainer`'s `lock` field (declared as the plain interface `java.util.concurrent.locks.ReadWriteLock`) is constructed in
**every** constructor as `new java.util.concurrent.locks.ReentrantReadWriteLock()` (confirmed by disassembling all three constructors).
`ReentrantReadWriteLock`'s write lock is, by contract, reentrant for the thread that already holds it. Every mutating path
(`writeAction`, `moveItemStackFromSlotToSlot`, `setItemStackForSlot`, `clear`, ...) acquires and releases that SAME lock instance around
a `Supplier`/`Function` call (`writeAction`, disassembled: `lock.writeLock().lock(); try { return supplier.get(); } finally {
lock.writeLock().unlock(); }`, with the try/finally shown as an exception table rather than javassist-visible catch blocks). Since a
`SlotFilter.test()` callback fires synchronously, on the calling (world) thread, from inside an outer `writeAction` call that is
already holding that write lock, a nested call back into `s.view.clear()` / `setItemStackForSlot(...)` (i.e. `VSessions.fill`, section
3) on the SAME container instance re-enters the SAME lock on the SAME thread — **this will not deadlock.** Tracing the denial branch of
`internal_moveItemStackFromSlot` end to end (16.2) also shows it never touches the container again after `cantRemoveFromSlot` returns
`true`, so a full page-swap run as a side effect inside the filter callback cannot be clobbered by, or race against, the rest of that
same call. Section 13's flagged risk is real code to write carefully, but it is not a dead end, and it is not a deadlock risk.

**Still recommended (belt-and-braces), and still the right default for the build pass**: keep `test()` itself to just noting the
attempt (set a flag / stash `(session, direction)`) and run the actual `VSessions.swap`-equivalent call from a `World.execute(new
PageSwapTask(...))` scheduled on the same tick — the exact pattern this mod already uses for `VCloseTask` (section 6). Reasons to prefer
this over the now-proven-safe inline call: (a) it costs one extra tick of latency, nothing else; (b) it means nobody has to separately
prove `smartMoveItem`'s and the bulk `InventoryAction` handlers' post-denial behaviour is as clean as the one call chain traced in 16.2
before relying on inline reentrancy there too; (c) it keeps `SlotFilter.test()` — which the engine may call from more than one code
path, present and future — trivially side-effect-free from the container's own point of view, which is the safer property to hold onto
even though this pass found no counter-example.

### R16.4 One more data point for open question 15.1 (does a bigger container get a 5th row)

`ContainerWindow`'s constructor (disassembled) does nothing but `super(WindowType.Container)` and store the `ItemContainer` — no row or
size field anywhere on the window. The wire format for a container's contents, `com.hypixel.hytale.protocol.InventorySection`, carries
a plain `short capacity` plus a `Map` of slot→item — nothing here or in `WindowType` (a 7-value enum: `Container, PocketCrafting,
BasicCrafting, DiagramCrafting, StructuralCrafting, Processing, Memories` — no row-count payload) hardcodes 36 or 4 rows anywhere in the
server jar. That is real, if indirect, evidence FOR "yes, a bigger container should render as more rows" — the client is being sent a
bare number and must already know how to lay out something other than exactly 36 slots, since `slotsPerPage`'s already-configured
range (9-90) only makes sense if the client can already draw more than 4 rows of 9 for a `Page.Bench` window. It is inference from the
ABSENCE of a server-side limit, not a confirmed client behaviour, so the in-game check section 15 Q1 already asks for still stands.
**One concrete recommendation this adds**: whatever the final slot count is, keep it an exact multiple of 9 (e.g. 36+9=45, not 36+2=38)
— a ragged final row reads as broken far more readily than a bigger-than-36 container is likely to be rejected outright, given nothing
server-side caps it below the already-live `slotsPerPage` maximum of 90.
