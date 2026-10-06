# Pets - concept sheet (launch list + dragon hatchling)

Cloud draft, 2026-10-06. Original pixel art made by code (`research/cloud/pet-art/make_pets.py`, Python + Pillow). No copied art, no
game files, and none of the vanilla Hytale creature designs: every pet is a stylised original "chibi" animal. Concept only; nothing built.
Inputs read: `research/cloud/Pets-Spec.md` (launch list section 5, rarities section 2), `research/Dragon-Pets-Idea.md`,
`research/cloud/Dragon-Quest-Spec.md` (elements, hatchling stage), `docs/answered/pets.md` (R6-R9 locks + the 2026-10-06 Nestkeeper note),
`OPEN-QUESTIONS.md` (pets section), `CLOUD-RESUME.md` (the "Pets concept sheet" item). Style copied from
`research/cloud/light-armor/make_sheets.py` (chunky pixels, 1-px outline, 4-step shading lit top-left, labels).

**Start here (v2, 2026-10-06):** `research/cloud/pet-art/pet-sheet-v2.png`. The v1 sheet (`pet-sheet.png`, flat side-view sprites)
is kept for comparison; sections 1-4 below describe v1.

## 0. v2 - redo in the vanilla Hytale creature style

Why: Skyy's review (`docs/answered/pets.md`, LOCKED 2026-10-06): "i dont really like any accept maybe the rabbit. more drtail, and
match the hytale style/look"; dragon icon: "make the inventory icon look like the dragons in the mod were using".

**How v2 is made (`research/cloud/pet-art/make_pets_v2.py`, Python + Pillow, deterministic).** Instead of painting flat sprites, every
pet is BUILT like a Hytale creature model: 15-40 boxes (head, snout, cheeks, ears, body, legs, horns, wings, saddle ...), each with
its own painted-style texture at about one texel per model unit (fur strokes, wool clumps, feather rows, dragon scales, horn rings,
leather; painted top-to-bottom gradient, bevel highlight on top edges, warm highlights and cool shadows, subtle noise; eyes, noses,
socks, spots and stripes as texel decals). A small ray-caster renders the boxes in a 3/4 view onto a 128 x 128 canvas (the vanilla
model-icon size), lit top-left, with a 1-px dark outline and a ground shadow. Started from the rabbit (Skyy's favourite), then every
other pet was matched to it and re-checked side by side (same camera, light, eye style, texture rules).

| File | What |
|---|---|
| `research/cloud/pet-art/pet-sheet-v2.png` | All 16 pets at 2x (1904 x 1202) + the 9 dragon elements + the dragon inventory icon |
| `research/cloud/pet-art/pet-<name>-v2.png` | One card per pet at 3x (16 files, rabbit ... dragon-hatchling) |
| `research/cloud/pet-art/dragon-elements-v2.png` | The dragon in all 9 elements (5 quest + 4 secret), one model recoloured |
| `research/cloud/pet-art/icon-dragon-128-v2.png`, `icon-dragon-64-v2.png` | Dragon inventory icon concept, transparent, 128 x 128 and 64 x 64 |
| `research/cloud/pet-art/make_pets_v2.py` | The generator. `python3 research/cloud/pet-art/make_pets_v2.py` (all), or add pet names to write a 3x `preview-v2.png` (delete after) |

Folder total about 540 KB (v1 + v2). Same 16 pets, families, zones and rarity bars as v1 (section 3 proposals unchanged).

**What changed per pet (v1 -> v2).** All: real 3D box bodies, big boxy heads, short thick legs, big eyes (dark rim, coloured iris, tall
pupil, white 2-3 px glint, small lower reflection, lid line), painted texture. Rabbit: tan fur, cream belly / muzzle / feet, pink inner
ears and nose, darker back saddle and ear tips, white puff tail. Chicken: feathered body, red comb + wattles, raised tail. Goat: two-part
curved horns, beard, amber eyes. Warthog / Boar / Tusker: one hog rig (bristle crest, snout pad, tusks) - grey, dark brown, and
rust-red with white war paint for the Tusker. Bear: shoulder hump, light muzzle, claws. Turkey: 7-feather fan with banded tips, blue
head, red snood. Wolf: neck ruff, light chest / socks / tail tip, amber eyes. Hawk: on a perch, barred chest, yellow cere + dark hook.
Ram / Mouflon: four-box curled horns, saddle (mount marker kept from v1). Skrill: still the original "stormwing" (bat wing on a spar,
spark crest), hovering. Horse: long neck + mane, blaze, bridle, saddle. Camel: hump, striped blanket with tassels.

**Dragon (original - NOT Nestkeeper's).** We have no files from Aures - Dragon Nestkeeper and must not copy or trace them (PROJECT-RULES 2;
Skyy's permission request was sent 2026-10-06). From web snippets only (UNVERIFIED): Nestkeeper has custom dragon models, 4 growth
stages, a "Plain Dragon" in green plains / forests, every dragon with its own look, small dragons carried with cloth, adults ridden
(CurseForge page). No look details were found in text. So v2 draws an ORIGINAL juvenile dragon in a chunky Hytale-like spirit: four
legs, big boxy head with a blunt snout, fangs and jaw plate, long swept-back horns plus a smaller pair, cheek frills, folded wings on
a spar, back and tail spines, ribbed belly plates, tail curling toward the viewer with a spade tip. The inventory icon is the same model
(no shadow, fit to 124 px). **When Aures says OK, the icon should be re-rendered from their dragon model instead** (local session; the
renderer here is only for our own box models).

**What I learned about the Hytale look (web, UNVERIFIED - no game files here):**
- Official modding docs: "a modern, stylized voxel game, with retro pixel-art textures"; models use only cubes and quads (no
  triangles, no edge loops) made in Blockbench with the Hytale plugin; mobs / players / equipment use 64 px pixel density (vs 32 px
  for blocks) - hytale.com "an introduction to making models for hytale" and hytalemodding.dev "art assets".
- A guide describes characters as relatively detailed with expressive animation on a block world, character textures sharper than older
  sandbox games.
- Not found in text (my guesses, to check against Assets.zip): exact palettes of Rabbit / Boar / Sheep / Kweebec, eye construction,
  how much noise vanilla creature textures carry. The v2 look (warm natural colours, painted gradients, big glinting eyes, chunky
  short-legged boxes) is my reading of the trailers' style, not a measurement.

Sources: [hytale.com - an introduction to making models for hytale](https://hytale.com/news/2025/12/an-introduction-to-making-models-for-hytale),
[hytalemodding.dev - art assets](https://hytalemodding.dev/en/docs/established-information/server/content-categories/art-assets),
[allthings.how guide](https://allthings.how/?p=3233), [CurseForge - Aures - Dragon Nestkeeper](https://www.curseforge.com/hytale/mods/aures-dragon-nestkeeper).

**v2 open points.** v2 local checks: rows 4-6 of "For the local session" below. v2 questions: rows 7-9 of "Questions for Skyy".

## 1. Files

| File | What |
|---|---|
| `research/cloud/pet-art/pet-sheet.png` | All pets: skill pets / combat + class pets / mounts + dragon; rarity bar, name, role, rarity, zone |
| `research/cloud/pet-art/pet-<name>.png` | One card per pet, bigger (16 files: rabbit ... dragon-hatchling) |
| `research/cloud/pet-art/dragon-elements.png` | The dragon hatchling in all 9 elements (5 quest + 4 secret) |
| `research/cloud/pet-art/make_pets.py` | The generator (deterministic: a re-run gives the same bytes) |

Total PNG size about 110 KB. Run: `python3 research/cloud/pet-art/make_pets.py`.

## 2. What is drawn

All 15 launch pets from Pets-Spec section 5 (one picture each, not one per zone family - the list is short enough), plus the dragon
hatchling. Side view, facing right, all on the same 60 x 46 pixel grid so the sizes compare (mounts are a bit bigger; Lv 1 pets would
show at 0.6x in game, Pets-Spec section 6).

| Row | Pets | Notes |
|---|---|---|
| Skill pets (slot 1, never fight - R7) | Rabbit, Chicken (Farming); Goat, Warthog (Mining); Bear, Turkey (Foraging) | Goat has a yellow eye with a bar pupil |
| Combat + class (Summon slot - R7) | Wolf, Boar; Hawk (Archer), Ram (Warrior), Skrill (Mage), Tusker (Berserker), Mouflon (Priest) | Tusker = the "recoloured Warthog" from the spec: rust red, big gold-tipped tusks, white war paint, red mane |
| Mounts + dragon | Horse, Camel, Dragon Hatchling (Fire shown) | Mount pets (Ram, Mouflon, Horse, Camel) wear a small leather saddle with gold trim = the "can be ridden" marker |

- **Skrill:** drawn as an original "stormwing" (a hovering little wyvern-bird with bat wings, a spark crest and a forked spark tail),
  NOT the vanilla Skrill look. It floats (small shadow) because it is the Mage's pet.
- **Dragon hatchling:** big head, small wings, back spines, belly plates, sitting by its broken egg shell (Dragon-Quest-Spec D7
  "Hatchling, Lv 1, 0.4x"). Pink Mythic frame. The element strip shows Earth / Thunder / Water / Fire / Air and the secret Blood / Void /
  Light / Crystal as recolours of one design (matches "one rig, recoloured" in Dragon-Quest-Spec section 2).
- **Rarity bar colours:** Common white, Uncommon green, Rare blue, Epic purple, Legendary gold, Mythic pink (SkyBlock pet colours,
  Pets-Spec section 2 names).

## 3. Proposals made only for this sheet (not in the spec)

The spec gives no zone or "found at" rarity per pet, so the sheet labels are proposals:

| Pet | Zone label | Found-at rarity | Why |
|---|---|---|---|
| Rabbit / Chicken | Z1 Emerald Wilds | Common | starter / farm animals (Rabbit = starter pet, spec section 4) |
| Turkey, Boar | Z1 Emerald Wilds | Uncommon | forest + wild taming |
| Goat, Bear, Wolf, Ram | Z3 Whisperfrost | Uncommon / Rare / Rare / Epic | mountain + cold forest animals |
| Warthog, Hawk, Mouflon, Horse, Camel | Z2 Howling Sands | Uncommon / Epic / Epic / Uncommon / Rare | dry country; Horse from the Zone 2 stable quest (R6) |
| Skrill, Tusker | Z4 Devastated Lands | Epic | late class pets |
| Dragon Hatchling | Z5 dinosaur caves | Mythic | R8 + Dragon-Quest-Spec |

Every pet can still be raised with the per-skill Upgrade Stones (R9), so the bar only shows the usual starting rarity.

## 4. Notes

- The Dragon plan may change: the 2026-10-06 note in `docs/answered/pets.md` and the open OPEN-QUESTIONS.md pets line ("DRAGON as a pet
  with Aures' Dragon Nestkeeper: our secondary pet slot summons their dragon, or their mod owns the dragon and our slot links it, or our
  own dragons later?" [default (1) summon via our slot if allowed, else (2)]). If (1) or (2) wins, the in-game dragon would be Nestkeeper's
  model, and our hatchling art would only be an icon / for option (3). Nestkeeper's art must not be copied (PROJECT-RULES 2).
- These are concept pictures for the look and the colours, not textures. In game the pets would use vanilla models where the spec says
  so (Pets-Spec section 5 model ids); this art is then the menu icon / style guide, or the base for our own models if we make any.
- Warthog is used twice in the spec (Mining + Berserker); the sheet makes them clearly different (grey Warthog vs red Tusker).

## For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Whether the vanilla models in Pets-Spec (Rabbit, Chicken, Goat, Warthog, Bear_Grizzly, Turkey, Wolf, Boar, Hawk, Ram, Skrill, Mouflon, Horse, Camel) exist and how they look next to these concepts (Assets.zip, read-only). |
| 2 | Whether a saddle / tint / recolour (Tusker, dragon elements) can be done at build time without committing vanilla assets. |
| 3 | Whether item icons for pets can be generated from these 60 x 46 drawings (icon size and style of vanilla item icons). |
| 4 | v2: open the vanilla Rabbit, Boar, Sheep, Goat, Wolf, Bear_Grizzly, Horse, Camel models + textures (read-only) and note per creature: texture size, how big the eyes are (px), how much noise / gradient the textures carry, leg and head proportions - then tune `make_pets_v2.py` (palettes, eye size, `tex_offset` noise) to match. |
| 5 | v2: vanilla model-icon size and camera (assumed 128 x 128, 3/4 view from the front-left, lit top-left) and item icon size (assumed 64 x 64). |
| 6 | v2 dragon: once Aures allows it, render the pet inventory icon from the Nestkeeper dragon model (their files stay in their mod; nothing of theirs committed). Until then the original icon here is a placeholder. |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Do these looks fit SkyWynn (chunky, cute, side view), or should pets look closer to the vanilla Hytale animals? | keep vanilla models in game; this art for icons + menus |
| 2 | Pet rarity colours: SkyBlock's (Common white ... Mythic pink) or the SkyyGear gear rarity colours? | SkyBlock pet colours |
| 3 | Are the zone labels and "found at" rarities in section 3 OK? | as in section 3 |
| 4 | Should mount pets show a saddle when summoned? | yes, small saddle |
| 5 | Skrill (Mage): keep the vanilla Skrill, or an original "stormwing" like the sheet? | vanilla Skrill model in game |
| 6 | Dragon hatchling: our own design (this sheet) or wait for the Nestkeeper decision? | wait for the Nestkeeper answer; this art stays a concept |
| 7 | v2: is this box-model look close enough to vanilla Hytale animals, and is the rabbit still the best one? Which pets need another pass? | v2 look; redo only the ones you name |
| 8 | v2: in game, should pets use vanilla models (Pets-Spec section 5) with these renders only as menu / inventory icons, or should we build our own models from these box layouts? | vanilla models in game, these as icons |
| 9 | Dragon icon: keep this original dragon until Aures answers, then switch to a render of their dragon? | yes |
