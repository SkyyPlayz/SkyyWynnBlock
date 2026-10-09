# Recolour + look swaps for ALL armor - plan

*Written 2026-10-08. Planning only: nothing built, deployed or committed. Owner: Skyy (they/them).*

Skyy (docs/answered/gear.md, 2026-10-08), on The Armory's Alteration Table: "yeah, i really like the recoloring, and id like to make that
work for all of the armor if we can."

Later the same day (via the main session): "do a design per tree type in that set, so every hardwood gets its own design in that trees
color, and you can use the armorys system to change the look. allow them to change up the vanilla armor, so miners can be dapper too."

So the swap system must handle two kinds of variant:
- **Colour variants** - same model, other texture (The Armory's way).
- **Look variants** - a different MODEL with the same stats: one foraging design per tree type in each tree tier (F1-F5,
  research/Gathering-Progression-Spec.md 2.2), and other looks for the vanilla metal (mining) sets.

Sources read (read-only): `TheArmoryMod-1.22.0.jar` (classes `me.ladypaladra.thearmorymod.alteration.*`, its item / recipe / patch JSON),
`HytaleServer.jar` (protocol item classes), the live `SkyyGear/build_skyygear_0.2.10.py`, `SkyySkills/build_skyyskills_0.4.24.py`,
`SkyySacks/build_skyysacks_0.7.14.py`. Scratch `tools/dev/scratch/recolor/` deleted afterwards. Nothing of theirs is copied here: only
facts, their ids and their bench id.

---

## 1. How the Alteration Table works (VERIFIED from the jar bytecode)

**It is ordinary crafting-recipe data plus their own Java page. Family = a ResourceType.**

| Part | What it is |
|---|---|
| The table | A block `Alteration_Table` (Workbench tier 2 recipe). Opening it shows THEIR custom page (`AlterationPage`), not a vanilla bench window. Filter chips All / Head / Chest / Hands / Legs / Weapon + a search box. |
| Fuel | `Alteration_Kit` (crafted at the Workbench). One kit = 3 charges; the table holds 3 charges and stocks up to 50 kits. Creative mode skips charges. |
| A "family" | A **ResourceType** (e.g. `Resource_Armor_Iron_Chest`). Every member item lists that ResourceType in its `ResourceTypes` field. |
| A "variant" | An item whose own `Recipe` has ONE input = that ResourceType (quantity 1) and a `BenchRequirement` `{ Id: "ArmoryAlteration", Type: "StructuralCrafting" }`. |
| The index | `AlterationRecipeIndex.ensureBuilt()` walks **every** `CraftingRecipe` in the game's asset map (all mods, not only theirs). Any recipe that names the `ArmoryAlteration` bench with type StructuralCrafting, has exactly one ResourceType input and an item output joins the family of that ResourceType. Built once, lazily, on first use. |
| Is an item alterable? | Yes if any of its ResourceTypes is a known family key. |
| The swap | `AlterationTransaction.processFromInventory`: fires the engine's `CraftRecipeEvent$Pre` (cancellable), removes the input from its slot, fires `CraftRecipeEvent$Post`, puts the new item in the same slot (else inventory / ground). |
| Metadata | `buildTransferMetadata`: **clones the whole item metadata document**. The excluded-keys set is empty (`Collections.emptySet()`). So every key - SkyyGear's rarity / level / modifiers, enchantments - comes across unchanged. |
| Durability | Carried as a **fraction**: new durability = old fraction x the new item's max. Max is scaled the same way. A one-time INFO log warns if a family mixes different MaxDurability values. |
| Config | None. `AlterationConfig` holds compile-time constants only (bench id, kit id, charges). |

**How their vanilla Iron recolours join (important):** The Armory does NOT override vanilla `Armor_Iron_*`. It ships four Patchly
`.patch` files (`Server/Item/Items/Armor/Iron/Armor_Iron_Chest.patch` etc.) that only ADD `"ResourceTypes": [{ "Id":
"Resource_Armor_Iron_Chest" }]` to the vanilla item. Patchly (by riprod) is a patch library bundled inside their jar. It listens to
every asset pack registering (`AssetPackRegisterEvent`) and merges `.patch` files into an override pack it builds itself. **So the vanilla
Iron set is ALREADY swappable today** into 97 Armory looks (Black, Blue, Cyan, Green, Magenta, Purple, Red, White, Yellow, Rusty, Stone,
each colour also `_Alt`, some `_Fab`). Their recolours carry the same stats as vanilla Iron (Chest Health 17, Lv 20, durability 100).

### 1.1 Can OUR pack plug into it? Yes - with our own files only (VERIFIED by the code path; UNVERIFIED in game)

- The index reads every recipe in the asset map, so **our own items** with a `Recipe` naming the `ArmoryAlteration` bench and **our own**
  ResourceType are picked up. No registry, no tag list, no config needed. Nothing of theirs is overridden.
- Our page entries show with our own names / icons (their page reads the variant's Item).
- Adding a vanilla item (Copper armor etc.) to a family needs a `ResourceTypes` line on the vanilla item. Two ways: a Patchly `.patch`
  in our asset pack (the way they do Iron; it only works while The Armory - which carries Patchly - is loaded, which is also the only
  time the table exists), or a vanilla item override generated at build time. Patchly reading OTHER packs' `.patch` files is very likely
  from its code (pack-register listener, per-pack sources) but **UNVERIFIED in game**.
- A recipe that names `ArmoryAlteration` while The Armory is absent should simply never be usable. **UNVERIFIED**: whether the server logs a
  WARN for an unknown bench (would show as a dev error badge; check in P0).
- SkyySacks `/craft` never lists these recipes: it only shows recipes whose bench has an equipped bench accessory (VERIFIED in
  `benchRecipes`), and there is no Alteration accessory.

---

## 2. What SkyyGear does on an alteration today (from the live 0.2.10 script)

| Question | Answer |
|---|---|
| Does the roll survive? | **Yes.** The metadata document is cloned, so rarity, level stamp, modifiers, identified / unidentified state all carry. |
| Does it re-roll? | **No, for a stamped piece.** `GearCraftSys` (on `CraftRecipeEvent$Post`) snapshots the output id, then `GearCraftTask.rollIn` only rolls a stack that has **no SkyyGear document** and is **fresh** (full durability, metadata equal to a bench output). An altered stamped piece has the document -> skipped. |
| Smithing XP farm? | **No, for a stamped piece** (XP is paid only for pieces `rollIn` rolled). Edge: a piece with NO document yet and full durability would be rolled + pay craft XP **once** on its first swap (then it has a document). SkyyGear stamps new items within ~250 ms of arriving, so this is rare and cannot loop. |
| Level band block | With `craft.belowBand = block` (default is `min`), `GearCraftPreSys` cancels `CraftRecipeEvent$Pre` for a below-band crafter - that would also **refuse a colour swap** of a high piece. Not live by default, but a bug in waiting. |
| Stats after a swap | SkyyGear keys stats / band by **item id**. Armory colours of one family share stats, and words like "Iron" put `Armor_Iron_Chest_Black` in the Iron band, so a swap keeps the numbers. Our own variant ids must map to their base id the same way (section 4.3). |
| Other mods | SkyySkills' CraftSys pays only Alchemybench / Furnace recipes; SkyyCooking only cooking - neither reacts. |

**Small SkyyGear fix (whichever option):** in `GearCraftSys` and `GearCraftPreSys`, skip any recipe whose bench is `ArmoryAlteration`
(the same test their `isAlterationRecipe` does). Then a swap can never roll, pay XP or be refused. Plus: mining stat lines must follow
the FAMILY, not just the 4 vanilla ids (section 4.3), or a miner loses their mining lines by recolouring.

---

## 3. Options

### (a) Plug our items into The Armory's table

What we would ship (all in our own jar's asset pack, all ours, generated at build time where vanilla-derived, never committed when
vanilla-derived):
1. `Server/Item/ResourceTypes/Resource_Skyy_<Family>.json` - one per family (e.g. `Resource_Skyy_ForageF1_Chest`, `Resource_Skyy_Copper_Chest`). Our own ids.
2. Each variant item `Server/Item/Items/<our id>.json`: the base piece's stats, its own Model / Texture / Icon, `ResourceTypes: [our family]`,
   and `Recipe: { Input: [{ ResourceTypeId: our family, Quantity: 1 }], BenchRequirement: [{ Id: "ArmoryAlteration", Type: "StructuralCrafting", Categories: ["ArmoryAlteration"] }], TimeSeconds: 0 }`.
3. Our base pieces (gathering sets) list the same ResourceType (plus their normal crafting recipe elsewhere).
4. For vanilla metal bases other than Iron: `Server/Item/Items/Armor/<Metal>/Armor_<Metal>_<Slot>.patch` adding our ResourceType (Patchly) -
   24 tiny files. (Iron needs nothing: The Armory already did it.)
5. Textures / models / icons (our art, or recolours generated from vanilla at build time) + language lines for the names.

- **Needs LadyPaladra?** No. We do not change any of their files; we only name their bench id. A friendly heads-up is still nice (PACK.md
  contact). It is NOT an adaptation of their work, so the CC BY-NC adaptation clause is not even needed.
- **Covers:** our farming + foraging sets (colour AND look variants - the table does not care if the model differs), all vanilla metal
  mining sets, The Armory's own pieces (already). Other pack mods' armor: only if their author ships families - we never add their ids
  to our families (that would need a patch of their items = their files).
- **Cost:** data generation in a build script + SkyyGear guard. No UI, no Java swap code.
- **Risks:** fully dependent on The Armory loading (Hytale 0.7 on 2026-10-12 may break it until LadyPaladra updates). Players need
  Alteration Kits (3 crystals + 1 iron bar = 3 swaps) - fine, or a cost we cannot tune. Their page, their look (not our vanilla-style kit).
  Patchly-on-our-pack UNVERIFIED.

### (b) Our OWN swap station (a "Wardrobe" bench / page)

A small block + page in our mod (SkyyGear or a new tiny `SkyyWardrobe`): pick a piece -> see its family -> pick a look -> swap.
- **Swap code:** on the world thread, count before / after, `new ItemStack(newId, qty, durability scaled like theirs, max, metadata clone)`
  in the same slot. No craft events fired at all, so no roll / XP / refusal risk. Page previews use `new ItemStack(id, 1)` only (UI rule:
  never a metadata stack in an ItemGridSlot).
- **Families:** read from the SAME data as (a): every `ArmoryAlteration` recipe in the asset map (ours + The Armory's, exactly like their
  index) + our own family table. So it also swaps The Armory's pieces, and our pieces still swap if The Armory is gone or broken on 0.7.
- **Cost / gate:** our choice - coins, a dye item, a Smithing level, free. Editable in Server Setup (skyycfg).
- **Vanilla bases:** our station can treat `Armor_Copper_Chest` as the base of `Resource_Skyy_Copper_Chest` from our own table - **no patch
  and no override of the vanilla item needed.**
- **Other pack armor:** only by referencing their existing variant ids (e.g. a mod that already has colour ids). Never our recolour of
  their textures unless their licence allows it (The Armory's CC BY-NC would; still ask first, our rule).
- **Cost:** a full new system (block, page, swap, config) = Ultracode round. **Risks:** item swap = dupe / loss surface; another page to
  keep vanilla-looking.

### (c) Dye item with one item id (per-stack texture)

- **VERIFIED not possible per item:** the item packet `ItemWithAllMetadata` carries only `itemId, quantity, durability, maxDurability,
  quality, overrideDroppedItemAnimation, metadata`. Model and texture live on the item asset (`ItemBase.model / texture`, per id). So two
  stacks of one id always look the same.
- `ItemAppearanceConditions` are `Map<Integer stat index, condition[]>` with `Model / Texture / Condition range` - driven by the WEARER's
  entity stat, not by the item. In theory a per-player "look" stat could pick a texture (a transmog per player, no extra ids).
  **UNVERIFIED:** whether worn armor honours appearance conditions at all (vanilla uses them for held items). It would need a probe build;
  it also changes every piece of that family on that player at once. Not recommended now.

### Comparison

| | (a) Armory table | (b) own station | (c) dye / stat |
|---|---|---|---|
| Our gathering sets | yes | yes | probe only |
| Vanilla mining sets | yes (Iron already; others via patch) | yes (no patch) | probe only |
| The Armory's pieces | yes (theirs) | yes (reads their recipes) | no |
| Other pack armor | only their own families | their existing ids only | no |
| Works without The Armory / if 0.7 breaks it | no | yes | yes |
| Roll / XP risk | guard needed (small) | none (no craft event) | none |
| Build cost | low (data + art) | high (Ultracode) | probe first |
| Licence fit | clean (our files, their bench id) | clean | clean |

**Item id count (both a and b need one id per look):** pieces x looks. The Armory already loads 946 colour ids, so the engine copes.
Our plan below adds about 300 ids (section 4.2). Every id needs a generated icon; `skyyart.render_icon` is proven only for wands /
staffs, so armor icons need a `check_icon` against a vanilla armor icon first.

---

## 4. Recommendation

**Do (a) now, written so (b) can reuse it later.** The family data (ResourceTypes + `ArmoryAlteration` recipes) is exactly what our own
station would read, so nothing is wasted. Build (b) only if The Armory breaks on 0.7 for long, or Skyy wants swaps from the SkyWynn Menu
/ a coin cost.

### 4.1 Rules for every family

- All members of a family have **identical stats and MaxDurability** - only Model / Texture / Icon / name change. Look variants copy the
  base piece's numbers at build time.
- A family is **one slot of one set** (e.g. F1 Chest), never across tiers or sets - otherwise a swap would turn a cheap piece into a
  better one (stats are per item id).
- **Combat Armory looks are NOT added to mining families** (different stats; would let a miner turn a Copper chest into a Cobalt Dragon
  chest). Only same-stat looks.

### 4.2 What each armor group gets

| Group | Looks | Ids (new) |
|---|---|---|
| **Foraging** (5 tree tiers) | one design per tree type, in that tree's colours (Skyy): F1 Oak, Birch, Beech, Ash, Aspen (5); F2 Maple, Azure (2); F3 Gumboab, Dry, Bottletree, Palo (4); F4 Redwood, Fir, Cedar, Poisoned, Spiral (5); F5 Sallow, Burnt, Petrified, Bamboo, Camphor, Banyan, Jungle, Blue Fig, Fire, Crystalwood (10) = 26 designs. Crafted as the key-log design; swap to any tree of the same tier. | 26 x 4 = 104 (incl. the 5 bases) |
| **Farming** (7 crop sets) | one design per crop of the pair (Wheat / Lettuce, Carrot / Corn, ...) = 14 designs, same idea as the trees | 14 x 4 = 56 |
| **Mining: Iron** | The Armory's 20 colours (+ `_Fab`) - already live through their patch | 0 |
| **Mining: Copper, Thorium, Cobalt, Adamantite, Mithril, Onyxium** | 8 colours each, recoloured from the vanilla set at build time | 6 x 4 x 8 = 192 |
| The Armory combat sets | their own families (already) | 0 |
| Other pack armor | none unless the mod has its own variant ids | 0 |

Total about 350 new ids (well under The Armory's 946).

**Which Armory looks serve each mining tier:** only **Iron** has same-stat Armory looks (`Armor_Iron_<Slot>_<Colour>`, 97 ids). The
Armory has no Copper / Thorium / Cobalt / Adamantite / Mithril / Onyxium recolours of vanilla armor - its metal-tier sets (Cobalt Dragon,
Elite Rook, Daemon, Academy, Grand Lich ...) have their own stats and stay combat. So the other five metals + Copper get OUR recolours.
Later "dapper" extras (new models from our artist, e.g. a top-hat helm) can join a metal's family the same way.

### 4.3 How stats / SkyyGear rolls stay the mining set's

- The roll (rarity / level / modifiers) carries in the metadata (section 2).
- Base stats: our recolour ids copy the vanilla piece's JSON numbers at build time; Armory Iron colours already equal vanilla Iron.
- **SkyyGear maps every look id to its base id** (new rule `gear:base`): band, level, stat lines and the planned MINING lines come from the
  base (`Armor_Cobalt_Chest`), found via the family table (our generated list + every `ArmoryAlteration` recipe whose family contains a
  vanilla mining id). So `Armor_Iron_Chest_Purple_Fab` is a mining Iron chest. This also keeps the Pack-Armor-Plan default "the 97 Iron
  recolours stay out of combat drops".
- Our ids use our own namespace so they can never clash with a future Armory id: `Skyy_Look_<BaseId>_<Look>` (e.g.
  `Skyy_Look_Armor_Cobalt_Chest_Red`, `Skyy_Look_Forage_F1_Chest_Birch`). SkyyGear's id rules already treat `Skyy_` ids as gear candidates;
  the base map gives the band.

### 4.4 Colour palette (names only, same words as The Armory so the table reads as one system)

Black, White, Red, Blue, Green, Purple, Yellow, Cyan (8). The Armory also uses Gray, Magenta, Rusty, Stone - Rusty / Gray can be added
for Copper and Iron-ish looks later if Skyy wants 10.
Recolour the **cloth / leather / trim** parts and keep the **metal in its tier colour** (LOCKED 2026-10-06: tier = metal colour - Copper
copper, Thorium green, Cobalt blue ...), so a red Cobalt chest still reads as Cobalt.

### 4.5 Art pipeline

- **Vanilla metal recolours:** a build script reads the vanilla model + texture from Assets.zip, finds the cloth / leather texels with
  `skyyart.node_rects`, gradient-maps them to each palette colour (`skyyart.recolor`), renders icons (`render_icon`, after a `check_icon`
  on a vanilla armor icon), writes PNGs + item JSON straight into the jar. Nothing vanilla-derived is committed.
- **Gathering sets:** the artist's base model + texture per tier go to `art/gathering-armor/` (our own art, committable). Per-tree /
  per-crop looks: either the artist paints each one, or (cheaper) the artist makes one model per tier with a texture split into
  "wood / bark" and "detail" parts, and the build script recolours the wood parts with a palette sampled from that tree's vanilla log /
  leaf texture at build time (`skyyart.palette_from`), plus hand-made extras per tree where the artist wants. Skyy's question 2.

### 4.6 Phases (PROJECT-RULES 4 round sizes)

| Phase | What | Round |
|---|---|---|
| P0 | After Hytale 0.7 (2026-10-12) and The Armory loads clean: Skyy swaps a SkyyGear-rolled `Armor_Iron_Chest` at the table. Check: rarity / level / lines kept, durability fraction, no Smithing XP, gear.log has no CRAFT line, logs clean. | no agents (Skyy test + log scan) |
| P1 | SkyyGear: skip `ArmoryAlteration` recipes in GearCraftSys + GearCraftPreSys; `gear:base` map (look id -> base id) used for band / stats / mining lines; the Armory Iron colours count as mining Iron. | Lean (one mod, no saved-data change) - or folded into the mining-lines round |
| P2 | Vanilla metal recolours: 192 ids, generated art + icons + families (Patchly patches for the 6 vanilla bases) in our armor jar; a build check that every family has equal stats / durability. | Full (new items in player hands = rollback floor) |
| P3 | Foraging per-tree designs (104 ids) + farming per-crop designs (56) when the artist's models land in `art/gathering-armor/`; families from day one. | Full, together with the gathering-armor round |
| P4 (only if needed) | Own Wardrobe station (b): bench + page + swap + Server Setup cost; reads the same families. | Ultracode (item swaps, dupes, new system) |

---

## 5. Questions for Skyy (each with a recommended default)

1. **Use The Armory's table for our looks, or our own station?** [The Armory's table now (cheap, same data works for our own station
   later); build our own only if The Armory breaks on 0.7 or you want swaps from the menu / for coins.]
2. **Tree designs: hand-painted per tree, or one model per tier recoloured per tree from the tree's own colours?** [One model per tier,
   recoloured per tree at build time + small hand-made extras per tree where the artist wants - 26 full designs is a lot of art.]
3. **How do players get each tree look?** [Craft the tier's key-log set, swap to any tree of that tier at the table. No per-tree recipes.]
4. **Farming: one design per crop (14) like the trees, or one design per set + colours?** [One per crop of the pair - matches the trees.]
5. **How many colours for the vanilla metal mining sets?** [8: Black, White, Red, Blue, Green, Purple, Yellow, Cyan; metal keeps its tier
   colour, the cloth / leather / trim change.]
6. **Iron: keep The Armory's 20 Iron colours as the miner's Iron looks?** [Yes - free, already live, same stats.]
7. **Combat Armory looks on mining sets (e.g. a Cobalt Dragon look on a mining Cobalt chest)?** [No - different stats; a "look only"
   item that borrows their model path would need their files at runtime and a rules exception. Ask again later if wanted.]
8. **Swap cost?** [The Armory's Alteration Kit (3 swaps per kit). With our own station later: a small coin cost, editable in Server Setup.]
9. **Our armor recolours for other pack mods (not The Armory)?** [No - only their own variant ids, never our recolours of their art.]
