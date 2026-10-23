# Dragons - 6 dragon pet icons + 4 dragon egg icons (round D4 of research/Dragon-Pet-Spec.md, sections 8 + 9)

**Status: DRAFT for Skyy's review** (2026-10-23). Not committed, not wired in, not seen in game. **Start here:** `sheet.png`.

Follows Skyy's words in `docs/answered/pets.md`: 2026-10-06 "for the dragons, make the inventory icon look like the dragons in the mod
were using" (an ORIGINAL drawing in that chunky Hytale style - skill `skywynn-art` section 3) and the spec's "a 64 px inventory icon per
dragon (original)" + "dragon egg icons". Original pixels drawn from code (`tools/art/make_dragon_icons.py`, pure Python standard
library). No vanilla file, no Dragon Nestkeeper file (All Rights Reserved) and no reference picture was read, copied, traced or
recoloured. Deterministic (two runs = same bytes, checked).

## Files (laid out like the jar)

| File | Item id | Id status | What |
|---|---|---|---|
| `Common/Icons/ItemsGenerated/Skyy_PetIcon_DragonPlain.png` | `Skyy_PetIcon_DragonPlain` | existing (SkyyPets 0.4.11+ portrait) | Plain Dragon, Earth: mossy green, rock spikes, moss, leaf tail |
| `Common/Icons/ItemsGenerated/Skyy_PetIcon_DragonTundra.png` | `Skyy_PetIcon_DragonTundra` | existing | Tundra Dragon, Water: ice blue, glowing ice crystal spikes + tail |
| `Common/Icons/ItemsGenerated/Skyy_PetIcon_DragonFire.png` | `Skyy_PetIcon_DragonFire` | existing | Fire Dragon: red, ember belly, dark curled horns, flame tail |
| `Common/Icons/ItemsGenerated/Skyy_PetIcon_DragonStorm.png` | `Skyy_PetIcon_DragonStorm` | existing | Storm Dragon, Thunder: indigo, gold horns + wing bones, lightning stripes, bolt tail |
| `Common/Icons/ItemsGenerated/Skyy_PetIcon_DragonSky.png` | `Skyy_PetIcon_DragonSky` | existing | Sky Dragon, Air: white-teal, feathered wings, cheek feathers, feather tail |
| `Common/Icons/ItemsGenerated/Skyy_PetIcon_DragonVoid.png` | `Skyy_PetIcon_DragonVoid` | NEW (kind `DragonVoid` = round D5, secret) | Void Dragon: dark violet, glowing eyes + horn tips, star-specked wings, void aura |
| `Common/Icons/ItemsGenerated/Skyy_PetEgg_Dragon_Fire.png` | `Skyy_PetEgg_Dragon_Fire` | existing (SkyyPets item) | Fire Dragon Egg |
| `Common/Icons/ItemsGenerated/Skyy_PetEgg_Dragon_Thunder.png` | `Skyy_PetEgg_Dragon_Thunder` | existing | Storm Dragon Egg |
| `Common/Icons/ItemsGenerated/Skyy_PetEgg_Dragon_Air.png` | `Skyy_PetEgg_Dragon_Air` | existing | Sky Dragon Egg |
| `Common/Icons/ItemsGenerated/Skyy_PetEgg_Dragon_Void.png` | `Skyy_PetEgg_Dragon_Void` | NEW (proposed id for D5 / D6) | Void Dragon Egg |
| `sheet.png` | - | - | review sheet: all 10 at 2x on element-coloured slots + actual 64 / 32 px strip |
| `manifest.json` | - | - | every file: bytes, sha256, id, existing / new, element, colour |

All icons 64 x 64 RGBA, straight alpha. Body pixels hard alpha + a 1 px dark outline; the element glow / halo is soft (alpha <= 0.85),
like `art/pet-eggs`.

**No egg icon for Plain / Tundra:** those eggs are Aures' own items (`Dragon_Egg_Plain`, `Dragon_Egg_Tundra`, Dragon Nestkeeper) - we
never ship a file for their ids (PROJECT-RULES 2).

## The look

- **Dragons:** one chunky box model (the style of our pet icons in `art/pets` and Hytale's 3/4 model icons): big head + snout, big
  glinting eyes, horns, back spikes, four stubby clawed legs, a tail curling up, two raised wings. The element shows in the colours,
  horns, spikes, wing details and the tail tip. Glowing parts (crystals, flame, bolt, leaf, void stars) get a soft element glow.
- **Eggs:** the approved pet egg look (`art/pet-eggs`): same egg shape, the **Legendary** ornate gold cup (scrolls, milgrain, claws),
  halo, rim light, sparkles; dragon eggs are Legendary items. Shell = element colour + dragon-scale rows + the element emblem (flame,
  bolt, wind swirl, void star); gem, speckles, halo and rim light in the element colour.
- Element colours (Style Guide section 15): Fire orange `#ff8a2a`, Water blue `#4aa8ff`, Earth green `#7ed957`, Thunder yellow
  `#ffd64d`, Air white-teal `#bdf5ea`, Void `#b58cff` (tools/skyyui.py).

## For the main session (wiring - not done here)

`SkyyPets` today MAKES these at build time: the 5 portraits as recolours of the vanilla `Dragon_Frost` model icon and the 3 egg
icons as recolours of our Combat Legendary egg (`build_skyypets_0.4.12.py`, the `EGG_FILES[... PORTRAIT_ID ...]` and
`EGG_FILES["Common/" + _ic]` lines). Next SkyyPets patch: read these files from `art/dragons/Common/...` instead (like `EGG_ART` reads
`art/pet-eggs`); the paths and ids are identical, so nothing else changes. The Void icon + egg wait for the `DragonVoid` kind (D5).

## UNVERIFIED

1. Not seen in game (inventory, Pets card, Hatchery grid).
2. Straight vs premultiplied alpha for the soft glow pixels (same open point as `art/pet-eggs`).
3. `Skyy_PetEgg_Dragon_Void` / `Skyy_PetIcon_DragonVoid` ids are proposals - the D5 builder picks the final ids (rename the files to match).

## Rebuild

```
python tools/art/make_dragon_icons.py            # pure Python, ~5 s; writes this folder
python tools/art/make_dragon_icons.py --out DIR  # somewhere else (e.g. a scratch folder)
```
Edit the look in the script: `ELEMENTS` (dragon colours), `dragon()` / `horns()` / `wing_parts()` / `tail_tip()` (the box model),
`EGGS` + `emblem_shape()` (eggs).

## Open questions for Skyy (each with a default)

1. Dragon icons as a young dragon standing with raised wings (side 3/4 view, like the pet icons)? [yes]
2. Dragon eggs in the Legendary gold cup (they are Legendary items) with the element emblem on the shell? [yes]
3. Earth = green (Style Guide) for the Plain dragon, not brown? [green body, brown wings]
