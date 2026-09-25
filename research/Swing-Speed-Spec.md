# Swing Speed Spec: Mining Speed makes the pickaxe swing faster (SkyyTrees 0.2.3)

*Written 2026-09-25 for workflow skywynn-swing-speed. Answers Skyy's report of 2026-09-25: "the mining skill tree increases mining
speed. but once you have a pick that can break a block in one hit, you are limited by how fast you swing the pick. so mining speed
needs to increase how fast you swing your pick." Research only: no build script, patch, jar or game file was changed. Engine checks
were read-only (bytecode from `HytaleServer.jar`, JSON from `Assets.zip` read in memory, installed mods read-only). The scratch
dumps under `tools/dev/scratch/swing/` were deleted afterwards. This file replaces the first draft written earlier today. That
draft said "no lever". It was wrong, and section 9 explains why.*

**LOCKED 2026-09-25 (Skyy):**
- Mining Speed max bonus is **+40%** faster pickaxe swings (was +25%). A new `trees.properties` uses `Mining.MSpeed.per=0.016` (25 levels x 1.6% = 40%, a swing every 0.25 s, back to back). A file already on `0.01` keeps +25% until that line is set to `0.016`. If +40% is still too slow, vanilla swing timing may need adjusting. The engine does not go past +40% without re-timing the animation.
- Chopping Speed II stays renamed **Heavy Hatchet** (breaking power on wood). HARD RULE: hatchet swing-speed bonuses apply only to tree-breaking and wood-chopping. They must not change weapon-axe combat speed for Berserker or any combat class. Weapon axes get their own combat swing-speed stat, and Chopping Speed / Heavy Hatchet do not touch it. SkyyTrees 0.2.3 still speeds every `Hatchet_Attack` swing, including hits on mobs, and has no combat swing-speed stat yet. `Weapon_Axe_*` and `Weapon_Battleaxe_*` already use other roots, so Chopping Speed does not reach them today.

**Build status (2026-09-25):** SkyyTrees 0.2.3 has been built from this spec: `tools/trees_0_2_3_patch.py` ->
`SkyyTrees/build_skyytrees_0.2.3.py` -> `SkyyTrees/SkyyTrees-0.2.3.jar`. All the section 3.7 self-checks pass at build time. The bare-JVM
harness (section 7 A) ran 168 checks with 0 fails, and its scratch folder was deleted. It is not deployed and not tested in game. There are
three small deviations:
- The Server Setup help text for `swing.enabled` is shortened to fit the kit's 100-character limit.
- When `respec.coins` > 0, the notice says "You can respec the tree in /tree ..." instead of claiming the respec is free.
- Unlocking Mining Speed, Chopping Speed or Heavy Hatchet in 0.2.3 marks `note.swing`, so a brand-new owner never sees the "no longer
  adds breaking power" line.

Review fixes, same day, rebuilt (lint 0 fails; still not deployed or tested in game):
- Self-check 2 now also follows a `Selector` step's hit chains (`HitEntity`, `HitEntityRules[].Next`, `HitBlock`). The engine forks
  those chains, the same as the 2nd and later `Parallel` branches, and the check counts both the same cautious way. Today the mob-hit
  step (`Pickaxe_Mine_Damage` / `Hatchet_Chop_Damage`) has no `RunTime`, so the swing is still 0.25 s. If a Hytale update gives it one
  that pushes the swing past 0.25 s, the build now stops. An in-memory test confirmed this.
- With `swing.enabled` OFF, the "Now:" line of Mining Speed / Chopping Speed says "turned off on this server (Faster tool swings is
  OFF)". Before, it still showed the full bonus. `tree:fn:bonus` returns 0 for those two nodes while the switch is off.
- The logged-once flag for a failed swing apply is now atomic, because every world thread runs the tick.

**Legend.** VERIFIED = seen in `HytaleServer.jar` bytecode or in `Assets.zip` / installed-mod JSON. INFERRED = strongly implied, not
proven (mostly: what the client does). UNVERIFIED = needs Skyy's in-game test.

---

## 0. VERDICT: YES

**A server mod can make one player swing a pickaxe faster. SkyyTrees can do it on its own. SkyySkills is not needed.**

1. **What limits a pickaxe today is a cooldown, not the swing motion.** The vanilla pickaxe swing (`Pickaxe_Mine`) takes **0.25 s**
   from start to finish. But you can only start a new swing every **0.35 s**. That 0.35 s is the engine's default cooldown for a
   left-click (`InteractionTypeUtils.getDefaultCooldown` returns 0.35 for `Primary`). The vanilla pickaxe root interaction sets no
   cooldown of its own, so it gets this default. So every vanilla pickaxe swings 0.25 s, then waits a forced ~0.10 s. Once one hit
   breaks the block, 0.35 s per block is the ceiling. That is exactly what Skyy noticed. (VERIFIED, section 1.)
2. **Hytale's own interaction content can shorten that cooldown for players who carry a certain status effect.** Two stock
   interaction types do it:
   - `EffectCondition` checks "does this player have effect X?".
   - `TriggerCooldown` restarts the swing cooldown with a shorter time.
   Both types are sent to the client and run on both client and server. So the client, which decides when the next swing starts,
   agrees with the server. (VERIFIED on the server side; client side INFERRED from the packet classes and point 3.)
3. **This exact trick already ships in a published mod on this machine.** Hylamity 0.2.0 (`Mods/Hylamity-0.2.0.jar`) has a
   `Mining_Speed_Boost` effect that its Java code puts on the player. It also has a pickaxe root that starts with
   `EffectCondition [Mining_Speed_Boost]`, then `TriggerCooldown 0.159 s`, then a faster pickaxe swing. Players without the effect
   fall through to the vanilla `Pickaxe_Attack`. (VERIFIED, section 2.6.) Skyy's rule "steal what works" points straight at it.
4. **How SkyyTrees 0.2.3 uses it:**
   - It ships 40 hidden "swing tier" effects per tool: +1 % to +40 %.
   - It ships one override of the vanilla pickaxe root and one of the vanilla hatchet root. Each override is a small decision tree
     that picks the player's tier and restarts the cooldown at `0.35 / (1 + tier %)` seconds.
   - Its existing once-per-second `TreeTick` puts the matching tier effect on the player from the Mining Speed / Chopping Speed
     node levels.
   - Default: +1 % per level, +25 % at max (a swing every 0.28 s instead of 0.35 s).
5. **Limits:**
   - The bonus comes in whole-percent steps.
   - **+40 % is the ceiling.** At 0.25 s the swings run back to back. Going past that would mean copying and re-timing the vanilla
     swing and its animation, which this spec does not do.
   - It speeds up **every** swing of that pickaxe, including hits on mobs. A pickaxe does 1 damage, so this hardly matters. A
     blocks-only version would need a client round trip before every swing, which is not worth it.
   - It **replaces one small vanilla file per tool** (the root interaction). Another mod that replaces the same file would win or
     lose silently. SkyyTrees checks this at start and logs it.
   - Nothing here is tested in game yet.

Other mods are not needed. Heavy Pick stays breaking power. Chopping Speed gets the same treatment for hatchets (section 3.2).
Farming gets nothing (section 3.3).

---

## 1. How a pickaxe swing is timed (all VERIFIED)

| Fact | Source |
|---|---|
| Every vanilla pickaxe uses `"Interactions": {"Primary": "Pickaxe_Attack"}`. It is set on `Tool_Pickaxe_Crude`; Wood, Scrap, Copper, Iron, Cobalt, Thorium, Adamantite, Mithril and Onyxium inherit it through `"Parent": "Tool_Pickaxe_Crude"` | `Assets.zip` `Server/Item/Items/Tool/Pickaxe/*.json` |
| RootInteraction `Pickaxe_Attack` = `{"Interactions": ["Pickaxe_Attack"]}`. It has **no `Cooldown` key** | `Server/Item/RootInteractions/Weapons/Pickaxe/Variants/Pickaxe_Attack.json` |
| Interaction `Pickaxe_Attack` = `Chaining` (ChainingAllowance 1.25), `Next: ["Pickaxe_Mine"]` | `Server/Item/Interactions/Weapons/Pickaxe/Variants/Pickaxe_Attack.json` |
| `Pickaxe_Mine`: `Simple` 0.083 s (plays `ItemAnimationId "Mine"`), then a `Parallel` of: block branch 0.05 s then `Pickaxe_Block_Break` (the block breaks **0.133 s** into the swing); entity hit-scan `Selector` 0.083 s + pad 0.084 s; effect branch (`Pickaxe_Mine_Effect`, 0.167 s). **Whole swing = 0.25 s.** No step sets `WaitForAnimationToFinish` | `.../Pickaxe/Attacks/Pickaxe_Mine.json`, `Pickaxe_Mine_Effect.json`, `Pickaxe_Block_Break.json` |
| Pickaxe animation `Mine` = 14-frame `.blockyanim` (`holdLastKeyframe`), `Speed 1`. It fits inside the 0.25 s swing | `Server/Item/Animations/Pickaxe.json`, `Common/.../Pickaxe/Attacks/Mine/Mine_FPS.blockyanim` |
| `InteractionManager.isOnCooldown(ref, type, root, click)`: no root `Cooldown` means time = `InteractionTypeUtils.getDefaultCooldown(type)` and id = `root.getId()` | bytecode |
| `InteractionTypeUtils.getDefaultCooldown`: **0.35 f** for every InteractionType except CollisionEnter/Leave, Projectile*, GameModeSwap, EntityStatEffect, Pickup, OnBreak, OnBreakImpact (those get 0). **Primary = 0.35 s** | bytecode + `InteractionTypeUtils$1` switch map |
| `RootInteraction.resetCooldownOnStart()` = `cooldown == null or !cooldown.skipCooldownReset`, so **true** for the pickaxe root. So `CooldownHandler.isOnCooldown` creates the entry and starts the 0.35 s cooldown **when the swing starts** | bytecode |
| `CooldownHandler$Cooldown`: `setCooldownMax(x)` lowers the remaining time to x if it was higher; `deductCharge()` then `resetCooldown()` sets remaining = cooldownMax; `CooldownHandler.tick` **removes** expired entries; `DEFAULT_CHARGE_TIMES = {0.0}` (one charge, refills at once) | bytecode + `InteractionManager.<clinit>` |
| Hatchets are the same: `Tool_Hatchet_Crude` has `Primary: "Hatchet_Attack"` (the others inherit it). The root has no `Cooldown`. `Hatchet_Chop` = 0.083 + 0.167 = **0.25 s**. Same 0.35 s cadence | `Server/Item/...Hatchet...` |
| Block damage: a block starts at health 1.0 (`BlockHealthChunk`). Each hit removes the tool's `Power` for that gather type, after `DamageBlockEvent` (where SkyyTrees multiplies). Adamantite/Mithril/Onyxium pickaxes have Rocks power 1.0, so they **one-shot rock even with no tree bonus**. The best hatchets have Woods 0.5, so logs always take at least 2 hits | `BlockHarvestUtils.damageSingleBlock` bytecode; tool JSON |

**Net: vanilla cadence = max(swing 0.25 s, cooldown 0.35 s) = 0.35 s per swing (about 2.9 swings a second), for pickaxes and
hatchets.** The last 0.10 s of every cycle is a forced wait. The server steps cooldowns in ticks, so real timings round to a tick.

---

## 2. The mechanism

### 2.1 Pieces (all stock engine types, no new Java interaction class)

- **`EffectConditionInteraction`** (`...config.none`). It lives in the "none" package: both sides simulate it and neither waits
  for data from the other. It has `generatePacket`/`configurePacket`, so it is sent to the client. `firstRun` reads the player's
  `EffectControllerComponent.getActiveEffects()`:
  - `Match: All` fails when any listed effect is missing.
  - `Match: None` fails when any listed effect is present.
  - Otherwise the step finishes, then `Next` runs (failed: `Failed` runs).
  (VERIFIED bytecode. Vanilla eating uses it the same way: `Food_EffectCondition_*`, 45 files.)
- **`TriggerCooldownInteraction`** (`...config.client`, has a packet). It calls
  `CooldownHandler.getCooldown(id, ...)`, then `setCooldownMax(cooldown)`, then `deductCharge()`. That restarts the named cooldown
  at the new length. With no `Id`, it uses the chain's initial root cooldown id, which is the root id. (VERIFIED bytecode. Vanilla
  uses it once, in the fire-trap staff.)
- **Instant steps cost no time.** `InteractionManager.doTickChain` keeps running the next operation in the **same tick** while
  each one finishes. The loop ends only when an operation is still running. So a decision tree of instant `EffectCondition` steps
  adds zero delay. (VERIFIED bytecode. SkyyCooking relies on the same thing for its 39-step food chains.)
- **Status effects from Java:**
  - Add: `EffectControllerComponent.addEffect(Ref, int index, EntityEffect, float duration, OverlapBehavior, ComponentAccessor)`.
  - Remove: `removeEffect(Ref, int, ComponentAccessor)`.
  - Read: `getActiveEffects()` gives an `Int2ObjectMap` of `ActiveEntityEffect` (`getRemainingDuration()`).
  - Index: `EntityEffect.getAssetMap().getIndex(id)`.
  SkyySkills 0.4.3 already does this in its own tick (`ecc.addEffect(ref, ids[k], fx, extra, OverlapBehavior.EXTEND, cb)`, build
  line ~3445). (VERIFIED.)

### 2.2 How one swing runs with SkyyTrees 0.2.3

1. The player clicks with a pickaxe. The client and the server each check the cooldown with id `Pickaxe_Attack`: 0.35 s default,
   started now.
2. The root `Pickaxe_Attack` (**SkyyTrees' override**) runs the interaction `Skyy_Tree_Swing_Mine`: a tree of instant
   `EffectCondition` steps.
   - No Skyy swing effect: go straight to the vanilla interaction `Pickaxe_Attack`. That is the unchanged vanilla swing and the
     unchanged 0.35 s cadence.
   - Effect `Skyy_Tree_Swing_Mine_25`: reach the leaf `TriggerCooldown {Id "Pickaxe_Attack", Cooldown 0.28}`, then vanilla
     `Pickaxe_Attack`. The cooldown that started in step 1 is now 0.28 s.
3. The vanilla swing plays exactly as before: same 0.25 s, same animation, same block break at 0.133 s, same sounds.
4. After 0.28 s the next swing may start: +25 % swings per second. The swing motion is not sped up. The idle gap after each swing
   just shrinks. At +40 % (0.25 s) the gap is gone and swings run back to back.

When the player stops clicking, the cooldown entry expires and the engine deletes it (`CooldownHandler.tick` prunes it). The next
swing starts from the root's 0.35 s default again, so nothing lingers after a pause.

### 2.3 Generated assets (from the build script; nothing from the game is committed)

| Path in the SkyyTrees jar | What |
|---|---|
| `Server/Entity/Effects/SkyyTrees/Skyy_Tree_Swing_Mine_01.json` ... `_40.json` | `{"Duration": 3, "OverlapBehavior": "Overwrite"}`. No icon, no ApplicationEffects, no stats. Hidden marker "pickaxe swing tier k %" |
| `Server/Entity/Effects/SkyyTrees/Skyy_Tree_Swing_Chop_01.json` ... `_40.json` | the same for hatchets |
| `Server/Item/Interactions/SkyyTrees/Skyy_Tree_Swing_Mine.json` | the decision tree below, leaves end in `"Pickaxe_Attack"` |
| `Server/Item/Interactions/SkyyTrees/Skyy_Tree_Swing_Chop.json` | the same for `"Hatchet_Attack"` |
| `Server/Item/RootInteractions/Weapons/Pickaxe/Variants/Pickaxe_Attack.json` | **override** (same path and id as vanilla): `{"Interactions": ["Skyy_Tree_Swing_Mine"]}` |
| `Server/Item/RootInteractions/Weapons/Hatchet/Variants/Hatchet_Attack.json` | **override**: `{"Interactions": ["Skyy_Tree_Swing_Chop"]}` |

The overrides keep vanilla's "no `Cooldown` key". So the engine default (0.35 s, id = root id) and `resetCooldownOnStart = true`
stay exactly as they were. RootInteractions and Interactions are separate asset stores, so the root `Pickaxe_Attack` pointing at
the Interaction `Pickaxe_Attack` is normal. Vanilla's own root does exactly that.

**Decision tree** (the build generates it; any correct tree is fine). The top node answers "no bonus" with one check:

```json
{ "Type": "EffectCondition", "Match": "None",
  "EntityEffectIds": ["Skyy_Tree_Swing_Mine_01", "...", "Skyy_Tree_Swing_Mine_40"],
  "Next": "Pickaxe_Attack",
  "Failed": SPLIT(1, 40) }
```

- `SPLIT(lo, hi)` with lo < hi, mid = (lo + hi + 1) / 2:
  `{"Type": "EffectCondition", "Match": "None", "EntityEffectIds": [ids mid..hi], "Next": SPLIT(lo, mid-1), "Failed": SPLIT(mid, hi)}`
  (6 levels deep for 40 tiers).
- `LEAF(k)`:
  `{"Type": "TriggerCooldown", "Cooldown": {"Id": "Pickaxe_Attack", "Cooldown": round(0.35 / (1 + k/100), 4)}, "Next": "Pickaxe_Attack"}`.
- Hatchet: the same with `Chop` ids and `"Hatchet_Attack"` (both the cooldown id and the final interaction).

### 2.4 Tier cooldowns

| Tier | +1 % | +5 % | +10 % | +15 % | +20 % | **+25 % (default max)** | +30 % | +35 % | **+40 % (ceiling)** |
|---|---|---|---|---|---|---|---|---|---|
| Seconds per swing | 0.3465 | 0.3333 | 0.3182 | 0.3043 | 0.2917 | **0.28** | 0.2692 | 0.2593 | **0.25** |
| Swings per second | 2.89 | 3.00 | 3.14 | 3.29 | 3.43 | **3.57** | 3.71 | 3.86 | **4.00** |

**Why the ceiling is +40 %.** The vanilla swing lasts 0.25 s. A cooldown shorter than that would ask for a new swing while the old
one is still running. Going faster means Hylamity's route: copy `Pickaxe_Mine` with shorter RunTimes, and give it a faster
`ItemPlayerAnimationsId` animation set. That copies and re-times vanilla content and has to track every Hytale update. Not
proposed. Open question Q4.

### 2.5 Why the client agrees (INFERRED, first test confirms)

- The client starts chains and predicts them. The server runs the same chain and reconciles through `SyncInteractionChain(s)`.
- Both interaction types above build a network packet, so the client runs them too.
- `EntityEffect` is `NetworkSerializable`, and `EffectControllerComponent` sends `EntityEffectUpdate`s, so the client knows which
  tier the player has.
- Hylamity relies on exactly this. Risk: for a moment after a tier change (up to one tick) the client and server may pick
  different leaves. The engine's desync handling corrects that swing.

### 2.6 The shipped precedent: Hylamity 0.2.0 (read-only, not enabled in Skyy's world)

- `Server/Item/RootInteractions/Weapons/Pickaxe/Variants/Root_Pickaxe_Attack_Boost.json`:
  `EffectCondition Match All ["Mining_Speed_Boost"]`, then `Next: TriggerCooldown {Cooldown 0.15909, Id "root_cooldown"}`, then
  `Pickaxe_Attack_Boost`; `Failed: "Pickaxe_Attack"`; root `"Cooldown": {"Id": "root_cooldown", "Cooldown": 0.35}`.
- `Pickaxe_Mine_Boost` is a copy of `Pickaxe_Mine` without the 0.083 s and 0.05 s delays. That is how it gets past +40 %, which we
  skip.
- `Server/Entity/Effects/Tool/Buff/Mining_Speed_Boost.json` is `Duration 1.7, Overwrite` with an icon.
  `BlockBreakEventSystem` (Java) calls `EffectControllerComponent.addEffect` when a block breaks with their Wulfrum pickaxe.
- Differences in our version:
  - We replace the root asset `Pickaxe_Attack` itself. Hylamity replaces the Crude/Copper **item** JSON so it points at its own
    root. Replacing one 1-line root is smaller and covers every pickaxe that inherits the Crude root, modded ones included.
  - We keep the vanilla swing.
  - Our effect is hidden and tiered.

### 2.7 Rejected routes (why not)

- **Reflection into the private `cooldownHandler`** (the Perfect Parries pattern, research note 2). It changes only the server's
  copy. The client keeps its own cooldown and still starts swings every 0.35 s, so nothing speeds up, or the chains desync.
- **`TimeResource.timeDilationModifier`** is shared by the whole world. It speeds up every timed interaction for everyone, and
  probably the day clock.
- **`InteractionManager.setGlobalTimeShift`** is a head start of one step for one InteractionType. It fades within 1-2 ticks, knows
  nothing about items, and is server-only.
- **Custom Java interaction or item swapping** (give the player a "fast pickaxe" item). It changes item ids and breaks sacks,
  collections and trades.
- **More breaking power** (today's design) cannot beat 1 hit per 0.35 s. That is the bug.

---

## 3. SkyyTrees 0.2.3 design

### 3.1 Node changes (ids, slots, icons, B, tokens and max levels unchanged; one new kind)

`KINDS += ["SWING"]` → index 23. Every existing kind number stays the same, so build-assert it.

| Id | 0.2.2 | 0.2.3 name | kind, max, per | Now text (`%V`) | How text |
|---|---|---|---|---|---|
| `MSpeed` | Mining Speed: DMG 25 x 0.02 = +50 % breaking power on rock and ore | **Mining Speed** | SWING, 25, **0.01** (+25 %) | `+%V pickaxe swing speed` | `Less wait between pickaxe swings - more blocks per second, even when one hit breaks the block (any pickaxe, also on mobs)` |
| `MHeavy` | Heavy Pick: DMG 20 x 0.02 on ore, "adds to Mining Speed" | **Heavy Pick** | DMG, 20, 0.02 (unchanged, +40 %) | `+%V breaking power on ore` | `Ore blocks only - ore breaks in fewer hits (more damage per hit)` |
| `FSpeed` | Chopping Speed: DMG 25 x 0.02 on wood | **Chopping Speed** | SWING, 25, **0.01** (+25 %) | `+%V hatchet swing speed` | `Less wait between hatchet swings - more logs per second (any hatchet, also on mobs)` |
| `FSpeed2` | Chopping Speed II: DMG 20 x 0.02 on wood, "adds to Chopping Speed" | **Heavy Hatchet** | DMG, 20, 0.02 (unchanged, +40 %) | `+%V breaking power on wood` | `Wood blocks break in fewer hits (more damage per hit)` |

- `TreeFx.dmgBonus`: drop `MSPEED` (rock) and `FSPEED` (wood). What stays is `ore → + MHEAVY` and `Woods → + FSPEED2`. The
  `rock` local then goes unused.
- `TreeFx.value` for SWING returns the **effective** fraction: `min(floor(per x level x 100 + 1e-6), 40) / 100`. So
  `tree:fn:bonus("Mining.MSpeed")` and the page show what really applies. This follows the precedent of `FELLER_ALL` at the Feller
  max.
- `TreeDefs.valueText` for SWING shows a whole percent. At 40 it adds " (max)".
- `TreeKit.fraction()` already counts any kind not listed as a percent node, so SWING is a percent node. No change needed.
- Manifest description: "Breaking power, ..." becomes "Pickaxe / hatchet swing speed, breaking power, ...".

### 3.2 Foraging: yes, Chopping Speed gets the same treatment (hatchets only)

**Why:**

1. **Same engine situation.** Hatchets use the same 0.35 s default cooldown over a 0.25 s swing (section 1).
2. **Top hatchets are already stuck today.** Every hatchet from Cobalt up has Woods power 0.5. Even the old maxed +90 % gives
   0.95, never 1.0, so a log takes 2 hits whatever the tree says. For endgame hatchets, Chopping Speed does nothing today, exactly
   like Mining Speed on an Adamantite pick. Swing speed helps every hatchet tier.
3. **Players expect "Speed" to mean the same thing in both trees.**

Breaking power still matters on wood for Crude to Iron hatchets, since logs are always multi-hit. So **Chopping Speed II keeps
breaking power**. It becomes "Heavy Hatchet", the Foraging twin of Heavy Pick. Only its display name and text change; its id
`FSpeed2` and its saved key stay.

"Axes" in the combat sense (`Weapon_Axe_*`, `Weapon_Battleaxe_*`, the Berserker weapons) have their own roots and are **not**
touched. The Bark Scraper uses `Scraper_Attack` and is not touched.

### 3.3 Farming: no change

The Farming tree has no speed node (its kinds are DD, ITEM, XP, HP, EXTRA, EXTRA2, MOVE). Ripe crops are F-harvested through
`UseBlockEvent`, or broken in one hit. There is no multi-swing cadence to speed up, and all 12 slots are taken. The same mechanism
could later speed up sickle swings (Q6).

### 3.4 Per-level values and cap

- LOCKED 2026-09-25: Mining Speed is **+1.6 % per level, 25 levels, +40 % at max**, so a swing every 0.25 s (back to back). Was +1 % per
  level, +25 % at max, a swing every 0.28 s. New files use `Mining.MSpeed.per=0.016`. A file already on `0.01` keeps +25 %. If +40 % is
  still too slow, vanilla swing timing may need adjusting.
- Chopping Speed stays **+1 % per level, 25 levels, +25 % at max** until a later lock says otherwise. The Heavy Hatchet hard rule above
  limits where that bonus applies.
- Hard ceiling: **+40 %**. Only 40 tier assets exist, and 40 % is where the swings run back to back. An admin can go up to it with
  `MSpeed.per` / `MSpeed.max` in Server Setup. Past +40 % the Server Setup page asks first and warns that it is capped.
- A player's tier is `floor(level x per x 100)`, which is exact with the default 0.01. An admin value like 0.015 rounds down to a
  whole percent, and the page shows the real (rounded) number.

**Old vs new time per block** (holding the button; block health 1.0; hits = ceil(1 / (power x (1 + bonus))); time about hits x
seconds per swing):

| Target, tool | vanilla | 0.2.2 at max (breaking power) | 0.2.3 at max (swing +25 %, Heavy Pick/Hatchet +40 %) |
|---|---|---|---|
| Rock, Crude pick (0.25) | 4 hits, 1.40 s | 3 hits, 1.05 s | 4 hits, 1.12 s |
| Rock, Copper pick (0.35) | 3, 1.05 s | 2, 0.70 s | 3, 0.84 s |
| Rock, Iron/Cobalt/Thorium pick (0.5) | 2, 0.70 s | 2, 0.70 s | 2, **0.56 s** |
| Rock, Adamantite/Mithril/Onyxium (1.0) | 1, 0.35 s | 1, 0.35 s | 1, **0.28 s** |
| Iron ore, Iron pick (0.25) | 4, 1.40 s | 3, 1.05 s | 3, **0.84 s** |
| Iron ore, Adamantite pick (0.5) | 2, 0.70 s | 2, 0.70 s | 2, **0.56 s** |
| Log, Crude hatchet (0.15) | 7, 2.45 s | 4, 1.40 s | 5, 1.40 s |
| Log, Iron hatchet (0.3) | 4, 1.40 s | 2, 0.70 s | 3, 0.84 s |
| Log, Cobalt+ hatchet (0.5) | 2, 0.70 s | 2, 0.70 s | 2, **0.56 s** |

What the table shows:

- From Iron-tier tools up, and for every block that one hit already breaks, the new version is faster. That is the case Skyy
  reported.
- Early tools on rock (Crude, Copper) and the Iron hatchet lose a little. The old +50 % / +90 % breaking power happened to cross a
  hit breakpoint there.
- Q2 and Q3 offer fixes if Skyy wants them.

### 3.5 When it applies

- **Only inside a pickaxe swing** (or a hatchet swing). The check lives in the swing's own root interaction. No other item runs it:
  swords, bows, the pickaxe's other actions, hoes and hatchets all use their own roots. So "only while holding a pickaxe" is built
  in. SkyyTrees does **not** need a held-item check. Skipping it also avoids a delay of up to 1 s after switching to the pickaxe.
- **Any item whose Primary root is `Pickaxe_Attack` / `Hatchet_Attack`.** That covers all vanilla pickaxes and hatchets, plus
  modded ones that inherit the Crude item. Items with their own root (for example Hylamity's Crude/Copper/Wulfrum item overrides,
  or Multitools) get no Skyy bonus. Nothing breaks.
- **Mining and combat cannot be split cheaply.** One pickaxe swing both breaks the block and hit-scans for mobs (a `Parallel`
  inside `Pickaxe_Mine`), so faster swings also mean faster hits on mobs.
  - Every vanilla pickaxe deals 1 physical damage per hit (the Crude `Pickaxe_Mine_Damage` var, inherited), so this does not
    matter.
  - Hatchets hit a bit harder, and SkyyClasses never blocks tools ("tools ... never blocked"). LOCKED 2026-09-25 HARD RULE: that must
    not stand. Hatchet swing-speed bonuses apply only while breaking trees or wood. They must not speed weapon-axe combat for Berserker
    or any combat class. Weapon axes get a separate combat swing-speed stat. Chopping Speed and Heavy Hatchet do not feed it. 0.2.3
    still speeds every hatchet swing, including hits on mobs.
  - A blocks-only version would need a `BlockCondition` step before every swing. That step waits for client data (a network round
    trip) and needs block matchers. Q5 accepted that cost for pickaxes and rejected it. The hatchet hard rule now requires the split
    for wood chopping versus combat.
- Creative mode: blocks break at once anyway. Nothing special is needed.

### 3.6 How it is applied and removed (`TreeTick`, world thread, once a second, no new system)

This goes in `TreeTick.tick` after `TreeFx.stats(cb, ref, v)`. `TreeTick` already holds `ref`, `cb` and the fresh `v[]`, and it
already skips players that are not ready yet.

```
TreeSwing.apply(cb, ref, v):
  if (!TreeCfg.SWING_ON || !TreeSwing.ready()) -> clear both families on this player, return
  TreeSwing.fam(cb, ref, MINE_IDX, tier(v[I_MSPEED]));
  TreeSwing.fam(cb, ref, CHOP_IDX, tier(v[I_FSPEED]));

TreeSwing.fam(cb, ref, int[] idx /* [1..40] */, int k):
  ecc = (EffectControllerComponent) cb.getComponent(ref, EffectControllerComponent.getComponentType()); if null return
  map = ecc.getActiveEffects()
  for t = 1..40: if (t != k && map.containsKey(idx[t])) ecc.removeEffect(ref, idx[t], cb)
  if (k > 0):
    a = map.get(idx[k])
    if (a == null || a.getRemainingDuration() < 1.5f)
      ecc.addEffect(ref, idx[k], (EntityEffect) EntityEffect.getAssetMap().getAsset(idx[k]), 3.0f, OverlapBehavior.OVERWRITE, cb)
```

- `ready()` resolves the 80 indexes the first time through (the asset maps are loaded by then) with
  `EntityEffect.getAssetMap().getIndex(id)`. `Integer.MIN_VALUE` or a negative index means missing: warn once ("swing effects
  missing - asset pack not loaded?") and keep swing off. It also checks **once** that
  `RootInteraction.getAssetMap().getAsset("Pickaxe_Attack").getInteractionIds()[0]` is `"Skyy_Tree_Swing_Mine"` (and the same for
  `Hatchet_Attack`). If not, it logs a warning ("another mod replaced the pickaxe swing root - Mining Speed swing bonus inactive for
  pickaxes"). The effects are still applied; they are harmless.
- Timing: 3 s duration, refreshed when under 1.5 s. That is one effect update per player about every 1.5-2 s, and none for players
  without the nodes. The 1 s tick keeps it alive with room to spare. Finite effects on purpose: an infinite one would be saved in
  the player's entity forever.
- **Removal:**

| When | What happens |
|---|---|
| Respec, node turned off, node disabled (`enabled=false`), level change | `TreeFx.compute` gives the new value, so the next tick (at most 1 s) swaps or removes the tier effect |
| Profile switch | the epoch changes, `compute` reads the new profile, the tier is corrected within 1 s |
| `swing.enabled` turned OFF (Server Setup) | every player's swing effects are removed within 1 s |
| Switching items | nothing needed: the bonus only exists inside the pickaxe or hatchet swing |
| Logout | the effect is saved with at most 3 s left. After the next join, `TreeTick` re-checks within 1 s of the player being ready |
| World switch | `TreeTick` runs in the new world and re-applies. No `PlayerReadyEvent` hook is used |
| Plugin shutdown | the effects run out within 3 s |
| Mid-streak change | the engine's cooldown entry keeps the last length until the player pauses for one cooldown (then it is pruned, section 2.2). At most one streak of the old speed |

- Uninstall caveat (UNVERIFIED): if a player logs out within 3 s of a refresh, a `Skyy_Tree_Swing_*` effect is saved with them.
  How the engine loads an effect id that no longer exists (SkyyTrees removed) was not checked. This is the same class of caveat as
  the `skyytree_*` stat modifiers. The HANDOFF note "turn nodes off before uninstalling" covers it; for this bonus that means turn
  `swing.enabled` off and wait 5 s.

### 3.7 Build-time generation and self-checks (the SkyyCooking pattern; the build fails when one is false)

The patch reads `Assets.zip` **in memory** (python `zipfile`, read-only) and writes only our own JSON into the jar through
`B.assemble(..., extra_files=...)`. No vanilla file is copied into the repo (the repo is public).

**Checks:**

1. The vanilla roots `Pickaxe_Attack` and `Hatchet_Attack` still equal `{"Interactions": ["Pickaxe_Attack"]}` /
   `["Hatchet_Attack"]` with no `Cooldown` key. The vanilla Interactions `Pickaxe_Attack` and `Hatchet_Attack` exist.
   `Tool_Pickaxe_Crude` / `Tool_Hatchet_Crude` still have those Primary ids.
2. The swing length worked out from `Pickaxe_Mine` / `Hatchet_Chop` (first step + longest `Parallel` branch, following the
   `Replace` default ids and a `Selector` step's forked `HitEntity` / `HitEntityRules` / `HitBlock` chains) is **at most 0.25 s**,
   so no tier cooldown is shorter than the swing.
3. `InteractionTypeUtils.getDefaultCooldown` still loads the float 0.35. Check with javassist: its ConstPool has 0.35f and the
   method's `ldc` uses it. Otherwise a Hytale update changed the base and every tier number would be wrong.
4. The build walks its own generated tree in python: for every tier 0..40, a player holding only that tier's effect reaches the
   right leaf (tier 0 reaches plain `Pickaxe_Attack`).
5. Every id the tree references exists, either generated or vanilla. No generated id collides with a vanilla id except the two
   intended root overrides. Effect JSON parses.
6. `KINDS.index("SWING") == 23` and every older kind index is unchanged.

### 3.8 Compatibility notes

- Installed mods that replace vanilla interaction files by path is a common, working pattern: AdvancedFarming and Farming_Overhaul
  replace the Sickle swings, EndlessLeveling a Shortbow step, H1Z Blunderbusses a RootInteraction. **No installed mod replaces
  `Pickaxe_Attack` or `Hatchet_Attack`** (scanned every jar and zip in `UserData/Mods`).
- If a future mod replaces the same root, whichever loads last wins. The start-up check (3.6) logs which one is active.
- SkyyCooking, SkyySkills and the other Skyy mods ship no pickaxe or hatchet interaction assets. No overlap.

---

## 4. Saved data and config migration

### 4.1 Players keep everything

- Player files (`players/<pkey>.properties`: `Mining.MSpeed=<level>`, `Foraging.FSpeed=<level>`, `Foraging.FSpeed2=<level>`) stay
  **unchanged**. Levels, off flags and respec times load as they are.
- Dust is never stored. It is always total XP / rate, minus the recomputed spend, and B and tokens do not change. So every Dust and
  token balance is identical.
- No player-file format change is needed.
- **One-time notice (default ON, Q7).** On the first tick where a profile has `MSpeed`, `FSpeed` or `FSpeed2` above 0, send the
  chat line below once. Then write `note.swing=1` into that profile's file. It is a new key: older versions ignore it, and a
  downgrade that drops it only shows the notice once more.
  > [Trees] Mining Speed now makes your pickaxe swing faster (it no longer adds breaking power). Chopping Speed does the same for
  > hatchets. Chopping Speed II is now Heavy Hatchet (breaking power on wood). A respec is free if you want to spend your Dust
  > again.

### 4.2 `trees.properties` (once, in `TreeCfg.upgrade`, when the file has no `swing.enabled` key)

This follows the 0.2.1 Tree Feller migration: same ISO-8859-1 read, `writeAtomic`, and parse from the new content.

- The exact old default lines `Mining.MSpeed.per=0.02` and `Foraging.FSpeed.per=0.02` become `...per=0.01`.
- **Custom values are kept**, with a server-log warning: "Mining.MSpeed.per=X kept - since 0.2.3 it is pickaxe swing speed per
  level (0.01 = 1 %, capped at +40 %)".
- Append the 0.2.3 block:
  ```
  # Swing speed (0.2.3): Mining Speed / Chopping Speed shorten the wait between pickaxe / hatchet swings. Their per = fraction per
  # level (0.01 = 1%), whole percents, capped at +40% (then the swings are back to back). false = those two nodes do nothing.
  swing.enabled=true
  ```
- Everything else in the file is left alone. The old node comment "# Foraging S10 Chopping Speed II (...)" keeps its old name,
  which is harmless. A fresh file gets the new name.
- If the read fails, the migrated values are used in memory and the next load tries again (the 0.2.1 rule).
- The migration runs inside `TreeCfg.load`, **before** `CfgPub.start`, so the config kit's snapshot already contains it. It is not
  logged as a hand edit.

---

## 5. Server Setup rows (tools/skyycfg.py, CONFIG-CONTRACT)

| Row | Change |
|---|---|
| **new** `("swing.enabled", "Faster tool swings", "abilities", "bool", "true", "", "", "", "", "live", "ON: Mining Speed and Chopping Speed shorten the wait between pickaxe / hatchet swings. OFF: those two nodes do nothing.", "reload")` | `TreeCfg.load` reads `swing.enabled` (default true) into `volatile boolean SWING_ON`. The build rule "every key TreeCfg.load reads is bound to a row" covers it. The `config:def` header goes from 24 rows to 25. |
| `nodes.Mining` table | LOCKED 2026-09-25: `MSpeed.per` default is `0.016` (+40 % at 25). Was `0.01` (+25 %). A file already on `0.01` keeps it. `MSpeed.max` stays 25. `MHeavy.*` unchanged. |
| `nodes.Foraging` table | `FSpeed.per` default is now `0.01` (swing speed). `FSpeed2.*` unchanged (now "Heavy Hatchet"). |
| `TreeKit.checkNode` | For a SWING node, when the saved or typed `per x max` goes over 0.40, ask first: `?Mining Speed would reach +X% - swings are capped at +40% (then they are back to back). Save it anyway?` Refusals and ranges are otherwise unchanged. |

There are no other new rows. The tier step (1 %) and the ceiling (40) are fixed in the assets at build time. A cap row could only
lower what `per` / `max` already control.

---

## 6. Patch checklist for `tools/trees_0_2_3_patch.py` (edit the patch, never the generated file)

1. VERSION 0.2.3, and a docstring section at the top with the 0.2.3 notes, UNVERIFIED items and TEST (the house pattern).
2. `KINDS += ["SWING"]` with the assert. Update the NODES rows from 3.1.
3. `TreeFx.dmgBonus`: drop MSPEED and FSPEED. `TreeFx.value` / `TreeDefs.valueText`: add the SWING case.
4. New class `TreeSwing`:
   - static `int[] MINE_IDX`, `CHOP_IDX` (length 41) and `ready()`.
   - `tier(double)`, `fam(...)`, `apply(...)`, `clear(...)`.
   - Methods go before their callers. No lambdas, generics, autoboxing or enhanced-for (javassist rules).
   Call `TreeSwing.apply(cb, ref, v)` from `TreeTick.tick`. It is **not** a new system (one `registerSystem` per class; none added).
5. `TreeCfg`: `SWING_ON`; `upgrade()` migration (4.2); `DEFAULTS` block; `ADD023` text.
6. `CFG_ROWS` + `TreeKit.checkNode` (section 5). Keep the build asserts over the default file and the rows up to date.
7. Asset generation (2.3) with the self-checks (3.7). Add the files to `extra_files`.
   (`B.manifest` already sets `IncludesAssetPack: True`.)
8. API probes (`B.probe`):
   - `EffectControllerComponent`: getComponentType, getActiveEffects, addEffect, removeEffect.
   - `EntityEffect`: getAssetMap.
   - `ActiveEntityEffect`: getRemainingDuration.
   - `OverlapBehavior`: OVERWRITE.
   - `RootInteraction`: getAssetMap, getInteractionIds.
9. One-time notice (4.1): add the `note.swing` key to `TreeData` load and save.
10. Optional admin sub-command `/tree swing`. It prints your swing tiers, their seconds per swing, and whether the two roots are
    SkyyTrees'. It needs `requirePermission("skyytrees.admin")` + `setPermissionGroups(new String[0])` (HANDOFF rule).
11. Plain `python build_skyytrees_0.2.3.py` must end with `assembled ...jar`. `tools/ci/lint.py` must report 0 fails. Never pass
    `--deploy`. `tools/deploy_set.py` only runs with `--check`.

**No SkyySkills, SkyyAccessories or SkyyClasses change is needed.**

---

## 7. Test plan

**A. Bare JVM harness** (scratch folder, deleted afterwards; like the 0.2.2 r4-trees harness):
- All classes load under `-Xverify:all`.
- `tier()` for levels 0..25 at per 0.01, 0.015 and 0.02 (capped at 40).
- Migration:
  - 0.2.2 default file: two lines changed plus the block appended; the rest byte for byte.
  - Custom `per`: kept, with the warning.
  - A second load does nothing.
- `checkNode` asks first above 40 %. The row reads back its default. Export, then import preview says nothing to change.
- `dmgBonus`: rock gets 0, ore gets MHEAVY, wood gets FSPEED2.
- The generated JSON parses. The python tree walk is correct for tiers 0..40.

**B. In game (Skyy, after a deploy):**

1. Server log shows "[SkyyTrees] 0.2.3 ready", a swing line (80 effects, pickaxe root = SkyyTrees, hatchet root = SkyyTrees), and no
   asset errors naming `Skyy_Tree_Swing`.
2. **Baseline.** No nodes, Adamantite pickaxe. Hold left-click on a stone wall for 10 s: about 28 blocks.
   `/tree swing` says tier 0.
3. **Mining Speed 25** (buy with `debug.extraDust`). The same 10 s gives about 35 blocks (0.28 s). Check:
   - The swing looks like a normal full swing with a shorter pause.
   - No block pops back, no rubber-banding. The client and server agree, which confirms 2.5.
   - No status icon or empty HUD slot appears for the hidden effect (UNVERIFIED; if one appears, see Q8).
4. **Level 5** (+5 %). `/tree` shows "+5% pickaxe swing speed", and `/tree swing` says tier 5 (0.3333 s).
5. **Hatchets.** Chopping Speed 25 on logs with a Cobalt hatchet: 2 hits per log, swings clearly faster. Heavy Hatchet 20 with an
   Iron hatchet: 3 hits instead of 4.
6. **Heavy Pick** 20 with an Iron pick on iron ore: 3 hits instead of 4. Rock with a Copper pick: 3 hits (Mining Speed no longer
   adds breaking power).
7. **Switching.** Swap to a sword: normal sword speed. Swap back: fast at once (no 1 s delay).
8. **Removal.**
   - Respec Mining: after one pause, back to 0.35 s.
   - Turn Mining Speed off: the same.
   - `swing.enabled` OFF in Server Setup: every player is vanilla within about 1 s, and the Mining Speed page says "Now: turned off
     on this server (Faster tool swings is OFF)". Back ON: fast again, and the page shows the bonus again.
9. **Persistence.** Logout and login, profile switch (a profile without the node is at vanilla speed), world switch (hub, then
   island): the tier always matches the active profile.
10. **Two accounts.** One with the node, one without, mining side by side: only the first is faster (per player).
11. A pickaxe hit on a mob comes faster (expected, 1 damage). Creative mode: nothing odd.
12. **Old data.**
    - A 0.2.2 player file loads with the same levels, tokens and Dust.
    - The notice appears once per profile.
    - `trees.properties` has `per=0.01` for both nodes, the new `swing.enabled` line, and the log line.
    - The Server Setup Trees page shows "Faster tool swings" under Abilities.

---

## 8. Open questions for Skyy (the build uses the default unless Skyy says otherwise)

| # | Question | Default |
|---|---|---|
| Q1 | ANSWERED 2026-09-25: Mining Speed max is +40 % (0.25 s per swing, `Mining.MSpeed.per=0.016`). Chopping Speed stays +25 % until a later lock. If +40 % is still too slow, vanilla swing timing may need adjusting | was +25 % for both |
| Q2 | Early tools on rock (Crude/Copper) are a little slower than with 0.2.2's +50 % breaking power (table 3.4). Should Heavy Pick also cover rock (+40 % on rock **and** ore)? | **No**, Heavy Pick stays ore-only. Adamantite+ picks one-shot rock anyway |
| Q3 | Heavy Hatchet (+40 % wood breaking power) cannot make top hatchets (0.5 power) one-chop a log. Raise it to +100 % at max so a maxed Heavy Hatchet one-chops logs with Cobalt+ hatchets (a strong endgame goal, big with Tree Feller)? | **No**, keep +40 % |
| Q4 | More than +40 % ever (a copied, re-timed vanilla swing and a faster animation, Hylamity-style)? | **No** |
| Q5 | ANSWERED 2026-09-25: faster pickaxe hits on mobs stay accepted. Hatchet swing speed is wood and trees only, and must not speed weapon-axe combat. Weapon axes get their own combat swing-speed stat | was: accept for both tools |
| Q6 | Farming: add a sickle swing-speed node later? (Every slot is taken, so it would replace one) | **No, not now** |
| Q7 | One-time chat notice explaining the change and the free respec? | **Yes** |
| Q8 | The effect is hidden (no status icon). If the HUD shows an empty slot, or Skyy wants feedback, show a small "Mining Speed" icon while it is active? | **Hidden** |
| Q9 | Should accessories / SkyyGear add swing speed later (for example a "Mining Speed" talisman)? That would need a bridge key `swing:<uuid>` that SkyyTrees sums into the tier, like the movement protocol | **Not now** (design note only) |
| Q10 | ANSWERED 2026-09-25: keep the name Heavy Hatchet. HARD RULE: it does not affect weapon-axe combat speed | **Heavy Hatchet** |

---

## 9. How this corrects the earlier research

- **Research note 1 and this file's first draft** said "no separate ability-style cooldown ... the chain length *is* the cadence"
  and "no side-effect-free lever". **Wrong on both counts.**
  - The root has no `Cooldown` key, but the engine then applies `InteractionTypeUtils.getDefaultCooldown(Primary)` = 0.35 s, which
    is longer than the 0.25 s swing.
  - The stock `EffectCondition` + `TriggerCooldown` interactions change that cooldown per player on both sides.
  - The draft's other facts are still correct and were used above: `RunTime` chain values; `TimeResource.timeDilationModifier` is
    world-wide; `globalTimeShift` is a one-step head start; `DefaultEntityStatTypes` has no attack-speed stat; server authority
    with client prediction.
- **Research note 2** was right that `CooldownHandler` is the real gate. It proposed Perfect Parries' reflection. That changes only
  the server's copy, so the client would not swing faster (2.7). It also missed Hylamity's shipped Pickaxe boost, which is the
  working pattern to copy. It found correctly that MMOSkillTree's HASTE and VEIN_MINER rewards are empty placeholders and that
  SimpleEnchantments' Efficiency is a breaking-power multiplier.
- **Research note 3** (code map) is correct and was used for sections 3-6:
  - node rows ~495/504/509/518
  - `dmgBonus` ~1859
  - `TreeDmgSys` ~2485
  - `TreeTick` ~2540
  - `CFG_ROWS` ~3032
  - `checkNode` ~3159
  - Farming has no DMG node
  - the node table in Server Setup is generic

## Appendix: engine citations (read this session)

| Claim | Where |
|---|---|
| `getDefaultCooldown`: 0.35 f default, 0 for 11 listed types (Primary not among them) | `...interaction.config.InteractionTypeUtils#getDefaultCooldown` + `InteractionTypeUtils$1.<clinit>` |
| Cooldown picked at chain start (root Cooldown else default; id = cooldownId else root id) | `com.hypixel.hytale.server.core.entity.InteractionManager#isOnCooldown` |
| `resetCooldownOnStart` = no Cooldown, or not skipCooldownReset | `RootInteraction#resetCooldownOnStart` |
| Entry created / started on check; expired entries pruned | `CooldownHandler#isOnCooldown`, `#getCooldown(String,F,[F,Z,Z)`, `#tick` (removeIf), `CooldownHandler$Cooldown#hasCooldown/deductCharge/resetCooldown/setCooldownMax/tick` |
| `DEFAULT_CHARGE_TIMES = {0f}` | `InteractionManager.<clinit>` |
| TriggerCooldown restarts the named (or root) cooldown at its own length | `...config.client.TriggerCooldownInteraction#firstRun/#resetCooldown` |
| EffectCondition Match All / None semantics, reads `EffectControllerComponent.getActiveEffects()` | `...config.none.EffectConditionInteraction#firstRun`; `protocol.Match` = {All, None} |
| Instant operations run back to back in one tick | `InteractionManager#doTickChain` (loop back to 144 while the operation counter advances) |
| Effect API | `EffectControllerComponent` (addEffect with duration and OverlapBehavior, removeEffect, getActiveEffects, CODEC = saved), `EntityEffect` (getAssetMap, isInfinite, getDuration), `OverlapBehavior` {EXTEND, OVERWRITE, IGNORE}, `ActiveEntityEffect#getRemainingDuration` |
| `getInteractionIds()` for the start-up root check | `RootInteraction` (reflect) |
| Interaction `ItemPlayerAnimationsId` overrides the animation set; server animation duration = blockyanim duration x Speed (only for WaitForAnimationToFinish steps, not used by the pickaxe) | `Interaction#getAnimationDuration` |
| Block health 1.0, damage after `DamageBlockEvent` | `BlockHarvestUtils#damageSingleBlock` (`BlockHealthChunk.getBlockHealth/damageBlock`, `setHealth(1.0)`) |
| Tool damage vs mobs: pickaxe var Physical 1 (Absolute); hatchet var Physical 5 (Dps x the damage step's own RunTime, not the swing rate) | `Tool_Pickaxe_Crude.json`, `Tool_Hatchet_Crude.json` InteractionVars; `DamageCalculator#scaleDamage`, `DamageEntityInteraction#attemptEntityDamage0` |
| Hylamity precedent | `Mods/Hylamity-0.2.0.jar`: `Root_Pickaxe_Attack_Boost.json`, `Pickaxe_Attack_Boost.json`, `Pickaxe_Mine_Boost.json`, `Mining_Speed_Boost.json`, `BlockBreakEventSystem.class` (addEffect) |
| No installed mod replaces the pickaxe or hatchet roots | scan of every jar and zip in `UserData/Mods` |
| SkyySkills applies effects from a tick (`addEffect(..., OverlapBehavior.EXTEND, cb)`) | `SkyySkills/build_skyyskills_0.4.3.py` ~3445 |
