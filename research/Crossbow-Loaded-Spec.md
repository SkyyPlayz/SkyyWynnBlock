# Crossbows stay loaded: the Archery level-5 reward (engine research + SkyySkills 0.4.5 spec)

*Written 2026-09-25. This was read-only research. Only this file was written. Scratch bytecode helpers lived under
`tools/dev/scratch/xbow/` and were deleted afterwards. No build script, jar, doc or game file was touched.*

*Skyy's ask (2026-09-25): "in the archer skill tree, an early on upgrade should make the crossbow stay loaded when you scroll off it and
scroll back (add it to the lvl5 reward)". No Archer class tree exists yet (class trees are Borderlands-style research, HANDOFF 1). So
this becomes the **Archery skill's level-5 reward** in SkyySkills. It ships as **SkyySkills 0.4.5**, built on round 6's 0.4.4. Skyy
uses they/them.*

*Inputs: HANDOFF sections 1 and 3, `tools/CONFIG-CONTRACT.md`, `tools/PROFILES-CONTRACT.md`, `SkyySkills/build_skyyskills_0.4.3.py`,
`SkyyClasses/build_skyyclasses_0.1.5.py`, `SkyySacks/build_skyysacks_0.7.6.py`, three research passes (engine, reference mods, code map),
and my own checks with `tools/dev` (reflect.py, bc.py, bcfull.py, bcfull2.py, cpgrep.py). Those checks ran against the release
`HytaleServer.jar`, `Assets.zip` (read in memory) and `More_Crossbow_Tiers.zip`. SkyySkills line numbers below are from 0.4.3 (the
live, frozen script) and are context only. Round 6's `build_skyyskills_0.4.4.py` is still being edited: during the review pass its
anchors moved twice (+21, then +37 lines). So this spec gives **no 0.4.4 line numbers**. 3.1 lists each 0.4.4 anchor by its literal
text and the method it sits in, which is what the `rep` patch keys on. All of them are still present verbatim.*

*Reviewed 2026-09-25: section 7 lists the review findings, what changed and what was rejected.*

**VERIFIED** = seen directly in bytecode, in asset JSON, or in our own source. **INFERRED** = strongly implied, not read literally.
**UNTESTED** = not seen in game yet (section 4 checks it).

---

## 0. Verdict

**VERDICT: YES.** A server mod can keep one player's crossbow loaded across a hotbar switch. The engine offers no switch that stops
the unloading for one player. SkyySkills therefore lets the vanilla unload happen and puts the same bolts back about 0.1 s after the
player scrolls back. It pays for them with the arrows vanilla just handed back.

In plain words:
1. **How vanilla unloads.** When you scroll AWAY from a loaded crossbow, a small built-in script on the crossbow (its `SwapFrom`
   interaction) gives your loaded bolts back as Crude Arrows. When you scroll ONTO a crossbow, engine code then wipes the loaded
   counter to 0. So you never lose arrows, but you always have to reload (VERIFIED, 1.3 and 1.4).
2. **Where "loaded" lives.** It is not stored on the crossbow item. It is one number on the player, the `Ammo` stat (0-6), just like
   Health or Stamina. The server owns it and the client only displays it (VERIFIED, 1.1).
3. **What the perk does.** Take an Archer with Archery 5 or higher. When they scroll away, SkyySkills notes how many bolts were
   loaded; this is the exact number vanilla refunds (VERIFIED, 1.3). When they scroll back to that same crossbow, SkyySkills waits
   until the engine's wipe has run (3 server ticks, about 0.1 s). It then takes that many Crude Arrows back out of the inventory and
   sets the counter again. The crossbow is ready to shoot, with no reload animation and no reload wait.
4. **What cannot be done.** The two vanilla steps cannot be switched off for one player. Both are driven by item data that every
   player and every crossbow shares (1.9). So the perk undoes them instead. It feels like the crossbow stayed loaded. The visible
   differences are small: your arrow count goes up by N when you leave (vanilla already does this) and down by N when you come back,
   and the bolt counter reads 0 for about 0.1 s after scrolling back.
5. **No free arrows, ever.** Every bolt put back is paid with a real Crude Arrow from your inventory at that moment. The crossbow
   item never carries hidden bolts, so dropping, trading, selling or storing it cannot duplicate anything (2.6).
6. **Which crossbows.** It works for all 6 crossbows in the pack by the id start `Weapon_Crossbow_`: Iron and Ancient Steel, plus
   More Crossbow Tiers' Cobalt, Thorium, Mithril and Adamantite. Each crossbow keeps its own count.
7. **Status.** Not seen in game yet. The engine facts are verified in bytecode and assets. The timing and what the client shows are
   the parts section 4 confirms.

| Question | Answer |
|---|---|
| Can one player's crossbow stay loaded across a hotbar switch? | **Yes**, by putting the bolts back after the vanilla unload (restore, not prevention) |
| Where is "loaded" stored? | Per player: `EntityStatMap` stat `Ammo`, index `DefaultEntityStatTypes.getAmmo()`. Never on the `ItemStack` |
| Hook | `InventorySetActiveSlotEvent` (an `EntityEventSystem` on Player; 9 installed mods use it) + SkyySkills' existing per-tick `AcroSys` |
| Timing | Bolts return 3 ticks after the switch back (~0.1 s at the default 30 TPS, VERIFIED `TickingThread.TPS = 30`) |
| Anti-dupe | Refund on leave (vanilla) + pay on return (ours) = net zero. The bolt count is read exactly at the switch |
| Who gets it | Archer class, Archery >= `perk.archery.keepLoaded.level` (default 5), on the active profile, crossbow allowed by SkyyClasses. Re-checked live right before any arrows are taken, and dropped on the first tick after a profile switch |
| Engine patch / asset override needed? | **No.** Plain plugin code, same API family SkyySkills already uses |

---

## 1. Evidence: how vanilla loads and unloads a crossbow

### 1.1 "Loaded" = the player's `Ammo` stat (VERIFIED)
- `Server/Item/Items/Weapon/Crossbow/Template_Weapon_Crossbow.json` contains:
  - `"Weapon": {"EntityStatsToClear": ["SignatureEnergy","SignatureCharges","Ammo"], "StatModifiers": {"Ammo": [{"Amount": 6, "CalculationType": "Additive"}], ...}}`
  - `"DisplayEntityStatsHUD": ["Ammo"]`
- `Server/Entity/Stats/Ammo.json` = `{"InitialValue": 0, "Min": 0, "Max": 0}`. The cap of 6 exists only while a crossbow is in hand. It
  comes from the item modifier that `StatModifiersManager.recalculateEntityStatModifiers` adds under the key `"*Weapon_"` for the item
  in hand.
- `EntityStatMap` is an ECS `Component` on the entity. It has `get(int)` / `get(String)`, `setStatValue(int, float)`,
  `addStatValue`, `minimizeStatValue` and so on. `EntityStatValue` has `get()`, `getMax()`, `getMin()`, `set(float)`.
  `DefaultEntityStatTypes.getAmmo()` is the index. There is no loaded flag anywhere on `ItemStack`.
- `EntityStatValue.set(f)` and `computeModifiers(...)` both clamp the value to `[min, max]` (bytecode). A write while the cap is 0
  therefore becomes 0. The restore must wait for the cap (2.4).
- `setStatValue(int, float)` = `setStatValue(Predictable.NONE, ...)` and records an `EntityStatOp.Set` change. That change is what the
  client's HUD counter receives (bytecode).
- **No loaded look.** `Server/Item/Animations/Crossbow.json` holds only `Shoot, Reload, ReloadCharged, ReloadCharged2-5, ReloadReady,
  ShootCharged`. `ItemAppearanceConditions` keys are only `SignatureEnergy` and `SignatureCharges`. Nothing on the model depends on
  `Ammo`, so there is no visual state to keep in sync.

### 1.2 Loading costs arrows, firing does not (VERIFIED)
- **Primary** goes through `Weapon_Crossbow_Primary_Signature` / `_Overcharge` into `Weapon_Crossbow_Primary_Reload.json`:
  `DurabilityCondition` → `StatsCondition Costs{Ammo:1}` → `ChangeStat Ammo -1` → shot. If that fails it goes to `Replace Reload_Start`
  → `Root_Common_StatAmmoReload_Entry` (a reload starts).
- **Reload** (also `Ability3`) is `Common_StatAmmoReload_Entry.json`: 0.8 s `ReloadReady`, then a `Repeat` loop (`InterruptedBy`
  Primary/Secondary). Each step runs while Ammo < 100 %:
  - `Common_StatAmmoReload_ItemConsume.json` = `ModifyInventory ItemToRemove {Weapon_Arrow_Crude, 1}`, `RequiredGameMode: Adventure`
  - then `Common_StatAmmoReload_StatModifier.json` = `ApplyEffect StatModifiers {Ammo: 1}`
- So arrows are paid when **loading**, never when firing, and only **Crude** arrows are used. In Creative, loading is free:
  `ModifyInventoryInteraction.firstRun` returns early when the game mode differs (offsets 60-70).
- `ModifyInventoryInteraction.firstRun` removes with
  `InventoryComponent.getCombined(acc, ref, InventoryComponent.HOTBAR_STORAGE_BACKPACK).removeItemStack(stack, true, true)`. It adds
  with `SimpleItemContainer.addOrDropItemStack(acc, ref, combined, stack)`, which **drops on the ground** whatever does not fit
  (offsets 71-98 and 199-235).

### 1.3 Switching away: the `SwapFrom` refund (asset, VERIFIED)
- The template's `"Interactions": {"SwapFrom": "Root_Weapon_Crossbow_Swap_From", ...}`. The root has `RequireNewClick: false`,
  `Cooldown 0` and points to `Weapon_Crossbow_Swap_From.json`:
  `Condition RequiredGameMode Adventure`. If that fails (not Adventure) it goes straight to `ChangeActiveSlot`. Otherwise it runs a
  ladder `StatsCondition Costs{Ammo:6}` … `{Ammo:1}`. The first step that passes runs `ModifyInventory ItemToAdd {Weapon_Arrow_Crude, k}`
  and then `ChangeActiveSlot`.
- **`StatsCondition` only checks. It does not spend** (`StatsConditionInteraction.firstRun` calls `canAfford` and sets `Failed`;
  there is no stat write). So the ladder refunds `k = min(floor(Ammo), 6)` arrows and **leaves `Ammo` untouched**.
- `ChangeActiveSlotInteraction.tick0` then calls `InventoryComponent$Hotbar.setActiveSlot(byte, Ref, ComponentAccessor)` (declared
  on `ActiveSlotInventoryComponent`; the call passes the interaction's `CommandBuffer`, which implements `ComponentAccessor`). That
  method fires `InventorySetActiveSlotEvent(sectionId, previousSlot, newSlot)` (bytecode).
  **Consequence for the design: inside our handler for that event, `Ammo` still equals exactly the load that was just refunded.** No
  per-tick tracking or guessing is needed.
- **Every event is a real change (VERIFIED, bytecode of both `setActiveSlot` overloads).** The method returns at once, with no event,
  when the new slot equals the current one. Otherwise it reads `previousSlot` from its own `activeSlot` field, writes the new slot,
  and only then fires. So the engine never sends a no-op event, and `previousSlot` is always the slot that was really active.
- **The hotbar can only change through this interaction.** A raw `SetActiveSlot` packet for section -1 disconnects the client with
  `server.general.disconnect.hotbarChangeWithoutInteraction` (`InventoryPacketHandler.lambda$handle$7`, bytecode). So in Adventure,
  every scroll or number key runs the refund. Server-side calls (`Inventory.setActiveHotbarSlot`, NPC helpers) skip it; see 2.9.
- **Shortbows** have the same kind of refund (1 drawn arrow, `Ammo` cap 1). They are out of scope and this perk ignores them.

### 1.4 Switching back: the engine wipe (code, VERIFIED)
- `InventorySystems$ActiveSlotChangedEntityEventSystem.handle(..., InventorySetActiveSlotEvent)` does the following:
  - sets Hotbar/Utility `setOutdatedEquipment(true)`
  - calls `StatModifiersManager.scheduleRecalculate()`
  - for section -1, reads `InventoryComponent.getItemInHand` (already the **new** item) → `Item.getWeapon().getEntityStatsToClear()`
    → `queueEntityStatsToClear(int[])`
- `queueEntityStatsToClear` only adds to a set. The wipe happens in `StatModifiersManager.recalculateEntityStatModifiers`, which is
  called every tick by `EntityStatsSystems$Recalculate` (an `EntityTickingSystem` over every `EntityStatMap`). It runs only when
  flagged, and does this:
  - `minimizeStatValue(Predictable.SELF, id)` for each queued stat (Ammo → 0)
  - then re-applies the effect, armor and in-hand item modifiers (the crossbow's +6 cap)
- So scrolling onto any crossbow sets `Ammo` to 0 at the **next `Recalculate` pass**. `Recalculate` declares no system dependencies,
  so its order relative to the interaction tick (where the event fires) is not defined. It may run later in the same tick or in the
  next tick. After it has run, the cap is 6 and the value is 0.
- `InventorySystems$LegacyHotbarChangeStatSystem` also queues the same clear whenever the **active** hotbar slot's stack changes to a
  non-equivalent one. `ItemStack.isEquivalentType` compares item id **and metadata**. This is one more reason the perk must never
  write metadata onto a held crossbow (1.9).

### 1.5 The event we hook (VERIFIED)
- `com.hypixel.hytale.server.core.event.events.ecs.InventorySetActiveSlotEvent extends EcsEvent` (not cancellable).
  - `getInventorySectionId()` (-1 = hotbar, -5 = utility, -8 = tools)
  - `getPreviousSlot()` (int)
  - `getNewSlot()` (byte)
- It is used the same way by SimpleEnchantments, ZiggfreedCommon/MMOSkillTree, Spyglass, CarryChest, Aetherhaven, Alec's Tamework,
  Starky's Shield and WansWonderWeapon (research pass 2). SkyySkills' own `SmeltSys` is the template: an `EntityEventSystem` with
  `super(EventClass.class)` and a Player query.

### 1.6 What the client shows (INFERRED from the protocol, UNTESTED)
- The HUD bolt counter is the `Ammo` stat (`DisplayEntityStatsHUD`). The server pushes `Set` changes, so the counter shows whatever the
  server holds.
- Leaving: vanilla gives N Crude Arrows back (the inventory count rises). Returning: the counter reads 0 for about 3 ticks plus ping,
  then jumps to N as the arrow count drops by N. No reload animation or sound plays, because no interaction runs.

### 1.7 Every crossbow in the pack uses the same template (VERIFIED)
- Vanilla `Weapon_Crossbow_Iron.json` and `Weapon_Crossbow_Ancient_Steel.json` are `"Parent": "Template_Weapon_Crossbow"` with no
  overrides of `Interactions` or `Weapon`.
- `More_Crossbow_Tiers.zip` (Serj 1.1.0, `IncludesAssetPack: false`, no code) has `Weapon_Crossbow_{Cobalt,Thorium,Mithril,Adamantite}.json`,
  all `"Parent": "Template_Weapon_Crossbow"`, with no `Interactions` and no `Weapon` block. They behave exactly like Iron.
- Only the not-packed "Endgame&QoL expansion - Crossbow Tiers" overrides `Weapon` on some tiers. It is not in PACK.md.
- SkyyClasses already maps `Weapon_Crossbow_` to Archer (`CLASSES[0]["weapons"]`, `build_skyyclasses_0.1.5.py` lines 140-144).
- SkyySacks never pockets arrows: `SackDefs.catOf` returns null for `Weapon_Arrow_*` (`build_skyysacks_0.7.6.py` lines 320-346), so a
  bag sweep cannot take the refunded arrows away between leaving and returning.

### 1.8 Engine facts the build uses (all VERIFIED)
| Piece | Exact name |
|---|---|
| Event | `server.core.event.events.ecs.InventorySetActiveSlotEvent` (`getInventorySectionId() int`, `getPreviousSlot() int`, `getNewSlot() byte`) |
| Event system base | `component.system.EntityEventSystem` (ctor `super(Class)`, `getQuery()`, `handle(int, ArchetypeChunk, Store, CommandBuffer, EcsEvent)`) |
| Stats | `server.core.modules.entitystats.EntityStatMap.getComponentType()`, `.get(int)` → `EntityStatValue` (`get()`, `getMax()`), `.setStatValue(int, float)` |
| Ammo index | `server.core.modules.entitystats.asset.DefaultEntityStatTypes.getAmmo()` (static int) |
| Hotbar | `server.core.inventory.InventoryComponent$Hotbar.getComponentType()`, `getActiveSlot()` (byte), `getInventory()` → `ItemContainer.getItemStack(short)` |
| Arrow count | `InventoryComponent$Hotbar`, `$Storage`, `$Backpack` → `getInventory()` → slots; or `Player.getInventory().getHotbar()/getStorage()/getBackpack()` (SkyySacks pattern) |
| Arrow payment | `InventoryComponent.getCombined(ComponentAccessor, Ref, InventoryComponent.HOTBAR_STORAGE_BACKPACK).removeItemStack(new ItemStack("Weapon_Arrow_Crude", n), true, true)` → `ItemStackTransaction.succeeded()`, exactly vanilla's reload call |
| Stack identity | `ItemStack.getItemId()`, `isEmpty()`, `isEquivalentType(ItemStack)` (id + metadata) |
| Game mode | `Player.getGameMode()` vs `protocol.GameMode.Creative` (SkyySkills `Acro.creativeMode` already does this) |
| Death | `server.core.modules.entity.damage.DeathComponent.getComponentType()` present on the entity (SkyyCoins pattern) |
| Ref identity | `component.Ref` has no `equals`: identity, one per entity per world store, `isValid()` |
| Tick rate | `server.core.util.thread.TickingThread.TPS = 30` (worlds may `setTps`) |

### 1.9 Rejected ways (and why)
- **Override the crossbow `SwapFrom` asset** (for example a custom Interaction type registered like ItemStateChanger's
  `ChangeItemState`, placed in an overriding `Root_Weapon_Crossbow_Swap_From`). This would change every crossbow for every player.
  It would clash with any other mod touching that file. It still cannot stop the 1.4 wipe, which is engine code reading the new item's
  `EntityStatsToClear`. Editing that list in the template would affect everyone and every tier. SkyySkills also ships no asset pack.
- **Javassist-patch `StatModifiersManager.queueEntityStatsToClear`** (research pass 1, option 4). Our toolchain compiles our own
  classes; it cannot redefine engine classes at runtime without an agent. It would also be a global change.
- **Store the load in `ItemStack` metadata** (research pass 2). Writing metadata onto the held crossbow makes the active stack
  "non-equivalent", and `LegacyHotbarChangeStatSystem` then wipes `Ammo` itself (1.4). HANDOFF section 2 also forbids metadata stacks
  in `ItemGridSlot` (the 2026-09-25 disconnect). And it would put hidden value on a tradeable item. Memory-only state is safer and
  needs no item write.
- **Remove the refunded arrows right after leaving** (research pass 1, option 1). If that removal ever failed or raced, it would
  duplicate items. Paying at return (2.5) instead fails safe: no arrows means no bolts.
- **Keying by player only.** SimpleEnchantments' `EnchantmentEternalShotSystem` shows that trap. Two crossbows share one `Ammo`
  stat, so the kept load must be per hotbar slot and per stack (2.3).

---

## 2. Design

### 2.1 In one paragraph
The perk is per player and lives in memory, on the world thread. On a hotbar switch **away** from a crossbow, SkyySkills reads that
player's `Ammo`: the exact bolts vanilla just refunded. It remembers them for that hotbar slot and that crossbow stack. On a switch
**back** to the same stack, it arms a restore. Three of SkyySkills' own ticks later, after vanilla's wipe, it takes up to that many
Crude Arrows from the inventory and sets `Ammo` to what it paid for, never above the cap. Nothing is saved to disk. Nothing is written
onto items. No interaction is started.

### 2.2 Who has it (the perk flag, per player and per profile)
The perk is active for a player only while **all** of these hold:
1. `perk.archery.keepLoaded.enabled=true` (the part switch).
2. The current class is **Archer**: `SkillClass.slot(u) == SkillClass.slotOfClass("Archer")` (storage slot 5, `Combat.Archer`).
   `SkillClass.consistent(u)` must also hold, so it is off during a profile/class mismatch after a switch.
3. The **Archery** level on the **active profile** is at least `perk.archery.keepLoaded.level` (default **5**):
   `SkillStore.level(u, SkillClass.slotOfClass("Archer")) >= LEVEL`. `data(u)` resolves the profile key itself.
4. Not while `profile:busy:<uuid>` is `TRUE` (PROFILES-CONTRACT rule 5: no item moves while the live inventory may belong to another
   profile).

Per crossbow, at switch time: the item id starts with one entry of `perk.archery.keepLoaded.items` (default `Weapon_Crossbow_`). When
SkyyClasses publishes `class:fn:allowed`, it must also answer `TRUE` for `(uuid, itemId)`, which is the weapon lock. This mirrors
`SkillClass.itemOk`.

No new saved flag. The flag is **computed** from the profile's own Archery level, so it follows profiles automatically. For speed it
is cached per UUID (`Xbow.ON`). The cache is refreshed every second in `Perks.tick`, right after a level-up in `SkillXp.gain4`, and
after a profile switch in `Perks.switched`. Without SkyyClasses there is no class, so the perk is off. Archery cannot be earned without
a class anyway (`SkillClass.killSlot`).

**The cache only decides when to remember and arm. It never decides a payout.** In 0.4.4 `Perks.tick` and the epoch check that calls
`Perks.switched` sit behind `AcroSys`'s once-per-second gate (`if (s[14] < 1.0) return;`), so the cache can be up to 1 s old. A
profile switch, on the other hand, happens in one world-thread task with no delay (PROFILES-CONTRACT, "Switch" row). So two extra
checks run on every tick and at the moment of payment (2.5):
- **Epoch stamp.** Each `XbowState` stores the `profile:epoch:<uuid>` value it was built under (`Perks.epoch(u)`, one bridge map read,
  no lock, no I/O). If the live value differs, the whole state is dropped at once (2.4, 2.5 step 1).
- **Live check before paying.** Right before arrows are taken, rules 1-4 and the weapon rule are computed again, uncached (2.5 step 3).

### 2.3 State (memory only, one `XbowState` per online player, `ConcurrentHashMap<UUID, XbowState>`)
| Field | Meaning |
|---|---|
| `ref` | The entity `Ref` this state belongs to. A different `Ref` (relog or world change) wipes the state |
| `epoch` | The `profile:epoch:<uuid>` value this state was built under (`Perks.epoch(u)`, -1 = none seen). A different live value wipes the state |
| `ticks` | Counter, +1 on every `AcroSys` tick for this player |
| `n[i]`, `st[i]`, `cre[i]` | Kept load per hotbar slot `i`: bolt count (0 = none), the stack seen at switch-away (identity check), and whether the player was in Creative then |
| `enterAt` | `ticks` value at the last switch onto the current slot |
| `pendSlot`, `pendAt` | An armed restore: its slot (-1 = none) and the `ticks` value when it was armed |

Size the arrays by the hotbar capacity (`InventoryComponent.DEFAULT_HOTBAR_CAPACITY`, or 16 to be safe) and ignore slot indices out
of range.

### 2.4 Step order on a hotbar switch (`XbowSlotSys`, section -1 only, world thread)
The handler receives `prev = getPreviousSlot()` and `new = getNewSlot()`. It gets the state; if `state.ref != ref` it resets the state
and stores `ref`. Then it runs the **epoch check** (`Xbow.fresh`, shared with 2.5):
- `e = Perks.epoch(u)`. If `e < 0` (absent), change nothing. If `state.epoch < 0`, adopt `e`: the first value is a baseline, not a
  switch (PROFILES-CONTRACT semantics rule 2, the same rule as `Perks.epochChanged`).
- If `state.epoch >= 0` and differs from `e`: reset the whole state, store `epoch = e`, and put `Boolean.FALSE` into `Xbow.ON` for
  `u`. The cache comes back on through `Perks.switched` → `Xbow.refresh` within 1 s. Setting it false (instead of recomputing here)
  keeps the new profile's first file load out of this handler.

Then:

**A. Leaving `prev`:**
1. If a restore was armed for `prev` and has not landed yet (`pendSlot == prev`): cancel it and **leave `n[prev]` as it was**. The bolts
   are still in the inventory as arrows, and live `Ammo` may already be wiped. Skip to B.
2. Otherwise, if the perk is active, the stack in slot `prev` is a crossbow (items rule + allowed), **and** the player held it for at
   least `delayTicks` (`ticks - enterAt >= delayTicks`), then set `k = min(floor(Ammo.get()), floor(Ammo.getMax()), 6)`. That is
   exactly the Adventure refund (1.3). Store `n[prev] = k`, `st[prev] = that stack`, `cre[prev] = creative now`. If `k == 0`, clear
   the entry.
   The "held long enough" rule matters: right after switching onto a crossbow, `Ammo` can still show the previous crossbow's value
   until vanilla's wipe runs (1.4). Such a stale value is never recorded.
3. Otherwise clear `n[prev]`.
4. Cancel any other armed restore (`pendSlot = -1`).

**B. Arriving at `new`:**
1. Set `enterAt = ticks`.
2. If `n[new] > 0`, the perk is active, and the stack now in slot `new` passes `isEquivalentType(st[new])` (same id, same metadata:
   rolled crossbows are unique) → arm: `pendSlot = new`, `pendAt = ticks`.
3. Otherwise clear `n[new]`. The crossbow was moved, dropped, traded or replaced. Its bolts already came back as arrows when it was
   left, so nothing is lost.

### 2.5 The restore (`Xbow.tick` inside `AcroSys`, every tick, world thread)
First: `ticks++`. Then:
1. **Wipe the whole state** (all kept loads, the armed restore) if any of these is true:
   - the `Ref` changed
   - a `DeathComponent` is on the entity
   - the live profile epoch differs from `state.epoch`: the `Xbow.fresh` check from 2.4, run **here on every tick**, before anything
     else. It does not wait for `Perks.switched`, which runs at most once per second
   - the cached perk flag is false
2. Keep the state but do not restore this tick while `profile:busy` is set. The armed restore is kept; it still times out at 60 ticks.
3. If a restore is armed and `ticks >= pendAt + delayTicks` (default 3):
   - **Still valid?** The active hotbar slot must be `pendSlot` and its stack must be equivalent to `st[pendSlot]`. If not, drop the
     entry and the armed restore.
   - **Cap there?** Let `v = EntityStatMap.get(Ammo)`. If `v == null` or `v.getMax() < 1`, wait. After 60 ticks, give up and drop it.
   - `target = min(n[slot], floor(v.getMax()))`, `cur = floor(v.get())`, `need = target - cur`.
     `cur` is above 0 only if the player clicked and a vanilla reload already loaded some bolts; that is paid, so no double pay.
   - If `need > 0`:
     - **Live eligibility, uncached (`Xbow.eligibleNow(u, itemId)`).** Compute 2.2 rules 1-4 again right now: `XbowCfg.ON`,
       `SkillClass.consistent(u)`, `SkillClass.slot(u) == SkillClass.slotOfClass("Archer")`,
       `SkillStore.level(u, SkillClass.slotOfClass("Archer")) >= XbowCfg.LEVEL`, not busy, **and** `Xbow.allowed(u, itemId)` for
       the stack in the slot. Ignore `Xbow.ON` here. If any fails: drop the entry and the armed restore, pay nothing, and put
       the rules 1-3 result (what `refresh` computes, without the weapon rule) into `Xbow.ON`. The epoch check above already
       matched, so `data(u)` reads the profile that is loaded now; this adds no file I/O.
     - **Creative:** only when `cre[slot]` and Creative now, `pay = need` for free. Vanilla loads free in Creative and gave no refund.
     - **Otherwise:** `have` = Crude Arrows in hotbar + storage + backpack, and `pay = min(need, have)`. If `pay > 0`, remove them with
       `getCombined(store, ref, HOTBAR_STORAGE_BACKPACK).removeItemStack(new ItemStack("Weapon_Arrow_Crude", pay), true, true)`.
       If that transaction did not succeed, `pay = 0`.
     - If `pay > 0`: `esm.setStatValue(ammoIdx, (float) (cur + pay))`. Always **pay first, set second**: a failure can never give a
       free bolt.
   - Clear the entry and the armed restore, whatever the outcome.
   - Debug: see the debug row in 3.3.

**Why 3 ticks.** The switch event fires inside the interaction tick. `Recalculate`, which applies the wipe, may run before or after
that in the same tick (1.4). `AcroSys` may also run before or after either. After 3 `AcroSys` ticks, at least one full `Recalculate`
pass has certainly run after the event. The counter math: the restore lands at world tick T+2 or T+3. Together with the cap check,
the restore therefore never lands before the wipe (VERIFIED order logic; UNTESTED feel).

**What leans on the tick count alone, and what a mistake would cost (review, 7.8).**
- Coming back from a **non-crossbow** slot there is already a positive signal: the `Ammo` cap is 0 until `Recalculate` re-applies the
  crossbow's +6, and the cap check waits for exactly that.
- Coming back **directly from another crossbow** (the cap stays 6), nothing public shows that the wipe has run.
  `StatModifiersManager`'s public API is only `recalculateEntityStatModifiers`, `queueEntityStatsToClear` and `scheduleRecalculate`
  (reflection): no pending flag, no queue getter. Here the 3-tick count is the only guard.
- If the count were ever too short, the error goes toward **loss, never gain**. An early restore is paid and then wiped, so the
  player loses those arrows. On the leaving side, the value read is the same stale `Ammo` vanilla's ladder refunded in that moment,
  and every bolt put back later is paid 1:1. So no free bolt can come out either way.
- So section 4 steps 5 (two crossbows, direct 3 → 1 and 1 → 3) and 12 are **pre-launch go/no-go checks**, not only follow-ups
  after a field report. If arrows ever go missing there, raise the default delay or apply F1 before 0.4.5 ships.

A system dependency (`SystemDependency(Order.AFTER, EntityStatsSystems$Recalculate.class)`, VERIFIED constructible) could save one
tick. It is **not** used: a cross-module ordering edge that fails to resolve would break setup, for a 33 ms gain.

### 2.6 Anti-dupe rules (the complete list)
| Case | What happens | Why it is safe |
|---|---|---|
| Normal round trip | Vanilla refunds N arrows on leave, we take N back on return | Net zero, like vanilla plus a free reload *time* |
| Arrows spent, sold, stored or dropped while away | We take only what you still have: `pay = min(N, have)` | No arrows means no bolts; never negative |
| Inventory full when leaving | Vanilla drops the refund on the ground (`addOrDropItemStack`); we charge from the inventory at return | Whatever you did not pick up is not loaded |
| Crossbow dropped, traded (`/trade`), sold (`/ah`), put in a chest or vault, or moved to another slot | The kept entry is cleared (slot empty or stack not equivalent) | Its bolts were already refunded; the item carries **no** hidden data |
| Another crossbow of the same id put into the slot | Equivalent (same id, no metadata), so it gets the paid restore | Paid with your own arrows: no gain but time |
| Two crossbows | One entry per hotbar slot; each keeps its own count | The shared `Ammo` stat only ever holds the *active* crossbow's load |
| Clicking during the ~0.1 s gap | Vanilla sees Ammo 0 and starts a reload (paid per bolt); our restore then tops up only `target - cur`, paid | Never above the cap (`EntityStatValue.set` clamps); never a projectile |
| Double shots | Impossible: the perk only writes one stat value; it never starts an interaction or spawns a projectile | Every shot is a vanilla click with `StatsCondition Costs{Ammo:1}` |
| Rapid scrolling (leave before the restore lands) | Armed restore cancelled, kept count unchanged, `Ammo` not re-read | Stale values are never recorded (2.4 A1/A2) |
| Creative | Free restore only if both the leave and the return were in Creative; mixed modes are charged | Vanilla loads free in Creative and refunds nothing there |
| Profile switch, `profile:busy`, death, relog, world change | All kept loads wiped, nothing restored; no restore while busy | Arrows were refunded into the inventory the kept load belonged to |
| Profile switch while a restore is armed (within the 3-20 tick window) | The per-tick epoch check (2.5 step 1) drops the state on the first tick after the switch, before any payment | The new profile's arrows are never spent on the old profile's load |
| Class, level or weapon lock changes between arming and paying | `Xbow.eligibleNow` is computed live right before paying (2.5 step 3); the 1 s cache is not trusted for payouts | The level/class gate holds at the moment arrows are spent |
| Other players | Every map is keyed by UUID; flag per player | Multiplayer-safe |
| Server-side slot change (another mod, no `SwapFrom` refund) | Load kept and restored for arrows | Same cost as vanilla, which would wipe the bolts and make you reload |

### 2.7 What the client shows (UNTESTED)
- **Leaving** (unchanged vanilla): the crossbow's loaded bolts appear as +N Crude Arrows.
- **Returning:** the bolt counter shows 0 for about 0.1 s (3 ticks plus ping). Then it shows N while the Crude Arrows drop by N. There
  is no reload animation and no sound. The crossbow model looks the same as always, because no loaded pose exists (1.1).
- If the player lacks arrows: a partial or no restore, the counter shows what was paid for, and a normal reload finishes the rest.

### 2.8 Profile switch, relog, death, world change
- **Profile switch:** the first `Xbow.tick` or slot event after the switch sees a new epoch and drops the old profile's kept loads
  and any armed restore (2.4, 2.5 step 1). This does not wait for the once-per-second `Perks.switched`. `Perks.switched(u)` still calls
  `Xbow.forget(u)` and `Xbow.refresh(u)`, so the flag is recomputed from the new profile's Archery level and class. A Warrior profile
  never has it.
- **Relog:** the state is wiped (new `Ref`), plus `Acro.retainOnline` prunes offline UUIDs every 30 s. Kept loads are lost, but the
  bolts are already in the inventory as arrows. What vanilla does with a crossbow held **loaded** at logout is unchanged and untouched.
- **Death:** wiped while the `DeathComponent` is present. Whatever the server's death rules do to items applies to the refunded arrows
  like any item.
- **World change** (`/hub`, `/island`, portals): wiped (new `Ref`). A teleport means reloading once. This is an open question (6.3).
- Nothing is written to `players/<pkey>.properties`, and there is no migration.

### 2.9 Known limits (documented, not bugs)
- The restore is not instant: about 0.1 s. A click inside that window starts a vanilla reload (2.6).
- Only the loaded bolts are kept. The **Signature** meter (the big-arrow ability charge, `SignatureEnergy` / `SignatureCharges`) still
  resets on a switch like vanilla (open question 6.5).
- Only **Crude** arrows exist in the crossbow's economy: vanilla loads Crude, refunds Crude, and we charge Crude.
- A crossbow in the off-hand / utility slot (`Utility.Compatible: true`) is not covered. Only hotbar switches are.
- **Vanilla, not this perk (INFERRED):** `StatsCondition` does not spend `Ammo` (1.3). If two `SwapFrom` chains ever ran in one tick
  before `Recalculate`, vanilla itself could refund twice. The perk's restores are always paid, so it creates no arrows there. It
  would, however, make such a vanilla loop faster (no reload time between rounds). So step 4.9's quick-flick check is a
  **go/no-go gate for 0.4.5**: if a double refund is ever seen, 0.4.5 does not ship until it is understood. This is a separate risk
  from the slot event: the engine never sends a repeated or no-op `InventorySetActiveSlotEvent` (1.3), so the single `pendSlot` needs
  no duplicate-event guard.
- **SkyyProfiles, not this perk (INFERRED):** switching profile while holding a *loaded* crossbow leaves the `Ammo` stat on the entity.
  The next profile's active stack decides whether vanilla wipes it. That is a pre-existing edge for a later SkyyProfiles pass.

---

## 3. SkyySkills 0.4.5 build (patch on 0.4.4)

### 3.1 Files and version
- Source of truth: `tools/skills_0_4_5_patch.py` (asserted `rep` anchors, the `skills_0_4_3_patch.py` style). It writes
  `SkyySkills/build_skyyskills_0.4.5.py` with `VERSION = "0.4.5"`, display name `"0.4.5 SkyySkills"`.
- Nothing else changes: not SkyyClasses, SkyyTrees, SkyyMenu or SkyyProfiles. The new rows appear in SkyyMenu's Server Setup on their
  own through the kit.
- The header docstring gets a "0.4.5: Crossbows stay loaded (research/Crossbow-Loaded-Spec.md)" block summarizing 2.2-2.8.
- **0.4.4 anchors, by literal text** (no line numbers: the script is still moving, see the header). Each string below occurred
  **exactly once** in `build_skyyskills_0.4.4.py` at review time. The `skills_0_4_3_patch.py` `rep(old, new, count=1)` helper
  already asserts that count, so any drift fails loudly instead of patching the wrong place. The two "called, not patched" rows need
  a plain `assert anchor in s`.

  | Anchor text (literal, as in the .py source) | Where it sits | Used by |
  |---|---|---|
  | `{PKG}.PartyCfg.ensureDefaults(p);` | `SkillCfg.load` | 3.2 `XbowCfg.ensureDefaults(p)` after it |
  | `{PKG}.BridgeCfg.read(p);` | `SkillCfg.load` | 3.2 `XbowCfg.read(p)` after it |
  | `pr.sendMessage({MSG}.raw("SKILL LEVEL UP  "` | `SkillXp.gain4`, inside the `for (lv ...)` loop | 3.7 unlock line after it |
  | `public static void switched(java.util.UUID u) {{` | `Perks.switched` | 3.7 |
  | `public static void tick(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref) {{` | `Perks.tick` | 3.7 |
  | `public static long epoch(java.util.UUID u)` | `Perks.epoch` (exists; called, not patched) | 2.4 / 2.5 epoch check |
  | `{PKG}.BridgeXp.retain(online);` | `Acro.retainOnline` | 3.7 `Xbow.retain(online)` after it |
  | `{PKG}.Brew.tick(u, store, cb, ref, dt);` | `AcroSys.tick`, **before** `if (s[14] < 1.0) return;` | 3.6 `Xbow.tick` after it |
  | `public static java.util.ArrayList lines(java.util.UUID u, int s, int lv, boolean next) {{` | `StatsPage.lines` | 3.7 |
  | `("bridge.bonus.enabled", "Skill tree bonuses"` | `CFG_ROWS`, parts | 3.3 part-switch row after that row |
  | `"On: the class damage bonus also applies when hitting players.", "reload;confirm=on"))` | end of the `perk.combat.damageVsPlayers` append inside `if _k == "combat":` | 3.3 perks rows after it |
  | `getEntityStoreRegistry().registerSystem(new {PKG}.SmeltSys());` | `setup()` | 3.5 register `XbowSlotSys` after it |
  | `assert len(_absent) == 21` | after `CFG_ROWS` | stays as is (3.3) |
  | `assert len(CFG_ROWS) == 154` | after `CFG_ROWS` | bump by 5 (3.9) |
  | `public static int slotOfClass(String c) {{` | `SkillClass.slotOfClass` (exists; called, not patched) | 2.2, 3.7 |
- **0.4.4 removed `SkillDefs.CLASS0` / `CLASS_END`** (class slots are now `CLASS_SLOT = [5, 6, 7, 8, 9, 14, 15]` for Berserker and
  Priest). Always find the Archer slot with `SkillClass.slotOfClass("Archer")` (still slot 5). Never use slot arithmetic.

### 3.2 Config: `XbowCfg` (new class, the `PartyCfg` / `FellCfg` pattern)
The default text is `XBOW_L`, appended to `L`, so it is inside `DEFAULTS` and the kit's default-file asserts. It is ASCII only, with
no `"`:
```
# ---------- Crossbows stay loaded (SkyySkills 0.4.5) - the Archery level-5 reward, research/Crossbow-Loaded-Spec.md ----------
# Comments must stay on their own lines.
# An Archer whose Archery level is at least 'level' keeps a crossbow's loaded bolts when switching hotbar slots and back.
# Vanilla gives the bolts back as Crude Arrows when you switch away; switching back loads them again, paid with those arrows.
perk.archery.keepLoaded.enabled=true
perk.archery.keepLoaded.level=5
# item id starts that count as crossbows, comma separated
perk.archery.keepLoaded.items=Weapon_Crossbow_
# server ticks after switching back before the bolts return (3-20; 3 = about 0.1 s)
perk.archery.keepLoaded.delayTicks=3
# debug=true: players with skyyskills.admin see a chat line for every kept / restored load
perk.archery.keepLoaded.debug=false
```
- Fields: `public static volatile boolean ON = true; int LEVEL = 5; String[] ITEMS = {"Weapon_Crossbow_"}; int DELAY = 3; boolean DEBUG = false;`
  and `public static final String DEFAULTS = <XBOW_LIT>`.
- `read(Properties p)`:
  - `ON = SkillCfg.bool(p, "perk.archery.keepLoaded.enabled", true)`
  - `LEVEL` clamped 0..100
  - `ITEMS` = the comma list, trimmed, empties dropped; `{"Weapon_Crossbow_"}` when it ends up empty
  - `DELAY` clamped 3..20
  - `DEBUG` bool
- `ensureDefaults(Properties p)`: if `p.getProperty("perk.archery.keepLoaded.enabled") == null`, append `"\n" + DEFAULTS` to
  `SkillCfg.FILE`, log one info line, warn on failure. This is the `FellCfg.ensureDefaults` body.
- `SkillCfg.load`: call `XbowCfg.ensureDefaults(p)` after `PartyCfg.ensureDefaults(p)` (0.4.3 line 2120) and `XbowCfg.read(p)` after
  `BridgeCfg.read(p)` (line 2168 area). `/skills reload` and the kit's `SkillKit.reload` then re-read it for free.
- `isCrossbow(String id)`: non-null and `id.startsWith(ITEMS[i])` for some `i`.

### 3.3 Server Setup rows (tools/CONFIG-CONTRACT.md: `reload` binding to `xp.properties`, kit build checks)
The tuple layout is `(key, label, category, type, default, min, max, opts, unit, flags, help, binding)`:
```python
# parts (after "bridge.bonus.enabled"): part switch = bool + live,part,danger; asks only when switched OFF
("perk.archery.keepLoaded.enabled", "Crossbows stay loaded", "parts", "bool", "true", "", "", "", "", _LP,
 "Off: a crossbow unloads when you switch slots, as in vanilla (its bolts come back as arrows).", "reload"),
# perks (after "perk.combat.damageVsPlayers")
("perk.archery.keepLoaded.level", "Crossbows stay loaded from Archery", "perks", "int", "5", "0", "100", "", "", "live",
 "Archery level that unlocks it (5 = the level-5 reward, 0 = every Archer).", "reload"),
("perk.archery.keepLoaded.items", "Crossbow ids (stay loaded)", "perks", "text", "Weapon_Crossbow_", "", "500", "", "", "live,adv",
 "Item id starts that count as crossbows, comma separated. More Crossbow Tiers is included.", "reload"),
("perk.archery.keepLoaded.delayTicks", "Stay-loaded restore delay", "perks", "int", "3", "3", "20", "", "", "live,adv",
 "Server ticks after switching back before the bolts return (3 = about 0.1 s).", "reload"),
("perk.archery.keepLoaded.debug", "Stay-loaded debug lines", "perks", "bool", "false", "", "", "", "", "live,adv",
 "On: admins see a chat line each time a crossbow load is kept or put back (for testing).", "reload"),
```
- The lengths are checked: labels 21/34/26/25/23 (max 40) and help 93/73/89/76/87 (max 100).
- Each default equals its `XBOW_L` line, so 0.4.3's default assert holds. The "absent from the default file" count stays **21**
  (only rows missing from `DEFAULTS` count, and all 5 are in `XBOW_L`). The sibling `assert len(CFG_ROWS) == 154` goes up by 5 (3.9).
- No key lies inside a table family (`block.`, `prefix.`, `suffix.`, `combat.role.`, `alchemy.xp.`, `smithing.xp.`).
- The unit is `""`: ticks are not a kit unit, so the label says it.
- Debug lines, admins only (`pr.hasPermission("skyyskills.admin")`, the `acro.doubleJump.debug` pattern), at most one per event:
  - `[Skills debug] kept 6 bolts - Weapon_Crossbow_Iron, slot 1`
  - `[Skills debug] put back 6 bolts, paid 6 Crude Arrows`
  - `[Skills debug] put back 2 of 6 bolts - only 2 Crude Arrows`
  - `[Skills debug] load dropped - crossbow left slot 1`

### 3.4 `XbowState` (new class) and `Xbow` (new class, logic; no inner classes, lambdas or generics: javassist rules)
- **`XbowState`** holds public fields exactly as in 2.3 (including `long epoch = -1L`), with the arrays created in the constructor.
- `Xbow.S` = `ConcurrentHashMap` UUID → `XbowState`. `Xbow.ON` = `ConcurrentHashMap` UUID → `Boolean` (the cached flag).
- `Xbow.state(UUID u)`: get or create.
- `Xbow.forget(UUID u)`: `S.remove(u)`.
- `Xbow.retain(java.util.Set online)`: prune `S` and `ON`. Call it from `Acro.retainOnline` next to `BridgeXp.retain(online)`.
- `Xbow.refresh(UUID u)`: compute 2.2 rules 1-3 → `ON.put(u, Boolean)`. On false, also `forget(u)`.
- `Xbow.active(UUID u)`: `Boolean.TRUE.equals(ON.get(u)) && !busy(u)`, where `busy` = bridge `profile:busy:<uuid>` is `Boolean.TRUE`.
- `Xbow.allowed(UUID u, String id)`: `XbowCfg.isCrossbow(id)`. Also, when `SkillClass.allowedFn()` is non-null, it must answer `TRUE`
  for `new Object[]{u, id}`. Wrap in try; any error = false.
- `Xbow.rules(UUID u)`: 2.2 rules 1-3, uncached (the body `refresh` uses). `Xbow.eligibleNow(UUID u, String id)`:
  `rules(u) && !busy(u) && allowed(u, id)`, used only right before paying (2.5 step 3).
- `Xbow.fresh(XbowState s, UUID u)`: the epoch check from 2.4 (adopt on first value, reset + `ON.put(u, FALSE)` on a change). It is
  called first in both `onSlot` and `tick`.
- `Xbow.onSlot(Store st, Ref ref, ArchetypeChunk chunk, int idx, int prev, int neu)`: the 2.4 steps.
  - Read the stacks from `InventoryComponent$Hotbar.getInventory().getItemStack((short) slot)`.
  - Read `Ammo` from `EntityStatMap` via `chunk.getComponent(idx, EntityStatMap.getComponentType())`.
  - Read the Creative state from `Player.getGameMode()`.
- `Xbow.tick(Store st, Ref ref, PlayerRef pr, UUID u)`: the 2.5 steps.
  - Early exit when `S` has no entry for `u` (nearly every player, nearly every tick). Otherwise `fresh(s, u)` runs first, every tick.
  - Count arrows over `$Hotbar`, `$Storage` and `$Backpack` `getInventory()` slots, summing `getQuantity()` where
    `getItemId().equals("Weapon_Arrow_Crude")`.
- `Xbow.line(UUID u, int s, int lv, boolean next)`: the Stats page text or null (3.7).
- Every method catches `Throwable`, with one `FAILED_ONCE` warning per method like `AcroSys`. A failure never touches the inventory
  after a partial step, because of the pay-first order.

### 3.5 `XbowSlotSys` (new `EntityEventSystem`, the `SmeltSys` pattern at 0.4.3 line 6137)
- ctor `super(InventorySetActiveSlotEvent.class)`; `getQuery()` returns `Player.getComponentType()`.
- `handle(...)`: cast, return unless `getInventorySectionId() == -1`, get `PlayerRef` (return if null), then call `Xbow.onSlot(...)`.
  The whole body is in try/catch with a `FAILED_ONCE` warning.
- Register it in `setup()` next to `CraftSys` / `SmeltSys` (0.4.3 lines 7524-7539):
  `getEntityStoreRegistry().registerSystem(new {PKG}.XbowSlotSys());`

### 3.6 `AcroSys` hook (0.4.3 lines 4435-4474)
Right after `{PKG}.Brew.tick(u, store, cb, ref, dt);` add `{PKG}.Xbow.tick(store, ref, pr, u);`. It runs every tick, outside the
`AcroCfg.ENABLED` block, so turning Acrobatics off does not turn this off. No new ticking system is needed.

This spot is **before** `AcroSys`'s once-per-second gate (`if (s[14] < 1.0) return;`), on purpose: the 3-tick timing needs every
tick. The epoch check that calls `Perks.switched` and the `Perks.tick` refresh of `Xbow.ON` sit **after** that gate, so they can lag
up to 1 s. That is why `Xbow.tick` runs its own epoch check every tick and re-checks eligibility live before paying (2.2, 2.5). It
must never rely on `Perks.switched` or `Perks.tick` alone to invalidate a restore.

### 3.7 Level reward line, `/skills` page, and the other hooks
- **Level-up chat** (`SkillXp.gain4`, 0.4.3 lines 3311-3343): inside the `for (lv ...)` loop, right after the `SKILL LEVEL UP` line,
  when all of the following hold:
  - `lvOn`
  - `skill == SkillClass.slotOfClass("Archer")`
  - `XbowCfg.ON`
  - `XbowCfg.LEVEL >= 1`
  - `lv == (long) XbowCfg.LEVEL` (`lv` is a `long` in that loop)

  send `"  Unlocked: Crossbows stay loaded when you switch slots"` in `#ffc800`. After the loop, call `Xbow.refresh(u)` so the perk
  works at once instead of within 1 s. The result reads:
  ```
  SKILL LEVEL UP  Archery 4 -> 5   +500 coins
    Unlocked: Crossbows stay loaded when you switch slots
    next: Archery 6 at ... XP - /skills
  ```
- **Stats page** (`StatsPage.lines`, 0.4.3 lines 6567-6639): right after the class damage line (6620-6623), when
  `XbowCfg.ON && s == SkillClass.slotOfClass("Archer")`:
  - `!next && lv >= LEVEL` → now-line `"Crossbows stay loaded when you switch slots"`
  - `next && lv + 1 == LEVEL` → the "Level 5 adds" line with the same text

  The page's existing note "You are not an Archer right now - these boosts work while you are one" covers non-Archers. The 7-line cap
  still fits: max Health, class damage, this line.
- **`Perks.tick`** (per second, 0.4.3 line 3614): add `{PKG}.Xbow.refresh(u);`.
- **`Perks.switched`** (0.4.3 line 3604): add `{PKG}.Xbow.forget(u); {PKG}.Xbow.refresh(u);`.
- **`Acro.retainOnline`** (0.4.3 line 3875): add `{PKG}.Xbow.retain(online);`.
- **Ready log line and plugin description:** append `crossbows stay loaded at Archery <LEVEL> (<on|off>)`.

### 3.8 Threads
Everything runs on the player's world thread: the event handler, `AcroSys`, `Perks.tick` and `gain4`. The only other thread that
touches the maps is the ticker's 30-second prune (`retainOnline`), and `ConcurrentHashMap` covers it. `XbowCfg` fields are `volatile`
and written by `SkillCfg.load` (kit reload thread). No file I/O is added, and no lock is taken.

### 3.9 Build-time checks (add to the patch's asserts and to 0.4.4's API probe lists, the `B.probe(pool, c, m)` loops; 0.4.3 had them at lines 571/641)
Probe every call in 1.8:
- `InventorySetActiveSlotEvent#getInventorySectionId/getPreviousSlot/getNewSlot`
- `EntityStatMap#get(int)/setStatValue(int,float)`
- `EntityStatValue#get/getMax`
- `DefaultEntityStatTypes#getAmmo`
- `InventoryComponent#getCombined(ComponentAccessor,Ref,ComponentType[])` and the field `HOTBAR_STORAGE_BACKPACK`
- `InventoryComponent$Hotbar/$Storage/$Backpack#getComponentType`
- `ActiveSlotInventoryComponent#getActiveSlot`
- `ItemContainer#removeItemStack(ItemStack,boolean,boolean)/getItemStack(short)/getCapacity`
- `ItemStack#isEquivalentType(ItemStack)`
- `DeathComponent#getComponentType`

Also assert:
- `must("Weapon_Arrow_Crude")`
- `must("Weapon_Crossbow_Iron")`
- that every Assets.zip item starting with `Weapon_Crossbow_` has `Parent` = `Template_Weapon_Crossbow` (or is the template)
- that `Template_Weapon_Crossbow.Weapon.EntityStatsToClear` still contains `"Ammo"`
- that `Template_Weapon_Crossbow.Weapon.StatModifiers.Ammo` is exactly `[{"Amount": 6, "CalculationType": "Additive"}]` (the cap of
  6 the design hardcodes)
- that the `SwapFrom` root is still `Root_Weapon_Crossbow_Swap_From` and its `Interactions` is exactly `["Weapon_Crossbow_Swap_From"]`
- **the refund ladder itself.** Walk `Server/Item/Interactions/Weapons/Crossbow/Weapon_Crossbow_Swap_From.json` (read in memory from
  Assets.zip) and assert its shape as it is today (VERIFIED at review):
  - the root is `Type: Condition`, `RequiredGameMode: Adventure`, `Failed: {Type: ChangeActiveSlot}`
  - following `Next`, then `Failed` five times, gives exactly 6 `StatsCondition` nodes with `Costs == {"Ammo": k}` for k = 6, 5, 4,
    3, 2, 1 in that order
  - each of those nodes' `Next` is `ModifyInventory` with `ItemToAdd == {"Id": "Weapon_Arrow_Crude", "Quantity": k}` (the same k)
    and nothing else, and its `Next` is `{Type: ChangeActiveSlot}`
  - the last node's `Failed` is `{Type: ChangeActiveSlot}`
  - no node anywhere in the file has `Type` `ChangeStat` (or any other type not listed above). "Checks but does not spend" (1.3) holds.
- bump 0.4.4's `assert len(CFG_ROWS) == 154` to **159** (154 + the 5 `perk.archery.keepLoaded.*` rows), the same way 0.4.4 bumped
  0.4.3's 151. If round 6 ends on a different count, use that count + 5. `assert len(_absent) == 21` stays unchanged (3.3).

If Hytale changes the crossbow, the build then fails loudly instead of the perk going quiet. The ladder check matters most: the cap of
6, the 1:1 Crude refund and "the ladder does not spend `Ammo`" are what the anti-dupe argument (2.6) rests on.

---

## 4. Test plan (how Skyy sees it working; copy into TEST-CHECKLIST.md)
Setup: the Archer profile (e.g. 'Strawberry') in **Adventure** mode, one crossbow in hotbar slot 1, a sword in slot 2, and 20 Crude
Arrows (`Weapon_Arrow_Crude`, the only arrow a crossbow loads).

1. **Unlock.** `/skills xp archery 1175` (level 5 on the default curve). Chat shows `SKILL LEVEL UP  Archery 4 -> 5 +500 coins` and
   `Unlocked: Crossbows stay loaded when you switch slots`. `/skills` → Archery shows the line under "Boosts right now". At level 4 it
   showed under "Level 5 adds".
2. **Core.** Reload fully: counter 6, arrows 14. Scroll to slot 2: arrows go to 20 (vanilla). Scroll back to slot 1: within a blink
   the counter shows 6 and arrows 14. One click shoots at once, with no reload.
3. **Partial.** Shoot 2 (counter 4). Slot 2: arrows 18. Slot 1: counter 4, arrows 14.
4. **No free arrows.** Load 6 and go to slot 2 (arrows 20). Put all 20 arrows in a chest and go back to slot 1: counter 0, a normal
   reload is needed, and nothing is gained. Take 3 arrows back and repeat: counter 3.
5. **Two crossbows (go/no-go).** Iron in slot 1 loaded to 6, a More Crossbow Tiers Cobalt crossbow in slot 3, empty. 1 → 3: Cobalt
   shows 0. Load Cobalt to 2. 3 → 1: Iron 6. 1 → 3: Cobalt 2. At the end, arrows + loaded bolts = the starting total. Repeat the
   direct 3 → 1 → 3 switch 10 times. This is the one case where only the 3-tick count guards the restore (2.5). If arrows ever go
   missing, 0.4.5 does not ship as is (raise the delay default or apply F1).
6. **Crossbow leaves the slot.** Load 6 and go to slot 2. Move or drop the crossbow, or put it in a chest. Back to slot 1: nothing
   restored, arrow count unchanged.
7. **Gate.** A fresh Archer profile under level 5 behaves like vanilla. A Warrior profile holding a crossbow behaves like vanilla.
8. **Server Setup.** SkyWynn Menu → Mods → Skills → Parts → "Crossbows stay loaded" OFF (it asks to confirm): vanilla behavior. ON: it
   works again. Perks → "Crossbows stay loaded from Archery" = 10: the level-5 Archer loses it. Set 0: every Archer has it. Set back
   to 5.
9. **Fast hands (go/no-go).** Scroll back and click instantly, 10 times. At worst a reload starts. The count stays balanced, there
   are never two shots from one click, and the counter never goes above 6. Then the **quick flick**: load 6 and flick the scroll
   wheel hard across two or more slots at once, 10 times. Each time the arrow count must rise by exactly 6, never 12. A double
   refund would be a vanilla bug (2.9), but the perk would make it faster to repeat, so if it is ever seen, 0.4.5 does not ship until
   it is understood. Turn on Advanced → "Stay-loaded debug lines" to watch each keep and restore.
10. **Profile / relog / death / teleport.** Load 6 and go to slot 2, then each of: relog, die, `/hub`, switch profile and back. After
    each, slot 1 needs a normal reload and the 6 arrows are in the inventory. Nothing lost, nothing gained.
    **Switch during an armed restore:** set "Stay-loaded restore delay" to 20. Give a second profile a plain Iron Crossbow in slot 1,
    at most Archery 4 (or a non-Archer class), and 10 Crude Arrows. Use SkyyProfiles `islandOnSwitch=false` (or stand on the target
    island), so no world change wipes the state first. Turn on the debug lines. On the Archer profile, load 6, go to slot 2, scroll
    back to slot 1, then send `/profiles switch 2` as fast as you can (about 0.6 s at delay 20). If no "put back" line appeared before
    the switch, the restore was still armed. On the second profile the counter must stay 0 and its 10 arrows must stay 10 (2.5 epoch
    check). Set the delay back to 3.
11. **Two accounts.** A friend who is not an Archer at level 5 sees vanilla behavior while Skyy has the perk.
12. **If the restore does not stick (go/no-go)** (counter flashes 6 then 0, arrows gone): raise "Stay-loaded restore delay" to 6
    and repeat steps 2 and 5. Then report it; the fallback is section 5. Do not ship 0.4.5 on the default delay while this happens.

---

## 5. Fallbacks (only if section 4 shows a problem)
- **F1. The restore gets wiped** (step 12 still fails at delay 20). This would mean `Recalculate` runs less often than every tick.
  Re-apply once more on the tick after the restore if `Ammo` dropped to 0 without a shot. Or add the `SystemDependency(Order.AFTER,
  EntityStatsSystems$Recalculate)` ordering (2.5), guarded by try/catch at registration.
- **F2. The client shows a wrong counter** (the server value is right, but the HUD stays at 0). Send the value again one tick later.
  `setStatValue` records a change only when the value really differs, so the re-send has to write 0 first and then the paid value.
  This is UNTESTED and a last resort.
- **F3. Same feel without the restore:** a "fast reload" perk. It keeps vanilla unloading but shortens the 0.8 s `ReloadReady`
  windup, which needs item-variant content (like research/Swing-Speed-Spec.md's conclusion). It is much heavier and only an
  alternative if F1 and F2 both fail.

---

## 6. Open questions for Skyy (the build uses the default unless Skyy says otherwise)
1. **Level:** Archery **5** (your "lvl5 reward"). It is changeable in game (Perks tab). *Default: 5.*
2. **Archer only?** It works only while you are an Archer (like the class damage perk), with the crossbow allowed by SkyyClasses.
   *Default: yes.*
3. **Teleports:** kept loads are dropped on relog, death, profile switch **and** world change (`/hub`, `/island`). You reload once
   after a teleport; nothing is lost. Keep them across teleports instead? *Default: dropped (simplest, safest).*
4. **Shortbows too?** They have the same unload (1 drawn arrow). The perk could cover them by adding `Weapon_Shortbow_` to the item
   list, but that is untested. *Default: crossbows only.*
5. **Signature meter:** the big-arrow ability charge still resets on a switch, as in vanilla. Keep it too? *Default: no, bolts only.*
6. **Feedback:** a quiet click sound when the bolts go back in, or a one-time chat hint the first time it happens? *Default: none. The
   level-up line and the /skills page say it.*
7. **Existing Archers already at 5+** when 0.4.5 goes live: one chat line on their next join ("New Archery reward: ...")? *Default: no.
   /skills shows it.*
8. **Player toggle** in /settings to turn it off for yourself? *Default: no. Server owners have the part switch.*
9. **Teaser before level 5:** show "Level 5: crossbows stay loaded" on the Archery page at levels 1-3 too? *Default: no. It shows at
   level 4 under "Level 5 adds".*

---

## 7. Review notes (2026-09-25)

Eight findings were checked against `build_skyyskills_0.4.4.py` on disk, the release `HytaleServer.jar` (reflect.py, bc.py,
bcfull.py) and `Assets.zip`. The verdict is unchanged: **YES**.

| # | Finding (severity given) | Result | What changed |
|---|---|---|---|
| 7.1 | 0.4.4 line numbers in 3.1 drifted (medium) | **Applied.** Confirmed at +21 lines, and the file moved again during the review (+37 by the end, mtime 06:21). `Perks.switched` / `Perks.tick` drifted too (the finding missed those). All anchor texts are still present, each exactly once | Header and 3.1: every 0.4.4 line number removed. 3.1 now lists the literal anchor text, the method it sits in, and what uses it. The `rep` helper's count assert is the drift guard. 0.4.3 line refs are kept as context (0.4.3 is frozen) |
| 7.2 | `setActiveSlot` signature says `CommandBuffer` (low) | **Applied.** The declared type is `ComponentAccessor` (both overloads); `tick0` passes `InteractionContext.getCommandBuffer()`, and `CommandBuffer implements ComponentAccessor` | 1.3 wording. Also added a VERIFIED fact from the same bytecode: `setActiveSlot` returns early with no event when the slot does not change, and reads `previousSlot` from its own field |
| 7.3 | 3.9 omits the `len(CFG_ROWS) == 154` bump (low) | **Applied.** Assert confirmed after `CFG_ROWS`; the `_absent == 21` reasoning also re-checked (only rows missing from `DEFAULTS` count) | 3.9: bump to 159 (or round 6's final count + 5). 3.3 points to it |
| 7.4 | Profile switch during an armed restore pays from the new profile (high) | **Applied.** Confirmed in 0.4.4 `AcroSys.tick`: `Brew.tick` (and so `Xbow.tick`) runs before `if (s[14] < 1.0) return;`, while `Perks.epochChanged` → `Perks.switched` and `Perks.tick` run after it. PROFILES-CONTRACT's "Switch" row is one world-thread task, and `profile:busy` is set and cleared inside it, so a tick never sees busy. The repro works when no world change follows the switch (`islandOnSwitch=false`, or already on the island). **Severity note:** no item is created. The new profile pays 1:1 with its own arrows, and the old profile keeps its refund. So it is a gate bypass (an instant reload for an ineligible profile), not a dupe. Still a real break of 2.2 and 2.8, and the fix is cheap | 2.2 (cache never decides a payout), 2.3 (`epoch` field), 2.4 and 2.5 step 1 (`Xbow.fresh` epoch check on every slot event and every tick, using the existing `Perks.epoch(u)`: one bridge read, no lock, no I/O; baseline rule as in `Perks.epochChanged`; on a change it resets and sets `ON` false, no file load in the handler), 2.5 step 3 (live check before paying), 2.6 (two new rows), 2.8, 3.4, 3.6 (why the placement stays before the gate), test 10 (switch during an armed restore) |
| 7.5 | Payout does not re-check eligibility live (medium) | **Applied** (merged with 7.4). One correction: *lowering* `perk.archery.keepLoaded.level` grants the perk to more players. *Raising* it, a class change without an epoch bump, or a weapon-lock change are the revoking cases | 2.5 step 3: `Xbow.eligibleNow(u, itemId)` = 2.2 rules 1-4 uncached + `Xbow.allowed`, right before paying. It runs only once per restore; the epoch check before it guarantees `data(u)` is the already-loaded profile |
| 7.6 | Build asserts do not cover the SwapFrom ladder itself (medium) | **Applied.** Ladder read from Assets.zip: `Condition(Adventure)` → six `StatsCondition Costs{Ammo:k}` for k = 6..1 on the `Failed` chain → each `Next` is `ModifyInventory ItemToAdd{Weapon_Arrow_Crude, k}` → `ChangeActiveSlot`; no `ChangeStat`. The template's `Ammo` modifier is `+6 Additive`. Most ladder changes would fail safe (a spending ladder makes us record 0), but a different refund item or ratio would change the economics silently | 3.9: exact ladder walk, `ItemToAdd` ids and quantities, no-`ChangeStat` check, the +6 cap, and the root's `Interactions` list |
| 7.7 | Duplicate slot events could desync the single `pendSlot`; make 4.9 a gate (medium) | **Partly applied.** *Rejected: the idempotency guard.* Bytecode shows the engine cannot send a repeated or no-op event: `setActiveSlot` returns early when the slot is unchanged, and `previousSlot` is read from the live field before the write. So a repeated `(prev, new)` pair needs a real `(new, prev)` change in between, which the handler processes normally. One scalar `pendSlot` is also the right shape: only the active slot can be restored, every leave cancels it (2.4 A.4), and payment re-checks the active slot and stack. Even a wrong count could not mint anything, because every restored bolt is paid 1:1. *Applied: the gate.* The vanilla double-refund worry (2.9) is a different thing from duplicate events, and the perk would make such a loop faster | 1.3 (new VERIFIED fact), 2.9 (the double refund is a go/no-go gate; no duplicate-event guard needed), test 9 (quick-flick check, go/no-go) |
| 7.8 | Both timing guards share the 3-tick assumption; add a positive Recalculate signal (low) | **Partly applied.** *Rejected: a general positive signal.* It cannot be built with the public API: `StatModifiersManager` exposes only `recalculateEntityStatModifiers`, `queueEntityStatsToClear` and `scheduleRecalculate` (reflection), with no pending flag and no queue getter. The proposed "Ammo cap drops to 0 and comes back" signal exists only when returning from a non-crossbow slot, and the cap check already waits for exactly that. For crossbow → crossbow the cap stays 6, so there is nothing to watch. *Corrected claim:* the two guards do not fail "toward over-credit". The leaving read equals what vanilla's ladder refunded in that same moment, and an early restore is paid and then wiped. So a timing error can cost the player arrows, never give free bolts. *Applied: pre-launch gating* | 2.5 ("What leans on the tick count alone"), tests 5 and 12 are go/no-go before 0.4.5 ships |

**Final verdict (after review): YES.** Restore-after-unload is still the design, with no engine patch and no asset override. Every
restored bolt is paid 1:1 with a Crude Arrow, which now also holds across a profile switch (per-tick epoch check) and against a
stale eligibility cache (live check before paying). The build fails loudly if the crossbow's refund ladder changes. Not seen in game
yet: tests 5, 9, 10 and 12 decide the timing, the client feel, and go/no-go.
