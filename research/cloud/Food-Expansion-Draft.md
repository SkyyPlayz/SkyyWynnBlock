# Food Expansion: every vanilla food, food families, eating rule, potions vs food

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: CLOUD-RESUME.md (task), docs/answered/skills.md (Cooking + Mana lines,
LOCKED 2026-10-06 FOOD and POTIONS), docs/answered/project.md (Dynamic Seasons, Orchard, NoCube candidates), docs/log/2026-10.md, PACK.md,
research/Cooking-Skill-Spec.md (2, 3.5, 4.1-4.5, 5), research/Alchemy-Skill-Spec.md (2, 4.1), research/Mob-Curve-Spec.md (0, 2.3, 5.2),
research/cloud/Stats-Page-Spec.md, research/Mana-Cost-And-Regen-Research.md (Mana.json), tools/cooking_0_1_*_patch.py (dish ids).
Every number is a placeholder and a Server Setup row (section 9). Times in seconds. Arithmetic checked with python3.

## 0. Decisions this draft follows (LOCKED, not re-decided)

| Date | Lock (docs/answered/skills.md) |
|---|---|
| 2026-10-02 | Grade = floor(Cooking / 10) + tree, cap 12. Strength x(1 + 0.32 x Grade); duration x2^(Grade/5) (unchanged). |
| 2026-10-06 | FOOD = primary healing: add ALL vanilla foods to the Grade / healing system, then our own; eat a little faster OR hits no longer cancel eating (pick one here). |
| 2026-10-06 | POTIONS focused (a health potion only heals: instant + over time), FLAT numbers not %, scaling with potion Grades like food. FOOD mixed: VEGGIES = Health, FRUIT = Mana, MEAT = Stamina, MUSHROOMS = bonus effects (temp Strength, crit damage ...); a dish from several families gets each family's bonus; better foods give smaller instant + over-time boosts to all three. |
| 2026-10-02 | Mana Regen boosts are PERCENT; in combat the whole Mana regen runs at 50%. Overall Level +0.5 max Health / +0.2 max Mana. |
| 2026-09-30 | Cooked food stays out of the Farming bag. |
| 2026-10-06 | Orchard in the pack: we may only REFERENCE its item ids (no reuse / changes of its content). Bakehouse, Culinary = candidates only. |

Note: Cooking-Skill-Spec 2.2 / 4.1 still print the old 2^(g/5) strength; the live rule is x(1 + 0.32g): G1 1.32, G5 2.6, G10 4.2, G12 4.84.

## 1. The yardstick: how much healing is "primary but not trivial"

From Mob-Curve-Spec 5.2 (Hard, same level): a mob bites every 3 s and kills you in 5-6 bites at every level 1-60, so one same-level
mob deals about **6% of your max Health per second** (5.5 bites -> 6.1%/s; +10 levels -> 3-4 bites = 8-11%/s). Other healing caps
already set the scale: Life Steal at most 5%/s (Mob-Curve 2.5), Priest group heals at most 6%/s (Class-Ability-Spec-Draft).

Target (python-checked, T3 veggie dish, one bite every Sated window, section 3):

| Grade | Health over time | Instant per bite | Sustained in a fight | vs one same-level mob | 10% -> full out of combat |
|---|---|---|---|---|---|
| 0 | 0.60 %/s | 12 % | 1.08 %/s | 18 % | 130 s (1 bite) |
| 2 | 0.98 %/s | 20 % | 1.77 %/s | 29 % | 71 s |
| 5 | 1.56 %/s | 31 % | 2.81 %/s | 46 % | 38 s |
| 10 | 2.52 %/s | 50 % | 4.54 %/s | 75 % | 16 s |
| 12 (tree cap) | 2.90 %/s | 58 % | 5.23 %/s | 86 % | 11 s |

So food is THE way to refill between fights at every Grade, and in a fight it slows death but never out-heals one same-level mob
(and only with perfect eating between bites). Today's live rule (vanilla T3 regen 1%/s x4.2 = 4.2%/s at G10, instant 15% x4.2 = 63%
with no cooldown) would out-heal a mob - this draft lowers the base regen and adds the Sated window to fix that.

## 2. Food families (the core rule)

Each food ingredient belongs to one family. **Grain counts as Veggie** (wheat, flour, dough, bread, rice, corn) so pies and bread
still heal. Eggs and cheese count as Meat; fish counts as Meat (section 7). Sticks, salt, spices, fuel: no family.

Base numbers per family at share 1.00 (Grade 0); x(1 + 0.32g) strength, duration 45 / 150 / 360 s x2^(g/5):

| Family | Restores / buff | T1 | T2 | T3 | Cap (after Grade) |
|---|---|---|---|---|---|
| Veggie = **Health** | instant % max Health | 5 | 8 | 12 | 60 % |
| | Health over time %/s (pulse 2 s) | 0.25 | 0.40 | 0.60 | 3.0 %/s |
| | max Health (T3 only) | - | - | +10 % | +50 % |
| Fruit = **Mana** | instant % max Mana | 5 | 8 | 12 | 100 % |
| | Mana Regen % (the live percent stat) | +10 | +15 | +20 | +100 % |
| Meat = **Stamina** | instant % max Stamina | 10 | 20 | 30 | 100 % |
| | max Stamina | +10 % | +20 % | +30 % | +150 % |
| | Stamina regen per 0.1 s (vanilla FruitVeggie T2/T3) | - | +0.025 | +0.05 | x Grade, no cap |
| Mushroom = **bonus** | Strength (flat, +1% dmg each) OR Crit Damage %, set per dish | +2 / +3 % | +4 / +5 % | +6 / +8 % | 30 / 35 % |

**Combos (shares).** A dish with N families gives each family `share = (1/N) x (1 + 0.15 x (N-1))`, rounded:
1 family 1.00, 2 families 0.60, 3 families 0.45, 4 families 0.36 (total value 1.00 / 1.20 / 1.35 / 1.44). Focused food = the
strongest single bar; mixed food = more total value spread thin (Skyy: "smaller instant and over time boosts" to all three).

**Stacking.** One buff per family runs at a time (vanilla rule kept, Cooking-Skill-Spec 4.2: a weaker buff never replaces a stronger
one, ranked by strength then duration). So combos stack ACROSS families, never inside one: a Vegetable Skewer + a Fruit Skewer =
full Health + full Mana; a Garden Skewer on top adds nothing. G12 check: every cap holds except Crit Damage (8 x 4.84 = 38.7 -> 35).

Examples (python): G0 Garden Skewer (veg+fruit, T2) = 5% HP + 0.24%/s, 5% Mana + 9% Mana Regen, 150 s. G10 Hunter's Skewer
(veg+meat) = 20% HP + 1.01%/s, 50% Stamina + max Stamina +50%, 600 s. G10 Meat Pie (meat+dough, T3, share 0.6) = 30% HP + 1.51%/s,
76% Stamina, max Stamina +76%, 1,440 s.

## 3. Eating rule (recommendation: eat FASTER, hits still cancel)

| Option | Effect | Risk |
|---|---|---|
| A. Faster eating, x0.75 charge (T1 2.0 -> 1.5 s, T2 2.5 -> 1.9 s, T3 3.0 -> 2.25 s), hits still cancel | A bite now fits inside a mob's 3 s attack cycle; dodge, step back, eat | none new; keeps eating a skill |
| B. Hits no longer cancel eating | Eat while tanking | With 50-60% instant bites at G10+, you could eat-tank forever; needs a much harsher Sated window |

**Recommend A**, plus the **Sated** window for both: after any food instant restore you are Sated for 25 s; while Sated, food still
gives its over-time buffs but no instant restore (all three instants share one Sated). Raw snacks (T1) only set Sated for 8 s.
How: our dish items use our own copy of the consume chain (`Skyy_Cook_Consume_T<n>`, charge x0.75, `FailOnDamage` kept or dropped by
a build switch) and wrap the instant effects in `EffectCondition` on `Skyy_Cook_Sated` (Match None) -> instant + `ApplyEffect Sated`.
All vanilla interaction types (VERIFIED list in Cooking-Skill-Spec 4.2); no Java. Vanilla raw items keep vanilla timing unless the
override test (stage 2) works.

## 4. Every vanilla food in the system

Ids: "spec" = VERIFIED earlier in Assets.zip by the local Cooking spec; "repo" = named in repo docs, edibility / exact effect
UNVERIFIED. Web values: raw plant food = 5% heal + Regen I for 45 s (allthings.how, nerdschalk snippets). Graded = gets Grades 1-12;
"G0 copy" = our Skyy item at Grade 0 too (Cooking 0-9), so the family rules apply from the first dish.

| Item (id) | Today (vanilla) | Family -> new tier | Graded |
|---|---|---|---|
| Raw fruit: `Plant_Fruit_Apple`, `_Berries_Red`, `_Pinkberry`, `_Mango`, `_Coconut`, `_Azure`, `_Spiral`, `_Windwillow` (repo) | 5% + Regen I 45 s (web) | Fruit T1 (snack, Sated 8 s) | no (raw) |
| `Plant_Fruit_Poison` (repo) | UNVERIFIED (poison?) | none - keep vanilla | no |
| Raw veg: Carrot, Lettuce, Potato, Corn, Onion, Rice, Tomato, Turnip, Aubergine, Cauliflower, Chilli, Pumpkin (`Plant_Crop_<X>_Item`, repo) | 5% + Regen I (web; which are edible UNVERIFIED) | Veggie T1 snack | no |
| Mushroom caps / common / glowing (`Plant_Crop_Mushroom_*`, repo) | UNVERIFIED | Mushroom T1: Strength +2, 45 s (glowing: Crit Damage +3%) | no |
| `Food_Wildmeat_Raw`, `Food_Beef_Raw`, `Food_Pork_Raw`, `Food_Chicken_Raw` (repo) | T1 instant 5% (spec) | Meat T1 (Stamina) | no |
| `Food_Fish_Raw` (+ `_Uncommon/_Rare/_Epic/_Legendary`, spec/repo) | T1 instant 5% | Meat T1 (fish, section 7) | no |
| `Food_Egg` (repo) | UNVERIFIED | Meat T1 | no |
| `Food_Cheese` (spec) | UNVERIFIED | Meat T1 snack | no (recipe input by id, spec 3.5) |
| `Food_Candy_Cane` (repo) | UNVERIFIED (event) | Fruit T1 (sugar) | no |
| `Food_Wildmeat_Cooked` (spec) | T1: Heal + Regen T1 + Meat T1 | Meat T1 | yes + G0 copy |
| `Food_Fish_Grilled` (spec) | as above | Meat T1 (fish) | yes + G0 copy |
| `Food_Vegetable_Cooked` (spec) | T1: Heal + Regen + FruitVeggie T1 | Veggie T1 | yes + G0 copy |
| `Food_Bread` (spec) | instant 15% only | Veggie T2, instant only (x1.5 instant, no HoT) | yes + G0 copy |
| `Food_Popcorn` (spec) | T3 instant 15% only | Veggie T2, instant only (x1.5) | yes + G0 copy |
| `Food_Kebab_Vegetable` (spec) | T2 heal + regen + FruitVeggie | Veggie T2 | yes + G0 copy |
| `Food_Kebab_Fruit` (spec) | same | Fruit T2 | yes + G0 copy |
| `Food_Kebab_Meat` (spec) | T2 heal + regen + Meat | Meat T2 | yes + G0 copy |
| `Food_Kebab_Mushroom` (spec) | T2 heal + regen + FruitVeggie | Mushroom T2 (Strength +4) + small Veggie (share 0.6) | yes + G0 copy |
| `Food_Salad_Berry` (lettuce + berries, spec) | T2 | Veggie + Fruit T2 (0.60 each) | yes + G0 copy |
| `Food_Salad_Mushroom` (spec) | T2 | Veggie + Mushroom T2 (Crit Damage +5%) | yes + G0 copy |
| `Food_Salad_Caesar` (spec) | T3 | Veggie + Meat (cheese) T3 | yes + G0 copy |
| `Food_Pie_Apple` (spec) | T3 | Fruit + Veggie (dough) T3 | yes + G0 copy |
| `Food_Pie_Pumpkin` (spec) | T3 | Veggie T3 (focused Health pie) | yes + G0 copy |
| `Food_Pie_Meat` (spec) | T3 | Meat + Veggie (dough) T3 | yes + G0 copy |
| `Plant_Crop_Health/Mana/Stamina1-3` (alchemy crops, repo) | UNVERIFIED | none - potion inputs | no |
| `Ingredient_Flour / _Dough / _Salt / _Spices` | not food | no family (XP only, LOCKED difficulty rule) | no |
| Milk (bucket?) | UNVERIFIED if it exists | if it exists: Meat T1 drink | no |

Raw items (no Grade) only change if a pack file can override a vanilla item (Cooking-Skill-Spec 5.4: UNVERIFIED) - stage 2 tests one.

## 5. Our own new dishes (Chef's Stove / Cooking Bench; T = tier; XP by the LOCKED difficulty rule)

| Dish (Skyy_Cook_*) | Recipe idea | Families | T | Bonus |
|---|---|---|---|---|
| Garden Skewer | stick + 2 veg + 2 fruit | Veggie + Fruit | 2 | Skyy's own example (HP + Mana) |
| Hunter's Skewer | stick + 2 meat + 2 veg | Veggie + Meat | 2 | |
| Forest Skewer | stick + 2 meat + 2 mushroom | Meat + Mushroom | 2 | Strength |
| Glowcap Skewer | stick + 2 fruit + 2 glowing mushroom | Fruit + Mushroom | 2 | Crit Damage (caster snack) |
| Omelette | 2 eggs + veg + cheese | Meat + Veggie | 2 | |
| Rice Bowl | rice + 2 veg + salt | Veggie | 3 | focused Health, Zone 2+ crop |
| Fruit Tart | dough + 3 fruit | Fruit + Veggie | 3 | best Mana food |
| Chilli Pot | meat + chilli + tomato + spices | Meat + Veggie | 3 | |
| Mushroom Stew | 3 mushrooms + potato + salt | Mushroom + Veggie | 3 | Strength +6 at share 0.6 |
| Hearty Stew | meat + 2 veg + mushroom + salt | Veggie + Meat + Mushroom | 3 | 3 families |
| Waiting Room Lunch Tray ("Form 27-B: one (1) balanced meal") | bread + meat + fruit + mushroom | all 4 | 3 | the all-rounder (share 0.36) |

Every new dish is graded (Grades 0-12) like the vanilla ones; its recipe lists ingredient TYPES (any fruit / any veg) where vanilla
already has a resource type (Fruit Skewer's "any fruit"), else exact ids. Bazaar: food max stack 25 (LOCKED stack rule).

## 6. Pack mods: Orchard (deployed), Bakehouse + Culinary (candidates)

- **NoCube's Orchard 0.0.2** (9 fruits: apricot, lemon, mandarin, orange, peach, pear, persimmon, plum, pomegranate; 17 juices):
  its page forbids changing its content -> we do NOT re-grade or override its items; they keep their own effects. We only reference ids:
  (a) if its fruits carry the vanilla "Fruits" resource type, they already work as "any fruit" in Fruit / Garden Skewers and the
  Fruit Tart (UNVERIFIED); if not, our recipes list `<Orchard fruit id>` x9 by exact id; (b) its fruits = Fruit family in our tables
  (Bazaar, collections); (c) juices stay its own drinks - we pay Cooking XP for a Fruit Press craft by output id (difficulty rule,
  ~ a one-step craft); (d) a later "Orchard Tart" of ours uses its fruits by id. Ids all UNVERIFIED (read from its jar locally).
- **NoCube's Bakehouse** (breads, pastries, pies; Hand Quern flour) and **Culinary** (Chef's Stove dishes with buffs): if added, same
  rule - no grading of their items (that would reuse their models / data; question 6), Cooking XP for their crafts by output id, and
  their flour / dough listed as our Veggie-family inputs by id. Watch: Bakehouse flour vs our Flour XP (LOCKED: flour pays little).
- **Dynamic Seasons**: crops by season change veggie / fruit supply only; no food rule changes.

## 7. Fish foods (with research/cloud/SkyyFishing-Spec-Draft.md, written in parallel)

Fish = Meat family (Stamina). Fish rarity sets the dish tier: Common -> T1 (Grilled Fish), Uncommon / Rare -> T2, Epic / Legendary
-> T3. New: Fish Skewer (Meat T2), Fish and Chips (fish + potato: Meat + Veggie T2), Sushi Roll (fish + rice + seaweed?: Meat +
Veggie T3), Fish Stew (fish + veg + mushroom: 3 families T3). Weight / length only sets the sell price, never the food power (Grade
comes from Cooking). HyFishing's fish foods (deployed stopgap) stay as they are (no licence -> no changes; ids by reference only).

## 8. Potions vs food (focused, FLAT, graded)

Potion Grade = floor(Alchemy / 10) (+ future tree), strength x(1 + 0.32g) like food; potion DURATION keeps the Alchemy perk (+1%
per level) and does not also use 2^(g/5). Base sized so each tier heals ~ vanilla's % at the zone and Grade you usually reach it
(python): Lesser Lv 5 / G0, Small Lv 20 / G2, normal Lv 33 / G3, Greater Lv 49 / G5.

| Health potion | Instant (flat HP) | Over 5 s (flat, removed if hit - vanilla rule kept) | at G10 | Max HP where used |
|---|---|---|---|---|
| Lesser | 20 | 20 | 84 + 84 | 140 |
| Small | 30 | 40 | 126 + 168 | 169 |
| Normal | 45 | 65 | 189 + 273 | 287 |
| Greater | 75 | 120 | 315 + 504 | 554 |

Safety cap: a potion's instant heal is at most 60% of max Health (row). Stamina potions: flat too, sized after the local session
reads the Stamina max. Mana: a focused Mana potion (instant Mana + Mana over 5 s) is new - vanilla "Signature" potions restore
SignatureEnergy, not Mana (question 4). Potions have no Sated window (their cost is the alchemy chain); food has the families.

## 9. Server Setup rows (Cooking -> Food; Alchemy -> Potions)

"build" = baked into the generated assets (a change takes effect after the next jar build); "live" = read at runtime.

| Row | Default | Kind |
|---|---|---|
| Family base numbers (section 2 table, one row each) | as table | build |
| Combo share bonus per extra family | 0.15 | build |
| Caps (instant HP 60%, HoT 3 %/s, max HP +50%, Mana Regen +100%, max Stamina +150%, Strength 30, Crit Damage 35%) | as listed | build |
| Sated window (dishes / raw snacks) | 25 / 8 s | build |
| Eating speed (charge multiplier) | 0.75 | build |
| Hits cancel eating | on | build |
| Mushroom bonus: Strength / Crit Damage (read by SkyyGear) | on | live |
| Food Mana Regen counts in the Mana regen sum (SkyySkills) | on | live |
| Potion base flat numbers per tier (section 8) | as table | build |
| Potion instant cap (% max Health) | 60 | build |
| Potion Grades on / off | on | build |

## 10. Build stages

1. **SkyyCooking (full round: changes the effect of items players already hold):** family effects for the 15 dishes, G0 copies,
   Sated, x0.75 consume chain; new base numbers; tooltips per family ("Health + Mana food").
2. **Override test (lean):** one raw item (`Plant_Fruit_Apple`) as a pack override; if it wins, all raw foods of section 4.
3. **New dishes (lean):** section 5 recipes + XP rows (difficulty rule) + lang.
4. **Bonus + Mana bridge (full, several mods):** SkyyGear reads active `Skyy_Cook_Bonus_*` effects (Strength / Crit Damage) via a
   new `cook:fn:bonus` bridge key; SkyySkills adds food Mana Regen % into its sum (so the in-combat 50% applies); Stats page "Food" row.
5. **Potions (full):** SkyySkills Alchemy - flat graded health / stamina potions, new Mana potion.
6. **Fish + pack ids (lean, after SkyyFishing):** fish dishes; Orchard / Bakehouse / Culinary ids in recipes, XP and the Bazaar.

## For the local session (UNVERIFIED)

- Exact ids + edibility of every raw fruit / crop / mushroom / egg / cheese / candy / milk in Assets.zip; their vanilla effects.
- Whether a pack file can override a vanilla item (raw foods) - Cooking-Skill-Spec 5.4 says UNVERIFIED.
- Vanilla max Stamina (Stamina.json) and whether an effect can add Mana Regen % or Strength (likely needs the Java bridge, stage 4).
- Asset count: 4 families x 3 tiers x 4 shares x 13 Grades ~ 624 effects + ~624 checks + ~29 dishes x 13 ~ 377 items (~1,600 files;
  today 447) - confirm build time / jar size; fallback = fewer shares (1.00 / 0.60 only).
- Orchard item ids + resource types (does its fruit count as "any fruit"?); HyFishing fish / food ids; Bakehouse / Culinary ids.
- Whether `EffectCondition` around the instant heal works inside `InteractionVars.Effect` (Sated).
- Web sources (snippets; wiki / guide hosts blocked): https://allthings.how/hytale-health-and-healing-food-potions-and-damage-reduction/ ,
  https://nerdschalk.com/early-cooking-recipes-in-hytale-you-should-try-now/ , https://www.thespike.gg/hytale/all-foods-in-hytale ,
  https://progameguides.com/hytale/all-hytale-cooking-recipes-list/ (food list + heal values), https://www.curseforge.com/hytale/mods/buff-stacks
  (vanilla: eating again resets a buff timer). No page found for NoCube Culinary / Orchard item lists.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Eating rule: faster eating (x0.75) with hits still cancelling, or hits never cancel? | [faster, hits still cancel] |
| 2 | Sated: after a food instant restore, no more instant restore for 25 s (over-time buffs still apply)? | [yes, 25 s] |
| 3 | Grain (bread, dough, rice, corn) counts as Veggie = Health; eggs / cheese / fish count as Meat = Stamina? | [yes] |
| 4 | Mana potions: a new focused Mana potion, or turn vanilla Signature potions into Mana potions? | [new Mana potion; Signature stays] |
| 5 | Mushroom bonuses: Strength on brown / common mushroom dishes, Crit Damage on glowing ones - other bonuses wanted? | [those two] |
| 6 | NoCube foods (Orchard juices, Bakehouse, Culinary): keep their own effects, no Grades (their page forbids content reuse)? | [yes] |
| 7 | Potion heal-over-time still removed when you get hit (vanilla rule)? | [yes] |
| 8 | Fish foods: plain Meat family, or should rare fish add a small bonus (like mushrooms)? | [plain Meat] |
