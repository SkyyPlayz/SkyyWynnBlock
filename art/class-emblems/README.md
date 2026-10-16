# Class emblems - 8 classes (64 x 64 + 128 x 128 + locked 64)

**Status: APPROVED (Spellblade crest approved 2026-10-16) for Skyy's review** (2026-10-16). 7 crests are the APPROVED ones; only the Spellblade crest is new.
Nothing here is wired in or seen in game yet. **Start here:** `sheet.png`.

Why: Skyy 2026-10-16 (Character > Profiles screenshot, `docs/answered/ui.md` CLASS ICONS ON PROFILES): "didn't we make class icons?
why arnt they shown here?" - yes: the cloud class emblems in `research/cloud/class-art/` were APPROVED (`docs/answered/gear.md`
line 86, 2026-10-06: "they look great!", then Monk = wrapped fist + Priest = soul cage v2 on 10-07, v2 detail for the other 5 on
10-08). They were never moved into `art/` and had no Spellblade (the 8th class came on 10-08). This folder is that set, game-ready,
plus the Spellblade.

| Class | Status | Symbol |
|---|---|---|
| Warrior `#e0b060` | APPROVED (as drawn 10-08) | longsword crossed over a spear |
| Berserker `#d9443f` | APPROVED | bearded double-bit battleaxe crossed with a flanged mace |
| Archer `#8fd67a` | APPROVED | recurve shortbow with a nocked red-fletched arrow |
| Assassin `#b58cff` | APPROVED | kunai crossed with a dagger |
| Mage `#7fb0e0` | APPROVED | staff with the big violet crystal head + tooled spellbook |
| Priest `#f2e6a0` | APPROVED | soul cage v2 + wand + halo |
| Monk `#f08a30` (Saffron) | APPROVED | linen-wrapped fist + bo staff + wind swirl |
| **Spellblade - DRAFT** `#6fd0d8` | **NEW, for review** | a two-handed GREATSWORD (broad bevelled blade with a glowing teal rune fuller, long straight crossguard with a teal gem, long two-hand grip in dark teal leather with a steel mid-ring, violet pommel gem) in front of a violet arcane CRESCENT sweep (the class's wide arc / Momentum) |

Spellblade choices (defaults, Skyy can change): the weapon is the two-handed sword, not the Great Shield (the sword is its main
weapon and the shield is not built yet); the sweep is violet like the Breach rune in the Spellblade ability icons, because a teal
sweep vanished on the teal field; same crest, gold trim, slate rim, rivets and top gem as the other 7.

## Files

| File | What |
|---|---|
| `Common/Icons/ClassEmblems/<Class>.png` | 64 x 64 RGBA (lists, HUD, Profiles rows), transparent outside the crest |
| `Common/Icons/ClassEmblems/<Class>_128.png` | 128 x 128 RGBA (class cards, the class pick) - drawn at 128, not scaled |
| `Common/Icons/ClassEmblems/<Class>_Locked.png` | 64 x 64 grey version (empty profile slot / class not unlocked) |
| `sheet.png` | review sheet: every class at 2x / 128 / 64 / 32 / locked, APPROVED or NEW tag, a dark HUD strip and a Profiles-row mock ("Spellblade Aragorn - ACTIVE", an empty locked slot) |
| `manifest.json` | every file: path, bytes, sha256, size, class, colour, status |

Generator: `tools/art/make_class_emblems.py` (Pillow only; deterministic - two runs give the same bytes, checked). It imports the
approved painter `research/cloud/class-art/make_emblems.py` read-only and adds the Spellblade symbol. The 7 approved classes are
shipped with the APPROVED PNGs' own pixels (`research/cloud/class-art/icons/`); a fresh re-render matches them except a few
anti-aliasing pixels on the Archer's thin bow string under the local Pillow (4 px at 64, 9 px at 128) - the script prints that note
and keeps the approved pixels. Original art drawn from code; no vanilla file, other mod or reference picture read, copied or traced.

```
python tools/art/make_class_emblems.py      # needs Pillow; writes this folder
```

## The ability icons

The ability icons (`art/ability-icons/`) use the same 8 class colours on a round frame; the Spellblade ability set (5 icons, DRAFT)
was drawn in the same pass (`art/ability-icons/sheet-spellblade.png`). The emblems stay crests (the approved look) so a CLASS reads
differently from an ABILITY at a glance.

## UNVERIFIED (for the main session)

1. How a mod shows a PNG in a custom UI page (Profiles rows, class pick, Class tab, HUD): probably as an icon item
   (`Skyy_ClassEmblem_<Class>` with `Icon` = this PNG, the SkyyMenu icon-item pattern) - not checked.
2. The 128 versions assume a card slot of 128 px; vanilla item slots draw 64.
3. Not seen in game.

## Open questions for Skyy (each with a default)

1. Spellblade crest: greatsword + violet sweep OK? [yes]
2. Show the Great Shield on the Spellblade crest too (a second weapon, like Warrior sword + spear)? [no - not built yet]
