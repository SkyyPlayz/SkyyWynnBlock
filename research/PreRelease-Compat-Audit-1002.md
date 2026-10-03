# 0.7 pre-release compatibility audit (2026-10-02)

Research only. No mod code changed, nothing built, deployed or committed. This updates `research/PreRelease-Compat-Report.md`
(2026-09-30, 23 pins) for the current 24-jar set and adds checks that report did not run.

| | Release (control) | Pre-release |
|---|---|---|
| Server jar | 0.6.8, rev d2feeb39, `install\release\...\Server\HytaleServer.jar` (2026-09-21) | 0.7.0-pre.4, rev fab7fc95, `install\pre-release\...\Server\HytaleServer.jar` (2026-09-30) |
| JRE | Temurin 26.0.2+10 | Temurin 26.0.2+10 (same) |
| Notes | | The same pre-release build the 09-30 report used. No newer pre-release is installed on this PC. |

Set checked: the 24 pins in `tools/deploy_set.py` SET (2026-10-02). That is 1,057 classes in jars next to their build scripts. All 24
jars are present (`deploy_set.py --check`).

## 1. Bottom line

- **Everything loads.** All 1,057 classes load, link and pass the bytecode verifier (`-Xverify:all`) on 0.7, the same as on 0.6.8.
  The checks covered:
  - 1,043 distinct engine member references (3,428 per-mod, per-opcode rows);
  - 406 engine classes;
  - 892 engine methods the mods reach.

  Every one of them resolves on 0.7 with the same signature, access and static/instance kind, except the 3 below.
- **BROKEN (same 3 engine methods as on 09-30, still in the current pins):** 5 call sites in 3 mods. None of them fail at load time;
  each throws the first time its line runs.
  - **SkyyIslands 0.5.5 (serious):** a new island comes out empty, relight does nothing, and `/hub` with no `/sethub` hub fails.
  - **SkyyMenu 0.3.5:** the Spawn button throws.
  - **SkyyProfiles 0.1.5 (low):** the fallback teleport after a profile switch fails. It only runs when SkyyIslands is missing.
- **New since 09-30:**
  1. **`PlayerConnectEvent` is now an async event.** It moved from `IEvent` to `IAsyncEvent`. SkyyProfiles' join hook still runs,
     and still runs before the player enters a world, but it may now run on another thread. RISKY.
  2. **SkyyMobs 0.1 (new mod) works on 0.7.**
     - Its zone lookup `BlockChunk.getEnvironment` is deprecated in 0.7, but it still returns the right value.
     - 12 vanilla roles it levels are gone in 0.7, and 37 new 0.7 roles get no level until a rebuild.
  3. **A release-day rebuild stops in 9 build scripts on 0.7 data:** Skills, Cooking, Gear, Collections, Classes, Exploration, Trees,
     Menu and Mobs. Mostly this is vanilla content the scripts count or check, plus rune abilities that cost Mana.
     - Islands, Menu and Profiles also stop with compile errors on the 3 removed methods.
     - 15 kit-using scripts stop at `SUI.verify()` (the kit check, `tools/skyyui.py` l.2612).
  4. **SkyyUiProbe 0.3 probe 24** throws IllegalAccessError on **both** versions. This is not a 0.7 issue (section 4).
- **Verdicts:**
  - **BROKEN 3:** Islands, Menu, Profiles.
  - **RISKY 9:** Skills, Cooking, Gear, Collections, Classes, Exploration, Trees, Mobs, Hud. Profiles is RISKY as well as BROKEN.
  - **OK 12:** Sacks, Coins, Party, Bank, Bazaar, Accessories, Essentials, Guilds, Vault, Auctions, Ranks, UiProbe.

## 2. How it was checked

All tools ran from `tools/dev/scratch/compat-audit-1002/` with TEMP/TMP there and `-XX:-UsePerfData`. The folder was deleted
afterwards. Game files were only read.

1. **Constant-pool link check (pure Python).** Every class of every jar was parsed.
   - Every Fieldref, Methodref and InterfaceMethodref was taken from the instruction that uses it (invokevirtual, invokestatic,
     getfield, putstatic ...).
   - It was resolved by JVMS 5.4.3 rules against each server jar, with the mod's own classes overlaid and JDK classes read from the
     JRE. This includes calls whose owner is a mod class but whose method is inherited from an engine class.
   - Then checked:
     - access (public / protected-from-subclass / package / private) and class accessibility;
     - static versus instance;
     - writes to final fields, and `<init>` in the named class;
     - Methodref versus interface mismatches;
     - superclass / interface kind and final classes;
     - abstract methods a mod class no longer implements;
     - mod methods that stop overriding an engine method (would silently never be called);
     - engine-class hierarchy and flag drift;
     - deprecation added in 0.7.
   - The release run is the control. It finds one problem, and that one exists on both versions (SkyyUiProbe, section 4).
2. **JVM load / link / verify.** On the real JRE with `-Xverify:all`, each jar had its own URLClassLoader over one server jar.
   - Every class was loaded without its static initialiser running.
   - Each class was linked through reflection. `-Xlog:verification` showed that every mod class goes through the verifier.
   - Result: 1,057 / 1,057 OK on 0.6.8 and on 0.7.
3. **Behaviour diff.** The normalised bytecode of the 892 engine methods the mods reach was compared, release against pre-release.
   - The comparison is index-free: constant-pool order, invokedynamic bootstrap indexes and lambda numbering are ignored, and lambda
     bodies are included.
   - It then went one level deeper: the engine methods those methods call.
4. **Events.** For all 30 engine event types the mods reference, the checks were:
   - sync / async / ECS kind;
   - whether the engine still creates the type or a subclass of it (a `new` site).
5. **Strings and reflection.**
   - Engine class names in string constants still exist.
   - The engine systems the mods order against still exist and are still created.
   - Reflective fields the mods read are unchanged in 0.7:
     - Essentials' durability fields;
     - `HytaleAssetStore.cachedInitPackets`;
     - Skills' `StatsConditionBaseInteraction.rawCosts` and `costs`;
     - the Workbench-tab fields `CraftingBench.categories`, `CraftingPlugin.registries` and `BenchRecipeRegistry.categoryMap`.
   - Manifest keys and `"ServerVersion": "*"` are unchanged.
   - No new vanilla command clashes with a Skyy command or alias. The commands new in 0.7 are abilities, beam, ephemeral,
     wilderness, height, position and two marker debug commands.
6. **Assets.**
   - Every string in the jars (class constants plus JSON / lang values) was matched against asset ids that left a category between
     the two Assets.zip files.
   - Also checked:
     - the vanilla files the jars override;
     - the vanilla Parents they inherit from;
     - the JSON keys they use, against the engine's codec strings;
     - the island instance template keys.
7. **Release-day build dry run.** A differential, read-only check of the build scripts' own checks:
   - Each pinned build script was parsed. Every top-level statement ran on its own, with asserts recorded instead of stopping.
   - `install\release` paths were redirected to `install\pre-release` for the 0.7 run.
   - A javassist pool over the chosen server jar was provided, so the engine-fact and API probes ran too:
     - SkyySacks' bench-link engine facts and `skyywbtab.probe`;
     - SkyyGear's bytecode asserts;
     - SkyyEssentials' signature asserts;
     - every `B.probe`.
   - Every statement that builds a class or could write or delete anything was skipped: `makeClass`, `addMethod`, `writeFile`,
     `os.remove`, `open(...,'w')`, `subprocess`, deploy and assemble. Nothing was compiled into a class and nothing was written.
   - A check that fails only in the 0.7 run is a release-day build stop. The release run is the control: 0 failures happened only on
     release.
8. **`SUI.verify` on the 0.7 Assets.zip** with kit 1.4.

## 3. Overview (all 24 pins)

"Engine refs" = engine classes / member references checked. "Link 0.7" = constant-pool check. "Verify" = JVM load + link + verify.
"Rebuild" = what a build on 0.7 data would do.

| Mod | Pin | Engine refs | Link 0.7 | Verify | Rebuild on 0.7 | Verdict |
|---|---|---|---|---|---|---|
| SkyyHud | 0.3.11 | 61 / 102 | OK | 32/32 | OK | RISKY (in-game HUD check) |
| SkyySacks | 0.7.12 | 106 / 216 | OK | 47/47 | stops at SUI.verify only | OK |
| SkyyCoins | 0.1.5 | 27 / 36 | OK | 11/11 | OK | OK |
| SkyyCollections | 0.2.5 | 79 / 125 | OK | 48/48 | stops (2 asset counts) + SUI | RISKY |
| SkyyParty | 0.1.6 | 53 / 74 | OK | 29/29 | SUI only | OK |
| SkyyBank | 0.1.5 | 35 / 43 | OK | 12/12 | SUI only | OK |
| **SkyyIslands** | 0.5.5 | 102 / 175 | **3 missing** | 73/73 | compile errors (3) + SUI | **BROKEN** |
| SkyyBazaar | 0.1.2 | 43 / 57 | OK | 19/19 | OK | OK |
| SkyyGear | 0.2 | 195 / 375 | OK | 95/95 | stops (7 asset asserts) | RISKY |
| SkyySkills | 0.4.12 | 161 / 298 | OK | 99/99 | stops (spell costs) + SUI | RISKY |
| SkyyAccessories | 0.5.2 | 85 / 142 | OK | 31/31 | SUI only | OK |
| SkyyClasses | 0.1.10 | 98 / 148 | OK | 48/48 | stops (1 prefix) + SUI | RISKY |
| **SkyyMenu** | 0.3.5 | 68 / 136 | **1 missing** | 37/37 | compile error + probe + icon check | **BROKEN** |
| SkyyEssentials | 0.1.7 | 137 / 285 | OK | 69/69 | OK | OK |
| **SkyyProfiles** | 0.1.5 | 90 / 145 | **1 missing** | 45/45 | compile error + SUI | **BROKEN (low)** + RISKY |
| SkyyCooking | 0.1.3 | 54 / 68 | OK | 24/24 | stops (vanilla food self-check) | RISKY |
| SkyyTrees | 0.2.5 | 83 / 114 | OK | 33/33 | stops (Glider) + SUI | RISKY |
| SkyyExploration | 0.2.2 | 104 / 180 | OK | 81/81 | stops (icon + portal chest lists) + SUI | RISKY |
| SkyyGuilds | 0.1.6 | 41 / 58 | OK | 48/48 | SUI only | OK |
| SkyyVault | 0.1.5 | 93 / 166 | OK | 45/45 | SUI only | OK |
| SkyyAuctions | 0.1.2 | 82 / 163 | OK | 35/35 | OK | OK |
| SkyyRanks | 0.1.1 | 51 / 80 | OK | 51/51 | OK | OK |
| SkyyUiProbe | 0.3 | 80 / 123 | OK (see 4) | 16/16 | SUI only | OK (probe 24 bug on both versions) |
| SkyyMobs | 0.1 | 86 / 119 | OK | 29/29 | stops (1 role name) + SUI | RISKY |

## 4. Per-mod tables

Line numbers are in the pinned build script `<Mod>/build_<mod>_<ver>.py`.

"Moved to ChunkGrid" means the method now sits in the new superclass `ChunkGrid` of `ChunkStore`. Those calls still resolve, so they
need no change.

### SkyyHud 0.3.11 - RISKY (look only)
| Check | Result |
|---|---|
| Link / verify | OK: 102 refs, 32/32 classes. 22 engine overrides still override. |
| Behaviour | No reached engine method changed. `Player.getPlayerConnection` is deprecated in both versions. |
| Assets | None used. The vanilla HUD was redone in 0.7 (Abilities, Mana, Stamina, Hotbar), and the vanilla Mana bar now shows for everyone (max 100). |
| Rebuild | OK (no kit). |
| To do | Look at the default widget layout next to the new vanilla HUD in game (UNVERIFIED). |

### SkyySacks 0.7.12 - OK
| Check | Result |
|---|---|
| Link / verify | OK: 216 refs, 47/47. |
| Behaviour | None. The 7 deprecated inventory getters it uses are deprecated in both versions too. |
| Build engine facts | All 20 bench / pocket-link bytecode facts (l.560-640) and `skyywbtab.probe` pass on 0.7. |
| Assets | OK. Bag items, qualities and `Family` are a custom key, as before. |
| Rebuild | Stops only at `SUI.verify` (kit fix, section 7). |

### SkyyCoins 0.1.5 - OK
OK: 36 refs, 11/11. No behaviour, asset or rebuild issue.

### SkyyCollections 0.2.5 - RISKY
| Check | Result |
|---|---|
| Link / verify | OK: 125 refs, 48/48. `ChunkStore.getStore` and `getChunkSectionReferenceAtBlock` moved to ChunkGrid. |
| Assets (runtime) | 0.7 adds `Plant_Crop_Mushroom_Common_Lime_Large` and `Wood_Sadwillow_Trunk`. The current jar does not count them (not in its lists). |
| Rebuild | Stops at l.249 `assert len(MUSH) == 19` (now 20) and l.267 `assert len(TRUNKS) == 33` (now 34). A new Sadwillow log collection also needs its reward row. Also stops at SUI.verify. |

### SkyyParty 0.1.6 - OK
OK: 74 refs, 29/29. Rebuild stops only at SUI.verify.

### SkyyBank 0.1.5 - OK
OK: 43 refs, 12/12. Rebuild stops only at SUI.verify.

### SkyyIslands 0.5.5 - BROKEN
| Check | Result |
|---|---|
| Missing on 0.7 | 1) `FillTask.put` (l.2785) `WorldChunk.setBlock(int,int,int,String)`: removed. Caught by `catch (Throwable) { return 0; }`, so every new island logs "(0 blocks)": no blocks, no chest, no kit, the player arrives over the void. 2) `RelightNow.run` (l.2841) `ChunkLightingManager.invalidateLightInChunk(ChunkStore,int,int)`: removed and swallowed ("0/9 chunks"). 3) `HubCmd.sendToHub` (l.2891) `ISpawnProvider.getSpawnPoint(World,UUID)`: removed (now `getSpawnPointAsync`). It is only reached when no `/sethub` hub is set or loaded. `/hub` (l.5452) shows "Could not warp". The callers at l.3120, 3180 and 5799 log "could not send a player to the hub", "reset evacuation failed" and "login routing failed", and the player stays put. |
| Verify | 73/73 OK. |
| Behaviour | `InstancesPlugin.spawnInstance` (4 args) forwards to a new 5-arg overload. `teleportPlayerToInstance` and `teleportPlayerToLoadingInstance` now resolve the spawn point asynchronously. The logic is the same and Global spawn completes at once, so there is no impact. `ChunkStore.getStore` moved to ChunkGrid. |
| Assets | Instance template keys and `Default_Void` unchanged. |
| Rebuild | Javassist compile errors on the 3 calls, plus SUI.verify. |

### SkyyBazaar 0.1.2 - OK
OK: 57 refs, 19/19. No asset or rebuild issue.

### SkyyGear 0.2 - RISKY
| Check | Result |
|---|---|
| Link / verify | OK: 375 refs, 95/95, 87 overrides intact. `getStore`, `getWorld` and `getChunkSectionReferenceAtBlock` moved to ChunkGrid. |
| Behaviour | `ItemComponent.setItemStack` now also resets a merge range (harmless). One level deeper: `InteractionContext.getRootInteractionId` (used by `InteractionManager.walkChain`) now returns the rune ability's cast root for the new ability slot (section id -11). A rune cast can therefore never look like a charged weapon attack. Low. |
| Build engine facts | The UseBlockEvent$Pre, OpenContainer, BreakBlockEvent, PlacedBy and StatModifiersManager asserts all pass on 0.7. Every system it orders against still exists unchanged: ArmorDamageReduction, NPCDamageSystems$DropDeathItems, StashSystem, EntityStatsSystems$Recalculate. |
| Assets (runtime) | New 0.7 gear has no SkyyGear level rule, so it keeps Hytale's own item level: `Weapon_Bangstick` (Uncommon, ItemLevel 10, stacks) and `Weapon_Longsword_Ruined_Giant` (Common, 25). |
| Rebuild | Stops at: l.797 stackable-gear rule (Bangstick); l.1051-1052 level fallback for non-developer ids (Bangstick, Ruined_Giant + 2 NPC variants); l.1672 `CHG_FAMILIES` counts (Daggers 17/17, Longsword 21/20, Staff 25/23, Club 23/0). |

### SkyySkills 0.4.12 - RISKY
| Check | Result |
|---|---|
| Link / verify | OK: 298 refs, 99/99. `getStore` and `getChunkSectionReferenceAtBlock` moved to ChunkGrid. |
| Behaviour | `EffectControllerComponent.addEffect` forwards to a new owner overload (same logic). `Velocity.addInstruction` gained a `preMultiplier` that defaults to 1.0 (no change). |
| Build engine checks | The Mana / crossbow asset checks (l.1851-1870) pass on 0.7. The `StatsConditionBaseInteraction` field asserts (l.12155-12156) pass. |
| Mana (design) | Vanilla `Mana.json` Max goes from 0 to 100. Base Mana posts `target - vanilla max`, floored at 0 (l.5349), so every player has 100 Mana whatever the class (as on 09-30). Skyy decision. |
| Assets (runtime) | The jar's 40 generated vanilla overrides are copies of 0.6.8 files. On 0.7 they re-add the per-staff `Staff_Cast_Summon_Charged` var at Mana 10, which 0.7 removed from 21 staffs. That is harmless: it is the same cost the interaction override sets, and nothing else in those files changed. The new 0.7 `Weapon_Staff_Scrap_Lightbulb` and the rune abilities keep full vanilla Mana costs. |
| Rebuild | **Stops in SPELL GEN** (from the `with zipfile` block at l.2391): 1) "Halloween_Broomstick has 0 Mana cast check(s) and 1 drain(s) - expected exactly one of each" (l.2039). The 0.7 staffs only keep the drain var. 2) "Ability_ChargedShot_Release_1 (top): a Mana Costs 10 on a StatsCondition interaction that is not a known cast check" (l.2257). New rune interactions `Ability_ChargedShot_Release_1-4` cost 10 / 20 / 30 / 50 Mana. 3) The gate simulation (l.2365, called at l.2481) and the `Weapon_Staff_Wood` asserts (l.2439, l.2490-2491) fail after that. Also stops at SUI.verify. |

### SkyyAccessories 0.5.2 - OK
OK: 142 refs, 31/31. `skyywbtab.probe` passes. Parents changed a little in 0.7 (crops, Voidheart), with no break. Rebuild stops only at SUI.verify.

### SkyyClasses 0.1.10 - RISKY (small)
| Check | Result |
|---|---|
| Link / verify | OK: 148 refs, 48/48. `CommandBuffer.removeEntity` / `tryRemoveComponent` are unchanged (an earlier diff hit was a bootstrap-index false positive). |
| Assets (runtime) | `Flamethrower_Goblin` became `Weapon_Flamethrower_Scrap` (+ `_Dungeon`). It now falls under the catch-all `Weapon_` "that weapon" rule (still unassigned / blocked). The new `Weapon_Bangstick` falls under the same catch-all. |
| Rebuild | Stops at l.400 "weapon prefix Flamethrower_ matches no item" (UNASSIGNED l.278). Also stops at SUI.verify. |

### SkyyMenu 0.3.5 - BROKEN
| Check | Result |
|---|---|
| Missing on 0.7 | `MenuPage.doSpawn` (l.3984) calls `ISpawnProvider.getSpawnPoint(World,UUID)`, so pressing Spawn throws NoSuchMethodError. |
| Assets | Icon `Furniture_Ancient_Chest_Large_Treasure` is gone (Bank tile l.226, Mods list l.479). |
| Rebuild | Compile error, plus `B.probe` of `getSpawnPoint` (l.1770), plus "unknown vanilla item id: Furniture_Ancient_Chest_Large_Treasure" (l.749). |

### SkyyEssentials 0.1.7 - OK
OK: 285 refs, 69/69. Warp, WorldReturnPoint, SlotFilter and DeathSystems signatures are unchanged, and the durability reflection fields are unchanged. Its build asserts (l.540-625) pass on 0.7.

### SkyyProfiles 0.1.5 - BROKEN (low) + RISKY
| Check | Result |
|---|---|
| Missing on 0.7 | `ProfSwitch.travel` (l.2213) fallback `getSpawnPoint`. It only runs when `/island` cannot be resolved, and is caught ("fallback teleport after a switch failed"). |
| Event change | `ProfConnect` is registered with `registerGlobal(PlayerConnectEvent.class, ...)` (l.4340). On 0.7, `PlayerConnectEvent implements IAsyncEvent`. `EventBus.getRegistry` sends it to `AsyncEventBusRegistry`, which wraps the Consumer (`lambda$registerGlobal$0/1`), and `Universe.addPlayer` now runs `dispatchForAsync(...).dispatch(e).thenCompose(...)`. So the hook still runs, and still before the player enters a world, but on whatever thread completes the chain. `InstancesPlugin` registers an EARLY async handler that may resolve a return point later, for example for a player who logged out on an island instance. ProfJoin's file reads may then run off the join thread (UNVERIFIED which thread). |
| Rebuild | Compile error, plus SUI.verify. |

### SkyyCooking 0.1.3 - RISKY
| Check | Result |
|---|---|
| Link / verify | OK: 68 refs, 24/24. |
| Assets (runtime) | Dish parents changed in 0.7 (`Food_Wildmeat_Cooked`, `Food_Fish_Grilled`, `Food_Vegetable_Cooked`). The vanilla food buffs the gates compare against now last 360 s (were 45 / 150). `Food_Instant_Heal_Bread` is now `Percent` Health 10. Eating takes 2.5 s (same as 09-30). Balance look for Skyy. |
| Rebuild | Stops at self-check 4 (l.487): "vanilla effect Food_Instant_Heal_Bread no longer matches this build's expectation". The EXPECT table is at l.475-482. Follow-on checks l.746 and l.882 fail too. |

### SkyyTrees 0.2.5 - RISKY
| Check | Result |
|---|---|
| Link / verify | OK: 114 refs, 33/33. `EffectControllerComponent.addEffect` / `removeEffect` are harmless (removeEffect is an ldc / ldc_w change only). Moved to ChunkGrid: `getStore`, `getChunkSectionReferenceAtBlock`. |
| Assets | Icon `Glider` is gone as an item (l.813 RFall, l.822 RDodge2). An item *animation* named Glider was added, which hid it from a category-blind scan. The `Hatchet_Attack` / `Pickaxe_Attack` overrides match vanilla 0.7 byte for byte. `Skyy_Tree_Chop.json` still lacks vanilla 0.7's `"Trigger_Explosion_State_Generic"`, so hatchets do not trigger explosive blocks. |
| Rebuild | Stops at l.834 "unknown item id: Glider". 19 follow-on table asserts fail after that. Also stops at SUI.verify. |

### SkyyExploration 0.2.2 - RISKY
| Check | Result |
|---|---|
| Link / verify | OK: 180 refs, 81/81. Moved to ChunkGrid: `getStore`, `getWorld`, `getChunkSectionReferenceAtBlock`. |
| Deprecated in 0.7 | `EventTitleUtil.showEventTitleToPlayer(PlayerRef, Message, Message, boolean)` (`ExpSpot.banner`, `ExpTick.zone`). It still works: the boolean maps to `EventTitleStyle` Major or Default with the same fade numbers. The replacement overload `(..., EventTitleStyle)` exists only in 0.7. |
| Assets | `Objective_Treasure_Map` is gone (CARD_ICON l.597). 0.7 adds 9 spawner chest drop lists: `Portals_Goblin_Chest_Tier1-5`, `_Cache`, `Portals_Goblin_Tier1-2` and `Portals_Hollows_Ancient_Chest`. The current jar has no XP row for them (UNVERIFIED what it pays: probably the default). The StashSystem ordering and the 27 Discovery zones are unchanged. |
| Rebuild | Stops at l.548 (`len(SPAWN_DL) == 46`, now 55), l.560 (drop-list name pattern) and l.597 (icon). Also stops at SUI.verify. |

### SkyyGuilds 0.1.6 - OK
OK: 58 refs, 48/48. Rebuild stops only at SUI.verify.

### SkyyVault 0.1.5 - OK
OK: 166 refs, 45/45. ItemStack / transaction constructors and codec keys are unchanged. Rebuild stops only at SUI.verify.

### SkyyAuctions 0.1.2 - OK
OK: 163 refs, 35/35. No issue.

### SkyyRanks 0.1.1 - OK
OK: 80 refs, 51/51. `hytale:Adventurer` still exists. `PlayerChatEvent` is async in both versions. No issue.

### SkyyUiProbe 0.3 - OK for 0.7 (dev mod; one bug on both versions)
| Check | Result |
|---|---|
| Link | `ProbeWin.open` (probe 24, build l.1544 `pg.sendUpdate(ub)`) calls `CustomUIPage.sendUpdate(UICommandBuilder)`. That method is **protected**, and `ProbeWin` extends Object, so the call throws IllegalAccessError on 0.6.8 **and** 0.7. It is caught, and probe 24 then logs "could not open probe 24". Not a 0.7 issue. Another builder has SkyyUiProbe 0.3.1 in progress (untracked files), so check there. |
| Verify | 16/16 OK. Rebuild stops only at SUI.verify. |

### SkyyMobs 0.1 - RISKY
| Check | Result |
|---|---|
| Link / verify | OK: 119 refs, 29/29. `ChunkStore.getChunkComponent` / `getGenerator` moved to ChunkGrid. |
| Deprecated + changed | `BlockChunk.getEnvironment(int,int,int)` (`MobLevel.blockEnv`) is deprecated in 0.7. Environment data moved to a per-section `EnvironmentSection` component, and BlockChunk now reads it through `environmentSections`, bound in `loadFromHolder`. The value is the same, so it works. The forward-compatible read is the one vanilla's `WorldSupport.getEnvironmentId` uses (0.7 only): `store.getComponent(sectionRef, EnvironmentSection.getComponentType()).get(x, y, z)`. Every ordering system it names is unchanged: RoleBuilderSystem (adds one harmless component), EntityStatsSystems$Setup, BalancingInitialisationSystem and ArmorDamageReduction. |
| Assets (runtime) | 12 built-in levelled roles are gone in 0.7, so they are dead entries: Goblin_Hermit, Goblin_Ogre, Goblin_Ogre_Tutorial, Goblin_Scavenger (+Battleaxe / Sword), the 4 goblin *_Patrol roles, Spawn_Void and Spectre_Void. 37 new 0.7 roles get no level until a rebuild: Coffer_Goblin_* (7), Goblin_Burner / Feastmaster / Guardian / Spectator / Turret / Lobber_Turret, Void_Spectre(_Static), Void_Spawn_*, Void_Tentacle(_Surge), Void_Anomaly_Crystal_* (4), Bear_Voidtaken_*, Crawler / Eye / Larva_Void_Surge, Skeleton_Archer_Turret, Spider_Cave_Ambush / Spiderling and Voidtaken_Goblin_Surge. The Env_Portal_Goblin_* rows it ships do exist in 0.7. |
| Rebuild | Stops at l.292 "should get a level: Spectre_Void" (renamed `Void_Spectre`). All other asset checks pass on 0.7: volcanic environments, biome rows, env rows and role rules. A rebuild then auto-levels all 37 new roles, including crystals, a marker and turrets. Review them before shipping (section 7). |

## 5. Engine changes that touch the set (0.6.8 to 0.7.0-pre.4)

- **Removed (BROKEN):**
  - `WorldChunk.setBlock(IIILjava/lang/String;)Z`. In 0.7 only `setBlock(IIIILBlockType;III)Z` is left (deprecated in both).
  - `ChunkLightingManager.invalidateLightInChunk(ChunkStore,II)Z`. In 0.7 every lighting method takes `ChunkGrid`.
  - `ISpawnProvider.getSpawnPoint(World,UUID)Transform`, now `getSpawnPointAsync(...)` returning `CompletableFuture<Transform>`. The
    new helper `SpawnUtil.teleportToSpawn/teleportWhenResolved` exists in 0.7 only.
- **Hierarchy:**
  - `PlayerConnectEvent` went from `IEvent` to `IAsyncEvent` (RISKY, Profiles).
  - `ChunkStore` gained the superclass `ChunkGrid`, and 5 called methods moved up into it. They still resolve.
  - `GameplayConfig` and `PlayerConfig` gained `NetworkSerializable` (harmless).
  - No class became final, an interface or non-public.
- **Deprecated in 0.7 (still work):**
  - `EventTitleUtil.showEventTitleToPlayer(...,boolean)` (Exploration);
  - `BlockChunk.getEnvironment(III)` (Mobs).
- **Bytecode changed in reached methods, all harmless:**
  - `InstancesPlugin.spawnInstance`, `teleportPlayerToInstance` and `teleportPlayerToLoadingInstance`: async spawn resolution.
  - `EffectControllerComponent.addEffect` (owner overload) and `removeEffect` (ldc_w only).
  - `ItemComponent.setItemStack`.
  - `BlockChunk.getEnvironment`.
  - One level deeper:
    - ECS `Store` archetype internals;
    - `TickingThread` run tracking;
    - `I18nModule.getMessages` (null language goes through `resolveLanguage` now);
    - `Velocity$Instruction` `preMultiplier`, defaulting to 1;
    - `InteractionContext.getRootInteractionId` (rune ability root);
    - `EventTitleUtil` boolean to style.
- **The 09-30 report's "8 of 682 methods changed"** is now 7 of 892, plus the 3 removed and the 5 moved. Two earlier hits were
  false positives from invokedynamic bootstrap renumbering: `WorldChunk.getBlockComponentEntity` and
  `CommandBuffer.removeEntity/tryRemoveComponent`.
- **Events:** all 30 referenced event types are still created by the engine (same counts). The only kind change is
  PlayerConnectEvent.

## 6. Update of research/PreRelease-Compat-Report.md

| 09-30 finding | Now (current pins) |
|---|---|
| Islands setBlock / relight / getSpawnPoint (0.5.4 l.2382 / 2438 / 2488) | **Still present** in 0.5.5 at l.2785 / 2841 / 2891 (callers l.3120, 3180, 5452, 5799). |
| Relight fix "`invalidateLightInChunkSections(world.getChunkStore(), cx, cz, 0, 10)`, try it and catch NoSuchMethodError" | **Correction:** in 0.7 that method takes `ChunkGrid`. Javassist compiles against ONE server jar, so a call to a method missing from that jar cannot be compiled at all, and the try / catch pair is not buildable. Use `invalidateLoadedChunks()` (the same on both versions) or reflection (section 7). The same applies to SpawnUtil, which is 0.7 only. |
| Menu doSpawn + icon + probe | **Still present** in 0.3.5: l.3984, icon l.226 / 479, probe l.1770. |
| Profiles travel fallback | **Still present** in 0.1.5 l.2213. **New:** the PlayerConnectEvent async change. |
| SUI.verify 1 / 273 fails (close X anchor) | **Still fails** with kit 1.4 (l.2612). Release passes 273 values / 97 files / 14 client values. Blocks 15 builds. |
| Icons Objective_Treasure_Map, Glider | **Still present** (Exploration l.597, Trees l.813 / 822). Both now stop a rebuild. |
| Skyy_Tree_Chop.json lacks the explosion trigger | **Still missing.** |
| Mana base (vanilla 100) | Unchanged: SkyySkills 0.4.12 still posts `target - vanilla max`. **New:** the 0.4.12 spell-cost generator stops a 0.7 rebuild, and 0.7 rune abilities cost Mana. |
| Cooking balance look | **Now a rebuild stop** (self-check 4). |
| "All 23 event classes still fired" | 30 types now. All are still created, **but PlayerConnectEvent became async** (missed on 09-30). |
| No command clash | Re-checked with /mobs and the current set: no clash. |
| Pack mods | The files are unchanged since 09-30, so the findings stand: More Crossbow Tiers OK; Saplings From Trees loses the blue fig leaf texture. |
| New mods / pins since 09-30 | SkyyMobs 0.1, Gear 0.2, Skills 0.4.12, Accessories 0.5.2, Classes 0.1.10, Sacks 0.7.12 and more: no new missing engine member. Their 0.7 issues are listed in section 4. |

## 7. Fix list for release day

The build tools read `install\release\...` (skyybuild, skyyui, skyycfg, plus 15 pinned scripts with their own Assets.zip path). When
0.7 becomes the release, the first build runs on 0.7 automatically.

Two notes on the fixes:
- "Both versions" fixes can ship before release day: they use calls that exist with the same signature in 0.6.8 and 0.7.
- "0.7 only" fixes compile only against the 0.7 jar.

**Must fix, or new players and buttons break:**

1. **SkyyIslands 0.5.6** (`tools/islands_0_5_6_patch.py` from the generated 0.5.5):
   - **FillTask.put l.2785 (both versions):** use the code below. It is the same path the removed String overload took (getIndex,
     then the 8-arg call with 0, 0, 0). The non-deprecated `BlockOperations.setBlock(ChunkStore, Ref, x, y, z, id, type, rot, filler,
     settings)` also exists on both, but its arguments are UNVERIFIED.

     ```
     int bid = BlockType.getAssetMap().getIndex(id);
     if (bid == Integer.MIN_VALUE) return 0;
     return chunk.setBlock(x, y, z, bid, (BlockType) BlockType.getAssetMap().getAsset(bid), 0, 0, 0) ? 1 : 0;
     ```
   - **RelightNow.run l.2841:**
     - Both versions: `world.getChunkLighting().invalidateLoadedChunks()`. It has the same signature on both and relights every
       loaded chunk of the island world, which is only a few chunks (UNVERIFIED in game).
     - 0.7 only: `invalidateLightInChunkSections(world.getChunkStore(), cx, cz, 0, 10)`.
   - **HubCmd.sendToHub l.2891:**
     - 0.7 only: `SpawnUtil.teleportToSpawn(ref, store, target, from, null)`. Treat it as sent, and never `join()` it on the world
       thread.
     - Both versions (stopgap): `Transform[] p = sp.getSpawnPoints(); where = (p != null && p.length > 0) ? p[0] : null;`. It is
       identical on both versions, but gives no per-player spawn and no height fit. UNVERIFIED for a FitToHeightMap main world.
2. **SkyyMenu 0.3.6:**
   - `doSpawn` l.3984: the same fix as 1, sendToHub.
   - Replace the `getSpawnPoint` probe at l.1770.
   - `Furniture_Ancient_Chest_Large_Treasure` becomes `Furniture_Ancient_Chest_Large` (l.226, l.479; it exists in both versions).
3. **`tools/skyyui.py` l.2612:** anchor the close-X check on the text before `@PageOverlay` (the 09-30 report, section 4, has a
   string that matches both versions). Run `tools/skyyui_test.py` and bump KIT_VERSION. Without it, 15 UI builds stop.

**Rebuild stops (each mod's next version; data and design, small code):**

4. **SkyySkills.** The spell-cost generator must learn the 0.7 shapes:
   - staffs without a per-item charged var (l.2039 rule, gate simulation l.2365, called at l.2481, the `Weapon_Staff_Wood` asserts l.2439 / l.2490-2491);
   - rune interactions `Ability_ChargedShot_Release_1-4` (10 / 20 / 30 / 50 Mana; l.2257).

   **Skyy decides:** divide rune costs like spells, or keep runes at vanilla cost. This ties into the class-ability slots planned for
   the runes. Also decide the Base Mana question (vanilla 100).
5. **SkyyCooking:** update the EXPECT table (l.475-482) to the 0.7 food effects: buffs 360 s, bread heal Percent 10.
   **Skyy decides:** a balance pass.
6. **SkyyGear:**
   - level rules (FAMILIES / FAM_DEV) for `Weapon_Bangstick` and `Weapon_Longsword_Ruined_Giant` (+ NPC variants);
   - the stackable-gear rule at l.797;
   - the CHG_FAMILIES counts at l.1665-1668.
7. **SkyyCollections:** counts 20 / 34 (l.249, l.267), plus a Sadwillow log collection and its reward row. **Skyy decides** its curve.
8. **SkyyClasses:** the UNASSIGNED prefix `Flamethrower_` becomes `Weapon_Flamethrower_` (l.278). **Skyy decides:** does any class own
   the Bangstick?
9. **SkyyExploration:**
   - `Objective_Treasure_Map` becomes `Deco_Treasure` (l.597);
   - the 9 portal / shard chest drop lists: count l.548 and pattern l.560. **Skyy decides** their XP.
   - Optional: switch to the `EventTitleStyle` overload.
10. **SkyyTrees:**
    - `Glider` becomes `Template_Glider` (l.813, l.822);
    - add `"Trigger_Explosion_State_Generic"` as the first entry of the first Parallel branch in `Skyy_Tree_Chop.json`.
11. **SkyyMobs:**
    - l.290-292: change the test id `Spectre_Void` to `Void_Spectre`.
    - Before shipping the rebuild, review the 37 new auto-levelled roles. Probably add `Void_Anomaly_Crystal_*`, `*_Marker`, the
      turrets and maybe `Coffer_Goblin_*` to `levels.exclude` (**Skyy decides**).
    - Optional: the EnvironmentSection read (0.7 only).
12. **SkyyProfiles:**
    - `travel` l.2213: the same fix as 1, sendToHub (low).
    - PlayerConnectEvent: no code change is required. Confirm in game that the join hook logs and works on 0.7, and treat
      `ProfConnect` as running on any thread.

**Housekeeping:**

13. Pack: ask for, or wait for, a Saplings From Trees update (unchanged).
14. SkyyUiProbe: fix probe 24's protected `sendUpdate` call (both versions).
15. Make this link check a permanent `tools/dev/linkcheck.py`. A separate task.

**In-game test on 0.7:**
- a brand-new player's `/island` (blocks, chest, kit);
- `/hub` with and without `/sethub`;
- Menu, then Spawn;
- a profile switch (watch for "connect handler failed");
- island relight;
- the HUD next to the new vanilla HUD;
- the swapped icons;
- a hatchet on explosive blocks;
- mob levels and plates on new 0.7 mobs;
- wand / staff / spellbook casts and a rune ability (Mana);
- cooked dishes and buffs;
- Sadwillow logs and the new mushroom in collections.

## 8. Facts for "switch the modpack to the pre-release now?" (the decision is Skyy's)

- **The live jars load on 0.7 today.**
- **Breakages until the fixes ship:**
  - new players' islands are empty, and new islands are not relit;
  - Menu Spawn fails;
  - the hub fallbacks fail;
  - the Glider, Treasure Map and Bank chest icons are gone.
- **Two kinds of fixes:**
  - **Both versions:** the Islands, Menu and Profiles fixes above (the 8-arg setBlock, `invalidateLoadedChunks`, `getSpawnPoints`)
    and the icon swaps. These can ship on the release first.
  - **0.7 only:** the async spawn helper and the rune / Mana work.
- **Building against the pre-release** needs one switch in skyybuild / skyyui / skyycfg. 15 pinned scripts also hard-code
  `install\release`. After that switch, 9 scripts plus the kit stop until the section 7 data fixes land.

## 9. UNVERIFIED / limits

- **Not played in game:** nothing ran on 0.7 in game. Behaviour comes from bytecode and asset diffs only.
- **Deeper engine changes:** behaviour diffs cover the reached engine methods plus one level of their callees, not the whole call
  graph.
- **PlayerConnectEvent thread:** which thread runs the hook on 0.7 is not proven.
- **Client and data effects:**
  - what the client shows for a vanished `ItemIcon`;
  - the HUD overlap;
  - what Exploration pays for the new portal chests;
  - the `getSpawnPoints` stopgap on a FitToHeightMap world.
- **Build dry run limits:** it skipped every statement that builds a class or touches a file. Checks inside such statements were
  not run, and javassist compile errors were taken from the constant-pool check instead.
