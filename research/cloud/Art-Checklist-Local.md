# Art checklist for the local session - what to read in Assets.zip, and how each concept becomes a real asset

Cloud draft, 2026-10-06. Paper only; no game files here. One checklist for every art folder in `research/cloud/`. The local session
reads Assets.zip READ-ONLY (PROJECT-RULES 1), writes findings into scratch `tools/dev/scratch/art-check/`, and records the answers as
one line per folder in `docs/log/` plus the folder README's "For the local session" list.
Inputs read: `tools/skyyart.py` (kit 1.0 header + function list), `research/Loot-Unid-Spec.md` (asset patterns, VERIFIED lines),
`research/Vault-Arrows-Spec.md` E12, `research/Accessory-Table-Spec.md`, `research/SkyyArmory-Spec.md`, `research/NightVision-Glare-Research.md`,
every art folder README, `research/cloud/Capstone-Sets.md`, `research/cloud/Enchanted-Materials-Draft.md`, `research/cloud/SkyyFishing-Spec-Draft.md`.

**Decisions followed (not re-decided):**
- `docs/answered/gear.md` 2026-10-06 art review: real textures at >= vanilla density, 2x if the engine allows (vanilla Mithril armor
  Chest 192x64, Head 160x64, Legs 128x64, Hands 64x64; icons 64x64); half-mask cowl helmets; Mithril helmet wings; Wolverine claws;
  the soul cage floats above the palm and spins slowly (engine check); Mining armor starts at Copper; Goldenwood helmet echoes Mithril.
- `docs/answered/pets.md` 2026-10-06: pets match the vanilla creature style (Rabbit texture 160x160, model icon 128x128); the dragon
  icon in the Dragon Nestkeeper style - **no tracing their files until Aures says OK** (PROJECT-RULES 2).
- `docs/answered/bags.md` / `docs/answered/gear.md`: Mining helmet lamps really light (reuse the SkyyAccessories Lantern light code).
- PROJECT-RULES 2: the repo is public - vanilla pixels are never committed; build scripts read Assets.zip and write the result into
  the jar (`tools/skyyart.py`). Concept sheets are our own art and may be committed.

## 0. What is already known (do not re-check)

| Fact | Source |
|---|---|
| Item JSON keys `Icon`, `IconProperties` (Scale, Rotation [x,y,z], Translation [x,y]), `Model`, `Texture`, `PlayerAnimationsId`, `DroppedItemAnimation`, `ItemSoundSetId` | `research/Loot-Unid-Spec.md` 1.3 (VERIFIED) |
| Icons live at `Common/Icons/ItemsGenerated/<Id>.png`, 64x64, PREMULTIPLIED alpha (steps 0/49/127/206/255); a plugin jar may ship its own (SkyyVault, SkyySacks, SkyyHud) | Loot-Unid-Spec, Vault-Arrows-Spec E12 |
| Vanilla re-texture pattern: one `.blockymodel` + a new texture of the SAME size / UV (`Weapon_Sword_Steel_Rusty`, `Weapon_Wand_Wood_Rotten`) | Loot-Unid-Spec (VERIFIED) |
| A recoloured texture shipped from a plugin jar works: SkyyArmory 0.1 metal wands (deployed 2026-10-03, used in game) | `docs/log/2026-10.md` |
| `SA.render_icon` matches vanilla only for the `[45, 90, 0]` wand / staff view; other views (ingot `[22.5, 45, 22.5]`) are ~1.5 px off - run `SA.check_icon` on a vanilla item of the same family first | `tools/skyyart.py` header |
| Block / entity light = `ColorLight(radius, r, g, b)`; torch `#ba9`, the brightest vanilla light `Rock_Crystal_Iridescent_Large` `#cde` Radius 18; the Lantern uses `DynamicLightUpdate` on the player | `research/NightVision-Glare-Research.md` |
| Vanilla benches animate with `CustomModelAnimation` `.blockyanim` (`Alchemy_Crafting.blockyanim`, Looping true) | `research/Accessory-Table-Spec.md` |

## 1. Global reads (do these once, they serve every folder)

Grep recipe (Windows, read-only; output to scratch): `python -c "import zipfile,sys; z=zipfile.ZipFile(r'<Assets.zip>'); [print(n) for n in z.namelist() if sys.argv[1] in n]" <text>`
and PNG sizes with `SA.png_size(z.read(name))`. Write each list to `tools/dev/scratch/art-check/<topic>.txt`.

| # | Read | Grep for | Record |
|---|---|---|---|
| G1 | Armor items, all materials | `Server/Item/Items/Armor/` then each JSON's `Model`, `Texture`, `Icon`, `IconProperties` | table: material x slot (Head / Chest / Hands / Legs) -> model path, texture path, texture WxH, icon props. Confirm the slot list is exactly these 4 (Capstone-Sets uses "Boots": map to Legs or Hands?) |
| G2 | Armor model node names | the `.blockymodel` of Leather (Light / Medium / Heavy), Cloth (Wool, Linen, Cotton, Silk), Wood, Copper..Onyxium | node list per slot (`SA.node_names`) + a **UV island map**: each node's UV rect drawn as a labelled box on the texture size (new kit helper, section 4) |
| G3 | Weapon / tool families | `Weapon/Wand`, `Weapon/Staff`, `Weapon/Spellbook` (Grimoire), `Weapon/Dagger`, `Throwing_Knife` / kunai, any `Bo` / quarterstaff, fist / gauntlet / claw items, `Tool/Pickaxe`, `Tool/Hatchet`, `Tool/Hoe`, `Tool/Shovel` | model, texture size, node names, IconProperties per family; the icon view (Rotation) each family uses |
| G4 | Ingredients / materials | `Ingredient_Bar_*`, `Ore_*`, `Wood_*` logs, `Plant_Crop_*_Item`, fibre, silk, crystals, fish (`Fish*`, `Food_Fish_*`) | icon only (64x64) + IconProperties; these are the bases of the Enchanted icons |
| G5 | Creatures | `Common/NPC/` or `Characters/` models for Rabbit, Chicken, Goat, Warthog, Bear_Grizzly, Turkey, Wolf, Boar, Hawk, Ram, Skrill, Mouflon, Horse, Camel; their textures (Rabbit 160x160 known) and the **128x128 model icons** (find the folder: grep `Rabbit` under `Icons/`) | path pattern for model icons, size, background (transparent?), view angle |
| G6 | UI icon slots | `Common/UI/` icons the pages use (`Icons/CraftingCategories/*`, `Icons/Abilities/`, ItemQualities frames) | sizes (category icons, ability icons) - decides the class emblem sizes |
| G7 | Light keys | the item JSON of `Furniture_Crude_Torch`, any held lantern, glowing crystals / lava blocks | the JSON key that gives a HELD item or a block light (`Light`? `Color` + `Radius`?), and whether an ARMOR item can carry it |
| G8 | Glow / emissive | any blockymodel / texture / material key like `Emissive`, `Fullbright`, `ShadingMode`, `Glow`, a second "emissive" texture file; candidates: crystals, lava, portals, Prisma / Onyxium gear, spawners | whether a texture part can glow in the dark without lighting the world; if none exists, "glow" = bright colour + a real light (G7) |
| G9 | Item animations | `.blockyanim` under `Common/Items/` (not `Characters/`); item JSON keys pointing at one (`Animation`, `ModelAnimation`, `CustomModelAnimation` on items, `DroppedItemAnimation`) | can a HELD item loop its own model animation (soul cage spin, glints)? Which vanilla held item does (spinning crystal, portal key, compass?) |
| G10 | Item particles | item JSON `Particles` / `ParticleSystemId` on wands / staffs (SkyyArmory-Spec 4 mentions an item particle) | can a held item or a dropped item emit particles (enchanted shimmer, lamp sparks) |
| G11 | Texture density limits | the largest item / armor texture in the zip and any model `TextureSize` / `PixelsPerUnit`-like key | whether a 2x texture on the SAME model works (density 2x = texture twice as big, UVs scaled) or needs a model edit - the "2x if the engine allows" question |

## 2. Per folder

Priority: **P1** = next build needs it, **P2** = this month, **P3** = later. "Route" = how the concept becomes an asset (section 3).

| Folder | Concept | Read (on top of section 1) | Record | Route | Pri |
|---|---|---|---|---|---|
| `research/cloud/accessory-art/` | 44 booster icons (11 lines x 4 rarities), drawn 32x32; "Love them" | G4 icon frame, ItemQualities frames (G6), how a dark slot looks behind an icon | final size 64x64; halo alpha OK on the slot | R2c: redraw at 64 (or 2x nearest + touch-up) as our own PNGs in the SkyyAccessories jar; keep the vanilla model for the 3D item | **P1** |
| `research/cloud/weapon-art/` | wands (built), staffs, spellbooks, soul cage, kunai, bo staff, claws, gauntlets, hand wraps | G3 all families; G9 + G10 for the soul cage; spellbook model nodes (cover, corners, clasp); is there any fist / claw item | per weapon: base vanilla model + texture size + nodes to recolour; soul cage: can the cage node rotate on a loop while held; the node offset that lifts it "above the palm" | R1 texture swap for staff / spellbook / kunai / bo (wand recipe); R3 new model for claws (long straight blades), gauntlets, soul cage | **P1** |
| `research/cloud/light-armor/` | Copper..Onyxium black-leather sets + half-mask cowls | G1 + G2 for Light Leather and each vanilla metal HELMET (Mithril wings) | UV islands for collar, shoulders, belt, tassels; which helmet model can carry a half mask; the echo shapes per metal | R4 armor repaint on the Light Leather model at >= vanilla density; helmets R3 if no mask geometry | **P1** |
| `research/cloud/gathering-armor-art/` | Mining (Copper+), Farming crop sets | G1/G2 for the base armors; G7 + G8 for the **helmet lamp** | lamp: armor light key or Lantern-style DynamicLight; lamp texture glow | R4; lamp = Lantern light code (shared helper, one light per player) + bright texture; crop hats R3 if no geometry | **P1** (lamp) / P2 |
| `research/cloud/foraging-armor/` | Wood..Goldenwood | G1/G2 for vanilla `Armor_Wood`; Farmer's Workbench wood categories | is vanilla Wood = Softwood; tassel / thorn geometry; Goldenwood helmet = Mithril helmet model? | R4 on the Wood model; Goldenwood helmet R1 on the Mithril helmet model | P2 |
| `research/cloud/heavy-armor/` | Heavy Leather (tier 1 Heavy) | G1/G2 `Armor_Leather_Heavy_*` | 4 slots exist; pauldron / tasset geometry | R4 retexture or keep vanilla (README Q2 default: keep vanilla for now) | P3 |
| `research/cloud/cloth-armor/` | Crude Robe | G1/G2 cloth tunic models; any hood; `Ingredient_Crystal_Green` colour | robe skirt below the knee? hood model? | R4 on the cloth model | P2 |
| `research/cloud/pet-art/` | 16 pets + dragon | G5 all; Dragon Nestkeeper only as a STYLE reference (no file reading for tracing until Aures OK) | vanilla creature proportions + palette per pet; model icon path / size | R2a: pet ITEM icon = render the vanilla creature model at 128 (new kit view, check_icon against a vanilla model icon) or recolour the vanilla model icon; the creature itself = vanilla model (+ R1 tint for variants) | P2 |
| `research/cloud/capstone-set-art/` (in progress) | Bailiff / Clerk / Notary sets, Voidglass + Aetherium | G1/G2 for Heavy plate, Light leather, Cloth robe bases; G8 (smoked glass, floating runes) | slot mapping (Boots?); transparency support in armor textures (glass) | R4 + R5 glow; runes R6 if animation exists, else painted | P3 |
| `research/cloud/fishing-art/` (in progress) | rods + reels (8 tiers), hooks, lines, sinkers | any vanilla rod / bobber / line model (fishing "does not exist in this build" per `research/Durability-Switch-Research.md` - grep anyway: `Fish`, `Rod`, `Bobber`); G4 fish icons; HyFishing's rod is NOT a source (licence) | nearest stick-like vanilla model (wand / staff / spear) for the rod; bobber entity | R3 new rod model (or R1 on a staff), parts = icon-only items (R2c) | P2 |
| `research/cloud/enchanted-art/` (in progress) | ~40 Enchanted materials + Blocks | G4 base icons; G10 (dropped-item shimmer), G9; ItemQualities glow | can an icon carry a glint frame (animated icons? no -> static); quality-frame colour for "Enchanted" | R2b: `recolor_icon` / tint of the vanilla base icon + a painted static glint overlay (kit helper) - vanilla pixels never committed | **P1** (Enchanted round) |
| `research/cloud/class-art/` (in progress) | 7 class emblems, 64 + 128 | G6 page icon sizes; can an inline page show a jar PNG directly (not as an item icon)? | path rule for UI images from a jar | R2c: our own PNG; if pages only take item icons, ship 7 hidden emblem ITEMS and use `item_icon` (proven path) | P2 |

## 3. Routes (how a concept becomes a jar asset)

| Route | When | Steps | Kit status |
|---|---|---|---|
| **R1 texture swap** | same shape as a vanilla item | `SA.item_parts` -> `SA.palette_from` (colour from the tier's vanilla pickaxe / ingot / staff gem) -> `SA.recolor` per node rects (`SA.node_rects`) -> `SA.render_icon` (after `check_icon` on that family) | exists (wand proof) |
| **R2a icon render** | new icon from a model | `SA.render_icon(model, tex, props)` at 64 (items) / 128 (model icons) | 64 proven for wands only; 128 + creature views unproven |
| **R2b icon recolour** | variant of a vanilla icon | `SA.recolor_icon(icon, grad, weights)` + overlay | exists; overlay helper missing |
| **R2c own icon** | our own drawing (accessories, parts, emblems) | concept generator -> final 64x64 PNG, **premultiplied** on write (`SA.png_encode` of premultiplied pixels), shipped in the jar | needs a premultiply helper + a "draw at 64" pass of each generator |
| **R3 new model** | geometry vanilla lacks (claws, soul cage, rod, half mask, hat brims) | author a `.blockymodel` (Blockbench-style JSON: nodes, boxes, UV offsets) in OUR build script as data; texture painted by us | **missing**: no model writer / validator in the kit; first test = one small model (claw blade) in a lean round |
| **R4 armor repaint** | new look on a vanilla armor model | read the UV island map (G2) -> paint our concept's details onto each island at the model's texture size (or 2x, G11) -> palette from the vanilla metal | **missing**: island map dump + a "paint by island" helper; concept sheets are front paintings, NOT UV maps |
| **R5 glow** | lamp, sap, glass, runes | per G8: emissive part if it exists; else bright texels + a real light (G7) | unknown |
| **R6 animation** | soul cage spin, rune float | per G9: a `.blockyanim` looping one node's rotation | unknown |

Kit additions to propose (each proven in `SA.verify()`, like skyyui): `SA.uv_map(model, tex_size)` (island map PNG for painters),
`SA.premultiply(img)`, `SA.overlay(icon, layer)`, `SA.scale_texture(png, 2)` + matching UV x2 (only if G11 says a model can take it),
`SA.check_icon` runs for the armor / ingot / creature views before `render_icon` is trusted there.

## 4. Order of work (priority)

| # | Step | Unblocks |
|---|---|---|
| 1 | G1, G2, G11 (armor table + UV maps + density) | Light, Mining, Foraging, Cloth, Heavy, Capstone |
| 2 | G4 + G6 + the accessory icons at 64 (R2c, premultiply helper) | SkyyAccessories icons (approved art) |
| 3 | G7 + G8 (light + glow) | Mining helmet lamp (LOCKED real light) |
| 4 | G3 + G9 + G10 (weapons, animation, particles) | Weapons v2 build, soul cage spin |
| 5 | G4 for every Enchanted base + overlay helper | Enchanted materials round |
| 6 | G5 (creatures + model icons) | Pets v2 |
| 7 | fishing grep, R3 model test | SkyyFishing stage 1 |
| 8 | class emblem image path (G6) | Profiles / Stats cards |

## For the local session (UNVERIFIED)

Everything in sections 1-2 is a check; the biggest unknowns:
1. G11: can a vanilla model take a 2x texture, or does 2x density need a model with doubled UVs (Skyy asked "double if they allow it")?
2. G8 / G7: emissive textures and lights on ARMOR (helmet lamp) - or only on blocks / held items.
3. G9: a looping model animation on a held item (soul cage).
4. Whether a plugin jar can ship a NEW `.blockymodel` (proven only for pack zips: `More_Crossbow_Tiers.zip`).
5. Capstone "Boots": Hytale's armor slots are Head / Chest / Hands / Legs - map Boots to Legs (and Legs to Hands?) or rename.
6. Pages: can an inline page show a jar PNG that is not an item icon (class emblems)?
7. `SA.render_icon` for 128 px creature model icons (view angle and lighting of vanilla model icons).

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Order: accessory icons + lamp first, then light armor, weapons, Enchanted, pets? | [as section 4] |
| 2 | If the engine cannot take 2x textures, stay at vanilla density (same as vanilla) rather than editing models? | [yes - vanilla density] |
| 3 | If armor cannot glow, the helmet lamp is a bright painted lamp + the real light around you - OK? | [yes] |
| 4 | Capstone sets: "Boots" becomes the Legs slot (Hytale has no separate boots)? | [yes, wait for the G1 check] |
| 5 | New 3D shapes (claws, soul cage, rods, masks) need hand-made models - OK to make our own, one small test first? | [yes, claw blade first] |
