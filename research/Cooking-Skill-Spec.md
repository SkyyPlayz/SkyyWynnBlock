# Cooking skill: build spec (SkyySkills 0.4, next to Alchemy)

*Written 2026-09-23 by the research workflow `skywynn-cooking-research` (writer). Research only: no build script, mod folder or game file was changed.*
*Revised 2026-09-23 (verifier fix pass): merged `CraftSys` handler written out (3.1), rate-cap call site (6.4), strength/duration exponents in the scaling rules (4.1), Grade clamp (8.6), Cooking tree marked pending Skyy's OK (7), pie-chain XP 118, sources tightened (15).*
*Builds on SkyySkills 0.3.2 (`SkyySkills/build_skyyskills_0.3.2.py`, per-profile storage) and is written to land in the same **0.4** patch as `research/Alchemy-Skill-Spec.md` (new `tools/skills_0_4_patch.py`; edit the patch, not the generated script). The tree part follows `research/Skill-Trees-Spec.md` (SkyyTrees template). Owner: Skyy (they/them).*

**Legend.** VERIFIED = seen in `HytaleServer.jar` bytecode or reflection (tools/dev), in `Assets.zip`, in an installed mod jar, in our own build scripts, or in a cited web source. UNVERIFIED = design, estimate, inference, or not yet tested in game. `[SKYY?]` = a number or choice Skyy should confirm.

**Skyy's call (2026-09-23, HANDOFF log 22:30):** build Cooking next to Alchemy *if* cooking level can raise the strength and duration of the food you cook: x2 at level 50, x4 at level 100, and skill-tree modifiers make it even better. Later the same night (22:45): Cooking is **table use only** (Cooking Bench accessory removed; the vanilla bench draws from your sacks).

---

## 0. Feasibility verdict (plain words)

**Yes, it can be built, with one design choice: a dish carries a "Grade" (0 to 12) instead of an exact number.** Your Cooking level sets the Grade (one Grade per 10 levels), and the Grade multiplies both the strength and the duration of everything the dish does: x1 at level 0, **x2 at level 50, x4 at level 100** exactly. Skill-tree nodes push dishes to Grade 11 and 12 (x4.59 and x5.28); the engine allows that part too, but the Cooking tree itself waits for Skyy's OK on a 4th SkyyTrees tree (section 7).

| Skyy's condition | Can it be done? | Verified mechanism |
|---|---|---|
| Food remembers the cook's power | **Yes** | At the vanilla Cooking Bench every finished dish fires `CraftRecipeEvent$Post` on the cook's own entity, before the engine hands out the item, and the event is cancellable (VERIFIED bytecode, both the instant and the timed-queue path). SkyySkills cancels it and hands out the **graded item** instead (e.g. `Skyy_Cook_Food_Pie_Meat_G5`), exactly the way the engine would have handed out the plain one. The Grade lives in the item id, so it survives chests, trades, drops, relogs and Magic Bags. |
| Eating scales **strength** | **Yes** | A graded dish is a normal food item whose eat chain points at **pre-scaled effect assets** (heal %, regen per tick, max-Health / max-Stamina bonus, damage resistance all x the Grade multiplier). Vanilla `ApplyEffectInteraction` looks the effect up by id and applies its own numbers (VERIFIED bytecode), so no runtime trick is needed. |
| Eating scales **duration** | **Yes** | The same assets carry `Duration` x the multiplier (45 s buff becomes 90 s at Grade 5, 180 s at Grade 10). |
| Instant heals scale | **Yes, in amount** | Instant heals are 0.1 s effects (`Food_Instant_Heal_T1/T2/T3/Bread`, +5/10/15/15% max Health, VERIFIED). Their amount scales (15% becomes 60% at Grade 10). They have no duration to extend, and we never touch their 0.1 s duration. |
| Skill-tree modifiers push it further | **Yes (engine)**, scope pending | Tree nodes add Grades (a guaranteed +1 from the capstone, chances of +1/+2), extra dishes, ingredient refunds and XP. All hooks run in our own craft code (VERIFIED event). The engine allows it; what is still open is scope: the Cooking tree would be a 4th SkyyTrees tree, and the trees spec ships only the 3 gathering trees. It is not built until Skyy says yes (section 7, question 5). Cooking works on levels alone until then. |

**What cannot be done, and the closest workable alternative:**

1. **Scaling a vanilla food effect per bite at runtime** is impossible: `EffectControllerComponent.addEffect` has a duration override but **no strength/magnitude argument**, and `EntityEffect` is an immutable asset (VERIFIED reflection). → We pre-build 12 scaled copies of each food effect (the "Grade" assets).
2. **A placed Campfire cannot know who cooked.** It is a Processing bench: `ProcessingBenchBlock` has no owner field and completes recipes with no event (VERIFIED). → Campfire food stays Grade 0 and pays no XP; the 3 campfire dishes (cooked meat, grilled fish, cooked vegetables) get **Cooking Bench recipes** (vanilla "Variant recipe" pattern) so a leveled cook can grade them.
3. **An exact per-level number on every dish** would stop food from stacking and would need unlimited assets. → 12 Grades, one per 10 levels (the curve `2^(level/50)` sampled every 10 levels).
4. **Separate "+% strength only" or "+% duration only" tree nodes** would need a second Grade axis (12 x 12 variants per dish). → Tree nodes raise the Grade, which raises both together. A duration-only node is possible later only through the runtime fallback (section 11).
5. **Vanilla food eaten while a Cook buff runs** can run its own vanilla buff of the same family next to the Cook buff, because vanilla's tier checks do not know our ids and overriding vanilla assets is UNVERIFIED. → Documented limit; worst case is one extra vanilla-strength buff (section 5.4).
6. **Faster cooking per player** is impossible: bench speed comes from the bench's tier asset (`CraftingTimeReductionModifier`), not from the player (VERIFIED, Alchemy spec 5.4). The Cooking Bench has no tiers at all (VERIFIED).

---

## 1. How it plays (one paragraph)

You cook at a placed vanilla **Cooking Bench**; its ingredients can come from your Magic Bags (the existing SkyySacks bench link). Each finished dish earns Cooking XP. From Cooking 10 on, dishes come out graded: "Meat Pie (Grade 5)" heals twice as much and its buffs are twice as strong and last twice as long. Anyone who eats it gets that power (the eater's own level does not matter). Food of the same Grade stacks. If Skyy approves it, Cooking also gets its own small skill tree on the SkyyTrees template that raises Grades further (section 7).

---

## 2. The power curve and Grades

### 2.1 Formula (recommended: exponential, sampled every 10 levels)

- **Grade** `g = floor(CookingLevel / 10)` + tree bonuses, capped at `12`.
- **Multiplier** `M(g) = 2^(g/5)` (strength and duration both).
- This is exactly `2^(level/50)` read at levels 0, 10, 20 ... 100, so it hits Skyy's anchors: level 50 → Grade 5 → **x2.00**, level 100 → Grade 10 → **x4.00** (VERIFIED arithmetic).

**Why `2^(level/50)` and not piecewise-linear** (`1 + L/50` to 50, then `2 + (L-50)/25`):
- One formula hits both anchors with no kink. Piecewise-linear doubles its slope at level 50.
- Every step is the same relative gain (+14.9% per Grade), so each new Grade feels the same size.
- Tree bonuses compose cleanly: one more Grade is always another x1.149, at any level.
- Cost: early levels give a bit less than linear (level 30: x1.52 instead of x1.60). That is acceptable for a skill whose headline numbers are at 50 and 100.

**Why Grades every 10 levels** (not smaller steps): 12 steps keep the asset count sane (section 4), give a simple rule players can remember ("a new Grade every 10 Cooking levels"), and keep food from cooks in the same 10-level band identical, so it stacks and trades as one item.

### 2.2 Grade table (VERIFIED arithmetic)

| Grade | Reached at | Multiplier | Name suffix | Rarity colour (never below the dish's own) |
|---|---|---|---|---|
| 0 | Cooking 0-9 | x1.00 | (plain vanilla item) | vanilla |
| 1 | 10 | x1.15 | (Grade 1) | Uncommon |
| 2 | 20 | x1.32 | (Grade 2) | Uncommon |
| 3 | 30 | x1.52 | (Grade 3) | Rare |
| 4 | 40 | x1.74 | (Grade 4) | Rare |
| 5 | **50** | **x2.00** | (Grade 5) | Rare |
| 6 | 60 | x2.30 | (Grade 6) | Epic |
| 7 | 70 | x2.64 | (Grade 7) | Epic |
| 8 | 80 | x3.03 | (Grade 8) | Epic |
| 9 | 90 | x3.48 | (Grade 9) | Legendary |
| 10 | **100** | **x4.00** | (Grade 10) | Legendary |
| 11 | tree only | x4.59 | (Grade 11) | Legendary |
| 12 | tree only (cap) | x5.28 | (Grade 12) | Legendary |

Rarity names Common..Legendary are the vanilla `Server/Item/Qualities` ids SkyyAccessories already uses (VERIFIED). The colour mapping is a suggestion `[SKYY?]`.

### 2.3 How the power is shown

- **On the item (native tooltip):** the graded item has its own name and description through `Server/Languages/en-US/server.lang` in the SkyySkills jar, the same way SkyyAccessories, SkyySacks and SkyyMenu name their items (VERIFIED: all three ship their own `server.lang` and are live together). Example:
  - Name: `Meat Pie (Grade 5)`
  - Description: `Grade 5 food, cooked at Cooking 50 or higher. Heal and buffs x2.00 stronger, buffs last x2.00 longer.` followed by the vanilla description text (read from the vanilla `server.lang` at build time, as SkyyAccessories' `vname()` does, VERIFIED).
- **On the Stats page** (section 8.4): your current Grade, its multiplier, the level of the next Grade, and your tree chances.
- **Not used:** per-stack `ItemDisplay` metadata. It exists (`ItemDisplayMetadata`, key `ItemDisplay`, read by `ItemStack.getDisplayName()`; the client binary knows the key; VERIFIED), but graded ids make it unnecessary. It is the display path of the fallback in section 11.

---

## 3. Stamping the power on food

### 3.1 Vanilla Cooking Bench (primary path, VERIFIED hook)

Engine facts (VERIFIED bytecode via `tools/dev/bc.py` / `bcfull.py`, matching Alchemy spec 3.1):
- `Bench_Cooking` = bench id `Cookingbench`, `Bench.Type: Crafting`, no tier levels. `Bench_Campfire` = `Campfire`, `Processing` (VERIFIED Assets.zip).
- A Crafting bench opens `SimpleCraftingWindow`. Every vanilla cooking recipe has `TimeSeconds` 1, 2 or 5, so it takes the **queued** path: `queueCraft` fires `Pre`; later `CraftingManager.tick` removes one unit's inputs, fires `new CraftRecipeEvent$Post(job.recipe, job.quantity)` on the player's `Ref`, and **if not cancelled** calls `giveOutput(ref, accessor, job, 1)`, which gives **one unit** (`iconst_1`).
  - So: one `Post` per finished dish, but `getQuantity()` is the whole batch size. **Count 1 unit per `Post` when `TimeSeconds > 0`** (same rule as Alchemy).
- The instant path (`craftItem`, `TimeSeconds <= 0`) fires `Post(recipe, qty)` once, then `giveOutput(ref, accessor, recipe, qty)`, then `PlayerCraftEvent`.
- Events are dispatched synchronously: `CommandBuffer.invoke(Ref, EcsEvent)` calls `Store.internal_invoke` right away (VERIFIED), so a cancel set in our handler is seen by the engine's `isCancelled()` check that follows.
- Vanilla `giveOutput` = `getOutputItemStacks(recipe, n)` → for each stack `InventoryUtils.getContainerForItemPickup(ref, item, playerSettings, accessor)` → `SimpleItemContainer.addOrDropItemStack(accessor, ref, container, stack)` (VERIFIED). `CommandBuffer` implements `ComponentAccessor` (VERIFIED).
- Creative mode skips input removal (VERIFIED, Alchemy spec 3.1).
- Precedents: Aetherhaven's `GaiaDraughtCraftSystem` handles `CraftRecipeEvent$Post` to give crafted potions per-stack data; EndgameAndQoL and SimpleEnchantments cancel `CraftRecipeEvent$Pre` (all VERIFIED constant pools).

**Hook: the shared `CraftSys` from the Alchemy spec** (one `EntityEventSystem` for `CraftRecipeEvent$Post`; one system class, never registered twice). `RecipeXp.classify(rc)` gains Cookingbench/Campfire → `COOKING` (section 6). For a Cooking recipe, CraftSys does the grading **synchronously in the handler** (it must cancel before the engine's `isCancelled()` check), then queues the XP award exactly like Alchemy.

**The merged handler, written once.** This is the whole `CraftSys.handle` body for the 0.4 patch: the Alchemy spec 3.1 body with the Cooking branch added. The Alchemy spec has no merged version; this one is the reference for both specs. The variables `idx`, `chunk`, `st` (Store), `buf` (CommandBuffer) and `ev` are the parameters of the existing `event_system()` helper (VERIFIED, `build_skyyskills_0.3.2.py` ~line 2535). Simple class names stand for the build script's constants (`PR`, `PLA`, `EST`, `WLD`, ...).

```java
CraftRecipeEvent$Post e = (CraftRecipeEvent$Post) ev;
CraftingRecipe rc = e.getCraftedRecipe();
if (rc == null) return;
long[] rule = RecipeXp.classify(rc);                        // {slot, base xp per craft} or null; Cookingbench/Campfire -> COOKING (null when cook.enabled=false)
if (rule == null) return;
Ref r = chunk.getReferenceTo(idx);
if (r == null) return;
PlayerRef pr = (PlayerRef) st.getComponent(r, PlayerRef.getComponentType());
if (pr == null || SkillXp.creative(st, r)) return;          // Alchemy's creative exit, UNCHANGED and still FIRST: creative gets vanilla output, no Grade, no XP
Object ext = st.getExternalData();
if (!(ext instanceof EntityStore)) return;
World w = ((EntityStore) ext).getWorld();
if (w == null) return;
int units = rc.getTimeSeconds() > 0.0f ? 1 : Math.max(1, e.getQuantity());   // queued path: 1 unit per Post
java.util.UUID u = pr.getUuid();
boolean gave = false;
if (rule[0] == SkillDefs.COOKING) {                         // --- Cooking branch (new) ---
  if (e.isCancelled()) return;                              // another system took over this craft: no Grade, no XP
  Player p = (Player) st.getComponent(r, Player.getComponentType());
  java.util.List plan = p == null ? null : Cook.plan(u, rc, units);   // graded stacks + extras + refunds (sections 3.5, 7), or null = vanilla output
  if (plan != null) {
    e.setCancelled(true);                                   // engine skips giveOutput (and PlayerCraftEvent on the instant path)
    for (int i = 0; i < plan.size(); i++) {
      ItemStack s = (ItemStack) plan.get(i);
      ItemContainer c = InventoryUtils.getContainerForItemPickup(r, s.getItem(), Cook.settings(buf, r), buf);  // mirror vanilla giveOutput
      if (c == null) c = p.getInventory().getCombinedStorageHotbarBackpack();                                  // SkyySacks 0.6.5 lesson
      SimpleItemContainer.addOrDropItemStack(buf, r, c, s);
    }
    gave = true;
  }
}
w.execute(new CraftTask(e, u, w.getName(), rc, rule, units, SkillStore.pkey(u), gave));   // Alchemy's CraftTask + one flag
```

- **Where `creative` comes from:** there is no `creative` variable. `SkillXp.creative(st, r)` is the only creative test (VERIFIED `build_skyyskills_0.3.2.py` line 1549: it reads the `Player` component's game mode and returns false when `creativeXp=true`). It stays in the early return, ahead of the Cooking branch, so a creative craft never reaches grading and never queues a `CraftTask`. Do **not** loosen that early return for Cooking. With the default `creativeXp=false`, creative = vanilla output, no Grade, no XP (6.4 item 1). If an admin sets `creativeXp=true`, creative crafts get both Grade and XP, on purpose, since that switch means "treat creative like survival".
- `Player p` is read only to find the fallback container. When it is missing (never expected on a player entity) the plan is skipped and vanilla gives the plain dish, so a cancel can never lose items.
- Signatures used above: `InventoryUtils.getContainerForItemPickup(Ref, Item, PlayerSettings, ComponentAccessor)` and `ItemStack.getItem()` (VERIFIED `reflect.py`), `getCombinedStorageHotbarBackpack()` (VERIFIED, used by `build_skyysacks_0.7.2.py` line 1843).

**The merged `CraftTask.run()`** (world thread, after every other system has seen the event; Alchemy spec 3.1 steps plus two Cooking lines):
1. `if (ev.isCancelled() && !this.cookGave) return;` Our own cancel does not drop the XP; anyone else's cancel still does.
2. `PlayerRef pr = Universe.get().getPlayer(u)`. Stop if it is null or `!pr.isValid()`.
3. `if (!key.equals(SkillStore.pkey(u))) return;` (profile switched: no XP; the graded dish was already handed out by the handler, which is correct because the ingredients were really spent).
4. **Cooking only:** `long base = rule[1] * units;` `if (rule[0] == SkillDefs.COOKING && !Cook.allowXp(u, base)) return;` This is the rate cap of 6.4 item 7.
5. `SkillXp.gain(pr, (int) rule[0], SkillCfg.scaled(amount))`, where `amount = base` for Alchemy and `Math.round(base * CookCfg.XP_MULT)` (`cook.xpMultiplier`) for Cooking.
6. If `rule[0] == SkillDefs.ALCHEMY`: `Brew.extraPotion(...)` (Alchemy spec 5.3), unchanged.

- `Cook.settings(buf, r)` reads `PlayerSettings` the way vanilla does (`PlayerSettings.getComponentType()`, falling back to `PlayerSettings.defaults()`, VERIFIED calls in `giveOutput`). If that proves awkward, the storage-first container alone is fine.
- `Cook.plan` returns **null** (let vanilla give the plain item) when the recipe makes no gradable dish, or when every unit rolls Grade 0 and no batch extra or refund triggers. So Grade-0 cooks never go through the replacement path.
- Giving with the handler's `CommandBuffer` mirrors vanilla, which gives queued output through the crafting ticker's accessor at the same moment (VERIFIED signatures). UNVERIFIED in game: the first test build confirms the dish lands in the inventory; fallback = give the same stacks from a `world.execute` task with `Store` (the SkyySkills 0.3 double-drop path, VERIFIED shipped).

### 3.2 Placed Campfire (Processing bench)

- Not attributable (VERIFIED: `ProcessingBenchBlock` has no owner field, `advanceProcessing` fires no event). Campfire food stays **Grade 0**, and the placed Campfire pays **no Cooking XP**.
- **Workaround (build now):** three recipe-variant items add the campfire dishes to the Cooking Bench, copying the vanilla pattern `Server/Item/Items/Ingredient/Life Essence Recipes/*.json` (`"Variant": true`, a `Parent`, and a `Recipe` whose `Output` is another existing item; VERIFIED in Assets.zip):

| Recipe item (never obtained) | Output | Inputs | Bench / category | Time |
|---|---|---|---|---|
| `Skyy_Cook_Recipe_Wildmeat` | `Food_Wildmeat_Cooked` x1 | ResourceType `Meats` x1, ResourceType `Fuel` x1 | Cookingbench / Prepared | 2 s |
| `Skyy_Cook_Recipe_Fish` | `Food_Fish_Grilled` x1 | `Food_Fish_Raw` x1, `Fuel` x1 | Cookingbench / Prepared | 2 s |
| `Skyy_Cook_Recipe_Vegetable` | `Food_Vegetable_Cooked` x1 | ResourceType `Vegetables` x1, `Fuel` x1 | Cookingbench / Prepared | 2 s |

  Inputs mirror the Campfire recipes (VERIFIED) plus 1 Fuel `[SKYY?]`. The output is the vanilla item, and CraftSys grades it like any dish. UNVERIFIED: a mod-shipped Variant recipe item loads like vanilla's (SkyyAccessories' mod items with recipes load, VERIFIED in game; the Variant flag is the new part).
- **Later option (UNVERIFIED hook, shared with Smithing's placed-Furnace XP, Alchemy spec 10.3):** "the collector is the cook". While a player has a `ProcessingBenchWindow` open on a Campfire, watch the player's `InventoryChangeEvent`; a `MoveTransaction` whose `getOtherContainer()` is that bench's output container moved cooked food into the player (all classes and methods VERIFIED by reflection). Replace those stacks with graded ones and pay XP. Decide this once for Furnace and Campfire.

### 3.3 SkyySacks /craft (the Crafting tab)

- Per Skyy's 22:45 call, **cooking recipes leave /craft** (SkyySacks-Plan.md "table-only"). SkyySacks crafts by its own counted removal and gives `new ItemStack(outId, total)` itself; it never calls `CraftingManager`, so no engine event sees its crafts (VERIFIED `build_skyysacks_0.7.2.py` ~line 2389-2459).
- **Open point `[SKYY?]`:** does the **Campfire** bench accessory (still listed in the merged Crafting tab, HANDOFF section 5) count as "cooking recipes"? Recommendation: yes, remove its recipes from /craft too (the placed Campfire and the new Cooking Bench recipes cover them).
- **If any cooking recipe stays in /craft**, SkyySacks needs two calls (for its next build; nothing is edited here):
  1. XP: it already calls the Alchemy spec's **`skill:fn:craftxp`** for every tab; `RecipeXp.classify` routes Cookingbench/Campfire recipes to Cooking. Nothing extra.
  2. Items: replace its output loop for that craft with the list from **`cook:fn:out`** (section 8.2), which returns the graded stacks plus batch extras. It awards no XP, so there is no double count.

### 3.4 After cooking: trades, chests, bags, bazaar

| Situation | Result |
|---|---|
| Someone else eats your dish | They get **your** Grade's effects. The eater's Cooking level never matters. |
| Traded, dropped, put in a chest, relog | The Grade is part of the item id, so nothing can strip it (no metadata involved). |
| Magic Bags (SkyySacks pool) | **The pool does not keep metadata** (VERIFIED: `itemId=count` only; `catOf` goes by id prefix; withdraw builds `new ItemStack(id, qty)`). Graded ids survive it unchanged. Today `catOf` sends `Food_*` to the Farming bag but returns null for `Skyy_*`, so graded dishes stay in the inventory. **SkyySacks change (recommended):** `catOf`: `Skyy_Cook_Food_` → `"Farming"` (keep `Skyy_Cook_Recipe_` out). |
| Bazaar | Graded ids are not commodities. Skyy can list any Grade later in `products.properties` (ids are checked against the live asset map, VERIFIED SkyyBazaar 0.1.1 notes). |
| How Grades show in bag pages and listings (decided, not an oversight) | Each Grade is its own row, because each Grade is a different item with different power and they do not stack. No grouping is needed for the first build. The Farming bag page sorts rows by count, then by id (VERIFIED `CountCmp`, `build_skyysacks_0.7.2.py` ~line 1012), so Grades of one dish are not always next to each other, and the per-item bag cap (640 / 2,240 / 20,160) applies to each Grade separately. Optional polish for the SkyySacks owner later: sort `cook:prefix` rows by dish, then Grade. For the Bazaar, list at most a few Grades (for example 5 and 10) rather than all 12 per dish `[SKYY?]`. |
| Death | `DropOnDeath: true` is copied from the vanilla dish. |
| Loot, NPC merchants, prefab chests | Vanilla ids, so Grade 0 (Assets.zip drops and barter shops reference the plain ids, VERIFIED). |
| Animals or NPCs that want a vanilla dish (e.g. NPC roles listing `Food_Kebab_Meat`) | A graded copy is a different id and is not accepted. Minor. |

### 3.5 Which items get Grades

**Graded (15 dishes, VERIFIED recipes and effect chains in Assets.zip):**

| Dish | Eat tier / charge | Effects (vanilla) | Bench |
|---|---|---|---|
| `Food_Wildmeat_Cooked`, `Food_Fish_Grilled` | T1 / 2.0 s | Instant Heal T1 + HealthRegen T1 + Meat T1 | Campfire (+ new Cooking Bench recipe) |
| `Food_Vegetable_Cooked` | T1 | Instant Heal T1 + HealthRegen T1 + FruitVeggie T1 | Campfire (+ new recipe) |
| `Food_Bread` | T2 / 2.5 s | Instant Heal Bread (15%) | Cookingbench, Baked, 5 s |
| `Food_Kebab_Meat` | T2 | Heal T2 + HealthRegen T2 + Meat T2 | Prepared, 1 s |
| `Food_Kebab_Fruit`, `_Mushroom`, `_Vegetable`, `Food_Salad_Berry`, `Food_Salad_Mushroom` | T2 | Heal T2 + HealthRegen T2 + FruitVeggie T2 | Prepared, 1 s |
| `Food_Popcorn` | T3 / 3.0 s | Heal T3 | Baked, 5 s |
| `Food_Pie_Meat` | T3 | Heal T3 + HealthRegen T3 + Meat T3 | Baked, 5 s, recipe knowledge |
| `Food_Pie_Apple`, `Food_Pie_Pumpkin`, `Food_Salad_Caesar` | T3 | Heal T3 + HealthRegen T3 + FruitVeggie T3 | Baked 5 s / Prepared 1 s, knowledge |

**Not graded:**
- `Food_Cheese`: it is an input **by item id** for Caesar Salad and `Potion_Morph_Mouse` (VERIFIED), so a graded copy would break both recipes. `[SKYY?]` (alternative: grade it and accept that graded cheese cannot be used as an ingredient).
- `Food_Fish_Raw` (filleting `Fish` / `Fish_Uncommon..Legendary` resources) and the ingredients `Ingredient_Flour`, `_Dough`, `_Salt`, `_Spices`: raw or not food. They still pay XP.
- Correction to the research notes: vanilla cooking already matters a little. Raw meat and raw fish give only the T1 instant heal; the campfire versions add HealthRegen T1 and a Meat/FruitVeggie T1 buff (VERIFIED item JSON).

---

## 4. Generated assets (asset pack inside the SkyySkills jar)

The build script generates everything from `Assets.zip` (read in memory, like SkyyAccessories 0.4.1 does) and passes it to `B.assemble(..., extra_files=...)`; `B.manifest` already sets `IncludesAssetPack: true` for every Skyy mod (VERIFIED `tools/skyybuild.py` lines 61-95). Precedents that mod packs can ship these asset kinds: `More Foods.zip` ships food items with `"Parent": "Template_Food"` and its own `InteractionVars.Effect` plus two custom food effects; NotEnoughPotions ships 34 effects; 20+ installed mods ship `Server/Item/Interactions` JSON (all VERIFIED file listings). **UNVERIFIED in our toolchain:** effects and interactions (only items and lang are proven). This is the first in-game test (section 13, step 1).

### 4.1 Effects: `Server/Entity/Effects/SkyyCook/Skyy_Cook_<BaseEffect>_G<g>.json`

13 base effects x Grades 1-12 = **156 files**. Bases (all VERIFIED values):

| Base | Vanilla numbers |
|---|---|
| `Food_Instant_Heal_T1` / `_T2` / `_T3` / `_Bread` | `StatModifiers.Health` 5 / 10 / 15 / 15, `ValueType: Percent`, Duration 0.1, cooldown 0 |
| `HealthRegen_Buff_T1` / `_T2` / `_T3` | Health +1 / 1.5 / 2 % every 2 s, for 45 / 150 / 360 s |
| `Meat_Buff_T1` / `_T2` / `_T3` | max Health x1.05 / 1.10 / 1.15 (Multiplicative, Max) for 45 / 150 / 360 s; T3 also 5% Physical and Projectile resistance |
| `FruitVeggie_Buff_T1` / `_T2` / `_T3` | max Stamina x1.10 / 1.20 / 1.30 for 45 / 150 / 360 s; T2/T3 also +0.025 / 0.05 Stamina every 0.1 s |

**Scaling rules** (copy the base JSON, then change only these fields). `M = 2^(g/5)`; the two build-time exponents `a` and `b` (knobs below, both 1.0 by default) turn it into a **strength factor `S = M^a`** and a **duration factor `D = M^b`**. With the defaults `S = D = M`.
- **Strength fields use `S`:**
  - `StatModifiers.<stat>` → value x S.
  - `RawStatModifiers.<stat>[].Amount` with `CalculationType: Multiplicative` → `1 + (Amount - 1) x S` (the bonus part scales, so x1.15 becomes x1.60 at Grade 10 with a = 1). Additive → Amount x S.
  - `DamageResistance.<type>[].Amount` → Amount x S.
- **The duration field uses `D`:** `Duration` → x D **only if the base Duration is above 0.5 s**. Instant effects keep 0.1 s. Reason: a cooldown-0 effect applies once whatever its duration (VERIFIED pulse rule, Alchemy spec section 2), so there is nothing to gain and it avoids surprises.
- No other field uses either factor. `DamageCalculatorCooldown`, `ValueType`, `OverlapBehavior` (Overwrite), `StatusEffectIcon`: unchanged.
- **Safety caps** (applied after scaling; never reached at or below Grade 10 with a = b = 1): instant heal ≤ 100%, regen ≤ 12% per tick, max-stat bonus ≤ +150%, resistance ≤ 50%, Duration ≤ 2400 s. At Grade 12 only FruitVeggie T3's stamina bonus is clipped (+158% → +150%).
- **Balance knobs (build time):** `COOK_STRENGTH_EXP = 1.0` (a), `COOK_DURATION_EXP = 1.0` (b). Skyy asked for x4 strength **and** x4 duration, which makes the total healing of a regen buff x16 at level 100. If that is too much, `a = b = 0.5` gives x2 x x2 = x4 total. `[SKYY?]` These numbers are baked into the assets, so a change means a rebuild; everything else in this spec is a runtime key.
- **Text follows the factors:** the item description (2.3) and the Stats page (8.4) print S ("x.. stronger") and D ("last x.. longer") from the same build-time constants, not M, so they stay true if a or b changes. The build-time check 4.5.1 stays on M (`M(5) == 2.0`, `M(10) == 4.0`); add `S` and `D` to the generator's printed summary.

What players get with the default a = b = 1 (VERIFIED arithmetic):

| Effect | Grade 0 (vanilla) | Grade 5 (level 50) | Grade 10 (level 100) | Grade 12 (tree cap) |
|---|---|---|---|---|
| Instant heal T1 / T2 / T3 | 5 / 10 / 15 % | 10 / 20 / 30 % | 20 / 40 / 60 % | 26 / 53 / 79 % |
| HealthRegen T1 | 1 %/2 s, 45 s | 2 %, 90 s | 4 %, 180 s | 5.3 %, 238 s |
| HealthRegen T2 | 1.5 %, 150 s | 3 %, 300 s | 6 %, 600 s | 7.9 %, 792 s |
| HealthRegen T3 | 2 %, 360 s | 4 %, 720 s | 8 %, 1440 s (24 min) | 10.6 %, 1900 s |
| Meat T3 | max HP +15 %, resist 5 %, 360 s | +30 %, 10 %, 720 s | +60 %, 20 %, 1440 s | +79 %, 26 %, 1900 s |
| FruitVeggie T3 | max Stamina +30 %, 360 s | +60 %, 720 s | +120 %, 1440 s | +150 % (cap), 1900 s |

### 4.2 Family checks: `Server/Item/Interactions/SkyyCook/Skyy_Cook_<Family>_Check_T<t>_G<g>.json`

3 families (HealthRegen, Meat, FruitVeggie) x 3 tiers x Grades 1-12 = **108 files**. They replace vanilla's `<Family>_TierCheck_T<t>` for graded dishes and keep vanilla's rule ("a weaker buff never replaces a stronger one", VERIFIED: `Meat_TierCheck_T2` = `EffectCondition` on `Meat_Buff_T3`, `Match: None`, then `ClearEntityEffect` T1 + `ApplyEffect` T2).

- **Rank** of a family member = (strength value, then duration). Members = the 3 vanilla buffs (Grade 0) + the 36 graded ones. Ties in strength exist (HealthRegen T1 Grade 5 = T3 Grade 0 = 2%/tick) and are broken by duration.
- Generated JSON for member X:
  ```json
  { "Type": "EffectCondition", "EntityEffectIds": [ "<every member ranked above X>" ], "Match": "None",
    "Next": { "Type": "Serial", "Interactions": [
        { "Type": "ClearEntityEffect", "EntityEffectId": "<each member ranked below X>" },
        { "Type": "ApplyEffect", "EffectId": "Skyy_Cook_<Family>_Buff_T<t>_G<g>" } ] },
    "Failed": { "Type": "Simple", "RunTime": 0 } }
  ```
  The top member of each family (T3 Grade 12) has nothing above it: generate the `Serial` alone, no condition.
- All four interaction types are vanilla (`EffectCondition`, `Serial`, `ClearEntityEffect`, `ApplyEffect`, VERIFIED in Assets.zip), so no custom Java interaction is needed.

### 4.3 Graded dishes: `Server/Item/Items/SkyyCook/Skyy_Cook_<Dish>_G<g>.json`

15 dishes x 12 Grades = **180 files**. Built exactly like the vanilla dish, which itself is `Parent: Template_Food` plus its own keys (VERIFIED: e.g. `Food_Kebab_Meat` own keys = BlockType, DropOnDeath, Icon, InteractionVars, Interactions, ItemLevel, MaxStack, Parent, PlayerAnimationsId, Quality, Recipe, TranslationProperties):
- `"Parent": "Template_Food"` and a copy of **every own key of the vanilla dish except `Recipe`**, so model, icon, eat tier (`Interactions.Secondary`), eat animation, particles and sounds are identical.
- **Never** `Parent: <vanilla dish>`: that dish's recipe could be inherited, and for dishes with no explicit `Output` (e.g. `Food_Pie_Meat`) the recipe would then craft the graded item directly. Build-time assert: no generated dish has a `Recipe`.
- `TranslationProperties`: `server.items.Skyy_Cook_<Dish>_G<g>.name` / `.description`.
- `Quality`: from the table in 2.2.
- `InteractionVars.Effect.Interactions`: `{ "Type": "ApplyEffect", "EffectId": "Skyy_Cook_Food_Instant_Heal_<T>_G<g>" }` then the dish's family checks `"Skyy_Cook_<Family>_Check_T<t>_G<g>"` in the vanilla order. `Consume_Charge` and the SFX vars stay as copied.
- Lang: `items.<id>.name` and `server.items.<id>.name` (+ `.description`), both forms, as SkyyAccessories writes them (VERIFIED).
- Optional: `"Variant": true` to keep 180 items out of the creative item list. What that flag does is UNVERIFIED; test before relying on it.

### 4.4 Recipe variants

The 3 items of section 3.2 (`Skyy_Cook_Recipe_*`). Total generated: 156 + 108 + 180 + 3 = **447 JSON files**, plus about 730 lang lines. Icons and models are vanilla, so no new textures.

### 4.5 Build-time checks (the build fails if one is false)

1. `M(5) == 2.0` and `M(10) == 4.0`.
2. Every effect / interaction id referenced by a generated file exists among the generated files or in Assets.zip.
3. No generated dish has a `Recipe`; each recipe variant's `Output` is one of the 15 dishes.
4. The 15 dish ids, their eat chains and the 13 base effects still look as this spec expects (a Hytale update that changes them stops the build instead of shipping wrong numbers).
5. No generated id collides with a vanilla id (all start with `Skyy_Cook_`).

---

## 5. Eating

### 5.1 The hook

**No Java.** A graded dish runs the vanilla eat chain (VERIFIED): `Root_Secondary_Consume_Food_T<n>` → `Condition_Consume_Food_T<n>` (Adventure mode only, not crouching) → charge 2.0 / 2.5 / 3.0 s (`FailOnDamage`) → `ModifyInventory` (-1 held) → `Serial [ConsumedSFX, Effect, 0.2 s pause]`. `Effect` is the item's `InteractionVars.Effect`, which on our items points at the Grade assets. `ApplyEffectInteraction.firstRun` looks the effect up by id in `EntityEffect.getAssetMap()` and calls `EffectControllerComponent.addEffect(ref, effect, accessor)`, so the asset's own scaled Duration and magnitudes apply (VERIFIED bytecode).

There is no "food eaten" event in the jar (VERIFIED absence); none is needed.

### 5.2 Strength and duration

Both come straight from the assets (section 4.1). The instant heal fires once per bite. Buffs last `base x M` seconds.

### 5.3 Stacking rules when eating again

- **Instant heal:** every bite heals (vanilla `Overwrite`, one-shot).
- **Same buff again** (same family, same tier, same Grade): the timer restarts at full length (`Overwrite`), never adds up. Eating 5 pies does not give 5 x 24 minutes.
- **Stronger buff of the same family:** replaces the weaker one (the weaker is cleared).
- **Weaker buff while a stronger one runs:** does nothing for that family (you still get the instant heal). Vanilla's rule, kept.
- **Different families** (regen + Meat + FruitVeggie): run side by side, like vanilla.
- **Vanilla (Grade 0) dishes** are members of the family ranking, so a graded dish clears a weaker vanilla buff and refuses to replace a stronger one.

### 5.4 Known limit

Vanilla chains (`HealthRegen_TierCheck_T*` etc.) only know vanilla ids. Eating a **plain** dish while a graded buff of the same family runs applies the vanilla buff **next to** it. Worst case: one extra vanilla-strength buff per family. It cannot grow further (a graded dish eaten afterwards clears the vanilla one). Fixing it would mean overriding vanilla interaction files (`More Foods.zip` overrides the vanilla item `Food_Wildmeat_Cooked` by id, VERIFIED file, but whether a pack override wins is UNVERIFIED), or the runtime path of section 11. Recommendation: accept.

### 5.5 Caps

Section 4.1 safety caps. Duration never stacks (Overwrite). There is no cap on how often you eat (vanilla has none; the 2-3 s charge is the limit).

---

## 6. XP

### 6.1 Sources

| Source | XP? | How |
|---|---|---|
| Vanilla Cooking Bench, instant or queued | **Yes** | `CraftSys` (section 3.1), 1 unit per `Post` when queued |
| SkyySacks /craft cooking recipe (only if one stays) | Yes | SkyySacks' existing `skill:fn:craftxp` call (Alchemy spec 7.2) |
| Placed Campfire | No | No owner, no event (VERIFIED). Later option in 3.2 |
| Eating food | No | No consume event in the jar (VERIFIED, 5.1). XP comes from cooking, the way SkyBlock's Alchemy pays for brewing (taking the potion out of the Brewing Stand, amount set by the ingredient), not for drinking (VERIFIED, https://hypixelskyblock.minecraft.wiki/w/Alchemy, section 15) |
| Batch-cook extras, refunds | No | Only the paid unit pays |
| Creative mode | No | Inputs are free (VERIFIED); `creativeXp=false` |

### 6.2 XP table (base XP per finished craft, keyed by primary output id, like Alchemy)

Sized so that time at the bench plus gathering the ingredients pays about what gathering itself pays per minute (UNVERIFIED pacing estimate). `[SKYY?]`

| Output | XP / craft | Note |
|---|---|---|
| `Ingredient_Salt` (5 per craft) | 3 | |
| `Ingredient_Flour`, `Ingredient_Spices`, `Ingredient_Dough` | 5 | |
| `Food_Fish_Raw` (filleting any fish) | 2 | |
| `Food_Cheese` | 15 | |
| `Food_Wildmeat_Cooked`, `Food_Fish_Grilled`, `Food_Vegetable_Cooked` (new Cooking Bench recipes) | 10 | |
| `Food_Bread`, the 4 kebabs, `Food_Salad_Berry`, `Food_Salad_Mushroom` | 25 | |
| `Food_Popcorn` | 40 | |
| `Food_Pie_Apple`, `Food_Pie_Meat`, `Food_Pie_Pumpkin` | 100 | |
| `Food_Salad_Caesar` | 120 | |
| Any other Cookingbench / Campfire recipe (modded content) | `cook.xp.default=10` | the server log names it once |

A full Meat Pie chain, one craft of each (flour, dough, spices, salt, pie), pays 5 + 5 + 5 + 3 + 100 = **118** (VERIFIED arithmetic; chain VERIFIED in Assets.zip: the pie takes 1 dough, 1 spices, 1 salt, a Meats resource and 3 Fuel; dough takes 1 flour; one salt craft makes 5 salt, so later pies skip the salt craft and pay 115).

### 6.3 Pace on the shared 100-level curve (VERIFIED arithmetic, UNVERIFIED hours)

| To reach | Total XP (0.3.2 table) | Pies needed (100 XP) | Grade unlocked |
|---|---|---|---|
| Level 10 | 9,925 | about 100 | 1 |
| Level 20 | 522,425 | about 5,200 | 2 |
| Level 30 | 8,022,425 | about 80,000 | 3 |
| Level 50 | 55,172,425 | about 552,000 | **5 (x2)** |
| Level 100 | 637,672,425 | about 6.4 million | **10 (x4)** |

This is far slower than the Alchemy spec's pace (level 50 in about 27 h, because a Greater potion pays 18,000). Cooking's dishes are cheap to make, so per-dish XP is small; the curve is the shared lock. **Decision for Skyy:** either accept that Grade 5 is a long-term goal like Mining 50, or scale Cooking up with `cook.xpMultiplier` (for example x20 puts level 50 at about 27,000 pies, near Alchemy's pace). Recommendation: pick one crafting pace for Alchemy and Cooking together. `[SKYY?]`

### 6.4 Anti-exploit

1. **Creative:** no XP and no Grade (vanilla output), checked in `CraftSys` like Alchemy.
2. **Batch-size trap:** 1 unit per `Post` on the queued path; outputs built with `getOutputItemStacks(rc, units)` (VERIFIED `giveOutput(..., job, 1)`).
3. **No loops:** no cooking output feeds back into its own chain, and no cooking output has a salvage recipe (VERIFIED recipe scan). Build-time check: fail if any Cookingbench output worth more than 5 XP is an input to a recipe that returns one of its own inputs (Alchemy's loop check, extended).
4. **No crafting graded food directly:** no generated dish has a recipe (assert 4.5.3).
5. **Cancelled crafts:** if another system cancelled `Post` before us, we neither grade nor pay.
6. **Profile switch:** the Grade uses the active profile's level at craft time; the XP award is dropped if the pkey changed before `CraftTask` ran (Alchemy rule).
7. **Rate cap (safety net):** `cook.maxXpPerMinute=20000` **base** XP per player per minute (counted before `cook.xpMultiplier` and the global multiplier, so raising the pace in 6.3 never trips it). `0` turns it off.
   - **Where:** `CraftTask.run()` step 4 (section 3.1), on the world thread, right before `SkillXp.gain`: `if (rule[0] == SkillDefs.COOKING && !Cook.allowXp(u, base)) return;`.
   - **`Cook.allowXp(u, base)`:** a `static synchronized` method (worlds run on their own threads) over a `HashMap` UUID → `long[]{windowStartMillis, sum}`. It resets the window after 60 s; if `sum + base` would pass the cap it returns false and logs one line per player per minute; otherwise it adds `base` and returns true. Stale entries are harmless (one small array per player who cooked); SkyySkills 0.3.2 has no disconnect hook today (VERIFIED grep), so clearing them is optional.
   - **Effect when it trips:** only the XP of that craft is dropped. The dish, its Grade and any tree extras were already handed out by the handler, which is correct: the ingredients were really spent, and the Grade depends on level, not on speed.
   - **Headroom:** the fastest legitimate source is Caesar Salad (120 XP, 1 s recipe) = 7,200/min; kebabs and berry/mushroom salads (25 XP, 1 s) are 1,500/min, pies 1,200/min (VERIFIED recipe times in Assets.zip). The cap is about 2.8x the peak. This is Cooking-only; Alchemy's bench path stays uncapped (Alchemy spec section 6 item 6).
8. **Admin test items:** `/skills cook` is admin only (section 8.5).
9. **Soft gate (future):** every award goes through `SkillXp.gain`, so the drift slowdown will apply automatically.

---

## 7. Skill-tree modifiers

> **Build gate: pending Skyy's OK (question 5). Do not build this section yet.** The locked focus call gives trees to the three gathering skills, and `research/Skill-Trees-Spec.md` ships "one template, three trees" with Cooking deferred to this spec (its sections 0, 7 and 14). Skyy's Cooking call asks for skill-tree modifiers, which reads as a yes, but a 4th tree in SkyyTrees has not been confirmed. Until Skyy says yes: SkyyTrees ships its 3 trees unchanged, `tree:fn:level` is absent or answers 0 for `Cooking.*`, and Cooking runs on levels alone (Grades 0-10). Once approved, add the Cooking tab to the trees spec's own build order and open questions so both docs agree, then build it as an additive SkyyTrees release after the first one. The table below is the proposed design, priced so it is ready when the answer comes.

### 7.1 Where: its own Cooking tree on the SkyyTrees template (recommended), not the Farming tree

- The trees spec puts every tree in the new **SkyyTrees** mod on one 12-slot template: tiers open at skill level 1/10/20/30/45/60; **Tokens** (1 + level/5) unlock nodes; **Dust** (1 per 10 XP of **that** skill) levels them; free respec (VERIFIED `research/Skill-Trees-Spec.md` sections 3-5). It explicitly left "Food / Cooking modifiers" to this spec and offered `tree:fn:level` to feed them.
- **Why not the Farming tree:** its 12 slots are already designed around crops; its Dust comes from Farming XP, so food power would be bought with farming progress, which breaks the lock "a tree is tied to its skill" (design lock batch 2 item 8); and a farmer who never cooks would see dead nodes.
- **Why a Cooking tree is cheap:** SkyyTrees' node table is generated from Python (`TreeDefs`), so a 4th tree is one table plus one tab. Dust works as soon as Cooking is a SkyySkills slot (`skill:fn:xp` with `"Cooking"`).
- **`[SKYY?]`** The focus call says "a skill tree per **gathering** skill"; Cooking is an artisan skill. Skyy's Cooking call ("you can make it even better with the skill tree modifiers") reads as a yes. Please confirm.

### 7.2 The Cooking tree ("Kitchen"), same slot template and cost curve as the gathering trees

Config ids use the `C` prefix. Every effect runs in SkyySkills' `Cook.plan` (craft time), which reads `tree:fn:level` `(UUID, "Cooking.<Id>")` → Integer (0 when turned off), except S3 (XP) and S4 (Health), which use SkyyTrees' existing XP and STAT hooks.

| Slot | Tier (Cooking lvl) | Node (id) | Max | Per level (total at max) | Hook |
|---|---|---|---|---|---|
| S1 | I (1) | Gourmet (CGourmet) | 25 | +0.8% chance a dish comes out 1 Grade higher (20%) | `Cook.plan`, VERIFIED event |
| S2 | I (1) | Batch Cook (CBatch) | 20 | +1% chance of one extra dish, same Grade, no XP (20%) | `Cook.plan`, VERIFIED |
| S3 | I (1) | Cooking Wisdom (CWisdom) | 15 | +1% Cooking XP (15%) | SkyyTrees XP bonus `xp.cooking`; **needs** the trees-bridge reader in `SkillXp.gain2` to cover the Cooking slot (the trees spec limits it to rows 0-2) |
| S4 | II (10) | Well Fed (CFed) | 10 | +1 max Health (+10) | SkyyTrees STAT (`skyytree_health`), SHIPPED pattern |
| S5 | II (10) | Frugal (CFrugal) | 10 | +2% chance to get back one item-id ingredient (not Fuel, not a ResourceType input) (20%) | `Cook.plan` + `CraftingRecipe.getInput()` (VERIFIED `MaterialQuantity.getItemId()`) |
| S6 | III (20) | Grill Mastery (CGrill) | 15 | +2% chance of +1 Grade on T1 dishes (cooked meat, grilled fish, cooked vegetables) (30%) | `Cook.plan` |
| S7 | III (20) | Prep Mastery (CPrep) | 10 | +3% chance of +1 Grade on T2 dishes (bread, kebabs, salads) (30%) | `Cook.plan` |
| S8 | IV (30) | Baker Mastery (CBaker) | 10 | +3% chance of +1 Grade on T3 dishes (popcorn, pies, Caesar) (30%) | `Cook.plan` |
| S9 | IV (30) | Prep Cook (CIngr) | 10 | +3% chance that an ingredient craft (flour, dough, salt, spices) gives double output (30%) | `Cook.plan` |
| S10 | V (45) | Gourmet II (CGourmet2) | 20 | +1% chance of +1 Grade on any dish, adds to S1 (+20%) | `Cook.plan` |
| S11 | V (45) | Signature Dish (CSig) | 10 | +1% chance of **+2** Grades (10%) | `Cook.plan` |
| S12 | VI (60) | Master Chef (CMaster) | 5 | Level 1: **+1 Grade on every dish**. Levels 2-5: +5% chance each of one more Grade (+20%) | `Cook.plan` |

**How Grade bonuses combine (one roll per dish):**
1. `g = floor(level / 10) + (Master Chef >= 1 ? 1 : 0)`.
2. `p1` = S1 + S10 + the matching mastery (S6/S7/S8) + Master Chef's chance, capped at 100%. Roll once: success → `g + 1`.
3. Roll S11 separately: success → `g + 2` (instead of the step-2 bonus if both hit, so at most +2 from rolls).
4. Cap at 12.
- Example, level 100 with everything maxed: Grade 11 always, Grade 12 on most dishes.
- Example, level 50 with S1 at 10 and Prep Mastery at 5: bread is Grade 5, with a 23% chance of Grade 6.

**Later, not in this build:** a "Hearty" node (+% buff duration only) or "Potent" (+% strength only). They need either a second Grade axis or the runtime path (section 11). A "faster cooking" node is impossible (section 0, item 6).

**Without SkyyTrees:** `tree:fn:level` is absent, every node reads 0, and Cooking works on levels alone (zero-dependency rule).

---

## 8. Storage, bridge keys, /skills row, Stats page, commands

### 8.1 Slot and storage (aligned with the Alchemy spec)

- **Slot 12 = `Cooking`**, the slot the Alchemy spec reserves ("12+ reserved - next free: Cooking"). `N = 13`, `COOKING = 12`. Label `Cooking`, icon `Food_Pie_Apple` (VERIFIED id, use `must()`), colour `#ffb070`. Slot 12 is `>= CLASS0` but not a class, so every loop the Alchemy spec bounds with `CLASS_END = 10` already covers it (Alchemy spec 9.3).
- **Per profile** (tools/PROFILES-CONTRACT.md): new keys `Cooking` and `Cooking.paid` in `Skyy_SkyySkills/players/<pkey>.properties`, read and written through `SkillDefs.NAMES` by the existing 0.3.2 file layer. Old files read as 0 XP with no back-pay (VERIFIED `readFile` behaviour, Alchemy spec 8).
- **Nothing else is stored.** The Grade lives in the item id. Tree node levels live in SkyyTrees' own `players/<pkey>.properties` as `Cooking.<Id>=<level>` (trees spec section 11 format).
- **Perk row:** add `cooking` as perk row 7 (`PERK_SLOT` gains 12). Default flat perks 0: the Grade is Cooking's perk. `perk.cooking.healthPerLevel` stays available `[SKYY?]`.
- Level-up coins: the existing `coinsPerLevel x level`.

### 8.2 Bridge keys

| Key | Type | Written by | Notes |
|---|---|---|---|
| `skill:<uuid>` | String | SkyySkills | gains `Cooking:<lvl>` (after `Alchemy`, `Smithing`) |
| `skill:fn:level` | Function (UUID, skill) → Integer | SkyySkills | answers `"Cooking"` via `SkillDefs.indexOf` (VERIFIED code) |
| `skill:fn:xp` | Function (UUID, skill) → Long | SkyySkills (trees patch) | gives the Cooking tree its Dust |
| `skill:fn:craftxp` | Function (Alchemy spec 7.2) | SkyySkills | Cooking recipes are classified automatically |
| `skill:fn:addxp` | Function (Alchemy spec 7.1) | SkyySkills | Cooking stays **out** of `bridge.addxp.skills` (no outside source needs it) |
| **`cook:fn:grade`** | Function apply(UUID) → Integer | SkyySkills (new) | guaranteed Grade now (level/10 + Master Chef), for the HUD / Menu / SkyySacks |
| **`cook:fn:out`** | Function apply(Object[]{UUID, String recipeId, Integer crafts}) → java.util.List of ItemStack | SkyySkills (new) | graded outputs + batch extras + refunds for a craft **another mod** completed (SkyySacks). No XP (that goes through `craftxp`). Returns null for a non-cooking recipe. World thread only |
| **`cook:prefix`** | String `"Skyy_Cook_Food_"` | SkyySkills (new) | lets SkyySacks' `catOf` and the Bazaar recognise graded dishes without hard-coding |
| `tree:fn:level` | Function (UUID, `"Cooking.CGourmet"`) → Integer | SkyyTrees | read by `Cook.plan` |
| `profile:fn:key`, `profile:epoch:<uuid>` | contract | SkyyProfiles | already handled by 0.3.2 |

All new keys are published in `setup()` and removed in `shutdown()`, next to `skill:fn:level`. Plain `java.util.function.Function` classes (no lambdas), like `SkillFn`.

### 8.3 /skills row

- Row order from the Alchemy spec plus Cooking: **Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, class skill** = 8 rows. The Alchemy spec already sized this: root Group height 624 with a Cooking row; more than 8 rows needs tabs.
- Row text: `Cooking 37` + bar + `12.3k/20.0k`, and a small second label `Grade 3 food x1.52`. No underscores in ids (e.g. `#SkyySRowCookG`), text through `b.set(...)`.
- Footer hint gains "cook at the Cooking Bench".

### 8.4 Stats page (`StatsPage.lines` / `how` for slot 12)

Example at level 37 with a few tree levels:

| Section | Lines |
|---|---|
| Boosts right now (level 37) | "Food you cook - Grade 3 (heal and buffs x1.52 stronger - buffs last x1.52 longer)"; "Next Grade - Grade 4 (x1.74) at Cooking 40"; "Skill tree - 12% chance of a higher Grade - 5% extra dish - 4% ingredient back" (only when above 0) |
| Level 38 adds | "+3800 coins when you reach level 38". On a level ending in 9: "Level 40 adds - Grade 4 food (x1.74)" |
| How (grey footer) | "Earn XP by cooking at a Cooking Bench (ingredients can come from your bags) - pies and Caesar salad pay the most - a placed Campfire gives no XP" |

Dashes instead of commas and colons, as the Alchemy spec does.

### 8.5 Commands (HANDOFF command rules)

- `/skills stats cooking`, `/skills top cooking`: the existing commands; add `cooking` to help texts and the unknown-skill message (`coo` prefix has no clash).
- `/skills xp cooking <amount>`: the Alchemy spec's admin test helper, unchanged.
- **New admin helper `/skills cook <dish> <grade>`**: gives 5 of `Skyy_Cook_<dish>_G<grade>` (grade 0 = vanilla), for testing effects without leveling. `requirePermission("skyyskills.admin")` + `setPermissionGroups(new String[0])`, a positional subcommand with two `withRequiredArg`.

### 8.6 xp.properties additions (appended once, `CookCfg.ensureDefaults`, the `AlchCfg` pattern)

```
# ---------- Cooking (SkyySkills 0.4) ----------
# Comments must stay on their own lines.
cook.enabled=true
# Grade = floor(level / 10) + tree. The x2 at 50 / x4 at 100 numbers are baked into the generated effect assets.
# maxGrade can only LOWER the cap: the jar only has assets for Grades 1-12, so values above 12 are read as 12. Raising it needs a rebuild.
cook.maxGrade=12
# Base XP per finished craft at the Cooking Bench, keyed by the craft's primary OUTPUT item id. 0 = no XP.
cook.xp.Ingredient_Salt=3
cook.xp.Ingredient_Flour=5
cook.xp.Ingredient_Spices=5
cook.xp.Ingredient_Dough=5
cook.xp.Food_Fish_Raw=2
cook.xp.Food_Cheese=15
cook.xp.Food_Wildmeat_Cooked=10
cook.xp.Food_Fish_Grilled=10
cook.xp.Food_Vegetable_Cooked=10
cook.xp.Food_Bread=25
cook.xp.Food_Kebab_Fruit=25
cook.xp.Food_Kebab_Meat=25
cook.xp.Food_Kebab_Mushroom=25
cook.xp.Food_Kebab_Vegetable=25
cook.xp.Food_Salad_Berry=25
cook.xp.Food_Salad_Mushroom=25
cook.xp.Food_Popcorn=40
cook.xp.Food_Pie_Apple=100
cook.xp.Food_Pie_Meat=100
cook.xp.Food_Pie_Pumpkin=100
cook.xp.Food_Salad_Caesar=120
cook.xp.default=10
cook.xpMultiplier=1.0
cook.maxXpPerMinute=20000
# Dishes that get Grades (must match the generated assets; others always come out plain)
cook.graded=Food_Wildmeat_Cooked,Food_Fish_Grilled,Food_Vegetable_Cooked,Food_Bread,Food_Kebab_Fruit,Food_Kebab_Meat,Food_Kebab_Mushroom,Food_Kebab_Vegetable,Food_Salad_Berry,Food_Salad_Mushroom,Food_Popcorn,Food_Pie_Apple,Food_Pie_Meat,Food_Pie_Pumpkin,Food_Salad_Caesar
```

`CookCfg` drops any `cook.graded` id that has no generated asset (logged once), so a typo cannot hand out missing items. The same guard covers the Grade number: `CookCfg` reads `cook.maxGrade` as `clamp(value, 0, Cook.GEN_MAX)`, where `GEN_MAX = 12` is a build-time constant written by the asset generator (like `COOK_STRENGTH_EXP` / `COOK_DURATION_EXP`, section 4.1), and `Cook.grade` / `Cook.plan` clamp every result to that value again before building an id. An edited `cook.maxGrade=13` therefore logs one warning and behaves as 12; no `_G13` id is ever looked up. Tree percentages live in SkyyTrees' `trees.properties` (`Cooking.<Id>.per`, trees spec section 11).

---

## 9. Integration points

1. **Alchemy spec (`research/Alchemy-Skill-Spec.md`) — aligned:**
   - Same 0.4 patch, same `CraftSys` / `CraftTask` / `RecipeXp.classify` (Cooking adds `Cookingbench` and `Campfire` → slot 12). **Changes to Alchemy's CraftTask** (merged version in 3.1): the `cookGave` flag in step 1 (`if (ev.isCancelled() && !cookGave) return;`, because Cooking cancels `Post` itself to hand out the graded dish), plus two lines that only run for `COOKING` (the rate cap, step 4, and `cook.xpMultiplier`, step 5). Alchemy recipes behave exactly as before. The Alchemy spec's header still says "one line"; the merged 3.1 text here is the reference. Alchemy's creative early return in `CraftSys` stays first and unchanged.
   - Same unit rule (1 per queued `Post`), same creative rule, same pkey check, same `skill:fn:craftxp` for SkyySacks, same admin `/skills xp`.
   - Slot 12, `N = 13`, 8 rows, perk row 7. Alchemy's `CLASS_END` fixes cover slot 12.
   - **Pace conflict:** Alchemy is sized so level 50 takes about 27 h; Cooking's defaults make level 50 much slower (section 6.3). Pick one crafting pace for both. `[SKYY?]`
   - Alchemy's potion-duration perk (`perk.alchemy.durationPerLevel`) extends potions at drink time with `addEffect(..., EXTEND, ...)`. Cooking does not use that path; the two never touch the same effects (potion ids vs `Skyy_Cook_*` and vanilla food buffs). If Skyy picks "Cooking parity" for Alchemy (x4 at 100), note that Cooking's x4 is on both strength and duration, Alchemy's only on duration.
2. **Trees spec (`research/Skill-Trees-Spec.md`) — aligned:**
   - **Pending Skyy's OK (section 7 build gate).** If approved, the Cooking tree is a 4th tree in SkyyTrees on the same template, tiers, Tokens, Dust and respec. `TreeDefs` gains the section 7.2 table; the page gains a Cooking tab. The trees spec's build order (its section 14) ships 3 trees today; the Cooking tab is added there, as a later SkyyTrees release, only after the yes.
   - Needs `skill:fn:xp` (trees patch) to answer `"Cooking"`, and the `skill:bonus` XP reader in `SkillXp.gain2` to apply `xp.cooking` to slot 12 (the trees spec limits it to rows 0-2).
   - The "Tree" button on /skills rows should also appear on the Cooking row.
   - If Skyy decides trees are gathering-only, drop section 7; Cooking still works on levels.
3. **Asset pack in SkyySkills:** this is SkyySkills' first asset pack (Alchemy adds none). If another part of 0.4 ever ships lang lines, they go into the **same** `server.lang` file in the jar. Uninstalling SkyySkills would leave graded dishes as unknown items (behaviour UNVERIFIED). If that matters, the generated assets can move to a tiny asset-only jar that never changes.
4. **SkyySacks (another workflow owns it):** `catOf` → `Skyy_Cook_Food_` to Farming (3.4); remove Cookingbench (and Campfire `[SKYY?]`) recipes from /craft per the table-only call; if one stays, give the `cook:fn:out` list (3.3). Its bench link already feeds the vanilla Cooking Bench window, so bag ingredients just work.
5. **SkyyAccessories:** the Cooking Bench accessory stops counting (its plan already says so). No other change.
6. **Placed Campfire and placed Furnace:** one shared "collector is the cook/smelter" design, decided once (3.2, Alchemy spec 10.3).
7. **SkyyBazaar:** optional products for graded dishes later (3.4).
8. **HUD / Menu:** `skill:<uuid>` carries `Cooking:<lvl>`; SkyyMenu parses it generically (VERIFIED per the Alchemy spec). `cook:fn:grade` is available for a HUD line.

---

## 10. Builder checklist

**New classes** (dependency order; javassist rules: no generics, lambdas, autoboxing, enhanced-for, inner classes, String-switch):

| Class | Holds |
|---|---|
| `CookCfg` | config fields, `read`, `ensureDefaults`, `xpFor(outId)`, `graded` set, generated-id set (from a build-time constant) |
| `Cook` | `GEN_MAX` (build-time, 12), `grade(u)` and `plan(u, recipe, units)` → List of ItemStack or null (Grade rolls, batch, refund, ingredient double; every Grade clamped to `min(cook.maxGrade, GEN_MAX)`), `gradedId(dish, g)`, `settings(accessor, ref)`, `allowXp(u, base)` (synchronized per-minute XP window, 6.4 item 7) |
| `CookGradeFn`, `CookOutFn` | the `cook:fn:grade` / `cook:fn:out` Functions |
| `CookCmd` | admin `/skills cook <dish> <grade>` |

**Edits:** `SkillDefs` (slot 12, `COOKING`, `ROW_SLOTS`, `PERK_SLOT`), `RecipeXp.classify` (Cooking benches), `CraftSys` (grading branch, merged body in 3.1), `CraftTask` (`cookGave` flag, rate-cap check, `cook.xpMultiplier`), `PerkCfg` (8 rows), `SkillsPage` / `StatsPage` (`lines`, `how`, row label), `SkillCfg.load` → `CookCfg`, `setup()` / `shutdown()` (publish/remove the new keys), manifest text, and the asset generator + asserts (section 4) at the end of the build script before `B.assemble`.

**Add to the `B.probe` list** (VERIFIED to exist today): `CraftRecipeEvent` `getCraftedRecipe`, `getQuantity`; `CancellableEcsEvent` `setCancelled`, `isCancelled`; `CraftingManager` `getOutputItemStacks`; `InventoryUtils` `getContainerForItemPickup`; `SimpleItemContainer` `addOrDropItemStack`; `CraftingRecipe` `getInput`, `getPrimaryOutput`, `getOutputs`, `getBenchRequirement`, `getTimeSeconds`, `getId`; `MaterialQuantity` `getItemId`, `getResourceTypeId`, `getQuantity`; `ItemStack(String, int)`; `PlayerSettings` `getComponentType`, `defaults`.

---

## 11. Fallback (Plan B): vanilla ids + metadata + runtime scaling

Use this only if the generated effect or interaction assets fail to load (section 13, step 1).

- **Stamp:** the same `CraftSys` cancel-and-give, but give the **vanilla** id with `ItemStack.withMetadata("SkyyCook", {g})` plus an `ItemDisplay` name/description (VERIFIED APIs; SkyyRolls 0.1.1 already stamps metadata; the relog test in TEST-CHECKLIST is still open).
- **Bags:** the SkyySacks pool would strip it (VERIFIED), so SkyySacks must never sweep a stack with metadata.
- **Eating:** detect it with an `EntityEventSystem` on `InventoryChangeEvent`: active hotbar slot, `SlotTransaction` REMOVE by 1, `Item.isConsumable()`, read `getSlotBefore()` metadata, ignore moves and recent crafts. This is exactly what MMOSkillTree's `ConsumeItemEventSystem` does (VERIFIED constant pool). Confirm it was a real bite by finding the dish's vanilla buff freshly applied, so a dropped item does nothing.
- **Scaling:** swap the fresh vanilla buff for the Grade asset with `addEffect(ref, gradedEffect, duration, OVERWRITE, accessor)` and remove the vanilla one (VERIFIED overloads); add the extra instant heal with `EntityStatMap.addStatValue` (VERIFIED signature; the % base must be computed from max Health, UNVERIFIED).
- **Pros:** vanilla ids everywhere; allows duration-only / strength-only tree nodes. **Cons:** heuristics, unverified tooltip rendering, the bag conflict, the pending metadata relog test, and it still needs the 156 effect assets for strength.
- A cleaner variant would add a custom Interaction class to the eat chain. Mods can register new interaction types (`getCodecRegistry(Interaction.CODEC).register(name, class, codec)`, VERIFIED in Aetherhaven's bootstrap, which corrects the research notes), but it would mean overriding vanilla food assets (UNVERIFIED) and building a `BuilderCodec` from javassist (UNVERIFIED in our toolchain).

---

## 12. Build order

1. **SkyySkills 0.4** = Alchemy spec + this spec in one patch (`tools/skills_0_4_patch.py`), built without deploying.
2. **Load test first:** deploy to a test copy of the world and check that the 447 generated assets load (step 1 below) before anything else. If effects or interactions fail, switch to section 11.
3. **SkyySacks** next build: `catOf` + table-only removal (+ `craftxp` already planned by Alchemy).
4. **SkyyTrees:** 0.1 ships the 3 gathering trees as the trees spec says. The Cooking tab comes in a later SkyyTrees release **only if Skyy approves the Cooking tree** (section 7 build gate, question 5).
5. Deploy the set together once Skyy OKs it (HANDOFF deploy rule), then log it in HANDOFF section 6.

---

## 13. In-game test checklist (for Skyy)

1. **Server log:** SkyySkills 0.4 ready, no asset errors mentioning `Skyy_Cook_`. Then `/skills cook Food_Bread 5` gives "Bread (Grade 5)" with the right tooltip (name, description, Rare colour).
2. **/skills:** 8 rows, Cooking at 0. `/skills stats cooking` shows "Grade 0" and "Grade 1 at Cooking 10".
3. **Plain craft:** place a vanilla Cooking Bench, keep the ingredients only in your Farming bag, cook 1 Bread at Cooking 0. You get a normal Bread and "+25 Cooking XP".
4. **Batch:** queue 5 kebabs. You get 5 kebabs and 125 XP (not 625).
5. **Grade craft:** `/skills xp cooking 55172425` (level 50), cook a Meat Pie → "Meat Pie (Grade 5)" lands in your inventory, exactly one per pie.
6. **Strength:** take damage to about 30% health, eat a Grade 5 bread → about +30% of your max health (plain bread gives 15%).
7. **Duration:** eat a Grade 5 Meat Pie → the regen icon runs 12:00 (plain 6:00), your max health is +30%.
8. **Stacking rules:** eat a Grade 10 pie (`/skills cook Food_Pie_Meat 10`), then a Grade 5 kebab → the pie's regen and Meat buff stay. Eat a Grade 10 pie again → the timer resets to 24:00, it does not add.
9. **Known limit check:** eat a plain meat pie while the Grade 10 buff runs → a second regen icon may appear (expected, section 5.4).
10. **Stacks and storage:** two Grade 5 breads stack; Grade 5 and Grade 6 do not. Put Grade 5 bread in a chest, relog, take it out → still Grade 5.
11. **Bags:** with the SkyySacks change, the graded dish goes into the Farming bag and comes back out as the same Grade.
12. **Campfire:** cooking at a placed Campfire gives plain food and no XP. The Cooking Bench shows the Cooked Meat, Grilled Fish and Cooked Vegetables recipes.
13. **Creative:** cook in creative → plain food, no XP.
14. **Two accounts:** player B eats player A's Grade 5 pie → B gets the Grade 5 effects.
15. **Profiles:** on a fresh profile (Cooking 0) the same recipe gives plain food.
16. **Tree (only once the Cooking tree is approved and built):** raise Gourmet with debug Dust, cook 50 kebabs → some come out one Grade higher. Master Chef → every dish +1 Grade.

---

## 14. Open questions for Skyy

1. Is **x4 strength and x4 duration** (so regen heals x16 in total at level 100) what you want, or x4 overall (`a = b = 0.5`)?
2. **Pace:** at these XP values Grade 5 is about 550,000 pies away. Raise `cook.xpMultiplier` to match Alchemy's pace?
3. Does the **Campfire accessory** leave /craft too (table-only)?
4. **Cheese:** keep it ungraded (so Caesar salad and the mouse potion still work)?
5. **Cooking tree:** yes to a 4th SkyyTrees tree for Cooking (an artisan skill)? Until you answer, it is not built and Cooking works on levels alone (Grades 0-10).
6. Fuel cost on the new Cooking Bench campfire recipes (1 Fuel)?
7. Rarity colours per Grade (table 2.2)?

---

## 15. Sources

**Engine** (`HytaleServer.jar`, read-only, `tools/dev`):
- Bytecode: `SimpleCraftingWindow#handleAction`; `CraftingManager#tick`, `#craftItem`, `#queueCraft`, `#giveOutput` (both overloads); `CommandBuffer#invoke`; `ApplyEffectInteraction#firstRun`; `ItemStack#getDisplayName` / `#getDisplayDescription`; `PlayerCraftingSystems$CraftingTickingSystem#tick`.
- Reflection: `CraftingManager`, `CraftingRecipe`, `BenchRequirement`, `CraftRecipeEvent` / `$Post`, `EffectControllerComponent`, `ItemStack`, `ItemDisplayMetadata`, `SimpleItemContainer`, `InventoryUtils`, `MoveTransaction`, `InventoryChangeEvent`, `ProcessingBenchWindow`, `CommandBuffer`.
- `callers.py`: who calls `craftItem` / `queueCraft` / `CraftingManager.tick`.
- Client binary: `HytaleClient.exe` contains `ClientItemMetadata.ItemDisplay` / `ItemDisplayMetadata` strings.

**Assets** (`Assets.zip`, in memory): `Server/Item/Items/Bench/*.json`, `Server/Item/Items/Food/*.json`, `Server/Item/Items/Ingredient/**` (incl. `Life Essence Recipes/`), `Server/Entity/Effects/Food/**`, `Server/Item/Interactions/Consumables/**`, `Server/Item/RootInteractions/Consumables/*`, recipe scan of all items for Cookingbench/Campfire and for dish ids used as inputs.

**Installed mods** (read-only): `More Foods.zip` (food items parenting `Template_Food`, custom food effects, vanilla-id override), `MMOSkillTree-1.6.0.jar` (`ConsumeItemEventSystem`), `Aetherhaven-3.1.3.jar` (`GaiaDraughtCraftSystem`, `GaiaDraughtService`, `ReputationUnlocksBootstrap` interaction registration, `JewelryNativeTooltipManager`), `SimpleEnchantments-1.2.0.jar` (`NativeTooltipManager`, `CraftRecipeCancelSystem`), `EndgameAndQoL5.4.1.jar` (`RecipeOverrideSystem`), `NotEnoughPotions-2.3.0.jar` (effect assets), plus a scan of every jar/zip for effect and interaction assets.

**Our code and docs:** `SkyySkills/build_skyyskills_0.3.2.py`, `SkyySacks/build_skyysacks_0.7.2.py`, `SkyyAccessories/build_skyyaccessories_0.4.1.py`, `SkyyBazaar/build_skyybazaar_0.1.1.py`, `tools/skyybuild.py`, `tools/PROFILES-CONTRACT.md`, `HANDOFF.md`, `SkyySkills-Plan.md`, `SkyySacks-Plan.md`, `SkyyAccessories-Plan.md`, `research/Alchemy-Skill-Spec.md`, `research/Skill-Trees-Spec.md`.

**Web** (summarized in our own words):
- Wynncraft Cooking: a cooked food's duration grows with Cooking level, from about 18 min for a level-1 cook to 48 min at the level-105 cap; its charges go 1/2/3 by level band; the level does not raise strength, only the material tier does (top tiers add about 40%). https://wynncraft.wiki.gg/wiki/Cooking (fetched 2026-09-23, VERIFIED). The closest real precedent for "cooking level makes food last longer".
- Stardew Valley Qi Seasoning: gold-quality dish, +80% health/energy, +1 to buff stats, +50% buff duration. https://stardewvalleywiki.com/Qi_Seasoning (fetched, VERIFIED). A precedent for one quality value scaling strength and duration together.
- Hypixel SkyBlock has 13 skills and no Cooking skill. https://hypixelskyblock.minecraft.wiki/w/Skills (fetched, VERIFIED).
- Hypixel SkyBlock Alchemy: XP is paid when a brewed potion is taken out of the Brewing Stand, and the amount depends on the ingredient added, not on drinking. https://hypixelskyblock.minecraft.wiki/w/Alchemy (fetched 2026-09-23, VERIFIED). Used in 6.1. (The old official wiki.hypixel.net page now redirects to a notice that the official wiki closed in July 2026.)
- mcMMO Farmer's Diet (Herbalism) and Fisherman's Diet (Fishing): **not a precedent for this design.** Each rank only adds a flat +1 hunger point restored (up to +5 at rank 5); neither changes saturation, buff strength or buff duration. https://github.com/mcMMO-Dev/mcmmo-wiki-repo (`skills/herbalism.md`, `skills/fishing.md`, fetched 2026-09-23, VERIFIED; same text as https://wiki.mcmmo.org/en/skills/herbalism and https://wiki.mcmmo.org/en/skills/fishing).
- Valheim (food stacking by slots) and the Spigot "Expanded Cooking" quality plugin: reported by the research agent (https://valheim.weirdgloop.org/w/Food, https://www.spigotmc.org/resources/115968/). UNVERIFIED by the writer; background only.

**Corrections to the research notes:**
- Campfire dishes are not identical to raw food: they add HealthRegen T1 and a Meat/FruitVeggie T1 buff.
- Mods **can** register new Interaction types (Aetherhaven, VERIFIED); the notes said UNVERIFIED.
- Our toolchain **can** ship asset JSON (items + lang proven by SkyyAccessories); the notes said it cannot.
- Food instant heals are `EntityEffect` assets (`StatModifiers`, 0.1 s), not `ChangeStatInteraction`.
- On the queued path each `Post` reports the whole batch size; outputs and XP must count 1 per `Post`.
- The fish "splitting" recipes take `Fish_*` resource inputs and make `Food_Fish_Raw`; there is no self-duplicating recipe.
