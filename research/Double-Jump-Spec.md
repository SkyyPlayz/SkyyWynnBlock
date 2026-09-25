# Double Jump node - Acrobatics tree spec

*Skyy's ask (2026-09-24): "add a double jump node to the acrobatics tree". This is the spec for the build agents of feedback round 2 (HANDOFF running log 07:15: SkyyTrees 0.2.1 + SkyySkills 0.4.2). Skyy uses they/them. Inputs: HANDOFF sections 1-3, `research/Exploration-Build-Spec.md` section 4.2, `tools/skyymove.py`, `SkyySkills/build_skyyskills_0.4.py`, `SkyyTrees/build_skyytrees_0.1.py`. Engine checks used `tools/dev` (reflect.py, bc.py, bcfull.py, callers.py, cpgrep.py, bcmod.py, reflectmod.py) against the release `HytaleServer.jar`, python `zipfile` on `Assets.zip` and every jar/zip in `UserData/Mods`, and a read-only string scan of `Client/HytaleClient.exe`. Nothing was written anywhere except this file.*

**VERIFIED** = seen in bytecode, assets, our own source or the client binary's strings. **UNVERIFIED** = inferred, or not seen in game yet.

---

## 0. Verdict

| Question | Verdict |
|---|---|
| **Can the Acrobatics tree give a double jump?** | **YES, as a server-side `Velocity` push in SkyySkills' Acrobatics tick.** LOCKED 2026-09-25: the trigger is a second jump in mid-air. The 2026-09-24 research recommended crouch because the jump key may not be visible to the server (section 1.1). |
| **Trigger, and where it is copied from** | **LOCKED 2026-09-25: jump again while already in mid-air** (`acro.doubleJump.trigger=jump`). Not crouch. The 2026-09-24 research below copied a crouch edge from TerrariaAddons because `MovementStates.jumping` may be invisible in normal air (section 1.1, test 5.0). Skyy locked the second jump anyway. Crouch and `both` stay admin overrides. |
| **Why not the jump key?** | Evidence (section 1.1) says `MovementStates.jumping` is the client's **jump-rising physics state**, not "jump key down". A mid-air press with no extra jump available very likely changes nothing the server can see. **None** of the 6 installed double-jump implementations uses the jump key in normal air. The spec keeps a `jump` trigger mode behind config, for the case where probe 5.0 proves otherwise. |
| **Native engine double jump?** | It exists, but only for armor, and the client does it: `Armor.MovementSettings.ExtraJumpCount` (vanilla `Debug_Movement_Boots`). The server never reads it except to serialize the item asset (VERIFIED, callers.py). No runtime or per-player API exists. It is not usable for a tree node. It is the only way to get a real jump-key double jump, so it is a gear idea for later (section 4, F4). |
| **Push** | `Velocity.addInstruction(new Vector3d(vx, vy, vz), (VelocityConfig) null, ChangeVelocityType.Set)`. This is our own `Acro.boost` path (dodge push, `.Add`). `.Set` is what TerrariaAddons, Zephyr and GrapplingHook use, and it matches the engine's own jump, which *sets* `vy = jumpForce`. |
| **Placement** | **LOCKED 2026-09-25: tier III, slot 7** (the alternative in section 2.1). It replaces Sprinter (`RSpeed2`). Quick Dodge (`RDodge`) returns to tier II slot 5. Unlocked at Acrobatics 20. SkyyTrees 0.2.3 still has the node in tier II slot 5; the next Trees build does the move. |

---

## 1. Feasibility evidence

### 1.1 The jump key mid-air is (almost certainly) invisible to the server
1. **The server's own jump replay** is `KnockbackPredictionSystems$SimulateKnockback.tick`, offsets 649-712. A jump happens only when `onGround && KnockbackSimulation.wasOnGround() && consumeWasJumping()`, which sets `vy = MovementSettings.jumpForce`. `jumping` / `swimJumping` are cleared as soon as `falling` becomes true (offsets 781-798). `getJumpCombo()/setJumpCombo()` count consecutive **ground** hops, capped at 3 (`Math.min(combo + 1, 3)`), and reset when you land without moving. It is a bunny-hop combo, not a multi-jump. (VERIFIED, bcfull. This corrects the earlier research notes.)
2. **NPC controller:** `MotionControllerWalk.updateAscendingStates` sets `MovementStates.jumping` from its ascent animation type. `updateDescendingStates` sets `falling`. Here `jumping` means "rising after a jump". (VERIFIED, bcfull.)
3. **The client's movement state machine** (identifiers in `HytaleClient.exe`):
   - `AirborneRegion` holds `JumpState`, `FallState`, `JumpSprintState` and `FallSprintState`.
   - The transitions are `CanJump`, `OnJumpStarted`, `OnJumpReleased`, `OnJumpDoublePressed`, `ValidateJump`, and next to them `CanExtraJump` and `ConsumeExtraJump`.
   - The item tooltip key is `client.itemTooltip.movementSettings.extraJumpCount`.
   
   (VERIFIED strings; the semantics are inferred.) If `CanJump` / `CanExtraJump` fail, a press does not enter `JumpState`, so `jumping` never rises. (UNVERIFIED.)
4. **The `ClientMovement` packet** (`ToServerPacket`) carries only `movementStates`, positions, orientations, `wishMovement`, `velocity`, `mountedTo` and `riderMovementStates`. It has no raw key field. `PlayerInput$SetMovementStates.apply` copies the client's states unvalidated. (VERIFIED, reflect + bc.)
5. **No installed mod uses the jump key in normal air** (table 1.3). TerrariaAddons ports Terraria's Cloud in a Bottle, which is a jump-key item in Terraria, yet it binds it to **crouch**.
6. **`MovementSettings.fallJumpForce`** (vanilla 7) and `jumpBufferDuration` 0.3 / `jumpBufferMaxYVelocity` 3 exist (VERIFIED, vanilla `Server/Entity/MovementConfig/Default.json`). So the client *does* jump in mid-air in two cases: probably a coyote jump after walking off a ledge, and a buffered jump just before landing. Both are the client's **own** jumps (UNVERIFIED semantics). In `jump` mode they must never count as double jumps (section 3.2, rule J).

### 1.2 The native double jump (armor, client-side)
- `Assets.zip` `Server/Item/Items/Armor/_Debug/Debug_Movement_Boots.json`: `"Armor": {"ArmorSlot": "Legs", "MovementSettings": {"ExtraJumpCount": 1, "ExtraJumpParticleSystem": "Example_Projectile_Trail_ShortLived", "ExtraJumpSoundEvent": "SFX_Player_Jump"}}` (VERIFIED).
- `server.core.asset.type.item.config.ItemMovementSettings` is only referenced by `ItemArmor.toPacket` (VERIFIED, callers.py over the whole jar). The protocol form has `extraJumpCount`, `extraJumpParticleSystem` and `extraJumpSoundEventIndex` (VERIFIED, reflect).
- `protocol.MovementSettings`, the live per-player settings object that `skyymove.py` writes, has **no** extra-jump field (VERIFIED, reflect: 66 fields, none of them extra jumps).
- `protocol.MovementStates.extraJumpsUsed` (byte) is reported by the client. The server only copies it (`MovementStatesSystems$TickingSystem.copyMovementStatesFrom`) (VERIFIED).
- **Rejected for the node:** a hidden or phantom Legs item would take the player's real Legs slot. Per-player rewritten item-asset packets are too fragile.

### 1.3 Every double jump found (vanilla + 125+ installed mods, full string scan)
| Source | Trigger | Push | Reset | Status |
|---|---|---|---|---|
| **Vanilla** `Server/Item/Interactions/Double_Jump.json` + `RootInteractions/Double_Jump.json`, bound in `Server/Item/Unarmed/Interactions/Empty.json` `"Wielding": "Double_Jump"` | Wielding (the guard hold, see `DamageSystems$WieldingDamageReduction`) with an **empty hand** | `StatsCondition` Stamina 2.01, then `ApplyForce` (0,2,0) Force 15, Stamina -2, `StaminaRegenDelay` Set -0.3, `Impact_Feathers_Black` at both feet | none (no airborne check) | VERIFIED asset; whether the client ever starts Wielding bare-handed is UNVERIFIED (test 5.14) |
| **Vanilla** `Debug_Movement_Boots` | real jump key, client | client physics | client (`extraJumpsUsed`) | VERIFIED asset + client strings; armor only |
| **TerrariaAddons 1.7.4** `items.accessories.cloudInABottle.CloudInABottle` (EntityTickingSystem) | `BoostOrderManager.isCrouchPressed(pr, ms.crouching)` edge, with `!onGround` and `!swimming` | `Velocity.addInstruction(new Vector3d(-sin(yaw)*10, 15, -cos(yaw)*10), null, Set)`; sound `CloudInABottle_DoubleJump`; `ParticleUtil.spawnParticleEffect("Block_Break_Snow", pos, singletonList(ref), store)` | `ms.onGround` → `BoostOrderManager.reset(pr)` | VERIFIED bytecode; **our trigger source** |
| **Zephyr 0.3.15** `doublejump.DoubleJumpInteraction extends SimpleInstantInteraction` | `Ability3` on its Karambit (item-bound; `AbilityInjector` can add it to other items, off by default) | `Velocity ... Set`, horizontal 10 / vertical 15; `StatUtil.tryConsume` = `EntityStatMap.subtractStatValue(int, float)` 1.5 Stamina; cooldown 150 ms | `GroundResetSystem`: `onGround` / `inFluid` / `climbing` | VERIFIED bytecode + `doublejump_defaults.json`; **our reset + stamina source** |
| **Starky's Shield 1.3.6** `ShieldCapPrimaryJumpHitCooldown` | Primary attack while `!onGround && jumping` | `ApplyForce` Add (Z -2, Y 4) Force 20 | per-player maps | VERIFIED; weapon-only |
| **GrapplingHook 2.0.2** `jump.GrappleInputEdge.jumpPressedThisTick` | `jumping` edge (component, and the queued `PlayerInput$SetMovementStates`) | Set (hook pull) | - | VERIFIED; **runs after `GrappleFlightHelper.enableTempFlight` / `forceFlyingState` in `GrappleTickSystem.tick`** (offsets 445-605), so the player is flying. This is not evidence for normal air. |
| **MoreBoots 0.0.3** `Air_Jump` | `"Equipped"` interaction plus a custom `CanJump` stat (Initial 2 < cost 5, no regen) | `ApplyForce` 20 | none | UNVERIFIED; likely broken |
| **Skyys-Modpack 1.5.0** (disabled in "HUD mod") | copies vanilla, adding Wielding → `Double_Jump` for Unarmed Block/Item too | `ApplyForce` 15, 1.5 Stamina | - | VERIFIED asset |
| BetterMovement 1.1.2, Glider, Jetpacks 1.5.0 | - | - | - | no double-jump strings at all (VERIFIED scan) |

All of these mods are disabled in the "HUD mod" world `config.json` (VERIFIED), so none of them conflicts in game today.

### 1.4 Engine facts the build uses (all VERIFIED unless marked)
| Piece | Exact name | How verified |
|---|---|---|
| States | `server.core.entity.movement.MovementStatesComponent.getComponentType()/getMovementStates()`; `protocol.MovementStates` public fields `onGround jumping falling crouching flying gliding mounting climbing mantling inFluid swimming sitting sleeping rolling sliding extraJumpsUsed(byte)` | reflect; already probed in SkyySkills 0.4 |
| Push | `server.core.modules.physics.component.Velocity.getComponentType()/getClientVelocity()` (`org.joml.Vector3d`) and `addInstruction(org.joml.Vector3d, server.core.modules.splitvelocity.VelocityConfig, protocol.ChangeVelocityType)`; `ChangeVelocityType.Set` / `.Add` | reflect + TerrariaAddons / GrapplingHook bytecode + our `Acro.boost` |
| Jump force | `server.core.entity.entities.player.movement.MovementManager.getComponentType()/getSettings()`, then `protocol.MovementSettings.jumpForce` / `.fallJumpForce` (float) | reflect, GrapplingHook bytecode, `skyymove.py` |
| Gravity | `server.core.modules.physics.util.PhysicsConstants.GRAVITY_ACCELERATION` (double, 32) | reflect + `skyymove.py` |
| Fall damage | `DamageSystems$FallDamagePlayers.tick`: when a queued `SetMovementStates` has `onGround` and `Player.getCurrentFallDistance() > 0`, the last `|clientVelocity.y|` is compared with `MovementConfig.getMinFallSpeedToEngageRoll()` (not in fluid); damage x max health / 100; `rolling` mitigates (`getMaxFallSpeedRollFullMitigation`, `getFallDamagePartialMitigationPercent`) | bc + bcfull |
| Roll threshold lookup | `((EntityStore) store.getExternalData()).getWorld().getGameplayConfig().getPlayerConfig().getMovementConfigIndex()`, then `MovementConfig.getAssetMap().getAsset(i)` → `getMinFallSpeedToEngageRoll()`. `MovementConfig` = `server.core.entity.entities.player.movement.MovementConfig`; vanilla value **21.0** (BetterMovement's override: 24). `protocol.MovementSettings` also has a public `minFallSpeedToEngageRoll` float (it is `MovementConfig.toPacket()`'s per-player copy), but `FallDamagePlayers.tick` reads the asset (offsets 92-289), so the build uses the asset | bc of FallDamagePlayers + reflect + Assets |
| Stamina | `EntityStatMap.getComponentType()/get(int)/subtractStatValue(int, float)/setStatValue(int, float)`, `DefaultEntityStatTypes.getStamina()`, `EntityStatValue.get()`; `modules.entitystats.asset.EntityStatType.getAssetMap().getIndex("StaminaRegenDelay")` (the stat exists: `Server/Entity/Stats/StaminaRegenDelay.json`) | reflect + Zephyr `StatUtil.tryConsume` + Assets |
| Game mode | `Player.getGameMode() == protocol.GameMode.Creative` | reflect; SkyySkills `SkillXp.creative` |
| FX | `server.core.universe.world.SoundUtil.playSoundEvent3d(int, protocol.SoundCategory, Vector3d, ComponentAccessor)`; `server.core.asset.type.soundevent.config.SoundEvent.getAssetMap().getIndex(Object)`; `server.core.universe.world.ParticleUtil.spawnParticleEffect(String, Vector3dc, List, ComponentAccessor)`; assets `SFX_Player_Jump` and `Impact_Feathers_Black` exist | reflect + TerrariaAddons bytecode + Assets |
| Vanilla numbers | `JumpForce 11.8` (h0 = 11.8² / 64 = 2.18 blocks), `FallJumpForce 7`, `JumpBufferDuration 0.3`, `MinFallSpeedToEngageRoll 21`, `MaxFallSpeedToEngageRoll 31` | Assets `Server/Entity/MovementConfig/Default.json` |

---

## 2. Design

### 2.1 Placement: replace, keep the template at 12
**LOCKED 2026-09-25: the tier III column.** Slot 7, replaces Sprinter. The "why tier II" text below is the 2026-09-24 recommendation. It is not the lock.
The template is fixed: `SLOT_TIER = [1,1,1,2,2,3,3,4,4,5,5,6]`, `SLOT_MAX = [25,20,15,10,10,15,10,10,10,20,10,5]`, `assert mx == SLOT_MAX[s]`, 12 nodes per tree, `TIER_LV = {1,10,20,30,45,60}` (VERIFIED, `build_skyytrees_0.1.py`).

| | Recommended: **slot 5, tier II** | Alternative: slot 7, tier III |
|---|---|---|
| Replaces | Quick Dodge `RDodge` (+10 % dodge push). Its twin Evasion `RDodge2` (tier V) stays, so the `dodge.acrobatics` hook stays alive | Sprinter `RSpeed2` (+5 % speed) |
| Unlock | Acrobatics **10** (cumulative XP 9,925: about 1-2 h of play) | Acrobatics 20 (522,425 XP: tens of hours with the 240/min movement cap) |
| Levels 2-10 | 150 x lv³ Dust (B of slot 5), 303,750 Dust in total (607,500 Acrobatics XP at 2 XP/Dust) | 500 x lv³, 1,012,500 Dust in total |
| Tree totals at max | speed +20 % (unchanged), jump +0.7, fall -15 %, **dodge +10 % (was 20), and none of it before Acrobatics 45** (only Evasion is left, tier V), Stamina +8 | speed **+15 %**, rest unchanged |
| Tree dodge push, Acrobatics 10-44 | **none** (Quick Dodge was the only tree dodge node below tier V) | Quick Dodge, up to +10 %, from Acrobatics 10 (unchanged) |

**Why tier II:** tier VI (the natural "capstone" slot) needs Acrobatics 60 = 111,672,425 XP. That is unreachable under the Acrobatics caps (the Tree-Feller-style capstone slot would hide the node from everyone). Tier II lets every player feel the node early. The 10 levels (55 % → 100 %) are the long grind. By numbers the lost bonus (Quick Dodge's +10 % dodge push) is the smallest one in the tree, and Skyy only locked the Stamina node here ("a Stamina node in the Acrobatics tree; the rest ... figure out later", HANDOFF 1). **What tier II really costs, stated plainly:** it is not a smaller dodge number. It removes the tree's dodge push **completely for Acrobatics 10-44**. The only tree dodge node left is Evasion at tier V, Acrobatics 45 = 38,072,425 cumulative XP. That is about 3,800x the 9,925 XP of level 10, and about 2,600 h at the 240/min movement cap alone (fall XP has its own cap and adds some; that pace is UNVERIFIED). So for nearly every player the tree gives **no** dodge push at all. The skill's own dodge push stays: `acro.dodgeBoostPerLevel=0.004`, i.e. +4 % at Acrobatics 10, +8 % at 20, +17.6 % at 44, capped at `acro.dodgeBoostMax=0.5` (VERIFIED, `build_skyyskills_0.4.1.py` `Acro.dodgeBonus` and `Acro.boost`). Tier III keeps Quick Dodge from level 10 and removes Sprinter's +5 % speed instead, but Double Jump then waits until Acrobatics 20 (522,425 XP). **Open decision for Skyy** (section 6): tier II (now) or tier III (later).

### 2.2 The node
Slot and trigger below are what 0.2.1 specified. **LOCKED 2026-09-25** moves the node to tier III slot 7 and sets the trigger to a second jump. Stamina stays 2. See the lock before section 6.
| Field | Value |
|---|---|
| Slot / tier | 5 / II in the 0.2.1 build (LOCKED 2026-09-25: slot 7 / tier III) |
| Id / name | `RDouble` / `Double Jump` (no `_`, `,` or `:`) |
| Icon | `Plant_Fruit_Windwillow` (VERIFIED item id; fallback `Ingredient_Feathers_Light`) |
| Kind | new `DJUMP` (appended to `KINDS`; existing kind numbers unchanged) |
| max / base / per | 10 / 0.50 / 0.05 → value `V = base + per x level` (the VEIN / FELLER formula): L1 **55 %** ... L10 **100 %** |
| Card NOW | `Jump once more in mid-air at %V of your jump height` (`%V` = pct, the default branch of `valueText`) |
| Card HOW | `Press %K in mid-air - once per jump - resets when you land - costs Stamina - no Acrobatics XP - needs SkyySkills 0.4.2` |
| Cost | unlock 1 token; level lv → lv+1 = 150 x lv³ Dust |

| Level | V | Air jump at vanilla h0 2.18 b | vy (b/s) at jumpForce 11.8 | Dust for next level |
|---|---|---|---|---|
| 1 | 55 % | 1.20 b | 8.75 | 150 |
| 2 | 60 % | 1.31 | 9.14 | 1,200 |
| 3 | 65 % | 1.41 | 9.51 | 4,050 |
| 4 | 70 % | 1.52 | 9.87 | 9,600 |
| 5 | 75 % | 1.63 | 10.22 | 18,750 |
| 6 | 80 % | 1.74 | 10.55 | 32,400 |
| 7 | 85 % | 1.85 | 10.88 | 51,450 |
| 8 | 90 % | 1.96 | 11.19 | 76,800 |
| 9 | 95 % | 2.07 | 11.50 | 109,350 |
| 10 | 100 % | 2.18 | 11.80 | - |

The air jump is a fraction of **the player's current jump**. `MovementManager.getSettings().jumpForce` already includes the Acrobatics level, Spring Step / High Jumper and gear through the movement protocol. So the double jump feels like "your jump again". Hard cap: `acro.doubleJump.maxBlocks=3.5`, which is vy 14.97. That matches the vy 15 that vanilla `Double_Jump.json`, Zephyr and TerrariaAddons all use.

### 2.3 Rules (all server-side, per player, in memory)
Rule 3's crouch press is what 0.2.1 specified. **LOCKED 2026-09-25:** the default trigger is a second jump (`acro.doubleJump.trigger=jump`). Stamina in rule 5 stays 2.
1. **One extra jump per airtime.** `acro.doubleJump.maxJumps=1`, admin-raisable (Zephyr `maxJumps` pattern).
2. **The charge resets** on any tick with `onGround || climbing || inFluid || swimming || mantling`. This is Zephyr's `GroundResetSystem` set plus mantling. It also resets on a world change and a profile switch.
3. **Trigger** = crouch **press** (rising edge). Holding crouch never fires twice. A press in the first `acro.doubleJump.minAirMs=100` ms after leaving the ground is ignored (and consumed).
4. **Anti-spam cooldown:** `acro.doubleJump.cooldownMs=250` between two double jumps (Zephyr uses 150).
5. **Stamina:** `acro.doubleJump.stamina=2.0` (vanilla `Double_Jump.json`'s own cost). With less Stamina there is no double jump and the charge is **not** used. `StaminaRegenDelay` is set to -0.3, copying vanilla, to pause regen briefly (`acro.doubleJump.staminaRegenDelay=0.3`, 0 = off).
6. **Off while** mounting, flying, gliding, sitting, sleeping, climbing, in fluid, swimming, mantling (the existing `Acro.excludedState`), and in **creative**. The creative check reads the real game mode: `SkillXp.creative` returns false when `creativeXp=true`, so it must not be reused.
7. **Falling-speed gate:** no double jump while falling faster than `acro.doubleJump.maxFallSpeed`. The default 0 means the world's `MovementConfig.MinFallSpeedToEngageRoll` (21 b/s in vanilla = about 6.9 blocks of free fall), the speed at which the engine starts to treat a landing as a hurting fall. A negative value means no limit.
8. **Push:** `vy = min(jumpForce x sqrt(V), sqrt(2 x 32 x maxBlocks))`. Horizontal = the client's current horizontal velocity plus `acro.doubleJump.forwardPush=2.0` b/s along it when moving at 1 b/s or more (the "small push"; the `Acro.boost` pattern). It is sent as one `Set` instruction.
9. `acro.enabled=false`, `acro.doubleJump.enabled=false`, the node toggled off in `/tree` (`.off`), or the trees bridge off (`bridge.bonus`, read inside `SkillBonus.sum`): no double jump.

### 2.4 Fall damage
- Engine fall damage uses the **landing speed** (1.4). A double jump sets `vy` upward, so the next landing speed comes from the new apex. A double jump right before a short landing softens it. This is the normal double-jump behavior. (VERIFIED formula; the in-game feel is UNVERIFIED.)
- Rule 7 means you can only double jump while a landing would **not yet hurt**. So it never cancels a damaging fall and never saves you from the void after a long drop. Soft Landing / Featherfall and the Skills fall reduction stay the fall-damage tools.
- **No conflict with the vanilla landing roll:** the roll matters at landing speeds of 21-31 b/s, and the double jump is off above 21. A crouch pressed to roll during a fast fall reaches the roll, not the double jump.
- There is no Acrobatics fall-XP exploit: fall XP only pays for damage that really applied (SkyySkills 0.4 rule). A softer landing pays less, never more.

### 2.5 Acrobatics XP
- The double jump pays **0 XP** by default (`acro.doubleJump.xp=0`). If an admin raises it, it goes into the pending pool `s[11]` and the existing sliding 240/min cap.
- At a double jump, `s[9]` (last paid jump ms) is set to now. If the client reports a `jumping` edge caused by our push, the existing ground-jump XP path cannot pay it (`acro.jumpCooldownMs` 800).
- The node gives no Dust: it earns no XP.

### 2.6 Feel and cosmetics (optional polish, `acro.doubleJump.fx=true`)
- Sound `SFX_Player_Jump` at the player: the native extra-jump sound of `Debug_Movement_Boots`.
- Particles `Impact_Feathers_Black` at the feet: vanilla `Double_Jump.json`'s particle. The target list is `singletonList(ref)`, like TerrariaAddons (UNVERIFIED whether other players see it).
- All FX go in try/catch: a missing asset never blocks the jump.

### 2.7 Known limits (documented, not bugs)
- **Latency:** the push is sent by the server, so it lands about 1 tick + ping after the press. The client does not predict it (UNVERIFIED feel; TerrariaAddons and Zephyr ship the same model).
- **Crouch in the air has other uses:** a player who presses crouch mid-air to prepare a landing slide will double jump. They can turn the node off per player in `/tree` (the existing toggle).
- **Client-authoritative movement:** the engine trusts client `onGround` (VERIFIED: `SetMovementStates.apply` overwrites). A hacked client could refill the charge. That is the same trust as vanilla movement, and the Stamina cost bounds it.
- **Native armor extra jumps stack.** A future armor piece with `ExtraJumpCount` adds its own jump-key jump on top of ours (see F4).

---

## 3. Implementation split

### 3.1 SkyyTrees 0.2.1 (patch on 0.2; source of truth `tools/trees_0_2_1_patch.py`, asserted `rep` anchors, writes `SkyyTrees/build_skyytrees_0.2.1.py`, VERSION `"0.2.1"`)
1. `KINDS += ["DJUMP"]` (after 0.2's `SOON`) → `T["K_DJUMP"]`.
2. `NODES["Acrobatics"]` slot 5 (index 4), which was `RDodge` in 0.2:
   `("RDouble", "Double Jump", "Plant_Fruit_Windwillow", "DJUMP", 10, 0.05, 0.5, "Jump once more in mid-air at %V of your jump height", "Press %K in mid-air - once per jump - resets when you land - costs Stamina - no Acrobatics XP - needs SkyySkills 0.4.2", "", "")`. `must()` checks the icon.
3. `TreeFx.value(i, eff)`: `if (k == @K_VEIN@ || k == @K_FELLER@ || k == @K_DJUMP@) return BASE[i] + per * eff;`. `valueText` needs no change (the default branch = pct).
4. `TreeFx.bonusMap`: `putNZ(m, "doublejump.acrobatics", v[@I_RDOUBLE@]);` and `dodge.acrobatics` becomes `v[@I_RDODGE2@]` only. `acroPost` and `stats()` are unchanged (RDodge was not in them).
   Also in the patch: the 0.2 build assert `_tot(("RDodge", "RDodge2")) == 0.2` (0.2 line 427) becomes `_tot(("RDodge2",)) == 0.1`, and Evasion's NOW text `+%V dodge push - adds to Quick Dodge` becomes `+%V dodge push` (Quick Dodge no longer exists) (VERIFIED, `build_skyytrees_0.2.py` lines 392-398 and 427).
5. `TreePage` HOW line (0.1 line 2237 pattern, `TreeDefs.HOW[i0].replace("%C", cd(i0))`): add `.replace("%K", TreeFx.djKey())`. `djKey()` = bridge `skill:dj:key` when it is a String, else `"crouch"`.
6. **Old save lines (explicit migration code, required).** Status: SkyyTrees 0.2 is **built** (`build_skyytrees_0.2.py`, `SkyyTrees-0.2.jar` 07:46) but **not deployed**: the live `UserData/Mods/SkyyTrees.jar` is `"0.1 SkyyTrees"` and `tools/deploy_set.py` pins `("SkyyTrees", "0.1")`; 0.1 has no Acrobatics tree, so no player file holds an `Acrobatics.*` line today (VERIFIED). The alias below matters only if 0.2 is deployed before 0.2.1, but it is cheap, so 0.2.1 always ships it.
   - **What 0.2 does without it** (VERIFIED, 0.2 `TreeStore.readFile()` / `snap()` / `saveNow()`, lines 985-1089): `readFile` reads each slot only by its current key `TreeDefs.TREES[i / 12] + "." + TreeDefs.ID[i]`, and resolves `.off` names through `TreeDefs.idx`, which knows current ids only. There is no alias table and no version branch. `snap()` rebuilds the whole file from `TreeData`, so an unread line is dropped on the next save. Once slot 5's id is `RDouble`, an old `Acrobatics.RDodge=<n>` would be ignored and the slot would load as 0.
   - **Impact without it:** Tokens and Dust are computed from the saved levels (`TreeCalc.tokSpent` / `dustSpent`), never stored (VERIFIED). So nothing would be spent and lost: the slot's Token and Dust would come back as unspent. The player would silently lose the node level and have to re-buy it.
   - **Code** (in `tools/trees_0_2_1_patch.py`, `rep` on 0.2's `readFile`; each anchor asserted unique inside the readFile `M()` block). Insert right before readFile's `for (int tt = 0; tt < @PKG@.TreeDefs.NT; tt++) {` loop:
     ```java
     // 0.2.1: Acrobatics slot 5 was RDodge (Quick Dodge) in 0.2 - same slot = same Token and Dust cost
     if (p.getProperty("Acrobatics.RDouble") == null) {
       String ov = p.getProperty("Acrobatics.RDodge");
       if (ov != null) { try { int x = Integer.parseInt(ov.trim()); d.lv[@I_RDOUBLE@] = x < 0 ? 0 : (x > 1000 ? 1000 : x); } catch (Throwable t) { } }
     }
     ```
     In the `.off` loop, replace `if (i >= 0) d.off[i] = true;` with:
     ```java
     if (i < 0 && "Acrobatics".equals(tn) && "RDodge".equalsIgnoreCase(xs[j].trim())) i = @I_RDOUBLE@;
     if (i >= 0) d.off[i] = true;
     ```
     (`RDodge2` is a different id, and `idx` matches it before this line.) `snap()` and `saveNow()` stay unchanged. They write current ids, so the next save writes `Acrobatics.RDouble=<n>` (and `RDouble` in `Acrobatics.off`), and the `RDodge` line is gone. A file is saved only after a change (`dirty`), so an untouched file keeps its `RDodge` line and is aliased again on every load, which is harmless. An `Acrobatics.RDouble` line always wins over `RDodge`.
   - **`trees.properties` (correction):** 0.2's `ADD02` block is appended only when `TreeCfg.has02` finds no `dust.xpPerDust.` / `Acrobatics.` / `Exploration.` key, so only to a file that 0.1 wrote (VERIFIED, lines 819-826 and 905). A file that 0.2 wrote never gets it again, so 0.2.1 needs its own once-only block. `ADD021` holds the `RDouble` row's `node_lines`, plus a comment line saying old `Acrobatics.RDodge.*` lines are unused and can be deleted. `has021(p)` is true when any key starts with `Acrobatics.RDouble.`. In `load()`, add `else if (loaded && !has021(p))` after the `has02` branch. The `else` matters: on a 0.1 file, 0.2.1's own `ADD02` already carries the `RDouble` lines, and `p` was read before that append. Without the block, the built-in defaults still apply (`apply()` gives every key a code default, VERIFIED lines 858-865), so it only affects what admins see. Old `Acrobatics.RDodge.*` config lines are ignored by `apply()`: an admin's edited Quick Dodge numbers do **not** carry over to Double Jump (documented).
   - **Build-time test** (jpype harness, temp `DIR` under `tools/dev/scratch/`, deleted afterwards). (a) A player file with `Acrobatics.RDodge=3` and `Acrobatics.off=RDodge` gives `readFile` → `lv[I_RDOUBLE] == 3`, `off[I_RDOUBLE] == true`, and `snap()` → `Acrobatics.RDouble=3`, `Acrobatics.off=RDouble`, no key equal to `Acrobatics.RDodge`. (b) A file with both `Acrobatics.RDouble=2` and `Acrobatics.RDodge=3` gives `lv[I_RDOUBLE] == 2`. (c) `Acrobatics.RDodge2=4` still loads as Evasion 4 and never as `RDouble`. (d) Balance: in case (a), `tokSpent` / `dustSpent` for Acrobatics are the same as a 0.2 file with `RDodge=3` loaded under 0.2.
7. `/tree acrobatics` test text, spec 4.4 test 5: Quick Dodge → Evasion.

### 3.2 SkyySkills 0.4.2 (patch on 0.4.1; source of truth `tools/skills_0_4_2_patch.py`, `rep` style)
**xp.properties block**, appended once when there is no `acro.doubleJump.enabled` key (the `ExplCfg` / `AlchCfg` ensureDefaults pattern, called beside `AcroCfg.ensureDefaults`); `/skills reload` re-reads it. Comments go on their own lines. **LOCKED 2026-09-25:** the default trigger line is `acro.doubleJump.trigger=jump`, not `crouch`. Stamina stays `2.0`. The block below is what 0.4.2 shipped; the live default in `build_skyyskills_0.4.5.py` follows the lock.
```
# ---------- Double Jump (SkyySkills 0.4.2) - Acrobatics skill-tree node, SkyyTrees 0.2.1 skill:bonus doublejump.acrobatics ----------
# trigger: crouch = press crouch in mid-air (0.4.2 default); jump = the jump key in mid-air. LOCKED 2026-09-25 default is jump.
acro.doubleJump.enabled=true
acro.doubleJump.trigger=jump
acro.doubleJump.maxJumps=1
# Air jump height = node value (fraction of your own jump height), capped at maxFraction and at maxBlocks.
acro.doubleJump.maxFraction=1.0
acro.doubleJump.maxBlocks=3.5
acro.doubleJump.forwardPush=2.0
acro.doubleJump.stamina=2.0
acro.doubleJump.staminaRegenDelay=0.3
acro.doubleJump.cooldownMs=250
acro.doubleJump.minAirMs=100
# 0 = the world's MovementConfig MinFallSpeedToEngageRoll (vanilla 21 - the speed where landings start to hurt); below 0 = no limit.
acro.doubleJump.maxFallSpeed=0
acro.doubleJump.xp=0
acro.doubleJump.fx=true
# debug=true: players with skyyskills.admin see a chat line for every crouch / jump / extra-jump edge while airborne (test 5.0).
acro.doubleJump.debug=false
```
`AcroCfg` fields: `DJ_ON, DJ_TRIGGER (int: 0 crouch, 1 jump, 2 both; LOCKED 2026-09-25: missing or unknown -> 1 jump + one WARN), DJ_MAX_JUMPS (1..5), DJ_MAX_FRAC (0..1.5), DJ_MAX_BLOCKS (0.5..10), DJ_FORWARD (0..10), DJ_STAMINA (>=0), DJ_REGEN_DELAY (>=0), DJ_CD (>=0), DJ_MIN_AIR (>=0), DJ_MAX_FALL, DJ_XP (>=0), DJ_FX, DJ_DEBUG`. On setup and on every reload, SkyySkills puts the bridge key `skill:dj:key` = `"crouch"` / `"jump"` / `"jump or crouch"`, and removes it in shutdown. The default key is `jump`.

**Acro STATE:** `double[281]` → `double[292]`. Update the layout comment:
`281` prev crouching, `282` air jumps used since the last ground contact, `283` last double jump ms, `284` airborne-since ms (0 = grounded), `285` prev jumping (own copy; `s[5]` belongs to `move()`), `286` last debug line ms, `287` prev `extraJumpsUsed`, `288-291` spare.
`Acro.reset(s)` (world change) and `Acro.profileReset(s)` also zero 281, 282, 284 and 285.

**New Acro methods**, added in this order, before `airJump` (javassist: no forward references, no lambdas, generics, autoboxing or enhanced-for). The aliases are the build script's (`MMG`, `MCF` = `...player.movement.MovementConfig`, `PHC`, `ESM`, `ESV`, `DST`, `ESTT` = `...entitystats.asset.EntityStatType`, `SEV`, `SNU`, `SCAT`, `PTU`, `GM`, `EST`, `WLD` are the new ones):
```java
public static double djFraction(java.util.UUID u) {            // tree value, 0 = no node
  double f = {PKG}.SkillBonus.sum(u, "doublejump.acrobatics");
  if (!(f > 0.0)) return 0.0;
  return f > {PKG}.AcroCfg.DJ_MAX_FRAC ? {PKG}.AcroCfg.DJ_MAX_FRAC : f;
}
public static boolean creativeMode({ST} st, {REF} r) {          // real game mode (NOT SkillXp.creative)
  try { {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType()); return p != null && p.getGameMode() == {GM}.Creative; }
  catch (Throwable t) { return false; }
}
public static double djMaxFall({ST} store) {                    // 0 = no limit
  // Read the WORLD's MovementConfig asset, exactly like DamageSystems$FallDamagePlayers does for real fall damage.
  // Do NOT "simplify" this to djSettings(...).minFallSpeedToEngageRoll: that per-player protocol.MovementSettings is a
  // toPacket() copy that movement mods rewrite, and fall damage never reads it, so the two can drift apart.
  double c = {PKG}.AcroCfg.DJ_MAX_FALL;
  if (c < 0.0) return 0.0;
  if (c > 0.0) return c;
  try {
    {WLD} w = (({EST}) store.getExternalData()).getWorld();
    int mi = w.getGameplayConfig().getPlayerConfig().getMovementConfigIndex();
    {MCF} mc = ({MCF}) {MCF}.getAssetMap().getAsset(mi);
    if (mc != null && mc.getMinFallSpeedToEngageRoll() > 0.0f) return (double) mc.getMinFallSpeedToEngageRoll();
  } catch (Throwable t) { }
  return 21.0;
}
public static {MVS} djSettings({ST} store, {REF} ref) {
  try { {MMG} mm = ({MMG}) store.getComponent(ref, {MMG}.getComponentType()); return mm == null ? null : mm.getSettings(); }
  catch (Throwable t) { return null; }
}
public static boolean djStamina({CB} cb, {REF} ref) {           // false = not enough Stamina (charge kept)
  double cost = {PKG}.AcroCfg.DJ_STAMINA;
  if (cost <= 0.0) return true;
  try {
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());
    if (m == null) return true;
    int si = {DST}.getStamina();
    {ESV} sv = m.get(si);
    if (sv == null) return true;
    if ((double) sv.get() < cost) return false;
    m.subtractStatValue(si, (float) cost);
    if ({PKG}.AcroCfg.DJ_REGEN_DELAY > 0.0) {
      int di = {ESTT}.getAssetMap().getIndex("StaminaRegenDelay");
      if (di != Integer.MIN_VALUE) m.setStatValue(di, (float) (0.0 - {PKG}.AcroCfg.DJ_REGEN_DELAY));
    }
    return true;
  } catch (Throwable t) { warnOnce("double jump stamina failed: " + t); return false; }
}
public static void djFx({ST} store, {REF} ref) {                // optional polish, never throws
  if (!{PKG}.AcroCfg.DJ_FX) return;
  try {
    {TRC} tc = ({TRC}) store.getComponent(ref, {TRC}.getComponentType());
    if (tc == null) return;
    {V3D} p = tc.getPosition();
    int si = {SEV}.getAssetMap().getIndex("SFX_Player_Jump");
    if (si != Integer.MIN_VALUE) {SNU}.playSoundEvent3d(si, {SCAT}.SFX, p, store);
    {PTU}.spawnParticleEffect("Impact_Feathers_Black", p, java.util.Collections.singletonList(ref), store);
  } catch (Throwable t) { }
}
public static void djDebug(double[] s, {PR} pr, String what, double vy, long now) {
  if (pr == null || (double) now - s[286] < 200.0) return;
  try { if (!pr.hasPermission("skyyskills.admin")) return; } catch (Throwable t) { return; }
  s[286] = (double) now;
  long air = s[284] > 0.0 ? now - (long) s[284] : 0L;
  pr.sendMessage({MSG}.raw("[Skills] DJ debug: " + what + " in air - vy " + (Math.round(vy * 10.0) / 10.0) + " - air " + air + " ms - used " + (int) s[282]).color("#c8a0ff"));
}
```
**`airJump`**, world thread, every tick:
```java
public static void airJump(double[] s, {ST} store, {CB} cb, {REF} ref, {PR} pr, java.util.UUID u, {MVT} ms, long now) {
  if (ms == null) return;
  boolean cEdge = ms.crouching && s[281] < 0.5;
  boolean jEdge = ms.jumping && s[285] < 0.5;
  int xj = (int) ms.extraJumpsUsed;
  boolean xEdge = (double) xj != s[287];
  s[281] = ms.crouching ? 1.0 : 0.0;
  s[285] = ms.jumping ? 1.0 : 0.0;
  s[287] = (double) xj;
  if (ms.onGround || ms.climbing || ms.inFluid || ms.swimming || ms.mantling) { s[282] = 0.0; s[284] = 0.0; return; }
  if (s[284] <= 0.0) s[284] = (double) now;
  if (!{PKG}.AcroCfg.DJ_ON) return;
  {VEL} v = null; {V3D} cv = null; double vy0 = 0.0;
  if (cEdge || jEdge || xEdge) {
    v = ({VEL}) cb.getComponent(ref, {VEL}.getComponentType());
    if (v != null) cv = v.getClientVelocity();
    if (cv != null) vy0 = cv.y();
    if ({PKG}.AcroCfg.DJ_DEBUG) djDebug(s, pr, cEdge ? "crouch edge" : (jEdge ? "jump edge" : "extraJumpsUsed " + xj), vy0, now);
  }
  int trig = {PKG}.AcroCfg.DJ_TRIGGER;
  boolean byCrouch = trig != 1 && cEdge;
  boolean byJump = trig != 0 && jEdge;
  if (!byCrouch && !byJump) return;
  if (v == null || cv == null) return;
  if (excludedState(ms) || creativeMode(store, ref)) return;
  if ((double) now - s[284] < (double) {PKG}.AcroCfg.DJ_MIN_AIR) return;
  if (s[282] >= (double) {PKG}.AcroCfg.DJ_MAX_JUMPS) return;
  if ((double) now - s[283] < (double) {PKG}.AcroCfg.DJ_CD) return;
  double f = djFraction(u);
  if (f <= 0.0) return;
  double mf = djMaxFall(store);
  if (mf > 0.0 && vy0 < 0.0 - mf) return;                                   // rule 7
  {MVS} st = djSettings(store, ref);
  double jf = (st != null && st.jumpForce > 0.0f) ? (double) st.jumpForce : 11.8;
  if (!byCrouch) {                                                           // rule J: jump mode only
    double fj = (st != null && st.fallJumpForce > 0.0f) ? (double) st.fallJumpForce : 7.0;
    if (vy0 > 0.5 * fj) return;                                              // the client jumped itself (coyote / buffered jump)
  }
  if (!djStamina(cb, ref)) return;                                           // rule 5 (charge kept)
  double g = {PHC}.GRAVITY_ACCELERATION;
  double vy = jf * Math.sqrt(f);
  double cap = Math.sqrt(2.0 * g * {PKG}.AcroCfg.DJ_MAX_BLOCKS);
  if (vy > cap) vy = cap;
  double hx = cv.x();
  double hz = cv.z();
  double hl = Math.sqrt(hx * hx + hz * hz);
  double fw = {PKG}.AcroCfg.DJ_FORWARD;
  if (hl >= 1.0 && fw > 0.0) { hx = hx + hx / hl * fw; hz = hz + hz / hl * fw; }
  v.addInstruction(new {V3D}(hx, vy, hz), ({VCF}) null, {CVT}.Set);
  s[282] = s[282] + 1.0;
  s[283] = (double) now;
  s[9] = (double) now;                                                       // 2.5: no ground-jump XP from our push
  if ({PKG}.AcroCfg.DJ_XP > 0.0 && !{PKG}.SkillXp.creative(store, ref)) s[11] = s[11] + {PKG}.AcroCfg.DJ_XP;
  djFx(store, ref);
}
```
(`warnOnce` = a FAILED_ONCE-style flag, like `AcroSys.FAILED_ONCE`.)

**Hook in `AcroSys.tick`**, inside `if (AcroCfg.ENABLED)`, right after `Acro.move(...)` and before `Acro.dodge(...)`: `{PKG}.Acro.airJump(s, store, cb, ref, pr, u, ms, now);`. It runs every tick (edge detection), before the 1 s gate.

**UI:**
- The Acrobatics `treeLine` (Stats page, 0.4.1 spec 3.5) appends `double jump <pct(V)>` when `djFraction > 0`.
- The Acrobatics `lines()` gains `"Double Jump (skill tree): air jump at 55% of your jump height - press crouch in mid-air - 2 Stamina"`, with the key taken from `skill:dj:key`. When `acro.doubleJump.enabled=false`, the line reads `"Double Jump is turned off on this server"`.

**Build probes** (add to the `B.probe` list): `(MVT, "extraJumpsUsed")`, `(CVT, "Set")`, `(MMG, "getComponentType")`, `(MMG, "getSettings")`, `(MVS, "jumpForce")`, `(MVS, "fallJumpForce")`, `(PHC, "GRAVITY_ACCELERATION")`, `(MCF, "getAssetMap")`, `(MCF, "getMinFallSpeedToEngageRoll")`, `(WLD, "getGameplayConfig")`, `("...asset.type.gameplay.GameplayConfig", "getPlayerConfig")`, `("...asset.type.gameplay.PlayerConfig", "getMovementConfigIndex")`, `(ESM, "subtractStatValue")`, `(ESM, "setStatValue")`, `(DST, "getStamina")`, `(ESTT, "getAssetMap")`, `(SEV, "getAssetMap")`, `(SNU, "playSoundEvent3d")`, `(PTU, "spawnParticleEffect")`, `(SCAT, "SFX")`. Then `-Xverify:all` and the jpype harness as usual, followed by `python tools/ci/lint.py` (0 fails).

### 3.3 Cross-mod contract (new)
| Key | Writer | Reader | Shape |
|---|---|---|---|
| `skill:bonus:<uuid>["trees"]` `doublejump.acrobatics` | SkyyTrees 0.2.1 (`TreeTick` 1 s post, republished within 1 s of a profile switch) | SkyySkills 0.4.2 `Acro.djFraction` | Double: air-jump height as a fraction of the player's jump height (0.55-1.0); absent = no node |
| `skill:bonus:<uuid>["trees"]` `dodge.acrobatics` | SkyyTrees 0.2.1 | SkyySkills 0.4.1+ | now `RDodge2` only |
| `skill:dj:key` | SkyySkills 0.4.2 (setup + reload; removed in shutdown) | SkyyTrees 0.2.1 card HOW `%K` | String `crouch` / `jump` / `jump or crouch`; absent = `crouch` |

**Deploy pairing:** SkyyTrees 0.2.1 + SkyySkills 0.4.2 go in the same set. Each still loads alone. Trees without 0.4.2 shows the card ("needs SkyySkills 0.4.2") and nothing happens. Skills 0.4.2 without the node does nothing.

### 3.4 Threads
Everything runs in `AcroSys.tick` (an `EntityTickingSystem` on `Player`, world thread, not parallel; VERIFIED in the 0.4 source comment and query). The Velocity instruction is the same path as `Acro.boost`: `Velocity` instruction → `PlayerVelocityInstructionSystem` → `ChangeVelocity` packet. Stamina uses `EntityStatMap` through `cb.getComponent` (Zephyr / Perks pattern), on the same thread. The bridge is read from `ConcurrentHashMap`s. State is keyed by UUID in `Acro.STATE`, so multiplayer is per player. `Acro.retainOnline` already prunes it.

---

## 4. Fallbacks (if test 5.0 shows crouch is not reported in mid-air)
| # | Trigger | Copy from | Cost / risk |
|---|---|---|---|
| F1 | **Dodge in mid-air**: the existing `Acro.dodge` rising edge of `Dodge_Left` / `Dodge_Right` (`EffectControllerComponent.hasEffect`) while `!onGround` becomes the double jump (and not the dodge push) | our own 0.4 code (VERIFIED detection) | cheap; UNVERIFIED that the client allows a dodge in the air (add a `dodge edge` debug line in `dodge()` for test 5.0) |
| F2 | **Empty-hand guard (Wielding)**: SkyySkills ships an override of `Server/Item/Unarmed/Interactions/Empty.json` whose `Wielding` points to `Root_Skyy_Double_Jump`, then a Java `SimpleInstantInteraction` that runs the gates of 3.2 | vanilla binding (VERIFIED asset) + Zephyr `DoubleJumpInteraction.firstRun` gate chain | empty hand only; collides with other Unarmed overrides (Skyys-Modpack) |
| F3 | **Ability3 injected** into every weapon and tool | Zephyr `AbilityInjector` / `ability_injection_defaults.json` | heavy; ability keys are reserved for class skills (HANDOFF 1): not recommended |
| F4 | **Real jump key, as gear**: a SkyWynn Legs armor with `Armor.MovementSettings.ExtraJumpCount: 1` (+ `ExtraJumpSoundEvent`, `ExtraJumpParticleSystem`) and a trade-off (low defense). The tree node would then unlock its recipe (Collections `coll:recipes` style) instead of a passive | vanilla `Debug_Movement_Boots` (VERIFIED) | the only way to get the jump key; it takes the Legs slot. This fits Skyy's "gear always has a trade-off" rule anyway. Good as a later item even if the node works |

If crouch works but Skyy wants the jump key, set `acro.doubleJump.trigger=both` only after 5.0 shows `jump edge in air` lines for plain mid-air presses.

---

## 5. Test checklist (in order, riskiest first; copy into TEST-CHECKLIST.md)
**5.0 Probe (do this first, about 2 minutes):** set `acro.doubleJump.debug=true`, run `/skills reload`, stay in Adventure mode, and watch chat.
- (a) Jump and press **crouch** near the apex: a `crouch edge in air` line appears. This decides the default trigger.
- (b) Jump and press **jump** again near the apex: record whether a `jump edge in air` line appears. The expected answer is no.
- (c) Walk off a ledge and press jump within about 0.2 s: record it (coyote jump; the `vy` in the line should be about +7).
- (d) Optional, native check: `/give Debug_Movement_Boots`, wear it, and double-tap jump. A real double jump plus an `extraJumpsUsed 1` line confirms the native path (F4).
- (e) Dodge in mid-air: record any push or line (F1).

1. Unlock Double Jump 1 in `/tree acrobatics` at Acrobatics 10 (or with `debug.extraTokens`): crouch in mid-air gives a visible second jump (about 1.2 blocks). The `/tree` card says "Press crouch in mid-air".
2. Once per airtime: a second crouch in the same airtime does nothing. After landing it works again. Climbing a ladder or touching water also recharges.
3. Stamina: the bar drops by 2 per double jump. Below 2 Stamina nothing happens and the charge is kept.
4. Level 10 (`debug.extraDust`): the air jump is about as high as a normal jump. With high jump bonuses (Acrobatics 100 + Spring Step) it is capped at about 3.5 blocks.
5. Off while gliding (Glider item), swimming, climbing, mounted, under `/fly` (SkyyEssentials) and in creative.
6. Fall gate: from about 3 blocks of falling, crouch works. After about 10 blocks of falling, crouch does nothing and the vanilla landing roll still works.
7. Fall damage: a 6-block drop with a double jump just before landing = no damage. From 20 blocks you cannot double jump, and the damage is unchanged (compare Soft Landing).
8. XP: 20 double jumps in place add no Acrobatics XP (`/skills stats acrobatics` before and after, standing still between jumps).
9. Toggle the node off in `/tree`: no double jump. On again: it works within 1 s.
10. Profile switch, relog and world change (hub ↔ island): it works, with no stuck charges. The other profile without the node cannot double jump.
11. Two players: each has their own charge. A player without the node cannot double jump next to one who has it.
12. Sprint, jump, crouch in the air: a double jump happens (known, 2.7). Sprint-crouch on the ground still slides.
13. Stats page: the Acrobatics tree line shows `double jump 55%`. The dodge line shows only Evasion's part.
14. Vanilla empty hand: hold right-click in the air and on the ground. Record whether the vanilla `Wielding` → `Double_Jump` already pushes you up (1.3). If it does, tell Skyy: it is a free vanilla stamina jump for everyone.
15. `acro.doubleJump.enabled=false`, then `/skills reload`: no double jump, and the card still shows. SkyyTrees 0.2.1 with SkyySkills 0.4.1: the card shows, nothing happens.
16. Migration (only needed in game if SkyyTrees 0.2 was deployed before 0.2.1; the harness test of 3.1 point 6 always runs). A 0.2 player file with `Acrobatics.RDodge=3` and `Acrobatics.off=RDodge` loads as Double Jump 3, turned off. The Acrobatics Tokens and Dust shown are unchanged. After one change in `/tree` (for example, toggling it on), the file has `Acrobatics.RDouble=3` and no `Acrobatics.RDodge` line.

---

## LOCKED 2026-09-25 — placement, activation, Stamina (Skyy, voice)

1. **Tier III, not tier II.** Use the alternative already written in section 2.1: slot 7 (index 6), unlocked at Acrobatics 20, replaces Sprinter (`RSpeed2`). Quick Dodge (`RDodge`) returns to tier II slot 5. Do not invent a new slot. SkyyTrees 0.2.3 still places `RDouble` in slot 5 (it replaced Quick Dodge). The next Trees build does this move. The tier III slot's Dust coefficient is the existing template value for slot 7 (`SLOT_B` 500, section 2.1). That is not a new Stamina cost.
2. **Activation: jump again while already in mid-air** (a second jump). Not crouch in mid-air. The config key already exists: `acro.doubleJump.trigger=jump`. Crouch and `both` stay choices in Server Setup, not the default. Section 1.1 still says the client may not report `MovementStates.jumping` in normal air (test 5.0). Skyy locked the jump key anyway. If test 5.0 shows no jump edge, that is a follow-up. It does not keep crouch as the default.
3. **Stamina stays 2** (`acro.doubleJump.stamina=2.0`). Section 2.1's tier III column does not name a different Stamina cost. There is no conflict. Do not invent one.

New `xp.properties`, and a missing `acro.doubleJump.trigger`, use `jump`. A file that already has `acro.doubleJump.trigger=crouch` keeps crouch until that line is set to `jump`.

## 6. Open questions for Skyy
1. LOCKED 2026-09-25: **tier III slot 7** (Acrobatics 20, replaces Sprinter). Was: tier II slot 5 (Acrobatics 10, replaces Quick Dodge) or tier III? See the lock above.
2. LOCKED 2026-09-25: **jump again in mid-air**, not crouch. The boots item (F4) is still open: should a later gear piece add a real jump-key extra jump on top?
3. **Stamina 2 is locked** with the decision above. Still open: 55 % → 100 % of your jump height over 10 levels, no XP, and no double jump once you fall fast enough to get hurt.
