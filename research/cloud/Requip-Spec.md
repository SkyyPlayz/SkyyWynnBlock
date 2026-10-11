# Requip (Wardrobe v2) - design spec (one gear pool per profile, loadouts pick from it)

*Cloud draft 2026-10-11. Spec only: no code, nothing built. Owner: Skyy (they/them). Replaces the 0.1 swap model of
`research/cloud/Wardrobe-Spec.md` (sections 1, 3, 5.2, 6.2) - its refusals, files, journal and page rules are kept where this file says so.*

## 0. Decisions this spec follows

- `docs/answered/gear.md` line 153, TESTED + LOCKED 2026-10-10 (Skyy, SkyyWardrobe 0.1 screenshots), word for word:
  "i can save a set, but i cant make a new loadout, because it just changes what this one shows when i swap. you might have to do like
  skyblock does where you have to click unequip, the set you are wearing vanishes, and reappears when you equip it.  but i have a better
  idea. in fairy tail Erza has a magic call requip. where she stores armor and weapons in an extradimensional space around her, and using
  magic could instantly swap armor types.    im picturing an infinite storage space like a chess, you can dump all your gear into. and
  everything in there is selectable for the loadouts. (might be easier if we added an armor one, and items one for weapons and tools
  /potions and food. then also let it pull from the pocket dimension for blocks in the hot bar. (so they auto refill.)"
  -> REQUIP: per-profile INFINITE ARMOR space + ITEMS space (weapons, tools, potions, food); a loadout = references picked from them
  (4 armor + 9 hotbar + pet + summon + abilities); a new loadout never needs the gear worn first; Equip = worn armor / hotbar go back into
  the spaces and the picks come out; hotbar BLOCK slots refill from the Pocket Dimension. Spec first (cloud), build = Ultracode.
- `docs/answered/gear.md` line 154, LOCKED 2026-10-10 (Skyy, Requip clarified), word for word: "so you compile gear, then select what
  each kit uses from the pool. so your good weapon, you can select in every loadout, and swap out the armor, and tool in your hot bar
  for the job" -> the spaces are ONE POOL; the SAME item can be picked in SEVERAL loadouts; a loadout only says which pooled item goes in
  which armor / hotbar slot. **It never owns a copy.**
- Still standing (not re-decided): gear.md line 141 (a loadout = armor + hotbar + pet + summon + abilities with modifiers; one click
  swaps all), line 140 (loadout swapper), line 122 (own mod SkyyWardrobe, menu tile + `/wardrobe`, 18 slots / 4 free + Overall Level
  10 / 20 / 30 / 40, partial sets keep the worn piece, no unidentified pieces, slot names, 500-coin look edit), line 120 (look edit of a
  whole set from inside - the W2 Looks of `research/cloud/Wardrobe-Spec.md` section 4 move onto pooled armor unchanged).
- `tools/PROFILES-CONTRACT.md`: per-profile data under `pkey`, `profile:busy`, `profile:epoch` (settle window).
- `tools/CONFIG-CONTRACT.md` + `tools/skyycfg.py`: every number below is a Server Setup row, times in seconds.
- `HANDOFF.md` 2 + 3: inline pages, vanilla look (`tools/skyyui.py`), element ids without underscores, **never a metadata ItemStack in an
  ItemGridSlot**, no page update from hover; player commands `hytale:Adventurer` on root and every variant.
- `PROJECT-RULES.md` 4: items that could be lost / duplicated + saved data + migration = **Ultracode**; one-time migrations follow the
  migration rule (old defaults only, History snapshot, change-log line with Undo, run-once marker, bytes kept).

## 1. Plain words (for Skyy)

- **Requip** is your gear pool. Two spaces per profile: **Armor** (helmets, chests, hands, legs) and **Items** (weapons, tools, potions,
  food). Dump gear in from the Requip page (click an item, or Deposit all). It holds as much as you will ever need (section 9).
- **Loadouts** do not hold gear any more. A loadout is a list of picks: "this helmet, this chest, ..., my best sword in hotbar 1, my
  pickaxe in hotbar 2, Stone from my bags in hotbar 9", plus pet, summon and abilities. The same sword can be picked in every loadout.
- You build a loadout by clicking a slot and picking from the pool - nothing has to be worn first (the 0.1 problem is gone).
- **Equip**: what you wear in the slots the loadout picks goes back into the pool, the picks come out onto you. One click, one safe
  transaction - a crash at any moment can never copy or lose an item.
- Your best sword is only ever in ONE place: in the pool, or on you. If loadout A put it in hotbar 1 and loadout B wants it in hotbar 2,
  Equip B just moves it from slot 1 to slot 2.
- **Block slots** (hotbar only) pull from your Magic Bags (Pocket Dimension) and keep refilling while you build.

## 2. What changes from 0.1 (and what stays)

| 0.1 (live, `SkyyWardrobe/build_skyywardrobe_0.1.py`) | Requip (0.2) | Why |
|---|---|---|
| Each loadout STORES its own stacks (docstring lines 16-37) | Loadouts store **references** (entry ids); stacks live once in the pool | gear.md 154 |
| A new loadout = Equip an empty one, then Save current (lines 31-34) | Click a slot, pick from the pool | gear.md 153 "cant make a new loadout" |
| "Equipped" loadout = the gear on you belongs to it | Gear on you belongs to the POOL (entry state OUT); a loadout is only marked "last equipped" | one item, many loadouts |
| Equip swaps live <-> loadout array (lines 1574-1688) | Equip moves live -> pool and pool -> live (and live -> live for a shared item) | same transaction shape |
| Kept: lossless slot format, atomic write + read back, write-ahead journal chain, crash repair at join, refusals, pets / abilities bridge, slots / unlocks, `swap.keepIds` | same code, extended (sections 7-8) | proven in game 2026-10-10 |

## 3. The two spaces

### 3.1 What goes where

| Space | Accepts | Classifier (UNVERIFIED P2) |
|---|---|---|
| **Armor** | any item that fits an armor spot (Head / Chest / Hands / Legs): vanilla, The Armory pool, SLVR / Arcane / Voidcloak, our own sets, look ids `Skyy_Look_*` | the item asset's armor slot (the same test the engine uses to allow it in the Armor section) |
| **Items** | weapons (incl. bows, staffs, wands, spellbooks, kunai, Bo, wraps / gauntlets), tools (pickaxe, hatchet, shovel, hoe, rod, multitools), potions, food, other usable consumables | asset Weapon / Tool component, or a consumable interaction; fallback id prefix (`Weapon_`, `Tool_`, `Potion_`, `Food_`, `Skyy_Food_`) + Server Setup allow table |

### 3.2 Refused (and why)

| Refused | Why | Where it goes instead |
|---|---|---|
| Blocks + materials (anything with a Magic Bag home type, `sacks` `homeOf` != null) | they belong in the Pocket Dimension; hotbar block slots pull from there (section 6) | Magic Bags |
| Unidentified gear, mystery boxes | LOCKED gear.md 122 ("no unidentified pieces") - identify first | inventory |
| Magic Bags, backpacks, anything that holds items | storage inside storage = a dupe surface | inventory |
| Accessories / talismans | SkyyAccessories' own bag (per profile) | Accessory Bag |
| `swap.keepIds` (default `Skyy_Menu`, `Skyy_Vault_*`) | menu item / vault arrows are buttons, never stored | stay put |
| Item ids the game no longer knows | cannot be rebuilt safely | stay in inventory (already pooled ones stay pooled, section 5.3) |
| Server Setup `items.deny` ids | owner choice | inventory |
| Pets | pets are SkyyPets records, not items - a loadout names the pet id (0.1 bridge, kept) | - |

### 3.3 Entries (the pool's units)

- **Unique entry** (max stack 1: all armor, weapons, tools): one item = one entry with a stable **entry id** (`eid`, 16 random hex
  characters, never reused). Rarity, level, rolls, reforge, durability live in the stack itself (lossless format, section 8.1).
- **Kind entry** (stackables: potions, food): one entry per KIND (id + metadata, the 0.1 `WdCodec.kind` rule, lines 693-703) with a
  count (stored as a Long, taken out in max-stack pieces). Deposit merges into the existing kind entry.
- Entry state: **IN** (the stack is in the pool file) or **OUT** (it is on you or somewhere in the world; the file keeps only a
  display copy - id, name, rarity, Lv - that can NEVER be turned back into an item). This is the dupe rule: the pool only holds a
  rebuildable stack while the item is not in the world.
- **The stamp:** a unique item leaving the pool gets a tiny metadata key `SkyyRequip = { e: "<eid>" }` (no player id, nothing personal).
  It is how Requip recognises "this is my pooled sword" when it comes back, even after a reforge, repair or level-up while it was out
  (UNVERIFIED P1: those actions keep foreign metadata keys). Kind entries are never stamped (a stamp would stop potions stacking).
  Take out (section 4) removes the stamp - an item that leaves Requip for good is a plain item again.

## 4. Getting items in and out

| Action | Where | Does | Rules |
|---|---|---|---|
| **Deposit (click)** | Requip page, "Your inventory" panel = OUR non-draggable ItemGrid copy of storage + backpack + hotbar (metadata-free icons, HANDOFF 2) bound to SlotClicking (the SkyyMenu launcher pattern) | that stack moves into the right space | refused items show greyed with the reason on hover; worn armor is deposited from the Armor panel's "Put in pool" button |
| **Shift-click** | same grid | same as click (UNVERIFIED P3 whether SlotClicking carries the shift key; if it does, shift = deposit and plain click = show details) | - |
| **Deposit all** | page button + `/requip dump` | every allowed stack in storage + backpack goes in (hotbar only if `deposit.hotbar` is on, default off); one transaction, one chat line "Deposited 14 items (3 refused - see page)" | keepIds never; refused items stay |
| **Take out** | entry card button | IN entry -> inventory (storage, hotbar, backpack - only where it fits WHOLE, the 0.1 Clear rule lines 1701-1720); stamp removed; the entry is deleted and every loadout pick of it shows "removed" | "Inventory full" = nothing moves; asks twice when the entry is picked in a loadout |
| **Forget** | card of an OUT entry that is not with you | deletes the display copy + every pick of it (the item itself is wherever it is; it is a plain stamped item and can be deposited again as a NEW entry) | asks twice |
| **Admin** | `/requipadmin give <player> ...` | runs the same transaction | op only |

No client drag in or out of the page (`AreItemsDraggable: false`): every move is a server-side button (the SkyyVault 0.1.5 lesson).

### 4.1 Auto-pull toggle (Skyy 2026-10-11 - "like the mining bags, but for gear")

Skyy: "what i picture is like the mining bags. but for gear. (you can toggle weather or not it auto pulls from your inventory.)"
- One toggle per profile on the Requip page: **Auto-pull ON / OFF** [default OFF; Server Setup row `requip.autoPullDefault`].
- ON: the same model as the Magic Bags - a sweep every 2 s (SkyySacks 0.7.16 `SweepTask`, the "sweep removes exactly `take` from the
  slot" rule, file header lines 4-14) moves accepted gear (section 3.2: armor, weapons, tools, potions, food) from the STORAGE and
  BACKPACK sections into the pool, each move through the same write-ahead journal as a Deposit (section 7).
- Never pulled: anything worn, anything in the hotbar (Hytale's default pickup spot - the player keeps what they hold), stamped items
  that a loadout currently has OUT, and the refused kinds. Kind entries (potions / food) are only pulled if Requip already holds that kind.
- Order with the Magic Bags: blocks / materials go to the bags (SkyySacks), gear to Requip - the two accept lists never overlap
  (section 3.2), so both sweeps can run without fighting over a stack.
- UNVERIFIED (probe P11, local): two 2 s sweeps on the same inventory never race (stagger by 1 s, or one bridge call
  `sacks:fn:sweepNow` order).

## 5. Loadouts = references

### 5.1 A pick per slot

Each of the 13 slots (Head, Chest, Hands, Legs, Hotbar 1-9) holds one of:

| Pick | Meaning on Equip |
|---|---|
| **Item** `eid` | that pooled item goes in this slot |
| **Kind** `eid` + amount (default: one full stack) | up to that many of the potion / food come out |
| **Pocket block** `itemId` + target (hotbar only, section 6) | taken from your Magic Bags, refilled while equipped |
| **Keep** (default for a slot you never touch) | the slot is not touched (LOCKED gear.md 122 "partial sets keep the worn piece") |
| **Empty** | whatever is there goes back into the pool (or the inventory if it cannot be pooled) |

Plus pet, summon and abilities exactly as 0.1 (`WdBridge`, lines 1344-1435; `pets:fn:loadoutGet/Set`, `class:fn:loadoutGet/Set`).
An item pick only accepts entries of the right space and spot (a helmet only on Head; Items entries only on hotbar).

### 5.2 Picker UI (1120 x 900 page, the 0.1 size, line 2275)

```
+---------------------------------------------------------------------------------------------------------------+
| REQUIP - profile "Fox"          Loadouts 6 / 18          [Armor space] [Items space] [Your inventory]  [Close] |
+--------------------------+------------------------------------+------------------------------------------------+
| LOADOUTS (9 per page)    | LOADOUT 2 "Mining"   [Rename]      | POOL - Head pieces (filtered by the slot)      |
| 1 Combat    LAST WORN    |  [H] [C] [Ha] [L]   Pet: Rock Mole |  [ ][ ][ ][ ][ ][ ][ ][ ][ ]   9 x 5 = 45     |
| 2 Mining    > editing    |  hotbar [1][2][3]...[9]            |  [ ][ ][ ][ ][ ][ ][ ][ ][ ]   per page       |
| 3 Farming                |  Summon: -   Abilities: Dash, ...  |  ...                                          |
| 4 (empty)                |  selected slot: Hotbar 2           |  name / rarity colour / Lv under each icon      |
|                          |  [Pick] [Keep] [Empty] [Pocket...] |  "in 3 loadouts"  "ON YOU"  "NOT WITH YOU"      |
| [Equip 2]  [Save pets +  |                                    |  [< Page 1/23 >]  Sort: newest / rarity / Lv  |
|  abilities]              |                                    |  Search (text field, id or name)               |
+--------------------------+------------------------------------+------------------------------------------------+
| Deposit all   |   Purse ...   |   one-line help: click a slot, then click an item in the pool               |
+---------------------------------------------------------------------------------------------------------------+
```

- Column widths: 250 + 340 + 466 + 4 gaps of 16 = 1120 (9 cells of 48 + 8 gaps of 2 = 448 fit in 466).
- Every icon = `new ItemStack(id, 1)` (never the real stack: metadata, HANDOFF 2); rarity / Lv / reforge as text, hover = SkyyGear's
  tooltip lines (`gear:fn:stats`), no update from hover.
- Click a slot -> the right panel filters to what fits; click an entry -> picked (no item moves; only the loadout file changes).
- Page rebuilt only after a click (0.1 E6 rule); the page carries a token, a click from a stale page rebuilds it (0.1 lines 2124-2254).
- **Save pets + abilities** = 0.1 "Save current" minus the items part (pets / summon / ability snapshot of now into this loadout).
- The 0.1 equipped marker becomes **LAST WORN** (display only).

### 5.3 When a picked item changes

| Case | What happens |
|---|---|
| Item is OUT and on you (any section) | Equip moves it live -> live into the slot (no pool trip) |
| Item is OUT and not on you (dropped, in a chest, in the Vault, traded, died) | slot treated as **Keep**, note "Best Sword is not with you"; card shows NOT WITH YOU; Forget available |
| Reforged / repaired / levelled while out | same entry (the stamp); the pool stores the new stack when it comes back (P1) |
| Reforged into a different item id (look change at The Armory table while worn) | stamp kept -> same entry, new id; picks still point at the entry; a pick on a now-wrong spot (cannot happen for looks - same slot) is skipped with a note |
| Kind entry used up (potions drunk) | Equip takes what is left; 0 left = the entry stays as "0 left" while any loadout picks it, then goes |
| Kind entry: you carry more of the same kind | on the way back ALL of that kind in the slot returns to the entry (it is the same kind) |
| Item taken out with Take out / Forgotten | every pick of it shows "removed"; that slot acts as Keep until re-picked |
| Item id deleted from the game (pack removed) | entry stays IN, greyed "unknown item"; never put on a player (0.1 `known()`, lines 704-712); comes back if the pack returns |
| Durability 0 / broken | stays an entry; Equip still moves it (vanilla decides what a broken item does) |
| Same stamped eid deposited twice (a dupe made elsewhere, e.g. a SkyyProfiles crash rollback) | the second one becomes a NEW entry, WARN line in `requip.log` (admin audit); never refused, never deleted |

## 6. Pocket Dimension block slots (auto-refill)

Facts (`SkyySacks/build_skyysacks_0.7.16.py` docstring lines 84-94 and 113-117):
- SkyySacks already has a **stack auto-refill**: every 2 s the stacks a player USED since the last tick top up from the bag pool when that
  bag is carried; per-player mode Hotbar only (default) / Full inventory / Off; Server Setup `bags.refill` + `bags.refillDefault`.
  It **never fills an empty slot** and never a stack with metadata.
- Bridge for other mods: `sacks:fn:count`, `sacks:fn:all`, `sacks:fn:take {UUID, itemId, qty} -> Long`, `sacks:fn:put` (refund of a take
  in the last 60 s only), `sacks:fn:commit`. World thread only, settled profile key, a bag of that item's home type (or the Omni) carried.

Requip rules:
1. A **Pocket block** pick = item id + target (default = the item's max stack). Only items with a Magic Bag home type; only hotbar.
2. **Equip**: `sacks:fn:take(target)` -> a plain `ItemStack(id, n)` (no metadata, no stamp) into the slot; a failed place = `sacks:fn:put`
   refund in the same task. No bag carried / 0 in the bags = slot left as Keep, note "No Stone in your bags".
3. **While equipped**: Requip publishes `requip:pocket:<uuid>` = `Map<Integer slot, String itemId>` (the reserved block slots of the worn
   loadout). **SkyySacks change (0.7.17, small):** its 2 s refill also refills a reserved slot that is EMPTY or below target - so a slot
   you build down to 0 refills too (today it would stay empty). One owner of every bag move (SkyySacks), no race. Without that SkyySacks
   version: the existing refill tops up used stacks; an emptied slot waits for the next Equip.
4. **Leaving the loadout** (Equip another one, slot not Keep): the block stack goes back to the bags through a **new**
   `sacks:fn:deposit {UUID, itemId, qty} -> Long accepted` (SkyySacks 0.7.17; same gates; bag capacity respected). What does not fit:
   stays in the inventory (storage, then backpack; never dropped). Without the new fn: the stack moves to storage and the 2 s sweep
   collects it (UNVERIFIED: SkyySacks KEPT counts may keep it in the inventory - fine, nothing lost).
5. Blocks are never stored in Requip; the journal only records "pocket take n / pocket deposit n" for the crash repair (section 7.4).

## 7. Equip - one write-ahead transaction

### 7.1 Plan (pure, nothing moves)

On the player's world thread, after the 0.1 gate (dead, combat 10 s, `profile:busy`, 30 s settle after a profile switch, 1 s gap, one
change at a time, stale page - `WdGate`, lines 2035-2122). For each of the 13 slots, compare live stack X with pick T:

| X \ T | Keep | Empty | Item / Kind entry | Pocket block |
|---|---|---|---|---|
| X is the picked entry already (stamp / kind match) | - | - | **no move** | - |
| X poolable (or stamped) | no move | X -> pool | X -> pool, T -> slot | X -> pool, take blocks |
| X not poolable (refused, keepIds) | no move | X -> storage / backpack (whole fit) else no move | same: X -> storage / backpack first; no room = slot skipped | same |
| X empty | no move | no move | T -> slot | take blocks |

T OUT and on you elsewhere = a **relocate** move (live slot A -> slot B; done before the pool moves so the slot it leaves can be refilled).
T OUT and not on you = slot treated as Keep (note). The plan lists every move: `{kind: deposit | withdraw | relocate | spill | pocketTake |
pocketBack, slot, eid, stack docs (on / off), kind counts before (onB / offB, the 0.1 evidence, lines 1504-1572)}`.

### 7.2 The steps, and what a crash at each step leaves

The files: pool shards + loadouts file + ONE journal per profile (`requip/<pkey>/journal.json`). The engine saves the player every ~10 s
and on leave (0.1 docstring line 55); a server crash rolls the live inventory back to its last save.

| # | Step | Crash right after this step: state | Repair at next join (world thread, after `profile:busy` clears) |
|---|---|---|---|
| 1 | Gate + plan (memory only) | nothing written, nothing moved | nothing to do |
| 2 | **Journal** written (stage `moving`, the moves, `pre` = the touched entries + loadout marks as they were, pool rev R, profile epoch) - tmp + fsync + ATOMIC_MOVE + read back. Failure = refuse, nothing moves | journal says moving; live + pool both at R | evidence: no move reached the inventory -> pool restored from `pre` (= unchanged), journal deleted |
| 3 | **Live moves**, one at a time, each read back (0.1 `takeOff` / `put`, lines 1445-1465). Order: relocates, spills, deposits (X off), withdrawals (T on), pocket takes. A failed move = roll back the done moves in reverse in the same task (0.1 `rollback`, lines 1466-1480); journal back to its earlier steps; a failed rollback = journal `failed`, Requip SHUT for that profile until `/requipadmin repair` (0.1 `lock`) | some moves done in memory of the live inventory only; pool file still R | per move, live evidence: the stamped `eid` found anywhere in the live inventory = it is OUT; not found + journal says it went in = it is IN (rebuilt from the journal's stack doc); kind entries by kind counts (onB / offB); pocket moves by bag counts (`sacks:fn:count`) |
| 4 | Pool + loadouts updated in memory: deposited entries IN with their stack (stamp kept on the stored copy), withdrawn entries OUT (display copy only), rev R+1 | same as 3 | same as 3 |
| 5 | **Save**: every touched shard written (tmp + fsync + ATOMIC_MOVE, read back, count compared - 0.1 `save` lines 1076-1098), then `index.json` with the new shard revs. A failed save = memory back to `pre`, live moves rolled back, journal back (0.1 lines 1666-1677) | some shards at R+1, others at R; journal still `moving` | the journal is the commit record: every touched shard is rewritten from evidence (never trusted half-written); index rewritten |
| 6 | Journal stage `saved` (kept `journalKeepSeconds`, 30 s, from the newest step - the chain rule, lines 1170-1232) | files R+1; live may still be the OLD inventory if the engine had not saved the player yet | evidence: an item the file says is IN but is found in the live inventory (stamp / kind count) -> it never left: entry back to OUT, the stack copy dropped from the file; an item the file says is OUT but is not on you and the journal shows it came out in this step -> it never arrived: entry back to IN from the journal's stack doc. Result: **every item exists exactly once** |
| 7 | Pets / summon / abilities via the bridge (after items, 0.1 lines 2148-2168); a failed part is reported, items are not undone | items done | nothing (no items) |
| 8 | 1 s timer deletes the journal after 30 s (only while it still says `saved`; lines 1243-1255); graceful shutdown deletes them after the engine saved every player (lines 1256-1278) | - | - |

**Why no dupe:** the pool file holds a rebuildable stack only for IN entries, and an entry becomes IN only after its live removal was
read back (steps 3-5); any later doubt is resolved from the LIVE inventory (the stamp makes a unique item traceable anywhere in the
inventory, not only in its old slot - stronger than 0.1, which compared slot by slot). **Why no loss:** the journal (written before any
move) carries the full stack doc of every piece that moves in either direction, so a piece missing from both the live inventory and the
pool is rebuilt from it; a displaced or unplaceable stack becomes an **orphan** (0.1 lines 833-860: kept, retried at every load, shown
on the page as "Returned items - take out"), never deleted.

**Chained changes inside 30 s** (Equip, then Deposit, then Equip): each joins the same journal as a new step (0.1 chain rule); repair
walks newest first. **Deposit all, Take out, Forget, Pick** use the same journal (Pick / Forget only touch the loadouts file - one step,
no live evidence needed).

### 7.3 The shared item (one place at a time)

- An entry is IN or OUT, never both; a pick is only a pointer. Ten loadouts picking the same sword = ten pointers, one sword.
- Equip of loadout B while A is worn: a slot whose pick equals what is already there does not move; the shared sword in a different slot
  is relocated live -> live (no pool trip, no stamp change).
- Two picks of the same unique entry in ONE loadout (sword in hotbar 1 and 3) are refused at Pick time ("already in hotbar 1").
- A kind entry may be picked in several slots of one loadout (5 potions in 7, 5 in 8): the plan splits the count; short = the later slot
  gets less.

### 7.4 Pocket moves inside the transaction

`pocketTake` and `pocketBack` are bridge calls into SkyySacks (which saves its own pool through its saver). The journal records the
amount and the bag count before (`sacks:fn:count`). Repair: live slot holds the blocks and the bags show the debit -> happened; slot
empty / other item and the bag count is back -> not happened; unclear -> no action + WARN (blocks are a cheap, countable resource; we
never create blocks to "fix" a doubt). UNVERIFIED P6: SkyySacks' own crash window (its saver) vs ours.

## 8. Files and formats

### 8.1 Layout (per profile key, `Skyy_SkyyWardrobe/requip/<pkey>/`)

| File | Holds |
|---|---|
| `index.json` | `{format:2, rev, spaces:{armor:{shards:[{n, rev, count}]}, items:{...}}, migratedFrom01:<stamp or absent>}` |
| `armor-000.json` ... | up to `pool.shardSize` (100) entries each: `{eid, state:IN/OUT, stack:<slot doc> (IN only), show:{id, name, rarity, lv} (OUT), addedAt, kind?, count?}` |
| `items-000.json` ... | same for the Items space |
| `loadouts.json` | the loadout list: name, picks per slot (`{t:"e", eid}` / `{t:"k", eid, n}` / `{t:"p", id, n}` / `"keep"` / `"empty"`), pets, summon, ability snapshot, `lastWorn`, slot floor |
| `journal.json` | section 7 (format 3: 0.1's format 2 + move kinds) |
| `orphans.json` | stacks that could not be placed or rebuilt (0.1 rule) |

Stack doc = the 0.1 / SkyyVault / SkyyProfiles lossless slot format: explicit `id, qty, durability, maxDurability, quality,
overrideAnim, meta` + the engine `ItemStack.CODEC` encoding, EXTENDED JSON, codec decoded first, explicit fields as fallback
(`SkyyWardrobe/build_skyywardrobe_0.1.py` `WdCodec.slotDoc` line 714, `stackOf` line 733, `toJson` EXTENDED). Atomic write = 0.1
`atomicWrite` line 895 (tmp + fsync + ATOMIC_MOVE + REPLACE_EXISTING, 5 x 20 ms retries on a Windows FileSystemException). An unreadable /
newer-format file keeps that profile's Requip SHUT (0.1 lines 995-996), nothing written over it. `requip.log` = one line per DEPOSIT /
TAKE / EQUIP / PICK / FORGET / REPAIR / MIGRATE / ADMIN (ids + rarity, no metadata).

### 8.2 Profiles, death, Vault

| Case | Rule |
|---|---|
| **Profile switch** | pool + loadouts are per `pkey`; a switch closes the page (1 s ticker), Requip stays shut 30 s (`afterSwitchSeconds`, SkyyProfiles' rollback window); SkyyProfiles swaps the live inventory itself (contract rule 5), so a stamped sword worn on profile A travels with A's inventory snapshot. Repair runs whenever a key is active again (0.1 "no epoch rule", lines 1972-1978). |
| **Death** | pool contents are not in the inventory: never dropped. Worn / hotbar picks follow the server's death rule (island deaths keep items, `docs/answered/world.md`); a dropped stamped item = entry OUT "not with you" until picked back up. Every change refuses while dead; the death screen replaces the page (0.1 E5). |
| **SkyyVault** | the Vault is per PLAYER (`SkyyVault/build_skyyvault_0.1.5.py` line 441), shared by every profile. A stamped item put in the Vault and taken out on profile B: unknown `eid` for B's pool -> deposits as a NEW entry (restamped); A's entry stays "not with you" (Forget). Requip never reads the Vault. |
| **Bazaar / AH / trade / collections** | pooled items are invisible to them (not in the inventory). Out items are ordinary items; the stamp rides along and means nothing to other mods (P1 checks SkyyGear / AH compare by id + its own doc). |
| **SkyyProfiles crash recovery** | its 30 s marker can roll the live inventory back; our 30 s settle + journal keep window cover it (0.1 reasoning, docstring lines 39-41). |

## 9. Limits ("infinite" = paging + per-file caps)

Method (python3): 9 x 5 = 45 entries per page; pages = ceil(cap / 45). Size per entry is an estimate (~3 KB with a SkyyGear doc stored
twice - explicit + codec; UNVERIFIED P7).

| Row | Default | Range | Result |
|---|---|---|---|
| `space.armorCap` | 1000 entries | 50-10000 | 1000 -> 23 pages; ~2.9 MB |
| `space.itemsCap` | 1000 entries | 50-10000 | same |
| `pool.shardSize` (adv) | 100 entries / file | 25-500 | ~300 KB per shard; an Equip touches at most 13 entries -> usually 1-3 shards written |
| kind entry count | Long | - | taken out in max-stack pieces |
| worst case per player | 8 profiles x 2 spaces x 1000 x 3 KB | - | ~47 MB on disk (owner can lower the caps) |

At the cap: Deposit refused with "Armor space full (1000) - Take out or Forget something"; nothing else changes. Lowering a cap never
deletes: an over-cap space just refuses deposits (the "lowering never deletes" rule). Loadouts stay 18 max (gear.md 122).

## 10. Migration of 0.1 loadouts (one time per profile)

Runs lazily the first time a profile key is loaded by 0.2, on the world thread, journaled like a Deposit all:
1. Read `loadouts/<pkey>.json` (format 1) READ-ONLY; the file is never changed or deleted (kept for a rollback to 0.1, which would simply
   show the old loadouts again - see the floor note in section 13).
2. Every stored stack of every loadout (armor + hotbar, orphans included) -> a NEW pool entry in the right space; a 0.1 hotbar stack that
   Requip would refuse (a block, a bag) -> `orphans.json` as "Returned items" (take out from the page; never lost).
3. Each 0.1 loadout -> a Requip loadout with the same number, name, pets, summon, abilities; its picks point at the new entries in the
   same slots; slots it stored nothing in = Keep.
4. The 0.1 **equipped** loadout (its gear is on you, its stored spots empty): the loadout keeps name / pets / abilities with Keep picks;
   the page shows once: "Put what you wear into Requip and pick it for <name>?" [Yes] - one Deposit + Pick, never automatic.
5. `index.json` gets `migratedFrom01` (the run-once marker); one `requip.log` MIGRATE line per profile with counts.

**Settings:** 0.1 `config.properties` rows keep their keys and values (slots.*, swap.keepIds, combatSeconds, ...). `swap.hotbar` and
`swap.strict` lose their meaning (Keep / Empty picks replace them): left in the file, shown as "(0.1, unused)" in Server Setup. New rows
(section 11) are appended by the kit. No value is rewritten, so the migration rule (old defaults only, History snapshot, change-log line
with Undo, run-once marker, bytes + line endings kept) has nothing to change; if a later review wants a default changed, it follows that
rule exactly.

## 11. Server Setup (category **Requip**, through `tools/skyycfg.py`, times in seconds)

Kept from 0.1 (lines 400-423): `wardrobe.enabled`, `slots.free` 4, `slots.max` 18, `slots.byLevel` 6:10,10:20,14:30,18:40,
`swap.keepIds`, `swap.gapSeconds` 1 s, `combatSeconds` 10 s, `afterSwitchSeconds` 30 s, `journalKeepSeconds` 30 s, `nameMax` 16.
New:

| Row | Default | Notes |
|---|---|---|
| `space.armorCap` / `space.itemsCap` | 1000 / 1000 | section 9 |
| `pool.shardSize` (adv, restart) | 100 | entries per file |
| `deposit.hotbar` | off | Deposit all also empties the hotbar |
| `items.deny` | (empty) | ids never accepted (trailing `*` = prefix) |
| `items.allow` | (empty) | extra ids for the Items space when the classifier misses them |
| `pocket.enabled` | on | Pocket block picks |
| `pocket.target` | 0 | 0 = the item's max stack, else that amount |
| `pocket.backToBags` | on | leaving a loadout returns blocks to the bags (needs `sacks:fn:deposit`) |
| `stamp.enabled` (adv, danger) | on | off = unique items matched by kind only (reforge-while-out then makes a new entry) |

## 12. Build phases and engine probes

| Phase | What | Round |
|---|---|---|
| R0 | Probes P1-P10 in a probe jar (`/rqprobe`), one local test session | lean (probe) |
| R1 | **SkyyWardrobe 0.2 "Requip"**: spaces, entries, stamp, deposit / Deposit all / Take out / Forget, picks + picker page, Equip transaction (7.2), repair, migration (10), Server Setup, `/requip` (+ aliases `/wardrobe`, `/wd`, `/loadout`) and `/requipadmin` (+ `/wardrobeadmin`), harness: format round trip, crash at every step of 7.2 (the 0.1 `CRASH_AT` / `CRASH_AFTER_SAVE` hooks), migration fixtures from real 0.1 files | **Ultracode** |
| R2 | **SkyySacks 0.7.17**: `sacks:fn:deposit` + refill of reserved empty slots (`requip:pocket:<uuid>`); SkyyWardrobe 0.2.1 Pocket block picks | Full round (two mods, items) |
| R3 | Looks (`research/cloud/Wardrobe-Spec.md` section 4) on IN armor entries / a whole loadout's armor picks; needs `gear:base` | Full round (coins + items) |
| R4 | Polish: sort / search, Stats-page line, a hotkey-ish `/requip <n>` | lean |

Engine probes (all **UNVERIFIED**):

| # | Check | Fallback |
|---|---|---|
| P1 | A foreign metadata key (`SkyyRequip`) survives: moving between sections, SkyyGear reforge / re-identify / level-up / repair, The Armory alteration, durability loss, death drop + pick up, Vault round trip | kind match only (`stamp.enabled` off) |
| P2 | Classifying an item asset: armor slot, Weapon, Tool, consumable interaction, block / Magic Bag home type | id prefixes + `items.allow` / `items.deny` |
| P3 | A custom page ItemGrid of the player's inventory bound to SlotClicking; does the event carry shift? | plain click = deposit |
| P4 | A server API to save one player's inventory at once after a swap (shortens the 30 s window) | journal keep window as in 0.1 |
| P5 | No autosave / tick interleaves one world-thread task (0.1 assumption) | per-move journal evidence already covers it |
| P6 | `sacks:fn:take/deposit` from our world-thread task; SkyySacks saver timing vs our journal | pocket moves left to SkyySacks' own refill |
| P7 | Real size of a stack doc with a full SkyyGear document | adjust `pool.shardSize` / caps |
| P8 | A page with 45 pool icons + 13 slots + the inventory mirror (~100 ItemGridSlots) renders without lag | 27 per page |
| P9 | `removeItemStackFromSlot` / `setItemStackForSlot` on storage + backpack sections from a page click (0.1 proved armor + hotbar) | deposit from hotbar only |
| P10 | Death drop rules outside islands (what drops from hotbar / armor) | none needed (pool is safe either way) |

## 13. Cross-mod summary

| Mod | Link |
|---|---|
| SkyyProfiles | `pkey`, `profile:busy`, `profile:epoch` (0.1 unchanged) |
| SkyySacks | `sacks:fn:take/put/count` (live), NEW `sacks:fn:deposit` + reserved-slot refill reading `requip:pocket:<uuid>` (0.7.17) |
| SkyyPets / SkyyClasses | 0.1 bridge unchanged |
| SkyyGear | tooltip lines `gear:fn:stats`; stamp must survive its rewrites (P1); unidentified refused |
| SkyyMenu | tile renamed "Requip" (Q1), `wardrobe:fn:open` kept (+ `requip:fn:open` alias) |
| SkyyVault / SkyyAccessories | none (inventory is the only path between them) |

Rollback floor (`tools/deploy_set.py`): once 0.2 has run, never roll SkyyWardrobe below 0.2 - 0.1 cannot read `requip/` and would
show the pre-migration loadouts whose stacks were moved into the pool (items invisible, not lost; reinstall 0.2 to see them).

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Name it "Requip" in game (menu tile, page title, `/requip`), with `/wardrobe`, `/wd`, `/loadout` still working? | [Yes - mod stays SkyyWardrobe so data folders never move] |
| 2 | A slot your loadout does not pick: leave what you wear (Keep), or put it away? | [Keep, like the LOCKED partial-set rule; each slot has an "Empty" choice] |
| 3 | Space size per profile? | [1000 armor + 1000 items, editable up to 10000] |
| 4 | What Requip refuses: blocks / materials (bags), unidentified, bags, accessories? | [Refuse all four, as in 3.2] |
| 5 | Deposit all: include the hotbar? | [No - storage + backpack only; Server Setup row] |
| 6 | Block slots: how many blocks to keep in the slot? | [A full stack, refilled from your bags] |
| 7 | Picked item not with you at Equip (in a chest, dropped): skip that slot? | [Skip + chat note; the card says NOT WITH YOU] |
| 8 | 0.1 loadouts: move their gear into the pool automatically on update? | [Yes, once; what you wear now is only moved when you click Yes] |
| 9 | Potions / food in loadouts: how many come out? | [One full stack per picked slot, editable per pick] |
| 10 | Should items in the pool count anywhere (collections, net worth later)? | [No for now] |

**Skyy's answers (2026-10-11, word for word, given to the cloud session):** "1. an /requip  or /rq      2. yes    3. could you rephrase that? (what i picture is like the mining bags. but for gear.  (you can toggle weather or not it auto pulls from your inventory.)  and anything in there, you can select when creating a loadout. when you equip a a saved loadout, it places whatever your wearing in the storage bag, and replaces it with the new load out."
- Q1: commands are `/requip` and `/rq` (the in-game name is Requip; whether the old `/wardrobe` / `/wd` / `/loadout` stay as aliases is still open - default: keep them as hidden aliases for one version).
- Q2: YES - an unpicked slot keeps what you wear (each slot also offers "Empty").
- The picture Skyy describes matches sections 3-7 (one gear bag per profile, loadouts pick from it, Equip puts what you wear into the bag
  and takes the loadout out). NEW from it: the auto-pull toggle - section 4.1.
- Q8 (0.1 migration) was asked again in plainer words; still open, default unchanged.
- Q8 answered 2026-10-11 (Skyy, word for word: "question 3 yes", to the plain-words version "should gear saved inside the old Wardrobe
  loadouts move into the new gear bag automatically on update, once; worn gear only moves when you click Yes?"): YES - section 10 as written.
- Old command aliases (2026-10-11, Skyy, word for word: "im the only player. no need to worry about players. i understand whats going on"):
  no aliases - only `/requip` and `/rq`; `/wardrobe`, `/wd`, `/loadout` are removed (no transition version needed).

## For the local session

- Probes P1-P10 (section 12) before R1; P1 (the stamp survives SkyyGear rewrites) and P3 (inventory grid clicks) decide the design;
  P2 decides the classifier.
- Measure a real stack doc size (P7) from the live 0.1 files in a scratch COPY (`tools/dev/scratch/requip/`), never UserData.
- Collect a few real `Skyy_SkyyWardrobe/loadouts/<pkey>.json` files (scratch copies) as migration fixtures for the R1 harness.
- SkyySacks 0.7.17 needs a patch script (`tools/sacks_0_7_17_patch.py`) for `sacks:fn:deposit` + the reserved-slot refill.
- Add the rollback floor note for SkyyWardrobe 0.2 to `tools/deploy_set.py` when R1 is pinned.
- Line numbers cited from `SkyyWardrobe/build_skyywardrobe_0.1.py` and `SkyySacks/build_skyysacks_0.7.16.py` are as of 2026-10-11.
