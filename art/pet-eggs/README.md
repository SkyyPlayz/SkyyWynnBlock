# Pet eggs - 30 egg icons + 6 world textures (round A0 of research/Pet-Eggs-Spec.md)

**Status: DRAFT for Skyy's review** (2026-10-16, Skyy away: "work through as much of your list as you can while im gone.").
Not committed, not wired in, not seen in game. **Start here:** `sheet.png`.

Follows `docs/answered/pets.md` 2026-10-15 PET EGGS + HATCHING (Skyy: "there are mining eggs, farming eggs, combat eggs and so on" +
"eggs come in rarities from common to mythic") and the spec sections 1.1 (ids, Mythic quality, model), 1.2 (icons) and 8 (round A0).
Original pixels drawn from code (`tools/art/make_pet_eggs.py`, numpy + Pillow, paint engine `tools/art/ability_icon_core.py`);
deterministic (two runs = same bytes, checked). No vanilla file, other mod or reference picture read, copied or traced.

## How to read an egg

| Part | Means | Look |
|---|---|---|
| Shell colour + motif | the egg's TYPE (category) | Mining slate blue: cracked shell with blue ore crystals + gold flecks. Farming wheat gold: a wheat ear with leaves, furrows. Foraging bark green: bark grain, a knot, moss, a leaf sprout on top. Combat red: two crossed swords + claw scratches. Exploration teal: a gold compass star in a ring + a dotted trail to an X |
| Egg cup metal | RARITY | Common dark iron, Uncommon bronze, Rare silver, Epic gold, Legendary ornate gold (scrolls + milgrain), Mythic platinum with prism bands - the approved accessory rarity idea (metal + growing gem) |
| Front gem | RARITY | vanilla quality colour (Common grey, Uncommon green, Rare blue, Epic purple, Legendary gold) + Mythic `#CC66CC` (the `Skyy_Pet_Mythic` quality); round -> faceted diamond with claws -> milgrain -> a 4-point star (Mythic) |
| Speckles | RARITY | rarity-coloured speckles on the shell, 5 (Common) -> 18 (Mythic, rainbow) |
| Glow | RARITY | none on Common / Uncommon; a soft halo + rim light from Rare up, strongest on Legendary; Mythic = a shimmering multi-colour halo; sparkles on Legendary + Mythic |

## Files

| File | What |
|---|---|
| `Common/Icons/ItemsGenerated/Skyy_PetEgg_<Category>_<Rarity>.png` | 30 item icons, 64 x 64 RGBA (ids = spec 1.1 `Skyy_PetEgg_<Category>_<Rarity>`) |
| `Common/Items/Pets/Skyy_PetEgg_<Rarity>_Texture.png` | 6 world / held textures, 32 x 32 RGBA, one per rarity (spec 1.1: "vanilla Egg.blockymodel by path + our own texture per rarity") |
| `sheet.png` | review sheet: 5 x 6 grid at 2x on rarity-coloured slots, an actual-size strip (64 + 32 px), the 6 textures at 6x + on a box preview |
| `manifest.json` | every file (bytes, sha256), item id, name, palettes, the vanilla model's UV layout |

## The 6 textures (spec UNVERIFIED item 4 - now checked)

The vanilla egg model `Items/Consumables/Food/Egg.blockymodel` (read from Assets.zip 2026-10-16, numbers only) is ONE box
14 x 16 x 14 on a **32 x 32** texture, custom UVs: front (0,0) 14x16, top (14,0) 14x14, back + left + right all share (14,14) 14x16,
bottom (0,16) 14x14. Our textures use exactly that layout: a warm ivory shell (rounded shading per face), rarity-coloured speckles, a
3-row band of the rarity's cup metal round the bottom of the sides, a gem dot on the front (Uncommon up), a faint rarity tint;
Mythic adds a prism shimmer. In the world the egg is a rounded box, so the category cannot show there - only the icon shows it
(spec: one texture per rarity).

## Defaults used (Skyy can change)

1. Rarity is carried by an egg CUP (a stand) rather than painting the shell, so the category colour stays clean on every rarity.
   [default: cup]
2. Exploration motif = compass star + trail to an X (no Exploration pet art exists yet). [default]
3. Mythic = platinum + prism shimmer (Mythic is our own quality colour `#CC66CC`). [default]
4. The halo is a soft semi-transparent glow (alpha up to ~0.85) outside the egg; the egg, cup and outline are hard alpha.

## UNVERIFIED (for the main session)

1. Straight vs premultiplied alpha for the soft halo pixels in Hytale's item-icon renderer (the approved accessory icons were written
   premultiplied; these are straight). If the halo looks too bright or dark in game, make the halo hard-alpha or premultiply it.
2. How the 32 x 32 texture looks on the vanilla egg model in game (`CustomModelScale` 0.6, held + dropped) - not seen.
3. A Fishing egg (spec 2.3, later) is not drawn - add a `Fishing` entry to `CATEGORIES` / `SHELL` / `MOTIF` when that round comes.
4. Not seen in game.

## Rebuild

```
python tools/art/make_pet_eggs.py        # needs numpy + Pillow; writes this folder (~80 s)
```

## Open questions for Skyy (each with a default)

1. Egg cup for rarity, or rarity painted on the shell itself? [egg cup]
2. Any type motif to change (Mining crystals, Farming wheat, Foraging bark + sprout, Combat crossed swords, Exploration compass)? [keep]
