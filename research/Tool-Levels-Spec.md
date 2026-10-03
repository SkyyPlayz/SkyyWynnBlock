# SkyyGear 0.2.2 "tool levels": build spec

> **Skyy's words win over this draft:** OPEN-QUESTIONS.md, "Q&A with Skyy 2026-10-02", the LOCKED 2026-10-02 TOOL LEVELS block
> (gate skills, crafted at your level, answers 1-4). Older locks that still apply are named where they bite.

*Written 2026-10-02 (spec writer, Opus); corrected the same night after the critic review (editor, Opus - every correction re-checked
against the scripts / bytecode first; what was applied or rejected is in section 16). Nothing is built. Sources, all read only: **B** =
`SkyyGear/build_skyygear_0.2.py` (the live SET pin), **B1** = `SkyyGear/build_skyygear_0.2.1.py` (still being built - its line numbers
are as of the 2026-10-02 22:19 file; 0.2.2 is a patch on top of the FINAL 0.2.1, so every hook below is named by class + method first),
**S** = `SkyySkills/build_skyyskills_0.4.12.py`, **T** = `SkyyTrees/build_skyytrees_0.2.5.py`, **C** =
`SkyyCollections/build_skyycollections_0.2.5.py`, `HytaleServer.jar` bytecode (release; javassist dumps of a scratch copy; "offset" = the
bytecode index in that method), `Assets.zip` (JSON copied into scratch, Parent chains resolved), and the read-only 0.7 PRE-RELEASE jar +
Assets.zip for section 2.5. Skyy's docs SkyyGear-Plan.md / SkyyGear-Stat-Catalog.md were only read.*

**Legend.** VERIFIED = seen in bytecode, Assets.zip or a live build script. INFERRED = likely, not proven. UNVERIFIED = needs the game
(stage 0 / in-game test). **PLACEHOLDER** = a number Skyy has not picked; every placeholder is a Server Setup row (section 9).

---

## 0. Plain words (for Skyy)

- **Which skill:** pickaxe + shovel check **Mining**, hatchet checks **Foraging**, hoe + sickle check **Farming**. A Lv 13 pickaxe needs
  Mining 13.
- **Too low:** the tool cannot break any block (stone, ore, logs, dirt, crops, grass). A popup says **"Requires Mining 13 (you: 9)"**.
  Nothing is lost: no crack, no drop, no XP. Hitting a mob with it stays normal (tools are not weapons). Creative mode is never blocked;
  admins can be let through with a switch (off by default; weapons have no such switch). Hoes and sickles can also be stopped from tilling /
  sickle-harvesting - question 2 (built, but switched off until you have tried it; a too-low sickle still hits mobs and still swings
  left / right).
- **Crafting:** tools come out at your skill level inside the material's range (Wood / Crude 1-13, Copper 10-18, Iron 15-23 ...) and roll
  a rarity like weapons (Rare, Legendary ...). Below the range you get the range's first level and a chat line telling you so.
- **Speed:** the tool's **level** sets how fast it breaks, not the material - a Lv 13 Crude pickaxe mines like a Lv 13 Copper one. A tool
  **never breaks slower than in vanilla**. At the first level of each material the main blocks break as in vanilla; a few tools are a
  little faster even there, because they are lifted onto the shared speed line (the Wood pickaxe works like the Crude one; the Crude and
  Copper hatchets and the Copper shovel are lifted). Example, Copper pickaxe on iron ore: Lv 10 = 8 hits (vanilla), Lv 13 = 5 hits, Lv 18
  = 3 hits. A better material adds a little (+3 % Copper ... +12 % Mithril). Hytale breaks blocks in whole hits, so a level does not
  change the hit count of every block - the tooltip shows the hits. The Goblins' Scrap pickaxe (Lv 10-17) follows the same line, so it
  gets much better on stone and dirt (stone 10 hits -> 3 at Lv 10).
- **Fortune:** every tool level adds +0.1 % double-drop chance (Lv 18 Copper about +1.9 %, Lv 49 Mithril about +5.5 %). Small next to
  your skill perk (up to 50 %) and your tree (20-45 %).
- **Reforge:** tools can be reforged now, on the same page, for the same costs; the rarity never changes. Pickaxe + shovel roll Mining
  Fortune, Mining Wisdom, Mining Speed; hatchet Foraging Fortune, Foraging Wisdom, Chopping Speed; hoe + sickle Farming Fortune and
  Farming Wisdom (your list, unchanged).
- **Name (question 1):** "Mining Speed" / "Chopping Speed" stay your names. Because gear swing speed is "not for now" (your earlier
  lock), the tool stat makes every hit break MORE - fewer hits per block, so you mine faster. Your Mining tree's Mining Speed still makes
  you swing faster, so players will see two "Mining Speed" lines that both speed mining up in different ways. The other option is to call
  the tool stat Mining Power / Chopping Power.
- A tool's Fortune and Wisdom count **while you hold it**.
- **Tools without the new level mark never lock you out (question 4):** they work at your level, up to their own level. That covers the
  tools you own today - but also tools from chests, mob drops, the Auction House and admin gives, so a Mining 1 player with a plain
  Mithril pickaxe still mines at full vanilla speed. Crafting a tool, or reforging one you have the level for, adds the mark. One Server
  Setup switch; off = those tools follow the level rule like plain weapons already do (and players can be locked out of tools they own).
- **Heavy Hatchet (question 5):** maxed, it now fells a log in one hit from an **Iron hatchet at Lv 20** (today only Thorium and better),
  or a bit earlier with a big Chopping Speed roll (Iron Lv 19 with +5 %, Copper Lv 18 with +16 %).
- **Sickle swings:** Hytale does not tell the server when a sickle swing harvests a crop, so sickle swings give no Farming XP today (that
  was already true). Question 3 asks to fix that in the next SkyySkills.
- Everyone gets **one chat line** about tool levels the first time it is on.
- Every number is in Server Setup -> Gear -> **Tools**.

---

## 1. The model

| Rule | Detail |
|---|---|
| Which items | The gathering tools of `TOOL_FAMILIES` (B:735, B1:816): `Tool_Pickaxe_`, `Tool_Shovel_` -> kind `mining`; `Tool_Hatchet_` -> `foraging`; `Tool_Hoe_`, `Tool_Sickle_` -> `farming` (`GearData.toolKind` B:4638, `kindFor` B:4647). 32 vanilla ids (VERIFIED Assets.zip): Pickaxe Crude / Wood / Copper / Iron / Thorium / Cobalt / Adamantite / Mithril / Onyxium / Scrap, Hatchet Crude / Wood / Copper / Iron / Thorium / Cobalt / Adamantite / Mithril / Onyxium, Shovel Crude / Copper / Iron / Thorium / Cobalt, Hoe Crude / Copper / Iron / Thorium, Sickle Crude / Copper / Iron / Steel_Rusty. Other `Tool_*` (Bark Scraper) stay kind `tool`, no gate. Tools stay **not gear** (`GearData.isGearMs` / `isGear` B:4601-4630 never take `Tool_`), so weapon code (`GearHit.judge` B:7632, `GearStats.totals` B:6585) never sees them. |
| Gate skill (LOCKED) | `GATE_BY_KIND` (B:720, B1:801): mining -> Mining, foraging -> Foraging, farming -> Farming. |
| Level | The stored `lvl` of the tool's SkyyGear document (0.2 already writes it on craft, B header (4)); a tool without a document reads the material table (`GearLevel.level` B:4835 = the band start). |
| Band | The shared `level.material` table (`GearLevel.band` B:4897): Wood / Crude 1-13, Copper 10-18 (LOCKED 2026-10-01: copper TOOLS keep 10-18, only copper armor starts at 1), Bronze / Iron 15-23, Thorium 20-28, Cobalt 25-38, Adamantite 35-43, Mithril / Onyxium 40-49, Scrap and Steel_Rusty (family rows B:887-888, start 10 -> 10-17). No new band rows. Scrap (the Goblin pickaxe) and Steel_Rusty (a sickle, no Specs) are NOT ladder points (section 3.2 rule 1). |
| Crafted level | Already built in 0.2 (`GearRoll.craftLevel` B:5824): the crafter's gate skill, raised to `level.gateFloor`, moved into the band. 0.2.2 only adds the 0.2.2 marker (section 7) and the rarity roll (section 6). |
| Gate floor | `level.gateFloor` (default 1, `GearLevel.floor` B:4935): a skill below 1 counts as 1, so a new player can use Lv 1 tools. Unchanged. |
| Under-level | `GearDefs.enforcedKind` (B:2781) answers true for mining / foraging / farming while `part.tools` and `tool.gate` are on (today ENFORCED_KINDS = combat + equipment, B:724, B1:805). That one change turns on the real gate line, the below-band craft note and `craft.belowBand=block` for tools (they all ask `enforcedKind`). Under-level = blocks refused (section 2). With `part.tools` on but `tool.gate` off, `GearView.gateLine` gets a tool branch (the old-tool line of section 8), never "(coming later)". |
| Creative | Never gated: creative breaking skips the damage event entirely (section 2.1 row 4), the break backstop skips game mode Creative, and the hoe / sickle marker (2.2) is never put on a player in Creative (the `Hoe_Till` root has a Creative settings branch, so creative players run the same root). |
| Staff bypass | **None exists today** (searched B and B1: the only permission check is `skyygear.admin` in `Gear.admin` B:2663, used by admin commands; weapons have no bypass). New row `tool.staffBypass`, default **off** like weapons: on = players with `skyygear.admin` are never blocked by a tool level - block hits, the backstop and the hoe / sickle marker alike. |
| Global switches | `part.gate` off (B:1826) = every gate passes, tools included (`GearGate.check` state 5). New `part.tools` off = 0.2 behaviour (tool gate "coming later", Normal tools, no tool stats). |

---

## 2. Enforcement hooks (bytecode proof)

### 2.1 Block damage with a tool in hand: `DamageBlockEvent`

Every tool swing that breaks blocks ends in `BreakBlockInteraction` (Assets.zip: `Pickaxe_Block_Break` = UseBlock then **BreakBlock**
`Tool: Pickaxe`; `Hatchet_Chop` and the hoe swings -> `Block_Break` = UseBlock then **BreakBlock**; `Shovel_Dig` selector HitBlock and the
sickle's not-ripe fallback -> `Block_Break_Adventure` = Condition Adventure then **BreakBlock**).

| # | Fact | Proof |
|---|---|---|
| 1 | Survival swing -> `BlockHarvestUtils.performBlockDamage(ownerRef, entityRef, pos, item, tool=null, toolId, matchTool, 1.0f, 0, false, ...)` | `BreakBlockInteraction#interactWithBlock` offsets 441-466 |
| 2 | -> `damageSingleBlock(..., durability=true, ...)` | `BlockHarvestUtils#performBlockDamage` (13 args) offsets 8-33 |
| 3 | Damage of the hit = the tool's `ItemToolSpec` power for the block's `Breaking.GatherType` (spec found only when spec quality >= block `Breaking.Quality`; a weapon or builder tool gets none) x scale 1.0 | `damageSingleBlock` 718-743 + 1061-1066; `getSpecPowerDamageBlock` 44-63 (weapon -> null), 64-69 (block quality), 112-139 (spec loop + quality check) |
| 4 | Creative never reaches it: `Player.getGameMode() == Creative` -> `performBlockBreak` directly (no DamageBlockEvent; BreakBlockEvent yes) | `BreakBlockInteraction#interactWithBlock` 377-435 |
| 5 | **Soft blocks** (crops, grass, flowers - `Gathering.Soft`): damage forced to 1.0 and scale to 1.0, then the SAME event below. **Fragile** blocks also pass the event first | `damageSingleBlock` 853-911 (soft), 1544-1561 (fragile check comes after the event) |
| 6 | No power and not soft (e.g. a hatchet on Mithril ore): "unbreakable" particles + incorrect-tool sound, return false - **no event** (nothing happens anyway) | `damageSingleBlock` 914-1060 |
| 7 | `new DamageBlockEvent(itemInHand, pos, blockType, currentHealth, damage)` is invoked **on the player's entity ref** (`ComponentAccessor.invoke(Ref, EcsEvent)`; the ref is the owning entity = the player) | `damageSingleBlock` 1194-1233; `BreakBlockInteraction#interactWithBlock` 304-324 picks the ref |
| 8 | `DamageBlockEvent` extends `CancellableEcsEvent`; fields itemInHand (final), targetBlock, blockType (final), currentDamage (final), damage; `getDamage` / `setDamage(float)` | javassist member list of `server.core.event.events.ecs.DamageBlockEvent` |
| 9 | Dispatch is **synchronous**: `CommandBuffer.invoke` -> `Store.internal_invoke` loops every matching `EntityEventSystem` and calls `handleInternal` in one pass | `CommandBuffer#invoke(Ref,EcsEvent)` 31; `Store#internal_invoke(CommandBuffer,EntityEventType,Ref,EcsEvent)` 24-136 (`handleInternal` at 116) |
| 10 | **Cancelled** -> `BlockSection.invalidateBlock(x,y,z)` (re-sends the block to clients) and `return false` | `damageSingleBlock` 1238-1264; `BlockSection#invalidateBlock` adds the position to `changedPositions` |
| 11 | Not cancelled -> `damage = event.getDamage()` (re-read after every handler), then `BlockHealthChunk.damageBlock(now, world, pos, damage)` | `damageSingleBlock` 1265-1270, 1527-1542 |
| 12 | Block health starts at **1.0**; each hit subtracts the damage; destroyed when health <= 0 (or within `MathUtil.EPSILON_FLOAT` of 0) -> `performBlockBreak` | `BlockHealth.<init>()` = this(1.0f, Instant.MIN); `NO_DAMAGE_INSTANCE` = 1.0 (clinit); `BlockHealthChunk#lambda$damageBlock$0` 12-19; `BlockHealth#isDestroyed`; `damageSingleBlock` 1544-1615 |
| 13 | Durability loss runs only at the very end, so a cancelled hit costs no durability (durability is OFF by default anyway, LOCKED 2026-09-30) | `damageSingleBlock` 2162-2179 |

**So a cancelled hit leaves no damage, no drops and no XP:** it returns (row 10) before `damageBlock` (no `UpdateBlockDamage` packet - that
is sent inside `damageBlock`), before `performBlockBreak` (no `BreakBlockEvent`, so SkyySkills, SkyyCollections and SkyyTrees never hear of
it), before durability. Hits-to-break = the smallest n with n x damage >= 1.0.

(Rows 10-12 and every offset in this table are the RELEASE jar. The 0.7 pre-release moves block health into `BlockHealthSection` but keeps
the event, the cancel and the re-read - section 2.5.)

**Second hook (backstop): `BreakBlockEvent`.** `performBlockBreak` (12 args) builds `new BreakBlockEvent(item, pos, blockType)`, invokes it
on the entity ref and, when cancelled, calls `invalidateBlock` and returns before the block goes and before any drop (offsets 35-99).
Paths that break without a damage event (creative - skipped by us; other mods calling `performBlockBreak` with a player and a held tool)
are refused there too. SkyyTrees' Tree Feller / Vein Burst extra breaks also come here, always with the same tool that just broke a block,
so they pass. The only other creator of the event is the F-pickup of a loose block: `BlockHarvestUtils#performPickupByInteraction`
builds `new BreakBlockEvent(null, pos, blockType)` (offsets 341-349, `aconst_null` as the item) - so `getItemInHand()` can be **null**
(VERIFIED: a jar-wide scan finds exactly these two `new BreakBlockEvent` sites, release and pre-release).

**The 0.2.2 systems** (one registerSystem per class; `EntityEventSystem`, query `Archetype.empty()` like `TreeDmgSys` T:3242):
- `GearToolHitSys` (DamageBlockEvent): returns at once when the event is already cancelled (SkyyIslands' guard may have run first - no
  popup then), when the entity has no PlayerRef, or when the item is not a gathering tool. Then `GearToolHit.onDamage(uuid, gameMode, e)`:
  gate (section 1) -> on fail `e.setCancelled(true)` + popup; on pass `e.setDamage(e.getDamage() x m)` with m from section 3.
  `handle()` only collects the PlayerRef UUID + game mode and calls `onDamage`. The popup needs a `PlayerRef` (`GearGate.popup` sends
  through `pr.getPacketHandler()`, B:5069-5081), so `GearToolHit.popup(uuid, ...)` resolves it with `Universe.get().getPlayer(uuid)` -
  exactly as `Gear.tell` (B:2699) and GearHitSys's projectile branch (B:8541) do - and sends nothing when that is null (player gone, bare
  JVM); the throttle map is written before the send, so the harness counts popups by the map (section 11 AD1).
- `GearToolBreakSys` (BreakBlockEvent): skips creative / non-players; (1) posts the tool bonus from `e.getItemInHand()` and pins it
  (section 4.2) - a **null** item (F-pickup) means "no change": no post, no pin, no backstop; (2) backstop: an under-level gathering tool
  cancels the break (no popup - the damage hook already showed one). Null is never a gathering tool, so F-pickups are never refused.

### 2.2 Hoe tilling

| Fact | Proof |
|---|---|
| The hoe's Secondary is root `Hoe_Till` (all four hoes, inherited from `Tool_Hoe_Crude`) -> interaction `Hoe_Till` = `Type: ChangeBlock` (Changes: Soil_Dirt / Grass / Mud / ... -> `Soil_Dirt_Tilled`, RequireNotBroken) then `ModifyInventory` durability -1 | Assets.zip `RootInteractions/Weapons/Hoe/Attacks/Till/Hoe_Till.json`, `Interactions/.../Till/Hoe_Till.json` |
| `ChangeBlockInteraction#interactWithBlock` fires **no event**: broken-item check (0-31), change map (123-154), `BlockOperations.setBlock` (198-218), sync data, sound | bytecode |
| `SimpleBlockInteraction#tick0` (its caller) fires none either: distance check, `resolveItemInHand`, `interactWithBlock` (548) | bytecode |

**Can it be refused server-side without desync?** Not by the server alone: there is no event to cancel, and `ChangeBlock` is a client
interaction (it has a packet, so the client predicts the tilled block); reverting the block afterwards would show it tilled and then pop
back. The only clean refusal makes **both sides** say no: SkyyTrees' **shipped** pattern (live since 0.2.3, deployed 2026-09-25, T
docstring "0.2.3 TreeSwing"; research/Swing-Speed-Spec.md section 2) - **its client side is still UNVERIFIED**: the T 0.2.3 header (l.75)
and 0.2.4 header (l.166) list "that the CLIENT swings faster too" as needing Skyy's test, the HANDOFF 2026-09-25 06:53 line says
"UNVERIFIED in game: the client really swings faster, no status icon, overrides win", and neither HANDOFF nor TEST-CHECKLIST records a
result. The pattern: a **hidden marker effect** on the player plus an override whose first step is an `EffectCondition`.
`EffectConditionInteraction` lives in `...interaction.config.none`, has `generatePacket`, and `firstRun` reads the active effects of
`entityTarget.getEntity(ctx, ctx.getEntity())` (offsets 25-41) - the target defaults to `InteractionTarget.USER` (constructor offsets
11-15; codec keys `EntityEffectIds`, `Match`, `Entity`), so the check reads the player even inside a `HitBlock` branch; `Match: None`
fails when a listed effect is present (offsets 164-191). VERIFIED server side; the client running it is INFERRED (stage 0 check b). Shape
(generated from Assets.zip at build time, never committed):

```
Server/Item/RootInteractions/Weapons/Hoe/Attacks/Till/Hoe_Till.json   (override, same path + id as vanilla)
  { "Settings": <vanilla Settings copied exactly, incl. the Creative branch>, "Interactions": ["Skyy_Gear_Till_Gate"] }
Server/Item/Interactions/SkyyGear/Skyy_Gear_Till_Gate.json
  { "Type": "EffectCondition", "Match": "None", "EntityEffectIds": ["Skyy_Gear_Tool_Lock"],
    "Next": "Hoe_Till", "Failed": { "Type": "Simple", "RunTime": 0.233 } }
Server/Entity/Effects/SkyyGear/Skyy_Gear_Tool_Lock.json   { "Duration": 3, "OverlapBehavior": "Overwrite" }  (no icon, no stats)
(sickle: NOT the root - generated copies of the two swing SELECTORS, section 2.3)
```

`GearToolFx.lock(u)` puts the marker on while the **main-hand** item (the hotbar's active slot) is a strict under-level hoe or sickle AND
the player is not in Creative AND not let through by `tool.staffBypass` (the `Hoe_Till` root's Settings have a `Creative` branch -
Cooldown `BlockInteraction_Creative`, `ClickBypass` - so creative players run the same root; without the skip an op in creative could not
till), and takes it off otherwise. Refresh points:
- `GearToolSlotSys` (`InventorySetActiveSlotEvent`, an `EcsEvent` with section / previous / new slot) - **only** when
  `getInventorySectionId() == InventoryComponent.HOTBAR_SECTION_ID`: the event fires from `ActiveSlotInventoryComponent.setActiveSlot`,
  and `InventoryComponent$Hotbar`, `$Utility` and `$Tool` all extend that class (VERIFIED), so utility and tools-section changes fire it
  too. Reading the hand inside the event is safe: `setActiveSlot` writes the slot at offset 17 and fires the event at 22-36.
- a **new** `GearToolInvSys` (`InventoryChangeEvent`, only when `getInventory() instanceof InventoryComponent$Hotbar` and the active
  slot's stack changed identity) - NOT the existing `GearFxInvSys`: its handler (B:9419-9429, comment "engine review 5: only an event of
  the ARMOR container runs the armor pass") returns for every container but armor, so hotbar changes never reach it, and it stays
  byte-identical.
- `GearTick` every second (refresh, like SkyyTrees `TreeSwing`) - the backstop for anything the two events miss.

A popup "Requires Farming 13 (you: 9)" is sent when the marker goes on (throttled), because a refused till itself reaches the server as
nothing. Row `tool.farmLock`, **default off** until stage 0 check b passed in game (question 2): the override files are in the jar either
way (assets cannot be switched at run time), but with the row off the marker is never put on and every till / sickle swing passes the
condition into the vanilla chain.

### 2.3 Sickle swings and F-harvest

| Path | Fact | Proof |
|---|---|---|
| Sickle swing on a **ripe** crop | `Sickle_Attack` -> swing -> Selector `HitBlock` -> `HarvestCrop` (RequireNotBroken). `HarvestCropInteraction#interactWithBlock` -> `FarmingUtil.harvest` (51) -> `harvest0`: `setBlock` to the after-harvest stage + `giveDrops`. **No cancellable event before the harvest.** | Assets.zip `Sickle_Swing_Left_Selector.json`; bytecode `HarvestCropInteraction#interactWithBlock`, `FarmingUtil#harvest`, `#harvest0` |
| ... the drops | `giveDrops` -> `ItemUtils.interactivelyPickupItem(playerRef, stack, pos, acc)` per drop -> `InteractivelyPickupItemEvent` (a `CancellableEcsEvent` with get/setItemStack) on the player. Cancelled = the item is neither given nor dropped (lost), so it is **no gate**; it is a usable but thin **signal** (section 14, question 3): the event holds ONLY the `ItemStack` (its one constructor is `(ItemStack)`; the position is a parameter of `interactivelyPickupItem`, not of the event) - no crop block, no position, so a listener cannot dedupe against F-harvest by position (`HarvestGate.claim` keys on world + `PlacedStore.key(x,y,z)`, S:8339 / S:9199 / S:9264), cannot skip placed crops and has no crop id. SkyyCollections already found that only `performPickupByInteraction` and `FarmingUtil.giveDrops` fire it (C:2789ff) and works around the missing position with a 2 s window opened by `UseBlockEvent$Post` (C:2788-2820) - which sickle swings never open. | `FarmingUtil#giveDrops` 65; `ItemUtils#interactivelyPickupItem` 0-27 |
| Sickle swing on a not-ripe crop / grass | `HarvestCrop` fails -> `Block_Break_Adventure` -> BreakBlock -> **DamageBlockEvent** (2.1) - gated like every block | Assets.zip |
| SkyySkills today | Sickle swing harvests pay **no Farming XP** and no double drop (S:743, the 0.1 note "Sickle-swing harvesting fires no event and is NOT counted") | S |
| F-harvest (ripe crops, berry bushes) | `UseBlockInteraction#doInteraction`: the block's interaction for the type (113-117), `UseBlockEvent$Pre` via `CommandBuffer.invoke` - cancellable (179-220), the block's root (`HarvestCrop`) pushed (234-237), `UseBlockEvent$Post` (245-265). SkyySkills pays it later (HarvestSys S:9639 + HarvestTask polling up to 2 s). | bytecode; S |

**Rules:** the F-harvest is a bare-hand harvest in vanilla (`doInteraction` reads the BLOCK's interaction, not the item's - so any item in
hand works; INFERRED for every item), so it is **never gated** by the held tool. An under-level sickle's swing harvest can only be
refused by the same marker pattern as the hoe - but **not at the root**:

- The root `Sickle_Attack` (`ClickQueuingTimeout 0.3`, `RequireNewClick false`) -> interaction `Sickle_Attack` = `Chaining` (left /
  right swing) -> `Sickle_Swing_*` -> `Sickle_Swing_*_Selector`, and each selector carries BOTH `HitBlock` (`HarvestCrop`, Failed
  `Block_Break_Adventure`) and `HitEntity` (`Sickle_Swing_*_Damage`) (Assets.zip). A root gate with a "swing that hits nothing" Failed
  branch would therefore also stop mob hits (contradicting section 0) and would wrap the chaining (R5).
- So the gate goes into **generated copies of the two selectors**, same ids as vanilla (`Sickle_Swing_Left_Selector`,
  `Sickle_Swing_Right_Selector`): every field copied exactly, only the `HitBlock` interaction list wrapped -
  `{"Type": "EffectCondition", "Match": "None", "EntityEffectIds": ["Skyy_Gear_Tool_Lock"], "Next": <the vanilla HarvestCrop entry>,
  "Failed": {"Type": "Simple"}}` (Failed = nothing; a not-ripe crop would be refused by 2.1 anyway). `HitEntity`, the swings and the
  root stay vanilla: a too-low sickle still hits mobs and still alternates left / right.
- Binding: all four sickles set `Swing_Left_Selector` / `Swing_Right_Selector` in their `InteractionVars` to an inline
  `{"Parent": "Sickle_Swing_*_Selector", ...}` that overrides only `RunTime` / `Selector` geometry (Crude: nothing), never `HitBlock`
  (Assets.zip, VERIFIED for Crude / Copper / Iron / Steel_Rusty) - so they inherit the gated `HitBlock` (INFERRED: Parent resolution
  against an overridden asset; stage 0 check b). The build stops if a vanilla sickle's var ever overrides `HitBlock`, or the selector /
  root shapes change. The start-up check reads each sickle's resolved selector from the live item map and logs "sickle gate active on N
  of 4 sickles" (and which `Hoe_Till` root is active), like SkyyTrees 3.6.
- Farming_Overhaul and AdvancedFarming (in the Mods folder, NOT enabled in the HUD mod world - its config.json lists only the Skyy mods +
  Saplings From Trees + More Crossbow Tiers) replace sickle files: the same start-up check shows when they win.

### 2.4 Popup throttle

- Text (Skyy's words): title **"Requires Mining 13 (you: 9)"** in the vanilla red (`GearDefs.C_BAD`), body "<Copper Pickaxe> is Lv 13 - it
  cannot break blocks yet." (hoe / sickle: "... cannot till or harvest yet."), item icon = a metadata-free `new ItemStack(id, 1)` (the UI
  rule), style Warning - exactly the `GearGate.popup` call (B:5069: `NotificationUtil.sendNotification`).
- Own throttle map `GearToolHit.POPPED` (UUID -> last ms) so weapon popups (B:5069, fixed 1.5 s) stay byte-identical; window = row
  `tool.popupMs` (1500 ms, shown in seconds). A pickaxe swings every 0.25-0.35 s and a shovel's selector can hit several blocks per
  swing, so one popup per window is the most a player sees.
- The player comes from `Universe.get().getPlayer(uuid)` (2.1); null = no popup, the block still holds.
- The player switch `gear.blockedPopup` (existing, `Gear.notifyOn`) turns the popup off; the block stays.

### 2.5 The 0.7 pre-release (Skyy: "wait for 0.7")

Diffed against the read-only pre-release `HytaleServer.jar` + `Assets.zip` (research/PreRelease-Compat-Audit-1002.md does not cover these
hooks):

| What | 0.7 pre-release |
|---|---|
| `DamageBlockEvent`, `BreakBlockEvent`, `InteractivelyPickupItemEvent`, `InventorySetActiveSlotEvent` | member lists identical |
| Event creators | the same sites: `damageSingleBlock` (now offset 1207), `performBlockBreak` 35, `performPickupByInteraction` 341 (still `aconst_null`), `ItemUtils.interactivelyPickupItem` 0, `setActiveSlot` 22 |
| `damageSingleBlock` | the event is still built (1207-1220), a cancel still calls `invalidateBlock` and returns (1253-1273), `getDamage` is still re-read (1280) |
| Block health | moved from `BlockHealthChunk` to `BlockHealthSection` (`getHealth(III)` 1202, `damage(IIIFInstant)` 1551, static `BlockHealth.isDestroyed(F)` 1583, `ChunkSection.markNeedsSaving` 1558) - section 2.1 rows 10-12 offsets are release-only; 0.2.2 calls none of these |
| `applyItemDurabilityLoss` | gained an `ActiveSlotInventoryComponent` argument (0.2.2 does not call it) |
| Creative branch | `BreakBlockInteraction#interactWithBlock` still sends Creative to `performBlockBreak` (offsets moved by 2) |
| Assets | `Block_Break`, `Block_Break_Adventure` and `Hatchet_Chop` gained a `Trigger_Explosion_State_Generic` step (0.2.2 overrides none of them); the `Hoe_Till` and `Sickle_Attack` roots + interactions, both sickle selectors and both swings are byte-identical, so the farm-lock shape asserts pass; the four hoe items are identical and the four sickle items change only their `Swing_*_Effect` vars (sound), their selector vars are unchanged |
| Tool Specs | unchanged for every ladder gather type and all 32 tools; NEW gather types `Metals` (32 blocks; tools 0.001, Mithril pickaxe / hatchet 0.5 / 0.05) and `GoblinMetal` (2 blocks; Iron pickaxe 0.34, Thorium and up 0.5) - off the ladder, so m = 1 (vanilla) until a ladder row is added (section 13 Waits) |

---

## 3. Level -> breaking power

### 3.1 Where it is applied: the hit's damage

`GearToolHit.onDamage` multiplies the event: `e.setDamage(e.getDamage() x m)`. It works per stack (the event's own `itemInHand` = the
exact tool that hit, row 7 above) and per block type (`e.getBlockType().getGathering().getBreaking().getGatherType()`; soft and
gather-less blocks get m = 1).

**m** = target power / the tool's own vanilla power for that gather type (read from `item.getTool().getSpecs()` exactly like
`getSpecPowerDamageBlock` does - NOT from `getDamage()`, which may already carry SkyyTrees' bonus):

> base = vanilla + (max(vanilla, L(family, gatherType, effLevel) x matBonus) - vanilla) x tool.power.strength
>
> target = base x (1 + power roll %)          (m = target / vanilla; the roll = stat `mpow` / `cpow`, section 5)

- **L(family, gatherType, level)** = the **power ladder** (3.2). **matBonus** = 1 + `tool.matBonus` % x the band's first level (0.3:
  Copper +3 %, Iron +4.5 %, Mithril +12 %; a band starting at Lv 1 gets none - the same rule as 0.2.1 `GearBase.bonus`, B1:6546).
- **Never below vanilla** (the max): no tool, old or new, ever breaks slower than today. Off-tool gather types (a pickaxe on wood, a hatchet
  on stone, SoftBlocks, Benches) keep m = 1.
- `effLevel` = the tool's level, or for an old tool min(its level, your skill) (section 7).
- The power roll (`mpow` / `cpow`, shown as Mining Speed / Chopping Speed by default - question 1; section 5) multiplies on top, so it
  works in both `tool.power` modes and at any strength; `tool.power=vanilla` = strength 0.
- Computed per call from the cached ladder (3.2) and the live rows; the cache is keyed on the config epoch, which the tooltip signature
  (`GearView.sig`) already includes, so a Server Setup change re-renders the "Breaks in" line too.

**Composition with SkyyTrees `TreeFx.dmgBonus` (PROVEN order-free).** `TreeDmgSys` (T:3242-3265) is an `EntityEventSystem` on the same
`DamageBlockEvent`, query `Archetype.empty()`, no dependencies, returns when cancelled, and does `e.setDamage(e.getDamage() * (1.0 + b))`
(T:3263) with b = Heavy Pick on rock + ore / Heavy Hatchet on Woods (`dmgBonus` T:2587). Both systems multiply the **same float** of the
**same event object** inside one synchronous dispatch (2.1 rows 9 + 11), and the engine reads it once after all handlers, so the result is
vanilla x (1 + b) x m whichever runs first. A cancel by either is final. Neither ever sets an absolute value. (SkyyIslands' guard only
cancels.)

**Composition with the +40 % swing ceiling.** Power changes hits per block; SkyyTrees' Mining Speed / Chopping Speed change seconds per
swing (40 hidden tier effects, 0.35 s -> 0.25 s, T "0.2.3 TreeSwing"). They multiply in time and never touch each other. The first hit
lands 0.133 s into a pickaxe or hatchet swing (Assets.zip `Pickaxe_Mine` 0.083 s + 0.05 s), so time per block = 0.133 + (hits - 1) x
swing. The ceiling only matters for one-hit blocks, where more power does nothing and only swing speed helps.

### 3.2 The ladder ("same level ~ same speed across materials", never below vanilla)

Per tool family and its main gather types: Pickaxe -> Rocks, VolcanicRocks, OreCopper, OreIron, OreSilver, OreGold, OreThorium,
OreCobalt, OreAdamantite, OreMithril, Soils; Hatchet -> Woods; Shovel -> Soils. **Built at run time, not at build time** (several inputs
are live Server Setup rows): the vanilla points come from the live Item asset map at start (the same `getTool().getSpecs()` that
`getSpecPowerDamageBlock` reads, so a Hytale balance patch is picked up) for the built-in list of vanilla material tools only (a modded
`Tool_Pickaxe_*` never becomes a point); their x positions are the live band starts (`GearLevel.band`, the editable `level.material`
table); `tool.power.growth`, `tool.ladder.*` overrides, `tool.matBonus` and `tool.power.strength` are applied when the ladder is (re)built
or per call, cached on the config epoch. The build only asserts that the default inputs give the table below. A
`tool.ladder.<Family>_<GatherType>` row replaces that ladder; it may also name a gather type that is not on the list (e.g. 0.7's
`GoblinMetal`, section 2.5) as long as a vanilla tool of that family has it in its Specs - that gather type then joins the family's main
gather types.

1. A point at each material's band start = that material's vanilla power (the best one when two start together: Crude / Wood at 1,
   Mithril / Onyxium at 40). **Only the craftable material tools are points** (Crude, Wood, Copper, Iron, Thorium, Cobalt, Adamantite,
   Mithril, Onyxium): the **Scrap** pickaxe (a Goblin Miner drop, family row Scrap start 10, B:887) and the **Steel_Rusty** sickle (no
   Specs) are excluded. The ladders below only come out with Scrap excluded - with it, the Lv 10 point would be
   OreCopper 0.334 (not 0.25), OreIron / Silver / Gold 0.167 (not 0.125), OreThorium / Cobalt 0.1 (not 0.084), OreAdamantite 0.071 (not
   0.0635), OreMithril 0.056 (not 0.0533), and a Lv 10 Copper pickaxe would take 3 / 6 hits on copper / iron ore instead of 4 / 8.
   A Scrap pickaxe still uses the Pickaxe ladder at its own level with its own +3 % bonus (band start 10), never below its own vanilla:
   Lv 10 = stone 10 -> 3 hits, dirt 10 -> 2 hits, copper ore 3 and iron ore 6 hits (its vanilla 0.334 / 0.167 stay above the ladder
   there); by Lv 15 stone 2, copper ore 2, iron ore 4 - a Copper pickaxe of the same level, as "same level ~ same speed" says.
2. Points never go down, and each point is at least the previous one x (1 + `tool.power.growth` x levels between) - default 3 % a level.
   This fills vanilla's flat stretches (vanilla Wood and Copper hatchets are both 0.2; the Copper shovel 0.2 is even below Crude 0.4).
3. Straight lines between points; past the last point + 3 % a level.

**Never below vanilla; equal at a material's first level for the main blocks - not for every block.** Of the 113 band-start cases (9
pickaxes x 11 gather types + 9 hatchets + 5 shovels, Scrap excluded) 93 keep exactly their vanilla hit count and **20 get faster**; none
is slower anywhere (float model of 2.1 row 12 over every level of every band, Scrap included). The 20 (vanilla -> ladder hits):
- Wood pickaxe, all 11 gather types (lifted to the Crude point): Rocks 10 -> 4, VolcanicRocks 30 -> 12, OreCopper 10 -> 8, OreIron /
  OreSilver / OreGold 15 -> 12, OreThorium / OreCobalt 18 -> 16, OreAdamantite 23 -> 20 (Quality 4 - a Wood pickaxe cannot mine it
  anyway), OreMithril 27 -> 24, Soils 10 -> 3.
- Onyxium pickaxe Soils 2 -> 1 (its own 0.5 sits under the shared Lv 40 point).
- Cobalt pickaxe VolcanicRocks 6 -> 5, OreAdamantite 8 -> 7, OreMithril 12 -> 10; Thorium pickaxe VolcanicRocks 6 -> 5; Copper pickaxe
  OreMithril 20 -> 19.
- Crude hatchet 7 -> 5, Copper hatchet 5 -> 4, Copper shovel 5 -> 2 (the three that show in the 3.3 table).

Causes: the 3 %-a-level floor (rule 2), the material bonus crossing a hit line, and shared band starts (Crude / Wood at 1, Mithril /
Onyxium at 40). The OreMithril cases never show in game: no block uses that gather type (Mithril ore is Rocks Quality 5; release and 0.7
Assets.zip).

Default output (growth 3 %, Scrap excluded; ladder level:power):

| Family / gather type | Ladder |
|---|---|
| Pickaxe Rocks | 1:0.25, 10:0.35, 15:0.5, 20:0.575, 25:0.661, 35:1, 40:1.15 |
| Pickaxe OreCopper | 1:0.125, 10:0.25, 15:0.5, 20:0.575, 25:0.661, 35:0.86, 40:1 |
| Pickaxe OreIron (= OreSilver, OreGold) | 1:0.084, 10:0.125, 15:0.25, 20:0.5, 25:0.575, 35:0.747, 40:1 |
| Pickaxe OreThorium (= OreCobalt) | 1:0.063, 10:0.084, 15:0.125, 20:0.25, 25:0.287, 35:0.5, 40:0.575 |
| Pickaxe OreAdamantite | 1:0.05, 10:0.064, 15:0.084, 20:0.125, 25:0.144, 35:0.25, 40:0.5 (only Quality 4 picks - Thorium and up - can mine it at all) |
| Pickaxe OreMithril | 1:0.042, 10:0.053, 15:0.063, 20:0.084, 25:0.097, 35:0.126, 40:0.25 (no block uses this gather type) |
| Pickaxe VolcanicRocks | 1:0.084, 10:0.12, 15:0.17, 20:0.196, 25:0.225, 35:0.34, 40:0.391 |
| Pickaxe Soils | 1:0.35, 10:0.5, 15:0.575, 20:0.661, 25:0.76, 35:1, 40:1.15 |
| Hatchet Woods | 1:0.2, 10:0.254, 15:0.3, 20:0.5, 25:0.575, 35:0.747, 40:0.86 |
| Shovel Soils | 1:0.4, 10:0.508, 15:0.584, 20:0.672, 25:0.773 (vanilla shovels stop at Cobalt) |

The **Quality gate stays the material's**: a Copper pickaxe (Rocks q2) never mines `Ore_Adamantite_Magma` (OreAdamantite q4) or
`Ore_Mithril_Stone` (Rocks **q5**), whatever its level (`getSpecPowerDamageBlock` 112-136). (Correction of the task's fact list: "any
pickaxe can mine any ore" is true only for Copper / Iron / Silver / Gold / Thorium / Cobalt ore.)

### 3.3 Hits per block (band start and cap; vanilla in brackets; seconds at the vanilla 0.35 s swing)

| Tool | Lv | Stone | Copper ore | Iron ore | Oak log | Dirt |
|---|---|---|---|---|---|---|
| Crude pickaxe | 1 | **4** (4) 1.18 s | **8** (8) 2.58 s | **12** (12) 3.98 s | off-tool | **3** (3) 0.83 s |
| Crude pickaxe | 13 | **3** (4) 0.83 s | **3** (8) 0.83 s | **5** (12) 1.53 s | off-tool | **2** (3) 0.48 s |
| Copper pickaxe | 10 | **3** (3) 0.83 s | **4** (4) 1.18 s | **8** (8) 2.58 s | off-tool | **2** (2) 0.48 s |
| Copper pickaxe | 18 | **2** (3) 0.48 s | **2** (4) 0.48 s | **3** (8) 0.83 s | off-tool | **2** (2) 0.48 s |
| Iron pickaxe | 15 | **2** (2) 0.48 s | **2** (2) 0.48 s | **4** (4) 1.18 s | off-tool | **2** (2) 0.48 s |
| Iron pickaxe | 23 | **2** (2) 0.48 s | **2** (2) 0.48 s | **2** (4) 0.48 s | off-tool | **2** (2) 0.48 s |
| Crude hatchet | 1 | off-tool | | | **5** (7) 1.53 s | off-tool |
| Crude hatchet | 13 | | | | **4** (7) 1.18 s | |
| Copper hatchet | 10 | | | | **4** (5) 1.18 s | |
| Copper hatchet | 18 | | | | **3** (5) 0.83 s | |
| Iron hatchet | 15 | | | | **4** (4) 1.18 s | |
| Iron hatchet | 23 | | | | **2** (4) 0.48 s | |
| Crude shovel | 1 / 13 | | | | | **3** (3) / **2** (3) |
| Copper shovel | 10 / 18 | | | | | **2** (5) / **2** (5) |
| Iron shovel | 15 / 23 | | | | | **2** (2) / **2** (2) |

(Crude hatchet Lv 1 = 5 hits, not 7: the Lv 1 point is the better of Crude 0.15 / Wood 0.2 - never below vanilla. Copper shovel = vanilla's
odd 0.2 lifted to the ladder.)

**Where the hit counts change** (level:hits):

- Crude pickaxe - stone 1-8:4, 9-13:3; copper ore 1-2:8, 3:7, 4-6:6, 7-9:5, 10-11:4, 12-13:3; iron ore 1-2:12, 3-4:11, 5-6:10, 7-9:9,
  10:8, 11:7, 12:6, 13:5; dirt 1-9:3, 10-13:2.
- Copper pickaxe - stone 10-14:3, 15-18:2; copper ore 10-11:4, 12-14:3, 15-18:2; iron ore 10:8, 11:7, 12:6, 13-14:5, 15-16:4, 17-18:3.
- Iron pickaxe - stone 2 all band (vanilla Iron, Thorium and Cobalt are all 2 too); iron ore 15-16:4, 17-19:3, 20-23:2; thorium ore 15:8,
  16:7, 17:6, 18-19:5, 20-23:4.
- Hatchets on logs - Crude / Wood 1-9:5, 10-13:4; Copper 10-15:4, 16-18:3; Iron 15:4, 16-19:3, 20-23:2.
- Thorium pickaxe Lv 20-28 - thorium ore 20-26:4, 27-28:3; adamantite ore 20-22:8, 23-26:7, 27-28:6. Mithril Lv 40-49: stone 1, thorium
  ore 2, adamantite ore 2 (already near the one-hit floor).

**With the tree and a roll** (all multiply): Copper pickaxe Lv 13 on iron ore: level 5 hits -> + max Heavy Pick (+40 %) 4 -> + a +16 %
Mining Speed (`mpow`) roll 3 (Lv 13 power rolls: Legendary 7-14, Fabled 7-16, Mythic 9-19 - `GearRoll.bounds` B:5689 with the default
rarity table B:628). Iron hatchet Lv 20 on oak: 2 hits -> + max Heavy Hatchet (+100 %) **1**. Copper hatchet Lv 18: 3 -> HH max 2 -> + a
+16 % Chopping Speed (`cpow`) roll 1 (Lv 18: Legendary 8-17, Fabled 9-19). (The first draft used +30 % rolls, which a Lv 13-18 tool
cannot roll.)

**Heavy Hatchet behaviour change (question 5).** Skyy's lock (2026-09-25): "Heavy Hatchet max is +100 % wood breaking power, so a top
hatchet (0.5 power) cuts a log in one hit" - in vanilla that is Thorium and better. With the ladder, a maxed Heavy Hatchet one-chops a log
from an **Iron hatchet at Lv 20** (2 hits before), and earlier with a Chopping Speed roll: the smallest roll that does it is Iron Lv 19
+5 %, Lv 18 +14 %, Lv 17 +26 %, Lv 16 +41 %; Copper Lv 18 +16 %, Lv 17 +28 %, Lv 16 +43 % (rolls reach Legendary 8-17 / Mythic 11-23 at
Lv 18, 5.2). Crude / Wood never (they would need +78 % at Lv 13). This follows "same level ~ same speed" (an Iron Lv 20 hatchet = a
Thorium Lv 20 one), but it moves Skyy's "top hatchet" line, so it is asked, not assumed.

**Why not smooth "+X % speed"?** Breaking is whole hits (2.1 row 12), so a small multiplier only shows when it crosses a 1/n line. A
random "sometimes one hit less" rounding would make the average smooth, but its result would depend on whether SkyyTrees multiplied first
(order is unspecified), and vanilla mining is fully predictable - so the multiplier stays deterministic and the tooltip shows the real
hit counts (section 8).

---

## 4. Base Fortune by level, and how bonuses reach SkyySkills

### 4.1 Base Fortune

> Fortune % = `tool.fortune.perLevel` (0.1) x effLevel x matBonus     (every gathering tool; hoes and sickles get Fortune only, no power)

| Material | Band start | Band cap |
|---|---|---|
| Crude / Wood | Lv 1: 0.10 % | Lv 13: 1.30 % |
| Copper | Lv 10: 1.03 % | Lv 18: 1.85 % |
| Iron | Lv 15: 1.57 % | Lv 23: 2.40 % |
| Thorium (highest hoe) | Lv 20: 2.12 % | Lv 28: 2.97 % |
| Cobalt | Lv 25: 2.69 % | Lv 38: 4.08 % |
| Adamantite | Lv 35: 3.87 % | Lv 43: 4.75 % |
| Mithril / Onyxium | Lv 40: 4.48 % | Lv 49: 5.49 % |

Same level ~ same Fortune; the better material a little more (Skyy 2026-10-01: "iron: a bit more Mining Fortune").

### 4.2 The bridge: source `"gear"` in `skill:bonus:<uuid>`

SkyyGear posts one source in the shared map SkyySkills already reads: `skill:bonus:<uuid>` (ConcurrentHashMap source -> unmodifiable Map,
exactly SkyyTrees' `postBonus` shape, T:2463) under the key **`"gear"`** (lower case like SkyyTrees' `"trees"`, T:2395; SkyySkills ignores
the key name). Value = only the held tool's keys, fractions: pickaxe / shovel `dd.mining`, `xp.mining`; hatchet `dd.foraging`,
`xp.foraging`; hoe / sickle `dd.farming`, `xp.farming`. dd = base Fortune (4.1) + Fortune roll / 100; xp = Wisdom roll / 100. Zeros
are left out; an empty map removes the source (T:2468 pattern). Values only while the tool's gate passes (strict tools) or always (old
tools at their effective level).

**How SkyySkills uses it (VERIFIED, S, no change needed):** `SkillBonus.sum` (S:5685) adds the key over every source; `xpBonus`
(S:5710) clamps 0..5 and `boost` (S:5721) pays the fraction by chance; `dd` (S:5741) clamps 0..1; `Perks.chanceU` (S:6663) = level perk
(level x `perk.<skill>.doubleDropPerLevel` 0.005) + dd, capped at `perk.doubleDropMax` (S:11328, default 1.0). `breakDouble` (S:6926) /
`harvestDouble` (S:6938) read it **at award time**.

**Event order - why the value is the tool that broke the block (PROVEN):**

1. SkyySkills `BreakSys` (S:9599-9626) handles `BreakBlockEvent` synchronously and only queues the award: `w.execute(new BreakTask(...))`
   (S:9626). `BreakTask.run` (S:9180ff) reads `skill:bonus` (XP boost + double drop).
2. `World#execute` only offers the task to `taskQueue` (offsets 41-46). `World#consumeTaskQueue` polls until the queue is empty - tasks
   added while it runs are run in the same pass, first in first out (offsets 9-110). `World#tick` = `consumeTaskQueue` (49) ->
   entity store tick (67) -> chunk store tick (106) -> `consumeTaskQueue` (124). So BreakTask never runs inside the event.
3. `GearToolBreakSys` writes `"gear"` from `e.getItemInHand()` (the exact stack the engine passed down, `performBlockBreak` 35-42) inside
   the same synchronous dispatch (2.1 row 9) - before BreakTask can run, whichever system runs first. **A null item = no change** (no
   post, no pin): the F-pickup of a loose block builds its BreakBlockEvent with a null item (`performPickupByInteraction` 341-349), and
   reading null as "no gathering tool" would wipe the held tool's source for the pin window - the F-pickup's BreakTask reads the source
   as it is, i.e. the tool in hand ("counts while you hold it", step 5).
4. **Pin**, so nothing replaces it before BreakTask: the handler bumps `GearToolFx.PIN[u]` and queues `GearToolUnpin` with
   `world.execute`; its first run re-queues itself once, its second run lowers the pin and re-posts from the hand. Every task queued in
   that dispatch (BreakTask included) was offered before the second hop, so by (2) it has run. While pinned, the hand refreshes (GearTick,
   slot / inventory events) skip that player. Nested breaks (Tree Feller: one BreakBlockEvent per log, all with the same tool) just count up.
   If `world.execute` throws (`World#execute` refuses tasks while the world is closing, offsets 0-40), the pin is dropped at once.
5. **F-harvest:** HarvestTask pays 100 ms - 2 s later (S:9233ff polling); it reads the source as it is then = the item in hand then
   (refreshed at once on slot change, and every second). Rule for players: "a tool's Fortune and Wisdom count while you hold it". Felled
   logs that SkyySkills credits later (tree physics) follow the same rule.

**Removed / recomputed:**

| When | What | Where |
|---|---|---|
| The tool leaves the main hand (slot change, moved, dropped) | Re-post from the new hand item (no gathering tool = source removed) | `GearToolSlotSys` (InventorySetActiveSlotEvent, hotbar section only), the new `GearToolInvSys` (InventoryChangeEvent of the hotbar - `GearFxInvSys` B:9419-9429 only ever handles the armor container), `GearTick` (B:9560) each second - all skip while pinned (2.2) |
| Level up / skill or config change | Recompute (gate and Fortune follow the level) | `GearTick` (it already re-reads levels: `GearGate.refresh`) |
| Profile switch | Remove while `profile:busy:<uuid>` is set; recompute after the epoch changes (PROFILES-CONTRACT rules 3-5: SkyyProfiles swaps the inventory) | `GearTick` |
| Logout | Remove our source (the shared map stays - other mods post in it), forget pins / caches | `GearByeB.accept` (B:9478, PlayerDisconnectEvent) |
| Shutdown | Remove our source for everyone still posted | plugin shutdown |
| `part.tools` off | Remove for everyone at the next tick | `GearTick` |

### 4.3 Totals against the double-drop cap (economy)

| Skill | Level perk Lv 50 / 100 | Tree max (T:746-790) | Tool level max | Tool roll max (Mythic) | Total Lv 50 | Total Lv 100 | After the cap (100 %) |
|---|---|---|---|---|---|---|---|
| Mining | 25 / 50 % | 20 % (Mining Fortune) | 5.5 % (Mithril Lv 49) | 13 % | 63.5 % | 88.5 % | 88.5 % |
| Foraging (trunks only, `perk.foraging.doubleDropOnly=_Trunk`) | 25 / 50 % | 40 % (Foraging Fortune 20 + Fortune II 20) | 5.5 % | 13 % | 83.5 % | 108.5 % | 100 % |
| Farming | 25 / 50 % | 45 % (Farming Fortune 25 + Fortune II 20) | 3.0 % (Thorium hoe Lv 28) | 10 % (Mythic at Lv 28) | 83 % | 108 % | 100 % |

Mid game (skill 20, Mining Fortune tree 5, a Rare Lv 20 Iron pickaxe with a +3 % roll): 10 + 5 + 2.1 + 3 = **20.1 %**. The tool share stays
small; Foraging and Farming reach the cap only with a maxed tree, the best tool and a Mythic roll: at skill **84** for Foraging (40 + 5.49 +
13 + 0.5 per level) and **85** for Farming (45 + 2.97 + 10 + 0.5 per level); Mining never does (88.5 % at 100). Recommendation: keep the
cap at 100 %.
Wisdom: tree 15 % + tool roll up to 13 % = up to +28 % gathering XP, multiplied with the pacing boost of the next SkyySkills (x3 to Lv 10
-> x1.5 by Lv 20, answer 4 - a separate build, only a dependency here).

---

## 5. Modifiers

### 5.1 New STATS rows (appended after the last row, so every existing index stays)

| key | Label | Slot letter | Unit | Max at 100 % | Weight | Live | Applied as |
|---|---|---|---|---|---|---|---|
| `mfort` | Mining Fortune | `m` | % | 10 | 10 | 1 | `dd.mining` + v / 100 |
| `mwis` | Mining Wisdom | `m` | % | 10 | 10 | 1 | `xp.mining` + v / 100 |
| `mpow` | Mining Speed (question 1) | `m` | % | 30 | 10 | 1 | breaking power x (1 + v / 100), Rocks / VolcanicRocks / Ore* / Soils only |
| `ffort` | Foraging Fortune | `h` | % | 10 | 10 | 1 | `dd.foraging` |
| `fwis` | Foraging Wisdom | `h` | % | 10 | 10 | 1 | `xp.foraging` |
| `cpow` | Chopping Speed (question 1) | `h` | % | 30 | 10 | 1 | breaking power on Woods only - blocks only, never mobs (Heavy Hatchet hard rule) |
| `afort` | Farming Fortune | `f` | % | 10 | 10 | 1 | `dd.farming` |
| `awis` | Farming Wisdom | `f` | % | 10 | 10 | 1 | `xp.farming` |

The keys name the mechanism (power) and are saved in item documents, so they never change; the label is the only thing question 1
decides (a one-line build change either way). All PLACEHOLDERS (the existing `stat` table, Server Setup -> Gear -> Stats). Slot letters:
`m` = Mining tools (pickaxe, shovel), `h` = hatchet, `f` = Farming tools (hoe, sickle) - by the document's kind (`GearData.kindFor`).
Build asserts to update: the letter regex
`[wsae]` (B:714) -> `[wsaemhf]`; "live stats = SPEC_KEYS[:22]" (B:717) -> + the 8 tool keys; `S_KEYS == SPEC_KEYS + LATER_KEYS` -> + TOOL_KEYS.

### 5.2 The roll code (existing, B)

- `GearRoll.allowed(i, slot)` (B:5662) answers false for slot 3 (tools) today. New: `GearRoll.pool(slot, id)` (B:5673) uses, for slot 3,
  the letter of the tool's kind; tool letters never match weapon / armor / equipment slots, and weapon letters never match tools.
- `pool` also skips the tool rows while `part.tools` is off (they would do nothing - Skyy's lock 2026-09-30 "if it's not in the game yet,
  don't leave it in the reforge list"; shown grey "(off on this server)" like Charged Attack Damage, `GearView.suffix`).
- Count = the rarity's modifier count (Normal 1, Unique 2, Rare 3 ...) capped by the pool (`rollMods` B:5708): pickaxes / hatchets carry
  all 3 stats from Rare up, hoes / sickles both stats from Unique up; above that, rarity only makes the rolls stronger.
- Value = `GearRoll.bounds` (B:5689): max x rarity low..high % x level factor (`GearLevel.factor` B:4867: 25 % at Lv 0 -> 100 % at Lv 40),
  whole numbers, at least 1:

| Level | Fortune / Wisdom (max 10) | Mining / Chopping Speed = power (max 30) |
|---|---|---|
| 1 | Normal 1-2 ... Mythic 2-3 | Normal 2-5 ... Mythic 5-10 |
| 13 | Normal 1-3, Rare 2-4, Legendary 2-5, Mythic 3-6 | Normal 4-9, Rare 6-12, Legendary 7-14, Mythic 9-19 |
| 18 | Normal 2-4, Rare 2-5, Legendary 3-6, Mythic 4-8 | Normal 5-11, Rare 7-14, Legendary 8-17, Mythic 11-23 |
| 28 | Normal 2-5, Rare 3-6, Legendary 3-7, Mythic 5-10 | Normal 7-14, Rare 9-19, Legendary 10-22, Mythic 14-30 |
| 40+ | Normal 3-6, Rare 4-8, Legendary 5-10, Mythic 6-13 | Normal 9-18, Rare 12-24, Legendary 14-29, Mythic 18-39 |

### 5.3 Name: Skyy's "Mining Speed" / "Chopping Speed" by default (question 1 - settle before the build)

What Skyy locked, all of it:
- Answer 3 (2026-10-02): the reforge pool is "Mining Fortune, Mining Wisdom, **Mining Speed**" and "Foraging Fortune, Foraging Wisdom,
  **Chopping Speed**". Answer 2 calls the level effect "breaking **speed**".
- R9 (OPEN-QUESTIONS, "keep all the small live defaults"): "**no sickle / gear swing-speed for now**" - so gear cannot make swings
  faster; the only way a gear stat speeds mining up is more damage per hit (fewer hits per block).
- Catalog / Plan: lock 31 **Breaking Power** - "Add. Lets you mine harder blocks" (SkyyGear-Stat-Catalog.md:167; Plan l.113) = the
  tool's Quality tier, a different thing; lock 32 **Mining Speed** - "increases pick swing speed" (the SkyyTrees node); lock 33 **Pick
  Breaking Damage** - "damage to blocks only, not mobs; open: how Hytale decides pick damage vs hits-to-break" (Plan l.115). The tool stat
  is lock 33's mechanism, and section 2.1 answers lock 33's open point (each block has 1.0 health, hits = the smallest n with n x damage
  >= 1).

So the build ships **Skyy's labels** with the power mechanism: "Mining Speed: +12% - fewer hits per block" / "Chopping Speed: +12% -
fewer hits per block". Downside (why the first draft renamed it): the Mining tree's "Mining Speed" node already means faster swings, so
two "Mining Speed" lines exist that speed mining up in different ways (they multiply: 3.1). Alternatives for question 1: "Mining Power" /
"Chopping Power" (the first draft's pick - but it sits right next to lock 31's "Breaking Power", which means mining harder blocks), or
lock 33's own "Breaking Damage". Gear "Mining Speed" as faster swings is not an option now (R9 lock; it would also need a SkyyTrees build,
share the +40 % ceiling and do nothing once the tree gives +40 %).

---

## 6. Reforge + craft

| Item | 0.2.2 |
|---|---|
| Reforge page list | `GearForge.rows` (B:7144) adds gathering tools (today `isGear` only). |
| Refusal | `GearForge.refuse` (B:7197): the tool line (B:7200 "Tools get their own modifiers with gathering gear - they cannot be reforged yet.") goes while `part.tools` and `tool.reforge` are on; texts say "weapon, armor piece or tool". |
| A tool without a document | `GearData.effective` (B:5986, today a legacy document only for gear) also answers the in-memory legacy document (`GearData.legacy` = `base(kindFor(id), 0, true, "legacy")`, Normal) for a plain gathering tool while `part.tools` is on - so gate, tooltip and reforge all see one. The reforge writes it (the LOCKED "old gear stays plain until reforged" rule) with 1 modifier. |
| Rarity | Kept (`GearRoll.reforge` B:5917 never changes `r`). |
| Level | Kept (`stampIfMissing` B:5910 stamps a missing `lvl` with the level it reads now). The 0.2.2 marker is written only when the reforging player meets that level (section 7); an old tool reforged by a lower player stays an old tool and its new rolls use its effective level (so a low player gets no stronger rolls from an old high tool). |
| Cost | `cost.reforge` by rarity (base + per level x level) x row `tool.reforgeCost` (100 %). Coins taken first, refunded on failure (unchanged `GearForge.reforge` B:7215). Smithing XP from `xp.reforge` (unchanged). |
| Crafting rarity | `GearRoll.craftDoc` (B:5900) rolls tools like weapons while `tool.craftRolls` is on: craft odds column (Normal 60 / Unique 25 / Rare 10 / Legendary 4 / Fabled 1 / Mythic 0) + the Smithing step-up (`smith.perLevel`, `smith.cap`), never above `craft.maxRarity` (Fabled). Modifiers from the family pool. Off = Normal, no rolls (0.2). |
| Crafted level | Unchanged (`craftLevel` B:5824) + the 0.2.2 marker. Both craft paths (vanilla bench `GearCraftSys` -> `GearCraftTask` -> `craftDoc`; SkyySacks `/craft` -> `gear:fn:roll` mode 8 -> `craftDoc`) - no SkyySacks change. |
| Below the band | Now that the gate is enforced, `GearRoll.craftNote` (B:5842) prints "Made at Lv 10 (the lowest level of Copper gear) - you need Mining 10 to use it (you: 4)." for tools too, and `craft.belowBand=block` refuses tool crafts at vanilla benches (`blockWhy` B:5880, both ask `enforcedKind`). Default stays `min` (make it at the band start). |
| Quality frame | `GearView.apply` (B:6340, `plainTool` B:6355): only a Normal tool without modifiers keeps the item's own quality frame (0.2 finding 4); a rolled tool (rarity above Normal or any modifier) gets its rarity frame like gear. |
| Admin `/gear level` (and the other write actions) | Today `GearAdmin.run` answers "<item> is not gear" for every action but `read` unless `GearData.gearish` (B:10873; `gearish` B:4737-4739 = gear, or a `Tool_` id that already HAS a document), and its level action writes `lvl` + `lvlA` only (B:10903-10913) - so `/gear level 13` on a plain Copper pickaxe is refused. 0.2.2: the guard in `GearAdmin.run` becomes `gearish(id, md) || (PART_TOOLS && GearData.gatherTool(id))` (a new helper = `toolKind` is mining / foraging / farming), and the level action also writes `tl` = 1 when the item is a gathering tool (`clear` removes `tl` too); `unid` / `identify` refuse gathering tools (tools are never unidentified). `GearData.gearish` itself stays unchanged: it also gates `GearFns.docOf` (B:7298, the `gear:fn:*` bridge SkyyAuctions reads), `GearThrowSys` (B:7422) and `/gear me`, so widening it globally would make plain tools look like gear documents to SkyyAuctions. (`stampStack` would have been safe either way: its second guard `st == 0 && !isGear` returns, B:6899.) `GearAdmin.me` (B:10945, `/gear`) gets the same local widening, read only, so `/gear` shows a held tool's lines. |
| `/gear read` (admin) | `GearAdmin.read` (B:10828) gets a tool block when the held item is a gathering tool: kind + gate skill, stored `lvl` / `lvlA` / `tl`, old or strict, the effective level for you (section 7), gate result, the target power and m for each `tool.hint` reference block plus hits, base Fortune, the rolls, and whether the bridge source is posted / pinned right now. For stage 0 and support. |

---

## 7. Old tools: never locked out (question 4)

| Tool | Marker | Effective level |
|---|---|---|
| No SkyyGear document: vanilla tools owned before 0.2, AND every tool that never went through `craftDoc` - chest loot, mob drops (the Goblin Miner's Scrap pickaxe), Auction House purchases of plain tools, kits, admin gives | none | min(table level = band start, your skill) |
| Document written by 0.2 / 0.2.1 (crafted while the gate was "coming later") | none | min(stored `lvl`, your skill) |
| Document written by 0.2.2: craft, reforge by a player who meets the level, admin `/gear level` (the `GearAdmin` change, section 6) | `tl` = 1 | the stored `lvl` (strict gate) |

**What `tool.legacyLenient` really covers (question 4).** "No 0.2.2 marker" is not "owned before the update": the code cannot tell a
tool someone had before 0.2.2 from a plain tool found, bought or given later. With the row on (default), all of them are ungated
forever (until crafted / reforged by someone with the level) - so a Mining 1 player with a plain Mithril pickaxe from a chest or the
Auction House mines at full vanilla Mithril speed (never below vanilla, 3.1). Weapons do NOT work like this: a plain weapon is strict
in 0.2 - `GearData.effective` returns `legacy(id)` for plain gear (B:5991) and `GearHit.judge` (B:7632-7653) checks its table level -
so "like weapons" is not met for unmarked tools while the row is on. Turning the row off makes every unmarked tool strict at its band
start (or its stored 0.2 / 0.2.1 level), which also locks players out of tools they own today. A middle option the code CAN tell apart:
lenient only for tools with a 0.2 / 0.2.1 document (crafted since 2026-10-02), strict for tools without any document (found, bought,
given, and vanilla tools from before 0.2). Default: lenient, as the first draft had it, until Skyy picks.

- `GearToolLv.effLevel(u, id, d)`; "your skill" = the gate skill level, raised to `level.gateFloor`. Without SkyySkills: the stored level
  and `level.noSkills` decide (as for weapons).
- An old tool **never blocks** (effective <= your skill) and gives power and Fortune at its effective level - and never less than vanilla
  power (3.1), so nobody loses speed compared with today.
- **No mass rewrite:** the rule is read on use; no stack is rewritten to add the marker. The passive stamp never writes a plain tool:
  `GearStamp.stampStack` (B:6889) returns early for an item that is not `gearish` (B:4737: gear, or a tool that already HAS a document)
  and for any non-gear id without a document - the in-memory legacy document of section 6 stays in memory. 0.2 / 0.2.1 tool documents already have a view;
  it re-renders through the normal view signature (`GearView.sig` includes the shown lines + config epoch), which never rewrites `lvl`.
  Plain tools keep their vanilla tooltip until crafted / reforged.
- Switch `tool.legacyLenient` (default on; choice if Skyy picks the middle option: `all` / `crafted` / `off`). Off = unmarked tools
  follow the strict gate like new ones.
- `tool.gate` off = every tool behaves like an old tool (never blocks, works at min(level, skill)).
- SkyyRolls-migrated tool documents (src `rolls`) count as old; their old weapon lines do nothing on tools (tools never feed combat
  totals) and show grey; a reforge replaces them.
- Rollback to 0.2.1 is safe: `tl` and the new stat keys are unknown fields that 0.2.1 keeps and shows by name (reading rule 3); its tools
  are simply ungated again.

---

## 8. Tooltips (vanilla look, `GearView.lines` B:6222)

```
Copper Pickaxe                                         <- rarity colour (Normal: the item's own quality colour)
Lv 13 - Requires Mining 13                             <- vanilla "met" green; red + " (you: 9)" when too low
Breaks in: Stone 3 hits - Copper Ore 3 - Iron Ore 5    <- the tool alone, at its effective level
Mining Fortune at Lv 13: +1.3%
Mining Fortune: +3%
Mining Speed: +8% - fewer hits per block                <- label per question 1
Mining Wisdom: +2%

RARE TOOL                                              <- rarity colour (slotWord TOOL exists, B:5997)
```

- **Gate line** (`GearView.gateLine` B:6155): tools take the enforced branch (green `C_OK` / red `C_BAD` + "(you: M)", the 0.2 design
  review colours). An old tool below its level: "Lv 18 - old tool: works as Lv 9 for you" in the kit's info blue (#7caacc, vanilla
  BarterPage note colour); at or above: the green line. "(coming later)" and the grey "(coming later: gathering gear)" line (B:6244) go
  while `part.tools` is on.
- **Hits line** (pickaxe, hatchet, shovel): up to 3 reference blocks per family from row `tool.hint.<Family>` (default Pickaxe
  Rock_Stone, Ore_Copper_Stone, Ore_Iron_Stone; Hatchet Wood_Oak_Trunk; Shovel Soil_Dirt), computed with the SAME function as the hit
  (3.1) from the live BlockType (gather type + quality) - a block the tool cannot mine shows "too hard". Without tree bonuses (stated in
  the row help).
- **Fortune line** one decimal; **modifier lines** = the existing `modLine` (B:6023); tool lines no longer forced grey (`statLines`
  B:6188 greys slot 3 today).
- Hoe / sickle: gate line + Fortune line + rolls (no hits line).
- 0.2.1 found that the client draws its own vanilla box from the item asset under our text (B1 `GearBase.HINT_W`). What the client draws
  for a TOOL is UNVERIFIED (stage 0 check c); if it shows a vanilla number, add a grey hint the same way.

---

## 9. Server Setup rows (new page `tools` "Tools"; kit 1.1 row format of B:1824)

| Row | Label (<= 40) | Type / default / range | Flags | Help (<= 100) |
|---|---|---|---|---|
| `part.tools` | Tool levels and tool stats | bool / true | live,part,danger | Tools need their level and get speed, Fortune and rolls. Off = 0.2 tools. |
| `tool.gate` | Under-level tools are blocked | bool / true | live,danger | A tool above your skill cannot break blocks. Off = it works at your level instead. |
| `tool.legacyLenient` | Unmarked tools work at your level | bool / true (question 4) | live | Tools without the new level mark (old, found, bought, given) work at min(their level, your skill). |
| `tool.staffBypass` | Admins ignore tool levels | bool / false | live | Players with skyygear.admin are never blocked by a tool level, hoe and sickle lock too. |
| `tool.farmLock` | Lock under-level hoes and sickles | bool / **false** (question 2) | live | Too-low hoes cannot till, too-low sickles cannot harvest. Test in game before turning on. |
| `tool.notice` | One-time tool levels chat line | bool / true | live | Each player gets one chat line about tool levels (the gear.notices switch still applies). |
| `tool.popupMs` | Tool level popup every | int / 1500 / 250-60000 ms | live | At most one "Requires Mining N" popup per this time. |
| `tool.power` | Breaking speed from tool level | choice / ladder (ladder, vanilla) | live,danger | Ladder = the level sets breaking power (same level, same speed). Vanilla = Hytale's. |
| `tool.power.strength` | Level effect strength | int / 100 / 0-100 % | live,danger | 100 = the full ladder, 0 = vanilla. Never below the tool's own vanilla power. |
| `tool.power.growth` | Ladder growth per level | dec / 3 / 0-50 % | live,danger | Each ladder step climbs at least this much a level (and past the last tier). |
| `tool.matBonus` | Better material bonus | dec / 0.3 / 0-10 % | live,danger | Power and Fortune x (1 + this % x band start): Copper +3%, Iron +4.5%, Mithril +12%. |
| `tool.ladder.<Family>_<GatherType>` | Breaking power ladder | table / (empty) / text Points | live,adv | level:power list, e.g. Pickaxe_Rocks=1:0.25,10:0.35. Empty = built from vanilla tools. |
| `tool.fortune.perLevel` | Tool Fortune per level | dec / 0.1 / 0-10 % | live,danger | Double-drop chance a tool adds per level (Lv 18 = +1.8%), x the material bonus. |
| `tool.hint.<Family>` | Tooltip reference blocks | table / Pickaxe Rock_Stone,Ore_Copper_Stone,Ore_Iron_Stone; Hatchet Wood_Oak_Trunk; Shovel Soil_Dirt | live | Blocks the tooltip's "Breaks in" line shows (max 3, without tree bonuses). |
| `tool.reforge` | Tools can be reforged | bool / true | live | Pickaxes, shovels, hatchets, hoes and sickles show on the Reforge page. |
| `tool.reforgeCost` | Tool reforge cost | int / 100 / 0-1000 % | live,danger | Tool reforges cost this % of the gear reforge cost (Costs page). |
| `tool.craftRolls` | Crafted tools roll a rarity | bool / true | live,danger | Crafted tools roll rarity + tool modifiers like weapons. Off = Normal, no rolls. |
| `tool.log` | Log tool hits | bool / false | live,adv | One gear.log line per refused tool hit (testing). |
| `stats.mfort` ... `stats.awis` | (the `stat` table) | 10,10 / 10,10 / 30,10 / 10,10 / 10,10 / 30,10 / 10,10 / 10,10 | live,danger | (Max at 100 % / Weight - the existing table.) |

Still used, unchanged: `part.gate`, `rarity`, `odds` (Craft column), `smith.perLevel`, `smith.cap`, `craft.maxRarity`, `craft.levelFrom`,
`craft.belowBand`, `cost.reforge`, `xp.reforge`, `stat.levelFloor`, `stat.levelFull`, `level.material`, `level.gateFloor`,
`level.noSkills`; the player switches `gear.blockedPopup` and `gear.notices` (only its help text changes, see the notice below).
SkyySkills (not SkyyGear): `perk.doubleDropMax`, `perk.<skill>.doubleDropPerLevel`, `bridge.bonus.enabled`, `bridge.bonus.xpSkills`.

**One-time update `GearCfg.migrate022`** (the established marker pattern of migrate013 / migrate02 / migrate021): History snapshot first
("before the 0.2.2 tool rows"), add-only (the missing `stats.<tool key>` lines after the last `stats.` line, the missing tool rows under a
`SkyyGear 0.2.2 tool levels` marker), new settings start at their defaults (no change-log line - the 0.1.2 rule), the kit's atomic write
(bytes and CR kept), runs once; a fresh file carries everything. Danger set additions: every row marked danger above.

**One-time player notice** (the project's pattern: SkyyTrees `note.swing`, SkyyGear `GearNotice`). On the first `GearTick` with
`part.tools`, `tool.gate` and `tool.notice` on, once per profile, never while `profile:busy:<uuid>` is set, honouring the player switch
`gear.notices` (B:11137 - its help text becomes "One-time lines about gear system changes"): "[Gear] Tools now have levels: a pickaxe or
shovel needs Mining, a hatchet Foraging, a hoe or sickle Farming at the tool's level. Hover a tool to see it. Tools you already own keep
working at your level." (last sentence only while `tool.legacyLenient` is on). Stored as a new key `noticeTools=true` in the same
`players/<pkey>.properties` file. Careful: `GearNotice.run` writes the WHOLE file ("# SkyyGear player flags\nnoticeShown=true\n",
B:6655), so 0.2.2 changes the writer to read-merge-write both keys (a profile that saw neither notice must not get `noticeShown=true`
by accident, and one that saw the migration notice must keep it).

---

## 10. Bridges

| Key | Direction | Change |
|---|---|---|
| `skill:bonus:<uuid>` source `"gear"` | SkyyGear writes, SkyySkills reads | NEW (4.2). SkyySkills 0.4.12 reads any source - no SkyySkills change. |
| `skill:fn:level` | SkyyGear reads | Gate + effective level (as for weapons). |
| `profile:epoch:<uuid>`, `profile:busy:<uuid>` | SkyyGear reads | Recompute / pause the source (4.2). |
| `coins:fn:get/take/add`, `skill:fn:addxp` | SkyyGear reads | Tool reforges (unchanged calls). |
| `gear:fn:roll` mode 8 | SkyySacks calls | Tools now roll rarity + modifiers - same call, no SkyySacks change. |
| `gear:fn:level`, `gear:fn:sig`, `gear:fn:describe` | SkyyAuctions calls | Work for tool documents unchanged (the sig already includes the level; describe shows tool lines). Plain tools still answer null, exactly as today: `GearFns.docOf` (B:7294-7300) asks `gearish` first, and `gearish` stays unchanged (section 6). |
| `gear:gates` | published | Unchanged ("combat:class,mining:Mining,foraging:Foraging,farming:Farming"). |
| SkyyTrees | - | No change: TreeDmgSys multiplies independently (3.1), swing tiers untouched, Fortune / Wisdom sources add up. |
| SkyyCollections | - | No change (counts the same breaks / pickups). |
| SkyySkills Stats page | SkyySkills shows | `StatsPage.treeLine` (S:10810) prints the SUM of every source as "Skill tree: +X% double drops, +Y% XP", so the held tool's bonus appears under that label. Cosmetic only; the next SkyySkills can relabel it ("Tree + tool") or split it by source. |

Main session (not this build): SkyyMenu `MODS_VERSIONS` bump; `tools/deploy_set.py` pin; HANDOFF / TEST-CHECKLIST.

---

## 11. Tests

**Bare-JVM harness `SkyyGear/test_skyygear_0.2.2.py`** (every earlier section carried forward; new section AD). The 2026-10-02 lesson
(SkyyUiProbe 0.3.1): the harness must **run** the code paths, not only load classes.

| # | What it executes |
|---|---|
| AD1 gate | **Fixtures (named, since `test_skyygear_0.2.1.py` builds no `BlockType` or `ItemTool` today):** tool items = the 0.2.1 harness's fake Item map (`fake_item`, test l.899-914: an allocated `Item` with fields set by reflection) plus the protected field `Item.tool` set to `new ItemTool(new ItemToolSpec[] { new ItemToolSpec(gatherType, power, quality), ... }, 1.0f, null)` - both public constructors (VERIFIED: `ItemToolSpec(String,float,int)`, `ItemTool(ItemToolSpec[],float,ItemTool$DurabilityLossBlockTypes[])`) - with the numbers of all 32 tools read from Assets.zip (copied into scratch, Parent chains resolved); blocks = `BlockType.CODEC.decodeJson(RawJsonReader.fromJsonString(json), extraInfo)` on the Assets.zip block JSON (the AB8 decode, test l.5305), or, if that decode needs more of the asset store, an allocated `BlockType` whose `gathering` is a `BlockGathering` holding `new BlockBreakingDropType(gatherType, quality, 1, null, null)` (public constructor); both read back through `getGathering().getBreaking().getGatherType()` / `getQuality()` before use. Real `DamageBlockEvent` objects (public constructor `(ItemStack, Vector3i, BlockType, float, float)`) through `GearToolHit.onDamage`: strict under-level -> cancelled, damage untouched, one popup per `tool.popupMs` (counted in `POPPED`, no Universe in the bare JVM); at level -> not cancelled, damage x m; old tool -> never cancelled; creative / staff bypass on + admin / `part.tools` off / `part.gate` off / `tool.gate` off / non-tool item / an already-cancelled event (no popup) / Bark Scraper. `BreakBlockEvent` backstop the same, plus a **null item** (F-pickup) -> never cancelled. **Then the REAL `GearToolHitSys.handle` and `GearToolBreakSys.handle`** on the 0.2.1 AD3(b) ECS shim (test l.5541ff builds it - CommandBuffer / ArchetypeChunk subclasses, fixtures by Ref + ComponentType identity; l.5930-6103 runs `GearHitSys.handle` on it): a player ref with PlayerRef + Player (Adventure / Creative), a ref without PlayerRef (a mob or the world), null item, an already-cancelled event; no system error logged. Bytecode: both registered in `GearFx.setup`, one registerSystem per class. |
| AD2 crafted level | `craftDoc` for all 32 tools at skills 0 / 4 / 9 / 10 / 13 / 18 / 23 / 28 / 49 / 80: the stamped level = clamp into the band, marker `tl` set, 6,000 rolls per family match the craft odds + Smithing step (chi-square), modifiers only from the family pool, count = min(rarity count, pool); `tool.craftRolls` off -> Normal, no modifiers; mode 8 path; the below-band note text for tools. |
| AD3 bridge | `GearToolFx.post` for every family: keys and values (base x bonus + rolls / 100); removed for no tool / strict under-level / `part.tools` off / profile busy / `GearByeB.accept`; old tools use the effective level. **Null item:** a BreakBlockEvent with a null item (the F-pickup shape) leaves the posted value and the pin count untouched. **Refresh filters:** `GearToolSlotSys` on an `InventorySetActiveSlotEvent` of the utility or tools section (ids from `InventoryComponent.UTILITY_SECTION_ID` / `TOOLS_SECTION_ID`) changes nothing, on the hotbar section it re-posts; `GearToolInvSys` re-posts only for a hotbar `InventoryChangeEvent` that changed the active slot's stack; `GearFxInvSys` is byte-identical to 0.2.1. **Pin:** post from a BreakBlockEvent, a GearTick refresh with another item in hand leaves the value, a simulated FIFO world queue with BreakTask queued before AND after the first unpin hop -> BreakTask always reads the breaking tool, the second hop restores the hand value; nested pins. Then the **real SkyySkills jar** (the SET pin) is loaded in the same JVM: `SkillBonus.dd` / `xpBonus` / `Perks.chanceU` return the expected sums with a `"trees"` source present, capped by `perk.doubleDropMax`. Bytecode: `World#execute` = `Deque.offer`, `consumeTaskQueue` polls to empty, `World#tick` order, SkyySkills `BreakSys` ends in `World.execute(BreakTask)`. |
| AD4 power | Every vanilla tool x main gather type x every level of its band: the jar's target power = an independent Python copy of 3.1-3.2 (1e-6); the section 3.3 tables reproduced through real events (`getDamage` after `onDamage` -> hits); a simulated TreeDmgSys multiply before vs after = the same final damage; off-tool gather types and soft blocks untouched; never below vanilla; strength 0 = vanilla exactly; Quality-gated blocks untouched; `tool.ladder.*` rows parsed and used; power rolls (`mpow` / `cpow`) applied only on main gather types; the ladder points exclude Scrap / Steel_Rusty and the Scrap pickaxe gets the 3.2 numbers; the 20 faster band-start cases of 3.2 exactly; a changed `level.material` start or `tool.power.growth` rebuilds the ladder after the config epoch moves. |
| AD5 reforge | `GearForge.reforge` on a bare container with a coins stub: plain tool -> Normal document + 1 modifier, level = band start; Rare stays Rare, modifiers only from the pool; level kept; marker only when the reforger meets the level, else still old + rolls at the effective level; cost = `cost.reforge` x `tool.reforgeCost`, taken first, refunded on a forced failure; Smithing XP call; refused with `tool.reforge` / `part.tools` off; `rows` lists tools. |
| AD6 old tools | `effLevel` matrix: no document / 0.2 document / 0.2.1 document / 0.2.2 marker / admin `lvlA` x skill below / at / above x `tool.legacyLenient` on / off (and `crafted` if question 4 picks the middle option) x `tool.gate` on / off; a found / bought plain tool behaves exactly like an old one (the documented question-4 loophole); gate line text + colour each; power and Fortune at the effective level; the stack object is unchanged (nothing written). |
| AD7 tooltips | Lines for strict met / not met, old below / above, no SkyySkills, Normal plain tool keeps its own quality, a rolled tool gets its rarity frame, no "(coming later)", the hits line = the hit function for every reference block. |
| AD8 migrate022 | On a scratch COPY of the live `config.properties` (read only original): exact bytes, History, marker, add-only, CRLF, twice = once, a fresh file equals; Undo of a new line through the kit. |
| AD9 farm lock (built unless question 2 = no) | Generated assets: the `Hoe_Till` root override keeps the vanilla `Settings` (both the `Adventure` and the `Creative` branch) byte-equal; the two selector copies equal the vanilla selectors in every field except the wrapped `HitBlock` list (`HitEntity`, `Selector`, `RunTime`, `Next` identical); the `Sickle_Attack` root and the swings are NOT in the jar; every referenced id exists; no other vanilla id is overridden; the build stops if the vanilla shapes change or if any vanilla sickle's `Swing_*_Selector` var overrides `HitBlock`. Marker logic: on / off on a hotbar slot change, on a hotbar inventory change and in GearTick (fake effect controller or bytecode); **never on in Creative; never on with `tool.staffBypass` + admin; never on while `tool.farmLock` is off (the default)**. The start-up check logs the active `Hoe_Till` root and "sickle gate active on N of 4 sickles". |
| AD10 byte-compare | 0.2.1 jar -> 0.2.2 jar: every class difference listed, the new classes, non-class entries (manifest, generated assets). |
| AD11 admin + read | `GearAdmin.run` on a bare inventory: `/gear level 13` on a plain Copper pickaxe -> a document with `lvl` 13, `lvlA`, `tl` 1, strict at once (AD1 refuses it at Mining 9); `clear` removes all three; refused as "not gear" with `part.tools` off; a plain Bark Scraper still refused. `GearData.gearish` unchanged: `GearFns.docOf` still answers null for a plain tool. `/gear read` prints the tool block (section 6). |
| AD12 notice | Shown once per profile, never while busy, silent with `gear.notices` off or `tool.notice` off; the players file keeps `noticeShown` when `noticeTools` is added (and gets no `noticeShown` it did not have); the text drops its last sentence with `tool.legacyLenient` off. |

**Cross-check (full round):** all SET jars in one JVM with `-Xverify:all`, the engine-access audit (protected members only from a subclass
on `this` - the 0.3.1 lesson), the Adventurer permission audit (no new player command expected), `python tools/ci/lint.py` 0 fails.

**In game (numbered, for TEST-CHECKLIST):**
1. Mining 9 and any Copper pickaxe (plain or crafted) set to Lv 13 with the admin `/gear level 13` (0.2.2 lets it write tools and marks
   them strict; `/gear read` shows `tl 1`): hit stone -> popup "Requires Mining 13 (you: 9)", no crack, no drop, no XP; the block does
   not flicker away (UNVERIFIED client side, stage 0 check a).
2. Hit tall grass and a crop with it -> also refused. Hit a mob -> normal damage. Switch to Creative -> it breaks blocks.
3. Craft a Copper pickaxe at Mining 13 -> tooltip "Lv 13 - Requires Mining 13" green, "Breaks in: Stone 3 hits - Copper Ore 3 - Iron Ore
   5"; mine iron ore -> 5 hits (count them); at Mining 18 craft another -> 3 hits.
4. Craft ten tools -> some come out Unique / Rare with Mining Fortune / Wisdom / Speed lines (label per question 1).
5. Reforge a pickaxe -> rarity stays, new rolls, coins taken, Smithing XP.
6. A pickaxe you owned before 0.2.2 -> still works at once; tooltip "old tool: works as Lv N for you" (0.2 / 0.2.1 crafted ones).
7. Hold a Fortune pickaxe: `/skills stats mining` shows the bonus line ("Skill tree: +X% double drops" - it sums every source, see
   section 10) higher than with an empty hand; swap to an empty hand -> it drops back within a second.
8. (Stage 0 check b - only after turning Server Setup -> Gear -> Tools -> "Lock under-level hoes and sickles" ON.) Server log: "sickle
   gate active on 4 of 4 sickles" and the `Hoe_Till` root = SkyyGear. Under-level hoe: right-click dirt -> no tilling, popup when you
   select it; a level-ok hoe tills; in Creative the under-level hoe tills. Under-level sickle on ripe wheat -> no harvest, the swing
   still plays, it still hits a mob, left / right swings still alternate; the Iron sickle behaves the same. Turn the switch off -> all
   normal again within a second.
9. F-harvest an eternal crop while holding a Farming Fortune hoe -> double drops happen more often; bare hand -> base chance. F-pick a
   loose rock while holding a Fortune pickaxe -> `/gear read` still shows the source posted (the null-item pickup changes nothing).
10. Heavy Hatchet maxed + a Lv 20 Iron hatchet -> oak log in one hit (question 5).
11. First join after the update -> one "[Gear] Tools now have levels ..." line; relog -> no second line.
12. Drag a different tool onto your selected hotbar slot (no slot change) -> `/gear read` shows the new tool's source at once, not after
    a second.

---

## 12. Risks

| # | Risk | Mitigation |
|---|---|---|
| R1 | The client may predict a block break or a crack and then get it back from `invalidateBlock` (a brief flicker on refused hits). | Same path the engine uses for its own refusals (island protection does it today). Stage 0 check a. |
| R2 | Players craft Copper tools at Mining 2 and get a tool they cannot use until Mining 10 (band start, LOCKED copper tools 10-18). | The craft chat line says so; `craft.belowBand=block` refuses at benches; the next SkyySkills x3 early XP makes Mining 10 quick. |
| R3 | Sickle swing harvests stay outside SkyySkills (no XP, no double drop) - sickle Fortune / Wisdom only count on F-harvests while held. | Question 3: a SkyySkills change through `InteractivelyPickupItemEvent` (setItemStack can even double the stack) - with the limits listed there (the event carries only the item). |
| R4 | The `Hoe_Till` root / sickle selector overrides clash with another mod that replaces the same files (Farming_Overhaul, AdvancedFarming exist in the Mods folder; not enabled in the test world). Whichever loads last wins. | Start-up check logs the active root and "sickle gate active on N of 4". `tool.farmLock` off only stops the marker - the override files stay in the jar for every hoe and sickle (assets cannot be switched at run time) and pass every till / harvest straight into the vanilla chain. |
| R5 | (was: a root gate on `Sickle_Attack` could reset the left / right combo and also stopped mob hits.) Now the root and the swings are untouched; the remaining risk is that the four sickles' inline selector vars (`{"Parent": "Sickle_Swing_*_Selector", ...}`) do not pick up the overridden parent, so the sickle gate silently does nothing. | Harmless when it fails (vanilla harvest). The start-up check reads each sickle's resolved selector and logs it; stage 0 check b; fallback = no sickle gate (hoe only) or SkyyGear-owned sickle items later. |
| R6 | Whole-hit breaking: some levels change nothing on some blocks (e.g. an Iron pickaxe is 2 hits on stone through its whole band, like vanilla Iron / Thorium / Cobalt). | The tooltip hits line; growth row; the power roll and Heavy Pick push over the lines. |
| R7 | The level ladder makes low materials at high band levels as fast as the next material at that level (Lv 13 Crude = Lv 13 Copper). | Intended (Skyy 2026-10-01 "same level = about the same stats"); bands cap it (Crude stops at 13). |
| R8 | A tool swapped in the same tick after a break could move the Fortune of that break. | The pin (4.2 step 4). F-harvest / felled logs use the hand at award time (documented). |
| R9 | The hidden lock marker is saved with a player who logs out within 3 s of a refresh (same caveat as SkyyTrees' swing effects). | 3 s duration, Overwrite; harmless (it only blocks hoe till / sickle harvest for up to 3 s). Never happens while `tool.farmLock` is off (the marker is never put on). |
| R10 | Per-hit work (document read) at up to 4 hits a second per player. | Identity cache of the last held stack -> (level, marker, rolls) per player. |
| R11 | 0.2.1 is still changing. | Every hook is named by class + method; line numbers are 0.2 (live) with 0.2.1 lines as of the 22:19 file. |
| R12 | Fortune / Wisdom do nothing when SkyySkills is missing or `bridge.bonus.enabled` is off. | Same limit as the tree nodes; the power part still works. |
| R13 | Vanilla tools stop early: hoes at Thorium (Lv 28), sickles at Iron (23), shovels at Cobalt (38). Farming tools cap their level there. | Our own tool tiers later (the 50+ plan, Gear-Levels-Wynn-Spec question 3). |
| R14 | The SkyySkills Stats page calls the summed bonus "Skill tree" (S:10810), so a tool's Fortune / Wisdom shows under that name. | Cosmetic; relabel in the next SkyySkills (section 10). |
| R15 | `tool.legacyLenient` on = every unmarked tool (chest loot, mob drops, AH, admin gives - not only old ones) is ungated forever; a low player with a found high tool mines at its full vanilla speed. | Question 4 (keep / only 0.2-crafted tools / off); crafting and qualifying reforges add the mark. |
| R16 | The client side of the marker + EffectCondition pattern was never confirmed in game (SkyyTrees 0.2.3 / 0.2.4 headers, HANDOFF 2026-09-25 06:53). If the client does not run the condition, a refused till / harvest is predicted by the client and the block shows wrong until it is re-sent. | `tool.farmLock` default off; Skyy turns it on for stage 0 check b and keeps it on only if it looks right. |
| R17 | The Scrap pickaxe (a Goblin Miner drop) gets the Pickaxe ladder at its level: Lv 10 = stone 10 -> 3 hits, dirt 10 -> 2. | "Same level ~ same speed" (Skyy 2026-10-01); its own ore advantage stays; it is not a ladder point (3.2). |
| R18 | 0.7: new gather types `Metals` / `GoblinMetal` get no level effect (m = 1). | Section 2.5; a `tool.ladder.Pickaxe_GoblinMetal` row (or a build) adds them after the 0.7 release. |

---

## 13. Stages

| Stage | What | Size |
|---|---|---|
| 0 - checks (in the 0.2.2 test, no extra build; none can run in the bare-JVM harness) | a: refused hits show no flicker / crack; b (with `tool.farmLock` turned ON by Skyy): the `Hoe_Till` override is active, all four sickles (the inline-selector ones included) refuse ripe crops while too low, still hit mobs and still alternate left / right, a creative player tills; c: what the client draws under a tool tooltip; d: the one-time notice shows once. | S |
| **0.2.2 ships** | Gate (DamageBlockEvent + BreakBlockEvent backstop, popup), `enforcedKind` for gathering kinds, level ladder power (run-time ladder), base Fortune, the 8 tool stats (rolls, reforge, crafted rarity), old-tool rule (question 4), tooltips, the `"gear"` bridge source with the pin and the hotbar refreshes, Server Setup page + migrate022, staff bypass row, the `GearAdmin` level / read changes, the one-time notice, and the hoe / sickle lock built with `tool.farmLock` **off** (unless question 2 = no: then it is left out). | L (full round: saved documents, coins on reforge, several mods read the bridge) |
| Waits | Sickle swing harvest XP + double drops (SkyySkills, question 3); the gathering pacing x3 -> x1.5 (SkyySkills, answer 4, queued); found-tool levels by zone (gear stage 4, waits with found gear); gear swing speed (not now - R9 lock; a SkyyTrees build if it ever comes); the other gathering stats (Mining Spread, Auto Smelt, Timber - locks 34 / 36 / 39; Breaking Power = Quality, lock 31); gathering armor sets; our own tool tiers past vanilla; on the 0.7 release day: re-run the section 2.5 diff on the release build and decide ladder rows for `Metals` / `GoblinMetal`. | - |

**Build order inside 0.2.2** (`SkyyGear/build_skyygear_0.2.2.py` = a direct copy of the FINAL `build_skyygear_0.2.1.py` with only these
changes - SkyyGear has no patch scripts, B1 header l.7; each step leaves a building jar):

1. **Data:** the 8 STATS rows + slot letters `m` / `h` / `f` (asserts B:714-717 updated), `GearData.gatherTool`, `tl` reading,
   `GearCfg` rows of section 9 + `migrate022` + the `tools` Server Setup page.
2. **Levels + gate:** `enforcedKind` for gathering kinds (with `part.tools` + `tool.gate`), `GearToolLv.effLevel` (section 7,
   `tool.legacyLenient` per question 4), `GearData.effective` for plain gathering tools, the `GearView.gateLine` tool branch.
3. **Block hooks:** `GearToolHitSys` + `GearToolHit.onDamage` + popup (`Universe.get().getPlayer`), `GearToolBreakSys` backstop (null =
   no change), Creative + `tool.staffBypass`.
4. **Power:** the run-time ladder (3.2, epoch cache, `tool.ladder.*` parser), m (3.1), the hits function shared with the tooltip.
5. **Bridge:** `GearToolFx.post` / pin / `GearToolUnpin`, `GearToolSlotSys` (hotbar only), `GearToolInvSys` (hotbar only), `GearTick`
   refresh, logout / shutdown / profile-busy removal.
6. **Craft + reforge:** `craftDoc` rarity + family pool + `tl`, `GearForge.rows` / `refuse` / cost row, the reforge marker rule,
   `GearAdmin.run` guard + `tl` on `/gear level`, `/gear read` tool block, `/gear` (`me`) for tools.
7. **Tooltips:** gate line, "Breaks in", Fortune line, rolls not grey, quality frame rule.
8. **Farm lock** (unless question 2 = no): generated `Hoe_Till` root + two selector copies + `Skyy_Gear_Tool_Lock`, shape asserts,
   `GearToolFx.lock` (Creative / bypass / row), start-up check; `tool.farmLock` default off.
9. **Notice:** `noticeTools` with the read-merge-write `GearNotice` writer.
10. **Harness** AD1-AD12 + carried 0.2.1 sections, then the full-round cross-check (section 11).

---

## 14. Questions for Skyy (each has a recommended default)

Question 1 must be answered before the build (it is a label in the item tooltips); the others have safe defaults the build can ship with.

1. **Stat name (before the build).** Your reforge list says "Mining Speed" / "Chopping Speed", and you also said gear swing speed is "not
   for now". So the tool stat makes each hit STRONGER - fewer hits per block, which makes mining faster. Keep your names for it, even
   though your Mining tree's "Mining Speed" means faster swings (two "Mining Speed" lines that both speed mining up)? Or call the tool
   stat **Mining Power / Chopping Power** (close to the planned "Breaking Power", which means mining harder blocks), or "Breaking
   Damage" (your lock 33's name)? **Default: your names, Mining Speed / Chopping Speed.**
2. **Too-low hoes and sickles.** Should a too-low hoe also not till, and a too-low sickle not harvest ripe crops? It works by putting a
   tiny check of a hidden marker in front of the vanilla till and in front of the sickle's crop harvest - the same trick as your
   swing-speed tree, whose client side was never confirmed in game. A too-low sickle still hits mobs and still swings left / right.
   Without it, a too-low hoe / sickle only cannot break blocks. **Default: build it, but ship the switch OFF; you turn it on in Server
   Setup -> Gear -> Tools to test it (test step 8) and keep it on if it looks right.**
3. **Sickle swings and Farming XP.** Hytale never tells the server when a sickle swing harvests a crop, so sickle swings give no Farming
   XP and no double drops today - only F-harvests and broken crops count. Hytale does send a "picked up an item" event for those drops,
   but it carries ONLY the item - no crop, no position. So the next SkyySkills would pay by the dropped crop item, could not tell a crop
   you placed, and could not match it to a block; it would skip pickups inside an F-harvest window the way SkyyCollections already does
   (a 2 s window opened by the F on a ripe block, C:2788-2820 - sickle swings never open it). Add it anyway, together with the pacing
   boost? **Default: yes, in the next SkyySkills, with those limits.** Until then, sickle Fortune / Wisdom count when you F-harvest
   while holding the sickle.
4. **Tools without the new level mark.** Today every tool that was never crafted under 0.2.2 - the ones you own, but also chest loot,
   mob drops, Auction House buys and admin gives - works at your level and never locks you out, so a Mining 1 player with a plain
   Mithril pickaxe mines at full vanilla speed. Weapons do not work like this (a plain weapon needs its level). Keep that; or only let
   tools crafted since 0.2 (2026-10-02) work at your level and make found / bought / given ones need their level like weapons; or make
   every tool need its level (players can be locked out of tools they own)? **Default: keep - every unmarked tool works at your level
   (switch `tool.legacyLenient`).**
5. **Heavy Hatchet one-chop.** Your lock: maxed Heavy Hatchet = a top hatchet fells a log in one hit (vanilla: Thorium and better). With
   tool levels an Iron hatchet does it from Lv 20, or a bit earlier with a big Chopping Speed roll (Iron Lv 19 with +5 %, Copper Lv 18
   with +16 %). OK, or keep one-chop for Thorium-and-better only? **Default: OK - it follows "same level, same speed".**

---

## 15. Fact check of the task's starting facts

- Right: SkyyGear live 0.2; TOOL_FAMILIES B:735; GATE_BY_KIND / ENFORCED_KINDS B:720-724; `GearGate.check` B:5043; tool gate "(coming
  later)" B:6152-6161; tool reforge refusal B:7200; STATS B:655 with letters w/s/a/e and S_LIVE; weapon enforcement = amount 0 + cancel +
  knockback removed + popup (B:8584-8587); tools get a document + level on craft, Normal, no modifiers; SkyyTrees swing tiers and
  TreeFx.dmgBonus; SkyySkills reads `skill:bonus` on every award with xp 0..5 and a capped double-drop chance; hoes have no Specs;
  hatchet Woods power Crude 0.15 / Wood 0.2 / Copper 0.2 / Iron 0.3 / Thorium+ 0.5.
- **Wrong: "staff bypass setting exists in SkyyGear"** - it does not (section 1); this spec adds `tool.staffBypass` (default off).
- **Partly wrong: "any pickaxe can mine any ore"** - Adamantite ore needs Quality 4 (Thorium pickaxe and up) and Mithril ore is
  GatherType Rocks with Quality 5 (Adamantite pickaxe and up, then one hit).
- Added: the vanilla Copper shovel (Soils 0.2) is weaker than the Crude shovel (0.4); sickle swing harvests fire no cancellable event but
  do fire `InteractivelyPickupItemEvent`; plain dirt pays no Mining XP (S:1129-1137: only Soil_Sand / Soil_Gravel), so shovel Fortune /
  Wisdom only matter on sand and gravel.

---

## 16. Review notes (critic review 2026-10-02, each item re-checked by the editor before applying)

| # | Verdict | Proof / reason |
|---|---|---|
| 1 hand refresh | Applied (2.2, 4.2) | `GearFxInvSys` returns for every container but armor (B:9419-9429). New `GearToolInvSys` (hotbar only) instead of touching it; `GearToolSlotSys` filters `HOTBAR_SECTION_ID` (`InventoryComponent$Hotbar` / `$Utility` / `$Tool` all extend `ActiveSlotInventoryComponent`, whose `setActiveSlot` writes at 17 and fires at 22-36). |
| 2 `/gear level` on a plain tool | Applied, narrower | `GearAdmin.run` refuses non-`gearish` items (B:10873) and the level action writes only `lvl` / `lvlA` (B:10903-10913) - confirmed. Fixed with a LOCAL guard in `GearAdmin.run` + `tl` = 1; the suggested global `gearish` extension is rejected because `gearish` also gates `GearFns.docOf` (B:7298), the `gear:fn:*` bridge SkyyAuctions reads (stampStack's second guard B:6899 is real but not the only caller). |
| 3 sickle gate stops mob hits | Applied (2.2, 2.3, R4, R5, Q2) | Both sickle selectors carry `HitBlock` and `HitEntity` (Assets.zip). The gate moved into selector copies (HitBlock only, root + swings untouched); `tool.farmLock` default off until stage 0. One correction to the critic: R9 does switch off with the row (the marker is never put on); what stays is the override files. |
| 4 Creative / staff and the lock | Applied | The `Hoe_Till` root has a `Creative` settings branch (Assets.zip); `GearToolFx.lock` skips Creative and honours `tool.staffBypass`. |
| 5 null item on F-pickups | Applied (2.1, 4.2) | `performPickupByInteraction` builds `new BreakBlockEvent(null, ...)` (341-349); a jar scan finds only it and `performBlockBreak` 35. Null = no change. |
| 6 harness runs the real handle() | Applied (AD1) | 0.2.1 AD3(b) runs the real `GearHitSys.handle` on an ECS shim (test l.5930-6103); the 0.2.1 test has 0 `BlockType` / `ItemTool` mentions, so fixtures are named (`fake_item` + public `ItemToolSpec` / `ItemTool` constructors; `BlockType.CODEC.decodeJson` as AB8 l.5305, or `BlockBreakingDropType`'s public constructor). |
| 7 Scrap / Steel_Rusty | Applied (1, 3.2, R17) | Reproduced: the nine ladders need Scrap excluded; with it the Lv 10 points and the Copper Lv 10 ore hits change exactly as the critic says; the Scrap pickaxe numbers (stone 10 -> 3, dirt 10 -> 2, ores at its own 0.334 / 0.167) too. |
| 8 "exactly vanilla at band starts" | Applied (0, 3.2) | Reproduced 20 of 113 (float model): the critic's list exactly. Reworded to "never below vanilla; equal for the main blocks". |
| 9 `tool.legacyLenient` scope | Applied (0, 7, 9, R15, Q4) | Plain weapons are strict (`effective` -> `legacy(id)` B:5991, `GearHit.judge` B:7632-7653). Question 4 added, default lenient kept, texts fixed; also offered the middle option the code can tell apart (0.2-crafted documents only). |
| 10 rename of a locked answer | Applied (0, 5.1, 5.3, 8, Q1) | Answer 3 says Mining / Chopping Speed; catalog lock 31 Breaking Power "lets you mine harder blocks" (Stat-Catalog l.167); R9 "no sickle / gear swing-speed for now" (OPEN-QUESTIONS l.98). Default label = Skyy's; Q1 settled before the build. Keys `mpow` / `cpow` stay (mechanism names, saved in documents). |
| 11 pickup event has no position | Applied (2.3, Q3, R3) | `InteractivelyPickupItemEvent`: one field `itemStack`, one constructor `(ItemStack)`; `HarvestGate.claim` keys on position (S:8339); SkyyCollections' 2 s `UseBlockEvent$Post` window (C:2788-2820). |
| 12 popup needs a PlayerRef | Applied (2.1, 2.4) | `GearGate.popup` sends through `pr.getPacketHandler()` (B:5069-5081). Resolved with `Universe.get().getPlayer(uuid)` as `Gear.tell` (B:2699) and GearHitSys (B:8541) do - not "as GearRefreshTask does": that task is built with a PlayerRef (B:9601) and never looks one up. |
| 13 "generated at build time" vs live rows | Applied (3.1, 3.2) | Ladder built at run time from the live item map + live band table, cached on the config epoch; the build only asserts the default output. |
| 14 cap "near 90+" | Applied (4.3) | 84 (Foraging) and 85 (Farming) recomputed. |
| 15 Heavy Hatchet | Applied (0, 3.3, Q5) | Reproduced: Iron Lv 20 + HH max = 1 hit; smallest rolls listed. |
| 16 stale B1 lines | Applied | `TOOL_FAMILIES` B1:816, `GATE_BY_KIND` B1:801, `ENFORCED_KINDS` B1:805 in the 22:19 file. |
| 17 "proven pattern" | Applied (2.2, R16) | T 0.2.3 header l.75 and 0.2.4 l.166 mark the client side UNVERIFIED; HANDOFF 2026-09-25 06:53 says so; no result recorded. |
| M1 0.7 check | Applied (2.5) | Verified on the pre-release jar / Assets.zip. Two precisions: `markNeedsSaving` is `ChunkSection.markNeedsSaving` called from `damageSingleBlock` (1558), not a `BlockHealthSection` member; the new `applyItemDurabilityLoss` argument is an `ActiveSlotInventoryComponent`. Added: `Hatchet_Chop` also gained `Trigger_Explosion_State_Generic`; the sickle items' selector vars are unchanged. |
| M2 one-time notice | Applied (9) | Pattern: `note.swing` (T) / `GearNotice` (B:6628ff); `GearNotice.run` writes the whole players file (B:6655), so the writer becomes read-merge-write. |
| M3 `/gear read` | Applied (6) | `GearAdmin.read` (B:10828) has no tool output today. |
| M4 missing tests | Applied (AD1, AD3, AD9) | Null item, hotbar-section filter, Creative / staff / row-off for the lock. |
| Editor's own | Applied | (a) The 3.3 examples used +30 % power rolls a Lv 13-18 tool cannot roll (Lv 13 max 19, Lv 18 max 23, `GearRoll.bounds` B:5689 + rarity table B:628) - now +16 %. (b) The OreMithril ladder row was missing from the table. (c) All four sickles' selector vars inline-`Parent` the vanilla selectors (the fact the new sickle design rests on). |
