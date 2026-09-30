# Pre-release compatibility report: will the Skyy mods run on the beta?

Research only (2026-09-30). No code changed, nothing built, committed or deployed.

| | Release (what the pack runs on) | Pre-release (the beta with runes) |
|---|---|---|
| Server version | 0.6.8 (rev d2feeb39) | 0.7.0-pre.4 (rev fab7fc95) |
| Java | Temurin 26.0.2 | Temurin 26.0.2 (same) |
| Engine classes (com.hypixel) | 9,921 | 10,238 (46 removed, 363 added) |
| Assets.zip entries | 60,695 | 65,575 (793 removed, 5,673 added, 2,019 changed) |

Live set checked: the 23 pins in `tools/deploy_set.py` SET (945 classes). Pack mods checked: More Crossbow Tiers 1.1.0 and
Saplings From Trees 1.0.4.

## 1. Bottom line

- **Every class loads, passes the verifier and links.** No class fails in any of the 23 jars. The plugin manifest format did
  not change, and `"ServerVersion": "*"` still matches 0.7.0-pre.4. I tested this against the pre-release's own semver code.
- **3 engine methods the mods call no longer exist** (5 call sites in 3 mods). Nothing crashes at load time, because Java
  only resolves a method the first time that line runs:
  - **SkyyIslands (serious):** a new player's island comes out **empty**. There are no blocks, no chest and no starter
    kit, so the player spawns over the void. Relight also quietly stops working, and `/hub` with no `/sethub` hub throws
    an error.
  - **SkyyMenu:** the Menu "Spawn" button throws an error.
  - **SkyyProfiles:** the spawn fallback after a profile switch fails. It only runs when SkyyIslands is missing.
- **UI kit:** `SUI.verify()` fails 1 of 273 checks on the pre-release. The vanilla value is unchanged: new "Runic" blocks were
  inserted next to the text the check looks for. It only stops builds, not the running mods. The fix is one line in
  `tools/skyyui.py`.
- **Assets:** 3 item ids used as UI icons are gone (SkyyMenu Bank tile, SkyyExploration card, SkyyTrees 2 nodes). The
  vanilla files SkyyTrees overrides (Hatchet_Attack, Pickaxe_Attack roots) did **not change** between the release and the
  pre-release (byte-identical).
- **Design changes Skyy must decide on (not crashes):**
  - Vanilla Mana goes from max 0 to **max 100 for every player**. SkyySkills' Base Mana then adds nothing.
  - Vanilla food buffs now last **360 s** (they were 45 s or 150 s).
  - Eating takes 2.5 s (was 2.0 s) and damage no longer interrupts it.
  - The vanilla Abilities, Mana, Stamina and Hotbar HUD was redone.
- **Pack mods:**
  - More Crossbow Tiers: OK.
  - Saplings From Trees: blue fig leaves lose their texture (a renamed vanilla file). It also hides 3 small vanilla leaf
    tweaks.

## 2. How it was checked

1. **Load / verify / link (bare JVM):** I used the pre-release JRE with `-Xverify:all`, `-XX:-UsePerfData` and only the
   pre-release `HytaleServer.jar` on the classpath. Each mod jar got its own `URLClassLoader`.
   - Every class was loaded and linked through reflection. This runs the bytecode verifier and loads every type in the
     method signatures.
   - Every constant-pool reference was then resolved by JVM rules against the pre-release: 20,556 method/field references
     and 3,071 outside class references. This catches what verification cannot: NoSuchMethodError, NoSuchFieldError,
     NoClassDefFoundError and IncompatibleClassChangeError (a Methodref pointing at an interface, and the reverse).
   - Also checked:
     - abstract methods a mod class no longer implements (AbstractMethodError);
     - mod methods that stop overriding an engine method because its signature changed (they would silently never be
       called);
     - whether each of the 23 engine event classes the mods listen to is still created by the engine.
   - The same run against the release jar was the control. It found 0 problems, so the checker is sound.
2. **Build-script names:** the 23 build scripts name 277 distinct `com.hypixel.hytale...` classes. All of them still exist.
3. **Behaviour:** I compared the bytecode of all 682 engine methods the mods call, release against pre-release. 8 differ, and
   none of them hurt the mods (list in section 5).
4. **Vanilla look:** `SUI.verify(<pre-release Assets.zip>, <pre-release Client\Data\Game\Interface>)`, then a diff of every
   document, texture, sound and quality file the kit copies.
5. **Assets:** every string in the mods (class constants plus asset JSON values, split into words) was compared with every
   asset id and path in both Assets.zip files, per category (items, interactions, root interactions, sound events, effects,
   qualities, NPC roles, drops, particles, models). Also checked:
   - vanilla files the mods override, and vanilla files the mods inherit from (Parent) that changed;
   - JSON keys the mod assets use, against the engine's codec strings;
   - vanilla translation keys;
   - zone Discovery blocks (still 27, unchanged).
6. **Pack mods:** the same asset checks. Both are asset-only zips with no code.

## 3. Per-mod results

OK = loads, links, no vanished asset ids, no behaviour change found. Line numbers are in the pinned build script.

| Mod | Pin | Result | What, where, smallest fix |
|---|---|---|---|
| SkyyHud | 0.3.10 | OK (check in game) | Code and assets OK. The vanilla HUD changed (Abilities, Mana, Stamina, Hotbar, Chat, Reticle, BossBar documents), and the Mana bar now shows for everyone (max 100). Re-check the default widget layout for overlaps in game (UNVERIFIED). |
| SkyySacks | 0.7.7 | OK | - |
| SkyyCoins | 0.1.5 | OK | - |
| SkyyCollections | 0.2.4 | OK | Uses `ChunkStore.getStore/getChunkSectionReferenceAtBlock`: these moved to the new superclass `ChunkGrid` and still resolve. |
| SkyyParty | 0.1.6 | OK | - |
| SkyyBank | 0.1.4 | OK | - |
| **SkyyIslands** | 0.5.4 | **BREAKS (3)** | See 3a. |
| SkyyBazaar | 0.1.2 | OK | - |
| SkyyGear | 0.1 | OK | `EffectControllerComponent.addEffect` and `ItemComponent.setItemStack` changed inside but behave the same (section 5). Four engine system classes named by string for ordering still exist. |
| SkyySkills | 0.4.7 | OK (design) | Code OK. Base Mana: see 3c. The crossbow template fields the build asserts on are unchanged. |
| SkyyAccessories | 0.4.5 | OK | Inherits from vanilla items that changed a little (crop items, Ingredient_Voidheart got ItemLevel 30). Nothing breaks. |
| SkyyClasses | 0.1.8 | OK | - |
| **SkyyMenu** | 0.3.3 | **BREAKS (1) + icon** | 1) `MenuPage.doSpawn` (l.3717) calls the removed `ISpawnProvider.getSpawnPoint(World, UUID)`. Pressing Spawn throws NoSuchMethodError. Fix: see 3b. 2) The icon `Furniture_Ancient_Chest_Large_Treasure` is gone (Bank tile l.208 and the Mods list l.428). Use `Furniture_Ancient_Chest_Large`, which exists in both versions. A rebuild on the new game also stops at the build-time `B.probe(... ISpawnProvider, "getSpawnPoint")` (l.1604). That is a good guard, but update it with the fix. |
| SkyyEssentials | 0.1.5 | OK | Warp and WorldReturnPoint constructors are unchanged. |
| **SkyyProfiles** | 0.1.3 | **BREAKS (1, low)** | `ProfSwitch.travel` (l.1688) uses the fallback teleport to the world spawn only when `/island` cannot be resolved. It calls the removed `getSpawnPoint`. The `catch (Throwable)` logs "fallback teleport after a switch failed" and the player stays put. Fix: see 3b. It never runs while SkyyIslands is in the pack. |
| SkyyCooking | 0.1.2 | OK (balance) | Assets OK. Dishes inherit vanilla `Consume_Charge_Food_T1_Inner`: eating now takes 2.5 s instead of 2.0 s, damage no longer interrupts it, and walk speed while eating went from 0.4 to 0.75. The vanilla buffs your EffectCondition gates compare against (HealthRegen / Meat / FruitVeggie T1 and T2) now last 360 s (were 45 s and 150 s). This needs a balance look. Vanilla foods also now play a one-shot `ConsumeSide` animation, while the dishes still override `Consume` with Looping true. Cosmetic only. |
| SkyyTrees | 0.2.5 | OK + icon + 1 small drift | 1) Icon `Glider` is gone (the Glider item was removed) on the Acrobatics nodes RFall "Soft Landing" and RDodge2 "Evasion" (l.813, l.822). Use `Template_Glider`, which exists with an icon in both versions. 2) The vanilla `Hatchet_Attack` / `Pickaxe_Attack` root files that SkyyTrees overrides did not change in the pre-release, and every vanilla id the SkyyTrees interactions point to still exists. 3) `Skyy_Tree_Chop.json` is a copy of the release `Hatchet_Chop`. The pre-release added one line, `"Trigger_Explosion_State_Generic"`, to vanilla `Hatchet_Chop` (vanilla `Pickaxe_Mine` too). It is the first entry of the first Parallel branch, before the hit Selector: a ChangeState that sets the targeted block to "Exploding". With the SkyyTrees chain, a hatchet swing no longer triggers explosive blocks. Fix: add that one line at the same spot in the copy. The pickaxe chain points at vanilla and needs nothing. |
| SkyyExploration | 0.2.2 | OK + icon | Icon `Objective_Treasure_Map` is gone (`CARD_ICON`, l.597; `must()` also stops a rebuild on the new game). Use `Deco_Treasure` or `Deco_Treasure_Pile_Small`, which exist in both versions (check that the icon looks right). The engine banner call `EventTitleUtil.showEventTitleToPlayer(..., boolean)` still exists: the boolean now maps to the new EventTitleStyle Default or Major. The 27 zone Discovery blocks and the StashSystem ordering are unchanged. |
| SkyyGuilds | 0.1.4 | OK | - |
| SkyyVault | 0.1.4 | OK | The ItemStack / MoveTransaction / SlotTransaction constructors and the ItemStack codec keys are unchanged. |
| SkyyAuctions | 0.1.2 | OK | - |
| SkyyRanks | 0.1.1 | OK | The permission group string `hytale:Adventurer` still exists in the engine. |
| SkyyUiProbe | 0.2 | OK | - |

### 3a. SkyyIslands 0.5.4: three breaks

| # | Where | What happens on the pre-release | Smallest fix |
|---|---|---|---|
| 1 | `FillTask.put` (l.2382): `chunk.setBlock(x, y, z, id)` | `WorldChunk.setBlock(int,int,int,String)` was removed. Only `setBlock(int,int,int,int,BlockType,int,int,int)` is left. The NoSuchMethodError is swallowed by `catch (Throwable) { return 0; }`. Every new island then logs "starter island placed ... (0 blocks)": no grass, stone, tree or chest, the starter kit has nowhere to go, and the player arrives at y=129 over the void. | Replace the body with `int bid = BlockType.getAssetMap().getIndex(id); return chunk.setBlock(x, y, z, bid, (BlockType) BlockType.getAssetMap().getAsset(bid), 0, 0, 0) ? 1 : 0;`. This is exactly what the engine's own String version does. The 8-argument method exists in the release **and** the pre-release, so one jar works on both. |
| 2 | `RelightNow.run` (l.2438): `invalidateLightInChunk(world.getChunkStore(), cx, cz)` | Removed and swallowed by `catch (Throwable)`: "relight queued ... (0/9 chunks)" and nothing is relit. | `world.getChunkLighting().invalidateLightInChunkSections(world.getChunkStore(), cx, cz, 0, 10)`. The release's removed method did exactly this call inside. It only exists in the pre-release, so for one jar on both, try it first and catch NoSuchMethodError to fall back to the old call. |
| 3 | `HubCmd.sendToHub` (l.2488): `getSpawnProvider().getSpawnPoint(target, uuid)` | Removed. It is now `getSpawnPointAsync(World, UUID)`, which returns a `CompletableFuture<Transform>`. The call throws out of `/hub` and every caller of sendToHub (l.2709, 2769, 4983, 5330) when no `/sethub` hub is set. | See 3b. |

### 3b. The spawn-point fix (SkyyIslands, SkyyMenu, SkyyProfiles)

The pre-release has a ready-made helper: `SpawnUtil.teleportToSpawn(ref, componentAccessor, targetWorld, currentWorld,
null)` (class `com.hypixel.hytale.server.core.universe.world.SpawnUtil`).
- It resolves the async spawn point.
- It then adds the Teleport component on the current world's thread. Vanilla `InstancesPlugin.teleportPlayerToInstance`
  now does the same through `SpawnUtil.teleportWhenResolved`.
- Replace `getSpawnPoint(...)` + `addComponent(Teleport.createForPlayer(...))` with that call and treat it as "sent".
- Do **not** `join()` the future on the world thread. `FitToHeightMapSpawnProvider` completes it later, which can deadlock.
  `Global` and `Individual` providers complete right away, which is why islands (Global) are fine.
- SpawnUtil exists only in the pre-release. For one jar on both versions, wrap the old call in `try` and catch
  NoSuchMethodError to reach the new one. Java resolves each call only when it runs.

### 3c. Mana (SkyySkills, and anything that spends Mana)

The pre-release `Server/Entity/Stats/Mana.json` changed:
- InitialValue and Max went from 0 to 100.
- A Creative-mode regen block was added.
- `UseIgnoreFlag` was added on the Charging condition.

SkyySkills posts Base Mana as `base - vanilla max`, floored at 0 (l.4060). With a vanilla max of 100 that is 0, so every
player gets 100 Mana whatever their class, and Overall Level Mana adds on top. The build already prints "NOTE FOR SKYY:
vanilla max Mana is 100" in that case. This needs a Skyy decision:
- keep vanilla 100;
- re-scale Skyy's numbers; or
- push Max down with a negative modifier.

## 4. Shared UI kit (`SUI.verify` on the pre-release)

- **Result: 1 failure out of 273 style values.** All 97 kit textures and sounds are present and byte-identical. The 11 item
  quality files are identical. All 14 client reference values pass.
- **The failure:** the check "the container close X ships hidden" (`tools/skyyui.py` l.2612) looks for
  `Visible: @CloseButton; } }; @PageOverlay`. The pre-release inserts new blocks between `@DecoratedContainer` and
  `@PageOverlay`: `@RunicContainer`, `@RunicPanel`, `@RunicCheck*`, `@RunicTitleStyle`, `@RunicHeadlineStyle` and
  `@RunicBodyStyle`. **The close button itself is unchanged** (`@CloseButton = false`, same button style).
- **Smallest fix:** keep everything up to `Visible: @CloseButton;\n  }\n};` but anchor it on the text in front instead of
  `@PageOverlay`. For example, this string matches exactly once in **both** versions:
  `'    Background: "Common/ContainerDecorationBottom.png";\n  }\n\n  Button #CloseButton {'` ... through
  `'    Visible: @CloseButton;\n  }\n};'`. Or check `'@DecoratedContainer = Group {\n  @ContentPadding = Padding(Full: 9 + 8);\n  @CloseButton = false;'`.
  Then run `tools/skyyui_test.py`.
- **Other kit documents:** 2 more changed but no kit value in them moved.
  - `PortalDeviceActive.ui`: new `#EntriesRemaining` label, and the close button got Bottom: 25.
  - `PortalDeviceSummon.ui`: `#BreachTimeBullet` became `#EntryLimit`.
- **Client docs:** `InGame/Common` and `InGame/Tooltips/ItemTooltip` renamed "Cursed" to "Ephemeral". No Skyy mod uses it.
- **UI markup:** no property name disappeared from any vanilla `.ui` document. One new property is `ShowItemTooltip`.

## 5. Engine diff for everything the mods reference

- **Removed (breaks):**
  - `WorldChunk.setBlock(IIILjava/lang/String;)Z`
  - `ChunkLightingManager.invalidateLightInChunk(ChunkStore,II)Z`
  - `ISpawnProvider.getSpawnPoint(World,UUID)Transform`
- **Moved but still resolving:** `ChunkStore.getStore()`, `getChunkSectionReferenceAtBlock(III)` and `getWorld()` now live
  in the new superclass `ChunkGrid` (SkyyCollections, Islands, Gear, Skills, Trees, Exploration). No change needed.
- **Nothing else changed:** no class, field, modifier (static, visibility) or class-versus-interface change on any
  referenced member.
- **No new abstract methods** in any engine supertype a mod class extends or implements.
- **No lost overrides.**
- **All 23 event classes are still fired** (BreakBlockEvent, PlaceBlockEvent, PlayerReadyEvent, PlayerChatEvent,
  CraftRecipeEvent, UseBlockEvent, the warp events, and so on).
- **Bytecode changed in 8 of the 682 called engine methods, all harmless:**
  - `EffectControllerComponent.addEffect(...)`: now forwards to a new overload that also records an owner (null for us).
    Same logic.
  - `EffectControllerComponent.removeEffect`: constant-pool reshuffle only.
  - `InstancesPlugin.spawnInstance(4 args)`: forwards to a new 5-argument overload (extra callback, null). The template
    lookup (`Server/Instances/<name>/instance.bson`) is unchanged, and the vanilla `Default_Void` template is
    byte-identical, so `SkyyIsland` (Version 4, Void, Global spawn) still loads.
  - `InstancesPlugin.teleportPlayerToInstance`: the teleport is now asynchronous through SpawnUtil. SkyyIslands does
    nothing right after the call, so no impact.
  - `ItemComponent.setItemStack`: now also resets a merge range. No impact.
  - `ChunkGrid` getters: only the class name changed.
- **New vanilla top-level commands:** `/abilities`, `/beam`, `/knockback`, `/wilderness`, `/ephemeral`. None clash with
  a Skyy command. **Do not name the class-abilities command `/abilities`.**

## 6. Asset-level dependencies

- **Vanished ids the mods use (category-aware, no false hits left):**
  - SkyyMenu: `Furniture_Ancient_Chest_Large_Treasure`
  - SkyyExploration: `Objective_Treasure_Map`
  - SkyyTrees: `Glider`

  The other removals do not touch the Skyy set:
  - 6 items, 55 interactions, 23 root interactions, 5 sounds, 23 NPC roles (mostly old goblins and the Goblin dungeon)
    and 4 drop lists.
  - This includes the vanilla `Double_Jump` interaction, which SkyySkills and SkyyTrees do not use.
- **Overrides of vanilla files:**
  - SkyyTrees `Hatchet_Attack` and `Pickaxe_Attack` root interactions: the vanilla files did not change in the
    pre-release. No other Skyy asset shares an id with a vanilla asset, and no new vanilla id collides with a Skyy id.
  - `Hatchet_Chop`, `Hatchet_Chop_Damage`, `Hatchet_Chop_Effect`, `Chaining`, `None`, `Pickaxe_Attack` all still exist.
  - `Hatchet_Chop` and `Pickaxe_Mine` gained the explosion trigger (see SkyyTrees).
  - `Block_Break`, which SkyyTrees points to, is now Serial [explosion trigger, camera effect]. It is inherited, so fine.
- **Changed vanilla parents the mods inherit from:**
  - SkyyCooking: food charge, food buffs, food items.
  - SkyyAccessories: crop items, Voidheart.
  - SkyyMenu, Cooking, Vault: the `Item` animation set, which gained ConsumeSide / ConsumeDisgust.
  - None of these break anything. Cooking needs the balance look above.
- **Qualities:** unchanged. The Skyy quality files use the same keys.
- **JSON keys:** every key the mod assets use still exists in the engine. `Family` is a custom key and was already ignored
  on the release.
- **Translation keys:** no vanilla key a mod uses was removed.
- **Sounds:** all sound events the mods name still exist. 487 vanilla sound events were retuned (volume and content), which
  is not a break.
- **Hatchets and pickaxes:** the vanilla tools gained "IsIncorrect" gather entries (a poor-hit sound on the wrong
  material). SkyyTrees reads the block's gather type, not the tool's, so it is unaffected.
- **Damage types:** new Fire / Earth / Water / Wind / Lightning / Crush damage types (`Server/Entity/Damage`, and
  `Server/Abilities/Elements`). They collide with nothing, and are worth knowing for SkyyGear's element stats.

## 7. Pack mods (UserData\Mods, read-only)

| Mod | Result | Details |
|---|---|---|
| More Crossbow Tiers 1.1.0 (`More_Crossbow_Tiers.zip`) | OK | Assets only. All parents and the 4 InteractionVars names (`Standard_Projectile_Damage`, `Combo_Projectile_Damage`, `Signature_BigArrow_Damage`, `Guard_Wield`) still exist in the pre-release crossbow files. It inherits the new crossbow template: reload moved from the Ability3 to the Ability4 slot, and some base damage and durability values changed. Its `"ServerVersion": "~0.5.6"` fails on the release as well: warning only, the same as today. |
| Saplings From Trees 1.0.4 (`SaplingFromTrees-1.0.4.zip`) | BREAKS (cosmetic) | 1) Its `Plant_Leaves_Fig_Blue` override points at `Blocks/Foliage/Leaves/Ball_Textures/Fig_Blue_.png`. The pre-release renamed that file to `Fig_Blue.png`, so blue fig leaves show a missing texture. 2) It overrides 43 vanilla leaf items, and 4 of them changed in the pre-release: Fig_Blue, Oak (texture weight 1 to 4), Palm_Arid and Palm_Oasis (`UseDefaultDropWhenPlaced` removed). The override brings back the release versions. 3) It declares no `ServerVersion`, which gives a warning today; the engine says this "will be a hard error in the future". Fix: an update from its author. We cannot patch a third-party pack. |

## 8. What to do when the beta becomes the release

`tools/skyybuild.py` and `tools/skyyui.py` read `install\release\...`, so the first build after the game update runs
against the new jar automatically.

1. **SkyyIslands next version (patch script):** the FillTask `setBlock` fix (works on both versions), the RelightNow fix and
   the sendToHub fix (3a, 3b). This is the only must-fix: without it no new player gets an island.
2. **SkyyMenu next version:** the `doSpawn` fix, the Bank icon swap (both places) and the probe update.
3. **SkyyProfiles next version:** the `travel` fallback fix (low priority).
4. **`tools/skyyui.py` l.2612:** re-anchor the close-button check (section 4), run `tools/skyyui_test.py` and bump
   KIT_VERSION. Every UI build stops at `SUI.verify()` until this is done.
5. **Icons:** SkyyExploration `Objective_Treasure_Map` to `Deco_Treasure`; SkyyTrees `Glider` to `Template_Glider`. Both
   ids exist on the release too, so this can ship early.
6. **SkyyTrees:** add `"Trigger_Explosion_State_Generic"` to `Skyy_Tree_Chop.json` as the first entry of the first Parallel
   branch, the way vanilla `Hatchet_Chop` has it.
7. **Skyy decisions (OPEN-QUESTIONS):** the Mana base (vanilla now gives 100) and a Cooking balance pass (eat time,
   vanilla buffs at 360 s).
8. **Rebuild every pinned mod** against the new jar. Expected build stops are guards doing their job:
   - the SkyyMenu `getSpawnPoint` probe;
   - javassist compile errors on the SkyyIslands calls;
   - the Exploration / Trees / Menu `must()` item-id checks.
9. **Gate the update with a link check like section 2.1.** The scratch tooling was deleted as the task rules say. A
   permanent `tools/dev/linkcheck.py` would make this a one-command check (separate task).
10. **In-game test on the new version:**
    - a brand-new player's `/island` (blocks, chest, kit);
    - `/hub` with no `/sethub`;
    - Menu -> Spawn;
    - a profile switch;
    - the island relight;
    - the SkyyHud layout next to the new vanilla Abilities / Mana HUD;
    - the three swapped icons.
11. **Pack:** ask for (or wait for) a Saplings From Trees update. More Crossbow Tiers is fine.

## 9. UNVERIFIED / limits

- What the client shows for an `ItemIcon` whose ItemId no longer exists: probably an empty icon, possibly a client error
  when the page opens. Swapping the 3 ids removes the question.
- Only the direct engine methods were bytecode-diffed, not everything they call. Runtime behaviour on the pre-release was
  not played in game.
- The SkyyHud overlap with the new vanilla HUD needs eyes in game.

## 10. Pointers for the runes / class-abilities research (seen while scanning, not checked in depth)

- **Items:** new `Server/Item/Items/Rune/Ability/*`, for example Rune_Fireball, Rune_GroundSlam, Rune_Enrage, Rune_WindStrike,
  Rune_ChainHook, Rune_ChargedShot and Rune_PoisonImbue. Modifier runes live in `Rune/Modifier/*`, for example
  Rune_Aoe_Up and Rune_Convert_Lightning.
- **Elements:** `Server/Abilities/Elements/{Earth,Fire,Lightning,Water,Wind}`.
- **Interaction slots:** weapons have Ability1 to Ability4 slots. The crossbow reload moved Ability3 to Ability4.
- **Mana:** base Mana is now 100.
- **UI:** new pages `AugmentUpgradePage`, `AugmentOptionButton`, `AugmentCostSlot` and `AugmentMessagePage`. New client
  pages `InGame/Pages/Abilities/AbilityBenchPanel.ui` and `RuneBagPanel.ui`. New vanilla "Runic" UI styles in `Common.ui`
  (`@RunicContainer`, `@RunicPanel`, `@RunicTitleStyle` and more), which the vanilla-look kit could adopt for class-ability
  pages.
- **Admin command:** `/abilities give`.
