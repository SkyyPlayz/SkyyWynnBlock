# Monk kit spec (weapons, ladders, traversal numbers, engine probes)

Cloud draft, 2026-10-06. Paper numbers; nothing built. Inputs: `research/classes/Monk.md` (the locked design), `docs/answered/classes.md` (2026-10-03/04/05 locks), `research/SkyyArmory-Spec.md` (how the wand and staff ladders are built: our own items per metal, recipes mirroring a vanilla weapon,
levels from the metal bands, tap/hold, costs fixed in the jar), `research/Magic-Traversal-Spec.md` (traversal cost rule), `research/cloud/Class-Ability-Spec-Draft.md` (Monk abilities).
Vanilla ids: `Weapon_Staff_Bo_Bamboo` and `Weapon_Staff_Bo_Wood` exist (docs/answered/classes.md); everything else UNVERIFIED.

## 0. The kit in plain words

| Part | What | Status |
|---|---|---|
| Class | Monk replaces the Shaman slot (the placeholder class slot 8 in SkyySkills / SkyyClasses: `CLASS_SLOT = {5,6,7,8,9,14,15}`, order Archer, Warrior, Assassin, **Shaman -> Monk**, Mage, Berserker, Priest) | LOCKED 2026-10-03 |
| Weapons | **Bo staff** (melee, reach) and **fist weapons** (cloth hand wraps, gauntlets, claws: one weapon family, one traversal) | LOCKED |
| Traversals | Bo staff charged = **Pole-Vault** + flowing fall + **skipping bounds**; fists charged = **Rising Strike** (+ hang time, **Plunge Punch**) | LOCKED |
| Armor | Light armor (the Leather type): leather -> copper -> ... ladder keeps the leather look (LOCKED 2026-10-05) | LOCKED |
| Class skill name | **open** (suggestions below) | open |
| Kit | Wood Bo staff + 1 pair of cloth hand wraps (default `kit.Monk`) | proposal |

## 1. Bo staff ladder

Our own metal Bo staffs, built like the SkyyArmory wands (wood shaft + metal caps, one Bo staff per metal; the vanilla Bamboo and Wood Bo staffs stay as tiers 1-2). The metal sets the **level band** and a **small material bonus**; the level raises damage like all gear (SkyyGear).

| Tier | Item (proposed id `SkyyArmory_Bo_<Metal>`) | Level band (the gear bands) | Look (like the wands: wood shaft + metal tips) | Recipe mirrors (UNVERIFIED) |
|---|---|---|---|---|
| 1 | **Bamboo Bo staff** (vanilla `Weapon_Staff_Bo_Bamboo`) | 1-8 | bamboo | vanilla |
| 2 | **Wood Bo staff** (vanilla `Weapon_Staff_Bo_Wood`) | 1-13 | wood | vanilla |
| 3 | **Copper Bo staff** | 10-18 | wood + copper caps and bands | that metal's **Spear** recipe (a long weapon): Copper Bar x ~4 + wood |
| 4 | **Iron Bo staff** | 15-23 | iron caps | the Iron Spear |
| 5 | **Thorium Bo staff** | 20-28 | thorium caps | the Thorium Spear |
| 6 | **Cobalt Bo staff** | 25-38 | cobalt caps | the Cobalt Spear |
| 7 | **Adamantite Bo staff** | 35-43 | adamantite caps | the Adamantite Spear |
| 8 | **Mithril Bo staff** | 40-49 | mithril caps | the Mithril Spear (if vanilla has one; else the Mithril Sword recipe) |
| 9 | **Onyxium Bo staff** | 50+ (later) | black caps | no vanilla recipe (own tiers) |
Art: the same kit as the wands (`tools/skyyart.py`): recolour the vanilla Bo texture with metal bands at build time (never commit vanilla assets). **Reach**: +0.5 block over a sword; hit combo of **3 swings** with a short **sweep** on the third.

### 1.1 Bo staff numbers (Lv 1, before level scaling)
| Stat | Value | Notes |
|---|---|---|
| Combo | 3 hits: **5 / 5 / 9** (average 6.3) | sword is 6 / 6 / 11 (7.7) |
| Swing time | 0.45 s per hit | slightly faster than a sword |
| Weapon DPS | about 0.82x a sword at the same level | traded for reach and the traversal |
| Reach | +0.5 block | |
| Material bonus | up to +12% like other weapons (the SkyyGear rule) | |
Everything scales with the SkyyGear curve F(L), the bands above, rarity and reforge; **no SkyyArmory code** for levels (SkyyGear stamps the crafting level).

## 2. Fist weapon ladder (wraps, gauntlets, claws: one family, three flavours)

All three share the same traversal (Rising Strike) and the same level system; they differ in identity:

| Variant | Identity | Stat flavour | Materials |
|---|---|---|---|
| **Cloth hand wraps** | fastest, light | attack speed +15%, damage -10%, Dodge-friendly | **cloth ladder**: Wool Scrap / Linen Scrap -> Cotton -> Silk -> Cindercloth -> Shadoweave (same cloth tiers as Mage/Priest robes) |
| **Gauntlets** | balanced, durable | the baseline; +Defence on the weapon (a small hand guard) | **metal ladder** Copper -> Onyxium (the vanilla armor "Gauntlets" pieces exist, e.g. Iron Gauntlets, Thorium Gauntlets) |
| **Claws** | crit / bleed | crit chance +6%, **bleed** (0.2 H over 3 s) on crit, damage -5% | metal ladder + a hide (leather) |

| Tier | Wraps (cloth) | Gauntlets (metal) | Claws (metal) | Level band |
|---|---|---|---|---|
| 1 | Wool Wraps | - | - | 1-13 |
| 2 | Linen Wraps | Copper Gauntlets | Copper Claws | 10-18 |
| 3 | Cotton Wraps | Iron Gauntlets | Iron Claws | 15-23 |
| 4 | Silk Wraps | Thorium Gauntlets | Thorium Claws | 20-28 |
| 5 | Cindercloth Wraps | Cobalt Gauntlets | Cobalt Claws | 25-38 |
| 6 | Shadoweave Wraps | Adamantite Gauntlets | Adamantite Claws | 35-43 |
| 7 | (Prisma / Moon cloth, later) | Mithril Gauntlets | Mithril Claws | 40-49 |
| 8 | - | Onyxium Gauntlets (later) | Onyxium Claws (later) | 50+ |
Ids proposed `SkyyArmory_Fist_<Variant>_<Tier>`; wraps and gauntlets mirror the **matching armor hands piece** recipe (that piece's bars / cloth, about 4 each); claws mirror the **Dagger** recipe of the metal.

### 2.1 Fist numbers (Lv 1, before level scaling)
| Variant | Combo | Hit speed | Weapon DPS vs sword |
|---|---|---|---|
| Wraps | 4 hits: 3 / 3 / 3 / 5 (3.5 avg) | 0.30 s | about 0.95x |
| Gauntlets | 4 hits: 3 / 3 / 3 / 6 (3.75 avg) | 0.33 s | about 0.9x |
| Claws | 4 hits: 3 / 3 / 3 / 5 (3.5 avg) + bleed | 0.30 s | about 0.9x + bleed |
Fist weapons trade damage per hit for **combo speed**, which suits Flowing Form (each hit = 1 combo).

## 3. Traversal numbers

Cost rule (LOCKED 2026-10-05): every traversal costs **Mana and Stamina**; physical ones (the Monk's) cost **more Stamina than Mana**; a traversal that does not move you costs nothing; no cooldowns (cost only). The Monk's Stamina pool is small (about 12; Exploration adds +0.1 per level),
so costs are kept low; **suggestion:** a Monk-only row **+0.15 max Stamina per Monk level** (like the Priest / Mage Mana rows) so a Monk at level 40 has about 18.

### 3.1 Bo staff - Pole-Vault (charged attack)
| Part | Value |
|---|---|
| Cost | **7 Stamina + 3 Mana** (physical: about 2 : 1 Stamina : Mana) |
| Lunge | 3 blocks forward on the ground first (a quick step) |
| Vault | rises **4.5 blocks**, travels **7 blocks** forward over about 0.8 s |
| Kick | any enemy in the path takes **2x a normal Bo hit** (LOCKED), once per enemy |
| Flowing fall | after the vault you fall **15% slower** and take **15% less fall damage** (LOCKED); no fall damage at all if you bound (below) |
| Free air jump | **1 free mid-air jump** if it is your first jump after the vault (LOCKED) |

### 3.2 Skipping bounds
| Part | Value |
|---|---|
| Trigger | press jump in the window **0.25 s before landing to 0.10 s after** (the "timed landing") |
| Effect | bound **forward** 5 blocks + 0.5 per block you fell (cap +8), height **1.4x** a normal jump; still the slow fall (-15%) |
| Chain | as long as the timing holds (each bound has the same window) |
| Cost | **3 Stamina + 1 Mana** per bound (more than a normal jump; LOCKED "cost more Stamina than a jump") |
| Fall damage | a **timed landing takes none** (LOCKED); a missed landing takes the normal (reduced 15%) damage |
| Damage | none (LOCKED) |
| Cap | Stamina runs out -> the chain ends; no hard cap |

### 3.3 Fists - Rising Strike and Plunge Punch (charged attack)
| Part | Value |
|---|---|
| Cost | **8 Stamina + 4 Mana** |
| Leap | an uppercut leap **6 blocks up**, 1.5 forward; enemies in front (cone 3 blocks, width 1.5) take **1.2 H** and are **knocked up with you** (up to 5 blocks) |
| Hang time | at the top **you and the knocked-up enemies slow** (50% speed) for **1.2 s** (LOCKED: "a few attacks") |
| Air hits | hits on airborne enemies add knockback: **6 blocks horizontal ("flying")** |
| **Plunge Punch** | **crouch near the top**: slam down at **14 blocks/s**, **dragging** the knocked-up enemies; landing damage **1.0 H** area 3 blocks; **no fall damage, no Acrobatics XP** (LOCKED) |
| No plunge | a 15%-slower steerable fall (-15% fall damage), LOCKED |

## 4. Class skill name (open) and slot
Suggested names for the Monk's weapon skill (first line = recommended): **Discipline** (fits Monk and Divinity / Fury style single words), Zen, Kenpo, Harmony, Focus. The skill follows the standard class skill rules (kills pay it, class XP multiplier x3, flat curve LIVE since 0.4.12).
It fills the Shaman placeholder slot; the `skill:fn:level` prefixes (the three-letter prefixes `fur`, `div`, `ber`, `pri`) need a new `dis` / `zen` prefix; SkyyClasses class table `Monk` with `weapons = Bo staff + fists`.

## 5. Engine probe list (the checks that block building; do these with SkyyUiProbe-style probes before coding)
| # | Probe | How to test | Why |
|---|---|---|---|
| 1 | **Slow-fall / glide**: can a mod reduce fall speed (a movement setting or per-tick velocity clamp) without server lag | apply a downward velocity cap for 2 s after a jump, measure fall time | Flowing fall |
| 2 | **Jump input at landing**: can the server see a jump press within +/- 0.25 s of touching ground (the client sends the jump key as a movement state) | log timestamps of the "OnGround" transition vs jump | skipping bounds |
| 3 | **Mid-air jump**: can a player jump once more in the air (movement protocol / MovementSettings "air jumps") | the double-jump spec exists (`research/Double-Jump-Spec.md`): reuse | free air jump |
| 4 | **Fall damage cancel**: cancel the fall damage event for a timed landing | log the Damage event cause "Fall" and cancel it | no fall damage |
| 5 | **Server push / velocity set** for a lunge and a vault (impulse, not teleport) | push 7 blocks forward + 4.5 up | Pole-Vault, Rising Strike |
| 6 | **Hit enemies along a path** (a sweep volume) with 2x damage once per enemy | per-enemy once flag + a damage event | the vault kick |
| 7 | **Knock enemies up with you** and **slow them** (hang time) for 1.2 s | a velocity + a slow effect on mobs | Rising Strike |
| 8 | **Drag mobs down** on Plunge Punch (set their velocity) | downward push on the same targets | Plunge Punch |
| 9 | Cost: **Stamina and Mana per bound** with the live pools; what happens at 0 Stamina mid-chain | change both stats | costs |
| 10 | **Crouch near the top** detection (sneak input) | movement state flags | Plunge Punch trigger |
| 11 | **Acrobatics XP**: exclude the Plunge Punch's fall from XP (a flag on the movement) | check the Acrobatics fall XP path (SkySkills) | LOCKED rule |
| 12 | **Flowing Form aura**: a 5-block aura applying "Awe" to enemies and counting combos on hits (damage event on the Monk) | a per-player aura tick (1 s) + a hit counter | A1 |
| 13 | **Vanilla Bo staff / Bamboo staff behaviour**: the item ids and their attack interaction (charged attack = vanilla "traversal"?) | read `Weapon_Staff_Bo_*` in Assets.zip | base items |

## 6. Server Setup rows (sketch)
`monk.enabled`, `bo.<metal>.*` (damage multipliers, band), `fist.<variant>.*`, `trav.vault.height / distance / staminaCost / manaCost`, `trav.bound.windowBefore / windowAfter / baseDistance / perBlock / cap / staminaCost`, `trav.rising.height / hangSeconds / knockback`, `trav.plunge.speed`, `monk.staminaPerLevel` (0.15), `monk.skillName`.

## 7. Findings
| # | Finding |
|---|---|
| 1 | The Monk's Stamina pool (about 12) is the limiting factor: a vault (7) + a bound (3) already uses 10. Without a per-level Stamina row the Monk cannot chain. |
| 2 | Fists need cloth items at every tier (a cloth ladder that only the Monk uses): reuse the same cloth items as robes and bags (Wool, Linen, Cotton, Silk, Cindercloth, Shadoweave). |
| 3 | The vanilla armor gauntlets suggest a natural recipe source for the fist gauntlets; check that a Weapon_ item can reuse the armor texture/model (the SkyyArmory art route). |
| 4 | Three variants x 8 tiers = 24 fist items + 9 Bo staffs; start with **Wraps (cloth) + Gauntlets** only, claws later (Monk.md "later class idea: a Martial Artist with kicks + fists"). |

## 8. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | The probes in section 5 (all). |
| 2 | Recipes of the vanilla Spear / Dagger / hands armor per metal (Assets.zip) and which bench/tab they use. |
| 3 | `Weapon_Staff_Bo_Bamboo` / `_Wood` interactions: whether they already have a charged attack. |
| 4 | Whether a new class skill slot needs SkySkills table edits (the Shaman placeholder slot is already in the table, per the 0.4.4 notes). |

## 9. Questions for Skyy
1. Class skill name: **Discipline**, Zen, Kenpo, Harmony or Focus?
2. Start with wraps + gauntlets only (claws later)?
3. A Monk-only Stamina row (+0.15 per level)?
