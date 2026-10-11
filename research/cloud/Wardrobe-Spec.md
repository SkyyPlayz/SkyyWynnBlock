# Wardrobe - design spec (SkyBlock-style armor-set swaps from the SkyWynn Menu)

*Cloud draft 2026-10-08. Spec only: no code, nothing built. Owner: Skyy (they/them). Model: Fable (spec synthesis).*

## 0. Decisions this spec follows

- `docs/answered/gear.md` LOCKED 2026-10-08 (WARDROBE): "id like to swap from the menu. because i want a hypixle sky block like wardrobe
  you can place your armor sets in to quickly swap between them. (id like to be able to edit the look of the entire set from in there.)"
  -> our OWN Wardrobe page from the SkyWynn Menu; slots hold a full set (Head / Chest / Hands / Legs); one click swaps; the LOOK of a
  whole set changes from inside the wardrobe using the look families of `research/Recolor-Plan.md`. This answers Recolor-Plan Q1
  (not only The Armory's table) and Q8 (a swap cost of our own).
- `docs/answered/gear.md` LOCKED 2026-10-08 (ARMOR SPLIT): mining armor = vanilla metal sets, combat armor = The Armory pool, farming +
  foraging = our own sets. LOCKED 2026-10-08 (FORAGING per tree): every tree type of a tier is its own look, same stats; miners get
  swappable looks too.
- `docs/answered/gear.md` LOCKED 2026-10-05: ARMOR TYPES (Heavy / Light / Cloth) - a set's type bonus comes from the pieces worn, so
  a wardrobe swap simply changes what is worn; nothing in this spec adds a type rule.
- `research/Recolor-Plan.md` 4.1-4.3: a look family = one slot of one set, identical stats + MaxDurability, ids
  `Skyy_Look_<BaseId>_<Look>`, SkyyGear `gear:base` maps a look id to its base id, The Armory's Iron recolours are already a family.
- `tools/PROFILES-CONTRACT.md`: per-profile data under `pkey`, respect `profile:busy`, one key per operation.
- `HANDOFF.md` 2-3: inline pages only, vanilla look (`tools/skyyui.py`), no metadata stacks in an ItemGridSlot, command rules.
- `PROJECT-RULES.md` 4: items that could be lost or duplicated + saved data + a new system = **Ultracode** round.
- Not re-decided here: Alteration Table facts (Recolor-Plan 1), the foraging tiers F1-F5 (`research/Gathering-Progression-Spec.md` 2.2).

## 1. Plain words (for Skyy)

- A **Wardrobe** page in the SkyWynn Menu (tile + `/wardrobe`). It has numbered slots; each slot holds one armor SET (helmet, chest,
  hands, legs) and a name. Click **Equip** on a slot: what you wear goes into that slot and the slot's set goes onto you. Nothing
  ever touches your hotbar or backpack during a swap, so it is fast and safe.
- You fill a slot with **Store** (your worn set moves in) or by putting single pieces into it from your inventory. A slot can be
  partial (just a helmet is fine).
- **Edit look**: pick a slot, press **Looks**, choose a colour / design, and every piece in that set that HAS that look changes to it
  at once. Rarity, level, rolls, reforge and durability all stay. Pieces without that look keep theirs. It costs something small
  (default: one Alteration Kit charge style cost in coins, editable in Server Setup).
- Slots: 4 free at the start (SkyBlock's number today), more unlocked by Overall Level (default) up to 18, admins can set more.
- Everything is per profile, saved like the Vault (lossless, atomic files, crash-safe).

## 2. Hypixel SkyBlock's Wardrobe (what we copy, what we change)

### 2.1 Facts (web research 2026-10-08, Sonnet agent; the official wiki.hypixel.net closed in July 2026, the Fandom wiki was not
readable - the main source is the community wiki, forum posts where named)

| Topic | Fact | Source |
|---|---|---|
| Size | 2 pages ("Wardrobe (1/2)", "(2/2)"), 18 slots at the top rank; 9 per page is implied, not stated | https://hypixelskyblock.minecraft.wiki/w/Wardrobe |
| Unlocks (today) | Default 4, VIP 6, VIP+ 10, MVP 14, MVP+ 18 slots; plus up to 9 Community Center slots (slot 1 free, slot 2 250 Gems, 3-9 500 Gems each, 6 days per upgrade) | same page; https://hypixelskyblock.minecraft.wiki/w/Loadouts |
| Unlocks (old) | Default 2, VIP 5, VIP+ 9, MVP 13, MVP+ 18 - the 2026-07-08 (0.26) patch added 2 free slots for Default and 1 for VIP / VIP+ / MVP | wiki History; https://hypixel.net/threads/june-24-skyblock-resource-pack-loadouts-and-healing-revamp-changes.6107861/ |
| Where | SkyBlock Menu (shown from SkyBlock Level 5), `/wardrobe [page]`, `/wd`; since Loadouts (July 2026) the menu entry is `/loadout` | wiki page; https://hypixel.net/threads/easier-wardrobe-swapping.5742047/ |
| Hotkeys | none built in; players bind a key to the command | https://hypixel.net/threads/make-a-key-to-armor-swap-from-wardrobe-without-opening-it.3389033/ |
| Swapping | full sets or mixed single pieces can be stored; the worn set cannot be edited from the wardrobe; a swap = open + up to two clicks. Whether the worn set lands in the slot you equipped from: UNVERIFIED (the common memory of the UI says yes - the slot shows your old set after the click; treated as the model here) | wiki page; forum 5742047 |
| Partial sets | mixed pieces can be stored (so a slot may be partial); Loadouts "keep what you already wear" for an unselected part; the plain wardrobe's rule for a missing piece: UNVERIFIED | wiki Wardrobe + Loadouts; forum 6107861 |
| Cooldown | was 30 s; the 2026-06-24 alpha / 0.26 patch set the Wardrobe + Equipment Wardrobe cooldown to 0 (Loadouts keep one); staff want to move away from mid-combat swaps; no documented dungeon / Kuudra block; one forum claim of "cannot open in combat" (unconfirmed) | forum 6107861; https://hypixel.net/threads/look-we-just-need-a-way-to-quickly-change-set-ups.5533866/ |
| Display | stained-glass panes, dyes, arrows, barriers per slot; disabled icon = undyed leather armor; no player preview and no set names documented | wiki page |
| Rank downgrade | armor in newly locked slots goes to the Stash (nothing deleted) | wiki page |
| Scope | armor only; Equipment (necklace, cloak, belt, gloves) has its own Equipment Wardrobe (`/eq`, July 2026: Default 2 ... MVP+ 9); pets never | https://hypixelskyblock.minecraft.wiki/w/Equipment_Wardrobe |
| Bugs | July 2026 "Wardrobe wipe bug" after swaps around the Loadouts backend change (sets deleted, no staff reply); a secondhand alpha dupe claim; a player proposal of a ~1 s swap cooldown against dupes | https://hypixel.net/threads/wardrobe-wipe-bug.6118104/; https://hypixel.net/threads/a-way-for-wardrobe-to-have-equipments.5596913/ |

Lesson for us: the one documented disaster is LOSS after a backend change, not a dupe - hence the journal + read-back + "nothing is ever
deleted" rules in section 5.

### 2.2 What we take and what we change

| SkyBlock | SkyWynn | Why |
|---|---|---|
| Opened from the SkyBlock Menu + `/wardrobe` | SkyWynn Menu tile + `/wardrobe` (alias `/wd`) | Skyy: "swap from the menu" |
| 9 slots per page, 2 pages (18) | 9 slots per page, up to 2 pages (18) | same feel; first 4 free (SkyBlock today gives 4; it gave 2 before July 2026), the rest unlocked by Overall Level (SkyBlock: ranks + gems - we have no paid ranks for gameplay) |
| Equip swaps worn <-> slot | same, one world-thread task | one click, no inventory space needed |
| Unequip = armor back to the slot it came from | **Store** = worn set into an empty slot; **Take out** = a piece from a slot to the inventory | plainer words, and Take out covers the SkyBlock "lift the piece out" case |
| No set names | Names (rename field, 16 chars) + auto name "Set 3" | Skyy's "edit the look of the entire set" needs a place to see the set as a thing |
| No look editing | **Looks** button per slot (section 4) | the whole point of Skyy's request |
| Cooldown 0 since July 2026 (was 30 s); no documented combat block | 1 s per-player swap gap + refused while dead / in combat (10 s like Profiles) / `profile:busy` | dupe and abuse safety, section 5 |

## 3. The page

### 3.1 Where it opens

- SkyWynn Menu: a **Wardrobe** tile (icon = our own item `Skyy_Menu_Icon_Wardrobe`, the SkyyMenu 0.3.11 own-icon pattern; until the art
  lands: the vanilla Armor Bench icon). Greyed with hover text "Needs SkyyWardrobe" when the mod is absent (the Identify-tile pattern).
- Commands: `/wardrobe` (aliases `/wd`, `/wardrobes`), `/wardrobe <n>` = equip slot n at once (the SkyBlock hotkey habit), `/wardrobe
  store <n>`, `/wardrobe name <n> <name>`. Player commands with `setPermissionGroups(hytale:Adventurer)` on root AND every variant
  (HANDOFF 3). Admin: `/wardrobeadmin slots <player> <n>`, `/wardrobeadmin look <player> <slot> <look>`, `/wardrobeadmin reload`,
  `/wardrobeadmin config` (permission `skyywardrobe.admin`).
- Vanilla look through `tools/skyyui.py` + `research/Vanilla-UI-Style-Guide.md` 14 (card page recipe). Inline page, ids without
  underscores, `#SkyyWd...` prefix.

### 3.2 Layout (about 920 x 760; the kit's `assert_page_size`)

```
+--------------------------------------------------------------------------------+
| WARDROBE - profile "Fox"                 Slots 6 / 18   Page 1 of 2    [Close]  |
+--------------------------------------------------------------------------------+
| WEARING:  [H] [C] [Ha] [L]   Iron set, Light, Lv 18                            |
|           [Store into slot...]                                                  |
+--------------------------------------------------------------------------------+
| 1 "Mining"        2 "Forest"        3 "Set 3"        | 4 (locked)   5 (locked)  |
| [H][C][Ha][L]     [H][C][ ][L]      [ ][ ][ ][ ]     | Overall Lv 10 Overall 15 |
| EQUIPPED          Equip  Looks      Equip  Looks     |                          |
| Looks  Take out   Take out          Take out         |                          |
| ...                                                                             |
+--------------------------------------------------------------------------------+
| Swap cost: 0 coins   Look change: 500 coins   [< Page] [Page >]                 |
+--------------------------------------------------------------------------------+
```

- A slot card = name (click = rename text field, 16 chars, kit `text_field`), four `ItemGridSlot`s drawn **metadata-free** (`new
  ItemStack(id, 1)`, HANDOFF 2) with the rarity colour and "Lv N" as text under each icon (the SkyySacks bag page way), and buttons.
  Hover text per piece = SkyyGear's own tooltip lines through `gear:fn:stats` / the item's display lines (no page update from hover).
- The grid is **display only** (`AreItemsDraggable: false`): no client drag into or out of the page. Every move is a button, so the
  server owns every transfer (the SkyyVault 0.1.5 lesson: the client lifts items in container windows by itself and tells the
  server nothing).
- The **EQUIPPED** marker shows on the slot whose set is worn (section 6.2 "worn-from" link); its Equip button is hidden.
- Locked cards show the unlock rule ("Overall Lv 10" / "500 coins" / "admin") and, for a coin unlock, a **Buy** button -> the kit's
  one-shot confirm (SkyyVault buy rules: price shown is the price charged, one at a time, 1.5 s refuse window).

### 3.3 Buttons and what they do (all on the player's world thread, one task each)

| Button | Does | Refused when |
|---|---|---|
| **Equip** (slot n) | For each of the 4 armor slots: take the worn piece out, put the stored piece in, put the worn piece into the wardrobe slot. One task, verified slot by slot (section 5.2). Partial set: an empty wardrobe piece leaves that worn piece ON (SkyBlock keeps it; see Q3). | dead, in combat, `profile:busy`, settle window, another wardrobe task < 1 s ago, slot empty, page stale (section 5.3) |
| **Store** (header, "into slot...") | Pick an EMPTY slot (or an empty piece spot in a partial slot): the worn pieces move in. | no empty slot, nothing worn, same refusals |
| **Take out** (slot n) | Opens the piece picker (4 small buttons H / C / Ha / L): the piece goes to storage -> hotbar -> backpack (`addItemStack`, remainder respected); if nothing fits: refused with "Inventory full", the piece stays. Never dropped on the ground. | inventory full for that piece, same refusals |
| **Put in** (slot n, only when a piece spot is empty) | The page lists armor pieces in your inventory for that spot (id + rarity + Lv, buttons); one click moves it in. SkyyGear "unidentified" pieces and mystery boxes are not listed (Q6). | same refusals |
| **Looks** (slot n) | Section 4. | slot empty, no piece has any family, cost not payable |
| **Rename** | Name field, 16 chars, letters / digits / space; sanitised like the Sacks page. | - |
| **Page < >** | 9 cards per page. | - |

Chat feedback is one short line per action ("Equipped Forest.", "Stored into slot 3.", "Take out: inventory full.").

### 3.4 Partial sets

- A slot may hold 1-4 pieces. Equip swaps **only the spots that are filled** in the wardrobe slot; the other worn pieces stay on
  (SkyBlock behaviour, Q3 default). Alternative (Q3): "strict swap" - the worn piece of an empty spot moves into that spot, so after
  Equip you wear exactly the set (worn pieces never get stranded). Default = SkyBlock's (keep), Server Setup row `swap.strict`.
- A worn spot that is empty while the wardrobe spot is full: the stored piece goes on, nothing comes back (the spot becomes empty).
- Store into a partial slot fills only the empty spots; worn pieces for filled spots stay on (the chat line says which).

## 4. Edit the LOOK of a whole set

### 4.1 Data: look families (from `research/Recolor-Plan.md`, nothing new)

- A **family** = one slot of one set: all ids with identical stats + MaxDurability, e.g. `Resource_Skyy_Copper_Chest` =
  { `Armor_Copper_Chest` (base), `Skyy_Look_Armor_Copper_Chest_Red`, ..._Black, ... }. Families come from the SAME two sources the
  Recolor-Plan's option (b) names: (1) our generated family table (built into the armor jar at build time, published on the bridge as
  `look:families` = `Map<String familyId, String[] memberIds>` + `look:base` = `Map<String id, String baseId>`); (2) every
  `ArmoryAlteration` recipe in the asset map (The Armory's Iron recolours and their own sets), scanned once lazily like their index.
  Without The Armory source (2) is empty: their looks are simply not offered (section 7.3).
- A **look name** = the suffix after the base id (`Red`, `Birch`, `Purple_Fab`); the Armory's names are their id suffix (`Black`,
  `Blue_Alt`). The page shows the look as a human name (language line) + the recoloured icon (the member id's own icon, metadata-free).
- A **set-wide look** = a look name that at least one piece of the set can take. The page lists the union of look names over the
  4 pieces; next to each: "4 / 4 pieces" or "3 / 4 (hands keep theirs)".

### 4.2 The Looks page (sub-page of the slot card)

```
| LOOKS - slot 2 "Forest" (Foraging F1)                                  [Back] |
| Pieces: [H Oak] [C Oak] [Ha Birch] [L Oak]                                     |
| Pick a look for the whole set:                                                 |
|  (icon) Oak     4/4   [Apply]      (icon) Birch  4/4  [Apply]                  |
|  (icon) Beech   4/4   [Apply]      (icon) Ash    3/4  [Apply]  (no hands)      |
|  ...                                                                           |
| Cost: 500 coins per set (any number of pieces)     Purse: 12,400               |
```

- Only the stored set is edited (never the worn one) - keep the swap and the look change as two separate transactions. Want to
  recolour what you wear? Store, Looks, Equip (3 clicks). Q4 asks whether the worn set should get a Looks button too.
- **Apply**: pay first (`coins:fn:take`, must return TRUE), then for each piece with that look in its family: new stack =
  `new ItemStack(newId, 1, durability scaled by fraction (Recolor-Plan 1 "Durability"), newMax, metadata.clone())`, written into
  the wardrobe slot's array, saved atomically, read back. A failed save = refund the exact coins and keep the old array (SkyyVault buy
  pattern). Pieces without that look are untouched. Chat: "Forest is now Birch (3 of 4 pieces)."
- **Metadata**: the whole BsonDocument is cloned, so SkyyGear's document (rarity, level, modifiers, `lvl0`, `spd`, reforge, set
  field) survives exactly. SkyyGear keys stats by id -> `gear:base` (Recolor-Plan 4.3, built in Recolor P1) makes the new id's band /
  stat lines the base piece's. **No craft event is fired**, so no roll, no Smithing XP, no below-band refusal (Recolor-Plan 3 b).
- **Preview** (UNVERIFIED, section 9): a player-model preview inside a custom page is not a known client element. The page shows the
  4 recoloured ICONS of the target look instead (the member id's icon), which is what The Armory's page does too. If a later probe
  finds a "paper doll" element, add it; nothing in the data model changes.
- **Cost** (Q5): Server Setup `look.cost` coins per set change (default 500), `look.kit` = 0 / 1 Alteration Kit charge instead of
  coins when The Armory is present and `look.useKit=true` (default false - our economy uses coins; Recolor-Plan Q8). Creative mode and
  `skyywardrobe.free` permission skip the cost.

### 4.3 Rules the family data must obey (checked at build + at load)

- Every member of a family has the same stats + MaxDurability as the base (Recolor-Plan 4.1); a family that mixes durability is
  logged once and its odd members are skipped (never a durability-scaling loss).
- A look change never crosses tiers or slots: the target id must be in the SAME family as the current id. The page can only offer
  family members, and the Apply handler re-checks it.
- Stack size 1 always (armor never stacks).

## 5. Data and dupe-proofing

### 5.1 Files (per PROFILE, SkyyVault's lossless format)

- `Skyy_SkyyWardrobe/wardrobes/<pkey>.json`: `{format:1, mod, uuid, key, savedAt, rev, slotsUnlocked, slots:[{n, name, pieces:{Head:{...},
  Chest:{...}, Hands:{...}, Legs:{...}}, wornFrom:bool}]}`. Each piece = the SkyyProfiles 0.1 slot format: explicit `id, qty,
  durability, maxDurability, quality, overrideAnim, meta` (BsonDocument) PLUS the engine `ItemStack.CODEC` encoding (decoded first,
  explicit fields as fallback), EXTENDED JSON. Undecodable stacks go to `orphans` and are retried at every load, never dropped.
- Writes: tmp + fsync + `ATOMIC_MOVE` (5 x 20 ms retries on a Windows `FileSystemException`), read back and the piece count compared;
  ordered by `rev` under a per-wardrobe IO lock (an older snapshot can never overwrite a newer file). A file that exists but cannot be
  read keeps that wardrobe SHUT (page says "Wardrobe unavailable - ask an admin", nothing written over it, warned once a minute).
- `wardrobe.log`: one line per EQUIP / STORE / TAKE / PUT / LOOK / UNLOCK / REFUND / ROLLBACK (admin audit; ids + rarity, no metadata).
- `config.properties` through `tools/skyycfg.py` (section 8); `config-changes.log`, `config-history/` as every kit adopter.

### 5.2 The swap transaction (write-ahead, like a SkyyProfiles switch)

All on the player's world thread, ONE uninterrupted task, per-player `BUSY` guard (a second click while busy is refused):

1. Refuse checks (section 3.3): dead, in combat (`DamageDataComponent` within 10 s), `profile:busy:<uuid>` present, settle window
   (30 s after a `profile:epoch` change - SkyyVault's `afterSwitchSeconds` reasoning: SkyyProfiles keeps its switch marker 30 s and a
   crash inside it rolls the live inventory back, which would duplicate anything we moved), another wardrobe task < 1 s ago, page `rev`
   stale.
2. Resolve `pkey` ONCE. Read the slot's pieces from memory (= the file).
3. **Journal first**: write `wardrobes/<pkey>.journal` = `{op:"equip", slot:n, rev, at, want:[per spot: wardrobe piece id + worn piece id]}`
   atomically. Then the 4-spot move:
   - for each spot H / C / Ha / L: `worn = armor.removeItemStackFromSlot(spot, 1)` (must `succeeded()`, remainder 0; else stop);
     `armor.setItemStackForSlot(spot, stored, false)` then READ the slot back (id + metadata equal, the ProfInv way); on success put
     `worn` into the array spot.
   - any failure mid-way = **rollback in the same task**: put back every spot already moved (array piece <-> armor piece), verify;
     if even that fails the journal becomes `stage=failed`, the wardrobe is SHUT for this profile until an admin runs
     `/wardrobeadmin repair <player>` (nothing deleted; the journal lists what should be where), the player is told.
4. Write the file (rev+1) synchronously, read back. Delete the journal. Log one line. Rebuild the page.

**Crash in the middle.** At the next join of that player (the engine saves the player on world leave; a hard crash can lose up to 10
s of inventory), SkyyWardrobe finds the journal: a `stage=saved` journal means the live armor may or may not hold the swapped set.
Repair rule (runs on the player's world thread after `profile:busy` clears, like the Profiles recovery): for each spot compare the
LIVE armor piece against the journal's two candidates by id + metadata: live == stored-candidate -> the swap happened there, the
array must hold the worn-candidate; live == worn-candidate -> no swap there, the array must hold the stored-candidate; neither ->
leave the array as the file says and WARN (admin). The result is always "each piece exists exactly once": the piece that is on the
player is not in the file and the other is. A journal with no file change (crash before step 4) and a live armor still matching
the pre-swap state = nothing to do, journal deleted.

**Why no item ever doubles**: a piece is in the live armor OR in the array, never both: the array only receives a piece whose
`removeItemStackFromSlot` succeeded in this task, and the file is only written after the live side was read back. The window is one
world-thread task, so no tick, event, death or sweep can interleave (SkyySacks / SkyyAccessories inventory code also runs there).

### 5.3 Other dupe surfaces and their rule

| Surface | Rule |
|---|---|
| Two clicks in one tick / double click | Per-player `BUSY` flag set at task start, cleared at the end; the page carries `rev` and every click names the rev it saw - a click with an old rev is refused and the page rebuilt (the SkyyVault "page-bound" rule). |
| Death with the page open | The page closes on `DeathComponent` (1 s ticker -> world-thread close task, the SkyyVault VCloseTask pattern); Equip / Store refuse while dead. Vanilla keep-inventory rules apply to worn armor, never to wardrobe contents (they are not in the inventory). Island deaths keep items (world.md). |
| Profile switch | The wardrobe is read through `pkey` at task start; an epoch change closes the open page (ticker) and starts the 30 s settle; the file for the OLD key is untouched by anything that runs after the switch. SkyyProfiles snapshots the Armor section itself (0.1.6 step 2), so a stored set stays with its profile and the worn set with its profile. |
| Full inventory | Only **Take out** needs space: `addItemStack` into storage -> hotbar -> backpack; on any remainder the piece STAYS in the wardrobe (nothing dropped, the SkyyAccessories unequip rule). Equip / Store never need space. |
| Page open across a world change | Profiles' CloseTask pattern (SkyyMenu 0.3.5): the page is closed by the ticker when the player's world changes; a click from a page that is no longer on screen is refused (stale rev). |
| Admin give / creative | `/wardrobeadmin` commands run the same transaction; creative skips costs only. |
| Durability switch OFF (gear.md LOCKED 2026-09-30) | Pieces keep whatever durability they have; a look change scales by fraction (1.0 stays 1.0). |
| Unidentified / mystery box | Never storable (Q6): the piece picker skips them, Store skips worn unidentified pieces (SkyyGear refuses to wear them anyway) with a chat note. |
| The Armory's own alteration | A piece swapped at THEIR table while stored: impossible (it is not in the inventory). While worn: fine, the next Store stores the new id. |
| Rollback floor | Item data on disk = `deploy_set.py` rollback floor for SkyyWardrobe 0.1 (a rollback to "absent" would strand files: the floor note says "stored sets stay in `wardrobes/`, reinstall to get them"). |
| Shutdown | Open pages made inert; every dirty wardrobe written synchronously before the saver stops (SkyyVault shutdown). |

### 5.4 Threads

Clicks, commands and the transaction: the player's world thread. A 1 s ticker (shared scheduler) only reads the bridge / session
table and hands closes to world-thread tasks. File writes: synchronous on the world thread for the transaction (it must know the
result, like Vault buys), a daemon saver for renames / unlock bookkeeping. No ECS systems needed.

## 6. Slots and unlocks

### 6.1 Numbers (Server Setup, section 8)

| Row | Default | Notes |
|---|---|---|
| `slots.free` | 4 | SkyBlock gives 4 free slots today (2 before July 2026) |
| `slots.max` | 18 | 2 pages of 9 (SkyBlock's rank maximum) |
| `slots.byLevel` (table) | `6:10, 10:20, 14:30, 18:40` | slot count : Overall Level (`skill:overall:<uuid>`, SkyySkills 0.4.6+) - a level unlocks the slots up to that count (mirrors SkyBlock's 4 / 6 / 10 / 14 / 18 ladder) |
| `slots.coinPrice` (table) | empty | optional: slot n : coins (Bank/Vault-style buy); empty = level only |
| `slots.perRank` | off | later: SkyyRanks perks ("rank perks later", R9) |

Unlocks are additive: a slot is open when ANY rule opens it; admin `slots <player> <n>` sets a floor stored in the file
(`slotsUnlocked`). Lowering a setting never deletes a stored set: a slot above the new cap shows as **locked but full** - Take out
and Equip still work, Store / Put in do not (the SkyyProfiles "lowering never deletes" rule).

### 6.2 Worn-from link

A slot remembers `wornFrom=true` when its set was just equipped (so the card says EQUIPPED and hides Equip). It is a display hint
only: the next Equip of ANY slot clears it; wearing a different piece manually does not break anything - the next Store asks for a
slot like always. (SkyBlock shows the equipped slot the same way.)

## 7. Cross-mod

| Mod | Link | Without it |
|---|---|---|
| **SkyyGear** | Rolls live in the item metadata -> stored as is. Look change needs `gear:base` (Recolor P1) so the new id keeps band / lines; the page reads tooltip lines via `gear:fn:stats` (or the item's display lines). SkyyGear's `GearFxInvSys` (armor `InventoryChangeEvent`) re-applies worn stats after every Equip by itself - no call needed; UNVERIFIED that `setItemStackForSlot` fires it (section 9). Unidentified pieces never stored. | pieces store fine (plain vanilla stacks); Looks still works (families come from the armor jar + The Armory), the swapped id just shows vanilla stats |
| **SkyyArmory / the armor jar** | Publishes `look:families` + `look:base` (bridge, plain java.lang) from the generated family table. | only The Armory's recipe-derived families remain |
| **The Armory** | Its `ArmoryAlteration` recipes feed the family scan (Iron recolours + its own sets). Its kit as an optional cost. | its looks are unavailable; their ids already stored keep working as stored stacks (the item asset must still exist - a missing asset = orphan, retried) |
| **SkyyProfiles** | `pkey`, `profile:busy`, epoch -> close + settle 30 s. | pkey = uuid = profile 1 |
| **SkyyMenu** | Tile + Server Setup pages via `tools/skyycfg.py`; `/wardrobe` listed on the Mods tile. | commands only |
| **SkyyCoins** | `coins:fn:take` / `coins:fn:add` for look changes and coin unlocks; refund on a failed write. | look changes free, coin unlocks hidden |
| **SkyySkills** | `skill:overall:<uuid>` for level unlocks (the Overall Level of `research/Overall-Level-Spec.md`). | only free + admin slots |
| **SkyyStats page** (`research/cloud/Stats-Page-Spec.md`) | Nothing to publish: the worn set is what counts. Nice-to-have: a "Wardrobe" line "6 / 18 slots, equipped: Forest" through the same hover text source as Your Profile. | - |
| **SkyyAccessories** | Not involved (accessories are not armor). SkyBlock's wardrobe stores armor only; equipment slots (necklace etc.) are separate there too. | - |
| **SkyyRanks** | later: rank slot perks row. | - |
| **SkyyClasses** | nothing: armor is not class-gated (soft types, LOCKED 2026-10-05). | - |

## 8. Server Setup (through `tools/skyycfg.py`, `tools/CONFIG-CONTRACT.md`)

Category **Wardrobe**: `enabled` (on), `slots.free` 2, `slots.max` 18 (1-18), `slots.byLevel` table, `slots.coinPrice` table, `swap.strict`
off, `swap.gapSeconds` 1, `combatSeconds` 10, `afterSwitchSeconds` 30, `look.cost` 500, `look.useKit` off, `look.kitId`
`Alteration_Kit`, `nameMax` 16, `saveDelayMillis` 1000 (renames). Times shown in seconds. Admin edits reload without restart
(`reload:` rows); hand-edited table lines are checked (kit 1.1).

## 9. Engine checks needed (all UNVERIFIED - for the local session / the probe step)

| # | Check | Why it matters | Fallback |
|---|---|---|---|
| E1 | `InventoryComponent.getArmor()` accepts `removeItemStackFromSlot(spot, 1)` + `setItemStackForSlot(spot, stack, false)` from a page click task and the client re-renders the worn model at once (SkyyProfiles 0.1.6 does exactly this for the Armor section during a switch - VERIFIED there, but inside a world-change flow) | the swap itself | `addItemStack` into the armor container after a clear |
| E2 | SkyyGear's armor `InventoryChangeEvent` system fires on `setItemStackForSlot` (not only on player-driven moves) | worn Health / resistance after a swap | call `gear:fn:resync` (new bridge fn) after the task |
| E3 | A custom page can show a player / armor-stand preview (any client element like `ItemIcon` for entities) | the Looks preview | icons of the target look only (the plan's default) |
| E4 | `ItemStack.CODEC` round trip for The Armory's ids whose model path lives in their jar (an orphan if The Armory is removed) | stored sets after a pack change | orphans kept + retried (SkyyVault rule) |
| E5 | Death with a custom page open: does the engine close the page itself? | page state | our ticker closes it anyway |
| E6 | The 1 s `swap.gapSeconds` is enough against PageManager dropping clicks during a rebuild (SkyySacks: periodic page updates make PageManager drop clicks) | UX | rebuild only on click, never on a timer |
| E7 | `ArmoryAlteration` recipe scan from our jar (asset map walk) while The Armory is absent logs no WARN | clean logs | scan only when the bench id resolves |

## 10. Which mod owns it + build plan

**Owner: a new mod `SkyyWardrobe`** (not inside SkyyGear). Reasons: SkyyGear is already the largest script and is queued for 4 rounds
(mob curve, tool levels, loot, speed tiers); the wardrobe is item storage like SkyyVault (its closest code relative: sessions, lossless
files, buy pattern) and must keep working if SkyyGear is rolled back; zero dependencies either way (bridge only). The look-family DATA
stays with the armor jar (SkyyArmory / the recolour build), not with the wardrobe.

| Phase | What | Round (PROJECT-RULES 4) |
|---|---|---|
| W0 | Local probes E1-E7 in a probe jar (SkyyKeyProbe-style `/wdprobe`), one test session; answers folded in here | lean (probe) |
| W1 | **SkyyWardrobe 0.1**: page + tile + commands, slots (free 2, level unlocks, admin), Equip / Store / Take out / Put in, partial sets, journal + repair, per-profile files, Server Setup, `wardrobe.log`, harness test (format round trip, journal repair cases, refusals) | **Ultracode** (items that could be lost or duplicated, saved data, new system) |
| W2 | **Looks** inside the wardrobe: family scan (bridge + Armory recipes), the Looks sub-page, Apply with coins / kit, refund path. Needs Recolor P1 (`gear:base`, SkyyGear) and at least one family live (The Armory's Iron recolours exist today; our own come with Recolor P2 / P3) | Full round (coins + items; one mod) |
| W3 | Polish: coin slot unlocks, rank perks row, Stats-page line, preview if E3 says yes, `/wardrobe <n>` hotkey-ish command | lean |

Build notes for W1: javassist limits per `tools/AGENT-BRIEF.md`; copy the SkyyVault 0.1.5 file / session / buy code shapes (same
repo, our own code); test harness in a bare JVM like `test_skyyvault_0.1.5.py`; cross-check + lint before pin; rollback floor
note for the data folder.

## 11. Questions for Skyy (each with a recommended default)

1. **Free slots and unlocks?** [4 free; 6 at Overall Lv 10, 10 at 20, 14 at 30, 18 at 40 (SkyBlock's rank ladder by level instead of
   rank); no coin unlocks at first - editable rows]
2. **Where does the WORN set go on Equip?** [Into the slot you equipped from (SkyBlock swap). The alternative - worn set to your
   inventory - needs 4 free slots and is slower.]
3. **Partial sets on Equip: keep the worn piece where the slot has none (SkyBlock), or move it into the slot so you wear exactly the
   set?** [Keep (SkyBlock); `swap.strict` row for the other]
4. **Looks button also on the WORN set?** [No in W2 (store, change, equip = 3 clicks); yes in W3 if you miss it]
5. **Look change cost?** [500 coins per set change, editable; Alteration Kit charges only as an option when The Armory is on]
6. **Store unidentified pieces / mystery boxes?** [No - identify first]
7. **Set names?** [Yes, 16 characters, auto "Set N"]
8. **Swap limits?** [Refused while dead, 10 s after combat, 1 s between swaps; no dungeon / arena rule yet (none exist)]
9. **A Wardrobe tile on the main menu, or inside Your Profile?** [Main menu tile (Skyy: "swap from the menu"); Your Profile gets a
   one-line summary]
10. **Own mod SkyyWardrobe?** [Yes]

## 12. For the local session

- Probes E1-E7 (section 9) before W1 - E1 + E2 are the only blockers.
- The Hypixel facts in 2.1 are from the pages cited there (the exact UI swap behaviour and partial-set rule are UNVERIFIED - Skyy
  knows the real thing and can correct Q2 / Q3); the SkyWynn numbers in 6.1 are proposals.
- The tile icon needs our own art (`art/` + the SkyyMenu own-icon pattern); the vanilla Armor Bench icon is the stand-in.
- Recolor-Plan P1 (`gear:base`) must land before W2; W1 does not need it.

## Scope change (Skyy 2026-10-10)
"Oh yeah, and the wardrobe thing for quick swapping armor should be a full loadout swapper, so you make a loadout with the armor, and pets you want. (later maybe even hot bar)" -> each loadout = armor (+ looks) + pet slot + summon slot pets; one click swaps everything; hotbar loadouts later.
