# Soul Orb spec (the Priest's second weapon)

Cloud draft, 2026-10-06. Paper numbers; nothing built. Locks used (docs/answered/classes.md, 2026-10-04): hold right-click = soul tethers on every enemy in a small radius where you look (up to the tier's cap); damage starts at once, tethers **stabilize** after **1.5-2.5 s**
(wispy -> solid) and then hold while you keep holding the button; **no natural Mana regen while tethering, but Mana Steal still works**; damage is **stored as bonus healing** (capped by tier) for **Wings of Fate** (the traversal: long gliding bounds, locks onto a **party member** and carries you
to them; arrival heals a base amount even with nothing stored, plus all stored healing); the ladder is a **Soul Orb then Soul Cages**: a soul inside a **dodecahedron metal lattice (20 points = 20 gems = 20 tethers)**, the soul, gems and tethers taking the colour of the tier's essence;
Copper 2 tethers 1.1x, Iron 4 tethers 1.1x, Thorium 6 tethers 1.5x, Cobalt 10 tethers 1.5x; proposed Adamantite 14 / 2.0x, Mithril 16 / 2.0x, Onyxium 20 / 2.5x; **balance target: max Mana Steal = the drain of a full Cobalt cage (10 tethers)**.
Traversal costs (2026-10-05 lock): magical traversals cost **2 parts Mana : 1 part Stamina** (e.g. 10 + 5 or 20 + 10); traversal lock-on only targets party members; no cooldowns by default.
Inputs read: `research/classes/Priest.md`, `research/cloud/Class-Ability-Spec-Draft.md`, `docs/answered/classes.md` (Mana pools: Priest 30 + 5 per Divinity level). Vanilla item names UNVERIFIED.

## 1. The ladder (tiers, colours, recipes)

Gem count per cage is visible on the model = tether count; **recipe cost** proposes **half** that many gems (rounded up) so the cage is craftable (20 diamonds would be absurd). Essence colours: the soul and gems share the colour.

| Tier | Name | Tethers | Colour | Essence (recipe) | Gem (vanilla `Rock_Gem_*`) | Metal bars | Made from | Level band |
|---|---|---|---|---|---|---|---|---|
| 0 | **Soul Orb** | 1 | 🔵 blue | Essence of Life x 20 | 1 Blue Crystal Shard | - | 4 Sticks + 1 Plant Fiber (the frame) | 1-13 |
| 1 | **Copper Soul Cage** | 2 | 🟢 green | **Life** x 15 | Emerald x 1 | Copper Bar x 8 | the Soul Orb | 10-18 |
| 2 | **Iron Soul Cage** | 4 | 🔴 red | **Fire** x 15 (deep-cave mobs) | Ruby x 2 | Iron Bar x 10 | the Copper Cage | 15-23 |
| 3 | **Thorium Soul Cage** | 6 | 🔷 cyan (ice-blue) | **Ice** x 15 | Sapphire x 3 | Thorium Bar x 12 | the Iron Cage | 20-28 |
| 4 | **Cobalt Soul Cage** | 10 | 🟡 yellow | **Lightning** x 12 | Topaz x 5 | Cobalt Bar x 14 | the Thorium Cage | 25-38 |
| 5 | **Adamantite Soul Cage** | 14 | 🟣 purple | **Void** x 12 | Voidstone x 7 | Adamantite Bar x 16 | the Cobalt Cage | 35-43 |
| 6 | **Mithril Soul Cage** | 16 | 🌫️ white-green (wind) | **Wind / Zephyr** essence x 10 (UNVERIFIED item; fallback: Crystal Shard White) | Zephyr x 8 | Mithril Bar x 18 | the Adamantite Cage | 40-49 |
| 7 | **Onyxium Soul Cage** | 20 | ⚫ black-violet | **Voidheart** x 3 + Void x 10 | Diamond x 10 | Onyxium Bar x 20 (no vanilla recipe yet; later, own tiers) | the Mithril Cage | 50+ (later) |
Notes:
- The seven vanilla gems (Diamond, Emerald, Ruby, Sapphire, Topaz, Voidstone, Zephyr) map one-to-one onto the seven cages. Copper-Cobalt essences exist in the Collections registry (Life, Fire, Ice, Lightning, Void); the Adamantite+ essences and the Zephyr essence are **UNVERIFIED**.
- Each recipe also needs 1 **Enchanted** item of the tier's metal from Copper Cage on (Enchanted-Materials-Draft), following the standing rule that every tier is crafted from the previous one.
- Quantities of essence rise with rarity (Life is a crop by-product; Fire / Ice / Lightning / Void come from specific mobs; the numbers are about **30 to 60 minutes of farming that essence** at the tier's zone).

## 2. Tether numbers

| Tier | Tethers | Mana per tether per second | **Full-cage drain (Mana/s)** | Damage per Mana (multiplier) | Stabilize time | Stored-heal cap (max Health of the healed ally) |
|---|---|---|---|---|---|---|
| Soul Orb | 1 | 1.00 | **1.0** | 1.0x | 2.5 s | 10% |
| Copper | 2 | 1.05 | **2.1** | 1.1x | 2.3 s | 15% |
| Iron | 4 | 1.10 | **4.4** | 1.1x | 2.1 s | 20% |
| Thorium | 6 | 1.15 | **6.9** | 1.5x | 1.9 s | 30% |
| Cobalt | 10 | 1.20 | **12.0** | 1.5x | 1.7 s | 40% |
| Adamantite | 14 | 1.25 | **17.5** | 2.0x | 1.6 s | 50% |
| Mithril | 16 | 1.30 | **20.8** | 2.0x | 1.5 s | 55% |
| Onyxium | 20 | 1.35 | **27.0** | 2.5x | 1.5 s | 60% |
("Mana per second per tether stays about the same, only a few small steps up": +0.05 per tier. Stabilize time falls from 2.5 s to the floor of 1.5 s, as locked. The stored-heal cap never goes above the single-target heal cap of **60%** in `Class-Ability-Spec-Draft`.)

### 2.1 Damage
- **Damage per Mana at the Soul Orb = 0.08 H** (H = one charged wand shot at the player's level). That is **below** the Mage staff's 0.10 H per Mana (Mage = more damage per Mana, Priest trades damage for healing: LOCKED).
- Damage per second **per tether** = `0.08 H x multiplier x Mana rate`: Orb 0.08, Copper 0.09, Iron 0.10, Thorium 0.14, Cobalt 0.14, Adamantite 0.20, Mithril 0.21, Onyxium 0.27 H per second **on each tethered enemy**.
- **Whole-cage output** (all tethers on different enemies): Orb 0.08 / Copper 0.19 / Iron 0.39 / Thorium 0.83 / Cobalt 1.44 / Adamantite 2.80 / Mithril 3.33 / Onyxium 5.4 H per second in total. Single-target it is weak by design (0.08-0.27 H/s against a boss): the orb is a **crowd tool** that feeds healing.
- Budget check (Class-Ability-Spec-Draft): the orb's damage is **not** an ability; the budget rule used is "total sustained output at most 1.5x the weapon's sustained DPS (about 1 H/s)" - Onyxium at 5.4 H/s only happens when 20 enemies are packed within the small radius; Cobalt at 1.44 H/s is in range.
- **Targeting radius**: a **3-block sphere** around where you look; lock-on range up to **25 blocks**; a tether breaks if the enemy is farther than **30 blocks**, line of sight is blocked for **3 s**, or it dies.
- **Wispy phase**: damage is dealt at once, but a **wispy** tether snaps if you look away or the target leaves the 3-block sphere; once **stable (solid)** it holds while you keep the button held.
- Kills by tether pay class XP normally (the level-gap rule applies); Divinity XP only from heals (see Wings).

## 3. Mana, regen and Mana Steal

| Rule | Value |
|---|---|
| No natural regen | **no Mana regen** while holding the button with **at least one tether** (any, wispy or solid) |
| Drain | each tether drains its per-second Mana continuously; if Mana hits 0 all tethers snap |
| Mana Steal | **works** while tethering: each tether's damage counts for the steal window (SkyyGear Mana Steal today is a flat amount per window) |
| **Balance target** (LOCKED) | **max total Mana Steal from gear = the drain of a full Cobalt cage = 12.0 Mana per second** (= 36 per 3-second window in Wynn's unit). So with max Mana Steal a Priest can hold a Cobalt cage forever; **Adamantite (17.5/s), Mithril (20.8/s), Onyxium (27/s)** drain more than the cap so they run out |
| Cap in the build | clamp **total Mana Steal** contributions to **12.0 Mana/s** while tethering (a SkyyGear row `manaSteal.maxPerSecond`, 12) |
| Priest Mana | 30 + 5 per Divinity level: Lv 20 = 130; Lv 45 = 255; at Lv 45 an Adamantite cage drains 17.5/s: **net -5.5/s with max Mana Steal = 46 s** of tethering |
| Combat regen rules | the in-combat 50% regen does not apply while tethering (regen is fully blocked) |

## 4. Stored healing and Wings of Fate

### 4.1 Stored healing
| Rule | Value |
|---|---|
| Storage | **50% of the damage the tethers deal** is stored as healing, counted in **HP** |
| Cap | the tier's % of the **target's max Health** (table above), checked at release |
| Decay | none while tethering; after you release the button it **decays 2% per second** (a Soulweaver path node can remove the decay: `Class-Tree-Paths.md` S2) |
| Who | one pool per Priest, released by Wings of Fate onto **one party member** |
| Anti-exploit | only **hostile** enemies feed it; a training dummy or friendly mob does not; the pool resets on death and profile switch |

### 4.2 Wings of Fate (traversal, magical)
| Rule | Value |
|---|---|
| Trigger | the weapon's **charged attack** (hold = glide start) |
| Cost | **20 Mana + 10 Stamina** (2 : 1, LOCKED ratio); **no cooldown** (cost only) |
| Glide | **14 blocks** of fast gliding bounds in the look direction (no ally lock), fall speed halved, glowing blue wings + trail (looks only) |
| Ally lock | if a **party member** is in the look direction within **30 blocks**, it locks on and carries you to them (farther than without) |
| Arrival | heals the ally: **base heal = 10% max Health + 1% per tier** (Orb 10%, Onyxium 17%) + **all stored soul healing** (capped) |
| Cap | arrival heal never above **60%** of the ally's max Health per use |
| Divinity XP | 1 per HP healed on the ally (live heal bridge) |
| Lock-on safety | never targets hostile mobs or non-party players; no ally = glide only |
| Perks later | the tree can slow / stun on arrival (looks only for now) |

## 5. Server Setup rows (sketch)
`soulorb.enabled`, per-tier table (tethers, manaPerTether, damageMult, stabilizeSeconds, storeCapPercent), `soulorb.damagePerMana` (0.08 H), `soulorb.lockRadius` (3), `soulorb.lockRange` (25), `soulorb.snapRange` (30), `soulorb.storeFraction` (0.5), `soulorb.decayPercentPerSecond` (2),
`soulorb.noRegen` (on), `manaSteal.maxPerSecond` (12), `wings.glideBlocks` (14), `wings.lockRange` (30), `wings.manaCost` (20), `wings.staminaCost` (10), `wings.baseHealPercent` (10), `wings.perTierPercent` (1), `wings.capPercent` (60).

## 6. Checks and findings
| # | Finding |
|---|---|
| 1 | The ladder's tether counts (2 / 4 / 6 / 10 / 14 / 16 / 20) and 20 gems per Onyxium cage are huge: recipe gems use **half**, model shows all. |
| 2 | **Cobalt = exactly 12.0/s**, so the balance target is a single number: `manaSteal.maxPerSecond = 12`. |
| 3 | Mage and Priest Mana scales are 30 + 10/L and 30 + 5/L; a Priest with the cage drains fastest, a Priest Lv 20 (130 Mana) with a Cobalt cage (12/s) lasts **11 s without Mana Steal**, indefinitely with max Mana Steal, so the target is meaningful. |
| 4 | The stored cap matches the single-target heal cap (60%). |
| 5 | The damage per Mana (0.08 H) is a placeholder; compare with the real wand tooltips (e.g. "Charged shot 5 Mana ... 35-45 damage at Lv 6") once SkyyArmory numbers settle. |

## 7. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Engine: a held interaction that keeps draining Mana each second and spawns **multiple tether entities** (beams) on several targets; the tether's wispy / solid states (two particle styles). |
| 2 | Blocking natural Mana regen only while the weapon is held and tethering (a regen modifier flag) while Mana Steal keeps working. |
| 3 | Gliding / lock-on traversal: a server-push glide plus a party-member lock-on (party data from SkyyParty). |
| 4 | Whether the `Rock_Gem_*` and essence items match my vanilla names (Collections-Spec lists `Rock_Gem_Diamond / Emerald / Ruby / Sapphire / Topaz / Voidstone / Zephyr` as VERIFIED; Adamantite+ essences unverified). |
| 5 | Models: the dodecahedron cage as a new generated asset (art kit `tools/skyyart.py`), recoloured per tier. |
| 6 | Mana Steal cap: how SkyyGear's Mana Steal is implemented (flat per window) and where a `maxPerSecond` clamp fits. |

## 8. Questions for Skyy
1. OK with the recipe gem count being **half** the tether count?
2. Mithril essence (wind / Zephyr) and Onyxium (Voidheart + Void): fine as proposals?
3. Should stored healing also work on Sacred Heal (a path node) or only on Wings of Fate?
