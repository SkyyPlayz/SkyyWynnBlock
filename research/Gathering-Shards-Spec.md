# Gathering + Shards - build spec (lifelong tools, tier gate, Fishing / Farming split, six shard islands, totems)

Written 2026-10-13 (spec writer, Fable; SPEC round - nothing built, nothing deployed). Merges every decision Skyy locked 2026-10-11 ..
2026-10-13 (`docs/answered/gear.md`, `skills.md`, `economy.md`, `world.md`, `social.md`, `ui.md` - they WIN over every older doc)
with `research/Gathering-Progression-Spec.md` (2026-10-06, tiers / Enchanted / collections - still the material tables),
`research/Tool-Levels-Spec.md` + `research/cloud/Tool-Levels-Revision.md` (power ladder, hooks - revised here for lifelong tools),
`research/Shard-Islands-Ideas.md`, `research/cloud/Pocket-Shards-Spec.md` (REPLACED: no minion block; its lazy production math
survives), `research/cloud/Gathering-Tiers-Draft.md`, `research/Rebirth-Ideas.md`, `research/Tutorial-Plan.md`,
`research/Hytale-0.7-Port.md`. Engine facts come from the Hytale **0.7.0 release** jar + Assets.zip (reflection + constant pools, read
only, scratch deleted) and the live build scripts (SkyyGear 0.2.23, SkyyIslands 0.5.5, SkyySkills 0.4.30, SkyyFishing 0.1.2).

Legend: **VERIFIED** = seen in the 0.7 jar / Assets.zip / a live script. **UNVERIFIED** = needs a probe (named). **PLACEHOLDER** =
a number Skyy has not picked; every runtime placeholder is a Server Setup row (section 11). Rarity names below are SkyyGear's live
ladder: Normal (shown with the vanilla "Common" frame = Skyy's "common"), Unique, Rare, Legendary, Fabled, Mythic (boss-only), Set,
Untiered (orange, specials).

---

## 0. Plain words (for Skyy)

- You get ONE hatchet, ONE pickaxe, ONE hoe and ONE sickle at spawn (Crude, Common). A hub quest gives your ONE fishing pole. You never
  craft these again: in `/smithing` (the Anvil tab) you **tier them up** with Enchanted materials, **raise their rarity** with Sigils,
  **reforge** their lines, and spend **Upgrade Points** the tool earned while you used it. Shovels stay plain craftable items.
- A tool's **level is your skill level**, capped by its tier. Its **tier gates** what you can break: your tier = normal speed, one tier
  up = slow (a quarter of the power), two up = refused with a popup.
- Gathering **armor** works the same way (level = skill level capped by tier, tier up on the Anvil, keeps rarity).
- **Fishing** becomes its own skill with its own tree; **Farming** splits into Farming, Ranching and Orchard (three skills, one shared
  tree; your Farming level = their average).
- **Shards** are portal blocks on your island. Each opens a private mini world: a hub island with fixed slots around it, islands that
  grow in place, eternal plants, totems that call themed workers. You collect from the shard menu (that is when XP and collections are
  paid). Nothing can be built or broken there - only gathered, and totems placed / picked up.
- **Rebirth** (own spec) sends tools back to Crude level 0 but keeps rarity, lines and points, adds a rebirth modifier, and unlocks the
  Multitool merge.

---

## 1. Decisions followed (quoted; nothing here re-decides them)

| Date / file | Skyy's words (short, word for word where it matters) | What it fixes here |
|---|---|---|
| gear.md 2026-10-11 GATHERING PROGRESSION | "you need a copper pickaxe to mine iron, iron for thorium, thorium to mine cobalt and so on. do the same for the farming and foraging tiers" + popup "Own tier + next, next is slow"; "your tool levels with your mining ... gives you upgrade points to put into things like vein mine fortune or speed" + popup "= your skill level, capped by tier" | sections 4, 5, 6 |
| gear.md 2026-10-11 UPGRADE COST | "we will make upgrading more difficult than crafting. (like it costs a enchanted iron ingot to upgrade copper to iron, and so on.)" | 6.1 |
| gear.md 2026-10-12 LIFELONG TOOLS | "you spawn with a pickaxe and an axe, at common ... you upgrade the rarity with special tool upgrade items in / smithing ... the rarity acts as a sort of stat multiplier, and boosts what you can get from rolls ... you can only upgrade your tool through the upgrader, you cant make a new one. when you rebirth, you pickaxe keeps its rarity, and stats, but reverts back to crude, and its level resets to 0 ... gets a rebirth modifier ... unlock the multi tool after the first rebirth" + popups "All together", "Yes, all gathering tools", "Fold it in, lock to rebirth 1" | 3, 5, 6, 8.5 |
| gear.md 2026-10-12 STARTING TOOLS / SHOVEL + POLE | "youll start with the hatchet, the pickaxe, the hoe, and the cycle, but well do a quest at hub to get into fishing." / "the shovel is weird, we can leave it out as a craft item. and the pole will level with you once you get it" | 3.1, 5.4 |
| gear.md 2026-10-12 GATHERING ARMOR LEVELS | popup "Yes, like the tools": level = skill level capped by tier, tier up with Enchanted, keep rarity + rolls, T1 on rebirth | 5.5 |
| gear.md 2026-10-12 RARITY SIGILS | "we will make it work on any and all gear that has a rarity. and skip tiers ... common pickaxe, and a legendary upgrade rune, you can just upgrade it to legendary in the /smithing menu" + popup "Sigils" | 6.2 |
| gear.md 2026-10-10 (still valid) | ONE Anvil tab (Reforge + Upgrade), `/smithing` hub, "[Lv N]" names, multitool merge rules (best rarity, merged lines) | 6, 8.5 |
| skills.md 2026-10-11 FARMING TOTEMS + IDEAS | Rain Totem -> Totem Pole; popups "No fuel, optional booster", "Both: tier by Upgrade, extras in slots"; 12 totem types kept | 9.3 |
| skills.md 2026-10-11 SHARD ISLANDS / SHARDS 2 / SHARDS 3 | "mini islands you only accses from the shard placed on your island (like a portal there.) ... starts with 1 wheat island ... and a single T1 harvest spirit totem ... all plants are eternal ... 3 lvs max to start ... buy a new island for a new crop" / "collections and xp are gained when you collect from the shard ... auto compactors ... time compressors ... its all portected" / popup "fixed slots ... the same shard menu from the portal on your main island" / "6 shards, lets add a combat one" + popup "Shared totems, themed workers ... right click them to see their info, upgrade them, give them modifiers, and pick them up ... shards can also be picked up ... each shard has a max storage" | 9 |
| skills.md 2026-10-11 HARVEST MOON + FARMING SKILLS | "harvest moon gives extra, only and extremely low chance to get enchanted (can be boosted by moon blade modifier on scythe ... each should probly be its own shard, and its own skill so your farming level is the average of your 3 farming skills. but they keep one shared farming skill tree" | 5.3, 9.3 |
| skills.md 2026-10-12 FISHING ROD / FISHING SKILL | "you upgrade the pole, but you have to craft a new reel, hooks, line, and sinkers." / "fishing gets its own skill, and skill tree" | 5.4 |
| skills.md 2026-10-12 REBIRTH (all lines) + Rebirth-Ideas.md | resets skills + class, keeps island / shards / gear; XP past max -> points; Nexus tree | 8.5 (data only - the rebirth spec owns the tree) |
| skills.md 2026-10-11 STOP PUNCHING TREES | "our own gate (no-tool = tier 0 ...) - build our own, don't pack it" | 4.1 |
| social.md 2026-10-12 STARTER ISLANDS + Tutorial-Plan | starter islands fixed, nothing protected; tutorial "make crude tools" = the one starter set | 3.1 |
| world.md 2026-10-11 MGG BIOME SELECTOR | study read-only for runtime world creation (ARR, no code copied) | 10 |
| ui.md 2026-10-13 VISUALS | cloud draws the shard menu / totem pages, local review, no wait for Skyy | 9.6 |
| PROJECT-RULES 2 | check existing mods first; no duplicates; MIT may be folded with credit | 2 |

Older locks kept: Tree Feller 1/2/4/5/6/10 (SkyyTrees `feller.logs`), Vein Mine + Tree Feller also in the trees and stacking with the
tool (total cap 8, gear.md 2026-10-10), tool stat names Mining / Chopping / Digging Power, Fortune caps (tool 25, armor 15 ...),
Enchanted ratio 100 (bags.md 2026-10-06), Enchanted from INGOTS for metals, coins never skip collections (R3).

---

## 2. What exists to reuse (survey done first - PROJECT-RULES 2)

### 2.1 Skyy's Mods folder (read only, `python tools/mod_check.py - <word>`) + `research/Mod-Database.md`

| Mod | Licence | Verdict |
|---|---|---|
| **Multitools** 1.2.9 (InkBlindCat) | MIT | **FOLD** its 8 multitool models / icons into SkyyGear with credit; drop the pack mod; the merge is locked to rebirth 1 (gear.md 2026-10-12). Its own recipes go (section 12). |
| **MoreTotems** 1.0.068 (nagatwin; Water / Void / Fire deployables) | MIT | **FOLD the Water Totem** (model, rain-on-crops idea) as the base of our Rain Totem, credit nagatwin; Void / Fire = combat deployables LATER, not here. |
| ShamanTotem 0.1.0 (Fire / Ice / Slowness deployables) | unknown | duplicate of MoreTotems' idea; skip (no duplicates rule). |
| StopPunchingTrees 1.1.1 | not shown | not packed; our tier gate covers "no tool = tier 0" (Skyy 2026-10-11). |
| LincerosLevelTools 2.5.3 (Evolution Stone per metal, tool levelling UI) | check | **STUDY ONLY**: one stone per metal that evolves a tool = the same shape as our Enchanted-ingot tier-up; read its UI layout (36 ui files) for the tool page, copy nothing. |
| PJ-HyperPickaxes 1.3.5 (Fortune / Silktouch pickaxe variants) | check | skip; our rolls already carry Fortune. |
| vein-mining 2.4.0 (EineNT, <0.7), treeharvester 1.1 (Serilum) | - | skip; SkyyTrees already has Vein Burst + Tree Feller (no duplicates). |
| AdvancedFarming 1.3.1 | none | ideas only (metal hoes / sickles, bigger watering cans) - already in the older spec. Farming_Overhaul replaces sickle files: keep OFF (clash with our sickle gate). |
| Resource_Chickens 1.0.3 (45 resource chickens, 89 NPC files) | check | **STUDY** for the Ranching shard look (resource animals as workers); pack by id only if its licence allows; else our own Herd Spirits. |
| Kami.OreGolems 1.0.7 (47 ore-golem NPCs, no code) | check | **STUDY** for Mining Golem worker looks (ore-textured golems per metal); pack by id if allowed, else recolour vanilla golems. |
| Clay Factoria 1.1.2 (worker NPCs from clay, construction sign) | check | study its "placed worker that does a job" NPC loop for totem workers (read only). |
| AutoStorage, HyPipes, AutoSort | mixed | factory-style automation, not SkyBlock-style; not packed (Skyy: shards are the only automation). |
| MGG Biome Selector 1.2.0 | ARR | **STUDY** (section 10): creates a dimension at runtime with `Universe.addWorld` + a `WorldConfigProvider`; no code copied. |
| VoidProtect 1.1.0 (0.7, 220 classes, no items) | check | a 0.7 protection plugin - read its event list to confirm our SkyyIslands guards cover 0.7 (section 10.3). |
| YUNG's HyDungeons, hyrifts, UnstableRifts | ARR / check | instanced worlds through portal keys = proof the instance route works on 0.7-era builds; dungeons spec, not ours. |
| Beacon 2.0.3 (area buffs) | check | shape of "placed block with an area effect + tiers" for Totem Poles; read only. |
| EndlessLeveling, RPGLeveling, MMOSkillTree, ProficiencyLevels | mixed | skill systems with no shard / minion / rebirth feature; SkyySkills stays. |

**No installed or surveyed mod does minions, instanced per-player resource islands, lifelong upgrading tools or rebirth** -> build our own
(SkyyShards + SkyyGear + SkyySkills rounds), folding the two MIT pieces above. Cloud survey leads (research/cloud/Mod-Survey-0.7.md):
AutoFarmer / HyRise (tiered auto-harvest 3x3 .. 7x7) = fold the IDEA of area-by-tier into Harvest Spirit totem tiers.

### 2.2 Our own code (VERIFIED in the live scripts)

| Piece | Where | Reused for |
|---|---|---|
| Tool power ladder, tool rarity + 9 tool stats, `tool.rarityBoost`, Fortune / Wisdom bridge, "[Lv N]" names | SkyyGear 0.2.17-0.2.23 (`GearTool`, `GearRoll.craftDoc`) | lifelong tool stats (5) |
| Upgrade page (same rarity + lines, re-levelled), Reforge tab, multitool merge (best rarity, merged lines), `/smithing` | SkyyGear 0.2.21-0.2.23 (+0.2.24 Anvil tab planned) | tier-up, sigils, points page (6) |
| `DamageBlockEvent` cancel / multiply hook, `BreakBlockEvent` backstop, popup throttle, hoe / sickle marker lock (`tool.farmLock`, built, off) | Tool-Levels-Spec 2.1-2.4; 0.7: event + cancel + re-read unchanged (2.5) | tier gate (4) |
| Per-profile island world `skyy-island-<pkey>` via `Universe.addWorld`, island registry, guards (Damage / Break / Place / Pickup / Use / Drop / UseEntity / Hurt), "(loaded) / (unloaded)" state, evac to hub, starter kit chest | SkyyIslands 0.5.5 | the shard world + protection (9, 10) |
| Block that opens our page on right-click: item json `Interactions.Use = OpenCustomUI {Page: {Id}}` + `OpenCustomUIInteraction.registerSimple`; `PageManager.openCustomPage(Ref, Store, CustomUIPage)` exists in 0.7 | SkyyFishing bench, SkyyMenu item; 0.7 reflection | shard portal menu (9.6) |
| Click-through-effect pattern (interaction `ApplyEffect` marker -> our tick reads the effect) | SkyyFishing 0.1.2 cast click | step-on-pad teleport without a custom interaction type (10.4) |
| Collections credit `coll:fn:add(uuid, id, n<=256, source)` + `bridge.add.sources` whitelist; `skill:fn:addxp` | SkyyCollections 0.2.9, SkyySkills | shard Collect (9.5) |
| Eternal-seed crops regrow (VERIFIED, older spec 2.3); Memories gate eternal seeds world-wide | Assets.zip | eternal plants in shards |
| Soul Orb / Soul Cage weapons | SkyyArmory 0.1.21 | Combat shard Soul Cage totems (9.3) |
| Enchanted materials design (18 ids, `tools/skyyench.py`, Compressing tab, KnowSync) | Gathering-Progression-Spec 4 - **NOT BUILT YET** (`Skyy_Ench` appears 0 times in SkyyCollections 0.2.9) | phase 1 of this spec |

---

## 3. Player flow

### 3.1 First hour
1. Profile created -> SkyyIslands puts the **starter set** in the starter chest (today's `starter.kit` row): Crude Hatchet, Crude Pickaxe,
   Crude Hoe, Crude Sickle, each a SkyyGear tool document with `ll=1` (lifelong), rarity Normal, level 1, 0 points. The tutorial step
   "make crude tools" becomes "take your tools from the chest" (Tutorial-Plan 5 reworded). No tool recipe exists any more (12.1).
2. Chop (Foraging), mine stone / copper (Crude = tier 0, copper ore is "next tier, slow" = vanilla's 8 hits), farm wheat.
3. Hub: the **fishing quest** hands the Crude **Fishing Pole** (lifelong, `ll=1`) + a Wooden Reel + T1 hook / line / sinker, and walks
   through cast / bite / reel. The pole levels with Fishing from then on.
4. First **shard**: the quest line (Tutorial-Plan 24) gives the **Farming Shard** item (Skyy: "the farming shard starts with 1 wheat
   island ... and a single T1 harvest spirit totem"). Place it on your island -> a portal pad. Right-click = shard menu; "Enter" = the
   shard world.

### 3.2 Every day after
- Gather in the overworld with your tier tools; the tool's XP bar fills; spend points on Speed / Fortune / Vein Mine / perks.
- Collection ranks unlock the **Enchanted recipes** (100 ingots / logs / crops -> 1 Enchanted) and the next tier's **armor**; the
  Anvil tier-up eats the Enchanted of the NEW tier (Copper -> Iron = 1 Enchanted Iron Ingot).
- Sigils (boss / quest / event drops, never sold) raise rarity; reforge afterwards to fill the new slots.
- Visit shards to collect (XP + collections), buy islands, grow them, craft / upgrade totems, add shard upgrades.

### 3.3 Rebirth (data only here)
Tools + gathering armor go back to Crude / T1 at level 0, keep rarity, modifiers and points, gain the rebirth modifier line; the
Multitool merge appears on the Anvil after rebirth 1. Shards, islands, totems, storage upgrades stay as they are.

---

## 4. The tier gate

### 4.1 Tiers (tool tier T, material tier M)

| Tier | Pickaxe / hatchet / hoe / sickle / pole material | Live level band (`level.material`, editable) | Tool level cap | Skill level needed to tier UP to it |
|---|---|---|---|---|
| T0 | Crude (spawn) | 1-13 | 13 | - |
| T1 | Copper | 5-18 (Skyy's live edit) | 18 | 5 |
| T2 | Iron | 15-23 | 23 | 15 |
| T3 | Thorium | 20-28 | 28 | 20 |
| T4 | Cobalt | 25-38 | 38 | 25 |
| T5 | Adamantite | 35-43 | 43 | 35 |
| T6 | Mithril | 40-49 | 49 | 40 |
| T7 | Onyxium | 40-49 (**PLACEHOLDER** 45-55 once caps rise with rebirth) | 49 | 45 |

Material tiers M0-M7 per skill are the tables of section 7. **Rule:** tool T vs block M: `M <= T` normal (the live power ladder);
`M = T + 1` slow (power x `gate.nextFactor` 0.25, i.e. about 4x the hits); `M >= T + 2` refused (event cancelled, popup "Needs an Iron
pickaxe" throttled by `tool.popupMs`). No tool in hand = T-1 (bare hands break stone / dirt / crops only; logs and ore refused - the
Stop-Punching-Trees lock). Vanilla's own Quality gates stay underneath (Adamantite ore needs Thorium-or-better quality: consistent,
T3 pick on M5 = two up = refused anyway).

### 4.2 Gate speeds (hits per block, Lv at the tool's band cap, no tree / rolls; from the live ladder, Tool-Levels-Spec 3.3)

| Tool (Lv) | Own tier block | Next tier block (x0.25 power) | Two up |
|---|---|---|---|
| Crude pick Lv 13 | stone 3 | copper ore 3 -> **8** (= vanilla's 8: the tutorial pace) | iron ore refused |
| Copper pick Lv 18 | copper ore 2 | iron ore 3 -> **12** | thorium refused |
| Iron pick Lv 23 | iron ore 2 | thorium ore 4 -> **16** | cobalt refused |
| Thorium pick Lv 28 | thorium 3 | cobalt ~4 -> **14** | adamantite refused (also quality) |
| Cobalt pick Lv 38 | cobalt 2 | adamantite ~6 -> **24** | mithril refused |
| Copper hatchet Lv 18 | Grove log 3 | Autumn / Azure log 3 -> **12** | Savanna refused |
| Iron hatchet Lv 23 | Autumn log 2 | Savanna log 2 -> **8** | Northern refused |

Skyy's words: "your max thorium pick is really slow, until you can upgrade it" - the x0.25 row is that. `gate.nextFactor` is a row
(0.1-1.0); 1.0 = the old speed-only ladder.

### 4.3 Where the gate runs (VERIFIED hooks, 0.7 unchanged)
- Pickaxe / hatchet / shovel / sickle-on-unripe: `DamageBlockEvent` (`GearToolHitSys`): refuse = `setCancelled(true)` (no damage, no
  drop, no XP, no durability); slow = `setDamage(damage x 0.25)`; the block's tier comes from a built-in table `gate.blocks`: ore gather
  types (OreCopper M1, OreIron M2, OreThorium M3, OreCobalt M4, OreAdamantite M5, Rocks-quality-5 Mithril M6) and log block ids per
  tree tier (section 7.2; generated from the trunk ids at build time, asserted against Assets.zip). Crude = T0 breaks stone / dirt /
  sand / clay (M0) normally.
- `BreakBlockEvent` backstop keeps the refusal for other breakers (Tool-Levels-Spec 2.1).
- **Crops (Farming):** soft blocks force damage 1.0 (one hit) - a crop cannot be "slowed", and a ripe-crop sickle harvest fires no
  cancellable event (2.3). So the Farming gate is: **M = T + 1 harvests at half XP and no Fortune; M >= T + 2 refused** through the
  shipped marker pattern (`tool.farmLock`, EffectCondition on the two sickle selectors + the `Hoe_Till` root; client side still
  UNVERIFIED -> probe G1). F-harvest by hand is never gated (bare hand = T-1 = wheat / lettuce only, M0 / M1). Hoe tier also sets the
  **till area** (1 / 3x3 / 3x3 / 5x5 / 5x5 / 7x7 / 7x7 / 9x9 for T0-T7, `hoe.area`) and the sickle tier the **sweep width** (Sickle
  Range stat + `sickle.sweep` 1 / 1 / 2 / 2 / 3 / 3 / 4 / 4).
- **Fishing:** pole T vs fish tier (by zone water, SkyyFishing-Spec-Draft 5): next tier = the fight bar drains 2x; two up = "the line
  snaps" (no catch, the bait is lost). Lives in SkyyFishing's own fight code, no block hook.
- Creative never gated; `tool.staffBypass` as in Tool-Levels-Spec.

---

## 5. Lifelong tools and armor

### 5.1 The one-of-each rule
- Per profile, SkyyGear keeps `lifelong.<kind>` = the item's SkyyGear document uid (kinds: pickaxe, hatchet, hoe, sickle, pole; after
  rebirth 1 also multitool). The document carries `ll=1`, `txp` (tool XP), `up.*` (points spent), `pts` (unspent), `rb` (rebirth
  modifier level), `tier` (T0-T7), plus today's `lvl`, rarity, modifiers.
- Tool **recipes** are removed from every bench and `/craft` (vanilla pickaxe / hatchet / hoe / sickle / rod jsons get
  `KnowledgeRequired: true` with no unlock - the SkyyGear override owner, F20 of the older spec). Shovels keep their recipes.
- **Lost tool** (void, death with drop on, lava): `/smithing` -> "Reclaim" gives the same document back (the item is a view of the
  document, the document is the truth) after a `tool.reclaimCooldown` 600 s; a found duplicate (the old stack reappears from a chest)
  is detected by uid at pickup and turned into a plain `Tool_<kind>_Crude` Normal (no `ll`). Admin `/gearadmin lifelong <player> <kind>`
  re-issues. Death keeps tools (SkyyCoins' death penalty is coins; "gear isnt lost or locked away" - Skyy 2026-10-12).
- Found / looted / admin-given tools (Scrap pickaxe, chest tools, AH): stay plain tools with **today's lenient rule** (Tool-Levels-Spec 7),
  but they get **no points, no tier-up, no sigils** and they are gated by their own material tier like any tool. Nothing is taken away.

### 5.2 Level and stats
- Tool level = `min(skill level, tier cap)` recomputed every second from `skill:<uuid>` (the existing GearTick), never stored as a craft
  level. "[Lv N]" in the name follows it. The power ladder, Fortune per level, rarity boost and the 9 tool stats stay exactly as
  0.2.17-0.2.23 (no new maths).
- Rarity = stat multiplier (`tool.rarityBoost` 0/5/10/15/20/25 Normal..Mythic, live) + modifier slot count (`rarity.<id>` 1-6, live) +
  better roll bounds (live). Raising rarity with a Sigil adds the new slots EMPTY -> the next Reforge fills them ("you'll want to
  reroll your tool after every rarity upgrade").

### 5.3 Three farming skills, one tree (SkyySkills + SkyyTrees)
| Skill | XP from | Shard | Tool |
|---|---|---|---|
| Farming | crops (today's Farming XP table) | Farming Shard (Sprites) | hoe + sickle |
| Ranching | milking / shearing / egg pickup / slaughter drops of farm animals (counting hooks: `InteractivelyPickupItemEvent` for drops + `UseEntityEvent` on a farm animal - the SkyyIslands GuardUseEntity hook proves the event; **UNVERIFIED** which vanilla animal interactions give items -> probe R1) | Ranching Shard (Herd Spirits) | shears / bucket (plain items, no level) |
| Orchard | fruit from trees: vanilla Apple + NoCube's Orchard fruit ids (pack mod, by id) + saplings planted | Orchard Shard (Dryads) | hatchet (Orchard logs count as Foraging, fruit as Orchard) |

`skill:<uuid>` publishes all three plus a derived **Farming (avg)** = floor((F + R + O) / 3) used by: the Farming tree (SkyyTrees reads
the average as the tree's level), farm armor level, the hoe / sickle level cap, collection XP rewards marked `xp:Farming` (paid to
Farming). The HUD skill list shows "Farming 12 (F 15 / R 9 / O 12)". Overall Level counts the three as one skill at the average (no
inflation). Rebirth points: one Farming branch (shared tree) fed by all three XP pools.

### 5.4 Fishing
- New skill **Fishing** (SkyySkills, own curve = Foraging's), own tree (SkyyTrees: Fortune, bite speed, double catch, treasure chance,
  sea-creature damage later), own rebirth branch.
- The **pole** is the lifelong tool: SkyyFishing's `SkyyFishing_Rod_<Tier>` ids become the pole's tiers (T0 Crude / Wooden, T1 Copper
  ... as the rod ladder of SkyyFishing-Spec-Draft 4.1: rod = max weight). Reel, hook, line, sinker stay crafted parts (Fishing Bench,
  as built) and are rigged onto the pole; they wear / get replaced as you progress. Pole level = Fishing level capped by tier; tier-up
  = Enchanted metal of the tier + 10 of the tier's wood category (**PLACEHOLDER**).

### 5.5 Gathering armor
Mining / Foraging / Farming / Fishing sets (older spec 3.4-3.5 tables stay for ingredients and looks): level = skill level capped by
the tier band; tier up on the Anvil (Upgrade action) with Enchanted of the new tier (per piece: head 1 / chest 2 / legs 2 / hands 1 of
the older "6 per set" rule; E-curve ores 1 / 1 / 1 / 0); keeps rarity + rolls; sigils apply; rebirth -> T1 keeping rarity. The first
set of each skill is still **crafted** once (collection unlock), after that only upgraded. Combat armor / weapons unchanged.

---

## 6. The Anvil (`/smithing`, one tab) - actions on a lifelong tool / armor piece

| Action | Cost | Rule |
|---|---|---|
| **Tier up** | section 6.1 + `tool.tierCoins` (coins per tier: 100 / 500 / 2,000 / 5,000 / 15,000 / 40,000 / 100,000 **PLACEHOLDER**) | needs the skill level of the new tier (4.1); keeps rarity, lines, points, XP; new item id of the tier (the live Upgrade page re-levels, VERIFIED) |
| **Rarity** (Sigil) | 1 Sigil of the target rarity | upward only; skips tiers; new slots empty; works on any item with a rarity (tools, armor, weapons, accessories later) |
| **Reforge** | today's coin cost | unchanged (fills empty slots) |
| **Upgrade Points** | points | section 6.3 |
| **Multitool merge** | pickaxe + hatchet (same tier) | after rebirth 1 only; result keeps the BEST rarity, merged lines, the SUM of points of both (no stat loss - Skyy 2026-10-12 replaces the 0.2.18 85 % / 70 % penalty; those rows go to 100 / 100 and the merged tool counts as both kinds for levels and gates: Mining level for rock, Foraging for logs) |
| **Reclaim** | free after cooldown | 5.1 |

### 6.1 Tier-up costs (Enchanted = 100 base, bags.md 2026-10-06)
| Step | Pickaxe / hatchet / hoe / sickle / pole | Armor piece (Head / Chest / Legs / Hands) |
|---|---|---|
| T0 Crude -> T1 Copper | **25 Copper Ingots** (no Enchanted yet - Zone 1 first hour; question 1) | first set crafted, no step |
| T1 -> T2 Iron | 1 Enchanted Iron Ingot | 1 / 2 / 2 / 1 Enchanted Iron |
| T2 -> T3 Thorium | 1 Enchanted Thorium Ingot | 1 / 2 / 2 / 1 |
| T3 -> T4 Cobalt | 2 Enchanted Cobalt Ingots | 1 / 1 / 1 / 0 (R curve) |
| T4 -> T5 Adamantite | 2 Enchanted Adamantite Ingots | 1 / 1 / 1 / 0 |
| T5 -> T6 Mithril | 3 Enchanted Mithril Ingots (needs the Zone 4 veins, older spec Q6) | 1 / 1 / 1 / 1 |
| T6 -> T7 Onyxium | 3 Enchanted Onyxium (Zone 5 / later) | later |
Hatchets take the Enchanted KEY LOG of the tree tier instead (Maple / Gumboab / Redwood / Sallow / Zone-5 wood), hoes + sickles the
Enchanted key CROP (Carrot / Cauliflower / Pumpkin / Tomato / Cotton / Potato), the pole the metal + wood above. "Harder than crafting":
a fresh Iron pickaxe used to cost ~3 bars; 1 Enchanted Iron = 100 bars.

### 6.2 Sigils (`Skyy_Sigil_<Rarity>`, never sold on the Bazaar / NPC shops, AH allowed - question 3)
| Sigil | Sources (PLACEHOLDER rows in the loot tables) |
|---|---|
| Unique Sigil | collection tier VI rewards (one per key collection), hub quest chain, event crates (keys earned) |
| Rare Sigil | Zone 2+ zone bosses, slayer tiers, Lost Loot (rare) |
| Legendary Sigil | Zone 3+ bosses, capstone dungeon floors, guild games |
| Fabled Sigil | Zone 4 bosses (rare), rebirth shop |
| Mythic | no sigil - Mythic stays boss-only items (question 3) |

### 6.3 Tool XP and Upgrade Points
- **Tool XP** = every skill XP point earned with that tool in hand (same number the player sees; shard Collect XP does NOT count - no
  tool in hand). Bar size for point n = `pts.base` 300 x `pts.growth` 1.18^n (PLACEHOLDER: point 1 at 300 XP, point 10 at ~1,600,
  point 25 at ~18,000; a Zone 1 player gets ~6 points in the first hours, a maxed tool ~35). The bar + points show on the tooltip and
  the Anvil.
- **Perks** (per tool kind; `up.<key>` levels; rows `pts.cost.<key>` and `pts.max.<key>`):

| Perk | Tools | Per level | Max | Cost per level | Needs |
|---|---|---|---|---|---|
| Speed (Power) | pick / hatchet / multitool | +2 % power (same stat as the roll, after it) | 10 | 1 | - |
| Fortune | all incl. hoe / sickle / pole (Fishing Fortune) | +1 Fortune | 10 | 1 | - |
| Wisdom | all | +1 % skill XP | 5 | 2 | T2 |
| Vein Mine / Tree Feller | pick / hatchet | +1 level (stacks with the tree; total cap 8 = the lock) | 3 | 3 / 5 / 8 | T2 / T3 / T4 |
| Magnet | pick / hatchet | drops fly to you (radius 2 / 4 / 6) | 3 | 2 | T2 |
| Wide Till / Wide Sweep | hoe / sickle | +1 ring of area / +1 sweep width (on top of the tier area, 4.3) | 2 | 3 | T2 |
| Green Thumb | hoe | chance to auto-replant 25 / 50 / 100 % | 3 | 3 | T3 |
| Auto-Smelt | pick | ore -> ingot (Skyy: "a really late game tree upgrade" - the tool perk mirrors it) | 1 | 10 | T5 + Adamantite collection VII |
| Steady Line | pole | bar drains 10 / 20 / 30 % slower | 3 | 2 | T2 |
| Rebirth modifier | all | set by the rebirth tree, not points (`rb`) | - | - | rebirth 1 |

Points are never refunded except by `/smithing` "Reset points" for `pts.resetCoins` 5,000 x spent points (question 6).

---

## 7. Material tier tables (proposal; zones / ids VERIFIED in the older spec, Zone 5 PLACEHOLDER)

### 7.1 Ore (Mining) - tool tier that mines it normally
| M | Ore | Zone | Normal from | Slow with | Enchanted |
|---|---|---|---|---|---|
| M0 | stone, cobble, dirt, sand, clay, gravel | all | T0 (and bare hands) | - | Cobblestone / Rubble |
| M1 | Copper | 0-3 | T1 Copper | T0 Crude | Copper Ingot |
| M2 | Iron (+ Silver / Gold side ores) | 0-4 | T2 Iron | T1 | Iron Ingot |
| M3 | Thorium | 2 | T3 | T2 | Thorium Ingot |
| M4 | Cobalt | 3 (+4 boulders) | T4 | T3 | Cobalt Ingot |
| M5 | Adamantite | 4 | T5 | T4 (quality 4 OK) | Adamantite Ingot |
| M6 | Mithril | Zone 4 deep veins (SkyyWorldGen, older Q6) | T6 | T5 | Mithril Ingot |
| M7 | Onyxium | Zone 5 (later) | T7 | T6 | Onyxium Ingot |

### 7.2 Wood (Foraging) - 5 zone tiers (older spec 2.2, key log bold)
| M | Tier | Logs | Zone | Normal from | Enchanted |
|---|---|---|---|---|---|
| M1 | Grove | **Oak**, Birch, Beech, Ash, Aspen | 1 | T1 Copper (T0 slow) | Oak |
| M2 | Autumn / Azure | **Maple**, Azure | 1 (tier 3) | T2 Iron | Maple |
| M3 | Savanna | **Gumboab**, Dry, Bottletree, Palo | 2 | T3 Thorium | Gumboab |
| M4 | Northern | **Redwood**, Fir, Cedar, Poisoned, Spiral | 3 | T4 Cobalt | Redwood |
| M5 | Wastes | **Sallow**, Burnt, Petrified, Bamboo, Camphor, Banyan, Jungle, Blue Fig, Fire, Crystalwood | 4 | T5 Adamantite | Sallow |
| M6 / M7 | Zone 5 woods (Starblight / own) | later | 5 | T6 / T7 | later |
Orchard trees (Apple, NoCube fruit trees, Amber, Frostwood, Stormbark, Windwillow, Wild Wisteria) = M1 for the hatchet; their FRUIT pays
Orchard XP.

### 7.3 Crops (Farming), animals (Ranching), fruit (Orchard)
| M | Farming pair (vanilla bench order) | Hoe / sickle normal from | Ranching | Orchard |
|---|---|---|---|---|
| M1 | **Wheat**, Lettuce | T0 Crude (M1 slow = half XP) / T1 | Chicken (eggs, feathers, meat) | Apple, Wild Berries |
| M2 | **Carrot**, Corn | T2 | Pig (meat, hide) | Pear, Plum (NoCube) |
| M3 | **Cauliflower**, Turnip | T3 | Sheep (wool, meat) | Orange, Lemon, Mandarin |
| M4 | **Pumpkin**, Aubergine | T4 | Cow (milk, beef, leather) | Peach, Apricot |
| M5 | **Tomato**, Chilli | T5 | Zone 3 beasts (Wildmeat) | Persimmon, Pomegranate |
| M6 | **Cotton**, Rice | T6 | Zone 4 (later) | Amber / Frostwood fruit (later) |
| M7 | **Potato**, Onion | T7 | later | later |
Ranching has no tool tier: its gate is the animal's collection + Ranching level to buy / breed the tier (`ranch.level` 1 / 10 / 20 /
30 / 40). Seed / sapling / animal recipes stay collection-locked as the older spec 3.5 (Bazaar buy-lock F21).

---

## 8. Data model per profile (`tools/PROFILES-CONTRACT.md`: every file keyed by `pkey(u)`)

| Mod | File / key | Fields |
|---|---|---|
| SkyyGear | item documents (existing per-item store) | + `ll` 1, `tier` 0-7, `txp` long, `pts` int, `up.<key>` int, `rb` int, `kind`; per profile `lifelong/<pkey>.properties`: `pickaxe=<uid>`, `hatchet=`, `hoe=`, `sickle=`, `pole=`, `multitool=`, `migrated=1` |
| SkyySkills | `players/<pkey>.properties` | + `xp.Fishing`, `xp.Ranching`, `xp.Orchard`; bridge `skill:<uuid>` gains Fishing / Ranching / Orchard / FarmingAvg |
| SkyyTrees | `players/<pkey>.properties` | + Fishing tree nodes; Farming tree unchanged (level = the average) |
| SkyyFishing | rig per pole uid (today: per rod item) | reel / hook / line / sinker ids + wear on the POLE document (`rig.*`) |
| **SkyyShards** (new) | `shards/<pkey>.properties` | `world=skyy-shard-<pkey>`, per shard `s.<kind>.placed=<island world>:<x,y,z>` or `inventory`, `s.<kind>.storageTier`, `s.<kind>.upgrades=compactor:2,compressor:1`, per island `i.<kind>.<slot>.type=<crop/ore/log/animal/mob>`, `.size=1-3`, `.lastRun=<epoch s>`, `.stored=<item:count,...>`, per totem `t.<kind>.<slot>.<n>=<type>:<tier>:<mod1>,<mod2>:<booster>:<x,y,z>`; `v=1` |
| SkyyIslands | island registry | + `shard.world=<name>` (protected like `world.old`), guards read `shard:fn:allowed(world, action, blockId)` from the bridge |
| Rebirth (later) | own mod | reads / writes `rb`, resets `tier`, `lvl` via `gear:fn:rebirth(uuid)` |

Bridge keys (java.lang types only): `shard:fn:allowed` (Function Object[]{String world, String action, String blockId} -> Boolean),
`shard:fn:collect` (internal), `gear:fn:lifelong` (Function Object[]{UUID, String kind} -> String uid or null), `gear:fn:toolxp`
(BiConsumer-like Function Object[]{UUID, String skill, Integer xp} -> Boolean; SkyySkills calls it on every XP grant with a held tool).
Deleting a profile archives the shard world folder with the island (SkyyProfiles 0.1.5 rules), never deletes.

---

## 9. Shards (SkyyShards)

### 9.1 Shape (locked)
- Six shard ITEMS: Mining, Foraging, Farming, Ranching, Orchard, Combat Shard (`Skyy_Shard_<Kind>`), each a placeable portal block on
  the owner's island (model: the vanilla `Platform_MagicInactive` pad look recoloured per kind - the Portal_Device model, our texture).
  Pick it up = right-click "Pick up" in its menu (never by breaking: `GatherType: Unbreakable`); its state lives in the file, not the
  block, so moving is free.
- ONE private **shard world** per profile (`skyy-shard-<pkey>`, Void worldgen, `setSpawningNPC false`, `setBlockTicking true` for
  crops, `setSavingPlayers true`, `setDeleteOnRemove false`), created on the first shard placement like island worlds. Each shard kind
  owns a **region** 1,024 blocks apart (Mining at 0,0; Foraging 1024,0; ... on a ring) so one world holds all six (question 7:
  one world vs six). Each region = **hub island** (arrival pad, exit pad, menu totem) + **6 fixed slots** on a hexagon 48 blocks out,
  each with a pre-made **bridge prefab** that appears when the slot is bought and an **island prefab in 3 sizes** (Small 13x13, Medium
  21x21, Large 29x29 - the bigger one contains the smaller one, grown in place by pasting the next prefab centred on the same point).
  Any island type in any slot; no order lock (Skyy's popup). Start: slot 1 filled (Farming: Wheat Small + T1 Harvest Spirit Totem).
- Everything there is **protected**: SkyyIslands' guards (Damage / Break / Place / Pickup / Use / Drop / UseEntity / Hurt, VERIFIED on
  island worlds) run with the shard rule: allowed = harvesting a resource block of the island's type with a tool (crop / ore / log /
  animal), placing and picking up `Skyy_Totem_*` blocks on the island's totem pads, using the pads and menus; everything else
  cancelled. The owner and co-op members (island co-op list) may enter; visitors may not (question 8).
- **Eternal plants / nodes:** crops are the vanilla ETERNAL variants (regrow, VERIFIED); ore nodes and trees regrow by our timer
  (`shard.regrowSec` 90, the Ore-Regrow cloud draft's approach: a regrow task re-sets the block); Ranching animals respawn
  (`shard.animalRespawnSec`); Combat mobs come from Soul Cage totems. Manual gathering in the shard pays normal XP / collections at
  once (it is you breaking it); the totems' production is paid at **Collect**.

### 9.2 Production, storage, Collect (lazy, no ticking - Pocket-Shards-Spec 8 kept)
- Per island: `rate` items / min = base rate of the island type x size factor (1 / 1.6 / 2.4) x sum of totem worker rates in range x
  shard upgrades (time compressor). `lastRun` + `stored`; on any menu open / Collect: `elapsed = min(now - lastRun, shard.maxOffline
  3 days)`, `stored += floor(elapsed x rate)`, capped by the **shard storage** (`storage.tier` 1-5: 1 / 3 / 6 / 12 / 24 stacks of 100
  per island, upgraded in the shard menu for Enchanted + coins). Full = the island's totems play a "sleeping" animation when loaded.
- **Collect** (menu button, per island or all): items go storage-first into Magic Bags / inventory (count before and after - the
  AGENT-BRIEF rule), then `skill:fn:addxp` pays the skill's XP (`shard.xpPercent` 50 % of the overworld XP per item - Skyy: collections
  AND xp are gained on collect; the half keeps real play ahead) and `coll:fn:add` credits collections in chunks of 256 (source
  `shard`, whitelisted). Combat shard Collect pays Combat XP 0 % (drops only, like SkyBlock) - question 9.
- **Auto-compactor** (shard upgrade I / II): stored items turn into their Enchanted form at 100 (I) and the collection credit is the
  base amount (the older spec 4.2 alias rule). **Time compressor** (I-III): rate x1.25 / 1.5 / 2.0 - costs Void essence (Zone bosses)
  + coins. **Booster** slot on the shard (not the totem): an Enchanted item burns 24 h for +10 % rate (optional, Skyy's "no fuel").

### 9.3 Totems (one system, themed workers)
| Shard | Worker (model) | Totem types (farming list = Skyy's 12, kept) |
|---|---|---|
| Farming | **Sprites** (small glowing wisps - Fairy Grove look) | Harvest Spirit (auto-harvest, the starter), Rain (water, from MoreTotems' Water Totem, MIT), Fertilizer, Blessing of the Sun, Fairy Grove, Season Ward, Scarecrow / Guardian, Pollinator, **Harvest Moon**, Compost, Mushroom / Shade |
| Ranching | **Herd Spirits** | Herd / Ranch Pole (breeding, more wool / eggs / milk) + Harvest Spirit (collects) + Scarecrow |
| Orchard | **Dryads** | Harvest Spirit (fruit), Rain, Fertilizer, Pollinator, Season Ward |
| Foraging | **Treants** | Lumber Spirit (= Harvest Spirit for logs), Sap Tap (+Tree Sap), Fertilizer (regrow faster) |
| Mining | **Golems** (vanilla golem recolours; Kami OreGolems looks if licensed) | Quarry Spirit (= Harvest Spirit for ore), Auto-Smelt Pole (ingots), Geode Pole (rare gem chance) |
| Combat | **Soul Cages** (SkyyArmory soul tie-in) | Soul Cage Totem (needs a Soul Orb of the mob kind: spawns that mob on the arena island; the worker "harvests" kills -> drops only), Lure Pole (+spawn rate), Trophy Pole (+rare drop) |

Rules (locked + proposal): no fuel; **tier up on the Anvil Upgrade action** (Totem I -> Totem Pole II -> Grand Pole III -> Ancient Pole
IV -> Mythic Pole V; costs Enchanted of the shard's material + Essence: 1 / 2 / 3 / 5 / 8 Enchanted + 10 / 25 / 50 / 100 / 200 Life or
Soul Essence, PLACEHOLDER); range 3 / 5 / 7 / 9 / 11 blocks radius (a Small island is 13 wide - the starter T1 cannot cover it, Skyy:
"farm is bigger than the spirits range so you can go in there and manually farm too"); worker rate 1 / 1.6 / 2.4 / 3.5 / 5 items / min
(base, PLACEHOLDER, Server Setup); **2 upgrade slots** (modifiers: Wider Area +2, Faster +20 %, Auto-Replant, Compost, Storage +3 stacks,
Rare Finder; crafted items `Skyy_TotemMod_*`) + **1 optional booster slot** (Life / Water / Soul Essence: +area +growth for 1 h real
time). **Right-click a placed totem** = its page: info (tier, workers, rate, range circle shown as particles for 10 s), Upgrade
(opens the Anvil with it), Modifiers (2 slots), Pick up. Harvest Moon rule: at night only, +25 % crops, and an **extremely low**
chance (`moon.enchChance` 0.05 %) of an Enchanted crop; the sickle's **Moon Blade** modifier (new roll, scythe / sickle pool) multiplies
that chance x2-x5. Totem items: `Skyy_Totem_<Type>` with a tier document (SkyyGear document, no rarity - question 10).

### 9.4 Islands: buy, grow, cost (per shard; 3 sizes at launch = Skyy's "3 lvs max to start")
| Step | Cost (PLACEHOLDER rows `island.<kind>.cost.*`) | Needs |
|---|---|---|
| Buy a slot's island (type chosen from the shard's list) | 100 of that material (Wheat / Copper ore / Oak log / Chicken feed / Apple / a Soul Orb) + coins 1,000 x slot number | the material's collection I; Combat: the Soul Orb of the mob |
| Small -> Medium | 8 Eternal Seeds of the crop (Farming / Orchard sapling / Ranching feed) or 2 Enchanted of the material + coins 5,000 | the collection IV |
| Medium -> Large | 24 Eternal Seeds or 5 Enchanted + coins 20,000 | the collection VI |
Eternal Seeds stay the vanilla Memories-gated recipe (world-wide gate, older spec 2.3) - so Medium needs some exploration first.

### 9.5 Shard menu (one custom page, the SAME page from the portal on the main island and from the hub totem inside)
Tabs: **Overview** (all six shards: placed / not, storage fill, "Enter" button per placed shard), **Islands** (slots as a hexagon map
with size + type, Buy / Grow), **Totems** (list per island, tier, slots), **Collect** (per island counts, Collect all), **Upgrades**
(storage tier, compactor, time compressor, booster slot), **Pick up shard**. Vanilla look through `tools/skyyui.py`; the cloud draws the
mockup first (ui.md 2026-10-13), local review, then build.

### 9.6 Entering and leaving (engine: 10.4)
"Enter" button -> `Universe.addWorld` if unloaded -> `transferPlayerAsync` to the region's arrival pad (the SkyyIslands `/island`
pattern, VERIFIED). Stepping on the pad (CollisionEnter -> marker effect -> our tick) is the second way. Exit pad / "Leave" -> back to
the island at the portal. On disconnect inside a shard the next login routes home (the SkyyIslands login router). Empty shard world
-> unload after `shard.unloadSec` 120 (our own idle check -> `Universe.removeWorld(name)` keeps the folder; VERIFIED pattern = island
"(unloaded)" state).

---

## 10. Engine (Hytale 0.7.0) - what is proven, what is not

### 10.1 Private worlds per player (VERIFIED)
- `Universe.addWorld(String)`, `addWorld(String, String, String)`, `makeWorld(String, Path, WorldConfig[, boolean])`, `loadWorld`,
  `removeWorld(String)`, `removeWorldExceptionally`, `isWorldLoadable`, `getWorlds()`, `transferPlayerAsync(PlayerRef, World, ...)`
  (0.7 jar reflection). SkyyIslands 0.5.5 already makes one world per profile this way, and MGG Biome Selector creates its dimensions
  with the same calls (`addWorld`, `getWorld`, `isWorldLoadable`, `validateWorldPath`, a `WorldConfigProvider` that sets
  `VoidWorldGenProvider` / `GlobalSpawnProvider` / `setCanSaveChunks` / `setSaveNewChunks` - its constant pool, no code copied).
- `WorldConfig` has `setSpawningNPC`, `setBlockTicking`, `setSavingPlayers`, `setCanUnloadChunks`, `setDeleteOnRemove`,
  `setGameTimePaused`, `setPvpEnabled`, daytime / nighttime duration overrides (time compressor could even run real faster days -
  not needed, production is math).
- Vanilla **instances** (`InstancesPlugin.spawnInstance(asset, world, transform)`, `Server/Instances/<name>/instance.bson` with
  `RemovalConditions` WorldEmpty / IdleTimeout / Timeout and `DeleteOnRemove`, `InstanceWorldConfig.setRemovalConditions`,
  `Instance_Gateway` block = `BlockEntity.Components.InstanceConfig` + `Use: OpenCustomUI ConfigInstanceBlock`) are a second route:
  a shard region could be an instance asset spawned per player. Rejected for v1: instances are built for throw-away dungeons
  (removal on empty, no per-player persistence by name); `addWorld` with a named folder is what islands use and persists.

### 10.2 How many, load / unload cost (partly UNVERIFIED)
- `World extends TickingThread` (VERIFIED): **one Java thread per LOADED world**. Unloaded worlds cost disk only. So the limit is
  loaded worlds = players currently inside shards (one world per profile, 9.1) + loaded islands; a 50-player server with half in
  shards = ~75 world threads. **UNVERIFIED** how that ticks on Skyy's host -> probe S1: smoke-test server, create 40 void shard worlds
  with one Small island each, measure RAM and tick time (`World.getBufferedTickLengthMetricSet`), then unload them with
  `removeWorld` and confirm the folders stay and re-load. Load cost of a void world with ~4 chunks of prefab is expected small (an
  island world loads in ~1 s today - SkyyIslands log lines).
- Unload trigger: `WorldEmptyCondition` exists only for instances; for plain worlds we run our own idle check (`World.getPlayerCount()`
  VERIFIED) -> `Universe.removeWorld(name)` (**UNVERIFIED** that it saves chunks first and keeps the folder when `DeleteOnRemove`
  is false -> probe S2: fill storage, remove, re-add, read back).

### 10.3 Protection (VERIFIED pattern, 0.7 port in progress)
SkyyIslands' guard systems on `DamageBlockEvent`, `BreakBlockEvent`, `PlaceBlockEvent`, `InteractivelyPickupItemEvent`,
`UseBlockEvent$Pre`, `DropItemEvent$PlayerRequest`, `UseEntityEvent$Pre` and the damage filter are live and cancellable; the 0.7
crosscheck lists none of them as missing (only chunk / block accessors moved - the island port fixes those). VoidProtect 1.1.0 (0.7,
220 classes) is the cross-check: read its event list for anything 0.7 added (e.g. fluid / explosion events) -> probe P1 (desk).

### 10.4 Portal block with a right-click custom page (VERIFIED) + step-on teleport (pattern VERIFIED, 1 s latency)
- Right-click page: item json `BlockType.Interactions.Use = [{Type: OpenCustomUI, Page: {Id: "SkyyShardMenu"}}]` +
  `OpenCustomUIInteraction.registerSimple(id, supplier)` - exactly how the SkyyFishing bench and the SkyyMenu item open their pages;
  vanilla's own `Portal_Device` opens its summon page the same way (built-in packets `OpenPortalSummonPage`, not reusable for our
  content). `PageManager.openCustomPage(Ref, Store, CustomUIPage)` + `handleLegacyCustomPageEvent` exist in 0.7 (the port replaces
  `handleEvent`).
- Step-on: vanilla pads use `CollisionEnter` interactions of built-in types (`HubPortal`, `ExitInstance`, `TeleportInstance`,
  `PortalReturn`). A mod cannot add a new interaction Type from javassist code (**UNVERIFIED** - the interaction codec registry may be
  open; probe S3), so v1 uses `CollisionEnter -> ApplyEffect Skyy_Shard_Enter` and our 1 s tick teleports players carrying the effect
  (the SkyyFishing click pattern). "Enter" in the menu is instant either way.
- **UNVERIFIED**: `OpenCustomUI` on a block whose item carries a SkyyGear document (the shard keeps no document - state is in the
  file, so no issue); block placement of a custom block model with our texture draws (SkyyMenu item is an ITEM model; a BLOCK with
  `CustomModel` + our PNG -> probe S4 in the UI probe pack).

### 10.5 Pasting island prefabs and regrowing blocks (UNVERIFIED on 0.7)
Island / bridge prefabs need block writes: 0.7 moved them to `BlockOperations.setBlock(ChunkStore, Ref, x, y, z, ...)` (Hytale-0.7-Port
probe). The Islands port lands this first; SkyyShards reuses the same helper (`skyy.bridge` `islands:fn:setBlock`, or a shared
a new shared block-access helper (planned skyyblocks.py)). Prefab format: the SkyyIslands starter-island fill (block list) - VERIFIED technique on 0.6, 0.7 after the port.
Alternative: vanilla prefab files (`.prefab`) through `PrefabEditSession` - not probed.

### 10.6 Worker NPCs (UNVERIFIED, cosmetic only)
Workers are visual: a looping NPC (vanilla golem / recoloured wisp) wandering the island while loaded. Spawning a named NPC at a point
with a tether = the SkyyMerchants / SkyyTownProbe NPC spawn code (VERIFIED on 0.6, port pending). If NPC spawn is late, v1 ships totems
with particles only (Fairy Grove dots) and adds workers in the totem round.

---

## 11. Build phases (each = one round; versions derived from the live SET, shift if another round lands first)

| Phase | Round type | Mods | Scope | Harness / tests |
|---|---|---|---|---|
| **0. 0.7 port** (running) | - | all | prerequisite: Islands + block API, PageManager | crosscheck 0 fails, smoke PASS |
| **1. Enchanted** | full (economy) | SkyyCollections 0.2.10, SkyySkills 0.4.31, SkyyBazaar 0.1.8, SkyySacks 0.7.18, shared `tools/skyyench.py` | the older spec phase A exactly (18 items at ratio 100, ingots for metals, Compressing tab, KnowSync, Bazaar rows at base x100, bag homes) | older spec A harness (T1-T3), LP loop check |
| **2. Skills split** | full (saved data) | SkyySkills 0.4.32, SkyyTrees 0.3.6, SkyyHud 0.3.19, SkyyCollections 0.2.11 | Fishing / Ranching / Orchard skills + XP hooks (probe R1 first), Farming average, Fishing tree, HUD lines, collection XP routing | XP math unit model; bridge `skill:<uuid>` new keys; a profile file without the keys loads as 0 |
| **3. Lifelong tools + tier gate** | ultracode (new system, items) | SkyyGear 0.3.0 (from 0.2.24), SkyyIslands 0.5.7 (starter set), SkyyFishing 0.2.0 (pole = lifelong), SkyyTrees 0.3.7 (points stack rule), SkyySacks (recipe hide) | 4, 5, 6 without sigils / multitool; migration 12.1; tool XP + points page; recipes locked | gate matrix test (every tool tier x block tier = normal / slow / refused, popup counts); one-of-each guard (dupe by uid); points never lost on tier-up; reclaim; lenient old tools; TEST steps for Skyy |
| **4. Sigils + armor levels** | full | SkyyGear 0.3.1, SkyyArmory / loot tables (sigil drops), SkyyCollections (Unique Sigil rewards) | 6.2 + 5.5 | sigil skips tiers, slots empty then reforge fills; armor tier-up keeps rarity; never sold (Bazaar assert) |
| **5. SkyyShards 0.1 - worlds + Farming shard** | ultracode | NEW SkyyShards 0.1, SkyyIslands 0.5.8 (guard bridge, co-op entry), SkyyMenu (hub button) | shard world, Farming region, hub + 6 slots, Wheat island 3 sizes, Harvest Spirit T1, storage, Collect, menu (cloud mockup first) | probes S1-S4 before build; conservation (collect = stored, items before / after), offline math unit test, protection matrix, unload / reload keeps storage |
| **6. SkyyShards 0.2 - totems** | ultracode (art + NPC) | SkyyShards 0.2, SkyyGear (totem tier-up on the Anvil), SkyyArmory (Soul Cage link) | all totem types, tiers, slots, booster, right-click page, workers (or particles), Harvest Moon + Moon Blade roll, MoreTotems Water fold | rate math vs range; slot items; pick-up returns the exact tier document |
| **7. SkyyShards 0.3 - the other five shards + upgrades** | full x2 | SkyyShards 0.3, SkyyWorldGen (Mithril veins if not yet) | Mining / Foraging / Orchard / Ranching / Combat regions, compactor, time compressor, Combat Soul Cages | same harness per kind; Combat drops only |
| **8. Rebirth** | own spec | rebirth mod + SkyyGear (`gear:fn:rebirth`), Multitools fold (models, credit) | rebirth modifier, Multitool merge unlock, armor T1 reset | - |
| later | - | Zone 5 tiers (T7 / M7), Mythic sigil question, gems (research/Gems-Ideas.md) | | |

Phase 3 needs 1 (Enchanted exists) and benefits from 2 (pole levels with Fishing; without 2 the pole follows Foraging as a stopgap -
avoid: run 2 first). 5-7 need 0 (block API) and 3 (tier gate rules inside shards). Each round pins + deploys as one set with the
rollback floors: SkyyGear 0.3.0 becomes a floor once a lifelong document exists (older tools would lose `ll` fields on rollback - they
keep working as plain tools, but the one-of-each registry must be rebuilt by the migration again); SkyyShards 0.1 is a floor once a
shard world exists (`removeWorld` leaves the folder, a rollback hides it).

---

## 12. Migration (never take anything away)

### 12.1 Tools players already own (crafted, rolled, several per kind)
On the first login after phase 3 (once per profile, `migrated=1`): for each kind the **best** owned tool across inventory + Magic Bags
+ Requip pool + Vault (order: highest rarity, then highest level, then most modifier lines) becomes the lifelong one (`ll=1`, its
rarity / lines / level kept; tier = its material; no points yet). A player with NO tool of a kind gets a fresh Crude Normal one in the
inventory (storage-first). All other tools stay usable as plain tools (lenient rule, no tier-up / points / sigils) and can be
salvaged for their vanilla outputs; multitools owned today keep working the same way until rebirth 1 (their recipes vanish with the
pack mod; Skyy's 2026-10-12 open point). A chat line + one popup explains it once; the Anvil shows "Lifelong" on the chosen tool. A
player who disagrees with the pick can run `/smithing` -> "Make lifelong" ONCE within 7 days on another owned tool of that kind
(`tool.repickDays` 7) - the first pick goes back to plain.

### 12.2 Other data
- Skill files: new XP keys default 0; Farming XP stays Farming; nothing moves. Collection counts untouched.
- SkyyGear config rows: the 0.2.18 multitool penalty rows (speed 85 / fortune 70) rewrite to 100 / 100 only if untouched (one-time
  setting migration rule, Undo line); `tool.gate` turns on with the gate rows at their defaults.
- Starter chest row `starter.kit`: the four Crude tools are added only if the row still holds the default (same rule).
- Enchanted items: as the older spec 7 (floor SkyyCollections 0.2.10 once deployed).
- No shard data exists yet; the shard world is created on first placement.

---

## 13. Risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| World threads per player | one thread per loaded shard world; 50+ loaded worlds could stutter | ONE world per profile (not six), unload after 120 s empty, probe S1 before phase 5, `shard.maxLoaded` cap with a queue message |
| Lost / duplicated lifelong tool | the only tool of its kind; a dupe through a crash window or chest copy would break "one" | document uid is the truth; pickup dedupe; Reclaim; `profile:busy` respected; crash journal like Wardrobe |
| Gate feels like a wall | Skyy wants "smooth"; a refused popup every swing is noise | next tier is slow not refused; popup throttled; tooltip "Breaks in" shows the hits; Enchanted cost visible on the Anvil early |
| Farming cannot be slowed | soft blocks one-hit; the sickle gate depends on the UNVERIFIED client marker | ship the Farming gate as XP / Fortune first; the hard refusal only after probe G1 |
| Enchanted first (phase 1) was never built | every tier-up cost depends on it | phase 1 is the first round of this spec; nothing in 3+ builds without it |
| Shard XP inflation | collect XP + collections from automation can outpace play | 50 % XP, storage caps, offline cap 3 days, time compressor max x2, Combat pays no XP; economy audit re-run (research/cloud/Economy-Audit.md) |
| Prefab writes on 0.7 | block API moved | Islands port first; shared helper |
| Ranching / Orchard hooks unknown | which vanilla animal interactions give items | probe R1 in phase 2; Ranching XP from pickups only until proven |
| Sigils as a paid-perk magnet | rarity items are the riskiest reward | never sold, keys earnable (economy.md 2026-10-11) |
| 0.7 pack mods (Multitools, MoreTotems) may not load until updated | folds depend on their assets | fold = copy MIT assets into our jars with credit, so the pack mods are not needed |

---

## 14. Questions for Skyy (each with the recommended default)

| # | Question | Default |
|---|---|---|
| 1 | Crude -> Copper tier-up cost: 25 Copper Ingots (first hour, no Enchanted yet) or 1 Enchanted Copper Ingot (100 ingots) like every other step? | **25 ingots** |
| 2 | Tool XP = the skill XP you earn with the tool in hand (one number), bar 300 x 1.18^n? Or points per skill level instead? | **XP bar** |
| 3 | Sigils: Unique / Rare / Legendary / Fabled from collections, bosses, dungeons, rebirth shop; NO Mythic Sigil (Mythic stays boss-only)? Tradeable on the AH? | **no Mythic sigil; AH yes, Bazaar / NPC never** |
| 4 | Next-tier slow factor 0.25 (about 4x the hits)? | **0.25** |
| 5 | Farming gate = half XP + no Fortune one tier up, refused two up (crops can't be slowed)? Hoe till area 1 / 3x3 / 3x3 / 5x5 / 5x5 / 7x7 / 7x7 / 9x9 per tier? | **yes** |
| 6 | Point reset for coins (5,000 x points spent) or never? | **for coins** |
| 7 | ONE private shard world per profile holding all six shard regions (cheaper, one thread) or one world per shard (six)? | **one world** |
| 8 | Who may enter your shards: owner + co-op members; visitors never? | **owner + co-op** |
| 9 | Shard Collect pays 50 % of the overworld XP per item (collections 100 %); Combat shard pays drops only, no XP? | **50 % / drops only** |
| 10 | Totems have tiers I-V but NO rarity / rolls (modifiers come from the 2 slots)? | **no rarity** |
| 11 | Starter Farming Shard comes from the hub quest line (after the mini boss), not at spawn? | **hub quest** |
| 12 | Multitool merge after rebirth 1 = sum of points, best rarity, merged lines, no penalty (the 0.2.18 85 % / 70 % rows go to 100)? | **yes** |
| 13 | Orchard uses NoCube's Orchard fruit by id (pack mod stays) and vanilla Apple; Ranching uses vanilla animals (no animal mod)? | **yes** |
| 14 | Harvest Moon Enchanted chance 0.05 % per crop at night, Moon Blade x2-x5? | **yes** |

---

## 15. Probes (before the phase that needs them)

| Probe | What | Phase |
|---|---|---|
| G1 | the hoe / sickle marker lock on the client (tool.farmLock on, swing an under-tier sickle) | 3 |
| R1 | which farm-animal interactions fire which events / drops (milk, shear, eggs) on 0.7 | 2 |
| S1 | 40 void shard worlds: RAM, tick length, unload / reload time | 5 |
| S2 | `removeWorld` keeps the folder + chunks; re-add reads storage back | 5 |
| S3 | can a jar register a new interaction Type (codec registry open?) - else the effect pattern | 5 |
| S4 | a placed custom BLOCK model with our texture + `OpenCustomUI` draws and opens | 5 |
| P1 | VoidProtect's 0.7 event list vs our guards (desk, read only) | 5 |
| N1 | spawn a tethered cosmetic NPC in a shard world on 0.7 | 6 |

Scratch used for the engine reads: `tools/dev/scratch/gatherspec/` (deleted).
