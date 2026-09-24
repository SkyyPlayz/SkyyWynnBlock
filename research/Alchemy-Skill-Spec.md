# Alchemy skill: build spec (SkyySkills 0.4)

*Written 2026-09-23 by the research workflow `skywynn-skill-research` (writer for "alchemy"). Research only. No build script, mod folder or game file was changed.*
*Builds on SkyySkills 0.3.2 (`SkyySkills/build_skyyskills_0.3.2.py`, per-profile storage). Suggested next version: **0.4**, produced by a new `tools/skills_0_4_patch.py` (edit the patch, not the generated script, like 0.3.2).*
*Sibling specs (all written 2026-09-23, VERIFIED present in `research/`):*
- *`research/Skill-Trees-Spec.md` puts the trees in a separate SkyyTrees mod. Its small SkyySkills bridge patch is queued **after** the current SkyySkills work (its section 9.3), so 0.4 needs no rebase. That patch rebases on 0.4 instead, because both touch the /skills rows and `Perks`.*
- *`research/Cooking-Skill-Spec.md` lands in the same 0.4 patch. It adds slot 12 and changes one line of `CraftTask` (its section 9.1).*
- *`research/Smithing-Smelting-Spec.md` also lands in 0.4. It owns the Smithing XP numbers and the placed vanilla Furnace hook, so it replaces sections 10.2 and 10.3 here. Key names stay the same.*

**Legend.** VERIFIED = seen in `HytaleServer.jar` bytecode (tools/dev), in `Assets.zip`, in an installed mod jar, in our own build scripts or logs, or in a cited web source. UNVERIFIED = design, estimate or not yet tested in game. `[SKYY?]` = a number or choice Skyy (they/them) should confirm.

---

## 0. Summary

1. **Primary XP source: the vanilla Alchemy Bench**, caught with the ECS event `CraftRecipeEvent$Post`. It fires for every finished potion on the player's own entity. VERIFIED.
2. **Do not use `PlayerCraftEvent`.** Almost every potion recipe has `TimeSeconds` 1, so the bench **queues** it, and the queued path never fires `PlayerCraftEvent`. VERIFIED. This corrects the research notes.
3. **Queued crafts fire one `Post` per potion, but each `Post` reports the whole batch size.** So count **1 unit per `Post`** when `TimeSeconds > 0`. VERIFIED. The installed ZiggfreedCommon mod gets this wrong.
4. **SkyySacks crafts** (the /craft page and the Furnace tab) bypass `CraftingManager`, so no engine event fires for them. VERIFIED. They report through a new bridge function, **`skill:fn:craftxp`**. A general grant function, **`skill:fn:addxp`**, is added for future reforge and powder mods.
5. **XP table:** 30 Alchemy Bench recipes, VERIFIED from `Assets.zip`. Lesser potion 50, Small 850, normal 8,000, Greater 18,000. Vials pay 0. The bomb pays 10 because salvaging it back makes a loop. This is sized to the shared 100-level curve. Level 50 takes about 27 focused hours (UNVERIFIED estimate).
6. **Perks per level:** potion effects last +1% longer (+100% at level 100) and max Mana goes up +0.2. There is also a 0.2% chance per level to brew one extra potion `[SKYY?]`. The duration perk uses `EffectControllerComponent.addEffect(..., OverlapBehavior.EXTEND, ...)`, which is VERIFIED to extend without restarting the effect.
7. **Slots:** Alchemy = slot 10, Smithing = slot 11. Slot 3 ("Combat") stays in storage so old saves keep their data, but its /skills row goes away. The class weapon skill gets its own named row. Every `CLASS0..N` loop must be bounded to `CLASS_END = 10` (section 9.3).
8. **Smithing row:** exists now. It levels from smelting in the SkyySacks Furnace tab, per Skyy's newer plan row. Reforging and powders feed it later through `skill:fn:addxp`. The placed vanilla Furnace fires no craft event (VERIFIED). `research/Smithing-Smelting-Spec.md` section 3 specifies a separate hook for it in the same 0.4 build (see 10.3).

---

## 1. Decisions this spec follows

| Source | Decision | How this spec applies it |
|---|---|---|
| Skyy focus call (HANDOFF section 1) | "Alchemy (build it)" | Full skill: slot, XP, perks, page |
| Skyy, 22:45 log + `SkyySkills-Plan.md` + `SkyySacks-Plan.md` (commit 67ed1ea) | Alchemy is **table use only**. The Alchemy Bench accessory and the /craft Alchemy tab go away. The vanilla table draws from the sacks | The vanilla bench is the main source. The bridge covers any Alchemy recipe SkyySacks still crafts (the 0.7.2 tab, the Collections tab) at no cost |
| Same commit | "Smelting in the furnace (vanilla Furnace and the SkyySacks Furnace tab) gives Smithing XP" | The Smithing row gets smelting XP now (SkyySacks tab). The vanilla Furnace hook is in `research/Smithing-Smelting-Spec.md` section 3 (see 10.3) |
| Workflow brief | "Smithing row with no XP source yet" | **Conflict:** Skyy's newer plan row adds smelting, and Skyy's word wins. To match the brief instead, set `smithing.smelt.enabled=false` |
| Design lock | No shared Combat skill | Slot 3 is retired from the UI; storage is kept (section 9) |
| HANDOFF engineering lock | Level cap 100, same table for every skill | Alchemy and Smithing use `SkillDefs.PER` / `CUM` unchanged |
| PROFILES-CONTRACT | Per-profile storage via `pkey` | Already handled by the 0.3.2 file layer (section 8) |

---

## 2. How alchemy works in Hytale today (facts)

**Bench.** VERIFIED from `Server/Item/Items/Bench/Bench_Alchemy.json`:
- Item `Bench_Alchemy`, bench id **`Alchemybench`**, `Bench.Type: "Crafting"`. Furnace and Tannery are `"Processing"`.
- Categories: `Alchemy_Potions`, `Alchemy_Potions_Misc`, `Alchemy_Seeds`, `Alchemy_Bombs`.
- `TierLevels` has 4 entries with `CraftingTimeReductionModifier` 0.0 / 0.2 / 0.4 / 0.6. Upgrades cost silver + gold bars and one gem: Emerald, then Zephyr, Sapphire, Ruby.
- Recipes ask for `RequiredTierLevel` 1 to 5. How tier 5 reads its time reduction (there are only 4 entries) is UNVERIFIED and does not matter here.
- The bench itself is crafted at Workbench tier 2.

**Recipes.** VERIFIED: a scan of `Server/Item/Items/**` and `Server/Item/Recipes/**` found **30** recipes with `BenchRequirement.Id == "Alchemybench"`. The research notes said 31, but their own table lists 30.

- **Recipe ids.** Recipes built into an item get the id `<ItemId>_Recipe_Generated_<n>`. VERIFIED: `CraftingRecipe.generateIdFromItemRecipe(Item, int)` exists, and the live log `Skyy_SkyySacks/crafts.log` shows `Ingredient_Bar_Iron_Recipe_Generated_0`. So **our XP table is keyed by the primary output item id**, not the recipe id.

**Which window the bench opens.** A Crafting-type bench opens `SimpleCraftingWindow`. This is VERIFIED by inference: the Alchemy block defines exactly the two states `CraftCompleted` and `CraftCompletedInstant`, and those are the two states `SimpleCraftingWindow.handleAction` sets. The hook in section 3 works for any window anyway.

**Potion effects.** VERIFIED from `Server/Entity/Effects/Potion/*.json`, `Status/Antidote.json` and `ActiveEntityEffect.calculateCyclesToRun` bytecode:

| Effect | Duration | Pulse (DamageCalculatorCooldown) | What it does | Pulses at base |
|---|---|---|---|---|
| `Potion_Health_Instant*` | 0.1 s | 0 = applies once | +15..35% Health | 1 (fixed) |
| `Potion_Health_Regen*` | 5.05 s | 5 s | +15..55% Health per pulse | 1 |
| `Potion_Signature_Regen*` | 30.05 s | 5 s | +5..15% SignatureEnergy per pulse | 6 |
| `Potion_Stamina_Instant*` | 1.5 s | 0 | +30..90% Stamina | 1 (fixed) |
| `Potion_Stamina_Cooldown` | 15 s | - | debuff after a stamina potion | - |
| `Potion_Morph_Dog/Frog/Mouse/Pigeon` | 60 s | - | model change | - |
| `Antidote` | 120 s | - | applied by the Antidote potion (and buckets) | - |

- Pulse rule (VERIFIED bytecode): with cooldown > 0, the effect pulses every `cooldown` seconds while `remainingDuration > 0`. The first pulse comes after one full cooldown. With cooldown 0, it applies exactly once.
- Every potion effect uses `OverlapBehavior: Overwrite`. Drinking again while it is active resets the remaining time to the base duration.

---

## 3. XP sources

### 3.1 Vanilla Alchemy Bench: `CraftRecipeEvent$Post` (VERIFIED)

**What the engine does.** VERIFIED: `CraftingManager` and `SimpleCraftingWindow` bytecode, disassembled with `tools/dev/bcfull.py`.

- `SimpleCraftingWindow.handleAction` (offsets 148-203) picks the path:
  - If `recipe.getTimeSeconds() > 0`, it calls `CraftingManager.queueCraft(...)`. This is the **queued** path.
  - Otherwise it calls `CraftingManager.craftItem(...)`. This is the **instant** path.
- **Queued path.** `queueCraft` fires `CraftRecipeEvent$Pre` once. Later, `CraftingManager.tick` removes the inputs for one unit at a time. When a unit finishes it fires **`new CraftRecipeEvent$Post(job.recipe, job.quantity)`** on the player's `Ref` (offsets 681-704), then `giveOutput` unless the event was cancelled.
  - So **one `Post` fires per finished unit, but `getQuantity()` returns the whole job size**.
  - **`PlayerCraftEvent` is never fired on this path.**
- **Instant path.** `craftItem` fires `Pre`, removes the inputs, fires `Post(recipe, quantity)` once, calls `giveOutput`, then fires `PlayerCraftEvent` (world event bus).
- **Creative mode.** Both paths skip input removal when the player's `GameMode` is `Creative` (`tick` offset 185, `craftItem` offset 130). Creative crafts are free.
- **Cancel.** `cancelAllCrafting` refunds the inputs through `refundInputToInventory`. It fires no `Post`.
- **Who fires `Post`.** Only `CraftingManager.craftItem` and `CraftingManager.tick` construct it (`tools/dev/callers.py`).
  - The placed Furnace and Tannery run in `ProcessingBenchBlock.advanceProcessing` (driven by `BenchSystems$ProcessingBenchTick`) and fire no craft event at all.
- **Which potions queue.** 18 of the 30 Alchemy recipes (every potion plus the bomb) have `TimeSeconds` 1 or 0.5, so they take the queued path. The other 12 (vials, seeds, fertilizer) have 0 or no time, which is assumed to read as 0 (UNVERIFIED default), so they take the instant path.
- **Precedent.** `ZiggfreedCommon-2.0.0.jar` `com.ziggfreed.common.objectives.producer.ZigCraftProducer extends EntityEventSystem` handles `CraftRecipeEvent$Post` the same way: `chunk.getReferenceTo(idx)`, then the `PlayerRef` component, with `getQuery()` = `Archetype.empty()`. VERIFIED with `reflectmod.py` / `bcmod.py`.
  - It counts `max(1, getQuantity())`, which over-counts queued batches. **Do not copy that part.**

**Hook.** This is a new `CraftSys` built with the existing `event_system()` helper (build script line ~2528). The pattern matches `BreakSys`: defer to `world.execute`, then check for cancel.

```python
CRE  = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent"
CRP_ = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Post"   # '$' form, like UBP = UseBlockEvent$Post
CRR  = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
BRQ  = "com.hypixel.hytale.protocol.BenchRequirement"      # public fields: id, requiredTierLevel, type (VERIFIED reflect)
MQ   = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"
csy  = pool.makeClass(PKG + ".CraftSys", pool.get(EES))
event_system(csy, "CraftSys", CRP_, f"""
    {CRP_} e = ({CRP_}) ev;
    {CRR} rc = e.getCraftedRecipe();
    if (rc == null) return;
    long[] rule = {PKG}.RecipeXp.classify(rc);            // {{slot, base xp per craft}} or null (section 4)
    if (rule == null) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null || {PKG}.SkillXp.creative(st, r)) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    int units = rc.getTimeSeconds() > 0.0f ? 1 : Math.max(1, e.getQuantity());   // queued: 1 per Post (see above)
    java.util.UUID u = pr.getUuid();
    w.execute(new {PKG}.CraftTask(e, u, w.getName(), rc, rule, units, {PKG}.SkillStore.pkey(u)));""")
```

**`CraftTask.run()`** runs on the world thread, after every other system has seen the event:
1. `if (ev.isCancelled()) return;`
2. `PlayerRef pr = Universe.get().getPlayer(u)`. Stop if it is null or `!pr.isValid()`.
3. `if (!key.equals(SkillStore.pkey(u))) return;` The profile switched between the craft and the award, so nothing is credited to the wrong save.
4. `SkillXp.gain(pr, (int) rule[0], SkillCfg.scaled(rule[1] * units));` This reuses the existing chat line, level-up line, coins and publish.
5. If `rule[0] == SkillDefs.ALCHEMY`: `Brew.extraPotion(pr, rc, units, world)` (section 5.3).

Register it in `setup()` next to the others: `getEntityStoreRegistry().registerSystem(new {PKG}.CraftSys());`.

The unit rule is safe for Alchemy recipes. `craftItem` is only reached for a bench recipe when `TimeSeconds <= 0`. The other `craftItem` caller is `FieldCraftingWindow` (via `CraftingWindow.craftSimpleItem`), which is pocket Fieldcraft, and no Alchemybench recipe is a Fieldcraft recipe. VERIFIED from `callers.py` output.

### 3.2 SkyySacks crafts: bridge `skill:fn:craftxp` (VERIFIED need, new contract)

`build_skyysacks_0.7.2.py` does its own crafting. VERIFIED: a grep finds no `craftItem` or `queueCraft` call. So engine events never see these crafts:
- **/craft page** (`CraftPage.handleDataEvent`, 0.7.2 line 2361; the `"craft:"` branch starts at line 2378): counted removal, then `SimpleItemContainer.addOrDropItemStack`, then `CraftLog.write(k, recipeId, qty, done, flag, given, audit)` (line 2450). VERIFIED. `CraftPageFactory` only builds a `CraftPage` for a tab (`Function.apply`) and has no `handleDataEvent`.
- **Furnace / Tannery tab**: `ProcBench.finishUnit(ProcJob j)` adds the outputs of one unit of `j.recipe` to the output slot. It is called from `advance(now)`, which `ProcTask` runs every second on the world thread for online players.

SkyySacks reports these with `skill:fn:craftxp` (section 7). SkyySkills decides the skill and the XP from the same `RecipeXp.classify` table the bench uses. Alchemybench recipes go to Alchemy, Furnace recipes go to Smithing, everything else pays 0. So SkyySacks needs no skill knowledge.

### 3.3 Not XP sources (by design)

| Action | Why not |
|---|---|
| Drinking a potion | No consume event exists in `HytaleServer.jar` (VERIFIED by absence; consuming runs through `ApplyEffectInteraction` in the item's interaction chain). XP comes from brewing, like SkyBlock |
| Resizing vials (`Potion_Empty_Small`, `Potion_Empty_Large`) | `Potion_Empty_Small` splits 1 vial into 2 small ones; `Potion_Empty_Large` merges 2 vials into 1 large one (VERIFIED, `Server/Item/Items/Potion/*.json`). Both are free and pointless, so 0 XP |
| Cancelling or refunding a queued craft | No `Post` fires (VERIFIED) |
| Creative mode | Inputs are not consumed (VERIFIED). Uses the existing `creativeXp=false` |
| Salvaging | Salvage is a Processing bench, so no `Post` (VERIFIED). It pays nothing |

---

## 4. XP table and pace

### 4.1 Table: base XP per finished craft

The key is the recipe's **primary output id**. This is base XP, before the global `multiplier`. One craft pays once, whatever the output count.

| Output | Tier | Inputs (VERIFIED, Assets.zip) | Out | XP/craft |
|---|---|---|---|---|
| `Potion_Health_Lesser`, `Potion_Signature_Lesser`, `Potion_Stamina_Lesser` | I | small vial + fruit x6 + petals x3 | 1 | **50** |
| `Potion_Antidote` | I | vial + fibre x5 + life essence x2 + venom sac | 1 | **80** |
| `Weapon_Bomb_Popberry` | I | red berries x6 + boom powder x2 + fibre x4 | 2 | **10** (loop, see 6.4) |
| `Potion_Morph_Dog/Frog/Mouse/Pigeon` | I, Memories 4 | vial + life essence x10 + one item | 1 | **800** |
| `Potion_Empty_Small`, `Potion_Empty_Large` | I | vial x1 / vial x2 | 2 / 1 | **0** |
| `Plant_Seeds_Health1/Mana1/Stamina1` | II | void essence x2 | 3 | **60** |
| `Tool_Fertilizer_Crystal` | II | crystal shards x25 + void essence | 1 | **300** |
| `Potion_Health_Small`, `Potion_Signature_Small`, `Potion_Stamina_Small` | II | Lesser potion + tier-1 alchemy crop | 1 | **850** |
| `Potion_Health`, `Potion_Signature`, `Potion_Stamina` | III | vial + fruit x12 + petals x6 + tier-2 crop | 1 | **8,000** |
| `Plant_Seeds_Health2/Mana2/Stamina2` | IV | void essence x4 | 2 | **300** |
| `Potion_Health_Greater`, `Potion_Signature_Greater`, `Potion_Stamina_Greater` | IV | normal potion + tier-3 crop | 1 | **18,000** |
| `Plant_Seeds_Health3/Mana3/Stamina3` | V | void essence x8 | 1 | **1,200** |
| Any other Alchemybench recipe (future content) | by `RequiredTierLevel` | - | - | `alchemy.tierXp` = 50, 850, 8000, 18000, 18000; the server log names it once |

**Chains.** A Small potion eats a Lesser, so the chain pays 900. A Greater eats a normal potion, so the chain pays 26,000.

**The alchemy crops.** The tier-1 to tier-3 alchemy crops (`Plant_Crop_Health1..3`, Mana, Stamina) already pay Farming 10 / 15 / 20 (0.3.2 defaults, VERIFIED). So alchemy also feeds Farming. Wynncraft's Alchemism is only a half match: its potions take Farming grain **and** Fishing oil (more grain than oil). SkyWynn has only the Farming half, because Fishing is shelved (https://wynncraft.wiki.gg/wiki/Alchemism, VERIFIED by fetch on 2026-09-23).

**Why this matches SkyBlock.** Numbers VERIFIED at https://hypixelskyblock.minecraft.wiki/w/Alchemy:
- SkyBlock pays per potion by ingredient rank. Base Sugar is +5; Enchanted Sugar Cane +15,000; Enchanted Blaze Rod +23,000.
- It caps at 50, using the standard table: level 50 = 55,172,425 total XP. That is the same number as our levels 1-50 (0.3.2 asserts the table).
- We map Hytale's four potion tiers onto that ladder:
  - Lesser (about 10 raw items) sits near SkyBlock's cheap brews.
  - Greater sits between Enchanted Sugar Cane and Enchanted Blaze Rod.
- So a Greater potion pays about what SkyBlock's power-leveling brews pay per potion.

### 4.2 Crafts to reach each level (VERIFIED arithmetic on the 0.3.2 table)

| Band | XP needed | Main brew at that stage | Crafts needed |
|---|---|---|---|
| 0 → 10 | 9,925 | Lesser (bench I) | 199 potions |
| 10 → 20 | 512,500 | Small chains (bench II) | 570 chains |
| 20 → 25 | 2,500,000 | normal potions (bench III) | 313 |
| 25 → 50 | 52,150,000 | Greater chains (bench IV) | 2,006 chains |
| 50 → 60 | 56,500,000 | Greater chains | 2,173 chains |
| 60 → 100 | 526,000,000 | Greater chains | 20,231 chains (level 99 → 100 alone: 731) |

### 4.3 Time estimate (UNVERIFIED throughput)

Assumed pace: about 1,800 plant items gathered per hour from a planted patch with bags. (The word "Garden" here was a SkyBlock-style patch, not a SkyWynn island. SkyWynn's Garden island is parked as of 2026-09-24; farming stays on the main islands.) That gives about 200 Lesser, 190 Small chains or 100 normal / Greater chains per hour (plant-limited).

| To reach | Hours |
|---|---|
| Level 10 | about 1 h |
| Level 20 | about 4 h |
| Level 25 | about 7 h |
| Level 50 | about **27 h** |
| Level 60 | about 49 h |
| Level 100 | about 250 h |

This is faster than SkyWynn's raw Mining numbers and slower than a coin-funded SkyBlock run. Tune it with `multiplier` or the per-item keys. `[SKYY?]`

---

## 5. Per-level perks (all VERIFIED implementable)

These go to the **player who drinks or brews**, at the level of their **active profile**.

### 5.1 Brewer: potion effects last longer (headline, SkyBlock parity)

- Default **+1% per level**, capped at +100% (x2 at level 100): `perk.alchemy.durationPerLevel=0.01`, `perk.alchemy.durationMax=1.0`.
- SkyBlock gives +1% per level to +50% at its cap of 50 (wiki, VERIFIED).
- Skyy's Cooking target is x2 at 50 and x4 at 100. For Cooking parity, use 0.03 and 3.0. `[SKYY?]`

**Engine support.** VERIFIED from `EffectControllerComponent.addEffect(Ref, int, EntityEffect, float, OverlapBehavior, ComponentAccessor)` bytecode:
- If the effect is already active and the behavior is `OverlapBehavior.EXTEND`, it does `remainingDuration += duration`, sends an `EntityEffectUpdate` to the client and returns `true`.
- It does **not** create a new `ActiveEntityEffect`. The pulse timer (`sinceLastDamage`) keeps running, so there is no extra pulse and no restart.
- `OverlapBehavior` has `EXTEND`, `OVERWRITE` and `IGNORE`.
- Changing effect **strength** is not possible: `EntityEffect` is an immutable codec asset with getters only (VERIFIED reflect).

**Detection.** This is design, UNVERIFIED in game. It runs every tick inside the existing `AcroSys.tick` (the same place `Acro.dodge` already checks effects every tick with `EntityEffect.getAssetMap().getIndex(...)` and `ecc.hasEffect(...)`).

```java
// Brew.tick(UUID u, Store st, CommandBuffer cb, Ref ref, float dt) - called every tick from AcroSys.tick, BEFORE the 1 s gate
Float b = (Float) BONUS.get(u);                         // set once per second by Perks.tick: min(level*perLevel, max)
if (b == null || b.floatValue() <= 0.0f) { SEEN.remove(u); return; }
int[] ids = AlchCfg.extIdx();                           // resolved lazily from perk.alchemy.extend via EntityEffect.getAssetMap().getIndex(id)
EffectControllerComponent ecc = (EffectControllerComponent) st.getComponent(ref, EffectControllerComponent.getComponentType());
if (ecc == null || ids.length == 0) return;
Object[] seen = (Object[]) SEEN.get(u);                 // [2k] = last ActiveEntityEffect object, [2k+1] = Float remaining after our last look
if (seen == null || seen.length != 2 * ids.length) { seen = new Object[2 * ids.length]; SEEN.put(u, seen); }
it.unimi.dsi.fastutil.ints.Int2ObjectMap m = ecc.getActiveEffects();
for (int k = 0; k < ids.length; k++) {
  Object o = m == null ? null : m.get(ids[k]);
  if (!(o instanceof ActiveEntityEffect)) { seen[2 * k] = null; seen[2 * k + 1] = null; continue; }
  ActiveEntityEffect a = (ActiveEntityEffect) o;
  if (a.isInfinite()) continue;
  EntityEffect fx = (EntityEffect) EntityEffect.getAssetMap().getAsset(ids[k]);
  if (fx == null || fx.isDebuff()) continue;
  float rem = a.getRemainingDuration();
  boolean fresh = seen[2 * k] != a;                                          // a new application (new object)
  if (!fresh) {
    float last = ((Float) seen[2 * k + 1]).floatValue();
    if (rem > last + 0.01f) fresh = true;                                    // Overwrite re-drink reset it upward
    else if (rem < last - dt - 0.25f && Math.abs(rem - fx.getDuration()) < 0.5f) fresh = true;  // re-drink reset it DOWN to base
  }
  if (fresh) {
    float extra = fx.getDuration() * b.floatValue();
    if (extra >= 0.05f && ecc.addEffect(ref, ids[k], fx, extra, OverlapBehavior.EXTEND, cb)) rem = rem + extra;
  }
  seen[2 * k] = a;
  seen[2 * k + 1] = Float.valueOf(rem);
}
```

- **Why this is safe.** Remaining time can only go **up** through `addEffect`, so an upward jump is always a re-application. Lag cannot cause it, because we compare against the last value we saw in game time, not wall time. Each application is extended once, by `base x bonus`, so repeated drinking can never stack past `base x (1 + bonus)`.
- **Whitelist.** `perk.alchemy.extend` holds exact effect ids. The build script checks each one against `Server/Entity/Effects/**`:
  - `Potion_Health_Regen`, `_Lesser`, `_Small`, `_Large`, `_Greater`
  - `Potion_Signature_Regen`, `_Lesser`, `_Small`, `_Large`, `_Greater`
  - `Potion_Morph_Dog`, `Potion_Morph_Frog`, `Potion_Morph_Mouse`, `Potion_Morph_Pigeon`
  - `Antidote`
- **Left out on purpose:**
  - `*_Instant*`, because a cooldown-0 effect applies once whatever its duration (VERIFIED), so extending it does nothing.
  - `Potion_Stamina_Cooldown`, which is a debuff.
  - `Potion_Morph_Mosshorn`, a debuff from buckets.
  - `Potion_Stamina_Regen`, which only an NPC interaction applies (`DamageEntityParent.json`).
- **What players actually get** (VERIFIED pulse math):

  | Level | Mana potion regen pulses | Health regen pulses | Morph length | Antidote length |
  |---|---|---|---|---|
  | 0 (base) | 6 | 1 | 60 s | 120 s |
  | 25 | 7 | 1 | 75 s | 150 s |
  | 50 | 9 | 1 | 90 s | 180 s |
  | 99+ | 11 → 12 | **2** | about 120 s | about 240 s |

  **Honest limit:** a Health potion's regen is one pulse at 5 s, so its second pulse only arrives at +98% or more (level 99+). The instant heal never changes. Option for Skyy in section 15.
- Antidote from buckets also gets extended. The perk goes by effect, not by source. This is harmless.

### 5.2 Max Mana (SkyBlock's Intelligence analogue)

- `perk.alchemy.manaPerLevel=0.2`: +20 max Mana at level 100. `[SKYY?]`
- SkyBlock gives +1 to +2 Intelligence per Alchemy level (wiki, VERIFIED).
- It uses the existing flat-perk mechanism unchanged: once per second, `Perks.tick` puts `StaticModifier(MAX, ADDITIVE)` on key `skyyskill_mana`.
- This gives SkyyAccessories' Intelligence talismans (a % of flat Mana) something to multiply. Vanilla base Mana is 0 (HANDOFF balance note).

### 5.3 Extra potion (the gathering skills' double drops, for brewing) `[SKYY?]`

- `perk.alchemy.extraPotionPerLevel=0.002`: a 0.2% chance per level, 20% at level 100, capped by `perk.alchemy.extraPotionMax=0.25`.
- One roll per finished unit (vanilla bench) or per reported craft (bridge).
- On a hit, it gives the recipe's primary output once more: `new ItemStack(out.getItemId(), out.getQuantity())`.
- The item is handed out by the existing `Perks.give(pr, List, world)`, which calls `SimpleItemContainer.addOrDropItemStack(st, r, p.getInventory().getCombinedStorageHotbarBackpack(), is)`. VERIFIED: 0.3.2 double drops use exactly this.
- Only outputs starting with `Potion_` or `Weapon_Bomb_` qualify, never `Potion_Empty*` (`perk.alchemy.extraPotionOnly`, `...Never`). Seeds and vials never double.
- Chat line: "Extra potion! +1 Potion Health Greater (Alchemy perk)". It is throttled like "Double drop!" and hidden by `/skills quiet`.
- Set the rate to 0 to turn it off.

### 5.4 Considered and rejected

| Idea | Why not |
|---|---|
| Stronger potions (bigger heal) | `EntityEffect` numbers cannot be changed at runtime (VERIFIED). A bonus heal through `EntityStatMap.addStatValue` would need to catch 0.1 s instant effects and guess what "Percent" means (UNVERIFIED). Not worth the risk now |
| mcMMO Catalysis (faster brewing) | `CraftingManager$CraftingJob` has no public fields or setters (VERIFIED reflect), and bench speed comes from the bench tier asset |
| Unlocking recipes by level (Wynncraft / mcMMO style) | SkyBlock does not gate potions by the brewer's Alchemy level. It does gate most non-vanilla potions behind a **Collection tier** instead, for example Haste needs Coal III and Archery needs Feather III (https://hypixelskyblock.minecraft.wiki/w/Potions, VERIFIED by fetch on 2026-09-23). Hytale already gates by bench tier and Memories level. If Skyy wants a SkyBlock-style unlock, it belongs with Collections, not the Alchemy skill (design, UNVERIFIED) |

---

## 6. Anti-exploit rules

1. **Creative:** no XP on either path. The bench path checks `SkillXp.creative(st, r)` in `CraftSys`; the bridge path checks it again on the world thread in `BridgeTask`. Creative crafts consume nothing (VERIFIED).
2. **Cancelled events:** `CraftTask` checks `ev.isCancelled()` after every system has run (`world.execute` always queues, which is the documented 0.1 `BreakTask` pattern).
3. **Batch size trap:** queued recipes count 1 unit per `Post`, never `getQuantity()` (VERIFIED, section 3.1).
4. **Craft / uncraft loops:**
   - The only Alchemy output with a reverse recipe is `Weapon_Bomb_Popberry`. Salvaging 1 bomb returns 2 berries + 1 boom powder + 1 fibre (`Server/Item/Recipes/Salvage/Salvage_Weapon_Bomb_Popberry.json`, VERIFIED). That recovers 2/3 of the inputs, so the bomb pays **10**.
   - Vials pay 0.
   - `Salvage_Weapon_Deployable_Healing_Totem` returns 3 normal Health potions from a totem that cost 10 Greater. That is a net loss, not a loop.
   - **Build-time check:** scan `Server/Item/Items/**` + `Server/Item/Recipes/**`. The build fails if any Alchemybench output worth more than 10 XP is an input to a recipe that returns one of that recipe's own inputs. This reruns on every build, so a Hytale update cannot slip a loop in.
5. **No double count:** vanilla bench crafts go through the event only. SkyySacks calls the bridge only for crafts that did **not** go through `CraftingManager` (contract rule, section 7).
6. **Bridge caps:**
   - Refuse a call over `bridge.maxXpPerCall=500000` base XP.
   - Cap each player at `bridge.maxXpPerMinute=3000000` (after the multiplier) across all bridge sources, with one server-log line per minute when it trips.
   - The vanilla bench path is not capped. Every `Post` is a real, paid, non-creative craft, and the legit maximum is about 2.7M per minute (150 Greater per minute at bench IV).
7. **Offline:** the bridge refuses unknown or offline players (returns FALSE / 0). No disk I/O on the caller's thread.
8. **Profile switch:** the award is dropped if `pkey(u)` changed between the craft and the award. The bridge refuses when the caller's optional `expectKey` differs.
9. **Potion extension stacking:** at most one extension per application (section 5.1). State lives in memory per UUID. It is cleared on an epoch change (`Perks.switched`) and on disconnect (`Acro.retainOnline` prunes it).
10. **Soft gate (future):** every award goes through `SkillXp.gain`, so the drift slowdown will apply automatically when it is built.

---

## 7. Bridge contract

Both functions are published on `System.getProperties().get("skyy.bridge")` in `setup()`, next to `skill:fn:level`, and removed in `shutdown()`. They are plain `java.util.function.Function` objects: no generics, no lambdas. Callers find them the same way SkyySkills finds `coins:fn:add`.

### 7.1 `skill:fn:addxp`: general grant (reforge, powders, future mods)

```
apply(Object[] { java.util.UUID player, String skill, Number baseXp, String source }) -> Boolean
```
- `skill` must be an exact `SkillDefs.NAMES` or `LABELS` entry (no 3-letter prefix match), **and** listed in `bridge.addxp.skills` (default `Alchemy,Smithing`). Gathering, Acrobatics and class skills cannot be granted from outside.
- `baseXp` is `longValue()`, more than 0 and at most `bridge.maxXpPerCall`. SkyySkills applies `multiplier` (`SkillCfg.scaled`) and the per-minute cap.
- `source` is free text for logs (`"reforge:Weapon_Sword_Iron"`, `"powder:fire"`).
- **TRUE** = accepted and queued on the player's world thread. The creative / profile re-check there can still drop it. **FALSE** = refused: unknown skill, not grantable, bad amount, cap, offline.
- It can be called from any thread. It never blocks and never does file I/O.

### 7.2 `skill:fn:craftxp`: "I finished these crafts without CraftingManager"

```
apply(Object[] { java.util.UUID player, String recipeId, Number crafts, String source [, String expectKey] }) -> Long
```
- `recipeId` = `CraftingRecipe.getId()`. It is resolved with `CraftingRecipe.getAssetMap().getAsset(id)`; `DefaultAssetMap.getAsset(Object)` is VERIFIED in `SimpleCraftingWindow` bytecode and used by SkyySacks.
- The skill and XP come from `RecipeXp.classify(recipe)`. `crafts` is clamped to 1..10000.
- The optional `expectKey` is the caller's profile storage key. If it differs, the call is refused.
- It returns the scaled XP accepted, or `0L`. It also rolls the extra-potion perk for Alchemy recipes.
- **Rule for callers:** call it only for crafts your mod completed itself. Never call it for crafts that went through `CraftingManager.craftItem` / `queueCraft`; SkyySkills already counts those.

### 7.3 What SkyySacks must call, and when (for its next build; nothing is edited here)

1. **/craft page:** in `CraftPage.handleDataEvent` (not `CraftPageFactory`), `"craft:"` branch, right after `CraftLog.write(...)` (0.7.2 line 2450), when `done > 0`:
   ```java
   try {
     Object f = bridge().get("skill:fn:craftxp");
     if (f instanceof java.util.function.Function)
       ((java.util.function.Function) f).apply(new Object[] { u, String.valueOf(r.getId()), Integer.valueOf(done), "sacks:craft", k });
   } catch (Throwable t) { }
   ```
   This covers every tab. Non-alchemy / non-furnace recipes return 0. It stays correct after the Alchemy tab is removed.
2. **Furnace tab:**
   - Add `public java.util.LinkedHashMap xpDone` (recipe id → Integer) to `ProcBench`. Increment it in `finishUnit` only when `paid == true`, meaning a real output. The no-output fallback and `cancel()` never count.
   - In `ProcTask.run()`, right after `int d = pb.advance(now);`, drain `xpDone` with one `craftxp(u, recipe, count, "sacks:" + pb.bench.toLowerCase(), k)` call per recipe.
   - Memory only: a crash loses at most 1 s of XP. Offline replay is credited on the first `ProcTask` after login, when the player is online.
   - `research/Smithing-Smelting-Spec.md` section 4 gives the exact place for SkyySacks 0.7.3 and its offline-replay ledger. Where the two differ, follow that spec.
3. SkyySacks keeps working without SkyySkills: the bridge key is simply missing.

### 7.4 Future reforge / powder mod (Smithing)

After the reforge or powder is paid for and applied, call `skill:fn:addxp` with `{u, "Smithing", Long.valueOf(xp), "reforge:<itemId>"}`. The amounts belong to that mod `[SKYY?]`. SkyySkills needs no change.

---

## 8. Storage per profile (tools/PROFILES-CONTRACT.md)

- **Files.** The file is `Skyy_SkyySkills/players/<pkey>.properties`, where `pkey` = `SkillStore.pkey(u)` (the contract helper, already in 0.3.2). New keys `Alchemy`, `Alchemy.paid`, `Smithing`, `Smithing.paid` are written by `snap()` and read by `readFile()` through `SkillDefs.NAMES`. So they are per profile with no new code.
  - Old files simply have no key, which reads as 0 XP. The paid marker defaults to the current level, so there are no back-payments. VERIFIED `readFile` behavior.
- **Bridge values** stay UUID-keyed and describe the active profile:
  - `skill:<uuid>` gains `Alchemy:<lvl>,Smithing:<lvl>`.
  - `skill:fn:level` answers `alchemy` and `smithing` through `SkillDefs.indexOf`.
- **Memory-only state is per UUID and is reset on an epoch change** in `Perks.switched(u)`: `Brew.BONUS`, `Brew.SEEN`, the extra-potion chat throttle and the bridge per-minute window.
- The Mana modifier and the duration bonus are recomputed every second from the active profile's level (existing `Perks.tick` flow).
- **Side finding** (VERIFIED from code, not caused by this spec): `snap()` rebuilds the file from `NAMES` only, so any key not in `NAMES` is **dropped on the next save**. The 0.3.1 note says "Old Combat.Berserker XP stays in the file, unread"; in fact it disappears at that player's first save. It is spike data, but the same mechanism is why slot 3 must stay in `NAMES` (section 9).

---

## 9. Slots and rows

### 9.1 Slot table (fixed indices, append-only)

| Slot | File key (`NAMES`) | Label | Status in 0.4 |
|---|---|---|---|
| 0 | Mining | Mining | live |
| 1 | Foraging | Foraging | live |
| 2 | Farming | Farming | live |
| 3 | Combat | Combat (old) | **retired from the UI; storage only** |
| 4 | Acrobatics | Acrobatics | live |
| 5 | Combat.Archer | Archery | live |
| 6 | Combat.Warrior | Swordsmanship | live |
| 7 | Combat.Assassin | Assassination | later (greyed out, class LATER) |
| 8 | Combat.Shaman | Shaman skill | later |
| 9 | Combat.Mage | Sorcery | live |
| **10** | **Alchemy** | Alchemy | **NEW**. Icon `Potion_Health`, color `#7fe0d0` |
| **11** | **Smithing** | Smithing | **NEW**. Icon `Ingredient_Bar_Iron`, color `#c0c8d0` |
| 12+ | reserved | - | next free: Cooking (`research/Cooking-Skill-Spec.md`), then Exploration |

New constants: `N = 12`, `CLASS_END = 10` (= `CLASS0 + CLASSES.length`), `ALCHEMY = 10`, `SMITHING = 11`. Update the build-script assert `len(SLOT_NAMES) == ... == 10` to 12. Both icon ids are VERIFIED in `Assets.zip`; use `must()`.

### 9.2 Retiring slot 3 without breaking saves

- **Keep** index 3 and file key `Combat` forever.
  - `readFile` and `snap` are name-keyed, and `snap` drops unknown keys (section 8).
  - Removing the name would delete any unmigrated legacy Combat XP on the next save.
  - Renumbering would shift every later slot's paid marker, because `data[N + i]` is rebuilt from names, but in-process arrays and `SkillTop.AT` would be off by one.
- **Keep** `SkillStore.moveLegacy` (legacy Combat XP moves to the first class chosen), with its loop bound fixed (9.3).
- **Remove it from the UI:**
  - /skills no longer has a "Combat" row. The class row shows the class weapon skill by name (`SkillClass.skillName`).
  - With no class, the row reads "Class skill - choose a class with /class". If slot 3 still holds XP, a second line says "Old Combat XP (level N) moves to the first class you choose".
- **Aliases stay for compatibility:**
  - `combat` in `/skills top|stats` still means the current class skill (`SkillClass.argSlot`).
  - `skill:fn:level` with `"Combat"` still answers the current class skill (`SkillFn`).
  - `perk.combat.*` keys keep their names; they are the class-skill perks.
- **Bridge string** `skill:<uuid>`: drop the `Combat:<lvl>` entry. The class skill is already appended by name. SkyyMenu parses the string generically (VERIFIED `build_skyymenu_0.1.2.py` `skills()`), so this is safe.
- **Later (0.5+):** only drop `Combat` from `NAMES` after a one-time scan shows no file has `Combat > 0`. Recommendation: never; it costs nothing.

### 9.3 Code pitfalls when slots 10-11 are added (0.3.2 line numbers)

Slots 10-11 are `>= CLASS0` but are **not** classes. These places must use `CLASS_END` instead of `N`, or they misroute Alchemy and Smithing into class code or throw `ArrayIndexOutOfBounds` on `CLASSES[s - CLASS0]`:

| Line | Where | Fix |
|---|---|---|
| 1147-1148 | `SkillClass.weaponOk` | `slot >= CLASS_END` → false |
| 1306 | `SkillStore.levelsString` class loop | `s < CLASS_END`; then append `Alchemy` and `Smithing` explicitly |
| 1368-1369 | `SkillStore.moveLegacy` | Bound both to `CLASS_END`. Otherwise **any Alchemy XP blocks the legacy Combat migration forever** |
| 2828 | `StatsPage.lines` `row = s >= CLASS0 ? COMBAT : s` | Use a perk-row map (9.4) |
| 2854, 2867 | `StatsPage.lines` damage text; `StatsPage.how` | Only for class slots |
| 2910-2911 | `StatsPage.build` "You are not a X right now" note | Only for class slots |

Also:
- `SkillCfg.parseRule` keeps `sk > FARMING → reject`. Block rules cannot pay Alchemy.
- `SkillDefs.indexOf`: `alc` and `smi` prefixes resolve correctly; there is no clash with `sha` or `sor`.

### 9.4 Perk rows

`PerkCfg` arrays are indexed by perk row. Extend `KEYS` to `{"mining","foraging","farming","combat","acrobatics","alchemy","smithing"}` (7 rows) and add a map `PERK_SLOT = {0, 1, 2, COMBAT, 4, 10, 11}`:
- Row 3 = the current class level (existing `Perks.rowLevel`).
- Rows 5 and 6 = the levels of slots 10 and 11.
- **Fix `Perks.rowLevel` (0.3.2 line 1604).** Its fallback today is `return SkillStore.level(u, row);`. That only works because rows 0-2 and 4 happen to equal their slot numbers (VERIFIED, lines 1599-1605). With rows 5 and 6 it would silently read slots 5 and 6 (Archery, Swordsmanship) instead of 10 and 11. Change it to `return SkillStore.level(u, SkillDefs.PERK_SLOT[row]);`. The `row == COMBAT` branch above it stays as it is.
- **Fix `Perks.levels` (line 1619).** It sizes its array with `SkillDefs.ROWS` (5 today). Use `PerkCfg.KEYS.length` (7), so it follows the perk rows, not the /skills rows. `Perks.levels(u)` then returns `int[7]`.
- The other `SkillDefs.ROWS` users (lines 1301 and 2718-2723) are /skills-row loops. They move to `ROW_SLOTS` (section 11). VERIFIED by grep.
- The defaults arrays gain two entries: alchemy `manaPerLevel` 0.2, everything else 0.
- `PerkCfg.read` already reads `perk.<key>.healthPerLevel / staminaPerLevel / manaPerLevel` for every key.
- `doubleDropPerLevel` stays limited to rows 0-2.

---

## 10. Smithing row

### 10.1 What it is now

A normal skill row (slot 11) with the shared curve, level-up coins, Top 10 and a Stats page. No per-level perks yet (`perk.smithing.*` all 0). Its only XP source today is smelting in the SkyySacks Furnace tab, through `craftxp`.

### 10.2 Smelting XP table (base XP per finished unit)

**Draft, replaced by `research/Smithing-Smelting-Spec.md` sections 2.2-2.6** (same key names, plus three). Kept here for reference.

Keyed by output id, `smithing.xp.<id>`. Roughly 2x the Mining ore XP in 0.3.2 (VERIFIED defaults). `[SKYY?]`

| Output (Furnace recipe, VERIFIED) | XP |
|---|---|
| Ingredient_Bar_Copper | 10 |
| Ingredient_Bar_Iron | 16 |
| Ingredient_Bar_Silver | 20 |
| Ingredient_Bar_Gold | 24 |
| Ingredient_Bar_Cobalt | 30 |
| Ingredient_Bar_Thorium | 36 |
| Ingredient_Bar_Mithril | 50 |
| Ingredient_Bar_Adamantite | 60 |
| Ingredient_Bar_Onyxium | 80 |
| Ingredient_Bar_Prisma | 100 |
| Potion_Empty (glass vial from sand) | 4 |
| Every other Furnace recipe (smooth rock, bricks, clay) | `smithing.smeltDefault=1` |

- **Loops (corrected):** no recipe turns a bar straight back into ore, but salvaging bar-made gear does return ore. VERIFIED: 144 recipes in `Server/Item/Recipes/Salvage/` give `Ore_*` or `*Bar_*` outputs; for example `Salvage_Armor_Adamantite_Chest` gives 2 `Ore_Adamantite`. So ore → bar → gear → salvage → ore is possible. Whether it pays depends on bars in versus ore out per item (UNVERIFIED here). `research/Smithing-Smelting-Spec.md` section 2.4 owns this check and the final numbers.
- Pace: 100 iron bars = 1,600 XP, and level 10 is about 620 iron bars. This is deliberately a trickle until reforging and powders arrive.

### 10.3 Placed vanilla Furnace (superseded)

`research/Smithing-Smelting-Spec.md` section 3 now specifies this hook for the same 0.4 build. Use that spec. The notes below are this spec's original draft, kept for reference.

- It fires no craft event, and it runs with no player attached. VERIFIED: `ProcessingBenchBlock.advanceProcessing` / `BenchSystems$ProcessingBenchTick`.
- Candidate hooks, both needing a test build:
  - Watch `ProcessingBenchBlock.getOutputContainer()` with `ItemContainer.registerChangeEvent(Consumer)` (VERIFIED method) while a `ProcessingBenchWindow` is open for a player, found through `WindowManager.getWindows()` as SkyySacks' `CraftLinkTask` does. Credit the items that player removes, using the same table.
  - Or read the player-side ECS `InventoryChangeEvent` (VERIFIED class).
- This draft left it out of 0.4. The Smithing-Smelting spec puts it back in.

### 10.4 What the Stats page says

- **Boosts right now:** "No boosts yet - they arrive with reforging and powders".
- **How to earn XP:** "Earn XP by smelting ore in the Furnace tab of /craft (the placed Furnace later). Reforging and adding powders will level Smithing too when they arrive".

---

## 11. How Alchemy shows up in game

**/skills page.** Inline, same syntax as 0.3.2. No underscores in ids; TextButton + EventData.

- **Row order:** Mining, Foraging, Farming, **Alchemy**, **Smithing**, Acrobatics, class skill. That is 7 rows, driven by a new `ROW_SLOTS = {0, 1, 2, 10, 11, 4, CLASS_ROW}` list instead of `ROWS = 5`.
- **Size:** rows go from 72 to **58 px** (Acrobatics 72 with its bonus line), with 4 px gaps. The root Group height becomes `94 + sum(rowH + 4) + 20` = **562** for 7 rows (624 with a Cooking row).
- **Row contents:**
  - Icon 44x44.
  - Title label 20 px, FontSize 14.
  - Bar 10 px.
  - Progress label 18 px, FontSize 11.
  - Stats button 100x28.
- More than 8 rows (Exploration) needs tabs, "Gathering | Artisan | Combat and movement", using the SkyySacks tab-button pattern.
- **Skill average:** over the rows shown. The class row counts only when there is a class.
- **Footer hint:** "Mine - chop - harvest - brew at the Alchemy Bench - smelt - fight with your class weapons - run jump fall dodge.  Stats shows every boost". No commas or colons.

**Chat.** Existing throttled lines, via `SkillDefs.LABELS`:
- "+850 Alchemy XP (12.3k/20.0k)"
- "SKILL LEVEL UP  Alchemy 11 -> 12   +1200 coins"

**Stats page (Alchemy).** Titled "Alchemy - level L of 100". Every text goes through `b.set("#Id.Text", ...)`. Example at level 25:

| Section | Lines |
|---|---|
| Boosts right now (level 25) | "+25% longer potion effects (Mana potions 7 regen pulses instead of 6 - morphs 75s)"; "+5 max Mana"; "5% chance to brew an extra potion" |
| Level 26 adds | "+1% longer potion effects"; "+0.2 max Mana"; "+0.2% extra potion chance"; "+2600 coins when you reach level 26" |
| How (grey footer) | "Earn XP by brewing at the Alchemy Bench - stronger potions and higher bench tiers pay more (Greater potions pay the most)" |

`StatsPage.lines` computes the pulse counts from the whitelist's base durations: `floor(duration x (1 + bonus) / cooldown)`.

**Commands.** Help and unknown-skill texts add `alchemy` and `smithing`:
- `/skills stats alchemy`
- `/skills top alchemy`
- New admin test helper **`/skills xp <skill> <amount>`**. It targets yourself; uses `requirePermission("skyyskills.admin")` + `setPermissionGroups(new String[0])` (HANDOFF command rules); takes a positional subcommand with `withRequiredArg` x2 (`ArgTypes.STRING`, parsed); and grants through the same path as the bridge with source `admin`, so Skyy can test perks quickly.

**HUD / Menu.** `skill:<uuid>` now carries `Alchemy:<lvl>,Smithing:<lvl>`. SkyyMenu shows it with no change.

---

## 12. xp.properties additions

- The build writes these into `DEFAULTS` for new files.
- `AlchCfg.ensureDefaults(p)` appends the section once to an existing file that has no `alchemy.` key (the `AcroCfg` / `PerkCfg.ensureDefaults` pattern).
- `SkillCfg.load()` calls `AlchCfg.read(p)`, so `/skills reload` covers it.
- Every item and effect id is checked against `Assets.zip` at build time (`must()`, plus a new effect-id check).

```
# ---------- Alchemy + Smithing (SkyySkills 0.4) ----------
# Comments must stay on their own lines.
alchemy.enabled=true
# Base XP per finished craft at the Alchemy Bench (and Alchemybench crafts other Skyy mods report via skill:fn:craftxp),
# keyed by the craft's primary OUTPUT item id. 0 = no XP. Unlisted recipes use alchemy.tierXp by bench tier I..V.
alchemy.xp.Potion_Health_Lesser=50
alchemy.xp.Potion_Signature_Lesser=50
alchemy.xp.Potion_Stamina_Lesser=50
alchemy.xp.Potion_Antidote=80
alchemy.xp.Weapon_Bomb_Popberry=10
alchemy.xp.Potion_Morph_Dog=800
alchemy.xp.Potion_Morph_Frog=800
alchemy.xp.Potion_Morph_Mouse=800
alchemy.xp.Potion_Morph_Pigeon=800
alchemy.xp.Potion_Empty_Small=0
alchemy.xp.Potion_Empty_Large=0
alchemy.xp.Plant_Seeds_Health1=60
alchemy.xp.Plant_Seeds_Mana1=60
alchemy.xp.Plant_Seeds_Stamina1=60
alchemy.xp.Tool_Fertilizer_Crystal=300
alchemy.xp.Potion_Health_Small=850
alchemy.xp.Potion_Signature_Small=850
alchemy.xp.Potion_Stamina_Small=850
alchemy.xp.Potion_Health=8000
alchemy.xp.Potion_Signature=8000
alchemy.xp.Potion_Stamina=8000
alchemy.xp.Plant_Seeds_Health2=300
alchemy.xp.Plant_Seeds_Mana2=300
alchemy.xp.Plant_Seeds_Stamina2=300
alchemy.xp.Potion_Health_Greater=18000
alchemy.xp.Potion_Signature_Greater=18000
alchemy.xp.Potion_Stamina_Greater=18000
alchemy.xp.Plant_Seeds_Health3=1200
alchemy.xp.Plant_Seeds_Mana3=1200
alchemy.xp.Plant_Seeds_Stamina3=1200
alchemy.tierXp=50,850,8000,18000,18000
# Brewer perks - Alchemy level of the player who DRINKS (duration) or BREWS (extra potion)
perk.alchemy.durationPerLevel=0.01
perk.alchemy.durationMax=1.0
perk.alchemy.extend=Potion_Health_Regen,Potion_Health_Regen_Lesser,Potion_Health_Regen_Small,Potion_Health_Regen_Large,Potion_Health_Regen_Greater,Potion_Signature_Regen,Potion_Signature_Regen_Lesser,Potion_Signature_Regen_Small,Potion_Signature_Regen_Large,Potion_Signature_Regen_Greater,Potion_Morph_Dog,Potion_Morph_Frog,Potion_Morph_Mouse,Potion_Morph_Pigeon,Antidote
perk.alchemy.manaPerLevel=0.2
perk.alchemy.extraPotionPerLevel=0.002
perk.alchemy.extraPotionMax=0.25
perk.alchemy.extraPotionOnly=Potion_,Weapon_Bomb_
perk.alchemy.extraPotionNever=Potion_Empty
# Smithing: smelting XP per finished unit (SkyySacks Furnace tab via skill:fn:craftxp). Reforging / powders use skill:fn:addxp later.
# (Draft values. research/Smithing-Smelting-Spec.md section 2.6 replaces the smithing.* lines below.)
smithing.smelt.enabled=true
smithing.xp.Ingredient_Bar_Copper=10
smithing.xp.Ingredient_Bar_Iron=16
smithing.xp.Ingredient_Bar_Silver=20
smithing.xp.Ingredient_Bar_Gold=24
smithing.xp.Ingredient_Bar_Cobalt=30
smithing.xp.Ingredient_Bar_Thorium=36
smithing.xp.Ingredient_Bar_Mithril=50
smithing.xp.Ingredient_Bar_Adamantite=60
smithing.xp.Ingredient_Bar_Onyxium=80
smithing.xp.Ingredient_Bar_Prisma=100
smithing.xp.Potion_Empty=4
smithing.smeltDefault=1
# Cross-mod XP (skill:fn:addxp / skill:fn:craftxp)
bridge.addxp.skills=Alchemy,Smithing
bridge.maxXpPerCall=500000
bridge.maxXpPerMinute=3000000
```

---

## 13. Builder checklist (classes, methods, probes)

**New classes** (add them in dependency order; javassist rules apply: no generics, lambdas, autoboxing, enhanced-for, inner classes or String-switch):

| Class | What it holds |
|---|---|
| `AlchCfg` | config fields; `read`; `ensureDefaults`; `xpFor(outId, tier, recipe)`; `smeltFor(outId)`; `extIdx()` (lazy `getIndex`, re-resolved after reload, logs missing ids once) |
| `RecipeXp` | `classify(CraftingRecipe)` → `long[]{slot, xp}` or null. It loops `getBenchRequirement()`, compares `br[i].id`: `Alchemybench` → ALCHEMY, `Furnace` → SMITHING (only if `smithing.smelt.enabled`) |
| `CraftTask` | Runnable (section 3.1) |
| `CraftSys` | `EntityEventSystem` for `CraftRecipeEvent$Post` |
| `Brew` | `BONUS`, `SEEN`, `tick(...)`, `extraPotion(...)` |
| `BridgeXp` | `offer` / `offerCraft`, per-minute window, grantable list |
| `BridgeTask` | Runnable: key check, creative check, `SkillXp.gain`, extra potion |
| `SkillAddFn`, `SkillCraftFn` | the two bridge `Function`s |
| `XpCmd` | the admin `/skills xp` subcommand |

**Edits:**
- `SkillDefs` (slots, `CLASS_END`, `ALCHEMY`, `SMITHING`, `ROW_SLOTS`, `PERK_SLOT`)
- `PerkCfg` (7 rows)
- `Perks.levels` (size by `PerkCfg.KEYS.length`) / `rowLevel` (read through `PERK_SLOT`, section 9.4), plus `Perks.tick` → sets `Brew.BONUS`
- `Perks.switched` → clears Brew state
- `AcroSys.tick` → `Brew.tick(u, store, cb, ref, dt)` every tick, before the 1 s gate
- `Acro.retainOnline` → prune the Brew maps
- `SkillsPage`, `StatsPage` (`lines`, `how`, class-only guards)
- `SkillStore.levelsString`, `moveLegacy`; `SkillClass.weaponOk`, `argSlot` text
- `SkillCfg.load` → `AlchCfg`
- `setup()` / `shutdown()` → register `CraftSys`, publish and remove both bridge functions
- Manifest text: add Alchemy and Smithing

**Add to the `B.probe` list** (every one VERIFIED to exist today):
- `CraftRecipeEvent` `getCraftedRecipe`, `getQuantity`
- `com.hypixel.hytale.component.system.CancellableEcsEvent` `isCancelled`
- `CraftingRecipe` `getTimeSeconds`, `getPrimaryOutput`, `getBenchRequirement`, `getId`, `getAssetMap`
- `MaterialQuantity` `getItemId`, `getQuantity`
- `EffectControllerComponent` `getActiveEffects`, `addEffect`
- `ActiveEntityEffect` `getRemainingDuration`, `isInfinite`
- `EntityEffect` `getDuration`, `isDebuff`, `getAssetMap`
- `IndexedLookupTableAssetMap` `getAsset`, `getIndex`
- `OverlapBehavior` `EXTEND`
- `EntityStatMap` `putModifier` (already probed)

---

## 14. In-game test checklist for Skyy

Deploy SkyySkills 0.4 with the approved set. Reconnect is enough.

1. **Server log:** "[SkyySkills] 0.4 ready ..." and no "failed" lines.
2. **/skills:** 7 rows (Mining, Foraging, Farming, Alchemy, Smithing, Acrobatics, your class skill such as Archery). There is no "Combat" row. Old levels are unchanged.
3. **One potion:** place an Alchemy Bench in survival and brew **1** Lesser Health Potion from inventory ingredients. About 1 s later: "+50 Alchemy XP".
4. **Batch:** brew **5** in one batch. The total must be **250** XP (5 x 50), not 1,250.
5. **Cancel:** start a batch of 5 and close or cancel after 2 finish. Only those 2 pay.
6. **Bags:** brew with the ingredients only in your magic bags (bag link). XP still arrives.
7. **Vials:** craft small vials. No XP.
8. **Creative:** switch to creative and brew. No XP.
9. **Test level:** `/skills xp alchemy 3100000` gives about level 25. `/skills stats alchemy` shows +25% duration, +5 Mana and a 5% extra chance.
10. **Duration:** drink a Lesser Signature (mana) potion. The status timer should start near 37 s instead of 30 s. Drink it again partway through; the timer goes back to about 37 s and does not stack higher.
11. **Morph:** it lasts about 75 s at level 25.
12. **Mana:** your max Mana goes up by 0.2 per Alchemy level.
13. **Extra potion:** brew about 50 Lesser potions at level 25. You should see about 2-3 "Extra potion!" lines.
14. **Smithing:** SkyySacks Furnace tab, smelt 10 copper ore (needs the SkyySacks build with the bridge call). You get "+100 Smithing XP" as the units finish.
15. **Profiles:** switch profile. Alchemy shows that profile's level, and the potion bonus follows it.
16. **Save:** relog. The XP is still there (`players/<uuid>.properties` has `Alchemy=`).
17. **Leaderboard and Smithing text:** `/skills top alchemy`, and `/skills stats smithing` shows the "reforging and powders later" text.

---

## 15. Open questions for Skyy

Every question below already has a default in section 12, so the build is not blocked. Treat those `alchemy.*`, `perk.alchemy.*` and `smithing.*` defaults as provisional until Skyy answers, and expect one tuning pass after Skyy plays it.

1. **Pace:** is about 27 h to Alchemy 50 and about 250 h to 100 right? One knob scales it: `multiplier` or the `alchemy.xp.*` keys. The Cooking spec (its section 9.1) notes that its defaults make Cooking 50 much slower, so pick one crafting pace for both.
2. **Duration curve:** SkyBlock parity (+1% per level, x2 at 100), or Cooking parity (x4 at 100 → `durationPerLevel=0.03`)?
3. **Health potions:** should their regen get a guaranteed extra pulse at levels 50 and 100? That would mean extending by whole 5 s steps. It would need one more small rule; it is not in this spec.
4. **Extra potion perk:** keep it at 0.2% per level (20% at 100), or turn it off?
5. **Mana per level:** is 0.2 right (+20 at 100)?
6. **Smithing now:** answered. Skyy asked for furnace smelting XP (22:25 log, HANDOFF section 1), so it stays on. `smithing.smelt.enabled=false` is only the off switch. The amounts are in `research/Smithing-Smelting-Spec.md`.

---

## 16. Sources

**Engine and assets** (read-only, via `tools/dev` on `HytaleServer.jar` and Python `zipfile` on `Assets.zip`):
- `SimpleCraftingWindow#handleAction`
- `CraftingManager#tick` / `#craftItem` / `#queueCraft` / `#cancelAllCrafting`
- `EffectControllerComponent#addEffect`
- `ActiveEntityEffect#tick` / `#calculateCyclesToRun`
- Reflected: `CraftingRecipe`, `BenchRequirement`, `EntityEffect`, `OverlapBehavior`, `EntityStatMap`, `ProcessingBenchBlock`, `ProcessingBenchWindow`, `InventoryChangeEvent`
- Assets: `Bench_Alchemy.json`, `Server/Item/Items/**` recipes, `Server/Item/Recipes/Salvage/*`, `Server/Entity/Effects/**`

**Installed mod:** `ZiggfreedCommon-2.0.0.jar` `ZigCraftProducer` (reflect + bytecode).

**Our code:**
- `SkyySkills/build_skyyskills_0.3.2.py`
- `SkyySacks/build_skyysacks_0.7.2.py`
- `SkyyMenu/build_skyymenu_0.1.2.py`
- `tools/PROFILES-CONTRACT.md`
- `HANDOFF.md`, `SkyySkills-Plan.md`, `SkyySacks-Plan.md`
- Live log `Saves/HUD mod/mods/Skyy_SkyySacks/crafts.log`

**Web** (summarized in our own words):
- SkyBlock Alchemy (XP per ingredient, cap 50, +1% duration per level, Intelligence per level, level-50 total): https://hypixelskyblock.minecraft.wiki/w/Alchemy. VERIFIED by fetch on 2026-09-23.
- SkyBlock Potions (most non-vanilla potions unlock at a Collection tier, not an Alchemy level): https://hypixelskyblock.minecraft.wiki/w/Potions. VERIFIED by fetch on 2026-09-23.
- Wynncraft Alchemism (feeds on Farming grain and Fishing oil, more grain than oil; duration and charges scale with level): https://wynncraft.wiki.gg/wiki/Alchemism (ingredients VERIFIED by fetch on 2026-09-23; background only)
- mcMMO Alchemy (Catalysis brew speed, Concoctions ingredient ranks): https://github.com/mcMMO-Dev/mcmmo-wiki-repo/blob/master/skills/alchemy.md (research notes, background only)

**Corrections to the research notes:**
- `PlayerCraftEvent` is not usable for potions (the queued path).
- `CraftingManager.tick` completes queued crafts at **crafting** benches, not the placed Furnace / Tannery (those are `ProcessingBenchBlock` with no craft event).
- There are 30 Alchemy recipes, not 31.
- A 1 s potion recipe is queued at a placed bench; it is not instant.
