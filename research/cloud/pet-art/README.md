# Pets - concept sheet (launch list + dragon hatchling)

Cloud draft, 2026-10-06. Original pixel art made by code (`research/cloud/pet-art/make_pets.py`, Python + Pillow). No copied art, no
game files, and none of the vanilla Hytale creature designs: every pet is a stylised original "chibi" animal. Concept only; nothing built.
Inputs read: `research/cloud/Pets-Spec.md` (launch list section 5, rarities section 2), `research/Dragon-Pets-Idea.md`,
`research/cloud/Dragon-Quest-Spec.md` (elements, hatchling stage), `docs/answered/pets.md` (R6-R9 locks + the 2026-10-06 Nestkeeper note),
`OPEN-QUESTIONS.md` (pets section), `CLOUD-RESUME.md` (the "Pets concept sheet" item). Style copied from
`research/cloud/light-armor/make_sheets.py` (chunky pixels, 1-px outline, 4-step shading lit top-left, labels).

**Start here:** `research/cloud/pet-art/pet-sheet.png` (all 16 pets in 3 rows + the 9 dragon element recolours).

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

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Do these looks fit SkyWynn (chunky, cute, side view), or should pets look closer to the vanilla Hytale animals? | keep vanilla models in game; this art for icons + menus |
| 2 | Pet rarity colours: SkyBlock's (Common white ... Mythic pink) or the SkyyGear gear rarity colours? | SkyBlock pet colours |
| 3 | Are the zone labels and "found at" rarities in section 3 OK? | as in section 3 |
| 4 | Should mount pets show a saddle when summoned? | yes, small saddle |
| 5 | Skrill (Mage): keep the vanilla Skrill, or an original "stormwing" like the sheet? | vanilla Skrill model in game |
| 6 | Dragon hatchling: our own design (this sheet) or wait for the Nestkeeper decision? | wait for the Nestkeeper answer; this art stays a concept |
